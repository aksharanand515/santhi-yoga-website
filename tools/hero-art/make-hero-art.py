#!/usr/bin/env python3
"""Santhi Yoga India: build the home hero's photograph and its motion map.

Turns tools/hero-art/source.webp (a 1672x941 mock-up of a Kerala pavilion at
sunset, with placeholder writing on it) into the files the home hero uses in
assets/img:

  hero-pavilion-{960,1440,1920,2560}.webp   the photograph, writing removed
  hero-pavilion-maps.webp                   depth (red), sea (green), sway (blue)

Steps
  1. Clean    paint out the mock-up's navigation, headline, subline, link, side
              words and scroll icon. Each masked row is filled between its nearest
              clean pixels: the sky's gradient runs top to bottom and the floor's
              grain side to side, so rows carry both, then the grain is put back.
  2. Upscale  4x with Real-ESRGAN (x4plus), run through onnxruntime so no PyTorch
              is needed, blended with a little of the plain resize so the photo
              keeps its grain, and settled at 2560 px wide.
  3. Depth    Depth Anything V2 (small) on the whole frame and on two overlapping
              squares, fitted together, so near and far are known everywhere.
  4. Masks    the sea between the palms (for ripples and glints), and what may
              sway: the sheer curtains, the near leaves (not the pillars behind
              them) and, gently, the palms beyond. Packed with depth into one
              lossless WebP that the WebGL shader in assets/js/site.js reads.

It prints the sun's position (the data-sun attribute on .hero-gl in index.html)
and the tiny blurred placeholder used as the stage background in site.css.

Needs:  pip install pillow numpy scipy onnx onnxruntime
Run:    python3 tools/hero-art/make-hero-art.py [--out assets/img]
The first run downloads the Real-ESRGAN weights (64 MB) and the depth model
(99 MB), both from GitHub, next to this script. Neither is committed.
"""
import argparse, base64, collections, io, os, pickle, urllib.request, zipfile
import numpy as np
import onnxruntime as ort
from onnx import TensorProto, helper, numpy_helper
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ESRGAN = ('RealESRGAN_x4plus.pth', 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth')
DEPTH = ('depth_anything_v2_vits.onnx', 'https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/v2.0.0/depth_anything_v2_vits.onnx')
LUMA = np.array([.2126, .7152, .0722], np.float32)
Image.MAX_IMAGE_PIXELS = None


def fetch(name, url):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        print('downloading', name); urllib.request.urlretrieve(url, path)
    return path


def smooth(a, b, t):
    t = np.clip((t - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def clean(im):
    """1. The mock-up's writing, found as whatever differs from the sky behind it."""
    a = np.asarray(im).astype(np.float32)
    H, W, _ = a.shape
    L = a @ LUMA
    bg = ndi.median_filter(L, size=25)
    yy, xx = np.mgrid[0:H, 0:W]
    mask = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in [(250, 20, 1180, 82), (290, 186, 785, 334), (290, 352, 695, 408), (290, 442, 518, 488), (1298, 220, 1412, 314)]:
        mask |= (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1) & (np.abs(L - bg) > 5)
    mask = ndi.binary_dilation(mask, iterations=3)
    mask |= (xx >= 1272) & (xx <= 1424) & (yy >= 27) & (yy <= 78)   # the button, taken out whole
    mask |= (xx >= 820) & (xx <= 854) & (yy >= 834) & (yy <= 904)   # the scroll icon on the floor
    out = a.copy()
    for y in np.nonzero(mask.any(1))[0]:
        good, bad = np.nonzero(~mask[y])[0], np.nonzero(mask[y])[0]
        for c in range(3): out[y, bad, c] = np.interp(bad, good, a[y, good, c])
    soft = np.stack([ndi.gaussian_filter1d(out[..., c], 2.2, axis=0) for c in range(3)], -1)
    m = ndi.gaussian_filter(mask.astype(np.float32), 1.2)[..., None]
    out = out * (1 - m) + soft * m
    grain = float(np.std((L - ndi.gaussian_filter(L, 2))[100:180, 300:700]))
    out += np.random.default_rng(11).normal(0, grain, (H, W, 1)).astype(np.float32) * m
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def load_torch_zip(path):
    """Read a PyTorch checkpoint's tensors without PyTorch."""
    z = zipfile.ZipFile(path)
    prefix = z.namelist()[0].split('/')[0]
    kinds = {'FloatStorage': np.float32, 'HalfStorage': np.float16}

    class Storage:
        def __init__(self, key, dtype): self.key, self.dtype = key, dtype

    def rebuild(storage, offset, size, stride, *_):
        raw = np.frombuffer(z.read(f'{prefix}/data/{storage.key}'), dtype=storage.dtype)
        return np.lib.stride_tricks.as_strided(raw[offset:], shape=size, strides=[s * raw.itemsize for s in stride]).copy()

    class Unpickler(pickle.Unpickler):
        def find_class(self, mod, name):
            if name in kinds: return name
            if name == '_rebuild_tensor_v2': return rebuild
            if name == 'OrderedDict': return collections.OrderedDict
            return super().find_class(mod, name)

        def persistent_load(self, pid):
            return Storage(pid[2], kinds.get(pid[1], np.float32))

    d = Unpickler(z.open(f'{prefix}/data.pkl')).load()
    return d.get('params_ema', d.get('params', d))


def esrgan_session():
    """Real-ESRGAN's RRDBNet, rebuilt as an ONNX graph from the published weights."""
    W = load_torch_zip(fetch(*ESRGAN))
    nodes, inits, n = [], [], [0]

    def t():
        n[0] += 1; return f't{n[0]}'

    def const(v):
        name = t(); inits.append(numpy_helper.from_array(np.array(v, np.float32), name)); return name

    def op(kind, ins, **kw):
        o = t(); nodes.append(helper.make_node(kind, ins, [o], **kw)); return o

    def conv(x, p):
        for s in ('weight', 'bias'): inits.append(numpy_helper.from_array(W[f'{p}.{s}'].astype(np.float32), f'{p}.{s}'))
        return op('Conv', [x, f'{p}.weight', f'{p}.bias'], pads=[1, 1, 1, 1])

    lrelu = lambda x: op('LeakyRelu', [x], alpha=0.2)

    def rdb(x, p):
        feats = [x]
        for i in range(1, 5): feats.append(lrelu(conv(op('Concat', feats, axis=1) if len(feats) > 1 else x, f'{p}.conv{i}')))
        return op('Add', [op('Mul', [conv(op('Concat', feats, axis=1), f'{p}.conv5'), const(.2)]), x])

    feat = conv('input', 'conv_first'); body = feat
    for i in range(len({k.split('.')[1] for k in W if k.startswith('body.')})):
        o = body
        for j in (1, 2, 3): o = rdb(o, f'body.{i}.rdb{j}')
        body = op('Add', [op('Mul', [o, const(.2)]), body])
    feat = op('Add', [feat, conv(body, 'conv_body')])
    for p in ('conv_up1', 'conv_up2'): feat = lrelu(conv(op('Resize', [feat, '', const([1, 1, 2, 2])], mode='nearest'), p))
    out = conv(lrelu(conv(feat, 'conv_hr')), 'conv_last')
    nodes.append(helper.make_node('Identity', [out], ['output']))
    graph = helper.make_graph(nodes, 'rrdb', [helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 3, None, None])],
                              [helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 3, None, None])], inits)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)]); model.ir_version = 8
    return ort.InferenceSession(model.SerializeToString(), providers=['CPUExecutionProvider'])


