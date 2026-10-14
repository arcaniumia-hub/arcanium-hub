"""s06 — VAZIO (28.32–32.80; its first framing is also drawn by s05 on 28.30, the frame seg 15's pose appears).
"Sem edição, você tem um terreno vazio… e ninguém para pra olhar um terreno vazio."

SHOT F (28.30 jump) — the finished house, big and lit, him low in frame.  "SEM" (28.376): the kit cuts every light, the
     studio's monitors die with it, the music is gone — only wind.  The wind takes the house piece by piece (roof torn
     off on "EDIÇÃO", walls blown downwind): wind streaks rake across the frame, the camera cranes up and back to
     show the emptiness; the world drains of colour.  "VAZIO" (30.27): the plinth
     sinks into the lot — nothing left but grass, wind and the stepping stones of a path to nowhere.
SHOT G (30.80 jump) — cutaway, he is gone too: a low, lonely wide of the empty lot floating in the dark, colour drained.
     "NINGUÉM" — a tumbleweed rolls in on the wind and bounces across the lot ON the words (-GUÉM, PARA, OLHAR,
     TERRENO, VAZIO); a passer-by hurries past, head down in his phone (it dings on "OLHAR") — he never looks.  The
     tumbleweed rolls right behind him.  The phone is the only colour in the frame.
Captions: engine look on the measured onsets (_c_kit.PAGES), y 1605 (his beard bottom stays above ~1541).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS
from sections import _c_kit as K

START, END = E.span(15, 16)                   # 28.32 – 32.80
W, H = E.W, E.H
clamp, lerp, expo, eo, smooth = E.clamp, K.lerp, K.expo, K.eo, K.smooth

# tumbleweed ground contacts land on the words
BOUNCES = [K.O_GUEM, K.O_PARA, K.O_OLHAR, K.O_TERRENO16, K.O_VAZIO16]

CUES = [c for c in HS.BUILD_CUES if START <= c[0] < END] + [
    (K.O_SEM + .01, 'thud', {'gain': -16}),                   # the power dies (with the kit's switch)
    (29.30, 'whoosh', {'gain': -15, 'pan': .5}),              # the walls are blown downwind
    (K.O_VAZIO15 + .03, 'thud', {'gain': -12}),               # the plinth is gone: empty
    (K.J16, 'whoosh', {'gain': -18}),                         # cutaway: a gust
] + [(b, 'crack', {'seed': i, 'dur': .18, 'gain': -17 - 1.5 * i, 'pan': -.5 + .25 * i}) for i, b in enumerate(BOUNCES)] + [
    (b, 'thud', {'gain': -26 - 1.5 * i, 'pan': -.5 + .25 * i}) for i, b in enumerate(BOUNCES)] + [
    (K.O_OLHAR + .03, 'notify', {'gain': -12, 'pan': .2}),    # his phone dings — he never looks up
]

# ================================================================================================ SHOT F
HSIZE = (1080, 1400); HFADE = (1120, 1360)
def sy(y, h=HSIZE[1]): return (y - h / 2) / h
AV_F = dict(show=True, s=1.0, x=0., y=400., alpha=1.0, copies=[], bright=1.0)     # chin <= ~1541: captions clear his face
CF0 = dict(yaw=27.0, pitch=16.0, dist=27.0, fov=30, target=(0.0, 2.2, -0.4), shift=(0, sy(505)))
CF1 = dict(yaw=37.0, pitch=25.0, dist=34.5, fov=30, target=(0.0, 0.9, -0.6), shift=(0, sy(585)))
CF2 = dict(yaw=40.0, pitch=23.0, dist=30.5, fov=30, target=(0.0, 0.4, -0.2), shift=(0, sy(590)))

def cam_f(t):
    c = K.cam_mix(CF0, CF1, K.eio3((t - 28.55) / (30.30 - 28.55)))
    if t > 30.25: c = K.cam_mix(c, CF2, smooth((t - 30.25) / (K.J16 - 30.25)))
    return c

def drain(t):
    """world saturation over the vanish (1 -> 0.28)."""
    return lerp(1.0, .28, smooth((t - (K.O_SEM + .05)) / (30.35 - K.O_SEM)))

def wind_layer(t, k, size=(W, 1500), n=34, seed=0, alpha=1.0, speed=1.0):
    """wind streaks raking left -> right (half-res, soft). k = wind strength 0..1."""
    w2, h2 = size[0] // 2, size[1] // 2
    im = Image.new('RGBA', (w2, h2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(n):
        r = [K.hrand(i, seed * 10 + j) for j in range(7)]
        y = r[0] * h2; L = (60 + 260 * r[1]) * (.5 + .5 * k); v = (900 + 1300 * r[2]) * speed
        x = (r[3] * (w2 + 600) + v * t * .5) % (w2 + 600) - 300
        yy = y + 14 * math.sin(t * (1.5 + r[4]) + i)
        a = int(255 * alpha * k * (.10 + .22 * r[5]))
        if a < 3: continue
        d.line([(x, yy), (x + L, yy - L * .06)], fill=(232, 232, 240, a), width=1 if r[6] < .7 else 2)
    return im.resize(size, Image.BILINEAR)

def shot_f(ctx, t):
    st = HS.state_at(t)
    s = drain(t)
    lights = st['lights']
    dim = .44 + .20 * (1 - lights if t >= K.O_SEM else 0) + .08 * smooth((t - 29) / 1.3)
    ctx.bg_img = K.studio_bg(round(dim, 2), 12.0, sat=round(max(.3, s), 2))
    ctx.avatar = dict(AV_F)
    dx, dy = K.shake(t, 28.54, 6.0, .4, 13, 5)
    ex, ey = K.shake(t, K.O_VAZIO15, 5.0, .35, 11, 6); dx += ex; dy += ey
    ctx.cam = dict(z=1.0 + .01 * K.kick(t, K.O_SEM, 1, .3), x=540., y=900., dx=dx, dy=dy, rot=0.)
    hs = K.House(st, cam_f(t), HSIZE, fade=HFADE, t=t)
    img = hs.img if s > .98 else K.desat(hs.img, s, cool=1 - s, mul=1 - .12 * (1 - s))
    ctx.add('behind', img, 0, 0, center=False)
    wk = st['wind']
    if wk > .02:
        ctx.add('behind', wind_layer(t, wk, (W, 1400), 34, 1, .9), 0, 0, center=False)
        ctx.add('front', wind_layer(t, wk, (W, 1920), 10, 2, .45, 1.6), 0, 0, center=False)
    ctx.post['sat'] = lerp(1.0, .62, smooth((t - K.O_SEM) / (30.35 - K.O_SEM)))
    ctx.post['bright'] = lerp(1.0, .93, smooth((t - K.O_SEM) / .4))
    ctx.post['vignette'] = .36 + .14 * smooth((t - K.O_SEM) / 1.5)
    K.captions(ctx, t)

# ================================================================================================ SHOT G — the empty lot
GSIZE = (1080, 1500)
CG0 = dict(yaw=15.0, pitch=28.5, dist=24.0, fov=30, target=(0.0, 0.0, 2.2), shift=(0, .02))
CG1 = dict(yaw=11.5, pitch=27.0, dist=22.0, fov=30, target=(0.0, 0.0, 2.4), shift=(0, .02))
G_ORG = (0, 50)
def cam_g(t): return K.cam_mix(CG0, CG1, (t - K.J16) / (END - K.J16))

# --- tumbleweed (3-D tangle of twigs, rolling + bouncing on the words)
TW_R, TW_Z = 0.52, 6.9
def tw_geom():
    def mk():
        rng = np.random.default_rng(7); loops = []
        for _ in range(46):
            n = rng.normal(size=3); n /= np.linalg.norm(n)
            a = np.cross(n, [0, 0, 1.0]); a = a / (np.linalg.norm(a) + 1e-9); b = np.cross(n, a)
            ph = rng.uniform(0, 2 * np.pi); span = rng.uniform(1.4, 4.2); m = 22
            th = ph + np.linspace(0, span, m)
            rad = TW_R * (rng.uniform(.62, 1.0) + .10 * np.sin(th * rng.uniform(2, 5)))
            pts = (np.cos(th)[:, None] * a + np.sin(th)[:, None] * b) * rad[:, None] + rng.normal(0, .02, (m, 3))
            loops.append(pts)
        return loops
    return K.C('twgeom', mk)

def tw_state(t):
    """tumbleweed centre (x, y, z) and roll angle at t."""
    x0, t0, v = -2.75, 30.92, 3.55
    x = x0 + v * (t - t0)
    # hops between ground contacts (the first one comes in from the air)
    pts = [t0 - .18] + BOUNCES + [BOUNCES[-1] + .44, BOUNCES[-1] + .80]
    hts = [.55, .42, .48, .44, .40, .34, .26]
    y = TW_R
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if a <= t < b:
            u = (t - a) / (b - a); y = TW_R + 4 * hts[i] * u * (1 - u)
            if i == 0: y = TW_R + hts[0] * (1 - u * u) * 1.6
    ang = (x - x0) / TW_R
    return np.array([x, y, TW_Z]), ang

def tumbleweed(hs, t):
    """(sprite, x, y) of the tumbleweed + its ground shadow (world px)."""
    c, ang = tw_state(t)
    S, Z = hs.proj([c, [c[0], 0.0, c[2]]])
    sc = hs.px_per_m(c)
    ca, sa = math.cos(-ang), math.sin(-ang)
    Rz = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
    Ry = np.array([[math.cos(.6), 0, math.sin(.6)], [0, 1, 0], [-math.sin(.6), 0, math.cos(.6)]])
    R = Rz @ Ry
    SS = 2; Rp = int(TW_R * sc * 1.25) + 6
    im = Image.new('RGBA', (2 * Rp * SS, 2 * Rp * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    loops = [p @ R.T for p in tw_geom()]
    order = sorted(range(len(loops)), key=lambda k: loops[k][:, 2].mean())
    for k in order:
        p = loops[k]; dep = clamp(p[:, 2].mean() / TW_R * .5 + .5)
        col = (int(lerp(92, 205, dep)), int(lerp(80, 182, dep)), int(lerp(62, 140, dep)), 255)
        xy = [(Rp * SS + x * sc * SS, Rp * SS - y * sc * SS) for x, y, z in p]
        d.line(xy, fill=col, width=max(1, int(sc * .028 * SS * (.7 + .6 * dep))), joint='curve')
    spr = im.resize((2 * Rp, 2 * Rp), Image.LANCZOS)
    # shadow on the lot
    hgt = c[1] - TW_R
    sw = int(TW_R * sc * 2.2); shh = max(4, int(sw * .26))
    sh = Image.new('L', (sw + 40, shh + 40)); ImageDraw.Draw(sh).ellipse((20, 20, 20 + sw, 20 + shh), fill=int(150 * clamp(1 - hgt / .9)))
    shi = Image.new('RGBA', sh.size, (6, 6, 10, 0)); shi.putalpha(sh.filter(ImageFilter.GaussianBlur(8)))
    return spr, S[0], shi, S[1]

# --- the passer-by (maquette figure, head down in his phone)
WK_Z = 5.5
WK_V = 2.35
def walker_x(t): return 3.6 - WK_V * (t - K.J16)

def walker(hs, t):
    """(sprite, foot screen xy, phone glow screen xy) of the passer-by walking left."""
    x = walker_x(t); foot = np.array([x, 0.0, WK_Z])
    S, Z = hs.proj([foot]); sc = hs.px_per_m(foot)
    h = 1.76 * sc; SS = 2
    phase = (t - K.J16) * WK_V / 1.50                            # stride 1.5 m
    bob = abs(math.sin(phase * math.pi * 2)) * h * .012
    w_ = int(h * .9) + 20; hh = int(h * 1.1) + 20
    im = Image.new('RGBA', (w_ * SS, hh * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fx, fy = w_ / 2 * SS, (hh - 10) * SS
    H_ = h * SS; wd = H_ * .30
    c = np.array([214, 212, 206]); shd = c * .62; dark = c * .45
    def col(cc, a=255): return (int(cc[0]), int(cc[1]), int(cc[2]), a)
    sw = math.sin(phase * math.pi * 2) * .26
    hip = (fx, fy - H_ * .50 - bob * SS)
    for k, s_ in ((0, sw), (1, -sw)):                           # legs (far one darker)
        lx = fx + s_ * H_ * .45
        d.polygon([(hip[0] - wd * .14, hip[1]), (hip[0] + wd * .14, hip[1]), (lx + wd * .09, fy), (lx - wd * .09, fy)], fill=col(c if k else shd))
    sy_ = fy - H_ * .80 - bob * SS
    lean = -H_ * .03                                            # leaning forward (walking left)
    d.polygon([(fx - wd * .46 + lean, sy_), (fx + wd * .46 + lean, sy_), (fx + wd * .30, fy - H_ * .47 - bob * SS), (fx - wd * .30, fy - H_ * .47 - bob * SS)], fill=col(c))
    d.polygon([(fx + wd * .05 + lean, sy_), (fx + wd * .46 + lean, sy_), (fx + wd * .30, fy - H_ * .47 - bob * SS), (fx + wd * .05, fy - H_ * .47 - bob * SS)], fill=col(shd))
    # back arm swings, front arm bent up holding the phone in front of his face
    d.line([(fx + wd * .42 + lean, sy_ + H_ * .03), (fx + wd * .42 + sw * H_ * .3, fy - H_ * .50)], fill=col(shd), width=max(2, int(wd * .18)))
    hand = (fx - wd * .95 + lean, sy_ + H_ * .03)
    d.line([(fx - wd * .40 + lean, sy_ + H_ * .03), (fx - wd * .55, sy_ + H_ * .20), hand], fill=col(c), width=max(2, int(wd * .18)), joint='curve')
    d.line([(fx + wd * .46 + lean, sy_), (fx + wd * .30, fy - H_ * .47 - bob * SS)], fill=(160, 120, 255, 200), width=max(1, int(H_ / 60)))
    # head bowed toward the phone
    hr = H_ * .085; hc = (fx - wd * .18 + lean, sy_ - hr * 1.05)
    d.ellipse((hc[0] - hr, hc[1] - hr, hc[0] + hr, hc[1] + hr), fill=col(c))
    # phone: dark slab with a lit screen facing him
    pw, ph = wd * .26, wd * .44
    d.polygon([(hand[0] - pw * .5, hand[1] - ph * .6), (hand[0] + pw * .4, hand[1] - ph * .75), (hand[0] + pw * .5, hand[1] + ph * .3), (hand[0] - pw * .4, hand[1] + ph * .45)], fill=(20, 20, 28, 255))
    d.polygon([(hand[0] - pw * .2, hand[1] - ph * .55), (hand[0] + pw * .45, hand[1] - ph * .66), (hand[0] + pw * .47, hand[1] + ph * .26), (hand[0] - pw * .15, hand[1] + ph * .36)], fill=(150, 190, 255, 255))
    spr = im.resize((w_, hh), Image.LANCZOS)
    org = (S[0][0] - w_ / 2, S[0][1] - (hh - 10))
    phone = (org[0] + hand[0] / SS, org[1] + hand[1] / SS)
    face = (org[0] + hc[0] / SS, org[1] + hc[1] / SS)
    return spr, org, phone, face, sc

def soft_ellipse(w, h, a, col=(6, 6, 10)):
    def mk():
        m = Image.new('L', (w + 40, h + 40)); ImageDraw.Draw(m).ellipse((20, 20, 20 + w, 20 + h), fill=255)
        im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m.filter(ImageFilter.GaussianBlur(9))); return im
    return E.fade(K.C(('sell', w, h, col), mk), a)

def g_bg():
    """dark, drained studio far behind the floating lot."""
    def mk():
        im = K.studio_bg(.62, 22.0, sat=.25)
        a = np.asarray(im, np.float32) * np.array([.93, .96, 1.04], np.float32)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return K.C('gbg', mk)

def shot_g(ctx, t):
    st = HS.state_at(t)
    ctx.bg_img = g_bg()
    ctx.avatar = dict(show=False, s=1.0, x=0., y=0., alpha=0., copies=[], bright=1.0)
    ctx.cam = dict(z=1.0, x=540., y=900., dx=0., dy=0., rot=0.)
    hs = K.House(st, cam_g(t), GSIZE, org=G_ORG, t=t)
    ctx.add('behind', K.desat(hs.img, .26, cool=.8, mul=.92), G_ORG[0], G_ORG[1], center=False)
    layers = []
    # tumbleweed (further back) and the walker (front edge of the lot)
    if t >= 30.86:
        spr, (tx, ty), shi, (gx, gy) = tumbleweed(hs, t)
        layers.append((TW_Z, lambda spr=spr, tx=tx, ty=ty, shi=shi, gx=gx, gy=gy: (ctx.add('behind', shi, gx, gy), ctx.add('behind', K.desat(spr, .55), tx, ty))))
    if t >= K.J16 - 1e-6:
        spr, org, phone, face, sc = walker(hs, t)
        fx = org[0] + spr.width / 2; fy = org[1] + spr.height - 10
        def dw(spr=spr, org=org, phone=phone, face=face, sc=sc, fx=fx, fy=fy):
            ctx.add('behind', soft_ellipse(int(sc * .9), int(sc * .22), .5), fx, fy)
            ctx.add('behind', spr, org[0], org[1], center=False)
            ding = math.exp(-(t - K.O_OLHAR) / .35) if t >= K.O_OLHAR else 0
            ctx.add('behind', K.glow_spot(int(sc * .55), (120, 165, 255), .55 + .4 * ding), phone[0], phone[1])
            ctx.add('behind', K.glow_spot(int(sc * .28), (150, 190, 255), .35 + .35 * ding), face[0], face[1] + sc * .04)
        layers.append((WK_Z, dw))
    for z, fn in sorted(layers, key=lambda l: l[0]): fn()
    wk = st['wind']
    ctx.add('behind', wind_layer(t, max(.55, wk), (W, 1500), 30, 3, .8), 0, G_ORG[1], center=False)
    ctx.post['sat'] = .9
    ctx.post['vignette'] = .46
    lt = t - K.J16
    if lt < .08: ctx.post['flash'] = .10 * (1 - lt / .08)
    K.captions(ctx, t)

# ================================================================================================ draw
def draw(ctx, lt, t):
    if t < K.J16: shot_f(ctx, t)
    else: shot_g(ctx, t)
