"""
Surface fields painted on the figure (computed once on the neutral mesh, carried by skinning):

* ``top``  : > 0 inside a fitted sleeveless top
* ``legs`` : > 0 inside full-length leggings

Each field is a smooth, signed, distance-like value in metres, so that a sharp
threshold at 0 in the shader gives clean, smooth garment edges.
"""
import numpy as np

import rig


def _smin(a, b, k=0.01):
    """Smooth minimum (keeps the field continuous)."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def _sig(x, x0, w):
    return 1 / (1 + np.exp(-(x - x0) / w))


def bone_share(m, prefixes):
    ids = [m.i(n) for n in m.names if any(n.startswith(p) for p in prefixes)]
    w = np.zeros(len(m.verts))
    for k in range(m.widx.shape[1]):
        w += np.where(np.isin(m.widx[:, k], ids), m.wval[:, k], 0)
    return w


def garment_fields(m=None):
    m = m or rig.neutral()
    v = m.verts
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    ax = np.abs(x)
    arm = bone_share(m, ["upperarm", "lowerarm", "wrist", "finger", "metacarpal"])
    hand = bone_share(m, ["wrist", "finger", "metacarpal", "lowerarm02"])
    foot = bone_share(m, ["foot", "toe"])
    head = bone_share(m, ["head", "neck", "jaw", "eye", "special", "oris", "levator", "oculi", "tongue", "orbicularis", "risorius", "temporalis", "mandible"])

    # ---------------------------------------------------------------- leggings
    waist = 0.99 + 0.012 * (y > 0)  # a touch higher at the back
    legs = np.minimum.reduce([
        waist - z,                       # below the waistband
        z - 0.105,                       # above the hem at the ankle
        (0.45 - arm) * 0.06,             # not the arms/hands hanging alongside
        (0.5 - foot) * 0.05,
    ])

    # ---------------------------------------------------------------- sleeveless top
    front = _sig(-y, -0.005, 0.02)          # 1 at the front, 0 at the back
    neck = front * (1.238 + 2.4 * ax ** 2) + (1 - front) * (1.325 + 1.2 * ax ** 2)
    strap = _sig(ax, 0.058, 0.010) * (1 - _sig(ax, 0.112, 0.010))   # shoulder straps
    upper = neck * (1 - strap) + 1.55 * strap
    # armholes: an upright ellipse around each shoulder joint
    e = np.sqrt(((y + 0.005) / 0.082) ** 2 + ((z - 1.300) / 0.112) ** 2)
    hole = np.where(ax > 0.105, (e - 1.0) * 0.06, 0.2)
    top = np.minimum.reduce([
        z - 0.962,
        upper - z,
        hole,
        0.172 - ax,
        (0.85 - arm) * 0.06,
    ])
    return {"top": top.astype(np.float32), "legs": legs.astype(np.float32)}
