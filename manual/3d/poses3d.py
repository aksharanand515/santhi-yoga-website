"""
The pose library, written as anatomical joint angles (see rig.py for conventions).

Each entry may also carry:
    contacts / pairs / free   (see solve.py)
    view   : (azimuth, elevation) in degrees; azimuth 0 = the figure's right side
             (figure faces image-right), 90 = front, 180 = left side, -90 = back
    props  : list of prop dicts (see props3d.py)
"""
import copy

Z = "z"

# ------------------------------------------------------------------ helpers
FEET_FLAT = [("heel_L", Z, 0), ("heel_R", Z, 0), ("ball_L", Z, 0), ("ball_R", Z, 0)]
PALMS = [("palm_L", Z, 0), ("palm_R", Z, 0), ("fingertip_L", Z, 0.004, 0.6), ("fingertip_R", Z, 0.004, 0.6),
         ("wristpalm_L", Z, 0.012, 0.6), ("wristpalm_R", Z, 0.012, 0.6)]
TOES_TUCKED = [("toepad_L", Z, 0), ("toepad_R", Z, 0)]
# fingers pointing forward (the figure faces -y): fingertips ahead of the wrist
FWD = [("fingertip_L", "wristpalm_L", "y", -0.15, 0.5), ("fingertip_R", "wristpalm_R", "y", -0.15, 0.5)]
PRON = [("forearm", 0, 40, 120)]


def lr(a, b):
    return a, b


P = {}

# ------------------------------------------------------------------ standing
P["tadasana"] = dict(view=(0, 4), hand="relaxed", shoulder=(0, 2, 0), contacts=FEET_FLAT)

P["front"] = dict(view=(90, 2), shoulder=(0, 7, 8), forearm=-78, hand="relaxed", contacts=FEET_FLAT)

P["front_arms_out"] = dict(view=(90, 2), shoulder=(0, 90, 0), forearm=-80, hand="flat", contacts=FEET_FLAT)

P["arm_forward"] = dict(view=(0, 3), shoulder=(90, 4, 0), hand="flat", contacts=FEET_FLAT)

P["arm_up"] = dict(view=(0, 3), shoulder=(178, 4, 0), hand="flat", contacts=FEET_FLAT)

P["pranamasana"] = dict(view=(0, 4), shoulder=(8, 30, -72), elbow=128, forearm=0, wrist=(70, 0), hand="flat",
                        contacts=FEET_FLAT, pairs=[("palm_L", "palm_R")],
                        free=[("shoulder", 2, -90, -50), ("elbow", 0, 110, 140), ("shoulder", 1, 20, 40)])

P["hasta_uttanasana"] = dict(view=(0, 4), root=(0, -6, 0), hip=(-8, 0, 0), knee=3, lumbar=(-12, 0, 0), thoracic=(-9, 0, 0),
                             cervical=(-3, 0, 0), head=(-2, 0, 0), shoulder=(176, 4, 0), hand="flat", contacts=FEET_FLAT,
                             free=[("root", 1, -10, 0)])

P["padahastasana"] = dict(view=(0, 4), root=(0, 118, 0), hip=(118, 0, 0), lumbar=(22, 0, 0), thoracic=(18, 0, 0),
                          cervical=(14, 0, 0), shoulder=(130, 6, 0), elbow=8, wrist=(78, 0), forearm=85, hand="flat",
                          contacts=FEET_FLAT + PALMS,
                          free=PRON + [("root", 1, 100, 135), ("hip", 0, 100, 135), ("shoulder", 0, 90, 170), ("wrist", 0, 40, 95)], rel=FWD)

P["padahasta_beginner"] = dict(view=(0, 4), root=(0, 95, 0), hip=(125, 0, 0), knee=48, ankle=(22, 0), lumbar=(18, 0, 0),
                               thoracic=(14, 0, 0), cervical=(10, 0, 0), shoulder=(112, 6, 0), wrist=(80, 0), forearm=85, hand="flat",
                               contacts=FEET_FLAT + PALMS,
                               free=PRON + [("root", 1, 80, 115), ("hip", 0, 110, 140), ("shoulder", 0, 80, 150), ("ankle", 0, 10, 30)], rel=FWD)

P["ardha_uttanasana"] = dict(view=(0, 4), root=(0, 80, 0), hip=(80, 0, 0), knee=6, lumbar=(-6, 0, 0), thoracic=(-4, 0, 0),
                             cervical=(-18, 0, 0), shoulder=(70, 4, 0), hand="grip", contacts=FEET_FLAT,
                             pairs=[("palm_L", "shin_L", 1.2), ("palm_R", "shin_R", 1.2)],
                             free=[("shoulder", 0, 35, 110), ("shoulder", 1, -5, 20), ("root", 1, 70, 95), ("hip", 0, 70, 100), ("elbow", 0, 0, 30)])

P["utkatasana"] = dict(view=(0, 4), root=(0, 32, 0), hip=(88, 0, 0), knee=86, ankle=(32, 0), lumbar=(-4, 0, 0),
                       shoulder=(165, 4, 0), cervical=(-8, 0, 0), hand="flat", contacts=FEET_FLAT,
                       free=[("root", 1, 20, 45), ("hip", 0, 70, 100), ("ankle", 0, 20, 40)])

