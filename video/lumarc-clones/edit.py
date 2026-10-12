"""LUMARC Reel — "We're not real" (3 HeyGen clones on green, composited; 1080x1920, 30 fps, ~34 s).

    python3 edit.py tracks          # -> work/track_{a,b,c}.mp4 (each clone re-timed onto the edit timeline) + work/voice.wav
    python3 edit.py cues            # -> cues.json (sound.py)
    python3 sound.py                # -> music.wav
    python3 edit.py render [t0 t1]  # -> out/video.mp4 (silent)
    python3 edit.py stills t …      # -> out/still_<t>.jpg
    python3 edit.py mux             # -> out/lumarc-clones.mp4

Sources (src/, gitignored): b = clone 1 (blazer), c = clone 2 (hoodie), a = clone 3 (white tee). Every line is cut
from its clone's take at the measured speech island and laid on the timeline; between lines each clone plays its
own silent "[PAUSE]" footage (ping-pong) so the listeners stay alive. Timeline values are snapped to the 25 fps
source grid so the re-timed tracks stay lip-synced.
"""
import os, sys, json, math, subprocess, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE)
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
th = _load('th', os.path.join(V, 'lumarc-talkinghead/edit.py'))
yv = _load('yv', os.path.join(V, 'lumarc-yourvideo/edit.py'))
for k in ['W', 'H', 'FPS', 'Reader', 'zoom', 'font', 'gradient', 'word_img', 'clamp', 'eout', 'ein', 'back', 'GRAD', 'WHITE', 'MUTED', 'BG', 'syl']:
    globals()[k] = getattr(th, k)
for k in ['pill', 'put', 'popin', 'fade', 'cached', 'text_im']:
    globals()[k] = getattr(yv, k)

SRC = {k: os.path.join(HERE, f'src/{k}.mp4') for k in 'abc'}
WORK = os.path.join(HERE, 'work'); OUT = os.path.join(HERE, 'out')
os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
HY = os.path.join(V, 'silence-hyper/master.mp4')
LOGO = os.path.join(V, 'silence-motion/img/logo.png')
G = 0.04                                                    # 25 fps source grid
def snap(x): return round(round(x / G) * G, 2)
NAME = {'b': 'CLONE #1', 'c': 'CLONE #2', 'a': 'CLONE #3'}

# ---------------------------------------------------------------- script: (clone, src_in, src_out, caption, gap before)
LINES = [
    ('b', 0.24, 3.60, "Hi. | I'm not *real. | I'm a *digital *clone.", 0.20),
    ('c', 3.24, 4.08, "*Me *too.", 0.28),
    ('a', 2.92, 4.48, "Yeah... | *same.", 0.28),
    ('b', 6.32, 8.88, "The real one | *hates being | on camera...", 0.36),
    ('c', 6.76, 8.00, "So he | *made *us.", 0.24),
    ('a', 7.16, 10.40, "Now he posts | *every *single *day... | without | recording *anything.", 0.24),
    ('b', 11.64, 13.92, "*Monday, | I launched a product | in *Paris.", 0.40),
    ('c', 10.76, 13.04, "*Tuesday, | I presented | to *investors.", 0.28),
    ('a', 13.04, 16.36, "*Wednesday... | I explained *taxes. | Nobody watched. | *Fair.", 0.28),
    ('b', 16.68, 17.60, "Want a *clone | of *you?", 0.40),
    ('c', 15.80, 17.24, "*LUMARC | builds yours.", 0.20),
    ('a', 18.84, 20.12, "Comment | *“CLONE”.", 0.20),
    ('b', 20.32, 21.24, "And the | *real one?", 0.40),
    ('c', 20.04, 20.88, "On *vacation.", 0.80),
]
def timeline():
    t = 0.0; out = []
    for k, s0, s1, cap, gap in LINES:
        t0 = snap(t + gap); d = snap(s1 - s0); out.append(dict(k=k, s0=s0, s1=s0 + d, t0=t0, t1=t0 + d, cap=cap)); t = t0 + d
    return out
TL = timeline()
L = {i: ln for i, ln in enumerate(TL)}
END = snap(TL[-1]['t1'] + .36); DUR = END + 3.0
IDLE = {'b': [(3.80, 6.16), (9.04, 11.44), (14.08, 16.48), (17.80, 20.08), (21.44, 24.28)],
        'c': [(0.20, 3.04), (4.24, 6.56), (8.20, 10.56), (13.24, 15.60), (17.44, 19.84), (21.04, 23.88)],
        'a': [(0.20, 2.76), (4.64, 7.00), (10.60, 12.84), (16.56, 18.64), (20.28, 22.80)]}

