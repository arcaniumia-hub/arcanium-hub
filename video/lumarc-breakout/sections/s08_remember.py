"""s08 — "The brand you still remember tomorrow." (TL15, 17.48–19.96)

17.48  JUMP CUT -> wide centred framing (z 1.10 -> 1.17 slow push): behind him a WALL OF POSTS (the feed, as mini post
       cards floating deep in the dark studio — dimmed, defocused, perspective-tilted, parallax) scrolls up fast with
       motion blur and locks into place (elastic settle) just before "BRAND".
17.70  "BRAND" -> one post (silence.one — the SILENCE ONE film LUMARC made, playing live) ignites: it lifts out of the
       wall (spring 1.08), exposure flash + sheen, a brand-gradient border draws itself on clockwise with a star glint
       riding its head, bloom + purple glow; the rest of the wall drops a stop (spotlight) and the camera taps in.
18.29  "YOU STILL" -> time passes: the studio sinks into night, clock ticks, grey fog rolls across the wall; every other
       post desaturates, blurs, dims and recedes — forgotten. The LUMARC-made post stays crisp and bright.
18.80  "REMEMBER" -> it pushes hard toward camera (spring to 1.30 with overshoot, clear of his head), leaves an
       after-image (two border echoes ripple out), light sweep, the halo behind his head swells; camera kick + lean.
19.21  a frosted lock-screen card rises over his chest ("TODAY 11:59 PM"; captions off from here — the card carries the
       word). 19.333 "TOMORROW." -> the date rolls TODAY -> TOMORROW, 11:59 PM -> 8:00 AM, morning light blooms in the
       glass and returns to the studio (fog burns off). The remembered post flies down in an arc right of his face,
       shedding its chrome but keeping its brand halo (light trail, motion blur), into the silence.one notification.
19.87  the lock card is dismissed (drops out of frame with motion blur) -> clean studio at the 19.96 cut.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _D_kit as K
from sections import feedkit as FK

START, END = E.span(15, 15)               # 17.48 – 19.96

# word onsets measured on src/tight16k.raw (10 ms RMS envelope + 3-band spectrogram: "s" frication 18.42-18.60,
# "t" release of STILL 18.64, "ill" 18.65-18.80, REMEMBER from 18.80, "t" burst of TOMORROW 19.34)
WORDS = {'THE': 17.59, 'BRAND': 17.70, 'YOU': 18.29, 'STILL': 18.42, 'REMEMBER': 18.80, 'TOMORROW.': 19.34}
W_THE, W_BRAND, W_YOU, W_STILL, W_REM, W_TOM = (WORDS[k] for k in ('THE', 'BRAND', 'YOU', 'STILL', 'REMEMBER', 'TOMORROW.'))
CARD0 = W_TOM - .13                        # lock card starts rising
PAGES = K.make_pages([[('THE', W_THE, False), ('BRAND', W_BRAND, False)],
                      [('YOU', W_YOU, False), ('STILL', W_STILL, False)],
                      [('REMEMBER', W_REM, True)]], CARD0 + .01)
CAP_Y = 1440

clamp, lerp = E.clamp, K.lerp
W, H = E.W, E.H
WHITE = (250, 249, 246)

# ---------------------------------------------------------------- timing
SCROLL1 = W_BRAND - .05                    # wall locks
FOG0 = W_YOU - .02
ROLL0 = W_TOM - .01                        # date roll starts on the word (first frame of the 't' burst)
FLY0, FLY1 = W_TOM + .08, W_TOM + .34      # remembered post flies into the notification
EXIT0 = 19.865                             # lock card drops away on the last frames (clean studio at the 19.96 cut)
NOTE0 = W_TOM + .15                        # notification banner drops in

CUES = [
    (START - .02, 'swipe', {'gain': -4}),                     # cut + the wall scrolls
    (SCROLL1, 'tick', {'gain': -6}),                          # wall locks
    (W_BRAND, 'shimmer', {'gain': -4, 'pan': .35}),           # the brand's post ignites
    (W_BRAND, 'pop', {'gain': -6, 'pan': .35}),
    (FOG0, 'whoosh', {'gain': -13}),                          # fog rolls in, night falls
    (W_YOU + .01, 'clock', {'i': 0, 'gain': -4}),
    (W_STILL, 'clock', {'i': 1, 'gain': -4}),
    (W_STILL + .13, 'clock', {'i': 0, 'gain': -6}),
    (W_STILL + .25, 'clock', {'i': 1, 'gain': -8}),
    (W_REM, 'impact', {'gain': -7}),                          # REMEMBER push
    (W_REM + .01, 'glass', {'gain': -6, 'seed': 4, 'pan': .3}),
    (CARD0 - .03, 'swoosh_up', {'gain': -8}),                 # lock card rises
    (ROLL0, 'tick', {'gain': -2}),                            # date roll
    (ROLL0 + .05, 'tick', {'gain': -5}),
    (ROLL0 + .09, 'tick', {'gain': -7}),
    (FLY0, 'whoosh', {'gain': -12, 'pan': .3}),               # post flies into the notification
    (NOTE0 + .03, 'notify', {'gain': -1}),
    (FLY1, 'pop', {'gain': -8, 'pan': .25}),
    (EXIT0 + .01, 'flick', {'gain': -9}),                    # lock card dismissed into the cut
]
CUES = [(round(t_, 3), k_, p_) for t_, k_, p_ in CUES]


# ---------------------------------------------------------------- the wall
TW, IMG_H, HEAD, FOOT = 240, 300, 46, 42
TH = HEAD + IMG_H + FOOT
COLS = [540 + (i - 2) * 262 for i in range(5)]
ROWS = [-20, 380, 780, 1180]
HERO = (3, 1)                               # (col, row index) -> world (802, 380)
TILES = [
    ('loc2', 'brightside.cafe'), ('bad_flyer', 'tonys.pizza.nyc'), ('loc4', 'jess.travels'), ('close_food', 'smash.burger.co'),
    ('loc5', 'city.realty'), ('carousel_1', 'northroast.coffee'), ('bad_blurry_photo', 'burgerhouse_'), ('loc3', 'sunset.rooftop'),
    (None, None), ('design_post', 'maisoncrumb'), ('loc7', 'beach.days'), ('bad_shaky_video', 'salon.glow.studio'),
    ('website', 'oliva.restaurant'), ('close_skill', 'the.craft.bench'), ('loc6', 'urban.gym.co'), ('carousel_2', 'petal.florist'),
    ('close_service', 'corner.latte'), ('loc1', 'fresh.bowl'), ('bad_flyer', 'daily.donuts'), ('loc2', 'moda.boutique'),
]
LIKES = ['212', '9', '1,031', '2,291', '57', '3,880', '14', '842', '', '5,402', '388', '6', '1,207', '976', '133', '419', '451', '87', '31', '264']


def slot_list():
    out = []
    k = 0
    for r, y in enumerate(ROWS):
        for c, x in enumerate(COLS):
            out.append((c, r, x, y)); k += 1
    return out
SLOTS = slot_list()


def tile_frame(user, likes, verified=False, liked=False):
    """mini post card chrome (header, footer, border) without the media (RGBA TW x TH)."""
    def mk():
        im = Image.new('RGBA', (TW, TH), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
        av = FK._avatar_circle(30, 'lumarc' if user == 'lumarc_studio' else user, ring=False)
        im.alpha_composite(av, (10, (HEAD - 30) // 2))
        f = E.font(17, 700); d.text((48, HEAD // 2), user, font=f, fill=(240, 240, 242), anchor='lm')
        if verified: im.alpha_composite(FK.icon('verified', 17, (61, 133, 250)), (48 + int(f.getlength(user)) + 5, HEAD // 2 - 8))
        im.alpha_composite(FK.icon('dots', 22), (TW - 30, HEAD // 2 - 11))
        y = HEAD + IMG_H + 9
        im.alpha_composite(FK.icon('heart_fill', 24, (255, 48, 64)) if liked else FK.icon('heart', 24), (10, y))
        im.alpha_composite(FK.icon('comment', 24), (44, y)); im.alpha_composite(FK.icon('share', 24), (78, y))
        im.alpha_composite(FK.icon('save', 24), (TW - 34, y))
        if likes: d.text((112, y + 12), f'{likes} likes', font=E.font(15, 600), fill=(225, 225, 230), anchor='lm')
        return im
    return K.C(('s08frame', user, likes, verified, liked), mk)


def tile_img(i):
    asset, user = TILES[i]
    def mk():
        im = tile_frame(user, LIKES[i]).copy()
        ay = .5 if i < 10 else .35
        im.paste(K.cover(E.asset(asset), TW, IMG_H, ay=ay), (0, HEAD))
        im = K.round_img(im, 16)
        b = Image.new('L', (TW, TH)); ImageDraw.Draw(b).rounded_rectangle((0, 0, TW - 1, TH - 1), 16, outline=255, width=2)
        e = Image.new('RGBA', (TW, TH), (255, 255, 255, 0)); e.putalpha(b.point(lambda v: int(v * .16))); im.alpha_composite(e)
        return im
    return K.C(('s08tile', i), mk)


HM0, HM1 = 26.20, 27.45                  # HYPER excerpt shown in the remembered post (slow motion .45x)


def hero_frames():
    """the excerpt decoded ONCE from a fixed origin (pure function of t regardless of where a render chunk starts),
    cropped to the post's 4:5 media box."""
    def mk():
        n = int(round((HM1 - HM0) * E.FPS)) + 1
        r = E.Reader(E.HYPER, HM0, HM1 - HM0 + .2, vf=f'fps={E.FPS},scale=540:960')
        h = int(540 * 1.25); y0 = int(960 * .575 - h / 2); out = []
        for i in range(n):
            f = r.get(i, (540, 960)); out.append(f.crop((0, y0, 540, y0 + h)))
        r.close(); return out
    return K.C('s08heroframes', mk)


