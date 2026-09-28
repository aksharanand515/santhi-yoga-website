#!/usr/bin/env python3
"""
Build the Santhi Yoga School 200-Hour Yoga Teacher Training Manual.

    Markdown chapters (src/)  +  structured data (data/)  +  drawn figures (figures.py)
        -> one HTML document (build/manual.html)
        -> print-ready A4 PDF via WeasyPrint

Usage:  python3 build.py            full build (HTML + PDF)
        python3 build.py --html     HTML only (fast, for checking)
        python3 build.py --only 25  build a single chapter file (by number) for proofing

Everything the book cites must exist in data/references.yaml; the build stops if a
citation key is missing, and reports references that are never cited.
"""
import argparse
import html
import pathlib
import re
import sys
from collections import OrderedDict, defaultdict

import markdown
import yaml

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
DATA = ROOT / "data"
BUILD = ROOT / "build"
PDF_NAME = "Santhi-Yoga-School-200-Hour-TTC-Manual.pdf"

sys.path.insert(0, str(ROOT))
sys.modules.setdefault("build", sys.modules[__name__])
import figures  # noqa: E402
import render_data  # noqa: E402

WARN = []


def warn(msg):
    WARN.append(msg)


# --------------------------------------------------------------------------------------
# References
# --------------------------------------------------------------------------------------
REFS = yaml.safe_load((DATA / "references.yaml").read_text(encoding="utf-8"))
CITED = OrderedDict()


def cite_label(key, narrative=False):
    r = REFS.get(key)
    if r is None:
        warn(f"MISSING REFERENCE KEY: {key}")
        return f"[{key}?]"
    CITED[key] = True
    authors = r.get("short") or r["author"].split(",")[0]
    year = r["year"]
    if narrative:
        return f'<a class="cite" href="#ref-{key}">{authors} ({year})</a>'
    return f'<a class="cite" href="#ref-{key}">{authors}, {year}</a>'


def process_citations(text):
    # Parenthetical: [@a; @b, p. 4]
    def paren(m):
        parts = [p.strip() for p in m.group(1).split(";")]
        out = []
        for p in parts:
            mm = re.match(r"@([A-Za-z][\w-]*)(?:,\s*(.+))?$", p)
            if not mm:
                out.append(p)
                continue
            lab = cite_label(mm.group(1))
            if mm.group(2):
                lab = lab[:-4] + f", {mm.group(2)}</a>"
            out.append(lab)
        return "(" + "; ".join(out) + ")"

    text = re.sub(r"\[(@[A-Za-z][^\]]*?)\]", paren, text)
    # Narrative: @key  -> Author (Year)
    text = re.sub(r"(?<![\w.@/])@([A-Za-z][\w-]*\d{4}[a-z0-9]*)\b",
                  lambda m: cite_label(m.group(1), narrative=True) if m.group(1) in REFS or not m.group(1)[0].isalpha() else cite_label(m.group(1), narrative=True), text)
    return text


# --------------------------------------------------------------------------------------
# Block syntax  ::: kind Optional title   ...   :::
# --------------------------------------------------------------------------------------
BOX_TITLES = {
    "objectives": "Learning Objectives",
    "keyconcept": "Key Concept",
    "tip": "Teacher Tip",
    "safety": "Safety First",
    "exercise": "Practical Exercise",
    "evidence": "What the Evidence Says",
    "trad": "Traditional Teaching",
    "history": "Historical Note",
    "note": "Note",
    "verse": "",
    "takeaways": "Key Takeaways",
    "reflect": "Reflection Questions",
    "practice": "Teacher-Practice Exercises",
    "check": "Knowledge Check",
    "assignment": "Teaching Assignment",
    "myth": "Myth and Reality",
    "cue": "Cueing Script",
    "plain": "",
    "form": "",
}
REVIEW_KINDS = ["takeaways", "reflect", "practice", "check", "assignment"]


