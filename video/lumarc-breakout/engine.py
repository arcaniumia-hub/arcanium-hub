"""LUMARC "Break out of the feed" Reel — compositor engine (1080x1920, 30 fps). Forked from lumarc-showcase/engine.py.

World = studio plate (or a section's own background) -> `behind` layers -> keyed avatar (+ copies) -> `front` layers
-> virtual camera (zoom / pan / roll) -> `screen` layers -> captions -> post FX (flash, RGB split, glitch, zoom blur,
vignette, grain).  One section module (sections/sNN_*.py) is active at a time and fills a fresh Ctx every frame.

Section contract (see sections/README.md):
    START, END = engine.span(i0, i1)       # timeline seconds, from TL segment indices
    def draw(ctx, lt, t): ...              # lt = t - START
    CUES = [(t, 'kind', {...}), ...]       # optional sound cues (absolute timeline seconds)
"""
import os, sys, math, json, glob, importlib, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE)
sys.path.insert(0, HERE)
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
import importlib.util
_th = _load('_th', os.path.join(V, 'lumarc-talkinghead/edit.py'))
_yv = _load('_yv', os.path.join(V, 'lumarc-yourvideo/edit.py'))

W, H, FPS = 1080, 1920, 30
font, gradient, word_img, zoom = _th.font, _th.gradient, _th.word_img, _th.zoom
clamp, eout, ein, back, syl = _th.clamp, _th.eout, _th.ein, _th.back, _th.syl
pill, put, popin, fade, text_im = _yv.pill, _yv.put, _yv.popin, _yv.fade, _yv.text_im
GRAD = [(79, 107, 255), (106, 85, 255), (154, 77, 255)]
GRAD_LIGHT = [(140, 162, 255), (164, 142, 255), (208, 146, 255)]
WHITE, MUTED, BG = (250, 249, 246), (166, 166, 184), (14, 14, 20)

from timeline import TL, VOICE_END
END_HOLD = 2.6
DUR = round(VOICE_END + END_HOLD, 2)
def span(i0, i1):
    """timeline seconds covering TL segments i0..i1 inclusive (section boundaries sit on segment starts)."""
    a = 0.0 if i0 == 0 else TL[i0]['t0']
    z = DUR if i1 >= len(TL) - 1 else TL[i1 + 1]['t0']
    return a, z
def seg(i): return TL[i]

SRC = os.path.join(HERE, 'src')
def asset(name):
    return _cache(('asset', name), lambda: Image.open(os.path.join(SRC, 'assets', name + '.png')).convert('RGB'))
_C = {}
def _cache(k, fn):
    if k not in _C: _C[k] = fn()
    return _C[k]
cached = lambda key, fn: _cache(('u', key), fn)
def ease(x, kind='out'):
    return {'out': eout, 'in': ein, 'back': back, 'lin': lambda v: clamp(v)}[kind](x)
def seg_t(i, frac=0.0):
    s = TL[i]; return s['t0'] + (s['t1'] - s['t0']) * frac

# ---------------------------------------------------------------- words (captions + timing for sections)
def _voice_islands():
    """speech islands (start, end) on the edit timeline, from the re-timed plate's audio (10 ms hop)."""
    def mk():
        raw = os.path.join(SRC, 'tight16k.raw')
        if not os.path.exists(raw):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(SRC, 'tight.mov'), '-ac', '1', '-ar', '16000', '-f', 'f32le', raw], check=True)
        x = np.fromfile(raw, np.float32); h = 160
        r = np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')[::h]); sp = 20 * np.log10(r + 1e-6) > -40
        out, i, n = [], 0, len(sp)
        while i < n:
            if sp[i]:
                j = i
                while j < n and (sp[j] or (j + 8 < n and sp[j:j + 8].any())): j += 1
                if j - i >= 4: out.append((i / 100, j / 100))
                i = j
            else: i += 1
        return out
    return _cache('islands', mk)

