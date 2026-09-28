"""
Figures for the muscle atlas cards: each muscle is shown either painted on the body model
(superficial muscles, and deep muscles as their surface projection) or, where the OpenSim model
provides its path, as a muscle on the skeleton.
"""
import numpy as np

import fig3dhtml as F3

MUSCLE = "#B5533C"
MUSCLE2 = "#3F6F9C"
BACK, FRONT, RSIDE, LSIDE = (270, 4), (90, 4), (0, 4), (180, 4)

# name -> ("paint", pose, view, {colour: [regions]}, note) | ("bones", builder name, note)
ATLAS = {
    "Diaphragm": ("bones", "diaphragm", "deep: inside the rib cage"),
    "Rectus abdominis": ("paint", "front", FRONT, {MUSCLE: ["rectus_abdominis"]}, ""),
    "Transversus abdominis": ("paint", "front", (60, 4), {MUSCLE: ["transversus"]}, "deep: shown projected to the surface"),
    "External and internal obliques": ("paint", "front", (55, 4), {MUSCLE: ["obliques"]}, ""),
    "Erector spinae": ("paint", "tadasana", BACK, {MUSCLE: ["erector_spinae"]}, ""),
    "Multifidus": ("paint", "tadasana", BACK, {MUSCLE: ["multifidus"]}, "deep: shown projected to the surface"),
    "Quadratus lumborum": ("paint", "tadasana", BACK, {MUSCLE: ["quadratus_lumborum"]}, "deep: shown projected to the surface", (0.80, 1.40, 0.24)),
    "Psoas major": ("bones", "psoas", "deep: lumbar spine to femur"),
    "Iliacus": ("bones", "iliacus", "deep: iliac fossa to femur"),
    "Gluteus maximus": ("paint", "tadasana", BACK, {MUSCLE: ["gluteus_maximus"]}, ""),
    "Gluteus medius and minimus": ("paint", "front_arms_out", (320, 4), {MUSCLE: ["gluteus_medius"]}, "medius shown; minimus lies beneath it", (0.62, 1.15, 0.26)),
    "Deep hip rotators": ("bones", "rotators", "deep to gluteus maximus"),
    "Adductors": ("paint", "legs_apart", FRONT, {MUSCLE: ["adductors"]}, "legs apart to show the inner thigh", (0.40, 1.00, 0.26)),
    "Tensor fasciae latae": ("paint", "front_arms_out", (20, 4), {MUSCLE: ["tensor_fasciae_latae"], "#C9A774": ["it_band"]}, "with the iliotibial band (gold)", (0.40, 1.08, 0.24)),
    "Hamstrings": ("paint", "tadasana", BACK, {MUSCLE: ["hamstrings"]}, "", (0.38, 1.02, 0.22)),
    "Quadriceps femoris": ("paint", "tadasana", FRONT, {MUSCLE: ["quadriceps"]}, "", (0.38, 1.02, 0.22)),
    "Gastrocnemius": ("paint", "tadasana", BACK, {MUSCLE: ["gastrocnemius"]}, ""),
    "Soleus": ("paint", "tadasana", (230, 4), {MUSCLE: ["soleus"]}, "largely deep to gastrocnemius"),
    "Tibialis anterior": ("paint", "front", (60, 4), {MUSCLE: ["tibialis_anterior"]}, ""),
    "Latissimus dorsi": ("paint", "front_arms_out", BACK, {MUSCLE: ["latissimus"]}, "", (0.86, 1.62, 0.30)),
    "Trapezius": ("paint", "tadasana", BACK, {MUSCLE: ["trapezius"]}, ""),
    "Rhomboids": ("paint", "tadasana", BACK, {MUSCLE: ["rhomboids"]}, "deep to trapezius"),
    "Serratus anterior": ("paint", "front_arms_out", (25, 6), {MUSCLE: ["serratus"]}, "", (0.95, 1.62, 0.28)),
    "Rotator cuff": ("paint", "tadasana", BACK, {MUSCLE: ["rotator_cuff"]}, "posterior cuff projected; subscapularis lies in front of the scapula"),
    "Pectoralis major and minor": ("paint", "front", FRONT, {MUSCLE: ["pectorals"]}, "minor lies deep to major"),
    "Deltoid": ("paint", "tadasana", (35, 4), {MUSCLE: ["deltoid"]}, "", (1.05, 1.70, 0.28)),
    "Biceps brachii": ("paint", "front", FRONT, {MUSCLE: ["biceps"]}, ""),
    "Triceps brachii": ("paint", "tadasana", BACK, {MUSCLE: ["triceps"]}, ""),
    "Forearm flexors and extensors": ("paint", "front", (90, 4), {MUSCLE: ["forearm_flexors_sup"], MUSCLE2: ["forearm_extensors_sup"]}, "palms forward: flexors (red) on the front and inner side; extensors (blue) lie on the back", (0.72, 1.25, 0.32)),
    "Sternocleidomastoid": ("paint", "front", (50, 4), {MUSCLE: ["scm"]}, ""),
    "Scalenes": ("paint", "front", (40, 4), {MUSCLE: ["scalenes"]}, "deep: shown projected to the surface"),
    "Levator scapulae": ("paint", "tadasana", (230, 4), {MUSCLE: ["levator_scapulae"]}, "deep to trapezius; shown projected"),
    "Suboccipitals and deep neck flexors": ("paint", "tadasana", BACK, {MUSCLE: ["suboccipitals"]}, "suboccipitals projected; deep flexors lie in front of the spine"),
}

# which part of the body to frame: z range (metres) of the standing figure
FRAME = {"trunk": (0.80, 1.50), "hip": (0.55, 1.15), "thigh": (0.35, 1.05), "leg": (0.0, 0.62),
         "shoulder": (0.95, 1.70), "neck": (1.30, 1.72)}


# extra standing pose for the atlas: anatomical position with the legs apart
POSES = {"legs_apart": {"view": (90, 2), "shoulder": (0, 12, 8), "forearm": -78, "hand": "relaxed",
                        "hip": (0, 16, 0), "free": [("ankle", 1, -25, 25)],
                        "contacts": [("heel_L", "z", 0), ("heel_R", "z", 0), ("ball_L", "z", 0), ("ball_R", "z", 0)]}}


def image(name, group, w_mm=34):
    spec = ATLAS.get(name)
    if spec is None:
        return ""
    if spec[0] == "paint":
        _, pose, view, cols, note = spec[:5]
        crop = tuple(spec[5]) if len(spec) > 5 else FRAME.get(group)
        info = F3.render(POSES.get(pose, pose), 520, muscles=cols, view=view, palette="ghost", crop=crop)
        h = w_mm * info["h"] / info["w"]
        if h > 70:
            w_mm = 70 * info["w"] / info["h"]
            h = 70
        img = f'<img src="{info["file"]}" style="width:{w_mm:.1f}mm;height:{h:.1f}mm;display:block;margin:0 auto" alt="">'
    else:
        import anatfigs
        _, key, note = spec
        info = anatfigs.atlas_scene(key)
        h = w_mm * info["h"] / info["w"]
        if h > 60:
            w_mm = 60 * info["w"] / info["h"]
            h = 60
        img = f'<img src="{info["file"]}" style="width:{w_mm:.1f}mm;height:{h:.1f}mm;display:block;margin:0 auto" alt="">'
    cap = f'<div class="mnote">{note}</div>' if note else ""
    return img + cap
