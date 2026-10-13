"""s08 — "That's why we created LUMARC." (35.04–37.28)  SIGNATURE: GLASS SLATS -> LOGO DOWNBEAT

35.04  cut to a centred, clean close shot (the UI clears); 7 seams start to glint in the silence.
35.38  "That's why": the frame splits into 8 vertical prisms of glass. Each one turns on its vertical axis (alternating
       directions, different angles), its image slides up/down at its own speed and is refracted (magnified 1.06–1.12x,
       shifted proportional to the angle, mild fluted-lens curvature). Every prism has a sliding vertical specular,
       a bright leading edge, a lit lilac side face (thickness) and a shadowed trailing edge. Between them: the deep
       LUMARC brand space (night gradient, violet core, soft depth-of-field particles).
36.00  "we created": the glass frosts over, the prisms turn edge-on and become blades of light; particles stretch
       into speed streaks (riser). 36.40 the blades rush to the centre.
36.60  "LUMARC" (measured onset 36.58): the blades meet -> a white-violet light burst centred on the logo (additive,
       ~3-frame decay; frame edges stay deep night), anamorphic streak, shockwave ring, bloom; the logo pops in
       whole where the 8 blades met (scale 1.14 -> 1). THE downbeat.  36.70 a sheen sweeps the logo.
37.00  resolve: the prisms flip back in from edge-on (centre outward) — their edges fade out as they reach 0° — onto
       a tighter close-up (z 1.30) while the logo shrinks to 300 px at y 252 for the s09 handoff (s09 opens wider,
       z 1.12, so the 37.28 jump reads as a cut).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

START, END = E.span(21, 21)            # 35.04 – 37.28
# measured on the voice track
W_THATS, W_WHY, W_WE, W_CREATED = 35.38, 35.57, 36.00, 36.10
HIT = 36.60                             # "LUMARC" onset (E.word_time = 36.645, voice onset 36.58)
CONV0 = 36.40                           # blades converge
RES0, RES1 = 37.00, 37.24               # resolve back to the studio

CUES = [
    (35.18, 'tick', {'gain': -12}),                 # seams glint
    (W_THATS - .02, 'glass', {}),                   # prisms split
    (W_WHY, 'whoosh', {'gain': -8}),
    (W_WE - .1, 'riser', {'to': HIT}),              # build to the logo
    (CONV0, 'swoosh_up', {'gain': -4}),             # blades rush in
    (HIT, 'boom', {}),                              # THE downbeat
    (HIT, 'impact', {'gain': -4}),
    (HIT + .03, 'shimmer', {}),
    (RES0 - .02, 'glass', {'gain': -6}),            # prisms flip back
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H
N = 8
SW = W / N                              # 135 px
LCX, LCY = W / 2, H * .46               # logo / burst centre


def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x):
    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def C(k, fn): return E.cached(('s08',) + (k if isinstance(k, tuple) else (k,)), fn)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0


# ================================================================ brand space
def space_base():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H * .46) / (H * .42)) ** 2)
        base = np.array(E.BG, np.float32) * .75
        core = np.clip(1 - r, 0, 1) ** 1.9
        col = base[None, None] + core[..., None] * np.array([62, 40, 140], np.float32)
        r2 = np.sqrt(((xx - W * .5) / (W * .55)) ** 2 + ((yy - H * 1.02) / (H * .3)) ** 2)
        col += (np.clip(1 - r2, 0, 1) ** 2)[..., None] * np.array([24, 36, 120], np.float32)
        # soft volumetric shafts falling from the top
        for x0, wd, a in ((W * .3, 90, 10), (W * .62, 140, 8), (W * .82, 70, 6)):
            sh = np.exp(-((xx - x0 - (yy - H * .1) * .12) / wd) ** 2) * np.clip(1 - yy / (H * .9), 0, 1)
            col += sh[..., None] * np.array([a, a * .8, a * 2], np.float32)
        return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA')
    return C('space', mk)


def particles():
    def mk():
        rng = np.random.default_rng(21); n = 150
        return dict(a=rng.uniform(0, 2 * math.pi, n), r=rng.uniform(.05, 1.0, n) ** .7, z=rng.uniform(0, 1, n),
                    b=rng.uniform(.4, 1, n), hue=rng.uniform(0, 1, n))
    return C('parts', mk)


def sprite(sig_b, a_b, h_b):
    """soft gaussian particle (sigma bucket, alpha bucket, hue bucket) — cached."""
    def mk():
        sig = .7 + sig_b * .9; R = int(math.ceil(sig * 3.2)) + 1
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
        g = np.exp(-(xx * xx + yy * yy) / (2 * sig * sig))
        if sig > 3:      # bokeh: soft disc with a brighter rim
            rr = np.sqrt(xx * xx + yy * yy) / (sig * 1.6)
            g = np.clip(1.2 - rr, 0, 1) ** .6 * (.55 + .45 * np.clip(rr, 0, 1) ** 3) * np.clip((1.05 - rr) * 6, 0, 1)
        peak = (a_b / 6) * (1.0 if sig < 2 else (2 / sig) ** .55)
        h = h_b / 3
        col = (int(lerp(170, 235, h)), int(lerp(175, 165, h)), 255)
        im = Image.new('RGBA', g.shape[::-1], col + (0,)); im.putalpha(Image.fromarray((np.clip(g * peak, 0, 1) * 255).astype(np.uint8)))
        return im
    return C(('spr', sig_b, a_b, h_b), mk)


def draw_particles(img, t, speed_t, burst=0.0, streak=0.0):
    """depth starfield drifting toward camera (pure function of t). Soft gaussian sprites, bokeh when near;
    `streak` > 0 adds radial speed lines for the near ones."""
    P = particles()
    z = (P['z'] + speed_t) % 1.0
    persp = .35 + 1.9 * z ** 2
    R = P['r'] * persp * 760 + burst * 560 * P['r'] * (.4 + z)
    xs = LCX + np.cos(P['a']) * R; ys = LCY + np.sin(P['a']) * R * 1.25
    al = np.clip(z * 2.2, 0, 1) * np.clip((1 - z) * 6, 0, 1) * P['b']
    sig = .3 + 6.2 * z ** 2.2                               # depth of field: near = big + soft
    lines = None
    if streak > .02:
        lines = Image.new('L', (W // 2, H // 2)); ld = ImageDraw.Draw(lines)
    for x, y, a, s, h, rr, ang in zip(xs, ys, al, sig, P['hue'], R, P['a']):
        if a < .05 or not (-40 < x < W + 40 and -40 < y < H + 40): continue
        sp = sprite(min(9, int(s / .9)), max(1, min(6, int(a * 6 + .5))), int(h * 3.99))
        E._paste(img, dict(img=sp, xy=(int(x - sp.width / 2), int(y - sp.height / 2)), glass=0))
        if lines is not None and s < 4:
            L = streak * (40 + rr * .35)
            x0, y0 = x - math.cos(ang) * L, y - math.sin(ang) * L * 1.25
            ld.line((x0 / 2, y0 / 2, x / 2, y / 2), fill=int(200 * a * min(1, streak)), width=1)
    if lines is not None:
        g = lines.filter(ImageFilter.GaussianBlur(.8)).resize((W, H), Image.BILINEAR)
        lay = Image.new('RGBA', (W, H), (200, 190, 255, 0)); lay.putalpha(g); img.alpha_composite(lay)


def speed_int(t):
    """integral of particle speed: slow drift, accelerating into the hit, calm after."""
    s = .05 * (t - START)
    s += .5 * clamp((t - W_WE) / (HIT - W_WE)) ** 3          # riser
    s += .12 * eout((t - HIT) / .6)
    return s


def space_frame(t, burst=0.0):
    bg = space_base().copy()
    st = clamp((t - (W_WE + .1)) / (HIT - W_WE - .1)) ** 2 * (1 - clamp((t - HIT) / .05))
    draw_particles(bg, t, speed_int(t), burst=burst, streak=st * 1.4)
    return bg


# ================================================================ glass prisms
def frosted(A):
    im = Image.fromarray(A).resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2))
    return np.asarray(im.resize((W, H), Image.BILINEAR))


def slat_state(i, t):
    """dict(th: angle 0..pi/2, sgn, dy: image slide, xc, sc, refr: px, mag, frost 0..1)."""
    c = (i + .5) * SW
    dc = abs(i - (N - 1) / 2) / ((N - 1) / 2)          # 0 centre .. 1 edge
    sgn = 1 if i % 2 == 0 else -1
    if t < RES0 - .001:
        op = expo((t - (W_THATS - .02 + dc * .07)) / .55)
        drift = max(0.0, t - W_THATS)
        th = op * math.radians((24 + 16 * hrand(i, 1)) * (.7 + .55 * dc)) + math.radians(4) * math.sin(drift * 3 + i) * op
        th += math.radians(90) * smooth((t - (W_CREATED + .06 + (1 - dc) * .1)) / .34)   # toward edge-on
        th = clamp(th, 0, math.radians(90))
        dy = sgn * op * (40 + 50 * hrand(i, 2)) * (.5 + .5 * dc) + sgn * drift * (40 + 70 * hrand(i, 3))
        spread = 1 + .07 * op + .12 * smooth((t - W_WE) / .5)
        xc = W / 2 + (c - W / 2) * spread
        cv = ein((t - CONV0) / (HIT - CONV0))
        xc = lerp(xc, W / 2 + (c - W / 2) * .02, cv)
        sc = 1 - .04 * op * (.4 + .6 * dc)
        refr = sgn * math.sin(th) * (40 + 40 * hrand(i, 4))
        mag = 1.06 + .06 * math.sin(th)
        frost = smooth((t - W_WE) / .5)
        return dict(th=th, sgn=sgn, dy=dy, xc=xc, sc=sc, refr=refr, mag=mag, frost=frost, op=op)
    # resolve: flip back in from edge-on, centre outward; everything converges to identity at 0 deg
    k = expo((t - (RES0 + dc * .06)) / .2)
    th = math.radians(90) * (1 - k)
    st = math.sin(th)
    return dict(th=th, sgn=sgn, dy=sgn * 90 * (1 - k) ** 2, xc=c, sc=1 - .03 * st, refr=sgn * st * 50, mag=1 + .08 * st,
                frost=.6 * st, op=st)


_U = {}
def render_slats(fr, t, bg, blades=True):
    """composite the 8 prisms (sampling `fr`) over `bg` (RGBA brand space)."""
    A = np.asarray(fr.convert('RGB'))
    out = np.asarray(bg.convert('RGB'), np.float32).copy()
    fz = None
    lines = Image.new('L', (W // 2, H // 2)); ld = ImageDraw.Draw(lines)
    yy = np.arange(H, dtype=np.float32)
    vgrad = (np.clip(1 - yy / H, 0, 1) ** 2 * 14)[:, None, None]           # glass catches light from above
    for i in range(N):
        S = slat_state(i, t)
        th, sgn = S['th'], S['sgn']; cth, sth = math.cos(th), math.sin(th)
        edge = clamp(sth * 2.4) ** 2                                         # edges fade out as the prism reaches 0 deg
        w_f = SW * cth * S['sc']
        x0 = int(round(S['xc'] - w_f / 2)); x1 = int(round(S['xc'] + w_f / 2)); w = x1 - x0
        src_c = (i + .5) * SW
        if w >= 1:
            u = (np.arange(w, dtype=np.float32) + .5) / w - .5
            u2 = u * (1 - .22 * sth * (2 * np.abs(u)) ** 2)                  # fluted-lens curvature
            sx = np.clip(np.floor(src_c + u2 * SW / S['mag'] + S['refr']).astype(np.int32), 0, W - 1)
            sy = np.clip(np.floor((yy - H * .42) / S['mag'] + H * .42 - S['dy'] + .5).astype(np.int32), 0, H - 1)
            face = A[:, sx][sy].astype(np.float32)
            if S['frost'] > .02:
                if fz is None: fz = frosted(A)
                face = face * (1 - min(.92, S['frost'])) + fz[:, sx][sy].astype(np.float32) * min(.92, S['frost'])
            # glass tint + fresnel falloff toward the far edge
            ff = (u + .5) if sgn > 0 else (.5 - u)                           # 0 near leading edge .. 1 far edge
            shade = 1 - .42 * sth * ff ** 1.4
            face = face * shade[None, :, None] * np.array([.94, .94, 1.0], np.float32) + np.array([6, 4, 16], np.float32) * S['op']
            # sliding vertical specular + slow horizontal glint travelling with the slide
            pos = .5 + sgn * (.85 * sth - .35)
            spec = np.exp(-((u + .5 - pos) / .2) ** 2) * .16 * edge + np.exp(-((u + .5 - pos) / .05) ** 2) * .10 * edge * sth
            gy = (H * hrand(i, 8) + sgn * (t - W_THATS) * (500 + 400 * hrand(i, 9))) % (H * 1.5) - H * .25
            glint = (np.exp(-((yy - gy) / 140) ** 2) * .10 * edge)[:, None, None]
            lift = spec[None, :, None] + vgrad / 255 * edge + glint
            face = face + (255 - face) * np.clip(lift, 0, .9)
            # leading edge: bright 2 px + soft falloff; trailing edge: darker (fake thickness)
            le = w - 1 if sgn > 0 else 0
            for k_, f in ((0, .8), (1, .4), (2, .14)):
                xx = le - k_ * sgn
                if 0 <= xx < w: face[:, xx] += (np.array([246, 242, 255], np.float32) - face[:, xx]) * f * edge
            tr = min(w, 14)
            if tr > 1:
                ramp = (1 - np.linspace(0, 1, tr, dtype=np.float32)) ** 2 * .55 * edge
                if sgn > 0: face[:, :tr] *= (1 - ramp)[None, :, None]
                else: face[:, w - tr:] *= (1 - ramp[::-1])[None, :, None]
            a0, a1 = max(0, x0), min(W, x1)
            if a1 > a0: out[:, a0:a1] = face[:, a0 - x0:a1 - x0]
        # side face (glass thickness), lit lilac, on the leading side
        ws = int(round(SW * .15 * sth * S['sc']))
        if ws >= 1:
            sx0 = x1 if sgn > 0 else x0 - ws
            if fz is None: fz = frosted(A)
            cols = np.clip(np.arange(sx0, sx0 + ws) + int(S['refr'] * 1.5), 0, W - 1)
            sd = fz[:, cols].astype(np.float32) * .7 + np.array([120, 100, 235], np.float32) * (.18 + .3 * sth ** 4)
            gr = np.linspace(1.15, .6, ws, dtype=np.float32) if sgn > 0 else np.linspace(.6, 1.15, ws, dtype=np.float32)
            sd = sd * gr[None, :, None] + vgrad * 1.5
            b0, b1 = max(0, sx0), min(W, sx0 + ws)
            if b1 > b0:
                out[:, b0:b1] = out[:, b0:b1] * .2 + sd[:, b0 - sx0:b1 - sx0] * .8
        if blades:   # blade of light along the leading edge (strong when edge-on)
            li = clamp((sth - .82) / .18) ** 1.5 * edge
            if li > .02:
                xe = x1 if sgn > 0 else x0
                ld.line(((xe / 2, 0), (xe / 2, H / 2)), fill=int(255 * li), width=2)
    if blades and lines.getbbox():
        glow = np.asarray(lines.filter(ImageFilter.GaussianBlur(9)), np.float32) * 2.6
        core = np.asarray(lines.filter(ImageFilter.GaussianBlur(.7)), np.float32)
        add = glow[..., None] / 255 * np.array([120, 95, 255], np.float32) + core[..., None] / 255 * np.array([255, 250, 255], np.float32)
        vfall = (.55 + .45 * np.exp(-((np.arange(H // 2) - LCY / 2) / (H * .3)) ** 2))[:, None, None]
        add = np.asarray(Image.fromarray(np.clip(add * vfall, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
        out += add
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')


# ================================================================ logo moment
LOGO_W = 780
def logo_img():
    return C('logo', lambda: E.logo(LOGO_W))


def logo_bloom():
    def mk():
        lg = logo_img(); p = 160
        a = Image.new('L', (lg.width + 2 * p, lg.height + 2 * p)); a.paste(lg.getchannel('A'), (p, p))
        out = Image.new('RGBA', a.size, (0, 0, 0, 0))
        for r, col, m in ((60, (110, 80, 255), .9), (22, (160, 140, 255), .8)):
            g = Image.new('RGBA', a.size, col + (0,)); g.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, m=m: int(min(255, v * m * 1.6))))
            out.alpha_composite(g)
        return out
    return C('bloom', mk)


def logo_slices(t):
    """the logo, whole from the hit frame on (the 8 blades converging ARE the slices; it pops 1.14 -> 1 in scale)."""
    return logo_img()


def sheen(img, k, width=.16, strength=.8):
    if k <= 0 or k >= 1: return img
    w, h = img.size
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :] + np.linspace(0, .35, h, dtype=np.float32)[:, None]
    c = lerp(-.3, 1.5, k); band = np.clip(1 - np.abs(xx - c) / width, 0, 1) ** 2 * strength
    a = np.asarray(img.getchannel('A'), np.float32) / 255
    m = Image.fromarray((band * a * 255).astype(np.uint8))
    out = img.copy(); out.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [m])); return out


def burst_maps():
    """additive light maps (float32, full res): radial white-violet burst + anamorphic streak, centred on the logo."""
    def mk():
        h2, w2 = H // 2, W // 2
        yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32); yy *= 2; xx *= 2
        r = np.sqrt((xx - LCX) ** 2 + ((yy - LCY) * .85) ** 2)
        core = 1 / (1 + (r / 70) ** 2.2)
        halo = np.exp(-(r / 430) ** 2)
        rad = core[..., None] * np.array([255, 248, 255], np.float32) + halo[..., None] * np.array([120, 92, 255], np.float32) * .85
        dy = yy - LCY
        st = np.exp(-(dy / 5) ** 2) * np.exp(-((xx - LCX) / 620) ** 2)
        st2 = np.exp(-(dy / 26) ** 2) * np.exp(-((xx - LCX) / 900) ** 2)
        stk = st[..., None] * np.array([255, 250, 255], np.float32) * .9 + st2[..., None] * np.array([110, 120, 255], np.float32) * .5
        up = lambda a: np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
        return up(rad), up(stk)
    return C('burst', mk)


def light_burst(img, t):
    if t < HIT - .034: return img
    if t < HIT: env_r, env_s = .18, .25                         # 1-frame pre-glow where the blades meet
    else:
        x = (t - HIT); env_r = math.exp(-x / .075); env_s = math.exp(-x / .16) * .9
    if env_r < .02 and env_s < .02: return img
    rad, stk = burst_maps()
    o = np.asarray(img.convert('RGB'), np.float32) + rad * env_r + stk * env_s
    return Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).convert('RGBA')


def shock(img, t, cx, cy):
    k = (t - HIT) / .55
    if not 0 <= k < 1: return img
    lay = Image.new('L', (W // 2, H // 2)); d = ImageDraw.Draw(lay)
    for R0, wmul, am in ((40, 1.0, 1.0), (10, .6, .5)):
        R = (R0 + 1100 * eout(k)) / 2; wd = max(1, int((22 * (1 - k) + 2) * wmul / 2))
        d.ellipse((cx / 2 - R, cy / 2 - R * .92, cx / 2 + R, cy / 2 + R * .92), outline=int(255 * am * (1 - k) ** 1.2), width=wd)
    g = np.asarray(lay.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255
    o = np.asarray(img.convert('RGB'), np.float32) + g * np.array([190, 170, 255], np.float32)
    return Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).convert('RGBA')


def sparks(img, t, cx, cy):
    k = (t - HIT) / .6
    if not 0 <= k < 1: return
    lay = Image.new('L', (W // 2, H // 2)); d = ImageDraw.Draw(lay)
    for j in range(46):
        a = hrand(j, 5) * 2 * math.pi; sp = 300 + 700 * hrand(j, 6)
        r0 = sp * eout(k); r1 = sp * eout(max(0, k - .07))
        x0, y0 = cx + math.cos(a) * r1, cy + math.sin(a) * r1 * 1.1
        x1, y1 = cx + math.cos(a) * r0, cy + math.sin(a) * r0 * 1.1
        d.line((x0 / 2, y0 / 2, x1 / 2, y1 / 2), fill=int(255 * (1 - k) ** 1.5), width=2 if j % 3 == 0 else 1)
    g = lay.filter(ImageFilter.GaussianBlur(.9)).resize((W, H), Image.BILINEAR)
    s = Image.new('RGBA', (W, H), (225, 215, 255, 0)); s.putalpha(g); img.alpha_composite(s)


# ================================================================ captions (own, voice-synced)
PAGES = [([('THAT\'S', W_THATS), ('WHY', W_WHY)], W_THATS - .04, W_WE - .04),
         ([('WE', W_WE), ('CREATED', W_CREATED)], W_WE - .04, CONV0 + .1)]


def captions(ctx, t, y=1420, base=92):
    for words, a, z in PAGES:
        if not a <= t < z: continue
        ims = [E.word_img(w, base, 'white')[0] for w, _ in words]
        gap = base * .36; widths = []
        for w, _ in words:
            l, tp, r, b = E.font(base).getbbox(w); widths.append(r - l)
        x = W / 2 - (sum(widths) + gap * (len(words) - 1)) / 2
        for (w, t0), im, ww in zip(words, ims, widths):
            if t >= t0 - .02:
                lt = t - t0 + .02; s = .72 + .28 * back(lt / .16)
                al = clamp(lt / .05) * clamp((z - t) / .06)
                ctx.add('screen', im if abs(s - 1) < .01 else im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR),
                        x + ww / 2, y, alpha=al)
            x += ww + gap


# ================================================================ draw
END_CAM = dict(z=1.36, x=540., y=800., dx=0., dy=0., rot=0.)   # resolve framing (s09 opens at z 1.12)


def draw(ctx, lt, t):
    ctx.captions = False
    ctx.post['rgb'] = 0.
    captions(ctx, t)

    if t < RES0:
        # founder framing inside the prisms: centred, slow push
        ctx.cam = dict(z=1.2 + .08 * smooth(lt / 1.6), x=540., y=800., dx=0., dy=0., rot=0.)
        ctx.avatar.update(s=1.0, x=0.)
        ctx.bg_dim = .1 + .2 * smooth((t - W_THATS) / .6)

    if t < W_THATS - .04:
        # ---- the silent beat: 7 seams glint (soft travelling specular, no hard lines)
        def wrap(fr):
            k = smooth((t - 35.12) / .2)
            if k <= 0: return fr
            a = np.asarray(fr.convert('RGB'), np.float32).copy()
            yy = np.arange(H, dtype=np.float32)
            for i in range(1, N):
                x = int(i * SW); yc = (H * (.2 + .6 * hrand(i, 7)) + (t - 35.12) * 1800 * (1 if i % 2 else -1)) % H
                g = (np.exp(-((yy - yc) / 260) ** 2) * .85 + .1) * k
                for dx, f in ((-2, .25), (-1, .7), (0, 1.0), (1, .45)):
                    a[:, x + dx] += (255 - a[:, x + dx]) * (g * f)[:, None] * .8
            return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
        ctx.wrap = wrap
        return

    if t < HIT:
        # ---- prisms
        def wrap(fr):
            out = render_slats(fr, t, space_frame(t))
            return light_burst(out, t)
        if t >= CONV0 + .1:      # founder no longer visible: skip the world render
            ctx.full = space_base()
        ctx.wrap = wrap
        ctx.post['vignette'] = .45
        cv = ein((t - CONV0) / (HIT - CONV0))
        ctx.post['zoom_blur'] = .5 * cv
        return

    # ---- logo moment
    k_res = expo((t - RES0) / (RES1 - RES0 - .02))
    lx, ly = LCX, lerp(LCY, 252, k_res)
    lsc = lerp(1.0 + .14 * (1 - expo((t - HIT) / .35)) + .03 * smooth((t - HIT) / .4), 300 / LOGO_W, k_res)

    def wrap(fr):
        if t < RES0:
            out = space_frame(t, burst=.9 * eout((t - HIT) / .7))
        else:
            out = render_slats(fr, t, space_frame(t, burst=.9))
        sparks(out, t, LCX, LCY)
        out = shock(out, t, LCX, LCY)
        # bloom + logo
        bl = logo_bloom(); bs = lsc
        ba = (1.0 + 2.0 * (1 - eout((t - HIT) / .45))) * (1 - .6 * k_res)
        bim = bl if abs(bs - 1) < .01 else bl.resize((int(bl.width * bs), int(bl.height * bs)), Image.BILINEAR)
        for _ in range(int(ba)): out.alpha_composite(bim, (int(lx - bim.width / 2), int(ly - bim.height / 2)))
        fr_ = ba - int(ba)
        if fr_ > .02: out.alpha_composite(E.fade(bim, fr_), (int(lx - bim.width / 2), int(ly - bim.height / 2)))
        lg = logo_slices(t)
        sk = (t - (HIT + .1)) / .32
        if 0 < sk < 1: lg = sheen(lg, sk)
        if abs(lsc - 1) > .01: lg = lg.resize((int(lg.width * lsc), int(lg.height * lsc)), Image.LANCZOS)
        out.alpha_composite(lg, (int(lx - lg.width / 2), int(ly - lg.height / 2)))
        return light_burst(out, t)

    if t < RES0:
        ctx.full = space_base()
    else:
        ctx.cam = dict(END_CAM); ctx.avatar.update(s=1.0, x=0.)
        ctx.bg_dim = .1 * (1 - k_res)
    ctx.wrap = wrap
    ctx.post['vignette'] = .45 - .13 * k_res
    if t < HIT + 1 / 30: ctx.post['bright'] = 1.22          # peak frame only
