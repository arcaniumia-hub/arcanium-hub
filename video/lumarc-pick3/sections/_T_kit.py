"""_T_kit — helpers + sprites for s06_pick_three (author T).  Read-only for other authors.

Display type with glyph masks + light sheen, glow / ring / glint sprites, motion smear, frosted brand glass, the brand
space (studio melted into LUMARC light), bokeh, god rays, the CTA UI (glass card, gradient "Send message" pill with a
generic chat bubble, phone row, sent chat bubble, touch indicator) and the strike-through bar.
Several helpers are copies (same look) of lumarc-ia/sections/_F_kit.py and lumarc-showcase/sections/s12_end.py.
"""
import math, re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E

W, H = E.W, E.H
clamp, back = E.clamp, E.back


def C(k, fn): return E.cached(('T',) + (k if isinstance(k, tuple) else (k,)), fn)
def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def eo(x, p=3): x = clamp(x); return 1 - (1 - x) ** p
def ei(x, p=2): x = clamp(x); return x ** p
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def bump(x): x = clamp(x); return math.sin(math.pi * x)
def dec(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def hr(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def shake(t, t0, amp, tau=.12, f=19., seed=0.):
    u = t - t0
    if u < 0 or u > tau * 7: return 0.0, 0.0
    k = amp * math.exp(-u / tau)
    return k * math.sin(2 * math.pi * f * u + seed), k * math.sin(2 * math.pi * f * 1.37 * u + 1.7 + seed)


def scale_im(im, s, lanczos=False):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.LANCZOS if lanczos else Image.BILINEAR)


def fade(im, k):
    k = clamp(k)
    if k >= .999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * k))); return im


def paste(base, im, x, y, center=True, alpha=1.0):
    """alpha-composite im onto base (clipped), centre (x, y) by default."""
    if im is None or alpha <= .01: return
    if alpha < .999: im = fade(im, alpha)
    if center: x, y = x - im.width / 2, y - im.height / 2
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, -x), max(0, -y); x1, y1 = min(im.width, base.width - x), min(im.height, base.height - y)
    if x1 <= x0 or y1 <= y0: return
    if x0 or y0 or x1 < im.width or y1 < im.height: im = im.crop((x0, y0, x1, y1))
    base.alpha_composite(im, (x + x0, y + y0))


def smear(img, L, axis=0):
    """box motion blur of length L px along axis (0 = vertical, 1 = horizontal), edge-clamped."""
    if abs(L) < 1.5: return img
    from scipy.ndimage import uniform_filter1d
    mode = img.mode; a = np.asarray(img, np.float32)
    a = uniform_filter1d(a, int(round(abs(L))) + 1, axis=axis, mode='nearest')
    return Image.fromarray(np.clip(a + .5, 0, 255).astype(np.uint8), mode)


