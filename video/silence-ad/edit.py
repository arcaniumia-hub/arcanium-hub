"""SILENCE — "what if instead of presenting your product like this..." (1920x1080, 24 fps, 30 s).
Inputs (cwd): prod.png, clips/{T,A1,A2,A3,B1,B2,C1,C2,C3,D1,D2}.mp4, logo_raw.png, fonts/, mix.wav
Usage: python3 edit.py out.mp4
"""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1920, 1080, 24, 30.0
BEAT = 60 / 118
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def ein(x): x = clamp(x); return x ** 3
def rnd(i): v = math.sin(i * 127.1 + 311.7) * 43758.5453; return v - math.floor(v)
INTER = {w: f'fonts/Inter-{w}.ttf' for w in (300, 500, 600)}
def F(w, size): return ImageFont.truetype(INTER[w], size)
def comp(base, p, x, y):  # alpha_composite that tolerates off-canvas positions
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y)
    r, b = min(p.width, base.width - x), min(p.height, base.height - y)
    if r > l and b > t: base.alpha_composite(p.crop((l, t, r, b)) if (l or t or r < p.width or b < p.height) else p, (x + l, y + t))

# ---------- timeline: (start, end, clip, src_in, speed, grade)
C1 = 13.0; C2 = C1 + 5 * BEAT; C3 = C1 + 11 * BEAT; D = C1 + 16 * BEAT
SHOTS = [
    (4.50, 6.00, 'T', 0.00, 1.0, 'void'),
    (6.00, 7.20, 'A1', 1.00, 1.0, 'cold'), (7.20, 8.00, 'A3', 0.40, 1.0, 'cold'),
    (8.00, 8.60, 'A2', 1.20, 1.0, 'cold'), (8.60, 9.20, 'A1', 3.20, 1.0, 'cold'),
    (9.20, 9.60, 'A3', 2.40, 1.0, 'cold'), (9.60, 10.0, 'A2', 3.20, 1.0, 'cold'),
    (10.0, 11.4, 'B1', 0.20, 0.85, 'turn'), (11.4, 13.0, 'B2', 2.40, 0.6, 'warm'),
    (C1, C2, 'C1', 0.40, 1.0, 'warm'), (C2, C3, 'C2', 0.70, 1.0, 'warm'), (C3, D, 'C3', 0.60, 1.0, 'blue'),
    (D, 23.6, 'D1', 1.20, 1.0, 'void'), (23.6, 25.8, 'D2', 0.50, 0.9, 'void'),
]

class Reader:
    """Streams one shot's frames from ffmpeg (speed < 1 → blended slow motion)."""
    def __init__(self, s):
        a, b, clip, src, sp, _ = s
        n = round((b - a) * FPS) + 2
        vf = f'setpts=(PTS-STARTPTS)/{sp},framerate=fps={FPS}' if sp != 1 else f'fps={FPS}'
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(src), '-i', f'clips/{clip}.mp4', '-vf', vf + f',scale={W}:{H}',
                                   '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: self.last = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        return self.last

