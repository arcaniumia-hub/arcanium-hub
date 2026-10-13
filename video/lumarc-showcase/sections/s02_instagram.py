"""s02 — INSTAGRAM (6.04–9.32): "Your customers do the exact same thing with your Instagram."

  6.04  the countdown hits 0.00: flash + glitch + RGB split, tight on his face (TL[2] jump cut lands on the hit).
  6.07  CAMERA PULL-BACK REVEAL: the shot shrinks into a phone screen — it was a Reel all along. The phone floats in a
        deep purple space with blurred phones/posts at depth (parallax), the Reels UI slides in (rail, handle, caption,
        progress bar). 3-D tilt via a real homography.
  7.32  "EXACT": the phone swings in 3-D, a specular light sweep crosses the glass.
  7.70  "SAME THING": a finger (hairline touch ring, press-scale + release ripple) starts to swipe the Reel away (rubber-band reveals the next Reel) — and lets it snap back.
  8.70  "INSTAGRAM": double-tap heart pops on screen, the rail heart fills red with a spark burst, counters roll,
        floating hearts stream up — the UI comes alive. Phone settles centre, frontal, by 9.2 (handoff to s03).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

START, END = E.span(2, 2)
T0 = START                                   # 6.04
T_PULL, T_EXACT, T_SAME, T_REL, T_INSTA = 6.07, 7.32, 7.70, 8.00, 8.70
PW_END, CY_END = 618, 768            # settled phone: y ~ 135..1400 -> captions (cap_y 1536) live below it, bottom glyph <= 1630
T_UI_TOP, T_UI_BOT = 6.42, 6.84

CUES = [(T0, 'impact', {}), (T0, 'glitch', {}), (T_PULL, 'whoosh', {}),
        (6.55, 'swoosh_up', {}),
        (T_EXACT, 'glass', {}),
        (T_SAME + .03, 'swipe', {}), (T_REL + .05, 'click', {}),
        (T_INSTA, 'heart', {}), (T_INSTA + .02, 'pop', {}), (T_INSTA + .30, 'shimmer', {})]

W, H = E.W, E.H
clamp, eout = E.clamp, E.eout
def lerp(a, b, k): return a + (b - a) * k
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def qio(x): x = clamp(x); return 8 * x ** 4 if x < .5 else 1 - (-2 * x + 2) ** 4 / 2
def expo(x): x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0
def spring(x, k=7.0, damp=5.0):
    """0 -> 1 with a damped overshoot (x in seconds-ish units)."""
    if x <= 0: return 0.0
    return 1 - math.exp(-damp * x) * math.cos(k * x)

# ---------------------------------------------------------------- canonical phone
SW, SH = 902, 1920                 # screen = centre crop of the 1080x1920 frame (19.5:9 phones crop 9:16 sides)
BEZ = 34; MARG = 10
PW0, PH0 = SW + 2 * BEZ, SH + 2 * BEZ          # 970 x 1988 body
CW, CH = PW0 + 2 * MARG, PH0 + 2 * MARG        # canvas with room for side buttons
R_BODY, R_SCR = 150, 118

def _mask(w, h, r, ss=3):
    m = Image.new('L', (w * ss, h * ss)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def body():
    def mk():
        im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        # side buttons
        for (x0, y0, x1, y1) in [(2, 380, MARG + 4, 470), (2, 520, MARG + 4, 660), (2, 690, MARG + 4, 830), (CW - MARG - 4, 560, CW - 2, 780)]:
            d.rounded_rectangle((x0, y0, x1, y1), 4, fill=(70, 70, 86, 255))
        m = _mask(PW0, PH0, R_BODY)
        # titanium frame: lavender rim light top-left -> dark bottom-right
        yy, xx = np.mgrid[0:PH0, 0:PW0].astype(np.float32)
        u = np.clip((xx / PW0) * .4 + (yy / PH0) * .6, 0, 1)
        c0, c1 = np.array([190, 180, 235], np.float32), np.array([40, 38, 56], np.float32)
        rim = (c0 + (c1 - c0) * u[..., None] ** .6)
        fr = Image.fromarray(rim.astype(np.uint8)).convert('RGBA'); fr.putalpha(m)
        im.alpha_composite(fr, (MARG, MARG))
        inner = _mask(PW0 - 8, PH0 - 8, R_BODY - 4)
        blk = Image.new('RGBA', (PW0 - 8, PH0 - 8), (10, 10, 14, 255)); blk.putalpha(inner)
        im.alpha_composite(blk, (MARG + 4, MARG + 4))
        return im
    return E.cached('b_body', mk)

def scr_mask(): return E.cached('b_smask', lambda: _mask(SW, SH, R_SCR))
def island():
    def mk():
        w, h = 250, 72; im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); im.putalpha(_mask(w, h, h // 2))
        bl = Image.new('RGBA', (w, h), (0, 0, 0, 255)); bl.putalpha(_mask(w, h, h // 2)); return bl
    return E.cached('b_island', mk)

# ---------------------------------------------------------------- Reels UI (canonical screen coords)
WHITE = (250, 249, 246)
def _heart_poly(cx, cy, s, n=80):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = 16 * math.sin(a) ** 3; y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s, cy + y * s))
    return pts

def heart_img(size, fill=None, outline=WHITE, width=5, ss=3):
    def mk():
        S = int(size * 1.3) * ss; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = _heart_poly(S / 2, S / 2 + S * .02, size * ss / 34.)
        if fill: d.polygon(pts, fill=fill + (255,))
        if outline: d.line(pts + [pts[0]], fill=outline + (255,), width=width * ss, joint='curve')
        return im.resize((S // ss, S // ss), Image.LANCZOS)
    return E.cached(('b_heart', size, fill, outline, width), mk)

def grad_heart(size):
    def mk():
        h = heart_img(size, fill=(255, 255, 255), outline=None)
        g = E.gradient(h.width, h.height, [(255, 120, 170), (255, 48, 96), (200, 60, 255)]).convert('RGBA'); g.putalpha(h.getchannel('A'))
        return g
    return E.cached(('b_gheart', size), mk)

def icon_comment(size=64, ss=3):
    def mk():
        S = size * ss; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = 5 * ss; p = 5 * ss
        d.ellipse((p, p, S - p, S - p), outline=WHITE + (255,), width=w)
        d.polygon([(p + 2 * ss, S - p - 2 * ss), (p + 18 * ss, S - p - 10 * ss), (p + 10 * ss, S - p - 20 * ss)], fill=WHITE + (255,))
        return im.resize((size, size), Image.LANCZOS)
    return E.cached('b_icom', mk)

def icon_share(size=64, ss=3):
    def mk():
        S = size * ss; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = 5 * ss
        a, b, c = (6 * ss, 10 * ss), (S - 6 * ss, 8 * ss), (S * .45, S - 6 * ss)
        d.line([a, b, c, (S * .38, S * .45), a], fill=WHITE + (255,), width=w, joint='curve')
        d.line([(S * .38, S * .45), b], fill=WHITE + (255,), width=w)
        return im.resize((size, size), Image.LANCZOS)
    return E.cached('b_ishare', mk)

def icon_save(size=64, ss=3):
    def mk():
        S = size * ss; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = 5 * ss
        x0, x1, y0, y1 = 12 * ss, S - 12 * ss, 6 * ss, S - 6 * ss
        d.line([(x0, y1), (x0, y0), (x1, y0), (x1, y1), (S / 2, y1 - 16 * ss), (x0, y1)], fill=WHITE + (255,), width=w, joint='curve')
        return im.resize((size, size), Image.LANCZOS)
    return E.cached('b_isave', mk)

def label(s, size, wght=600, col=WHITE, shadow=True):
    def mk():
        f = E.font(size, wght); l, t, r, b = f.getbbox(s); pad = 12
        im = Image.new('RGBA', (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
        if shadow:
            sh = Image.new('L', im.size); ImageDraw.Draw(sh).text((pad - l, pad - t), s, font=f, fill=200)
            sim = Image.new('RGBA', im.size, (0, 0, 0, 0)); sim.putalpha(sh.filter(ImageFilter.GaussianBlur(4))); im.alpha_composite(sim, (0, 2))
        ImageDraw.Draw(im).text((pad - l, pad - t), s, font=f, fill=col + (255,))
        return im
    return E.cached(('b_lab', s, size, wght, col, shadow), mk)

RAIL_X = 834
Y_HEART, Y_COM, Y_SHARE, Y_SAVE, Y_DISC = 1150, 1300, 1440, 1570, 1715

def _shade(top_side):
    a = np.zeros(SH, np.float32)
    if top_side: a[:300] = np.clip(1 - np.linspace(0, 1, 300), 0, 1) ** 1.6 * .55
    else: a[SH - 760:] = np.clip(np.linspace(0, 1, 760), 0, 1) ** 1.7 * .78
    sh = Image.new('RGBA', (SW, SH), (4, 3, 10, 0)); sh.putalpha(Image.fromarray((np.repeat(a[:, None], SW, 1) * 255).astype(np.uint8)))
    return sh

def ui_top():
    """top shade + status bar + 'Reels' header."""
    def mk():
        im = Image.new('RGBA', (SW, SH), (0, 0, 0, 0)); im.alpha_composite(_shade(True))
        d = ImageDraw.Draw(im)
        im.alpha_composite(label('9:41', 36, 600), (54, 22))
        # battery + signal
        d.rounded_rectangle((SW - 120, 42, SW - 66, 66), 7, outline=WHITE + (230,), width=3); d.rectangle((SW - 115, 47, SW - 80, 61), fill=WHITE + (255,))
        for i in range(4): d.rounded_rectangle((SW - 200 + i * 14, 62 - 6 - i * 5, SW - 192 + i * 14, 66), 2, fill=WHITE + (255,))
        im.alpha_composite(label('Reels', 54, 700), (34, 118))
        # camera icon
        d.rounded_rectangle((SW - 112, 136, SW - 50, 182), 12, outline=WHITE + (255,), width=5); d.ellipse((SW - 94, 146, SW - 68, 172), outline=WHITE + (255,), width=4)
        return im
    return E.cached('b_ui_top', mk)

def ui_bottom():
    """bottom shade + account block + caption + audio line."""
    def mk():
        im = Image.new('RGBA', (SW, SH), (0, 0, 0, 0)); im.alpha_composite(_shade(False))
        d = ImageDraw.Draw(im)
        # account block
        av = E.gradient(84, 84, E.GRAD).convert('RGBA'); av.putalpha(_mask(84, 84, 42))
        lg = E.logo(60); av.alpha_composite(lg, (42 - lg.width // 2, 42 - lg.height // 2)) if lg.width < 84 else None
        ring = Image.new('RGBA', (96, 96), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 95, 95), outline=WHITE + (255,), width=3)
        im.alpha_composite(ring, (34, 1596)); im.alpha_composite(av, (40, 1602))
        hl = label('lumarc_studio', 38, 700); im.alpha_composite(hl, (140, 1612))
        fw = label('Follow', 32, 600); fx = 140 + hl.width + 8
        d.rounded_rectangle((fx, 1614, fx + fw.width + 14, 1614 + fw.height + 2), 14, outline=WHITE + (220,), width=3)
        im.alpha_composite(fw, (fx + 7, 1615))
        im.alpha_composite(label('Your page is their first impression.', 32, 500, (232, 230, 242)), (30, 1712))
        # audio line: little note + text
        nd = 44; d.ellipse((nd, 1790, nd + 16, 1804), fill=WHITE + (255,)); d.line((nd + 14, 1796, nd + 14, 1768), fill=WHITE + (255,), width=4)
        d.line((nd + 14, 1768, nd + 26, 1774), fill=WHITE + (255,), width=4)
        im.alpha_composite(label('lumarc_studio  ·  Original audio', 30, 500, (225, 222, 238)), (nd + 30, 1766))
        return im
    return E.cached('b_ui_bot', mk)

def rail(alpha_slide, t):
    """right rail (icons + counts) as one RGBA strip; the heart is drawn separately (animated)."""
    def mk():
        im = Image.new('RGBA', (180, SH), (0, 0, 0, 0)); cx = 90
        for ic, y, txt in [(icon_comment(), Y_COM, '1,204'), (icon_share(), Y_SHARE, '3,912'), (icon_save(), Y_SAVE, '')]:
            im.alpha_composite(ic, (cx - ic.width // 2, y - ic.height // 2))
            if txt:
                l = label(txt, 28, 600); im.alpha_composite(l, (cx - l.width // 2, y + 36))
        d = ImageDraw.Draw(im)
        for i in range(3): d.ellipse((cx - 22 + i * 18, Y_SAVE + 75 - 4, cx - 14 + i * 18, Y_SAVE + 75 + 4), fill=WHITE + (255,))
        disc = E.gradient(70, 70, E.GRAD).convert('RGBA'); disc.putalpha(_mask(70, 70, 16))
        ImageDraw.Draw(disc).rounded_rectangle((0, 0, 69, 69), 16, outline=WHITE + (255,), width=4)
        im.alpha_composite(disc, (cx - 35, Y_DISC - 35))
        return im
    return E.cached('b_rail', mk)

def fmt_k(v): return f'{v / 1000:.1f}K'

# ---------------------------------------------------------------- background space
def space_bg():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        base = np.array([12, 10, 20], np.float32)
        def glow(cx, cy, rx, ry, col, a):
            g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)); return g[..., None] * np.array(col, np.float32) * a
        img = base + glow(540, 800, 520, 700, (106, 85, 255), .42) + glow(880, 300, 380, 380, (154, 77, 255), .22) \
            + glow(150, 1400, 420, 380, (79, 107, 255), .18)
        img = img * (1 - .55 * np.clip(((xx - 540) / 900) ** 2 + ((yy - 860) / 1300) ** 2, 0, 1))[..., None]
        # bokeh dust
        rng = np.random.default_rng(7); im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
        dust = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(dust)
        for _ in range(70):
            x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 9)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 190, 255, int(rng.uniform(20, 90))))
        im.alpha_composite(dust.filter(ImageFilter.GaussianBlur(2.5)))
        return im.convert('RGB')
    return E.cached('b_space', mk)

def _mini_phone(content, w):
    h = int(w * PH0 / PW0); im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    m = _mask(w, h, int(R_BODY * w / PW0)); b = Image.new('RGBA', (w, h), (36, 34, 50, 255)); b.putalpha(m); im.alpha_composite(b)
    bz = int(BEZ * w / PW0); sw, sh = w - 2 * bz, h - 2 * bz
    c = content.convert('RGB'); sc = max(sw / c.width, sh / c.height)
    c = c.resize((int(c.width * sc) + 1, int(c.height * sc) + 1), Image.LANCZOS)
    c = c.crop(((c.width - sw) // 2, (c.height - sh) // 2, (c.width - sw) // 2 + sw, (c.height - sh) // 2 + sh)).convert('RGBA')
    c.putalpha(_mask(sw, sh, int(R_SCR * w / PW0))); im.alpha_composite(c, (bz, bz)); return im

def depth_sprites():
    """blurred phones / posts floating at depth: (sprite, cx, cy, depth)."""
    def mk():
        out = []
        for name, kind, w, cx, cy, rot, blur, dim, depth in [
                ('close_food', 'phone', 360, 96, 640, 9, 8, .34, .55),
                ('close_service', 'phone', 330, 1000, 1180, -8, 9, .32, .5),
                ('carousel_1', 'post', 300, 930, 330, -6, 12, .26, .35),
                ('design_post', 'post', 280, 150, 1560, 7, 13, .2, .3),
                ('close_skill', 'phone', 240, 1010, 1720, 12, 15, .2, .25)]:
            img = E.asset(name)
            if kind == 'phone': sp = _mini_phone(img, w)
            else:
                c = img.resize((w, int(img.height * w / img.width)), Image.LANCZOS).convert('RGBA'); c.putalpha(_mask(c.width, c.height, 18)); sp = c
            sp = Image.eval(sp.convert('RGB'), lambda v: int(v * dim)).convert('RGBA'); sp.putalpha(_alpha_of(name, kind, w))
            sp = sp.rotate(rot, Image.BICUBIC, expand=True)
            pad = blur * 3; big = Image.new('RGBA', (sp.width + 2 * pad, sp.height + 2 * pad), (0, 0, 0, 0)); big.alpha_composite(sp, (pad, pad))
            out.append((big.filter(ImageFilter.GaussianBlur(blur)), cx, cy, depth))
        return out
    return E.cached('b_depth', mk)

def _alpha_of(name, kind, w):
    img = E.asset(name)
    if kind == 'phone':
        h = int(w * PH0 / PW0); return _mask(w, h, int(R_BODY * w / PW0))
    h = int(img.height * w / img.width); return _mask(w, h, 18)

def glow_sprite():
    def mk():
        im = Image.new('RGBA', (300, 560), (0, 0, 0, 0)); m = Image.new('L', (300, 560))
        ImageDraw.Draw(m).rounded_rectangle((60, 60, 240, 500), 40, fill=255)
        g = Image.new('RGBA', im.size, (120, 90, 255, 0)); g.putalpha(m.filter(ImageFilter.GaussianBlur(34))); return g
    return E.cached('b_glow', mk)

def shadow_sprite():
    def mk():
        im = Image.new('RGBA', (300, 560), (0, 0, 0, 0)); m = Image.new('L', (300, 560))
        ImageDraw.Draw(m).rounded_rectangle((70, 70, 230, 490), 40, fill=255)
        g = Image.new('RGBA', im.size, (0, 0, 6, 0)); g.putalpha(m.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * .8))); return g
    return E.cached('b_shadow', mk)

def next_reel():
    def mk():
        img = E.asset('close_skill'); sc = max(SW / img.width, SH / img.height)
        c = img.resize((int(img.width * sc) + 1, int(img.height * sc) + 1), Image.LANCZOS)
        return c.crop(((c.width - SW) // 2, 0, (c.width - SW) // 2 + SW, SH)).convert('RGBA')
    return E.cached('b_next', mk)

# ---------------------------------------------------------------- 3-D projection
def homography(src, dst):
    """coeffs for PIL PERSPECTIVE mapping output (dst) -> input (src)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()

