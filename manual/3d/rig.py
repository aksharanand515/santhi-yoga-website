"""
Anatomical rig for the MakeHuman base mesh.

Poses are written as joint angles in degrees, measured from the anatomical
neutral position (standing upright, arms hanging by the sides with the palms
facing the thighs, legs straight and parallel):

    lumbar / thoracic / cervical / head : (flexion, lateral flexion to the left, rotation to the left)
    hip_L, hip_R          : (flexion, abduction, external rotation)
    knee_L, knee_R        : flexion
    ankle_L, ankle_R      : (dorsiflexion, inversion)
    toes_L, toes_R        : extension (toes bent up)
    clav_L, clav_R        : (elevation, protraction) of the shoulder girdle
    shoulder_L, shoulder_R: (flexion, abduction, external rotation)
    elbow_L, elbow_R      : flexion
    forearm_L, forearm_R  : pronation (+) / supination (-)
    wrist_L, wrist_R      : (extension, radial deviation)
    hand_L, hand_R        : "relaxed" | "flat" | "spread" | "grip" | "fist" | "mudra" | float curl

and a root orientation for the pelvis: root=(yaw, pitch, roll) where pitch +90
tips the body face-down (prone) and -90 lays it face-up (supine), yaw turns the
body to its left about the vertical, and roll tips it towards its left side.

Coordinates: X = figure's left, -Y = anterior (front), Z = up, metres.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as Rot

import mhmodel

HERE = Path(__file__).resolve().parent
NEUTRAL_CACHE = HERE / "cache" / "neutral.npz"
D2R = np.pi / 180

EX = np.array([1.0, 0, 0])
EY = np.array([0, 1.0, 0])
EZ = np.array([0, 0, 1.0])


# ----------------------------------------------------------------------------- transforms
def rotv(axis, deg):
    return Rot.from_rotvec(np.asarray(axis, float) * deg * D2R).as_matrix()


def about(R, h):
    """4x4 matrix rotating by R about point h."""
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = h - R @ h
    return M


def min_rot(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    s = np.linalg.norm(v)
    c = float(np.dot(a, b))
    if s < 1e-9:
        return np.eye(3) if c > 0 else rotv(np.cross(a, [1, 0, 0]) if abs(a[0]) < .9 else np.cross(a, [0, 1, 0]), 180)
    return Rot.from_rotvec(v / s * np.arctan2(s, c)).as_matrix()


class Model:
    def __init__(self, d):
        self.verts = d["verts"]
        self.quads = d["quads"]
        self.part = d["part"]
        self.names = [str(n) for n in d["names"]]
        self.idx = {n: i for i, n in enumerate(self.names)}
        self.parents = d["parents"]
        self.heads = d["heads"]
        self.tails = d["tails"]
        self.widx = d["widx"]
        self.wval = d["wval"]
        self.nb = len(self.names)

    def i(self, n):
        return self.idx[n]

    # FK: local rotations (in rest-space axes, about the bone head) -> global 4x4 transforms
    def fk(self, local, root=np.eye(4)):
        G = np.zeros((self.nb, 4, 4))
        for b in range(self.nb):
            L = about(local[b], self.heads[b])
            p = self.parents[b]
            G[b] = (root if p < 0 else G[p]) @ L
        return G

    def blend_weights(self):
        """Per-vertex share of dual-quaternion skinning (rest is linear blend)."""
        if not hasattr(self, "_blend"):
            sh = [self.i(n) for n in self.names if n.split(".")[0] in ("clavicle", "shoulder01", "upperarm01")]
            w = np.zeros(len(self.verts))
            for k in range(self.widx.shape[1]):
                w += np.where(np.isin(self.widx[:, k], sh), self.wval[:, k], 0)
            self._blend = np.clip(0.55 - w * 1.4, 0.12, 0.55)[:, None]
        return self._blend

    def skin_idx(self, G, I):
        """Blended skinning of a subset of vertices."""
        I = np.asarray(I)
        V = self.verts[I]
        a = self.skin(G, verts=V, idx=I, dqs=False)
        b = dq_skin(G, V, self.widx[I], self.wval[I])
        f = self.blend_weights()[I]
        return a * (1 - f) + b * f

    def skin_blend(self, G):
        a = self.skin(G, dqs=False)
        b = self.skin(G, dqs=True)
        f = self.blend_weights()
        return a * (1 - f) + b * f

    def skin(self, G, verts=None, idx=None, dqs=True):
        V = self.verts if verts is None else verts
        wi = self.widx if idx is None else self.widx[idx]
        wv = self.wval if idx is None else self.wval[idx]
        if idx is not None and verts is None:
            V = self.verts[idx]
        if not dqs:
            Vh = np.concatenate([V, np.ones((len(V), 1))], 1)
            out = np.zeros_like(V)
            for k in range(wi.shape[1]):
                T = G[wi[:, k]]
                out += wv[:, k:k + 1] * np.einsum("nij,nj->ni", T[:, :3, :], Vh)
            return out
        return dq_skin(G, V, wi, wv)


# ----------------------------------------------------------------------------- dual quaternion skinning
def _mat_to_dq(G):
    q = Rot.from_matrix(G[:, :3, :3]).as_quat()  # x y z w
    q = np.concatenate([q[:, 3:4], q[:, :3]], 1)  # w x y z
    t = G[:, :3, 3]
    tq = np.concatenate([np.zeros((len(t), 1)), t], 1)
    d = 0.5 * _qmul(tq, q)
    return q, d


def _qmul(a, b):
    w1, x1, y1, z1 = a.T
    w2, x2, y2, z2 = b.T
    return np.stack([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                     w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                     w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2], 1)


def dq_skin(G, V, wi, wv):
    q, d = _mat_to_dq(G)
    Q = q[wi]  # n,k,4
    Dd = d[wi]
    # hemisphere alignment with the first influence
    s = np.sign(np.einsum("nkj,nj->nk", Q, Q[:, 0, :]))
    s[s == 0] = 1
    w = wv * s
    b0 = np.einsum("nk,nkj->nj", w, Q)
    be = np.einsum("nk,nkj->nj", w, Dd)
    nrm = np.linalg.norm(b0, axis=1, keepdims=True)
    b0 /= nrm
    be /= nrm
    w0, v0 = b0[:, :1], b0[:, 1:]
    we, ve = be[:, :1], be[:, 1:]
    # rotate
    out = V + 2 * np.cross(v0, np.cross(v0, V) + w0 * V)
    # translate
    t = 2 * (w0 * ve - we * v0 + np.cross(v0, ve))
    return out + t


# ----------------------------------------------------------------------------- neutral pose
def _seg_dir(m, G, a, b):
    """Posed direction from head of bone a to tail of bone b."""
    ha = (G[m.i(a)] @ np.append(m.heads[m.i(a)], 1))[:3]
    tb = (G[m.i(b)] @ np.append(m.tails[m.i(b)], 1))[:3]
    return tb - ha


def _pt(m, G, bone, which="tail"):
    p = m.tails[m.i(bone)] if which == "tail" else m.heads[m.i(bone)]
    return (G[m.i(bone)] @ np.append(p, 1))[:3]


def build_neutral():
    m = Model(mhmodel.load())
    local = np.tile(np.eye(3), (m.nb, 1, 1))

    def glob_rot(G, b):
        return G[m.i(b)][:3, :3]

    def correct(bone, first, last, target):
        """Rotate `bone` so that the segment head(first)->tail(last) points along target (world)."""
        nonlocal local
        G = m.fk(local)
        p = m.parents[m.i(bone)]
        Rp = G[p][:3, :3] if p >= 0 else np.eye(3)
        cur = _seg_dir(m, G, first, last)
        C = min_rot(cur, np.asarray(target, float))
        local[m.i(bone)] = Rp.T @ C @ Rp @ local[m.i(bone)]

    def twist(bone, axis_first, axis_last, probe_bone, want, share=None):
        """Twist `bone` about the segment axis so that probe (tail of probe_bone) lies towards `want`."""
        nonlocal local
        G = m.fk(local)
        h = _pt(m, G, axis_first, "head")
        ax = _seg_dir(m, G, axis_first, axis_last)
        ax /= np.linalg.norm(ax)
        pr = _pt(m, G, probe_bone, "tail") - h
        pr -= ax * pr.dot(ax)
        wt = np.asarray(want, float) - ax * np.dot(want, ax)
        ang = np.arctan2(np.dot(np.cross(pr, wt), ax), np.dot(pr, wt))
        bones = share or [(bone, 1.0)]
        for bn, f in bones:
            p = m.parents[m.i(bn)]
            Rp = G[p][:3, :3]
            R = Rot.from_rotvec(ax * ang * f).as_matrix()
            local[m.i(bn)] = Rp.T @ R @ Rp @ local[m.i(bn)]
            G = m.fk(local)

    for s, sx in (("L", 1), ("R", -1)):
        # legs: thighs nearly vertical (knees slightly in), shins vertical
        correct(f"upperleg01.{s}", f"upperleg01.{s}", f"upperleg02.{s}", [-sx * 0.02, 0.0, -1])
        correct(f"lowerleg01.{s}", f"lowerleg01.{s}", f"lowerleg02.{s}", [-sx * 0.005, 0.012, -1])
        # feet: keep the rest pitch, point forward with a little toe-out
        G = m.fk(local)
        f = _seg_dir(m, G, f"foot.{s}", f"toe2-1.{s}")
        horiz = np.hypot(f[0], f[1])
        correct(f"foot.{s}", f"foot.{s}", f"toe2-1.{s}", [sx * horiz * np.sin(6 * D2R), -horiz * np.cos(6 * D2R), f[2]])
        # arms: hanging, slightly away from the body; forearms nearly straight
        correct(f"upperarm01.{s}", f"upperarm01.{s}", f"upperarm02.{s}", [sx * np.sin(7 * D2R), 0.02, -np.cos(7 * D2R)])
        correct(f"lowerarm01.{s}", f"lowerarm01.{s}", f"lowerarm02.{s}", [sx * 0.10, -0.06, -1])
        # hand in line with the forearm
        correct(f"wrist.{s}", f"wrist.{s}", f"finger3-1.{s}", _seg_dir(m, m.fk(local), f"lowerarm01.{s}", f"lowerarm02.{s}"))
        # palms facing the thighs: thumb points forward
        twist(f"lowerarm01.{s}", f"lowerarm01.{s}", f"lowerarm02.{s}", f"finger1-3.{s}", [0, -1, 0],
              share=[(f"lowerarm01.{s}", 0.25), (f"lowerarm02.{s}", 0.45), (f"wrist.{s}", 0.30)])

    G = m.fk(local)
    V = m.skin(G, dqs=False)
    heads = np.array([(G[b] @ np.append(m.heads[b], 1))[:3] for b in range(m.nb)])
    tails = np.array([(G[b] @ np.append(m.tails[b], 1))[:3] for b in range(m.nb)])

    # The base mesh's arms are short against adult anthropometry (humerus ~0.172 x stature,
    # forearm ~0.146 x stature). Lengthen the upper arm and forearm smoothly along their axes.
    def chain_share(side, names):
        ids = [m.i(f"{n}.{side}") for n in names]
        w = np.zeros(len(V))
        for k in range(m.widx.shape[1]):
            w += np.where(np.isin(m.widx[:, k], ids), m.wval[:, k], 0)
        return w

    for s in "LR":
        sh = heads[m.i(f"upperarm01.{s}")]
        el = heads[m.i(f"lowerarm01.{s}")]
        wr = heads[m.i(f"wrist.{s}")]
        for (a, b, extra, below) in ((sh, el, 0.055, ["upperarm01", "upperarm02", "lowerarm01", "lowerarm02", "wrist"]),
                                      (el, wr, 0.018, ["lowerarm01", "lowerarm02", "wrist"])):
            ax = (b - a) / np.linalg.norm(b - a)
            Ls = np.linalg.norm(b - a)
            share = chain_share(s, below)
            # fingers and metacarpals follow the wrist
            fing = [n for n in m.names if n.endswith("." + s) and (n.startswith("finger") or n.startswith("metacarpal"))]
            ids = [m.i(n) for n in fing]
            for k in range(m.widx.shape[1]):
                share += np.where(np.isin(m.widx[:, k], ids), m.wval[:, k], 0)
            tt = np.clip(((V - a) @ ax) / Ls, 0, 1)
            V += (np.clip(share, 0, 1) * tt)[:, None] * ax * extra
            for arr in (heads, tails):
                tj = np.clip(((arr - a) @ ax) / Ls, 0, 1)
                sel = np.array([n.endswith("." + s) and any(n.startswith(p) for p in below + ["finger", "metacarpal"]) for n in m.names])
                arr[sel] += (tj[sel])[:, None] * ax * extra
    # stand on the floor (z = 0)
    dz = -V[:, 2].min()
    V[:, 2] += dz
    heads[:, 2] += dz
    tails[:, 2] += dz
    NEUTRAL_CACHE.parent.mkdir(exist_ok=True)
    d = mhmodel.load()
    np.savez_compressed(NEUTRAL_CACHE, verts=V, quads=d["quads"], part=d["part"], names=d["names"],
                        parents=d["parents"], heads=heads, tails=tails, widx=d["widx"], wval=d["wval"])


REFINED_CACHE = HERE / "cache" / "neutral_sub.npz"


def build_refined():
    """Subdivide the neutral mesh once (Catmull-Clark, in Blender), carrying the skin weights."""
    import bpy
    d = np.load(NEUTRAL_CACHE)
    m = Model({k: d[k] for k in d.files})
    bpy.ops.wm.read_factory_settings(use_empty=True)
    me = bpy.data.meshes.new("n")
    me.from_pydata([tuple(v) for v in m.verts], [], [tuple(int(i) for i in f) for f in m.quads])
    me.update()
    pa = me.attributes.new("part", "INT", "FACE")
    pa.data.foreach_set("value", m.part.astype(np.int32))
    ob = bpy.data.objects.new("n", me)
    bpy.context.scene.collection.objects.link(ob)
    used = np.unique(m.widx)
    groups = {}
    for b in used:
        g = ob.vertex_groups.new(name=m.names[b])
        groups[b] = g
    for vi in range(len(m.verts)):
        for k in range(m.widx.shape[1]):
            w = float(m.wval[vi, k])
            if w > 0:
                groups[m.widx[vi, k]].add([vi], w, "REPLACE")
    mod = ob.modifiers.new("s", "SUBSURF")
    mod.levels = 1
    mod.render_levels = 1
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    em = ev.to_mesh()
    nv = len(em.vertices)
    V = np.zeros(nv * 3)
    em.vertices.foreach_get("co", V)
    V = V.reshape(-1, 3)
    Q = np.array([list(p.vertices) for p in em.polygons], int)
    part = np.zeros(len(em.polygons), np.int32)
    em.attributes["part"].data.foreach_get("value", part)
    name_of = {g.index: g.name for g in ob.vertex_groups}
    W = np.zeros((nv, 4), int)
    WV = np.zeros((nv, 4), np.float32)
    for vi, vert in enumerate(em.vertices):
        gs = sorted(((g.weight, m.i(name_of[g.group])) for g in vert.groups), reverse=True)[:4]
        s = sum(w for w, _ in gs) or 1.0
        for k, (w, b) in enumerate(gs):
            W[vi, k] = b
            WV[vi, k] = w / s
        if not gs:
            W[vi, 0] = m.i("head")
            WV[vi, 0] = 1.0
    ev.to_mesh_clear()
    np.savez_compressed(REFINED_CACHE, verts=V, quads=Q, part=part, names=d["names"], parents=d["parents"],
                        heads=d["heads"], tails=d["tails"], widx=W, wval=WV)


@lru_cache(None)
def neutral():
    if not NEUTRAL_CACHE.exists() or NEUTRAL_CACHE.stat().st_mtime < mhmodel.CACHE.stat().st_mtime:
        build_neutral()
    if not REFINED_CACHE.exists() or REFINED_CACHE.stat().st_mtime < NEUTRAL_CACHE.stat().st_mtime:
        build_refined()
    d = np.load(REFINED_CACHE)
    return Model({k: d[k] for k in d.files})


@lru_cache(None)
def neutral_coarse():
    if not NEUTRAL_CACHE.exists() or NEUTRAL_CACHE.stat().st_mtime < mhmodel.CACHE.stat().st_mtime:
        build_neutral()
    d = np.load(NEUTRAL_CACHE)
    return Model({k: d[k] for k in d.files})


if __name__ == "__main__":
    build_neutral()
    m = neutral()
    print("height", m.verts[:, 2].max())
    for b in ["upperleg01.L", "lowerleg01.L", "foot.L", "upperarm01.L", "lowerarm01.L", "wrist.L", "finger1-3.L"]:
        print(b, np.round(m.heads[m.i(b)], 3), np.round(m.tails[m.i(b)], 3))


# ----------------------------------------------------------------------------- anatomical degrees of freedom
def _axes(side=None):
    sx = 1 if side == "L" else -1
    return {
        "trunk": (EX, EY, EZ),
        "hip": (-EX, -sx * EY, sx * EZ),
        "knee": (EX,),
        "ankle": (-EX, sx * EY),
        "toes": (-EX,),
        "clav": (-sx * EY, -sx * EZ),
        "shoulder": (-EX, -sx * EY, sx * EZ),
        "elbow": (-EX,),
        "forearm": (-sx * EZ,),
        "wrist": (-sx * EY, -EX),
        "finger": (sx * EY,),
        "thumb": (-EX * 0.35 + sx * EY * 0.94,),
    }


def _R(axes, angles, share=1.0):
    R = np.eye(3)
    for a, t in zip(axes, angles):
        if t:
            R = R @ rotv(a, t * share)
    return R


HAND_PRESETS = {  # (finger curl per joint, thumb curl, spread)
    "relaxed": (18, 12, 0),
    "flat": (0, 0, 4),
    "spread": (-4, -10, 12),
    "grip": (62, 35, 0),
    "fist": (85, 45, 0),
    "mudra": (22, 30, 0),
    "cup": (38, 20, 0),
}

SPINE = {"lumbar": [("spine05", .34), ("spine04", .33), ("spine03", .33)],
         "thoracic": [("spine02", .5), ("spine01", .5)],
         "cervical": [("neck01", .35), ("neck02", .35), ("neck03", .30)],
         "head": [("head", 1.0)]}


def _vec(v, n):
    if v is None:
        return (0,) * n
    if np.isscalar(v):
        return (v,) + (0,) * (n - 1)
    v = tuple(v)
    return (v + (0,) * n)[:n]


def expand(pose):
    """Fill symmetric shortcuts: hip=(...) -> hip_L and hip_R, etc."""
    P = dict(pose)
    for k in ["hip", "knee", "ankle", "toes", "clav", "shoulder", "elbow", "forearm", "wrist", "hand"]:
        if k in P:
            v = P.pop(k)
            P.setdefault(k + "_L", v)
            P.setdefault(k + "_R", v)
    return P


def local_rotations(m, pose):
    P = expand(pose)
    local = np.tile(np.eye(3), (m.nb, 1, 1))

    def put(bone, R):
        b = m.i(bone)
        local[b] = local[b] @ R

    # spine
    for seg, bones in SPINE.items():
        ang = _vec(P.get(seg), 3)
        for bone, f in bones:
            put(bone, _R(_axes()["trunk"], ang, f))
    for s in "LR":
        A = _axes(s)
        # legs
        fl, ab, ro = _vec(P.get("hip_" + s), 3)
        put(f"upperleg01.{s}", _R(A["hip"], (fl, ab, ro * 0.6)))
        put(f"upperleg02.{s}", rotv(A["hip"][2], ro * 0.4))
        put(f"lowerleg01.{s}", rotv(A["knee"][0], _vec(P.get("knee_" + s), 1)[0]))
        dor, inv = _vec(P.get("ankle_" + s), 2)
        put(f"foot.{s}", _R(A["ankle"], (dor, inv)))
        te = _vec(P.get("toes_" + s), 1)[0]
        for t in range(1, 6):
            put(f"toe{t}-1.{s}", rotv(A["toes"][0], te))
        # arms
        el, pr = _vec(P.get("clav_" + s), 2)
        sf, sa, sr = _vec(P.get("shoulder_" + s), 3)
        # automatic shoulder-girdle rhythm when the arm is raised
        elev = np.degrees(np.arccos(np.clip(_R(A["shoulder"], (sf, sa, 0)) @ -EZ @ -EZ, -1, 1)))
        auto = max(0.0, elev - 60) * 0.12
        put(f"clavicle.{s}", _R(A["clav"], (el + auto, pr)))
        put(f"shoulder01.{s}", rotv(A["clav"][0], auto * 0.6))
        # keep the arm direction relative to the thorax: undo the girdle rotation at the shoulder joint
        girdle = _R(A["clav"], (el + auto * 1.6, pr))
        Rsh = _R(A["shoulder"], (sf, sa, sr * 0.6))
        # share part of large elevations with the shoulder cap (reduces skin collapse at the deltoid)
        k = float(np.clip((elev - 70) / 110, 0, 1)) * 0.28
        if k > 0:
            rv = Rot.from_matrix(Rsh).as_rotvec()
            cap = Rot.from_rotvec(rv * k).as_matrix()
            put(f"shoulder01.{s}", cap)
            put(f"upperarm01.{s}", girdle.T @ cap.T @ Rsh)
        else:
            put(f"upperarm01.{s}", girdle.T @ Rsh)
        put(f"upperarm02.{s}", rotv(A["shoulder"][2], sr * 0.4))
        put(f"lowerarm01.{s}", rotv(A["elbow"][0], _vec(P.get("elbow_" + s), 1)[0]))
        pn = _vec(P.get("forearm_" + s), 1)[0]
        put(f"lowerarm01.{s}", rotv(A["forearm"][0], pn * 0.2))
        put(f"lowerarm02.{s}", rotv(A["forearm"][0], pn * 0.45))
        put(f"wrist.{s}", rotv(A["forearm"][0], pn * 0.35))
        we, wr = _vec(P.get("wrist_" + s), 2)
        put(f"wrist.{s}", _R(A["wrist"], (we, wr)))
        h = P.get("hand_" + s, "relaxed")
        curl, thumb, spread = HAND_PRESETS[h] if isinstance(h, str) else (h, h * 0.5, 0)
        for f in range(2, 6):
            for j in (1, 2, 3):
                put(f"finger{f}-{j}.{s}", rotv(A["finger"][0], curl * (0.8 if j == 1 else 1.0)))
        for j in (1, 2, 3):
            put(f"finger1-{j}.{s}", rotv(A["thumb"][0], thumb * (0.5 if j == 1 else 1.0)))
    return local


def root_matrix(m, pose):
    yaw, pitch, roll = _vec(pose.get("root"), 3)
    R = rotv(EZ, yaw) @ rotv(EX, pitch) @ rotv(EY, roll)
    piv = (m.heads[m.i("upperleg01.L")] + m.heads[m.i("upperleg01.R")]) / 2
    return about(R, piv)


def posed(pose, m=None):
    m = m or neutral()
    G = m.fk(local_rotations(m, pose), root_matrix(m, pose))
    return m, G


def pose_mesh(pose, m=None):
    m, G = posed(pose, m)
    return m.skin_blend(G), G
