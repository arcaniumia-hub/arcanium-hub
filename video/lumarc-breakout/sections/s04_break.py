"""s04 — BREAK OUT (7.80–11.96).  "Not mine." / (the glass shatters) / "Good content doesn't stay on the screen."

One continuous take (no pose jumps). Shared glass state (crack network, Reel, jolts) lives in s03_swipe.
7.80  His Reel fills the cracked screen (feed chrome still printed on the glass), seen THROUGH it: a touch flatter
      than real life. Slow push-in (tension).
7.90  "NOT" — third hit: jolt + glass flex + light flare, and the knock star races across the whole screen (16 radial
      fissures reach the edges in ~3 frames; on his dark hoodie they scatter light and read pale).
8.09  "MINE." — the concentric spiderweb completes inner -> outer and the studio light starts leaking through the
      cracks (fissures turn to light, violet halo, strongest at the impact), the glass bulges (growing refraction),
      tremor + leak build with the riser; creaks at 8.30 / 8.45.
8.56  BREAK — one-frame flash + boom (the fissures blaze). The glass (feed UI + the flat Reel printed on it) bursts into
      ~80 shards blown TOWARD the lens (explosive first 2-3 frames, then 0.32x slow motion) + six authored hero BLADES
      of the cover glass that fly straight at the lens: they loom from 1x to ~5x in 0.3 s nearly in place, defocused
      and motion-blurred, and sweep out across the frame edges (never toward his face). Rigid planar pieces in 3-D
      (pinhole camera, homography per shard), tumbling, short shutter (crisp, high-speed-photography read).
      Photographic "hero look" glass (GK render_refract): dark refracting bodies with a sweeping internal gradient
      (broken-mirror slices of his face), the slab's side face peeking out as a lit strip, crisp white bevels on the
      key side + purple/blue monitor rim on the others, a hard-edged window reflection sliding across each piece as it
      turns, star glints, tapered glass dust with sparkles, bloom on the glass highlights only. The printed photo
      dies within 2 frames while the white UI glyphs (For you, heart, home...) stay printed on the flying cover glass.
      Camera: expo-out dolly toward him 8.56 -> 9.40 (he comes FORWARD x1.11, studio parallax via bg_z) — the
      shards spread over the whole frame and clear his face by ~8.83; the glass is gone by ~9.0.
9.28  He's out. Eight loose shards drift in slow motion around the frame edges (off his face and off the caption band),
      three still carrying a UI glyph, one big soft foreground piece for depth; light catches on CONTENT, DOESN'T, STAY.
9.76  "CONTENT": snap push-in to a tight face framing (3 frames, radial motion blur on the world only — the words stay
      crisp); 10.76 "STAY": snap back out (the frame doesn't stay either).
11.08 A smoked-glass screen pane flies in BEHIND his head; ON (11.20) and THE (11.28) print on it with the voice
      (engine captions off), SCREEN slams on 11.38 and on its stressed vowel (11.60) the pane cracks (light catch,
      impact star -> spiderweb, glints) with a camera jolt. Hard cut to s05 at 11.96 (studio framing).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import feedkit as FK
from sections import _glasskit as GK
from sections import s03_swipe as S3

START, END = E.span(9, 11)                    # 7.80 – 11.96
W, H = E.W, E.H
clamp, eout, ein = E.clamp, E.eout, E.ein
smooth, lerp = S3.smooth, S3.lerp

# word onsets measured on src/tight16k.raw (10 ms RMS envelope + >3.5 kHz band for s / prevoiced g, d)
# (spectrogram: "stay" s 10.76, ay 10.98-11.18 -> "on" 11.20 -> nasal dip 11.23-11.27 -> "the" 11.28 -> s of "screen" 11.38,
#  k-burst 11.58, stressed vowel 11.60)
WORD_FIX = {(9, 'NOT'): 7.90, (9, 'MINE.'): 8.09, (11, 'GOOD'): 9.41, (11, 'CONTENT'): 9.76, (11, "DOESN'T"): 10.40,
            (11, 'STAY'): 10.76, (11, 'ON'): 11.20, (11, 'THE'): 11.28, (11, 'SCREEN.'): 11.38}
W_NOT, W_MINE = S3.W_NOT, S3.W_MINE
BREAK = 8.56
W_GOOD, W_CONTENT, W_DOESNT, W_STAY = 9.41, 9.76, 10.40, 10.76
W_ON, W_THE, W_SCREEN = 11.20, 11.28, 11.38
SCREEN_V = 11.60                              # stressed vowel of "scrEEn" -> the pane cracks
PANE_IN = 11.08
CAP_OFF = min(11.18, S3._page_a(11, 'ON') or 11.18)   # engine captions off: "ON THE SCREEN." is printed on the pane
CREAKS = (8.30, 8.45)

VP = S3.VP; IMPACT = S3.IMPACT; FR = S3.FR
FOC = 1600.0
ZH, ZB = 4.55, 7.0                            # depth of him / the studio wall behind the glass (units of FOC)
C_MAX = .45                                   # camera travel (units of FOC) toward him: x ZH/(ZH-C_MAX) = 1.11 (the dolly)
TAU_C, U_C = .22, .84                         # expo-out dolly: ~75 % of the travel in the first 0.3 s, at rest by 9.40
BGZ0 = S3.BGZ0
def _group(i, j, k):
    if j <= 1: return ('a', j, k // 4)                    # crushed centre: a few wedge pieces
    if j <= 6: return ('b', j, k // 2)                    # mid rings: pairs of cells
    return ('c', i)
FACE = (540.0, 790.0)                         # his face on the glass at the break
SH = GK.Shatter(FR, seed=3, focal=FOC, vp=VP, group=_group, wave=20000., speed=1.25)
DUST = GK.Dust(FR, n=340, seed=5, focal=FOC, vp=VP)


class HeroShards(GK.Shatter):
    """authored blade-shaped hero pieces of the cover glass (they get huge, so they must not show the spiderweb's
    curved ring cells): same flight model as the shatter, own shapes."""
    def __init__(self, items, F, focal, vp):
        self.F, self.f, self.vp = F, float(focal), (float(vp[0]), float(vp[1])); self.shards = items


def _blade(rng, cx, cy, L, wid, ang):
    """a sharp glass blade (irregular triangle or dagger quad) of length L, width wid, axis angle ang (radians)."""
    ca, sa = math.cos(ang), math.sin(ang)
    if rng.random() < .5:
        pts = [(L * .5, rng.uniform(-.1, .1) * wid), (-L * .5, wid * .5 * rng.uniform(.8, 1.1)), (-L * rng.uniform(.25, .45), -wid * .5 * rng.uniform(.8, 1.1))]
    else:
        pts = [(L * .5, 0.0), (L * rng.uniform(-.05, .15), wid * .5), (-L * .5, wid * rng.uniform(.15, .35)), (-L * rng.uniform(.15, .35), -wid * .5)]
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def _heroes():
    """six blades of the cover glass around the impact (never toward his face) are blown straight AT the lens: each
    grows from 1x to ~5x in 0.3 s nearly in place, defocused + motion-blurred, and sweeps out across a frame edge."""
    for s in SH.shards: s['vz'] *= 1.6                         # the whole pane is blown toward the lens
    rng = np.random.default_rng(29); items = []
    spec = [(165, 300, 330, 120), (220, 330, 300, 130), (318, 300, 320, 120), (12, 280, 290, 140), (58, 250, 300, 110), (122, 270, 340, 130)]
    for i, (adeg, r0, L, wid) in enumerate(spec):
        a = math.radians(adeg); cx, cy = IMPACT[0] + r0 * math.cos(a), IMPACT[1] + r0 * math.sin(a)
        poly = _blade(rng, cx, cy, L, wid, a + rng.uniform(-1.1, 1.1))
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        c = (float(np.mean(xs)), float(np.mean(ys))); dx, dy = c[0] - IMPACT[0], c[1] - IMPACT[1]; dist = math.hypot(dx, dy)
        vz = -rng.uniform(4000, 5200)
        ax = rng.normal(0, 1, 3); ax[2] *= .5; ax /= np.linalg.norm(ax)
        items.append(dict(i=500 + i, polys=[poly], poly=poly, c=c, dist=dist, dir=(dx / dist, dy / dist), area=GK.poly_area(poly),
                          bbox=(int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs)) + 3, int(max(ys)) + 3),
                          vr=-dist * (-vz / FOC) * rng.uniform(.45, .62), vz=vz, axis=ax, w=rng.uniform(3.0, 5.0) * rng.choice([-1, 1]),
                          delay=dist / 20000., ph=rng.uniform(0, 6.3), grav=rng.uniform(100, 250), side=0.0,
                          cull=6.5, edge_k=1.5, shade_k=1.25, hero=True))
    return HeroShards(items, FR, FOC, VP)


HS = _heroes()


def _inside(pt, poly):
    x, y = pt; n = len(poly); ins = False
    for k in range(n):
        x0, y0 = poly[k - 1]; x1, y1 = poly[k]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0): ins = not ins
    return ins


HIDDEN = {s['i'] for s in SH.shards if any(_inside(s['c'], h['poly']) for h in HS.shards)}   # cells the blades replace

CUES = [
    (W_NOT, 'knock', {'seed': 3, 'gain': 3}),
    (W_NOT + .004, 'crack', {'dur': .5, 'seed': 7, 'gain': 0}),
    (W_MINE, 'crack', {'dur': .42, 'seed': 9, 'gain': -3}),
    (W_MINE + .02, 'glass', {'seed': 4, 'gain': -6}),
    (CREAKS[0], 'crack', {'dur': .16, 'seed': 11, 'gain': -11}),
    (CREAKS[1], 'crack', {'dur': .12, 'seed': 12, 'gain': -9}),
    (BREAK, 'boom', {'gain': 0}),
    (BREAK, 'shatter', {'dur': 1.6, 'gain': 0}),
    (BREAK + .04, 'whoosh', {'gain': -3}),
    (BREAK + .38, 'glass', {'seed': 6, 'gain': -9}),          # slow-mo shards shimmer past
    (8.82, 'swoosh_up', {'gain': -7}),                        # (peak) the hero blades fly past the lens
    (W_CONTENT, 'whoosh', {'gain': -12}),                    # snap push-in on CONTENT
    (W_CONTENT + .03, 'shimmer', {'gain': -12}),              # a drifting shard glints on CONTENT
    (W_DOESNT + .06, 'tick', {'gain': -16, 'pan': .4}),       # a far shard catches the light on DOESN'T
    (W_STAY, 'whoosh', {'gain': -13, 'pan': -.2}),            # snap back out on STAY
    (W_STAY + .02, 'tick', {'gain': -10}),                    # ...and on STAY
    (PANE_IN + .05, 'whoosh', {'gain': -9}),                  # the screen pane flies in behind him
    (W_SCREEN, 'impact', {'gain': -4}),                       # SCREEN slams onto the pane
    (SCREEN_V, 'crack', {'dur': .4, 'seed': 13, 'gain': -2}),  # ...and the pane cracks
    (SCREEN_V + .02, 'glass', {'seed': 8, 'gain': -10}),
]


def C(k, fn): return E.cached(('s04',) + (k if isinstance(k, tuple) else (k,)), fn)


# ================================================================ camera / timing curves (pure functions of t)
def z_in(t):
    """camera inside the Reel (behind the glass): slow push while the glass gives way."""
    return S3.Z_IN * (1 + .045 * smooth((min(t, BREAK) - 7.86) / (BREAK - 7.86)) ** 1.4)


Z_BRK = z_in(BREAK)


def cam_c(t):
    """forward travel of the camera after the break (units of FOC), expo-out: the camera is kicked forward by the burst
    (the glass rushes at the lens), passes the glass plane at ~9.0 and settles by 9.40 -> he comes FORWARD x1.11."""
    u = t - BREAK
    if u <= 0: return 0.0
    return C_MAX * (1 - math.exp(-min(u, U_C) / TAU_C)) / (1 - math.exp(-U_C / TAU_C))


def z_real(t):
    c = cam_c(t); z = Z_BRK * ZH / (ZH - c)
    if t > BREAK + U_C: z *= 1 + .02 * smooth((t - BREAK - U_C) / 2.4)       # keeps drifting in while he talks
    return z


def bgz_real(t):
    c = cam_c(t); return BGZ0 * (ZB / (ZB - c)) / (ZH / (ZH - c))


def tau(t):
    """shard sim time: an explosive first 2-3 frames, then 0.3x slow motion."""
    u = max(0.0, t - BREAK); return .085 * (1 - math.exp(-u / .03)) + .32 * u


def shard_ink(s, u):
    """how much of the screen image a flying shard still carries: the display layer dies within a few frames and clear
    glass remains (the UI glyphs stay printed, see glyph_key). Pieces over his face clear first so the real him reads
    through the burst at once."""
    d = math.hypot(s['c'][0] - FACE[0], (s['c'][1] - FACE[1]) * .8)
    tg = u + s['delay'] if u > 0 else 0.0               # global sim time (a piece keeps its print until released)
    return 1 - smooth(tg / (.03 if d < 300 else .06))


def any_ink(tau_):
    """True while at least one piece still carries the printed photo (else the cheap static glass print is enough)."""
    return any(shard_ink(s, max(0.0, tau_ - s['delay'])) > .004 for s in SH.shards + HS.shards)


def glyph_key():
    """alpha = the white UI glyphs of the feed chrome: they stay printed on the flying cover glass."""
    def mk():
        a = np.zeros((H, W), np.float32)
        top = np.asarray(FK.chrome_top().convert('L'), np.float32); nav = np.asarray(FK.chrome_nav().convert('L'), np.float32)
        a[:FK.TOP_Y] = np.clip((top - 60) / 110, 0, 1); a[FK.NAV_Y:] = np.clip((nav - 60) / 110, 0, 1)
        return Image.fromarray((a * 255).astype(np.uint8))
    return C('gkey', mk)


def static_glass():
    """the cover glass after the display died: only the chrome glyphs are still printed on it."""
    def mk():
        im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); im.alpha_composite(FK.chrome_top(), (0, 0))
        im.alpha_composite(FK.chrome_nav(), (0, FK.NAV_Y)); im.putalpha(glyph_key()); return im
    return C('sglass', mk)


def leak(t):
    if t < W_MINE: return 0.0
    k = .28 * smooth((t - W_MINE) / .08) + .62 * smooth((t - W_MINE - .05) / (BREAK - W_MINE - .05)) ** 1.6
    for c in CREAKS:
        if t >= c: k += .18 * math.exp(-(t - c) / .06)
    return min(1.2, k)


def refr(t):
    return 1.0 + 2.6 * smooth((t - W_MINE) / (BREAK - W_MINE)) ** 1.5 if t >= W_MINE else 1.0


def tremor(t):
    """build-up micro shake before the break (deterministic per frame)."""
    if not (W_MINE + .05 < t < BREAK): return (0.0, 0.0)
    k = smooth((t - W_MINE - .05) / (BREAK - W_MINE - .05)) ** 2 * 3.2
    i = int(round(t * E.FPS)); r = np.random.default_rng(i * 7 + 1)
    return (float(r.normal(0, 1)) * k, float(r.normal(0, 1)) * k)


# ================================================================ the glass (what is printed on it) and the real world
def glass_screen(ctx, t):
    """inside world (flat, screen look) + feed chrome. RGBA, no cracks."""
    ctx.bg_z = BGZ0
    im = S3.screen_look(S3.inside_world(ctx, t, z=z_in(t))).convert('RGBA')
    im.alpha_composite(FK.chrome_top(), (0, 0)); im.alpha_composite(FK.chrome_nav(), (0, FK.NAV_Y))
    return im


def soft_studio():
    return C('soft_studio', lambda: E.studio().filter(ImageFilter.GaussianBlur(1.1)))


PUNCH = (W_CONTENT, W_STAY)                  # snap push-in on CONTENT, snap back out on STAY (the frame doesn't stay)


def punch(t):
    """0..1 weight of the tight framing (3-frame snap zooms with a hint of overshoot)."""
    def snap(x):
        x = clamp(x / .11); return 1 - (1 - x) ** 3 + .06 * math.sin(math.pi * x) * x
    if t < PUNCH[0] - .01: return 0.0
    return snap(t - PUNCH[0] + .01) * (1 - snap(t - PUNCH[1] + .01)) if t < PUNCH[1] + .2 else 0.0


def punch_speed(t):
    return abs(punch(t + 1 / 60) - punch(t - 1 / 60)) * 30


def zoom_smear(img, amt, c=(560, 860), n=5):
    """radial motion blur of the world for the snap zooms (scale spread `amt` over a 180-degree shutter), applied
    BEFORE the captions so the words stay crisp."""
    if amt < .004: return img
    rgb = img.convert('RGB'); acc = np.zeros((H, W, 3), np.float32)
    for i in range(n):
        acc += np.asarray(E.zoom(rgb, 1 + amt * (i / (n - 1) - .5), c), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8)).convert('RGBA')


def real_world(ctx, t):
    ctx.bg_z = bgz_real(t); ctx.bg_img = soft_studio()           # a touch of DOF on the studio
    w = punch(t)
    z = z_real(t) * (1 + .17 * w)
    dx = dy = 0.0
    u = t - BREAK
    if 0 <= u < .2:   # the break hits the camera
        k = int(u * E.FPS); tab = [(0, 0), (0, 12), (-8, -7), (5, 4), (-2, -2), (1, 1)]
        if k < len(tab): dx, dy = tab[k]
    if SCREEN_V <= t < SCREEN_V + .2:
        k = int((t - SCREEN_V) * E.FPS); tab = [(0, 0), (0, 7), (-5, -4), (3, 2), (-1, -1)]
        if k < len(tab): dx, dy = tab[k]
    fr = ctx.compose(cam=dict(z=z, x=VP[0] + (560 - VP[0]) * w, y=VP[1] + (840 - VP[1]) * w, dx=dx, dy=dy, rot=0.))
    return fr


def burst_glow(t):
    """the light behind the glass bursting through the hole (additive RGBA)."""
    u = t - BREAK
    if not (0 <= u < .5): return None
    a = math.exp(-u / .05)
    def mk():
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        r = np.hypot(xx - IMPACT[0], (yy - IMPACT[1]) * .9)
        g = np.exp(-(r / 230) ** 2) + .18 * np.exp(-(r / 620) ** 2)
        return np.clip(g, 0, 1)
    g = C('burst', mk)
    im = Image.new('RGBA', (W // 4, H // 4), (226, 214, 255, 0))
    im.putalpha(Image.fromarray(np.clip(g * 255 * a, 0, 255).astype(np.uint8)))
    return im.resize((W, H), Image.BILINEAR)


def add_light(fr, glow, col=(226, 214, 255)):
    """additive light (the glow's alpha x col) onto fr. (The colour is passed explicitly: a resized RGBA glow is
    premultiplied, so its transparent corner pixel reads black.)"""
    if glow is None: return fr
    from PIL import ImageChops
    al = glow.getchannel('A'); r, g, b = col
    add = Image.merge('RGB', [al.point(lambda v, c=c: int(v * c / 255 * .9)) for c in (r, g, b)])
    return ImageChops.add(fr.convert('RGB'), add).convert('RGBA')


# the photographic glass look of the flying pieces (GK render_refract "hero look")
GLASS_KW = dict(dof=2.5, near=120.0, cull_scale=4.2, glyph_alpha=.9, refract=26.0, edge=2.2, veil=.10, sheen=.5,
                reflect=1.0, refl_cap=.5, env_q=2, env_pow=3.0, bevel=2.6, shade=.85, absorb=.22, tint=(12, 10, 30), rim=1.0,
                blur_cap=9.0, blur_fade=30.0, max_smear=12, smear_div=4.0, star_scale=4.0, smear_soft=True,
                q_blur=5.0, tex_r_area=90000, thick=2.4, gloss=.9)
BLOOM = 1.0


def bloom(fr, base, k):
    """photographic bloom of the glass highlights only: what the shards ADD over the world (hot bevels, glints,
    reflections) glows softly (quarter res)."""
    if k <= 0: return fr
    a = np.asarray(fr.convert('RGB'), np.int16); b = np.asarray(base.convert('RGB'), np.int16)
    d = np.clip((a - b).max(2) - 45, 0, 255).astype(np.uint8)
    sm = Image.fromarray(d).resize((W // 4, H // 4), Image.BOX)
    g = np.asarray(sm.filter(ImageFilter.GaussianBlur(2.2)), np.float32) * 1.6 + np.asarray(sm.filter(ImageFilter.GaussianBlur(7)), np.float32) * 1.4
    g = np.asarray(Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255 * k
    out = a + g[..., None] * np.array([150, 140, 255], np.float32) * .55
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')


# ================================================================ drifting slow-mo shards after the break
class Floaters(GK.Shatter):
    """a few loose shards drifting in slow motion around him (camera-relative 3-D), carrying bits of the feed UI."""
    def __init__(self, items, focal, vp):
        self.f, self.vp = float(focal), (float(vp[0]), float(vp[1]))
        self.shards = items; self.F = None

    def pose(self, s, tau):
        u = tau
        P = np.array(s['p0'], float) + np.array(s['v'], float) * u + np.array([0, .5 * s['grav'] * u * u, 0])
        tx, ty, tz = s['tilt0']; ph = s['ph']
        R = GK.rot3(tx + .32 * math.sin(.9 * u + ph), ty + .32 * math.cos(.7 * u + ph * 1.3), tz + s['w'] * u)   # slow spin + wobble
        return P, R, u


def _poly(rng, cx, cy, r):
    """a chunky convex-ish glass shard outline (3-5 corners) of radius ~r around (cx, cy) in texture space."""
    n = int(rng.integers(3, 6)); a0 = rng.uniform(0, 6.28)
    angs = a0 + (np.arange(n) + rng.uniform(-.28, .28, n)) * 2 * math.pi / n
    k = rng.uniform(.55, 1.0)                                 # elongation
    return [(cx + r * rng.uniform(.65, 1.1) * math.cos(a), cy + r * k * rng.uniform(.65, 1.1) * math.sin(a)) for a in angs]


def floaters():
    def mk():
        rng = np.random.default_rng(41); items = []
        # (screen x, y at t = 10 s, depth (FOC units, camera-relative), screen radius px, texture centre on the cover
        # glass). Kept off his face, off the caption band (y 1300-1540) and off the pane's corner zone; three carry a
        # UI glyph (heart, "For you", home), one is a big defocused foreground piece for depth.
        spec = [(120, 330, 1.5, 120, (927, 128)),      # heart glyph, top-left
                (968, 290, 2.2, 90, (150, 128)),       # "For you" fragment, top-right
                (40, 1080, .8, 230, (540, 980)),       # big soft foreground piece, left edge
                (1010, 900, 1.1, 140, (540, 1040)),    # right, mid
                (160, 1716, 1.3, 130, (108, 1830)),    # home glyph, lower-left
                (950, 1700, 1.6, 110, (756, 1830)),    # reels glyph, lower-right
                (915, 640, 3.4, 48, (540, 1100)),      # small far piece beside his head
                (200, 560, 3.0, 56, (560, 1160))]      # small far piece, left
        for i, (sx, sy, d, r, (tx, ty)) in enumerate(spec):
            Z = d * FOC; X = (sx - VP[0]) * Z / FOC; Y = (sy - VP[1]) * Z / FOC
            poly = _poly(rng, tx, ty, r * d)
            xs, ys = [p[0] for p in poly], [p[1] for p in poly]
            bbox = (int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs)) + 3, int(max(ys)) + 3)
            ax = rng.normal(0, 1, 3); ax /= np.linalg.norm(ax)
            out = (X / (math.hypot(X, Y) + 1e-6), Y / (math.hypot(X, Y) + 1e-6))
            v = (out[0] * rng.uniform(25, 55) * d, (out[1] * rng.uniform(12, 30) + 14) * d, rng.uniform(-60, 0))
            u0 = 10.0 - BREAK                                     # positions above are where they are at t = 10 s
            p0 = (X - v[0] * u0, Y - v[1] * u0, Z - v[2] * u0)
            items.append(dict(i=1000 + i, poly=poly, bbox=bbox, c=(float(np.mean(xs)), float(np.mean(ys))),
                              p0=p0, v=v, grav=0.0, axis=ax, w=rng.uniform(.25, .55) * rng.choice([-1, 1]),
                              ph0=0.0, tilt0=(rng.uniform(-.45, .45), rng.uniform(-.45, .45), rng.uniform(-3, 3)),
                              ph=rng.uniform(0, 6.3), delay=0.0, dist=500, dir=out, vr=0, vz=0, side=0))
        return Floaters(items, FOC, VP)
    return C('floaters3', mk)


FLOAT_GLINTS = [(0, W_CONTENT + .02, 1.0), (3, W_STAY + .02, 1.0), (6, W_DOESNT + .06, .5)]   # light catches on words


def floater_vertex(fl, s, tau):
    """screen position of the piece's corner that faces the key light (where a glint sits)."""
    P, R, _ = fl.pose(s, tau); cx, cy = s['c']
    loc = np.array([[x - cx, y - cy, 0] for x, y in s['poly']], float)
    pp = fl.proj(P[None] + loc @ R.T)
    k = int(np.argmin(pp[:, 0] * .55 + pp[:, 1] * .83)); return pp[k], FOC / P[2]


