#!/usr/bin/env python3
"""Santhi School of Yoga & Vedanta Studies: build the logo with the school's full name.

The school's logo artwork (tools/brand/logo-source.webp, 1024x1024) reads
"Santhi Yoga / SCHOOL". This keeps everything else about it -- the seated
figure, the lotus, the green and gold rings, the cream -- and sets the full
name in the same manner:

  Santhi School of Yoga          green serif, as "Santhi Yoga" was
  ------------ . ------------    the same gold rules and dot
  & VEDANTA STUDIES              gold spaced capitals, as "SCHOOL" was

Steps
  1. Clean   paint the old lettering out inside the inner gold ring. The cream
             there is flat (it varies by under one level), so it is refilled
             with the same colour and the same faint grain. The figure's soft
             shadow reaches down into the lettering; under the legs it is
             continued at its own measured fade rather than cut off.
  2. Letter  set the new lines in Cormorant Garamond (the site's display face,
             from assets/fonts) in a headless browser, each line as large as
             the ring allows at its baseline.
  3. Export  square files with the cream carried to the corners -- no
             transparency, which showed as black corners in dark mode:
               assets/brand/santhi-school-of-yoga-logo-1024.png  master; Business Profile, Instagram
               assets/brand/santhi-school-of-yoga-logo-512.png   the organisation's logo in the site's data
               assets/brand/santhi-school-of-yoga-logo-232.webp  the footer, and articles' publisher logo

Needs Pillow (pip install pillow) and Playwright's Chromium for Node.
Usage: python3 tools/brand/make-logo.py
"""
import math
import random
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'tools/brand/logo-source.webp'
OUT = ROOT / 'assets/brand'
NAME, SUB = 'Santhi School of Yoga', '& VEDANTA STUDIES'

# Measured on the source artwork
BG = (251, 241, 233)                                 # the cream inside the rings
CX, CY, RX, RY = 510.5, 521.0, 413.5, 439.0          # the inner gold ring (slightly oval)
MARGIN = 9                                           # keep clear of the gold line
LEG_X0, LEG_X1, SHADOW_ROW, SHADOW_FADE = 380, 650, 676, 16.0  # the figure's shadow: 62 -> 40 levels over rows 676-683
TEXT_TOP = 680                                       # the old lettering starts here (684 under the legs)


def clean(im):
    px = im.load()
    rnd = random.Random(7)
    inside = lambda x, y: ((x - CX) / (RX - MARGIN)) ** 2 + ((y - CY) / (RY - MARGIN)) ** 2 < 1
    shadow = {x: px[x, SHADOW_ROW] for x in range(LEG_X0, LEG_X1 + 1)}
    for y in range(SHADOW_ROW + 1, int(CY + RY)):
        for x in range(int(CX - RX), int(CX + RX) + 1):
            if not inside(x, y):
                continue
            if LEG_X0 <= x <= LEG_X1:
                k = math.exp(-(y - SHADOW_ROW) / SHADOW_FADE)
                base = [BG[i] + (shadow[x][i] - BG[i]) * k for i in range(3)]
            elif y >= TEXT_TOP:
                base = BG
            else:
                continue
            px[x, y] = tuple(max(0, min(255, round(v + rnd.gauss(0, 0.5)))) for v in base)
    return im


PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: "Cormorant Garamond"; font-weight: 400 600; src: url("cormorant-garamond-latin.woff2") format("woff2"); }
html, body { margin: 0; }
#logo { position: relative; width: 1024px; height: 1024px; }
#logo img, #logo svg { position: absolute; inset: 0; }
</style></head><body>
<div id="logo"><img src="base.png" width="1024" height="1024" alt=""><svg id="t" viewBox="0 0 1024 1024" width="1024" height="1024">
  <defs><filter id="emboss" x="-5%" y="-20%" width="110%" height="160%"><feDropShadow dx="0" dy="2.2" stdDeviation="1.8" flood-color="#5A4626" flood-opacity=".30"/></filter></defs>
