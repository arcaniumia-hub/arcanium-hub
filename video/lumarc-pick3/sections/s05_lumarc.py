"""s05 — LUMARC TAKES THE STAGE + THE PROOF (19.28–31.72).  Author L.  Art in sections/_L_kit.py, triangle = _tri kit.

19.30 A  "At LUMARC, we're AI-first."  THE DROP: lights slam on out of the shattered rule's darkness (lilac flash,
         snap pull-back 1.20 -> 1.0, glints still drifting).  He sits lower; above him the LUMARC glass sign is dead.
         19.38 AT: "AT" pops above the sign · 19.49 LU-: the sign strikes like neon (flicker) · 19.70 -MARC: full
         blaze + bloom + light on the wall.  20.22 WE'RE: the sign lifts to the top, "WE'RE" kicker · 20.46 AI: a
         giant gradient "AI-" rises from BEHIND him (boom, shake, RGB split) · 20.81 FIRST: "FIRST" rises tucked
         behind his head (impact).  A light sweep runs over the lockup.
21.30 B  "Not AI-only."  JUMP -> snap-in close-up (the lockup goes soft behind his head).  21.40 NOT: a frosted pill
         springs up under his chin "NOT" · 21.57 "AI-ONLY." · 21.74 ONLY: a human THUMBPRINT scans into the glass
         button on the left (ridges draw centre-out, ripple) — the human touch.
22.30 C  "AI does the heavy lifting…"  JUMP -> he sits right, the "AI Agent" glass panel swoops up on the left and
         RACES: Editing ✓ Captions ✓ Color ✓ Versions ✓ Formats ✓ Resizing ✓ (bars zip, a ✓ on each syllable AI /
         DOES / THE / HEA- / -VY / LIF-).  22.92 a loaded iron BARBELL drops in; 23.08 HEA-: it slams on the panel
         (thud, jolt, dust ring) · 23.30 LIFTING: a lift field rises off the panel and floats it away effortlessly.
23.84 D  "our team does the thinking."  Whip: the panel flies out left; three glass cards fly OUT OF HIS HEAD (light
         trails = thoughts) into the left column, each landing ON its word: 24.30 TEAM -> STRATEGY · 24.79 DOES ->
         CREATIVITY · 25.16 THINK- -> TASTE; the thought-lines pulse on "thinking".
25.60 E  "So you get content that's faster,"  JUMP -> snap-out, DOF; THE TRIANGLE (kit) assembles beside him (orbs
         lock on YOU / GET, beams on CONTENT) · 26.73 FAST-: FAST lights (overdrive) + speed streaks rip past it.
27.28 F  "costs less…"  27.44 COSTS: a paper price tag "$$$$" pops out of the CHEAP orb into the triangle · 27.78
         LESS: the dollar signs drop off one by one ($$$$ -> $), CHEAP lights, the tag shrinks into the orb, the
         FAST–CHEAP beam lights.
28.36 G  "and looks like this."  28.68 LOOKS: GOOD lights (glints), the last two beams light · 28.79 LIKE: crash
         push toward GOOD, it charges · 28.97 THIS: GOOD EXPLODES — flash, light rays, an iris tears open from the orb.
29.00 MONTAGE (avatar hidden from here), cut on the 140 BPM half-time grid of the montage bed:
         29.00 SILENCE ONE particles materialise into the headphones (out of the explosion) · 29.30 whip -> the
         croissant pull (24 fps) · 29.60 flash -> LUMARC 3D post wall · 29.83 punch -> the burger · 30.07 -> the CASA
         maquette at night · 30.37 whip -> website + carousel mockups · 30.57 the glass CRACKS (breakout kit) and
         30.70 SHATTERS toward the lens -> LETTERBOX HERO: "Introducing SILENCE ONE" in a cinema band, "MADE BY
         lumarc" credit · 31.33 macro of leather + gold with a lens flare · 31.70 last frame (hard cut to s06).
Captions: own word pops in the engine look on the measured onsets (bottom, y 1170, under his chin); A and B use their
kinetic type instead ("AT" + the sign, "WE'RE AI- FIRST" lockup, the "NOT AI-ONLY." pill).  "LIKE THIS." stays over
the first montage shot until the word ends (29.28); then no captions, only the small credit in the letterbox bar.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _tri as TRI
from sections import _L_kit as LK

K = LK.K
GK = E._load('_glasskit_L', os.path.join(E.V, 'lumarc-breakout/sections/_glasskit.py'))
START, END = E.span(20, 27)                      # 19.28 – 31.72
W, H, FPS = E.W, E.H, E.FPS
clamp = E.clamp

# word / syllable onsets measured on src/tight16k.raw (5 ms STFT + 10 ms band envelopes 80-1000 Hz / >3 kHz):
# vowel onsets after pauses, plosive bursts after their closure, fricative starts (f, s, th, h).
ON = dict(
    AT=19.38, LUMARC=19.49, MARC=19.70, RC=19.95, WERE=20.22, AI=20.46, FIRST=20.81, FIRST_V=20.94, END20=21.28,
    NOT=21.40, AI2=21.57, ONLY=21.74, END21=22.22,
    AI3=22.39, DOES=22.76, THE=22.92, HEAVY=22.99, HEA=23.08, VY=23.22, LIFTING=23.30, LIF=23.41, TING=23.59, END22=23.78,
    OUR=24.07, TEAM=24.30, DOES2=24.79, THE2=24.98, THINKING=25.04, THINK=25.16, END23=25.49,
    SO=25.70, YOU=25.94, GET=26.07, CONTENT=26.31, THATS=26.50, FASTER=26.66, FAST=26.73, END24=27.18,
    COSTS=27.44, COSTS_V=27.52, LESS=27.78, END25=28.26,
    AND=28.50, LOOKS=28.68, LIKE=28.79, THIS=28.98, END26=29.30,
)

# first frame of each beat (the avatar shows a segment's pose on the nearest 25 fps source frame: the poses of seg 21
# and 22 surface one frame before their segment start)
J_A, J_B, J_C, J_E, J_X, J_M, J_END = 579, 639, 669, 768, 869, 870, 952
T_B, T_C, T_E = J_B / FPS, J_C / FPS, J_E / FPS
T_WHIP = 23.84                                   # C -> D: the panel whips out (no jump: continuous take)
CUTS = [870, 879, 888, 895, 902, 911, 921, 940]  # montage shots (on the 140 BPM 16th grid from THIS)
J_HIT, J_SHAT = 917, 921                         # glass crack / shatter (M6 -> M7)


def lerp(a, b, k): return a + (b - a) * k
def eo(x, p=3): x = clamp(x); return 1 - (1 - x) ** p
def ei(x, p=2): x = clamp(x); return x ** p
def sm(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def bump(x): x = clamp(x); return math.sin(math.pi * x)
def dec(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def backo(x, s=1.7): x = clamp(x) - 1; return 1 + x * x * ((s + 1) * x + s)
def hr(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def scaled(im, s):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
def shake(t, t0, amp, tau=.16, f=19., seed=0.):
    if t < t0: return 0.0, 0.0
    k = amp * math.exp(-(t - t0) / tau); u = t - t0
    return k * math.sin(2 * math.pi * f * u + seed), k * math.sin(2 * math.pi * f * 1.37 * u + 1.7 + seed)
def w2s(cam, x, y):
    """world point -> (screen x, screen y, scale) through the engine camera (same clamp as compose_world)."""
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return X + (x - cam['x']) * z, Y + (y - cam['y']) * z, z


# ================================================================================================ captions
def _pages():
    P = []
    def page(words, z, cy=1170, base=92, cx=540, maxw=830):        # maxw 830: every line stays inside x 70-960
        ws = [dict(text=tx, emph=em, t0=t0) for tx, em, t0 in words]
        for k, w in enumerate(ws): w['t1'] = ws[k + 1]['t0'] if k + 1 < len(ws) else z - .12
        P.append(dict(words=ws, a=ws[0]['t0'] - .04, z=z, cx=cx, cy=cy, base=base, maxw=maxw))
    page([('AI', 0, ON['AI3']), ('DOES', 0, ON['DOES']), ('THE', 0, ON['THE'])], ON['HEAVY'] - .02)
    page([('HEAVY', 1, ON['HEAVY']), ('LIFTING…', 1, ON['LIFTING'])], T_WHIP + .06)
    page([('OUR', 0, ON['OUR']), ('TEAM', 1, ON['TEAM']), ('DOES', 0, ON['DOES2'])], ON['THE2'] - .02)
    page([('THE', 0, ON['THE2']), ('THINKING.', 1, ON['THINKING'])], T_E - .001)
    page([('SO', 0, ON['SO']), ('YOU', 0, ON['YOU']), ('GET', 0, ON['GET']), ('CONTENT', 0, ON['CONTENT'])], ON['THATS'] - .02, base=82)
    page([("THAT'S", 0, ON['THATS']), ('FASTER,', 1, ON['FASTER'])], ON['COSTS'] - .02)
    page([('COSTS', 0, ON['COSTS']), ('LESS…', 1, ON['LESS'])], ON['AND'] - .02)
    page([('AND', 0, ON['AND']), ('LOOKS', 0, ON['LOOKS'])], ON['LIKE'] - .02)
    page([('LIKE', 0, ON['LIKE']), ('THIS.', 1, ON['THIS'])], ON['END26'] - .02)
    return P
PAGES = _pages()

def font_w(text, sz):
    l, t, r, b = E.font(sz).getbbox(text); return r - l

def _layout(p):
    def mk():
        base = p['base']; ws = p['words']
        def widths(k): return [font_w(w['text'], int(base * k * (1.2 if w['emph'] else 1.0))) for w in ws]
        k = 1.0; tot = sum(widths(1.0)) + base * .34 * (len(ws) - 1)
        if tot > p['maxw']: k = p['maxw'] / tot
        wd = widths(k); tot = sum(wd) + base * k * .34 * (len(ws) - 1); x = p['cx'] - tot / 2; out = []
        for w, ww in zip(ws, wd):
            out.append((w, int(base * k * (1.2 if w['emph'] else 1.0)), x + ww / 2, p['cy'])); x += ww + base * k * .34
        return out
    return E.cached(('L5_lay', id(p)), mk)

def captions(ctx, t, dy=0.0, alpha=1.0):
    for p in PAGES:
        if not (p['a'] <= t < p['z']): continue
        for w, sz, cx, cy in _layout(p):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            a = alpha
            if lt < .05: a *= lt / .05
            if p['z'] - t < .06: a *= max(0, (p['z'] - t) / .06)
            ctx.add('screen', scaled(img, s), cx, cy + dy, alpha=a)


# ================================================================================================ shared looks
def bg_soft(r=5, dim=.22):
    def mk():
        im = E.studio().filter(ImageFilter.GaussianBlur(r))
        return Image.blend(im, Image.new('RGB', im.size, (8, 7, 14)), dim)
    return E.cached(('L5_bgsoft', r, dim), mk)

def seam_shade(xs, ytop, reach=170, amax=.93):
    """(RGBA, y0): the take's own frame cuts his arm off with a hard vertical edge (source x = 0, opaque from source
    y ~1445 down).  When he sits right (C/D x+235, E x+318) that edge lands inside the frame: this world-space falloff
    lets the arm sink into the set's shadow instead (opaque left of the edge, smooth to nothing `reach` px right of it,
    faded in from above).  Place top-left at (0, y0) on the 'front' layer so it rides the camera with him."""
    def mk():
        w = int(xs + reach + 8); y0 = int(ytop - 300); h = H - y0
        xx = np.arange(w, dtype=np.float32)[None, :]; yy = np.arange(h, dtype=np.float32)[:, None] + y0
        hx = 1 - np.clip((xx - (xs - 26)) / (reach + 26), 0, 1); hx = hx * hx * (3 - 2 * hx)
        vy = np.clip((yy - (ytop - 290)) / 330, 0, 1); vy = vy * vy * (3 - 2 * vy)
        im = np.zeros((h, w, 4), np.uint8); im[..., 0], im[..., 1], im[..., 2] = 7, 6, 13
        im[..., 3] = np.clip(hx * vy * amax * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(im, 'RGBA'), y0
    return E.cached(('L5_seam', round(xs, 1), round(ytop, 1), reach, amax), mk)

def shade_seam(ctx, s, x):
    """hide the source-frame edge of the avatar placed at scale s, shift x (bottom-aligned, as the engine places it)."""
    xs = 540 - W * s / 2 + x; ytop = H - H * s + 1440 * s
    img, y0 = seam_shade(xs, ytop)
    ctx.add('front', img, 0, y0, center=False)


def motes(ctx, t, t0, n=26, life=.9, layer='screen'):
    """glints of the shattered rule still drifting through the light (continuity with s04)."""
    u = t - t0
    if u > life: return
    for i in range(n):
        x = 60 + 960 * hr(i, 1) + 40 * math.sin(u * 2 + i); y = 200 + 1300 * hr(i, 2) - 60 * u * (.4 + hr(i, 3))
        a = (1 - u / life) * (.35 + .65 * abs(math.sin(u * (5 + 6 * hr(i, 4)) + i)))
        s = 14 + int(26 * hr(i, 5))
        ctx.add(layer, LK.star(s, (235, 228, 255)), x, y, alpha=a)


# ================================================================================================ A — AT LUMARC, WE'RE AI-FIRST
AS, AY = .90, 60.                               # avatar scale / drop: he sits lower, the lockup owns the top
ZA = 1.115                                      # settled camera zoom of A (hides the scaled avatar's side edges)
def _wy(sy): return 900 + (sy - 900) / ZA        # screen y (at the settled zoom) -> world y
SIGN_Y0, SIGN_Y1, SIGN_S1 = _wy(560), _wy(326), .40   # the sign: big over his head, then lifted to the top (inside y 280+)
KICK_Y, AI_Y, FIRST_Y = _wy(404), _wy(548), _wy(714)
UP0, UP1 = ON['WERE'] - .16, ON['WERE'] + .02

def neon(t):
    j = int(round(t * FPS))
    if j < 585: return 0.0
    seq = {585: .22, 586: .9, 587: .30, 588: .62, 589: .18, 590: .55}
    return seq.get(j, 1.0)

def sign_pose(t):
    up = eo((t - UP0) / (UP1 - UP0), 3) if t >= UP0 else 0.0
    return lerp(SIGN_Y0, SIGN_Y1, up), lerp(1.0, SIGN_S1, up), up

def lockup(ctx, t, layer='behind', blur=False):
    """the sign + kicker + giant type at time t (world coords)."""
    ly, ls, up = sign_pose(t); nl = neon(t)
    ctx.add(layer, K.blob(900, 420, (90, 60, 230), 120, .6), 540, ly + 10,
            alpha=clamp(nl * lerp(.85, .35, up) + .3 * dec(t, ON['MARC'], .3)))
    if nl < .999: ctx.add(layer, scaled(LK.logo_dead(620), ls), 540, ly, alpha=1 - nl * .75)
    if nl > .01:
        lit = LK.logo_lit(620)
        sw = (t - ON['MARC'] - .02) / .45
        if 0 < sw < 1: lit = K.sheen(lit, sw, .12, .7)
        ctx.add(layer, scaled(lit, ls * (1 + .025 * dec(t, ON['MARC'], .12))), 540, ly, alpha=nl)
    # "AT" above the sign (19.38) -> leaves as the sign lifts
    if ON['AT'] - .02 <= t < UP0 + .06:
        k = E.back((t - ON['AT'] + .02) / .18, 1.8); a = clamp((t - ON['AT'] + .02) / .05) * clamp(1 - (t - UP0) / .06)
        ctx.add(layer, scaled(LK.kicker('AT', 66), (.7 + .3 * k) * (1 - .3 * clamp((t - UP0) / .06))), 540, KICK_Y - (SIGN_Y0 - ly), alpha=a)
    # "WE'RE" kicker under the lifted sign
    if t >= ON['WERE'] - .02:
        k = E.back((t - ON['WERE'] + .02) / .18, 1.8)
        ctx.add(layer, scaled(LK.kicker("WE'RE", 56), .7 + .3 * k), 540, KICK_Y, alpha=clamp((t - ON['WERE'] + .02) / .05))
    # giant type rising from behind him
    if t >= ON['AI'] - .02:
        k = expo((t - ON['AI'] + .02) / .30)
        ctx.add(layer, K.blob(1000, 600, (100, 70, 255), 140, .7), 540, 640, alpha=.5 * k + .4 * dec(t, ON['AI'], .25))
        img, _ = K.giant('AI-', 282)
        sw = (t - 21.02) / .36
        if 0 < sw < 1: img = K.sheen(img, sw, .10, .55)
        ctx.add(layer, scaled(img, .93 + .07 * k), 540 + 10, AI_Y + 170 * (1 - k), alpha=clamp((t - ON['AI'] + .02) / .06))
    if t >= ON['FIRST'] - .02:
        k = expo((t - ON['FIRST'] + .02) / .26)
        img, _ = K.giant('FIRST', 236)
        sw = (t - 21.08) / .36
        if 0 < sw < 1: img = K.sheen(img, sw, .10, .55)
        ctx.add(layer, scaled(img, .95 + .05 * k), 540, FIRST_Y + 140 * (1 - k), alpha=clamp((t - ON['FIRST'] + .02) / .05))

def beat_a(ctx, t):
    lt = t - J_A / FPS; P = ctx.post
    ctx.avatar.update(s=AS, y=AY)
    ctx.avatar['bright'] = 1.0 + .10 * dec(t, ON['AI'], .2)
    z = ZA + .20 * (1 - expo(lt / .34)) + .035 * sm((t - 19.62) / 1.66) + .022 * dec(t, ON['AI'], .2) * (t >= ON['AI'])
    sx, sy = shake(t, ON['AI'], 13, .16); sx2, sy2 = shake(t, ON['FIRST'] + .02, 8, .12, seed=1.3)
    ctx.cam = dict(z=z, x=540., y=900., dx=sx + sx2, dy=sy + sy2, rot=0.)
    ctx.bg_dim = .10 + .12 * sm((t - ON['AI']) / .3)
    lockup(ctx, t)
    motes(ctx, t, J_A / FPS, life=.8)
    P['flash'] = .20 * dec(t, J_A / FPS, .03) + .14 * dec(t, ON['AI'], .05) + .10 * dec(t, ON['MARC'], .05)
    P['flash_col'] = (190, 160, 255)
    P['bright'] = 1 + .14 * dec(t, J_A / FPS, .06) + .10 * dec(t, ON['FIRST'] + .02, .08)
    P['rgb'] = 6 * clamp(1 - (t - ON['AI']) / .12) if t >= ON['AI'] else 0.0
    P['vignette'] = .34


# ================================================================================================ B — NOT AI-ONLY
PILL_W, PILL_H, PILL_Y = 740, 134, 1192

def lockup_soft():
    """the A lockup at rest, defocused (backdrop of the close-up)."""
    def mk():
        class _C:
            def __init__(self): self.L = []
            def add(self, layer, img, x, y, center=True, glass=0, alpha=1.0):
                if img is None or alpha <= .01: return
                if alpha < 1: img = E.fade(img, alpha)
                self.L.append((img, x - img.width / 2, y - img.height / 2))
        c = _C(); lockup(c, 21.25)
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for img, x, y in c.L: E._paste(im, dict(img=img, xy=(int(x), int(y)), glass=0))
        return K.soft_blur(im, 9)
    return E.cached('L5_lock_soft', mk)

def pill_img(t):
    p, pad = LK.pill_base(PILL_W, PILL_H)
    im = p.copy(); o = pad
    d0 = 112; cx, cy = o + 14 + d0 // 2, o + PILL_H // 2
    dsk = LK.disc(d0); im.alpha_composite(dsk, (cx - d0 // 2, cy - d0 // 2))
    k = clamp((t - ON['ONLY'] + .02) / .24)
    if k < 1:
        ghost = E.fade(LK.fingerprint(86, 1.0), .16); im.alpha_composite(ghost, (cx - ghost.width // 2, cy - ghost.height // 2))
    if k > 0:
        fp = LK.fingerprint(86, k); im.alpha_composite(fp, (cx - fp.width // 2, cy - fp.height // 2))
    x = o + 14 + d0 + 30
    for txt, emph, t0 in (('NOT', 0, ON['NOT']), ('AI-ONLY.', 1, ON['AI2'])):
        wi, wpad = E.word_img(txt, 76, 'grad' if emph else 'white')
        ww = font_w(txt, 76)
        if t >= t0 - .02:
            lt = t - t0 + .02; s = .72 + .28 * E.back(lt / .16, 1.4); a = clamp(lt / .05)
            w2 = scaled(wi, s); E._paste(im, dict(img=E.fade(w2, a), xy=(int(x + ww / 2 - w2.width / 2), int(cy - w2.height / 2 + 2)), glass=0))
        x += ww + 26
    return im

def beat_b(ctx, t):
    lt = t - T_B; P = ctx.post
    z = 1.42 - .12 * expo(lt / .20) + .03 * sm(lt / 1.0)
    ctx.cam = dict(z=z, x=540., y=880., dx=0., dy=0., rot=0.)
    ctx.bg_img = bg_soft(4, .12)
    ctx.add('behind', lockup_soft(), 540, 960, alpha=.85)
    if t >= ON['NOT'] - .03:
        u = t - ON['NOT'] + .03; k = E.back(u / .22, 1.7)
        ctx.add('screen', scaled(pill_img(t), .62 + .38 * k), 540, PILL_Y + 40 * (1 - eo(u / .2)), glass=14 if u > .1 else 0,
                alpha=clamp(u / .06))
        if t >= ON['ONLY']:                        # the thumb press: ripple from the button
            v = t - ON['ONLY']
            if v < .45:
                bx = 540 - PILL_W / 2 + 14 + 56
                ctx.add('screen', K.ring(30 + 120 * eo(v / .45), 4, (210, 195, 255), (1 - v / .45) * .9), bx, PILL_Y)
    P['flash'] = .12 * dec(t, T_B, .05); P['flash_col'] = (230, 222, 255)
    P['bright'] = 1 + .06 * dec(t, ON['ONLY'], .1)
    P['vignette'] = .36


# ================================================================================================ C/D — AI AGENT + THE TEAM
AV_C = 235.
PX, PY = 318, 812                               # agent panel centre (screen)
TICKS = [ON['AI3'] + .01, ON['DOES'] + .01, ON['THE'] + .01, ON['HEA'], ON['VY'], ON['LIF']]
DROP0, LAND, LIFT0 = 22.92, ON['HEA'], ON['LIFTING'] + .02
KB_W = 470                                       # the barbell's width

def panel_img(t):
    base, pad = LK.agent_base(); im = base.copy(); o = pad
    hot_rows = sum(1 for tk in TICKS if t >= tk)
    for i, (ic, lab) in enumerate(LK.TASKS):
        cy = o + LK.AP_ROW0 + LK.AP_ROWP * i + LK.AP_ROWP // 2
        tk = TICKS[i]; d0 = .22 + .03 * i
        f = 1.0 if t >= tk else (sm((t - (tk - d0)) / d0) ** 1.4)
        done = t >= tk
        li = LK.row_label(lab, done); im.alpha_composite(li, (o + 88, int(cy - li.height / 2)))
        bf = LK.bar_fill((LK.AP_BAR1 - LK.AP_BAR0) * f)
        if bf is not None:
            im.alpha_composite(bf, (o + LK.AP_BAR0, cy - 6))
            if f < 1:
                hx = o + LK.AP_BAR0 + (LK.AP_BAR1 - LK.AP_BAR0) * f
                gl = K.blob(26, 26, (205, 195, 255), 7, .9); im.alpha_composite(gl, (int(hx - gl.width / 2), int(cy - gl.height / 2)))
        if done:
            k = E.back((t - tk) / .18, 2.2)
            cb = scaled(LK.check_badge(), max(.05, .4 + .6 * k))
            im.alpha_composite(cb, (int(o + LK.AP_STAT - cb.width / 2), int(cy - cb.height / 2)))
            if t - tk < .25:
                rg = K.ring(18 + 40 * eo((t - tk) / .25), 2.5, (220, 210, 255), 1 - (t - tk) / .25)
                im.alpha_composite(rg, (int(o + LK.AP_STAT - rg.width / 2), int(cy - rg.height / 2)))
        elif t >= tk - d0 - .2:
            sp = LK.spinner((t * 720 + i * 50) % 360); im.alpha_composite(sp, (int(o + LK.AP_STAT - sp.width / 2), int(cy - sp.height / 2)))
    hot = max([.4 * dec(t, tk, .08) for tk in TICKS if t >= tk] + [0.0])
    if t >= LIFT0 - .06: hot = max(hot, .9 * sm((t - LIFT0 + .06) / .08))
    ob = LK.orb(t, hot); im.alpha_composite(ob, (int(o + LK.AP_ORB[0] - ob.width / 2), int(o + LK.AP_ORB[1] - ob.height / 2)))
    if t >= ON['TING']:                           # all done: a light sweep over the panel
        sw = (t - ON['TING']) / .35
        if sw < 1: im = K.sheen(im, sw, .14, .45)
    return im, pad

def kb_state(t):
    """(x, y, sx, sy, smear) of the kettlebell centre (screen); None when absent."""
    if t < DROP0 or t >= T_WHIP + .02: return None
    X = PX
    kb = LK.barbell(KB_W); YL = PY - LK.AP_H / 2 - kb.height / 2 + 6
    if t < LAND:
        u = (t - DROP0) / (LAND - DROP0); y0 = -kb.height
        y = y0 + (YL - y0) * u * u; v = 2 * (YL - y0) * u / (LAND - DROP0) / FPS
        return X, y, .96, 1.05, min(60, v * .35)
    if t < LIFT0:
        u = t - LAND; sq = .10 * math.exp(-u / .045)
        return X, YL + 6 * math.exp(-u / .05) * math.cos(u * 40), 1 + sq * .7, 1 - sq, 0.0
    u = t - LIFT0
    y = YL - 1150 * ei(u / .52, 2.2) - 6 * math.sin(u * 10)
    return X + 8 * math.sin(u * 7), y, 1.0, 1.0, min(50, 1150 * 2.2 * clamp(u / .52) ** 1.2 / .52 / FPS * .3)

def panel_jolt(t):
    if t < LAND: return 0.0
    u = t - LAND; return 20 * math.exp(-u / .07) * math.cos(u * 2 * math.pi * 4.2)

def draw_agent(ctx, t):
    if t >= T_WHIP + .18: return
    ox = 0.0; smear = 0.0
    if t >= T_WHIP:
        u = (t - T_WHIP) / .16; ox = -1300 * ei(u, 2.2); smear = 160 * bump(min(1, u * 1.3))
    if t < T_C + .26:
        k = expo((t - T_C) / .26); oy = 380 * (1 - k); al = clamp(.3 + k)
    else: oy, al = 0.0, 1.0
    jy = panel_jolt(t)
    im, pad = panel_img(t)
    if smear > 2: im = K.hsmear(im, smear)
    ctx.add('screen', im, PX + ox, PY + oy + jy, glass=16 if (al > .6 and smear < 2) else 0, alpha=al)
    ks = kb_state(t)
    if ks is None: return
    x, y, ksx, ksy, smr = ks
    kb = LK.barbell(KB_W)
    orb_y = PY - LK.AP_H / 2 + oy + jy + 8          # the lift field rises off the panel's top edge
    if t < LAND:                                 # its shadow grows on the panel as it falls
        u = (t - DROP0) / (LAND - DROP0)
        ctx.add('screen', scaled(K.blob(420, 40, (0, 0, 0), 12, .85), .3 + .7 * u), x, PY - LK.AP_H / 2 + 10, alpha=u * u)
    if t >= LIFT0 - .06:                         # tractor beam from the agent orb
        bk = clamp((t - LIFT0 + .06) / .06)
        top = y + kb.height * ksy / 2 - 16
        if orb_y - top > 6:
            bm = LK.beam(orb_y - top, t, 560, 200, 250)
            if smear > 2: bm = K.hsmear(bm, smear)
            ctx.add('screen', bm, x, (orb_y + top) / 2, alpha=bk * (.8 + .2 * math.sin(t * 40)))
    if LAND <= t < LAND + .32:                   # dust puff + sparks off the impact
        u = t - LAND
        for i in range(16):
            a = math.pi * (1.0 + 1.0 * hr(i, 3)); sp = 240 + 480 * hr(i, 4)
            px = x + math.cos(a) * sp * u; py = PY - LK.AP_H / 2 + 6 + math.sin(a) * sp * u * .45 + 700 * u * u
            ctx.add('screen', K.blob(9, 9, (225, 215, 255), 3, 1.0), px, py, alpha=(1 - u / .32))
        rg = K.ring(80 + 220 * eo(u / .3), 5, (230, 220, 255), 1.0); rg = rg.resize((rg.width, max(2, int(rg.height * .22))), Image.BILINEAR)
        ctx.add('screen', rg, x, PY - LK.AP_H / 2 + 8, alpha=(1 - u / .32) * .8)
    wi = scaled(kb, 1) if abs(ksx - 1) < .01 and abs(ksy - 1) < .01 else kb.resize((int(kb.width * ksx), int(kb.height * ksy)), Image.BILINEAR)
    if smr > 1.5: wi = K.vsmear(wi, smr)
    if t >= LIFT0:                               # lit from below by the beam
        wi = wi.copy(); wi.alpha_composite(E.fade(K.glow_of(wi.getchannel('A'), (140, 110, 255), 10, 1.0), .5 * clamp((t - LIFT0) / .1)))
    ctx.add('screen', wi, x, y)

# ---- the team cards (D)
CARD_T = [ON['TEAM'], ON['DOES2'], ON['THINK']]
CARD_X, CARD_Y, CARD_S = 318, [636, 832, 1028], 1.10
SLOT_T = [T_WHIP + .12, T_WHIP + .18, T_WHIP + .24]   # empty glass slots slide in as the panel leaves
HEAD_PT = (690, 556)                             # where the thoughts leave his head (screen): just off the top-left of
                                                 # his hair, so the thought-lines arc left of his face, never across it

def card_pos(i, t):
    """(x, y, scale, alpha) of card i; None before launch."""
    tl = CARD_T[i]; t0 = tl - .22
    if t < t0: return None
    u = clamp((t - t0) / (tl - t0))
    e = eo(u, 2.4)
    cx, cy = (HEAD_PT[0] + CARD_X) / 2 + 40, min(HEAD_PT[1], CARD_Y[i]) - 150
    x = (1 - e) ** 2 * HEAD_PT[0] + 2 * (1 - e) * e * cx + e * e * CARD_X
    y = (1 - e) ** 2 * HEAD_PT[1] + 2 * (1 - e) * e * cy + e * e * CARD_Y[i]
    if t < tl: s = .22 + .78 * e
    else: s = 1 + .08 * math.exp(-(t - tl) / .06) * math.cos((t - tl) * 30)
    return x, y, s, clamp(u * 3)

def thought_line(x0, y0, x1, y1, a, pulse=None):
    """soft light curve (+ a travelling pulse 0..1) from his head (x0, y0) to a card end (x1, y1) -> (img, cx, cy).
    A quadratic arc bowing out to the left (control point left of the card end), so it stays off his face."""
    cx_, cy_ = min(x0, x1) - 34, y0 + .16 * (y1 - y0)
    def bz(u): return ((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx_ + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy_ + u * u * y1)
    pts = [bz(i / 24) for i in range(25)]
    pad = 30; X0 = min(p[0] for p in pts) - pad; Y0 = min(p[1] for p in pts) - pad
    X1 = max(p[0] for p in pts) + pad; Y1 = max(p[1] for p in pts) + pad
    L = Image.new('L', (int(X1 - X0) + 1, int(Y1 - Y0) + 1)); ox, oy = X0, Y0
    d = ImageDraw.Draw(L); d.line([(x - ox, y - oy) for x, y in pts], fill=int(255 * a), width=3, joint='curve')
    if pulse is not None and 0 <= pulse <= 1:
        px, py = bz(pulse); px -= ox; py -= oy
        d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=255)
    g = L.filter(ImageFilter.GaussianBlur(5))
    im = K.colorize(g, (130, 100, 255)); im.alpha_composite(K.colorize(L, (225, 215, 255)))
    return im, ox + im.width / 2, oy + im.height / 2

def slot_img():
    def mk():
        w, h = int(LK.CARD_W * CARD_S), int(LK.CARD_H * CARD_S)
        p, pad = K.panel(w, h, 40, fill=(16, 13, 34), a=.30, border=.0)
        im = p.copy(); im.alpha_composite(K.dashed_rrect(w, h, 40, a=.55), (pad, pad))
        pl = K.icon('plus', 44, (200, 190, 240)); im.alpha_composite(E.fade(pl, .7), (pad + 60, pad + h // 2 - 22))
        return im
    return E.cached('L5_slot', mk)

def draw_cards(ctx, t):
    for i in range(3):                           # empty slots, waiting for the thinking
        if t < SLOT_T[i] or t >= CARD_T[i] + .04: continue
        u = t - SLOT_T[i]; k = eo(u / .2, 3)
        ctx.add('screen', slot_img(), CARD_X - 160 * (1 - k), CARD_Y[i], alpha=k * clamp((CARD_T[i] + .04 - t) / .06))
    for i in range(3):
        cp = card_pos(i, t)
        if cp is None: continue
        x, y, s, a = cp
        tl = CARD_T[i]
        lit = 1.0 if t >= tl else .35
        # the thought-line from his head
        la = .55 * a * (1 if t < tl + .1 else .55) + .45 * dec(t, ON['THINK'], .25)
        pulse = None
        if t >= ON['THINK'] - .02: pulse = ((t - ON['THINK'] + .02) / .30 + i * .12) % 1.0 if t < ON['THINK'] + .6 else None
        ln, lx, ly = thought_line(HEAD_PT[0] - 10, HEAD_PT[1], x + LK.CARD_W * CARD_S / 2 * s - 12, y, clamp(la), pulse)
        ctx.add('screen', ln, lx, ly)
        im = LK.card(i, lit)
        if t >= ON['THINK'] - .02:                # "thinking": a sheen over all three, staggered
            sw = (t - ON['THINK'] + .02 - .05 * i) / .35
            if 0 < sw < 1: im = K.sheen(im, sw, .14, .6)
        ctx.add('screen', scaled(im, s * CARD_S), x, y, glass=12 if (t >= tl and s < 1.1) else 0, alpha=a)
        if t >= tl and t - tl < .3:                # landing ring around the icon disc
            u = t - tl; ctx.add('screen', K.ring(50 + 90 * eo(u / .3), 4, (220, 205, 255), (1 - u / .3) * .9), x - LK.CARD_W * CARD_S / 2 + 84, y)

def beat_cd(ctx, t):
    lt = t - T_C; P = ctx.post
    ctx.avatar.update(x=AV_C)
    shade_seam(ctx, 1.0, AV_C)
    z = 1.16 - .10 * expo(lt / .22) + .045 * sm(lt / 3.2)
    sx, sy = shake(t, LAND, 12, .12, 23)
    wx = 0.0
    if T_WHIP <= t < T_WHIP + .2:               # the whip nudges the camera
        wx = -26 * bump((t - T_WHIP) / .2)
    ctx.cam = dict(z=z, x=540., y=850., dx=sx + wx, dy=sy, rot=0.)
    ctx.bg_img = bg_soft(3, .10)
    draw_agent(ctx, t)
    if t >= SLOT_T[0]: draw_cards(ctx, t)
    captions(ctx, t)
    # light from the panel / beam / cards on his near side
    def wrap(fr):
        k = .12 + .25 * dec(t, LAND, .15) * (t >= LAND) + .2 * dec(t, ON['THINK'], .25) * (t >= ON['THINK'])
        return K.add_light(fr, K.blob(700, 900, (70, 50, 170), 120, 1.0), 300, 860, k)
    ctx.wrap = wrap
    P['flash'] = .12 * dec(t, T_C, .05) + .10 * dec(t, LAND, .04); P['flash_col'] = (230, 222, 255)
    P['bright'] = 1 + .08 * dec(t, LAND, .06)
    P['vignette'] = .34


# ================================================================================================ E/F/G — THE TRIANGLE
AV_E, AV_ES = 318., .94                          # he sits right; his cheek clears the GOOD orb
TSZ, TX, TY = 672, 405, 750                      # triangle box (world): labels x ~ 100-700, y ~ 450-1050
CXE, CYE = 405., 840.                            # camera pivot of E/F/G = the triangle's x: the slow push never drives
                                                 # CHEAP's label out of the safe zone (x >= 70)
ASM0, ASM1 = T_E - .10, T_E + .90               # assemble 0 -> 1 (orbs already in flight on the cut; locks on YOU / GET, beams over CONTENT)
FC_T, CG_T, GF_T = ON['LESS'] + .12, ON['LOOKS'] + .04, ON['LIKE'] + .02
CHARGE0 = ON['LIKE']

def node_lit(t, t0, over=.62, tau=.12):
    if t < t0 - 1 / FPS: return 0.0, 1.0
    u = max(0.0, t - t0)
    return 1 + over * math.exp(-u / tau) * min(1, (t - t0 + 1 / FPS) * FPS), 1 + .24 * bump(u / .26)

def tri_state(t):
    a = clamp((t - ASM0) / (ASM1 - ASM0))
    lf, pf = node_lit(t, ON['FAST']); lc, pc = node_lit(t, ON['LESS']); lg, pg = node_lit(t, ON['LOOKS'])
    if t >= CHARGE0:                              # GOOD charges up before it blows
        ch = ei((t - CHARGE0) / (J_X / FPS - CHARGE0), 1.6); lg = max(lg, 1 + .7 * ch); pg *= 1 + .16 * ch
    edge = (clamp((t - FC_T) / .12), clamp((t - CG_T) / .12), clamp((t - GF_T) / .12))
    d = TRI.drift(t, .6)
    return TRI.state(assemble=a, lit=(lf, lc, lg), pop=(pf, pc, pg), edge=edge, flow=t * .9,
                     yaw=d['yaw'] - 6, pitch=d['pitch'] + 3, roll=d['roll'])

def cam_e(t):
    lt = t - T_E
    z = 1.16 - .16 * expo(lt / .22) + .045 * sm(lt / 3.2)
    dx = dy = 0.0
    if t >= CHARGE0:                              # crash push toward GOOD: zoom about GOOD's screen point
        z0 = z; k = ei((t - CHARGE0) / (J_X / FPS - CHARGE0 + .04), 2.0)
        z += .34 * k
        gx, gy = TRI.anchor('good', tri_state(CHARGE0), TSZ, canvas=(W, H), at=(TX, TY))
        px, py = CXE + (gx - CXE) * z0, CYE + (gy - CYE) * z0
        dx, dy = px - CXE - (gx - CXE) * z, py - CYE - (gy - CYE) * z
    return dict(z=z, x=CXE, y=CYE, dx=dx, dy=dy, rot=0.)

def streaks(ctx, t, fx, fy):
    """speed lines ripping past the FAST orb (right -> left) on FASTER."""
    u = t - ON['FAST'] + .03
    if u < 0 or u > .55: return
    for i in range(11):
        d0 = .03 * hr(i, 7); v = (u - d0) / .28
        if v < 0 or v > 1: continue
        y = fy + (hr(i, 2) - .5) * 170; L = 300 + 420 * hr(i, 3); th = 5 + 8 * hr(i, 4)
        x = fx + 520 - 1300 * eo(v, 1.6)
        ctx.add('screen', LK.streak(L, th, a=1.0), x + L / 2, y, alpha=(1 - v) * (.55 + .45 * hr(i, 5)) * clamp(u / .04))

def draw_tag(ctx, t, st, cam):
    """CHEAP: the "$$$$" tag pops out of the orb (COSTS), sheds its dollars (LESS) and shrinks back in."""
    if t < ON['COSTS'] - .03 or t > ON['LESS'] + .50: return
    cx, cy, z = w2s(cam, *TRI.anchor('cheap', st, TSZ, canvas=(W, H), at=(TX, TY)))
    gx, gy, _ = w2s(cam, *TRI.anchor('center', st, TSZ, canvas=(W, H), at=(TX, TY)))
    tx, ty = gx + 10, gy + 34
    u = t - ON['COSTS'] + .03
    if t < ON['LESS'] + .18:
        e = eo(u / .16, 2.4); x = lerp(cx, tx, e); y = lerp(cy, ty, e) - 60 * bump(min(1, u / .16)); s = .2 + .8 * E.back(u / .2, 1.6)
    else:
        v = (t - ON['LESS'] - .18) / .30; e = ei(v, 2.0)
        x = lerp(tx, cx, e); y = lerp(ty, cy, e); s = lerp(.62, .05, e)
    n = 4; drops = [ON['LESS'], ON['LESS'] + .06, ON['LESS'] + .12]
    for k, td in enumerate(drops):
        if t >= td: n = 3 - k
    if t >= ON['LESS']: s *= lerp(1.0, .62, eo((t - ON['LESS']) / .2))
    rot = 9 * math.exp(-max(0, u - .12) / .18) * math.cos(max(0, u - .12) * 26) - 4
    im = LK.tag(n, 250).rotate(rot, Image.BICUBIC, expand=True)
    ctx.add('screen', scaled(im, s * z), x, y, alpha=clamp(u / .05) * (1 - clamp((t - ON['LESS'] - .40) / .1)))
    for k, td in enumerate(drops):                # the shed dollar signs fall away
        v = t - td
        if 0 <= v < .45:
            dl = LK.dollar(int(64 * z)).rotate(-40 * v * (1 if k % 2 else -1), Image.BICUBIC, expand=True)
            ctx.add('screen', dl, tx + 70 - 30 * k + 60 * v * (1 if k % 2 else -1), ty - 10 + 900 * v * v + 40 * v, alpha=1 - v / .45)

def sparkles(ctx, t, gx, gy, z):
    u = t - ON['LOOKS'] + .02
    if u < 0 or u > .7: return
    for i in range(7):
        d0 = .05 * i; v = (u - d0) / .35
        if v < 0 or v > 1: continue
        a = 2 * math.pi * hr(i, 9); r = (60 + 90 * hr(i, 8)) * z
        s = int((26 + 40 * hr(i, 6)) * z * (.4 + .6 * bump(v)))
        ctx.add('screen', LK.star(max(8, s)), gx + math.cos(a) * r, gy + math.sin(a) * r, alpha=bump(v))

def th_e(ctx, t):
    """talking head with the triangle (E/F/G): sets ctx (cam, avatar, bg, wrap, screen layers)."""
    P = ctx.post
    ctx.avatar.update(s=AV_ES, x=AV_E)
    shade_seam(ctx, AV_ES, AV_E)
    cam = cam_e(t); ctx.cam = cam
    ctx.bg_img = bg_soft(5, .20)
    st = tri_state(t)
    bx, by, z = w2s(cam, TX, TY)
    tsz = int(round(TSZ * z / 2)) * 2
    lf, lc, lg = st['lit']
    spill = .10 * max(lf, lc, lg) + .18 * max(0, max(lf, lc, lg) - 1)      # the lit orbs throw light on his near side
    def wrap(fr, st=st, bx=bx, by=by, tsz=tsz, spill=spill):
        if spill > .01: fr = K.add_light(fr, K.blob(520, 900, (90, 60, 220), 110, 1.0), 640, 900, spill)
        return TRI.paste(fr, st, tsz, bx, by, frost=9)
    ctx.wrap = wrap
    fx, fy, _ = w2s(cam, *TRI.anchor('fast', st, TSZ, canvas=(W, H), at=(TX, TY)))
    streaks(ctx, t, fx, fy)
    draw_tag(ctx, t, st, cam)
    gx, gy, _ = w2s(cam, *TRI.anchor('good', st, TSZ, canvas=(W, H), at=(TX, TY)))
    sparkles(ctx, t, gx, gy, z)
    if t >= CHARGE0:                              # GOOD charging: a growing star glint
        k = ei((t - CHARGE0) / (J_X / FPS - CHARGE0), 1.5)
        ctx.add('screen', LK.star(int(120 + 380 * k)), gx, gy, alpha=.35 + .6 * k)
    P['flash'] = .14 * dec(t, T_E, .05) + .06 * dec(t, ON['FAST'], .05) + .05 * dec(t, ON['LESS'], .05) + .06 * dec(t, ON['LOOKS'], .05)
    P['flash_col'] = (230, 222, 255)
    P['bright'] = 1 + .05 * dec(t, ON['FAST'], .08)
    P['vignette'] = .36
    return gx, gy

def beat_e(ctx, t):
    th_e(ctx, t)
    captions(ctx, t)


# ================================================================================================ the explosion + MONTAGE
def m_hyper(src, z=1.0, cx=540, cy=960):
    fr = E.clip(E.HYPER).at(src)
    return E.zoom(fr, z, (cx, cy)) if abs(z - 1) > .002 else fr

def m_croissant(src, z=1.0):
    fr = LK.clip24(E.CROISSANT_PULL).at(src)
    return E.zoom(fr, z, (540, 900)) if abs(z - 1) > .002 else fr

def m_motion(src, z=1.0):
    fr = E.clip(E.MOTION3D).at(src)
    return E.zoom(fr, z, (540, 960)) if abs(z - 1) > .002 else fr

BAND_Y0, BAND_Y1 = 552, 1262                    # the letterbox window (M7): 1080 x 710 ~ 1.52:1
def letterbox(t):
    """M7: SILENCE ONE's launch shot in a cinema band (full-res crop, black bars) -> RGB."""
    u = (t - CUTS[6] / FPS) / ((CUTS[7] - CUTS[6]) / FPS)
    fr = E.clip(E.HYPER).at(8.12 + (t - CUTS[6] / FPS))             # 1x, inside the shot (8.07-8.77)
    fr = E.zoom(fr, 1.0 + .05 * u, (540, 900))
    out = Image.new('RGB', (W, H), (0, 0, 0))
    sy0 = 900 - (BAND_Y1 - BAND_Y0) // 2 - 60
    out.paste(fr.crop((0, sy0, W, sy0 + BAND_Y1 - BAND_Y0)), (0, BAND_Y0))
    return out

