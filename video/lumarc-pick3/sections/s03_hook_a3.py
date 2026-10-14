"""s03 — HOOK A3 (8.00–12.20): "Content that's fast, cheap AND good?  Everyone says that's impossible."

  8.00  frame 1 = him (right) + THE TRIANGLE (sections/_tri.py) on the left, all three nodes DIM; a big "?" rockets in
        from the lens and lands in its heart on "Content" (8.13, pop + small light hit), then pulses; the camera eases in.
        Captions top band: CONTENT THAT'S (8.12 / 8.47)
  8.71  "FAST,"  the FAST node lights (overdrive + pop + ding), punch
  9.42  "CHEAP"  CHEAP lights, the FAST-CHEAP beam charges;  9.64 "AND" the other beams start drawing
  9.79  "GOOD?"  GOOD lights, every beam blazes and the "?" turns into a huge gradient "?" that SLAMS (the question)
 10.067 (pose jump) hard cut: him centred.  THE FLOOD — "Everyone says": chat bubbles, comments, a group-chat
        notification pop in from every edge on the rhythm of his words ("pick two 🙄", "not a chance.", "lol", ...),
        never over his face.  Caption EVERYONE SAYS (10.17 / 10.59) · THAT'S (10.98)
 11.20  "imPOSSIBLE": an OS error dialog SLAMS in (⚠ Error · IMPOSSIBLE. · [Pick two]) = the word itself, then red
        IMPOSSIBLE rubber stamps hit from everywhere (11.31 / 11.43 / 11.54).
 11.86  his knowing look: the camera pushes into his face and the whole flood slides out of frame; settled by 12.12,
        clean hard cut into the body at 12.20.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _tri as TRI
from sections import _H_kit as K

START, END = E.span(10, 12)                      # 8.00 – 12.20
W, H = E.W, E.H

# word onsets (timeline s) measured on src/tight16k.raw (10 ms band envelopes 80-900 / 900-3k / >3.5 kHz + spectrogram)
ONSETS = dict(CONTENT=8.12, THATS=8.47, FAST=8.71, CHEAP=9.42, AND=9.64, GOOD=9.79, GOOD_END=9.98,
              EVERYONE=10.17, SAYS=10.59, THATS2=10.98, IMPOSSIBLE=11.18, POS=11.31, VOICE_END=11.84)
Wd = ONSETS
J12 = K.jump_t(12)                               # 10.0667
T_Q = 8.13                                       # frame 1: the '?' rockets in from the lens, lands on "Content" (8.13)
T_DIALOG = 11.20                                 # the error dialog lands ("im-" 11.18)
T_STAMPS = (11.31, 11.43, 11.54)
T_PUSH = 11.86                                   # knowing look: push-in, flood slides out
CAP_END1, CAP_END2 = J12 - .03, T_DIALOG - .02
lerp, clamp, eo, eio = K.lerp, K.clamp, K.eo, K.eio

# ------------------------------------------------------------------------------------------- the flood (bubbles)
# (t, kind, text, user, x, y, rot) — screen px at the flood framing; never over his face (x 380-700, y 650-1150)
BUBBLES = [
    (10.12, 'chat', 'pick two 🙄', None, 292, 530, -3),
    (10.21, 'comment', 'not a chance.', '@agency_guy', 790, 545, 3),
    (10.31, 'blue', 'lol', None, 196, 790, 5),
    (10.42, 'chat', 'nope.', None, 858, 1000, -4),
    (10.53, 'chat', 'good luck with that 😂', None, 540, 1238, -2),
    (10.63, 'blue', '😂😂😂', None, 862, 780, -5),
    (10.73, 'notif', "that's impossible 💀", 'Group chat', 330, 1420, -2),
    (10.84, 'chat', 'no way', None, 190, 1030, 4),
    (10.94, 'comment', 'never gonna happen', '@your_cfo', 760, 1560, 3),
    (11.05, 'comment', 'choose two. classic.', '@realist', 400, 1720, -3),
]

CUES = [
    (8.14, 'swipe', {'gain': -10, 'pan': -.3}), (T_Q, 'pop', {'gain': -10, 'pan': -.35}),   # swipe pre-roll .14 -> from 8.00
    (8.02, 'shimmer', {'gain': -16, 'pan': -.4}),
    (Wd['FAST'], 'ding', {'note': 'E6', 'gain': -9, 'pan': -.35}), (Wd['FAST'], 'pop', {'gain': -12, 'pan': -.35}),
    (Wd['CHEAP'], 'ding', {'note': 'C6', 'gain': -9, 'pan': -.5}), (Wd['CHEAP'], 'pop', {'gain': -12, 'pan': -.5}),
    (Wd['AND'], 'swoosh', {'gain': -13, 'pan': -.4}),
    (Wd['GOOD'], 'ding', {'note': 'G6', 'gain': -9, 'pan': -.15}), (Wd['GOOD'] + .03, 'impact', {'gain': -4}),
    (Wd['GOOD'] + .03, 'shing', {'gain': -10, 'pan': -.3}),
    (J12, 'swipe', {'gain': -9}),
] + [(b[0], 'notify' if b[1] == 'notif' else 'pop', {'gain': -6 - (i % 3) * 2, 'pan': (b[4] - 540) / 540 * .8})
     for i, b in enumerate(BUBBLES)] + [
    (T_DIALOG, 'buzzer', {'gain': -5}), (T_DIALOG, 'thud', {'gain': -2}),
    (T_STAMPS[0], 'buzzer', {'gain': -12, 'pan': -.5}), (T_STAMPS[0], 'thud', {'gain': -10, 'pan': -.5}),
    (T_STAMPS[1], 'buzzer', {'gain': -13, 'pan': .5}), (T_STAMPS[1], 'thud', {'gain': -11, 'pan': .5}),
    (T_STAMPS[2], 'buzzer', {'gain': -14, 'pan': 0}), (T_STAMPS[2], 'thud', {'gain': -12}),
    (T_PUSH, 'whoosh', {'gain': -9}),
]

# ------------------------------------------------------------------------------------------- captions
def _pages():
    def mk():
        P = K.page
        return K.chain([P([('CONTENT', Wd['CONTENT'], 0), ("THAT'S", Wd['THATS'], 0)], base=100),
                        P([('FAST,', Wd['FAST'], 1)], base=104),
                        P([('CHEAP', Wd['CHEAP'], 1), ('AND', Wd['AND'], 0), ('GOOD?', Wd['GOOD'], 1)], base=74, z=CAP_END1),
                        P([('EVERYONE', Wd['EVERYONE'], 0), ('SAYS', Wd['SAYS'], 0)], base=100),
                        P([("THAT'S", Wd['THATS2'], 0)], base=100, z=CAP_END2)], CAP_END2)
    return E.cached('H3_pages', mk)
CAP_Y = 340

# ------------------------------------------------------------------------------------------- part 1: the question
AV_X = 280                                       # he sits right: GOOD keeps clear of his face
TRI_AT, TRI_SIZE = (352, 792), 600               # fixed in screen space (rides the punches + shake only), so the
FACE_X = 540 + AV_X                              # camera push no longer drags the CHEAP label out of x >= 70

def q_mark(kind):
    """the '?' in the triangle's heart: 'idle' white-hot with a purple glow | 'lit' LUMARC gradient + strong glow."""
    def mk():
        if kind == 'idle': return K.big_word('?', 230, 'white', glow=True)
        im = K.big_word('?', 230, 'grad', glow=True)
        a = im.getchannel('A').filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * .8))
        g = Image.new('RGBA', im.size, (150, 110, 255, 0)); g.putalpha(a)
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(im); return out
    return E.cached(('H3_q', kind), mk)