def project(w, h, cx, cy, s, rx, ry, rz, f=2600.):
    rx, ry, rz = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    R = Rz @ Ry @ Rx; pts = []
    for x, y in [(0, 0), (w, 0), (w, h), (0, h)]:
        X, Y, Z = R @ np.array([(x - w / 2) * s, (y - h / 2) * s, 0.])
        k = f / (f + Z); pts.append((cx + X * k, cy + Y * k))
    return pts

# ---------------------------------------------------------------- motion
def phone_state(t):
    lt = t - T0
    p = eio((t - T_PULL) / .80)                     # the pull-back
    pw = lerp(1172, PW_END, p)
    cx = 540; cy = lerp(960, CY_END, p)
    ry = lerp(0, -9, p)
    ry += -12 * math.sin(math.pi * clamp((t - T_PULL) / .80))         # swing during the pull
    rx = lerp(0, 5, p); rz = lerp(0, -2.2, p)
    # float
    fl = clamp((t - 7.0) / .4)
    cy += fl * 7 * math.sin((t - 7.0) * 2.4); ry += fl * 1.4 * math.sin((t - 7.0) * 1.7)
    # EXACT: 3-D swing
    if t > T_EXACT - .04:
        e = t - (T_EXACT - .04)
        ry += 24 * math.sin(math.pi * eio(e / 1.0)) * (1 if e < 1.0 else 0)
        rx += -3 * math.sin(math.pi * eio(e / 1.0)) * (1 if e < 1.0 else 0)
    # INSTAGRAM: punch + settle frontal & centred
    if t > T_INSTA - .1:
        k = eio((t - (T_INSTA - .1)) / .6)
        ry = lerp(ry, 0, k); rx = lerp(rx, 1.5, k); rz = lerp(rz, 0, k); cx = 540
        pw *= 1 + .045 * math.exp(-max(0, t - T_INSTA) / .12) * (1 if t > T_INSTA else 0)
    return dict(pw=pw, cx=cx, cy=cy, rx=rx, ry=ry, rz=rz, p=p)

