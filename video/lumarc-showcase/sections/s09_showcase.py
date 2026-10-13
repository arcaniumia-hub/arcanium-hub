"""s09 — THE PORTFOLIO (37.28–48.16). Four framings, one per promise; every mockup lands on its word.
Own caption track (engine look) on measured onsets; founder drawn with feathered plate borders (no cut lines);
studio truck is self-covering (no exposed plate edge).

A  TL22 "We turn the photos and videos you already have into Reels that stop the scroll..."  (37.28–41.76)
   37.28  multicam snap out of s08's tight logo framing (z 1.36) into a wider truck: founder slides right / smaller.
   37.93  "PHOTOS"  a blurry phone photo flies in from depth (3D card, BEFORE chip).
   38.58  "VIDEOS"  a shaky video card swipes in behind it, jittering.
   39.08  "ALREADY" a 52 px light band (brand gradient, white-hot core, flare) sweeps down: a soft 30 px wipe turns
          what it passed premium (blurry -> close_food, shaky -> close_service) with a prism fringe on the boundary,
          light spill on the cards and a 1.04 pop as it crosses each card; the chip flips to AFTER the instant the
          band core crosses it (T_CHIP ~39.57).
   39.95  "INTO REELS" a phone spins in (perspective Y-spin, LUMARC back face, motion blur) and lands on "REELS"
          40.28 playing the SILENCE ONE film under a Reels UI; a phone-shaped light pulse hugs it.
   40.70  "THAT STOP" a fingertip ring drags the reel up (trail; next post is a cheap flyer)... 41.01 "STOP" snaps back.
   41.46  "SCROLL"  double-tap heart.
B  TL23 "carousels people save..."  (41.76–43.12)  founder left, tighter. A glass carousel card turns in from
   the right, swipes slide 1 -> 2 on "PEOPLE" 42.40, bookmark fills + ping + 'Saved' glass pill pops above on "SAVE" 42.85.
C  TL24 "designs that look like a big brand made them..."  (43.12–45.40)  wide, founder right. The poster is a
   lightbox on the studio wall BEHIND him: a real light pool (multiplicative + bounce) flickers on at "DESIGNS" 43.15,
   camera punches in on "BIG" 44.35, sheen on "BRAND" 44.62, "Made by LUMARC" types on from BRAND and holds.
D  TL25 "and a website that turns followers into customers."  (45.40–48.16)  founder centred behind a perspective
   laptop (lid tilted back, trapezoid deck, lip, contact shadow, glass sweep) that rises and lands on "WEBSITE" 45.67;
   the site scrolls, the cursor clicks "Book a table" 46.42, 'New booking' drops onto the screen-top edge 46.52,
   followers card left of his head on "FOLLOWERS" 46.75, counter lands + gradient pulse on "CUSTOMERS" 47.53,
   then a push-in (z -> 1.24) so the 48.16 cut to s10 (z 1.06) reads as a pull-out; the card parallaxes out left
   as a foreground layer (faster than his head, blurring, gone by ~47.95) so it never crosses his ear.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
import engine as E

START, END = E.span(22, 25)              # 37.28 – 48.16
T23, T24, T25 = E.TL[23]['t0'], E.TL[24]['t0'], E.TL[25]['t0']   # 41.76, 43.12, 45.40 jump cuts

# word onsets measured on the voice track (src/voice16k.raw is float32 16 kHz of the SOURCE take; mapped through
# timeline.SEG; 300-3000 Hz envelope, 10 ms hop)
W_TURN, W_PHOTOS, W_VIDEOS, W_ALREADY, W_HAVE = 37.52, 37.93, 38.58, 39.04, 39.92
W_INTO, W_REELS, W_THAT, W_STOP, W_SCROLL = 40.10, 40.27, 40.64, 41.01, 41.46
W_CAROUSELS, W_PEOPLE, W_SAVE = 41.84, 42.41, 42.85
W_DESIGNS, W_LOOK, W_BIG, W_BRAND, W_MADE = 43.17, 43.72, 44.35, 44.62, 45.05
W_AND2, W_WEBSITE, W_TURNS, W_FOLLOWERS, W_INTO2, W_CUSTOMERS = 45.46, 45.67, 46.36, 46.75, 47.28, 47.53

# own caption track (engine captions are syllable estimates that trail the hero words by up to 8 frames):
# same look as the engine (E._layout + E.word_img), but every word pops on its measured onset.  '*' = emphasis.
CAPS = [
    [('WE', 37.36), ('TURN', 37.52), ('THE', 37.72), ('PHOTOS', 37.93)],
    [('AND', 38.46), ('VIDEOS', 38.58)],
    [('YOU', 39.02), ('ALREADY', 39.14), ('HAVE', 39.92)],
    [('INTO', 40.10), ('*REELS', 40.27)],
    [('THAT', 40.64), ('STOP', 41.01), ('THE', 41.22), ('SCROLL...', 41.43)],
    [('*CAROUSELS', 41.84)],
    [('PEOPLE', 42.41), ('SAVE...', 42.85)],
    [('*DESIGNS', 43.17), ('THAT', 43.46), ('LOOK', 43.72)],
    [('LIKE', 43.98), ('A', 44.10), ('BIG', 44.35), ('BRAND', 44.62)],
    [('MADE', 45.05), ('THEM...', 45.24)],
    [('AND', 45.46), ('A', 45.58), ('*WEBSITE', 45.67)],
    [('THAT', 46.18), ('TURNS', 46.36), ('FOLLOWERS', 46.75)],
    [('INTO', 47.28), ('*CUSTOMERS.', 47.53)],
]

# choreography times
TRUCK0 = 37.30
SCAN0, SCAN1 = W_ALREADY + .04, W_ALREADY + .78
SPIN0, SPIN1 = 39.95, W_REELS + .01
FLIP0 = SPIN0 - .09
DRAG0, DRAG1 = 40.70, W_STOP
CAR_IN0, CAR_IN1 = T23, T23 + .22
SWIPE0 = 42.40
POWER = W_DESIGNS - .02
LAP0, LAP1 = T25 - .02, W_WEBSITE + .02
SCROLL0, SCROLL1 = 45.86, 46.30
CLICK = 46.42
NOTIF = 46.52

CREDIT0 = W_BRAND + .02                 # "Made by LUMARC" types on from BRAND

CUES = [
    (START, 'swipe', {'gain': -8}),                    # multicam snap out of the logo framing
    (TRUCK0, 'whoosh', {'gain': -10}),                 # camera trucks, logo lifts
    (W_PHOTOS - .04, 'whoosh', {'gain': -4}),          # blurry photo flies in
    (W_PHOTOS + .04, 'pop', {'gain': -8}),
    (W_VIDEOS - .06, 'swipe', {}),                     # shaky video card
    (SCAN0 - .02, 'shimmer', {}),                      # scanning light band
    (SCAN0, 'riser', {'to': SCAN1}),
    (SPIN0, 'swoosh_up', {}),                          # phone spins in
    (W_REELS, 'impact', {}),                           # lands on REELS
    (DRAG0, 'swipe', {'gain': -6}),                    # finger drags the reel
    (W_STOP, 'impact', {'gain': -2}),                  # STOP — snaps back
    (W_SCROLL, 'heart', {}),                           # double-tap heart
    (T23 - .03, 'glass', {}),                          # carousel card turns in
    (T23, 'whoosh', {'gain': -8}),
    (SWIPE0, 'swipe', {}),                             # slide 1 -> 2
    (W_SAVE, 'pop', {}),                               # bookmark fills + Saved pill pops
    (W_SAVE + .06, 'notify', {'gain': -8}),
    (POWER, 'impact', {'gain': -6}),                   # lightbox powers on
    (POWER + .07, 'tick', {'gain': -8}),               # flicker
    (POWER + .15, 'tick', {'gain': -10}),
    (W_BIG, 'whoosh', {'gain': -10}),                  # punch-in on BIG
    (W_BRAND, 'shimmer', {}),                          # light sweep
    (CREDIT0 + .00, 'type', {'gain': -9}),             # credit types on
    (CREDIT0 + .08, 'type', {'gain': -10}),
    (CREDIT0 + .16, 'type', {'gain': -10}),
    (CREDIT0 + .24, 'type', {'gain': -10}),
    (LAP0, 'whoosh', {'gain': -4}),                    # laptop rises
    (W_WEBSITE, 'impact', {'gain': -6}),
    (SCROLL0, 'swoosh_up', {'gain': -10}),             # page scroll
    (CLICK, 'click', {}),                              # Book a table
    (NOTIF, 'notify', {}),                             # New booking
    (W_FOLLOWERS, 'pop', {'gain': -6}),                # followers card
    (W_FOLLOWERS + .2, 'riser', {'to': W_CUSTOMERS}),  # counter rolls
    (W_CUSTOMERS, 'cash', {}),                         # customers land
    (W_CUSTOMERS + .25, 'whoosh', {'gain': -14}),      # slow push-in out of the section
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H
WHITE, MUTED = E.WHITE, E.MUTED


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def cub(x): x = clamp(x); return 1 - (1 - x) ** 3
def quint(x): x = clamp(x); return 1 - (1 - x) ** 5
def inout(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def C(k, fn): return E.cached(('s09',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def spring(x, freq=2.2, damp=6.0):
    """0 -> 1 with a damped overshoot (x in seconds-normalised units)."""
    if x <= 0: return 0.0
    return 1 - math.exp(-damp * x) * math.cos(freq * math.pi * x)


# ================================================================ 3D projection (true perspective)
def _coeffs(dst, src):
    """PIL PERSPECTIVE coefficients mapping output points `dst` -> input points `src`."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, np.float64), np.array(B, np.float64)).tolist()


