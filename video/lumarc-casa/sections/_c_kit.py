"""_c_kit.py — shared helpers for s05_retencao + s06_vazio (author C).  Pure functions of t; the house kit
(sections/_house.py) is only CALLED (state_at / render / its camera) — its state timeline is never changed.

  * measured word onsets of segs 10-16 (src/tight16k.raw: 5 ms-hop spectrogram + RMS / 80-900 Hz / 1-3 kHz / >3.5 kHz
    band envelopes; plosive = burst after the closure silence, fricative = start of the noise band, vowel after a
    voiced consonant = onset of the 80-900 Hz band) and the caption pages they drive (engine look)
  * house layer (HS.render through a camera, placed in the 1080x1920 world, + projection of model points); a cheap
    low-res variant for defocused plates
  * UI art: play chip, scrubber (progress bar + chapters + knob + time bubble), preview card, retention card, eye +
    lock reticle, image placeholder / photo card, type field, motion streak, wind streaks, tumbleweed, passer-by
"""
import math, os, sys
_PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJ not in sys.path: sys.path.insert(0, _PROJ)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS

W, H, FPS = E.W, E.H, E.FPS
clamp, eout, back = E.clamp, E.eout, E.back
WHITE, MUTED, NIGHT = (250, 249, 246), (166, 166, 184), (14, 14, 20)
GRAD = E.GRAD

# ------------------------------------------------------------------------------------------------ measured onsets (s)
# seg 10 "você assistiu até aqui | porque a casa | tava sendo construída | na sua frente."
#   VOCÊ v 16.735 | ASSISTIU a 16.93 (ss 17.04, tʃ of -tiu 17.30) | ATÉ a 17.45, -TÉ t burst 17.60 |
#   AQUI a 17.76, -QUI k burst 17.85 | PORQUE p burst 18.335 | A 18.62 | CASA k burst 18.72 | TAVA t burst 19.07 |
#   SENDO s 19.25 | CONSTRUÍDA k burst 19.79, stressed Í 19.97 | NA n 20.21 | SUA s 20.30 | FRENTE f 20.52 (vowel 20.585)
O_VOCE, O_ASSISTIU, O_ATE, O_TE, O_AQUI, O_QUI = 16.735, 16.93, 17.45, 17.60, 17.76, 17.85
O_PORQUE, O_A10, O_CASA = 18.335, 18.62, 18.72
O_TAVA, O_SENDO, O_CONSTRUIDA, O_IDA = 19.07, 19.25, 19.79, 19.97
O_NA, O_SUA, O_FRENTE, O_FREN = 20.21, 20.30, 20.52, 20.585
# seg 11 "É isso que | uma boa edição faz:"   É 21.05 | ISSO i 21.17 (ss 21.31) | QUE k 21.52 | UMA u 21.71 |
#   BOA b 21.91 | EDIÇÃO e 22.07 (dʒ 22.15) | FAZ f 22.43
O_E11, O_ISSO, O_QUE, O_UMA11, O_BOA, O_EDICAO11, O_FAZ = 21.05, 21.17, 21.52, 21.71, 21.91, 22.07, 22.43
# seg 12 "dá um motivo | pro seu olho ficar."   DÁ d 22.95 | UM 23.07 | MOTIVO m 23.22, -TI- tʃ burst 23.36 |
#   PRO p burst 23.77 | SEU s 23.86 | OLHO o 24.04 | FICAR f 24.30, stressed -CAR k burst 24.425
O_DA, O_UM12, O_MOTIVO, O_TI, O_PRO, O_SEU, O_OLHO, O_FICAR, O_CAR = 22.95, 23.07, 23.22, 23.36, 23.77, 23.86, 24.04, 24.30, 24.425
# seg 13 "Cada frase, uma imagem."   CADA k burst 24.755 | FRASE f 25.00 | (pause 25.52-25.645) UMA u 25.665 |
#   IMAGEM i 25.82 (-MA- 25.93, -GEM ʒ 26.12)
O_CADA13, O_FRASE, O_UMA13, O_IMAGEM = 24.755, 25.00, 25.665, 25.82
# seg 14 "Cada palavra, um movimento."   CADA k burst 26.47 | PALAVRA p burst 26.74 (-LA- 26.86) | (pause 27.29-27.43)
#   UM 27.43 | MOVIMENTO m 27.48, stressed -MEN- 27.77, -TO t burst 28.11
O_CADA14, O_PALAVRA, O_UM14, O_MOVIMENTO, O_MEN, O_TO = 26.47, 26.74, 27.43, 27.48, 27.77, 28.11
# seg 15 "Sem edição, | você tem um | terreno vazio…"   SEM s 28.376 | EDIÇÃO e 28.56 (ç 28.80) | (pause 29.12-29.43)
#   VOCÊ v 29.435 | TEM t 29.70 | UM 29.80 | TERRENO t burst 29.94 | VAZIO v 30.27 (a 30.29, -ZI- 30.37)
O_SEM, O_EDICAO15, O_VOCE15, O_TEM, O_UM15, O_TERRENO15, O_VAZIO15, O_ZI15 = 28.376, 28.56, 29.435, 29.70, 29.80, 29.94, 30.27, 30.37
# seg 16 "e ninguém para | pra olhar um | terreno vazio."   E 30.858 | NINGUÉM n 30.92, -GUÉM g burst 31.13 |
#   PARA p burst 31.39 | PRA p 31.67 | OLHAR o 31.72 | UM 31.95 | TERRENO t burst 32.10 | VAZIO v 32.38 (-ZI- 32.50)
O_E16, O_NINGUEM, O_GUEM, O_PARA, O_PRA, O_OLHAR, O_UM16, O_TERRENO16, O_VAZIO16 = 30.858, 30.92, 31.13, 31.39, 31.67, 31.72, 31.95, 32.10, 32.38

