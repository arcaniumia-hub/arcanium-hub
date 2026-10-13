"""Private helpers for s07_movie + s08_cta (author D): measured word onsets + own caption pages (engine look), a
deterministic reader for the 24 fps croissant pull, the trailer "film" (cover-fit plates, grade, halation, light
leaks, gate weave, letterbox), gold trailer type, iOS-style notification stack, the Instagram comment sheet + iOS
keyboard, the LUMARC lower third and the end card. Everything is a pure function of t (no per-frame state)."""
import copy, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import engine as E

W, H, FPS = E.W, E.H, E.FPS
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
CREAM = (250, 246, 238)
LAV = (164, 142, 255)
TL = E.TL
M0, M1 = E.MOVIE


def C(k, fn): return E.cached(('D',) + (k if isinstance(k, tuple) else (k,)), fn)
def fr(t): return int(round(t * FPS))
def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def scale_im(im, s, resample=Image.BILINEAR):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(im.width * s + .5)), max(1, int(im.height * s + .5))), resample)


# ================================================================== measured word onsets
# voice16k.raw (10 ms RMS envelope, 2.5/1 ms-hop spectrograms, 14th-order LPC formant tracks); edit-timeline seconds.
# Line 17 is measured in the THERAPIST TAKE's own seconds (src) and mapped through TL[17], so it stays right if the
# integrator re-times / extends that line. NB: in the take the therapist SPELLS the name: "comment L-U-M-A-R-C".
L14, L15, L16, L17 = TL[14], TL[15], TL[16], TL[17]
def e17(src): return round(L17['t0'] + (src - L17['s0']), 3)
FB = L17['s1'] >= 25.86            # "For brands." (take src 25.28-25.88) is inside the edit?

MEASURED = {
    14: [('I', 36.90), ('SELL', 37.00), ('CROISSANTS,', 37.23), ('NOT', 38.33), ('MOVIES!', 38.50)],
    15: [('KEVIN…', 39.64), ('YOUR', 40.45), ('CROISSANTS', 40.78), ('DESERVE', 41.54), ('A', 42.10), ('MOVIE.', 42.14)],
    16: [('…OH.', 46.57), ('OH.', 47.73), ('OKAY…', 48.60), ("I'M", 49.68), ('LISTENING.', 49.76)],
    17: [(w, e17(s)) for w, s in (('IF', 17.92), ('YOUR', 18.08), ('INSTAGRAM', 18.39), ('STOPPED', 18.92),
                                   ('TALKING', 19.34), ('TO', 19.56), ('YOU…', 19.76), ('COMMENT', 20.34),
                                   ('“LUMARC”.', 21.12), ('WE', 23.62), ('DO', 23.88), ('COUPLES', 24.00),
                                   ('THERAPY.', 24.40), ('FOR', 25.30), ('BRANDS.', 25.46))],
}
SPELL = [(c, e17(s)) for c, s in zip('LUMARC', (21.12, 21.35, 21.80, 22.12, 22.41, 22.62))]   # spoken letters
def wt(seg, text, nth=0):
    return [t for w, t in MEASURED[seg] if w == text][nth]


def _pages():
    """engine caption pages with the measured onsets (by occurrence); t1 / page in-out recomputed like engine._pages.
    Pages never spill onto the next line's picture, into the movie, or past the last spoken word."""
    pages = copy.deepcopy(E.PAGES)
    words = [w for p in pages for w in p['words']]
    for seg, lst in MEASURED.items():
        ws = [w for w in words if w['seg'] == seg]
        if [w['text'] for w in ws] != [x for x, _ in lst]:
            raise ValueError(f'caption words of line {seg} changed: {[w["text"] for w in ws]}')
        for w, (_, t0) in zip(ws, lst): w['t0'] = t0
    for k, w in enumerate(words[:-1]):
        if words[k + 1]['seg'] == w['seg']: w['t1'] = max(w['t0'] + .06, words[k + 1]['t0'])
    for w in words: w['t1'] = max(w['t1'], w['t0'] + .06)
    for j, p in enumerate(pages):
        nxt = pages[j + 1]['words'][0]['t0'] if j + 1 < len(pages) else E.DUR; last = p['words'][-1]['t1']
        p['a'] = p['words'][0]['t0'] - .04; p['z'] = nxt - .02 if nxt - last < .5 else last + .35
        if p['seg'] + 1 < len(TL):
            p['z'] = min(p['z'], math.ceil(TL[p['seg'] + 1]['t0'] * FPS - 1e-6) / FPS)
        if p['seg'] == 15: p['z'] = min(p['z'], M0)
        if p['seg'] == 17: p['z'] = min(p['z'], E.VOICE_END)
        p['key'] = ' '.join(w['text'] for w in p['words'])
    return [p for p in pages if p['seg'] in MEASURED]
PAGES = _pages()


def captions(ctx, t, segs, sizes=None, cy0=None, skip=(), layer='screen'):
    """the engine's word-pop captions for lines `segs` on the measured onsets (replaces ctx.captions this frame).
    sizes: {page key: base size}; skip: page keys not to draw (replaced by kinetic UI)."""
    ctx.captions = False
    cy0 = ctx.cap_y if cy0 is None else cy0
    for p in PAGES:
        if p['seg'] not in segs or not (p['a'] <= t < p['z']) or p['key'] in skip: continue
        base = (sizes or {}).get(p['key'], ctx.cap_size)
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img = E.cap_word(w['text'], sz, w['spk'] if w['emph'] else None)
            if lt < .05: img = E.fade(img, lt / .05)
            if p['z'] - t < .06: img = E.fade(img, max(0., (p['z'] - t) / .06))
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add(layer, img, int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2), center=False)


# ================================================================== camera helpers
def face_cam(face, z, to=(540, 640), rot=0.0):
    """camera that scales by z around world point `face` and moves it toward screen point `to` (engine clamps)."""
    fx, fy = face; k = min(1., (z - 1) / .5)
    return dict(z=z, x=fx, y=fy, dx=(to[0] - fx) * k, dy=(to[1] - fy) * k, rot=rot)