def scroll_offset(t):
    if t < T_SAME: return 0.0, 0.0
    if t < T_REL:
        k = eout((t - T_SAME) / (T_REL - T_SAME)); return 330 * k, k
    k = spring((t - T_REL) * 1.25, 8, 5.5)
    return 330 * (1 - k), max(0, 1 - (t - T_REL) / .2)

# ---------------------------------------------------------------- frame
def draw(ctx, lt, t):
    P = ctx.post
    # the hit
    P['flash'] = 0.0                                   # the hit is LIGHT (light_hit in _wrap), not a grey mix
    P['glitch'] = 1.0 * math.exp(-lt / .10) if lt < .4 else 0
    P['rgb'] = 20 * math.exp(-lt / .09) if lt < .3 else 0
    if lt < .1: P['zoom_blur'] = .5 * (1 - lt / .1)
    st = phone_state(t)
    # inner camera: tight -> normal Reel framing during the pull
    k = st['p']
    ctx.cam.update(z=lerp(1.42, 1.08, k), x=518, y=lerp(720, 800, k), dx=22 * (1 - k), dy=lerp(40, 0, k))
    ctx.captions = True
    ctx.cap_y = 1536; ctx.cap_size = 84
    ctx.wrap = lambda fr: _wrap(fr, t, st)