# onsets measured by hand on the voice (spectrogram + 10 ms envelope) where the automatic alignment is off
WORD_FIX = {(0, "HEY."): 0.09, (1, "YEAH,"): 0.63, (1, "YOU."): 0.98, (2, "DOWN"): 1.48, (2, "HERE."): 1.72, (3, "YOUR"): 2.28, (3, "CONTENT"): 2.52, (3, "LIVES"): 3.06, (3, "IN"): 3.32, (3, "HERE."): 3.54, (4, "TINY."): 4.1, (5, "FLAT."): 4.78, (6, "ONE"): 5.42, (6, "SWIPE..."): 5.63, (7, "AND"): 6.32, (7, "IT'S"): 6.42, (7, "GONE."): 6.65, (9, "NOT"): 7.9, (9, "MINE."): 8.09, (11, "GOOD"): 9.41, (11, "CONTENT"): 9.76, (11, "DOESN'T"): 10.4, (11, "STAY"): 10.76, (11, "ON"): 11.2, (11, "THE"): 11.28, (11, "SCREEN."): 11.38, (12, "IT"): 12.07, (12, "STAYS"): 12.17, (12, "IN"): 12.58, (12, "YOUR"): 12.68, (12, "HEAD."): 12.92, (13, "THE"): 13.39, (13, "PRODUCT"): 13.5, (13, "YOU"): 14.09, (13, "CAN"): 14.22, (13, "ALMOST"): 14.45, (13, "TOUCH."): 14.93, (14, "THE"): 15.51, (14, "VIDEO"): 15.65, (14, "YOU"): 16.34, (14, "WATCH"): 16.48, (14, "TWICE."): 16.87, (15, "THE"): 17.59, (15, "BRAND"): 17.7, (15, "YOU"): 18.29, (15, "STILL"): 18.42, (15, "REMEMBER"): 18.8, (15, "TOMORROW."): 19.34, (16, "THAT'S"): 20.06, (16, "WHAT"): 20.42, (16, "WE"): 20.57, (16, "BUILD"): 20.76, (16, "AT"): 21.11, (16, "LUMARC."): 21.23, (17, "WANT"): 22.15, (17, "YOUR"): 22.37, (17, "BRAND"): 22.69, (17, "TO"): 23, (17, "BREAK"): 23.17, (17, "OUT"): 23.46, (17, "OF"): 23.61, (17, "THE"): 23.67, (17, "FEED?"): 23.74, (18, "COMMENT"): 24.38, (18, "“LUMARC”"): 24.97, (19, "AND"): 25.74, (19, "I'LL"): 25.86, (19, "SHOW"): 25.99, (19, "YOU"): 26.23, (19, "HOW."): 26.36}

def _snap_words(pages):
    """refine word onsets onto the energy dip that precedes each word (syllable estimates run late)."""
    raw = os.path.join(SRC, 'tight16k.raw'); x = np.fromfile(raw, np.float32); h = 160
    r = np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')[::h]); sm = np.convolve(20 * np.log10(r + 1e-6), np.ones(3) / 3, 'same')
    words = [w for p in pages for w in p['words']]; isl = _voice_islands()
    starts = [a for a, b in isl]
    for k, w in enumerate(words):
        if any(abs(w['t0'] - a) < .03 for a in starts): continue          # already on an island start
        i0 = max(0, int((w['t0'] - .20) * 100)); i1 = int((w['t0'] + .12) * 100)
        seg_ = sm[i0:i1]
        if len(seg_) < 3: continue
        j = int(np.argmin(seg_)); local = sm[max(0, i0 - 10):i1 + 10].mean()
        if seg_[j] < local - 8:
            t = (i0 + j) / 100 + .02
            lo = words[k - 1]['t0'] + .08 if k and words[k - 1]['seg'] == w['seg'] else -1
            if t > lo and abs(t - w['t0']) < .2: w['t0'] = t
    for k, w in enumerate(words[:-1]):
        if words[k + 1]['seg'] == w['seg']: w['t1'] = max(w['t0'] + .06, words[k + 1]['t0'])

