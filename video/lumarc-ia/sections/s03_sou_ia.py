"""s03 — SOU IA (15.72–22.20).  "Ah, e pode me desconsiderar nesse vídeo… eu claramente sou IA, né? Só tô aqui pra
prender a sua atenção por alguns segundos."   Deadpan, self-aware comedy.

15.72  JUMP -> confessional snap-in: tight close-up (z 1.62 -> 1.46, 3-frame zoom-blur settle), 'zoom'.
16.64  "DESCONSIDERAR" — his picture shrinks into a desktop WINDOW ("apresentador.mov", glass title bar, traffic
       lights, an "Ignorar" button with an eye-slash) floating over a blurred copy of itself.  A cursor flies in and
       CLICKS "Ignorar" on the stressed "-RAR" (17.10): the window starts to minimize (genie squash towards the
       dock)… stalls… and SPRINGS back (17.33).  Three frantic clicks (17.58/17.66/17.74) -> the window shakes "no".
       He just keeps talking.
17.80  the window maximizes back into a new framing (medium close-up z 1.30) and the cursor leaves.
18.25  "CLARAMENTE" — official AI face scan: tracking brackets snap onto his face, a glowing scan line sweeps
       forehead -> chin, landmark dots + a faint triangulated mesh appear behind it, tag "ANALISANDO…".
19.10  "IA" — tiny glitch; the tag flips to "AVATAR · 100% IA" (glass, LUMARC gradient), mesh turns violet.
19.33  "NÉ?" — the check mark draws in ('ding') + a deadpan sitcom push-in on his face.
19.60  scan UI collapses; camera eases out to a medium shot.
20.19  "AQUI": an empty glass "attention bar" slides in under his chin; 20.24 an open padlock falls in from above the
       frame (gravity + vertical motion smear)…
20.51  "PRENDER" — the shackle SLAMS shut on the bar (CLUNK 'lock', camera jolt + punch-in, flash ring).
20.78  "A SUA ATENÇÃO" types into the bar (kinetic type = the caption) and the bar fills with the LUMARC gradient.
21.33  "POR ALGUNS SEGUNDOS." — a stopwatch (with a remaining-time ring) replaces the eye icon and the fill counts down
       in five steps, one per clock tick (21.44/21.62/21.80/21.97/22.10); the hand jumps and the padlock rattles on each;
22.10  it hits zero -> the padlock pops open ('click') -> hard cut to s04.
Captions: own word pops (engine look) on onsets measured on src/tight16k.raw (spectrogram + 10 ms envelope).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import Delaunay
import engine as E
from sections import _B_kit as K

START, END = E.span(5, 7)                    # 15.72 – 22.20
T6, T7 = E.TL[6]['t0'], E.TL[7]['t0']        # 17.84 (no jump), 19.60 (no jump)
W, H = E.W, E.H
clamp, eout, ein, back, lerp, smooth, expo = K.clamp, K.eout, K.ein, K.back, K.lerp, K.smooth, K.expo

# word onsets measured on src/tight16k.raw (5 ms spectrogram + low/high band envelopes, see out/B/spec5-7.png)
O = dict(AH=15.81, E=16.19, PODE=16.30, ME=16.52, DES=16.64, RAR=17.10, NESSE=17.22, VIDEO=17.40, VIDEO_END=17.72,
         EU=18.02, CLARAMENTE=18.25, SOU=18.88, IA=19.10, NE=19.33, NE_END=19.47,
         SO=19.84, TO=20.03, AQUI=20.19, PRA=20.35, PRENDER=20.51, A=20.78, SUA=20.84, ATENCAO=20.97,
         POR=21.33, ALGUNS=21.45, SEGUNDOS=21.62, END=22.08)

T_CLICK = O['RAR']                     # the click on "Ignorar"
T_GENIE = T_CLICK + .02                 # minimize attempt starts
T_SPRING = 17.31                        # …and springs back
T_CLICKS = (17.58, 17.66, 17.74)        # frantic clicks
T_MAX = 17.80                           # window maximizes
T_LOCK_IN = O['AQUI']                   # attention bar slides in (on 'aqui')
T_DROP = 20.24                          # padlock falls in from above the frame…
T_LAND = 20.46                          # …and lands on the bar
DROP_H = 1520.                          # fall height (px): starts fully off-frame
T_TICKS = (21.44, 21.62, 21.80, 21.97)  # countdown ticks (clock cues)
T_ZERO = 22.10                          # countdown hits zero -> lock pops open

CUES = [
    (START, 'zoom', {'gain': -9}),                      # confessional snap-in
    (O['DES'], 'swipe', {'gain': -9}),                  # frame shrinks into a window
    (O['DES'] + .08, 'pop', {'gain': -16}),             # title bar UI
    (16.80, 'flick', {'gain': -16, 'pan': .4}),         # cursor flies in
    (T_CLICK, 'click', {'gain': -2}),                   # click "Ignorar"
    (T_GENIE, 'whoosh', {'gain': -15}),                 # minimize attempt
    (T_SPRING, 'pop', {'gain': -7}),                    # …springs back
    (T_CLICKS[0], 'click', {'gain': -5}),
    (T_CLICKS[1], 'click', {'gain': -6}),
    (T_CLICKS[2], 'click', {'gain': -6}),
    (T_CLICKS[0] + .03, 'knock', {'gain': -13}),         # the window shakes "no"
    (T_MAX, 'whoosh', {'gain': -12}),                   # window maximizes
    (O['CLARAMENTE'], 'scan', {'dur': .7, 'gain': -6}),
    (O['CLARAMENTE'] + .02, 'tick', {'gain': -12}),     # brackets lock on
    (O['IA'], 'glitch', {'gain': -8}),
    (O['IA'] + .01, 'pop', {'gain': -9}),               # "AVATAR · 100% IA"
    (O['NE'] + .03, 'ding', {'note': 'E6', 'gain': -10}),
    (T7, 'swipe', {'gain': -16}),                       # scan UI collapses, camera eases out
    (T_LOCK_IN, 'swipe', {'gain': -16}),                # glass bar slides in
    (T_DROP + .05, 'whoosh', {'gain': -17}),            # padlock falls into frame
    (O['PRENDER'], 'lock', {'gain': -1}),               # CLUNK
    (O['PRENDER'] + .01, 'thud', {'gain': -10}),
    (O['SUA'] + .04, 'swoosh_up', {'gain': -15}),       # the bar fills
    (O['POR'] + .02, 'pop', {'gain': -14}),             # stopwatch
] + [(tk, 'clock', {'i': i, 'gain': -11}) for i, tk in enumerate(T_TICKS)] + [
    (T_ZERO, 'click', {'gain': -6}),                    # lock pops open
]

# ---------------------------------------------------------------- captions (measured onsets)
PAGES = [
    (O['AH'] - .04, O['ME'] - .02, [('AH,', O['AH'], False), ('E', O['E'], False), ('PODE', O['PODE'], False)]),
    (O['ME'] - .02, O['NESSE'] - .02, [('ME', O['ME'], False), ('DESCONSIDERAR', O['DES'], True)]),
    (O['NESSE'] - .02, T_MAX + .06, [('NESSE', O['NESSE'], False), ('VÍDEO…', O['VIDEO'], False)]),
    (O['EU'] - .04, O['SOU'] - .02, [('EU', O['EU'], False), ('CLARAMENTE', O['CLARAMENTE'], False)]),
    (O['SOU'] - .02, T7 + .02, [('SOU', O['SOU'], False), ('IA,', O['IA'], True), ('NÉ?', O['NE'], False)]),
    (O['SO'] - .04, O['PRENDER'] - .02, [('SÓ', O['SO'], False), ('TÔ', O['TO'], False), ('AQUI', O['AQUI'], False), ('PRA', O['PRA'], False)]),
    (O['PRENDER'] - .02, O['A'] - .01, [('PRENDER', O['PRENDER'], True)]),
    (O['POR'] - .02, END, [('POR', O['POR'], False), ('ALGUNS', O['ALGUNS'], False), ('SEGUNDOS.', O['SEGUNDOS'], False)]),
]


# ================================================================ the window gag
WIN_S = .76                    # window content scale
TB = 86                        # title bar height (px)
BTN_W = 236                    # 'Ignorar' button width


def _eye_slash(d=30, col=(250, 249, 246)):
    S = 4; D = d * S; m = Image.new('L', (D, D)); dr = ImageDraw.Draw(m)
    dr.ellipse((D * .06, D * .26, D * .94, D * .74), outline=255, width=int(2.4 * S))
    dr.ellipse((D * .36, D * .36, D * .64, D * .64), fill=255)
    dr.line((D * .14, D * .86, D * .86, D * .14), fill=0, width=int(6 * S))
    dr.line((D * .14, D * .86, D * .86, D * .14), fill=255, width=int(2.6 * S))
    m = m.resize((d, d), Image.LANCZOS); im = Image.new('RGBA', (d, d), col + (0,)); im.putalpha(m); return im


def button_img(state):
    """'Ignorar' pill: state 0 normal, 1 hover, 2 pressed."""
    def mk():
        w, h = BTN_W, 64
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); m = Image.new('L', (w, h))
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
        if state == 0: body = Image.new('RGBA', (w, h), (255, 255, 255, 0)); a = .14
        else:
            body = E.gradient(w, h, E.GRAD).convert('RGBA'); a = .95 if state == 1 else .75
        body.putalpha(m.point(lambda v: int(v * a))); im.alpha_composite(body)
        b = Image.new('L', (w, h)); ImageDraw.Draw(b).rounded_rectangle((1, 1, w - 2, h - 2), h // 2 - 1, outline=255, width=2)
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [b.point(lambda v: int(v * .35))]))
        im.alpha_composite(_eye_slash(36), (22, 14))
        tx = K.text_img('Ignorar', 36, 600, E.WHITE); im.alpha_composite(tx, (68, (h - tx.height) // 2))
        return im
    return K.C(('btn', state), mk)


def titlebar(w):
    def mk():
        im = Image.new('RGBA', (w, TB), (0, 0, 0, 0)); m = Image.new('L', (w, TB + 40))
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, TB + 39), 34, fill=255); m = m.crop((0, 0, w, TB))
        body = Image.new('RGBA', (w, TB), (22, 22, 32, 0)); body.putalpha(m.point(lambda v: int(v * .94))); im.alpha_composite(body)
        g = np.linspace(1, 0, TB, dtype=np.float32)[:, None] ** 2 * .10
        sh = Image.fromarray((np.repeat(g, w, 1) * 255).astype(np.uint8)); sh = Image.composite(sh, Image.new('L', (w, TB)), m)
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, TB), 255)] * 3 + [sh]))
        d = ImageDraw.Draw(im)
        for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
            cx = 38 + i * 34; d.ellipse((cx - 10, TB / 2 - 10, cx + 10, TB / 2 + 10), fill=c + (255,))
        tt = K.text_img('apresentador.mov', 34, 500, (200, 200, 214))
        cx_ = (126 + w - 22 - BTN_W) / 2                       # centred between the traffic lights and the button
        im.alpha_composite(tt, (int(cx_ - tt.width / 2), int(TB / 2 - tt.height / 2)))
        d.line((0, TB - 1, w, TB - 1), fill=(255, 255, 255, 38))
        return im
    return K.C(('tbar', w), mk)


def desktop():
    """dark LUMARC desktop: night base + a soft violet glow behind the window."""
    def mk():
        y, x = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        r = np.sqrt(((x - 540) / 700) ** 2 + ((y - 1000) / 1000) ** 2)
        g = np.exp(-r ** 2 * 1.6)[..., None] * np.array([46, 30, 96], np.float32)
        base = np.array([9, 9, 15], np.float32) + g
        return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return K.C('desktop', mk)


def win_border(w, h, r):
    def mk():
        b = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(b).rounded_rectangle((1, 1, w * 2 - 2, h * 2 - 2), r * 2, outline=255, width=4)
        b = b.resize((w, h), Image.LANCZOS)
        return Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [b.point(lambda v: int(v * .30))])
    return K.C(('wborder', w, h, r), mk)


def round_mask(w, h, r):
    def mk():
        m = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), r * 2, fill=255)
        return m.resize((w, h), Image.LANCZOS)
    return K.C(('rmask', w, h, r), mk)


def win_scale(t):
    k = expo((t - O['DES']) / .30)
    kx = expo((t - T_MAX) / .17) if t >= T_MAX else 0.
    return lerp(lerp(1.0, WIN_S, k), 1.0, kx), k * (1 - kx)


def genie_k(t):
    """minimize amount: grows (ease-in), stalls, springs back with overshoot (negative = stretch up)."""
    if t < T_GENIE: return 0.
    if t < T_SPRING: return .62 * ein((t - T_GENIE) / (T_SPRING - T_GENIE)) ** .8
    u = (t - T_SPRING) / .30
    if u >= 1: return 0.
    return .62 * (1 - back(u, 3.2))


def no_shake(t):
    t0 = T_CLICKS[0] + .02
    k = (t - t0) / .40
    if not 0 <= k < 1: return 0.
    return 44 * math.sin(k * math.pi * 7) * (1 - k) ** 1.3


def win_geom(t):
    """-> (s, k_ui, x0, y0 (content top-left), cw, ch, title top)"""
    s, kui = win_scale(t)
    cw, ch = int(W * s), int(H * s)
    cyc = lerp(960, 1052, kui)
    x0 = 540 - cw / 2 + no_shake(t); y0 = cyc - ch / 2
    return s, kui, x0, y0, cw, ch, y0 - TB * kui


def button_pos(t):
    s, kui, x0, y0, cw, ch, ty = win_geom(t)
    return x0 + cw - 22 - BTN_W / 2, ty + TB / 2


def window_wrap(t):
    def wrap(fr):
        s, kui, x0, y0, cw, ch, ty = win_geom(t)
        if kui < .002: return fr
        # desktop: blurred, darkened copy of the frame itself
        bg = fr.convert('RGB').reduce(4).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)
        bg = Image.blend(bg, desktop(), .62 * kui).convert('RGBA')
        tb = int(round(TB * kui))
        win = Image.new('RGBA', (cw, ch + tb), (0, 0, 0, 0))
        win.paste(fr.convert('RGB').resize((cw, ch), Image.BILINEAR), (0, tb))
        if tb > 0:
            bar = titlebar(cw).crop((0, TB - tb, cw, TB)); win.alpha_composite(bar, (0, 0))
            st = 2 if any(0 <= t - c < .09 for c in (T_CLICK,) + T_CLICKS) else (1 if t >= 17.03 else 0)
            b = button_img(st)
            if st == 2: b = K.scale_im(b, .95)
            bx, by = cw - 22 - BTN_W / 2, tb - TB / 2
            win.alpha_composite(b, (int(bx - b.width / 2), int(by - b.height / 2)))
        r = int(lerp(0, 34, kui))
        if r > 1:
            m = round_mask(cw, ch + tb, r); win.putalpha(m)
            if kui > .3: win.alpha_composite(K.fade(win_border(cw, ch + tb, r), (kui - .3) / .7))
        # genie (minimize attempt) — horizontal strips squeezed towards the dock (bottom centre)
        gk = genie_k(t)
        X0, Y0 = x0, ty
        if abs(gk) > .003:
            hw = win.height; n = 120; out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            dock_y = 1890.; top1 = lerp(Y0, Y0 + .50 * (dock_y - Y0), gk); bot1 = lerp(Y0 + hw, dock_y, gk * .9)
            for i in range(n):
                a0, a1 = int(hw * i / n), int(hw * (i + 1) / n)
                v = (i + .5) / n; f = smooth(v) ** 1.4
                wv = cw * max(.05, 1 - gk * .92 * f)
                ya = lerp(top1, bot1, i / n); yb = lerp(top1, bot1, (i + 1) / n)
                cx = 540 + no_shake(t) * (1 - f)
                hh = max(1, int(round(yb - ya)) + 1)
                strip = win.crop((0, a0, cw, a1)).resize((max(1, int(wv)), hh), Image.BILINEAR)
                out.alpha_composite(strip, (int(cx - wv / 2), int(ya)))
            sh = K.soft_shadow(int(cw * (1 - gk * .5)), int(bot1 - top1), 34, 34, .55)
            bg.alpha_composite(sh, (int(540 - sh.width / 2), int(top1 - 60 + 22)))
            bg.alpha_composite(out)
        else:
            sh = K.soft_shadow(cw, win.height, 34, 34, .6 * kui)
            bg.alpha_composite(sh, (int(X0 + cw / 2 - sh.width / 2), int(Y0 - 60 + 24)))
            bg.alpha_composite(win, (int(X0), int(Y0)))
        return bg
    return wrap


def cursor_xy(t):
    """cursor hotspot position (screen) or None."""
    bx, by = button_pos(t)
    tgt = (bx + 18, by + 6)
    t_in, t_arr = 16.78, 17.03
    if t < t_in: return None
    if t < t_arr:
        u = (t - t_in) / (t_arr - t_in); e = eout(u)
        p0 = (1160., 1560.); c = (980., 700.)
        x = (1 - e) ** 2 * p0[0] + 2 * (1 - e) * e * c[0] + e * e * tgt[0]
        y = (1 - e) ** 2 * p0[1] + 2 * (1 - e) * e * c[1] + e * e * tgt[1]
        return x, y
    if t < T_MAX:
        j = .0
        if t > T_CLICKS[0] - .1: j = 3 * math.sin(t * 70)        # frantic hand
        return tgt[0] + j, tgt[1] + j * .5
    u = (t - T_MAX) / .22
    if u >= 1: return None
    e = ein(u); return tgt[0] + 520 * e, tgt[1] + 900 * e


def draw_cursor(ctx, t):
    p = cursor_xy(t)
    if p is None: return
    im, pad = K.cursor_img(74)
    pressed = any(0 <= t - c < .08 for c in (T_CLICK,) + T_CLICKS)
    s = .86 if pressed else 1.0
    if s != 1: im = K.scale_im(im, s); pad = pad * s
    # motion trail while flying in
    if 16.78 <= t < 17.0:
        q = cursor_xy(t - 1 / 60)
        if q is not None:
            for g in range(7, 0, -1):                             # smooth smear over ~1.5 frames of travel
                f = g / 7 * 3.0
                ctx.add('screen', im, p[0] + (q[0] - p[0]) * f - pad, p[1] + (q[1] - p[1]) * f - pad, center=False, alpha=.20 * (1 - g / 8))
    ctx.add('screen', im, p[0] - pad, p[1] - pad, center=False)
    # click ripples
    for c in (T_CLICK,) + T_CLICKS:
        u = (t - c) / .30
        if 0 <= u < 1:
            d = int(30 + 90 * eout(u)); rg = K.ring(d, 3, (255, 255, 255), .85 * (1 - u))
            ctx.add('screen', rg, p[0], p[1])


# ================================================================ the AI face scan
# landmarks: offsets from (face centre x, head top) in take pixels (measured on the keyed plate at 19.1 s)
LM = [(-150, 190), (155, 190), (-110, 118), (-40, 104), (40, 104), (115, 118),                               # temples, forehead
      (-150, 247), (-146, 297), (-138, 357), (-122, 417), (-98, 465), (-65, 502), (-30, 522), (0, 528),        # jaw L
      (32, 522), (68, 502), (102, 465), (128, 417), (143, 357), (151, 297), (155, 247),                         # jaw R
      (-120, 228), (-92, 214), (-62, 210), (-32, 216), (32, 216), (62, 210), (94, 214), (122, 228),             # brows
      (-95, 251), (-66, 240), (-38, 252), (-66, 262), (38, 252), (68, 240), (98, 251), (68, 262),               # eyes
      (0, 258), (2, 292), (4, 326), (-28, 334), (34, 334), (3, 346),                                            # nose
      (-56, 412), (-25, 397), (0, 401), (28, 397), (60, 412), (30, 434), (0, 441), (-28, 434),                  # mouth
      (-100, 330), (105, 330), (-80, 390), (85, 390)]                                                           # cheeks
TRI = Delaunay(np.array(LM, np.float32)).simplices
EDGES = sorted({tuple(sorted((int(a), int(b)))) for s_ in TRI for a, b in ((s_[0], s_[1]), (s_[1], s_[2]), (s_[0], s_[2]))})
BOX = (-188, 92, 192, 552)          # face box (offsets)
SCAN0, SCAN1 = O['CLARAMENTE'] + .03, O['SOU'] - .02    # scan line sweep


def tag_img(stage, kcheck=0.):
    """the tag above the face box: stage 0 'ANALISANDO…', 1 'AVATAR · 100% IA' + check (kcheck 0..1 drawn)."""
    def mk(stage=stage):
        if stage == 0:
            tx = K.text_img('ANALISANDO…', 35, 600, (226, 228, 240), track=4); w = tx.width + 76; h = 70
            im = K.dark_glass(w, h, 18, .60, .40).copy()
            d = ImageDraw.Draw(im); d.ellipse((22, h / 2 - 7, 36, h / 2 + 7), fill=(120, 200, 255, 255))
            im.alpha_composite(tx, (50, (h - tx.height) // 2)); return im
        a = K.text_img('AVATAR', 40, 700, E.WHITE, track=3); dot = K.text_img('·', 40, 700, (170, 170, 190))
        b = K.grad_text('100% IA', 42, 800); h = 84; w = 32 + a.width + 12 + dot.width + 12 + b.width + 18 + 52 + 22
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        glow = K.soft_shadow(w, h, 24, 22, .0, 40)
        body = K.dark_glass(w, h, 24, .70, .0); im.alpha_composite(body)
        bd = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(bd).rounded_rectangle((2, 2, w * 2 - 3, h * 2 - 3), 46, outline=255, width=5)
        bd = bd.resize((w, h), Image.LANCZOS)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(bd); im.alpha_composite(g)
        x = 32
        for p_ in (a, dot, b): im.alpha_composite(p_, (x, (h - p_.height) // 2 + 1)); x += p_.width + 12
        return im
    base = K.C(('tag', stage), mk)
    if stage == 0 or kcheck <= 0: return base
    im = base.copy(); w, h = im.size
    D = 52; cx, cy = w - 22 - D / 2, h / 2
    disc = K.C(('chkdisc', D), lambda: _disc(D))
    ds = .5 + .5 * back(clamp(kcheck * 2.2), 2.6)
    dd = K.scale_im(disc, ds)
    im.alpha_composite(K.fade(dd, clamp(kcheck * 4)), (int(cx - dd.width / 2), int(cy - dd.height / 2)))
    S = 4; c = 56; m = Image.new('L', (c * S, c * S)); d = ImageDraw.Draw(m)
    pts = [(16, 29), (24, 37), (40, 20)]; L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2])
    kk = clamp((kcheck - .2) / .8) * (L1 + L2)
    if kk > 0:
        p1 = pts[1] if kk >= L1 else (pts[0][0] + (pts[1][0] - pts[0][0]) * kk / L1, pts[0][1] + (pts[1][1] - pts[0][1]) * kk / L1)
        d.line([(pts[0][0] * S, pts[0][1] * S), (p1[0] * S, p1[1] * S)], fill=255, width=5 * S)
        if kk > L1:
            u = (kk - L1) / L2; p2 = (pts[1][0] + (pts[2][0] - pts[1][0]) * u, pts[1][1] + (pts[2][1] - pts[1][1]) * u)
            d.line([(pts[1][0] * S, pts[1][1] * S), (p2[0] * S, p2[1] * S)], fill=255, width=5 * S)
    m = m.resize((c, c), Image.LANCZOS); ck = Image.new('RGBA', (c, c), E.WHITE + (0,)); ck.putalpha(m)
    im.alpha_composite(ck, (int(cx - c / 2), int(cy - c / 2)))
    return im


def _disc(d):
    S = 4; m = Image.new('L', (d * S, d * S)); ImageDraw.Draw(m).ellipse((0, 0, d * S - 1, d * S - 1), fill=255)
    m = m.resize((d, d), Image.LANCZOS); g = E.gradient(d, d, E.GRAD).convert('RGBA'); g.putalpha(m); return g


def scan_overlay(ctx, t, fx, top, M, z):
    """brackets, scan line, landmark dots + mesh, tag — screen space through the camera map M."""
    if not (O['CLARAMENTE'] - .02 <= t < T7 + .18): return
    kin = expo((t - O['CLARAMENTE'] + .02) / .20)
    kout = clamp((t - T7) / .16)
    al = (1 - kout)
    if al <= .01: return
    shrink = 1 - .25 * eout(kout)
    pts = np.array([M(fx + dx, top + dy) for dx, dy in LM], np.float32)
    cxs, cys = M(fx, top + 330)
    pts = (pts - (cxs, cys)) * shrink + (cxs, cys)
    bx0, by0 = M(fx + BOX[0], top + BOX[1]); bx1, by1 = M(fx + BOX[2], top + BOX[3])
    sc = 1.22 - .22 * kin
    bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
    bx0, bx1 = bcx + (bx0 - bcx) * sc * shrink, bcx + (bx1 - bcx) * sc * shrink
    by0, by1 = bcy + (by0 - bcy) * sc * shrink, bcy + (by1 - bcy) * sc * shrink
    ident = t >= O['IA']
    # ---- one supersampled overlay canvas for lines (box brackets + mesh + scan line)
    pad = 40; X0, Y0 = int(bx0) - pad, int(by0) - pad; X1, Y1 = int(bx1) + pad, int(by1) + pad
    w, h = X1 - X0, Y1 - Y0; S = 2
    m_line = Image.new('L', (w * S, h * S)); dl = ImageDraw.Draw(m_line)
    m_mesh = Image.new('L', (w * S, h * S)); dm = ImageDraw.Draw(m_mesh)
    # scan progress (sweeps top -> bottom of the box)
    ks = clamp((t - SCAN0) / (SCAN1 - SCAN0)); ys = by0 + (by1 - by0) * sio_(ks)
    # mesh edges: an edge appears once the scan line passed both ends
    for a, b in EDGES:
        ya, yb = max(pts[a][1], pts[b][1]), 0
        if ys >= ya + 2 or t >= SCAN1:
            dm.line([((pts[a][0] - X0) * S, (pts[a][1] - Y0) * S), ((pts[b][0] - X0) * S, (pts[b][1] - Y0) * S)], fill=255, width=S)
    # brackets
    L = 52 * S; lw = 4 * S
    for (x, y, sx, sy) in ((bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)):
        X, Y = (x - X0) * S, (y - Y0) * S
        dl.line([(X, Y + sy * L), (X, Y), (X + sx * L, Y)], fill=255, width=lw, joint='curve')
    m_line = m_line.resize((w, h), Image.LANCZOS); m_mesh = m_mesh.resize((w, h), Image.LANCZOS)
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    mesh_col = (186, 150, 255) if ident else (150, 215, 255)
    mesh_a = (.40 if t < O['IA'] + .3 else .30) * al
    c = Image.new('RGBA', (w, h), mesh_col + (0,)); c.putalpha(m_mesh.point(lambda v: int(v * mesh_a))); ov.alpha_composite(c)
    if ident:
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m_line.point(lambda v: int(v * al))); ov.alpha_composite(g)
    else:
        c = Image.new('RGBA', (w, h), (235, 240, 255, 0)); c.putalpha(m_line.point(lambda v: int(v * .95 * al))); ov.alpha_composite(c)
    ctx.add('screen', ov, X0, Y0, center=False)
    # scan line + glow trail
    if SCAN0 <= t < SCAN1 + .12:
        la = al * (1 - clamp((t - SCAN1) / .12))
        sw = int(bx1 - bx0 + 30)
        ctx.add('screen', scan_band(sw), (bx0 + bx1) / 2, ys - 60, alpha=la)
    # dots
    for i, (x, y) in enumerate(pts):
        if ys < y and t < SCAN1: continue
        tp = SCAN0 + (SCAN1 - SCAN0) * inv_sio((y - by0) / max(1, by1 - by0))
        u = (t - tp) / .10
        sp = .4 + .6 * back(u, 2.5) if u < 1 else 1.0
        d = K.glow_dot(4.6 if ident else 4.2, (170, 120, 255) if ident else (120, 210, 255))
        a = (.85 if t < O['IA'] + .3 else .6) * al
        ctx.add('screen', K.scale_im(d, sp), x, y, alpha=a)
    # tag above the box (top-left corner)
    stage = 1 if ident else 0
    kc = clamp((t - O['NE'] - .02) / .16)
    tg = tag_img(stage, kc)
    pop = .6 + .4 * back((t - (O['IA'] if ident else O['CLARAMENTE'] + .06)) / .18, 2.6)
    tg = K.scale_im(tg, pop * shrink)
    ctx.add('screen', tg, (bx0 + bx1) / 2, by0 - tg.height / 2 - 26, alpha=al * clamp((t - O['CLARAMENTE'] - .06) / .06))


def sio_(x): return K.sio(x)
def inv_sio(y):
    y = clamp(y); return math.acos(1 - 2 * y) / math.pi


def scan_band(w):
    def mk():
        h = 76
        a = np.zeros((h, w), np.float32)
        y = np.arange(h, dtype=np.float32)[:, None]
        trail = np.clip(y / 60, 0, 1) ** 2 * .22 * (y <= 60)
        line = np.exp(-((y - 61) / 1.6) ** 2) * 1.0 + np.exp(-((y - 61) / 7) ** 2) * .35
        xr = np.linspace(-1, 1, w, dtype=np.float32)[None, :]; edge = np.clip((1 - np.abs(xr)) / .12, 0, 1)
        a = np.clip((trail + line) * edge, 0, 1)
        col = np.zeros((h, w, 3), np.float32); g = np.asarray(E.gradient(w, 1, [(120, 210, 255), (150, 160, 255), (190, 130, 255)]), np.float32)
        col[:] = g; col = col * (1 - np.exp(-((y - 61) / 1.6) ** 2)[..., None] * .0) + 255 * np.exp(-((y - 61) / 1.2) ** 2)[..., None] * .6
        return Image.fromarray(np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8), 'RGBA')
    return K.C(('scanband', w), mk)


# ================================================================ the padlock + attention bar
BAR_W, BAR_H = 636, 108
BAR_X, BAR_Y = 522, 1318                 # bar centre (screen)
LOCK_X = BAR_X - BAR_W / 2 + 596         # shackle centre x (clear of the label, wraps the bar's right end)
SHK_W, SHK_T = 112, 22                   # shackle outer width, tube thickness
BODY_W, BODY_H = 150, 128
OPEN_DY = 46


def _tube_shade(mask):
    """chrome tube shading from a mask: distance to edge -> cylinder normal -> metal ramp."""
    from scipy.ndimage import distance_transform_edt
    m = np.asarray(mask, np.float32) / 255
    d = distance_transform_edt(m > .5); r = max(1., d.max())
    n = np.sqrt(np.clip(1 - (1 - d / r) ** 2, 0, 1))
    return m, n


def shackle_img():
    def mk():
        S = 2; w = SHK_W * S; leg = 150 * S; t = SHK_T * S; h = leg + w // 2
        m = Image.new('L', (w, h)); d = ImageDraw.Draw(m)
        d.arc((0, 0, w - 1, w - 1), 180, 360, fill=255, width=t)
        d.rectangle((0, w // 2, t - 1, h), fill=255); d.rectangle((w - t, w // 2, w - 1, h), fill=255)
        m, n = _tube_shade(m)
        x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
        base = 70 + 150 * n ** 1.6 + 70 * n ** 12
        rgb = np.dstack([base * .96, base * .97, base * 1.04 + 8])
        rgb[..., 0] += 30 * (x > 0) * n; rgb[..., 2] += 50 * (x > 0) * n           # violet monitor reflection on the right
        im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), m * 255]).astype(np.uint8), 'RGBA')
        return im.resize((SHK_W, h // S), Image.LANCZOS)
    return K.C('shackle', mk)


def body_img():
    def mk():
        S = 2; w, h = BODY_W * S, BODY_H * S; r = 26 * S
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
        mm = np.asarray(m, np.float32) / 255
        y = np.linspace(0, 1, h, dtype=np.float32)[:, None]; x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
        v = 150 - 105 * y + 70 * np.exp(-((y - .14) / .045) ** 2) - 20 * np.exp(-((y - .55) / .18) ** 2) + 26 * np.exp(-((y - .88) / .04) ** 2)
        v = v * (1 - .18 * x ** 2)
        rng = np.random.default_rng(3); brushed = np.repeat(rng.normal(0, 1, (1, w)).astype(np.float32), h, 0)
        brushed = np.asarray(Image.fromarray(((brushed * 20) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)), np.float32) - 128
        v = v + brushed * .35
        rgb = np.dstack([v * .92, v * .93, v * 1.02 + 8])
        vio = np.exp(-((y - .74) / .16) ** 2) * np.clip(x + .3, 0, 1)
        rgb = rgb + vio[..., None] * np.array([70, 30, 150], np.float32)
        blu = np.exp(-((y - .30) / .10) ** 2) * np.clip(-x + .2, 0, 1)
        rgb = rgb + blu[..., None] * np.array([20, 40, 110], np.float32)
        # bevel: darker rim
        from scipy.ndimage import distance_transform_edt
        dd = distance_transform_edt(mm > .5); rim = np.clip(1 - dd / (5 * S), 0, 1)
        rgb = rgb * (1 - .45 * rim[..., None]) + 255 * (np.clip(1 - dd / (2 * S), 0, 1) * .25 * (y < .5))[..., None]
        im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), mm * 255]).astype(np.uint8), 'RGBA')
        d = ImageDraw.Draw(im)                                    # keyhole
        cx, cy = w / 2, h * .52
        d.ellipse((cx - 13 * S, cy - 13 * S - 8 * S, cx + 13 * S, cy + 13 * S - 8 * S), fill=(18, 18, 26, 255))
        d.polygon([(cx - 7 * S, cy - 6 * S), (cx + 7 * S, cy - 6 * S), (cx + 11 * S, cy + 26 * S), (cx - 11 * S, cy + 26 * S)], fill=(18, 18, 26, 255))
        return im.resize((BODY_W, BODY_H), Image.LANCZOS)
    return K.C('lockbody', mk)


def lock_img(open_k):
    """padlock RGBA (shackle raised by open_k*OPEN_DY); returns (img, shackle-top offset from img top)."""
    key = round(open_k, 2)
    def mk():
        sk = shackle_img(); bd = body_img()
        top_pad = OPEN_DY + 10
        hh = top_pad + sk.height + 10
        im = Image.new('RGBA', (BODY_W + 40, hh + 20), (0, 0, 0, 0))
        sy = top_pad - int(OPEN_DY * key) + 0
        im.alpha_composite(sk, ((im.width - sk.width) // 2, sy))
        by = top_pad + sk.height - 64
        shd = K.soft_shadow(BODY_W, BODY_H, 26, 10, .5, 20)
        im.alpha_composite(shd, ((im.width - shd.width) // 2, by - 20 + 8))
        im.alpha_composite(bd, ((im.width - BODY_W) // 2, by))
        return im, top_pad, by
    return K.C(('lock', key), mk)


def _eye(d=40, col=(250, 249, 246)):
    S = 4; D = d * S; m = Image.new('L', (D, D)); dr = ImageDraw.Draw(m)
    dr.ellipse((D * .04, D * .24, D * .96, D * .76), outline=255, width=int(3 * S)); dr.ellipse((D * .34, D * .34, D * .66, D * .66), fill=255)
    m = m.resize((d, d), Image.LANCZOS); im = Image.new('RGBA', (d, d), col + (0,)); im.putalpha(m); return im


def _watch(d=40, k=0.0, col=(250, 249, 246)):
    S = 4; D = d * S; m = Image.new('L', (D, D)); dr = ImageDraw.Draw(m)
    dr.ellipse((D * .12, D * .2, D * .88, D * .96), outline=255, width=int(3 * S))
    dr.rectangle((D * .42, D * .02, D * .58, D * .12), fill=255); dr.line((D * .5, D * .12, D * .5, D * .2), fill=255, width=int(3 * S))
    a = -math.pi / 2 + 2 * math.pi * k; cx, cy = D * .5, D * .58
    dr.line((cx, cy, cx + math.cos(a) * D * .26, cy + math.sin(a) * D * .26), fill=255, width=int(3 * S))
    m = m.resize((d, d), Image.LANCZOS); im = Image.new('RGBA', (d, d), col + (0,)); im.putalpha(m); return im


def bar_base():
    def mk():
        im = K.dark_glass(BAR_W, BAR_H, BAR_H // 2, .55, .42).copy()
        return im
    return K.C('barbase', mk)


def bar_fill(k, w=BAR_W - 16, h=BAR_H - 16):
    """gradient fill (k 0..1 of the width) with a soft leading edge."""
    if k <= .002: return None
    g = K.C(('barg', w, h), lambda: E.gradient(w, h, E.GRAD).convert('RGBA'))
    m = K.C(('barm', w, h), lambda: _pill_mask(w, h))
    x = np.arange(w, dtype=np.float32); edge = k * w
    ramp = np.clip((edge - x) / 18 + .5, 0, 1)[None, :]
    a = (np.asarray(m, np.float32) * ramp * .62).astype(np.uint8)
    out = g.copy(); out.putalpha(Image.fromarray(a)); return out


def _pill_mask(w, h):
    m = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), h, fill=255)
    return m.resize((w, h), Image.LANCZOS)


BAR_WORDS = [('A', O['A']), ('SUA', O['SUA']), ('ATENÇÃO', O['ATENCAO'])]


def fill_level(t):
    """fills on 'a SUA atenção', then counts down in five steps: one per clock tick, the last one at zero."""
    if t < O['SUA']: return 0.
    if t < O['POR']: return eout((t - O['SUA']) / (O['POR'] - .05 - O['SUA']))
    lv = 1.0
    for tk in T_TICKS + (T_ZERO,):
        lv -= .2 * eout((t - tk) / .09)
    return max(0., lv)


def tick_pulse(t):
    """0..1 decaying pulse after each countdown tick."""
    p = 0.
    for tk in T_TICKS + (T_ZERO,):
        u = t - tk
        if 0 <= u < .25: p = max(p, math.exp(-u * 16))
    return p


def smear_v(im, L):
    """vertical motion smear (the trail sits above: the object falls down)."""
    L = int(L); n = int(min(40, max(4, L / 5)))
    src = np.asarray(im, np.float32).copy(); src[..., :3] *= src[..., 3:] / 255
    acc = np.zeros((im.height + L, im.width, 4), np.float32)
    for g in range(n):
        o = int(round(L * g / (n - 1))); acc[o:o + im.height] += src * (1.6 if g == n - 1 else 1.0)
    acc /= (n + .6)
    acc[..., :3] /= np.maximum(acc[..., 3:], 1) / 255
    return Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8), 'RGBA')


def draw_lock(ctx, t, jolt):
    if t < T_LOCK_IN: return
    jx, jy = jolt
    kin = expo((t - T_LOCK_IN) / .28)
    bx = BAR_X + (1 - kin) * -700 + jx; by = BAR_Y + jy
    ctx.add('screen', bar_base(), bx, by, glass=10, alpha=clamp(kin * 1.4))
    fl = fill_level(t)
    f = bar_fill(fl)
    if f is not None: ctx.add('screen', f, bx, by)
    # icon: eye, then a stopwatch for the countdown
    if t < O['POR']:
        ctx.add('screen', K.C('eye', lambda: _eye(44)), bx - BAR_W / 2 + 56, by, alpha=.95)
    else:
        u = (t - O['POR']) / .18; s = (.6 + .4 * back(u, 2.4)) * (1 + .22 * tick_pulse(t))
        kk = sum(eout((t - tk) / .06) for tk in T_TICKS + (T_ZERO,)) / 5          # the hand jumps on every tick
        wi = K.C(('watch', round(kk, 2)), lambda: _watch(50, round(kk, 2)))
        ctx.add('screen', K.scale_im(wi, s), bx - BAR_W / 2 + 54, by)
        rg = K.ring(76, 4, (190, 170, 255), .9, k=max(.001, fill_level(t)))   # remaining-time ring around it
        ctx.add('screen', K.scale_im(rg, s), bx - BAR_W / 2 + 54, by)
    # kinetic label (= the spoken words "a sua atenção")
    x = bx - BAR_W / 2 + 102
    for wd, t0 in BAR_WORDS:
        im = K.text_img(wd, 46, 800, E.WHITE, track=1)
        if t >= t0 - .02:
            lt = t - t0 + .02; s = .7 + .3 * back(lt / .16, 1.6)
            ctx.add('screen', K.scale_im(im, s), x + im.width / 2, by + 2, alpha=clamp(lt / .05))
        x += im.width + 14
    # padlock: falls (open), lands, slams shut on PRENDER, pops open at zero
    if t < T_DROP: return
    vy = 0.
    if t < T_LAND:
        u = (t - T_DROP) / (T_LAND - T_DROP); yoff = -DROP_H * (1 - u * u)
        vy = DROP_H * 2 * u / (T_LAND - T_DROP) / 30                         # px per frame
    else:
        u = (t - T_LAND) / .12; yoff = -10 * math.sin(math.pi * clamp(u)) if u < 1 else 0
    if t < O['PRENDER'] - .015: ok = 1.0
    elif t < T_ZERO: ok = max(0., 1 - (t - O['PRENDER'] + .015) / .035)
    else:
        u = (t - T_ZERO) / .10; ok = clamp(back(u, 3.0)) if u < 1 else 1.0
    im, tp, byy = lock_img(ok)
    jig = sum(7 * math.exp(-(t - tk) * 11) * math.sin((t - tk) * 52) for tk in T_TICKS if 0 <= t - tk < .4)
    if abs(jig) > .3:                                                     # the lock rattles on every tick
        w0, h0 = im.size; im = im.rotate(jig, Image.BICUBIC, expand=True, center=(w0 / 2, tp + 10))
        dx_, dy_ = (im.width - w0) / 2, (im.height - h0) / 2
    else: dx_ = dy_ = 0.
    if vy > 6: im, sm = smear_v(im, vy * .75), vy * .75
    else: sm = 0.
    # shackle top sits ~34 px above the bar top when closed
    sx = LOCK_X + jx + (bx - BAR_X - jx); sy = BAR_Y - BAR_H / 2 - 34 - tp + yoff + jy
    ctx.add('screen', im, sx - im.width / 2, sy - sm - dy_, center=False)
    # slam flash ring
    u = (t - O['PRENDER']) / .32
    if 0 <= u < 1:
        rg = K.ring(int(120 + 260 * eout(u)), max(2, int(10 * (1 - u))), (200, 180, 255), .9 * (1 - u) ** 1.5)
        ctx.add('screen', rg, sx, sy + byy + BODY_H / 2)


# ================================================================ draw
def draw(ctx, lt, t):
    ctx.captions = False
    P = ctx.post
    av = K.av_frame(ctx, t)
    fx, top = K.face_track(av)

    if t < O['DES']:
        # ---- shot 1: confessional snap-in (JUMP at START)
        k = expo(lt / .22)
        z = 1.46 + .16 * (1 - k) - .02 * clamp(lt / .9)
        ctx.cam = dict(z=z, x=530., y=868., dx=0., dy=0., rot=0.)
        ctx.bg_img = K.C('bg_s1', lambda: K.studio_at(1.06, (540, 760), blur=5))
        P['zoom_blur'] = .55 * clamp(1 - lt / .1)
        P['vignette'] = .42
        K.caps(ctx, t, PAGES, y=1500)
        return

    if t < T_MAX + .2:
        # ---- the window gag: inner camera keeps the close-up, the frame shrinks into a window
        z = 1.44 - .02 * clamp((t - O['DES']) / 1.2)
        if t >= T_MAX: z = lerp(z, 1.30, expo((t - T_MAX) / .17))
        ctx.cam = dict(z=z, x=530., y=868., dx=0., dy=0., rot=0.)
        ctx.bg_img = K.C('bg_s1', lambda: K.studio_at(1.06, (540, 760), blur=5))
        P['vignette'] = .34
        ctx.wrap = window_wrap(t)
        draw_cursor(ctx, t)
        s, kui, x0, y0, cw, ch, ty = win_geom(t)
        K.caps(ctx, t, PAGES, y=lerp(1500, 1480, kui), base=int(lerp(92, 84, kui)), maxw=int(lerp(900, 780, kui)))
        if t >= T_MAX: P['zoom_blur'] = .35 * clamp(1 - (t - T_MAX) / .12)
        return

    if t < T7:
        # ---- the face scan (medium close-up; deadpan push on "né?")
        z = 1.30 + .05 * smooth((t - T_MAX) / (O['NE'] - T_MAX))
        if t >= O['NE']: z += .07 * expo((t - O['NE']) / .14)
        cam = dict(z=z, x=530., y=880., dx=0., dy=0., rot=0.)
        ctx.cam = cam
        ctx.bg_img = K.C('bg_s3', lambda: K.studio_at(1.08, (540, 760), blur=7, dim=.12))
        P['vignette'] = .44
        M, _ = K.cam_map(cam)
        scan_overlay(ctx, t, fx, top, M, z)
        if O['IA'] - .01 <= t < O['IA'] + .14:
            u = (t - O['IA'] + .01) / .15
            P['rgb'] = 9 * (1 - u); P['glitch'] = .28 * (1 - u) if u < .5 else 0
        K.caps(ctx, t, PAGES, y=1520)
        return

    # ---- shot 4: medium shot, the attention bar + padlock
    k = expo((t - T7) / .35)
    z = lerp(1.42, 1.13, k) + .03 * clamp((t - T7) / 2.6)
    if t >= O['PRENDER']: z += .07 * expo((t - O['PRENDER']) / .10) - .03 * smooth((t - O['PRENDER'] - .2) / 1.2)   # punch-in on the CLUNK
    jx, jy = K.shake(t, O['PRENDER'], 14, .26)
    cam = dict(z=z, x=532., y=lerp(880., 905., k), dx=jx * .6, dy=jy * .6, rot=0.)
    ctx.cam = cam
    ctx.bg_img = K.C('bg_s4', lambda: K.studio_at(1.04, (540, 760), blur=5))
    P['vignette'] = .40
    M, _ = K.cam_map(cam)
    if t < T7 + .18: scan_overlay(ctx, t, fx, top, M, z)
    draw_lock(ctx, t, (jx, jy))
    if O['PRENDER'] - .01 <= t < O['PRENDER'] + .08:
        P['flash'] = .10 * (1 - (t - O['PRENDER'] + .01) / .09); P['flash_col'] = (190, 170, 255)
    K.caps(ctx, t, PAGES, y=1560)