_CHOKE = {}
def clean_take(ctx, px=2, soft=1.2):
    """draw ctx.shot's take ourselves with its matte choked by `px` (the engine key leaves a 2-3 px light/green fringe
    round hair and ears that crash zooms magnify into a cut-out outline). Same placement as the engine (s=1, x=y=0)."""
    S = ctx.shot
    if not S['show'] or S['angle'] not in E.ANGLES or S['angle'] == 'wide': return
    assert abs(S['s'] - 1) < .005 and S['x'] == 0 and S['y'] == 0 and S['alpha'] >= 1 and S['bright'] == 1
    av = E.graded(S['spk'], S['src'], S['angle'])
    k = (S['spk'], S['angle']); hit = _CHOKE.get(k)
    if hit is not None and hit[0] is av: out = hit[1]
    else:
        from scipy.ndimage import minimum_filter
        a = np.asarray(av.getchannel('A'))
        a2 = Image.fromarray(minimum_filter(a, size=2 * px + 1)).filter(ImageFilter.GaussianBlur(soft))
        out = av.copy(); out.putalpha(Image.fromarray(np.minimum(a, np.asarray(a2))))
        _CHOKE[k] = (av, out)
    S['show'] = False
    ctx.behind.append(dict(img=out, xy=(0, 0), glass=0))


def snap(f, f_hit, n=3):
    """crash-zoom progress 0..1 over the n frames that END on f_hit (frame-exact, ease-out)."""
    k = clamp((f - (f_hit - n)) / n); return 1 - (1 - k) ** 2