def render_floaters(fr, t):
    fl = floaters(); tau_ = t - BREAK
    fr = fl.render_refract(fr, static_glass(), tau_, dz=0.0, focus_z=(ZH - C_MAX) * FOC, dof=8.0, shutter_dtau=.004,
                           near=200, alpha=floater_alpha(t), cull_scale=9, img_alpha=0.0, glyph_alpha=.9, refract=18.0,
                           edge=2.2, veil=.9, sheen=1.0, reflect=2.2, bevel=3.4, spec_gain=1.6)
    for i, tg, amp in FLOAT_GLINTS:
        u = t - tg
        if not (-.05 < u < .35): continue
        a = clamp((u + .05) / .05) * math.exp(-max(0, u) / .11) * floater_alpha(t) * amp
        if a < .03: continue
        (x, y), sc = floater_vertex(fl, fl.shards[i], tau_)
        sz = int(110 + 120 * min(1.4, sc) * amp) | 1; st = GK.star(64, 8).resize((sz, sz), Image.BILINEAR)
        E._paste(fr, dict(img=E.fade(st, min(1, a)), xy=(int(x - sz / 2), int(y - sz / 2)), glass=0))
    return fr


def floater_alpha(t):
    return smooth((t - BREAK - .30) / .35)


# ================================================================ "ON THE SCREEN." pane
PW, PH = 736, 252
PANE_W = (550.0, 556.0)                        # world position (centre) — behind his head
PF = GK.Fracture(center=(560, 128), size=(PW, PH), seed=21, radials=12,
                 rings=[12, 30, 56, 92, 140, 200, 280, 380, 520, 700],
                 hits=[(SCREEN_V, 26, 64, .7, .03)], race=(SCREEN_V + .025, 4200), web=(SCREEN_V + .07, .12))


