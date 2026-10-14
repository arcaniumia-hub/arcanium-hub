"""Kit for s08_resultado / s09_twist / s10_cta (author F).  Read-only for other authors.

    captions on measured onsets (engine look)      caps_layer(ctx, t, pages, y)
    display type (gradient / white, glyph mask)    display(text, size, wght, style) -> (RGBA, mask float32)
    light sheen through glyphs                     sheen(img, k, mask, half, strength)
    3-D cards (homography, AA edges)               cam_quad(...), warp(img, quad) -> (RGBA, x0, y0)
    LUMARC portfolio stills / film frames          grab(path, t, w), cover(img, w, h), tile(name, w, h)
    frames of THIS film without captions           film_frame(t) (disk cache keyed by the other sections' source)
    VHS look                                       vhs(img, t, k)
    icons: phone handset, package, check, clock, tag, chevron
"""
import math, os, re, glob, hashlib, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E

W, H = E.W, E.H
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
CACHE = os.path.join(E.HERE, 'out', 'F', 'cache'); os.makedirs(CACHE, exist_ok=True)


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def C(k, fn): return E.cached(('F',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def bump(u, d=.16):
    """0 -> 1 -> 0 pop envelope (fast attack at u=0, damped by d)."""
    if u < 0 or u > d * 3: return 0.0
    return math.sin(min(1.0, u / (d * .35)) * math.pi / 2) * math.exp(-max(0, u - d * .35) / (d * .55))
def shake(t, t0, amp, tau=.12, f=19., seed=0.):
    u = t - t0
    if u < 0 or u > tau * 6: return 0.0, 0.0
    e = amp * math.exp(-u / tau)
    return e * math.sin(u * f * 6.283 + seed), e * .7 * math.cos(u * f * 5.1 + seed * 2.3)


def scale_im(im, s, lanczos=False):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.LANCZOS if lanczos else Image.BILINEAR)


def fade(im, k):
    if k >= .999: return im
    out = im.copy(); out.putalpha(im.getchannel('A').point(lambda v: int(v * max(0., k)))); return out


def paste(base, im, x, y, center=True, alpha=1.0):
    if im is None or alpha <= .01: return
    if alpha < .999: im = fade(im, alpha)
    if center: x, y = x - im.width / 2, y - im.height / 2
    E._paste(base, dict(img=im, xy=(int(round(x)), int(round(y))), glass=0))


def rotated(im, deg):
    if abs(deg) < .05: return im
    return im.rotate(deg, Image.BICUBIC, expand=True)


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


def caption_sprites(t, pages, base=92):
    """[(img, dx, dy)] visible at t. pages: [(a, z, [(text, t0, emph), ...])] — same pop as the engine captions."""
    out = []
    for a, z, words in pages:
        if not (a <= t < z): continue
        for (text, t0, emph, sz, _w), cx, cy in _layout(words, base):
            if t < t0 - .02: continue
            lt = t - t0 + .02; s = .72 + .28 * back(lt / .16, 1.4)
            img, _ = E.word_img(text, sz, 'grad' if emph else 'white')
            if lt < .05: img = fade(img, lt / .05)
            if z - t < .06: img = fade(img, (z - t) / .06)
            out.append((scale_im(img, s), cx, cy))
    return out


def caps_layer(ctx, t, pages, x=540, y=1420, base=92, alpha=1.0, layer='screen'):
    for img, dx, dy in caption_sprites(t, pages, base):
        ctx.add(layer, img, x + dx, y + dy, alpha=alpha)


# ---------------------------------------------------------------- display type
def display(text, size, wght=900, style='grad', glow=.5, shadow=.8, track=0, cols=None):
    """big display word: gradient (LUMARC light) or white, soft violet glow + shadow. -> (RGBA, glyph mask float32 0..1)"""
    def mk():
        f = E.font(size, wght); pad = int(size * .42)
        if track:
            ws = [f.getbbox(ch) for ch in text]; adv = [f.getlength(ch) for ch in text]
            tw = int(sum(adv) + track * (len(text) - 1)); _, t, _, b = f.getbbox('HÉgy')
        else:
            l, t, r, b = f.getbbox(text); tw = r - l; _, t, _, b = f.getbbox(text + 'H')
        w, h = tw + 2 * pad, (b - t) + 2 * pad
        m = Image.new('L', (w, h)); d = ImageDraw.Draw(m)
        if track:
            x = pad
            for ch, a in zip(text, adv): d.text((x, pad - t), ch, font=f, fill=255); x += a + track
        else:
            l = f.getbbox(text)[0]; d.text((pad - l, pad - t), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        if shadow:
            sh = Image.new('RGBA', (w, h), (4, 2, 14, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(size * .09)).point(lambda v: int(v * shadow)))
            out.alpha_composite(sh, (0, int(size * .04)))
        if style == 'grad':
            g = E.gradient(w, h, cols or E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
            if glow:
                gl = Image.new('RGBA', (w, h), (120, 90, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(size * .16)).point(lambda v: int(v * glow)))
                out.alpha_composite(gl)
            out.alpha_composite(g)
        else:
            col = E.WHITE if style == 'white' else style
            if glow:
                gl = Image.new('RGBA', (w, h), (140, 120, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(size * .16)).point(lambda v: int(v * glow * .6)))
                out.alpha_composite(gl)
            c = Image.new('RGBA', (w, h), col + (0,)); c.putalpha(m); out.alpha_composite(c)
        return out, np.asarray(m, np.float32) / 255
    return C(('disp', text, size, wght, str(style), glow, shadow, track, str(cols)), mk)


def sheen(img, k, mask, half=30, strength=.55, slope=.35):
    """narrow diagonal light band that brightens ONLY the glyphs (mask = bare glyph alpha 0..1, same size as img)."""
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


def text_line(text, size, wght=600, col=E.WHITE, shadow=.7):
    def mk():
        f = E.font(size, wght); l, t, r, b = f.getbbox(text); _, t2, _, b2 = f.getbbox('Hgy')
        pad = int(size * .4); w, h = r - l + 2 * pad, b2 - t2 + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t2), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        if shadow:
            sh = Image.new('RGBA', (w, h), (4, 2, 12, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(size * .12)).point(lambda v: int(v * shadow)))
            out.alpha_composite(sh, (0, 2))
        c = Image.new('RGBA', (w, h), col + (0,)); c.putalpha(m); out.alpha_composite(c)
        return out
    return C(('tl', text, size, wght, col, shadow), mk)


# ---------------------------------------------------------------- light
def glow_sprite(w, h, col, blur, a=1.0):
    def mk():
        pad = int(blur * 2.5); m = Image.new('L', (int(w) + 2 * pad, int(h) + 2 * pad))
        ImageDraw.Draw(m).ellipse((pad, pad, pad + w, pad + h), fill=int(255 * a))
        im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); return im
    return C(('glow', int(w), int(h), col, blur, a), mk)


def add_light(fr, glow, x, y, k=1.0):
    """additive light: glow sprite (colour x alpha) added onto fr centred at (x, y). Returns RGBA."""
    if k <= .01: return fr
    base = fr.convert('RGB'); L = Image.new('RGB', base.size, (0, 0, 0))
    a = glow.getchannel('A').point(lambda v: int(v * min(1.0, k)))
    col = Image.new('RGB', glow.size, glow.getpixel((glow.width // 2, glow.height // 2))[:3])
    L.paste(col, (int(x - glow.width / 2), int(y - glow.height / 2)), a)
    return ImageChops.add(base, L).convert('RGBA')


def add_field(fr, field, k, x0=0, y0=0):
    """additive float32 field (h, w, 3) at offset."""
    if k <= .01: return fr
    a = np.asarray(fr.convert('RGB'), np.float32); h, w = field.shape[:2]
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe > xs and ye > ys: a[ys:ye, xs:xe] += field[ys - y0:ye - y0, xs - x0:xe - x0] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def _smear(img, L, axis):
    """box motion blur of length L px along axis (edge-clamped, continuous: no stroboscopic copies)."""
    if abs(L) < 1.5: return img
    from scipy.ndimage import uniform_filter1d
    mode = img.mode; a = np.asarray(img, np.float32)
    a = uniform_filter1d(a, int(round(abs(L))) + 1, axis=axis, mode='nearest')
    return Image.fromarray(np.clip(a + .5, 0, 255).astype(np.uint8), mode)


def hsmear(img, L, n=None):
    """horizontal motion blur of length L px (edge-clamped)."""
    return _smear(img, L, 1)


def vsmear(img, L, n=None):
    return _smear(img, L, 0)


# ---------------------------------------------------------------- 3-D cards
def homography(src, dst):
    """coeffs for PIL PERSPECTIVE mapping output (dst) -> input (src)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def rot3(rx, ry, rz):
    """rotation matrix from degrees (applied X, then Y, then Z)."""
    rx, ry, rz = (math.radians(v) for v in (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]); Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


FOCAL = 2000.0


def project(P, f=FOCAL, vp=(540., 960.)):
    """camera-space points (N, 3) -> screen (N, 2). Z = f is the 1:1 plane."""
    P = np.asarray(P, float); z = np.maximum(P[:, 2], 1.0)
    return np.stack([vp[0] + f * P[:, 0] / z, vp[1] + f * P[:, 1] / z], 1)


def card_corners(w, h, R, T, s=1.0, local=(0., 0., 0.)):
    """camera-space corners of a w x h card (scaled s), first offset by `local` (in the rotated frame), rotated by R,
    then translated by T (the rotation pivot is at T)."""
    loc = np.array([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]], float) * s
    loc = loc + np.array(local, float)[None]
    return loc @ R.T + np.array(T, float)[None]


def warp(img, quad, pad=2, clip=(-200, -200, W + 200, H + 200)):
    """perspective-map img (RGBA) onto the screen quad [(x, y) TL, TR, BR, BL] -> (RGBA patch, x0, y0) or None.
    A transparent border gives anti-aliased card edges."""
    if pad:
        im = Image.new('RGBA', (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0)); im.paste(img.convert('RGBA'), (pad, pad))
    else: im = img.convert('RGBA')
    q = np.asarray(quad, float)
    x0, y0 = max(clip[0], int(math.floor(q[:, 0].min())) - 2), max(clip[1], int(math.floor(q[:, 1].min())) - 2)
    x1, y1 = min(clip[2], int(math.ceil(q[:, 0].max())) + 2), min(clip[3], int(math.ceil(q[:, 1].max())) + 2)
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    ex = pad * (q[1, 0] - q[0, 0]) / max(1, img.width)       # grow the quad by the pad (approx.)
    src = [(0, 0), (im.width, 0), (im.width, im.height), (0, im.height)]
    # quad of the padded image: extend the original quad outward by pad px in texture space
    def lerp2(a, b, k): return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
    pw, ph = img.width, img.height
    # bilinear extrapolation of the quad to the padded texture corners
    def at(u, v):
        top = lerp2(q[0], q[1], u); bot = lerp2(q[3], q[2], u); return lerp2(top, bot, v)
    du, dv = pad / pw, pad / ph
    dst = [at(-du, -dv), at(1 + du, -dv), at(1 + du, 1 + dv), at(-du, 1 + dv)]
    dst = [(x - x0, y - y0) for x, y in dst]
    try: co = homography(src, dst)
    except np.linalg.LinAlgError: return None
    out = im.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BILINEAR, fillcolor=(0, 0, 0, 0))
    return out, x0, y0


def put_warp(base, img, quad, alpha=1.0):
    r = warp(img, quad)
    if r is None: return
    p, x0, y0 = r
    if alpha < .999: p = fade(p, alpha)
    E._paste(base, dict(img=p, xy=(x0, y0), glass=0))


# ---------------------------------------------------------------- the LUMARC portfolio
def grab(path, t, w=540):
    """one frame of a video (nearest frame at/after t), width w (aspect kept), disk-cached jpg -> RGB."""
    key = hashlib.sha1(f'{path}|{t:.3f}|{w}'.encode()).hexdigest()[:16]
    def mk():
        p = os.path.join(CACHE, f'g_{key}.jpg')
        if not os.path.exists(p):
            tmp = p + f'.{os.getpid()}.jpg'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1', '-vf', f'scale={w}:-2',
                            '-q:v', '2', tmp], check=True)
            os.replace(tmp, p)
        return Image.open(p).convert('RGB')
    return C(('grab', key), mk)


def cover(img, w, h, ax=.5, ay=.5, z=1.0):
    """cover-fit crop of img to w x h (focus ax, ay; extra zoom z)."""
    sc = max(w / img.width, h / img.height) * z
    im = img.resize((max(w, int(img.width * sc + .5)), max(h, int(img.height * sc + .5))), Image.LANCZOS)
    x0 = int((im.width - w) * ax); y0 = int((im.height - h) * ay)
    return im.crop((x0, y0, x0 + w, y0 + h))


V = E.V
# name -> (loader, focus x, focus y, zoom)   (no prices, no delivery times, no people's captions in frame)
PORTFOLIO = {
    'hyper_ring':   (lambda: grab(E.HYPER, 7.8, 720), .5, .5, 1.0),      # gold light ring
    'hyper_gold':   (lambda: grab(E.HYPER, 8.4, 720), .5, .45, 1.0),     # "Introducing SILENCE ONE"
    'hyper_grid':   (lambda: grab(E.HYPER, 10.5, 720), .5, .5, 1.0),     # 4x4 product grid
    'hyper_noise':  (lambda: grab(E.HYPER, 12.0, 720), .5, .45, 1.0),    # TRAFFIC / NOISE type
    'hyper_orbit':  (lambda: grab(E.HYPER, 17.4, 720), .5, .5, 1.0),     # spatial audio rings
    'hyper_part':   (lambda: grab(E.HYPER, 22.8, 720), .5, .5, 1.0),     # particle headphones
    'hyper_leather': (lambda: grab(E.HYPER, 23.4, 720), .5, .5, 1.0),    # leather macro
    'hyper_feel':   (lambda: grab(E.HYPER, 25.8, 720), .5, .5, 1.0),     # "Hear nothing. Feel everything."
    'tear_feel':    (lambda: grab(E.TEARDOWN, 6.0, 720), .5, .5, 1.0),
    'tear_explode': (lambda: grab(E.TEARDOWN, 14.0, 720), .5, .5, 1.0),
    'croissant':    (lambda: E.img(os.path.join(E.THERAPY_A, 'croissant_hero.jpg')), .5, .5, 1.0),
    'oven':         (lambda: E.img(os.path.join(E.THERAPY_A, 'croissant_oven.jpg')), .5, .5, 1.0),
    'storefront':   (lambda: E.img(os.path.join(E.THERAPY_A, 'storefront_line.jpg')), .5, .3, 1.0),
    'carousel1':    (lambda: E.img(os.path.join(E.SHOWCASE_A, 'carousel_1.png')), .5, .5, 1.0),
    'carousel2':    (lambda: E.img(os.path.join(E.SHOWCASE_A, 'carousel_2.png')), .5, .5, 1.0),
    'burger':       (lambda: E.img(os.path.join(E.SHOWCASE_A, 'close_food.png')), .5, .45, 1.0),
    'latte':        (lambda: E.img(os.path.join(E.SHOWCASE_A, 'close_service.png')), .5, .45, 1.0),
    'watch':        (lambda: E.img(os.path.join(E.SHOWCASE_A, 'close_skill.png')), .5, .5, 1.0),
    'website':      (lambda: E.img(os.path.join(E.SHOWCASE_A, 'website.png')), .5, .5, 1.0),
    'casa_house':   (lambda: grab(E.FILMS['casa'], 39.6, 720), .5, .42, 1.35),    # the lit maquette (casa end card)
    'breakout_feed': (lambda: grab(E.FILMS['breakout'], 4.2, 720), .5, .5, 1.0),
    'breakout_touch': (lambda: grab(E.FILMS['breakout'], 14.7, 720), .5, .5, 1.0),
    'motion_logo':  (lambda: grab(E.MOTION3D, 8.0, 720), .5, .5, 1.0),
    'motion_ui':    (lambda: grab(E.MOTION3D, 14.0, 720), .5, .5, 1.0),
}


def tile(name, w, h):
    def mk():
        ld, ax, ay, z = PORTFOLIO[name]
        try: src = ld()
        except Exception: src = Image.new('RGB', (w, h), (30, 26, 50))
        return cover(src, w, h, ax, ay, z)
    return C(('tile', name, w, h), mk)


def card(img, radius=26, border=(255, 255, 255), border_a=.22, shadow_a=.0):
    """rounded photo card with a hairline light border (RGBA)."""
    im = E.rounded(img.convert('RGBA'), radius)
    d = Image.new('L', im.size); ImageDraw.Draw(d).rounded_rectangle((1, 1, im.width - 2, im.height - 2), radius, outline=255, width=2)
    b = Image.new('RGBA', im.size, border + (0,)); b.putalpha(d.point(lambda v: int(v * border_a))); im.alpha_composite(b)
    return im


# ---------------------------------------------------------------- frames of THIS film (for the rewind)
_MINE = ('s09_twist.py', 's10_cta.py')


def src_hash():
    def mk():
        h = hashlib.sha1()
        fs = sorted(glob.glob(os.path.join(E.HERE, 'sections', '*.py'))) + [os.path.join(E.HERE, f) for f in ('engine.py', 'timeline.py')]
        for f in fs:
            if os.path.basename(f) in _MINE: continue
            h.update(os.path.basename(f).encode()); h.update(open(f, 'rb').read())
        return h.hexdigest()[:12]
    return C('srchash', mk)


def film_frame(t, w=W):
    """frame t of this film rendered WITHOUT engine captions (a pure function of t and the other sections' code),
    disk-cached under out/F/cache.  Falls back to the keyed take over the studio if a section fails."""
    t = round(t * E.FPS) / E.FPS
    def mk():
        p = os.path.join(CACHE, f'rw_{src_hash()}_{t:07.3f}.jpg')
        if os.path.exists(p): return Image.open(p).convert('RGB')
        F = E.Film.__new__(E.Film); F.av = E.Avatar(t); F.sections = E.load_sections()
        orig = E.word_img
        def blank(text, size, style):              # every caption word (engine look, all kits) -> invisible
            im, pad = orig(text, size, style)
            return C(('blankw', im.size), lambda: Image.new('RGBA', im.size, (0, 0, 0, 0))), pad
        E.word_img = blank
        try:
            ctx = E.Ctx(t); ctx.compose = lambda cam=None, avatar=None: F.compose_world(ctx, cam, avatar)
            m = F.section_at(t)
            if m is not None: m.draw(ctx, t - m.START, t)
            fr = ctx.full.convert('RGBA') if ctx.full is not None else F.compose_world(ctx)
            if ctx.wrap is not None: fr = ctx.wrap(fr).convert('RGBA')
            for L in ctx.screen: E._paste(fr, L)
            out = E.post(fr.convert('RGB'), ctx.post, t)
        except Exception as ex:                         # a section in progress: keep the rewind alive
            ctx = E.Ctx(t); out = E.post(F.compose_world(ctx).convert('RGB'), ctx.post, t)
        finally:
            E.word_img = orig
            try: F.av.r.close()
            except Exception: pass
        tmp = p + f'.{os.getpid()}.jpg'; out.save(tmp, quality=93); os.replace(tmp, p)
        return out
    im = C(('ff', t, src_hash()), mk)
    return im if w == W else C(('ffs', t, w), lambda: im.resize((w, int(w * H / W)), Image.BILINEAR))


# ---------------------------------------------------------------- VHS
_vh_rng = np.random.default_rng(11)
_VH_NOISE = [_vh_rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(4)]
_VH_ROWN = [_vh_rng.normal(0, 1, H // 2).astype(np.float32) for _ in range(8)]


def vhs(img, t, k=1.0, band_y=None, band_h=90, jitter=1.0, chroma=1.0, smear=1.0):
    """VHS tape look on a full frame (computed at half res: tape is low-res).  band_y = centre of the tracking band
    (screen px, None = rolling).  Returns RGB 1080x1920."""
    if k <= .01: return img.convert('RGB')
    j = int(round(t * E.FPS))
    sm = img.convert('RGB').resize((W // 2, H // 2), Image.BILINEAR)
    a = np.asarray(sm, np.float32)
    h2, w2 = a.shape[:2]
    # luma / chroma (YIQ-ish)
    Y = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    I = a[..., 0] * .596 - a[..., 1] * .274 - a[..., 2] * .322
    Q = a[..., 0] * .211 - a[..., 1] * .523 + a[..., 2] * .312
    # chroma bleeds horizontally + shifted right
    from scipy.ndimage import uniform_filter1d
    I = uniform_filter1d(I, int(6 + 10 * smear * k), axis=1); Q = uniform_filter1d(Q, int(6 + 10 * smear * k), axis=1)
    sh = int(round(5 * chroma * k)); I = np.roll(I, sh, 1); Q = np.roll(Q, sh, 1)
    Y = uniform_filter1d(Y, 2, axis=1)
    # per-row horizontal jitter + the tracking band
    rows = _VH_ROWN[j % 8] * 1.2 * jitter * k
    if band_y is None: band_y = (H * (.15 + 1.1 * ((t * .9) % 1.0)))
    by = band_y / 2; bh = band_h / 2
    yy = np.arange(h2, dtype=np.float32)
    band = np.exp(-((yy - by) / bh) ** 2)
    rows = rows + band * (14 + 10 * _VH_ROWN[(j + 3) % 8]) * k
    idx = (np.arange(w2)[None, :] - rows[:, None].astype(np.int32)) % w2
    ri = np.arange(h2)[:, None]
    Y = Y[ri, idx]; I = I[ri, idx]; Q = Q[ri, idx]
    # the band is noisy + bright
    nz = _VH_NOISE[j % 4]
    Y = Y + nz * (6 + 70 * band[:, None]) * k + band[:, None] * 30 * k
    # scanlines + lifted blacks + softened contrast
    Y = Y * (1 - .10 * k * (np.arange(h2) % 2)[:, None]) * (1 - .06 * k) + 10 * k
    r = Y + .956 * I + .621 * Q; g = Y - .272 * I - .647 * Q; b = Y - 1.106 * I + 1.703 * Q
    o = np.stack([r, g, b], -1)
    o = a + (o - a) * k
    out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return out


def vhs_osd(text, size=64, tri=None):
    """VHS on-screen display text (white, soft bloom), optional triangle glyphs: tri = 'rew' | 'ff' | 'play' | None."""
    def mk():
        f = E.font(size, 700); l, t, r, b = f.getbbox(text); _, t2, _, b2 = f.getbbox('H')
        gw = int(size * 1.35) if tri else 0; pad = 24
        w, h = r - l + gw + 2 * pad + (int(size * .3) if tri else 0), int(size * 1.0) + 2 * pad
        m = Image.new('L', (w, h)); d = ImageDraw.Draw(m)
        cy = h / 2; s = size * .42
        if tri == 'rew':
            for k in range(2):
                x = pad + k * s * 1.25
                d.polygon([(x, cy), (x + s * 1.25, cy - s), (x + s * 1.25, cy + s)], fill=255)
        elif tri == 'ff':
            for k in range(2):
                x = pad + k * s * 1.25
                d.polygon([(x + s * 1.25, cy), (x, cy - s), (x, cy + s)], fill=255)
        elif tri == 'play':
            d.polygon([(pad + s * 1.4, cy), (pad, cy - s), (pad, cy + s)], fill=255)
        d.text((pad + gw + (int(size * .3) if tri else 0) - l, cy - (t2 + b2) / 2), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        g = Image.new('RGBA', (w, h), (200, 220, 255, 0)); g.putalpha(m.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * .6)))
        out.alpha_composite(g)
        c = Image.new('RGBA', (w, h), (245, 245, 250, 0)); c.putalpha(m); out.alpha_composite(c)
        return out
    return C(('osd', text, size, tri), mk)


# ---------------------------------------------------------------- icons (drawn at 4x, downsampled)
def _ss(size, fn, col=E.WHITE):
    S = 4; m = Image.new('L', (size * S, size * S)); fn(ImageDraw.Draw(m), size * S)
    m = m.resize((size, size), Image.LANCZOS)
    im = Image.new('RGBA', (size, size), col + (0,)); im.putalpha(m); return im


_PHONE_PATH = ("M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83"
               "l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99"
               " 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z")    # handset glyph (24 x 24 box)


def path_pts(p, n=14):
    """SVG path (M/L/H/V/C, absolute + relative, Z) -> polygon points (cubics sampled)."""
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
    """classic handset glyph."""
    def mk():
        pts = path_pts(_PHONE_PATH)
        def f(d, s): d.polygon([(x / 24 * s, y / 24 * s) for x, y in pts], fill=255)
        return _ss(size, f, col)
    return C(('iphone', size, col), mk)


def icon_check(size=80, col=E.WHITE, w=.12):
    def mk():
        def f(d, s):
            d.line([(s * .2, s * .52), (s * .42, s * .74), (s * .82, s * .3)], fill=255, width=int(s * w), joint='curve')
            for x, y in ((s * .2, s * .52), (s * .82, s * .3)):
                r = s * w / 2; d.ellipse((x - r, y - r, x + r, y + r), fill=255)
        return _ss(size, f, col)
    return C(('icheck', size, col, w), mk)


def icon_box(size=96, col=E.WHITE):
    """delivery package (isometric box outline with tape)."""
    def mk():
        def f(d, s):
            lw = int(s * .07)
            top = [(s * .5, s * .12), (s * .88, s * .3), (s * .5, s * .48), (s * .12, s * .3)]
            d.polygon(top, outline=255, width=lw)
            d.line([top[3], (s * .12, s * .72), (s * .5, s * .9), (s * .88, s * .72), top[1]], fill=255, width=lw, joint='curve')
            d.line([top[2], (s * .5, s * .9)], fill=255, width=lw)
            d.line([(s * .31, s * .21), (s * .69, s * .39)], fill=255, width=int(lw * .8))
        return _ss(size, f, col)
    return C(('ibox', size, col), mk)


def clock_face(size=120, col=E.WHITE):
    """watch face: ring + 12 tick marks, no digits (hands drawn per frame by clock_hands)."""
    def mk():
        def f(d, s):
            c = s / 2; lw = int(s * .05)
            d.ellipse((lw, lw, s - lw, s - lw), outline=255, width=lw)
            for i in range(12):
                a = i * math.pi / 6; r0 = s * (.33 if i % 3 else .30); r1 = s * .40
                d.line([(c + r0 * math.cos(a), c + r0 * math.sin(a)), (c + r1 * math.cos(a), c + r1 * math.sin(a))], fill=255, width=int(s * (.035 if i % 3 else .05)))
        return _ss(size, f, col)
    return C(('iclock', size, col), mk)


def clock_hands(size, a_min, a_hr, col=E.WHITE, blur=0.0):
    S = 3; m = Image.new('L', (size * S, size * S)); d = ImageDraw.Draw(m); c = size * S / 2
    for ang, L, wd in ((a_hr, .22, .07), (a_min, .33, .045)):
        x, y = c + math.sin(ang) * L * size * S, c - math.cos(ang) * L * size * S
        d.line([(c, c), (x, y)], fill=255, width=int(wd * size * S)); r = wd * size * S / 2; d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    r = .06 * size * S; d.ellipse((c - r, c - r, c + r, c + r), fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    if blur > .3: m = m.filter(ImageFilter.GaussianBlur(blur))
    im = Image.new('RGBA', (size, size), col + (0,)); im.putalpha(m); return im


def chevron(size=90, col=E.WHITE, w=.16):
    def mk():
        def f(d, s):
            d.line([(s * .14, s * .3), (s * .5, s * .68), (s * .86, s * .3)], fill=255, width=int(s * w), joint='curve')
            for x, y in ((s * .14, s * .3), (s * .86, s * .3)):
                r = s * w / 2; d.ellipse((x - r, y - r, x + r, y + r), fill=255)
        return _ss(size, f, col)
    return C(('ichev', size, col, w), mk)


def grad_fill(mask_im, cols=None):
    """an RGBA image whose colour is the LUMARC gradient (left -> right) and alpha = mask_im's alpha."""
    g = E.gradient(mask_im.width, mask_im.height, cols or E.GRAD_LIGHT).convert('RGBA'); g.putalpha(mask_im.getchannel('A')); return g


def ring_sprite(R, w=3.0, a=1.0, col=(250, 250, 255)):
    def mk():
        S = int(2 * R + 4 * w + 8); yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); d = np.hypot(xx - S / 2, yy - S / 2)
        al = np.exp(-((d - R) / w) ** 2) * a
        return Image.fromarray(np.dstack([np.full((S, S, 3), col, np.float32), al * 255]).astype(np.uint8), 'RGBA')
    return C(('ring', int(R), w, a, col), mk)


def star(size=64):
    """anamorphic 4-ray glint (white RGBA)."""
    def mk():
        S = size; yy, xx = np.mgrid[-S:S + 1, -S:S + 1].astype(np.float32) / S
        r = np.hypot(xx, yy) + 1e-6
        a = np.exp(-(r / .07) ** 2) + .35 * np.exp(-(r / .22) ** 2)
        a += np.exp(-(np.abs(yy) / (.012 + .02 * np.abs(xx))) ** 2) * np.clip(1 - np.abs(xx), 0, 1) ** 2
        a += .6 * np.exp(-(np.abs(xx) / (.012 + .02 * np.abs(yy))) ** 2) * np.clip(1 - np.abs(yy) / .6, 0, 1) ** 2
        im = Image.new('RGBA', (2 * S + 1, 2 * S + 1), (255, 255, 255, 0)); im.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)))
        return im
    return C(('star', size), mk)
