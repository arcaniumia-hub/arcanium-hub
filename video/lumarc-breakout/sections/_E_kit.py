"""Private helpers for s09_lumarc + s10_cta (author E). Not a section (the loader only matches sNN_*.py).

Adapted from ../lumarc-showcase (s11 comment row / s12 end card: sheen, frost, space, bokeh, slices) plus a few small
3-D / compositing utilities. Everything is cached or a pure function of the arguments.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

W, H = E.W, E.H
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back


def C(k, fn): return E.cached(('E',) + (k if isinstance(k, tuple) else (k,)), fn)
def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def expo_in(x):
    x = clamp(x); return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def kick(x, tau=.12): return 0.0 if x < 0 else math.exp(-x / tau)
def bump(x, a, b):
    """0 -> 1 -> 0 over [a, b] (sin)."""
    if x <= a or x >= b: return 0.0
    return math.sin(math.pi * (x - a) / (b - a))
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def scale_im(im, s, lanczos=False):
    if abs(s - 1) < .005: return im
    return im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.LANCZOS if lanczos else Image.BILINEAR)


# ---------------------------------------------------------------- type
def txt(s, size, wght, col, pad=2):
    def mk():
        f = E.font(size, wght); l, t, r, b = f.getbbox(s)
        im = Image.new('RGBA', (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0)); ImageDraw.Draw(im).text((pad - l, pad - t), s, font=f, fill=col)
        return im
    return C(('txt', s, size, wght, col, pad), mk)


def pop_words(ctx, t, words, a, z, y=1440, base=92, maxw=860):
    """voice-synced caption line in the engine's style (word pop, back-ease, 1.06 punch while spoken).
    words = [(TEXT, t0, 'white'|'grad'), ...]; visible on [a, z)."""
    if not a <= t < z: return
    def measure(b):
        ws = []
        for w, _, st in words:
            l, tp, r, bb = E.font(int(b * (1.0 if st == 'white' else 1.1))).getbbox(w); ws.append(r - l)
        return ws, sum(ws) + b * .34 * (len(words) - 1)
    widths, tot = measure(base)
    if tot > maxw:
        base = int(base * maxw / tot); widths, tot = measure(base)
    gap = base * .34; x = W / 2 - tot / 2
    for (w, t0, st), ww in zip(words, widths):
        if t >= t0 - .02:
            im = E.word_img(w, int(base * (1.0 if st == 'white' else 1.1)), st)[0]
            lt = t - t0 + .02; s = (.72 + .28 * back(lt / .16)) * (1.05 if .05 < lt < .28 else 1)
            al = clamp((lt + .02) / .05) * clamp((z - t) / .06)
            ctx.add('screen', scale_im(im, s), x + ww / 2, y, alpha=al)
        x += ww + gap


# ---------------------------------------------------------------- the founder (keyed plate) for light passes
def film_of(ctx):
    for c in (ctx.compose.__closure__ or ()):
        v = c.cell_contents
        if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    return None


def avatar_rgba(ctx):
    F = film_of(ctx)
    return None if F is None else F.av.frame(ctx.t)


def top_light(ctx, col, k, y0=560, y1=1050, rim=1.0, broad=.25, d=10):
    """light from above (the logo / a flash) falling on his head and shoulders, added as a 'front' layer:
    a rim on every upward-facing edge of his silhouette (hair, shoulders) + a weak broad wash, only where he is."""
    if k <= .01: return
    av = avatar_rgba(ctx)
    if av is None: return
    from scipy.ndimage import gaussian_filter
    a = np.asarray(av.getchannel('A'), np.float32)[y0:y1] / 255
    up = np.zeros_like(a); up[d:] = a[:-d]
    e = gaussian_filter(np.clip(a - up, 0, 1), 3.0) * a
    ramp = C(('tl_ramp', y0, y1), lambda: (np.clip((y1 - np.arange(y0, y1, dtype=np.float32)) / (y1 - y0), 0, 1) ** 1.8)[:, None])
    v = (e * rim * 1.6 + a * ramp * broad) * k
    im = Image.new('RGBA', (W, y1 - y0), col + (0,)); im.putalpha(Image.fromarray(np.clip(v * 255, 0, 255).astype(np.uint8)))
    ctx.add('front', im, 0, y0, center=False)


# ---------------------------------------------------------------- light / glass helpers
def radial(w, h, col, power=2.0, alpha=1.0):
    def mk():
        y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]; x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
        a = np.clip(1 - np.sqrt(x * x + y * y), 0, 1) ** power * alpha
        im = Image.new('RGBA', (w, h), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return C(('radial', w, h, col, power, alpha), mk)


def add_light(img, field, k, x0=0, y0=0):
    """additive light: img (RGBA/RGB, full frame) += field (float32 hxwx3) * k at offset (x0, y0)."""
    if k <= .01: return img
    a = np.asarray(img.convert('RGB'), np.float32)
    h, w = field.shape[:2]
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(img.width, x0 + w), min(img.height, y0 + h)
    if xe > xs and ye > ys:
        a[ys:ye, xs:xe] += field[ys - y0:ye - y0, xs - x0:xe - x0] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def add_rgba_light(base, im, x, y, k=1.0):
    """additive composite of an RGBA sprite (rgb * alpha * k) onto base (RGBA, in place-ish; returns new)."""
    if k <= .01: return base
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(base.width, x + im.width), min(base.height, y + im.height)
    if x1 <= x0 or y1 <= y0: return base
    s = np.asarray(im.crop((x0 - x, y0 - y, x1 - x, y1 - y)), np.float32)
    b = np.asarray(base.crop((x0, y0, x1, y1)).convert('RGB'), np.float32)
    b = b + s[..., :3] * (s[..., 3:4] / 255) * k
    out = base.copy(); out.paste(Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)).convert('RGBA'), (x0, y0)); return out


def sheen(img, k, mask, half=30, strength=.55, slope=.35):
    """narrow diagonal light band that brightens only the ink (`mask` float32 HxW 0..1); never touches alpha."""
    if k <= 0 or k >= 1: return img
    w, h = img.size
    xx = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * slope
    c = lerp(-2 * half, w + h * slope + 2 * half, k)
    band = np.clip(1 - np.abs(xx - c) / half, 0, 1) ** 1.5 * strength
    cols = np.nonzero(band.max(0) > 0)[0]
    if len(cols) == 0: return img
    x0, x1 = int(cols[0]), int(cols[-1]) + 1
    A = np.asarray(img, np.float32)[:, x0:x1].copy()
    m = (band[:, x0:x1] * mask[:, x0:x1])[..., None]
    A[..., :3] += (255 - A[..., :3]) * m
    out = img.copy(); out.paste(Image.fromarray(A.astype(np.uint8), 'RGBA'), (x0, 0)); return out


def ink_mask(key, img, lo, hi):
    return C(('ink', key), lambda: np.clip((np.asarray(img.getchannel('A'), np.float32) - lo) / (hi - lo), 0, 1))


def glow_of(key, img, layers=((60, (100, 70, 255), 1.3), (18, (170, 150, 255), 1.0), (4, (235, 230, 255), .8)), pad=150):
    """coloured glow from an RGBA image's alpha (padded by `pad`)."""
    def mk():
        a = Image.new('L', (img.width + 2 * pad, img.height + 2 * pad)); a.paste(img.getchannel('A'), (pad, pad))
        out = Image.new('RGBA', a.size, (0, 0, 0, 0))
        for r, col, m in layers:
            g = Image.new('RGBA', a.size, col + (0,)); g.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, m=m: int(min(255, v * m * 1.6))))
            out.alpha_composite(g)
        return out
    return C(('glow', key), mk)


