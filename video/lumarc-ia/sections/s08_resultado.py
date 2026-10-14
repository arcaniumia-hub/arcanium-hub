"""s08 — O RESULTADO (57.08–62.84).  "O resultado?" / "Entrega mais rápida." / "Preço mais baixo." /
"E um conteúdo que ninguém diria que é genérico."

A  57.08 JUMP — HARD STOP: the studio lights die (monitors off, a cold spot on him, heavy vignette); "O" (57.155) a small
   white kicker.  57.21 "RESULTADO": ONE big hit — the lights slam back on with a violet flash, SNAP ZOOM (z 1.04 ->
   1.30 in 3 frames, zoom blur + RGB split + shake) and RESULTADO slams in huge behind him (scale 1.7 -> 1, ghost trail),
   his head overlapping the letters; 57.535 stressed "-TA-" a light sheen runs through the word + micro punch;
   57.66 "-DO?" the "?" swings in.  57.90 whip-pan out (horizontal smear).
B  58.00 JUMP — whip-in, new framing.  "ENTREGA" (58.09) a glass delivery bar drops in above his head: watch face
   (ticks, no digits) · track · target ring; 58.245 a parcel hops onto the track; 58.47 "MAIS" it starts rolling and
   the watch starts ticking; 58.665 "RÁPIDA" (stress 58.775): FAST-FORWARD — the parcel zips to the end, the watch
   hands whirl, light streaks rip through the studio (behind and in front of him), he leaves speed echoes, push-in +
   zoom blur; 58.80 the ring fills with the LUMARC gradient and the ✓ pops.  No time numbers anywhere.
C  (59.20, same shot) the bar flies up.  59.50 "PREÇO": a LUMARC price tag (R$ glyph only, no digits) swings in on a
   string at his left; 59.69 "MAIS" it squashes smaller while a cascade of chevrons pulses down at his right;
   59.91 "BAIXO": the string pays out — the tag DROPS, shrinks and lands lower with a spring on the stressed "BAI"
   (60.00), the chevrons punch down.
D  60.40 JUMP — he is in front of a dark wall of empty frames (3-D, rotated, DOF); "E UM" the frames' edges light up
   in a wave; 60.87 "CONTEÚDO": the wall flips on, tile by tile from the centre out — REAL LUMARC work (SILENCE ONE
   films, croissant, North Roast carousel, website, burger/latte/watchmaker close-ups, casa maquette, breakout feed,
   3-D motion); two tiles play video.  "QUE NINGUÉM DIRIA" the wall drifts (parallax) and a glint crosses it.
   61.745 "QUE É…" the red GENÉRICO stamp's shadow grows on the glass; 62.15 (stressed "NÉ", as in the hook) the stamp
   SLAMS where it landed in the hook (it IS the caption word) — the wall drains to grey for 4 frames… and fights back:
   62.20 cracks race through the stamp, 62.29 "-RI-": it SHATTERS (shards + ink dust fly at the lens) and a burst of
   portfolio cards explodes out of the impact toward the camera (3-D, tumbling, motion-blurred) while the wall flares
   back to full colour.  62.70 a card flies into the lens -> cut.
Captions: own word pops (engine look) on the measured onsets; "RESULTADO?" is the giant type itself, "GENÉRICO" is the
stamp itself.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _F_kit as K
from sections import _shared as SH

START, END = E.span(27, 30)                      # 57.08 – 62.84
T27, T28, T29, T30 = (E.TL[i]['t0'] for i in (27, 28, 29, 30))     # 57.08, 58.00, 59.20 (joined), 60.40
W, H = E.W, E.H
clamp, eout, ein, back, lerp, smooth, expo, eio = E.clamp, E.eout, E.ein, E.back, K.lerp, K.smooth, K.expo, K.eio

# word onsets measured on src/tight16k.raw (5 ms STFT + 80-900 Hz / 1-3 kHz / >3.5 kHz band envelopes, out/F/sp_*.png):
# plosive bursts after their closure, fricative starts, vowel onsets after a pause
O = dict(O=57.155, RESULTADO=57.21, TA=57.535, DO=57.66, RES_END=57.80,            # "o re-sul-TA-do?"
         ENTREGA=58.09, TRE=58.245, GA=58.39, MAIS=58.47, MAIS_S=58.60,           # "en-TRE-ga MAIS"  (s of mais .60)
         RAPIDA=58.665, RA=58.775, PI=58.935, RAP_END=59.12,                      # [h] 58.665, stressed vowel .775
         PRECO=59.50, MAIS2=59.69, BAIXO=59.91, BAI=60.00, BAIXO_END=60.30,       # p burst .50 | m .69 | b .91
         E=60.495, UM=60.72, CONTEUDO=60.87, QUE=61.165, NINGUEM=61.22,           # k burst 60.87 | k 61.165
         DIRIA=61.535, QUE2=61.745, E2=61.80, GENERICO=62.045, NE=62.15,         # d 61.535 | k 61.745 | ʒ 62.045
         RI=62.29, CO=62.45, GEN_END=62.62)

HIT = O['RESULTADO']
ZIP0, ZIP1 = O['RAPIDA'] - .01, O['RA'] + .03          # the parcel zips (58.655 -> 58.805)
CHECK = ZIP1
SWING = O['PRECO'] - .10                               # tag swings in, lands on "PREÇO"
DROP0, DROP1 = O['BAIXO'], O['BAI'] + .02             # string pays out -> lands on "BAI"
FLIP0 = O['CONTEUDO'] - .03                            # tiles flip on, centre first
STAMP_IN = O['NE'] - .085                              # the stamp falls (hook: 85 ms) and lands on "NÉ"
SLAM = O['NE']
CRACK = O['NE'] + .05
BURST = O['RI']
LENS0 = 62.60                                          # the last card leaves the wall -> into the lens on the cut

CUES = [
    (T27 + .005, 'switch', {'gain': -4}),                      # lights die (hard stop)
    (T27 + .01, 'sub', {'gain': -10}),
    (HIT - .03, 'zoom', {'gain': -5}),                         # snap zoom
    (HIT, 'impact', {'gain': 0}),                              # ONE big hit
    (HIT, 'boom', {'gain': -3}),
    (O['TA'], 'shimmer', {'gain': -13}),                       # sheen through the word
    (O['DO'] + .02, 'pop', {'gain': -9}),                      # "?"
    (57.91, 'whoosh', {'gain': -9}),                           # whip out
    (T28, 'swipe', {'gain': -8}),                              # whip in
    (O['ENTREGA'] - .02, 'whoosh', {'gain': -13}),             # delivery bar drops in
    (O['ENTREGA'] + .14, 'click', {'gain': -9}),               # ...and lands
    (O['TRE'], 'pop', {'gain': -10}),                          # parcel hops on
    (O['MAIS'], 'clock', {'i': 0, 'gain': -9}),                # the watch starts ticking
    (O['MAIS'] + .09, 'clock', {'i': 1, 'gain': -10}),
    (ZIP0, 'ff', {'dur': .2, 'gain': -2}),                     # FAST-FORWARD zip
    (ZIP0 + .02, 'whoosh', {'gain': -8}),
    (CHECK, 'ding', {'note': 'E6', 'gain': -6}),               # ✓
    (CHECK + .01, 'pop', {'gain': -8}),
    (59.21, 'swipe', {'gain': -12}),                           # bar flies away
    (SWING, 'whoosh', {'gain': -12}),                          # tag swings in
    (O['PRECO'], 'cash', {'gain': -7}),                        # "PREÇO"
    (O['MAIS2'], 'tick', {'gain': -9}),                        # squash
    (O['MAIS2'] + .02, 'flick', {'gain': -14, 'pan': .5}),     # chevrons
    (DROP0, 'swoosh_up', {'gain': -16}),                       # (reverse feel) string pays out
    (DROP0 + .01, 'whoosh', {'gain': -10}),
    (DROP1, 'thud', {'gain': -5}),                             # lands on "BAI"
    (DROP1 + .01, 'pop', {'gain': -8}),
    (T30, 'whoosh', {'gain': -10}),                            # cut to the wall
    (O['E'], 'shimmer', {'gain': -15}),                        # frame edges light up
    (FLIP0 + .02, 'flick', {'gain': -6, 'pan': 0.0}),          # tiles flip on (cascade)
    (FLIP0 + .12, 'flick', {'gain': -9, 'pan': -.4}),
    (FLIP0 + .22, 'flick', {'gain': -11, 'pan': .4}),
    (FLIP0 + .32, 'flick', {'gain': -13, 'pan': -.6}),
    (O['DIRIA'], 'shimmer', {'gain': -11}),                    # glint across the wall
    (O['QUE2'], 'riser', {'to': SLAM, 'gain': -8}),            # stamp shadow grows
    (SLAM, 'stamp', {'gain': 0}),                              # SLAM (callback to the hook)
    (SLAM, 'thud', {'gain': -5}),
    (CRACK, 'crack', {'gain': -3}),                            # cracks race through the stamp
    (BURST, 'shatter', {'dur': 1.0, 'gain': 0}),               # SHATTER
    (BURST, 'boom', {'gain': -2}),
    (BURST + .02, 'glass', {'gain': -9}),
    (BURST + .06, 'whoosh', {'gain': -5}),                     # the work explodes at the lens
    (LENS0 + .06, 'whoosh', {'gain': -9}),                     # a card flies into the lens
]

F_, T_ = False, True
PAGES_B = [(O['ENTREGA'] - .04, O['MAIS'] - .02, [('ENTREGA', O['ENTREGA'], F_)]),
           (O['MAIS'] - .02, T29 + .25, [('MAIS', O['MAIS'], F_), ('RÁPIDA.', O['RAPIDA'], T_)])]
PAGES_C = [(O['PRECO'] - .04, T30, [('PREÇO', O['PRECO'], F_), ('MAIS', O['MAIS2'], F_), ('BAIXO.', O['BAIXO'], T_)])]
PAGES_D = [(O['E'] - .04, O['QUE'] - .02, [('E', O['E'], F_), ('UM', O['UM'], F_), ('CONTEÚDO', O['CONTEUDO'], T_)]),
           (O['QUE'] - .02, O['QUE2'] - .02, [('QUE', O['QUE'], F_), ('NINGUÉM', O['NINGUEM'], F_), ('DIRIA', O['DIRIA'], F_)]),
           (O['QUE2'] - .02, BURST + .12, [('QUE', O['QUE2'], F_), ('É…', O['E2'], F_)])]


def C(k, fn): return K.C(('s08',) + (k if isinstance(k, tuple) else (k,)), fn)


def cam_xy(cam):
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return z, X, Y


def avatar_cutout(ctx, t):
    """him in screen space through the current camera (for type that sits BEHIND him but must stay crisp)."""
    av = K.av_frame(ctx, t)
    if av is None: return None
    A = ctx.avatar
    if A['bright'] != 1:
        av = Image.merge('RGBA', [*Image.eval(av.convert('RGB'), lambda v: int(min(255, v * A['bright']))).split(), av.getchannel('A')])
    lay = av
    if abs(A['s'] - 1) > .005 or A['x'] or A['y']:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); a2 = K.scale_im(av, A['s'])
        E._paste(lay, dict(img=a2, xy=(int(540 - a2.width / 2 + A['x']), int(H - a2.height + A['y'])), glass=0))
    z, X, Y = cam_xy(ctx.cam)
    return E.zoom(lay, z, (ctx.cam['x'], ctx.cam['y']), dx=X - ctx.cam['x'], dy=Y - ctx.cam['y'], rot=ctx.cam['rot'])


# =========================================================================================== A: "O resultado?"
WORD_SIZE = 136


def spot_mask():
    """cold spotlight on him in the dark studio (float32 multiplier, full frame)."""
    def mk():
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        r = np.sqrt(((xx - 540) / 430) ** 2 + ((yy - 980) / 760) ** 2)
        m = .16 + .84 * np.clip(1.25 - r, 0, 1) ** 1.6
        m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
        return m[..., None]
    return C('spot', mk)


def beat_a(ctx, t):
    P = ctx.post
    u = t - HIT
    if t < HIT:
        z = 1.04 + .015 * (t - T27) / (HIT - T27); cy = 900
    else:
        z = lerp(1.04, 1.34, expo(u / .09)) + .06 * smooth((u - .1) / .75)
        if t >= O['TA']: z += .025 * K.bump(t - O['TA'], .12)
        cy = lerp(900, 800, expo(u / .09))
    dx, dy = K.shake(t, HIT, 18., tau=.08, f=17.)
    ex = clamp((t - 57.90) / .10)                                     # whip out
    ctx.cam = dict(z=z, x=540., y=cy, dx=dx - 189 * ein(ex), dy=dy, rot=0.)
    if t < HIT:                                                        # HARD STOP: lights out
        ctx.bg_dim = .84; ctx.avatar['bright'] = .62
        P['vignette'] = .8; P['sat'] = .55
    else:
        P['flash'] = .10 * (1 - clamp(u / .07)); P['flash_col'] = (236, 228, 255)     # (no grey veil)
        P['bright'] = 1 + .55 * (1 - eout(u / .16)) + .06 * (1 - clamp(u / .4))       # exposure punch: lights slam on
        P['zoom_blur'] = 1.0 * (1 - clamp(u / .08))
        P['rgb'] = 9 * (1 - clamp(u / .10))
        P['vignette'] = .38
    # the word (screen layer) + him cut out on top -> RESULTADO sits BEHIND his head, crisp
    layers = []
    cx, cy0 = 495, 478                                                 # word centre: "RESULTADO?" centred, head overlaps it
    if t >= O['O'] - .02:                                              # "O" kicker
        k = clamp((t - O['O'] + .02) / .1)
        o_im, _ = K.display('O', 70, 800, 'white', glow=.3)
        sc = .8 + .2 * back(k, 2)
        layers.append((K.scale_im(o_im, sc), 118 - 300 * ein(ex), cy0 - 112, k * (.75 if t < HIT else 1)))
    if t >= HIT - .05:
        wd, wm = K.display('RESULTADO', WORD_SIZE, 900, 'grad', glow=.55)
        ks = clamp((t - (HIT - .05)) / .05)
        s = lerp(1.75, 1.0, ein(ks)) if t < HIT else 1 + .05 * math.exp(-u / .06) * math.cos(u * 55)
        if t >= O['TA']:
            wd = K.sheen(wd, (t - O['TA']) / .38, wm, 34, .6)
            s *= 1 + .03 * K.bump(t - O['TA'], .12)
        smear = 0
        if ex > 0: smear = -260 * ex
        if t < HIT:                                                     # ghost trail of the slam
            for g in (2, 1):
                gs = lerp(1.75, 1.0, ein(clamp(ks - .35 * g))) * 1.0
                layers.append((K.scale_im(wd, gs), cx, cy0, .22 * ks / g))
        im = K.scale_im(wd, s)
        if smear: im = K.hsmear(im, smear)
        layers.append((im, cx + 300 * ein(ex) * -1, cy0, clamp(ks * 2.5)))
        if t >= O['DO'] - .03:                                          # "?" swings in
            kq = clamp((t - (O['DO'] - .03)) / .2)
            q, _ = K.display('?', int(WORD_SIZE * 1.02), 900, 'grad', glow=.55, cols=[E.GRAD_LIGHT[2]] * 3)
            qi = K.rotated(K.scale_im(q, .5 + .5 * back(kq, 2.6)), lerp(-40, 8, eout(kq)) * (1 - kq) + 8 * kq)
            if smear: qi = K.hsmear(qi, smear)
            pad = int(WORD_SIZE * .42)
            layers.append((qi, cx + im.width / 2 - pad + 50 - 300 * ein(ex), cy0 - 3, clamp(kq * 3)))
    for im, x, y, a in layers: ctx.add('screen', im, x, y, alpha=a)
    if t >= HIT - .05:
        cut = avatar_cutout(ctx, t)
        if cut is not None:
            if ex > 0: cut = K.hsmear(cut, -230 * ein(ex))
            ctx.add('screen', cut, 0, 0, center=False)
    if t < HIT:
        def wrap(fr, t=t):
            a = np.asarray(fr.convert('RGB'), np.float32) * spot_mask()
            return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
        ctx.wrap = wrap
    elif ex > 0:
        ctx.wrap = lambda fr: K.hsmear(fr.convert('RGB'), -230 * ein(ex)).convert('RGBA')
    ctx.captions = False


# =========================================================================================== B: "Entrega mais rápida."
BAR_W, BAR_H = 960, 210
BAR_Y = 318
TRACK_X0, TRACK_X1 = 236, 770                                          # in panel px
CLOCK_X, RING_X = 122, 862


def bar_panel():
    def mk():
        p = E.glass_panel(BAR_W, BAR_H, 52, tint=(150, 140, 255), alpha=.13, border=.5)
        d = ImageDraw.Draw(p)
        cy = BAR_H // 2
        d.rounded_rectangle((TRACK_X0, cy - 10, TRACK_X1, cy + 10), 10, fill=(255, 255, 255, 46))
        for i in range(1, 6):                                          # quiet milestone dots (no labels)
            x = TRACK_X0 + (TRACK_X1 - TRACK_X0) * i / 6
            d.ellipse((x - 4, cy - 4, x + 4, cy + 4), fill=(255, 255, 255, 80))
        ring = K.ring_sprite(56, 2.6, .8)
        p.alpha_composite(ring, (int(RING_X - ring.width / 2), int(cy - ring.height / 2)))
        cf = K.clock_face(140, (236, 236, 250))
        p.alpha_composite(cf, (int(CLOCK_X - 70), int(cy - 70)))
        return p
    return C('bar', mk)


def streak_sprite(L, th, col):
    def mk():
        w, h = int(L), int(th * 6 + 6)
        x = np.linspace(0, 1, w, dtype=np.float32)[None, :]; y = (np.arange(h, dtype=np.float32)[:, None] - h / 2) / max(1, th)
        a = np.exp(-y ** 2) * (x ** 1.6) * np.clip((1 - x) / .06, 0, 1)
        core = np.exp(-(y * 2.2) ** 2) * x ** 2
        rgb = np.zeros((h, w, 3), np.float32) + np.array(col, np.float32)
        rgb = rgb + (255 - rgb) * core[..., None] * .8
        return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8), 'RGBA')
    return C(('streak', int(L), th, col), mk)


STREAKS = [dict(y=120 + hy * 1700, L=420 + 900 * K.hrand(i, 2), th=2.2 + 4.0 * K.hrand(i, 3), v=6200 + 5200 * K.hrand(i, 4),
                ph=K.hrand(i, 5), col=[(120, 140, 255), (160, 120, 255), (210, 190, 255), (255, 255, 255)][i % 4],
                front=(i % 3 == 0))
           for i, hy in enumerate([K.hrand(j, 1) for j in range(46)])]


def streaks(ctx, t, k):
    if k <= .02: return
    for s in STREAKS:
        x = -1200 + ((t - ZIP0) * s['v'] + s['ph'] * 2400) % 2900
        sp = streak_sprite(s['L'], round(s['th'], 1), s['col'])
        ctx.add('screen' if s['front'] else 'behind', sp, x, s['y'], center=False, alpha=k * (.85 if s['front'] else 1.0))


def beat_b(ctx, t):
    P = ctx.post
    u = t - T28
    win = clamp(u / .09)                                               # whip-in
    zk = K.bump(t - ZIP0, .16)
    z = 1.16 + .05 * smooth((t - T28) / 1.2) + .07 * zk
    ex = clamp((t - (T29 + .02)) / .2)                                 # (C reuses this shot)
    ctx.cam = dict(z=z, x=540., y=820., dx=189 * (1 - eout(win)), dy=0., rot=0.)
    if win < 1: ctx.wrap = lambda fr, L=230 * (1 - eout(win)): K.hsmear(fr.convert('RGB'), -L).convert('RGBA')
    # speed: streaks + echoes + zoom blur
    sk = clamp((t - ZIP0) / .05) * (1 - clamp((t - CHECK) / .16))
    streaks(ctx, t, sk)
    if sk > .02:
        ctx.avatar['copies'] = [dict(x=-70 * sk, alpha=.32 * sk), dict(x=-150 * sk, alpha=.16 * sk)]
        if win >= 1 and t < CHECK: ctx.wrap = lambda fr, L=22 * sk: K.hsmear(fr.convert('RGB'), L).convert('RGBA')
    # the delivery bar (screen space, glass)
    if t >= O['ENTREGA'] - .03 and ex < 1:
        k = clamp((t - (O['ENTREGA'] - .03)) / .2)
        y = lerp(-140, BAR_Y, back(k, 1.6)) - 340 * ein(ex)
        pnl = bar_panel().copy()
        cy = BAR_H // 2
        # progress
        if t < O['MAIS']: pr = 0.0
        elif t < ZIP0: pr = .16 * eio((t - O['MAIS']) / (ZIP0 - O['MAIS']))
        else: pr = lerp(.16, 1.0, eio((t - ZIP0) / (ZIP1 - ZIP0)))
        px = TRACK_X0 + (TRACK_X1 - TRACK_X0) * pr
        if pr > .005:
            fw = int(px - TRACK_X0) + 8
            fill = E.gradient(max(2, fw), 20, E.GRAD_LIGHT).convert('RGBA')
            m = Image.new('L', fill.size); ImageDraw.Draw(m).rounded_rectangle((0, 0, fill.width - 1, 19), 10, fill=255); fill.putalpha(m)
            pnl.alpha_composite(fill, (TRACK_X0, cy - 10))
            if sk > .05:                                               # light trail behind the parcel
                tr = streak_sprite(240, 3.0, (200, 190, 255))
                K.paste(pnl, K.fade(tr, sk), px - 240, cy - tr.height / 2, center=False)
        # watch hands
        if t < O['MAIS']: am, ah = 0.0, 0.0
        elif t < ZIP0: am = (t - O['MAIS']) * 6.0; ah = am / 12
        else:
            v = eio((t - ZIP0) / (ZIP1 - ZIP0 + .06)); am = (ZIP0 - O['MAIS']) * 6.0 + v * 2 * math.pi * 9; ah = am / 12
        whirl = clamp((t - ZIP0) / .04) * (1 - clamp((t - ZIP1 - .04) / .1))
        hands = K.clock_hands(140, am, ah, (250, 250, 255), blur=2.5 * whirl)
        K.paste(pnl, hands, CLOCK_X - 70, cy - 70, center=False)
        if whirl > .05:
            for g in (1, 2):
                gh = K.clock_hands(140, am - .5 * g, ah - .04 * g, (180, 170, 255), blur=3)
                K.paste(pnl, gh, CLOCK_X - 70, cy - 70, center=False, alpha=.35 * whirl / g)
        # the parcel riding the track
        if t >= O['TRE'] - .02:
            kb = clamp((t - (O['TRE'] - .02)) / .16)
            hop = -38 * math.sin(math.pi * clamp(kb * 1.0)) * (1 - kb * .2)
            box = K.icon_box(92, (250, 248, 255))
            if sk > .05: box = K.hsmear(box, 26 * sk)
            bx = px if pr > 0 else TRACK_X0
            if t < CHECK + .02 or True:
                ab = 1.0 - clamp((t - CHECK) / .08)
                K.paste(pnl, K.scale_im(box, .6 + .4 * back(kb, 2)), bx, cy - 52 + hop, alpha=ab)
        # target ring fills + check
        if t >= CHECK - .01:
            kc = clamp((t - (CHECK - .01)) / .18)
            disc = Image.new('L', (120, 120)); ImageDraw.Draw(disc).ellipse((4, 4, 115, 115), fill=255)
            g = E.gradient(120, 120, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(disc)
            g = K.scale_im(g, .3 + .7 * back(kc, 2.2))
            K.paste(pnl, g, RING_X, cy)
            ck = K.scale_im(K.icon_check(74, (255, 255, 255), .14), .4 + .6 * back(clamp(kc * 1.4), 3))
            K.paste(pnl, ck, RING_X, cy + 2)
        s = 1 + .03 * K.bump(t - CHECK, .1) + .02 * K.bump(t - O['PI'], .1)
        im = K.scale_im(pnl, s)
        ctx.add('screen', im, 540, y, glass=16, alpha=clamp(k * 3) * (1 - ex))
        rx_ = 540 + (RING_X - BAR_W / 2) * s
        if t >= CHECK and t < CHECK + .4:                              # flash at the ring
            gl = K.glow_sprite(260, 260, (150, 130, 255), 40)
            ctx.add('screen', gl, rx_, y, alpha=.8 * (1 - clamp((t - CHECK) / .35)))
        if CHECK - .01 <= t < CHECK + .17:                             # shock ring (screen space: never clipped)
            kc = clamp((t - (CHECK - .01)) / .18)
            ctx.add('screen', K.ring_sprite(62 + 90 * eout(kc), 3.0, .9 * (1 - kc)), rx_, y)
    # ▶▶ ghost glyph through the frame during the zip
    if sk > .05 and t < CHECK + .2:
        ff = K.vhs_osd('', 190, 'ff')
        ctx.add('behind', K.hsmear(ff, 40), 300 + 900 * clamp((t - ZIP0) / .3), 760, alpha=.35 * sk)


# =========================================================================================== C: "Preço mais baixo."
TAG_W, TAG_H = 236, 330
PIVOT = (238, -60)


def tag_img():
    """vertical LUMARC price tag (R$ glyph, no digits) on a square canvas whose centre is the string hole."""
    def mk():
        S = 3; w, h = TAG_W * S, TAG_H * S
        m = Image.new('L', (w, h)); d = ImageDraw.Draw(m)
        ch = int(h * .17); r = int(w * .12)
        d.polygon([(w * .24, 0), (w * .76, 0), (w, ch), (w, h - r), (0, h - r), (0, ch)], fill=255)
        d.rounded_rectangle((0, h - 3 * r, w - 1, h - 1), r, fill=255)
        hole = (w / 2, h * .1); hr = w * .055
        d.ellipse((hole[0] - hr, hole[1] - hr, hole[0] + hr, hole[1] + hr), fill=0)
        m = m.resize((TAG_W, TAG_H), Image.LANCZOS)
        g = Image.new('RGB', (TAG_W, TAG_H))
        yy, xx = np.mgrid[0:TAG_H, 0:TAG_W].astype(np.float32)
        k = np.clip((xx / TAG_W * .55 + yy / TAG_H * .45), 0, 1)[..., None]
        c0, c1, c2 = (np.array(c, np.float32) for c in E.GRAD)
        col = np.where(k < .5, c0 + (c1 - c0) * (k / .5), c1 + (c2 - c1) * ((k - .5) / .5))
        col = col * (1.05 - .25 * (yy / TAG_H))[..., None] + np.clip(1 - yy / (TAG_H * .5), 0, 1)[..., None] ** 2 * 40
        body = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA'); body.putalpha(m)
        # inner hairline + R$ glyph
        ln = Image.new('L', (w, h)); ImageDraw.Draw(ln).polygon([(w * .27, h * .035), (w * .73, h * .035), (w * .95, ch + h * .015), (w * .95, h * .955),
                                                                (w * .05, h * .955), (w * .05, ch + h * .015)], outline=255, width=4)
        ln = ln.resize((TAG_W, TAG_H), Image.LANCZOS)
        wl = Image.new('RGBA', (TAG_W, TAG_H), (255, 255, 255, 0)); wl.putalpha(ln.point(lambda v: int(v * .45))); body.alpha_composite(wl)
        f = E.font(118, 900); l, tp, rr, b = f.getbbox('R$')
        tm = Image.new('L', (TAG_W, TAG_H)); ImageDraw.Draw(tm).text(((TAG_W - (rr - l)) / 2 - l, TAG_H * .56 - (b + tp) / 2), 'R$', font=f, fill=255)
        sh = Image.new('RGBA', (TAG_W, TAG_H), (20, 10, 60, 0)); sh.putalpha(tm.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .5)))
        body.alpha_composite(sh, (0, 4))
        tx = Image.new('RGBA', (TAG_W, TAG_H), E.WHITE + (0,)); tx.putalpha(tm); body.alpha_composite(tx)
        # on a square canvas centred on the hole, with a soft shadow
        R = int(math.hypot(TAG_W / 2, TAG_H) + 40)
        can = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0))
        ox, oy = int(R - TAG_W / 2), int(R - TAG_H * .1)
        shd = Image.new('RGBA', can.size, (0, 0, 10, 0)); sa = Image.new('L', can.size); sa.paste(m, (ox + 10, oy + 26))
        shd.putalpha(sa.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .55))); can.alpha_composite(shd)
        can.alpha_composite(body, (ox, oy))
        return can
    return C('tag', mk)


def down_arrow():
    """big LUMARC-gradient down arrow with a soft glow (RGBA)."""
    def mk():
        S = 3; w, h = 150, 250
        m = Image.new('L', (w * S, h * S)); d = ImageDraw.Draw(m)
        d.rounded_rectangle((w * S * .36, 0, w * S * .64, h * S * .62), w * S * .14, fill=255)
        d.polygon([(0, h * S * .52), (w * S, h * S * .52), (w * S * .5, h * S)], fill=255)
        m = m.resize((w, h), Image.LANCZOS)
        pad = 40; big = Image.new('L', (w + 2 * pad, h + 2 * pad)); big.paste(m, (pad, pad))
        out = Image.new('RGBA', big.size, (0, 0, 0, 0))
        gl = Image.new('RGBA', big.size, (120, 90, 255, 0)); gl.putalpha(big.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .6)))
        out.alpha_composite(gl)
        g = Image.new('RGBA', big.size)
        col = np.zeros((big.height, big.width, 3), np.float32)
        yy = np.linspace(0, 1, big.height, dtype=np.float32)[:, None, None]
        c0, c2 = np.array(E.GRAD_LIGHT[0], np.float32), np.array(E.GRAD_LIGHT[2], np.float32)
        col = col + c0 + (c2 - c0) * yy
        g = Image.fromarray(col.astype(np.uint8)).convert('RGBA'); g.putalpha(big)
        out.alpha_composite(g)
        return out
    return C('darrow', mk)


def beat_c(ctx, t):
    # bar exit handled in beat_b; here: the tag + the arrow (same camera as B)
    if t >= SWING:
        k = clamp((t - SWING) / .12)
        u = t - SWING
        theta = 34 * (1 - eout(k)) + (-14 * math.exp(-u / .32) * math.sin(u * 2 * math.pi * 1.7) if u > .0 else 0)
        L = 470                                                            # string length (pivot -> hole)
        sc = .9
        if t >= O['MAIS2']:
            km = clamp((t - O['MAIS2']) / .12); sc = lerp(.9, .74, back(km, 2.0))
            sc *= 1 - .06 * K.bump(t - O['MAIS2'], .08)
        drop = 0.0
        if t >= DROP0:
            kd = clamp((t - DROP0) / (DROP1 - DROP0))
            ud = t - DROP1
            drop = 430 * (kd ** 2 if t < DROP1 else 1 + .06 * math.exp(-ud / .07) * math.cos(ud * 40))
            L += drop
            sc = lerp(.74, .58, eout(kd))
            if t >= DROP1: sc *= 1 + .06 * math.exp(-ud / .07) * math.cos(ud * 38)
            theta += 6 * math.sin(kd * 3) * (1 - kd)
        L = L - 260 * (1 - eout(k))                                      # drops in from above
        def hole(L_, th_):
            return PIVOT[0] + L_ * math.sin(math.radians(th_)), PIVOT[1] + L_ * math.cos(math.radians(th_))
        hx, hy = hole(L, theta)
        img = K.rotated(K.scale_im(tag_img(), sc), -theta) if abs(theta) > .1 else K.scale_im(tag_img(), sc)
        # string
        st = Image.new('RGBA', (W, 1200), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
        d.line([(PIVOT[0], 0), (hx, hy)], fill=(225, 222, 240, 200), width=3)
        ctx.add('screen', st, 0, 0, center=False, alpha=clamp(k * 3))
        if DROP0 <= t < DROP1 + .03:                                       # speed ghosts during the drop
            for g in (1, 2, 3):
                ctx.add('screen', img, hx, hy - drop * .16 * g, alpha=.28 / g)
        ctx.add('screen', img, hx, hy, alpha=clamp(k * 3))
    # the arrow: pops in on "MAIS", punches down on "BAIXO"
    if t >= O['MAIS2'] - .02:
        k = clamp((t - (O['MAIS2'] - .02)) / .16)
        y = 430
        if t >= DROP0:
            kd = clamp((t - DROP0) / (DROP1 - DROP0)); ud = t - DROP1
            y += 330 * (ein(kd) if t < DROP1 else 1 + .05 * math.exp(-ud / .08) * math.cos(ud * 36))
        ar = down_arrow()
        sc = .5 + .5 * back(k, 2.4)
        if t >= DROP1: sc *= 1 + .06 * math.exp(-(t - DROP1) / .07) * math.cos((t - DROP1) * 40)
        if DROP0 <= t < DROP1 + .04:
            for g in (1, 2, 3):
                ctx.add('screen', K.scale_im(ar, sc), 842, y - 50 * g, alpha=.25 / g)
        ctx.add('screen', K.scale_im(ar, sc), 842, y, alpha=clamp(k * 3))
        for i in range(3):                                                  # chevrons pulsing under it
            ph = ((t - O['MAIS2']) * 2.4 - i * .33) % 1.0
            a = (.25 + .6 * (1 - ph)) * clamp(k * 3 - i * .4) * .8
            cg = K.grad_fill(K.chevron(92, (255, 255, 255), .15))
            ctx.add('screen', cg, 842, y + 165 + i * 58 + 12 * ph, alpha=a)


# =========================================================================================== D: the portfolio wall
COLS, ROWS = 7, 8
TW, TH, GAP = 196, 294, 16
WALL_W, WALL_H = COLS * TW + (COLS - 1) * GAP, ROWS * TH + (ROWS - 1) * GAP
TEX = .5                                                                 # wall texture scale (soft = DOF)
ORDER = ['croissant', 'hyper_part', 'carousel1', 'burger', 'hyper_feel', 'website', 'watch', 'casa_house', 'hyper_ring',
         'latte', 'breakout_feed', 'hyper_orbit', 'oven', 'carousel2', 'tear_feel', 'motion_ui', 'hyper_grid', 'storefront',
         'hyper_leather', 'motion_logo', 'tear_explode', 'hyper_gold', 'breakout_touch', 'hyper_noise']
VIDEO_TILES = {(3, 4): ('croissant_pull', 0), (2, 3): ('hyper', 1)}       # (col, row) -> live video


def wall_names():
    def mk():
        rng = np.random.default_rng(5); out = {}; last = []
        pool = list(ORDER)
        for r in range(ROWS):
            for c in range(COLS):
                for _ in range(40):
                    n = pool[int(rng.integers(0, len(pool)))]
                    if n not in [out.get((c - 1, r)), out.get((c, r - 1)), out.get((c - 1, r - 1)), out.get((c + 1, r - 1))]: break
                out[(c, r)] = n
        return out
    return C('wnames', mk)


def tile_tex(name):
    w, h = int(TW * TEX), int(TH * TEX)
    return C(('ttex', name), lambda: K.card(K.tile(name, w, h), 9, border_a=.18))


def empty_tex(glow):
    w, h = int(TW * TEX), int(TH * TEX)
    def mk(g):
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        fc = tuple(int(a + (b - a) * g) for a, b in zip((22, 20, 34), (54, 44, 104)))
        d.rounded_rectangle((0, 0, w - 1, h - 1), 9, fill=fc + (255,), outline=(170, 160, 255, int(50 + 205 * g)), width=2 + int(g > .5))
        return im
    gq = round(glow * 8) / 8
    return C(('etex', gq), lambda: mk(gq))


def tile_center(c, r):
    return (c * (TW + GAP) + TW / 2) * TEX, (r * (TH + GAP) + TH / 2) * TEX


def video_tex(kind, t):
    w, h = int(TW * TEX), int(TH * TEX)
    if kind == 'croissant_pull':
        src_t = 1.0 + ((t - FLIP0) * .8) % 3.6
        fr = E.clip(E.CROISSANT_PULL, (540, 956)).at(src_t)
    else:
        src_t = 22.0 + (t - FLIP0) % 4.0
        fr = E.clip(E.HYPER, (360, 640)).at(src_t)
    return K.card(K.cover(fr, w, h), 9, border_a=.18)


def wall_texture(t):
    tw, th = int(WALL_W * TEX), int(WALL_H * TEX)
    names = wall_names()
    base = Image.new('RGBA', (tw, th), (12, 11, 20, 255))
    cxw, cyw = tw / 2, th * .58
    rmax = math.hypot(tw / 2, th * .6)
    for r in range(ROWS):
        for c in range(COLS):
            x, y = tile_center(c, r)
            d = math.hypot(x - cxw, y - cyw) / rmax
            # edge glow wave on "E UM" (before the flip)
            gw = clamp(1 - abs((t - O['E']) * 1.6 - d) / .25) if t < FLIP0 + .4 else 0
            f = clamp((t - FLIP0 - d * .42) / .11)
            if f <= 0:
                im = empty_tex(max(.15 * clamp((t - T30) / .3), gw))
            else:
                key = (c, r)
                im = video_tex(*VIDEO_TILES[key][:1], t) if key in VIDEO_TILES else tile_tex(names[key])
                if f < 1:
                    sx = max(.02, eout(f))
                    im = im.resize((max(1, int(im.width * sx)), im.height), Image.BILINEAR)
                    fl = Image.new('RGBA', im.size, (255, 255, 255, int(200 * (1 - f))))
                    im = im.copy(); im.alpha_composite(Image.composite(fl, Image.new('RGBA', im.size, (0, 0, 0, 0)), im.getchannel('A')))
            base.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    return base


def wall_pose(t):
    """(R, T) of the wall plane in camera space."""
    u = smooth((t - T30) / (END - T30))
    ry = lerp(-13, -6, u); rx = lerp(5, 3, u)
    R = K.rot3(rx, ry, 0)
    T = (lerp(30, -10, u), lerp(-60, -30, u), K.FOCAL * lerp(1.12, 1.06, u))
    return R, T


def grey_k(t):
    """the stamp drains the wall for a few frames, then the work flares back."""
    if t < SLAM: return 0.0
    return clamp((t - SLAM) / .03) * (1 - clamp((t - (BURST - .03)) / .05))


def wall_frame(t):
    tex = wall_texture(t)
    R, T = wall_pose(t)
    q = K.project(K.card_corners(WALL_W, WALL_H, R, T))
    bg = Image.new('RGBA', (W, H), (8, 8, 14, 255))
    K.put_warp(bg, tex, q)
    a = np.asarray(bg.convert('RGB'), np.float32)
    # grade: dim + vignette + floor shadow behind his body, glint sweep on "DIRIA", grey drain on the slam
    a *= wall_grade()
    gk = grey_k(t)
    if gk > 0:
        g = a.mean(2, keepdims=True); a = a + (g * .6 - a) * gk * .85
    fl = clamp((t - BURST) / .04) * (1 - clamp((t - BURST - .04) / .5))
    if fl > 0: a *= 1 + .55 * fl
    sw = (t - O['DIRIA']) / .55
    if 0 < sw < 1:
        a = a + glint_field(sw) * 70
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def wall_grade():
    def mk():
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        v = 1 - .62 * np.clip(((xx - 540) / 760) ** 2 + ((yy - 860) / 1150) ** 2 - .12, 0, 1)
        low = 1 - .45 * np.clip((yy - 1150) / 700, 0, 1)
        m = (v * low * .95).astype(np.float32)
        return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255
    return C('wgrade', mk)


def glint_field(k):
    yy, xx = np.mgrid[0:H // 8, 0:W // 8].astype(np.float32) * 8
    c = lerp(-600, 1700, k)
    band = np.exp(-(((xx + yy * .45) - c) / 120) ** 2)
    f = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    return f[..., None] * np.array([.9, .85, 1.0], np.float32)


# ---- the stamp, its cracks and shards
STAMP_C = (540, 1468)


def stamp_shards():
    """the stamp cut into ~11 polygons (seeded Voronoi-ish fan around the impact) -> [(piece RGBA, cx, cy)]"""
    def mk():
        st = SH.generic_stamp(760); w, h = st.size
        rng = np.random.default_rng(3)
        cx, cy = w * .47, h * .52
        n = 11; angs = np.sort(rng.uniform(0, 2 * math.pi, n))
        out = []
        for i in range(n):
            a0, a1 = angs[i], angs[(i + 1) % n] + (2 * math.pi if i == n - 1 else 0)
            R = max(w, h)
            mid = (a0 + a1) / 2; rr = rng.uniform(.18, .32) * min(w, h)
            poly = [(cx + math.cos(mid) * rr * .3, cy + math.sin(mid) * rr * .3)]
            for a in np.linspace(a0, a1, 6): poly.append((cx + math.cos(a) * R, cy + math.sin(a) * R))
            m = Image.new('L', (w, h)); ImageDraw.Draw(m).polygon(poly, fill=255)
            piece = st.copy(); piece.putalpha(Image.fromarray(np.minimum(np.asarray(st.getchannel('A')), np.asarray(m))))
            bb = piece.getbbox()
            if not bb: continue
            pc = piece.crop(bb)
            out.append((pc, bb[0] + pc.width / 2 - w / 2, bb[1] + pc.height / 2 - h / 2, mid))
        return out
    return C('shards', mk)


def crack_lines(k):
    """white-hot fracture lines racing from the impact through the stamp (RGBA, stamp-sized canvas)."""
    st = SH.generic_stamp(760); w, h = st.size
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = np.random.default_rng(9); cx, cy = w * .47, h * .52
    for i in range(9):
        a = rng.uniform(0, 2 * math.pi); L = rng.uniform(.5, 1.0) * max(w, h) * .6 * k
        x, y = cx, cy; pts = [(x, y)]
        for s in range(8):
            a += rng.normal(0, .25); x += math.cos(a) * L / 8; y += math.sin(a) * L / 8 * .6; pts.append((x, y))
        d.line(pts, fill=(255, 240, 240, 255), width=3)
    g = im.filter(ImageFilter.GaussianBlur(4)); out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im)
    return out


def draw_stamp(ctx, t):
    if t < O['QUE2'] or t > BURST + .7: return
    st = SH.generic_stamp(760)
    cx, cy = STAMP_C
    if t < STAMP_IN:                                                     # its shadow grows on the glass
        k = clamp((t - O['QUE2']) / (STAMP_IN - O['QUE2']))
        sh = C('stshadow', lambda: Image.merge('RGBA', [Image.new('L', st.size, 30), Image.new('L', st.size, 0), Image.new('L', st.size, 8),
                                                         st.getchannel('A').filter(ImageFilter.GaussianBlur(26))]))
        ctx.add('screen', K.scale_im(sh, lerp(1.5, 1.08, k)), cx + 20 * (1 - k), cy + 40 * (1 - k), alpha=.55 * k)
        return
    if t < SLAM:                                                         # falls (hook: 85 ms, 2.7 -> 1)
        u = clamp((t - STAMP_IN) / (SLAM - STAMP_IN)); kk = u ** 2.2
        s = lerp(2.7, 1.0, kk); rot = lerp(7, 0, kk)
        im = K.rotated(K.scale_im(st, s), rot)
        if s > 1.4: im = im.filter(ImageFilter.GaussianBlur((s - 1) * 3))
        ctx.add('screen', im, cx, cy, alpha=clamp(u * 2.2) * .9)
        return
    if t < BURST:                                                        # slammed, then cracking
        u = t - SLAM
        s = 1 + .035 * math.exp(-u / .05) * math.cos(u * 60)
        im = K.scale_im(st, s)
        if u < .12:
            halo = C('sthalo', lambda: st.filter(ImageFilter.GaussianBlur(7)))
            ctx.add('screen', K.scale_im(halo, 1.03), cx, cy, alpha=.5 * (1 - u / .12))
        if t >= CRACK:
            kc = eout((t - CRACK) / (BURST - CRACK))
            im = im.copy(); im.alpha_composite(K.scale_im(crack_lines(kc), s))
        ctx.add('screen', im, cx + 3 * math.sin(t * 90) * clamp((t - CRACK) / .02), cy, alpha=1)
        return
    # SHATTER: pieces fly outward + toward the lens, spinning, fading
    u = t - BURST
    kick = expo(u / .04)                                                 # instant separation (gaps on the 1st frame)
    for i, (pc, ox, oy, mid) in enumerate(stamp_shards()):
        sp = 900 + 900 * K.hrand(i, 7)
        dirx, diry = math.cos(mid), math.sin(mid) * .8
        kx = (58 + 40 * K.hrand(i, 14)) * kick
        x = cx + ox * (1 + 2.2 * u) + dirx * (sp * u + kx)
        y = cy + oy * (1 + 2.2 * u) + diry * (sp * u + kx) + 900 * u * u
        s = 1 + 2.4 * u * (.6 + K.hrand(i, 8))
        rot = (K.hrand(i, 9) - .5) * (420 * u + 22 * kick)
        a = 1 - clamp((u - .15) / .4)
        if a <= .02: continue
        im = K.rotated(K.scale_im(pc, s), rot)
        if u > .07: im = im.filter(ImageFilter.GaussianBlur(min(6, (u - .07) * 16)))
        ctx.add('screen', im, x, y, alpha=a)
    if u < .14:                                                          # white-hot core + glint where it broke
        kf = 1 - eout(u / .14)
        ctx.add('screen', K.glow_sprite(300, 190, (255, 214, 206), 40), cx, cy, alpha=.85 * kf)
        ctx.add('screen', K.scale_im(K.star(110), 1.4 + 1.6 * eout(u / .14)), cx, cy, alpha=kf)
    # red ink dust
    if u < .5:
        for i in range(26):
            ang = K.hrand(i, 11) * 2 * math.pi; dist = (200 + 700 * K.hrand(i, 12)) * eout(u / .45)
            sz = int(4 + 10 * K.hrand(i, 13))
            dot = K.glow_sprite(sz, sz, SH.STAMP_RED, 1.2)
            ctx.add('screen', dot, cx + math.cos(ang) * dist, cy + math.sin(ang) * dist * .6 + 300 * u * u, alpha=(1 - u / .5) * .9)


# ---- the burst of LUMARC work toward the lens
BURST_CARDS = ['croissant', 'hyper_part', 'carousel1', 'burger', 'website', 'casa_house', 'hyper_feel', 'latte',
               'hyper_ring', 'hyper_orbit', 'watch', 'carousel2', 'oven', 'motion_ui', 'tear_feel', 'hyper_gold']


def lens_tex():
    return C('lenstex', lambda: K.card(K.tile('hyper_part', 480, 720), 34, border_a=.3))


def burst_tex(name):
    return C(('btex', name), lambda: K.card(K.tile(name, 300, 450), 22, border_a=.3))


BURST_SEEDS = None


def burst_specs():
    """cards that burst out of the wall from behind him and fly past the lens: start (screen x, y), delay, spin."""
    def mk():
        rng = np.random.default_rng(17); out = []
        n = 30
        for i in range(n):
            ang = (i / n) * 2 * math.pi + rng.uniform(-.12, .12)
            r0 = rng.uniform(60, 330)
            x = 540 + math.cos(ang) * r0 * 1.1; y = 900 + math.sin(ang) * r0 * 1.3
            out.append(dict(x=x, y=y, ang=ang, name=BURST_CARDS[i % len(BURST_CARDS)], delay=rng.uniform(0, .07),
                            vz=3000 + 2200 * rng.uniform(), vr=900 + 900 * rng.uniform(),
                            rx=rng.uniform(-1, 1), ry=rng.uniform(-1, 1), rz=rng.uniform(-1, 1)))
        return out
    return C('bspecs', mk)


def draw_burst(ctx, t):
    """3-D: each card starts on the wall plane behind him (drawn BEHIND him while deeper than his plane), then crosses
    it and flies past the lens in front of him."""
    u = t - BURST
    if u < 0: return
    Zw = K.FOCAL * 1.12
    z, X_, Y_ = cam_xy(ctx.cam)
    items = []
    for i, sp in enumerate(burst_specs()):
        v = u - sp['delay']
        if v <= 0: continue
        X0, Y0 = (sp['x'] - 540) * Zw / K.FOCAL, (sp['y'] - 960) * Zw / K.FOCAL
        Z = Zw - sp['vz'] * (v + 1.0 * v * v)
        if Z < 240: continue
        X = X0 + math.cos(sp['ang']) * sp['vr'] * v
        Y = Y0 + math.sin(sp['ang']) * sp['vr'] * v * .9 - 150 * v
        R = K.rot3(sp['rx'] * 170 * v, sp['ry'] * 230 * v, sp['rz'] * 130 * v)
        corners = K.card_corners(TW, TH, R, (X, Y, Z))
        items.append((Z, sp['name'], corners, v))
    items.sort(key=lambda it: -it[0])
    for Z, name, corners, v in items:
        q = K.project(corners)
        if q[:, 0].max() < -50 or q[:, 0].min() > W + 50 or q[:, 1].max() < -50 or q[:, 1].min() > H + 50: continue
        span = max(q[:, 0].max() - q[:, 0].min(), q[:, 1].max() - q[:, 1].min())
        if span > 2300: continue
        tex = burst_tex(name)
        if span > 800: tex = K.scale_im(tex, .5)
        r = K.warp(tex, q)
        if r is None: continue
        p, x0, y0 = r
        blur = clamp((Zw * .5 - Z) / (Zw * .42)) * 9
        if blur > .8: p = p.filter(ImageFilter.GaussianBlur(blur))
        a = clamp(v / .03) * (1 - clamp((span - 1500) / 800))
        if Z > K.FOCAL * .97:                       # still behind his plane: world layer, behind him
            wx = ctx.cam['x'] + (x0 - X_) / z; wy = ctx.cam['y'] + (y0 - Y_) / z
            ctx.add('behind', K.scale_im(p, 1 / z), wx, wy, center=False, alpha=a)
        else:
            ctx.add('screen', p, x0, y0, center=False, alpha=a)


def beat_d(ctx, t):
    P = ctx.post
    u = t - T30
    ctx.bg_img = wall_frame(t)
    win = clamp(u / .1)
    z = 1.0 + .06 * smooth(u / 2.4) + .03 * K.bump(t - O['CONTEUDO'], .14)
    dx, dy = K.shake(t, SLAM, 22., tau=.08, f=18.)
    dx2, dy2 = K.shake(t, BURST, 30., tau=.12, f=14., seed=1.3)
    ctx.cam = dict(z=max(1.0, z + .1 * (1 - eout(win))), x=540., y=960., dx=dx + dx2, dy=dy + dy2, rot=0.)
    ctx.avatar['y'] = 30
    gk = grey_k(t)
    if gk > 0: ctx.avatar['bright'] = 1 - .15 * gk
    # light from the wall on him: violet/warm spill + rim (via a front glow behind his shoulders)
    draw_stamp(ctx, t)
    draw_burst(ctx, t)
    if t >= BURST:
        v = t - BURST
        P['flash'] = .08 * (1 - clamp(v / .06)); P['flash_col'] = (255, 240, 236)
        P['bright'] = 1 + .40 * (1 - eout(v / .16))
        P['zoom_blur'] = .25 * (1 - clamp(v / .07))
        P['rgb'] = 7 * (1 - clamp(v / .12))
    if t >= SLAM and t < SLAM + .1:
        P['flash'] = max(P['flash'], .3 * (1 - (t - SLAM) / .1)); P['flash_col'] = (255, 90, 90)
    # the last card flies out of the wall (behind him, upper right) into the lens -> the cut (3-D, tilted, blurred)
    if t >= LENS0:
        k = clamp((t - LENS0) / (END - 1 / 30 - LENS0)); d = k ** 1.25
        Zw = K.FOCAL * 1.12; Z = lerp(Zw, 270., d)
        sx, sy = lerp(880, 600, smooth(k)), lerp(500, 930, smooth(k))
        R = K.rot3(lerp(10, 0, eout(k)), lerp(-32, 0, eout(k)), lerp(8, 0, eout(k)))
        q = K.project(K.card_corners(TW, TH, R, ((sx - 540) * Z / K.FOCAL, (sy - 960) * Z / K.FOCAL, Z)))
        r = K.warp(lens_tex(), q, clip=(-40, -40, W + 40, H + 40))
        if r is not None:
            p_, x0, y0 = r
            sc = K.FOCAL / Z
            if sc > 1.6: p_ = p_.filter(ImageFilter.GaussianBlur(min(14, (sc - 1.6) * 2.4)))
            a = clamp(k * 6)
            z, X_, Y_ = cam_xy(ctx.cam)
            if Z > K.FOCAL * .97:                                             # still behind his plane
                ctx.add('behind', K.scale_im(p_, 1 / z), ctx.cam['x'] + (x0 - X_) / z, ctx.cam['y'] + (y0 - Y_) / z, center=False, alpha=a)
            else:
                ctx.add('screen', p_, x0, y0, center=False, alpha=a)
    P['vignette'] = .42


# =========================================================================================== draw
def draw(ctx, lt, t):
    ctx.captions = False
    if t < T28:
        beat_a(ctx, t)
        return
    if t < T30:
        beat_b(ctx, t)
        beat_c(ctx, t)
        K.caps_layer(ctx, t, PAGES_B + PAGES_C, y=1430)
        return
    beat_d(ctx, t)
    K.caps_layer(ctx, t, PAGES_D, y=1235)
