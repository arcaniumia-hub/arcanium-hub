"""_H_kit — helpers for the three alternative HOOKS (s01_hook_a1, s02_hook_a2, s03_hook_a3; author H). Read-only for
everybody else.

* camera: the engine camera (ctx.cam) + an exact forward map world -> screen (cam_map), avatar placement by face anchor
* captions in the engine look on MEASURED onsets (own pages, never stacked, safe-zone y chosen per beat)
* type: rich text with colour emoji, tracked caps, Inter / Outfit
* motion: slam (scale + directional motion blur), decaying shakes, light hits, zoom blur of the world only
* the triangle: thin wrappers over sections/_tri.py (never re-implemented): node masking (hide nodes not yet shown)
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import engine as E
from sections import _tri as TRI

W, H, FPS = E.W, E.H, E.FPS
clamp = E.clamp
def lerp(a, b, k): return a + (b - a) * k
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def eo(x, p=3): x = clamp(x); return 1 - (1 - x) ** p
def ei(x, p=2): x = clamp(x); return x ** p
def back(x, s=1.7): return E.back(x, s)
def bump(x): x = clamp(x); return math.sin(math.pi * x)
def decay(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def win(t, a, b): return a <= t < b

def jump_t(i):
    """first 30 fps frame time that shows segment i's pose (the avatar takes the NEAREST 25 fps frame)."""
    t0 = E.TL[i]['t0']; k = int(round(t0 * 25))
    return next(j for j in range(int(t0 * 30) - 3, int(t0 * 30) + 4) if E.Avatar._k_of(j / 30) >= k) / 30

def fi(t): return int(round(t * FPS))

# ------------------------------------------------------------------------------------------- camera / avatar
FACE = (540.0, 905.0)       # plate point between his eyes and mouth (take coordinates)
HEAD_TOP, CHIN = 588.0, 1062.0

def set_cam(ctx, z=1.0, x=540., y=960., dx=0., dy=0., rot=0.):
    ctx.cam.update(z=z, x=x, y=y, dx=dx, dy=dy, rot=math.radians(rot))

def cam_map(cam, p):
    """world point -> screen point through the engine camera (incl. its edge clamp)."""
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    c, s = math.cos(cam['rot']), math.sin(cam['rot'])
    vx, vy = (p[0] - cam['x']) * z, (p[1] - cam['y']) * z
    return X + c * vx - s * vy, Y + s * vx + c * vy

def av_map(A, p):
    """take (plate) point -> world point for avatar placement A (ctx.avatar dict)."""
    s = A['s']; return 540 + A['x'] + (p[0] - 540) * s, H + A['y'] - (H - p[1]) * s

def scr(ctx, p):
    """take point -> screen (avatar placement + camera)."""
    return cam_map(ctx.cam, av_map(ctx.avatar, p))

def shake(t, t0, amp, tau=.16, f=19., seed=0.):
    if t < t0: return 0.0, 0.0
    u = t - t0; e = amp * math.exp(-u / tau)
    return e * math.sin(2 * math.pi * f * u + seed), e * .8 * math.sin(2 * math.pi * f * 1.27 * u + 1.7 + seed)

def punch(t, t0, amp, tau=.12):
    """camera punch: instant +amp zoom on t0 that eases back (exp)."""
    return amp * math.exp(-(t - t0) / tau) if t >= t0 else 0.0

# ------------------------------------------------------------------------------------------- type
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
INTER = '/usr/share/fonts/opentype/inter/Inter-{}.otf'
SERIF_B = '/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf'
SERIF_I = '/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf'
_F = {}
def ffont(path, size):
    k = (path, size)
    if k not in _F: _F[k] = ImageFont.truetype(path, size)
    return _F[k]
def inter(size, w='Bold'): return ffont(INTER.format(w), size)

def emoji(ch, size):
    def mk():
        f = ImageFont.truetype(EMOJI, 109); im = Image.new('RGBA', (220, 170), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 10), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im
        s = size / 128.0
        return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return E.cached(('H_emoji', ch, size), mk)

def _is_emo(c):
    o = ord(c)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x2B50, 0x2728, 0x2764)

def _runs(text):
    runs, cur = [], ''
    for c in text:
        if ord(c) in (0xFE0F, 0x200D): continue
        if _is_emo(c):
            if cur: runs.append((cur, False)); cur = ''
            runs.append((c, True))
        else: cur += c
    if cur: runs.append((cur, False))
    return runs

