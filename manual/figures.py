"""
Figures for the manual.  Every figure is drawn in code as SVG so that labels are always
legible, colours match the book, and anatomy can be checked against the text.

Anatomical drawings are *schematic*: proportions are simplified for teaching and every
caption says so.  Nothing here is traced from a copyrighted source.
"""
import math

from posefig import draw, Figure, INK, STRETCH, ACTIVE, ghost
from poses import P

FIG = {}

C = dict(forest="#3F4A2E", forest2="#4B5236", sage="#8C906C", sagepale="#EEF0E4", gold="#B8914A",
         golddeep="#8A6A2C", goldpale="#F6EEDC", terra="#C2795C", clay="#A25A40", terrapale="#FBEDE6",
         teak="#5C3B24", ink="#2A271E", ink2="#4A463A", paper="#FFFEFA", bone="#F1E8D6", boneline="#9C8762",
         blue="#3D6475", bluepale="#E3EDF0", cart="#CFE0E3", disc="#D8E6E4", nerve="#E0B84F", line="#E4D8C4",
         lung="#F2D6CC", violet="#6B5B8E")


def reg(fid, svg, caption, cls=""):
    FIG[fid] = dict(svg=svg, caption=caption, cls=cls)


def get(fid):
    return FIG.get(fid)


def f(x):
    if isinstance(x, str):
        return x
    return f"{x:.1f}".rstrip("0").rstrip(".")


def svg(w, h, body, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" font-family="Inter">'
            f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["golddeep"]}"/></marker>'
            f'<marker id="arrb" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["blue"]}"/></marker>'
            f'<marker id="arrt" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["clay"]}"/></marker>{extra_defs}</defs>{body}</svg>')


def T(x, y, s, size=7, col=None, anchor="start", weight=400, italic=False, family=None, ls=0):
    col = col or C["ink"]
    fam = f' font-family="{family}"' if family else ""
    st = ' font-style="italic"' if italic else ""
    lsp = f' letter-spacing="{ls}"' if ls else ""
    lines = s.split("\n")
    if len(lines) == 1:
        return f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}"{fam}{st}{lsp}>{s}</text>'
    out = f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}"{fam}{st}{lsp}>'
    for i, ln in enumerate(lines):
        out += f'<tspan x="{f(x)}" dy="{0 if i == 0 else size * 1.22:.1f}">{ln}</tspan>'
    return out + "</text>"


def leader(x1, y1, x2, y2, col=None):
    col = col or C["teak"]
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{col}" stroke-width=".5"/>'
            f'<circle cx="{f(x1)}" cy="{f(y1)}" r="1.1" fill="{col}"/>')