def zoom_blur(amount, anchor=(540, 640), n=14):
    """ctx.wrap: radial motion blur of the world (captions/UI stay crisp). The blurred taps are taken at half
    resolution (14 of them: no ghost banding) and added to the full-res sharp tap."""
    def wrap(frame):
        rgb = frame.convert('RGB'); w2, h2 = W // 2, H // 2
        sm = rgb.resize((w2, h2), Image.BILINEAR); ax, ay = anchor[0] / 2, anchor[1] / 2
        acc = np.zeros((h2, w2, 3), np.float32)
        for i in range(1, n):
            a = 1 / (1 + amount * .16 * i / (n - 1))
            acc += np.asarray(sm.transform((w2, h2), Image.AFFINE, (a, 0, ax - a * ax, 0, a, ay - a * ay), Image.BILINEAR), np.float32)
        acc = Image.fromarray(np.clip(acc / (n - 1), 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        out = (np.asarray(rgb, np.float32) + np.asarray(acc, np.float32) * (n - 1)) / n
        return Image.fromarray(out.astype(np.uint8)).convert('RGBA')
    return wrap


# ================================================================== fonts / type
SERIF = os.path.join(E.V, 'birra-reel/fonts/corm.woff2')          # Cormorant Garamond (variable 300-700)
INTER = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'


def serif(size, wght=600):
    def mk():
        f = ImageFont.truetype(SERIF, size)
        try: f.set_variation_by_axes([wght])
        except Exception: pass
        return f
    return C(('serif', size, wght), mk)


def inter(size, weight='Regular'):
    return C(('inter', size, weight), lambda: ImageFont.truetype(INTER % weight, size))


def emoji(ch, size):
    def mk():
        try:
            f = ImageFont.truetype(EMOJI, 109)
            im = Image.new('RGBA', (170, 170), (0, 0, 0, 0)); ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
            im = im.crop(im.getbbox())
            return im.resize((max(1, int(im.width * size / im.height)), size), Image.LANCZOS)
        except Exception:
            return Image.new('RGBA', (size, size), (0, 0, 0, 0))
    return C(('emoji', ch, size), mk)


def tracked_mask(text, f, track):
    """L mask of letter-spaced text (tight vertical bbox of the font's caps + pad 6)."""
    adv = [f.getlength(c) for c in text]
    w = int(sum(adv) + track * (len(text) - 1)) + 12
    _, tp, _, b = f.getbbox('HÉgy' if any(c in 'gjpqy' for c in text) else 'HÉ')
    _, tp, _, b2 = f.getbbox(text); tp = min(tp, f.getbbox('H')[1]); b = max(b2, f.getbbox('H')[3])
    m = Image.new('L', (w, b - tp + 12)); d = ImageDraw.Draw(m); x = 6.
    for c, a in zip(text, adv):
        d.text((x, 6 - tp), c, font=f, fill=255); x += a + track
    return m


def mask_rgba(m, col):
    out = Image.new('RGBA', m.size, col + (0,)); out.putalpha(m); return out


def ui_text(s, f, col):
    """tight RGBA text (pad 4) in font f."""
    def mk():
        l, tp, r, b = f.getbbox(s)
        im = Image.new('RGBA', (r - l + 8, b - tp + 8), (0, 0, 0, 0)); ImageDraw.Draw(im).text((4 - l, 4 - tp), s, font=f, fill=col)
        return im
    return C(('uit', s, id(f), col), mk)


# ================================================================== croissant pull (24 fps, deterministic by frame)
PULL_N = 121
class _Pull:
    """native frame f of croissant_pull.mp4 (1080x1912). The reader seeks to (f-.5)/24 with exact frames, so frame f
    is the same whatever frame a chunk starts on."""
    def __init__(self): self.r, self.f0, self.memo = None, 0, {}
    def get(self, f):
        f = max(0, min(PULL_N - 1, int(f)))
        if f in self.memo: return self.memo[f]
        if self.r is not None and (f < self.f0 + self.r.n - 1 or f > self.f0 + self.r.n + 30): self.r.close(); self.r = None
        if self.r is None:
            self.f0 = f; self.r = E.Reader(E.CROISSANT_PULL, (f - .5) / 24, (PULL_N - f) / 24 + .2, vf='scale=1080:1912', exact=True)
        im = self.r.get(f - self.f0, (1080, 1912))
        if im is None: im = self.memo.get(max(self.memo) if self.memo else 0) or Image.new('RGB', (1080, 1912))
        self.memo[f] = im.copy()
        for k in [k for k in self.memo if abs(k - f) > 4]: del self.memo[k]
        return self.memo[f]
_PULL = _Pull()


def pull_frame(native_t):
    """frame-blended pull at native time (seconds); blending makes ramps/slow-mo smooth."""
    x = native_t * 24; f0 = int(math.floor(x)); k = x - f0
    a = _PULL.get(f0)
    if k < .08 or f0 + 1 >= PULL_N: return a
    b = _PULL.get(f0 + 1)
    if k > .92: return b
    return Image.blend(a, b, k)


# ================================================================== film plates
def plate_src(name, width=1350):
    """asset pre-scaled (LANCZOS) to `width` for cheap high-quality affine sampling."""
    def mk():
        im = E.asset(name); return im.resize((width, int(im.height * width / im.width + .5)), Image.LANCZOS)
    return C(('psrc', name, width), mk)


def frame_from(img, z=1.0, cx=.5, cy=.5, dx=0., dy=0., rot=0., resample=Image.BILINEAR, vis=None):
    """cover-fit `img` to 1080x1920, zoomed z around its point (cx, cy) (fractions) which lands on screen centre
    (+dx, dy); rot in degrees. The source window is clamped to stay inside the image. vis=(y0, y1): only those
    screen rows must be covered (e.g. the letterboxed scope frame) — cover-fit and clamp against them."""
    iw, ih = img.size
    vy0, vy1 = vis if vis else (0, H)
    s = max(W / iw, (vy1 - vy0) / ih) * z
    hw = W / 2 / s
    ux, uy = cx * iw - dx / s, cy * ih - dy / s
    ux = min(max(ux, hw * (1 + abs(rot) * .02)), iw - hw * (1 + abs(rot) * .02))
    ex = 1 + abs(rot) * .02
    uy = min(max(uy, (H / 2 - vy0) / s * ex), ih - (vy1 - H / 2) / s * ex)
    r = math.radians(rot); c, si = math.cos(r) / s, math.sin(r) / s
    # output (x, y) -> source: u = ux + c*(x-W/2) + si*(y-H/2) ; v = uy - si*(x-W/2) + c*(y-H/2)
    data = (c, si, ux - c * W / 2 - si * H / 2, -si, c, uy + si * W / 2 - c * H / 2)
    return img.transform((W, H), Image.AFFINE, data, resample)


def leak_tex():
    """warm light-leak texture (float32 H/4 x W/4 x 3, 0..1): soft orange/amber blobs."""
    def mk():
        h, w = H // 4, W // 4
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        out = np.zeros((h, w, 3), np.float32)
        for cx, cy, rx, ry, col in ((.95, .25, .35, .30, (1.0, .45, .12)), (1.05, .55, .25, .45, (1.0, .70, .30)),
                                    (.80, .10, .20, .12, (1.0, .85, .55))):
            g = np.exp(-(((x / w - cx) / rx) ** 2 + ((y / h - cy) / ry) ** 2))
            out += g[..., None] * np.array(col, np.float32)
        return np.clip(out, 0, 1.4)
    return C('leak', mk)


def film_look(img, t, leak=0.0, leak_dx=0.0, halation=.30, contrast=.35, warm=1.0, lift=4.0):
    """trailer grade on an RGB frame: S-curve contrast, warm highlights / cool-ish shadows, halation (red-orange glow
    round highlights), additive light leak sliding in from the right by leak_dx (fraction of W)."""
    a = np.asarray(img, np.float32) / 255.
    a = a * (1 - contrast) + (a * a * (3 - 2 * a)) * contrast
    lum = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    tint = (lum - .45)[..., None] * np.array([.07, .015, -.07], np.float32) * warm
    a = a + tint
    if halation > .01:
        sm = Image.fromarray(np.clip(lum * 255, 0, 255).astype(np.uint8)).resize((W // 6, H // 6), Image.BILINEAR)
        hl = np.asarray(sm, np.float32) / 255.
        hl = np.clip((hl - .62) / .38, 0, 1)
        hl_im = Image.fromarray((hl * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
        hv = np.asarray(hl_im, np.float32)[..., None] / 255.
        a = a + hv * np.array([1.0, .42, .16], np.float32) * halation
    if leak > .01:
        tex = leak_tex(); sh = int(leak_dx * W / 4)
        t2 = np.roll(tex, sh, 1)
        if sh > 0: t2[:, :sh] = 0
        lk = np.asarray(Image.fromarray(np.clip(t2 * 180, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 180.
        a = 1 - (1 - a) * (1 - np.clip(lk * leak, 0, 1))          # screen blend
    a = a * (1 - lift / 255) + lift / 255
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def letterbox(img, bar):
    """black bars of height `bar` top and bottom (RGB or RGBA)."""
    if bar <= 0: return img
    d = ImageDraw.Draw(img); b = int(round(bar))
    d.rectangle((0, 0, W, b - 1), fill=(0, 0, 0)); d.rectangle((0, H - b, W, H), fill=(0, 0, 0))
    return img


SLIT = (H - 452) / 2          # 2.39:1 scope slit (1080 x 452) = bars of 734
SCOPE = 300                   # the trailer's expanded frame: 1080 x 1320 (bars of 300)


# ================================================================== trailer type
GOLD = [(255, 247, 220), (250, 216, 140), (206, 150, 60), (246, 206, 118), (132, 84, 26)]


def gold_fill(m, hi=.42):
    """vertical gold gradient (with a bright specular band) masked by L image m."""
    w, h = m.size
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    stops = np.array([0, .30, .55, .72, 1.0], np.float32)
    cols = np.array(GOLD, np.float32)
    rgb = np.stack([np.interp(y[:, 0], stops, cols[:, c]) for c in range(3)], 1)[:, None, :].repeat(w, 1)
    band = np.exp(-((y - hi) / .06) ** 2)[..., None] * 60
    rgb = np.clip(rgb + band, 0, 255)
    out = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); out.putalpha(m); return out


def gold_word(m):
    """gold letters with bevel (light top edge, dark bottom edge), thin dark outline, warm glow + drop shadow; padded 60."""
    P = 60
    big = Image.new('L', (m.width + 2 * P, m.height + 2 * P)); big.paste(m, (P, P))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    sh = mask_rgba(big.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .75)), (12, 6, 0))
    out.alpha_composite(sh, (0, 10))
    glow = mask_rgba(big.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * .55)), (255, 160, 60))
    out.alpha_composite(glow)
    edge = mask_rgba(big.filter(ImageFilter.MaxFilter(3)), (60, 34, 8))
    out.alpha_composite(edge)
    out.alpha_composite(gold_fill(big))
    a = np.asarray(big, np.float32) / 255
    up = np.roll(a, 2, 0); dn = np.roll(a, -2, 0)
    hi = np.clip(a - up, 0, 1) * .85; lo = np.clip(a - dn, 0, 1) * .55
    A = np.asarray(out, np.float32)
    A[..., :3] = A[..., :3] + (255 - A[..., :3]) * hi[..., None] - A[..., :3] * lo[..., None]
    return Image.fromarray(np.clip(A, 0, 255).astype(np.uint8)), P


def title_img():
    """KEVIN'S / BAKERY trailer title (gold serif, each line its own gold ramp) -> (RGBA, bare ink mask for the sheen)."""
    def mk():
        m1 = tracked_mask('KEVIN’S', serif(96, 700), 96 * .30)
        m2 = tracked_mask('BAKERY', serif(236, 650), 236 * .06)
        g1, P = gold_word(m1); g2, _ = gold_word(m2)
        gap = 14
        w = max(g1.width, g2.width); h = g1.height + g2.height - 2 * P + gap
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        img.alpha_composite(g2, ((w - g2.width) // 2, g1.height - 2 * P + gap))
        img.alpha_composite(g1, ((w - g1.width) // 2, 0))
        ink = np.zeros((h, w), np.float32)
        x1, x2 = (w - g1.width) // 2 + P, (w - g2.width) // 2 + P
        ink[P:P + m1.height, x1:x1 + m1.width] = np.asarray(m1, np.float32) / 255
        y2 = g1.height - 2 * P + gap + P
        ink[y2:y2 + m2.height, x2:x2 + m2.width] = np.maximum(ink[y2:y2 + m2.height, x2:x2 + m2.width], np.asarray(m2, np.float32) / 255)
        return img, ink
    return C('title2', mk)


def add_light(img, k, col=(255, 240, 215), y0=0, y1=H):
    """additive light over rows y0..y1 (a flash that brightens, never a grey veil)."""
    if k <= .01: return img
    a = np.asarray(img, np.float32).copy()
    a[int(y0):int(y1), :, :3] += np.array(col, np.float32) * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)


def small_caps(text, size=44, track=.48, col=(238, 226, 204), wght=500, rules=0):
    """letter-spaced serif small caps (trailer credit), optional thin gold rules either side; soft dark halo."""
    def mk():
        m = tracked_mask(text, serif(size, wght), size * track)
        P = 40; rl = rules
        w = m.width + 2 * P + (2 * (rl + 34) if rl else 0)
        im = Image.new('RGBA', (w, m.height + 2 * P), (0, 0, 0, 0))
        x0 = (w - m.width) // 2
        halo = Image.new('L', im.size); halo.paste(m, (x0, P))
        im.alpha_composite(mask_rgba(halo.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .55)), (0, 0, 0)))
        im.alpha_composite(mask_rgba(m, col), (x0, P))
        if rl:
            d = ImageDraw.Draw(im); cy = P + m.height // 2
            d.line((x0 - 30 - rl, cy, x0 - 30, cy), fill=(214, 172, 96, 220), width=2)
            d.line((x0 + m.width + 30, cy, x0 + m.width + 30 + rl, cy), fill=(214, 172, 96, 220), width=2)
        return im
    return C(('scaps', text, size, track, col, wght, rules), mk)


def sheen(img, k, mask, half=34, strength=.6, slope=.35):
    """narrow diagonal light band that lifts ONLY the ink (mask float HxW 0..1); k 0..1 = position."""
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


def flare_field():
    """anamorphic streak + soft core (float32 300 x W x 3, 0..1) centred vertically."""
    def mk():
        h = 300; y, x = np.mgrid[0:h, 0:W].astype(np.float32)
        yy = (y - h / 2); xx = (x - W / 2)
        streak = np.exp(-(yy / 3.2) ** 2) * np.exp(-(xx / 700) ** 2)
        haze = np.exp(-(yy / 26) ** 2) * np.exp(-(xx / 420) ** 2) * .35
        core = np.exp(-((xx / 160) ** 2 + (yy / 60) ** 2)) * .5
        f = streak[..., None] * np.array([1.0, .86, .62]) + haze[..., None] * np.array([1.0, .62, .25]) \
            + core[..., None] * np.array([1.0, .80, .50])
        return f.astype(np.float32)
    return C('flare', mk)


def add_field(img, field, k, cy):
    if k <= .01: return img
    a = np.asarray(img, np.float32); h = field.shape[0]; y0 = int(cy - h / 2)
    ys, ye = max(0, y0), min(H, y0 + h)
    if ye > ys:
        a = a.copy(); a[ys:ye, :, :3] += field[ys - y0:ye - y0] * 255 * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)


# ================================================================== iOS notification stack
def _squircle_mask(s, r):
    m = Image.new('L', (s * 4, s * 4)); ImageDraw.Draw(m).rounded_rectangle((0, 0, s * 4 - 1, s * 4 - 1), r * 4, fill=255)
    return m.resize((s, s), Image.LANCZOS)


def _circle_mask(s):
    m = Image.new('L', (s * 4, s * 4)); ImageDraw.Draw(m).ellipse((0, 0, s * 4 - 1, s * 4 - 1), fill=255)
    return m.resize((s, s), Image.LANCZOS)


def heart_glyph(size, col=(255, 255, 255), fill=True, width=3):
    def mk():
        ss = 4; S = size * ss; im = Image.new('L', (S, S)); d = ImageDraw.Draw(im); pts = []
        for i in range(120):
            a = i / 120 * 2 * math.pi
            x = 16 * math.sin(a) ** 3; y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((S / 2 + x * S / 36, S * .47 - y * S / 36))
        if fill: d.polygon(pts, fill=255)
        else: d.line(pts + [pts[0]], fill=255, width=width * ss, joint='curve')
        return mask_rgba(im.resize((size, size), Image.LANCZOS), col)
    return C(('heart', size, col, fill, width), mk)


def app_badge(s):
    """small app badge: warm-gradient squircle with a white heart (generic 'activity' glyph — no logo)."""
    def mk():
        g = E.gradient(s, s, [(255, 190, 70), (255, 60, 120), (170, 60, 230)]).rotate(-45, Image.BILINEAR, expand=False).convert('RGBA')
        g.putalpha(_squircle_mask(s, int(s * .24)))
        hg = heart_glyph(int(s * .56)); g.alpha_composite(hg, ((s - hg.width) // 2, int(s * .24)))
        return g
    return C(('badge', s), mk)


def bakery_avatar(s):
    def mk():
        a = E.asset('croissant_hero'); q = int(min(a.width, a.height) * .62)
        cx, cy = int(a.width * .40), int(a.height * .62)
        face = a.crop((cx - q // 2, cy - q // 2, cx + q // 2, cy + q // 2)).resize((s, s), Image.LANCZOS).convert('RGBA')
        face.putalpha(_circle_mask(s)); return face
    return C(('bav', s), mk)


NW, NH = 980, 168


def notif_card(title, body, bold_body=False):
    """iOS-style communication notification (dark material): avatar + app badge, bold title, body, 'now'."""
    def mk():
        im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
        m = Image.new('L', (NW * 2, NH * 2)); ImageDraw.Draw(m).rounded_rectangle((0, 0, NW * 2 - 1, NH * 2 - 1), 88, fill=255)
        m = m.resize((NW, NH), Image.LANCZOS)
        body_l = Image.new('RGBA', (NW, NH), (36, 34, 38, 0)); body_l.putalpha(m.point(lambda v: int(v * .80)))
        im.alpha_composite(body_l)
        b = Image.new('L', (NW, NH)); ImageDraw.Draw(b).rounded_rectangle((1, 1, NW - 2, NH - 2), 44, outline=255, width=2)
        im.alpha_composite(mask_rgba(b.point(lambda v: int(v * .10)), (255, 255, 255)))
        av = bakery_avatar(96); im.alpha_composite(av, (28, (NH - 96) // 2))
        bd = app_badge(40)
        im.alpha_composite(bd, (28 + 96 - 34, (NH - 96) // 2 + 96 - 36))
        tx = 150
        tt = ui_text(title, inter(34, 'SemiBold'), (245, 245, 247)); im.alpha_composite(tt, (tx, 30))
        nw = ui_text('now', inter(29, 'Regular'), (160, 160, 166)); im.alpha_composite(nw, (NW - 30 - nw.width, 34))
        bb = ui_text(body, inter(34, 'SemiBold' if bold_body else 'Regular'), (236, 236, 240)); im.alpha_composite(bb, (tx, 88))
        return im
    return C(('notif', title, body, bold_body), mk)


def notif_shadow():
    def mk():
        P = 40; m = Image.new('L', (NW + 2 * P, NH + 2 * P)); ImageDraw.Draw(m).rounded_rectangle((P, P + 10, P + NW, P + NH + 10), 44, fill=255)
        return mask_rgba(m.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * .55)), (0, 0, 0))
    return C('nshadow', mk)


def notif_stack(ctx, t, items, top=236, layer='screen', out_t=None):
    """items: [(t_arrive, title, body, bold)] — newest on top; each drops in from above (0.16 s, slight overshoot) and
    pushes the older ones down one slot; the 4th+ fade away. out_t: everything flicks up and out."""
    arrived = [it for it in items if t >= it[0]]
    if not arrived: return
    n = len(arrived)
    slot_h = NH + 16
    k_out = 0.0 if out_t is None else ein(clamp((t - out_t) / .14))
    for j, (ta, title, body, bold) in enumerate(arrived):
        rank = n - 1 - j                                   # 0 = newest
        # each newer arrival pushes this card down one slot (eased)
        y = top + slot_h * sum(eout(clamp((t - arrived[i][0]) / .16)) for i in range(j + 1, n))
        k_in = clamp((t - ta) / .16)
        if rank == 0 and k_in < 1:
            y = lerp(top - NH - 120, top, back(k_in, 1.4))
        alpha = 1.0 if rank < 3 else max(0., 1 - (t - arrived[j + 3][0]) / .08)
        if rank == 0: alpha = min(alpha, clamp(k_in * 3))
        y -= k_out * (y + NH + 40)
        if alpha <= .02: continue
        card = notif_card(title, body, bold)
        ctx.add(layer, notif_shadow(), W / 2, y + NH / 2, alpha=alpha * .9)
        ctx.add(layer, card, W / 2, y + NH / 2, glass=18, alpha=alpha)


# ================================================================== Instagram comment sheet + iOS keyboard (dark)
IG_BLUE = (0, 149, 246)
KB_ROWS = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
KB_M, KB_G, KB_KH, KB_RG, KB_TOP = 8, 14, 122, 28, 22
KB_KW = (W - 2 * KB_M - 9 * KB_G) / 10
EMO_H, INP_H = 106, 132
KB_H = KB_TOP + 4 * KB_KH + 3 * KB_RG + 96
SHEET_H = EMO_H + INP_H + KB_H
FIELD = (132, EMO_H + 18, 1052, EMO_H + 18 + 96)          # x0, y0, x1, y1 inside the sheet
TXT_X = FIELD[0] + 34


def key_rect(ch):
    """(x0, y0, x1, y1) of a letter key inside the keyboard area (y from the keyboard top)."""
    for r, row in enumerate(KB_ROWS):
        if ch in row:
            i = row.index(ch)
            if r == 0: x0 = KB_M + i * (KB_KW + KB_G)
            elif r == 1: x0 = KB_M + (KB_KW + KB_G) / 2 + i * (KB_KW + KB_G)
            else: x0 = KB_M + 1.5 * (KB_KW + KB_G) + i * (KB_KW + KB_G)
            y0 = KB_TOP + r * (KB_KH + KB_RG)
            return x0, y0, x0 + KB_KW, y0 + KB_KH
    raise KeyError(ch)


def _rr(d, box, r, fill):
    d.rounded_rectangle(tuple(int(round(v)) for v in box), r, fill=fill)


def sheet_base():
    """the static sheet: emoji reactions row, input row (avatar, empty field, placeholder), keyboard."""
    def mk():
        S = 2
        im = Image.new('RGBA', (W * S, SHEET_H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, W * S, SHEET_H * S + 80), 34 * S, fill=(16, 16, 18, 255))
        # keyboard panel
        d.rectangle((0, (EMO_H + INP_H) * S, W * S, SHEET_H * S), fill=(30, 30, 32, 255))
        d.line((0, (EMO_H + INP_H) * S, W * S, (EMO_H + INP_H) * S), fill=(46, 46, 50, 255), width=2)
        ky = (EMO_H + INP_H) * S
        def key(box, fill, lab=None, f=None, col=(255, 255, 255)):
            x0, y0, x1, y1 = box
            _rr(d, (x0 * S, ky + (y0 + 3) * S, x1 * S, ky + (y1 + 3) * S), 11 * S, (12, 12, 14, 255))   # key shadow
            _rr(d, (x0 * S, ky + y0 * S, x1 * S, ky + y1 * S), 11 * S, fill)
            if lab:
                d.text(((x0 + x1) / 2 * S, ky + (y0 + y1) / 2 * S), lab, font=f, fill=col, anchor='mm')
        fk = ImageFont.truetype(INTER % 'Regular', 50 * S); fs = ImageFont.truetype(INTER % 'Regular', 36 * S)
        for row in KB_ROWS:
            for ch in row: key(key_rect(ch), (92, 92, 96, 255), ch, fk)
        r3 = KB_TOP + 2 * (KB_KH + KB_RG)
        key((KB_M, r3, KB_M + 1.35 * KB_KW, r3 + KB_KH), (62, 62, 66, 255), '⇧', ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 50 * S))
        key((W - KB_M - 1.35 * KB_KW, r3, W - KB_M, r3 + KB_KH), (62, 62, 66, 255), '⌫', ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 46 * S))
        r4 = KB_TOP + 3 * (KB_KH + KB_RG)
        key((KB_M, r4, KB_M + 1.25 * KB_KW, r4 + KB_KH), (62, 62, 66, 255), '123', fs)
        key((KB_M + 1.25 * KB_KW + KB_G, r4, KB_M + 2.25 * KB_KW + KB_G, r4 + KB_KH), (62, 62, 66, 255))
        key((KB_M + 2.25 * KB_KW + 2 * KB_G, r4, W - KB_M - 2.4 * KB_KW - KB_G, r4 + KB_KH), (92, 92, 96, 255), 'space', fs)
        key((W - KB_M - 2.4 * KB_KW, r4, W - KB_M, r4 + KB_KH), (62, 62, 66, 255), 'return', fs)
        # home indicator
        hy = ky + (KB_H - 34) * S
        _rr(d, ((W / 2 - 140) * S, hy, (W / 2 + 140) * S, hy + 10 * S), 5 * S, (235, 235, 240, 255))
        # input row: avatar + field + placeholder
        fy0, fy1 = FIELD[1], FIELD[3]
        d.rounded_rectangle((FIELD[0] * S, fy0 * S, FIELD[2] * S, fy1 * S), 48 * S, outline=(62, 62, 66, 255), width=2 * S, fill=(16, 16, 18, 255))
        im = im.resize((W, SHEET_H), Image.LANCZOS)
        av_d = 84; av = Image.new('RGBA', (av_d, av_d), (0, 0, 0, 0))
        g = Image.new('RGBA', (av_d, av_d), (58, 60, 70, 255)); dg = ImageDraw.Draw(g)
        dg.ellipse((av_d * .32, av_d * .17, av_d * .68, av_d * .53), fill=(168, 170, 186, 255))
        dg.ellipse((av_d * .14, av_d * .60, av_d * .86, av_d * 1.25), fill=(168, 170, 186, 255))
        g.putalpha(_circle_mask(av_d)); im.alpha_composite(g, (28, int((fy0 + fy1) / 2 - av_d / 2)))
        # emoji reactions
        emos = ['❤️', '🙌', '🔥', '👏', '😢', '😍', '😮', '😂']
        step = (W - 2 * 60) / (len(emos) - 1)
        for i, e in enumerate(emos):
            em = emoji(e, 54); im.alpha_composite(em, (int(60 + i * step - em.width / 2), int(EMO_H / 2 - em.height / 2 + 4)))
        return im
    return C('sheet_base', mk)


def placeholder():
    return ui_text('Add a comment for lumarc_studio…', inter(36, 'Regular'), (150, 150, 156))


def typed_text(n):
    def mk():
        s = 'LUMARC'[:n]; f = inter(52, 'Medium')
        l, tp, r, b = f.getbbox('LUMARC'); im = Image.new('RGBA', (r - l + 12, b - tp + 12), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((6 - l, 6 - tp), s, font=f, fill=(250, 250, 252))
        return im, (f.getlength(s) if s else 0) + 6 - l
    return C(('typed', n), mk)


def key_popup(ch):
    """iOS key-press balloon (letter enlarged above the key) as RGBA + its anchor offset (key top-left inside it)."""
    def mk():
        S = 3; kw, kh = KB_KW, KB_KH; pw, ph = kw * 1.5, kh * 1.18
        Wd, Hd = pw + 20, ph + kh + 20
        im = Image.new('RGBA', (int(Wd * S), int(Hd * S)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cx = Wd / 2; col = (126, 126, 132, 255)
        px0, py0 = cx - pw / 2, 4
        _rr(d, (px0 * S, py0 * S, (px0 + pw) * S, (py0 + ph) * S), 16 * S, col)
        kx0, ky0 = cx - kw / 2, py0 + ph - 10
        _rr(d, (kx0 * S, ky0 * S, (kx0 + kw) * S, (ky0 + kh - 6) * S), 11 * S, col)
        d.polygon([(px0 * S, (py0 + ph - 18) * S), ((px0 + pw) * S, (py0 + ph - 18) * S), ((kx0 + kw) * S, (ky0 + 26) * S), (kx0 * S, (ky0 + 26) * S)], fill=col)
        d.text((cx * S, (py0 + ph * .48) * S), ch, font=ImageFont.truetype(INTER % 'Regular', 84 * S), fill=(255, 255, 255, 255), anchor='mm')
        im = im.resize((int(Wd), int(Hd)), Image.LANCZOS)
        sh = mask_rgba(im.getchannel('A').filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .5)), (0, 0, 0))
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, 4)); out.alpha_composite(im)
        return out, (kx0, ky0)
    return C(('kpop', ch), mk)


def comment_sheet(t, t_up, spell, t_post, t_down):
    """the sheet image at time t (None when hidden) and its top y on screen. spell = [(letter, onset)]."""
    if t < t_up or t >= t_down + .24: return None, None
    k_up = expo((t - t_up) / .30)
    k_dn = ein(clamp((t - t_down) / .22))
    y = H - SHEET_H * k_up + (SHEET_H + 40) * k_dn
    im = sheet_base().copy()
    n = sum(1 for _, ts in spell if t >= ts - .01)
    if t >= t_post + .05: n = 0                                     # posted: the field clears
    fy0, fy1 = FIELD[1], FIELD[3]
    if n == 0:
        ph = placeholder(); im.alpha_composite(ph, (TXT_X - 4, int((fy0 + fy1) / 2 - ph.height / 2)))
        caret_x = TXT_X - 2
    else:
        tx, adv = typed_text(n); im.alpha_composite(tx, (TXT_X - 6, int((fy0 + fy1) / 2 - tx.height / 2)))
        caret_x = TXT_X - 6 + adv + 3
    # caret: solid while typing, blinking when idle
    typing = spell[0][1] - .05 <= t <= spell[-1][1] + .25
    blink = int((t - t_up) / .5) % 2 == 0
    if (typing or blink) and t < t_post + .05 and k_up > .6:
        d = ImageDraw.Draw(im); d.rectangle((int(caret_x), fy0 + 26, int(caret_x) + 3, fy1 - 26), fill=IG_BLUE + (255,))
    # Post
    pressed = t_post <= t < t_post + .1
    pa = .42 if n == 0 else (.55 if pressed else 1.0)
    po = ui_text('Post', inter(36, 'SemiBold'), IG_BLUE)
    im.alpha_composite(E.fade(po, pa), (FIELD[2] - 36 - po.width, int((fy0 + fy1) / 2 - po.height / 2)))
    # key press balloons
    ky = EMO_H + INP_H
    for ch, ts in spell:
        if ts - .02 <= t < ts + .13:
            x0, y0, x1, y1 = key_rect(ch)
            pop, (ax, ay) = key_popup(ch)
            im.alpha_composite(pop, (int(x0 - ax), int(ky + y0 - ay)))
    return im, y


# ================================================================== LUMARC lower third (mockumentary chip)
LT_W, LT_H = 560, 228


def lt_card():
    """dark glass name chip: lavender bar, LUMARC wordmark, 'licensed brand therapist'."""
    def mk():
        S = 2; im = Image.new('RGBA', (LT_W * S, LT_H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, LT_W * S - 1, LT_H * S - 1), 32 * S, fill=(14, 12, 22, 170))
        d.rounded_rectangle((1, 1, LT_W * S - 2, LT_H * S - 2), 32 * S, outline=(255, 255, 255, 36), width=2)
        im = im.resize((LT_W, LT_H), Image.LANCZOS)
        bar = E.rounded(E.gradient(6, LT_H - 60, [(120, 140, 255), (150, 120, 255), (190, 130, 255)]).convert('RGBA'), 3)
        im.alpha_composite(bar, (28, 30))
        lg = E.logo(400); im.alpha_composite(lg, (40, 10))
        ds = mask_rgba(tracked_mask('licensed brand therapist', E.font(40, 500), 1.2), (238, 232, 222))
        im.alpha_composite(ds, (56, 146))
        return im
    return C('ltcard2', mk)


def lower_third(ctx, t, t_in, x=64, y=1150, layer='screen', t_out=None):
    """the chip wipes open from its bar (glass blur behind), content slides in with it."""
    if t < t_in: return
    k = eout(clamp((t - t_in) / .30))
    a_out = 1.0 if t_out is None else 1 - clamp((t - t_out) / .12)
    if a_out <= .01: return
    card = lt_card()
    w = max(8, int(LT_W * k))
    piece = card.crop((0, 0, w, LT_H))
    ctx.add(layer, piece, x + int(-20 * (1 - k)), y, center=False, glass=14, alpha=min(1., k * 2) * a_out)


# ================================================================== end card (brand space, glass, logo, type)
HZ_Y, HZ_R = 1560, 1700


def space():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        col = np.zeros((H, W, 3), np.float32) + np.array([10, 10, 17], np.float32)
        r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - 820) / (H * .30)) ** 2)
        col += (np.clip(1 - r, 0, 1) ** 2.2)[..., None] * np.array([46, 32, 112], np.float32)
        cy = HZ_Y + HZ_R
        d = np.sqrt((xx - W / 2) ** 2 + (yy - cy) ** 2) - HZ_R
        fall = np.exp(-((xx - W / 2) / 520) ** 2)
        hue = np.clip(xx / W, 0, 1)[..., None]
        rimc = np.array([96, 124, 255], np.float32) * (1 - hue) + np.array([176, 104, 255], np.float32) * hue
        rim = np.exp(-(d / 2.6) ** 2) * fall
        atmo = np.where(d > 0, np.exp(-np.clip(d, 0, None) / 70), np.exp(np.clip(d, None, 0) / 14)) * fall
        haze = np.where(d > 0, np.exp(-d / 260), 0) * fall
        inside = d < 0
        col = np.where(inside[..., None], col * .45 + np.array([8, 7, 16], np.float32) * (1 - np.exp(d / 400))[..., None], col)
        col += rimc * (rim[..., None] * 1.25 + atmo[..., None] * .55 + haze[..., None] * .22)
        col += np.array([255, 255, 255], np.float32) * (np.exp(-(d / 1.4) ** 2) * fall ** 3 * .45)[..., None]
        v = 1 - .55 * np.clip(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .45) / (H * .62)) ** 2 - .15, 0, 1)
        return Image.fromarray(np.clip(col * v[..., None], 0, 255).astype(np.uint8)).convert('RGBA')
    return C('space', mk)


def bokeh_sprite(r, col):
    def mk():
        s = int(r * 2 + 8); y, x = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
        d = np.sqrt(x * x + y * y) / r
        a = np.clip((1.0 - d) / .35, 0, 1) ** 1.5 * (.7 + .3 * np.clip((d - .5) / .4, 0, 1))   # soft defocused disc
        im = Image.new('RGBA', (s, s), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.filter(ImageFilter.GaussianBlur(r * .08 + .8))
    return C(('bokeh', r, col), mk)


MOTES = [  # x, y, radius, alpha, drift x/y px/s, colour (kept clear of the type column)
    (130, 400, 40, .16, 6, -9, (70, 100, 255)), (950, 330, 26, .18, -5, -7, (150, 80, 255)),
    (930, 1500, 54, .12, -4, -6, (110, 80, 255)), (120, 1240, 18, .22, 7, -10, (120, 130, 255)),
    (700, 210, 12, .22, 3, -8, (170, 140, 255)), (1000, 860, 30, .13, -6, -9, (140, 70, 255)),
    (260, 1760, 22, .16, 4, -12, (90, 110, 255)),
]


def end_motes(img, lt, alpha):
    if alpha <= .02: return
    for i, (x, y, r, a, vx, vy, col) in enumerate(MOTES):
        px = x + vx * lt + 10 * math.sin(lt * .6 + i); py = y + vy * lt
        tw = .8 + .2 * math.sin(lt * 1.3 + i * 1.7)
        sp = bokeh_sprite(r, col)
        img.alpha_composite(E.fade(sp, min(1, a * alpha * tw * 2.0)), (int(px - sp.width / 2), int(py - sp.height / 2)))


def frost(fr, k):
    """heavy blur + deep-violet duotone; k 0..1 = glass rising (blur radius ramps with k, graded on the blur)."""
    if k <= .02: return fr
    ke = eout(k)
    small = fr.convert('RGB').resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(9 * (.35 + .65 * ke)))
    a = np.asarray(small, np.float32) / 255
    L = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    L = np.clip((L - .05) * 1.25, 0, 1) ** 1.35
    c0 = np.array([12, 11, 20], np.float32); c1 = np.array([40, 28, 98], np.float32); c2 = np.array([118, 96, 226], np.float32)
    col = c0 + (c1 - c0) * np.clip(L * 2.4, 0, 1)[..., None] + (c2 - c1) * (np.clip(L * 2.4 - 1, 0, 1) * .55)[..., None]
    h, w = col.shape[:2]; y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    col *= (1 - .7 * np.clip(((x - w / 2) / (w * .7)) ** 2 + ((y - h * .44) / (h * .6)) ** 2 - .12, 0, 1))[..., None]
    if k < 1: col = a * 255 + (col - a * 255) * ke
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert('RGBA')


LOGO_W = 720
GP = 150


def logo_img(): return C('logo', lambda: E.logo(LOGO_W))


def logo_glow():
    def mk():
        lg = logo_img()
        a = Image.new('L', (lg.width + 2 * GP, lg.height + 2 * GP)); a.paste(lg.getchannel('A'), (GP, GP))
        out = Image.new('RGBA', a.size, (0, 0, 0, 0))
        for r, col, m in ((70, (100, 70, 255), .9), (24, (160, 140, 255), .7)):
            g = Image.new('RGBA', a.size, col + (0,)); g.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, m=m: int(min(255, v * m * 1.6))))
            out.alpha_composite(g)
        return out
    return C('lglow', mk)