def tri_state(t):
    lit = [0., 0., 0.]; pop = [1., 1., 1.]; edge = [.18, .18, .18]          # faintly alive from frame 1
    for i, nm in enumerate(('FAST', 'CHEAP', 'GOOD')):
        tw = Wd[nm]
        if t >= tw - .02:
            lit[i] = clamp((t - tw + .02) / .07) * (1 + .6 * K.decay(t, tw + .03, .15))
            pop[i] = 1 + .3 * K.bump((t - tw + .02) / .22)
    if t >= Wd['CHEAP']: edge[0] = max(.18, .8 * eo((t - Wd['CHEAP']) / .2))
    draw = [1., 1., 1.]
    if t >= Wd['AND']:
        edge[1] = edge[2] = max(.18, .7 * eo((t - Wd['AND']) / .15))
    if t >= Wd['GOOD']:
        b = 1 + .7 * K.decay(t, Wd['GOOD'] + .03, .18)
        edge = [max(e, b) for e in edge]
    dr = TRI.drift(t, .7)
    return TRI.state(lit=tuple(lit), pop=tuple(pop), edge=tuple(edge), draw=tuple(draw), plate=.85,
                     flow=t * .9,
                     yaw=dr['yaw'] * .7 + 6, pitch=dr['pitch'] * .7 + 3, roll=dr['roll'])

