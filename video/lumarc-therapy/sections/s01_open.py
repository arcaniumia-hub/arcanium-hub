"""s01 — the hook (0.00–3.02): "So… what brings you two here today?"

0.00–1.10  prestige cold-open title over the empty office (wide plate, dimmed, slow push): SESSION 1 / COUPLES THERAPY
           / "Kevin & his Instagram" — the absurd couple is named in the hook frame. The therapist's "So…" (0.42) plays
           under it as V.O. (his lips still hold the "o" until ~1.05, so the cut waits for "what").
1.10       CUT to the therapist (MS) one frame before "what" (1.13); chip THE THERAPIST. The "So…" caption page ends ON
           the cut (no half-faded word over his face).
1.70       CUT on "you" (1.75): Kevin — apron, hurt frown (silent take src 3.15…).
1.90       CUT on "two" (1.92): his Instagram — gradient hoodie, arms crossed, side-eye squint (src 3.94…), held through
           "here" so the absurd couple reads.
2.40       CUT back to the therapist on "today?" (2.43), unbothered, chip back on (same shot, same label) until 2.78.
All takes go through K.show() (clean matte: no cream outline / green fringe).
Measured onsets (voice16k.raw): SO… .42 · WHAT 1.13 · BRINGS 1.43 · YOU 1.75 · TWO 1.92 · HERE 2.14 · TODAY? 2.43
"""
import engine as E
from sections import _A_kit as K

START, END = E.span(0, 0)
W, H, FPS = E.W, E.H, E.FPS
L0 = E.TL[0]

F_T1 = 33      # 1.100  therapist (one frame before WHAT 1.13)
F_K = 51       # 1.700  Kevin cutaway (YOU 1.75)
F_I = 57       # 1.900  Instagram cutaway (TWO 1.92)
F_T2 = 72      # 2.400  back to the therapist (TODAY? 2.43)
CUTS = [F_T1 / FPS, F_K / FPS, F_I / FPS, F_T2 / FPS]
CHIP_Y = 1160
I_OPEN = 35.0      # Instagram's silent reaction material (src 34.7-36.2: chin up, side-eye, arms crossed, mouth shut)
Z_OPEN, OPEN_Y = 1.02, 300.
TITLE_Y = 1150     # centre of the title block: kicker ~1000, big lines ~1060-1290, clear of the face and the caption

CUES = [
    (0.02, 'thud', {'gain': -2}),                 # the prestige title lands (nudged off 0.00 so the attack survives)
    (F_T1 / FPS + .01, 'tick', {'gain': -6}),     # chip THE THERAPIST
    (F_K / FPS, 'tick', {'gain': -8, 'pan': -.2}),   # cutaway accents (tiny, under the dialogue)
    (F_I / FPS, 'tick', {'gain': -8, 'pan': .2}),
]

def t_src(t): return L0['s0'] + (t - L0['t0'])

def draw(ctx, lt, t):
    f = K.fr(t)
    if f < F_T1:
        # ---------------- cold open: Instagram's silent offended side-eye + the premise title (the hook frame)
        K.show(ctx, 'I', I_OPEN + t, 'I')
        k = t / (F_T1 / FPS)
        ctx.cam.update(z=Z_OPEN + .05 * k, x=K.FACE['I'][0], y=OPEN_Y)
        ctx.wrap = K.dim_wrap()
        ctx.post.update(vignette=.50, sat=.92)
        ctx.add('screen', K.hook_title(t, F_T1 / FPS), W / 2, TITLE_Y)
    elif f < F_K:
        # ---------------- therapist, first sight: "what brings…"
        K.show(ctx, 'T', t_src(t), 'T')
        ctx.cam.update(z=1.0 + .03 * (t - F_T1 / FPS), x=528., y=520.)
        K.chip(ctx, t, F_T1 / FPS + .01, 9.0, 'THE THERAPIST', '', y=CHIP_Y, speed=1.9)   # quick: the shot is 0.6 s
    elif f < F_I:
        # ---------------- "you" -> Kevin (silent hurt frown), medium close
        u = t - F_K / FPS
        K.show(ctx, 'K', 3.15 + u, 'K')
        ctx.cam.update(K.face_cam(K.FACE['K'], 1.20 + .10 * u, to=(540, 600)))
    elif f < F_T2:
        # ---------------- "two" -> Instagram (arms crossed, side-eye squint), medium close
        u = t - F_I / FPS
        K.show(ctx, 'I', 3.94 + u, 'I')
        ctx.cam.update(K.face_cam(K.FACE['I'], 1.16 + .08 * u, to=(540, 560)))
    else:
        # ---------------- back to the therapist: "…today?" (continuous take time); his label returns with him
        K.show(ctx, 'T', t_src(t), 'T')
        ctx.cam.update(z=1.0 + .03 * (t - F_T1 / FPS), x=528., y=520.)
        K.chip(ctx, t, F_T2 / FPS - 1.0, 2.78, 'THE THERAPIST', '', y=CHIP_Y)                # already fully on
    K.captions(ctx, t, (0,), cuts=CUTS)
