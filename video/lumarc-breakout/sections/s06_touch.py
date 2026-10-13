"""s06 — THE PRODUCT YOU CAN ALMOST TOUCH (13.32–15.40).  "The product you can almost touch."

Still in his studio, but now the WORK is the subject: rack focus — he goes soft in the background, a phone takes the
foreground (frame-in-frame) playing the SILENCE ONE teardown film, and the product leaves the screen.

13.32  CUT to the wide angle (s05 ends on its 1.25x punch-in: -20 % scale, his head drops; focus racks off him): a
       phone rises into the bottom of frame with motion blur, tilted toward us, playing the teardown film's hero shot
       ("Hear nothing. Feel everything.").
13.50  "PRODUCT" (p-burst 13.50): BREAK-OUT. A burst of light from the screen, the glass ripples, and the headphone pushes OUT of the
       phone: it starts exactly where the film shows it (printed on the tilted screen) and stands up into 3-D space —
       while it crosses the bezel the part still inside is clipped by the screen and the part outside overlaps the phone
       frame (out-of-bounds pop-out). The phone tips back and becomes the plinth it hovers over; gold/violet sparks fly
       out of the screen. The product rotates through the turntable angles (real 3-D views), lit from below by the
       screen, its soft shadow cast on the glass; the film keeps playing (the teardown) under it. His hands frame it.
14.46  "ALMOST": macro push — the camera dives into the ear cup (zoom blur) and lands on the real macro texture of the
       protein-leather cushion and the champagne ring (rack focus breathing).
14.67  an (unseen) fingertip approaches from the lower right: its soft shadow converges on the leather and darkens...
14.93  "TOUCH." (t-burst 14.93, contact on the 14.933 frame): the protein leather DENTS under the fingertip (radial
       pinch of the grain, lit/shaded dent walls, contact occlusion, soft rebound), liquid-glass rings run across the
       leather (refraction + caustic crests, only on the surface), a small light pulse, haptic thud + micro-shake.
15.10  the leading ring becomes a liquid-lens iris wipe back to the studio (magnifying, chromatic rim); rack focus returns
       to him (hand-off to s07 at 15.40).

The product is the SILENCE ONE turntable (orbit0-2 sprite sheets) keyed off black (_C_kit.key_rgba: texture/brightness
body + luminance matte, un-premultiplied, defringed), sharpened, graded with a violet/blue monitor rim. Captions use the
measured onsets and sit at the top (the product and phone own the lower two thirds).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _C_kit as K

START, END = E.span(13, 13)                   # 13.32 – 15.40
W, H = E.W, E.H
clamp, lerp, smooth, kick = E.clamp, K.lerp, K.smooth, K.kick

# word onsets measured on src/tight16k.raw (10 ms RMS envelope, >3.5 kHz band, spectrogram)
WORD_FIX = {(13, 'THE'): 13.39, (13, 'PRODUCT'): 13.50, (13, 'YOU'): 14.09, (13, 'CAN'): 14.22, (13, 'ALMOST'): 14.45,
            (13, 'TOUCH.'): 14.93}
T_PRODUCT, T_PV = 13.495, 13.62              # "PRODUCT": p-burst 13.50 (break-out lands on the 13.500 frame) / stressed vowel
T_ALMOST, T_TOUCH, T_TV = 14.46, 14.93, 15.05     # TOUCH: t-burst 14.93-14.94 (contact on the 14.933 frame)
T_REVEAL = 15.10
PAGES = K.caption_pages(13, WORD_FIX)
CAP_Y = 330

CUES = [
    (START + .04, 'whoosh', {'gain': -6}),                 # the phone rises into frame
    (T_PRODUCT, 'impact', {'gain': -3}),                   # BREAK-OUT
    (T_PRODUCT, 'glass', {'seed': 3, 'gain': -6}),
    (T_PV, 'swoosh_up', {'gain': -5}),                     # the headphone rises out of the screen
    (T_PRODUCT + .04, 'shimmer', {'gain': -11}),
    (14.12, 'glass', {'seed': 7, 'gain': -13}),            # light sweep across the product
    (T_ALMOST + .14, 'whoosh', {'gain': -5}),              # macro dive
    (T_ALMOST, 'riser', {'to': T_TOUCH, 'gain': -8}),
    (T_TOUCH, 'thud', {'gain': 3}),                        # haptic thud
    (T_TOUCH, 'click', {'gain': -4}),
    (T_TOUCH + .02, 'shimmer', {'gain': -12}),
    (T_REVEAL + .03, 'swoosh_up', {'gain': -10}),          # ripple wipe back to the studio (15.10-15.17)
]


def C(k, fn): return E.cached(('s06',) + (k if isinstance(k, tuple) else (k,)), fn)


# ---------------------------------------------------------------- canonical phone (from the showcase s02)
SW, SH = 902, 1920
BEZ = 34; MARG = 10
PW0, PH0 = SW + 2 * BEZ, SH + 2 * BEZ
CW, CH = PW0 + 2 * MARG, PH0 + 2 * MARG
R_BODY, R_SCR = 150, 118
FILM_X0 = (1080 - SW) // 2                    # the 9:16 film is centre-cropped into the 902-wide screen


def _mask(w, h, r, ss=3):
    m = Image.new('L', (w * ss, h * ss)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def body():
    def mk():
        im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for (x0, y0, x1, y1) in [(2, 380, MARG + 4, 470), (2, 520, MARG + 4, 660), (2, 690, MARG + 4, 830), (CW - MARG - 4, 560, CW - 2, 780)]:
            d.rounded_rectangle((x0, y0, x1, y1), 4, fill=(70, 70, 86, 255))
        m = _mask(PW0, PH0, R_BODY)
        yy, xx = np.mgrid[0:PH0, 0:PW0].astype(np.float32)
        u = np.clip((xx / PW0) * .4 + (yy / PH0) * .6, 0, 1)
        c0, c1 = np.array([196, 186, 240], np.float32), np.array([38, 36, 54], np.float32)
        rim = (c0 + (c1 - c0) * u[..., None] ** .6)
        fr = Image.fromarray(rim.astype(np.uint8)).convert('RGBA'); fr.putalpha(m)
        im.alpha_composite(fr, (MARG, MARG))
        inner = _mask(PW0 - 8, PH0 - 8, R_BODY - 4)
        blk = Image.new('RGBA', (PW0 - 8, PH0 - 8), (8, 8, 12, 255)); blk.putalpha(inner)
        im.alpha_composite(blk, (MARG + 4, MARG + 4))
        return im
    return C('body', mk)


def scr_mask(): return C('smask', lambda: _mask(SW, SH, R_SCR))


def island():
    def mk():
        w, h = 250, 72; bl = Image.new('RGBA', (w, h), (0, 0, 0, 255)); bl.putalpha(_mask(w, h, h // 2)); return bl
    return C('island', mk)


def phone_state(t):
    """phone pose: centre, scale (canonical -> screen), rx (top away), ry, rz."""
    rise = K.expo((t - START + .02) / .22)
    cy = lerp(2420., 1560., rise); s = .50; rx = 20.; ry = lerp(-9., -4., rise); rz = lerp(5., 2.5, rise); cx = 540.
    b = K.eio((t - T_PRODUCT) / .36)
    rx = lerp(rx, 57., b); cy = lerp(cy, 1830., b); s = lerp(s, .63, b); ry = lerp(ry, 0., b); rz = lerp(rz, 0., b)
    if t > T_PRODUCT:   # settle drift
        x = t - T_PRODUCT
        cy += 5 * math.sin(x * 2.1); rz += .6 * math.sin(x * 1.6 + .5)
    return dict(cx=cx, cy=cy, s=s, rx=rx, ry=ry, rz=rz)


def phone_proj(st, pts):
    return K.proj_pts(pts, CW, CH, st['cx'], st['cy'], st['s'], st['rx'], st['ry'], st['rz'], f=2600.)


def phone_quad(st):
    return [(x, y) for x, y, _ in phone_proj(st, [(0, 0), (CW, 0), (CW, CH), (0, CH)])]


def screen_quad(st):
    x0, y0 = MARG + BEZ, MARG + BEZ
    return [(x, y) for x, y, _ in phone_proj(st, [(x0, y0), (x0 + SW, y0), (x0 + SW, y0 + SH), (x0, y0 + SH)])]


# ---------------------------------------------------------------- the product (turntable cells)
CELL_C = (245., 258.)                          # centre of the object in a turntable cell (cell 0 bbox centre)
FILM_HP_C, FILM_HP_W = (525., 952.), 744.      # the film's hero headphone (src 5.30): centre / width in film px
CELL_W0 = 286.                                 # object width in cell 0
FLOAT_C = (540., 1396.)                        # headband top ≈ y 1095: under his chin in the wide framing
FLOAT_SC = 1.50                                # cell px -> screen px when floating (object ~430 px wide)


def cell_index(t):
    """turntable angle: 3/4 view -> almost frontal while it comes out and floats."""
    if t < T_PRODUCT: return 0.0
    return 22 * (1 - (1 - clamp((t - T_PRODUCT) / 1.0)) ** 2.2) + 1.2 * clamp((t - 14.5) / .9)


def product_rect_float(t):
    """the 4 corners of the 520x520 cell when floating (screen px), with a gentle bob."""
    x = max(0.0, t - T_PRODUCT)
    cx = FLOAT_C[0] + 4 * math.sin(x * 1.3)
    cy = FLOAT_C[1] + 9 * math.sin(x * 2.4 + .3)
    sc = FLOAT_SC * (1 + .012 * math.sin(x * 1.7))
    rz = math.radians(1.2 * math.sin(x * 1.5 + 1.0))
    pts = []
    for X, Y in [(0, 0), (520, 0), (520, 520), (0, 520)]:
        dx, dy = (X - CELL_C[0]) * sc, (Y - CELL_C[1]) * sc
        pts.append((cx + dx * math.cos(rz) - dy * math.sin(rz), cy + dx * math.sin(rz) + dy * math.cos(rz)))
    return pts


def product_rect_screen():
    """the 4 corners of the cell printed on the phone screen exactly over the film's headphone at the break."""
    st = phone_state(T_PRODUCT); k = FILM_HP_W / CELL_W0
    pts = []
    for X, Y in [(0, 0), (520, 0), (520, 520), (0, 520)]:
        fx, fy = FILM_HP_C[0] + (X - CELL_C[0]) * k, FILM_HP_C[1] + (Y - CELL_C[1]) * k
        pts.append((fx - FILM_X0 + MARG + BEZ, fy + MARG + BEZ))
    return [(x, y) for x, y, _ in phone_proj(st, pts)]


