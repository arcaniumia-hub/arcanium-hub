"""_C_kit — private helpers for s05_head + s06_touch (author C). Not a section (the loader only matches sNN_*.py).

  - easing, 3-D card projection + bbox-limited perspective warp (homography; mip prefilter, AA pad)
  - fast_blur / smear (motion blur of a sprite) / DOF helpers
  - key_rgba(): luminance + texture key of the SILENCE ONE headphone renders on black (removes the light streak behind it,
    keeps the dark cushions solid). Keys are cached on disk in out/C/cache (recomputed when missing).
  - film frames of the SILENCE ONE teardown film, orbit turntable cells, macro still
  - captions with hand-measured onsets (same look as the engine captions)
  - ripple (glass/liquid refraction rings), light_hit (exposure flash with bloom), touch ring, star glint
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy import ndimage as ndi
import engine as E

W, H = E.W, E.H
V = E.V
clamp, eout, ein = E.clamp, E.eout, E.ein
CACHE_DIR = os.path.join(E.HERE, 'out', 'C', 'cache')


def C(k, fn): return E.cached(('Ckit',) + (k if isinstance(k, tuple) else (k,)), fn)
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
    return 0.0 if x < 0 else math.exp(-x / tau)
def bump(x, a, b):
    """0 outside [a, b], smooth 0->1->0 inside."""
    if x <= a or x >= b: return 0.0
    return math.sin(math.pi * (x - a) / (b - a)) ** 2


# ---------------------------------------------------------------- 3-D
def rot3(rx, ry, rz):
    rx, ry, rz = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def proj_pts(pts, w, h, cx, cy, s, rx, ry, rz, f=2600.):
    """screen positions of canvas points `pts` [(x, y)] of a w x h card scaled s, centred (cx, cy), rotated rx/ry/rz (deg;
    rx > 0 tips the top AWAY from the camera), pinhole focal f. Returns [(sx, sy, depth)]."""
    R = rot3(-rx, ry, rz); out = []
    for x, y in pts:
        X, Y, Z = R @ np.array([(x - w / 2) * s, (y - h / 2) * s, 0.])
        k = f / max(1e-3, f + Z); out.append((cx + X * k, cy + Y * k, Z))
    return out


def quad(w, h, cx, cy, s, rx=0., ry=0., rz=0., f=2600.):
    return [(x, y) for x, y, _ in proj_pts([(0, 0), (w, 0), (w, h), (0, h)], w, h, cx, cy, s, rx, ry, rz, f)]


def homography(src, dst):
    """coeffs for PIL PERSPECTIVE mapping output (dst) -> input (src)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def warp(src, q, bounds=(W, H), pad=2, resample=Image.BILINEAR, margin=0):
    """projectively map the whole of `src` (RGBA) onto quad q (TL TR BR BL). Returns (img, x0, y0) cropped to the quad's
    bbox (clipped to `bounds` + margin) or None. Prefilters a minified source (cheap mip), AA edges via a clear pad."""
    xs = [p[0] for p in q]; ys = [p[1] for p in q]
    x0, y0 = max(-margin, int(math.floor(min(xs))) - 2), max(-margin, int(math.floor(min(ys))) - 2)
    x1, y1 = min(bounds[0] + margin, int(math.ceil(max(xs))) + 2), min(bounds[1] + margin, int(math.ceil(max(ys))) + 2)
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    ew = max(math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]), math.hypot(q[2][0] - q[3][0], q[2][1] - q[3][1]))
    eh = max(math.hypot(q[3][0] - q[0][0], q[3][1] - q[0][1]), math.hypot(q[2][0] - q[1][0], q[2][1] - q[1][1]))
    sx_, sy_ = min(1.0, 1.5 * ew / src.width), min(1.0, 1.5 * eh / src.height)
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
    return src.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, resample), x0, y0


def paste(base, img, x, y, alpha=1.0):
    """alpha-composite img at integer (x, y) with clipping."""
    if img is None or alpha <= .01: return
    if alpha < 1: img = E.fade(img, alpha)
    E._paste(base, dict(img=img, xy=(int(round(x)), int(round(y))), glass=0))


