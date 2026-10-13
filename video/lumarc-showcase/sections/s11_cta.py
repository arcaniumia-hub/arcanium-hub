"""s11 — "Comment 'LUMARC', and we'll show you what your page could look like." (51.08–54.36)

51.08  CUT to a medium shot; "COMMENT" pops big while a dark frosted Instagram comment row rises into the lower third
       (gradient story-ring avatar, handle 'you · now', 'Reply').
51.65  "LUMARC": the comment types itself letter by letter (gradient text, caret), small punch-in on the word.
52.08  the heart fills red with a pop + spark burst (and a '1 like' appears).
52.32  CUT (jump) — the founder steps back into depth in front of HIS PAGE: a frosted profile card (story-ring avatar,
       'yourbrand', posts / followers / following) with a 3×3 grid of loading skeletons ("we'll show you").
52.90  "what your page": the 9 posts fly in tile by tile (diagonal wave, scale-down + light kiss on landing) from
       LUMARC's premium work; carousel / Reel badges; followers count up.
53.85  "like": a light sweep shimmers across the finished grid. Handoff to s12 (54.36): s12 rebuilds this exact frame.
"""
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

START, END = E.span(28, 29)            # 51.08 – 54.36
T29 = E.TL[29]['t0']                    # 52.32 jump cut
# word onsets measured on the voice track (src/voice16k.raw)
W_COMMENT = 51.12
W_LUMARC = 51.65
TYPE0, TYPE_DT = 51.66, .052            # L-U-M-A-R-C (done 51.92)
HEART = 52.08
W_AND, W_WELL, W_SHOW, W_YOU = 52.40, 52.52, 52.62, 52.84
W_WHAT, W_YOUR, W_PAGE = 52.90, 53.06, 53.20
W_COULD, W_LOOK, W_LIKE = 53.46, 53.70, 53.84
TILE0, TILE_DT = 52.92, .085            # 9 tiles: 52.92 … 53.60
SWEEP = 53.86

TILE_ORDER = [0, 1, 3, 2, 4, 6, 5, 7, 8]   # diagonal wave (index = grid cell, row-major)