def jump_t(i):
    """first 30 fps frame showing segment i's pose (the avatar takes the NEAREST 25 fps source frame)."""
    t0 = E.TL[i]['t0']; k = int(round(t0 * 25))
    return next(j for j in range(int(t0 * 30) - 3, int(t0 * 30) + 4) if E.Avatar._k_of(j / 30) >= k) / 30
J10, J11, J12, J13, J14, J15, J16, J17 = (jump_t(i) for i in range(10, 18))   # 16.667 21.0 22.867 24.7 26.4 28.3 30.8 32.8

# caption pages: words = [(TEXT, onset, emphasis)]; a page shows [a, z)
PAGES = [
    dict(a=J10, z=O_ATE - .02, words=[('VOCÊ', O_VOCE, 0), ('ASSISTIU', O_ASSISTIU, 0)]),
    dict(a=O_ATE - .02, z=18.31, words=[('ATÉ', O_ATE, 0), ('AQUI', O_AQUI, 1)]),
    dict(a=18.31, z=19.05, words=[('PORQUE', O_PORQUE, 0), ('A', O_A10, 0), ('CASA', O_CASA, 0)]),
    dict(a=19.05, z=O_CONSTRUIDA - .02, words=[('TAVA', O_TAVA, 0), ('SENDO', O_SENDO, 0)]),
    dict(a=O_CONSTRUIDA - .02, z=20.19, words=[('CONSTRUÍDA', O_CONSTRUIDA, 1)]),
    dict(a=20.19, z=J11, words=[('NA', O_NA, 0), ('SUA', O_SUA, 0), ('FRENTE.', O_FRENTE, 1)]),
    dict(a=J11, z=21.69, words=[('É', O_E11, 0), ('ISSO', O_ISSO, 0), ('QUE', O_QUE, 0)]),
    dict(a=21.69, z=O_EDICAO11 - .02, words=[('UMA', O_UMA11, 0), ('BOA', O_BOA, 0)]),
    dict(a=O_EDICAO11 - .02, z=J12, words=[('EDIÇÃO', O_EDICAO11, 1), ('FAZ:', O_FAZ, 0)]),
    dict(a=J12, z=23.75, words=[('DÁ', O_DA, 0), ('UM', O_UM12, 0), ('MOTIVO', O_MOTIVO, 1)]),
    dict(a=23.75, z=O_FICAR - .02, words=[('PRO', O_PRO, 0), ('SEU', O_SEU, 0), ('OLHO', O_OLHO, 0)]),
    dict(a=O_FICAR - .02, z=J13, words=[('FICAR.', O_FICAR, 1)]),
    # segs 13-14: every word is its own kinetic visual (s05 draws them; no caption line)
    dict(a=J15, z=29.40, words=[('SEM', O_SEM, 0), ('EDIÇÃO,', O_EDICAO15, 0)]),
    dict(a=29.40, z=29.92, words=[('VOCÊ', O_VOCE15, 0), ('TEM', O_TEM, 0), ('UM', O_UM15, 0)]),
    dict(a=29.92, z=O_VAZIO15 - .02, words=[('TERRENO', O_TERRENO15, 0)]),
    dict(a=O_VAZIO15 - .02, z=J16, words=[('VAZIO…', O_VAZIO15, 1)]),
    dict(a=J16, z=31.65, words=[('E', O_E16, 0), ('NINGUÉM', O_NINGUEM, 0), ('PARA', O_PARA, 0)]),
    dict(a=31.65, z=32.08, words=[('PRA', O_PRA, 0), ('OLHAR', O_OLHAR, 0), ('UM', O_UM16, 0)]),
    dict(a=32.08, z=J17, words=[('TERRENO', O_TERRENO16, 0), ('VAZIO.', O_VAZIO16, 1)]),
]
# caption line: y 1605 (glyph body ~1568-1642).  Every shot keeps his beard bottom <= ~1540 (measured on the take:
# the chin reaches take row ~1141 in segs 10-16 -> avatar y <= 400 at s=1), so no caption ever touches his face.
CAP_Y, CAP_BASE = 1605, 92