def vblur(im, L):
    """vertical box blur of length L px (uniform vertical motion over the shutter)."""
    n = int(round(L))
    if n < 2: return im
    a = np.asarray(im, np.float32); h = a.shape[0]
    padded = np.concatenate([np.repeat(a[:1], n // 2, 0), a, np.repeat(a[-1:], n - n // 2, 0)], 0)
    c = np.cumsum(padded, 0, dtype=np.float32); c = np.concatenate([np.zeros_like(c[:1]), c], 0)
    out = (c[n:n + h] - c[:h]) / n
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), im.mode)


def homography(src, dst):
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def rot3(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]); Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def card_quad(w, h, cx, cy, s, rx, ry, rz, f=2400.):
    """screen corners (TL TR BR BL) of a w x h card scaled s, centred at (cx, cy), rotated (degrees), pinhole f."""
    R = rot3(*(math.radians(v) for v in (rx, ry, rz))); pts = []
    for x, y in [(0, 0), (w, 0), (w, h), (0, h)]:
        X, Y, Z = R @ np.array([(x - w / 2) * s, (y - h / 2) * s, 0.])
        k = f / (f + Z); pts.append((cx + X * k, cy + Y * k))
    return pts


def warp(src, quad, pad=3):
    """projectively map RGBA `src` onto `quad` -> (img, x0, y0) (AA edges via a transparent pad; cheap mip)."""
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    x0, y0 = int(math.floor(min(xs))) - 2, int(math.floor(min(ys))) - 2
    x1, y1 = int(math.ceil(max(xs))) + 2, int(math.ceil(max(ys))) + 2
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    ew = max(math.hypot(quad[1][0] - quad[0][0], quad[1][1] - quad[0][1]), math.hypot(quad[2][0] - quad[3][0], quad[2][1] - quad[3][1]))
    sc = min(1.0, 1.5 * ew / src.width)
    if sc < .9: src = src.resize((max(4, int(src.width * sc)), max(4, int(src.height * sc))), Image.BILINEAR, reducing_gap=2.0)
    s2 = Image.new('RGBA', (src.width + 2 * pad, src.height + 2 * pad), (0, 0, 0, 0)); s2.paste(src, (pad, pad))
    sq = [(pad, pad), (s2.width - pad, pad), (s2.width - pad, s2.height - pad), (pad, s2.height - pad)]
    co = homography(sq, [(x - x0, y - y0) for x, y in quad])
    return s2.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BILINEAR), x0, y0