# ---------------------------------------------------------------- scenes
S_DUO, S_TRIO = L[1]['t0'] - .12, L[2]['t0'] - .12
S_PARIS, S_BOARD, S_TAX = L[6]['t0'] - .2, L[7]['t0'] - .14, L[8]['t0'] - .14
S_BACK, S_BEACH = L[9]['t0'] - .2, L[12]['t1'] + .28
SCENES = [(0, S_PARIS, 'studio'), (S_PARIS, S_BOARD, 'paris'), (S_BOARD, S_TAX, 'board'), (S_TAX, S_BACK, 'taxes'),
          (S_BACK, S_BEACH, 'studio'), (S_BEACH, END, 'beach'), (END, DUR, 'end')]
WHIPS = [S_PARIS, S_BOARD, S_TAX, S_BACK, S_BEACH]
GLITCH = [(L[0]['t0'] + .9, .28), (L[0]['t0'] + 2.25, .18)]

def scene_at(t):
    for a, z, n in SCENES:
        if a <= t < z: return n, a
    return 'end', END

def speaker(t):
    for ln in TL:
        if ln['t0'] - .06 <= t < ln['t1'] + .1: return ln['k']
    return None

# layout per scene: clone -> (cx, scale, y offset). Bottom of every take is the waist cut, kept at/below the frame bottom.
POS_SOLO = {'b': (540, .90, 0), 'c': (540, .94, 60), 'a': (540, 1.0, 0)}
POS_SCENE = {'paris': (360, .80, 0), 'board': (720, .78, 40), 'taxes': (730, .80, 0)}   # solo away-shots: keep the set visible
POS_DUO = {'b': (300, .66, 0), 'c': (790, .60, 20)}
POS_TRIO = {'b': (240, .60, 0), 'a': (545, .53, 0), 'c': (850, .55, 20)}
HEAD = {'a': 84, 'b': 170, 'c': 164}                         # head top in the source frame (px)

def lerp(p, q, k): return tuple(p[i] + (q[i] - p[i]) * k for i in range(3))

def layout(t):
    """-> list of (clone, cx, scale, yoff, alpha) back-to-front for the studio scenes."""
    if t < S_DUO:
        return [('b', *POS_SOLO['b'], 1)]
    if t < S_TRIO:
        k = eout((t - S_DUO) / .35)
        b = lerp(POS_SOLO['b'], POS_DUO['b'], k); c = lerp((1500, .60, 20), POS_DUO['c'], k)
        return [('b', *b, 1), ('c', *c, 1)]
    k = eout((t - S_TRIO) / .35)
    b = lerp(POS_DUO['b'], POS_TRIO['b'], k); c = lerp(POS_DUO['c'], POS_TRIO['c'], k)
    a = POS_TRIO['a']; ay = 900 * (1 - back((t - S_TRIO) / .4, 1.6)) if t - S_TRIO < .4 else 0
    return [('a', a[0], a[1], a[2] + ay, 1), ('b', *b, 1), ('c', *c, 1)]

def head_xy(k, cx, s, yoff):
    top = H - s * H + yoff
    return cx, top + s * (HEAD[k] + 230)

# camera keyframes for the studio: (time, target clone or None, zoom)
CAM = [(0, None, 1.0), (L[3]['t0'] - .1, 'b', 1.55), (L[4]['t0'] - .1, 'c', 1.55), (L[5]['t0'] - .1, 'a', 1.6),
       (S_PARIS, None, 1.0),
       (S_BACK, None, 1.0), (L[9]['t0'] + .3, 'b', 1.35), (L[10]['t0'] - .1, None, 1.0), (L[11]['t0'] - .1, 'a', 1.5),
       (L[12]['t0'] - .1, None, 1.08)]

def camera(t, lay):
    prev = [c for c in CAM if c[0] <= t]; cur = prev[-1]; before = prev[-2] if len(prev) > 1 else cur
    def state(c):
        tgt, z = c[1], c[2]
        if tgt is None: return (540., 960., z)
        for k, cx, s, yo, al in lay:
            if k == tgt: x, y = head_xy(k, cx, s, yo); return (x, y, z)
        return (540., 960., 1.0)
    k = eout((t - cur[0]) / .3)
    return lerp(state(before), state(cur), k)

# ---------------------------------------------------------------- scene art (1080x1920, cached)
def vgrad(cols, h=H, w=W):
    ys = np.linspace(0, 1, h)[:, None]; n = len(cols) - 1; c = np.array(cols, np.float32)
    idx = np.minimum((ys * n).astype(int), n - 1); f = ys * n - idx
    g = c[idx[:, 0]] * (1 - f) + c[idx[:, 0] + 1] * f
    return Image.fromarray(np.repeat(g[:, None, :], w, 1).astype(np.uint8), 'RGB')

