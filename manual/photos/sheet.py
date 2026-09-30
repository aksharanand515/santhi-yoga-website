"""Contact sheet of candidate photos for visual selection (dev tool)."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import commons as C


def sheet(key, n=16, out=None, cols=4, cell=300, start=0):
    cands = json.loads((C.HERE / "cand" / f"{key}.json").read_text())[start:start + n]
    rows = (len(cands) + cols - 1) // cols
    S = Image.new("RGB", (cols * cell, rows * (cell + 18)), "white")
    d = ImageDraw.Draw(S)
    for i, m in enumerate(cands):
        f = C.CACHE / "thumbs" / (hashlib.md5(m["title"].encode()).hexdigest()[:16] + ".jpg")
        try:
            C.download(m["url"] if m["w"] <= 520 else m["thumb"], f, tries=3)
            im = Image.open(f).convert("RGB")
            im.thumbnail((cell - 6, cell - 6))
            x, y = (i % cols) * cell, (i // cols) * (cell + 18)
            S.paste(im, (x + 3, y + 3))
            d.text((x + 4, y + cell), f"{start + i}: u{m['usage']} {m['w']}x{m['h']} {m['license'][:12]}", fill="black")
        except Exception as e:
            print("fail", m["title"], e, flush=True)
    S.save(out or f"/tmp/{key}.png")


if __name__ == "__main__":
    key, out = sys.argv[1], sys.argv[2]
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    sheet(key, out=out, start=start)
