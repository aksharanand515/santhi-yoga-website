"""
Surface regions of the main superficial muscles (and the surface projection of a few deep
ones), painted on the figure to show which muscles work or lengthen in a posture.

Shapes follow standard surface anatomy (Moore et al., Clinically Oriented Anatomy; Kendall
et al., Muscles: Testing and Function) and are defined on the neutral (anatomical-position)
mesh in two chart systems:

* limbs: t = 0..1 along the segment (thigh hip->knee, shank knee->ankle, arm shoulder->elbow,
  forearm elbow->wrist) and theta around it (0 anterior, 90 lateral, 180 posterior, 270 medial);
  muscles are spindles/teardrops whose centre angle and half-width vary along t;
* trunk: theta about the vertical body axis (0 anterior midline, +90 lateral, 180 posterior
  midline; the chart is mirrored for left and right) and height z; muscles are polygons.

Each region is a signed, distance-like field in metres (> 0 inside) so the shader can draw a
clean edge.
"""
from functools import lru_cache

import numpy as np

import look
import rig

WORK = "#3F6F9C"      # working (contracting)
STRETCH = "#C2795C"   # lengthening under load
R_TRUNK = 0.13        # metres per radian on the trunk chart (approximate trunk radius)


# ------------------------------------------------------------------ geometry
@lru_cache(None)
def _geometry():
    m = rig.neutral()
    v = m.verts
    H = lambda b: m.heads[m.i(b)]  # noqa: E731
    segs = {}
    for s, sx in (("L", 1), ("R", -1)):
        for name, a, b in (("thigh", H(f"upperleg01.{s}"), H(f"lowerleg01.{s}")),
                           ("shank", H(f"lowerleg01.{s}"), H(f"foot.{s}")),
                           ("arm", H(f"upperarm01.{s}"), H(f"lowerarm01.{s}")),
                           ("forearm", H(f"lowerarm01.{s}"), H(f"wrist.{s}"))):
            ax = b - a
            L = np.linalg.norm(ax)
            ax = ax / L
            rel = v - a
            t = rel @ ax / L
            radial = rel - np.outer(rel @ ax, ax)
            ant = np.array([0, -1.0, 0]) - ax * (-ax[1])
            ant /= np.linalg.norm(ant)
            lat = np.cross(ax, ant)
            if lat[0] * sx < 0:
                lat = -lat
            th = np.degrees(np.arctan2(radial @ lat, radial @ ant)) % 360
            r = np.linalg.norm(radial, axis=1)
            segs[(name, s)] = (t, th, r, L)
    cy = -0.03
    th_trunk = np.degrees(np.arctan2(np.abs(v[:, 0]), -(v[:, 1] - cy)))  # 0 anterior .. 180 posterior
    return m, v, segs, th_trunk


def _mask(m, names, side=None):
    return look.bone_share(m, [f"{n}.{side}" if side else n for n in names]) > 0.5


THIGH = ["upperleg01", "upperleg02"]
SHANK = ["lowerleg01", "lowerleg02"]
ARM = ["upperarm01", "upperarm02"]
FOREARM = ["lowerarm01", "lowerarm02"]


def _spindle(seg, side, t0, t1, c0, c1, hw, bones, power=0.6, peak=0.5, taper_end=0.15):
    """A spindle on a limb: centre angle c0->c1 along t0..t1, max half-width hw (degrees)."""
    m, v, segs, _ = _geometry()
    t, th, r, L = segs[(seg, side)]
    s = (t - t0) / (t1 - t0)
    sc = np.clip(s, 0, 1)
    # asymmetric bump: peak position `peak`; keep a narrow tendon at the ends
    prof = np.where(sc < peak, np.sin(np.pi / 2 * sc / peak), np.sin(np.pi / 2 * (1 - sc) / (1 - peak)))
    w = hw * (taper_end + (1 - taper_end) * np.clip(prof, 0, 1) ** power)
    c = c0 + (c1 - c0) * sc
    d = np.abs((th - c + 180) % 360 - 180)
    f_ang = np.radians(w - d) * np.maximum(r, 0.02)
    f_t = np.minimum(t - t0, t1 - t) * L
    f = np.minimum(f_ang, f_t)
    return np.where(_mask(m, bones, side), f, -0.05)