def pane_body():
    def mk():
        S = 3; m = Image.new('L', (PW * S, PH * S)); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW * S - 1, PH * S - 1), 30 * S, fill=255)
        m = m.resize((PW, PH), Image.LANCZOS)
        yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
        body = np.zeros((PH, PW, 3), np.float32) + np.array([12, 11, 24], np.float32)
        body += (1 - yy / PH)[..., None] * np.array([22, 18, 44], np.float32)                 # top lighter
        sheen = np.exp(-(((xx * .55 + yy * .9) - PW * .38) / 70) ** 2) * 26 + np.exp(-(((xx * .55 + yy * .9) - PW * .52) / 18) ** 2) * 14
        body += sheen[..., None]
        al = np.asarray(m, np.float32) / 255 * .80
        im = Image.fromarray(np.dstack([np.clip(body, 0, 255), al * 255]).astype(np.uint8), 'RGBA')
        b = Image.new('L', (PW * S, PH * S)); ImageDraw.Draw(b).rounded_rectangle((S, S, PW * S - 1 - S, PH * S - 1 - S), 29 * S, outline=255, width=2 * S)
        b = b.resize((PW, PH), Image.LANCZOS); bb = np.asarray(b, np.float32) / 255
        top = np.clip(1.15 - yy / PH * 1.2, .25, 1)            # bezel catches light on top
        edge = Image.fromarray(np.dstack([np.full((PH, PW, 3), 245, np.float32), bb * top * 150]).astype(np.uint8), 'RGBA')
        im.alpha_composite(edge)
        return im
    return C('pbody', mk)