def glow(img, xy, r, col, a=.6):
    lay = Image.new('L', img.size); ImageDraw.Draw(lay).ellipse((xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r), fill=int(255 * a))
    lay = lay.filter(ImageFilter.GaussianBlur(r * .45)); c = Image.new('RGB', img.size, col)
    return Image.composite(c, img, lay)

def F(path, size): return ImageFont.truetype(path, size)
COMIC = os.path.join(HERE, 'src/ComicNeue.ttf')

def art_studio():
    im = vgrad([(6, 6, 12), (16, 12, 34), (10, 9, 20)])
    im = glow(im, (540, 980), 520, (90, 70, 230), .55); im = glow(im, (180, 300), 260, (79, 107, 255), .25)
    im = glow(im, (920, 520), 300, (154, 77, 255), .25)
    d = ImageDraw.Draw(im, 'RGBA')
    # floor grid in perspective
    hy = 1460
    for i in range(-12, 13):
        d.line((540 + i * 40, hy, 540 + i * 260, H), fill=(120, 100, 255, 40), width=2)
    for j in range(9):
        y = hy + (H - hy) * (j / 8) ** 1.8; d.line((0, y, W, y), fill=(120, 100, 255, 34), width=2)
    # halo ring behind the clones (LUMARC orb echo)
    ring = Image.new('L', im.size); ImageDraw.Draw(ring).ellipse((140, 520, 940, 1320), outline=255, width=6)
    ring = ring.filter(ImageFilter.GaussianBlur(2)); g = gradient(W, H, GRAD); im = Image.composite(g, im, ring.point(lambda v: int(v * .55)))
    halo = ring.filter(ImageFilter.GaussianBlur(26)); im = Image.composite(g, im, halo.point(lambda v: int(v * .5)))
    # neon sign
    f = font(92, 800); s = 'CLONE LAB'; w = f.getlength(s)
    m = Image.new('L', im.size); ImageDraw.Draw(m).text(((W - w) / 2, 230), s, font=f, fill=255)
    im = Image.composite(g, im, m.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .8)))
    im = Image.composite(Image.new('RGB', im.size, (236, 232, 255)), im, m.point(lambda v: int(v * .92)))
    rnd = np.random.default_rng(7); d = ImageDraw.Draw(im, 'RGBA')
    for _ in range(140):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 1400), rnd.uniform(1, 3.2)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 190, 255, int(rnd.uniform(40, 150))))
    return im

def art_paris():
    im = vgrad([(48, 52, 120), (180, 110, 170), (255, 158, 112), (255, 196, 140)])
    im = glow(im, (300, 1150), 230, (255, 226, 170), .9)
    d = ImageDraw.Draw(im, 'RGBA'); rnd = np.random.default_rng(3)
    # far skyline
    x = -20
    while x < W:
        w = rnd.uniform(60, 140); h = rnd.uniform(160, 420); d.rectangle((x, 1420 - h, x + w, 1920), fill=(92, 62, 110, 255))
        d.polygon([(x - 6, 1420 - h), (x + w / 2, 1420 - h - rnd.uniform(20, 70)), (x + w + 6, 1420 - h)], fill=(84, 56, 104, 255))
        for _ in range(int(h / 50)):
            wx, wy = rnd.uniform(x + 8, x + w - 20), rnd.uniform(1430 - h, 1400)
            d.rectangle((wx, wy, wx + 12, wy + 18), fill=(255, 210, 140, 160))
        x += w + rnd.uniform(4, 18)
    # Eiffel tower silhouette (right side)
    cx, base, top = 820, 1500, 260; col = (40, 28, 62, 255)
    def tw(y):  # half width at height y
        u = (base - y) / (base - top); return 260 * (1 - u) ** 2.4 + 10
    pts_l = [(cx - tw(y), y) for y in np.linspace(base, top, 60)]; pts_r = [(cx + tw(y), y) for y in np.linspace(top, base, 60)]
    d.polygon(pts_l + pts_r, fill=col)
    d.ellipse((cx - 130, 1330, cx + 130, 1620), fill=(255, 170, 120, 255))                  # arch opening
    d.rectangle((cx - 170, 1255, cx + 170, 1280), fill=col); d.rectangle((cx - 95, 905, cx + 95, 925), fill=col)
    d.rectangle((cx - 4, top - 90, cx + 4, top), fill=col)
    # foreground street
    d.rectangle((0, 1560, W, H), fill=(58, 40, 70, 255))
    for i in range(6): d.line((i * 220 - 60, 1920, 540, 1560), fill=(255, 190, 140, 50), width=3)
    return im

