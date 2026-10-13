"""s10 — "You run the business. / We make it impossible to ignore." (48.16–51.08)

48.16  CUT to a calm, symmetrical medium close-up (z 1.42 settling to 1.34, then a slow pull to 1.28 — a clearly new
       framing after s09's z 1.11 laptop shot, with a 3-frame zoom-blur settle). The breath before the climax; the studio racks out of focus,
       an elegant sentence-case line "You run the business." fades up word by word (a different, quieter typographic
       voice than the rest of the Reel) with a hairline that draws out under "business".
49.24  CUT (jump) to an extreme close-up (z 1.58, face high in frame). "WE MAKE IT" word-pop captions.
49.95  SIGNATURE — "IMPOSSIBLE" (on the stressed "POSS"; "WE MAKE IT" rides the punch-out): punch-out (the frame pulls back, he shrinks into depth) while the founder SPLITS into
       four holographic copies — additive light, luminance-only, #4f6bff left / #9a4dff right, scanlines, edge glow,
       fading out towards the torso — that slide out with ghost trails. The founder and the copies are drawn by this
       section with feathered plate edges (no cardboard-cutout borders).
       Behind them a wall of outlined IMPOSSIBLE rows slams in from alternating sides; the centre row fills with the
       LUMARC gradient — huge type BEHIND him (his head overlaps the letters).
50.50  "TO" pops in FRONT of him.  50.45 the copies get sucked back into him (accelerating trails)...
50.65  "IGNORE" slams in front (on "ig-NORE") (scale 2.5 -> 1) — additive violet light bloom (not a grey flash), screen shake, short
       chromatic burst, echo outlines, punch-in.
       Final poster frame: IMPOSSIBLE (behind) + founder + TO IGNORE (front) = layered depth.
50.96  whip exit: accelerating push-in + zoom blur into the s11 cut.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E

START, END = E.span(26, 27)            # 48.16 – 51.08
T27 = E.TL[27]['t0']                    # 49.24 jump cut
# word onsets re-measured on the mixed voice (src/tight16k.raw = tight.mov audio, edit timeline; spectrogram +
# low/high band envelopes — see out/F/polish/spec_s10b.png). The older values (voice16k) ran 0.1–0.3 s early.
W_YOU, W_RUN, W_THE, W_BUS = 48.22, 48.40, 48.60, 48.72
W_WE, W_MAKE, W_IT = 49.30, 49.49, 49.65     # "make" k-burst 49.63 -> "it"
W_IMP = 49.95                           # "im-POSS": p-burst (word onset "im" 49.78)
W_TO = 50.50                            # t-burst
W_IGN = 50.65                           # "ig-NORE": stressed syllable (engine word_time 50.66) — THE hit
COLLAPSE = W_IGN - .20                  # copies start rushing back in (on "-ble to")
EXIT = END - .12                        # whip out into s11

CUES = [
    (START, 'swipe', {'gain': -14}),                 # soft cut into the calm frame
    (W_BUS, 'shimmer', {'gain': -14}),               # hairline draws under "business"
    (T27, 'whoosh', {'gain': -10}),                  # jump cut to the close-up
    (W_IMP - .06, 'whoosh', {}),                     # pull back + split
    (W_IMP, 'impact', {'gain': -3}),                 # IMPOSSIBLE wall slams
    (W_IMP + .03, 'glitch', {'gain': -8}),           # RGB-split clones
    (W_TO, 'tick', {'gain': -6}),                    # "TO"
    (COLLAPSE, 'swoosh_up', {'gain': -4}),           # clones sucked back in
    (W_IGN, 'impact', {}),                           # IGNORE
    (W_IGN, 'boom', {}),
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def C(k, fn): return E.cached(('s10',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0


def film_of(ctx):
    """the engine's Film (to read the keyed avatar frame for our own tinted clones)."""
    for c in (ctx.compose.__closure__ or ()):
        v = c.cell_contents
        if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    return None


