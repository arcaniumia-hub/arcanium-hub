"""s10 — CTA + END CARD (TL17-19 + hold, 22.04–29.44):
"Want your brand to break out of the feed?" / "Comment 'LUMARC'" / "and I'll show you how." / end card / loop flick.

22.04  JUMP CUT -> medium (z 1.19). Behind him a FROSTED GLASS WALL: the feed (4 columns of posts) seen through
       frosted glass lit by the studio's violet light, scrolling up fast with motion blur, settling (elastic).
22.69  "BRAND" — one post (northroast.coffee) lights up behind the frost: brand-gradient ring + glow bleeding through.
23.00  "TO" — the post knocks against the glass from inside (callback to his knocks): the glass flexes.
23.17  "BREAK" — a crack star bursts across the glass over the post (fissures, glints, refraction, its light leaks
       through the cracks), camera jolt.
23.46  "OUT" — it BREAKS OUT: the glass shatters toward the lens (3-D shards, DOF, motion blur, dust of light), the
       post flies out crisp and saturated, tumbling forward into the space in front of him (upper right), the hole in
       the wall shows the sharp feed behind the glass. "OF THE FEED?" it hangs there, then rushes into the lens
       (multi-sample shutter blur + growing defocus).
24.28  JUMP CUT hidden by the post passing the lens: it covers the frame (opaque, defocused), then wipes off past the
       camera (2-3 frames, motion-blurred edge) onto a tight framing in his real studio — he is out of the feed. "COMMENT" pops; an Instagram comment bar (glass)
       rises into the lower third; 24.99 L-U-M-A-R-C types itself letter by letter with the voice; 25.38 Post ->
       the comment lifts into a posted comment; 25.52 its heart pops red + burst + floating hearts, likes count up.
25.64  JUMP CUT -> wide (UI persists). "SHOW" -> a reply from lumarc_studio slides in under the comment
       ("Check your DMs."). "HOW." punch.
26.50  The UI lifts away, brand glass frosts over the world (violet duotone), the LUMARC logo slices converge and
26.84  slam on the end of the voice (boom): END CARD — logo, "Be seen. Be remembered.", gradient pill
       Comment “LUMARC”, @lumarc_studio · slumarc.com, planet-horizon light, bokeh, light sweeps.
29.10  LOOP HANDSHAKE: a thumb flick — the end card is flicked up into the feed (chrome slides back in), accelerating to
       ~12 000 px/s with vertical motion blur, so the last frame flows into frame 0 (the feed flying up onto his Reel).
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _glasskit as GK
from sections import _E_kit as K
from sections import feedkit as FK

START, END = E.span(17, 19)                        # 22.04 – 29.44
T18, T19 = E.TL[18]['t0'], E.TL[19]['t0']          # 24.28, 25.64 (jump cuts)
VEND = E.VOICE_END                                 # 26.84
W, H = E.W, E.H
clamp, lerp, smooth, expo, kick, eio = E.clamp, K.lerp, K.smooth, K.expo, K.kick, K.eio
eout, ein, back = E.eout, E.ein, E.back

# word onsets measured on src/tight16k.raw (10 ms RMS envelope + <600 Hz / 600-3k / >3.5 kHz bands, spectrogram):
# "want" w 22.15 | nt-closure 22.33-22.36, "your" 22.37 | b-burst 22.69 "brand" | d-t closure 22.97-22.99, aspirated
# t-burst 23.00 "to" | b-closure 23.14-23.16, release 23.17 "break" (r->ei glide 23.20-23.33) | k-closure 23.41-23.44,
# k-release into "out" 23.46 | t 23.59-23.60, "of" 23.61, "the" 23.67, f-frication 23.74-23.86 "feed", vowel 23.87 |
# "comment" k-burst 24.38 | "lumarc" voicing 24.97 (k-closure 25.32-25.35) | "and" 25.74, "I'll" 25.86,
# sh-noise 25.99 "show", y-glide 26.23 "you", breathy h 26.36 "how" (vowel 26.43, voice ends 26.65)
WORD_FIX = {(17, 'WANT'): 22.15, (17, 'YOUR'): 22.37, (17, 'BRAND'): 22.69, (17, 'TO'): 23.00, (17, 'BREAK'): 23.17,
            (17, 'OUT'): 23.46, (17, 'OF'): 23.61, (17, 'THE'): 23.67, (17, 'FEED?'): 23.74,
            (18, 'COMMENT'): 24.38, (18, '“LUMARC”'): 24.97,
            (19, 'AND'): 25.74, (19, "I'LL"): 25.86, (19, 'SHOW'): 25.99, (19, 'YOU'): 26.23, (19, 'HOW.'): 26.36}
W_WANT, W_YOUR, W_BRAND, W_TO, W_BREAK, W_OUT, W_OF, W_THE, W_FEED = 22.15, 22.37, 22.69, 23.00, 23.17, 23.46, 23.61, 23.67, 23.74
W_COMMENT, W_LUM = 24.38, 24.97
W_AND, W_ILL, W_SHOW, W_YOU, W_HOW = 25.74, 25.86, 25.99, 26.23, 26.36

SETTLE = 22.60                                     # the wall's scroll lands
RUSH0 = 24.10                                      # the post rushes into the lens
TYPE0, TYPE_DT = 24.99, .055                       # L-U-M-A-R-C (done 25.27, "lumarc" ends 25.35)
SEND = 25.38
HEART = 25.52
REPLY = W_SHOW
UI_OUT = 26.50                                     # the UI lifts away into the brand glass
HIT = VEND                                         # logo slam = end of the voice (score: end boom + shimmer)
ASM = .16
LIFT = 27.00
TAG1, TAG2 = 27.08, 27.30                          # "Be seen." / "Be remembered."
PILL, HANDLE = 27.52, 27.70
SWEEP1, SWEEP2 = 28.30, 28.55
FL0 = 29.10                                        # loop flick starts
LOOP_T = round(E.DUR * E.FPS) / E.FPS             # virtual time of the next loop's frame 0 (883 / 30 = 29.4333)

CUES = [
    (START, 'swoosh_up', {'gain': -9}),                       # cut: the frosted feed wall scrolls up
    (SETTLE, 'tick', {'gain': -8}),                           # lands
    (W_BRAND, 'pop', {'gain': -9, 'pan': .35}),               # the brand's post lights up behind the frost
    (W_BRAND + .01, 'shimmer', {'gain': -13, 'pan': .35}),
    (W_TO, 'knock', {'seed': 5, 'gain': -6, 'pan': .3}),      # it knocks on the glass from inside
    (W_BREAK, 'crack', {'dur': .45, 'seed': 13, 'gain': -2, 'pan': .3}),
    (W_OUT, 'shatter', {'dur': 1.3, 'seed': 6, 'gain': -2, 'pan': .2}),
    (W_OUT, 'impact', {'gain': -5}),
    (W_OUT + .02, 'whoosh', {'gain': -6, 'pan': .25}),
    (W_FEED, 'glass', {'seed': 2, 'gain': -12, 'pan': .3}),
    (T18, 'whoosh', {'gain': -3}),                            # the post rushes the lens (whoosh peaks as it passes, hiding the 24.28 cut)
    (T18 + .10, 'swoosh_up', {'gain': -11}),                  # comment bar rises (revealed as the card wipes off)
    (W_COMMENT, 'pop', {'gain': -10}),
] + [(TYPE0 + i * TYPE_DT, 'type', {'i': i, 'gain': 2}) for i in range(6)] + [
    (SEND, 'click', {'gain': 2}),
    (SEND + .02, 'swipe', {'gain': -13}),
    (HEART, 'heart', {'gain': 2}),
    (HEART, 'pop', {'gain': -6}),
    (T19, 'whoosh', {'gain': -15}),
    (REPLY, 'notify', {'gain': -4}),
    (W_HOW, 'tick', {'gain': -9}),
    (UI_OUT, 'glass', {'seed': 8, 'gain': -8}),
    (HIT - ASM - .02, 'riser', {'to': HIT, 'gain': 0}),
    (HIT, 'boom', {'gain': 0}),
    (HIT, 'impact', {'gain': -4}),
    (HIT + .03, 'shimmer', {'gain': -8}),
    (TAG1, 'swipe', {'gain': -12}),
    (TAG2, 'swipe', {'gain': -12}),
    (PILL, 'pop', {'gain': -3}),
    (HANDLE, 'tick', {'gain': -10}),
    (SWEEP1, 'shimmer', {'gain': -9}),
    (FL0, 'flick', {'gain': 2}),
]


# ======================================================================================= helpers
def C(k, fn): return K.C(('s10',) + (k if isinstance(k, tuple) else (k,)), fn)


def studio_graded(blur, dim):
    def mk():
        bg = E.studio().filter(ImageFilter.GaussianBlur(blur)) if blur > .3 else E.studio()
        return Image.blend(bg, Image.new('RGB', bg.size, (0, 0, 0)), dim)
    return C(('studio', blur, dim), mk)


def cover(img, w, h, fx=.5, fy=.5):
    sc = max(w / img.width, h / img.height); im = img.resize((int(img.width * sc + .999), int(img.height * sc + .999)), Image.LANCZOS)
    x, y = int((im.width - w) * fx), int((im.height - h) * fy); return im.crop((x, y, x + w, y + h))


# ======================================================================================= the frosted feed wall
FOC = 1600.0
VP = (540.0, 860.0)
Z_HIM = 1330.0
CW, HEAD, MED, FOOT = 300, 46, 375, 54
CH = HEAD + MED + FOOT                             # 475
PX_, PY_ = 316, CH + 14
COLS = [800 - 2 * PX_, 800 - PX_, 800, 800 + PX_]
BX, BY = COLS[2], 430.0                            # the brand post's centre at rest (world)
RB = 3                                             # its row index in the grid image
NROWS = 10
SCROLL0 = 1180.0                                   # content starts this much lower and flies up into place
GY0 = BY - RB * PY_ - CH / 2                       # world y of the grid image top at rest (offset 0)
TILES = [('loc2', 'brightside.cafe'), ('bad_flyer', 'tonys.pizza.nyc'), ('loc4', 'jess.travels'), ('close_food', 'smash.burger.co'),
         ('loc5', 'city.realty'), ('design_post', 'maisoncrumb'), ('bad_blurry_photo', 'burgerhouse_'), ('loc3', 'sunset.rooftop'),
         ('close_skill', 'the.craft.bench'), ('loc7', 'beach.days'), ('bad_shaky_video', 'salon.glow.studio'), ('website', 'oliva.restaurant'),
         ('loc6', 'urban.gym.co'), ('carousel_2', 'petal.florist'), ('close_service', 'corner.latte'), ('loc1', 'fresh.bowl')]
BRAND_USER = 'northroast.coffee'


def card_art(img_name, user, likes='', scale=2, brand=False):
    """an Instagram feed post card (dark mode) at `scale` x the wall size (RGBA, rounded)."""
    def mk():
        s = scale; w, hh, mh, fh = CW * s, HEAD * s, MED * s, FOOT * s
        im = Image.new('RGBA', (w, hh + mh + fh), (12, 12, 16, 255)); d = ImageDraw.Draw(im)
        a = E.asset(img_name)
        av = cover(a, 30 * s, 30 * s).convert('RGBA'); av.putalpha(K.circle_mask(30 * s)); im.alpha_composite(av, (10 * s, 8 * s))
        f = E.font(int(13 * s), 700); d.text((48 * s, 9 * s), user, font=f, fill=(242, 242, 246))
        if brand:
            d.text((48 * s, 25 * s), 'Sponsored', font=E.font(int(10.5 * s), 400), fill=(170, 170, 180))
            x = 48 * s + int(f.getlength(user)) + 5 * s
            im.alpha_composite(FK.icon('verified', int(14 * s), (61, 133, 250)), (x, int(10 * s)))
        im.alpha_composite(FK.icon('dots', int(18 * s)), (w - 28 * s, 14 * s))
        im.paste(cover(a, w, mh, .5, .4), (0, hh))
        y = hh + mh + 9 * s
        for k, nm in enumerate(('heart', 'comment', 'share')):
            im.alpha_composite(FK.icon(nm, int(22 * s)), (int((10 + k * 32) * s), y))
        im.alpha_composite(FK.icon('save', int(22 * s)), (w - 32 * s, y))
        if likes: d.text((10 * s, y + 25 * s), likes, font=E.font(int(11 * s), 700), fill=(240, 240, 244))
        return E.rounded(im, 12 * s)
    return C(('card', img_name, user, likes, scale, brand), mk)


def brand_card(scale=2): return card_art('carousel_1', BRAND_USER, '3,880 likes', scale, True)


def grid(sharp=True, with_brand=True):
    """tall RGBA grid of post cards (wall size), rows 0..NROWS-1, image top = world GY0 at rest."""
    def mk():
        gh = NROWS * PY_ + 40
        im = Image.new('RGBA', (W, gh), (0, 0, 0, 0)); n = 0
        for r in range(NROWS):
            for c in range(4):
                x = int(COLS[c] - CW / 2); y = int(r * PY_)
                if (r, c) == (RB, 2):
                    if with_brand: im.alpha_composite(brand_card(1), (x, y))
                    continue
                nm, user = TILES[(n * 7 + 3) % len(TILES)]; n += 1
                im.alpha_composite(card_art(nm, user, '', 1), (x, y))
        if sharp: return im
        # frosted: premultiplied blur + grade (desaturate, darken, cool)
        a = np.asarray(im, np.float32); al = a[..., 3:4] / 255
        pm = Image.fromarray(np.dstack([a[..., :3] * al, al[..., 0] * 255]).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(13))
        b = np.asarray(pm, np.float32); al = b[..., 3:4] / 255
        rgb = np.where(al > 1e-3, b[..., :3] / np.maximum(al, 1e-3), 0)
        g = rgb.mean(2, keepdims=True); rgb = g + (rgb - g) * .42
        rgb = rgb * .40 + np.array([9, 9, 24], np.float32) * .6
        return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), b[..., 3]]).astype(np.uint8), 'RGBA')
    return C(('grid', sharp, with_brand), mk)


def scroll_off(t):
    """content offset (px, + = lower than rest): flies up and lands with an elastic settle at SETTLE."""
    if t >= SETTLE + .5: return 0.0
    x = (t - START) / (SETTLE - START)
    if x < 1:
        return SCROLL0 * (1 - x) ** 2.4 - 26 * math.sin(math.pi * x) ** 4 * (x > .6)
    e = t - SETTLE
    return -14 * math.exp(-e / .09) * math.sin(e * 2 * math.pi * 3.2)


def scroll_vel(t, dt=1 / 60): return (scroll_off(t) - scroll_off(t - dt)) / dt


def frost_bg():
    return C('frost_bg', lambda: studio_graded(14, .55).convert('RGBA'))


def glass_overlay():
    """the glass surface itself: top edge highlight, cool sheen, two soft diagonal reflections, frost grain."""
    def mk():
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None]; x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        a = (1 - y) ** 3 * .10 + np.exp(-((x * .7 + y * .35 - .42) / .05) ** 2) * .07 + np.exp(-((x * .7 + y * .35 - .58) / .02) ** 2) * .05
        rng = np.random.default_rng(3); a = a + rng.normal(0, .012, (H, W)).astype(np.float32)
        top = 34
        a[top:top + 2] += .55; a[top + 2:top + 5] += .12
        a[:top] = 0
        im = Image.new('RGBA', (W, H), (226, 228, 255, 0)); im.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)))
        return im
    return C('glass_ov', mk)


def brand_glow_art():
    """what the lit brand post looks like through the frost: blurred gradient ring + bright card (RGBA, padded 120)."""
    def mk():
        p = 120; w, h = CW + 2 * p, CH + 2 * p
        ring = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(ring).rounded_rectangle((p * 2 - 14, p * 2 - 14, (p + CW) * 2 + 14, (p + CH) * 2 + 14), 40, outline=255, width=16)
        ring = ring.resize((w, h), Image.LANCZOS)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(ring.filter(ImageFilter.GaussianBlur(9)))
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        halo = Image.new('RGBA', (w, h), (120, 90, 255, 0)); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((p - 30, p - 30, p + CW + 30, p + CH + 30), 60, fill=150)
        halo.putalpha(m.filter(ImageFilter.GaussianBlur(40))); out.alpha_composite(halo)
        card = Image.new('RGBA', (w, h), (0, 0, 0, 0)); card.alpha_composite(brand_card(1), (p, p))
        card = card.filter(ImageFilter.GaussianBlur(9)); out.alpha_composite(E.fade(card, .85))
        out.alpha_composite(g)
        return out
    return C('brand_glow', mk)


# ---- crack + shatter of the glass over the brand post
FR = GK.Fracture(center=(BX - 22, BY + 40), size=(W, H), seed=27, radials=14,
                 rings=[14, 34, 62, 100, 150, 215, 295, 390, 500, 640, 820, 1050, 1350],
                 hits=[(W_TO, 8, 22, .5, .02), (W_BREAK, 110, 330, .85, .07)], web=(W_BREAK + .05, .12), early_rings=(1, 6))
R_HOLE = 285.0                                     # glass pieces whose centroid lies within this radius fly out
def _group(i, j, k):
    if j <= 1: return ('a', k // 3)
    if j <= 3: return ('b', j, k // 2)
    return ('c', i)
SH = GK.Shatter(FR, seed=4, focal=FOC, vp=VP, group=_group, wave=9000., speed=1.15)
SH_IDS = {s['i'] for s in SH.shards if s['dist'] <= R_HOLE}


def hole_mask():
    """AA mask of the hole (union of the flown pieces) + its lit rim."""
    def mk():
        S = 2; m = Image.new('L', (W * S, H * S)); d = ImageDraw.Draw(m)
        for s in SH.shards:
            if s['i'] in SH_IDS:
                for poly in s['polys']: d.polygon([(x * S, y * S) for x, y in poly], fill=255)
        m = m.resize((W, H), Image.LANCZOS)
        from scipy.ndimage import maximum_filter
        ma = np.asarray(m, np.float32) / 255
        rim = np.clip(maximum_filter(ma, size=5) - ma, 0, 1)
        return ma, rim
    return C('hole', mk)


def wall_light():
    """the studio's violet monitor light diffusing through the frost from behind him (additive field, world px) and a
    stop of fall-off toward the top corners, so the wall sits in the same light as his rim."""
    def mk():
        y, x = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        g = np.exp(-(((x - 540) / 600) ** 2 + ((y - 1010) / 470) ** 2))[..., None] * np.array([38, 25, 96], np.float32)
        g += np.exp(-(((x - 540) / 900) ** 2 + ((y - 1650) / 330) ** 2))[..., None] * np.array([26, 16, 68], np.float32)
        g += np.exp(-(((x - 860) / 260) ** 2 + ((y - 300) / 240) ** 2))[..., None] * np.array([16, 12, 40], np.float32)
        g -= (np.clip(((x - 540) / 540) ** 2 * .5 + ((y - 900) / 1100) ** 2, 0, 1) * 16)[..., None]
        return np.asarray(Image.fromarray(np.clip(g + 64, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) - 64
    return C('wall_light', mk)


def wall_rgb(t):
    """the wall (frosted feed + glass) as RGB, world coords, before cracks/hole."""
    out = frost_bg().copy()
    off = scroll_off(t); v = scroll_vel(t)
    g = grid(False)
    y = int(round(GY0 + off - 20))
    if abs(v) > 300:
        y0 = max(0, -y); y1 = min(g.height, H - y)
        if y1 > y0:
            crop = K.vblur(g.crop((0, y0, W, y1)), min(160, abs(v) / 60))
            out.alpha_composite(crop, (0, y + y0))
    else:
        E._paste(out, dict(img=g, xy=(0, y), glass=0))
    out = K.add_light(out, wall_light(), 1.0)
    # the brand post lights up behind the frost
    if t >= W_BRAND - .02:
        k = expo((t - W_BRAND + .02) / .25) * (.85 + .15 * math.sin((t - W_BRAND) * 9)) + .4 * kick(t - W_BRAND, .15)
        k += .35 * kick(t - W_TO, .12) * (t >= W_TO)
        bg = brand_glow_art()
        E._paste(out, dict(img=E.fade(bg, min(1.0, k)), xy=(int(BX - bg.width / 2), int(BY + off - bg.height / 2)), glass=0))
    out.alpha_composite(glass_overlay())
    return out.convert('RGB')


def flex(img, t):
    """the knock on "TO": the glass bulges for a few frames (radial displacement around the post)."""
    k = kick(t - W_TO, .07) * (t >= W_TO) * math.sin(min(math.pi, (t - W_TO) * 40))
    if abs(k) < .02: return img
    def grids():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx, dy = xx - BX, yy - BY; r = np.hypot(dx, dy) + 1
        f = np.exp(-(r / 220) ** 2)
        return dx / r * f, dy / r * f, yy, xx
    ux, uy, yy, xx = C('flexg', grids)
    a = np.asarray(img, np.float32)
    sx = np.clip(xx - ux * 9 * k, 0, W - 1).astype(np.int32); sy = np.clip(yy - uy * 9 * k, 0, H - 1).astype(np.int32)
    return Image.fromarray(a[sy, sx].astype(np.uint8))


def behind_hole():
    """what the hole shows: the feed behind the glass, sharp, the brand's slot empty (RGB world)."""
    def mk():
        out = studio_graded(3, .62).convert('RGBA')
        g = grid(True, with_brand=False)
        a = np.asarray(g, np.float32); a[..., :3] *= .55; g = Image.fromarray(a.astype(np.uint8), 'RGBA')
        E._paste(out, dict(img=g, xy=(0, int(round(GY0 - 20))), glass=0))
        # the empty slot: dark, with a faint violet afterglow
        sl = Image.new('RGBA', (CW, CH), (6, 5, 12, 255)); sl = E.rounded(sl, 12)
        out.alpha_composite(sl, (int(BX - CW / 2), int(BY - CH / 2)))
        rg = K.radial(520, 640, (120, 90, 255), 2.0, .55); out.alpha_composite(rg, (int(BX - 260), int(BY - 320)))
        return out.convert('RGB')
    return C('behind_hole', mk)