CUES = [
    (START, 'whoosh', {'gain': -10}),
    (W_COMMENT, 'glass', {'gain': -4}),              # comment row rises
] + [(TYPE0 + i * TYPE_DT, 'type', {'gain': -9}) for i in range(6)] + [
    (HEART, 'heart', {}),
    (HEART, 'pop', {'gain': -6}),
    (T29, 'swipe', {'gain': -4}),                     # cut to the profile page
    (W_SHOW, 'glass', {'gain': -8}),                  # skeleton grid shimmers in
] + [(TILE0 + k * TILE_DT + .02, 'pop', {'gain': -7}) for k in (0, 3, 6, 8)] + [
    (SWEEP, 'shimmer', {}),
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def C(k, fn): return E.cached(('s11',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def scale_im(im, s):
    if abs(s - 1) < .01: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)


def txt(s, size, wght, col):
    def mk():
        f = E.font(size, wght); l, t, r, b = f.getbbox(s)
        im = Image.new('RGBA', (r - l + 4, b - t + 4), (0, 0, 0, 0)); ImageDraw.Draw(im).text((2 - l, 2 - t), s, font=f, fill=col)
        return im
    return C(('txt', s, size, wght, col), mk)


def circle_mask(d, ss=4):
    m = Image.new('L', (d * ss, d * ss)); ImageDraw.Draw(m).ellipse((0, 0, d * ss - 1, d * ss - 1), fill=255)
    return m.resize((d, d), Image.LANCZOS)


def story_avatar(d, mono=False, initial=None):
    """IG story-ring avatar: gradient ring, dark gap, inner avatar (user silhouette or brand monogram)."""
    def mk():
        im = Image.new('RGBA', (d, d), (0, 0, 0, 0))
        ring = E.gradient(d, d, [(255, 170, 60), (255, 60, 120), (170, 60, 255)] if not mono else E.GRAD).convert('RGBA')
        ring = ring.rotate(-45, Image.BILINEAR); ring.putalpha(circle_mask(d)); im.alpha_composite(ring)
        g = int(d * .06); dd = d - 2 * g
        gap = Image.new('RGBA', (dd, dd), (16, 16, 22, 255)); gap.putalpha(circle_mask(dd)); im.alpha_composite(gap, (g, g))
        g2 = int(d * .11); d2 = d - 2 * g2
        if initial:
            inner = E.gradient(d2, d2, E.GRAD).convert('RGBA')
            f = E.font(int(d2 * .46), 800); ImageDraw.Draw(inner).text((d2 / 2, d2 / 2), initial, font=f, fill=E.WHITE, anchor='mm')
        else:
            inner = Image.new('RGBA', (d2, d2), (58, 60, 78, 255)); di = ImageDraw.Draw(inner)
            di.ellipse((d2 * .32, d2 * .16, d2 * .68, d2 * .52), fill=(170, 172, 190, 255))
            di.ellipse((d2 * .14, d2 * .58, d2 * .86, d2 * 1.25), fill=(170, 172, 190, 255))
        inner.putalpha(circle_mask(d2)); im.alpha_composite(inner, (g2, g2))
        return im
    return C(('sav', d, mono, initial), mk)


def heart_shape(size, fill, outline=None, width=3):
    def mk():
        ss = 4; S = size * ss; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = []
        for i in range(120):
            a = i / 120 * 2 * math.pi
            x = 16 * math.sin(a) ** 3
            y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((S / 2 + x * S / 36, S * .47 - y * S / 36))
        if fill: d.polygon(pts, fill=fill)
        if outline: d.line(pts + [pts[0]], fill=outline, width=width * ss, joint='curve')
        return im.resize((size, size), Image.LANCZOS)
    return C(('heart', size, fill, outline, width), mk)


# ================================================================ comment row (TL28)
CW, CH = 920, 236
CARD_Y = 1352
TXT_SIZE = 66


def comment_card():
    def mk():
        card = E.glass_panel(CW, CH, radius=48, tint=(14, 14, 22), alpha=.62, border=.32)
        card.alpha_composite(story_avatar(104), (38, 38))
        card.alpha_composite(txt('you', 40, 700, (245, 245, 250)), (172, 34))
        card.alpha_composite(txt('now', 34, 400, (150, 150, 165)), (172 + txt('you', 40, 700, (0, 0, 0)).width + 16, 38))
        card.alpha_composite(txt('Reply', 34, 600, (150, 150, 165)), (172, 174))
        return card
    return C('card', mk)


def lumarc_text():
    def mk():
        f = E.font(TXT_SIZE, 800); l, t, r, b = f.getbbox('LUMARC'); _, ta, _, ba = f.getbbox('LUMARC')
        w, h = r - l + 8, b - t + 8
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((4 - l, 4 - t), 'LUMARC', font=f, fill=255)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
        xs = [4 + f.getlength('LUMARC'[:i]) for i in range(7)]
        return g, xs
    return C('lumtxt', mk)


def draw_comment(ctx, t):
    k_in = expo((t - (W_COMMENT - .04)) / .45)
    if k_in <= 0: return
    out = clamp((T29 - .02 - t) / .1)
    card = comment_card().copy()
    # typed text
    g, xs = lumarc_text()
    n = int(clamp((t - TYPE0) / TYPE_DT + 1, 0, 6)) if t >= TYPE0 else 0
    tx, ty = 172, 92
    if n > 0:
        cut = g.crop((0, 0, int(xs[n]) + (6 if n == 6 else 0), g.height))
        card.alpha_composite(cut, (tx, ty))
        # newest letter pops (small scale from its baseline)
        lt = t - (TYPE0 + (n - 1) * TYPE_DT)
        if lt < .08 and n <= 6:
            li = g.crop((int(xs[n - 1]), 0, int(xs[n]), g.height)); s = 1.25 - .25 * eout(lt / .08)
            li2 = scale_im(li, s)
            card.alpha_composite(Image.new('RGBA', li.size, (14, 14, 22, 0)), (tx + int(xs[n - 1]), ty))
            card.alpha_composite(li2, (int(tx + xs[n - 1] + li.width / 2 - li2.width / 2), int(ty + li.height - li2.height)))
    # caret: solid while typing, then blinks
    cx = tx + (xs[n] if n else 4) + 6
    typing = TYPE0 - .1 <= t <= TYPE0 + 6 * TYPE_DT + .1
    blink = (int((t - START) / .26) % 2 == 0)
    if (typing or blink) and t < HEART + .05:
        cr = C('caret', lambda: E.gradient(5, TXT_SIZE + 6, E.GRAD_LIGHT).convert('RGBA'))
        card.alpha_composite(cr, (int(cx), ty - 2))
    # heart
    hx, hy = CW - 92, 104
    if t < HEART:
        card.alpha_composite(heart_shape(50, None, (235, 235, 242, 255), 3), (hx - 25, hy - 25))
    else:
        lt = t - HEART
        s = .4 + .6 * back(lt / .24, 3.2)
        hh = scale_im(heart_shape(50, (255, 48, 64, 255)), s)
        card.alpha_composite(hh, (int(hx - hh.width / 2), int(hy - hh.height / 2)))
        # spark burst
        kb = lt / .35
        if kb < 1:
            d = ImageDraw.Draw(card, 'RGBA')
            for j in range(10):
                a = j / 10 * 2 * math.pi + .3
                r0, r1 = 30 + 34 * eout(kb), 30 + 50 * eout(kb)
                col = (255, 90, 110) if j % 2 else (190, 150, 255)
                d.line((hx + math.cos(a) * r0, hy + math.sin(a) * r0, hx + math.cos(a) * r1, hy + math.sin(a) * r1),
                       fill=col + (int(255 * (1 - kb)),), width=4)
            # ring
            R = 26 + 40 * eout(kb)
            d.ellipse((hx - R, hy - R, hx + R, hy + R), outline=(255, 70, 90, int(200 * (1 - kb))), width=3)
        lk = txt('1 like', 34, 600, (150, 150, 165))
        card.alpha_composite(E.fade(lk, clamp(lt / .15)), (172 + txt('Reply', 34, 600, (0, 0, 0)).width + 28, 174))
    y = CARD_Y + 160 * (1 - k_in)
    ctx.add('screen', card, W / 2, y, glass=16, alpha=clamp(k_in * 1.6) * out)


def draw_comment_word(ctx, t):
    if t < W_COMMENT - .02: return
    lt = t - W_COMMENT + .02
    s = (.72 + .28 * back(lt / .18)) * (1.05 if .05 < lt < .3 else 1)
    im = E.word_img('COMMENT', 124, 'white')[0]
    ctx.add('screen', scale_im(im, s), W / 2, 1128, alpha=clamp(lt / .05) * clamp((T29 - .02 - t) / .08))


# ================================================================ profile page (TL29)
GX0, GY0 = 90, 470
PC_H = 1218                              # profile card height (top at 220)
TS, GAP = 296, 6
AV_S = .80


def teardown_frame():
    def mk():
        try:
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '8.5', '-i', E.TEARDOWN, '-frames:v', '1', '-vf', 'scale=540:960',
                                  '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, timeout=30).stdout
            return Image.frombytes('RGB', (540, 960), raw)
        except Exception:
            return Image.new('RGB', (540, 960), (20, 20, 24))
    return C('tdframe', mk)


def square(img, fx=.5, fy=.5, zoom=1.0):
    w, h = img.size; s = min(w, h) / zoom
    x0 = (w - s) * fx; y0 = (h - s) * fy
    return img.crop((int(x0), int(y0), int(x0 + s), int(y0 + s))).resize((TS, TS), Image.LANCZOS)


def _badge(kind):
    im = Image.new('RGBA', (40, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == 'car':
        d.rounded_rectangle((12, 4, 36, 28), 4, outline=(255, 255, 255, 240), width=3)
        d.rounded_rectangle((4, 12, 28, 36), 4, fill=(255, 255, 255, 240))
    else:   # reel
        d.rounded_rectangle((4, 6, 36, 34), 7, outline=(255, 255, 255, 240), width=3)
        d.polygon([(16, 13), (16, 27), (27, 20)], fill=(255, 255, 255, 240))
    sh = Image.new('RGBA', (52, 52), (0, 0, 0, 0)); a = Image.new('L', (52, 52)); a.paste(im.getchannel('A'), (6, 6))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * .6))); sh.alpha_composite(im, (6, 6))
    return sh


def tiles():
    def mk():
        A = E.asset
        src = [
            (square(A('close_food'), .5, .55), None),
            (square(A('carousel_1'), .5, .3), 'car'),
            (square(A('design_post'), .5, .35), None),
            (square(A('close_service'), .5, .4), 'reel'),
            (square(A('website'), .62, .5), None),
            (square(A('close_skill'), .5, .45), 'reel'),
            (square(A('carousel_2'), .5, .3), 'car'),
            (square(teardown_frame(), .5, .5), 'reel'),
            (square(A('close_food'), .5, .62, 1.7), None),
        ]
        out = []
        for im, b in src:
            im = im.convert('RGBA')
            if b: im.alpha_composite(_badge(b), (TS - 58, 4))
            out.append(im)
        return out
    return C('tiles', mk)


def cell_xy(i):
    r, c = divmod(i, 3)
    return GX0 + c * (TS + GAP) + TS / 2, GY0 + r * (TS + GAP) + TS / 2


def profile_card():
    def mk():
        w, h = 960, PC_H
        card = E.glass_panel(w, h, radius=46, tint=(14, 14, 22), alpha=.8, border=.28)
        card.alpha_composite(story_avatar(132, mono=True, initial='Y'), (40, 40))
        card.alpha_composite(txt('yourbrand', 40, 700, (245, 245, 250)), (200, 50))
        # verified-ish dot in brand gradient
        dot = E.gradient(30, 30, E.GRAD).convert('RGBA'); dot.putalpha(circle_mask(30))
        ImageDraw.Draw(dot).line((8, 15, 13, 20, 22, 10), fill=(255, 255, 255, 255), width=3)
        card.alpha_composite(dot, (200 + txt('yourbrand', 40, 700, (0, 0, 0)).width + 12, 58))
        for j, lab in enumerate(['posts', 'followers', 'following']):
            card.alpha_composite(txt(lab, 34, 400, (160, 160, 175)), (200 + j * 220, 152))
        return card
    return C('pcard', mk)


def fmt_followers(v):
    return f'{v / 1000:.1f}K' if v >= 1000 else f'{int(v)}'


def stat_vals(t):
    k = smooth((t - TILE0) / (TILE0 + 9 * TILE_DT + .3 - TILE0))
    posts = 3 + int(round(k * 245))
    fol = lerp(214, 38200, k ** 1.6)
    return f'{posts}', fmt_followers(fol), '312'


def skel_tile():
    def mk():
        im = Image.new('RGBA', (TS, TS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, TS - 1, TS - 1), 8, fill=(27, 26, 36, 255))
        d.rounded_rectangle((1, 1, TS - 2, TS - 2), 7, outline=(255, 255, 255, 26), width=1)      # 1 px inner highlight
        d.line((10, 1, TS - 10, 1), fill=(255, 255, 255, 46), width=1)
        return im
    return C('skel2', mk)


def skel_shimmer(t, i):
    """the slice of one diagonal light band (shared by all 9 skeletons, so it sweeps the grid as one)."""
    gw = 3 * TS + 2 * GAP
    ph = ((t - T29) / .62) % 1.0
    c = lerp(-300, gw * 1.5 + 300, ph)
    r, cc = divmod(i, 3); ox, oy = cc * (TS + GAP), r * (TS + GAP)
    xx = np.arange(TS, dtype=np.float32)[None, :] + ox + (np.arange(TS, dtype=np.float32)[:, None] + oy) * .5
    band = np.clip(1 - np.abs(xx - c) / 150, 0, 1) ** 2 * .10
    if band.max() < .004: return None
    m = np.asarray(skel_tile().getchannel('A'), np.float32) / 255
    im = Image.new('RGBA', (TS, TS), (200, 196, 255, 0)); im.putalpha(Image.fromarray((band * m * 255).astype(np.uint8)))
    return im


def sweep_band(k, w, h, width=.2, strength=.75):
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :] + np.linspace(0, .5, h, dtype=np.float32)[:, None]
    c = lerp(-.4, 1.9, k); band = np.clip(1 - np.abs(xx - c) / width, 0, 1) ** 2 * strength
    im = Image.new('RGBA', (w, h), (255, 255, 255, 0)); im.putalpha(Image.fromarray((band * 255).astype(np.uint8))); return im