def shift_v(fr, dy, blur=0.0):
    """the whole frame translated vertically by dy px (edges clamped) + vertical motion blur (whip pan)."""
    dy = int(round(dy))
    if dy == 0 and blur < 1.5: return fr
    a = np.asarray(fr.convert('RGB'))
    if dy > 0: a = np.concatenate([np.repeat(a[:1], dy, 0), a[:-dy]], 0)
    elif dy < 0: a = np.concatenate([a[-dy:], np.repeat(a[-1:], -dy, 0)], 0)
    out = Image.fromarray(np.ascontiguousarray(a))
    if blur >= 1.5:   # blur at half res (cheap), it is a whip
        sm = out.resize((W // 2, H // 2), Image.BILINEAR); sm = smear(sm, blur / 2, 0); out = sm.resize((W, H), Image.BILINEAR)
    return out.convert('RGBA')


def add_field(fr, field, k, x0=0, y0=0):
    """additive float32 light field (h, w, 3) at offset (x0, y0)."""
    if k <= .01: return fr
    a = np.asarray(fr.convert('RGB'), np.float32); h, w = field.shape[:2]
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe > xs and ye > ys: a[ys:ye, xs:xe] += field[ys - y0:ye - y0, xs - x0:xe - x0] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


# ================================================================================================ type
def display(text, size, wght=900, style='grad', glow=.5, shadow=.8, track=0, cols=None):
    """display word/line: LUMARC gradient light or a colour, soft violet glow + shadow -> (RGBA, glyph mask 0..1)."""
    def mk():
        f = E.font(size, wght); pad = int(size * .42)
        adv = [f.getlength(ch) for ch in text]
        tw = int(sum(adv) + track * (len(text) - 1)) if track else int(f.getbbox(text)[2] - f.getbbox(text)[0])
        _, t, _, b = f.getbbox(text + 'H')
        w, h = tw + 2 * pad, (b - t) + 2 * pad
        m = Image.new('L', (w, h)); d = ImageDraw.Draw(m)
        if track:
            x = pad
            for ch, a in zip(text, adv): d.text((x, pad - t), ch, font=f, fill=255); x += a + track
        else:
            d.text((pad - f.getbbox(text)[0], pad - t), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        if shadow:
            sh = Image.new('RGBA', (w, h), (4, 2, 14, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(size * .09)).point(lambda v: int(v * shadow)))
            out.alpha_composite(sh, (0, int(size * .04)))
        if style == 'grad':
            g = E.gradient(w, h, cols or E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
            if glow:
                gl = Image.new('RGBA', (w, h), (120, 90, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(size * .16)).point(lambda v: int(min(255, v * glow))))
                out.alpha_composite(gl)
            out.alpha_composite(g)
        else:
            col = E.WHITE if style == 'white' else style
            if glow:
                gl = Image.new('RGBA', (w, h), (140, 120, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(size * .16)).point(lambda v: int(min(255, v * glow * .6))))
                out.alpha_composite(gl)
            c = Image.new('RGBA', (w, h), col + (0,)); c.putalpha(m); out.alpha_composite(c)
        return out, np.asarray(m, np.float32) / 255
    return C(('disp', text, size, wght, str(style), glow, shadow, track, str(cols)), mk)


def sheen(img, k, mask, half=30, strength=.55, slope=.35):
    """narrow diagonal light band that brightens ONLY the glyphs (mask = bare glyph alpha, same size as img)."""
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


def wipe(img, k, mask=None, soft=40, edge=.8):
    """reveal img left -> right (k 0..1) with a bright light edge riding the reveal (on the glyphs only)."""
    if k >= 1: return img
    if k <= 0: return None
    xs = np.arange(img.width, dtype=np.float32)
    wv = (img.width + soft) * eo(k, 2.2)
    m = np.clip((wv - xs) / soft, 0, 1)[None, :]
    A = np.asarray(img, np.float32).copy()
    A[..., 3] *= m
    if mask is not None:
        e = np.exp(-((xs - wv + soft * .5) / 14) ** 2)[None, :] * mask
        A[..., :3] += (255 - A[..., :3]) * e[..., None] * edge
        A[..., 3] = np.maximum(A[..., 3], e * 255 * (1 - k))
    return Image.fromarray(np.clip(A, 0, 255).astype(np.uint8), 'RGBA')


# ================================================================================================ light sprites
def glow_sprite(w, h, col, blur, a=1.0):
    def mk():
        pad = int(blur * 2.5); m = Image.new('L', (int(w) + 2 * pad, int(h) + 2 * pad))
        ImageDraw.Draw(m).ellipse((pad, pad, pad + w, pad + h), fill=int(255 * a))
        im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); return im
    return C(('glow', int(w), int(h), col, blur, a), mk)


def ring_sprite(R, w=3.0, a=1.0, col=(250, 250, 255)):
    def mk():
        S = int(2 * R + 4 * w + 8); yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); d = np.hypot(xx - S / 2, yy - S / 2)
        al = np.exp(-((d - R) / w) ** 2) * a
        return Image.fromarray(np.dstack([np.full((S, S, 3), col, np.float32), al * 255]).astype(np.uint8), 'RGBA')
    return C(('ring', int(R), w, a, col), mk)


def glint(size=64):
    """anamorphic 4-ray glint (white RGBA)."""
    def mk():
        S = size; yy, xx = np.mgrid[-S:S + 1, -S:S + 1].astype(np.float32) / S
        r = np.hypot(xx, yy) + 1e-6
        a = np.exp(-(r / .07) ** 2) + .35 * np.exp(-(r / .22) ** 2)
        a += np.exp(-(np.abs(yy) / (.012 + .02 * np.abs(xx))) ** 2) * np.clip(1 - np.abs(xx), 0, 1) ** 2
        a += .6 * np.exp(-(np.abs(xx) / (.012 + .02 * np.abs(yy))) ** 2) * np.clip(1 - np.abs(yy) / .6, 0, 1) ** 2
        im = Image.new('RGBA', (2 * S + 1, 2 * S + 1), (255, 255, 255, 0)); im.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)))
        return im
    return C(('glint', size), mk)


