"""Kit for s05_showreel_a (author C): easing, caches, native-fps clip reader, voice envelope, avatar access + face/hand
trackers, engine-look captions with measured onsets, tracked type, per-letter sprites, anamorphic flare, film grain/
weave, plate compositing (DOF + light match + regrade).  Read-only for other authors."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

W, H = E.W, E.H
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
CACHE = os.path.join(E.HERE, 'out', 'C', 'cache'); os.makedirs(CACHE, exist_ok=True)


def lerp(a, b, k): return a + (b - a) * k
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def expo_in(x):
    x = clamp(x); return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def sio(x):
    x = clamp(x); return .5 - .5 * math.cos(math.pi * x)
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def C(k, fn): return E.cached(('C',) + (k if isinstance(k, tuple) else (k,)), fn)
def decay(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0


def hop(x):
    """0 -> 1 -> 0 parabolic hop for x in [0, 1] (0 outside)."""
    return 4 * x * (1 - x) if 0 <= x <= 1 else 0.0


def spring(x, f=3.0, d=6.0):
    """overshooting settle 0 -> 1 (x in seconds-ish units)."""
    if x <= 0: return 0.0
    return 1 - math.exp(-d * x) * math.cos(2 * math.pi * f * x)


def scale_im(im, sx, sy=None):
    sy = sx if sy is None else sy
    if abs(sx - 1) < .01 and abs(sy - 1) < .01: return im
    return im.resize((max(1, int(round(im.width * sx))), max(1, int(round(im.height * sy)))), Image.BILINEAR)


def fade(im, k):
    if k >= .999: return im
    a = np.asarray(im.getchannel('A'), np.float32) * max(0., k)
    out = im.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8))); return out


def rot_im(im, deg):
    if abs(deg) < .2: return im
    return im.rotate(deg, Image.BICUBIC, expand=True)


def paste(base, im, x, y, center=True):
    if im is None: return
    if center: x, y = x - im.width / 2, y - im.height / 2
    E._paste(base, dict(img=im, xy=(int(round(x)), int(round(y))), glass=0))


def add_light(img, light, k=1.0):
    """additive light (float32 HxWx3 or smaller region dict) onto an RGB/RGBA PIL image -> RGBA."""
    o = np.asarray(img.convert('RGB'), np.float32) + light * k
    return Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).convert('RGBA')


# ---------------------------------------------------------------- stills / clips
def still(path, t, size=(W, H)):
    """one frame of a video at time t (ffmpeg seek, cached on disk) -> RGB."""
    def mk():
        fn = os.path.join(CACHE, f'st_{os.path.basename(path)}_{t:.3f}_{size[0]}x{size[1]}.png')
        if not os.path.exists(fn):                      # atomic: parallel renders may race on the first use
            tmp = fn[:-4] + f'.{os.getpid()}.tmp.png'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1', '-vf',
                            f'scale={size[0]}:{size[1]}', tmp], check=True)
            os.replace(tmp, fn)
        return Image.open(fn).convert('RGB')
    return C(('still', path, round(t, 3), size), mk)


class NClip:
    """sequential reader at the source's NATIVE frame rate: at(src_t) = source frame round(src_t * fps) — a pure function
    of src_t whatever frame the reader started at (exact frames, no CFR padding)."""
    def __init__(self, path, fps, size=(W, H)):
        self.path, self.fps, self.size, self.r, self.k0 = path, fps, size, None, None
    def at(self, src_t):
        k = max(0, int(math.floor(src_t * self.fps + .5 + 1e-6)))
        if self.r is not None and (k < self.k0 + self.r.n - 1 or k > self.k0 + self.r.n + 40): self.r.close(); self.r = None
        if self.r is None:
            self.k0 = k
            self.r = E.Reader(self.path, (k - .5) / self.fps, 8, vf=f'scale={self.size[0]}:{self.size[1]}', exact=True)
        return self.r.get(k - self.k0, self.size)
_nclips = {}
def nclip(path, fps, size=(W, H)):
    k = (path, fps, size)
    if k not in _nclips: _nclips[k] = NClip(path, fps, size)
    return _nclips[k]


# ---------------------------------------------------------------- voice
def _env_arr():
    def mk():
        x = np.fromfile(os.path.join(E.SRC, 'tight16k.raw'), np.float32); h = 160
        r = np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')[::h // 2])          # 5 ms hop, 10 ms window
        db = 20 * np.log10(r + 1e-6)
        return np.clip((db + 46) / 34, 0, 1).astype(np.float32)
    return C('env', mk)


def env(t, smooth_s=0.0):
    """voice loudness 0..1 at timeline t (5 ms hop); optional box smoothing (s)."""
    a = _env_arr(); i = int(t * 200)
    if smooth_s > 0:
        n = max(1, int(smooth_s * 200)); lo = max(0, i - n); return float(a[lo:i + 1].mean()) if i >= 0 and lo < len(a) else 0.0
    return float(a[i]) if 0 <= i < len(a) else 0.0


def wave(t0, t1, n):
    """raw voice samples over [t0, t1) resampled to n points (peak-preserving) -> float32 [-1, 1]."""
    x = C('raw16k', lambda: np.fromfile(os.path.join(E.SRC, 'tight16k.raw'), np.float32))
    a, b = max(0, int(t0 * 16000)), max(0, int(t1 * 16000))
    seg = x[a:b]
    if len(seg) < n: return np.zeros(n, np.float32)
    seg = seg[:len(seg) // n * n].reshape(n, -1)
    i = np.abs(seg).argmax(1); return seg[np.arange(n), i].astype(np.float32)


# ---------------------------------------------------------------- avatar access + trackers
def film_of(ctx):
    for c in (ctx.compose.__closure__ or ()):
        v = c.cell_contents
        if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    return None


def av_frame(ctx, t):
    F = film_of(ctx)
    return F.av.frame(t) if F is not None else None


_FT = {}
def face_track(av):
    """-> (fx, fy, top) face centre (between eyes / nose) and head top in take coordinates (avatar s=1, x=y=0)."""
    if av is None: return 535., 800., 598.
    if _FT.get('k') is av: return _FT['v']
    A = np.asarray(av.reduce(4), np.int16); a = A[..., 3]
    rows = np.where(a.max(1) > 128)[0]
    top = float(rows[0] * 4) if len(rows) else 598.
    r0 = int(top / 4) + 30; r1 = int(top / 4) + 100
    sub = A[r0:r1]; r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    skin = (r > 95) & (r > g + 15) & (r > b + 20) & (sub[..., 3] > 200)
    ys, xs = np.where(skin)
    fx = float(xs.mean() * 4 + 2) if len(xs) > 50 else 535.
    fy = top + 215.
    v = (fx, fy, top); _FT.update(k=av, v=v); return v


_HT = {}
def hand_track(av, side=1):
    """centroid of the skin pixels of one hand (side=+1: screen-right half) in the lower body, take coordinates."""
    if av is None: return (820., 1400.) if side > 0 else (260., 1400.)
    key = (id(av), side)
    if _HT.get('k') == key and _HT.get('av') is av: return _HT['v']
    A = np.asarray(av.reduce(4), np.int16)
    y0, y1 = 1150 // 4, 1880 // 4
    x0, x1 = (560 // 4, W // 4) if side > 0 else (0, 520 // 4)
    sub = A[y0:y1, x0:x1]; r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    skin = (r > 110) & (r > g + 18) & (r > b + 25) & (sub[..., 3] > 200)
    ys, xs = np.where(skin)
    v = ((float(xs.mean()) + x0) * 4 + 2, (float(ys.mean()) + y0) * 4 + 2) if len(xs) > 30 else ((820., 1400.) if side > 0 else (260., 1400.))
    _HT.update(k=key, av=av, v=v); return v


# ---------------------------------------------------------------- captions (engine look, measured onsets)
def _cap_layout(words, base, maxw):
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


def caps(t, pages, y=1420, base=92, x=540, maxw=900, alpha=1.0, punch=None):
    """pages: [(a, z, [(TEXT, t0, emph), ...]), ...] -> list of (img, cx, cy) word pops exactly like the engine
    captions.  punch = (TEXT, t_hit): that word kicks (scale) again at t_hit."""
    out = []
    for a, z, words in pages:
        if not (a <= t < z): continue
        L = _cap_layout(words, base, maxw)
        nxt = [w[1] for w in words[1:]] + [z]
        for (it, cx, cy), t1 in zip(L, nxt):
            text, t0, em, sz, _ = it
            if t < t0 - .02: continue
            lt = t - t0 + .02; s = .72 + .28 * back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            if punch and text == punch[0] and t >= punch[1]: s *= 1 + .22 * decay(t, punch[1], .09)
            im = E.word_img(text, sz, 'grad' if em else 'white')[0]
            al = clamp(lt / .05) * clamp((z - t) / .06) * alpha
            out.append((fade(scale_im(im, s), al), x + cx, y + cy))
    return out


# ---------------------------------------------------------------- type
def tracked(s, size, wght=300, col=E.WHITE, track=.3, glow=0.0):
    """single-line tracked text (RGBA, tight box + small pad)."""
    def mk():
        f = E.font(size, wght); tr = size * track
        adv = [f.getlength(ch) for ch in s]; wsum = sum(adv) + tr * (len(s) - 1)
        pad = int(size * .5); asc, desc = f.getmetrics()
        im = Image.new('L', (int(wsum) + 2 * pad, asc + desc + 2 * pad)); d = ImageDraw.Draw(im); x = pad
        for ch, a in zip(s, adv): d.text((x, pad), ch, font=f, fill=255); x += a + tr
        out = Image.new('RGBA', im.size, col + (0,)); out.putalpha(im)
        if glow > 0:
            g = Image.new('RGBA', im.size, (150, 130, 255, 0)); g.putalpha(im.filter(ImageFilter.GaussianBlur(size * .25)).point(lambda v: int(v * glow)))
            g.alpha_composite(out); out = g
        return out
    return C(('tracked', s, size, wght, col, track, glow), mk)


def letters(word, size, style='white', wght=900):
    """per-letter sprites of `word` laid out as the full word would be: -> (list of (img, cx, base_y), word_w, cap_h).
    cx = centre x of each letter relative to the word's left edge; base_y = sprite centre y relative to baseline.
    style: 'white' | 'grad' (gradient continuous across the word) with the engine's dark stroke + shadow."""
    def mk():
        f = E.font(size, wght); sw = max(3, size // 22); pad = int(size * .35)
        l, tp, r, b = f.getbbox(word, stroke_width=sw)
        Ww, Hw = r - l + 2 * pad, b - tp + 2 * pad
        ox, oy = pad - l, pad - tp                     # text origin in the word canvas
        asc = f.getmetrics()[0]; base = oy + asc       # baseline y in canvas
        grad = E.gradient(Ww, Hw, E.GRAD_LIGHT).convert('RGBA') if style == 'grad' else None
        out = []; x = 0.0
        for i, ch in enumerate(word):
            prefix = f.getlength(word[:i])
            fill = Image.new('L', (Ww, Hw)); ImageDraw.Draw(fill).text((ox + prefix, oy), ch, font=f, fill=255)
            strk = Image.new('L', (Ww, Hw)); ImageDraw.Draw(strk).text((ox + prefix, oy), ch, font=f, fill=255, stroke_width=sw, stroke_fill=255)
            bb = strk.getbbox()
            if bb is None: out.append((None, ox + prefix + f.getlength(ch) / 2, 0)); continue
            x0, y0, x1, y1 = bb; m = int(size * .22)
            x0, y0, x1, y1 = max(0, x0 - m), max(0, y0 - m), min(Ww, x1 + m), min(Hw, y1 + m)
            shadow = strk.filter(ImageFilter.GaussianBlur(size * .12))
            im = Image.new('RGBA', (Ww, Hw), (0, 0, 0, 0))
            sh = Image.new('RGBA', (Ww, Hw), (6, 6, 12, 0)); sh.putalpha(shadow.point(lambda v: int(v * .8))); im.alpha_composite(sh, (0, int(size * .04)))
            st = Image.new('RGBA', (Ww, Hw), (10, 10, 16, 0)); st.putalpha(strk.point(lambda v: int(v * .9))); im.alpha_composite(st)
            if grad is not None:
                gl = Image.new('RGBA', (Ww, Hw), (120, 90, 255, 0)); gl.putalpha(fill.filter(ImageFilter.GaussianBlur(size * .16)).point(lambda v: int(v * .55)))
                im.alpha_composite(gl); g = grad.copy(); g.putalpha(fill); im.alpha_composite(g)
            else:
                c = Image.new('RGBA', (Ww, Hw), E.WHITE + (0,)); c.putalpha(fill); im.alpha_composite(c)
            im = im.crop((x0, y0, x1, y1))
            out.append((im, (x0 + x1) / 2 - ox, (y0 + y1) / 2 - base))
        return out, f.getlength(word), asc * .72
    return C(('letters', word, size, style, wght), mk)


def draw_word(base_img, word, size, style, x, y, fx=None, wght=900, alpha=1.0):
    """paste a per-letter animated word: left edge x, baseline y; fx(i, n) -> dict(dx, dy, sx, sy, rot, a)
    (sy scales from the baseline)."""
    sprites, ww, ch = letters(word, size, style, wght)
    n = len(sprites)
    for i, (im, cx, cy) in enumerate(sprites):
        if im is None: continue
        p = dict(dx=0., dy=0., sx=1., sy=1., rot=0., a=1.)
        if fx: p.update(fx(i, n))
        if p['a'] * alpha <= .01: continue
        s = scale_im(im, p['sx'], p['sy'])
        s = rot_im(s, p['rot'])
        # scale y about the baseline: sprite centre moves
        ccy = cy * p['sy']
        paste(base_img, fade(s, p['a'] * alpha), x + cx * 1.0 + p['dx'], y + ccy + p['dy'])
    return ww


# ---------------------------------------------------------------- light
def flare_sprite(w, h, col=(110, 130, 255), core=(255, 250, 255), thick=4.0, reach=.55):
    """anamorphic streak (float32 h x w x 3, additive), centred."""
    def mk():
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dy = yy - h / 2; ax = np.abs(xx - w / 2) / (w / 2)
        st = np.exp(-(dy / thick) ** 2) * np.exp(-(ax / reach) ** 2)
        st2 = np.exp(-(dy / (thick * 6)) ** 2) * np.exp(-(ax / (reach * 1.3)) ** 2)
        orb = np.exp(-((xx - w / 2) ** 2 + dy ** 2) / (2 * (thick * 9) ** 2))
        return (st[..., None] * np.array(core, np.float32) * .9 + st2[..., None] * np.array(col, np.float32) * .55
                + orb[..., None] * np.array(core, np.float32) * .55).astype(np.float32)
    return C(('flare', w, h, col, core, thick, reach), mk)


def add_flare(img, cx, cy, k, w=2200, h=160, **kw):
    """additive anamorphic flare centred at (cx, cy) on an RGBA/RGB image -> RGBA."""
    if k <= .01: return img
    F = flare_sprite(w, h, **kw)
    a = np.asarray(img.convert('RGB'), np.float32).copy()
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    ax0, ay0, ax1, ay1 = max(0, x0), max(0, y0), min(img.width, x0 + w), min(img.height, y0 + h)
    if ax1 <= ax0 or ay1 <= ay0: return img.convert('RGBA')
    a[ay0:ay1, ax0:ax1] += F[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def ring_img(d, w, col=(255, 255, 255), a=1.0, blur=0.0):
    d = max(4, int(d)); w = max(1, int(round(w))); n = d + 2 * w + 8 + int(blur * 3)
    im = Image.new('L', (n, n)); ImageDraw.Draw(im).ellipse(((n - d) / 2, (n - d) / 2, (n + d) / 2, (n + d) / 2), outline=int(255 * a), width=max(1, int(w)))
    if blur > .3: im = im.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new('RGBA', (n, n), col + (0,)); out.putalpha(im); return out


# ---------------------------------------------------------------- plates (real locations)
def plate(path, blur, zoom=1.0):
    """location plate cover-fit to 1080x1920 (x zoom), DOF blur; + a very soft copy for light wrap; + mean colour."""
    def mk():
        im = Image.open(path).convert('RGB')
        sc = max(W / im.width, H / im.height) * zoom
        im = im.resize((int(im.width * sc + .5), int(im.height * sc + .5)), Image.LANCZOS)
        x0, y0 = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((x0, y0, x0 + W, y0 + H))
        sharp = im.filter(ImageFilter.GaussianBlur(blur)) if blur > .3 else im
        wrap = np.asarray(im.reduce(4).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR), np.float32)
        mean = np.asarray(im.crop((150, 500, 930, 1500)), np.float32).reshape(-1, 3).mean(0)
        return sharp, wrap, mean
    return C(('plate', path, blur, zoom), mk)


def graded_avatar(av, s, x, y, L, wrapimg):
    """the keyed founder (RGBA full frame from the engine) regraded for a location: tint, exposure toward the plate,
    key light side, rim colour/side, light wrap from the plate.  -> (RGBA sprite, (px, py)) placed like the engine
    places the avatar (scale s around the bottom centre, offset x, y)."""
    from scipy.ndimage import minimum_filter
    if abs(s - 1) > .005: av = av.resize((int(W * s), int(H * s)), Image.BILINEAR)
    px, py = int(540 - av.width / 2 + x), int(H - av.height + y)
    # crop to the visible frame + the alpha bbox
    bb = av.getchannel('A').getbbox()
    if bb is None: return None, (0, 0)
    x0, y0, x1, y1 = bb
    x0, y0 = max(x0, -px), max(y0, -py); x1, y1 = min(x1, W - px), min(y1, H - py)
    if x1 <= x0 or y1 <= y0: return None, (0, 0)
    av = av.crop((x0, y0, x1, y1)); px, py = px + x0, py + y0
    A = np.asarray(av, np.float32); rgb = A[..., :3]; al = A[..., 3] / 255
    rgb = rgb * np.array(L['tint'], np.float32) * L.get('expo', 1.0)
    if L.get('desat'): g = rgb.mean(2, keepdims=True); rgb = g + (rgb - g) * (1 - L['desat'])
    gx = np.linspace(-1, 1, W, dtype=np.float32)[px:px + av.width][None, :, None]
    side = L['side']
    if side:
        lit = np.clip(.5 + .5 * side * gx * 1.4, 0, 1)
        rgb = rgb * (1 - L['amt'] * .55 + L['amt'] * 1.1 * lit) + np.array(L['key'], np.float32) * L['amt'] * .25 * lit
    band = np.clip(al - minimum_filter(al, size=11), 0, 1)[..., None]
    rs = np.clip(.5 + L['rside'] * gx * 1.6, 0, 1) if L['rside'] else .5
    e = band * rs * L['ramt']
    rgb = rgb * (1 - e) + np.array(L['rim'], np.float32) * e
    edge = np.clip(al - minimum_filter(al, size=7), 0, 1)[..., None]
    wc = wrapimg[py:py + av.height, px:px + av.width]
    wk = L.get('wrap', .3)
    rgb = rgb * (1 - wk * edge) + wc * wk * edge
    out = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), A[..., 3:]]).astype(np.uint8), 'RGBA')
    return out, (px, py)