def part1(ctx, t):
    P = ctx.post
    u = t - START
    z = 1.08 + .07 * eo(u / .9, 2) + .02 * clamp((t - 8.9) / 1.1)
    zp = K.punch(t, Wd['FAST'], .03, .10) + K.punch(t, Wd['CHEAP'], .03, .10) + K.punch(t, Wd['GOOD'] + .03, .06, .12)
    zp += K.punch(t, T_Q, .025, .08)
    z += zp
    sx, sy = K.shake(t, Wd['GOOD'] + .03, 10, tau=.12)
    ctx.avatar.update(x=AV_X)
    fx = K.FACE[0] + AV_X
    K.set_cam(ctx, z=z, x=fx, y=K.FACE[1], dx=FACE_X - fx + sx, dy=905 - K.FACE[1] + sy)
    ctx.bg_dim = .14
    K.edge_shadow(ctx, AV_X)                             # the shifted take's left edge (low in frame)
    st = tri_state(t)
    zk = 1 + zp / 1.12
    ax, ay = TRI_AT[0] + sx, TRI_AT[1] + sy
    size = int(round(TRI_SIZE * zk))
    ctx.add('screen', K.tri_render(st, size, at=(ax, ay)), 0, 0, center=False)
    # the '?' in the heart of the triangle
    cx, cy = TRI.anchor('center', st, size, canvas=(W, H), at=(ax, ay))
    tg = Wd['GOOD'] + .03
    if t < tg:                                           # frame 1: the '?' rockets in from the lens, then pulses
        pulse = 1 + .06 * math.sin(2 * math.pi * 1.5 * (t - T_Q)) if t >= T_Q else 1.0
        q = clamp((t - START) / (T_Q - START)); s0 = 1 + 1.3 * (1 - eo(q, 3)) + .14 * K.decay(t, T_Q, .07)
        qi = q_mark('idle')
        img = K.zoom_trail(qi, s0 * zk * 1.10, s0 * zk) if t < T_Q else K.scaled(qi, pulse * s0 * zk)
        ctx.add('screen', img, cx, cy + 4)
    else:
        q = (t - tg)
        s = 1.12 * (1 + .8 * (1 - K.back(clamp(q / .16), 2.6))) * zk
        s *= 1 + .03 * math.sin(2 * math.pi * 1.4 * q)
        ctx.add('screen', K.scaled(q_mark('lit'), s), cx, cy + 4 + 4 * math.sin(3 * q))
    hk = .22 * K.decay(t, tg, .07) if t >= tg else 0
    if T_Q <= t < tg: hk = max(hk, .14 * K.decay(t, T_Q, .06))      # the '?' lands: a small light hit
    wraps = []
    if hk > .02: wraps.append(lambda fr, hk=hk: K.light_hit(fr, hk))
    return wraps