# ------------------------------------------------------------------------------------------------ small maths
def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def sio(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def eio3(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eo(x, p=3.0): x = clamp(x); return 1 - (1 - x) ** p
def ei(x, p=2.0): x = clamp(x); return x ** p
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def C(k, fn): return E.cached(('C',) + (k if isinstance(k, tuple) else (k,)), fn)
def pulse(t, t0, dur): return 0.0 if t < t0 or t > t0 + dur else math.sin(math.pi * (t - t0) / dur)

def shake(t, t0, amp, dur=.32, freq=19.0, seed=0):
    """decaying shake (dx, dy) px after an impact at t0."""
    if t < t0 or t > t0 + dur: return 0.0, 0.0
    u = clamp((t - t0) / dur); e = (1 - u) ** 2.2 * amp; ph = seed * 1.7
    return (e * .55 * math.sin(2 * math.pi * freq * (t - t0) + ph), e * math.sin(2 * math.pi * freq * 1.13 * (t - t0) + ph + 1.1))

def kick(t, t0, amp, dur=.22):
    """quick punch 0 -> amp -> 0 after t0."""
    if t < t0 or t > t0 + dur: return 0.0
    u = clamp((t - t0) / dur); return amp * math.sin(math.pi * min(1, u * 2.2)) * (1 - u)

def scaled(img, s):
    if abs(s - 1) < .004: return img
    return img.resize((max(1, int(round(img.width * s))), max(1, int(round(img.height * s)))), Image.BILINEAR)

# ------------------------------------------------------------------------------------------------ grading
def _studio_base(blur, z, cy):
    def mk():
        im = E.studio().convert('RGB')
        if z != 1: im = E.zoom(im, z, (540, cy))
        return im.filter(ImageFilter.GaussianBlur(blur)) if blur > .3 else im
    return C(('studio_base', round(blur, 2), round(z, 3), cy), mk)

_SBG = {}
def studio_bg(dim=.30, blur=5.0, sat=1.0, z=1.0, cy=760):
    """the studio plate (zoomed about (540, cy)), defocused + dimmed (+ saturation).  The blur is cached; dim / sat are
    cheap PIL ops on top, memoised on 0.01 steps (small LRU)."""
    key = (round(dim, 2), round(blur, 2), round(sat, 2), round(z, 3), cy)
    if key in _SBG: return _SBG[key]
    im = desat(_studio_base(blur, z, cy), key[2], mul=1 - key[0])
    if len(_SBG) > 48: _SBG.pop(next(iter(_SBG)))
    _SBG[key] = im
    return im

def desat(img, s, cool=0.0, mul=1.0):
    """saturation s (+ optional cool grade, exposure mul) on RGB/RGBA (alpha kept). PIL ops (fast)."""
    a = img.getchannel('A') if img.mode == 'RGBA' else None
    rgb = img.convert('RGB')
    if abs(s - 1) > .004: rgb = Image.blend(rgb.convert('L').convert('RGB'), rgb, s)
    if cool or abs(mul - 1) > .004:
        lut = []
        for f in (1 - .07 * cool, 1 - .02 * cool, 1 + .06 * cool):
            lut += [int(min(255, v * f * mul)) for v in range(256)]
        rgb = rgb.point(lut)
    if a is not None: rgb.putalpha(a)
    return rgb

def house_grade(img, haze=(7, 5, 16), mul=(.97, .96, 1.0)):
    """sit the maquette in the dark purple studio: a touch of haze in the blacks (same grade as s03/s04)."""
    def mk():
        luts = []
        for c in range(3): luts += [int(min(255, v * mul[c] + haze[c] * (1 - v / 255))) for v in range(256)]
        return luts
    luts = C(('hlut', haze, mul), mk)
    r, g, b, a = img.split()
    rgb = Image.merge('RGB', (r, g, b)).point(luts)
    return Image.merge('RGBA', (*rgb.split(), a))

def _fade_mask(w, h, y0, y1):
    def mk():
        g = np.clip((y1 - np.arange(h, dtype=np.float32)) / max(1, y1 - y0), 0, 1); g = g * g * (3 - 2 * g)
        return Image.fromarray((np.repeat(g[:, None], w, 1) * 255).astype(np.uint8))
    return C(('fade', w, h, y0, y1), mk)

# ------------------------------------------------------------------------------------------------ house layer
def cam_mix(a, b, k):
    out = {}
    for key in ('yaw', 'pitch', 'dist', 'fov', 'roll'):
        d = 0.0 if key == 'roll' else 30.0
        out[key] = lerp(a.get(key, d), b.get(key, d), k)
    out['target'] = tuple(lerp(np.array(a['target'], float), np.array(b['target'], float), k))
    sa, sb = a.get('shift', (0, 0)), b.get('shift', (0, 0))
    out['shift'] = (lerp(sa[0], sb[0], k), lerp(sa[1], sb[1], k))
    return out

class House:
    """one render of the house + a projector into the WORLD frame (the render is pasted at `org`, scaled by `up`).
    lowres=k renders at 1/k resolution (ss=1) and scales up: for defocused plates only."""
    def __init__(self, st, cam, size, org=(0, 0), t=None, ss=2, glow=1.0, grade=True, fade=None, lowres=1, people=True):
        self.st, self.cam, self.size, self.org = st, cam, size, org
        rs = (max(8, size[0] // lowres), max(8, size[1] // lowres)) if lowres > 1 else size
        im = HS.render(st, cam, size=rs, t=st['t'] if t is None else t, ss=1 if lowres > 1 else ss, glow=glow, people=people)
        if lowres > 1: im = im.resize(size, Image.BILINEAR)
        im = house_grade(im) if grade else im
        if fade is not None:
            im.putalpha(ImageChops.multiply(im.getchannel('A'), _fade_mask(size[0], size[1], fade[0], fade[1])))
        self.img = im
        self._c = HS._Cam(cam, size[0], size[1])
    def proj(self, P):
        """world-frame (x, y) + depth of model-space points (N, 3) (follows the lot's rise like HS.anchor)."""
        lot = self.st['lot']
        P = np.asarray(P, float).reshape(-1, 3) * lot['s'] + np.array([0, lot['dy'], 0])
        S, Z = self._c.proj(P)
        return S + np.array(self.org, float), Z
    def px_per_m(self, P):
        """screen px per metre at model point P (horizontal)."""
        S, _ = self.proj([P, np.asarray(P, float) + np.array([1.0, 0, 0])])
        return float(np.hypot(*(S[1] - S[0])))

# ------------------------------------------------------------------------------------------------ captions
def _layout(words, base):
    items = []
    for (txt, t0, em) in words:
        sz = int(base * (1.2 if em else 1.0)); l, t_, r, b = E.font(sz).getbbox(txt)
        if r - l > 900: sz = int(sz * 900 / (r - l)); l, t_, r, b = E.font(sz).getbbox(txt)
        items.append([txt, t0, em, sz, r - l])
    lines, cur, cw = [], [], 0
    for it in items:
        add = it[4] + (base * .34 if cur else 0)
        if cur and cw + add > 900: lines.append((cur, cw)); cur, cw = [], 0; add = it[4]
        cur.append(it); cw += add
    lines.append((cur, cw)); out = []; lh = base * 1.12; y0 = -(len(lines) - 1) * lh / 2
    for li, (ln, lw) in enumerate(lines):
        x = -lw / 2
        for it in ln: out.append((it, x + it[4] / 2, y0 + li * lh)); x += it[4] + base * .34
    return out

def captions(ctx, t, y=CAP_Y, base=CAP_BASE, pages=PAGES, x=540, alpha=1.0, layer='screen'):
    """the engine's caption look (word pop on its onset, gradient emphasis) with the measured onsets."""
    ctx.captions = False
    for p in pages:
        if not (p['a'] <= t < p['z']): continue
        ws = p['words']; lay = _layout(ws, base)
        for k, (it, cx, cy) in enumerate(lay):
            txt, t0, em, sz, _ = it
            if t < t0 - .02: continue
            t1 = ws[k + 1][1] if k + 1 < len(ws) else p['z']
            lt = t - t0 + .02; s = .72 + .28 * back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            img, _ = E.word_img(txt, sz, 'grad' if em else 'white')
            a = clamp(lt / .05) * alpha
            if p['z'] - t < .06: a *= max(0, (p['z'] - t) / .06)
            ctx.add(layer, scaled(img, s), x + cx, y + cy, alpha=a)

# ------------------------------------------------------------------------------------------------ light + glass bits
def glow_spot(r, col=(154, 77, 255), a=1.0):
    def mk():
        R = max(2, int(r)); g = Image.new('L', (2 * R, 2 * R)); ImageDraw.Draw(g).ellipse((R * .55, R * .55, R * 1.45, R * 1.45), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(R * .28)); im = Image.new('RGBA', g.size, col + (0,)); im.putalpha(g); return im
    im = C(('spot', int(r), col), mk)
    return E.fade(im, a) if a < 1 else im

def ring(r, k, col=WHITE, width=6):
    """expanding ring (k 0..1) of final radius r."""
    R = int(r) + 8; im = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0))
    rr = r * (.15 + .85 * eout(k)); a = int(235 * (1 - k) ** 1.6)
    if a > 2: ImageDraw.Draw(im).ellipse((R - rr, R - rr, R + rr, R + rr), outline=col + (a,), width=max(2, int(width * (1 - k)) + 2))
    return im

def soft_shadow(w, h, radius, blur=26, opacity=.55, pad=60):
    """drop shadow of a rounded rect (RGBA, size + 2 pad)."""
    def mk():
        m = Image.new('L', (w + 2 * pad, h + 2 * pad)); ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + w, pad + h), radius, fill=255)
        im = Image.new('RGBA', m.size, (2, 2, 8, 0)); im.putalpha(m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))); return im
    return C(('shadow', w, h, radius, blur, opacity, pad), mk)

