"""s07 — "The video you watch twice." (TL14, 15.40–17.48)

15.40  JUMP CUT -> tight multicam framing: founder on the right third (z 1.40, plate edge pinned at the frame edge), the
       studio falls out of focus. A Reel card swings in from the bottom-left in true perspective with motion blur — a
       powered-off glass screen: deep black glass mirroring the purple room, a specular streak sliding across as it turns.
15.667 "VIDEO" ('v' 15.645) -> it lands (settle spring) and the screen WAKES: the picture spreads out radially from the
       centre with a glowing edge + over-exposure; its live colour spills onto his left cheek/shoulder.
15.67–16.87  the Reel plays the end of the SILENCE ONE film (scaled into the video area above the Reels UI so its own
       "SILENCE ONE / $349" end card never collides with the author row); the progress bar runs to the end exactly on
       "TWICE." On "WATCH" the house lights go down and the screen lights him.
16.867 "TWICE." -> tape rewind INSIDE the card only (VHS tracking bands, head-switch noise, RGB split, scanlines,
       ghosting; the content scrubs back ~28x; the bar races back with a hot scrubber head; the screen light flickers on
       him). A glass replay glyph spins backwards in the card centre. Camera double-bump (twice).
17.167 tape stop -> the Reel restarts (40h burst), ring pulses, the replay glyph collapses into a gradient "×2" badge
       which glides up into a corner chip (the replay then plays clean); an outline echo of "TWICE." ripples out of the
       caption. Lip-sync is never touched.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _D_kit as K
from sections import feedkit as FK

START, END = E.span(14, 14)               # 15.40 – 17.48

# word onsets measured on src/tight16k.raw (10 ms RMS envelope + 3-band spectrogram; re-verified in review:
# 'the' voicing 15.51 | 'v' frication 15.645 (vowel 15.72) | 'you' 16.34 | 'w' glide 16.47-16.50 | 't' burst 16.87)
WORDS = {'THE': 15.51, 'VIDEO': 15.65, 'YOU': 16.34, 'WATCH': 16.48, 'TWICE.': 16.87}
W_THE, W_VIDEO, W_YOU, W_WATCH, W_TWICE = (WORDS[k] for k in ('THE', 'VIDEO', 'YOU', 'WATCH', 'TWICE.'))
PAGES = K.make_pages([[('THE', W_THE, False), ('VIDEO', W_VIDEO, False)],
                      [('YOU', W_YOU, False), ('WATCH', W_WATCH, False), ('TWICE.', W_TWICE, True)]], END - .02)
CAP_Y = 1440

clamp, lerp = E.clamp, K.lerp
W, H = E.W, E.H

# ---------------------------------------------------------------- timing
FLY0, LAND = START - .03, W_VIDEO + .01   # card swing-in, lands on VIDEO
RW0, RW1 = W_TWICE - .01, W_TWICE + .295  # rewind window (first rewind frame = the frame of the 't' burst; tape stop at RW1)
L0, L1 = 19.22, 27.45                     # the card's Reel = HYPER excerpt 19.12 .. 27.45 (8.33 s): loops there
LOOP = L1 - L0
SCRUB = (19.0, 27.6)
PLAY_A, PLAY_B = (25.90, 27.50), (19.15, 19.60)   # the two stretches that play at 1x (before / after the rewind)

CUES = [
    (START - .02, 'swipe', {'gain': -6, 'pan': -.3}),        # multicam snap + card swings in
    (FLY0 + .13, 'whoosh', {'gain': -10, 'pan': -.4}),       # the card's swing (peaks mid-flight)
    (LAND, 'glass', {'gain': -4, 'seed': 7, 'pan': -.35}),   # lands on VIDEO
    (LAND, 'thud', {'gain': -10}),
    (W_TWICE - .015, 'click', {'gain': -2, 'pan': -.35}),    # bar hits the end
    (W_TWICE, 'rewind', {'dur': .34, 'gain': 0, 'pan': -.3}),
    (W_TWICE, 'glitch', {'gain': -10, 'seed': 14, 'pan': -.3}),
    (RW1, 'thud', {'gain': -6}),                             # tape stop
    (RW1 + .01, 'pop', {'gain': -2}),                        # ×2 badge
    (RW1 + .03, 'shimmer', {'gain': -6}),
    (RW1 + .02, 'impact', {'gain': -12}),
]
CUES = [(round(t_, 3), k_, p_) for t_, k_, p_ in CUES]


# ---------------------------------------------------------------- source time of the card's Reel
def src_time(t):
    if t < RW0: return L1 - (RW0 - t)
    if t < RW1:
        u = (t - RW0) / (RW1 - RW0)
        return L1 - LOOP * K.eio(u)
    return L0 + (t - RW1)


def rewinding(t): return RW0 <= t < RW1 + .05


# ---------------------------------------------------------------- card geometry
CW, CH = 480, 854
CR = 34


def card_state(t):
    """(cx, cy, s, rx, ry, rz) of the Reel card in screen space."""
    x_, y_, s_, rx_, ry_, rz_ = 292., 770., 1.0, 2.5, -13., -1.5
    if t < LAND + .5:
        u = clamp((t - FLY0) / (LAND - FLY0))
        e = K.cub(u) * .55 + K.quint(u) * .45
        x0, y0, s0, rx0, ry0, rz0 = -120., 1380., .70, 14., 58., -14.
        cx, cy = lerp(x0, x_, e), lerp(y0, y_, e) - 90 * math.sin(math.pi * e) * (1 - e)
        s = lerp(s0, s_, e); rx = lerp(rx0, rx_, e); ry = lerp(ry0, ry_, e); rz = lerp(rz0, rz_, e)
        if t >= LAND:          # settle spring (overshoot in ry / scale)
            k = t - LAND
            ry += 5.0 * math.exp(-k * 9) * math.sin(k * 24)
            s *= 1 + .018 * math.exp(-k * 10) * math.sin(k * 26)
        return cx, cy, s, rx, ry, rz
    k = t - LAND
    cx, cy = x_ + 3 * math.sin(k * 1.3), y_ - 7 * math.sin(k * 1.7)
    ry = ry_ + 1.6 * math.sin(k * 1.1); rx = rx_ + .8 * math.sin(k * 1.5 + 1)
    s = s_ * (1 + .006 * k)
    # "twice": two small punches of the card on the rewind start and the tape stop
    s *= 1 + .028 * K.kick(t - RW0, .09) + .034 * K.kick(t - RW1, .10)
    return cx, cy, s, rx, ry, rz_


# ---------------------------------------------------------------- art
WHITE = (250, 249, 246)


def heart(sz, fill=True, col=(255, 56, 92)):
    def mk():
        n = sz * 4; m = Image.new('L', (n, n)); d = ImageDraw.Draw(m); pts = []
        for i in range(120):
            a = i / 120 * 2 * math.pi
            x = 16 * math.sin(a) ** 3; y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
            pts.append((n / 2 + x * n / 36, n / 2 + y * n / 36 - n * .02))
        if fill: d.polygon(pts, fill=255)
        else: d.line(pts + [pts[0]], fill=255, width=int(n * .075), joint='curve')
        m = m.resize((sz, sz), Image.LANCZOS)
        im = Image.new('RGBA', (sz, sz), col + (0,)); im.putalpha(m); return im
    return K.C(('s07heart', sz, fill, col), mk)


def reels_ui():
    """Reels chrome for the card (scrims, title, right rail, author row, caption). The progress bar is drawn live."""
    def mk():
        w, h = CW, CH
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        yy = np.arange(h, dtype=np.float32)[:, None]
        g = np.clip((yy - h * .66) / (h * .34), 0, 1) ** 1.5 * .80 + np.clip(1 - yy / (h * .13), 0, 1) ** 2 * .50
        im.putalpha(Image.fromarray((np.repeat(g, w, 1) * 255).astype(np.uint8)))
        d = ImageDraw.Draw(im)
        d.text((24, 26), 'Reels', font=E.font(30, 800), fill=WHITE)
        d.rounded_rectangle((w - 60, 28, w - 24, 56), 8, outline=WHITE, width=3); d.ellipse((w - 50, 34, w - 34, 50), outline=WHITE, width=3)
        rx = w - 42; y = int(h * .50); f = E.font(19, 700)
        def lab(s, yy_):
            l, tp, r, b = f.getbbox(s); d.text((rx - (r - l) / 2 - l, yy_), s, font=f, fill=WHITE)
        im.alpha_composite(heart(44, True), (rx - 22, y)); lab('48.3K', y + 48)
        y += 96; im.alpha_composite(FK.icon('comment', 42), (rx - 21, y)); lab('1,204', y + 46)
        y += 92; im.alpha_composite(FK.icon('share', 42), (rx - 21, y)); lab('3,981', y + 46)
        y += 90; im.alpha_composite(FK.icon('dots', 38), (rx - 19, y))
        by = h - 178
        av = E.gradient(50, 50, [(210, 180, 120), (150, 116, 70), (60, 48, 30)]).convert('RGBA'); m = Image.new('L', (50, 50))
        ImageDraw.Draw(m).ellipse((0, 0, 49, 49), fill=255); av.putalpha(m); im.alpha_composite(av, (20, by))
        f2 = E.font(25, 700); d.text((82, by + 10), 'silence.one', font=f2, fill=WHITE)
        x = 82 + int(f2.getlength('silence.one')) + 8; im.alpha_composite(FK.icon('verified', 24, (61, 133, 250)), (x, by + 13))
        x += 34; d.rounded_rectangle((x, by + 6, x + 88, by + 44), 10, outline=WHITE, width=2); d.text((x + 13, by + 11), 'Follow', font=E.font(20, 700), fill=WHITE)
        d.text((20, by + 66), 'Hear nothing. Feel everything.', font=E.font(22, 500), fill=(236, 236, 240))
        nx, ny = 22, by + 104                                   # music note glyph (Outfit has no ♪)
        d.ellipse((nx, ny + 12, nx + 9, ny + 19), fill=(205, 205, 215)); d.line((nx + 8, ny + 15, nx + 8, ny + 1), fill=(205, 205, 215), width=2)
        d.line((nx + 8, ny + 1, nx + 14, ny + 5), fill=(205, 205, 215), width=2)
        d.text((44, by + 100), 'Original audio · SILENCE ONE', font=E.font(19, 500), fill=(205, 205, 215))
        return im
    return K.C('s07reelsui', mk)


def rim():
    """glass rim + sheen over the card (RGBA CW x CH)."""
    def mk():
        w, h = CW, CH
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        u = xx / w * .8 + yy / h * .5
        sheen = np.clip(.10 - u * .14, 0, 1) + .05 * np.exp(-((u - .62) / .03) ** 2)
        sh = Image.new('RGBA', (w, h), (255, 255, 255, 0)); sh.putalpha(Image.fromarray((np.clip(sheen, 0, 1) * 255).astype(np.uint8)))
        im.alpha_composite(sh)
        ss = 3; m = Image.new('L', (w * ss, h * ss)); d = ImageDraw.Draw(m)
        d.rounded_rectangle((1, 1, w * ss - 2, h * ss - 2), CR * ss, outline=255, width=3 * ss)
        m = m.resize((w, h), Image.LANCZOS)
        edge = np.asarray(m, np.float32) / 255.
        lit = np.clip(1.0 - (xx / w * .5 + yy / h * .5), .25, 1)          # top-left edge catches the light
        a = Image.fromarray((edge * lit * 200).astype(np.uint8))
        e = Image.new('RGBA', (w, h), (235, 232, 255, 0)); e.putalpha(a); im.alpha_composite(e)
        return im
    return K.C('s07rim', mk)


def shadow_glow():
    def mk():
        pad = 120; w, h = CW + 2 * pad, CH + 2 * pad
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((pad, pad + 22, pad + CW, pad + CH + 22), CR, fill=255)
        sh = m.filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * .62))
        out = Image.new('RGBA', (w, h), (4, 3, 10, 0)); out.putalpha(sh)
        m2 = Image.new('L', (w, h)); ImageDraw.Draw(m2).rounded_rectangle((pad - 6, pad - 6, pad + CW + 6, pad + CH + 6), CR + 6, fill=255)
        gl = m2.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * .30))
        g = Image.new('RGBA', (w, h), (110, 86, 255, 0)); g.putalpha(gl)
        out.alpha_composite(g)
        return out, pad
    return K.C('s07shadow', mk)


def replay_glyph(sz=96, col=WHITE):
    """counter-clockwise circular arrow (replay), supersampled."""
    def mk():
        n = sz * 4; m = Image.new('L', (n, n)); d = ImageDraw.Draw(m)
        r = n * .33; c = n / 2; wd = int(n * .10)
        d.arc((c - r, c - r, c + r, c + r), 200, 500, fill=255, width=wd)
        a = math.radians(200); hx, hy = c + r * math.cos(a), c + r * math.sin(a)
        L = n * .16; tang = a - math.pi / 2           # arrow head pointing back (counter-clockwise)
        p1 = (hx + L * math.cos(tang), hy + L * math.sin(tang))
        p2 = (hx + L * .55 * math.cos(tang + 2.3), hy + L * .55 * math.sin(tang + 2.3))
        p3 = (hx + L * .55 * math.cos(tang - 2.3), hy + L * .55 * math.sin(tang - 2.3))
        d.polygon([p1, p2, p3], fill=255)
        m = m.resize((sz, sz), Image.LANCZOS)
        im = Image.new('RGBA', (sz, sz), col + (0,)); im.putalpha(m); return im
    return K.C(('replay', sz, col), mk)


def glyph_disc(d=176):
    def mk():
        im = Image.new('RGBA', (d, d), (0, 0, 0, 0)); m = Image.new('L', (d * 3, d * 3))
        ImageDraw.Draw(m).ellipse((0, 0, d * 3 - 1, d * 3 - 1), fill=255); m = m.resize((d, d), Image.LANCZOS)
        body = Image.new('RGBA', (d, d), (14, 12, 26, 0)); body.putalpha(m.point(lambda v: int(v * .58))); im.alpha_composite(body)
        r = Image.new('L', (d * 3, d * 3)); ImageDraw.Draw(r).ellipse((3, 3, d * 3 - 4, d * 3 - 4), outline=255, width=6); r = r.resize((d, d), Image.LANCZOS)
        rr = Image.new('RGBA', (d, d), (255, 255, 255, 0)); rr.putalpha(r.point(lambda v: int(v * .55))); im.alpha_composite(rr)
        return im
    return K.C(('disc', d), mk)


def x2_badge():
    """gradient pill with ×2 (Outfit 800)."""
    def mk():
        f = E.font(84, 800); s = '×2'; l, tp, r, b = f.getbbox(s)
        w, h = r - l + 64, 122
        m = Image.new('L', (w * 3, h * 3)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), h * 3 // 2, fill=255); m = m.resize((w, h), Image.LANCZOS)
        g = E.gradient(w, h, E.GRAD).convert('RGBA'); g.putalpha(m)
        d = ImageDraw.Draw(g); d.text(((w - (r - l)) / 2 - l, (h - (b - tp)) / 2 - tp - 2), s, font=f, fill=WHITE)
        hl = Image.new('L', (w, h)); ImageDraw.Draw(hl).rounded_rectangle((2, 2, w - 3, h - 3), h // 2, outline=255, width=2)
        hh = Image.new('RGBA', (w, h), (255, 255, 255, 0)); hh.putalpha(hl.point(lambda v: int(v * .45))); g.alpha_composite(hh)
        return E.shadow(g, 16, .55, (0, 8))
    return K.C('x2badge', mk)


def ring(r, a, col=(200, 186, 255), width=4):
    n = int(2 * r + 16); im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((8, 8, n - 8, n - 8), outline=col + (int(255 * clamp(a)),), width=width)
    return im


def osd_rew():
    def mk():
        im = Image.new('RGBA', (150, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for x0 in (8, 44):
            d.polygon([(x0 + 34, 10), (x0 + 34, 50), (x0, 30)], fill=(255, 255, 255, 255))
        g = im.filter(ImageFilter.GaussianBlur(3)); out = Image.new('RGBA', im.size, (0, 0, 0, 0))
        out.alpha_composite(g); out.alpha_composite(im); return out
    return K.C('osdrew', mk)


# ---------------------------------------------------------------- VHS rewind (content only)
_xs = np.arange(CW)[None, :]
_ys = np.arange(CH, dtype=np.float32)


def vhs(img, k, t):
    a = np.asarray(img, np.float32)
    fi = int(round(t * E.FPS)); rng = np.random.default_rng(1000 + fi)
    y = _ys
    dx = (np.sin(y * .045 + fi * 1.7) * 3 + np.sin(y * .011 + fi * .9) * 5) * k
    bands = []
    for j, (spd, hgt, amp) in enumerate(((2300, 40, 30), (1500, 18, 16))):
        yb = ((t * spd + j * 430) % (CH + 240)) - 120; bands.append(yb)
        dx = dx + np.exp(-((y - yb) / hgt) ** 2) * amp * k * (rng.random(CH) * .7 + .6)
    hs = np.clip((y - (CH - 34)) / 34, 0, 1)
    dx = dx + hs * 30 * k * (rng.random(CH) - .3)
    idx = np.clip((_xs - dx[:, None]).astype(np.int32), 0, CW - 1)
    out = np.take_along_axis(a, np.repeat(idx[..., None], 3, 2), 1)
    s = int(round(7 * k))
    if s:
        out[..., 0] = np.roll(out[..., 0], s, 1); out[..., 2] = np.roll(out[..., 2], -s, 1)
    nz = rng.normal(0, 1, (CH // 2, CW // 2)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    band = np.exp(-((y - bands[0]) / 10) ** 2)[:, None] + hs[:, None]
    out += (nz * 14 * k + (nz > 1.3) * 170 * band * k)[..., None]
    out[::3] *= 1 - .20 * k
    g = out.mean(2, keepdims=True); out = g + (out - g) * (1 - .28 * k)
    out = out * (1 - .06 * k) + 12 * k
    jy = int(round(6 * k * math.sin(fi * 2.1)))
    if jy: out = np.roll(out, jy, 0)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# the film sits in the video area ABOVE the Reels author row (its own end-card text "SILENCE ONE / specs / $349" must
# never collide with the UI): scaled .84, top-anchored, feathered into the card's black (the film is shot on black).
FW, FH = 404, 718
FX, FY = (CW - FW) // 2, 8


def film_mask():
    def mk():
        f = 26
        yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
        d = np.minimum.reduce([xx, FW - 1 - xx, yy + 40, FH - 1 - yy])      # top edge sits under the header scrim
        return Image.fromarray((np.clip(d / f, 0, 1) ** 1.5 * 255).astype(np.uint8))
    return K.C('s07filmmask', mk)


def place_film(fr):
    """film frame (any size) -> RGB CW x CH card content."""
    f = fr.resize((FW, FH), Image.BILINEAR) if fr.size != (FW, FH) else fr
    out = Image.new('RGB', (CW, CH), (5, 5, 7)); out.paste(f, (FX, FY), film_mask())
    return out


def content(t):
    """the card's video frame (RGB CW x CH) incl. rewind treatment."""
    st = src_time(t)
    if RW0 <= t < RW1:
        a = K.scrub_at(st, *SCRUB, size=(CW, CH))
        b = K.scrub_at(st + .45 * (1 - abs(2 * (t - RW0) / (RW1 - RW0) - 1)), *SCRUB, size=(CW, CH))   # ghost of the frames just passed
        im = place_film(Image.blend(a, b, .4))
        u = (t - RW0) / (RW1 - RW0)
        k = .55 + .45 * math.sin(math.pi * clamp(u * 1.15))
        return vhs(im, k, t)
    rng = PLAY_A if st >= PLAY_A[0] else PLAY_B
    im = place_film(K.fixed_at(E.HYPER, rng[0], rng[1], (CW, CH), st))
    if RW1 <= t < RW1 + .10:              # tape settles: tracking clears over 3 frames
        return vhs(im, .45 * (1 - (t - RW1) / .10), t)
    return im


