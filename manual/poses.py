"""Pose library for the manual's illustrations (see posefig.py for the angle conventions).

All figures face right unless flip=True.  Where a posture must rest on the floor at several
points (hands, feet, head, knees), `settle` nudges the listed angles so those points share one
floor line.
"""
from posefig import settle

LEGFIRST = ["farLeg", "nearLeg", "farArm", "torso", "head", "nearArm"]
ARMFIRST = ["farArm", "nearArm", "farLeg", "torso", "head", "nearLeg"]
BACKARM = ["farArm", "farLeg", "nearArm", "torso", "head", "nearLeg"]

P = {}

# ---------------------------------------------------------------- standing
P["tadasana"] = dict(face=0, ua2=92, fa2=92, th2=91, sh2=91)
P["pranamasana"] = dict(face=0, ua1=72, fa1=-72, h1=-84, ua2=70, fa2=-70, h2=-84, th2=91, sh2=91)
P["hasta_uttanasana"] = dict(lt=-96, ut=-112, nk=-122, hd=-128, face=-40, ua1=-116, fa1=-120, h1=-122,
                             ua2=-113, fa2=-117, h2=-119, th1=86, sh1=90, th2=87, sh2=91)
P["padahastasana"] = dict(lt=52, ut=86, nk=100, hd=106, face=175, ua1=70, fa1=160, h1=150, ua2=72, fa2=158, h2=150,
                         th1=88, sh1=90, th2=90, sh2=90, order=["farArm", "farLeg", "nearLeg", "torso", "head", "nearArm"])
P["padahasta_beginner"] = settle(dict(lt=20, ut=45, nk=65, hd=75, face=160, ua1=100, fa1=95, h1=4, ua2=98, fa2=93, h2=4,
                                      th1=70, sh1=110, th2=72, sh2=108, order=LEGFIRST), ["heel1", "toe1", "fi1"],
                                 ["ua1", "fa1", "ua2", "fa2", "th1", "sh1", "th2", "sh2"])
P["ardha_uttanasana"] = dict(lt=2, ut=0, nk=5, hd=5, face=70, ua1=100, fa1=120, h1=120, ua2=98, fa2=118, h2=118,
                             th1=90, sh1=90, th2=91, sh2=91)
P["utkatasana"] = settle(dict(lt=-58, ut=-64, nk=-66, hd=-68, face=0, ua1=-66, fa1=-66, h1=-66, ua2=-63, fa2=-63, h2=-63,
                              th1=35, sh1=112, ft1=0, th2=37, sh2=110, ft2=0), ["heel1", "toe1"], ["sh1", "sh2"])
P["virabhadrasana1"] = settle(dict(lt=-88, ut=-92, nk=-94, hd=-96, face=-10, ua1=-94, fa1=-94, h1=-94, ua2=-91, fa2=-91, h2=-91,
                                   th1=18, sh1=92, ft1=0, th2=128, sh2=128, ft2=-8), ["heel1", "toe1", "heel2", "toe2"],
                              ["th1", "sh1", "th2", "sh2", "ft2"])
P["virabhadrasana2"] = settle(dict(view="front", face=None, ua1=180, fa1=180, h1=180, ua2=0, fa2=0, h2=0,
                                   th1=170, sh1=92, ft1=180, th2=48, sh2=48, ft2=0), ["heel1", "toe1", "heel2", "toe2"],
                              ["th1", "sh1", "th2", "sh2"])
P["vrksasana"] = dict(view="front", face=None, ua1=-100, fa1=-78, h1=-90, ua2=-80, fa2=-102, h2=-90,
                      th1=150, sh1=10, ft1=90, th2=90, sh2=90, ft2=0)
P["trikonasana"] = settle(dict(view="front", lt=-30, ut=-6, nk=-6, hd=-12, face=None, ua1=-90, fa1=-90, h1=-90,
                               ua2=90, fa2=90, h2=90, th1=116, sh1=116, ft1=180, th2=64, sh2=64, ft2=0),
                          ["heel1", "toe1", "heel2", "toe2"], ["th1", "sh1", "th2", "sh2", "lt", "ut", "ua2", "fa2"],
                          pins=[("wr2", ("an2", "kn2"), 0.35)])
