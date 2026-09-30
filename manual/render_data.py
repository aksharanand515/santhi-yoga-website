"""
Renderers for the structured parts of the manual (data/*.yaml):
asana monographs, the muscle atlas, asana–anatomy mapping tables, glossaries,
pose indexes, the cue library and inline sequence strips.

Each render_<name>(arg, chapter, numbered, xref) returns an HTML string.  Markdown inside
YAML values is rendered with the same citation/evidence-badge processing as the chapters.
"""
import html
import pathlib
import re
import unicodedata

import markdown
import yaml

from poses import P
import figures
import fig3dhtml as F3
import photohtml as PH

DATA = pathlib.Path(__file__).parent / "data"
_cache = {}


def load(name):
    if name not in _cache:
        _cache[name] = yaml.safe_load((DATA / f"{name}.yaml").read_text(encoding="utf-8"))
    return _cache[name]


def md(s, inline=False):
    import build  # late import to share citation handling
    if s is None:
        return ""
    s = build.process_inline(build.process_citations(str(s)))
    out = markdown.markdown(s, extensions=["smarty", "sane_lists", "tables"])
    if inline:
        out = out.removeprefix("<p>").removesuffix("</p>")
    return out


def ul(items, cls=""):
    if not items:
        return ""
    c = f' class="{cls}"' if cls else ""
    return f"<ul{c}>" + "".join(f"<li>{md(i, True)}</li>" for i in items) + "</ul>"