# ---------------------------------------------------------------- blur
def fast_blur(img, r):
    """gaussian blur; big radii are done at reduced resolution."""
    if r < .45: return img
    if r < 3: return img.filter(ImageFilter.GaussianBlur(r))
    q = 2 if r < 8 else 3 if r < 16 else 4
    w, h = img.size
    sm = img.resize((max(2, w // q), max(2, h // q)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / q))
    return sm.resize((w, h), Image.BILINEAR)


def pad_img(img, p):
    out = Image.new('RGBA', (img.width + 2 * p, img.height + 2 * p), (0, 0, 0, 0)); out.paste(img, (p, p)); return out


def smear(img, dx, dy, n=None):
    """directional motion blur of an RGBA sprite over a displacement (dx, dy) (centred: half before, half after).
    Long smears are accumulated at half resolution with enough taps to leave no visible steps.
    Returns (img, ox, oy): the new image and the offset of its top-left relative to the input's top-left."""
    L = math.hypot(dx, dy)
    if L < 1.5: return img, 0, 0
    q = 2 if L > 24 else 1
    src = img.resize((max(2, img.width // q), max(2, img.height // q)), Image.BILINEAR) if q > 1 else img
    ddx, ddy = dx / q, dy / q; Lq = L / q
    n = n or int(min(44, max(3, Lq / .9)))          # <= ~1 px per tap at the working res: no stepped ghost copies
    px, py = int(math.ceil(abs(ddx) / 2)) + 1, int(math.ceil(abs(ddy) / 2)) + 1
    a = np.asarray(src, np.float32); a[..., :3] *= a[..., 3:] / 255.
    acc = np.zeros((src.height + 2 * py, src.width + 2 * px, 4), np.float32)
    wts = np.sin(np.pi * (np.arange(n) + .5) / n) ** .7                 # soft (cosine-ish) shutter: no hard double edges
    for i in range(n):
        f = i / (n - 1) - .5; ox, oy = int(round(px + ddx * f)), int(round(py + ddy * f))
        acc[oy:oy + src.height, ox:ox + src.width] += a * wts[i]
    acc /= wts.sum()
    al = acc[..., 3:]; rgb = np.where(al > .5, acc[..., :3] * 255. / np.maximum(al, 1e-3), 0)
    out = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al, 0, 255)]).astype(np.uint8), 'RGBA')
    if q > 1: out = out.resize((out.width * q, out.height * q), Image.BILINEAR)
    return out, -px * q, -py * q


def multiply_alpha(img, k):
    if k >= .999: return img
    return E.fade(img, k)


def tint_rgba(img, bright=1.0, add=None, mul=None):
    """brightness / additive colour / per-channel multiply on an RGBA image (alpha kept)."""
    a = np.asarray(img, np.float32); rgb = a[..., :3]
    if mul is not None: rgb = rgb * np.array(mul, np.float32)
    if bright != 1: rgb = rgb * bright
    if add is not None: rgb = rgb + np.array(add, np.float32)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]).astype(np.uint8), 'RGBA')


# ---------------------------------------------------------------- disk cache (atomic, shared by parallel renders)
def disk_cached(name, fn):
    def mk():
        p = os.path.join(CACHE_DIR, name + '.png')
        if os.path.exists(p):
            try: return Image.open(p).convert('RGBA')
            except Exception: pass
        im = fn()
        try:
            os.makedirs(CACHE_DIR, exist_ok=True); tmp = p + f'.{os.getpid()}.tmp'
            im.save(tmp, format='PNG'); os.replace(tmp, p)
        except Exception: pass
        return im
    return C(('disk', name), mk)


