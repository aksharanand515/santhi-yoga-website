"""
Figures for the manual.  Every figure is drawn in code as SVG so that labels are always
legible, colours match the book, and anatomy can be checked against the text.

Anatomical figures are rendered from real bone geometry (anatfigs.py); diagrams that remain
schematic say so in their captions.  Nothing here is traced from a copyrighted source.
"""
import math

from posefig import ACTIVE
import fig3dhtml as F3
import photohtml as PH

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


# centre-line points of the subtle-body diagrams, on the neutral body, attached to spine bones
SUBTLE = {"base": ("spine05", [0, -0.02, 0.855]), "sacral": ("spine05", [0, -0.035, 0.935]),
          "navel": ("spine03", [0, -0.05, 1.03]), "heart": ("spine01", [0, -0.04, 1.255]),
          "throat": ("neck02", [0, -0.06, 1.445]), "brow": ("head", [0, -0.10, 1.595]),
          "crown": ("head", [0, -0.05, 1.690]), "chest": ("spine01", [0, -0.04, 1.20]),
          "pelvis": ("spine05", [0, -0.03, 0.90]), "head": ("head", [0, -0.05, 1.56])}


def seated_figure(x, y, h, key="meditation_front", palette="light"):
    """Seated 3D figure of height h at (x, y); returns (svg <image>, width, M) where M maps a SUBTLE
    point name to SVG coordinates."""
    info = F3.render(key, 900, palette=palette)
    w = h * info["w"] / info["h"]
    el, _, proj = F3.svg_image(info, x, y, w)
    P3 = F3.fig3d.points(key, SUBTLE)
    return el, w, (lambda name: proj(P3[name]))


