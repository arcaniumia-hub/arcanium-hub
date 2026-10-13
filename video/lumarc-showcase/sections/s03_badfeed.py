"""s03 — THE BAD FEED (9.32–14.44).  "They find your page. A blurry photo. A shaky video. A flyer made in five minutes."

TL3  the frame grows out of s02's phone screen (dive) into their Instagram profile: a whip-zoom settles to exactly z=1
     (UI type pin-sharp) while the page flick-scrolls (motion blurred) and bounces onto the header on "page"; the
     founder sits low so name / stats / Follow read above his head.
TL4  multicam cut (camera pan, founder right — off-centre framings are camera moves, never plate shifts). The blurry tile lifts out of the grid (leaving a hole) and flies forward in 3-D as a
     post card IN FRONT of him, landing on "blurry"; its photo keeps hunting for focus (AF brackets) and never gets sharp
     (iPhone AF/AE box keeps hunting).
TL5  cut (founder left). The shaky-video tile tears out BEHIND him as a big card that shakes with motion blur, its
     own footage jittering and a play bar running; glitch wobble on "shaky".
TL6  cut (low, founder bottom-right). The flyer slams in crooked from above the lens like a cheap sticker (squash + boing),
     the camera takes the hit; a starburst "5 MIN!" sticker pops on "five".
Every card drains colour from the world (sat 1 -> .55, cooler, darker): the BEFORE.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import engine as E

START, END = E.span(3, 6)                       # 9.32 – 14.44
T3, T4, T5, T6 = (E.TL[i]['t0'] for i in (3, 4, 5, 6))
# word onsets measured on the voice track (caption estimates are ±80 ms off here)
W_PAGE, W_BLURRY, W_SHAKY, W_FLYER, W_FIVE = 9.93, 10.60, 11.66, 12.85, 13.68
USER = 'yourbusiness'

CUES = [
    (T3 + .01, 'whoosh', {}),                   # whip into the page
    (W_PAGE + .02, 'click', {}),                # scroll lands on the header
    (T4 + .06, 'whoosh', {}),                   # tile lifts
    (W_BLURRY, 'pop', {}),                      # blurry card lands
    (T5 + .01, 'whoosh', {}),                   # blurry card thrown out / shaky tears out
    (W_SHAKY, 'glitch', {}),                    # shaky wobble
    (W_SHAKY + .02, 'pop', {}),
    (T6 + .01, 'whoosh', {}),                   # shaky card thrown out
    (W_FLYER, 'pop', {}),                       # cheap 'boing' slam
    (W_FLYER, 'impact', {'gain': -9}),
    (W_FIVE, 'pop', {}),                        # 5 MIN sticker
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def noise(t, seed, freqs=(7.3, 11.9, 17.1)):
    return sum(math.sin(t * f * 2 * math.pi + seed * (i + 1) * 1.7) / (i + 1) for i, f in enumerate(freqs)) / 1.83


# ---------------------------------------------------------------- 3-D card projection
def persp(img, rx=0., ry=0., rz=0., s=1., f=2200.):
    """project a flat RGBA card rotated in 3-D (degrees). returns (img, cx, cy) — card centre inside the result."""
    w, h = img.size
    rx, ry, rz = (math.radians(v) for v in (rx, ry, rz))
    cx_, sx_ = math.cos(rx), math.sin(rx); cy_, sy_ = math.cos(ry), math.sin(ry); cz_, sz_ = math.cos(rz), math.sin(rz)
    R = (np.array([[cz_, -sz_, 0], [sz_, cz_, 0], [0, 0, 1]]) @ np.array([[cy_, 0, sy_], [0, 1, 0], [-sy_, 0, cy_]])
         @ np.array([[1, 0, 0], [0, cx_, -sx_], [0, sx_, cx_]]))
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = []
    for x, y in src:
        X, Y, Z = R @ np.array([(x - w / 2) * s, (y - h / 2) * s, 0.])
        k = f / (f + Z); dst.append((X * k, Y * k))
    xs = [p[0] for p in dst]; ys = [p[1] for p in dst]
    x0, y0 = math.floor(min(xs)) - 1, math.floor(min(ys)) - 1
    ow, oh = math.ceil(max(xs)) - x0 + 2, math.ceil(max(ys)) - y0 + 2
    dst = [(x - x0, y - y0) for x, y in dst]
    A = []; B = []
    for (X, Y), (x, y) in zip(dst, src):
        A.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y]); B.append(x)
        A.append([0, 0, 0, X, Y, 1, -y * X, -y * Y]); B.append(y)
    co = np.linalg.solve(np.array(A, float), np.array(B, float))
    out = img.transform((max(1, ow), max(1, oh)), Image.PERSPECTIVE, tuple(co), Image.BILINEAR)
    # centre of the card after projection
    return out, -x0, -y0


def mblur(img, dx, dy, n=5):
    """directional motion blur (premultiplied average of n shifted copies) along (dx, dy) px."""
    L = math.hypot(dx, dy)
    if L < 2: return img, 0, 0
    n = int(clamp(L / 6, 3, 9))
    a = np.asarray(img, np.float32); al = a[..., 3:4] / 255.; pm = np.concatenate([a[..., :3] * al, al], 2)
    px, py = int(math.ceil(abs(dx) / 2)) + 1, int(math.ceil(abs(dy) / 2)) + 1
    big = np.zeros((a.shape[0] + 2 * py, a.shape[1] + 2 * px, 4), np.float32)
    for i in range(n):
        k = i / (n - 1) - .5; ox, oy = int(round(px + dx * k)), int(round(py + dy * k))
        big[oy:oy + a.shape[0], ox:ox + a.shape[1]] += pm
    big /= n; al2 = big[..., 3:4]
    rgb = np.where(al2 > 1e-4, big[..., :3] / np.maximum(al2, 1e-4), 0)
    out = Image.fromarray(np.clip(np.concatenate([rgb, al2 * 255], 2), 0, 255).astype(np.uint8), 'RGBA')
    return out, px, py


# ---------------------------------------------------------------- art (all cached)
def anton(size):
    return E.cached(('anton', size), lambda: ImageFont.truetype(os.path.join(os.path.dirname(E._th.__file__), 'fonts/Anton.ttf'), size))


def cover(img, w, h, zoom=1.0, cx=.5, cy=.5):
    sc = max(w / img.width, h / img.height) * zoom
    im = img.resize((max(w, int(img.width * sc)), max(h, int(img.height * sc))), Image.LANCZOS)
    x0 = int((im.width - w) * cx); y0 = int((im.height - h) * cy)
    return im.crop((x0, y0, x0 + w, y0 + h))


def cheap_tile(w, h, lines, bg, fg, outline=None):
    im = Image.new('RGB', (w, h), bg); d = ImageDraw.Draw(im)
    tot = sum(s for _, s in lines) * 1.08; y = (h - tot) / 2
    for txt, s in lines:
        f = anton(s); l, t, r, b = f.getbbox(txt)
        d.text(((w - (r - l)) / 2 - l, y - t), txt, font=f, fill=fg, stroke_width=4 if outline else 0, stroke_fill=outline)
        y += s * 1.08
    return im


GRID_Y, TW, TH, GAP = 860, 358, 448, 3
def tile_rect(i):
    r, c = divmod(i, 3); x = c * (TW + GAP); y = GRID_Y + r * (TH + GAP); return x, y, TW, TH


def tiles():
    def mk():
        bl, sh, fl = E.asset('bad_blurry_photo'), E.asset('bad_shaky_video'), E.asset('bad_flyer')
        dull = lambda im, k=.8: Image.blend(im, Image.new('RGB', im.size, (60, 52, 40)), 1 - k)
        T = [
            cover(bl, TW, TH),
            cheap_tile(TW, TH, [('WE ARE', 70), ('OPEN!!!', 96)], (250, 225, 30), (220, 20, 30), outline=(255, 255, 255)),
            cover(sh.crop((0, 0, 896, 1060)), TW, TH),
            cover(fl, TW, TH),
            dull(cover(bl, TW, TH, 1.9, .85, .2)),
            cheap_tile(TW, TH, [('SALE', 120), ('20% OFF', 70)], (30, 90, 255), (255, 250, 60)),
            cover(sh.crop((0, 0, 896, 1060)), TW, TH, 1.6, .2, .6).transpose(Image.FLIP_LEFT_RIGHT),
            cover(fl, TW, TH, 2.0, .6, .62),
            cheap_tile(TW, TH, [('HAPPY', 84), ('MONDAY', 84)], (60, 200, 90), (255, 90, 200), outline=(20, 20, 20)),
            dull(cover(bl, TW, TH, 1.4, .1, .9), .7),
            cover(fl, TW, TH, 1.5, .2, .1),
            cheap_tile(TW, TH, [('NEW', 90), ('MENU', 110), ('SOON', 60)], (240, 240, 240), (30, 30, 30)),
            cover(sh.crop((0, 0, 896, 1060)), TW, TH, 1.3, .9, .4),
            cheap_tile(TW, TH, [('CALL', 90), ('US', 130)], (200, 20, 30), (255, 255, 255)),
            dull(cover(bl, TW, TH, 1.2, .5, .5).rotate(4, Image.BICUBIC, expand=False), .75),
            cover(fl, TW, TH, 1.7, .9, .9),
            cheap_tile(TW, TH, [('THANK', 80), ('YOU!!', 100)], (255, 140, 0), (40, 40, 200)),
            dull(cover(sh.crop((0, 0, 896, 1060)), TW, TH, 1.8, .5, .3)),
        ]
        reel = [2, 6, 12, 17]
        for i in reel:   # reel badge
            d = ImageDraw.Draw(T[i]); x, y = TW - 50, 22
            d.rounded_rectangle((x, y, x + 32, y + 30), 7, outline=(255, 255, 255), width=3)
            d.polygon([(x + 12, y + 8), (x + 23, y + 15), (x + 12, y + 22)], fill=(255, 255, 255))
        return T
    return E.cached('s03_tiles', mk)


HY = 130          # header pushed below the phone's top UI (Reels header) — stats sit at y >= 380


def page(holes=()):
    """their Instagram profile (dark mode), optionally with lifted tiles left as holes. Drawn 1:1 at output scale
    (TL3 holds the camera at exactly z=1) so the UI type stays pin-sharp — only the posts look bad."""
    def mk():
        ph = GRID_Y + 6 * (TH + GAP) + 40
        im = Image.new('RGB', (W, ph), (10, 10, 13)); d = ImageDraw.Draw(im)
        wt = (245, 245, 248); mu = (168, 168, 178); o = HY
        # app bar
        d.line([(122, 152 + o), (100, 130 + o), (122, 108 + o)], fill=wt, width=6, joint='curve')
        d.text((150, 106 + o), USER, font=E.font(50, 700), fill=wt)
        for k in range(3): d.ellipse((910 + k * 22, 126 + o, 922 + k * 22, 138 + o), fill=wt)
        # avatar (no-brand grey) + stats
        av = Image.new('RGBA', (190, 190), (0, 0, 0, 0)); a = ImageDraw.Draw(av)
        a.ellipse((0, 0, 189, 189), fill=(58, 58, 66)); a.ellipse((53, 41, 137, 125), fill=(110, 110, 120))
        a.pieslice((25, 113, 165, 243), 180, 360, fill=(110, 110, 120))
        m = Image.new('L', (190, 190)); ImageDraw.Draw(m).ellipse((0, 0, 189, 189), fill=255); av.putalpha(m)
        im.paste(av.convert('RGB'), (100, 225 + o), m)
        for (n, lab), x in zip((('9', 'posts'), ('47', 'followers'), ('212', 'following')), (460, 660, 870)):
            f = E.font(56, 800); l, t, r, b = f.getbbox(n); d.text((x - (r - l) / 2 - l, 262 + o - t), n, font=f, fill=wt)
            f = E.font(34, 400); l, t, r, b = f.getbbox(lab); d.text((x - (r - l) / 2 - l, 340 + o - t), lab, font=f, fill=wt)
        d.text((100, 438 + o), 'Your Business', font=E.font(38, 700), fill=wt)
        d.text((100, 486 + o), 'best in town!!! open 7 days. call us', font=E.font(34, 400), fill=mu)
        for x0, x1, txt, col in ((100, 530, 'Follow', (0, 149, 246)), (546, 980, 'Message', (40, 40, 46))):
            d.rounded_rectangle((x0, 548 + o, x1, 616 + o), 16, fill=col)
            f = E.font(34, 700); l, t, r, b = f.getbbox(txt); d.text(((x0 + x1) / 2 - (r - l) / 2 - l, 582 + o - (b - t) / 2 - t), txt, font=f, fill=wt)
        # tab bar
        for k in range(3):
            x = 180 + k * 360; d.rectangle((x - 24, 660 + o, x + 24, 704 + o), outline=wt if k == 0 else mu, width=4)
            if k == 0:
                for j in (1, 2): d.line([(x - 24 + 16 * j, 660 + o), (x - 24 + 16 * j, 704 + o)], fill=wt, width=3); d.line([(x - 24, 660 + o + 15 * j), (x + 24, 660 + o + 15 * j)], fill=wt, width=3)
        d.rectangle((0, GRID_Y - 8, 358, GRID_Y - 4), fill=wt)
        T = tiles()
        for i, tl in enumerate(T):
            x, y, w, h = tile_rect(i)
            if i in holes: d.rectangle((x, y, x + w - 1, y + h - 1), fill=(4, 4, 6)); continue
            im.paste(tl, (x, y))
        return im
    return E.cached(('s03_page', tuple(holes)), mk)


def page_view(holes, blur):
    """top 1920 px of the page, blurred by `blur` (blend of cached radii)."""
    def mk(r):
        im = page(holes).crop((0, 0, W, H))
        return im.filter(ImageFilter.GaussianBlur(r)) if r else im
    R = [0, 3, 7]
    blur = clamp(blur, 0, R[-1])
    for a, b in zip(R, R[1:]):
        if blur <= b:
            ia = E.cached(('s03_pv', tuple(holes), a), lambda: mk(a)); ib = E.cached(('s03_pv', tuple(holes), b), lambda: mk(b))
            k = (blur - a) / (b - a)
            return ia if k < .02 else ib if k > .98 else Image.blend(ia, ib, k)


def ig_card(content, likes, w=760, sticker=False):
    """IG post card: rounded, neutral avatar, '<likes> likes', baked shadow. Returns RGBA."""
    c = E.ig_post(content, USER, w)
    d = ImageDraw.Draw(c)
    d.ellipse((20, 17, 90, 87), fill=(16, 16, 20)); d.ellipse((22, 19, 88, 85), fill=(70, 70, 78))
    ih = c.height - 104 - 120
    d.text((26, 104 + ih + 74), f'{likes} likes', font=E.font(28, 700), fill=(235, 235, 240))
    c = E.rounded(c, 26)
    if sticker:   # die-cut white sticker border
        pad = 18; big = Image.new('RGBA', (c.width + 2 * pad, c.height + 2 * pad), (0, 0, 0, 0)); big.alpha_composite(c, (pad, pad))
        a = big.getchannel('A').filter(ImageFilter.MaxFilter(2 * 15 + 1)).filter(ImageFilter.GaussianBlur(1.2))
        wb = Image.new('RGBA', big.size, (252, 252, 250, 0)); wb.putalpha(a); wb.alpha_composite(big); c = wb
    return E.shadow(c, blur=26, opacity=.7, offset=(0, 22))


def blurry_card(r):
    def mk():
        bl = E.asset('bad_blurry_photo')
        return ig_card(bl.filter(ImageFilter.GaussianBlur(r)) if r else bl, 3)
    return E.cached(('s03_blur', r), mk)


def shaky_frame():
    return E.cached('s03_shk_frame', lambda: ig_card(Image.new('RGB', (896, 1120), (0, 0, 0)), 5))


def flyer_card():
    return E.cached('s03_flyer', lambda: ig_card(E.asset('bad_flyer'), 2, sticker=True))


def starburst():
    def mk():
        S = 300; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = []
        for k in range(32):
            a = k * math.pi / 16; r = (S * .48) if k % 2 == 0 else (S * .36)
            pts.append((S / 2 + r * math.cos(a), S / 2 + r * math.sin(a)))
        d.polygon(pts, fill=(255, 226, 0), outline=(20, 20, 20)); d.line(pts + [pts[0]], fill=(20, 20, 20), width=6)
        for txt, sz, y in (('5 MIN', 78, S / 2 - 34), ('DESIGN!', 44, S / 2 + 42)):
            f = anton(sz); l, t, r, b = f.getbbox(txt)
            d.text((S / 2 - (r - l) / 2 - l, y - (b - t) / 2 - t), txt, font=f, fill=(225, 20, 30), stroke_width=3, stroke_fill=(255, 255, 255))
        return E.shadow(im, blur=14, opacity=.6, offset=(0, 10))
    return E.cached('s03_burst', mk)


# ---------------------------------------------------------------- camera helpers
def o2w(cam, ox, oy):
    """output pixel -> world pixel for a camera dict (no roll)."""
    return cam['x'] + (ox - cam['x'] - cam['dx']) / cam['z'], cam['y'] + (oy - cam['y'] - cam['dy']) / cam['z']


def put_card(ctx, layer, img, wx, wy, rx=0., ry=0., rz=0., s=1., vel=(0, 0), alpha=1.):
    im, cx, cy = persp(img, rx, ry, rz, s)
    ox = oy = 0
    if abs(vel[0]) + abs(vel[1]) > 2: im, ox, oy = mblur(im, vel[0], vel[1])
    ctx.add(layer, im, wx - cx - ox, wy - cy - oy, center=False, alpha=alpha)


# ---------------------------------------------------------------- per-segment card states (pure functions of t)
def blurry_state(t):
    """(wx, wy, rx, ry, rz, s, alpha) of the blurry card, or None."""
    x, y, w, h = tile_rect(0); tx, ty = x + w / 2, y + h / 2
    ts = 760 * .75; s0 = w / ts * 1.0          # start: card content ~ tile width
    cam = cam4(T4 + .3)
    lx, ly = o2w(cam, 285, 870); ls = 530 / cam['z'] / 760
    if t < T4 + .04: return None
    if t < W_BLURRY + .02:
        u = (t - T4 - .04) / (W_BLURRY + .02 - T4 - .04); k = eout(u)
        arc = math.sin(math.pi * u)
        return (lerp(tx, lx, k), lerp(ty, ly, k) - 60 * arc, lerp(0, -8, k) + 14 * arc, lerp(0, 16, k) + 22 * arc,
                lerp(0, -4, k) - 8 * arc, lerp(s0 * .62, ls, back(u, 1.6)), clamp(u / .12))
    if t < T5:     # floating, gently breathing
        lt = t - W_BLURRY
        return (lx + 4 * math.sin(lt * 2.1), ly + 6 * math.sin(lt * 1.7), -8 + 2 * math.sin(lt * 1.3), 16 - 3 * math.sin(lt * 1.1),
                -4 + .8 * math.sin(lt * 1.9), ls * (1 + .012 * lt), 1)
    if t < T5 + .2:   # thrown out to the left (in the new framing)
        u = (t - T5) / .2; k = ein(u)
        return (lx - 900 * k, ly - 200 * k, -8, 16 + 40 * k, -4 - 25 * k, ls, 1 - clamp((u - .7) / .3))
    return None


WHIP = .42      # TL3 whip-zoom settles to exactly z=1 (1:1, crisp page UI)
def cam3(t):
    u = clamp((t - T3) / WHIP); k = eout(u)
    if u >= 1: return dict(z=1.0, x=540., y=800., dx=0., dy=0., rot=0.)
    return dict(z=lerp(1.3, 1.0, k), x=540., y=800., dx=0., dy=0., rot=math.radians(lerp(-2.4, 0, k)))
# multicam: off-centre framings are camera pans (the plate never shows its borders), z >= 1.25
def cam4(t):    # medium, founder right
    lt = t - T4; z = 1.27 + .03 * smooth(lt / 1.16); return dict(z=z, x=540., y=820., dx=(z - 1) * 540 * .98, dy=40., rot=0.)
def cam5(t):    # tighter, founder left
    lt = t - T5; z = 1.40 + .03 * smooth(lt / 1.08); return dict(z=z, x=540., y=820., dx=-(z - 1) * 540 * .98, dy=60., rot=0.)
def cam6(t):    # low, founder bottom-right — headroom for the flyer
    lt = t - T6; z = 1.33 + .05 * smooth(lt / 1.84); return dict(z=z, x=540., y=820., dx=(z - 1) * 540 * .98, dy=(z - 1) * 820 * .55, rot=0.)


def grade(t):
    """(sat, bright) — every bad card drains the world."""
    sat = 1.0; br = 1.0
    for tw, ds, db in ((W_PAGE, .08, .02), (W_BLURRY, .14, .04), (W_SHAKY, .12, .04), (W_FLYER, .12, .04)):
        k = eout((t - tw) / .35); sat -= ds * k; br -= db * k
    return sat, br


def wrap_grade(sat, br, tint=(.97, .99, 1.04)):
    m = np.array(tint, np.float32) * br
    def f(fr):
        a = np.asarray(fr.convert('RGB'), np.float32)
        g = a.mean(2, keepdims=True); a = (g + (a - g) * sat) * m
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return f


DIVE = .13          # first 4 frames: the frame grows out of s02's phone screen (640x1328 @ 540,800)
PH_RECT = (220, 136, 860, 1464)


def dive(fr, u):
    """frame scaled from the phone-screen rectangle to full frame over a blurred, purple-dark copy of itself."""
    k = eout(clamp(u))
    x0, y0, x1, y1 = (lerp(a, b, k) for a, b in zip(PH_RECT, (0, 0, W, H)))
    w, h = int(round(x1 - x0)), int(round(y1 - y0))
    if w >= W - 2: return fr
    fr = fr.convert('RGB')
    bgk = fr.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    bgk = Image.blend(bgk, Image.new('RGB', (W, H), (34, 18, 70)), .55)
    inner = fr.resize((w, h), Image.BILINEAR).convert('RGBA')
    r = int(lerp(64, 0, k)); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    inner.putalpha(m); out = bgk.convert('RGBA'); out.alpha_composite(inner, (int(round(x0)), int(round(y0))))
    return out


# ---------------------------------------------------------------- draw
def draw(ctx, lt, t):
    sat, br = grade(t)
    ctx.wrap = wrap_grade(sat, br)
    ctx.post['vignette'] = .32 + .25 * (1 - sat)

    if t < T4:
        # ---- TL3: dive out of the s02 phone into their profile; the page flick-scrolls and bounces onto the header on "page"
        ctx.cam = cam3(t)
        def off(tt):
            u = (tt - T3) / (W_PAGE + .05 - T3)
            return 1650 * (1 - back(u, 1.25)) if u < 1 else -18 * math.exp(-(tt - W_PAGE - .05) * 9) * math.cos((tt - W_PAGE - .05) * 18)
        o = off(t); v = off(t) - off(t - 1 / 30)
        P = page(); oi = int(round(o))
        if oi >= 0: bg = P.crop((0, oi, W, oi + H))
        else:
            bg = Image.new('RGB', (W, H), (10, 10, 13)); bg.paste(P.crop((0, 0, W, H + oi)), (0, -oi))
        k = abs(v)
        if k > 3:   # vertical motion blur of the scroll
            f = clamp(k / 3.2, 1, 22); bg = bg.resize((W, int(H / f)), Image.BOX).resize((W, H), Image.BILINEAR)
        ctx.bg_img = bg; ctx.bg_dim = .1
        # founder sits low so the whole header (name, stats, Follow / Message) reads above his head
        ctx.avatar.update(y=290. + 40 * (1 - eout((t - T3) / WHIP)))
        ctx.post['zoom_blur'] = 1.1 * (1 - clamp((t - T3) / .09))
        if t < T3 + .065: ctx.captions = False      # no smeared caption (or s02's last page) inside the dive
        if t < T3 + DIVE:
            g = ctx.wrap; ctx.wrap = lambda fr: dive(g(fr), (t - T3) / DIVE)
        return

    # TL4..6: the page wall stays behind him, out of focus (multicam = camera framings, see cam4..6)
    holes = tuple(i for i, tt in ((0, T4 + .04), (2, T5 + .03)) if t >= tt)
    if t < T5:
        ctx.cam = cam4(t)
        ctx.bg_img = page_view(holes, 7 * eout((t - T4 - .05) / .45)); ctx.bg_dim = .25 * eout((t - T4) / .4)
    elif t < T6:
        ctx.cam = cam5(t)
        ctx.bg_img = page_view(holes, 7); ctx.bg_dim = .3
    else:
        ctx.cam = cam6(t)
        ctx.bg_img = page_view(holes, 7); ctx.bg_dim = .5

    # ---- blurry photo: hunts for focus forever
    st = blurry_state(t)
    if st is not None:
        wx, wy, rx, ry, rz, s, al = st
        lt_ = t - W_BLURRY
        r = 9 + 5 * math.sin(lt_ * 2 * math.pi * 1.6) * (1 if lt_ > 0 else 0)   # try to focus, fail, try again
        if lt_ < 0: r = 11
        R = [2, 5, 8, 11, 14]; r = clamp(r, R[0], R[-1])
        i = min(len(R) - 2, max(0, int((r - R[0]) // 3))); k = (r - R[i]) / 3
        card = Image.blend(blurry_card(R[i]), blurry_card(R[i + 1]), clamp(k)).copy()
        if 0 <= lt_ and t < T5:     # iPhone-style AF/AE box hunting: shrinks on every focus attempt, never locks
            d = ImageDraw.Draw(card); pad = (card.width - 760) // 2
            ph = (lt_ * 1.6) % 1.0
            cx, cy = pad + 400, pad + 104 + 500; hs = 150 * (1 - .18 * eout(ph / .35) + .18 * eout((ph - .55) / .45))
            col = (255, 214, 10, 255 if ph < .7 else 150)
            d.rectangle((cx - hs, cy - hs, cx + hs, cy + hs), outline=col, width=5)
            tk = 20
            for (ax, ay, bx, by) in ((cx, cy - hs, cx, cy - hs + tk), (cx, cy + hs, cx, cy + hs - tk),
                                     (cx - hs, cy, cx - hs + tk, cy), (cx + hs, cy, cx + hs - tk, cy)):
                d.line([(ax, ay), (bx, by)], fill=col, width=5)
            sx, sy = cx + hs + 40, cy + 40 * math.sin(lt_ * 4.1)           # exposure sun on its slider
            d.line([(sx, cy - hs), (sx, sy - 26)], fill=col, width=3); d.line([(sx, sy + 26), (sx, cy + hs)], fill=col, width=3)
            d.ellipse((sx - 11, sy - 11, sx + 11, sy + 11), outline=col, width=4)
            for j in range(8):
                ang = j * math.pi / 4; d.line([(sx + 16 * math.cos(ang), sy + 16 * math.sin(ang)), (sx + 22 * math.cos(ang), sy + 22 * math.sin(ang))], fill=col, width=3)
        vel = (0, 0)
        if t >= T5: vel = (-900 * (ein((t - T5) / .2) - ein((t - T5 - 1 / 30) / .2)), 0)
        put_card(ctx, 'front', card, wx, wy, rx, ry, rz, s, vel, al)

    # ---- shaky video: tears out of the grid BEHIND him, shakes, plays
    if T5 + .03 <= t < T6 + .2:
        x, y, w, h = tile_rect(2); tx, ty = x + w / 2, y + h / 2
        cam = cam5(T5 + .4); lx, ly = o2w(cam, 785, 800); ls = 570 / cam['z'] / 760
        if t < W_SHAKY + .02:
            u = (t - T5 - .03) / (W_SHAKY + .02 - T5 - .03); k = eout(u)
            wx, wy, s = lerp(tx, lx, k), lerp(ty, ly, k), lerp(w / 760 * .9, ls, back(u, 1.8))
            rx, ry, rz = 10 * math.sin(math.pi * u), lerp(0, -14, k), lerp(0, 3, k); al = clamp(u / .15)
        else:
            wx, wy, s, rx, ry, rz, al = lx, ly, ls, 0, -14, 3, 1
        sk = 1.0 if t < T6 else 1.0
        lt_ = t - T5
        amp = (1.0 + 1.6 * math.exp(-max(0, t - W_SHAKY) * 6)) * sk
        jx = 16 * amp * noise(lt_, 1.0); jy = 12 * amp * noise(lt_, 2.3); jr = 2.2 * amp * noise(lt_, 3.1, (5.1, 9.7, 13.3))
        jx1 = 16 * amp * noise(lt_ - 1 / 30, 1.0); jy1 = 12 * amp * noise(lt_ - 1 / 30, 2.3)
        vel = (jx - jx1, jy - jy1)
        if t >= T6:
            u = (t - T6) / .2; k = ein(u); wx += 1100 * k; wy -= 160 * k; ry -= 40 * k; rz += 20 * k; al *= 1 - clamp((u - .7) / .3)
            vel = (vel[0] + 1100 * (k - ein((t - T6 - 1 / 30) / .2)), vel[1])
        # the footage itself shakes inside the card
        sh = E.asset('bad_shaky_video')
        ix = 33 + 30 * noise(lt_ * 1.3, 5.2); iy = 11 + 11 * noise(lt_ * 1.3, 6.1)
        cont = sh.crop((int(ix), int(iy), int(ix) + 830, int(iy) + 1037)).rotate(1.6 * noise(lt_, 7.7), Image.BILINEAR)
        cont = cont.resize((760, 950), Image.BILINEAR)
        cont = cont.crop((0, 0, 760, 950))
        # progress bar
        dd = ImageDraw.Draw(cont); prog = clamp(.18 + (t - T5) * .11)
        dd.rectangle((0, 935, 760, 950), fill=(0, 0, 0)); dd.rectangle((0, 941, 760, 946), fill=(120, 120, 128))
        dd.rectangle((0, 941, int(760 * prog), 946), fill=(250, 250, 250)); dd.ellipse((int(760 * prog) - 9, 934, int(760 * prog) + 9, 952), fill=(255, 255, 255))
        card = shaky_frame().copy(); pad = (card.width - 760) // 2
        card.paste(cont, (pad, pad + 104))
        put_card(ctx, 'behind', card, wx + jx, wy + jy, rx, ry, rz + jr, s, vel, al)
        if abs(t - W_SHAKY) < .12:
            ctx.post['rgb'] = 9 * (1 - abs(t - W_SHAKY) / .12); ctx.post['glitch'] = .35 * (1 - abs(t - W_SHAKY) / .12)

    # ---- flyer: slams in crooked like a cheap sticker
    if t >= T6 + .08:
        cam = cam6(W_FLYER); lx, ly = o2w(cam, 305, 700); ls = 470 / cam['z'] / (760 + 36)
        u = (t - T6 - .08) / (W_FLYER - T6 - .08)
        if u < 1:
            k = ein(u)
            s = lerp(ls * 2.6, ls, k); rz = lerp(-28, -8, k); rx = lerp(-35, 0, k); ry = lerp(25, 6, k)
            wx, wy = lerp(lx - 150, lx, k), lerp(ly - 500, ly, k); al = clamp(u / .25); sy = 1
            vel = (0, 0)
        else:
            lt_ = t - W_FLYER
            wob = math.exp(-lt_ * 7) * math.sin(lt_ * 2 * math.pi * 4.2)      # boing
            s = ls * (1 + .07 * wob); rz = -8 + 4 * wob; rx = 0; ry = 6 + 2 * math.sin(lt_ * 1.4); wx, wy = lx, ly + 3 * math.sin(lt_ * 1.6); al = 1
            vel = (0, 0)
            sh_ = 16 * math.exp(-lt_ * 10) * math.sin(lt_ * 2 * math.pi * 7)          # the camera takes the hit
            ctx.cam['dx'] += sh_; ctx.cam['dy'] += sh_ * .7
            ctx.post['flash'] = .18 * clamp(1 - lt_ / .08); ctx.post['flash_col'] = (255, 240, 200)
        put_card(ctx, 'front', flyer_card(), wx, wy, rx, ry, rz, s, vel, al)
        if t >= W_FIVE:     # 5 MIN sticker on the flyer's corner
            lt_ = t - W_FIVE; k = back(lt_ / .22, 3.0)
            b = starburst(); sc = 1.0 * k
            if sc > .02:
                im = b.rotate(lerp(-40, 14, eout(lt_ / .25)) + 2 * math.sin(lt_ * 5), Image.BICUBIC, expand=True)
                im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
                bx, by = o2w(cam, 530, 380)
                ctx.add('front', im, bx, by, alpha=clamp(lt_ / .05))