def project(w, h, ry=0., rx=0., rz=0., s=1., f=2400.):
    """projected 2D corners (TL, TR, BR, BL) of a w x h card centred at the origin."""
    pts = []
    cz, sz = math.cos(rz), math.sin(rz); cx_, sx_ = math.cos(rx), math.sin(rx); cy_, sy_ = math.cos(ry), math.sin(ry)
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        x, y = x * cz - y * sz, x * sz + y * cz                   # roll
        y, z = y * cx_, y * sx_                                     # tilt (top away for rx > 0)
        x, z = x * cy_ + z * sy_, -x * sy_ + z * cy_                # yaw
        k = f / (f + z) * s; pts.append((x * k, y * k))
    return pts


def persp(img, ry=0., rx=0., rz=0., s=1., f=2400.):
    """warp RGBA `img` (rotated in 3D about its centre, perspective). Returns (im, (ox, oy), front_facing):
    (ox, oy) = where the card centre lands inside `im`."""
    p = 2
    src = Image.new('RGBA', (img.width + 2 * p, img.height + 2 * p), (0, 0, 0, 0)); src.paste(img, (p, p))
    q = project(src.width, src.height, ry, rx, rz, s, f)
    xs = [a for a, _ in q]; ys = [b for _, b in q]
    x0, y0 = math.floor(min(xs)), math.floor(min(ys)); ow, oh = math.ceil(max(xs)) - x0 + 1, math.ceil(max(ys)) - y0 + 1
    (ax, ay), (bx, by), (cx, cy) = q[0], q[1], q[2]
    front = ((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) > 0
    if ow < 3 or oh < 3: return None, (0, 0), front
    dst = [(x - x0, y - y0) for x, y in q]
    srcp = [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)]
    co = _coeffs(dst, srcp)
    im = src.transform((ow, oh), Image.PERSPECTIVE, co, Image.BILINEAR)
    return im, (-x0, -y0), front


def add3d(ctx, layer, img, x, y, ry=0., rx=0., rz=0., s=1., alpha=1., glass=0, f=2400.):
    im, (ox, oy), front = persp(img, ry, rx, rz, s, f)
    if im is None: return front
    ctx.add(layer, im, x - ox, y - oy, center=False, alpha=alpha, glass=glass)
    return front


def bright(img, k):
    """scale RGB of an RGBA image (keeps alpha)."""
    if abs(k - 1) < .01: return img
    a = img.getchannel('A'); rgb = Image.eval(img.convert('RGB'), lambda v: int(min(255, v * k)))
    out = rgb.convert('RGBA'); out.putalpha(a); return out


def cover(img, w, h, ay=.5):
    c = img.convert('RGB'); sc = max(w / c.width, h / c.height)
    c = c.resize((max(w, int(c.width * sc + .999)), max(h, int(c.height * sc + .999))), Image.LANCZOS)
    x0 = (c.width - w) // 2; y0 = int((c.height - h) * ay)
    return c.crop((x0, y0, x0 + w, y0 + h))


def glow_dot(r, col, a=1.0):
    def mk():
        n = int(r * 4); yy, xx = np.mgrid[0:n, 0:n].astype(np.float32); d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / r
        al = np.exp(-d ** 2 * 1.2)
        im = Image.new('RGBA', (n, n), col + (0,)); im.putalpha(Image.fromarray((al * 255 * a).astype(np.uint8))); return im
    return C(('glow', r, col, a), mk)


# ================================================================ A: before/after cards
CARD_W, CARD_H, CARD_R = 430, 538, 26
CARD_X, CARD_Y = 300, 930
VID_W, VID_H = 380, 475


def card_art(name, w, h, after=False):
    def mk():
        src = E.asset(name)
        im = cover(src, w, h, .5 if not after else .45).convert('RGBA')
        if not after:     # the "before" grade: flat, a touch grey
            g = Image.eval(im.convert('RGB'), lambda v: int(v * .9 + 10)); im = g.convert('RGBA')
        im = E.rounded(im, CARD_R)
        b = Image.new('L', (w, h)); ImageDraw.Draw(b).rounded_rectangle((1, 1, w - 2, h - 2), CARD_R, outline=255, width=2)
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [b.point(lambda v: int(v * .38))]))
        return im
    return C(('card', name, w, h, after), mk)


def chip(text, grad):
    return C(('chip', text, grad), lambda: E.pill(text, 34, 800, fill=(18, 18, 26, 225), fg=WHITE if grad else (200, 200, 212),
                                                  padx=24, pady=12, grad=grad))


BAND_FEATHER = 30          # px: soft edge of the before -> after wipe


def _farr(img):
    return np.asarray(img, np.float32)


def _beam_cols(w):
    """per-column beam colour: brand gradient #4f6bff -> #9a4dff across the band."""
    def mk():
        x = np.linspace(0, 1, w, dtype=np.float32)[:, None]
        a, b, c = (np.array(v, np.float32) for v in E.GRAD)
        return np.where(x < .5, a + (b - a) * (x * 2), b + (c - b) * (x * 2 - 1))
    return C(('beamcols', w), mk)


def scan_card(bname, aname, w, h, by, after_ay=True):
    """card with the light band at local row `by`: rows above it are already premium (soft 30 px wipe), with a
    prism fringe on the boundary and the band's light spilling onto the card."""
    before = card_art(bname, w, h); after = card_art(aname, w, h, True)
    if by <= -70: return before
    if by >= h + 70: return after
    B = C(('farr', bname, w, h), lambda: _farr(before)); A = C(('farr', aname, w, h, 1), lambda: _farr(after))
    yy = np.arange(h, dtype=np.float32)[:, None, None]
    m = np.clip((by - yy) / BAND_FEATHER + .5, 0, 1); m = m * m * (3 - 2 * m)
    out = B + (A - B) * m
    d = yy - by
    # prism fringe on the boundary: red lags, blue leads (vertical chromatic split, only inside the band)
    band = np.exp(-(d / 26) ** 2)[..., 0]
    r = np.roll(out[..., 0], 7, 0); bl = np.roll(out[..., 2], -7, 0)
    out[..., 0] += (r - out[..., 0]) * band; out[..., 2] += (bl - out[..., 2]) * band
    # light spill: brand-gradient glow + white-hot core
    col = _beam_cols(w)[None, :, :]
    halo = np.exp(-(d / 80) ** 2) * .38 + np.exp(-(d / 24) ** 2) * .55
    core = np.exp(-(d / 5) ** 2)
    rgb = out[..., :3]
    rgb = rgb + col * halo * .9
    rgb = rgb + (255 - rgb) * np.clip(core * 1.1, 0, 1)
    out = np.dstack([np.clip(rgb, 0, 255), A[..., 3:]])
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def beam_img(w):
    """world-space light band: 52 px glowing band in the brand gradient, white-hot core, wide soft halo,
    anamorphic flare tails; fades out before it reaches his face."""
    def mk():
        hh = 420; yy = np.linspace(-hh / 2, hh / 2, hh, dtype=np.float32)[:, None]
        xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
        ends = np.clip((1 - xx) / .30, 0, 1) ** 1.5                                   # soft right end (stops before his face)
        band = np.exp(-(np.abs(yy) / 26) ** 4)                                         # ~52 px flat-topped band
        core = np.exp(-(yy / 4.5) ** 2)
        halo = np.exp(-(yy / 120) ** 2) * .30 + np.exp(-(yy / 50) ** 2) * .35
        flare = np.exp(-(yy / 2.2) ** 2) * np.exp(-((xx - .38) / .30) ** 2) * .9
        al = np.clip(band * .82 + core + halo + flare, 0, 1) * ends
        cols = _beam_cols(w).reshape(1, w, 3)
        hot = np.clip(core * 1.2 + flare + band * .18, 0, 1)[..., None]
        col = cols + (255 - cols) * hot
        im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
        return im
    return C(('beam2', w), mk)


BEAM_Y0, BEAM_Y1 = 250, 1290
def beam_y(t): return lerp(BEAM_Y0, BEAM_Y1, inout((t - SCAN0) / (SCAN1 - SCAN0)))


CHIP_H = 88                                        # pill height (E.pill 34 px, pady 12)
CHIP_CY = CARD_H - CHIP_H / 2 - 6                  # chip centre row in card-local coords
def _chip_flip_t():
    """time the band core crosses the chip centre (card has landed: top edge at CARD_Y - CARD_H/2)."""
    lo, hi = SCAN0, SCAN1
    for _ in range(40):
        m = (lo + hi) / 2
        if beam_y(m) - (CARD_Y - CARD_H / 2) < CHIP_CY: lo = m
        else: hi = m
    return round(hi, 4)
T_CHIP = _chip_flip_t()                            # ~39.57: chip flips BEFORE -> AFTER as the band passes it
def _cross_t(y):
    lo, hi = SCAN0, SCAN1
    for _ in range(40):
        m = (lo + hi) / 2
        if beam_y(m) < y: lo = m
        else: hi = m
    return round(hi, 4)
CUES += [
    (_cross_t(545), 'pop', {'gain': -10}),             # video card swells as the band crosses its centre
    (T_CHIP, 'pop', {}),                               # photo card: chip flips to AFTER as the band crosses it
]


