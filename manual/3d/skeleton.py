"""
Full-body skeleton (and lower-limb muscle paths) from the OpenSim full-body model of
Rajagopal et al. (2016), whose bone geometry derives from Delp et al. (1990) and
Holzbaur et al. (2005); models distributed with OpenSim (opensim-models), CC BY 3.0.

The skeleton is assembled in its default (anatomical, standing) configuration and returned
in the manual's frame: X = figure's left, -Y = anterior, Z = up (metres, feet on z = 0).
"""
import json
import urllib.request
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as Rot

import vtp

HERE = Path(__file__).resolve().parent
OS = HERE / "osim"
GEOM = OS / "geometry"
MODEL = OS / "Rajagopal2016.osim"
RAW = "https://raw.githubusercontent.com/opensim-org/opensim-models/master/Geometry/"


def to_ours(p):
    """OpenSim (X anterior, Y up, Z right) -> manual frame (X left, -Y anterior, Z up)."""
    p = np.asarray(p, float)
    return np.stack([-p[..., 2], -p[..., 0], p[..., 1]], axis=-1)


def _vec(s):
    return np.array([float(x) for x in s.split()])


def _xform(trans, orient):
    M = np.eye(4)
    M[:3, :3] = Rot.from_euler("XYZ", orient).as_matrix()  # OpenSim body-fixed X-Y-Z
    M[:3, 3] = trans
    return M


def _mesh(name):
    GEOM.mkdir(parents=True, exist_ok=True)
    f = GEOM / name
    if not f.exists():
        urllib.request.urlretrieve(RAW + name, f)
    return vtp.read(f)


@lru_cache(None)
def _model():
    root = ET.parse(MODEL).getroot()
    bodies = {}
    for b in root.find(".//BodySet/objects"):
        geoms = []
        ag = b.find("attached_geometry")
        if ag is not None:
            for mesh in ag.findall("Mesh"):
                geoms.append((mesh.find("mesh_file").text.strip(), _vec(mesh.find("scale_factors").text)))
        bodies[b.get("name")] = geoms
    joints = []
    for j in root.find(".//JointSet/objects"):
        frames = {}
        for fr in j.find("frames"):
            frames[fr.get("name")] = (fr.find("socket_parent").text.split("/")[-1],
                                      _xform(_vec(fr.find("translation").text), _vec(fr.find("orientation").text)))
        par = j.find("socket_parent_frame").text
        ch = j.find("socket_child_frame").text
        joints.append((j.get("name"), frames[par], frames[ch]))
    return root, bodies, joints


@lru_cache(None)
def body_transforms():
    """Ground transforms (OpenSim frame) of every body with all coordinates at zero."""
    root, bodies, joints = _model()
    X = {"ground": np.eye(4)}
    pending = list(joints)
    while pending:
        rest = []
        for name, (pb, poff), (cb, coff) in pending:
            if pb in X:
                X[cb] = X[pb] @ poff @ np.linalg.inv(coff)
            else:
                rest.append((name, (pb, poff), (cb, coff)))
        if len(rest) == len(pending):
            break
        pending = rest
    return X


@lru_cache(None)
def bones():
    """{body: [(mesh_file, verts (manual frame), faces)]} in the default standing pose."""
    root, bodies, joints = _model()
    X = body_transforms()
    out = {}
    for b, geoms in bodies.items():
        if b not in X:
            continue
        lst = []
        for mf, sc in geoms:
            P, F = _mesh(mf)
            P = P * sc
            Pg = (X[b][:3, :3] @ P.T).T + X[b][:3, 3]
            lst.append((mf, to_ours(Pg), F))
        out[b] = lst
    # stand on the floor
    zmin = min(v[:, 2].min() for lst in out.values() for _, v, _ in lst)
    for lst in out.values():
        for k, (mf, v, F) in enumerate(lst):
            lst[k] = (mf, v - np.array([0, 0, zmin]), F)
    return out


@lru_cache(None)
def floor_offset():
    root, bodies, joints = _model()
    X = body_transforms()
    zmin = np.inf
    for b, geoms in bodies.items():
        if b in X:
            for mf, sc in geoms:
                P, F = _mesh(mf)
                Pg = (X[b][:3, :3] @ (P * sc).T).T + X[b][:3, 3]
                zmin = min(zmin, to_ours(Pg)[:, 2].min())
    return zmin


def point(body, loc):
    """A point given in a body's OpenSim frame -> manual frame (standing on the floor)."""
    X = body_transforms()[body]
    p = X[:3, :3] @ np.asarray(loc, float) + X[:3, 3]
    return to_ours(p) - np.array([0, 0, floor_offset()])


@lru_cache(None)
def muscles():
    """Lower-limb muscle paths: {name: dict(points=[xyz...], F=max force, l0=fibre length, ts=tendon slack)}."""
    root, bodies, joints = _model()
    out = {}
    for mu in root.iter():
        if not mu.tag.endswith("Muscle"):
            continue
        name = mu.get("name")
        pts = []
        pps = mu.find(".//PathPointSet/objects")
        if pps is None:
            continue
        for pp in pps:
            loc = pp.find("location")
            if loc is None:
                continue
            body = pp.find("socket_parent_frame").text.split("/")[-1]
            pts.append(point(body, _vec(loc.text)))

        def g(tag, default=0.0):
            e = mu.find(tag)
            return float(e.text) if e is not None else default
        out[name] = dict(points=np.array(pts), F=g("max_isometric_force"), l0=g("optimal_fiber_length"),
                         ts=g("tendon_slack_length"))
    return out


if __name__ == "__main__":
    B = bones()
    for b, lst in B.items():
        for mf, v, F in lst:
            print(f"{b:10s} {mf:26s} {len(v):6d} z {v[:, 2].min():.3f}..{v[:, 2].max():.3f}  x {v[:, 0].min():+.3f}..{v[:, 0].max():+.3f}")
    M = muscles()
    print(len(M), "muscles;", sorted(M)[:12])
