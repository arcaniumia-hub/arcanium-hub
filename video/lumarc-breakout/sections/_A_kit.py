"""Private helpers for s01_feed + s02_tinyflat (author A). Not a section (the loader only matches sNN_*.py).

  - easing / spring, homography + 3-D plane projection (copied from ../lumarc-showcase s02)
  - vblur(): vertical motion blur (box, cumulative sum) for the fast feed scroll
  - feed(): FK.screen + the live bits of HIS post (ticking like count, real Reel playhead bar)
  - well(): his Reel media pushed back into a lit box ("down here"): perspective walls lit by the spill of his studio,
    glossy floor reflection, AO seams, glass rim
  - ripple(): glass-tap ripple (refraction rings + caustic highlight) on an image
  - card_quad(): textured card projected onto the screen through a tilted 3-D plane (mip-mapped, AA edges, fog, DOF)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
import sections.feedkit as FK

W, H = E.W, E.H
MW, MH = FK.W, FK.MEDIA_H
clamp, eout, ein = E.clamp, E.eout, E.ein


def C(k, fn): return E.cached(('A',) + (k if isinstance(k, tuple) else (k,)), fn)
def lerp(a, b, k): return a + (b - a) * k
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def qio(x): x = clamp(x); return 8 * x ** 4 if x < .5 else 1 - (-2 * x + 2) ** 4 / 2
def expo(x): x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0
def expo_in(x): x = clamp(x); return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def spring(x, k=7.0, damp=5.0):
    """0 -> 1 with a damped overshoot (x in seconds)."""
    if x <= 0: return 0.0
    return 1 - math.exp(-damp * x) * math.cos(k * x)
def kick(x, tau=.12):
    """1 at x=0 decaying to 0 (impulse envelope), 0 before."""
    return 0.0 if x < 0 else math.exp(-x / tau)


# ---------------------------------------------------------------- geometry
def homography(src, dst):
    """coeffs for PIL PERSPECTIVE mapping output (dst) -> input (src)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def rot(rx, ry, rz):
    rx, ry, rz = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


class Plane:
    """a flat plane (u, v in plane px) seen by a pinhole camera: the plane point (u0, v0) lands on screen (sx, sy) at
    scale k; the plane is rotated by rx (top away from camera for rx > 0), ry, rz; focal f (px)."""
    def __init__(self, u0, v0, sx, sy, k, rx=0., ry=0., rz=0., f=2400.):
        self.u0, self.v0, self.sx, self.sy, self.k, self.f = u0, v0, sx, sy, k, f
        self.R = rot(-rx, ry, rz)
    def p3(self, u, v):
        X, Y, Z = self.R @ np.array([(u - self.u0) * self.k, (v - self.v0) * self.k, 0.])
        return float(X), float(Y), float(Z)
    def proj(self, u, v):
        X, Y, Z = self.p3(u, v); z = self.f / max(1e-3, self.f + Z)
        return self.sx + X * z, self.sy + Y * z, Z
    def depth(self, u, v): return self.p3(u, v)[2]


