"""Kit for s06_showreel_b (author D): captions on measured onsets (engine look), keyed-plate access, real-location
panels (plate + DOF + clone graded to the plate light + light wrap), the casa maquette time-lapse map, a patched
feedkit (breakout assets) and the glass kit.  Read-only for other authors."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E

W, H = E.W, E.H
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def C(k, fn): return E.cached(('D',) + (k if isinstance(k, tuple) else (k,)), fn)


def scale_im(im, s):
    if abs(s - 1) < .005: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)


def fade(im, k):
    if k >= .999: return im
    out = im.copy(); out.putalpha(im.getchannel('A').point(lambda v: int(v * max(0., k)))); return out


def paste(base, im, x, y, center=True, alpha=1.0):
    """alpha-composite im onto base (RGBA) at (x, y) (centre by default), clipped to the frame."""
    if im is None or alpha <= .01: return
    if alpha < .999: im = fade(im, alpha)
    if center: x, y = x - im.width / 2, y - im.height / 2
    E._paste(base, dict(img=im, xy=(int(round(x)), int(round(y))), glass=0))


# ---------------------------------------------------------------- the engine Film (keyed plate frames)
def film_of(ctx):
    for c in (ctx.compose.__closure__ or ()):
        v = c.cell_contents
        if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    return None


def av_frame(ctx, t):
    F = film_of(ctx)
    return F.av.frame(t) if F is not None else None


# ---------------------------------------------------------------- captions (engine look, measured onsets)
def _layout(words, base, maxw=900):
    items = []
    for text, t0, emph in words:
        sz = int(base * (1.2 if emph else 1.0)); l, tp, r, b = E.font(sz).getbbox(text)
        if r - l > maxw: sz = int(sz * maxw / (r - l)); l, tp, r, b = E.font(sz).getbbox(text)
        items.append([text, t0, emph, sz, r - l])
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


def _baseline_dy(text, sz):
    """vertical offset that puts a word_img's letters on the line's baseline: word_img centres the image on the ink
    bbox, so accents (CONSTRÓI, VÍDEO, VOCÊ, TRÊS, NÃO) or a descender (Q) would shift the letters off the line."""
    def mk():
        sw = max(3, sz // 22); f = E.font(sz)
        _, t, _, b = f.getbbox(text, stroke_width=sw); _, tH, _, bH = f.getbbox('H', stroke_width=sw)
        return -((tH - t) + (bH - b)) / 2.0
    return C(('bdy', text, sz), mk)


def caption_sprites(t, pages, base=92):
    """[(img, dx, dy)] of the caption words visible at t (offsets from the caption centre). pages: [(a, z, [(text,
    t0, emph), ...])].  Same pop as the engine captions (back-out scale, 50 ms fade-in, 60 ms fade-out); every word
    sits on the same baseline (accents/descenders don't push it off the line)."""
    out = []
    for a, z, words in pages:
        if not (a <= t < z): continue
        for (text, t0, emph, sz, _w), cx, cy in _layout(words, base):
            if t < t0 - .02: continue
            lt = t - t0 + .02; s = .72 + .28 * back(lt / .16, 1.4)
            img, _ = E.word_img(text, sz, 'grad' if emph else 'white')
            if lt < .05: img = fade(img, lt / .05)
            if z - t < .06: img = fade(img, (z - t) / .06)
            out.append((scale_im(img, s), cx, cy + _baseline_dy(text, sz) * s))
    return out


def draw_caps(fr, t, pages, x=540, y=1450, base=92, alpha=1.0):
    for img, dx, dy in caption_sprites(t, pages, base):
        paste(fr, img, x + dx, y + dy, alpha=alpha)


def caps_layer(ctx, t, pages, x=540, y=1450, base=92, alpha=1.0, layer='screen'):
    for img, dx, dy in caption_sprites(t, pages, base):
        ctx.add(layer, img, x + dx, y + dy, alpha=alpha)


# ---------------------------------------------------------------- real-location panels
FX, FY = 528.0, 840.0             # face centre in take coordinates (avatar s=1, between the eyes)
# look: plate path, plate point of interest (x, y in the 1080x1920 cover-fit plate), DOF blur, grade of the clone
LOOKS = dict(
    studio=dict(path=None, poi=(560, 760), blur=2.2, tint=(1.0, 1.0, 1.0), bright=1.0, pull=0.0, wrap=.18, rim=None, sat=1.0),
    paris=dict(path=E.CLONE_BG[3], poi=(700, 760), blur=4.5, tint=(1.05, 1.02, .98), bright=1.10, pull=.16, wrap=.42,
               rim=(255, 246, 232), rside=1, ramt=.30, key=(255, 244, 228), kside=1, kamt=.10, sat=.96),
    office=dict(path=os.path.join(E.THERAPY_A, 'angle_therapist.jpg'), poi=(560, 960), blur=3.2, tint=(1.07, 1.01, .93),
                bright=1.10, pull=.18, wrap=.42, rim=(255, 226, 182), rside=1, ramt=.34, key=(255, 228, 190), kside=1,
                kamt=.14, sat=.98),
    beach=dict(path=E.CLONE_BG[6], poi=(700, 960), zoom=1.3, hy=(.47, 560), blur=3.6, tint=(1.10, 1.03, .92), bright=1.16, pull=.20, wrap=.48,
               rim=(255, 236, 200), rside=1, ramt=.38, key=(255, 236, 205), kside=1, kamt=.16, sat=1.02),
    rooftop=dict(path=E.CLONE_BG[2], poi=(760, 780), blur=4.5, tint=(1.12, 1.0, .86), bright=1.06, pull=.20, wrap=.45,
                 rim=(255, 196, 120), rside=1, ramt=.45, key=(255, 200, 140), kside=1, kamt=.14, sat=1.0),
)


def plate(name):
    """(sharp-ish DOF plate, heavy-blur wrap plate, mean colour) at 1080x1920 (cover fit, 6 % extra for parallax)."""
    L = LOOKS[name]
    def mk():
        if L['path'] is None: im = E.studio()
        else:
            im = Image.open(L['path']).convert('RGB')
            sc = max(W / im.width, H / im.height) * 1.06 * L.get('zoom', 1.0)
            im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
            x0, y0 = (im.width - W) // 2, (im.height - H) // 2
            if 'hy' in L: y0 = int(min(max(L['hy'][0] * im.height - L['hy'][1], 0), im.height - H))   # horizon at screen y
            im = im.crop((x0, y0, x0 + W, y0 + H))
        sharp = im.filter(ImageFilter.GaussianBlur(L['blur'])) if L['blur'] > .3 else im
        wrap = im.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
        mean = np.asarray(im.crop((200, 500, 880, 1500)), np.float32).reshape(-1, 3).mean(0)
        return sharp, wrap, mean
    return C(('plate', name), mk)


def _affine_out(src, size, sx, sy, ox, oy, fill=None):
    """resample src so that output pixel (u, v) shows src pixel (ox + u / sx, oy + v / sy)."""
    return src.transform(size, Image.AFFINE, (1 / sx, 0, ox, 0, 1 / sy, oy), Image.BILINEAR,
                         fillcolor=fill)


def grade_clone(av, look):
    """grade the keyed (studio-lit) avatar crop to a plate's light: tint + exposure, pull toward the plate mean, key
    light from one side, warm rim, a touch of saturation.  av: RGBA crop."""
    L = LOOKS[look]
    if L['path'] is None: return av
    rgb = np.asarray(av.convert('RGB'), np.float32); al = np.asarray(av.getchannel('A'), np.float32) / 255
    rgb = rgb * np.array(L['tint'], np.float32) * L['bright']
    m = al > .5
    if m.any():
        cm = rgb[m].mean(0); pm = plate(look)[2]
        rgb = rgb * (1 + L['pull'] * (pm / (cm + 1e-3) - 1))
    if L['sat'] != 1: g = rgb.mean(2, keepdims=True); rgb = g + (rgb - g) * L['sat']
    w = rgb.shape[1]
    gx = np.linspace(-1, 1, w, dtype=np.float32)[None, :, None]
    lit = np.clip(.5 + .5 * L['kside'] * gx, 0, 1)
    rgb = rgb * (1 - L['kamt'] * .5 + L['kamt'] * lit) + np.array(L['key'], np.float32) * L['kamt'] * .18 * lit
    from scipy.ndimage import minimum_filter
    band = np.clip(al - minimum_filter(al, size=11), 0, 1)[..., None]
    side = np.clip(.5 + L['rside'] * gx * 1.4, 0, 1)
    e = band * side * L['ramt']
    rgb = rgb * (1 - e) + np.array(L['rim'], np.float32) * e
    out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); out.putalpha(av.getchannel('A'))
    return out