def progress(t):
    return clamp((src_time(t) - L0) / LOOP)


ON0 = LAND - .025                          # screen wakes on VIDEO ('v' onset 15.645 -> first lit frame 15.667)


def power(t):
    """screen power: dark glass during the swing-in, switches ON exactly on VIDEO (with an over-exposed flash).
    returns (light output for the spill, ui alpha, radial reveal 0..1)."""
    if t < ON0: return .10, 0., 0.
    k = t - ON0
    return 1 + 1.1 * K.kick(k, .07), clamp(k / .08), clamp(k / .10)


def glass_refl():
    """what a dark glass screen mirrors: the purple room in front of it (mirrored plate, defocused, dimmed)."""
    def mk():
        p = E.studio().crop((0, 200, 1080, 1400)).transpose(Image.FLIP_LEFT_RIGHT)
        p = p.resize((816, 906), Image.BILINEAR).filter(ImageFilter.GaussianBlur(10))
        return np.asarray(K.grade(p, bright=.50, sat=1.1), np.float32)
    return K.C('s07refl', mk)


def _card_uv():
    def mk():
        yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
        u = (xx / CW * .8 + yy / CH * .5) / 1.3
        d = np.hypot(xx - CW / 2, (yy - CH * .45) * .92)
        return u, d
    return K.C('s07uv', mk)