P["virabhadrasana1"] = dict(view=(20, 6), root=(0, -4, 0), hip_L=(92, 0, 0), knee_L=92, ankle_L=(4, 0),
                            hip_R=(-32, 0, 42), knee_R=0, ankle_R=(22, 8), lumbar=(-10, 0, 0), thoracic=(-8, 0, 0),
                            cervical=(-10, 0, 0), shoulder=(172, 5, 0), hand="flat",
                            contacts=[("heel_L", Z, 0), ("ball_L", Z, 0), ("heel_R", Z, 0), ("ball_R", Z, 0)],
                            free=[("hip_R", 0, -45, -15), ("ankle_R", 0, 10, 35), ("knee_L", 0, 75, 100), ("root", 1, -12, 5)])

P["virabhadrasana2"] = dict(view=(90, 4), root=(0, 0, 0), hip_L=(0, 58, 72), knee_L=88, ankle_L=(4, 0),
                            hip_R=(0, 38, -8), ankle_R=(2, 0), cervical=(0, 0, 78), shoulder=(0, 90, 0), forearm=85,
                            hand="flat",
                            contacts=[("heel_L", Z, 0), ("ball_L", Z, 0), ("heel_R", Z, 0), ("ball5_R", Z, 0)],
                            free=[("hip_L", 1, 40, 75), ("hip_R", 1, 25, 45), ("knee_L", 0, 70, 100), ("ankle_L", 1, -15, 15),
                                  ("ankle_R", 1, -20, 20)])

P["vrksasana"] = dict(view=(90, 4), hip_L=(40, 58, 62), knee_L=148, ankle_L=(-20, 10), shoulder=(172, -2, 0),
                      hand="flat", contacts=[("heel_R", Z, 0), ("ball_R", Z, 0)],
                      pairs=[("heel_L", "thighinner_R", 0.8)],
                      free=[("hip_L", 0, 25, 80), ("hip_L", 1, 30, 70), ("hip_L", 2, 30, 80), ("knee_L", 0, 110, 155)])

P["trikonasana"] = dict(view=(90, 4), root=(0, 0, -42), hip_L=(0, -14, -6), hip_R=(0, 74, 84), ankle_R=(0, -4),
                        ankle_L=(0, 10), lumbar=(0, -12, 0), thoracic=(0, -8, 12), cervical=(0, 0, 55), head=(-10, 0, 20),
                        shoulder_R=(0, 88, 0), shoulder_L=(0, 88, 0), forearm=80, hand="flat",
                        contacts=[("heel_L", Z, 0), ("ball_L", Z, 0), ("heel_R", Z, 0), ("ball_R", Z, 0)],
                        pairs=[("palm_R", "shin_R", 0.6)],
                        free=[("root", 2, -60, -25), ("hip_L", 1, -35, 10), ("hip_R", 1, 55, 100), ("shoulder_R", 1, 60, 110),
                              ("lumbar", 1, -30, 0), ("ankle_L", 1, -10, 25)])

P["trikonasana_block"] = copy.deepcopy(P["trikonasana"])
P["trikonasana_block"].update(root=(0, 0, -36), pairs=[], contacts=P["trikonasana"]["contacts"] + [("palm_R", Z, 0.23)],
                              free=[("root", 2, -50, -20), ("hip_L", 1, -35, 10), ("hip_R", 1, 50, 95), ("shoulder_R", 1, 60, 110)],
                              props=[dict(kind="block", at="palm_R", size=(0.23, 0.15, 0.075), stand="tall")])

P["trikonasana_floor"] = copy.deepcopy(P["trikonasana"])
P["trikonasana_floor"].update(root=(0, 0, -62), hip_R=(0, 92, 84), hip_L=(0, -30, -6), lumbar=(0, -18, 0), thoracic=(0, -12, 14),
                              pairs=[("palm_R", "ball5_R", 0.5)], contacts=P["trikonasana"]["contacts"] + [("palm_R", Z, 0)],
                              shoulder_R=(0, 92, 0),
                              free=[("root", 2, -85, -45), ("hip_L", 1, -50, 5), ("hip_R", 1, 70, 115), ("shoulder_R", 1, 75, 100),
                                    ("lumbar", 1, -35, 0)])

# ------------------------------------------------------------------ sun salutation
P["lunge"] = dict(view=(0, 4), root=(0, 30, 0), hip_L=(128, 0, 0), knee_L=112, ankle_L=(28, 0),
                  hip_R=(-18, 0, 0), knee_R=38, ankle_R=(-10, 0), toes_R=60,
                  lumbar=(-12, 0, 0), thoracic=(-10, 0, 0), cervical=(-22, 0, 0), shoulder=(62, 4, 0), wrist=(80, 0),
                  forearm=85, hand="flat", contacts=[("heel_L", Z, 0), ("ball_L", Z, 0), ("knee_R", Z, 0), ("toepad_R", Z, 0)] + PALMS,
                  free=PRON + [("root", 1, 10, 45), ("hip_R", 0, -40, 5), ("knee_R", 0, 20, 70), ("shoulder", 0, 30, 90), ("ankle_R", 0, -40, 30),
                        ("hip_L", 0, 110, 140)], rel=FWD)

P["plank"] = dict(view=(0, 4), root=(0, 76, 0), hip=(0, 0, 0), ankle=(-4, 0), toes=80, shoulder=(84, 4, 0), wrist=(88, 0),
                  forearm=85, hand="flat", cervical=(-4, 0, 0), contacts=PALMS + TOES_TUCKED,
                  free=PRON + [("root", 1, 60, 85), ("shoulder", 0, 70, 100), ("ankle", 0, -30, 20)], rel=FWD)