def panel(av, look, pw, cx, z=1.0, pz=1.0, pdx=0.0, oy=0.0, t=0.0, flip=False):
    """one real-location panel (RGB, pw x 1920): the clone (keyed take `av`, bottom-anchored scale z) with his face at
    panel x = cx, over the look's plate (its point of interest centred, parallax zoom pz, shift pdx) with DOF, the
    clone graded to the plate's light and a light wrap on his edge."""
    L = LOOKS[look]; sharp, wrapimg, mean = plate(look)
    pz = max(1.0, pz)                                  # never zoom the plate out past its edges
    # plate: output (u, v) -> plate (px + (u - pw/2 - pdx)/pz, py + (v - 960)/pz)
    px, py = L['poi']
    ox = px - (pw / 2 + pdx) / pz; oyp = py - 960 / pz
    ox = min(max(ox, 0), W - pw / pz); oyp = min(max(oyp, 0), H - H / pz)
    bg = _affine_out(sharp, (pw, H), pz, pz, ox, oyp)
    # clone: output (u, v) -> take (FX + (u - cx)/z, 1920 + (v - oy - 1920)/z)   (flip: a mirrored clone)
    fx = FX
    if flip: av = av.transpose(Image.FLIP_LEFT_RIGHT); fx = W - FX
    a = _affine_out(av, (pw, H), z, z, fx - cx / z, H - (oy + H) / z, fill=(0, 0, 0, 0))
    if L['path'] is not None:
        a = grade_clone(a, look)
        al = np.asarray(a.getchannel('A'), np.float32) / 255
        from scipy.ndimage import minimum_filter
        edge = np.clip(al - minimum_filter(al, size=9), 0, 1)[..., None] * L['wrap']
        wr = np.asarray(_affine_out(wrapimg, (pw, H), pz, pz, ox, oyp), np.float32)
        rgb = np.asarray(a.convert('RGB'), np.float32)
        rgb = rgb * (1 - edge) + wr * edge
        b = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); b.putalpha(a.getchannel('A')); a = b
    out = bg.convert('RGBA'); out.alpha_composite(a)
    return out.convert('RGB')


