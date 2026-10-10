"""LUMARC talking-head Reel — frame-accurate edit (numpy + PIL -> ffmpeg).

    python3 edit.py cues            # writes cues.json (sound design reads it)
    python3 sound.py                # -> music.wav
    python3 edit.py render [t0 t1]  # -> out/video.mp4 (silent) ; t0/t1 = optional preview range
    python3 edit.py stills t1 t2 …  # -> out/still_<t>.jpg
    python3 edit.py mux             # -> out/lumarc-talkinghead.mp4 (voice + music, ≤30 MB)

Timeline == plate time (the speech is never retimed). Phrase timings were measured from the voice energy
(speech islands), words inside a phrase are spread by syllable count.
"""
import os, sys, json, math, re, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 30
PLATE = os.path.join(HERE, 'plate.mp4')
HY = os.path.join(V, 'silence-hyper/master.mp4')          # BEFORE (cheap) 0-4.8 s / AFTER 6.4 s+ / LUMARC card 28 s+
SM = os.path.join(V, 'silence-motion/silence-motion.mp4')
LE = os.path.join(V, 'lumarc-motion-en/lumarc-3d-en.mp4')  # tacky flyer 0-3.5 s, service cards 12-18 s, post wall 8 s
DROP, END = 22.55, 48.90
DUR = END + (34.4 - 28.3)                                   # end card runs to the end of the hyper master
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- brand
BG = (14, 14, 20); WHITE = (250, 249, 246); MUTED = (166, 166, 184)
GRAD = [(79, 107, 255), (106, 85, 255), (154, 77, 255)]
GRAD_LIGHT = [(140, 162, 255), (164, 142, 255), (208, 146, 255)]   # caption tint (readable on dark)

# ---------------------------------------------------------------- script (measured speech islands)
# '|' = caption page break, '*' = emphasis word, phrases flagged 'hide' get no caption, 'end' = end-card caption
PHRASES = [
    (0.38, 1.70, "Your product | might be *amazing..."),
    (2.00, 3.26, "but if it shows up | like *this,"),
    (3.50, 4.51, "nobody stops | to look."),
    (5.18, 8.00, "Most brands post | a product photo | on a *white background,"),
    (8.19, 9.36, "write *“SALE” | in *red,"),
    (9.51, 10.39, "and hope | for the best."),
    (11.56, 13.96, "And the post | *disappears | from the feed | in *two *seconds."),
    (14.55, 15.47, "Now think | about this:"),
    (15.99, 16.42, "what *if,"),
    (16.72, 18.65, "instead of presenting | your product"),
    (19.23, 20.14, "like this..."),
    (21.55, 22.99, "you presented it | like *THIS?"),
    (23.63, 24.68, "That's what we do | at *LUMARC."),
    (25.20, 25.86, "*Videos,"),
    (26.20, 26.74, "*editing,"),
    (26.96, 27.62, "*Reels,"),
    (27.88, 28.74, "*carousels,"),
    (28.88, 29.56, "*designs,"),
    (29.80, 30.50, "*captions..."),
    (31.08, 34.11, "Everything built | to make people | *stop *scrolling | and look | at your *brand."),
    (34.67, 35.37, "Because today,"),
    (35.75, 36.91, "being good | isn't *enough."),
    (37.60, 38.49, "You have to | *look *good."),
    (39.03, 39.98, "You have to | be *seen."),
    (41.04, 41.74, "And above all,"),
    (42.03, 42.56, "*remembered."),
    (43.15, 44.64, "Want to see | what your product | could look like?"),
    (45.70, 47.52, "Send me the word | *VIDEO | in a DM,"),
    (47.86, 48.50, "and I'll show you."),
    (48.97, 49.45, "LUMARC.", 'hide'),
    (49.83, 50.41, "Be *seen.", 'end'),
    (50.77, 51.38, "Be *remembered.", 'end'),
]
BIG_WORDS = {'videos,', 'editing,', 'reels,', 'carousels,', 'designs,', 'captions...', 'remembered.'}