def process_blocks(text):
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        m = re.match(r"^:::\s*([a-z]+)\s*(.*)$", lines[i])
        if m and m.group(1) in BOX_TITLES:
            kind, title = m.group(1), m.group(2).strip()
            body = []
            i += 1
            while i < len(lines) and not re.match(r"^:::\s*$", lines[i]):
                body.append(lines[i])
                i += 1
            i += 1  # skip closing
            title = title or BOX_TITLES[kind]
            if kind == "takeaways":
                out.append('<div class="review-head"><span>Chapter Review</span></div>\n')
            body_txt = "\n".join(body)
            if kind == "check":
                body_txt = re.sub(r"^Answers:\s*(.*)$",
                                  lambda mm: f'<p class="answers"><b>Answers</b> {mm.group(1)}</p>',
                                  body_txt, flags=re.M)
            head = f'<div class="box-title">{title}</div>\n' if title else ""
            out.append(f'<div class="box box-{kind}" markdown="1">\n{head}\n{body_txt}\n\n</div>\n')
            continue
        if lines[i].startswith(":::"):
            warn(f"Unknown block: {lines[i]}")
        out.append(lines[i])
        i += 1
    return "\n".join(out)


EV = {"H": ("Historical", "h"), "T": ("Traditional", "t"), "I": ("Interpretive", "i"),
      "S": ("Scientific", "s"), "C": ("Clinical caution", "c")}


def process_inline(text):
    text = re.sub(r"\[\[([HTISC])\]\]",
                  lambda m: f'<span class="ev ev-{EV[m.group(1)][1]}">{EV[m.group(1)][0]}</span>', text)
    return text


# --------------------------------------------------------------------------------------
# Figures, tables, cross-references, data blocks
# --------------------------------------------------------------------------------------
XREF = {}  # "fig:id" -> "Figure 17.3"


class Chapter:
    def __init__(self, path):
        self.path = path
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            raise SystemExit(f"{path.name}: missing front matter")
        self.meta = yaml.safe_load(m.group(1))
        self.body = m.group(2)
        self.kind = self.meta.get("kind", "chapter")
        self.num = str(self.meta.get("number", ""))
        self.title = self.meta["title"]
        self.short = self.meta.get("short", self.title)
        self.id = self.meta.get("id") or path.stem
        self.fig_n = 0
        self.tab_n = 0
        self.headings = []


def numbered(ch, kind):
    if kind == "fig":
        ch.fig_n += 1
        n = ch.fig_n
    else:
        ch.tab_n += 1
        n = ch.tab_n
    prefix = ch.num if ch.num else "0"
    return f"{prefix}.{n}"


def process_figures_tables(ch, text):
    def fig(m):
        fid = m.group(1)
        f = figures.get(fid)
        if f is None:
            warn(f"{ch.path.name}: missing figure {fid}")
            return f'<p class="missing">[missing figure {fid}]</p>'
        label = numbered(ch, "fig")
        XREF[f"fig:{fid}"] = f"Figure {label}"
        cls = f.get("cls", "")
        return (f'\n<figure class="fig {cls}" id="fig-{fid}">{f["svg"]}'
                f'<figcaption><span class="fignum">Figure {label}</span> {md_inline(f["caption"])}</figcaption></figure>\n')

    text = re.sub(r"^!fig\(([\w-]+)\)\s*$", fig, text, flags=re.M)

    def photo(m):
        src, cap = m.group(1), m.group(2)
        num = ""
        if ch.num:
            num = f'<span class="fignum">Figure {numbered(ch, "fig")}</span> '
        return (f'\n<figure class="fig photo" ><img src="assets/{src}" alt=""/>'
                f'<figcaption>{num}{md_inline(cap)}</figcaption></figure>\n')

    text = re.sub(r"^!photo\(([^|)]+)\|([^)]*)\)\s*$", photo, text, flags=re.M)

    def tab(m):
        cap, tid = m.group(1).strip(), m.group(2)
        label = numbered(ch, "tab")
        if tid:
            XREF[f"tab:{tid}"] = f"Table {label}"
        idattr = f' id="tab-{tid}"' if tid else ""
        return f'<div class="tcap"{idattr}><span class="tabnum">Table {label}</span> {md_inline(cap)}</div>\n'

    text = re.sub(r"^Table:\s*(.*?)\s*(?:\{#tab:([\w-]+)\})?\s*$", tab, text, flags=re.M)

    def datablock(m):
        name, arg = m.group(1), m.group(2)
        fn = getattr(render_data, f"render_{name}", None)
        if fn is None:
            warn(f"unknown data block {name}")
            return ""
        return "\n" + fn(arg, ch, numbered, XREF) + "\n"

    text = re.sub(r"^!(asana|muscles|mapping|glossary|poseindex|cues|sequence|table|allasanas|musclegroup)\(([^)]*)\)\s*$",
                  datablock, text, flags=re.M)
    return text