def pane_glow():
    def mk():
        w, h = PW + 260, PH + 260; m = Image.new('L', (w, h))
        ImageDraw.Draw(m).rounded_rectangle((130, 130, w - 130, h - 130), 40, fill=200)
        im = Image.new('RGBA', (w, h), (120, 86, 255, 0)); im.putalpha(m.filter(ImageFilter.GaussianBlur(55))); return im
    return C('pglow', mk)


def word_art(text, size, wght, grad):
    def mk():
        f = E.font(size, wght); l, t_, r, b = f.getbbox(text); pad = int(size * .35)
        w, h = r - l + 2 * pad, b - t_ + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t_), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        if grad:
            gl = Image.new('RGBA', (w, h), (130, 90, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(size * .16)).point(lambda v: int(v * .7)))
            out.alpha_composite(gl)
            g = np.asarray(E.gradient(w, h, E.GRAD_LIGHT), np.float32) * np.linspace(1.15, .92, h)[:, None, None]
            g = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert('RGBA'); g.putalpha(m); out.alpha_composite(g)
        else:
            c = Image.new('RGBA', (w, h), (244, 243, 250, 0)); c.putalpha(m.point(lambda v: int(v * .92))); out.alpha_composite(c)
        return out, pad
    return C(('word', text, size, wght, grad), mk)


