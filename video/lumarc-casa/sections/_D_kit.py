"""_D_kit.py — helpers for s07_final (author D).  Pure functions of t.  The house kit (sections/_house.py) is only
CALLED (state_at / render / its camera projection); its canonical state timeline is never changed.

  * measured word onsets of segs 17-18 (src/tight16k.raw: 5 ms-hop spectrogram + RMS / 80-900 Hz / 1-3 kHz /
    >3.5 kHz band envelopes; plosive = burst after its closure silence, fricative = start of the noise band, vowel after
    a voiced consonant = rise of the 80-900 Hz band) and the caption pages they drive (engine caption look)
  * house layer: HS.render through a camera, graded into the studio, faded at the bottom, + projection of model points;
    a second lot ("a sua") rendered with the SAME camera at a world offset; temporal motion blur (shutter samples)
  * light FX: anamorphic flare, glow spot, sheen restricted to the house hull, glass chips (rewind / play / plus)
  * Instagram comment composer (PT-BR UI: "Adicione um comentário…", Publicar)
  * end card: brand space, logo glow, display type, CTA pill, handle
"""
import math, os, sys
_PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJ not in sys.path: sys.path.insert(0, _PROJ)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS

W, H, FPS = E.W, E.H, E.FPS
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
WHITE, MUTED, NIGHT = (250, 249, 246), (166, 166, 184), (14, 14, 20)
IG_BLUE = (0, 149, 246)

def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def sio(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def eo(x, p=3): x = clamp(x); return 1 - (1 - x) ** p
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def C(k, fn): return E.cached(('D',) + (k if isinstance(k, tuple) else (k,)), fn)
def scale_im(im, s, lanczos=False):
    if abs(s - 1) < .005: return im
    return im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.LANCZOS if lanczos else Image.BILINEAR)
