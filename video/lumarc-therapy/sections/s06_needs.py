"""s06 — Therapist: "Instagram, what do you need from him?" / Instagram: "Consistency. Good lighting. Reels. Is that
too much to ask?"  (lines 12-13, 28.66–36.84)

Beats (timeline s, 30 fps frame grid; word onsets measured on src/voice16k.raw — see _C_kit.MEASURED):
  28.66   the therapist (the shot started at 28.30 in s05), slow push: "Instagram, … what do you need from him?"
  29.833  "what" (29.83): pen click — his yellow legal pad swings in from the left (it never crosses the caption band;
          real paper: rules, margin, gum binding; a callback already on it: «Kevin: feels "creative" ??»). He writes
          «Instagram needs:» while he asks, and underlines it on "him?" (30.89).
  31.400  CUT to Instagram (line 13). The pad stays: every need is handwritten on it as he says it, each with a ding
          (E6 → G6 → B6, the list climbs): «1. Consistency» (31.44).
  32.89   «2. Good lighting» starts on "Good" — and on "lighting" (33.067) the brass floor lamp behind him CLICKS ON:
          bulb flare with a one-frame stutter, warm spill on the bookcase, a warm key and a soft beauty glow on his
          face. He stays beautifully lit for the rest of his line.
  34.200  "Reels." (34.19) — a Reels-style punch-in jump cut on him, «3. Reels» + the Reels glyph doodled next to it.
  35.200  the pad slides away to the left (list done).
  35.733  "Is that TOO much…" (TOO 35.74) — CRASH ZOOM onto his face (3-frame snap with motion blur, 'zoom'), held.
  36.267  "…to ASK?" (36.25) — CUT to Kevin's guilty face (brows up, eyes sliding away), slow push, until 36.84.
The lamp light is computed in world space (lit plate cached per level, light on the keyed take, bloom post-camera).
Captions: the engine's word-pop captions on the measured onsets; "Consistency. / Good lighting. / Reels." are the
handwriting on the pad (no stacked text), the captions return for "Is that too much to ask?".
"""
import math
from PIL import Image
import engine as E
from sections import _C_kit as K

START, END = E.span(12, 13)                   # 28.66 – 36.84
W, H, FPS = E.W, E.H, E.FPS
L12, L13 = E.TL[12], E.TL[13]

F_PAD = K.fr(K.wt(12, 'WHAT'))             # 895  29.833  pad swings in, pen click ("what" 29.83)
F_I = 942                                  # 31.400  Instagram (line 13 starts 31.38; "Consistency" 31.44)
F_LAMP = K.fr(K.wt(13, 'LIGHTING.'))       # 992  33.067  "lighting" (33.07): the lamp clicks on
F_REELS = K.fr(K.wt(13, 'REELS.'))         # 1026 34.200  "Reels." (34.19): punch-in
F_PADOUT = 1056                            # 35.200  the pad leaves (silence after "Reels.")
F_ZOOM = K.fr(K.wt(13, 'TOO'))             # 1072 35.733  crash zoom lands on "TOO" (35.74)
F_K = K.fr(K.wt(13, 'ASK?'))               # 1088 36.267  Kevin's guilty face on "ASK?" (36.25)

SCHED = dict(head=(29.90, .80), ul=(K.wt(12, 'HIM?'), .16), n1=(K.wt(13, 'CONSISTENCY.'), .52), n2=(K.wt(13, 'GOOD'), .56),
             n3=(K.wt(13, 'REELS.'), .30), reel=(K.wt(13, 'REELS.') + .27, .34))

CUES = [
    (K.wt(12, 'WHAT'), 'click', {'gain': 4}),                          # pen click as the pad comes in
    (K.wt(13, 'CONSISTENCY.'), 'ding', {'note': 'E6', 'gain': -2}),     # need #1
    (K.wt(13, 'GOOD'), 'ding', {'note': 'G6', 'gain': -2}),             # need #2
    (F_LAMP / FPS, 'click', {'gain': 10}),                             # the lamp switch
    (K.wt(13, 'REELS.'), 'ding', {'note': 'B6', 'gain': -2}),           # need #3 (+ punch-in)
    (F_PADOUT / FPS, 'swipe', {'gain': -12}),                          # the pad slides away
    (F_ZOOM / FPS, 'zoom', {}),                                        # crash zoom on "TOO"
]