Q_SCREEN = product_rect_screen()


def out_p(t):
    """break-out progress 0..1."""
    return 1 - (1 - clamp((t - T_PRODUCT) / .40)) ** 3


def product_quad(t):
    p = out_p(t)
    qf = product_rect_float(t)
    arc = -70 * math.sin(math.pi * clamp(p * 1.05))           # rises a little above its rest, settles
    grow = 1 + .07 * math.sin(math.pi * clamp(p * 1.1))       # surges toward the lens, settles
    cxf = sum(x for x, _ in qf) / 4; cyf = sum(y for _, y in qf) / 4
    q = []
    for (xs, ys), (xf, yf) in zip(Q_SCREEN, qf):
        xf2 = cxf + (xf - cxf) * grow; yf2 = cyf + (yf - cyf) * grow
        q.append((lerp(xs, xf2, p), lerp(ys, yf2, p) + arc))
    return q


def sharpen(img):
    def f(im): return im.filter(ImageFilter.UnsharpMask(1.6, 70, 2))
    return f(img)


def cell_img(k):
    """turntable cell, sharpened (it is shown ~1.5x), graded into the studio: cooler shadows and a violet / blue rim
    from the monitors behind him."""
    k = int(round(clamp(k, 0, 29)))
    return C(('cell', k), lambda: K.disk_cached(f'cellg_{k:02d}_r5', lambda: _cell_mk(k)))


