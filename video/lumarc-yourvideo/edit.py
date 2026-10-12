"""LUMARC Reel — "Your product isn't boring... your video is." (1080x1920, 30 fps, ~28 s)

    python3 edit.py cues            # -> cues.json (read by sound.py)
    python3 sound.py                # -> music.wav
    python3 edit.py render [t0 t1]  # -> out/video.mp4 (silent)
    python3 edit.py stills t1 t2 …  # -> out/still_<t>.jpg
    python3 edit.py mux             # -> out/lumarc-your-video.mp4 (voice + music, < 30 MB)

Shares the caption/zoom/reader toolkit with ../lumarc-talkinghead/edit.py. Timeline == plate time; phrase
timings were measured from the voice (speech islands), words inside a phrase are spread by syllables.
"""
import os, sys, json, math, subprocess, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location('th', os.path.join(V, 'lumarc-talkinghead/edit.py'))
th = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(th)
from_th = ['W', 'H', 'FPS', 'Reader', 'zoom', 'font', 'gradient', 'word_img', 'clamp', 'eout', 'ein', 'back', 'VIGNETTE',
           'GRAD', 'WHITE', 'MUTED', 'BG', 'syl']
globals().update({k: getattr(th, k) for k in from_th})

PLATE = os.path.join(HERE, 'plate.mp4')
HY = os.path.join(V, 'silence-hyper/master.mp4')
SM = os.path.join(V, 'silence-motion/silence-motion.mp4')
LE = os.path.join(V, 'lumarc-motion-en/lumarc-3d-en.mp4')
END = 25.25; DUR = END + 3.0
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- script (measured speech islands)
PHRASES = [
    (0.37, 2.07, "Your product | isn't *boring..."),
    (2.66, 3.63, "your *video is."),
    (4.40, 5.20, "*Same product."),
    (5.60, 6.29, "*Same budget."),
    (6.91, 8.74, "Two completely | *different results."),
    (9.58, 11.91, "This one gets | scrolled past | in *one *second..."),
    (12.74, 13.97, "This one gets *watched,"),
    (14.34, 14.82, "*saved..."),
    (15.53, 16.15, "and *sold."),
    (16.97, 18.54, "The difference | isn't the product."),
    (18.99, 20.08, "It's *how you *show it."),
    (20.99, 22.04, "Want to see yours | like this?"),
    (22.61, 23.65, "Comment *“VIDEO”..."),
    (24.14, 25.07, "and I'll send you | an example."),
]
BIG_WORDS = {'boring...', 'video'}

def build_pages():
    pages = []
    for a, z, text in PHRASES:
        groups = [g.split() for g in text.split('|')]
        flat = [w for g in groups for w in g]; wt = [syl(w.strip('*')) + .35 for w in flat]
        tot = sum(wt); t = a; k = 0
        for g in groups:
            ws = []
            for w in g:
                d = (z - a) * wt[k] / tot; k += 1
                ws.append(dict(text=w.strip('*').upper(), emph=w.startswith('*'), t0=t, t1=t + d, big=w.strip('*').lower() in BIG_WORDS))
                t += d
            pages.append(dict(words=ws))
    for i, p in enumerate(pages):
        nxt = pages[i + 1]['words'][0]['t0'] if i + 1 < len(pages) else DUR
        last = p['words'][-1]['t1']
        p['a'] = p['words'][0]['t0'] - .04; p['z'] = nxt - .02 if nxt - last < .45 else last + .4
    return pages
PAGES = build_pages()