P["ashtanga_namaskara"] = dict(view=(0, 4), root=(0, 112, 0), hip=(62, 0, 0), knee=62, ankle=(-4, 0), toes=80,
                               lumbar=(-18, 0, 0), thoracic=(-12, 0, 0), cervical=(-20, 0, 0),
                               shoulder=(-10, 16, 0), elbow=120, wrist=(88, 0), forearm=85, hand="flat",
                               contacts=[("chin", Z, 0), ("chest", Z, 0), ("knee_L", Z, 0), ("knee_R", Z, 0)] + PALMS + TOES_TUCKED,
                               free=PRON + [("root", 1, 95, 130), ("hip", 0, 40, 90), ("knee", 0, 40, 90), ("shoulder", 0, -40, 20),
                                     ("elbow", 0, 90, 150), ("lumbar", 0, -35, 0)], rel=FWD)

P["bhujangasana"] = dict(view=(0, 4), root=(0, 90, 0), hip=(-4, 0, 0), ankle=(-58, 0), lumbar=(-34, 0, 0),
                         thoracic=(-28, 0, 0), cervical=(-16, 0, 0), head=(-6, 0, 0),
                         shoulder=(-30, 8, 0), elbow=100, wrist=(85, 0), forearm=85, hand="flat",
                         contacts=[("pubis", Z, 0), ("thigh_L", Z, 0), ("thigh_R", Z, 0), ("dorsum_L", Z, 0), ("dorsum_R", Z, 0)] + PALMS,
                         free=PRON + [("lumbar", 0, -48, -15), ("thoracic", 0, -45, -10), ("shoulder", 0, -60, 20), ("elbow", 0, 55, 115),
                               ("root", 1, 80, 100), ("wrist", 0, 50, 100), ("ankle", 0, -80, -45)], rel=FWD)

P["adho_mukha"] = dict(view=(0, 4), root=(0, 134, 0), hip=(108, 0, 0), ankle=(22, 0), shoulder=(176, 6, 0), wrist=(55, 0),
                       forearm=85, hand="spread", cervical=(0, 0, 0), contacts=PALMS + [("heel_L", Z, 0.05, 0.4), ("heel_R", Z, 0.05, 0.4), ("ball_L", Z, 0), ("ball_R", Z, 0)],
                       free=[("forearm", 0, 50, 110), ("root", 1, 124, 145), ("hip", 0, 95, 120), ("shoulder", 0, 168, 182), ("ankle", 0, 5, 35), ("wrist", 0, 35, 80)], rel=FWD)

# ------------------------------------------------------------------ supine
P["savasana"] = dict(view=(0, 22), root=(0, -90, 0), hip=(0, 8, 38), ankle=(-22, 0), shoulder=(0, 22, 0), forearm=-80,
                     hand="relaxed", head=(4, 0, 0))

P["leg_raise"] = dict(view=(0, 6), root=(0, -90, 0), hip_L=(0, 0, 0), hip_R=(90, 0, 0), ankle=(10, 0), shoulder=(0, 6, 0),
                      forearm=60, hand="flat")

P["double_leg_raise"] = dict(view=(0, 6), root=(0, -90, 0), hip=(90, 0, 0), ankle=(10, 0), shoulder=(0, 6, 0), forearm=60, hand="flat")

P["bridge"] = dict(view=(0, 6), root=(0, -90, 0), hip=(18, 4, 0), knee=100, ankle=(12, 0), lumbar=(-12, 0, 0), thoracic=(-6, 0, 0),
                   cervical=(30, 0, 0), shoulder=(-8, 6, 0), forearm=70, hand="flat",
                   contacts=[("heel_L", Z, 0), ("ball_L", Z, 0), ("heel_R", Z, 0), ("ball_R", Z, 0), ("occiput", Z, 0),
                             ("shoulderback_L", Z, 0), ("shoulderback_R", Z, 0), ("backhand_L", Z, 0, 0.5), ("backhand_R", Z, 0, 0.5)],
                   free=[("root", 1, -135, -95), ("hip", 0, -10, 40), ("knee", 0, 80, 130), ("cervical", 0, 10, 60), ("ankle", 0, -10, 35),
                         ("shoulder", 0, -45, 25)])

P["supta_padangusthasana"] = dict(view=(0, 6), root=(0, -90, 0), hip_L=(0, 0, 0), hip_R=(82, 0, 0), ankle=(14, 0),
                                  shoulder_L=(0, 10, 0), forearm_L=60, shoulder_R=(100, 4, 0), elbow_R=6, hand_R="grip", hand_L="flat",
                                  props=[dict(kind="strap", frm=["palm_R"], around=["ball_R"])])

P["legs_up_wall"] = dict(view=(0, 6), root=(0, -90, 0), hip=(88, 0, 0), ankle=(0, 0), shoulder=(0, 25, 0), forearm=-80, hand="relaxed",
                         props=[dict(kind="wall", at="heel_L", side="y+", offset=0.0)])

# ------------------------------------------------------------------ inversions
HEADSTAND_BASE = dict(contacts=[("crown", Z, 0), ("ulnar_L", Z, 0), ("ulnar_R", Z, 0), ("elbow_L", Z, 0), ("elbow_R", Z, 0)],
                      pairs=[("fingertip_L", "knuckles_R", 0.4), ("fingertip_R", "knuckles_L", 0.4)],
                      hand="grip", shoulder=(160, -8, -40), elbow=98, forearm=18)
HS_FREE = [("shoulder", 0, 130, 185), ("shoulder", 1, -15, 30), ("shoulder", 2, -80, 10), ("elbow", 0, 60, 150),
           ("cervical", 0, -15, 20), ("forearm", 0, -40, 50)]

P["sirsasana"] = dict(HEADSTAND_BASE, view=(0, 4), root=(0, 178, 0), ankle=(-10, 0), free=HS_FREE + [("root", 1, 165, 195)])

