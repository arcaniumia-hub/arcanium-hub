"""s03 — ONE SWIPE (5.32–7.80).  "One swipe..." / "and it's gone." / (silence: knock, knock)

5.32  Hard cut to the viewer's own feed (screen settles from 104 % — the framing change that hides the jump cut), his
      Reel post centred, him talking inside it ("One...").
5.45  A real touch lands on the glass (soft translucent fingertip disc + contact ripple), drags the feed up 46 px…
5.63  SWIPE — the finger flicks up and lifts off (motion-smeared); the feed is thrown: his post exits the top and a
      stream of eight forgettable posts whizzes past with true per-row motion blur (90-degree box shutter along the
      scroll, capped so every post still reads as a post), decelerating (friction) to rest on random posts EXACTLY on
      6.65 "GONE." He is off-screen: voice only. Engine captions start only once s02's "FLAT." page is over.
7.08  Dead silence. The feed sits perfectly still.
7.24  KNOCK — from inside: the whole phone jolts (scale pop + shake), the glass flexes (local bulge) and a small
      impact star cracks the screen (screen space, over all UI: dark fissures + specular glints + refraction + crushed
      white impact point + sparkles).
7.27  …the feed starts to creep DOWN by itself in two tugs — he is pulling his post back from inside.
7.50  KNOCK — bigger crack, first concentric rings. 7.53 the feed is yanked down (3-frame rewind smear; the cracks stay
      put on the glass) and his Reel post slams back into place at 7.64 (jolt + elastic settle): for two frames it sits
      in the feed with its lumarc_studio header (his post is back), then opens to fill the screen (7.71–7.85, mask
      reveal with the same camera anchor as the post's media, so nothing jumps) — close to the glass.
The glass state (cracks, Reel) continues seamlessly in s04 (one continuous take 7.08 → 11.96).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import feedkit as FK
from sections import _glasskit as GK

START, END = E.span(6, 8)                       # 5.32 – 7.80
W, H = E.W, E.H
clamp, eout, ein = E.clamp, E.eout, E.ein

# word onsets measured on src/tight16k.raw (10 ms RMS + >3.5 kHz band energy for the fricatives)
WORD_FIX = {(6, 'ONE'): 5.42, (6, 'SWIPE...'): 5.63, (7, 'AND'): 6.32, (7, "IT'S"): 6.42, (7, 'GONE.'): 6.65}
W_SWIPE, W_GONE = 5.63, 6.65
W_NOT, W_MINE = 7.90, 8.09
TOUCH = 5.45                                    # finger lands
K1, K2 = 7.24, 7.50                             # knocks (dead-silence beat 7.08–7.80)
CREEP = (7.27, 7.37)                            # two tugs after the first knock
YANK, LAND = 7.53, 7.64                         # the feed is yanked back down to his Reel (3 smear frames)
OPEN0, OPEN1 = 7.71, 7.85                       # ...it sits in the feed (header visible) for 2 frames, then opens to fill the screen

S0 = FK.center_scroll(FK.SPECIAL)               # 3745: his Reel centred
DRAG = 46.0
S_R = FK.center_scroll(10) - 230.0              # rest on random posts after the throw
CREEP_PX = (240.0, 330.0)
Y_M0 = FK.media_rect(FK.SPECIAL, S0)[1]          # 305: his media top when centred
Z_IN = 1.0                                      # camera inside the Reel once it fills the screen
BGZ0 = 1.07                                     # studio pre-zoom (leaves room for the parallax dolly after the break)
VP = (588.0, 1230.0)                            # camera anchor / vanishing point of the glass act (= the impact: we fly through the hole)

IMPACT = (588.0, 1230.0)                        # his upper chest once the Reel fills the screen
FR = GK.Fracture(center=IMPACT, seed=7, radials=16, ring_p=(1.05, .12, .05, .95),      # dense web near the impact,
                 hits=[(K1, 34, 105, .45, .05), (K2, 150, 360, .8, .08)], race=(W_NOT, 14000), web=(W_MINE, .14))  # sparse far out

CUES = [
    (TOUCH, 'click', {'gain': -3}),                         # fingertip on glass
    (W_SWIPE, 'flick', {'gain': 2}),                        # SWIPE
    (W_SWIPE + .07, 'whoosh', {'gain': 0}),                 # the feed stream
    (W_GONE, 'tick', {'gain': 3}),                          # stops dead on GONE
    (K1, 'knock', {'seed': 1}),
    (K1 + .004, 'crack', {'dur': .22, 'seed': 3, 'gain': -5}),
    (CREEP[0], 'swipe', {'gain': -15}),                     # the feed creeps down by itself (dragged from inside)
    (CREEP[1], 'swipe', {'gain': -13}),
    (K2, 'knock', {'seed': 2, 'gain': 2}),
    (K2 + .004, 'crack', {'dur': .34, 'seed': 5, 'gain': -2}),
    (YANK + .01, 'rewind', {'dur': .14, 'gain': 2}),        # pulled back from inside
    (LAND, 'thud', {'gain': -3}),                           # his Reel slams into place
]


def _page_a(seg_i, first=None):
    """start time of the engine caption page of segment seg_i (optionally the one starting with word `first`)."""
    for p in E.PAGES:
        if p['seg'] == seg_i and (first is None or p['words'][0]['text'].strip('.,!?"') == first): return p['a']
    return None


CAP_ON = max([START, (_page_a(6) or START) - .001] + [p['z'] for p in E.PAGES if p['seg'] < 6])
# engine captions only once s02's last page ("FLAT.") is over and the "ONE SWIPE..." page is up (never both stacked)


def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def C(k, fn): return E.cached(('s03',) + (k if isinstance(k, tuple) else (k,)), fn)


# ================================================================ scroll (pure function of t)
def _tug(t, t0, d): return smooth((t - t0) / d)


def scroll_at(t):
    if t < TOUCH + .03: return S0
    if t < W_SWIPE: return S0 + DRAG * smooth((t - TOUCH - .03) / (W_SWIPE - TOUCH - .03))
    Sd = S0 + DRAG
    if t < W_GONE:
        u = (t - W_SWIPE) / (W_GONE - W_SWIPE); return Sd + (S_R - Sd) * (1 - (1 - u) ** 2.3)     # steady friction: still moving 2 frames before GONE
    s = S_R
    s -= CREEP_PX[0] * _tug(t, CREEP[0], .10) + CREEP_PX[1] * _tug(t, CREEP[1], .11)
    if t >= YANK:
        sc = S_R - sum(CREEP_PX); tgt = S0 - 40                  # slams 40 px past centre, then springs back
        u = clamp((t - YANK) / (LAND - YANK))
        p = .5 * (2 * u) ** 2 if u < .5 else 1 - .5 * (2 * (1 - u)) ** 2.2
        s = sc + (tgt - sc) * p
        if t > LAND: s += 40 * E.eout(clamp((t - LAND) / .14))
    return s


def scroll_vel(t, dt=1 / 240):
    return (scroll_at(t + dt) - scroll_at(t - dt)) / (2 * dt)


# ================================================================ feed with true motion blur
def _content_strip(top, height, special):
    """content rows from screen-y `top` (may be < 0) for `height` rows, no chrome. RGB uint8 array."""
    out = np.zeros((height, W, 3), np.uint8); y = 0
    while y < height:
        sy = top + y                                     # screen y of this tile's first row
        tile = FK.screen(scroll_now[0] + sy, special=special, chrome=False).convert('RGB')
        h = min(H, height - y); out[y:y + h] = np.asarray(tile)[:h]; y += h
    return out


scroll_now = [0.0]


def blur_len(t, v):
    """motion-blur length (px) of the scrolling feed: 90-degree shutter capped at 340 px for the throw, so the posts
    whizzing past still read as posts; the yank back (YANK..LAND, ~3 posts per frame) is capped at 420 px too: a
    strobing rewind of real posts (photos, headers, captions streaking down), never a grey mush."""
    if YANK <= t <= LAND + .02: return int(min(420, abs(v) * .5 / E.FPS))
    return int(min(340, abs(v) * .25 / E.FPS))


def feed_screen(ctx, t, scroll=None, vel=None, special=None, chrome=True):
    """the phone screen (RGBA) at time t: feed at scroll with vertical motion blur (shutter 180°)."""
    s = scroll_at(t) if scroll is None else scroll
    v = scroll_vel(t) if vel is None else vel
    L = blur_len(t, v)
    # his Reel media, only when it is (partly) on screen
    my = FK.media_rect(FK.SPECIAL, s)[1]
    if special is None and my < H + L and my + FK.MEDIA_H > -L:
        special = reel_media(ctx, t)
    scroll_now[0] = s
    if L < 2:
        im = FK.screen(s, special=special, chrome=False).convert('RGB')
    else:
        pad = L // 2 + 1
        strip = _content_strip(-pad, H + 2 * pad, special).astype(np.float32)
        cs = np.cumsum(strip, 0); cs = np.concatenate([np.zeros((1, W, 3), np.float32), cs], 0)
        a = (cs[L:L + H + 2 * pad - L + 1] - cs[:H + 2 * pad - L + 1]) / L
        o = pad - L // 2
        im = Image.fromarray(np.clip(a[o:o + H], 0, 255).astype(np.uint8))
    im = im.convert('RGBA')
    if chrome:
        im.alpha_composite(FK.chrome_top(), (0, 0)); im.alpha_composite(FK.chrome_nav(), (0, FK.NAV_Y))
    return im


def reel_media(ctx, t):
    """his live studio world as the Reel's 4:5 media (slow push while he talks)."""
    z = 1.0 + .035 * smooth((t - START) / 1.0)
    fr = ctx.compose(cam=dict(z=z, x=540., y=900., dx=0., dy=0., rot=0.))
    return fr.convert('RGB').crop((0, 300, W, 300 + FK.MEDIA_H))