def hero_media(t, size=(TW, IMG_H)):
    fr = hero_frames()
    x = clamp(((26.25 + (t - START) * .45) - HM0) * E.FPS / (len(fr) - 1)) * (len(fr) - 1)
    i = min(len(fr) - 2, int(x)); f = x - i
    im = fr[i] if f < .02 else Image.blend(fr[i], fr[i + 1], f)       # frame-blended slow motion (no judder)
    return im.resize(size, Image.BILINEAR)


def hero_img(t):
    im = tile_frame('silence.one', '48.2K', True, True).copy()
    im.paste(hero_media(t), (0, HEAD))
    im.alpha_composite(FK.icon('reels', 26), (TW - 36, HEAD + 10))
    return K.round_img(im, 16)


def spot(t):
    """on BRAND the rest of the wall drops a stop: a spotlight on the brand's post."""
    return K.smooth((t - W_BRAND + .02) / .22)


def forget(i, t):
    """0 = vivid, 1 = forgotten (staggered)."""
    d = .02 + .18 * K.hrand(i, 7)
    return K.smooth((t - (FOG0 + d)) / .42)


def scroll_off(t):
    """wall offset: it arrives scrolling up and locks with a small elastic settle."""
    u = (t - START) / (SCROLL1 - START)
    if u >= 1:
        k = t - SCROLL1; return -10 * math.exp(-k * 9) * math.sin(k * 20 + .6) * 1.5
    return 560 * (1 - K.expo(u)) ** 1.15 - 14 * math.sin(math.pi * u) * u