def art_board():
    im = vgrad([(10, 14, 30), (18, 24, 48), (12, 14, 26)])
    im = glow(im, (540, 520), 420, (60, 90, 200), .35)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rounded_rectangle((110, 250, 970, 800), 26, fill=(22, 28, 52, 255), outline=(120, 140, 255, 160), width=4)
    d.text((160, 290), 'INVESTOR DAY', font=font(52, 800), fill=(236, 238, 255))
    d.text((160, 360), 'Q4 · Series A', font=font(34, 400), fill=(160, 170, 210))
    # window light strips
    for i in range(7): d.rectangle((i * 160 + 10, 900, i * 160 + 120, 1350), fill=(40, 52, 96, 120))
    d.rectangle((0, 1380, W, H), fill=(30, 22, 18, 255)); d.rectangle((0, 1380, W, 1404), fill=(70, 52, 40, 255))
    return im

def art_board_chart(im, k):
    d = ImageDraw.Draw(im, 'RGBA')
    pts = [(160 + i * 90, 740 - (i ** 1.6) * 28 - 10 * math.sin(i * 1.7)) for i in range(10)]
    n = max(2, int(2 + k * 8)); d.line(pts[:n], fill=(120, 230, 160, 255), width=8, joint='curve')
    x, y = pts[n - 1]; d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(150, 255, 190, 255))
    for i in range(6):
        h = 40 + i * 28 * k; d.rectangle((640 + i * 46, 760 - h, 670 + i * 46, 760), fill=(110, 130, 255, 200))

def art_taxes():
    im = vgrad([(196, 192, 182), (176, 172, 162), (150, 146, 138)])
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((90, 70, 990, 130), fill=(235, 240, 240, 255))                              # fluorescent tube
    d.rectangle((100, 250, 980, 880), fill=(244, 244, 238, 255), outline=(150, 150, 150, 255), width=8)  # whiteboard
    d.text((150, 285), 'TAXES 101', font=F(COMIC, 92), fill=(40, 60, 160))
    for i, s in enumerate(['• Form 1040', '• Deductions', '• Brackets (part 1 of 9)', '• Depreciation schedules']):
        d.text((160, 420 + i * 92), s, font=F(COMIC, 52), fill=(60, 60, 70))
    d.rectangle((0, 1500, W, H), fill=(120, 116, 108, 255))
    # sad plant
    d.rectangle((900, 1380, 1000, 1500), fill=(120, 90, 70, 255))
    for a in (-.6, -.2, .3): d.line((950, 1380, 950 + 120 * math.sin(a), 1380 - 160 * math.cos(a) + 40), fill=(110, 130, 70, 255), width=10)
    return im.filter(ImageFilter.GaussianBlur(1.2))

def art_beach():
    im = vgrad([(70, 150, 210), (150, 200, 230), (255, 205, 160), (255, 180, 130)], h=1180)
    full = Image.new('RGB', (W, H)); full.paste(im, (0, 0))
    sea = vgrad([(40, 120, 170), (70, 160, 190)], h=260); full.paste(sea, (0, 1180))
    sand = vgrad([(240, 210, 160), (220, 186, 136)], h=H - 1440); full.paste(sand, (0, 1440))
    full = glow(full, (760, 1120), 150, (255, 240, 200), .95)
    d = ImageDraw.Draw(full, 'RGBA')
    for i in range(40):
        x = (i * 97) % W; y = 1200 + (i * 37) % 220; d.line((x, y, x + 50, y), fill=(255, 255, 255, 110), width=3)
    # umbrella
    d.line((360, 860, 420, 1600), fill=(90, 70, 60, 255), width=12)
    um = [(360 + 330 * math.cos(a), 860 - 150 * math.sin(a)) for a in np.linspace(0, math.pi, 40)]
    d.polygon(um, fill=(255, 255, 255, 255))
    for j in range(0, 40, 8): d.polygon([(360, 860)] + um[j:j + 5], fill=(106, 85, 255, 255))
    # beach chair (LUMARC stripes)
    x0, y0 = 300, 1500
    d.line((x0, y0 + 260, x0 + 120, y0), fill=(110, 80, 60, 255), width=14); d.line((x0 + 360, y0 + 260, x0 + 300, y0 + 60), fill=(110, 80, 60, 255), width=14)
    for i, col in enumerate([(79, 107, 255), (250, 249, 246), (154, 77, 255), (250, 249, 246)]):
        d.polygon([(x0 + 120 + i * 45, y0 + 10 * i / 4), (x0 + 165 + i * 45, y0 + 10 * (i + 1) / 4), (x0 + 330 + i * 8, y0 + 230), (x0 + 290 + i * 8, y0 + 230)], fill=col + (255,))
    # drink
    d.polygon([(760, 1600), (840, 1600), (820, 1700), (780, 1700)], fill=(255, 140, 90, 230))
    d.line((815, 1600, 850, 1530), fill=(255, 255, 255, 255), width=6); d.ellipse((828, 1578, 858, 1608), fill=(255, 210, 60, 255))
    return full

