"""
Contact solver: adjusts selected joint angles and the root position so that named
landmarks touch the floor (or props, walls) and grips close, without the body
passing through the floor.

A pose spec is the rig pose dict plus optional keys:
    contacts: list of (landmark, axis, value[, weight])   axis in "xyz"
    pairs:    list of (landmarkA, landmarkB[, weight])     -> made coincident
    rel:      list of (landmarkA, landmarkB, axis, value[, weight]) -> A[axis] - B[axis] = value
    free:     list of (dof, component, low, high)          -> dof values the solver may change
    floor:    height of the floor (default 0); nothing may go below it
"""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

import landmarks
import rig

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache" / "solved.json"
AX = {"x": 0, "y": 1, "z": 2}
SPEC_KEYS = {"contacts", "pairs", "rel", "free", "starts", "floor", "view", "props", "label", "palette", "mat", "overlay", "notes", "look"}


def _get(pose, key, comp):
    v = pose.get(key)
    if v is None and "_" in key:
        v = pose.get(key.rsplit("_", 1)[0])
    if v is None:
        return 0.0
    if np.isscalar(v):
        return float(v) if comp == 0 else 0.0
    v = list(v)
    return float(v[comp]) if comp < len(v) else 0.0


def _set(pose, key, comp, val):
    v = pose.get(key)
    if v is None and key in ("hip", "knee", "ankle", "toes", "clav", "shoulder", "elbow", "forearm", "wrist"):
        pass
    n = 3
    if v is None:
        v = [0.0] * n
    elif np.isscalar(v):
        v = [float(v)] + [0.0] * (n - 1)
    else:
        v = list(v) + [0.0] * (n - len(v))
    v[comp] = float(val)
    pose[key] = v


def _sample_idx(m):
    body = np.zeros(len(m.verts), bool)
    body[np.unique(m.quads[m.part == 0])] = True
    idx = np.where(body)[0]
    return idx[::41]


MODEL_VERSION = 5  # bump when the body model or landmarks change


def _key(spec):
    return hashlib.md5((json.dumps(spec, sort_keys=True, default=str) + str(MODEL_VERSION)).encode()).hexdigest()