def _pages():
    """caption pages; word onsets aligned to the voice: syllable-weighted positions are mapped onto the speech
    islands of each segment (pauses skipped), so a word after a pause starts when the voice does."""
    isl = _voice_islands(); pages = []
    for i, s in enumerate(TL):
        if not s['cap']: continue
        own = [(max(a, s['t0']), min(b, s['t1'])) for a, b in isl if b > s['t0'] + .02 and a < s['t1'] - .02]
        if not own: own = [(s['t0'] + .04, s['t1'] - .06)]
        speech = sum(b - a for a, b in own)
        def at(frac):   # position along the concatenated speech -> timeline time
            d = frac * speech
            for a, b in own:
                if d <= b - a + 1e-6: return a + d
                d -= b - a
            return own[-1][1]
        groups = [g.split() for g in s['cap'].split('|')]
        flat = [w for g in groups for w in g]; wt = [syl(w.strip('*“”"')) + .35 for w in flat]; tot = sum(wt); acc = 0.0; k = 0
        for g in groups:
            ws = []
            for w in g:
                t0 = at(acc / tot); acc += wt[k]; t1 = at(acc / tot); k += 1
                ws.append(dict(text=w.strip('*').upper(), emph=w.startswith('*'), t0=t0, t1=t1, seg=i))
            pages.append(dict(words=ws, seg=i))
    _snap_words(pages)
    words = [w for p in pages for w in p['words']]
    for w in words:
        k = (w['seg'], w['text'])
        if k in WORD_FIX: w['t0'] = WORD_FIX[k]
    for k in range(len(words) - 2, -1, -1):          # keep order: pull earlier words back before a corrected one
        a, b = words[k], words[k + 1]
        if a['seg'] == b['seg'] and a['t0'] > b['t0'] - .08: a['t0'] = b['t0'] - .08
    for k, w in enumerate(words[:-1]):
        if words[k + 1]['seg'] == w['seg']: w['t1'] = max(w['t0'] + .06, words[k + 1]['t0'])
    for j, p in enumerate(pages):
        nxt = pages[j + 1]['words'][0]['t0'] if j + 1 < len(pages) else DUR; last = p['words'][-1]['t1']
        p['a'] = p['words'][0]['t0'] - .04; p['z'] = nxt - .02 if nxt - last < .5 else last + .35
    return pages
PAGES = _pages()
WORDS = [w for p in PAGES for w in p['words']]
def word_time(text, seg_index=None, nth=0):
    """start time of a caption word (case-insensitive, punctuation-insensitive)."""
    key = ''.join(c for c in text.upper() if c.isalnum())
    hits = [w for w in WORDS if ''.join(c for c in w['text'] if c.isalnum()) == key and (seg_index is None or w['seg'] == seg_index)]
    return hits[nth]['t0'] if len(hits) > nth else None

# ---------------------------------------------------------------- readers
class Reader:
    def __init__(self, path, ss, dur, vf=None, rgba=False, exact=False):
        """exact=True: native frames, no constant-frame-rate padding (ffmpeg would otherwise duplicate the first frame
        when the seek point falls between frames) -> frame i is exactly source frame (first frame at/after ss) + i."""
        self.pf = 'rgba' if rgba else 'rgb24'; self.bpp = 4 if rgba else 3
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{max(0, ss):.4f}', '-i', path, '-t', f'{dur + .3:.3f}',
                                   '-vf', vf or f'fps={FPS},scale={W}:{H}'] + (['-fps_mode', 'passthrough'] if exact else []) +
                                  ['-f', 'rawvideo', '-pix_fmt', self.pf, '-'],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.n = 0; self.last = None; self.size = None
    def get(self, idx, size=(W, H)):
        while self.n <= idx:
            b = self.p.stdout.read(size[0] * size[1] * self.bpp)
            if len(b) < size[0] * size[1] * self.bpp: break
            self.last = Image.frombuffer('RGBA' if self.bpp == 4 else 'RGB', size, b, 'raw', 'RGBA' if self.bpp == 4 else 'RGB', 0, 1); self.n += 1
        return self.last
    def close(self):
        try: self.p.kill()
        except Exception: pass

class Clip:
    """sequential random-ish access to another video (e.g. the SILENCE teardown film) at timeline speed."""
    def __init__(self, path, size=(W, H)): self.path, self.size, self.r, self.t0 = path, size, None, None
    def at(self, src_t):
        """frame nearest to src_t (sources are 30 fps); a pure function of src_t whatever the reader's start."""
        k = max(0, int(math.floor(src_t * 30 + .5 + 1e-6)))
        if self.r is not None and (k < self.t0 + self.r.n - 1 or k > self.t0 + self.r.n + 45): self.r.close(); self.r = None
        if self.r is None:
            self.t0 = k
            self.r = Reader(self.path, (k - .5) / 30, 30, vf=f'scale={self.size[0]}:{self.size[1]}', exact=True)
        return self.r.get(k - self.t0, self.size)
_clips = {}
def clip(path, size=(W, H)):
    k = (path, size)
    if k not in _clips: _clips[k] = Clip(path, size)
    return _clips[k]
