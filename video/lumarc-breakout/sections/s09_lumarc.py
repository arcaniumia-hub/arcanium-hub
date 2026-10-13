"""s09 — "That's what we build at LUMARC." (TL16, 19.96–22.04)

Callback to the shatter (s04): the glass that broke comes BACK and BUILDS the brand.
19.96  JUMP CUT -> wide framing (z 1.0, slow push). Glass shards rush back in from behind the lens (huge, defocused,
       motion-blurred), receding into the studio, decelerating into a loose EXPLODED VIEW of a smoked-glass pane hovering
       behind his head (each piece displaced out from its slot and toward camera, slowly turning, catching glints).
20.57  "WE" — the exploded view starts to collapse: outer pieces first.
20.76  "BUILD" — the pieces snap into their slots in a wave from the outer edge in (each landing = a click + a light
       kiss on the piece), converging on the glint of the LUMARC rings.
21.23  "LUMARC" (measured onset) — the last piece slams home exactly on the downbeat: light floods every seam, a star
       flare bursts from the glint, the logo ignites (violet bloom), the studio wall and his hair catch its light,
       camera kick + boom. The seams heal fast (one clean pane by ~21.40).
21.37  "lu-MARC" stress — a light sweep runs across the logo and the glass.
21.5   Hold: him + the glowing LUMARC pane behind his head, slow push. Hand-off (jump cut) to s10 at 22.04.
Captions: own (engine style) "THAT'S WHAT" / "WE BUILD" / "AT" — the word LUMARC is the logo itself.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _glasskit as GK
from sections import _E_kit as K

START, END = E.span(16, 16)                       # 19.96 – 22.04
W, H = E.W, E.H
clamp, lerp, smooth, expo, kick = E.clamp, K.lerp, K.smooth, K.expo, K.kick

# word onsets measured on src/tight16k.raw (10 ms RMS + <600 Hz / >3.5 kHz band energies):
# "that's" voicing 20.06 ("ts" 20.31-20.37) | "what" w 20.42 | t-closure 20.53-20.56, "we" 20.57 | b-burst 20.76 |
# d-release 21.01, "at" 21.11 | t-closure 21.19-21.22, "lu" voicing 21.23, "MAR" stressed vowel 21.37, k-burst 21.88
WORD_FIX = {(16, "THAT'S"): 20.06, (16, 'WHAT'): 20.42, (16, 'WE'): 20.57, (16, 'BUILD'): 20.76, (16, 'AT'): 21.11,
            (16, 'LUMARC.'): 21.23}
W_THATS, W_WHAT, W_WE, W_BUILD, W_AT, W_LUM = 20.06, 20.42, 20.57, 20.76, 21.11, 21.23
W_MARC = 21.37
T0 = START
SNAP0 = 20.80                                      # first piece lands (just after the b-burst of BUILD)
SNAP_D = .24                                       # each piece's snap duration (accelerating into its slot)

# ---------------------------------------------------------------- geometry
FOC = 1600.0
VP = (540.0, 820.0)
Z_HIM = 1330.0                                     # his depth (the pane sits behind him at Z = FOC)
PCX, PCY, PW, PH = 540, 368, 880, 330
RX0, RY0 = PCX - PW // 2, PCY - PH // 2            # pane top-left (world)
RECT = (RX0, RY0, RX0 + PW, RY0 + PH)
LOGO_W = 660
def logo(): return E.logo(LOGO_W)
LOGO_H = 225
LX0, LY0 = PCX - LOGO_W // 2, PCY - LOGO_H // 2   # logo top-left (world)
IMPACT = (LX0 + .152 * LOGO_W, LY0 + .505 * LOGO_H)   # the glint where the two rings cross (~ (310, 368))
BG_BLUR, BG_DIM = 1.4, .16

CUES = [
    (START, 'whoosh', {'gain': -5}),                         # the glass rushes back past the lens
    (START + .02, 'glass', {'seed': 9, 'gain': -7}),
    (W_WHAT + .02, 'shimmer', {'gain': -17}),                # the exploded view hangs, glinting
    (W_WE, 'glass', {'seed': 3, 'gain': -11}),               # the collapse starts
] + [(t, 'click', {'gain': g}) for t, g in ((20.80, -3), (20.86, -2), (20.93, -1), (20.97, 0), (21.03, 1), (21.08, 2), (21.12, 3), (21.17, 4))] + [
    (W_LUM, 'boom', {'gain': -1}),                           # last piece slams home: downbeat
    (W_LUM, 'impact', {'gain': -6}),
    (W_LUM + .01, 'shimmer', {'gain': -5}),
    (W_MARC, 'glass', {'seed': 5, 'gain': -9, 'pan': .2}),   # light sweep
]


# ---------------------------------------------------------------- art
def studio_graded():
    def mk():
        bg = E.studio().filter(ImageFilter.GaussianBlur(BG_BLUR))
        return Image.blend(bg, Image.new('RGB', bg.size, (0, 0, 0)), BG_DIM)
    return K.C(('s09_bg',), mk)


def pane_mask():
    def mk():
        S = 3; m = Image.new('L', (PW * S, PH * S)); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW * S - 1, PH * S - 1), 34 * S, fill=255)
        return m.resize((PW, PH), Image.LANCZOS)
    return K.C('s09_pmask', mk)


def pane_art():
    """the smoked-glass pane as it looks in place (RGB, pane size): the studio frosted through dark glass, a cool
    top sheen, a bevel highlight and the LUMARC logo printed in it (pre-ignition brightness)."""
    def mk():
        bg = studio_graded().crop(RECT).filter(ImageFilter.GaussianBlur(20))
        a = np.asarray(bg, np.float32)
        a = a * .42 + np.array([14, 11, 30], np.float32) * .58                         # smoked violet glass
        y = np.linspace(0, 1, PH, dtype=np.float32)[:, None, None]
        x = np.linspace(0, 1, PW, dtype=np.float32)[None, :, None]
        a = a + (1 - y) ** 2.2 * 26 + np.exp(-((x * .9 + y * .5 - .35) / .10) ** 2) * 10   # top sheen + faint diagonal reflection
        a = a + np.exp(-((y - .86) / .07) ** 2) * np.array([70, 40, 150], np.float32) * .35      # the monitors' glow on the lower lip
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
        # bevel: lit top edge, darker bottom edge, thin outer rim
        S = 3; e = Image.new('L', (PW * S, PH * S)); ImageDraw.Draw(e).rounded_rectangle((0, 0, PW * S - 1, PH * S - 1), 34 * S, outline=255, width=4 * S)
        e = np.asarray(e.resize((PW, PH), Image.LANCZOS), np.float32) / 255
        lit = (1 - y[..., 0]) ** 1.5 * .95 + .18
        b = np.asarray(im, np.float32)
        b[..., :3] = b[..., :3] * (1 - e[..., None] * .5) + e[..., None] * lit[..., None] * np.array([225, 220, 255], np.float32) * .85
        im = Image.fromarray(np.clip(b, 0, 255).astype(np.uint8), 'RGBA')
        lg = K.scale_im(logo(), 1.0)
        al = np.asarray(lg, np.float32); al[..., :3] *= .80
        im.alpha_composite(Image.fromarray(al.astype(np.uint8), 'RGBA'), (LX0 - RX0, LY0 - RY0))
        return im.convert('RGB')
    return K.C('s09_pane', mk)


def glass_tex():
    """full-frame RGB texture the shards carry (world coordinates): the pane art at its place."""
    def mk():
        im = studio_graded().copy(); im.paste(pane_art(), (RX0, RY0)); return im
    return K.C('s09_gtex', mk)


# ---------------------------------------------------------------- the assembly (reverse-time shard flight)
def _group(i, j, k):
    if j <= 1: return ('a', k // 3)                   # crushed centre: a few wedges
    return ('c', i)


class Assembly(GK.Shatter):
    """GK.Shatter pieces with an authored flight (keyframed in screen position + depth, so the composition is
    controlled): from right in front of the lens -> exploded view around the pane -> snap into the slot."""
    def pose(self, s, tau):
        t = tau
        x = clamp((t - T0) / .62); g = (1 - x) ** 3                                  # rush in from the lens, decelerating
        if t >= s['tl']: h = 0.0
        elif t <= s['ts']: h = 1.0
        else:
            u = (t - s['ts']) / (s['tl'] - s['ts']); h = 1 - u ** 2.2              # accelerate into the slot (slam)
        th = s['om'] * (t - T0)                                                     # slow swirl of the exploded view
        hx, hy = s['hov']
        hxr = hx * math.cos(th) - hy * math.sin(th); hyr = hy * math.cos(th) + hx * math.sin(th)
        bob = math.sin(2.1 * (t - T0) + s['ph']) * 7
        cx, cy = s['c']
        sx = cx + hxr * h + (s['far'][0] - (cx + hx)) * g
        sy = cy + (hyr + bob) * h + (s['far'][1] - (cy + hy)) * g
        Z = FOC + (s['z1'] - FOC) * h + (s['z0'] - s['z1']) * g
        X = (sx - VP[0]) * Z / FOC; Y = (sy - VP[1]) * Z / FOC
        ang = s['af'] * g + (s['ac'] + .10 * math.sin(1.7 * (t - T0) + s['ph'])) * h
        R = GK.axis_angle(s['axis'], ang) if abs(ang) > 1e-5 else np.eye(3)
        return np.array([X, Y, Z]), R, max(0.0, t - T0)


def assembly():
    def mk():
        F = GK.Fracture(center=IMPACT, size=(W, H), seed=33, radials=12, rings=[20, 52, 100, 165, 245, 340, 450, 570, 700],
                        hits=[(0.0, 6, 12, .5, .01)])
        S = Assembly(F, seed=8, focal=FOC, vp=VP, rect=RECT, group=_group, wave=20000.)
        rng = np.random.default_rng(17)
        dmax = max(s['dist'] for s in S.shards); dmin = min(s['dist'] for s in S.shards)
        for s in S.shards:
            cx, cy = s['c']; r = (s['dist'] - dmin) / (dmax - dmin)
            # landing: outer pieces first, the piece on the glint last = exactly on "LUMARC"
            s['tl'] = W_LUM - (W_LUM - SNAP0) * min(1.0, r ** .75 * 1.04) + rng.uniform(-.012, .012) * (r > .05)
            s['tl'] = min(W_LUM, s['tl'])
            s['ts'] = s['tl'] - SNAP_D * (.8 + .4 * rng.random())
            # far start (t = 19.96): a third right in front of the lens (huge, defocused) spread over the frame,
            # the rest mid-air below / around him
            if rng.random() < .46:
                s['z0'] = rng.uniform(200, 520); s['far'] = (rng.uniform(-60, 1140), rng.uniform(-60, 600))
            else:
                s['z0'] = rng.uniform(520, 1250)
                side = -1 if cx < 540 else 1
                s['far'] = (540 + side * rng.uniform(330, 760), rng.uniform(150, 880))
            # exploded view: out from the glint (screen px) + toward the camera (outer pieces more)
            dx, dy = s['dir']
            out = 55 + 230 * r + rng.uniform(-15, 30)
            s['hov'] = (dx * out * .78 + rng.uniform(-22, 22), dy * out * 1.15 + rng.uniform(-22, 22) - 30 * r)
            s['z1'] = FOC - rng.uniform(60, 220) * (.3 + .7 * r)
            s['om'] = rng.uniform(.06, .16) * rng.choice([-1, 1])
            s['af'] = rng.uniform(2.5, 5.0) * rng.choice([-1, 1])
            s['ac'] = rng.uniform(.22, .55) * rng.choice([-1, 1])
            ax = rng.normal(0, 1, 3); ax[2] *= .45; s['axis'] = ax / np.linalg.norm(ax)
            s['ph'] = rng.uniform(0, 6.3)
        # per-pixel maps over the pane: landing time of the piece covering it, seams (outline of every piece)
        tl = Image.new('F', (PW, PH), 99.0); sm = Image.new('F', (PW, PH), 99.0)
        dl, ds = ImageDraw.Draw(tl), ImageDraw.Draw(sm)
        for s in sorted(S.shards, key=lambda s: -s['tl']):
            for poly in s['polys']:
                dl.polygon([(x - RX0, y - RY0) for x, y in poly], fill=float(s['tl']))
        for s in sorted(S.shards, key=lambda s: -s['tl']):
            for poly in s['polys']:
                pts = [(x - RX0, y - RY0) for x, y in poly]
                ds.line(pts + [pts[0]], fill=float(s['tl']), width=1)
        TL = np.asarray(tl, np.float32).copy(); SM = np.asarray(sm, np.float32).copy()
        pm = np.asarray(pane_mask(), np.float32) / 255
        from scipy.ndimage import minimum_filter
        SM[~(minimum_filter(pm, size=7) > .5)] = 99.0          # no seams on the pane's own outer border
        return S, TL, SM
    return K.C('s09_asm', mk)


def pane_layer(t):
    """the part of the pane already assembled (RGBA, pane size) with landing kisses and seams."""
    S, TL, SM = assembly()
    landed = TL <= t
    if not landed.any(): return None
    art = np.asarray(pane_art(), np.float32)
    pm = np.asarray(pane_mask(), np.float32) / 255
    rgb = art.copy()
    # light kiss on each piece as it lands
    kiss = np.clip(1 - (t - TL) / .11, 0, 1) * landed
    if kiss.max() > 0: rgb += (255 - rgb) * (kiss * .30)[..., None]
    # seams: dark fissure + lit edge; flood with light at the slam, heal afterwards
    sv = (SM <= t).astype(np.float32)
    if t >= W_LUM:
        heal = 1 - smooth((t - W_LUM - .02) / .15)          # the seams flood with light, then heal fast (clean logo)
        flood = math.exp(-(t - W_LUM) / .05)
    else:
        heal, flood = 1.0, 0.0
    if heal > .01 and sv.any():
        from scipy.ndimage import gaussian_filter
        seam = gaussian_filter(sv, .6) * heal
        rgb = rgb * (1 - seam[..., None] * .45) + seam[..., None] * np.array([210, 205, 255], np.float32) * (.22 + 1.6 * flood)
        if flood > .02:
            gl = gaussian_filter(sv, 4.0) * 1.6 * flood * heal
            rgb = rgb + gl[..., None] * np.array([150, 120, 255], np.float32)
    a = landed * pm
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def shards_layers(t):
    """in-flight pieces split by depth: (behind him, in front of him) full-frame RGBA or None."""
    S, TL, SM = assembly()
    fly = [s for s in S.shards if t < s['tl']]
    if not fly: return None, None
    zs = {s['i']: S.pose(s, t)[0][2] for s in fly}
    out = []
    for front in (False, True):
        sel = [s for s in fly if (zs[s['i']] < Z_HIM) == front]
        if not sel: out.append(None); continue
        ids = {s['i'] for s in sel}
        canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        def ia(s, u):        # printed image strength: near the lens a piece is clear glass; in the exploded view smoked glass
            return clamp((zs[s['i']] - 420) / 650) * .9 + .1 * clamp((t - s['ts']) / .1)
        img = S.render(canvas, glass_tex(), t, dz=0.0, focus_z=FOC, dof=4.0, shutter_dtau=1 / 60, near=80,
                       cull_scale=14.0, keep=lambda s: s['i'] in ids, img_alpha=ia, spec_gain=.8,
                       alpha_fn=lambda s, u: .42 + .58 * clamp((zs[s['i']] - 300) / 800))
        out.append(img)
    return out[0], out[1]


# ---------------------------------------------------------------- ignition
def ign(t):
    """0 before the slam; spikes to 1 then settles to a steady .62."""
    if t < W_LUM: return 0.0
    e = t - W_LUM
    return .62 + .38 * math.exp(-e / .16)


def logo_glow():
    return K.glow_of('s09_lg', logo(), layers=((46, (96, 70, 255), 1.2), (14, (160, 140, 255), 1.0), (3, (235, 230, 255), .7)), pad=120)


def flare(t):
    """anamorphic star flare at the glint (RGBA, centred) or None."""
    if t < W_LUM - .01: return None
    e = t - W_LUM
    k = math.exp(-e / .12) * 1.0 + .22 + .06 * math.sin(e * 7)
    st = GK.star(64, 8)
    sz = int(150 + 260 * math.exp(-e / .10)) | 1
    im = st.resize((int(sz * 1.9), sz), Image.BILINEAR)
    return E.fade(im, min(1.0, k))


def halo():
    def mk():
        w, h = 1500, 900
        y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]; x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
        r = np.sqrt(x * x + y * y)
        a = np.clip(1 - r, 0, 1) ** 1.9 * .85 + np.exp(-(y / .035) ** 2) * np.clip(1 - np.abs(x), 0, 1) ** 2 * .35   # + anamorphic streak
        im = Image.new('RGBA', (w, h), (104, 78, 255, 0)); im.putalpha(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)))
        return im
    return K.C('s09_halo', mk)


def sweep_layer(t):
    """broad diagonal light band across the glass (RGBA pane size) on the MARC stress."""
    k = (t - W_MARC) / .42
    if not 0 < k < 1: return None
    xx = np.arange(PW, dtype=np.float32)[None, :] + np.arange(PH, dtype=np.float32)[:, None] * .55
    c = lerp(-200, PW + PH * .55 + 200, K.eio(k))
    band = np.clip(1 - np.abs(xx - c) / 90, 0, 1) ** 2 * .22 * K.bump(k, 0, 1) ** .5
    pm = np.asarray(pane_mask(), np.float32) / 255
    im = Image.new('RGBA', (PW, PH), (240, 238, 255, 0)); im.putalpha(Image.fromarray((band * pm * 255).astype(np.uint8)))
    return im


def logo_layer(t):
    """ignited logo over the assembled pane (RGBA, logo size + glow padding) — sheen on MARC."""
    if t < W_LUM: return None
    lg = logo()
    k = (t - (W_MARC - .02)) / .5
    if 0 < k < 1: lg = K.sheen(lg, k, K.ink_mask('s09_logo', logo(), 90, 200), 34, .62)
    return lg


# ---------------------------------------------------------------- camera
def camera(t):
    lt = t - START
    z = 1.0 + .05 * smooth(lt / 2.08) + .028 * kick(t - W_LUM, .16) * (t >= W_LUM)
    dy = 0.0; rot = 0.0
    if t >= W_LUM:
        e = t - W_LUM; dy = 7 * math.exp(-e / .09) * math.sin(e * 2 * math.pi * 9); rot = .0016 * math.exp(-e / .1) * math.sin(e * 40)
    return dict(z=z, x=540., y=820., dx=0., dy=dy, rot=rot)


CAP = [
    ([("THAT'S", W_THATS, 'white'), ('WHAT', W_WHAT, 'white')], W_THATS - .04, W_WE - .02),
    ([('WE', W_WE, 'white'), ('BUILD', W_BUILD, 'white')], W_WE - .04, W_AT - .02),
    ([('AT', W_AT, 'white')], W_AT - .04, W_LUM + .22),
]


def draw(ctx, lt, t):
    ctx.captions = False
    ctx.cam = camera(t)
    ctx.bg_img = studio_graded()
    g = ign(t)
    # light of the logo on the wall behind the pane
    if g > 0:
        ctx.add('behind', halo(), PCX, PCY + 20, alpha=min(1.0, g * .95))
    # assembled part of the pane
    pl = pane_layer(t)
    if pl is not None:
        ctx.add('behind', pl, RX0, RY0, center=False)
    if t >= W_LUM:
        gl = logo_glow(); ctx.add('behind', gl, PCX, PCY, alpha=min(1.0, .55 + .9 * (g - .62) / .38 * .6 + .15))
        ctx.add('behind', logo_layer(t), LX0, LY0, center=False)
        sw = sweep_layer(t)
        if sw is not None: ctx.add('behind', sw, RX0, RY0, center=False)
        fl = flare(t)
        if fl is not None: ctx.add('behind', fl, IMPACT[0], IMPACT[1])
    # pieces still flying
    b, f = shards_layers(t)
    if b is not None: ctx.add('behind', b, 0, 0, center=False)
    if f is not None: ctx.add('front', f, 0, 0, center=False)
    # the logo's light on his hair / shoulders
    if g > 0: K.top_light(ctx, (170, 150, 255), .75 * g, y0=560, y1=1100, rim=1.0, broad=.10)
    for words, a, z in CAP:
        K.pop_words(ctx, t, words, a, z, y=1440)
    P = ctx.post
    P['vignette'] = .36
    if W_LUM <= t < W_LUM + .07: P['rgb'] = 3.0
