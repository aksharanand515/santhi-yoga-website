"""
Generic cached renderer for anatomy scenes (bones, discs, muscles, translucent body).

    info = render_scene(key, objects, view=(0, 0), width=900, points={"L5": xyz, ...})
    info["file"]  -> "figs3d/<key>-<hash>.png"
    info["pts"]   -> {name: (u, v)} projected positions in 0..1 image coordinates
    info["w"], info["h"]

objects: list of dicts {verts, faces, color, alpha=1, rough=0.55, smooth=True, subdiv=1, emit=None}
"""
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figs3d"
VERSION = 4


def _digest(objects, extra):
    h = hashlib.md5()
    for o in objects:
        h.update(np.round(np.asarray(o["verts"], float), 5).tobytes())
        h.update(json.dumps([o.get("color"), o.get("alpha", 1), o.get("rough", 0.55), o.get("subdiv", 1),
                             o.get("smooth", True), o.get("emit")]).encode())
    h.update(json.dumps(extra, sort_keys=True, default=str).encode())
    return h.hexdigest()[:16]


def viewdir(view):
    az, el = np.radians(view[0]), np.radians(view[1])
    return np.array([-np.cos(az) * np.cos(el), -np.sin(az) * np.cos(el), np.sin(el)])


def render_scene(key, objects, view=(0, 0), width=900, margin=0.04, points=None, samples=64, fit=None,
                 floor=False, light_scale=1.0, up=None):
    points = points or {}
    extra = dict(view=view, width=width, margin=margin, samples=samples, fit=fit, floor=floor, v=VERSION,
                 ls=light_scale, up=up)
    h = _digest(objects, extra)
    png = OUT / f"{key}-{h}.png"
    meta = png.with_suffix(".json")
    d = viewdir(view)
    up0 = np.array(up if up is not None else ([0, 0, 1.0] if abs(d[2]) < 0.95 else [0, 1.0, 0]))
    rt = np.cross(up0, d)
    rt /= np.linalg.norm(rt)
    upv = np.cross(d, rt)
    allp = np.concatenate([np.asarray(o["verts"], float) for o in objects] if fit is None else [np.asarray(fit, float)])
    u, w = allp @ rt, allp @ upv
    cu, cw = (u.min() + u.max()) / 2, (w.min() + w.max()) / 2
    spanu, spanw = np.ptp(u) * (1 + 2 * margin), np.ptp(w) * (1 + 2 * margin)
    W = int(width)
    Hpx = max(8, int(round(W * spanw / spanu)))
    c3 = rt * cu + upv * cw

    def project(p):
        p = np.asarray(p, float) - c3
        return float(0.5 + (p @ rt) / spanu), float(0.5 - (p @ upv) / spanw)
    if not (png.exists() and meta.exists()):
        import bpy
        import render3d as R
        R.reset()
        for i, o in enumerate(objects):
            col = o.get("color", "#E8DCC4")
            mat = R.material(f"m{i}", col, o.get("rough", 0.55), alpha=o.get("alpha", 1.0), emission=o.get("emit"))
            R.add_mesh(f"o{i}", o["verts"], o["faces"], mat, smooth=o.get("smooth", True), subdiv=o.get("subdiv", 1),
                       fix_normals=o.get("fix", True))
        if floor:
            R.floor(0)
        R.suns(strength=light_scale)
        R.camera(c3, d, max(spanu, spanw))
        cam = bpy.context.scene.camera.data
        cam.sensor_fit = "HORIZONTAL" if spanu >= spanw else "VERTICAL"
        cam.ortho_scale = spanu if spanu >= spanw else spanw
        if up is not None:
            ob = bpy.context.scene.camera
            from mathutils import Vector
            ob.rotation_euler = Vector(-d).to_track_quat("-Z", "Y").to_euler()
            # roll so that `up` points up in the image
            import mathutils
            m = mathutils.Matrix((tuple(rt), tuple(upv), tuple(d))).transposed()
            ob.rotation_euler = m.to_euler()
        OUT.mkdir(exist_ok=True)
        R.render(png, (W, Hpx), samples)
        from fig3d import _optimise
        _optimise(png)
        meta.write_text(json.dumps({"w": W, "h": Hpx}))
    info = json.loads(meta.read_text())
    info["file"] = "figs3d/" + png.name
    info["pts"] = {k: project(v) for k, v in points.items()}
    info["project"] = project
    return info