P["trikonasana_block"] = dict(P["trikonasana"], lt=-45, ut=-28, nk=-28, hd=-32, ua1=-90, fa1=-90, ua2=92, fa2=92)
P["trikonasana_floor"] = dict(P["trikonasana"], lt=-18, ut=8, nk=8, hd=0, ua1=-88, fa1=-88, ua2=88, fa2=88, h2=88)

# ---------------------------------------------------------------- sun salutation extras
P["lunge"] = dict(lt=-15, ut=-30, nk=-60, hd=-75, face=-30, ua1=93, fa1=93, h1=0, ua2=91, fa2=91, h2=0,
                 th1=-10, sh1=92, ft1=0, th2=131.5, sh2=177, ft2=180, order=ARMFIRST)
P["plank"] = settle(dict(lt=-12, ut=-12, nk=-10, hd=-8, face=40, ua1=90, fa1=90, h1=0, ua2=92, fa2=92, h2=0,
                         th1=168, sh1=168, ft1=100, th2=168, sh2=168, ft2=100), ["toe1", "wr1", "fi1"],
                    ["th1", "sh1", "th2", "sh2", "ft1", "ft2"])
P["ashtanga_namaskara"] = settle(dict(lt=28, ut=12, nk=0, hd=-5, face=60, th1=125, sh1=180, ft1=100, th2=123, sh2=180, ft2=100,
                                      ua1=-150, fa1=82, h1=0, ua2=-148, fa2=82, h2=0, order=BACKARM),
                                 ["kn1", "toe1", "neckb", "wr1"], ["th1", "sh1", "lt", "ut", "ua1", "fa1", "th2", "sh2"])
P["bhujangasana"] = settle(dict(lt=-12, ut=-48, nk=-68, hd=-78, face=-12, th1=180, sh1=180, ft1=180, th2=179, sh2=179, ft2=179,
                                ua1=100, fa1=78, h1=0, ua2=98, fa2=76, h2=0), ["hip", "fi1", "wr1", "an1"],
                           ["ua1", "fa1", "ua2", "fa2", "lt"])
P["adho_mukha"] = settle(dict(lt=50, ut=54, nk=58, hd=62, face=125, th1=117, sh1=117, ft1=0, th2=115, sh2=115, ft2=0,
                              ua1=54, fa1=54, h1=0, ua2=52, fa2=52, h2=0), ["heel1", "toe1", "fi1", "wr1"],
                         ["th1", "sh1", "th2", "sh2", "ua1", "fa1", "ua2", "fa2"])

# ---------------------------------------------------------------- supine & rest
P["savasana"] = dict(lt=180, ut=180, nk=180, hd=180, face=-90, th1=0, sh1=0, ft1=-62, th2=1, sh2=1, ft2=-66,
                     ua1=5, fa1=4, h1=4, ua2=7, fa2=6, h2=6)
P["leg_raise"] = dict(P["savasana"], th1=-90, sh1=-90, ft1=-90)
P["double_leg_raise"] = dict(P["savasana"], th1=-90, sh1=-90, ft1=-90, th2=-88, sh2=-88, ft2=-88)
P["balasana"] = settle(dict(lt=24, ut=30, nk=42, hd=52, face=110, th1=58, sh1=180, ft1=180, th2=56, sh2=180, ft2=180,
                            ua1=165, fa1=172, h1=180, ua2=163, fa2=170, h2=180, order=BACKARM),
                       ["kn1", "an1", "headc"], ["th1", "lt", "ut", "nk", "hd", "th2"])
P["vajrasana"] = dict(th1=4, sh1=178, ft1=180, th2=5, sh2=177, ft2=180, ua1=80, fa1=20, h1=20, ua2=80, fa2=22, h2=22, face=0)
P["sukhasana_side"] = dict(th1=8, sh1=165, ft1=150, th2=6, sh2=170, ft2=155, ua1=78, fa1=22, h1=20, ua2=80, fa2=20, h2=18, face=0)
P["meditation_front"] = dict(view="front", face=None, th1=167, sh1=12, ft1=0, th2=13, sh2=168, ft2=180,
                             ua1=100, fa1=122, h1=150, ua2=80, fa2=58, h2=30)