def upscale(im, width, tile=192, pad=16):
    """2. 4x in overlapping tiles, then down to the final width with a little of the plain resize."""
    sess = esrgan_session()
    a = np.asarray(im).astype(np.float32) / 255
    H, W, _ = a.shape
    out = np.zeros((H * 4, W * 4, 3), np.float32)
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            y0, x0, y1, x1 = max(0, y - pad), max(0, x - pad), min(H, y + tile + pad), min(W, x + tile + pad)
            r = sess.run(None, {'input': a[y0:y1, x0:x1].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
            th, tw = min(tile, H - y), min(tile, W - x)
            out[y * 4:(y + th) * 4, x * 4:(x + tw) * 4] = r[(y - y0) * 4:(y - y0 + th) * 4, (x - x0) * 4:(x - x0 + tw) * 4]
        print(f'  upscaled rows to {min(H, y + tile)}/{H}')
    size = (width, round(width * H / W))
    sharp = np.asarray(Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8)).resize(size, Image.LANCZOS)).astype(np.float32)
    plain = np.asarray(im.resize(size, Image.LANCZOS)).astype(np.float32)
    return Image.fromarray(np.clip(sharp * .82 + plain * .18, 0, 255).astype(np.uint8))


def depth(im):
    """3. Near is 1, far is 0."""
    sess = ort.InferenceSession(fetch(*DEPTH), providers=['CPUExecutionProvider'])
    name = sess.get_inputs()[0].name
    mean, std = np.array([.485, .456, .406], np.float32), np.array([.229, .224, .225], np.float32)
    W, H = im.size

    def run(img, size):
        a = (np.asarray(img.resize((518, 518), Image.BICUBIC)).astype(np.float32) / 255 - mean) / std
        d = sess.run(None, {name: a.transpose(2, 0, 1)[None]})[0][0]
        return np.asarray(Image.fromarray(d).resize(size, Image.BICUBIC))

    norm = lambda d: (d - np.percentile(d, 1)) / (np.percentile(d, 99.5) - np.percentile(d, 1))
    full = norm(run(im, (W, H)))
    out, wsum = full * .35, np.full_like(full, .35)
    for x0 in (0, W - H):
        sq = norm(run(im.crop((x0, 0, x0 + H, H)), (H, H)))
        k = np.linalg.lstsq(np.stack([sq.ravel(), np.ones(sq.size)], 1), full[:, x0:x0 + H].ravel(), rcond=None)[0]
        w = np.minimum(1, np.minimum(np.arange(H), H - 1 - np.arange(H)) / 120 + .05)
        out[:, x0:x0 + H] += (sq * k[0] + k[1]) * w; wsum[:, x0:x0 + H] += w
    return np.clip(out / wsum, 0, 1)