# ================================================================ his Reel opening to fill the screen
def inside_world(ctx, t, z=None):
    """the world as seen inside the full-screen Reel (camera Z_IN anchored at VP), RGB."""
    z = Z_IN if z is None else z
    return ctx.compose(cam=dict(z=z, x=VP[0], y=VP[1], dx=0., dy=0., rot=0.)).convert('RGB')


def screen_look(img, k=1.0):
    """content seen THROUGH a phone screen: a touch flatter (lifted blacks, softer contrast, less saturation)."""
    if k <= 0: return img
    a = np.asarray(img, np.float32)
    g = a.mean(2, keepdims=True); a = g + (a - g) * (1 - .12 * k)
    a = a * (1 - .08 * k) + 9 * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def open_k(t): return E.eout(clamp((t - OPEN0) / (OPEN1 - OPEN0))) if t > OPEN0 else 0.0


def reel_screen(ctx, t):
    """t >= YANK: feed (still settling) with his Reel expanding to fill the screen; chrome on top. RGBA."""
    k = open_k(t)
    s = scroll_at(t)
    if k >= .999:
        im = screen_look(inside_world(ctx, t)).convert('RGBA')
    else:
        base = feed_screen(ctx, t, scroll=s, chrome=False)
        if k > 0:
            y_m = FK.media_rect(FK.SPECIAL, s)[1]
            top = y_m * (1 - k); bot = (y_m + FK.MEDIA_H) * (1 - k) + H * k
            off = (y_m - 300) * (1 - k)
            z = lerp(1.035, Z_IN, k)
            wd = screen_look(ctx.compose(cam=dict(z=z, x=540., y=900., dx=0., dy=0., rot=0.)).convert('RGB'), k)
            r0, r1 = int(round(top)), int(round(bot))
            r0c, r1c = max(0, r0), min(H, r1)
            if r1c > r0c:
                w0 = int(round(r0c - off)); w1 = w0 + (r1c - r0c)
                w0c, w1c = max(0, w0), min(H, w1)
                piece = wd.crop((0, w0c, W, w1c))
                base.paste(piece, (0, r0c + (w0c - w0)))
        im = base
    im.alpha_composite(FK.chrome_top(), (0, 0)); im.alpha_composite(FK.chrome_nav(), (0, FK.NAV_Y))
    return im