def _cell_mk(k):
    from scipy.ndimage import minimum_filter, gaussian_filter
    im = solid_alpha(sharpen(K.orbit_cell(k))); a = np.asarray(im, np.float32)
    al = a[..., 3] / 255.
    band = np.clip(al - minimum_filter(al, size=7), 0, 1)
    band = gaussian_filter(band, 1.2)
    gx = np.linspace(-1, 1, a.shape[1], dtype=np.float32)[None, :]
    gy = np.clip(1.2 - np.linspace(0, 1, a.shape[0], dtype=np.float32)[:, None] * .9, 0, 1)
    rimc = np.where(gx[..., None] < 0, np.array([190, 110, 255], np.float32), np.array([120, 140, 255], np.float32))
    e = (band * (.25 + .40 * np.abs(gx)) * gy)[..., None] * .55
    rgb = a[..., :3] * np.array([1.0, .985, .99], np.float32)
    rgb = rgb * (1 - e) + rimc * e
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]).astype(np.uint8), 'RGBA')


def product_layer(t, st):
    """the warped product (RGBA, x0, y0) with the break-out clip, under-light and motion blur; None before the break."""
    if t < T_PRODUCT: return None
    q = product_quad(t)
    spr = cell_img(cell_index(t))
    # light from the screen below + the flash of the break
    x = t - T_PRODUCT
    fl = kick(x, .07)
    spr = underlight(spr, .55 + 1.2 * fl)
    w_ = K.warp(spr, q, margin=60)
    if w_ is None: return None
    img, x0, y0 = w_
    img = glint(img, t)
    p = out_p(t)
    if p < .62:   # out-of-bounds clip: visible inside the screen or above the phone's top edge
        sq = screen_quad(st)
        m = Image.new('L', img.size, 0); d = ImageDraw.Draw(m)
        d.polygon([(px - x0, py - y0) for px, py in sq], fill=255)
        (ax, ay), (bx, by) = sq[0], sq[1]
        # half-plane above the top edge (extended far left/right)
        dxe, dye = bx - ax, by - ay; L = math.hypot(dxe, dye) or 1; ux, uy = dxe / L, dye / L
        P1 = (ax - ux * 3000, ay - uy * 3000); P2 = (bx + ux * 3000, by + uy * 3000)
        d.polygon([(P1[0] - x0, P1[1] - y0), (P2[0] - x0, P2[1] - y0), (P2[0] - x0, P2[1] - y0 - 6000), (P1[0] - x0, P1[1] - y0 - 6000)], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(1.2))
        rel = clamp((p - .45) / .17)               # the clip releases as it is fully out
        if rel > 0: m = m.point(lambda v: int(v + (255 - v) * rel))
        img.putalpha(ImageChops.multiply(img.getchannel('A'), m))
    # motion blur (centre velocity over a 180-degree shutter)
    qa, qb = product_quad(t - 1 / 120), product_quad(t + 1 / 120)
    dx = sum(b[0] - a[0] for a, b in zip(qa, qb)) / 4; dy = sum(b[1] - a[1] for a, b in zip(qa, qb)) / 4
    if math.hypot(dx, dy) > 2:
        img, ox, oy = K.smear(img, dx, dy); x0 += ox; y0 += oy
    return img, x0, y0