def rich(text, fnt, col, esize=None):
    """one line of text with colour emoji (RGBA, tight height = font ascent + descent)."""
    def mk():
        asc, desc = fnt.getmetrics(); h = asc + desc; es = esize or int(h * .78)
        parts = []; x = 0
        for s, e in _runs(text):
            if e:
                im = emoji(s, es); parts.append((im, x, (h - im.height) // 2 + int(h * .03))); x += im.width + int(es * .1)
            else:
                w = int(math.ceil(fnt.getlength(s)))
                im = Image.new('RGBA', (w + 4, h + 4), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((2, 2), s, font=fnt, fill=tuple(col) + (255,))
                parts.append((im, x, -2)); x += w
        out = Image.new('RGBA', (max(1, x + 4), h + 6), (0, 0, 0, 0))
        for im, px, py in parts: out.alpha_composite(im, (px, max(0, py + 2)))
        return out
    return E.cached(('H_rich', text, id(fnt), tuple(col), esize), mk)

def tracked(s, fnt, col, track):
    w = int(sum(fnt.getlength(c) for c in s) + track * (len(s) - 1)) + 8
    asc, desc = fnt.getmetrics(); im = Image.new('RGBA', (w, asc + desc), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
    for c in s: d.text((x, 0), c, font=fnt, fill=tuple(col) + (255,)); x += fnt.getlength(c) + track
    return im

def scaled(im, s):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.BILINEAR)

def rotated(im, deg):
    if abs(deg) < .05: return im
    return im.rotate(deg, Image.BICUBIC, expand=True)

def faded(im, a): return E.fade(im, a) if a < .999 else im

def glow_sprite(r, col):
    def mk():
        n = int(2 * r); yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + .5
        d = np.hypot(xx - r, yy - r) / r; a = np.clip(1 - d, 0, 1) ** 2.2
        im = Image.new('RGBA', (n, n), tuple(col) + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return E.cached(('H_glow', int(r), tuple(col)), mk)

def big_word(text, size, style='white', glow=True):
    """display word: engine word look (dark stroke + soft shadow) + an optional LUMARC-purple glow behind it."""
    def mk():
        im, pad = E.word_img(text, size, style)
        if not glow: return im
        a = im.getchannel('A').filter(ImageFilter.GaussianBlur(size * .18)).point(lambda v: int(v * .55))
        g = Image.new('RGBA', im.size, (118, 92, 255, 0)); g.putalpha(a)
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(im); return out
    return E.cached(('H_big', text, size, style, glow), mk)

def ink_box(text, size):
    """(w, h) of a word's ink at font size (no pad) — for layout."""
    l, t, r, b = E.font(size).getbbox(text); return r - l, b - t

# ------------------------------------------------------------------------------------------- captions (engine look)
def page(words, a=None, z=None, base=92):
    ws = [dict(text=w, t0=t0, emph=bool(e)) for (w, t0, e) in words]
    return dict(a=(ws[0]['t0'] - .04) if a is None else a, z=z, words=ws, base=base)

def chain(pages, end):
    for i, p in enumerate(pages):
        if p['z'] is None: p['z'] = (pages[i + 1]['a'] - .02) if i + 1 < len(pages) else end
    return pages

def _layout(p):
    key = ('H_lay', tuple(w['text'] for w in p['words']), tuple(w['emph'] for w in p['words']), p['base'])
    return E.cached(key, lambda: E._layout(dict(words=p['words']), p['base']))

def base_dy(text, sz):
    def mk():
        f = E.font(sz); sw = max(3, sz // 22)
        l, t, r, b = f.getbbox(text, stroke_width=sw); l2, t2, r2, b2 = f.getbbox('A', stroke_width=sw)
        return (t + b) / 2 - (t2 + b2) / 2
    return E.cached(('H_bdy', text, sz), mk)

def captions(ctx, t, pages, y, x=W / 2, special=None, alpha=1.0, red=()):
    """active page at centre (x, y): word pop on its onset, gradient for emphasis; `red` = words drawn in alarm red."""
    ctx.captions = False
    for p in pages:
        if not (p['a'] <= t < p['z']): continue
        ws = p['words']; yy0 = y(t) if callable(y) else y
        for i, (w, sz, cx, cy) in enumerate(_layout(p)):
            t0 = w['t0']
            if t < t0 - .02: continue
            t1 = ws[i + 1]['t0'] if i + 1 < len(ws) else min(p['z'], t0 + .5)
            lt = t - t0 + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            a = clamp(lt / .05) * alpha
            if p['z'] - t < .06: a *= clamp((p['z'] - t) / .06)
            if w['text'] in red: img = red_word(w['text'], sz)
            else: img = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')[0]
            yy = yy0 + cy + base_dy(w['text'], sz) * s
            if special and w['text'] in special and special[w['text']](ctx, t, img, x + cx, yy, s, a): continue
            if a <= .01: continue
            ctx.add('screen', scaled(img, s), x + cx, yy, alpha=a)

RED = (255, 62, 78)
def red_word(text, size):
    def mk():
        im, pad = E.word_img(text, size, 'white'); a = im.getchannel('A')
        f = E.font(size); sw = max(3, size // 22); l, t, r, b = f.getbbox(text, stroke_width=sw)
        fill = Image.new('L', im.size); ImageDraw.Draw(fill).text((pad - l, pad - t), text, font=f, fill=255)
        out = im.copy(); col = Image.new('RGBA', im.size, RED + (0,)); col.putalpha(fill); out.alpha_composite(col)
        gl = Image.new('RGBA', im.size, (255, 40, 60, 0)); gl.putalpha(fill.filter(ImageFilter.GaussianBlur(size * .2)).point(lambda v: int(v * .6)))
        o2 = Image.new('RGBA', im.size, (0, 0, 0, 0)); o2.alpha_composite(gl); o2.alpha_composite(out); return o2
    return E.cached(('H_red', text, size), mk)

# ------------------------------------------------------------------------------------------- motion
def mblur(im, vx, vy):
    """directional motion blur along -(vx, vy) px (premultiplied). Returns (img, ox, oy) centre offset."""
    L = math.hypot(vx, vy)
    if L < 1.5: return im, 0.0, 0.0
    n = int(min(14, max(3, L / 4.0)))
    a = np.asarray(im, np.float32).copy(); a[..., :3] *= a[..., 3:] / 255.
    h, w = a.shape[:2]; px, py = int(math.ceil(abs(vx))), int(math.ceil(abs(vy)))
    acc = np.zeros((h + py, w + px, 4), np.float32)
    x0, y0 = (px if vx > 0 else 0), (py if vy > 0 else 0)
    for i in range(n):
        f = i / (n - 1); ox, oy = int(round(x0 - vx * f)), int(round(y0 - vy * f))
        acc[oy:oy + h, ox:ox + w] += a
    acc /= n
    rgb = np.where(acc[..., 3:] > .5, acc[..., :3] * 255. / np.maximum(acc[..., 3:], 1e-3), 0)
    out = Image.fromarray(np.clip(np.dstack([rgb, acc[..., 3:]]), 0, 255).astype(np.uint8), 'RGBA')
    return out, (acc.shape[1] / 2 - x0 - w / 2), (acc.shape[0] / 2 - y0 - h / 2)

def zoom_trail(im, s0, s1, n=6):
    """radial zoom smear of a sprite (scales s0..s1 stacked) — for things slamming in from the lens."""
    if abs(s1 - s0) < .02: return scaled(im, s1)
    big = scaled(im, max(s0, s1)); acc = np.zeros((big.height, big.width, 4), np.float32)
    for i in range(n):
        s = lerp(s1, s0, i / (n - 1) * .9); sp = scaled(im, s); a = np.asarray(sp, np.float32).copy(); a[..., :3] *= a[..., 3:] / 255.
        w = 1.0 if i == 0 else .55 * (1 - i / n)
        x0, y0 = (big.width - sp.width) // 2, (big.height - sp.height) // 2
        acc[y0:y0 + sp.height, x0:x0 + sp.width] += a * w
    acc /= max(1e-3, acc[..., 3:].max() / 255.) if acc[..., 3:].max() > 255 else 1
    rgb = np.where(acc[..., 3:] > .5, acc[..., :3] * 255. / np.maximum(acc[..., 3:], 1e-3), 0)
    return Image.fromarray(np.clip(np.dstack([rgb, acc[..., 3:]]), 0, 255).astype(np.uint8), 'RGBA')

def zblur(fr, k, n=4, anchor=(W / 2, H / 2)):
    """radial zoom blur of the world (use in ctx.wrap -> screen layers / captions stay crisp)."""
    rgb = fr.convert('RGB'); acc = np.asarray(rgb, np.float32).copy()
    for i in range(1, n):
        acc += np.asarray(E.zoom(rgb, 1 + k * .05 * i, anchor), np.float32)
    return Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8))

def hsmear(fr, L):
    """horizontal box smear of L px (whip), edge-clamped."""
    L = int(round(L))
    if L < 2: return fr
    a = np.asarray(fr.convert('RGB'), np.float32); c = np.cumsum(np.pad(a, ((0, 0), (L, 0), (0, 0)), mode='edge'), 1)
    out = (c[:, L:] - c[:, :-L]) / L
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def light_hit(fr, k, col=(196, 182, 255)):
    """flash that reads as LIGHT: exposure push + highlight bloom + tint lift (k <= ~.6)."""
    rgb = fr.convert('RGB'); a = np.asarray(rgb, np.float32)
    sm = np.asarray(rgb.resize((W // 4, H // 4), Image.BILINEAR), np.float32)
    lum = sm.mean(2, keepdims=True); hb = sm * np.clip((lum - 80) / 110, 0, 1)
    bloom = np.asarray(Image.fromarray(hb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32)
    y = (a * (1 + 1.5 * k) + bloom * (2.2 * k) + np.array(col, np.float32) * (.22 * k)) / 255.
    y = np.where(y < .72, y, .72 + .28 * (1 - np.exp(-(y - .72) / .28)))
    return Image.fromarray(np.clip(y * 255, 0, 255).astype(np.uint8))

def tint_edges(fr, k, col=(255, 40, 60)):
    """coloured light from the frame edges (alarm / red hit), k 0..1."""
    def mk():
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        d = np.maximum(np.abs(xx / (W / 8) - 1), np.abs(yy / (H / 8) - 1)); m = np.clip((d - .45) / .55, 0, 1) ** 1.6
        return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255
    m = E.cached('H_edgemask', mk)
    a = np.asarray(fr.convert('RGB'), np.float32)
    a = a * (1 - .55 * k * m) + np.array(col, np.float32) * (.55 * k * m)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def compose_wraps(*fns):
    fns = [f for f in fns if f is not None]
    if not fns: return None
    def w(fr):
        for f in fns: fr = f(fr)
        return fr
    return w

def scrim(w, h, a=.55, r=None):
    """soft dark ellipse behind type (legibility over busy plates)."""
    def mk():
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)); m = np.clip(1 - d, 0, 1) ** 1.3
        im = Image.new('RGBA', (w, h), (6, 6, 12, 0)); im.putalpha(Image.fromarray((m * 255 * a).astype(np.uint8))); return im
    return E.cached(('H_scrim', w, h, a), mk)

# ------------------------------------------------------------------------------------------- the triangle (kit wrappers)
def tri_render(st, size, at, show=(1, 1, 1), canvas=(W, H)):
    """TRI.render on a full-frame canvas; nodes with show[i] == 0 are hidden (scaled to nothing + erased)."""
    st = dict(TRI._norm(st))
    if not all(show):
        st['pop'] = tuple(p if s else .0005 for p, s in zip(st['pop'], show))
    im = TRI.render(st, size, canvas=canvas, at=at)
    if not all(show):
        d = None
        for i, nm in enumerate(TRI.NODES):
            if show[i]: continue
            x, y = TRI.anchor(nm, st, size, canvas=canvas, at=at)
            if d is None: m = Image.new('L', im.size, 255); d = ImageDraw.Draw(m)
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=0)
        if d is not None: im.putalpha(ImageChops.multiply(im.getchannel('A'), m))
    return im

def tri_bbox_crop(im):
    bb = im.getbbox()
    if not bb: return None, 0, 0
    return im.crop(bb), bb[0], bb[1]

def ring(r, width, col, a=1.0):
    """thin glowing ring sprite (shock ring)."""
    def mk():
        n = int(2 * r + 4 * width + 8); im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); c = n / 2
        m = Image.new('L', (n, n)); d = ImageDraw.Draw(m); d.ellipse((c - r, c - r, c + r, c + r), outline=255, width=max(1, int(width)))
        g = m.filter(ImageFilter.GaussianBlur(width * 1.4))
        al = ImageChops.lighter(m, g.point(lambda v: min(255, v * 2)))
        im = Image.new('RGBA', (n, n), tuple(col) + (0,)); im.putalpha(al); return im
    return faded(E.cached(('H_ring', int(r), int(width), tuple(col)), mk), a)

def edge_shadow(ctx, world_x):
    """soft shadow falloff over the take's cut edge when the avatar is shifted sideways at s=1 (his shoulders fill the
    take's full width from take-y ~1450, so the shifted take shows a straight vertical edge low in the frame)."""
    def mk():
        w = 380; yy, xx = np.mgrid[0:H, 0:w].astype(np.float32)
        a = np.clip(1 - np.abs(xx - w / 2) / (w / 2), 0, 1) ** 1.1 * np.clip((yy - 1150) / 380, 0, 1) ** 1.4
        im = Image.new('RGBA', (w, H), (10, 8, 20, 0)); im.putalpha(Image.fromarray((a * 250).astype(np.uint8))); return im
    ctx.add('front', E.cached('H_edge', mk), world_x, H / 2)