def leak(t):
    if t < W_BREAK: return 0.0
    return .26 * expo((t - W_BREAK) / .12) + .16 * clamp((t - W_BREAK) / (W_OUT - W_BREAK))


def wall_cracked(t):
    """wall + cracks at time t (t < W_OUT) -> RGB."""
    img = flex(wall_rgb(t), t)
    if t < W_TO: return img
    return FR.composite(img, t, refr=1.0, leak=leak(t), glint=1.0, sweep=lerp(-300, 1600, clamp((t - W_BREAK) / .5)),
                        powder=.55, sparks=1.0, leak_falloff=(.25, 200.0))


def glass_tex():
    """what the flying glass carries: the cracked wall at the moment of the break (RGB)."""
    return C('gtex', lambda: wall_cracked(W_OUT - .001))


def wall_final():
    """the wall after the break (static): cracks frozen, the hole open onto the sharp feed, a lit rim."""
    def mk():
        base = np.asarray(FR.composite(wall_rgb(W_OUT + 2.0), W_OUT + .5, refr=1.0, leak=.18, glint=.6, powder=0.0, sparks=0.0,
                                       leak_falloff=(.3, 260.0)), np.float32)
        ma, rim = hole_mask()
        bh = np.asarray(behind_hole(), np.float32)
        out = base * (1 - ma[..., None]) + bh * ma[..., None]
        out = out + rim[..., None] * np.array([220, 215, 255], np.float32) * .8
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    return C('wall_final', mk)


