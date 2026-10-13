"""s12 — "LUMARC. Be seen. Be remembered." + end card (54.36–58.84)

54.36  CUT (punch-in, z 1.03 -> 1.14) on the founder in front of his finished page (the s11 world rebuilt, frozen grid,
       feathered plate). Within 0.2 s the frame goes behind brand glass: a heavy (~45 px) blur graded into a
       deep-violet duotone with crushed blacks and a strong vignette — no stray food colours, just LUMARC light.
54.38  The 8 logo slices fly in from above/below on light trails with a bright glow edge, converging exactly on
54.58  "LUMARC" (measured stress): slam with a scale punch, additive violet bloom centred on the logo (no grey flash),
       shockwave ring, thin spark streaks. Boom.
55.08  (TL31 cut is hidden behind the glass; the camera behind it keeps one slow push.) The logo lifts;
55.22  "Be seen." rises out of a mask line under the logo.  55.94 "Be remembered." rises; 56.10 a narrow glyph-clipped
       light band runs through "remembered." then "seen." (shimmer).
56.30  The founder dissolves out of the glass (gone by 56.60, as his voice ends) into the designed end-card space:
       night gradient, a planet-horizon light arc in the lower third, a few slow defocused bokeh motes.
56.86  END CARD, balanced on the vertical centre: logo 600 px @ y 690, tagline 74 px @ 915/1011, gradient pill
       Comment “LUMARC” 760x132 (60 px, wght 700) @ y 1190 with a gentle breathing scale and floor glow,
       @lumarc_studio · slumarc.com 42 px @ y 1318. 58.00 one last light sweep over the logo and the pill.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import s11_cta as S11

START, END = E.span(30, 32)            # 54.36 – 58.84
T31, T32 = E.TL[31]['t0'], E.TL[32]['t0']   # 55.08, 55.80 (hidden behind the glass)
# word onsets measured on the voice track (src/voice16k.raw)
HIT = 54.58                             # "lu-MARC" stress (onset 54.46)
ASM = .16                                # slice assembly duration (lands on HIT)
W_BE1, W_SEEN = 55.14, 55.22
W_BE2, W_REM = 55.88, 55.94
SHIM = 56.10
GONE0, GONE1 = 56.30, round(E.VOICE_END - .04, 2)   # founder dissolves with his last word
PILL = 56.86
HANDLE = 57.06
SWEEP2 = 58.0

CUES = [
    (START, 'whoosh', {'gain': -8}),                # punch-in
    (START + .02, 'glass', {'gain': -4}),          # frost rises
    (HIT - ASM, 'riser', {'to': HIT}),             # slices converge
    (HIT, 'boom', {}),
    (HIT, 'impact', {'gain': -3}),
    (HIT + .03, 'shimmer', {'gain': -8}),
    (W_SEEN, 'swipe', {'gain': -9}),
    (W_REM, 'swipe', {'gain': -9}),
    (SHIM, 'shimmer', {}),                          # "remembered"
    (PILL, 'pop', {}),
    (HANDLE, 'tick', {'gain': -10}),
    (SWEEP2, 'shimmer', {'gain': -6}),
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H
N = 8


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def C(k, fn): return E.cached(('s12',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def scale_im(im, s, lanczos=False):
    if abs(s - 1) < .005: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS if lanczos else Image.BILINEAR)
def add_light(img, field, k, x0=0, y0=0):
    """additive light: img (RGBA, full frame) += field (float32 HxWx3) * k, at offset."""
    if k <= .01: return img
    a = np.asarray(img.convert('RGB'), np.float32)
    h, w = field.shape[:2]
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe > xs and ye > ys:
        a[ys:ye, xs:xe] += field[ys - y0:ye - y0, xs - x0:xe - x0] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


# ================================================================ brand space (end-card background)
HZ_Y, HZ_R = 1540, 1700                 # planet-horizon arc: top at y 1540


def space():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        col = np.zeros((H, W, 3), np.float32) + np.array([10, 10, 17], np.float32)
        # soft violet light behind the logo / type block
        r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - 860) / (H * .30)) ** 2)
        col += (np.clip(1 - r, 0, 1) ** 2.2)[..., None] * np.array([46, 32, 112], np.float32)
        # planet horizon: dark body below a thin gradient rim, atmosphere glow above it
        cy = HZ_Y + HZ_R
        d = np.sqrt((xx - W / 2) ** 2 + (yy - cy) ** 2) - HZ_R            # <0 inside the planet
        fall = np.exp(-((xx - W / 2) / 520) ** 2)                          # brightest at the centre
        hue = np.clip(xx / W, 0, 1)[..., None]
        rimc = np.array([96, 124, 255], np.float32) * (1 - hue) + np.array([176, 104, 255], np.float32) * hue
        rim = np.exp(-(d / 2.6) ** 2) * fall
        atmo = np.where(d > 0, np.exp(-np.clip(d, 0, None) / 70), np.exp(np.clip(d, None, 0) / 14)) * fall
        haze = np.where(d > 0, np.exp(-d / 260), 0) * fall
        inside = d < 0
        col = np.where(inside[..., None], col * .45 + np.array([8, 7, 16], np.float32) * (1 - np.exp(d / 400))[..., None], col)
        col += rimc * (rim[..., None] * 1.25 + atmo[..., None] * .55 + haze[..., None] * .22)
        col += np.array([255, 255, 255], np.float32) * (np.exp(-(d / 1.4) ** 2) * fall ** 3 * .45)[..., None]
        # vignette
        v = 1 - .55 * np.clip(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .45) / (H * .62)) ** 2 - .15, 0, 1)
        return Image.fromarray(np.clip(col * v[..., None], 0, 255).astype(np.uint8)).convert('RGBA')
    return C('space2', mk)


def bokeh_sprite(r, col):
    def mk():
        s = int(r * 2 + 8); y, x = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
        d = np.sqrt(x * x + y * y) / r
        a = np.clip((1.0 - d) / .35, 0, 1) ** 1.5 * (.7 + .3 * np.clip((d - .5) / .4, 0, 1))   # soft defocused disc
        im = Image.new('RGBA', (s, s), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.filter(ImageFilter.GaussianBlur(r * .08 + .8))
    return C(('bokeh', r, col), mk)


BOKEH = [  # x, y, radius, alpha, drift x/y px/s, colour
    (150, 420, 40, .16, 6, -9, (70, 100, 255)), (930, 330, 26, .18, -5, -7, (150, 80, 255)),
    (900, 1420, 54, .12, -4, -6, (110, 80, 255)), (170, 1280, 18, .22, 7, -10, (120, 130, 255)),
    (640, 230, 12, .22, 3, -8, (170, 140, 255)), (1010, 900, 32, .13, -6, -9, (140, 70, 255)),
    (300, 1720, 22, .16, 4, -12, (90, 110, 255)),
]


def motes(img, t, alpha):
    if alpha <= .02: return
    for i, (x, y, r, a, vx, vy, col) in enumerate(BOKEH):
        lt = t - START
        px = x + vx * lt + 10 * math.sin(lt * .6 + i)
        py = y + vy * lt
        tw = .8 + .2 * math.sin(t * 1.3 + i * 1.7)
        sp = bokeh_sprite(r, col)
        img.alpha_composite(E.fade(sp, min(1, a * alpha * tw * 2.0)), (int(px - sp.width / 2), int(py - sp.height / 2)))


# ================================================================ glass grade (founder + page behind brand glass)
def grade_maps():
    def mk():
        h, w = H // 8, W // 8
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        v = 1 - .7 * np.clip(((x - w / 2) / (w * .7)) ** 2 + ((y - h * .44) / (h * .6)) ** 2 - .12, 0, 1)
        return v.astype(np.float32)
    return C('gmaps', mk)


def frost(fr, k):
    """heavy blur + deep-violet duotone (crushed blacks, strong vignette). k 0..1 = glass rising."""
    if k <= 0: return fr
    small = fr.convert('RGB').resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(9))
    a = np.asarray(small, np.float32) / 255
    L = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    L = np.clip((L - .05) * 1.25, 0, 1) ** 1.35
    c0 = np.array([12, 11, 20], np.float32); c1 = np.array([40, 28, 98], np.float32); c2 = np.array([118, 96, 226], np.float32)
    col = c0 + (c1 - c0) * np.clip(L * 2.4, 0, 1)[..., None] + (c2 - c1) * (np.clip(L * 2.4 - 1, 0, 1) * .55)[..., None]
    col *= grade_maps()[..., None]
    g = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert('RGBA')
    if k >= 1: return g
    soft = fr.convert('RGB').filter(ImageFilter.BoxBlur(int(2 + 18 * k))).convert('RGBA')
    return Image.blend(soft, g, eout(k))


# ================================================================ logo
LOGO_W = 760


def logo_img(): return C('logo', lambda: E.logo(LOGO_W))
GP = 150                                 # padding of the glow images


def logo_glow():
    """bright violet glow of the logo shape (RGBA, padded by GP)."""
    def mk():
        lg = logo_img()
        a = Image.new('L', (lg.width + 2 * GP, lg.height + 2 * GP)); a.paste(lg.getchannel('A'), (GP, GP))
        out = Image.new('RGBA', a.size, (0, 0, 0, 0))
        for r, col, m in ((60, (100, 70, 255), 1.3), (18, (170, 150, 255), 1.0), (4, (235, 230, 255), .8)):
            g = Image.new('RGBA', a.size, col + (0,)); g.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, m=m: int(min(255, v * m * 1.6))))
            out.alpha_composite(g)
        return out
    return C('glow', mk)


def logo_bloom():
    def mk():
        lg = logo_img()
        a = Image.new('L', (lg.width + 2 * GP, lg.height + 2 * GP)); a.paste(lg.getchannel('A'), (GP, GP))
        out = Image.new('RGBA', a.size, (0, 0, 0, 0))
        for r, col, m in ((70, (100, 70, 255), .9), (24, (160, 140, 255), .7)):
            g = Image.new('RGBA', a.size, col + (0,)); g.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, m=m: int(min(255, v * m * 1.6))))
            out.alpha_composite(g)
        return out
    return C('bloom', mk)


def hit_field():
    """additive violet bloom centred on the logo (float32), 1100x900 around the logo centre."""
    def mk():
        w, h = 1400, 1100
        y, x = np.mgrid[0:h // 4, 0:w // 4].astype(np.float32) * 4
        r2 = ((x - w / 2) / 520) ** 2 + ((y - h / 2) / 330) ** 2
        f = np.exp(-r2 * 1.4)[..., None] * np.array([96, 72, 230], np.float32) \
            + np.exp(-r2 * 5)[..., None] * np.array([60, 50, 120], np.float32) \
            + np.exp(-(((x - w / 2) / 680) ** 2 + ((y - h / 2) / 16) ** 2))[..., None] * np.array([120, 120, 255], np.float32)  # anamorphic streak
        return np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32)
    return C('hitf', mk)


def slices_onto(out, t, cx, cy, s):
    """during the assembly: 8 slices converge on light trails with a bright glow edge; returns True if drawn."""
    k = (t - (HIT - ASM)) / ASM
    if not 0 <= k < 1: return False
    lg = scale_im(logo_img(), s); gl = scale_im(logo_glow(), s); gp = int(GP * s)
    sw = lg.width / N; x0, y0 = int(cx - lg.width / 2), int(cy - lg.height / 2)
    def off(i, kk): return (1 if i % 2 == 0 else -1) * (300 + 220 * hrand(i, 9)) * (1 - ein(kk) if kk < 1 else 0) ** 1.0
    for i in range(N):
        a0, a1 = int(i * sw), int((i + 1) * sw)
        piece = lg.crop((a0, 0, a1, lg.height)); gpiece = gl.crop((a0 + gp, 0, a1 + gp, gl.height))
        o = off(i, k)
        # light trail: glow copies at earlier positions (streak towards where the slice came from)
        for g in range(5, 0, -1):
            kk = max(0.0, k - .07 * g)
            out.alpha_composite(E.fade(gpiece, .3 * (1 - g / 6) * clamp(k * 4) * (1 - k ** 3)), (x0 + a0, int(y0 - gp + off(i, kk))))
        out.alpha_composite(E.fade(gpiece, .9 * clamp(k * 3)), (x0 + a0, int(y0 - gp + o)))
        out.alpha_composite(E.fade(piece, clamp(k * 3)), (x0 + a0, int(y0 + o)))
    return True


def sheen(img, k, mask, half=30, strength=.55, slope=.35):
    """narrow diagonal light band (+-half px) that brightens ONLY the ink: `mask` (float32 HxW, 0..1) is the bare
    glyph / pill-body shape, without the baked shadow or glow. The band lifts RGB towards white and never touches
    alpha, so nothing can appear outside the glyphs (no haze over shadows, glows or the transparent padding)."""
    if k <= 0 or k >= 1: return img
    w, h = img.size
    xx = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * slope
    c = lerp(-2 * half, w + h * slope + 2 * half, k)
    band = np.clip(1 - np.abs(xx - c) / half, 0, 1) ** 1.5 * strength
    cols = np.nonzero(band.max(0) > 0)[0]
    if len(cols) == 0: return img
    x0, x1 = int(cols[0]), int(cols[-1]) + 1                   # only the columns the band touches
    A = np.asarray(img, np.float32)[:, x0:x1].copy()
    m = (band[:, x0:x1] * mask[:, x0:x1])[..., None]
    A[..., :3] += (255 - A[..., :3]) * m
    out = img.copy(); out.paste(Image.fromarray(A.astype(np.uint8), 'RGBA'), (x0, 0)); return out


def ink_mask(key, img, lo, hi):
    """glyph mask from an image's alpha: below `lo` (shadow / glow / padding) -> 0, above `hi` -> 1."""
    return C(('ink', key), lambda: np.clip((np.asarray(img.getchannel('A'), np.float32) - lo) / (hi - lo), 0, 1))