def m_shot(j, t):
    """the montage frame at frame j (RGB, before transitions)."""
    if j < CUTS[1]:
        u = (t - CUTS[0] / FPS) / .3
        return m_hyper(22.90 + (t - CUTS[0] / FPS) * 1.9, 1.08 - .08 * eo(u, 2))
    if j < CUTS[2]: return m_croissant(3.92 + (t - CUTS[1] / FPS) * 1.6, 1.0 + .05 * (t - CUTS[1] / FPS) / .3)
    if j < CUTS[3]: return m_motion(8.25 + (t - CUTS[2] / FPS) * 1.0, 1.04)
    if j < CUTS[4]: return LK.burger((t - CUTS[3] / FPS) / .23)
    if j < CUTS[5]: return LK.house_shot((t - CUTS[4] / FPS) / .3)
    if j < CUTS[6]: return LK.mockups((t - CUTS[5] / FPS) / .33)
    if j < CUTS[7]: return letterbox(t)
    u = (t - CUTS[7] / FPS) / .4
    return m_hyper(23.60 + (t - CUTS[7] / FPS), 1.0 + .06 * u)      # leather macro -> hinge flare (the film's own cut)

def whip(img, L, dx):
    out = E.zoom(img, 1.0, dx=dx) if dx else img
    return K.hsmear(out.convert('RGB'), L, keep=True).convert('RGB') if L > 2 else out

