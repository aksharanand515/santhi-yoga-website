"""
posefig — a small kinematic figure renderer for the manual's posture illustrations.

A pose is a dict of *absolute* segment angles in degrees (0 = pointing right, 90 = pointing
down, -90 = pointing up; SVG y-axis points down).  Segments hang off the hip joint (the
pelvis point), so body proportions stay identical in every illustration.

Keys
  lt, ut, nk     lower torso (hip->waist), upper torso (waist->neck base), neck
  hd, face       head axis (neck->crown) and the direction the face points
  ua1 fa1 h1     near arm: upper arm, forearm, hand      (…2 = far arm)
  th1 sh1 ft1    near leg: thigh, shin, foot             (…2 = far leg)
  view           'side' (default) or 'front'
  sw             shoulder spread factor in front view (1 = square to viewer, <1 = turned)
  flip           mirror horizontally (figure faces left)

Muscle overlays are drawn as spindles between anatomical anchor points, e.g.
  ('th1', 0.05, 'post') = near thigh, 5 % of the way from hip to knee, on its posterior surface.
"""
import math
import re

# proportions (arbitrary units; standing height ~172)
L = dict(lt=20, ut=33, nk=8, ua=29, fa=25, h=15, th=43, sh=42, ft=18, heel=5)
R = dict(  # radii at proximal/distal ends
    ua=(5.6, 4.3), fa=(4.2, 3.0), h=(3.1, 2.2), th=(9.2, 5.8), sh=(5.8, 3.6), ft=(3.3, 2.4), nk=(4.3, 4.3))
HEAD_R = 9.4

INK = "#4E5A3A"      # torso, head
LIMB = "#5B6845"     # near limbs
INK_FAR = "#A7AC8C"  # far side
PAPER = "#FFFEFA"
STRETCH = "#C2795C"  # lengthening muscle
ACTIVE = "#3D6475"   # contracting muscle
BONE = "#E9DFC8"


def unit(a):
    r = math.radians(a)
    return (math.cos(r), math.sin(r))


