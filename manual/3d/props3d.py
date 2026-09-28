"""
Simple prop meshes placed relative to the posed figure: yoga mat, block, folded
blanket, bolster, strap, chair and wall. Each builder returns (verts, faces, colour).
"""
import numpy as np

COL = {"mat": "#C9BC9F", "block": "#B7A27F", "blanket": "#D8CCB4", "blanket2": "#B9A98A", "bolster": "#8E9B78",
       "strap": "#B8914A", "chair": "#6E6A62", "chairseat": "#8A7F6E", "wall": "#EFE9DD"}


def box(center, size, yaw=0.0, bevel=0.0):
    """Axis-aligned box (optionally rotated about z) as quads; bevel handled by the renderer."""
    cx, cy, cz = center
    sx, sy, sz = np.asarray(size) / 2
    corners = np.array([[x, y, z] for z in (-sz, sz) for y in (-sy, sy) for x in (-sx, sx)])
    c, s = np.cos(yaw), np.sin(yaw)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    V = corners @ R.T + np.array([cx, cy, cz])
    F = [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]]
    return V, F


def cylinder(p0, p1, r, n=24):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ax = p1 - p0
    L = np.linalg.norm(ax)
    ax /= L
    u = np.cross(ax, [0, 0, 1.0])
    if np.linalg.norm(u) < 1e-6:
        u = np.cross(ax, [0, 1.0, 0])
    u /= np.linalg.norm(u)
    w = np.cross(ax, u)
    V, F = [], []
    for k in range(n):
        a = 2 * np.pi * k / n
        d = (np.cos(a) * u + np.sin(a) * w) * r
        V.append(p0 + d)
        V.append(p1 + d)
    for k in range(n):
        a0, b0 = 2 * k, 2 * k + 1
        a1, b1 = 2 * ((k + 1) % n), 2 * ((k + 1) % n) + 1
        F.append([a0, a1, b1, b0])
    c0 = len(V)
    V.append(p0)
    V.append(p1)
    for k in range(n):
        F.append([c0, 2 * ((k + 1) % n), 2 * k, 2 * k])
        F.append([c0 + 1, 2 * k + 1, 2 * ((k + 1) % n) + 1, 2 * ((k + 1) % n) + 1])
    return np.array(V), F


def tube(points, r, n=10):
    """A tube along a polyline (for straps)."""
    P = np.asarray(points, float)
    # smooth the polyline (Chaikin)
    for _ in range(3):
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]):
            Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1])
        P = np.array(Q)
    V, F = [], []
    prev = None
    for i, p in enumerate(P):
        t = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]
        t /= np.linalg.norm(t) + 1e-12
        u = np.cross(t, [0, 0, 1.0]) if prev is None else prev - t * prev.dot(t)
        if np.linalg.norm(u) < 1e-6:
            u = np.cross(t, [0, 1.0, 0])
        u /= np.linalg.norm(u)
        prev = u
        w = np.cross(t, u)
        for k in range(n):
            a = 2 * np.pi * k / n
            # flattened section: a strap is ~4x wider than thick
            V.append(p + np.cos(a) * u * r * 2.2 + np.sin(a) * w * r * 0.5)
    for i in range(len(P) - 1):
        for k in range(n):
            F.append([i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k])
    return np.array(V), F


def mat_for(verts, pad=0.12):
    """A 183 x 61 cm mat under the figure, along its longer horizontal extent."""
    lo, hi = verts.min(0), verts.max(0)
    ext = hi - lo
    along_x = ext[0] > ext[1]
    c = (lo + hi) / 2
    size = (1.83, 0.61, 0.006) if along_x else (0.61, 1.83, 0.006)
    return box((c[0], c[1], -0.003), size)


def chair(center_xy, seat, facing):
    """Folding chair with the seat top at height `seat`; `facing` is the yaw (radians) of the open side."""
    cx, cy = center_xy
    parts = []
    c, s = np.cos(facing), np.sin(facing)
    R = np.array([[c, -s], [s, c]])

    def xy(dx, dy):
        p = R @ np.array([dx, dy])
        return cx + p[0], cy + p[1]
    parts.append(box((*xy(0, 0), seat - 0.015), (0.42, 0.40, 0.03), facing) + ("chairseat",))
    parts.append(box((*xy(0, 0.19), seat + 0.20), (0.42, 0.025, 0.28), facing) + ("chair",))
    for dx in (-0.19, 0.19):
        for dy in (-0.18, 0.18):
            x, y = xy(dx, dy)
            parts.append(cylinder((x, y, 0), (x, y, seat - 0.03), 0.012, 12) + ("chair",))
        x, y = xy(dx, 0.19)
        parts.append(cylinder((x, y, seat), (x, y, seat + 0.34), 0.012, 12) + ("chair",))
    return parts