def page_layers(ctx, t, intro=True):
    """profile card + grid into ctx 'behind' layers (world space, camera z=1)."""
    k_card = expo((t - (T29 - .02)) / .4) if intro else 1
    cy = 220 + PC_H / 2 + 80 * (1 - k_card)
    al = clamp(k_card * 1.4)
    ctx.add('behind', profile_card(), W / 2, cy, glass=18, alpha=al)
    # live stats
    oy = cy - PC_H / 2
    for j, v in enumerate(stat_vals(t)):
        im = txt(v, 46, 700, (245, 245, 250))
        ctx.add('behind', im, 60 + 200 + j * 220, oy + 98, center=False, alpha=al)
    # grid
    T = tiles()
    for k, i in enumerate(TILE_ORDER):
        cx, cyy = cell_xy(i); cyy += 80 * (1 - k_card)
        t0 = TILE0 + k * TILE_DT
        if t < t0 + .02:
            # loading skeleton: dark glass tile + one synchronised diagonal shimmer across the whole grid
            sk = expo((t - (T29 + .06 + .025 * i)) / .3)
            if sk > 0 and intro:
                ctx.add('behind', skel_tile(), cx, cyy + 14 * (1 - sk), alpha=sk * al)
                sh = skel_shimmer(t, i)
                if sh is not None: ctx.add('behind', sh, cx, cyy + 14 * (1 - sk), alpha=sk * al)
            continue
        lt = t - t0
        k = expo(lt / .26)
        s = lerp(1.28, 1.0, k)
        ang = math.atan2(cyy - 900, cx - 540); R = 170 * (1 - k)
        x = cx + math.cos(ang) * R; y = cyy + math.sin(ang) * R
        im = T[i]
        if lt < .16:      # light kiss on landing
            fl = C(('kiss',), lambda: Image.new('RGBA', (TS, TS), (255, 255, 255, 255)))
            im = im.copy(); im.alpha_composite(E.fade(fl, .45 * (1 - lt / .16)))
        ctx.add('behind', scale_im(im, s), x, y, alpha=clamp(lt / .035) * al)     # opaque after 1 frame — no ghosting
    # final shimmer sweep across the finished grid
    ks = (t - SWEEP) / .5
    if 0 < ks < 1:
        gw = 3 * TS + 2 * GAP
        band = sweep_band(ks, gw, gw)
        m = C('gridmask', lambda: _grid_mask())
        a = np.minimum(np.asarray(band.getchannel('A')), np.asarray(m)); band.putalpha(Image.fromarray(a))
        ctx.add('behind', band, GX0, GY0, center=False)
    # dark halo behind the founder (separates him from the page)
    halo = C('halo', lambda: _halo())
    ctx.add('behind', halo, W / 2, 1300, alpha=.85 * al)


