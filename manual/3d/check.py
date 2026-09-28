"""Report contact/pair errors for all poses (development aid)."""
import sys
import numpy as np
import landmarks
import poses3d
import rig
import solve


def errors(name):
    spec = poses3d.P[name]
    P, t = solve.solve(spec)
    m, G = rig.posed(P)
    L = landmarks.landmarks()
    out = []
    for c in spec.get("contacts", []):
        if c[1] == "z":
            reg = np.array(landmarks.region(c[0]), int)
            e = (m.skin_idx(G, reg) + t)[:, 2].min() - c[2]
        else:
            p = m.skin_idx(G, [L[c[0]]])[0] + t
            e = p[solve.AX[c[1]]] - c[2]
        if abs(e) > 0.02:
            out.append(f"{c[0]}.{c[1]} {e:+.3f}")
    for a, b, *_ in spec.get("pairs", []):
        pa = m.skin_idx(G, [L[a]])[0] + t
        pb = m.skin_idx(G, [L[b]])[0] + t
        d = np.linalg.norm(pa - pb)
        if d > 0.04:
            out.append(f"{a}~{b} {d:.3f}")
    fr = [f"{f[0]}[{f[1]}]={solve._get(P, f[0], f[1]):.0f}" + ("*" if abs(solve._get(P, f[0], f[1]) - f[2]) < 0.5 or abs(solve._get(P, f[0], f[1]) - f[3]) < 0.5 else "")
          for f in spec.get("free", [])]
    return out, fr


if __name__ == "__main__":
    names = sys.argv[1].split(",") if len(sys.argv) > 1 else list(poses3d.P)
    for n in names:
        e, fr = errors(n)
        flag = "!!" if e else "ok"
        print(f"{flag} {n:24s} {'; '.join(e)}")
        if e:
            print("      ", " ".join(x for x in fr if x.endswith("*")))