def wall_image(t):
    if t < W_OUT: return wall_cracked(t)
    wf = wall_final()
    k = math.exp(-(t - W_OUT) / .10)            # flash of light through the hole at the break
    if k > .03:
        a = np.asarray(wf, np.float32); ma, rim = hole_mask()
        f = C('hole_flash', lambda: np.asarray(Image.fromarray((ma * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)), np.float32) / 255)
        a = a + f[..., None] * np.array([170, 140, 255], np.float32) * 1.4 * k
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return wf


def shard_layers(t):
    tau = (t - W_OUT) * 1.1
    if tau <= 0 or tau > 2.2: return None, None
    out = []
    zs = {s['i']: SH.pose(s, tau)[0][2] for s in SH.shards if s['i'] in SH_IDS}
    for front in (False, True):
        ids = {i for i, z in zs.items() if (z < Z_HIM) == front}
        if not ids: out.append(None); continue
        canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        img = SH.render(canvas, glass_tex(), tau, dz=0.0, focus_z=FOC * .9, dof=7.0, shutter_dtau=1.1 / 60, near=120,
                        cull_scale=6.0, keep=lambda s: s['i'] in ids, spec_gain=1.3,
                        img_alpha=lambda s, u: clamp(1 - u / .5) * .8 + .1, alpha_fn=lambda s, u: clamp(1.25 - u / 1.4))
        out.append(img)
    return out[0], out[1]