def syl(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    if not w: return 1
    if w in ('dm',): return 2
    n = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and not w.endswith(('le', 'ee')) and n > 1: n -= 1
    return max(1, n)

def build_words():
    pages = []
    for ph in PHRASES:
        a, z, text = ph[:3]; flag = ph[3] if len(ph) > 3 else ''
        groups = [g.split() for g in text.split('|')]
        flat = [w for g in groups for w in g]; wt = [syl(w.strip('*')) + .35 for w in flat]
        tot = sum(wt); t = a; k = 0
        for g in groups:
            ws = []
            for w in g:
                d = (z - a) * wt[k] / tot; k += 1
                ws.append(dict(text=w.strip('*').upper(), emph=w.startswith('*'), t0=t, t1=t + d,
                               big=w.strip('*').lower() in BIG_WORDS))
                t += d
            pages.append(dict(words=ws, flag=flag, phrase_end=z))
    for i, p in enumerate(pages):
        nxt = pages[i + 1]['words'][0]['t0'] if i + 1 < len(pages) else DUR
        last = p['words'][-1]['t1']
        p['a'] = p['words'][0]['t0'] - .04
        p['z'] = nxt - .02 if nxt - last < .45 else last + .4
    return pages
PAGES = build_words()

# ---------------------------------------------------------------- edit decisions
# B-roll: (t0, t1, file, src_t0, opts)  — everything else is the face plate
BI = os.path.join(V, 'birra-reel/out/birra-reel.mp4')        # 2D animated explainer (another LUMARC job)
BROLL = [
    (2.70, 4.95, LE, 0.10, dict(paint=(220, 420), z=(1.10, 1.16), anchor=(540, 940))),   # tacky flyer — "like this"
    (4.95, 6.30, LE, 2.20, dict(paint=(220, 420), z=(1.25, 1.30), anchor=(540, 900))),
    (6.30, 8.15, HY, 0.50, dict(z=(1.42, 1.48), anchor=(540, 1240))),                   # white-background photo
    (8.15, 9.45, HY, 2.15, dict(z=(1.40, 1.46), anchor=(540, 1240))),                   # 50% OFF / "SALE"
    (9.45, 10.45, HY, 3.55, dict(z=(1.40, 1.45), anchor=(540, 1300))),                  # BUY NOW — hope for the best
    (10.45, 14.55, 'feed', 0, dict()),                                                   # feed scroll — "disappears"
    (16.00, 19.15, HY, 0.05, dict(z=(1.0, 1.04))),                                       # "What if instead of presenting…"
    (19.15, 20.20, HY, 3.30, dict(z=(1.0, 1.06), sat=.6)),                               # "like this…"
    (DROP, 23.05, HY, 6.40, dict(nopip=1)),                                              # THIS — slam
    (23.05, 23.62, HY, 7.70, dict(z=(1.0, 1.06), nopip=1)),                              # ring
    (23.62, 25.20, LE, 6.20, dict(z=(1.0, 1.05), pip='top')),                                       # LUMARC logo reveal
    (25.20, 25.98, SM, 9.55, dict(z=(1.0, 1.05))),                                       # Videos
    (25.98, 26.90, LE, 17.00, dict()),                                                   # editing
    (26.90, 27.82, LE, 15.90, dict()),                                                   # Reels
    (27.82, 28.82, LE, 13.90, dict()),                                                   # carousels
    (28.82, 29.74, LE, 12.90, dict()),                                                   # designs
    (29.74, 31.08, LE, 10.05, dict()),                                                   # captions — "impossible to scroll past"
    (31.08, 32.55, HY, 7.90, dict(z=(1.0, 1.05))),                                       # Introducing SILENCE ONE
    (32.55, 33.25, LE, 8.10, dict(z=(1.0, 1.08))),                                       # stop scrolling — post wall
    (33.25, 34.67, SM, 4.00, dict(z=(1.0, 1.04))),                                       # look at your brand — hero
    (34.67, 35.75, HY, 12.10, dict()),                                                   # Because today — NOISE
    (35.75, 37.60, HY, 18.70, dict()),                                                   # being good isn't enough — 40h/250g
    (37.60, 38.75, SM, 3.00, dict(z=(1.0, 1.06))),                                       # look good
    (38.75, 41.04, BI, 15.00, dict(z=(1.0, 1.05))),                                      # be seen — 2D animation job
    (44.10, 45.70, HY, 22.40, dict(z=(1.0, 1.05))),                                      # could look like
    (END, DUR, HY, 28.30, dict(nopip=1)),                                                # LUMARC end card
]
NO_CAPTION = [(DROP, 25.18)]                               # THIS slam + LUMARC logo reveal speak for themselves
# face framing: (t0, t1, scale0, scale1, ease) — a scale jump between segments reads as a jump cut
FACE = [
    (0.00, 0.45, 1.42, 1.12, 'out'), (0.45, 2.00, 1.12, 1.18, 'lin'), (2.00, 2.70, 1.00, 1.03, 'lin'),
    (4.95, 6.30, 1.22, 1.26, 'lin'), (10.45, 12.45, 1.04, 1.10, 'lin'), (12.45, 14.55, 1.24, 1.30, 'lin'),
    (14.55, 15.99, 1.00, 1.05, 'lin'), (15.99, 16.72, 1.24, 1.26, 'lin'), (16.72, 19.15, 1.04, 1.12, 'lin'),
    (20.20, DROP, 1.00, 1.34, 'in'), (23.62, 25.20, 1.16, 1.21, 'lin'), (29.74, 31.08, 1.26, 1.30, 'lin'),
    (31.08, 32.55, 1.00, 1.06, 'lin'), (33.25, 34.67, 1.20, 1.24, 'lin'), (34.67, 35.75, 1.00, 1.04, 'lin'),
    (35.75, 37.60, 1.15, 1.20, 'lin'), (37.60, 38.00, 1.00, 1.02, 'lin'), (38.75, 39.03, 1.08, 1.09, 'lin'),
    (39.03, 41.04, 1.28, 1.34, 'lin'), (41.04, 42.03, 1.00, 1.04, 'lin'), (42.03, 43.15, 1.32, 1.38, 'lin'),
    (43.15, 44.10, 1.00, 1.04, 'lin'), (44.75, 45.70, 1.12, 1.15, 'lin'), (45.70, END, 1.00, 1.14, 'lin'),
]
FACE_ANCHOR = (540, 520)
PUNCH = [1.20, 9.00, 24.30, 36.45, 42.03, 46.36]           # extra kick-zoom on emphasis words
SWIPE = (12.38, 12.62)                                      # "disappears" — the feed swipes the post away
FLASH = [(DROP, .9), (END, .7), (42.03, .35)]
DM = (46.36, END)                                           # DM bubble "VIDEO"

def cues():
    cuts = sorted({b[0] for b in BROLL} | {b[1] for b in BROLL if b[1] < DUR - .1})
    hits = [DROP, END]
    c = dict(dur=DUR, drop=DROP, endcard=END, breakdown=[34.55, 42.03],
             whoosh=[t for t in cuts if all(abs(t - h) > .05 for h in hits)],
             hits=[25.20, 42.03], ticks=[w['t0'] for p in PAGES for w in p['words'] if w['emph'] and p['flag'] != 'hide'],
             pops=[DM[0]], swipe=[SWIPE[0] - .2])
    json.dump(c, open(os.path.join(HERE, 'cues.json'), 'w'), indent=1)

# ---------------------------------------------------------------- helpers
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def ein(x): x = clamp(x); return x ** 2.2
def back(x, s=2.2): x = clamp(x) - 1; return 1 + x * x * ((s + 1) * x + s)

class Reader:
    def __init__(self, path, ss, dur, fps_in=None):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-i', path, '-t', f'{dur + .3:.3f}',
                                   '-vf', f'fps={FPS},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.n = 0; self.last = None
    def get(self, idx):
        while self.n <= idx:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            self.last = Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1); self.n += 1
        return self.last
    def close(self):
        try: self.p.kill()
        except Exception: pass