# ---------------------------------------------------------------- headphone key
def key_rgba(rgb, hole_frac=.09):
    """SILENCE ONE render on black -> RGBA. Core = bright or textured pixels (fabric, leather, metal) closed into one
    body; everything else inside its convex hull that is not a big background hole (the headband arch) and is either
    near the core or textured is kept (smooth shaded cup shells); the soft light streak of the backdrop is dropped."""
    from scipy.spatial import ConvexHull
    a = np.asarray(rgb.convert('RGB'), np.float32)
    lum = a.max(2); h_, w_ = lum.shape
    m1 = ndi.uniform_filter(lum, 7); m2 = ndi.uniform_filter(lum * lum, 7)
    sd = np.sqrt(np.clip(m2 - m1 * m1, 0, None))
    core = (lum > 95) | ((sd > 5.0) & (lum > 10))
    core = ndi.binary_closing(core, structure=np.ones((3, 3)), iterations=8)
    lab, n = ndi.label(core)
    sizes = ndi.sum(core, lab, range(1, n + 1)); core = lab == (np.argmax(sizes) + 1)
    ys, xs = np.nonzero(core); pts = np.c_[xs, ys]
    hull = ConvexHull(pts); poly = [tuple(map(float, pts[i])) for i in hull.vertices]
    hm = Image.new('L', (w_, h_)); ImageDraw.Draw(hm).polygon(poly, fill=255)
    hullm = ndi.binary_dilation(np.asarray(hm) > 0, iterations=3)
    low = lum > 14; area = core.sum()
    holes = ndi.binary_fill_holes(core) & ~core; hl, hn = ndi.label(holes); big = np.zeros_like(core)
    if hn:
        hs = ndi.sum(holes, hl, range(1, hn + 1))
        big = np.isin(hl, [i + 1 for i, s_ in enumerate(hs) if s_ >= area * hole_frac])
    big = ndi.binary_erosion(big, iterations=2)
    near = ndi.distance_transform_edt(~core) < 6
    obj = core | (low & hullm & ~big & (near | (sd > 3.5)))
    holes = ndi.binary_fill_holes(obj) & ~obj; hl, hn = ndi.label(holes)
    if hn:
        hs = ndi.sum(holes, hl, range(1, hn + 1))
        obj |= np.isin(hl, [i + 1 for i, s_ in enumerate(hs) if s_ < area * hole_frac])
    obj = ndi.binary_opening(obj, iterations=1)
    lab, n = ndi.label(obj)
    if n > 1:
        sizes = ndi.sum(obj, lab, range(1, n + 1)); obj = lab == (np.argmax(sizes) + 1)
    obj = ndi.binary_erosion(obj, iterations=1)
    # alpha: a slightly eroded solid body + a luminance matte inside the hull for everything soft (shaded shells,
    # rim glow): black stays transparent (no dark fringe), dim parts are partly transparent but correctly coloured
    # (un-premultiplied), so the edge reads as light falling off rather than a cut-out outline.
    hard = ndi.gaussian_filter(ndi.binary_erosion(obj, iterations=2).astype(np.float32), 1.0)
    soft = np.clip((lum - 7) / 26, 0, 1) ** 1.2 * ndi.gaussian_filter(hullm.astype(np.float32), 2.0)
    soft = np.where(big, soft * .35, soft)
    al = np.maximum(hard, soft)
    un = np.clip(a / np.maximum(al, .08)[..., None], 0, 255)
    a = np.where((al < .999)[..., None], un, a)
    return Image.fromarray(np.dstack([np.clip(a, 0, 255), np.clip(al, 0, 1)[..., None] * 255]).astype(np.uint8), 'RGBA')


def bbox_crop(img, pad=6):
    bb = img.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    if not bb: return img, (0, 0)
    x0, y0, x1, y1 = max(0, bb[0] - pad), max(0, bb[1] - pad), min(img.width, bb[2] + pad), min(img.height, bb[3] + pad)
    return img.crop((x0, y0, x1, y1)), (x0, y0)


def film_src(s, fps=30):
    """snap a film source time for E.clip(...).at() so a fresh reader (chunk start / still) and a sequential one return
    the SAME frame: ffmpeg's input seek + fps filter duplicates the first frame when -ss sits in the first half of a
    frame interval (and '%.3f' rounding can push an on-grid time there), so seek 3/4 of the way into the interval."""
    return (math.floor(s * fps + 1e-6) + .75) / fps


def film_frame(path, src_t, size=(W, H)):
    """one frame of a film (exact seek, independent of the shared sequential readers)."""
    import subprocess
    p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{src_t:.3f}', '-i', path, '-frames:v', '1', '-vf',
                        f'scale={size[0]}:{size[1]}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    return Image.frombuffer('RGB', size, p.stdout[:size[0] * size[1] * 3], 'raw', 'RGB', 0, 1).copy()