def add(p, v, s=1.0):
    return (p[0] + v[0] * s, p[1] + v[1] * s)


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def capsule(a, b, ra, rb):
    """Path for the convex hull of two circles (tapered limb)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1e-6
    ang = math.atan2(dy, dx)
    s = max(-0.99, min(0.99, (ra - rb) / d))
    off = math.acos(s)
    # tangent points
    a1 = (a[0] + ra * math.cos(ang + off), a[1] + ra * math.sin(ang + off))
    a2 = (a[0] + ra * math.cos(ang - off), a[1] + ra * math.sin(ang - off))
    b1 = (b[0] + rb * math.cos(ang + off), b[1] + rb * math.sin(ang + off))
    b2 = (b[0] + rb * math.cos(ang - off), b[1] + rb * math.sin(ang - off))
    return (f"M{f(a1[0])},{f(a1[1])} L{f(b1[0])},{f(b1[1])} "
            f"A{f(rb)},{f(rb)} 0 0 0 {f(b2[0])},{f(b2[1])} "
            f"L{f(a2[0])},{f(a2[1])} A{f(ra)},{f(ra)} 0 1 0 {f(a1[0])},{f(a1[1])} Z")


def catmull(pts, n=8):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


DEFAULT = dict(lt=-90, ut=-90, nk=-90, hd=-90, face=0,
               ua1=90, fa1=90, h1=90, ua2=90, fa2=90, h2=90,
               th1=90, sh1=90, ft1=0, th2=90, sh2=90, ft2=0,
               view="side", sw=1.0, flip=False)


class Figure:
    def __init__(self, pose):
        self.p = dict(DEFAULT)
        self.p.update(pose)
        self.solve()

    # ------------------------------------------------------------------ kinematics
    def solve(self):
        p = self.p
        J = {}
        front = p["view"] == "front"
        hip = (0.0, 0.0)
        J["hip"] = hip
        J["waist"] = add(hip, unit(p["lt"]), L["lt"])
        J["neckb"] = add(J["waist"], unit(p["ut"]), L["ut"])
        J["neckt"] = add(J["neckb"], unit(p["nk"]), L["nk"])
        J["headc"] = add(J["neckt"], unit(p["hd"]), HEAD_R * 0.62)
        J["crown"] = add(J["headc"], unit(p["hd"]), HEAD_R)
        # shoulders
        base_sh = lerp(J["waist"], J["neckb"], 0.9)
        if front:
            perp = unit(p["ut"] + 90)
            spread = 16.5 * p["sw"]
            J["sh1"] = add(base_sh, perp, -spread)
            J["sh2"] = add(base_sh, perp, spread)
            hp = unit(p["lt"] + 90)
            J["hip1"] = add(hip, hp, -9.5)
            J["hip2"] = add(hip, hp, 9.5)
        else:
            J["sh1"] = J["sh2"] = base_sh
            J["hip1"] = J["hip2"] = hip
        for s in "12":
            J[f"el{s}"] = add(J[f"sh{s}"], unit(p[f"ua{s}"]), L["ua"])
            J[f"wr{s}"] = add(J[f"el{s}"], unit(p[f"fa{s}"]), L["fa"])
            J[f"fi{s}"] = add(J[f"wr{s}"], unit(p[f"h{s}"]), L["h"])
            J[f"kn{s}"] = add(J[f"hip{s}"], unit(p[f"th{s}"]), L["th"])
            J[f"an{s}"] = add(J[f"kn{s}"], unit(p[f"sh{s}"]), L["sh"])
            fd = unit(p[f"ft{s}"])
            # sole side = away from the knee
            n1 = unit(p[f"ft{s}"] + 90)
            kv = (J[f"kn{s}"][0] - J[f"an{s}"][0], J[f"kn{s}"][1] - J[f"an{s}"][1])
            if n1[0] * kv[0] + n1[1] * kv[1] > 0:
                n1 = (-n1[0], -n1[1])
            if front and p.get(f"ftfront{s}", True) and abs(math.sin(math.radians(p[f"ft{s}"]))) > 0.9:
                pass
            base = add(J[f"an{s}"], n1, 3.2)
            J[f"heel{s}"] = add(base, fd, -L["heel"])
            J[f"toe{s}"] = add(base, fd, L["ft"])
        self.J = J

    # anchor on a segment: seg in (lt, ut, th1, sh1, ua1, fa1 ...), t in [0,1], side in ant/post/mid/lat
    def anchor(self, seg, t, side="mid", k=1.0):
        J, p = self.J, self.p
        segs = {
            "lt": ("hip", "waist", 11.5, 10.0, p["lt"], "trunk"),
            "ut": ("waist", "neckb", 10.0, 7.0, p["ut"], "trunk"),
            "nk": ("neckb", "neckt", 4.3, 4.3, p["nk"], "trunk"),
        }
        for s in "12":
            segs[f"th{s}"] = (f"hip{s}", f"kn{s}", R["th"][0], R["th"][1], p[f"th{s}"], "limb")
            segs[f"sh{s}"] = (f"kn{s}", f"an{s}", R["sh"][0], R["sh"][1], p[f"sh{s}"], "limb")
            segs[f"ua{s}"] = (f"sh{s}", f"el{s}", R["ua"][0], R["ua"][1], p[f"ua{s}"], "limb")
            segs[f"fa{s}"] = (f"el{s}", f"wr{s}", R["fa"][0], R["fa"][1], p[f"fa{s}"], "limb")
            segs[f"ft{s}"] = (f"heel{s}", f"toe{s}", R["ft"][0], R["ft"][1], p[f"ft{s}"], "limb")
        a, b, ra, rb, ang, typ = segs[seg]
        pt = lerp(J[a], J[b], t)
        r = ra + (rb - ra) * t
        if side == "mid":
            return pt
        ant = ang - 90 if typ == "limb" else ang + 90
        sign = 1 if side == "ant" else -1
        return add(pt, unit(ant), sign * r * 0.62 * k)

    # ------------------------------------------------------------------ drawing
    def torso_path(self):
        J, p = self.J, self.p
        front = p["view"] == "front"
        spine = catmull([add(J["hip"], unit(p["lt"]), -8), J["hip"], J["waist"], lerp(J["waist"], J["neckb"], .55), J["neckb"]], 7)
        # half-widths along the spine: (u, anterior, posterior); u = 0 bottom of pelvis, 1 = neck base
        if front:
            sw = max(.55, p["sw"])
            keys = [(0.0, 7, 7), (0.13, 14.5, 14.5), (0.27, 15.2, 15.2), (0.47, 12.4, 12.4),
                    (0.76, 15.2 * sw + 1.5, 15.2 * sw + 1.5), (0.9, 13 * sw + 1, 13 * sw + 1), (1.0, 5.4, 5.4)]
        else:
            keys = [(0.0, 4.0, 5.8), (0.12, 8.4, 11.0), (0.24, 9.2, 10.0), (0.46, 9.0, 7.4),
                    (0.72, 11.0, 8.4), (0.88, 8.4, 7.4), (1.0, 4.6, 4.8)]
        # arclength
        d = [0.0]
        for i in range(1, len(spine)):
            d.append(d[-1] + math.dist(spine[i], spine[i - 1]))
        tot = d[-1]
        left, right = [], []
        for i, pt in enumerate(spine):
            u = d[i] / tot
            for j in range(len(keys) - 1):
                if keys[j][0] <= u <= keys[j + 1][0]:
                    t = (u - keys[j][0]) / (keys[j + 1][0] - keys[j][0])
                    e = 0.5 - 0.5 * math.cos(math.pi * t)
                    wa = keys[j][1] + (keys[j + 1][1] - keys[j][1]) * e
                    wb = keys[j][2] + (keys[j + 1][2] - keys[j][2]) * e
                    break
            a = spine[max(0, i - 1)]
            b = spine[min(len(spine) - 1, i + 1)]
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            n = unit(ang + 90)
            left.append(add(pt, n, wa))
            right.append(add(pt, n, -wb))
        pts = left + right[::-1]
        dstr = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"
        return dstr

    def svg_parts(self, far=INK_FAR, near=INK, outline=PAPER, ow=1.3):
        J, p = self.J, self.p
        front = p["view"] == "front"
        parts = []

        def limb(a, b, key, col):
            ra, rb = R[key]
            parts.append(f'<path d="{capsule(J[a], J[b], ra, rb)}" fill="{col}" stroke="{outline}" stroke-width="{ow}"/>')

        def arm(s, col):
            limb(f"sh{s}", f"el{s}", "ua", col)
            limb(f"el{s}", f"wr{s}", "fa", col)
            limb(f"wr{s}", f"fi{s}", "h", col)

        def leg(s, col):
            limb(f"hip{s}", f"kn{s}", "th", col)
            limb(f"kn{s}", f"an{s}", "sh", col)
            parts.append(f'<path d="{capsule(J[f"heel{s}"], J[f"toe{s}"], R["ft"][0], R["ft"][1])}" fill="{col}" stroke="{outline}" stroke-width="{ow}"/>')
            limb(f"an{s}", f"an{s}", "ft", col) if False else None

        c_far = near if front else far
        order = p.get("order")
        torso = [f'<path d="{self.torso_path()}" fill="{near}" stroke="{outline}" stroke-width="{ow}" stroke-linejoin="round"/>',
                 f'<path d="{capsule(J["neckb"], J["neckt"], 4.6, 4.3)}" fill="{near}" stroke="{outline}" stroke-width="{ow}"/>']
        hd = unit(p["hd"])
        fc = unit(p["face"]) if p["face"] is not None else (0, 0)
        bun = add(add(J["headc"], hd, HEAD_R * 0.55), fc, -HEAD_R * 0.72)
        head = [f'<circle cx="{f(bun[0])}" cy="{f(bun[1])}" r="{f(HEAD_R*0.42)}" fill="{near}" stroke="{outline}" stroke-width="{ow}"/>'
                if p.get("bun", True) and p["face"] is not None else "",
                f'<ellipse cx="{f(J["headc"][0])}" cy="{f(J["headc"][1])}" rx="{f(HEAD_R)}" ry="{f(HEAD_R*1.1)}" '
                f'transform="rotate({f(p["hd"]+90)} {f(J["headc"][0])} {f(J["headc"][1])})" fill="{near}" stroke="{outline}" stroke-width="{ow}"/>']
        limbc = LIMB if near == INK else near
        c_far = limbc if front else far
        layers = {"farArm": lambda: arm("2", c_far), "farLeg": lambda: leg("2", c_far),
                  "nearArm": lambda: arm("1", limbc), "nearLeg": lambda: leg("1", limbc)}
        seq = order or (["farArm", "farLeg", "torso", "head", "nearLeg", "nearArm"])
        for item in seq:
            if item == "torso":
                parts.extend(torso)
            elif item == "head":
                parts.extend(head)
            else:
                layers[item]()
        return parts

    def points(self):
        pts = []
        rad = {"kn": 6, "an": 4, "el": 4.5, "wr": 3.2, "fi": 2.4, "toe": 2.5, "heel": 3.4, "sh": 6, "hip": 9}
        for k, v in self.J.items():
            r = next((rv for rk, rv in rad.items() if k.startswith(rk)), 0)
            pts += [(v[0] - r, v[1] - r), (v[0] + r, v[1] + r)]
        for tok in re.findall(r"(-?[\d.]+),(-?[\d.]+)", self.torso_path()):
            pts.append((float(tok[0]), float(tok[1])))
        c = self.J["headc"]
        pts += [(c[0] - HEAD_R - 2, c[1] - HEAD_R - 2), (c[0] + HEAD_R + 2, c[1] + HEAD_R + 2)]
        return pts


def muscle_path(a, b, w, bulge=0.5):
    """Spindle (lens) between two points, max half-width w."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1
    n = (-dy / d, dx / d)
    m1 = add(lerp(a, b, bulge), n, w * 1.5)
    m2 = add(lerp(a, b, bulge), n, -w * 1.5)
    return (f"M{f(a[0])},{f(a[1])} Q{f(m1[0])},{f(m1[1])} {f(b[0])},{f(b[1])} "
            f"Q{f(m2[0])},{f(m2[1])} {f(a[0])},{f(a[1])} Z")