def decay(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def kick(t, t0, dur=.24):
    """0 -> 1 -> 0 punch after t0 (fast attack, smooth release)."""
    if t < t0 or t > t0 + dur: return 0.0
    u = (t - t0) / dur
    return math.sin(math.pi * min(1.0, u * 2.4)) * (1 - u) if u < 1 else 0.0

# ------------------------------------------------------------------------------------------------ measured onsets (s)
# seg 17 "Com edição… | as pessoas entram."
#   COM k: voicing rises 32.875 (kit 32.86) | EDIÇÃO e ~32.98, dʒ 33.12, ç (s-noise, no voicing) 33.25, -ÇÃO vowel 33.38 |
#   (pause 33.55-34.04) AS a 34.04 (weak), full vowel 34.105 | PESSOAS p burst 34.27, ss 34.37 | ENTRAM: linked z of
#   "pessoas" 34.62-34.70, "en" vowel 34.71 | -TRAM t closure 34.89-34.92, burst 34.923
O_COM, O_EDICAO, O_DI, O_SS, O_CAO = 32.87, 32.98, 33.12, 33.25, 33.38
O_AS, O_PESSOAS, O_ENTRAM, O_TRAM = 34.08, 34.27, 34.70, 34.92
# seg 18 "Quer construir | a sua? | Comenta “LUMARC”."
#   QUER k burst 35.203 | CONSTRUIR k closure 35.33-35.355, burst 35.358 | "ir a" voiced to 35.79 (the "a" is linked into
#   "construi-ra", ~35.70) | SUA s 35.79 (strongest hiss of the line), "ua" vowel 35.92 | (pause 36.11-36.78) COMENTA k
#   burst 36.78, -TA t burst 37.12 | LUMARC: l 37.21 (F2 drop after the "ta" vowel), u 37.32 (level jumps +5 dB, low
#   F2), m 37.42 (nasal: level drops 4-5 dB), -MAR- a vowel 37.50 (1-3 kHz band +25 dB), r flap 37.59, final k burst
#   37.735 (after the 37.67-37.73 closure), voice ends 37.84   [review: u / m re-measured, were 37.26 / 37.31]
O_QUER, O_CONSTRUIR, O_A18, O_SUA, O_UA = 35.20, 35.36, 35.70, 35.79, 35.92
O_COMENTA, O_TA, O_LUMARC, O_MAR, O_RC, O_VEND = 36.78, 37.12, 37.21, 37.50, 37.735, 37.84
TYPE_T = (37.21, 37.32, 37.42, 37.50, 37.59, 37.73)           # L U M A R C — each letter on its own phoneme

def jump_t(i):
    """first 30 fps frame that shows segment i's pose (the avatar takes the NEAREST 25 fps source frame)."""
    t0 = E.TL[i]['t0']; k = int(round(t0 * 25))
    return next(j for j in range(int(t0 * 30) - 3, int(t0 * 30) + 4) if E.Avatar._k_of(j / 30) >= k) / 30
J17, J18 = jump_t(17), jump_t(18)                             # 32.80, 35.1667

# caption pages: words = [(TEXT, onset, emphasis)]; a page shows [a, z)
PAGES = [   # shot A pages stay on ONE line (a second line would sit on his chin / below the safe area)
    dict(a=32.84, z=33.98, words=[('COM', O_COM, 0), ('EDIÇÃO…', O_EDICAO, 1)]),
    dict(a=34.04, z=O_ENTRAM - .02, words=[('AS', O_AS, 0), ('PESSOAS', O_PESSOAS, 0)]),
    dict(a=O_ENTRAM - .02, z=J18 - .001, words=[('ENTRAM.', O_ENTRAM, 1)]),
    dict(a=J18, z=35.68, words=[('QUER', O_QUER, 0), ('CONSTRUIR', O_CONSTRUIR, 0)]),
    dict(a=35.66, z=36.76, words=[('A', O_A18, 0), ('SUA?', O_SUA, 1)]),
]

def _layout(words, base, maxw=900):
    """word items + (x, y) offsets; wraps into lines wider than maxw (same rule as the engine's captions)."""
    items = []
    for (txt, t0, em) in words:
        sz = int(base * (1.2 if em else 1.0)); l, t_, r, b = E.font(sz).getbbox(txt)
        if r - l > maxw: sz = int(sz * maxw / (r - l)); l, t_, r, b = E.font(sz).getbbox(txt)
        items.append([txt, t0, em, sz, r - l])
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

def captions(ctx, t, y=1560, base=92, pages=PAGES, x=540, alpha=1.0):
    """the engine's caption look (word pop, gradient emphasis) on the measured onsets. Screen layer."""
    for p in pages:
        if not (p['a'] <= t < p['z']): continue
        ws = p['words']
        for k, (it, cx, cy) in enumerate(_layout(ws, base)):
            txt, t0, em, sz, _ = it
            if t < t0 - .02: continue
            t1 = ws[k + 1][1] if k + 1 < len(ws) else p['z']
            lt = t - t0 + .02; s = .72 + .28 * back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            img, _ = E.word_img(txt, sz, 'grad' if em else 'white')
            a = alpha
            if lt < .05: a *= lt / .05
            if p['z'] - t < .06: a *= max(0, (p['z'] - t) / .06)
            ctx.add('screen', scale_im(img, s), x + cx, y + cy, alpha=a)

def kinetic_word(ctx, t, txt, t0, y, size=104, style='white', layer='screen', alpha=1.0):
    """one big word popping on its onset (engine pop curve)."""
    if t < t0 - .02: return
    lt = t - t0 + .02; s = (.72 + .28 * back(lt / .18, 1.6)) * (1.04 if .04 < lt < .30 else 1.0)
    img = E.word_img(txt, size, style)[0]
    ctx.add(layer, scale_im(img, s), 540, y, alpha=clamp(lt / .05) * alpha)

# ------------------------------------------------------------------------------------------------ studio / avatar
def studio_bg(dim=.42, blur=12.0):
    """the studio plate, defocused + dimmed (the house and he are in front of it). Cached."""
    def mk():
        im = E.studio().convert('RGB').filter(ImageFilter.GaussianBlur(blur))
        a = np.asarray(im, np.float32) * (1 - dim)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return C(('studio', dim, blur), mk)

# ------------------------------------------------------------------------------------------------ cameras
def cam_mix(a, b, k):
    out = {}
    for key in ('yaw', 'pitch', 'dist', 'fov', 'roll'):
        d = 0.0 if key == 'roll' else 30.0
        out[key] = lerp(a.get(key, d), b.get(key, d), k)
    out['target'] = tuple(lerp(np.array(a['target'], float), np.array(b['target'], float), k))
    sa, sb = a.get('shift', (0, 0)), b.get('shift', (0, 0))
    out['shift'] = (lerp(sa[0], sb[0], k), lerp(sa[1], sb[1], k))
    return out

def cam_offset(cam, O):
    """the same camera looking at a lot placed at world offset O (render that lot with this camera)."""
    c = dict(cam); c['target'] = tuple(np.array(cam['target'], float) - np.asarray(O, float)); return c

# ------------------------------------------------------------------------------------------------ house layer
def house_grade(img, haze=(7, 5, 16), mul=(.97, .96, 1.0)):
    """sit the maquette in the dark purple studio: atmospheric haze in the blacks (same grade as s03/s04)."""
    luts = []
    for c in range(3):
        luts += [int(min(255, v * mul[c] + haze[c] * (1 - v / 255))) for v in range(256)]
    r, g, b, a = img.split()
    rgb = Image.merge('RGB', (r, g, b)).point(luts)
    return Image.merge('RGBA', (*rgb.split(), a))

def fade_mask(w, h, y0, y1):
    def mk():
        g = np.clip((y1 - np.arange(h, dtype=np.float32)) / max(1, y1 - y0), 0, 1); g = g * g * (3 - 2 * g)
        return Image.fromarray((np.repeat(g[:, None], w, 1) * 255).astype(np.uint8))
    return C(('fade', w, h, y0, y1), mk)

def _premul(im):
    a = np.asarray(im, np.float32); al = a[..., 3:4] / 255.
    return np.concatenate([a[..., :3] * al, al], 2)

def _unpremul(acc):
    al = acc[..., 3:4]
    rgb = np.where(al > 1e-4, acc[..., :3] / np.maximum(al, 1e-4), 0)
    return Image.fromarray(np.clip(np.concatenate([rgb, al * 255], 2), 0, 255).astype(np.uint8), 'RGBA')

def _bounds_y(st, cam, size, gap=0.6, margin=70):
    """vertical extent (rows) of a lot render: lot slab + its floating shadow + the house up to the chimney."""
    lot = st['lot']; L = HS.LOT; k = 1.0 + gap * .06
    pts = [(x, y, z) for x in (-L, L) for z in (-L, L) for y in (0.0, -HS.LOT_TH)]
    pts += [(x * k, -HS.LOT_TH - gap, z * k) for x in (-L, L) for z in (-L, L)]
    pts += [(x, HS.YR + .9, HS.ZH + z) for x in (-HS.HX - .4, HS.HX + .4) for z in (-HS.HZ - .4, HS.HZ + .4)]
    P = np.array(pts, float) * lot['s'] + np.array([0, lot['dy'], 0])
    S, Z = HS._Cam(cam, size[0], size[1]).proj(P)
    if Z.min() < 1.0: return 0, size[1]
    return max(0, int(S[:, 1].min()) - margin), min(size[1], int(S[:, 1].max()) + margin)

def crop_cam(cam, size, y0, y1):
    """camera that renders rows y0..y1 of the full `size` render with the SAME pixel mapping (same focal, same width
    -> the kit's width-relative blur radii are unchanged)."""
    Wf, Hf = size; f = (Hf / 2) / math.tan(math.radians(cam.get('fov', 30)) / 2)
    sh = cam.get('shift', (0, 0)); cxf, cyf = Wf / 2 + sh[0] * Wf, Hf / 2 + sh[1] * Hf
    Hc = y1 - y0
    c = dict(cam); c['fov'] = math.degrees(2 * math.atan((Hc / 2) / f))
    c['shift'] = ((cxf - Wf / 2) / Wf, (cyf - y0 - Hc / 2) / Hc)
    return c

class House:
    """one render of a lot: image + projector into the frame. `O` = world offset of this lot (same camera as the main
    lot, so both share one perspective). `st` may be any canonical state (state_at(t')). `blur` = list of
    (state, cam) shutter samples averaged for motion blur (the main sample is (st, cam)).
    crop=True renders only the rows the lot occupies (same width, same pixel mapping): self.img is that band and
    self.org its top-left in the frame."""
    def __init__(self, st, cam, size, org=(0, 0), t=None, O=(0, 0, 0), ss=2, glow=1.0, fade=None, grade=True,
                 blur=None, alpha=1.0, crop=True):
        self.st, self.O = st, np.asarray(O, float)
        self.cam = cam_offset(cam, self.O) if self.O.any() else cam
        y0, y1 = 0, size[1]
        if crop and not blur and float(np.max(st['fly'])) <= 0:
            y0, y1 = _bounds_y(st, self.cam, size)
            if y1 - y0 < 40: y0, y1 = 0, min(size[1], 40)
        rc = crop_cam(self.cam, size, y0, y1) if (y0, y1) != (0, size[1]) else self.cam
        rs = (size[0], y1 - y0)
        tt = st['t'] if t is None else t
        im = HS.render(st, rc, size=rs, t=tt, ss=ss, glow=glow)
        if blur:
            acc = _premul(im)
            for (s2, c2) in blur:
                c2 = cam_offset(c2, self.O) if self.O.any() else c2
                acc += _premul(HS.render(s2, c2, size=rs, t=s2['t'], ss=1, glow=glow))
            im = _unpremul(acc / (1 + len(blur)))
        if grade: im = house_grade(im)
        if fade is not None or alpha < 1:
            a = im.getchannel('A')
            if fade is not None: a = ImageChops.multiply(a, fade_mask(size[0], size[1], fade[0], fade[1]).crop((0, y0, size[0], y1)))
            if alpha < 1: a = a.point(lambda v: int(v * alpha))
            im.putalpha(a)
        self.img = im
        self.size = rs
        self.org = (org[0], org[1] + y0)
        self._c = HS._Cam(rc, rs[0], rs[1])
    def proj(self, P):
        """frame (x, y) of model points (N, 3) of THIS lot (follows the lot's rise like HS.anchor)."""
        lot = self.st['lot']
        P = np.asarray(P, float).reshape(-1, 3) * lot['s'] + np.array([0, lot['dy'], 0])
        S, Z = self._c.proj(P)
        return S + np.array(self.org, float), Z
    def anchor(self, name): return self.proj([HS.ANCHORS[name]])[0][0]
    def hull(self):
        """convex hull (frame px) of the house volume (walls + roof prism) — mask for light FX on the house only."""
        hx, hz, zc = HS.HX + .35, HS.HZ + .35, HS.ZH
        pts = [(x, y, zc + z) for x in (-hx, hx) for z in (-hz, hz) for y in (0.0, HS.YW)]
        pts += [(x, HS.YR + .25, zc + z) for x in (-.2, .2) for z in (-hz, hz)]
        pts += [(1.8, HS.YR + .65, zc - 2.3)]
        S, _ = self.proj(pts)
        return _hull(S)

def _hull(P):
    P = sorted(map(tuple, np.asarray(P, float)))
    if len(P) < 3: return P
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]

