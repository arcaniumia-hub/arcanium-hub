"""_A_kit.py — helpers for s01_hook + s02_virada (author A).  Read-only for everybody else.

* word onsets measured on src/tight16k.raw (5 ms STFT: 80-900 Hz / 1-3 kHz / >3.5 kHz band envelopes + a 1024-pt
  narrow-band formant view for vowel boundaries) -> W[...]
* a 2.5-D shot rig: virtual camera (zoom Z about a focus point) that places him with the engine avatar scale and renders
  the slop wall with parallax straight from its texture (one resample, no engine zoom)
* captions with the engine look on the measured onsets (pages switch on the words, never stacked)
* rich text with colour emoji (Noto Color Emoji) for the generic-AI clichés, grades (cold / drained) as PIL matrices
* THE SLOP WALL: a dense mosaic of generic-AI posts (src/assets + drawn clichés), cold flat light, baked DOF
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import engine as E

W, H, FPS = E.W, E.H, E.FPS
clamp = E.clamp
def lerp(a, b, k): return a + (b - a) * k
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def eo(x, p=3): x = clamp(x); return 1 - (1 - x) ** p
def ei(x, p=2): x = clamp(x); return x ** p
def back(x, s=1.7): return E.back(x, s)
def decay(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def rnd(seed): return np.random.default_rng(seed)
def spring(x, f=3.2, d=5.0):
    """0 -> 1 damped spring (overshoots), x in seconds."""
    if x <= 0: return 0.0
    return 1 - math.exp(-d * x) * math.cos(2 * math.pi * f * x)

OUT = os.path.join(E.HERE, 'out', 'A'); os.makedirs(OUT, exist_ok=True)
CACHE = os.path.join(OUT, 'cache'); os.makedirs(CACHE, exist_ok=True)
def disk_cached(name, fn, ver=1):
    """PIL image cached in memory AND on disk (out/A/cache) — the parallel render processes build it once."""
    def mk():
        p = os.path.join(CACHE, f'{name}_v{ver}.png')
        if os.path.exists(p):
            try: return Image.open(p).copy()
            except Exception: pass
        im = fn(); tmp = p + f'.{os.getpid()}.tmp.png'; im.save(tmp, compress_level=1); os.replace(tmp, p); return im
    return E.cached(('A_disk', name, ver), mk)

GK = E._load('_glasskit_A', os.path.join(E.V, 'lumarc-breakout/sections/_glasskit.py'))

def jump_t(i):
    """timeline time of the first 30 fps frame that shows segment i's pose (the avatar takes the NEAREST 25 fps source
    frame, so the pose can jump one frame before the segment start) -> framing changes must land here."""
    t0 = E.TL[i]['t0']; k = int(round(t0 * 25))
    return next(j for j in range(int(t0 * 30) - 3, int(t0 * 30) + 4) if E.Avatar._k_of(j / 30) >= k) / 30
CUT3 = jump_t(3)            # 9.8333: the scratch (s01's last frame already shows seg 3's pose -> s02 draws it)
CUT5 = jump_t(5)            # 15.70: seg 5's pose shows on s02's last frame -> a whip frame hides it

# ------------------------------------------------------------------------------------------- avatar / rig
FACE = (540.0, 900.0)       # plate point between his eyes and mouth
def avatar_at(ctx, s, fx, fy, alpha=1.0, show=True):
    """place him so his face anchor lands at screen (fx, fy) at scale s (engine scales about the bottom centre).
    Keeps the plate covering the frame bottom + sides (he fills the full width from plate row ~1400 down)."""
    ax = fx - 540 - (FACE[0] - 540) * s
    lim = max(0.0, 540 * (s - 1)); ax = max(-lim, min(lim, ax))
    ay = fy - 1920 + (1920 - FACE[1]) * s
    ay = max(ay, 0.0)                                     # never lift the take's bottom edge into the frame
    ctx.avatar.update(show=show, s=s, x=ax, y=ay, alpha=alpha)
    return 540 + ax + (FACE[0] - 540) * s, 1920 + ay - (1920 - FACE[1]) * s

class Cam:
    """virtual camera: zoom Z about world point (fx, fy) in the 'him plane' (his take at s=1 = the 1080x1920 frame),
    + screen offset (sx, sy) for shakes.  screen = C + (p - F) * Z + S."""
    def __init__(self, Z=1.0, fx=540., fy=960., sx=0., sy=0., rot=0.):
        self.Z, self.fx, self.fy, self.sx, self.sy, self.rot = Z, fx, fy, sx, sy, rot
    def scr(self, x, y): return 540 + (x - self.fx) * self.Z + self.sx, 960 + (y - self.fy) * self.Z + self.sy
    def place_avatar(self, ctx, alpha=1.0):
        fx, fy = self.scr(*FACE)
        return avatar_at(ctx, self.Z, fx, fy, alpha)
    def wall(self, k=.55):
        """the wall's own camera (parallax k: it moves k as much as the him plane)."""
        return Cam(1 + (self.Z - 1) * k, 540 + (self.fx - 540) * k, 960 + (self.fy - 960) * k, self.sx, self.sy)