def shock(img, t, cx, cy):
    k = (t - HIT) / .6
    if not 0 <= k < 1: return
    lay = Image.new('L', (W // 2, H // 2)); d = ImageDraw.Draw(lay)
    for R0, wm, am, dl in ((40, .7, .55, 0), (10, .45, .3, .08)):
        kk = clamp((t - HIT - dl) / .6)
        if kk <= 0: continue
        R = (R0 + 1150 * eout(kk)) / 2; wd = max(1, int((18 * (1 - kk) + 2) * wm / 2))
        d.ellipse((cx / 2 - R, cy / 2 - R * .62, cx / 2 + R, cy / 2 + R * .62), outline=int(255 * am * (1 - kk) ** 1.4), width=wd)
    g = lay.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    add = np.asarray(g, np.float32)[..., None] / 255 * np.array([160, 150, 255], np.float32)
    o = np.asarray(img.convert('RGB'), np.float32) + add
    img.paste(Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)))


def sparks(img, t, cx, cy):   # (unused: read as clip-art; kept for reference)
    k = (t - HIT) / .5
    if not 0 <= k < 1: return
    d = ImageDraw.Draw(img, 'RGBA')
    for j in range(28):
        a = hrand(j, 5) * 2 * math.pi; sp = 360 + 640 * hrand(j, 6)
        r0 = sp * eout(k); r1 = sp * eout(max(0, k - .12))
        x0, y0 = cx + math.cos(a) * r1, cy + math.sin(a) * r1 * .7
        x1, y1 = cx + math.cos(a) * r0, cy + math.sin(a) * r0 * .7
        d.line((x0, y0, x1, y1), fill=(225, 218, 255, int(200 * (1 - k) ** 1.6)), width=2)