def smear(im, dx, dy, n):
    """directional motion blur of an RGBA sprite (premultiplied, centred). Returns (img, ox, oy) offset of the pad."""
    p = int(math.ceil(max(abs(dx), abs(dy)) / 2)) + 2
    big = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); big.paste(im, (p, p))
    a = np.asarray(big, np.float32); al = a[..., 3:4] / 255; pm = np.concatenate([a[..., :3] * al, al], 2)
    h, w = pm.shape[:2]; acc = np.zeros_like(pm); n = max(2, n)
    for i in range(n):
        s = i / (n - 1) - .5; ox, oy = int(round(dx * s)), int(round(dy * s))
        ys0, ys1 = max(0, -oy), min(h, h - oy); xs0, xs1 = max(0, -ox), min(w, w - ox)
        if ys1 <= ys0 or xs1 <= xs0: continue
        acc[ys0 + oy:ys1 + oy, xs0 + ox:xs1 + ox] += pm[ys0:ys1, xs0:xs1]
    acc /= n; al = acc[..., 3:4]
    rgb = np.where(al > 1e-4, acc[..., :3] / np.maximum(al, 1e-4), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al * 255, 0, 255)]).astype(np.uint8), 'RGBA'), p, p


def circle_mask(d, ss=4):
    m = Image.new('L', (d * ss, d * ss)); ImageDraw.Draw(m).ellipse((0, 0, d * ss - 1, d * ss - 1), fill=255)
    return m.resize((d, d), Image.LANCZOS)


def heart_shape(size, fill, outline=None, width=3):
    def mk():
        ss = 4; S = size * ss; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = []
        for i in range(120):
            a = i / 120 * 2 * math.pi
            x = 16 * math.sin(a) ** 3
            y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((S / 2 + x * S / 36, S * .47 - y * S / 36))
        if fill: d.polygon(pts, fill=fill)
        if outline: d.line(pts + [pts[0]], fill=outline, width=width * ss, joint='curve')
        return im.resize((size, size), Image.LANCZOS)
    return C(('heart', size, fill, outline, width), mk)