def draw_cards(ctx, t):
    """the before/after card pair (world 'front' layer)."""
    if t < W_PHOTOS - .12: return
    by = beam_y(t) if t >= SCAN0 - .05 else -1e9
    rec = cub((t - (SPIN0 + .02)) / .45)                            # recede behind the arriving phone
    dof = rec
    # ---- video card (behind)
    if t >= W_VIDEOS - .10:
        k = expo((t - (W_VIDEOS - .10)) / .5)
        x = lerp(-260, 410, k); y = lerp(500, 545, k)
        ry = math.radians(lerp(55, -14, k)); rz = math.radians(lerp(-8, 4, k))
        cy0 = y - VID_H / 2
        frac = clamp((by - cy0) / VID_H)
        shake = 1 - clamp(frac * 1.4)
        fi = int(t * 30)
        x += shake * (hrand(fi, 1) - .5) * 14 * k; y += shake * (hrand(fi, 2) - .5) * 12 * k; rz += shake * (hrand(fi, 3) - .5) * .03 * k
        art = scan_card('bad_shaky_video', 'close_service', VID_W, VID_H, by - cy0)
        s = 1 + .045 * math.sin(math.pi * frac) if 0 < frac < 1 else 1.0          # pop as the band passes
        # recede
        x = lerp(x, 640, rec); y = lerp(y, 430, rec); s *= lerp(1, .72, rec); ry = lerp(ry, math.radians(16), rec)
        art = bright(art, lerp(1, .55, dof))
        if dof > .05: art = art.filter(ImageFilter.GaussianBlur(4 * dof))
        add3d(ctx, 'front', E.shadow(art, 26, .55, (0, 16)), x, y, ry, 0, rz, s, alpha=clamp((t - (W_VIDEOS - .10)) / .06))
    # ---- photo card (front)
    k = expo((t - (W_PHOTOS - .12)) / .55)
    x = lerp(470, CARD_X, k); y = lerp(1050, CARD_Y, k)
    s = lerp(.30, 1.0, k); ry = math.radians(lerp(-70, -10, k)); rx = math.radians(lerp(30, 0, k)); rz = math.radians(lerp(10, -3, k))
    cy0 = y - CARD_H / 2
    frac = clamp((by - cy0) / CARD_H)
    if 0 < frac < 1: s *= 1 + .04 * math.sin(math.pi * frac)
    art = scan_card('bad_blurry_photo', 'close_food', CARD_W, CARD_H, by - cy0).copy()
    aft = t >= T_CHIP
    ck = chip('AFTER' if aft else 'BEFORE', aft)
    pk = back((t - T_CHIP) / .22, 2.6) if aft else 1
    if abs(pk - 1) > .01: ck = ck.resize((max(1, int(ck.width * (.6 + .4 * pk))), max(1, int(ck.height * (.6 + .4 * pk)))), Image.BILINEAR)
    art.alpha_composite(ck, (int(14 + (chip('AFTER', True).width - ck.width) / 2), int(CARD_H - ck.height - 6)))
    if t < SPIN0:
        fk = ein((t - FLIP0) / (SPIN0 - FLIP0))                       # flips edge-on: the photo turns into the Reel
        ry = lerp(ry, math.radians(-90), fk); s *= lerp(1, 1.04, fk)
        art = bright(art, 1 + .5 * fk)
        add3d(ctx, 'front', E.shadow(art, 30, .6, (0, 20)), x, y, ry, rx, rz, s, alpha=clamp((t - (W_PHOTOS - .12)) / .06))
    # ---- the light band (world), over the cards
    if SCAN0 - .05 <= t <= SCAN1 + .14:
        a = clamp((t - (SCAN0 - .05)) / .08) * clamp((SCAN1 + .14 - t) / .14)
        ctx.add('front', beam_img(700), -20, by - 210, center=False, alpha=a)


# ================================================================ A: phone + Reels UI
PH_W = 480
PH_BEZ = int(PH_W * .035)
SCR_W, SCR_H = PH_W - 2 * PH_BEZ, int(PH_W * 2.05) - 2 * PH_BEZ
PH_X, PH_Y = 340, 820


def heart_mask(sz):
    def mk():
        n = sz * 4; im = Image.new('L', (n, n)); d = ImageDraw.Draw(im)
        pts = []
        for i in range(120):
            a = i / 120 * 2 * math.pi
            x = 16 * math.sin(a) ** 3; y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
            pts.append((n / 2 + x * n / 36, n / 2 + y * n / 36 - n * .02))
        d.polygon(pts, fill=255)
        return im.resize((sz, sz), Image.LANCZOS)
    return C(('heart', sz), mk)