def sheen_house(img, hull, k, org=(0, 0), half=70, strength=.55, slope=-.55, col=(255, 246, 232)):
    """diagonal light band sweeping across the house (masked by its hull and the render's alpha); k 0..1."""
    if not 0 < k < 1 or len(hull) < 3: return img
    w, h = img.size
    xs = [p[0] - org[0] for p in hull]; ys = [p[1] - org[1] for p in hull]
    x0, y0 = int(max(0, min(xs) - 4)), int(max(0, min(ys) - 4)); x1, y1 = int(min(w, max(xs) + 4)), int(min(h, max(ys) + 4))
    if x1 - x0 < 4 or y1 - y0 < 4: return img
    m = Image.new('L', (x1 - x0, y1 - y0)); ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in zip(xs, ys)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(6))
    xx = np.arange(x1 - x0, dtype=np.float32)[None, :] + np.arange(y1 - y0, dtype=np.float32)[:, None] * slope
    lo_, hi_ = xx.min() - 2 * half, xx.max() + 2 * half
    c = lerp(lo_, hi_, k)
    band = np.clip(1 - np.abs(xx - c) / half, 0, 1) ** 1.6 * strength
    A = np.asarray(img.crop((x0, y0, x1, y1)), np.float32)
    mm = band * (np.asarray(m, np.float32) / 255) * (A[..., 3] / 255)
    A[..., :3] += (np.array(col, np.float32) - A[..., :3]) * mm[..., None]
    out = img.copy(); out.paste(Image.fromarray(np.clip(A, 0, 255).astype(np.uint8), 'RGBA'), (x0, y0)); return out