# ================================================================ type
TYPE = 74


def word_mask_img(text, wght, grad):
    def mk():
        f = E.font(TYPE, wght); l, _, r, _ = f.getbbox(text); _, t, _, b = f.getbbox('Hgy'); pad = 30
        w, h = r - l + 2 * pad, b - t + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sh = Image.new('RGBA', (w, h), (4, 2, 14, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .8)))
        out.alpha_composite(sh, (0, 3))
        if grad:
            g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
            gl = Image.new('RGBA', (w, h), (120, 90, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .45)))
            out.alpha_composite(gl); out.alpha_composite(g)
        else:
            c = Image.new('RGBA', (w, h), E.WHITE + (0,)); c.putalpha(m); out.alpha_composite(c)
        return out, r - l, np.asarray(m, np.float32) / 255          # bare glyph mask (for the sheen)
    return C(('wm', text, wght, grad), mk)


def line_img(words):
    ims = [word_mask_img(*w) for w in words]; gap = 20
    tot = sum(iw for _, iw, _ in ims) + gap * (len(ims) - 1)
    x = -tot / 2; out = []
    for im, iw, m in ims:
        out.append((im, x + iw / 2, m)); x += iw + gap
    return out


def rise(im, k, dist=50):
    if k >= 1: return im
    if k <= 0: return None
    dy = int(dist * (1 - k))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.paste(im.crop((0, 0, im.width, im.height - dy)), (0, dy))
    return E.fade(out, clamp(k * 2.2))