P["bridge"] = settle(dict(lt=25, ut=18, nk=0, hd=0, face=-90, th1=192, sh1=100, ft1=180, th2=190, sh2=98, ft2=180,
                          ua1=175, fa1=178, h1=180, ua2=173, fa2=176, h2=180),
                     ["heel1", "toe1", "neckb", "headc", "wr1"], ["lt", "ut", "th1", "sh1", "th2", "sh2", "nk", "hd"])
P["supta_padangusthasana"] = dict(P["savasana"], th1=-80, sh1=-80, ft1=-80, ua1=-60, fa1=-70, h1=-70)
P["legs_up_wall"] = dict(P["savasana"], th1=-90, sh1=-90, ft1=-90, th2=-89, sh2=-89, ft2=-89, ft1b=0)

# ---------------------------------------------------------------- Sivananda 12 basic postures
P["sirsasana"] = dict(lt=90, ut=90, nk=90, hd=90, face=180, th1=-90, sh1=-90, ft1=-90, th2=-89, sh2=-89, ft2=-89,
                      ua1=125, fa1=5, h1=-40, ua2=121, fa2=8, h2=-40)
P["sirsasana_prep"] = settle(dict(lt=70, ut=84, nk=90, hd=90, face=180, th1=140, sh1=140, ft1=100, th2=138, sh2=138, ft2=100,
                                  ua1=125, fa1=5, h1=-40, ua2=121, fa2=8, h2=-40), ["crown", "el1", "wr1", "toe1"],
                             ["th1", "sh1", "th2", "sh2", "lt", "ut", "ua1", "fa1"])
P["sirsasana_tuck"] = dict(P["sirsasana"], lt=88, ut=90, th1=132, sh1=-42, ft1=-60, th2=130, sh2=-44, ft2=-62)
P["dolphin"] = settle(dict(lt=58, ut=62, nk=66, hd=70, face=130, th1=118, sh1=118, ft1=0, th2=116, sh2=116, ft2=0,
                           ua1=96, fa1=0, h1=0, ua2=94, fa2=0, h2=0), ["heel1", "toe1", "el1", "wr1"],
                      ["th1", "sh1", "th2", "sh2", "ua1", "ua2", "lt", "ut"])
P["sarvangasana"] = settle(dict(lt=95, ut=100, nk=175, hd=175, face=-90, th1=-92, sh1=-92, ft1=-92, th2=-90, sh2=-90, ft2=-90,
                                ua1=5, fa1=-105, h1=-110, ua2=8, fa2=-100, h2=-110), ["headc", "el1", "sh1"],
                           ["nk", "hd", "ua1", "ua2"])
P["viparita_karani"] = settle(dict(lt=55, ut=40, nk=5, hd=5, face=-90, th1=-110, sh1=-110, ft1=-110, th2=-108, sh2=-108, ft2=-108,
                                   ua1=180, fa1=-60, h1=-60, ua2=178, fa2=-62, h2=-62), ["headc", "neckb", "el1"],
                              ["lt", "ut", "ua1", "fa1", "ua2", "fa2", "nk", "hd"])
P["halasana"] = settle(dict(lt=98, ut=102, nk=175, hd=175, face=-90, th1=150, sh1=150, ft1=100, th2=148, sh2=148, ft2=100,
                            ua1=5, fa1=0, h1=0, ua2=6, fa2=2, h2=2), ["headc", "el1", "wr1", "toe1"],
                       ["nk", "hd", "ua1", "th1", "sh1", "ua2", "th2", "sh2"])
P["halasana_chair"] = dict(P["halasana"], th1=176, sh1=176, ft1=100, th2=175, sh2=175, ft2=100)
P["_unused_karnapidasana"] = settle(dict(lt=100, ut=108, nk=175, hd=175, face=-90, th1=128, sh1=-10, ft1=180, th2=126, sh2=-12, ft2=180,
                                 ua1=5, fa1=0, h1=0, ua2=6, fa2=2, h2=2), ["headc", "el1", "kn1", "toe1"],
                            ["nk", "hd", "th1", "sh1", "th2", "sh2", "ua1", "ua2"])
P["matsyasana"] = settle(dict(lt=183, ut=-138, nk=120, hd=106, face=195, th1=0, sh1=0, ft1=-65, th2=1, sh2=1, ft2=-68,
                              ua1=37, fa1=0, h1=0, ua2=36, fa2=0, h2=0), ["crown", "el1", "an1", "hip"],
                         ["nk", "hd", "ua1", "ua2"])