# ------------------------------------------------------------------------------------------------ light FX
def glow_spot(r, col=(154, 77, 255), a=1.0):
    def mk():
        R = max(2, int(r)); g = Image.new('L', (2 * R, 2 * R)); ImageDraw.Draw(g).ellipse((R * .55, R * .55, R * 1.45, R * 1.45), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(R * .28))
        im = Image.new('RGBA', g.size, col + (0,)); im.putalpha(g); return im
    im = C(('spot', int(r), col), mk)
    return E.fade(im, a) if a < 1 else im

def flare(w=620, h=26, col=(255, 210, 150)):
    """anamorphic light streak (a light switching on, seen through a lens)."""
    def mk():
        x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]; y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
        a = np.exp(-(x / .38) ** 2) * np.exp(-(y / .22) ** 2) + .5 * np.exp(-(x / .9) ** 2) * np.exp(-(y / .10) ** 2)
        core = np.exp(-(x / .05) ** 2 - (y / .5) ** 2) * .8
        A = np.clip(a + core, 0, 1)
        im = Image.new('RGBA', (w, h), col + (0,)); im.putalpha(Image.fromarray((A * 255).astype(np.uint8))); return im
    return C(('flare', w, h, col), mk)

def add_light(img, field, k, x0=0, y0=0):
    """additive light: img (RGBA) += field (float32 h x w x 3) * k at offset (x0, y0). Returns new RGBA."""
    if k <= .01: return img
    a = np.asarray(img, np.float32).copy()
    h, w = field.shape[:2]; Hh, Ww = a.shape[:2]
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(Ww, x0 + w), min(Hh, y0 + h)
    if xe > xs and ye > ys:
        a[ys:ye, xs:xe, :3] += field[ys - y0:ye - y0, xs - x0:xe - x0] * k
        if a.shape[2] == 4: a[ys:ye, xs:xe, 3] = np.maximum(a[ys:ye, xs:xe, 3], np.clip(field[ys - y0:ye - y0, xs - x0:xe - x0].max(2) * k * 2, 0, 255))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)