def hit_field():
    def mk():
        w, h = 1400, 1100
        y, x = np.mgrid[0:h // 4, 0:w // 4].astype(np.float32) * 4
        r2 = ((x - w / 2) / 520) ** 2 + ((y - h / 2) / 330) ** 2
        f = np.exp(-r2 * 1.4)[..., None] * np.array([96, 72, 230], np.float32) \
            + np.exp(-r2 * 5)[..., None] * np.array([60, 50, 120], np.float32) \
            + np.exp(-(((x - w / 2) / 680) ** 2 + ((y - h / 2) / 16) ** 2))[..., None] * np.array([120, 120, 255], np.float32)
        return np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32)
    return C('hitf', mk)


def add_light_field(img, field, k, x0, y0):
    if k <= .01: return img
    a = np.asarray(img.convert('RGB'), np.float32)
    h, w = field.shape[:2]
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe > xs and ye > ys:
        a[ys:ye, xs:xe] += field[ys - y0:ye - y0, xs - x0:xe - x0] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def shock(img, t, t0, cx, cy):
    k = (t - t0) / .6
    if not 0 <= k < 1: return img
    lay = Image.new('L', (W // 2, H // 2)); d = ImageDraw.Draw(lay)
    for R0, wm, am, dl in ((40, .7, .55, 0), (10, .45, .3, .08)):
        kk = clamp((t - t0 - dl) / .6)
        if kk <= 0: continue
        R = (R0 + 1150 * eout(kk)) / 2; wd = max(1, int((18 * (1 - kk) + 2) * wm / 2))
        d.ellipse((cx / 2 - R, cy / 2 - R * .62, cx / 2 + R, cy / 2 + R * .62), outline=int(255 * am * (1 - kk) ** 1.4), width=wd)
    g = lay.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    add = np.asarray(g, np.float32)[..., None] / 255 * np.array([160, 150, 255], np.float32)
    o = np.asarray(img.convert('RGB'), np.float32) + add
    return Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).convert('RGBA')


def ink_mask(key, img, lo, hi):
    return C(('ink', key), lambda: np.clip((np.asarray(img.getchannel('A'), np.float32) - lo) / (hi - lo), 0, 1))


def end_word(text, size, wght, grad):
    """end-card word: white or LUMARC gradient, soft dark shadow, + bare glyph mask (for the sheen)."""
    def mk():
        f = E.font(size, wght); l, _, r, _ = f.getbbox(text); _, t, _, b = f.getbbox('Hgy'); pad = 30
        w, h = r - l + 2 * pad, b - t + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        out.alpha_composite(mask_rgba(m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .8)), (4, 2, 14)), (0, 3))
        if grad:
            g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
            out.alpha_composite(mask_rgba(m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .45)), (120, 90, 255)))
            out.alpha_composite(g)
        else:
            out.alpha_composite(mask_rgba(m, E.WHITE))
        return out, r - l, np.asarray(m, np.float32) / 255
    return C(('ew', text, size, wght, grad), mk)


def end_line(words, gap=22):
    ims = [end_word(*w) for w in words]
    tot = sum(iw for _, iw, _ in ims) + gap * (len(ims) - 1)
    x = -tot / 2; out = []
    for im, iw, m in ims:
        out.append((im, x + iw / 2, m)); x += iw + gap
    return out


def rise(im, k, dist=46):
    if k >= 1: return im
    if k <= 0: return None
    dy = int(dist * (1 - k))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.paste(im.crop((0, 0, im.width, im.height - dy)), (0, dy))
    return E.fade(out, clamp(k * 2.2))


def end_pill():
    return C('pill', lambda: E.pill('Comment  “LUMARC”', 64, 700, grad=True, padx=86, pady=44))


def end_pill_glow():
    def mk():
        p = end_pill(); a = p.getchannel('A').point(lambda v: 255 if v > 200 else 0)
        big = Image.new('L', (p.width + 200, p.height + 200)); big.paste(a, (100, 100))
        return mask_rgba(big.filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * .7)), (110, 80, 255))
    return C('pillglow', mk)


def end_small(text, size, wght, col):
    return C(('esm', text, size, wght, col), lambda: E.text_im(text, size, wght, col))