def scale_im(im, s):
    if abs(s - 1) < .01: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)


# ================================================================ calm type (TL26)
def calm_word(text, wght):
    """-> (img, ink width, baseline y inside img)"""
    def mk():
        f = E.font(82, wght); l, _, r, _ = f.getbbox(text); _, t, _, b = f.getbbox('Hgy'); pad = 40
        w, h = r - l + 2 * pad, b - t + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sh = Image.new('RGBA', (w, h), (4, 4, 10, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .9)))
        out.alpha_composite(sh, (0, 4))
        c = Image.new('RGBA', (w, h), E.WHITE + (0,)); c.putalpha(m); out.alpha_composite(c)
        return out, r - l, pad - t + f.getmetrics()[0]
    return C(('calm', text, wght), mk)


CALM = [('You', W_YOU, 380), ('run', W_RUN, 380), ('the', W_THE, 380), ('business.', W_BUS, 650)]


def calm_type(ctx, t):
    y = 1415; gap = 22
    ims = [calm_word(w, wg) for w, _, wg in CALM]
    tot = sum(iw for _, iw, _ in ims) + gap * (len(ims) - 1)
    x = W / 2 - tot / 2
    out_k = clamp((T27 - .03 - t) / .12)
    bx0 = bx1 = base = None
    for (w, t0, wg), (im, iw, bl) in zip(CALM, ims):
        k = eout((t - t0 + .02) / .38)
        if k > 0:
            ctx.add('screen', im, x + iw / 2, y + 18 * (1 - k), alpha=k * out_k)
        if w == 'business.':
            # hairline only under the word itself (ink extent, without the period)
            f = E.font(82, wg); bx0 = x; bx1 = x + f.getlength('business'); base = y - im.height / 2 + bl
        x += iw + gap
    # hairline draws out (left -> right) under "business", 14 px below the baseline
    k = expo((t - W_BUS - .05) / .55)
    if k > 0 and bx0 is not None:
        lw = int(bx1 - bx0)
        ln = C(('hair', lw), lambda: _hairline(lw))
        wln = max(2, int(lw * k))
        ctx.add('screen', ln.crop((0, 0, wln, ln.height)), bx0, base + 14 - ln.height / 2, center=False, alpha=.95 * out_k)


def _hairline(lw):
    g = E.gradient(lw, 3, E.GRAD_LIGHT).convert('RGBA')
    a = np.full((3, lw), 255, np.float32); a[0] *= .45; a[2] *= .45
    ramp = np.clip(np.minimum(np.arange(lw), lw - 1 - np.arange(lw)) / 10, 0, 1)[None, :]
    g.putalpha(Image.fromarray((a * ramp).astype(np.uint8))); return g


# ================================================================ captions (own, voice-synced)
def pop_words(ctx, t, words, a, z, y=1450, base=92):
    if not a <= t < z: return
    ims = [E.word_img(w, base, st)[0] for w, _, st in words]
    gap = base * .34; widths = []
    for w, _, st in words:
        l, tp, r, b = E.font(base).getbbox(w); widths.append(r - l)
    x = W / 2 - (sum(widths) + gap * (len(words) - 1)) / 2
    for (w, t0, st), im, ww in zip(words, ims, widths):
        if t >= t0 - .02:
            lt = t - t0 + .02; s = (.72 + .28 * back(lt / .16)) * (1.06 if .05 < lt < .3 else 1)
            al = clamp(lt / .05) * clamp((z - t) / .06)
            ctx.add('screen', scale_im(im, s), x + ww / 2, y, alpha=al)
        x += ww + gap


WE_MAKE_IT = [('WE', W_WE, 'white'), ('MAKE', W_MAKE, 'white'), ('IT', W_IT, 'white')]


# ================================================================ IMPOSSIBLE wall (behind)
WALL_SIZE = 150
ROW_H = 160
WALL_Y0 = 552                          # centre of the solid row (world)