ART = {}
def art(name):
    if name not in ART: ART[name] = {'studio': art_studio, 'paris': art_paris, 'board': art_board, 'taxes': art_taxes, 'beach': art_beach}[name]()
    return ART[name]

# ---------------------------------------------------------------- clone tracks
def tracks():
    """re-time each clone take onto the timeline (speech at its line, its own idle footage elsewhere)."""
    N = round(DUR / G)
    for k in 'abc':
        lines = [ln for ln in TL if ln['k'] == k]; pieces = []; t = 0.0; idle_i = 0; direction = 1
        def fill(d):
            nonlocal idle_i, direction
            while d > 1e-6:
                i0, i1 = IDLE[k][idle_i % len(IDLE[k])]; seg = min(d, snap(i1 - i0))
                pieces.append((i0, snap(i0 + seg), direction < 0)); d = snap(d - seg); direction *= -1
                if direction > 0: idle_i += 1
        for ln in lines:
            fill(snap(ln['t0'] - t)); pieces.append((ln['s0'], ln['s1'], False)); t = ln['t1']
        fill(snap(DUR - t))
        fc = []; labels = []
        for i, (s0, s1, rev) in enumerate(pieces):
            fc.append(f'[0:v]trim=start={s0:.2f}:end={s1:.2f},setpts=PTS-STARTPTS{",reverse" if rev else ""}[p{i}]'); labels.append(f'[p{i}]')
        fc.append(''.join(labels) + f'concat=n={len(pieces)}:v=1:a=0,fps=25[v]')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC[k], '-filter_complex', ';'.join(fc), '-map', '[v]', '-c:v', 'libx264',
                        '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-t', f'{DUR:.2f}', os.path.join(WORK, f'track_{k}.mp4')], check=True)
        print(k, len(pieces), 'pieces')
    # voice: every line's audio at its timeline slot
    SR = 48000; voice = np.zeros(int(DUR * SR) + SR, np.float32)
    for ln in TL:
        b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ln["s0"]:.3f}', '-t', f'{ln["s1"] - ln["s0"]:.3f}', '-i', SRC[ln['k']], '-vn',
                            '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        x = np.frombuffer(b, np.float32).copy(); f = int(.012 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        i = int(ln['t0'] * SR); voice[i:i + len(x)] += x
    pcm = (np.clip(voice[:int(DUR * SR)], -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', os.path.join(WORK, 'voice.wav')], input=pcm, check=True)

def key(img):
    """green-screen key -> RGBA with despill."""
    a = np.asarray(img).astype(np.float32); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.maximum(r, b); diff = g - m
    alpha = np.clip(255 - (diff - 30) * 255 / 70, 0, 255).astype(np.uint8)
    g2 = np.where(diff > 0, m + diff * .15, g)
    out = np.dstack([r, g2, b, alpha]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

def clone_img(src, s, bright=1.0):
    w, h = int(W * s), int(H * s)
    im = src.resize((w, h), Image.BILINEAR)
    im = key(im)
    al = im.getchannel('A').filter(ImageFilter.GaussianBlur(1.1)); im.putalpha(al)
    if bright != 1: im = Image.merge('RGBA', [*Image.eval(im.convert('RGB'), lambda v: int(v * bright)).split(), al])
    return im

def paste_clone(base, im, cx, yoff, k, rim=True):
    x = int(cx - im.width / 2); y = int(H - im.height + yoff)
    if rim:   # brand-coloured rim light / shadow so the key sits in the scene
        al = im.getchannel('A'); sh = Image.new('RGBA', im.size, (90, 70, 230, 0)); sh.putalpha(al.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .55)))
        base.alpha_composite(sh, (x, y))
    base.alpha_composite(im, (x, y))

# ---------------------------------------------------------------- captions
def build_pages():
    pages = []
    for ln in TL:
        a, z = ln['t0'], ln['t1']; groups = [g.split() for g in ln['cap'].split('|')]
        flat = [w for g in groups for w in g]; wt = [syl(w.strip('*')) + .35 for w in flat]; tot = sum(wt); t = a; i = 0
        for g in groups:
            ws = []
            for w in g:
                d = (z - a) * wt[i] / tot; i += 1
                ws.append(dict(text=w.strip('*').upper(), emph=w.startswith('*'), t0=t, t1=t + d, big=False)); t += d
            pages.append(dict(words=ws, k=ln['k']))
    for i, p in enumerate(pages):
        nxt = pages[i + 1]['words'][0]['t0'] if i + 1 < len(pages) else DUR; last = p['words'][-1]['t1']
        p['a'] = p['words'][0]['t0'] - .04; p['z'] = nxt - .02 if nxt - last < .45 else last + .35
    return pages
PAGES = build_pages()

def draw_captions(fr, t, cy0):
    for p in PAGES:
        if not (p['a'] <= t < p['z']): continue
        for w, sz, cx, cy in yv.layout(p, 92):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * back(lt / .16)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.06
            img, _ = word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = fade(img, lt / .05)
            if p['z'] - t < .06: img = fade(img, (p['z'] - t) / .06)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            fr.alpha_composite(img, (int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2)))

