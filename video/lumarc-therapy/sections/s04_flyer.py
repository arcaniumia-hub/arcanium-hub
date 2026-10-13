"""s04 — "And when you DO show up… it's a flyer." / Kevin: "People love flyers!" / "Seven fonts, Kevin. SEVEN."  (lines 6-8)

Beats (timeline s, frame grid 30 fps; onsets measured on src/voice16k.raw, see _B_kit.MEASURED):
  15.04  Instagram, slow push through "And when you DO show up…", his loaded pause and "it's a ffff-" (the long /f/
         17.13-17.34 is a visible lip-bite: the wind-up).
  17.267 SMASH CUT, top-down on the walnut coffee table between them, mid-fall: the printed flyer is SLAPPED down like
         evidence in an interrogation — out of focus and motion-blurred while close to the lens, its shadow racing in
         to meet it. IMPACT 17.367 on the voiced "FLY-" (17.35, the stressed syllable — the slap and the word hit
         together): table/camera jolt, the sheet skids a few px on its air cushion. Paper = real sheet (printer margins,
         quarter-fold creases, dog-eared corner, fibre, ink never pure white), window light + fig-leaf shadows.
  17.967 Kevin, proud and defensive: "People love flyers!" (slow push).
  19.80  SMASH CUT on "Seven" (/s/ 19.83) to the flyer: a red felt-tip (ink multiplied into the print) loops fonts 1-6
         in rapid fire — capsule loops that hug each block, a handwritten number by each, a tick per loop — the camera
         drifting down the page with the count.
  21.10  "Kevin." (21.13) — cutaway to Kevin's silent guilty furrow (tighter reaction camera).
  21.633 "SEVEN." (/s/ 21.67) — back on the flyer, CRASH ZOOM into the bottom corner: the 7th loop goes round the tiny
         "*some exclusions apply" during the hiss; the big "7" lands on the voiced "SE-" (21.95) = the sting's second stab.
  22.233 DUNNN (22.25): Instagram's smug face, dramatic eased push-in, held into the therapist's question (s05).
B_review: measured captions (FLYER no longer 0.5 s late, no stale page over the Kevin / flyer cuts), slap on the
stressed syllable, readable count (capsule loops, multiply ink, digits off the busy art), hero 7 framed with its loop,
no black table corners in the slap, clean matte on all takes.
"""
import math
import numpy as np
from PIL import Image
import engine as E
from sections import _B_kit as K

START, END = E.span(6, 8)                     # 15.04 – 22.94

WORDS = {(seg, w): t for seg in (6, 7, 8) for w, t in K.MEASURED[seg]}
FR = lambda j: j / E.FPS
T_FLYER = WORDS[(6, 'FLYER.')]           # 17.13 (the /f/); the stressed "FLY" voices at 17.35
CUT_SLAP = FR(518)          # 17.2667 — out of the lip-bite /f/, mid-fall
IMPACT = FR(521)            # 17.3667 — the slap lands on the voiced "FLY-" (17.35)
CUT_K1 = FR(539)            # 17.9667 — Kevin
CUT_COUNT = FR(594)         # 19.80   — the flyer + marker ("Seven" /s/ 19.83)
CUT_K2 = FR(633)            # 21.10   — Kevin's guilty face ("Kevin." /k/ 21.13)
CUT_SEVEN = FR(649)         # 21.6333 — back on the flyer
ZOOM7 = FR(650)             # 21.6667 — crash zoom ("SEVEN." /s/ 21.67)
DIGIT7 = FR(657)            # 21.90 — the big 7 is written over frames 658-659: half on 21.933, whole on 21.967
                            #   = the voiced "SE-" (21.95) and the sting's second stab (21.67 + .28)
CUT_IG = FR(667)            # 22.2333 — DUNNN (21.67 + .58): Instagram

COUNT = [FR(594 + 6 * i) for i in range(6)]        # loop i starts drawing (4 frames each, its number right after)
CIRC_DUR, DIG_DUR = 4 / E.FPS, 2.4 / E.FPS
C7_START, C7_DUR = ZOOM7 + 1 / E.FPS, 4 / E.FPS

CUES = [
    (IMPACT, 'whoosh', {'gain': -5}),                        # the throw (peaks on the slap)
    (IMPACT, 'impact', {'gain': -3}),                        # the slap on the table
] + [(round(c + CIRC_DUR, 3), 'tick', {}) for c in COUNT] + [
    (WORDS[(8, 'SEVEN.')], 'zoom', {}),                      # crash zoom into the fine print
    (WORDS[(8, 'SEVEN.')], 'sting', {}),                     # dun (zoom) – dun (the 7) – DUNNN (Instagram)
]

IG_FACE = (452, 410)
K_FACE = (548, 440)

def _smooth(x):
    x = E.clamp(x); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------------------------------- the coffee table
# Both inserts are one physical set-up: the flyer on the walnut coffee table between them, top-down, in the window
# light (leaf shadows from the fig tree). World = flyer art px.
REST = (438, 574, -0.8, 1.0)             # where the sheet comes to rest (centre wx, wy, rotation, scale)
CAM_ROT = -3.0
FALL0 = IMPACT - 3.5 / E.FPS             # the sheet's fall (we cut in mid-fall, 3 frames before the slap)

def _light_shift(t):
    return 7 * math.sin(t * .9), 5 * math.sin(t * .7 + 1)                    # the fig tree in a breeze

