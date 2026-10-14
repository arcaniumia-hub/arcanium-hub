"""s01 — HOOK A1 (0.00–3.00): "FAST. CHEAP. GOOD. You've always had to pick two."

Three hard SNAPS, one per word, each a new framing of his face that covers the take's jump (0.567 / 1.000 / 1.433):
  0.00  frame 1 = his face + the FAST slam already in flight: a glass orb (⚡) + the huge word rocket in from the lens
        (zoom trail) and LAND on "FAST" (0.08): camera punch + shake, light hit, speed streaks rip across the word.
  0.567 snap (tighter, dutch -2.5°): CHEAP + the price-tag orb whip in from the left and land on "CHEAP" (0.65); the tag
        orb swings on its string.
  1.000 snap (wider, dutch +2°): GOOD + the star orb drop in from above and land on "GOOD" (1.10): star glints.
  1.433 snap to the two-shot: he sits right, THE TRIANGLE (sections/_tri.py) assembles on the left — the three orbs he
        just "claimed" fly in from the lens and lock (lit), beams draw, plate fades in.  Captions top band.
  2.22  "PICK": the triangle tilts toward camera, FAST + CHEAP overdrive and their beam shoots FAST -> CHEAP (lands 2.36)
  2.42  "TWO": GOOD goes dead — red ✗ stamps (buzzer), camera punch, red edge light.  2.68–3.00 settled (drift only),
        captions gone by 2.94: clean hard cut into the body at 3.00.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _tri as TRI
from sections import _H_kit as K

START, END = E.span(0, 3)                       # 0.00 – 3.00
W, H = E.W, E.H

# word onsets (timeline s) measured on src/tight16k.raw: 10 ms band envelopes (80-900 Hz / 900-3k / >3.5 kHz) +
# 2.5 ms STFT spectrogram (plosive bursts / fricative onsets)
ONSETS = dict(FAST=0.08, CHEAP=0.65, GOOD=1.10, YOUVE=1.53, ALWAYS=1.65, HAD=1.97, TO=2.11, PICK=2.22, TWO=2.42,
              VOICE_END=2.68)
Wd = ONSETS
J1, J2, J3 = K.jump_t(1), K.jump_t(2), K.jump_t(3)          # 0.5667, 1.0000, 1.4333 (pose jumps -> snaps)
T_BEAM0, T_BEAM1 = Wd['PICK'], Wd['PICK'] + .14              # FAST -> CHEAP beam draws, lands
T_X = Wd['TWO']                                              # GOOD gets the ✗
CAP_END = 2.94
ZOOM_AMP = .5                                                # FAST: extra scale of the group on frame 1 (lens rush)

lerp, clamp, eo, eio = K.lerp, K.clamp, K.eo, K.eio

# ------------------------------------------------------------------------------------------- the three slams
# word, node index, font px, slam kind, onset, shot start, shot end, camera (z, face screen x, y, rot deg)
SLAMS = [
    dict(word='FAST', i=0, px=236, kind='zoom', t=Wd['FAST'], a=0.0, b=J1, cam=(1.30, 540, 932, 0.0), z1=1.345, gy=388),
    dict(word='CHEAP', i=1, px=190, kind='left', t=Wd['CHEAP'], a=J1, b=J2, cam=(1.44, 528, 962, -2.4), z1=1.47, gy=380),
    dict(word='GOOD', i=2, px=200, kind='drop', t=Wd['GOOD'], a=J2, b=J3, cam=(1.20, 552, 918, 2.0), z1=1.235, gy=392),
]
NOTES = ('E6', 'C6', 'G6')

CUES = [
    (0.00, 'whoosh', {'gain': -9}), (Wd['FAST'], 'impact', {'gain': 0}), (Wd['FAST'], 'boom', {'gain': -9}),
    (Wd['FAST'] + .02, 'zoom', {'gain': -13}), (Wd['FAST'] + .03, 'ding', {'note': 'E6', 'gain': -10}),
    (J1, 'swipe', {'gain': -9, 'pan': -.4}), (Wd['CHEAP'], 'impact', {'gain': -1}),
    (Wd['CHEAP'] + .03, 'ding', {'note': 'C6', 'gain': -10}), (Wd['CHEAP'] + .05, 'tick', {'gain': -16, 'pan': -.3}),
    (J2, 'whoosh', {'gain': -11}), (Wd['GOOD'], 'impact', {'gain': -1}),
    (Wd['GOOD'] + .03, 'ding', {'note': 'G6', 'gain': -10}), (Wd['GOOD'] + .04, 'shimmer', {'gain': -13}),
    (J3, 'whoosh', {'gain': -8, 'pan': -.3}), (J3 + .04, 'lock', {'gain': -13, 'pan': -.25}),
    (J3 + .13, 'lock', {'gain': -14, 'pan': -.45}), (J3 + .22, 'lock', {'gain': -14, 'pan': -.05}),
    (J3 + .45, 'shimmer', {'gain': -21, 'pan': -.3}),
    (T_BEAM0 - .02, 'swoosh', {'gain': -11, 'pan': -.3}), (T_BEAM1, 'shing', {'gain': -12, 'pan': -.35}),
    (T_X, 'buzzer', {'gain': -6, 'pan': -.1}), (T_X, 'thud', {'gain': -10}),
]

# ------------------------------------------------------------------------------------------- captions (shot 4)
def _pages():
    def mk():
        P = K.page
        return K.chain([P([("YOU'VE", Wd['YOUVE'], 0), ('ALWAYS', Wd['ALWAYS'], 0)], base=100),
                        P([('HAD', Wd['HAD'], 0), ('TO', Wd['TO'], 0)], base=100),
                        P([('PICK', Wd['PICK'], 1), ('TWO.', Wd['TWO'], 1)], base=112)], CAP_END)
    return E.cached('H1_pages', mk)
CAP_Y = 372

# ------------------------------------------------------------------------------------------- orb sprites (kit)
def orb_sprite(i, lit, size, x=0.0):
    """one node of the triangle kit alone (no label), as a sprite CENTRED on the orb centre."""
    def mk():
        show = [0, 0, 0]; show[i] = 1
        lt = [0., 0., 0.]; lt[i] = lit; xx = [0., 0., 0.]; xx[i] = x
        st = TRI.state(lit=tuple(lt), x=tuple(xx), draw=(0, 0, 0), plate=0, label=0)
        im = K.tri_render(st, size, at=(size / 2, size / 2), show=show, canvas=(size, size))
        cx, cy = TRI.anchor(TRI.NODES[i], st, size, canvas=(size, size), at=(size / 2, size / 2))
        bb = im.getbbox(); hw = int(math.ceil(max(cx - bb[0], bb[2] - cx))); hh = int(math.ceil(max(cy - bb[1], bb[3] - cy)))
        return im.crop((int(round(cx)) - hw, int(round(cy)) - hh, int(round(cx)) + hw, int(round(cy)) + hh))
    return E.cached(('H1_orb', i, lit, size, x), mk)

def _slam_u(t, t_land, dur=.11):
    return clamp((t - (t_land - dur)) / dur)

def _dur(S):
    return .11 if S['a'] == 0 else S['t'] - S['a'] + 1 / 30          # in flight on the shot's first frame

def slam_shot(ctx, t, S):
    P = ctx.post
    z0, fx, fy, rot = S['cam']; tl = S['t']
    # camera: hold framing + slow push, punch on the landing
    z = lerp(z0, S['z1'], eio((t - S['a']) / max(.1, S['b'] - S['a']))) + K.punch(t, tl, .075, .10)
    if S['kind'] == 'zoom': z -= .09 * (1 - eo(t / tl, 2))                 # frame 1: the camera rushes in onto the hit
    sx, sy = K.shake(t, tl, 13, tau=.10, f=21, seed=S['i'])
    K.set_cam(ctx, z=z, x=K.FACE[0], y=K.FACE[1], dx=fx - K.FACE[0] + sx, dy=fy - K.FACE[1] + sy, rot=rot)
    ctx.bg_dim = .18
    # ---- layout: [orb] gap [WORD], centred, at y = gy
    word = S['word']; px = S['px']
    wimg = K.big_word(word, px, 'white')
    iw, ih = K.ink_box(word, px)
    D = ih * 1.12; size = D / 2 / TRI.K_ORB
    gap = px * .16; total = D + gap + iw; x0 = 540 - total / 2
    ox, oy = x0 + D / 2, S['gy']; wx, wy = x0 + D + gap + iw / 2, S['gy']
    u = _slam_u(t, tl, _dur(S)); k = eo(u, 3)
    landed = t >= tl
    words = []                                           # drawn after the orb (type on top)
    # ---- word
    if S['kind'] == 'zoom':                              # the whole group rockets in from the lens (about its centre)
        g = 1 + ZOOM_AMP * (1 - k)                       # frame 1 keeps the whole word + orb inside the frame
        gx = lambda x: 540 + (x - 540) * g
        if not landed: img = K.zoom_trail(wimg, g * 1.07, g)
        else: img = K.scaled(wimg, 1 + .045 * K.decay(t, tl, .07) + .03 * clamp((t - tl) / .45))
        words.append((img, gx(wx), wy))
    elif S['kind'] == 'left':
        dx = -820 * (1 - k)
        if not landed:
            v = 820 * 3 * (1 - u) ** 2 / 9 * 1.3
            img, ox_, oy_ = K.mblur(wimg, v, 0); words.append((img, wx + dx + ox_, wy + oy_))
        else:
            sq = K.decay(t, tl, .06)
            words.append((K.scaled(wimg, 1 + .03 * clamp((t - tl) / .4)), wx + 14 * sq, wy))
    else:
        dy = -560 * (1 - k)
        if not landed:
            v = 560 * 3 * (1 - u) ** 2 / 9 * 1.3
            img, ox_, oy_ = K.mblur(wimg, 0, v); words.append((img, wx + ox_, wy + dy + oy_))
        else:
            sq = K.decay(t, tl, .07)
            img = wimg.resize((int(wimg.width * (1 + .06 * sq)), int(wimg.height * (1 - .08 * sq))), Image.BILINEAR)
            words.append((K.scaled(img, 1 + .03 * clamp((t - tl) / .4)), wx, wy + 6 * sq))
    # ---- orb (lands 1 frame after the word, overdrives on the word)
    lit = 1.0 + .6 * K.decay(t, tl + .02, .12)
    osp = orb_sprite(S['i'], round(lit, 2), round(size))
    uo = _slam_u(t, tl + .03, _dur(S) + .03); ko = eo(uo, 3)
    if S['kind'] == 'zoom':
        g2 = 1 + ZOOM_AMP * (1 - ko); so = g2 * (1 + .22 * (1 - ko)); oxx, oyy, ang = 540 + (ox - 540) * g2, oy, 0
    elif S['kind'] == 'left':
        so = 1 + .25 * (1 - ko); oxx, oyy = ox - 900 * (1 - ko), oy
        ang = 34 * math.exp(-(t - tl - .03) / .22) * math.cos(2 * math.pi * 2.4 * (t - tl - .03)) if t >= tl + .03 else 30
    else:
        so = 1 + .2 * (1 - ko); oxx, oyy, ang = ox, oy - 620 * (1 - ko), 0
    so *= 1 + .14 * K.bump((t - tl - .03) / .16)
    img = K.scaled(K.rotated(osp, ang), so)
    if S['kind'] == 'zoom' and t < tl + .03: img = K.zoom_trail(img, 1.12, 1.0)
    ctx.add('screen', img, oxx, oyy)
    for img, x, y in words: ctx.add('screen', img, x, y)
    # ---- landing ring
    if t >= tl + .03:
        q = clamp((t - tl - .03) / .32)
        if q < 1: ctx.add('screen', K.ring(D * (.55 + 1.6 * eo(q, 2)), 3, (190, 170, 255), 1), ox, oy, alpha=(1 - q) ** 1.5 * .9)
    # ---- flavour
    if S['kind'] == 'zoom': speed_streaks(ctx, t, tl, wx, wy, iw, ih)
    if S['kind'] == 'drop': glints(ctx, t, tl, wx, wy, iw, ih, ox, oy, D)
    # ---- light hit on the landing (world only -> type stays crisp)
    hk = .30 * K.decay(t, tl, .06) if landed else 0
    wraps = []
    if hk > .02: wraps.append(lambda fr, hk=hk: K.light_hit(fr, hk))
    # cover frame (t = 0) crisp; the first frames of the zoom shot carry a little zoom blur of the world
    if S['kind'] == 'zoom' and 0 < t < tl:
        zb = .30 * (1 - clamp(t / tl))
        if zb > .03: wraps.append(lambda fr, zb=zb: K.zblur(fr, zb, anchor=(540, 700)))
    P['rgb'] = 5.0 * K.decay(t, S['a'], .05) if t > S['a'] + 1e-6 or S['a'] > 0 else 0.0
    return wraps

def speed_streaks(ctx, t, tl, wx, wy, iw, ih):
    """FAST: thin light streaks rip across the word band right after the landing."""
    u = t - tl
    if not (0 <= u < .34): return
    rng = np.random.default_rng(11)
    for j in range(9):
        y = wy + (rng.random() - .5) * ih * 1.5; L = 160 + 420 * rng.random(); d0 = rng.random() * .08
        p = (u - d0) / .26
        if not (0 < p < 1): continue
        x = lerp(1250, -300, eo(p, 2)) + (rng.random() - .5) * 200
        a = (1 - p) * (.55 + .45 * rng.random())
        im = E.cached(('H1_streak', int(L)), lambda L=L: _streak(int(L)))
        ctx.add('screen', im, x, y, alpha=a)

def _streak(L):
    im = Image.new('RGBA', (L + 20, 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(L):
        a = int(255 * (i / L) ** 1.8); d.line((10 + i, 7, 10 + i, 7), fill=(235, 230, 255, a))
    g = im.filter(ImageFilter.GaussianBlur(2.5)); out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(Image.merge('RGBA', (*Image.new('RGB', im.size, (150, 120, 255)).split(), g.getchannel('A'))))
    out.alpha_composite(im); return out

def _star(r):
    def mk():
        n = int(r * 2 + 4); yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
        d = np.hypot(xx, yy) + 1e-3
        a = np.exp(-np.abs(yy) / (r * .045)) * np.clip(1 - np.abs(xx) / r, 0, 1) ** 2 + np.exp(-np.abs(xx) / (r * .045)) * np.clip(1 - np.abs(yy) / r, 0, 1) ** 2
        a = a + .9 * np.exp(-d / (r * .09))
        im = Image.new('RGBA', (n, n), (255, 255, 255, 0)); im.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))); return im
    return E.cached(('H1_star', int(r)), mk)

def glints(ctx, t, tl, wx, wy, iw, ih, ox, oy, D):
    """GOOD: star glints pop on the letters and the orb."""
    pts = [(wx - iw * .30, wy - ih * .42, 0.00, 70), (wx + iw * .38, wy - ih * .10, .06, 52), (ox + D * .28, oy - D * .3, .03, 64),
           (wx + iw * .05, wy + ih * .45, .11, 40)]
    for x, y, d0, r in pts:
        u = (t - tl - d0) / .30
        if 0 < u < 1:
            s = K.bump(u) ** .7
            ctx.add('screen', _star(r).rotate(20 * u, Image.BILINEAR), x, y, alpha=s)

# ------------------------------------------------------------------------------------------- shot 4: the two-shot
AV_X = 280                       # he sits right (GOOD keeps clear of his face, CHEAP label stays inside x >= 70)
TRI_AT = (352, 792)              # triangle box centre (screen); rides only the punches + shake, not the slow push
TRI_SIZE = 600
Z4 = 1.12

def tri_state(t):
    u = (t - J3) / .56; a = .30 + .70 * clamp(u)
    st = dict(lit=[1., 1., 1.], x=[0., 0., 0.], edge=[0., 0., 0.], draw=[1., 1., 1.], assemble=a, flow=t * .9)
    # tilt toward camera on "PICK" (FAST-CHEAP side comes forward)
    k = eo((t - T_BEAM0 + .04) / .30, 3)
    dr = TRI.drift(t, .55)
    st.update(yaw=dr['yaw'] * .6 + lerp(0, -15, k), pitch=dr['pitch'] * .6 + lerp(0, 7, k), roll=dr['roll'] + lerp(0, -3, k))
    if t >= T_BEAM0 - .02:
        st['draw'][0] = eo((t - T_BEAM0) / (T_BEAM1 - T_BEAM0), 2)
        st['edge'][0] = 1.0 + .6 * K.decay(t, T_BEAM1, .14)
        ov = .5 * K.decay(t, T_BEAM0, .16) + .45 * K.decay(t, T_BEAM1, .12)
        st['lit'][0] = st['lit'][1] = 1 + ov
        st['lit'][2] = lerp(1, .35, clamp((t - T_BEAM0) / .12))
    if t >= T_X - .03:
        q = clamp((t - T_X + .03) / .18); st['x'][2] = q; st['lit'][2] = lerp(.35, 0, q)
    st['pop'] = [1., 1., 1. + .18 * K.bump((t - T_X + .03) / .2)]
    for k_ in ('lit', 'x', 'edge', 'draw', 'pop'): st[k_] = tuple(st[k_])
    return TRI.state(**st)

def two_shot(ctx, t):
    P = ctx.post
    ctx.avatar.update(x=AV_X)
    zp = K.punch(t, T_X, .05, .12) + K.punch(t, J3, .05, .08)
    z = lerp(Z4, Z4 + .045, eio((t - J3) / (END - J3))) + zp
    sx, sy = K.shake(t, T_X, 12, tau=.12, f=19, seed=2.0)
    K.set_cam(ctx, z=z, x=540 + AV_X, y=K.FACE[1], dx=sx, dy=sy + 10)
    ctx.bg_dim = .12
    K.edge_shadow(ctx, AV_X)                             # the shifted take's left edge (low in frame)
    st = tri_state(t)
    # the triangle rides the camera punches + shake (screen layer = crisp, no resample); fixed placement otherwise
    zk = 1 + zp / Z4
    ax, ay = TRI_AT[0] + sx, TRI_AT[1] + sy
    im = K.tri_render(st, int(round(TRI_SIZE * zk)), at=(ax, ay))
    ctx.add('screen', im, 0, 0, center=False)
    wraps = []
    if J3 <= t < J3 + .12:                                    # whip in from the right (covers the jump with motion)
        q = 1 - (t - J3) / .12; wraps.append(lambda fr, q=q: K.hsmear(fr, 260 * q * q))
    rk = .75 * K.decay(t, T_X, .10)
    if rk > .03: wraps.append(lambda fr, rk=rk: K.tint_edges(fr, rk))
    P['rgb'] = 5.0 * K.decay(t, J3, .05) + 4.0 * K.decay(t, T_X, .05)
    return wraps

# ------------------------------------------------------------------------------------------- draw
def draw(ctx, lt, t):
    P = ctx.post; P['vignette'] = .36
    wraps = []
    if t < J3:
        S = SLAMS[0] if t < J1 else SLAMS[1] if t < J2 else SLAMS[2]
        wraps += slam_shot(ctx, t, S)
        ctx.captions = False
    else:
        wraps += two_shot(ctx, t)
        K.captions(ctx, t, _pages(), CAP_Y)
    ctx.wrap = K.compose_wraps(*wraps)