# ---------------------------------------------------------------- overlays
def chip(text):
    im = pill('      ' + text, 38, 700, (14, 14, 22, 225)); d = ImageDraw.Draw(im); y = im.height // 2
    d.ellipse((54, y - 22, 82, y + 6), fill=(154, 120, 255)); d.polygon([(56, y - 4), (80, y - 4), (68, y + 22)], fill=(154, 120, 255))
    d.ellipse((63, y - 13, 73, y - 3), fill=(14, 14, 22))
    return im

def counters(fr, t):
    ln = L[5]
    if ln['t0'] + .5 <= t < ln['t1'] + .3:
        lt = t - ln['t0'] - .5; n = int(30 * eout(lt / 1.3))
        put(fr, pill(f'POSTS THIS MONTH: {n}', 40, 800, grad=True), W / 2, 1480, popin(lt), 1 - clamp((t - ln['t1']) / .3))
    if ln['t0'] + 2.0 <= t < ln['t1'] + .3:
        lt = t - ln['t0'] - 2.0
        im = cached('rec0', lambda: pill('RECORDINGS: 0', 40, 800, (230, 50, 70, 235)))
        put(fr, im, W / 2, 1590, popin(lt), 1 - clamp((t - ln['t1']) / .3))

def views0(fr, t):
    ln = L[8]; at = ln['t0'] + (15.10 - 13.04)
    if at <= t < ln['t1'] + .2:
        im = cached('v0', lambda: eye_pill('0 views'))
        put(fr, im, W / 2, 1560, popin(t - at), 1 - clamp((t - ln['t1']) / .2))

def eye_pill(text):
    im = pill('      ' + text, 42, 700, (20, 20, 28, 230)); d = ImageDraw.Draw(im); y = im.height // 2
    d.ellipse((50, y - 14, 92, y + 14), outline=WHITE, width=4); d.ellipse((64, y - 7, 78, y + 7), fill=WHITE)
    return im

_logo = None
def logo_pop(fr, t):
    global _logo
    ln = L[10]
    if ln['t0'] <= t < ln['t1'] + .25:
        if _logo is None:
            lg = Image.open(LOGO).convert('RGBA'); lg = lg.resize((520, int(lg.height * 520 / lg.width)), Image.LANCZOS)
            gl = Image.new('RGBA', (lg.width + 120, lg.height + 120), (0, 0, 0, 0)); a = Image.new('L', gl.size); a.paste(lg.getchannel('A'), (60, 60))
            halo = Image.new('RGBA', gl.size, (120, 90, 255, 0)); halo.putalpha(a.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * .8)))
            gl.alpha_composite(halo); gl.alpha_composite(lg, (60, 60)); _logo = gl
        put(fr, _logo, W / 2, 1500, popin(t - ln['t0'], .3), 1 - clamp((t - ln['t1'] - .1) / .15))

def comment(fr, t):
    ln = L[11]; a = ln['t0'] + .25; z = L[12]['t0'] - .05
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
    d.text((170, 52), 'you', font=font(34, 700), fill=(235, 235, 242)); d.text((170 + font(34, 700).getlength('you') + 16, 56), 'now', font=font(28, 400), fill=MUTED)
    n = int(clamp((lt - .1) / .07, 0, 5)); txt = 'CLONE'[:n]; d.text((170, 96), txt, font=font(52, 800), fill=WHITE)
    if n < 5 and int(lt * 6) % 2 == 0:
        x = 172 + font(52, 800).getlength(txt); d.rectangle((x, 102, x + 4, 150), fill=WHITE)
    on = n >= 5 and lt > .5; col = (255, 60, 100) if on else (180, 180, 195); hx, hy = 30 + bw - 70, 30 + bh // 2
    r = 13 * (1 + .5 * math.exp(-(lt - .5) / .1) if on else 1)
    d.ellipse((hx - 2 * r, hy - r * 1.2, hx, hy + r * .5), fill=col if on else None, outline=col, width=3)
    d.ellipse((hx, hy - r * 1.2, hx + 2 * r, hy + r * .5), fill=col if on else None, outline=col, width=3)
    d.polygon([(hx - 2 * r + 1, hy - r * .1), (hx + 2 * r - 1, hy - r * .1), (hx, hy + r * 1.9)], fill=col if on else None, outline=col)
    put(fr, card, W / 2, 1560, popin(lt, .25), 1 - clamp((t - (z - .1)) / .1))