def _wrap(fr, t, st):
    lt = t - T0
    # ---- screen content
    scr = fr.crop(((W - SW) // 2, 0, (W - SW) // 2 + SW, SH))
    off, touch_k = scroll_offset(t)
    if off > .5:
        s2 = next_reel().copy(); s2 = s2.crop((0, 0, SW, SH))
        canvas = Image.new('RGBA', (SW, SH), (0, 0, 0, 255))
        canvas.alpha_composite(s2.crop((0, 0, SW, int(off) + 2)), (0, SH - int(off)))
        canvas.alpha_composite(scr.crop((0, int(off), SW, SH)), (0, 0)); scr = canvas
    ut = clamp((t - T_UI_TOP) / .3)
    if ut > 0: scr.alpha_composite(_fade(ui_top(), ut) if ut < 1 else ui_top())
    ui_a = clamp((t - T_UI_BOT) / .3)
    if ui_a > 0:
        ub = ui_bottom(); rise = (1 - eout((t - T_UI_BOT) / .4)) * 40
        scr.alpha_composite(_fade(ub, ui_a) if ui_a < 1 else ub, (0, int(rise)))
        # rail slides in from the right edge
        sl = (1 - eout((t - T_UI_BOT) / .45)) * 160
        rl = rail(1, t); scr.alpha_composite(_fade(rl, ui_a) if ui_a < 1 else rl, (int(RAIL_X - 90 + sl), 0))
        _heart_ui(scr, t, ui_a, sl)
        # progress bar
        pg = clamp((t - 6.2) / 9.0) * .9 + .06
        d = ImageDraw.Draw(scr)
        d.rectangle((0, SH - 8, SW, SH), fill=(255, 255, 255, int(70 * ui_a)))
        d.rectangle((0, SH - 8, int(SW * pg), SH), fill=(255, 255, 255, int(235 * ui_a)))
    _double_tap(scr, t)
    _touch(scr, t, off)
    # ---- assemble the canonical phone
    ph = body().copy()
    ph.paste(scr.convert('RGB'), (MARG + BEZ, MARG + BEZ), scr_mask())
    isl = island(); ph.alpha_composite(isl, (CW // 2 - isl.width // 2, MARG + BEZ + 22))
    # specular sweep across the glass on "EXACT" (plus a faint one when the pull settles)
    for (ta, dur, amp) in [(T_EXACT - .02, .5, .32), (6.62, .55, .16)]:
        sp = (t - ta) / dur
        if 0 < sp < 1: _sheen(ph, sp, amp)
    # ---- project into the frame
    s = st['pw'] / PW0
    dst = project(CW, CH, st['cx'], st['cy'], s, st['rx'], st['ry'], st['rz'])
    co = homography([(0, 0), (CW, 0), (CW, CH), (0, CH)], dst)
    out = space_bg().copy().convert('RGBA') if st['pw'] < 1150 else Image.new('RGBA', (W, H), (12, 10, 20, 255))
    if st['pw'] < 1150:
        rev = st['p']
        for sp_, x, y, depth in depth_sprites():
            # depth: farther things move/scale less during the pull (parallax)
            zs = lerp(1 + 1.6 * depth, 1.0, rev)
            sx = W / 2 + (x - W / 2) * zs + st['ry'] * 6 * depth; sy = st['cy'] - 822 + 822 + (y - 822) * zs
            im = sp_ if abs(zs - 1) < .01 else sp_.resize((int(sp_.width * zs), int(sp_.height * zs)), Image.BILINEAR)
            _paste_c(out, im, sx, sy + 10 * math.sin(t * 1.3 + x), clamp(rev * 1.6))
        xs = [p[0] for p in dst]; ys = [p[1] for p in dst]
        bw, bh = max(xs) - min(xs), max(ys) - min(ys)
        g = glow_sprite().resize((int(bw * 1.9), int(bh * 1.35)), Image.BILINEAR)
        _paste_c(out, g, (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, .85 * clamp(rev * 1.5))
        shd = shadow_sprite().resize((int(bw * 1.5), int(bh * 1.25)), Image.BILINEAR)
        _paste_c(out, shd, (min(xs) + max(xs)) / 2 + 30, (min(ys) + max(ys)) / 2 + 60, clamp(rev * 1.5))
    phw = ph.transform((W, H), Image.PERSPECTIVE, co, Image.BICUBIC)
    out.alpha_composite(phw)
    _floating_hearts(out, t, dst)
    k = .5 * math.exp(-lt / .04)
    return light_hit(out, k) if k > .01 else out

def _fade(img, a): return E.fade(img, a)
def _paste_c(base, im, cx, cy, a=1.0):
    if a <= .01: return
    if a < 1: im = E.fade(im, a)
    E._paste(base, dict(img=im, xy=(int(cx - im.width / 2), int(cy - im.height / 2)), glass=0))

def _sheen(ph, sp, amp):
    def mk():
        yy, xx = np.mgrid[0:CH // 4, 0:CW // 4].astype(np.float32)
        return (xx / (CW / 4)) * .75 + (yy / (CH / 4)) * .45
    u = E.cached('b_sheen_u', mk)
    c = lerp(-.3, 1.5, eio(sp))
    band = np.exp(-((u - c) / .09) ** 2) * amp + np.exp(-((u - c + .16) / .025) ** 2) * amp * .6
    a = Image.fromarray((np.clip(band, 0, 1) * 255).astype(np.uint8)).resize((CW, CH), Image.BILINEAR)
    from PIL import ImageChops
    a = ImageChops.multiply(a, ph.getchannel('A'))
    hl = Image.new('RGBA', (CW, CH), (255, 255, 255, 0)); hl.putalpha(a); ph.alpha_composite(hl)

def touch_ring(ss=4):
    """soft touch indicator: hairline white ring (70%) + faint fill (15%) + whisper of shadow."""
    def mk():
        S, r, w = 200, 66, 5
        m = Image.new('L', (S * ss, S * ss)); d = ImageDraw.Draw(m)
        d.ellipse(((S / 2 - r) * ss, (S / 2 - r) * ss, (S / 2 + r) * ss, (S / 2 + r) * ss), fill=38)
        d.ellipse(((S / 2 - r) * ss, (S / 2 - r) * ss, (S / 2 + r) * ss, (S / 2 + r) * ss), outline=178, width=w * ss)
        m = m.resize((S, S), Image.LANCZOS)
        im = Image.new('RGBA', (S, S), (255, 255, 255, 0)); im.putalpha(m)
        sh = Image.new('RGBA', (S, S), (0, 0, 10, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .35)))
        out = Image.new('RGBA', (S, S), (0, 0, 0, 0)); out.alpha_composite(sh, (0, 3)); out.alpha_composite(im); return out
    return E.cached('b_touch2', mk)

def ripple_ring(ss=4):
    def mk():
        S, r = 200, 90; m = Image.new('L', (S * ss, S * ss))
        ImageDraw.Draw(m).ellipse(((S / 2 - r) * ss, (S / 2 - r) * ss, (S / 2 + r) * ss, (S / 2 + r) * ss), outline=200, width=3 * ss)
        im = Image.new('RGBA', (S, S), (255, 255, 255, 0)); im.putalpha(m.resize((S, S), Image.LANCZOS)); return im
    return E.cached('b_ripple', mk)

TX, TY0 = SW / 2 + 60, SH - 520
def _touch(scr, t, off):
    """finger lands (.12 s before SAME), presses (1 -> .85), drags the Reel up, lifts on release with a ripple."""
    if t < T_SAME - .12 or t > T_REL + .45: return
    y_rel = TY0 - 330 * .95
    if t < T_REL:
        a = clamp((t - (T_SAME - .12)) / .07)
        s = 1 - .15 * eout((t - (T_SAME - .04)) / .1)
        y = TY0 - off * .95
    else:
        e = t - T_REL; a = 1 - clamp(e / .18); s = .85 + .15 * eout(e / .12); y = y_rel
        rp = clamp(e / .4)
        if rp < 1:
            rr = ripple_ring(); k = .5 + 1.1 * eout(rp)
            ri = rr.resize((int(rr.width * k), int(rr.height * k)), Image.BILINEAR)
            scr.alpha_composite(_fade(ri, .75 * (1 - rp) ** 1.5), (int(TX - ri.width / 2), int(y - ri.height / 2)))
    if a <= .01: return
    tc = touch_ring(); ti = tc.resize((int(tc.width * s), int(tc.height * s)), Image.BILINEAR) if abs(s - 1) > .005 else tc
    scr.alpha_composite(_fade(ti, a) if a < 1 else ti, (int(TX - ti.width / 2), int(y - ti.height / 2)))

def light_hit(fr, k, col=(196, 182, 255)):
    """a flash that reads as LIGHT, not fog: exposure push + highlight bloom + faint violet lift, filmic shoulder."""
    rgb = fr.convert('RGB'); a = np.asarray(rgb, np.float32)
    sm = np.asarray(rgb.resize((W // 4, H // 4), Image.BILINEAR), np.float32)
    lum = sm.mean(2, keepdims=True); hb = sm * np.clip((lum - 80) / 110, 0, 1)
    bloom = np.asarray(Image.fromarray(hb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32)
    y = (a * (1 + 1.7 * k) + bloom * (2.4 * k) + np.array(col, np.float32) * (.20 * k)) / 255.
    y = np.where(y < .72, y, .72 + .28 * (1 - np.exp(-(y - .72) / .28)))
    return Image.fromarray(np.clip(y * 255, 0, 255).astype(np.uint8)).convert('RGBA')

def _heart_ui(scr, t, a, sl):
    x = RAIL_X + sl
    if t < T_INSTA:
        h = heart_img(64); likes = 48200
        scr.alpha_composite(_fade(h, a), (int(x - h.width / 2), int(Y_HEART - h.height / 2)))
    else:
        e = t - T_INSTA
        s = 1 + .55 * math.sin(min(e / .28, 1) * math.pi) * math.exp(-e * 2)
        h = heart_img(64, fill=(255, 48, 80), outline=(255, 48, 80))
        hs = h.resize((int(h.width * s), int(h.height * s)), Image.BILINEAR)
        scr.alpha_composite(hs, (int(x - hs.width / 2), int(Y_HEART - hs.height / 2)))
        # spark burst
        if e < .45:
            d = ImageDraw.Draw(scr); k = eout(e / .45)
            for i in range(8):
                ang = i * math.pi / 4 + .2; r0, r1 = 50 + 40 * k, 62 + 66 * k
                col = [(255, 80, 120), (170, 120, 255)][i % 2] + (int(255 * (1 - k)),)
                d.line((x + r0 * math.cos(ang), Y_HEART + r0 * math.sin(ang), x + r1 * math.cos(ang), Y_HEART + r1 * math.sin(ang)), fill=col, width=6)
        likes = 48200 + int(100 + 4700 * eout((t - T_INSTA) / .62)) if t > T_INSTA else 48200
    l = label(fmt_k(likes), 28, 600)
    scr.alpha_composite(_fade(l, a), (int(x - l.width / 2), Y_HEART + 36))

def _double_tap(scr, t):
    e = t - T_INSTA
    if e < 0 or e > .50: return
    s0 = .2 + 1.0 * spring(.34 * 1.6, 10, 6)
    s = (.2 + 1.0 * spring(e * 1.6, 10, 6)) if e < .34 else s0 * (1 - .45 * E.ein(clamp((e - .34) / .16)))   # pops, then shrinks away
    a = 1.0 if e < .34 else 1 - clamp((e - .34) / .16) ** 1.5
    h = E.cached('b_bigheart', lambda: E.shadow(grad_heart(300), 26, .5, (0, 12)))
    hs = h.resize((max(1, int(h.width * s)), max(1, int(h.height * s))), Image.BILINEAR)
    y = SH * .60 - 260 * E.ein(clamp((e - .34) / .16))
    scr.alpha_composite(_fade(hs, a), (int(SW / 2 - hs.width / 2), int(y - hs.height / 2)))

def _floating_hearts(out, t, dst):
    """hearts streaming up past the phone's right edge after the like (screen space)."""
    e = t - (T_INSTA + .08)
    if e <= 0: return
    xr = (dst[1][0] + dst[2][0]) / 2; yb = (dst[1][1] * .45 + dst[2][1] * .55)
    cols = [grad_heart(54), heart_img(46, fill=(255, 48, 80), outline=None), grad_heart(40), heart_img(58, fill=(170, 120, 255), outline=None)]
    for i in range(9):
        ei = e - i * .07
        if ei <= 0 or ei > 1.1: continue
        k = ei / 1.1; h = cols[i % 4]
        x = xr - 30 + 24 * math.sin(ei * 6 + i) + (i % 3) * 22
        y = yb - 620 * eout(k) - (i % 2) * 40
        s = .6 + .5 * eout(min(1, ei / .2))
        hs = h.resize((int(h.width * s), int(h.height * s)), Image.BILINEAR)
        _paste_c(out, hs, x, y, (1 - k ** 2) * clamp(ei / .08))