def rays_field(R=1150, n=26, seed=3):
    """god rays: soft radial light streaks (float32 2R x 2R x 3, centre at (R, R)) computed at 1/4 res."""
    def mk():
        s = 4; N = 2 * R // s
        yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) * s - R
        ang = np.arctan2(yy, xx); r = np.hypot(xx, yy) + 1
        rng = np.random.default_rng(seed); acc = np.zeros_like(r)
        for i in range(n):
            a0 = rng.uniform(-math.pi, math.pi); wd = rng.uniform(.012, .05); g = rng.uniform(.35, 1.0)
            d = np.angle(np.exp(1j * (ang - a0)))
            acc += g * np.exp(-(d / wd) ** 2)
        fall = np.exp(-r / (R * .42)) * np.clip((r - 60) / 140, 0, 1)
        v = np.clip(acc * fall, 0, 1.4)
        hue = np.clip((xx + R) / (2 * R), 0, 1)[..., None]
        col = np.array([110, 120, 255], np.float32) * (1 - hue) + np.array([190, 120, 255], np.float32) * hue
        f = v[..., None] * col
        im = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).resize((2 * R, 2 * R), Image.BILINEAR)
        return np.asarray(im, np.float32)
    return C(('rays', R, n, seed), mk)


def bokeh(r, col):
    def mk():
        s = int(r * 2 + 8); y, x = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
        d = np.sqrt(x * x + y * y) / r
        a = np.clip((1.0 - d) / .35, 0, 1) ** 1.5 * (.7 + .3 * np.clip((d - .5) / .4, 0, 1))
        im = Image.new('RGBA', (s, s), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.filter(ImageFilter.GaussianBlur(r * .08 + .8))
    return C(('bokeh', r, col), mk)


# ================================================================================================ backgrounds
def bg_soft():
    """the studio plate, defocused + dimmed (depth of field: the glass UI pops, he stays sharp)."""
    def mk():
        im = E.studio().filter(ImageFilter.GaussianBlur(6))
        return Image.blend(im, Image.new('RGB', im.size, (8, 7, 14)), .30)
    return C('bg_soft', mk)


def _vig_small():
    def mk():
        h, w = H // 8, W // 8
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        return (1 - .72 * np.clip(((x - w / 2) / (w * .7)) ** 2 + ((y - h * .42) / (h * .6)) ** 2 - .10, 0, 1)).astype(np.float32)
    return C('vig8', mk)


def frost(fr, k, dark=1.0):
    """brand glass over the frame: heavy blur graded into a deep-violet duotone (crushed blacks, strong vignette).
    k 0..1 = the glass rising; the blur radius ramps with k (computed at 1/8 res, upscaled)."""
    if k <= .02: return fr
    ke = eo(k)
    small = fr.convert('RGB').resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(8 * (.3 + .7 * ke)))
    a = np.asarray(small, np.float32) / 255
    L = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    L = np.clip((L - .05) * 1.25, 0, 1) ** 1.35
    c0 = np.array([9, 8, 16], np.float32); c1 = np.array([34, 24, 88], np.float32); c2 = np.array([110, 90, 220], np.float32)
    col = c0 + (c1 - c0) * np.clip(L * 2.4, 0, 1)[..., None] + (c2 - c1) * (np.clip(L * 2.4 - 1, 0, 1) * .5)[..., None]
    col *= (_vig_small() * dark + (1 - dark))[..., None]
    if k < 1: col = a * 255 + (col - a * 255) * ke
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert('RGBA')