def solid_alpha(im):
    """repair the turntable key: no see-through in the ear-cup shells (notches in the lower shells, pin holes) and no
    soft light-streak haze inside the headband arch (only a 3 px soft edge is kept along the arch)."""
    from scipy import ndimage as ndi
    a = np.asarray(im, np.float32).copy(); al = a[..., 3] / 255.
    body = al > .5
    holes = ndi.binary_fill_holes(body) & ~body
    lab, n = ndi.label(holes)
    big = np.zeros_like(body)
    if n:
        sz = ndi.sum(holes, lab, range(1, n + 1)); big = np.isin(lab, [i + 1 for i, s_ in enumerate(sz) if s_ > 600])
    al = np.where(holes & ~big, 1.0, al)
    al = np.where(big, al * np.clip(1 - ndi.distance_transform_edt(big) / 3., 0, 1), al)
    yy, xx = np.mgrid[-9:10, -9:10]; disk = xx * xx + yy * yy <= 81
    closed = ndi.binary_closing(np.pad(body, 12), structure=disk)[12:-12, 12:-12]
    lower = np.zeros_like(body); lower[290:, :] = True
    add = closed & ~body & lower & ~big
    al = np.where(add, np.maximum(al, .96), al)
    # the deep-shadow pocket at the bottom of the left ear cup (between the shell crescent and the cushion) keys out as
    # black -> the cup looked cut off. Fill that pocket (only it: left of x 220, never the gap between the cups) with
    # an opaque near-black shadow (+ the matching pocket under the right cup in the frontal cells).
    yy, xx = np.mgrid[-24:25, -24:25]; disk = xx * xx + yy * yy <= 576
    pocket = ndi.binary_closing(np.pad(body, 30), structure=disk)[30:-30, 30:-30] & ~body
    pocket[:330, :] = False
    lab, n = ndi.label(pocket)
    if n:
        keep = [i + 1 for i, (cy_, cx_) in enumerate(ndi.center_of_mass(pocket, lab, range(1, n + 1)))
                if (cx_ < 220 or (cx_ < 300 and cy_ > 400)) and (lab == i + 1).sum() > 150]
        pm = ndi.gaussian_filter(ndi.binary_dilation(np.isin(lab, keep), iterations=2).astype(np.float32), 1.0)
        pc = pm * (al < .9)                                   # recolour only the soft edge + pocket, not the cushion
        a[..., :3] = a[..., :3] * (1 - pc[..., None]) + np.array([16, 15, 18], np.float32) * pc[..., None]
        al = np.maximum(al, pm * .98)
    a[..., 3] = np.clip(al, 0, 1) * 255
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def underlight(spr, k):
    """warm/violet bounce light from the screen on the lower half of the product (additive)."""
    def grad():
        yy = np.linspace(0, 1, 520, dtype=np.float32)[:, None]
        g = np.clip((yy - .45) / .55, 0, 1) ** 1.6
        col = np.array([150, 110, 255], np.float32) * .55 + np.array([255, 196, 120], np.float32) * .45
        return (g[..., None] * col[None, None, :]).repeat(520, 1)
    g = C('ulight', grad)
    a = np.asarray(spr, np.float32)
    rgb = a[..., :3] + g * (.28 * k)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]).astype(np.uint8), 'RGBA')


# ---------------------------------------------------------------- the screen (frame-in-frame)
def film_at(src):
    fr = E.clip(E.TEARDOWN, (540, 960)).at(K.film_src(src))     # deterministic across chunked renders
    if fr is None: fr = Image.new('RGB', (540, 960), (8, 8, 10))
    return fr.crop((FILM_X0 / 2, 0, (FILM_X0 + SW) / 2, SH / 2)).resize((SW, SH), Image.BILINEAR)