def _grid_mask():
    gw = 3 * TS + 2 * GAP; m = Image.new('L', (gw, gw)); d = ImageDraw.Draw(m)
    for i in range(9):
        r, c = divmod(i, 3); d.rectangle((c * (TS + GAP), r * (TS + GAP), c * (TS + GAP) + TS - 1, r * (TS + GAP) + TS - 1), fill=255)
    return m


def _halo():
    w, h = 1000, 1100
    x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]; y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    a = np.clip(1 - (x ** 2 + y ** 2), 0, 1) ** 1.6 * .55
    im = Image.new('RGBA', (w, h), (6, 6, 12, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im


# ================================================================ captions (own, voice-synced)
CAP_PAGES = [
    ([('AND', W_AND, 'white'), ("WE'LL", W_WELL, 'white'), ('SHOW', W_SHOW, 'white'), ('YOU', W_YOU, 'white')], W_AND - .04, W_WHAT - .03),
    ([('WHAT', W_WHAT, 'white'), ('YOUR', W_YOUR, 'white'), ('PAGE', W_PAGE, 'grad')], W_WHAT - .04, W_COULD - .03),
    ([('COULD', W_COULD, 'white'), ('LOOK', W_LOOK, 'white'), ('LIKE.', W_LIKE, 'white')], W_COULD - .04, END),
]


def pop_words(ctx, t, words, a, z, y=1560, base=84):
    if not a <= t < z: return
    gap = base * .34; widths = []
    for w, _, st in words:
        l, tp, r, b = E.font(base).getbbox(w); widths.append(r - l)
    x = W / 2 - (sum(widths) + gap * (len(words) - 1)) / 2
    for (w, t0, st), ww in zip(words, widths):
        if t >= t0 - .02:
            im = E.word_img(w, base, st)[0]
            lt = t - t0 + .02; s = (.72 + .28 * back(lt / .16)) * (1.06 if .05 < lt < .3 else 1)
            al = clamp(lt / .05) * clamp((z - t) / .06)
            ctx.add('screen', scale_im(im, s), x + ww / 2, y, alpha=al)
        x += ww + gap


# ================================================================ founder (feathered plate edges)
def film_of(ctx):
    for c in (ctx.compose.__closure__ or ()):
        v = c.cell_contents
        if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    return None


def feather_mask():
    """alpha multiplier: soft 110 px ramps at the plate's left/right borders + fade into the bottom corners, so the
    scaled-down plate never shows straight 'cardboard' cut lines on the hoodie."""
    def mk():
        x = np.arange(W, dtype=np.float32)[None, :]; y = np.arange(H, dtype=np.float32)[:, None]
        side = np.clip(np.minimum(x, W - 1 - x) / 110, 0, 1); side = side * side * (3 - 2 * side)
        cx = np.clip((W / 2 - np.abs(x - W / 2)) / 340, 0, 1)
        bot = np.clip((H - y) / 320, 0, 1)
        return (side * (1 - (1 - cx) * (1 - bot))).astype(np.float32)
    return C('feather', mk)


_FA = {}
def add_founder(ctx, s):
    """draw the founder ourselves as the top 'behind' layer (instead of the engine's hard-edged plate)."""
    F = film_of(ctx)
    if F is None: ctx.avatar.update(s=s, x=0., y=0.); return
    ctx.avatar['show'] = False
    av = F.av.frame(ctx.t)
    if _FA.get('k') is not av:
        a = np.asarray(av.getchannel('A'), np.float32) * feather_mask()
        o = av.copy(); o.putalpha(Image.fromarray(a.astype(np.uint8))); _FA.update(k=av, v={}, f=o)
    if s not in _FA['v']: _FA['v'][s] = scale_im(_FA['f'], s)
    im = _FA['v'][s]
    ctx.add('behind', im, 540 - im.width / 2, H - im.height, center=False)


# ================================================================ draw
def page_scene(ctx, t, intro=True):
    """the TL29 world (also rebuilt by s12 for its opening frames)."""
    ctx.bg_dim = .55; ctx.bg_blur = 8
    page_layers(ctx, t, intro)
    add_founder(ctx, AV_S)


def draw(ctx, lt, t):
    ctx.captions = False
    if t < T29:
        ka = expo((t - W_LUMARC) / .3)
        ctx.cam = dict(z=1.14 + .04 * smooth(lt / 1.2) + .05 * ka, x=540., y=760., dx=0., dy=0., rot=0.)
        ctx.bg_dim = .22; ctx.bg_blur = 2
        draw_comment_word(ctx, t)
        draw_comment(ctx, t)
        ctx.post['vignette'] = .4
        return
    # ---- profile page
    k = expo((t - T29) / .45)
    ctx.cam = dict(z=1.0 + .06 * (1 - k) + .025 * smooth((t - T29) / 2.0), x=540., y=900., dx=0., dy=0., rot=0.)
    page_scene(ctx, t)
    for words, a, z in CAP_PAGES:
        pop_words(ctx, t, words, a, z)
    ctx.post['vignette'] = .42
