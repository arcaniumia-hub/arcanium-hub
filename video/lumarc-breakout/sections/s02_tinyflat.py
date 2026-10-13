"""s02 — TINY / FLAT (4.00–5.32): "Tiny." / "Flat."
Word onsets measured on src/tight16k.raw: TINY 4.10 (t-burst; aspiration to 4.24, vowel 4.25) | FLAT 4.78 (f from 4.74,
voice 4.87).

  4.00  "Tiny." (jump cut = SMASH ZOOM-OUT): his Reel fills the screen, and in 4 frames the camera slams out (radial
        zoom blur) into the Explore page: a dense mosaic of hundreds of thumbnails under the app chrome (status bar,
        search field, tab bar). He is ONE tile, ~87 px. Lands with a small elastic undershoot on the word; a
        LUMARC-gradient ring draws itself around his tile; the word TINY is set TINY (38 px, glass tooltip) — the joke.
        The camera keeps drifting out: the grid keeps growing.
  4.72  "Flat." (jump cut = new framing, chrome gone): the whole plane FALLS BACK FLAT like a card dropping onto a
        table (gravity ease-in, hinge at the bottom, true motion blur of the fall), lands on the vowel of FLAT with a
        dead squash (no bounce) on the frame's centre line, and the colour drains to grey. FLAT. in flat, shadowless
        grey type; when the word is done (5.10) the WORD falls flat too (tips back on its baseline, lands 5.27, thud).
        The frame ends as a thin grey floor line: hard cut into s03's plain feed (his post centred, same eye line).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
import sections.feedkit as FK
from sections import _A_kit as K

START, END = E.span(4, 5)                                   # 4.00 – 5.32
T4, T5 = E.TL[4]['t0'], E.TL[5]['t0']                       # 4.00, 4.72 (jump cuts)
ONSETS = {(4, 'TINY.'): 4.10, (5, 'FLAT.'): 4.78}
W_TINY, W_FLAT = 4.10, 4.78
T_LANDZ = 4.13                                              # the smash zoom lands
T_FLAT_LAND = 4.86                                          # the plane lands flat (vowel of FLAT, 4.87)

CUES = [(T4, 'whoosh', {'gain': -2}), (T4 + .01, 'swoosh_up', {'gain': -10}),
        (W_TINY + .02, 'pop', {'gain': -9}), (W_TINY + .05, 'tick', {'gain': -14}),
        (T5 + .02, 'whoosh', {'gain': -9}), (T_FLAT_LAND, 'thud', {'gain': 0}),
        (5.12, 'whoosh', {'gain': -16}), (5.27, 'thud', {'gain': -11})]        # the word falls flat

W, H = E.W, E.H
clamp, lerp = E.clamp, K.lerp

# ---------------------------------------------------------------- the Explore grid (plane coords = 1x screen px)
PX, PY = 90, 112                    # cell pitch
TW, TH = 87, 109                    # tile (4:5) — 3 px gutters
NC, NR = 17, 40
HC, HR = 8, 20                      # his tile
HIS_CX, HIS_CY = HC * PX + TW / 2, HR * PY + TH / 2
TS = 1.5                            # texture scale


V = E.V
def _src_pool():
    """(image, weight, can_flip): the feed photos + LUMARC's SILENCE ONE product stills (product tiles on black)."""
    def mk():
        pool = []
        for n, w_, fl in [('loc1', 1.3, 1), ('loc2', 1.3, 1), ('loc3', 1.3, 1), ('loc4', 1.3, 1), ('loc5', 1.0, 1), ('loc6', 1.0, 1),
                          ('loc7', 1.3, 1), ('close_food', 1.2, 1), ('close_service', 1.2, 1), ('close_skill', 1.2, 1),
                          ('carousel_1', .6, 0), ('carousel_2', .6, 0), ('design_post', .5, 0), ('website', .4, 0),
                          ('bad_blurry_photo', .7, 1), ('bad_shaky_video', .7, 1), ('bad_flyer', .3, 0)]:
            pool.append((E.asset(n), w_, fl))
        for pth, w_ in [('silence-motion/img/hero.jpg', .35), ('silence-motion/img/macro.jpg', .35), ('silence-hyper/img/before.jpg', .2)]:
            pool.append((Image.open(f'{V}/{pth}').convert('RGB'), w_, 1))
        for k in range(2):
            sh = Image.open(f'{V}/silence-motion/img/orbit{k}.jpg').convert('RGB')
            for j in (1, 4, 7):
                c, r = j % 5, j // 5; pool.append((sh.crop((c * 520, r * 520, c * 520 + 520, r * 520 + 520)), .12, 1))
        return pool
    return K.C('s02_pool', mk)


