"""ONYX X1 — "basic presentation" vs blockbuster trailer (1080x1920, 30 fps, 30 s).
Inputs (cwd): before.png, hero.png, c1..c6.mp4, logo.png, mix.wav, Cinzel.ttf, Outfit.ttf, Comic.ttf
Usage: python3 edit.py out.mp4
"""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 30.0
GOLD = (232, 182, 92)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def eback(x): x = clamp(x); return 1 + 2.6 * (x - 1) ** 3 + 1.6 * (x - 1) ** 2
def rnd(i): v = math.sin(i * 127.1 + 311.7) * 43758.5453; return v - math.floor(v)
def F(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

# ---------- sprites
def text_sprite(lines, f, fill, spacing=0, glow=None, stroke=0, stroke_fill=(0, 0, 0), lh=1.15, gold=False):
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    def width(s): return sum(d0.textbbox((0, 0), ch, font=f)[2] for ch in s) + spacing * (len(s) - 1) if spacing else d0.textbbox((0, 0), s, font=f, stroke_width=stroke)[2]
    ws = [width(l) for l in lines]; size = f.size; pad = 80
    im = Image.new('RGBA', (max(ws) + 2 * pad, int(size * lh * len(lines)) + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = pad + (max(ws) - ws[i]) // 2; y = pad + int(i * size * lh)
        if spacing:
            for ch in l: d.text((x, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill); x += d0.textbbox((0, 0), ch, font=f)[2] + spacing
        else: d.text((x, y), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    if gold:  # metallic vertical gradient through the glyph alpha
        a = im.split()[3]; g = np.zeros((im.height, im.width, 3), np.uint8)
        ys = np.linspace(0, 1, im.height)[:, None]
        band = (ys * len(lines)) % 1
        g[..., 0] = np.clip(255 - 70 * band + 30 * np.exp(-((band - .42) / .05) ** 2), 0, 255)
        g[..., 1] = np.clip(225 - 110 * band + 30 * np.exp(-((band - .42) / .05) ** 2), 0, 255)
        g[..., 2] = np.clip(150 - 120 * band + 40 * np.exp(-((band - .42) / .05) ** 2), 0, 255)
        im = Image.fromarray(g).convert('RGBA'); im.putalpha(a)
    if glow:
        a = im.split()[3].filter(ImageFilter.GaussianBlur(glow[1]))
        gl = Image.new('RGBA', im.size, glow[0] + (0,)); gl.putalpha(a.point(lambda v: min(255, int(v * glow[2]))))
        im = Image.alpha_composite(gl, im)
    return im
def place(frame, spr, cx, cy, alpha=1., scale=1.):
    if alpha <= .01: return
    s = spr if abs(scale - 1) < .003 else spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BICUBIC)
    if alpha < .999: s = s.copy(); s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    frame.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))
def cover(im, w=W, h=H):
    im = im.convert('RGB'); s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))

