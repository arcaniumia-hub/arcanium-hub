"""s06 — PICK THREE + CTA + END CARD (31.72–40.60): "You don't have to pick two anymore. Pick three. Tap 'Send message',
or call the number on the screen." + his silent smile (the end card).

 A  31.73 CUT back to him after the montage: he sits right, tight push that settles (z 1.30 -> 1.21, a 1.2° roll
    settles), DOF studio.  The glass triangle REBUILDS beside him: the orbs fly in from the lens and lock ON the words —
    FAST on "YOU" (31.85), CHEAP on "DON'T" (31.95), GOOD on "HAVE" (32.05) — the rods draw, the plate fades in.
    32.37 "PICK": GOOD + FAST light (overdrive) and the beam draws GOOD -> FAST · 32.53 "TWO": the red ✗ stamps CHEAP.
    32.73 "ANYMORE": a glowing LUMARC-gradient bar STRIKES THROUGH the caption "PICK TWO" (lands 32.87 on "-MORE":
    the words go grey, the triangle jolts) · 33.15–33.57 the pause: slow push, the ✗ flickers like a dying neon.
 B  33.57 "PICK": SNAP — the triangle flies to centre stage and grows, the world goes behind frosted brand glass (violet
    duotone), the ✗ is BLOWN OFF CHEAP, "PICK" slams in at the top.  33.767 "THREE": THE DROP — all three vertices and
    edges BLAZE (kit complete), full-frame shockwave, flash, god rays, shake, chromatic hit, "THREE." slams in at the
    bottom in huge LUMARC gradient.  The hero triangle floats (3-D drift, energy pulses) until a WHIP-PAN up exits it.
 C  34.43 JUMP (the whip-pan continues: the new shot rises in from below with motion blur): he is framed lower and
    smaller (s .76, the take's cut edges feathered into the dark), a premium frosted-glass CTA card floats over his head
    with the gradient "Send message" pill (generic chat bubble).  34.53 "TAP" (caption): a fingertip touch indicator
    comes down on the pill's right end — press, ripple rings, glow.  35.03 "SEND": a light sheen reads the label (it IS
    the caption of "Send message") and a sent chat bubble "Hi! I want all three." shoots out of the button, landing
    35.30 on "MESSAGE" (delivered ticks, idle float).  36.07 "OR": the bubble flies off, the card rises + grows ·
    36.20 "CALL": the phone row pops in, the handset RINGS (ring waves), (854) 295-2249 wipes in with a light edge ·
    36.53 "NUMBER": a sheen runs through the digits (pop) · 36.93 "SCREEN": a gradient underline sweeps under the
    number and viewfinder corners snap around it.
 D  37.37 (his last word ends) the button folds away, the card wraps the phone row and glides to its end slot.
    37.47 END CARD (his silent smile): BOOM + SHIMMER — the studio melts into the LUMARC brand space (bokeh, exposure
    kick), he settles lower; the all-lit triangle IGNITES where the logo will be (callback to "Pick three.", ring) and
    37.61 spins + collapses into the LUMARC logo (flash + sting 38.03, wordmark wipe, light sweep 38.41);
    38.30 "Pick three." rises, 38.48 "Fast. Affordable. Actually good.", 38.62 the card grows: slumarc.com ·
    @lumarc_studio under the number.  The phone never leaves the screen.  39.90 a last sweep over "Pick three." + number.

Everything key sits inside the Meta safe zone (x 70–960, y 280–1250); captions are my own pages in the engine look on
the measured onsets (never over his face).  The logo resolve moved from "Pick three." to the end card: it gives the
hero triangle a full beat on the drop and gives the end card its own brand reveal on the closing BOOM.
Word onsets measured on src/tight16k.raw (10 ms RMS + 80–1000 Hz / >3 kHz band envelopes + spectrogram, out/T/sp_*.png).
Review pass (out/T_review): the take's left frame edge (he sits at x +265) is feathered into the studio in beats A/B;
the drop moved one frame later (33.767, between the "th" onset and the vowel); PICK uses the same gradient voice as
THREE. with ~50 px air to the FAST label; the tap lands lower-right on the pill; the end-card tagline is 52 px.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _tri as TRI
from sections import _shared as SH
from sections import _T_kit as K

START, END = E.span(28, 33)                     # 31.72 – 40.60
W, H, FPS = E.W, E.H, E.FPS
clamp = E.clamp
lerp, smooth, eo, ei, expo, eio, bump, dec, hr = K.lerp, K.smooth, K.eo, K.ei, K.expo, K.eio, K.bump, K.dec, K.hr

# word onsets (master timeline seconds), measured on src/tight16k.raw
ON = dict(
    # seg 28 "You don't have to pick two anymore."   ("any-MORE": the m-nasal starts at 32.86)
    YOU=31.85, DONT=31.92, HAVE=32.05, TO=32.26, PICK1=32.37, TWO=32.54, ANY=32.74, MORE=32.86, END28=33.12,
    # seg 29 "Pick three."   (p-burst 33.57, "th" 33.72, vowel 33.87)
    PICK=33.58, THREE=33.73, END29=34.10,      # THREE: k-release 33.72, 'th' 33.73-33.84, 'r' 33.85, vowel 33.87
    # seg 30-31 "Tap 'Send message',"
    TAP=34.54, END30=34.76, SEND=35.04, MESSAGE=35.31, END31=35.79,
    # seg 32 "or call the number on the screen."
    OR=36.06, CALL=36.19, THE=36.43, NUMBER=36.53, ON=36.85, THE2=36.90, SCREEN=36.95, END32=37.36,
)


def F(j): return j / FPS
T0 = F(952)            # 31.733 first frame (31.700 already shows seg 28's pose: it belongs to the montage section)
A_DUR = .84                                          # assemble a(t) = .20 + (t - T0) / A_DUR
def T_A(a): return T0 + (a - .20) * A_DUR
T_YOU, T_DONT, T_HAVE = T_A(.34), T_A(.46), T_A(.58)  # FAST / CHEAP / GOOD lock: 31.851 / 31.952 / 32.052
T_PICK1, T_TWO, T_ANY, T_MORE = F(971), F(976), F(982), F(986)
T_PICK, T_THREE = F(1007), F(1013)                   # 33.567, 33.767 ('th' 33.74, vowel 33.87: the drop sits between)
T_C = F(1033)          # 34.433 = first frame showing seg 30's pose (JUMP) — the CTA shot
T_TAP, T_SEND, T_MSG = F(1036), F(1051), F(1059)
T_OR, T_CALL, T_NUM, T_SCREEN = F(1082), F(1086), F(1096), F(1108)
T_END = F(1124)        # 37.467 END CARD
T_LOGO = T_END + .14   # logo morph start (1.0 s): flash at +.42 -> 38.03
D_LOGO = 1.0
T_PT, T_TAG, T_HDL, T_SWEEP = 38.30, 38.48, 38.62, 39.90

# ================================================================================================ sound
CUES = [
    (T0, 'whoosh', {'gain': -9}),                                  # cut-in, orbs in flight
    (T_YOU, 'lock', {'gain': -9, 'pan': -.25}), (T_DONT, 'lock', {'gain': -10, 'pan': -.45}), (T_HAVE, 'lock', {'gain': -10, 'pan': -.1}),
    (T_A(.64), 'shing', {'gain': -17, 'pan': -.4}), (T_A(.76), 'shing', {'gain': -16, 'pan': -.3}),   # rods land
    (T_PICK1, 'ding', {'note': 'G6', 'gain': -9, 'pan': -.15}), (T_PICK1 + .01, 'ding', {'note': 'E6', 'gain': -11, 'pan': -.3}),
    (T_PICK1, 'pop', {'gain': -15}), (T_PICK1 + .13, 'shing', {'gain': -11, 'pan': -.2}),
    (T_TWO, 'stamp', {'gain': -9, 'pan': -.4}), (T_TWO + .01, 'buzzer', {'dur': .22, 'gain': -15}),
    (T_ANY, 'swipe', {'gain': -6, 'pan': -.3}),                    # strike-through
    (T_MORE, 'thud', {'gain': -9}),
    (33.17, 'riser', {'to': T_THREE, 'gain': -8}),
    (T_PICK, 'whoosh', {'gain': -6}), (T_PICK, 'impact', {'gain': -9}), (T_PICK + .02, 'pop', {'gain': -8}),
    (T_THREE, 'boom', {'gain': 0}), (T_THREE, 'braam', {'note': 'D2', 'dur': 2.0, 'gain': -4}),
    (T_THREE, 'impact', {'gain': -6}), (T_THREE + .02, 'shimmer', {'gain': -8}), (T_THREE, 'sub', {'gain': -8}),
    (T_C - .04, 'swoosh', {'gain': -7}),                            # whip-pan
    (T_TAP, 'tap', {'gain': -2}), (T_TAP + .01, 'click', {'gain': -12}),
    (T_SEND, 'whoosh', {'gain': -13, 'pan': .25}),                  # message sent
    (T_SEND + .03, 'shimmer', {'gain': -17}),
    (T_MSG, 'notify', {'gain': -8, 'pan': .2}),                     # delivered
    (T_OR - .02, 'swipe', {'gain': -13}),                           # bubble off, card grows
    (T_CALL, 'pop', {'gain': -8}), (T_CALL + .02, 'ding', {'note': 'E6', 'gain': -14}), (T_CALL + .13, 'ding', {'note': 'E6', 'gain': -17}),
    (T_CALL + .05, 'type', {'i': 0, 'gain': -15}), (T_CALL + .12, 'type', {'i': 1, 'gain': -16}), (T_CALL + .19, 'type', {'i': 2, 'gain': -17}),
    (T_NUM, 'shimmer', {'gain': -10}),
    (T_SCREEN, 'swipe', {'gain': -10}), (T_SCREEN + .02, 'click', {'gain': -9}),
    (T_END, 'boom', {'gain': 0}), (T_END, 'shimmer', {'gain': -4}), (T_END + .01, 'impact', {'gain': -8}),
    (T_LOGO, 'swoosh_up', {'gain': -10}), (T_LOGO + .42 * D_LOGO, 'sting', {'gain': -6}), (T_LOGO + .80 * D_LOGO, 'shimmer', {'gain': -12}),
    (T_PT, 'swipe', {'gain': -14}), (T_TAG, 'tick', {'gain': -15}), (T_HDL, 'tick', {'gain': -16}),
    (T_SWEEP, 'shimmer', {'gain': -11}),
]

# ================================================================================================ captions
def font_w(text, sz):
    l, t, r, b = E.font(sz).getbbox(text); return r - l


def page(lines, a, z, cx, cy, base=90, maxw=900, k_emph=1.2):
    ws = [dict(text=tx, emph=em, t0=t0, line=li) for li, ln in enumerate(lines) for tx, em, t0 in ln]
    for k, w in enumerate(ws): w['t1'] = ws[k + 1]['t0'] if k + 1 < len(ws) else z - .12
    return dict(words=ws, a=a, z=z, cx=cx, cy=cy, base=base, maxw=maxw, n=len(lines), ke=k_emph)


CX = 515                        # content centre x of the CTA / end card (safe zone x 70-960)
ACX, ACY, AW = 345, 1150, 500                   # beat A: the free column under the triangle (he sits right)
PAGES = [
    page([[('YOU', 0, ON['YOU']), ("DON'T", 0, ON['DONT'])], [('HAVE', 0, ON['HAVE']), ('TO', 0, ON['TO'])]], ON['YOU'] - .04, T_PICK1 - .02, ACX, ACY, 88, AW),
    page([[('PICK', 0, T_PICK1), ('TWO', 0, ON['TWO'])], [('ANYMORE.', 1, ON['ANY'])]], T_PICK1 - .02, T_PICK + .07, ACX, ACY - 4, 92, AW, 1.16),
    page([[('TAP', 1, ON['TAP'])]], T_C + .03, T_SEND - .05, CX, 402, 100, 850),
    page([[('OR', 0, ON['OR']), ('CALL', 0, ON['CALL']), ('THE', 0, ON['THE']), ('NUMBER', 0, ON['NUMBER'])]], ON['OR'] - .04, ON['ON'] - .02, CX, 340, 88, 850),
    page([[('ON', 0, ON['ON']), ('THE', 0, ON['THE2']), ('SCREEN.', 1, ON['SCREEN'] - .02)]], ON['ON'] - .02, T_END - .12, CX, 340, 92, 850),
]
P_STRIKE = PAGES[1]


def _layout(p):
    def mk():
        base = p['base']; out = []; lh = base * 1.14; y0 = -(p['n'] - 1) * lh / 2
        for li in range(p['n']):
            ws = [w for w in p['words'] if w['line'] == li]
            def widths(k): return [font_w(w['text'], int(base * k * (p['ke'] if w['emph'] else 1.0))) for w in ws]
            k = 1.0; tot = sum(widths(1.0)) + base * .34 * (len(ws) - 1)
            if tot > p['maxw']: k = p['maxw'] / tot
            wd = widths(k); tot = sum(wd) + base * k * .34 * (len(ws) - 1); x = p['cx'] - tot / 2
            for w, ww in zip(ws, wd):
                out.append((w, int(base * k * (p['ke'] if w['emph'] else 1.0)), x + ww / 2, p['cy'] + y0 + li * lh)); x += ww + base * k * .34
        return out
    return E.cached(('T_lay', id(p)), mk)


def captions(ctx, t, dy=0.0, alpha=1.0):
    for p in PAGES:
        if not (p['a'] <= t < p['z']): continue
        struck = p is P_STRIKE and t >= T_MORE
        for w, sz, cx, cy in _layout(p):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            a = alpha
            if lt < .05: a *= lt / .05
            if p['z'] - t < .06: a *= max(0, (p['z'] - t) / .06)
            if struck and w['line'] == 0:          # the struck words go grey
                g = clamp((t - T_MORE) / .12)
                img = E.word_img(w['text'], sz, 'dim')[0] if g >= .5 else img
                a *= 1 - .38 * g
                cx += K.shake(t, T_MORE, 9, .07, 23)[0]
            ctx.add('screen', K.scale_im(img, s), cx, cy + dy, alpha=a)


def strike(ctx, t, dy=0.0, alpha=1.0):
    """'ANYMORE.': a glowing gradient bar strikes through 'PICK TWO' (draws 32.73 -> lands 32.87)."""
    if not (T_ANY - .01 <= t < P_STRIKE['z']): return
    L = [(w, sz, cx, cy) for w, sz, cx, cy in _layout(P_STRIKE) if w['line'] == 0]
    x0 = min(cx - font_w(w['text'], sz) / 2 for w, sz, cx, cy in L) - 22
    x1 = max(cx + font_w(w['text'], sz) / 2 for w, sz, cx, cy in L) + 22
    y = L[0][3] + 4 + dy
    k = eo((t - T_ANY) / (T_MORE - T_ANY), 2.4)
    full = x1 - x0
    bar = K.strike_bar(full, 16)                 # bar body starts 40 px into the sprite (padding)
    th = math.radians(4.0)                       # tilts up to the right
    if k < 1: bar = bar.crop((0, 0, max(42, int(40 + full * k) + 40), bar.height))
    a = alpha * clamp((t - T_ANY + .01) / .03)
    if P_STRIKE['z'] - t < .06: a *= max(0, (P_STRIKE['z'] - t) / .06)
    jx, jy = K.shake(t, T_MORE, 9, .07, 23)
    rb = bar.rotate(math.degrees(th), Image.BICUBIC, expand=True)
    r0 = bar.width / 2 - 40                      # sprite centre -> the bar's left end, before rotation
    ctx.add('screen', rb, x0 + r0 * math.cos(th) + jx, y - r0 * math.sin(th) + jy, alpha=a)
    if 0 < k < 1:     # hot spark riding the head
        hx = x0 + full * k * math.cos(th); hy = y - full * k * math.sin(th)
        ctx.add('screen', K.glow_sprite(70, 70, (200, 180, 255), 14), hx, hy, alpha=.9 * a)
        ctx.add('screen', K.glint(46), hx, hy, alpha=a)
    if T_MORE <= t < T_MORE + .25:               # landing glint at the right end
        u = t - T_MORE
        ctx.add('screen', K.glint(70), x0 + full * math.cos(th) + jx, y - full * math.sin(th) + jy, alpha=a * (1 - u / .25))


# ================================================================================================ the triangle
TS = 900
A_AT, A_SC = (353., 740.), .68                 # beside him (labels ~ x 80-615, y 475-1010; CHEAP clear of x 70 even when it jolts)
B_AT, B_SC = (540., 753.), .77                 # centre stage (labels ~ y 447-1061: ~50 px air to PICK above and THREE. below)
E_AT, E_SC = (540., 404.), .44                 # end card: the lit triangle ignites where the logo will be
LOGO_Y, LOGO_SC = 378., .70                    # logo 540 px wide, centre y 378
A_YAW, A_PITCH = -9., 4.


def tri_A(t):
    a = clamp(.20 + (t - T0) / A_DUR)
    d = TRI.drift(t, .6)
    lit = [0., 0., 0.]; pop = [1., 1., 1.]; x = [0., 0., 0.]; edge = [0., 0., 0.]; draw = [1., 1., 1.]
    for i in range(3):          # the orbs arrive glowing (energy of the flight) and cool to grey glass after the lock
        lk = .34 + .12 * i
        lit[i] = .9 if a < lk else .22 + .68 * math.exp(-(a - lk) / .10)
    e, sgn = TRI.EDGE_OF[('good', 'fast')]
    if t >= T_PICK1 - 1 / FPS:
        u = max(0.0, t - T_PICK1)
        Lk = 1 + .65 * math.exp(-u / .11) * min(1, (t - T_PICK1 + 1 / FPS) * FPS)
        lit[0] = lit[2] = Lk; pop[0] = pop[2] = 1 + .22 * bump(u / .24)
    if t >= T_PICK1:
        draw[e] = sgn * eo((t - T_PICK1) / .14, 2.2); edge[e] = 1.0
    else:
        draw[e] = 0.0
    xk = clamp((t - T_TWO) / .18)
    if t > 33.15:                                  # dying-neon flicker before it gets blown off
        j = int(t * FPS)
        fl = 1.0 if hr(j, 4) > .35 else .35 + .3 * hr(j, 5)
        xk *= fl
    x[1] = xk
    lt = t - T0
    yaw = A_YAW * (1 - .3 * eo(lt / 1.0)) + d['yaw']
    pitch = A_PITCH + d['pitch']
    sc = A_SC * (1 + .025 * smooth((t - T_MORE) / .9))
    return TRI.state(assemble=a, lit=tuple(lit), pop=tuple(pop), x=tuple(x), edge=tuple(edge), draw=tuple(draw),
                     flow=(t * .9 if t >= T_PICK1 + .14 else None), yaw=yaw, pitch=pitch, roll=d['roll'], scale=sc)


def tri_B(t):
    u = t - T_PICK + 1 / FPS                      # +1 frame: the PICK frame itself already moves
    k = eo(u / .2, 3)
    d = TRI.drift(t, .45)
    e, sgn = TRI.EDGE_OF[('good', 'fast')]
    lit = [1., 0., 1.]; edge = [0., 0., 0.]; edge[e] = 1.
    draw = [1., 1., 1.]; draw[e] = sgn * 1.0
    xk = 1 - clamp(u / .12)                        # the ✗ is blown off (grows 1.9x + fades)
    pop = [1., 1 + .28 * bump(u / .22), 1.]
    c = clamp((t - T_THREE + 1 / FPS) / .9) if t >= T_THREE else 0.0
    if t >= T_THREE:
        v = t - T_THREE
        pop = [p * (1 + .10 * math.exp(-v / .12)) for p in pop]
    yaw = lerp(A_YAW * .7, 0, k) + d['yaw']; pitch = lerp(A_PITCH, 0, k) + d['pitch']
    sc = lerp(A_SC * 1.02, B_SC, k) * (1 + .035 * smooth((t - T_THREE) / .75))
    return TRI.state(lit=tuple(lit), x=(0., xk, 0.), pop=tuple(pop), edge=tuple(edge), draw=tuple(draw), complete=c,
                     ring=2.5, flow=t * 1.1, yaw=yaw, pitch=pitch, roll=d['roll'], scale=sc), \
        (lerp(A_AT[0], B_AT[0], k), lerp(A_AT[1], B_AT[1], k))


def tri_E(t):
    u = t - T_END
    c = clamp((u + 1 / FPS) / .6)
    lg = clamp((t - T_LOGO) / D_LOGO)
    m = eio(clamp((t - T_LOGO) / .9))
    sc = lerp(E_SC, LOGO_SC, m) * (1 + .38 * (1 - eo((u + 1 / FPS) / .16, 3)))
    at = (CX, lerp(E_AT[1], LOGO_Y, m))
    d = TRI.drift(t, .35 * (1 - clamp(lg * 3)))
    st = TRI.state(complete=c, logo=lg, ring=1.9, flow=t * 1.1, yaw=d['yaw'], pitch=d['pitch'], roll=d['roll'], scale=sc,
                   label=0., alpha=clamp((u + 1 / FPS) / .05))
    return st, at


# ================================================================================================ big type (beat B)
def big(word, t0, y, size, style, t, ctx_add, s_from=1.6, dy=0.0):
    if t < t0 - .005: return
    u = t - t0 + 1 / FPS
    im, m = K.display(word, size, 900, style, glow=.65 if style == 'grad' else .55, shadow=.85, track=int(size * .02))
    for t1, dd in ((T_THREE + .22, .5),):
        sk = (t - t1) / dd
        if 0 < sk < 1: im = K.sheen(im, sk, m, 40, .55)
    s = 1 + (s_from - 1) * (1 - eo(u / .18, 3))
    s *= 1 + .012 * math.sin(u * 4.0)
    a = clamp(u / .06)
    ctx_add(K.scale_im(im, s), 540, y + dy, a)


def rays_img():
    """god rays as an RGB image centred on the hero triangle (full frame)."""
    def mk():
        f = K.rays_field(1150, 28, 3)
        cx, cy = int(B_AT[0]), int(B_AT[1] + .25 * TRI.K_R * TS * B_SC)
        x0, y0 = 1150 - cx, 1150 - cy
        crop = f[y0:y0 + H, x0:x0 + W]
        return Image.fromarray(np.clip(crop, 0, 255).astype(np.uint8))
    return K.C('rays_img', mk)


def add_rgb(fr, img, k):
    if k <= .01: return fr
    if k < .999: img = img.point(lambda v: int(v * k))
    return ImageChops.add(fr.convert('RGB'), img).convert('RGBA')


def premul_shift(layer, dy, blur):
    """RGBA layer moved vertically + vertical motion blur (premultiplied, no dark fringes)."""
    from scipy.ndimage import uniform_filter1d
    a = np.asarray(layer, np.float32).copy()
    a[..., :3] *= a[..., 3:4] / 255
    dy = int(round(dy))
    if dy: a = np.roll(a, dy, 0); a[:dy] = 0 if dy > 0 else a[:dy]
    if dy < 0: a[dy:] = 0
    if blur >= 1.5: a = uniform_filter1d(a, int(blur) + 1, axis=0, mode='constant')
    al = np.maximum(a[..., 3:4], 1e-3)
    a[..., :3] = np.where(a[..., 3:4] > .5, a[..., :3] * 255 / al, 0)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


# ================================================================================================ CTA (beats C + D)
CARD_TOP0, CARD_TOP = 466, 402   # card top: button only (sits lower, balanced) -> with the phone row
BTN_OFF = 118                   # button centre below the card top
ROW_OFF = 100                   # phone row centre above the card bottom
CARD_B0, CARD_B1 = 704, 840     # card bottom: button only -> with the phone row
END_TOP, END_BOT, END_ROW = 712, 950, 790     # end card: the card wraps the phone row + the handles
T_FOLD = T_END - .10            # the button folds away / the card reshapes (his last word ends 37.36)


def card_geom(t):
    """(top, bottom, button alpha, phone row centre y) of the CTA card."""
    top, bot, ba = CARD_TOP0, CARD_B0, 1.0
    if t >= T_OR - .02:
        g = clamp((t - (T_OR - .02)) / .22); gb = K.back(g, 1.3) if g < 1 else 1
        top = lerp(CARD_TOP0, CARD_TOP, eo(g, 3)); bot = lerp(CARD_B0, CARD_B1, gb)
    row = bot - ROW_OFF
    if t >= T_FOLD:
        g = eo((t - T_FOLD) / .34, 3)
        eb = lerp(END_ROW + 92, END_BOT, eo((t - (T_HDL - .06)) / .3, 3))    # grows again when the handles arrive
        top = lerp(top, END_TOP, g); row = lerp(row, END_ROW, g); bot = lerp(bot, eb, g)
        ba = 1 - clamp((t - T_FOLD) / .10)
    return top, bot, ba, row


def card_enter(t):
    """(dy, scale, alpha) of the card on its entrance (whip-pan continuity: it rises in with the shot)."""
    u = t - T_C
    k = eo(u / .2, 3)
    return 260 * (1 - k), .9 + .1 * K.back(clamp(u / .22), 1.6), clamp((u + .04) / .08)


def phone_parts_layout():
    num, nm, badge, hs = K.phone_row()
    gap = 30; pad = int(K.PHONE_SIZE * .42)
    nw = num.width - 2 * pad
    tot = badge.width + gap + nw
    bx = CX - tot / 2 + badge.width / 2
    nx0 = CX - tot / 2 + badge.width + gap - pad          # left edge of the number image
    return num, nm, badge, hs, bx, nx0, nw, pad


def draw_cta(ctx, t):
    top, bot, ba, row = card_geom(t)
    edy, es, ea = card_enter(t) if t < T_C + .3 else (0.0, 1.0, 1.0)
    # ---- card glass + shadow
    h = bot - top; cy = (top + bot) / 2 + edy
    ctx.add('screen', K.card_shadow(h), CX, cy + 14, alpha=ea * .9)
    pan = K.card_panel(h)
    if abs(es - 1) > .004: pan = K.scale_im(pan, es)
    ctx.add('screen', pan, CX, cy, glass=16, alpha=ea)
    # ---- the button
    if ba > .01:
        bim, lmask, imask, (lx0, lx1) = K.button()
        g = clamp((t - (T_OR - .02)) / .22)
        by = lerp(CARD_TOP0, CARD_TOP, eo(g, 3)) + BTN_OFF + edy
        bx = CX
        s = es
        press = 0.0
        if t >= T_TAP - .04:
            press = clamp((t - (T_TAP - .04)) / .04) * math.exp(-max(0.0, t - T_TAP) / .12)    # down ON the tap
            v = t - (T_TAP + .16)
            s *= 1 - .05 * press + (.025 * math.exp(-v / .07) * math.sin(v * 40) if v > 0 else 0)
        if t >= T_FOLD: s *= 1 - .10 * clamp((t - T_FOLD) / .10)
        img = bim
        # label sheen reads "Send message" as he says it
        sk = (t - (T_SEND - .03)) / (T_MSG - T_SEND + .2)
        if 0 < sk < 1: img = K.sheen(img, sk, lmask, 34, .75, .3)
        sk2 = (t - (T_END - .9)) / .7
        if 0 < sk2 < 1: img = K.sheen(img, sk2, np.maximum(lmask, imask), 30, .5, .3)
        gk = .55 + .12 * math.sin(t * 3.1) + .6 * press + .45 * bump(clamp((t - T_SEND) / .3))
        ctx.add('screen', K.button_glow(), bx, by + 10, alpha=ba * ea * min(1, gk))
        if abs(s - 1) > .003: img = K.scale_im(img, s)
        ctx.add('screen', img, bx, by, alpha=ba * ea)
        if press > 0:      # inner light on the press
            ctx.add('screen', K.glow_sprite(int(K.BTN_W * .8), 90, (230, 220, 255), 30), bx, by, alpha=.35 * press * ba)
        # ---- touch indicator (fingertip) + ripples, at the button's right end
        tx, ty = bx + 318, by + 30                # lower-right of the pill, clear of the label (off the end-cap centre: not a toggle knob)
        if T_C + .05 <= t < T_TAP + .55:
            u = t - T_TAP
            if u < 0:   # coming down: big + faint -> fingertip size
                k = clamp((t - (T_C + .05)) / (T_TAP - T_C - .05))
                ctx.add('screen', K.scale_im(K.touch_dot(46), 1.7 - .7 * eo(k)), tx, ty, alpha=.25 + .55 * k)
            else:
                pk = .86 if u < .14 else lerp(.86, 1.05, eo((u - .14) / .1))
                al = 1.0 if u < .16 else max(0.0, 1 - (u - .16) / .22)
                ctx.add('screen', K.scale_im(K.touch_dot(46), pk), tx, ty, alpha=.85 * al)
                r1 = K.ring_sprite(int(40 + 190 * eo(u / .5)), 3.2, .95)
                ctx.add('screen', r1, tx, ty, alpha=max(0, 1 - u / .5))
                if u > .07:
                    r2 = K.ring_sprite(int(30 + 130 * eo((u - .07) / .42)), 2.6, .8)
                    ctx.add('screen', r2, tx, ty, alpha=max(0, 1 - (u - .07) / .42))
                if u < .12: ctx.add('screen', K.glow_sprite(90, 90, (240, 236, 255), 14), tx, ty, alpha=.9 * (1 - u / .12))
        # ---- the sent message bubble
        if T_SEND - .01 <= t < T_OR + .12:
            sb = K.sent_bubble()
            u = t - T_SEND
            land = T_MSG - T_SEND
            k = clamp(u / land)
            x1, y1 = 952 - sb.width / 2 + 6, CARD_TOP0 - 62
            x0_, y0_ = tx - 40, by - 10
            px = lerp(x0_, x1, eo(k, 3)); py = lerp(y0_, y1, eo(k, 2.2)) - 40 * bump(k)
            s = lerp(.25, 1.0, eo(k, 3))
            if t >= T_MSG: s = 1 + .06 * math.exp(-(t - T_MSG) / .07) * math.cos((t - T_MSG) * 38)
            if t >= T_MSG: py += 5 * math.sin((t - T_MSG) * 3.2)           # idle float while it waits
            a = clamp(u / .06)
            if t >= T_OR - .04:
                v = clamp((t - (T_OR - .04)) / .14); py -= 160 * ei(v); a *= 1 - v
            ctx.add('screen', K.scale_im(sb, s), px, py, alpha=a)
            if 0 < k < .9:  # a soft light trail
                ctx.add('screen', K.glow_sprite(90, 60, (170, 150, 255), 18), lerp(x0_, x1, eo(max(0, k - .15), 3)), lerp(y0_, y1, eo(max(0, k - .15), 2.2)), alpha=.5 * (1 - k))
    # ---- phone row
    if t >= T_CALL - .03:
        num, nm, badge, hs, bxx, nx0, nw, pad = phone_parts_layout()
        ry = row + edy
        u = t - T_CALL
        # badge pops + rings
        bs = .4 + .6 * K.back(clamp((u + .03) / .2), 2.2) if u < .3 else 1.0
        bs *= 1 + .07 * bump(clamp((t - T_NUM) / .2))
        ctx.add('screen', K.glow_sprite(150, 150, (120, 90, 255), 24), bxx, ry + 6, alpha=.7 * clamp((u + .03) / .15))
        ctx.add('screen', K.scale_im(badge, bs), bxx, ry, alpha=clamp((u + .03) / .08))
        ring = math.sin(u * 2 * math.pi * 9) * 16 * math.exp(-max(0, u - .05) / .22) if u > 0 else 0
        if t >= T_END - .1: ring += math.sin((t - T_END) * 2 * math.pi * 9) * 10 * math.exp(-(t - T_END) / .2) * (t > T_END)
        ctx.add('screen', K.scale_im(hs, bs).rotate(ring, Image.BICUBIC, expand=True), bxx, ry, alpha=clamp((u + .03) / .08))
        if 0 < u < .55:   # ring waves off the handset
            for i in range(2):
                v = (u - .08 * i) / .45
                if 0 < v < 1:
                    ctx.add('screen', K.ring_sprite(int(70 + 60 * eo(v)), 2.4, .8), bxx, ry, alpha=(1 - v) * .8)
        # number: light-wipe in, sheens, pop on NUMBER
        img = num
        for t0, dd, st in ((T_NUM - .03, .42, .7), (T_END + .1, .6, .55), (T_SWEEP + .2, .7, .6)):
            sk = (t - t0) / dd
            if 0 < sk < 1: img = K.sheen(img, sk, nm, 30, st)
        img = K.wipe(img, (t - (T_CALL + .01)) / .3, nm)
        if img is not None:
            ns = 1 + .06 * bump(clamp((t - T_NUM) / .22))
            if abs(ns - 1) > .003: img = K.scale_im(img, ns)
            ctx.add('screen', img, nx0 + num.width / 2, ry - 2)
        # underline + viewfinder corners on SCREEN
        if t >= T_SCREEN - .02:
            v = t - (T_SCREEN - .02)
            k = eo(v / .24, 3)
            uw = nw * k
            if uw > 4:
                ul = K.underline(uw, 8)
                ctx.add('screen', ul, nx0 + pad + uw / 2, ry + 58)
                if k < 1: ctx.add('screen', K.glow_sprite(50, 22, (220, 210, 255), 7), nx0 + pad + uw, ry + 60, alpha=.95)
            ba2 = clamp(v / .06) * (1 - clamp((t - T_FOLD) / .12))
            if ba2 > .01:
                sk = 1.35 - .35 * eo(v / .14, 3)
                bx0, bx1 = nx0 + pad - 34, nx0 + pad + nw + 34
                by0, by1 = ry - 74, ry + 76
                cxm, cym = (bx0 + bx1) / 2, (by0 + by1) / 2
                br = K.bracket(46, 7)
                for fx, fy, rot in ((-1, -1, 0), (1, -1, -90), (1, 1, 180), (-1, 1, 90)):
                    px = cxm + (bx1 - cxm) * fx * sk; py = cym + (by1 - cym) * fy * sk
                    im = br.rotate(rot, Image.BICUBIC) if rot else br
                    ctx.add('screen', im, px - fx * 23 + 0 * fx, py - fy * 23, alpha=ba2)


def draw_handles(ctx, t):
    if t < T_HDL - .01: return
    k = expo((t - T_HDL) / .45)
    ctx.add('screen', divider(), CX, END_ROW + 64, alpha=clamp(k * 2))
    ctx.add('screen', handles(), CX, END_ROW + 110 + 16 * (1 - k), alpha=clamp(k * 2.2))


def divider():
    def mk():
        w = 700; a = np.clip(1 - np.abs(np.linspace(-1, 1, w, dtype=np.float32)) ** 2, 0, 1) * .28
        im = Image.new('RGBA', (w, 2), (255, 255, 255, 0)); im.putalpha(Image.fromarray(np.repeat((a * 255).astype(np.uint8)[None, :], 2, 0)))
        return im
    return K.C('divider', mk)


# ================================================================================================ end card text
def end_text(ctx, t):
    # "Pick three."
    if t >= T_PT - .01:
        k = expo((t - T_PT) / .45)
        im, m = K.display('Pick three.', 128, 800, 'grad', glow=.6, shadow=.85)
        for t0, dd in ((T_PT + .3, .55), (T_SWEEP, .7)):
            sk = (t - t0) / dd
            if 0 < sk < 1: im = K.sheen(im, sk, m, 34, .6)
        ctx.add('screen', im, CX, 556 + 40 * (1 - k), alpha=clamp(k * 2.2))
    if t >= T_TAG - .01:
        k = expo((t - T_TAG) / .45)
        ctx.add('screen', tagline(), CX, 648 + 26 * (1 - k), alpha=clamp(k * 2.2))


def tagline():
    def mk():
        parts = [('Fast.', 500, E.WHITE), ('Affordable.', 500, E.WHITE), ('Actually good.', 800, None)]
        size = 52; gap = 24                  # 52 px: still reads at arm's length on a phone (was 48)
        fonts = [E.font(size, wg) for _, wg, _ in parts]
        ws = [f.getlength(s) for (s, _, _), f in zip(parts, fonts)]
        _, tt, _, bb = fonts[0].getbbox('FAgy')
        w = int(sum(ws) + gap * 2) + 60; h = int(bb - tt) + 50
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 30
        mall = Image.new('L', (w, h))
        layers = []
        for (s, wg, col), f, ww in zip(parts, fonts, ws):
            m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((x, 25 - tt), s, font=f, fill=255)
            mall = ImageChops.lighter(mall, m); layers.append((m, col)); x += ww + gap
        sh = Image.new('RGBA', (w, h), (4, 2, 12, 0)); sh.putalpha(mall.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * .85)))
        out.alpha_composite(sh, (0, 3))
        for m, col in layers:
            if col is None:
                g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m); out.alpha_composite(g)
            else:
                c = Image.new('RGBA', (w, h), col + (0,)); c.putalpha(m.point(lambda v: int(v * .94))); out.alpha_composite(c)
        return out
    return K.C('tagline', mk)


def handles():
    def mk():
        im, _ = K.display('slumarc.com  ·  @lumarc_studio', 42, 500, (214, 211, 236), glow=0, shadow=.8)
        return im
    return K.C('handles', mk)


BOKEH = [(150, 360, 40, .16, 6, -9, (70, 100, 255)), (930, 300, 26, .18, -5, -7, (150, 80, 255)), (960, 1120, 52, .13, -4, -6, (110, 80, 255)),
         (110, 1060, 20, .22, 7, -10, (120, 130, 255)), (660, 200, 13, .22, 3, -8, (170, 140, 255)), (1015, 720, 30, .14, -6, -9, (140, 70, 255)),
         (70, 760, 24, .15, 4, -12, (90, 110, 255)), (420, 150, 20, .17, -3, -6, (160, 120, 255))]


# ================================================================================================ beats
def beat_a(ctx, t):
    lt = t - T0
    ctx.bg_img = K.bg_soft(); ctx.avatar.update(x=265.)
    z = 1.30 - .12 * eo(lt / .45, 3) + .03 * smooth((lt - .45) / 1.4)
    if t >= T_MORE: z += .02 * math.exp(-(t - T_MORE) / .1) * (t - T_MORE < .5)
    ctx.cam.update(z=z, x=600., y=800., rot=math.radians(1.2 * (1 - eo(lt / .45, 3))))
    st = tri_A(t)
    jx, jy = K.shake(t, T_MORE, 7, .07, 21, 1.)
    ax, ay = A_AT[0] + jx, A_AT[1] + jy
    ctx.wrap = lambda fr, st=st: TRI.paste(fr, st, TS, ax, ay, frost=9)
    ctx.post['bright'] = 1 + .16 * math.exp(-lt / .05)        # the cut-in: a short exposure kick (no grey veil)
    feather_a(ctx, t)
    captions(ctx, t); strike(ctx, t)


def feather_a(ctx, t):
    """he sits right (x +265): the take's LEFT frame edge lands at screen x ~195 and slices his hoodie + gesturing hand
    with a hard vertical line from y ~1500 down.  Feather it into the studio (wide, soft) + darken the frame floor."""
    edge_feather(ctx, t, sides=(-1,), y0=1150, width=170, ramp=200)
    ctx.add('screen', K.floor_shade(), 540, 960, alpha=.8)


def beat_b(ctx, t):
    u = t - T_PICK
    ctx.bg_img = K.bg_soft(); ctx.avatar.update(x=265.)
    feather_a(ctx, t)
    lt = t - T0
    z = 1.30 - .12 + .03 * smooth((lt - .45) / 1.4) + .16 * eo(u / .22, 3) + .05 * smooth((t - T_THREE) / .8)
    sx, sy = K.shake(t, T_THREE, 16, .09, 17)
    ctx.cam.update(z=z, x=600., y=800., dx=sx * .5, dy=sy * .5)
    kf = clamp((u + 1 / FPS) / .1)
    st, at = tri_B(t)
    # whip-pan out (last 2 frames before the jump)
    wk = clamp((t - (T_C - 2.5 / FPS)) / (2.5 / FPS))
    wdy, wbl = -520 * wk ** 2, 220 * wk ** 1.5
    tsx, tsy = K.shake(t, T_THREE, 12, .08, 19, 2.)
    def wrap(fr):
        bg = K.frost(fr, kf)
        if t >= T_THREE and wk <= 0:          # god rays: bang on THREE, then a slow breath
            v = t - T_THREE
            rk = 1.0 * math.exp(-v / .22) + .32 * clamp(v / .3) * (1 + .15 * math.sin(v * 5))
            bg = add_rgb(bg, rays_img(), rk)
        hero = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        hero.alpha_composite(TRI.render(st, TS, canvas=(W, H), at=(at[0] + tsx, at[1] + tsy)))
        def add(im, x, y, a): K.paste(hero, im, x, y, alpha=a)
        big('PICK', T_PICK, 344, 150, 'grad', t, add, 1.55, tsy * .6)     # same voice as THREE. (never reads 'PICK FAST')
        big('THREE.', T_THREE, 1172, 168, 'grad', t, add, 1.9, tsy * .6)
        if wk > 0:
            hero = premul_shift(hero, wdy, wbl); bg = K.shift_v(bg, wdy * .5, wbl * .6)
        bg.alpha_composite(hero)
        return bg
    ctx.wrap = wrap
    # the A captions flick out on PICK
    if u < .04:
        a = .3 * (1 - clamp(u / .04))
        captions(ctx, t, dy=-60 * eo((u + 1 / FPS) / .07), alpha=a); strike(ctx, t, dy=-60 * eo((u + 1 / FPS) / .07), alpha=a)
    P = ctx.post
    if t >= T_THREE:
        v = t - T_THREE
        P['flash'] = .16 * math.exp(-v / .04); P['flash_col'] = (190, 170, 255)
        P['rgb'] = 7 * clamp(1 - v / .1)
        P['bright'] = 1 + .55 * math.exp(-v / .09)
    elif u < .1:
        P['zoom_blur'] = .5 * (1 - u / .1) if u > 0 else 0
    if T_THREE - .1 <= t < T_THREE:
        P['zoom_blur'] = .35 * ei((t - (T_THREE - .1)) / .1)
    P['vignette'] = .38


def world_c(ctx, t):
    """the CTA shot: he is framed lower + smaller under the glass card; the studio in soft focus."""
    endk = eio(clamp((t - T_END) / .6))
    ctx.avatar.update(s=lerp(.76, .72, endk), y=lerp(0., 50., endk))
    z = 1.0 + .03 * smooth((t - T_C) / 3.0) + .02 * smooth((t - T_END) / 3.0)
    ctx.cam.update(z=z, x=540., y=1120.)
    if t < T_END:
        ctx.bg_img = K.bg_soft()
    else:
        u = t - T_END
        bp = K.brand_plate()
        ctx.bg_img = Image.blend(K.bg_soft(), bp, clamp(u / .3)) if u < .3 else bp
        ctx.bg_z = 1 + .05 * smooth(u / 3.1)
        for i, (x, y, r, a, vx, vy, col) in enumerate(BOKEH):
            px = x + vx * u + 10 * math.sin(u * .6 + i); py = y + vy * u
            tw = .8 + .2 * math.sin(t * 1.3 + i * 1.7)
            ctx.add('behind', K.bokeh(r, col), px, py, alpha=min(1, a * clamp(u / .6) * tw * 2.0))
    edge_feather(ctx, t)
    ctx.add('screen', K.floor_shade(), 540, 960)


def edge_feather(ctx, t, sides=(-1, 1), y0=1100, width=96, ramp=220):
    """the take's left/right frame edges cut his hands/hoodie with a hard vertical line wherever the take does not
    fill the frame (scaled down, or shifted sideways): paint the background back over the last `width` px inside each
    visible edge with a soft ramp (world layer -> rides the camera with him).  Uses the avatar's x offset too."""
    s, ax_ = round(ctx.avatar['s'], 3), round(ctx.avatar['x'], 1)
    bg = ctx.bg_img if ctx.bg_img is not None else E.studio()
    for side in sides:
        ex = 540 + side * 540 * s + ax_
        x0 = int(ex - 14) if side < 0 else int(ex - width); x1 = x0 + width + 14
        x0c, x1c = max(0, x0), min(W, x1)
        if x1c - x0c < 4: continue                    # that edge is off the world: nothing to hide
        def mk(x0=x0, x1=x1, side=side, ex=ex):
            xs = np.arange(x0, x1, dtype=np.float32) + .5
            d = (xs - ex) * -side                      # >0 inside the take
            ax = np.clip(1 - (d - 4) / (width - 10), 0, 1) ** 1.6
            ys = np.arange(y0, H, dtype=np.float32)
            ay = np.clip((ys - y0) / ramp, 0, 1)
            return (ay[:, None] * ax[None, :] * 255).astype(np.uint8)
        a = E.cached(('T', 'feather', side, s, ax_, y0, width, ramp), mk)[:, x0c - x0:x1c - x0]
        strip = bg.crop((x0c, y0, x1c, H)).convert('RGBA'); strip.putalpha(Image.fromarray(np.ascontiguousarray(a)))
        ctx.add('front', strip, x0c, y0, center=False)