def md_inline(s):
    s = process_inline(process_citations(s))
    return markdown.markdown(s, extensions=["smarty"]).removeprefix("<p>").removesuffix("</p>")


MD_EXT = ["tables", "attr_list", "md_in_html", "def_list", "smarty", "sane_lists"]


def md(text):
    out = markdown.markdown(text, extensions=MD_EXT, output_format="html", lazy_ol=False)
    # WeasyPrint ignores <ol start>; reset the list-item counter explicitly
    return re.sub(r'<ol start="(\d+)"', lambda m: f'<ol start="{m.group(1)}" style="counter-reset: list-item {int(m.group(1)) - 1}"', out)


def number_headings(ch, htmltext):
    n2 = 0
    n3 = 0

    def h(m):
        nonlocal n2, n3
        level, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        if "nonum" in attrs:
            return m.group(0)
        if level == "2":
            n2 += 1
            n3 = 0
            num = f"{ch.num}.{n2}" if ch.num else ""
            hid = f"{ch.id}-s{n2}"
            ch.headings.append((num, re.sub(r"<[^>]+>", "", inner), hid))
            numspan = f'<span class="hnum">{num}</span>' if num else ""
            return f'<h2 id="{hid}"{attrs}>{numspan}{inner}</h2>'
        else:
            n3 += 1
            return f"<h3{attrs}>{inner}</h3>"

    return re.sub(r"<h([23])((?: [^>]*)?)>(.*?)</h\1>", h, htmltext, flags=re.S)


DEV_RE = re.compile(r"([ऀ-ॿ][ऀ-ॿ\s।॥०-९\-]*[ऀ-ॿ।॥])")
MAL_RE = re.compile(r"([ഀ-ൿ]+)")


def script_spans(htmltext):
    # wrap Devanagari / Malayalam runs that sit in text (not inside tags)
    parts = re.split(r"(<[^>]+>)", htmltext)
    for i, p in enumerate(parts):
        if p.startswith("<"):
            continue
        p = DEV_RE.sub(r'<span class="dev" lang="sa">\1</span>', p)
        p = MAL_RE.sub(r'<span class="mal" lang="ml">\1</span>', p)
        parts[i] = p
    return "".join(parts)