def maps(im, d):
    """4. Depth, the sea and what may sway, in one picture; also where the sun is."""
    a = np.asarray(im).astype(np.float32)
    H, W, _ = a.shape
    L = a @ LUMA
    v, u = [g.astype(np.float32) for g in np.mgrid[0:H, 0:W]]
    u, v = u / W, v / H
    far = d < .1
    Lb = ndi.gaussian_filter(L, 6); Lb[v > .56] = 0
    sy, sx = np.unravel_index(np.argmax(Lb), Lb.shape)
    sea = ndi.binary_opening(far & (v > .615) & (v < .81) & (u > .1) & (u < .91) & (L > 150), iterations=1)
    water = ndi.gaussian_filter(sea.astype(np.float32), 1.5) * smooth(.61, .64, v) * (1 - smooth(.785, .81, v))
    pillar = ((u > .058) & (u < .119)) | ((u > .905) & (u < .958))
    curtains = ((u < .058) & (v < .56)) | ((u > .945) & (v < .74))
    leaves = (L < 120) & (d > .18) & ~pillar & (((u < .16) & (v > .13) & (v < .72)) | ((u > .87) & (v > .36) & (v < .7)))
    palms = (L < 150) & far & (v > .42) & (v < .83) & (u > .1) & (u < .91)
    sway = ndi.gaussian_filter(ndi.grey_dilation(np.maximum.reduce([curtains * 1., leaves * .75, palms * .3]), size=5), 2.5)
    dep = np.where(d < .12, d + .09 * smooth(.45, .84, v) * (1 - d / .12), d)
    dep = ndi.gaussian_filter(dep, 1.2)
    pack = np.dstack([dep, np.clip(water, 0, 1), np.clip(sway, 0, 1)])
    return Image.fromarray((pack * 255 + .5).astype(np.uint8)).resize((1024, 576), Image.LANCZOS), (sx / W, sy / H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, '..', '..', 'assets', 'img'))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    print('1. removing the mock-up writing'); src = clean(Image.open(os.path.join(HERE, 'source.webp')).convert('RGB'))
    print('2. upscaling'); photo = upscale(src, 2560)
    for w, q in ((960, 80), (1440, 78), (1920, 76), (2560, 72)):
        im = photo if w == photo.width else photo.resize((w, round(photo.height * w / photo.width)), Image.LANCZOS)
        im.save(os.path.join(args.out, f'hero-pavilion-{w}.webp'), 'WEBP', quality=q, method=6)
    print('3. depth'); d = depth(src)
    print('4. masks'); packed, sun = maps(src, d)
    packed.save(os.path.join(args.out, 'hero-pavilion-maps.webp'), 'WEBP', lossless=True, method=6)
    buf = io.BytesIO(); photo.resize((32, 18), Image.LANCZOS).save(buf, 'WEBP', quality=60)
    print(f'sun: data-sun="{sun[0]:.3f} {sun[1]:.3f}"')
    print('placeholder: data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode())


if __name__ == '__main__':
    main()
