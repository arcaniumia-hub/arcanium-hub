"""s02 — HOOK A2 (3.00–8.00): "Every agency says: fast, cheap or good — pick two. They're wrong."

THE AGENCY DECK: a smug corporate pitch-deck board (navy glass, teal "corporate" header, serif "THE RULE:", ™, a
handshake clip-art, a cheesy gold italic footer) floats beside him; THE TRIANGLE (sections/_tri.py) is its diagram.
  3.00  frame 1 = his face (right) + the deck SLAMS in on the left (clicker click + cheesy shine sweep), "THE RULE:"
        readable at once.  Captions top band: EVERY AGENCY (3.09 / 3.29) · SAYS: (3.79)
  4.36  the camera pushes into the deck (he drifts off right); a presenter's red LASER DOT jumps to each node as it pops
        on its word: FAST 4.47 · CHEAP 5.26 · GOOD 5.92 (the node labels ARE the words).
  6.267 (pose jump) snap to the deck front-on, full frame: "PICK" (6.36) ✓ on FAST, "TWO." (6.57) ✓ on CHEAP, their
        beam lights, GOOD greys out; the footer "Pick two. 😉" stamps word by word (kinetic type of the line).
  7.233 SNAP-IN on him (tight), the deck pushed to his left; "WRONG." (7.35): a giant red marker strike slashes the deck
        (title strike + a big X), the glass CRACKS (glasskit), glitch + RGB split, red edge light, punch + shake.
  7.68–8.00 his confident beat (slow push), captions gone by 7.94: clean hard cut at 8.00.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _tri as TRI
from sections import _H_kit as K

START, END = E.span(4, 9)                       # 3.00 – 8.00
W, H = E.W, E.H
GK = E._load('_glasskit_H', E.V + '/lumarc-breakout/sections/_glasskit.py')

# word onsets (timeline s) measured on src/tight16k.raw (10 ms band envelopes 80-900 / 900-3k / >3.5 kHz + spectrogram)
ONSETS = dict(EVERY=3.09, AGENCY=3.29, SAYS=3.79, SAYS_END=4.26, FAST=4.53, CHEAP=5.26, OR=5.76, GOOD=5.92,
              PICK=6.36, TWO=6.57, THEYRE=7.25, WRONG=7.35, VOICE_END=7.68)
Wd = ONSETS
J8 = K.jump_t(8)                                 # 6.2667: pose jump -> the front-on deck
T_PUSH = 4.36                                    # push into the deck
T_SNAP = 7 + 7 / 30                              # 7.2333: snap-in on him (one frame before "They're")
T_WRONG = Wd['WRONG']
CAP_END = 7.94
lerp, clamp, eo, eio = K.lerp, K.clamp, K.eo, K.eio

CUES = [
    (3.00, 'click', {'gain': -4}), (3.14, 'swipe', {'gain': -9, 'pan': -.4}), (3.02, 'shimmer', {'gain': -14, 'pan': -.4}),
    (T_PUSH, 'whoosh', {'gain': -16, 'pan': -.3}),
    (Wd['FAST'], 'pop', {'gain': -7, 'pan': -.2}), (Wd['FAST'] + .02, 'ding', {'note': 'E6', 'gain': -13}),
    (Wd['CHEAP'], 'pop', {'gain': -7, 'pan': -.4}), (Wd['CHEAP'] + .02, 'ding', {'note': 'C6', 'gain': -13}),
    (Wd['GOOD'], 'pop', {'gain': -7, 'pan': .1}), (Wd['GOOD'] + .02, 'ding', {'note': 'G6', 'gain': -13}),
    (J8, 'swipe', {'gain': -10}),
    (Wd['PICK'], 'stamp', {'gain': -8, 'pan': -.1}), (Wd['PICK'] + .01, 'tick', {'gain': -12}),
    (Wd['TWO'], 'stamp', {'gain': -8, 'pan': -.35}), (Wd['TWO'] + .01, 'tick', {'gain': -12}),
    (Wd['TWO'] + .10, 'shing', {'gain': -14, 'pan': -.25}), (6.80, 'shimmer', {'gain': -17}),
    (T_SNAP, 'whoosh', {'gain': -7}),
    (T_WRONG, 'scratch', {'gain': -3}), (T_WRONG, 'thud', {'gain': -1}), (T_WRONG + .02, 'crack', {'gain': -6, 'pan': -.4}),
    (T_WRONG + .03, 'glitch', {'gain': -9}), (T_WRONG + .12, 'glass', {'gain': -14, 'pan': -.4}),
]

# ------------------------------------------------------------------------------------------- captions
def _pages():
    def mk():
        P = K.page
        return K.chain([P([('EVERY', Wd['EVERY'], 0), ('AGENCY', Wd['AGENCY'], 1)], base=100),
                        P([('SAYS:', Wd['SAYS'], 0)], base=100, z=T_PUSH + .06),
                        P([("THEY'RE", Wd['THEYRE'], 0), ('WRONG.', Wd['WRONG'], 1)], base=108)], CAP_END)
    return E.cached('H2_pages', mk)
CAP_Y = 340
CAP_Y_WRONG = 398                                # two-line page: top of THEY'RE >= y 285
def cap_y(t): return CAP_Y if t < T_SNAP - .05 else CAP_Y_WRONG

# ------------------------------------------------------------------------------------------- the deck (flat)
CW, CH = 900, 1100
TRI_C, TRI_S = (450, 626), 660                  # triangle on the card (card px)
NAVY0, NAVY1 = (24, 38, 88), (11, 17, 44)

def _card_mask():
    return E.cached('H2_mask', lambda: _rr_mask(CW, CH, 46))

def _rr_mask(w, h, r):
    m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

def card_base():
    def mk():
        g = np.linspace(0, 1, CH, dtype=np.float32)[:, None, None]
        bg = np.array(NAVY0, np.float32) * (1 - g) + np.array(NAVY1, np.float32) * g
        bg = np.repeat(bg, CW, 1)
        im = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
        d = ImageDraw.Draw(im)
        # faint corporate grid in the diagram area
        for x in range(60, CW, 60): d.line((x, 330, x, 900), fill=(60, 90, 170, 255), width=1)
        for y in range(330, 901, 57): d.line((40, y, CW - 40, y), fill=(60, 90, 170, 255), width=1)
        # header band: cheesy teal -> blue corporate gradient
        x = np.linspace(0, 1, CW, dtype=np.float32)[None, :, None]
        c0, c1, c2 = np.array((0, 176, 212), np.float32), np.array((37, 99, 235), np.float32), np.array((70, 60, 210), np.float32)
        band = np.where(x < .5, c0 + (c1 - c0) * x / .5, c1 + (c2 - c1) * (x - .5) / .5)
        band = np.repeat(band, 130, 0)
        im.paste(Image.fromarray(band.astype(np.uint8)), (0, 0))
        d = ImageDraw.Draw(im)
        # generic logo: ring with a swoosh gap + wordmark
        d.ellipse((44, 34, 106, 96), outline=(255, 255, 255, 255), width=8)
        d.arc((31, 21, 119, 109), 200, 330, fill=(255, 214, 90, 255), width=7)
        f = K.inter(40, 'Black'); im.alpha_composite(K.tracked('AGENCY PLAYBOOK', f, (255, 255, 255), 5), (132, 38))
        f2 = K.inter(22, 'Bold'); im.alpha_composite(K.tracked('CONFIDENTIAL', f2, (220, 240, 255), 6), (CW - 250, 54))
        # title: corporate serif + ™
        ft = K.ffont(K.SERIF_B, 128); tw = ft.getlength('THE RULE:')
        tx = (CW - tw) / 2 - 14
        sh = Image.new('RGBA', (CW, 260), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((tx + 6, 152 - 130 + 8), 'THE RULE:', font=ft, fill=(0, 0, 0, 160))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (0, 130))
        d.text((tx, 152), 'THE RULE:', font=ft, fill=(255, 255, 255, 255))
        d.text((tx + tw + 4, 166), '™', font=K.ffont(K.SERIF_B, 48), fill=(255, 214, 90, 255))
        # gold underline swoosh
        pts = [(tx + 10 + i * (tw - 20) / 40, 302 + 6 * math.sin(i / 40 * math.pi) - 3 * i / 40) for i in range(41)]
        d.line(pts, fill=(255, 205, 80, 255), width=7, joint='curve')
        # cheesy handshake clip-art + legal line
        fl = K.inter(21, 'Medium'); lg = K.tracked('© AGENCY INC. · ALL RIGHTS RESERVED', fl, (150, 170, 220), 3)
        im.alpha_composite(lg, ((CW - lg.width) // 2, CH - 50))
        # sheen + border, then the rounded mask
        sheen = np.clip(1 - np.abs(np.linspace(-1, 1, CW)[None, :] * .8 + np.linspace(-1, 1, CH)[:, None] * .6 + .35) * 2.2, 0, 1) * .10
        s_im = Image.new('RGBA', (CW, CH), (255, 255, 255, 0)); s_im.putalpha(Image.fromarray((sheen * 255).astype(np.uint8)))
        im.alpha_composite(s_im)
        m = _card_mask(); im.putalpha(m.point(lambda v: int(v * .95)))
        b = Image.new('L', (CW, CH)); ImageDraw.Draw(b).rounded_rectangle((1, 1, CW - 2, CH - 2), 46, outline=255, width=3)
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', (CW, CH), 255)] * 3 + [b.point(lambda v: int(v * .55))]))
        return im
    return E.cached('H2_card_base', mk)

def tick_sprite(D):
    def mk():
        S = D * 3; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((4, 4, S - 5, S - 5), fill=(34, 197, 94, 255), outline=(255, 255, 255, 255), width=int(S * .06))
        d.line([(S * .28, S * .52), (S * .44, S * .68), (S * .74, S * .34)], fill=(255, 255, 255, 255), width=int(S * .11), joint='curve')
        im = im.resize((D, D), Image.LANCZOS)
        return K.scaled(E.shadow(im, 8, .5, (0, 5)), 1.0)
    return E.cached(('H2_tick', D), mk)

def footer_img(n_words, wink):
    """'Pick two. 😉' in a cheesy gold italic serif — word by word."""
    def mk():
        f = K.ffont(K.SERIF_I, 106); words = ['Pick', 'two.']
        im = Image.new('RGBA', (CW, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        full = 'Pick two.'; tw = f.getlength(full) + 110; x = (CW - tw) / 2 - 40
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
        xs = [x, x + f.getlength('Pick ')]
        for i in range(n_words):
            ds.text((xs[i] + 5, 32), words[i], font=f, fill=(0, 0, 0, 170))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        for i in range(n_words):
            d.text((xs[i], 26), words[i], font=f, fill=(255, 207, 84, 255))
        if wink:
            e = K.emoji('😉', 96); im.alpha_composite(e, (int(x + f.getlength(full) + 22), 42))
        return im
    return E.cached(('H2_foot', n_words, wink), mk)

def marker_stroke(p0, p1, width, prog, seed):
    """rough red marker stroke from p0 to p1, drawn up to prog (0..1), on a card-size RGBA."""
    def mk(q):
        im = Image.new('L', (CW, CH)); d = ImageDraw.Draw(im); rng = np.random.default_rng(seed)
        n = 40; pts = []
        for i in range(n + 1):
            f = i / n * q; x = lerp(p0[0], p1[0], f); y = lerp(p0[1], p1[1], f)
            nx, ny = -(p1[1] - p0[1]), (p1[0] - p0[0]); L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
            j = math.sin(f * 7 + seed) * 6 + rng.normal(0, 1.2)
            pts.append((x + nx * j, y + ny * j))
        if len(pts) > 1:
            d.line(pts, fill=255, width=width, joint='curve')
            for r_, (x, y) in ((width / 2, pts[0]), (width / 2, pts[-1])): d.ellipse((x - r_, y - r_, x + r_, y + r_), fill=255)
        tex = np.asarray(im, np.float32) / 255
        streak = (np.random.default_rng(seed + 9).random((CH, CW)) * .25 + .82).astype(np.float32)
        a = Image.fromarray((np.clip(tex * streak, 0, 1) * 235).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
        out = Image.new('RGBA', (CW, CH), (232, 30, 48, 0)); out.putalpha(a); return out
    q = round(clamp(prog), 2)
    return E.cached(('H2_mark', p0, p1, width, q, seed), lambda: mk(q))

FRACT = None
def fracture():
    global FRACT
    if FRACT is None:
        FRACT = GK.Fracture(center=(520, 560), size=(CW, CH), seed=5, radials=14,
                            hits=[(T_WRONG, 34, 170, .6, .05)], race=(T_WRONG + .05, 9000), web=(T_WRONG + .10, .16))
    return FRACT

def card_state(t):
    s = dict(show=[0, 0, 0], pop=[1., 1., 1.], lit=[1., 1., 1.], edge=[0., 0., 0.], draw=[0., 0., 0.], tick=[0., 0.],
             foot=0, wink=0, strike=[0., 0., 0.], laser=None)
    s['show'] = [1, 1, 1]; s['draw'] = [1., 1., 1.]; s['lit'] = [0., 0., 0.]
    for i, nm in enumerate(('FAST', 'CHEAP', 'GOOD')):
        tw = Wd[nm]
        if t >= tw - .02:
            q = clamp((t - tw + .02) / .08)
            s['lit'][i] = q * (1 + .6 * K.decay(t, tw + .04, .16))
            s['pop'][i] = 1 + .32 * K.bump((t - tw + .02) / .24)
    # laser dot: glides to the node being said
    if T_PUSH - .05 <= t < J8:
        tgt = [(Wd['FAST'] - .08, 0), (Wd['CHEAP'] - .08, 1), (Wd['GOOD'] - .08, 2)]
        cur = None
        for k_, (tt, i) in enumerate(tgt):
            if t >= tt: cur = (k_, tt, i)
        s['laser'] = cur
    # pick two
    if t >= Wd['PICK'] - .02: s['tick'][0] = clamp((t - Wd['PICK'] + .02) / .14); s['foot'] = 1
    if t >= Wd['TWO'] - .02: s['tick'][1] = clamp((t - Wd['TWO'] + .02) / .14); s['foot'] = 2
    if t >= Wd['TWO'] + .05:
        q = eo((t - Wd['TWO'] - .05) / .2); s['edge'][0] = q * (1 + .5 * K.decay(t, Wd['TWO'] + .25, .15))
        s['draw'][0] = 1.0
        s['lit'][2] = lerp(1, .12, q)
        s['lit'][0] = s['lit'][1] = 1 + .4 * K.decay(t, Wd['TWO'] + .05, .15)
    if t >= 6.74: s['wink'] = 1
    # wrong
    if t >= T_WRONG - .02:
        s['strike'][0] = eo((t - T_WRONG + .02) / .07, 2)
        s['strike'][1] = eo((t - T_WRONG - .05) / .08, 2)
        s['strike'][2] = eo((t - T_WRONG - .12) / .08, 2)
    return s

LASER_POS = None
def card_flat(t):
    s = card_state(t)
    im = card_base().copy()
    # the triangle diagram (kit): nodes pop on their words, lit; dim rods draw between shown nodes
    st = TRI.state(lit=tuple(s['lit']), pop=tuple(s['pop']), edge=tuple(s['edge']), draw=tuple(s['draw']),
                   plate=.6, flow=t * .9 if t >= Wd['TWO'] else None,
                   **TRI.drift(t, .25))
    if any(s['show']):
        tri = K.tri_render(st, TRI_S, at=TRI_C, show=s['show'], canvas=(CW, CH))
        im.alpha_composite(tri)
    # ticks (✓ on FAST and CHEAP)
    for j, nm in enumerate(('fast', 'cheap')):
        q = s['tick'][j]
        if q <= 0: continue
        x, y = TRI.anchor(nm, st, TRI_S, canvas=(CW, CH), at=TRI_C); r = TRI.radius(st, TRI_S, nm, canvas=(CW, CH), at=TRI_C)
        sp = tick_sprite(86); sc = 1 + 1.2 * (1 - K.back(q, 2.2))
        sp = K.scaled(sp, sc)
        im.alpha_composite(K.faded(sp, clamp(q * 3)), (int(x + r * 1.42 - sp.width / 2), int(y - r * .15 - sp.height / 2)))
    # footer
    if s['foot']:
        im.alpha_composite(footer_img(s['foot'], s['wink']), (0, 893))
    # laser dot
    if s['laser'] is not None:
        k_, tt, i = s['laser']
        nm = TRI.NODES[i]; x1, y1 = TRI.anchor(nm, st, TRI_S, canvas=(CW, CH), at=TRI_C)
        if k_ == 0: x0, y0 = 450, 300
        else: x0, y0 = TRI.anchor(TRI.NODES[i - 1], st, TRI_S, canvas=(CW, CH), at=TRI_C)
        q = eo((t - tt) / .10, 2); x, y = lerp(x0, x1, q) + 26, lerp(y0, y1, q) + 30
        x += 3 * math.sin(t * 41); y += 3 * math.cos(t * 37)
        g = K.glow_sprite(56, (255, 30, 40)); im.alpha_composite(g, (int(x - 56), int(y - 56)))
        im.alpha_composite(g, (int(x - 56), int(y - 56)))
        d = ImageDraw.Draw(im); d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=(255, 60, 60, 255)); d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 235, 235, 255))
    # the strike (WRONG)
    if s['strike'][0] > 0:
        im.alpha_composite(marker_stroke((70, 238), (840, 212), 34, s['strike'][0], 3))
    if s['strike'][1] > 0:
        im.alpha_composite(marker_stroke((90, 360), (820, 1010), 46, s['strike'][1], 5))
    if s['strike'][2] > 0:
        im.alpha_composite(marker_stroke((820, 370), (100, 1000), 46, s['strike'][2], 7))
    # the crack (glass deck)
    if t >= T_WRONG:
        a = im.getchannel('A'); rgb = fracture().composite(im, t, refr=1.0, glint=1.0, sparks=1.0)
        im = rgb.convert('RGBA'); im.putalpha(a)
    return im

def card_shadow():
    def mk():
        m = _card_mask(); pad = 80
        a = Image.new('L', (CW + 2 * pad, CH + 2 * pad)); a.paste(m, (pad, pad + 30))
        a = a.filter(ImageFilter.GaussianBlur(34)).point(lambda v: int(v * .65))
        im = Image.new('RGBA', a.size, (0, 0, 0, 0)); im.putalpha(a); return im
    return E.cached('H2_cshadow', mk)

def warp(img, cx, cy, s, ry=0., rx=0., rz=0., f=2600.):
    """project the flat card (centred) into the frame: returns (sprite, x0, y0)."""
    w, h = img.size
    dst = GK.project(w, h, cx, cy, s, rx, ry, rz, f)
    xs, ys = [p[0] for p in dst], [p[1] for p in dst]
    x0, y0 = int(math.floor(min(xs))) - 1, int(math.floor(min(ys))) - 1
    x1, y1 = int(math.ceil(max(xs))) + 1, int(math.ceil(max(ys))) + 1
    co = GK.homography([(0, 0), (w, 0), (w, h), (0, h)], [(x - x0, y - y0) for x, y in dst])
    return img.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BILINEAR), x0, y0

def place_card(ctx, t, cx, cy, s, ry, alpha=1.0, glitch=0.0, rz=0.0, reflect=0.0):
    card = card_flat(t)
    sh = card_shadow(); pad = 80
    sp, x0, y0 = warp(sh, cx + 10 * s, cy + 18 * s, s, ry, rz=rz)
    ctx.add('screen', sp, x0, y0, center=False, alpha=alpha * .9)
    sp, x0, y0 = warp(card, cx, cy, s, ry, rz=rz)
    if glitch > .02:
        a = np.asarray(sp).copy(); rng = np.random.default_rng(int(t * 1000))
        for _ in range(int(3 + 8 * glitch)):
            y = int(rng.integers(0, max(1, a.shape[0] - 40))); hh = int(rng.integers(8, 60))
            a[y:y + hh] = np.roll(a[y:y + hh], int(rng.integers(-60, 60) * glitch), 1)
        k = int(10 * glitch)
        if k: a[..., 0] = np.roll(a[..., 0], k, 1); a[..., 2] = np.roll(a[..., 2], -k, 1)
        sp = Image.fromarray(a, 'RGBA')
    if reflect > .01:                                   # glossy floor: the deck mirrored below, fading out
        rf = sp.transpose(Image.FLIP_TOP_BOTTOM); h = rf.height
        g = (np.clip(1 - np.arange(h, dtype=np.float32) / (h * .42), 0, 1) ** 1.6 * .30 * reflect)[:, None]
        a = (np.asarray(rf.getchannel('A'), np.float32) * g).astype(np.uint8)
        rf = rf.filter(ImageFilter.GaussianBlur(3)); rf.putalpha(Image.fromarray(a))
        ctx.add('screen', rf, x0, y0 + h + 14, center=False)
    ctx.add('screen', sp, x0, y0, center=False, alpha=alpha)
    return sp, x0, y0

# ------------------------------------------------------------------------------------------- shots
def face_cam(ctx, z, fx, fy, av_x=0., rot=0., sx=0., sy=0.):
    """put his face anchor at screen (fx, fy) with zoom z (avatar shifted av_x in the world)."""
    ctx.avatar.update(x=av_x)
    if abs(av_x) > 1: K.edge_shadow(ctx, av_x if av_x > 0 else 1080 + av_x)
    K.set_cam(ctx, z=z, x=K.FACE[0] + av_x, y=K.FACE[1], dx=fx - K.FACE[0] - av_x + sx, dy=fy - K.FACE[1] + sy, rot=rot)

NODE_OFF = ((0., -102.), (-206., 254.), (206., 254.))      # node centres relative to the card centre (card px)
def focus(t):
    """(dx, dy, k): where the camera leans on the deck — the node being said."""
    seq = [(T_PUSH + .25, (0., 0., 0.))] + [(Wd[n] - .04, NODE_OFF[i] + (1.,)) for i, n in enumerate(('FAST', 'CHEAP', 'GOOD'))]
    cur = (0., 0., 0.); prev = cur
    for tt, v in seq:
        if t >= tt: prev, cur, t0 = cur, v, tt
    if t < seq[0][0]: return cur
    q = eio((t - t0) / .28)
    return tuple(lerp(a, b, q) for a, b in zip(prev, cur))

def draw(ctx, lt, t):
    P = ctx.post; P['vignette'] = .36
    wraps = []
    if t < J8:
        # ---- two-shot -> the camera flies into the deck (he exits right)
        u = eo((t - T_PUSH) / .30, 3) if t >= T_PUSH else 0.0
        z = lerp(1.12, 1.16, clamp((t - 3.0) / 1.36)) + .42 * u
        face_cam(ctx, z, lerp(778, 1420, u), lerp(905, 880, u), av_x=232)
        if u > .97: ctx.avatar.update(show=False)
        ctx.bg_dim = .12 + .33 * u; ctx.bg_blur = 9 * u
        # the deck slams in at 3.00 (scale + tilt settle), then the push
        v = clamp((t - 2.96) / .24); k = eo(v, 3)
        s = lerp(.60, .955, u) * (1 + .20 * (1 - k)) + .02 * clamp((t - 4.66) / 1.6)
        ry = lerp(17, 1.5, u) + 24 * (1 - k)
        cx = lerp(300, 540, u) - 110 * (1 - k); cy = lerp(800, 772, u)
        fo = focus(t)                                    # the camera follows the laser to each node on its word
        cx -= fo[0] * .20 * s * u; cy -= fo[1] * .20 * s * u; s *= 1 + .045 * fo[2] * u
        fl = 1 - u                                       # idle float of the deck before the push
        ry += fl * 2.2 * math.sin(2.1 * t + .5); cy += fl * 5 * math.sin(1.7 * t)
        sp, x0, y0 = place_card(ctx, t, cx, cy, s, ry, reflect=u, rz=-fo[0] * .006 * u)
        if t < 3.42: shine(ctx, t, sp, x0, y0)
        if T_PUSH < t < T_PUSH + .3:
            sp_ = (eo((t - T_PUSH + 1 / 60) / .30, 3) - eo((t - T_PUSH - 1 / 60) / .30, 3)) * 30
            if sp_ > .3: wraps.append(lambda fr, L=min(140, 60 * sp_): K.hsmear(fr, L))
        if t < 3.0 + 2 / 30: P['rgb'] = 0.0 if t < 3.0 + 1e-6 else 5.0
    elif t < T_SNAP:
        # ---- the deck front-on (snap at the pose jump: punch + dutch), avatar out, studio blurred
        u = t - J8
        ctx.avatar.update(show=False); ctx.bg_blur = 9; ctx.bg_dim = .45
        K.set_cam(ctx, z=1.0)
        s = .99 + .012 * clamp(u / .95) + .05 * K.decay(t, J8, .07)
        sx, sy = K.shake(t, Wd['PICK'], 5, tau=.08); sx2, sy2 = K.shake(t, Wd['TWO'], 5, tau=.08)
        place_card(ctx, t, 540 + sx + sx2, 762 + sy + sy2, s, 0, rz=-1.3, reflect=1.0)
        if u < .1: wraps.append(lambda fr, q=1 - u / .1: K.hsmear(fr, 200 * q * q))
        P['rgb'] = 4.0 * K.decay(t, J8, .05)
    else:
        # ---- snap-in on him; the deck at his left gets struck + cracked
        u = t - T_SNAP
        z = 1.40 + .05 * eio(u / .77) + K.punch(t, T_SNAP, .06, .08) + K.punch(t, T_WRONG, .06, .11)
        sx, sy = K.shake(t, T_WRONG, 16, tau=.13, f=18)
        face_cam(ctx, z, 735, 960, av_x=150, sx=sx, sy=sy)
        ctx.bg_dim = .15
        gl = K.decay(t, T_WRONG, .09) if t >= T_WRONG else 0
        k = eo(u / .14, 3)
        place_card(ctx, t, 284 + sx * .6 - 120 * (1 - k), 858 + sy * .6, .61 * (1 + .1 * (1 - k)), 24 + 10 * (1 - k), glitch=gl)
        rk = .8 * K.decay(t, T_WRONG, .12)
        if rk > .03: wraps.append(lambda fr, rk=rk: K.tint_edges(fr, rk))
        P['rgb'] = 4.0 * K.decay(t, T_SNAP, .05) + 9.0 * K.decay(t, T_WRONG, .07)
        P['glitch'] = .5 * K.decay(t, T_WRONG + .01, .05) if t >= T_WRONG + .01 else 0
    K.captions(ctx, t, _pages(), cap_y, red=('WRONG.',))
    ctx.wrap = K.compose_wraps(*wraps)

def shine(ctx, t, sp, x0, y0):
    """the cheesy PowerPoint transition: a light bar sweeps across the deck."""
    u = (t - 3.04) / .34
    if not (0 < u < 1): return
    w, h = sp.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    pos = lerp(-.3, 1.3, u) * (w + h * .5)
    m = np.clip(1 - np.abs(xx + yy * .5 - pos) / 70, 0, 1) ** 2 * .55
    a = (np.asarray(sp.getchannel('A'), np.float32) / 255 * m * 255).astype(np.uint8)
    im = Image.new('RGBA', (w, h), (255, 255, 255, 0)); im.putalpha(Image.fromarray(a))
    ctx.add('screen', im, x0, y0, center=False)