TEARDOWN = os.path.join(V, 'silence-motion/silence-motion.mp4')
HYPER = os.path.join(V, 'silence-hyper/master.mp4')
LOGO = os.path.join(V, 'silence-motion/img/logo.png')
def logo(width=520):
    def mk():
        lg = Image.open(LOGO).convert('RGBA'); return lg.resize((width, int(lg.height * width / lg.width)), Image.LANCZOS)
    return _cache(('logo', width), mk)

# ---------------------------------------------------------------- avatar (green screen)
STUDIO = os.path.join(SRC, 'studio_plate.png')
def studio(): return _cache('studio', lambda: Image.open(STUDIO).convert('RGB'))

def key(img):
    a = np.asarray(img).astype(np.float32); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.maximum(r, b); diff = g - m
    alpha = np.clip(255 - (diff - 30) * 255 / 70, 0, 255)
    g2 = np.where(diff > 0, m + diff * .12, g)
    return np.dstack([r, g2, b]), alpha / 255.0

_gx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]
_rim_y = np.clip((1640 - np.arange(H, dtype=np.float32)) / 260, 0, 1)[:, None, None]
def light_avatar(rgb, al):
    """sit the studio-lit HeyGen take into the dark purple set: exposure, cool fill, purple/blue rim from the monitors."""
    rgb = rgb * .93
    rgb = rgb * np.array([.98, .98, 1.03], np.float32)
    from scipy.ndimage import minimum_filter
    band = np.clip(al - minimum_filter(al, size=9), 0, 1)[..., None]
    rim = np.where(_gx > 0, np.array([120, 130, 255], np.float32), np.array([190, 90, 255], np.float32))
    e = band * (.25 + .30 * np.abs(_gx)) * .55 * _rim_y
    rgb = rgb * (1 - e) + rim * e
    return rgb

# the HeyGen take is a floating bust (body cut at y≈1600 of the source): crop 864x1536 at (108, 40) and scale x1.25 so the
# cut lands below the frame bottom; head top ≈ y 615, eyes ≈ y 760, elbows touch the frame edges.
AV_VF = f'crop=864:1536:108:40,scale={W}:{H}:flags=bicubic'
AV_FPS = 25                       # tight.mov is read at its native rate; frame = nearest source frame of t
class Avatar:
    def __init__(self, t0):
        self.k0 = self._k_of(t0); self.r = Reader(os.path.join(SRC, 'tight.mov'), (self.k0 - .5) / AV_FPS, DUR - t0 + 1, vf=AV_VF, exact=True)
        self._k = None
    @staticmethod
    def _k_of(t):
        j = int(round(min(t, VOICE_END - .04) * FPS))             # timeline frame number (exact integer)
        return (2 * j * AV_FPS + FPS) // (2 * FPS)                 # nearest 25 fps source frame, integer maths (no float ties)
    def frame(self, t):
        """keyed avatar (RGBA PIL, full 1080x1920) at timeline t; holds the last frame after the voice ends.
        Pure function of t: the source frame is the nearest 25 fps frame, whatever t the reader started at."""
        f = self.r.get(self._k_of(t) - self.k0)
        if self._k is not None and self._k[0] is f: return self._k[1]
        rgb, al = key(f); rgb = light_avatar(rgb, al)
        a8 = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.9))
        out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); out.putalpha(a8)
        self._k = (f, out); return out