def mix_cam(a, b, k):
    return Cam(lerp(a.Z, b.Z, k), lerp(a.fx, b.fx, k), lerp(a.fy, b.fy, k), lerp(a.sx, b.sx, k), lerp(a.sy, b.sy, k))

def shake(t, t0, amp, tau=.22, f=21., seed=0):
    """decaying camera shake (dx, dy) after t0 (pure function of t)."""
    if t < t0: return 0.0, 0.0
    u = t - t0; e = amp * math.exp(-u / tau)
    return e * math.sin(2 * math.pi * f * u + seed), e * .8 * math.sin(2 * math.pi * f * 1.27 * u + 1.7 + seed)

# ------------------------------------------------------------------------------------------- grades (PIL matrix: fast, C)
def grade(im, sat=1.0, tint=(1., 1., 1.), lift=(0, 0, 0), contrast=1.0, bright=1.0):
    """colour matrix grade: saturation, per-channel gain (tint), contrast about mid grey, black lift."""
    lr, lg, lb = .299, .587, .114
    s = sat; c = contrast * bright
    M = []
    for i, (g, l) in enumerate(zip(tint, lift)):
        row = [(1 - s) * lr, (1 - s) * lg, (1 - s) * lb]; row[i] += s
        row = [v * c * g for v in row]
        off = (128 * (1 - contrast) * bright) * g + l
        M += row + [off]
    mode = im.mode
    out = im.convert('RGB').convert('RGB', tuple(M))
    if mode == 'RGBA': out = out.convert('RGBA'); out.putalpha(im.getchannel('A'))
    return out

def cold(im, k=1.0):
    """the generic world's look: cold, flat, a bit washed (k = strength)."""
    if k <= .01: return im
    return grade(im, sat=1 - .28 * k, tint=(1 - .07 * k, 1 - .01 * k, 1 + .06 * k), lift=(10 * k, 13 * k, 20 * k), contrast=1 - .14 * k)

def drained(im, k=1.0, keep=0.0):
    """colour drains (k=1 -> almost greyscale, cool)."""
    if k <= .01: return im
    return grade(im, sat=lerp(1, .06 + keep, k), tint=(1 - .03 * k, 1, 1 + .04 * k), contrast=1 - .06 * k, bright=1 - .12 * k)

# ------------------------------------------------------------------------------------------- type
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
INTER = '/usr/share/fonts/opentype/inter/Inter-{}.otf'
ANTON = os.path.join(E.V, 'lumarc-talkinghead/fonts/Anton.ttf')
SERIF_I = '/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf'
_F = {}
def ffont(path, size):
    k = (path, size)
    if k not in _F: _F[k] = ImageFont.truetype(path, size)
    return _F[k]
def inter(size, w='Bold'): return ffont(INTER.format(w), size)

def emoji(ch, size):
    """colour emoji sprite at `size` px tall-ish (rendered at the font's native 109 px, resampled)."""
    def mk():
        f = ImageFont.truetype(EMOJI, 109); im = Image.new('RGBA', (200, 170), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 10), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im
        s = size / 128.0
        return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return E.cached(('A_emoji', ch, size), mk)