WALL_OX, WALL_OY = -170, -250             # wall-canvas origin in wall coordinates
WCW, WCH = 1420, 1700
WALL_S, WALL_RX, WALL_F = .92, 8., 2400.  # the wall sits deeper than him: smaller, top tipped away
WALL_C = (540., 760.)                      # world position of the canvas centre


def wall_scale(z):
    return WALL_S * (1.12 / z) ** .5        # parallax: the deeper wall zooms less than him


def wall_pt(x, y, z):
    """wall coords -> world coords."""
    return K.proj([(x - WALL_OX, y - WALL_OY)], WCW, WCH, WALL_C[0], WALL_C[1], wall_scale(z), WALL_RX, 0, 0, WALL_F)[0]


def tile_bg(i):
    """the tile as seen on the wall: dimmer, a touch desaturated, slightly defocused (DOF)."""
    return K.C(('s08tilebg', i), lambda: K_pad(K.grade(tile_img(i), sat=.80, bright=.58, contrast=.94), 14).filter(ImageFilter.GaussianBlur(1.9)))


def tile_half(i):
    return K.C(('s08tilehalf', i), lambda: tile_bg(i).resize((tile_bg(i).width // 2, tile_bg(i).height // 2), Image.BILINEAR))


WQ = 2                                     # the wall is defocused: built + warped at half resolution, then upscaled
FLV = 16                                   # quantized "forgetting" levels per tile (cached)


def tile_level(i, f):
    """tile i (half resolution) at forgetting level f: desaturated, dimmed, flattened, defocused, receding."""
    k = int(round(clamp(f) * FLV))
    def mk():
        hb = tile_half(i)
        if k == 0: return hb
        g = k / FLV
        hb = K.grade(hb, sat=1 - .9 * g, bright=1 - .42 * g, contrast=1 - .40 * g, lift=10 * g)
        hb = K.fast_blur(hb, 3.5 * g); sc = 1 - .08 * g
        return hb.resize((int(hb.width * sc), int(hb.height * sc)), Image.BILINEAR)
    return K.C(('s08tlv', i, k), mk)


def wall_layer(t, z):
    """the forgettable posts (world RGBA) — the remembered post is drawn separately, in front."""
    gone = 1 - K.smooth((t - ROLL0) / .35)                       # gone for good by morning
    if gone < .01: return None
    off = scroll_off(t)
    can = Image.new('RGBA', (WCW // WQ, WCH // WQ), (0, 0, 0, 0))
    for i, (c, r, x, y) in enumerate(SLOTS):
        if (c, r) == HERO: continue
        f = forget(i, t)
        fy = y + off + 4 * math.sin(t * 1.3 + i) - 26 * f - WALL_OY
        fx = x + 3 * math.cos(t * 1.1 + i * 1.7) - WALL_OX
        if fy + TH < -40 or fy - TH > WCH + 40: continue
        a = (1 - .78 * f) * gone if f > .01 else gone
        if a < .01: continue
        im = tile_level(i, f)
        K.paste(can, im, fx / WQ - im.width / 2, fy / WQ - im.height / 2, alpha=a)
    v = abs(scroll_vel(t))
    if v > 120: can = K.vsmear(can, min(90, v / 30 * .9) / WQ)
    q = K.quad(WCW, WCH, WALL_C[0], WALL_C[1], wall_scale(z), WALL_RX, 0, 0, WALL_F)
    r = K.warp(can, [(x / WQ, y / WQ) for x, y in q], bounds=(W // WQ, H // WQ))
    if r is None: return None
    im, x0, y0 = r
    return im.resize((im.width * WQ, im.height * WQ), Image.BILINEAR), x0 * WQ, y0 * WQ


def K_pad(im, p):
    out = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); out.paste(im, (p, p)); return out


def scroll_vel(t):
    return (scroll_off(t + 1 / 120) - scroll_off(t - 1 / 120)) * 60


# ---------------------------------------------------------------- fog
FOG_R, FOG_C = 480, 270                     # fog field (quarter res of the frame), mirrored to wrap horizontally


def fog_field(seed=31):
    """layered value noise, features ~1.8x wider than tall (fog banks), seamless horizontally (mirrored)."""
    def mk():
        rng = np.random.default_rng(seed)
        acc = np.zeros((FOG_R, FOG_C), np.float32); amp = 1.0; tot = 0
        for oc in (3, 6, 12, 24):
            n = rng.random((oc * 3 + 2, oc + 2)).astype(np.float32)
            im = Image.fromarray((n * 255).astype(np.uint8)).resize((FOG_C, FOG_R), Image.BICUBIC)
            acc += np.asarray(im, np.float32) / 255 * amp; tot += amp; amp *= .5
        acc /= tot
        acc = (acc - acc.min()) / (acc.max() - acc.min())
        return np.concatenate([acc, acc[:, ::-1]], 1)
    return K.C(('fog', seed), mk)


def _fog_alpha(t, speeds, seeds, gain, bias):
    n = 0
    for sp, sd, wt in zip(speeds, seeds, (.6, .4)):
        F = fog_field(sd); sh = int(round((t - START) * sp / 4)) % F.shape[1]
        n = n + wt * np.roll(F, -sh, 1)[:, :FOG_C]
    return np.clip((n - bias) * gain, 0, 1)


def fog_layer(t, dens):
    """grey fog banks rolling across the wall (behind him)."""
    if dens < .01: return None
    a = _fog_alpha(t, (70, -34), (31, 7), 2.1, .22)
    yy = np.linspace(0, 1, FOG_R, dtype=np.float32)[:, None]
    shape = np.clip(1.25 - np.abs(yy - .36) * 1.7, 0, 1)
    al = np.clip((a * .80 + .16) * shape * dens, 0, .88)
    m = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)).resize((W, H), Image.BICUBIC)
    out = Image.new('RGBA', (W, H), (96, 92, 118, 0)); out.putalpha(m)
    return out


def fog_front(t, dens):
    """a thin low-lying bank drifting in front of him (only the lower frame) — sells the volume."""
    if dens < .01: return None
    a = _fog_alpha(t, (110, 60), (5, 12), 2.4, .35)
    yy = np.linspace(0, 1, FOG_R, dtype=np.float32)[:, None]
    shape = np.clip((yy - .66) / .22, 0, 1) ** 1.3
    al = np.clip(a * shape * dens * .42, 0, .5)
    y0 = int(FOG_R * .64)                       # only the lower third carries this bank
    m = Image.fromarray((al[y0:] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)).resize((W, H - y0 * 4), Image.BICUBIC)
    out = Image.new('RGBA', m.size, (110, 106, 132, 0)); out.putalpha(m)
    return out, y0 * 4


def fog_density(t):
    d = .82 * K.smooth((t - FOG0) / .55)
    return d * (1 - .62 * K.smooth((t - ROLL0) / .5))          # morning burns the fog off (hand-off to the studio)


# ---------------------------------------------------------------- the remembered post
HX, HY = COLS[HERO[0]], ROWS[HERO[1]]


def border_ring():
    def mk():
        p = 18; w, h = TW + 2 * p, TH + 2 * p
        m = Image.new('L', (w * 3, h * 3)); ImageDraw.Draw(m).rounded_rectangle((p * 3 - 9, p * 3 - 9, (p + TW) * 3 + 8, (p + TH) * 3 + 8), 20 * 3, outline=255, width=13)
        m = m.resize((w, h), Image.LANCZOS)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
        gl = Image.new('RGBA', (w, h), (140, 110, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(7)))
        out = Image.new('RGBA', (w, h)); out.alpha_composite(gl); out.alpha_composite(gl); out.alpha_composite(g)
        return out
    return K.C('s08ring', mk)


def ring_reveal(k):
    """border drawn on clockwise from the top-left corner, k 0..1."""
    rg = border_ring()
    if k >= .999: return rg
    w, h = rg.size
    def mk():
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        a0 = math.degrees(math.atan2(-h / 2, -w / 2))
        return (np.degrees(np.arctan2(yy - h / 2, xx - w / 2)) - a0) % 360
    ang = K.C(('s08ang', w, h), mk)
    m = (ang <= k * 360).astype(np.float32)
    a = np.asarray(rg.getchannel('A'), np.float32) * m
    out = rg.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8))); return out


def hero_state(t):
    """(x, y, scale, alpha) of the remembered post in WORLD coords (before the flight)."""
    off = scroll_off(t)
    x, y = wall_pt(HX, HY + off + 4 * math.sin(t * 1.3 + 3), camera(t)['z'])
    kb = t - W_BRAND + .01
    s = 1.0
    if kb >= 0: s = lerp(1, 1.08, K.spring(kb, 2.4, 7.5)) + .04 * K.kick(kb, .10)
    if t >= W_REM - .01:
        k = t - W_REM + .01
        s = lerp(1.08, 1.30, K.spring(k, 2.4, 7.5)) + .03 * K.kick(kb, .10)
        x += 34 * K.expo(k / .3); y -= 18 * K.expo(k / .3)          # comes forward, clear of his head
    return x, y, s


def sheen(img, k):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx / w + yy / h * .6) / 1.6; c = lerp(-.3, 1.3, k)
    band = np.exp(-((u - c) / .09) ** 2) * .55
    a = np.asarray(img, np.float32)
    rgb = a[..., :3] + (255 - a[..., :3]) * band[..., None]
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]).astype(np.uint8), 'RGBA')


