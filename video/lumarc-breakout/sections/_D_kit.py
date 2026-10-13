"""_D_kit — private helpers for s07_twice + s08_remember (author D). Not a section (the loader only matches sNN_*.py).

  - easing, bump/kick, deterministic hash noise
  - true-perspective card warp (homography) + bbox-limited output, directional motion blur (smear)
  - additive light compositing, radial glow sprites, star glints
  - captions with hand-measured onsets (exactly the engine look) for a list of pages
  - HYPER film frames: sequential playback (E.clip) + a 10 fps disk cache for fast scrubbing (rewind)
"""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

W, H = E.W, E.H
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
CACHE_DIR = os.path.join(E.HERE, 'out', 'D', 'cache')


def C(k, fn): return E.cached(('Dkit',) + (k if isinstance(k, tuple) else (k,)), fn)
def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def expo_in(x): x = clamp(x); return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def cub(x): x = clamp(x); return 1 - (1 - x) ** 3
def quint(x): x = clamp(x); return 1 - (1 - x) ** 5
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def kick(x, tau=.12): return 0.0 if x < 0 else math.exp(-x / tau)
def bump(x, a, b):
    if x <= a or x >= b: return 0.0
    return math.sin(math.pi * (x - a) / (b - a)) ** 2
def spring(x, freq=2.0, damp=7.0):
    """0 -> 1 with a damped overshoot; x in seconds."""
    if x <= 0: return 0.0
    return 1 - math.exp(-damp * x) * math.cos(freq * math.pi * x)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0


# ---------------------------------------------------------------- perspective
def homography(src, dst):
    """coeffs for PIL PERSPECTIVE mapping output (dst) -> input (src)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def rot3(rx, ry, rz):
    rx, ry, rz = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def proj(pts, w, h, cx, cy, s=1., rx=0., ry=0., rz=0., f=2400.):
    """screen positions of card-local points [(x, y)] for a w x h card scaled s, centred (cx, cy), rotated (degrees;
    rx > 0 tips the top away, ry > 0 swings the right edge TOWARD the camera). Returns [(sx, sy)]."""
    R = rot3(-rx, ry, rz); out = []
    for x, y in pts:
        X, Y, Z = R @ np.array([(x - w / 2) * s, (y - h / 2) * s, 0.])
        k = f / max(1e-3, f + Z); out.append((cx + X * k, cy + Y * k))
    return out


def quad(w, h, cx, cy, s=1., rx=0., ry=0., rz=0., f=2400.):
    return proj([(0, 0), (w, 0), (w, h), (0, h)], w, h, cx, cy, s, rx, ry, rz, f)


def warp(src, q, bounds=(W, H), pad=2, margin=0):
    """map the whole of RGBA `src` onto quad q (TL TR BR BL) -> (img, x0, y0) cropped to the bbox, or None."""
    xs = [p[0] for p in q]; ys = [p[1] for p in q]
    x0, y0 = max(-margin, int(math.floor(min(xs))) - 2), max(-margin, int(math.floor(min(ys))) - 2)
    x1, y1 = min(bounds[0] + margin, int(math.ceil(max(xs))) + 2), min(bounds[1] + margin, int(math.ceil(max(ys))) + 2)
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    ew = max(math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]), math.hypot(q[2][0] - q[3][0], q[2][1] - q[3][1]))
    eh = max(math.hypot(q[3][0] - q[0][0], q[3][1] - q[0][1]), math.hypot(q[2][0] - q[1][0], q[2][1] - q[1][1]))
    sx_, sy_ = min(1.0, 1.4 * ew / src.width), min(1.0, 1.4 * eh / src.height)
    if sx_ < .9 or sy_ < .9:
        src = src.resize((max(4, int(src.width * sx_)), max(4, int(src.height * sy_))), Image.BILINEAR, reducing_gap=2.0)
    if src.mode != 'RGBA': src = src.convert('RGBA')
    if pad:
        s2 = Image.new('RGBA', (src.width + 2 * pad, src.height + 2 * pad), (0, 0, 0, 0)); s2.paste(src, (pad, pad)); src = s2
        sq = [(pad, pad), (src.width - pad, pad), (src.width - pad, src.height - pad), (pad, src.height - pad)]
    else:
        sq = [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)]
    dq = [(x - x0, y - y0) for x, y in q]
    co = homography(sq, dq)
    return src.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BILINEAR), x0, y0


# ---------------------------------------------------------------- image ops
def paste(base, img, x, y, alpha=1.0):
    if img is None or alpha <= .01: return
    if alpha < 1: img = E.fade(img, alpha)
    E._paste(base, dict(img=img, xy=(int(round(x)), int(round(y))), glass=0))


def fast_blur(img, r):
    if r < .45: return img
    if r < 3: return img.filter(ImageFilter.GaussianBlur(r))
    q = 2 if r < 8 else 3 if r < 16 else 4
    w, h = img.size
    sm = img.resize((max(2, w // q), max(2, h // q)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / q))
    return sm.resize((w, h), Image.BILINEAR)


def smear(img, dx, dy, n=None):
    """directional motion blur of an RGBA sprite over (dx, dy) (centred). Returns (img, ox, oy) offset of the new
    top-left relative to the input's top-left."""
    L = math.hypot(dx, dy)
    if L < 1.5: return img, 0, 0
    n = n or int(min(40, max(3, L / 1.6)))
    px, py = int(math.ceil(abs(dx) / 2)) + 1, int(math.ceil(abs(dy) / 2)) + 1
    a = np.asarray(img, np.float32).copy(); a[..., :3] *= a[..., 3:] / 255.
    acc = np.zeros((img.height + 2 * py, img.width + 2 * px, 4), np.float32)
    for i in range(n):
        f = i / (n - 1) - .5; ox, oy = int(round(px + dx * f)), int(round(py + dy * f))
        acc[oy:oy + img.height, ox:ox + img.width] += a
    acc /= n
    al = acc[..., 3:]; rgb = np.where(al > .5, acc[..., :3] * 255. / np.maximum(al, 1e-3), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al, 0, 255)]).astype(np.uint8), 'RGBA'), -px, -py


