"""s05 — SHOWREEL A (28.00–37.04).  "Deixa eu te mostrar o que acontece quando a IA tá na mão certa. Um produto com cara
de comercial de cinema. Um texto que dança no ritmo da sua fala. Um cenário que muda num estalo."

SEG 11  SHOWREEL MODE (28.00 JUMP).  Three frames of a burnt film leader flash, then a medium close-up seen through a
        camera viewfinder: rack focus in, corner brackets, blinking ● REC, running timecode, voice-reactive audio meter.
        "MOSTRAR" (28.41): the thin wide-tracked title SHOWREEL tracks open above him with a gradient hairline.
        "ACONTECE" (29.03): letterbox bars slide in.  "IA" (29.58): the autofocus box locks onto his face (tracked) with
        an "IA" chip; "MÃO" (30.07): the box jumps to his hand (tracked); "CERTA" (30.235): HARD SNAP — crash zoom into
        his hand, white flash, RGB split, a ✓ badge (the score drops).  30.40: the frame shrinks into a frame of a 35 mm
        film strip (sprockets, edge print), which pulls down a frame (projector rattle, motion blur) onto the first frame
        of the showreel and scales up into it.
SEG 12  CINEMA (30.76 JUMP, voice-over).  Full-frame cuts on the words, letterbox bars stepping in on every cut (the
        frame becomes more "cinema" each cut): "UM PRODUTO" SILENCE ONE assembling from gold particles (hyper film) ·
        "COM CARA DE" a macro of the earcup leather + gold ring with a light sweep · "COMERCIAL" the croissant
        pull-apart, speed-ramped · "CINEMA" (32.30) the bars SLAM to a true 2.39:1 scope strip — the hero shot with an
        anamorphic flare — and "C I N E M A" opens in thin wide-tracked type, credit line under the strip.  Film grain,
        gate weave, subtitles in the picture.
SEG 13  KINETIC TYPE (32.96 JUMP, captions off).  The scope bars open onto him (smaller, room above his head); every
        word of the line is set as big type that dances on its measured syllables: UM pops · TEXTO's letters drop in
        and bounce on TEX/TO · QUE wobbles · DANÇA (gradient, huge) rises from BEHIND his head and dances a letter wave
        on DAN/ÇA · NO RITMO: RITMO's letters stretch with his real voice envelope over an equalizer that sits behind
        him · DA SUA FALA: FALA stretches with the voice while his actual waveform scrolls behind him.  The camera sways
        with the syllables, the studio light breathes with his voice.
SEG 14  SET SWAPS (35.24 JUMP).  He stays keyed while the location swaps on the syllables — Paris (35.24), café
        (CEnário 35.42), beach (náRIO 35.66), boardroom (QUE 35.93), home studio (muDA 36.24) — each plate with DOF and
        him regraded to it (tint, exposure, key side, rim colour, light wrap), snap push-ins.  "es-" winds up (push-in,
        drained colour) and on "esTAlo" (36.70) a finger SNAP: white flash, zoom-blur shock ring, and the golden rooftop
        sunset.  Captions: engine look with measured onsets.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _C_kit as K

START, END = E.span(11, 14)                         # 28.00 – 37.04
T12, T13, T14 = E.TL[12]['t0'], E.TL[13]['t0'], E.TL[14]['t0']    # 30.76, 32.96, 35.24 (all JUMP)
W, H = E.W, E.H
clamp, lerp, expo, sio, eout, back, decay, hop = K.clamp, K.lerp, K.expo, K.sio, K.eout, K.back, K.decay, K.hop

# word / syllable onsets measured on src/tight16k.raw (5 ms RMS envelope + high-band ratio + spectrogram, out/C/spec_*.png;
# re-checked in review: TEXTO = /t/ burst 33.225, QUE = /k/ burst 33.56, NO = nasal 34.10, DA = /d/ release 34.55, QUE = /k/ 35.92)
O = dict(DEIXA=28.09, EU=28.29, TE=28.365, MOSTRAR=28.41, O=28.84, QUE=28.95, ACONTECE=29.03, QUANDO=29.38, A=29.52,
         IA=29.58, TA=29.89, NA=29.96, MAO=30.07, CERTA=30.235, CER_V=30.41, END11=30.68,
         UM=30.875, PRODUTO=31.00, COM=31.38, CARA=31.55, DE=31.87, COMERCIAL=31.93, DE2=32.27, CINEMA=32.30, END12=32.80,
         UM3=33.035, TEXTO=33.225, TO=33.46, QUE3=33.56, DANCA=33.76, DAN=33.79, CA=33.93, NO=34.10, RITMO=34.21,
         MO=34.42, DA=34.55, SUA=34.63, FALA=34.79, FA=34.91, LA=35.01, END13=35.13,
         UM4=35.33, CENARIO=35.42, RIO=35.66, QUE4=35.92, MUDA=36.00, DA4=36.24, NUM=36.31, ESTALO=36.36, TA4=36.70,
         END14=36.97)

def pose_t(T):
    """first timeline frame that shows the take's pose after the jump at T (the engine maps 30 fps -> nearest 25 fps
    source frame, so a jump can surface one frame before its TL segment starts)."""
    for j in range(int(T * 30) - 3, int(T * 30) + 4):
        if E.Avatar._k_of(j / 30) / 25 >= T - 1e-6: return j / 30 - 1e-6
T14V = pose_t(T14)       # 35.2333: the set swaps start on the frame where the pose jumps
T_OUT = pose_t(END)      # 37.0333: last frame already shows s06's pose -> an exit smear frame covers it
T_MCU = 28.10            # leader flash -> viewfinder MCU
T_STRIP = 30.40          # the frame shrinks into the film strip
T_PULL0, T_PULL1 = 30.47, 30.63                  # pull-down; then 4 frames of scale-up that land on full frame at T12
SNAP = O['TA4']

# ---------------------------------------------------------------- sound
CUES = [
    (START, 'film', {'dur': .16, 'gain': -8}),                    # leader flicker
    (START, 'whoosh', {'gain': -13}),
    (T_MCU, 'click', {'gain': -10}),                              # AF / REC on
    (O['MOSTRAR'], 'shimmer', {'gain': -13}),                     # SHOWREEL title tracks open
    (O['ACONTECE'], 'swipe', {'gain': -11}),                      # letterbox bars
    (O['IA'], 'tick', {'gain': -8}),                              # AF lock (double beep)
    (O['IA'] + .08, 'tick', {'gain': -10}),
    (O['MAO'], 'tick', {'gain': -8}),                             # AF jumps to the hand
    (O['CERTA'], 'impact', {'gain': -2}),                         # HARD SNAP (the drop)
    (O['CERTA'], 'sub', {'gain': -6}),
    (T_STRIP, 'film', {'dur': .36, 'gain': -9}),                  # projector strip
    (T_PULL0 + .02, 'whoosh', {'gain': -10}),                     # pull-down
    (T12, 'zoom', {'gain': -11}),                                 # into the cinema shots
    (O['COM'], 'swipe', {'gain': -12}),
    (O['COMERCIAL'], 'whoosh', {'gain': -11, 'pan': .3}),
    (O['CINEMA'], 'boom', {'gain': -4}),                          # scope bars slam
    (O['CINEMA'] + .03, 'shimmer', {'gain': -11}),                # anamorphic flare
    (T13, 'swoosh_up', {'gain': -12}),                            # bars open on him
    (O['UM3'], 'pop', {'gain': -15}),
    (O['TEXTO'], 'flick', {'gain': -13}),
    (O['TO'], 'pop', {'gain': -13}),
    (O['QUE3'], 'pop', {'gain': -15, 'pan': .3}),
    (O['DANCA'], 'swoosh_up', {'gain': -9}),                      # DANÇA rises from behind him
    (O['DAN'] + .02, 'pop', {'gain': -11, 'pan': -.3}),
    (O['CA'], 'pop', {'gain': -11, 'pan': .3}),
    (O['NO'], 'tick', {'gain': -13}),
    (O['RITMO'], 'flick', {'gain': -10}),
    (O['DA'], 'pop', {'gain': -15}),
    (O['FALA'], 'swoosh_up', {'gain': -12}),
    (T14V, 'swipe', {'gain': -10}),                               # Paris
    (O['CENARIO'], 'flick', {'gain': -9, 'pan': -.3}),            # café
    (O['RIO'], 'flick', {'gain': -9, 'pan': .3}),                 # beach
    (O['QUE4'], 'flick', {'gain': -9, 'pan': -.3}),               # boardroom
    (O['DA4'], 'flick', {'gain': -9, 'pan': .3}),                 # home studio
    (O['ESTALO'], 'riser', {'to': SNAP, 'gain': -15}),            # wind-up
    (SNAP, 'snap', {'gain': 0}),                                  # finger SNAP -> rooftop sunset
    (SNAP, 'impact', {'gain': -9}),
    (SNAP + .03, 'shimmer', {'gain': -12}),
]

# ---------------------------------------------------------------- captions (measured onsets)
PAGES11 = [
    (O['DEIXA'] - .02, O['O'] - .02, [('DEIXA', O['DEIXA'], False), ('EU', O['EU'], False), ('TE', O['TE'], False), ('MOSTRAR', O['MOSTRAR'], False)]),
    (O['O'] - .02, O['QUANDO'] - .02, [('O', O['O'], False), ('QUE', O['QUE'], False), ('ACONTECE', O['ACONTECE'], False)]),
    (O['QUANDO'] - .02, O['TA'] - .02, [('QUANDO', O['QUANDO'], False), ('A', O['A'], False), ('IA', O['IA'], False)]),
    (O['TA'] - .02, T12, [('TÁ', O['TA'], False), ('NA', O['NA'], False), ('MÃO', O['MAO'], True), ('CERTA.', O['CERTA'], True)]),
]
PAGES12 = [
    (O['UM'] - .03, O['COM'] - .02, [('UM', O['UM'], False), ('PRODUTO', O['PRODUTO'], True)]),
    (O['COM'] - .02, O['COMERCIAL'] - .02, [('COM', O['COM'], False), ('CARA', O['CARA'], False), ('DE', O['DE'], False)]),
    (O['COMERCIAL'] - .02, O['CINEMA'] - .01, [('COMERCIAL', O['COMERCIAL'], False), ('DE', O['DE2'], False)]),
]
PAGES14 = [
    (O['UM4'] - .03, O['QUE4'] - .02, [('UM', O['UM4'], False), ('CENÁRIO', O['CENARIO'], False)]),
    (O['QUE4'] - .02, O['NUM'] - .02, [('QUE', O['QUE4'], False), ('MUDA', O['MUDA'], False)]),
    (O['NUM'] - .02, END, [('NUM', O['NUM'], False), ('ESTALO.', O['ESTALO'], True)]),
]


def paste_all(fr, items):
    for im, x, y in items: K.paste(fr, im, x, y)


def cam_screen(cam):
    """world -> screen mapping of an engine camera dict (rotation ignored; engine clamp maths)."""
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return lambda px, py: (X + (px - cam['x']) * z, Y + (py - cam['y']) * z)


def bars(fr, top, bot=None, col=(4, 4, 7)):
    bot = top if bot is None else bot
    d = ImageDraw.Draw(fr)
    if top > .5: d.rectangle((0, 0, W, int(round(top)) - 1), fill=col + (255,))
    if bot > .5: d.rectangle((0, H - int(round(bot)), W, H), fill=col + (255,))
    return fr


# ================================================================ SEG 11 — showreel mode
def leader_base():
    def mk():
        rng = np.random.default_rng(11)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - 540) / 700) ** 2 + ((yy - 960) / 1100) ** 2)
        lum = 1.0 - .55 * np.clip(r - .25, 0, 1) ** 1.4
        base = np.array([178, 166, 146], np.float32)[None, None] * lum[..., None]
        base += (rng.random((H // 8, W // 8)).repeat(8, 0).repeat(8, 1)[..., None] - .5) * 10
        im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
        dk = (46, 40, 34); lt = (236, 230, 218)
        d.line((0, 960, W, 960), fill=dk, width=5); d.line((540, 0, 540, H), fill=dk, width=5)
        for R, w_, c in ((420, 10, lt), (372, 5, lt), (300, 3, dk)):
            d.ellipse((540 - R, 960 - R, 540 + R, 960 + R), outline=c, width=w_)
        lab = K.tracked('SHOWREEL', 64, 600, dk, .38)
        im.paste(lab, (540 - lab.width // 2, 960 + 120 - lab.height // 2), lab)
        lg = K.tracked('LUMARC', 40, 700, dk, .5)
        im.paste(lg, (540 - lg.width // 2, 960 - 150 - lg.height // 2), lg)
        return im
    return K.C('leader', mk)


def leader_frame(t):
    j = int(round((t - START) * E.FPS))                   # 0, 1, 2
    im = leader_base().copy().convert('RGBA')
    ang = 360 * (t - START) / .25                         # sweep hand
    ov = Image.new('L', (W, H)); d = ImageDraw.Draw(ov)
    d.pieslice((540 - 1400, 960 - 1400, 540 + 1400, 960 + 1400), -90, -90 + ang, fill=95)
    dark = Image.new('RGBA', (W, H), (30, 24, 20, 0)); dark.putalpha(ov); im.alpha_composite(dark)
    rng = np.random.default_rng(100 + j)
    d2 = ImageDraw.Draw(im)
    for _ in range(26):                                   # dust + hairs
        x, y = rng.integers(0, W), rng.integers(0, H); r = rng.integers(2, 7)
        d2.ellipse((x - r, y - r, x + r, y + r), fill=(20, 16, 12, 200))
    for _ in range(3):
        x = int(rng.integers(60, W - 60)); d2.line((x, 0, x + int(rng.integers(-30, 30)), H), fill=(250, 246, 236, 120), width=2)
    for _ in range(2):
        x, y = int(rng.integers(100, W - 100)), int(rng.integers(100, H - 100))
        d2.arc((x - 60, y - 40, x + 60, y + 40), int(rng.integers(0, 180)), int(rng.integers(200, 330)), fill=(30, 24, 20, 230), width=2)
    # burn: hot orange light leak growing over the 3 frames (the last frame almost burns out)
    k = (.25, .55, 1.0)[min(2, max(0, j))]
    leak = burn_map()
    im = K.add_light(im, leak, k)
    off = (int(rng.integers(-6, 7)), int(rng.integers(-10, 11)))
    out = Image.new('RGBA', (W, H), (10, 8, 6, 255)); out.alpha_composite(im, off)
    return out


def burn_map():
    def mk():
        h2, w2 = H // 4, W // 4
        yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32) * 4
        a = np.exp(-(((xx - 1150) / 520) ** 2 + ((yy - 260) / 900) ** 2))
        b = np.exp(-(((xx + 80) / 300) ** 2 + ((yy - 1500) / 600) ** 2)) * .6
        L = a[..., None] * np.array([255, 150, 50], np.float32) * 1.3 + b[..., None] * np.array([255, 90, 40], np.float32) \
            + (a ** 3)[..., None] * np.array([255, 240, 200], np.float32)
        return np.asarray(Image.fromarray(np.clip(L, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
    return K.C('burn', mk)


def corner_box(w, h, arm=56, lw=4, col=(255, 255, 255), a=1.0):
    w, h = max(2 * arm + 4, int(w)), max(2 * arm + 4, int(h))
    def mk():
        im = Image.new('L', (w + 2 * lw, h + 2 * lw)); d = ImageDraw.Draw(im); o = lw; v = int(255 * a)
        for (x, y, sx, sy) in ((o, o, 1, 1), (o + w, o, -1, 1), (o, o + h, 1, -1), (o + w, o + h, -1, -1)):
            d.line((x, y, x + sx * arm, y), fill=v, width=lw); d.line((x, y, x, y + sy * arm), fill=v, width=lw)
        out = Image.new('RGBA', im.size, col + (0,)); out.putalpha(im); return out
    return K.C(('cbox', w // 2 * 2, h // 2 * 2, arm, lw, col, round(a, 2)), mk)


def timecode(t):
    """HH:MM:SS:FF of the timeline (fixed-width cells)."""
    f = int(round(t * E.FPS)); s = f // 30; tc = f'00:{s // 60:02d}:{s % 60:02d}:{f % 30:02d}'
    def ch(c): return K.tracked(c, 36, 500, E.WHITE, 0)
    cw = 25; im = Image.new('RGBA', (cw * len(tc) + 40, 70), (0, 0, 0, 0))
    for i, c in enumerate(tc):
        g = ch(c); im.alpha_composite(g, (20 + i * cw + (cw - g.width) // 2 + 2, (70 - g.height) // 2))
    return im


def meter(level, lvl2):
    """voice-reactive stereo audio meter (two thin bars)."""
    im = Image.new('RGBA', (190, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for row, lv in enumerate((level, lvl2)):
        y = 6 + row * 18
        n = 16
        for i in range(n):
            on = i < int(lv * n + .5)
            c = (120, 230, 150) if i < 11 else ((240, 210, 90) if i < 14 else (240, 80, 80))
            d.rectangle((i * 11 + 4, y, i * 11 + 12, y + 9), fill=c + ((235,) if on else (50,)))
    return im


def ia_chip():
    def mk():
        txt = K.tracked('IA', 40, 800, E.WHITE, .12)          # >= 34 px (README minimum)
        w, h = txt.width - 14, 62
        g = E.gradient(w, h, E.GRAD).convert('RGBA'); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=255)
        g.putalpha(m); g.alpha_composite(txt, ((w - txt.width) // 2, (h - txt.height) // 2)); return g
    return K.C('ia_chip', mk)


def check_badge(d=74):
    def mk():
        S = 3; n = d * S; im = E.gradient(n, n, E.GRAD).convert('RGBA'); m = Image.new('L', (n, n))
        ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255); im.putalpha(m)
        dd = ImageDraw.Draw(im); w_ = int(n * .09)
        dd.line([(n * .28, n * .52), (n * .44, n * .68), (n * .73, n * .35)], fill=(255, 255, 255, 255), width=w_, joint='curve')
        return im.resize((d, d), Image.LANCZOS)
    return K.C(('check', d), mk)


def bars11(t):
    return 190 * expo((t - O['ACONTECE']) / .26) if t >= O['ACONTECE'] else 0.0


def cam11(t, face_hit):
    """viewfinder camera: MCU with a slow push + handheld drift; on CERTA a crash punch-in that drags his face (as it
    was at the hit, take coordinates) to the upper centre of the frame."""
    z0 = 1.22 + .12 * sio((t - T_MCU) / 2.1)
    dx = 5 * math.sin(1.7 * t) + 3 * math.sin(3.3 * t + 1); dy = 4 * math.sin(1.3 * t + 2) + 2 * math.sin(2.9 * t)
    rot = .0025 * math.sin(1.1 * t + .5)
    cam = dict(z=z0, x=540., y=760., dx=dx, dy=dy, rot=rot)
    if t >= O['CERTA'] and face_hit is not None:
        k = expo((t - O['CERTA']) / .07)
        zc = z0 + .55 * k
        S0 = cam_screen(dict(cam, rot=0.))(*face_hit)
        tx, ty = lerp(S0[0], 540., k), lerp(S0[1], 680., k)
        sh = K.decay(t, O['CERTA'], .09)
        fx_, fy_ = face_hit
        cam = dict(z=zc, x=fx_, y=fy_, dx=tx - fx_ + 14 * sh * math.sin(t * 97), dy=ty - fy_ + 10 * sh * math.cos(t * 83), rot=.012 * sh)
    return cam


def strip_art(s):
    """film strip geometry for frame scale s -> (frame_w, frame_h, margin, pitch)."""
    fw, fh = W * s, H * s; m = .15 * fw; gap = .035 * fh; pitch = fh + gap
    return fw, fh, m, pitch


def film_strip(fr, t):
    """the live frame shrinks into a 35 mm strip; the strip pulls down one frame to the first showreel shot."""
    if t < T_PULL0: s = lerp(1.0, .58, expo((t - T_STRIP) / .07))
    elif t < T_PULL1: s = .58
    else: s = lerp(.58, 1.0, sio((t - T_PULL1) / (T12 - T_PULL1)))
    u = clamp((t - T_PULL0) / (T_PULL1 - T_PULL0)); ease = (4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2)
    fw, fh, m, pitch = strip_art(s)
    scroll = ease * pitch
    vel = 0.0
    if T_PULL0 < t < T_PULL1:
        u2 = clamp((t - 1 / 30 - T_PULL0) / (T_PULL1 - T_PULL0)); e2 = (4 * u2 ** 3 if u2 < .5 else 1 - (-2 * u2 + 2) ** 3 / 2)
        vel = (ease - e2) * pitch
    out = K.C('strip_bg', strip_bg).copy()
    x0 = 540 - fw / 2 - m; x1 = 540 + fw / 2 + m
    d = ImageDraw.Draw(out)
    d.rectangle((int(x0), 0, int(x1), H), fill=(24, 19, 16, 255))
    # frames: -1 leader, 0 live, 1 shot A first frame, 2 shot B
    srcs = {-1: leader_base(), 0: fr, 1: shotA_frame(T12), 2: K.still(E.HYPER, 23.65)}
    flick = 1 + .05 * (K.hrand(int(t * 30), 3) - .5)
    for i in (-1, 0, 1, 2):
        cy = 960 + i * pitch - scroll
        if cy + fh / 2 < -10 or cy - fh / 2 > H + 10: continue
        im = srcs[i].convert('RGB').resize((max(1, int(fw)), max(1, int(fh))), Image.BILINEAR)
        if i != 0 or abs(flick - 1) > .01: im = im.point(lambda v: min(255, int(v * flick)))
        out.paste(im, (int(round(540 - fw / 2)), int(round(cy - fh / 2))))
    # sprockets (cut-outs) + edge print, scrolling with the strip
    hw, hh = .34 * m, .24 * m; hp = .52 * m
    off = (-scroll) % hp
    y = off - hp
    while y < H + hp:
        for xc in (x0 + m * .36, x1 - m * .36):
            d.rounded_rectangle((xc - hw / 2, y - hh / 2, xc + hw / 2, y + hh / 2), max(2, hh * .25), fill=(9, 8, 12, 255), outline=(70, 62, 56, 255), width=1)
        y += hp
    ep = edge_print(max(10, int(m * .27)))
    ey = (-scroll) % ep.height - ep.height
    while ey < H:
        out.alpha_composite(ep, (int(x1 - m * .97), int(ey))); ey += ep.height
    if vel > 6:                                           # vertical motion blur along the pull
        a = np.asarray(out.convert('RGB'), np.float32); L = int(min(220, vel * .9))
        c = np.cumsum(np.pad(a, ((L, 0), (0, 0), (0, 0))), 0)
        a = (c[L:] - c[:-L]) / L
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return out


def strip_bg():
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
    g = np.exp(-(((xx - 540) / 520) ** 2 + ((yy - 960) / 900) ** 2))
    a = np.array([9, 8, 13], np.float32) + g[..., None] * np.array([60, 40, 120], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).convert('RGBA')


def edge_print(size):
    def mk():
        t = K.tracked('LUMARC  ·  SHOWREEL  ·  ', size, 600, (236, 150, 64), .25)
        return t.rotate(90, Image.BICUBIC, expand=True)
    return K.C(('edge', size), mk)


def title_showreel(fr, t):
    """SHOWREEL in thin wide-tracked type, tracking opens; gradient hairline draws under it."""
    lt = t - O['MOSTRAR']
    if lt < 0: return
    out_k = 1 - clamp((t - O['CERTA']) / .08)          # bows out at the punch-in (never over his head)
    if out_k <= 0: return
    trk = lerp(.10, .42, expo(lt / .45)); size = 76; cy = 410
    chars = 'SHOWREEL'; f = E.font(size, 250)
    adv = [f.getlength(c) for c in chars]; tr = size * trk; tw = sum(adv) + tr * (len(chars) - 1)
    x = 540 - tw / 2
    for i, c in enumerate(chars):
        k = clamp((lt - .025 * i) / .16)
        if k <= 0: x += adv[i] + tr; continue
        g = K.tracked(c, size, 250, E.WHITE, 0, glow=.5)
        K.paste(fr, K.fade(g, k * out_k), x + adv[i] / 2, cy + (1 - eout(k)) * 18 - 30 * (1 - out_k))
        x += adv[i] + tr
    lw = int(560 * expo((lt - .08) / .4))
    if lw > 4:
        ln = K.C(('hair', lw), lambda: hairline(lw))
        K.paste(fr, K.fade(ln, out_k), 540, cy + 66)


def hairline(w):
    g = E.gradient(w, 3, E.GRAD_LIGHT).convert('RGBA')
    m = np.ones((3, w), np.float32); x = np.linspace(0, 1, w); m *= np.clip(np.minimum(x, 1 - x) * 8, 0, 1)[None]
    g.putalpha(Image.fromarray((m * 255).astype(np.uint8))); return g


def seg11(ctx, t):
    P = ctx.post
    ctx.captions = False
    if t < T_MCU:                                         # burnt leader flash (3 frames)
        ctx.full = leader_frame(t); P['grain'] = 2.2; P['vignette'] = .5
        return
    av = K.av_frame(ctx, t)
    fx, fy, top = K.face_track(av)
    hand = K.hand_track(av, +1) if t >= O['MAO'] - .05 else None
    face_hit = HIT.get('face') if t >= O['CERTA'] else None     # punch-in anchors on his face at the hit
    cam = cam11(t, face_hit)
    ctx.cam = cam
    S = cam_screen(cam)
    P['vignette'] = .40
    # impact
    if t >= O['CERTA']:
        k = t - O['CERTA']
        P['flash'] = .55 * math.exp(-k / .045); P['rgb'] = 12 * math.exp(-k / .08); P['zoom_blur'] = .9 * math.exp(-k / .07)
        P['bright'] = 1 + .12 * math.exp(-k / .1)
    ui = []
    # viewfinder brackets
    kb = expo((t - T_MCU) / .22)
    sc = lerp(1.07, 1.0, kb)
    bw, bh = 912 * sc, 1430 * sc
    ui.append((corner_box(bw, bh, 64, 4, E.WHITE, .9 * kb), 540, 960))
    # REC + timecode + meter
    if t >= T_MCU + .02:
        blink = ((t - T_MCU) % 1.0) < .62
        dot = K.C('recdot', lambda: rec_dot())
        if blink: ui.append((dot, 128, 296))
        ui.append((K.tracked('REC', 34, 700, E.WHITE, .12), 194, 296))
        tc = timecode(t); ui.append((tc, 996 - tc.width / 2, 296))
        lv = K.env(t, .06); lv2 = K.env(t - .03, .06)
        mt = meter(lv * .95, lv2 * .9)
        if not (O['MAO'] <= t < O['CERTA'] + .1): ui.append((mt, 996 - mt.width / 2 + 6, 1640))
        ui.append((K.tracked('LUMARC STUDIO', 34, 500, (220, 220, 232), .26), 318, 1640))
    # AF box: frame -> face (IA) -> hand (MÃO) -> ✓ (CERTA)
    if t >= O['IA'] - .02:
        fs = S(fx, fy)
        face_r = (fs[0] - 200, fs[1] - 250, fs[0] + 200, fs[1] + 230)
        frame_r = (84, 245, 996, 1675)
        k1 = expo((t - O['IA'] + .02) / .14)
        r = tuple(lerp(a, b, k1) for a, b in zip(frame_r, face_r))
        if t >= O['MAO'] and hand is not None:
            hs = S(*hand)
            hand_r = (hs[0] - 165, hs[1] - 175, hs[0] + 165, hs[1] + 150)
            k2 = expo((t - O['MAO']) / .10)
            if t >= O['CERTA']:                           # back onto his face, locked: the punch-in follows it
                k3 = expo((t - O['CERTA']) / .08)
                face_now = (fs[0] - 230, fs[1] - 290, fs[0] + 230, fs[1] + 260)
                hand_r = tuple(lerp(a, b, k3) for a, b in zip(hand_r, face_now))
            r = tuple(lerp(a, b, k2) for a, b in zip(r, hand_r))
        locked = t >= O['IA'] + .10
        col = (175, 160, 255) if locked else E.WHITE
        if t >= O['MAO'] and t < O['MAO'] + .08: col = E.WHITE
        lw = 5 if t < O['CERTA'] else 7
        bx = corner_box(r[2] - r[0], r[3] - r[1], 46, lw, col, .95)
        ui.append((bx, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2))
        if O['IA'] + .04 <= t < O['MAO'] + .05:
            ch = ia_chip(); kc = back((t - O['IA'] - .04) / .18, 2.2) * (1 - clamp((t - O['MAO']) / .05))
            ui.append((K.scale_im(ch, max(.05, .5 + .5 * kc)), r[0] + ch.width / 2 - 2, r[1] - 40))
        if t >= O['CERTA']:
            kc = back((t - O['CERTA']) / .16, 2.6)
            ui.append((K.scale_im(check_badge(), .3 + .7 * kc), r[2] - 6, r[1] + 6))
    # captions drop with the CERTA punch-in so they never sit on his (now 1.9x) chin / beard
    cap_y = 1330 + 150 * (expo((t - O['CERTA']) / .08) if t >= O['CERTA'] else 0.)
    caps = K.caps(t, PAGES11, y=cap_y, base=88)
    bt = bars11(t)
    hold = {'ui': ui, 'caps': caps}

    def wrap(fr):
        if t < T_MCU + .3:                                # rack focus in + burn residue
            kf = 1 - expo((t - T_MCU) / .2)
            if kf > .02: fr = fr.filter(ImageFilter.GaussianBlur(14 * kf))
            kb_ = math.exp(-(t - T_MCU) / .06) * .9
            if kb_ > .02: fr = K.add_light(fr, burn_map(), kb_)
        title_showreel(fr, t)
        paste_all(fr, hold['ui'])
        bars(fr, bt)
        paste_all(fr, hold['caps'])
        if t >= T_STRIP: fr = film_strip(fr, t)
        return fr
    ctx.wrap = wrap
    if t >= T_STRIP:
        P['flash'] = 0.; P['rgb'] = 0.; P['zoom_blur'] = 0.; P['vignette'] = .25


HIT = {}


def rec_dot():
    S = 4; n = 26 * S; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, n - 1, n - 1), fill=(236, 50, 60, 255)); return im.resize((26, 26), Image.LANCZOS)


# ================================================================ SEG 12 — cinema
HYPER_A0 = 22.55                                         # gold particles assembling the headphone
def shotA_frame(t):
    return E.clip(E.HYPER).at(HYPER_A0 + max(0., t - T12))


def bars12(t):
    seq = [(T12, 0, 250), (O['COM'], 250, 330), (O['COMERCIAL'], 330, 420), (O['CINEMA'], 420, (H - 452) / 2)]
    v = 0.0
    for t0, a, b in seq:
        if t >= t0: v = lerp(a, b, expo((t - t0) / (.07 if b < 700 else .09)))
    return v


def light_sweep(img, t0, t1, t, ang=.35, width=180, k=.55):
    """diagonal specular sweep that only lights the highlights."""
    u = (t - t0) / (t1 - t0)
    if not 0 <= u <= 1: return img
    a = np.asarray(img.convert('RGB'), np.float32)
    lum = a.mean(2) / 255
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
    pos = lerp(-1200, 1300, sio(u))
    d = (xx + yy * ang) - pos
    band = np.exp(-(d / width) ** 2)
    band = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    m = band * np.clip(lum * 1.6 - .25, 0, 1) * k
    a = a + m[..., None] * np.array([255, 236, 200], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def grade12(im, warm=0.0, contrast=1.08):
    a = np.asarray(im.convert('RGB'), np.float32)
    a = (a - 128) * contrast + 128
    if warm: a = a * np.array([1 + .04 * warm, 1.0, 1 - .05 * warm], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def scope_frame(t):
    """2.39:1 strip: the hero still in a wide black frame, slow push, anamorphic flare."""
    lt = t - O['CINEMA']
    src = K.still(E.HYPER, 24.05)
    ch = lerp(880, 770, sio(lt / .7)); cw = ch * 2.39
    cx, cy = 540, 1075
    key = ('scope_src',)
    base = K.C(key, lambda: _scope_canvas(src))
    # crop from the padded canvas (source centred at (PADX + 540, cy))
    PADX = (base.width - W) // 2
    box = (PADX + cx - cw / 2, cy - ch / 2, PADX + cx + cw / 2, cy + ch / 2)
    sh = 452
    im = base.resize((W, sh), Image.BICUBIC, box=box)
    # atmosphere inside the scope frame (warm haze + lifted blacks) so the 2.39 strip reads against the bars
    hz = K.C('scope_haze', scope_haze)
    a = np.asarray(im, np.float32)
    a = a + hz * (1 - a / 255) ** 2
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def scope_haze():
    yy, xx = np.mgrid[0:452, 0:W].astype(np.float32)
    g = np.exp(-(((xx - 540) / 470) ** 2 + ((yy - 250) / 300) ** 2))
    side = np.exp(-(((xx - 540) / 900) ** 2))
    return (g[..., None] * np.array([34, 24, 14], np.float32) + side[..., None] * np.array([12, 10, 14], np.float32)
            + (np.exp(-((yy - 452) / 50) ** 2) * .5)[..., None] * np.array([22, 16, 10], np.float32))


def _scope_canvas(src):
    PADX = 520
    cv = Image.new('RGB', (W + 2 * PADX, H), (0, 0, 0))
    m = np.ones((H, W), np.float32); x = np.arange(W, dtype=np.float32)
    m *= np.clip(np.minimum(x, W - 1 - x) / 160, 0, 1)[None]
    mi = Image.fromarray((m * 255).astype(np.uint8))
    cv.paste(src, (PADX, 0), mi)
    return cv


def cinema_title(fr, t):
    lt = t - O['CINEMA']
    if lt < 0: return
    trk = lerp(.30, .62, expo(lt / .6)); size = 104; cy = (H - 452) / 2 - 118
    chars = 'CINEMA'; f = E.font(size, 200)
    adv = [f.getlength(c) for c in chars]; tr = size * trk; tw = sum(adv) + tr * (len(chars) - 1)
    x = 540 - tw / 2
    for i, c in enumerate(chars):
        k = clamp((lt - .03 * i) / .2)
        if k > 0:
            g = K.tracked(c, size, 200, E.WHITE, 0, glow=.35)
            K.paste(fr, K.fade(g, k), x + adv[i] / 2, cy + (1 - eout(k)) * 14)
        x += adv[i] + tr
    k2 = clamp((lt - .14) / .25)
    if k2 > 0:
        cr = K.tracked('SILENCE ONE  ·  UM FILME LUMARC', 34, 400, (176, 176, 194), .26)
        K.paste(fr, K.fade(cr, k2), 540, (H + 452) / 2 + 76)
        ln = K.C(('hair', 300), lambda: hairline(300))
        K.paste(fr, K.fade(ln, k2), 540, cy + 84)


def seg12(ctx, t):
    P = ctx.post
    ctx.captions = False
    P['grain'] = 1.7; P['vignette'] = .48
    wx, wy = 1.2 * math.sin(t * 23.0), 1.0 * math.cos(t * 19.0)          # gate weave
    bt = bars12(t)
    if t < O['COM']:
        u = (t - T12) / (O['COM'] - T12)
        f = shotA_frame(t)
        fr = E.zoom(f, 1.0 + .055 * sio(u), (540, 1000), dx=wx, dy=wy).convert('RGBA')
        fr = grade12(fr, .3)
        fl = .28 + .10 * math.sin(t * 11) + .75 * K.decay(t, T12, .18)
        fr = K.add_flare(fr, 540, 1150, fl, w=2400, h=180, col=(90, 120, 255), thick=3.5, reach=.6)
    elif t < O['COMERCIAL']:
        u = (t - O['COM']) / (O['COMERCIAL'] - O['COM'])
        f = K.still(E.HYPER, 23.65)
        fr = E.zoom(f, 1.04 + .09 * sio(u), (700, 900), dx=wx, dy=wy).convert('RGBA')
        fr = grade12(fr, .4)
        fr = light_sweep(fr, O['COM'] + .02, O['COMERCIAL'] + .05, t, ang=-.55, width=150, k=.7)
    elif t < O['CINEMA']:
        u = (t - O['COMERCIAL']) / (O['CINEMA'] - O['COMERCIAL'])
        ramp = 1 - (1 - clamp(u)) ** 2.2                   # speed ramp: fast tear, slow-motion finish
        f = K.nclip(E.CROISSANT_PULL, 24).at(3.62 + 1.15 * ramp)
        fr = E.zoom(f, 1.08 + .05 * u, (560, 1150), dx=wx, dy=wy).convert('RGBA')
        fr = grade12(fr, .2, 1.1)
    else:
        lt = t - O['CINEMA']
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        strip = scope_frame(t)
        y0 = int((H - 452) / 2)
        fr.paste(strip, (0, y0))
        k = .9 * K.decay(t, O['CINEMA'], .5) + .35 + .12 * math.sin(lt * 8)
        fr = K.add_flare(fr, 540 + 40 * lt, y0 + 226 + 30, k, w=2600, h=200, col=(80, 110, 255), thick=3.0, reach=.62)
        P['vignette'] = .2; P['grain'] = 1.4
        if lt < .1: P['bright'] = 1 + .35 * (1 - lt / .1)
    if bt < 700: bars(fr, bt)
    else:
        y0 = int((H - 452) / 2); bars(fr, y0, H - y0 - 452)
    if t >= O['CINEMA']: cinema_title(fr, t)
    cp = K.caps(t, PAGES12, y=1420, base=82)
    if cp: ctx.add('screen', cap_shade(), 540, 1420)
    for im, x, y in cp: ctx.add('screen', im, x, y)
    ctx.full = fr
    if t < T12 + .1: P['zoom_blur'] = .6 * (1 - (t - T12) / .1)


# ================================================================ SEG 13 — kinetic type
AV13 = dict(s=.90, x=0., y=0.)


def seg13(ctx, t):
    P = ctx.post
    ctx.captions = False
    ctx.avatar.update(AV13)
    e = K.env(t, .04)
    ctx.bg_dim = .34 - .16 * e
    # camera: sway with the syllables + punches on DANÇA / FALA
    accents = [O['UM3'], O['TEXTO'], O['TO'], O['QUE3'], O['DAN'], O['CA'], O['NO'], O['RITMO'], O['MO'], O['DA'], O['SUA'], O['FALA'], O['LA']]
    rot = 0.0
    for i, a in enumerate(accents):
        if t >= a: rot += (1 if i % 2 == 0 else -1) * .010 * math.exp(-(t - a) / .22) * math.sin(min(math.pi, (t - a) / .22 * math.pi) + .3)
    z = 1.02 + .045 * K.decay(t, O['DANCA'], .25) + .035 * K.decay(t, O['FALA'], .25)
    ctx.cam = dict(z=z, x=540., y=900., dx=4 * math.sin(t * 2.1), dy=3 * math.sin(t * 1.7), rot=rot)
    # the type — world space ('front' moves with the camera); DANÇA, the equalizer and the waveform sit BEHIND him
    if t < O['DANCA'] - .02:
        page1(ctx, t)
    elif t < O['NO'] - .03:
        page2(ctx, t)
    elif t < O['DA'] - .03:
        page3(ctx, t)
    else:
        page4(ctx, t)
    # the founder (drawn here so the take's side edges can be feathered into the dark studio at s < 1)
    av = K.av_frame(ctx, t)
    if av is not None:
        sp, (px, py) = feathered_avatar(av, AV13['s'])
        ctx.avatar['show'] = False
        ctx.add('behind', sp, px, py, center=False)
    # opening: the scope bars retract onto him
    ko = expo((t - T13) / .16)
    bt = lerp((H - 452) / 2, 0, ko)
    if bt > 1:
        ctx.wrap = lambda fr: bars(fr, bt)
        P['zoom_blur'] = .4 * (1 - ko)


def layer_img():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def page1(ctx, t):
    L = layer_img()
    # "UM TEXTO" on one line, "QUE" below right
    s_um, s_tx = 104, 190
    w_um = E.font(s_um, 900).getlength('UM'); w_tx = E.font(s_tx, 900).getlength('TEXTO'); gap = 36
    x = 540 - (w_um + gap + w_tx) / 2; base = 470
    lt = t - O['UM3']
    def fx_um(i, n):
        k = back(lt / .2, 2.4)
        return dict(sx=.4 + .6 * k, sy=.4 + .6 * k, rot=lerp(-24, -4, eout(lt / .25)) + 3 * math.sin(t * 9) * K.decay(t, O['UM3'] + .2, .3), a=clamp(lt / .05))
    K.draw_word(L, 'UM', s_um, 'white', x, base, fx_um)
    if t >= O['TEXTO'] - .02:
        def fx_tx(i, n):
            t0 = O['TEXTO'] - .02 + .035 * i
            u = (t - t0) / .16
            if u < 0: return dict(a=0.)
            dy = -170 * (1 - clamp(u)) ** 2 if u < 1 else 0
            land = K.decay(t, t0 + .16, .06)
            sx, sy = 1 + .16 * land, 1 - .22 * land
            # bounce on "TO"
            hb = hop((t - O['TO'] - .02 * i) / .16)
            dy -= 44 * hb; sy *= 1 + .12 * hb
            rot = (4 if i % 2 else -4) * hb + (1 - clamp(u)) * (14 if i % 2 else -14)
            return dict(dy=dy, sx=sx, sy=sy, rot=rot, a=clamp(u * 3))
        K.draw_word(L, 'TEXTO', s_tx, 'white', x + w_um + gap, base, fx_tx)
    if t >= O['QUE3'] - .02:
        lq = t - O['QUE3'] + .02
        def fx_q(i, n):
            k = back(lq / .18, 2.6)
            return dict(sx=.3 + .7 * k, sy=.3 + .7 * k, rot=8 + 14 * math.sin(lq * 26) * math.exp(-lq / .2), dy=-30 * hop(lq / .2), a=clamp(lq / .05))
        K.draw_word(L, 'QUE', 128, 'white', 640, 650, fx_q)
    ctx.add('front', L, 0, 0, center=False)


def page2(ctx, t):
    """DANÇA — huge gradient word rising from behind his head, letter wave on DAN / ÇA."""
    L = layer_img(); size = 240
    ww = E.font(size, 900).getlength('DANÇA'); x = 540 - ww / 2; base = 762
    def fx(i, n):
        t_in = O['DANCA'] - .05 + .025 * i
        u = (t - t_in) / .16
        if u < 0: return dict(a=0.)
        rise = 260 * (1 - eout(u))
        dy = rise
        rot = 0.; sx = sy = 1.
        for k_, (ts, sgn) in enumerate(((O['DAN'], 1), (O['CA'], -1))):
            ti = ts + (.03 * i if sgn > 0 else .03 * (n - 1 - i))
            hb = hop((t - ti) / .15)
            dy -= 70 * hb; rot += sgn * (11 if i % 2 == 0 else -11) * hb
            land = K.decay(t, ti + .15, .05) if t >= ti + .15 else 0
            sx *= 1 + .12 * land; sy *= 1 - .16 * land
        rot += 5 * math.sin((t - O['DANCA']) * 14 + i * 1.3) * clamp((t - O['CA'] - .12) / .1)
        return dict(dy=dy, rot=rot, sx=sx, sy=sy, a=clamp(u * 2.5))
    K.draw_word(L, 'DANÇA', size, 'grad', x, base, fx)
    ctx.add('behind', L, 0, 0, center=False)


def page3(ctx, t):
    """NO RITMO — RITMO's letters stretch with his voice over an equalizer behind him."""
    L = layer_img(); B = layer_img()
    s_no, s_r = 112, 200
    w_no = E.font(s_no, 900).getlength('NO'); w_r = E.font(s_r, 900).getlength('RITMO'); gap = 34
    x = 540 - (w_no + gap + w_r) / 2; base = 560
    ln = t - O['NO'] + .04
    K.draw_word(L, 'NO', s_no, 'white', x, base, lambda i, n: dict(sx=.4 + .6 * back(ln / .18, 2.4), sy=.4 + .6 * back(ln / .18, 2.4), a=clamp(ln / .04), rot=-6))
    if t >= O['RITMO'] - .02:
        lr = t - O['RITMO'] + .02
        def fx(i, n):
            u = (lr - .025 * i) / .14
            if u < 0: return dict(a=0.)
            ev = K.env(t - .035 * i, .03)
            kick = hop((t - O['MO'] - .02 * i) / .14)
            sy = (.3 + .7 * back(u, 2.2)) * (1 + .45 * ev + .15 * kick)
            sx = (.3 + .7 * back(u, 2.2)) * (1 - .06 * ev)
            return dict(sx=sx, sy=sy, dy=-30 * kick, rot=(3 if i % 2 else -3) * ev, a=clamp(u * 3))
        K.draw_word(L, 'RITMO', s_r, 'grad', x + w_no + gap, base, fx)
    # equalizer behind him
    d = ImageDraw.Draw(B); n = 21; x0, x1 = 90, 990; bw = (x1 - x0) / n
    ke = expo((t - O['NO']) / .2)
    g = K.C('eqgrad', lambda: E.gradient(W, 1, E.GRAD_LIGHT))
    for i in range(n):
        ev = K.env(t - .012 * abs(i - n // 2) - .01 * (i % 3), .02)
        hgt = (24 + 260 * ev * (.55 + .45 * K.hrand(i, 7)) * (1 - .35 * abs(i - n // 2) / (n // 2))) * ke
        cx = x0 + (i + .5) * bw; col = g.getpixel((int(cx), 0))
        d.rounded_rectangle((cx - bw * .32, 860 - hgt, cx + bw * .32, 860), 6, fill=col + (215,))
    B = B.filter(ImageFilter.GaussianBlur(.6))
    ctx.add('behind', glowify(B), 0, 0, center=False)
    ctx.add('front', L, 0, 0, center=False)


def glowify(im, r=14, k=.7):
    a = im.getchannel('A').filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * k))
    g = Image.new('RGBA', im.size, (130, 100, 255, 0)); g.putalpha(a); g.alpha_composite(im); return g


def page4(ctx, t):
    """DA SUA FALA — FALA stretches with the voice; his real waveform scrolls behind him."""
    L = layer_img(); B = layer_img()
    s_s, s_f = 120, 280
    w_da = E.font(s_s, 900).getlength('DA'); w_su = E.font(s_s, 900).getlength('SUA'); gap = 36
    x = 540 - (w_da + gap + w_su) / 2; base = 360
    for wd, t0, xx in (('DA', O['DA'], x), ('SUA', O['SUA'], x + w_da + gap)):
        if t < t0 - .04: continue
        lw_ = t - t0 + .04
        K.draw_word(L, wd, s_s, 'white', xx, base, lambda i, n, lw_=lw_: dict(sx=.4 + .6 * back(lw_ / .18, 2.4), sy=.4 + .6 * back(lw_ / .18, 2.4),
                                                                          a=clamp(lw_ / .04), dy=-24 * hop(lw_ / .2), rot=4 * math.sin(lw_ * 20) * math.exp(-lw_ / .2)))
    if t >= O['FALA'] - .02:
        lf = t - O['FALA'] + .02
        wf = E.font(s_f, 900).getlength('FALA'); xf = 540 - wf / 2
        def fx(i, n):
            u = (lf - .03 * i) / .16
            if u < 0: return dict(a=0.)
            ev = K.env(t - .04 * i, .03)
            hb = hop((t - (O['FA'] if i < 2 else O['LA']) - .02 * (i % 2)) / .14)
            k = .3 + .7 * back(u, 2.2)
            return dict(sx=k * (1 - .08 * ev), sy=k * (1 + .32 * ev + .08 * hb), dy=-30 * hb, rot=(5 if i % 2 else -5) * hb, a=clamp(u * 3))
        K.draw_word(L, 'FALA', s_f, 'grad', xf, 700, fx)
    # waveform display behind him: his real voice over the last 0.8 s, scrolling right -> left (mirrored, filled)
    kw = expo((t - O['DA']) / .25)
    ctx.add('behind', voice_wave(t, kw), 0, 0, center=False)
    ctx.add('front', L, 0, 0, center=False)


# ================================================================ SEG 14 — set swaps
PL = {
    'paris':   dict(name='PARIS', drift=30, i=4, blur=4.0, s=1.0, x=0, y=70, z=1.04, tint=(1.03, 1.0, .96), expo=1.04, side=1, amt=.10, key=(255, 240, 215), rim=(255, 246, 228), rside=1, ramt=0.35),
    'cafe':    dict(name='CAFETERIA', drift=-30, i=2, blur=6.0, s=1.0, x=0, y=70, z=1.10, tint=(1.07, 1.0, .90), expo=1.0, side=-1, amt=.12, key=(255, 226, 180), rim=(255, 214, 160), rside=-1, ramt=0.32),
    'beach':   dict(name='PRAIA', drift=25, i=7, blur=3.5, s=1.0, x=0, y=70, z=1.00, tint=(1.04, 1.03, 1.0), expo=1.10, side=1, amt=.14, key=(255, 250, 235), rim=(255, 255, 245), rside=1, ramt=0.42),
    'board':   dict(name='SALA DE REUNIÃO', drift=-25, i=5, blur=4.0, s=1.0, x=0, y=70, z=1.10, tint=(.97, 1.0, 1.05), expo=1.03, side=-1, amt=.08, key=(225, 236, 255), rim=(225, 236, 255), rside=-1, ramt=0.3),
    'studio':  dict(name='HOME STUDIO', drift=20, i=1, blur=6.0, s=1.0, x=0, y=70, z=1.04, tint=(1.0, .97, 1.05), expo=.98, side=-1, amt=.10, key=(255, 200, 150), rim=(165, 120, 255), rside=1, ramt=0.45),
    'rooftop': dict(name='TERRAÇO', drift=-20, i=3, blur=4.5, s=1.0, x=0, y=70, z=1.06, tint=(1.10, .97, .84), expo=1.02, side=1, amt=.16, key=(255, 170, 90), rim=(255, 172, 92), rside=1, ramt=0.55),
}
SWAPS = [(T14V, 'paris'), (O['CENARIO'], 'cafe'), (O['RIO'], 'beach'), (O['QUE4'], 'board'), (O['DA4'], 'studio'), (SNAP, 'rooftop')]


def seg14(ctx, t):
    P = ctx.post
    ctx.captions = False
    cur, t_sw = SWAPS[0][1], SWAPS[0][0]
    for ts, name in SWAPS:
        if t >= ts: cur, t_sw = name, ts
    Lp = PL[cur]
    sharp, wrapimg, mean = K.plate(E.CLONE_BG[Lp['i'] - 1], Lp['blur'])
    av = K.av_frame(ctx, t)
    lt = t - t_sw
    # the plate drifts on its own (slow push + slide): parallax against him
    bg = E.zoom(sharp, 1.03 + .05 * lt, (540, 760), dx=Lp.get('drift', 0) * lt).convert('RGBA')
    if av is not None:
        sp, (px, py) = K.graded_avatar(av, Lp['s'], Lp['x'], Lp['y'], Lp, wrapimg)
        if sp is not None: bg.alpha_composite(sp, (px, py))
    ctx.avatar['show'] = False
    ctx.bg_img = bg.convert('RGB')
    lt = t - t_sw
    z = Lp['z'] + .06 * math.exp(-lt / .07)                           # snap push on every swap
    if cur == 'studio' and t >= O['ESTALO']:                          # wind-up before the snap
        w_ = K.sio((t - O['ESTALO']) / (SNAP - O['ESTALO']))
        z += .08 * w_; P['sat'] = 1 - .35 * w_; P['vignette'] = .32 + .25 * w_; P['rgb'] = 3 * w_
    if cur == 'rooftop': z = 1.08 - .06 * K.sio(lt / .4)
    dx = 6 * math.sin(t * 1.9 + 1) + 3 * math.sin(t * 3.7); dy = 5 * math.sin(t * 1.4) + 2 * math.sin(t * 4.1)
    sh = K.decay(t, SNAP, .1) if t >= SNAP else 0
    ctx.cam = dict(z=z, x=540. + Lp.get('cx', 0), y=900., dx=dx + 16 * sh * math.sin(t * 91), dy=dy + 12 * sh * math.cos(t * 77), rot=.004 * math.sin(t * 1.3) + .015 * sh)
    if lt < .05 and t_sw != T14V: P['flash'] = .18 * (1 - lt / .05)
    if t < T14V + .06: P['flash'] = .5 * (1 - (t - T14V) / .06); P['zoom_blur'] = .5 * (1 - (t - T14V) / .06)
    if t >= SNAP:
        k = t - SNAP
        P['flash'] = .9 * math.exp(-k / .045); P['zoom_blur'] = 1.0 * math.exp(-k / .08); P['rgb'] = 10 * math.exp(-k / .08)
        P['flash_col'] = (255, 246, 230)
    caps = K.caps(t, PAGES14, y=1470, base=92, punch=('ESTALO.', SNAP))
    chip_k = clamp((lt - (.12 if cur == 'rooftop' else 0)) / .07) * (0 if t >= T_OUT else 1)   # not under the zoom blurs
    chip = loc_chip(Lp['name'])
    ring_k = (t - SNAP) / .32 if t >= SNAP else -1
    if t >= T_OUT:                                     # exit smear: the next section's pose jump is under it
        ctx.cam['z'] += .10; P['zoom_blur'] = 1.0; P['flash'] = .22; P['flash_col'] = (255, 240, 220)

    def wrap(fr):
        if 0 <= ring_k < 1:                            # starts wide (never a tight 'monocle' ring on his face)
            R = 520 + 1500 * eout(ring_k)
            rg = K.ring_img(R, 16 * (1 - ring_k) + 3, (255, 236, 210), (1 - ring_k) ** 1.3, blur=2.5)
            K.paste(fr, rg, 540, 980)
            rg2 = K.ring_img(R * .72, 6 * (1 - ring_k) + 2, (200, 170, 255), .7 * (1 - ring_k) ** 1.5, blur=1.5)
            K.paste(fr, rg2, 540, 980)
        if chip_k > .01: K.paste(fr, K.fade(chip, chip_k), 96 + chip.width / 2, 268 + 16 * (1 - eout(chip_k)))
        paste_all(fr, caps)
        return fr
    ctx.wrap = wrap


# ================================================================ draw
def draw(ctx, lt, t):
    if t < T12:
        _face_at_hit(ctx, t)
        seg11(ctx, t)
    elif t < T13:
        seg12(ctx, t)
    elif t < T14V:
        seg13(ctx, t)
    else:
        seg14(ctx, t)


def _face_at_hit(ctx, t):
    """his face at the CERTA hit (take coordinates) — measured once from the take's frame at that instant so the
    punch-in is a pure function of t (independent of which frames were rendered before)."""
    if t < O['CERTA'] or 'face' in HIT: return
    k_hit = E.Avatar._k_of(O['CERTA'])
    # read that source frame with a separate reader (does not disturb the film's sequential reader)
    r = E.Reader(os.path.join(E.SRC, 'tight.mov'), (k_hit - .5) / E.AV_FPS, .2, vf=E.AV_VF, exact=True)
    f = r.get(0); r.close()
    rgb, al = E.key(f)
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); im.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    fx, fy, top = K.face_track(im); HIT['face'] = (fx, fy - 40)


def voice_wave(t, kw, cy=800, amp=190, n=96, span=.8):
    """mirrored filled waveform of the real voice (peak envelope per column), gradient fill + glow (RGBA full frame)."""
    x = K.C('raw16k', lambda: np.fromfile(os.path.join(E.SRC, 'tight16k.raw'), np.float32))
    a = int((t - span) * 16000); b = int(t * 16000); hop_ = (b - a) // n
    v = np.zeros(n, np.float32)
    for i in range(n):
        s0 = a + i * hop_
        if s0 >= 0: v[i] = np.abs(x[s0:s0 + hop_]).max() if s0 + hop_ <= len(x) else 0
    v = np.clip(v * 3.0, 0, 1) ** .8
    v = np.convolve(v, np.array([.25, .5, .25], np.float32), 'same') * kw
    xs = np.linspace(40, 1040, n)
    top = [(float(xx), float(cy - 8 - amp * vv)) for xx, vv in zip(xs, v)]
    bot = [(float(xx), float(cy + 8 + amp * .55 * vv)) for xx, vv in zip(xs[::-1], v[::-1])]
    # deeper, semi-transparent fill (the LUMARC dark gradient) so the light-gradient FALA in front of it pops
    m = Image.new('L', (W, H)); ImageDraw.Draw(m).polygon(top + bot, fill=190)
    g = K.C('wave_grad2', lambda: E.gradient(W, H, E.GRAD).convert('RGBA'))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gl = Image.new('RGBA', (W, H), (110, 80, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda q: int(q * .6)))
    out.alpha_composite(gl)
    body = g.copy(); body.putalpha(m); out.alpha_composite(body)
    # bars look: thin dark gaps every column
    d = ImageDraw.Draw(out); step = (xs[1] - xs[0])
    for xx in xs: d.line((xx + step / 2, cy - amp - 10, xx + step / 2, cy + amp), fill=(0, 0, 0, 0), width=3)
    return out


def feathered_avatar(av, s_, feather=90):
    """the keyed take scaled around its bottom centre, alpha feathered over `feather` px at both side edges."""
    im = av.resize((int(W * s_), int(H * s_)), Image.BILINEAR)
    ramp = K.C(('feather', im.width, feather), lambda: Image.fromarray((np.clip(np.minimum(np.arange(im.width), im.width - 1 - np.arange(im.width)) / feather, 0, 1) ** 1.5 * 255).astype(np.uint8)[None].repeat(im.height, 0)))
    a = Image.fromarray((np.asarray(im.getchannel('A'), np.uint16) * np.asarray(ramp, np.uint16) // 255).astype(np.uint8))
    im.putalpha(a)
    return im, (int(540 - im.width / 2), int(H - im.height))


def cap_shade():
    """soft dark lower-third shade behind the subtitles on bright footage."""
    def mk():
        w, h = 1080, 340                                   # alpha windowed to exactly 0 at the canvas edges (no seam)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        a = np.exp(-(((xx - w / 2) / (w * .40)) ** 4 + ((yy - h / 2) / 94.) ** 2)) * .55
        win = np.sin(np.pi * np.clip(yy / (h - 1), 0, 1)) ** 2 * np.clip(np.sin(np.pi * np.clip(xx / (w - 1), 0, 1)), 0, 1) ** .5
        a = a * win
        im = Image.new('RGBA', (w, h), (4, 4, 8, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return K.C('cap_shade', mk)


def loc_chip(name):
    """location slate: dark glass pill with a map pin + tracked name."""
    def mk():
        txt = K.tracked(name, 34, 600, E.WHITE, .18)
        w, h = txt.width + 30, 64
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=150)
        body = Image.new('RGBA', (w, h), (10, 10, 16, 0)); body.putalpha(m); im.alpha_composite(body)
        b = Image.new('L', (w, h)); ImageDraw.Draw(b).rounded_rectangle((1, 1, w - 2, h - 2), h // 2, outline=110, width=2)
        bd = Image.new('RGBA', (w, h), (255, 255, 255, 0)); bd.putalpha(b); im.alpha_composite(bd)
        S = 4; pin = Image.new('L', (26 * S, 34 * S)); d = ImageDraw.Draw(pin)
        d.ellipse((2 * S, 1 * S, 24 * S, 23 * S), fill=255); d.polygon([(4 * S, 16 * S), (22 * S, 16 * S), (13 * S, 33 * S)], fill=255)
        d.ellipse((9 * S, 7 * S, 17 * S, 15 * S), fill=0)
        pin = pin.resize((26, 34), Image.LANCZOS)
        pg = E.gradient(26, 34, E.GRAD_LIGHT).convert('RGBA'); pg.putalpha(pin)
        im.alpha_composite(pg, (20, (h - 34) // 2))
        im.alpha_composite(txt, (40 + 4, (h - txt.height) // 2))
        return im
    return K.C(('loc', name), mk)
