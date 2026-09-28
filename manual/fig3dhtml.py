"""
HTML/SVG helpers that place the rendered 3D figures (3d/fig3d.py) in the manual.

    img(key, max_w, max_h)   -> <img> sized in mm to fit the box
    box(key, w, h)           -> the image centred in a fixed w × h mm panel (sequence strips)
    svg_image(info, x, y, w) -> <image> element for use inside an SVG composition
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "3d"))

import fig3d  # noqa: E402
import muscles3d  # noqa: E402

WORK = muscles3d.WORK
STRETCH = muscles3d.STRETCH


def render(key, px=800, muscles=None, view=None, palette="default", overrides=None, samples=64, margin=0.04, crop=None):
    extra, ov = None, ()
    if muscles:
        items = [(r, k) for k in muscles for r in muscles[k]]  # k: "work", "stretch" or a colour
        extra, ov = muscles3d.overlay_attrs(items)
    return fig3d.pose_image(key, width=px, view=tuple(view) if view else None, palette=palette, overlays=ov,
                            extra_attrs=extra, spec_overrides=overrides, samples=samples, margin=margin, crop=crop)


def fit(info, max_w, max_h):
    ar = info["h"] / info["w"]
    w = min(max_w, max_h / ar)
    return w, w * ar


def img(key, max_w, max_h, px=800, cls="fig3d", **kw):
    info = render(key, px, **kw)
    w, h = fit(info, max_w, max_h)
    return f'<img class="{cls}" src="{info["file"]}" style="width:{w:.2f}mm;height:{h:.2f}mm" alt="">'


def box(key, bw, bh, px=300, pad=1.0, **kw):
    info = render(key, px, **kw)
    w, h = fit(info, bw - 2 * pad, bh - 2 * pad)
    return (f'<div class="ph" style="width:{bw}mm;height:{bh}mm"><img src="{info["file"]}" '
            f'style="width:{w:.2f}mm;height:{h:.2f}mm;margin-top:{(bh - h) / 2:.2f}mm" alt=""></div>')


def svg_image(info, x, y, w):
    """<image> of width w (user units) at (x, y); returns (element, height, project) where
    project(xyz) gives SVG user coordinates of a 3D point."""
    h = w * info["h"] / info["w"]

    def project(p):
        u, v = info["project"](p)
        return x + u * w, y + v * h
    return f'<image href="{info["file"]}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"/>', h, project
