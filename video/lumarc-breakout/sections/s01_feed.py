"""s01 — THE FEED (0.00–4.00): "Hey. / Yeah, you. / Down here. / Your content lives in here."

The film opens INSIDE the viewer's own Instagram feed (feedkit, pure screen pixels: no grain, no vignette, no camera).
Word onsets measured on src/tight16k.raw (10 ms RMS + band energies), not the syllable estimate:
  HEY 0.09 (voice .13) | YEAH .63  YOU .98 | DOWN 1.48  HERE 1.72 (h 1.71, vowel 1.78) |
  YOUR 2.28  CONTENT 2.52  LIVES 3.06  IN 3.32 (auto said 3.50)  HERE 3.54 (soft h from 3.46, vowel 3.62; tap 3.61)

  0.00  LOOP HANDSHAKE / THUMBNAIL: frame 0 is the first frame anyone sees (feed thumbnail), so it reads clean: his
        Reel post exactly centred in the feed, crisp. s10's motion-blurred thumb flick SNAPS onto it (whip-to-crisp)
        and the momentum carries the feed ~17 px past centre before it settles back (elastic catch, at rest by
        ~0.2 s). scroll(t) = S* + 40 e^(-14t) sin(22t), S* = 3745. Haptic tick on the snap.
        His live studio world plays inside the post; the like counter ticks, the Reel playhead bar runs along the
        bottom of the media (it IS this film's playhead), mute + reels badges. Captions are burned INSIDE his Reel.
  0.52  "Yeah, you." (jump cut = inner framing snaps tight on his face) — the phone screen slowly pushes in on the
        post and the rest of the feed dims; "YOU." (.98) gets a micro punch.
  1.40  "Down here." (jump cut = inner framing back to medium) — on DOWN the post's floor DROPS: his world falls
        back into a deep lit box behind the glass (perspective walls lit by his monitors' spill, glossy floor
        reflection, AO seams, glass rim); it lands with a thud + bounce on HERE. He is literally down in there.
  2.16  "Your content lives in here." (jump cut = new camera) — the phone screen is only a WINDOW on an endless
        WALL of feeds (his column + neighbouring feeds left/right, staggered): on CONTENT the app chrome retracts
        under the bezel (opaque wipe, never a ghost over post text) and the camera pulls back; on LIVES it cranes up
        and the wall tilts back into purple fog (perspective, mip-mapped depth of field, depth fog), infinite above,
        rushing past the lens below. His post is the light source: the other posts are unlit (exposure down, film
        shoulder on the whites, colour out — the loud tonys.pizza flyer above him near-monochrome), the wall falls off into darkness away from him, his light spills on the neighbours + lavender rim.
        On HERE (vowel 3.62) a knuckle tap from inside his post: refraction rings ON the glass of the wall only (never
        in the void), caustic crest, jolt, rim flare — foreshadows the knock at 7.08.
Captions: segs 0-2 burned inside his post (move/scale with it); seg 3 = engine-look captions on screen, page 1 riding
on his hoodie, page 2 on the photo of the post below his (never over any post's UI text), each on a soft dark scrim. All captions use the
measured ONSETS (K.draw_caps fix=) so they are right before the integrator merges them into WORD_FIX.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
import sections.feedkit as FK
from sections import _A_kit as K

START, END = E.span(0, 3)                                   # 0.00 – 4.00
T1, T2, T3 = E.TL[1]['t0'], E.TL[2]['t0'], E.TL[3]['t0']    # 0.52, 1.40, 2.16 (jump cuts)
# re-verified on src/tight16k.raw (10 ms RMS + 80-900 Hz / 2.5-8 kHz band energies):
#   HEY breath .08, voiced .13 | YEAH .63 | YOU .985 | DOWN 1.485 | HERE h 1.71, vowel 1.78 | YOUR 2.285 | CONTENT k-burst
#   2.52 | LIVES 3.06 | IN 3.32 (the z of "lives" 3.27-3.32, vowel 3.33) | HERE h 3.46 (long, soft), vowel 3.62
ONSETS = {(0, 'HEY.'): 0.09, (1, 'YEAH,'): 0.63, (1, 'YOU.'): 0.98, (2, 'DOWN'): 1.48, (2, 'HERE.'): 1.72,
          (3, 'YOUR'): 2.28, (3, 'CONTENT'): 2.52, (3, 'LIVES'): 3.06, (3, 'IN'): 3.32, (3, 'HERE.'): 3.54}
W_HEY, W_YOU, W_DOWN, W_HERE1 = .09, .98, 1.48, 1.72
W_YOUR, W_CONTENT, W_LIVES, W_HERE2 = 2.28, 2.52, 3.06, 3.54
T_LAND = 1.76                                               # the box floor lands (h 1.71 -> vowel 1.78 of "here")
T_TAP = 3.61                                                # knuckle tap from inside (vowel of "here" 3.62)

CUES = [(0.0, 'swipe', {'gain': -13}), (0.02, 'tick', {'gain': -11}),
        (T1, 'whoosh', {'gain': -14}), (W_YOU, 'thud', {'gain': -12}),
        (W_DOWN - .02, 'whoosh', {'gain': -6}), (T_LAND, 'thud', {'gain': -2}),
        (T3, 'swoosh_up', {'gain': -10}), (W_CONTENT, 'whoosh', {'gain': -5}), (W_LIVES, 'shimmer', {'gain': -12}),
        (T_TAP, 'knock', {'gain': -5}), (T_TAP + .01, 'glass', {'gain': -13})]

W, H = E.W, E.H
clamp, eout, lerp = E.clamp, E.eout, K.lerp
S_STAR = FK.center_scroll(FK.SPECIAL)                       # 3745: his media centred in the feed area
MY0 = K.special_top(S_STAR) + FK.HEAD_H                     # 305: media top on screen at rest
MCX, MCY = W / 2, MY0 + FK.MEDIA_H / 2                      # 540, 980
CAP_Y3 = 1450                                              # seg-3 screen captions (over his media in the window shot)
CAP_MY, CAP_MB = 1060, 64                                   # in-media caption centre / base size (media px)
CAP_SCRIM = .62                                             # soft dark scrim behind the seg-3 captions over the wall

# ---------------------------------------------------------------- loop handshake
# Frame 0 is the thumbnail / first frame anyone sees: it must read clean. s10's thumb flick (motion-blurred, ~12 000
# px/s) SNAPS onto his post on frame 0 — whip-to-crisp, the post exactly centred and sharp — and the momentum carries
# it ~17 px past centre before it settles back (elastic catch, at rest by ~0.2 s). Haptic tick on the snap.
B_SNAP, A_, W_ = 40., 14., 22.
def scroll_at(t):
    """o(0) = 0 (centred), o'(0) = +B*W (still moving up with the flick's momentum), damped back to rest."""
    return S_STAR + B_SNAP * math.exp(-A_ * t) * math.sin(W_ * t)
def scroll_vel(t):
    return B_SNAP * math.exp(-A_ * t) * (W_ * math.cos(W_ * t) - A_ * math.sin(W_ * t))


# ---------------------------------------------------------------- framing inside his Reel (world camera)
def inner_cam(t):
    if t < T1:     # medium (his own Reel framing), a slow living drift
        return dict(z=1.0 + .05 * K.smooth(t / T1), x=540., y=900., dx=0., dy=0.)
    if t < T2:     # "Yeah, you." tight on the face
        e = t - T1
        return dict(z=1.30 + .05 * K.smooth(e / .88), x=540., y=760., dx=0., dy=60. - 10 * K.smooth(e / .88))
    # "Down here." medium again (inside the box), a breath of push
    e = t - T2
    return dict(z=1.06 + .03 * K.smooth(e / .76), x=540., y=900., dx=0., dy=0.)


def shot_seg(t): return 0 if t < T1 else 1 if t < T2 else 2 if t < T3 else 3


def media_img(ctx, t):
    return FK.special_media(ctx, inner_cam(t)).convert('RGBA')


def caption_layer(t):
    """the captions burned into his Reel (transparent 1080x1350), cut with the shot."""
    ov = Image.new('RGBA', (FK.W, FK.MEDIA_H), (0, 0, 0, 0))
    K.draw_caps(ov, t, CAP_MY, CAP_MB, {shot_seg(t)}, fix=ONSETS); return ov


def finish_media(m, t):
    m = m.convert('RGBA'); m.alpha_composite(K.progress_bar(t / E.DUR), (0, FK.MEDIA_H - 6)); return m


# ---------------------------------------------------------------- the box depth ("down here")
FALL0 = W_DOWN - .02
def box_depth(t):
    """0 -> 1: the floor falls (gravity: accelerating) from DOWN and lands on HERE with a damped bounce."""
    if t < FALL0: return 0.0
    if t < T_LAND: return ((t - FALL0) / (T_LAND - FALL0)) ** 2
    e = t - T_LAND
    return 1.0 - .045 * math.exp(-e / .10) * math.sin(e * 30)
def _sb(d): return 1 - (1 - .62) * d                      # back-wall scale of the box at depth d (K.well sb_min=.62)
def fall_trail(t):
    """radial motion blur of the falling wall = its scale change over a 180-degree shutter (physically timed)."""
    if t < FALL0 or t > T_LAND + .2: return 0.0
    return max(0.0, _sb(box_depth(t - 1 / 60)) / _sb(box_depth(t)) - 1)


# ---------------------------------------------------------------- feed phase (0 – 2.16)
def _dim_mask():
    def mk():
        m = Image.new('L', (W, H)); ImageDraw.Draw(m).rectangle((0, MY0, W, MY0 + FK.MEDIA_H), fill=255)
        return m.filter(ImageFilter.GaussianBlur(10))
    return K.C('s01_dim', mk)


def push_amt(t):
    if t < T1: return 1.0
    p = 1 + .055 * K.eio((t - T1) / .85)
    p += .022 * math.sin(math.pi * clamp((t - W_YOU) / .22)) * (1 if t >= W_YOU else 0)     # micro punch on YOU
    if t >= T2:      # cut: back to the full post so the box reads as a hole in it, slow push toward it
        p = 1.0 + .03 * K.smooth((t - T2) / .76)
    return p


def dim_amt(t):
    if t < T1: return 0.0
    return .58 * K.eio((t - T1) / .35)


def feed_phase(ctx, t):
    if t < .5: s = scroll_at(t); v = scroll_vel(t)
    else: s = S_STAR; v = 0.0
    m = media_img(ctx, t); ov = caption_layer(t)
    if t >= T2: m = K.well(m, box_depth(t), trail=fall_trail(t), overlay=ov)
    else: m.alpha_composite(ov)
    m = finish_media(m, t)
    blurL = abs(v) / 60.0 if t >= .5 / E.FPS else 0.0     # 180-degree shutter; frame 0 (the snap) is crisp
    scr = K.feed(s, m, t, chrome=True, blurL=blurL)
    dim = dim_amt(t)
    if dim > .005:
        rgb = scr.convert('RGB'); k = 1 - dim
        scr = Image.composite(rgb, rgb.point(lambda v: int(v * k)), _dim_mask()).convert('RGBA')
    p = push_amt(t)
    sh = 0.0
    if t >= T_LAND:                                         # the landing thud shakes the phone
        e = t - T_LAND; sh = 11 * math.exp(-e / .07) * math.sin(e * 2 * math.pi * 11)
    if abs(p - 1) > .001 or abs(sh) > .3:
        scr = K.affine(scr.convert("RGB"), p, (MCX, MCY), (MCX, MCY + sh), (W, H), Image.BILINEAR).convert("RGBA")
    if T1 <= t < T1 + .75: scr = K.sheen(scr, (t - T1) / .75, .085)     # the glass catches the light as it pushes in
    return scr


# ---------------------------------------------------------------- column phase (2.16 – 4.00)
V_HIS = FK.post_top(FK.SPECIAL) + FK.HEAD_H + FK.MEDIA_H / 2          # plane anchor: centre of his media (content px)
CARD_IMG_H = FK.HEAD_H + FK.MEDIA_H + FK.ACT_H + FK.META_H            # card without the inter-post gap
WIN_V0 = S_STAR - FK.TOP_Y                                             # the phone viewport on the plane
TAP_U, TAP_V = 760., V_HIS + 250.                                      # knuckle point: lower right of his media (by his hand)
ORDER = [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]                    # feed posts other than his
GAP_U = 64.                                                            # gutter between neighbouring feeds of the wall
SIDE = [(-1, 760.), (1, -1010.)]                                       # neighbouring feeds: (side, vertical stagger)
NEXT_MEDIA_V = FK.post_top(FK.SPECIAL + 1) + FK.HEAD_H                 # the post under his (seg-3 captions sit on it)


def post_index(i):
    """posts above/below the real list repeat (endless feed); never a second copy of his."""
    if 0 <= i < len(FK.POSTS): return i
    return ORDER[(i * 5 + 3) % len(ORDER)]


def side_index(side, n):
    return ORDER[(n * 7 + (4 if side < 0 else 9)) % len(ORDER)]


def card_full(j):
    def mk():
        im = Image.new('RGBA', (W, CARD_IMG_H), FK.BG + (255,))
        im.alpha_composite(FK._head(j), (0, 0)); im.alpha_composite(FK._media(j), (0, FK.HEAD_H))
        im.alpha_composite(FK._foot(j).crop((0, 0, W, FK.ACT_H + FK.META_H)), (0, FK.HEAD_H + FK.MEDIA_H))
        return im
    return K.C(('s01_card', j), mk)


UNLIT = {1: (.06, .66, 1.45), None: (.34, .90, .62)}       # (saturation, exposure a, shoulder b) — flyer / others


def _unlit_lut(a, b):
    """film-like shoulder f(x) = a x / (1 + b x): an unlit print next to a light source — whites roll off hard (a
    white/cream post can never glow), shadows keep their detail, contrast drops with the exposure."""
    return [int(round(255 * a * (v / 255) / (1 + b * v / 255))) for v in range(256)] * 3


def card_muted(j):
    """the other posts as the camera sees them next to his glowing one: unlit (exposure down, highlights rolled off,
    colour pulled out) so HIS post is unmistakably the light source of the shot. The loud red/yellow tonys.pizza
    flyer that sits right above him is graded hardest: near-monochrome, its white paper ~26 % grey, its red type
    ~1.7:1 against it — still a photograph of a flyer, no longer a billboard."""
    def mk():
        s, a, b = UNLIT.get(j, UNLIT[None])
        im = K.desat(card_full(j), s).convert('RGB').point(_unlit_lut(a, b))
        return im.convert('RGBA')
    return K.C(('s01_unlit', j), mk)


def his_card(m, t):
    im = Image.new('RGBA', (W, CARD_IMG_H), FK.BG + (255,))
    im.alpha_composite(FK._head(FK.SPECIAL), (0, 0))
    mm = m.convert('RGBA'); mm.alpha_composite(FK._reel_overlay()); im.alpha_composite(mm, (0, FK.HEAD_H))
    im.alpha_composite(K.special_foot(K.likes_at(t)).crop((0, 0, W, FK.ACT_H + FK.META_H)), (0, FK.HEAD_H + FK.MEDIA_H))
    return im


def col_cam(t):
    """camera over the endless wall: cut at 2.16 to a window view; CONTENT = pull back; LIVES = crane up, the
    wall tilts back into the fog like a crawl (infinite above, rushing past the lens below)."""
    e = t - T3
    pull = K.qio((t - (W_CONTENT - .04)) / .60)                         # 2.48 -> 3.08
    crane = K.eio((t - (W_LIVES - .05)) / .52)                         # 3.01 -> 3.53
    drift = K.smooth((t - 3.45) / .55)
    k = lerp(.80, .50, pull); k = lerp(k, .44, crane) - .03 * drift
    rx = lerp(3., 6., pull); rx = lerp(rx, 52., crane) + 4 * drift
    ry = 0.; rz = lerp(0., -1.0, crane) - 1.0 * drift
    sx = 540.; sy = lerp(985., 960., pull); sy = lerp(sy, 1000., crane) - 20 * drift
    sy -= 22 * K.smooth(e / .30) * (1 - pull)                        # the cut lands, then a small settle drift
    jolt = 0.0
    if t >= T_TAP:                                                      # glass tap: the post jolts toward the lens
        x = t - T_TAP; jolt = .05 * math.sin(min(1., x / .04) * math.pi / 2) * math.exp(-x / .08)
    return dict(k=k, rx=rx, ry=ry, rz=rz, sx=sx, sy=sy, jolt=jolt, pull=pull, crane=crane, drift=drift)


def plane_at(t):
    c = col_cam(t)
    return K.Plane(W / 2, V_HIS, c['sx'], c['sy'], c['k'], c['rx'], c['ry'], c['rz'], f=2300.), c


def _quad(P, u0, v0, u1, v1):
    return [P.proj(u0, v0)[:2], P.proj(u1, v0)[:2], P.proj(u1, v1)[:2], P.proj(u0, v1)[:2]]


def _offscreen(q):
    xs = [p[0] for p in q]; ys = [p[1] for p in q]
    return max(xs) < -20 or min(xs) > W + 20 or max(ys) < -50 or min(ys) > H + 50


def cap_y3(t, n):
    """seg-3 caption line centre: page 0 ("YOUR CONTENT") rides on his hoodie, inside his post, while the camera pulls
    back (never over the post's own UI text); page 1 ("LIVES IN HERE.") sits on the photo of the post below his,
    clear of its header."""
    P, c = plane_at(t)
    if n == 0: return min(1440., P.proj(W / 2, V_HIS - FK.MEDIA_H / 2 + 1150)[1])
    return max(1380., min(1600., P.proj(W / 2, NEXT_MEDIA_V + 170)[1]))


VOID_H = 2300
_GRID4 = tuple(a * 4 + 2 for a in np.mgrid[0:H // 4, 0:W // 4].astype(np.float32))   # quarter-res screen grid (y, x)
def column_phase(ctx, t):
    P, c = plane_at(t)
    oy = int(round((VOID_H - H) / 2 + 120 - 260 * c['crane'] - 60 * c['drift']))   # the void parallaxes with the crane
    out = K.void_bg(VOID_H).crop((0, oy, W, oy + H))
    # his live media (box depth relaxing out after the cut)
    m = media_img(ctx, t)
    d = box_depth(t) * (1 - K.smooth((t - T3) / .55))
    if d > .01: m = K.well(m, d)
    m = finish_media(m, t)
    # near clip: the plane rushes past the lens below his post once the wall tilts back
    dZ = P.depth(W / 2, V_HIS + 1000) / 1000
    v_lim = V_HIS + (420 - P.f) / dZ if dZ < -1e-6 else 1e9
    # soft glow behind his card (spill on the void through the gutters)
    glow = Image.new('L', (W // 4, H // 4)); dg = ImageDraw.Draw(glow)
    qh = _quad(P, -40, V_HIS - FK.MEDIA_H / 2 - FK.HEAD_H - 40, W + 40, V_HIS - FK.MEDIA_H / 2 - FK.HEAD_H + CARD_IMG_H + 40)
    dg.polygon([(x / 4, y / 4) for x, y in qh], fill=255)
    gl = Image.new('RGBA', (W // 4, H // 4), (110, 88, 255, 0)); gl.putalpha(glow.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * .5)))
    out.alpha_composite(gl.resize((W, H), Image.BILINEAR))
    vr = K.void_bg().getpixel((540, 300))[:3]
    mask = Image.new('L', (W // 4, H // 4))                            # where the glass (the wall of posts) is
    ws = 1 - K.smooth((t - (W_CONTENT + .03)) / .34)                   # the phone window (it was the screen)
    def put(key, fn, u0, v0, j_bright, his=False, mipblur=False):
        v1 = min(v0 + CARD_IMG_H, v_lim)
        if v1 - v0 < 20: return None
        if his:
            jo = 1 + c['jolt']; cu, cv = W / 2, V_HIS
            quad = [P.proj(cu + (u - cu) * jo, cv + (v - cv) * jo)[:2] for u, v in [(u0, v0), (u0 + W, v0), (u0 + W, v1), (u0, v1)]]
        else: quad = _quad(P, u0, v0, u0 + W, v1)
        if _offscreen(quad): return None
        Z = P.depth(u0 + W / 2, (v0 + v1) / 2)
        fog = math.exp(-max(0., Z) / 3200.)
        blur = 0.0 if his else min(14., abs(Z) * (.0042 if Z > 0 else .0075))
        if mipblur and blur > 3: mipblur = False                           # strong defocus: true Gaussian at 1/3 res
        br = 1.0 if his else j_bright * (fog if Z > 0 else math.exp(Z / 2600.))
        K.warp_pyr(out, key, fn, (W, CARD_IMG_H), quad, vfrac=(v1 - v0) / CARD_IMG_H, blur=blur, bright=br,
                   tint=None if (his or fog > .98) else (vr + (1 - fog,)), mask=mask, mipblur=mipblur)
        return quad
    # the neighbouring feeds (the wall goes on forever, left and right), then his own feed column
    for side, voff in SIDE:
        u0 = (W + GAP_U) * side
        for n in range(FK.SPECIAL - 11, FK.SPECIAL + 8):
            j = side_index(side, n)
            put(('mut', j), (lambda j=j: card_muted(j)), u0, FK.post_top(n) + voff, .33, mipblur=True)
    hero_q = None; hc = None
    for i in range(FK.SPECIAL - 10, FK.SPECIAL + 6):
        v0 = FK.post_top(i)
        if i == FK.SPECIAL:
            hc = his_card(m, t)
            hero_q = put(('his', round(t * E.FPS)), (lambda: hc), 0, v0, 1.0, his=True)
            K._PYR.pop((('his', round(t * E.FPS)), 0, 0), None)
            for kk in [k_ for k_ in K._PYR if k_[0][0] == 'his']: K._PYR.pop(kk, None)
        else:
            j = post_index(i)
            put(('mut', j), (lambda j=j: card_muted(j)), 0, v0, .54, mipblur=True)
    # his post is the light source of the shot: the wall falls off into darkness away from it (the loud posts at the
    # top of the frame recede), grows with the pull-back
    if hero_q is not None:
        dk = .12 + .50 * c['pull']
        if dk > .02:
            hx, hy = P.proj(W / 2, V_HIS)[:2]
            yy, xx = _GRID4
            fall = dk * (1 - np.exp(-(((xx - hx) / 600.) ** 2 + ((yy - hy) / 720.) ** 2)))
            out.paste((0, 0, 0), (0, 0, W, H), Image.fromarray((fall * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR))
    # his post is the one that glows: light spills onto the wall around it, lavender rim; flares on the tap
    ha = .35 * c['pull'] + .65 * c['crane'] + (.9 * math.exp(-(t - T_TAP) / .18) if t >= T_TAP else 0.)
    if hero_q is not None:
        _hero_light(out, hero_q, .30 + .35 * c['crane'] + (.5 * math.exp(-(t - T_TAP) / .2) if t >= T_TAP else 0.), ha)
    # the phone window that the first shot was: its app chrome dissolves first (before the move, so it never sits
    # over the posts' own text), then the glowing bezel shrinks away with the pull-back
    wc = 1 - K.ein(clamp((t - (W_CONTENT - .07)) / .16))            # chrome retract 2.45 -> 2.61 (accelerating)
    if ws > .01 and WIN_V0 + H + 14 < v_lim:
        v_a, v_b = WIN_V0, WIN_V0 + H
        mk = Image.new('L', (W // 2, H // 2), int(255 * .70 * ws))            # everything outside it was off-screen
        ImageDraw.Draw(mk).polygon([(x / 2, y / 2) for x, y in _quad(P, 0, v_a, W, v_b)], fill=0)
        out.paste((0, 0, 0), (0, 0, W, H), mk.filter(ImageFilter.GaussianBlur(1.5)).resize((W, H), Image.BILINEAR))
        wq = _quad(P, -14, v_a - 14, W + 14, v_b + 14)
        if wc > .01: K.warp_into(out, _win_chrome(round((1 - wc) * 12) / 12), wq)
        _warp_half(out, _win_rim_half(), wq, ws)
    # tap: the glass of the whole wall ripples from inside his post (refraction rings, perspective-squashed, ON the
    # posts only — never in the void) + a light pulse
    if T_TAP <= t < T_TAP + .8:
        tx, ty, _ = P.proj(TAP_U, TAP_V)
        mfull = mask.filter(ImageFilter.GaussianBlur(1)).resize((W, H), Image.BILINEAR)
        out = K.ripple(out, tx, ty, t - T_TAP, amp=10, speed=1250, width=40, q=2, ay=math.cos(math.radians(c['rx'])) * .9 + .1,
                       hl_gain=85, r0=20, mask=mfull)
    if T_TAP <= t < T_TAP + .5:
        e = t - T_TAP; cxp, cyp, _ = P.proj(TAP_U, TAP_V)
        fl = Image.new('L', (W // 4, H // 4)); r = (24 + 200 * K.eout(e / .5)) / 4
        ay = math.cos(math.radians(c['rx'])) * .9 + .1
        ImageDraw.Draw(fl).ellipse((cxp / 4 - r, cyp / 4 - r * ay, cxp / 4 + r, cyp / 4 + r * ay), outline=255, width=3)
        fl = fl.filter(ImageFilter.GaussianBlur(2.5)).point(lambda v: int(v * .55 * (1 - e / .5) ** 1.5))
        fl = Image.fromarray(np.minimum(np.asarray(fl), np.asarray(mask)))
        ring = Image.new('RGBA', (W // 4, H // 4), (200, 190, 255, 0)); ring.putalpha(fl)
        out.alpha_composite(ring.resize((W, H), Image.BILINEAR))
    return out


def _hero_light(out, quad, spill, rim):
    """his post is the light source: soft lavender spill on the neighbouring posts (outside his card), a glow along
    its edges and a crisp lavender rim line (one quarter-res light layer + a bbox-local rim)."""
    q4 = [(x / 4, y / 4) for x, y in quad]
    g = Image.new('L', (W // 4, H // 4)); ImageDraw.Draw(g).polygon(q4, fill=255)
    hole = np.asarray(g.filter(ImageFilter.GaussianBlur(1.2)), np.float32)
    a = np.clip(np.asarray(g.filter(ImageFilter.GaussianBlur(26)), np.float32) * spill - hole, 0, 255)
    if rim > .02:
        ln = Image.new('L', (W // 4, H // 4)); ImageDraw.Draw(ln).line(q4 + q4[:1], fill=255, width=3)
        a = a + np.asarray(ln.filter(ImageFilter.GaussianBlur(5)), np.float32) * .9 * rim
    lay = Image.new('RGBA', (W // 4, H // 4), (126, 102, 255, 0)); lay.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    out.alpha_composite(lay.resize((W, H), Image.BILINEAR))
    if rim > .02:
        xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
        bx0, by0 = max(0, int(min(xs)) - 4), max(0, int(min(ys)) - 4); bx1, by1 = min(W, int(max(xs)) + 5), min(H, int(max(ys)) + 5)
        if bx1 - bx0 > 4 and by1 - by0 > 4:
            ln = Image.new('L', (bx1 - bx0, by1 - by0))
            ImageDraw.Draw(ln).line([(x - bx0, y - by0) for x, y in quad + quad[:1]], fill=int(255 * min(1., .75 * rim)), width=3, joint='curve')
            out.paste(Image.new('RGB', ln.size, (200, 190, 255)), (bx0, by0), ln)


def _win_chrome(p=0.0):
    """the app chrome of the phone viewport, as a plane card (1108 x 1948, transparent middle). p 0..1 retracts it:
    the top bar slides up and the tab bar down, under the bezel (opaque the whole time — never a half-transparent
    bar over the posts' own text)."""
    def mk():
        pw, ph = W + 28, H + 28
        im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
        ht, hn = int(round(FK.TOP_Y * (1 - p))), int(round(FK.NAV_H * (1 - p)))
        if ht > 0: im.alpha_composite(FK.chrome_top().crop((0, FK.TOP_Y - ht, W, FK.TOP_Y)), (14, 14))
        if hn > 0: im.alpha_composite(FK.chrome_nav().crop((0, 0, W, hn)), (14, 14 + H - hn))
        return im
    return K.C(('s01_winc', p), mk)


def _win_rim_half():
    return K.C('s01_winr_h', lambda: _win_rim().resize(((W + 28) // 2, (H + 28) // 2), Image.LANCZOS))


def _warp_half(base, src, quad, alpha):
    """perspective-warp a soft RGBA layer at half resolution and upscale it (the glow rim needs no more)."""
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    x0, y0 = max(0, int(min(xs)) - 4), max(0, int(min(ys)) - 4); x1, y1 = min(W, int(max(xs)) + 5), min(H, int(max(ys)) + 5)
    if x1 - x0 < 4 or y1 - y0 < 4: return
    sz = ((x1 - x0 + 1) // 2, (y1 - y0 + 1) // 2)
    co = K.homography([(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)], [((x - x0) / 2, (y - y0) / 2) for x, y in quad])
    lay = src.transform(sz, Image.PERSPECTIVE, co, Image.BILINEAR).resize((x1 - x0, y1 - y0), Image.BILINEAR)
    if alpha < 1: lay = E.fade(lay, alpha)
    base.alpha_composite(lay, (x0, y0))


def _win_rim():
    """the glowing bezel outline of the phone viewport (1108 x 1948)."""
    def mk():
        pw, ph = W + 28, H + 28
        im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
        m = Image.new('L', (pw * 2, ph * 2)); ImageDraw.Draw(m).rounded_rectangle((4, 4, pw * 2 - 5, ph * 2 - 5), 110, outline=255, width=12)
        rim = Image.new('RGBA', (pw, ph), (205, 196, 255, 0)); rim.putalpha(m.resize((pw, ph), Image.LANCZOS).point(lambda v: int(v * .85)))
        gl = Image.new('RGBA', (pw, ph), (120, 100, 255, 0)); gl.putalpha(m.resize((pw, ph), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .7)))
        im.alpha_composite(gl); im.alpha_composite(rim)
        return im
    return K.C('s01_winr', mk)


# ---------------------------------------------------------------- frame
def draw(ctx, lt, t):
    P = ctx.post
    if t < T3:
        ctx.captions = False
        ctx.full = feed_phase(ctx, t)
        # a phone screen has no grain / vignette; the "film" look creeps in once the magic starts
        mg = K.smooth((t - T1) / .6)
        P['vignette'] = .30 * mg; P['grain'] = .25 + .55 * mg
        if t >= T2: P['vignette'] = .34; P['grain'] = .85
    else:
        fr = column_phase(ctx, t)
        K.draw_caps(fr, t, CAP_Y3, 84, {3}, fix=ONSETS, cy_fn=lambda n: cap_y3(t, n), scrim=CAP_SCRIM)
        ctx.full = fr; ctx.captions = False
        P['vignette'] = .34; P['grain'] = 1.0