# ---------- grading
LUMA = np.array([.2126, .7152, .0722], np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - .28 * (((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)).clip(.55, 1)[..., None]
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def grain(i):
    g = GRAIN[i % 6]; return np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
def grade(f, kind, k=0.):
    x = f.astype(np.float32) / 255
    if kind == 'flat':
        x = x * .82 + .2
    else:
        def cold(x):
            y = (x @ LUMA)[..., None]; return (y + (x - y) * .55) * np.array([.93, 1., 1.07], np.float32)
        def warm(x): return np.clip((x - .035) / .965, 0, 1) ** 1.05 * np.array([1.06, 1., .9], np.float32)
        if kind == 'cold': x = cold(x)
        elif kind == 'warm': x = warm(x)
        elif kind == 'turn':  # cold -> warm gold across the shot
            w = clamp((k - .35) / .55); x = cold(x) * (1 - w) + warm(x) * w
        elif kind == 'blue': x = np.clip((x - .03) / .97, 0, 1) ** 1.06
        elif kind == 'void': x = np.clip((x - .025) / .975, 0, 1) ** 1.08
        x = x * VIG
    return x

def finish(x, i, amt=.022):
    x = x + grain(i) * amt
    return (np.clip(x, 0, 1) * 255 + .5).astype(np.uint8)

# ---------- PART 1: the "before" post
prod = Image.open('prod.png').convert('RGB').resize((W, H), Image.LANCZOS)
BEFORE = np.asarray(prod)
def sticker_text():
    f = ImageFont.truetype('fonts/ArchivoBlack.ttf', 118)
    d0 = ImageDraw.Draw(Image.new('L', (1, 1))); s = 'NEW HEADPHONES!!'
    w = d0.textbbox((0, 0), s, font=f)[2]
    im = Image.new('RGBA', (w + 60, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((34, 26), s, font=f, fill=(20, 20, 160, 255))
    d.text((26, 18), s, font=f, fill=(235, 18, 30, 255), stroke_width=5, stroke_fill=(255, 236, 0, 255))
    return im
def sticker_burst():
    im = Image.new('RGBA', (420, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for k in range(36):
        r = 205 if k % 2 == 0 else 160; a = k * math.pi / 18
        pts.append((210 + r * math.cos(a), 210 + r * math.sin(a)))
    d.polygon(pts, fill=(255, 226, 0, 255), outline=(230, 30, 30, 255), width=6)
    f = ImageFont.truetype('fonts/ArchivoBlack.ttf', 96); f2 = ImageFont.truetype('fonts/ArchivoBlack.ttf', 84)
    for s, ff, y in (('50%', f, 150), ('OFF', f2, 262)):
        w = d.textbbox((0, 0), s, font=ff)[2]; d.text((210 - w / 2, y - 60), s, font=ff, fill=(225, 20, 30, 255))
    return im.rotate(-12, expand=True, resample=Image.BICUBIC)
def sticker_button():
    im = Image.new('RGBA', (470, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 14, 462, 144), 28, fill=(0, 30, 120, 255))
    d.rounded_rectangle((0, 0, 454, 130), 28, fill=(25, 90, 255, 255), outline=(120, 220, 255, 255), width=4)
    f = ImageFont.truetype('fonts/ArchivoBlack.ttf', 64); s = 'BUY NOW'
    w = d.textbbox((0, 0), s, font=f)[2]; d.text((227 - w / 2, 22), s, font=f, fill=(255, 255, 255, 255))
    return im
STICKERS = [(sticker_text(), 960, 150, -1), (sticker_burst(), 1610, 700, 1), (sticker_button(), 420, 930, -1)]
def before_frame(t):
    z = 1 + .03 * min(t, 3.8) / 3.8
    cw, ch = int(W / z), int(H / z)
    im = prod.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BICUBIC)
    base = Image.fromarray(finish(grade(np.asarray(im), 'flat'), 0, .006)).convert('RGBA')
    for i, (spr, cx, cy, sgn) in enumerate(STICKERS):
        u = seg(t, 3.75 + i * .07, 4.35 + i * .07)
        if u >= 1: continue
        lift = eout(min(u / .3, 1)); fall = max(0., (u - .2) / .8)
        sc = 1 + .1 * lift; rot = sgn * (6 * lift + 55 * fall ** 1.5)
        y = cy - 18 * lift + 1700 * fall ** 2; x = cx + sgn * 160 * fall
        s = spr.resize((int(spr.width * sc), int(spr.height * sc)), Image.BICUBIC).rotate(rot, expand=True, resample=Image.BICUBIC)
        if lift > 0:  # paper lifting off: soft shadow
            sh = Image.new('RGBA', s.size, (0, 0, 0, 0)); sh.putalpha(s.split()[3].point(lambda v: int(v * .35 * lift)).filter(ImageFilter.GaussianBlur(12)))
            comp(base, sh, x - s.width / 2 + 14 * lift, y - s.height / 2 + 22 * lift)
        comp(base, s, x - s.width / 2, y - s.height / 2)
    return base.convert('RGB')

# ---------- the shatter (4.50 → 5.25): the flat post breaks into shards that fly past camera
FROZEN = None
SHARDS = []
EDGES = []
def build_shards():
    global FROZEN
    FROZEN = Image.fromarray(np.asarray(before_frame(4.6)))  # stickers already gone
    def rr(p): return math.hypot(p[0] - W / 2, (p[1] - H / 2) / .9)
    def near(A, r): return min(range(len(A)), key=lambda n: abs(rr(A[n]) - r))
    k = 0; bands = (0, 150, 330, 560, 900, 9999)
    for c in range(15):  # shards follow the crack web: wedges between radial cracks, cut by the rings
        A, B = CRACKS[c], CRACKS[(c + 1) % 15]
        for b0, b1 in zip(bands, bands[1:]):
            ia0, ia1, ib0, ib1 = near(A, b0), near(A, b1), near(B, b0), near(B, b1)
            poly = A[ia0:ia1 + 1] + B[ib0:ib1 + 1][::-1]
            if len(poly) < 3: continue
            xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
            x0, y0 = max(0, int(min(xs))), max(0, int(min(ys))); x1, y1 = min(W, int(math.ceil(max(xs))) + 1), min(H, int(math.ceil(max(ys))) + 1)
            if x1 - x0 < 2 or y1 - y0 < 2: continue
            m = Image.new('L', (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(m).polygon([(p[0] - x0, p[1] - y0) for p in poly], fill=255)
            patch = FROZEN.crop((x0, y0, x1, y1)).convert('RGBA'); patch.putalpha(m)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            dx, dy = cx - W / 2, cy - H / 2; dist = math.hypot(dx, dy) + 1
            SHARDS.append(dict(p=patch, cx=cx, cy=cy, ux=dx / dist, uy=dy / dist, dist=dist,
                               v=700 + 1100 * rnd(k * 3.3), rot=(rnd(k * 5.1) - .5) * 120, delay=.2 * dist / 1300 * (.5 + .5 * rnd(k + 9))))
            k += 1
CRACKS = []
for c in range(15):  # radial glass cracks with jagged kinks, plus web rings between them
    a0 = c / 15 * 2 * math.pi + (rnd(c * 3.7) - .5) * .3; pts = [(W / 2, H / 2)]; r = 0
    while r < 1300:
        r += 60 + 90 * rnd(c * 11 + r); a = a0 + (rnd(c * 7 + r * .13) - .5) * .35
        pts.append((W / 2 + r * math.cos(a), H / 2 + r * .9 * math.sin(a)))
    CRACKS.append(pts)
def cracks(im, t):  # glass cracks race out from the product just before the break
    R = 1300 * eout(seg(t, 4.34, 4.5)); d = ImageDraw.Draw(im)
    for pts in CRACKS:
        seg_pts = [p for p in pts if math.hypot(p[0] - W / 2, p[1] - H / 2) <= R]
        if len(seg_pts) > 1:
            d.line([(x + 2, y + 2) for x, y in seg_pts], fill=(120, 120, 120), width=3); d.line(seg_pts, fill=(255, 255, 255), width=2)
    for ring in (150, 330, 560):
        if R < ring: continue
        for c in range(15):
            p = CRACKS[c]; q = CRACKS[(c + 1) % 15]
            pi = min(p, key=lambda v: abs(math.hypot(v[0] - W / 2, v[1] - H / 2) - ring)); qi = min(q, key=lambda v: abs(math.hypot(v[0] - W / 2, v[1] - H / 2) - ring))
            if rnd(c * 5 + ring) > .35: d.line([pi, qi], fill=(255, 255, 255), width=2)
    return im
def shatter(under, t):
    u = (t - 4.5) / .5
    base = Image.fromarray(under).convert('RGBA')
    for s in SHARDS:
        q = clamp((u - s['delay']) / (1 - s['delay']))
        e = q ** 2
        zs = 1 + 4.5 * e * (1.4 - s['dist'] / 1300)
        if zs > 7 or q >= 1: continue
        x = s['cx'] + s['ux'] * (s['v'] * e + 260 * e * zs); y = s['cy'] + s['uy'] * (s['v'] * e + 260 * e * zs) + 300 * e * e
        p = s['p']
        if e > 0: p = p.resize((max(1, int(p.width * zs)), max(1, int(p.height * zs))), Image.BILINEAR).rotate(s['rot'] * e, expand=True, resample=Image.BILINEAR)
        a = 1 - clamp((q - .3) / .5)
        if a < 1: p = p.copy(); p.putalpha(p.split()[3].point(lambda v: int(v * a)))
        comp(base, p, x - p.width / 2, y - p.height / 2)
    return np.asarray(base.convert('RGB'))

# ---------- text / end card
def text_im(s, f, fill=(255, 255, 255), tracking=0):
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    if tracking:
        ws = [d0.textlength(ch, font=f) for ch in s]; w = int(sum(ws) + tracking * (len(s) - 1))
    else: w = int(d0.textlength(s, font=f))
    asc, desc = f.getmetrics(); im = Image.new('RGBA', (w + 8, asc + desc + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if tracking:
        x = 4
        for ch, cw in zip(s, ws): d.text((x, 4), ch, font=f, fill=fill); x += cw + tracking
    else: d.text((4, 4), s, font=f, fill=fill)
    return im
TAG = text_im('Same product. Different story.', F(500, 58))
logo = Image.open('logo_raw.png').convert('RGBA')
la = np.asarray(logo).copy(); la[..., 3] = np.where(la[..., 3] < 40, 0, la[..., 3]); logo = Image.fromarray(la)
LOGO = logo.resize((int(logo.width * 1.1), int(logo.height * 1.1)), Image.LANCZOS)
L_SEEN = text_im('Be seen.', F(500, 50)); L_REM = text_im('Be remembered.', F(500, 50))
BTN = Image.new('RGBA', (420, 76), (0, 0, 0, 0)); _d = ImageDraw.Draw(BTN)
_d.rounded_rectangle((1, 1, 418, 74), 37, outline=(255, 255, 255, 215), width=2)
_bt = text_im('Get your free quote', F(500, 27)); BTN.alpha_composite(_bt, ((420 - _bt.width) // 2, (76 - _bt.height) // 2 + 1))
URL = text_im('SLUMARC.COM', F(500, 21), (255, 255, 255, 200), tracking=9)
def card_base():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    im.alpha_composite(L_SEEN, ((W - L_SEEN.width) // 2, 612)); im.alpha_composite(L_REM, ((W - L_REM.width) // 2, 676))
    im.alpha_composite(BTN, ((W - BTN.width) // 2, 790)); im.alpha_composite(URL, ((W - URL.width) // 2, 990))
    return im
CARD = card_base()
LX, LY = (W - LOGO.width) // 2, 300
L_ALPHA = np.asarray(LOGO)[..., 3:].astype(np.float32) / 255
L_RGB = np.asarray(LOGO)[..., :3].astype(np.float32) / 255
def end_card(t):
    x = np.asarray(CARD.convert('RGB')).astype(np.float32) / 255
    u = seg(t, 27.75, 29.0)  # single soft light sweep over the logo, then still
    lw = LOGO.width; cols = np.arange(lw, dtype=np.float32)[None, :] + np.arange(LOGO.height, dtype=np.float32)[:, None] * .45
    band = np.exp(-((cols - (-260 + (lw + 520) * eout(u) * 1.0)) / 70) ** 2)[..., None] * (0 < u < 1)
    rgb = np.clip(L_RGB + band * .85, 0, 1)
    sub = x[LY:LY + LOGO.height, LX:LX + lw]
    x[LY:LY + LOGO.height, LX:LX + lw] = sub * (1 - L_ALPHA) + rgb * L_ALPHA
    return x

# ---------- render
def main(out):
    build_shards()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', 'mix.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', out], stdin=subprocess.PIPE)
    readers = {}; N = int(DUR * FPS)
    for i in range(N):
        t = i / FPS
        if t < 4.5:
            im = before_frame(t)
            if t >= 4.36: im = cracks(im, t)
            fr = finish(np.asarray(im).astype(np.float32) / 255, i, .006)
        elif t < 25.8:
            si = next(k for k, s in enumerate(SHOTS) if s[0] <= t + 1e-6 < s[1])
            s = SHOTS[si]
            if si not in readers:
                for k in list(readers): readers.pop(k).p.kill()
                readers[si] = Reader(s)
            raw = readers[si].next(); k = (t - s[0]) / (s[1] - s[0])
            if s[2] == 'T':  # camera pushes through the broken post into the void
                z = 1 + .07 * eout(seg(t, 4.5, 6.0)); cw, ch = int(W / z), int(H / z)
                raw = np.asarray(Image.fromarray(raw).crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BICUBIC))
            x = grade(raw, s[5], k)
            if s[2] == 'T' and t < 5.0:
                x = np.asarray(shatter(finish(x, i), t)).astype(np.float32) / 255
                x = x + max(0, 1 - (t - 4.5) / .09) * .4  # impact flash
            if 6.0 <= t < 10.0:  # chaos: micro shake escalates
                amp = int(2 + 10 * seg(t, 6, 10)); dx = int((rnd(i) - .5) * amp); dy = int((rnd(i + 99) - .5) * amp)
                x = np.roll(np.roll(x, dx, 1), dy, 0)
            if s[2] == 'C3' and t > D - .17:  # match cut: city lights bloom into the light beam
                x = x + ((t - (D - .17)) / .17) ** 2 * .55 * np.array([1., .9, .75], np.float32)
            if s[2] == 'D1' and t < D + .25:
                x = x + (1 - (t - D) / .25) ** 2 * .55 * np.array([1., .9, .75], np.float32)
            if t > 25.3: x = x * (1 - seg(t, 25.3, 25.8))
            fr = finish(x, i)
        elif t < 27.3:
            a = eout(seg(t, 25.95, 26.25)) * (1 - seg(t, 27.0, 27.3))
            im = Image.new('RGBA', (W, H), (0, 0, 0, 255))
            tg = TAG.copy(); tg.putalpha(tg.split()[3].point(lambda v: int(v * a)))
            im.alpha_composite(tg, ((W - TAG.width) // 2, (H - TAG.height) // 2))
            fr = finish(np.asarray(im.convert('RGB')).astype(np.float32) / 255, i, .012)
        else:
            x = end_card(t) * eout(seg(t, 27.3, 27.6))
            fr = finish(x, i if t < 29.0 else 0, .012)  # last second: frozen grain = truly still
        enc.stdin.write(fr.tobytes())
        if i % 48 == 0: print('frame', i, flush=True)
    enc.stdin.close(); enc.wait(); print('done')

if __name__ == '__main__':
    main(sys.argv[1])