def box(x, y, w, h, fill, stroke="none", rx=3, sw=.8):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def arrow(x1, y1, x2, y2, col=None, sw=1, m="arr", dash=""):
    col = col or C["golddeep"]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{col}" stroke-width="{sw}" marker-end="url(#{m})"{d}/>'


def curve_arrow(d, col=None, sw=1, m="arr"):
    col = col or C["golddeep"]
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" marker-end="url(#{m})"/>'


def embed(pose_svg, x, y, w):
    """Place a posefig SVG inside another SVG at (x,y) with width w."""
    import re
    vb = re.search(r'viewBox="([^"]+)"', pose_svg).group(1).split()
    vw, vh = float(vb[2]), float(vb[3])
    h = w * vh / vw
    inner = re.sub(r'^<svg[^>]*>', f'<svg x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" viewBox="{" ".join(vb)}">', pose_svg)
    return inner, h


# =====================================================================================
# SECTION I — philosophy and history
# =====================================================================================
def fig_timeline():
    W, H = 520, 250
    b = []
    x0, x1 = 30, 505
    # scale: nonlinear segments for readability
    segs = [(-2600, -1000, 0, .2), (-1000, 0, .2, .40), (0, 1000, .40, .58), (1000, 1800, .58, .70), (1800, 2030, .70, 1.0)]

    def X(yr):
        for a, bnd, u0, u1 in segs:
            if a <= yr <= bnd:
                return x0 + (x1 - x0) * (u0 + (u1 - u0) * (yr - a) / (bnd - a))
        return x1
    y = 118
    b.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{C["forest"]}" stroke-width="1.4"/>')
    for yr, lab in [(-2500, "2500 BCE"), (-1500, "1500"), (-1000, "1000"), (-500, "500 BCE"), (0, "1 CE"),
                    (500, "500"), (1000, "1000"), (1500, "1500"), (1800, "1800"), (1900, "1900"), (2000, "2000")]:
        xx = X(yr)
        b.append(f'<line x1="{f(xx)}" y1="{y-3}" x2="{f(xx)}" y2="{y+3}" stroke="{C["forest"]}" stroke-width=".8"/>')
        b.append(T(xx, y + 12, lab, 5.6, C["ink2"], "middle"))
    # era bands
    bands = [(-2600, -1900, "Indus (Harappan)\ncivilisation", C["bone"], 0),
             (-1500, -500, "Vedic period", C["goldpale"], 0),
             (-800, -200, "Early Upaniṣads", "#EDE4D0", 1),
             (-200, 400, "Epics & Gītā; Yoga Sūtra", C["sagepale"], 0),
             (500, 1300, "Tantric traditions", "#EFE7F2", 1),
             (1000, 1750, "Haṭha texts", "#F5E4DA", 0),
             (1850, 2030, "Modern yoga", C["bluepale"], 1)]
    for a, bnd, lab, col, row in bands:
        ya = 62 + row * 26
        b.append(box(X(a), ya, X(bnd) - X(a), 20, col, C["line"], 2, .5))
        b.append(T((X(a) + X(bnd)) / 2, ya + 8.5 if "\n" in lab else ya + 12.5, lab, 5.8, C["teak"], "middle", 600))
    # events below
    ev = [(-2000, "Seals sometimes read as\n“proto-yogic” — contested"),
          (-1200, "Ṛgveda composed\n(c. 1500–1200 BCE)"),
          (-600, "Bṛhadāraṇyaka &\nChāndogya Upaniṣads"),
          (-300, "Kaṭha Up.: first definition\nof yoga (2.3.11)"),
          (150, "Bhagavad Gītā within\nthe Mahābhārata"),
          (375, "Pātañjala Yogaśāstra\n(c. 325–425 CE, Maas)"),
          (1050, "Amṛtasiddhi\n(c. 11th c.)"),
          (1450, "Haṭha Yoga Pradīpikā\n(c. 15th c.)"),
          (1893, "Vivekananda,\nChicago 1893"),
          (1933, "Krishnamacharya teaches\nat Mysore palace"),
          (1966, "Iyengar, Light on\nYoga published"),
          (2015, "First International\nDay of Yoga")]
    for i, (yr, lab) in enumerate(ev):
        xx = X(yr)
        lvl = i % 3
        yy = 142 + lvl * 32
        b.append(f'<line x1="{f(xx)}" y1="{y+3}" x2="{f(xx)}" y2="{yy-7}" stroke="{C["gold"]}" stroke-width=".6" stroke-dasharray="1.5 1.2"/>')
        b.append(f'<circle cx="{f(xx)}" cy="{y}" r="2.2" fill="{C["gold"]}"/>')
        b.append(T(xx, yy, lab, 5.5, C["ink"], "middle"))
    b.append(T(x0, 22, "A TIMELINE OF YOGA", 7, C["golddeep"], "start", 700, ls=1.4))
    b.append(T(x0, 36, "Dates are approximate and scholarly estimates differ; the scale is compressed before 1000 CE.", 6, C["ink2"], italic=True))
    return svg(W, H, "".join(b))


reg("timeline", fig_timeline(),
    "Major phases in the history of yoga. Dates for early texts are scholarly estimates, not certainties "
    "[@samuel2008; @maas2013; @mallinson2017]. The Indus seals are listed because they are often cited, "
    "not because they are evidence of yoga practice.", "full")


def fig_eightlimbs():
    W, H = 420, 270
    names = [("Yama", "yama", "ethical restraints"), ("Niyama", "niyama", "personal observances"),
             ("Āsana", "āsana", "steady, comfortable seat"), ("Prāṇāyāma", "prāṇāyāma", "regulation of breath"),
             ("Pratyāhāra", "pratyāhāra", "withdrawal of the senses"), ("Dhāraṇā", "dhāraṇā", "concentration"),
             ("Dhyāna", "dhyāna", "meditation"), ("Samādhi", "samādhi", "absorption")]
    dev = ["यम", "नियम", "आसन", "प्राणायाम", "प्रत्याहार", "धारणा", "ध्यान", "समाधि"]
    b = []
    for i, (n, iast, meaning) in enumerate(names):
        y = 236 - i * 28
        w = 250 - i * 14
        x = 30 + (250 - w) / 2 + 40
        inner = i >= 5
        col = C["forest"] if inner else (C["sagepale"] if i < 2 else C["goldpale"])
        tc = "#FFF8EA" if inner else C["forest"]
        b.append(box(x, y - 17, w, 23, col, C["line"] if not inner else "none", 3, .6))
        b.append(T(x + 10, y - 2, f"{i+1}", 8, C["gold"] if inner else C["golddeep"], "start", 700))
        b.append(T(x + 24, y - 2, n, 9.5, tc, "start", 600, family="Cormorant"))
        b.append(T(x + w - 8, y - 2, meaning, 6.2, "#E9E2CF" if inner else C["ink2"], "end"))
    # brackets
    b.append(f'<path d="M352,240 h6 v-138 h-6" fill="none" stroke="{C["golddeep"]}" stroke-width=".8"/>')
    b.append(T(364, 176, "Bahiraṅga\n“outer” limbs\n(YS 2.29–3.1)", 6.4, C["golddeep"], "start", 600))
    b.append(f'<path d="M352,96 h6 v-78 h-6" fill="none" stroke="{C["forest"]}" stroke-width=".8"/>')
    b.append(T(364, 50, "Antaraṅga\n“inner” limbs\n= saṃyama\n(YS 3.4, 3.7)", 6.4, C["forest"], "start", 600))
    return svg(W, H, "".join(b))


reg("eightlimbs", fig_eightlimbs(),
    "The eight limbs (*aṣṭāṅga*) of Patañjali’s yoga (YS 2.29). Patañjali calls the last three “inner” relative to the first five (YS 3.7); "
    "practised together on one object they are called *saṃyama* (YS 3.4). The ladder image is a teaching device: the text "
    "presents the limbs as mutually supporting, not as strictly sequential stages.", "")


def fig_samkhya():
    W, H = 470, 300
    b = []

    def node(x, y, w, t1, t2, fill, tc=C["forest"], h=30):
        b.append(box(x - w / 2, y - h / 2, w, h, fill, C["line"], 4, .6))
        b.append(T(x, y - 2, t1, 8.8, tc, "middle", 600, family="Cormorant"))
        b.append(T(x, y + 9, t2, 5.8, C["ink2"] if tc == C["forest"] else "#E9E2CF", "middle"))

    def ln(x1, y1, x2, y2):
        b.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{C["sage"]}" stroke-width=".9"/>')
    node(110, 30, 150, "Puruṣa", "pure consciousness · the witness · (1)", C["forest"], "#FFF8EA")
    node(330, 30, 170, "Prakṛti", "unmanifest matter · three guṇas · (2)", C["goldpale"])
    ln(330, 45, 330, 66)
    node(330, 82, 170, "Mahat / Buddhi", "intellect · discernment · (3)", "#FFF")
    ln(330, 97, 330, 118)
    node(330, 134, 170, "Ahaṃkāra", "“I-maker” · sense of ownership · (4)", "#FFF")
    ln(330, 149, 330, 162); ln(150, 162, 420, 162)
    for x in (110, 235, 360):
        ln(x if x != 110 else 150, 162, x, 180)
    ln(420, 162, 420, 180)
    node(110, 196, 100, "Manas", "mind · (5)", C["sagepale"])
    node(220, 196, 110, "5 Jñānendriya", "organs of perception (6–10)", C["sagepale"])
    node(345, 196, 110, "5 Karmendriya", "organs of action (11–15)", C["sagepale"])
    b.append(box(38, 222, 390, 0.1, C["line"]))
    ln(420, 180, 440, 180)
    node(233, 250, 170, "5 Tanmātra", "subtle elements: sound, touch, form, taste, smell (16–20)", "#F7F0E4")
    node(233, 286, 170, "5 Mahābhūta", "space, air, fire, water, earth (21–25)", "#F2E6D3")
    ln(440, 180, 440, 250); ln(440, 250, 318, 250)
    ln(233, 265, 233, 271)
    b.append(T(110, 60, "Puruṣa does not evolve;\nit only witnesses.", 6, C["ink2"], "middle", italic=True))
    b.append(T(40, 262, "sattva-dominant side\n(top row) · tamas-\ndominant side (right)", 5.6, C["ink2"], "start", italic=True))
    return svg(W, H + 6, "".join(b))


reg("samkhya", fig_samkhya(),
    "The twenty-five *tattva*s of classical Sāṃkhya, the philosophical background of Patañjali’s Yoga, following the *Sāṃkhyakārikā* "
    "(c. 4th–5th century CE) [@larson1979]. The diagram is a map of categories, not of physical anatomy.", "")


def fig_kleshas():
    W, H = 420, 170
    b = []
    b.append(box(20, 118, 380, 36, C["forest"], "none", 4))
    b.append(T(210, 134, "Avidyā — misapprehension (YS 2.4–2.5)", 9, "#FFF8EA", "middle", 600, family="Cormorant"))
    b.append(T(210, 146, "the “field” in which the other four grow: taking the impermanent, impure, painful and non-self for their opposites", 5.8, "#E9E2CF", "middle"))
    items = [("Asmitā", "I-am-ness: identifying the seer\nwith the instrument of seeing (2.6)"),
             ("Rāga", "attachment that follows\npleasure (2.7)"),
             ("Dveṣa", "aversion that follows\npain (2.8)"),
             ("Abhiniveśa", "clinging to life; fear of\ndeath, even in the wise (2.9)")]
    for i, (n, d) in enumerate(items):
        x = 20 + i * 97
        b.append(f'<path d="M{x+46},{118} C{x+46},{104} {x+46},{100} {x+46},{88}" stroke="{C["sage"]}" stroke-width="1.2" fill="none"/>')
        b.append(box(x, 30, 92, 58, C["goldpale"], C["line"], 4, .6))
        b.append(T(x + 46, 48, n, 10, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(x + 46, 62, d, 5.6, C["ink2"], "middle"))
    b.append(T(20, 16, "THE FIVE KLEŚAS (AFFLICTIONS) · YOGA SŪTRA 2.3–2.9", 6.6, C["golddeep"], "start", 700, ls=1.1))
    return svg(W, H, "".join(b))


reg("kleshas", fig_kleshas(), "The five *kleśa*s in the Yoga Sūtra. Patañjali describes them as the root of the causes of suffering; "
    "*kriyā yoga* (2.1–2.2) is offered to weaken them [@bryant2009].")


def fig_fourpaths():
    W, H = 360, 260
    cx, cy = 180, 132
    b = []
    b.append(f'<circle cx="{cx}" cy="{cy}" r="44" fill="{C["forest"]}"/>')
    b.append(T(cx, cy - 4, "Yoga of", 7, "#E9E2CF", "middle"))
    b.append(T(cx, cy + 9, "Synthesis", 12, "#FFF8EA", "middle", 600, family="Cormorant"))
    paths = [("Karma Yoga", "action · hands", "selfless service", 0, -1),
             ("Bhakti Yoga", "emotion · heart", "devotion", 1, 0),
             ("Jñāna Yoga", "intellect · head", "enquiry, discrimination", 0, 1),
             ("Rāja Yoga", "will · mind", "meditation, mental control", -1, 0)]
    for n, sub, what, dx, dy in paths:
        x, y = cx + dx * 118, cy + dy * 92
        b.append(f'<line x1="{f(cx+dx*44)}" y1="{f(cy+dy*44)}" x2="{f(x-dx*48)}" y2="{f(y-dy*22)}" stroke="{C["gold"]}" stroke-width="1"/>')
        b.append(box(x - 60, y - 22, 120, 44, C["goldpale"], C["gold"], 5, .6))
        b.append(T(x, y - 5, n, 11, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(x, y + 6, sub, 6, C["golddeep"], "middle", 600))
        b.append(T(x, y + 15, what, 5.8, C["ink2"], "middle"))
    return svg(W, H, "".join(b))


reg("fourpaths", fig_fourpaths(), "Integrating the four classical paths: they are practised together so that "
    "head, heart, hands and will develop in balance. The associations with faculties are a traditional teaching aid.")


def fig_koshas():
    W, H = 400, 250
    b = []
    cx, cy = 140, 125
    layers = [("Annamaya", "food sheath · physical body", "#EFE3CF"),
              ("Prāṇamaya", "vital sheath · breath, energy", "#E6E8D5"),
              ("Manomaya", "mental sheath · mind, emotion, senses", "#DCE3D6"),
              ("Vijñānamaya", "sheath of discernment · intellect", "#CCD7CC"),
              ("Ānandamaya", "sheath of bliss", "#B7C5B5")]
    for i, (n, d, col) in enumerate(layers):
        rx, ry = 118 - i * 21, 110 - i * 19
        b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" stroke="#FFFEFA" stroke-width="1.4"/>')
        ly = cy - ry + 9
        b.append(leader(cx + 4, ly, 272, 30 + i * 36))
        b.append(T(276, 32 + i * 36, n + "maya kośa".replace("maya", "") if False else n + " kośa", 10, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(276, 42 + i * 36, d, 6, C["ink2"]))
    b.append(f'<circle cx="{cx}" cy="{cy+8}" r="15" fill="{C["gold"]}"/>')
    b.append(T(cx, cy + 11, "Ātman", 8.5, "#FFF8EA", "middle", 600, family="Cormorant"))
    b.append(T(276, 220, "Ātman, the Self, is not a sixth layer:\nVedānta teaches it is what the sheaths\nare mistaken for (Taittirīya Up. 2.1–2.5).", 6, C["ink2"], italic=True))
    return svg(W, H, "".join(b))


reg("koshas", fig_koshas(), "The five sheaths (*pañca-kośa*) of the *Taittirīya Upaniṣad* [@olivelle1996]. The model is a map for "
    "self-enquiry and for teaching; it describes levels of experience, not anatomical structures.")


def seated_outline(x, y, w):
    """A front-view meditating figure in soft outline for subtle-body diagrams."""
    s = draw(P["meditation_front"], floor=False, mat=False)
    s = s.replace('fill="#4E5A3A"', 'fill="#E9E1CF"').replace('fill="#5B6845"', 'fill="#E9E1CF"')
    s = s.replace('stroke="#FFFEFA"', 'stroke="#FFFEFA"')
    return embed(s, x, y, w)


def fig_chakras():
    W, H = 470, 330
    b = []
    fig_svg, h = seated_outline(120, 20, 200)
    b.append(fig_svg)
    # figure coordinates: compute from pose
    fig = Figure(P["meditation_front"])
    J = fig.J
    import re
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', draw(P["meditation_front"], floor=False, mat=False)).group(1).split()]
    sc = 200 / vb[2]

    def M(pt):
        return (120 + (pt[0] - vb[0]) * sc, 20 + (pt[1] - vb[1]) * sc)
    spine = [M(J["hip"]), M(J["waist"]), M(J["neckb"]), M(J["headc"])]
    base = M((0, 8))
    navel = M((0, -14))
    heart = M((0, -36))
    throat = M((0, -54))
    brow = M((J["headc"][0], J["headc"][1] - 1))
    crown = M((J["crown"][0], J["crown"][1] - 1))
    # nadis: ida and pingala spiralling around sushumna
    sx = base[0]
    top = brow[1]
    bot = base[1]
    pts_i, pts_p = [], []
    n = 60
    for k in range(n + 1):
        t = k / n
        yy = bot + (top - bot) * t
        amp = 13 * math.sin(math.pi * t) ** 0.6
        ph = t * 5 * math.pi
        pts_i.append((sx - amp * math.cos(ph), yy))
        pts_p.append((sx + amp * math.cos(ph), yy))
    b.append(f'<line x1="{f(sx)}" y1="{f(bot)}" x2="{f(sx)}" y2="{f(crown[1])}" stroke="{C["gold"]}" stroke-width="2.4" stroke-linecap="round"/>')
    b.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts_i) + f'" fill="none" stroke="{C["blue"]}" stroke-width="1.1"/>')
    b.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts_p) + f'" fill="none" stroke="{C["terra"]}" stroke-width="1.1"/>')
    ch = [("Sahasrāra", "crown · “thousand-petalled”", crown, "#9C7BB0"),
          ("Ājñā", "between the eyebrows · 2 petals", brow, "#6F6AA8"),
          ("Viśuddha", "throat · 16 petals · space", throat, "#4F8BB0"),
          ("Anāhata", "heart · 12 petals · air", heart, "#6E9A5B"),
          ("Maṇipūra", "navel · 10 petals · fire", navel, "#D9A93E"),
          ("Svādhiṣṭhāna", "sacral · 6 petals · water", M((0, 0)), "#D98A4E"),
          ("Mūlādhāra", "base of spine · 4 petals · earth", base, "#B8574A")]
    for i, (n_, d, pt, col) in enumerate(ch):
        b.append(f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="5.2" fill="{col}" stroke="#FFFEFA" stroke-width="1.2"/>')
        ty = 36 + i * 40
        b.append(f'<line x1="{f(pt[0]+6)}" y1="{f(pt[1])}" x2="{338}" y2="{f(ty-3)}" stroke="{C["line"]}" stroke-width=".6"/>')
        b.append(T(342, ty, n_, 10, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(342, ty + 10, d, 6, C["ink2"]))
    # nadi legend
    b.append(T(20, 40, "Nāḍīs", 10, C["forest"], "start", 600, family="Cormorant"))
    b.append(f'<line x1="20" y1="54" x2="36" y2="54" stroke="{C["gold"]}" stroke-width="2.4"/>' + T(40, 56, "Suṣumṇā · central channel", 6))
    b.append(f'<line x1="20" y1="66" x2="36" y2="66" stroke="{C["blue"]}" stroke-width="1.2"/>' + T(40, 68, "Iḍā · “lunar”, left nostril", 6))
    b.append(f'<line x1="20" y1="78" x2="36" y2="78" stroke="{C["terra"]}" stroke-width="1.2"/>' + T(40, 80, "Piṅgalā · “solar”, right nostril", 6))
    b.append(T(20, 100, "The crossing, spiral\nform is a common\nmodern rendering;\nmany texts simply\nplace iḍā and\npiṅgalā to the left\nand right of the\ncentral channel.", 5.8, C["ink2"], italic=True))
    return svg(W, H, "".join(b))


reg("chakras", fig_chakras(),
    "The six *cakra*s and *sahasrāra* as commonly taught in modern yoga, following the arrangement of the 16th-century "
    "*Ṣaṭcakranirūpaṇa* [@avalon1919]. Earlier texts describe different numbers and placements of cakras [@mallinson2017]. "
    "This is a map of traditional meditative experience; no anatomical structures corresponding to cakras or nāḍīs have been identified.", "")


def fig_vayus():
    W, H = 440, 300
    b = []
    fig_svg, h = seated_outline(110, 18, 200)
    b.append(fig_svg)
    regions = [("Udāna", "throat & head · upward movement;\nspeech, effort, “rising” at death", 172, 60, 30, 26, "#4F8BB0"),
               ("Prāṇa", "chest · inward movement;\nbreathing in, taking in", 172, 112, 36, 26, "#6E9A5B"),
               ("Samāna", "navel region · balancing, “equalising”;\ndigestion and assimilation", 172, 158, 36, 18, "#D9A93E"),
               ("Apāna", "pelvis · downward & outward;\nelimination, exhalation, birth", 172, 196, 40, 20, "#B8574A")]
    ys = [40, 96, 152, 208]
    for (n, d, cx, cy, rx, ry, col), ty in zip(regions, ys):
        b.append(f'<ellipse cx="{cx+38}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" fill-opacity=".28" stroke="{col}" stroke-width=".8"/>')
        b.append(f'<line x1="{cx+38+rx}" y1="{cy}" x2="318" y2="{ty-3}" stroke="{C["line"]}" stroke-width=".6"/>')
        b.append(T(322, ty, n, 11, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(322, ty + 10, d, 5.9, C["ink2"]))
    b.append(T(322, 262, "Vyāna", 11, C["forest"], "start", 600, family="Cormorant"))
    b.append(T(322, 272, "pervades the whole body; circulation,\nco-ordination, outward distribution", 5.9, C["ink2"]))
    b.append(f'<rect x="120" y="22" width="180" height="258" rx="30" fill="none" stroke="#9C7BB0" stroke-width=".8" stroke-dasharray="3 2"/>')
    b.append(arrow(210, 70, 210, 50, "#4F8BB0", 1))
    b.append(arrow(200, 104, 206, 116, "#6E9A5B", 1))
    b.append(arrow(210, 200, 210, 218, "#B8574A", 1))
    return svg(W, H, "".join(b))


reg("vayus", fig_vayus(), "The five *vāyu*s (“winds”) of *prāṇa* as usually taught. Texts disagree on their exact seats and functions; "
    "the dashed outline stands for *vyāna*, which pervades the whole body. These are traditional categories of experience, "
    "not physiological systems.")


def fig_bandhas():
    W, H = 420, 250
    b = []
    s = draw(P["sukhasana_side"], floor=True, mat=True)
    s = s.replace('fill="#4E5A3A"', 'fill="#E4DBC6"').replace('fill="#5B6845"', 'fill="#E4DBC6"').replace('fill="#A7AC8C"', 'fill="#EFE9DA"')
    inner, h = embed(s, 70, 20, 170)
    b.append(inner)
    import re
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    sc = 170 / vb[2]
    fig = Figure(P["sukhasana_side"])
    J = fig.J
    # the svg translated body by -low; replicate: low = max y of points
    low = max(p[1] for p in fig.points())

    def M(pt):
        return (70 + (pt[0] - vb[0]) * sc, 20 + (pt[1] - low - vb[1]) * sc)
    jal = M(J["neckt"])
    udd = M((J["waist"][0] + 6, J["waist"][1] + 2))
    mul = M((J["hip"][0] + 2, J["hip"][1] + 7))
    items = [("Jālandhara bandha", "chin lock: chin drawn towards the\nsternum, back of neck lengthened", jal, 40),
             ("Uḍḍīyāna bandha", "abdominal lock: after exhalation, the\nabdomen is drawn in and up", udd, 108),
             ("Mūla bandha", "root lock: gentle contraction and lift\nof the pelvic floor / perineum", mul, 176)]
    for n, d, pt, ty in items:
        b.append(f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="7" fill="{C["gold"]}" fill-opacity=".35" stroke="{C["golddeep"]}" stroke-width="1"/>')
        b.append(f'<line x1="{f(pt[0]+7)}" y1="{f(pt[1])}" x2="262" y2="{ty-3}" stroke="{C["golddeep"]}" stroke-width=".5"/>')
        b.append(T(266, ty, n, 10.5, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(266, ty + 10, d, 5.9, C["ink2"]))
    b.append(T(266, 232, "Mahā bandha = all three held together\n(Haṭha Yoga Pradīpikā 3.19–25)", 5.9, C["golddeep"], italic=True))
    return svg(W, H, "".join(b))


reg("bandhas", fig_bandhas(), "The three principal *bandha*s shown on a seated practitioner (schematic). Uḍḍīyāna bandha is practised only on an empty stomach and "
    "after exhalation; see the safety notes that follow.")


def fig_om():
    W, H = 420, 150
    b = []
    parts = [("A", "Vaiśvānara", "waking state", "outward-knowing"),
             ("U", "Taijasa", "dreaming state", "inward-knowing"),
             ("M", "Prājña", "deep sleep", "a mass of knowing"),
             ("—", "Turīya", "“the fourth”", "silence; the Self itself")]
    for i, (l, n, st, d) in enumerate(parts):
        x = 20 + i * 100
        fill = C["forest"] if i == 3 else C["goldpale"]
        tc = "#FFF8EA" if i == 3 else C["forest"]
        b.append(box(x, 34, 90, 96, fill, C["line"], 5, .6))
        b.append(T(x + 45, 70, l, 26, C["gold"], "middle", 500, family="Cormorant"))
        b.append(T(x + 45, 92, n, 10, tc, "middle", 600, family="Cormorant"))
        b.append(T(x + 45, 104, st, 6.2, C["golddeep"] if i < 3 else "#E2C27F", "middle", 600))
        b.append(T(x + 45, 116, d, 5.8, C["ink2"] if i < 3 else "#E9E2CF", "middle"))
    b.append(T(20, 20, "THE FOUR QUARTERS OF OṀ · MĀṆḌŪKYA UPANIṢAD 3–12", 6.6, C["golddeep"], "start", 700, ls=1.1))
    return svg(W, H, "".join(b))


reg("om", fig_om(), "The Māṇḍūkya Upaniṣad maps the three sounds of AUM onto waking, dreaming and deep sleep, and the silence that follows onto *turīya* [@olivelle1996].")


def fig_gunas():
    W, H = 360, 200
    b = []
    pts = [(180, 30), (60, 175), (300, 175)]
    b.append(f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{C["goldpale"]}" stroke="{C["gold"]}" stroke-width="1"/>')
    lab = [("Sattva", "clarity · light · balance", 180, 22, "middle"),
           ("Rajas", "activity · passion · restlessness", 52, 190, "start"),
           ("Tamas", "inertia · heaviness · dullness", 308, 190, "end")]
    for n, d, x, y, a in lab:
        b.append(T(x, y - (12 if y < 50 else -2), n, 11, C["forest"], a, 600, family="Cormorant"))
        b.append(T(x, y + (0 if y < 50 else 10) , d, 6, C["ink2"], a))
    b.append(T(180, 120, "every experience is a\nmixture of the three guṇas\n(Bhagavad Gītā 14.5–18)", 6.4, C["teak"], "middle", italic=True))
    return svg(W, H + 12, "".join(b))


reg("gunas", fig_gunas(), "The three *guṇa*s of Sāṃkhya and the Bhagavad Gītā. Yogic practice aims to strengthen *sattva*, while the "
    "Gītā ultimately points beyond all three (14.19–26).")


# =====================================================================================
# SECTION II — anatomy
# =====================================================================================
def fig_planes():
    W, H = 470, 250
    b = []
    s = draw(P["tadasana"] | dict(view="front", face=None, ua1=100, fa1=100, h1=100, ua2=80, fa2=80, h2=80), floor=False, mat=False)
    inner, h = embed(s, 45, 26, 60)
    b.append(inner)
    s2 = draw(P["tadasana"], floor=False, mat=False)
    inner2, _ = embed(s2, 190, 26, 35)
    # planes around a front figure (oblique projection)
    cx, top, bot = 75, 20, 220
    b.append(f'<polygon points="{cx},{top} {cx+22},{top-12} {cx+22},{bot-12} {cx},{bot}" fill="{C["terra"]}" fill-opacity=".20" stroke="{C["terra"]}" stroke-width=".7"/>')
    b.append(f'<polygon points="{cx-46},{top+6} {cx+46},{top+6} {cx+46},{bot+6} {cx-46},{bot+6}" fill="{C["blue"]}" fill-opacity=".10" stroke="{C["blue"]}" stroke-width=".7"/>')
    b.append(f'<polygon points="{cx-52},{125} {cx+40},{125} {cx+62},{113} {cx-30},{113}" fill="{C["gold"]}" fill-opacity=".30" stroke="{C["golddeep"]}" stroke-width=".7"/>')
    rows = [("Sagittal plane", "divides left from right; flexion and extension\n(e.g. forward bends, backbends)", C["terra"]),
            ("Frontal (coronal) plane", "divides front from back; abduction, adduction,\nlateral flexion (e.g. triangle, side bends)", C["blue"]),
            ("Transverse (horizontal) plane", "divides upper from lower; rotation\n(e.g. twists, hip rotation)", C["golddeep"])]
    for i, (n, d, col) in enumerate(rows):
        y = 46 + i * 58
        b.append(box(170, y - 12, 8, 30, col, "none", 1))
        b.append(T(186, y, n, 10.5, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(186, y + 11, d, 6.2, C["ink2"]))
    b.append(T(186, 220, "Axes: a movement in a plane turns about the axis perpendicular to it —\nsagittal plane ↔ mediolateral axis · frontal plane ↔ anteroposterior axis ·\ntransverse plane ↔ longitudinal (vertical) axis.", 6.2, C["teak"]))
    return svg(W, H, "".join(b))


reg("planes", fig_planes(), "Anatomical position (standing, facing forward, palms forward) with the three cardinal planes. Real yoga movements usually "
    "combine planes; the planes are a vocabulary for describing them [@neumann2017].")


def fig_directions():
    W, H = 440, 250
    b = []
    s = draw(P["tadasana"] | dict(view="front", face=None, ua1=100, fa1=100, h1=100, ua2=80, fa2=80, h2=80), floor=False, mat=False)
    inner, h = embed(s, 60, 16, 70)
    b.append(inner)
    s2 = draw(P["tadasana"], floor=False, mat=False)
    inner2, h2 = embed(s2, 270, 16, 34)
    b.append(inner2)
    b.append(arrow(40, 120, 40, 30, C["golddeep"]) + arrow(40, 130, 40, 220, C["golddeep"]))
    b.append(T(36, 26, "Superior (cranial)", 6.3, C["ink"], "start", 600) + T(36, 234, "Inferior (caudal)", 6.3, C["ink"], "start", 600))
    b.append(arrow(95, 90, 138, 90, C["blue"]) + arrow(95, 90, 102, 90, C["blue"]))
    b.append(T(142, 92, "Lateral", 6.3, C["blue"], "start", 600) + T(95, 84, "Medial", 6.3, C["blue"], "middle", 600))
    b.append(arrow(124, 135, 134, 170, C["clay"], m="arrt"))
    b.append(T(138, 150, "Proximal → distal\n(towards the\nextremity)", 6, C["clay"], "start", 600))
    b.append(arrow(300, 110, 340, 110, C["golddeep"]) + arrow(282, 110, 250, 110, C["golddeep"]))
    b.append(T(344, 112, "Anterior (ventral)", 6.3, C["ink"], "start", 600) + T(246, 112, "Posterior\n(dorsal)", 6.3, C["ink"], "end", 600))
    b.append(T(350, 170, "Superficial ↔ deep:\ncloser to / further\nfrom the surface", 6, C["teak"], italic=True))
    b.append(T(350, 210, "Ipsilateral = same side\nContralateral = opposite side", 6, C["teak"], italic=True))
    return svg(W, H, "".join(b))


reg("directions", fig_directions(), "Directional terms are always relative to anatomical position, even when the body is upside down: in headstand the head is still *superior* to the feet.")


def joint_panel(label, pose_a, pose_b, note):
    return label, pose_a, pose_b, note


def fig_jointmoves():
    W, H = 500, 330
    b = []
    base = P["tadasana"]
    fr = dict(view="front", face=None, ua1=100, fa1=100, h1=100, ua2=80, fa2=80, h2=80)
    panels = [
        ("Hip flexion / extension", [base | dict(th1=20, sh1=90, ft1=0, ua1=90), base | dict(th1=120, sh1=120, ft1=30)], "sagittal"),
        ("Shoulder flexion / extension", [base | dict(ua1=-70, fa1=-70, h1=-70), base | dict(ua1=130, fa1=130, h1=130)], "sagittal"),
        ("Spinal flexion / extension", [base | dict(ut=-40, nk=-10, hd=0, face=60), base | dict(lt=-95, ut=-118, nk=-130, hd=-135, face=-40)], "sagittal"),
        ("Hip abduction / adduction", [base | fr | dict(th1=130, sh1=130), base | fr | dict(th1=78, sh1=78, th2=90)], "frontal"),
        ("Shoulder abduction", [base | fr | dict(ua1=180, fa1=180, h1=180, ua2=0, fa2=0, h2=0), base | fr | dict(ua1=-100, fa1=-100, h1=-100, ua2=-80, fa2=-80, h2=-80)], "frontal"),
        ("Spinal lateral flexion", [base | fr | dict(ut=-60, nk=-55, hd=-55), base | fr | dict(ut=-120, nk=-125, hd=-125)], "frontal"),
    ]
    for i, (lab, poses, plane) in enumerate(panels):
        col = i % 3
        row = i // 3
        x = 14 + col * 162
        y = 20 + row * 150
        b.append(box(x, y, 152, 138, "#FBF7EF", C["line"], 4, .5))
        b.append(T(x + 8, y + 14, lab, 9.4, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(x + 144, y + 14, plane + " plane", 5.6, C["terra"] if plane == "sagittal" else C["blue"], "end", 600))
        for k, ps in enumerate(poses):
            s = draw(ps, floor=False, mat=False)
            inner, h = embed(s, 0, 0, 1)
            import re
            vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
            scale = min(62 / vb[2], 104 / vb[3])
            wv = vb[2] * scale
            inner, h = embed(s, x + 10 + k * 72 + (62 - wv) / 2, y + 24 + (104 - vb[3] * scale), wv)
            b.append(inner)
    b.append(T(14, 324, "Rotation (internal/external, spinal rotation) occurs in the transverse plane and is shown in the twist and hip-rotation figures later in this section.", 6, C["ink2"], italic=True))
    return svg(W, H + 4, "".join(b))


reg("jointmoves", fig_jointmoves(), "Basic joint movements illustrated with the manual’s figure. In each panel the left figure shows the first-named movement.", "full")


def vertebra_shape(cx, cy, w, h, ang, kind):
    """Lateral view of one vertebra: body (anterior, right) and spinous process (posterior, left)."""
    r = math.radians(ang)
    ca, sa = math.cos(r), math.sin(r)

    def P_(x, y):  # local -> global (x right/anterior, y down)
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    body = [P_(-w / 2, -h / 2), P_(w / 2, -h / 2), P_(w / 2, h / 2), P_(-w / 2, h / 2)]
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in body) + " Z"
    out = f'<path d="{d}" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".7" stroke-linejoin="round"/>'
    # posterior elements
    if kind == "C":
        sp = [P_(-w / 2, -h * .2), P_(-w / 2 - 10, h * .05), P_(-w / 2 - 14, h * .45), P_(-w / 2 - 10, h * .55), P_(-w / 2, h * .3)]
    elif kind == "C7":
        sp = [P_(-w / 2, -h * .2), P_(-w / 2 - 14, 0), P_(-w / 2 - 22, h * .6), P_(-w / 2 - 17, h * .75), P_(-w / 2, h * .35)]
    elif kind == "T":
        sp = [P_(-w / 2, -h * .3), P_(-w / 2 - 12, -h * .1), P_(-w / 2 - 20, h * 1.1), P_(-w / 2 - 16, h * 1.2), P_(-w / 2, h * .3)]
    else:  # lumbar: short, square, horizontal
        sp = [P_(-w / 2, -h * .32), P_(-w / 2 - 10, -h * .3), P_(-w / 2 - 20, -h * .2), P_(-w / 2 - 20, h * .28), P_(-w / 2 - 10, h * .3), P_(-w / 2, h * .25)]
    d2 = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in sp) + " Z"
    out = f'<path d="{d2}" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".7" stroke-linejoin="round"/>' + out
    return out


def fig_spine():
    W, H = 380, 468
    b = []
    # control points of the vertebral-body centreline (x = anterior to the right)
    ctrl = [(170, 22), (178, 60), (168, 100), (148, 150), (140, 205), (148, 262), (168, 312), (174, 352), (166, 385), (150, 410), (140, 440)]

    def cm(pts, n=40):
        out = []
        P2 = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(P2) - 2):
            p0, p1, p2, p3 = P2[i - 1], P2[i], P2[i + 1], P2[i + 2]
            for k in range(n):
                t = k / n
                out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                        + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
        out.append(pts[-1])
        return out
    line = cm(ctrl)
    L = [0]
    for i in range(1, len(line)):
        L.append(L[-1] + math.dist(line[i], line[i - 1]))
    tot = L[-1]

    def at(s):
        for i in range(1, len(L)):
            if L[i] >= s:
                t = (s - L[i - 1]) / (L[i] - L[i - 1] or 1)
                p = (line[i - 1][0] + (line[i][0] - line[i - 1][0]) * t, line[i - 1][1] + (line[i][1] - line[i - 1][1]) * t)
                a = math.degrees(math.atan2(line[i][1] - line[i - 1][1], line[i][0] - line[i - 1][0]))
                return p, a
        return line[-1], 90
    need = 7 * (7.5 + 3.2) + sum(9.5 + i * 1.2 + 3.4 for i in range(12)) + sum(13.5 + i * .4 + 6.5 for i in range(5))
    k = (tot - 90) / need
    verts = [("C", 7, 7.5 * k, 18, 3.2 * k)] + [("T", 12, 9.5 * k, 22, 3.4 * k)] + [("L", 5, 13.5 * k, 30, 6.5 * k)]
    s = 4
    regions = {}
    for kind, n, h, w, disc in verts:
        start = s
        for i in range(n):
            hh = h + (i * (1.2 if kind == "T" else 0.4)) * k
            (p, a) = at(s + hh / 2)
            vk = kind if not (kind == "C" and i == 6) else "C7"
            rot = a - 90
            b.append(vertebra_shape(p[0], p[1], w + (i * .6 if kind != "C" else 0), hh, rot, vk))
            s += hh
            if not (kind == "L" and i == n - 1):
                (pd, ad) = at(s + disc / 2)
                r = math.radians(ad - 90)
                ww = w + 1
                corners = [(-ww / 2, -disc / 2), (ww / 2, -disc / 2), (ww / 2, disc / 2), (-ww / 2, disc / 2)]
                pts = [(pd[0] + x * math.cos(r) - y * math.sin(r), pd[1] + x * math.sin(r) + y * math.cos(r)) for x, y in corners]
                b.append('<path d="M' + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + f' Z" fill="{C["disc"]}" stroke="#9FBAB6" stroke-width=".5"/>')
            s += disc
        regions[kind] = (start, s)
    # sacrum & coccyx
    (p0, a0) = at(s + 2)
    sac = (f'M{f(p0[0]+14)},{f(p0[1]-4)} C{f(p0[0]+20)},{f(p0[1]+20)} {f(p0[0]+6)},{f(p0[1]+52)} {f(p0[0]-10)},{f(p0[1]+66)} '
           f'L{f(p0[0]-18)},{f(p0[1]+62)} C{f(p0[0]-10)},{f(p0[1]+40)} {f(p0[0]-16)},{f(p0[1]+14)} {f(p0[0]-22)},{f(p0[1]-2)} Z')
    b.append(f'<path d="{sac}" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".7"/>')
    for k in range(4):
        yy = p0[1] + 12 + k * 12
        b.append(f'<line x1="{f(p0[0]-14+k*1.5)}" y1="{f(yy)}" x2="{f(p0[0]+12-k*3.5)}" y2="{f(yy+3)}" stroke="{C["boneline"]}" stroke-width=".5"/>')
    cx0, cy0 = p0[0] - 12, p0[1] + 68
    for k in range(4):
        b.append(f'<ellipse cx="{f(cx0-k*2)}" cy="{f(cy0+k*6)}" rx="{f(4.5-k*.8)}" ry="2.6" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".6"/>')
    # region brackets
    labels = [("C", "Cervical  C1–C7", "lordosis (concave posteriorly)"), ("T", "Thoracic  T1–T12", "kyphosis (convex posteriorly);\nribs attach here"),
              ("L", "Lumbar  L1–L5", "lordosis; largest bodies,\nthickest discs")]
    for kind, n, d in labels:
        a, e = regions[kind]
        ya, _ = at(a)
        ye, _ = at(e)
        x = 238
        b.append(f'<path d="M{x-6},{f(ya[1])} h6 v{f(ye[1]-ya[1])} h-6" fill="none" stroke="{C["golddeep"]}" stroke-width=".8"/>')
        mid = (ya[1] + ye[1]) / 2
        b.append(T(x + 8, mid - 3, n, 9.5, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(x + 8, mid + 7, d, 5.9, C["ink2"]))
    b.append(f'<path d="M232,{f(p0[1])} h6 v70 h-6" fill="none" stroke="{C["golddeep"]}" stroke-width=".8"/>')
    b.append(T(246, p0[1] + 22, "Sacrum  S1–S5 (fused)", 9.5, C["forest"], "start", 600, family="Cormorant"))
    b.append(T(246, p0[1] + 32, "kyphotic curve; forms the back\nof the pelvis at the SI joints", 5.9, C["ink2"]))
    b.append(T(246, p0[1] + 60, "Coccyx  (3–5 small segments)", 7.5, C["forest"], "start", 600))
    # annotations left, computed from the drawn column
    (c7, _) = at(regions["C"][1] - 5)
    b.append(leader(c7[0] - 30, c7[1] + 4, 70, c7[1] + 4) + T(66, c7[1] + 2, "C7: prominent\nspinous process", 5.9, C["ink2"], "end"))
    (t6, _) = at((regions["T"][0] + regions["T"][1]) / 2)
    b.append(leader(t6[0] - 26, t6[1] + 8, 70, t6[1] + 8) + T(66, t6[1] + 6, "spinous process\n(posterior)", 5.9, C["ink2"], "end"))
    b.append(leader(t6[0] + 4, t6[1], 220, t6[1] - 30) + T(222, t6[1] - 32, "vertebral\nbody", 5.9, C["ink2"]))
    (ld, _) = at(regions["L"][0] + (regions["L"][1] - regions["L"][0]) * 0.52)
    b.append(leader(ld[0] + 2, ld[1], 70, ld[1] + 10) + T(66, ld[1] + 8, "intervertebral\ndisc", 5.9, C["ink2"], "end"))
    b.append(arrow(300, 18, 336, 18, C["golddeep"]) + T(296, 20, "anterior", 6, C["golddeep"], "end", 600))
    return svg(W, H, "".join(b))


reg("spine", fig_spine(), "The vertebral column in lateral view (schematic; anterior to the right). Typical counts are 7 cervical, 12 thoracic and 5 lumbar vertebrae, "
    "a sacrum of 5 fused segments and a small coccyx; variation exists between individuals [@moore2018].", "half")


def fig_vertebra():
    W, H = 500, 230
    b = []
    # superior view of a lumbar vertebra (anterior at top)
    cx, cy = 110, 100
    body = (f'M{cx-38},{cy-30} C{cx-40},{cy-62} {cx+40},{cy-62} {cx+38},{cy-30} C{cx+36},{cy-14} {cx+18},{cy-10} {cx},{cy-10} '
            f'C{cx-18},{cy-10} {cx-36},{cy-14} {cx-38},{cy-30} Z')
    b.append(f'<path d="{body}" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".9"/>')
    # disc ring hint
    b.append(f'<ellipse cx="{cx}" cy="{cy-36}" rx="16" ry="10" fill="none" stroke="{C["boneline"]}" stroke-width=".4" stroke-dasharray="2 1.5"/>')
    arch = (f'M{cx-26},{cy-14} L{cx-30},{cy+8} L{cx-78},{cy+2} L{cx-80},{cy+14} L{cx-30},{cy+22} L{cx-22},{cy+40} '
            f'L{cx-8},{cy+58} L{cx-7},{cy+90} L{cx+7},{cy+90} L{cx+8},{cy+58} L{cx+22},{cy+40} L{cx+30},{cy+22} '
            f'L{cx+80},{cy+14} L{cx+78},{cy+2} L{cx+30},{cy+8} L{cx+26},{cy-14} Z')
    b.append(f'<path d="{arch}" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".9" stroke-linejoin="round"/>')
    b.append(f'<path d="M{cx-18},{cy-6} C{cx-22},{cy+14} {cx-10},{cy+34} {cx},{cy+36} C{cx+10},{cy+34} {cx+22},{cy+14} {cx+18},{cy-6} Z" fill="#FFFEFA" stroke="{C["boneline"]}" stroke-width=".8"/>')
    for sx in (-1, 1):
        b.append(f'<ellipse cx="{cx+sx*24}" cy="{cy+30}" rx="6" ry="9" transform="rotate({sx*-30} {cx+sx*24} {cy+30})" fill="{C["cart"]}" stroke="{C["boneline"]}" stroke-width=".6"/>')
    lab = [((cx, cy - 40), "vertebral body", 230 - 30, 30), ((cx, cy + 14), "vertebral foramen (spinal cord / cauda equina)", 200, 60),
           ((cx - 28, cy + 2), "pedicle", 200, 80), ((cx - 70, cy + 8), "transverse process", 200, 100),
           ((cx + 24, cy + 30), "superior articular process (facet)", 200, 120), ((cx + 14, cy + 50), "lamina", 200, 140),
           ((cx, cy + 82), "spinous process", 200, 160)]
    for (px, py), t, tx, ty in lab:
        b.append(f'<line x1="{f(px)}" y1="{f(py)}" x2="{tx-4}" y2="{ty-2}" stroke="{C["teak"]}" stroke-width=".45"/><circle cx="{f(px)}" cy="{f(py)}" r="1" fill="{C["teak"]}"/>')
        b.append(T(tx, ty, t, 6.2))
    b.append(T(cx, 18, "Lumbar vertebra, superior view", 7, C["golddeep"], "middle", 700))
    b.append(T(cx, 28, "anterior ↑", 5.8, C["ink2"], "middle"))
    # motion segment lateral
    ox, oy = 370, 70
    for dy in (0, 62):
        b.append(box(ox, oy + dy, 60, 40, C["bone"], C["boneline"], 4, .8))
        b.append(f'<path d="M{ox},{oy+dy+8} L{ox-18},{oy+dy+4} L{ox-38},{oy+dy+12} L{ox-40},{oy+dy+28} L{ox-18},{oy+dy+30} L{ox},{oy+dy+30} Z" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".8"/>')
    b.append(box(ox + 1, oy + 42, 58, 18, C["disc"], "#8FB1AC", 5, .7))
    b.append(f'<ellipse cx="{ox+33}" cy="{oy+51}" rx="10" ry="5" fill="#B4D0CC"/>')
    b.append(f'<circle cx="{ox-10}" cy="{oy+52}" r="5" fill="{C["nerve"]}" stroke="#B48F27" stroke-width=".5"/>')
    b.append(f'<path d="M{ox-26},{oy+34} q4,8 0,16" fill="none" stroke="{C["boneline"]}" stroke-width="1.6"/>')
    b.append(T(ox + 30, 18, "Motion segment, lateral view", 7, C["golddeep"], "middle", 700))
    b.append(T(ox + 30, 28, "anterior →", 5.8, C["ink2"], "middle"))
    for (px, py), t, tx, ty in [((ox + 33, oy + 51), "nucleus pulposus", ox + 70, oy + 48), ((ox + 55, oy + 44), "annulus fibrosus", ox + 70, oy + 60),
                                ((ox - 10, oy + 52), "spinal nerve in intervertebral foramen", ox - 60, oy + 128),
                                ((ox - 26, oy + 40), "facet (zygapophyseal) joint", ox - 60, oy + 142)]:
        b.append(f'<line x1="{f(px)}" y1="{f(py)}" x2="{f(tx)}" y2="{f(ty-3)}" stroke="{C["teak"]}" stroke-width=".45"/><circle cx="{f(px)}" cy="{f(py)}" r="1" fill="{C["teak"]}"/>')
        b.append(T(tx, ty, t, 6.1, anchor="start"))
    return svg(W, H, "".join(b))


reg("vertebra", fig_vertebra(), "A lumbar vertebra from above and a spinal motion segment from the side (schematic). Each segment moves at three joints: the "
    "intervertebral disc in front and the paired facet joints behind [@bogduk2005].", "full")


def fig_pelvis():
    W, H = 470, 290
    b = []
    cx = 170
    bone = f'fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".9" stroke-linejoin="round"'
    for sx in (-1, 1):
        def X(v):
            return cx + sx * v
        ilium = (f'M{X(22)},{60} C{X(40)},{30} {X(95)},{22} {X(120)},{40} C{X(132)},{50} {X(130)},{70} {X(122)},{84} '
                 f'L{X(116)},{96} C{X(104)},{104} {X(96)},{112} {X(90)},{124} C{X(80)},{146} {X(62)},{176} {X(46)},{186} '
                 f'C{X(34)},{194} {X(18)},{196} {X(8)},{190} L{X(8)},{172} C{X(22)},{168} {X(34)},{150} {X(34)},{130} '
                 f'C{X(34)},{110} {X(22)},{98} {X(22)},{60} Z')
        b.append(f'<path d="{ilium}" {bone}/>')
        # obturator foramen
        b.append(f'<ellipse cx="{X(48)}" cy="176" rx="12" ry="15" transform="rotate({sx*30} {X(48)} 176)" fill="#FFFEFA" stroke="{C["boneline"]}" stroke-width=".7"/>')
        # ischial tuberosity
        b.append(f'<path d="M{X(60)},{188} C{X(66)},{206} {X(58)},{214} {X(48)},{212} C{X(42)},{208} {X(44)},{196} {X(46)},{190}" {bone}/>')
        # acetabulum + femur
        b.append(f'<circle cx="{X(96)}" cy="146" r="20" fill="#E7DCC4" stroke="{C["boneline"]}" stroke-width=".9"/>')
        fem = (f'M{X(96)},{128} C{X(112)},{126} {X(122)},{140} {X(118)},{152} L{X(136)},{170} C{X(150)},{160} {X(160)},{170} {X(156)},{186} '
               f'L{X(146)},{200} L{X(140)},{280} L{X(118)},{280} L{X(122)},{204} L{X(108)},{178} L{X(92)},{164} C{X(80)},{160} {X(78)},{134} {X(96)},{128} Z')
        b.append(f'<path d="{fem}" {bone}/>')
        b.append(f'<circle cx="{X(97)}" cy="146" r="15" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".9"/>')
    # sacrum
    sac = f'M{cx-28},{58} L{cx+28},{58} C{cx+30},{90} {cx+20},{130} {cx+6},{150} L{cx-6},{150} C{cx-20},{130} {cx-30},{90} {cx-28},{58} Z'
    b.append(f'<path d="{sac}" fill="#EADFC8" stroke="{C["boneline"]}" stroke-width=".9"/>')
    for k in range(4):
        y = 72 + k * 18
        for sx in (-1, 1):
            b.append(f'<circle cx="{cx+sx*(13-k*2)}" cy="{y}" r="2.2" fill="#FFFEFA" stroke="{C["boneline"]}" stroke-width=".5"/>')
    b.append(f'<path d="M{cx-4},150 L{cx+4},150 L{cx+2},166 L{cx-2},166 Z" {bone}/>')
    b.append(box(cx - 20, 34, 40, 20, C["bone"], C["boneline"], 3, .8))
    b.append(box(cx - 20, 55, 40, 3, C["disc"], "none", 1))
    # pubic symphysis
    b.append(f'<rect x="{cx-3}" y="176" width="6" height="18" fill="{C["cart"]}" stroke="{C["boneline"]}" stroke-width=".5"/>')
    labels = [((cx, 44), "L5 vertebra", 330, 30), ((cx - 26, 100), "sacroiliac (SI) joint", 330, 50), ((cx, 104), "sacrum", 330, 70),
              ((cx + 122, 50), "iliac crest", 330, 90), ((cx + 126, 84), "ASIS (anterior superior iliac spine)", 330, 110),
              ((cx + 97, 146), "femoral head in acetabulum (hip joint)", 330, 130), ((cx + 146, 172), "greater trochanter", 330, 150),
              ((cx + 112, 162), "femoral neck", 330, 170), ((cx, 186), "pubic symphysis", 330, 190), ((cx + 48, 176), "obturator foramen", 330, 210),
              ((cx + 54, 206), "ischial tuberosity (“sitting bone”)", 330, 230), ((cx, 160), "coccyx", 330, 250)]
    for (px, py), t, tx, ty in labels:
        b.append(f'<line x1="{f(px)}" y1="{f(py)}" x2="{tx-4}" y2="{ty-2}" stroke="{C["teak"]}" stroke-width=".4"/><circle cx="{f(px)}" cy="{f(py)}" r="1" fill="{C["teak"]}"/>')
        b.append(T(tx, ty, t, 6.2))
    return svg(W, H, "".join(b))


reg("pelvis", fig_pelvis(), "The pelvis and hip joints, anterior view (schematic). The pelvis is a ring of two hip bones and the sacrum; the femoral head sits deep in the acetabulum. "
    "Depth and orientation of the socket, and the angle of the femoral neck, vary considerably between people [@clark2016; @neumann2017].", "full")


def fig_pelvictilt():
    W, H = 470, 190
    b = []
    for i, (lab, ang, note) in enumerate([("Anterior tilt", 12, "ASIS moves forward and down;\nlumbar lordosis increases"),
                                          ("Neutral", 0, "ASIS and pubic symphysis\nroughly in one vertical plane"),
                                          ("Posterior tilt", -12, "ASIS moves back and up;\nlumbar curve flattens")]):
        cx, cy = 85 + i * 150, 112   # hip joint = centre of rotation
        r = math.radians(ang)

        def R(x, y):
            return (cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r))
        outline = [(-30, -30), (-16, -44), (4, -46), (22, -38), (32, -24), (30, -14), (22, -6), (26, 14), (24, 30),
                   (12, 32), (0, 20), (-12, 28), (-18, 34), (-26, 28), (-22, 12), (-34, -6)]
        b.append('<path d="M' + " L".join(f"{f(x)},{f(y)}" for x, y in (R(*p) for p in outline)) +
                 f' Z" fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".9" stroke-linejoin="round"/>')
        sac = [(-22, -32), (-30, -6), (-34, 16), (-30, 18), (-24, -4), (-14, -30)]
        b.append('<path d="M' + " L".join(f"{f(x)},{f(y)}" for x, y in (R(*p) for p in sac)) +
                 f' Z" fill="#E4D6BA" stroke="{C["boneline"]}" stroke-width=".7"/>')
        hc = R(0, 0)
        b.append(f'<circle cx="{f(hc[0])}" cy="{f(hc[1])}" r="7" fill="#E7DCC4" stroke="{C["boneline"]}" stroke-width=".8"/>')
        b.append(f'<line x1="{f(hc[0])}" y1="{f(hc[1])}" x2="{f(hc[0]+2)}" y2="{f(hc[1]+44)}" stroke="#E2D6BC" stroke-width="7" stroke-linecap="round"/>')
        top = R(-18, -32)
        bulge = 16 + ang * 1.4
        lum_end = (top[0] - 2, top[1] - 52)
        b.append(f'<path d="M{f(top[0])},{f(top[1])} Q{f(top[0]+bulge)},{f(top[1]-28)} {f(lum_end[0])},{f(lum_end[1])}" '
                 f'fill="none" stroke="{C["forest"]}" stroke-width="4" stroke-linecap="round"/>')
        asis = R(32, -24)
        pub = R(24, 30)
        b.append(f'<circle cx="{f(asis[0])}" cy="{f(asis[1])}" r="2.4" fill="{C["clay"]}"/><circle cx="{f(pub[0])}" cy="{f(pub[1])}" r="2.4" fill="{C["blue"]}"/>')
        b.append(f'<line x1="{f(asis[0])}" y1="{f(asis[1])}" x2="{f(pub[0])}" y2="{f(pub[1])}" stroke="{C["ink2"]}" stroke-width=".5" stroke-dasharray="2 1.5"/>')
        b.append(T(cx, 172, lab, 10, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(cx, 181, note.split("\n")[0], 5.8, C["ink2"], "middle"))
        b.append(T(cx, 188, note.split("\n")[1], 5.8, C["ink2"], "middle"))
    b.append(T(14, 14, "PELVIC TILT · lateral view, facing right · rotation occurs at the hip joints", 6.4, C["golddeep"], "start", 700, ls=.6))
    b.append(T(456, 14, "● ASIS   ● pubic symphysis", 6, C["ink2"], "end"))
    return svg(W, H + 6, "".join(b))


reg("pelvictilt", fig_pelvictilt(), "Pelvic tilt and its effect on the lumbar curve (schematic). Much “alignment” teaching in forward bends and backbends is really about where the pelvis is allowed to move.")


def fig_shoulder():
    W, H = 480, 260
    b = []
    bone = f'fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".9" stroke-linejoin="round"'
    cx = 120
    # ribcage hint
    for k in range(7):
        y = 60 + k * 20
        b.append(f'<path d="M{cx},{y} C{cx+50},{y-10} {cx+86},{y+2} {cx+92},{y+20}" fill="none" stroke="#E2D7C0" stroke-width="3"/>')
    b.append(box(cx - 5, 30, 10, 190, "#E7DCC4", C["boneline"], 3, .6))
    # scapula (right side of the body shown on the right, posterior view)
    sc = (f'M{cx+30},{66} L{cx+104},{58} C{cx+112},{70} {cx+106},{90} {cx+100},{104} L{cx+52},{182} '
          f'C{cx+46},{188} {cx+40},{184} {cx+38},{176} L{cx+30},{66} Z')
    b.append(f'<path d="{sc}" {bone}/>')
    b.append(f'<path d="M{cx+34},{84} L{cx+118},{66} L{cx+124},{56} L{cx+114},{52} L{cx+104},{62} L{cx+32},{76} Z" {bone}/>')
    b.append(f'<path d="M{cx+10},{40} C{cx+50},{30} {cx+90},{44} {cx+120},{50}" fill="none" stroke="{C["boneline"]}" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<path d="M{cx+10},{40} C{cx+50},{30} {cx+90},{44} {cx+120},{50}" fill="none" stroke="{C["bone"]}" stroke-width="4.4" stroke-linecap="round"/>')
    b.append(f'<circle cx="{cx+124}" cy="{74}" r="15" {bone}/>')
    b.append(f'<path d="M{cx+116},{84} L{cx+134},{84} L{cx+138},{220} L{cx+122},{220} Z" {bone}/>')
    labels = [((cx + 66, 40), "clavicle", 300, 34), ((cx + 118, 57), "acromion", 300, 52), ((cx + 76, 70), "spine of scapula", 300, 70),
              ((cx + 124, 76), "head of humerus (glenohumeral joint)", 300, 88), ((cx + 34, 120), "medial border", 300, 106),
              ((cx + 44, 180), "inferior angle", 300, 124), ((cx + 70, 130), "scapula lies on the rib cage:\nthe scapulothoracic “joint”", 300, 142)]
    for (px, py), t, tx, ty in labels:
        b.append(f'<line x1="{f(px)}" y1="{f(py)}" x2="{tx-4}" y2="{ty-2}" stroke="{C["teak"]}" stroke-width=".4"/><circle cx="{f(px)}" cy="{f(py)}" r="1" fill="{C["teak"]}"/>')
        b.append(T(tx, ty, t, 6.2))
    b.append(T(cx + 60, 246, "Right shoulder girdle, posterior view (schematic)", 6.4, C["golddeep"], "middle", 600))
    # movements
    b.append(T(300, 182, "Scapular movements", 10, C["forest"], "start", 600, family="Cormorant"))
    mv = [("Elevation / depression", "shrugging up / drawing down"), ("Protraction / retraction", "sliding forward around the ribs / squeezing back"),
          ("Upward / downward rotation", "glenoid turns up (arms overhead) / down")]
    for i, (a, d) in enumerate(mv):
        b.append(T(300, 196 + i * 20, a, 6.5, C["ink"], "start", 600))
        b.append(T(300, 204 + i * 20, d, 5.8, C["ink2"]))
    return svg(W, H, "".join(b))


reg("shoulder", fig_shoulder(), "The shoulder girdle is a chain: sternum → clavicle → scapula → humerus. Raising the arms overhead needs both glenohumeral movement and "
    "upward rotation of the scapula (scapulohumeral rhythm) [@neumann2017].", "full")


def fig_knee():
    W, H = 430, 250
    b = []
    bone = f'fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".9" stroke-linejoin="round"'
    cx = 120
    fem = f'M{cx-18},10 L{cx+18},10 L{cx+22},70 C{cx+46},84 {cx+48},110 {cx+36},118 L{cx+6},116 L{cx},108 L{cx-6},116 L{cx-36},118 C{cx-48},110 {cx-46},84 {cx-22},70 Z'
    b.append(f'<path d="{fem}" {bone}/>')
    tib = f'M{cx-44},132 L{cx+44},132 C{cx+46},146 {cx+34},156 {cx+22},160 L{cx+16},240 L{cx-16},240 L{cx-22},160 C{cx-34},156 {cx-46},146 {cx-44},132 Z'
    b.append(f'<path d="{tib}" {bone}/>')
    b.append(f'<path d="M{cx-50},150 L{cx-40},150 L{cx-42},240 L{cx-50},240 Z" {bone}/>')  # fibula (lateral, viewer's left for right knee)
    # menisci
    b.append(f'<path d="M{cx-42},128 C{cx-40},120 {cx-10},120 {cx-6},128" fill="none" stroke="#8FB1AC" stroke-width="4" stroke-linecap="round"/>')
    b.append(f'<path d="M{cx+6},128 C{cx+10},120 {cx+42},120 {cx+42},128" fill="none" stroke="#8FB1AC" stroke-width="4" stroke-linecap="round"/>')
    # cruciates
    b.append(f'<line x1="{cx-2}" y1="130" x2="{cx-14}" y2="104" stroke="{C["clay"]}" stroke-width="3.2" stroke-linecap="round"/>')
    b.append(f'<line x1="{cx+6}" y1="134" x2="{cx+12}" y2="104" stroke="{C["blue"]}" stroke-width="3.2" stroke-linecap="round"/>')
    # collaterals
    b.append(f'<line x1="{cx+44}" y1="92" x2="{cx+34}" y2="170" stroke="#B89B5C" stroke-width="3.2" stroke-linecap="round"/>')
    b.append(f'<line x1="{cx-44}" y1="92" x2="{cx-47}" y2="152" stroke="#B89B5C" stroke-width="3.2" stroke-linecap="round"/>')
    labels = [((cx, 40), "femur", 260, 22), ((cx - 14, 108), "anterior cruciate ligament (ACL)", 260, 50), ((cx + 11, 108), "posterior cruciate ligament (PCL)", 260, 68),
              ((cx + 26, 122), "medial meniscus", 260, 86), ((cx - 26, 122), "lateral meniscus", 260, 104),
              ((cx + 40, 130), "medial collateral ligament (MCL)", 260, 122), ((cx - 46, 120), "lateral collateral ligament (LCL)", 260, 140),
              ((cx - 46, 200), "fibula", 260, 158), ((cx, 200), "tibia", 260, 176)]
    for (px, py), t, tx, ty in labels:
        b.append(f'<line x1="{f(px)}" y1="{f(py)}" x2="{tx-4}" y2="{ty-2}" stroke="{C["teak"]}" stroke-width=".4"/><circle cx="{f(px)}" cy="{f(py)}" r="1" fill="{C["teak"]}"/>')
        b.append(T(tx, ty, t, 6.2))
    b.append(T(cx - 50, 8, "lateral", 5.8, C["ink2"], "middle", italic=True) + T(cx + 50, 8, "medial", 5.8, C["ink2"], "middle", italic=True))
    b.append(T(260, 206, "The knee is mainly a hinge (flexion/extension)\nwith a little rotation when flexed. It tolerates\ntwisting under load poorly — which is why\nlotus is never forced from the knee.", 6.2, C["teak"], italic=True))
    return svg(W, H, "".join(b))


reg("knee", fig_knee(), "Right knee, anterior view with the patella removed (schematic). The menisci deepen the flat tibial plateau; the cruciate and collateral ligaments limit "
    "forward/backward and side-to-side movement of the tibia on the femur [@moore2018].")


def fig_foot():
    W, H = 470, 200
    b = []
    bone = f'fill="{C["bone"]}" stroke="{C["boneline"]}" stroke-width=".8" stroke-linejoin="round"'
    # medial view: calcaneus, talus, navicular, cuneiform, metatarsal, phalanges
    b.append(f'<path d="M40,140 C30,120 40,104 64,102 L96,108 L100,130 L84,146 C66,152 48,150 40,140 Z" {bone}/>')  # calcaneus
    b.append(f'<path d="M78,86 C84,72 112,70 122,82 L126,96 L104,106 L84,104 Z" {bone}/>')  # talus
    b.append(f'<path d="M126,90 L146,94 L146,112 L124,110 Z" {bone}/>')  # navicular
    b.append(f'<path d="M148,96 L170,102 L168,122 L146,116 Z" {bone}/>')  # cuneiform
    b.append(f'<path d="M172,106 L250,134 L248,146 L170,124 Z" {bone}/>')  # 1st metatarsal
    b.append(f'<circle cx="252" cy="142" r="7" {bone}/>')
    b.append(f'<path d="M258,138 L282,142 L282,152 L258,150 Z" {bone}/>')
    b.append(f'<path d="M284,142 L302,146 L300,154 L284,152 Z" {bone}/>')
    b.append(f'<path d="M92,58 L108,58 L112,84 L90,84 Z" {bone}/>')  # tibia stub
    b.append(f'<path d="M50,152 C120,160 200,158 252,152" fill="none" stroke="{C["terra"]}" stroke-width="1.6" stroke-dasharray="3 2"/>')
    b.append(f'<path d="M60,142 C100,118 160,112 248,144" fill="none" stroke="{C["golddeep"]}" stroke-width="1" />')
    b.append(T(120, 176, "Medial longitudinal arch (right foot, medial view)", 6.4, C["golddeep"], "middle", 600))
    for (px, py), t, tx, ty in [((60, 128), "calcaneus", 20, 188 - 10), ((104, 86), "talus", 60, 40), ((136, 100), "navicular", 130, 58),
                                ((210, 124), "1st metatarsal", 210, 92), ((150, 156), "plantar fascia", 170, 190 - 4)]:
        b.append(f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty+2}" stroke="{C["teak"]}" stroke-width=".4"/>' + T(tx, ty, t, 6, anchor="middle"))
    # plantar tripod
    ox = 380
    foot = f'M{ox-20},{176} C{ox-34},{150} {ox-30},{96} {ox-26},{70} C{ox-24},{40} {ox-10},{20} {ox+8},{22} C{ox+30},{24} {ox+36},{50} {ox+32},{80} C{ox+28},{110} {ox+16},{150} {ox+12},{174} C{ox+6},{190} {ox-12},{192} {ox-20},{176} Z'
    b.append(f'<path d="{foot}" fill="#F3EBDD" stroke="{C["boneline"]}" stroke-width=".9"/>')
    for (x, y, t) in [(ox - 4, 172, "heel"), (ox - 16, 58, "1st metatarsal head\n(ball of big toe)"), (ox + 26, 74, "5th metatarsal head")]:
        b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{C["gold"]}" fill-opacity=".55" stroke="{C["golddeep"]}"/>')
    b.append(f'<polygon points="{ox-4},172 {ox-16},58 {ox+26},74" fill="none" stroke="{C["golddeep"]}" stroke-width=".8" stroke-dasharray="2 1.5"/>')
    b.append(T(ox + 2, 12, "The “tripod” of the foot (sole)", 6.4, C["golddeep"], "middle", 600))
    b.append(T(ox - 60, 60, "big-toe\nmound", 5.8, C["ink2"], "end") + T(ox + 44, 76, "little-toe\nmound", 5.8, C["ink2"]) + T(ox + 20, 180, "heel", 5.8, C["ink2"]))
    return svg(W, H, "".join(b))


reg("foot", fig_foot(), "The foot as a foundation: the medial arch (left) and the three weight-bearing points often cued in standing poses (right). Arch height varies widely "
    "and a low arch is not in itself a problem.", "full")


def fig_hand():
    W, H = 470, 210
    b = []
    ox, oy = 110, 20
    hand = (f'M{ox-40},{oy+180} C{ox-50},{oy+140} {ox-52},{oy+110} {ox-48},{oy+96} L{ox-74},{oy+62} C{ox-80},{oy+52} {ox-70},{oy+44} {ox-62},{oy+52} '
            f'L{ox-38},{oy+78} L{ox-36},{oy+20} C{ox-36},{oy+10} {ox-24},{oy+10} {ox-24},{oy+20} L{ox-22},{oy+66} L{ox-16},{oy+6} C{ox-16},{oy-4} {ox-2},{oy-4} {ox-2},{oy+6} '
            f'L{ox},{oy+64} L{ox+8},{oy+12} C{ox+10},{oy+2} {ox+22},{oy+4} {ox+20},{oy+14} L{ox+16},{oy+70} L{ox+28},{oy+32} C{ox+32},{oy+22} {ox+42},{oy+26} {ox+40},{oy+36} '
            f'L{ox+30},{oy+100} C{ox+28},{oy+140} {ox+24},{oy+160} {ox+22},{oy+180} Z')
    b.append(f'<path d="{hand}" fill="#F3EBDD" stroke="{C["boneline"]}" stroke-width=".9"/>')
    pts = [(ox - 26, oy + 74, "base of index finger\n(2nd MCP joint)"), (ox - 40, oy + 84, "thumb mound"), (ox + 22, oy + 96, "outer knuckle / edge"),
           (ox - 8, oy + 156, "heel of the hand")]
    for x, y, t in pts:
        b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{C["gold"]}" fill-opacity=".5" stroke="{C["golddeep"]}"/>')
    b.append(T(ox + 60, oy + 20, "Spread the load around the\nwhole rim of the palm and press\nthrough the base of the index\nfinger and thumb, rather than\nsinking into the heel of the hand.", 6.2, C["teak"]))
    b.append(T(ox, 206, "Right palm: loading points", 6.4, C["golddeep"], "middle", 600))
    # wrist angle panel
    x0, y0 = 330, 160
    b.append(f'<line x1="{x0-20}" y1="{y0}" x2="{x0+110}" y2="{y0}" stroke="#CDBFA5"/>')
    b.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+36}" y2="{y0}" stroke="{C["forest"]}" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0-80}" stroke="{C["sage"]}" stroke-width="7" stroke-linecap="round"/>')
    b.append(f'<path d="M{x0+18},{y0} A18,18 0 0 0 {x0},{y0-18}" fill="none" stroke="{C["clay"]}" stroke-width="1"/>')
    b.append(T(x0 - 10, y0 - 50, "≈ 90° wrist\nextension\n(plank, forearm\nvertical)", 6, C["clay"], "end"))
    b.append(f'<line x1="{x0+62}" y1="{y0}" x2="{x0+96}" y2="{y0}" stroke="{C["forest"]}" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<line x1="{x0+62}" y1="{y0}" x2="{x0+100}" y2="{y0-70}" stroke="{C["sage"]}" stroke-width="7" stroke-linecap="round"/>')
    b.append(T(x0 + 74, y0 + 14, "less extension\n(downward dog)", 6, C["ink2"]))
    b.append(T(x0 + 40, 30, "Wrist angle under load", 6.4, C["golddeep"], "middle", 600))
    return svg(W, H, "".join(b))


reg("hand", fig_hand(), "Weight-bearing through the hands. Plank and crow place the wrist near the end of its extension range under load; commonly reported active wrist extension "
    "is around 70°, though individuals differ [@neumann2017]. Spreading load and building tolerance gradually are the practical responses.", "full")


def fig_ribs():
    W, H = 470, 180
    b = []
    # pump handle (lateral view)
    x0, y0 = 60, 40
    b.append(box(x0 - 4, y0 - 10, 8, 120, "#E7DCC4", C["boneline"], 2, .6))
    b.append(T(x0, y0 - 16, "spine", 5.6, C["ink2"], "middle"))
    for k, dy in enumerate((0, 28, 56)):
        b.append(f'<path d="M{x0},{y0+dy} C{x0+40},{y0+dy+10} {x0+80},{y0+dy+26} {x0+104},{y0+dy+36}" fill="none" stroke="{C["boneline"]}" stroke-width="3"/>')
        b.append(f'<path d="M{x0},{y0+dy} C{x0+40},{y0+dy-2} {x0+82},{y0+dy+8} {x0+108},{y0+dy+14}" fill="none" stroke="{C["terra"]}" stroke-width="1.4" stroke-dasharray="3 2"/>')
    b.append(box(x0 + 104, y0 + 20, 8, 96, "#E7DCC4", C["boneline"], 2, .6))
    b.append(arrow(x0 + 126, y0 + 60, x0 + 126, y0 + 40, C["clay"], m="arrt") + arrow(x0 + 126, y0 + 60, x0 + 142, y0 + 60, C["clay"], m="arrt"))
    b.append(T(x0 + 116, y0 + 132, "sternum", 5.6, C["ink2"], "middle"))
    b.append(T(x0 + 50, 170, "Pump-handle motion (upper ribs, side view):\nsternum moves forward and up", 6.2, C["forest"], "middle", 600))
    # bucket handle (front view)
    x1, y1 = 330, 40
    b.append(box(x1 - 4, y1 - 10, 8, 110, "#E7DCC4", C["boneline"], 2, .6))
    for sx in (-1, 1):
        for dy in (20, 44, 68):
            b.append(f'<path d="M{x1},{y1+dy} C{x1+sx*40},{y1+dy+26} {x1+sx*80},{y1+dy+20} {x1+sx*96},{y1+dy-4}" fill="none" stroke="{C["boneline"]}" stroke-width="3"/>')
            b.append(f'<path d="M{x1},{y1+dy} C{x1+sx*44},{y1+dy+16} {x1+sx*90},{y1+dy+8} {x1+sx*104},{y1+dy-10}" fill="none" stroke="{C["terra"]}" stroke-width="1.4" stroke-dasharray="3 2"/>')
    b.append(arrow(x1 + 104, y1 + 70, x1 + 122, y1 + 60, C["clay"], m="arrt") + arrow(x1 - 104, y1 + 70, x1 - 122, y1 + 60, C["clay"], m="arrt"))
    b.append(T(x1, 170, "Bucket-handle motion (lower ribs, front view):\nribs swing up and out, widening the chest", 6.2, C["forest"], "middle", 600))
    return svg(W, H + 12, "".join(b))


reg("ribs", fig_ribs(), "Rib movement during inhalation (dashed = inhaled position, schematic). Upper ribs mainly increase the front-to-back depth of the chest; lower ribs mainly increase its width [@calais2006; @west2020].", "full")


def fig_diaphragm():
    W, H = 470, 230
    b = []
    for i, (lab, dome, rib) in enumerate([("Exhalation", 92, 0), ("Inhalation", 116, 8)]):
        ox = 40 + i * 230
        # torso outline
        b.append(f'<path d="M{ox+10},{20} C{ox-4-rib},{80} {ox-6-rib},{150} {ox+14},{210} L{ox+166},{210} C{ox+186+rib},{150} {ox+184+rib},{80} {ox+170},{20} Z" fill="#FBF6EC" stroke="{C["line"]}" stroke-width=".8"/>')
        for k in range(6):
            y = 42 + k * 18
            b.append(f'<path d="M{ox+18-rib*(k/6)},{y} C{ox+40},{y+10} {ox+80},{y+12} {ox+90},{y+8}" fill="none" stroke="#E4D6BB" stroke-width="2.4"/>')
            b.append(f'<path d="M{ox+162+rib*(k/6)},{y} C{ox+140},{y+10} {ox+100},{y+12} {ox+90},{y+8}" fill="none" stroke="#E4D6BB" stroke-width="2.4"/>')
        # lungs
        for sx in (-1, 1):
            cx = ox + 90 + sx * 38
            b.append(f'<path d="M{cx},{36} C{cx+sx*34},{40} {cx+sx*44+sx*rib},{dome-10} {cx+sx*40+sx*rib},{dome+ (6 if i else 0)} '
                     f'C{cx+sx*10},{dome-14} {cx-sx*20},{dome-20} {cx-sx*24},{dome-8} C{cx-sx*26},{70} {cx-sx*12},{40} {cx},{36} Z" '
                     f'fill="{C["lung"]}" stroke="#D9A898" stroke-width=".8"/>')
        # diaphragm dome
        d = f'M{ox+8-rib},{dome+26} C{ox+30},{dome-30} {ox+70},{dome-20} {ox+90},{dome-4} C{ox+110},{dome-20} {ox+150},{dome-30} {ox+172+rib},{dome+26}'
        b.append(f'<path d="{d}" fill="none" stroke="{C["clay"]}" stroke-width="4" stroke-linecap="round"/>')
        b.append(f'<path d="M{ox+80},{dome+2} L{ox+72},{dome+80} M{ox+100},{dome+2} L{ox+108},{dome+80}" stroke="{C["clay"]}" stroke-width="2"/>')
        b.append(f'<ellipse cx="{ox+90}" cy="{dome+60 + (10 if i else 0)}" rx="{50 + (8 if i else 0)}" ry="30" fill="#EFE1C6" stroke="#D7C39B" stroke-width=".6"/>')
        b.append(T(ox + 90, dome + 64 + (10 if i else 0), "abdominal contents", 5.6, C["ink2"], "middle"))
        b.append(T(ox + 90, 226, lab, 11, C["forest"], "middle", 600, family="Cormorant"))
        if i:
            b.append(arrow(ox + 90, dome - 40, ox + 90, dome - 10, C["clay"], 1.2, "arrt"))
            b.append(arrow(ox + 176, 120, ox + 196, 120, C["clay"], 1.2, "arrt") + arrow(ox + 4, 120, ox - 16, 120, C["clay"], 1.2, "arrt"))
            b.append(arrow(ox + 150, dome + 70, ox + 162, dome + 84, C["clay"], 1.2, "arrt"))
    b.append(leader(62, 118, 20, 60) + T(18, 56, "diaphragm", 6, C["clay"], "end", 600) if False else "")
    b.append(T(150, 140, "diaphragm", 6.2, C["clay"], "middle", 600))
    b.append(T(92, 176, "crura attach to\nlumbar vertebrae", 5.6, C["ink2"], "middle"))
    return svg(W, H + 4, "".join(b))


reg("diaphragm", fig_diaphragm(), "The diaphragm in exhalation and inhalation (front view, schematic). Contracting, the dome descends and flattens, lower ribs widen, and abdominal "
    "contents are displaced downward and forward; in quiet breathing, exhalation is largely passive recoil [@west2020; @hall2021].", "full")


def fig_spirogram():
    W, H = 500, 220
    b = []
    x0, y0, x1, y1 = 60, 20, 300, 190
    # volume scale: 0 at bottom (y1) to 6000 mL at top (y0)
    def Y(v):
        return y1 - (y1 - y0) * v / 6000
    b.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{C["ink2"]}" stroke-width=".6"/>')
    b.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{C["ink2"]}" stroke-width=".6"/>')
    for v in range(0, 6001, 1000):
        b.append(T(x0 - 4, Y(v) + 2, f"{v}", 5.4, C["ink2"], "end") + f'<line x1="{x0-2}" y1="{f(Y(v))}" x2="{x0}" y2="{f(Y(v))}" stroke="{C["ink2"]}" stroke-width=".5"/>')
    b.append(T(24, 105, "mL", 5.6, C["ink2"], "middle"))
    # trace: tidal breathing at FRC 2300 to 2800, then max inspiration to 5800, max expiration to 1200, back
    pts = []
    x = x0 + 5
    def wave(x, n, lo, hi, step=10):
        out = []
        for k in range(n * 2):
            out.append((x + k * step, Y(hi if k % 2 else lo)))
        return out
    pts += wave(x, 3, 2300, 2800)
    x = pts[-1][0] + 12
    pts += [(x, Y(2300)), (x + 22, Y(5800)), (x + 44, Y(1200)), (x + 64, Y(2300))]
    x = pts[-1][0] + 10
    pts += wave(x, 3, 2300, 2800)
    d = "M" + " ".join(f"{f(a)},{f(c)}" for a, c in pts)
    b.append(f'<path d="{d}" fill="none" stroke="{C["blue"]}" stroke-width="1.2" stroke-linejoin="round"/>')
    for v, col in [(5800, C["line"]), (2800, C["line"]), (2300, C["line"]), (1200, C["line"])]:
        b.append(f'<line x1="{x0}" y1="{f(Y(v))}" x2="{x1}" y2="{f(Y(v))}" stroke="{col}" stroke-width=".5" stroke-dasharray="2 2"/>')
    # brackets on right
    items = [(2800, 5800, "IRV  inspiratory reserve  3000 mL", 312), (2300, 2800, "TV  tidal volume  500 mL", 312),
             (1200, 2300, "ERV  expiratory reserve  1100 mL", 312), (0, 1200, "RV  residual volume  1200 mL", 312)]
    for a, c, t, x in items:
        b.append(f'<path d="M{x-6},{f(Y(c))} h4 v{f(Y(a)-Y(c))} h-4" fill="none" stroke="{C["golddeep"]}" stroke-width=".7"/>')
        b.append(T(x + 2, (Y(a) + Y(c)) / 2 + 2, t, 6, C["ink"]))
    b.append(T(312, 200, "VC vital capacity = IRV + TV + ERV ≈ 4600 mL\nTLC total lung capacity ≈ 5800 mL\nFRC = ERV + RV ≈ 2300 mL", 5.8, C["teak"]))
    return svg(W, H + 10, "".join(b))


reg("spirogram", fig_spirogram(), "Lung volumes and capacities, using the textbook values for an average young adult man [@hall2021]. Values vary with body size, sex, age and training; "
    "they are shown to explain what “full breathing” changes (mainly the use of the reserve volumes), not as targets.", "full")


def fig_ans():
    W, H = 470, 250
    b = []
    rows = [("Pupils", "dilate", "constrict"), ("Heart rate", "increases", "decreases"), ("Airways (bronchi)", "dilate", "constrict"),
            ("Digestion", "inhibited", "stimulated"), ("Salivation", "reduced, thick", "increased, watery"),
            ("Liver", "releases glucose", "stores glycogen"), ("Bladder", "relaxes (retains)", "contracts (empties)"),
            ("Adrenal medulla", "releases adrenaline", "—")]
    b.append(box(20, 20, 430, 30, C["forest"], "none", 3))
    b.append(T(110, 39, "Organ", 7, "#FFF8EA", "middle", 700))
    b.append(T(250, 34, "Sympathetic", 9.5, "#FFF8EA", "middle", 600, family="Cormorant") + T(250, 45, "thoracolumbar outflow (T1–L2)", 5.6, "#E9E2CF", "middle"))
    b.append(T(380, 34, "Parasympathetic", 9.5, "#FFF8EA", "middle", 600, family="Cormorant") + T(380, 45, "craniosacral (CN III, VII, IX, X; S2–S4)", 5.6, "#E9E2CF", "middle"))
    for i, (o, s_, p_) in enumerate(rows):
        y = 64 + i * 20
        if i % 2:
            b.append(box(20, y - 12, 430, 20, "#FAF6EE", "none", 0))
        b.append(T(40, y + 1, o, 6.8, C["ink"], "start", 600))
        b.append(T(250, y + 1, s_, 6.8, C["clay"], "middle"))
        b.append(T(380, y + 1, p_, 6.8, C["blue"], "middle"))
    b.append(T(20, 234, "Both branches are active all the time; health depends on flexible shifting between them, not on one “winning”.\n"
                        "The vagus nerve (CN X) carries roughly three-quarters of all parasympathetic fibres.", 6.1, C["teak"], italic=True))
    return svg(W, H + 6, "".join(b))


reg("ans", fig_ans(), "Typical effects of the two branches of the autonomic nervous system [@hall2021]. The table simplifies: several organs receive only one branch, and "
    "responses depend on context.", "full")


def fig_rsa():
    W, H = 470, 150
    b = []
    x0, x1 = 50, 440
    b.append(T(20, 44, "breath", 6, C["ink2"], "start", 600) + T(20, 104, "heart rate", 6, C["ink2"], "start", 600))
    pts_b, pts_h = [], []
    for k in range(0, 391):
        x = x0 + k
        t = k / 390 * 3 * 2 * math.pi
        pts_b.append((x, 48 - 20 * math.sin(t)))
        pts_h.append((x, 108 - 14 * math.sin(t - 0.35)))
    b.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts_b) + f'" fill="none" stroke="{C["blue"]}" stroke-width="1.3"/>')
    b.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts_h) + f'" fill="none" stroke="{C["clay"]}" stroke-width="1.3"/>')
    for k in range(3):
        xa = x0 + k * 130
        b.append(box(xa, 16, 65, 116, C["goldpale"], "none", 0).replace('rx="0"', 'rx="0" fill-opacity=".5"'))
        b.append(T(xa + 32, 142, "inhale: HR rises", 5.8, C["golddeep"], "middle"))
        b.append(T(xa + 97, 142, "exhale: HR falls", 5.8, C["ink2"], "middle"))
    return svg(W, H, "".join(b))


reg("rsa", fig_rsa(), "Respiratory sinus arrhythmia (schematic): heart rate rises a little with each inhalation and falls with each exhalation. Slow, even breathing near six breaths a minute "
    "tends to enlarge these oscillations, which is one physiological basis of slow-breathing practices [@lehrer2014; @russo2017].", "full")


def fig_contraction():
    W, H = 470, 170
    b = []
    kinds = [("Concentric", "muscle shortens while producing force", "lifting into locust: back extensors", 60, "short"),
             ("Isometric", "force without change in length", "holding the lifted locust still", 0, "same"),
             ("Eccentric", "muscle lengthens while producing force", "lowering slowly from locust", -60, "long")]
    for i, (n, d, ex, ang, st) in enumerate(kinds):
        ox = 20 + i * 150
        b.append(box(ox, 10, 140, 150, "#FBF7EF", C["line"], 4, .5))
        # upper arm vertical, forearm at angle
        sx, sy = ox + 50, 30
        ex_, ey = ox + 50, 90
        a = math.radians(-20 if st == "short" else (10 if st == "same" else 38))
        wx, wy = ex_ + 50 * math.cos(a), ey + 50 * math.sin(a)
        b.append(f'<line x1="{sx}" y1="{sy}" x2="{ex_}" y2="{ey}" stroke="{C["bone"]}" stroke-width="9" stroke-linecap="round"/>')
        b.append(f'<line x1="{sx}" y1="{sy}" x2="{ex_}" y2="{ey}" stroke="{C["boneline"]}" stroke-width=".6"/>')
        b.append(f'<line x1="{ex_}" y1="{ey}" x2="{f(wx)}" y2="{f(wy)}" stroke="{C["bone"]}" stroke-width="7" stroke-linecap="round"/>')
        mx, my = ex_ + 14 * math.cos(a), ey + 14 * math.sin(a)
        col = ACTIVE
        b.append(f'<path d="M{sx+4},{sy+10} Q{sx+ (26 if st=="short" else 18 if st=="same" else 12)},{(sy+my)/2} {f(mx)},{f(my)} Q{sx+8},{(sy+my)/2} {sx+4},{sy+10} Z" fill="{col}" fill-opacity=".8"/>')
        b.append(f'<circle cx="{f(wx)}" cy="{f(wy)}" r="6" fill="{C["gold"]}"/>')
        if st == "short":
            b.append(arrow(f(wx + 14), f(wy + 10), f(wx + 14), f(wy - 10), C["golddeep"]))
        elif st == "long":
            b.append(arrow(f(wx + 14), f(wy - 16), f(wx + 14), f(wy + 2), C["golddeep"]))
        b.append(T(ox + 70, 118, n, 11, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(ox + 70, 130, d, 5.7, C["ink2"], "middle"))
        b.append(T(ox + 70, 146, "e.g. " + ex, 5.7, C["golddeep"], "middle", italic=True))
    return svg(W, H, "".join(b))


reg("contraction", fig_contraction(), "Three kinds of muscle contraction, shown for the elbow flexors for clarity; the yoga examples beneath each apply the same idea to the back extensors in locust.", "full")


def fig_tension():
    W, H = 470, 200
    musc = [(("lt", 0.0, "post"), ("sh1", 0.06, "post"), 3.2, "stretch"),
            (("sh1", 0.1, "post"), ("sh1", 0.8, "post"), 2.6, "stretch"),
            (("lt", 0.25, "post"), ("ut", 0.85, "post"), 2.4, "stretch")]
    s = draw(P["paschimottanasana"], muscles=musc, floor=True)
    inner, h = embed(s, 20, 20, 250)
    b = [inner]
    b.append(T(290, 40, "Tension (tensile load)", 10, C["clay"], "start", 600, family="Cormorant"))
    b.append(T(290, 52, "tissues on the convex side are pulled:\nhamstrings, calf, back of the trunk,\nposterior hip and spinal ligaments", 6, C["ink2"]))
    b.append(T(290, 98, "Compression", 10, C["blue"], "start", 600, family="Cormorant"))
    b.append(T(290, 110, "tissues on the concave side are pressed\ntogether: front of the hip, abdomen,\nanterior discs when the spine rounds", 6, C["ink2"]))
    b.append(T(290, 156, "When a fold stops, the limit may be\ntension (felt behind) or compression\n(felt in front, e.g. belly meets thighs).", 6.1, C["teak"], italic=True))
    return svg(W, H, "".join(b))


reg("tension", fig_tension(), "Tension and compression in a seated forward bend. Coloured spindles show tissues that are lengthening under load (terracotta). Recognising which "
    "kind of limit a student has reached changes what you teach next [@clark2016].", "full")


def fig_rom():
    W, H = 470, 150
    a = draw(P["leg_raise"] | dict(th1=-60, sh1=-60, ft1=-60), floor=True)
    bp = draw(P["supta_padangusthasana"], props=[], floor=True)
    i1, h1 = embed(a, 30, 20, 170)
    i2, h2 = embed(bp, 250, 10, 170)
    b = [i1, i2]
    b.append(T(115, 140, "Active range: how far your own muscles lift the leg", 6.4, C["forest"], "middle", 600))
    b.append(T(335, 140, "Passive range: how far the leg goes with help (strap, hands)", 6.4, C["forest"], "middle", 600))
    return svg(W, H + 4, "".join(b))


reg("rom", fig_rom(), "Active versus passive range of motion. The gap between them is the range you can reach but cannot yet control — a useful thing for a teacher to notice.", "full")


def fig_pain():
    W, H = 470, 170
    b = []
    cols = [("#6E9A5B", "GREEN · continue", "warmth, muscular effort, trembling from\nwork, a broad even stretch sensation,\nbreath steady; fades soon after", "Keep going; stay attentive."),
            ("#D9A93E", "AMBER · modify", "unfamiliar or one-sided sensation,\nsensation that builds with each\nbreath, breath becoming strained", "Back off, modify, add support;\nreassess next practice."),
            ("#B8574A", "RED · stop", "sharp, stabbing, burning or electric\npain; numbness or tingling; joint pain;\ndizziness, chest pain, breathlessness", "Come out slowly; do not resume that\npractice; refer if it persists.")]
    for i, (col, t, d, act) in enumerate(cols):
        x = 14 + i * 152
        b.append(box(x, 10, 146, 150, "#fff", col, 5, 1.1))
        b.append(box(x, 10, 146, 26, col, "none", 5))
        b.append(box(x, 26, 146, 10, col, "none", 0))
        b.append(T(x + 73, 27, t, 7.4, "#fff", "middle", 700, ls=.8))
        b.append(T(x + 10, 52, d, 6.1, C["ink"]))
        b.append(f'<line x1="{x+10}" y1="106" x2="{x+136}" y2="106" stroke="{C["line"]}"/>')
        b.append(T(x + 10, 120, act, 6.3, C["forest"], "start", 600))
    return svg(W, H, "".join(b))


reg("pain", fig_pain(), "A traffic-light guide to sensation during practice. It is a teaching tool, not a diagnostic instrument; pain is a protective output of the nervous system and "
    "does not map neatly onto tissue damage [@raja2020; @butler2013].", "full")


def fig_load():
    W, H = 470, 190
    b = []
    x0, y0, x1, y1 = 50, 20, 440, 160
    b.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{C["ink2"]}" stroke-width=".7"/>' + f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{C["ink2"]}" stroke-width=".7"/>')
    b.append(T(x1, y1 + 14, "weeks of practice →", 6, C["ink2"], "end") + T(x0 - 6, y0 + 4, "load", 6, C["ink2"], "end"))
    cap = [(x0 + k, y1 - 30 - 70 * (1 - math.exp(-k / 170))) for k in range(0, 391, 5)]
    b.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in cap) + f'" fill="none" stroke="{C["forest"]}" stroke-width="1.6"/>')
    b.append(T(x1 - 4, cap[-1][1] - 6, "tissue capacity", 6.4, C["forest"], "end", 600))
    import random
    random.seed(3)
    bars = []
    for k in range(20):
        x = x0 + 10 + k * 19
        capy = y1 - 30 - 70 * (1 - math.exp(-(x - x0) / 170))
        hgt = (y1 - capy) * (0.72 + 0.15 * random.random())
        spike = k == 13
        if spike:
            hgt = (y1 - capy) * 1.28
        bars.append(box(x, y1 - hgt, 11, hgt, C["terra"] if spike else C["gold"], "none", 1).replace('rx="1"', 'rx="1" fill-opacity=".75"'))
    b += bars
    b.append(T(x0 + 10 + 13 * 19 + 5, y1 - 136, "sudden spike:\nload exceeds capacity", 6, C["clay"], "middle", 600))
    b.append(T(x0 + 16, 34, "Gradual, repeated loading slightly\nbelow capacity lets capacity rise", 6, C["ink2"], italic=True))
    return svg(W, H, "".join(b))


reg("load", fig_load(), "A conceptual model of load and capacity. Tissues adapt to loads they meet regularly; injury risk rises when load jumps faster than capacity can adapt. "
    "The curve is illustrative, not data [@soligard2016].", "full")


def fig_motorlearning():
    W, H = 470, 130
    b = []
    st = [("Cognitive", "What do I do?", "many errors; relies on\nexplanation and demonstration", "short, clear cues;\none point at a time"),
          ("Associative", "How do I do it better?", "fewer errors; begins to\nfeel the pose from inside", "refine; invite noticing;\nreduce the number of cues"),
          ("Autonomous", "It happens by itself", "consistent; attention freed\nfor breath and awareness", "offer subtler, internal\ninquiry; less talk")]
    for i, (n, q, d, t) in enumerate(st):
        x = 12 + i * 154
        b.append(box(x, 10, 142, 108, C["goldpale"] if i != 2 else C["sagepale"], C["line"], 4, .6))
        b.append(T(x + 71, 28, n, 11, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(x + 71, 40, q, 6.3, C["golddeep"], "middle", 600, italic=True))
        b.append(T(x + 71, 56, d, 5.9, C["ink2"], "middle"))
        b.append(f'<line x1="{x+14}" y1="80" x2="{x+128}" y2="80" stroke="{C["line"]}"/>')
        b.append(T(x + 71, 94, "Teacher: " + t.split("\n")[0], 5.9, C["forest"], "middle", 600))
        b.append(T(x + 71, 103, t.split("\n")[1], 5.9, C["forest"], "middle", 600))
        if i < 2:
            b.append(arrow(x + 143, 64, x + 153, 64, C["golddeep"]))
    return svg(W, H, "".join(b))


reg("motorlearning", fig_motorlearning(), "Three stages of motor learning after Fitts and Posner, with what each asks of the teacher [@fitts1967]. Students move between stages pose by pose, not all at once.", "full")


def fig_attention():
    W, H = 360, 230
    b = []
    cx, cy, r = 180, 118, 72
    st = [("Focused attention", "resting on the breath", -90), ("Mind wandering", "caught up in thought", 0),
          ("Noticing", "“I have wandered”", 90), ("Returning", "gently shifting back", 180)]
    for n, d, a in st:
        x = cx + r * math.cos(math.radians(a))
        y = cy + r * math.sin(math.radians(a))
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="30" fill="{C["goldpale"]}" stroke="{C["gold"]}" stroke-width=".8"/>')
        b.append(T(x, y - 2, n, 7.8, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(x, y + 8, d, 5.4, C["ink2"], "middle"))
    for a in (-45, 45, 135, 225):
        a1, a2 = math.radians(a - 20), math.radians(a + 20)
        x1_, y1_ = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2_, y2_ = cx + r * math.cos(a2), cy + r * math.sin(a2)
        b.append(curve_arrow(f"M{f(x1_)},{f(y1_)} A{r},{r} 0 0 1 {f(x2_)},{f(y2_)}", C["golddeep"]))
    b.append(T(cx, cy + 3, "each return\nis a repetition", 6.6, C["teak"], "middle", italic=True))
    return svg(W, H, "".join(b))


reg("attention", fig_attention(), "The cycle of attention in focused meditation, after @hasenkamp2012. Noticing that the mind has wandered is not failure; it is the moment in which the skill is trained.")


def fig_nadishodhana():
    W, H = 470, 170
    b = []
    steps = [("Inhale", "left", 4, C["blue"]), ("Retain", "both closed", 16, C["sage"]), ("Exhale", "right", 8, C["terra"]),
             ("Inhale", "right", 4, C["terra"]), ("Retain", "both closed", 16, C["sage"]), ("Exhale", "left", 8, C["blue"])]
    x = 20
    unit = 13.8
    for i, (n, side, cnt, col) in enumerate(steps):
        w = cnt * 7.6
        b.append(box(x, 40, w - 3, 34, col, "none", 3).replace("/>", ' fill-opacity=".85"/>'))
        b.append(T(x + (w - 3) / 2, 55, n, 7, "#fff", "middle", 700))
        b.append(T(x + (w - 3) / 2, 66, side, 5.6, "#fff", "middle"))
        b.append(T(x + (w - 3) / 2, 86, f"{cnt} counts", 5.8, C["ink2"], "middle"))
        x += w
    b.append(T(20, 24, "ONE ROUND OF NĀḌĪ ŚODHANA (ANULOMA VILOMA) AT A 1 : 4 : 2 RATIO — base count 4", 6.4, C["golddeep"], "start", 700, ls=.8))
    b.append(f'<line x1="20" y1="104" x2="450" y2="104" stroke="{C["line"]}"/>')
    b.append(T(20, 122, "Beginners: omit retention and breathe in and out for equal counts (e.g. 4 : 4), then lengthen the exhalation (4 : 8).", 6.3, C["ink"]))
    b.append(T(20, 136, "Add retention only when the breath stays smooth and unhurried; the traditional 1 : 4 : 2 ratio is an advanced target, not a starting point.", 6.3, C["ink"]))
    b.append(T(20, 150, "Hand: Viṣṇu mudrā — right thumb closes the right nostril, ring (and little) finger the left.", 6.3, C["forest"], "start", 600))
    return svg(W, H, "".join(b))


reg("nadishodhana", fig_nadishodhana(), "The pattern of alternate-nostril breathing as taught in this course. Retention (*kumbhaka*) is optional and is omitted for beginners and for anyone with contraindications.", "full")


def fig_classarc():
    W, H = 480, 200
    b = []
    x0, x1, y0, y1 = 40, 420, 30, 140
    segs = [("Opening relaxation", 5, .08), ("Pranayama", 15, .18), ("Sun salutations", 10, .65), ("Leg raises", 5, .6),
            ("Headstand", 8, .75), ("Shoulderstand · plough · fish", 12, .6), ("Forward bend", 5, .45),
            ("Cobra · locust · bow", 10, .78), ("Twist", 4, .5), ("Crow", 3, .85), ("Standing forward bend · triangle", 6, .55),
            ("Final relaxation", 7, .06)]
    tot = sum(s[1] for s in segs)
    x = x0
    pts = [(x0, y1)]
    for n, mins, inten in segs:
        w = (x1 - x0) * mins / tot
        y = y1 - (y1 - y0) * inten
        pts += [(x + 2, y), (x + w - 2, y)]
        b.append(f'<line x1="{f(x)}" y1="{y1}" x2="{f(x)}" y2="{y1+4}" stroke="{C["ink2"]}" stroke-width=".5"/>')
        b.append(f'<text x="{f(x + w/2)}" y="{y1 + 8}" font-size="5.6" fill="{C["ink"]}" transform="rotate(35 {f(x + w/2)} {y1+8})">{n}</text>')
        x += w
    pts.append((x1, y1))
    d = "M" + " L".join(f"{f(a)},{f(c)}" for a, c in pts)
    b.append(f'<path d="{d} Z" fill="{C["goldpale"]}" stroke="none"/>')
    b.append(f'<path d="{d}" fill="none" stroke="{C["golddeep"]}" stroke-width="1.2" stroke-linejoin="round"/>')
    b.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{C["ink2"]}" stroke-width=".6"/>')
    b.append(T(x0 - 6, y0 + 4, "effort", 6, C["ink2"], "end") + T(x0 - 6, y1, "rest", 6, C["ink2"], "end"))
    b.append(T(x1, 16, "total ≈ 90 minutes · short relaxation between postures throughout", 6, C["ink2"], "end", italic=True))
    return svg(W, H + 40, "".join(b))


reg("classarc", fig_classarc(), "The shape of a traditional 90-minute classical class: effort rises and falls, with savasana between postures and a long final relaxation. Timings are indicative.", "full")


def fig_peakpose():
    W, H = 470, 150
    b = []
    stages = [("Arrive", "centring, breath", .1), ("Warm", "mobilise joints,\nraise heat", .4), ("Prepare", "open & strengthen the\nregions the peak needs", .7),
              ("Peak", "the key posture,\nwith options", .95), ("Counter", "neutralise; release\nwhat worked hardest", .5), ("Integrate", "twists, forward bends,\nrelaxation", .15)]
    x0, x1, y1 = 30, 450, 110
    pts = []
    for i, (n, d, h) in enumerate(stages):
        x = x0 + (x1 - x0) * (i + .5) / len(stages)
        y = y1 - 80 * h
        pts.append((x, y))
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="4" fill="{C["gold"] if n != "Peak" else C["clay"]}"/>')
        b.append(T(x, y - 8, n, 9, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(x, y1 + 14, d, 5.8, C["ink2"], "middle"))
    d = "M" + " ".join(f"{f(x)},{f(y)}" for x, y in pts)
    b.insert(0, f'<path d="{d}" fill="none" stroke="{C["golddeep"]}" stroke-width="1" stroke-dasharray="3 2"/>')
    return svg(W, H, "".join(b))


reg("peakpose", fig_peakpose(), "The arc of a peak-pose class. Everything before the peak prepares for it; everything after it restores balance.", "full")


def fig_classroom():
    W, H = 470, 220
    b = []
    b.append(box(20, 20, 300, 180, "#FBF7EF", C["line"], 4, .7))
    for r in range(3):
        for c in range(4):
            x = 44 + c * 68 + (r % 2) * 14
            y = 50 + r * 50
            b.append(box(x, y, 40, 16, "#8FA7A3", "none", 2).replace("/>", ' fill-opacity=".55"/>'))
    b.append(box(140, 26, 60, 10, C["gold"], "none", 2))
    b.append(T(170, 33.5, "teacher’s mat", 5.4, "#fff", "middle", 600))
    for (x, y, lab) in [(170, 44, "1"), (310, 110, "2"), (30, 110, "3"), (170, 196, "4")]:
        b.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{C["forest"]}"/>' + T(x, y + 2.5, lab, 6.5, "#fff", "middle", 700))
    b.append(f'<path d="M170,44 L60,190 M170,44 L300,190" stroke="{C["clay"]}" stroke-width=".5" stroke-dasharray="3 2"/>')
    notes = ["1  Front: demonstrate; see faces and breath", "2, 3  Sides: see sagittal-plane alignment —\n    knees, pelvis, spine in lunges and folds",
             "4  Back: see the whole room as students see it;\n    best place to check what they understood", "Staggered mats let every student see you\nand let you see every student.",
             "Move while you teach; never teach a\nwhole class from your own mat."]
    for i, t in enumerate(notes):
        b.append(T(334, 40 + i * 34, t, 6.1, C["ink"] if i < 3 else C["teak"], italic=i >= 3))
    return svg(W, H, "".join(b))


reg("classroom", fig_classroom(), "Teaching positions and sight lines in a group class. Circulating between these positions is how you observe; staying on your own mat is how you perform.", "full")


def fig_consent():
    W, H = 470, 120
    b = []
    steps = [("Ask", "at the start of class:\nconsent card or clear\nopt-in/opt-out"), ("Check", "just before touch:\n“May I offer a hand\nhere?”"),
             ("Touch", "only as agreed; clear,\nbrief, purposeful, on\nsafe areas"), ("Check again", "“How is that?”\nready to stop at once"),
             ("Release", "slowly and clearly;\nconsent can be\nwithdrawn at any time")]
    for i, (n, d) in enumerate(steps):
        x = 12 + i * 92
        b.append(box(x, 14, 82, 94, C["goldpale"] if i % 2 == 0 else C["sagepale"], C["line"], 4, .6))
        b.append(T(x + 41, 32, n, 10, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(x + 41, 48, d, 5.8, C["ink2"], "middle"))
        if i < 4:
            b.append(arrow(x + 83, 60, x + 91, 60, C["golddeep"]))
    return svg(W, H, "".join(b))


reg("consent", fig_consent(), "A consent process for hands-on assistance. Consent given at the start of class does not cover every touch; it is re-checked moment to moment.", "full")


def fig_cuestructure():
    W, H = 470, 110
    b = []
    parts = [("Breath", "“Inhale…”"), ("Body part", "“…lift the chest…”"), ("Direction / action", "“…forward and up,…”"), ("Anchor", "“…keeping the\npelvis heavy.”")]
    for i, (n, d) in enumerate(parts):
        x = 14 + i * 114
        b.append(box(x, 14, 104, 70, "#fff", C["gold"], 4, .8))
        b.append(T(x + 52, 34, n, 10, C["forest"], "middle", 600, family="Cormorant"))
        b.append(T(x + 52, 52, d, 6.6, C["teak"], "middle", italic=True))
        if i < 3:
            b.append(T(x + 109, 52, "+", 11, C["golddeep"], "middle", 600))
    b.append(T(14, 102, "One cue = one breath + one body part + one clear direction (+ what stays still). Then pause and let students do it.", 6.3, C["ink2"]))
    return svg(W, H, "".join(b))


reg("cuestructure", fig_cuestructure(), "The anatomy of a clear verbal cue.", "full")




# --------------------------------------------------------------------- muscle location sketches
def muscle_sketch(pose, musc, labels=(), w=None):
    return draw(pose, muscles=musc, labels=labels, floor=False, mat=False)


def fig_hamstring_psoas():
    W, H = 470, 250
    s1 = draw(P["tadasana"], muscles=[(("lt", 0.0, "post"), ("sh1", 0.06, "post"), 3.4, "stretch")],
              labels=[(("th1", 0.1, "post"), "ischial tuberosity", -14, -6), (("sh1", 0.06, "post"), "below the knee", -14, 10)], floor=False, mat=False)
    s2 = draw(P["tadasana"], muscles=[(("lt", 0.7, "post", -0.1), ("th1", 0.1, "mid"), 3.0, "active")],
              labels=[(("lt", 0.75, "mid"), "T12–L5 vertebrae", 16, -8), (("th1", 0.12, "mid"), "lesser trochanter", 16, 12)], floor=False, mat=False)
    s1, s2 = ghost(s1), ghost(s2)
    i1, h1 = embed(s1, 50, 6, 118)
    i2, h2 = embed(s2, 270, 6, 118)
    b = [i1, i2]
    b.append(T(115, 246, "Hamstrings (posterior thigh)", 7, C["clay"], "middle", 600))
    b.append(T(335, 246, "Psoas major (deep, in front of the hip)", 7, C["blue"], "middle", 600))
    return svg(W, H + 6, "".join(b))


reg("hamstring_psoas", fig_hamstring_psoas(), "Location sketches of two muscles that dominate yoga conversations. The hamstrings cross the back of hip and knee; the psoas runs from the lumbar spine, "
    "in front of the hip joint, to the femur. Sketches are schematic; see the muscle atlas for attachments.", "full")


# --------------------------------------------------------------------- sequence strip helper
def sequence_strip(names, labels, numbers=True, w=470, per_row=6, size=66):
    """Row(s) of pose icons with captions, used for Surya Namaskar and class charts."""
    import re
    rows = (len(names) + per_row - 1) // per_row
    cell_w = w / per_row
    H = rows * (size + 30) + 6
    b = []
    for i, (n, lab) in enumerate(zip(names, labels)):
        r, c = divmod(i, per_row)
        x = c * cell_w + 4
        y = r * (size + 30) + 4
        b.append(box(x, y, cell_w - 8, size, "#FAF6EE", "none", 4))
        s = draw(P[n] if isinstance(n, str) else n, floor=True, pad=5)
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
        sc = min((cell_w - 16) / vb[2], (size - 8) / vb[3])
        ww, hh = vb[2] * sc, vb[3] * sc
        inner, _ = embed(s, x + (cell_w - 8 - ww) / 2, y + size - hh - 3, ww)
        b.append(inner)
        if numbers:
            b.append(f'<circle cx="{f(x+9)}" cy="{f(y+9)}" r="6" fill="{C["forest"]}"/>' + T(x + 9, y + 11.4, str(i + 1), 6.4, "#fff", "middle", 700))
        for k, ln in enumerate(lab.split("\n")):
            b.append(T(x + (cell_w - 8) / 2, y + size + 10 + k * 8, ln, 6 if k == 0 else 5.5, C["forest"] if k == 0 else C["ink2"], "middle", 600 if k == 0 else 400))
    return svg(w, H, "".join(b))


SURYA = [("pranamasana", "Prayer\nexhale"), ("hasta_uttanasana", "Arms up, arch\ninhale"), ("padahastasana", "Hands to feet\nexhale"),
         ("lunge", "Lunge, right leg back\ninhale"), ("plank", "Plank\nretain"), ("ashtanga_namaskara", "Knees, chest, chin\nexhale"),
         ("bhujangasana", "Cobra\ninhale"), ("adho_mukha", "Inverted V\nexhale"), ("lunge", "Lunge, right foot forward\ninhale"),
         ("padahastasana", "Hands to feet\nexhale"), ("hasta_uttanasana", "Arms up, arch\ninhale"), ("pranamasana", "Prayer\nexhale")]
reg("surya", sequence_strip([n for n, _ in SURYA], [l for _, l in SURYA], per_row=6, size=70),
    "Sūrya Namaskār as taught in this course: twelve positions, each linked to one breath. The right leg steps back in position 4 and forward in position 9; "
    "the next round begins with the left leg. The lunge figures show the stepping leg in the lighter tone.", "full")

TWELVE = [("sirsasana", "1 Headstand\nŚīrṣāsana"), ("sarvangasana", "2 Shoulderstand\nSarvāṅgāsana"), ("halasana", "3 Plough\nHalāsana"),
          ("matsyasana", "4 Fish\nMatsyāsana"), ("paschimottanasana", "5 Forward bend\nPaścimottānāsana"), ("bhujangasana", "6 Cobra\nBhujaṅgāsana"),
          ("salabhasana", "7 Locust\nŚalabhāsana"), ("dhanurasana", "8 Bow\nDhanurāsana"), ("ardha_matsyendrasana", "9 Half spinal twist\nArdha Matsyendrāsana"),
          ("kakasana", "10 Crow\nKākāsana"), ("padahastasana", "11 Standing forward bend\nPāda Hastāsana"), ("trikonasana", "12 Triangle\nTrikoṇāsana")]
reg("twelve", sequence_strip([n for n, _ in TWELVE], [l.split(" ", 1)[1] for _, l in TWELVE], per_row=6, size=74),
    "The twelve basic postures of the classical sequence in their traditional order. Savāsana is taken between postures.", "full")
