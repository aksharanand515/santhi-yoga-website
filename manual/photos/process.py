"""
Turn the selected Commons photographs into the manual's house style.

Every photo gets the same treatment so that pictures by different photographers read as one
set: a crop around the practitioner with even margins, a warm monochrome tone mapped between
the book's ink (#2A271E) and paper (#FFFEFA) colours, a gentle contrast curve, and edges that
feather into the page. Crops are automatic for plain studio backgrounds and can be overridden
per photo in selection.yaml (normalised x0, y0, x1, y1 on the original).
"""
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "photos_out"
INK = np.array([0x2A, 0x27, 0x1E], float)
PAPER = np.array([0xFF, 0xFE, 0xFA], float)
MID = np.array([0x9C, 0x93, 0x80], float)   # warm mid-tone of the duotone


def auto_box(g, pad=0.07):
    """Bounding box of the subject on a light, plain background (grayscale 0..1 array)."""
    h, w = g.shape
    border = np.concatenate([g[:h // 12].ravel(), g[-h // 12:].ravel(), g[:, :w // 12].ravel(), g[:, -w // 12:].ravel()])
    bg = np.median(border)
    spread = np.percentile(np.abs(border - bg), 90) + 0.06
    small = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))) / 255.0
    mask = np.abs(small - bg) > spread
    # ignore thin vignette rings at the very edge
    mask[: h // 40] = mask[-h // 40:] = False
    mask[:, : w // 40] = mask[:, -w // 40:] = False
    ys, xs = np.nonzero(mask)
    if len(xs) < 50:
        return 0, 0, 1, 1
    x0, x1 = np.percentile(xs, [0.5, 99.5])
    y0, y1 = np.percentile(ys, [0.5, 99.5])
    bw, bh = x1 - x0, y1 - y0
    p = pad * max(bw, bh)
    return max(0, (x0 - p) / w), max(0, (y0 - p) / h), min(1, (x1 + p) / w), min(1, (y1 + p) / h)


def tone(g, lift=0.0):
    """Warm monochrome: luminance -> ink/mid/paper ramp with a soft S-curve."""
    lo, hi = np.percentile(g, [0.8, 99.2])
    g = np.clip((g - lo) / max(hi - lo, 1e-3), 0, 1)
    g = np.clip(g + lift, 0, 1)
    g = g + 0.10 * np.sin(2 * np.pi * g) / (2 * np.pi) * -1   # gentle S-curve
    g = np.clip(g, 0, 1)[..., None]
    a = np.clip(g * 2, 0, 1)
    b = np.clip(g * 2 - 1, 0, 1)
    rgb = np.where(g < 0.5, INK * (1 - a) + MID * a, MID * (1 - b) + PAPER * b)
    return rgb


def feather(rgb, amount=0.07):
    """Fade the outer edge of the picture into the paper colour."""
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum.reduce([xx / w, (w - 1 - xx) / w, yy / h, (h - 1 - yy) / h])
    t = np.clip(d / amount, 0, 1)
    t = t * t * (3 - 2 * t)
    return rgb * t[..., None] + PAPER * (1 - t[..., None])


def make(src, key, box=None, aspect=None, width=1400, lift=0.0, flip=False):
    """Process one photo; returns the output path (cached by content + parameters)."""
    im = Image.open(src)
    im = im.convert("RGB")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    g = np.asarray(im.convert("L"), float) / 255.0
    H, W = g.shape
    x0, y0, x1, y1 = box or auto_box(g)
    if aspect:   # grow the box to the requested width/height ratio, staying inside the image
        bw, bh = (x1 - x0) * W, (y1 - y0) * H
        cx, cy = (x0 + x1) / 2 * W, (y0 + y1) / 2 * H
        if bw / bh < aspect:
            bw = bh * aspect
        else:
            bh = bw / aspect
        bw, bh = min(bw, W), min(bh, H)
        cx = min(max(cx, bw / 2), W - bw / 2)
        cy = min(max(cy, bh / 2), H - bh / 2)
        x0, x1, y0, y1 = (cx - bw / 2) / W, (cx + bw / 2) / W, (cy - bh / 2) / H, (cy + bh / 2) / H
    crop = g[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
    ci = Image.fromarray((crop * 255).astype(np.uint8))
    scale = width / ci.width
    ci = ci.resize((width, max(1, int(round(ci.height * scale)))), Image.LANCZOS)
    rgb = feather(tone(np.asarray(ci, float) / 255.0, lift))
    sig = hashlib.md5(f"{Path(src).name}{box}{aspect}{width}{lift}{flip}v3".encode()).hexdigest()[:10]
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{key}-{sig}.jpg"
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(out, quality=88, optimize=True, progressive=True)
    return out