def zoom(img, s, anchor=(W / 2, H / 2), dx=0., dy=0., rot=0.):
    """scale `img` by s around `anchor` (anchor stays put), then translate by dx,dy (px)."""
    if abs(s - 1) < 1e-4 and not dx and not dy and not rot: return img
    ax, ay = anchor; c, si = math.cos(rot), math.sin(rot)
    # output (x,y) -> input: ((x-ax-dx)R^-1)/s + a
    a = c / s; b = si / s; d = -si / s; e = c / s
    cx = ax + dx; cy = ay + dy
    return img.transform((W, H), Image.AFFINE, (a, b, ax - a * cx - b * cy, d, e, ay - d * cx - e * cy), Image.BILINEAR)

_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = (1 - .38 * np.clip((((_xx - W / 2) / (W * .62)) ** 2 + ((_yy - H * .42) / (H * .62)) ** 2) - .25, 0, 1) ** 1.2)[..., None]
del _yy, _xx

# ---------------------------------------------------------------- type
_fonts = {}
def font(size, wght=800):
    k = (size, wght)
    if k not in _fonts:
        f = ImageFont.truetype(os.path.join(HERE, 'fonts/Outfit.ttf'), size)
        f.set_variation_by_axes([wght]); _fonts[k] = f
    return _fonts[k]