def _tiles():
    """~680 varied thumbnails: random crops/grades of the photos + a few quiet text posts."""
    def mk():
        rng = np.random.default_rng(42); pool = _src_pool()
        wts = np.array([p[1] for p in pool]); wts = wts / wts.sum()
        tw, th = int(TW * TS), int(TH * TS)
        words = ['new menu', 'open late', 'link in bio', 'today only', 'hello fall', 'swipe ->', 'save this', 'pov:']
        muted = [(38, 52, 64), (64, 44, 40), (52, 58, 44), (70, 62, 52), (40, 40, 58), (88, 74, 60), (30, 30, 34), (210, 200, 186)]
        out = []
        for k in range(NC * NR):
            if rng.random() < .93:
                im, _, fl = pool[int(rng.choice(len(pool), p=wts))]
                sc = rng.uniform(.35, 1.0); ch = int(min(im.height, im.width * 1.25) * sc); cw = int(ch * .8)
                x = int(rng.uniform(0, im.width - cw + 1)); y = int(rng.uniform(0, im.height - ch + 1))
                t = im.crop((x, y, x + cw, y + ch)).resize((tw, th), Image.BILINEAR, reducing_gap=2.0)
                if fl and rng.random() < .5: t = t.transpose(Image.FLIP_LEFT_RIGHT)
                a = np.asarray(t, np.float32); g = rng.uniform(.78, 1.1); tint = rng.uniform(.9, 1.1, 3)
                t = Image.fromarray(np.clip(a * g * tint, 0, 255).astype(np.uint8))
            else:
                bgc = muted[int(rng.integers(len(muted)))]; t = Image.new('RGB', (tw, th), bgc); d = ImageDraw.Draw(t)
                fg = (24, 24, 26) if sum(bgc) > 450 else (236, 232, 224)
                d.text((tw / 2, th / 2), words[int(rng.integers(len(words)))], font=E.font(int(tw * .13), 500), fill=fg, anchor='mm')
            out.append(t)
        return out
    return K.C('s02_tiles', mk)


def texture():
    """the whole grid at TS x (RGB), his cell left black (drawn live)."""
    def mk():
        tl = _tiles(); im = Image.new('RGB', (int(NC * PX * TS), int(NR * PY * TS)), (0, 0, 0))
        for k, t in enumerate(tl):
            c, r = k % NC, k // NC
            if (c, r) == (HC, HR): continue
            im.paste(t, (int(c * PX * TS), int(r * PY * TS)))
        return im
    return K.C('s02_tex', mk)


def tex_mip(level):
    """texture mips: 0 = TS x, 1 = TS/2, 2 = TS/4, 3 = TS/8."""
    def mk():
        t = texture()
        return t.resize((t.width >> level, t.height >> level), Image.LANCZOS)
    return texture() if level == 0 else K.C(('s02_mip', level), mk)


def his_media(ctx, t):
    return FK.special_media(ctx, dict(z=1.16, x=540., y=820., dx=0., dy=30.))


# ---------------------------------------------------------------- TINY: smash zoom-out
S0 = W / TW                                                 # his tile fills the frame width
SCX, SCY = 540., 905.                                       # where his tile lands on screen


def tiny_scale(t):
    e = t - T4
    x = clamp(e / (T_LANDZ - T4))
    s = math.exp(math.log(S0) * (1 - (1 - (1 - x) ** 3)))    # log-space cubic-out: violent, readable
    if e > T_LANDZ - T4:                                    # elastic undershoot, then the slow drift out continues
        u = e - (T_LANDZ - T4)
        s *= 1 - .07 * math.exp(-u / .09) * math.sin(u * 22)
        s *= 1 - .26 * K.eout(u / (T5 - T_LANDZ))
    return s


def grid_frontal(S, cx, cy, ax, ay):
    """the grid plane frontal at scale S with grid point (ax, ay) on screen (cx, cy) -> RGB 1080x1920."""
    lvl = 0 if S * 1.0 >= TS * .55 else 1 if S >= TS * .28 else 2
    tex = tex_mip(lvl); ts = TS / (1 << lvl)
    return K.affine(tex, S / ts, (ax * ts, ay * ts), (cx, cy), (W, H), Image.BILINEAR)


