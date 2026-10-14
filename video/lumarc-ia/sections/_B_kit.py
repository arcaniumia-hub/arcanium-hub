"""Kit for s03_sou_ia + s04_pincel (author B): voice-synced captions with measured onsets, face tracker on the keyed
plate, virtual camera helpers, glass chips, cursor, studio background at any zoom.  Read-only for other authors."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

W, H = E.W, E.H
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def sio(x):
    x = clamp(x); return .5 - .5 * math.cos(math.pi * x)
def C(k, fn): return E.cached(('B',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0


def scale_im(im, s):
    if abs(s - 1) < .01: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)


def fade(im, k):
    if k >= .999: return im
    a = np.asarray(im.getchannel('A'), np.float32) * max(0., k)
    out = im.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8))); return out


def shake(t, t0, amp, dur=.4, f1=91.0, f2=203.0):
    k = (t - t0) / dur
    if not 0 <= k < 1: return 0., 0.
    a = amp * (1 - k) ** 2
    return a * math.sin(t * f1 + 1.3) + .5 * a * math.sin(t * f2), a * .8 * math.cos(t * f1 * .9) + .4 * a * math.sin(t * f2 * .8 + .7)


# ---------------------------------------------------------------- the engine Film (keyed plate frames)
def film_of(ctx):
    for c in (ctx.compose.__closure__ or ()):
        v = c.cell_contents
        if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    return None


def av_frame(ctx, t):
    F = film_of(ctx)
    return F.av.frame(t) if F is not None else None


_FT = {}
FACE_DX = 18.0          # eye-midpoint x - skin centroid x (calibrated on the take at 19.1 s)


def face_track(av):
    """-> (fx, top): face centre x (between the eyes) and head top y, in take coordinates (avatar s=1, x=y=0).
    Measured on the keyed frame itself (half res): pure function of the frame."""
    if av is None: return 528., 600.
    if _FT.get('k') is av: return _FT['v']
    h2 = av.reduce(4)
    A = np.asarray(h2, np.int16)
    a = A[..., 3]
    rows = np.where(a.max(1) > 128)[0]
    top = float(rows[0] * 4) if len(rows) else 600.
    r0 = int(top / 4) + 38; r1 = int(top / 4) + 105
    sub = A[r0:r1]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    skin = (r > 95) & (r > g + 15) & (r > b + 20) & (sub[..., 3] > 200)
    xs = np.where(skin)[1]
    fx = float(xs.mean() * 4 + 2) + FACE_DX if len(xs) > 50 else 528.
    v = (fx, top); _FT.update(k=av, v=v); return v


# ---------------------------------------------------------------- captions (engine look, measured onsets)
def _layout(words, base, maxw):
    items = []
    for text, t0, em in words:
        sz = int(base * (1.2 if em else 1.0)); l, tp, r, b = E.font(sz).getbbox(text)
        if r - l > maxw: sz = int(sz * maxw / (r - l)); l, tp, r, b = E.font(sz).getbbox(text)
        items.append([text, t0, em, sz, r - l])
    lines, cur, cw = [], [], 0
    for it in items:
        add = it[4] + (base * .34 if cur else 0)
        if cur and cw + add > maxw: lines.append((cur, cw)); cur, cw = [], 0; add = it[4]
        cur.append(it); cw += add
    lines.append((cur, cw)); out = []; lh = base * 1.12; y0 = -(len(lines) - 1) * lh / 2
    for li, (ln, lw) in enumerate(lines):
        x = -lw / 2
        for it in ln: out.append((it, x + it[4] / 2, y0 + li * lh)); x += it[4] + base * .34
    return out


def caps(ctx, t, pages, y=1460, base=92, x=540, maxw=900, layer='screen', alpha=1.0, skip=()):
    """pages: [(a, z, [(TEXT, t0, emph), ...]), ...] -> word pops exactly like the engine captions."""
    for a, z, words in pages:
        if not (a <= t < z): continue
        L = _layout(words, base, maxw)
        nxt = [w[1] for w in words[1:]] + [z]
        for (it, cx, cy), t1 in zip(L, nxt):
            text, t0, em, sz, _ = it
            if text in skip or t < t0 - .02: continue
            lt = t - t0 + .02; s = .72 + .28 * back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            im = E.word_img(text, sz, 'grad' if em else 'white')[0]
            al = clamp(lt / .05) * clamp((z - t) / .06) * alpha
            ctx.add(layer, scale_im(im, s), x + cx, y + cy, alpha=al)


# ---------------------------------------------------------------- studio plate at any zoom / blur (half res)
def studio_at(z=1.0, anchor=(540., 760.), shift=(0., 0.), blur=0.0, dim=0.0):
    """the studio plate scaled by z around `anchor` (anchor lands at anchor+shift on screen), blurred (px at full res),
    dimmed — built at half resolution (out of focus anyway), upsampled once."""
    half = C('studio_half', lambda: E.studio().reduce(2))
    im = half
    if abs(z - 1) > 1e-4 or shift != (0., 0.):
        ax, ay = anchor[0] / 2, anchor[1] / 2; sx, sy = (anchor[0] + shift[0]) / 2, (anchor[1] + shift[1]) / 2; a = 1 / z
        im = im.transform(im.size, Image.AFFINE, (a, 0, ax - a * sx, 0, a, ay - a * sy), Image.BILINEAR)
    if blur > .3: im = im.filter(ImageFilter.GaussianBlur(blur / 2))
    if dim > .01: im = Image.blend(im, Image.new('RGB', im.size, (0, 0, 0)), dim)
    return im.resize((W, H), Image.BILINEAR)


# ---------------------------------------------------------------- camera mapping (engine compose_world maths)
def cam_map(cam):
    """world -> screen function for an engine camera dict (rot ignored)."""
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam.get('dx', 0), cam['y'] + cam.get('dy', 0)
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return lambda px, py: (X + (px - cam['x']) * z, Y + (py - cam['y']) * z), z


# ---------------------------------------------------------------- glass chips / UI
def dark_glass(w, h, r, alpha=.62, border=.32):
    return E.glass_panel(w, h, r, tint=(14, 14, 22), alpha=alpha, border=border)


def soft_shadow(w, h, r, blur=26, op=.55, pad=60):
    def mk():
        m = Image.new('L', (w + 2 * pad, h + 2 * pad)); ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=255)
        out = Image.new('RGBA', m.size, (0, 0, 0, 0)); out.putalpha(m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op)))
        return out
    return C(('shadow', w, h, r, blur, op, pad), mk)


def text_img(s, size, wght=700, col=E.WHITE, track=0):
    def mk():
        f = E.font(size, wght)
        if not track:
            l, tp, r, b = f.getbbox(s); im = Image.new('RGBA', (r - l + 8, b - tp + 8), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((4 - l, 4 - tp), s, font=f, fill=col); return im
        ws = [f.getlength(ch) for ch in s]; tot = int(sum(ws) + track * (len(s) - 1)) + 8
        l, tp, r, b = f.getbbox(s); im = Image.new('RGBA', (tot, b - tp + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
        for ch, w in zip(s, ws): d.text((x, 4 - tp), ch, font=f, fill=col); x += w + track
        return im
    return C(('txt', s, size, wght, col, track), mk)


def grad_text(s, size, wght=800, cols=None):
    def mk():
        f = E.font(size, wght); l, tp, r, b = f.getbbox(s)
        m = Image.new('L', (r - l + 8, b - tp + 8)); ImageDraw.Draw(m).text((4 - l, 4 - tp), s, font=f, fill=255)
        g = E.gradient(m.width, m.height, cols or E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m); return g
    return C(('gtxt', s, size, wght, str(cols)), mk)


def cursor_img(h=78):
    """classic arrow pointer: white fill, dark outline, soft shadow (RGBA; hotspot at (pad, pad))."""
    def mk():
        S = 4; pad = 30
        pts = [(0, 0), (0, 1.0), (.25, .78), (.42, 1.13), (.57, 1.06), (.41, .72), (.72, .72)]
        hh = h * S; P = [(pad * S + x * hh * .86, pad * S + y * hh * .86) for x, y in pts]
        size = (int(h * 1.0 + 2 * pad) * S, int(h * 1.1 + 2 * pad) * S)
        m_out = Image.new('L', size); ImageDraw.Draw(m_out).polygon(P, fill=255)
        m_out = m_out.filter(ImageFilter.MaxFilter(4 * 2 + 1))
        m_in = Image.new('L', size); ImageDraw.Draw(m_in).polygon(P, fill=255)
        m_in = m_in.filter(ImageFilter.MinFilter(3))
        im = Image.new('RGBA', size, (0, 0, 0, 0))
        sh = Image.new('RGBA', size, (0, 0, 0, 0)); sh.putalpha(m_out.filter(ImageFilter.GaussianBlur(5 * S)).point(lambda v: int(v * .55)))
        im.alpha_composite(sh, (3 * S, 6 * S))
        o = Image.new('RGBA', size, (16, 16, 22, 0)); o.putalpha(m_out); im.alpha_composite(o)
        f = Image.new('RGBA', size, (252, 252, 255, 0)); f.putalpha(m_in); im.alpha_composite(f)
        return im.resize((size[0] // S, size[1] // S), Image.LANCZOS), pad
    return C(('cursor', h), mk)


def ring(d, w, col=(255, 255, 255), a=1.0, k=1.0, start=-90):
    """arc ring (RGBA) of diameter d, stroke w, fraction k (clockwise from `start` deg)."""
    S = 3; D = d * S
    m = Image.new('L', (D, D))
    if k >= .999: ImageDraw.Draw(m).ellipse((w * S / 2, w * S / 2, D - w * S / 2, D - w * S / 2), outline=255, width=int(w * S))
    elif k > .001: ImageDraw.Draw(m).arc((w * S / 2, w * S / 2, D - w * S / 2, D - w * S / 2), start, start + 360 * k, fill=255, width=int(w * S))
    m = m.resize((d, d), Image.LANCZOS)
    im = Image.new('RGBA', (d, d), col + (0,)); im.putalpha(m.point(lambda v: int(v * a))); return im


def glow_dot(r, col, core=(255, 255, 255)):
    def mk():
        s = int(r * 6); im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        y, x = np.mgrid[0:s, 0:s].astype(np.float32); d = np.sqrt((x - s / 2) ** 2 + (y - s / 2) ** 2)
        g = np.exp(-(d / (r * 1.4)) ** 2) * .55; c = np.clip((r - d) / 1.2, 0, 1)
        a = np.clip(g + c, 0, 1)
        col_ = np.array(col, np.float32) * (1 - c[..., None]) + np.array(core, np.float32) * c[..., None]
        return Image.fromarray(np.dstack([col_, a * 255]).astype(np.uint8), 'RGBA')
    return C(('gdot', r, col, core), mk)


def line_img(p0, p1, col=(255, 255, 255), w=2.0, a=1.0):
    """anti-aliased line as (img, x0, y0) — drawn 3x supersampled on its own small canvas."""
    S = 3; x0, y0 = min(p0[0], p1[0]) - 6, min(p0[1], p1[1]) - 6
    x1, y1 = max(p0[0], p1[0]) + 6, max(p0[1], p1[1]) + 6
    ww, hh = int(x1 - x0) + 1, int(y1 - y0) + 1
    m = Image.new('L', (ww * S, hh * S))
    ImageDraw.Draw(m).line([((p0[0] - x0) * S, (p0[1] - y0) * S), ((p1[0] - x0) * S, (p1[1] - y0) * S)], fill=255, width=max(1, int(w * S)))
    m = m.resize((ww, hh), Image.LANCZOS)
    im = Image.new('RGBA', (ww, hh), col + (0,)); im.putalpha(m.point(lambda v: int(v * a)))
    return im, int(x0), int(y0)