def slug(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ------------------------------------------------------------------------------ asanas
def render_asana(arg, ch, numbered, xref):
    data = {a["id"]: a for a in load("asanas")}
    a = data[arg.strip()]
    n = a.get("number", "")
    photo = PH.has(a["fig"])
    main = (PH.photo_img(a["fig"], 92, 84, "hero") if photo
            else F3.img(a["fig"], 92, 80, px=1100, muscles=a.get("muscles3d")))
    label = numbered(ch, "fig")
    xref[f"fig:asana-{a['id']}"] = f"Figure {label}"
    facts = "".join(f"<dt>{k}</dt><dd>{md(v, True)}</dd>" for k, v in a["facts"].items())
    H = []
    H.append(f'<section class="asana" id="asana-{a["id"]}">')
    H.append('<div class="asana-head">'
             f'<div class="asana-no">{n}</div><div class="asana-names">'
             f'<h2 class="asana-sk nonum">{html.escape(a["sanskrit"])}</h2>'
             f'<div class="asana-en">{html.escape(a["english"])}</div></div>'
             f'<div><div class="asana-dev">{a.get("devanagari", "")}</div>'
             f'<div class="asana-pron">{md(a.get("pronunciation", ""), True)}</div></div></div>')
    legend = ""
    if a.get("muscles3d") and not photo:
        legend = (f' <span style="color:{F3.WORK}">■</span> working (contracting) '
                  f'<span style="color:{F3.STRETCH}">■</span> lengthening')
    H.append('<div class="asana-hero"><figure class="fig-main' + (' has-photo' if photo else '') + '" id="fig-asana-' + a["id"] + '">' + main +
             f'<figcaption><span class="fignum">Figure {label}</span> {md(a.get("photo_caption" if photo else "caption", a["english"]) or a.get("caption"), True)}{legend}</figcaption></figure>'
             f'<dl class="asana-facts">{facts}</dl></div>')
    H.append(f'<p class="lead">{md(a["meaning"], True)}</p>')

    def sec(num, title, body):
        H.append(f'<h3><span class="h3n">{num}</span>{title}</h3>{body}')

    sec("01", "Purpose", md(a["purpose"]))
    sec("02", "Preparation", ul(a["preparation"]))
    steps = "".join(f"<li>{md(s, True)}</li>" for s in a["technique"])
    sec("03", "Technique, step by step", f'<ol class="asana-steps">{steps}</ol>')
    sec("04", "Breathing", md(a["breathing"]))
    sec("05", "Alignment", ul(a["alignment"]))
    # anatomy
    jt = "".join(f"<tr><td>{md(r[0], True)}</td><td>{md(r[1], True)}</td></tr>" for r in a["joints"])
    sec("06", "Major joints and their positions",
        f'<table class="kv"><thead><tr><th>Joint</th><th>Position / movement</th></tr></thead><tbody>{jt}</tbody></table>')
    mt = "".join(f"<tr><td>{md(r[0], True)}</td><td>{md(r[1], True)}</td><td>{md(r[2], True)}</td></tr>" for r in a["muscles"])
    mmap = ""
    if photo and a.get("muscles3d"):
        mimg = F3.img(a["fig"], 58, 34, px=1100, muscles=a.get("muscles3d"))
        mmap = (f'<figure class="muscle-map">{mimg}<figcaption>Muscle map: '
                f'<span style="color:{F3.WORK}">■</span> working (contracting) '
                f'<span style="color:{F3.STRETCH}">■</span> lengthening</figcaption></figure>')
    sec("07", "Major muscles and what they are doing", mmap +
        f'<table><thead><tr><th style="width:26%">Muscle(s)</th><th style="width:26%">Action in this pose</th><th>Role</th></tr></thead><tbody>{mt}</tbody></table>')
    sec("08", "Spinal action and planes of movement", md(a["spine"]) + md(a["planes"]))
    sec("09", "Biomechanics: how the pose loads the body", md(a["biomechanics"]))
    H.append('<div class="two-col">')
    H.append(f'<div><h4>Common mistakes</h4>{ul(a["mistakes"])}</div>')
    H.append(f'<div><h4>Common student limitations</h4>{ul(a["limitations"])}</div>')
    H.append("</div>")
    H.append(f'<div class="box box-safety"><div class="box-title">Contraindications and precautions</div>'
             f'<p><b>Avoid, or practise only with individual guidance, when:</b></p>{ul(a["contraindications"])}'
             f'<p><b>Precautions:</b></p>{ul(a["precautions"])}'
             f'<p class="small muted">Contraindications in yoga rest largely on expert consensus, physiology and case reports rather than trials. '
             f'When in doubt, the student’s own healthcare professional has the final word.</p></div>')
    # variations with figures
    vf = []
    for v in a.get("variation_figs", []):
        if not PH.has(v["fig"]):
            continue   # only accurate photographs are shown; the text describes the others
        s = PH.photo_img(v["fig"], 52, 39, "var")
        vf.append(f"<figure class=\"has-photo\">{s}<figcaption>{md(v['caption'], True)}</figcaption></figure>")
    sec("10", "Modifications, variations and props",
        (f'<div class="var-figs">{"".join(vf)}</div>' if vf else "") +
        f'<h4>Modifications</h4>{ul(a["modifications"])}'
        f'<h4>Beginner variation</h4>{md(a["beginner"])}'
        f'<h4>Advanced variation</h4>{md(a["advanced"])}'
        f'<h4>Use of props</h4>{ul(a["props_use"])}')
    cues = "".join(f"<li>“{md(c, True)}”</li>" for c in a["cues"])
    sec("11", "Teaching the pose", f'<h4>Safe teaching cues</h4><ul class="cue-list">{cues}</ul>'
        f'<h4>Hands-on guidance</h4>{md(a["adjustments"])}')
    sec("12", "Transitions and counterpose",
        f'<table class="kv"><tbody><tr><td>Into the pose</td><td>{md(a["transition_in"], True)}</td></tr>'
        f'<tr><td>Out of the pose</td><td>{md(a["transition_out"], True)}</td></tr>'
        f'<tr><td>Counterpose</td><td>{md(a["counterpose"], True)}</td></tr></tbody></table>')
    H.append(f'<div class="box box-trad"><div class="box-title">Effects traditionally attributed</div>{md(a["traditional"])}</div>')
    H.append(f'<div class="box box-evidence"><div class="box-title">What modern evidence does and does not support</div>{md(a["evidence"])}</div>')
    H.append("</section>")
    return "\n".join(H)


def render_allasanas(arg, ch, numbered, xref):
    return "\n".join(render_asana(a["id"], ch, numbered, xref) for a in load("asanas"))


# ------------------------------------------------------------------------------ muscles
def render_muscles(arg, ch, numbered, xref):
    groups = load("muscles")
    g = next(g for g in groups if g["id"] == arg.strip())
    out = [f'<p class="small muted">{md(g.get("intro", ""), True)}</p>' if g.get("intro") else ""]
    for m in g["muscles"]:
        mid = "muscle-" + slug(m["name"])
        import atlas3d
        sketch = atlas3d.image(m["name"], g["id"])
        rows = [("Origin", m["origin"]), ("Insertion", m["insertion"]), ("Primary actions", m["actions"]),
                ("Role in yoga", m["role"]), ("Stretch or strengthen?", m["train"]), ("Key asanas", m["asanas"]),
                ("Common misconception", m.get("myth", "—"))]
        tab = "<table><tbody>" + "".join(f"<tr><td>{k}</td><td>{md(v, True)}</td></tr>" for k, v in rows) + "</tbody></table>"
        body = (f'<div class="muscle-row"><div class="mfig">{sketch}</div><div class="mtab">{tab}</div></div>' if sketch else tab)
        out.append(f'<div class="muscle" id="{mid}"><h4 class="mname">{html.escape(m["name"])}'
                   f'<small>{html.escape(m.get("latin", ""))}</small></h4>{body}</div>')
    return "\n".join(out)


def all_muscles():
    for g in load("muscles"):
        for m in g["muscles"]:
            yield g, m


# ------------------------------------------------------------------------------ mapping tables
def render_mapping(arg, ch, numbered, xref):
    """Asana–anatomy mapping table on portrait pages: related columns are paired in one cell."""
    groups = load("mapping")
    g = next(g for g in groups if g["id"] == arg.strip())
    label = numbered(ch, "tab")
    xref[f"tab:map-{g['id']}"] = f"Table {label}"

    def pair(r, k1, l1, k2, l2):
        return (f'<span class="ml">{l1}</span>{md(r[k1], True)}'
                f'<span class="ml">{l2}</span>{md(r[k2], True)}')
    rows = []
    for r in g["rows"]:
        fig = PH.photo_img(r["fig"], 22, 16.5, "thumb") if r.get("fig") and PH.has(r["fig"]) else ""
        aid = "map-" + slug(r["asana"])
        rows.append(f'<tr id="{aid}"><td class="mapname">{md(r["asana"], True)}<div class="mapfig">{fig}</div></td>'
                    f'<td>{pair(r, "joints", "Joints", "movement", "Movement")}</td>'
                    f'<td>{pair(r, "muscles", "Key muscles", "action", "Action")}</td>'
                    f'<td>{md(r["loading"], True)}</td>'
                    f'<td>{pair(r, "limitations", "Common limitations", "modifications", "Modifications")}</td></tr>')
    head = ('<thead><tr><th style="width:17%">Asana</th><th style="width:20%">Joints · movement</th>'
            '<th style="width:25%">Muscles · action</th><th style="width:15%">Loading</th>'
            '<th>Limitations · modifications</th></tr></thead>')
    return (f'<div class="maptable"><div class="tcap" id="tab-map-{g["id"]}"><span class="tabnum">Table {label}</span> '
            f'{md(g["title"], True)}</div><table>{head}<tbody>{"".join(rows)}</tbody></table>'
            f'<p class="small muted">{md(g.get("note", ""), True)}</p></div>')


# ------------------------------------------------------------------------------ glossary
def render_glossary(arg, ch, numbered, xref):
    items = load(f"glossary_{arg.strip()}")
    items = sorted(items, key=lambda t: strip(t["term"]).lower())
    out = ['<dl class="gloss">']
    last = None
    for t in items:
        L = strip(t["term"])[0].upper()
        if L != last:
            out.append(f'<div class="gl-letter">{L}</div>')
            last = L
        dev = f' <span class="dev">{t["dev"]}</span>' if t.get("dev") else ""
        out.append(f'<dt>{html.escape(t["term"])}{dev}</dt><dd>{md(t["def"], True)}</dd>')
    out.append("</dl>")
    return "\n".join(out)


def strip(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


# ------------------------------------------------------------------------------ pose indexes
def pose_entries():
    """Every posture that has a monograph or a mapping-table row, with its anchor."""
    entries = []
    for a in load("asanas"):
        entries.append((a["sanskrit"], a["english"], f"asana-{a['id']}", True))
    for g in load("mapping"):
        for r in g["rows"]:
            sk = r.get("sanskrit") or r["asana"]
            en = r.get("english") or ""
            aid = "map-" + slug(r["asana"])
            if not any(strip(e[0]).lower() == strip(sk).lower() and e[3] for e in entries):
                entries.append((sk, en, aid, False))
    return entries


def render_poseindex(arg, ch, numbered, xref):
    entries = pose_entries()
    mode = arg.strip()
    if mode == "sanskrit":
        entries = sorted(entries, key=lambda e: strip(e[0]).lower())
        rows = [f'<p><span class="pi-sk">{html.escape(sk)}</span>&nbsp;— {html.escape(en)}<span class="pi-dots"></span>'
                f'<a class="pg" href="#{aid}"></a>{" ★" if main else ""}</p>' for sk, en, aid, main in entries]
    else:
        entries = sorted(entries, key=lambda e: (e[1] or e[0]).lower())
        rows = [f'<p><span class="pi-sk">{html.escape(en or sk)}</span>&nbsp;— <i>{html.escape(sk)}</i><span class="pi-dots"></span>'
                f'<a class="pg" href="#{aid}"></a>{" ★" if main else ""}</p>' for sk, en, aid, main in entries]
    return ('<p class="small muted">★ = full illustrated monograph in @ch:twelve-asanas; other page numbers point to the mapping tables in @ch:mapping '
            'or to the chapter where the pose is taught.</p><div class="poseindex">' + "".join(rows) + "</div>")


def render_musclegroup(arg, ch, numbered, xref):
    """Muscle index: alphabetical, with page references to the atlas cards."""
    ms = sorted(all_muscles(), key=lambda gm: gm[1]["name"].lower())
    rows = [f'<p><span class="pi-sk">{html.escape(m["name"])}</span>&nbsp;— {html.escape(g["title"])}<span class="pi-dots"></span>'
            f'<a class="pg" href="#muscle-{slug(m["name"])}"></a></p>' for g, m in ms]
    return '<div class="poseindex">' + "".join(rows) + "</div>"


# ------------------------------------------------------------------------------ cues
def render_cues(arg, ch, numbered, xref):
    data = load("cues")
    out = []
    for cat in data:
        out.append(f'<h3>{html.escape(cat["title"])}</h3>')
        if cat.get("note"):
            out.append(md(cat["note"]))
        rows = "".join(f'<tr><td>{md(c[0], True)}</td><td><i>“{md(c[1], True)}”</i></td><td>{md(c[2], True) if len(c) > 2 else ""}</td></tr>'
                       for c in cat["cues"])
        out.append(f'<table><thead><tr><th style="width:18%">Pose / moment</th><th style="width:48%">Cue</th><th>Why it works / watch for</th></tr></thead><tbody>{rows}</tbody></table>')
    return "\n".join(out)


# ------------------------------------------------------------------------------ sequence strips
def render_sequence(arg, ch, numbered, xref):
    """!sequence(pose=Label/sub; pose=Label/sub; …) or !sequence(@name) from data/sequences.yaml"""
    arg = arg.strip()
    if arg.startswith("@"):
        seq = load("sequences")[arg[1:]]
        items = [(s[0], s[1]) for s in seq]
    else:
        items = []
        for part in arg.split(";"):
            if not part.strip():
                continue
            k, v = part.split("=", 1)
            items.append((k.strip(), v.strip()))
    cells = []
    for i, (k, lab) in enumerate(items):
        s = (f'<div class="ph has-photo" style="width:22mm;height:17mm">{PH.photo_img(k, 22, 16.5, "strip")}</div>'
             if PH.has(k) else F3.box(k, 22, 17, px=300))
        main, _, sub = lab.partition("/")
        cells.append(f'<div class="step">{s}<span class="sn">{i+1}</span><span class="sl"><b>{html.escape(main)}</b>'
                     f'{"<br>" + html.escape(sub) if sub else ""}</span></div>')
    return '<div class="seq">' + "".join(cells) + "</div>"


def render_photocredits(arg, ch, numbered, xref):
    return PH.render_photocredits(arg, ch, numbered, xref)


def render_table(arg, ch, numbered, xref):
    return ""