# ---- the post that breaks out
def hero_state(t):
    """(cx, cy, scale, rx, ry, rz, alpha) of the broken-out post in SCREEN space (scale 1 = the wall card at z 1)."""
    if t < W_OUT: return None
    e = t - W_OUT
    za = camera(min(t, T18 - 1e-3))['z']
    sx0, sy0 = 540 + (BX - 540) * za, 860 + (BY - 860) * za
    k1 = expo(e / .24)
    cx = lerp(sx0, 842, k1); cy = lerp(sy0, 470, k1); s = lerp(za, 1.40, k1)
    rx = lerp(0, 10, k1); ry = lerp(0, -26, k1); rz = lerp(0, -6, k1)
    if e > .12:   # it keeps coming at you, slowly, with a breath of float
        d = smooth((e - .12) / (RUSH0 - W_OUT - .12))
        cy += -12 * d + 4 * math.sin((e - .12) * 5); cx += -6 * d; s += .14 * d
        rx -= 4 * d; ry += 8 * d; rz += 3 * d
    al = 1.0
    if t >= RUSH0:
        u = min(1.0, (t - RUSH0) / (T18 - RUSH0))
        k = u ** 2.4
        cx = lerp(cx, 590, k); cy = lerp(cy, 900, k); s = s * (1 + 5.2 * k)
        rx *= (1 - k); ry *= (1 - .7 * k); rz *= (1 - k)
        if t > T18:   # it passes the lens: the (opaque, defocused) card slides off past the camera, wiping onto the close-up
            e2 = (t - T18) / EXIT_D; f = e2 ** 1.15
            cx += 2900 * f; cy += 520 * f; s *= 1 + .35 * e2; ry *= 1 - e2; rx *= 1 - e2
    return cx, cy, s, rx, ry, rz, al


EXIT_D = .10                                       # the card clears the frame 2-3 frames after the 24.28 cut


def hero_quad(st, qq=1):
    cx, cy, s, rx, ry, rz = st[:6]
    q = K.card_quad(600, 950, cx, cy, s * .5, rx, ry, rz, 2400.)
    return [(x / qq, y / qq) for x, y in q]


def hero_art(qq):
    return C(('hart', qq), lambda: K.scale_im(brand_card(2), 1 / qq, lanczos=True))


def hero_defocus(s):
    """defocus (full-res px) of the post as it comes toward the lens (the camera is focused on him)."""
    return 0.0 if s < 1.7 else 3.5 * (s - 1.7) ** 1.25


def warp_clip(src, quad, clip, pad=3):
    """K.warp, but only the part of the quad's bbox inside `clip` (x0, y0, x1, y1) is rendered (the post near the lens
    is several screens wide: warping its whole bbox wasted ~90% of the time)."""
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    x0, y0 = max(int(math.floor(min(xs))) - 2, clip[0]), max(int(math.floor(min(ys))) - 2, clip[1])
    x1, y1 = min(int(math.ceil(max(xs))) + 2, clip[2]), min(int(math.ceil(max(ys))) + 2, clip[3])
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    ew = max(math.hypot(quad[1][0] - quad[0][0], quad[1][1] - quad[0][1]), math.hypot(quad[2][0] - quad[3][0], quad[2][1] - quad[3][1]))
    sc = min(1.0, 1.5 * ew / src.width)
    if sc < .9: src = src.resize((max(4, int(src.width * sc)), max(4, int(src.height * sc))), Image.BILINEAR, reducing_gap=2.0)
    s2 = Image.new('RGBA', (src.width + 2 * pad, src.height + 2 * pad), (0, 0, 0, 0)); s2.paste(src, (pad, pad))
    sq = [(pad, pad), (s2.width - pad, pad), (s2.width - pad, s2.height - pad), (pad, s2.height - pad)]
    co = K.homography(sq, [(x - x0, y - y0) for x, y in quad])
    return s2.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BILINEAR), x0, y0


def hero_layer(t):
    """the broken-out post: perspective card with a real shutter (the card is re-projected at several sub-frame times
    over a 180-degree shutter and accumulated, so translation + scale + tumble blur correctly), defocus as it rushes the
    lens -> (img, x, y) screen, cropped to the frame."""
    st = hero_state(t)
    if st is None: return None
    s = st[2]
    qq = 1 if s < 2.2 else (2 if s < 5 else 4)
    q1 = hero_quad(st, qq)
    xs = [p[0] for p in q1]; ys = [p[1] for p in q1]
    sw, sh = W / qq, H / qq
    if max(xs) < -60 or min(xs) > sw + 60 or max(ys) < -60 or min(ys) > sh + 60: return None
    p0 = hero_state(t - 1 / 60)
    L = 0.0 if p0 is None else max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(q1, hero_quad(p0, qq)))
    blur = hero_defocus(s) / qq
    n = int(min(24, max(1, math.ceil(L / (1.6 + 1.2 * blur)))))     # steps finer than ~2 px / the defocus are invisible
    art = hero_art(qq)
    m = int(blur * 2.5) + 3
    clip = (-m, -m, int(math.ceil(sw)) + m, int(math.ceil(sh)) + m)
    samples = []
    for i in range(n):
        tau = t - (1 / 60) * (1 - i / (n - 1)) if n > 1 else t
        sti = hero_state(tau) if tau >= W_OUT else None
        if sti is None: continue
        r = warp_clip(art, hero_quad(sti, qq), clip)
        if r is not None: samples.append(r)
    if not samples: return None
    bx0 = max(min(x0 for _, x0, _ in samples), -m); by0 = max(min(y0 for _, _, y0 in samples), -m)
    bx1 = min(max(x0 + im.width for im, x0, _ in samples), int(sw) + m); by1 = min(max(y0 + im.height for im, _, y0 in samples), int(sh) + m)
    if bx1 - bx0 < 2 or by1 - by0 < 2: return None
    acc = np.zeros((by1 - by0, bx1 - bx0, 4), np.float32)
    for im, x0, y0 in samples:
        a = np.asarray(im, np.float32)
        ix0, iy0 = max(0, bx0 - x0), max(0, by0 - y0); ix1, iy1 = min(im.width, bx1 - x0), min(im.height, by1 - y0)
        if ix1 <= ix0 or iy1 <= iy0: continue
        a = a[iy0:iy1, ix0:ix1]; al_ = a[..., 3:4] / 255
        acc[y0 + iy0 - by0:y0 + iy1 - by0, x0 + ix0 - bx0:x0 + ix1 - bx0] += np.concatenate([a[..., :3] * al_, al_ * 255], 2)
    acc /= len(samples)
    e = t - W_OUT
    if e < .5:     # freshly broken out: a light kiss over the card
        kz = .55 * math.exp(-e / .07)
        acc[..., :3] += (acc[..., 3:4] - acc[..., :3]) * kz
    if blur > .6:
        from scipy.ndimage import gaussian_filter
        acc = gaussian_filter(acc, (blur * .8, blur * .8, 0), mode='constant', truncate=2.5)
    # crop to the frame, un-premultiply, back to full res
    cx0, cy0 = max(0, -bx0), max(0, -by0); cx1, cy1 = min(acc.shape[1], int(math.ceil(sw)) - bx0), min(acc.shape[0], int(math.ceil(sh)) - by0)
    if cx1 <= cx0 or cy1 <= cy0: return None
    acc = acc[cy0:cy1, cx0:cx1]; al_ = acc[..., 3:4]
    rgb = np.where(al_ > .5, acc[..., :3] * 255 / np.maximum(al_, 1e-3), 0)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al_, 0, 255)]).astype(np.uint8), 'RGBA')
    X0, Y0 = (bx0 + cx0) * qq, (by0 + cy0) * qq
    if qq > 1: im = im.resize((im.width * qq, im.height * qq), Image.BILINEAR)
    return im, X0, Y0


def hero_glow(t):
    st = hero_state(t)
    if st is None or t >= RUSH0 + .05: return None
    cx, cy, s, rx, ry, rz, al = st
    k = (.55 + .45 * math.exp(-(t - W_OUT) / .2)) * clamp((RUSH0 + .05 - t) / .1)
    g = C('hglow', lambda: K.radial(760, 1000, (120, 90, 255), 2.2, .45))
    return E.fade(K.scale_im(g, s * .8), min(1.0, k)), cx, cy


# ======================================================================================= comment UI (screen space)
UIW = 900
COMP_H, COMP_Y = 150, 1392
CARD_H, CARD_Y = 214, 1186
REPLY_W, REPLY_H, REPLY_Y = 830, 156, 1404