def smear_hq(img, dx, dy, max_n=36):
    """smoother directional blur for big displacements: works at half resolution with dense samples."""
    L = math.hypot(dx, dy)
    if L < 24: return smear(img, dx, dy)
    w, h = img.size
    sm = img.resize((max(2, w // 2), max(2, h // 2)), Image.BILINEAR)
    out, ox, oy = smear(sm, dx / 2, dy / 2, n=int(min(max_n, max(6, L / 3.2))))
    return out.resize((out.width * 2, out.height * 2), Image.BILINEAR), ox * 2, oy * 2


def vsmear(img, L):
    """vertical box motion blur (L px) of an RGBA image, premultiplied (cumsum)."""
    L = int(L)
    if L < 2: return img
    a = np.asarray(img, np.float32).copy(); a[..., :3] *= a[..., 3:] / 255.
    c = np.cumsum(np.pad(a, ((L, L), (0, 0), (0, 0))), 0)
    h = a.shape[0]; half = L // 2
    out = (c[L + half:L + half + h] - c[L - half - 1:L - half - 1 + h]) / (2 * half + 1)
    al = out[..., 3:]; rgb = np.where(al > .5, out[..., :3] * 255. / np.maximum(al, 1e-3), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al, 0, 255)]).astype(np.uint8), 'RGBA')


def grade(img, sat=1.0, bright=1.0, contrast=1.0, lift=0.0, tint=None):
    """colour ops on RGB/RGBA (alpha kept)."""
    a = np.asarray(img, np.float32); rgb = a[..., :3]
    if sat != 1: g = rgb.mean(2, keepdims=True); rgb = g + (rgb - g) * sat
    if contrast != 1: rgb = 128 + (rgb - 128) * contrast
    if bright != 1: rgb = rgb * bright
    if lift: rgb = rgb + lift
    if tint is not None: rgb = rgb * np.array(tint, np.float32)
    out = np.clip(rgb, 0, 255)
    if a.shape[2] == 4: out = np.dstack([out, a[..., 3:]])
    return Image.fromarray(out.astype(np.uint8), img.mode)


def add_light(base, img, x, y, gain=1.0):
    """screen-blend an RGBA light sprite onto base (RGBA or RGB) at top-left (x, y), in place."""
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(base.width, x + img.width), min(base.height, y + img.height)
    if x1 <= x0 or y1 <= y0: return
    reg = np.asarray(base.crop((x0, y0, x1, y1)), np.float32)
    sp = np.asarray(img.crop((x0 - x, y0 - y, x1 - x, y1 - y)), np.float32)
    add = np.clip(sp[..., :3] * (sp[..., 3:] / 255.) * gain, 0, 255)
    rgb = 255 - (255 - reg[..., :3]) * (255 - add) / 255.
    out = np.dstack([rgb, reg[..., 3:]]) if reg.shape[2] == 4 else rgb
    base.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), base.mode), (x0, y0))