def radial_field(w, h, col, sx, sy, p=1.4):
    def mk():
        y, x = np.mgrid[0:h // 4, 0:w // 4].astype(np.float32) * 4
        r2 = ((x - w / 2) / sx) ** 2 + ((y - h / 2) / sy) ** 2
        f = np.exp(-r2 * p)[..., None] * np.array(col, np.float32)
        return np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32)
    return C(('rfield', w, h, col, sx, sy, p), mk)

# ------------------------------------------------------------------------------------------------ glass chips
def chip(kind, h=112):
    """frosted glass circle with a white glyph: 'rew' (◀◀), 'play' (▶), 'plus' (+). Same family as s04's pause chip."""
    def mk():
        w = h; G = 50; out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
        m = Image.new('L', out.size); ImageDraw.Draw(m).ellipse((G, G, G + w - 1, G + h - 1), fill=255)
        sh = Image.new('RGBA', out.size, (4, 4, 10, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .5)))
        out.alpha_composite(sh, (0, 6))
        out.alpha_composite(E.glass_panel(w, h, radius=h // 2, alpha=.16, border=.6), (G, G))
        ss = 4; gl = Image.new('L', (w * ss, h * ss)); d = ImageDraw.Draw(gl); c = w * ss / 2
        u = h * ss
        if kind == 'rew':
            for k in (0, 1):
                ox = c + (-.05 - .17 * k) * u + .02 * u
                d.polygon([(ox + .16 * u, c - .16 * u), (ox + .16 * u, c + .16 * u), (ox - .02 * u, c)], fill=255)
        elif kind == 'play':
            d.polygon([(c - .11 * u, c - .19 * u), (c - .11 * u, c + .19 * u), (c + .2 * u, c)], fill=255)
        elif kind == 'plus':
            bw, bl = .07 * u, .40 * u
            d.rounded_rectangle((c - bw / 2, c - bl / 2, c + bw / 2, c + bl / 2), bw / 2, fill=255)
            d.rounded_rectangle((c - bl / 2, c - bw / 2, c + bl / 2, c + bw / 2), bw / 2, fill=255)
        gl = gl.resize((w, h), Image.LANCZOS)
        g = Image.new('RGBA', (w, h), WHITE + (0,)); g.putalpha(gl.point(lambda v: int(v * .96)))
        out.alpha_composite(g, (G, G))
        return out
    return C(('chip', kind, h), mk)

def soft_ring(r, k, col=(200, 186, 255), a0=.8):
    """soft expanding light ring (shockwave), drawn at half res and blurred; k 0..1."""
    rr = r * (.2 + .8 * eout(k)); R = int(r) + 30
    im = Image.new('L', (R, R)); d = ImageDraw.Draw(im); c = R / 2
    d.ellipse((c - rr / 2, c - rr * .62 / 2, c + rr / 2, c + rr * .62 / 2), outline=255, width=max(2, int(10 * (1 - k)) + 2))
    im = im.filter(ImageFilter.GaussianBlur(3 + 4 * k)).resize((2 * R, 2 * R), Image.BILINEAR)
    out = Image.new('RGBA', im.size, col + (0,)); out.putalpha(im.point(lambda v: int(v * a0 * (1 - k) ** 1.5))); return out

def ring(r, k, col=(250, 249, 246), wmax=6):
    """expanding ring (tap ripple / shockwave), k 0..1."""
    R = int(r) + 8; im = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0))
    rr = r * (.15 + .85 * eout(k)); a = int(230 * (1 - k) ** 1.6)
    ImageDraw.Draw(im).ellipse((R - rr, R - rr, R + rr, R + rr), outline=col + (a,), width=max(2, int(wmax * (1 - k)) + 2))
    return im