def dark_glass(t):
    """the powered-off screen: deep black glass carrying a mirrored, defocused room + a specular streak that slides
    across as the card swings (parallax with its rotation) -> reads as real glass, not a black slab."""
    cx, cy, s, rx, ry, rz = card_state(t)
    R = glass_refl()
    ox = int(clamp((ry + 13) / 75) * 300) + 18; oy = int(clamp((rx - 2.5) / 12) * 40) + 6
    refl = R[oy:oy + CH, ox:ox + CW]
    u, _ = _card_uv()
    c = .30 + (ry + 13) / 95 - (cy - 770) / 2600
    streak = (np.exp(-((u - c) / .055) ** 2) * .26 + np.exp(-((u - c - .16) / .02) ** 2) * .10)[..., None]
    base = np.array([5, 5, 9], np.float32)
    a = base + refl * .62
    a = a + (255 - a) * streak
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def wake(c, g, k):
    """radial power-on: the picture spreads out from the centre over the dark glass, its edge glowing."""
    _, d = _card_uv()
    R = k * 1.12 * 560
    m = np.clip((R - d) / 70 + .5, 0, 1)[..., None]
    edge = np.exp(-((d - R) / 46) ** 2)[..., None] * (1 - k) * 150
    a = np.asarray(c, np.float32) * m + np.asarray(g, np.float32) * (1 - m) + edge * np.array([.86, .84, 1.0], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def card_img(t):
    pw, ui, kon = power(t)
    if kon <= 0:
        c = dark_glass(t)
    else:
        c = content(t)
        if abs(pw - 1) > .01: c = K.grade(c, bright=pw, lift=40 * max(0, pw - 1))
        if kon < 1: c = wake(c, dark_glass(t), kon)
    c = c.convert('RGBA')
    if ui > .01: c.alpha_composite(E.fade(reels_ui(), ui) if ui < 1 else reels_ui())
    if ui > .3: draw_bar(c, t)
    if RW0 <= t < RW1 + .02 and int((t - RW0) * 30) % 6 < 4:
        c.alpha_composite(osd_rew(), (22, 74))
    draw_replay(c, t)
    c = K.round_img(c, CR)
    c.alpha_composite(rim())
    return c


def draw_bar(c, t):
    d = ImageDraw.Draw(c)
    p = progress(t); by = CH - 30; bh = 8; bx0, bx1 = 22, CW - 22
    d.rounded_rectangle((bx0, by, bx1, by + bh), bh // 2, fill=(255, 255, 255, 64))
    px = int(bx0 + (bx1 - bx0) * p)
    if rewinding(t):
        if px - bx0 > 4:
            g = E.gradient(px - bx0, bh, E.GRAD_LIGHT).convert('RGBA'); g = K.round_img(g, bh // 2); c.alpha_composite(g, (bx0, by))
        hd = K.radial(110, (190, 170, 255), 1.3, 1.0); c.alpha_composite(hd, (px - 55, by + bh // 2 - 55))
    elif px - bx0 > 2:
        d.rounded_rectangle((bx0, by, px, by + bh), bh // 2, fill=(255, 255, 255, 240))
    d.ellipse((px - 11, by + bh // 2 - 11, px + 11, by + bh // 2 + 11), fill=(255, 255, 255, 255))
    if RW0 - .10 < t < RW0 + .06:   # end-of-bar flash
        fl = K.radial(150, (255, 255, 255), 1.2, clamp(1 - abs(t - RW0) / .10)); c.alpha_composite(fl, (bx1 - 75, by + bh // 2 - 75))


def draw_replay(c, t):
    """replay glyph (spins backwards with the tape) + ×2 badge at the loop restart."""
    if t >= RW0:
        k = t - RW0
        kk = max(0., t - RW1)
        disc = glyph_disc(212); cx, cy = CW // 2, int(CH * .40)
        sc = .55 + .45 * E.back(clamp(k / .16), 2.2)
        out_ = K.smooth((kk - .02) / .12)                                  # after the tape stop the glyph collapses
        a = clamp(k / .05) * (1 - out_)
        sc *= 1 - .65 * out_
        if a > .01:
            dd = disc.resize((int(disc.width * sc), int(disc.height * sc)), Image.BILINEAR)
            c.alpha_composite(E.fade(dd, a), (cx - dd.width // 2, cy - dd.height // 2))
            ang = 360 * K.eio(clamp(k / (RW1 - RW0 + .06))) * 1.5           # spins backwards with the tape
            gl = replay_glyph(132).rotate(ang, Image.BICUBIC)
            gl = gl.resize((int(gl.width * sc), int(gl.height * sc)), Image.BILINEAR)
            c.alpha_composite(E.fade(gl, a), (cx - gl.width // 2, cy - gl.height // 2))
        if t >= RW1:
            for j, dl in enumerate((0, .07)):
                q = (kk - dl) / .32
                if 0 < q < 1: rg = ring(106 + 110 * K.cub(q), (1 - q) * .9, width=4 if j else 6); c.alpha_composite(rg, (cx - rg.width // 2, cy - rg.height // 2))
            # ×2 pops ON the collapsing replay glyph, then glides up into a corner chip so the replay plays clean
            b = x2_badge()
            m = K.expo(clamp((kk - .13) / .16))
            bs = E.back(clamp(kk / .14), 2.6) * (1.0 - .46 * m)
            bx, by = lerp(cx, CW - 84, m), lerp(cy, 122, m) - 26 * math.sin(math.pi * m)
            if bs > .02:
                bb = b.resize((max(1, int(b.width * bs)), max(1, int(b.height * bs))), Image.BILINEAR)
                if 0 < m < .9: bb, ox, oy = K.smear(bb, (CW - 84 - cx) * .10 * (1 - m), (122 - cy) * .10 * (1 - m))
                K.paste(c, bb, bx - bb.width / 2, by - bb.height / 2, alpha=clamp(kk / .03))


# ---------------------------------------------------------------- light spill (card -> him + studio)
def spill_color(t):
    st = src_time(t)
    sm = K.scrub_at(st, *SCRUB, size=(CW, CH)).resize((8, 14), Image.BILINEAR)
    a = np.asarray(sm, np.float32).reshape(-1, 3)
    col = a.mean(0); lum = a.mean()
    return col, lum


def wrap_fn(t, q):
    def fn(fr):
        col, lum = spill_color(t)
        gain = (.55 + .007 * lum) * (1 + .45 * theater(t))
        if rewinding(t): gain *= .8 + .5 * K.hrand(int(t * 30), 3)
        gain *= power(t)[0] if t < LAND + .3 else 1
        c = tuple(int(min(255, 40 + v * 1.6)) for v in col)
        spr = K.radial(140, (255, 255, 255), 1.7, 1.0, sy=1.25)
        tint = Image.new('RGBA', spr.size, c + (0,)); tint.putalpha(spr.getchannel('A'))
        big = tint.resize((900, 1125), Image.BILINEAR)
        xs = [p[0] for p in q]; ys = [p[1] for p in q]
        ex = max(xs) - 40; ey = (min(ys) + max(ys)) / 2
        fr = fr.convert('RGB')
        K.add_light(fr, big, ex - 450, ey - 560, gain * .55)
        return fr
    return fn


# ---------------------------------------------------------------- draw
def camera(t):
    z = 1.40 + .05 * K.smooth((t - START) / (END - START))
    z *= 1 + .016 * K.kick(t - RW0, .10) + .020 * K.kick(t - RW1, .11)
    return dict(z=z, x=540., y=840., dx=900., dy=700. - 840. + 6 * math.sin((t - START) * 1.4), rot=0.)


def theater(t):
    return K.smooth((t - W_WATCH + .02) / .30)


def draw(ctx, lt, t):
    ctx.captions = False
    ctx.cam = camera(t)
    ctx.bg_blur = 3.5
    th = theater(t)                       # "you WATCH": the house lights go down, the screen lights him
    ctx.bg_dim = .06 + .36 * th
    ctx.avatar['bright'] = 1 - .10 * th
    ctx.post['vignette'] = .38 + .22 * th
    if t < FLY0: return
    cx, cy, s, rx, ry, rz = card_state(t)
    art = card_img(t)
    q = K.quad(CW, CH, cx, cy, s, rx, ry, rz, 2300.)
    # shadow + glow (projected with the same quad, padded)
    sg, pad = shadow_glow()
    qs = K.quad(sg.width, sg.height, cx, cy + 6, s, rx, ry, rz, 2300.)
    r = K.warp(sg, qs, margin=200)
    if r: ctx.add('screen', r[0], r[1], r[2], center=False, alpha=clamp((t - FLY0) / .12))
    r = K.warp(art, q, margin=200)
    if r is None: return
    im, x0, y0 = r
    if t < LAND + .04:   # motion blur along the swing
        p0 = card_state(t - 1 / 60.)
        dx, dy = (cx - p0[0]) * 1.1, (cy - p0[1]) * 1.1
        if math.hypot(dx, dy) > 2: im, ox, oy = K.smear_hq(im, dx, dy); x0 += ox; y0 += oy
    ctx.add('screen', im, x0, y0, center=False)
    ctx.wrap = wrap_fn(t, q)
    # "TWICE." echoes once on the tape stop: a gradient ghost of the word swells out of it and fades (said twice)
    if RW1 <= t < RW1 + .30:
        qq = (t - RW1) / .30; bx_ = CAPBOX['TWICE.']
        ge = echo_outline('TWICE.', bx_[4]); s_ = 1.03 + .42 * K.cub(qq)
        ge = ge.resize((int(ge.width * s_), int(ge.height * s_)), Image.BILINEAR)
        ctx.add('screen', ge, W / 2 + bx_[0], CAP_Y + bx_[1], alpha=.95 * (1 - qq) ** 1.3)
    K.caps_to_layers(ctx, t, PAGES, CAP_Y)


CAPBOX = K.caption_boxes(PAGES)


def echo_outline(text, size):
    """thin light-gradient outline of a caption word (same metrics/padding as engine word_img) — a ripple echo."""
    def mk():
        f = E.font(size); pad = int(size * .45); sw = max(3, size // 22)
        l, tp, r, b = f.getbbox(text, stroke_width=sw)
        w, h = r - l + 2 * pad, b - tp + 2 * pad
        fill = Image.new('L', (w, h)); ImageDraw.Draw(fill).text((pad - l, pad - tp), text, font=f, fill=255)
        ring_ = np.clip(np.asarray(fill.filter(ImageFilter.MaxFilter(7)), np.float32) - np.asarray(fill.filter(ImageFilter.MaxFilter(3)), np.float32), 0, 255)
        m = Image.fromarray(ring_.astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6))
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m)
        glow = Image.new('RGBA', (w, h), (130, 100, 255, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(5)))
        out = Image.new('RGBA', (w, h)); out.alpha_composite(glow); out.alpha_composite(g); return out
    return K.C(('s07echo', text, size), mk)