# ---------------------------------------------------------------- edit decisions
SPLIT = (4.40, 8.80)            # same product, same budget: cheap (top) vs LUMARC (bottom)
FEED = (8.80, 12.55)            # "scrolled past in one second" — flung away at FLING
FLING = 11.45
WOW = (12.55, 16.75)            # "watched, saved… and sold" — premium film + engagement UI
MONTAGE = (18.95, 20.15)        # "how you show it" — 4 hard cuts
COMMENT = (22.58, END)          # Instagram comment "VIDEO"
BROLL = [                       # (t0, t1, file, src_t0, opts)
    (0.00, 2.62, SM, 11.40, dict(z=(1.18, 1.0), anchor=(540, 900))),          # hook: teardown, exploded driver
    (WOW[0], WOW[1], HY, 22.30, dict(z=(1.0, 1.08))),                            # gold particle headphones → macro
    (18.95, 19.25, HY, 6.45, dict()), (19.25, 19.55, HY, 10.10, dict()),         # THIS · grid
    (19.55, 19.85, SM, 13.00, dict()), (19.85, MONTAGE[1], HY, 19.00, dict()),   # teardown · 40h
    (END, DUR, HY, 28.30, dict(endcard=1)),                                       # LUMARC card (logo), CTA overlaid
]
FACE = [  # (t0, t1, s0, s1, ease)
    (2.62, 4.40, 1.30, 1.18, 'out'), (16.75, 17.75, 1.00, 1.04, 'lin'), (17.75, 18.95, 1.22, 1.27, 'lin'),
    (20.15, 22.58, 1.00, 1.06, 'lin'), (22.58, END, 1.14, 1.24, 'lin'),
]
FACE_ANCHOR = (540, 520)
PUNCH = [3.05, 17.55, 23.10]
FLASH = [(0.0, .8), (2.62, .5), (12.55, .7), (18.95, .5), (19.25, .35), (19.55, .35), (19.85, .35), (END, .6)]
NOPIP = [(0, 2.62), MONTAGE, (END, DUR)]

def cues():
    c = dict(dur=DUR, end=END, split=SPLIT, feed=FEED, fling=FLING, wow=WOW, montage=MONTAGE,
             cuts=[0.0, 2.62, 4.40, 5.60, 8.80, 12.55, 16.75, 18.95, 19.25, 19.55, 19.85, 20.15, END],
             pops=[12.80, 14.36, 22.62], sold=15.55, ticks=[9.6, 10.1, 10.6, 11.1],
             emph=[w['t0'] for p in PAGES for w in p['words'] if w['emph']])
    json.dump(c, open(os.path.join(HERE, 'cues.json'), 'w'), indent=1)

# ---------------------------------------------------------------- captions
def layout(page, base):
    items = []
    for w in page['words']:
        sz = int(base * (1.5 if w['big'] else 1.18 if w['emph'] else 1.0))
        l, t, r, b = font(sz).getbbox(w['text'])
        if r - l > 900: sz = int(sz * 900 / (r - l)); l, t, r, b = font(sz).getbbox(w['text'])
        items.append([w, sz, r - l])
    lines, cur, cw = [], [], 0
    for it in items:
        add = it[2] + (base * .26 if cur else 0)
        if cur and cw + add > 900: lines.append((cur, cw)); cur, cw = [], 0; add = it[2]
        cur.append(it); cw += add
    lines.append((cur, cw))
    out = []; lh = base * 1.12; y0 = -(len(lines) - 1) * lh / 2
    for li, (ln, lw) in enumerate(lines):
        x = -lw / 2
        for it in ln:
            out.append((it[0], it[1], x + it[2] / 2, y0 + li * lh)); x += it[2] + base * .26
    return out

def cap_y(t):
    if SPLIT[0] <= t < SPLIT[1]: return 960          # on the seam between before / after
    if 0 <= t < 2.62: return 1180
    return 1250

def fade(img, k):
    img = img.copy(); img.putalpha(img.getchannel('A').point(lambda v: int(v * k))); return img

def draw_captions(fr, t):
    for p in PAGES:
        if not (p['a'] <= t < p['z']): continue
        cy0 = cap_y(t)
        for w, sz, cx, cy in layout(p, 94):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02
            s = .72 + .28 * back(lt / .16)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.06
            img, _ = word_img(w['text'], sz, 'grad' if (w['emph'] or w['big']) else 'white')
            if lt < .05: img = fade(img, lt / .05)
            if p['z'] - t < .06: img = fade(img, (p['z'] - t) / .06)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            fr.alpha_composite(img, (int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2)))