P["sirsasana_prep"] = dict(HEADSTAND_BASE, view=(0, 4), root=(0, 145, 0), hip=(125, 0, 0), ankle=(20, 0), toes=40,
                           contacts=HEADSTAND_BASE["contacts"] + [("toepad_L", Z, 0), ("toepad_R", Z, 0)],
                           free=HS_FREE + [("root", 1, 120, 175), ("hip", 0, 90, 150)])

P["sirsasana_tuck"] = dict(HEADSTAND_BASE, view=(0, 4), root=(0, 172, 0), hip=(125, 0, 0), knee=145, ankle=(-20, 0),
                           free=HS_FREE + [("root", 1, 155, 190)])

P["dolphin"] = dict(view=(0, 4), root=(0, 138, 0), hip=(92, 0, 0), ankle=(22, 0), shoulder=(150, 6, -30), elbow=90, forearm=20,
                    hand="grip", cervical=(10, 0, 0),
                    contacts=[("ulnar_L", Z, 0), ("ulnar_R", Z, 0), ("elbow_L", Z, 0), ("elbow_R", Z, 0), ("ball_L", Z, 0), ("ball_R", Z, 0)],
                    pairs=[("fingertip_L", "knuckles_R", 0.3), ("fingertip_R", "knuckles_L", 0.3)],
                    free=[("root", 1, 115, 160), ("hip", 0, 70, 110), ("shoulder", 0, 120, 180), ("elbow", 0, 60, 130),
                          ("shoulder", 2, -70, 10), ("ankle", 0, 5, 40)])

BLANKET_SH = dict(kind="blanket", at="shoulderback_L", size=(0.62, 0.44, 0.06), under="shoulders")
SHOULDERS_ON = [("shoulderback_L", Z, 0.06), ("shoulderback_R", Z, 0.06), ("occiput", Z, 0.0),
                ("elbow_L", Z, 0.06), ("elbow_R", Z, 0.06)]

BACK_HANDS = [("palm_L", "back_L", 1.0), ("palm_R", "back_R", 1.0), ("fingertip_L", "lowback_L", 0.4), ("fingertip_R", "lowback_R", 0.4)]
ARMS_BACK_FREE = [("shoulder", 0, -110, -60), ("shoulder", 1, -20, 30), ("elbow", 0, 100, 160), ("forearm", 0, -100, 100), ("wrist", 0, 0, 90)]

P["sarvangasana"] = dict(view=(0, 5), root=(0, 180, 0), lumbar=(4, 0, 0), thoracic=(12, 0, 0), cervical=(74, 0, 0), head=(8, 0, 0),
                         shoulder=(-88, 14, 0), elbow=135, forearm=-60, wrist=(40, 0), hand="flat", ankle=(-10, 0),
                         contacts=SHOULDERS_ON, pairs=BACK_HANDS,
                         free=ARMS_BACK_FREE + [("root", 1, 176, 186), ("cervical", 0, 55, 100), ("thoracic", 0, 0, 30), ("head", 0, 0, 30)],
                         props=[BLANKET_SH])

P["viparita_karani"] = dict(view=(0, 5), root=(0, -135, 0), hip=(44, 0, 0), lumbar=(0, 0, 0), thoracic=(8, 0, 0), cervical=(50, 0, 0),
                            shoulder=(-40, 14, 0), elbow=95, forearm=70, wrist=(60, 0), hand="flat",
                            contacts=SHOULDERS_ON, pairs=[("palm_L", "buttock_L", 1.0), ("palm_R", "buttock_R", 1.0)],
                            free=[("root", 1, -150, -120), ("cervical", 0, 30, 75), ("shoulder", 0, -80, -10), ("elbow", 0, 60, 140),
                                  ("hip", 0, 35, 55), ("forearm", 0, 20, 100)],
                            props=[BLANKET_SH])

P["halasana"] = dict(view=(0, 5), root=(0, 150, 0), hip=(115, 0, 0), lumbar=(20, 0, 0), thoracic=(22, 0, 0), cervical=(70, 0, 0),
                     ankle=(15, 0), toes=60, shoulder=(-88, 8, 0), forearm=85, hand="flat",
                     contacts=SHOULDERS_ON + [("toepad_L", Z, 0), ("toepad_R", Z, 0), ("palm_L", Z, 0.0), ("palm_R", Z, 0.0)],
                     free=[("root", 1, 120, 200), ("hip", 0, 90, 160), ("cervical", 0, 50, 95), ("shoulder", 0, -130, -40), ("lumbar", 0, 0, 40)],
                     props=[BLANKET_SH])

P["halasana_chair"] = dict(view=(0, 5), root=(0, 160, 0), hip=(92, 0, 0), lumbar=(12, 0, 0), thoracic=(16, 0, 0), cervical=(66, 0, 0),
                           ankle=(0, 0), shoulder=(-88, 12, 0), elbow=135, forearm=-60, wrist=(40, 0), hand="flat",
                           contacts=SHOULDERS_ON + [("ankle_L", Z, 0.48), ("ankle_R", Z, 0.48)],
                           pairs=BACK_HANDS,
                           free=ARMS_BACK_FREE + [("root", 1, 140, 190), ("hip", 0, 70, 120), ("cervical", 0, 50, 85)],
                           props=[BLANKET_SH, dict(kind="chair", at="ankle_L", seat=0.46, facing="body")])