FILM_KEY_T = 5.30           # teardown film: the hero shot the product breaks out of (keyed, full res)
def film_sprite():
    """the headphone of the teardown film's hero frame (src 5.30 s), keyed, as a full 1080x1920 RGBA layer (same
    coordinates as the film frame)."""
    return disk_cached('film_sprite_530', lambda: key_rgba(film_frame(E.TEARDOWN, FILM_KEY_T)))


ORBIT = os.path.join(V, 'silence-motion/img')
def orbit_cell(k):
    """turntable angle k (0..39: 3/4 view -> frontal), keyed RGBA 520x520 (object centred like the source cell)."""
    k = int(clamp(k, 0, 39)); sheet, i = divmod(k, 10)
    def mk():
        im = Image.open(os.path.join(ORBIT, f'orbit{sheet}.jpg')).convert('RGB')
        cx, cy = (i % 5) * 520, (i // 5) * 520
        return key_rgba(im.crop((cx, cy, cx + 520, cy + 520)))
    return disk_cached(f'orbit_{k:02d}', mk)


def hero_sprite():
    return disk_cached('hero', lambda: key_rgba(Image.open(os.path.join(ORBIT, 'hero.jpg'))))


def macro():
    return C('macro', lambda: Image.open(os.path.join(ORBIT, 'macro.jpg')).convert('RGB'))


# ---------------------------------------------------------------- captions with measured onsets
def caption_pages(seg_idx, fix):
    """the engine caption pages of segment `seg_idx`, with word onsets replaced by `fix` {(seg, WORD): t}."""
    pages = [dict(p, words=[dict(w) for w in p['words']]) for p in E.PAGES if p['seg'] == seg_idx]
    words = [w for p in pages for w in p['words']]
    for w in words:
        k = (w['seg'], w['text'])
        if k in fix: w['t0'] = fix[k]
    for k in range(len(words) - 1):
        words[k]['t1'] = max(words[k]['t0'] + .06, words[k + 1]['t0'])
    words[-1]['t1'] = max(words[-1]['t1'], words[-1]['t0'] + .25)
    for j, p in enumerate(pages):
        p['a'] = p['words'][0]['t0'] - .04
        p['z'] = pages[j + 1]['words'][0]['t0'] - .02 if j + 1 < len(pages) else E.TL[seg_idx]['t1'] + .2
    return pages


def draw_caps(fr, t, pages, cy0, base=92, x0=None, alpha=1.0):
    """same look as engine.draw_captions (word pop, gradient on emphasis) for the given pages."""
    cx0 = fr.width / 2 if x0 is None else x0
    for p in pages:
        if not (p['a'] <= t < p['z']): continue
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            a = alpha
            if lt < .05: a *= lt / .05
            if p['z'] - t < .06: a *= (p['z'] - t) / .06
            if a < 1: img = E.fade(img, max(0, a))
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            E._paste(fr, dict(img=img, xy=(int(cx0 + cx - img.width / 2), int(cy0 + cy - img.height / 2)), glass=0))


# ---------------------------------------------------------------- light
def light_hit(fr, k, col=(196, 182, 255)):
    """a flash that reads as LIGHT, not fog: exposure push + highlight bloom + faint tint, filmic shoulder."""
    rgb = fr.convert('RGB'); a = np.asarray(rgb, np.float32)
    sm = np.asarray(rgb.resize((W // 4, H // 4), Image.BILINEAR), np.float32)
    lum = sm.mean(2, keepdims=True); hb = sm * np.clip((lum - 80) / 110, 0, 1)
    bloom = np.asarray(Image.fromarray(hb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32)
    y = (a * (1 + 1.7 * k) + bloom * (2.4 * k) + np.array(col, np.float32) * (.20 * k)) / 255.
    y = np.where(y < .72, y, .72 + .28 * (1 - np.exp(-(y - .72) / .28)))
    return Image.fromarray(np.clip(y * 255, 0, 255).astype(np.uint8)).convert('RGBA')


def radial(size, col, power=2.0, alpha=1.0):
    """soft radial glow sprite (RGBA, size x size)."""
    def mk():
        yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
        r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
        a = np.clip(1 - r, 0, 1) ** power * alpha
        im = Image.new('RGBA', (size, size), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return C(('radial', size, col, power, alpha), mk)


def star(size=64, rays=4, soft=1.0):
    """anamorphic star glint (white RGBA): hot core + thin tapering rays."""
    def mk():
        S = size; yy, xx = np.mgrid[-S:S + 1, -S:S + 1].astype(np.float32) / S
        r = np.hypot(xx, yy) + 1e-6
        core = np.exp(-(r / (.07 * soft)) ** 2) + .35 * np.exp(-(r / (.22 * soft)) ** 2)
        ray = np.zeros_like(r); lines = max(1, rays // 2)
        for k in range(lines):
            a = math.pi * k / lines
            d = np.abs(xx * math.sin(a) - yy * math.cos(a)); along = np.abs(xx * math.cos(a) + yy * math.sin(a))
            L = 1.0 if (k % 2 == 0 or lines <= 2) else .55
            ray += np.exp(-(d / (.012 + .02 * along)) ** 2) * np.clip(1 - along / L, 0, 1) ** 2
        a = np.clip(core + ray * .9, 0, 1)
        im = Image.new('RGBA', (2 * S + 1, 2 * S + 1), (255, 255, 255, 0))
        im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return C(('star', size, rays, soft), mk)


def add_light(base, img, x, y, gain=1.0):
    """additive (screen blend) composite of an RGBA light sprite onto base (RGBA, opaque) at top-left (x, y), in place.
    C-speed: premultiply the sprite by its alpha (x gain), then ImageChops.screen over the covered region."""
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(base.width, x + img.width), min(base.height, y + img.height)
    if x1 <= x0 or y1 <= y0 or gain <= .003: return
    sp = img.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    a = sp.getchannel('A')
    if gain != 1: a = a.point(lambda v, g=gain: min(255, int(v * g + .5)))
    pm = ImageChops.multiply(sp.convert('RGB'), Image.merge('RGB', (a, a, a)))
    reg = base.crop((x0, y0, x1, y1))
    out = ImageChops.screen(reg.convert('RGB'), pm)
    if reg.mode == 'RGBA': out.putalpha(reg.getchannel('A'))
    base.paste(out, (x0, y0))


# ---------------------------------------------------------------- touch
def touch_ring(ss=4):
    """soft touch indicator: hairline white ring + faint fill + whisper of shadow (200x200 RGBA)."""
    def mk():
        S, r, w = 200, 62, 5
        m = Image.new('L', (S * ss, S * ss)); d = ImageDraw.Draw(m)
        d.ellipse(((S / 2 - r) * ss, (S / 2 - r) * ss, (S / 2 + r) * ss, (S / 2 + r) * ss), fill=46)
        d.ellipse(((S / 2 - r) * ss, (S / 2 - r) * ss, (S / 2 + r) * ss, (S / 2 + r) * ss), outline=190, width=w * ss)
        m = m.resize((S, S), Image.LANCZOS)
        im = Image.new('RGBA', (S, S), (255, 255, 255, 0)); im.putalpha(m)
        sh = Image.new('RGBA', (S, S), (0, 0, 10, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .4)))
        out = Image.new('RGBA', (S, S), (0, 0, 0, 0)); out.alpha_composite(sh, (0, 4)); out.alpha_composite(im); return out
    return C('touch_ring', mk)


def ring_line(size, width_px, col=(255, 255, 255), alpha=200, ss=3):
    def mk():
        m = Image.new('L', (size * ss, size * ss))
        ImageDraw.Draw(m).ellipse((width_px * ss, width_px * ss, (size - width_px) * ss, (size - width_px) * ss), outline=alpha, width=width_px * ss)
        im = Image.new('RGBA', (size, size), col + (0,)); im.putalpha(m.resize((size, size), Image.LANCZOS)); return im
    return C(('ringline', size, width_px, col, alpha), mk)


def ripple(img, cx, cy, e, amp=9.0, speed=900., width=46., q=2, ay=1.0, hl_gain=70., r0=30., decay=.32, rings=((1.0, 1.0), (.6, .5)), trough=.35):
    """refraction rings expanding from (cx, cy), e = seconds since the touch. Leading crest + weaker inner rings;
    caustic highlight on the crests, soft shade in the troughs. Only the disc the wave has reached is processed.
    Returns RGB."""
    if e < 0: return img
    from scipy.ndimage import map_coordinates
    R = r0 + speed * e; env = min(1., e / .03) * math.exp(-e / decay)
    if env < .01: return img.convert('RGB')
    w, h = img.size; ext = R + 3 * width
    X0, Y0 = max(0, int(cx - ext)), max(0, int(cy - ext * ay)); X1, Y1 = min(w, int(cx + ext)), min(h, int(cy + ext * ay))
    if X1 - X0 < 8 or Y1 - Y0 < 8: return img.convert('RGB')
    base = img.convert('RGB'); crop = base.crop((X0, Y0, X1, Y1))
    cw, ch = crop.size; sw, sh = max(2, cw // q), max(2, ch // q)
    small = np.asarray(crop.resize((sw, sh), Image.BILINEAR) if q > 1 else crop, np.float32)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    dx, dy = xx - (cx - X0) / q, (yy - (cy - Y0) / q) / ay; r = np.sqrt(dx * dx + dy * dy) + 1e-3
    Rq = R / q; wd = width / q
    wave = np.zeros_like(r)
    for fr_, k in rings:
        Rk = Rq * fr_
        if Rk < 1: continue
        u = (r - Rk) / wd
        wave += np.sin(u * math.pi) * np.exp(-(u / 1.3) ** 2) * k
    wave *= env
    disp = wave * amp / q
    sxp, syp = xx - dx / r * disp, yy - dy * ay / r * disp
    out = np.stack([map_coordinates(small[..., c], [syp, sxp], order=1, mode='nearest') for c in range(3)], -1)
    crest = np.clip(wave, 0, 1) ** 2; tr = np.clip(-wave, 0, 1) ** 2
    surf = np.clip((out.mean(-1) - 5.) / 28., 0, 1)[..., None]      # caustics only where there is a surface (not the void)
    out = out + surf * (crest[..., None] * hl_gain * np.array([.9, .88, 1.0], np.float32) - tr[..., None] * hl_gain * trough)
    res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    if q > 1: res = res.resize((cw, ch), Image.BILINEAR)
    m = np.clip(np.abs(wave) * 6, 0, 1)
    mm = Image.fromarray((m * 255).astype(np.uint8)).resize((cw, ch), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    base.paste(Image.composite(res, crop, mm), (X0, Y0))
    return base


def zblur(img, amount, center=(W / 2, H / 2), n=5):
    """radial zoom blur (average of copies magnified about `center`)."""
    if amount < .02: return img
    base = img.convert('RGB'); acc = np.asarray(base, np.float32).copy()
    cx, cy = center
    for i in range(1, n):
        s = 1 + amount * .05 * i; a = 1 / s
        acc += np.asarray(base.transform(base.size, Image.AFFINE, (a, 0, cx - cx * a, 0, a, cy - cy * a), Image.BILINEAR), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8)).convert(img.mode)


def zoom_smear(img, s0, s1, center=(W / 2, H / 2), max_step=4.0):
    """camera zoom motion blur: the average of copies of `img` scaled between s0 and s1 about `center` (s = scale of
    the scene at the shutter open/close relative to this frame, e.g. v(t -/+ 1/60) / v(t)). Enough taps that no
    copy is more than ~max_step px from the next at the frame corners; long smears are accumulated at half resolution
    (they are all blur anyway). Returns RGB."""
    span = abs(s1 - s0)
    if span < .003: return img
    cx, cy = center
    reach = max(math.hypot(cx, cy), math.hypot(W - cx, cy), math.hypot(cx, H - cy), math.hypot(W - cx, H - cy))
    q = 2 if span * reach > 24 else 1
    base = img.convert('RGB'); full = base.size
    if q > 1: base = base.resize((full[0] // q, full[1] // q), Image.BILINEAR); cx, cy = cx / q, cy / q
    n = int(clamp(span * reach / q / max_step + 1, 3, 12))
    acc = np.zeros((base.height, base.width, 3), np.float32)
    for i in range(n):
        s = s0 + (s1 - s0) * i / (n - 1); a = 1 / s
        acc += np.asarray(base.transform(base.size, Image.AFFINE, (a, 0, cx - cx * a, 0, a, cy - cy * a), Image.BILINEAR), np.float32)
    out = Image.fromarray((acc / n + .5).astype(np.uint8))
    return out.resize(full, Image.BILINEAR) if q > 1 else out
