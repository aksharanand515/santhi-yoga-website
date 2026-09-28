"""
Renders pose figures for the manual (cached PNGs in manual/figs3d/).

    info = pose_image("sirsasana", width=1000)
    info["file"]   -> path relative to the manual root ("figs3d/xxxx.png")
    info["w"], info["h"] -> pixel size
    info["project"](xyz) -> (u, v) in 0..1 image coordinates (for labels)
"""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "figs3d"
RENDER_VERSION = 7

PALETTES = {
    "default": ("#C69A78", "#7E8C66", "#3F4A2E"),
    "light": ("#C69A78", "#C8CCBC", "#A4A996"),
    "ghost": ("#E6DCCB", "#E6DCCB", "#E6DCCB"),
}


def _hash(obj):
    return hashlib.md5(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def _attr_digest(attrs):
    if not attrs:
        return None
    h = hashlib.md5()
    for k in sorted(attrs):
        h.update(k.encode())
        h.update(np.round(np.asarray(attrs[k], np.float32), 4).tobytes())
    return h.hexdigest()[:12]


def viewdir(view):
    az, el = np.radians(view[0]), np.radians(view[1])
    return np.array([-np.cos(az) * np.cos(el), -np.sin(az) * np.cos(el), np.sin(el)])


def _landmark(m, G, t, name):
    import landmarks
    return m.skin_idx(G, [landmarks.landmarks()[name]])[0] + t


def build_props(spec, verts, m, G, t, with_mat=True):
    import props3d as PR
    items = []  # (verts, faces, colour-key)
    for pr in spec.get("props", []):
        k = pr["kind"]
        if k == "block":
            p = _landmark(m, G, t, pr["at"])
            dims = {"tall": (0.075, 0.15, 0.23), "mid": (0.075, 0.23, 0.15), "low": (0.15, 0.23, 0.075)}[pr.get("stand", "tall")]
            V, F = PR.box((p[0], p[1], dims[2] / 2), dims)
            items.append((V, F, "block"))
        elif k == "blanket":
            sh = (_landmark(m, G, t, "shoulderback_L") + _landmark(m, G, t, "shoulderback_R")) / 2
            cr = _landmark(m, G, t, "crown")
            d = cr - sh
            d[2] = 0
            d /= np.linalg.norm(d) + 1e-9
            L, W, H = pr.get("size", (0.62, 0.44, 0.06))
            c = sh - d * (L / 2 - 0.035)
            yaw = np.arctan2(d[1], d[0])
            for j, (hh, col) in enumerate(((H * 0.5, "blanket"), (H * 0.5, "blanket2"))):
                V, F = PR.box((c[0], c[1], hh / 2 + j * hh), (L, W, hh * 0.96), yaw)
                items.append((V, F, col))
        elif k == "bolster":
            a = _landmark(m, G, t, pr.get("frm", "lowback"))
            b = _landmark(m, G, t, pr.get("to", "occiput"))
            r = pr.get("r", 0.10)
            d = b - a
            d[2] = 0
            d /= np.linalg.norm(d)
            p0 = a - d * 0.05
            p1 = p0 + d * 0.65
            V, F = PR.cylinder((p0[0], p0[1], r), (p1[0], p1[1], r), r, 32)
            items.append((V, F, "bolster"))
        elif k == "strap":
            hands = [_landmark(m, G, t, h) for h in pr["frm"]]
            feet = [_landmark(m, G, t, f) for f in pr["around"]]
            # the strap runs from the hand(s), round the sole(s) and back
            sole = [f + np.array([0, 0, 0]) for f in feet]
            if len(hands) == 1:
                h = hands[0]
                f = sole[0]
                dirv = f - h
                dirv /= np.linalg.norm(dirv)
                side = np.cross(dirv, [0, 0, 1.0])
                side /= np.linalg.norm(side) + 1e-9
                pts = [h + side * 0.012, f + side * 0.03 + dirv * 0.02, f + dirv * 0.035, f - side * 0.03 + dirv * 0.02, h - side * 0.012]
            else:
                pts = [hands[0], sole[0] + (sole[0] - hands[0]) / np.linalg.norm(sole[0] - hands[0]) * 0.03,
                       sole[1] + (sole[1] - hands[1]) / np.linalg.norm(sole[1] - hands[1]) * 0.03, hands[1]]
            V, F = PR.tube(pts, 0.006)
            items.append((V, F, "strap"))
        elif k == "chair":
            a = (_landmark(m, G, t, "ankle_L") + _landmark(m, G, t, "ankle_R")) / 2
            hip = (_landmark(m, G, t, "sit_L") + _landmark(m, G, t, "sit_R")) / 2
            d = a - hip
            d[2] = 0
            d /= np.linalg.norm(d)
            c = a + d * 0.10
            facing = np.arctan2(d[1], d[0]) - np.pi / 2
            for V, F, col in PR.chair((c[0], c[1]), pr.get("seat", 0.46), facing):
                items.append((V, F, col))
        elif k == "wall":
            ys = verts[:, 1]
            y0 = ys.min() - 0.004
            lo, hi = verts.min(0), verts.max(0)
            V, F = PR.box(((lo[0] + hi[0]) / 2, y0 - 0.02, 0.8), (2.6, 0.04, 1.6))
            items.append((V, F, "wall"))
    if with_mat:
        V, F = PR.mat_for(verts)
        items.append((V, F, "mat"))
    return items


def pose_image(key, width=1000, view=None, mat=False, palette="default", overlays=(), spec_overrides=None,
               margin=0.05, samples=64, scale=None, extra_attrs=None, crop_floor=False, crop=None):
    import poses3d
    spec = copy.deepcopy(poses3d.P[key]) if isinstance(key, str) else copy.deepcopy(key)
    if spec_overrides:
        spec.update(spec_overrides)
    view = view or spec.get("view", (0, 4))
    job = dict(spec=spec, width=width, view=view, mat=mat, palette=palette, overlays=overlays, margin=margin,
               samples=samples, scale=scale, v=RENDER_VERSION, extra=_attr_digest(extra_attrs))
    if crop is not None:
        job["crop"] = crop
    h = _hash(job)
    png = OUT / f"{key if isinstance(key, str) else 'pose'}-{h}.png"
    meta = png.with_suffix(".json")
    if png.exists() and meta.exists():
        info = json.loads(meta.read_text())
    else:
        info = _render(spec, png, width, view, mat, palette, overlays, margin, samples, scale, extra_attrs, crop)
        meta.write_text(json.dumps(info))
    return _finish(info, png)


def _finish(info, png):
    c = np.array(info["center"])
    rt, up = np.array(info["right"]), np.array(info["up"])
    sw, sh = info["span"]

    def project(p):
        p = np.asarray(p, float) - c
        return (0.5 + (p @ rt) / sw, 0.5 - (p @ up) / sh)
    info = dict(info)
    info["file"] = "figs3d/" + png.name
    info["project"] = project
    return info


def _render(spec, png, width, view, mat, palette, overlays, margin, samples, scale, extra_attrs, crop=None):
    import look
    import render3d as R
    import rig
    import solve
    from props3d import COL

    v, G, P = solve.mesh(spec)
    m = rig.neutral()
    t = solve.solve(spec)[1]
    items = build_props(spec, v, m, G, t, with_mat=mat)
    d = viewdir(view)
    up0 = np.array([0, 0, 1.0]) if abs(d[2]) < 0.95 else np.array([0, 1.0, 0])
    rt = np.cross(up0, d)
    rt /= np.linalg.norm(rt)
    up = np.cross(d, rt)
    vv = v if crop is None else v[(v[:, 2] >= crop[0]) & (v[:, 2] <= crop[1])]
    if crop is not None and len(crop) > 2:   # also limit the horizontal extent (image plane)
        uu = vv @ rt
        vv = vv[np.abs(uu - np.median(uu)) <= crop[2]]
    pts = [vv] + [V for V, F, col in items if col not in ("mat", "wall")]
    allp = np.concatenate(pts)
    u, w = allp @ rt, allp @ up
    umin, umax, wmin, wmax = u.min(), u.max(), w.min(), w.max()
    if mat:  # include the visible part of the mat, a little
        mv = [V for V, F, col in items if col == "mat"][0]
        wmin = min(wmin, (mv @ up).min() * 0.3 + wmin * 0.7)
    cu, cw = (umin + umax) / 2, (wmin + wmax) / 2
    spanu, spanw = (umax - umin) * (1 + 2 * margin), (wmax - wmin) * (1 + 2 * margin)
    if scale:
        spanu = max(spanu, scale[0])
        spanw = max(spanw, scale[1])
    aspect = spanw / spanu
    W = int(width) if aspect <= 1 else int(round(width / aspect))  # `width` is the long side
    Hpx = max(8, int(round(W * aspect)))
    # camera centre in 3D: pick a point on the line of sight through (cu, cw)
    c3 = rt * cu + up * cw + d * float((v @ d).mean())  # include depth so the lights sit around the figure
    R.reset()
    skin, top, legs = PALETTES[palette]
    fmat = R.figure_material("fig", skin, top, legs, overlays)
    A = dict(look.garment_fields())
    if extra_attrs:
        A.update(extra_attrs)
    R.add_mesh("body", v, m.quads, fmat, attrs=A)
    mats = {}
    for i, (V, F, col) in enumerate(items):
        if col not in mats:
            rough = 0.9 if col in ("mat", "blanket", "blanket2", "wall", "bolster") else 0.6
            mats[col] = R.material(col, COL[col], rough)
        ob = R.add_mesh(f"prop{i}", V, F, mats[col], smooth=col in ("bolster", "strap", "chair"), subdiv=0, fix_normals=True)
        if col == "wall":
            ob.visible_shadow = False   # a wall would shade the whole floor (shadow catcher)
    if crop is None or crop[0] <= 0.01:
        R.floor(0)
    radius = max(spanu, spanw) / 2
    R.lights(c3, max(radius, 0.6))
    cam = R.camera(c3, d, max(spanu, spanw))
    import bpy
    bpy.context.scene.camera.data.sensor_fit = "HORIZONTAL" if spanu >= spanw else "VERTICAL"
    bpy.context.scene.camera.data.ortho_scale = spanu if spanu >= spanw else spanw
    OUT.mkdir(exist_ok=True)
    R.render(png, (W, Hpx), samples)
    _optimise(png)
    return {"w": W, "h": Hpx, "center": c3.tolist(), "right": rt.tolist(), "up": up.tolist(), "span": [spanu, spanw]}


def _optimise(png):
    from PIL import Image
    im = Image.open(png).convert("RGBA")
    # trim fully transparent borders is avoided (keeps projection exact); just recompress
    im.save(png, optimize=True, compress_level=9)


def points(key, pts, spec_overrides=None):
    """Posed 3D positions of named points.
    pts: {name: landmark-name | (bone, rest_xyz)}; rest_xyz is given on the neutral (standing) body
    and follows `bone`."""
    import landmarks
    import rig
    import solve
    import poses3d
    spec = copy.deepcopy(poses3d.P[key]) if isinstance(key, str) else copy.deepcopy(key)
    if spec_overrides:
        spec.update(spec_overrides)
    P, t = solve.solve(spec)
    m, G = rig.posed(P)
    L = landmarks.landmarks()
    out = {}
    for name, p in pts.items():
        if isinstance(p, str):
            out[name] = m.skin_idx(G, [L[p]])[0] + t
        else:
            bone, xyz = p
            out[name] = (G[m.i(bone)] @ np.array([*xyz, 1.0]))[:3] + t
    return out