# ---------------------------------------------------------------- UI overlays
def pill(text, size=40, wght=700, fill=None, fg=WHITE, padx=34, pady=18, grad=False):
    f = font(size, wght); l, tp, r, b = f.getbbox(text); w, h = r - l + 2 * padx, b - tp + 2 * pady
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); m = Image.new('L', im.size)
    ImageDraw.Draw(m).rounded_rectangle((20, 20, 20 + w, 20 + h), h // 2, fill=255)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * .6)))
    im.alpha_composite(sh, (0, 6))
    body = gradient(im.width, im.height, GRAD).convert('RGBA') if grad else Image.new('RGBA', im.size, fill or (20, 20, 28, 235))
    body.putalpha(m.point(lambda v: int(v * (body.getpixel((im.width // 2, im.height // 2))[3] / 255)))); im.alpha_composite(body)
    ImageDraw.Draw(im).text((20 + padx - l, 20 + pady - tp), text, font=f, fill=fg)
    return im

def put(fr, im, cx, cy, s=1.0, alpha=1.0, rot=0.0):
    if s <= .01 or alpha <= .01: return
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    if abs(s - 1) > .01: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if alpha < 1: im = fade(im, alpha)
    fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def popin(lt, d=.22, k=2.4): return 0 if lt < 0 else (.5 + .5 * back(lt / d, k))

_cache = {}
def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

def draw_split_labels(fr, t):
    a, z = SPLIT
    if not (a <= t < z): return
    put(fr, cached('lb', lambda: pill('BEFORE', 34, 700, (235, 235, 240, 235), (30, 30, 40))), 170, 90, popin(t - a))
    if t >= 5.6: put(fr, cached('la', lambda: pill('LUMARC', 34, 700, grad=True)), 170, 1050, popin(t - 5.6))
    # glowing seam
    if t >= 5.6:
        k = eout((t - 5.6) / .3); y = 960
        ImageDraw.Draw(fr).rectangle((0, y - 2, int(W * k), y + 2), fill=(170, 140, 255, 255))

def draw_feed_ui(fr, t):
    a, z = FEED
    if not (a + .5 <= t < FLING + .35): return
    secs = min(1.0, max(0.0, (t - 9.6) / (FLING - 9.6)))
    im = pill(f'{secs:.1f}s', 46, 700, (230, 40, 60, 235))
    put(fr, im, W / 2, 230, popin(t - a - .5), 1 - clamp((t - FLING - .15) / .2))

def draw_wow_ui(fr, t):
    a, z = WOW
    if not (a <= t < z): return
    out = 1 - clamp((t - (z - .15)) / .15)
    # views counter (watched)
    if t >= 12.80:
        v = 1.2e6 * eout((t - 12.80) / 1.4)
        s = f'{v / 1e6:.1f}M views' if v >= 1e5 else f'{int(v / 1e3)}K views'
        im = pill('     ' + s, 44, 700, (16, 16, 24, 220)); y = im.height // 2
        ImageDraw.Draw(im).polygon([(58, y - 18), (58, y + 18), (88, y)], fill=WHITE)
        put(fr, im, W / 2, 230, popin(t - 12.80), out)
    # saved
    if t >= 14.36:
        put(fr, cached('sv', lambda: bookmark_pill()), 300, 380, popin(t - 14.36), out)
    # sold
    if t >= 15.55:
        lt = t - 15.55; s = 1.0 + .9 * (1 - eout(lt / .16)) if lt < .16 else 1.0
        put(fr, cached('sold', lambda: stamp('SOLD')), 760, 420, s, min(1, lt / .06) * out, rot=-9)

def bookmark_pill():
    im = pill('      Saved', 44, 700, (16, 16, 24, 220))
    d = ImageDraw.Draw(im); x, y, w, h = 58, im.height // 2 - 22, 28, 40
    d.polygon([(x, y), (x + w, y), (x + w, y + h), (x + w / 2, y + h - 12), (x, y + h)], fill=WHITE)
    return im

def stamp(text):
    f = font(120, 900); l, tp, r, b = f.getbbox(text); w, h = r - l + 70, b - tp + 50
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); m = Image.new('L', im.size)
    ImageDraw.Draw(m).rounded_rectangle((20, 20, 20 + w, 20 + h), 26, fill=255)
    g = gradient(im.width, im.height, GRAD).convert('RGBA'); g.putalpha(m)
    glow = Image.new('RGBA', im.size, (120, 90, 255, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(18)))
    im.alpha_composite(glow); im.alpha_composite(g)
    ImageDraw.Draw(im).text((20 + 35 - l, 20 + 25 - tp), text, font=f, fill=WHITE)
    return im

def draw_comment(fr, t):
    a, z = COMMENT
    if not (a <= t < z): return
    lt = t - a; bw, bh = 760, 150
    card = Image.new('RGBA', (bw + 60, bh + 60), (0, 0, 0, 0)); m = Image.new('L', card.size)
    ImageDraw.Draw(m).rounded_rectangle((30, 30, 30 + bw, 30 + bh), 38, fill=255)
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .7)))
    card.alpha_composite(sh, (0, 8))
    body = Image.new('RGBA', card.size, (24, 24, 32, 240)); body.putalpha(m.point(lambda v: int(v * .94))); card.alpha_composite(body)
    d = ImageDraw.Draw(card)
    av = gradient(84, 84, GRAD).convert('RGBA'); am = Image.new('L', (84, 84)); ImageDraw.Draw(am).ellipse((0, 0, 83, 83), fill=255)
    av.putalpha(am); card.alpha_composite(av, (62, 30 + (bh - 84) // 2))
    d.text((170, 52), 'yourbrand', font=font(34, 700), fill=(235, 235, 242))
    d.text((170 + font(34, 700).getlength('yourbrand') + 16, 56), 'now', font=font(28, 400), fill=MUTED)
    n = int(clamp((lt - .1) / .07, 0, 5)); txt = 'VIDEO'[:n]
    d.text((170, 96), txt, font=font(52, 800), fill=WHITE)
    if n < 5 and int(lt * 6) % 2 == 0:
        x = 172 + font(52, 800).getlength(txt); d.rectangle((x, 102, x + 4, 150), fill=WHITE)
    # heart (turns on when the word is complete)
    hx, hy, on = 30 + bw - 70, 30 + bh // 2, n >= 5 and lt > .55
    col = (255, 60, 100) if on else (180, 180, 195)
    hs = 1 + .5 * math.exp(-(lt - .55) / .1) if on else 1
    r = 13 * hs
    d.ellipse((hx - 2 * r, hy - r * 1.2, hx, hy + r * .5), fill=col if on else None, outline=col, width=3)
    d.ellipse((hx, hy - r * 1.2, hx + 2 * r, hy + r * .5), fill=col if on else None, outline=col, width=3)
    d.polygon([(hx - 2 * r + 1, hy - r * .1), (hx + 2 * r - 1, hy - r * .1), (hx, hy + r * 1.9)], fill=col if on else None, outline=col)
    put(fr, card, W / 2, 1520, popin(lt, .25), 1 - clamp((t - (z - .1)) / .1))

def draw_endcard(fr, t):
    if t < END: return
    lt = t - END
    if lt >= 1.0:
        put(fr, cached('cta', lambda: pill('Comment “VIDEO”', 56, 800, grad=True, padx=56, pady=26)), W / 2, 1250, popin(lt - 1.0, .3))
    if lt >= 1.3:
        a = clamp((lt - 1.3) / .3)
        put(fr, cached('tag', lambda: text_im('Be seen. Be remembered.', 40, 500, (225, 225, 235))), W / 2, 1395, 1, a)
        put(fr, cached('hdl', lambda: text_im('@lumarc_studio  ·  slumarc.com', 32, 500, MUTED)), W / 2, 1455, 1, a)

def text_im(s, size, wght, col):
    f = font(size, wght); l, tp, r, b = f.getbbox(s)
    im = Image.new('RGBA', (r - l + 20, b - tp + 20), (0, 0, 0, 0)); ImageDraw.Draw(im).text((10 - l, 10 - tp), s, font=f, fill=col)
    return im

# ---------------------------------------------------------------- frame
def face_scale(t):
    s = 1.0
    for a, z, s0, s1, e in FACE:
        if a <= t < z:
            x = (t - a) / (z - a); x = eout(x) if e == 'out' else ein(x) if e == 'in' else x
            s = s0 + (s1 - s0) * x; break
    for p in PUNCH:
        if t >= p: s += .06 * math.exp(-(t - p) / .14) * (1 - math.exp(-(t - p) / .02))
    return s

def band(img, s=1.0, anchor=(540, 960)):
    return zoom(img, s, anchor).crop((0, 480, W, 1440))

class Edit:
    def __init__(self, t0):
        self.t0 = t0; self.plate = th.Reader(PLATE, t0, DUR - t0 + .5); self.rd = {}
    def clip(self, key, path, ss, a, t, dur):
        if key not in self.rd:
            st = ss + max(0., t - a); self.rd[key] = (Reader(path, st, dur - max(0., t - a)), max(a, t))
        r, r0 = self.rd[key]; return r.get(int(round((t - r0) * FPS)))
    def gc(self, t):
        for k in list(self.rd):
            if t >= k[1]: self.rd[k][0].close(); del self.rd[k]
    def frame(self, t):
        self.gc(t)
        plate = self.plate.get(int(round((t - self.t0) * FPS)))
        cur = next((b for b in BROLL if b[0] <= t < b[1]), None)
        since = None
        if cur:
            a, z, path, ss, o = cur
            img = self.clip(('b', z, a), path, ss, a, t, z - a)
            if o.get('endcard') and t - a > 1.6:             # hold the logo frame, slow push
                img = self.hold(path, ss + 1.6)
            z0, z1 = o.get('z', (1, 1)); x = (t - a) / (z - a)
            s = z0 + (z1 - z0) * eout(x) + .10 * (1 - eout((t - a) / .14))
            if o.get('endcard'): s = 1 + .03 * x
            img = zoom(img, s, o.get('anchor', (W / 2, H / 2))); since = t - a
        elif SPLIT[0] <= t < SPLIT[1]:
            img = self.split(t); since = min(t - SPLIT[0], abs(t - 5.6) if t >= 5.6 else 9)
        elif FEED[0] <= t < FEED[1]:
            img = self.feed(t); since = t - FEED[0]
        else:
            img = zoom(plate, face_scale(t), FACE_ANCHOR)
            img = Image.fromarray(np.clip(np.asarray(img).astype(np.float32) * VIGNETTE, 0, 255).astype(np.uint8))
            starts = [f[0] for f in FACE if f[0] <= t]; since = t - max(starts) if starts else 9
        arr = None
        if since is not None and since < 3 / FPS and t > .05:
            arr = np.asarray(img).copy(); k = int(14 * (1 - since * FPS / 3)) + 2
            arr[..., 0] = np.roll(arr[..., 0], k, 1); arr[..., 2] = np.roll(arr[..., 2], -k, 1)
        for at, amt in FLASH:
            if at <= t < at + .3:
                arr = (np.asarray(img) if arr is None else arr).astype(np.float32)
                arr = arr + (255 - arr) * amt * math.exp(-(t - at) / .07)
        if arr is not None: img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        fr = img.convert('RGBA')
        if not any(a <= t < z for a, z in NOPIP) and (cur or SPLIT[0] <= t < SPLIT[1] or FEED[0] <= t < FEED[1]):
            self.pip(fr, plate, t)
        draw_split_labels(fr, t); draw_feed_ui(fr, t); draw_wow_ui(fr, t)
        draw_captions(fr, t); draw_comment(fr, t); draw_endcard(fr, t)
        return fr.convert('RGB')
    _held = {}
    def hold(self, path, at):
        k = (path, at)
        if k not in Edit._held:
            b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{at:.3f}', '-i', path, '-frames:v', '1', '-vf', f'scale={W}:{H}',
                                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            Edit._held[k] = Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1).copy()
        return Edit._held[k]
    def split(self, t):
        a, z = SPLIT; c = Image.new('RGB', (W, H), BG)
        top = band(self.clip(('top', z, a), HY, .55, a, t, z - a), 1.30 + .04 * (t - a) / (z - a), (540, 840))
        y = int(-960 * (1 - eout((t - a) / .3)))
        c.paste(top, (0, y))
        if t >= 5.6:
            bot = band(self.clip(('bot', z, 5.6), SM, 3.2, 5.6, t, z - 5.6), 1.0 + .05 * (t - 5.6) / (z - 5.6), (540, 900))
            c.paste(bot, (0, 960 + int(960 * (1 - eout((t - 5.6) / .3)))))
        return c
    def feed(self, t):
        return th.Edit.feed.__get__(self)(t + (12.38 - FLING))      # reuse the talking-head feed, fling re-timed
    def pip(self, fr, plate, t):
        D, R, cx, cy = 300, 430, 540, 610
        face = plate.crop((cx - R, cy - R, cx + R, cy + R)).resize((D, D), Image.BILINEAR)
        ring = 8; tot = D + 2 * ring + 60; o = 30
        b = cached('pipframe', lambda: self._pipframe(D, ring, tot, o)).copy()
        fm = cached('pipmask', lambda: self._pipmask(D))
        fc = face.convert('RGBA'); fc.putalpha(fm); b.alpha_composite(fc, (o + ring, o + ring))
        starts = [s for s in [SPLIT[0], FEED[0], WOW[0]] if s <= t]; lt = t - max(starts) if starts else 1
        s = back(lt / .25, 1.8) if lt < .25 else 1.0
        py = 1380 if not (SPLIT[0] <= t < SPLIT[1]) else 1500
        put(fr, b, 70 + tot / 2 - o, py + tot / 2 - o, s)
    @staticmethod
    def _pipframe(D, ring, tot, o):
        b = Image.new('RGBA', (tot, tot), (0, 0, 0, 0))
        sh = Image.new('L', (tot, tot)); ImageDraw.Draw(sh).ellipse((o, o + 8, o + D + 2 * ring, o + D + 2 * ring + 8), fill=200)
        shi = Image.new('RGBA', (tot, tot), (0, 0, 0, 0)); shi.putalpha(sh.filter(ImageFilter.GaussianBlur(14))); b.alpha_composite(shi)
        rm = Image.new('L', (tot, tot)); ImageDraw.Draw(rm).ellipse((o, o, o + D + 2 * ring, o + D + 2 * ring), fill=255)
        g = gradient(tot, tot, GRAD).convert('RGBA'); g.putalpha(rm); b.alpha_composite(g)
        return b
    @staticmethod
    def _pipmask(D):
        m = Image.new('L', (D, D)); ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255); return m

def render(t0=0., t1=None, path=None):
    t1 = DUR if t1 is None else t1; path = path or os.path.join(OUT, 'video.mp4')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    E = Edit(t0)
    for i in range(int(round((t1 - t0) * FPS))):
        enc.stdin.write(E.frame(t0 + i / FPS).tobytes())
    enc.stdin.close(); enc.wait()

def stills(ts):
    for t in ts:
        a = max(0, t - .4); E = Edit(a)
        for i in range(int(round((t - a) * FPS)) + 1): f = E.frame(a + i / FPS)
        f.save(os.path.join(OUT, f'still_{t:05.2f}.jpg'), quality=88)

def mux():
    vid = os.path.join(OUT, 'video.mp4'); fin = os.path.join(OUT, 'lumarc-your-video.mp4')
    af = ('[0:a]aresample=48000,highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'apad=whole_dur=%.2f,asplit=2[v][key];[1:a]volume=0.5[m];[m][key]sidechaincompress=threshold=0.05:ratio=4:attack=25:release=320[md];'
          '[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]' % DUR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', PLATE, '-i', os.path.join(HERE, 'music.wav'), '-filter_complex', af, '-map', '[a]',
                    '-c:a', 'pcm_s16le', '-ar', '48000', os.path.join(OUT, 'mix.wav')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', os.path.join(OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-maxrate', '7M', '-bufsize', '14M', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}', fin], check=True)
    print(fin, os.path.getsize(fin) / 1e6, 'MB')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'render'
    if cmd == 'cues': cues()
    elif cmd == 'render': render(*[float(x) for x in sys.argv[2:4]])
    elif cmd == 'stills': stills([float(x) for x in sys.argv[2:]])
    elif cmd == 'mux': mux()
