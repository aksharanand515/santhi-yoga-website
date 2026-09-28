"""Named surface points on the neutral figure (vertex indices), used for contacts, grips and labels."""
from functools import lru_cache

import numpy as np

import look
import rig


def _nearest(v, cand, target):
    idx = np.where(cand)[0]
    d = np.linalg.norm(v[idx] - target, axis=1)
    return int(idx[np.argmin(d)])


def _extreme(v, cand, direction, near=None, radius=None):
    idx = np.where(cand)[0]
    if near is not None:
        d = np.linalg.norm(v[idx] - near, axis=1)
        idx = idx[d < radius]
    return int(idx[np.argmax(v[idx] @ np.asarray(direction, float))])


@lru_cache(None)
def landmarks():
    m = rig.neutral()
    v = m.verts
    H = lambda b: m.heads[m.i(b)]  # noqa: E731
    T = lambda b: m.tails[m.i(b)]  # noqa: E731
    head = look.bone_share(m, ["head", "jaw", "eye", "special", "oris", "levator", "oculi", "orbicularis", "risorius", "temporalis", "tongue"]) > 0.5
    body = np.zeros(len(v), bool)
    body[np.unique(m.quads[m.part == 0])] = True
    L = {}
    L["crown"] = _extreme(v, head & body, [0, 0.12, 1])
    L["forehead"] = _extreme(v, head & body, [0, -1, 0.6])
    L["nose"] = _extreme(v, head & body, [0, -1, 0])
    L["chin"] = _extreme(v, head & body, [0, -0.7, -1])
    L["occiput"] = _extreme(v, head & body, [0, 1, 0.15])
    zc = lambda z: np.abs(v[:, 2] - z) < 0.012  # noqa: E731
    mid = np.abs(v[:, 0]) < 0.02
    L["c7"] = _extreme(v, body & zc(H("neck01")[2]) & mid, [0, 1, 0])
    L["chest"] = _extreme(v, body & zc(1.26) & mid, [0, -1, 0])
    L["belly"] = _extreme(v, body & zc(1.02) & mid, [0, -1, 0])
    L["pubis"] = _extreme(v, body & zc(0.905) & mid, [0, -1, 0])
    L["sacrum"] = _extreme(v, body & zc(H("upperleg01.L")[2] + 0.05) & mid, [0, 1, 0])
    L["upperback"] = _extreme(v, body & zc(1.24) & mid, [0, 1, 0])
    L["midback"] = _extreme(v, body & zc(1.10) & mid, [0, 1, 0])
    L["lowback"] = _extreme(v, body & zc(1.00) & mid, [0, 1, 0])
    for s, sx in (("L", 1), ("R", -1)):
        near = body & (np.abs(v[:, 0] - sx * 0.075) < 0.015)
        L[f"back_{s}"] = _extreme(v, near & zc(1.12), [0, 1, 0])
        L[f"lowback_{s}"] = _extreme(v, near & zc(1.01), [0, 1, 0])
    for s, sx in (("L", 1), ("R", -1)):
        hip, knee, ank = H(f"upperleg01.{s}"), H(f"lowerleg01.{s}"), H(f"foot.{s}")
        sh, el, wr = H(f"upperarm01.{s}"), H(f"lowerarm01.{s}"), H(f"wrist.{s}")
        hand = look.bone_share(m, [f"wrist.{s}", f"metacarpal", f"finger"]) > 0.5
        hand &= np.sign(v[:, 0]) == sx
        foot = look.bone_share(m, [f"foot.{s}", "toe"]) > 0.5
        foot &= np.sign(v[:, 0]) == sx
        side = np.sign(v[:, 0]) == sx
        armv = look.bone_share(m, [f"upperarm01.{s}", f"upperarm02.{s}", f"lowerarm01.{s}", f"lowerarm02.{s}", f"wrist.{s}"]) > 0.5
        noarm = body & side & (look.bone_share(m, ["upperarm", "lowerarm", "wrist", "finger", "metacarpal"]) < 0.08)
        mcp = H(f"finger3-1.{s}")
        palm_c = (wr * 0.45 + mcp * 0.55)
        L[f"palm_{s}"] = _nearest(v, hand, palm_c + np.array([-sx * 0.04, 0, 0]))
        L[f"backhand_{s}"] = _nearest(v, hand, palm_c + np.array([sx * 0.04, 0, 0]))
        L[f"fingertip_{s}"] = _extreme(v, hand, [0, -0.05, -1])
        L[f"thumbtip_{s}"] = _nearest(v, hand, T(f"finger1-3.{s}") + np.array([0, -0.01, -0.005]))
        L[f"knuckles_{s}"] = _nearest(v, hand, mcp + np.array([sx * 0.03, 0, 0]))
        L[f"wristpalm_{s}"] = _nearest(v, hand, wr + np.array([-sx * 0.04, 0, -0.01]))
        L[f"elbow_{s}"] = _extreme(v, armv, [0, 1, 0], near=el, radius=0.05)
        fa = (el * 0.55 + wr * 0.45)
        L[f"forearm_{s}"] = _nearest(v, armv, fa + np.array([-sx * 0.06, 0, 0]))
        L[f"forearmback_{s}"] = _nearest(v, armv, fa + np.array([sx * 0.06, 0, 0]))
        L[f"ulnar_{s}"] = _nearest(v, armv, fa + np.array([0, 0.06, 0]))
        L[f"ulnarwrist_{s}"] = _nearest(v, armv, wr + np.array([0, 0.05, 0.02]))
        L[f"triceps_{s}"] = _extreme(v, body & side, [0, 1, 0], near=sh * 0.3 + el * 0.7, radius=0.05)
        L[f"shoulder_{s}"] = _extreme(v, body & side, [sx * 0.2, 0.3, 1], near=sh, radius=0.08)
        L[f"shoulderback_{s}"] = _extreme(v, body & side & zc(sh[2] - 0.05), [sx * 0.1, 1, 0])
        L[f"scapula_{s}"] = _nearest(v, body & side, np.array([sx * 0.08, 0.15, 1.20]))
        L[f"heel_{s}"] = _extreme(v, foot, [0, 0.8, -1])
        L[f"ball_{s}"] = _nearest(v, foot, H(f"toe1-1.{s}") + np.array([sx * 0.0, 0.0, -0.035]))
        L[f"ball5_{s}"] = _nearest(v, foot, H(f"toe5-1.{s}") + np.array([0, 0.0, -0.03]))
        L[f"toe_{s}"] = _extreme(v, foot, [0, -1, -0.1])
        L[f"toepad_{s}"] = _extreme(v, foot, [0, -1, -1.2])
        midfoot = (ank + H(f"toe2-1.{s}")) / 2
        L[f"dorsum_{s}"] = _extreme(v, foot, [0, -0.3, 1], near=midfoot, radius=0.05)
        L[f"ankle_{s}"] = _nearest(v, body & side, ank + np.array([0, -0.03, 0.02]))
        L[f"achilles_{s}"] = _nearest(v, body & side, ank + np.array([0, 0.035, 0.03]))
        L[f"knee_{s}"] = _extreme(v, body & side & zc(knee[2]), [0, -1, 0])
        L[f"kneeback_{s}"] = _extreme(v, body & side & zc(knee[2]), [0, 1, 0])
        L[f"kneeside_{s}"] = _extreme(v, body & side & zc(knee[2]), [sx, 0, 0])
        L[f"kneeinner_{s}"] = _extreme(v, body & side & zc(knee[2]), [-sx, 0, 0])
        L[f"shin_{s}"] = _extreme(v, body & side & zc((knee[2] + ank[2]) / 2), [0, -1, 0])
        L[f"calf_{s}"] = _extreme(v, body & side & zc(knee[2] * 0.65 + ank[2] * 0.35), [0, 1, 0])
        L[f"thigh_{s}"] = _extreme(v, body & side & zc((hip[2] + knee[2]) / 2), [0, -1, 0])
        L[f"thighback_{s}"] = _extreme(v, body & side & zc((hip[2] + knee[2]) / 2), [0, 1, 0])
        L[f"thighinner_{s}"] = _extreme(v, body & side & zc(hip[2] * 0.62 + knee[2] * 0.38), [-sx, 0, 0])
        L[f"thighout_{s}"] = _extreme(v, body & side & zc(hip[2] * 0.4 + knee[2] * 0.6), [sx, 0, 0])
        L[f"sit_{s}"] = _nearest(v, body & side, np.array([sx * 0.07, 0.08, hip[2] - 0.085]))
        L[f"buttock_{s}"] = _extreme(v, body & side & zc(hip[2] - 0.03), [0, 1, 0])
        L[f"hipside_{s}"] = _extreme(v, noarm & zc(hip[2] - 0.02), [sx, 0, 0])
        L[f"ribs_{s}"] = _extreme(v, noarm & zc(1.12), [sx, 0, 0])
        L[f"waist_{s}"] = _extreme(v, noarm & zc(1.02), [sx, 0, 0])
        L[f"armpit_{s}"] = _extreme(v, noarm & zc(1.25), [sx, 0, 0])
    return L


@lru_cache(None)
def region(name, radius=0.035):
    """Vertex indices of the skin patch around a landmark (for 'lowest point touches' contacts)."""
    m = rig.neutral()
    v = m.verts
    i = landmarks()[name]
    body = np.zeros(len(v), bool)
    body[np.unique(m.quads[m.part == 0])] = True
    d = np.linalg.norm(v - v[i], axis=1)
    # stay on the same limb: compare dominant bone
    dom = m.widx[np.arange(len(v)), np.argmax(m.wval, axis=1)]
    same_side = np.sign(v[:, 0]) == np.sign(v[i, 0]) if abs(v[i, 0]) > 0.03 else np.ones(len(v), bool)
    sel = np.where(body & (d < radius) & same_side)[0]
    return tuple(sel.tolist())


def points(verts, names):
    L = landmarks()
    return np.array([verts[L[n]] for n in names])


if __name__ == "__main__":
    L = landmarks()
    m = rig.neutral()
    for k, i in L.items():
        print(f"{k:14s} {i:6d} {np.round(m.verts[i], 3)}")