def pane_art(t):
    """pane with the words landed so far + its cracks (RGBA, PW x PH)."""
    im = pane_body().copy()
    # ON / THE land word by word (small, tracked), SCREEN. slams large
    def put(text, t0, size, wght, grad, x, y, pop=1.18):
        if t < t0 - .02: return
        art, pad = word_art(text, size, wght, grad)
        k = clamp((t - t0 + .02) / .14); s = 1 + (pop - 1) * (1 - eout(k)) ** 2
        a = clamp((t - t0 + .02) / .05)
        img = art if abs(s - 1) < .005 else art.resize((int(art.width * s), int(art.height * s)), Image.BILINEAR)
        cx, cy = x + art.width / 2 - pad, y + art.height / 2 - pad
        E._paste(im, dict(img=E.fade(img, a), xy=(int(cx - img.width / 2), int(cy - img.height / 2)), glass=0))
    put('ON', W_ON, 50, 700, False, 46, 24)
    put('THE', W_THE, 50, 700, False, 46 + int(E.font(50, 700).getlength('ON ')) + 2, 24)
    put('SCREEN.', W_SCREEN, 150, 900, True, 44, 80, pop=1.3)
    if t >= SCREEN_V:
        rgb = PF.composite(im.convert('RGB'), t, refr=1.2, leak=.25 * math.exp(-(t - SCREEN_V) / .25), glint=1.4 + 2 * math.exp(-(t - SCREEN_V) / .1),
                           sweep=200 + (t - SCREEN_V) * 600, powder=.9, sparks=1.0)
        rgb.putalpha(im.getchannel('A')); im = rgb
    return im