# ---------------------------------------------------------------- building blocks for sections
def glass_panel(w, h, radius=36, tint=(255, 255, 255), alpha=.10, border=.45, shine=True):
    """frosted-glass card (RGBA). Put it in a layer with glass=<blur px> so the engine blurs what is behind it."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); m = Image.new('L', (w, h))
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    body = Image.new('RGBA', (w, h), tint + (int(255 * alpha),)); body.putalpha(m.point(lambda v: int(v * alpha)))
    im.alpha_composite(body)
    if shine:   # diagonal sheen
        g = np.linspace(1, 0, h, dtype=np.float32)[:, None] ** 2 * .22
        sh = Image.fromarray((np.repeat(g, w, 1) * 255).astype(np.uint8)); sh = Image.composite(sh, Image.new('L', (w, h)), m)
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [sh]))
    b = Image.new('L', (w, h)); ImageDraw.Draw(b).rounded_rectangle((1, 1, w - 2, h - 2), radius, outline=255, width=2)
    im.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [b.point(lambda v: int(v * border))]))
    return im

def rounded(img, radius):
    img = img.convert('RGBA'); m = Image.new('L', img.size); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius, fill=255)
    a = np.minimum(np.asarray(img.getchannel('A')), np.asarray(m)); img.putalpha(Image.fromarray(a)); return img

def shadow(img, blur=30, opacity=.6, offset=(0, 18), col=(0, 0, 0)):
    """img with a soft drop shadow baked in (returns bigger RGBA, same centre)."""
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1]))
    out = Image.new('RGBA', (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new('L', out.size); a.paste(img.getchannel('A'), (pad + offset[0], pad + offset[1]))
    sh = Image.new('RGBA', out.size, col + (0,)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity)))
    out.alpha_composite(sh); out.alpha_composite(img, (pad, pad)); return out

def phone(content, w=520):
    """iPhone-style mockup with `content` (any PIL image, cover-fit 9:19.5 screen)."""
    h = int(w * 2.05); r = int(w * .16); bez = int(w * .035)
    sw, sh_ = w - 2 * bez, h - 2 * bez
    c = content.convert('RGB'); sc = max(sw / c.width, sh_ / c.height); c = c.resize((int(c.width * sc) + 1, int(c.height * sc) + 1), Image.BILINEAR)
    c = c.crop(((c.width - sw) // 2, (c.height - sh_) // 2, (c.width - sw) // 2 + sw, (c.height - sh_) // 2 + sh_))
    body = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=(18, 18, 24, 255), outline=(90, 90, 110, 255), width=3)
    body.alpha_composite(rounded(c, r - bez), (bez, bez))
    d.rounded_rectangle((w // 2 - w * .14, bez + 12, w // 2 + w * .14, bez + 12 + w * .07), w * .035, fill=(0, 0, 0, 255))   # island
    return body

def laptop(content, w=900):
    """laptop mockup (screen 16:10) with `content` cover-fit."""
    sw = int(w * .84); shh = int(sw * .625); bz = int(w * .02)
    c = content.convert('RGB'); sc = max(sw / c.width, shh / c.height); c = c.resize((int(c.width * sc) + 1, int(c.height * sc) + 1), Image.BILINEAR)
    c = c.crop(((c.width - sw) // 2, 0, (c.width - sw) // 2 + sw, shh))
    lid_w, lid_h = sw + 2 * bz, shh + 2 * bz + 10; base_h = int(w * .045)
    im = Image.new('RGBA', (w, lid_h + base_h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0 = (w - lid_w) // 2
    d.rounded_rectangle((x0, 0, x0 + lid_w, lid_h), 22, fill=(20, 20, 26, 255), outline=(100, 100, 120, 255), width=3)
    im.paste(c, (x0 + bz, bz + 6))
    d.rounded_rectangle((0, lid_h - 2, w, lid_h + base_h), 14, fill=(150, 150, 165, 255))
    d.rounded_rectangle((w // 2 - 80, lid_h - 2, w // 2 + 80, lid_h + 10), 6, fill=(110, 110, 125, 255))
    return im

def ig_post(img, user='yourbrand', w=760, sponsored=False):
    """Instagram feed post card (dark mode)."""
    c = img.convert('RGB'); ih = int(c.height * w / c.width); c = c.resize((w, ih), Image.BILINEAR)
    hh = 104; fh = 120
    im = Image.new('RGBA', (w, hh + ih + fh), (16, 16, 20, 255)); d = ImageDraw.Draw(im)
    av = gradient(66, 66, GRAD).convert('RGBA'); m = Image.new('L', (66, 66)); ImageDraw.Draw(m).ellipse((0, 0, 65, 65), fill=255); av.putalpha(m)
    im.alpha_composite(av, (22, 19)); d.text((104, 26), user, font=font(30, 700), fill=(240, 240, 245))
    if sponsored: d.text((104, 62), 'Sponsored', font=font(22, 400), fill=(160, 160, 170))
    d.text((w - 60, 30), '···', font=font(34, 700), fill=(220, 220, 230))
    im.paste(c, (0, hh))
    y = hh + ih + 22
    # heart, comment, share, save glyphs (outline)
    def heart(x, y, s=1, fill=None, col=(235, 235, 240)):
        r = 11 * s; d.ellipse((x - 2 * r, y - r * 1.2, x, y + r * .5), fill=fill, outline=col, width=3)
        d.ellipse((x, y - r * 1.2, x + 2 * r, y + r * .5), fill=fill, outline=col, width=3)
        d.polygon([(x - 2 * r + 1, y - r * .1), (x + 2 * r - 1, y - r * .1), (x, y + r * 1.9)], fill=fill, outline=col)
    heart(48, y + 18)
    d.ellipse((96, y, 136, y + 38), outline=(235, 235, 240), width=3)
    d.polygon([(170, y + 4), (210, y + 19), (170, y + 34), (178, y + 19)], outline=(235, 235, 240))
    d.polygon([(w - 54, y), (w - 24, y), (w - 24, y + 40), (w - 39, y + 28), (w - 54, y + 40)], outline=(235, 235, 240))
    return im

def big_text(text, size=200, style='grad', wght=900):
    """large display word with soft shadow (RGBA)."""
    return word_img(text, size, style)[0]

def kinetic(text, size, style, t, t0, dur=.18):
    """pop-in word image for time t (None before t0)."""
    if t < t0: return None
    im = word_img(text, size, style)[0]; k = back((t - t0) / dur, 2.0); s = .6 + .4 * k
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    return fade(im, clamp((t - t0) / .06))

# ---------------------------------------------------------------- context
class Ctx:
    def __init__(self, t):
        self.t = t
        self.cam = dict(z=1.12, x=540., y=820., dx=0., dy=0., rot=0.)
        self.bg_img = None; self.bg_z = 1.0; self.bg_dim = 0.0; self.bg_blur = 0.0
        self.avatar = dict(show=True, s=1.0, x=0., y=0., alpha=1.0, copies=[], bright=1.0)
        self.behind, self.front, self.screen = [], [], []
        self.full = None
        self.captions = True; self.cap_y = 1420; self.cap_size = 92
        self.wrap = None          # callable(frame_rgba) -> frame_rgba, applied after the camera (frame-in-frame, swipes, slats)
        self.compose = None       # set by the engine: compose(cam=None, avatar=None) -> RGBA world through a camera
        self.post = dict(flash=0., flash_col=(255, 255, 255), glitch=0., rgb=0., zoom_blur=0., vignette=.32, grain=1.0, bright=1.0, sat=1.0)
    def add(self, layer, img, x, y, center=True, glass=0, alpha=1.0):
        """layer: 'behind' | 'front' | 'screen'. (x, y) = centre (default) or top-left. glass = blur radius of what is behind."""
        if img is None or alpha <= .01: return
        if alpha < 1: img = fade(img, alpha)
        if center: x, y = x - img.width / 2, y - img.height / 2
        getattr(self, layer).append(dict(img=img, xy=(int(round(x)), int(round(y))), glass=glass))

def _paste(base, L):
    img, (x, y) = L['img'], L['xy']
    if L['glass']:
        x0, y0, x1, y1 = max(0, x), max(0, y), min(base.width, x + img.width), min(base.height, y + img.height)
        if x1 > x0 and y1 > y0:
            region = base.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(L['glass']))
            m = img.getchannel('A').crop((x0 - x, y0 - y, x1 - x, y1 - y)).point(lambda v: 255 if v > 8 else 0)
            base.paste(region, (x0, y0), m)
    if x >= 0 and y >= 0 and x + img.width <= base.width and y + img.height <= base.height:
        base.alpha_composite(img, (x, y))
    else:
        x0, y0 = max(0, -x), max(0, -y); x1, y1 = min(img.width, base.width - x), min(img.height, base.height - y)
        if x1 > x0 and y1 > y0: base.alpha_composite(img.crop((x0, y0, x1, y1)), (x + x0, y + y0))

# ---------------------------------------------------------------- captions
def _layout(page, base):
    items = []
    for w in page['words']:
        sz = int(base * (1.2 if w['emph'] else 1.0)); l, t, r, b = font(sz).getbbox(w['text'])
        if r - l > 900: sz = int(sz * 900 / (r - l)); l, t, r, b = font(sz).getbbox(w['text'])
        items.append([w, sz, r - l])
    lines, cur, cw = [], [], 0
    for it in items:
        add = it[2] + (base * .34 if cur else 0)
        if cur and cw + add > 900: lines.append((cur, cw)); cur, cw = [], 0; add = it[2]
        cur.append(it); cw += add
    lines.append((cur, cw)); out = []; lh = base * 1.12; y0 = -(len(lines) - 1) * lh / 2
    for li, (ln, lw) in enumerate(lines):
        x = -lw / 2
        for it in ln: out.append((it[0], it[1], x + it[2] / 2, y0 + li * lh)); x += it[2] + base * .34
    return out

def draw_captions(fr, t, cy0, base=92, since=None):
    for p in PAGES:
        if not (p['a'] <= t < p['z']): continue
        if since is not None and TL[p['seg']]['t0'] < since - 1e-6: continue     # page belongs to the previous section
        for w, sz, cx, cy in _layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = fade(img, lt / .05)
            if p['z'] - t < .06: img = fade(img, (p['z'] - t) / .06)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            fr.alpha_composite(img, (int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2)))

# ---------------------------------------------------------------- post FX
_grain = [np.random.default_rng(i).normal(0, 6.5, (H // 2, W // 2, 1)).astype(np.float32) for i in range(6)]
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_R2 = (((_xx - W / 2) / (W * .7)) ** 2 + ((_yy - H * .45) / (H * .7)) ** 2)
del _yy, _xx
def post(img, P, t):
    a = np.asarray(img, np.float32)
    if P['zoom_blur'] > .01:
        acc = a.copy(); n = 4
        for i in range(1, n):
            s = 1 + P['zoom_blur'] * .06 * i
            acc += np.asarray(zoom(img, s), np.float32)
        a = acc / n
    if P['rgb'] > .1:
        k = int(P['rgb']); a = a.copy(); a[..., 0] = np.roll(a[..., 0], k, 1); a[..., 2] = np.roll(a[..., 2], -k, 1)
    if P['glitch'] > .01:
        r = np.random.default_rng(int(t * 1000)); a = a.copy()
        for _ in range(int(4 + 10 * P['glitch'])):
            y = r.integers(0, H - 80); h = r.integers(10, 90); a[y:y + h] = np.roll(a[y:y + h], int(r.integers(-90, 90) * P['glitch']), 1)
    if P['sat'] != 1: g = a.mean(2, keepdims=True); a = g + (a - g) * P['sat']
    if P['bright'] != 1: a = a * P['bright']
    if P['flash'] > .01: a = a + (np.array(P['flash_col'], np.float32) - a) * P['flash']
    a = a * (1 - P['vignette'] * np.clip(_R2 - .2, 0, 1))[..., None]
    if P['grain']: a = a + np.repeat(np.repeat(_grain[int(round(t * FPS)) % 6], 2, 0), 2, 1) * P['grain']
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---------------------------------------------------------------- sections + frame
def load_sections():
    mods = []
    for f in sorted(glob.glob(os.path.join(HERE, 'sections', 's[0-9][0-9]_*.py'))):
        name = os.path.splitext(os.path.basename(f))[0]
        mods.append(importlib.import_module('sections.' + name))
    return mods

class Film:
    def __init__(self, t0=0.0, page=None):
        self.av = Avatar(t0); self.sections = load_sections()
    def section_at(self, t):
        for m in self.sections:
            if m.START <= t < m.END: return m
        return None
    def compose_world(self, ctx, cam=None, avatar=None):
        t = ctx.t; cam = dict(ctx.cam, **(cam or {})); A = dict(ctx.avatar, **(avatar or {}))
        bg = (ctx.bg_img or studio())
        if ctx.bg_z != 1: bg = zoom(bg, ctx.bg_z, (540, 760))
        if ctx.bg_blur > .3: bg = bg.filter(ImageFilter.GaussianBlur(ctx.bg_blur))
        if ctx.bg_dim > .01: bg = Image.blend(bg, Image.new('RGB', bg.size, (0, 0, 0)), ctx.bg_dim)
        world = bg.convert('RGBA')
        for L in ctx.behind: _paste(world, L)
        if A['show'] and A['alpha'] > .01:
            av = self.av.frame(t)
            if A['bright'] != 1:
                av = Image.merge('RGBA', [*Image.eval(av.convert('RGB'), lambda v: int(min(255, v * A['bright']))).split(), av.getchannel('A')])
            def place(img, s, x, y, alpha):
                if abs(s - 1) > .005: img = img.resize((int(W * s), int(H * s)), Image.BILINEAR)
                if alpha < 1: img = fade(img, alpha)
                _paste(world, dict(img=img, xy=(int(540 - img.width / 2 + x), int(H - img.height + y)), glass=0))
            for c in A['copies']:
                place(av, A['s'] * c.get('s', 1), A['x'] + c.get('x', 0), A['y'] + c.get('y', 0), A['alpha'] * c.get('alpha', .8))
            place(av, A['s'], A['x'], A['y'], A['alpha'])
        for L in ctx.front: _paste(world, L)
        z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
        X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
        return zoom(world.convert('RGB'), z, (cam['x'], cam['y']), dx=X - cam['x'], dy=Y - cam['y'], rot=cam['rot']).convert('RGBA')
    def frame(self, t):
        ctx = Ctx(t); ctx.compose = lambda cam=None, avatar=None: self.compose_world(ctx, cam, avatar)
        m = self.section_at(t)
        if m is not None: m.draw(ctx, t - m.START, t)
        if ctx.full is not None: fr = ctx.full.convert('RGBA')
        else: fr = self.compose_world(ctx)
        if ctx.wrap is not None: fr = ctx.wrap(fr).convert('RGBA')
        for L in ctx.screen: _paste(fr, L)
        if ctx.captions: draw_captions(fr, t, ctx.cap_y, ctx.cap_size, since=m.START if m is not None else None)
        return post(fr.convert('RGB'), ctx.post, t)

# ---------------------------------------------------------------- CLI
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
def render(t0, t1, path):
    F = Film(t0)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    j0 = int(round(t0 * FPS))                       # integer frame grid: t = j / FPS exactly (section + avatar agree)
    for i in range(int(round((t1 - t0) * FPS))):
        enc.stdin.write(F.frame((j0 + i) / FPS).tobytes())
    enc.stdin.close(); enc.wait()

def stills(ts, outdir):
    os.makedirs(outdir, exist_ok=True); paths = []
    for t in ts:
        t = round(t * FPS) / FPS; F = Film(t); p = os.path.join(outdir, f'still_{t:06.2f}.jpg'); F.frame(t).save(p, quality=88); paths.append(p)
    return paths

def sheet(t0, t1, step, path, cols=6, w=270):
    """contact sheet with time labels. Sections are pure functions of t, so frames can be sampled sparsely."""
    F = Film(t0); ims = []; n = int(round((t1 - t0) / step))
    for i in range(n):
        t = round(t0 + i * step, 4); im = F.frame(t).resize((w, int(w * H / W)), Image.BILINEAR)
        ImageDraw.Draw(im).text((6, 6), f'{t:.2f}s', font=font(22, 700), fill=(255, 230, 0)); ims.append(im)
    rows = math.ceil(len(ims) / cols); S = Image.new('RGB', (cols * w, rows * ims[0].height))
    for i, im in enumerate(ims): S.paste(im, ((i % cols) * w, (i // cols) * im.height))
    S.save(path, quality=85); return path

def collect_cues():
    cues = []
    for m in load_sections(): cues += [(float(c[0]), c[1], c[2] if len(c) > 2 else {}) for c in getattr(m, 'CUES', [])]
    return sorted(cues)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'render': render(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else os.path.join(OUT, 'video.mp4'))
    elif cmd == 'stills': print('\n'.join(stills([float(x) for x in sys.argv[3:]], sys.argv[2])))
    elif cmd == 'sheet': print(sheet(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], int(sys.argv[6]) if len(sys.argv) > 6 else 6))
    elif cmd == 'prender':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 4; F_ = int(round(DUR * FPS)); cuts = [round(F_ * i / n) for i in range(n + 1)]
        ps = [subprocess.Popen([sys.executable, __file__, 'render', str(cuts[i] / FPS), str(cuts[i + 1] / FPS), os.path.join(OUT, f'part{i}.mp4')]) for i in range(n)]
        for p in ps: p.wait()
        open(os.path.join(OUT, 'parts.txt'), 'w').write(''.join(f"file 'part{i}.mp4'\n" for i in range(n)))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(OUT, 'parts.txt'), '-c', 'copy', os.path.join(OUT, 'video.mp4')], check=True)
    elif cmd == 'cues': print(json.dumps(collect_cues(), indent=1))
    elif cmd == 'info':
        for i, s in enumerate(TL): print(i, s['t0'], s['t1'], s['cap'])
        print('DUR', DUR)