PAD_C = (470, 1150)          # pad centre on screen (clear of the caption band at 1480, off his face)
PAD_S = 1.0
PAD_ROT = -2.5

def src(line, t): return line['s0'] + (t - line['t0'])

def pad_layer(ctx, t):
    f = K.fr(t)
    if f < F_PAD or f >= F_PADOUT + 8: return
    # in: swings in from the left on a slight arc (a hand sliding the pad into view) — it never sweeps through the
    # caption band; out: slides back out to the left.
    k_in = E.back(E.clamp((t - F_PAD / FPS) / .32), 1.2); k_out = E.ein(E.clamp((t - F_PADOUT / FPS) / .24))
    dx = -1000 * (1 - k_in) - 1050 * k_out
    dy = 70 * (1 - k_in) ** 2 + 50 * k_out + 3 * math.sin(t * 1.3)
    rot = PAD_ROT + 9 * (1 - k_in) + 6 * k_out + .3 * math.sin(t * .9)
    im = K.notepad(t, SCHED)
    if abs(PAD_S - 1) > .01: im = im.resize((int(im.width * PAD_S), int(im.height * PAD_S)), Image.BICUBIC)
    im = im.rotate(rot, Image.BICUBIC, expand=True)
    ctx.add('screen', im, PAD_C[0] + dx, PAD_C[1] + dy)

def i_cam(t):
    f = K.fr(t); u = t - F_I / FPS
    z = 1.03 + .018 * u
    if f >= F_REELS: z += .13                                          # Reels-style punch-in jump cut
    to = (520, 560)
    if f >= F_ZOOM - 2:                                                # crash zoom: frames -2, -1, 0 -> 1/3, 2/3, 1
        k = E.clamp((f - (F_ZOOM - 3)) / 3); k = 1 - (1 - k) ** 2
        z0 = 1.03 + .018 * ((F_ZOOM - 3) / FPS - F_I / FPS) + .13
        z = z0 + (1.62 - z0) * k + .04 * max(0., t - F_ZOOM / FPS)
        to = (520 + 20 * k, 560 + 20 * k)
    return K.face_cam(K.FACE['I'], z, to=to)

def draw(ctx, lt, t):
    f = K.fr(t)
    if f < F_I:
        # ---------------- the therapist: "Instagram, what do you need from him?" (+ his pad)
        K.cu_take(ctx, 'T', src(L12, t))
        ctx.cam.update(K.t_cam(t))
    elif f < F_K:
        # ---------------- Instagram: the needs; the lamp; Reels; crash zoom
        Lv = K.lamp_level(t, F_LAMP / FPS)
        K.cu_take(ctx, 'I', src(L13, t), fx=K.lamp_take(Lv) if Lv > .001 else None)
        cam = i_cam(t); ctx.cam.update(cam)
        ctx.bg_img = K.lamp_off_plate() if f < F_LAMP else K.lamp_plate(Lv)
        wraps = [K.lamp_bloom(Lv)]
        if f in (F_ZOOM - 2, F_ZOOM - 1):
            wraps.append(K.zoom_blur(1.0 if f == F_ZOOM - 2 else .55, anchor=K.cam_map(ctx.cam, *K.FACE['I'])))
        ctx.wrap = K.chain(*wraps)
    else:
        # ---------------- "…to ASK?" — Kevin's guilty face
        u = t - F_K / FPS
        K.cu_take(ctx, 'K', 24.20 + u)
        ctx.cam.update(K.face_cam(K.FACE['K'], 1.30 + .06 * u, to=(540, 620)))
    pad_layer(ctx, t)
    K.captions(ctx, t, (12, 13), skip={(13, 'CONSISTENCY.'), (13, 'GOOD'), (13, 'REELS.')})