def _fall_pose(t):
    """(pose, h) of the sheet while it falls onto the table (h = height 0..1)."""
    k = E.clamp((t - FALL0) / (IMPACT - FALL0)); h = .8 * (1 - k ** 1.35)
    if t < IMPACT:
        return (REST[0] + 10 + 260 * h, REST[1] - 14 - 360 * h, REST[2] + .8 + 18 * h, 1 + 1.05 * h), h
    dt = t - IMPACT; e = 1 - math.exp(-dt / .085)                            # it lands and skids on its air cushion
    flex = 1 + .012 * math.exp(-dt / .05) * math.cos(2 * math.pi * dt / .1)
    return (REST[0] + 10 * (1 - e), REST[1] - 14 * (1 - e), REST[2] + .8 * (1 - e), flex), 0.0

def _slap_frame(t):
    pap = K.paper_rgba(2)
    dt = t - IMPACT
    s = .93 * (1 + .025 * math.exp(-max(dt, 0) / .1) * (dt >= 0)) + .03 * E.clamp(dt / .85)
    C = [540, 800]
    if dt >= 0:                                                               # the table (and camera) jolt
        C[1] += 15 * math.exp(-dt / .08) * math.cos(2 * math.pi * 9 * dt)
        C[0] += -8 * math.exp(-dt / .08) * math.sin(2 * math.pi * 12 * dt)
    if t < IMPACT:                                                            # motion blur: half-frame shutter
        poses = [_fall_pose(t - i * .5 / E.FPS / 5)[0] for i in range(6)]; h = _fall_pose(t)[1]
    else:
        pose, h = _fall_pose(t); poses = [pose]
    return K.table_scene((448, 600), s, CAM_ROT, C, pap, poses, h, _light_shift(t))

# ------------------------------------------------------------------------------------------- the count (19.80+)
S2 = 2
SEVEN_AT, SEVEN_S = (722, 962), 2.60     # art point framed by the crash zoom (the 7 + the circled fine print), px/art px
def _cam_count(t):
    """(focus world x, y, screen px per art px, rot, screen focus) during the count / the 7."""
    k = _smooth((t - CUT_COUNT) / (CUT_K2 - CUT_COUNT))                      # drifts down the page with the count
    fx, fy = K.art_to_world(452, 545 + 50 * k, REST)
    s, rot, C = 1.03 + .03 * k, CAM_ROT + .6 + .4 * k, (540, 800)
    fx += 2.0 * math.sin(t * 2.3) + 1.2 * math.sin(t * 5.1 + 1); fy += 1.6 * math.sin(t * 1.9 + 2)   # handheld life
    if t >= ZOOM7 - 1e-6:                                                     # crash zoom into the fine print
        z = E.eout((t - ZOOM7 + 1 / E.FPS) / (2.6 / E.FPS))
        tx, ty = K.art_to_world(*SEVEN_AT, REST); ts = SEVEN_S * (1 + .03 * E.clamp((t - DIGIT7) / .3))
        fx, fy, s, rot = fx + (tx - fx) * z, fy + (ty - fy) * z, s + (ts - s) * z, rot + (-1.6 - rot) * z
        C = (540, 800 + 160 * z)
    return (fx, fy), s, rot, C

def _marks(t):
    st = []
    for i, c in enumerate(COUNT):
        cf = E.eout((t - c) / CIRC_DUR) if t >= c else 0.0
        df = E.clamp((t - c - CIRC_DUR) / DIG_DUR)
        st.append((cf, df))
    cf = E.eout((t - C7_START) / C7_DUR) if t >= C7_START else 0.0
    st.append((cf, E.clamp((t - DIGIT7) / (2.2 / E.FPS))))
    return st

def _count_frame(t):
    F, s, rot, C = _cam_count(t)
    return K.table_scene(F, s, rot, C, K.marked_paper(S2, _marks(t)), [REST], 0.0, _light_shift(t))

# ------------------------------------------------------------------------------------------- draw
def draw(ctx, lt, t):
    if t < CUT_SLAP:
        # Instagram: slow push through the setup, his loaded pause and the "ffff" wind-up
        K.show(ctx, 'I', ctx.shot['src'], 'I')
        ctx.cam.update(z=1 + .035 * (t - START), x=IG_FACE[0], y=IG_FACE[1])
    elif t < CUT_K1:
        ctx.full = _slap_frame(t)                         # "FLY-er." — SLAP onto the coffee table
    elif t < CUT_COUNT:
        # Kevin: "People love flyers!" — proud, defensive
        K.show(ctx, 'K', 10.08 + (t - 18.08), 'K')
        ctx.cam.update(z=1 + .028 * (t - CUT_K1), x=K_FACE[0], y=K_FACE[1])
    elif t < CUT_K2 or CUT_SEVEN <= t < CUT_IG:
        ctx.full = _count_frame(t)
        if ZOOM7 - .5 / E.FPS <= t < ZOOM7 + 1.5 / E.FPS:  # smooth crash-zoom blur on the picture only
            amt = .09 if t < ZOOM7 + .5 / E.FPS else .03
            ctx.wrap = lambda fr, a=amt: K.zoom_blur(fr, a, (540, 900))
    elif t < CUT_SEVEN:
        # "Kevin." — his silent guilty face, from a tighter reaction camera
        K.show(ctx, 'K', 11.95 + (t - CUT_K2), 'K')
        ctx.cam.update(z=1.13 + .05 * (t - CUT_K2), x=520, y=540, dy=10)
    else:
        # DUNNN — Instagram's smug face, dramatic push-in
        K.show(ctx, 'I', ctx.shot['src'], 'I')
        k = E.eout((t - CUT_IG) / .75)
        ctx.cam.update(z=1.0 + .17 * k, x=500, y=420)
    K.captions(ctx, t, (6, 7, 8), cuts=(CUT_K1, CUT_COUNT, CUT_K2, CUT_SEVEN),    # "SEVEN." stays on his face
               at={(6, 'FLYER.'): IMPACT})                  # FLYER. pops WITH the slap on the voiced "FLY-"