def warp_into(base, src, quad, alpha=1.0, blur=0.0, bright=1.0, tint=None, pad=2, aniso=False):
    """projectively map the whole of `src` (RGBA) onto screen `quad` (4 corners TL TR BR BL) of `base` (RGBA in place).
    Prefilters (mip) so a minified card does not alias; AA edges via a transparent pad."""
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    x0, y0 = max(0, int(math.floor(min(xs))) - 2), max(0, int(math.floor(min(ys))) - 2)
    x1, y1 = min(base.width, int(math.ceil(max(xs))) + 2), min(base.height, int(math.ceil(max(ys))) + 2)
    if x1 - x0 < 2 or y1 - y0 < 2: return
    # projected size -> pre-scale the source to ~1.4x of it (cheap mip)
    ew = max(math.hypot(quad[1][0] - quad[0][0], quad[1][1] - quad[0][1]), math.hypot(quad[2][0] - quad[3][0], quad[2][1] - quad[3][1]))
    if aniso:      # a receding plane is minified far more vertically than horizontally
        eh = max(math.hypot(quad[3][0] - quad[0][0], quad[3][1] - quad[0][1]), math.hypot(quad[2][0] - quad[1][0], quad[2][1] - quad[1][1]))
        sx_, sy_ = min(1.0, 1.4 * ew / src.width), min(1.0, 1.4 * eh / src.height)
        if sx_ < .95 or sy_ < .95:
            src = src.resize((max(4, int(src.width * sx_)), max(2, int(src.height * sy_))), Image.BILINEAR, reducing_gap=2.0)
    else:
        sc = min(1.0, 1.4 * ew / src.width)
        if sc < .95:
            src = src.resize((max(4, int(src.width * sc)), max(4, int(src.height * sc))), Image.BILINEAR, reducing_gap=2.0)
    if pad:
        s2 = Image.new('RGBA', (src.width + 2 * pad, src.height + 2 * pad), (0, 0, 0, 0)); s2.paste(src, (pad, pad)); src = s2
        sq = [(pad, pad), (src.width - pad, pad), (src.width - pad, src.height - pad), (pad, src.height - pad)]
    else:
        sq = [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)]
    dq = [(x - x0, y - y0) for x, y in quad]
    co = homography(sq, dq)
    out = src.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BILINEAR)
    if bright != 1 or tint is not None:
        a = np.asarray(out, np.float32); rgb = a[..., :3] * bright
        if tint is not None: rgb = rgb + (np.array(tint[:3], np.float32) - rgb) * tint[3]
        a = np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]); out = Image.fromarray(a.astype(np.uint8), 'RGBA')
    if blur > .4:
        if blur > 3 and out.width * out.height > 120000:
            q = 3; sm = out.resize((max(2, out.width // q), max(2, out.height // q)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur / q))
            out = sm.resize(out.size, Image.BILINEAR)
        else: out = out.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1: out = E.fade(out, alpha)
    base.alpha_composite(out, (x0, y0))


def affine(img, s, src_anchor, dst_anchor, size, resample=Image.BILINEAR):
    """scale `img` by s so that src_anchor lands on dst_anchor; output `size`."""
    a = 1 / s; c = src_anchor[0] - dst_anchor[0] / s; f = src_anchor[1] - dst_anchor[1] / s
    return img.transform(size, Image.AFFINE, (a, 0, c, 0, a, f), resample)


def radial_blur(img, S, center, passes=3):
    """continuous zoom/radial motion blur: the average of 2**passes copies magnified about `center` by log-evenly
    spaced factors 1 .. S (recursive doubling: pass k blends the image with itself scaled by r**(2**k)). Smooth
    streaks, no stepped ghost copies."""
    if S <= 1.002: return img
    mode = img.mode; out = img.convert('RGB'); n = 2 ** passes; r = S ** (1.0 / (n - 1))
    for k in range(passes - 1, -1, -1):
        f = r ** (2 ** k)
        out = Image.blend(out, affine(out, f, center, center, out.size), .5)
    return out.convert(mode) if mode != 'RGB' else out


# ---------------------------------------------------------------- mip pyramids (anisotropic, lazy, cached)
_PYR = {}
def pyr_level(key, base_fn, a, b):
    """level (a, b) of the pyramid of base_fn(): width / 2**a, height / 2**b (box-filtered reduce, cached)."""
    k = (key, a, b)
    if k in _PYR: return _PYR[k]
    if a == 0 and b == 0: im = base_fn()
    elif a >= b and a > 0: im = pyr_level(key, base_fn, a - 1, b).reduce((2, 1))
    else: im = pyr_level(key, base_fn, a, b - 1).reduce((1, 2))
    _PYR[k] = im; return im


_PADM = {}
def _pad_mask(w, h, pad):
    k = (w, h, pad)
    if k not in _PADM:
        m = Image.new('L', (w + 2 * pad, h + 2 * pad), 0); m.paste(255, (pad, pad, pad + w, pad + h)); _PADM[k] = m
        if len(_PADM) > 400: _PADM.clear()
    return _PADM[k]


def _grade_lut(bright, tint):
    lut = []
    for c in range(3):
        tc, ta = (tint[c], tint[3]) if tint is not None else (0, 0.)
        lut += [int(min(255, max(0, v * bright * (1 - ta) + tc * ta))) for v in range(256)]
    return lut


def warp_pyr(base, key, base_fn, size, quad, vfrac=1.0, blur=0.0, bright=1.0, tint=None, alpha=1.0, mask=None, mq=4,
             mipblur=False):
    """warp_into for a cached OPAQUE card: picks the anisotropic mip level that matches the projected footprint (no
    per-frame resize of the full-res card), crops it to the top `vfrac` of its height (near clip). Warped as RGB + an
    L coverage mask (AA edges via a 2 px pad) and graded with a LUT — ~2x cheaper than an RGBA warp.
    mipblur: depth-of-field from a coarser mip level (box pyramid + bilinear = soft) instead of a Gaussian pass.
    `mask` (L, 1/mq res): the quad is also filled there (coverage of the glass plane). Returns True if drawn."""
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    x0, y0 = max(0, int(math.floor(min(xs))) - 2), max(0, int(math.floor(min(ys))) - 2)
    x1, y1 = min(base.width, int(math.ceil(max(xs))) + 2), min(base.height, int(math.ceil(max(ys))) + 2)
    if x1 - x0 < 2 or y1 - y0 < 2: return False
    if mask is not None: ImageDraw.Draw(mask).polygon([(x / mq, y / mq) for x, y in quad], fill=255)
    W0, H0 = size; H0 = H0 * vfrac
    bw_, bh_ = x1 - x0, y1 - y0
    # a strongly defocused card is warped AND blurred at 1/3 res, then upscaled (9x fewer warped pixels)
    lq = 3 if (blur > 3 and not mipblur and bw_ * bh_ > 60000) else 1
    qd = [((x - x0) / lq, (y - y0) / lq) for x, y in quad]
    osz = (max(2, int(math.ceil(bw_ / lq))), max(2, int(math.ceil(bh_ / lq))))
    ew = max(math.hypot(qd[1][0] - qd[0][0], qd[1][1] - qd[0][1]), math.hypot(qd[2][0] - qd[3][0], qd[2][1] - qd[3][1]), 1)
    eh = max(math.hypot(qd[3][0] - qd[0][0], qd[3][1] - qd[0][1]), math.hypot(qd[2][0] - qd[1][0], qd[2][1] - qd[1][1]), 1)
    a = max(0, min(6, int(math.floor(math.log2(max(1.0, W0 / (1.3 * ew)))))))
    b = max(0, min(7, int(math.floor(math.log2(max(1.0, H0 / (1.3 * eh)))))))
    if mipblur and blur > .8:
        sx, sy = ew * 2 ** a / W0, eh * 2 ** b / H0           # screen px per texel
        while a < 6 and sx * 2 <= blur * 1.1: a += 1; sx *= 2
        while b < 7 and sy * 2 <= blur * 1.1: b += 1; sy *= 2
        blur = max(0.0, blur - max(sx, sy)) * .5
    src = pyr_level(key, lambda: base_fn().convert('RGB'), a, b)
    if vfrac < .999: src = src.crop((0, 0, src.width, max(2, int(round(src.height * vfrac)))))
    pad = 2
    s2 = Image.new('RGB', (src.width + 2 * pad, src.height + 2 * pad)); s2.paste(src, (pad, pad))
    sq = [(pad, pad), (s2.width - pad, pad), (s2.width - pad, s2.height - pad), (pad, s2.height - pad)]
    co = homography(sq, qd)
    out = s2.transform(osz, Image.PERSPECTIVE, co, Image.BILINEAR)
    if osz[0] * osz[1] > 40000:      # the coverage mask is smooth: warp it at half res and upscale (AA edge ~1 px)
        co2 = homography(sq, [(x / 2, y / 2) for x, y in qd])
        m = _pad_mask(src.width, src.height, pad).transform(((osz[0] + 1) // 2, (osz[1] + 1) // 2), Image.PERSPECTIVE, co2,
                                                            Image.BILINEAR).resize(osz, Image.BILINEAR)
    else: m = _pad_mask(src.width, src.height, pad).transform(osz, Image.PERSPECTIVE, co, Image.BILINEAR)
    if bright != 1 or tint is not None: out = out.point(_grade_lut(round(bright, 3), None if tint is None else tuple(round(v, 3) for v in tint)))
    if lq > 1:
        out = out.filter(ImageFilter.GaussianBlur(blur / lq)).resize((bw_, bh_), Image.BILINEAR)
        m = m.filter(ImageFilter.GaussianBlur(blur / lq)).resize((bw_, bh_), Image.BILINEAR)
    elif blur > .4:
        if blur > 3 and out.width * out.height > 60000:
            q = 3; sz = (max(2, out.width // q), max(2, out.height // q))
            out = out.resize(sz, Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur / q)).resize(out.size, Image.BILINEAR)
            m = m.resize(sz, Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur / q)).resize(out.size, Image.BILINEAR)
        else:
            out = out.filter(ImageFilter.GaussianBlur(blur)); m = m.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1: m = m.point(lambda v: int(v * alpha))
    base.paste(out, (x0, y0), m)
    return True


def desat(img, s):
    """saturation s (0 grey .. 1 original), RGBA kept."""
    a = np.asarray(img, np.float32); rgb = a[..., :3]; g = rgb @ np.array([.299, .587, .114], np.float32)
    rgb = g[..., None] + (rgb - g[..., None]) * s
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]).astype(np.uint8), img.mode) if img.mode == 'RGBA' \
        else Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- motion blur
def vblur(im, L):
    """vertical box blur of length L px (uniform vertical translation during a 180-degree shutter)."""
    n = int(round(L))
    if n < 2: return im
    a = np.asarray(im, np.float32); h = a.shape[0]
    padded = np.concatenate([np.repeat(a[:1], n // 2, 0), a, np.repeat(a[-1:], n - n // 2, 0)], 0)
    c = np.cumsum(padded, 0, dtype=np.float32); c = np.concatenate([np.zeros_like(c[:1]), c], 0)
    out = (c[n:n + h] - c[:h]) / n
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), im.mode)


# ---------------------------------------------------------------- the live feed
LIKES0 = 48213
def likes_at(t):
    """live like counter for his post (a like lands every ~0.21-0.34 s)."""
    n = 0; tt = 0.0; r = np.random.default_rng(11)
    while True:
        tt += float(r.uniform(.21, .34))
        if tt > t: break
        n += 1
    return LIKES0 + n


def special_foot(likes):
    """FK's foot for his post, with an exact (ticking) like count."""
    p = FK.POSTS[FK.SPECIAL]
    def mk():
        im = FK._foot(FK.SPECIAL).copy(); d = ImageDraw.Draw(im)
        d.rectangle((24, FK.ACT_H, 520, FK.ACT_H + 46), fill=FK.BG)
        d.text((30, FK.ACT_H + 4), f'{likes:,} likes', font=E.font(30, 700), fill=FK.FG)
        return im
    return C(('foot', likes), mk)


def progress_bar(pg, w=MW):
    """thin Reel playhead bar (sits on the bottom edge of the media)."""
    im = Image.new('RGBA', (w, 6), (255, 255, 255, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 2, w, 5), fill=(255, 255, 255, 70))
    d.rectangle((0, 2, int(w * clamp(pg)), 5), fill=(255, 255, 255, 235))
    return im


def special_top(scroll): return FK.TOP_Y + FK.post_top(FK.SPECIAL) - scroll


def feed(scroll, media, t, chrome=True, blurL=0.0):
    """full phone screen (RGBA) with his media; the like count ticks; motion blur under fixed chrome."""
    scr = FK.screen(scroll, special=media, t=t, chrome=False)
    top = special_top(scroll)
    FK._paste_clip(scr, special_foot(likes_at(t)), 0, top + FK.HEAD_H + FK.MEDIA_H)
    if blurL > 1.5: scr = vblur(scr, blurL)
    if chrome:
        scr.alpha_composite(FK.chrome_top(), (0, 0)); scr.alpha_composite(FK.chrome_nav(), (0, FK.NAV_Y))
    return scr


# ---------------------------------------------------------------- the well ("down here")
def _grids():
    def mk():
        yy, xx = np.mgrid[0:MH, 0:MW].astype(np.float32); return yy, xx
    return C('grids', mk)


def _prof(a, axis, n_keep, smooth_px):
    """mean emission along an edge strip of the back wall (light that spills onto the adjacent wall)."""
    from scipy.ndimage import gaussian_filter1d
    p = a.mean(axis=axis); return gaussian_filter1d(p, smooth_px, axis=0, mode='nearest')


_WG = {}
def _well_geom(sb, VX, VY, q=2):
    """geometry-only maps of the box at 1/q resolution (cached for the last few depths)."""
    key = (round(sb, 4), VX, VY, q)
    if key in _WG: return _WG[key]
    h, w = MH // q, MW // q
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); yy = yy * q + q / 2; xx = xx * q + q / 2
    dx = xx - VX; dy = yy - VY
    sx = np.where(dx > 0, dx / (MW - VX), dx / (-VX))
    sy = np.where(dy > 0, dy / (MH - VY), dy / (-VY))
    side = sx > sy
    s = np.maximum(np.maximum(sx, sy), 1e-3)
    z = np.clip((1 / s - 1) / (1 / sb - 1), 0, 1)            # 0 at the front rim .. 1 at the back wall (perspective-correct)
    fx = np.where(side, VY + dy / s, VX + dx / s)               # where this pixel's depth line meets the front rim
    ri = np.clip(fx / MH * 67, 0, 67).astype(np.int32); ci = np.clip(fx / MW * 53, 0, 53).astype(np.int32)
    gain = np.where(side, .95, np.where(dy > 0, .62, .80))
    lit = ((.05 + 1.05 * z ** 2.4 + .55 * np.exp(-(1 - z) / .05)) * gain).astype(np.float32)
    pitch = 135.0
    ln = np.abs(((fx + pitch / 2) % pitch) - pitch / 2) * s / q
    lines = np.clip(1 - ln / 1.1, 0, 1) * (z * 10 + 3)
    zl = z * 4.0; dz = np.abs(zl - np.round(zl)) * (1 / s)
    lines = (lines + np.clip(1 - dz / (.018 * q), 0, 1) * (z > .05) * (z < .97) * 6).astype(np.float32)
    seam = np.abs(sx - sy) / np.maximum(s, 1e-3)
    ao = (1 - .45 * np.clip(1 - seam / (.03 * q), 0, 1)).astype(np.float32)
    which = np.where(side, np.where(dx > 0, 2, 3), np.where(dy > 0, 0, 1)).astype(np.int8)   # 0 floor 1 ceil 2 right 3 left
    g = dict(lit=lit, lines=lines, ao=ao, which=which, ri=ri, ci=ci)
    if len(_WG) > 3: _WG.clear()
    _WG[key] = g; return g


def well(media, d, vp=(540., 430.), sb_min=.62, trail=0.0, overlay=None):
    """media (1080x1350 RGB/RGBA) pushed back into a lit box of relative depth d (0..1). Returns RGB 1080x1350.
    The walls are lit by the back wall's own light (per-row / per-column spill profiles, inverse-square-ish falloff
    toward the rim, a hot bounce band at the back seam); glossy floor = the mirror image of his world (same depth as
    the back wall, so same scale, flipped below it), blurred and fading; faint gloss on the sides / ceiling.
    Walls are shaded at half resolution (soft by nature); the back wall, captions, AO and rim are full resolution."""
    if d <= .002:
        if overlay is None: return media.convert('RGB')
        m = media.convert('RGBA'); m.alpha_composite(overlay); return m.convert('RGB')
    q = 2
    sb = 1 - (1 - sb_min) * d
    VX, VY = vp
    bx0, bx1 = VX - VX * sb, VX + (MW - VX) * sb
    by0, by1 = VY - VY * sb, VY + (MH - VY) * sb
    m = m_plain = media.convert('RGB')
    bw, bh = int(round(bx1 - bx0)), int(round(by1 - by0))
    if overlay is not None:          # captions ride on the back wall and blur WITH it (no separate ghost copy)
        m = m.convert('RGBA'); m.alpha_composite(overlay); m = m.convert('RGB'); overlay = None
    back = m.resize((bw, bh), Image.BILINEAR, reducing_gap=2.0)
    back_plain = back if m is m_plain else m_plain.resize((bw, bh), Image.BILINEAR, reducing_gap=2.0)   # gloss: no text
    if trail > .004:     # falling away: true radial motion blur about the vanishing point (8 log-spaced samples:
        # the wall was 1..(1+trail) x bigger during the shutter) — smooth, no discrete ghost copies
        back = radial_blur(back, 1 + trail, ((VX - bx0), (VY - by0)))
    a = np.asarray(m_plain.resize((54, 68), Image.BILINEAR), np.float32)
    pL, pR = _prof(a[:, :7], 1, 7, 2.5), _prof(a[:, -7:], 1, 7, 2.5)            # (68, 3)
    pT, pB = _prof(a[:9], 0, 9, 2.5), _prof(a[-9:], 0, 9, 2.5)                  # (54, 3)
    glob = a.reshape(-1, 3).mean(0)
    G = _well_geom(sb, VX, VY, q); wh = G['which']
    spill = np.empty(wh.shape + (3,), np.float32)
    for k, (prof, idx) in enumerate([(pB, G['ci']), (pT, G['ci']), (pR, G['ri']), (pL, G['ri'])]):
        mk = wh == k; spill[mk] = prof[idx[mk]]
    spill = spill * .7 + glob * .3
    col = (np.array([7, 6, 13], np.float32) + spill * G['lit'][..., None] + G['lines'][..., None]) * G['ao'][..., None]
    # gloss: mirror images of his world across each seam (same depth as the back wall -> same scale), each cut to
    # its own wall
    hb = back_plain.resize((max(2, bw // q), max(2, bh // q)), Image.BILINEAR)
    bxq, byq, bwq, bhq = int(round(bx0 / q)), int(round(by0 / q)), hb.width, hb.height
    Hq, Wq = wh.shape
    acc = np.zeros((Hq, Wq, 3), np.float32); acc_a = np.zeros((Hq, Wq), np.float32)
    def gloss(img, x, y, a0, k, fade_axis):
        img = img.filter(ImageFilter.GaussianBlur(5 / q)); w_, h_ = img.size
        x0_, y0_, x1_, y1_ = max(0, x), max(0, y), min(Wq, x + w_), min(Hq, y + h_)
        if x1_ - x0_ < 2 or y1_ - y0_ < 2: return
        arr = np.asarray(img, np.float32)[y0_ - y:y1_ - y, x0_ - x:x1_ - x]
        if fade_axis in ('down', 'up'):
            g = np.linspace(1, 0, h_, dtype=np.float32) ** 1.6
            g = (g if fade_axis == 'down' else g[::-1])[y0_ - y:y1_ - y][:, None]
        else:
            g = np.linspace(1, 0, w_, dtype=np.float32) ** 1.6
            g = (g if fade_axis == 'right' else g[::-1])[x0_ - x:x1_ - x][None, :]
        al = g * a0 * (wh[y0_:y1_, x0_:x1_] == k)
        acc[y0_:y1_, x0_:x1_] += arr * al[..., None]; acc_a[y0_:y1_, x0_:x1_] += al
    fh = Hq - (byq + bhq)
    if fh > 3: gloss(hb.crop((0, max(0, bhq - fh), bwq, bhq)).transpose(Image.FLIP_TOP_BOTTOM), bxq, byq + bhq, .42, 0, 'down')
    if bxq > 3:
        ww = min(bxq, bwq)
        gloss(hb.crop((0, 0, ww, bhq)).transpose(Image.FLIP_LEFT_RIGHT), bxq - ww, byq, .14, 3, 'left')
        gloss(hb.crop((bwq - ww, 0, bwq, bhq)).transpose(Image.FLIP_LEFT_RIGHT), bxq + bwq, byq, .14, 2, 'right')
    if byq > 3:
        hh = min(byq, bhq); gloss(hb.crop((0, 0, bwq, hh)).transpose(Image.FLIP_TOP_BOTTOM), bxq, byq - hh, .10, 1, 'up')
    al = np.clip(acc_a, 0, 1)[..., None]
    col = col * (1 - al) + acc / np.maximum(acc_a[..., None], 1e-4) * al
    out = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((MW, MH), Image.BILINEAR).convert('RGBA')
    bxi, byi = int(round(bx0)), int(round(by0))
    out.paste(back, (bxi, byi))
    ao = C(('ao', bw, bh), lambda: _edge_ao(bw, bh))
    out.alpha_composite(ao, (bxi, byi))
    # the four corner seams of the box: soft AO crease + a hairline catch-light
    sm_ = Image.new('L', (MW // 2, MH // 2)); hl_ = Image.new('L', (MW, MH))
    ds, dh = ImageDraw.Draw(sm_), ImageDraw.Draw(hl_)
    for (fx_, fy_), (bx_, by_) in [((0, 0), (bx0, by0)), ((MW, 0), (bx1, by0)), ((MW, MH), (bx1, by1)), ((0, MH), (bx0, by1))]:
        ds.line([(fx_ / 2, fy_ / 2), (bx_ / 2, by_ / 2)], fill=255, width=5)
        dh.line([(fx_, fy_), (bx_, by_)], fill=60, width=2)
    crease = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); crease.putalpha(sm_.filter(ImageFilter.GaussianBlur(3)).resize((MW, MH), Image.BILINEAR).point(lambda v: int(v * .55)))
    out.alpha_composite(crease)
    lite = Image.new('RGBA', (MW, MH), (190, 175, 255, 0)); lite.putalpha(hl_); out.alpha_composite(lite)
    out.alpha_composite(C('rim', _rim))
    return out.convert('RGB')


def _edge_ao(w, h):
    a = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dmin = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    a = np.clip(1 - dmin / 26, 0, 1) ** 2 * .55
    im = Image.new('RGBA', (w, h), (4, 3, 10, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im


def _rim():
    im = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((1, 1, MW - 2, MH - 2), outline=(210, 200, 255, 70), width=2)
    sh = Image.new('L', (MW, MH)); ImageDraw.Draw(sh).rectangle((0, 0, MW - 1, MH - 1), outline=255, width=14)
    sh = sh.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .45))
    dark = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); dark.putalpha(sh)
    out = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); out.alpha_composite(dark); out.alpha_composite(im); return out


# ---------------------------------------------------------------- glass-tap ripple
def ripple(img, cx, cy, e, amp=9.0, speed=900., width=46., q=2, ay=1.0, hl_gain=70., r0=30., mask=None):
    """refraction rings expanding from (cx, cy) (ellipse squashed by ay for a tilted plane), e = seconds since the tap.
    A leading crest + a weaker second ring; bright caustic on the crest, a soft shadow in the trough.
    Computed at 1/q res inside the ring's bounding box only and composited ONLY where the wave is (the rest of the
    frame keeps its full-res pixels). `mask` (L, full size): where the glass is (never in the void)."""
    if e < 0 or e > .9: return img
    from scipy.ndimage import map_coordinates
    w, h = img.size; R = r0 + speed * e; Ro = R + 2.6 * width
    x0, x1 = max(0, int(cx - Ro)), min(w, int(cx + Ro) + 1); y0, y1 = max(0, int(cy - Ro * ay)), min(h, int(cy + Ro * ay) + 1)
    if x1 - x0 < 8 or y1 - y0 < 8: return img
    crop = img.crop((x0, y0, x1, y1)).convert('RGB'); cw, ch = crop.size; sw, sh = max(2, cw // q), max(2, ch // q)
    small = np.asarray(crop.resize((sw, sh), Image.BILINEAR), np.float32)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    fx, fy = cw / sw, ch / sh
    dx, dy = xx * fx - (cx - x0), (yy * fy - (cy - y0)) / ay; r = np.sqrt(dx * dx + dy * dy) + 1e-3
    env = min(1., e / .03) * math.exp(-e / .32)
    def ring(Rk, k):
        u = (r - Rk) / width
        return np.sin(u * math.pi) * np.exp(-(u / 1.3) ** 2) * k
    wave = (ring(R, 1.0) + ring(R * .6, .5) * (R * .6 > 2 * q)) * env
    disp = wave * amp
    sxp, syp = xx - dx / r * disp / fx, yy - dy * ay / r * disp / fy
    out = np.stack([map_coordinates(small[..., c], [syp, sxp], order=1, mode='nearest') for c in range(3)], -1)
    crest = np.clip(wave, 0, 1) ** 2; trough = np.clip(-wave, 0, 1) ** 2
    out = out + crest[..., None] * hl_gain * np.array([.88, .86, 1.0], np.float32) - trough[..., None] * hl_gain * .35
    res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).resize((cw, ch), Image.BILINEAR)
    wgt = Image.fromarray((np.clip(np.abs(wave) * 7, 0, 1) * 255).astype(np.uint8)).resize((cw, ch), Image.BILINEAR)
    if mask is not None: wgt = ImageChops.multiply(wgt, mask.crop((x0, y0, x1, y1)))
    o = img.copy(); o.paste(res if o.mode == 'RGB' else res.convert(o.mode), (x0, y0), wgt)
    return o


# ---------------------------------------------------------------- void / space background
def void_bg(h=H):
    """the purple depth void (h > H: a taller plate for camera parallax; same look, centred)."""
    def mk():
        yy, xx = np.mgrid[0:h, 0:W].astype(np.float32); yy = yy - (h - H) / 2
        base = np.array([9, 8, 15], np.float32)
        def glow(cx, cy, rx, ry, col, a):
            g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)); return g[..., None] * np.array(col, np.float32) * a
        img = base + glow(540, 760, 620, 900, (90, 70, 230), .30) + glow(900, 260, 420, 420, (154, 77, 255), .14) \
            + glow(140, 1500, 460, 420, (79, 107, 255), .12)
        img = img * (1 - .5 * np.clip(((xx - 540) / 950) ** 2 + ((yy - 900) / 1300) ** 2, 0, 1))[..., None]
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
        rng = np.random.default_rng(5); dust = Image.new('RGBA', (W, h), (0, 0, 0, 0)); d = ImageDraw.Draw(dust)
        for _ in range(int(60 * h / H)):
            x, y, r = rng.uniform(0, W), rng.uniform(0, h), rng.uniform(1.5, 7)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(190, 180, 255, int(rng.uniform(14, 60))))
        im.alpha_composite(dust.filter(ImageFilter.GaussianBlur(2.2)))
        return im
    return C(('void', h), mk)