P["matsyasana_supported"] = dict(lt=183, ut=-172, nk=165, hd=150, face=220, th1=0, sh1=0, ft1=-65, th2=1, sh2=1, ft2=-68,
                                 ua1=20, fa1=10, h1=5, ua2=22, fa2=12, h2=6)
P["uttana_padasana"] = dict(P["matsyasana"], th1=-35, sh1=-35, ft1=-35, th2=-34, sh2=-34, ft2=-34,
                            ua1=-40, fa1=-38, h1=-36, ua2=-39, fa2=-37, h2=-35)
P["paschimottanasana"] = settle(dict(lt=-22, ut=-2, nk=5, hd=10, face=80, ua1=8, fa1=4, h1=20, ua2=9, fa2=5, h2=20,
                                     th1=0, sh1=0, ft1=-78, th2=1, sh2=1, ft2=-80), ["hip", "an1", "kn1"], ["th1", "sh1", "th2", "sh2"])
P["paschimottanasana_strap"] = dict(lt=-60, ut=-42, nk=-30, hd=-25, face=15, ua1=-5, fa1=0, h1=0, ua2=-4, fa2=1, h2=1,
                                    th1=-12, sh1=10, ft1=-80, th2=-11, sh2=11, ft2=-80)
P["paschimottanasana_deep"] = dict(lt=-10, ut=8, nk=10, hd=12, face=90, ua1=15, fa1=12, h1=25, ua2=16, fa2=13, h2=25,
                                   th1=0, sh1=0, ft1=-80, th2=1, sh2=1, ft2=-82)
P["dandasana"] = dict(th1=0, sh1=0, ft1=-80, th2=1, sh2=1, ft2=-82, ua1=92, fa1=90, h1=0, ua2=94, fa2=92, h2=0, face=0)
P["sphinx"] = settle(dict(lt=-5, ut=-24, nk=-42, hd=-55, face=0, th1=180, sh1=180, ft1=180, th2=179, sh2=179, ft2=179,
                          ua1=92, fa1=0, h1=0, ua2=90, fa2=0, h2=0), ["hip", "el1", "wr1", "an1"], ["ua1", "ua2", "lt", "ut"])
P["_unused_raja"] = dict(P["bhujangasana"], sh1=-60, ft1=-80, sh2=-62, ft2=-82, nk=-80, hd=-100, face=-60)
P["salabhasana"] = dict(lt=-2, ut=0, nk=-4, hd=0, face=65, th1=198, sh1=198, ft1=198, th2=197, sh2=197, ft2=197,
                        ua1=178, fa1=180, h1=180, ua2=177, fa2=179, h2=180, order=ARMFIRST)
P["ardha_salabhasana"] = dict(P["salabhasana"], th2=180, sh2=180, ft2=180, lt=0)
P["dhanurasana"] = dict(lt=-8, ut=-25, nk=-45, hd=-60, face=10, th1=190, sh1=-37, ft1=-120, th2=188, sh2=-40, ft2=-120,
                        ua1=197, fa1=197, h1=190, ua2=195, fa2=195, h2=190)
P["ardha_dhanurasana"] = dict(P["dhanurasana"], th2=180, sh2=180, ft2=180, ua2=95, fa2=80, h2=0)
P["kakasana"] = settle(dict(lt=50, ut=30, nk=15, hd=15, face=60, th1=56, sh1=203, ft1=195, th2=54, sh2=201, ft2=195,
                            ua1=95, fa1=88, h1=0, ua2=92, fa2=88, h2=0, order=["farArm", "farLeg", "torso", "head", "nearArm", "nearLeg"]),
                       ["wr1", "fi1"], ["fa1", "fa2"])
P["_unused_kakasana_prep"] = settle(dict(lt=-42, ut=-30, nk=-5, hd=10, face=60, th1=-5, sh1=110, ft1=0, th2=-7, sh2=112, ft2=0,
                                 ua1=90, fa1=90, h1=0, ua2=88, fa2=88, h2=0, order=["farArm", "farLeg", "torso", "head", "nearLeg", "nearArm"]),
                            ["heel1", "toe1", "fi1", "wr1"], ["th1", "sh1", "th2", "sh2", "ua1", "fa1", "ua2", "fa2", "lt"])