LINE1 = [('Be', 300, False), ('seen.', 700, True)]
LINE2 = [('Be', 300, False), ('remembered.', 700, True)]


def draw_tagline(fr, t, y1, y2):
    for words, times, y, sh0 in ((LINE1, (W_BE1, W_SEEN), y1, SHIM + .22), (LINE2, (W_BE2, W_REM), y2, SHIM)):
        for (im, xo, gm), t0, (txt, _, grad) in zip(line_img(words), times, words):
            if grad: im = sheen(im, (t - sh0) / .5, gm, 30, .55)     # on the unshifted word, so the mask lines up
            r = rise(im, expo((t - t0 + .02) / .4))
            if r is None: continue
            fr.alpha_composite(r, (int(W / 2 + xo - r.width / 2), int(y - r.height / 2)))


def pill():
    return C('pill2', lambda: E.pill('Comment  “LUMARC”', 60, 700, grad=True, padx=80, pady=43))


def pill_glow():
    def mk():
        p = pill(); a = p.getchannel('A').point(lambda v: 255 if v > 200 else 0)
        big = Image.new('L', (p.width + 200, p.height + 200)); big.paste(a, (100, 100))
        g = Image.new('RGBA', big.size, (110, 80, 255, 0)); g.putalpha(big.filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * .75)))
        return g
    return C('pillglow', mk)


