"""Assembles the SOLARA before/after reel (1080x1920, 30fps, 30s).
Inputs in cwd: k1.png (before photo), k3.png (hero splash), c1..c4.mp4 (Kling clips),
music.wav, fonts/Montserrat-ExtraBold.ttf, fonts/ComicNeue-Bold.ttf
Usage: python3 edit.py out.mp4
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS, DUR = 1080, 1920, 30, 30.0
FB = '/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf'
FC = 'ComicNeue-Bold.ttf'
ORANGE = (255, 140, 30)

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def eback(x):
    x = clamp(x); c1 = 1.7; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def cover(im, w=W, h=H):
    im = im.convert('RGB'); s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))

# ---------- text sprites
def text_img(lines, size, fill=(255, 255, 255), font=FB, glow=None, stroke=0, stroke_fill=(0, 0, 0), spacing=1.12):
    f = ImageFont.truetype(font, size)
    d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    ws = [d0.textbbox((0, 0), l, font=f, stroke_width=stroke)[2] for l in lines]
    lh = int(size * spacing); pad = 60
    im = Image.new('RGBA', (max(ws) + pad * 2, lh * len(lines) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = pad + (max(ws) - ws[i]) // 2
        d.text((x, pad + i * lh), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    if glow:
        a = im.split()[3].filter(ImageFilter.GaussianBlur(glow[1]))
        g = Image.new('RGBA', im.size, glow[0] + (0,)); g.putalpha(a.point(lambda v: min(255, int(v * glow[2]))))
        im = Image.alpha_composite(g, im)
    return im

def chip(lines, size, bg=(255, 255, 255), fg=(15, 15, 15), radius=26):
    f = ImageFont.truetype(FB, size)
    d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    lh = int(size * 1.25); padx, pady = 34, 22
    boxes = []
    for l in lines:
        b = d0.textbbox((0, 0), l, font=f); boxes.append((b[2] - b[0], l, b))
    wmax = max(b[0] for b in boxes)
    im = Image.new('RGBA', (wmax + padx * 2 + 20, lh * len(lines) + pady * 2 + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (w, l, b) in enumerate(boxes):
        x0 = 10 + (wmax - w) // 2; y0 = 10 + i * lh
        d.rounded_rectangle((x0, y0, x0 + w + padx * 2, y0 + lh + pady * 2 - (pady if 0 < i else 0)), radius, fill=bg)
    for i, (w, l, b) in enumerate(boxes):
        x0 = 10 + (wmax - w) // 2; y0 = 10 + i * lh
        d.text((x0 + padx - b[0], y0 + pady + (lh - size) // 2 - b[1] + 4), l, font=f, fill=fg)
    return im

def place(frame, spr, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if alpha <= 0.01: return
    s = spr
    if abs(scale - 1) > .003: s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BICUBIC)
    if abs(rot) > .01: s = s.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < .999:
        a = s.split()[3].point(lambda v: int(v * alpha)); s = s.copy(); s.putalpha(a)
    frame.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

# ---------- assets
before = Image.open('k1.png'); hero = Image.open('k3.png')
before_full = cover(before.resize((before.width, before.height)))
gray = ImageEnhance.Color(before_full).enhance(.55)

T_INTRO = chip(['What if instead of showing', 'your product like this...'], 50)
T_CHEAP = text_img(['SOLARA - Orange Drink', 'BUY NOW!!!'], 66, fill=(230, 20, 20), font=FC, stroke=4, stroke_fill=(255, 235, 0))
T_YOU = text_img(['...you showed it', 'like'], 92, glow=((0, 0, 0), 12, 1.0))
T_THIS = text_img(['THIS?'], 230, fill=ORANGE, glow=(ORANGE, 28, 1.6))
WORDS = [(15.35, 'VITAMIN C'), (16.45, 'ZINC'), (17.55, 'MAGNESIUM'), (18.65, 'ZERO ADDED SUGAR')]
T_WORDS = [text_img([w], 104 if len(w) < 12 else 84, glow=((255, 120, 0), 22, 1.8), stroke=2, stroke_fill=(120, 50, 0)) for _, w in WORDS]
T_FUEL = text_img(['SUN-POWERED', 'ORANGE FUEL.'], 104, glow=((0, 0, 0), 18, 1.2))
T_SAME = text_img(['Same product.'], 96, glow=((0, 0, 0), 16, 1.3))
T_DIFF = text_img(['Different story.'], 96, fill=ORANGE, glow=((0, 0, 0), 16, 1.3))
T_ASK = chip(['Which one would you buy?'], 50)
T_BEF = chip(['BEFORE'], 36, bg=(40, 40, 40), fg=(235, 235, 235))
T_AFT = chip(['AFTER'], 36, bg=ORANGE, fg=(20, 10, 0))

# ---------- clip readers
class Clip:
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', path, '-vf',
            f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
            stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: self.last = Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1)
        return self.last

CLIPS = {k: Clip(f'c{k}.mp4') for k in (1, 2, 3, 4)}
SEGS = [(5.0, 10.0, 1), (10.0, 15.0, 2), (15.0, 20.0, 3), (20.0, 25.0, 4)]
hero_last = None

enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-i', 'mix.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
    '-movflags', '+faststart', '-shortest', sys.argv[1]], stdin=subprocess.PIPE)

rng = np.random.default_rng(1)
for f in range(int(DUR * FPS)):
    t = f / FPS
    # ----- base picture
    if t < 4.0:
        z = 1 + .05 * t / 4
        b = before_full.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox, oy = (b.width - W) // 2, (b.height - H) // 2
        base = b.crop((ox, oy, ox + W, oy + H))
    elif t < 5.0:
        base = Image.new('RGB', (W, H), (8, 6, 5))
    elif t < 25.0:
        k = [s for s in SEGS if s[0] <= t < s[1]][0][2]
        base = CLIPS[k].next()
        if k == 3: hero_last = base
    else:
        # split screen: before (left, desaturated) vs after (right, hero)
        base = Image.new('RGB', (W, H))
        sl = seg(t, 25.0, 25.5)
        L = gray.crop((270, 0, 810, H)); Rr = cover(hero).crop((270, 0, 810, H))
        base.paste(L, (0, 0)); base.paste(Rr, (540, 0))
        d = ImageDraw.Draw(base); d.rectangle((538, 0, 541, H), fill=(255, 255, 255))
        if sl < 1 and CLIPS[4].last is not None:  # split screen wipes in from the right
            pw = int(W * (1 - eout(sl)))
            if pw > 0: base.paste(CLIPS[4].last.crop((0, 0, pw, H)), (0, 0))
    frame = base.convert('RGBA')

    # ----- overlays
    if t < 4.0:
        a = eout(seg(t, .15, .5))
        place(frame, T_INTRO, W / 2, 330, a, .9 + .1 * eback(seg(t, .15, .55)))
        a2 = seg(t, 1.3, 1.45)
        if a2 > 0: place(frame, T_CHEAP, W / 2, 1600, a2, 1.0, rot=-4)
        if t > 3.88:  # white flash into the transition
            frame.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * seg(t, 3.88, 4.0)))))
    elif t < 5.0:
        fl = 1 - seg(t, 4.0, 4.18)
        if fl > 0: frame.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * fl))))
        place(frame, T_YOU, W / 2, 760, eout(seg(t, 4.05, 4.3)), .92 + .08 * eout(seg(t, 4.05, 4.35)))
        if t >= 4.5:
            sc = 1.6 - .6 * eout(seg(t, 4.5, 4.62))
            jx = rng.integers(-8, 9) if t < 4.75 else 0
            place(frame, T_THIS, W / 2 + jx, 1040, 1.0, sc)
    elif t < 5.25:  # flash on the impact
        frame.alpha_composite(Image.new('RGBA', (W, H), (255, 220, 170, int(200 * (1 - seg(t, 5.0, 5.25))))))
    if 15.0 <= t < 20.0:
        for (t0, _), spr in zip(WORDS, T_WORDS):
            life = t - t0
            if 0 <= life < 1.05:
                a = eout(seg(life, 0, .15)) * (1 - seg(life, .85, 1.05))
                place(frame, spr, W / 2, 1540, a, .7 + .3 * eback(seg(life, 0, .3)))
    if 20.0 <= t < 25.0:
        a = eout(seg(t, 20.9, 21.3)) * (1 - seg(t, 24.6, 24.95))
        place(frame, T_FUEL, W / 2, 400, a, .9 + .1 * eback(seg(t, 20.9, 21.35)))
    if t >= 25.0:
        place(frame, T_BEF, 270, 300, eout(seg(t, 25.35, 25.6)))
        place(frame, T_AFT, 810, 300, eout(seg(t, 25.35, 25.6)))
        place(frame, T_SAME, W / 2, 1360, eout(seg(t, 25.3, 25.6)), .85 + .15 * eback(seg(t, 25.3, 25.65)))
        place(frame, T_DIFF, W / 2, 1470, eout(seg(t, 25.9, 26.2)), .85 + .15 * eback(seg(t, 25.9, 26.25)))
        place(frame, T_ASK, W / 2, 1640, eout(seg(t, 27.0, 27.3)), .85 + .15 * eback(seg(t, 27.0, 27.35)))
    if t > 29.4:
        frame.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * seg(t, 29.4, 30.0)))))
    enc.stdin.write(frame.convert('RGB').tobytes())
    if f % 150 == 0: print('frame', f, flush=True)
enc.stdin.close(); enc.wait()
print('done')