def rr_mask(w, h, r, ss=3):
    """anti-aliased rounded-rect mask (L)."""
    def mk():
        m = Image.new('L', (w * ss, h * ss)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
        return m.resize((w, h), Image.LANCZOS)
    return C(('rrm', w, h, r), mk)

def text(s, size, wght=700, col=WHITE, a=255):
    """plain anti-aliased text (RGBA, tight + 6 px pad)."""
    def mk():
        f = E.font(size, wght); l, t_, r, b = f.getbbox(s)
        im = Image.new('RGBA', (r - l + 12, b - t_ + 12), (0, 0, 0, 0)); ImageDraw.Draw(im).text((6 - l, 6 - t_), s, font=f, fill=col + (a,))
        return im
    return C(('txt', s, size, wght, col, a), mk)

def play_chip(h=112, kind='play'):
    """frosted glass round chip with a play / rewind / fast-forward glyph (matches s04's pause chip)."""
    def mk():
        w = h; G = 50; out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
        m = Image.new('L', out.size); ImageDraw.Draw(m).ellipse((G, G, G + w - 1, G + h - 1), fill=255)
        sh = Image.new('RGBA', out.size, (4, 4, 10, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .5)))
        out.alpha_composite(sh, (0, 6)); out.alpha_composite(E.glass_panel(w, h, radius=h // 2, alpha=.16, border=.6), (G, G))
        S = 4; gl = Image.new('L', (out.width * S, out.height * S)); d = ImageDraw.Draw(gl); cx, cy = (G + w / 2) * S, (G + h / 2) * S
        for poly in glyph_polys(kind, h * .40 * S): d.polygon([(cx + x, cy + y) for x, y in poly], fill=255)
        gl = gl.resize(out.size, Image.LANCZOS)
        out.alpha_composite(Image.merge('RGBA', [Image.new('L', out.size, 250)] * 3 + [gl]))
        return out
    return C(('chip', h, kind), mk)

def glyph_polys(kind, s):
    """transport glyph polygons centred on (0, 0), size s."""
    if kind == 'play': return [[(-s * .34, -s * .5), (-s * .34, s * .5), (s * .52, 0)]]
    if kind == 'ff': return [[(-s * .62, -s * .42), (-s * .62, s * .42), (0, 0)], [(0, -s * .42), (0, s * .42), (s * .62, 0)]]
    if kind == 'rew': return [[(s * .62, -s * .42), (s * .62, s * .42), (0, 0)], [(0, -s * .42), (0, s * .42), (-s * .62, 0)]]
    return []

def glyph_img(kind, s, col=WHITE):
    def mk():
        S = 4; R = int(s * .8) + 4; m = Image.new('L', (2 * R * S, 2 * R * S)); d = ImageDraw.Draw(m)
        for poly in glyph_polys(kind, s * S): d.polygon([(R * S + x, R * S + y) for x, y in poly], fill=255)
        m = m.resize((2 * R, 2 * R), Image.LANCZOS); im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m); return im
    return C(('glyph', kind, s, col), mk)

def mmss(sec): sec = max(0, int(sec)); return f'{sec // 60}:{sec % 60:02d}'

def mblur_h(img, L):
    """horizontal motion smear of RGBA `img` over L px (premultiplied box), same size."""
    if abs(L) < 2: return img
    n = int(clamp(abs(L) / 5, 3, 14))
    a = np.asarray(img, np.float32); al = a[..., 3:4] / 255.; pm = np.concatenate([a[..., :3] * al, al], 2)
    acc = np.zeros_like(pm)
    for i in range(n):
        dx = int(round(L * (i / (n - 1) - .5)))
        acc += np.roll(pm, dx, 1)
    acc /= n; al2 = acc[..., 3:4]
    rgb = np.where(al2 > 1e-4, acc[..., :3] / np.maximum(al2, 1e-4), 0)
    return Image.fromarray(np.clip(np.concatenate([rgb, al2 * 255], 2), 0, 255).astype(np.uint8), 'RGBA')