def fig_chakras():
    W, H = 470, 330
    b = []
    el, w, M = seated_figure(80, 24, 290)
    b.append(el)
    base, navel, heart, throat, brow, crown = (M(k) for k in ("base", "navel", "heart", "throat", "brow", "crown"))
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
    b.append(f'<line x1="{f(sx)}" y1="{f(bot)}" x2="{f(sx)}" y2="{f(crown[1])}" stroke="{C["gold"]}" stroke-width="2.4" stroke-linecap="round" stroke-opacity=".9"/>')
    b.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts_i) + f'" fill="none" stroke="{C["blue"]}" stroke-width="1.1"/>')
    b.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts_p) + f'" fill="none" stroke="{C["terra"]}" stroke-width="1.1"/>')
    ch = [("Sahasrāra", "crown · “thousand-petalled”", crown, "#9C7BB0"),
          ("Ājñā", "between the eyebrows · 2 petals", brow, "#6F6AA8"),
          ("Viśuddha", "throat · 16 petals · space", throat, "#4F8BB0"),
          ("Anāhata", "heart · 12 petals · air", heart, "#6E9A5B"),
          ("Maṇipūra", "navel · 10 petals · fire", navel, "#D9A93E"),
          ("Svādhiṣṭhāna", "sacral · 6 petals · water", M("sacral"), "#D98A4E"),
          ("Mūlādhāra", "base of spine · 4 petals · earth", base, "#B8574A")]
    for i, (n_, d, pt, col) in enumerate(ch):
        b.append(f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="5.2" fill="{col}" stroke="#FFFEFA" stroke-width="1.2"/>')
        ty = 36 + i * 40
        b.append(f'<line x1="{f(pt[0]+6)}" y1="{f(pt[1])}" x2="{350}" y2="{f(ty-3)}" stroke="{C["golddeep"]}" stroke-width=".45" stroke-opacity=".7"/>')
        b.append(T(354, ty, n_, 10, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(354, ty + 10, d, 6, C["ink2"]))
    # nadi legend
    b.append(T(10, 40, "Nāḍīs", 10, C["forest"], "start", 600, family="Cormorant"))
    b.append(f'<line x1="10" y1="54" x2="26" y2="54" stroke="{C["gold"]}" stroke-width="2.4"/>' + T(30, 56, "Suṣumṇā · central", 6))
    b.append(f'<line x1="10" y1="66" x2="26" y2="66" stroke="{C["blue"]}" stroke-width="1.2"/>' + T(30, 68, "Iḍā · “lunar”", 6))
    b.append(f'<line x1="10" y1="78" x2="26" y2="78" stroke="{C["terra"]}" stroke-width="1.2"/>' + T(30, 80, "Piṅgalā · “solar”", 6))
    b.append(T(10, 250, "The crossing, spiral\nform is a common\nmodern rendering;\nmany texts simply\nplace iḍā and\npiṅgalā to the left\nand right of the\ncentral channel.", 5.8, C["ink2"], italic=True))
    return svg(W, H, "".join(b))


reg("chakras", fig_chakras(),
    "The six *cakra*s and *sahasrāra* as commonly taught in modern yoga, following the arrangement of the 16th-century "
    "*Ṣaṭcakranirūpaṇa* [@avalon1919]. Earlier texts describe different numbers and placements of cakras [@mallinson2017]. "
    "This is a map of traditional meditative experience; no anatomical structures corresponding to cakras or nāḍīs have been identified.", "")


def fig_vayus():
    W, H = 460, 300
    b = []
    el, w, M = seated_figure(60, 14, 272)
    b.append(el)
    cx = M("heart")[0]
    regions = [("Udāna", "throat & head · upward movement;\nspeech, effort, “rising” at death", M("throat"), 16, 14, "#4F8BB0"),
               ("Prāṇa", "chest · inward movement;\nbreathing in, taking in", M("chest"), 34, 26, "#6E9A5B"),
               ("Samāna", "navel region · balancing, “equalising”;\ndigestion and assimilation", M("navel"), 30, 16, "#D9A93E"),
               ("Apāna", "pelvis · downward & outward;\nelimination, exhalation, birth", M("pelvis"), 36, 18, "#B8574A")]
    ys = [40, 96, 152, 208]
    for (n, d, (px, py), rx, ry, col), ty in zip(regions, ys):
        b.append(f'<ellipse cx="{f(cx)}" cy="{f(py)}" rx="{rx}" ry="{ry}" fill="{col}" fill-opacity=".30" stroke="{col}" stroke-width=".8"/>')
        b.append(f'<line x1="{f(cx+rx)}" y1="{f(py)}" x2="338" y2="{ty-3}" stroke="{C["golddeep"]}" stroke-width=".45" stroke-opacity=".7"/>')
        b.append(T(342, ty, n, 11, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(342, ty + 10, d, 5.9, C["ink2"]))
    b.append(T(342, 262, "Vyāna", 11, C["forest"], "start", 600, family="Cormorant"))
    b.append(T(342, 272, "pervades the whole body; circulation,\nco-ordination, outward distribution", 5.9, C["ink2"]))
    b.append(f'<rect x="{f(60 + 4)}" y="10" width="{f(w - 8)}" height="280" rx="34" fill="none" stroke="#9C7BB0" stroke-width=".8" stroke-dasharray="3 2"/>')
    up_ = M("throat")
    b.append(arrow(cx + 14, up_[1] - 2, cx + 14, up_[1] - 26, "#4F8BB0", 1))
    lo = M("pelvis")
    b.append(arrow(cx + 16, lo[1] + 4, cx + 16, lo[1] + 26, "#B8574A", 1))
    return svg(W, H, "".join(b))


reg("vayus", fig_vayus(), "The five *vāyu*s (“winds”) of *prāṇa* as usually taught. Texts disagree on their exact seats and functions; "
    "the dashed outline stands for *vyāna*, which pervades the whole body. These are traditional categories of experience, "
    "not physiological systems.")


def fig_bandhas():
    W, H = 440, 250
    b = []
    el, w, M = seated_figure(40, 12, 226, key="sukhasana_side")
    b.append(el)
    P3 = F3.fig3d.points("sukhasana_side", {"jal": ("neck02", [0, -0.075, 1.445]), "udd": ("spine02", [0, -0.10, 1.10]),
                                           "mul": ("spine05", [0, -0.015, 0.86])})
    info = F3.render("sukhasana_side", 900, palette="light")
    _, _, proj = F3.svg_image(info, 40, 12, w)
    items = [("Jālandhara bandha", "chin lock: chin drawn towards the\nsternum, back of neck lengthened", proj(P3["jal"]), 40),
             ("Uḍḍīyāna bandha", "abdominal lock: after exhalation, the\nabdomen is drawn in and up", proj(P3["udd"]), 108),
             ("Mūla bandha", "root lock: gentle contraction and lift\nof the pelvic floor / perineum", proj(P3["mul"]), 176)]
    for n, d, pt, ty in items:
        b.append(f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="7" fill="{C["gold"]}" fill-opacity=".45" stroke="{C["golddeep"]}" stroke-width="1"/>')
        b.append(f'<line x1="{f(pt[0]+7)}" y1="{f(pt[1])}" x2="282" y2="{ty-3}" stroke="{C["golddeep"]}" stroke-width=".5"/>')
        b.append(T(286, ty, n, 10.5, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(286, ty + 10, d, 5.9, C["ink2"]))
    b.append(T(286, 232, "Mahā bandha = all three held together\n(Haṭha Yoga Pradīpikā 3.19–25)", 5.9, C["golddeep"], italic=True))
    return svg(W, H, "".join(b))


reg("bandhas", fig_bandhas(), "The three principal *bandha*s shown on a seated practitioner (side view; the locks themselves are internal actions). Uḍḍīyāna bandha is practised only on an empty stomach and "
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
    info = F3.render("front", 900, palette="light")
    w = 200 * info["w"] / info["h"]
    x0 = 75 - w / 2
    el, h, proj = F3.svg_image(info, x0, 26, w)
    # planes around the front figure (oblique projection), drawn behind and in front of it
    cx, top, bot = 75, 20, 232
    sag = f'<polygon points="{cx},{top} {cx+24},{top-12} {cx+24},{bot-12} {cx},{bot}" fill="{C["terra"]}" fill-opacity=".20" stroke="{C["terra"]}" stroke-width=".7"/>'
    fro = f'<polygon points="{cx-58},{top+6} {cx+58},{top+6} {cx+58},{bot+6} {cx-58},{bot+6}" fill="{C["blue"]}" fill-opacity=".10" stroke="{C["blue"]}" stroke-width=".7"/>'
    zt = proj([0, 0, 0.93])[1]
    tra = f'<polygon points="{cx-62},{f(zt+6)} {cx+44},{f(zt+6)} {cx+66},{f(zt-6)} {cx-40},{f(zt-6)}" fill="{C["gold"]}" fill-opacity=".30" stroke="{C["golddeep"]}" stroke-width=".7"/>'
    b += [fro, el, sag, tra]
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
    W, H = 470, 250
    b = []
    info = F3.render("front", 900, palette="light")
    w = 216 * info["w"] / info["h"]
    el, h, proj = F3.svg_image(info, 100 - w / 2, 16, w)
    b.append(el)
    info2 = F3.render("tadasana", 900, palette="light")
    w2 = 216 * info2["w"] / info2["h"]
    el2, h2, proj2 = F3.svg_image(info2, 318 - w2 / 2, 16, w2)
    b.append(el2)
    b.append(arrow(22, 120, 22, 30, C["golddeep"]) + arrow(22, 130, 22, 220, C["golddeep"]))
    b.append(T(18, 24, "Superior (cranial)", 6.3, C["ink"], "start", 600) + T(18, 234, "Inferior (caudal)", 6.3, C["ink"], "start", 600))
    P3 = F3.fig3d.points("front", {"mid": ("spine02", [0, -0.1, 1.15]), "elL": "elbow_L"})
    mx, my = proj(P3["mid"])
    # medial / lateral: from the midline out past the figure's left hand (image right)
    b.append(arrow(mx + 2, my, mx + 74, my, C["blue"]) + arrow(mx + 30, my, mx + 4, my, C["blue"]))
    b.append(T(mx + 76, my + 2, "Lateral", 6.3, C["blue"], "start", 600) + T(mx + 6, my - 5, "Medial", 6.3, C["blue"], "start", 600))
    # proximal -> distal along the figure's left arm (image right)
    ex, ey = proj(P3["elL"])
    b.append(arrow(ex + 14, ey - 16, ex + 24, ey + 30, C["clay"], m="arrt"))
    b.append(T(ex + 28, ey + 4, "Proximal → distal\n(towards the\nextremity)", 6, C["clay"], "start", 600))
    # anterior / posterior on the side figure (it faces image right)
    P4 = F3.fig3d.points("tadasana", {"c": ("spine02", [0, -0.02, 1.15])})
    cx2, cy2 = proj2(P4["c"])
    b.append(arrow(cx2 + 24, cy2, cx2 + 60, cy2, C["golddeep"]) + arrow(cx2 - 24, cy2, cx2 - 60, cy2, C["golddeep"]))
    b.append(T(cx2 + 64, cy2 + 2, "Anterior (ventral)", 6.3, C["ink"], "start", 600) + T(cx2 - 64, cy2 + 2, "Posterior (dorsal)", 6.3, C["ink"], "end", 600))
    b.append(T(388, 170, "Superficial ↔ deep:\ncloser to / further\nfrom the surface", 6, C["teak"], italic=True))
    b.append(T(388, 210, "Ipsilateral = same side\nContralateral = opposite side", 6, C["teak"], italic=True))
    return svg(W, H, "".join(b))


reg("directions", fig_directions(), "Directional terms are always relative to anatomical position, even when the body is upside down: in headstand the head is still *superior* to the feet.")


def joint_panel(label, pose_a, pose_b, note):
    return label, pose_a, pose_b, note


def fig_jointmoves():
    W, H = 500, 330
    b = []
    FR = dict(view=(90, 2))
    panels = [
        ("Hip flexion / extension", [dict(hip_L=(90, 0, 0), knee_L=90, free=[("root", 1, -8, 8)], contacts=[("heel_R", "z", 0), ("ball_R", "z", 0)]),
                                     dict(hip_L=(-25, 0, 0), ankle_L=(-20, 0), contacts=[("heel_R", "z", 0), ("ball_R", "z", 0)])], "sagittal"),
        ("Shoulder flexion / extension", [dict(shoulder_L=(170, 4, 0), shoulder_R=(0, 4, 0), hand="flat"),
                                          dict(shoulder_L=(-50, 4, 0), shoulder_R=(0, 4, 0), hand="flat")], "sagittal"),
        ("Spinal flexion / extension", [dict(lumbar=(28, 0, 0), thoracic=(30, 0, 0), cervical=(25, 0, 0), head=(10, 0, 0), shoulder=(56, 4, 0)),
                                        dict(lumbar=(-22, 0, 0), thoracic=(-14, 0, 0), cervical=(-25, 0, 0), head=(-10, 0, 0), shoulder=(-30, 4, 0))], "sagittal"),
        ("Hip abduction / adduction", [FR | dict(hip_L=(0, 40, 0), contacts=[("heel_R", "z", 0), ("ball_R", "z", 0)]),
                                       FR | dict(hip_L=(12, -18, 0), contacts=[("heel_R", "z", 0), ("ball_R", "z", 0)])], "frontal"),
        ("Shoulder abduction", [FR | dict(shoulder=(0, 90, 0), hand="flat"), FR | dict(shoulder=(0, 172, 0), hand="flat")], "frontal"),
        ("Spinal lateral flexion", [FR | dict(lumbar=(0, 14, 0), thoracic=(0, 16, 0), cervical=(0, 12, 0)),
                                    FR | dict(lumbar=(0, -14, 0), thoracic=(0, -16, 0), cervical=(0, -12, 0))], "frontal"),
    ]
    for i, (lab, poses, plane) in enumerate(panels):
        col = i % 3
        row = i // 3
        x = 14 + col * 162
        y = 20 + row * 150
        b.append(box(x, y, 152, 138, "#FBF7EF", C["line"], 4, .5))
        b.append(T(x + 8, y + 14, lab, 9.4, C["forest"], "start", 600, family="Cormorant"))
        b.append(T(x + 144, y + 25, plane + " plane", 5.6, C["terra"] if plane == "sagittal" else C["blue"], "end", 600))
        for k, ov in enumerate(poses):
            ov = dict(ov)
            if "free" not in ov and "contacts" in ov:
                ov["free"] = []
            info = F3.render("tadasana", 520, palette="light", overrides=ov)
            # same scale in every panel: 1.9 m of body height -> 104 units
            sc = 104 / 1.95
            wv, hv = info["span"][0] * sc, info["span"][1] * sc
            if wv > 70:
                sc *= 70 / wv
                wv, hv = 70, hv * 70 / wv
            el, _, _ = F3.svg_image(info, x + 10 + k * 72 + (62 - wv) / 2, y + 128 - hv, wv)
            b.append(el)
    b.append(T(14, 324, "Rotation (internal/external, spinal rotation) occurs in the transverse plane and is shown in the twist and hip-rotation figures later in this section.", 6, C["ink2"], italic=True))
    return svg(W, H + 4, "".join(b))


reg("jointmoves", fig_jointmoves(), "Basic joint movements illustrated with the manual’s figure. In each panel the left figure shows the first-named movement.", "full")


import anatfigs as AF  # noqa: E402  (3D anatomy figures; uses the helpers above)

reg("spine", AF.fig_spine(), "The vertebral column in lateral view (anterior to the right), rendered from the bone geometry of a validated musculoskeletal model [@rajagopal2016]. Typical counts are 7 cervical, 12 thoracic and 5 lumbar vertebrae, "
    "a sacrum of 5 fused segments and a small coccyx; variation exists between individuals [@moore2018].", "half")


reg("vertebra", AF.fig_vertebra(), "A lumbar vertebra from above and a spinal motion segment from the side. Each segment moves at three joints: the "
    "intervertebral disc in front and the paired facet joints behind [@bogduk2005].", "full")


reg("pelvis", AF.fig_pelvis(), "The pelvis and hip joints, anterior view. The pelvis is a ring of two hip bones and the sacrum; the femoral head sits deep in the acetabulum. "
    "Depth and orientation of the socket, and the angle of the femoral neck, vary considerably between people [@clark2016; @neumann2017].", "full")


reg("pelvictilt", AF.fig_pelvictilt(), "Pelvic tilt and its effect on the lumbar curve: the pelvis rotates about the hip joints and the lumbar spine follows. Much “alignment” teaching in forward bends and backbends is really about where the pelvis is allowed to move.")


reg("shoulder", AF.fig_shoulder(), "The shoulder girdle is a chain: sternum → clavicle → scapula → humerus. Raising the arms overhead needs both glenohumeral movement and "
    "upward rotation of the scapula (scapulohumeral rhythm) [@neumann2017].", "full")


reg("knee", AF.fig_knee(), "Right knee, anterior view with the patella removed; the femur is drawn semi-transparent so that the cruciate ligaments in the intercondylar notch are visible (ligaments and menisci modelled at their standard attachments). The menisci deepen the flat tibial plateau; the cruciate and collateral ligaments limit "
    "forward/backward and side-to-side movement of the tibia on the femur [@moore2018].")


reg("foot", AF.fig_foot(), "The foot as a foundation: the medial arch (left) and the three weight-bearing points often cued in standing poses (right). Arch height varies widely "
    "and a low arch is not in itself a problem.", "full")


reg("hand", AF.fig_hand(), "Weight-bearing through the hands. Plank and crow place the wrist near the end of its extension range under load; commonly reported active wrist extension "
    "is around 70°, though individuals differ [@neumann2017]. Spreading load and building tolerance gradually are the practical responses.", "full")


reg("ribs", AF.fig_ribs(), "Rib movement during inhalation (arrows). Upper ribs mainly increase the front-to-back depth of the chest; lower ribs mainly increase its width [@calais2006; @west2020].", "full")


reg("diaphragm", AF.fig_diaphragm(), "The diaphragm in exhalation and inhalation (front view; the rib cage is drawn translucent and the dome is modelled). Contracting, the dome descends and flattens, lower ribs widen, and abdominal "
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
    info = F3.render("paschimottanasana", 1000, muscles=dict(
        work=["rectus_abdominis", "iliopsoas"], stretch=["hamstrings", "gastrocnemius", "erector_spinae", "gluteus_maximus"]))
    w = 262
    el, h, proj = F3.svg_image(info, 14, 190 - w * info["h"] / info["w"], w)
    b = [el]
    b.append(T(290, 40, "Tension (tensile load)", 10, C["clay"], "start", 600, family="Cormorant"))
    b.append(T(290, 52, "tissues on the convex side are pulled:\nhamstrings, calf, back of the trunk,\nposterior hip and spinal ligaments", 6, C["ink2"]))
    b.append(T(290, 98, "Compression", 10, C["blue"], "start", 600, family="Cormorant"))
    b.append(T(290, 110, "tissues on the concave side are pressed\ntogether: front of the hip, abdomen,\nanterior discs when the spine rounds", 6, C["ink2"]))
    b.append(T(290, 156, "When a fold stops, the limit may be\ntension (felt behind) or compression\n(felt in front, e.g. belly meets thighs).", 6.1, C["teak"], italic=True))
    return svg(W, H, "".join(b))


reg("tension", fig_tension(), "Tension and compression in a seated forward bend. Terracotta: tissues lengthening under load; blue: the region compressed at the front of the hip and abdomen. Recognising which "
    "kind of limit a student has reached changes what you teach next [@clark2016].", "full")


def fig_rom():
    W, H = 470, 150
    b = []
    for (key, ov, x0) in (("leg_raise", dict(hip_R=(58, 0, 0)), 20), ("supta_padangusthasana", dict(hip_R=(96, 0, 0)), 245)):
        info = F3.render(key, 900, overrides=ov)
        w = 200
        hh = w * info["h"] / info["w"]
        if hh > 118:
            w, hh = w * 118 / hh, 118
        el, _, _ = F3.svg_image(info, x0 + (205 - w) / 2, 124 - hh, w)
        b.append(el)
    b.append(T(122, 140, "Active range: how far your own muscles lift the leg", 6.4, C["forest"], "middle", 600))
    b.append(T(347, 140, "Passive range: how far the leg goes with help (strap, hands)", 6.4, C["forest"], "middle", 600))
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
reg("hamstring_psoas", AF.fig_hamstring_psoas(), "Two muscles that dominate yoga conversations, drawn along their lines of action in the same musculoskeletal model [@rajagopal2016]. The hamstrings cross the back of hip and knee; the psoas runs from the lumbar spine, "
    "in front of the hip joint, to the femur. See the muscle atlas for attachments.", "full")


# --------------------------------------------------------------------- sequence strip helper
def sequence_strip(names, labels, numbers=True, w=470, per_row=6, size=66):
    """Row(s) of pose images with captions, used for Surya Namaskar and class charts."""
    rows = (len(names) + per_row - 1) // per_row
    cell_w = w / per_row
    H = rows * (size + 30) + 6
    b = []
    for i, (n, lab) in enumerate(zip(names, labels)):
        r, c = divmod(i, per_row)
        x = c * cell_w + 4
        y = r * (size + 30) + 4
        if PH.has(n):
            b.append(box(x, y, cell_w - 8, size, C["paper"], C["line"], 4, .35))
            b.append(PH.photo_svg(n, x + 2, y + 2, cell_w - 12, size - 4, "strip"))
        else:
            b.append(box(x, y, cell_w - 8, size, "#FAF6EE", "none", 4))
            info = F3.render(n, 420)
            bw, bh = cell_w - 16, size - 10
            sc = min(bw / info["w"], bh / info["h"])
            ww, hh = info["w"] * sc, info["h"] * sc
            el, _, _ = F3.svg_image(info, x + (cell_w - 8 - ww) / 2, y + size - hh - 4, ww)
            b.append(el)
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
    "the next round begins with the left leg.", "full")

TWELVE = [("sirsasana", "1 Headstand\nŚīrṣāsana"), ("sarvangasana", "2 Shoulderstand\nSarvāṅgāsana"), ("halasana", "3 Plough\nHalāsana"),
          ("matsyasana", "4 Fish\nMatsyāsana"), ("paschimottanasana", "5 Forward bend\nPaścimottānāsana"), ("bhujangasana", "6 Cobra\nBhujaṅgāsana"),
          ("salabhasana", "7 Locust\nŚalabhāsana"), ("dhanurasana", "8 Bow\nDhanurāsana"), ("ardha_matsyendrasana", "9 Half spinal twist\nArdha Matsyendrāsana"),
          ("kakasana", "10 Crow\nKākāsana"), ("padahastasana", "11 Standing forward bend\nPāda Hastāsana"), ("trikonasana", "12 Triangle\nTrikoṇāsana")]
reg("twelve", sequence_strip([n for n, _ in TWELVE], [l.split(" ", 1)[1] for _, l in TWELVE], per_row=6, size=74),
    "The twelve basic postures of the classical sequence in their traditional order. Savāsana is taken between postures.", "full")