def solve(spec, verbose=False):
    """Returns (pose dict with solved angles, root translation)."""
    spec = copy.deepcopy(spec)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    k = _key(spec)
    if k in cache:
        return cache[k]["pose"], np.array(cache[k]["trans"])
    m = rig.neutral()
    L = landmarks.landmarks()
    pose = {kk: vv for kk, vv in spec.items() if kk not in SPEC_KEYS}
    contacts = spec.get("contacts", [])
    pairs = spec.get("pairs", [])
    rel = spec.get("rel", [])
    free = spec.get("free", [])
    floor = spec.get("floor", 0.0)
    names = sorted({c[0] for c in contacts} | {p[0] for p in pairs} | {p[1] for p in pairs}
                   | {r_[0] for r_ in rel} | {r_[1] for r_ in rel})
    li = {n: j for j, n in enumerate(names)}
    lidx = np.array([L[n] for n in names], int) if names else np.zeros(0, int)
    # contact regions (lowest point of a small patch touches the target height)
    regs = [np.array(landmarks.region(c[0]), int) for c in contacts]
    rall = np.concatenate(regs) if regs else np.zeros(0, int)
    roff = np.cumsum([0] + [len(r_) for r_ in regs])
    samp = _sample_idx(m)
    x0 = np.array([_get(pose, f[0], f[1]) for f in free] + [0.0, 0.0, 0.0])
    lo = np.array([f[2] for f in free] + [-5, -5, -5.0])
    hi = np.array([f[3] for f in free] + [5, 5, 5.0])
    x0 = np.clip(x0, lo + 1e-6, hi - 1e-6)

    def build(x):
        P = copy.deepcopy(pose)
        for f, val in zip(free, x[:len(free)]):
            _set(P, f[0], f[1], val)
        return P

    def resid(x):
        P = build(x)
        mm, G = rig.posed(P)
        t = x[len(free):]
        r = []
        if len(lidx):
            pts = mm.skin_idx(G, lidx) + t
            rp = mm.skin_idx(G, rall) + t if len(rall) else None
            for j, c in enumerate(contacts):
                w = c[3] if len(c) > 3 else 1.0
                if c[1] == "z":
                    zz = rp[roff[j]:roff[j + 1], 2]
                    k = 0.004
                    val = -k * np.log(np.mean(np.exp(-(zz - zz.min()) / k))) + zz.min()
                else:
                    val = pts[li[c[0]], AX[c[1]]]
                r.append((val - c[2]) * 40 * w)
            for p in pairs:
                w = p[2] if len(p) > 2 else 1.0
                r.extend((pts[li[p[0]]] - pts[li[p[1]]]) * 25 * w)
            for q in rel:
                w = q[4] if len(q) > 4 else 1.0
                r.append((pts[li[q[0]], AX[q[2]]] - pts[li[q[1]], AX[q[2]]] - q[3]) * 25 * w)
        sp = mm.skin_idx(G, samp) + t
        pen = np.minimum(sp[:, 2] - floor, 0)
        r.extend(pen * 60)
        # stay close to the written angles
        r.extend((x[:len(free)] - x0[:len(free)]) * 0.004)
        r.extend(x[len(free):] * 0.0)
        return np.array(r)

    # initial root height: put the lowest point on the floor
    P0 = build(x0)
    mm, G = rig.posed(P0)
    sp = mm.skin_idx(G, samp)
    x0[-1] = floor - sp[:, 2].min()
    if free or contacts or pairs or rel:
        xs = np.array([10.0] * len(free) + [0.05] * 3)
        best = None
        rng = np.random.default_rng(7)
        starts = [x0]
        nstart = spec.get("starts", 1)
        for _ in range(nstart - 1):
            xr = x0.copy()
            span = (hi[:len(free)] - lo[:len(free)])
            xr[:len(free)] = np.clip(x0[:len(free)] + rng.uniform(-0.35, 0.35, len(free)) * span, lo[:len(free)] + 1e-6, hi[:len(free)] - 1e-6)
            starts.append(xr)
        for xi in starts:
            res = least_squares(resid, xi, bounds=(lo, hi), x_scale=xs, diff_step=1e-3, max_nfev=300)
            if best is None or res.cost < best.cost:
                best = res
        x = best.x
        if verbose:
            print("cost", best.cost, "nfev", best.nfev)
    else:
        x = x0
    P = build(x)
    trans = x[len(free):]
    # final: make sure nothing is below the floor
    mm, G = rig.posed(P)
    V = mm.skin_blend(G) + trans
    body = np.zeros(len(mm.verts), bool)
    body[np.unique(mm.quads[mm.part == 0])] = True
    dz = floor - V[body, 2].min()
    if dz > 0.002 or not contacts:
        trans = trans + np.array([0, 0, dz])
    cache[k] = {"pose": P, "trans": trans.tolist()}
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache))
    return P, trans


def mesh(spec):
    P, t = solve(spec)
    v, G = rig.pose_mesh(P)
    return v + t, G, P


def report(spec):
    """Print contact/pair errors after solving (for development)."""
    P, t = solve(spec)
    m, G = rig.posed(P)
    L = landmarks.landmarks()
    for c in spec.get("contacts", []):
        p = m.skin_idx(G, [L[c[0]]])[0] + t
        print(f"  contact {c[0]:12s} {c[1]}={p[AX[c[1]]]:+.3f} (target {c[2]})")
    for a, b, *_ in spec.get("pairs", []):
        pa = m.skin_idx(G, [L[a]])[0] + t
        pb = m.skin_idx(G, [L[b]])[0] + t
        print(f"  pair {a}-{b}: {np.linalg.norm(pa - pb):.3f} m")
    for f in spec.get("free", []):
        print(f"  free {f[0]}[{f[1]}] = {_get(P, f[0], f[1]):.1f}")