def hero_sprite(t):
    """crisp remembered post with its border + glow (RGBA)."""
    im = hero_img(t)
    fl = K.kick(max(0., t - W_BRAND), .10) if t >= W_BRAND - .01 else 0
    if fl > .02: im = K.grade(im, bright=1 + .55 * fl, lift=30 * fl)
    if W_BRAND - .01 <= t < W_BRAND + .34: im = sheen(im, (t - W_BRAND + .01) / .35)
    if W_REM - .01 <= t < W_REM + .40: im = sheen(im, (t - W_REM + .01) / .41)
    p = 18
    out = Image.new('RGBA', (TW + 2 * p, TH + 2 * p), (0, 0, 0, 0))
    if t >= W_BRAND - .01:
        out.alpha_composite(ring_reveal(K.cub((t - W_BRAND + .01) / .26)))
    out.alpha_composite(im, (p, p))
    return out


# ---------------------------------------------------------------- lock screen card
LW, LH = 900, 556
LR = 54
NOTE_Y = 376                                # notification panel top (card coords)
NW, NH = 840, 150
THUMB = (NW - 22 - 100, NOTE_Y + 12, 100, 125)  # x, y, w, h (card coords)


def lock_base():
    def mk():
        im = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
        m = K.rounded_mask(LW, LH, LR)
        body = Image.new('RGBA', (LW, LH), (12, 10, 24, 0)); body.putalpha(m.point(lambda v: int(v * .52))); im.alpha_composite(body)
        im.alpha_composite(E.glass_panel(LW, LH, LR, alpha=.08, border=.55))
        d = ImageDraw.Draw(im)
        # padlock
        cx = LW // 2; d.rounded_rectangle((cx - 15, 42, cx + 15, 66), 6, fill=(236, 236, 244, 230))
        d.arc((cx - 11, 26, cx + 11, 52), 180, 360, fill=(236, 236, 244, 230), width=5)
        return im
    return K.C('s08lockbase', mk)