def explore_chrome():
    """status bar + search field (top) and tab bar (bottom) of the Explore page (RGBA, full screen)."""
    def mk():
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        top = FK.chrome_top().crop((0, 0, W, FK.STATUS_H)); im.alpha_composite(Image.new('RGBA', (W, 190), FK.BG + (255,)))
        im.alpha_composite(top)
        d = ImageDraw.Draw(im); d.rounded_rectangle((28, 92, W - 28, 168), 22, fill=(38, 38, 40, 255))
        im.alpha_composite(FK.icon('search', 40, (168, 168, 168)), (52, 110))
        d.text((108, 130), 'Search', font=E.font(34, 400), fill=(168, 168, 168), anchor='lm')
        im.alpha_composite(FK.chrome_nav(), (0, FK.NAV_Y))
        return im
    return K.C('s02_chrome', mk)


def ring_img(w, h, prog, a=1.0):
    """LUMARC gradient ring around his tile, drawn on clockwise from 12 o'clock (prog 0..1)."""
    pad = 24; ss = 3; W2, H2 = w + 2 * pad, h + 2 * pad
    m = Image.new('L', (W2 * ss, H2 * ss)); ImageDraw.Draw(m).rounded_rectangle((pad * ss - 9 * ss, pad * ss - 9 * ss, (W2 - pad + 9) * ss, (H2 - pad + 9) * ss), 16 * ss, outline=255, width=5 * ss)
    m = m.resize((W2, H2), Image.LANCZOS)
    if prog < 1:
        pm = Image.new('L', (W2, H2)); ImageDraw.Draw(pm).pieslice((-W2, -H2, 2 * W2, 2 * H2), -90, -90 + 360 * prog, fill=255)
        m = Image.fromarray(np.minimum(np.asarray(m), np.asarray(pm)))
    g = E.gradient(W2, H2, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m.point(lambda v: int(v * a)))
    glow = Image.new('RGBA', (W2, H2), (130, 100, 255, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * .9 * a)))
    out = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(g); return out