def heart_img(sz, filled=True, col=(255, 60, 90), outline=False):
    def mk():
        m = heart_mask(sz)
        if outline:
            inner = m.filter(ImageFilter.MinFilter(5)); m2 = Image.fromarray(np.clip(np.asarray(m, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8))
            im = Image.new('RGBA', (sz, sz), col + (0,)); im.putalpha(m2); return im
        if col == 'grad':
            g = E.gradient(sz, sz, [(255, 90, 140), (230, 70, 200), (154, 77, 255)]).convert('RGBA'); g.putalpha(m); return g
        im = Image.new('RGBA', (sz, sz), col + (0,)); im.putalpha(m); return im
    return C(('heartimg', sz, filled, col, outline), mk)


def bookmark_img(sz, filled, grad=False):
    def mk():
        n = sz * 4; m = Image.new('L', (n, n)); d = ImageDraw.Draw(m)
        poly = [(n * .2, n * .08), (n * .8, n * .08), (n * .8, n * .92), (n * .5, n * .68), (n * .2, n * .92)]
        if filled: d.polygon(poly, fill=255)
        else: d.line(poly + [poly[0]], fill=255, width=int(n * .085), joint='curve')
        m = m.resize((sz, sz), Image.LANCZOS)
        if grad: im = E.gradient(sz, sz, E.GRAD_LIGHT).convert('RGBA')
        else: im = Image.new('RGBA', (sz, sz), (240, 240, 245, 255))
        im.putalpha(m); return im
    return C(('bm', sz, filled, grad), mk)


def reels_ui(liked):
    def mk():
        w, h = SCR_W, SCR_H
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        # scrims
        g = np.zeros((h, 1), np.float32); yy = np.arange(h, dtype=np.float32)[:, None]
        g += np.clip((yy - h * .68) / (h * .32), 0, 1) ** 1.4 * .78 + np.clip(1 - yy / (h * .14), 0, 1) ** 2 * .45
        sc = Image.fromarray((np.repeat(g, w, 1) * 255).astype(np.uint8)); im.putalpha(sc)
        d = ImageDraw.Draw(im)
        d.text((24, 62), 'Reels', font=E.font(32, 800), fill=WHITE)
        d.rounded_rectangle((w - 62, 64, w - 26, 94), 8, outline=WHITE, width=3); d.ellipse((w - 52, 71, w - 36, 87), outline=WHITE, width=3)
        # right rail
        rx = w - 46; y = int(h * .52)
        hi = heart_img(46, True, (255, 56, 92)) if liked else heart_img(46, False, (245, 245, 250), outline=True)
        im.alpha_composite(hi, (rx - 23, y)); f = E.font(21, 700)
        def lab(s, yy):
            l, tp, r, b = f.getbbox(s); d.text((rx - (r - l) / 2 - l, yy), s, font=f, fill=WHITE)
        lab('48.3K' if liked else '48.2K', y + 50)
        y += 104; d.ellipse((rx - 21, y, rx + 21, y + 40), outline=WHITE, width=3); d.polygon([(rx - 18, y + 30), (rx - 24, y + 46), (rx - 8, y + 38)], fill=WHITE)
        lab('1,204', y + 50)
        y += 104; d.polygon([(rx - 22, y + 4), (rx + 22, y + 18), (rx - 22, y + 34), (rx - 14, y + 18)], outline=WHITE, width=3)
        lab('3,981', y + 46)
        y += 96
        for i in range(3): d.ellipse((rx - 15 + i * 13, y, rx - 9 + i * 13, y + 6), fill=WHITE)
        # bottom-left
        by = h - 200
        av = E.gradient(52, 52, E.GRAD).convert('RGBA'); m = Image.new('L', (52, 52)); ImageDraw.Draw(m).ellipse((0, 0, 51, 51), fill=255); av.putalpha(m)
        im.alpha_composite(av, (22, by))
        d.text((86, by + 10), 'silence.one', font=E.font(26, 700), fill=WHITE)
        l, tp, r, b = E.font(26, 700).getbbox('silence.one')
        fx = 86 + r + 16; d.rounded_rectangle((fx, by + 6, fx + 92, by + 46), 10, outline=WHITE, width=2)
        d.text((fx + 14, by + 12), 'Follow', font=E.font(21, 700), fill=WHITE)
        d.text((22, by + 70), 'Hear nothing. Feel everything.', font=E.font(23, 500), fill=(235, 235, 240))
        d.text((22, by + 104), '♪ Original audio · SILENCE ONE', font=E.font(20, 500), fill=(205, 205, 215))
        return im
    return C(('reelsui', liked), mk)


def phone_back():
    def mk():
        w, h = PH_W, int(PH_W * 2.05); r = int(w * .16)
        g = np.linspace(0, 1, w, dtype=np.float32)[None, :]; v = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        base = 40 + 70 * np.exp(-((g - .28) * 3.2) ** 2) * (1 - .5 * v) + 18 * (1 - v)
        col = np.dstack([base * .80, base * .74, base * 1.25])
        im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA'); im = E.rounded(im, r)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), r, outline=(190, 180, 235, 255), width=4)
        d.rounded_rectangle((26, 26, 26 + 170, 26 + 170), 42, fill=(20, 20, 26, 255), outline=(80, 80, 95, 255), width=2)
        for cx, cy in ((70, 70), (70, 152), (152, 111)):
            d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(8, 8, 12, 255), outline=(95, 95, 115, 255), width=4)
            d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(30, 34, 60, 255))
        lg = E.logo(260); im.alpha_composite(lg, (w // 2 - lg.width // 2, h // 2 - lg.height // 2))
        return ImageOps.mirror(im)          # seen from behind
    return C('phback', mk)


def screen_content(t):
    """teardown film (+ the 'scroll' drag revealing the next post, and the double-tap heart)."""
    src_t = 3.70 + max(0.0, t - SPIN0)
    th = int(SCR_H * 1.0); tw = int(round(1080 * th / 1920))
    fr = E.clip(E.TEARDOWN, (tw if tw % 2 == 0 else tw + 1, th)).at(src_t)
    x0 = (fr.width - SCR_W) // 2
    reel = fr.crop((x0, 0, x0 + SCR_W, SCR_H)).convert('RGBA')
    liked = t >= W_SCROLL + .05
    reel.alpha_composite(reels_ui(liked))
    # progress bar
    d = ImageDraw.Draw(reel); pr = clamp((src_t - 0) / 14.0)
    d.rectangle((0, SCR_H - 6, SCR_W, SCR_H), fill=(255, 255, 255, 60)); d.rectangle((0, SCR_H - 6, int(SCR_W * pr), SCR_H), fill=(255, 255, 255, 230))
    # drag (stop the scroll)
    off = 0.0
    if DRAG0 <= t < DRAG1: off = .40 * inout((t - DRAG0) / (DRAG1 - DRAG0)) ** 1.3
    elif t >= DRAG1:
        x = (t - DRAG1) / .5; off = .40 * max(0.0, math.exp(-7 * x) * math.cos(2.6 * math.pi * x)) if x < 1 else 0
        off = .40 * (1 - spring((t - DRAG1) / .42, 1.6, 8.0))
    if off > .002:
        oy = int(SCR_H * off)
        nxt = C('nextpost', lambda: _next_post())
        out = Image.new('RGBA', (SCR_W, SCR_H), (0, 0, 0, 255))
        out.alpha_composite(reel, (0, -oy)); out.alpha_composite(nxt, (0, SCR_H - oy))
        reel = out
    # touch indicator: a crisp glass fingertip ring with a fading swipe trail
    if DRAG0 - .06 <= t < DRAG1 + .14:
        p_ = inout((t - DRAG0) / (DRAG1 - DRAG0)) ** 1.3
        a = clamp((t - (DRAG0 - .06)) / .06) * clamp((DRAG1 + .14 - t) / .14)
        tx, ty = SCR_W * .56, SCR_H * (.80 - .40 * p_)
        y0 = SCR_H * .80
        if ty < y0 - 4:
            tr = C(('trail', SCR_W), lambda: _trail())
            L = int(y0 - ty); seg_ = tr.resize((tr.width, max(2, L)), Image.BILINEAR)
            reel.alpha_composite(E.fade(seg_, a), (int(tx - seg_.width / 2), int(ty)))
        dot = C('touch2', lambda: _touch())
        press = 1 - .12 * clamp((t - (DRAG0 - .06)) / .08) + .12 * clamp((t - DRAG1) / .08)
        d_ = dot if abs(press - 1) < .01 else dot.resize((int(dot.width * press), int(dot.height * press)), Image.BILINEAR)
        reel.alpha_composite(E.fade(d_, a), (int(tx - d_.width / 2), int(ty - d_.height / 2)))
    # double-tap heart
    hk = t - W_SCROLL
    if 0 <= hk < .6:
        s = .3 + .9 * back(hk / .2, 3.0) - .25 * clamp((hk - .35) / .25)
        a = clamp(hk / .04) * clamp((.6 - hk) / .2)
        hm = heart_img(240, True, 'grad')
        hm = hm.resize((max(1, int(240 * s)), max(1, int(240 * s))), Image.BILINEAR)
        hm = E.shadow(hm, 18, .45, (0, 8))
        reel.alpha_composite(E.fade(hm, a), (SCR_W // 2 - hm.width // 2, int(SCR_H * .42) - hm.height // 2 - int(hk * 60)))
    return reel


def _touch():
    """fingertip: thin white ring + faint glass fill + soft outer glow (supersampled)."""
    n, k = 132, 4; N = n * k
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32); r = np.sqrt((xx - N / 2) ** 2 + (yy - N / 2) ** 2) / k
    ring = np.clip(1 - np.abs(r - 34) / 2.2, 0, 1)
    fill = (r < 34).astype(np.float32) * .16
    glow = np.exp(-((r - 34) / 14) ** 2) * .35
    al = np.clip(ring + fill + glow * (r > 34), 0, 1)
    im = Image.fromarray((al * 255).astype(np.uint8)).resize((n, n), Image.LANCZOS)
    out = Image.new('RGBA', (n, n), (255, 255, 255, 0)); out.putalpha(im); return out


def _trail():
    """vertical swipe trail (stretched to the drag length): gradient capsule, transparent at the far end."""
    w, h = 40, 256
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]; xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    al = np.clip(1 - np.abs(xx) ** 2, 0, 1) * (.05 + .45 * (1 - yy) ** 1.2)
    al *= np.clip(yy / .06, 0, 1) * 0 + 1
    col = np.zeros((h, w, 3), np.float32) + np.array([235, 232, 255], np.float32)
    im = Image.fromarray(col.astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((al * 255).astype(np.uint8))); return im


def _next_post():
    im = cover(E.asset('bad_flyer'), SCR_W, SCR_H).convert('RGBA')
    d = ImageDraw.Draw(im); d.rectangle((0, 0, SCR_W, 4), fill=(0, 0, 0, 255))
    return im


def phone_front(t):
    content = screen_content(t)
    return E.phone(content.convert('RGB'), PH_W)


def phone_state(t):
    p = clamp((t - SPIN0) / (SPIN1 - SPIN0))
    e = 1 - (1 - p) ** 3
    ry = math.radians(-270) * (1 - e)
    if t > SPIN1: ry += math.radians(7) * math.exp(-(t - SPIN1) * 9) * math.sin((t - SPIN1) * 22)
    s = lerp(CARD_H / (PH_W * 2.05), 1.0, cub(p))
    x = lerp(CARD_X, PH_X, cub(p)); y = lerp(CARD_Y, PH_Y, cub(p)) - 120 * math.sin(math.pi * cub(p))
    rz = math.radians(lerp(-3, 0, cub(p)))
    rx = 0.
    # floating idle + STOP punch
    if t > SPIN1:
        y += 8 * math.sin((t - SPIN1) * 2.4)
        ry += math.radians(4) * math.sin((t - SPIN1) * 1.3)
        s *= 1 + .035 * math.exp(-(t - W_STOP) * 10) * (t >= W_STOP)
    return x, y, ry, rx, rz, s


def phone_layer(t):
    """returns (img, ox, oy) — the warped phone (motion-blurred while spinning)."""
    def one(tt):
        x, y, ry, rx, rz, s = phone_state(tt)
        facing = math.cos(ry) * math.cos(rx) > 0
        art = phone_front(t) if facing else phone_back()
        shade = .65 + .35 * abs(math.cos(ry))
        art = bright(art, shade)
        im, (ox, oy), _ = persp(art, ry, rx, rz, s, 1900)
        return im, x - ox, y - oy
    x, y, ry, rx, rz, s = phone_state(t)
    ry2 = phone_state(t - 1 / 60)[2]
    if t < SPIN1 + .03 and abs(ry - ry2) > math.radians(8):
        # motion blur: average 3 sub-frames (premultiplied) on a shared canvas
        subs = [one(t - k / 330) for k in range(6)]
        subs = [s_ for s_ in subs if s_[0] is not None]
        if not subs: return None
        X0 = min(int(a) for _, a, _ in subs); Y0 = min(int(b) for _, _, b in subs)
        X1 = max(int(a) + im.width for im, a, _ in subs); Y1 = max(int(b) + im.height for im, _, b in subs)
        acc = np.zeros((Y1 - Y0, X1 - X0, 4), np.float32)
        for im, a, b in subs:
            arr = np.asarray(im, np.float32); al = arr[..., 3:4] / 255
            xo, yo = int(a) - X0, int(b) - Y0
            acc[yo:yo + im.height, xo:xo + im.width, :3] += arr[..., :3] * al
            acc[yo:yo + im.height, xo:xo + im.width, 3:] += al
        acc /= len(subs)
        rgb = acc[..., :3] / np.maximum(acc[..., 3:], 1e-4)
        out = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(acc[..., 3:] * 255, 0, 255)]).astype(np.uint8), 'RGBA')
        return out, X0, Y0
    r = one(t)
    return r if r[0] is not None else None


def phone_glow():
    def mk():
        w, h = PH_W + 360, int(PH_W * 2.05) + 360
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((180, 180, w - 180, h - 180), 70, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(70)).point(lambda v: int(v * .55))
        im = Image.new('RGBA', (w, h), (110, 80, 255, 0)); im.putalpha(m); return im
    return C('phglow', mk)


def phone_ring():
    def mk():
        w, h = PH_W, int(PH_W * 2.05); p = 40; r = int(w * .16)
        m = Image.new('L', (w + 2 * p, h + 2 * p)); ImageDraw.Draw(m).rounded_rectangle((p, p, p + w, p + h), r, outline=255, width=5)
        g = m.filter(ImageFilter.GaussianBlur(10))
        al = np.clip(np.asarray(m, np.float32) * .9 + np.asarray(g, np.float32) * 1.6, 0, 255)
        im = Image.new('RGBA', m.size, (190, 175, 255, 0)); im.putalpha(Image.fromarray(al.astype(np.uint8))); return im
    return C('phring', mk)


# ================================================================ B: carousel
CAR_W = 570
CAR_IMG = CAR_W - 40
CAR_IH = int(CAR_IMG * 1.25)
CAR_H = 92 + CAR_IH + 96
CAR_X, CAR_Y = 735, 800


def car_panel():
    def mk():
        im = E.glass_panel(CAR_W, CAR_H, 34, alpha=.13, border=.5)
        dark = Image.new('RGBA', (CAR_W, CAR_H), (14, 14, 20, 0)); m = Image.new('L', (CAR_W, CAR_H))
        ImageDraw.Draw(m).rounded_rectangle((0, 0, CAR_W - 1, CAR_H - 1), 34, fill=110); dark.putalpha(m)
        out = Image.new('RGBA', (CAR_W, CAR_H)); out.alpha_composite(dark); out.alpha_composite(im)
        d = ImageDraw.Draw(out)
        av = E.gradient(54, 54, [(196, 160, 120), (150, 110, 80), (110, 80, 60)]).convert('RGBA'); mm = Image.new('L', (54, 54)); ImageDraw.Draw(mm).ellipse((0, 0, 53, 53), fill=255); av.putalpha(mm)
        out.alpha_composite(av, (22, 20))
        d.text((90, 24), 'northroast.coffee', font=E.font(26, 700), fill=WHITE)
        d.text((90, 54), 'Sponsored', font=E.font(19, 400), fill=(190, 190, 205))
        for i in range(3): d.ellipse((CAR_W - 62 + i * 13, 44, CAR_W - 56 + i * 13, 50), fill=WHITE)
        # actions
        y = 92 + CAR_IH + 30
        out.alpha_composite(heart_img(40, False, (240, 240, 245), outline=True), (22, y - 2))
        d.ellipse((80, y, 116, y + 34), outline=(240, 240, 245), width=3); d.polygon([(84, y + 26), (79, y + 40), (94, y + 33)], fill=(240, 240, 245))
        d.polygon([(136, y + 3), (174, y + 16), (136, y + 30), (143, y + 16)], outline=(240, 240, 245), width=3)
        return out
    return C('carpanel', mk)