def pane_layer(ctx, t):
    """adds the pane in world space ('behind' him), flying in from depth with a slight 3-D tilt."""
    if t < PANE_IN: return
    k = clamp((t - PANE_IN) / .30); e = 1 - (1 - k) ** 4
    art = pane_art(t)
    depth = lerp(2.4, 1.0, e)                                 # flies in from far
    s = 1 / depth
    ry = lerp(-26, -9, e) + 1.5 * math.sin((t - PANE_IN) * 1.3); rx = lerp(10, 4, e); rz = lerp(-4, -1.2, e)
    cx, cy = PANE_W[0] + lerp(60, 0, e), PANE_W[1] + lerp(-40, 0, e) - 6 * smooth((t - PANE_IN) / 1.0)
    if SCREEN_V <= t < SCREEN_V + .15:                         # the hit pushes it back a touch
        cx += 0; cy += 4 * math.sin((t - SCREEN_V) * 60) * math.exp(-(t - SCREEN_V) / .05)
    pts = GK.project(PW, PH, 0, 0, s, rx, ry, rz, f=1800.)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ox, oy = int(math.floor(min(xs))) - 2, int(math.floor(min(ys))) - 2
    ow, oh = int(math.ceil(max(xs))) - ox + 3, int(math.ceil(max(ys))) - oy + 3
    co = GK.homography([(0, 0), (PW, 0), (PW, PH), (0, PH)], [(x - ox, y - oy) for x, y in pts])
    im = art.transform((ow, oh), Image.PERSPECTIVE, co, Image.BICUBIC)
    blur = 6 * (1 - e) ** 2
    if blur > .4: im = im.filter(ImageFilter.GaussianBlur(blur))
    a = clamp(k * 3.5)
    # the pane is a lit screen: soft violet spill on the wall behind it, then the glass itself
    ctx.add('behind', pane_glow(), cx, cy + 10, alpha=a * .55 * (1 + .6 * math.exp(-max(0, t - W_SCREEN) / .15) * (t >= W_SCREEN)))
    ctx.add('behind', im, cx + ox + ow / 2, cy + oy + oh / 2, alpha=a)
    v = t - SCREEN_V
    if -.01 < v < .16:   # light catch at the impact on the pane
        uu, vv = PF.C[0] / PW, PF.C[1] / PH
        px = (1 - uu) * (1 - vv) * pts[0][0] + uu * (1 - vv) * pts[1][0] + uu * vv * pts[2][0] + (1 - uu) * vv * pts[3][0]
        py = (1 - uu) * (1 - vv) * pts[0][1] + uu * (1 - vv) * pts[1][1] + uu * vv * pts[2][1] + (1 - uu) * vv * pts[3][1]
        fa = clamp((v + .01) / .02) * math.exp(-max(0, v) / .05)
        sz = 190; st = GK.star(64, 8).resize((sz, sz), Image.BILINEAR)
        ctx.add('behind', st, cx + px, cy + py, alpha=min(1, fa))