def brand_plate():
    """the studio melted into the LUMARC brand space: deep defocus, violet duotone, crushed blacks, halo light."""
    def mk():
        im = E.studio().resize((W // 6, H // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BICUBIC)
        a = np.asarray(im, np.float32) / 255
        L = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
        L = np.clip((L - .04) * 1.3, 0, 1) ** 1.3
        c0 = np.array([9, 8, 16], np.float32); c1 = np.array([30, 21, 78], np.float32); c2 = np.array([104, 86, 206], np.float32)
        col = c0 + (c1 - c0) * np.clip(L * 2.3, 0, 1)[..., None] + (c2 - c1) * (np.clip(L * 2.3 - 1, 0, 1) * .45)[..., None]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        top = np.exp(-(((xx - 540) / 620) ** 2 + ((yy - 560) / 360) ** 2))[..., None] * np.array([40, 30, 108], np.float32)
        halo = np.exp(-(((xx - 540) / 460) ** 2 + ((yy - 1150) / 420) ** 2))[..., None] * np.array([26, 18, 70], np.float32)
        col = col * .8 + top + halo
        v = 1 - .62 * np.clip(((xx - 540) / 760) ** 2 + ((yy - 860) / 1150) ** 2 - .08, 0, 1)
        return Image.fromarray(np.clip(col * v[..., None], 0, 255).astype(np.uint8))
    return C('bplate', mk)


def floor_shade():
    """dark foreground gradient over the frame bottom (hides the scaled take's frame edges; Meta's UI sits there)."""
    def mk():
        y = np.clip((np.arange(H, dtype=np.float32) - 1420) / 500, 0, 1) ** 1.4 * .9
        a = np.repeat(y[:, None], W, 1)
        x = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
        a = np.clip(a * (.75 + .5 * np.abs(x) ** 2), 0, .95)
        im = Image.new('RGBA', (W, H), (6, 5, 12, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return C('floor', mk)


# ================================================================================================ icons
def _ss(size, fn, col=E.WHITE):
    S = 4; m = Image.new('L', (size * S, size * S)); fn(ImageDraw.Draw(m), size * S)
    m = m.resize((size, size), Image.LANCZOS)
    im = Image.new('RGBA', (size, size), col + (0,)); im.putalpha(m); return im


_PHONE_PATH = ("M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83"
               "l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99"
               " 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z")


def path_pts(p, n=14):
    toks = re.findall(r'[MmLlHhVvCcZz]|-?\d*\.?\d+(?:e-?\d+)?', p)
    pts = []; i = 0; cur = (0., 0.); cmd = None; start = (0., 0.)
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]): cmd = toks[i]; i += 1
        if cmd in 'Zz': pts.append(start); cur = start; continue
        if cmd == 'M': cur = (num(), num()); start = cur; pts.append(cur); cmd = 'L'
        elif cmd == 'm': cur = (cur[0] + num(), cur[1] + num()); start = cur; pts.append(cur); cmd = 'l'
        elif cmd == 'L': cur = (num(), num()); pts.append(cur)
        elif cmd == 'l': cur = (cur[0] + num(), cur[1] + num()); pts.append(cur)
        elif cmd == 'H': cur = (num(), cur[1]); pts.append(cur)
        elif cmd == 'h': cur = (cur[0] + num(), cur[1]); pts.append(cur)
        elif cmd == 'V': cur = (cur[0], num()); pts.append(cur)
        elif cmd == 'v': cur = (cur[0], cur[1] + num()); pts.append(cur)
        elif cmd in 'Cc':
            a = [num() for _ in range(6)]
            if cmd == 'c': a = [a[0] + cur[0], a[1] + cur[1], a[2] + cur[0], a[3] + cur[1], a[4] + cur[0], a[5] + cur[1]]
            p0, p1, p2, p3 = cur, (a[0], a[1]), (a[2], a[3]), (a[4], a[5])
            for k in range(1, n + 1):
                u = k / n; v = 1 - u
                pts.append((v ** 3 * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u ** 3 * p3[0],
                            v ** 3 * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u ** 3 * p3[1]))
            cur = p3
    return pts


def icon_phone(size=96, col=E.WHITE):
    def mk():
        pts = path_pts(_PHONE_PATH)
        def f(d, s): d.polygon([(x / 24 * s, y / 24 * s) for x, y in pts], fill=255)
        return _ss(size, f, col)
    return C(('iphone', size, col), mk)


def icon_chat(size=80, col=E.WHITE, dots=True):
    """generic chat bubble: rounded bubble + tail (bottom-left), three dots cut out."""
    def mk():
        def f(d, s):
            d.rounded_rectangle((s * .06, s * .10, s * .94, s * .74), s * .26, fill=255)
            d.polygon([(s * .20, s * .62), (s * .44, s * .70), (s * .14, s * .92)], fill=255)
            if dots:
                for i in range(3):
                    cx = s * (.31 + .19 * i); cy = s * .42; r = s * .065
                    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
        return _ss(size, f, col)
    return C(('ichat', size, col, dots), mk)


def icon_check2(size=44, col=E.WHITE):
    """double tick (delivered)."""
    def mk():
        def f(d, s):
            w = int(s * .10)
            for ox in (0, s * .26):
                d.line([(s * .06 + ox, s * .52), (s * .24 + ox, s * .72), (s * .56 + ox, s * .30)], fill=255, width=w, joint='curve')
        return _ss(size, f, col)
    return C(('ichk2', size, col), mk)


# ================================================================================================ CTA UI
CARD_W = 930
BTN_W, BTN_H = 820, 156


def card_panel(h):
    """frosted dark-glass card CARD_W x h (h quantised to 4 px so growing it re-uses sprites)."""
    h = max(40, int(h) // 4 * 4)
    def mk():
        p = E.glass_panel(CARD_W, h, 54, tint=(150, 140, 255), alpha=.11, border=.5)
        dk = Image.new('RGBA', p.size, (10, 8, 22, 0)); m = Image.new('L', p.size)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W - 1, h - 1), 54, fill=120); dk.putalpha(m)
        out = Image.new('RGBA', p.size, (0, 0, 0, 0)); out.alpha_composite(dk); out.alpha_composite(p)
        return out
    return C(('card', h), mk)


def card_shadow(h):
    h = max(40, int(h) // 4 * 4)
    def mk():
        a = Image.new('L', (CARD_W + 200, h + 200)); ImageDraw.Draw(a).rounded_rectangle((100, 100, 100 + CARD_W, 100 + h), 54, fill=255)
        g = Image.new('RGBA', a.size, (4, 2, 10, 0)); g.putalpha(a.filter(ImageFilter.GaussianBlur(36)).point(lambda v: int(v * .55)))
        return g
    return C(('cshadow', h), mk)


def button(lit=0.0):
    """the gradient 'Send message' pill (generic chat bubble).  -> (RGBA, label glyph mask, label box (x0, y0))"""
    def mk():
        w, h = BTN_W, BTN_H; pad = 40
        im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        m = Image.new('L', im.size); ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + w, pad + h), h // 2, fill=255)
        sh = Image.new('RGBA', im.size, (20, 8, 60, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .7)))
        im.alpha_composite(sh, (0, 10))
        body = E.gradient(im.width, im.height, E.GRAD).convert('RGBA'); body.putalpha(m); im.alpha_composite(body)
        # top gloss + inner rim
        g = np.zeros((im.height, im.width), np.float32)
        yy = np.arange(im.height, dtype=np.float32)[:, None]
        g[:] = np.clip(1 - (yy - pad) / (h * .55), 0, 1) ** 2 * .22
        gl = Image.new('RGBA', im.size, (255, 255, 255, 0)); gl.putalpha(Image.fromarray((g * np.asarray(m, np.float32)).astype(np.uint8)))
        im.alpha_composite(gl)
        rim = Image.new('L', im.size); ImageDraw.Draw(rim).rounded_rectangle((pad + 1, pad + 1, pad + w - 2, pad + h - 2), h // 2, outline=255, width=2)
        rr = Image.new('RGBA', im.size, (255, 255, 255, 0)); rr.putalpha(rim.point(lambda v: int(v * .35))); im.alpha_composite(rr)
        # icon + label
        ic = icon_chat(78); f = E.font(64, 700); text = 'Send message'
        l, t, r, b = f.getbbox(text); _, tc, _, bc = f.getbbox('Sm')
        tw = r - l; gap = 26; tot = ic.width + gap + tw; x0 = pad + (w - tot) / 2
        im.alpha_composite(ic, (int(x0), int(pad + h / 2 - ic.height / 2 + 3)))
        lm = Image.new('L', im.size); ImageDraw.Draw(lm).text((x0 + ic.width + gap - l, pad + h / 2 - (tc + bc) / 2), text, font=f, fill=255)
        lab = Image.new('RGBA', im.size, E.WHITE + (0,)); lab.putalpha(lm)
        ls = Image.new('RGBA', im.size, (20, 6, 60, 0)); ls.putalpha(lm.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * .5)))
        im.alpha_composite(ls, (0, 2)); im.alpha_composite(lab)
        mask = np.asarray(lm, np.float32) / 255
        icm = np.zeros_like(mask); ica = np.asarray(ic.getchannel('A'), np.float32) / 255
        icm[int(pad + h / 2 - ic.height / 2 + 3):int(pad + h / 2 - ic.height / 2 + 3) + ic.height, int(x0):int(x0) + ic.width] = ica
        return im, mask, icm, (x0 + ic.width + gap, x0 + ic.width + gap + tw)
    return C('button', mk)