</svg></div>
<script>
const NS = 'http://www.w3.org/2000/svg', svg = document.getElementById('t');
const CX = __CX__, CY = __CY__, RX = __RX__, RY = __RY__, MARGIN = 38;
const halfChord = (y) => RX * Math.sqrt(1 - ((y - CY) / RY) ** 2);
function line(str, y, style, maxSize, spacing) {
  const t = document.createElementNS(NS, 'text');
  t.setAttribute('x', CX); t.setAttribute('y', y); t.setAttribute('text-anchor', 'middle'); t.textContent = str; svg.appendChild(t);
  let size = maxSize; const set = () => t.setAttribute('style', `${style};font-size:${size}px;letter-spacing:${spacing}em`); set();
  // a line is widest where the ring is narrowest: at its baseline
  while (t.getComputedTextLength() - size * spacing > 2 * (halfChord(y) - MARGIN) && size > 12) { size -= 0.5; set(); }
  return t.getComputedTextLength() - size * spacing;
}
document.fonts.ready.then(() => {
  const w = line(__NAME__, 774, "font-family:'Cormorant Garamond';font-weight:600;fill:#2D3520;stroke:#2D3520;stroke-width:1.3px;paint-order:stroke;filter:url(#emboss)", 90, 0.005);
  line(__SUB__, 860, "font-family:'Cormorant Garamond';font-weight:600;fill:#A3772B", 38, 0.3);
  const half = Math.min(w / 2 - 20, 200), y = 810, g = document.createElementNS(NS, 'g');
  g.setAttribute('stroke', '#B8923A'); g.setAttribute('stroke-width', 1.8); g.setAttribute('stroke-linecap', 'round');
  [[CX - half, CX - 16], [CX + 16, CX + half]].forEach(([a, b]) => { const l = document.createElementNS(NS, 'line'); Object.entries({ x1: a, x2: b, y1: y, y2: y }).forEach(([k, v]) => l.setAttribute(k, v)); g.appendChild(l); });
  const dot = document.createElementNS(NS, 'circle'); Object.entries({ cx: CX, cy: y, r: 4.6, fill: '#B8923A', stroke: 'none' }).forEach(([k, v]) => dot.setAttribute(k, v)); g.appendChild(dot);
  svg.appendChild(g);
  document.body.dataset.ready = '1';
});
</script></body></html>"""

SHOT = """const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1024, height: 1024 } });
  await p.goto(process.argv[2]); await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(300);
  await (await p.$('#logo')).screenshot({ path: process.argv[3] });
  await b.close();
})();"""


def letter(base, work):
    base.save(work / 'base.png')
    shutil.copy(ROOT / 'assets/fonts/cormorant-garamond-latin.woff2', work)
    page = PAGE.replace('__CX__', str(CX)).replace('__CY__', str(CY)).replace('__RX__', str(RX)).replace('__RY__', str(RY))
    page = page.replace('__NAME__', repr(NAME)).replace('__SUB__', repr(SUB))
    (work / 'logo.html').write_text(page, encoding='utf-8')
    (work / 'shot.js').write_text(SHOT, encoding='utf-8')
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1'], cwd=work,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.8)
        subprocess.run(['node', 'shot.js', f'http://127.0.0.1:{port}/logo.html', str(work / 'logo.png')], cwd=work, check=True)
    finally:
        server.terminate()
    return Image.open(work / 'logo.png').convert('RGB')


def main():
    im = clean(Image.open(SRC).convert('RGB'))
    with tempfile.TemporaryDirectory() as tmp:
        logo = letter(im, Path(tmp))
    logo.save(OUT / 'santhi-school-of-yoga-logo-1024.png', optimize=True)
    logo.resize((512, 512), Image.LANCZOS).save(OUT / 'santhi-school-of-yoga-logo-512.png', optimize=True)
    logo.resize((232, 232), Image.LANCZOS).save(OUT / 'santhi-school-of-yoga-logo-232.webp', quality=90, method=6)
    for name in ('santhi-school-of-yoga-logo-1024.png', 'santhi-school-of-yoga-logo-512.png', 'santhi-school-of-yoga-logo-232.webp'):
        print(f'wrote assets/brand/{name} ({(OUT / name).stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
