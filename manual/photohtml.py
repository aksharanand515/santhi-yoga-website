"""
Posture photographs for the manual (Wikimedia Commons, free licences), in one house style.

    photo_img(key, max_w, max_h, ctx)  -> <img> (or "" when no photo is selected for key)
    photo_svg(key, x, y, w, h, ctx)    -> <image> fitted and centred in a w × h box
    has(key)
    render_photocredits(...)           -> the photo-credits page (!photocredits)

Selections live in photos/selection.yaml (pose key -> Commons file, optional crop box, mirror
flag). Originals are fetched from Commons once (photos/cache, not committed); the processed
images in photos_out/ are committed so the book builds offline. Licence metadata is cached in
photos/meta.json.
"""
import html
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "photos"))

import process as PR  # noqa: E402

SEL_FILE = ROOT / "photos" / "selection.yaml"
META_FILE = ROOT / "photos" / "meta.json"
USED = {}   # key -> file title, in order of first use (for the credits page)

# output variants: target width in px and frame aspect (None = natural crop)
CTX = {"hero": (1400, None), "var": (900, 4 / 3), "strip": (620, 4 / 3), "thumb": (420, 4 / 3), "wide": (1100, None)}


def _sel():
    if not hasattr(_sel, "d"):
        _sel.d = yaml.safe_load(SEL_FILE.read_text(encoding="utf-8")) or {}
    return _sel.d


def _meta():
    if not hasattr(_meta, "d"):
        _meta.d = json.loads(META_FILE.read_text()) if META_FILE.exists() else {}
    return _meta.d


def _save_meta():
    META_FILE.write_text(json.dumps(_meta.d, indent=1, ensure_ascii=False))


def has(key):
    return key in _sel()


def _file_meta(title):
    M = _meta()
    if title not in M:
        import commons as C
        M.update(C.info([title]))
        _save_meta()
    return M[title]


def _original(title):
    import commons as C
    base = title[5:]
    # any copy already fetched (different cache folders / name spellings) is good enough if large
    for d in ("p1280", "p960"):
        for nm in (re.sub(r"[^\w.-]+", "_", base), base.replace(" ", "_")):
            f = C.CACHE / d / nm
            if f.exists() and f.stat().st_size > 20000:
                return f
    m = _file_meta(title)
    name = re.sub(r"[^\w.-]+", "_", base)
    return C.download(C.sized(m, 1280) if m["w"] > 1280 else m["url"], C.CACHE / "p1280" / name)


def processed(key, ctx="hero"):
    """Path (relative to the manual root) and pixel size of the processed photo."""
    s = _sel()[key]
    title = s["file"] if s["file"].startswith("File:") else "File:" + s["file"]
    width, aspect = CTX[ctx]
    box = s.get("box")
    sig_src = PR.OUT / f"{key}-{ctx}.json"
    # reuse a processed file when its parameters are unchanged (no network needed)
    want = dict(title=title, box=box, aspect=aspect, width=width, lift=s.get("lift", 0.0), flip=s.get("flip", False), v=3)
    if sig_src.exists():
        rec = json.loads(sig_src.read_text())
        if rec.get("params") == want and (ROOT / rec["file"]).exists():
            USED.setdefault(key, title)
            return rec["file"], rec["w"], rec["h"]
    src = _original(title)
    out = PR.make(src, f"{key}-{ctx}", box=tuple(box) if box else None, aspect=aspect, width=width,
                  lift=s.get("lift", 0.0), flip=s.get("flip", False))
    from PIL import Image
    w, h = Image.open(out).size
    rel = str(out.relative_to(ROOT))
    sig_src.write_text(json.dumps(dict(params=want, file=rel, w=w, h=h)))
    USED.setdefault(key, title)
    return rel, w, h


def fit(w, h, max_w, max_h):
    s = min(max_w / w, max_h / h)
    return w * s, h * s


def photo_img(key, max_w, max_h, ctx="hero", cls="photo"):
    if not has(key):
        return ""
    f, w, h = processed(key, ctx)
    ww, hh = fit(w, h, max_w, max_h)
    return f'<img class="{cls}" src="{f}" style="width:{ww:.2f}mm;height:{hh:.2f}mm" alt="">'


def photo_svg(key, x, y, bw, bh, ctx="strip"):
    """<image> fitted into the box (x, y, bw, bh) in SVG user units, centred horizontally and
    resting on the bottom edge."""
    f, w, h = processed(key, ctx)
    ww, hh = fit(w, h, bw, bh)
    return f'<image href="{f}" x="{x + (bw - ww) / 2:.2f}" y="{y + bh - hh:.2f}" width="{ww:.2f}" height="{hh:.2f}"/>'


def _plain(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def credits():
    """[(key, title, author, licence, licence url, page url, modified)] for every photo used."""
    out = []
    for key, title in USED.items():
        m = _file_meta(title)
        s = _sel()[key]
        mods = "cropped, toned monochrome" + (", mirrored" if s.get("flip") else "")
        out.append((key, title[5:], _plain(m.get("artist")) or "unknown", m.get("license", ""),
                    m.get("license_url", ""), m["page"], mods))
    return out


def render_photocredits(arg, ch, numbered, xref):
    rows = []
    seen = set()
    for key, title, author, lic, lic_url, page, mods in sorted(credits(), key=lambda r: r[1].lower()):
        if title in seen:
            continue
        seen.add(title)
        lic_html = f'<a href="{html.escape(lic_url)}">{html.escape(lic)}</a>' if lic_url else html.escape(lic)
        rows.append(f"<tr><td>{html.escape(title)}</td><td>{html.escape(author)}</td><td>{lic_html}</td>"
                    f'<td class="small"><a href="{html.escape(page)}">Wikimedia Commons</a>; {mods}</td></tr>')
    return ('<table class="credits"><thead><tr><th style="width:34%">Photograph (file name on Wikimedia Commons)</th>'
            '<th style="width:22%">Photographer / author</th><th style="width:14%">Licence</th><th>Source; changes made</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')