P["bakasana"] = dict(P["kakasana"], lt=62, ut=40, th1=64, sh1=200, th2=62, sh2=198, ua1=90, fa1=90, ua2=89, fa2=89)
P["mayurasana"] = dict(lt=2, ut=0, nk=-4, hd=0, face=20, th1=180, sh1=180, ft1=180, th2=179, sh2=179, ft2=179,
                       ua1=156, fa1=90, h1=180, ua2=154, fa2=90, h2=180)
P["malasana"] = settle(dict(lt=-62, ut=-72, nk=-78, hd=-82, face=0, th1=-12, sh1=116, ft1=0, th2=-10, sh2=114, ft2=0,
                            ua1=80, fa1=-60, h1=-80, ua2=78, fa2=-62, h2=-80), ["heel1", "toe1"], ["sh1", "sh2", "th1", "th2"])

# twists and seated, front view
P["ardha_matsyendrasana"] = dict(view="front", sw=0.55, lt=-90, ut=-90, nk=-90, hd=-90, face=180,
                                 th1=-40, sh1=60, ft1=90, th2=10, sh2=178, ft2=180,
                                 ua1=112, fa1=100, h1=100, ua2=46, fa2=56, h2=70,
                                 order=["farArm", "farLeg", "torso", "head", "nearLeg", "nearArm"])
P["easy_twist"] = dict(P["meditation_front"], sw=0.6, face=180, ua1=112, fa1=100, h1=100, ua2=70, fa2=100, h2=120)
P["baddha_konasana"] = dict(view="front", face=None, th1=162, sh1=18, ft1=0, th2=18, sh2=162, ft2=180,
                            ua1=98, fa1=78, h1=80, ua2=82, fa2=102, h2=100)

# kneeling
P["tabletop"] = settle(dict(lt=0, ut=0, nk=0, hd=0, face=60, th1=90, sh1=180, ft1=180, th2=91, sh2=180, ft2=180,
                            ua1=90, fa1=90, h1=0, ua2=91, fa2=91, h2=0), ["kn1", "an1", "wr1", "fi1"], ["ua1", "fa1", "ua2", "fa2"])
P["cat"] = dict(P["tabletop"], lt=-18, ut=16, nk=55, hd=75, face=150)
P["cow"] = dict(P["tabletop"], lt=12, ut=-14, nk=-38, hd=-50, face=-20)
P["ustrasana"] = dict(th1=90, sh1=180, ft1=180, th2=90, sh2=180, ft2=180, lt=-104, ut=-146, nk=-172, hd=178, face=-110,
                      ua1=118, fa1=108, h1=100, ua2=116, fa2=106, h2=100)
P["urdhva_dhanurasana"] = settle(dict(lt=5, ut=38, nk=70, hd=92, face=175, th1=160, sh1=100, ft1=180, th2=158, sh2=98, ft2=180,
                                      ua1=95, fa1=100, h1=180, ua2=93, fa2=98, h2=180), ["heel1", "toe1", "fi1", "wr1"],
                                 ["lt", "ut", "ua1", "fa1", "th1", "sh1", "ua2", "fa2", "th2", "sh2"])
P["navasana"] = dict(lt=-118, ut=-112, nk=-104, hd=-98, face=10, th1=-40, sh1=-40, ft1=-40, th2=-39, sh2=-39, ft2=-39,
                     ua1=12, fa1=12, h1=12, ua2=13, fa2=13, h2=13)

# ---------------------------------------------------------------- reference figures for the muscle atlas
P["front"] = dict(view="front", face=None, ua1=100, fa1=100, h1=100, ua2=80, fa2=80, h2=80)
P["arm_forward"] = dict(face=0, ua1=-2, fa1=-2, h1=-2, ua2=92, fa2=92, th2=91, sh2=91)
P["arm_up"] = dict(face=0, ua1=-92, fa1=-92, h1=-92, ua2=92, fa2=92, th2=91, sh2=91)
P["front_arms_out"] = dict(view="front", face=None, ua1=180, fa1=180, h1=180, ua2=0, fa2=0, h2=0)