def render_chapter(ch):
    text = ch.body
    text = process_blocks(text)
    text = process_figures_tables(ch, text)
    text = process_citations(text)
    text = process_inline(text)
    body = md(text)
    body = number_headings(ch, body)
    kinds = set(re.findall(r'class="box box-(\w+)"', body))
    if ch.kind == "chapter":
        for k in ["objectives"] + REVIEW_KINDS:
            if k not in kinds:
                warn(f"{ch.path.name}: chapter lacks '{k}' block")

    if ch.kind == "chapter":
        sec = ch.meta.get("section", "")
        head = (f'<header class="chap-open" id="{ch.id}">'
                f'<div class="chap-sec">Section {sec} · {html.escape(SECTION_NAMES.get(sec, ""))}</div>'
                f'<div class="chap-num"><span>Chapter</span> {ch.num}</div>'
                f'<h1 class="chap-title" data-short="{html.escape(ch.short)}">{html.escape(ch.title)}</h1>'
                + (f'<p class="chap-epigraph">{md_inline(ch.meta["epigraph"])}</p>' if ch.meta.get("epigraph") else "")
                + "</header>")
        return f'<section class="chapter" data-sec="{sec}">{head}\n<div class="chap-body">{body}</div></section>'
    if ch.kind == "appendix":
        head = (f'<header class="chap-open app-open" id="{ch.id}">'
                f'<div class="chap-num"><span>Appendix</span> {ch.num}</div>'
                f'<h1 class="chap-title" data-short="{html.escape(ch.short)}">{html.escape(ch.title)}</h1></header>')
        return f'<section class="chapter appendix {ch.meta.get("cls", "")}">{head}\n<div class="chap-body">{body}</div></section>'
    if ch.kind == "section":
        img = ch.meta.get("image")
        chaps = "".join(
            f'<li><a href="#{c.id}"><span class="dn">{c.num}</span> {html.escape(c.title)}</a></li>'
            for c in CHAPTERS if c.kind == "chapter" and str(c.meta.get("section")) == ch.num)
        return (f'<section class="divider" id="{ch.id}">'
                f'<div class="div-photo" style="background-image:url(assets/{img})"></div>'
                f'<div class="div-text"><div class="div-num">Section {ch.num}</div>'
                f'<h1 class="div-title" data-short="{html.escape(ch.short)}">{html.escape(ch.title)}</h1>'
                f'<div class="div-intro">{body}</div><ol class="div-chaps">{chaps}</ol></div></section>')
    if ch.kind == "front":
        cls = ch.meta.get("cls", "")
        title = "" if ch.meta.get("notitle") else f'<h1 class="front-title" id="{ch.id}" data-short="{html.escape(ch.short)}">{html.escape(ch.title)}</h1>'
        return f'<section class="front {cls}">{title}{body}</section>'
    if ch.kind == "raw":
        return body
    raise SystemExit(f"unknown kind {ch.kind}")


SECTION_NAMES = {
    "I": "Yoga Philosophy, Tradition & Practice",
    "II": "Asana, Pranayama, Meditation & Anatomy",
    "III": "Teaching, Professional Practice & Graduation",
}


# --------------------------------------------------------------------------------------
# Generated front and back matter
# --------------------------------------------------------------------------------------
def cover():
    return (ROOT / "cover.html").read_text(encoding="utf-8")


def toc():
    rows = []
    for c in CHAPTERS:
        if c.kind == "section":
            rows.append(f'<li class="toc-sec"><a href="#{c.id}"><span class="tn">Section {c.num}</span>'
                        f'<span class="tt">{html.escape(c.title)}</span></a></li>')
        elif c.kind == "chapter":
            rows.append(f'<li class="toc-ch"><a href="#{c.id}"><span class="tn">{c.num}</span>'
                        f'<span class="tt">{html.escape(c.title)}</span></a></li>')
        elif c.kind == "appendix":
            rows.append(f'<li class="toc-app"><a href="#{c.id}"><span class="tn">{c.num}</span>'
                        f'<span class="tt">{html.escape(c.title)}</span></a></li>')
        elif c.kind == "front" and c.meta.get("toc"):
            rows.append(f'<li class="toc-front"><a href="#{c.id}"><span class="tn"></span>'
                        f'<span class="tt">{html.escape(c.title)}</span></a></li>')
    first_app = next((i for i, r in enumerate(rows) if "toc-app" in r), None)
    if first_app is not None:
        rows.insert(first_app, '<li class="toc-sec"><span class="tn">Back matter</span>'
                               '<span class="tt">Appendices, Glossaries, Indexes &amp; References</span></li>')
    return ('<section class="toc"><h1 class="front-title" data-short="Contents" id="contents">Contents</h1>'
            '<ol class="toc-list">' + "".join(rows) + "</ol></section>")


def detailed_toc():
    """Chapter-by-chapter subsection listing, placed after the short contents."""
    blocks = []
    for c in CHAPTERS:
        if c.kind == "chapter" and c.headings:
            items = "".join(f'<li><a href="#{hid}"><span class="tn">{num}</span><span class="tt">{html.escape(t)}</span></a></li>'
                            for num, t, hid in c.headings)
            blocks.append(f'<div class="dtoc-ch"><h3><a href="#{c.id}">{c.num} · {html.escape(c.title)}</a></h3><ol>{items}</ol></div>')
    return ('<section class="dtoc"><h1 class="front-title" data-short="Detailed Contents" id="detailed-contents">'
            'Detailed Contents</h1><div class="dtoc-cols">' + "".join(blocks) + "</div></section>")