def _text_masks(text, size, wght=900, track=-6, stroke=2):
    f = E.font(size, wght)
    ws = []
    for ch in text:
        l, t, r, b = f.getbbox(ch); ws.append(f.getlength(ch))
    tot = int(sum(ws) + track * (len(text) - 1)) + 2 * 20
    asc = f.getbbox('I')
    h = asc[3] - asc[1] + 2 * 20
    fill = Image.new('L', (tot, h)); strk = Image.new('L', (tot, h))
    df, ds = ImageDraw.Draw(fill), ImageDraw.Draw(strk)
    x = 20
    for ch, w in zip(text, ws):
        df.text((x, 20 - asc[1]), ch, font=f, fill=255)
        ds.text((x, 20 - asc[1]), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
        x += w + track
    return fill, strk


def wall_word_solid():
    def mk():
        fill, strk = _text_masks('IMPOSSIBLE', WALL_SIZE)
        w, h = fill.size
        out = Image.new('RGBA', (w + 120, h + 120), (0, 0, 0, 0))
        glow = Image.new('RGBA', out.size, (110, 80, 255, 0))
        big = Image.new('L', out.size); big.paste(fill, (60, 60))
        glow.putalpha(big.filter(ImageFilter.GaussianBlur(34)).point(lambda v: int(v * .75)))
        out.alpha_composite(glow)
        g = E.gradient(w, h, [(96, 124, 255), (128, 104, 255), (176, 102, 255)]).convert('RGBA'); g.putalpha(fill)
        # subtle top highlight inside the letters
        hl = np.linspace(1.18, .92, h, dtype=np.float32)[:, None, None]
        ga = np.asarray(g, np.float32); ga[..., :3] = np.clip(ga[..., :3] * hl, 0, 255)
        out.alpha_composite(Image.fromarray(ga.astype(np.uint8)), (60, 60))
        return out
    return C('wsolid', mk)


def wall_row(style):
    """a long strip 'IMPOSSIBLE  IMPOSSIBLE  ...' in outline (style 0) or dim fill (style 1)."""
    def mk():
        fill, strk = _text_masks('IMPOSSIBLE', WALL_SIZE, stroke=2)
        w, h = fill.size; gap = 70; n = 5
        rowL = Image.new('L', (n * (w + gap), h))
        if style == 0:
            m = Image.fromarray(np.clip(np.asarray(strk, np.int16) - np.asarray(fill, np.int16), 0, 255).astype(np.uint8))
            m = m.point(lambda v: int(v * .55 * .95))      # row opacity baked in (no per-frame fade)
        else:
            m = fill.point(lambda v: int(v * .16))
        for i in range(n): rowL.paste(m, (i * (w + gap), 0))
        col = (200, 196, 255) if style == 0 else (120, 110, 255)
        out = Image.new('RGBA', rowL.size, col + (0,)); out.putalpha(rowL)
        return out, w + gap
    return C(('wrow', style), mk)


def outline_word():
    """single outline IMPOSSIBLE matching the solid one (for the centre row before it fills)."""
    def mk():
        fill, strk = _text_masks('IMPOSSIBLE', WALL_SIZE, stroke=2)
        m = Image.fromarray(np.clip(np.asarray(strk, np.int16) - np.asarray(fill, np.int16), 0, 255).astype(np.uint8))
        out = Image.new('RGBA', (fill.width + 120, fill.height + 120), (0, 0, 0, 0))
        o = Image.new('RGBA', fill.size, (220, 216, 255, 0)); o.putalpha(m)
        out.alpha_composite(o, (60, 60)); return out
    return C('woutline', mk)


def wipe_alpha(im, k, soft=60):
    """reveal im left->right (k 0..1) with a soft edge."""
    if k >= 1: return im
    if k <= 0: return None
    w = im.width; x = np.arange(w, dtype=np.float32)
    edge = lerp(-soft, w + soft, k)
    ramp = np.clip((edge - x) / soft + .5, 0, 1)
    a = (np.asarray(im.getchannel('A'), np.float32) * ramp[None, :]).astype(np.uint8)
    out = im.copy(); out.putalpha(Image.fromarray(a)); return out


def draw_wall(ctx, t):
    lt = t - W_IMP
    if lt < -.04: return
    # rows: offsets from the solid row
    rows = [(-2, 0), (-1, 1), (1, 0), (2, 1), (3, 0), (4, 1), (5, 0)]
    for k, (r, st) in enumerate(rows):
        img, period = wall_row(st)
        d = 1 if r % 2 else -1
        ent = expo((lt - .02 * abs(r)) / .42)
        if ent <= 0: continue
        drift = d * 70 * lt
        off = (d * -1) * 1100 * (1 - ent)
        x = W / 2 - img.width / 2 + ((drift + off + 0.5 * period) % period) - period / 2
        y = WALL_Y0 + r * ROW_H
        xi = int(round(x)); c0, c1 = max(0, -xi), min(img.width, W - xi)     # only the visible slice
        if c1 > c0:
            ctx.add('behind', img.crop((c0, 0, c1, img.height)), xi + c0, y - img.height / 2, center=False, alpha=ent)
    # centre row: outline snaps in, the gradient wipes in through it
    s = 1 + .22 * (1 - expo(lt / .28)) + .025 * clamp((t - W_IMP) / 1.6)
    ol = outline_word()
    ctx.add('behind', scale_im(ol, s), W / 2, WALL_Y0, alpha=clamp(lt / .05))
    sol = wipe_alpha(wall_word_solid(), eout((lt - .02) / .22))
    if sol is not None:
        ctx.add('behind', scale_im(sol, s), W / 2, WALL_Y0)
    # light riding the wipe edge — clipped to the glyphs (no free-floating vertical streak)
    k = (lt - .02) / .22
    if 0 < k < 1:
        ctx.add('behind', scale_im(edge_light(eout(k)), s), W / 2, WALL_Y0, alpha=1 - k * .5)


def edge_light(k):
    sol = wall_word_solid(); w, h = sol.size
    m = C('wfillmask', lambda: np.asarray(_text_masks('IMPOSSIBLE', WALL_SIZE)[0], np.float32) / 255)
    soft = 60; edge = lerp(-soft, w + soft, k) + soft / 2 - 60   # wipe_alpha's reveal boundary, in mask coords
    x = np.arange(m.shape[1], dtype=np.float32)[None, :]
    band = np.exp(-((x - edge) / 22) ** 2)
    a = np.zeros((h, w), np.float32); a[60:60 + m.shape[0], 60:60 + m.shape[1]] = m * band
    im = Image.new('RGBA', (w, h), (240, 236, 255, 0)); im.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)))
    return im