def gradient(w, h, cols):
    x = np.linspace(0, 1, w)[None, :, None]; c = np.array(cols, np.float32)
    g = np.where(x < .5, c[0] + (c[1] - c[0]) * (x / .5), c[1] + (c[2] - c[1]) * ((x - .5) / .5))
    return Image.fromarray(np.repeat(g, h, 0).astype(np.uint8), 'RGB')

_words = {}
def word_img(text, size, style):
    """RGBA word with dark stroke + soft shadow. style: 'white' | 'grad' | 'dim'."""
    k = (text, size, style)
    if k in _words: return _words[k]
    f = font(size); pad = int(size * .45); sw = max(3, size // 22)
    l, t, r, b = f.getbbox(text, stroke_width=sw)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    fill = Image.new('L', (w, h)); ImageDraw.Draw(fill).text((pad - l, pad - t), text, font=f, fill=255)
    strk = Image.new('L', (w, h)); ImageDraw.Draw(strk).text((pad - l, pad - t), text, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    shadow = strk.filter(ImageFilter.GaussianBlur(size * .16))
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('RGBA', (w, h), (6, 6, 12, 0)); sh.putalpha(shadow.point(lambda v: int(v * .85)))
    out.alpha_composite(sh, (0, int(size * .05)))
    st = Image.new('RGBA', (w, h), (10, 10, 16, 0)); st.putalpha(strk.point(lambda v: int(v * .9))); out.alpha_composite(st)
    if style == 'grad':
        g = gradient(w, h, GRAD_LIGHT).convert('RGBA'); g.putalpha(fill)
        glow = Image.new('RGBA', (w, h), (120, 90, 255, 0)); glow.putalpha(fill.filter(ImageFilter.GaussianBlur(size * .22)).point(lambda v: int(v * .55)))
        out.alpha_composite(glow); out.alpha_composite(g)
    else:
        col = WHITE if style == 'white' else (210, 210, 222)
        c = Image.new('RGBA', (w, h), col + (0,)); c.putalpha(fill); out.alpha_composite(c)
    # anchor = centre of the text body (without pad)
    _words[k] = (out, pad)
    return _words[k]

def layout(page, base):
    """returns [(word, size, cx, cy)] centred on (0,0); wraps to max width."""
    items = []
    for w in page['words']:
        sz = int(base * (1.55 if w['big'] and page['flag'] != 'end' else 1.18 if w['emph'] else 1.0))
        f = font(sz); l, t, r, b = f.getbbox(w['text'])
        if r - l > 880: sz = int(sz * 880 / (r - l)); l, t, r, b = font(sz).getbbox(w['text'])
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

def draw_captions(fr, t):
    if any(a <= t < z for a, z in NO_CAPTION): return
    for p in PAGES:
        if not (p['a'] <= t < p['z']) or p['flag'] == 'hide': continue
        cy0 = 1545 if p['flag'] == 'end' else 1250
        base = 94
        for w, sz, cx, cy in layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02
            s = .72 + .28 * back(lt / .16)
            active = w['t0'] - .02 <= t < w['t1'] + .04
            style = 'grad' if (w['emph'] or w['big']) else 'white'
            if active: s *= 1.06
            img, pad = word_img(w['text'], sz, style)
            if lt < .05: img = img.copy(); img.putalpha(img.getchannel('A').point(lambda v, k=lt / .05: int(v * k)))
            # out fade on the last 60 ms of the page
            if p['z'] - t < .06:
                img = img.copy(); k = (p['z'] - t) / .06; img.putalpha(img.getchannel('A').point(lambda v, k=k: int(v * k)))
            if abs(s - 1) > .01:
                img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            fr.alpha_composite(img, (int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2)))

def draw_dm(fr, t):
    a, z = DM
    if not (a <= t < z): return
    lt = t - a; s = .6 + .4 * back(lt / .22, 2.6)
    bw, bh = 470, 150
    card = Image.new('RGBA', (bw + 80, bh + 150), (0, 0, 0, 0))
    m = Image.new('L', card.size); ImageDraw.Draw(m).rounded_rectangle((40, 90, 40 + bw, 90 + bh), 75, fill=255)
    sh = Image.new('RGBA', card.size, (90, 60, 255, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * .7)))
    card.alpha_composite(sh)
    g = gradient(card.width, card.height, GRAD).convert('RGBA'); g.putalpha(m); card.alpha_composite(g)
    d = ImageDraw.Draw(card)
    d.text((card.width / 2, 58), 'DM  @lumarc_studio', font=font(34, 500), fill=WHITE + (235,), anchor='mm')
    n = clamp(int((lt - .12) / .06) + 1, 0, 5); txt = 'VIDEO'[:int(n)]
    if txt: d.text((card.width / 2, 90 + bh / 2), txt, font=font(76, 800), fill=WHITE, anchor='mm')
    if int(n) < 5 and int(lt * 6) % 2 == 0:
        tw = font(76, 800).getlength(txt) if txt else 0
        d.rectangle((card.width / 2 + tw / 2 + 6, 90 + bh / 2 - 32, card.width / 2 + tw / 2 + 11, 90 + bh / 2 + 32), fill=WHITE)
    # fade out at the cut to the end card
    if z - t < .1: card.putalpha(card.getchannel('A').point(lambda v, k=(z - t) / .1: int(v * k)))
    card = card.resize((int(card.width * s), int(card.height * s)), Image.BILINEAR)
    fr.alpha_composite(card, (int(W / 2 - card.width / 2), int(1500 - card.height / 2)))

