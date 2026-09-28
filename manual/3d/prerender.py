"""Pre-render every pose image the manual uses (renders are cached; safe to re-run)."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import yaml  # noqa: E402

import fig3dhtml as F3  # noqa: E402


def jobs(which):
    A = yaml.safe_load((ROOT / "data/asanas.yaml").read_text())
    if "hero" in which:
        for a in A:
            yield dict(key=a["fig"], px=1100, muscles=a.get("muscles3d"))
    if "var" in which:
        for a in A:
            for v in a.get("variation_figs", []):
                yield dict(key=v["fig"], px=640)
    if "map" in which:
        for g in yaml.safe_load((ROOT / "data/mapping.yaml").read_text()):
            for r in g["rows"]:
                if r.get("fig"):
                    yield dict(key=r["fig"], px=260)
    if "seq" in which:
        import re
        keys = []
        for k, v in yaml.safe_load((ROOT / "data/sequences.yaml").read_text()).items():
            keys += [x[0] for x in v]
        for f in (ROOT / "src").glob("*.md"):
            for m in re.findall(r"!sequence\(([^)]*)\)", f.read_text()):
                if not m.startswith("@"):
                    keys += [p.split("=")[0].strip() for p in m.split(";") if "=" in p]
        for k in dict.fromkeys(keys):
            yield dict(key=k, px=300)


if __name__ == "__main__":
    which = sys.argv[1:] or ["hero", "var", "map", "seq"]
    seen = set()
    for j in jobs(which):
        sig = repr(sorted(j.items(), key=str))
        if sig in seen:
            continue
        seen.add(sig)
        t = time.time()
        k = j.pop("key")
        info = F3.render(k, **j)
        print(f"{time.time() - t:6.1f}s  {info['file']}", flush=True)