# ================================================================ touch indicator
def touch_sprite(r=46):
    def mk():
        S = 4; R = r + 18; im = Image.new('RGBA', (2 * R * S, 2 * R * S), (0, 0, 0, 0))
        yy, xx = np.mgrid[0:2 * R * S, 0:2 * R * S].astype(np.float32) / S - R
        d = np.hypot(xx, yy)
        disc = np.clip((r - d) / 2.2, 0, 1)                                  # soft-edged fingertip contact
        body = disc * (.30 + .10 * np.clip(1 - d / r, 0, 1))
        rim = np.exp(-((d - r + 3) / 2.4) ** 2) * .32
        shadow = np.exp(-((d - r - 4) / 7) ** 2) * .16 * (d > r - 2)
        a = np.clip(body + rim, 0, 1)
        rgb = np.zeros(d.shape + (3,), np.float32) + np.array([238, 238, 244], np.float32)
        al = np.clip(a + shadow, 0, 1); rgb = np.where((shadow > a)[..., None], np.array([10, 10, 14], np.float32), rgb)
        im = Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), 'RGBA')
        return im.resize((2 * R, 2 * R), Image.LANCZOS)
    return C(('touch', r), mk)


TOUCH_XY = (742.0, 1232.0)


def touch_layer(fr, t):
    """paints the fingertip (land, drag, flick + lift-off with motion smear, contact ripple) onto fr (RGBA)."""
    if not (TOUCH - .01 < t < W_SWIPE + .12): return fr
    x, y = TOUCH_XY
    land = clamp((t - TOUCH) / .06)
    s = lerp(1.32, 1.0, eout(land)); a = .95 * land
    if t >= TOUCH + .03: y -= DRAG * smooth((t - TOUCH - .03) / (W_SWIPE - TOUCH - .03))
    trail = 0.0
    if t >= W_SWIPE:
        u = (t - W_SWIPE) / .075
        y -= 640 * clamp(u) ** 2; x -= 30 * clamp(u) ** 2
        trail = 640 * 2 * clamp(u) * (.5 / E.FPS) / .075
        a *= clamp(1 - (t - W_SWIPE - .035) / .05)
        s *= 1 - .12 * clamp(u)
    if a <= .01: return fr
    sp = touch_sprite()
    if abs(s - 1) > .01: sp = sp.resize((int(sp.width * s), int(sp.height * s)), Image.BILINEAR)
    if trail > 4:     # motion smear along the flick (premultiplied average of many shifted copies)
        pd = int(trail / 2) + 2
        sp = GK.smear(GK._pad(sp, pd), 0, trail, min(48, int(trail / 3) + 3))
        sp.putalpha(sp.getchannel('A').point(lambda v: min(255, int(v * 2.6))))
        yc = y + trail / 2
    else: yc = y
    E._paste(fr, dict(img=E.fade(sp, a), xy=(int(x - sp.width / 2), int(yc - sp.height / 2)), glass=0))
    # contact ripple
    rk = (t - TOUCH) / .30
    if 0 < rk < 1:
        R = int(46 + 52 * eout(rk)); ring = Image.new('RGBA', (2 * R + 6, 2 * R + 6), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((3, 3, 2 * R + 3, 2 * R + 3), outline=(240, 240, 248, int(120 * (1 - rk) ** 1.5)), width=3)
        E._paste(fr, dict(img=ring, xy=(int(TOUCH_XY[0] - R - 3), int(TOUCH_XY[1] - R - 3)), glass=0))
    return fr


# ================================================================ knocks: jolt, flex, flare
JOLT_TAB = [(0, 0), (0, 15), (-9, -8), (6, 5), (-3, -2), (1, 1)]
KNOCKS = [(K1, .8), (K2, 1.0), (W_NOT, 1.15)]


def jolt(t, knocks=KNOCKS):
    """screen shake (px) + scale pop for the knocks. Deterministic per frame index after each knock."""
    dx = dy = 0.0; z = 0.0
    for tk, amp in knocks:
        k = int(math.floor((t - tk) * E.FPS + 1e-4))
        if 0 <= k < len(JOLT_TAB):
            dx += JOLT_TAB[k][0] * amp; dy += JOLT_TAB[k][1] * amp
        if 0 <= t - tk < .25: z += .022 * amp * math.exp(-(t - tk) / .05)
    return dx, dy, z


def flex(t, knocks=KNOCKS):
    """glass bulge amount at the impact right after each knock."""
    b = 0.0
    for tk, amp in knocks:
        u = t - tk
        if 0 <= u < .2: b += .055 * amp * math.exp(-u / .04)
    return b


def bulge(img, c, amt, sigma=150):
    """magnify (glass flexing toward the lens) around c. img RGB."""
    if amt < .004: return img
    R = int(sigma * 2.2); x0, y0 = int(c[0] - R), int(c[1] - R)
    x0c, y0c, x1c, y1c = max(0, x0), max(0, y0), min(W, x0 + 2 * R), min(H, y0 + 2 * R)
    a = np.asarray(img)
    yy, xx = np.mgrid[y0c:y1c, x0c:x1c].astype(np.float32)
    dx, dy = xx - c[0], yy - c[1]; f = 1 - amt * np.exp(-(dx * dx + dy * dy) / (sigma * sigma))
    sx = np.clip(np.rint(c[0] + dx * f), 0, W - 1).astype(np.int32); sy = np.clip(np.rint(c[1] + dy * f), 0, H - 1).astype(np.int32)
    out = a.copy(); out[y0c:y1c, x0c:x1c] = a[sy, sx]
    return Image.fromarray(out)


def flare(t, knocks=KNOCKS):
    """impact light catch: (size, alpha) of a star glint at the impact."""
    best = (0, 0.0)
    for tk, amp in knocks:
        u = t - tk
        if 0 <= u < .12:
            a = math.exp(-u / .035) * min(1, amp)
            if a > best[1]: best = (int(150 + 120 * amp), a)
    return best


def glass_post(fr, t, z0=1.0, extra=(0, 0), knocks=KNOCKS, glint_base=1.0, leak=0.0, refr=None, sweep=None, leak_falloff=(.4, 650.0)):
    """fr (RGB/RGBA screen) -> cracks + flex + flare + jolt applied (RGBA)."""
    img = fr.convert('RGB')
    img = bulge(img, IMPACT, flex(t, knocks))
    g = glint_base
    for tk, amp in knocks:
        if t >= tk: g += 1.6 * amp * math.exp(-(t - tk) / .12)
    if refr is None: refr = 1.0
    if sweep is None: sweep = 300 + (t - K1) * 900
    img = FR.composite(img, t, refr=refr, leak=leak, glint=g, sweep=sweep, leak_falloff=leak_falloff).convert('RGBA')
    sz, a = flare(t, knocks)
    if a > .02:
        st = GK.star(64, 8); s_ = st.resize((sz, sz), Image.BILINEAR)
        E._paste(img, dict(img=E.fade(s_, a), xy=(int(IMPACT[0] - sz / 2), int(IMPACT[1] - sz / 2)), glass=0))
    dx, dy, z = jolt(t, knocks + [(LAND, .45)])
    dx += extra[0]; dy += extra[1]; z = z0 * (1 + z) * (1.012 if (abs(dx) + abs(dy)) > 0 else 1)
    if abs(z - 1) > 1e-4 or dx or dy:
        img = E.zoom(img.convert('RGB'), z, IMPACT, dx=dx, dy=dy).convert('RGBA')
    return img


# ================================================================ draw
def settle_zoom(t):
    """5.32 framing change: the screen settles from 104 % (hides the pose jump at the section cut)."""
    return 1 + .042 * (1 - E.eout(clamp((t - START) / .32)))


def draw(ctx, lt, t):
    ctx.captions = t >= CAP_ON                 # s02's 'FLAT.' page would otherwise spill over the cut
    ctx.bg_z = BGZ0
    P = ctx.post; P['vignette'] = .10; P['grain'] = .55
    if t < YANK:
        fr = feed_screen(ctx, t)
        fr = touch_layer(fr, t)
        if t < START + .34:
            fr = E.zoom(fr.convert('RGB'), settle_zoom(t), (540, 980)).convert('RGBA')
        if t >= K1:
            fr = glass_post(fr, t)
    else:
        fr = reel_screen(ctx, t)
        fr = glass_post(fr, t)
    ctx.full = fr
    # caption scrim while the feed streams under the words (keeps them legible over the blur)
    if W_SWIPE < t < W_GONE:
        k = clamp((t - W_SWIPE) / .1) * clamp((abs(scroll_vel(t)) - 2500) / 9000)
        ctx.add('screen', cap_scrim(), 540, ctx.cap_y + 6, alpha=.7 * k)


def cap_scrim():
    def mk():
        w, h = 1000, 300; m = Image.new('L', (w, h))
        ImageDraw.Draw(m).rounded_rectangle((170, 105, w - 170, h - 105), 46, fill=225)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); im.putalpha(m.filter(ImageFilter.GaussianBlur(40))); return im
    return C('scrim', mk)
