"""s07 — "And a great first impression doesn't just look good. It builds trust. And trust is what makes people buy."
(28.92–35.04)

Premium product-UI layer around the founder: frosted-glass cards floating in depth (behind him and in front of him).
TL18  wide, centred (s=1, cam z 1.02->1.09, slow lateral drift — no plate edges anywhere). "great" -> a glass
      brand-profile card rises BEHIND his left shoulder (his head overlaps it), "first" -> a hero-post card further
      back (defocused); "impression" -> the profile grid fills tile by tile; "look good" -> a 'Looks good' glass chip
      pops IN FRONT of him (clear of card and head), the check draws on "good", a sheen sweeps the card.
TL19  cut to an off-centre close-up (z 1.40, founder right via cam pan). "builds" -> a trust card BUILDS itself row
      by row on the left; stars fill one by one, reviews count up; on "trust" the shield fills with a glow ring and
      the trust meter completes.
TL20  cut to a medium shot (z 1.16, founder left). "trust" -> compact 5.0 trust chip; "makes" -> revenue card rises
      over his right shoulder, neon chart draws, counter rolls; "people" -> customer avatars stack in; "buy" -> chart
      spikes, 'New order / Purchase complete' notification drops in under the IG top bar (cash). Ends on a clean
      right-column layout (toast / chip / revenue) for the s08 slats.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

START, END = E.span(18, 20)                       # 28.92 – 35.04
T19, T20 = E.TL[19]['t0'], E.TL[20]['t0']         # 31.72, 32.84 (jump cuts)
# word onsets measured on the voice track (src/tight16k.raw, 10 ms low/high band envelopes: closures, bursts, fricatives)
W_GREAT, W_FIRST, W_IMPR = 29.22, 29.64, 29.85            # 'great' g-burst 29.22 (closure 29.19-29.21)
W_LOOK, W_GOOD = 31.05, 31.42                             # 'good' after the 31.33-31.41 silence
W_BUILDS, W_TRUST = 31.95, 32.30                          # 'trust' tr-burst 32.28, vowel 32.42
W_TRUST2, W_MAKES, W_PEOPLE, W_BUY = 33.01, 33.83, 34.25, 34.62   # 'makes' m-murmur 33.83, 'people' p-burst 34.25

# own caption track, engine look (same pages / words / layout as engine.draw_captions) on the measured onsets: the
# engine's syllable estimate has 'BUILDS' at 32.28 (10 frames after the voice and the trust card) and 'GREAT' 6 frames
# late. Engine captions are off for the whole section, which also removes the 1-frame ghost of s06's last page.
CAP_T0 = {18: [29.01, 29.12, W_GREAT, W_FIRST, W_IMPR, 30.55, 30.82, W_LOOK, W_GOOD],
          19: [31.78, W_BUILDS, 32.28],
          20: [32.90, W_TRUST2, 33.59, 33.70, W_MAKES, W_PEOPLE, W_BUY]}

CUES = [
    (W_GREAT - .02, 'glass', {'gain': -4}),          # profile card rises behind him
    (W_FIRST, 'whoosh', {'gain': -10}),              # hero post drifts in (far)
    (W_IMPR + .00, 'tick', {'gain': -8}),            # grid tiles
    (W_IMPR + .08, 'tick', {'gain': -9}),
    (W_IMPR + .16, 'tick', {'gain': -10}),
    (W_IMPR + .24, 'tick', {'gain': -11}),
    (W_LOOK, 'pop', {}),                             # 'Looks good' chip
    (W_GOOD + .02, 'shimmer', {'gain': -4}),         # check + sheen
    (T19, 'whoosh', {'gain': -6}),                   # cut to close-up
    (W_BUILDS, 'glass', {}),                         # trust card builds
    (W_BUILDS + .07, 'tick', {'gain': -8}),          # stars
    (W_BUILDS + .135, 'tick', {'gain': -8}),
    (W_BUILDS + .20, 'tick', {'gain': -8}),
    (W_BUILDS + .265, 'tick', {'gain': -8}),
    (W_TRUST, 'impact', {'gain': -6}),               # shield fills
    (W_TRUST + .02, 'shimmer', {}),
    (T20, 'swipe', {'gain': -6}),                    # cut to medium
    (W_TRUST2, 'pop', {'gain': -4}),                 # trust chip
    (W_MAKES - .02, 'swoosh_up', {}),                # revenue card
    (W_MAKES + .04, 'riser', {'to': W_BUY, 'gain': -8}),
    (W_PEOPLE, 'pop', {'gain': -8}),                 # customers
    (W_BUY, 'cash', {}),                             # purchase
    (W_BUY + .04, 'notify', {}),
]

clamp, eout, back = E.clamp, E.eout, E.back
W, H = E.W, E.H
WHITE = (250, 249, 246)
MUTED = (200, 198, 222)
SS = 3


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def C(key, fn): return E.cached(('s07',) + tuple(key if isinstance(key, tuple) else (key,)), fn)


# ================================================================ drawing kit
def F(size, w=500): return E.font(size, w)


def aa(w, h, fn, ss=SS):
    """draw at ss× then downsample (anti-aliased icons)."""
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); fn(big, ImageDraw.Draw(big), ss)
    return big.resize((w, h), Image.LANCZOS)


def grad_fill(mask, cols=E.GRAD_LIGHT):
    g = E.gradient(mask.width, mask.height, cols).convert('RGBA'); g.putalpha(mask); return g


def glow_of(img, r, a=.8, col=(120, 90, 255)):
    m = img.getchannel('A').filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(min(255, v * a)))
    g = Image.new('RGBA', img.size, col + (0,)); g.putalpha(m); return g


def padded(img, p):
    out = Image.new('RGBA', (img.width + 2 * p, img.height + 2 * p), (0, 0, 0, 0)); out.alpha_composite(img, (p, p)); return out


def text(d, xy, s, size, wght, fill, anchor='la'):
    d.text(xy, s, font=F(size, wght), fill=fill, anchor=anchor)


def text_grad(s, size, wght, cols=E.GRAD_LIGHT):
    f = F(size, wght); l, t, r, b = f.getbbox(s)
    m = Image.new('L', (r - l + 4, b - t + 4)); ImageDraw.Draw(m).text((2 - l, 2 - t), s, font=f, fill=255)
    return grad_fill(m, cols)


def check_pts(cx, cy, r):
    return [(cx - .42 * r, cy + .02 * r), (cx - .12 * r, cy + .32 * r), (cx + .46 * r, cy - .30 * r)]


def partial(pts, k):
    """polyline truncated at fraction k of its length."""
    if k >= 1: return pts
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L) * k; out = [pts[0]]
    for i, l in enumerate(L):
        if tot >= l: out.append(pts[i + 1]); tot -= l
        else:
            a, b = pts[i], pts[i + 1]; u = tot / l if l else 0; out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)); break
    return out


def check_badge(size, k=1.0, ring=False):
    """gradient circle with a white check drawn to fraction k."""
    kq = round(clamp(k) * 16) / 16
    def mk():
        def fn(big, d, s):
            R = size * s
            m = Image.new('L', big.size); ImageDraw.Draw(m).ellipse((0, 0, R - 1, R - 1), fill=255)
            big.alpha_composite(grad_fill(m, E.GRAD))
            hl = Image.new('L', big.size); ImageDraw.Draw(hl).ellipse((R * .12, R * .04, R * .88, R * .5), fill=60)
            big.alpha_composite(Image.merge('RGBA', [Image.new('L', big.size, 255)] * 3 + [Image.composite(hl, Image.new('L', big.size), m)]))
            if kq > 0:
                P = partial(check_pts(R / 2, R / 2, R * .62), kq)
                if len(P) > 1:
                    d.line(P, fill=(255, 255, 255, 255), width=int(R * .1), joint='curve')
                    for p in (P[0], P[-1]): d.ellipse((p[0] - R * .05, p[1] - R * .05, p[0] + R * .05, p[1] + R * .05), fill=(255, 255, 255, 255))
        return aa(size, size, fn)
    return C(('chk', size, kq), mk)


def star_poly(cx, cy, r):
    return [(cx + (r if i % 2 == 0 else r * .45) * math.sin(i * math.pi / 5), cy - (r if i % 2 == 0 else r * .45) * math.cos(i * math.pi / 5)) for i in range(10)]


STAR_GOLD = (255, 206, 96)
def star(size, fill):
    """star icon; fill 0..1 (pops from outline to solid)."""
    fq = round(clamp(fill) * 8) / 8
    def mk():
        def fn(big, d, s):
            R = size * s; P = star_poly(R / 2, R / 2 + R * .04, R * .48)
            d.polygon(P, fill=(255, 255, 255, 46))
            if fq > 0:
                m = Image.new('L', big.size); ImageDraw.Draw(m).polygon(P, fill=int(255 * fq))
                g = Image.new('RGBA', big.size, STAR_GOLD + (0,)); g.putalpha(m); big.alpha_composite(g)
        return aa(size, size, fn)
    return C(('star', size, fq), mk)


def shield_poly(cx, cy, w, h):
    pts = []
    top = cy - h / 2
    pts += [(cx, top), (cx + w * .5, top + h * .16)]
    for i in range(1, 13):                          # right side curving to the tip
        u = i / 12; x = cx + w * .5 * (1 - u ** 1.6); y = top + h * .16 + (h * .84) * (u ** .8)
        pts.append((x, y))
    right = pts[1:]
    left = [(2 * cx - x, y) for x, y in reversed(right)]
    return [pts[0]] + right + left


def shield(size, outline_k, fill_k):
    oq, fq = round(clamp(outline_k) * 12) / 12, round(clamp(fill_k) * 10) / 10
    def mk():
        w, h = size, int(size * 1.14)
        def fn(big, d, s):
            P = shield_poly(w * s / 2, h * s / 2, w * s * .86, h * s * .9)
            Pc = P + [P[0]]
            if fq > 0:
                m = Image.new('L', big.size); ImageDraw.Draw(m).polygon(P, fill=int(255 * fq)); big.alpha_composite(grad_fill(m, E.GRAD))
            if oq > 0:
                d.line(partial(Pc, oq), fill=(255, 255, 255, 235), width=int(3.2 * s), joint='curve')
            if fq > .5:
                ck = check_pts(w * s / 2, h * s * .47, w * s * .5)
                d.line(partial(ck, (fq - .5) * 2), fill=(255, 255, 255, 255), width=int(w * s * .075), joint='curve')
        return aa(w, h, fn)
    return C(('shield', size, oq, fq), mk)


def heart(size, col=(255, 92, 140)):
    def mk():
        def fn(big, d, s):
            R = size * s; P = []
            for i in range(80):
                a = i / 80 * 2 * math.pi; x = 16 * math.sin(a) ** 3; y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
                P.append((R / 2 + x * R / 36, R / 2 + y * R / 36 + R * .03))
            d.polygon(P, fill=col + (255,))
        return aa(size, size, fn)
    return C(('heart', size), mk)


def card_base(w, h, r=44, tint=(255, 255, 255), alpha=.12, glow=True):
    def mk():
        im = E.glass_panel(w, h, radius=r, tint=tint, alpha=alpha, border=.5)
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
        if glow:   # soft brand light leaking in the top-left corner
            g = Image.new('L', (w, h)); ImageDraw.Draw(g).ellipse((-w * .35, -h * .45, w * .55, h * .35), fill=80)
            g = Image.composite(g.filter(ImageFilter.GaussianBlur(60)), Image.new('L', (w, h)), m)
            gl = Image.new('RGBA', (w, h), (130, 100, 255, 0)); gl.putalpha(g); im.alpha_composite(gl)
        # crisp top-edge highlight
        e = Image.new('L', (w, h)); ImageDraw.Draw(e).rounded_rectangle((1, 1, w - 2, h - 2), r, outline=255, width=2)
        e = Image.fromarray((np.asarray(e, np.float32) * np.clip(1.2 - np.linspace(0, 1.6, h)[:, None], 0, 1) * .5).astype(np.uint8))
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [e]))
        return im
    return C(('base', w, h, r, tint, alpha, glow), mk)


def card_shadow(w, h, r=44, op=.55, blur=34):
    def mk():
        p = blur * 2; im = Image.new('RGBA', (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
        m = Image.new('L', im.size); ImageDraw.Draw(m).rounded_rectangle((p, p, p + w, p + h), r, fill=int(255 * op))
        im.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); return im
    return C(('shadow', w, h, r, op, blur), mk)


def crop_cover(img, w, h, fy=.5):
    sc = max(w / img.width, h / img.height); im = img.resize((int(img.width * sc) + 1, int(img.height * sc) + 1), Image.LANCZOS)
    x0 = (im.width - w) // 2; y0 = int((im.height - h) * fy); return im.crop((x0, y0, x0 + w, y0 + h))


def thumb(name, w, h, r=18, fy=.5):
    return C(('thumb', name, w, h, r), lambda: E.rounded(crop_cover(E.asset(name), w, h, fy), r))


def sheen(img, k, width=.22, strength=.55):
    """diagonal light sweep across an RGBA card (k: 0..1 position)."""
    if k <= 0 or k >= 1: return img
    w, h = img.size
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :] + np.linspace(0, .5, h, dtype=np.float32)[:, None]
    c = lerp(-.3, 1.8, k); band = np.clip(1 - np.abs(xx - c) / width, 0, 1) ** 2 * strength
    a = np.asarray(img.getchannel('A'), np.float32) / 255
    m = Image.fromarray((band * a * 255).astype(np.uint8))
    out = img.copy(); out.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [m])); return out


def scaled(img, s):
    if abs(s - 1) < .005: return img
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BICUBIC if s > 1 else Image.BILINEAR)


def blurred(img, r):
    if r < .35: return img
    p = int(r * 3) + 2; return padded(img, p).filter(ImageFilter.GaussianBlur(r))


# ================================================================ cards
PW, PH = 440, 592
def profile_static():
    def mk():
        im = card_base(PW, PH).copy(); d = ImageDraw.Draw(im); pad = 32
        # avatar with gradient story ring
        def av(big, dd, s):
            R = 92 * s; m = Image.new('L', big.size); ImageDraw.Draw(m).ellipse((0, 0, R - 1, R - 1), fill=255)
            big.alpha_composite(grad_fill(m, E.GRAD))
            dd.ellipse((5 * s, 5 * s, R - 5 * s, R - 5 * s), fill=(20, 18, 30, 255))
            ph = crop_cover(E.asset('close_food'), int(R - 16 * s), int(R - 16 * s), .45).convert('RGBA')
            pm = Image.new('L', ph.size); ImageDraw.Draw(pm).ellipse((0, 0, ph.width - 1, ph.height - 1), fill=255); ph.putalpha(pm)
            big.alpha_composite(ph, (int(8 * s), int(8 * s)))
        im.alpha_composite(aa(92, 92, av), (pad, pad))
        text(d, (pad + 112, pad + 10), 'yourbrand', 38, 700, WHITE)
        nw = F(38, 700).getlength('yourbrand')
        im.alpha_composite(check_badge(32), (int(pad + 112 + nw + 10), pad + 16))
        text(d, (pad + 112, pad + 56), 'Book online', 38, 400, MUTED)
        return im
    return C('profile', mk)


GRID = [('close_food', .45), ('carousel_1', .3), ('design_post', .3), ('close_service', .35)]
def profile_card(t):
    im = profile_static().copy(); pad = 32; cw = (PW - 2 * pad - 12) // 2; y0 = 156
    for i, (name, fy) in enumerate(GRID):
        k = (t - (W_IMPR - .04 + i * .08)) / .3
        if k <= 0: continue
        th = thumb(name, cw, cw, 20, fy); s = .82 + .18 * eout(k)
        th = scaled(th, s)
        if k < 1: th = E.fade(th, clamp(k * 2.5))
        x = pad + (i % 2) * (cw + 12) + (cw - th.width) // 2; y = y0 + (i // 2) * (cw + 12) + (cw - th.height) // 2
        im.alpha_composite(th, (x, y))
    if t < W_IMPR:   # empty tile placeholders
        d = ImageDraw.Draw(im)
        for i in range(4):
            x = pad + (i % 2) * (cw + 12); y = y0 + (i // 2) * (cw + 12)
            d.rounded_rectangle((x, y, x + cw, y + cw), 20, fill=(255, 255, 255, 18))
    return im


HW, HH = 300, 452
def hero_card():
    def mk():
        im = card_base(HW, HH, r=38).copy(); d = ImageDraw.Draw(im); p = 14
        im.alpha_composite(thumb('design_post', HW - 2 * p, int((HW - 2 * p) * 1.25), 26, .3), (p, p))
        y = p + int((HW - 2 * p) * 1.25) + 18
        im.alpha_composite(heart(40), (p + 10, y))
        text(d, (p + 62, y), '2.4k', 38, 600, WHITE)
        return im
    return C('hero', mk)


def chip(k_check):
    w, h = 420, 116
    def base():
        im = card_base(w, h, r=58, alpha=.16).copy(); d = ImageDraw.Draw(im)
        text(d, (124, h // 2 + 1), 'Looks good', 46, 600, WHITE, 'lm'); return im
    im = C('chip', base).copy(); im.alpha_composite(check_badge(76, k_check), (24, (h - 76) // 2)); return im


TW, TH = 440, 500
def trust_card(t):
    """trust card assembling row by row from W_BUILDS; completes on W_TRUST."""
    im = card_base(TW, TH).copy(); pad = 34
    rows = []
    def row(i, img, x, y):
        k = (t - (W_BUILDS - .02 + i * .055)) / .32
        if k <= 0: return
        dy = 26 * (1 - eout(k)); a = clamp(k * 3)
        im.alpha_composite(E.fade(img, a) if a < 1 else img, (x, int(y + dy)))
    # row 0: shield + title
    ok = (t - W_BUILDS) / .3; fk = (t - W_TRUST) / .16
    sh = shield(92, ok, fk)
    if fk > 0:   # glow ring on "trust"
        gk = clamp((t - W_TRUST) / .5)
        g = glow_of(padded(sh, 30), 14, .9 * (1 - gk) + .35)
        im.alpha_composite(g, (pad - 30, pad - 30 + 2))
    row(0, sh, pad, pad)
    row(0, C('t_title', lambda: text_im2('Trusted', 46, 700, WHITE)), pad + 116, pad + 6)
    row(1, C('t_sub', lambda: text_im2('Verified', 38, 400, MUTED)), pad + 116, pad + 60)
    # row 2: 5.0 + stars
    row(2, C('t_div', lambda: Image.new('RGBA', (TW - 2 * pad, 2), (255, 255, 255, 40))), pad, 158)
    row(2, C('t_50', lambda: text_im2('5.0', 92, 700, WHITE)), pad - 4, 180)
    st = Image.new('RGBA', (5 * 38 + 4 * 6, 40), (0, 0, 0, 0))
    for i in range(5):
        sk = (t - (W_BUILDS + .05 + i * .065)) / .1
        if t >= W_TRUST: sk = 1
        s_im = star(38, sk)
        if 0 < sk < 1.6:
            s_im = scaled(s_im, 1 + .25 * math.sin(math.pi * clamp(sk / 1.6)))
        st.alpha_composite(s_im.crop((0, 0, min(38, s_im.width), min(40, s_im.height))) if s_im.width > 38 else s_im, (i * 44, 0))
    row(3, st, pad + 150, 214)
    # row 3: reviews counter
    n = int(2184 * smooth((t - W_BUILDS - .05) / .4))
    row(4, text_im2(f'{n:,} reviews', 38, 400, MUTED), pad, 296)
    # row 4: trust meter
    row(5, C('t_lab', lambda: text_im2('Trust', 38, 500, WHITE)), pad, 364)
    if t >= W_TRUST - .02:
        ek = clamp((t - W_TRUST + .02) / .2)
        ex = C('t_exc', lambda: text_grad('Excellent', 38, 700))
        im.alpha_composite(E.fade(ex, ek), (TW - pad - ex.width, 366 + int(10 * (1 - eout(ek)))))
    bar_k = (t - (W_BUILDS + .2)) / .5
    if bar_k > 0:
        bw = TW - 2 * pad; y = 432
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((pad, y, pad + bw, y + 16), 8, fill=(255, 255, 255, 34))
        fk2 = .62 * eout(bar_k) + .38 * eout((t - W_TRUST) / .35)
        fw = max(16, int(bw * clamp(fk2)))
        m = Image.new('L', (fw, 16)); ImageDraw.Draw(m).rounded_rectangle((0, 0, fw - 1, 15), 8, fill=255)
        g = grad_fill(m, E.GRAD_LIGHT)
        im.alpha_composite(glow_of(padded(g, 12), 6, .9), (pad - 12, y - 12)); im.alpha_composite(g, (pad, y))
    return im


def text_im2(s, size, wght, col):
    f = F(size, wght); l, t, r, b = f.getbbox(s)
    im = Image.new('RGBA', (r + 4, b + 4), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 0), s, font=f, fill=col)
    return im


CW, CH = 440, 124
def trust_chip(t):
    def base():
        im = card_base(CW, CH, r=62, alpha=.14).copy(); d = ImageDraw.Draw(im)
        im.alpha_composite(shield(66, 1, 1), (26, (CH - 76) // 2))
        text(d, (112, CH // 2 + 2), '5.0', 52, 700, WHITE, 'lm')
        for i in range(5): im.alpha_composite(star(40, 1), (200 + i * 44, (CH - 40) // 2))
        return im
    im = C('tchip', base)
    sk = (t - W_TRUST2) / .45
    return sheen(im, sk, .25, .6) if 0 < sk < 1 else im


RW, RH = 440, 556
def chart_pts():
    def mk():
        n = 60; pts = []
        rng = np.random.default_rng(7)
        noise = np.convolve(rng.normal(0, 1, n + 8), np.ones(5) / 5, 'same')[4:-4]
        for i in range(n):
            u = i / (n - 1)
            y = .12 + .58 * u ** 1.6 + .07 * math.sin(u * 9) * (1 - u) + .035 * noise[i]
            pts.append((u, y))
        return pts
    return C('cpts', mk)


def chart(t, w, h):
    """neon line chart drawing in from W_MAKES, spiking on W_BUY."""
    p = .08 + .92 * smooth((t - W_MAKES) / (W_BUY - W_MAKES - .02))
    spike = eout((t - W_BUY) / .28)
    s = 2; Wc, Hc = w * s, h * s; top, bot = 22 * s, h * s - 8 * s
    pts = chart_pts(); n = len(pts); m = max(2, int(n * p))
    P = []
    for i in range(m):
        u, y = pts[i]
        if i >= n - 6: y += .28 * spike * ((i - (n - 6)) / 5) ** 2
        P.append((u * (Wc - 24 * s) + 6 * s, bot - (bot - top) * min(1, y)))
    im = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for gy in (.25, .5, .75):   # faint grid
        yy = int(top + (bot - top) * gy)
        for xx in range(0, Wc, 18 * s): d.line((xx, yy, xx + 8 * s, yy), fill=(255, 255, 255, 26), width=s)
    # area fill
    am = Image.new('L', (Wc, Hc)); ImageDraw.Draw(am).polygon(P + [(P[-1][0], bot), (P[0][0], bot)], fill=255)
    vg = np.linspace(.42, 0, Hc, dtype=np.float32)[:, None]
    am = Image.fromarray((np.asarray(am, np.float32) * vg).astype(np.uint8))
    area = Image.new('RGBA', (Wc, Hc), (110, 90, 255, 0)); area.putalpha(am); im.alpha_composite(area)
    lm = Image.new('L', (Wc, Hc)); ImageDraw.Draw(lm).line(P, fill=255, width=5 * s, joint='curve')
    g = Image.new('RGBA', (Wc, Hc), (130, 100, 255, 0)); g.putalpha(lm.filter(ImageFilter.GaussianBlur(9 * s)).point(lambda v: min(255, v * 2)))
    im.alpha_composite(g); im.alpha_composite(grad_fill(lm, E.GRAD_LIGHT))
    ex, ey = P[-1]
    if t >= W_BUY:   # ring pulse at the head
        rk = clamp((t - W_BUY) / .45); R = (10 + 40 * eout(rk)) * s
        d.ellipse((ex - R, ey - R, ex + R, ey + R), outline=(255, 255, 255, int(220 * (1 - rk))), width=3 * s)
    d.ellipse((ex - 9 * s, ey - 9 * s, ex + 9 * s, ey + 9 * s), fill=(255, 255, 255, 255))
    return im.resize((w, h), Image.LANCZOS), (ex / s, ey / s)


AV_COLS = [((255, 150, 120), (255, 90, 150)), ((90, 200, 255), (79, 107, 255)), ((150, 230, 170), (40, 170, 150)), ((210, 150, 255), (154, 77, 255))]
def face_dot(i, size=60):
    def mk():
        def fn(big, d, s):
            R = size * s; d.ellipse((0, 0, R - 1, R - 1), fill=(22, 20, 32, 255))
            m = Image.new('L', big.size); ImageDraw.Draw(m).ellipse((4 * s, 4 * s, R - 4 * s, R - 4 * s), fill=255)
            g = E.gradient(big.width, big.height, [AV_COLS[i][0], AV_COLS[i][1], AV_COLS[i][1]]).convert('RGBA'); g.putalpha(m)
            big.alpha_composite(g)
            # simple person glyph
            d.ellipse((R * .36, R * .2, R * .64, R * .48), fill=(255, 255, 255, 220))
            d.chord((R * .2, R * .54, R * .8, R * 1.1), 180, 360, fill=(255, 255, 255, 220))
            mm = Image.new('L', big.size); ImageDraw.Draw(mm).ellipse((0, 0, R - 1, R - 1), fill=255)
            a = np.minimum(np.asarray(big.getchannel('A')), np.asarray(mm)); big.putalpha(Image.fromarray(a))
        return aa(size, size, fn)
    return C(('face', i, size), mk)


def money(v): return '$' + f'{int(v):,}'


def revenue_card(t):
    def base():
        im = card_base(RW, RH).copy(); d = ImageDraw.Draw(im)
        text(d, (34, 34), 'Revenue', 38, 500, MUTED)
        lw = F(38, 600).getlength('Live')
        text(d, (RW - 34, 34), 'Live', 38, 600, WHITE, 'ra')
        d.ellipse((RW - 34 - lw - 30, 50, RW - 34 - lw - 14, 66), fill=(120, 230, 160, 255))
        return im
    im = C('rev', base).copy(); d = ImageDraw.Draw(im)
    v = lerp(31240, 48790, smooth((t - W_MAKES) / (W_BUY - W_MAKES)))
    if t >= W_BUY: v = 48790 + 129
    bump = math.sin(math.pi * clamp((t - W_BUY) / .3)) if t >= W_BUY else 0
    num = text_im2(money(v), 84, 700, WHITE)
    if bump > 0: num = scaled(num, 1 + .08 * bump)
    im.alpha_composite(num, (32, 86 - int(num.height * (.04 * bump))))
    ch, head = chart(t, RW - 48, 200)
    im.alpha_composite(ch, (24, 200))
    # customers row
    for i in range(4):
        k = (t - (W_PEOPLE - .04 + i * .06)) / .26
        if k <= 0: continue
        f = scaled(face_dot(i), .5 + .5 * back(k, 2.4)); f = E.fade(f, clamp(k * 3))
        cx = 34 + 30 + i * 40; cy = 456
        im.alpha_composite(f, (int(cx - f.width / 2), int(cy - f.height / 2)))
    k = (t - (W_PEOPLE + .2)) / .3
    if k > 0:
        tx = C('r_cust', lambda: text_im2('+312', 40, 700, WHITE))
        im.alpha_composite(E.fade(tx, clamp(k * 2)), (34 + 60 + 3 * 40 + 18 + int(16 * (1 - eout(k))), 436))
    if t >= W_BUY:   # +$129 floats up from the chart head
        fk = clamp((t - W_BUY) / .7)
        pl = C('r_plus', lambda: text_grad('+$129', 40, 700, [(150, 240, 190), (120, 230, 200), (110, 210, 255)]))
        a = clamp(fk * 5) * (1 - clamp((fk - .7) / .3))
        im.alpha_composite(E.fade(pl, a), (int(24 + head[0] - pl.width - 26), int(200 + head[1] + 6 - 34 * eout(fk))))
    return im


NW, NH = 880, 172
def notification():
    def mk():
        im = card_base(NW, NH, r=46, tint=(24, 22, 36), alpha=.62, glow=False).copy(); d = ImageDraw.Draw(im)
        def icon(big, dd, s):   # app icon: gradient squircle + shopping bag
            R = 108 * s; m = Image.new('L', big.size); ImageDraw.Draw(m).rounded_rectangle((0, 0, R - 1, R - 1), 28 * s, fill=255)
            big.alpha_composite(grad_fill(m, E.GRAD))
            dd.rounded_rectangle((R * .27, R * .38, R * .73, R * .8), 8 * s, fill=(255, 255, 255, 255))
            dd.arc((R * .36, R * .2, R * .64, R * .52), 180, 360, fill=(255, 255, 255, 255), width=int(6 * s))
            ck = check_pts(R / 2, R * .6, R * .3)
            dd.line(ck, fill=(110, 85, 255, 255), width=int(6 * s), joint='curve')
        im.alpha_composite(aa(108, 108, icon), (32, (NH - 108) // 2))
        x = 32 + 108 + 28
        text(d, (x, 38), 'New order', 42, 700, WHITE)
        nw = F(42, 700).getlength('New order')
        im.alpha_composite(check_badge(36), (int(x + nw + 14), 44))
        text(d, (NW - 36, 40), 'now', 36, 400, MUTED, 'ra')
        text(d, (x, 96), 'Purchase complete · $129', 38, 400, (226, 224, 240))
        return im
    return C('notif', mk)


# ================================================================ placement
def o2w(cam, ox, oy):
    X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    return cam['x'] + (ox - X) / cam['z'], cam['y'] + (oy - Y) / cam['z']


def put_card(ctx, layer, img, ox, oy, s=1.0, alpha=1.0, glass=14, blur=0.0, shadow=True, dim=1.0):
    """place a card at OUTPUT position (ox, oy) with on-screen scale s (world layers are pre-divided by cam z)."""
    if img is None or alpha <= .01 or s <= .02: return
    z = ctx.cam['z'] if layer != 'screen' else 1.0
    ss = s / z
    if dim < 1:
        img = Image.merge('RGBA', [*Image.eval(img.convert('RGB'), lambda v: int(v * dim)).split(), img.getchannel('A')])
    if layer == 'screen': x, y = ox, oy
    else: x, y = o2w(ctx.cam, ox, oy)
    if shadow:
        shd = card_shadow(img.width, img.height)
        ctx.add(layer, scaled(shd, ss), x, y + 22 * ss, alpha=alpha * .9)
    im = scaled(img, ss)
    if blur > .3: im = blurred(im, blur)
    g = int(round(glass * clamp(alpha * 1.4) * ss)) if glass else 0
    ctx.add(layer, im, x, y, glass=g, alpha=alpha)


def bob(t, ph, amp=7, per=3.2):
    return amp * math.sin(2 * math.pi * t / per + ph), amp * .6 * math.cos(2 * math.pi * t / (per * 1.3) + ph)


def rise_k(t, t0, d=.5): return expo((t - t0) / d)


# ================================================================ captions (own track)
def _cap_pages():
    pages = [dict(p, words=[dict(w) for w in p['words']]) for p in E.PAGES if p['seg'] in CAP_T0]
    for sg, ts in CAP_T0.items():
        ws = [w for p in pages if p['seg'] == sg for w in p['words']]
        assert len(ws) == len(ts), (sg, len(ws))
        for w, t0 in zip(ws, ts): w['t0'] = t0
        for a, b in zip(ws, ws[1:]): a['t1'] = b['t0']
        ws[-1]['t1'] = max(ws[-1]['t0'] + .2, min(ws[-1]['t1'], E.TL[sg]['t1']))
    for j, p in enumerate(pages):
        p['a'] = p['words'][0]['t0'] - .04
        if j + 1 < len(pages):
            nxt = pages[j + 1]['words'][0]['t0']; last = p['words'][-1]['t1']
            p['z'] = nxt - .02 if nxt - last < .5 else last + .35
            if pages[j + 1]['seg'] != p['seg']:      # a page never survives a multicam cut: it leaves ON the cut
                p['z'] = E.TL[p['seg'] + 1]['t0']; p['hard'] = True
        else: p['z'] = END; p['hard'] = True        # hard cut into s08
    return pages
CAP_PAGES = _cap_pages()


def draw_caps(ctx, t, cy0=1420, base=92):
    """same look/animation as engine.draw_captions (screen layers; engine captions off)."""
    ctx.captions = False
    for p in CAP_PAGES:
        if not (p['a'] <= t < p['z']): continue
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * back(lt / .16)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.06
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = E.fade(img, lt / .05)
            if p['z'] - t < .06 and not p.get('hard'): img = E.fade(img, (p['z'] - t) / .06)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2), center=False)


# ================================================================ draw
def draw(ctx, lt, t):
    draw_caps(ctx, t)
    if t < T19:
        # ---------------- TL18: wide & airy; profile card behind his shoulder, hero post far back, chip in front
        u = (t - START) / (T19 - START)
        z = 1.02 + .07 * smooth(u)
        ctx.cam = dict(z=z, x=540., y=860., dx=(z - 1) * 260 * (u - .5), dy=0., rot=0.)
        ctx.avatar.update(s=1.0, x=0.)
        ctx.bg_dim = .12
        # hero post (far): defocused, drifts slower
        k = rise_k(t, W_FIRST - .02, .7)
        if k > 0:
            bx, by = bob(t, 1.3, 6)
            put_card(ctx, 'behind', hero_card(), 850 + bx - 10 * u, 520 + by + 90 * (1 - k), s=.86 + .06 * k, alpha=clamp(k * 1.6) * .92,
                     blur=2.2 + 4 * (1 - k), glass=10, dim=.88)
        # profile card (mid, behind his head)
        k = rise_k(t, W_GREAT - .04, .62)
        if k > 0:
            bx, by = bob(t, 0, 7)
            im = profile_card(t)
            sk = (t - (W_GOOD + .02)) / .28          # sweep completes before the 31.72 cut
            if 0 < sk < 1: im = sheen(im, sk, .22, .5)
            put_card(ctx, 'behind', im, 262 + bx + 18 * u, 660 + by + 140 * (1 - k), s=.9 + .1 * k, alpha=clamp(k * 1.8),
                     blur=7 * (1 - k) ** 2)
        # 'Looks good' chip (front)
        k = (t - W_LOOK) / .3
        if k > 0:
            ck = clamp((t - W_GOOD) / .2)
            s = .55 + .45 * back(k, 2.0)
            bx, by = bob(t, 2.1, 5)
            put_card(ctx, 'screen', chip(ck), 300 + bx - 20 * u, 1150 + by + 40 * (1 - eout(k)), s=s, alpha=clamp(k * 3), glass=16)
        return

    if t < T20:
        # ---------------- TL19: off-centre close-up, trust card builds in front of him
        u = (t - T19) / (T20 - T19)
        z = 1.40 + .05 * u
        ctx.cam = dict(z=z, x=540., y=720., dx=212 - 16 * u, dy=0., rot=0.)    # off-centre close-up, founder right
        ctx.avatar.update(s=1.0, x=0.)
        ctx.bg_dim = .2
        k = (t - (W_BUILDS - .06)) / .45
        if k > 0:
            im = trust_card(t)
            if t >= W_TRUST:
                sk = (t - W_TRUST) / .45
                if sk < 1: im = sheen(im, sk, .25, .45)
            bx, by = bob(t, .7, 6)
            s = .9 + .1 * expo(k)
            # trust "pop" on the word
            if t >= W_TRUST: s *= 1 + .035 * math.sin(math.pi * clamp((t - W_TRUST) / .25))
            put_card(ctx, 'screen', im, 272 + bx, 900 + by + 60 * (1 - expo(k)), s=s, alpha=clamp(k * 3), glass=16)
            if t >= W_TRUST:
                ctx.post['flash'] = .12 * clamp(1 - (t - W_TRUST) / .15)
                ctx.post['flash_col'] = (190, 170, 255)
        return

    # ---------------- TL20: medium, founder left; trust chip, revenue card behind, purchase notification
    u = (t - T20) / (END - T20)
    z = 1.16 + .05 * smooth(u)
    ctx.cam = dict(z=z, x=540., y=880., dx=-(z - 1) * 540 + 4 + 10 * u, dy=0., rot=0.)    # medium, founder left
    ctx.avatar.update(s=1.0, x=0.)
    ctx.bg_dim = .14
    # revenue card (behind his shoulder)
    k = rise_k(t, W_MAKES - .04, .6)
    if k > 0:
        bx, by = bob(t, 2.6, 6)
        im = revenue_card(t)
        if t >= W_BUY:
            sk = (t - W_BUY) / .5
            if sk < 1: im = sheen(im, sk, .25, .4)
        put_card(ctx, 'front', im, 826 + bx, 880 + by + 160 * (1 - k), s=.84 + .07 * k, alpha=clamp(k * 1.8), blur=6 * (1 - k) ** 2)
    # trust chip (screen, upper right, above the revenue card)
    k = (t - W_TRUST2) / .3
    if k > 0:
        bx, by = bob(t, 4.0, 5)
        put_card(ctx, 'screen', trust_chip(t), 796 + bx, 494 + by + 30 * (1 - eout(k)), s=.9 * (.6 + .4 * back(k, 1.8)), alpha=clamp(k * 3), glass=14)
    # purchase notification (drops from the top on "buy")
    k = (t - (W_BUY - .03)) / .38
    if k > 0:
        y = lerp(-120, 330, back(k, 1.5))
        put_card(ctx, 'screen', notification(), 540, y, s=1.0, alpha=clamp(k * 4), glass=20)
        ctx.post['flash'] = .1 * clamp(1 - (t - W_BUY) / .14)
        ctx.post['flash_col'] = (200, 190, 255)