# ================================================================ founder + holographic clones (drawn here, feathered)
AV_S = .86                              # founder scale during the split (pulled back into depth)
HOLO = {-1: np.array([79, 107, 255], np.float32), 1: np.array([154, 77, 255], np.float32)}


def feather_mask():
    """multiplier for the plate alpha: soft 110 px ramps at the plate's left/right borders and a fade into the
    bottom corners, so a scaled-down plate never shows straight 'cardboard' cut lines."""
    def mk():
        x = np.arange(W, dtype=np.float32)[None, :]; y = np.arange(H, dtype=np.float32)[:, None]
        side = np.clip(np.minimum(x, W - 1 - x) / 110, 0, 1); side = side * side * (3 - 2 * side)
        cx = np.clip((W / 2 - np.abs(x - W / 2)) / 340, 0, 1)
        bot = np.clip((H - y) / 320, 0, 1)
        return (side * (1 - (1 - cx) * (1 - bot))).astype(np.float32)
    return C('feather', mk)


_FA = {}
def feathered(av):
    if _FA.get('k') is av: return _FA['v']
    a = np.asarray(av.getchannel('A'), np.float32) * feather_mask()
    out = av.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8)))
    _FA.update(k=av, v=out); return out


def add_founder(ctx, t, s):
    """the founder as our own 'behind' layer (on top of all other behind layers), plate edges feathered."""
    F = film_of(ctx)
    if F is None: ctx.avatar.update(s=s); return
    ctx.avatar['show'] = False
    av = scale_im(feathered(F.av.frame(t)), s)
    ctx.add('behind', av, 540 - av.width / 2, H - av.height, center=False)