def story_avatar(d, kind='you'):
    def mk():
        im = Image.new('RGBA', (d, d), (0, 0, 0, 0))
        ring = E.gradient(d, d, [(255, 170, 60), (255, 60, 120), (170, 60, 255)]).convert('RGBA').rotate(-45, Image.BILINEAR)
        ring.putalpha(K.circle_mask(d)); im.alpha_composite(ring)
        g = int(d * .06); dd = d - 2 * g
        gap = Image.new('RGBA', (dd, dd), (16, 16, 22, 255)); gap.putalpha(K.circle_mask(dd)); im.alpha_composite(gap, (g, g))
        g2 = int(d * .11); d2 = d - 2 * g2
        inner = Image.new('RGBA', (d2, d2), (58, 60, 78, 255)); di = ImageDraw.Draw(inner)
        di.ellipse((d2 * .32, d2 * .16, d2 * .68, d2 * .52), fill=(170, 172, 190, 255))
        di.ellipse((d2 * .14, d2 * .58, d2 * .86, d2 * 1.25), fill=(170, 172, 190, 255))
        inner.putalpha(K.circle_mask(d2)); im.alpha_composite(inner, (g2, g2))
        return im
    return C(('sav', d, kind), mk)


def lumarc_avatar(d):
    def mk():
        im = Image.new('RGBA', (d, d), (0, 0, 0, 0))
        ring = E.gradient(d, d, E.GRAD).convert('RGBA'); ring.putalpha(K.circle_mask(d)); im.alpha_composite(ring)
        g = int(d * .07); dd = d - 2 * g
        inner = Image.new('RGBA', (dd, dd), (12, 12, 18, 255))
        lg = E.logo(int(dd * 2.2)); ic = lg.crop((0, 0, int(lg.height * 1.05), lg.height))       # the rings mark only
        ic = ic.resize((int(dd * .78), int(dd * .78 * ic.height / ic.width)), Image.LANCZOS)
        inner.alpha_composite(ic, ((dd - ic.width) // 2, (dd - ic.height) // 2))
        inner.putalpha(K.circle_mask(dd)); im.alpha_composite(inner, (g, g))
        return im
    return C(('lav', d), mk)


def composer_base():
    def mk():
        card = E.glass_panel(UIW, COMP_H, radius=COMP_H // 2, tint=(14, 14, 22), alpha=.70, border=.30)
        card.alpha_composite(story_avatar(96), (27, 27))
        return card
    return C('comp', mk)


def lumarc_typed():
    def mk():
        f = E.font(58, 800); l, t, r, b = f.getbbox('LUMARC'); w, h = r - l + 8, b - t + 8
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((4 - l, 4 - t), 'LUMARC', font=f, fill=255)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
        xs = [4 + f.getlength('LUMARC'[:i]) for i in range(7)]
        return g, xs
    return C('lumtxt', mk)


def composer(t):
    card = composer_base().copy()
    n = int(clamp((t - TYPE0) / TYPE_DT + 1, 0, 6)) if t >= TYPE0 else 0
    tx, ty = 152, 42
    if n == 0:
        ph = K.txt('Add a comment for lumarc_studio…', 34, 400, (150, 150, 166))
        card.alpha_composite(ph, (tx, (COMP_H - ph.height) // 2))
    else:
        g, xs = lumarc_typed()
        card.alpha_composite(g.crop((0, 0, int(xs[n]) + (6 if n == 6 else 0), g.height)), (tx, ty))
        lt = t - (TYPE0 + (n - 1) * TYPE_DT)
        if lt < .08:   # newest letter pops from its baseline
            li = g.crop((int(xs[n - 1]), 0, int(xs[n]), g.height)); s = 1.3 - .3 * eout(lt / .08)
            li2 = K.scale_im(li, s)
            card.alpha_composite(li2, (int(tx + xs[n - 1] + li.width / 2 - li2.width / 2), int(ty + li.height - li2.height)))
    # caret
    typing = TYPE0 - .1 <= t <= TYPE0 + 6 * TYPE_DT + .1
    if t < SEND and (typing or int((t - T18) / .27) % 2 == 0):
        g, xs = lumarc_typed()
        cx = tx + (xs[n] if n else 0) + 4
        cr = C('caret', lambda: E.gradient(5, 66, E.GRAD_LIGHT).convert('RGBA'))
        card.alpha_composite(cr, (int(cx), 42))
    # Post button: dim -> bright once there is text; pressed on SEND
    on = n > 0 or t >= SEND
    col = (0, 149, 246) if on else (40, 70, 110)
    pb = K.txt('Post', 38, 700, col)
    ps = 1.0
    if SEND - .03 <= t < SEND + .15: ps = 1 - .14 * K.bump(t, SEND - .03, SEND + .15)
    pb2 = K.scale_im(pb, ps)
    card.alpha_composite(pb2, (int(UIW - 70 - pb2.width / 2), int(COMP_H / 2 - pb2.height / 2)))
    return card


def comment_card_base():
    def mk():
        card = E.glass_panel(UIW, CARD_H, radius=46, tint=(14, 14, 22), alpha=.72, border=.30)
        card.alpha_composite(story_avatar(96), (30, 30))
        y = K.txt('you', 36, 700, (245, 245, 250)); card.alpha_composite(y, (152, 30))
        card.alpha_composite(K.txt('now', 34, 400, (150, 150, 165)), (152 + y.width + 16, 32))
        g, xs = lumarc_typed(); card.alpha_composite(g, (148, 80))
        card.alpha_composite(K.txt('Reply', 34, 600, (150, 150, 165)), (152, 158))
        return card
    return C('ccard', mk)


def comment_card(t):
    card = comment_card_base().copy()
    hx, hy = UIW - 80, 92
    if t < HEART:
        card.alpha_composite(K.heart_shape(52, None, (235, 235, 242, 255), 3), (hx - 26, hy - 26))
    else:
        lt = t - HEART
        s = .4 + .6 * back(lt / .24, 3.2)
        hh = K.scale_im(K.heart_shape(52, (255, 48, 64, 255)), s)
        card.alpha_composite(hh, (int(hx - hh.width / 2), int(hy - hh.height / 2)))
        kb = lt / .35
        if kb < 1:
            d = ImageDraw.Draw(card, 'RGBA')
            for j in range(10):
                a = j / 10 * 2 * math.pi + .3
                r0, r1 = 30 + 34 * eout(kb), 30 + 52 * eout(kb)
                col = (255, 90, 110) if j % 2 else (190, 150, 255)
                d.line((hx + math.cos(a) * r0, hy + math.sin(a) * r0, hx + math.cos(a) * r1, hy + math.sin(a) * r1),
                       fill=col + (int(255 * (1 - kb)),), width=4)
            R = 26 + 42 * eout(kb)
            d.ellipse((hx - R, hy - R, hx + R, hy + R), outline=(255, 70, 90, int(200 * (1 - kb))), width=3)
        # likes count up fast (the comment takes off)
        n = int(1 + 46 * smooth((t - HEART - .05) / 1.0) ** 1.4)
        lk = K.txt(f'{n} like' + ('s' if n > 1 else ''), 34, 600, (150, 150, 165))
        rw = K.txt('Reply', 34, 600, (0, 0, 0)).width
        card.alpha_composite(E.fade(lk, clamp(lt / .12)), (152 + rw + 30, 158))
    return card


def mini_hearts(t, cx, cy):
    """little red hearts floating up from the comment's heart after the like."""
    out = []
    for j in range(7):
        t0 = HEART + .05 + j * .07
        u = (t - t0) / .9
        if not 0 <= u < 1: continue
        x = cx + math.sin(u * 5 + j * 1.7) * (14 + 10 * K.hrand(j, 2)) + (K.hrand(j, 3) - .5) * 40
        y = cy - 40 - u * (180 + 80 * K.hrand(j, 4))
        s = (.55 + .45 * K.hrand(j, 5)) * (1 - .3 * u)
        a = clamp(u / .1) * (1 - u) ** 1.2
        out.append((K.scale_im(K.heart_shape(40, (255, 48 + int(40 * K.hrand(j, 6)), 80, 255)), s), x, y, a))
    return out


def reply_card():
    def mk():
        card = E.glass_panel(REPLY_W, REPLY_H, radius=40, tint=(18, 14, 34), alpha=.74, border=.34)
        card.alpha_composite(lumarc_avatar(84), (26, 36))
        u = K.txt('lumarc_studio', 34, 700, (245, 245, 250)); card.alpha_composite(u, (130, 30))
        card.alpha_composite(FK.icon('verified', 30, (61, 133, 250)), (130 + u.width + 8, 33))
        card.alpha_composite(K.txt('now', 34, 400, (150, 150, 165)), (130 + u.width + 50, 30))
        card.alpha_composite(K.txt('Check your DMs. Let’s build yours.', 35, 500, (236, 234, 248)), (130, 84))
        return card
    return C('reply', mk)


def draw_ui(ctx, t):
    if t < T18 or t >= UI_OUT + .25: return
    out_k = expo((t - UI_OUT) / .2) if t >= UI_OUT else 0.0      # lift away into the brand glass
    oy = -140 * out_k; oa = 1 - out_k
    # "COMMENT" big word
    if W_COMMENT - .02 <= t < SEND:    # lifts away just before the posted comment takes its place (never stacked)
        lt = t - W_COMMENT + .02
        s = (.72 + .28 * back(lt / .18)) * (1.05 if .05 < lt < .3 else 1)
        ex = expo((t - (SEND - .12)) / .12) if t >= SEND - .12 else 0
        im = E.word_img('COMMENT', 124, 'white')[0]
        ctx.add('screen', K.scale_im(im, s * (1 - .12 * ex)), W / 2, 1160 - 60 * ex, alpha=clamp(lt / .05) * (1 - ex))
    # composer bar: rises with the cut, typed, sent (drops away)
    if t < SEND + .13:
        k_in = expo((t - T18) / .42)
        y = COMP_Y + 210 * (1 - k_in)
        a = clamp(k_in * 1.6)
        cm = composer(t)
        if t >= SEND:      # sent: the bar hands its text to the posted comment and dissolves in place
            d = expo((t - SEND) / .12); a *= 1 - d; cm = K.scale_im(cm, 1 - .03 * d)
        ctx.add('screen', cm, W / 2, y, glass=16, alpha=a)
    # posted comment: lifts out of the composer into place
    if t >= SEND:
        k = expo((t - SEND) / .32)
        y = lerp(COMP_Y, CARD_Y, k) + oy
        cc = comment_card(t)
        sc = lerp(.96, 1.0, k)
        ctx.add('screen', K.scale_im(cc, sc), W / 2, y, glass=16, alpha=clamp(k * 3) * oa)
        hx, hy = W / 2 - UIW / 2 + UIW - 80, y - CARD_H / 2 + 92
        for im, x, yy, a in mini_hearts(t, hx, hy):
            ctx.add('screen', im, x, yy, alpha=a * oa)
    # reply from lumarc_studio slides in under it
    if t >= REPLY - .02:
        k = expo((t - REPLY + .02) / .38)
        x = W / 2 + 18 + 260 * (1 - k)
        ctx.add('screen', reply_card(), x, REPLY_Y + oy, glass=16, alpha=clamp(k * 2) * oa)


# ======================================================================================= captions (own, voice-synced)
CAPS = [
    ([('WANT', W_WANT, 'white'), ('YOUR', W_YOUR, 'white'), ('BRAND', W_BRAND, 'white')], W_WANT - .04, W_TO - .02, 1440),
    ([('TO', W_TO, 'white'), ('BREAK', W_BREAK, 'grad'), ('OUT', W_OUT, 'grad')], W_TO - .04, W_OF - .02, 1440),
    ([('OF', W_OF, 'white'), ('THE', W_THE, 'white'), ('FEED?', W_FEED, 'white')], W_OF - .04, RUSH0 + .08, 1440),
    ([('AND', W_AND, 'white'), ("I'LL", W_ILL, 'white')], W_AND - .04, W_SHOW - .02, 1576),
    ([('SHOW', W_SHOW, 'white'), ('YOU', W_YOU, 'white'), ('HOW.', W_HOW, 'grad')], W_SHOW - .04, HIT - ASM - .01, 1576),     # gone before the logo slices fly in
]


def draw_caps(ctx, t):
    for words, a, z, y in CAPS:
        if a <= t < z:
            if t >= UI_OUT + .08:      # lifts last, into the brand glass
                k = expo((t - UI_OUT - .08) / .2)
                ctx_y = y - 180 * k
                K.pop_words(ctx, t, words, a, z, y=ctx_y)
            else:
                K.pop_words(ctx, t, words, a, z, y=y)


# ======================================================================================= cameras per shot
def camera(t):
    if t < T18:
        lt = t - START
        z = 1.19 + .035 * smooth(lt / 2.2) + .022 * kick(t - W_OUT, .14) * (t >= W_OUT) + .008 * kick(t - W_BREAK, .08) * (t >= W_BREAK)
        dx = dy = rot = 0.0
        for t0, amp in ((W_BREAK, 5.0), (W_OUT, 10.0)):
            if t >= t0:
                e = t - t0; dy += amp * math.exp(-e / .09) * math.sin(e * 2 * math.pi * 8); dx += amp * .6 * math.exp(-e / .09) * math.sin(e * 2 * math.pi * 6 + 1)
        if t >= W_OUT: rot = .0022 * math.exp(-(t - W_OUT) / .12) * math.sin((t - W_OUT) * 38)
        return dict(z=z, x=540., y=860., dx=dx, dy=dy, rot=rot)
    if t < T19:
        lt = t - T18
        z = 1.40 + .04 * smooth(lt / 1.4) + .02 * kick(t - W_LUM, .2) * (t >= W_LUM) + .015 * kick(t - HEART, .15) * (t >= HEART)
        return dict(z=z, x=540., y=1140., dx=0., dy=0., rot=0.)
    lt = t - T19
    z = 1.04 + .05 * smooth(lt / 1.2) + .03 * kick(t - W_HOW, .18) * (t >= W_HOW)
    return dict(z=z, x=540., y=820., dx=0., dy=0., rot=0.)


# ======================================================================================= end card (after ../lumarc-showcase s12)
HZ_Y, HZ_R = 1560, 1700


def space():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        col = np.zeros((H, W, 3), np.float32) + np.array([10, 10, 17], np.float32)
        r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - 870) / (H * .30)) ** 2)
        col += (np.clip(1 - r, 0, 1) ** 2.2)[..., None] * np.array([46, 32, 112], np.float32)
        cy = HZ_Y + HZ_R
        d = np.sqrt((xx - W / 2) ** 2 + (yy - cy) ** 2) - HZ_R
        fall = np.exp(-((xx - W / 2) / 520) ** 2)
        hue = np.clip(xx / W, 0, 1)[..., None]
        rimc = np.array([96, 124, 255], np.float32) * (1 - hue) + np.array([176, 104, 255], np.float32) * hue
        rim = np.exp(-(d / 2.6) ** 2) * fall
        atmo = np.where(d > 0, np.exp(-np.clip(d, 0, None) / 70), np.exp(np.clip(d, None, 0) / 14)) * fall
        haze = np.where(d > 0, np.exp(-d / 260), 0) * fall
        inside = d < 0
        col = np.where(inside[..., None], col * .45 + np.array([8, 7, 16], np.float32) * (1 - np.exp(d / 400))[..., None], col)
        col += rimc * (rim[..., None] * 1.25 + atmo[..., None] * .55 + haze[..., None] * .22)
        col += np.array([255, 255, 255], np.float32) * (np.exp(-(d / 1.4) ** 2) * fall ** 3 * .45)[..., None]
        v = 1 - .55 * np.clip(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .45) / (H * .62)) ** 2 - .15, 0, 1)
        return Image.fromarray(np.clip(col * v[..., None], 0, 255).astype(np.uint8)).convert('RGBA')
    return C('space', mk)


