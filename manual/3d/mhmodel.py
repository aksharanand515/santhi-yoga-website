"""
Loader for the MakeHuman base mesh, default skeleton and skinning weights.

The MakeHuman assets (base mesh, skeleton, weights) are released under CC0 1.0
(see mh/LICENSE.ASSETS.md). Coordinates are converted to a Z-up, metre-scaled
frame with the figure facing -Y (Blender's front view):

    X  = the figure's left            (MakeHuman +X)
    -Y = the figure's front / anterior (MakeHuman +Z)
    Z  = up                            (MakeHuman +Y)
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MH = HERE / "mh"
CACHE = HERE / "cache" / "mhmodel.npz"

KEEP_GROUPS = {"body", "helper-l-eye", "helper-r-eye"}
SCALE = 0.1  # MakeHuman decimetres -> metres


def _to_zup(v):
    v = np.asarray(v, float)
    return np.stack([v[..., 0], -v[..., 2], v[..., 1]], axis=-1) * SCALE


def _parse_obj():
    verts, faces, groups = [], [], []
    group = None
    with open(MH / "base.obj", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("v "):
                verts.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("g "):
                group = line.split(None, 1)[1].strip()
            elif line.startswith("f "):
                idx = [int(p.split("/")[0]) - 1 for p in line.split()[1:]]
                faces.append(idx)
                groups.append(group)
    return np.array(verts), faces, groups


# body-shape targets (CC0, MakeHuman macrodetails) and their weights
TARGETS = {
    "universal-female-young-maxmuscle-averageweight": 0.25,
    "universal-male-young-maxmuscle-averageweight": 0.25,
    "universal-female-young-averagemuscle-minweight": 0.10,
    "universal-male-young-averagemuscle-minweight": 0.10,
}


def _apply_targets(verts, targets):
    v = verts.copy()
    for name, w in targets.items():
        if not w:
            continue
        for line in (MH / "targets" / f"{name}.target").read_text().splitlines():
            if not line or line[0] == "#":
                continue
            i, dx, dy, dz = line.split()
            v[int(i)] += w * np.array([float(dx), float(dy), float(dz)])
    return v


def build_cache(targets=None):
    verts_all, faces_all, groups = _parse_obj()
    verts_all = _apply_targets(verts_all, TARGETS if targets is None else targets)
    skel = json.loads((MH / "default.mhskel").read_text())
    weights = json.loads((MH / "default_weights.mhw").read_text())["weights"]

    # joints: mean of reference vertices (in the full vertex numbering)
    joints = {name: verts_all[idx].mean(axis=0) for name, idx in skel["joints"].items()}

    keep = [i for i, g in enumerate(groups) if g in KEEP_GROUPS]
    used = sorted({v for i in keep for v in faces_all[i]})
    remap = -np.ones(len(verts_all), int)
    remap[used] = np.arange(len(used))
    quads = []
    part = []
    for i in keep:
        f = [remap[v] for v in faces_all[i]]
        if len(f) == 3:
            f = f + [f[2]]
        quads.append(f)
        part.append(0 if groups[i] == "body" else 1)
    quads = np.array(quads, int)
    verts = verts_all[used]

    bone_names = [n for n in skel["bones"]]
    order = []
    # topological order (parents first)
    placed = set()
    while len(order) < len(bone_names):
        for n in bone_names:
            p = skel["bones"][n]["parent"]
            if n not in placed and (p is None or p in placed):
                order.append(n)
                placed.add(n)
    parents = np.array([order.index(skel["bones"][n]["parent"]) if skel["bones"][n]["parent"] else -1 for n in order])
    heads = np.array([joints[skel["bones"][n]["head"]] for n in order])
    tails = np.array([joints[skel["bones"][n]["tail"]] for n in order])

    # sparse weights -> dense top-4
    W = np.zeros((len(verts), len(order)), np.float32)
    for bname, pairs in weights.items():
        if bname not in order:
            continue
        bi = order.index(bname)
        for v, w in pairs:
            if remap[v] >= 0:
                W[remap[v], bi] = w
    # eyes: follow the head rigidly if unweighted
    s = W.sum(1)
    W[s == 0, order.index("head")] = 1.0
    W /= W.sum(1, keepdims=True)
    k = 4
    top = np.argsort(-W, axis=1)[:, :k]
    topw = np.take_along_axis(W, top, axis=1)
    topw /= topw.sum(1, keepdims=True)

    CACHE.parent.mkdir(exist_ok=True)
    np.savez_compressed(CACHE, verts=_to_zup(verts), quads=quads, part=np.array(part),
                        names=np.array(order), parents=parents,
                        heads=_to_zup(heads), tails=_to_zup(tails),
                        widx=top, wval=topw.astype(np.float32))


def load():
    if not CACHE.exists():
        build_cache()
    d = np.load(CACHE, allow_pickle=False)
    return {k: d[k] for k in d.files}


if __name__ == "__main__":
    build_cache()
    m = load()
    v = m["verts"]
    print("verts", v.shape, "quads", m["quads"].shape, "bones", len(m["names"]))
    print("height", v[:, 2].max() - v[:, 2].min(), "zmin", v[:, 2].min())
    for n in ["root", "spine05", "spine01", "neck01", "head", "upperleg01.L", "lowerleg01.L", "foot.L",
              "clavicle.L", "shoulder01.L", "upperarm01.L", "lowerarm01.L", "wrist.L"]:
        i = list(m["names"]).index(n)
        print(f"{n:14s} head {np.round(m['heads'][i], 3)} tail {np.round(m['tails'][i], 3)}")
