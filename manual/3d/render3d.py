"""
Blender (bpy) renderer for the manual's figures.

Figures are rendered with Cycles on the CPU as soft, clay-like studio images on a
transparent background, with an optional soft contact shadow on the floor.
"""
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

# palette (linear-ish sRGB values are converted by Blender's colour management)
def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, 1.0)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 1
    sc.cycles.transparent_max_bounces = 8
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.threads_mode = "AUTO"
    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = srgb("#FFFFFF")
    bg.inputs[1].default_value = 0.08
    return sc


def material(name, color, rough=0.62, sss=0.0, alpha=1.0, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(color) if isinstance(color, str) else color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = 0.25
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (0.9, 0.45, 0.3)
        p.inputs["Subsurface Scale"].default_value = 0.012
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
    if emission:
        p.inputs["Emission Color"].default_value = srgb(emission)
        p.inputs["Emission Strength"].default_value = 0.35
    return m


def vcol_material(name, rough=0.6, sss=0.0):
    """Material whose base colour comes from the 'Col' colour attribute."""
    m = material(name, "#FFFFFF", rough, sss)
    nt = m.node_tree
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    nt.links.new(attr.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def _mix_rgba(nt, fac_socket, a, b):
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    ins = [s for s in mx.inputs if s.type == "RGBA"]
    outs = [s for s in mx.outputs if s.type == "RGBA"]
    nt.links.new(fac_socket, mx.inputs["Factor"])
    for sock, val in ((ins[0], a), (ins[1], b)):
        if isinstance(val, tuple):
            sock.default_value = val
        else:
            nt.links.new(val, sock)
    return outs[0]


def _attr(nt, name):
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    return a.outputs["Fac"]


def _step(nt, sock, edge=0.0, soft=0.0):
    """0/1 step of a field (optionally softened over `soft` metres)."""
    if soft <= 0:
        mth = nt.nodes.new("ShaderNodeMath")
        mth.operation = "GREATER_THAN"
        nt.links.new(sock, mth.inputs[0])
        mth.inputs[1].default_value = edge
        return mth.outputs[0]
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    nt.links.new(sock, mr.inputs["Value"])
    mr.inputs["From Min"].default_value = edge - soft
    mr.inputs["From Max"].default_value = edge + soft
    return mr.outputs["Result"]


def figure_material(name, skin, top, legs, overlays=(), rough=0.58, sss=0.08):
    """Skin with a fitted top and leggings (crisp edges from the 'top'/'legs' fields);
    optional overlays: list of (attribute, colour, opacity) blended on top."""
    m = material(name, skin, rough, sss)
    nt = m.node_tree
    col = srgb(skin)
    cur = _mix_rgba(nt, _step(nt, _attr(nt, "legs")), col, srgb(legs))
    cur = _mix_rgba(nt, _step(nt, _attr(nt, "top")), cur, srgb(top))
    for attr, colour, opacity in overlays:
        f = _step(nt, _attr(nt, attr), 0.0, 0.004)
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(f, mul.inputs[0])
        mul.inputs[1].default_value = opacity
        cur = _mix_rgba(nt, mul.outputs[0], cur, srgb(colour))
    nt.links.new(cur, nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def add_mesh(name, verts, faces, mat=None, colors=None, smooth=True, subdiv=1, attrs=None, fix_normals=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in np.asarray(verts, float)], [], [tuple(int(i) for i in f if i >= 0) for f in faces])
    me.update()
    if fix_normals:
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        me.update()
    if smooth:
        me.shade_smooth()
    if colors is not None:
        col = me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
        col.data.foreach_set("color", np.asarray(colors, np.float32).ravel())
    for an, av in (attrs or {}).items():
        at = me.attributes.new(an, "FLOAT", "POINT")
        at.data.foreach_set("value", np.asarray(av, np.float32))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if subdiv:
        mod = ob.modifiers.new("sub", "SUBSURF")
        mod.levels = subdiv
        mod.render_levels = subdiv
    return ob


def floor(z=0.0, size=40.0, shadow=True):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    ob = bpy.context.active_object
    ob.name = "floor"
    ob.is_shadow_catcher = True
    ob.visible_glossy = False
    return ob


def suns(key_dir=(-0.55, -0.8, 0.9), strength=1.0):
    """Scale-independent studio lighting with sun lamps (soft, angular size)."""
    def sun(name, direction, power, angle, color="#FFFFFF"):
        d = Vector(direction).normalized()
        ld = bpy.data.lights.new(name, "SUN")
        ld.energy = power * strength
        ld.angle = np.radians(angle)
        ld.color = srgb(color)[:3]
        ob = bpy.data.objects.new(name, ld)
        ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.collection.objects.link(ob)
    sun("key", key_dir, 3.2, 30, "#FFF4E6")
    sun("fill", (0.9, -0.5, 0.25), 0.9, 60, "#EEF2FF")
    sun("rim", (0.25, 1.0, 0.8), 1.6, 25, "#FFFFFF")
    sun("top", (0.05, 0.05, 1.0), 0.6, 60, "#FFFFFF")


def lights(center, radius, key_dir=(-0.55, -0.8, 0.9), strength=1.0):
    """Three-light studio set-up scaled to the subject size."""
    c = Vector(center)
    def area(name, direction, power, size, color="#FFFFFF"):
        d = Vector(direction).normalized()
        loc = c + d * radius * 4.0
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = power * (radius * 4.0) ** 2 * strength / 16.0
        ld.size = size * radius
        ld.color = srgb(color)[:3]
        ob = bpy.data.objects.new(name, ld)
        ob.location = loc
        ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.collection.objects.link(ob)
        return ob
    area("key", key_dir, 120.0, 2.2, "#FFF4E6")
    area("fill", (0.9, -0.5, 0.25), 30.0, 3.5, "#EEF2FF")
    area("rim", (0.25, 1.0, 0.8), 70.0, 1.5, "#FFFFFF")
    area("top", (0.0, 0.0, 1.0), 20.0, 4.0, "#FFFFFF")


def camera(target, direction, ortho_scale, clip=100.0):
    """Orthographic camera looking at target from `direction` (pointing from target to camera)."""
    d = Vector(direction).normalized()
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ortho_scale
    cd.clip_end = clip
    ob = bpy.data.objects.new("cam", cd)
    ob.location = Vector(target) + d * 20.0
    up = "Y"
    ob.rotation_euler = (-d).to_track_quat("-Z", up).to_euler()
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def render(path, res=(900, 900), samples=48):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path