def handle():
    return C('handle2', lambda: E.text_im('@lumarc_studio  ·  slumarc.com', 42, 500, (214, 211, 236)))


# ================================================================ layout over time
def layout(t):
    """logo centre y, logo scale (x LOGO_W), tagline ys."""
    up1 = expo((t - (T31 - .04)) / .5)            # lift on "Be seen."
    up2 = expo((t - (GONE0 + .1)) / .7)            # settle into the end card
    ly = 830 - 110 * up1 - 30 * up2
    ls = 1.0 - .16 * up1 - .05 * up2               # 760 -> 638 -> 600 px
    if t >= HIT:
        ls *= 1 + .14 * (1 - expo((t - HIT) / .3))
    ls *= 1 + .015 * smooth((t - GONE1) / 2.0)     # calm push on the end card
    y1 = ly + 225; y2 = y1 + 96
    return ly, ls, y1, y2


# ================================================================ draw
def draw(ctx, lt, t):
    ctx.captions = False

    if t < GONE1:
        # the world behind the glass: the founder in front of his finished page (s11 rebuilt, frozen state)
        S11.page_scene(ctx, S11.END - .01, intro=False)
        ctx.cam = dict(z=1.14 + .14 * smooth(lt / 2.2), x=540., y=860. - 60 * smooth(lt / 2.2), dx=0., dy=0., rot=0.)
        gone = smooth((t - GONE0) / (GONE1 - GONE0))
    else:
        ctx.full = space(); gone = 1.0

    k_frost = (t - (START + .01)) / .12

    def wrap(fr):
        if t < GONE1:
            out = frost(fr, k_frost)
            if gone > 0: out = Image.blend(out, space(), gone)
        else:
            out = space().copy()
        motes(out, t, clamp((t - HIT) / .6))
        ly, ls, y1, y2 = layout(t)
        cx = W / 2
        if t >= HIT - ASM:
            if t >= HIT:
                shock(out, t, cx, ly)
                # calm breathing glow
                bl = scale_im(logo_bloom(), ls)
                ba = (.7 + .15 * math.sin((t - HIT) * 2.4)) * clamp((t - HIT) / .2)
                out.alpha_composite(E.fade(bl, ba), (int(cx - bl.width / 2), int(ly - bl.height / 2)))
            s0 = ls * (1 + .25 * (1 - ein((t - (HIT - ASM)) / ASM))) if t < HIT else ls
            if not slices_onto(out, t, cx, ly, s0):
                lg = logo_img()
                for t0, d in ((HIT + .08, .4), (SWEEP2, .7)):
                    sk = (t - t0) / d
                    if 0 < sk < 1: lg = sheen(lg, sk, ink_mask('logo', logo_img(), 90, 200), 40, .6)
                lg = scale_im(lg, ls, lanczos=True)
                out.alpha_composite(lg, (int(cx - lg.width / 2), int(ly - lg.height / 2)))
            # additive bloom on the slam (light, not a grey veil)
            if t >= HIT - .02:
                kb = .95 * (1 - eout((t - HIT) / .45)) if t >= HIT else .45
                if kb > .01:
                    f = hit_field(); out = add_light(out, f, kb, int(cx - f.shape[1] / 2), int(ly - f.shape[0] / 2))
        draw_tagline(out, t, y1, y2)
        # end card
        if t >= PILL:
            k = t - PILL; s = (.55 + .45 * back(k / .32, 2.4)) * (1 + .018 * (1 - math.cos((t - PILL - .32) * 2.6)) if k > .32 else 1)
            py = 1190
            pg = pill_glow(); out.alpha_composite(E.fade(pg, clamp(k / .3) * (.8 + .2 * math.sin(t * 2.6))), (int(cx - pg.width / 2), int(py - pg.height / 2 + 14)))
            p = pill()
            ps = (t - (SWEEP2 + .25)) / .6
            if 0 < ps < 1: p = sheen(p, ps, ink_mask('pill', pill(), 200, 230), 40, .45)
            p = scale_im(p, s)
            out.alpha_composite(E.fade(p, clamp(k / .08)), (int(cx - p.width / 2), int(py - p.height / 2)))
        if t >= HANDLE:
            k = eout((t - HANDLE) / .5); hd = handle()
            out.alpha_composite(E.fade(hd, k), (int(cx - hd.width / 2), int(1318 + 16 * (1 - k) - hd.height / 2)))
        return out

    ctx.wrap = wrap
    P = ctx.post
    P['vignette'] = .3
    if t >= HIT:
        P['rgb'] = 4 * clamp(1 - (t - HIT) / .08)
    elif t >= HIT - .1:
        P['zoom_blur'] = .4 * ein((t - (HIT - .1)) / .1)
