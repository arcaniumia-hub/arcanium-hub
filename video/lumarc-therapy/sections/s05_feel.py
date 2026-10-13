"""s05 — Therapist: "Kevin… how did that make you feel?" / Kevin: "…Creative?" / [dead air] / Instagram: "My algorithm
cried."  (lines 9-11, 22.94–28.66)

Beats (timeline s, 30 fps frame grid; word onsets measured on src/voice16k.raw — see _C_kit.MEASURED):
  22.94   the therapist, calm and deadpan, MS; a slow creeping push through "Kevin…" and his loaded pause (23.35–23.81)
          into "how did that make you feel?" (FEEL 24.52).
  25.100  CUT to Kevin (tighter) while the question hangs: brows knotted, eyes shut, searching for the word (silent take
          tail) -> "…Creative?" (25.68) with a hopeful little smile. Slow push the whole time.
  26.167  REACTION CUT on the tail of "…Creati-ve?": the therapist hears the end of the word and just looks (head tilt,
          squint), locked-off close shot, 12 frames — the DEAD AIR (score out 25.57–26.80) + crickets at 26.30.
  26.567  CUT to Instagram mid side-eye (his own pre-roll: looking away in disgust), he turns back to camera ->
          "My algorithm…" (26.89). The lamp behind him is off (continuity with the "Good lighting." gag in s06).
  27.667  "cried." (27.67) — SMASH CUT to a screen recording of his Insights: Accounts reached — the daily line races off
          a cliff to zero, the total counts down 1,204 -> 3, the red "▼ 99.8%" lands with a low thud (27.933). A slow
          screen-recording punch-in on the cliff.
  28.300  CUT to the therapist (silent; his take's pre-roll into his next line) — he takes it in, unbothered. The shot
          runs on into s06 ("Instagram, what do you need from him?").
"""
import math
from PIL import Image
import engine as E
from sections import _C_kit as K

START, END = E.span(9, 11)                    # 22.94 – 28.66
W, H, FPS = E.W, E.H, E.FPS
L9, L10, L11, L12 = E.TL[9], E.TL[10], E.TL[11], E.TL[12]

F_K = 753          # 25.100  Kevin, searching for the word (FEEL? ends 25.02)
F_TS = 785         # 26.167  reaction cut on the last syllable of "…Creative?" (ends 26.30): the therapist's look
F_I = 797          # 26.567  Instagram's side-eye -> "My algorithm"
F_G = 830          # 27.667  "cried." (27.67) -> Insights screen recording
F_THUD = 838       # 27.933  the line hits zero, the red delta lands
F_T = 849          # 28.300  the therapist (silent) -> s06
T_PL0, T_PL1 = (F_G + 1) / FPS, F_THUD / FPS        # the plunge: 27.70 -> 27.933

CUES = [
    (26.30, 'crickets', {'dur': .5, 'gain': 4}),       # dead air (the moment "…Creative?" ends)
    (F_G / FPS, 'swipe', {'gain': -8}),               # into the screen recording on "cried."
    (F_THUD / FPS, 'thud', {'gain': -1}),             # the line hits the floor / -99.8%
]

def src(line, t): return line['s0'] + (t - line['t0'])

def draw(ctx, lt, t):
    f = K.fr(t)
    if f < F_K:
        # ---------------- the therapist: "Kevin… how did that make you feel?" — creeping push
        K.cu_take(ctx, 'T', src(L9, t))
        u = t - START
        ctx.cam.update(z=1.0 + .018 * u + .012 * max(0., u - .45), x=528., y=500.)
    elif f < F_TS:
        # ---------------- Kevin, searching… "…Creative?" — slow push on a tighter frame
        u = t - F_K / FPS
        K.cu_take(ctx, 'K', src(L10, t))
        ctx.cam.update(K.face_cam(K.FACE['K'], 1.14 + .05 * u, to=(540, 620)))
    elif f < F_I:
        # ---------------- dead air: the therapist's look (locked off)
        u = t - 26.30
        K.cu_take(ctx, 'T', 26.15 + u)                                   # silent reaction material
        ctx.cam.update(K.face_cam(K.FACE['T'], 1.40, to=(540, 640)))
    elif f < F_G:
        # ---------------- Instagram: side-eye, turns, "My algorithm…"
        u = t - F_I / FPS
        K.cu_take(ctx, 'I', src(L11, t))
        ctx.bg_img = K.lamp_off_plate()
        ctx.cam.update(K.face_cam(K.FACE['I'], 1.06 + .035 * u, to=(520, 560)))
    elif f < F_T:
        # ---------------- "cried." — the Insights screen recording
        u = t - F_G / FPS
        scr = K.insights_frame(t, F_G / FPS, T_PL0, T_PL1)
        z = 1.0 + .06 * K.smooth(u / .55)                                  # editor's punch-in (number stays in the safe area)
        jolt = 0.0
        if f >= F_THUD: jolt = 7 * math.exp(-(t - F_THUD / FPS) / .06) * math.cos(2 * math.pi * 11 * (t - F_THUD / FPS))
        dy = jolt - 34 * (1 - E.eout(u / .16))                             # the screen still settling from a scroll
        ctx.full = E.zoom(scr, z, (220, 1100), dy=dy) if (z > 1.001 or abs(dy) > .3) else scr
        ctx.post.update(vignette=.10, grain=.55)
    else:
        # ---------------- the therapist, silent: takes it in (continues into s06)
        K.cu_take(ctx, 'T', src(L12, t))
        ctx.cam.update(K.t_cam(t))
    K.captions(ctx, t, (9, 10, 11), zmax={(9, 'MAKE'): F_K / FPS, (10, '…CREATIVE?'): F_TS / FPS, (11, 'CRIED.'): F_T / FPS})
