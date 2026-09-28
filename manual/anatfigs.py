"""
Anatomy figures rendered from real bone geometry.

Bones come from the OpenSim full-body model of Rajagopal et al. (2016), whose geometry derives
from Delp et al. (1990) and Holzbaur et al. (2005) (CC BY 3.0); see 3d/skeleton.py and
3d/anat3d.py. Soft tissues that the model does not contain (discs, menisci, ligaments, the
diaphragm) are modelled on the bones at their standard anatomical attachments, and muscle
lines of action come from the same OpenSim model. Labels are placed by projecting 3D
landmarks, so leaders always point at the structure named.
"""
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "3d"))

import anat3d as A  # noqa: E402
import props3d as PR  # noqa: E402
import scene3d as S  # noqa: E402
import skeleton  # noqa: E402



class _Lazy:
    """figures.py imports this module part-way through; reach its helpers lazily."""
    def __getattr__(self, k):
        import figures
        return getattr(figures, k)


FG = _Lazy()


class _Colours(dict):
    def __missing__(self, k):
        return FG.C[k]


C = _Colours()


def T(*a, **k):
    return FG.T(*a, **k)


def f(x):
    return FG.f(x)
LIG = "#C9B27A"      # ligament
MENISCUS = "#8FB6B0"  # fibrocartilage
CART = "#B9D3D4"      # hyaline / articular cartilage
MUSCLE = "#B5533C"
MUSCLE2 = "#3F6F9C"


# ----------------------------------------------------------------------------- helpers
def O(v, F, color=A.BONE, **kw):
    return dict(verts=np.asarray(v, float), faces=F, color=color, **kw)


def place(info, x, y, w=None, h=None):
    """Place a rendered scene at (x, y) with width w (or height h). Returns (el, w, h, P)."""
    ar = info["h"] / info["w"]
    if w is None:
        w = h / ar
    h = w * ar

    def P(p):
        u, v = info["project"](p)
        return x + u * w, y + v * h
    el = f'<image href="{info["file"]}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"/>'
    return el, w, h, P


def lab(p, text, tx, ty, anchor="start", size=6.2, col=None, dot=True):
    """Leader from point p (svg coords) to a label at (tx, ty)."""
    lx = tx - 3 if anchor == "start" else (tx + 3 if anchor == "end" else tx)
    out = f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(lx)}" y2="{f(ty - 2.2)}" stroke="{C["teak"]}" stroke-width=".45"/>'
    if dot:
        out += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="1.2" fill="{C["teak"]}" stroke="#FFFEFA" stroke-width=".4"/>'
    return out + T(tx, ty, text, size, col, anchor)


def clip(v, F, keep):
    """Keep the faces whose vertices all satisfy keep (bool per vertex); unused vertices are dropped."""
    FF = [ff for ff in F if all(keep[i] for i in ff)]
    used = sorted({i for ff in FF for i in ff})
    return A._submesh(v, FF, used)


def rot(axis_pt, axis, ang_deg):
    """Rotation about a line; returns fn(points)."""
    from scipy.spatial.transform import Rotation as R
    Rm = R.from_rotvec(np.asarray(axis, float) / np.linalg.norm(axis) * np.radians(ang_deg)).as_matrix()
    c = np.asarray(axis_pt, float)
    return lambda p: (np.asarray(p, float) - c) @ Rm.T + c