P["matsyasana"] = dict(view=(0, 6), root=(0, -62, 0), hip=(-6, 0, 0), ankle=(-30, 0), lumbar=(-14, 0, 0), thoracic=(-26, 0, 0),
                       cervical=(-50, 0, 0), head=(-22, 0, 0), shoulder=(-86, 6, 0), elbow=88, forearm=88, wrist=(0, 0), hand="flat",
                       contacts=[("crown", Z, 0), ("buttock_L", Z, 0, 3), ("buttock_R", Z, 0, 3), ("heel_L", Z, 0), ("heel_R", Z, 0),
                                 ("elbow_L", Z, 0.0), ("elbow_R", Z, 0.0), ("palm_L", Z, 0.0, 0.3), ("palm_R", Z, 0.0, 0.3)],
                       free=[("root", 1, -85, -40), ("shoulder", 0, -110, -45), ("shoulder", 1, -10, 40), ("elbow", 0, 50, 120),
                             ("cervical", 0, -75, -25), ("thoracic", 0, -45, -5), ("lumbar", 0, -30, 5), ("head", 0, -40, -5), ("hip", 0, -25, 10)])

P["matsyasana_supported"] = dict(view=(0, 8), root=(0, -100, 0), ankle=(-25, 0), hip=(0, 6, 20), lumbar=(-8, 0, 0), thoracic=(-14, 0, 0),
                                 cervical=(-6, 0, 0), shoulder=(0, 50, 30), elbow=20, forearm=-80, hand="relaxed",
                                 contacts=[("buttock_L", Z, 0), ("buttock_R", Z, 0), ("heel_L", Z, 0), ("heel_R", Z, 0),
                                           ("upperback", Z, 0.20), ("occiput", Z, 0.20)],
                                 free=[("root", 1, -125, -90), ("lumbar", 0, -25, 5), ("thoracic", 0, -30, 5), ("cervical", 0, -30, 20),
                                       ("hip", 0, -15, 10)],
                                 props=[dict(kind="bolster", frm="midback", to="occiput")])

P["uttana_padasana"] = dict(view=(0, 6), root=(0, -66, 0), hip=(45, 0, 0), ankle=(-20, 0), lumbar=(-10, 0, 0), thoracic=(-22, 0, 0),
                            cervical=(-55, 0, 0), head=(-25, 0, 0), shoulder=(40, 0, 0), forearm=0, hand="flat",
                            contacts=[("crown", Z, 0), ("buttock_L", Z, 0), ("buttock_R", Z, 0)],
                            pairs=[("palm_L", "palm_R", 0.5)],
                            free=[("root", 1, -88, -40), ("thoracic", 0, -40, -10), ("cervical", 0, -70, -25), ("head", 0, -35, -5), ("hip", 0, 20, 60),
                                  ("shoulder", 0, 20, 60), ("shoulder", 1, -20, 10)])

# ------------------------------------------------------------------ seated
SIT = [("sit_L", Z, 0), ("sit_R", Z, 0)]

P["dandasana"] = dict(view=(0, 4), root=(0, 0, 0), hip=(92, 0, 0), ankle=(12, 0), shoulder=(4, 6, 0), wrist=(80, 0), forearm=85, hand="flat",
                      contacts=SIT + [("heel_L", Z, 0), ("heel_R", Z, 0)] + PALMS, free=PRON + [("root", 1, -10, 10), ("shoulder", 0, -25, 25), ("hip", 0, 80, 100), ("wrist", 0, 60, 100), ("shoulder", 1, 0, 20)], rel=FWD)

P["paschimottanasana"] = dict(view=(0, 4), root=(0, 55, 0), hip=(145, 0, 0), ankle=(8, 0), lumbar=(24, 0, 0), thoracic=(26, 0, 0),
                              cervical=(14, 0, 0), shoulder=(140, 8, 0), elbow=40, hand="grip",
                              contacts=SIT + [("heel_L", Z, 0), ("heel_R", Z, 0)],
                              pairs=[("palm_L", "toe_L", 1.2), ("palm_R", "toe_R", 1.2)],
                              free=[("root", 1, 35, 75), ("hip", 0, 120, 165), ("shoulder", 0, 100, 180), ("shoulder", 1, 0, 35),
                                    ("elbow", 0, 0, 120), ("lumbar", 0, 10, 35), ("thoracic", 0, 10, 38)])

P["paschimottanasana_strap"] = dict(view=(0, 4), root=(0, 12, 0), hip=(98, 0, 0), knee=14, ankle=(12, 0), lumbar=(4, 0, 0),
                                    thoracic=(6, 0, 0), shoulder=(62, 8, 0), elbow=18, hand="grip",
                                    contacts=SIT + [("heel_L", Z, 0), ("heel_R", Z, 0)],
                                    free=[("root", 1, 0, 25), ("hip", 0, 90, 115)],
                                    props=[dict(kind="strap", frm=["palm_L", "palm_R"], around=["ball_L", "ball_R"])])

P["paschimottanasana_deep"] = dict(view=(0, 4), root=(0, 70, 0), hip=(158, 0, 0), ankle=(8, 0), lumbar=(18, 0, 0), thoracic=(16, 0, 0),
                                   cervical=(6, 0, 0), shoulder=(168, 4, 0), elbow=20, hand="grip",
                                   contacts=SIT + [("heel_L", Z, 0), ("heel_R", Z, 0)],
                                   pairs=[("palm_L", "toe_L", 1.2), ("palm_R", "toe_R", 1.2), ("chest", "thigh_L", 0.3)],
                                   free=[("root", 1, 50, 85), ("hip", 0, 140, 175), ("shoulder", 0, 130, 185), ("elbow", 0, 0, 60),
                                         ("lumbar", 0, 5, 35), ("thoracic", 0, 5, 35)])