def tiny_label():
    """TINY. at 38 px in a small glass tooltip (with a notch pointing up at his tile)."""
    def mk():
        f = E.font(38, 800); l, t_, r, b = f.getbbox('TINY.'); tw, th = r - l, b - t_
        pw, ph = tw + 34, th + 26; im = Image.new('RGBA', (pw + 8, ph + 22), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ox, oy = 4, 14
        d.rounded_rectangle((ox, oy, ox + pw, oy + ph), 16, fill=(16, 14, 26, 225), outline=(190, 178, 255, 150), width=2)
        cx = ox + pw / 2; d.polygon([(cx - 11, oy + 1), (cx + 11, oy + 1), (cx, oy - 11)], fill=(16, 14, 26, 225))
        d.line([(cx - 11, oy), (cx, oy - 11), (cx + 11, oy)], fill=(190, 178, 255, 150), width=2)
        d.text((ox + pw / 2 - (l + r) / 2 + l, oy + ph / 2 - (t_ + b) / 2 + t_), 'TINY.', font=f, fill=(250, 249, 246))
        return E.shadow(im, 10, .55, (0, 6))
    return K.C('s02_tiny_lbl', mk)


def smash_blur(t):
    """zoom-blur amount per frame of the smash: the cut frame is crisp, then the slam, then clean on landing."""
    f = (t - T4) * E.FPS
    return {1: 2.6, 2: 1.5, 3: .6}.get(int(round(f)), 0.0)


def tiny_phase(ctx, t):
    S = tiny_scale(t)
    fr = grid_frontal(S, SCX, SCY, HIS_CX, HIS_CY).convert('RGBA')
    # his live tile, at full resolution whatever the scale
    tw, th = TW * S, TH * S
    m = his_media(ctx, t)
    if tw < W * 1.6:
        tile = m.resize((max(2, int(round(tw))), max(2, int(round(th)))), Image.BILINEAR, reducing_gap=2.0 if tw < 500 else None)
        E._paste(fr, dict(img=tile.convert('RGBA'), xy=(int(round(SCX - tw / 2)), int(round(SCY - th / 2))), glass=0))
    zb = smash_blur(t)
    if zb > .02: fr = K.zblur(fr, zb, (SCX, SCY)).convert('RGBA')
    # the rest of the grid sits a touch darker so his ringed tile reads
    e = t - T_LANDZ
    if e > 0:
        k = .22 * K.smooth(e / .25)
        a = np.asarray(fr.convert('RGB'), np.float32); a *= 1 - k
        x0, y0 = int(round(SCX - tw / 2)), int(round(SCY - th / 2)); x1, y1 = x0 + int(round(tw)), y0 + int(round(th))
        a[max(0, y0):y1, max(0, x0):x1] /= (1 - k)
        fr = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
        rg = ring_img(int(round(tw)), int(round(th)), K.eout(e / .20), 1.0)
        fr.alpha_composite(rg, (int(round(SCX - rg.width / 2)), int(round(SCY - rg.height / 2))))
    # TINY. (tiny) pops under his tile on the word
    if t >= W_TINY:
        lb = tiny_label(); u = t - W_TINY; s = .55 + .45 * E.back(u / .14, 2.2)
        im = lb.resize((max(1, int(lb.width * s)), max(1, int(lb.height * s))), Image.BILINEAR) if abs(s - 1) > .01 else lb
        im = E.fade(im, clamp(u / .05))
        E._paste(fr, dict(img=im, xy=(int(SCX - im.width / 2), int(SCY + th / 2 + 18 - 12 * (1 - min(1, u / .1)))), glass=0))
    fr.alpha_composite(explore_chrome())
    return fr


# ---------------------------------------------------------------- FLAT: the plane falls back flat
PIV0, PIV1 = 1880., 1090.                                   # screen y of the hinge (the sheet's bottom edge): cut -> landed
                                                            # (lands on the frame's centre line: s03 opens centred too)
SF0, SF1 = .92, .70                                         # grid scale at the hinge: the camera follows the fall down/back
FCX, FCY = 540., 760.                                       # his tile on screen at the cut
GY_PIV = HIS_CY + (PIV0 - FCY) / SF0                        # the grid row that is the sheet's bottom edge


def flat_cam(t):
    k = K.eio(clamp((t - T5) / (T_FLAT_LAND + .04 - T5)))
    return lerp(PIV0, PIV1, k), lerp(SF0, SF1, k)


def flat_rx(t):
    """0 -> 84 degrees: falls back (gravity) from the cut, lands on the vowel of FLAT; dead squash, no bounce."""
    x = clamp((t - T5) / (T_FLAT_LAND - T5))
    rx = 84 * x ** 2.2
    if t > T_FLAT_LAND: rx = 84 + 1.2 * K.smooth((t - T_FLAT_LAND) / .45)
    return rx


def grey_bg():
    def mk():
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        c = np.array([40, 40, 41], np.float32) * (1 - .10 * yy) + np.array([4, 4, 4], np.float32) * yy
        return Image.fromarray(np.repeat(c, W, 1).astype(np.uint8)).convert('RGBA')
    return K.C('s02_grey', mk)


def flat_phase(ctx, t):
    rx = flat_rx(t)
    drain = K.smooth((t - (T_FLAT_LAND - .06)) / .16)      # colour drains as it lands
    # plane: grid point (gx, gy) -> hinge-based projection. Plane anchored so his tile sits at (FCX, FCY) frontal.
    gy_piv = GY_PIV; PIV_Y, S_F = flat_cam(t)
    P = K.Plane(HIS_CX, gy_piv, FCX, PIV_Y, S_F, rx, 0., 0., f=1900.)
    bg = Image.blend(K.void_bg().convert('RGB'), grey_bg().convert('RGB'), clamp(.35 + .65 * drain)).convert('RGBA')
    m = his_media(ctx, t)
    # draw in horizontal bands (each with its own mip, anisotropic) so the receding grid does not alias
    tex = texture(); band = 2
    squash = 1 - .035 * math.exp(-max(0., t - T_FLAT_LAND) / .06) if t > T_FLAT_LAND else 1.0
    falling = T5 < t < T_FLAT_LAND + .02
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)) if falling else bg
    for r0 in range(0, NR, band):
        r1 = min(NR, r0 + band)
        gy0, gy1 = r0 * PY, min(r1 * PY, gy_piv)
        if gy1 - gy0 < 4: continue
        q = [P.proj(0, gy0)[:2], P.proj(NC * PX, gy0)[:2], P.proj(NC * PX, gy1)[:2], P.proj(0, gy1)[:2]]
        if squash != 1: q = [(x, PIV_Y + (y - PIV_Y) * squash) for x, y in q]
        ys = [p[1] for p in q]
        if max(ys) < -40 or min(ys) > H + 40: continue
        strip = tex.crop((0, int(gy0 * TS), tex.width, int(gy1 * TS))).convert('RGBA')
        if HR in range(r0, r1) and HR * PY < gy1:          # his live tile inside this band
            tl = m.resize((int(TW * TS), int(TH * TS)), Image.BILINEAR, reducing_gap=2.0)
            strip.paste(tl, (int(HC * PX * TS), int((HR * PY - gy0) * TS)))
        K.warp_into(lay, strip, q, pad=1, aniso=True)
    if falling:          # motion blur of the fall: the sheet's previous-frame pose is a vertical stretch about a fixed
        Sm, y_fix = fall_stretch(t)                         # line (hinge follow + foreshortening), 180-degree shutter
        if Sm is not None: lay = vstretch_blur(lay, Sm, y_fix, passes=4 if abs(Sm - 1) > .5 else 3)
        bg.alpha_composite(lay)
    # FLAT. — flat grey shadowless type, standing; when the word is done it FALLS FLAT itself (hinged at its baseline,
    # tips back onto the floor like the feed did, gravity ease-in) and lands dead on the cut
    if t >= T_FLAT_LAND - .02:
        u = t - (T_FLAT_LAND - .02)
        ty = flat_type(); im = E.fade(ty, clamp(.5 + u / .04))
        phi = word_fall(t)
        if phi < .3: bg.alpha_composite(im, (int(W / 2 - im.width / 2), int(TY_BASE - im.height)))
        else:
            Pt = K.Plane(im.width / 2, im.height, W / 2, TY_BASE, 1.0, phi, 0., 0., f=1900.)
            q = [Pt.proj(0, 0)[:2], Pt.proj(im.width, 0)[:2], Pt.proj(im.width, im.height)[:2], Pt.proj(0, im.height)[:2]]
            K.warp_into(bg, im, q, pad=2, aniso=True)
    cr = .04 * K.smooth((t - T_FLAT_LAND) / (END - T_FLAT_LAND))      # the camera creeps in on the dead feed
    if cr > .001: bg = K.affine(bg.convert('RGB'), 1 + cr, (540, PIV1 - 60), (540, PIV1 - 60), (W, H), Image.BICUBIC).convert('RGBA')
    return bg, drain


