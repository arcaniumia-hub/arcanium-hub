"""s09 — "That's what we build at LUMARC." (TL16, 19.96–22.04)  THE BRAND MOMENT

Callback to the shatter (s04): the glass he broke comes BACK as light and BUILDS the brand — a BIG LUMARC logo across
the monitors right behind him (text-behind-person: his crown just tucks over the wordmark's baseline), 880 px wide,
inside the safe area (x 100–980, y ≈ 420–720), never under the Reels header. The glass is the LOGO itself: two
fractures (the rings break around their glint, the wordmark around its own centre) and only the pieces carrying ink
are kept, so the pieces hug the logo (no rectangular pane) and the glass burns off at the slam.
19.96  JUMP CUT -> wide (z 1.0, slow push centred on the logo). Luminous glass shards (bright lit bevels, purple / blue
       monitor rims, glints, the logo's own light inside the pieces) rush back in from behind the lens — huge,
       defocused, motion-blurred — and decelerate into an EXPLODED VIEW of the logo hovering behind his head: every
       piece lifted out of its slot toward the camera and slowly turning; the pieces that carry the rings / wordmark
       glow, so "lumarc" already reads in pieces.
20.57  "WE" — the exploded view draws in (pieces drift back toward their slots).
20.76  "BUILD" — the pieces snap home in a wave from the outer edge in (each landing = a click + a light kiss + a
       glint), converging on the glint where the rings cross.
21.23  "LUMARC" (measured onset) — the last piece slams home on the downbeat: light floods every seam, star flare from
       the glint, the logo ignites (violet bloom, halo on the wall), the glass burns off into light leaving only the
       logo, his hair and shoulders catch its light, camera kick + boom.
21.37  "lu-MARC" stress — a light sweep runs across the logo.
21.5   Hold: him + the big glowing LUMARC behind his head, slow push. Hand-off (jump cut) to s10 at 22.04.
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
RUSH_D = .58                                       # the pieces' flight in from the lens (decelerating)
SNAP0 = 20.80                                      # first piece lands (just after the b-burst of BUILD)
SNAP_D = .24                                       # each piece's snap duration (accelerating into its slot)

# ---------------------------------------------------------------- geometry (world px; camera z 1.00 -> 1.04 around CAM)
FOC = 1600.0
LOGO_W = 880
def logo(): return E.logo(LOGO_W)
LOGO_H = int(218 * LOGO_W / 640)                   # 299
LCX, LCY = 540, 568
LX0, LY0 = LCX - LOGO_W // 2, LCY - LOGO_H // 2    # (100, 419): wordmark baseline y ≈ 632, his crown ≈ 622
PW, PH = 968, 372                                  # the glass the pieces come from (clear; burns off at the slam)
RX0, RY0 = LCX - PW // 2, LCY - PH // 2
IMPACT = (LX0 + 95 / 640 * LOGO_W, LY0 + 113 / 218 * LOGO_H)   # the glint where the two rings cross (~ (231, 574))
VP = (540.0, 640.0)
Z_HIM = 1330.0                                     # his depth (the logo plane sits behind him at Z = FOC)
CAM = (540., 596.)
BG_BLUR, BG_DIM = 1.6, .30
HEAD = (360, 560, 720, 900)                        # where his head is (world): pieces there stay behind him

CUES = [
    (START, 'whoosh', {'gain': -5}),                         # the glass rushes back past the lens
    (START + .02, 'glass', {'seed': 9, 'gain': -7}),
    (W_WHAT + .02, 'shimmer', {'gain': -15}),                # the exploded view hangs, glinting
    (W_WE, 'glass', {'seed': 3, 'gain': -11}),               # it draws in
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
    return K.C(('s09v2_bg',), mk)


def ink_zone():
    """where the glass exists (pane coords, bool): the logo's ink dilated by ~16 px — the pieces hug the logo (no
    rectangular pane: it is the LOGO that was broken)."""
    def mk():
        from scipy.ndimage import binary_dilation
        a = np.asarray(logo_ink().getchannel('A'), np.float32) / 255 > .10
        return binary_dilation(a, iterations=16)
    return K.C('s09v2_zone', mk)


def pane_mask():
    """AA union of the kept pieces (pane size, 0..1)."""
    def mk():
        S, TL, SM = assembly(); Sx = 3
        m = Image.new('L', (PW * Sx, PH * Sx)); d = ImageDraw.Draw(m)
        for s in S.shards:
            for poly in s['polys']: d.polygon([((x - RX0) * Sx, (y - RY0) * Sx) for x, y in poly], fill=255)
        return np.asarray(m.resize((PW, PH), Image.LANCZOS), np.float32) / 255
    return K.C('s09v2_pmask', mk)


def pane_edge():
    """the outer bevel of the assembled glass (pane size, 0..1) + how lit each part of it is (top-left key)."""
    def mk():
        from scipy.ndimage import minimum_filter, gaussian_filter
        pm = pane_mask()
        e = np.clip(pm - minimum_filter(pm, size=4), 0, 1)
        e = gaussian_filter(e, .5)
        y = np.linspace(0, 1, PH, dtype=np.float32)[:, None]; x = np.linspace(0, 1, PW, dtype=np.float32)[None, :]
        lit = np.clip(1.15 - y * .9 - x * .25, .25, 1)
        return e, lit
    return K.C('s09v2_pedge', mk)


def logo_ink():
    """the logo in its slot (pane size RGBA) — what the pieces carry (emissive)."""
    def mk():
        im = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); im.alpha_composite(logo(), (LX0 - RX0, LY0 - RY0)); return im
    return K.C('s09v2_ink', mk)


def glass_tex():
    """full-frame RGBA printed on the pieces: the logo (a touch hotter than at rest: it is light inside glass);
    alpha = its ink (the rest of every piece is clear glass)."""
    def mk():
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        a = np.asarray(logo(), np.float32).copy(); a[..., :3] = np.clip(a[..., :3] * 1.12 + 14, 0, 255)
        im.alpha_composite(Image.fromarray(a.astype(np.uint8), 'RGBA'), (LX0, LY0))
        return im
    return K.C('s09v2_gtex', mk)


# ---------------------------------------------------------------- the assembly (reverse-time shard flight)
def _group(i, j, k):
    if j <= 1: return ('a', k // 3)                   # crushed centre: a few wedges
    return ('c', i)


class Assembly(GK.Shatter):
    """GK.Shatter pieces with an authored flight (keyframed in screen position + depth, so the composition is
    controlled): from right in front of the lens -> exploded view of the logo -> snap into the slot."""
    def pose(self, s, tau):
        t = tau
        x = clamp((t - T0) / RUSH_D); g = (1 - x) ** 3                             # rush in from the lens, decelerating
        if t >= s['tl']: h = 0.0
        elif t <= s['ts']: h = 1.0
        else:
            u = (t - s['ts']) / (s['tl'] - s['ts']); h = 1 - u ** 2.2              # accelerate into the slot (slam)
        h *= 1 - .30 * smooth((t - W_WE) / .35)                                     # "WE": the exploded view draws in
        th = s['om'] * (t - T0)                                                     # slow swirl of the exploded view
        hx, hy = s['hov']
        hxr = hx * math.cos(th) - hy * math.sin(th); hyr = hy * math.cos(th) + hx * math.sin(th)
        bob = math.sin(2.1 * (t - T0) + s['ph']) * 6
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
        # two fractures: the rings mark breaks radially around its glint; the wordmark around its own centre (so no
        # long slivers run along the type), split at the gap between them; only the pieces carrying ink are kept
        XS = int(LX0 + 232 / 640 * LOGO_W)                  # the gap between the rings and the "l"
        F1 = GK.Fracture(center=IMPACT, size=(W, H), seed=33, radials=17, rings=[20, 48, 85, 128, 175, 228, 290],
                         hits=[(0.0, 6, 12, .5, .01)])
        WC = (LX0 + 420 / 640 * LOGO_W + 30, LY0 + 120 / 218 * LOGO_H)
        F2 = GK.Fracture(center=WC, size=(W, H), seed=41, radials=19, rings=[24, 58, 96, 138, 185, 236, 292, 352, 420],
                         hits=[(0.0, 6, 12, .5, .01)], split=.35)
        S = Assembly(F1, seed=8, focal=FOC, vp=VP, rect=(RX0, RY0, XS, RY0 + PH), group=_group, wave=20000.)
        S2 = Assembly(F2, seed=9, focal=FOC, vp=VP, rect=(XS, int(LY0 + 40 / 218 * LOGO_H), RX0 + PW, int(LY0 + 190 / 218 * LOGO_H)),
                      group=_group, wave=20000.)
        zone = ink_zone(); keep = []
        strong = np.asarray(logo_ink().getchannel('A'), np.uint8) > 20
        for k, s in enumerate(S.shards + S2.shards):        # only the pieces that carry part of the logo
            m = Image.new('1', (PW, PH)); d = ImageDraw.Draw(m)
            for poly in s['polys']: d.polygon([(x - RX0, y - RY0) for x, y in poly], fill=1)
            mb = np.asarray(m, bool)
            ov = int((mb & zone).sum())
            if ov >= max(180, .30 * s['area']) or int((mb & strong).sum()) >= 6:
                s['i'] = k; s['dist'] = math.hypot(s['c'][0] - IMPACT[0], s['c'][1] - IMPACT[1]) + 1
                keep.append(s)
        S.shards = keep
        rng = np.random.default_rng(17)
        dmax = max(s['dist'] for s in S.shards); dmin = min(s['dist'] for s in S.shards)
        for s in S.shards:
            cx, cy = s['c']; r = (s['dist'] - dmin) / (dmax - dmin)
            # landing: outer pieces first, the piece on the glint last = exactly on "LUMARC"
            s['tl'] = W_LUM - (W_LUM - SNAP0) * min(1.0, r ** .75 * 1.04) + rng.uniform(-.012, .012) * (r > .05)
            s['tl'] = min(W_LUM, s['tl'])
            s['ts'] = s['tl'] - SNAP_D * (.8 + .4 * rng.random())
            # far start (t = 19.96): a third right in front of the lens (huge, defocused) spread over the frame,
            # the rest mid-air around him, mostly off his face
            if rng.random() < .40:
                s['z0'] = rng.uniform(260, 560); s['far'] = (rng.uniform(-80, 1160), rng.uniform(-40, 760))
            else:
                s['z0'] = rng.uniform(560, 1250)
                side = -1 if cx < 540 else 1
                s['far'] = (540 + side * rng.uniform(380, 800), rng.uniform(120, 1000))
            # exploded view: lifted toward the camera (outer pieces more) and out from the logo's centre (screen px)
            in_head = HEAD[0] < cx < HEAD[2] and cy > HEAD[1]
            dz = rng.uniform(60, 140) + rng.uniform(60, 200) * r
            if in_head: dz = min(dz, 220)                                       # stays behind his head
            s['z1'] = FOC - dz
            sp = FOC / s['z1'] - 1
            s['hov'] = ((cx - LCX) * sp * 1.15 + rng.uniform(-14, 14), (cy - LCY) * sp * 1.6 + rng.uniform(-12, 12) - 10 * r)
            s['om'] = rng.uniform(.03, .08) * rng.choice([-1, 1])
            s['af'] = rng.uniform(2.5, 5.0) * rng.choice([-1, 1])
            s['ac'] = rng.uniform(.35, .80) * rng.choice([-1, 1])
            ax = rng.normal(0, 1, 3); ax[2] *= .35; s['axis'] = ax / np.linalg.norm(ax)
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
        from scipy.ndimage import minimum_filter
        um = np.asarray(tl, np.float32) < 98                          # union of the pieces
        SM[~minimum_filter(um, size=5)] = 99.0                        # no seams on the glass's own outer border
        return S, TL, SM
    return K.C('s09v2_asm', mk)


# ---------------------------------------------------------------- the assembled glass (static per-pixel layer)
def burn(t):
    """1 while the glass is assembled; burns off into light right after the slam (-> 0 by ~21.52)."""
    return 1.0 if t < W_LUM + .03 else 1 - smooth((t - W_LUM - .03) / .26)


def pane_layer(t):
    """the part of the glass already in place (RGBA, pane size): faint clear slab, glowing logo (pre-ignition), lit seams
    and bevel, a light kiss on every landing; at the slam the seams flood with light and the glass burns off."""
    S, TL, SM = assembly()
    landed = TL <= t
    if not landed.any(): return None
    b = burn(t)
    pm = pane_mask()
    from scipy.ndimage import gaussian_filter
    ink = np.asarray(logo_ink(), np.float32)
    ia = ink[..., 3] / 255
    logo_on = 1.0 if t < W_LUM else 1 - smooth((t - W_LUM) / .05)       # handed over to the ignited logo layer
    # 1 clear glass: a faint violet body + top sheen (alpha), lit bevel along the slab's outer edge
    y = np.linspace(0, 1, PH, dtype=np.float32)[:, None]
    body_a = (.07 + .10 * (1 - y) ** 2) * b
    col = np.zeros((PH, PW, 3), np.float32) + np.array([150, 140, 255], np.float32)
    A = np.broadcast_to(body_a, (PH, PW)).copy()
    e, lit = pane_edge()
    ea = np.clip(e * (.35 + .65 * lit) * 1.1 * b, 0, 1)
    col = col * (1 - ea[..., None]) + np.array([235, 232, 255], np.float32) * ea[..., None]; A = ea + A * (1 - ea)
    # 2 seams: lit hairlines between the pieces (rim light), flooding with light at the slam, then healing
    sv = (SM <= t).astype(np.float32)
    if t >= W_LUM:
        heal = 1 - smooth((t - W_LUM - .02) / .16); flood = math.exp(-(t - W_LUM) / .06)
    else:
        heal, flood = 1.0, 0.0
    if heal > .01 and sv.any():
        seam = np.clip(gaussian_filter(sv, .7) * 1.6, 0, 1) * heal
        sa = np.clip(seam * (.55 + .45 * flood), 0, 1)
        col = col * (1 - sa[..., None]) + np.array([205, 196, 255], np.float32) * (1 + .3 * flood) * sa[..., None]; A = sa + A * (1 - sa)
        gl = np.clip(gaussian_filter(sv, 3.5) * (.35 + 1.3 * flood) * heal, 0, 1)
        col = col * (1 - gl[..., None]) + np.array([150, 120, 255], np.float32) * gl[..., None]; A = gl + A * (1 - gl)
    # 3 the logo inside the glass, glowing (pre-ignition brightness)
    if logo_on > .01:
        la = ia * .92 * logo_on
        col = col * (1 - la[..., None]) + ink[..., :3] * 1.05 * la[..., None]; A = la + A * (1 - la)
    # 4 light kiss on each piece as it lands
    kiss = np.clip(1 - (t - TL) / .12, 0, 1) * landed
    if kiss.max() > 0:
        ka = kiss * .45
        col = col * (1 - ka[..., None]) + np.array([240, 236, 255], np.float32) * ka[..., None]; A = ka + A * (1 - ka)
    A = A * landed * pm
    if A.max() < .004: return None
    out = np.dstack([np.clip(col, 0, 255), np.clip(A * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


# ---------------------------------------------------------------- the flying pieces
GLASS_KW = dict(dof=3.0, near=90.0, glyph_alpha=1.0, img_alpha=0.0, veil=.30, env_col=(160, 140, 255), sheen=.9,
                reflect=.8, refl_cap=.38, env_q=2, env_pow=2.4, bevel=2.8, edge=1.1, rim=1.6,
                rim_cols=((196, 104, 255), (110, 150, 255)), edge_dark=.10, backlight=.45, back_col=(184, 150, 255),
                blur_cap=14.0, blur_fade=16.0, max_smear=10, smear_div=4.0, smear_soft=True, star_scale=4.0,
                star_gain=1.2, spec_gain=1.5, q_blur=5.0, tex_r_area=90000, thick=1.6, gloss=.5)


def _flying(t):
    S, TL, SM = assembly()
    return S, [s for s in S.shards if t < s['tl']]


def _alpha_near(S, zs):
    # near the lens a piece is a big defocused ghost: thin it so it never buries his face
    return lambda s, u: .35 + .65 * clamp((zs.get(s['i'], FOC) - 320) / 700)


def render_behind(base, t):
    """in-flight pieces BEHIND him, refracting the studio (RGBA world) -> RGBA."""
    S, fly = _flying(t)
    if not fly: return base
    zs = {s['i']: S.pose(s, t)[0][2] for s in fly}
    ids = {i for i, z in zs.items() if z >= Z_HIM}
    if not ids: return base
    return S.render_refract(base, glass_tex(), t, focus_z=FOC, shutter_dtau=1 / 60, cull_scale=12.0, refract=12.0,
                            absorb=.04, tint=(40, 30, 90), keep=lambda s: s['i'] in ids, alpha_fn=_alpha_near(S, zs), **GLASS_KW)


def render_front(t):
    """in-flight pieces IN FRONT of him (RGBA full frame or None) — no refraction (they are huge / defocused)."""
    S, fly = _flying(t)
    if not fly: return None
    zs = {s['i']: S.pose(s, t)[0][2] for s in fly}
    ids = {i for i, z in zs.items() if z < Z_HIM}
    if not ids: return None
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    return S.render_refract(canvas, glass_tex(), t, focus_z=FOC, shutter_dtau=1 / 60, cull_scale=12.0, refract=0.0,
                            keep=lambda s: s['i'] in ids, alpha_fn=_alpha_near(S, zs), **GLASS_KW)


def bloom(fr, base, k, col=(150, 132, 255)):
    """photographic bloom of what the glass ADDS over the world (hot bevels, glints, the logo's light) — computed at
    quarter res, added only over the rows it touches."""
    if k <= 0: return fr
    q = (W // 4, H // 4)
    a = np.asarray(fr.convert('RGB').resize(q, Image.BOX), np.int16); b = np.asarray(base.convert('RGB').resize(q, Image.BOX), np.int16)
    d = Image.fromarray(np.clip((a - b).max(2) * 1.15 - 26, 0, 255).astype(np.uint8))
    g = np.asarray(d.filter(ImageFilter.GaussianBlur(2.0)), np.float32) * 1.5 + np.asarray(d.filter(ImageFilter.GaussianBlur(7)), np.float32) * 1.5
    rows = np.nonzero(g.max(1) > 1.0)[0]
    if len(rows) == 0: return fr
    r0, r1 = max(0, rows[0] - 1), min(q[1], rows[-1] + 2)
    gb = Image.fromarray(np.clip(g[r0:r1], 0, 255).astype(np.uint8)).resize((W, (r1 - r0) * 4), Image.BILINEAR)
    gb = np.asarray(gb, np.float32)[..., None] / 255 * k * (np.array(col, np.float32) * .6)
    out = fr.copy(); y0, y1 = r0 * 4, r1 * 4
    band = np.asarray(out.crop((0, y0, W, y1)).convert('RGB'), np.float32) + gb
    out.paste(Image.fromarray(np.clip(band, 0, 255).astype(np.uint8)).convert('RGBA'), (0, y0))
    return out


def landing_glints(t):
    """a small star glint where each bigger piece clicks home (screen = world at the slot)."""
    S, TL, SM = assembly(); out = []
    for s in S.shards:
        e = t - s['tl']
        if not (0 <= e < .16) or s['area'] < 2500: continue
        k = math.exp(-e / .05) * min(1.0, s['area'] / 9000)
        # the slot corner nearest the key light
        pts = np.array(s['poly']); vi = int(np.argmin(pts[:, 0] * .55 + pts[:, 1] * .83))
        out.append((pts[vi, 0], pts[vi, 1], k))
    return out


# ---------------------------------------------------------------- ignition
def ign(t):
    """0 before the slam; spikes to 1 then settles to a steady .66."""
    if t < W_LUM: return 0.0
    e = t - W_LUM
    return .66 + .34 * math.exp(-e / .16)


def logo_glow():
    return K.glow_of('s09v2_lg', logo(), layers=((56, (96, 70, 255), 1.25), (16, (160, 140, 255), 1.0), (3, (235, 230, 255), .7)), pad=150)


def flare(t):
    """anamorphic star flare at the glint (RGBA, centred) or None."""
    if t < W_LUM - .01: return None
    e = t - W_LUM
    k = math.exp(-e / .12) * 1.0 + .22 + .06 * math.sin(e * 7)
    st = GK.star(64, 8)
    sz = int(170 + 300 * math.exp(-e / .10)) | 1
    im = st.resize((int(sz * 2.1), sz), Image.BILINEAR)
    return E.fade(im, min(1.0, k))


def halo():
    def mk():
        w, h = 1800, 1100
        y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]; x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
        r = np.sqrt(x * x + y * y)
        a = np.clip(1 - r, 0, 1) ** 1.9 * .85 + np.exp(-(y / .03) ** 2) * np.clip(1 - np.abs(x), 0, 1) ** 2 * .35   # + anamorphic streak
        im = Image.new('RGBA', (w, h), (104, 78, 255, 0)); im.putalpha(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)))
        return im
    return K.C('s09v2_halo', mk)


def scrim():
    """a soft shadow behind the wordmark (the hot monitors behind it are stopped down) so the thin type reads."""
    def mk():
        w, h = LOGO_W + 260, LOGO_H + 200
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((130, 100, w - 130, h - 100), 90, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(60))
        im = Image.new('RGBA', (w, h), (6, 4, 14, 0)); im.putalpha(m.point(lambda v: int(v * .55))); return im
    return K.C('s09v2_scrim', mk)


def sweep_k(t): return (t - (W_MARC - .02)) / .5


def logo_layer(t):
    """ignited logo (RGBA, logo size) — sheen on MARC."""
    if t < W_LUM: return None
    lg = logo()
    k = sweep_k(t)
    if 0 < k < 1: lg = K.sheen(lg, k, K.ink_mask('s09v2_logo', logo(), 90, 200), 40, .62)
    return lg


# ---------------------------------------------------------------- camera
def camera(t):
    lt = t - START
    z = 1.0 + .04 * smooth(lt / 2.08) + .03 * kick(t - W_LUM, .16) * (t >= W_LUM)
    dy = 0.0; rot = 0.0
    if t >= W_LUM:
        e = t - W_LUM; dy = 7 * math.exp(-e / .09) * math.sin(e * 2 * math.pi * 9); rot = .0016 * math.exp(-e / .1) * math.sin(e * 40)
    return dict(z=z, x=CAM[0], y=CAM[1], dx=0., dy=dy, rot=rot)


CAP = [
    ([("THAT'S", W_THATS, 'white'), ('WHAT', W_WHAT, 'white')], W_THATS - .04, W_WE - .02),
    ([('WE', W_WE, 'white'), ('BUILD', W_BUILD, 'white')], W_WE - .04, W_AT - .02),
    ([('AT', W_AT, 'white')], W_AT - .04, W_LUM + .22),
]


def world_behind(t):
    """everything behind him, in world space (RGB): graded studio, the logo's light on the wall, the assembled glass,
    the ignited logo, the pieces still flying behind him, bloom."""
    g = ign(t)
    w = studio_graded().convert('RGBA')
    sc = scrim(); E._paste(w, dict(img=E.fade(sc, .55 + .45 * smooth((t - SNAP0) / .4)), xy=(LCX - sc.width // 2, LCY - sc.height // 2 + 8), glass=0))
    if g > 0:
        hl = halo(); E._paste(w, dict(img=E.fade(hl, min(1.0, g * .95)), xy=(LCX - hl.width // 2, LCY + 20 - hl.height // 2), glass=0))
    base = w.copy()
    pl = pane_layer(t)
    if pl is not None: w.alpha_composite(pl, (RX0, RY0))
    if t >= W_LUM:
        gl = logo_glow(); a = min(1.0, .62 + .30 * (g - .66) / .34)
        E._paste(w, dict(img=E.fade(gl, a), xy=(LCX - gl.width // 2, LCY - gl.height // 2), glass=0))
        k = clamp((t - W_LUM) / .03)
        w.alpha_composite(E.fade(logo_layer(t), k) if k < 1 else logo_layer(t), (LX0, LY0))
    w = render_behind(w, t)
    for x, y, k in landing_glints(t):
        st = GK.star(48); sz = int(30 + 40 * k) | 1
        E._paste(w, dict(img=E.fade(st.resize((sz, sz), Image.BILINEAR), k), xy=(int(x - sz / 2), int(y - sz / 2)), glass=0))
    if t >= W_LUM:
        fl = flare(t)
        if fl is not None: E._paste(w, dict(img=fl, xy=(int(IMPACT[0] - fl.width / 2), int(IMPACT[1] - fl.height / 2)), glass=0))
    w = bloom(w, base, 1.0 if t < W_LUM else .7 + .25 * math.exp(-(t - W_LUM) / .15))
    return w.convert('RGB')


def draw(ctx, lt, t):
    ctx.captions = False
    ctx.cam = camera(t)
    ctx.bg_img = world_behind(t)
    f = render_front(t)
    if f is not None: ctx.add('front', f, 0, 0, center=False)
    # the logo's (and the glowing glass's) light on his hair / shoulders
    g = ign(t)
    pre = .22 * smooth((t - T0 - .25) / .4)
    if g > 0 or pre > 0: K.top_light(ctx, (170, 150, 255), max(pre, .85 * g), y0=560, y1=1100, rim=1.0, broad=.12)
    for words, a, z in CAP:
        K.pop_words(ctx, t, words, a, z, y=1440)
    P = ctx.post
    P['vignette'] = .36
    if W_LUM <= t < W_LUM + .07: P['rgb'] = 3.0