# ------------------------------------------------------------------------------------------- part 2: the flood
def bubble(kind, text, user):
    def mk():
        if kind in ('chat', 'blue'):
            f = K.inter(56, 'SemiBold'); tx = K.rich(text, f, (255, 255, 255), esize=58)
            pw, ph = tx.width + 72, tx.height + 44
            im = Image.new('RGBA', (pw + 20, ph + 26), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            col = (64, 64, 74, 245) if kind == 'chat' else (31, 122, 255, 250)
            d.rounded_rectangle((10, 4, 10 + pw, 4 + ph), ph // 2, fill=col)
            d.polygon([(26, ph - 6), (12, ph + 18), (54, ph - 2)], fill=col)
            im.alpha_composite(tx, (10 + 32, 4 + 20))
        elif kind == 'comment':
            f1 = K.inter(32, 'Bold'); f2 = K.inter(50, 'SemiBold')
            t1 = K.rich(user, f1, (175, 175, 190)); t2 = K.rich(text, f2, (255, 255, 255), esize=52)
            pw = max(t1.width, t2.width) + 150; ph = 146
            im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, pw - 1, ph - 1), 30, fill=(22, 22, 30, 238), outline=(255, 255, 255, 40), width=2)
            av = E.gradient(64, 64, [(255, 140, 90), (240, 80, 140), (150, 90, 255)]).convert('RGBA')
            m = Image.new('L', (64, 64)); ImageDraw.Draw(m).ellipse((0, 0, 63, 63), fill=255); av.putalpha(m)
            im.alpha_composite(av, (26, 41)); im.alpha_composite(t1, (110, 16)); im.alpha_composite(t2, (108, 58))
        else:   # notification banner (light frosted)
            f1 = K.inter(30, 'Bold'); f2 = K.inter(50, 'SemiBold')
            t1 = K.rich(user.upper() + '  ·  now', f1, (90, 90, 105)); t2 = K.rich(text, f2, (20, 20, 28), esize=52)
            pw = max(t1.width, t2.width) + 150; ph = 148
            im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, pw - 1, ph - 1), 34, fill=(242, 242, 247, 240))
            ic = E.gradient(68, 68, [(80, 220, 120), (40, 190, 90), (30, 160, 80)]).convert('RGBA')
            m = Image.new('L', (68, 68)); ImageDraw.Draw(m).rounded_rectangle((0, 0, 67, 67), 18, fill=255); ic.putalpha(m)
            bub = Image.new('RGBA', (68, 68), (0, 0, 0, 0)); ImageDraw.Draw(bub).ellipse((16, 18, 52, 46), fill=(255, 255, 255, 255))
            ic.alpha_composite(bub); im.alpha_composite(ic, (24, 34))
            im.alpha_composite(t1, (112, 20)); im.alpha_composite(t2, (110, 58))
        return E.shadow(im, 16, .55, (0, 10))
    return E.cached(('H3_bub', kind, text, user), mk)

def dialog():
    """generic OS error dialog — the word IMPOSSIBLE. itself (no brands)."""
    def mk():
        w, h = 880, 370; im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=(236, 236, 240, 252), outline=(255, 255, 255, 255), width=2)
        d.rounded_rectangle((0, 0, w - 1, 70), 26, fill=(214, 214, 222, 255)); d.rectangle((0, 44, w - 1, 70), fill=(214, 214, 222, 255))
        f = K.inter(32, 'Bold'); im.alpha_composite(K.rich('⚠️ Error', f, (40, 40, 50), esize=32), (28, 14))
        for a_, b_ in (((w - 52, 22), (w - 30, 44)), ((w - 52, 44), (w - 30, 22))): d.line((a_, b_), fill=(70, 70, 80, 255), width=4)
        # red stop icon
        d.ellipse((34, 104, 154, 224), fill=(226, 44, 58, 255)); d.rounded_rectangle((85, 124, 103, 184), 6, fill=(255, 255, 255, 255))
        d.ellipse((84, 194, 104, 214), fill=(255, 255, 255, 255))
        ft = K.inter(100, 'Black'); d.text((180, 96), 'IMPOSSIBLE.', font=ft, fill=(24, 24, 32, 255))
        fs = K.inter(34, 'Medium'); d.text((184, 222), 'Request: fast + cheap + good', font=fs, fill=(95, 95, 110, 255))
        # the only button: [ Pick two ]
        d.rounded_rectangle((w - 290, h - 92, w - 36, h - 30), 16, fill=(31, 110, 245, 255))
        fb = K.inter(36, 'Bold'); tw = fb.getlength('Pick two')
        d.text((w - 163 - tw / 2, h - 84), 'Pick two', font=fb, fill=(255, 255, 255, 255))
        d.rounded_rectangle((w - 520, h - 92, w - 310, h - 30), 16, outline=(160, 160, 175, 255), width=3, fill=(246, 246, 250, 255))
        tw2 = fb.getlength('Cancel'); d.text((w - 415 - tw2 / 2, h - 84), 'Cancel', font=fb, fill=(150, 150, 165, 255))
        return E.shadow(im, 30, .6, (0, 22))
    return E.cached('H3_dialog', mk)

MINIS = [(T_STAMPS[0], 255, 1300, -7, .56), (T_STAMPS[1], 830, 1350, 6, .56), (T_STAMPS[2], 540, 1560, -3, .62)]