def note_panel():
    def mk():
        im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
        m = K.rounded_mask(NW, NH, 36)
        body = Image.new('RGBA', (NW, NH), (38, 34, 58, 0)); body.putalpha(m.point(lambda v: int(v * .78))); im.alpha_composite(body)
        b = Image.new('L', (NW, NH)); ImageDraw.Draw(b).rounded_rectangle((1, 1, NW - 2, NH - 2), 36, outline=255, width=2)
        e = Image.new('RGBA', (NW, NH), (255, 255, 255, 0)); e.putalpha(b.point(lambda v: int(v * .30))); im.alpha_composite(e)
        # app icon: the brand's avatar (gold SILENCE ONE)
        ic = K.cover(Image.open(os.path.join(E.V, 'silence-motion/img/hero.jpg')), 92, 92, ay=.45).convert('RGBA')
        ic = K.round_img(ic, 22); im.alpha_composite(ic, (22, (NH - 92) // 2))
        d = ImageDraw.Draw(im)
        d.text((134, 30), 'silence.one', font=E.font(38, 700), fill=WHITE)
        fw = int(E.font(38, 700).getlength('silence.one'))
        im.alpha_composite(FK.icon('verified', 30, (61, 133, 250)), (134 + fw + 10, 36))
        d.text((134 + fw + 52, 32), 'now', font=E.font(34, 500), fill=(176, 172, 196))
        d.text((134, 82), 'Still on your mind? It’s back.', font=E.font(34, 500), fill=(226, 224, 236))
        return im
    return K.C('s08note', mk)


def roll_word(a_img, b_img, k, box_h):
    """cylinder roll from a_img to b_img (k 0..1) inside a box of height box_h; returns RGBA (w = max widths)."""
    w = max(a_img.width, b_img.width); h = box_h
    out = Image.new('RGBA', (w, h + 40), (0, 0, 0, 0))
    R = h * .55
    for img, ang in ((a_img, k * 90), (b_img, (k - 1) * 90)):
        if abs(ang) >= 89.5: continue
        c = math.cos(math.radians(ang)); sh = int(img.height * c)
        if sh < 2: continue
        im = img.resize((img.width, sh), Image.BILINEAR)
        im = E.fade(im, clamp(c ** 1.5)) if c < .999 else im
        y = (h + 40) / 2 - R * math.sin(math.radians(ang)) - sh / 2
        out.alpha_composite(im, (int((w - img.width) / 2), int(y))) if y >= 0 and y + sh <= out.height else K.paste(out, im, (w - img.width) / 2, y)
    return out


def date_imgs():
    a = K.text_rgba('TODAY', 72, 700, (206, 204, 220), tracking=9)
    b = K.text_rgba('TOMORROW', 72, 800, tracking=9, grad=E.GRAD_LIGHT)
    return a, b


def time_imgs():
    a = K.text_rgba('11:59', 158, 300, WHITE); b = K.text_rgba('8:00', 158, 300, WHITE)
    pa = K.text_rgba('PM', 52, 600, (226, 224, 236)); pb = K.text_rgba('AM', 52, 600, (226, 224, 236))
    return a, b, pa, pb


def lock_img(t):
    im = lock_base().copy()
    mg = K.smooth((t - ROLL0) / .30)            # TOMORROW: morning light blooms in the glass from the top edge
    if mg > .01:
        gw = K.radial(LW + 200, (168, 150, 255), 2.2, 1.0, sy=.62)
        K.paste(im, gw, LW / 2 - gw.width / 2, -gw.height * .45, alpha=.42 * mg + .25 * K.kick(t - ROLL0, .12))
        im = K.round_img(im, LR)
    # date
    a, b = date_imgs(); k = K.cub((t - ROLL0) / .14)
    dr = roll_word(a, b, k, 80); im.alpha_composite(dr, (LW // 2 - dr.width // 2, 124 - dr.height // 2))
    # time
    ta, tb, pa, pb = time_imgs()
    k2 = K.cub((t - ROLL0 - .03) / .16)
    tr = roll_word(ta, tb, k2, 132)
    k3 = K.cub((t - ROLL0 - .06) / .16)
    pr = roll_word(pa, pb, k3, 52)
    tw_ = lerp(ta.width, tb.width, k2); total = tw_ + 18 + pr.width
    x0 = LW / 2 - total / 2
    im.alpha_composite(tr, (int(x0 + tw_ / 2 - tr.width / 2), 262 - tr.height // 2))
    im.alpha_composite(pr, (int(x0 + tw_ + 18), 296 - pr.height // 2))
    # notification banner
    if t >= NOTE0:
        k = K.expo((t - NOTE0) / .22)
        npnl = note_panel()
        y = NOTE_Y - 40 * (1 - k)
        K.paste(im, npnl, (LW - NW) // 2, y, alpha=clamp((t - NOTE0) / .06))
    if ROLL0 + .02 <= t < ROLL0 + .62:      # morning light sweeps the glass
        im = sheen_soft(im, (t - ROLL0 - .02) / .60)
    return im


def sheen_soft(img, k):
    w, h = img.size
    yy, xx = np.mgrid[0:h:2, 0:w:2].astype(np.float32)
    u = (xx / w + yy / h * .5) / 1.5; c = lerp(-.25, 1.25, k)
    band = np.exp(-((u - c) / .10) ** 2) * .16
    bm = Image.fromarray((np.clip(band, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    a = np.asarray(img, np.float32); bb = np.asarray(bm, np.float32)[..., None] / 255.
    rgb = a[..., :3] + (255 - a[..., :3]) * bb
    al = np.maximum(a[..., 3:], bb * 255 * .0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8), 'RGBA')


LCX, LCY = 540, 1376


def lock_state(t):
    """(cx, cy, s, rx, alpha) of the lock card in screen space."""
    k = K.expo((t - CARD0) / .22)
    cy = LCY + 330 * (1 - k)
    rx = 22 * (1 - k)
    s = lerp(.92, 1.0, k)
    if t > CARD0 + .22: cy += -3 * math.sin((t - CARD0 - .22) * 2.2)
    if t > EXIT0:                               # dismissed: drops out of frame, tipping back (never across his face)
        u = (t - EXIT0) / (END - EXIT0); cy += 980 * u ** 2.1; rx += 26 * u ** 1.5; s *= 1 - .05 * u
    return LCX, cy, s, rx, clamp((t - CARD0) / .08)


def slot_screen(t):
    cx, cy, s, rx, a = lock_state(t)
    x, y, w, h = THUMB
    return cx + (x + w / 2 - LW / 2) * s, cy + (y + h / 2 - LH / 2) * s


# ---------------------------------------------------------------- camera
def camera(t):
    lt = t - START
    z = 1.10 + .07 * K.smooth(lt / (END - START)) + .030 * K.kick(t - W_REM + .01, .13) + .010 * K.kick(t - W_BRAND + .01, .10)
    lean = 14 * K.smooth((t - W_REM + .01) / .35) * (1 - K.smooth((t - FLY0) / .4))      # drifts toward the remembered post
    return dict(z=z, x=540., y=840., dx=lean, dy=-50. - .6 * lean, rot=0.)


def world_to_screen(cam, x, y):
    z = cam['z']; X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return X + (x - cam['x']) * z, Y + (y - cam['y']) * z


def night(t):
    return .26 * K.smooth((t - FOG0) / .5) * (1 - .62 * K.smooth((t - ROLL0) / .35))


# ---------------------------------------------------------------- draw
def ring_head(k, w, h):
    """point on the border ring (sprite coords) where the clockwise draw-on currently is."""
    a = math.atan2(-h / 2, -w / 2) + k * 2 * math.pi
    hw, hh = TW / 2 + 3, TH / 2 + 3
    dx, dy = math.cos(a), math.sin(a); r = min(hw / max(1e-6, abs(dx)), hh / max(1e-6, abs(dy)))
    return w / 2 + dx * r, h / 2 + dy * r


def glow_alpha(t):
    g = 0.
    if t >= W_BRAND - .01: g = .50 * K.cub((t - W_BRAND + .01) / .3) + .40 * K.kick(t - W_BRAND + .01, .16)
    if t >= W_REM - .01: g += .30 * K.smooth((t - W_REM + .01) / .2) + .45 * K.kick(t - W_REM + .01, .15)
    return g


def flight_pos(t, cam):
    """screen centre + scale of the remembered post on its way into the notification (quadratic arc right of his face)."""
    u = clamp((t - FLY0) / (FLY1 - FLY0))
    e = u * u * (3 - 2 * u) * .35 + K.eio(u) * .65           # softer peak speed than a pure cubic: stays legible
    h0 = hero_state(FLY0)
    sx0, sy0 = world_to_screen(cam, h0[0], h0[1]); s0 = cam['z'] * h0[2]
    sx1, sy1 = slot_screen(t)
    cxp, cyp = max(sx0, sx1) + 150, (sy0 + sy1) / 2 - 60
    bx = (1 - e) ** 2 * sx0 + 2 * (1 - e) * e * cxp + e ** 2 * sx1
    by = (1 - e) ** 2 * sy0 + 2 * (1 - e) * e * cyp + e ** 2 * sy1
    es = 1 - (1 - clamp(u * 1.15)) ** 2.2                     # shrinks early, so it never covers his face
    sc = lerp(s0, (THUMB[2] / TW) * lock_state(t)[2], es)
    return bx, by, sc, u, e


def draw(ctx, lt, t):
    ctx.captions = False
    cam = camera(t); ctx.cam = cam
    nt = night(t)
    ctx.bg_dim = .08 + nt
    ctx.bg_blur = 1.6
    ctx.avatar['bright'] = 1 - .30 * nt
    ctx.post['vignette'] = .36 + .4 * nt + .10 * spot(t) * (1 - K.smooth((t - FOG0) / .4))
    # wall + fog (behind him)
    wl = wall_layer(t, cam['z'])
    if wl: ctx.add('behind', wl[0], wl[1], wl[2], center=False)
    sp_ = spot(t)                              # spotlight: the rest of the wall drops a stop on BRAND
    if sp_ > .01: ctx.add('behind', Image.new('RGBA', (W, H), (5, 4, 12, int(255 * .46 * sp_))), 0, 0, center=False)
    fd = fog_density(t)
    fg = fog_layer(t, fd)
    if fg is not None: ctx.add('behind', fg, 0, 0, center=False)
    ff = fog_front(t, fd * (1 - .7 * K.smooth((t - CARD0) / .2)))
    if ff is not None: ctx.add('front', ff[0], 0, ff[1], center=False)
    # the remembered post
    flying = t >= FLY0
    hx, hy, hs = hero_state(t)
    glow_a = glow_alpha(t)
    if not flying:
        swell = 1 + .35 * K.smooth((t - W_REM + .01) / .25)
        g = K.radial(640, (118, 88, 255), 1.6, 1.0, sy=1.3)
        if hs * swell != 1: g = g.resize((int(g.width * hs * swell), int(g.height * hs * swell)), Image.BILINEAR)
        ctx.add('behind', g, hx, hy, alpha=clamp(glow_a))
        if t >= W_REM - .01:                  # REMEMBER: the brand leaves an after-image — two border echoes ripple out
            for dl in (0, .10):
                qq = (t - W_REM + .01 - dl) / .42
                if 0 < qq < 1:
                    rg = border_ring(); se = hs * (1 + .42 * K.cub(qq))
                    ctx.add('behind', rg.resize((int(rg.width * se), int(rg.height * se)), Image.BILINEAR), hx, hy, alpha=.85 * (1 - qq) ** 1.5)
        sp = hero_sprite(t)
        if hs != 1: sp = sp.resize((int(sp.width * hs), int(sp.height * hs)), Image.BILINEAR)
        if abs(scroll_vel(t)) > 120:
            sp, ox, oy = K.smear(sp, 0, min(90, abs(scroll_vel(t)) / 30 * .9))
        ctx.add('behind', sp, hx, hy)
        kb = (t - W_BRAND + .01) / .26           # BRAND: a star glint rides the head of the border as it draws on
        if 0 <= kb < 1.15:
            rw, rh = border_ring().size; px, py = ring_head(min(kb, 1), rw, rh)
            st = K.star(54, 4)
            ctx.add('behind', st, hx + (px - rw / 2) * hs, hy + (py - rh / 2) * hs, alpha=min(1, 1.6 * K.bump(kb, -.05, 1.15)))
    # lock screen card (screen space, frosted)
    if t >= CARD0:
        cx, cy, s, rx, a = lock_state(t)
        art = lock_img(t)
        q = K.quad(LW, LH, cx, cy, s, rx, 0, 0, 2200.)
        r = K.warp(art, q, margin=40)
        if r:
            im, x0, y0 = r
            if t > EXIT0:
                v = lock_state(t)[1] - lock_state(t - 1 / 60)[1]
                if v > 2: im, ox, oy = K.smear_hq(im, 0, v * .9); x0 += ox; y0 += oy
            ctx.add('screen', _shadow_card(), cx, cy + 18, alpha=a * .9)
            ctx.add('screen', im, x0, y0, center=False, glass=14, alpha=a)
    # the flight into the notification
    if flying:
        bx, by, sc, u, e = flight_pos(t, cam)
        if u >= 1:
            img = thumb_img(t)
            pk = 1 + .12 * K.kick(t - FLY1, .08)
            img = img.resize((int(img.width * pk), int(img.height * pk)), Image.BILINEAR)
            if t > EXIT0:
                v = slot_screen(t)[1] - slot_screen(t - 1 / 60)[1]
                if v > 2: img, ox, oy = K.smear(img, 0, v * .9)
            ctx.add('screen', img, bx, by)
            if t - FLY1 < .3:
                ctx.add('screen', K.radial(180, (190, 170, 255), 1.4, 1.0), bx, by, alpha=.9 * K.kick(t - FLY1, .07))
                st = K.star(70, 4); ctx.add('screen', st, bx + 40, by - 52, alpha=K.bump(t - FLY1, 0, .3))
        else:
            # the post sheds its chrome on the way: the media stays solid, header/footer/border fade around it
            mix = K.smooth((u - .12) / .55)
            tile = hero_sprite(t)
            w2, h2 = max(2, int(tile.width * sc)), max(2, int(tile.height * sc))
            sp = Image.new('RGBA', (w2, h2), (0, 0, 0, 0))
            gl_ = K.radial(320, (118, 88, 255), 1.6, 1.0, sy=1.3)
            if mix < .99: sp.alpha_composite(E.fade(tile.resize((w2, h2), Image.BILINEAR), 1 - mix))
            med = thumb_img(t, max(8, int(TW * sc)))
            hr = halo_ring(med.width, med.height)                  # the brand halo travels with it (dark media on dark room)
            K.paste(sp, hr, 18 * sc + med.width / 2 - hr.width / 2, (18 + HEAD) * sc + med.height / 2 - hr.height / 2, alpha=min(1, 1.4 * mix))
            K.paste(sp, med, 18 * sc, (18 + HEAD) * sc)
            sp = sp.rotate(-9 * math.sin(math.pi * e), Image.BICUBIC, expand=True)
            px, py = flight_pos(t - 1 / 120, cam)[:2]           # ~90° shutter: legible, still motion-blurred
            sp, ox, oy = K.smear_hq(sp, (bx - px) * 2 * .5, (by - py) * 2 * .5)
            ctx.add('screen', gl_.resize((int(gl_.width * sc), int(gl_.height * sc)), Image.BILINEAR), bx, by, alpha=.55 * (1 - mix) + .35 * mix)
            qx, qy = flight_pos(max(FLY0, t - .07), cam)[:2]       # light trail along the arc
            L = math.hypot(bx - qx, by - qy)
            if L > 20:
                tr = K.radial(128, (150, 120, 255), 1.8, 1.0).resize((int(L + 120 * sc), max(70, int(170 * sc))), Image.BILINEAR)
                tr = tr.rotate(-math.degrees(math.atan2(by - qy, bx - qx)), Image.BILINEAR, expand=True)
                ctx.add('screen', tr, (bx + qx) / 2, (by + qy) / 2, alpha=.62 * math.sin(math.pi * u))
            ctx.add('screen', sp, bx, by)
    K.caps_to_layers(ctx, t, PAGES, CAP_Y)


def _shadow_card():
    def mk():
        pad = 90; w, h = LW + 2 * pad, LH + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + LW, pad + LH), LR, fill=255)
        sh = m.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * .55))
        out = Image.new('RGBA', (w, h), (2, 2, 8, 0)); out.putalpha(sh); return out
    return K.C('s08shadowcard', mk)


def halo_ring(w, h):
    """brand-gradient rounded outline + glow hugging a w x h media rectangle (RGBA, padded by 14)."""
    def mk():
        p, ss = 14, 2; W2, H2 = w + 2 * p, h + 2 * p
        m = Image.new('L', (W2 * ss, H2 * ss)); ImageDraw.Draw(m).rounded_rectangle(((p - 4) * ss, (p - 4) * ss, (W2 - p + 3) * ss, (H2 - p + 3) * ss), 19 * ss, outline=255, width=4 * ss)
        m = m.resize((W2, H2), Image.LANCZOS)
        g = E.gradient(W2, H2, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
        gl = Image.new('RGBA', (W2, H2), (140, 110, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(6)))
        out = Image.new('RGBA', (W2, H2)); out.alpha_composite(gl); out.alpha_composite(gl); out.alpha_composite(g); return out
    return K.C(('s08halo', w, h), mk)


def thumb_img(t, w=None):
    """the remembered post's media as the notification thumbnail (rounded 4:5; default THUMB size)."""
    w = w or THUMB[2]; h = int(round(w * 1.25))
    m = hero_media(t, (w, h)).convert('RGBA')
    m = K.round_img(m, 16)
    b = Image.new('L', m.size); ImageDraw.Draw(b).rounded_rectangle((0, 0, m.width - 1, m.height - 1), 16, outline=255, width=2)
    e = Image.new('RGBA', m.size, (200, 186, 255, 0)); e.putalpha(b.point(lambda v: int(v * .8))); m.alpha_composite(e)
    return m