# ---- the glass crack + shatter (M6 -> M7)
GL_C = (560, 860)
def frac():
    def mk():
        return GK.Fracture(center=GL_C, size=(W, H), seed=12, radials=16,
                           hits=[(J_HIT / FPS, 40, 260, .7, .03)], race=(J_HIT / FPS + .03, 9000.), web=(J_HIT / FPS + .05, .08))
    return E.cached('L5_frac', mk)
def shards():
    return E.cached('L5_shards', lambda: GK.Shatter(frac(), seed=5, focal=1600., vp=GL_C, wave=12000., speed=1.3))
def glass_img():
    return E.cached('L5_glass', lambda: frac().composite(LK.mockups(1.0), J_SHAT / FPS - .001, refr=.7, leak=.2, glint=1.1, powder=.25).convert('RGBA'))
def tau(t):
    u = max(0.0, t - J_SHAT / FPS + .5 / FPS); return .10 * (1 - math.exp(-u / .03)) + .85 * u

def montage(ctx, t, j):
    P = ctx.post
    ctx.avatar['show'] = False
    fr = m_shot(j, t)
    # ---- transitions
    if j in (877, 878):  fr = whip(fr, (120, 280)[j - 877], (-70, -190)[j - 877])
    if j in (879, 880):  fr = whip(fr, (280, 110)[j - 879], (190, 60)[j - 879])
    if j in (909, 910):  fr = whip(fr, (120, 280)[j - 909], (70, 190)[j - 909])
    if j in (911, 912):  fr = whip(fr, (280, 110)[j - 911], (-190, -60)[j - 911])
    if CUTS[3] <= j < CUTS[3] + 4:              # punch-in onto the burger
        u = (j - CUTS[3]) / 4; fr = E.zoom(fr, 1.0 + .22 * (1 - eo(u, 2)), (540, 900))
        fr = K.zoom_smear(fr.convert('RGBA'), .08 * (1 - u), 540, 900).convert('RGB') if u < .75 else fr
    if J_HIT <= j < J_SHAT:                      # the glass cracks over the mockups
        fr = frac().composite(fr, t, refr=.7, leak=.08 + .12 * (j - J_HIT) / 4, glint=1.1, powder=.25)
    if J_SHAT <= j < J_SHAT + 9:                 # ... and shatters toward the lens: the letterbox behind it
        S = shards(); ta = tau(t); u = t - J_SHAT / FPS + .5 / FPS
        dz = 1300 * u ** 1.1; dzp = 1300 * max(0, u - .5 / FPS) ** 1.1
        if S.visible(ta, dz, 140., 3.6):
            fr = S.render(fr.convert('RGBA'), glass_img(), ta, dz=dz, focus_z=1600., dof=4., shutter_dtau=.012, dz_prev=dzp,
                          spec_gain=.5, cull_scale=3.6).convert('RGB')
    ctx.full = fr
    # ---- overlays
    if j < CUTS[1]:
        captions(ctx, t)                         # "LIKE THIS." still on its word
    if CUTS[6] <= j < CUTS[7]:                   # the credit in the letterbox bar
        a = clamp((t - CUTS[6] / FPS - .08) / .12)
        ctx.add('screen', LK.made_by(1.4), 540, 432, alpha=a)
    fl = 0.0
    for c, k in ((CUTS[2], .55), (CUTS[4], .25), (J_HIT, .22), (CUTS[7], .30)):
        fl = max(fl, k * dec(t, c / FPS, .05))
    P['flash'] = fl; P['flash_col'] = (255, 214, 170) if CUTS[4] <= j < CUTS[5] else (240, 234, 255)
    P['grain'] = 1.2; P['vignette'] = .28