P["navasana"] = dict(view=(0, 4), root=(0, -42, 0), hip=(95, 0, 0), ankle=(-10, 0), lumbar=(6, 0, 0), thoracic=(-4, 0, 0),
                     cervical=(8, 0, 0), shoulder=(52, 4, 0), hand="flat", forearm=10,
                     contacts=SIT, free=[("root", 1, -60, -25)])

P["baddha_konasana"] = dict(view=(90, 5), root=(0, 6, 0), hip=(62, 42, 48), knee=146, ankle=(-12, 38), shoulder=(22, 8, 0),
                            elbow=30, forearm=30, hand="grip", contacts=SIT + [("ball5_L", Z, 0.01, 0.5), ("ball5_R", Z, 0.01, 0.5)],
                            pairs=[("ball_L", "ball_R", 0.8), ("palm_L", "toe_L", 0.5), ("palm_R", "toe_R", 0.5)],
                            free=[("hip", 0, 45, 85), ("hip", 1, 25, 60), ("hip", 2, 20, 70), ("knee", 0, 125, 155), ("ankle", 1, 15, 50),
                                  ("shoulder", 0, 0, 50), ("elbow", 0, 0, 80), ("root", 1, -5, 15)])

SUKHA = dict(root=(0, 4, 0), hip_L=(86, 48, 58), hip_R=(84, 46, 60), knee=132, ankle=(-12, -20),
             contacts=SIT + [("ankle_L", Z, 0.04, 0.5), ("ankle_R", Z, 0.04, 0.5)],
             pairs=[("achilles_L", "shin_R", 0.35), ("achilles_R", "shin_L", 0.35)],
             free=[("root", 1, -6, 14), ("hip_L", 1, 30, 65), ("hip_L", 2, 30, 80), ("knee_L", 0, 110, 150),
                   ("hip_R", 1, 30, 65), ("hip_R", 2, 30, 80), ("knee_R", 0, 110, 150), ("hip_L", 0, 70, 100), ("hip_R", 0, 70, 100)])

P["sukhasana_side"] = dict(SUKHA, view=(0, 4), shoulder=(10, 8, 0), elbow=40, forearm=-70, wrist=(10, 0), hand="mudra")

P["meditation_front"] = dict(SUKHA, view=(90, 3), shoulder=(10, 12, 0), elbow=46, forearm=-75, wrist=(10, 0), hand="mudra")

P["easy_twist"] = dict(SUKHA, view=(60, 6), thoracic=(0, 0, 28), lumbar=(0, 0, 10), cervical=(0, 0, 30),
                       shoulder_R=(40, 10, 0), elbow_R=35, forearm_R=40, hand_R="grip",
                       shoulder_L=(-40, 18, 0), wrist_L=(80, 0), hand_L="flat", forearm_L=85,
                       pairs=SUKHA["pairs"] + [("palm_R", "knee_L", 0.8)],
                       contacts=SUKHA["contacts"] + [("palm_L", Z, 0)],
                       free=SUKHA["free"] + [("shoulder_R", 0, 10, 70), ("shoulder_R", 1, -30, 25), ("shoulder_L", 0, -70, -10), ("elbow_R", 0, 0, 80)])

P["ardha_matsyendrasana"] = dict(view=(50, 8), root=(0, 4, 0),
                                 hip_R=(80, 20, 70), knee_R=150, ankle_R=(-30, 0),
                                 hip_L=(112, -18, 10), knee_L=125, ankle_L=(8, 0),
                                 lumbar=(0, 0, 12), thoracic=(0, 0, 32), cervical=(0, 0, 40),
                                 shoulder_R=(60, -10, 40), elbow_R=8, hand_R="grip",
                                 shoulder_L=(-45, 20, 0), wrist_L=(80, 0), forearm_L=85, hand_L="flat",
                                 contacts=SIT + [("heel_L", Z, 0), ("ball_L", Z, 0), ("palm_L", Z, 0), ("kneeside_R", Z, 0.0, 0.6),
                                                 ("ankle_R", Z, 0.02, 0.5)],
                                 pairs=[("palm_R", "ankle_L", 0.6), ("triceps_R", "kneeside_L", 0.4), ("heel_R", "hipside_L", 0.4)],
                                 free=[("hip_L", 0, 90, 130), ("hip_L", 1, -40, 0), ("knee_L", 0, 100, 150), ("shoulder_R", 0, 30, 100),
                                       ("shoulder_R", 1, -40, 20), ("shoulder_L", 0, -80, -20), ("root", 1, -8, 15), ("root", 2, -10, 10),
                                       ("hip_R", 0, 60, 100), ("hip_R", 1, 5, 45), ("hip_R", 2, 40, 90), ("knee_R", 0, 130, 160)], starts=8)

P["malasana"] = dict(view=(0, 4), root=(0, 30, 0), hip=(118, 30, 25), knee=145, ankle=(34, 0), lumbar=(-6, 0, 0),
                     shoulder=(30, 30, -60), elbow=115, wrist=(65, 0), hand="flat", forearm=0, contacts=FEET_FLAT,
                     pairs=[("palm_L", "palm_R", 0.8)],
                     free=[("root", 1, 15, 50), ("hip", 0, 100, 135), ("ankle", 0, 20, 45), ("shoulder", 1, 10, 50), ("shoulder", 2, -90, -30),
                           ("elbow", 0, 90, 140), ("shoulder", 0, 0, 60)])