def draw(pose, muscles=(), labels=(), props=(), floor=True, mat=True, pad=8, width=None,
         ground=None, arrows=(), scale_hint=None, extra=""):
    """Render a pose to an SVG string.

    muscles: list of (anchorA, anchorB, halfwidth, kind['stretch'|'active'], optional label)
             anchors are tuples passed to Figure.anchor, or ('J', jointname)
    labels:  list of (anchor, text, dx, dy)
    props:   list of ('block', x, y, w, h) etc. in figure coordinates relative to floor-adjusted frame
    """
    fig = Figure(pose)
    J = fig.J
    pts = fig.points()
    ys = [p[1] for p in pts]
    # translate so that the lowest body point sits on the floor (y = 0)
    low = max(ys) if ground is None else ground
    tx = 0
    parts = []
    shapes = fig.svg_parts()

    def resolve(a):
        if a[0] == "J":
            return J[a[1]]
        return fig.anchor(*a)

    musc = []
    for m in muscles:
        a, b, w, kind = m[:4]
        pa, pb = resolve(a), resolve(b)
        col = STRETCH if kind == "stretch" else ACTIVE
        musc.append(f'<path d="{muscle_path(pa, pb, w)}" fill="{col}" fill-opacity=".86" stroke="{PAPER}" stroke-width=".7"/>')
    lab = []
    for (anc, text, dx, dy) in labels:
        pa = resolve(anc)
        tx_, ty_ = pa[0] + dx, pa[1] + dy
        anchor = "start" if dx >= 0 else "end"
        lab.append(f'<line x1="{f(pa[0])}" y1="{f(pa[1])}" x2="{f(tx_ - (2 if dx >= 0 else -2))}" y2="{f(ty_ - 1.5)}" stroke="#5C3B24" stroke-width=".5"/>'
                   f'<circle cx="{f(pa[0])}" cy="{f(pa[1])}" r="1.1" fill="#5C3B24"/>'
                   f'<text x="{f(tx_)}" y="{f(ty_)}" font-family="Inter" font-size="6.2" fill="#3A2617" text-anchor="{anchor}">{text}</text>')
    prop_svg = []
    for pr in props:
        kind = pr[0]
        if kind == "block":
            _, x, y, w, h = pr
            prop_svg.append(f'<rect x="{f(x)}" y="{f(-y - h)}" width="{f(w)}" height="{f(h)}" rx="1.5" fill="#D9B98A" stroke="#A88458" stroke-width=".7"/>')
        elif kind == "blanket":
            _, x, y, w, h = pr
            prop_svg.append(f'<rect x="{f(x)}" y="{f(-y - h)}" width="{f(w)}" height="{f(h)}" rx="2" fill="#E7D3C4" stroke="#C2795C" stroke-width=".7"/>'
                            f'<line x1="{f(x+2)}" y1="{f(-y-h/2)}" x2="{f(x+w-2)}" y2="{f(-y-h/2)}" stroke="#C2795C" stroke-width=".4" stroke-dasharray="2 1.5"/>')
        elif kind == "bolster":
            _, x, y, w, h = pr
            prop_svg.append(f'<rect x="{f(x)}" y="{f(-y - h)}" width="{f(w)}" height="{f(h)}" rx="{f(h/2)}" fill="#C9CDB3" stroke="#8C906C" stroke-width=".7"/>')
        elif kind == "wall":
            _, x = pr
            prop_svg.append(f'<rect x="{f(x)}" y="-190" width="5" height="190" fill="#EDE5D6" stroke="#CDBFA5" stroke-width=".6"/>')
        elif kind == "strap":
            _, a, b = pr
            pa, pb = resolve(a), resolve(b)
            prop_svg.append(f'<line x1="{f(pa[0])}" y1="{f(pa[1]-low)}" x2="{f(pb[0])}" y2="{f(pb[1]-low)}" stroke="#B8914A" stroke-width="1.6" stroke-linecap="round"/>')
        elif kind == "chair":
            _, x, h = pr
            prop_svg.append(f'<path d="M{f(x)},0 V{f(-h)} H{f(x+34)} V0 M{f(x+30)},{f(-h)} V{f(-h-38)}" fill="none" stroke="#A88458" stroke-width="2.2" stroke-linecap="round"/>')
    arr = []
    for (a, b, txt) in arrows:
        pa, pb = resolve(a) if isinstance(a[0], str) else a, resolve(b) if isinstance(b[0], str) else b
        arr.append(f'<line x1="{f(pa[0])}" y1="{f(pa[1])}" x2="{f(pb[0])}" y2="{f(pb[1])}" stroke="#B8914A" stroke-width="1.1" marker-end="url(#ah)"/>')
        if txt:
            arr.append(f'<text x="{f(pb[0]+2)}" y="{f(pb[1]-2)}" font-family="Inter" font-size="6" fill="#8A6A2C">{txt}</text>')

    body = "".join(shapes) + "".join(musc)
    # bounding box
    xs = [p[0] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    for pr in props:
        if pr[0] in ("block", "blanket", "bolster"):
            minx = min(minx, pr[1]); maxx = max(maxx, pr[1] + pr[3])
            miny = min(miny, low - pr[2] - pr[4])
        if pr[0] == "wall":
            minx = min(minx, pr[1]); maxx = max(maxx, pr[1] + 5)
        if pr[0] == "chair":
            minx = min(minx, pr[1]); maxx = max(maxx, pr[1] + 34); miny = min(miny, low - pr[2] - 40)
    for (anc, text, dx, dy) in labels:
        pa = resolve(anc)
        tw = len(text) * 3.1
        x2 = pa[0] + dx
        if dx >= 0:
            maxx = max(maxx, x2 + tw)
        else:
            minx = min(minx, x2 - tw)
        miny = min(miny, pa[1] + dy - 7)
        maxy = max(maxy, pa[1] + dy + 2)
    if floor:
        maxy = max(maxy, low + 4)
    minx -= pad; maxx += pad; miny -= pad; maxy += pad * 0.6
    flip = fig.p.get("flip")
    W, H = maxx - minx, maxy - miny
    g_open = f'<g transform="translate(0,{f(-low)})">'
    if flip:
        g_open = f'<g transform="translate({f(minx+maxx)},{f(-low)}) scale(-1,1)">'
    floor_svg = ""
    if floor:
        floor_svg += f'<line x1="{f(minx+2)}" y1="0" x2="{f(maxx-2)}" y2="0" stroke="#CDBFA5" stroke-width=".8"/>'
        if mat:
            floor_svg += f'<rect x="{f(minx+6)}" y="-1.6" width="{f(W-12)}" height="1.9" rx=".9" fill="#8FA7A3" fill-opacity=".55"/>'
    vb = f"{f(minx)} {f(miny - low)} {f(W)} {f(H)}"
    defs = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#B8914A"/></marker></defs>')
    labtxt = "".join(lab)
    if flip:
        # labels are drawn unflipped: mirror their anchor x
        labtxt = ""
        for (anc, text, dx, dy) in labels:
            pa = resolve(anc)
            px = minx + maxx - pa[0]
            tx_, ty_ = px - dx, pa[1] + dy
            anchor = "end" if dx >= 0 else "start"
            labtxt += (f'<line x1="{f(px)}" y1="{f(pa[1])}" x2="{f(tx_ + (2 if dx >= 0 else -2))}" y2="{f(ty_ - 1.5)}" stroke="#5C3B24" stroke-width=".5"/>'
                       f'<circle cx="{f(px)}" cy="{f(pa[1])}" r="1.1" fill="#5C3B24"/>'
                       f'<text x="{f(tx_)}" y="{f(ty_)}" font-family="Inter" font-size="6.2" fill="#3A2617" text-anchor="{anchor}">{text}</text>')
        labtxt = f'<g transform="translate(0,{f(-low)})">{labtxt}</g>'
    else:
        labtxt = f'<g transform="translate(0,{f(-low)})">{labtxt}</g>'
    wattr = f' width="{width}"' if width else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{wattr}>{defs}{floor_svg}'
            f'<g>{"".join(prop_svg)}</g>{g_open}{body}{"".join(arr)}</g>{labtxt}{extra}</svg>')