def silhouette(ch, size, col=(255, 255, 255)):
    """crisp single-colour silhouette of an emoji at any size (alpha upscaled + re-thresholded)."""
    def mk():
        f = ImageFont.truetype(EMOJI, 109); im = Image.new('RGBA', (200, 170), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox()); a = im.getchannel('A')
        s = size / max(im.width, im.height)
        a = a.resize((max(1, int(im.width * s * 2)), max(1, int(im.height * s * 2))), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
        a = a.point(lambda v: int(clamp((v - 90) / 80.) * 255)).resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        out = Image.new('RGBA', a.size, col + (0,)); out.putalpha(a); return out
    return E.cached(('A_sil', ch, size, col), mk)

def _is_emo(c):
    o = ord(c)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x2B50, 0x2B06, 0x2194, 0x21AA, 0x2728, 0x2764, 0x231A, 0x23F0)

def _runs(text):
    runs, cur, emo = [], '', None
    for c in text:
        if ord(c) in (0xFE0F, 0x200D): continue
        e = _is_emo(c)
        if e:
            if cur: runs.append((cur, False)); cur = ''
            runs.append((c, True))
        else: cur += c
    if cur: runs.append((cur, False))
    return runs

def rich(text, fnt, col, esize=None, stroke=0, stroke_col=(0, 0, 0)):
    """one line of text with colour emoji (RGBA, tight)."""
    def mk():
        asc, desc = fnt.getmetrics(); h = asc + desc; es = esize or int(h * .82)
        parts = []; x = 0
        for s, e in _runs(text):
            if e:
                im = emoji(s, es); parts.append((im, x, (h - im.height) // 2 + int(h * .04))); x += im.width + int(es * .08)
            else:
                w = int(fnt.getlength(s)) + 2 * stroke
                im = Image.new('RGBA', (w + 4, h + 2 * stroke + 4), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((stroke + 2, stroke + 2), s, font=fnt, fill=col + (255,), stroke_width=stroke, stroke_fill=stroke_col + (255,))
                parts.append((im, x, -stroke - 2)); x += w
        out = Image.new('RGBA', (max(1, x + 4), h + 2 * stroke + 8), (0, 0, 0, 0))
        for im, px, py in parts: out.alpha_composite(im, (px, max(0, py + stroke + 2)))
        return out
    return E.cached(('A_rich', text, id(fnt), col, esize, stroke), mk)

def wrap_words(text, fnt, max_w):
    """greedy word wrap (emoji counted ~1 em)."""
    lines, cur = [], ''
    for w in text.split(' '):
        tryl = (cur + ' ' + w).strip()
        wd = sum(fnt.size if e else fnt.getlength(s) for s, e in _runs(tryl))
        if cur and wd > max_w: lines.append(cur); cur = w
        else: cur = tryl
    if cur: lines.append(cur)
    return lines

def text_tracked(s, size, wght, col, track):
    f = E.font(size, wght); w = int(sum(f.getlength(c) for c in s) + track * (len(s) - 1)) + 8
    asc, desc = f.getmetrics(); im = Image.new('RGBA', (w, asc + desc), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
    for c in s: d.text((x, 0), c, font=f, fill=col + (255,)); x += f.getlength(c) + track
    return im

def scaled(im, s):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)

def rotated(im, deg):
    if abs(deg) < .05: return im
    return im.rotate(deg, Image.BICUBIC, expand=True)

def soft_shadow(img, blur=26, opacity=.55, offset=(0, 22)):
    return E.shadow(img, blur, opacity, offset)

# ------------------------------------------------------------------------------------------- captions (engine look)
def page(words, a=None, z=None, base=92):
    """words: [(TEXT, t0, emph)]; a/z default to first onset - .04 / set by pages()."""
    ws = [dict(text=w, t0=t0, emph=bool(e)) for (w, t0, e) in words]
    return dict(a=(ws[0]['t0'] - .04) if a is None else a, z=z, words=ws, base=base)

def chain(pages, end):
    """each page ends where the next starts (-.02); the last one at `end`."""
    for i, p in enumerate(pages):
        if p['z'] is None: p['z'] = (pages[i + 1]['a'] - .02) if i + 1 < len(pages) else end
    return pages

def _layout(p):
    key = ('A_lay', tuple(w['text'] for w in p['words']), tuple(w['emph'] for w in p['words']), p['base'])
    return E.cached(key, lambda: E._layout(dict(words=p['words']), p['base']))

def base_dy(text, sz):
    """vertical offset that puts every word image on a common baseline (accents shift word_img's ink box)."""
    def mk():
        f = E.font(sz); sw = max(3, sz // 22)
        l, t, r, b = f.getbbox(text, stroke_width=sw); l2, t2, r2, b2 = f.getbbox('A', stroke_width=sw)
        return (t + b) / 2 - (t2 + b2) / 2
    return E.cached(('A_bdy', text, sz), mk)

def captions(ctx, t, pages, y, x=W / 2, special=None, alpha=1.0, out_k=None):
    """draw the active page at centre (x, y) like the engine (word pop on its onset, gradient for emphasis).
    special: {TEXT: fn(ctx, t, img, cx, cy, s, a) -> True if it drew the word itself}."""
    ctx.captions = False
    for p in pages:
        if not (p['a'] <= t < p['z']): continue
        ws = p['words']
        for i, (w, sz, cx, cy) in enumerate(_layout(p)):
            t0 = w['t0']
            if t < t0 - .02: continue
            t1 = ws[i + 1]['t0'] if i + 1 < len(ws) else min(p['z'], t0 + .5)
            lt = t - t0 + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            a = clamp(lt / .05) * alpha
            if p['z'] - t < .06: a *= clamp((p['z'] - t) / .06)
            img = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')[0]
            yy = y + cy + base_dy(w['text'], sz) * s
            if special and w['text'] in special and special[w['text']](ctx, t, img, x + cx, yy, s, a): continue
            if a <= .01: continue
            ctx.add('screen', scaled(img, s), x + cx, yy, alpha=a)

def word_box(p, text, y, x=W / 2):
    """(cx, cy, w, h) of a caption word's ink in frame px."""
    for w, sz, cx, cy in _layout(p):
        if w['text'] == text:
            l, tt, r, b = E.font(sz).getbbox(text); return x + cx, y + cy + base_dy(text, sz), r - l, b - tt
    return None

# ------------------------------------------------------------------------------------------- motion blur / light
def mblur(im, vx, vy):
    """directional motion blur along -(vx, vy) px (premultiplied). Returns (img, ox, oy) centre offset."""
    L = math.hypot(vx, vy)
    if L < 1.5: return im, 0.0, 0.0
    n = int(min(16, max(3, L / 3.0)))
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

def smear_frame(fr, dx, dy, n=9):
    """whole-frame directional smear (whip pans)."""
    a = np.asarray(fr.convert('RGB'), np.float32); acc = np.zeros_like(a)
    for i in range(n):
        f = i / (n - 1) - .5; acc += np.roll(np.roll(a, int(round(dx * f)), 1), int(round(dy * f)), 0)
    return Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8))

def light_hit(fr, k, col=(196, 182, 255)):
    """a flash that reads as LIGHT: exposure push + highlight bloom + a faint tint lift (k <= ~.6)."""
    rgb = fr.convert('RGB'); a = np.asarray(rgb, np.float32)
    sm = np.asarray(rgb.resize((W // 4, H // 4), Image.BILINEAR), np.float32)
    lum = sm.mean(2, keepdims=True); hb = sm * np.clip((lum - 80) / 110, 0, 1)
    bloom = np.asarray(Image.fromarray(hb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32)
    y = (a * (1 + 1.7 * k) + bloom * (2.4 * k) + np.array(col, np.float32) * (.20 * k)) / 255.
    y = np.where(y < .72, y, .72 + .28 * (1 - np.exp(-(y - .72) / .28)))
    return Image.fromarray(np.clip(y * 255, 0, 255).astype(np.uint8)).convert('RGBA')

def glow_sprite(r, col, k=1.0):
    def mk():
        n = int(2 * r); yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + .5
        d = np.hypot(xx - r, yy - r) / r; a = np.clip(1 - d, 0, 1) ** 2.2
        im = Image.new('RGBA', (n, n), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return E.cached(('A_glow', r, col), mk)

# ------------------------------------------------------------------------------------------- generic-AI clichés (tiles)
TILE_W, TILE_H = 300, 375                      # 4:5 feed post at wall-texture resolution
def _cover(img, w, h, fx=.5, fy=.5, zoom=1.0):
    c = img.convert('RGB'); sc = max(w / c.width, h / c.height) * zoom
    c = c.resize((int(c.width * sc) + 1, int(c.height * sc) + 1), Image.LANCZOS)
    x0 = int((c.width - w) * fx); y0 = int((c.height - h) * fy)
    return c.crop((x0, y0, x0 + w, y0 + h))

def _grad_img(w, h, cols, diag=True):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx / w * .55 + yy / h * .45) if diag else yy / h
    c = np.array(cols, np.float32); n = len(cols) - 1
    i = np.clip((u * n).astype(int), 0, n - 1); f = (u * n - i)[..., None]
    out = c[i] * (1 - f) + c[np.minimum(i + 1, n)] * f
    return Image.fromarray(out.astype(np.uint8))

def _center_lines(im, lines, fnt, col, y, gap=1.12, stroke=0, stroke_col=(0, 0, 0), esize=None):
    for ln in lines:
        r = rich(ln, fnt, col, esize=esize, stroke=stroke, stroke_col=stroke_col)
        im.alpha_composite(r, ((im.width - r.width) // 2, int(y))); y += fnt.size * gap
    return y

def tile_design(kind, w=TILE_W, h=TILE_H, var=0):
    """one generic-AI post (RGB w x h).  kind: asset name or a drawn cliché."""
    def mk():
        if kind in ('ai_brain', 'robot_hand', 'stock_team', 'ai_selfie', 'ai_planet'):
            im = _cover(E.asset(kind), w, h, .5, .4, 1.0 + .06 * (var % 3)).convert('RGBA')
            over = {'ai_brain': 'O FUTURO É AGORA 🤖', 'robot_hand': 'IA + VOCÊ = 🚀', 'stock_team': 'TRABALHO EM EQUIPE 💼',
                    'ai_selfie': 'segunda motivada ☕✨', 'ai_planet': 'SONHE GRANDE 🌌'}[kind]
            if var % 2 == 0:
                f = ffont(ANTON, int(w * .105)) if kind != 'ai_selfie' else inter(int(w * .075), 'SemiBold')
                band = Image.new('RGBA', (w, int(h * .2)), (0, 0, 0, 0))
                g = np.linspace(.62, 0, band.height, dtype=np.float32)[:, None]
                band.putalpha(Image.fromarray((np.repeat(g, w, 1) * 255).astype(np.uint8)))
                im.alpha_composite(band, (0, 0))
                _center_lines(im, [over], f, (255, 255, 255), h * .05, stroke=2 if kind != 'ai_selfie' else 0)
            return im.convert('RGB')
        if kind in ('quote_a', 'quote_b', 'quote_c'):
            cols = {'quote_a': [(124, 58, 237), (219, 39, 119), (251, 146, 60)], 'quote_b': [(99, 102, 241), (168, 85, 247), (236, 72, 153)],
                    'quote_c': [(14, 165, 233), (139, 92, 246), (217, 70, 239)]}[kind]
            im = _grad_img(w, h, cols).convert('RGBA')
            q = {'quote_a': '“Acredite no processo.” ✨', 'quote_b': '“O sucesso é uma jornada, não um destino.”',
                 'quote_c': '“Seja a sua melhor versão.” 💫'}[kind]
            f = ffont(SERIF_I, int(w * .095)); lines = wrap_words(q, f, w * .8)
            y = (h - len(lines) * f.size * 1.15) / 2 - h * .04
            y = _center_lines(im, lines, f, (255, 255, 255), y, 1.15)
            _center_lines(im, ['— autor desconhecido'], inter(int(w * .045), 'Medium'), (255, 235, 250), y + h * .04)
            return im.convert('RGB')
        if kind == 'dicas':
            im = Image.new('RGBA', (w, h), (250, 204, 21, 255)); d = ImageDraw.Draw(im)
            f = inter(int(w * .13), 'Black'); _center_lines(im, ['10 DICAS', 'PRA VIRALIZAR'], f, (17, 17, 17), h * .2, 1.0)
            _center_lines(im, ['🚀🔥💯'], inter(int(w * .1), 'Bold'), (17, 17, 17), h * .55, esize=int(w * .12))
            d.rounded_rectangle((w * .22, h * .8, w * .78, h * .9), int(h * .05), fill=(17, 17, 17))
            _center_lines(im, ['ARRASTA →'], inter(int(w * .06), 'ExtraBold'), (250, 204, 21), h * .815)
            for i in range(5): d.ellipse((w / 2 - 44 + i * 20, h * .945, w / 2 - 36 + i * 20, h * .945 + 8), fill=(17, 17, 17) if i == 0 else (120, 100, 20))
            return im.convert('RGB')
        if kind == 'clickbait':
            im = _grad_img(w, h, [(185, 28, 28), (17, 17, 17)], diag=False).convert('RGBA')
            f = ffont(ANTON, int(w * .16)); _center_lines(im, ['VOCÊ', 'PRECISA', 'VER ISSO'], f, (255, 255, 255), h * .14, 1.02, stroke=3)
            _center_lines(im, ['😱👇'], f, (255, 255, 255), h * .7, esize=int(w * .2))
            return im.convert('RGB')
        if kind == 'prompt':
            im = Image.new('RGBA', (w, h), (243, 244, 246, 255)); d = ImageDraw.Draw(im)
            _center_lines(im, ['PROMPT DO DIA ✨'], inter(int(w * .085), 'ExtraBold'), (17, 24, 39), h * .1)
            d.rounded_rectangle((w * .08, h * .3, w * .92, h * .82), 18, fill=(255, 255, 255), outline=(209, 213, 219), width=3)
            f = inter(int(w * .058), 'Medium')
            y = h * .35
            for ln in wrap_words('Aja como um especialista em marketing e crie 100 posts virais sobre…', f, w * .74):
                im.alpha_composite(rich(ln, f, (55, 65, 81)), (int(w * .13), int(y))); y += f.size * 1.3
            _center_lines(im, ['salva pra depois 📌'], inter(int(w * .05), 'SemiBold'), (107, 114, 128), h * .87)
            return im.convert('RGB')
        if kind == 'bomdia':
            im = _grad_img(w, h, [(253, 186, 116), (251, 113, 133), (192, 132, 252)], diag=False).convert('RGBA')
            d = ImageDraw.Draw(im); d.ellipse((w * .3, h * .52, w * .7, h * .52 + w * .4), fill=(255, 237, 160))
            _center_lines(im, ['BOM DIA', 'SUCESSO! ☀️'], inter(int(w * .12), 'Black'), (255, 255, 255), h * .14, 1.05, esize=int(w * .12))
            return im.convert('RGB')
        if kind == 'substituir':
            im = _cover(E.asset('ai_brain'), w, h, .5, .2, 1.4)
            im = Image.blend(im, Image.new('RGB', (w, h), (6, 12, 40)), .55).convert('RGBA')
            _center_lines(im, ['A IA VAI', 'SUBSTITUIR', 'VOCÊ? 🤖'], inter(int(w * .12), 'ExtraBold'), (255, 255, 255), h * .26, 1.08, esize=int(w * .12))
            return im.convert('RGB')
        if kind == 'habitos':
            im = Image.new('RGBA', (w, h), (234, 88, 12, 255))
            _center_lines(im, ['7 HÁBITOS', 'DE PESSOAS', 'DE SUCESSO'], inter(int(w * .12), 'Black'), (255, 255, 255), h * .2, 1.05)
            _center_lines(im, ['📈💰🧠'], inter(int(w * .1)), (255, 255, 255), h * .66, esize=int(w * .12))
            return im.convert('RGB')
        if kind == 'emojicap':
            im = Image.new('RGBA', (w, h), (255, 255, 255, 255))
            ph = _cover(E.asset('robot_hand'), w, int(h * .62), .5, .5, 1.1); im.paste(ph, (0, 0))
            f = inter(int(w * .06), 'SemiBold'); y = h * .66
            for ln in wrap_words('🔥🔥 isso mudou TUDO 🤯🙌 #ia #sucesso #mindset #fyp', f, w * .86):
                im.alpha_composite(rich(ln, f, (30, 30, 30), esize=int(f.size * 1.05)), (int(w * .07), int(y))); y += f.size * 1.35
            return im.convert('RGB')
        raise KeyError(kind)
    return E.cached(('A_tile', kind, w, h, var), mk)

KINDS = ['ai_brain', 'quote_b', 'stock_team', 'dicas', 'ai_selfie', 'clickbait', 'robot_hand', 'quote_a', 'ai_planet',
         'prompt', 'bomdia', 'substituir', 'habitos', 'emojicap', 'quote_c']

# ------------------------------------------------------------------------------------------- THE SLOP WALL
COLS, ROWS = 7, 11
GUT = 16
STEP_X, STEP_Y = TILE_W + GUT, TILE_H + GUT
TEX_W, TEX_H = COLS * STEP_X + GUT, ROWS * STEP_Y + GUT
WALL_S0 = .74                                   # texture px -> screen px at rest (tile ≈ 222 px on screen)
WALL_C = (TEX_W / 2, STEP_Y * 2.0 + GUT + TILE_H / 2 + 410)   # texture point at screen centre at rest (scroll 0)

def wall_layout():
    """kind + variant per (col, row): 'all slightly the same' — repeats with small shifts, no identical neighbours."""
    def mk():
        r = rnd(41); lay = {}
        for row in range(ROWS):
            for col in range(COLS):
                for _ in range(20):
                    k = KINDS[int(r.integers(0, len(KINDS)))]
                    if k == 'stock_team' and r.random() < .6: continue
                    if lay.get((col - 1, row), ('',))[0] != k and lay.get((col, row - 1), ('',))[0] != k: break
                lay[(col, row)] = (k, int(r.integers(0, 4)))
        lay[(3, 2)] = ('stock_team', 0)          # the hero tile that flies out on "imagem" (above his head at rest)
        return lay
    return E.cached('A_wall_lay', mk)

def tile_rect(col, row):
    x0 = GUT + col * STEP_X; y0 = GUT + row * STEP_Y
    return x0, y0, x0 + TILE_W, y0 + TILE_H

def wall_texture():
    """the full mosaic (RGB), cold flat light + soft DOF baked (cached on disk)."""
    def mk():
        tex = Image.new('RGB', (TEX_W, TEX_H), (196, 206, 222))
        lay = wall_layout()
        for (c, r), (k, v) in lay.items():
            tile = tile_design(k, var=v)
            if v == 3: tile = grade(tile, sat=.9, tint=(.97, 1.0, 1.05))
            x0, y0, _, _ = tile_rect(c, r)
            tex.paste(tile, (x0, y0))
        # flat, cold, slightly washed "screen wall" look + soft focus (he is in focus, the wall ~1.5 m behind)
        tex = grade(tex, sat=.86, tint=(.95, .99, 1.06), lift=(12, 16, 24), contrast=.9)
        tex = tex.filter(ImageFilter.GaussianBlur(2.0))
        return tex
    return disk_cached('wall_tex', mk, ver=3)

def wall_backdrop():
    """a heavily defocused, dimmer quarter-res copy (for full-frame inserts in front of the wall)."""
    def mk():
        t = wall_texture(); s = t.resize((t.width // 4, t.height // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
        return grade(s, sat=.8, bright=.62, tint=(.95, 1., 1.08))
    return E.cached('A_wall_bd', mk)

def wall_map(cam, scroll=0.0):
    """affine (screen -> texture) for the wall seen through `cam` (already the wall's parallax camera).
    screen = C + (rest - F) * Z + S ;  rest = C + (tex - (WALL_C + (0, scroll))) * WALL_S0"""
    Zt = cam.Z * WALL_S0
    ox = 540 + (540 - cam.fx) * cam.Z + cam.sx - WALL_C[0] * Zt          # screen x of texture x=0
    oy = 960 + (960 - cam.fy) * cam.Z + cam.sy - (WALL_C[1] + scroll) * Zt
    return Zt, ox, oy

def wall_view(cam, scroll=0.0, backdrop=False, size=(W, H)):
    """render the slop wall through the wall camera (RGB, frame size)."""
    Zt, ox, oy = wall_map(cam, scroll)
    if backdrop:
        src = wall_backdrop(); q = 4
        a = 1 / (Zt * q)
        return src.transform(size, Image.AFFINE, (a, 0, -ox * a, 0, a, -oy * a), Image.BILINEAR)
    a = 1 / Zt
    return wall_texture().transform(size, Image.AFFINE, (a, 0, -ox * a, 0, a, -oy * a), Image.BILINEAR)

def tile_screen(cam, col, row, scroll=0.0):
    """screen rect (x0, y0, x1, y1) of wall tile (col, row)."""
    Zt, ox, oy = wall_map(cam, scroll); x0, y0, x1, y1 = tile_rect(col, row)
    return ox + x0 * Zt, oy + y0 * Zt, ox + x1 * Zt, oy + y1 * Zt

def visible_tiles(cam, scroll=0.0, margin=0):
    out = []
    for (c, r), kv in wall_layout().items():
        x0, y0, x1, y1 = tile_screen(cam, c, r, scroll)
        if x1 > -margin and x0 < W + margin and y1 > -margin and y0 < H + margin: out.append(((c, r), kv, (x0, y0, x1, y1)))
    return out

def rrect_sprite(w, h, r, col, a=1.0, blur=0.0):
    """rounded rectangle sprite (RGBA)."""
    def mk():
        pad = int(blur * 2.5) + 2
        m = Image.new('L', (w + 2 * pad, h + 2 * pad)); ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), r, fill=int(255 * a))
        if blur > .3: m = m.filter(ImageFilter.GaussianBlur(blur))
        im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m); return im
    return E.cached(('A_rr', w, h, r, col, round(a, 3), blur), mk)

def card3d(img, cx, cy, s=1.0, rx=0.0, ry=0.0, rz=0.0, f=2200.):
    """img (RGBA) as a card rotated in 3-D (degrees), centred at (cx, cy), scaled s -> (RGBA, x0, y0) top-left."""
    w, h = img.size
    if abs(rx) < .05 and abs(ry) < .05:
        im = rotated(scaled(img, s), rz); return im, cx - im.width / 2, cy - im.height / 2
    pts = GK.project(w, h, 0, 0, s, rx, ry, rz, f=f)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ox, oy = int(math.floor(min(xs))) - 2, int(math.floor(min(ys))) - 2
    ow, oh = int(math.ceil(max(xs))) - ox + 3, int(math.ceil(max(ys))) - oy + 3
    co = GK.homography([(0, 0), (w, 0), (w, h), (0, h)], [(x - ox, y - oy) for x, y in pts])
    im = img.transform((ow, oh), Image.PERSPECTIVE, co, Image.BICUBIC)
    return im, cx + ox, cy + oy

def vblur(img, L):
    """vertical box blur of length L px (scroll motion blur), RGB."""
    L = int(round(L))
    if L < 2: return img
    a = np.asarray(img, np.float32); c = np.cumsum(np.pad(a, ((L, 0), (0, 0), (0, 0)), mode='edge'), 0)
    out = (c[L:] - c[:-L]) / L
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def compose_wraps(*fns):
    fns = [f for f in fns if f is not None]
    if not fns: return None
    def w(fr):
        for f in fns: fr = f(fr)
        return fr
    return w

def zblur(fr, k, n=4, anchor=(W / 2, H / 2)):
    """radial zoom blur of the world (applied in ctx.wrap -> captions/screen layers stay crisp)."""
    rgb = fr.convert('RGB'); acc = np.asarray(rgb, np.float32).copy()
    for i in range(1, n):
        acc += np.asarray(E.zoom(rgb, 1 + k * .05 * i, anchor), np.float32)
    return Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8))

def vwhip(fr, L, dy):
    """vertical whip: shift by dy (edge-clamped, no black bands) + continuous box smear of L px."""
    a = np.asarray(fr.convert('RGB'))
    dy = int(round(dy))
    if dy > 0: a = np.concatenate([np.repeat(a[:1], dy, 0), a[:-dy]], 0)
    elif dy < 0: a = np.concatenate([a[-dy:], np.repeat(a[-1:], -dy, 0)], 0)
    return vblur(Image.fromarray(a), L)

def zblur_range(fr, R, n=12, anchor=(W / 2, H / 2)):
    """smooth radial zoom smear: n copies scaled 1 .. 1+R about anchor (for transition frames)."""
    rgb = fr.convert('RGB'); acc = np.zeros((H, W, 3), np.float32)
    for i in range(n):
        acc += np.asarray(E.zoom(rgb, 1 + R * i / (n - 1), anchor), np.float32)
    return Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8))