def car_slide(name):
    return C(('carslide', name), lambda: cover(E.asset(name), CAR_IMG, CAR_IH).convert('RGBA'))


def carousel(t):
    out = car_panel().copy()
    # image window
    sk = expo((t - SWIPE0) / .34)
    win = Image.new('RGBA', (CAR_IMG, CAR_IH), (0, 0, 0, 255))
    ox = int(-CAR_IMG * sk)
    a = car_slide('carousel_1'); b = car_slide('carousel_2')
    if sk < .999: win.alpha_composite(a, (ox, 0))
    if sk > .001: win.alpha_composite(b, (ox + CAR_IMG + 8, 0))
    if 0.02 < sk < .9:       # light motion streak
        win = Image.blend(win, win.filter(ImageFilter.BoxBlur(3)), .6 * (1 - abs(sk - .4) / .5))
    # counter pill
    d = ImageDraw.Draw(win)
    n = 2 if sk > .5 else 1
    d.rounded_rectangle((CAR_IMG - 86, 16, CAR_IMG - 16, 52), 18, fill=(10, 10, 14, 170))
    d.text((CAR_IMG - 72, 20), f'{n}/2', font=E.font(24, 700), fill=WHITE)
    out.alpha_composite(E.rounded(win, 18), (20, 92))
    # dots
    d = ImageDraw.Draw(out); cy = 92 + CAR_IH + 48
    for i in range(2):
        on = (i == 0) if n == 1 else (i == 1)
        r = 6 if on else 5; cx = CAR_W // 2 - 10 + i * 20
        if on: out.alpha_composite(E.gradient(2 * r, 2 * r, E.GRAD_LIGHT).convert('RGBA'), (cx - r, cy - r), ) if False else d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(150, 140, 255))
        else: d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(150, 150, 165))
    # bookmark
    y = 92 + CAR_IH + 26; bx = CAR_W - 62
    if t < W_SAVE: out.alpha_composite(bookmark_img(44, False), (bx, y))
    else:
        k = back((t - W_SAVE) / .22, 3.2); s = .5 + .5 * k + .25 * math.exp(-(t - W_SAVE) * 8) * 0
        bm = bookmark_img(44, True, True)
        bs = max(1, int(44 * (.6 + .6 * k) if t - W_SAVE < .22 else 44))
        bm = bm.resize((bs, bs), Image.BILINEAR)
        out.alpha_composite(bm, (bx + 22 - bs // 2, y + 22 - bs // 2))
    return out


def toast_saved():
    """'Saved' glass pill: 300 x 72, gradient bookmark + Outfit 600 34 px."""
    def mk():
        w, h = 300, 72
        im = E.glass_panel(w, h, 36, alpha=.16, border=.6)
        dark = Image.new('RGBA', (w, h), (16, 14, 30, 0)); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=200); dark.putalpha(m)
        out = Image.new('RGBA', (w, h)); out.alpha_composite(dark); out.alpha_composite(im)
        f = E.font(34, 600); tx = 'Saved'; l, tp, r, b = f.getbbox(tx)
        bm = bookmark_img(40, True, True); tw = 40 + 14 + (r - l); x0 = (w - tw) // 2
        out.alpha_composite(bm, (x0, (h - 40) // 2))
        ImageDraw.Draw(out).text((x0 + 54 - l, (h - (b - tp)) // 2 - tp), tx, font=f, fill=WHITE)
        return E.shadow(out, 20, .55, (0, 10))
    return C('toast2', mk)


def ping_ring(r, a, col=(190, 170, 255), width=3):
    n = int(2 * r + 12); im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((6, 6, n - 6, n - 6), outline=col + (int(255 * a),), width=width)
    return im


# ================================================================ C: lightbox poster
PO_W = 520
PO_H = int(PO_W * 1.25)
PO_X, PO_Y = 372, 560


def poster_art():
    def mk():
        fw = 16
        img = E.asset('design_post').resize((PO_W, PO_H), Image.LANCZOS).convert('RGBA')
        out = Image.new('RGBA', (PO_W + 2 * fw, PO_H + 2 * fw), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
        d.rounded_rectangle((0, 0, out.width - 1, out.height - 1), 10, fill=(22, 22, 28, 255), outline=(70, 70, 82, 255), width=2)
        out.alpha_composite(img, (fw, fw))
        d.rectangle((fw - 1, fw - 1, fw + PO_W, fw + PO_H), outline=(255, 250, 240, 120), width=1)
        return out
    return C('poster', mk)


def sheen(img, k, width=.16, strength=.75):
    """diagonal light sweep across an RGBA image, k: 0..1."""
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx / w + yy / h * .55) / 1.55
    c = lerp(-.25, 1.25, k)
    band = np.exp(-((u - c) / width) ** 2) * strength
    a = np.asarray(img, np.float32)
    rgb = a[..., :3] + (255 - a[..., :3]) * band[..., None]
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]).astype(np.uint8), 'RGBA')


def power(t):
    """lightbox brightness: flicker on at DESIGNS."""
    x = t - POWER
    if x < 0: return 0.0
    seq = [(.0, 1.0), (.04, .15), (.07, .85), (.10, .35), (.15, .95), (.19, .7), (.24, 1.0)]
    v = 0.0
    for a, b in seq:
        if x >= a: v = b
    return v


def credit(n):
    """'Made by LUMARC' typed to n characters: Outfit 600 46 px, LUMARC in the brand gradient, caret."""
    def mk():
        full = 'Made by LUMARC'; s_ = full[:n]
        f = E.font(46, 600); l, tp, r, b = f.getbbox(full)
        W_, H_ = r - l + 40, 76
        im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        pre = s_[:8]; post = s_[8:]
        ImageDraw.Draw(im).text((4 - l, 14 - tp), pre, font=f, fill=(236, 232, 248))
        if post:
            lp = f.getbbox('Made by ')[2]
            g = E.gradient(W_, H_, E.GRAD_LIGHT).convert('RGBA'); m = Image.new('L', g.size)
            ImageDraw.Draw(m).text((4 - l + lp, 14 - tp), post, font=f, fill=255); g.putalpha(m); im.alpha_composite(g)
        if n < len(full):
            cx = 4 + (f.getbbox(s_)[2] - l if s_ else 0) + 4
            ImageDraw.Draw(im).rectangle((cx, 12, cx + 3, 64), fill=(170, 150, 255, 255))
        return E.shadow(im, 10, .7, (0, 4))
    return C(('credit2', n), mk)


def light_map(pw):
    """light for the studio wall in C: (mult, add).  A pool centred on the poster (spot from above), a soft wall bounce
    (additive, so the dark wall actually lights up), falling to near black at the frame edges — not a grey veil."""
    def mk():
        yy, xx = np.mgrid[0:H:2, 0:W:2].astype(np.float32)
        cx, cy = PO_X, PO_Y - 30
        r2 = ((xx - cx) / 400) ** 2 + ((yy - cy) / 520) ** 2
        pool = np.exp(-r2 ** .85)
        cone = np.exp(-((xx - cx) / (120 + .30 * yy)) ** 2) * np.clip(1 - (yy - (cy + 260)) / 360, 0, 1) * np.clip(yy / 200, 0, 1)
        edge = np.clip(1 - np.sqrt(((xx - cx) / 950) ** 2 + ((yy - cy) / 1250) ** 2), 0, 1)
        mult = .40 + .16 * edge + pw * (.85 * pool + .2 * cone)
        add = pw * (46 * pool ** 1.3 + 14 * cone)
        mult = np.dstack([mult, mult * .99, mult * 1.02])
        add = np.dstack([add * .86, add * .80, add * 1.0])
        up = lambda a: np.asarray(Image.fromarray(np.clip(a * 40, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 40
        return up(mult), up(add / 10) * 10
    return C(('lmap2', round(pw, 2)), mk)


def lit_studio(dx, z, pw):
    def mk():
        m, a_ = light_map(pw)
        a = np.asarray(studio_shift(dx, z), np.float32) * m + a_
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return C(('litstudio2', dx, z, round(pw, 2)), mk)


def poster_warm():
    def mk():
        a = np.asarray(poster_art(), np.float32).copy(); a[..., 0] *= 1.05; a[..., 2] *= .92
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    return C('posterwarm', mk)


# ================================================================ D: website on a laptop
PAGE_W, PAGE_VH = 1344, 840
RES_Y0 = 752                 # reservations section starts here in page coords
SCROLL_TO = 640
BTN = (RES_Y0 + 520, 672, 360, 92)     # (cy, cx, w, h) of the Book a table button in page coords


def serif(size):
    return C(('serif', size), lambda: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf', size))


def page():
    def mk():
        site = E.asset('website')
        H2 = RES_Y0 + 820
        im = Image.new('RGB', (PAGE_W, H2), (13, 32, 26)); im.paste(site, (0, 0))
        d = ImageDraw.Draw(im)
        y = RES_Y0
        # subtle top divider + dish strip
        d.line((96, y + 70, PAGE_W - 96, y + 70), fill=(60, 86, 74), width=1)
        f = E.font(22, 500)
        d.text((PAGE_W // 2 - 90, y + 110), 'RESERVATIONS', font=E.font(24, 600), fill=(196, 178, 128))
        t = 'Reserve your evening'; sf = serif(76); l, tp, r, b = sf.getbbox(t)
        d.text((PAGE_W // 2 - (r - l) // 2 - l, y + 160), t, font=sf, fill=(240, 234, 220))
        t2 = 'Seasonal tasting menu · open Tue–Sun · 6pm to midnight'; l, tp, r, b = E.font(26, 400).getbbox(t2)
        d.text((PAGE_W // 2 - (r - l) // 2 - l, y + 270), t2, font=E.font(26, 400), fill=(170, 186, 176))
        # fields
        fx = [232, 532, 832]; labs = [('DATE', 'Fri, 18 Oct'), ('GUESTS', '2 people'), ('TIME', '8:00 PM')]
        for x, (a, b_) in zip(fx, labs):
            d.rounded_rectangle((x, y + 340, x + 280, y + 430), 10, outline=(90, 120, 104), width=2)
            d.text((x + 22, y + 352), a, font=E.font(18, 600), fill=(150, 170, 160))
            d.text((x + 22, y + 380), b_, font=E.font(30, 500), fill=(236, 232, 220))
        # button
        cy, cx, bw, bh = BTN
        d.rounded_rectangle((cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2), 8, fill=(226, 206, 150))
        t3 = 'BOOK A TABLE  →'; l, tp, r, b = E.font(30, 700).getbbox(t3)
        d.text((cx - (r - l) // 2 - l, cy - (b - tp) // 2 - tp), t3, font=E.font(30, 700), fill=(18, 36, 28))
        t4 = 'or call +1 (555) 014-2290'; l, tp, r, b = E.font(22, 400).getbbox(t4)
        d.text((cx - (r - l) // 2 - l, cy + 70), t4, font=E.font(22, 400), fill=(140, 160, 150))
        return im
    return C('page', mk)


def btn_booked():
    def mk():
        cy, cx, bw, bh = BTN
        im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, bw - 1, bh - 1), 8, fill=(90, 190, 130))
        t = 'BOOKED'; f = E.font(30, 800); l, tp, r, b = f.getbbox(t)
        tx = bw // 2 - (r - l) // 2 - l + 22
        d.text((tx, bh // 2 - (b - tp) // 2 - tp), t, font=f, fill=(10, 30, 18))
        cx0 = tx - 30; d.line([(cx0 - 14, bh // 2), (cx0 - 4, bh // 2 + 10), (cx0 + 14, bh // 2 - 10)], fill=(10, 30, 18), width=5, joint='curve')
        return im
    return C('booked', mk)


def cursor_img():
    def mk():
        s = 4; n = 40 * s; m = Image.new('L', (n, n)); d = ImageDraw.Draw(m)
        pts = [(2, 2), (2, 30), (9, 23), (14, 35), (19, 33), (14, 21), (24, 21)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=255)
        m = m.resize((40, 40), Image.LANCZOS)
        body = Image.new('RGBA', (40, 40), (12, 12, 16, 255)); body.putalpha(m)
        ol = m.filter(ImageFilter.MaxFilter(5))
        out = Image.new('RGBA', (40, 40), (255, 255, 255, 0)); out.putalpha(ol); out.alpha_composite(body)
        return out.resize((52, 52), Image.LANCZOS)
    return C('cursor', mk)


def site_frame(t):
    sc = SCROLL_TO * inout((t - SCROLL0) / (SCROLL1 - SCROLL0))
    pg = page(); y0 = int(round(sc))
    view = pg.crop((0, y0, PAGE_W, y0 + PAGE_VH)).convert('RGBA')
    cy, cx, bw, bh = BTN; by = cy - y0
    d = ImageDraw.Draw(view)
    if t >= CLICK:
        k = t - CLICK
        if k < .12:   # pressed
            d.rounded_rectangle((cx - bw // 2 + 4, by - bh // 2 + 3, cx + bw // 2 - 4, by + bh // 2 - 3), 8, fill=(190, 170, 118))
        else:
            view.alpha_composite(btn_booked(), (cx - bw // 2, by - bh // 2))
        if k < .6:     # ripple
            rr = 20 + 260 * eout(k / .6); a = int(200 * (1 - k / .6))
            rip = Image.new('RGBA', view.size, (0, 0, 0, 0)); ImageDraw.Draw(rip).ellipse((cx - rr, by - rr, cx + rr, by + rr), outline=(255, 245, 210, a), width=6)
            view.alpha_composite(rip)
    # cursor
    if t >= 45.98:
        k = cub((t - 46.02) / (CLICK - .04 - 46.02))
        px = lerp(1150, cx + 40, k); py = lerp(PAGE_VH - 40, by + 10, k)
        if t >= CLICK and t < CLICK + .1: px += 2; py += 2
        if t > CLICK + .25: px += (t - CLICK - .25) * 120; py += (t - CLICK - .25) * 90
        view.alpha_composite(cursor_img(), (int(px), int(py)))
    return view.convert('RGB')


LID_W, LID_BZ, LID_TOP, LID_CHIN = 780, 16, 20, 24
SW_, SH_ = LID_W - 2 * LID_BZ, int((LID_W - 2 * LID_BZ) * .625)
LID_H = LID_TOP + SH_ + LID_CHIN
LID_TILT = math.radians(-9)            # screen leans back ~9 deg (top recedes)
DECK_FW, DECK_D, LIP = 900, 48, 15     # deck front width, projected depth, front-lip thickness
LCAN_W = 1000


def lid_frame():
    def mk():
        im = Image.new('RGBA', (LID_W, LID_H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, LID_W - 1, LID_H - 1), 26, fill=(16, 16, 20, 255))
        d.rounded_rectangle((0, 0, LID_W - 1, LID_H - 1), 26, outline=(122, 122, 140, 255), width=3)
        d.rounded_rectangle((3, 3, LID_W - 4, LID_H - 4), 24, outline=(46, 46, 56, 255), width=2)
        d.ellipse((LID_W // 2 - 4, 7, LID_W // 2 + 4, 15), fill=(40, 44, 60, 255))
        return im
    return C('lidframe', mk)


def glass_refl():
    """static screen glass: a faint top-left gradient + a soft diagonal reflection (RGBA, screen size)."""
    def mk():
        yy, xx = np.mgrid[0:SH_, 0:SW_].astype(np.float32)
        u = xx / SW_ + yy / SH_ * .6
        al = np.clip(.08 * (1 - u / 1.2), 0, 1) + .04 * np.exp(-((u - .95) / .05) ** 2)
        im = Image.new('RGBA', (SW_, SH_), (255, 255, 255, 0)); im.putalpha(Image.fromarray((al * 255).astype(np.uint8))); return im
    return C('glassrefl', mk)


def glass_sweep(k):
    """moving reflection sweep across the screen glass, k: 0..1."""
    yy, xx = np.mgrid[0:SH_:2, 0:SW_:2].astype(np.float32)
    u = (xx * 2 / SW_ + yy * 2 / SH_ * .7) / 1.7
    c = lerp(-.3, 1.3, k)
    al = np.exp(-((u - c) / .07) ** 2) * .22 + np.exp(-((u - c - .1) / .02) ** 2) * .10
    m = Image.fromarray((np.clip(al, 0, 1) * 255).astype(np.uint8)).resize((SW_, SH_), Image.BILINEAR)
    im = Image.new('RGBA', (SW_, SH_), (255, 255, 255, 0)); im.putalpha(m); return im


def lid_corners():
    """projected corners of the tilted lid (TL, TR, BR, BL), relative to the lid centre."""
    return project(LID_W, LID_H, 0, LID_TILT, 0, 1., 2200.)


def deck():
    """the base: trapezoid deck in perspective with a gradient, keyboard well, trackpad, a highlight lip and a
    contact shadow.  Returns (RGBA canvas LCAN_W wide, hinge y)."""
    def mk():
        q = lid_corners(); hw = (q[2][0] - q[3][0]) / 2
        hy = 6
        Hc = hy + DECK_D + LIP + 50
        im = Image.new('RGBA', (LCAN_W, Hc), (0, 0, 0, 0)); cx = LCAN_W / 2
        sh = Image.new('L', (LCAN_W, Hc)); ImageDraw.Draw(sh).ellipse((cx - DECK_FW / 2 - 10, hy + DECK_D + LIP - 16, cx + DECK_FW / 2 + 10, hy + DECK_D + LIP + 24), fill=255)
        sh = sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .85))
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', sh.size, 0)] * 3 + [sh]))
        ss = 3
        m = Image.new('L', (LCAN_W * ss, Hc * ss)); dm = ImageDraw.Draw(m)
        bw = hw + 12
        dm.polygon([((cx - bw) * ss, (hy - 3) * ss), ((cx + bw) * ss, (hy - 3) * ss), ((cx + DECK_FW / 2) * ss, (hy + DECK_D) * ss),
                    ((cx - DECK_FW / 2) * ss, (hy + DECK_D) * ss)], fill=255)
        m = m.resize((LCAN_W, Hc), Image.LANCZOS)
        v = np.clip((np.arange(Hc, dtype=np.float32) - hy) / DECK_D, 0, 1)[:, None]
        xg = np.abs(np.linspace(-1, 1, LCAN_W, dtype=np.float32))[None, :]
        g = 62 + 96 * v ** .8 - 18 * xg ** 2 + 26 * np.exp(-((v - .74) / .10) ** 2) * (1 - xg ** 4)
        surf = Image.fromarray(np.clip(np.dstack([g * .96, g * .96, g * 1.06]), 0, 255).astype(np.uint8)).convert('RGBA'); surf.putalpha(m)
        im.alpha_composite(surf)
        d = ImageDraw.Draw(im)
        kw0, kw1 = bw * .86, DECK_FW / 2 * .80
        d.polygon([(cx - kw0, hy + 5), (cx + kw0, hy + 5), (cx + kw1 * .97, hy + DECK_D * .52), (cx - kw1 * .97, hy + DECK_D * .52)], fill=(34, 34, 42, 210))
        tp0, tp1 = 118, 136
        d.polygon([(cx - tp0, hy + DECK_D * .60), (cx + tp0, hy + DECK_D * .60), (cx + tp1, hy + DECK_D * .94), (cx - tp1, hy + DECK_D * .94)], outline=(96, 96, 112, 255))
        d.rectangle((cx - bw + 6, hy - 3, cx + bw - 6, hy + 1), fill=(14, 14, 18, 255))
        lm = Image.new('L', (LCAN_W * ss, Hc * ss)); ImageDraw.Draw(lm).rounded_rectangle(((cx - DECK_FW / 2) * ss, (hy + DECK_D - 1) * ss, (cx + DECK_FW / 2) * ss, (hy + DECK_D + LIP) * ss), 9 * ss, fill=255)
        lm = lm.resize((LCAN_W, Hc), Image.LANCZOS)
        lv = np.clip((np.arange(Hc, dtype=np.float32) - (hy + DECK_D)) / LIP, 0, 1)[:, None]
        lg = 120 - 70 * lv - 20 * xg ** 2
        lip = Image.fromarray(np.clip(np.dstack([lg * .95, lg * .95, lg * 1.06]), 0, 255).astype(np.uint8)).convert('RGBA'); lip.putalpha(lm)
        im.alpha_composite(lip)
        d.line((cx - DECK_FW / 2 + 10, hy + DECK_D, cx + DECK_FW / 2 - 10, hy + DECK_D), fill=(232, 232, 245, 230), width=2)
        d.rounded_rectangle((cx - 64, hy + DECK_D + 1, cx + 64, hy + DECK_D + 6), 3, fill=(70, 70, 82, 255))
        return im, hy
    return C('deck2', mk)


def lid_geom():
    q = lid_corners(); top = min(q[0][1], q[1][1]); bot = max(q[2][1], q[3][1])
    return top, bot


def laptop_img(t, sweep=None):
    """full laptop (RGBA, LCAN_W wide) with the live site on a lid tilted back in true perspective."""
    lid = lid_frame().copy()
    scr = site_frame(t).resize((SW_, SH_), Image.BILINEAR).convert('RGBA')
    scr.alpha_composite(glass_refl())
    if sweep is not None and 0 < sweep < 1: scr.alpha_composite(glass_sweep(sweep))
    lid.alpha_composite(scr, (LID_BZ, LID_TOP))
    wl, (ox, oy), _ = persp(lid, 0, LID_TILT, 0, 1., 2200.)
    dk, hy = deck(); top, bot = lid_geom()
    lid_h = bot - top
    out = Image.new('RGBA', (LCAN_W, int(math.ceil(lid_h)) + dk.height - hy), (0, 0, 0, 0))
    hinge = int(round(lid_h))
    out.alpha_composite(dk, (0, hinge - hy))
    out.alpha_composite(wl, (int(round(LCAN_W / 2 - ox)), int(round(hinge - bot - oy))))
    return out


def lid_screen_top_y():
    """y (in laptop_img coords) of the screen-glass top edge."""
    return LID_TOP * .98 + 2


def notif():
    def mk():
        w, h = 620, 116
        im = E.glass_panel(w, h, 32, alpha=.16, border=.6)
        dark = Image.new('RGBA', (w, h), (16, 16, 24, 0)); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 32, fill=215); dark.putalpha(m)
        out = Image.new('RGBA', (w, h)); out.alpha_composite(dark); out.alpha_composite(im)
        ic = E.rounded(Image.new('RGB', (76, 76), (13, 32, 26)), 18); d0 = ImageDraw.Draw(ic)
        l, tp, r, b = serif(50).getbbox('O'); d0.text((38 - (r - l) / 2 - l, 38 - (b - tp) / 2 - tp), 'O', font=serif(50), fill=(226, 206, 150))
        out.alpha_composite(ic, (22, 20))
        d = ImageDraw.Draw(out)
        f1 = E.font(36, 800); d.text((116, 18), 'New booking', font=f1, fill=WHITE)
        l, tp, r, b = f1.getbbox('New booking')
        cx = 116 + r + 30; cy = 18 + (tp + b) / 2
        d.ellipse((cx - 17, cy - 17, cx + 17, cy + 17), fill=(80, 205, 130))
        d.line([(cx - 8, cy), (cx - 2, cy + 7), (cx + 9, cy - 6)], fill=(255, 255, 255), width=5, joint='curve')
        d.text((116, 64), 'Table for 2 · Fri 8 PM', font=E.font(29, 500), fill=(206, 206, 220))
        d.text((w - 70, 22), 'now', font=E.font(22, 500), fill=(170, 170, 185))
        return E.shadow(out, 24, .6, (0, 12))
    return C('notif2', mk)


ST_W, ST_H = 262, 318


def stat_card(n_followers_k, cust, show_cust, pulse=0.):
    base = C('statbase2', lambda: _stat_base(ST_W, ST_H))
    out = base.copy(); d = ImageDraw.Draw(out)
    d.text((26, 24), 'FOLLOWERS', font=E.font(25, 700), fill=(186, 186, 204))
    d.text((24, 56), n_followers_k, font=E.font(60, 800), fill=WHITE)
    if show_cust > 0:
        ax = 44; a = int(255 * show_cust)
        lay = Image.new('RGBA', (ST_W, ST_H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.line((ax, 146, ax, 176), fill=(160, 140, 255, a), width=4); dl.polygon([(ax - 10, 172), (ax + 10, 172), (ax, 186)], fill=(160, 140, 255, a))
        dl.text((26, 198), 'CUSTOMERS', font=E.font(25, 700), fill=(186, 186, 204, a))
        f = E.font(64, 800); l, tp, r, b = f.getbbox(cust)
        cols = [tuple(int(c + (255 - c) * .55 * pulse) for c in cc) for cc in E.GRAD_LIGHT]
        g = E.gradient(r - l + 20, b - tp + 20, cols).convert('RGBA'); m = Image.new('L', g.size)
        ImageDraw.Draw(m).text((10 - l, 10 - tp), cust, font=f, fill=a); g.putalpha(m)
        if pulse > .02:
            gl = Image.new('RGBA', g.size, (150, 120, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .9 * pulse)))
            lay.alpha_composite(gl, (14, 226))
        lay.alpha_composite(g, (14, 226))
        out.alpha_composite(lay)
    return out


def _stat_base(w, h):
    im = E.glass_panel(w, h, 30, alpha=.13, border=.5)
    dark = Image.new('RGBA', (w, h), (14, 14, 22, 0)); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=150); dark.putalpha(m)
    out = Image.new('RGBA', (w, h)); out.alpha_composite(dark); out.alpha_composite(im); return out


# ================================================================ studio truck (parallax)
def studio_shift(dx, z=1.0):
    """studio plate trucked by dx — self-covering: the zoom always covers the shift, so no plate edge shows."""
    z = max(z, 1 + abs(dx) / 540 + .012)
    return E.zoom(E.studio(), z, (540, 760), dx=dx)


# ================================================================ avatar with feathered plate borders
FEATHER = 110            # px (source) soft ramp at the plate's left/right borders: no cardboard-cutout cut lines


def _film(ctx):
    try:
        for c in (ctx.compose.__closure__ or ()):
            v = c.cell_contents
            if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    except Exception:
        pass
    return None


def _feather_row():
    def mk():
        x = np.arange(W, dtype=np.float32)
        r = np.clip(np.minimum(x, W - 1 - x) / FEATHER, 0, 1)
        return (r * r * (3 - 2 * r))[None, :]
    return C('feather', mk)


_AVC = {}
def place_avatar(ctx, t, s, x, bright_k=1.0):
    """draw the keyed founder ourselves (last 'behind' layer = exactly where the engine would put him) with the plate's
    left/right borders feathered.  Falls back to the engine avatar if the film object is not reachable."""
    F = _film(ctx)
    if F is None:
        ctx.avatar.update(s=s, x=x, bright=bright_k); return
    ctx.avatar['show'] = False
    av = F.av.frame(t)
    k = (id(av), round(s, 4), round(bright_k, 3))
    if _AVC.get('k') != k:
        a = np.asarray(av, np.float32).copy()
        a[..., 3] *= _feather_row()
        if abs(bright_k - 1) > .005: a[..., :3] *= bright_k
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
        if abs(s - 1) > .005: im = im.resize((int(W * s), int(H * s)), Image.BILINEAR)
        _AVC.clear(); _AVC.update(k=k, im=im, av=av)
    im = _AVC['im']
    ctx.add('behind', im, int(540 - im.width / 2 + x), int(H - im.height), center=False)


# ================================================================ captions (own track, engine look)
def _cap_pages():
    pages = []
    for i, pg in enumerate(CAPS):
        ws = []
        for j, (tx, t0) in enumerate(pg):
            t1 = pg[j + 1][1] if j + 1 < len(pg) else t0 + .42
            ws.append(dict(text=tx.strip('*'), emph=tx.startswith('*'), t0=t0, t1=t1))
        pages.append(dict(words=ws))
    for i, p in enumerate(pages):
        p['a'] = p['words'][0]['t0'] - .04
        nxt = pages[i + 1]['words'][0]['t0'] - .04 if i + 1 < len(pages) else END
        last = p['words'][-1]['t0']
        p['z'] = min(END, nxt - .02 if nxt - last < 1.0 else last + .75)
        cut = min([c for c in (T23, T24, T25, END) if c > p['a']])
        p['z'] = min(p['z'], cut - 1e-3)      # never carry a page across a jump cut (no 1-frame ghost at the new cap_y)
    return pages
CAP_PAGES = _cap_pages()


def draw_caps(ctx, t, cy0, base=92):
    """same look/animation as engine.draw_captions, but on measured onsets. Drawn as screen layers (captions off)."""
    ctx.captions = False
    for p in CAP_PAGES:
        if not (p['a'] <= t < p['z']): continue
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * back(lt / .16)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.06
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = E.fade(img, lt / .05)
            if p['z'] - t < .06: img = E.fade(img, (p['z'] - t) / .06)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2), center=False)


def draw_A(ctx, t):
    # multicam snap at 37.28: open already part-way into the truck (s08 ends centred at z 1.36), then glide
    k = lerp(.38, 1.0, expo((t - START) / .75))
    push = smooth((t - 37.9) / 3.9)
    avs, avx = lerp(1.0, .84, k), lerp(0, 255, k)
    ctx.bg_img = studio_shift(lerp(0, 60, k), 1.0 + .03 * k)
    ctx.cam = dict(z=lerp(1.12, 1.03, k) + .05 * push, x=540., y=820., dx=0., dy=0., rot=0.)
    if t >= W_STOP: ctx.cam['z'] += .025 * math.exp(-(t - W_STOP) * 7)
    # s08 handoff: the logo (300 px @ y 252) lifts away
    if t < TRUCK0 + .4:
        a = 1 - cub((t - START) / .36)
        lg = E.logo(300); ctx.add('screen', lg, 540, 252 - 70 * ein((t - START) / .36), alpha=a)
    draw_cards(ctx, t)
    if t >= SPIN0:
        r = phone_layer(t)
        p = clamp((t - SPIN0) / (SPIN1 - SPIN0))
        x, y, ry, rx, rz, s = phone_state(t)
        gl = phone_glow()
        if s > .5: ctx.add('front', gl if abs(s - 1) < .02 else gl.resize((int(gl.width * s), int(gl.height * s)), Image.BILINEAR), x, y + 20, alpha=.9 * cub(p))
        if r is not None:
            im, X, Y = r
            ctx.add('front', E.shadow(im, 34, .55, (0, 26)) if p >= 1 else im, X + (im.width / 2 if p >= 1 else 0), Y + (im.height / 2 if p >= 1 else 0), center=p >= 1)
        # landing pulse on REELS: a phone-shaped light edge that expands a little and dies (hugs the phone)
        lk = (t - W_REELS) / .32
        if 0 <= lk < 1:
            pr = phone_ring(); sc_ = s * (1.0 + .10 * eout(lk))
            im = pr.resize((int(pr.width * sc_), int(pr.height * sc_)), Image.BILINEAR)
            ctx.add('front', im, x, y, alpha=(1 - lk) ** 1.6)
    place_avatar(ctx, t, avs, avx)
    ctx.cap_y = 1532                 # 2-line pages (wider engine word spacing) stay inside the y <= 1640 safe area
    ctx.post['vignette'] = .38


def draw_B(ctx, t):
    lt = t - T23
    ctx.bg_img = C('studioB', lambda: studio_shift(-60, 1.05))
    z = 1.2 + .045 * smooth(lt / 1.4) + .02 * math.exp(-(t - W_SAVE) * 7) * (t >= W_SAVE)
    ctx.cam = dict(z=z, x=540., y=780., dx=0., dy=0., rot=0.)
    k = cub((t - CAR_IN0) / (CAR_IN1 - CAR_IN0 + .14))
    ke = expo((t - CAR_IN0) / .5)
    ry = math.radians(lerp(-62, -6, ke)) + math.radians(2) * math.sin(lt * 1.6)
    x = lerp(1180, CAR_X, ke); y = CAR_Y + 6 * math.sin(lt * 2.0)
    s = lerp(.82, 1.0, ke)
    art = carousel(t)
    add3d(ctx, 'screen', E.shadow(art, 30, .55, (0, 20)), x, y, ry, 0, 0, s, alpha=clamp((t - CAR_IN0) / .05), glass=0)
    # SAVE: ping around the bookmark + the Saved pill pops ABOVE the card
    bx_, by_ = x + (CAR_W / 2 - 40) * s, y + (CAR_H / 2 - 48) * s
    pk = (t - W_SAVE) / .38
    if 0 <= pk < 1: ctx.add('screen', ping_ring(26 + 46 * eout(pk), (1 - pk) ** 1.5), bx_, by_)
    if t >= W_SAVE:
        tk = t - W_SAVE
        ts = toast_saved(); sc = .55 + .45 * back(tk / .28, 2.6)
        im = ts.resize((max(1, int(ts.width * sc)), max(1, int(ts.height * sc))), Image.BILINEAR)
        ctx.add('screen', im, x + 40, y - CAR_H / 2 * s - 58 + 26 * (1 - cub(tk / .28)), alpha=clamp(tk / .05))
    place_avatar(ctx, t, 1.0, -215)
    ctx.post['vignette'] = .4


def draw_C(ctx, t):
    lt = t - T24
    pw = power(t)
    ctx.bg_img = lit_studio(40, 1.0, pw)
    z = 1.0 + .05 * smooth(lt / 2.3) + .055 * expo((t - W_BIG) / .35) * (t >= W_BIG)
    ctx.cam = dict(z=z, x=430., y=760., dx=0., dy=0., rot=0.)
    po = bright(poster_warm() if pw > .5 else poster_art(), lerp(.22, 1.0, pw))
    sk = (t - W_BRAND) / .55
    if 0 < sk < 1: po = sheen(po, sk, .12, .55)
    ctx.add('behind', E.shadow(po, 24, .65, (0, 16)), PO_X, PO_Y)
    # credit types on from BRAND and holds to the cut (screen space, safe margin x >= 110)
    if t >= CREDIT0:
        n = min(14, int((t - CREDIT0) / .022) + 1)
        cr = credit(n)
        ctx.add('screen', cr, 110 - 10, 1000 - cr.height / 2, center=False, alpha=clamp((t - CREDIT0) / .04))
    # the poster's light spills on him from the left
    place_avatar(ctx, t, .88, 195, bright_k=1.0 + .05 * pw)
    ctx.post['vignette'] = .45


LAP_TOP = 1150            # screen-space y of the laptop canvas top when landed


def draw_D(ctx, t):
    lt = t - T25
    ctx.avatar.update(s=1.0, x=0)
    ctx.bg_img = C('studioD', lambda: studio_shift(0, 1.04))
    # slow push, then a deliberate push-in after CUSTOMERS so the 48.16 cut to s10 (z 1.06) reads as a pull-out
    pk = inout((t - (W_CUSTOMERS + .12)) / .5)          # closing push-in progress (0..1, 47.65 -> 48.15)
    z = 1.06 + .05 * smooth(lt / 2.7) + .13 * pk
    ctx.cam = dict(z=z, x=540., y=760., dx=0., dy=0., rot=0.)
    ctx.cap_y = 310                  # 2-line pages keep their top inside the y >= 220 safe area
    # laptop rises (screen space foreground -> parallax against the camera push)
    k = cub((t - LAP0) / (LAP1 - LAP0))
    ke = expo((t - LAP0) / .55)
    sw = (t - (W_WEBSITE + .05)) / .6
    sw2 = (t - (W_CUSTOMERS - .05)) / .6
    lap = laptop_img(t, sweep=sw if 0 < sw < 1 else (sw2 if 0 < sw2 < 1 else None))
    top = lerp(2050, LAP_TOP, k) + 5 * math.sin(lt * 1.8) * k
    cy = top + lap.height / 2
    gl = C('lapglow', lambda: _lap_glow())
    ctx.add('screen', gl, 540, top + 250, alpha=.75 * k)
    rx = math.radians(lerp(38, 0, ke)); ry = math.radians(lerp(-10, 0, ke))
    if abs(rx) > .004 or abs(ry) > .004:
        add3d(ctx, 'screen', lap, 540, cy, ry, rx, 0, 1., f=2200)
    else:
        ctx.add('screen', lap, 540, cy)
    # notification drops onto the laptop's screen-top edge
    if t >= NOTIF:
        nk = t - NOTIF
        dy = lerp(-70, 0, back(nk / .3, 2.0)); a = clamp(nk / .07)
        ctx.add('screen', notif(), 540, top + lid_screen_top_y() + 4 + dy, alpha=a, glass=14)
    # followers -> customers: glass card LEFT of his head
    if t >= W_FOLLOWERS - .04:
        fk = t - (W_FOLLOWERS - .04)
        ck = clamp((t - (W_FOLLOWERS + .25)) / (W_CUSTOMERS - (W_FOLLOWERS + .25)))
        n = int(round(1284 * (1 - (1 - ck) ** 2.2)))
        show = clamp((t - (W_FOLLOWERS + .2)) / .12)
        pulse = math.exp(-(t - W_CUSTOMERS) * 5) if t >= W_CUSTOMERS else 0
        card = stat_card('12.4K', f'+{n:,}', show, pulse)
        sc = .75 + .25 * back(fk / .28, 2.2)
        if t >= W_CUSTOMERS: sc *= 1 + .05 * math.exp(-(t - W_CUSTOMERS) * 9)
        # closing push-in: the card is a FOREGROUND element, so it parallaxes outward faster than his head
        # (camera dolly past it) and dissolves -> its right edge always runs away from his ear, never over it.
        ex = pk
        sc *= 1 + .2 * ex
        im = card if abs(sc - 1) < .005 else card.resize((max(1, int(card.width * sc)), max(1, int(card.height * sc))), Image.BILINEAR)
        if ex > .04:
            im = im.filter(ImageFilter.BoxBlur(min(6., 9. * ex)))
        cx = 540 + (204 - 40 * (1 - cub(fk / .3)) - 540) * (1 + .6 * ex)
        cy = 690 + (690 - 960) * .25 * ex
        a = clamp(fk / .06) * (1 - smooth((ex - .25) / .45))
        if a > .003:
            ctx.add('screen', im, cx, cy, alpha=a, glass=12)
    ctx.post['vignette'] = .38


def _lap_glow():
    w, h = LID_W + 400, 800
    m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((200, 200, w - 200, h - 200), 60, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(80)).point(lambda v: int(v * .5))
    im = Image.new('RGBA', (w, h), (110, 90, 255, 0)); im.putalpha(m); return im


# ================================================================ draw
def draw(ctx, lt, t):
    if t < T23: draw_A(ctx, t)
    elif t < T24: draw_B(ctx, t)
    elif t < T25: draw_C(ctx, t)
    else: draw_D(ctx, t)
    draw_caps(ctx, t, ctx.cap_y, ctx.cap_size)