def light_hit(fr, k, col=(196, 182, 255)):
    """a flash that reads as LIGHT (exposure push + highlight bloom), from the showcase."""
    rgb = fr.convert('RGB'); a = np.asarray(rgb, np.float32)
    sm = np.asarray(rgb.resize((W // 4, H // 4), Image.BILINEAR), np.float32)
    lum = sm.mean(2, keepdims=True); hb = sm * np.clip((lum - 80) / 110, 0, 1)
    bloom = np.asarray(Image.fromarray(hb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32)
    y = (a * (1 + 1.7 * k) + bloom * (2.4 * k) + np.array(col, np.float32) * (.20 * k)) / 255.
    y = np.where(y < .72, y, .72 + .28 * (1 - np.exp(-(y - .72) / .28)))
    return Image.fromarray(np.clip(y * 255, 0, 255).astype(np.uint8)).convert('RGBA')


# ---------------------------------------------------------------- captions (engine look, filtered by segment)
_PF = {}
def pages_fixed(fix):
    """E.PAGES with hand-measured onsets applied (same rules as engine._pages: order kept, t1 = next onset, page in/out),
    so the captions are on the measured words even before the integrator merges them into engine.WORD_FIX."""
    key = tuple(sorted(fix.items()))
    if key in _PF: return _PF[key]
    import copy
    pages = copy.deepcopy(E.PAGES); words = [w for p in pages for w in p['words']]
    for w in words:
        if (w['seg'], w['text']) in fix: w['t0'] = fix[(w['seg'], w['text'])]
    for k in range(len(words) - 2, -1, -1):
        a, b = words[k], words[k + 1]
        if a['seg'] == b['seg'] and a['t0'] > b['t0'] - .08: a['t0'] = b['t0'] - .08
    for k, w in enumerate(words[:-1]):
        if words[k + 1]['seg'] == w['seg']: w['t1'] = max(w['t0'] + .06, words[k + 1]['t0'])
    for j, p in enumerate(pages):
        nxt = pages[j + 1]['words'][0]['t0'] if j + 1 < len(pages) else E.DUR; last = p['words'][-1]['t1']
        p['a'] = p['words'][0]['t0'] - .04; p['z'] = nxt - .02 if nxt - last < .5 else last + .35
    _PF[key] = pages; return pages


SCRIM_COL = (7, 5, 14)
def cap_scrim(fr, boxes, alpha, padx=54, pady=34, blur=30, q=4):
    """soft dark scrim behind a caption line: the union of the revealed words' text boxes (screen px), padded, a
    pill shape blurred into a cloud (no visible edge), alpha <= 1. Drawn at 1/q res inside its own bbox only."""
    if alpha <= .01 or not boxes: return
    x0 = min(b[0] for b in boxes) - padx; x1 = max(b[2] for b in boxes) + padx
    y0 = min(b[1] for b in boxes) - pady; y1 = max(b[3] for b in boxes) + pady
    m = 3 * blur; X0, Y0 = int(max(0, x0 - m)), int(max(0, y0 - m)); X1, Y1 = int(min(fr.width, x1 + m)), int(min(fr.height, y1 + m))
    if X1 - X0 < 8 or Y1 - Y0 < 8: return
    sw, sh = max(2, (X1 - X0) // q), max(2, (Y1 - Y0) // q)
    mk = Image.new('L', (sw, sh)); r = (y1 - y0) / 2 / q
    ImageDraw.Draw(mk).rounded_rectangle(((x0 - X0) / q, (y0 - Y0) / q, (x1 - X0) / q, (y1 - Y0) / q), r, fill=int(255 * min(1., alpha)))
    mk = mk.filter(ImageFilter.GaussianBlur(blur / q)).resize((X1 - X0, Y1 - Y0), Image.BILINEAR)
    fr.paste(SCRIM_COL, (X0, Y0, X1, Y1), mk)


def draw_caps(fr, t, cy0, base, segs, x0=None, fix=None, cy_fn=None, scrim=0.0):
    """E.draw_captions restricted to the pages of `segs` (so a page never lingers across a cut into a new shot).
    fix: {(seg, WORD): onset} measured onsets; cy_fn(page_index_within_segs) -> centre y (per-page placement).
    scrim > 0: a soft dark scrim (that peak alpha) grows behind the revealed words so the line never fights busy
    pixels under it (fades in with the first word, out with the page)."""
    cx0 = fr.width / 2 if x0 is None else x0
    pages = pages_fixed(fix) if fix else E.PAGES
    n = -1
    for p in pages:
        if p['seg'] not in segs: continue
        n += 1
        if not (p['a'] <= t < p['z']): continue
        cy0_ = cy_fn(n) if cy_fn is not None else cy0
        if scrim > 0:
            boxes = []
            for w, sz, cx, cy in E._layout(p, base):
                if t < w['t0'] - .02: continue
                lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
                l_, t_, r_, b_ = E.font(sz).getbbox(w['text']); hw, hh = (r_ - l_) * s / 2, (b_ - t_) * s / 2
                boxes.append((cx0 + cx - hw, cy0_ + cy - hh, cx0 + cx + hw, cy0_ + cy + hh))
            fa = clamp((t - p['a']) / .14) * clamp((p['z'] - t) / .08)
            cap_scrim(fr, boxes, scrim * smooth(fa))
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = E.fade(img, lt / .05)
            if p['z'] - t < .06: img = E.fade(img, (p['z'] - t) / .06)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            E._paste(fr, dict(img=img, xy=(int(cx0 + cx - img.width / 2), int(cy0_ + cy - img.height / 2)), glass=0))


def zblur(img, amount, center=(W / 2, H / 2), n=5):
    """radial zoom blur for a layer only (chrome stays sharp): continuous streaks over magnifications 1 .. 1+amount*.2
    (16 log-spaced samples via recursive doubling — the old 5 discrete copies stepped visibly)."""
    if amount < .02: return img
    return radial_blur(img, 1 + amount * .05 * (n - 1), center, passes=6 if amount > 1 else 5).convert(img.mode)


def sheen(img, p, amp=.12):
    """a soft specular glare band sweeping diagonally across the phone glass (p 0..1)."""
    if p <= 0 or p >= 1 or amp <= .005: return img
    def mk():
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        return (xx / (W / 4)) * .55 + (yy / (H / 4)) * .45
    u = C('sheen_u', mk)
    c = lerp(-.25, 1.25, eio(p))
    band = np.exp(-((u - c) / .10) ** 2) * amp + np.exp(-((u - c + .13) / .02) ** 2) * amp * .5
    a = Image.fromarray((np.clip(band, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    hl = Image.new('RGBA', (W, H), (235, 232, 255, 0)); hl.putalpha(a)
    out = img.convert('RGBA'); out.alpha_composite(hl); return out