def icon(pose, **kw):
    """Small sequence-chart icon: no labels, compact padding, fixed aspect."""
    return draw(pose, pad=6, **kw)


# ------------------------------------------------------------------ contact solver
RADIUS_AT = {"crown": 0, "headc": HEAD_R * 1.08, "el": 4.3, "wr": 3.0, "fi": 2.2, "toe": 2.4, "heel": 3.3,
             "kn": 5.8, "an": 3.6, "hip": 9.0, "waist": 10.0, "neckb": 8.0, "sh": 5.6}


_CACHE = None


def settle(pose, contacts, free, weight=0.02, iters=4000, pins=()):
    """Cached wrapper around _settle (results stored in data/pose_cache.json)."""
    import json, hashlib, pathlib
    global _CACHE
    path = pathlib.Path(__file__).parent / "data" / "pose_cache.json"
    if _CACHE is None:
        _CACHE = json.loads(path.read_text()) if path.exists() else {}
    key = hashlib.md5(json.dumps([pose, contacts, free, weight, list(pins)], sort_keys=True, default=str).encode()).hexdigest()
    if key not in _CACHE:
        _CACHE[key] = _settle(pose, contacts, free, weight, iters, pins)
        path.write_text(json.dumps(_CACHE))
    return _CACHE[key]