# ------------------------------------------------------------------ kneeling
KNEEL = [("knee_L", Z, 0), ("knee_R", Z, 0), ("dorsum_L", Z, 0.01, 0.5), ("dorsum_R", Z, 0.01, 0.5), ("shin_L", Z, 0.01, 0.5), ("shin_R", Z, 0.01, 0.5)]

P["vajrasana"] = dict(view=(0, 4), root=(0, 0, 0), hip=(88, 0, 0), knee=160, ankle=(-56, 0), shoulder=(8, 8, 0), elbow=55, hand="flat",
                      forearm=80, wrist=(0, 0), contacts=KNEEL + [("buttock_L", Z, 0.12, 0.2)],
                      pairs=[("palm_L", "thigh_L", 0.8), ("palm_R", "thigh_R", 0.8)],
                      free=[("root", 1, -10, 10), ("hip", 0, 75, 100), ("knee", 0, 145, 168), ("shoulder", 0, -10, 40), ("elbow", 0, 20, 90),
                            ("ankle", 0, -95, -40)])

P["balasana"] = dict(view=(0, 4), root=(0, 115, 0), hip=(152, 6, 0), knee=152, ankle=(-56, 0), lumbar=(22, 0, 0), thoracic=(18, 0, 0),
                     cervical=(10, 0, 0), shoulder=(-6, 10, -75), elbow=6, forearm=-40, hand="relaxed",
                     contacts=KNEEL + [("forehead", Z, 0), ("backhand_L", Z, 0.0, 0.3), ("backhand_R", Z, 0.0, 0.3)],
                     free=[("root", 1, 95, 135), ("hip", 0, 135, 165), ("lumbar", 0, 5, 35), ("thoracic", 0, 5, 30), ("shoulder", 0, -30, 20)])

TABLE = dict(root=(0, 90, 0), hip=(90, 0, 0), knee=90, ankle=(-56, 0), shoulder=(90, 4, 0), wrist=(88, 0), forearm=85, hand="flat",
             contacts=[("knee_L", Z, 0), ("knee_R", Z, 0), ("shin_L", Z, 0.01, 0.5), ("shin_R", Z, 0.01, 0.5)] + PALMS, rel=FWD,
             free=PRON + [("root", 1, 70, 105), ("hip", 0, 70, 110), ("shoulder", 0, 70, 110), ("wrist", 0, 70, 100), ("ankle", 0, -95, -35)])
P["tabletop"] = dict(TABLE, view=(0, 4))
P["cat"] = dict(TABLE, view=(0, 4), lumbar=(20, 0, 0), thoracic=(26, 0, 0), cervical=(26, 0, 0), root=(0, 84, 0))
P["cow"] = dict(TABLE, view=(0, 4), lumbar=(-20, 0, 0), thoracic=(-14, 0, 0), cervical=(-26, 0, 0), root=(0, 98, 0))

P["ustrasana"] = dict(view=(0, 4), root=(0, -20, 0), hip=(-22, 0, 0), knee=90, ankle=(-70, 0), toes=0, lumbar=(-34, 0, 0), thoracic=(-30, 0, 0),
                      cervical=(-36, 0, 0), head=(-10, 0, 0), shoulder=(-60, 14, 0), forearm=0, hand="flat", contacts=KNEEL,
                      pairs=[("palm_L", "heel_L", 0.8), ("palm_R", "heel_R", 0.8)],
                      rel=[("hipside_L", "knee_L", "y", 0.04, 0.6), ("hipside_R", "knee_R", "y", 0.04, 0.6)],
                      free=[("root", 1, -50, 10), ("hip", 0, -50, 10), ("lumbar", 0, -55, -15), ("thoracic", 0, -45, -10),
                            ("shoulder", 0, -120, -30), ("shoulder", 1, 0, 35), ("knee", 0, 80, 100), ("ankle", 0, -95, -45)], starts=6)

# ------------------------------------------------------------------ prone
PRONE = [("pubis", Z, 0), ("thigh_L", Z, 0), ("thigh_R", Z, 0)]

P["sphinx"] = dict(view=(0, 4), root=(0, 90, 0), ankle=(-56, 0), lumbar=(-16, 0, 0), thoracic=(-12, 0, 0), cervical=(-6, 0, 0),
                   shoulder=(80, 6, 0), elbow=90, forearm=85, hand="flat",
                   contacts=PRONE + [("dorsum_L", Z, 0), ("dorsum_R", Z, 0), ("forearm_L", Z, 0), ("forearm_R", Z, 0), ("elbow_L", Z, 0.01)],
                   free=[("lumbar", 0, -30, 0), ("thoracic", 0, -25, 0), ("shoulder", 0, 55, 110), ("elbow", 0, 70, 110), ("root", 1, 80, 95),
                         ("ankle", 0, -95, -45)])

P["salabhasana"] = dict(view=(0, 4), root=(0, 98, 0), hip=(-24, 0, 0), ankle=(-35, 0), lumbar=(-18, 0, 0), thoracic=(-4, 0, 0),
                        cervical=(-10, 0, 0), shoulder=(8, -6, 0), forearm=85, hand="fist",
                        contacts=[("chin", Z, 0), ("chest", Z, 0)],
                        free=[("root", 1, 92, 102), ("hip", 0, -32, -15)])

P["ardha_salabhasana"] = dict(view=(0, 4), root=(0, 92, 0), hip_L=(0, 0, 0), hip_R=(-30, 0, 0), ankle=(-55, 0), lumbar=(-8, 0, 0),
                              cervical=(-10, 0, 0), shoulder=(2, 8, 0), forearm=85, hand="flat",
                              contacts=[("chin", Z, 0), ("chest", Z, 0), ("thigh_L", Z, 0), ("dorsum_L", Z, 0)],
                              free=[("root", 1, 85, 100), ("hip_R", 0, -45, -15)])