def _both(fn):
    return np.maximum(fn("L"), fn("R"))


def _poly_field(px, py, poly):
    """Signed distance (in chart units) to a polygon; > 0 inside."""
    poly = np.asarray(poly, float)
    n = len(poly)
    inside = np.zeros(len(px), bool)
    dmin = np.full(len(px), np.inf)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        # ray casting
        cond = ((y1 > py) != (y2 > py)) & (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1)
        inside ^= cond
        # distance to segment
        dx, dy = x2 - x1, y2 - y1
        tt = np.clip(((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy + 1e-12), 0, 1)
        dd = np.hypot(px - (x1 + tt * dx), py - (y1 + tt * dy))
        dmin = np.minimum(dmin, dd)
    return np.where(inside, dmin, -dmin)


def _trunk_poly(poly_deg_z):
    """Polygon on the trunk chart: points (theta degrees 0..180, z metres); mirrored left/right."""
    m, v, segs, th = _geometry()
    px = np.radians(th) * R_TRUNK          # metres around the trunk
    pts = [(np.radians(a) * R_TRUNK, z) for a, z in poly_deg_z]
    f = _poly_field(px, v[:, 2], pts)
    limb = look.bone_share(m, ["upperarm", "lowerarm", "wrist", "finger", "metacarpal", "upperleg02", "lowerleg", "foot", "toe"])
    return np.where(limb < 0.5, f, -0.05)


# ------------------------------------------------------------------ the regions
def _trapezius():
    # descending, transverse and ascending parts: occiput -> acromion -> spine of scapula -> T12
    return _trunk_poly([(180, 1.61), (152, 1.56), (140, 1.47), (118, 1.405), (112, 1.385), (126, 1.35), (150, 1.25),
                        (172, 1.09), (180, 1.07)])


REGIONS = {
    # trunk -----------------------------------------------------------------
    "rectus_abdominis": lambda: _trunk_poly([(0, 0.905), (9, 0.905), (15, 1.00), (19, 1.21), (0, 1.225)]),
    "obliques": lambda: _trunk_poly([(22, 1.02), (26, 1.16), (58, 1.215), (96, 1.19), (104, 1.08), (98, 0.985), (70, 0.965), (38, 0.94)]),
    "erector_spinae": lambda: _trunk_poly([(178, 0.935), (160, 0.95), (152, 1.05), (154, 1.25), (164, 1.42), (178, 1.44)]),
    "latissimus": lambda: _trunk_poly([(180, 1.20), (176, 0.99), (150, 0.975), (122, 1.02), (104, 1.13), (98, 1.26), (108, 1.285),
                                       (128, 1.23), (160, 1.21)]),
    "trapezius": _trapezius,
    "rhomboids": lambda: _trunk_poly([(178, 1.37), (160, 1.37), (146, 1.24), (150, 1.20), (178, 1.215)]),
    "serratus": lambda: _trunk_poly([(62, 1.09), (70, 1.23), (92, 1.255), (106, 1.20), (102, 1.10), (84, 1.07)]),
    "pectorals": lambda: _trunk_poly([(3, 1.18), (3, 1.36), (30, 1.365), (62, 1.35), (84, 1.315), (86, 1.28), (60, 1.235),
                                      (34, 1.185), (14, 1.165)]),
    "intercostals": lambda: _trunk_poly([(8, 1.12), (8, 1.32), (95, 1.30), (100, 1.12)]),
    "gluteus_maximus": lambda: _trunk_poly([(178, 0.985), (158, 1.005), (132, 0.975), (104, 0.875), (112, 0.84), (140, 0.80),
                                            (168, 0.79), (178, 0.82)]),
    "gluteus_medius": lambda: _trunk_poly([(92, 0.99), (104, 1.01), (140, 1.00), (148, 0.975), (120, 0.94), (100, 0.885), (90, 0.93)]),
    "iliopsoas": lambda: _trunk_poly([(18, 0.955), (42, 0.965), (50, 0.905), (36, 0.855), (24, 0.86)]),
    # thigh -----------------------------------------------------------------
    "rectus_femoris": lambda: _both(lambda s: _spindle("thigh", s, 0.02, 0.95, 5, 0, 24, THIGH, peak=0.45)),
    "vastus_lateralis": lambda: _both(lambda s: _spindle("thigh", s, 0.10, 0.92, 88, 55, 38, THIGH, peak=0.5)),
    "vastus_medialis": lambda: _both(lambda s: _spindle("thigh", s, 0.42, 0.95, 322, 312, 30, THIGH, peak=0.75, power=0.5)),
    "sartorius": lambda: _both(lambda s: _spindle("thigh", s, -0.02, 1.02, 22, 248, 7, THIGH + SHANK, peak=0.5, taper_end=0.6)),
    "tensor_fasciae_latae": lambda: _both(lambda s: _spindle("thigh", s, -0.06, 0.22, 62, 80, 18, THIGH + ["pelvis"], peak=0.45)),
    "it_band": lambda: _both(lambda s: _spindle("thigh", s, 0.15, 1.0, 88, 82, 9, THIGH, peak=0.5, taper_end=0.8)),
    "biceps_femoris": lambda: _both(lambda s: _spindle("thigh", s, 0.04, 1.04, 172, 118, 22, THIGH + SHANK, peak=0.5)),
    "semitendinosus": lambda: _both(lambda s: _spindle("thigh", s, 0.04, 1.04, 200, 238, 24, THIGH + SHANK, peak=0.45)),
    # adductor group (longus, brevis, magnus, gracilis, pectineus): the medial thigh, reaching
    # forward to the femoral triangle above and narrowing to the medial knee below
    "adductors": lambda: _both(lambda s: _spindle("thigh", s, -0.04, 0.80, 300, 272, 58, THIGH, peak=0.2, power=0.8)),
    # leg -------------------------------------------------------------------
    "gastrocnemius": lambda: _both(lambda s: np.maximum(_spindle("shank", s, 0.0, 0.60, 208, 188, 30, SHANK, peak=0.3),
                                                        _spindle("shank", s, 0.0, 0.52, 150, 172, 26, SHANK, peak=0.3))),
    "soleus": lambda: _both(lambda s: _spindle("shank", s, 0.28, 0.88, 180, 180, 62, SHANK, peak=0.45, power=0.8)),
    "tibialis_anterior": lambda: _both(lambda s: _spindle("shank", s, 0.08, 0.92, 34, 12, 16, SHANK, peak=0.35)),
    # shoulder and arm -----------------------------------------------------
    "deltoid": lambda: _both(lambda s: _spindle("arm", s, -0.16, 0.52, 92, 90, 118, ARM + ["shoulder01", "clavicle"], peak=0.25, power=0.9, taper_end=0.05)),
    "biceps": lambda: _both(lambda s: _spindle("arm", s, 0.20, 0.96, 0, 5, 32, ARM, peak=0.55)),
    "triceps": lambda: _both(lambda s: _spindle("arm", s, 0.10, 0.98, 182, 180, 48, ARM, peak=0.45)),
    "forearm_flexors": lambda: _both(lambda s: _spindle("forearm", s, 0.0, 0.80, 285, 280, 46, FOREARM, peak=0.25)),
    "forearm_extensors": lambda: _both(lambda s: _spindle("forearm", s, 0.0, 0.80, 100, 100, 46, FOREARM, peak=0.25)),
}
# composite regions
COMPOSITE = {
    "quadriceps": ["rectus_femoris", "vastus_lateralis", "vastus_medialis"],
    "hip_flexors": ["iliopsoas", "rectus_femoris", "tensor_fasciae_latae", "sartorius"],
    "calf": ["gastrocnemius", "soleus"],
    "abdominals": ["rectus_abdominis", "obliques"],
    "back_extensors": ["erector_spinae"],
    "shoulder_girdle": ["trapezius", "serratus"],
}


def _neck():
    m, v, segs, th = _geometry()
    ax = np.abs(v[:, 0])
    z = v[:, 2]
    post = np.radians(65 - np.abs(th - 180)) * 0.06
    return np.minimum.reduce([0.048 - ax, post, np.minimum(z - 1.405, 1.60 - z)])


def _segment_band(p0, p1, width):
    m, v, segs, th = _geometry()
    p0, p1 = np.asarray(p0), np.asarray(p1)
    d = p1 - p0
    L = np.linalg.norm(d)
    u = d / L
    s = np.clip((v - p0) @ u, 0, L)
    dist = np.linalg.norm(v - (p0 + np.outer(s, u)), axis=1)
    taper = 0.55 + 0.45 * np.sin(np.pi * s / L)
    return width * taper - dist


REGIONS["neck_extensors"] = _neck
# deep muscles shown as their projection onto the surface (atlas only)
REGIONS["transversus"] = lambda: _trunk_poly([(0, 0.925), (0, 1.12), (40, 1.13), (80, 1.12), (112, 1.08), (118, 1.00), (96, 0.955), (40, 0.93)])
REGIONS["multifidus"] = lambda: _trunk_poly([(179, 0.90), (166, 0.92), (164, 1.02), (169, 1.16), (179, 1.18)])
REGIONS["quadratus_lumborum"] = lambda: _trunk_poly([(168, 1.00), (140, 1.005), (132, 1.06), (150, 1.125), (168, 1.13)])
REGIONS["rotator_cuff"] = lambda: _trunk_poly([(150, 1.34), (126, 1.305), (112, 1.34), (118, 1.40), (138, 1.43), (152, 1.415)])
# the hamstrings as one block (posterior thigh, ischial tuberosity to just below the knee)
REGIONS["hamstrings"] = lambda: _both(lambda s: _spindle("thigh", s, 0.0, 1.04, 184, 178, 64, THIGH + SHANK, peak=0.45, power=0.7))
REGIONS["scalenes"] = lambda: np.maximum(_segment_band([0.036, -0.004, 1.52], [0.062, -0.030, 1.405], 0.013),
                                         _segment_band([-0.036, -0.004, 1.52], [-0.062, -0.030, 1.405], 0.013))
def _surf(x, z, towards):
    """Neutral-mesh surface vertex near (x, z) furthest in direction `towards`."""
    m, v, segs, th = _geometry()
    sel = np.where((np.abs(v[:, 0] - x) < 0.008) & (np.abs(v[:, 2] - z) < 0.008))[0]
    return v[sel[np.argmax(v[sel] @ np.asarray(towards, float))]]


def _band_facing(a, b, width, normal):
    """Band between surface points a and b measured in the plane perpendicular to `normal`
    (so it stays on the surface facing that way instead of sinking into the body)."""
    m, v, segs, th = _geometry()
    n = np.asarray(normal, float)
    n /= np.linalg.norm(n)
    flat = lambda p: p - np.outer(p @ n, n) if p.ndim > 1 else p - (p @ n) * n  # noqa: E731
    fa, fb, fv = flat(np.asarray(a)), flat(np.asarray(b)), flat(v)
    d = fb - fa
    L = np.linalg.norm(d)
    u = d / L
    t = np.clip((fv - fa) @ u, 0, L)
    dist = np.linalg.norm(fv - (fa + np.outer(t, u)), axis=1)
    taper = 0.55 + 0.45 * np.sin(np.pi * t / L)
    # only the surface that faces `normal` near the band
    depth = (v - (np.asarray(a) + np.outer(t / L, np.asarray(b) - np.asarray(a)))) @ n
    return np.where(depth > -0.02, width * taper - dist, -0.05)


def _surface_path(a, b, normal, k=8):
    """Points from a to b snapped outwards onto the surface along `normal`."""
    m, v, segs, th = _geometry()
    n = np.asarray(normal, float)
    n /= np.linalg.norm(n)
    pts = []
    for t in np.linspace(0, 1, k):
        p = np.asarray(a) * (1 - t) + np.asarray(b) * t
        rel = v - p
        off = rel - np.outer(rel @ n, n)
        near = np.where(np.linalg.norm(off, axis=1) < 0.010)[0]
        pts.append(v[near[np.argmax(v[near] @ n)]] if len(near) else p)
    return pts


def _levator():
    out = []
    for sx in (1, -1):
        a = np.array([sx * 0.030, 0.02, 1.535])   # C1–C4 transverse processes, side of the neck
        b = np.array([sx * 0.080, 0.07, 1.405])   # superior angle of the scapula
        pts = _surface_path(a, b, (sx * 0.6, 1.0, 0.15))
        out += [_segment_band(p, q, 0.011) for p, q in zip(pts[:-1], pts[1:])]
    return np.max(out, axis=0)


# forearm regions as they lie with the palms turned forward (the skin of the model twists as a
# whole with supination, so the palms-forward atlas pose needs its own chart angles)
def _posed_forearm(centre, hw, pose="front"):
    """Forearm spindle defined on the posed mesh of `pose` (angles about the posed forearm:
    0 anterior, 90 lateral, 180 posterior, 270 medial)."""
    import poses3d
    import solve
    spec = poses3d.P[pose]
    P, t = solve.solve(spec)
    m, G = rig.posed(P)
    v = rig.pose_mesh(P)[0]
    out = []
    for s_, sx in (("L", 1), ("R", -1)):
        head = lambda b: (G[m.i(b)] @ np.r_[m.heads[m.i(b)], 1.0])[:3]  # noqa: E731
        a, b = head(f"lowerarm01.{s_}"), head(f"wrist.{s_}")
        ax = (b - a) / np.linalg.norm(b - a)
        L = np.linalg.norm(b - a)
        rel = v - a
        tt = rel @ ax / L
        radial = rel - np.outer(rel @ ax, ax)
        ant = np.array([0, -1.0, 0]) - ax * (-ax[1])
        ant /= np.linalg.norm(ant)
        lat = np.cross(ax, ant)
        if lat[0] * sx < 0:
            lat = -lat
        th = np.degrees(np.arctan2(radial @ lat, radial @ ant)) % 360
        r = np.linalg.norm(radial, axis=1)
        sc = np.clip(tt / 0.8, 0, 1)
        prof = np.where(sc < 0.25, np.sin(np.pi / 2 * sc / 0.25), np.sin(np.pi / 2 * (1 - sc) / 0.75))
        w = hw * (0.15 + 0.85 * np.clip(prof, 0, 1) ** 0.6)
        d = np.abs((th - centre + 180) % 360 - 180)
        f = np.minimum(np.radians(w - d) * np.maximum(r, 0.02), np.minimum(tt, 0.8 - tt) * L)
        out.append(np.where(_mask(m, FOREARM, s_), f, -0.05))
    return np.maximum(*out)


# with the palms turned forward (atlas figure): flexors on the front and inner side, extensors on
# the back and outer side
REGIONS["forearm_flexors_sup"] = lambda: _posed_forearm(320, 60)
REGIONS["forearm_extensors_sup"] = lambda: _posed_forearm(140, 60)


REGIONS["levator_scapulae"] = _levator
REGIONS["suboccipitals"] = lambda: np.maximum(_segment_band([0.022, 0.045, 1.575], [0.004, 0.040, 1.535], 0.014),
                                              _segment_band([-0.022, 0.045, 1.575], [-0.004, 0.040, 1.535], 0.014))
REGIONS["scm"] = lambda: np.maximum(_segment_band([0.058, 0.012, 1.585], [0.022, -0.078, 1.378], 0.017),
                                    _segment_band([-0.058, 0.012, 1.585], [-0.022, -0.078, 1.378], 0.017))


@lru_cache(None)
def field(name):
    """Region field; 'name:L' / 'name:R' restricts it to one side of the body."""
    if ":" in name:
        base, side = name.split(":")
        m, v, segs, th = _geometry()
        keep = v[:, 0] > 0 if side == "L" else v[:, 0] < 0
        return np.where(keep, field(base), -0.05).astype(np.float32)
    if name in COMPOSITE:
        return np.max([field(n) for n in COMPOSITE[name]], axis=0)
    return REGIONS[name]().astype(np.float32)


def overlay_attrs(items):
    """items: list of (region, kind) with kind 'work' | 'stretch'.
    Returns (attrs dict, overlay tuple for render3d.figure_material)."""
    attrs, ov = {}, []
    for region, kind in items:
        a = "m_" + region.replace(":", "_")
        attrs[a] = field(region)
        col = WORK if kind == "work" else STRETCH if kind == "stretch" else kind  # or an explicit colour
        ov.append((a, col, 0.80 if kind in ("work", "stretch") else 0.92))
    return attrs, tuple(ov)


ALL = sorted(list(REGIONS) + list(COMPOSITE))