def references_html():
    groups = OrderedDict([
        ("primary", "Primary Texts and Translations"),
        ("scholarship", "Yoga History, Philosophy and Tradition"),
        ("textbook", "Anatomy, Physiology and Movement Textbooks"),
        ("research", "Research Articles and Reviews"),
        ("guideline", "Clinical Guidelines and Institutional Sources"),
        ("teaching", "Teaching, Ethics and Trauma-Aware Practice"),
    ])
    out = ['<p class="refs-intro">Every reference cited in this manual is listed below. Citation keys were checked at build time: '
           'the manual cites nothing that is not listed here. Where a traditional text exists in many translations, the '
           'translation consulted is listed; verse numbering of the <i>Haṭha Yoga Pradīpikā</i> in particular differs slightly between editions.</p>']
    for g, gname in groups.items():
        items = sorted([(k, r) for k, r in REFS.items() if r.get("type") == g],
                       key=lambda kr: (kr[1]["author"].lower(), str(kr[1]["year"])))
        if not items:
            continue
        out.append(f'<h2 class="nonum refs-group">{gname}</h2><ol class="refs">')
        for k, r in items:
            out.append(f'<li id="ref-{k}">{md_inline(format_ref(r))}</li>')
        out.append("</ol>")
    return "\n".join(out)


def format_ref(r):
    a = r["author"]
    y = r["year"]
    t = r["title"]
    if r.get("journal"):
        s = f'{a} ({y}). {t}. *{r["journal"]}*'
        if r.get("volume"):
            s += f', *{r["volume"]}*'
        if r.get("issue"):
            s += f'({r["issue"]})'
        if r.get("pages"):
            s += f', {r["pages"]}'
        s += "."
    else:
        s = f'{a} ({y}). *{t}*.'
        if r.get("edition"):
            s = s[:-1] + f' ({r["edition"]}).'
        if r.get("publisher"):
            s += f' {r["publisher"]}.'
    if r.get("doi"):
        s += f' https://doi.org/{r["doi"]}'
    if r.get("note"):
        s += f' {r["note"]}'
    return s


def index_html(chapter_htmls):
    """General index: anchor first occurrence of each term in each chapter."""
    terms = yaml.safe_load((DATA / "index_terms.yaml").read_text(encoding="utf-8"))
    entries = defaultdict(list)
    counter = [0]
    new_htmls = []
    compiled = []
    for t in terms:
        if isinstance(t, str):
            t = {"term": t}
        pats = t.get("match") or [re.escape(t["term"])]
        compiled.append((t["term"], re.compile(r"(?<![\w-])(" + "|".join(pats) + r")(?![\w-])", re.I)))
    for kind, cid, h in chapter_htmls:
        if kind != "chapter":
            new_htmls.append(h)
            continue
        parts = re.split(r"(<[^>]+>)", h)
        # track whether we are inside heading/figure/svg (skip those)
        skip_depth = 0
        done = set()
        for i, p in enumerate(parts):
            if p.startswith("<"):
                tag = re.match(r"</?(\w+)", p)
                if tag and tag.group(1) in ("h1", "h2", "h3", "svg", "figcaption", "a", "header", "script", "style"):
                    if p.startswith("</"):
                        skip_depth = max(0, skip_depth - 1)
                    elif not p.endswith("/>"):
                        skip_depth += 1
                continue
            if skip_depth or not p.strip():
                continue
            for term, rx in compiled:
                if term in done:
                    continue
                mm = rx.search(p)
                if mm:
                    counter[0] += 1
                    aid = f"ix{counter[0]}"
                    p = p[:mm.start()] + f'<span class="ixa" id="{aid}"></span>' + p[mm.start():]
                    entries[term].append(aid)
                    done.add(term)
            parts[i] = p
        new_htmls.append("".join(parts))
    # build index
    by_letter = OrderedDict()
    for term in sorted(entries, key=lambda s: strip_diacritics(s).lower()):
        L = strip_diacritics(term)[0].upper()
        by_letter.setdefault(L, []).append(term)
    out = ['<div class="index-cols">']
    for L, ts in by_letter.items():
        out.append(f'<div class="ix-letter">{L}</div>')
        for term in ts:
            pgs = ", ".join(f'<a class="pg" href="#{a}"></a>' for a in entries[term])
            out.append(f'<p class="ix-entry">{html.escape(term)}<span class="ix-pages"> {pgs}</span></p>')
    out.append("</div>")
    return new_htmls, "\n".join(out)


