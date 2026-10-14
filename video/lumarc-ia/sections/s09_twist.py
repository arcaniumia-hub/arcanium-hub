"""s09 — THE TWIST (62.84–69.32).  "Ah… e o resto desse vídeo?" / "A edição, os efeitos, a trilha…" /
"Também foi feito noventa por cento com IA."

A  62.84 JUMP — he LEANS IN: a tight, intimate close-up (z 1.8 -> 1.95, slight dutch that levels out), the studio drops
   into a soft dark DOF, warm key — a playful secret.  "AH…" (62.90).  63.42 "e o" the picture starts to WARBLE like a
   tape (tracking noise creeps in) and on "RESTO" (63.55) a VHS REWIND whips backwards through THIS film — real frames
   of every section rendered again without captions (the portfolio burst, the wall, the price tag, the delivery bar,
   RESULTADO, the AI-first stage, the agent, the clones, the house, the feed crack, the estalo set swaps, the dancing
   text, the cinema bars, the croissant painting, the face scan, the gauge, the generic wall…) — ONE look per frame,
   tracking band, chroma bleed, head-switching noise, ◀◀ REW OSD; 64.30 it clunks to a stop on the film's first frame
   (▶ PLAY).
B  64.48 JUMP — the frame becomes a 3-D layer stack (EXPLODED VIEW): on "A" (64.525) the camera orbits, the studio plate
   and his keyed layer separate in depth (true parallax), and ON EACH WORD a new labelled layer slides out of the
   stack: "EDIÇÃO" (64.715) an editor timeline (tracks, clips with real thumbnails, voice waveform, running playhead,
   frame guides); "EFEITOS" (65.60 / stressed 65.755) glass + glow + particles + flare; "TRILHA" (66.50) a live audio
   waveform + spectrum pulsing.  66.84 the stack slams back together into a flat frame (66.92 JUMP).
C  66.92 — "TAMBÉM FOI FEITO" (captions) while an odometer "0%" rises BEHIND his head and an AI scan line climbs the
   frame from the bottom (everything below it turns holographic: scanlines, cool grade, dot grid — him included).
   67.76 "NOVENTA" the counter races and LANDS 90 on the stressed "VEN" (68.025) with the scan line at 90 % of the frame
   (hit, flash, shock ring, the digits flood with the LUMARC gradient); 68.51 "CEN-to" the % pops; 68.70 "COM IA" the
   label "FEITO COM IA" clicks in beside the number; 68.95 a small warm note "+10% gente com bom gosto" writes on with
   a gold brush underline while the untouched top band of the frame glows warm (the human 10 %).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _F_kit as K

START, END = E.span(31, 33)                      # 62.84 – 69.32
T31, T32, T33 = (E.TL[i]['t0'] for i in (31, 32, 33))     # 62.84, 64.48, 66.92 (all JUMP)
W, H = E.W, E.H
clamp, eout, ein, back, lerp, smooth, expo, eio = E.clamp, E.eout, E.ein, E.back, K.lerp, K.smooth, K.expo, K.eio

# word onsets measured on src/tight16k.raw (5 ms STFT, 3 band envelopes; out/F/sp_d..sp_h, sp_z3, sp_z4)
O = dict(AH=62.90, AH_END=63.08, E_O=63.42, RESTO=63.55, DESSE=63.80, VIDEO=64.00, VI=64.05, VID_END=64.26,
         A=64.525, EDICAO=64.60, DI=64.715, CAO=64.96, OS=65.44, EFEITOS=65.60, FEI=65.755, A2=66.33, TRILHA=66.50,
         TRI_END=66.80, TAMBEM=67.00, BEM=67.21, FOI=67.35, FEITO=67.54, NOVENTA=67.76, VEN=68.025, POR=68.30,
         CENTO=68.40, CEN=68.51, COM=68.70, IA=68.90, IA_END=69.05)

REW0, REW1 = O['RESTO'], 64.30                    # the rewind
LAND = O['VEN']                                    # counter lands 90
COLLAPSE0, COLLAPSE1 = 66.84, T33

# frames of THIS film the rewind passes through (newest first); last = the film's first look
# ONE output frame per look (22 frames between REW0 and REW1), so every look in the list is actually seen:
# burst, wall, tag, bar, RESULTADO, team cards, agent, AI-FIRST, logo, feed crack, house, clones, set swap, dancing
# type, cinema, croissant painting, face scan, gauge, IA?, caption card, stamp, the slop wall (held under PLAY)
RW = [62.40, 61.40, 59.95, 58.86, 57.40, 52.60, 47.90, 45.50, 44.20, 42.95, 40.66, 38.70, 36.30, 34.70, 32.60,
      27.20, 19.30, 14.80, 11.60, 6.90, 4.30, 0.50]

CUES = [
    (T31, 'whoosh', {'gain': -14}),                            # lean in (tight cut)
    (O['AH'], 'heart', {'gain': -16}),                         # a soft intimate thump under "Ah…"
    (O['E_O'], 'glitch', {'gain': -14}),                       # tape warble creeps in
    (REW0 - .02, 'rewind', {'dur': REW1 - REW0 + .02, 'gain': -2}),   # VHS REWIND
    (REW0, 'scratch', {'gain': -12}),
    (REW1, 'click', {'gain': -4}),                             # tape clunks to a stop
    (REW1 + .02, 'thud', {'gain': -12}),
    (T32, 'swipe', {'gain': -8}),                              # the frame splits into layers
    (O['A'], 'swoosh_up', {'gain': -9}),                       # orbit
    (O['DI'] - .03, 'whoosh', {'gain': -10}),                  # EDIÇÃO layer slides out
    (O['DI'], 'pop', {'gain': -6}),
    (O['DI'] + .02, 'click', {'gain': -12}),
    (O['EFEITOS'] + .08, 'whoosh', {'gain': -10}),             # EFEITOS layer
    (O['FEI'], 'shimmer', {'gain': -6}),
    (O['FEI'], 'pop', {'gain': -7}),
    (O['TRILHA'] - .03, 'whoosh', {'gain': -10}),              # TRILHA layer
    (O['TRILHA'], 'pop', {'gain': -6}),
    (O['TRILHA'] + .02, 'sub', {'gain': -8}),
    (COLLAPSE0, 'swoosh_up', {'gain': -12}),                   # stack slams together
    (COLLAPSE1, 'impact', {'gain': -5}),
    (O['TAMBEM'], 'scan', {'dur': LAND - O['TAMBEM'], 'gain': -9}),   # AI scan line climbs
    (O['NOVENTA'] - .02, 'counter', {'dur': LAND - O['NOVENTA'] + .02, 'gain': -4}),
    (LAND, 'impact', {'gain': 0}),                             # 90 lands on "VEN"
    (LAND, 'boom', {'gain': -4}),
    (LAND + .02, 'shimmer', {'gain': -10}),
    (O['CEN'], 'pop', {'gain': -6}),                           # %
    (O['COM'], 'click', {'gain': -6}),                         # FEITO COM IA label
    (O['IA'], 'ding', {'note': 'E6', 'gain': -11}),
    (68.95, 'shimmer', {'gain': -12}),                         # +10% gente com bom gosto (warm)
]

F_, T_ = False, True
PAGES_A = [(O['AH'] - .04, O['E_O'] - .03, [('AH…', O['AH'], T_)]),
           (O['E_O'] - .03, T32, [('E', O['E_O'], F_), ('O', O['E_O'] + .07, F_), ('RESTO', O['RESTO'], F_),
                                  ('DESSE', O['DESSE'], F_), ('VÍDEO?', O['VIDEO'], T_)])]
PAGES_C = [(O['TAMBEM'] - .04, O['NOVENTA'] - .02, [('TAMBÉM', O['TAMBEM'], F_), ('FOI', O['FOI'], F_), ('FEITO', O['FEITO'], F_)])]


def C(k, fn): return K.C(('s09',) + (k if isinstance(k, tuple) else (k,)), fn)


# =========================================================================================== A: lean in + REWIND
def rew_index(t):
    """which RW frame shows at t: one look per output frame (integer frame maths: a pure function of t)."""
    j0 = math.ceil(REW0 * E.FPS - 1e-6)
    return min(len(RW) - 1, max(0, int(round(t * E.FPS)) - j0))


def osd(ctx, t):
    if t < REW0 - .02: return
    if t < REW1:
        im = K.vhs_osd('REW', 66, 'rew')
        blink = 1.0 if int((t - REW0) * 6) % 2 == 0 else .75
        ctx.add('screen', im, 86, 236, center=False, alpha=blink)
    else:
        ctx.add('screen', K.vhs_osd('PLAY', 66, 'play'), 86, 236, center=False)


def beat_a(ctx, t):
    P = ctx.post
    ctx.captions = False
    if t < REW0:
        u = t - T31
        z = 1.80 + .16 * eout(u / .75)
        ctx.cam = dict(z=z, x=535., y=880., dx=0., dy=-8 * (1 - eout(u / .6)), rot=math.radians(-1.8 * (1 - eout(u / .7))))
        ctx.bg_dim = .38; ctx.bg_blur = 5.0
        P['vignette'] = .62; P['sat'] = .95
        warm = 1.0
        # tape warble creeping in on "e o"
        kv = .55 * clamp((t - O['E_O']) / (REW0 - O['E_O']))
        if kv > .01:
            ctx.wrap = lambda fr, kv=kv: K.vhs(fr, t, kv, band_y=1700 - 1300 * kv, band_h=70, jitter=.6).convert('RGBA')
        P['grain'] = 1.0
    else:
        # full-frame flashes of this film, rewinding
        i = rew_index(t) if t < REW1 else len(RW) - 1
        fr = K.film_frame(RW[i])
        ctx.full = fr.convert('RGBA')
        u = clamp((t - REW0) / (REW1 - REW0))
        spd = 1.0 if t < REW1 else 0.0
        kv = 1.0 if t < REW1 else .75 - .35 * clamp((t - REW1) / .18)
        band = (1800 - ((t - REW0) * 5200) % 2100) if t < REW1 else 1500 - 900 * clamp((t - REW1) / .12)
        ctx.wrap = lambda f, kv=kv, band=band, spd=spd: rewind_fx(f, t, kv, band, spd)
        P['vignette'] = .5; P['grain'] = 1.4
        if t >= REW1 and t < REW1 + .06: P['flash'] = .2 * (1 - (t - REW1) / .06)
    osd(ctx, t) if t >= REW0 - .02 else None
    K.caps_layer(ctx, t, PAGES_A, y=1500)


def rewind_fx(fr, t, k, band, spd):
    im = K.vhs(fr, t, k, band_y=band, band_h=110 if spd else 80, jitter=1.4 if spd else .8, chroma=1.3)
    if spd:      # rewind: picture rolls a little + head-switching noise along the bottom + a second thin band
        a = np.asarray(im, np.float32)
        j = int(round(t * E.FPS))
        roll = int(28 * math.sin(j * 1.7))
        a = np.roll(a, roll, 0)
        hs = slice(H - 70, H)
        a[hs] = np.roll(a[hs], 36 + (j * 13) % 40, 1) * .8 + 30
        y2 = int((band + 700) % H); a[y2:y2 + 6] = a[y2:y2 + 6] * .4 + 150
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im.convert('RGBA')


# =========================================================================================== B: EXPLODED VIEW
TXW, TXH = 540, 960                               # layer texture size (half res)
LAYERS = ['plate', 'him', 'edit', 'fx', 'track']
SLOT = {'plate': 2.0, 'him': 1.0, 'edit': 0.0, 'fx': -1.0, 'track': -2.0}      # local z (x spacing), + = deeper
DEPLOY = {'edit': O['EDICAO'] - .04, 'fx': O['EFEITOS'] - .02, 'track': O['TRILHA'] - .05}
LABEL = {'edit': ('A', 'EDIÇÃO,'), 'fx': ('OS', 'EFEITOS,'), 'track': ('A', 'TRILHA…')}
LABEL_T = {'edit': (O['A'], O['EDICAO']), 'fx': (O['OS'], O['EFEITOS']), 'track': (O['A2'], O['TRILHA'])}


def void():
    """the space the layers float in: deep violet gradient, a perspective floor grid, a soft glow."""
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        col = np.zeros((H, W, 3), np.float32) + np.array([9, 8, 15], np.float32)
        r = np.sqrt(((xx - 560) / 700) ** 2 + ((yy - 820) / 900) ** 2)
        col += (np.clip(1 - r, 0, 1) ** 2)[..., None] * np.array([40, 30, 96], np.float32)
        im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
        g = Image.new('L', (W, H)); d = ImageDraw.Draw(g)
        hy = 1290                                                   # horizon of the floor grid
        for i in range(-14, 15):
            d.line([(540 + i * 34, hy), (540 + i * 330, H + 300)], fill=70, width=2)
        for j in range(1, 14):
            y = hy + (j / 13) ** 2.2 * (H - hy + 200)
            d.line([(0, y), (W, y)], fill=int(36 + 40 * j / 13), width=2)
        fade = Image.fromarray((np.clip((yy - hy) / 500, 0, 1) * np.clip(1 - np.abs(xx - 540) / 700, 0, 1) * 255).astype(np.uint8))
        g = Image.fromarray(np.minimum(np.asarray(g), np.asarray(fade)))
        grid = Image.new('RGB', (W, H), (130, 110, 255))
        im.paste(grid, (0, 0), g.point(lambda v: int(v * .55)))
        return im
    return C('void', mk)


def frame_border(im, a=.32):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, im.width - 2, im.height - 2), 14, outline=(235, 232, 255, int(255 * a)), width=2)
    return im


def plate_tex():
    def mk():
        p = E.studio().resize((TXW, TXH), Image.LANCZOS).convert('RGBA')
        p = E.rounded(p, 14)
        return frame_border(p, .25)
    return C('plate', mk)


def him_tex(ctx, t):
    av = K.av_frame(ctx, t)
    im = av.resize((TXW, TXH), Image.BILINEAR) if av is not None else Image.new('RGBA', (TXW, TXH), (0, 0, 0, 0))
    out = Image.new('RGBA', (TXW, TXH), (255, 255, 255, 8)); out.alpha_composite(im)
    return frame_border(out, .22)


def edit_static():
    """the editor overlay (static parts): frame guides + an NLE timeline panel with tracks and clips."""
    def mk():
        im = Image.new('RGBA', (TXW, TXH), (190, 180, 255, 10)); d = ImageDraw.Draw(im)
        # frame guides: corner brackets + safe area + centre cross
        L = 34
        for (x, y, sx, sy) in ((16, 16, 1, 1), (TXW - 17, 16, -1, 1), (16, TXH - 17, 1, -1), (TXW - 17, TXH - 17, -1, -1)):
            d.line([(x, y), (x + sx * L, y)], fill=(255, 255, 255, 210), width=3); d.line([(x, y), (x, y + sy * L)], fill=(255, 255, 255, 210), width=3)
        d.rectangle((40, 110, TXW - 41, 820), outline=(255, 255, 255, 60), width=1)
        d.line([(TXW / 2 - 12, TXH / 2), (TXW / 2 + 12, TXH / 2)], fill=(255, 255, 255, 120), width=1)
        d.line([(TXW / 2, TXH / 2 - 12), (TXW / 2, TXH / 2 + 12)], fill=(255, 255, 255, 120), width=1)
        # REC dot + "EDIT" chip at the top-left of the frame
        # NLE panel
        px0, py0, px1, py1 = 18, 640, TXW - 18, 930
        pnl = Image.new('RGBA', (px1 - px0, py1 - py0), (14, 12, 26, 228)); pnl = E.rounded(pnl, 14)
        im.alpha_composite(pnl, (px0, py0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((px0, py0, px1, py1), 14, outline=(170, 160, 255, 120), width=2)
        # ruler ticks
        for i in range(0, 60):
            x = 70 + i * 7.6
            d.line([(x, py0 + 12), (x, py0 + (24 if i % 5 == 0 else 18))], fill=(200, 200, 230, 150), width=1)
        f = E.font(16, 700)
        tracks = [('V3', 'fx'), ('V2', 'him'), ('V1', 'work'), ('A1', 'wave'), ('A2', 'music')]
        ty = py0 + 36
        rng = np.random.default_rng(4)
        thumbs = ['croissant', 'hyper_part', 'website', 'burger', 'casa_house', 'hyper_feel', 'latte']
        for k, (lab, kind) in enumerate(tracks):
            y = ty + k * 47; h = 38
            d.text((28, y + 10), lab, font=f, fill=(210, 205, 240, 230))
            x = 66
            j = 0
            while x < px1 - 16:
                w = int(rng.uniform(46, 120)) if kind != 'music' else 420
                x1 = min(px1 - 14, x + w)
                if kind == 'fx':
                    g = E.gradient(max(2, x1 - x), h, E.GRAD).convert('RGBA'); g = E.rounded(g, 6); im.alpha_composite(K.fade(g, .9), (int(x), y))
                elif kind in ('him', 'work'):
                    nm = 'storefront' if kind == 'him' else thumbs[j % len(thumbs)]
                    th = K.tile(nm, 90, 60).resize((max(2, x1 - x), h), Image.BILINEAR).convert('RGBA')
                    im.alpha_composite(E.rounded(th, 6), (int(x), y))
                    ImageDraw.Draw(im).rounded_rectangle((x, y, x1, y + h), 6, outline=(255, 255, 255, 120), width=1)
                elif kind == 'wave':
                    ImageDraw.Draw(im).rounded_rectangle((x, y, x1, y + h), 6, fill=(60, 120, 255, 120))
                    for xx in range(int(x) + 2, int(x1) - 2, 3):
                        a = (math.sin(xx * .31) * .5 + math.sin(xx * .07 + 1) * .5) * (h * .4) * (.3 + .7 * abs(math.sin(xx * .021)))
                        ImageDraw.Draw(im).line([(xx, y + h / 2 - a), (xx, y + h / 2 + a)], fill=(200, 225, 255, 230), width=1)
                else:
                    ImageDraw.Draw(im).rounded_rectangle((x, y, x1, y + h), 6, fill=(150, 80, 255, 110))
                    for xx in range(int(x) + 2, int(x1) - 2, 2):
                        a = (.35 + .65 * abs(math.sin(xx * .045))) * h * .32
                        ImageDraw.Draw(im).line([(xx, y + h / 2 - a), (xx, y + h / 2 + a)], fill=(230, 200, 255, 200), width=1)
                x = x1 + 4; j += 1
        return frame_border(im, .5)
    return C('edit', mk)


def edit_tex(t):
    im = edit_static().copy(); d = ImageDraw.Draw(im)
    u = clamp((t - DEPLOY['edit']) / (COLLAPSE0 - DEPLOY['edit']))
    x = 70 + u * (TXW - 100)
    d.line([(x, 652), (x, 920)], fill=(255, 255, 255, 240), width=2)
    d.polygon([(x - 8, 646), (x + 8, 646), (x, 660)], fill=(255, 255, 255, 255))
    if int(t * 4) % 2 == 0: d.ellipse((30, 40, 44, 54), fill=(255, 70, 80, 230))
    return im


PARTS = [(K.hrand(i, 31) * TXW, K.hrand(i, 32) * TXH, 1 + 2.4 * K.hrand(i, 33), 8 + 22 * K.hrand(i, 34)) for i in range(70)]


def fx_static():
    def mk():
        im = Image.new('RGBA', (TXW, TXH), (200, 190, 255, 12))
        for (x, y, w, h, col, b, a) in ((120, 260, 260, 260, (110, 80, 255), 60, .55), (430, 620, 220, 220, (60, 110, 255), 50, .5),
                                        (300, 820, 300, 160, (170, 90, 255), 60, .4)):
            gl = K.glow_sprite(w, h, col, b, a); im.alpha_composite(gl, (int(x - gl.width / 2), int(y - gl.height / 2)))
        # frosted UI card + a glass pill
        card = Image.new('RGBA', (300, 170), (255, 255, 255, 34)); card = E.rounded(card, 22)
        ImageDraw.Draw(card).rounded_rectangle((1, 1, 298, 168), 22, outline=(255, 255, 255, 150), width=2)
        im.alpha_composite(card, (40, 120))
        pill = Image.new('RGBA', (220, 52), (255, 255, 255, 40)); pill = E.rounded(pill, 26)
        ImageDraw.Draw(pill).rounded_rectangle((1, 1, 218, 50), 26, outline=(255, 255, 255, 170), width=2)
        im.alpha_composite(pill, (280, 700))
        # anamorphic flare streak
        fl = Image.new('RGBA', (TXW, 40), (0, 0, 0, 0)); a = np.zeros((40, TXW), np.float32)
        yy = np.arange(40, dtype=np.float32)[:, None] - 20; xx = np.arange(TXW, dtype=np.float32)[None, :]
        a = np.exp(-(yy / 2.2) ** 2) * np.exp(-((xx - 330) / 210) ** 2) + .4 * np.exp(-(yy / 7) ** 2) * np.exp(-((xx - 330) / 120) ** 2)
        fl = Image.fromarray(np.dstack([np.full((40, TXW, 3), (200, 210, 255), np.float32), np.clip(a, 0, 1) * 255]).astype(np.uint8), 'RGBA')
        im.alpha_composite(fl, (0, 380))
        return frame_border(im, .4)
    return C('fx', mk)


def fx_tex(t):
    im = fx_static().copy()
    for i, (x, y, r, sp) in enumerate(PARTS):
        yy = (y - (t - T32) * sp * 3) % TXH
        tw = .4 + .6 * abs(math.sin(t * 3 + i))
        g = K.glow_sprite(int(r * 2 + 2), int(r * 2 + 2), (220, 210, 255), max(.6, r * .5), 1.0)
        K.paste(im, g, x, yy, alpha=tw)
    st = K.star(40)
    for i, (x, y) in enumerate(((330, 400), (120, 205), (455, 640))):
        tw = (.5 + .5 * math.sin(t * 7 + i * 2)) ** 3
        K.paste(im, K.scale_im(st, .5 + .6 * tw), x, y, alpha=.4 + .6 * tw)
    return im


def voice_env():
    def mk():
        x = np.fromfile(E.os.path.join(E.SRC, 'tight16k.raw'), np.float32); h = 160
        r = np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')[::h])
        return np.clip((20 * np.log10(r + 1e-6) + 55) / 40, 0, 1)
    return C('venv', mk)


def track_tex(t):
    im = Image.new('RGBA', (TXW, TXH), (190, 200, 255, 10))
    env = voice_env(); j = int(t * 100)
    e = float(env[min(j, len(env) - 1)]) * .7 + .3 * (.5 + .5 * math.cos((t - O['TRILHA']) * 2 * math.pi * 2.2)) ** 4
    # oscilloscope waveform (3 glowing passes)
    pts = []
    for i in range(0, TXW - 40, 3):
        x = 20 + i; u = i / (TXW - 40)
        win = math.sin(math.pi * u) ** 1.2
        y = 500 + win * (110 * e + 18) * (math.sin(u * 31 + t * 19) * .6 + math.sin(u * 77 - t * 27) * .3 + math.sin(u * 9 + t * 5) * .4)
        pts.append((x, y))
    lay = Image.new('RGBA', (TXW, TXH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line(pts, fill=(120, 140, 255, 255), width=9)
    gl = lay.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(gl); im.alpha_composite(gl)
    l2 = Image.new('RGBA', (TXW, TXH), (0, 0, 0, 0)); ImageDraw.Draw(l2).line(pts, fill=(235, 230, 255, 255), width=3)
    im.alpha_composite(l2)
    # spectrum bars
    d = ImageDraw.Draw(im)
    n = 28
    for b in range(n):
        x = 34 + b * (TXW - 68) / n
        hgt = (16 + 150 * e * (.35 + .65 * abs(math.sin(b * 1.7 + t * (6 + b % 5))))) * (1 - abs(b - n / 2) / n * .8)
        col = tuple(int(c) for c in np.array(E.GRAD_LIGHT[0]) + (np.array(E.GRAD_LIGHT[2]) - np.array(E.GRAD_LIGHT[0])) * (b / n))
        d.rounded_rectangle((x, 880 - hgt, x + (TXW - 68) / n - 5, 880), 3, fill=col + (230,))
    return frame_border(im, .45)


def explode(t):
    """0 (flat frame) -> 1 (exploded stack) -> 0 (collapse)."""
    e = expo((t - (O['A'] - .02)) / .5)
    if t >= COLLAPSE0: e *= 1 - ein((t - COLLAPSE0) / (COLLAPSE1 - COLLAPSE0))
    return e


def deploy(name, t):
    if name in ('plate', 'him'): return 1.0
    k = clamp((t - DEPLOY[name]) / .2)
    return k


FB = 1150.0                                        # stack-camera focal (stronger perspective than the engine's)
ANCHOR = {'edit': (.93, .80), 'fx': (.70, .16), 'track': (.95, .52)}   # label anchor on each layer (texture u, v)
LABEL_Y = {'edit': 1360, 'fx': 470, 'track': 915}


def stack_pose(t):
    e = explode(t)
    orbit = smooth((t - T32) / (COLLAPSE0 - T32))
    ry = (-37 + 8 * orbit) * e; rx = (10 - 3 * orbit) * e; rz = -2 * e
    R = K.rot3(rx, ry, rz)
    Zc = FB * (1 + .50 * e - .08 * orbit * e)
    Tc = (lerp(0, -45, e), lerp(0, -55, e), Zc)
    return e, R, Tc, 410 * e


def layer_zlocal(name, t, spacing):
    z = SLOT[name] * spacing
    if name not in ('plate', 'him'):
        dk = deploy(name, t)
        z = lerp(SLOT['him'] * spacing - 10, z, eout(dk))
    return z


def beat_b(ctx, t):
    P = ctx.post
    ctx.captions = False
    e, R, Tc, spacing = stack_pose(t)
    if e <= .002:                                           # exactly flat: the normal frame (plate + him)
        out = E.studio().convert('RGBA'); av = K.av_frame(ctx, t)
        if av is not None: out.alpha_composite(av)
        ctx.full = out; return
    out = void().convert('RGBA')
    items = []
    for name in LAYERS:
        dk = deploy(name, t)
        if dk <= .01: continue
        coll = 1 - (clamp((t - COLLAPSE0) / (COLLAPSE1 - COLLAPSE0)) if name not in ('plate', 'him') else 0)
        corners = K.card_corners(W, H, R, Tc, local=(0, 0, layer_zlocal(name, t, spacing)))
        items.append((corners[:, 2].mean(), name, corners, clamp(dk * 1.6) * coll))
    items.sort(key=lambda it: -it[0])
    for zc, name, corners, a in items:
        if a <= .01: continue
        q = K.project(corners, f=FB)
        if name == 'plate': tex = plate_tex()
        elif name == 'him': tex = him_tex(ctx, t)
        elif name == 'edit': tex = edit_tex(t)
        elif name == 'fx': tex = fx_tex(t)
        else: tex = track_tex(t)
        if name in ('edit', 'fx', 'track') and t >= DEPLOY[name] and t < DEPLOY[name] + .3:   # arrival glow
            gk = 1 - (t - DEPLOY[name]) / .3
            tex = tex.copy(); ImageDraw.Draw(tex).rounded_rectangle((1, 1, TXW - 2, TXH - 2), 14, outline=(210, 200, 255, int(255 * gk)), width=7)
        K.put_warp(out, tex, q, alpha=a)
    # labels (screen space) on the right, each tied by a leader line to a point of its own layer
    lay = ImageDraw.Draw(out)
    for name in ('edit', 'fx', 'track'):
        art, word = LABEL[name]; ta, tw = LABEL_T[name]
        if t < tw - .03 or deploy(name, t) <= 0: continue
        uu, vv = ANCHOR[name]
        P3 = (np.array([(uu - .5) * W, (vv - .5) * H, layer_zlocal(name, t, spacing)]) @ R.T + np.array(Tc))[None]
        ax, ay = K.project(P3, f=FB)[0]
        k = clamp((t - (tw - .03)) / .14)
        coll = 1 - clamp((t - COLLAPSE0) / .05)
        if coll <= 0: continue
        lab = label_img(art, word, True)
        sc = (.7 + .3 * back(k, 2.4)) * (1 + .05 * K.bump(t - tw - .1, .12))
        lw = lab.width * sc
        lx = W - 36 - lw / 2 + 60 * (1 - eout(k)); ly = LABEL_Y[name]
        # leader: dot on the layer -> elbow -> label
        ex = lx - lw / 2 + 22
        lk = clamp(k * 1.6)
        pts = [(ax, ay), (ax + (ex - ax) * .45, ly), (ex, ly)]
        segs = [(pts[0], pts[1]), (pts[1], pts[2])]
        L = sum(math.dist(p0, p1) for p0, p1 in segs); run = L * lk; acc = 0
        for p0, p1 in segs:
            d_ = math.dist(p0, p1)
            if run <= acc: break
            f_ = min(1, (run - acc) / max(1, d_))
            lay.line([p0, (p0[0] + (p1[0] - p0[0]) * f_, p0[1] + (p1[1] - p0[1]) * f_)], fill=(215, 205, 255, int(220 * coll)), width=3)
            acc += d_
        dot = K.glow_sprite(18, 18, (230, 225, 255), 2.0)
        K.paste(out, dot, ax, ay, alpha=coll)
        ring = K.ring_sprite(13, 1.6, .9)
        K.paste(out, ring, ax, ay, alpha=coll * clamp(k * 2))
        ctx.add('screen', K.scale_im(lab, sc), lx, ly, alpha=clamp(k * 3) * coll)
    ctx.full = out
    P['vignette'] = .35
    if t >= COLLAPSE1 - 1 / 30: P['bright'] = 1.30; P['flash'] = .05          # exposure punch (no grey veil)


def label_img(art, word, word_on):
    def mk():
        f1, f2 = E.font(44, 600), E.font(64, 900)
        a_w = f1.getlength(art); w_w = f2.getlength(word)
        pw = int(a_w + w_w + 46 + 18); ph = 96
        im = Image.new('RGBA', (pw + 40, ph + 40), (0, 0, 0, 0))
        sh = Image.new('L', im.size); ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + pw, 26 + ph), ph // 2, fill=200)
        shi = Image.new('RGBA', im.size, (4, 2, 14, 0)); shi.putalpha(sh.filter(ImageFilter.GaussianBlur(12))); im.alpha_composite(shi)
        body = Image.new('RGBA', (pw, ph), (24, 20, 44, 236)); body = E.rounded(body, ph // 2)
        ImageDraw.Draw(body).rounded_rectangle((1, 1, pw - 2, ph - 2), ph // 2 - 1, outline=(190, 180, 255, 170), width=2)
        im.alpha_composite(body, (20, 20))
        d = ImageDraw.Draw(im)
        _, t1, _, b1 = f1.getbbox('A'); _, t2, _, b2 = f2.getbbox('E')
        d.text((20 + 23, 20 + ph / 2 - (t1 + b1) / 2 + 2), art, font=f1, fill=(225, 222, 245))
        if word_on:
            m = Image.new('L', im.size); ImageDraw.Draw(m).text((20 + 23 + a_w + 18, 20 + ph / 2 - (t2 + b2) / 2), word, font=f2, fill=255)
            g = E.gradient(im.width, im.height, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m); im.alpha_composite(g)
        return im
    return C(('label', art, word, word_on), mk)


# =========================================================================================== C: 90% COM IA
LINE_TOP = int(H * .10)                           # 90 % of the frame (from the bottom) = y 192
DIG_SIZE = 330
NUM_CX, NUM_CY = 420, 540


def digit_strip(size, grad):
    """vertical strip of digits 0..9,0 (for the odometer); returns (RGBA, cell height)."""
    def mk():
        f = E.font(size, 900); _, t, _, b = f.getbbox('0123456789'); ch = int((b - t) * 1.28)
        w = int(max(f.getlength(str(d)) for d in range(10))) + 8
        m = Image.new('L', (w, ch * 12)); d = ImageDraw.Draw(m)
        for i in range(12):
            dg = str(i % 10)
            d.text(((w - f.getlength(dg)) / 2, i * ch + (ch - (b - t)) / 2 - t), dg, font=f, fill=255)
        if grad:
            g = E.gradient(w, ch * 12, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m); return g, ch, m
        c = Image.new('RGBA', m.size, E.WHITE + (0,)); c.putalpha(m); return c, ch, m
    return C(('dstrip', size, grad), mk)


def wheel(pos, size, grad, blur=0.0):
    """odometer wheel showing digit `pos` (float: 3.5 = half way 3 -> 4)."""
    strip, ch, _ = digit_strip(size, grad)
    y = (pos % 10) * ch
    win = strip.crop((0, int(y), strip.width, int(y) + ch))
    if blur > .5: win = K.vsmear(win, blur)
    # fade the wheel edges (cylinder)
    a = np.asarray(win.getchannel('A'), np.float32)
    yy = np.linspace(-1, 1, ch, dtype=np.float32)[:, None]
    a = a * np.clip(1.25 - np.abs(yy) ** 3 * 1.2, 0, 1)
    win = win.copy(); win.putalpha(Image.fromarray(a.astype(np.uint8))); return win


def count_value(t):
    if t < O['TAMBEM']: return 0.0
    if t < O['NOVENTA']: return 18 * eio((t - O['TAMBEM']) / (O['NOVENTA'] - O['TAMBEM']))
    if t < LAND: return lerp(18, 90, ein(clamp((t - O['NOVENTA']) / (LAND - O['NOVENTA']))) * .55 + .45 * clamp((t - O['NOVENTA']) / (LAND - O['NOVENTA'])))
    u = t - LAND
    return 90 + .35 * math.exp(-u / .06) * math.sin(u * 50)


def number_img(t):
    """the odometer number '<tens><units>%' -> RGBA (centre-aligned to the units digit block)."""
    v = count_value(t)
    landed = t >= LAND
    spd = 0.0
    if O['NOVENTA'] <= t < LAND: spd = 1.0
    units = v % 10 if v < 89.999 else 0.0 + (v - 90)
    tens_pos = math.floor(v / 10 + 1e-6)
    fr = v % 10
    if fr > 9: tens_pos += smooth((fr - 9))                     # the tens wheel turns as units pass 9 -> 0
    if v >= 89.999: tens_pos = 9 + (v - 90) / 10
    g = landed
    uw = wheel(units, DIG_SIZE, g, blur=60 * spd)
    tw = wheel(tens_pos, DIG_SIZE, g, blur=12 * spd) if v >= 9.5 else None
    pct, _ = K.display('%', int(DIG_SIZE * .62), 900, 'grad' if landed else 'white', glow=.0, shadow=0)
    if t >= O['CEN']: pct = K.scale_im(pct, 1 + .22 * K.bump(t - O['CEN'], .12))
    gap = -6
    wdt = uw.width * 2 + pct.width + gap
    im = Image.new('RGBA', (wdt + 40, uw.height + 40), (0, 0, 0, 0))
    x = 20
    if tw is not None and (tens_pos > .02 or v >= 9.5):
        im.alpha_composite(tw, (x, 20))
    x += uw.width + gap
    im.alpha_composite(uw, (x, 20)); x += uw.width + gap
    K.paste(im, pct, x + pct.width / 2 - 30, 20 + uw.height * .56)
    return im


def number_layers(t):
    """(number RGBA with glow + shadow, scale)"""
    im = number_img(t)
    a = im.getchannel('A')
    out = Image.new('RGBA', (im.width + 120, im.height + 120), (0, 0, 0, 0))
    sh = Image.new('RGBA', out.size, (4, 2, 14, 0)); sa = Image.new('L', out.size); sa.paste(a, (60, 74))
    sh.putalpha(sa.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .7))); out.alpha_composite(sh)
    gk = .45 + (.45 * (1 - clamp((t - LAND) / .5)) if t >= LAND else 0)
    ga = Image.new('L', out.size); ga.paste(a, (60, 60))
    gl = Image.new('RGBA', out.size, (120, 90, 255, 0)); gl.putalpha(ga.filter(ImageFilter.GaussianBlur(30)).point(lambda v, gk=gk: int(v * gk)))
    out.alpha_composite(gl); out.alpha_composite(im, (60, 60))
    return out


def scan_assets():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        rows = (1 - .16 * ((np.arange(H) % 4) < 1)).astype(np.float32)[:, None, None]
        dots = (((xx % 24) < 2) & ((yy % 24) < 2)).astype(np.float32)[..., None]
        # the scan line sprite (1080 x 160): hot core + violet glow below (the processed side)
        y = np.arange(160, dtype=np.float32)[:, None] - 60
        a = np.exp(-(y / 2.0) ** 2) + .55 * np.exp(-(np.clip(y, 0, None) / 38)) * (y > 0) + .25 * np.exp(-(np.clip(-y, 0, None) / 12)) * (y <= 0)
        a = np.repeat(np.clip(a, 0, 1), W, 1)
        xs = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        c0, c2 = np.array(E.GRAD_LIGHT[0], np.float32), np.array(E.GRAD_LIGHT[2], np.float32)
        col = c0 + (c2 - c0) * xs[..., None]
        core = np.exp(-(y / 1.6) ** 2)[..., None]
        col = col * (1 - core) + 255 * core
        line = Image.fromarray(np.dstack([np.broadcast_to(col, (160, W, 3)), a * 255]).astype(np.uint8), 'RGBA')
        return rows, dots, line
    return C('scan', mk)


def scan_y(t):
    v = count_value(t)
    return H - (H - LINE_TOP) * clamp(v / 90)


def ai_treat(fr, t, yl, k):
    """everything below the scan line turns 'AI': cool holographic grade, scanlines, dot grid."""
    rows, dots, _ = scan_assets()
    y0 = int(max(0, min(H, yl)))
    if y0 >= H: return fr
    alpha = fr.getchannel('A') if fr.mode == 'RGBA' else None
    a = np.asarray(fr.convert('RGB'), np.float32)
    reg = a[y0:]
    lum = reg.mean(2, keepdims=True)
    tint = lum * np.array([.74, .86, 1.36], np.float32) + np.array([10, 8, 40], np.float32)
    reg = reg + (tint - reg) * .72 * k
    reg = reg * (1 - (1 - rows[y0:]) * 1.6 * k)
    reg = reg + dots[y0:] * 70 * k
    hh = min(240, H - y0)                                        # fresh-scan glow right under the line
    reg[:hh] += (np.exp(-np.arange(hh, dtype=np.float32) / 70)[:, None, None] * np.array([40, 30, 110], np.float32)) * k
    a[y0:] = reg
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    if alpha is not None: out.putalpha(alpha)
    return out


def warm_band(fr, k):
    if k <= .01: return fr
    a = np.asarray(fr.convert('RGB'), np.float32)
    band = a[:LINE_TOP]
    yy = np.linspace(0, 1, LINE_TOP, dtype=np.float32)[:, None, None]
    band = band * (1 + .25 * k) + np.array([60, 36, 6], np.float32) * k * (.35 + .65 * yy)
    a[:LINE_TOP] = band
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def note_img():
    """'+10% gente com bom gosto' — warm gold '+10%' + white text, gold brush underline."""
    def mk():
        f1, f2 = E.font(54, 800), E.font(50, 500)
        s1, s2 = '+10%', 'gente com bom gosto'
        w1, w2 = f1.getlength(s1), f2.getlength(s2)
        pw = int(w1 + 16 + w2) + 40; ph = 110
        im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
        m = Image.new('L', (pw, ph)); d = ImageDraw.Draw(m)
        _, t1, _, b1 = f1.getbbox('H')
        d.text((20, 30 - t1), s1, font=f1, fill=255)
        m2 = Image.new('L', (pw, ph)); ImageDraw.Draw(m2).text((20 + w1 + 16, 30 - t1 + 4), s2, font=f2, fill=255)
        sh = Image.new('RGBA', (pw, ph), (6, 3, 2, 0)); sh.putalpha(Image.fromarray(np.maximum(np.asarray(m), np.asarray(m2))).filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * .8)))
        im.alpha_composite(sh, (0, 3))
        gold = Image.new('RGBA', (pw, ph), (255, 200, 110, 0)); gold.putalpha(m); im.alpha_composite(gold)
        wt = Image.new('RGBA', (pw, ph), E.WHITE + (0,)); wt.putalpha(m2); im.alpha_composite(wt)
        return im
    return C('note', mk)


def brush_line(w, k):
    """gold brush-stroke underline (dry-brush texture), revealed left -> right by k."""
    def mk():
        h = 30; rng = np.random.default_rng(8)
        xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]; yy = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
        prof = np.clip(1 - np.abs(yy + .2 * np.sin(xx * 6)) / (.55 + .3 * np.sin(xx * 3 + 1) ** 2), 0, 1)
        streak = (rng.random((h, 1)) > .25).astype(np.float32) * .6 + .4
        taper = np.clip(xx / .05, 0, 1) * np.clip((1 - xx) / .2, 0, 1) ** .7
        a = prof * streak * taper
        col = np.zeros((h, w, 3), np.float32) + np.array([255, 196, 104], np.float32)
        return Image.fromarray(np.dstack([col, np.clip(a, 0, 1) * 255]).astype(np.uint8), 'RGBA')
    im = C(('brush', w), mk)
    if k >= 1: return im
    cw = max(1, int(w * k)); out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(im.crop((0, 0, cw, im.height)), (0, 0)); return out


def ia_label(t):
    """'FEITO COM IA' — two-line stack beside the number."""
    def mk():
        f = E.font(66, 800); s1, s2 = 'FEITO', 'COM IA'
        w = int(max(f.getlength(s1), f.getlength(s2))) + 40; h = 170
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        m1 = Image.new('L', (w, h)); ImageDraw.Draw(m1).text((20, 8), s1, font=f, fill=255)
        m2 = Image.new('L', (w, h)); ImageDraw.Draw(m2).text((20, 86), s2, font=f, fill=255)
        sh = Image.new('RGBA', (w, h), (4, 2, 14, 0)); sh.putalpha(Image.fromarray(np.maximum(np.asarray(m1), np.asarray(m2))).filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .8)))
        im.alpha_composite(sh, (0, 3))
        c = Image.new('RGBA', (w, h), E.WHITE + (0,)); c.putalpha(m1); im.alpha_composite(c)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m2); im.alpha_composite(g)
        return im
    return C('ialabel', mk)


def beat_c(ctx, t):
    P = ctx.post
    ctx.captions = False
    u = t - T33
    land = t - LAND
    z = 1.04 + .04 * smooth(u / 2.4) + .035 * K.bump(land, .14) * (t >= LAND)
    dx, dy = K.shake(t, LAND, 14., tau=.08, f=16.)
    dx2, dy2 = K.shake(t, T33, 12., tau=.06, f=18.)
    ctx.cam = dict(z=z, x=540., y=960., dx=dx + dx2, dy=dy + dy2, rot=0.)
    # number BEHIND his head (screen layer + his cutout on top)
    if t >= O['TAMBEM'] - .04:
        k = clamp((t - (O['TAMBEM'] - .04)) / .2)
        im = number_layers(t)
        sc = (.7 + .3 * back(k, 1.8)) * (1 + .07 * K.bump(land, .12) * (t >= LAND))
        ctx.add('screen', K.scale_im(im, sc), NUM_CX + 40, NUM_CY + 10, alpha=clamp(k * 2.5) * (.8 if t < LAND else 1))
        if t >= LAND and land < .5:
            ring = K.ring_sprite(120 + 600 * eout(land / .5), 4, .9 * (1 - land / .5))
            ctx.add('screen', ring, NUM_CX + 40, NUM_CY, alpha=1)
        cut = _cutout(ctx, t)
        if cut is not None: ctx.add('screen', ai_treat(cut, t, scan_y(t), .9 * clamp((t - O['TAMBEM']) / .1)), 0, 0, center=False)
    # FEITO COM IA label beside the number
    if t >= O['COM'] - .02:
        k = clamp((t - (O['COM'] - .02)) / .14)
        lab = ia_label(t)
        ctx.add('screen', K.scale_im(lab, .6 + .4 * back(k, 2.4)), 872, 528 + 20 * (1 - k), alpha=clamp(k * 3))
        if t >= O['IA'] and t < O['IA'] + .3:
            gl = K.glow_sprite(240, 120, (130, 100, 255), 30)
            ctx.add('screen', gl, 872, 570, alpha=.6 * (1 - (t - O['IA']) / .3))
    # +10% gente com bom gosto (warm, small) + gold brush underline
    if t >= 68.93:
        k = clamp((t - 68.93) / .16)
        nt = note_img()
        ctx.add('screen', nt, 540, 1338 + 14 * (1 - eout(k)), alpha=clamp(k * 2.5))
        bl = brush_line(int(nt.width * .9), eout(clamp((t - 68.98) / .22)))
        ctx.add('screen', bl, 540, 1392)
    # AI scan: below the line the frame is "AI"; the top 10 % stays human (warm once the note appears)
    yl = scan_y(t)
    kai = clamp((t - O['TAMBEM']) / .1)
    warm = clamp((t - 68.93) / .25)
    def wrap(fr, yl=yl, kai=kai, warm=warm):
        fr = ai_treat(fr, t, yl, .9 * kai)
        fr = warm_band(fr, .8 * warm)
        _, _, line = scan_assets()
        pulse = 1.0 + (.6 * (1 - clamp((t - LAND) / .4)) if t >= LAND else 0)
        if kai > .01: K.paste(fr, line, 0, yl - 60, center=False, alpha=min(1, .9 * kai * pulse))
        return fr
    ctx.wrap = wrap
    K.caps_layer(ctx, t, PAGES_C, y=1430)
    if t >= LAND:
        P['flash'] = .07 * (1 - clamp(land / .07)); P['flash_col'] = (225, 215, 255)
        P['bright'] = 1 + .50 * (1 - eout(land / .16))                            # exposure punch on "VEN"
        P['rgb'] = 6 * (1 - clamp(land / .1))
    if u < .08: P['bright'] = max(P['bright'], 1 + .28 * (1 - u / .08))
    P['vignette'] = .36


def _cutout(ctx, t):
    av = K.av_frame(ctx, t)
    if av is None: return None
    cam = ctx.cam; z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return E.zoom(av, z, (cam['x'], cam['y']), dx=X - cam['x'], dy=Y - cam['y'], rot=cam['rot'])


# =========================================================================================== draw
def draw(ctx, lt, t):
    if t < T32: beat_a(ctx, t)
    elif t < T33: beat_b(ctx, t)
    else: beat_c(ctx, t)