def tube(pts, r0, r1=None, n=40, belly=None, sides=18):
    """Smooth tube along a polyline, radius r0 at the ends and `belly` at the middle."""
    from scipy.interpolate import CubicSpline
    P = np.asarray(pts, float)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    keep = np.r_[True, np.diff(d) > 1e-6]
    P, d = P[keep], d[keep]
    if len(P) >= 3:
        cs = CubicSpline(d, P, bc_type="natural")
        s = np.linspace(0, d[-1], n)
        Q = cs(s)
    else:
        s = np.linspace(0, 1, n)
        Q = P[0] + np.outer(s, P[-1] - P[0])
        s = s * d[-1]
    t = s / s[-1]
    r1 = r0 if r1 is None else r1
    rad = r0 + (r1 - r0) * t
    if belly:
        rad = rad + (belly - rad) * np.sin(np.pi * t) ** 1.2
    # frames
    tang = np.gradient(Q, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    ref = np.array([0, 0, 1.0]) if abs(tang[0][2]) < 0.9 else np.array([1.0, 0, 0])
    V, Fc = [], []
    nrm = np.cross(tang[0], ref)
    nrm /= np.linalg.norm(nrm)
    for i in range(n):
        nrm = nrm - tang[i] * (nrm @ tang[i])
        nrm /= np.linalg.norm(nrm)
        bn = np.cross(tang[i], nrm)
        for k in range(sides):
            a = 2 * np.pi * k / sides
            V.append(Q[i] + rad[i] * (np.cos(a) * nrm + np.sin(a) * bn))
    for i in range(n - 1):
        for k in range(sides):
            a, b = i * sides + k, i * sides + (k + 1) % sides
            Fc.append([a, b, b + sides, a + sides])
    # caps
    V.append(Q[0])
    V.append(Q[-1])
    c0, c1 = len(V) - 2, len(V) - 1
    for k in range(sides):
        Fc.append([c0, (k + 1) % sides, k])
        Fc.append([c1, (n - 1) * sides + k, (n - 1) * sides + (k + 1) % sides])
    return np.array(V), Fc


def ribbon(pts, width, thick=0.0025, n=24, normal=None):
    """Flat band (ligament) along a polyline; `normal` gives the face direction."""
    P = np.asarray(pts, float)
    s = np.linspace(0, 1, n)
    Q = np.array([np.interp(s, np.linspace(0, 1, len(P)), P[:, j]) for j in range(3)]).T
    tang = np.gradient(Q, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    nm = np.asarray(normal, float)
    V = []
    for i in range(n):
        side = np.cross(tang[i], nm)
        side /= np.linalg.norm(side)
        w = width * (0.75 + 0.25 * np.sin(np.pi * s[i]))
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            V.append(Q[i] + side * a * w / 2 + nm * b * thick / 2)
    Fc = []
    for i in range(n - 1):
        for k in range(4):
            a, b = i * 4 + k, i * 4 + (k + 1) % 4
            Fc.append([a, b, b + 4, a + 4])
    Fc.append([0, 1, 2, 3])
    Fc.append([(n - 1) * 4 + 3, (n - 1) * 4 + 2, (n - 1) * 4 + 1, (n - 1) * 4])
    return np.array(V), Fc


@lru_cache(None)
def ribs_parts():
    """Components of hat_ribs_scap: ribs (L/R lists), sternum+costal cartilages, clavicles, scapulae."""
    v, F = A.mesh("torso", "hat_ribs_scap.vtp")
    n, labs = A._components(v, F)
    parts = dict(ribs=[], sternum=None, clav={}, scap={})
    for k in range(n):
        idx = np.where(labs == k)[0]
        if len(idx) < 30:
            continue
        sub = A._submesh(v, F, idx)
        side = "L" if sub[0][:, 0].mean() > 0 else "R"
        if len(idx) > 700 and abs(sub[0][:, 0].mean()) < 0.02:
            parts["sternum"] = sub
        elif len(idx) > 700:
            parts["scap"][side] = sub
        elif len(idx) in (263, 264, 265):
            parts["clav"][side] = sub
        else:
            parts["ribs"].append(sub)
    return parts


def spine_objs(names=None, color_by_region=True):
    V, D = A.spine()
    out = []
    for k, (v, F) in V.items():
        if names and k not in names:
            continue
        col = {"C": A.CERV, "T": A.THOR, "L": A.LUMB}[k[0]] if color_by_region else A.BONE
        out.append(O(v, F, col))
    return out


ORDER = [f"C{i}" for i in range(1, 8)] + [f"T{i}" for i in range(1, 13)] + [f"L{i}" for i in range(1, 6)]


def disc_below(name):
    """The disc between vertebra `name` and the one below it (L5: the lumbosacral disc)."""
    V, D = A.spine()
    z_hi = A.body_centre(V[name])[2]
    i = ORDER.index(name)
    z_lo = A.body_centre(V[ORDER[i + 1]])[2] if i + 1 < len(ORDER) else A.sacrum()[0][:, 2].max() - 0.03
    cand = [(v, F) for v, F in D if z_lo < v[:, 2].mean() < z_hi]
    return min(cand, key=lambda d: abs(d[0][:, 2].mean() - (z_lo + z_hi) / 2)) if cand else None


def discs_between(names):
    """Discs between consecutive vertebrae of the listed range (plus the one below the last)."""
    out = []
    for k in names:
        d = disc_below(k)
        if d is not None:
            out.append(O(d[0], d[1], A.DISC))
    return out


def vcentre(name):
    return A.body_centre(A.spine()[0][name])


# ============================================================================ spine
def fig_spine():
    W, H = 380, 470
    V, D = A.spine()
    objs = spine_objs() + [O(v, F, A.DISC) for v, F in D]
    sv, sF = A.sacrum()
    objs.append(O(sv, sF, A.SACR))
    info = S.render_scene("spine-lat", objs, view=(0, 0), width=520, samples=64)
    w = 452 * info["w"] / info["h"]
    x0 = 185 - w / 2
    el, w, h, P = place(info, x0, 10, h=452)
    b = [el]
    # region brackets from the vertebra extents
    zr = {}
    for k, (v, F) in V.items():
        r = k[0]
        lo, hi = zr.get(r, (9, -9))
        zr[r] = (min(lo, v[:, 2].min()), max(hi, v[:, 2].max()))
    zr["S"] = (sv[:, 2].min(), sv[:, 2].max())
    y_of = lambda z: P([0, 0.10, z])[1]  # noqa: E731
    xb = x0 + w + 18
    labels = {"C": ("Cervical  C1–C7", "lordosis (concave posteriorly)"),
              "T": ("Thoracic  T1–T12", "kyphosis (convex posteriorly);\nribs attach here"),
              "L": ("Lumbar  L1–L5", "lordosis; largest bodies,\nthickest discs"),
              "S": ("Sacrum and coccyx", "S1–S5 fused; kyphotic curve;\nforms the back of the pelvis")}
    for r, (n, d) in labels.items():
        lo, hi = zr[r]
        ya, ye = y_of(hi), y_of(lo)
        b.append(f'<path d="M{f(xb-6)},{f(ya+1)} h6 v{f(ye-ya-2)} h-6" fill="none" stroke="{C["golddeep"]}" stroke-width=".8"/>')
        mid = (ya + ye) / 2
        b.append(T(xb + 8, mid - 3, n, 9.5, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(xb + 8, mid + 7, d, 5.9, C["ink2"]))
    # left-hand annotations (posterior side)
    c1 = V["C1"][0]
    XL = 84
    b.append(lab(P(c1[np.argmax(c1[:, 1])]), "C1 (atlas)", XL, P(c1.mean(0))[1] - 4, "end", 5.9))
    b.append(lab(P(A.spinous_tip(V["C7"])), "C7: prominent\nspinous process", XL, P(A.spinous_tip(V["C7"]))[1] + 2, "end", 5.9))
    t6 = A.spinous_tip(V["T6"])
    b.append(lab(P(t6), "spinous process\n(posterior)", XL, P(t6)[1] + 4, "end", 5.9))
    l1 = A.spinous_tip(V["L1"])
    b.append(lab(P(l1), "T12–L1: the\nthoracolumbar\njunction", XL, P(l1)[1] - 6, "end", 5.9))
    # discs and bodies (anterior side)
    d34 = disc_below("L3")
    if d34 is not None:
        dv = d34[0]
        b.append(lab(P(dv[np.argmin(dv[:, 1])]), "intervertebral disc", xb + 8, P(dv.mean(0))[1] + 26, "start", 5.9))
    body = V["T8"][0]
    bp = body[np.argmin(body[:, 1])]
    b.append(lab(P(bp), "vertebral body (anterior)", xb + 8, P(bp)[1] + 30, "start", 5.9))
    cx = sv[np.argmin(sv[:, 2])]
    b.append(lab(P(cx), "coccyx", xb - 30, P(cx)[1] + 10, "start", 5.9))
    b.append(FG.arrow(xb + 60, 16, xb + 96, 16, C["golddeep"]) + T(xb + 56, 18, "anterior", 6, C["golddeep"], "end", 600))
    return FG.svg(W, H, "".join(b))


# ============================================================================ vertebra
def _vert_landmarks(v):
    """Superior-view landmarks of a lumbar vertebra from its mesh."""
    xc = v[:, 0].mean()
    central = v[np.abs(v[:, 0] - xc) < 0.004]
    ys = np.sort(central[:, 1])
    gaps = np.diff(ys)
    i = np.argmax(gaps)
    yb, yl = ys[i], ys[i + 1]           # back of the body, front of the lamina
    L = {}
    L["foramen"] = np.array([xc, (yb + yl) / 2, v[:, 2].max()])
    front = v[v[:, 1] < yb - 0.004]
    L["body"] = np.array([xc, front[:, 1].mean(), v[:, 2].max()])
    L["tp"] = v[np.argmax(v[:, 0])]
    L["tp_R"] = v[np.argmin(v[:, 0])]
    L["spinous"] = v[np.argmax(v[:, 1])]
    post = v[(v[:, 1] > yb) & (np.abs(v[:, 0] - xc) > 0.008)]
    L["sap"] = post[np.argmax(post[:, 2] + (post[:, 0] < xc) * 0)]
    sap_side = post[post[:, 0] < xc]
    L["sap_R"] = sap_side[np.argmax(sap_side[:, 2])]
    hw = 0.5 * (np.abs(L["tp"][0] - xc))
    ped = v[(v[:, 1] > yb - 0.006) & (v[:, 1] < yb + 0.006) & (v[:, 0] > xc)]
    L["pedicle"] = ped[np.argmin(np.abs(ped[:, 0] - xc - 0.4 * hw))] if len(ped) else L["tp"]
    lam = v[(v[:, 1] > yl) & (v[:, 1] < yl + 0.012) & (v[:, 0] > xc + 0.003)]
    L["lamina"] = lam[np.argmax(lam[:, 2])] if len(lam) else L["spinous"]
    return L


def _superior_points(info, v, P, x0, y0, w):
    """Landmarks of the superior view found on the rendered silhouette (SVG coordinates)."""
    from PIL import Image
    from scipy import ndimage
    im = np.asarray(Image.open(Path(__file__).parent / info["file"]))[:, :, 3] > 40
    H, W = im.shape
    s = w / W
    to = lambda r, c: (x0 + c * s, y0 + r * s)  # noqa: E731
    holes = ndimage.binary_fill_holes(im) & ~im
    lab_, n = ndimage.label(holes)
    out = {}
    if n:
        sizes = ndimage.sum(holes, lab_, range(1, n + 1))
        hole = lab_ == (np.argmax(sizes) + 1)
        rr, cc = np.nonzero(hole)
        fr, fc = rr.mean(), cc.mean()
        out["foramen"] = to(fr, fc)
        top, bot = rr.min(), rr.max()
        left = cc.min()
        # body: the solid part in front of (above) the foramen
        br, bc = np.nonzero(im[: max(top - 4, 1)])
        out["body"] = to(br.mean(), bc.mean())
        # pedicle: bone just lateral to the foramen at its front half
        r_ped = int(top + 0.3 * (bot - top))
        out["pedicle"] = to(r_ped, left - 0.035 * W)
        # lamina: bone just behind the foramen, slightly lateral
        out["lamina"] = to(bot + 0.03 * H, fc - 0.07 * W)
        # spinous process: lowest silhouette pixel near the midline
        rows = np.nonzero(im[:, int(fc)])[0]
        out["spinous"] = to(rows.max() - 0.02 * H, fc)
        # transverse process: left-most silhouette pixel
        r2, c2 = np.nonzero(im)
        i = np.argmin(c2)
        out["tp"] = to(r2[i], c2[i] + 0.01 * W)
    return out


def fig_vertebra():
    W, H = 500, 234
    V, D = A.spine()
    v3, F3 = V["L3"]
    L = _vert_landmarks(v3)
    b = []
    # superior view, anterior up
    info = S.render_scene("vert-sup", [O(v3, F3, A.LUMB)], view=(0, 89.9), width=700, samples=64, up=(0, -1, 0))
    el, w, h, P = place(info, 20, 34, w=180)
    b.append(el)
    b.append(T(110, 16, "Lumbar vertebra (L3), superior view", 7, C["golddeep"], "middle", 700))
    b.append(T(110, 26, "anterior ↑", 5.8, C["ink2"], "middle"))
    items = [("body", "vertebral body"), ("foramen", "vertebral foramen (cauda equina)"), ("pedicle", "pedicle"),
             ("tp", "transverse process"), ("sap", "superior articular process (facet)"), ("lamina", "lamina"),
             ("spinous", "spinous process")]
    ys = np.linspace(46, 192, len(items))
    L2 = _superior_points(info, v3, P, 20, 34, w)
    for (k, t), ty in zip(items, ys):
        b.append(lab(L2.get(k, P(L[k])), t, 214, ty))
    # motion segment L3-disc-L4, lateral view (anterior to the right)
    v4, F4 = V["L4"]
    d34 = disc_below("L3")
    disc = [d34] if d34 is not None else []
    objs = [O(v3, F3, A.LUMB), O(v4, F4, A.LUMB)] + [O(v, F, A.DISC) for v, F in disc]
    info2 = S.render_scene("vert-seg", objs, view=(0, 0), width=700, samples=64)
    el2, w2, h2, P2 = place(info2, 330, 36, h=130)
    b.append(el2)
    b.append(T(330 + w2 / 2, 16, "Motion segment L3–L4, lateral view", 7, C["golddeep"], "middle", 700))
    b.append(T(330 + w2 / 2, 26, "anterior →", 5.8, C["ink2"], "middle"))
    if disc:
        dv = disc[0][0]
        dc = dv.mean(0)
        ymin, ymax = dv[:, 1].min(), dv[:, 1].max()
        # nucleus pulposus: slightly posterior of the disc centre
        nuc = np.array([dc[0], ymin + 0.58 * (ymax - ymin), dc[2]])
        pn = P2(nuc)
        rx = (P2([0, ymax, dc[2]])[0] - P2([0, ymin, dc[2]])[0]) * 0.18
        b.append(f'<ellipse cx="{f(pn[0])}" cy="{f(pn[1])}" rx="{f(rx)}" ry="{f(rx*0.28)}" fill="#DDEBEE" stroke="#7FA6B6" stroke-width=".5"/>')
        b.append(lab(pn, "nucleus pulposus", 494, 196, "end"))
        b.append(lab(P2([dc[0], ymin + 0.02 * (ymax - ymin), dc[2]]), "annulus fibrosus", 494, 210, "end"))
        # spinal nerve in the intervertebral foramen (behind the disc, below the L3 pedicle)
        fz = dc[2] + 0.004
        fy = ymax + 0.012
        pf = P2([dc[0], fy, fz])
        b.append(f'<circle cx="{f(pf[0])}" cy="{f(pf[1])}" r="4.2" fill="{C["nerve"]}" stroke="#B48F27" stroke-width=".5"/>')
        b.append(lab(pf, "spinal nerve in the intervertebral foramen", 400, 182, "end"))
        L4 = _vert_landmarks(v4)
        b.append(lab(P2(L4["sap"]), "facet (zygapophyseal) joint", 400, 224, "end"))
    return FG.svg(W, H, "".join(b))


# ============================================================================ pelvis
def _pelvis_objs(fem_len=0.20, extra=True):
    objs = []
    for fn in ("r_pelvis.vtp", "l_pelvis.vtp"):
        v, F = A.mesh("pelvis", fn)
        objs.append(O(v, F, A.BONE))
    sv, sF = A.sacrum()
    objs.append(O(sv, sF, A.SACR))
    for s in ("r", "l"):
        v, F = A.mesh(f"femur_{s}")
        top = v[:, 2].max()
        v2, F2 = clip(v, F, v[:, 2] > top - fem_len)
        objs.append(O(v2, F2, A.BONE_DARK if False else A.BONE))
    if extra:
        objs += spine_objs(["L4", "L5"], color_by_region=False) + discs_between(["L4", "L5"])
        # The model's pubic bones stop ~2.4 cm from the midline; complete the pubic bodies and add
        # the fibrocartilaginous symphysis (about 5 mm) between them.
        PL = A.pelvis_landmarks()
        for s_, sx in (("L", 1), ("R", -1)):
            pb = PL[f"pubis_{s_}"]
            x0 = 0.003 * sx
            x1 = pb[0] + 0.006 * sx
            V, Fb = PR.box(((x0 + x1) / 2, pb[1] + 0.008, pb[2] + 0.002), (abs(x1 - x0), 0.016, 0.032))
            objs.append(O(V, Fb, A.BONE, subdiv=2))
        c = (PL["pubis_L"] + PL["pubis_R"]) / 2
        V, Fb = PR.box((0, c[1] + 0.008, c[2] + 0.002), (0.0065, 0.014, 0.030))
        objs.append(O(V, Fb, CART, subdiv=2))
    return objs


def _hole_point(info, P, side, below_y, x0, y0, w, h):
    """Centre (SVG coords) of the largest enclosed transparent region of a render that satisfies
    side(u, v) (0..1 image coordinates) and lies below SVG y = below_y."""
    from PIL import Image
    from scipy import ndimage
    im = np.asarray(Image.open(Path(__file__).parent / info["file"]))[:, :, 3] > 40
    holes = ndimage.binary_fill_holes(im) & ~im
    lab_, n = ndimage.label(holes)
    best = None
    for k in range(1, n + 1):
        rr, cc = np.nonzero(lab_ == k)
        u, v = cc.mean() / im.shape[1], rr.mean() / im.shape[0]
        sy = y0 + v * h
        if side(u, v) and sy > below_y and (best is None or len(rr) > best[0]):
            best = (len(rr), (x0 + u * w, sy))
    return best[1] if best else None


def fig_pelvis():
    W, H = 470, 290
    PL = A.pelvis_landmarks()
    FL = A.femur_landmarks()
    info = S.render_scene("pelvis-ant", _pelvis_objs(), view=(90, 4), width=900, samples=64)
    el, w, h, P = place(info, 14, 14, h=266)
    b = [el]
    V, D = A.spine()
    sv, _ = A.sacrum()
    # labels for the figure's left side (image right) where possible
    fv, _ = A.mesh("femur_l")
    lp, _ = A.mesh("pelvis", "l_pelvis.vtp")
    hip = PL["hip_L"]
    top = fv[fv[:, 2] > hip[2] - 0.04]
    midf = fv[(fv[:, 2] > hip[2] - 0.09) & (fv[:, 2] < hip[2] - 0.04)]
    gt = top[np.argmax(top[:, 0])]
    FL = dict(fhead_L=hip, gtroch_L=gt, neck_L=(hip + gt) / 2 - np.array([0, 0, 0.012]), ltroch_L=midf[np.argmin(midf[:, 0])])
    obt = _hole_point(info, P, lambda u, v: u > 0.5, P(PL["pubis_L"])[1], 14, 14, w, h)
    items = [(vcentre("L5"), "L5 vertebra"),
             (PL["si_L"] + np.array([0.004, -0.02, -0.01]), "sacroiliac (SI) joint"),
             (sv.mean(0) + np.array([0, -0.03, 0.0]), "sacrum"),
             (PL["crest_L"], "iliac crest"),
             (PL["asis_L"], "ASIS (anterior superior iliac spine)"),
             (FL["fhead_L"] + np.array([0, -0.02, 0]), "femoral head in the acetabulum (hip joint)"),
             (FL["neck_L"] + np.array([0, -0.015, 0]), "femoral neck"),
             (FL["gtroch_L"], "greater trochanter"),
             ((PL["pubis_L"] + PL["pubis_R"]) / 2 + np.array([0, -0.01, 0.005]), "pubic symphysis"),
             (lp[np.argmin(lp[:, 2])], "ischial tuberosity (“sitting bone”)"),
             (FL["ltroch_L"], "lesser trochanter (psoas insertion)")]
    pts = [(P(p)[1], P(p), t) for p, t in items]
    if obt is not None:
        pts.append((obt[1], obt, "obturator foramen"))
    pts = sorted(pts, key=lambda r: r[0])
    tx = 14 + w + 22
    ys = np.linspace(26, 262, len(pts))
    for (py, p, t), ty in zip(pts, ys):
        b.append(lab(p, t, tx, ty))
    return FG.svg(W, H, "".join(b))


# ============================================================================ pelvic tilt
def _tilted(angle):
    """Lumbar spine, sacrum, pelvis and proximal femurs with the pelvis tilted by `angle` degrees
    (positive = anterior tilt) about the hip axis; the lumbar curve absorbs the change so that
    T11 keeps its orientation."""
    PL = A.pelvis_landmarks()
    hc = (PL["hip_L"] + PL["hip_R"]) / 2
    ax = np.array([1.0, 0, 0])
    names = ["T10", "T11", "T12", "L1", "L2", "L3", "L4", "L5"]
    V, D = A.spine()
    parts = []   # (verts, faces, colour, level) level: 0 pelvis/sacrum, 1..: vertebra index from L5 up
    for fn in ("r_pelvis.vtp", "l_pelvis.vtp"):
        v, F = A.mesh("pelvis", fn)
        parts.append([v, F, A.BONE, 0])
    sv, sF = A.sacrum()
    parts.append([sv, sF, A.SACR, 0])
    order = names[::-1]  # L5 .. T10
    for i, k in enumerate(order):
        parts.append([V[k][0], V[k][1], A.LUMB if k[0] == "L" else A.THOR, i + 1])
    for i, k in enumerate(order):
        d = disc_below(k)
        if d is not None:
            parts.append([d[0], d[1], A.DISC, i])   # the disc below vertebra k moves with the segment below
    # whole column + pelvis rotated about the hip axis (positive x rotation tips the top backwards;
    # anterior tilt = top of the pelvis forward = -y)
    R0 = rot(hc, ax, angle)
    for p in parts:
        p[0] = R0(p[0])
    # un-rotate the column joint by joint (L5/S1 ... T12/L1), sharing the angle over 6 joints
    joints = order[:6]
    for j, k in enumerate(joints):
        vk = [p for p in parts if p[3] == j + 1 and p[2] != A.DISC][0][0]
        pivot = np.array([0, np.percentile(vk[:, 1], 20), vk[:, 2].min()])
        Rj = rot(pivot, ax, -angle / len(joints))
        for p in parts:
            if p[3] >= j + 1:
                p[0] = Rj(p[0])
    objs = [O(p[0], p[1], p[2]) for p in parts]
    for s in ("r", "l"):
        v, F = A.mesh(f"femur_{s}")
        top = v[:, 2].max()
        v2, F2 = clip(v, F, v[:, 2] > top - 0.16)
        objs.append(O(v2, F2, A.BONE))
    asis = R0(PL["asis_R"])
    pub = R0(PL["pubis_R"])
    return objs, asis, pub


def fig_pelvictilt():
    W, H = 470, 214
    b = []
    panels = [("Anterior tilt", 12, "ASIS moves forward and down;\nlumbar lordosis increases"),
              ("Neutral", 0, "ASIS and pubic symphysis\nroughly in one vertical plane"),
              ("Posterior tilt", -12, "ASIS moves back and up;\nlumbar curve flattens")]
    # a common frame so the three panels share scale and position
    allpts = []
    scenes = []
    for lab_, ang, note in panels:
        objs, asis, pub = _tilted(ang)
        scenes.append((objs, asis, pub))
        allpts.append(np.concatenate([o["verts"] for o in objs]))
    fitpts = np.concatenate(allpts)
    lo, hi = fitpts.min(0), fitpts.max(0)
    box8 = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    for i, ((lab_, ang, note), (objs, asis, pub)) in enumerate(zip(panels, scenes)):
        info = S.render_scene(f"tilt{i}", objs, view=(0, 0), width=520, samples=48, fit=box8)
        w = 160 * info["w"] / info["h"]
        x0 = 82 + i * 153 - w / 2
        el, w, h, P = place(info, x0, 20, h=160)
        b.append(el)
        pa, pp = P(asis), P(pub)
        b.append(f'<line x1="{f(pa[0])}" y1="{f(pa[1])}" x2="{f(pp[0])}" y2="{f(pp[1])}" stroke="{C["ink2"]}" stroke-width=".6" stroke-dasharray="2 1.5"/>')
        b.append(f'<circle cx="{f(pa[0])}" cy="{f(pa[1])}" r="2.6" fill="{C["clay"]}" stroke="#fff" stroke-width=".5"/>'
                 f'<circle cx="{f(pp[0])}" cy="{f(pp[1])}" r="2.6" fill="{C["blue"]}" stroke="#fff" stroke-width=".5"/>')
        # vertical reference through the pubic symphysis
        b.append(f'<line x1="{f(pp[0])}" y1="{f(pp[1]+4)}" x2="{f(pp[0])}" y2="{f(pa[1]-26)}" stroke="{C["gold"]}" stroke-width=".5"/>')
        cx = 82 + i * 153
        b.append(T(cx, 192, lab_, 10, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(cx, 201, note.split("\n")[0], 5.8, C["ink2"], "middle"))
        b.append(T(cx, 208, note.split("\n")[1], 5.8, C["ink2"], "middle"))
    b.append(T(14, 12, "PELVIC TILT · lateral view, facing right · rotation occurs at the hip joints", 6.4, C["golddeep"], "start", 700, ls=.6))
    b.append(f'<circle cx="372" cy="10" r="2.4" fill="{C["clay"]}"/>' + T(377, 12, "ASIS", 6, C["ink2"]))
    b.append(f'<circle cx="400" cy="10" r="2.4" fill="{C["blue"]}"/>' + T(405, 12, "pubic symphysis", 6, C["ink2"]))
    return FG.svg(W, H, "".join(b))


# ============================================================================ shoulder
def fig_shoulder():
    W, H = 480, 262
    R = ribs_parts()
    scv, scF = R["scap"]["R"]
    clv, clF = R["clav"]["R"]
    hv, hF = A.mesh("humerus_r")
    objs = [O(scv, scF, A.BONE), O(clv, clF, A.BONE), O(hv, hF, A.BONE)]
    for v, F in R["ribs"]:
        if v[:, 0].mean() < 0.01:
            objs.append(O(v, F, "#E6DDCC", alpha=0.55))
    objs += spine_objs([f"T{i}" for i in range(1, 11)] + ["C6", "C7"], color_by_region=False)
    fitp = np.concatenate([scv, clv, hv[hv[:, 2] > hv[:, 2].max() - 0.16], np.array([[0.02, 0.1, 1.46], [0.02, 0.1, 1.2]])])
    info = S.render_scene("shoulder-post", objs, view=(270, 6), width=900, samples=64, fit=fitp)
    el, w, h, P = place(info, 20, 12, h=236)
    b = [el]
    L = {}
    L["acromion"] = scv[np.argmin(scv[:, 0] - 0.4 * scv[:, 2])]
    L["inferior"] = scv[np.argmin(scv[:, 2])]
    z0, z1 = scv[:, 2].min(), scv[:, 2].max()
    zf = lambda t: z0 + t * (z1 - z0)  # noqa: E731
    mid = scv[(scv[:, 2] > zf(0.35)) & (scv[:, 2] < zf(0.55))]
    L["medial"] = mid[np.argmax(mid[:, 0])]
    x0_, x1_ = scv[:, 0].min(), scv[:, 0].max()
    up = scv[(scv[:, 2] > zf(0.70)) & (scv[:, 2] < zf(0.90)) & (scv[:, 0] > x0_ + 0.35 * (x1_ - x0_)) & (scv[:, 0] < x0_ + 0.7 * (x1_ - x0_))]
    L["spine"] = up[np.argmax(up[:, 1])]
    L["clav"] = clv[np.argmax(clv[:, 2] + 0.2 * clv[:, 0])]
    L["head"] = hv[np.argmax(hv[:, 2])] + np.array([0, 0.012, -0.012])
    L["body"] = np.array([scv[:, 0].mean(), scv[:, 1].max(), zf(0.40)])
    L["sup"] = scv[np.argmax(scv[:, 2] + 0.5 * scv[:, 0])]
    items = [("clav", "clavicle"), ("sup", "superior angle"), ("acromion", "acromion"), ("spine", "spine of the scapula"),
             ("head", "head of humerus (glenohumeral joint)"), ("medial", "medial border"), ("body", "scapula lies on the rib cage:\nthe scapulothoracic “joint”"),
             ("inferior", "inferior angle")]
    pts = sorted([(P(L[k])[1], P(L[k]), t) for k, t in items])
    tx = 20 + w + 26
    for (py, p, t), ty in zip(pts, np.linspace(26, 170, len(pts))):
        b.append(lab(p, t, tx, ty))
    b.append(T(20 + w / 2, 258, "Right shoulder girdle, posterior view", 6.4, C["golddeep"], "middle", 600))
    b.append(T(tx, 192, "Scapular movements", 10, C["forest"], "start", 600, family="Cormorant"))
    mv = [("Elevation / depression", "shrugging up / drawing down"), ("Protraction / retraction", "sliding forward around the ribs / squeezing back"),
          ("Upward / downward rotation", "glenoid turns up (arms overhead) / down")]
    for i, (a, d) in enumerate(mv):
        b.append(T(tx, 206 + i * 19, a, 6.5, C["ink"], "start", 600))
        b.append(T(tx, 214 + i * 19, d, 5.8, C["ink2"]))
    return FG.svg(W, H, "".join(b))


# ============================================================================ knee
def _knee_parts():
    fv, fF = A.mesh("femur_r")
    tv, tF = A.mesh("tibia_r", "r_tibia.vtp")
    bv, bF = A.mesh("tibia_r", "r_fibula.vtp")
    kz_t = tv[:, 2].max()
    kz_f = fv[:, 2].min()
    fv2, fF2 = clip(fv, fF, fv[:, 2] < kz_f + 0.13)
    tv2, tF2 = clip(tv, tF, tv[:, 2] > kz_t - 0.15)
    bv2, bF2 = clip(bv, bF, bv[:, 2] > kz_t - 0.17)
    top = tv[tv[:, 2] > kz_t - 0.012]
    xc = top[:, 0].mean()
    yc = top[:, 1].mean()
    med = top[top[:, 0] > xc]   # right knee: medial is towards +x
    latr = top[top[:, 0] <= xc]
    cm = np.array([med[:, 0].mean(), med[:, 1].mean(), kz_t])
    cl = np.array([latr[:, 0].mean(), latr[:, 1].mean(), kz_t])
    fx = fv[fv[:, 2] < kz_f + 0.05]
    return dict(fem=(fv2, fF2), tib=(tv2, tF2), fib=(bv2, bF2), kz_t=kz_t, kz_f=kz_f, xc=xc, yc=yc, cm=cm, cl=cl,
                fmed=fx[np.argmax(fx[:, 0])], flat=fx[np.argmin(fx[:, 0])], fibtop=bv[np.argmax(bv[:, 2])])


def fig_knee():
    W, H = 440, 262
    K = _knee_parts()
    tv_full, _ = A.mesh("tibia_r", "r_tibia.vtp")
    objs = [O(*K["fem"], A.BONE, alpha=0.40), O(*K["tib"], A.BONE), O(*K["fib"], A.BONE)]
    zt = K["kz_t"]
    zf = K["kz_f"]

    def plateau(x, y):
        near = tv_full[(np.abs(tv_full[:, 0] - x) < 0.008) & (np.abs(tv_full[:, 1] - y) < 0.008)]
        return (near[:, 2].max() if len(near) else zt - 0.006) + 0.003
    # menisci: medial C-shaped (opening towards the centre, i.e. -x), lateral almost ring-shaped (+x)
    men = {}
    for side, c, r, a0, a1 in (("med", K["cm"], 0.019, -130, 130), ("lat", K["cl"], 0.016, 35, 325)):
        th = np.radians(np.linspace(a0, a1, 44))
        pts = np.c_[c[0] + np.cos(th) * r, c[1] + np.sin(th) * r * 1.15, np.zeros_like(th)]
        pts[:, 2] = [plateau(x, y) for x, y, _ in pts]
        v, F = tube(pts, 0.0032, belly=0.0042, n=44)
        objs.append(O(v, F, MENISCUS, subdiv=1))
        men[side] = pts[np.argmax(pts[:, 0])] if side == "med" else pts[np.argmin(pts[:, 0])]
    xc, yc = K["xc"], K["yc"]
    # cruciates (in the intercondylar notch): ACL from the anterior tibia to the lateral femoral
    # condyle (posteriorly); PCL from the posterior tibia to the medial femoral condyle (anteriorly)
    acl = [np.array([xc + 0.003, yc - 0.014, zt - 0.002]), np.array([xc - 0.004, yc - 0.002, zt + 0.014]),
           np.array([xc - 0.011, yc + 0.012, zf + 0.030])]
    pcl = [np.array([xc - 0.001, yc + 0.022, zt - 0.008]), np.array([xc + 0.004, yc + 0.008, zt + 0.014]),
           np.array([xc + 0.010, yc - 0.006, zf + 0.030])]
    va, Fa = tube(acl, 0.0045, belly=0.006)
    vp, Fp = tube(pcl, 0.005, belly=0.0065)
    objs += [O(va, Fa, "#C0563C"), O(vp, Fp, "#3F6F9C")]
    # collaterals, hugging the bones
    fm, fl, fb = K["fmed"], K["flat"], K["fibtop"]
    band = lambda zz: tv_full[np.abs(tv_full[:, 2] - zz) < 0.006]  # noqa: E731
    tm1 = band(zt - 0.005)
    tm1 = tm1[np.argmax(tm1[:, 0])]
    tm2 = band(zt - 0.065)
    tm2 = tm2[np.argmax(tm2[:, 0])]
    mcl = [fm + np.array([0.002, 0.004, 0.0]), tm1 + np.array([0.003, 0.002, 0]), tm2 + np.array([0.002, 0.0, 0])]
    lcl = [fl + np.array([-0.002, 0.006, 0.0]), fb + np.array([-0.001, 0.0, 0.004])]
    vm, Fm = tube(mcl, 0.0035, belly=0.0045)
    vl, Fl = tube(lcl, 0.0032)
    objs += [O(vm, Fm, LIG), O(vl, Fl, LIG)]
    info = S.render_scene("knee-ant", objs, view=(90, -6), width=800, samples=64)
    el, w, h, P = place(info, 30, 16, h=236)
    b = [el]
    items = [((K["fem"][0][:, 0].mean(), K["fem"][0][:, 1].min() + 0.02, zf + 0.075), "femur (drawn see-through)"),
             (acl[1] + np.array([0, 0, 0.004]), "anterior cruciate ligament (ACL)"), (pcl[2] - np.array([0, 0, 0.006]), "posterior cruciate ligament (PCL)"),
             (men["med"], "medial meniscus"), (men["lat"], "lateral meniscus"),
             (mcl[1], "medial collateral ligament (MCL)"), (lcl[0] * 0.4 + lcl[1] * 0.6, "lateral collateral ligament (LCL)"),
             ((xc, yc - 0.03, zt - 0.045), "tibia"), (fb + np.array([0, -0.01, -0.03]), "fibula")]
    pts = [(P(p)[1], P(p), t) for p, t in items]
    tx = 30 + w + 30
    order = sorted(range(len(pts)), key=lambda i: pts[i][0])
    ys = np.linspace(24, 184, len(pts))
    for i, ty in zip(order, ys):
        b.append(lab(pts[i][1], pts[i][2], tx, ty))
    b.append(T(30 + w * 0.12, 12, "lateral", 5.8, C["ink2"], "middle", italic=True) + T(30 + w * 0.88, 12, "medial", 5.8, C["ink2"], "middle", italic=True))
    b.append(T(tx, 212, "The knee is mainly a hinge (flexion/extension)\nwith a little rotation when flexed. It tolerates\ntwisting under load poorly — which is why\nlotus is never forced from the knee.", 6.2, C["teak"], italic=True))
    return FG.svg(W, H, "".join(b))


# ============================================================================ foot
def _foot():
    fv, fF = A.mesh("calcn_r")
    tv, tF = A.mesh("toes_r")
    av, aF = A.mesh("talus_r")
    tb, tbF = A.mesh("tibia_r", "r_tibia.vtp")
    fb, fbF = A.mesh("tibia_r", "r_fibula.vtp")
    z0 = min(fv[:, 2].min(), tv[:, 2].min())
    tb2, tbF2 = clip(tb, tbF, tb[:, 2] < z0 + 0.14)
    fb2, fbF2 = clip(fb, fbF, fb[:, 2] < z0 + 0.14)
    allv = np.concatenate([fv, tv])
    low = allv[allv[:, 2] < z0 + 0.012]
    ymid = (allv[:, 1].min() + allv[:, 1].max()) / 2
    heel = low[low[:, 1] > ymid]
    fore = fv[fv[:, 1] < np.percentile(fv[:, 1], 18)]
    fore_low = fore[fore[:, 2] < np.percentile(fore[:, 2], 30)]
    L = dict(heel=heel[np.argmin(heel[:, 2] - 0.3 * heel[:, 1])],
             m1=fore_low[np.argmax(fore_low[:, 0])], m5=fore_low[np.argmin(fore_low[:, 0])])
    mid = fv[(fv[:, 1] > np.percentile(fv[:, 1], 40)) & (fv[:, 1] < np.percentile(fv[:, 1], 62))]
    L["navicular"] = mid[np.argmax(mid[:, 0] + 0.3 * mid[:, 2])]
    L["talus"] = av[np.argmax(av[:, 2])]
    L["calc"] = fv[np.argmax(fv[:, 1])]
    m1s = fv[(fv[:, 1] < np.percentile(fv[:, 1], 35)) & (fv[:, 1] > np.percentile(fv[:, 1], 12))]
    L["met1"] = m1s[np.argmax(m1s[:, 0] + m1s[:, 2])]
    objs = [O(fv, fF), O(tv, tF), O(av, aF), O(tb2, tbF2), O(fb2, fbF2)]
    return objs, L, z0


def fig_foot():
    W, H = 470, 212
    objs, L, z0 = _foot()
    b = []
    # medial view of the right foot (camera on the medial side, +x)
    info = S.render_scene("foot-med", objs, view=(180, 0), width=900, samples=64)
    el, w, h, P = place(info, 14, 36, w=270)
    b.append(el)
    heel, m1 = P(L["heel"]), P(L["m1"])
    # plantar fascia and the arch
    b.append(f'<path d="M{f(heel[0])},{f(heel[1]+2)} Q{f((heel[0]+m1[0])/2)},{f(max(heel[1], m1[1])+5)} {f(m1[0])},{f(m1[1]+2)}" fill="none" stroke="{C["terra"]}" stroke-width="1.6" stroke-dasharray="3 2"/>')
    nv = P(L["navicular"])
    b.append(f'<path d="M{f(heel[0])},{f(heel[1]-3)} Q{f(nv[0])},{f(nv[1]-8)} {f(m1[0])},{f(m1[1]-3)}" fill="none" stroke="{C["golddeep"]}" stroke-width="1"/>')
    tops = sorted([("met1", "1st metatarsal"), ("navicular", "navicular (keystone\nof the arch)"), ("talus", "talus")],
                  key=lambda it: P(L[it[0]])[0])
    xs = np.linspace(14 + 0.25 * w, 14 + 0.85 * w, len(tops))
    for (k, t), tx in zip(tops, xs):
        b.append(lab(P(L[k]), t, tx, 26, "middle"))
    b.append(lab(P(L["calc"]), "calcaneus", P(L["calc"])[0], 198, "middle"))
    b.append(lab(((heel[0] + m1[0]) / 2, max(heel[1], m1[1]) + 3.5), "plantar fascia", (heel[0] + m1[0]) / 2 - 30, 198, "middle"))
    b.append(T(14 + w / 2, 10, "Medial longitudinal arch (right foot, medial view)", 6.4, C["golddeep"], "middle", 600))
    # plantar view with the tripod
    # sole view: turn the foot over (180° about the antero-posterior axis) and look down on it
    flip = lambda p: np.asarray(p, float) * np.array([-1, 1, -1])  # noqa: E731
    sole = [dict(o, verts=flip(o["verts"])) for o in objs[:3]]
    info2 = S.render_scene("foot-plantar", sole, view=(0, 89.9), width=700, samples=64, up=(0, -1, 0))
    el2, w2, h2, P2_ = place(info2, 340, 26, h=176)
    P2 = lambda p: P2_(flip(p))  # noqa: E731
    b.append(el2)
    pts = [P2(L["heel"]), P2(L["m1"]), P2(L["m5"])]
    b.append(f'<polygon points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}" fill="{C["gold"]}" fill-opacity=".12" stroke="{C["golddeep"]}" stroke-width=".8" stroke-dasharray="2 1.5"/>')
    for x, y in pts:
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="6" fill="{C["gold"]}" fill-opacity=".55" stroke="{C["golddeep"]}"/>')
    b.append(T(340 + w2 / 2, 14, "The “tripod” of the foot (sole)", 6.4, C["golddeep"], "middle", 600))
    (hx, hy), (ax, ay), (cx_, cy_) = pts
    # which side is medial in the plantar image: 1st metatarsal side
    m1_left = ax < cx_
    b.append(T(ax + (-10 if m1_left else 10), ay - 6, "big-toe\nmound", 5.8, C["ink2"], "end" if m1_left else "start"))
    b.append(T(cx_ + (10 if m1_left else -10), cy_ - 6, "little-toe\nmound", 5.8, C["ink2"], "start" if m1_left else "end"))
    b.append(T(hx + 10, hy + 4, "heel", 5.8, C["ink2"]))
    return FG.svg(W, H, "".join(b))


# ============================================================================ hand
def fig_hand():
    W, H = 470, 214
    B = skeleton.bones()["hand_r"]
    objs = [O(v, F) for mf, v, F in B]
    rv, rF = A.mesh("radius_r")
    uv, uF = A.mesh("ulna_r")
    zc = min(v[:, 2].min() for mf, v, F in B)
    ztop = max(v[:, 2].max() for mf, v, F in B)
    rv2, rF2 = clip(rv, rF, rv[:, 2] < ztop + 0.03)
    uv2, uF2 = clip(uv, uF, uv[:, 2] < ztop + 0.03)
    objs += [O(rv2, rF2), O(uv2, uF2)]
    get = {mf: v for mf, v, F in B}
    # palmar view: the palm faces anterior (-y) in the anatomical position
    info = S.render_scene("hand-palm", objs, view=(90, 0), width=700, samples=64, up=(0, 0, -1))  # fingers up
    el, w, h, P = place(info, 40, 10, h=190)
    b = [el]
    m2 = get["metacarpal2_rvs.vtp"]
    m1 = get["metacarpal1_rvs.vtp"]
    m5 = get["metacarpal5_rvs.vtp"]
    carp = np.concatenate([get["capitate_rvs.vtp"], get["hamate_rvs.vtp"], get["scaphoid_rvs.vtp"], get["lunate_rvs.vtp"]])
    pts = [(m2[np.argmin(m2[:, 2])], "base of the index finger\n(2nd MCP joint)"), (m1.mean(0), "thumb mound (thenar)"),
           (m5.mean(0), "outer edge (hypothenar)"), (carp.mean(0), "heel of the hand (carpus)")]
    tx = 40 + w + 20
    for (p3, t), ty in zip(sorted(pts, key=lambda r: P(r[0])[1]), np.linspace(40, 160, 4)):
        p = P(p3)
        b.append(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="7" fill="{C["gold"]}" fill-opacity=".45" stroke="{C["golddeep"]}"/>')
        b.append(lab(p, t, tx, ty, dot=False))
    b.append(T(40 + w / 2, 208, "Right hand, palmar view: loading points", 6.4, C["golddeep"], "middle", 600))
    b.append(T(tx, 184, "Spread the load around the whole rim\nof the palm; press through the base of the\nindex finger and thumb.", 6.0, C["teak"], italic=True))
    # wrist angle panel
    x0, y0 = 400, 150
    b.append(f'<line x1="{x0-40}" y1="{y0}" x2="{x0+64}" y2="{y0}" stroke="#CDBFA5"/>')
    b.append(f'<line x1="{x0-30}" y1="{y0}" x2="{x0}" y2="{y0}" stroke="{C["forest"]}" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<line x1="{x0-30}" y1="{y0}" x2="{x0-30}" y2="{y0-70}" stroke="{C["sage"]}" stroke-width="7" stroke-linecap="round"/>')
    b.append(f'<path d="M{x0-14},{y0} A16,16 0 0 0 {x0-30},{y0-16}" fill="none" stroke="{C["clay"]}" stroke-width="1"/>')
    b.append(T(x0 - 36, y0 - 46, "≈ 90° wrist\nextension\n(plank)", 5.8, C["clay"], "end"))
    b.append(f'<line x1="{x0+20}" y1="{y0}" x2="{x0+52}" y2="{y0}" stroke="{C["forest"]}" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<line x1="{x0+20}" y1="{y0}" x2="{x0+54}" y2="{y0-58}" stroke="{C["sage"]}" stroke-width="7" stroke-linecap="round"/>')
    b.append(T(x0 + 22, y0 + 12, "less extension\n(downward dog)", 5.8, C["ink2"]))
    b.append(T(x0 + 10, 30, "Wrist angle under load", 6.4, C["golddeep"], "middle", 600))
    return FG.svg(W, H, "".join(b))


# ============================================================================ ribs
def _thorax(alpha=1.0, ribs_col="#E6DCC8"):
    R = ribs_parts()
    objs = [O(v, F, ribs_col, alpha=alpha) for v, F in R["ribs"]]
    sv, sF = R["sternum"]
    objs.append(O(sv, sF, "#DCD4C0", alpha=alpha))
    objs += spine_objs([f"T{i}" for i in range(1, 13)] + ["L1", "L2", "L3", "C7"], color_by_region=False)
    return objs, R


def fig_ribs():
    W, H = 470, 200
    objs, R = _thorax()
    b = []
    info = S.render_scene("thorax-lat", objs, view=(0, 0), width=700, samples=64)
    el, w, h, P = place(info, 30, 16, h=150)
    b.append(el)
    sv = R["sternum"][0]
    stern = sv[np.argmin(sv[:, 1])]
    ps = P(stern)
    b.append(FG.arrow(ps[0] + 6, ps[1], ps[0] + 26, ps[1] - 14, C["clay"], 1.3, "arrt"))
    b.append(lab(ps, "sternum", ps[0] + 30, ps[1] + 16))
    b.append(T(30 + w / 2, 182, "Pump-handle motion (upper ribs, side view):\nthe sternum moves forward and up", 6.2, C["forest"], "middle", 600))
    info2 = S.render_scene("thorax-front", objs, view=(90, 0), width=700, samples=64)
    el2, w2, h2, P2 = place(info2, 300, 16, h=150)
    b.append(el2)
    ribs = sorted(R["ribs"], key=lambda r: r[0][:, 2].min())
    for v, F in ribs[:4]:
        side = 1 if v[:, 0].mean() > 0 else -1
        p = v[np.argmax(v[:, 0] * side)]
        q = P2(p)
        b.append(FG.arrow(q[0] + side * 3, q[1], q[0] + side * 16, q[1] - 6, C["clay"], 1.1, "arrt"))
    b.append(T(300 + w2 / 2, 182, "Bucket-handle motion (lower ribs, front view):\nribs swing up and out, widening the chest", 6.2, C["forest"], "middle", 600))
    return FG.svg(W, H + 8, "".join(b))


# ============================================================================ diaphragm
def _dome(inhale):
    """Diaphragm as a double-domed sheet inside the lower rib cage. The rim follows the costal
    margin (high at the xiphoid in front, low at the back over the upper lumbar vertebrae); the
    right cupola sits higher than the left. Inhalation lowers and flattens the domes and the lower
    ribs widen."""
    yc, ry = 0.085, 0.080
    rx = 0.106 * (1.05 if inhale else 1.0)
    H0 = 0.105 if not inhale else 0.068
    n_r, n_t = 22, 72
    V, Fc = [], []
    for i in range(n_r + 1):
        r = i / n_r
        for j in range(n_t):
            t = 2 * np.pi * j / n_t
            ct, st = np.cos(t), np.sin(t)          # st < 0: anterior, st > 0: posterior
            x = rx * r * ct
            y = yc + ry * r * st
            # rim height: xiphoid ~1.20 in front, costal margin sloping to ~1.13 laterally, ~1.10 at the back
            rim = 1.150 + 0.060 * max(-st, 0) ** 1.5 - 0.040 * max(st, 0) - (0.008 if inhale else 0)
            lobes = np.exp(-((x + 0.05) / 0.055) ** 2) * 1.10 + np.exp(-((x - 0.05) / 0.055) ** 2) * 1.0  # right (x<0) higher
            ctr = 0.72 + 0.28 * lobes
            rim_c = 1.150 + 0.02 * (1 - r)          # the centre rises from the average rim height
            z = rim * r ** 2 + rim_c * (1 - r ** 2) + H0 * (1 - r ** 2) ** 0.6 * ctr
            V.append([x, y, z])
    for i in range(n_r):
        for j in range(n_t):
            a, b = i * n_t + j, i * n_t + (j + 1) % n_t
            Fc.append([a, b, b + n_t, a + n_t])
    return np.array(V), Fc


def crura(inhale=False):
    """Right (longer) and left crura: from the posterior dome down the front of L1–L3 (L1–L2 on the left)."""
    out = []
    for sx, low in ((-1, "L3"), (1, "L2")):
        l1, lo = vcentre("L1"), vcentre(low)
        front = lambda c: np.array([sx * 0.012, A.spine()[0][low][0][:, 1].min() - 0.004, c[2]])  # noqa: E731
        top = np.array([sx * 0.02, 0.105, 1.16 - (0.01 if inhale else 0)])
        cv, cF = tube([top, front(l1) + np.array([0, 0, 0.02]), front(lo)], 0.005, belly=0.008)
        out.append(O(cv, cF, "#9E4431"))
    return out


def fig_diaphragm():
    W, H = 470, 236
    b = []
    V, D = A.spine()
    for i, (lab_, inh) in enumerate((("Exhalation", False), ("Inhalation", True))):
        objs, R = _thorax(alpha=0.42)
        dv, dF = _dome(inh)
        objs.append(O(dv, dF, "#B5533C", rough=0.5, subdiv=1, fix=False))
        objs += crura(inh)
        fitb = np.array([[-0.16, 0, 1.0], [0.16, 0, 1.46]])
        info = S.render_scene(f"diaph{int(inh)}", objs, view=(90, 4), width=700, samples=64, fit=fitb)
        el, w, h, P = place(info, 20 + i * 230, 8, h=200)
        b.append(el)
        cx = 20 + i * 230 + w / 2
        b.append(T(cx, 226, lab_, 11, C["forest"], "middle", 600, family="Cormorant"))
        top = P([-0.05, 0.085, 1.170 + (0.068 if inh else 0.105)])
        if inh:
            b.append(FG.arrow(top[0], top[1] - 30, top[0], top[1] - 6, C["clay"], 1.2, "arrt"))
            b.append(FG.arrow(20 + i * 230 + w - 8, 120, 20 + i * 230 + w + 10, 116, C["clay"], 1.2, "arrt"))
            b.append(FG.arrow(20 + i * 230 + 8, 120, 20 + i * 230 - 10, 116, C["clay"], 1.2, "arrt"))
        else:
            b.append(lab(top, "diaphragm (dome)", 20 + i * 230 + w - 4, 30, "start"))
            crus = P([-0.012, A.spine()[0]["L2"][0][:, 1].min() - 0.004, vcentre("L2")[2]])
            b.append(lab(crus, "crura attach to the\nlumbar vertebrae", 20 + i * 230 + w - 4, 190, "start"))
    return FG.svg(W, H + 4, "".join(b))


# ============================================================================ muscles on the skeleton
def muscle_points(name):
    pts = np.asarray(skeleton.muscles()[name]["points"], float)
    if name.startswith("psoas"):
        # the model starts psoas at the pelvic rim; add its origin along the sides of T12–L4
        sx = 1 if name.endswith("_l") else -1
        V = A.spine()[0]
        up = []
        for k in ("T12", "L1", "L2", "L3", "L4"):
            c = A.body_centre(V[k])
            up.append(np.array([c[0] + sx * 0.026, c[1] + 0.004, c[2]]))
        up = [p for p in up if p[2] > pts[0][2] + 0.02]
        pts = np.r_[np.array(up), pts]
    return pts


def muscle_tube(name, belly=0.012, end=0.004):
    return tube(muscle_points(name), end, belly=belly, n=48)


def leg_skeleton(side="r", alpha=1.0, with_spine=True):
    objs = []
    for fn in ("r_pelvis.vtp", "l_pelvis.vtp"):
        v, F = A.mesh("pelvis", fn)
        objs.append(O(v, F, A.BONE, alpha=alpha))
    sv, sF = A.sacrum()
    objs.append(O(sv, sF, A.BONE, alpha=alpha))
    for s in ("r", "l"):
        for body in (f"femur_{s}", f"tibia_{s}", f"patella_{s}"):
            v, F = A.mesh(body)
            objs.append(O(v, F, A.BONE, alpha=alpha))
    if with_spine:
        objs += [dict(o, alpha=alpha) for o in spine_objs(["T11", "T12", "L1", "L2", "L3", "L4", "L5"], color_by_region=False)]
        objs += discs_between(["T11", "L5"])
    return objs


def fig_hamstring_psoas():
    W, H = 470, 262
    b = []
    M = skeleton.muscles()
    # hamstrings, posterior view of the right leg
    objs = leg_skeleton()
    for nm, col, bel in (("bflh_r", MUSCLE, 0.016), ("bfsh_r", "#C9745C", 0.012), ("semiten_r", MUSCLE, 0.013), ("semimem_r", "#A2483A", 0.017)):
        if nm in M:
            v, F = muscle_tube(nm, bel)
            objs.append(O(v, F, col, rough=0.5))
    fit = np.array([[-0.26, 0.05, 0.40], [0.10, 0.05, 1.10]])
    info = S.render_scene("hams-post", objs, view=(270, 4), width=700, samples=64, fit=fit)
    el, w, h, P = place(info, 70, 8, h=232)
    b.append(el)
    PL = A.pelvis_landmarks()
    b.append(lab(P(PL["ischial_R"]), "ischial tuberosity\n(common origin)", 64, P(PL["ischial_R"])[1] - 8, "end", 5.8))
    if "bflh_r" in M:
        pb = M["bflh_r"]["points"]
        b.append(lab(P(pb[-1]), "biceps femoris →\nhead of the fibula\n(lateral)", 70 + w + 6, P(pb[-1])[1] - 10, "start", 5.8))
    if "semiten_r" in M:
        ps = M["semiten_r"]["points"]
        b.append(lab(P(ps[-1]), "semitendinosus and\nsemimembranosus →\nmedial tibia", 64, P(ps[-1])[1] - 10, "end", 5.8))
    b.append(T(70 + w / 2, 256, "Hamstrings (right leg, posterior view)", 7, C["clay"], "middle", 600))
    # psoas and iliacus, anterior view
    objs2 = leg_skeleton()
    for nm, col, bel in (("psoas_r", MUSCLE2, 0.016), ("iliacus_r", "#6D8FB0", 0.016), ("psoas_l", MUSCLE2, 0.016), ("iliacus_l", "#6D8FB0", 0.016)):
        if nm in M:
            v, F = muscle_tube(nm, bel, 0.005)
            objs2.append(O(v, F, col, rough=0.5))
    fit2 = np.array([[-0.19, 0, 0.62], [0.19, 0, 1.18]])
    info2 = S.render_scene("psoas-ant", objs2, view=(90, 4), width=800, samples=64, fit=fit2)
    el2, w2, h2, P2 = place(info2, 236, 8, h=232)
    b.append(el2)
    if "psoas_l" in M:
        pp = M["psoas_l"]["points"]
        b.append(lab(P2(pp[0]), "psoas major: from\nT12–L4 (bodies and\ntransverse processes)", 236 + w2 + 5, P2(pp[0])[1] - 10))
        b.append(lab(P2(pp[-1]), "lesser trochanter\n(common insertion)", 236 + w2 + 5, P2(pp[-1])[1] + 8))
    if "iliacus_l" in M:
        pi = M["iliacus_l"]["points"]
        b.append(lab(P2(pi[0]), "iliacus: from the\niliac fossa", 236 + w2 + 5, P2(pi[0])[1] + 4))
    b.append(T(236 + w2 / 2, 256, "Psoas major and iliacus (anterior view)", 7, C["blue"], "middle", 600))
    return FG.svg(W, H + 6, "".join(b))


# ============================================================================ atlas scenes
def atlas_scene(key):
    """Skeleton scenes for deep muscles in the muscle atlas; returns a scene3d info dict."""
    M = skeleton.muscles()
    PL = A.pelvis_landmarks()
    FL = A.femur_landmarks()
    if key == "diaphragm":
        objs, R = _thorax(alpha=0.42)
        dv, dF = _dome(False)
        objs.append(O(dv, dF, MUSCLE, rough=0.5, subdiv=1, fix=False))
        objs += crura(False)
        return S.render_scene("atlas-diaphragm", objs, view=(90, 4), width=520, samples=48,
                              fit=np.array([[-0.16, 0, 1.0], [0.16, 0, 1.46]]))
    objs = leg_skeleton(with_spine=True)
    if key in ("psoas", "iliacus"):
        for s in ("r", "l"):
            nm = f"{key}_{s}"
            v, F = muscle_tube(nm, 0.016, 0.005)
            objs.append(O(v, F, MUSCLE, rough=0.5))
        return S.render_scene(f"atlas-{key}", objs, view=(90, 4), width=520, samples=48,
                              fit=np.array([[-0.19, 0, 0.66], [0.19, 0, 1.18]]))
    if key == "glutmed":
        for nm, col, bel in (("glmin1_r", "#7E8FA8", 0.010), ("glmin2_r", "#7E8FA8", 0.010), ("glmin3_r", "#7E8FA8", 0.010),
                             ("glmed1_r", MUSCLE, 0.013), ("glmed2_r", MUSCLE, 0.013), ("glmed3_r", MUSCLE, 0.013)):
            v, F = muscle_tube(nm, bel, 0.005)
            objs.append(O(v, F, col, rough=0.5))
        return S.render_scene("atlas-glutmed", objs, view=(0, 6), width=520, samples=48,
                              fit=np.array([[0, -0.12, 0.72], [0, 0.14, 1.12]]))
    if key == "rotators":
        v, F = muscle_tube("piri_r", 0.011, 0.004)
        objs.append(O(v, F, MUSCLE, rough=0.5))
        fr, _ = A.mesh("femur_r")
        topr = fr[fr[:, 2] > PL["hip_R"][2] - 0.04]
        gt = topr[np.argmin(topr[:, 0])]
        isch = PL["ischial_R"]
        sac = A.sacrum()[0]
        # obturator internus with the gemelli (lesser sciatic notch -> medial greater trochanter)
        notch = isch + np.array([0.012, 0.004, 0.035])
        v, F = tube([notch, (notch + gt) / 2 + np.array([0, 0.01, 0]), gt + np.array([0.008, 0.004, -0.010])], 0.004, belly=0.008)
        objs.append(O(v, F, "#C9745C", rough=0.5))
        # quadratus femoris (ischial tuberosity -> intertrochanteric crest)
        v, F = tube([isch + np.array([-0.004, 0.0, 0.012]), gt + np.array([0.012, 0.006, -0.045])], 0.006, belly=0.010)
        objs.append(O(v, F, "#A2483A", rough=0.5))
        return S.render_scene("atlas-rotators", objs, view=(270, 4), width=520, samples=48,
                              fit=np.array([[-0.20, 0, 0.72], [0.02, 0, 1.06]]))
    raise KeyError(key)
