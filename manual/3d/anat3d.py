"""
Anatomy components derived from the OpenSim skeleton (see skeleton.py): individual
vertebrae and discs, pelvis, limb bones, and named bony landmarks for labels and muscle
attachments. All coordinates in the manual frame (X left, -Y anterior, Z up, metres).
"""
from functools import lru_cache

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

import skeleton

BONE = "#E9DFCB"
BONE_DARK = "#D9CBAE"
DISC = "#9FB6C9"
CERV = "#E3D2B2"
THOR = "#EADFC8"
LUMB = "#E1CFAE"
SACR = "#D8C4A0"


def _components(v, F):
    rows, cols = [], []
    for f in F:
        for a, b in zip(f, list(f[1:]) + [f[0]]):
            rows.append(a)
            cols.append(b)
    A = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(v), len(v)))
    n, lab = connected_components(A, directed=False)
    return n, lab


def _submesh(v, F, idx):
    idx = np.asarray(idx)
    remap = -np.ones(len(v), int)
    remap[idx] = np.arange(len(idx))
    FF = [[remap[i] for i in f] for f in F if all(remap[i] >= 0 for i in f)]
    return v[idx], FF


def mesh(body, file=None):
    """Concatenate the meshes of an OpenSim body (optionally one file)."""
    V, F, off = [], [], 0
    for mf, v, f in skeleton.bones()[body]:
        if file and mf != file:
            continue
        V.append(v)
        F.extend([[i + off for i in ff] for ff in f])
        off += len(v)
    return np.concatenate(V), F


@lru_cache(None)
def spine():
    """{'C1'..'C7','T1'..'T12','L1'..'L5': (v, F)}, discs: list of (v, F) with the level below."""
    v, F = mesh("torso", "hat_spine.vtp")
    n, lab = _components(v, F)
    comps = []
    for k in range(n):
        idx = np.where(lab == k)[0]
        comps.append((v[idx, 2].mean(), idx))
    comps.sort(key=lambda c: -c[0])
    verts, discs = [], []
    for zc, idx in comps:
        (discs if len(idx) <= 60 else verts).append(idx)
    names = [f"C{i}" for i in range(1, 8)] + [f"T{i}" for i in range(1, 13)] + [f"L{i}" for i in range(1, 6)]
    assert len(verts) == 24, len(verts)
    V = {nm: _submesh(v, F, idx) for nm, idx in zip(names, verts)}
    D = [_submesh(v, F, idx) for idx in discs]
    return V, D


@lru_cache(None)
def sacrum():
    return mesh("pelvis", "sacrum.vtp")


def region_of(name):
    return {"C": "cervical", "T": "thoracic", "L": "lumbar"}[name[0]]


def spinous_tip(vmesh):
    v = vmesh[0]
    return v[np.argmax(v[:, 1])]  # most posterior point


def body_centre(vmesh):
    v = vmesh[0]
    # vertebral body: the anterior part
    y0 = np.percentile(v[:, 1], 25)
    sel = v[v[:, 1] <= y0]
    return sel.mean(0)


@lru_cache(None)
def pelvis_landmarks():
    rv, _ = mesh("pelvis", "r_pelvis.vtp")
    lv, _ = mesh("pelvis", "l_pelvis.vtp")
    sv, _ = sacrum()
    L = {}
    for s, v, sx in (("R", rv, -1), ("L", lv, 1)):
        L[f"crest_{s}"] = v[np.argmax(v[:, 2])]
        # ASIS: anterior-most point of the upper part
        up = v[v[:, 2] > np.percentile(v[:, 2], 70)]
        L[f"asis_{s}"] = up[np.argmin(up[:, 1])]
        low = v[v[:, 2] < np.percentile(v[:, 2], 15)]
        L[f"ischial_{s}"] = low[np.argmax(low[:, 1] - low[:, 2] * 0.5)]
        med = v[np.abs(v[:, 0]) < np.percentile(np.abs(v[:, 0]), 8)]
        L[f"pubis_{s}"] = med[np.argmin(med[:, 1] + med[:, 2] * 0.2)]
        L[f"psis_{s}"] = up[np.argmax(up[:, 1])]
    L["sacrum"] = sv.mean(0)
    L["coccyx"] = sv[np.argmin(sv[:, 2])]
    L["si_R"] = sv[np.argmin(sv[:, 0] + 0.3 * sv[:, 2])] * 0 + np.array([-0.045, sv[:, 1].mean(), np.percentile(sv[:, 2], 80)])
    L["si_L"] = L["si_R"] * np.array([-1, 1, 1])
    for s, sx in (("R", -1), ("L", 1)):
        L[f"hip_{s}"] = skeleton.point("pelvis", [-0.056276, -0.07849, 0.07726 * (1 if s == "R" else -1)])
    return L


@lru_cache(None)
def femur_landmarks():
    L = {}
    for s in ("R", "L"):
        v, _ = mesh(f"femur_{s.lower()}")
        sx = 1 if s == "L" else -1
        top = v[v[:, 2] > np.percentile(v[:, 2], 88)]
        L[f"gtroch_{s}"] = top[np.argmax(top[:, 0] * sx)]
        L[f"fhead_{s}"] = top[np.argmin(top[:, 0] * sx)]
        L[f"neck_{s}"] = (L[f"gtroch_{s}"] + L[f"fhead_{s}"]) / 2
        mid = v[(v[:, 2] > np.percentile(v[:, 2], 70)) & (v[:, 2] < np.percentile(v[:, 2], 82))]
        L[f"ltroch_{s}"] = mid[np.argmax(mid[:, 1] - mid[:, 0] * sx * 0.5)]
        low = v[v[:, 2] < np.percentile(v[:, 2], 8)]
        L[f"medcond_{s}"] = low[np.argmin(low[:, 0] * sx)]
        L[f"latcond_{s}"] = low[np.argmax(low[:, 0] * sx)]
    return L