def _settle(pose, contacts, free, weight=0.02, iters=4000, pins=()):
    """Adjust the angles named in `free` so that every joint in `contacts` rests on one common floor.

    Keeps angles as close as possible to the starting values (Tikhonov weight)."""
    import numpy as np
    from scipy.optimize import minimize
    base = dict(DEFAULT); base.update(pose)
    x0 = np.array([float(base[k]) for k in free])

    def lowest(fig, name):
        r = next((rv for rk, rv in RADIUS_AT.items() if name.startswith(rk)), 0)
        return fig.J[name][1] + r

    def cost(x):
        p = dict(base); p.update({k: v for k, v in zip(free, x)})
        fig = Figure(p)
        ys = [lowest(fig, c) for c in contacts]
        F = max(ys) if ys else 0
        c = sum((F - y) ** 2 for y in ys) + weight * float(np.sum((x - x0) ** 2))
        for a, b, t in pins:  # joint a should sit at the point t of the way from joint b towards joint b2
            b1, b2 = b if isinstance(b, (list, tuple)) else (b, b)
            q = lerp(fig.J[b1], fig.J[b2], t)
            c += 2 * ((fig.J[a][0] - q[0]) ** 2 + (fig.J[a][1] - q[1]) ** 2)
        return c

    res = minimize(cost, x0, method="Nelder-Mead", options={"maxiter": iters, "xatol": 0.05, "fatol": 1e-4})
    out = dict(pose)
    out.update({k: round(float(v), 1) for k, v in zip(free, res.x)})
    return out


def ghost(svg_text):
    """Recolour a figure as a pale outline so that muscle overlays stand out."""
    s = svg_text.replace(f'fill="{INK}"', 'fill="#EFE7D6"').replace(f'fill="{LIMB}"', 'fill="#EFE7D6"')
    s = s.replace(f'fill="{INK_FAR}"', 'fill="#F6F1E6"')
    s = s.replace(f'stroke="{PAPER}" stroke-width="1.3"', 'stroke="#B9A67F" stroke-width=".55"')
    return s