# ---------------------------------------------------------------- frame
def face_scale(t):
    for a, z, s0, s1, e in FACE:
        if a <= t < z:
            x = (t - a) / (z - a); x = eout(x) if e == 'out' else ein(x) if e == 'in' else x
            s = s0 + (s1 - s0) * x; break
    else: s = 1.0
    for p in PUNCH:
        if t >= p: s += .055 * math.exp(-(t - p) / .14) * (1 - math.exp(-(t - p) / .02))
    return s

class Edit:
    def __init__(self, t0):
        self.plate = Reader(PLATE, t0, DUR - t0 + .5); self.pidx = -1; self.t0 = t0
        self.br = {}
    def face(self, t):
        i = int(round((t - self.t0) * FPS)); return self.plate.get(i)
    def broll(self, k, t):
        a, z, path, ss, o = BROLL[k]
        if k not in self.br:
            st = ss + max(0., t - a); self.br[k] = (Reader(path, st, z - max(a, t)), max(a, t))
        r, rt0 = self.br[k]
        return r.get(int(round((t - rt0) * FPS)))
    def frame(self, t):
        cur = next((k for k, b in enumerate(BROLL) if b[0] <= t < b[1]), None)
        for k in list(self.br):
            if k != cur and t >= BROLL[k][1]: self.br[k][0].close(); del self.br[k]
        plate = self.face(t)
        if cur is not None:
            a, z, path, ss, o = BROLL[cur]
            img = self.feed(t) if path == 'feed' else self.broll(cur, t)
            if 'paint' in o:   # hide the old "What if instead…" banner on the flyer clip
                img = img.copy(); y0, y1 = o['paint']; c = img.getpixel((30, y0 - 10))
                ImageDraw.Draw(img).rectangle((0, y0, W, y1), fill=c)
            z0, z1 = o.get('z', (1, 1)); x = (t - a) / (z - a)
            s = z0 + (z1 - z0) * x + .10 * (1 - eout((t - a) / .14))       # incoming punch
            img = zoom(img, s, o.get('anchor', (W / 2, H / 2)), dy=o.get('dy', 0))
            if 'sat' in o:
                arr = np.asarray(img).astype(np.float32); g = arr.mean(2, keepdims=True)
                img = Image.fromarray(np.clip(g + (arr - g) * o['sat'], 0, 255).astype(np.uint8))
            since = t - a
        else:
            s = face_scale(t)
            seg = next(((a, z) for a, z, *_ in FACE if a <= t < z), (0, 0))
            prev_cut = max([b[1] for b in BROLL if b[1] <= t] + [seg[0]])
            since = t - prev_cut
            if SWIPE[0] <= t < SWIPE[1]:
                img = self.swipe(plate, t)
            else:
                img = zoom(plate, s, FACE_ANCHOR)
            arr = np.asarray(img).astype(np.float32) * VIGNETTE
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        # cut-in chromatic split (first 3 frames after any cut)
        arr = None
        if since < 3 / FPS and t > .2:
            arr = np.asarray(img).copy(); k = int(14 * (1 - since * FPS / 3)) + 2
            arr[..., 0] = np.roll(arr[..., 0], k, 1); arr[..., 2] = np.roll(arr[..., 2], -k, 1)
        for at, amt in FLASH:
            if at <= t < at + .3:
                arr = np.asarray(img).astype(np.float32) if arr is None else arr.astype(np.float32)
                k = amt * math.exp(-(t - at) / .07); arr = arr + (255 - arr) * k
        if arr is not None: img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        fr = img.convert('RGBA')
        if cur is not None and not BROLL[cur][4].get('nopip'): self.pip(fr, plate, t, cur)
        draw_captions(fr, t); draw_dm(fr, t)
        return fr.convert('RGB')
    def pip(self, fr, plate, t, cur):
        """speaker bubble while the work is on screen; pops in at the start of each B-roll run."""
        k = cur
        while k > 0 and abs(BROLL[k - 1][1] - BROLL[k][0]) < 1e-6 and not BROLL[k - 1][4].get('nopip'): k -= 1
        lt = t - BROLL[k][0]; s = back(lt / .25, 1.8) if lt < .25 else 1.0
        D = 300; R = 430                                  # bubble diameter / plate crop radius around the face
        cx, cy = 540, 610
        face = plate.crop((cx - R, cy - R, cx + R, cy + R)).resize((D, D), Image.BILINEAR)
        ring = 8; tot = D + 2 * ring + 60
        b = Image.new('RGBA', (tot, tot), (0, 0, 0, 0)); o = 30
        sh = Image.new('L', (tot, tot)); ImageDraw.Draw(sh).ellipse((o, o + 8, o + D + 2 * ring, o + D + 2 * ring + 8), fill=200)
        shi = Image.new('RGBA', (tot, tot), (0, 0, 0, 0)); shi.putalpha(sh.filter(ImageFilter.GaussianBlur(14))); b.alpha_composite(shi)
        rm = Image.new('L', (tot, tot)); ImageDraw.Draw(rm).ellipse((o, o, o + D + 2 * ring, o + D + 2 * ring), fill=255)
        g = gradient(tot, tot, GRAD).convert('RGBA'); g.putalpha(rm); b.alpha_composite(g)
        fm = Image.new('L', (D, D)); ImageDraw.Draw(fm).ellipse((0, 0, D - 1, D - 1), fill=255)
        fc = face.convert('RGBA'); fc.putalpha(fm); b.alpha_composite(fc, (o + ring, o + ring))
        if BROLL[cur][1] - t < .08 and (cur + 1 >= len(BROLL) or abs(BROLL[cur + 1][0] - BROLL[cur][1]) > 1e-6 or BROLL[cur + 1][4].get('nopip')):
            s *= max(0, (BROLL[cur][1] - t) / .08)
        if s <= .01: return
        b = b.resize((max(1, int(tot * s)), max(1, int(tot * s))), Image.BILINEAR)
        py = 150 if BROLL[cur][4].get('pip') == 'top' else 1330
        fr.alpha_composite(b, (int(70 + tot / 2 - b.width / 2 - o), int(py + tot / 2 - b.height / 2 - o)))
    _cards = None
    def feed(self, t):
        """dark-mode feed of generic posts; flung away on "disappears"."""
        if Edit._cards is None:
            def grab(path, at, box):
                b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(at), '-i', path, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
                im = Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1).copy()
                if path == LE: ImageDraw.Draw(im).rectangle((0, 220, W, 420), fill=im.getpixel((30, 210)))
                return im.crop(box)
            srcs = [grab(LE, 1.0, (40, 470, 1040, 1400)), grab(HY, 1.8, (0, 330, 1080, 1500)), grab(HY, 4.0, (0, 260, 1080, 1460)),
                    grab(LE, 2.6, (40, 470, 1040, 1400)), grab(HY, 2.6, (0, 330, 1080, 1500))]
            cards = []
            for i, im in enumerate(srcs):
                cw = 900; im = im.resize((cw, int(im.height * cw / im.width)), Image.BILINEAR)
                c = Image.new('RGB', (cw, im.height + 110), (22, 22, 30)); d = ImageDraw.Draw(c)
                d.ellipse((24, 24, 86, 86), fill=(70, 70, 86)); d.text((104, 30), ['yourbrand', 'bestdeals.store', 'shop_now'][i % 3], font=font(32, 600), fill=(235, 235, 240))
                d.text((104, 66), 'Sponsored', font=font(24, 400), fill=(150, 150, 165)); d.text((cw - 60, 40), '···', font=font(36, 700), fill=(200, 200, 210))
                c.paste(im, (0, 110)); cards.append(c)
            Edit._cards = cards
        def at(tt):
            y = 160 * (tt - 10.45)
            if tt > 12.38: y += 3600 * eout((tt - 12.38) / .4)
            return y
        acc = np.zeros((H, W, 3), np.float32); n = 6 if 12.3 < t < 12.85 else 1
        for j in range(n):
            y = at(t + j / n / FPS); c = Image.new('RGB', (W, H), BG); yy = 200 - y; i = 0
            while yy < H:
                cd = Edit._cards[i % len(Edit._cards)]
                if yy + cd.height > 0: c.paste(cd, (90, int(yy)))
                yy += cd.height + 40; i += 1
            acc += np.asarray(c, np.float32)
        return Image.fromarray((acc / n).astype(np.uint8))
    def swipe(self, plate, t):
        a, z = SWIPE; acc = np.zeros((H, W, 3), np.float32); n = 4
        old = zoom(plate, face_scale(a - .001), FACE_ANCHOR); new = zoom(plate, face_scale(z), FACE_ANCHOR)
        for j in range(n):
            tt = t + (j / n) / FPS; p = eout((tt - a) / (z - a)) if tt < z else 1
            off = int(p * H); c = Image.new('RGB', (W, H), BG)
            c.paste(old, (0, -off)); c.paste(new, (0, H - off + 24))
            acc += np.asarray(c, np.float32)
        return Image.fromarray((acc / n).astype(np.uint8))