CINZEL, OUTFIT, COMIC = 'Cinzel.ttf', 'Outfit.ttf', 'Comic.ttf'
chip_f = F(OUTFIT, 50, 500)
def chip(lines):
    d0 = ImageDraw.Draw(Image.new('L', (1, 1))); w = max(d0.textbbox((0, 0), l, font=chip_f)[2] for l in lines) + 90
    im = Image.new('RGBA', (w, 70 * len(lines) + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, im.height - 1), 30, fill=(255, 255, 255, 255))
    for i, l in enumerate(lines): d.text((w // 2, 25 + 70 * i + 35), l, font=chip_f, fill=(17, 17, 17), anchor='mm')
    return im
T_CHIP = chip(['What if instead of presenting', 'your product like this...'])
T_YOU = text_sprite(['...you presented it like'], F(OUTFIT, 74, 300), (240, 240, 240))
T_THIS = text_sprite(['THIS?'], F(CINZEL, 230, 800), (255, 255, 255), gold=True, glow=((255, 170, 60), 30, 1.4))
T_ONYX = text_sprite(['ONYX'], F(CINZEL, 260, 700), (255, 255, 255), spacing=40, gold=True, glow=((255, 160, 50), 40, 1.3))
CARDS = {12.1: text_sprite(['SILENCE', 'THE WORLD.'], F(CINZEL, 100, 700), (255, 255, 255), spacing=14, gold=True, glow=((255, 160, 50), 26, 1.1)),
         19.9: text_sprite(['HEAR', 'EVERYTHING.'], F(CINZEL, 100, 700), (255, 255, 255), spacing=14, gold=True, glow=((255, 160, 50), 26, 1.1))}
SPECS = [(13.4, 'ACTIVE NOISE CANCELLING'), (16.5, 'SPATIAL AUDIO'), (17.7, '40-HOUR BATTERY'), (18.9, 'ZERO-LATENCY MODE')]
T_SPECS = [text_sprite([s], F(OUTFIT, 64, 600), (255, 255, 255), spacing=8, glow=((0, 0, 0), 18, 1.2)) for _, s in SPECS]
T_X1 = text_sprite(['ONYX X1'], F(CINZEL, 150, 700), (255, 255, 255), spacing=22, gold=True, glow=((255, 160, 50), 34, 1.2))
T_TAG = text_sprite(['HEAR THE IMPOSSIBLE.'], F(OUTFIT, 46, 400), (230, 225, 215), spacing=14)
# basic slideshow pieces
sl_title = text_sprite(['ONYX X1 Headphones'], F(COMIC, 92), (26, 79, 214), stroke=3, stroke_fill=(255, 220, 0))
sl_bul = [text_sprite([s], F(COMIC, 62), (20, 20, 20)) for s in ['• Bluetooth', '• Good sound', '• Black color', '• Long battery']]
# LUMARC end card
CT1 = text_sprite(['Want your product', 'to look like this?'], F(OUTFIT, 70, 400), (250, 249, 246), lh=1.25)
CT2 = text_sprite(['@lumarc_studio  ·  slumarc.com'], F(OUTFIT, 42, 400), (166, 166, 184))
def pill(txt):
    f = F(OUTFIT, 48, 500); d0 = ImageDraw.Draw(Image.new('L', (1, 1))); w = d0.textbbox((0, 0), txt, font=f)[2] + 130; h = 124
    g = np.zeros((h, w, 3), np.uint8); xs = np.linspace(0, 1, w)
    for i, (a0, a1) in enumerate([(59, 139), (91, 61), (255, 255)]): g[..., i] = (a0 + (a1 - a0) * xs)[None, :]
    im = Image.fromarray(g).convert('RGBA'); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255); im.putalpha(m)
    ImageDraw.Draw(im).text((w // 2, h // 2), txt, font=f, fill=(255, 255, 255), anchor='mm'); return im
CT_BTN = pill('DM us "VIDEO"')
LOGO = Image.open('logo.png').convert('RGBA'); LOGO = LOGO.resize((700, int(LOGO.height * 700 / LOGO.width)), Image.LANCZOS)

# ---------- grade / fx (numpy)
xs = np.arange(256) / 255.
scurve = np.clip(xs ** 1.08 * 1.04, 0, 1)
LUT_R = np.clip(scurve + .035 * xs ** 2, 0, 1) * 255
LUT_G = np.clip(scurve + .01 * xs ** 2, 0, 1) * 255
LUT_B = np.clip(scurve - .045 * xs ** 2 + .035 * (1 - xs) ** 3, 0, 1) * 255
LUT = np.stack([LUT_R, LUT_G, LUT_B], 1).astype(np.uint8)
def grade(a): return np.stack([LUT[a[..., i], i] for i in range(3)], -1)
rng = np.random.default_rng(5)
NOISE = [np.repeat(np.repeat(rng.normal(0, 9, (H // 2, W // 2, 1)), 2, 0), 2, 1).astype(np.int16) for _ in range(4)]
def grain(a, k, f): return np.clip(a.astype(np.int16) + (NOISE[f % 4] * k).astype(np.int16), 0, 255).astype(np.uint8)
def chroma(a, px):
    if px < 1: return a
    out = a.copy(); out[..., 0] = np.roll(a[..., 0], px, 1); out[..., 2] = np.roll(a[..., 2], -px, 1); return out
def shake(img, amp, i):
    if amp < 1: return img
    z = 1 + amp * 2.2 / W; big = img.resize((int(W * z) + 2, int(H * z) + 2), Image.BILINEAR)
    dx, dy = (rnd(i) - .5) * 2 * amp, (rnd(i + 7) - .5) * 2 * amp
    l, t = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
    return big.crop((int(l), int(t), int(l) + W, int(t) + H))
VIG = None
def vignette(a, k):
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
        VIG = np.clip(1 - .55 * np.clip(r - .45, 0, 1) ** 1.4, 0, 1)[..., None]
    return (a * (1 - k + k * VIG)).astype(np.uint8)

# ---------- clips with speed ramps
class Clip:
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', path, '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.idx, self.cur = -1, None
    def at(self, src_t, fps=24):
        want = int(src_t * fps)
        while self.idx < want:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            self.cur = np.frombuffer(b, np.uint8).reshape(H, W, 3); self.idx += 1
        return self.cur
CL = {k: Clip(f'c{k}.mp4') for k in range(1, 7)}
def ramp_fsf(u, a=.6): return u - a * math.sin(2 * math.pi * u) / (2 * math.pi)  # fast-slow-fast
SEGS = [  # out_start, out_end, clip, src_in, src_out, curve
    (7.6, 12.1, 1, 0.0, 5.0, 'fsf'), (12.9, 15.9, 2, 0.5, 4.8, 'fsf'), (15.9, 19.9, 3, 0.0, 5.0, 'lin'),
    (20.6, 23.6, 4, 0.6, 4.9, 'fsf'), (23.6, 25.8, 5, 0.0, 4.2, 'fsf'), (25.8, 27.4, 6, 0.0, 2.6, 'lin')]
# flip-book frames for the studio-style intro
FLIPS = []
for k in range(1, 7):
    for ss in (.8, 2.2, 3.6):
        r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(ss), '-i', f'c{k}.mp4', '-frames:v', '1', '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
        if len(r.stdout) == W * H * 3: FLIPS.append(np.frombuffer(r.stdout, np.uint8).reshape(H, W, 3))
FLIPS = [FLIPS[i] for i in np.random.default_rng(2).permutation(len(FLIPS))]

before = Image.open('before.png').convert('RGB'); hero = cover(Image.open('hero.png'))
enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', 'mix.wav',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', sys.argv[1]], stdin=subprocess.PIPE)
IMPACTS = [7.6, 9.85, 12.1, 12.9, 15.9, 19.9, 20.6, 23.6, 24.65, 25.8]
_gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(_gl).ellipse((W / 2 - 480, 760 - 480, W / 2 + 480, 760 + 480), fill=(106, 85, 255, 70))
END_GLOW = _gl.filter(ImageFilter.GaussianBlur(150))

for f in range(int(DUR * FPS)):
    t = f / FPS; fx_shake = 0; fx_chroma = 0; flash = 0; bars = 0; grain_k = 0; vig = 0
    if t < 5.0:  # ---------------- basic slideshow
        fr = Image.new('RGBA', (W, H), (255, 255, 255, 255)); d = ImageDraw.Draw(fr)
        d.rectangle((0, 1700, W, H), fill=(26, 79, 214))
        z = 1 + .04 * t / 5; bw = int(820 * z); b = before.resize((bw, bw), Image.BILINEAR)
        wipe = eout(seg(t, .1, .7)); fr.paste(b.crop((0, 0, int(bw * wipe) or 1, bw)), (W // 2 - bw // 2, 560 - (bw - 820) // 2))
        place(fr, sl_title, W / 2, 470, seg(t, .5, .9))
        for i, sp in enumerate(sl_bul): place(fr, sp, 150 + sp.width / 2 + (1 - eout(seg(t, 1.3 + i * .55, 1.7 + i * .55))) * -900, 1440 + i * 70 - 40, 1.0)
        if t > 3.6:  # clip-art starburst
            k = eback(seg(t, 3.6, 3.9)); cx, cy, R = 850, 1350, 150 * k
            pts = [(cx + math.cos(a / 24 * 2 * math.pi) * (R if a % 2 == 0 else R * .72), cy + math.sin(a / 24 * 2 * math.pi) * (R if a % 2 == 0 else R * .72)) for a in range(24)]
            d.polygon(pts, fill=(255, 220, 0), outline=(220, 30, 30)); d.text((cx, cy - 20), 'ONLY', font=F(COMIC, int(40 * k) or 1), fill=(220, 30, 30), anchor='mm'); d.text((cx, cy + 25), '$199!', font=F(COMIC, int(58 * k) or 1), fill=(220, 30, 30), anchor='mm')
        place(fr, T_CHIP, W / 2, 230, eout(seg(t, .15, .5)) * (1 - seg(t, 4.75, 4.95)))
        if t > 4.8:  # tape-stop freeze + desaturate into the cut
            k = seg(t, 4.8, 5.0); a = np.asarray(fr.convert('RGB')).astype(np.float32); g = a.mean(2, keepdims=True)
            a = (a * (1 - k) + g * k) * (1 - .6 * k); fr = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
        out = np.asarray(fr.convert('RGB'))
    elif t < 6.2:  # ---------------- "...you presented it like THIS?"
        fr = Image.new('RGBA', (W, H), (4, 3, 3, 255))
        place(fr, T_YOU, W / 2, 820, eout(seg(t, 5.15, 5.45)))
        if t >= 5.75:
            k = seg(t, 5.75, 5.9); place(fr, T_THIS, W / 2, 1050, 1, 1.9 - .9 * eout(k))
            fx_shake = 26 * math.exp(-(t - 5.75) * 7); fx_chroma = int(14 * math.exp(-(t - 5.75) * 8)); flash = .8 * math.exp(-(t - 5.75) * 14)
        out = np.asarray(fr.convert('RGB'))
    elif t < 7.6:  # ---------------- flip-book studio intro -> ONYX
        if t < 6.95:
            i = int((t - 6.2) * 30 / 2); a = FLIPS[i % len(FLIPS)].astype(np.float32)
            lum = a.mean(2, keepdims=True); a = lum * np.array([1.05, .8, .45]) * 1.25 + a * .15
            out = np.clip(a, 0, 255).astype(np.uint8); fx_chroma = 4
        else:
            fr = Image.new('RGBA', (W, H), (6, 4, 2, 255)); k = seg(t, 6.95, 7.25)
            place(fr, T_ONYX, W / 2, H / 2, eout(k), 1.25 - .25 * eout(k))
            out = np.asarray(fr.convert('RGB')); flash = .7 * math.exp(-(t - 6.95) * 10)
        grain_k = .8
    elif t < 27.4:  # ---------------- the trailer
        sg = [s for s in SEGS if s[0] <= t < s[1]]
        if sg:
            s0, s1, c, a0, a1, cur = sg[0]; u = (t - s0) / (s1 - s0)
            src = a0 + (a1 - a0) * (ramp_fsf(u) if cur == 'fsf' else u)
            out = grade(CL[c].at(src))
        else:  # title cards
            ct = 12.1 if t < 13 else 19.9
            fr = Image.new('RGBA', (W, H), (5, 4, 3, 255)); k = seg(t, ct, ct + .18)
            place(fr, CARDS[ct], W / 2, H / 2, eout(k), 1.3 - .3 * eout(k))
            d = ImageDraw.Draw(fr); sw = int(900 * eout(seg(t, ct + .05, ct + .4)))  # anamorphic streak
            for yy, aa in ((H // 2, 140), (H // 2 + 2, 80)): d.line((W // 2 - sw, yy, W // 2 + sw, yy), fill=(255, 190, 110, aa), width=3)
            out = np.asarray(fr.convert('RGB'))
        bars = eout(seg(t, 7.6, 8.0)); grain_k = 1; vig = .9
        for t0, s in zip([x[0] for x in SPECS], T_SPECS):
            life = t - t0
            if 0 <= life < .95:
                fr = Image.fromarray(out).convert('RGBA'); place(fr, s, W / 2 + (1 - eout(seg(life, 0, .2))) * 60, 1540, eout(seg(life, 0, .12)) * (1 - seg(life, .75, .95)))
                ImageDraw.Draw(fr).line((W / 2 - 200 * eout(seg(life, .05, .35)), 1590, W / 2 + 200 * eout(seg(life, .05, .35)), 1590), fill=GOLD + (230,), width=3)
                out = np.asarray(fr.convert('RGB'))
        if 25.8 <= t < 27.4:  # product title over the final hero shot
            fr = Image.fromarray(out).convert('RGBA'); k = seg(t, 26.0, 26.3)
            place(fr, T_X1, W / 2, 1420, eout(k), 1.2 - .2 * eout(k)); place(fr, T_TAG, W / 2, 1545, eout(seg(t, 26.4, 26.8)))
            out = np.asarray(fr.convert('RGB'))
        for it in IMPACTS:
            if 0 <= t - it < .5:
                e = math.exp(-(t - it) * 9); fx_shake = max(fx_shake, 18 * e); fx_chroma = max(fx_chroma, int(10 * e)); flash = max(flash, .55 * math.exp(-(t - it) * 16))
        if 24.65 <= t < 25.2: flash = max(flash, .9 * math.exp(-(t - 24.65) * 8))
    else:  # ---------------- LUMARC end card (brand colors)
        lt = t - 27.4; fr = Image.new('RGBA', (W, H), (14, 14, 20, 255))
        if lt < .3: fr = Image.blend(Image.fromarray(grade(CL[6].at(2.6))).convert('RGBA'), fr, eout(lt / .3))
        fr.alpha_composite(END_GLOW)
        place(fr, LOGO, W / 2, 720, eout(seg(lt, .15, .6)), .9 + .1 * eout(seg(lt, .15, .6)))
        place(fr, CT1, W / 2, 1010, eout(seg(lt, .45, .8)))
        place(fr, CT_BTN, W / 2, 1230, eout(seg(lt, .8, 1.1)), (.85 + .15 * eback(seg(lt, .8, 1.15))) * (1 + .03 * max(0, math.sin(lt * 5))))
        place(fr, CT2, W / 2, 1400, eout(seg(lt, 1.1, 1.4)))
        out = np.asarray(fr.convert('RGB')); flash = .6 * math.exp(-lt * 7)
    # ---------- post
    if fx_chroma: out = chroma(out, fx_chroma)
    if grain_k: out = grain(out, grain_k, f)
    if vig: out = vignette(out.astype(np.float32), vig)
    img = Image.fromarray(out)
    if fx_shake: img = shake(img, fx_shake, f)
    if bars > 0:
        d = ImageDraw.Draw(img); bh = int(120 * bars); d.rectangle((0, 0, W, bh), fill=(0, 0, 0)); d.rectangle((0, H - bh, W, H), fill=(0, 0, 0))
    if flash > .01:
        img = Image.blend(img, Image.new('RGB', (W, H), (255, 236, 205)), min(1, flash))
    enc.stdin.write(img.tobytes())
    if f % 150 == 0: print('frame', f, flush=True)
enc.stdin.close(); enc.wait(); print('done')