TY_BASE = PIV1 - 122.                                       # FLAT.'s baseline on screen (just behind the floor sliver)
WF0, WF1 = 5.10, 5.27                                       # the word falls flat (after the voice ends at 5.07)
def word_fall(t):
    """0 -> 86 degrees: tips back with gravity (ease-in), lands dead at WF1 with a 2-degree settle."""
    if t < WF0: return 0.0
    if t < WF1: return 86 * ((t - WF0) / (WF1 - WF0)) ** 2.2
    return 86 + 1.5 * (1 - math.exp(-(t - WF1) / .03))


def _top_y(t):
    """screen y of the sheet's far (top) edge and of the hinge at time t."""
    PIV_Y, S_F = flat_cam(t)
    P = K.Plane(HIS_CX, GY_PIV, FCX, PIV_Y, S_F, flat_rx(t), 0., 0., f=1900.)
    return P.proj(HIS_CX, 0)[1], PIV_Y


def fall_stretch(t, shutter=.5 / E.FPS):
    """the previous pose maps y -> y_fix + (y - y_fix) * S (S, y_fix) over the shutter interval."""
    yt, ht = _top_y(t); yp, hp = _top_y(t - shutter)
    if abs(ht - yt) < 2: return None, None
    S = (hp - yp) / (ht - yt)
    if abs(S - 1) < .004: return None, None
    return S, (hp - ht * S) / (1 - S)


def vstretch_blur(img, S, y_fix, passes=3):
    """average of img stretched vertically about y_fix by log-even factors 1..S (recursive doubling)."""
    n = 2 ** passes; r = abs(S) ** (1.0 / (n - 1)); out = img
    for k in range(passes - 1, -1, -1):
        f = r ** (2 ** k)
        st = out.transform(out.size, Image.AFFINE, (1, 0, 0, 0, 1 / f, y_fix * (1 - 1 / f)), Image.BILINEAR)
        out = Image.blend(out, st, .5)
    return out


def flat_type():
    def mk():
        f = E.font(176, 600); l, t_, r, b = f.getbbox('FLAT.')
        im = Image.new('RGBA', (r - l + 8, b - t_ + 8), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4 - l, 4 - t_), 'FLAT.', font=f, fill=(138, 138, 138, 255)); return im
    return K.C('s02_flat_type', mk)


# ---------------------------------------------------------------- frame
def draw(ctx, lt, t):
    ctx.captions = False
    P = ctx.post
    if t < T5:
        ctx.full = tiny_phase(ctx, t)
        P['vignette'] = .22; P['grain'] = .7
    else:
        fr, drain = flat_phase(ctx, t)
        ctx.full = fr
        P['sat'] = 1 - drain; P['vignette'] = .22 * (1 - drain); P['grain'] = .7 - .3 * drain