def shadow_blob():
    def mk():
        S = 512; yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
        r = np.hypot((xx - S / 2) / (S / 2), (yy - S / 2) / (S / 2))
        a = np.clip(1 - r, 0, 1) ** 1.4
        im = Image.new('RGBA', (S, S), (0, 0, 4, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return C('shblob', mk)


def screen_content(t):
    """the phone screen (RGBA SW x SH): film, then after the break the teardown keeps playing under the product's shadow."""
    x = t - T_PRODUCT
    if x < 0:
        scr = film_at(K.FILM_KEY_T - (T_PRODUCT - t)).convert('RGBA')
    else:
        f = film_at(12.35 + x)
        f = Image.blend(f, Image.new('RGB', f.size, (6, 5, 10)), .22)
        scr = f.convert('RGBA')
        # the product's shadow on the glass (grows / sharpens as it settles above it)
        p = out_p(t)
        sw_, sh_ = int(SW * lerp(.6, .95, p)), int(SH * lerp(.16, .30, p))
        b = shadow_blob().resize((sw_, sh_), Image.BILINEAR)
        scr.alpha_composite(E.fade(b, .95 * p), ((SW - sw_) // 2, int(SH * .47 - sh_ / 2)))
        # light burst + glass ripple at the break
        if x < .5:
            scr = K.ripple(scr, SW / 2, SH * .48, x, amp=22, speed=2600, width=110, q=4, hl_gain=90, decay=.25).convert('RGBA')
        fl = kick(x, .07)
        if fl > .02:
            K.add_light(scr, burst_glow(), 0, 0, gain=min(1.0, 1.1 * fl))
    # glass glare (static diagonal sheen) + a moving glint at the break
    scr.alpha_composite(glare())
    return scr


def burst_glow():
    def mk():
        yy, xx = np.mgrid[0:SH // 4, 0:SW // 4].astype(np.float32) * 4
        r = np.hypot((xx - SW / 2) / (SW * .55), (yy - SH * .48) / (SW * .65))
        a = np.clip(1 - r, 0, 1) ** 1.3
        im = Image.new('RGBA', (SW // 4, SH // 4), (255, 230, 196, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.resize((SW, SH), Image.BILINEAR)
    return C('burst', mk)


def glare():
    def mk():
        yy, xx = np.mgrid[0:SH // 4, 0:SW // 4].astype(np.float32)
        u = (xx / (SW / 4)) * .55 + (yy / (SH / 4)) * .45
        a = np.clip(.10 - u * .12, 0, 1) + .05 * np.exp(-((u - .42) / .05) ** 2)
        im = Image.new('RGBA', (SW // 4, SH // 4), (255, 255, 255, 0)); im.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)))
        return im.resize((SW, SH), Image.BILINEAR)
    return C('glare', mk)


def phone_layer(t, st):
    ph = body().copy()
    scr = screen_content(t)
    ph.paste(scr.convert('RGB'), (MARG + BEZ, MARG + BEZ), scr_mask())
    isl = island(); ph.alpha_composite(isl, (CW // 2 - isl.width // 2, MARG + BEZ + 22))
    q = phone_quad(st)
    # entrance: vertical motion blur while it flies up (the warp keeps the part below the frame edge so the smear
    # stays opaque there — clipping it first made the body translucent at the bottom of frame)
    qa, qb = phone_quad(phone_state(t - 1 / 120)), phone_quad(phone_state(t + 1 / 120))
    dy = sum(b[1] - a[1] for a, b in zip(qa, qb)) / 4
    w_ = K.warp(ph, q, margin=10 + int(abs(dy) * .6))
    if w_ is None: return None
    img, x0, y0 = w_
    if abs(dy) > 2:
        img, ox, oy = K.smear(img, 0, dy); x0 += ox; y0 += oy
    return img, x0, y0


# ---------------------------------------------------------------- sparks out of the screen at the break
def sparks(fr, t, st):
    """tiny gold / violet sparks spat out of the screen edge at the break (one additive layer, motion-streaked)."""
    x = t - T_PRODUCT
    if not (0 <= x < .7): return
    rng = np.random.default_rng(11)
    sq = screen_quad(st); cx = sum(p[0] for p in sq) / 4; cy = sum(p[1] for p in sq) / 4
    items = []
    for i in range(18):
        side = -1 if i % 2 else 1
        ang = -math.pi / 2 + side * rng.uniform(.35, 1.25); sp = rng.uniform(600, 1500); d0 = rng.uniform(0, .04)
        x0 = cx + side * rng.uniform(120, 230); y0 = cy + rng.uniform(-260, -60); lf = rng.uniform(.30, .55)
        e = x - d0
        if e <= 0: continue
        px = x0 + math.cos(ang) * sp * e; py = y0 + math.sin(ang) * sp * e + 1400 * e * e
        life = 1 - e / lf
        if life <= 0: continue
        col = (255, 214, 150) if i % 3 else (196, 170, 255)
        vx, vy = math.cos(ang) * sp, math.sin(ang) * sp + 2800 * e
        n = math.hypot(vx, vy) or 1; L = min(26, n / 60)
        items.append((px, py, vx / n * L, vy / n * L, col, life))
    if not items: return
    X0 = int(min(p[0] for p in items)) - 40; Y0 = int(min(p[1] for p in items)) - 40
    X1 = int(max(p[0] for p in items)) + 40; Y1 = int(max(p[1] for p in items)) + 40
    cv = Image.new('RGBA', (X1 - X0, Y1 - Y0), (0, 0, 0, 0)); d = ImageDraw.Draw(cv)
    for px, py, lx, ly, col, life in items:
        d.line([(px - X0 - lx, py - Y0 - ly), (px - X0, py - Y0)], fill=col + (int(220 * life),), width=2)
    glow = cv.filter(ImageFilter.GaussianBlur(5))
    cv = cv.filter(ImageFilter.GaussianBlur(.7))
    out = Image.alpha_composite(glow, glow); out.alpha_composite(cv)
    K.add_light(fr, out, X0, Y0, gain=1.4)


# ---------------------------------------------------------------- the studio shot (him soft, phone + product)
def defocus(t):
    """background blur (rack focus): pulls off him as the phone arrives, back onto him for the hand-off."""
    b = lerp(1.0, 6.5, smooth((t - START) / .16))
    return lerp(b, 0.0, K.eio((t - T_REVEAL - .02) / .26))


def studio_shot(world, t, fg_blur=0.0):
    st = phone_state(t)
    world = world.convert('RGB')
    b = defocus(t)
    if b > .4: world = K.fast_blur(world, b)
    world = world.convert('RGBA')
    # the screen lights the space around the phone
    sq = screen_quad(st); scx = sum(p[0] for p in sq) / 4; scy = sum(p[1] for p in sq) / 4
    gs = C('spill', lambda: K.radial(400, (150, 120, 255), 1.6, .30).resize((1100, 900), Image.BILINEAR))
    K.add_light(world, gs, scx - 550, scy - 520)                 # light ADDS (screen blend): no grey veil
    bk = kick(t - T_PRODUCT, .1) if t >= T_PRODUCT else 0.0
    if bk > .03:
        gb = C('spill2', lambda: K.radial(400, (255, 214, 176), 1.8, .85).resize((1300, 1100), Image.BILINEAR))
        K.add_light(world, gb, scx - 650, scy - 640, gain=.75 * min(1.0, bk))
    ph = phone_layer(t, st)
    pr = product_layer(t, st)
    if fg_blur > .4:
        if ph is not None:
            p_ = int(fg_blur * 2.5) + 2; ph = (K.fast_blur(K.pad_img(ph[0], p_), fg_blur), ph[1] - p_, ph[2] - p_)
        if pr is not None:
            p_ = int(fg_blur * 2.5) + 2; pr = (K.fast_blur(K.pad_img(pr[0], p_), fg_blur), pr[1] - p_, pr[2] - p_)
    if ph is not None: K.paste(world, ph[0], ph[1], ph[2])
    if pr is not None and t > T_PRODUCT + .2: reflection(world, pr, st, t)
    sparks(world, t, st)
    if pr is not None:                            # (its shadow on the glass is painted into the screen content)
        K.paste(world, pr[0], pr[1], pr[2])
    return world


def reflection(world, pr, st, t):
    """the product mirrored in the glossy phone glass under it (faint, fading with distance, clipped to the screen)."""
    img, x0, y0 = pr
    bb = img.getchannel('A').getbbox()
    if not bb: return
    a = clamp((t - T_PRODUCT - .2) / .25)
    crop = img.crop(bb).transpose(Image.FLIP_TOP_BOTTOM)
    rh = max(4, int(crop.height * .55)); crop = crop.resize((crop.width, rh), Image.BILINEAR)
    g = C(('rgrad', rh), lambda: Image.fromarray((np.clip(1 - np.linspace(0, 1, rh), 0, 1) ** 1.6 * 255).astype(np.uint8)[:, None].repeat(4, 1)))
    fade_m = g.resize((crop.width, rh), Image.BILINEAR)
    rx0, ry0 = x0 + bb[0], y0 + bb[3] + 6
    m = Image.new('L', crop.size, 0)
    ImageDraw.Draw(m).polygon([(px - rx0, py - ry0) for px, py in screen_quad(st)], fill=255)
    al = ImageChops.multiply(ImageChops.multiply(crop.getchannel('A'), fade_m), m).point(lambda v: int(v * .30 * a))
    crop.putalpha(al)
    K.paste(world, crop.filter(ImageFilter.GaussianBlur(1.6)), rx0, ry0)


def glint(img, t):
    """a specular light sweep across the product's metal and fabric on "YOU" (masked by the product)."""
    p = (t - 14.10) / .34
    if not (0 < p < 1): return img
    w, h = img.size
    yy, xx = np.mgrid[0:h // 2, 0:w // 2].astype(np.float32)
    u = (xx / (w / 2)) * .72 + (yy / (h / 2)) * .28
    c = lerp(-.15, 1.15, K.eio(p))
    band = np.exp(-((u - c) / .06) ** 2) * .50 + np.exp(-((u - c + .07) / .015) ** 2) * .30
    a = Image.fromarray((np.clip(band, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    a = ImageChops.multiply(a, img.getchannel('A'))
    hl = Image.new('RGBA', (w, h), (255, 246, 228, 0)); hl.putalpha(a)
    out = img.copy(); out.alpha_composite(hl); return out


def world_cam(t):
    """13.32 CUT to the wide angle (s05 ends on its 1.25x punch-in: -20 % scale and his head drops ~70 px, with the rack
    focus and the phone rising — the pose jump reads as a multicam cut), then a slow push."""
    z = 1.0 + .055 * smooth((t - START) / 2.08)
    return dict(z=z, x=520., y=1400., dx=20., dy=0., rot=0.)


# ---------------------------------------------------------------- ALMOST: macro dive
def cup_point(t):
    """screen position of the right ear-cup's outer plate on the floating product."""
    q = product_rect_float(t); k = cell_index(t)
    u, v = lerp(300., 302., k / 22.) / 520., 330. / 520.
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
    tx, ty = lerp(x0, x1, u), lerp(y0, y1, u); bx, by = lerp(x3, x2, u), lerp(y3, y2, u)
    return lerp(tx, bx, v), lerp(ty, by, v)


TOUCH_P = (490., 1010.)                        # where the fingertip lands (screen), on the leather cushion
M_ANCHOR = (600., 430.)                        # macro.jpg pixel that sits under the touch point
M_SCALE = 1.75


def dive_img(shot, t, zc, z, kk):
    """the studio shot pushed into the ear cup: zoom about the cup point (which travels toward the touch point) with a
    radial zoom blur built from sub-frame zoom samples — rendered at half resolution (it is all motion blur anyway)."""
    q = 2; small = shot.convert('RGB').resize((W // q, H // q), Image.BILINEAR)
    tx, ty = TOUCH_P
    zp = dive_z(t - 1 / 60); n = int(clamp(math.log(max(z / zp, 1.0001)) / .011, 2, 16))   # <= ~1 % zoom per tap
    acc = None
    for i in range(n):
        zi = lerp(zp, z, (i + 1) / n)
        a = 1 / zi; cx, cy = zc[0] / q, zc[1] / q
        ox, oy = (zc[0] + (tx - zc[0]) * kk) / q, (zc[1] + (ty - zc[1]) * kk) / q
        im = small.transform(small.size, Image.AFFINE, (a, 0, cx - ox * a, 0, a, cy - oy * a), Image.BILINEAR)
        arr = np.asarray(im, np.float32); acc = arr if acc is None else acc + arr
    out = Image.fromarray((acc / n).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return out


def dive_z(t):
    return 1 + 5.0 * E.ein(clamp((t - T_ALMOST) / .30))


def macro_layer(t):
    """the macro still (RGB 1080x1920): leather + champagne ring, shallow focus, vignette, slow drift."""
    m = K.macro()
    x = t - T_ALMOST
    s = M_SCALE * lerp(.80, 1.0, K.expo((x - .12) / .32)) * (1 + .03 * clamp((t - 14.8) / .6))
    ax, ay = TOUCH_P[0] + 20 * (1 - clamp(x / .6)), TOUCH_P[1] - 10 * clamp((t - 14.7) / .7)
    dxs, dys = 0.0, 0.0
    if T_TOUCH <= t < T_TOUCH + .14:                   # haptic micro-shake
        kf = int((t - T_TOUCH) * E.FPS); tab = [(0, 0), (0, 7), (-5, -4), (3, 2), (-1, -1)]
        if kf < len(tab): dxs, dys = tab[kf]
    a = 1 / s
    img = m.transform((W, H), Image.AFFINE, (a, 0, M_ANCHOR[0] - (ax + dxs) * a, 0, a, M_ANCHOR[1] - (ay + dys) * a), Image.BICUBIC)
    # focus breathing: lands soft, sharpens by ~14.80
    fb = lerp(6.0, 0.0, K.eio((t - 14.58) / .26))
    if fb > .4: img = K.fast_blur(img, fb)
    # tilt-shift falloff (shallow DOF away from the touch band) + vignette + fade into black at top/bottom
    img = Image.composite(img, K.fast_blur(img, 7), dof_mask())
    a_ = np.asarray(img, np.float32) * vign()[..., None]
    return Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8))


def dof_mask():
    def mk():
        yy = np.arange(H, dtype=np.float32)
        a = np.exp(-((yy - TOUCH_P[1]) / 520.) ** 2)
        return Image.fromarray((np.repeat(a[:, None], W, 1) * 255).astype(np.uint8))
    return C('dofm', mk)


def vign():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = ((xx - TOUCH_P[0]) / 900.) ** 2 + ((yy - TOUCH_P[1]) / 1150.) ** 2
        v = np.clip(1.08 - .75 * r, 0, 1)
        top = np.clip((yy - 120) / 260, 0, 1); bot = np.clip((1880 - yy) / 320, 0, 1)
        return (v * np.minimum(top, 1) * bot).astype(np.float32)
    return C('vign', mk)


def finger_shadow(fr, t):
    """the (unseen) fingertip approaching the leather from the lower right: its soft round shadow (key light from the
    upper left) converges on the contact point, shrinking and darkening; it stays while the finger presses, then lifts."""
    x = (t - (T_TOUCH - .26)) / .26                      # approach 0 -> 1 (contact)
    lift = clamp((t - T_TOUCH - .18) / .16)              # lift-off after the press
    if x <= 0 or lift >= 1: return fr
    k = K.eout(clamp(x)) * (1 - .6 * lift)
    off = 1 - k
    blur = lerp(14., 46., off)
    a = .50 * K.smooth(clamp(x * 1.3)) * (1 - lift) ** 1.3
    if a < .02: return fr
    m = C('fpad', lambda: _fpad())
    bq = int(round(blur / 4)) * 4
    m2 = C(('fpad_b', bq), lambda: m.filter(ImageFilter.GaussianBlur(max(1, bq))))
    sc = lerp(1.0, 1.45, off)                                               # the closer the finger, the smaller its shadow
    m3 = m2.resize((int(m2.width * sc), int(m2.height * sc)), Image.BILINEAR)
    sh = Image.new('RGBA', m3.size, (2, 1, 4, 0)); sh.putalpha(m3.point(lambda v: int(v * a)))
    fr = fr.convert('RGBA')
    tx, ty = TOUCH_P[0] + 10 + 120 * off, TOUCH_P[1] + 14 + 140 * off
    K.paste(fr, sh, tx - m3.width * .40, ty - m3.height * .36)
    return fr


def _fpad():
    """fingertip shadow mask: a soft rounded pad, slightly elongated toward the lower right (the finger)."""
    S = 300; m = Image.new('L', (S, S)); d = ImageDraw.Draw(m)
    d.ellipse((80, 70, 200, 200), fill=255)
    d.ellipse((110, 110, 250, 290), fill=170)
    return m.rotate(-28, Image.BILINEAR, center=(140, 135))


def press_depth(e):
    """dent strength of the leather under the fingertip: presses in (2 frames), holds, releases with a soft rebound."""
    if e < 0: return 0.0
    if e < .17: return K.eout(e / .055)
    x = e - .17
    return math.exp(-x / .06) * math.cos(x * 20.)


def press_dent(fr, t):
    """the protein leather compresses under the fingertip: radial pinch of the grain + shading of the dent walls (key
    light from the upper left: the upper-left wall darkens, the lower-right wall catches light) + contact occlusion."""
    from scipy.ndimage import map_coordinates
    e = t - T_TOUCH; d = press_depth(e)
    if abs(d) < .02: return fr
    Rd = 112.; cx, cy = TOUCH_P
    X0, Y0 = int(cx - Rd - 4), int(cy - Rd - 4); S = int(2 * Rd + 8)
    base = fr.convert('RGB'); crop = np.asarray(base.crop((X0, Y0, X0 + S, Y0 + S)), np.float32)
    yy, xx = C('dent_grid', lambda: np.mgrid[0:S, 0:S].astype(np.float32))
    dx, dy = xx - (cx - X0), yy - (cy - Y0); r = np.sqrt(dx * dx + dy * dy) + 1e-3; u = np.clip(r / Rd, 0, 1)
    f = (1 - u * u) ** 2
    s = .16 * d * f                                                     # pinch: the grain is pulled toward the contact
    src = np.stack([cy - Y0 + dy * (1 + s), cx - X0 + dx * (1 + s)])
    out = np.stack([map_coordinates(crop[..., c], src, order=1, mode='nearest') for c in range(3)], -1)
    slope = 4 * 34. * d * u * (1 - u * u) / Rd                          # dh/dr of h = -D (1 - u^2)^2, D = 34 px
    hx, hy = slope * dx / r, slope * dy / r
    L = np.array([-.52, -.62, .58]); L = L / np.linalg.norm(L)
    nz = 1 / np.sqrt(1 + hx * hx + hy * hy)
    shade = ((-hx * L[0] - hy * L[1] + L[2]) * nz) / L[2] - 1
    ao = 1 - .50 * max(0.0, d) * np.exp(-(r / (.36 * Rd)) ** 2)
    out = out * (1 + 2.1 * shade)[..., None] * ao[..., None] + np.clip(shade, 0, None)[..., None] * 70
    m = Image.fromarray((np.clip(1.2 - u * 1.2, 0, 1) ** .5 * 255).astype(np.uint8))
    base.paste(Image.composite(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), Image.fromarray(crop.astype(np.uint8)), m), (X0, Y0))
    return base.convert('RGBA')


def touch_fx(fr, t):
    e = t - T_TOUCH
    if e < 0: return fr
    fr = press_dent(fr, t)
    # the press sends liquid-glass rings across the leather: a bright refracting crest + two inner echoes
    fr = K.ripple(fr, TOUCH_P[0], TOUCH_P[1], e - .03, amp=11, speed=880, width=70, q=1, hl_gain=120, decay=.42,
                  rings=((1.0, 1.0), (.66, .5), (.38, .28)), trough=.30, r0=95.).convert('RGBA')
    # a soft light pulse blooms from the contact
    g = K.radial(300, (255, 246, 236), 2.6, .55)
    pk = kick(e - .03, .07) if e >= .03 else 0.0
    if pk > .02: K.add_light(fr, g, TOUCH_P[0] - 150, TOUCH_P[1] - 150, gain=.7 * pk)
    return fr


# ---------------------------------------------------------------- frame
def draw(ctx, lt, t):
    ctx.cam = world_cam(t)
    ctx.captions = False
    P = ctx.post; P['vignette'] = .30

    need_world = t < T_ALMOST + .30 or t >= T_REVEAL
    if not need_world: ctx.full = C('black', lambda: Image.new('RGB', (W, H), (0, 0, 0)))

    def wrap(fr_world):
        if need_world:
            shot = studio_shot(fr_world, t, fg_blur=lerp(0, 3.0, K.eio((t - T_REVEAL) / .28)) if t >= T_REVEAL else 0.0)
        else:
            shot = None
        if t < T_ALMOST:
            fr = shot
        elif t < T_REVEAL:
            x = t - T_ALMOST
            if shot is not None:
                zc = cup_point(t); z = dive_z(t)
                tx, ty = TOUCH_P
                kk = E.ein(clamp(x / .30)) ** .8
                dz = dive_img(shot, t, zc, z, kk)
            else:
                dz = None
            a = K.smooth((x - .19) / .10)
            if a > 0 or dz is None:
                mac = macro_layer(t)
                mac = finger_shadow(mac, t)
                mac = touch_fx(mac, t)
            if dz is not None and a <= 0:
                fr = dz.convert('RGBA')
            elif dz is not None and a < 1:
                fr = Image.blend(dz.convert('RGB'), mac.convert('RGB'), a).convert('RGBA')
            else:
                fr = mac.convert('RGBA')
        else:
            # ripple wipe back to the studio
            rr = 140 + 2300 * K.eout((t - T_REVEAL) / .27) ** 1.4
            if rr < 1900:
                mac = touch_fx(macro_layer(t), t)
                fr = wipe(mac, shot, rr, t)
            else:
                fr = shot
        K.draw_caps(fr, t, PAGES, CAP_Y)
        return fr
    ctx.wrap = wrap


def lens_rim(shot, r, rr):
    """the wipe's edge is a liquid lens: just inside the rim the studio is magnified toward the centre with a slight
    chromatic split (half-res sampling, used only in the rim band; the centre stays full-res)."""
    from scipy.ndimage import map_coordinates
    band = np.exp(-((rr - r) / 85.) ** 2) * (r < rr + 40)
    if band.max() < .05: return shot
    small = np.asarray(shot.convert('RGB').resize((W // 2, H // 2), Image.BILINEAR), np.float32)
    yy, xx = C('grid', lambda: np.mgrid[0:H // 2, 0:W // 2].astype(np.float32))
    cx, cy = TOUCH_P[0] / 2, TOUCH_P[1] / 2
    ch = []
    for c, k in ((0, 1.10), (1, 1.0), (2, .90)):
        f = 1 - .16 * k * band
        ch.append(map_coordinates(small[..., c], [cy + (yy - cy) * f, cx + (xx - cx) * f], order=1, mode='nearest'))
    ref = Image.fromarray(np.clip(np.stack(ch, -1), 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    m = Image.fromarray((np.clip(band * 1.6, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return Image.composite(ref, shot.convert('RGB'), m)


def wipe(mac, shot, rr, t):
    """circular liquid wipe from the touch point: inside = studio, outside = macro, a bright refracting rim."""
    yy, xx = C('grid', lambda: np.mgrid[0:H // 2, 0:W // 2].astype(np.float32))
    r = np.hypot(xx * 2 - TOUCH_P[0], yy * 2 - TOUCH_P[1])
    m = np.clip((rr - r) / 60 + .5, 0, 1)
    rim = np.exp(-((r - rr) / 26) ** 2)
    mm = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    shot = lens_rim(shot, r, rr)
    out = Image.composite(shot.convert('RGB'), mac.convert('RGB'), mm).convert('RGBA')
    if rr > 10:
        rl = Image.fromarray((np.clip(rim * .55, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        hl = Image.new('RGBA', (W, H), (226, 214, 255, 0)); hl.putalpha(rl)
        out.alpha_composite(hl)
    return out