# ---------------------------------------------------------------- the casa maquette as a 2-s time-lapse
def piecewise(knots, x):
    """monotone piecewise-linear map through [(x, y)...]; duplicate x = an instant jump (the later y wins)."""
    if x <= knots[0][0]: return knots[0][1]
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x0 <= x < x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return knots[-1][1]


# ---------------------------------------------------------------- feed + glass kits (from lumarc-breakout)
_BREAK = os.path.join(E.V, 'lumarc-breakout/sections')


class _EProxy:
    """engine proxy for the breakout feedkit: identical, except asset() reads the breakout asset folder."""
    def __getattr__(self, k): return getattr(E, k)
    def asset(self, name):
        p = os.path.join(E.BREAKOUT_A, name + '.png')
        if not os.path.exists(p): p = os.path.join(E.SHOWCASE_A, name + '.png')
        return E.img(p)


def feedkit():
    def mk():
        m = E._load('_D_feedkit', os.path.join(_BREAK, 'feedkit.py')); m.E = _EProxy(); return m
    return C('feedkit', mk)


def glasskit():
    return C('glasskit', lambda: E._load('_D_glasskit', os.path.join(_BREAK, '_glasskit.py')))


# ---------------------------------------------------------------- small art
def touch_sprite(r=48):
    """iOS-style touch indicator: soft translucent fingertip disc with a hairline rim + whisper of shadow."""
    def mk():
        S = 2 * r + 24; yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); d = np.hypot(xx - S / 2, yy - S / 2)
        disc = np.clip((r - d) / 2.0, 0, 1)
        rim = np.exp(-((d - r + 1.5) / 1.6) ** 2)
        sh = np.exp(-((d - r - 3) / 5) ** 2) * .25
        a = np.clip(disc * .38 + rim * .55, 0, 1)
        col = np.full((S, S, 3), 245, np.float32)
        im = Image.fromarray(np.dstack([col, a * 255]).astype(np.uint8), 'RGBA')
        sh_im = Image.fromarray(np.dstack([np.zeros((S, S, 3), np.float32), sh * 255]).astype(np.uint8), 'RGBA')
        out = Image.new('RGBA', (S, S), (0, 0, 0, 0)); out.alpha_composite(sh_im); out.alpha_composite(im); return out
    return C(('touch', r), mk)


def ring_sprite(R, w=3.0, a=1.0):
    def mk():
        S = int(2 * R + 12); yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); d = np.hypot(xx - S / 2, yy - S / 2)
        al = np.exp(-((d - R) / w) ** 2) * a
        return Image.fromarray(np.dstack([np.full((S, S, 3), 250, np.float32), al * 255]).astype(np.uint8), 'RGBA')
    return C(('ring', int(R), w, a), mk)