def beat_c(ctx, t):
    world_c(ctx, t)
    u = t - T_C
    if u < .15:     # whip-pan in: the shot rises in from below with motion blur
        dy, bl = 280 * (1 - eo(u / .15, 3)), 130 * (1 - eo(u / .15, 2))
        ctx.wrap = lambda fr: K.shift_v(fr, dy, bl)
        ctx.post['flash'] = .10 * (1 - clamp(u / .1)); ctx.post['flash_col'] = (210, 200, 255)
    draw_cta(ctx, t)
    captions(ctx, t)
    ctx.post['vignette'] = .34


def beat_d(ctx, t):
    world_c(ctx, t)
    u = t - T_END
    P = ctx.post
    P['flash'] = .10 * math.exp(-u / .05); P['flash_col'] = (180, 160, 255)
    P['bright'] = 1 + .45 * math.exp(-u / .12)
    P['rgb'] = 5 * clamp(1 - u / .1)
    P['vignette'] = .34
    draw_cta(ctx, t)
    draw_handles(ctx, t)
    st, at = tri_E(t)
    ctx.add('screen', TRI.render(st, TS, canvas=(W, H), at=at), W / 2, H / 2)
    end_text(ctx, t)
    if u < .06: captions(ctx, t)


def draw(ctx, lt, t):
    ctx.captions = False
    if t < T_PICK: beat_a(ctx, t)
    elif t < T_C: beat_b(ctx, t)
    elif t < T_END: beat_c(ctx, t)
    else: beat_d(ctx, t)
