"""_house.py — the SHARED 3D house kit (kit author: house; READ-ONLY for every section owner).

One stylised house — a premium architectural maquette (matte cream walls with hairline panel seams, slim LUMARC-purple
accents, dark slate standing-seam roof, concrete plinth, floating grass lot with a soil edge, soft contact shadows +
fake AO, purple/blue rim light from the studio monitors, warm interior glow) — rendered by a pure numpy/PIL painter's
renderer with a perspective camera.  Its build state is ONE function of the edit timeline, keyed to word onsets measured
on src/tight16k.raw, so the house is the same object in every section.  Sections choose where/how big it is (camera,
placement, cutaways) but never change its state timeline.

API
---
    from sections import _house as HS

    st  = HS.state_at(t)                    # canonical build state at timeline t (dict; see below)
    cam = HS.hero_cam(t)                    # slow cinematic orbit: dict(yaw, pitch, dist, fov, target)
    img = HS.render(st, cam, size=(900, 900), t=t)          # -> PIL RGBA, transparent bg, own soft shadow
    xy  = HS.anchor('door', st, cam, size=(900, 900))        # screen (x, y) of a named 3-D point (labels, pointers)
    HS.BUILD_CUES                           # [(t, kind, params)] one sound cue per build hit — copy those in your span

    cam = dict(yaw=deg, pitch=deg, dist=m, fov=deg, target=(x, y, z), roll=deg, shift=(fx, fy))
        yaw 0 = looking at the front door (front faces +z), yaw > 0 = camera moves to the house's right; pitch > 0 =
        looking down.  The target lands on the image centre (+ shift * size).  World unit = metre: lot 15 x 15 m
        (top at y = 0, 1.1 m thick), house 7.2 x 8.4 m, walls to y 3.4, ridge y 5.7.  Good framings:
            hero (3/4)    HS.hero_cam(t)                                   ~ dict(yaw=32, pitch=24, dist=34, fov=30)
            front         dict(yaw=0, pitch=12, dist=30, fov=30, target=(0, 2.2, 0))
            door close-up dict(yaw=14, pitch=8, dist=11, fov=30, target=(0, 1.6, 3.6))
            top-down-ish  dict(yaw=35, pitch=55, dist=34, fov=30, target=(0, 0, 0))
    render(state, cam, size=(w, h), t=None, ss=2, shadow=True, gap=0.6, glow=1.0, people=True)
        ss     supersampling factor (2 = 2x2 AA; 1 for a cheap preview)
        shadow soft shadow of the floating lot on a virtual ground `gap` m below the lot (gap=0: contact shadow, e.g.
               a model standing on his desk); the house also shadows its own lot (key light from upper-left-front)
        glow   multiplier on the bloom (windows, LEDs, outline trace)
        t      timeline time (video frames in the windows, LED breathing) — defaults to state['t']
    Cost: ~0.12-0.2 s per 900x900 frame at ss=2 (geometry is static and cached; per frame only transforms).
    anchor names: 'door', 'step', 'lot_front', 'lot_center', 'slab', 'roof_peak', 'chimney', 'sign', 'win0'..'win3',
                  'wall_front', 'wall_right'.

state_at(t) keys (all pure functions of t; arrays are per piece, see PIECES):
    t, lot (dict a, dy, s), outline (0..1 trace), outline_a, slab (height 0..~1.04), led (slab LED 0..1),
    drop (per-piece y offset m), pa (per-piece alpha), tex (per-piece content reveal 0..1), roof_dy, roof_a,
    win[7] (window light 0..1; 0..3 = hero windows), vid[7] (video in window 0..1), lights (interior master 0..1),
    door_a, door_ang (deg, 0 closed, ~100 open outward), cta (door CTA light 0..1), sheen (-1 or 0..1 sweep),
    fly (per-piece 0..1: 0 in place, 1 blown away — vanish/return), sink (slab sink 0..1), wind (0..1),
    people_t (s since "pessoas" or -1), logo (0..1), dust [(x, z, age, scale)], phase (str).

Canonical build (measured onsets, edit timeline s — see W_* below):
    3.89 OLHA     the lot rises from below (expo-out), settles on 4.08 SÓ
    6.40 CASA     the house is traced in glowing light lines (wireframe), stays as a ghost guide until the walls are up
    6.99 ALICERCE the concrete plinth extrudes up out of the lot (stone + dust ring); 8.36 POSICIONAMENTO its purple
                  LED edge ignites
    9.57 PAREDES  wall blocks drop row by row (6 rows, 0.13 s apart, each lands with a tiny settle) — row 0 lands ON
                  the word; 10.73 CONTEÚDO the content panels (LUMARC posts) flash in as a ripple; 11.22 the roof
                  (gables + slate panels + chimney) falls and lands (thud + dust)
    11.59 JANELAS hero windows switch on one by one (11.59, 11.80, 12.02, 12.24) — warm interiors
    12.85 VÍDEOS  the four hero windows start playing LUMARC films (SILENCE ONE, croissant pull, teardown)
    13.70 PORTA   the door swings in from wide open and slams shut on the word (rebound)
    15.42 AÇÃO    the door's CTA light (purple LED handle + outline) ignites
    16.34 REPARA  a slow light sheen sweeps across the finished house
    28.37 SEM     lights cut, the wind takes the house piece by piece (roof first, right to left, top down) — the plinth
                  sinks into the lot exactly on 30.29 VAZIO -> empty lot (wind keeps blowing through seg 16)
    32.87 COM     plinth pops back; 32.98 EDIÇÃO every piece rewinds into place (bottom first); 33.40 (-ÇÃO) all lights on
    34.29 PESSOAS the door swings open (warm light spills on the path), 5 maquette figures appear and walk in;
                  34.70 ENTRAM the first one steps through the door (then every 0.14 s)
    37.20 LUMARC  the LUMARC sign above the door lights up (sweep + glow)
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E

V = E.V

# ---------------------------------------------------------------------------------------------- measured word onsets
# measured on src/tight16k.raw (edit timeline): 10 ms RMS + 80-900 Hz / >3.5 kHz band envelopes + spectrogram
# (onset = consonant burst / fricative start; stressed syllable noted where an effect lands on it)
W_OLHA, W_SO = 3.89, 4.08
W_CASA = 6.40
W_ALICERCE, W_CER = 6.99, 7.36                 # "O a|li|CER|ce": word onset / stressed syllable
W_POSIC = 8.36                                  # "posicionamento"
W_PAREDES, W_CONTEUDO, W_UDO = 9.57, 10.73, 10.97
W_JANELAS, W_NE, W_VIDEOS = 11.59, 11.80, 12.85
W_PORTA, W_ACAO = 13.70, 15.42
W_REPARA = 16.34
W_SEM, W_EDICAO15, W_TERRENO, W_VAZIO = 28.37, 28.55, 29.92, 30.29
W_COM, W_EDICAO, W_CAO = 32.87, 32.98, 33.40   # "Com e|di|ÇÃO": the -ÇÃO vowel at 33.40
W_PESSOAS, W_ENTRAM = 34.29, 34.70
W_LUMARC = 37.20

# build choreography derived from the onsets
LOT_T0 = W_OLHA
TRACE_T0, TRACE_DUR = W_CASA, 0.62
SLAB_T0, SLAB_DUR = W_ALICERCE, 0.42
ROW_DT, PERIM_DT, DROP_T, DROP_H = 0.13, 0.24, 0.26, 1.35
TEX_DT = 0.03
ROOF_LAND, ROOF_FALL = 11.22, 0.26
WIN_T = (W_JANELAS, W_NE, 12.02, 12.24)
VID_T = W_VIDEOS
DOOR_SWING = 0.30
VAN_T0, VAN_SPREAD, VAN_DUR = W_SEM + 0.05, 1.33, 0.55
SINK_T0 = W_VAZIO - 0.36
RET_T0, RET_SPREAD, RET_DUR = W_EDICAO - 0.06, 0.30, 0.32
SLAB_RET = W_COM
LIGHTS_BACK = W_CAO

# ---------------------------------------------------------------------------------------------- small maths
def _cl(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def _eo(x): x = _cl(x); return 1 - (1 - x) ** 3
def _expo(x): x = _cl(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def _ei(x): x = _cl(x); return x * x
def _back(x, s=1.7): x = _cl(x) - 1; return 1 + x * x * ((s + 1) * x + s)
def _ss(a, b, x): x = _cl((x - a) / (b - a)); return x * x * (3 - 2 * x)
def _nrm(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def _flick(t, t0, dur=0.10, seed=0):
    """light switching on at t0: two quick flickers then on."""
    if t < t0: return 0.0
    u = (t - t0) / dur
    if u >= 1: return 1.0
    r = np.random.default_rng(seed)
    pat = r.random(4) * .6 + .4
    return float(pat[int(u * 4)]) * (0.35 if int(u * 4) % 2 else 1.0)

# ---------------------------------------------------------------------------------------------- dimensions (metres)
LOT, LOT_TH = 7.5, 1.1
ZH = -0.9                         # house centre z on the lot (front garden 3.6 m)
HX, HZ, WT, RH, NR = 3.6, 4.2, 0.30, 0.50, 6
YS = 0.40                         # plinth top
YW = YS + NR * RH                 # 3.4 wall top
RISE = 2.3; YR = YW + RISE        # ridge 5.7
TH = math.atan2(RISE, HX)
OVH, RT = 0.38, 0.16              # roof overhang, roof panel thickness
FRONT = HZ + ZH                   # 3.3  front wall outer face z
BACK = -HZ + ZH
GAP = 0.013                       # block seam (half-gap per side)
COLF = 2 * HX / 9                 # 0.8  front/back column width
COLS = 2 * (HZ - WT) / 9          # 0.867 side column width

WARM = np.array([255, 196, 122], float)
PURPLE = np.array([154, 77, 255], float); BLUE = np.array([79, 107, 255], float); VIOLET = np.array([106, 85, 255], float)
CREAM = np.array([240, 235, 226], float); CREAM_IN = np.array([214, 208, 198], float)
CONCRETE = np.array([192, 189, 184], float); SLATE = np.array([50, 52, 64], float); SLATE_E = np.array([70, 72, 88], float)
LKEY = _nrm([-0.50, 0.82, 0.38])          # key light (world, fixed "sun" of the maquette)
WIND = _nrm([1.0, 0.0, -0.30])

# ---------------------------------------------------------------------------------------------- assets
_TX = {}
def _tx(key, fn):
    if key not in _TX: _TX[key] = fn()
    return _TX[key]

POSTS = [os.path.join(V, p) for p in (
    'lumarc-showcase/src/assets/carousel_1.png', 'lumarc-therapy/src/assets/croissant_hero.jpg',
    'lumarc-showcase/src/assets/close_food.png', 'lumarc-showcase/src/assets/design_post.png',
    'lumarc-breakout/src/assets/loc2.png', 'lumarc-showcase/src/assets/close_service.png',
    'lumarc-showcase/src/assets/carousel_2.png', 'lumarc-therapy/src/assets/storefront_line.jpg',
    'lumarc-showcase/src/assets/close_skill.png', 'lumarc-breakout/src/assets/loc1.png',
    'lumarc-therapy/src/assets/croissant_oven.jpg', 'lumarc-breakout/src/assets/loc3.png',
    'lumarc-breakout/src/assets/loc5.png', 'lumarc-showcase/src/assets/website.png',
    'lumarc-breakout/src/assets/loc4.png', 'lumarc-breakout/src/assets/loc6.png')]
CROISSANT = os.path.join(V, 'lumarc-therapy/src/assets/croissant_pull.mp4')
# hero windows 0..3 play: (path, offset s, loop s)
WIN_VIDS = [(E.HYPER, 2.0, 7.5), (CROISSANT, 0.0, 3.9), (E.TEARDOWN, 9.0, 7.5), (E.HYPER, 13.0, 7.5)]

def _cover(im, w, h):
    im = im.convert('RGB'); s = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * s + .5)), max(h, int(im.height * s + .5))), Image.LANCZOS)
    x0 = (im.width - w) // 2; y0 = (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))

def _post_tex(i, w, h):
    def mk():
        p = POSTS[i % len(POSTS)]
        im = _cover(Image.open(p), w, h).convert('RGBA') if os.path.exists(p) else Image.new('RGBA', (w, h), (120, 100, 200, 255))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w - 1, h - 1), outline=(236, 231, 222, 255), width=max(2, w // 34))   # printed-tile border
        a = np.asarray(im, np.float32)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        vig = 1 - .18 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        a[..., :3] *= vig[..., None]
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return _tx(('post', i, w, h), mk)

def _noise(n, m, cells, seed):
    r = np.random.default_rng(seed)
    a = r.random((max(2, m // cells), max(2, n // cells))).astype(np.float32)
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((n, m), Image.BICUBIC), np.float32) / 255

def _lot_top_tex():
    """15 x 15 m lot top: fine model-grass + stone path from the step to the front edge (1024 px)."""
    def mk():
        n = 1024; px = n / (2 * LOT)
        g = (_noise(n, n, 2, 1) - .5) * .16 + (_noise(n, n, 24, 2) - .5) * .20 + (_noise(n, n, 160, 3) - .5) * .14
        base = np.array([74, 101, 62], np.float32)
        yel = np.array([104, 118, 66], np.float32)
        m2 = _noise(n, n, 90, 4)[..., None]
        col = base * (1 - m2 * .5) + yel * (m2 * .5)
        col = col * (1 + g[..., None])
        sp = np.random.default_rng(5).random((n, n)) > .985
        col[sp] *= 1.25
        # light rim along the lot edge (grass catches the light where it folds over)
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
        e = np.minimum(np.minimum(xx, n - 1 - xx), np.minimum(yy, n - 1 - yy))
        col *= (1 + .14 * np.clip(1 - e / 7, 0, 1))[..., None]
        im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA')
        d = ImageDraw.Draw(im, 'RGBA')
        # path pavers: x in [-0.62, 0.62], z from the step (4.05) to the lot edge
        z = 4.12; k = 0
        rr = np.random.default_rng(9)
        while z < LOT - 0.15:
            zz = min(z + 0.46, LOT - 0.12)
            x0, x1 = -0.62 + rr.uniform(-.04, .04), 0.62 + rr.uniform(-.04, .04)
            P = [((x0 + LOT) * px, (z + LOT) * px), ((x1 + LOT) * px, (zz + LOT) * px)]
            d.rectangle((P[0][0] + 1, P[0][1] + 2, P[1][0] + 1, P[1][1] + 2), fill=(30, 36, 26, 120))
            c = int(206 + rr.uniform(-8, 6))
            d.rectangle((P[0][0], P[0][1], P[1][0], P[1][1]), fill=(c, c - 4, c - 12, 255))
            z = zz + 0.09; k += 1
        a = np.asarray(im, np.float32)
        a[..., :3] *= (1 + (_noise(n, n, 3, 11) - .5) * .10)[..., None]
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return _tx('lot_top', mk)

def _lot_side_tex():
    """soil strata with a grass fringe folding over the top edge."""
    def mk():
        w, h = 1024, 92
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        n1 = _noise(w, h, 3, 21); n2 = np.asarray(Image.fromarray((_noise(w // 16, h, 2, 22) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        top = np.array([104, 78, 58], np.float32); bot = np.array([52, 40, 34], np.float32)
        col = top * (1 - yy[..., None]) + bot * yy[..., None]
        band = np.sin(yy * 38 + n2 * 5) * .07
        col = col * (1 + band[..., None] + (n1[..., None] - .5) * .22)
        peb = np.random.default_rng(23).random((h, w)) > .992
        col[peb] = col[peb] * 1.45 + 10
        im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA')
        d = ImageDraw.Draw(im)
        r = np.random.default_rng(24)
        fringe = 9 + 5 * _noise(w, 1, 6, 25)[0]
        for x in range(w):            # grass tufts hanging over the edge
            f = fringe[x] + r.uniform(-2.5, 2.5)
            g = int(r.uniform(-12, 12))
            d.line((x, 0, x, f), fill=(70 + g, 98 + g, 58 + g // 2, 255))
        d.line((0, 0, w, 0), fill=(120, 140, 92, 255), width=2)
        return im
    return _tx('lot_side', mk)

def _glass_tex(w, h):
    def mk():
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        a = np.zeros((h, w, 3), np.float32)
        top = np.array([40, 42, 66], np.float32); bot = np.array([14, 15, 24], np.float32)
        v = (yy / h)[..., None]
        a[:] = top * (1 - v) + bot * v
        s = (xx / w + yy / h * .55)                         # diagonal reflection streaks
        a += (np.exp(-((s - .52) / .07) ** 2) * 30 + np.exp(-((s - .70) / .025) ** 2) * 18)[..., None] * np.array([.8, .8, 1.0])
        a += (np.exp(-(((xx - w * .15) / (w * .4)) ** 2 + ((yy - h * .1) / (h * .3)) ** 2)) * 26)[..., None] * (PURPLE / 255)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return _tx(('glass', w, h), mk)

def _warm_tex(w, h, floor=.70):
    def mk():
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w * .5) / (w * .75)) ** 2 + ((yy - h * .22) / (h * .9)) ** 2)
        k = np.clip(1 - r, 0, 1) ** 1.2
        hot = np.array([255, 226, 170], np.float32); mid = np.array([236, 150, 74], np.float32); low = np.array([120, 62, 32], np.float32)
        a = low + (mid - low) * np.clip(k * 1.8, 0, 1)[..., None] + (hot - mid) * np.clip(k * 1.8 - .8, 0, 1)[..., None]
        fl = (yy > h * floor)
        a[fl] = a[fl] * .62
        a[np.abs(yy - h * floor) < max(1, h * .012)] *= .5
        s = (xx / w + yy / h * .55)
        a += (np.exp(-((s - .55) / .06) ** 2) * 22)[..., None]
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return _tx(('warm', w, h, floor), mk)

def _streak(w, h):
    def mk():
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        s = (xx / w + yy / h * .55)
        al = np.exp(-((s - .5) / .06) ** 2) * 70 + np.exp(-((s - .68) / .02) ** 2) * 50
        im = Image.new('RGBA', (w, h), (255, 255, 255, 0)); im.putalpha(Image.fromarray(np.clip(al, 0, 255).astype(np.uint8)))
        return im
    return _tx(('streak', w, h), mk)

def _frame_tex(w, h):
    """window frame overlay: slate frame + slim purple inner line."""
    def mk():
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        b = max(3, int(w * .045))
        d.rectangle((0, 0, w - 1, h - 1), outline=(44, 45, 58, 255), width=b)
        d.rectangle((b, b, w - 1 - b, h - 1 - b), outline=(150, 92, 255, 255), width=max(1, b // 3))
        return im
    return _tx(('frame', w, h), mk)

def _door_tex(on):
    def mk():
        w, h = 80, 200
        im = Image.new('RGBA', (w, h), (46, 46, 60, 255)); d = ImageDraw.Draw(im)
        for x in (w * .33, w * .66):
            d.line((x, 8, x, h - 8), fill=(36, 36, 48, 255), width=2)
            d.line((x + 2, 8, x + 2, h - 8), fill=(62, 62, 78, 255), width=1)
        if on:
            g = E.gradient(6, 64, E.GRAD_LIGHT[::-1]).convert('RGBA')
            im.alpha_composite(g, (w - 16, h // 2 - 32))
            d.rectangle((1, 1, w - 2, h - 2), outline=(170, 120, 255, 255), width=2)
        else:
            d.rectangle((w - 16, h // 2 - 32, w - 10, h // 2 + 32), fill=(112, 112, 132, 255))
            d.rectangle((1, 1, w - 2, h - 2), outline=(60, 60, 76, 255), width=2)
        return im
    return _tx(('door', on), mk)

def _sign_tex():
    def mk():
        w, h = 440, 150
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=(16, 16, 24, 255), outline=(120, 96, 220, 255), width=3)
        lg = E.logo(360); im.alpha_composite(lg, ((w - lg.width) // 2, (h - lg.height) // 2))
        return im
    return _tx('sign', mk)

def _sign_off():
    def mk():
        w, h = 440, 150
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=(22, 22, 30, 255), outline=(60, 60, 76, 255), width=3)
        return im
    return _tx('sign_off', mk)

# ---------------------------------------------------------------------------------------------- geometry (static)
_S8 = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], float)   # idx = 4sx+2sy+sz
FACE_IDX = np.array([[4, 5, 7, 6], [0, 2, 3, 1], [2, 6, 7, 3], [0, 1, 5, 4], [1, 3, 7, 5], [0, 4, 6, 2]])
FACE_AX = np.array([0, 0, 1, 1, 2, 2]); FACE_SG = np.array([1., -1, 1, -1, 1, -1])
# texture corner order (TL, TR, BR, BL seen from outside) of the outer face, per wall
OUT_FACE = {'F': 4, 'R': 0, 'B': 5, 'L': 1}
TEX_CORNERS = {'F': [3, 7, 5, 1], 'R': [7, 6, 4, 5], 'B': [6, 2, 0, 4], 'L': [2, 3, 1, 0]}
WALL_N = {'F': (0, 0, 1), 'R': (1, 0, 0), 'B': (0, 0, -1), 'L': (-1, 0, 0)}

# openings per wall: (kind, id, col0, col1, row0, row1)
OPEN = {'F': [('win', 0, 1, 2, 1, 4), ('door', 0, 4, 4, 0, 3), ('win', 1, 6, 7, 1, 4)],
        'R': [('win', 2, 1, 2, 1, 4), ('win', 3, 5, 6, 1, 4)],
        'B': [('win', 6, 3, 5, 2, 4)],
        'L': [('win', 5, 2, 3, 1, 4), ('win', 4, 5, 6, 1, 4)]}
# content tiles (2 rows tall = 4:5 post): (col, row0)
TILES = {'F': [(0, 2), (8, 2), (3, 0), (5, 0)],
         'R': [(0, 2), (3, 1), (4, 3), (7, 1), (8, 3)],
         'B': [(1, 1), (7, 2)],
         'L': [(1, 2), (4, 1), (7, 3), (0, 0)]}
WALL_ORDER = ['F', 'R', 'B', 'L']

def _cell(wall, c, r0, r1, gap=GAP):
    """centre + half sizes of the wall cell block spanning rows r0..r1 (inclusive)."""
    y0, y1 = YS + r0 * RH + gap, YS + (r1 + 1) * RH - gap
    if wall in 'FB':
        x0 = -HX + c * COLF if wall == 'F' else HX - (c + 1) * COLF
        a, b = x0 + gap, x0 + COLF - gap
        z0, z1 = (FRONT - WT, FRONT) if wall == 'F' else (BACK, BACK + WT)
        return np.array([(a + b) / 2, (y0 + y1) / 2, (z0 + z1) / 2]), np.array([(b - a) / 2, (y1 - y0) / 2, (z1 - z0) / 2])
    zf = HZ - WT + ZH
    if wall == 'R': za, zb = zf - (c + 1) * COLS, zf - c * COLS
    else: za, zb = (-HZ + WT + ZH) + c * COLS, (-HZ + WT + ZH) + (c + 1) * COLS
    a, b = za + gap, zb - gap
    x0, x1 = (HX - WT, HX) if wall == 'R' else (-HX, -HX + WT)
    return np.array([(x0 + x1) / 2, (y0 + y1) / 2, (a + b) / 2]), np.array([(x1 - x0) / 2, (y1 - y0) / 2, (b - a) / 2])

def _opening_quad(wall, c0, c1, r0, r1, depth, grow=0.0):
    """TL, TR, BR, BL (seen from outside) of an opening rectangle at `depth` m into the wall (grow extends it)."""
    y0, y1 = YS + r0 * RH - grow, YS + (r1 + 1) * RH + grow
    if wall in 'FB':
        if wall == 'F':
            xl, xr = -HX + c0 * COLF - grow, -HX + (c1 + 1) * COLF + grow; z = FRONT - depth
            return np.array([[xl, y1, z], [xr, y1, z], [xr, y0, z], [xl, y0, z]])
        xl, xr = HX - c0 * COLF + grow, HX - (c1 + 1) * COLF - grow; z = BACK + depth
        return np.array([[xl, y1, z], [xr, y1, z], [xr, y0, z], [xl, y0, z]])
    zf = HZ - WT + ZH; zb = -HZ + WT + ZH
    if wall == 'R':
        zl, zr = zf - c0 * COLS + grow, zf - (c1 + 1) * COLS - grow; x = HX - depth
        return np.array([[x, y1, zl], [x, y1, zr], [x, y0, zr], [x, y0, zl]])
    zl, zr = zb + c0 * COLS - grow, zb + (c1 + 1) * COLS + grow; x = -HX + depth
    return np.array([[x, y1, zl], [x, y1, zr], [x, y0, zr], [x, y0, zl]])

def _rot(axis, ang):
    a = _nrm(axis); c, s = math.cos(ang), math.sin(ang); x, y, z = a
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])

class _Geo:
    """static house geometry: every rigid piece is a box (centre + 3 half-axis vectors) with per-face albedo."""
    def __init__(self):
        P = []          # dicts
        def add(kind, c, A, alb, **kw):
            d = dict(kind=kind, c=np.asarray(c, float), A=np.asarray(A, float), alb=np.asarray(alb, float), tex=-1,
                     wall='', row=-1, perim=0.0, outer=-1, tc=None, group='', ao=1.0)
            d.update(kw); P.append(d); return len(P) - 1
        # --- slab (plinth) + entrance step
        self.slab = add('slab', (0, YS / 2, ZH), np.diag([HX + .32, YS / 2, HZ + .32]), [CONCRETE] * 6, group='slab')
        self.step = add('step', (0, .1, FRONT + .32 + .26), np.diag([.78, .1, .26]), [CONCRETE * 1.03] * 6, group='slab')
        # --- wall blocks
        perim0 = {'F': 0, 'R': 9, 'B': 18, 'L': 27}
        self.blocks = []; self.cells = {}
        tex_k = 0
        for wall in WALL_ORDER:
            occ = np.zeros((9, NR), int)
            for (kind, i, c0, c1, r0, r1) in OPEN[wall]: occ[c0:c1 + 1, r0:r1 + 1] = -1
            tiles = TILES[wall]
            for c in range(9):
                r = 0
                while r < NR:
                    if occ[c, r] == -1: r += 1; continue
                    tall = (c, r) in tiles
                    r1 = r + 1 if tall else r
                    cc, hh = _cell(wall, c, r, r1)
                    face_alb = [CREAM] * 6
                    o = OUT_FACE[wall]
                    alb = [CREAM_IN if k == (o ^ 1) else CREAM for k in range(6)]
                    ao = 0.90 + 0.10 * min(1, r / 2.0)
                    k = add('block', cc, np.diag(hh), alb, wall=wall, row=r, rows=r1 - r + 1, col=c,
                            perim=perim0[wall] + c, outer=o, tc=TEX_CORNERS[wall], group='wall', ao=ao,
                            tex=(tex_k if tall else -1))
                    if tall: tex_k += 1
                    self.blocks.append(k)
                    for rr in range(r, r1 + 1): self.cells[(wall, c, rr)] = k
                    r = r1 + 1
        # --- sills under each window (attached outside items)
        self.sills = []
        for wall in WALL_ORDER:
            n = np.array(WALL_N[wall], float)
            for (kind, i, c0, c1, r0, r1) in OPEN[wall]:
                if kind != 'win': continue
                q = _opening_quad(wall, c0, c1, r0, r1, 0.0)
                bl, br = q[3], q[2]
                mid = (bl + br) / 2 + n * 0.02 + np.array([0, -0.035, 0])
                along = (br - bl) / 2 * 1.06
                A = np.stack([along, [0, .035, 0], n * 0.075], 1)
                k = add('sill', mid, A, [CREAM * 1.02] * 6, wall=wall, group='attached', win=i)
                self.sills.append(k)
        # --- roof assembly: gables are polys (below), slate panels (6 per slope), ridge cap, chimney
        self.roof = []
        sdir_r = np.array([math.cos(TH), -math.sin(TH), 0]); n_r = np.array([math.sin(TH), math.cos(TH), 0])
        L = (HX + OVH) / math.cos(TH) + .02
        zlen = HZ + OVH; nz = 6; seg = 2 * zlen / nz
        for side in (1, -1):
            sd = sdir_r * np.array([side, 1, 1]); nn = n_r * np.array([side, 1, 1])
            for j in range(nz):
                zc = ZH - zlen + seg * (j + .5)
                c = np.array([0, YR, zc]) + sd * (L / 2) + nn * (RT / 2 + .005)
                A = np.stack([sd * (L / 2), [0, 0, seg / 2 - .012], nn * (RT / 2)], 1)
                k = add('roof', c, A, [SLATE] * 6, group='roof', side=side, j=j)
                self.roof.append(k)
        k = add('ridge', (0, YR + RT * .95, ZH), np.diag([.17, .085, zlen + .02]), [SLATE_E] * 6, group='roof')
        self.roof.append(k); self.ridge = k
        ych = YR - 1.8 * math.tan(TH) + RT / math.cos(TH)
        self.chim = add('chim', (1.8, (ych - .25 + YR + .55) / 2, ZH - 2.3), np.diag([.32, (YR + .55 - (ych - .25)) / 2, .32]),
                        [CREAM * .97] * 6, group='roof')
        self.chimcap = add('chim', (1.8, YR + .59, ZH - 2.3), np.diag([.38, .045, .38]), [SLATE_E] * 6, group='roof')
        self.roof += [self.chim, self.chimcap]
        # --- door (hinged box; transform per frame) + sign plaque (attached)
        self.door = add('door', (0, 0, 0), np.eye(3), [SLATE * 1.05] * 6, group='door')
        self.sign = add('sign', (0, YS + 2.0 + .52, FRONT + .045), np.diag([1.08, .37, .045]), [SLATE * .7] * 6,
                        group='attached', wall='F', outer=4, tc=TEX_CORNERS['F'])
        self.P = P; self.N = len(P)
        self.C0 = np.array([p['c'] for p in P]); self.A0 = np.array([p['A'] for p in P])
        self.ALB = np.array([p['alb'] for p in P])
        self.AO = np.array([p['ao'] for p in P])
        self.kind = np.array([p['kind'] for p in P])
        # gables (triangular prisms, cream) — vertices relative to world; part of the roof assembly
        self.gables = []
        for z0, z1 in ((FRONT - WT, FRONT), (BACK, BACK + WT)):
            vs = np.array([[-HX, YW, z0], [HX, YW, z0], [0, YR, z0], [-HX, YW, z1], [HX, YW, z1], [0, YR, z1]], float)
            faces = [[0, 1, 2], [3, 5, 4], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]]
            self.gables.append(dict(v=vs, faces=faces, c=vs.mean(0), outer=(0 if z1 == FRONT else 1)))
        # panes: windows + doorway interior, with the blocks around each opening (drawn before them)
        self.panes = []
        for wall in WALL_ORDER:
            for (kind, i, c0, c1, r0, r1) in OPEN[wall]:
                nb = set()
                for c in range(c0 - 1, c1 + 2):
                    for r in range(r0 - 1, r1 + 2):
                        if (wall, c, r) in self.cells: nb.add(self.cells[(wall, c, r)])
                if kind == 'win':
                    q = _opening_quad(wall, c0, c1, r0, r1, 0.20, grow=0.02)
                else:
                    q = _opening_quad(wall, c0, c1, r0, r1, WT - .01, grow=0.30)
                w_m = np.linalg.norm(q[1] - q[0]); h_m = np.linalg.norm(q[3] - q[0])
                self.panes.append(dict(kind=kind, id=i, wall=wall, q=q, nb=sorted(nb), w=w_m, h=h_m, rows=(r0, r1),
                                       open=_opening_quad(wall, c0, c1, r0, r1, 0.0), n=np.array(WALL_N[wall], float)))
        self.win_pane = {p['id']: p for p in self.panes if p['kind'] == 'win'}
        self.door_pane = [p for p in self.panes if p['kind'] == 'door'][0]
        # vanish order d in [0, 1]: roof first, then top rows, right (downwind) before left, + jitter
        r = np.random.default_rng(77)
        d = np.zeros(self.N)
        for i, p in enumerate(P):
            x, y = p['c'][0], p['c'][1]
            h = (y - YS) / (YR - YS)
            d[i] = 0.64 * (1 - _cl(h)) + 0.24 * (1 - (x + HX) / (2 * HX)) + 0.12 * r.random()
        d[self.roof] = np.clip(d[self.roof] * .35, 0, None)
        d = (d - d.min()) / (d.max() - d.min())
        self.d = d
        self.fly_axis = np.array([_nrm(r.normal(size=3)) for _ in range(self.N)])
        self.fly_spin = r.uniform(200, 420, self.N) * np.where(r.random(self.N) > .5, 1, -1)
        self.fly_jit = r.normal(size=(self.N, 3)) * np.array([.5, .6, 1.0])
        self.fly_far = r.uniform(.75, 1.3, self.N)
        # block drop times
        self.t_land = np.full(self.N, -1.0)
        for k in self.blocks:
            p = P[k]
            self.t_land[k] = W_PAREDES + p['row'] * ROW_DT + (p['perim'] / 36.0) * PERIM_DT
        tiles = [k for k in self.blocks if P[k]['tex'] >= 0]
        tiles.sort(key=lambda k: (WALL_ORDER.index(P[k]['wall']), P[k]['col']))
        self.t_tex = np.full(self.N, 1e9)
        for j, k in enumerate(tiles): self.t_tex[k] = W_CONTEUDO + j * TEX_DT
        self.tiles = tiles
        # house convex hull planes (for occlusion tests): n.x <= off
        self.hull = [(np.array([1, 0, 0.]), HX + OVH), (np.array([-1, 0, 0.]), HX + OVH), (np.array([0, 0, 1.]), FRONT + OVH),
                     (np.array([0, 0, -1.]), -BACK + OVH), (np.array([0, -1, 0.]), 0.0),
                     (n_r, float(n_r @ np.array([0, YR + RT + .1, 0]))),
                     (n_r * np.array([-1, 1, 1]), float(n_r @ np.array([0, YR + RT + .1, 0])))]
        # outline edges (world segments) with trace start/end fractions
        self.edges = self._edges()

    def _edges(self):
        E_ = []
        def seg(a, b, t0, t1, w=1.0): E_.append((np.array(a, float), np.array(b, float), t0, t1, w))
        x0, x1, z0, z1 = -HX, HX, BACK, FRONT
        bot = [(x0, YS, z1), (x1, YS, z1), (x1, YS, z0), (x0, YS, z0)]
        top = [(x0, YW, z1), (x1, YW, z1), (x1, YW, z0), (x0, YW, z0)]
        for i in range(4): seg(bot[i], bot[(i + 1) % 4], .00 + .05 * i, .16 + .05 * i)
        for i in range(4): seg(bot[i], top[i], .16, .40)
        for i in range(4): seg(top[i], top[(i + 1) % 4], .36 + .03 * i, .52 + .03 * i)
        for z in (z1, z0):
            seg((x0, YW, z), (0, YR, z), .50, .68); seg((x1, YW, z), (0, YR, z), .50, .68)
        seg((0, YR, z1), (0, YR, z0), .64, .80)
        k = 0
        for p in self.panes:
            q = p['open']
            for i in range(4):
                if p['kind'] == 'door' and i == 3: continue
                seg(q[i], q[(i + 1) % 4], .60 + .035 * k, .78 + .035 * k, .8)
            k += 1
        return E_

G = _Geo()
PIECES = G.P
N_PIECES = G.N

# ---------------------------------------------------------------------------------------------- state timeline
def state_at(t):
    """canonical build state of the house at timeline t (pure function of t)."""
    t = float(t); N = G.N
    s = dict(t=t)
    # lot
    q = (t - LOT_T0) / 0.62
    s['lot'] = dict(a=_cl(q * 5), dy=-2.6 * (1 - _expo(q)), s=0.90 + 0.10 * _eo(q)) if q > 0 else dict(a=0., dy=-2.6, s=.9)
    # outline trace + ghost
    s['outline'] = _cl((t - TRACE_T0) / TRACE_DUR)
    ga = 1.0 if t < TRACE_T0 + TRACE_DUR + .25 else 1.0 - .40 * _ss(TRACE_T0 + TRACE_DUR + .25, TRACE_T0 + TRACE_DUR + .7, t)
    ga *= 1 - _ss(10.35, 11.25, t)
    s['outline_a'] = ga if t >= TRACE_T0 else 0.0
    # slab
    qs = (t - SLAB_T0) / SLAB_DUR
    slab = _back(qs, 1.4) if qs > 0 else 0.0
    # vanish / return of the slab: sink into the lot on VAZIO, pop back on COM
    sink = 0.0
    if t >= SINK_T0: sink = _ei((t - SINK_T0) / (W_VAZIO - SINK_T0))
    if t >= SLAB_RET: sink = 1 - _back((t - SLAB_RET) / 0.20, 1.3)
    s['slab'] = slab; s['sink'] = float(sink)
    s['led'] = _flick(t, W_POSIC, .14, 3) * (1 - _ss(W_SEM, W_SEM + .12, t)) + (_flick(t, LIGHTS_BACK, .1, 13) if t >= LIGHTS_BACK else 0)
    s['led'] = min(1.0, s['led'])
    # per-piece drop (blocks), alpha, content reveal
    drop = np.zeros(N); pa = np.ones(N)
    tl = G.t_land; bl = np.array(G.blocks)
    q = (t - (tl[bl] - DROP_T)) / DROP_T
    qq = np.clip(q, 0, 1)
    dy = DROP_H * (1 - (1 - (1 - qq) ** 3))
    u = np.clip((t - tl[bl]) / 0.20, 0, 1)
    dy += 0.045 * np.sin(np.pi * u) * (1 - u) * (u > 0)
    drop[bl] = dy
    pa[bl] = np.clip(q * 4, 0, 1)
    tex = np.clip((t - G.t_tex) / 0.16, 0, 1)
    s['drop'] = drop; s['tex'] = tex
    # roof assembly
    qr = (t - (ROOF_LAND - ROOF_FALL)) / ROOF_FALL
    rdy = 3.2 * (1 - _ei(qr)) if qr < 1 else 0.0
    ur = (t - ROOF_LAND) / .24
    if 0 < ur < 1: rdy += 0.07 * math.sin(math.pi * ur) * (1 - ur)
    s['roof_dy'] = rdy; s['roof_a'] = _cl(qr * 6) if qr > 0 else 0.0
    pa[G.roof] = s['roof_a']
    # sills follow the block below their window
    for k in G.sills:
        pane = G.win_pane[G.P[k]['win']]
        r0 = pane['rows'][0]
        pa[k] = _cl((t - (W_PAREDES + max(0, r0 - 1) * ROW_DT + .25)) / .12)
    pa[G.slab] = pa[G.step] = 1.0 if slab > 0 else 0.0
    # windows / lights / video
    win = np.zeros(7); vid = np.zeros(7)
    for i, tw in enumerate(WIN_T): win[i] = _flick(t, tw, .10, 5 + i)
    win[4:] = _flick(t, WIN_T[3] + .05, .1, 9)
    for i in range(4): vid[i] = _ss(VID_T + .045 * i, VID_T + .045 * i + .12, t)
    lights = _ss(W_JANELAS, W_JANELAS + .8, t)
    # lights cut at SEM, back at -ÇÃO
    off = _cl((t - W_SEM) / .12) if t >= W_SEM else 0.0
    if off > 0:
        f = 1 - off if off < 1 else 0.0
        if 0 < off < 1 and int(off * 6) % 2: f *= .3
        win *= f; vid *= f; lights *= f
    if t >= LIGHTS_BACK:
        on = _flick(t, LIGHTS_BACK, .09, 31)
        win[:] = on; vid[:4] = _ss(LIGHTS_BACK, LIGHTS_BACK + .10, t); lights = on
    s['win'] = win; s['vid'] = vid; s['lights'] = float(lights)
    # door: swings shut ON "porta", opens on "pessoas"
    if t < W_PORTA - DOOR_SWING: da, ang = 0.0, 100.0
    else:
        qd = (t - (W_PORTA - DOOR_SWING)) / DOOR_SWING
        da = _cl(qd * 7)
        ang = 102.0 * (1 - _cl(qd) ** 2.4) if qd < 1 else 0.0
        ud = (t - W_PORTA) / .30
        if 0 < ud < 1: ang += 9.0 * math.sin(math.pi * ud) * (1 - ud) ** 1.5
    if t >= W_PESSOAS - .08:
        ang = 98.0 * _eo((t - (W_PESSOAS - .08)) / .38)
    s['door_a'] = da; s['door_ang'] = ang
    cta = _flick(t, W_ACAO, .12, 17)
    if t >= W_SEM: cta *= 1 - off
    if t >= LIGHTS_BACK: cta = _flick(t, LIGHTS_BACK + .03, .1, 19)
    s['cta'] = cta
    s['sheen'] = (t - W_REPARA) / 0.75 if W_REPARA <= t < W_REPARA + 0.75 else -1.0
    # vanish (fly away) and return (rewind) per piece
    fly = np.zeros(N)
    if t >= VAN_T0:
        st = VAN_T0 + G.d * VAN_SPREAD
        fly = np.clip((t - st) / VAN_DUR, 0, 1)
    if t >= RET_T0 - 1e-9:
        st = RET_T0 + (1 - G.d) * RET_SPREAD
        k = np.clip((t - st) / RET_DUR, 0, 1)
        fly = 1 - (1 - (1 - k) ** 4)            # quart-out back into place
        fly = np.where(t < st, 1.0, fly)
    fly[G.slab] = fly[G.step] = 0.0
    s['fly'] = fly
    s['wind'] = _ss(W_SEM - .1, W_SEM + .5, t) * (1 - _ss(W_COM - .3, W_COM + .1, t))
    s['people_t'] = t - W_PESSOAS if t >= W_PESSOAS else -1.0
    s['logo'] = _ss(W_LUMARC, W_LUMARC + .35, t)
    # dust puffs (x, z, age, scale): plinth landing, roof landing, lot landing
    dust = []
    for (x, z, t0, sc) in ((0, ZH, SLAB_T0 + .08, 1.0), (0, ZH, ROOF_LAND, 0.8), (0, ZH, W_COM + .08, .7)):
        if 0 <= t - t0 < 1.2: dust.append((x, z, t - t0, sc))
    s['dust'] = dust
    s['pa'] = pa
    # phase name (debug / sections)
    for name, t0 in (('lot', LOT_T0), ('outline', TRACE_T0), ('slab', SLAB_T0), ('walls', W_PAREDES - .25),
                     ('roof', ROOF_LAND - ROOF_FALL), ('windows', W_JANELAS), ('door', W_PORTA - DOOR_SWING),
                     ('complete', W_ACAO), ('vanish', W_SEM), ('empty', W_VAZIO), ('return', W_COM),
                     ('people', W_PESSOAS), ('cta', W_LUMARC)):
        if t >= t0: s['phase'] = name
    s.setdefault('phase', 'none')
    return s

# ---------------------------------------------------------------------------------------------- sound cues
BUILD_CUES = [
    (W_OLHA, 'swoosh_up', {'gain': -6}),                     # the lot rises
    (W_SO, 'thud', {'gain': -9}),                            # ...and settles
    (W_CASA, 'shimmer', {'gain': -3}),                       # light-line trace of the house
    (W_CASA + .05, 'swoosh_up', {'gain': -12}),
    (W_ALICERCE + .03, 'stone', {}),                         # plinth extrudes (heavy)
    (W_POSIC, 'switch', {'gain': -9}),                       # plinth LED edge
] + [(round(W_PAREDES + r * ROW_DT, 3), 'block', {'seed': r, 'gain': -2 - r * .5}) for r in range(NR)] + [
    (W_CONTEUDO, 'flick', {'gain': -5}),                     # content panels ripple in
    (W_CONTEUDO + .12, 'pop', {'gain': -12}),
    (ROOF_LAND, 'thud', {}),                                 # roof lands
    (ROOF_LAND + .02, 'stone', {'gain': -10}),
] + [(WIN_T[i], 'switch', {'seed': i, 'gain': -3 - i, 'pan': (-.3, .2, .45, .6)[i]}) for i in range(4)] + [
    (W_VIDEOS, 'flick', {'gain': -4}),                       # windows start playing films
    (W_PORTA, 'door', {}),                                   # door slams shut ON "porta"
    (W_ACAO, 'switch', {'gain': -4}),                        # CTA light
    (W_ACAO + .02, 'shimmer', {'gain': -10}),
    (W_REPARA, 'shimmer', {'gain': -16}),                    # sheen (score is silent here: keep it whisper-quiet)
    (W_SEM, 'switch', {'gain': -6}),                         # lights cut
    (W_SEM, 'wind', {'dur': 4.45}),                          # the wind takes the house (through seg 16)
    (W_VAZIO - .1, 'whoosh', {'gain': -14}),                 # plinth sinks
    (W_COM, 'rewind', {'gain': -3}),                         # the house rewinds back
    (W_EDICAO + .10, 'block', {'seed': 11, 'gain': -6}),
    (W_EDICAO + .24, 'block', {'seed': 12, 'gain': -6}),
    (W_CAO - .03, 'thud', {'gain': -4}),
    (W_CAO, 'switch', {}),                                   # all lights back on
    (W_PESSOAS - .06, 'door', {'gain': -9}),                 # door swings open
    (W_PESSOAS, 'murmur', {'dur': 2.2}),                     # people arriving
    (W_LUMARC, 'switch', {'gain': -5}),                      # LUMARC sign lights
    (W_LUMARC + .03, 'shimmer', {'gain': -6}),
]

# ---------------------------------------------------------------------------------------------- camera
def hero_cam(t):
    """slow cinematic orbit (3/4 from the front-right, drifting right and breathing)."""
    u = _cl((t - 3.5) / 37.0)
    yaw = 24 + 22 * u + 3.0 * math.sin(t * .23)
    pitch = 23 + 2.0 * math.sin(t * .17 + 1.0)
    dist = 34.5 - 1.2 * math.sin(t * .11)
    return dict(yaw=yaw, pitch=pitch, dist=dist, fov=30, target=(0.0, 2.0, -0.2))

class _Cam:
    def __init__(self, cam, W, H):
        cam = cam or hero_cam(0)
        yaw = math.radians(cam.get('yaw', 30)); pit = math.radians(cam.get('pitch', 22))
        T = np.array(cam.get('target', (0, 2.0, -.2)), float); d = float(cam.get('dist', 34))
        self.C = T + d * np.array([math.sin(yaw) * math.cos(pit), math.sin(pit), math.cos(yaw) * math.cos(pit)])
        f = (T - self.C) / d; r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
        roll = math.radians(cam.get('roll', 0.0))
        if roll: r, u = r * math.cos(roll) + u * math.sin(roll), u * math.cos(roll) - r * math.sin(roll)
        self.f, self.r, self.u = f, r, u
        self.focal = (H / 2) / math.tan(math.radians(cam.get('fov', 30)) / 2)
        sh = cam.get('shift', (0, 0))
        self.cx, self.cy = W / 2 + sh[0] * W, H / 2 + sh[1] * H
        self.W, self.H = W, H
        # monitor rim lights live in camera space: purple from behind-left, blue from behind-right
        self.rim_p = _nrm(-0.75 * r + 0.55 * u + 0.55 * f)
        self.rim_b = _nrm(0.75 * r + 0.45 * u + 0.55 * f)
    def proj(self, P):
        D = P - self.C
        z = np.maximum(D @ self.f, 0.05)
        return np.stack([self.cx + self.focal * (D @ self.r) / z, self.cy - self.focal * (D @ self.u) / z], -1), z

def _shade(alb, n, cam, ao=1.0):
    lam = np.clip(n @ LKEY, 0, None)
    sky = np.clip(n[..., 1], 0, None)
    base = 0.50 + 0.52 * lam + 0.10 * sky
    col = alb * (base * ao)[..., None]
    rp = np.clip(n @ cam.rim_p, 0, None) ** 2; rb = np.clip(n @ cam.rim_b, 0, None) ** 2
    col = col + PURPLE * (rp * .42)[..., None] + BLUE * (rb * .40)[..., None]
    return np.clip(col, 0, 255)

# ---------------------------------------------------------------------------------------------- raster helpers
class _Cv:
    """internal canvas: premultiplied colour + coverage, both RGB so that PIL blends RGBA ink 'over' correctly
    (ImageDraw on an RGBA image overwrites instead of blending)."""
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.c = Image.new('RGB', (W, H)); self.a = Image.new('RGB', (W, H)); self.redraw()
    def redraw(self):
        self.dc = ImageDraw.Draw(self.c, 'RGBA'); self.da = ImageDraw.Draw(self.a, 'RGBA')
    def polygon(self, pts, fill, cover=True):
        A = fill[3] if len(fill) > 3 else 255
        if A <= 0: return
        self.dc.polygon(pts, fill=fill)
        if cover: self.da.polygon(pts, fill=(255, 255, 255, A))
    def line(self, pts, fill, width=1, cover=True):
        A = fill[3] if len(fill) > 3 else 255
        if A <= 0: return
        self.dc.line(pts, fill=fill, width=width)
        if cover: self.da.line(pts, fill=(255, 255, 255, A), width=width)
    def ellipse(self, box, fill, cover=True):
        A = fill[3] if len(fill) > 3 else 255
        if A <= 0: return
        self.dc.ellipse(box, fill=fill)
        if cover: self.da.ellipse(box, fill=(255, 255, 255, A))
    def rectangle(self, box, fill, cover=True):
        A = fill[3] if len(fill) > 3 else 255
        if A <= 0: return
        self.dc.rectangle(box, fill=fill)
        if cover: self.da.rectangle(box, fill=(255, 255, 255, A))
    def shade(self, pts, fill):
        """colour-only overlay (on surfaces that are already opaque)."""
        if fill[3] > 0: self.dc.polygon(pts, fill=fill)
    def patch(self, rgba, xy, cover=True):
        m = rgba.getchannel('A')
        self.c.paste(rgba.convert('RGB'), xy, m)
        if cover: self.a.paste((255, 255, 255), (xy[0], xy[1], xy[0] + rgba.width, xy[1] + rgba.height), m)

def _coeffs(dst, src):
    A = np.zeros((8, 8)); B = np.zeros(8)
    for i, ((x, y), (u, v)) in enumerate(zip(dst, src)):
        A[2 * i] = [x, y, 1, 0, 0, 0, -u * x, -u * y]; B[2 * i] = u
        A[2 * i + 1] = [0, 0, 0, x, y, 1, -v * x, -v * y]; B[2 * i + 1] = v
    try: return np.linalg.solve(A, B)
    except np.linalg.LinAlgError: return None

def _mip(img, span):
    if img.width > 2.0 * span and img.width > 48:
        f = int(img.width / (1.5 * span))
        if f > 1:
            return _tx(('mip', id(img), f), lambda: img.resize((max(8, img.width // f), max(8, img.height // f)), Image.BOX))
    return img

def _warp(img, quad, W, H, alpha=1.0):
    """perspective-map img (RGBA) onto screen quad (TL, TR, BR, BL) -> (patch, (x0, y0)) or None."""
    q = np.asarray(quad, float)
    x0, y0 = max(0, int(math.floor(q[:, 0].min()))), max(0, int(math.floor(q[:, 1].min())))
    x1, y1 = min(W, int(math.ceil(q[:, 0].max())) + 1), min(H, int(math.ceil(q[:, 1].max())) + 1)
    w, h = x1 - x0, y1 - y0
    if w < 2 or h < 2 or alpha <= .01: return None
    span = max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]), np.linalg.norm(q[3] - q[0]) * img.width / max(1, img.height), 1)
    img = _mip(img, span)
    co = _coeffs(q - [x0, y0], [(0, 0), (img.width, 0), (img.width, img.height), (0, img.height)])
    if co is None: return None
    out = img.transform((w, h), Image.PERSPECTIVE, tuple(co), Image.BILINEAR)
    if alpha < .999: out.putalpha(out.getchannel('A').point(lambda v: int(v * alpha)))
    return out, (x0, y0)

def _quad_tex(cv, img, quad, alpha=1.0, cover=True):
    r = _warp(img, quad, cv.W, cv.H, alpha)
    if r is not None: cv.patch(r[0], r[1], cover)

def _rgba(c, a=255): return (int(min(255, max(0, c[0]))), int(min(255, max(0, c[1]))), int(min(255, max(0, c[2]))), int(min(255, max(0, a))))

# ---------------------------------------------------------------------------------------------- people
PEOPLE = [(-1.25, 5.10), (1.50, 5.45), (-2.55, 6.35), (2.45, 6.70), (-0.35, 7.10)]
def _people(st):
    """[(feet pos, pop 0..~1.1, walk phase, depth inside the door, idx)] at the state time."""
    out = []
    tp = st['people_t']
    if tp < 0: return out
    door_out = np.array([0.0, 0.0, FRONT + .95]); door_in = np.array([0.0, 0.0, FRONT - 1.6])
    for i, (x, z) in enumerate(PEOPLE):
        t_app = .05 * i; t_arr = (W_ENTRAM - W_PESSOAS) + .14 * i
        if tp < t_app: continue
        start = np.array([x, 0.0, z])
        d1 = np.linalg.norm(door_out - start)
        v = d1 / max(.2, t_arr - t_app)
        v = min(v, 4.2)
        tt = tp - t_app; dist = tt * v
        a = _back(tt / .24, 1.8)
        if dist < d1: p = start + (door_out - start) * (dist / d1)
        else: p = door_out + (door_in - door_out) * min(1.0, (dist - d1) / np.linalg.norm(door_in - door_out))
        inside = max(0.0, FRONT - .05 - p[2])
        if inside > 1.3: continue
        # feet height: lot 0 -> step .2 -> plinth .4
        zz = p[2]
        p = p.copy(); p[1] = 0.0 if zz > FRONT + .32 + .52 else (.2 if zz > FRONT + .32 else YS)
        out.append((p, a, dist / 0.66, inside, i))
    return out

_PTINT = [(238, 234, 226), (228, 224, 238), (244, 238, 228), (232, 230, 224), (236, 228, 240)]
def _draw_person(d, foot, h, phase, i, alpha=1.0, dark=0.0):
    """architectural scale figure (billboard): foot (x, y) screen px, height px."""
    x, y = foot
    if h < 3 or alpha <= .01: return
    a = 255 * _cl(alpha)
    c = np.array(_PTINT[i % 5], float) * (1 - dark) + np.array([34, 22, 18]) * dark
    sh = c * .70
    w = h * .30
    sw = math.sin(phase * math.pi * 2) * .20
    hip = (x, y - h * .50)
    for k, s in ((0, sw), (1, -sw)):
        col = c if k else sh
        fx = x + s * h * .5
        d.polygon([(hip[0] - w * .15, hip[1]), (hip[0] + w * .15, hip[1]), (fx + w * .085, y), (fx - w * .085, y)], fill=_rgba(col, a))
    sy = y - h * .81
    d.polygon([(x - w * .48, sy), (x + w * .48, sy), (x + w * .30, y - h * .46), (x - w * .30, y - h * .46)], fill=_rgba(c, a))
    d.polygon([(x + w * .06, sy), (x + w * .48, sy), (x + w * .30, y - h * .46), (x + w * .06, y - h * .46)], fill=_rgba(sh, a))
    for k, s in ((0, -sw), (1, sw)):
        sx = x + (-1 if k == 0 else 1) * w * .46
        hx = sx + s * h * .32
        d.line([(sx, sy + h * .03), (hx, y - h * .49)], fill=_rgba(c if k == 0 else sh, a), width=max(1, int(w * .19)))
    hr = h * .085
    d.ellipse((x - hr, sy - hr * 2.3, x + hr, sy - hr * .1), fill=_rgba(c, a))
    if dark < .5:
        d.line([(x + w * .48, sy), (x + w * .31, y - h * .46)], fill=_rgba((160, 120, 255), a * .85), width=max(1, int(h / 55)))

# ---------------------------------------------------------------------------------------------- render
def _piece_transforms(st):
    """current centre + axes of every piece (vectorised where it matters)."""
    C = G.C0.copy(); A = G.A0.copy()
    C[:, 1] += st['drop']
    C[G.roof, 1] += st['roof_dy']
    h = max(0.0, st['slab']) * (1 - st['sink'])
    C[G.slab] = [0, YS * h / 2 - .002, ZH]; A[G.slab] = np.diag([HX + .32, max(1e-3, YS * h / 2), HZ + .32])
    hs = min(1.0, max(0.0, st['slab'])) * (1 - st['sink'])
    C[G.step] = [0, .1 * hs - .002, FRONT + .32 + .26]; A[G.step] = np.diag([.78, max(1e-3, .1 * hs), .26])
    q = G.door_pane['open']
    hinge = np.array([q[0][0] + .03, YS, FRONT - .07])
    wdt = (q[1][0] - q[0][0]) - .06; hgt = 2.0 - .03
    a = math.radians(st['door_ang'])
    dv = np.array([math.cos(a), 0, math.sin(a)]); nv = np.array([-math.sin(a), 0, math.cos(a)])
    C[G.door] = hinge + dv * wdt / 2 + np.array([0, hgt / 2, 0]) - nv * .03
    A[G.door] = np.stack([dv * wdt / 2, [0, hgt / 2, 0], nv * .03], 1)
    fly = st['fly']
    for i in np.nonzero(fly > 1e-4)[0]:
        u = fly[i]
        C[i] = C[i] + _fly_off(i, u)
        A[i] = _rot(G.fly_axis[i], math.radians(G.fly_spin[i] * u)) @ A[i] * (1 - .55 * u ** 1.4)
    return C, A

def _fly_off(i, u):
    return WIND * (8.5 * G.fly_far[i] * u * u) + np.array([0, 1, 0]) * (3.2 * u ** 1.5) + G.fly_jit[i] * (1.4 * u)

def _visible_pieces(st):
    pa = st['pa'] * (1 - np.clip((st['fly'] - .55) / .45, 0, 1))
    pa[G.door] = st['door_a'] * (1 - _cl((st['fly'][G.door] - .5) / .5))
    pa[G.sign] = (1.0 - _cl((st['fly'][G.sign] - .5) / .5)) if st['logo'] > 0 else 0.0
    pa[G.slab] = pa[G.step] = (1.0 if st['slab'] > 0 and st['sink'] < .999 else 0.0)
    return pa

def render(state, cam=None, size=(900, 900), t=None, ss=2, shadow=True, gap=0.6, glow=1.0, people=True):
    """the house at `state` seen through `cam` -> PIL RGBA (transparent background, with its own soft shadow)."""
    st = state; t = st['t'] if t is None else t
    Wo, Ho = int(size[0]), int(size[1]); W, H = int(round(Wo * ss)), int(round(Ho * ss))
    lot = st['lot']
    if lot['a'] <= 0: return Image.new('RGBA', (Wo, Ho), (0, 0, 0, 0))
    cam = _Cam(cam, W, H)
    cv = _Cv(W, H)
    gs = 4
    GW, GH = max(1, W // gs), max(1, H // gs)
    glow_l = Image.new('RGB', (GW, GH)); gd = ImageDraw.Draw(glow_l)
    pool_l = Image.new('RGB', (GW, GH)); pd = ImageDraw.Draw(pool_l)
    dy, ls = lot['dy'], lot['s']
    off = np.array([0, dy, 0])
    def LW(P): return np.asarray(P, float) * ls + off
    def pr(P): return cam.proj(LW(P))
    Cw = (cam.C - off) / ls                                   # camera in model space
    # ----- floating shadow under the lot
    if shadow:
        sh = Image.new('L', (GW, GH), 0)
        gy = -LOT_TH - gap; k = 1.0 + gap * .06
        sq = np.array([[-LOT * k, gy, -LOT * k], [LOT * k, gy, -LOT * k], [LOT * k, gy, LOT * k], [-LOT * k, gy, LOT * k]])
        P, _ = cam.proj(sq * ls + off * .3)
        ImageDraw.Draw(sh).polygon([tuple(p / gs) for p in P], fill=int(170 / (1 + gap * .5)))
        sh = sh.filter(ImageFilter.GaussianBlur(max(2, (3 + gap * 7) * W / 1800 * 2))).resize((W, H), Image.BILINEAR)
        a_ = _cl(1 + dy / 2.6) ** 2 * lot['a']
        if a_ < 1: sh = sh.point(lambda v: int(v * a_))
        cv.c.paste((4, 3, 10), (0, 0, W, H), sh); cv.a.paste((255, 255, 255), (0, 0, W, H), sh)
    # ----- lot: visible sides (soil) then the top (grass + path)
    lv = np.array([[sx * LOT, y, sz * LOT] for sx in (-1, 1) for y in (-LOT_TH, 0) for sz in (-1, 1)])  # idx 4sx+2y+sz
    LP, _ = pr(lv)
    sides = [((0, 0, 1), [3, 7, 5, 1]), ((1, 0, 0), [7, 6, 4, 5]), ((0, 0, -1), [6, 2, 0, 4]), ((-1, 0, 0), [2, 3, 1, 0])]
    stex = _lot_side_tex()
    for n, ids in sides:
        n = np.array(n, float)
        if n @ (Cw - n * LOT) <= 0: continue
        quad = LP[ids]; pts = [tuple(p) for p in quad]
        cv.polygon(pts, (70, 52, 40, 255))
        _quad_tex(cv, stex, quad)
        m = float(np.clip((_shade(np.array([100., 100, 100]), n, cam) / 100).mean(), 0, 1.4))
        cv.shade(pts, (8, 5, 16, int(255 * (1 - m) * .95)) if m < 1 else (255, 240, 230, int(255 * (m - 1) * .3)))
    top = LP[[2, 6, 7, 3]]
    cv.polygon([tuple(p) for p in top], (74, 101, 62, 255))
    _quad_tex(cv, _lot_top_tex(), top)
    mt = float(np.clip((_shade(np.array([100., 100, 100]), np.array([0, 1., 0]), cam) / 100).mean(), 0, 1.4))
    if mt < 1: cv.shade([tuple(p) for p in top], (8, 5, 16, int(255 * (1 - mt) * .8)))
    lot_mask_pts = [tuple(p / gs) for p in top]
    house = (st['slab'] > 0 and st['sink'] < .999) or st['outline'] > 0
    C, A = _piece_transforms(st)
    pa = _visible_pieces(st)
    # ----- shadows / AO on the lot
    if st['slab'] > 0 and st['sink'] < .999:
        _ground_shadow(cv, st, cam, pr, C, A, pa, gs, GW, GH, lot_mask_pts)
    # ----- warm light pools on the lot (windows, open door)
    lights = st['lights']
    if lights > .01 and st['slab'] > 0:
        for p in G.panes:
            if p['kind'] != 'win' or p['id'] >= 4: continue
            w_ = st['win'][p['id']]
            fl = max(st['fly'][j] for j in p['nb']) if p['nb'] else 0.0
            w_ *= 1 - _cl(fl / .3)
            if w_ < .02: continue
            q = p['open']; n = p['n']
            a0, a1 = q[3] + n * .3, q[2] + n * .3
            b0, b1 = q[3] + n * 2.4 + (q[3] - q[2]) * .30, q[2] + n * 2.4 + (q[2] - q[3]) * .30
            quad = np.array([a0, a1, b1, b0]); quad[:, 1] = 0.0
            quad[:, 0] = np.clip(quad[:, 0], -LOT, LOT); quad[:, 2] = np.clip(quad[:, 2], -LOT, LOT)
            S, _ = pr(quad)
            pd.polygon([tuple(s / gs) for s in S], fill=_rgba(WARM * .30 * w_ * glow))
        op = _cl(st['door_ang'] / 60.0) * lights * (1 - _cl(st['fly'][G.door] / .3))
        if op > .02:
            quad = np.array([[-.55, 0, FRONT + .55], [.55, 0, FRONT + .55], [1.5, 0, FRONT + 3.4], [-1.5, 0, FRONT + 3.4]])
            S, _ = pr(quad); pd.polygon([tuple(s / gs) for s in S], fill=_rgba(WARM * .55 * op * glow))
    # ----- the house
    if house:
        _draw_house(cv, gd, st, cam, pr, LW, C, A, pa, t, gs, glow, Cw, people)
    # ----- dust puffs (landings)
    for (x, z, age, scl) in st['dust']:
        _dust(cv, cam, pr, x, z, age, scl, ls)
    # ----- vanish particles + wind dust
    if st['wind'] > 0:
        _draw_particles(cv, st, cam, pr, ls)
    # ----- outline trace
    if st['outline'] > 0 and st['outline_a'] > .01:
        _draw_outline(cv, gd, st, cam, pr, gs, glow, Cw)
    # ----- resolve: reduce, bloom, sheen, unpremultiply
    if ss in (2, 3, 4): c = cv.c.reduce(ss); a = cv.a.getchannel(0).reduce(ss)
    elif ss == 1: c = cv.c; a = cv.a.getchannel(0)
    else: c = cv.c.resize((Wo, Ho), Image.BOX); a = cv.a.getchannel(0).resize((Wo, Ho), Image.BOX)
    C_ = np.asarray(c, np.float32); A_ = np.asarray(a, np.float32)[..., None]
    if glow > 0:
        pool = pool_l.filter(ImageFilter.GaussianBlur(max(2, W / 260)))
        lm = Image.new('L', (GW, GH), 0); ImageDraw.Draw(lm).polygon(lot_mask_pts, fill=255)
        pool = ImageChops.multiply(pool, Image.merge('RGB', [lm] * 3))
        g1 = glow_l.filter(ImageFilter.GaussianBlur(max(1, W / 1200)))
        g2 = glow_l.filter(ImageFilter.GaussianBlur(max(2, W / 260)))
        gsum = (np.asarray(g1.resize((Wo, Ho), Image.BILINEAR), np.float32) * .55 + np.asarray(g2.resize((Wo, Ho), Image.BILINEAR), np.float32) * .85
                + np.asarray(pool.resize((Wo, Ho), Image.BILINEAR), np.float32))
        C_ = C_ + gsum
        A_ = np.maximum(A_, np.clip(gsum.max(2, keepdims=True) * 1.2, 0, 255))
    if st['sheen'] >= 0:
        C_ = _sheen(C_, A_, st['sheen'])
    if lot['a'] < 1: C_ = C_ * lot['a']; A_ = A_ * lot['a']
    rgb = np.clip(C_ * 255 / np.maximum(A_, 1), 0, 255)
    return Image.fromarray(np.dstack([rgb, np.clip(A_, 0, 255)]).astype(np.uint8), 'RGBA')

def _ground_shadow(cv, st, cam, pr, C, A, pa, gs, GW, GH, lot_mask_pts):
    """house shadow along the key light + contact AO around the plinth, multiplied onto the lot (colour only)."""
    sm = Image.new('L', (GW, GH), 0); smd = ImageDraw.Draw(sm)
    lt = LKEY
    def ground(P):
        P = np.asarray(P, float); Q = P - lt * (P[..., 1:2] / lt[1]); Q[..., 1] = 0.0
        S, _ = pr(Q); return S / gs
    sel = np.nonzero((pa > .3) & np.isin(G.kind, ('block', 'roof', 'chim', 'ridge')) & (st['fly'] < .6))[0]
    if len(sel):
        V = C[sel, None, :] + np.einsum('nij,kj->nki', A[sel], _S8)
        Gp = ground(V)
        for j, i in enumerate(sel):
            v = Gp[j]; val = int(150 * pa[i])
            for f in (0, 1, 4, 5, 2):
                smd.polygon([tuple(v[k]) for k in FACE_IDX[f]], fill=val)
    if st['roof_a'] > .3 and st['fly'][G.ridge] < .6:
        for gb in G.gables:
            Gp = ground(gb['v'] + np.array([0, st['roof_dy'], 0]))
            for f in ([0, 1, 4, 3], [0, 2, 5, 3], [1, 2, 5, 4]): smd.polygon([tuple(Gp[k]) for k in f], fill=150)
    sm = sm.filter(ImageFilter.GaussianBlur(max(1.2, cv.W / 1100)))
    hs = (1 - st['sink']) * _cl(st['slab'])
    ao = Image.new('L', (GW, GH), 0); aod = ImageDraw.Draw(ao)
    for gr, val in ((.60, 60), (.20, 115)):
        fp = np.array([[-HX - .32 - gr, 0, BACK - .32 - gr], [HX + .32 + gr, 0, BACK - .32 - gr],
                       [HX + .32 + gr, 0, FRONT + .32 + gr], [-HX - .32 - gr, 0, FRONT + .32 + gr]])
        S, _ = pr(fp); aod.polygon([tuple(p / gs) for p in S], fill=int(val * hs))
    ao = ao.filter(ImageFilter.GaussianBlur(max(2, cv.W / 520)))
    sm = ImageChops.lighter(sm, ao)
    lm = Image.new('L', (GW, GH), 0); ImageDraw.Draw(lm).polygon(lot_mask_pts, fill=255)
    sm = ImageChops.multiply(sm, lm).resize((cv.W, cv.H), Image.BILINEAR)
    k_ = sm.point(lambda v: int(255 - v * .80)); kb = sm.point(lambda v: int(255 - v * .64))
    r_, g_, b_ = cv.c.split()
    cv.c = Image.merge('RGB', (ImageChops.multiply(r_, k_), ImageChops.multiply(g_, k_), ImageChops.multiply(b_, kb)))
    cv.redraw()

def _sheen(C_, A_, u):
    h, w = C_.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    pos = -0.35 + 1.75 * _ss(0, 1, u)
    s = xx / w + yy / h * .45 - pos * 1.45
    band = (np.exp(-(s / .08) ** 2) * .40 + np.exp(-(s / .018) ** 2) * .30) * math.sin(math.pi * _cl(u))
    return C_ + (A_ - C_) * band[..., None]

def _hull_in_front(P, Cw):
    """True if the house hull cannot hide point P (camera and P share an outer half-space of a hull face)."""
    for n, off in G.hull:
        if n @ P > off and n @ Cw > off: return True
    return False

_CLIPS = {}
def _win_clip(i):
    """one sequential reader per window (two windows play the same film at different offsets)."""
    if i not in _CLIPS: _CLIPS[i] = E.Clip(WIN_VIDS[i][0], (162, 288))
    return _CLIPS[i]

def _pane_img(p, st, t):
    """window pane texture: dark glass -> warm interior -> playing film, + reflection + slim frame."""
    i = p['id']; h = 150; w = max(40, int(h * p['w'] / p['h']))
    base = _glass_tex(w, h)
    wv = float(st['win'][i]); vv = float(st['vid'][i]) if i < 4 else 0.0
    if wv > .01: base = Image.blend(base, _warm_tex(w, h), min(1.0, wv))
    if vv > .01:
        path, off, loop = WIN_VIDS[i]
        try:
            fr = _win_clip(i).at(off + ((t - VID_T) % loop))
            fr = _cover(fr, w, h)
            a = np.asarray(fr, np.float32) * np.array([1.04, .98, .88], np.float32) * .92 + np.array([14, 8, 0], np.float32)
            fr = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
            base = Image.blend(base, fr, min(1.0, vv))
        except Exception:
            pass
    base = base.copy()
    base.alpha_composite(_streak(w, h))
    base.alpha_composite(_frame_tex(w, h))
    return base

def _draw_house(cv, gd, st, cam, pr, LW, C, A, pa, t, gs, glow, Cw, people):
    V = C[:, None, :] + np.einsum('nij,kj->nki', A, _S8)            # (N, 8, 3)
    S, _ = pr(V.reshape(-1, 3)); S = S.reshape(G.N, 8, 2)
    nrm = np.zeros((G.N, 6, 3)); fc = np.zeros((G.N, 6, 3))
    for f in range(6):
        ax = A[:, :, FACE_AX[f]]
        ln = np.linalg.norm(ax, axis=1, keepdims=True) + 1e-9
        nrm[:, f] = FACE_SG[f] * ax / ln
        fc[:, f] = C + FACE_SG[f] * ax
    vis = np.einsum('nfk,nfk->nf', nrm, Cw[None, None, :] - fc) > 1e-6
    col = _shade(G.ALB, nrm, cam, G.AO[:, None])
    _, depth = pr(C)
    fly = st['fly']; chaos = fly.max() > 1e-4
    wpx = max(1, cv.W // 1100)
    items = []
    for k in G.blocks:
        if pa[k] > .01: items.append((depth[k], 'box', k))
    for p in G.panes:
        lint = [j for j in p['nb'] if G.P[j]['row'] > p['rows'][1]]
        a_ = min(pa[j] for j in lint) if lint else 1.0
        fl = max(fly[j] for j in p['nb']) if p['nb'] else 0.0
        a_ *= 1 - _cl((fl - .15) / .25)
        if a_ <= .01: continue
        nb = [j for j in p['nb'] if pa[j] > .01]
        key = max(depth[j] for j in nb) + .01 if nb else float(pr(p['q'].mean(0)[None])[1][0])
        items.append((key, 'pane' if p['kind'] == 'win' else 'doorway', (p, a_)))
    door_open = st['door_ang'] > 4 or chaos
    if pa[G.door] > .01 and not door_open:
        nb = G.door_pane['nb']
        items.append(((max(depth[j] for j in nb) + .005) if nb else depth[G.door], 'box', G.door))
    if chaos:
        for k in G.roof + G.sills + [G.door, G.sign]:
            if pa[k] > .01: items.append((depth[k], 'box', k))
        if st['roof_a'] > .01:
            for gi, gb in enumerate(G.gables): items.append((float(pr(_gable_v(gb, st, gi).mean(0)[None])[1][0]), 'gable', gi))

    def draw_box(k, alpha):
        kind = G.kind[k]
        for f in range(6):
            if not vis[k, f]: continue
            pts = [tuple(S[k, j]) for j in FACE_IDX[f]]
            c = col[k, f]
            cv.polygon(pts, _rgba(c, 255 * alpha))
            if kind == 'block' and f == G.P[k]['outer']:
                tk = G.P[k]['tex']
                if tk >= 0 and st['tex'][k] > 0:
                    tv = st['tex'][k]; ta = _ss(0, .55, tv)
                    hh = 150; ww = int(hh * (COLF if G.P[k]['wall'] in 'FB' else COLS) / (2 * RH))
                    _quad_tex(cv, _post_tex(tk, ww, hh), S[k, G.P[k]['tc']], alpha * ta)
                    lam = float(np.clip(nrm[k, f] @ LKEY, 0, None)); shd = .55 + .50 * lam
                    if shd < 1: cv.shade(pts, (10, 6, 22, int(255 * alpha * (1 - shd) * .75 * ta)))
                    fl_ = math.sin(math.pi * _cl(tv / .55)) if tv < .55 else 0.0
                    if fl_ > .01:
                        cv.shade(pts, (255, 248, 255, int(255 * fl_ * .8 * alpha)))
                        gd.polygon([tuple(np.array(p_) / gs) for p_ in pts], fill=_rgba(np.array([190, 160, 255]) * fl_ * .5 * glow))
            elif kind == 'roof' and f == 2:
                q = S[k, FACE_IDX[f]]
                for m in (.2, .4, .6, .8):
                    a_ = q[0] + (q[1] - q[0]) * m; b_ = q[3] + (q[2] - q[3]) * m
                    cv.line([tuple(a_), tuple(b_)], _rgba(np.clip(c * 1.22 + 10, 0, 255), 210 * alpha), width=wpx, cover=False)
        if kind == 'door':
            for f, ids in ((4, [3, 7, 5, 1]), (5, [6, 2, 0, 4])):
                if not vis[k, f]: continue
                q = S[k, ids]
                dimg = Image.blend(_door_tex(False), _door_tex(True), _cl(st['cta'])) if 0 < st['cta'] < 1 else _door_tex(st['cta'] >= 1)
                _quad_tex(cv, dimg, q, alpha)
                lam = float(np.clip(nrm[k, f] @ LKEY, 0, None)); shd = .55 + .5 * lam
                if shd < 1: cv.shade([tuple(p_) for p_ in q], (8, 6, 16, int(255 * (1 - shd) * .5 * alpha)))
                if st['cta'] > .01 and f == 4:
                    hx = q[1] + (q[2] - q[1]) * .5 + (q[0] - q[1]) * .14
                    r_ = max(2, np.linalg.norm(q[1] - q[0]) / gs * .08)
                    gd.ellipse((hx[0] / gs - r_, hx[1] / gs - r_ * 3, hx[0] / gs + r_, hx[1] / gs + r_ * 3), fill=_rgba(PURPLE * 1.3 * st['cta'] * alpha * glow))
                    gd.polygon([tuple(p_ / gs) for p_ in q], outline=_rgba(np.array([150, 110, 255]) * .8 * st['cta'] * alpha * glow))

    # ---------- plinth (+ LED) and step
    if pa[G.slab] > 0:
        draw_box(G.slab, 1.0)
        if st['led'] > .01:
            for f in (0, 1, 4, 5):
                if not vis[G.slab, f]: continue
                ids = FACE_IDX[f]
                tops = [S[G.slab, j] for j in ids if _S8[j][1] > 0]
                if len(tops) == 2:
                    o_ = np.array([0, max(1.5, cv.H / 700)])
                    cv.line([tuple(tops[0] + o_), tuple(tops[1] + o_)], _rgba(np.array([205, 175, 255]), 255 * st['led']), width=max(1, cv.H // 900))
                    gd.line([tuple((tops[0] + o_) / gs), tuple((tops[1] + o_) / gs)], fill=_rgba(PURPLE * .9 * st['led'] * glow), width=1)
        if pa[G.step] > 0: draw_box(G.step, 1.0)
    # ---------- people the house may hide
    ppl = _people(st) if (people and st['people_t'] >= 0) else []
    front_ppl, back_ppl, inside_ppl = [], [], []
    for pp in ppl:
        if pp[3] > 0: inside_ppl.append(pp)
        elif _hull_in_front(pp[0], Cw): front_ppl.append(pp)
        else: back_ppl.append(pp)
    for pp in back_ppl: _person(cv, pp, pr, cam)
    # ---------- walls, panes, doorway (painter's order)
    items.sort(key=lambda x: -x[0])
    for key, kind, pl in items:
        if kind == 'box': draw_box(pl, pa[pl])
        elif kind == 'pane':
            p, a_ = pl
            q, _ = pr(p['q'])
            if (Cw - p['q'][0]) @ p['n'] <= 0:
                cv.polygon([tuple(x) for x in q], (22, 22, 30, int(255 * a_)))
            else:
                _quad_tex(cv, _pane_img(p, st, t), q, a_)
                w_ = st['win'][p['id']]
                if w_ > .01:
                    vv = st['vid'][p['id']] if p['id'] < 4 else 0
                    gcol = WARM * (1 - vv) + np.array([225, 190, 180]) * vv
                    gd.polygon([tuple(x / gs) for x in q], fill=_rgba(gcol * .42 * w_ * a_ * glow))
        elif kind == 'doorway':
            p, a_ = pl
            q, _ = pr(p['q'])
            li = st['lights']
            dark = _tx('doorway_dark', lambda: Image.new('RGBA', (60, 120), (12, 11, 18, 255)))
            base = Image.blend(dark, _warm_tex(60, 120, .80), _cl(li)) if li > .01 else dark
            _quad_tex(cv, base, q, a_)
            op = _cl(st['door_ang'] / 50.0)
            if li * op > .01:
                qo, _ = pr(p['open'])
                gd.polygon([tuple(x / gs) for x in qo], fill=_rgba(WARM * .75 * li * op * a_ * glow))
        elif kind == 'gable':
            _draw_gable(cv, G.gables[pl], st, cam, pr, Cw, pl)
    # ---------- attached outside items (sills, sign) on walls facing the camera
    if not chaos:
        for k in G.sills:
            if pa[k] > .01 and np.array(WALL_N[G.P[k]['wall']], float) @ (Cw - G.C0[k]) > 0: draw_box(k, pa[k])
    if st['logo'] > 0 and pa[G.sign] > .01 and (chaos or (Cw - G.C0[G.sign])[2] > 0):
        k = G.sign
        if not chaos: draw_box(k, pa[k])
        q = S[k, TEX_CORNERS['F']]
        if vis[k, 4]:
            lg = st['logo']
            _quad_tex(cv, _sign_off(), q, pa[k])
            sw = _sign_tex()
            if lg < 1:
                m = Image.new('L', sw.size, 0)
                ImageDraw.Draw(m).rectangle((0, 0, int(sw.width * _eo(lg) * 1.05), sw.height), fill=255)
                sw = sw.copy(); sw.putalpha(ImageChops.multiply(sw.getchannel('A'), m))
            _quad_tex(cv, sw, q, pa[k])
            gd.polygon([tuple(x / gs) for x in q], fill=_rgba(PURPLE * .32 * lg * pa[k] * glow))
            if lg < 1:
                e_ = q[0] + (q[1] - q[0]) * _eo(lg); f_ = q[3] + (q[2] - q[3]) * _eo(lg)
                cv.line([tuple(e_), tuple(f_)], (255, 255, 255, int(255 * (1 - lg))), width=max(2, cv.W // 450), cover=False)
                gd.line([tuple(e_ / gs), tuple(f_ / gs)], fill=_rgba(np.array([230, 210, 255]) * (1 - lg) * glow), width=3)
    # ---------- people stepping through the doorway: clipped to the opening, silhouetted against the light
    if inside_ppl:
        qo, _ = pr(G.door_pane['open'])
        x0, y0 = int(max(0, qo[:, 0].min() - 2)), int(max(0, qo[:, 1].min() - 2))
        x1, y1 = int(min(cv.W, qo[:, 0].max() + 3)), int(min(cv.H, qo[:, 1].max() + 3))
        if x1 > x0 + 1 and y1 > y0 + 1:
            tmp = _Cv(x1 - x0, y1 - y0)
            for pp in sorted(inside_ppl, key=lambda x: -x[3]):
                p, a_, ph, inside, i = pp
                _person(tmp, (p, a_ * (1 - _ss(.5, 1.3, inside)), ph, inside, i), pr, cam, dark=_cl(inside / .45) * .9, shift=(x0, y0))
            m = Image.new('L', (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in qo], fill=255)
            ta = ImageChops.multiply(tmp.a.getchannel(0), m)
            tc = ImageChops.multiply(tmp.c, Image.merge('RGB', [m] * 3))
            box = (x0, y0, x1, y1)
            inv = Image.merge('RGB', [ta.point(lambda v: 255 - v)] * 3)
            cv.c.paste(ImageChops.add(ImageChops.multiply(cv.c.crop(box), inv), tc), box)
            cv.a.paste(ImageChops.add(ImageChops.multiply(cv.a.crop(box), inv), Image.merge('RGB', [ta] * 3)), box)
    # ---------- open door leaf (outside the facade)
    if pa[G.door] > .01 and door_open and not chaos:
        if (Cw - G.C0[G.door])[2] > -1.0: draw_box(G.door, pa[G.door])
    # ---------- roof assembly: gables, chimney (plane rule), slate panels, ridge
    if not chaos and st['roof_a'] > .01:
        for gi, gb in enumerate(G.gables): _draw_gable(cv, gb, st, cam, pr, Cw, gi)
        n_r = np.array([math.sin(TH), math.cos(TH), 0])
        chim_after = n_r @ (Cw - np.array([0, YR + st['roof_dy'], 0])) > 0
        if not chim_after:
            for k in (G.chim, G.chimcap): draw_box(k, pa[k])
        rk = [k for k in G.roof if k not in (G.chim, G.chimcap, G.ridge)]
        for k in sorted(rk, key=lambda k: -depth[k]): draw_box(k, pa[k])
        draw_box(G.ridge, pa[G.ridge])
        if chim_after:
            for k in (G.chim, G.chimcap): draw_box(k, pa[k])
        # monitor rim light on the eaves and the ridge
        _roof_rim(cv, gd, st, cam, pr, gs, glow, Cw)
    # ---------- people in front of the house
    for pp in sorted(front_ppl, key=lambda x: -np.linalg.norm(x[0] - Cw)): _person(cv, pp, pr, cam)

def _roof_rim(cv, gd, st, cam, pr, gs, glow, Cw):
    """thin purple/blue light lines on the roof edges facing the studio monitors (camera-space rim)."""
    dyr = st['roof_dy']; a = st['roof_a']
    if a <= .05: return
    z0, z1 = BACK - OVH, FRONT + OVH
    ex = HX + OVH; ey = YR - (HX + OVH) * math.tan(TH) + RT / math.cos(TH)
    ry = YR + RT / math.cos(TH) + .01
    segs = [((0, ry, z0), (0, ry, z1), np.array([0, 1, 0.])),
            ((ex, ey, z0), (ex, ey, z1), np.array([1, .3, 0.])), ((-ex, ey, z0), (-ex, ey, z1), np.array([-1, .3, 0.])),
            ((0, ry, z1), (ex, ey, z1), np.array([.3, .5, 1.])), ((0, ry, z1), (-ex, ey, z1), np.array([-.3, .5, 1.])),
            ((0, ry, z0), (ex, ey, z0), np.array([.3, .5, -1.])), ((0, ry, z0), (-ex, ey, z0), np.array([-.3, .5, -1.]))]
    w = max(1, cv.W // 1000)
    for p0, p1, n in segs:
        n = _nrm(n)
        mid = (np.array(p0) + np.array(p1)) / 2 + np.array([0, dyr, 0])
        if n @ (Cw - mid) < -0.2 * np.linalg.norm(Cw - mid): continue
        kp = max(0.0, n @ cam.rim_p) ** 1.5; kb = max(0.0, n @ cam.rim_b) ** 1.5
        if kp + kb < .05: continue
        c = PURPLE * kp + BLUE * kb
        P, _ = pr(np.array([np.array(p0) + [0, dyr, 0], np.array(p1) + [0, dyr, 0]]))
        cv.line([tuple(P[0]), tuple(P[1])], _rgba(np.clip(c * .6 + 120 * (kp + kb), 0, 255), 200 * a * min(1, kp + kb)), width=w, cover=False)
        gd.line([tuple(P[0] / gs), tuple(P[1] / gs)], fill=_rgba(c * .45 * a * glow), width=1)

def _gable_v(gb, st, gi):
    v = gb['v'] + np.array([0, st['roof_dy'], 0])
    u = st['fly'][G.ridge]
    if u > 1e-4:
        c = v.mean(0)
        off = WIND * (8.5 * u * u) + np.array([0, 1, 0]) * (3.2 * u ** 1.5) + np.array([0, 0, 1.0 if gi == 0 else -1.0]) * u
        R = _rot((0.3, 1, .2 if gi else -.2), math.radians(260 * u * (1 if gi else -1)))
        v = (v - c) @ R.T * (1 - .55 * u ** 1.4) + c + off
    return v

def _draw_gable(cv, gb, st, cam, pr, Cw, gi):
    u = st['fly'][G.ridge]
    al = st['roof_a'] * (1 - _cl((u - .55) / .45))
    if al <= .01: return
    v = _gable_v(gb, st, gi)
    S, _ = pr(v); cen = v.mean(0)
    for f in gb['faces']:
        P = v[f]
        n = np.cross(P[1] - P[0], P[2] - P[0]); n = n / (np.linalg.norm(n) + 1e-9)
        if n @ (cen - P[0]) > 0: n = -n
        if n @ (Cw - P[0]) <= 0: continue
        cv.polygon([tuple(S[j]) for j in f], _rgba(_shade(CREAM, n, cam), 255 * al))

def _person(cv, pp, pr, cam, dark=0.0, shift=(0, 0)):
    p, a_, ph, inside, i = pp
    S, _ = pr(np.array([p, p + np.array([0, 1.75, 0])]))
    S = S - np.array(shift, float)
    h = S[0][1] - S[1][1]
    if h < 2: return
    if inside <= 0:
        rr = h * .15
        cv.ellipse((S[0][0] - rr * 1.4, S[0][1] - rr * .32, S[0][0] + rr * 1.4, S[0][1] + rr * .32), (8, 6, 14, int(110 * _cl(a_))))
    _draw_person(cv, (S[0][0], S[0][1]), h * _cl(a_, 0, 1.25), ph, i, min(1.0, a_ * 1.3), dark)

def _dust(cv, cam, pr, x, z, age, scl, ls):
    r = np.random.default_rng(int(abs(x) * 10 + abs(z) * 100 + scl * 1000))
    n_ = 70
    ang = r.uniform(0, 2 * math.pi, n_)
    k = _eo(age / 1.0)
    rad = (1.0 + r.uniform(0, .45, n_) + .55 * k) * scl
    px = x + np.cos(ang) * rad * (HX + .4); pz = z + np.sin(ang) * rad * (HZ + .4)
    py = .04 + r.uniform(0, .45, n_) * k * scl
    Sx, Z = pr(np.stack([px, py, pz], 1))
    al = (1 - _cl(age / 1.1)) ** 1.6 * .5
    for j in range(n_):
        rr = max(1.0, (.07 + .10 * (j % 3)) * cam.focal / Z[j] * ls * (1 + k))
        cv.ellipse((Sx[j][0] - rr, Sx[j][1] - rr * .7, Sx[j][0] + rr, Sx[j][1] + rr * .7), (226, 218, 206, int(255 * al)))

def _draw_particles(cv, st, cam, pr, ls):
    fly = st['fly']; t = st['t']
    pts, al, sz = [], [], []
    if t < RET_T0:
        for i in np.nonzero((fly > 0) & (fly < 1))[0]:
            u = fly[i]
            r = np.random.default_rng(i * 7 + 1)
            for j in range(4):
                o = r.normal(size=3) * .35
                p = G.C0[i] + o + WIND * (11 * u ** 1.3 * r.uniform(.7, 1.3)) + np.array([0, 1, 0]) * (2.6 * u * r.uniform(.5, 1.5)) \
                    + np.array([0, math.sin(u * 9 + j) * .3, math.cos(u * 7 + j) * .3])
                pts.append(p); al.append((1 - u) ** 1.2 * .9 * min(1, u * 8)); sz.append(r.uniform(.035, .10))
    # wind-borne dust drifting across the empty lot (seg 15-16)
    w = st['wind']
    if w > .01:
        r = np.random.default_rng(404)
        n_ = 46
        x0 = r.uniform(-LOT * 1.6, LOT, n_); z0 = r.uniform(-LOT, LOT, n_); sp = r.uniform(3.0, 6.5, n_)
        y0 = r.uniform(.05, 2.4, n_); ph = r.uniform(0, 6.28, n_)
        tt = t - W_SEM
        x = (x0 + sp * tt + LOT * 1.6) % (LOT * 2.6) - LOT * 1.6
        for j in range(n_):
            if abs(x[j]) > LOT * 1.05: continue
            p = np.array([x[j], y0[j] + .25 * math.sin(tt * 2.2 + ph[j]), z0[j] - .3 * tt])
            edge = _cl((LOT * 1.05 - abs(x[j])) / 2.0)
            pts.append(p); al.append(.45 * w * edge); sz.append(.03 + .03 * (j % 3))
    if not pts: return
    S, Z = pr(np.array(pts))
    for k in range(len(pts)):
        rr = max(.7, sz[k] * cam.focal / Z[k] * ls)
        cv.rectangle((S[k][0] - rr, S[k][1] - rr, S[k][0] + rr, S[k][1] + rr), (238, 232, 222, int(255 * al[k])))

def _hidden(P, Cw):
    """is world point P hidden by the (convex) house solid, seen from Cw?"""
    D = P - Cw; t0, t1 = 0.0, 1.0
    for n, off in _HID_PLANES:
        a = n @ D; b = off - n @ Cw
        if abs(a) < 1e-9:
            if b < 0: return False
            continue
        tt = b / a
        if a > 0: t1 = min(t1, tt)
        else: t0 = max(t0, tt)
        if t0 > t1: return False
    return t0 < 0.985
_nr = np.array([math.sin(TH), math.cos(TH), 0])
_HID_PLANES = [(np.array([1, 0, 0.]), HX - .03), (np.array([-1, 0, 0.]), HX - .03), (np.array([0, 0, 1.]), FRONT - .03),
               (np.array([0, 0, -1.]), -BACK - .03), (np.array([0, -1, 0.]), -YS - .03),
               (_nr, float(_nr @ np.array([0, YR, 0])) - .03), (_nr * np.array([-1, 1, 1]), float(_nr @ np.array([0, YR, 0])) - .03)]

def _draw_outline(cv, gd, st, cam, pr, gs, glow, Cw):
    q = st['outline']; A_ = st['outline_a']
    wpx = max(1, int(cv.W / 650))
    for (a, b, t0, t1, wgt) in G.edges:
        k = _cl((q - t0) / (t1 - t0))
        if k <= 0: continue
        e = a + (b - a) * k
        hid = _hidden((a + e) / 2, Cw)
        al = A_ * (0.26 if hid else 1.0) * wgt
        if al <= .01: continue
        S, _ = pr(np.array([a, e]))
        hgt = _cl(((a[1] + e[1]) / 2) / YR)
        c = BLUE * (1 - hgt) + PURPLE * hgt
        core = np.clip(c * .30 + 185, 0, 255)
        cv.line([tuple(S[0]), tuple(S[1])], _rgba(core, 255 * al), width=wpx)
        gd.line([tuple(S[0] / gs), tuple(S[1] / gs)], fill=_rgba(c * 1.0 * al * glow), width=2)
        if 0 < k < 1:
            r = wpx * 2.5
            cv.ellipse((S[1][0] - r, S[1][1] - r, S[1][0] + r, S[1][1] + r), (255, 255, 255, int(255 * al)))
            gd.ellipse((S[1][0] / gs - 3, S[1][1] / gs - 3, S[1][0] / gs + 3, S[1][1] / gs + 3), fill=_rgba(np.array([230, 210, 255]) * glow))

# ---------------------------------------------------------------------------------------------- anchors
ANCHORS = {
    'door': (0, YS + 1.0, FRONT), 'step': (0, .2, FRONT + .58), 'lot_front': (0, 0, LOT), 'lot_center': (0, 0, 0),
    'slab': (0, YS, FRONT + .32), 'roof_peak': (0, YR + .2, FRONT + OVH), 'chimney': (1.8, YR + .6, ZH - 2.3),
    'sign': (0, YS + 2.52, FRONT + .1), 'wall_front': (0, YS + 1.5, FRONT), 'wall_right': (HX, YS + 1.5, ZH),
    'win0': tuple(G.win_pane[0]['open'].mean(0)), 'win1': tuple(G.win_pane[1]['open'].mean(0)),
    'win2': tuple(G.win_pane[2]['open'].mean(0)), 'win3': tuple(G.win_pane[3]['open'].mean(0)),
}
def anchor(name, state, cam, size=(900, 900)):
    """screen (x, y) in the render's own pixel space of a named 3-D point (follows the lot's rise)."""
    c = _Cam(cam, size[0], size[1]); lot = state['lot']
    P = np.array(ANCHORS[name], float) * lot['s'] + np.array([0, lot['dy'], 0])
    S, _ = c.proj(P[None]); return float(S[0][0]), float(S[0][1])

# ---------------------------------------------------------------------------------------------- self test
if __name__ == '__main__':
    import sys, time
    out = os.path.join(E.HERE, 'out', 'house'); os.makedirs(out, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'strip'
    if cmd == 'strip':
        ts = [float(x) for x in sys.argv[2:]] or [3.95, 4.3, 6.6, 7.1, 8.6, 9.8, 10.3, 10.9, 11.3, 12.1, 13.2, 13.6, 14.1, 15.8,
                                                  16.6, 28.8, 29.5, 30.1, 31.0, 33.1, 33.6, 34.6, 35.1, 37.6]
        size = (450, 450); cols = 6
        ims = []; tt = []
        for t in ts:
            t0 = time.time(); im = render(state_at(t), hero_cam(t), size=size, t=t); tt.append(time.time() - t0)
            bg = Image.new('RGBA', size, (24, 18, 40, 255)); bg.alpha_composite(im)
            ImageDraw.Draw(bg).text((6, 6), f'{t:.2f}', font=E.font(22, 700), fill=(255, 230, 0)); ims.append(bg.convert('RGB'))
        rows = math.ceil(len(ims) / cols); Sh = Image.new('RGB', (cols * size[0], rows * size[1]))
        for i, im in enumerate(ims): Sh.paste(im, ((i % cols) * size[0], (i // cols) * size[1]))
        Sh.save(os.path.join(out, 'strip.jpg'), quality=86)
        print('mean render', np.mean(tt), 'max', np.max(tt))
    elif cmd == 'still':
        t = float(sys.argv[2]); size = (900, 900)
        cam = hero_cam(t)
        if len(sys.argv) > 3: cam.update(eval(sys.argv[3]))
        t0 = time.time(); im = render(state_at(t), cam, size=size, t=t); print('render', time.time() - t0)
        bg = Image.new('RGBA', size, (24, 18, 40, 255)); bg.alpha_composite(im); bg.convert('RGB').save(os.path.join(out, f'still_{t:.2f}.png'))
    elif cmd == 'orbit':
        t = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
        size = (450, 450); ims = []
        for yaw in range(-60, 300, 30):
            cam = dict(hero_cam(t), yaw=yaw)
            im = render(state_at(t), cam, size=size, t=t)
            bg = Image.new('RGBA', size, (24, 18, 40, 255)); bg.alpha_composite(im); ims.append(bg.convert('RGB'))
        Sh = Image.new('RGB', (6 * size[0], 2 * size[1]))
        for i, im in enumerate(ims): Sh.paste(im, ((i % 6) * size[0], (i // 6) * size[1]))
        Sh.save(os.path.join(out, 'orbit.jpg'), quality=86)