def button_glow():
    def mk():
        a = Image.new('L', (BTN_W + 260, BTN_H + 260)); ImageDraw.Draw(a).rounded_rectangle((130, 130, 130 + BTN_W, 130 + BTN_H), BTN_H // 2, fill=255)
        g = Image.new('RGBA', a.size, (110, 80, 255, 0)); g.putalpha(a.filter(ImageFilter.GaussianBlur(44)).point(lambda v: int(v * .8)))
        return g
    return C('bglow', mk)


def touch_dot(r=46):
    """the touch indicator: soft white fingertip disc with a bright rim (screen-recording style)."""
    def mk():
        S = int(r * 2 + 40); yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); d = np.hypot(xx - S / 2, yy - S / 2) / r
        a = np.clip(1 - d, 0, 1) ** .35 * .42 + np.exp(-((d - .97) / .08) ** 2) * .55 + np.exp(-(np.clip(d - 1, 0, None) / .25) ** 2) * .12 * (d > 1)
        im = Image.fromarray(np.dstack([np.full((S, S, 3), 255, np.float32), np.clip(a, 0, 1) * 255]).astype(np.uint8), 'RGBA')
        return im
    return C(('touch', r), mk)


def sent_bubble():
    """a SENT chat bubble (gradient, tail bottom-right): 'Hi! I want all three.' + double tick."""
    def mk():
        f = E.font(50, 600); text = 'Hi! I want all three.'
        l, t, r, b = f.getbbox(text); _, tc, _, bc = f.getbbox('Hg')
        tw = r - l; w = tw + 64 + 56; h = 112; pad = 30
        im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad + 14), (0, 0, 0, 0))
        m = Image.new('L', im.size); d = ImageDraw.Draw(m)
        d.rounded_rectangle((pad, pad, pad + w, pad + h), 44, fill=255)
        d.polygon([(pad + w - 46, pad + h - 30), (pad + w + 10, pad + h + 12), (pad + w - 6, pad + h - 46)], fill=255)
        sh = Image.new('RGBA', im.size, (10, 4, 30, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .6)))
        im.alpha_composite(sh, (0, 8))
        body = E.gradient(im.width, im.height, [(96, 120, 255), (120, 98, 255), (168, 92, 255)]).convert('RGBA'); body.putalpha(m); im.alpha_composite(body)
        tl = Image.new('L', im.size); ImageDraw.Draw(tl).text((pad + 34 - l, pad + h / 2 - (tc + bc) / 2 - 2), text, font=f, fill=255)
        tx = Image.new('RGBA', im.size, E.WHITE + (0,)); tx.putalpha(tl); im.alpha_composite(tx)
        ck = icon_check2(40, (225, 225, 255)); im.alpha_composite(ck, (pad + w - 30 - ck.width + 8, pad + h - ck.height - 8))
        return im
    return C('sent', mk)