_HO = {}
def holo_pair(av):
    """luminance-only light copies of the founder at HALF resolution, cropped to where they have any light:
    -> (x0, y0, {-1: blue RGBA uint8, 1: violet RGBA uint8}) in half-res plate coordinates.
    Additive-looking over the dark set: dark hoodie -> transparent, face/hands -> light, plus an edge glow and
    2 px scanlines; fades out towards the torso. Computed once per avatar frame."""
    if _HO.get('k') is av: return _HO['v']
    h2 = av.reduce(2)
    al8 = h2.getchannel('A')
    bb = al8.getbbox()
    if bb is None:
        v = (0, 0, None); _HO.update(k=av, v=v); return v
    # the light only exists above y=1700 (full res) -> crop rows first, 8 px margin for the edge blur
    x0, y0, x1, y1 = max(0, bb[0] - 8), max(0, bb[1] - 8), min(W // 2, bb[2] + 8), min(850, bb[3] + 8)
    if y1 <= y0:
        v = (0, 0, None); _HO.update(k=av, v=v); return v
    h2c, alc = h2.crop((x0, y0, x1, y1)), al8.crop((x0, y0, x1, y1))
    A = np.asarray(h2c, np.float32)
    a = A[..., 3] * (1 / 255)
    lum = (A[..., 0] * .3 + A[..., 1] * .59 + A[..., 2] * .11) * (1 / 255)
    edge = np.clip(a - np.asarray(alc.filter(ImageFilter.GaussianBlur(5)), np.float32) * (1 / 255), 0, 1) * 2.6
    edge = np.asarray(Image.fromarray((np.clip(edge, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) * (1 / 255)
    b = np.clip(lum * 1.7 - .08, 0, 1); b = b * np.sqrt(np.sqrt(b))                 # ^1.25
    alpha = np.clip(b * a * .46 + edge * .85, 0, .6) * holo_falloff()[y0:y1, x0:x1]
    a8 = (alpha * 255).astype(np.uint8)[..., None]
    l2 = lum * lum * np.sqrt(np.sqrt(lum))                                            # ^2.25
    base = (150 * l2 + 120 * edge)[..., None]; lum = lum[..., None]
    out = {}
    for side, tint in HOLO.items():
        rgb = np.clip(tint * (.75 + .9 * lum) + base, 0, 255).astype(np.uint8)
        out[side] = Image.fromarray(np.concatenate([rgb, a8], 2), 'RGBA')
    v = (int(x0), int(y0), out); _HO.update(k=av, v=v); return v


def holo_falloff():
    """half-res multiplier: 1 at head/shoulders -> 0 at the torso, 60 px side feather, 2 px scanlines."""
    def mk():
        yy = np.arange(H // 2, dtype=np.float32)[:, None] * 2
        vf = np.clip((1700 - yy) / (1700 - 980), 0, 1) ** 1.3
        xx = np.arange(W // 2, dtype=np.float32)[None, :] * 2
        sf = np.clip(np.minimum(xx, W - 1 - xx) / 60, 0, 1)
        m = (vf * sf).astype(np.float32); m[1::2] *= .85
        return m
    return C('holofall', mk)


def clone_offset(t, j):
    """horizontal offset (px) of clone ring j (1 = near, 2 = far) at time t."""
    D = {1: 320, 2: 590}[j]
    k = expo((t - (W_IMP + .04 * (j - 1))) / .30)
    d = D * k + (14 * j) * max(0.0, t - W_IMP - .3)
    if t > COLLAPSE:
        d *= 1 - clamp((t - COLLAPSE) / (W_IGN - COLLAPSE)) ** 1.8
    return d


def draw_clones(ctx, t, s):
    """all clone copies + their light trails are composited into ONE half-res premultiplied buffer (cropped to the
    clones' light), then upsampled once and added as a single layer — instead of ~16 full-frame composites."""
    if not (W_IMP - .01 <= t < W_IGN): return
    F = film_of(ctx)
    if F is None: return
    hx0, hy0, hp = holo_pair(F.av.frame(t))
    if hp is None: return
    # scale the half-res crops by s around the plate's bottom centre (same transform as add_founder)
    hw, hh = hp[1].size
    sw, sh = max(1, int(round(hw * s))), max(1, int(round(hh * s)))
    src = {side: (hp[side] if (sw, sh) == (hw, hh) else hp[side].resize((sw, sh), Image.BILINEAR)) for side in (-1, 1)}
    src_a = {side: src[side].getchannel('A') for side in (-1, 1)}
    # crop origin in half-res frame coords (plate scaled by s about (W/2, H) -> half: (W/4, H/2))
    cx0 = W / 4 + (hx0 - W / 4) * s
    cy0 = H / 2 + (hy0 - H / 2) * s
    copies = []
    for j in (2, 1):                           # far ring first
        for side in (-1, 1):
            d = clone_offset(t, j)
            if d < 2: continue
            vel = (d - clone_offset(t - 1 / 30, j)) * 30          # px / s
            al = (1.0 if j == 1 else .55) * clamp((t - W_IMP + .01) / .05)
            if t > COLLAPSE: al *= 1 - .5 * ein((t - COLLAPSE) / (W_IGN - COLLAPSE))
            nt = 3 if abs(vel) > 120 else 1                          # light trails behind the motion
            for g in range(nt, 0, -1):
                dd = d - max(abs(vel) / 30 * 1.3, 26) * g * (1 if vel >= 0 else -1)
                if (dd > 0) == (d > 0):
                    copies.append((side, side * dd, al * .32 * (1 - g / (nt + 1))))
            copies.append((side, side * d, al))
    if not copies: return
    # canvas bounds (half res) covering every copy
    xs = [cx0 + off / 2 for _, off, _ in copies]
    X0 = int(math.floor(max(0, min(xs)))); X1 = int(math.ceil(min(W / 2, max(xs) + sw)))
    Y0 = int(max(0, math.floor(cy0))); Y1 = int(min(H / 2, math.ceil(cy0) + sh))
    if X1 <= X0 or Y1 <= Y0: return
    canvas = Image.new('RGBA', (X1 - X0, Y1 - Y0), (0, 0, 0, 0))
    yi = int(round(cy0))
    for side, off, al in copies:                                   # PIL "over", far -> near, trails first
        xi = int(round(cx0 + off / 2))
        ax0, ay0 = max(X0, xi), max(Y0, yi); ax1, ay1 = min(X1, xi + sw), min(Y1, yi + sh)
        if ax1 <= ax0 or ay1 <= ay0: continue
        box = (ax0 - xi, ay0 - yi, ax1 - xi, ay1 - yi)
        S = src[side].crop(box)
        if al < .995: S.putalpha(src_a[side].crop(box).point(lambda v, al=al: int(v * al + .5)))
        canvas.alpha_composite(S, (ax0 - X0, ay0 - Y0))
    im = canvas.resize((canvas.width * 2, canvas.height * 2), Image.BILINEAR)
    ctx.add('behind', im, X0 * 2, Y0 * 2, center=False)


# ================================================================ front type
def to_img(): return E.word_img('TO', 96, 'white')[0]
def ignore_img(): return E.word_img('IGNORE', 204, 'white')[0]


def ignore_outline():
    def mk():
        fill, strk = _text_masks('IGNORE', 204, 800, track=0, stroke=3)
        m = Image.fromarray(np.clip(np.asarray(strk, np.int16) - np.asarray(fill, np.int16), 0, 255).astype(np.uint8))
        o = Image.new('RGBA', fill.size, (190, 170, 255, 0)); o.putalpha(m); return o
    return C('ignoutline', mk)


Y_TO, Y_IGN = 1238, 1388


def draw_front(ctx, t):
    if t >= W_TO - .02:
        lt = t - W_TO + .02
        s = .6 + .4 * back(lt / .2, 2.4)
        ctx.add('front', scale_im(to_img(), s), W / 2, Y_TO + 30 * (1 - eout(lt / .2)), alpha=clamp(lt / .05))
    if t >= W_IGN - .06:
        lt = t - (W_IGN - .06)
        k = ein(lt / .06)                       # lands exactly on W_IGN
        s = lerp(2.5, 1.0, k) if lt < .06 else 1 + .05 * (1 - eout((lt - .06) / .25))
        im = ignore_img()
        ctx.add('front', scale_im(im, s), W / 2, Y_IGN, alpha=clamp(.25 + lt / .05))
        # echo outlines expanding out of the word
        for e in range(3):
            ke = (t - W_IGN - e * .05) / .38
            if 0 <= ke < 1:
                ctx.add('front', scale_im(ignore_outline(), 1 + .55 * eout(ke)), W / 2, Y_IGN - 10, alpha=(1 - ke) ** 1.5 * .8)


# ================================================================ draw
def shake(t, t0, amp, dur=.42):
    k = (t - t0) / dur
    if not 0 <= k < 1: return 0., 0., 0.
    a = amp * (1 - k) ** 2
    return (a * math.sin(t * 97.0 + 1.3) + a * .5 * math.sin(t * 211.0),
            a * math.cos(t * 83.0) * .8 + a * .4 * math.sin(t * 173.0 + .7),
            a * .0009 * math.sin(t * 61.0))


def bloom_field():
    """additive violet light centred on IGNORE (float32 RGB, full res) — a light bloom, not a grey veil."""
    def mk():
        y, x = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        r = np.sqrt(((x - W / 2) / 560) ** 2 + ((y - Y_IGN) / 420) ** 2)
        core = np.exp(-r ** 2 * 2.2)[..., None] * np.array([150, 120, 255], np.float32)
        wide = np.exp(-r ** 2 * .45)[..., None] * np.array([60, 48, 150], np.float32)
        hot = np.exp(-(((x - W / 2) / 420) ** 2 + ((y - Y_IGN) / 90) ** 2) * 2)[..., None] * np.array([120, 110, 160], np.float32)
        im = Image.fromarray(np.clip(core + wide + hot, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        return np.asarray(im, np.float32)
    return C('bloom', mk)


def bg_plate(blur, z=1.0, anchor=(540, 760)):
    """the blurred studio built at HALF resolution (blur radius, zoom and the affine are 4x cheaper there and invisible
    on an out-of-focus plate), upsampled once. Same result as the engine's bg_z + bg_blur path."""
    half = C('studio_half', lambda: E.studio().reduce(2))
    im = half
    if abs(z - 1) > 1e-4:
        ax, ay = anchor[0] / 2, anchor[1] / 2; a = 1 / z
        im = im.transform(im.size, Image.AFFINE, (a, 0, ax - a * ax, 0, a, ay - a * ay), Image.BILINEAR)
    if blur > .3: im = im.filter(ImageFilter.GaussianBlur(blur / 2))
    return im.resize((W, H), Image.BILINEAR)


def bloom_u8():
    return C('bloom8', lambda: Image.fromarray(np.clip(bloom_field(), 0, 255).astype(np.uint8)))


def draw(ctx, lt, t):
    ctx.captions = False

    if t < T27:
        # ---------------- the breath: calm, symmetrical medium close-up (new framing vs s09), slow pull + rack focus
        k = smooth(lt / (T27 - START))
        z = 1.34 + .08 * (1 - expo(lt / .35)) - .06 * k            # 1.42 -> 1.34 settle, then a slow pull to 1.28
        ctx.cam = dict(z=z, x=540., y=740., dx=0., dy=0., rot=0.)
        ctx.bg_dim = .2 + .14 * k
        ctx.bg_img = bg_plate(2 + 5 * smooth(lt / .7), 1.08 - .04 * k)    # rack focus + slow background dolly
        ctx.post['vignette'] = .46
        ctx.post['bright'] = .97
        ctx.post['zoom_blur'] = .45 * clamp(1 - lt / .08)             # 2-3 frame settle masks the cut from s09
        calm_type(ctx, t)
        return

    if t < W_IMP - .05:
        # ---------------- jump cut: extreme close-up, "WE MAKE IT"
        k = (t - T27) / (W_IMP - T27)
        ctx.cam = dict(z=1.58 + .05 * k, x=540., y=640., dx=0., dy=0., rot=0.)
        ctx.bg_dim = .3; ctx.bg_img = C('bg4', lambda: bg_plate(4))
        ctx.post['vignette'] = .42
        pop_words(ctx, t, WE_MAKE_IT, T27, W_IMP + .01, y=1470)
        return

    # ---------------- IMPOSSIBLE: pull back, split, wall
    kp = expo((t - (W_IMP - .05)) / .32)                       # punch-out
    s_av = lerp(1.0, AV_S, kp)
    z = lerp(1.63, 1.0, kp)
    if t >= W_IGN:                                             # punch-in on IGNORE
        z = 1.0 + .05 * expo((t - W_IGN) / .35) + .015 * clamp((t - W_IGN) / .6)
    if t >= EXIT: z += .3 * ein((t - EXIT) / (END - EXIT))       # push-in whip into s11
    sx, sy, sr = shake(t, W_IGN, 34)
    sx2, sy2, sr2 = shake(t, W_IMP, 16, .3)
    ctx.cam = dict(z=z, x=540., y=lerp(640., 760., kp), dx=sx + sx2, dy=sy + sy2, rot=sr + sr2)
    ctx.bg_dim = .3 + .42 * kp
    ctx.bg_img = C('bg9', lambda: bg_plate(9)) if kp > .995 else bg_plate(4 + 5 * kp)
    draw_wall(ctx, t)
    draw_clones(ctx, t, s_av)
    add_founder(ctx, t, s_av)
    draw_front(ctx, t)
    if t < W_IMP + .01:                                        # "WE MAKE IT" rides the punch-out, fades into the slam
        pop_words(ctx, t, WE_MAKE_IT, T27, W_IMP + .01, y=1470)

    P = ctx.post
    P['vignette'] = .5
    # split: short chromatic + zoom blur on the pull-back
    P['rgb'] = 6 * clamp(1 - (t - W_IMP) / .16) if t >= W_IMP - .02 else 0
    P['zoom_blur'] = .5 * clamp(1 - abs(t - W_IMP) / .1)
    if t >= COLLAPSE:
        P['rgb'] = max(P['rgb'], 7 * ein((t - COLLAPSE) / (W_IGN - COLLAPSE)) if t < W_IGN else 9 * clamp(1 - (t - W_IGN) / .14))
    if t >= W_IGN:
        P['glitch'] = .4 * clamp(1 - (t - W_IGN) / .08)
        kb = 1.05 * (1 - eout((t - W_IGN) / .32)) if t < W_IGN + .32 else 0
        if kb > .01:
            def wrap(fr, kb=kb):
                b = bloom_u8().point(lambda v: int(v * kb + .5) if v * kb < 255 else 255)
                return ImageChops.add(fr.convert('RGB'), b)
            ctx.wrap = wrap
    if t >= EXIT:                                              # whip exit into s11
        P['zoom_blur'] = max(P['zoom_blur'], 1.0 * clamp((t - EXIT) / (END - EXIT)) ** 1.5)