def bokeh_sprite(r, col):
    def mk():
        s = int(r * 2 + 8); y, x = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
        d = np.sqrt(x * x + y * y) / r
        a = np.clip((1.0 - d) / .35, 0, 1) ** 1.5 * (.7 + .3 * np.clip((d - .5) / .4, 0, 1))
        im = Image.new('RGBA', (s, s), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.filter(ImageFilter.GaussianBlur(r * .08 + .8))
    return C(('bokeh', r, col), mk)


BOKEH = [(150, 420, 40, .16, 6, -9, (70, 100, 255)), (930, 330, 26, .18, -5, -7, (150, 80, 255)),
         (900, 1420, 54, .12, -4, -6, (110, 80, 255)), (170, 1280, 18, .22, 7, -10, (120, 130, 255)),
         (640, 230, 12, .22, 3, -8, (170, 140, 255)), (1010, 900, 32, .13, -6, -9, (140, 70, 255)),
         (300, 1720, 22, .16, 4, -12, (90, 110, 255))]


def motes(img, t, alpha):
    if alpha <= .02: return
    for i, (x, y, r, a, vx, vy, col) in enumerate(BOKEH):
        lt = t - UI_OUT
        px = x + vx * lt + 10 * math.sin(lt * .6 + i); py = y + vy * lt
        tw = .8 + .2 * math.sin(t * 1.3 + i * 1.7)
        sp = bokeh_sprite(r, col)
        img.alpha_composite(E.fade(sp, min(1, a * alpha * tw * 2.0)), (int(px - sp.width / 2), int(py - sp.height / 2)))


def frost(fr, k):
    """heavy blur + deep-violet duotone (crushed blacks, vignette); k 0..1 = the glass rising."""
    if k <= .02: return fr
    ke = eout(k)
    small = fr.convert('RGB').resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(9 * (.35 + .65 * ke)))
    a = np.asarray(small, np.float32) / 255
    L = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    L = np.clip((L - .05) * 1.25, 0, 1) ** 1.35
    c0 = np.array([12, 11, 20], np.float32); c1 = np.array([40, 28, 98], np.float32); c2 = np.array([118, 96, 226], np.float32)
    col = c0 + (c1 - c0) * np.clip(L * 2.4, 0, 1)[..., None] + (c2 - c1) * (np.clip(L * 2.4 - 1, 0, 1) * .55)[..., None]
    vm = C('gmap', lambda: (1 - .7 * np.clip(((np.mgrid[0:H // 8, 0:W // 8][1] - W / 16) / (W / 8 * .7)) ** 2 + ((np.mgrid[0:H // 8, 0:W // 8][0] - H / 8 * .44) / (H / 8 * .6)) ** 2 - .12, 0, 1)).astype(np.float32))
    col *= vm[..., None]
    if k < 1: col = a * 255 + (col - a * 255) * ke
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert('RGBA')


LOGO_W = 760
N_SL = 8
GP = 150


def logo_img(): return C('logo', lambda: E.logo(LOGO_W))
def logo_glow(): return K.glow_of('s10_lg', logo_img(), pad=GP)
def logo_bloom(): return K.glow_of('s10_lb', logo_img(), layers=((70, (100, 70, 255), .9), (24, (160, 140, 255), .7)), pad=GP)


def hit_field():
    def mk():
        w, h = 1400, 1100
        y, x = np.mgrid[0:h // 4, 0:w // 4].astype(np.float32) * 4
        r2 = ((x - w / 2) / 520) ** 2 + ((y - h / 2) / 330) ** 2
        f = np.exp(-r2 * 1.4)[..., None] * np.array([96, 72, 230], np.float32) \
            + np.exp(-r2 * 5)[..., None] * np.array([60, 50, 120], np.float32) \
            + np.exp(-(((x - w / 2) / 680) ** 2 + ((y - h / 2) / 16) ** 2))[..., None] * np.array([120, 120, 255], np.float32)
        return np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32)
    return C('hitf', mk)


def soft_sides(im, frac=.3):
    w = im.width; f = max(2.0, w * frac); x = np.arange(w, dtype=np.float32)
    ramp = np.clip(np.minimum(x + .5, w - .5 - x) / f, 0, 1); ramp = ramp * ramp * (3 - 2 * ramp)
    a = np.asarray(im.getchannel('A'), np.float32) * ramp[None, :]
    out = im.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8))); return out


def slices_onto(out, t, cx, cy, s):
    k = (t - (HIT - ASM)) / ASM
    if not 0 <= k < 1: return False
    lg = K.scale_im(logo_img(), s); gl = K.scale_im(logo_glow(), s); gp = int(GP * s)
    sw = lg.width / N_SL; x0, y0 = int(cx - lg.width / 2), int(cy - lg.height / 2)
    def off(i, kk): return (1 if i % 2 == 0 else -1) * (300 + 220 * K.hrand(i, 9)) * (1 - ein(kk) if kk < 1 else 0)
    for i in range(N_SL):
        a0, a1 = int(i * sw), int((i + 1) * sw)
        piece = lg.crop((a0, 0, a1, lg.height)); gpiece = soft_sides(gl.crop((a0 + gp, 0, a1 + gp, gl.height)))
        o = off(i, k)
        for g in range(5, 0, -1):
            kk = max(0.0, k - .07 * g)
            out.alpha_composite(E.fade(gpiece, .3 * (1 - g / 6) * clamp(k * 4) * (1 - k ** 3)), (x0 + a0, int(y0 - gp + off(i, kk))))
        out.alpha_composite(E.fade(gpiece, .9 * clamp(k * 3)), (x0 + a0, int(y0 - gp + o)))
        out.alpha_composite(E.fade(piece, clamp(k * 3)), (x0 + a0, int(y0 + o)))
    return True


def shock(img, t, cx, cy):
    k = (t - HIT) / .6
    if not 0 <= k < 1: return img
    lay = Image.new('L', (W // 2, H // 2)); d = ImageDraw.Draw(lay)
    for R0, wm, am, dl in ((40, .7, .55, 0), (10, .45, .3, .08)):
        kk = clamp((t - HIT - dl) / .6)
        if kk <= 0: continue
        R = (R0 + 1150 * eout(kk)) / 2; wd = max(1, int((18 * (1 - kk) + 2) * wm / 2))
        d.ellipse((cx / 2 - R, cy / 2 - R * .62, cx / 2 + R, cy / 2 + R * .62), outline=int(255 * am * (1 - kk) ** 1.4), width=wd)
    g = lay.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    add = np.asarray(g, np.float32)[..., None] / 255 * np.array([160, 150, 255], np.float32)
    o = np.asarray(img.convert('RGB'), np.float32) + add
    return Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).convert('RGBA')


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
        return out, r - l, np.asarray(m, np.float32) / 255
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
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(im.crop((0, 0, im.width, im.height - dy)), (0, dy))
    return E.fade(out, clamp(k * 2.2))


LINE1 = [('Be', 300, False), ('seen.', 700, True)]
LINE2 = [('Be', 300, False), ('remembered.', 700, True)]


def draw_tagline(fr, t, y1, y2):
    for words, t0s, y, sh0 in ((LINE1, (TAG1, TAG1 + .08), y1, SWEEP1 + .45), (LINE2, (TAG2, TAG2 + .08), y2, SWEEP1 + .25)):
        for (im, xo, gm), t0, (txt, _, grad) in zip(line_img(words), t0s, words):
            if grad: im = K.sheen(im, (t - sh0) / .5, gm, 30, .55)
            r = rise(im, expo((t - t0 + .02) / .4))
            if r is None: continue
            fr.alpha_composite(r, (int(W / 2 + xo - r.width / 2), int(y - r.height / 2)))


def pill():
    return C('pill', lambda: E.pill('Comment  “LUMARC”', 60, 700, grad=True, padx=80, pady=43))


def pill_glow():
    def mk():
        p = pill(); a = p.getchannel('A').point(lambda v: 255 if v > 200 else 0)
        big = Image.new('L', (p.width + 200, p.height + 200)); big.paste(a, (100, 100))
        g = Image.new('RGBA', big.size, (110, 80, 255, 0)); g.putalpha(big.filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * .75)))
        return g
    return C('pillglow', mk)


def handle():
    return C('handle', lambda: E.text_im('@lumarc_studio  ·  slumarc.com', 42, 500, (214, 211, 236)))


def layout(t):
    up = expo((t - LIFT) / .55)
    ly = 820 - 130 * up
    ls = 1.0 - .21 * up                         # 760 -> 600 px
    if t >= HIT: ls *= 1 + .14 * (1 - expo((t - HIT) / .3))
    ls *= 1 + .015 * smooth((t - PILL) / 1.6)
    y1 = ly + 225; y2 = y1 + 96
    return ly, ls, y1, y2


def end_card(t, base):
    """the end card over `base` (RGBA full frame: frosted world blending into space)."""
    out = base
    motes(out, t, clamp((t - HIT) / .6))
    ly, ls, y1, y2 = layout(t)
    cx = W / 2
    if t >= HIT - ASM:
        if t >= HIT:
            out = shock(out, t, cx, ly)
            bl = K.scale_im(logo_bloom(), ls)
            ba = (.7 + .15 * math.sin((t - HIT) * 2.4)) * clamp((t - HIT) / .2)
            out.alpha_composite(E.fade(bl, ba), (int(cx - bl.width / 2), int(ly - bl.height / 2)))
        s0 = ls * (1 + .25 * (1 - ein((t - (HIT - ASM)) / ASM))) if t < HIT else ls
        if not slices_onto(out, t, cx, ly, s0):
            lg = logo_img()
            for t0, d in ((HIT + .08, .4), (SWEEP1, .7)):
                sk = (t - t0) / d
                if 0 < sk < 1: lg = K.sheen(lg, sk, K.ink_mask('s10_logo', logo_img(), 90, 200), 40, .6)
            lg = K.scale_im(lg, ls, lanczos=True)
            out.alpha_composite(lg, (int(cx - lg.width / 2), int(ly - lg.height / 2)))
        if t >= HIT - .02:
            kb = .95 * (1 - eout((t - HIT) / .45)) if t >= HIT else .45
            if kb > .01:
                f = hit_field(); out = K.add_light(out, f, kb, int(cx - f.shape[1] / 2), int(ly - f.shape[0] / 2))
    draw_tagline(out, t, y1, y2)
    if t >= PILL:
        k = t - PILL; s = (.55 + .45 * back(k / .32, 2.4)) * (1 + .018 * (1 - math.cos((t - PILL - .32) * 2.6)) if k > .32 else 1)
        py = 1190
        pg = pill_glow(); out.alpha_composite(E.fade(pg, clamp(k / .3) * (.8 + .2 * math.sin(t * 2.6))), (int(cx - pg.width / 2), int(py - pg.height / 2 + 14)))
        p = pill()
        ps = (t - SWEEP2) / .6
        if 0 < ps < 1: p = K.sheen(p, ps, K.ink_mask('s10_pill', pill(), 200, 230), 40, .45)
        p = K.scale_im(p, s)
        out.alpha_composite(E.fade(p, clamp(k / .08)), (int(cx - p.width / 2), int(py - p.height / 2)))
    if t >= HANDLE:
        k = eout((t - HANDLE) / .5); hd = handle()
        out.alpha_composite(E.fade(hd, k), (int(cx - hd.width / 2), int(1318 + 16 * (1 - k) - hd.height / 2)))
    return out


# ======================================================================================= loop handshake (feed, frame 0)
D0, A_, W_ = 650., 22., 13.                        # s01: scroll(t) = S* - D0 e^(-A t) cos(W t)
V0 = D0 * A_                                       # 14 300 px/s at frame 0
S_STAR = FK.center_scroll(FK.SPECIAL)
FL_T = LOOP_T - FL0                                # flick duration (to the virtual frame 0)
FL_P = 1.5                                         # velocity ramp exponent
FL_TRAVEL = V0 * FL_T / (FL_P + 1)                 # content travel during the flick (~1.9 k px = one screen)


def flick_u(t): return clamp((t - FL0) / FL_T)
def flick_travel(t):
    u = flick_u(t); return FL_TRAVEL * u ** (FL_P + 1)
def flick_vel(t):
    u = flick_u(t); return V0 * u ** FL_P


def frame0_media():
    """his Reel's media exactly as frame 0 shows it: studio + his first frame (t=0), medium framing."""
    def mk():
        try:
            av = E.Avatar(0.0); a0 = av.frame(0.0).copy(); av.r.close()
        except Exception:
            a0 = None
        world = E.studio().convert('RGBA')
        if a0 is not None: world.alpha_composite(a0)
        m = world.convert('RGB').crop((0, 300, W, 300 + FK.MEDIA_H)).convert('RGBA')
        try:
            from sections import _A_kit as KA
            m.alpha_composite(KA.progress_bar(0.0), (0, FK.MEDIA_H - 6))
        except Exception:
            pass
        return m
    return C('f0media', mk)


def feed_screen(scroll):
    """the feed (no chrome) at `scroll`, his post with its frame-0 media and like count."""
    m = frame0_media()
    scr = FK.screen(scroll, special=m.convert('RGB'), t=0.0, chrome=False)
    try:
        from sections import _A_kit as KA
        top = KA.special_top(scroll)
        FK._paste_clip(scr, KA.special_foot(KA.likes_at(0.0)), 0, top + FK.HEAD_H + FK.MEDIA_H)
    except Exception:
        pass
    return scr


def flick_frame(t, card):
    """end card flicked up into the scrolling feed (screen RGBA)."""
    tr = flick_travel(t); v = flick_vel(t)
    # finger anticipation: the card dips a hair before the flick
    s = S_STAR - D0 - (FL_TRAVEL - tr)
    scr = feed_screen(s)
    scr.alpha_composite(card, (0, int(round(-tr))))
    if v > 120: scr = K.vblur(scr, min(240, v / 60))
    k = expo((t - FL0) / .2)
    scr.alpha_composite(FK.chrome_top(), (0, int(round(-FK.TOP_Y * (1 - k)))))
    scr.alpha_composite(FK.chrome_nav(), (0, int(round(FK.NAV_Y + FK.NAV_H * (1 - k)))))
    return scr


# ======================================================================================= draw
def draw(ctx, lt, t):
    ctx.captions = False
    P = ctx.post
    P['vignette'] = .36
    # -------- end card + flick
    if t >= HIT:
        gone = smooth((t - HIT) / .45)
        if gone < 1:
            ctx.cam = camera(min(t, T19 + 1.19))
            ctx.bg_img = studio_cta()
            # his held last frame from our own cached reader (a render chunk may start after the voice ends)
            ctx.avatar['show'] = False
            ctx.add('front', last_avatar(), 0, 0, center=False)
        else:
            ctx.full = space()
        def wrap(fr):
            if gone < 1:
                base = frost(fr, 1.0)
                base = Image.blend(base, space(), gone)
            else:
                base = space().copy()
            card = end_card(t, base.copy())
            if t >= FL0: return flick_frame(t, card)
            if FL0 - .07 <= t < FL0:   # thumb lands: the card gives a hair (press) before the flick
                d = 1 - .012 * K.bump(t, FL0 - .07, FL0 + .07)
                return E.zoom(card.convert('RGB'), d, (W / 2, H * .62)).convert('RGBA')
            return card
        ctx.wrap = wrap
        P['vignette'] = .3
        if t >= FL0:
            k = flick_u(t); P['vignette'] = .3 * (1 - k); P['grain'] = 1 - .75 * k
        if HIT <= t < HIT + .08: P['rgb'] = 4 * clamp(1 - (t - HIT) / .08)
        return
    ctx.cam = camera(t)
    # -------- beat A: the frosted feed wall + break-out
    if t < T18:
        ctx.bg_img = wall_image(t)
        b, f = shard_layers(t)
        if b is not None: ctx.add('behind', b, 0, 0, center=False)
        if f is not None: ctx.add('front', f, 0, 0, center=False)
        hg = hero_glow(t)
        if hg is not None: ctx.add('screen', hg[0], hg[1], hg[2])
        hl = hero_layer(t)
        if hl is not None: ctx.add('screen', hl[0], hl[1], hl[2], center=False)
        # light of the break on him (rim from behind / above)
        if t >= W_OUT:
            K.top_light(ctx, (176, 156, 255), .7 * math.exp(-(t - W_OUT) / .16), y0=560, y1=1150, rim=.9, broad=.06)
        elif t >= W_BREAK:
            K.top_light(ctx, (170, 150, 255), .35 * leak(t), y0=560, y1=1150, rim=1.0, broad=.0)
        if t >= W_OUT:
            P['flash'] = .18 * math.exp(-(t - W_OUT) / .05); P['flash_col'] = (190, 170, 255)
            if t < W_OUT + .06: P['rgb'] = 3.0
        if t >= RUSH0:
            P['zoom_blur'] = .35 * smooth((t - RUSH0) / (T18 - RUSH0))
        draw_caps(ctx, t)
        return
    # -------- beats B / C: he is out of the feed, back in his real studio (shallow DOF so the glass UI reads)
    ctx.bg_img = studio_cta()
    if t > VEND - .04 + 1e-4:    # the engine's reader cannot serve the held frame to a render chunk starting here
        ctx.avatar['show'] = False
        ctx.add('front', last_avatar(), 0, 0, center=False)
    draw_ui(ctx, t)
    draw_caps(ctx, t)
    if t < T18 + .2:     # the post passing the lens wipes off the frame (hides the jump cut); nearest thing: on top
        hl = hero_layer(t)
        if hl is not None: ctx.add('screen', hl[0], hl[1], hl[2], center=False)
    if t >= UI_OUT:      # the brand glass rises over the world
        k = clamp((t - UI_OUT - .06) / (HIT - UI_OUT - .06))
        def wrap(fr, k=k):
            out = frost(fr, k)
            return end_card(t, out) if t >= HIT - ASM else out
        ctx.wrap = wrap


def last_avatar():
    def mk():
        tt = round(VEND - .04, 2)
        av = E.Avatar(tt); im = av.frame(tt).copy(); av.r.close(); return im
    return C('last_av', mk)


def studio_cta():
    """his studio for the comment / reply shots: a touch of lens blur (DOF) and a stop down so the glass UI reads."""
    return studio_graded(3.0, .26)


