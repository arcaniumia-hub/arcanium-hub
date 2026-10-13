"""s05 — IT STAYS IN YOUR HEAD (11.96–13.32).  "It stays in your head."

He is out of the screen, in his real studio. LUMARC-made work (SILENCE ONE films playing live, the North Roast carousel,
Maison Crumb post, Oliva website, the burger close-up, the headphone hero) orbits his head as frosted-glass cards on a
steeply tilted 3-D ring that ENCLOSES his head: the far arc rises behind his head (occluded by him — only the card tops
peek over his hair), the sides pass his ears, the near arc sweeps in front of his collar/chest (never over his mouth);
true perspective scale, carousel yaw, depth of field (near cards defocus, far cards soft, focus on his head),
depth-dimmed/cooled far cards, purple glow under every card, motion blur (soft 180-degree shutter). Captions (measured
onsets) sit at the top, in the headroom (s04 also ends with its words up there).

11.96  CUT to the WIDE angle (s04 ends on a 1.27x close-up: -21 % scale, his head drops 160 px -> the pose jump reads
       as a multicam cut); the cards rush in from the frame edges, spiralling, motion-blurred, while the camera creeps in.
12.17  "STAYS": the cards are captured into the orbit (12.19-12.24, each lands with a glow pulse; glass cue).
12.58  "IN YOUR": the orbit keeps turning; the slots are steered so the cards arrive exactly on their lock positions.
12.93  "HEAD." (lock on the 12.933 frame; /h/ 12.92, vowel 12.96): the ring stops hard with a tiny overshoot and the
       cards turn toward camera and snap into focus; a luminous orbit line ignites around his head (back half behind
       him, front half in front) while a sonar pulse races outward from the orbit; a light hit, a specular sheen + lit
       bezel rim travel around the cards (staggered), star glints; the camera SNAP-PUNCHES in (spring, 1.075 -> 1.25x,
       jolt + roll wobble). Slow drift to 13.32 (hard cut to s06's wide angle: another clear framing change).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _C_kit as K

START, END = E.span(12, 12)                   # 11.96 – 13.32
W, H = E.W, E.H
clamp, lerp, smooth, kick = E.clamp, K.lerp, K.smooth, K.kick

# word onsets measured on src/tight16k.raw (10 ms RMS envelope, >3.5 kHz band, spectrogram)
WORD_FIX = {(12, 'IT'): 12.07, (12, 'STAYS'): 12.17, (12, 'IN'): 12.58, (12, 'YOUR'): 12.68, (12, 'HEAD.'): 12.92}
T_IT, T_STAYS, T_IN, T_YOUR = 12.07, 12.17, 12.58, 12.68
T_HEAD = 12.925                               # lock lands on the frame of "HEAD." (12.93: /h/ 12.90, vowel 12.97)
PAGES = K.caption_pages(12, WORD_FIX)
CAP_Y = 330                                   # top: the orbit owns the frame; s04 ends with its words up here too

CUES = [
    (START + .06, 'whoosh', {'gain': -4}),                  # cards rush past the lens into orbit
    (START + .02, 'swoosh_up', {'gain': -12}),
    (T_STAYS + .02, 'glass', {'seed': 5, 'gain': -9}),      # captured into the orbit (cards land 12.19-12.24)
    (T_IN + .02, 'whoosh', {'gain': -15, 'pan': .3}),        # orbit sweeps around
    (T_HEAD, 'impact', {'gain': -4}),                       # LOCK
    (T_HEAD, 'shimmer', {'gain': -6}),
    (T_HEAD + .01, 'glass', {'seed': 2, 'gain': -10}),
    (T_HEAD + .03, 'click', {'gain': -8}),
]

# ---------------------------------------------------------------- orbit geometry (world px; head plane = depth 0)
# a HALO around his head (world px; his head: x≈518, top 625, eyes ≈780, chin ≈960): the far arc passes behind his
# forehead (hidden by his head, only the card tops peek over his hair), the near arc sweeps in front of his collar.
OCX, OCY = 520., 880.
R = 400.
ELEV = math.radians(50.); SE, CE = math.sin(ELEV), math.cos(ELEV)
ROLL = math.radians(-3.)
CARD_S = .48                                  # card art -> world px at the head plane
F = 1700.                                     # focal: the head plane is at distance F (scale 1)
N = 8
CARDS = [('film', E.TEARDOWN, 4.10), ('img', 'carousel_1'), ('img', 'website'), ('img', 'close_food'),
         ('film', E.HYPER, 15.90), ('img', 'design_post'), ('hero', None), ('img', 'carousel_2')]
STAG = [0.00, .03, .01, .045, .02, .035, .005, .025]
FLY = .26                                       # fly-in duration: card i lands at START - .03 + STAG[i] + FLY (12.19-12.24)
BEZ = 12                                       # bezel (art px, art is 2x the base card size)


def C(k, fn): return E.cached(('s05',) + (k if isinstance(k, tuple) else (k,)), fn)


# ---------------------------------------------------------------- card art
def _content_size(i):
    kind = CARDS[i][0]
    if kind == 'film': return 300, 534
    if CARDS[i][1] == 'website': return 464, 294
    if CARDS[i][1] == 'close_food': return 300, 534
    return 352, 440


def _cover(img, w, h):
    sc = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * sc + .999), int(img.height * sc + .999)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2; return im.crop((x, y, x + w, y + h))


def _frame(content):
    """frosted glass card around `content` (RGB): bezel, hairline rim, sheen, inner vignette."""
    cw, ch = content.size; w, h = cw + 2 * BEZ, ch + 2 * BEZ
    def chrome():
        im = E.glass_panel(w, h, radius=34, alpha=.16, border=.0, shine=False)
        m = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(m).rounded_rectangle((2, 2, w * 2 - 3, h * 2 - 3), 68, outline=255, width=3)
        rim = Image.new('RGBA', (w, h), (235, 230, 255, 0)); rim.putalpha(m.resize((w, h), Image.LANCZOS).point(lambda v: int(v * .7)))
        im.alpha_composite(rim)
        # sheen: soft diagonal light over the upper-left of the glass
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        u = (xx / w) * .6 + (yy / h) * .4
        sh = np.clip(.16 - u * .22, 0, 1) + .10 * np.exp(-((u - .30) / .025) ** 2)
        sm = Image.new('L', (w, h)); ImageDraw.Draw(sm).rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=255)
        s_ = Image.fromarray((np.clip(sh, 0, 1) * 255).astype(np.uint8))
        sim = Image.new('RGBA', (w, h), (255, 255, 255, 0)); sim.putalpha(Image.composite(s_, Image.new('L', (w, h)), sm))
        return im, sim
    base, sheen = C(('chrome', w, h), chrome)
    out = base.copy()
    c = E.rounded(content.convert('RGBA'), 22)
    out.alpha_composite(c, (BEZ, BEZ))
    out.alpha_composite(sheen)
    return out


def card_art(i, t):
    kind = CARDS[i][0]; cw, ch = _content_size(i)
    if kind == 'film':
        src = K.film_src(CARDS[i][2] + (t - START))          # deterministic across chunked renders
        fr = E.clip(CARDS[i][1], (270, 480)).at(src)
        if fr is None: fr = Image.new('RGB', (270, 480), (10, 10, 14))
        return _frame(fr.resize((cw, ch), Image.BILINEAR))
    def mk():
        if kind == 'img':
            return _frame(_cover(E.asset(CARDS[i][1]), cw, ch))
        # hero product shot: the keyed headphone on a warm dark sweep
        bg = np.zeros((ch, cw, 3), np.float32)
        yy, xx = np.mgrid[0:ch, 0:cw].astype(np.float32)
        g = np.exp(-(((xx - cw * .5) / (cw * .55)) ** 2 + ((yy - ch * .42) / (ch * .5)) ** 2))
        bg += g[..., None] * np.array([58, 44, 30], np.float32) + np.array([10, 9, 12], np.float32)
        im = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
        sp = K.hero_sprite(); sc = cw * .86 / sp.width
        sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.LANCZOS)
        im.alpha_composite(sp, ((cw - sp.width) // 2, int(ch * .47 - sp.height / 2)))
        d = ImageDraw.Draw(im); f = E.font(26, 600)
        d.text((cw // 2, ch - 34), 'S I L E N C E   O N E', font=f, fill=(222, 200, 160), anchor='mm')
        return _frame(im.convert('RGB'))
    return C(('art', i), mk)


def glow_sprite():
    def mk():
        S = 320; m = Image.new('L', (S, S)); ImageDraw.Draw(m).rounded_rectangle((70, 70, S - 70, S - 70), 30, fill=255)
        g = Image.new('RGBA', (S, S), (122, 92, 255, 0)); g.putalpha(m.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * .62)))
        return g
    return C('glow', mk)


# ---------------------------------------------------------------- motion (pure functions of t)
OM = 2.30                                       # steady orbit speed (rad/s)
PH0 = -.55


def phase_free(t):
    u = max(0.0, t - START)
    return PH0 + OM * u + 1.5 * (1 - math.exp(-u / .16))


def _lock_phase():
    pf = phase_free(T_HEAD); step = math.pi / 4; off = math.pi / 8
    return off + step * math.ceil((pf - off) / step + .15)


PH_LOCK = _lock_phase()


def phase(t):
    if t < T_HEAD:
        k = smooth((t - T_IN) / (T_HEAD - T_IN))
        return phase_free(t) + (PH_LOCK - phase_free(T_HEAD)) * k
    x = t - T_HEAD
    return PH_LOCK + (OM / 26.) * math.exp(-x / .07) * math.sin(x * 26.) + .10 * x


def lockk(t): return smooth((t - T_HEAD) / .10)


WIPE = 3                                        # this card opens the shot as a defocused foreground wipe


def ring_xyz(a, r):
    """orbit-plane point (angle a, radius r) -> camera-space (X, Y, Z) relative to the ring centre (roll applied)."""
    X = r * math.cos(a); Zr = r * math.sin(a)
    Y = -Zr * SE; Z = Zr * CE
    return X * math.cos(ROLL) - Y * math.sin(ROLL), X * math.sin(ROLL) + Y * math.cos(ROLL), Z


def card_pos(i, t):
    """world-space centre (x, y), scale k, depth Z (relative to the head plane; >0 = behind him), orbit angle."""
    th = 2 * math.pi * i / N + phase(t)
    r = R * (1 - .05 * kick(t - T_HEAD, .09) * (t >= T_HEAD))
    u = clamp((t - START + .03 - STAG[i]) / FLY); e = 1 - (1 - u) ** 3      # all land in orbit on "STAYS"
    a = th + lerp(-.95, 0.0, e)                    # pulled in from the frame edges, spiralling onto the ring
    X, Y, Z = ring_xyz(a, lerp(2.25 * r, r, e))
    Z += lerp(-220., 0., e)
    k = F / max(1e-3, F + Z)
    return OCX + X * k, OCY + Y * k, k, Z, a


def _sheen_u(w, h):
    def mk():
        yy, xx = np.mgrid[0:h // 4, 0:w // 4].astype(np.float32)
        return (xx / (w / 4)) * .62 + (yy / (h / 4)) * .38
    return C(('sheen_u', w, h), mk)


def _rim(w, h):
    def mk():
        m = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(m).rounded_rectangle((3, 3, w * 2 - 4, h * 2 - 4), 66, outline=255, width=7)
        m = m.resize((w, h), Image.LANCZOS)
        im = Image.new('RGBA', (w, h), (236, 228, 255, 0)); im.putalpha(m)
        g = Image.new('RGBA', (w, h), (150, 120, 255, 0)); g.putalpha(m.filter(ImageFilter.GaussianBlur(6)))
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im); return out
    return C(('rim', w, h), mk)


def shimmer(art, xl):
    """lock shimmer in card space: a specular band sweeps across the glass + the bezel rim lights up."""
    if not (0 <= xl < .42): return art
    art = art.copy(); w, h = art.size
    sp = xl / .34
    if sp < 1:
        u = _sheen_u(w, h); c = lerp(-.2, 1.25, K.eio(sp))
        band = np.exp(-((u - c) / .07) ** 2) * .55 + np.exp(-((u - c + .1) / .018) ** 2) * .35
        a = Image.fromarray((np.clip(band, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
        from PIL import ImageChops
        a = ImageChops.multiply(a, art.getchannel('A'))
        hl = Image.new('RGBA', (w, h), (255, 250, 240, 0)); hl.putalpha(a); art.alpha_composite(hl)
    fl = kick(xl, .12)
    if fl > .03: art.alpha_composite(E.fade(_rim(w, h), fl))
    return art


def card_draw(ctx, i, t):
    x, y, k, Z, a = card_pos(i, t)
    if F + Z < 280: return None                  # behind the lens
    art = card_art(i, t)
    lk = lockk(t)
    order = ((a - (-math.pi / 2)) % (2 * math.pi)) / (2 * math.pi)
    xl = t - T_HEAD - .012 - .10 * order        # lock shimmer travels around the ring
    art = shimmer(art, xl)
    ry = -40 * math.cos(a) * (1 - .4 * lk)
    rx = 10.; rz = math.degrees(ROLL) * .6
    q = K.quad(art.width, art.height, x, y, CARD_S * k, rx, ry, rz, f=F)
    w_ = K.warp(art, q, bounds=(W, H), margin=200)
    if w_ is None: return None
    img, x0, y0 = w_
    # depth: dim + cool the far half, DOF (focus on his head plane)
    zn = Z / (R * CE)
    if zn > 0: bright = 1 - .30 * min(1, zn); blur = 2.6 * min(1.3, zn)
    else: bright = 1.0; blur = 4.2 * (-zn) ** 1.5 * (1 - .55 * lk)    # the lock snaps the near cards into focus
    fl = kick(xl, .07) if xl >= 0 else 0.0
    land = START - .03 + STAG[i] + FLY             # the card is captured into the orbit (on "STAYS")
    lf = .8 * kick(t - land, .09) if t >= land else 0.0
    fl = max(fl, lf * .45)
    if bright != 1 or fl > .01:
        img = K.tint_rgba(img, bright=bright * (1 + .55 * fl), add=(30 * fl, 26 * fl, 50 * fl) if fl > .01 else None,
                          mul=(.95, .95, 1.06) if zn > 0 else None)
    if blur > .5:
        p = int(blur * 2.2) + 2
        img = K.fast_blur(K.pad_img(img, p), blur); x0 -= p; y0 -= p
    # motion blur (180-degree shutter)
    xa, ya, ka, _, _ = card_pos(i, t - 1 / 120); xb, yb, kb, _, _ = card_pos(i, t + 1 / 120)
    dx, dy = xb - xa, yb - ya
    if math.hypot(dx, dy) > 2:
        img, ox, oy = K.smear(img, dx, dy); x0 += ox; y0 += oy
    layer = 'behind' if Z > 6 else 'front'
    # glow under the card
    gw = int((max(p_[0] for p_ in q) - min(p_[0] for p_ in q)) * 1.7) + 4
    gh = int((max(p_[1] for p_ in q) - min(p_[1] for p_ in q)) * 1.5) + 4
    if gw < 2600 and gh < 3000:
        g = glow_sprite().resize((max(4, gw), max(4, gh)), Image.BILINEAR)
        ga = min(1.0, (.55 + .45 * fl + .45 * lf) * (.65 if zn > 0 else 1.0))
        ctx.add(layer, g, x, y + 10 * k, alpha=ga)
    glass = int(round(9 * k)) if (blur < 4 and F + Z > 600) else 0
    ctx.add(layer, img, x0, y0, center=False, glass=glass)
    return (x, y, k, Z, a, q)


# ---------------------------------------------------------------- the orbit line + lock pulse (on HEAD)
def ring_strokes(radius, width, alpha, rev=1.0, hot=0.0, n=150):
    """segments of the orbit circle of `radius` in the ring plane: [(p0, p1, rgba, width_px, is_back)] in world px.
    rev: ignition progress (0 = front point only .. 1 = full circle), hot: brightness of the leading edge."""
    g0 = np.array(E.GRAD[0], np.float32); g2 = np.array(E.GRAD[2], np.float32)
    out = []; prev = None
    for j in range(n + 1):
        a = -math.pi / 2 + 2 * math.pi * j / n
        dist = abs(((a + math.pi / 2) + math.pi) % (2 * math.pi) - math.pi) / math.pi        # 0 front .. 1 back
        if dist > rev: prev = None; continue
        X, Y, Z = ring_xyz(a, radius); k = F / (F + Z)
        p = (OCX + X * k, OCY + Y * k)
        if prev is not None:
            col = g0 + (g2 - g0) * ((math.cos(a) + 1) / 2)
            hd = hot * clamp(1 - (rev - dist) / .22) if rev < 1 else 0.0
            c = tuple(int(min(255, v * (1 + 1.3 * hd) + 110 * hd)) for v in col) + (int(255 * alpha),)
            out.append((prev, p, c, max(2, int(round(width * k))), Z > 0))
        prev = p
    return out


def ring_layers(ctx, t):
    x = t - T_HEAD
    if x < 0: return
    rev = smooth(x / .22)
    al = .85 * kick(x, .25) + .38
    segs = ring_strokes(R, 3.4, min(1, al), rev, hot=1.0)
    if x < .5:                                        # sonar pulse racing outward in the orbit plane
        rr = R * (1.04 + 1.1 * K.expo(x / .5)); pa = (1 - x / .5) ** 1.6       # starts ON the orbit (never crosses his face)
        segs += ring_strokes(rr, 5.5 * (1 - .5 * x / .5), pa)
    for back in (True, False):
        ss = [s_ for s_ in segs if s_[4] == back]
        if not ss: continue
        xs = [p[0] for s_ in ss for p in (s_[0], s_[1])]; ys = [p[1] for s_ in ss for p in (s_[0], s_[1])]
        pad = 50; x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
        cw, ch = int(max(xs)) + pad - x0, int(max(ys)) + pad - y0
        cv = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(cv)
        for p0, p1, c, wd, _ in ss:
            d.line([(p0[0] - x0, p0[1] - y0), (p1[0] - x0, p1[1] - y0)], fill=c, width=wd)
        core = cv.filter(ImageFilter.GaussianBlur(.8))
        glow = K.fast_blur(cv, 13)
        out = Image.alpha_composite(glow, glow); out.alpha_composite(core)
        ctx.add('behind' if back else 'front', out, x0, y0, center=False)


def glints(ctx, t, placed):
    """star glints on the card corners during the lock flash."""
    x = t - T_HEAD
    if not (0 <= x < .45): return
    for i, pl in enumerate(placed):
        if pl is None: continue
        cx, cy, k, Z, a, q = pl
        order = ((a + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
        e = x - .02 - .10 * order
        if e < 0 or e > .3: continue
        s = math.sin(math.pi * clamp(e / .3)) * (1.0 if Z <= 0 else .6)
        st = K.star(70, 4)
        sz = max(8, int(st.width * (.55 + .5 * s) * k))
        sp = st.resize((sz, sz), Image.BILINEAR)
        px, py = q[1] if i % 2 == 0 else q[0]
        ctx.add('behind' if Z > 6 else 'front', sp, px, py, alpha=s)


# ---------------------------------------------------------------- camera
def camera(t):
    """11.96 CUT to the WIDE angle (s04 ends on a 1.27x close-up: -21 % scale, his head drops 160 px -> a clear
    multicam cut that hides the pose jump); a slow push while the memories gather; on "HEAD." a snap punch-in
    (spring, slight overshoot) to a 1.25x close-up, so the next cut (s06, wide again) is a clear framing change too.
    Anchored on his head (world 520, 805), re-centred by dx when there is room (the engine clamps at the edges)."""
    u = t - START
    z = 1.0 + .075 * clamp(u / (T_HEAD - START)) ** 1.25
    rot = 0.0
    dx, dyy = 0.0, 0.0
    if t >= T_HEAD:
        x = t - T_HEAD
        z += .15 * K.spring(x, 21., 16.) + .03 * smooth((x - .12) / .30)
        rot = -.012 * math.exp(-x / .09) * math.sin(x * 30.)          # tiny roll wobble on the punch (z >= 1.1 there)
        kf = int(x * E.FPS + 1e-6); tab = [(0, 0), (0, 6), (-4, -3), (2, 2), (-1, 0)]
        if kf < len(tab): dx, dyy = tab[kf]
    return dict(z=z, x=520., y=805., dx=20. + dx, dy=dyy, rot=rot)


# ---------------------------------------------------------------- frame
def draw(ctx, lt, t):
    ctx.cam = camera(t)
    ctx.bg_blur = .8
    P = ctx.post; P['vignette'] = .34
    ctx.captions = False
    # cards, far to near
    order = sorted(range(N), key=lambda i: -card_pos(i, t)[3])
    placed = [None] * N
    ring_layers(ctx, t)                           # under the cards in both layers
    for i in order:
        placed[i] = card_draw(ctx, i, t)
    glints(ctx, t, placed)
    x = t - T_HEAD
    if 0 <= x < .25:
        P['bright'] = 1 + .10 * kick(x, .06)
    fl = .24 * kick(x, .05) if x >= 0 else 0.0
    def wrap(fr):
        if fl > .02: fr = K.light_hit(fr, fl)
        K.draw_caps(fr, t, PAGES, CAP_Y)
        return fr
    ctx.wrap = wrap