def _box_v(a, n):
    """continuous vertical box filter of n rows (centred, edge-clamped) on a float32 HxWxC array — a true box shutter
    (summed-area), not a handful of discrete copies (those strobe: faces and text turn into venetian stripes)."""
    n = int(max(1, round(n)))
    if n <= 1: return a
    h0 = n // 2; m = n + 1
    p = np.pad(a, ((m, m), (0, 0), (0, 0)), mode='edge')
    c = np.empty((p.shape[0] + 1,) + p.shape[1:], np.float32); c[0] = 0; np.cumsum(p, 0, dtype=np.float32, out=c[1:])
    i0 = m - h0
    return (c[i0 + n:i0 + n + a.shape[0]] - c[i0:i0 + a.shape[0]]) / n


def vsmear(img, L, n=None):
    """vertical motion blur of length L px (box shutter) — scroll blur (edge-clamped, no wrap-around)."""
    if abs(L) < 1.5: return img
    a = np.asarray(img.convert('RGB'), np.float32)
    return Image.fromarray(np.clip(_box_v(a, abs(L)) + .5, 0, 255).astype(np.uint8))


def vsmear_rgba(img, L):
    """an RGBA sprite smeared upward over L px (premultiplied box blur); returns a taller sprite whose top-aligned
    original position is at the bottom (the trail points down, behind the upward motion)."""
    L = int(round(abs(L)))
    if L < 2: return img
    tall = Image.new('RGBA', (img.width, img.height + L), (0, 0, 0, 0)); tall.alpha_composite(img, (0, L))
    a = np.asarray(tall, np.float32); al = a[..., 3:4] / 255.0
    pm = np.concatenate([a[..., :3] * al, al * 255.0], 2)
    pm = np.pad(pm, ((L, L), (0, 0), (0, 0)))
    c = np.empty((pm.shape[0] + 1,) + pm.shape[1:], np.float32); c[0] = 0; np.cumsum(pm, 0, dtype=np.float32, out=c[1:])
    n = L + 1; Hh = tall.height
    s = (c[L + n:L + n + Hh] - c[L:L + Hh]) / n                    # window [y, y+n): the trail extends below the disc
    A = np.clip(s[..., 3:4], 0, 255); rgb = s[..., :3] / np.maximum(A / 255.0, 1e-4)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), A]).astype(np.uint8), 'RGBA')


def zoom_smear(img, amt, c, passes=5):
    """radial (crash-zoom) blur: 2**passes evenly spaced zoom-in samples over scales 1 .. 1+amt, by recursive doubling
    (passes zooms instead of 2**passes) — continuous streaks, no comb of discrete UI copies, no black border."""
    rgb = img.convert('RGB')
    if amt < 1e-3: return rgb.convert('RGBA')
    r = math.log(1 + amt)
    for k in range(1, passes + 1):
        rgb = Image.blend(rgb, E.zoom(rgb, math.exp(r / 2 ** k), c), .5)
    return rgb.convert('RGBA')


def hsmear(img, L, n=5):
    if abs(L) < 1.5: return img
    a = np.asarray(img, np.float32); acc = np.zeros_like(a); n = max(3, min(n, int(abs(L) / 4) + 2))
    for i in range(n):
        acc += np.roll(a, int(round(L * (i / (n - 1) - .5))), 1)
    return Image.fromarray((acc / n).astype(np.uint8), img.mode)


def glow_sprite(w, h, col, blur, a=1.0):
    def mk():
        pad = int(blur * 2.5); m = Image.new('L', (w + 2 * pad, h + 2 * pad)); ImageDraw.Draw(m).ellipse((pad, pad, pad + w, pad + h), fill=int(255 * a))
        im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); return im
    return C(('glow', w, h, col, blur, a), mk)


def add_light(fr, glow, x, y, k=1.0):
    """additive light: glow (RGBA sprite, colour x alpha) added onto fr (RGB/RGBA) centred at (x, y)."""
    if k <= .01: return fr
    base = fr.convert('RGB'); L = Image.new('RGB', base.size, (0, 0, 0))
    g = glow; a = g.getchannel('A').point(lambda v: int(v * min(1.0, k)))
    col = Image.new('RGB', g.size, g.getpixel((g.width // 2, g.height // 2))[:3])
    L.paste(col, (int(x - g.width / 2), int(y - g.height / 2)), a)
    return ImageChops.add(base, L)