def radial(size, col, power=2.0, alpha=1.0, sy=1.0):
    """soft radial glow sprite (RGBA size x int(size*sy))."""
    def mk():
        h = int(size * sy)
        yy, xx = np.mgrid[0:h, 0:size].astype(np.float32)
        r = np.hypot((xx - size / 2) / (size / 2), (yy - h / 2) / (h / 2))
        a = np.clip(1 - r, 0, 1) ** power * alpha
        im = Image.new('RGBA', (size, h), tuple(col) + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return C(('radial', size, tuple(col), power, alpha, sy), mk)


def star(size=64, rays=4, soft=1.0):
    def mk():
        S = size; yy, xx = np.mgrid[-S:S + 1, -S:S + 1].astype(np.float32) / S
        r = np.hypot(xx, yy) + 1e-6
        core = np.exp(-(r / (.07 * soft)) ** 2) + .35 * np.exp(-(r / (.22 * soft)) ** 2)
        ray = np.zeros_like(r); lines = max(1, rays // 2)
        for k in range(lines):
            a = math.pi * k / lines
            d = np.abs(xx * math.sin(a) - yy * math.cos(a)); along = np.abs(xx * math.cos(a) + yy * math.sin(a))
            ray += np.exp(-(d / (.012 + .02 * along)) ** 2) * np.clip(1 - along / 1.0, 0, 1) ** 2
        a = np.clip(core + ray * .9, 0, 1)
        im = Image.new('RGBA', (2 * S + 1, 2 * S + 1), (255, 255, 255, 0))
        im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return C(('star', size, rays, soft), mk)


def rounded_mask(w, h, r, ss=3):
    def mk():
        m = Image.new('L', (w * ss, h * ss)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
        return m.resize((w, h), Image.LANCZOS)
    return C(('rmask', w, h, r), mk)


def round_img(img, r):
    img = img.convert('RGBA'); m = rounded_mask(img.width, img.height, r)
    a = np.minimum(np.asarray(img.getchannel('A')), np.asarray(m)); img.putalpha(Image.fromarray(a)); return img


def cover(img, w, h, ay=.5, ax=.5):
    c = img.convert('RGB'); sc = max(w / c.width, h / c.height)
    c = c.resize((max(w, int(c.width * sc + .999)), max(h, int(c.height * sc + .999))), Image.LANCZOS)
    x0 = int((c.width - w) * ax); y0 = int((c.height - h) * ay)
    return c.crop((x0, y0, x0 + w, y0 + h))


def text_rgba(s, size, wght, col=(250, 249, 246), tracking=0, grad=None):
    """tight RGBA text image (optional letter tracking px, optional gradient fill)."""
    def mk():
        f = E.font(size, wght)
        if tracking:
            ws = [f.getlength(ch) for ch in s]; tw = int(sum(ws) + tracking * (len(s) - 1))
        else:
            tw = int(f.getlength(s))
        l, tp, r, b = f.getbbox(s); h_ = b - tp
        im = Image.new('L', (tw + 8, h_ + 8))
        d = ImageDraw.Draw(im)
        if tracking:
            x = 4
            for ch, w_ in zip(s, ws): d.text((x, 4 - tp), ch, font=f, fill=255); x += w_ + tracking
        else:
            d.text((4 - l, 4 - tp), s, font=f, fill=255)
        if grad:
            g = E.gradient(im.width, im.height, grad).convert('RGBA'); g.putalpha(im); return g
        out = Image.new('RGBA', im.size, tuple(col) + (0,)); out.putalpha(im); return out
    return C(('txt', s, size, wght, tuple(col), tracking, tuple(map(tuple, grad)) if grad else None), mk)


# ---------------------------------------------------------------- captions with measured onsets
def make_pages(spec, seg_end):
    """spec = [[(WORD, t0, emph), ...], ...] (one inner list per caption page) -> engine-style pages."""
    pages = []
    for g in spec:
        pages.append(dict(words=[dict(text=w, t0=t0, emph=e, seg=-1) for w, t0, e in g]))
    words = [w for p in pages for w in p['words']]
    for k, w in enumerate(words):
        nxt = words[k + 1]['t0'] if k + 1 < len(words) else w['t0'] + .5
        w['t1'] = max(w['t0'] + .06, nxt)
    for j, p in enumerate(pages):
        p['a'] = p['words'][0]['t0'] - .04
        p['z'] = pages[j + 1]['words'][0]['t0'] - .02 if j + 1 < len(pages) else seg_end
    return pages


def draw_caps(fr, t, pages, cy0, base=92, x0=None, alpha=1.0, zmax=None):
    """identical look to engine.draw_captions (word pop, gradient on emphasis) for the given pages."""
    cx0 = fr.width / 2 if x0 is None else x0
    for p in pages:
        z = p['z'] if zmax is None else min(p['z'], zmax)
        if not (p['a'] <= t < z): continue
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            a = alpha
            if lt < .05: a *= lt / .05
            if z - t < .06: a *= (z - t) / .06
            if a < 1: img = E.fade(img, max(0, a))
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            E._paste(fr, dict(img=img, xy=(int(cx0 + cx - img.width / 2), int(cy0 + cy - img.height / 2)), glass=0))


def caps_to_layers(ctx, t, pages, cy0, base=92, x0=None, alpha=1.0, zmax=None):
    """same as draw_caps but adds each word as a ctx 'screen' layer (drawn over the cards, like the engine captions)."""
    cx0 = W / 2 if x0 is None else x0
    for p in pages:
        z = p['z'] if zmax is None else min(p['z'], zmax)
        if not (p['a'] <= t < z): continue
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            a = alpha
            if lt < .05: a *= lt / .05
            if z - t < .06: a *= (z - t) / .06
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, cx0 + cx, cy0 + cy, alpha=max(0., a))


def caption_boxes(pages, base=92):
    """{word text: (cx, cy, w, h)} layout offsets of each word (relative to the caption centre)."""
    out = {}
    for p in pages:
        for w, sz, cx, cy in E._layout(p, base):
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            out[w['text']] = (cx, cy, img.width, img.height, sz)
    return out


# ---------------------------------------------------------------- HYPER frames
def hyper_play(src_t, size):
    """sequential playback frame of the SILENCE ONE hyper film (RGB, `size`)."""
    return E.clip(E.HYPER, size).at(src_t)


def fixed_frames(path, a, b, size):
    """frames of `path` between src a..b at the film fps, decoded ONCE from the fixed origin a (so a frame is a pure
    function of its source time, whatever chunk of the film is being rendered) -> list of RGB."""
    def mk():
        n = int(round((b - a) * E.FPS)) + 1
        r = E.Reader(path, a, b - a + .2, vf=f'fps={E.FPS},scale={size[0]}:{size[1]}')
        out = [r.get(i, size).copy() for i in range(n)]; r.close(); return out
    return C(('fixed', path, a, b, size), mk)


def fixed_at(path, a, b, size, src_t):
    fr = fixed_frames(path, a, b, size)
    return fr[int(round(clamp((src_t - a) / (b - a)) * (len(fr) - 1)))]


SCRUB_FPS = 10
def scrub_frames(a, b, size=(540, 960)):
    """frames of HYPER between src a..b at 10 fps, cached on disk (atomic, shared by parallel renders) -> list of RGB."""
    def mk():
        tag = f'hyper_{a:.1f}_{b:.1f}_{size[0]}x{size[1]}'
        d = os.path.join(CACHE_DIR, tag); n = int(round((b - a) * SCRUB_FPS)) + 1
        files = [os.path.join(d, f'{i:04d}.jpg') for i in range(n)]
        if not all(os.path.exists(f) for f in files):
            tmp = d + f'.{os.getpid()}.tmp'; os.makedirs(tmp, exist_ok=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-i', E.HYPER, '-t', f'{b - a + .05:.3f}',
                            '-vf', f'fps={SCRUB_FPS},scale={size[0]}:{size[1]}', '-q:v', '3', os.path.join(tmp, '%04d.jpg')], check=True)
            got = sorted(os.listdir(tmp))
            for i, g in enumerate(got): os.rename(os.path.join(tmp, g), os.path.join(tmp, f'{i:04d}.jpg'))
            try:
                if os.path.exists(d):
                    import shutil; shutil.rmtree(tmp, ignore_errors=True)
                else: os.replace(tmp, d)
            except OSError: pass
            files = [os.path.join(d, f'{i:04d}.jpg') for i in range(n)]
        return [Image.open(f).convert('RGB') if os.path.exists(f) else None for f in files]
    fr = C(('scrub', a, b, size), mk)
    last = None
    for i, f in enumerate(fr):
        if f is None: fr[i] = last
        else: last = f
    return fr


def scrub_at(src_t, a, b, size=(540, 960)):
    fr = scrub_frames(a, b, size)
    i = int(round((clamp((src_t - a) / (b - a))) * (len(fr) - 1)))
    return fr[i]