PHONE_SIZE = 90


def phone_row():
    """the phone row: gradient badge with a handset (drawn separately so it can ring) + the number -> parts."""
    def mk():
        from sections import _shared as SH
        num, nm = display(SH.PHONE, PHONE_SIZE, 800, 'white', glow=.35, shadow=.6)
        b = 132; disc = Image.new('L', (b * 3, b * 3)); ImageDraw.Draw(disc).ellipse((0, 0, b * 3 - 1, b * 3 - 1), fill=255)
        disc = disc.resize((b, b), Image.LANCZOS)
        badge = E.gradient(b, b, E.GRAD).convert('RGBA'); badge.putalpha(disc)
        hl = Image.new('RGBA', (b, b), (255, 255, 255, 0)); g = np.clip(1 - np.arange(b, dtype=np.float32) / (b * .6), 0, 1)[:, None] ** 2 * .25
        hl.putalpha(Image.fromarray((np.asarray(disc, np.float32) * g).astype(np.uint8))); badge.alpha_composite(hl)
        return num, nm, badge, icon_phone(70)
    return C('phone_row', mk)


def underline(w, h=8):
    def mk():
        u = E.gradient(max(2, int(w)), h, E.GRAD_LIGHT).convert('RGBA'); return E.rounded(u, h // 2)
    return C(('uline', int(w), h), mk)


def bracket(size=46, w=7):
    """a viewfinder corner (top-left orientation, white)."""
    def mk():
        def f(d, s):
            lw = int(s * w / size)
            d.line([(lw / 2, s), (lw / 2, lw / 2), (s, lw / 2)], fill=255, width=lw, joint='curve')
        return _ss(size, f, E.WHITE)
    return C(('brk', size, w), mk)


# ================================================================================================ strike-through bar
def strike_bar(L, th=16):
    """glowing strike bar of length L: white-hot core + LUMARC gradient + violet glow (RGBA, centred, horizontal)."""
    L = max(4, int(L) // 4 * 4)
    def mk():
        pad = 40; w, h = L + 2 * pad, th + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + L, pad + th), th // 2, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        gl = Image.new('RGBA', (w, h), (120, 80, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(min(255, v * 1.4))))
        out.alpha_composite(gl)
        sh = Image.new('RGBA', (w, h), (6, 2, 20, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * .6)))
        out.alpha_composite(sh, (0, 4))
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m); out.alpha_composite(g)
        core = Image.new('L', (w, h)); ImageDraw.Draw(core).rounded_rectangle((pad + 6, pad + th * .32, pad + L - 6, pad + th * .62), 3, fill=255)
        c = Image.new('RGBA', (w, h), (255, 255, 255, 0)); c.putalpha(core.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: int(v * .85)))
        out.alpha_composite(c)
        return out
    return C(('strike', L, th), mk)