# ------------------------------------------------------------------------------------------------ text helpers
def txt(s, size, wght, col, track=0):
    def mk():
        f = E.font(size, wght)
        if not track:
            l, t, r, b = f.getbbox(s)
            im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0)); ImageDraw.Draw(im).text((4 - l, 4 - t), s, font=f, fill=col)
            return im
        ws = [f.getlength(ch) + track for ch in s]; tw = int(sum(ws) - track) + 8
        l, t, r, b = f.getbbox('ÁGjy')
        im = Image.new('RGBA', (tw, b - t + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
        for ch, wch in zip(s, ws): d.text((x, 4 - t), ch, font=f, fill=col); x += wch
        return im
    return C(('txt', s, size, wght, col, track), mk)

def grad_txt(s, size, wght, cols=None):
    """gradient-filled text (RGBA) + its bare glyph mask (float 0..1)."""
    def mk():
        f = E.font(size, wght); l, t, r, b = f.getbbox(s); _, ta, _, ba = f.getbbox('ÁGjy'); pad = 6
        w, h = r - l + 2 * pad, ba - ta + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - ta), s, font=f, fill=255)
        g = E.gradient(w, h, cols or E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
        return g, np.asarray(m, np.float32) / 255
    return C(('gtxt', s, size, wght, str(cols)), mk)

def circle_mask(d, ss=4):
    m = Image.new('L', (d * ss, d * ss)); ImageDraw.Draw(m).ellipse((0, 0, d * ss - 1, d * ss - 1), fill=255)
    return m.resize((d, d), Image.LANCZOS)

def story_avatar(d):
    """IG story-ring avatar (warm gradient ring, dark gap, generic person) — the viewer ("você")."""
    def mk():
        im = Image.new('RGBA', (d, d), (0, 0, 0, 0))
        ring_ = E.gradient(d, d, [(255, 170, 60), (255, 60, 120), (170, 60, 255)]).convert('RGBA').rotate(-45, Image.BILINEAR)
        ring_.putalpha(circle_mask(d)); im.alpha_composite(ring_)
        g = int(d * .06); dd = d - 2 * g
        gap = Image.new('RGBA', (dd, dd), (16, 16, 22, 255)); gap.putalpha(circle_mask(dd)); im.alpha_composite(gap, (g, g))
        g2 = int(d * .11); d2 = d - 2 * g2
        inner = Image.new('RGBA', (d2 * 4, d2 * 4), (58, 60, 78, 255)); di = ImageDraw.Draw(inner); s4 = d2 * 4
        di.ellipse((s4 * .32, s4 * .16, s4 * .68, s4 * .52), fill=(172, 174, 192, 255))
        di.ellipse((s4 * .14, s4 * .58, s4 * .86, s4 * 1.25), fill=(172, 174, 192, 255))
        inner = inner.resize((d2, d2), Image.LANCZOS); inner.putalpha(circle_mask(d2)); im.alpha_composite(inner, (g2, g2))
        return im
    return C(('sav', d), mk)

# ------------------------------------------------------------------------------------------------ IG comment composer
CB_W, CB_H = 940, 168
CB_TX, CB_TS = 178, 60                       # typed text x, size
def comment_base(focus, active):
    """the composer card (PT-BR): avatar, rounded input field (lit outline when focused), 'Publicar' (muted / IG blue
    once there is text)."""
    def mk():
        card = E.glass_panel(CB_W, CB_H, radius=44, tint=(12, 12, 20), alpha=.70, border=.30)
        sh = Image.new('RGBA', (CB_W + 120, CB_H + 120), (0, 0, 0, 0))
        m = Image.new('L', sh.size); ImageDraw.Draw(m).rounded_rectangle((60, 60, 60 + CB_W, 60 + CB_H), 44, fill=255)
        sh.putalpha(m.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * .55)))
        out = Image.new('RGBA', sh.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, 10)); out.alpha_composite(card, (60, 60))
        out.alpha_composite(story_avatar(100), (60 + 30, 60 + (CB_H - 100) // 2))
        d = ImageDraw.Draw(out)
        fx0, fy0, fx1, fy1 = 60 + 150, 60 + 28, 60 + CB_W - 26, 60 + CB_H - 28
        d.rounded_rectangle((fx0, fy0, fx1, fy1), (fy1 - fy0) // 2, fill=(26, 26, 36, 215),
                            outline=(120, 110, 200, 200) if focus else (78, 78, 96, 200), width=2)
        col = IG_BLUE + (255,) if active else (96, 104, 136, 255)
        pb = txt('Publicar', 38, 700, col)
        out.alpha_composite(pb, (fx1 - 30 - pb.width, (fy0 + fy1) // 2 - pb.height // 2))
        return out
    return C(('cbase', focus, active), mk)

def placeholder():
    return txt('Adicione um comentário…', 40, 400, (150, 150, 168, 255))

def typed_lumarc():
    """'LUMARC' (gradient, bold) + cumulative letter x offsets."""
    def mk():
        f = E.font(CB_TS, 800); g, m = grad_txt('LUMARC', CB_TS, 800)
        xs = [6 + f.getlength('LUMARC'[:i]) for i in range(7)]
        return g, xs
    return C('lum', mk)

def publicar_center():
    """centre of the 'Publicar' label inside comment_base's image (with its 60 px margin)."""
    pb = txt('Publicar', 38, 700, IG_BLUE + (255,))
    fx1 = 60 + CB_W - 26; fy0, fy1 = 60 + 28, 60 + CB_H - 28
    return fx1 - 30 - pb.width / 2, (fy0 + fy1) / 2

# ------------------------------------------------------------------------------------------------ end card
def space():
    """brand night space: deep night gradient, violet light behind the house, a faint horizon glow at the bottom."""
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        col = np.zeros((H, W, 3), np.float32) + np.array([11, 10, 18], np.float32)
        r = np.sqrt(((xx - W / 2) / (W * .70)) ** 2 + ((yy - 930) / (H * .30)) ** 2)
        col += (np.clip(1 - r, 0, 1) ** 2.0)[..., None] * np.array([44, 30, 104], np.float32)
        r2 = np.sqrt(((xx - W / 2) / (W * .55)) ** 2 + ((yy - 330) / (H * .12)) ** 2)
        col += (np.clip(1 - r2, 0, 1) ** 2.2)[..., None] * np.array([26, 22, 70], np.float32)
        # horizon: a thin gradient rim low in the frame + atmosphere above it
        HZ_Y, HZ_R = 1760, 1500
        d = np.sqrt((xx - W / 2) ** 2 + (yy - (HZ_Y + HZ_R)) ** 2) - HZ_R
        fall = np.exp(-((xx - W / 2) / 560) ** 2)
        hue = np.clip(xx / W, 0, 1)[..., None]
        rimc = np.array([96, 124, 255], np.float32) * (1 - hue) + np.array([176, 104, 255], np.float32) * hue
        rim = np.exp(-(d / 2.4) ** 2) * fall
        atmo = np.where(d > 0, np.exp(-np.clip(d, 0, None) / 60), np.exp(np.clip(d, None, 0) / 12)) * fall
        haze = np.where(d > 0, np.exp(-d / 240), 0) * fall
        col = np.where((d < 0)[..., None], col * .5 + np.array([8, 7, 16], np.float32) * (1 - np.exp(d / 400))[..., None], col)
        col += rimc * (rim[..., None] * 1.1 + atmo[..., None] * .45 + haze[..., None] * .18)
        v = 1 - .5 * np.clip(((xx - W / 2) / (W * .78)) ** 2 + ((yy - H * .45) / (H * .62)) ** 2 - .15, 0, 1)
        return Image.fromarray(np.clip(col * v[..., None], 0, 255).astype(np.uint8))
    return C('space', mk)

def bokeh_sprite(r, col):
    def mk():
        s = int(r * 2 + 8); y, x = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
        d = np.sqrt(x * x + y * y) / r
        a = np.clip((1.0 - d) / .35, 0, 1) ** 1.5 * (.7 + .3 * np.clip((d - .5) / .4, 0, 1))
        im = Image.new('RGBA', (s, s), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.filter(ImageFilter.GaussianBlur(r * .08 + .8))
    return C(('bokeh', r, col), mk)

BOKEH = [  # x, y, radius, alpha, drift x/y px/s, colour
    (150, 470, 40, .14, 6, -9, (70, 100, 255)), (930, 390, 26, .16, -5, -7, (150, 80, 255)),
    (930, 1500, 50, .10, -4, -6, (110, 80, 255)), (140, 1330, 18, .20, 7, -10, (120, 130, 255)),
    (700, 210, 12, .20, 3, -8, (170, 140, 255)), (1010, 960, 30, .12, -6, -9, (140, 70, 255)),
    (330, 1700, 22, .14, 4, -12, (90, 110, 255)), (60, 820, 14, .16, 5, -7, (160, 120, 255)),
]

def logo_img(w): return C(('logo', w), lambda: E.logo(w))

def logo_glow(w, GP=120):
    def mk():
        lg = logo_img(w)
        a = Image.new('L', (lg.width + 2 * GP, lg.height + 2 * GP)); a.paste(lg.getchannel('A'), (GP, GP))
        out = Image.new('RGBA', a.size, (0, 0, 0, 0))
        for r, col, m in ((54, (100, 70, 255), 1.1), (16, (170, 150, 255), .8), (4, (235, 230, 255), .5)):
            g = Image.new('RGBA', a.size, col + (0,)); g.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, m=m: int(min(255, v * m * 1.6))))
            out.alpha_composite(g)
        return out
    return C(('lglow', w, GP), mk)

def ink_mask(key, img, lo, hi):
    return C(('ink', key), lambda: np.clip((np.asarray(img.getchannel('A'), np.float32) - lo) / (hi - lo), 0, 1))

def sheen(img, k, mask, half=30, strength=.55, slope=.35):
    """narrow diagonal light band that brightens only the ink (mask = bare glyph shape)."""
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

def rise(im, k, dist=44):
    """text rising out of a mask line (k 0..1)."""
    if k >= 1: return im
    if k <= 0: return None
    dy = int(dist * (1 - k))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.paste(im.crop((0, 0, im.width, im.height - dy)), (0, dy))
    return E.fade(out, clamp(k * 2.2))

def shadowed(im, blur=10, op=.8, dy=3):
    def_ = Image.new('RGBA', im.size, (0, 0, 0, 0))
    pad = blur * 2; out = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new('L', out.size); a.paste(im.getchannel('A'), (pad, pad + dy))
    sh = Image.new('RGBA', out.size, (4, 2, 14, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op)))
    out.alpha_composite(sh); out.alpha_composite(im, (pad, pad)); return out

def headline():
    """'Edição que faz o olho ficar.' — light 'Edição que faz' + bold gradient 'o olho ficar.' (one line)."""
    def mk():
        size = 60
        a = txt('Edição que faz', size, 400, WHITE + (255,))
        b, bm = grad_txt('o olho ficar.', size, 750)
        gap = 4
        w = a.width + gap + b.width; h = max(a.height, b.height)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        # align baselines: both rendered with top at the glyph bbox; use font metrics
        fa = E.font(size, 400); fb = E.font(size, 750)
        ya = 4 - fa.getbbox('Edição que faz')[1]; yb = 6 - fb.getbbox('ÁGjy')[1]
        base = max(ya, yb)
        im.alpha_composite(a, (0, base - ya)); im.alpha_composite(b, (a.width + gap, base - yb))
        m = np.zeros((h, w), np.float32); m[base - yb:base - yb + bm.shape[0], a.width + gap:a.width + gap + bm.shape[1]] = bm
        return shadowed(im), np.pad(m, ((20, 20), (20, 20)))
    return C('headline', mk)

def cta_pill():
    return C('ctapill', lambda: E.pill('Comenta  “LUMARC”', 58, 700, grad=True, padx=78, pady=40))

def cta_glow():
    def mk():
        p = cta_pill(); a = p.getchannel('A').point(lambda v: 255 if v > 200 else 0)
        big = Image.new('L', (p.width + 200, p.height + 200)); big.paste(a, (100, 100))
        g = Image.new('RGBA', big.size, (110, 80, 255, 0)); g.putalpha(big.filter(ImageFilter.GaussianBlur(36)).point(lambda v: int(v * .72)))
        return g
    return C('ctaglow', mk)

def handle_im():
    return C('handle', lambda: shadowed(txt('@lumarc_studio  ·  slumarc.com', 40, 500, (214, 211, 236, 255)), 8, .7))

def tagline_im():
    return C('tagline', lambda: shadowed(txt('SEJA VISTO. SEJA LEMBRADO.', 34, 500, (176, 170, 214, 255), track=6), 8, .7))