P["dhanurasana"] = dict(view=(0, 4), root=(0, 90, 0), hip=(-30, 10, 0), knee=112, ankle=(-30, 0), lumbar=(-26, 0, 0), thoracic=(-22, 0, 0),
                        cervical=(-22, 0, 0), shoulder=(-55, 12, 10), forearm=60, hand="grip",
                        contacts=[("belly", Z, 0)],
                        pairs=[("palm_L", "ankle_L", 0.8), ("palm_R", "ankle_R", 0.8)],
                        free=[("hip", 0, -50, -10), ("knee", 0, 80, 140), ("shoulder", 0, -80, -20), ("shoulder", 1, 0, 30),
                              ("lumbar", 0, -40, -10), ("thoracic", 0, -35, -5), ("root", 1, 70, 100)])

P["ardha_dhanurasana"] = dict(view=(20, 8), root=(0, 90, 0), hip_L=(0, 0, 0), hip_R=(-18, 6, 0), knee_R=115, ankle=(-35, 0),
                              lumbar=(-16, 0, 0), thoracic=(-14, 0, 0), cervical=(-12, 0, 0),
                              shoulder_L=(70, 8, 0), elbow_L=90, forearm_L=85, hand_L="flat",
                              shoulder_R=(-50, 12, 10), forearm_R=60, hand_R="grip",
                              contacts=PRONE + [("forearm_L", Z, 0), ("elbow_L", Z, 0.01), ("dorsum_L", Z, 0)],
                              pairs=[("palm_R", "ankle_R", 0.8)],
                              free=[("hip_R", 0, -40, 0), ("knee_R", 0, 90, 140), ("shoulder_R", 0, -80, -20), ("lumbar", 0, -30, 0),
                                    ("shoulder_L", 0, 50, 100), ("root", 1, 80, 95)])

# ------------------------------------------------------------------ arm balances
P["kakasana"] = dict(view=(0, 4), root=(0, 62, 0), hip=(128, 24, 12), knee=128, ankle=(-38, 0), toes=0, lumbar=(24, 0, 0), thoracic=(16, 0, 0),
                     cervical=(-24, 0, 0), shoulder=(52, 14, 0), elbow=62, wrist=(90, 0), forearm=85, hand="spread",
                     contacts=PALMS, pairs=[("kneeinner_L", "triceps_L", 0.8), ("kneeinner_R", "triceps_R", 0.8)],
                     free=PRON + [("root", 1, 45, 85), ("hip", 0, 110, 145), ("shoulder", 0, 25, 80), ("elbow", 0, 30, 90), ("wrist", 0, 60, 95),
                           ("hip", 1, 5, 35)], rel=FWD)

P["bakasana"] = dict(view=(0, 4), root=(0, 78, 0), hip=(140, 20, 12), knee=140, ankle=(-38, 0), lumbar=(28, 0, 0), thoracic=(20, 0, 0),
                     cervical=(-18, 0, 0), shoulder=(40, 12, 0), elbow=4, wrist=(90, 0), forearm=85, hand="spread",
                     contacts=PALMS, pairs=[("knee_L", "triceps_L", 0.8), ("knee_R", "triceps_R", 0.8)],
                     free=PRON + [("root", 1, 60, 95), ("hip", 0, 120, 160), ("shoulder", 0, 15, 70), ("wrist", 0, 60, 95), ("hip", 1, 5, 35)], rel=FWD)

P["mayurasana"] = dict(view=(0, 4), root=(0, 90, 0), hip=(0, 0, 0), ankle=(-45, 0), lumbar=(-4, 0, 0), cervical=(-12, 0, 0),
                       shoulder=(40, 14, 0), elbow=55, forearm=-60, wrist=(88, 0), hand="spread",
                       contacts=PALMS, pairs=[("elbow_L", "belly", 0.4), ("elbow_R", "belly", 0.4)],
                       rel=[("fingertip_L", "wristpalm_L", "y", 0.14, 0.5), ("fingertip_R", "wristpalm_R", "y", 0.14, 0.5),
                            ("crown", "heel_L", "z", 0.0, 0.6)],
                       free=[("root", 1, 75, 105), ("shoulder", 0, 10, 70), ("shoulder", 1, 0, 30), ("elbow", 0, 30, 100),
                             ("forearm", 0, -120, 120), ("wrist", 0, 60, 100)], starts=6)

# ------------------------------------------------------------------ backbends from the floor
P["urdhva_dhanurasana"] = dict(view=(0, 4), root=(0, -100, 0), hip=(-15, 8, 0), knee=80, ankle=(15, 0), lumbar=(-40, 0, 0),
                               thoracic=(-30, 0, 0), cervical=(-20, 0, 0), shoulder=(165, 10, 0), elbow=4, forearm=85, wrist=(80, 0), hand="spread",
                               contacts=FEET_FLAT + PALMS,
                               rel=[("fingertip_L", "wristpalm_L", "y", -0.15, 0.4), ("fingertip_R", "wristpalm_R", "y", -0.15, 0.4)],
                               free=[("root", 1, -135, -60), ("hip", 0, -35, 15), ("knee", 0, 50, 120), ("shoulder", 0, 140, 190),
                                     ("lumbar", 0, -55, -20), ("thoracic", 0, -45, -15), ("wrist", 0, 60, 100), ("ankle", 0, -10, 35),
                                     ("forearm", 0, -120, 120)], starts=6)
