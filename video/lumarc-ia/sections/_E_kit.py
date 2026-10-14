"""Kit for s07_lumarc (author E): captions on measured onsets (engine look), LUMARC glass UI pieces (dark frosted
panels, line icons, task dashboard rows, team cards, slot-machine chips, reticle, gauge, gradient check), the cartoon
weight, giant brand type and small light/blur helpers.  Everything is cached and deterministic.  Read-only for others."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import engine as E

W, H = E.W, E.H
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
GRAD, GRAD_L = E.GRAD, E.GRAD_LIGHT
WHITE, MUTED = E.WHITE, E.MUTED
LILAC = (196, 182, 255)
DJ = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
DJB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def decay(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def spring(x, f=2.2, d=5.5):
    """0 -> 1 with a damped overshoot (x in seconds-ish units of the caller)."""
    if x <= 0: return 0.0
    return 1 - math.exp(-d * x) * math.cos(2 * math.pi * f * x)
def C(k, fn): return E.cached(('E7',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0


def scale_im(im, sx, sy=None):
    sy = sx if sy is None else sy
    if abs(sx - 1) < .004 and abs(sy - 1) < .004: return im
    return im.resize((max(1, int(round(im.width * sx))), max(1, int(round(im.height * sy)))), Image.BILINEAR)


def fade(im, k):
    if k >= .999: return im
    out = im.copy(); out.putalpha(im.getchannel('A').point(lambda v, k=max(0.0, k): int(v * k))); return out


def paste(base, im, x, y, center=True, alpha=1.0):
    if im is None or alpha <= .01: return
    if alpha < .999: im = fade(im, alpha)
    if center: x, y = x - im.width / 2, y - im.height / 2
    E._paste(base, dict(img=im, xy=(int(round(x)), int(round(y))), glass=0))


def djfont(size, bold=False): return C(('dj', size, bold), lambda: ImageFont.truetype(DJB if bold else DJ, size))


def grad_img(w, h, cols=GRAD_L, vert=0.0):
    """horizontal brand gradient; vert > 0 adds a top-bright vertical falloff."""
    g = np.asarray(E.gradient(w, h, cols), np.float32)
    if vert:
        v = (1 + vert * (1 - np.linspace(0, 1, h, dtype=np.float32) * 2))[:, None, None]
        g = np.clip(g * v, 0, 255)
    return Image.fromarray(g.astype(np.uint8))


def colorize(mask, col):
    """RGBA of a single colour (or an RGB image) with `mask` (L) as alpha."""
    im = (Image.new('RGB', mask.size, col) if isinstance(col, tuple) else col.resize(mask.size)).convert('RGBA')
    im.putalpha(mask); return im


def glow_of(mask, col, blur, gain=1.0, pad=0):
    m = mask if not pad else Image.new('L', (mask.width + 2 * pad, mask.height + 2 * pad))
    if pad: m.paste(mask, (pad, pad))
    g = m.filter(ImageFilter.GaussianBlur(blur))
    if gain != 1: g = g.point(lambda v: int(min(255, v * gain)))
    return colorize(g, col)


def blob(w, h, col, blur, a=1.0):
    """soft elliptical light sprite (RGBA)."""
    def mk():
        pad = int(blur * 2.6); m = Image.new('L', (w + 2 * pad, h + 2 * pad))
        ImageDraw.Draw(m).ellipse((pad, pad, pad + w, pad + h), fill=int(255 * a))
        return colorize(m.filter(ImageFilter.GaussianBlur(blur)), col)
    return C(('blob', w, h, col, blur, a), mk)


def add_light(fr, sprite, x, y, k=1.0):
    """additive light (sprite colour x alpha x k) onto fr (RGBA) centred at (x, y); returns RGBA."""
    if k <= .01: return fr
    a = sprite.getchannel('A')
    if k < .999: a = a.point(lambda v, k=k: int(v * k))
    L = Image.new('RGB', fr.size, (0, 0, 0))
    col = Image.new('RGB', sprite.size, sprite.getpixel((sprite.width // 2, sprite.height // 2))[:3])
    L.paste(col, (int(x - sprite.width / 2), int(y - sprite.height / 2)), a)
    out = ImageChops.add(fr.convert('RGB'), L).convert('RGBA'); return out


def ring(R, w=3.0, col=(235, 228, 255), a=1.0):
    def mk():
        S = int(2 * R + 8 * w + 8); yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); d = np.hypot(xx - S / 2, yy - S / 2)
        al = np.exp(-((d - R) / w) ** 2) * a
        return Image.fromarray(np.dstack([np.broadcast_to(np.array(col, np.float32), (S, S, 3)), al * 255]).astype(np.uint8), 'RGBA')
    return C(('ring', int(R), round(w, 1), col, round(a, 2)), mk)


def _box1d(a, L, axis, edge=False):
    """continuous centred box average of length L px along `axis` (cumulative sums: O(1) per pixel whatever L, so a
    long smear is a smooth streak, not a stack of discrete copies)."""
    L = int(round(abs(L)))
    if L < 2: return a
    h = L // 2; n = a.shape[axis]
    pad = [(0, 0)] * a.ndim; pad[axis] = (h + 1, L - h)
    c = np.cumsum(np.pad(a, pad, mode='edge' if edge else 'constant'), axis=axis, dtype=np.float32)
    hi = [slice(None)] * a.ndim; lo = [slice(None)] * a.ndim
    hi[axis] = slice(L, L + n); lo[axis] = slice(0, n)
    return (c[tuple(hi)] - c[tuple(lo)]) / L


def _smear_rgba(img, L, axis):
    m = int(abs(L) / 2) + 2
    a = np.asarray(img.convert('RGBA'), np.float32); pm = a.copy(); pm[..., :3] *= a[..., 3:4] / 255
    pad = [(0, 0), (0, 0), (0, 0)]; pad[axis] = (m, m)
    acc = _box1d(np.pad(pm, pad), L, axis); al = acc[..., 3:4]
    rgb = np.where(al > .5, acc[..., :3] * 255 / np.maximum(al, 1e-3), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al, 0, 255)]).astype(np.uint8), 'RGBA')


def vsmear(img, L, n=6):
    """vertical motion blur of an RGBA sprite (premultiplied continuous box over L px; canvas grows by L/2 + 2 each
    side, same centre).  `n` is kept for call compatibility."""
    if abs(L) < 1.5: return img
    return _smear_rgba(img, L, 0)


def hsmear(img, L, n=6, keep=False):
    """horizontal motion blur (premultiplied, continuous box); keep=True returns the original size with edge padding
    (full-frame whip)."""
    if abs(L) < 1.5: return img
    if keep:
        a = np.asarray(img.convert('RGB'), np.float32)
        return Image.fromarray(np.clip(_box1d(a, L, 1, edge=True), 0, 255).astype(np.uint8)).convert('RGBA')
    return _smear_rgba(img, L, 1)


def zoom_smear(fr, amount, cx=540, cy=960, n=12, dark=1.0):
    """smooth radial (crash-zoom) blur of a full frame: n zoomed copies spread over 1 .. 1 + amount around (cx, cy),
    accumulated at half resolution and blended over the sharp frame's centre (RGBA in, RGBA out)."""
    if amount < .004: return fr
    src = fr.convert('RGB'); w, h = src.size; sm = src.resize((w // 2, h // 2), Image.BILINEAR)
    acc = np.zeros((h // 2, w // 2, 3), np.float32)
    hx, hy = cx / 2, cy / 2
    for i in range(n):
        a = 1 / (1 + amount * i / (n - 1))
        acc += np.asarray(sm.transform(sm.size, Image.AFFINE, (a, 0, hx - a * hx, 0, a, hy - a * hy), Image.BILINEAR), np.float32)
    acc /= n
    bl = Image.fromarray(np.clip(acc * dark, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    return bl.convert('RGBA')


def soft_blur(fr, r):
    """cheap large gaussian (quarter-res) of an RGB(A) frame."""
    if r < .4: return fr
    if r < 3: return fr.filter(ImageFilter.GaussianBlur(r))
    s = 4 if r > 8 else 2
    sm = fr.resize((fr.width // s, fr.height // s), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / s))
    return sm.resize(fr.size, Image.BILINEAR)


def sheen(img, k, width=.14, strength=.75, slope=.35):
    """diagonal light sweep across an RGBA sprite (k: 0 -> 1 position)."""
    if k <= 0 or k >= 1: return img
    w, h = img.size
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :] + np.linspace(0, slope, h, dtype=np.float32)[:, None]
    c = lerp(-.3, 1.3 + slope, k); band = np.clip(1 - np.abs(xx - c) / width, 0, 1) ** 2 * strength
    a = np.asarray(img.getchannel('A'), np.float32) / 255
    m = Image.fromarray((band * a * 255).astype(np.uint8))
    out = img.copy(); out.alpha_composite(colorize(m, (255, 255, 255))); return out


# ---------------------------------------------------------------- captions (engine look, measured onsets)
def caption_sprites(t, pages, base=92):
    """[(img, dx, dy)] visible at t.  pages: [(a, z, [(TEXT, t0, emph), ...])] — same pop as the engine captions."""
    out = []
    for a, z, words in pages:
        if not (a <= t < z): continue
        page = dict(words=[dict(text=w, emph=e, t0=t0) for w, t0, e in words])
        for w, sz, cx, cy in E._layout(page, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * back(lt / .16, 1.4)
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = fade(img, lt / .05)
            if z - t < .06: img = fade(img, (z - t) / .06)
            out.append((scale_im(img, s), cx, cy))
    return out


def caps_layer(ctx, t, pages, x=540, y=330, base=92, alpha=1.0):
    for img, dx, dy in caption_sprites(t, pages, base):
        ctx.add('screen', img, x + dx, y + dy, alpha=alpha)


# ---------------------------------------------------------------- dark frosted glass
def panel(w, h, r=40, fill=(18, 16, 34), a=.62, border=.55, glow=0.0):
    """dark frosted glass card: translucent night tint, top sheen, 2 px light border brighter top-left, soft drop
    shadow baked in (returns (img, pad))."""
    def mk():
        pad = 40
        im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
        sh = Image.new('L', im.size); sh.paste(m, (pad, pad + 14))
        im.alpha_composite(colorize(sh.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * .55)), (0, 0, 6)))
        body = np.zeros((h, w, 4), np.float32); body[..., :3] = fill
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        body[..., 3] = a * 255
        sheen_ = (np.clip(1 - yy / .45, 0, 1) ** 2 * 26)
        body[..., :3] += sheen_[..., None]
        b = Image.fromarray(np.clip(body, 0, 255).astype(np.uint8), 'RGBA')
        b.putalpha(ImageChops.multiply(b.getchannel('A'), m))
        im.alpha_composite(b, (pad, pad))
        # border: light top-left -> lilac bottom-right
        bm = Image.new('L', (w, h)); ImageDraw.Draw(bm).rounded_rectangle((1, 1, w - 2, h - 2), r, outline=255, width=2)
        gx = np.linspace(0, 1, w, dtype=np.float32)[None, :]; gy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        k = np.clip(1 - (gx * .5 + gy * .5), 0, 1)
        col = np.dstack([lerp(150, 255, k), lerp(130, 255, k), np.full_like(k, 255)])
        al = np.asarray(bm, np.float32) * (border * (.45 + .55 * k))
        bi = Image.fromarray(np.dstack([col, al]).astype(np.uint8), 'RGBA')
        im.alpha_composite(bi, (pad, pad))
        if glow:
            gm = Image.new('L', im.size); ImageDraw.Draw(gm).rounded_rectangle((pad, pad, pad + w, pad + h), r, outline=255, width=6)
            im = Image.alpha_composite(colorize(gm.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * glow)), (120, 90, 255)), im)
        return im, pad
    return C(('panel', w, h, r, fill, a, border, glow), mk)


def dashed_rrect(w, h, r, col=(196, 182, 255), a=.7, width=3, dash=18, gap=12):
    def mk():
        S = 2; im = Image.new('L', (w * S, h * S)); d = ImageDraw.Draw(im)
        # sample the rounded-rect perimeter and draw dashes along it
        pts = []
        R = r * S; ww, hh = (w - 2) * S, (h - 2) * S; o = S
        segs = []
        for (x0, y0, x1, y1) in ((o + R, o, o + ww - R, o), (o + ww, o + R, o + ww, o + hh - R), (o + ww - R, o + hh, o + R, o + hh), (o, o + hh - R, o, o + R)):
            segs.append(('L', x0, y0, x1, y1))
        corners = [(o + ww - R, o + R, -90, 0), (o + ww - R, o + hh - R, 0, 90), (o + R, o + hh - R, 90, 180), (o + R, o + R, 180, 270)]
        path = []
        for i in range(4):
            _, x0, y0, x1, y1 = segs[i]; n = int(math.hypot(x1 - x0, y1 - y0) / 2) + 1
            path += [(lerp(x0, x1, j / n), lerp(y0, y1, j / n)) for j in range(n)]
            cx, cy, a0, a1 = corners[i]; n = int(R * math.pi / 2 / 2) + 1
            path += [(cx + R * math.cos(math.radians(lerp(a0, a1, j / n))), cy + R * math.sin(math.radians(lerp(a0, a1, j / n)))) for j in range(n)]
        acc = 0.0; on = True; cur = [path[0]]; per = (dash if on else gap) * S
        for p0, p1 in zip(path, path[1:]):
            acc += math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            if on: cur.append(p1)
            if acc >= per:
                if on and len(cur) > 1: d.line(cur, fill=255, width=width * S)
                on = not on; acc = 0.0; cur = [p1]; per = (dash if on else gap) * S
        if on and len(cur) > 1: d.line(cur, fill=255, width=width * S)
        m = im.resize((w, h), Image.LANCZOS).point(lambda v: int(v * a))
        return colorize(m, col)
    return C(('dash', w, h, r, col, a, width, dash, gap), mk)


# ---------------------------------------------------------------- line icons (drawn at 4x, white on transparent)
def icon(name, s=64, col=(245, 243, 255), stroke=.075):
    """simple consistent line/solid icons: cut cc color music versions formats image video voice cube text motion
    upscale avatar knight spark gem plus check."""
    def mk():
        S = 4; n = s * S; m = Image.new('L', (n, n)); d = ImageDraw.Draw(m); lw = max(2, int(n * stroke))
        def P(x, y): return (x * n, y * n)
        if name == 'cut':
            f = djfont(int(n * .9)); d.text(P(.5, .52), '✂', font=f, fill=255, anchor='mm')
        elif name == 'cc':
            d.rounded_rectangle((*P(.08, .2), *P(.92, .8)), int(n * .12), outline=255, width=lw)
            f = E.font(int(n * .36), 800); d.text(P(.5, .5), 'CC', font=f, fill=255, anchor='mm')
        elif name == 'color':
            for i, (x, y) in enumerate(((.38, .38), (.62, .38), (.5, .6))):
                d.ellipse((*P(x - .24, y - .24), *P(x + .24, y + .24)), outline=255, width=lw)
        elif name == 'music':
            f = djfont(int(n * .86)); d.text(P(.5, .52), '♫', font=f, fill=255, anchor='mm')
        elif name == 'versions':
            for k, o in enumerate((.0, .12, .24)):
                d.rounded_rectangle((*P(.14 + o, .40 - o), *P(.62 + o, .84 - o)), int(n * .07), outline=255, width=lw, fill=0 if k < 2 else None)
        elif name == 'formats':
            d.rounded_rectangle((*P(.12, .14), *P(.46, .86)), int(n * .06), outline=255, width=lw)
            d.rounded_rectangle((*P(.56, .32), *P(.9, .66)), int(n * .06), outline=255, width=lw)
        elif name == 'image':
            d.rounded_rectangle((*P(.08, .16), *P(.92, .84)), int(n * .1), outline=255, width=lw)
            d.line([P(.16, .76), P(.4, .46), P(.56, .62), P(.68, .5), P(.86, .74)], fill=255, width=lw, joint='curve')
            d.ellipse((*P(.62, .26), *P(.76, .4)), fill=255)
        elif name == 'video':
            d.rounded_rectangle((*P(.06, .18), *P(.94, .82)), int(n * .14), outline=255, width=lw)
            d.polygon([P(.4, .34), P(.66, .5), P(.4, .66)], fill=255)
        elif name == 'voice':
            for i, hh in enumerate((.18, .4, .62, .32, .5, .22)):
                x = .14 + i * .144; d.rounded_rectangle((*P(x - .04, .5 - hh / 2), *P(x + .04, .5 + hh / 2)), int(n * .04), fill=255)
        elif name == 'cube':
            c = (.5, .52); r = .36
            top = [P(.5, .14), P(.86, .32), P(.5, .5), P(.14, .32)]
            d.polygon(top, outline=255, width=lw)
            d.line([P(.14, .32), P(.14, .7), P(.5, .88), P(.86, .7), P(.86, .32)], fill=255, width=lw, joint='curve')
            d.line([P(.5, .5), P(.5, .88)], fill=255, width=lw)
        elif name == 'text':
            f = E.font(int(n * .62), 700); d.text(P(.5, .52), 'Aa', font=f, fill=255, anchor='mm')
        elif name == 'motion':
            d.ellipse((*P(.44, .3), *P(.84, .7)), fill=255)
            for y, x0 in ((.36, .12), (.5, .06), (.64, .12)): d.line([P(x0, y), P(.36, y)], fill=255, width=lw)
        elif name == 'upscale':
            d.rounded_rectangle((*P(.1, .5), *P(.5, .9)), int(n * .05), outline=255, width=lw)
            d.line([P(.42, .58), P(.86, .14)], fill=255, width=lw)
            d.line([P(.56, .14), P(.86, .14), P(.86, .44)], fill=255, width=lw, joint='curve')
        elif name == 'avatar':
            d.ellipse((*P(.33, .1), *P(.67, .44)), fill=255)
            d.chord((*P(.12, .5), *P(.88, 1.26)), 180, 360, fill=255)
        elif name == 'knight':
            f = djfont(int(n * 1.02)); d.text(P(.5, .5), '♞', font=f, fill=255, anchor='mm')
        elif name == 'spark':
            def star(cx, cy, R, r):
                pts = []
                for k in range(16):
                    ang = k * math.pi / 8 - math.pi / 2
                    rr = R if k % 4 == 0 else (r if k % 2 == 1 else r * .62)
                    pts.append(P(cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
                d.polygon(pts, fill=255)
            star(.44, .54, .42, .1); star(.8, .2, .14, .035); star(.82, .82, .09, .024)
        elif name == 'gem':
            top = [P(.24, .18), P(.76, .18), P(.94, .38), P(.5, .9), P(.06, .38)]
            d.polygon(top, fill=255)
        elif name == 'plus':
            d.line([P(.5, .2), P(.5, .8)], fill=255, width=lw); d.line([P(.2, .5), P(.8, .5)], fill=255, width=lw)
        elif name == 'check':
            d.line([P(.18, .54), P(.42, .76), P(.84, .26)], fill=255, width=int(n * .13), joint='curve')
            for p in (P(.18, .54), P(.84, .26)): d.ellipse((p[0] - n * .065, p[1] - n * .065, p[0] + n * .065, p[1] + n * .065), fill=255)
        mm = m.resize((s, s), Image.LANCZOS)
        return colorize(mm, col) if isinstance(col, tuple) else colorize(mm, grad_img(s, s, col, .25))
    return C(('icon', name, s, col if isinstance(col, tuple) else 'grad', stroke), mk)


def gem_icon(s=170):
    """faceted gem: crown + pavilion, facets in graded lilac/white (premium 'bom gosto')."""
    def mk():
        S = 4; n = s * S; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        def P(x, y): return (x * n, y * n)
        tl, tr, r_, l_, b_ = P(.24, .2), P(.76, .2), P(.95, .4), P(.05, .4), P(.5, .92)
        m1, m2 = P(.4, .2), P(.6, .2)
        g1, g2, g3 = P(.32, .4), P(.5, .4), P(.68, .4)
        cols = [(250, 248, 255), (214, 204, 255), (176, 160, 255), (140, 130, 255), (120, 100, 250), (196, 170, 255), (160, 120, 255)]
        d.polygon([tl, m1, g1, l_], fill=cols[1] + (255,))
        d.polygon([m1, m2, g2], fill=cols[0] + (255,))
        d.polygon([m1, g2, g1], fill=cols[2] + (255,))
        d.polygon([m2, g3, g2], fill=cols[1] + (255,))
        d.polygon([m2, tr, r_, g3], fill=cols[3] + (255,))
        d.polygon([l_, g1, b_], fill=cols[5] + (255,))
        d.polygon([g1, g2, b_], fill=cols[2] + (255,))
        d.polygon([g2, g3, b_], fill=cols[4] + (255,))
        d.polygon([g3, r_, b_], fill=cols[6] + (255,))
        lw = int(n * .012)
        for a_, b2 in ((tl, tr), (tr, r_), (r_, b_), (b_, l_), (l_, tl), (l_, r_), (m1, g1), (m1, g2), (m2, g2), (m2, g3), (g1, b_), (g2, b_), (g3, b_)):
            d.line([a_, b2], fill=(255, 255, 255, 150), width=lw)
        return im.resize((s, s), Image.LANCZOS)
    return C(('gem', s), mk)


def icon_glow(img, blur=16, col=(120, 90, 255), gain=1.6):
    def mk():
        pad = int(blur * 2.5); a = img.getchannel('A')
        g = glow_of(a, col, blur, gain, pad); g.alpha_composite(img, (pad, pad)); return g
    return C(('iglow', id(img), blur, col, gain), mk)


# ---------------------------------------------------------------- giant brand type (behind him)
def giant(text, size, wght=900, style='grad'):
    """big display word: brand gradient (top-bright), a thin light top edge, a dark separation halo and a purple glow.
    Returns (img, pad)."""
    def mk():
        f = E.font(size, wght); l, t, r, b = f.getbbox(text); pad = int(size * .32)
        w, h = r - l + 2 * pad, b - t + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        out.alpha_composite(colorize(m.filter(ImageFilter.GaussianBlur(size * .09)).point(lambda v: int(v * .75)), (4, 3, 12)), (0, int(size * .04)))
        out.alpha_composite(colorize(m.filter(ImageFilter.GaussianBlur(size * .2)).point(lambda v: int(v * .55)), (110, 80, 255)))
        if style == 'grad':
            g = np.asarray(E.gradient(w, h, GRAD_L), np.float32)
            v = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
            g = g * (1.18 - .38 * v) + 18
            fill = colorize(m, Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)))
        else:
            fill = colorize(m, WHITE)
        out.alpha_composite(fill)
        # light top edge (inner highlight): mask minus mask shifted down
        sh = ImageChops.subtract(m, ImageChops.offset(m, 0, max(2, size // 70)))
        out.alpha_composite(colorize(sh.point(lambda v: int(v * .7)), (255, 255, 255)))
        return out, pad
    return C(('giant', text, size, wght, style), mk)


# ---------------------------------------------------------------- the cartoon weight
def weight_img(w=270):
    """cast-iron cartoon weight with a ring handle, engraved PESADO (the caption word as kinetic type)."""
    def mk():
        S = 3; n = w * S; h = int(n * .92); im = Image.new('RGBA', (n, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        # handle ring
        hr = int(n * .17); cx = n // 2; hy = int(h * .2)
        d.ellipse((cx - hr, hy - hr, cx + hr, hy + hr), outline=(78, 78, 94, 255), width=int(n * .065))
        d.arc((cx - hr, hy - hr, cx + hr, hy + hr), 200, 320, fill=(130, 130, 150, 255), width=int(n * .02))
        # body (trapezoid with rounded top corners)
        top, bot = int(h * .3), h - 4
        body = Image.new('L', (n, h)); bd = ImageDraw.Draw(body)
        bd.polygon([(n * .22, top), (n * .78, top), (n * .98, bot), (n * .02, bot)], fill=255)
        body = body.filter(ImageFilter.GaussianBlur(S * 3)).point(lambda v: 255 if v > 128 else 0)
        yy, xx = np.mgrid[0:h, 0:n].astype(np.float32)
        base = 52 + 34 * np.clip(1 - (yy - top) / (bot - top), 0, 1) + 34 * np.exp(-((xx - n * .36) / (n * .12)) ** 2) * np.clip(1 - (yy - top) / (bot - top) * .7, 0, 1)
        rgb = np.dstack([base, base * .98, base * 1.12])
        body_im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA'); body_im.putalpha(body)
        im.alpha_composite(body_im)
        # rim light (lilac, right edge) + bottom shadow band
        edge = ImageChops.subtract(body, ImageChops.offset(body, -S * 6, 0))
        im.alpha_composite(colorize(edge, (180, 160, 255)))
        edge_l = ImageChops.subtract(body, ImageChops.offset(body, S * 4, 0))          # cool kicker on the left edge
        im.alpha_composite(colorize(edge_l.point(lambda v: int(v * .55)), (200, 205, 235)))
        top_edge = ImageChops.subtract(body, ImageChops.offset(body, 0, S * 3))
        im.alpha_composite(colorize(top_edge.point(lambda v: int(v * .55)), (210, 210, 230)))
        # engraved label
        f = E.font(int(n * .17), 900); txt = 'PESADO'
        tm = Image.new('L', (n, h)); ImageDraw.Draw(tm).text((n / 2, top + (bot - top) * .56), txt, font=f, fill=255, anchor='mm')
        im.alpha_composite(colorize(ImageChops.offset(tm, 0, S * 2).point(lambda v: int(v * .6)), (0, 0, 0)))
        im.alpha_composite(colorize(tm, grad_img(n, h, GRAD_L, .2)))
        return im.resize((w, int(h / S)), Image.LANCZOS)
    return C(('weight', w), mk)


# ---------------------------------------------------------------- reticle / check / cursor
def brackets(w, h, L=46, lw=6, col=(250, 249, 255), a=1.0):
    """four corner brackets around a w x h box (RGBA, centred)."""
    def mk():
        pad = 30; im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        x0, y0, x1, y1 = pad, pad, pad + w, pad + h
        for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line([(cx, cy + sy * L), (cx, cy), (cx + sx * L, cy)], fill=col + (int(255 * a),), width=lw, joint='curve')
        g = im.getchannel('A').filter(ImageFilter.GaussianBlur(8))
        out = colorize(g.point(lambda v: int(v * .8)), (120, 100, 255)); out.alpha_composite(im); return out
    return C(('brk', int(w), int(h), L, lw, col, round(a, 2)), mk)


def big_check(s=420):
    """the gradient check stamp: thick rounded check in the brand gradient + inner highlight + glow (RGBA, pad)."""
    def mk():
        S = 3; n = s * S; m = Image.new('L', (n, n)); d = ImageDraw.Draw(m)
        pts = [(n * .16, n * .55), (n * .41, n * .78), (n * .86, n * .24)]; lw = int(n * .15)
        d.line(pts, fill=255, width=lw, joint='curve')
        for p in (pts[0], pts[2]): d.ellipse((p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2), fill=255)
        m = m.resize((s, s), Image.LANCZOS); pad = int(s * .3)
        out = Image.new('RGBA', (s + 2 * pad, s + 2 * pad), (0, 0, 0, 0))
        mp = Image.new('L', out.size); mp.paste(m, (pad, pad))
        out.alpha_composite(colorize(mp.filter(ImageFilter.GaussianBlur(s * .09)).point(lambda v: int(v * .7)), (4, 2, 14)), (0, int(s * .03)))
        out.alpha_composite(colorize(mp.filter(ImageFilter.GaussianBlur(s * .12)).point(lambda v: int(min(255, v * 1.3))), (120, 90, 255)))
        g = np.asarray(E.gradient(out.width, out.height, GRAD_L), np.float32)
        v = np.linspace(0, 1, out.height, dtype=np.float32)[:, None, None]; g = np.clip(g * (1.2 - .35 * v) + 10, 0, 255)
        out.alpha_composite(colorize(mp, Image.fromarray(g.astype(np.uint8))))
        hi = ImageChops.subtract(mp, ImageChops.offset(mp, 0, max(2, s // 60)))
        out.alpha_composite(colorize(hi.point(lambda v: int(v * .8)), (255, 255, 255)))
        return out
    return C(('bigcheck', s), mk)


def cursor(s=64):
    """pointer arrow (white, dark outline, soft shadow)."""
    def mk():
        S = 4; n = s * S; im = Image.new('RGBA', (n + 40 * S // 4, n + 40 * S // 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = [(.1, .04), (.1, .82), (.3, .64), (.44, .96), (.58, .9), (.45, .58), (.72, .58)]
        P = [(x * n + 10, y * n + 10) for x, y in pts]
        shadow = Image.new('L', im.size); ImageDraw.Draw(shadow).polygon([(x + 10, y + 16) for x, y in P], fill=150)
        im.alpha_composite(colorize(shadow.filter(ImageFilter.GaussianBlur(12)), (0, 0, 0)))
        d.polygon(P, fill=(250, 249, 255, 255), outline=(14, 12, 24, 255), width=int(n * .045))
        return im.resize((im.width // S, im.height // S), Image.LANCZOS)
    return C(('cursor', s), mk)