def render(t0=0., t1=None, path=None):
    t1 = DUR if t1 is None else t1; path = path or os.path.join(OUT, 'video.mp4')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    E = Edit(t0); n = int(round((t1 - t0) * FPS))
    for i in range(n):
        t = t0 + i / FPS
        enc.stdin.write(E.frame(t).tobytes())
        if i % 150 == 0: print(f'{t:6.2f}s', flush=True)
    enc.stdin.close(); enc.wait()

def stills(ts):
    for t in ts:
        E = Edit(max(0, t - .5))
        for i in range(int(round((t - max(0, t - .5)) * FPS)) + 1): f = E.frame(max(0, t - .5) + i / FPS)
        f.save(os.path.join(OUT, f'still_{t:05.2f}.jpg'), quality=88)

def mux():
    vid = os.path.join(OUT, 'video.mp4'); mus = os.path.join(HERE, 'music.wav'); fin = os.path.join(OUT, 'lumarc-talkinghead.mp4')
    af = ('[0:a]aresample=48000,highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'apad=whole_dur=%.2f,asplit=2[v][key];' % DUR +
          '[1:a]volume=0.5[m];[m][key]sidechaincompress=threshold=0.05:ratio=4:attack=25:release=320[md];'
          '[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', PLATE, '-i', mus, '-filter_complex', af, '-map', '[a]',
                    '-c:a', 'pcm_s16le', '-ar', '48000', os.path.join(OUT, 'mix.wav')], check=True)
    # 2-pass to land just under 30 MB
    kb = int((27.5 * 8 * 1000) / DUR) - 192
    for ps in (1, 2):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', os.path.join(OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
               '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{kb}k', '-pass', str(ps), '-passlogfile', os.path.join(OUT, 'x264'),
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}']
        subprocess.run(cmd + (['-f', 'mp4', '/dev/null'] if ps == 1 else [fin]), check=True)
    print(fin, os.path.getsize(fin) / 1e6, 'MB')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'render'
    if cmd == 'cues': cues()
    elif cmd == 'render': render(*[float(x) for x in sys.argv[2:4]])
    elif cmd == 'stills': stills([float(x) for x in sys.argv[2:]])
    elif cmd == 'mux': mux()