def endcard(fr, t):
    if t < END: return
    lt = t - END
    if lt >= .9: put(fr, cached('cta', lambda: pill('Comment “CLONE”', 56, 800, grad=True, padx=56, pady=26)), W / 2, 1250, popin(lt - .9, .3))
    if lt >= 1.2:
        a = clamp((lt - 1.2) / .3)
        put(fr, cached('tag', lambda: text_im('Your clone. Your content. Zero camera.', 40, 500, (225, 225, 235))), W / 2, 1395, 1, a)
        put(fr, cached('hdl', lambda: text_im('@lumarc_studio  ·  slumarc.com', 32, 500, MUTED)), W / 2, 1455, 1, a)

def glitch(img, t):
    for at, d in GLITCH:
        if at <= t < at + d:
            a = np.asarray(img).copy(); r = np.random.default_rng(int(t * 1000))
            for _ in range(9):
                y = r.integers(0, H - 80); h = r.integers(12, 90); sh = r.integers(-90, 90); a[y:y + h] = np.roll(a[y:y + h], sh, 1)
            k = int(r.integers(8, 22)); a[..., 0] = np.roll(a[..., 0], k, 1); a[..., 2] = np.roll(a[..., 2], -k, 1)
            return Image.fromarray(a)
    return img

# ---------------------------------------------------------------- frame
class Edit:
    def __init__(self, t0):
        self.t0 = t0; self.trk = {k: Reader(os.path.join(WORK, f'track_{k}.mp4'), t0, DUR - t0 + .5) for k in 'abc'}
        self.end = None
    def src(self, k, t): return self.trk[k].get(int(round((t - self.t0) * FPS)))
    def scene(self, t):
        name, a = scene_at(t)
        if name == 'end': return self.endframe(t)
        lt = t - a
        bg = art(name).copy() if name != 'board' else art('board').copy()
        if name == 'board': art_board_chart(bg, clamp(lt / 2.2))
        bg = zoom(bg, 1.0 + .025 * lt, (540, 900)).convert('RGBA')
        sp = speaker(t)
        if name == 'studio':
            lay = layout(t)
            for k, cx, s, yo, al in lay:
                bright = 1.0 if (sp in (None, k) or len(lay) == 1) else .72
                paste_clone(bg, clone_img(self.src(k, t), s, bright), cx, yo, k)
            # name tags above heads in group shots
            if len(lay) > 1 or t > L[0]['t0'] + 2.2:
                for k, cx, s, yo, al in lay:
                    first = {'b': L[0]['t0'] + 2.2, 'c': L[1]['t0'], 'a': L[2]['t0']}[k]
                    if t >= first:
                        hx, hy = head_xy(k, cx, s, yo)
                        tx, ty = (hx, hy - s * 330) if len(lay) > 1 else (hx + 300, hy - 40)
                        put(bg, cached('tag' + k + str(len(lay) > 1), lambda k=k, g=len(lay) > 1: pill(NAME[k], 30 if g else 40, 800, grad=True)), tx, ty, popin(t - first))
            x, y, z = camera(t, lay)
            k = min(1, max(0, (z - 1) / .35)); X = x + (540 - x) * k; Y = y + (700 - y) * k
            X = min(max(X, W - z * (W - x)), z * x); Y = min(max(Y, H - z * (H - y)), z * y)   # never expose the canvas edge
            img = zoom(bg.convert('RGB'), z, (x, y), dx=X - x, dy=Y - y)
            cap_y = 1310 if z > 1.2 or len(lay) == 1 else 560
        elif name == 'beach':
            img = bg.convert('RGB'); cap_y = 560
        else:
            k = {'paris': 'b', 'board': 'c', 'taxes': 'a'}[name]
            pos = POS_SCENE[name]; s = pos[1] * (1.0 + .02 * lt)
            im = clone_img(self.src(k, t), s)
            if name == 'taxes':  # dull: desaturate the presenter a bit
                rgb = im.convert('RGB'); g = rgb.convert('L').convert('RGB'); im = Image.merge('RGBA', [*Image.blend(rgb, g, .45).split(), im.getchannel('A')])
            paste_clone(bg, im, pos[0], pos[2], k, rim=name != 'taxes')
            img = bg.convert('RGB'); cap_y = 1310
        return img, name, cap_y
    def endframe(self, t):
        if self.end is None:
            b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '29.9', '-i', HY, '-frames:v', '1', '-vf', f'scale={W}:{H}',
                                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            self.end = Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1).copy()
            self.endr = Reader(HY, 28.3, 1.6)
        lt = t - END
        img = self.endr.get(int(round(lt * FPS))) if lt < 1.55 else self.end
        return zoom(img, 1 + .02 * lt), 'end', 0
    def frame(self, t):
        for k in 'abc': self.src(k, t)           # keep every track in step
        # whip pan between scenes
        wp = next((w for w in WHIPS if w - .12 <= t < w + .12), None)
        if wp is not None:
            p = (t - (wp - .12)) / .24; A, _, cy_a = self.scene(min(t, wp - 1 / FPS)); B, _, cy_b = self.scene(max(t, wp))
            c = Image.new('RGB', (W, H)); off = int(W * eout(p) if p < 1 else W)
            c.paste(A, (-off, 0)); c.paste(B, (W - off, 0))
            img = c.resize((W // 10, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
            img = Image.blend(c, img, .75 * (1 - abs(p - .5) * 2)); name = 'whip'; cap_y = cy_b if p > .5 else cy_a
        else:
            img, name, cap_y = self.scene(t)
        img = glitch(img, t)
        for at, amt in [(0.0, .7), (S_BEACH + .12, .35), (END, .6)]:
            if at <= t < at + .3:
                a = np.asarray(img).astype(np.float32); img = Image.fromarray(np.clip(a + (255 - a) * amt * math.exp(-(t - at) / .07), 0, 255).astype(np.uint8))
        fr = img.convert('RGBA')
        sc, sa = scene_at(t)
        if sc in ('paris', 'board', 'taxes') and name != 'whip':
            label = {'paris': 'MONDAY · PARIS', 'board': 'TUESDAY · INVESTORS', 'taxes': 'WEDNESDAY · TAXES'}[sc]
            put(fr, cached('chip' + sc, lambda: chip(label)), W / 2, 170, popin(t - sa - .1))
        if sc == 'beach' and name != 'whip':
            put(fr, cached('ooo', lambda: chip('OUT OF OFFICE')), W / 2, 170, popin(t - sa - .3))
        counters(fr, t); views0(fr, t); logo_pop(fr, t); comment(fr, t)
        if name != 'end': draw_captions(fr, t, cap_y)
        endcard(fr, t)
        return fr.convert('RGB')

def render(t0=0., t1=None):
    t1 = DUR if t1 is None else t1
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', os.path.join(OUT, 'video.mp4')], stdin=subprocess.PIPE)
    E = Edit(t0)
    for i in range(int(round((t1 - t0) * FPS))):
        enc.stdin.write(E.frame(t0 + i / FPS).tobytes())
        if i % 150 == 0: print(f'{t0 + i / FPS:.1f}', flush=True)
    enc.stdin.close(); enc.wait()

def stills(ts):
    for t in ts:
        E = Edit(t); E.frame(t).save(os.path.join(OUT, f'still_{t:05.2f}.jpg'), quality=88)

def cues():
    c = dict(dur=DUR, end=END, lines=[[ln['k'], ln['t0'], ln['t1']] for ln in TL], whips=WHIPS, glitch=[g[0] for g in GLITCH],
             duo=S_DUO, trio=S_TRIO, paris=S_PARIS, board=S_BOARD, tax=S_TAX, back=S_BACK, beach=S_BEACH,
             crickets=L[8]['t0'] + (15.10 - 13.04), logo=L[10]['t0'], comment=L[11]['t0'] + .25, realone=L[12]['t0'],
             counter=[L[5]['t0'] + .5, L[5]['t0'] + 2.0])
    json.dump(c, open(os.path.join(HERE, 'cues.json'), 'w'), indent=1)

def mux():
    fin = os.path.join(OUT, 'lumarc-clones.mp4')
    af = ('[0:a]aresample=48000,highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'apad=whole_dur=%.2f,asplit=2[v][key];[1:a]volume=0.42[m];[m][key]sidechaincompress=threshold=0.05:ratio=4:attack=25:release=320[md];'
          '[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]' % DUR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(WORK, 'voice.wav'), '-i', os.path.join(HERE, 'music.wav'), '-filter_complex', af,
                    '-map', '[a]', '-c:a', 'pcm_s16le', '-ar', '48000', os.path.join(OUT, 'mix.wav')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'video.mp4'), '-i', os.path.join(OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}', fin], check=True)
    print(fin, os.path.getsize(fin) / 1e6, 'MB')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'render'
    if cmd == 'tracks': tracks()
    elif cmd == 'cues': cues()
    elif cmd == 'render': render(*[float(x) for x in sys.argv[2:4]])
    elif cmd == 'stills': stills([float(x) for x in sys.argv[2:]])
    elif cmd == 'mux': mux()
