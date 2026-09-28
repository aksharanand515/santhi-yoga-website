"""Quick contact sheets of posed figures for checking poses during development."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rig  # noqa: E402
import render3d as R  # noqa: E402

VIEWS = {"side": (1, 0, 0), "rside": (-1, 0, 0), "front": (0, -1, 0), "back": (0, 1, 0),
         "three": (0.8, -1.0, 0.35), "top": (0, -0.2, 1), "rthree": (-0.8, -1.0, 0.35)}


def place(v):
    v = v.copy()
    v[:, 2] -= v[:, 2].min()
    c = (v.min(0) + v.max(0)) / 2
    v[:, 0] -= c[0]
    v[:, 1] -= c[1]
    return v


PALETTES = {
    "default": ("#C69A78", "#7E8C66", "#3F4A2E"),
    "light": ("#C69A78", "#C9CCBB", "#A7AC98"),
}


def shot(verts, quads, view, path, res=360, samples=20, extra=None, palette="default", overlays=(), attrs=None):
    import look
    R.reset()
    skin, top, legs = PALETTES[palette]
    mat = R.figure_material("fig", skin, top, legs, overlays)
    A = dict(look.garment_fields())
    A.update(attrs or {})
    R.add_mesh("body", verts, quads, mat, attrs=A)
    R.floor(0)
    lo, hi = verts.min(0), verts.max(0)
    c = (lo + hi) / 2
    d = viewdir(view) if isinstance(view, str) else np.array(view, float)
    d /= np.linalg.norm(d)
    # extent perpendicular to view
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([0, 1.0, 0])
    rt = np.cross(up, d); rt /= np.linalg.norm(rt)
    up2 = np.cross(d, rt)
    pr = verts - c
    ext = max(np.ptp(pr @ rt), np.ptp(pr @ up2)) * 1.12
    cen = c + rt * ((pr @ rt).max() + (pr @ rt).min()) / 2 + up2 * ((pr @ up2).max() + (pr @ up2).min()) / 2
    R.lights(cen, max(ext, 1.0) / 2)
    R.camera(cen, d, ext)
    R.render(path, (res, res), samples)


def viewdir(view):
    if isinstance(view, str):
        return np.array(VIEWS[view], float)
    az, el = np.radians(view[0]), np.radians(view[1])
    return np.array([-np.cos(az) * np.cos(el), -np.sin(az) * np.cos(el), np.sin(el)])


def spec_sheet(names, out, cols=4, res=340):
    import poses3d
    import solve
    tiles = []
    m = rig.neutral()
    for k, n in enumerate(names):
        spec = poses3d.P[n]
        v, G, P = solve.mesh(spec)
        p = HERE / "out" / f"spec_{n}.png"
        shot(v, m.quads, viewdir(spec.get("view", (0, 4))), p, res)
        im = Image.open(p)
        bg = Image.new("RGB", im.size, (250, 246, 238))
        bg.paste(im, (0, 0), im)
        ImageDraw.Draw(bg).text((6, 4), n, fill=(60, 60, 60))
        tiles.append(bg)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * res, rows * res), (255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * res, (k // cols) * res))
    sheet.save(out)
    return out


def contact(items, out, cols=4, res=360):
    """items: list of (label, pose_dict, view)."""
    tiles = []
    m = rig.neutral()
    for k, (label, pose, view) in enumerate(items):
        v, _ = rig.pose_mesh(pose)
        v = place(v)
        p = HERE / "out" / f"sheet_{k}.png"
        shot(v, m.quads, view, p, res)
        im = Image.open(p)
        bg = Image.new("RGB", im.size, (250, 246, 238))
        bg.paste(im, (0, 0), im)
        ImageDraw.Draw(bg).text((6, 4), label, fill=(60, 60, 60))
        tiles.append(bg)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * res, rows * res), (255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * res, (k // cols) * res))
    sheet.save(out)
    return out
