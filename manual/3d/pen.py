"""Which body parts go below the floor / carry the lowest points (development aid)."""
import sys
import numpy as np
import poses3d
import rig
import solve


def report(name):
    spec = poses3d.P[name]
    P, t = solve.solve(spec)
    m, G = rig.posed(P)
    V = m.skin_blend(G) + t
    dom = m.widx[np.arange(len(V)), np.argmax(m.wval, axis=1)]
    low = np.argsort(V[:, 2])[:400]
    parts = {}
    for i in low:
        b = m.names[dom[i]]
        parts.setdefault(b, []).append(V[i, 2])
    print(name)
    for b, zs in sorted(parts.items(), key=lambda kv: min(kv[1]))[:10]:
        print(f"   {b:16s} min z {min(zs):+.3f}  n={len(zs)}")


if __name__ == "__main__":
    for n in sys.argv[1].split(","):
        report(n)