def part2(ctx, t):
    P = ctx.post
    u = t - J12
    zp = eo((t - T_PUSH) / .26, 3) if t >= T_PUSH else 0.0
    z = 1.05 + .03 * clamp(u / 1.8) + K.punch(t, T_DIALOG, .035, .1) + .30 * zp
    sx, sy = 0., 0.
    for tt, amp in ((T_DIALOG, 14), (T_STAMPS[0], 8), (T_STAMPS[1], 8), (T_STAMPS[2], 8)):
        a, b = K.shake(t, tt, amp, tau=.09, f=20, seed=tt); sx += a; sy += b
    fy = lerp(985, 930, zp)
    K.set_cam(ctx, z=z, x=K.FACE[0], y=K.FACE[1], dx=sx, dy=fy - K.FACE[1] + sy)
    ctx.bg_dim = .16
    # everything below rides the camera ('front' layer): the push carries the flood out of frame
    zc = 1.05                                                # the flood is laid out at this zoom -> world coords
    blow = eo(clamp((t - T_PUSH) / .26), 2)               # the flood is BLOWN out (fast start, radially from his face)
    def wpt(x, y):
        k = 1 + 1.8 * blow
        dx, dy = (x - 540) / zc, (y - 985) / zc; L = max(1e-3, math.hypot(dx, dy))
        kick = 760 * blow / L                                # every card travels >= 760 px outward (the central
        return (K.FACE[0] + dx * (k + kick), K.FACE[1] + dy * (k + kick))   # ones too, no ghost lingering on his chest)
    fade = (1 - blow) ** 1.3                                # gone by ~12.07: his knowing look holds clean to the cut
    for i, (tb, kind, text, user, x, y, rot) in enumerate(BUBBLES):
        if t < tb - .01: continue
        q = (t - tb + .01) / .17
        s = .25 + .75 * K.back(clamp(q), 2.2) if q < 1 else 1.0
        dx = (-1 if x < 540 else 1) * 160 * (1 - eo(clamp(q)))
        img = K.rotated(K.scaled(bubble(kind, text, user), s / zc), rot)
        wx, wy = wpt(x + dx, y)
        ctx.add('front', img, wx, wy, alpha=clamp(q * 3) * fade)
    # more error dialogs stamp in from everywhere (the error-cascade gag)
    for tt, x, y, ang, sc in MINIS:
        if t < tt - .05: continue
        q = clamp((t - tt + .05) / .05)
        s = sc * (1.5 - .5 * eo(q, 2)) / zc
        wx, wy = wpt(x, y)
        ctx.add('front', K.rotated(K.scaled(dialog(), s), ang), wx, wy, alpha=clamp(q * 2.5) * fade)
    # the error dialog (the word itself)
    if t >= T_DIALOG - .06:
        q = clamp((t - T_DIALOG + .06) / .06)
        s = (1.35 - .35 * eo(q, 2) + .03 * K.decay(t, T_DIALOG, .06)) / zc
        wx, wy = wpt(540, 430)
        ctx.add('front', K.scaled(dialog(), s), wx, wy, alpha=clamp(q * 2.5) * fade)
    wraps = []
    if u < .07: wraps.append(lambda fr, q=1 - u / .07: K.hsmear(fr, 200 * q * q))
    if T_PUSH <= t < T_PUSH + .1:                            # the snap push: the flung cards streak out (zoom blur)
        wraps.append(lambda fr, k=.28 * (1 - (t - T_PUSH) / .1): K.zblur(fr, k, anchor=(540, 930)))
    rk = .55 * K.decay(t, T_DIALOG, .12) if t >= T_DIALOG else 0
    if rk > .03: wraps.append(lambda fr, rk=rk: K.tint_edges(fr, rk))
    P['rgb'] = 5.0 * K.decay(t, J12, .05) + 6.0 * K.decay(t, T_DIALOG, .06)
    P['glitch'] = .35 * K.decay(t, T_DIALOG, .04) if t >= T_DIALOG else 0
    return wraps

# ------------------------------------------------------------------------------------------- draw
def draw(ctx, lt, t):
    P = ctx.post; P['vignette'] = .36
    wraps = part1(ctx, t) if t < J12 else part2(ctx, t)
    K.captions(ctx, t, _pages(), CAP_Y)
    ctx.wrap = K.compose_wraps(*wraps)
