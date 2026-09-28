"""Minimal reader for VTK XML PolyData (.vtp) files (ascii or zlib-compressed binary)."""
import base64
import re
import struct
import xml.etree.ElementTree as ET
import zlib

import numpy as np

_DT = {"Float32": np.float32, "Float64": np.float64, "Int32": np.int32, "Int64": np.int64,
       "UInt32": np.uint32, "UInt64": np.uint64, "UInt8": np.uint8, "Int8": np.int8}


def _read_array(da, root):
    dt = _DT[da.get("type")]
    fmt = da.get("format", "ascii")
    txt = (da.text or "").strip()
    if fmt == "ascii":
        return np.array(txt.split(), dtype=dt)
    comp = root.get("compressor")
    hdr_t = np.uint64 if root.get("header_type") == "UInt64" else np.uint32
    hs = np.dtype(hdr_t).itemsize
    raw = base64.b64decode(txt)
    if comp:
        nblocks = int(np.frombuffer(raw[:hs], hdr_t)[0])
        hlen = hs * (3 + nblocks)
        # header is base64-encoded separately from the data blocks
        hdr_b64 = int(np.ceil(hlen / 3) * 4)
        hdr = np.frombuffer(base64.b64decode(txt[:hdr_b64])[:hlen], hdr_t)
        sizes = hdr[3:3 + nblocks]
        data = base64.b64decode(txt[hdr_b64:])
        out, pos = [], 0
        for s in sizes:
            out.append(zlib.decompress(data[pos:pos + int(s)]))
            pos += int(s)
        return np.frombuffer(b"".join(out), dt)
    n = int(np.frombuffer(raw[:hs], hdr_t)[0])
    return np.frombuffer(raw[hs:hs + n], dt)


def read(path):
    root = ET.parse(path).getroot()
    piece = root.find(".//Piece")
    pts = _read_array(piece.find("Points/DataArray"), root).astype(float).reshape(-1, 3)
    polys = piece.find("Polys")
    conn = off = None
    for da in polys.findall("DataArray"):
        if da.get("Name") == "connectivity":
            conn = _read_array(da, root).astype(int)
        elif da.get("Name") == "offsets":
            off = _read_array(da, root).astype(int)
    faces, start = [], 0
    for o in off:
        faces.append(conn[start:o].tolist())
        start = o
    return pts, faces