# ================================================================ draw
def draw(ctx, lt, t):
    P = ctx.post
    ctx.captions = t < BREAK or 9.30 <= t < CAP_OFF
    if t < S3.OPEN1:                                             # the Reel finishing its opening (from s03)
        ctx.bg_z = BGZ0
        fr = S3.reel_screen(ctx, t)
        ctx.full = S3.glass_post(fr, t)
        P['vignette'] = .10; P['grain'] = .55
        return
    if t < BREAK:
        fr = glass_screen(ctx, t)
        lk = leak(t)
        ctx.full = S3.glass_post(fr, t, z0=1.0, extra=tremor(t), leak=lk, refr=refr(t), glint_base=1.0 + .6 * lk,
                                 sweep=200 + (t - W_NOT) * 1500, leak_falloff=(.12, 430.0))
        P['vignette'] = .10 + .2 * lk; P['grain'] = .55 + .3 * lk
        if t > BREAK - .06: P['bright'] = 1 + .25 * smooth((t - BREAK + .06) / .06)
        return
    u = t - BREAK
    P['vignette'] = .34; P['grain'] = 1.0
    if t < 9.30:
        g = None
        if SH.visible(tau(t), cam_c(t) * FOC, 120.0, 4.2) or HS.visible(tau(t), cam_c(t) * FOC, 120.0, 4.2):
            if any_ink(tau(t)):
                g = glass_screen(ctx, t)
                g = FR.composite(g, BREAK, refr=refr(BREAK), leak=1.0 * math.exp(-u / .12) + .25, glint=2.0, sweep=900, leak_falloff=(.12, 430.0)).convert('RGBA')
                g.putalpha(glyph_key())
            else: g = static_glass()
        rw = real_world(ctx, t)
        rw = add_light(rw, burst_glow(t))
        c = cam_c(t)
        fs = lerp(1 / (1 - .8 * c), 1 / (ZH - c), smooth((u - .25) / .35))   # focus on the mid glass, then rack to him
        foc = FOC / fs
        SHUT = .25 / E.FPS                                           # short shutter: crisp, high-speed-photography shards
        dtau = tau(t) - tau(t - SHUT)
        if g is not None:
            kw = dict(dz=c * FOC, focus_z=foc, shutter_dtau=dtau, dz_prev=cam_c(t - SHUT) * FOC, img_alpha=shard_ink,
                      backlight=1.0 * math.exp(-u / .08), **GLASS_KW)
            fr = SH.render_refract(rw, g, tau(t), keep=lambda s: s['i'] not in HIDDEN, **kw)
            fr = HS.render_refract(fr, g, tau(t), **kw)
        else: fr = rw
        if g is not None: fr = bloom(fr, rw, BLOOM)
        if u < .05: fr = add_light(fr, burst_glow(t))            # the break itself: a hot radial burst in front of the glass
        da = smooth(u / .03) * (1 - smooth((u - .35) / .3))
        if da > .01:
            fr.alpha_composite(DUST.render((W, H), tau(t), c * FOC, tau(t) - tau(t - .5 / E.FPS), cam_c(t - .5 / E.FPS) * FOC, alpha=da,
                                           taper=True, sparkle=.3, gain=1.3))
        if u > .25: fr = render_floaters(fr, t)
        ctx.full = fr
        P['flash'] = .28 * math.exp(-u / .03); P['flash_col'] = (236, 228, 255); P['bright'] = 1 + .35 * math.exp(-u / .04)
        return
    # ------------------------------------------------ 9.30 – 11.96: out in the studio
    pane_layer(ctx, t)
    rw = real_world(ctx, t)
    ps = punch_speed(t)
    if ps > .05: rw = zoom_smear(rw, min(.05, .17 * ps / E.FPS * .5))
    fr = render_floaters(rw, t)
    ctx.full = fr
    if W_SCREEN <= t < W_SCREEN + .12: P['bright'] = 1 + .12 * math.exp(-(t - W_SCREEN) / .04)
    if SCREEN_V <= t < SCREEN_V + .15: P['bright'] = 1 + .18 * math.exp(-(t - SCREEN_V) / .05)