IRIS_R = {870: 360, 871: 820, 872: 1450, 873: 2300}

def burst(gx, gy, k, rays=True):
    """white-violet light burst at (gx, gy): hot core + anamorphic rays (RGBA full frame), strength k."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    im.alpha_composite(E.fade(K.blob(900, 900, (200, 180, 255), 170, 1.0), k), (int(gx - 900 / 2 - 442), int(gy - 900 / 2 - 442)))
    im.alpha_composite(E.fade(K.blob(260, 260, (255, 255, 255), 50, 1.0), k), (int(gx - 130 - 130), int(gy - 130 - 130)))
    if rays:
        st = LK.star(1500, (236, 228, 255)); im.alpha_composite(E.fade(st, k), (int(gx - 750), int(gy - 750)))
    return im

def explode(ctx, t, j):
    """j = J_X ("THIS"): GOOD blows (white-hot burst); J_M..J_M+3: an iris tears open from the orb onto the first shot."""
    gx, gy = th_e(ctx, t if j == J_X else J_X / FPS)
    if j == J_X:
        b = burst(gx, gy, 1.0)
        ctx.wrap = (lambda fr, w0=ctx.wrap, b=b: Image.alpha_composite(w0(fr).convert('RGBA'), b))
        ctx.post['flash'] = .18; ctx.post['flash_col'] = (236, 226, 255); ctx.post['bright'] = 1.22
        captions(ctx, t)
        return
    # the talking-head frame frozen on the blow (crash-zoom smeared) outside, the first montage shot inside the iris
    u = t - J_M / FPS
    th = ctx.compose()
    th = ctx.wrap(th) if ctx.wrap else th
    for L in ctx.screen: E._paste(th, L)
    ctx.screen.clear(); ctx.wrap = None
    th = E.zoom(th.convert('RGB'), 1 + 1.2 * u, (gx, gy))
    th = K.zoom_smear(th.convert('RGBA'), .18 + 1.4 * u, gx, gy).convert('RGB')
    th = Image.blend(th, Image.new('RGB', th.size, (200, 186, 255)), .35)
    shot = m_shot(J_M, t)
    r = IRIS_R.get(j, 2300)
    m = Image.new('L', (W, H)); ImageDraw.Draw(m).ellipse((gx - r, gy - r, gx + r, gy + r), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(8 + r * .01))
    fr = Image.composite(shot, th, m).convert('RGBA')
    if r < 2000:                                 # hot rim of the tear
        rg = K.ring(r, 10 + r * .012, (232, 220, 255), 1.0)
        fr.alpha_composite(rg, (int(gx - rg.width / 2), int(gy - rg.height / 2)))
    fr.alpha_composite(burst(gx, gy, max(0.0, .75 - u * 6), rays=True))
    for i in range(26):                          # sparks of the orb's glass
        a = 2 * math.pi * hr(i, 11); sp = (700 + 1800 * hr(i, 12)) * (u + .03)
        fr.alpha_composite(E.fade(K.blob(14, 14, (245, 238, 255), 4, 1.0), clamp(1 - u / .14)), (int(gx + math.cos(a) * sp - 20), int(gy + math.sin(a) * sp - 20)))
    ctx.full = fr.convert('RGB')
    ctx.avatar['show'] = False
    captions(ctx, t)
    ctx.post.update(flash=.16 * dec(t, J_M / FPS, .03), flash_col=(240, 232, 255), bright=1 + .12 * dec(t, J_M / FPS, .05), vignette=.3, grain=1.1)


# ================================================================================================ draw
def draw(ctx, lt, t):
    j = int(round(t * FPS)); ctx.captions = False
    if j < J_B: beat_a(ctx, t)
    elif j < J_C: beat_b(ctx, t)
    elif j < J_E: beat_cd(ctx, t)
    elif j < J_X: beat_e(ctx, t)
    elif j < J_M + 4: explode(ctx, t, j)
    else: montage(ctx, t, j)


# ================================================================================================ cues
CUES = sorted([
    # A — the drop + the lockup
    (J_A / FPS, 'whoosh', {'gain': -10}), (J_A / FPS, 'shimmer', {'gain': -14}),
    (ON['AT'], 'pop', {'gain': -14}),
    (ON['LUMARC'], 'glitch', {'gain': -16}),                         # neon strikes (flicker)
    (ON['MARC'], 'shing', {'gain': -8}), (ON['MARC'] + .01, 'shimmer', {'gain': -12}),
    (UP0, 'swoosh_up', {'gain': -14}), (ON['WERE'], 'pop', {'gain': -16}),
    (ON['AI'], 'boom', {'gain': -2}), (ON['AI'], 'impact', {'gain': -8}),
    (ON['FIRST'] + .02, 'impact', {'gain': -6}), (ON['FIRST'] + .02, 'thud', {'gain': -12}),
    # B — the pill + the thumbprint
    (T_B, 'snap', {'gain': -10}),
    (ON['NOT'] - .02, 'pop', {'gain': -8}), (ON['AI2'], 'pop', {'gain': -15}),
    (ON['ONLY'], 'tap', {'gain': -4}), (ON['ONLY'] + .02, 'scan', {'gain': -14}),
    # C — the agent + the kettlebell
    (T_C, 'swoosh_up', {'gain': -8}), (ON['AI3'], 'notify', {'gain': -15}),
] + [(tk, 'tick', {'gain': -5, 'pan': -.4 + .1 * i}) for i, tk in enumerate(TICKS)] + [
    (DROP0, 'whoosh', {'gain': -10}),
    (LAND, 'thud', {'gain': 0}), (LAND + .01, 'sub', {'gain': -10}),
    (LIFT0 - .04, 'swoosh_up', {'gain': -9}), (LIFT0, 'shimmer', {'gain': -14}),
    (ON['TING'], 'ding', {'note': 'A6', 'gain': -12}),
    # D — the cards
    (T_WHIP, 'swipe', {'gain': -6, 'pan': -.4}),
] + [(tl - .2, 'swoosh', {'gain': -16, 'pan': -.3}) for tl in CARD_T] + [
    (CARD_T[0], 'pop', {'gain': -6, 'pan': -.35}), (CARD_T[0], 'ding', {'note': 'C6', 'gain': -14}),
    (CARD_T[1], 'pop', {'gain': -6, 'pan': -.35}), (CARD_T[1], 'ding', {'note': 'E6', 'gain': -14}),
    (CARD_T[2], 'pop', {'gain': -6, 'pan': -.35}), (CARD_T[2], 'ding', {'note': 'G6', 'gain': -14}),
    (ON['THINK'] + .02, 'shimmer', {'gain': -12}),
    # E — the triangle assembles, FAST
    (T_E, 'whoosh', {'gain': -8}),
    (ASM0 + .12 * (ASM1 - ASM0) + .02, 'whoosh', {'gain': -14}), (ASM0 + .24 * (ASM1 - ASM0), 'whoosh', {'gain': -14}),
    (ASM0 + .34 * (ASM1 - ASM0), 'lock', {'gain': -7}), (ASM0 + .46 * (ASM1 - ASM0), 'lock', {'gain': -7}),
    (ASM0 + .58 * (ASM1 - ASM0), 'lock', {'gain': -7}),
    (ASM0 + .64 * (ASM1 - ASM0), 'shing', {'gain': -13}), (ASM0 + .76 * (ASM1 - ASM0), 'shing', {'gain': -13}),
    (ASM0 + .88 * (ASM1 - ASM0), 'shing', {'gain': -13}),
    (ON['FAST'], 'ding', {'note': 'E6', 'gain': -8}), (ON['FAST'] - .02, 'whoosh', {'gain': -7}),
    # F — costs less
    (ON['COSTS'], 'pop', {'gain': -10}), (ON['COSTS'] + .02, 'swoosh', {'gain': -14}),
    (ON['LESS'], 'ding', {'note': 'C6', 'gain': -8}),
    (ON['LESS'], 'pop', {'gain': -14}), (ON['LESS'] + .06, 'pop', {'gain': -15}), (ON['LESS'] + .12, 'pop', {'gain': -16}),
    (FC_T, 'shing', {'gain': -12}),
    # G — looks like THIS
    (ON['LOOKS'], 'ding', {'note': 'G6', 'gain': -8}), (ON['LOOKS'] + .02, 'shimmer', {'gain': -12}),
    (CG_T, 'shing', {'gain': -14}), (GF_T, 'shing', {'gain': -14}),
    (CHARGE0, 'riser', {'to': ON['THIS'], 'gain': -10}),
    (ON['THIS'], 'impact', {'gain': 0}), (ON['THIS'], 'glass', {'gain': -8}), (ON['THIS'] + .01, 'boom', {'gain': -3}),
    # MONTAGE — a trailer hit on every cut
    (CUTS[1] / FPS - .07, 'whoosh', {'gain': -9}), (CUTS[1] / FPS, 'taiko', {'gain': -4}),
    (CUTS[2] / FPS, 'impact', {'gain': -6}), (CUTS[2] / FPS, 'shutter', {'gain': -12}),
    (CUTS[3] / FPS, 'taiko', {'gain': -5}), (CUTS[3] / FPS, 'zoom', {'gain': -12}),
    (CUTS[4] / FPS, 'impact', {'gain': -6}),
    (CUTS[5] / FPS - .07, 'swipe', {'gain': -10}), (CUTS[5] / FPS, 'taiko', {'gain': -5}),
    (J_HIT / FPS, 'crack', {'gain': -3}), (J_HIT / FPS, 'knock', {'gain': -8}),
    (J_SHAT / FPS, 'shatter', {'gain': -1, 'dur': 1.0}), (J_SHAT / FPS, 'braam', {'note': 'D2', 'dur': 1.0, 'gain': -5}),
    (J_SHAT / FPS + .01, 'sub', {'gain': -9}),
    (CUTS[7] / FPS, 'taiko', {'gain': -3}), (CUTS[7] / FPS, 'impact', {'gain': -9}),
], key=lambda c: c[0])