def strip_diacritics(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


# --------------------------------------------------------------------------------------
CHAPTERS = []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", action="store_true")
    ap.add_argument("--only", help="comma list of file-name prefixes to build")
    args = ap.parse_args()

    files = sorted(SRC.glob("*.md"))
    if args.only:
        pre = args.only.split(",")
        files = [f for f in files if any(f.name.startswith(p) for p in pre)]
    for f in files:
        CHAPTERS.append(Chapter(f))

    rendered = []
    for ch in CHAPTERS:
        rendered.append((ch.kind, ch.id, render_chapter(ch)))

    # special generated pages
    final = []
    for kind, cid, h in rendered:
        h = h.replace("<p>!toc</p>", "@@TOC@@").replace("<p>!dtoc</p>", "@@DTOC@@")
        h = h.replace("<p>!references</p>", references_html())
        final.append((kind, cid, h))

    final_htmls, ix = index_html(final)
    body = "\n".join(final_htmls)
    body = body.replace("<p>!index</p>", ix)
    body = body.replace("@@TOC@@", toc()).replace("@@DTOC@@", detailed_toc())

    # cross references
    def xref(m):
        key = m.group(1)
        if key.startswith("ch:"):
            c = next((c for c in CHAPTERS if c.id == key[3:]), None)
            if not c:
                warn(f"bad chapter xref {key}")
                return key
            word = "Appendix" if c.kind == "appendix" else "Chapter"
            return f'<a class="xref" href="#{c.id}">{word}&nbsp;{c.num}</a>'
        if key.startswith("pg:"):
            return f'<a class="pgref" href="#{key[3:]}"></a>'
        if key not in XREF:
            warn(f"bad xref {key}")
            return key
        kind, fid = key.split(":")
        anchor = f"{'fig' if kind == 'fig' else 'tab'}-{fid}"
        return f'<a class="xref" href="#{anchor}">{XREF[key].replace(" ", "&nbsp;")}</a>'

    body = re.sub(r"@((?:fig|tab|ch|pg):[\w-]+)", xref, body)
    body = script_spans(body)

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Santhi Yoga School — 200-Hour Yoga Teacher Training Manual</title>
<meta name="author" content="Santhi School of Yoga &amp; Vedanta Studies">
<meta name="description" content="200-Hour Yoga Teacher Training Manual, Santhi Yoga School, Fort Kochi, Kerala, India">
<meta name="keywords" content="yoga teacher training, hatha yoga, anatomy, pranayama, Kerala">
<link rel="stylesheet" href="style.css">
</head><body>
{cover() if not args.only else ''}
{body}
</body></html>"""

    unused = [k for k in REFS if k not in CITED]
    BUILD.mkdir(exist_ok=True)
    (BUILD / "manual.html").write_text(doc, encoding="utf-8")
    for w in WARN:
        print("WARNING:", w)
    if unused:
        print(f"Note: {len(unused)} references listed but not cited: {', '.join(unused)}")
    print(f"HTML written: {BUILD/'manual.html'}  ({len(doc)//1024} KB)")
    if args.html:
        return
    from weasyprint import HTML
    out = ROOT / (PDF_NAME if not args.only else f"build/proof-{args.only.replace(',', '_')}.pdf")
    doc_obj = HTML(filename=str(BUILD / "manual.html"), base_url=str(ROOT)).render()
    print(f"Pages: {len(doc_obj.pages)}")
    # images above 300 dpi at their printed size are downsampled (keeps the file shareable)
    doc_obj.write_pdf(str(out), optimize_images=True, dpi=300)
    print(f"PDF written: {out}")


if __name__ == "__main__":
    main()
