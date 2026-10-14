"""s04 — PORTA + "AGORA REPARA…" (13.40–16.68).  "E a porta é o seu chamado pra ação. Agora repara…"

SHOT 3 (13.40, jump cut -> door close-up).  The door swings in from wide open (the warm doorway light is cut as it
     closes) and SLAMS shut ON "PORTA" (13.70): camera jolt + punch, a puff of dust off the threshold.  The camera then
     creeps in toward the handle through "é o seu…".  "CHAMADO" (14.71): a callout grows out of the handle — a frosted
     pill that widens word by word, "PRA" (15.29), "AÇÃO" (15.42): the pill is TAPPED (ripple) and lights up as the
     LUMARC CTA button, in sync with the kit's purple LED handle flickering on (both driven by state['cta']).
SHOT 4 (15.84, jump cut -> FREEZE).  Everything stops: the house, its window films and the camera freeze on the last
     frame; the world drains to near-monochrome with a cool cast and a deep vignette, one white flash frame + a single
     'tick' (the score is silent here).  Only he stays alive and in colour; the camera creeps in (anchored below his
     chin, so his face rises toward the centre and the caption stays on his hoodie) and ON "REPARA…" (16.36) leans in
     on his face; the frozen CTA drains away; the kit's light sheen sweeps across the frozen house.
Captions: own word pops (engine look) on the measured onsets; CHAMADO PRA AÇÃO is the CTA label itself (one place).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS
from sections import _b_kit as K

START, END = E.span(8, 9)                     # 13.40 – 16.68
T_FZ = K.jump_t(9)                            # 15.833: the frame his pose jumps (seg 9, 15.84) -> freeze
T_OUT = K.jump_t(10)                          # 16.667: his pose already jumps to seg 10 on our last frame

CUES = [c for c in HS.BUILD_CUES if START <= c[0] < END] + [
    (K.O_CHAMADO, 'pop', {'gain': -12}),                    # CTA callout grows out of the handle
    (K.O_PRA, 'pop', {'gain': -18}),                        # ...word by word
    (T_FZ, 'tick', {'gain': 6}),                            # FREEZE: one tick (the score cuts out here)
]

HSIZE = (1080, 1400)
HFADE = (1180, 1400)
def sy(y): return (y - HSIZE[1] / 2) / HSIZE[1]

AV3 = dict(show=True, s=1.00, x=-22., y=440., alpha=1.0, copies=[], bright=1.0)
# zoom anchor of the freeze push: below his chin (world y ~1500-1525 for AV3), so the push moves his face UP toward
# the frame centre and the caption line (y 1560) stays on his hoodie, never over his mouth/beard
FACE = (530., 1700.)

# ---------------------------------------------------------------------------------------------- shot 3 camera
C3A = dict(yaw=22.0, pitch=9.0, dist=14.6, fov=30, target=(0.0, 1.7, 3.3), shift=(0, sy(610)))
C3B = dict(yaw=16.0, pitch=7.0, dist=10.6, fov=30, target=(0.05, 1.55, 3.3), shift=(0, sy(620)))
C3C = dict(yaw=11.0, pitch=5.5, dist=7.4, fov=30, target=(0.16, 1.42, 3.3), shift=(0, sy(630)))

def cam3(t):
    """wide enough to see the door swing in, PUNCH-IN on the slam (expo), then a slow creep toward the handle."""
    c = K.cam_mix(C3A, C3B, .12 * K.smooth((t - START) / (HS.W_PORTA - START)))
    if t >= HS.W_PORTA:
        c = K.cam_mix(c, C3B, K.expo((t - HS.W_PORTA) / .30))
        c = K.cam_mix(c, C3C, K.sio((t - (HS.W_PORTA + .25)) / (T_FZ - (HS.W_PORTA + .25))) ** .9)
    return c

# floating motes in the lit air in front of the house: they drift while time runs and hang dead still in the freeze
MOTES = [(K.hrand(i, 31), K.hrand(i, 32), K.hrand(i, 33), K.hrand(i, 34)) for i in range(26)]
def motes(ctx, t, sat=1.0):
    for i, (a, b, c, d) in enumerate(MOTES):
        tt = t - 13.0
        x = (a * 1180 - 50 + 26 * math.sin(tt * (.6 + .5 * c) + i) + 14 * tt * (c - .5)) % 1180 - 50
        y = (b * 1050 + 40 - tt * (16 + 22 * d)) % 1050 + 40
        r = 3 + 9 * c * c
        col = (255, 214, 160) if i % 3 else (190, 160, 255)
        if sat < 1: g = int(sum(col) / 3); col = tuple(int(g + (v - g) * sat) for v in col)
        ctx.add('behind', K.glow_spot(r * 2.2, col, .55 * (.4 + .6 * d)), x, y)

def _dust(ctx, hs, t):
    """the slam puffs a little dust off the threshold (soft sprites, spread along the door bottom, drifting out)."""
    u = (t - HS.W_PORTA) / .9
    if not (0 <= u < 1): return
    base = hs.proj([[0, HS.YS + .02, HS.FRONT + .08], [.5, HS.YS + .02, HS.FRONT + .08]])[0]
    scale = abs(base[1][0] - base[0][0]) * 2                  # px per metre at the threshold
    for i in range(9):
        r1, r2 = K.hrand(i, 21), K.hrand(i, 22)
        x = base[0][0] + (r1 - .5) * scale * (.8 + 1.4 * K.eout(u))
        yv = base[0][1] - scale * (.05 + .25 * K.eout(u) * (.4 + r2))
        rad = scale * (.10 + .16 * K.eout(u)) * (.7 + .6 * r2)
        a = .30 * (1 - u) ** 1.5 * (.5 + .5 * r1)
        ctx.add('behind', K.glow_spot(max(6, rad), (226, 218, 206), a), x, yv)

# ---------------------------------------------------------------------------------------------- CTA callout
CTA_WORDS = [('CHAMADO', K.O_CHAMADO), ('PRA', K.O_PRA), ('AÇÃO', K.O_ACAO)]
PILL_L, PILL_Y = 128, 312                     # pill left edge / centre row (world frame)

def cta_callout(ctx, hs, st, t):
    if t < K.O_CHAMADO - .01: return
    A = hs.proj([K.HANDLE])[0][0]
    pill, G = K.grow_pill(CTA_WORDS, t, 74, cta=float(st['cta']) if t >= K.O_ACAO else 0.0)
    if pill is None: return
    lt = t - K.O_CHAMADO
    # leader from the handle up to the pill's underside (drawn on), dot + pulse on the handle
    h = pill.height - 2 * G
    B = (min(max(A[0], PILL_L + 60), PILL_L + 360), PILL_Y + h / 2 + 2)
    k = K.expo(lt / .18)
    x0, y0 = int(min(A[0], B[0])) - 40, int(B[1]) - 40
    x1, y1 = int(max(A[0], B[0])) + 40, int(A[1]) + 40
    if y1 - y0 > 10:
        ctx.add('behind', K.leader((x1 - x0, y1 - y0), (A[0] - x0, A[1] - y0), (B[0] - x0, B[1] - y0), k), x0, y0, center=False)
    ctx.add('behind', K.dot(9, K.clamp(lt / .5)), A[0], A[1])
    # pill: pops (scale from its left-centre), then grows word by word
    s = .6 + .4 * K.back(lt / .22, 1.6) if lt < .22 else 1.0
    tap = (t - K.O_ACAO) / .30
    if 0 <= tap < 1: s *= 1 - .045 * math.sin(math.pi * tap)            # the button is pressed
    im = pill if abs(s - 1) < .005 else pill.resize((max(1, int(pill.width * s)), max(1, int(pill.height * s))), Image.BILINEAR)
    cx = PILL_L - G * s; cy = PILL_Y - im.height / 2
    ctx.add('behind', im, cx, cy, center=False, alpha=K.clamp(lt / .06), glass=12 if lt > .06 else 0)
    if 0 <= tap < 1:                                                    # tap ripple on AÇÃO
        f = E.font(74); wC = f.getbbox('CHAMADO')[2] + f.getbbox('PRA')[2] + 2 * 74 * .30
        ctx.add('behind', K.ripple_ring(150, tap), PILL_L + 40 + wC + f.getbbox('AÇÃO')[2] / 2, PILL_Y)

# window 0's film loop (kit: master.mp4 from 2.0 s) opens on the hyper film's deliberately cheesy "before" ad (SILENCE ONE
# / NEW! / 50% OFF!!! / AMAZING SOUND / BUY NOW, src 2.0-4.6 s) -- exactly what it plays during this close-up (loop frames
# 17-89).  Here the same window shows the SAME film 130 frames later (its premium half: the gold ring, the lit headphones,
# "Introducing SILENCE ONE", the texture close-up; loop frames 147-219, no wrap), drawn with the kit's own pane renderer,
# seen only through the opening (the freeze bakes it too).
WIN0_PHASE = 130 / 30

def win0_pane(hs, st, t):
    """(RGBA, x0, y0) of window 0's pane re-rendered at the shifted film phase, clipped to what the opening shows."""
    p = HS.G.win_pane[0]
    if float(st['vid'][0]) < .01 or (hs.cam_model() - p['q'][0]) @ p['n'] <= 0: return None
    Q, Z = hs.proj(p['q']); O, _ = hs.proj(p['open'])
    if Z.min() < .5 or Q[:, 0].max() < 0 or Q[:, 0].min() > HSIZE[0]: return None
    wp = K.warp(HS._pane_img(p, st, t + WIN0_PHASE, hi=True), Q, pad=0)
    if wp is None: return None
    im, x0, y0 = wp
    m = Image.new('L', im.size); ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in O], fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel('A'), m))
    return K.house_grade(im), x0, y0

def overlays(ctx, hs, st, t):
    """everything pinned to the house in shot 3 (handle halo, threshold dust, CTA callout)."""
    if st['cta'] > .01:                                                 # the handle's light spills (halo)
        A = hs.proj([K.HANDLE])[0][0]
        ctx.add('behind', K.glow_spot(110, (150, 90, 255), .55 * st['cta']), A[0], A[1])
    _dust(ctx, hs, t)
    cta_callout(ctx, hs, st, t)

# ---------------------------------------------------------------------------------------------- draw
def draw(ctx, lt, t):
    ctx.captions = False
    if t < T_FZ: shot3(ctx, t)
    else: freeze(ctx, t)

def shot3(ctx, t):
    st = HS.state_at(t)
    ctx.bg_img = K.studio_bg(.40, 12.0)
    dx, dy = K.shake(t, HS.W_PORTA, 12.0, dur=.36, freq=17, seed=4)
    ctx.cam = dict(z=1.035 + .022 * K.kick(t, HS.W_PORTA, 1.0, .26), x=540., y=760., dx=dx, dy=dy, rot=0.)
    ctx.avatar = dict(AV3)
    ctx.post['vignette'] = .36
    hs = K.House(st, cam3(t), HSIZE, (0, 0), t=t, fade=HFADE)
    ctx.add('behind', hs.img, 0, 0, center=False)
    w0 = win0_pane(hs, st, t)
    if w0 is not None: ctx.add('behind', w0[0], w0[1], w0[2], center=False)
    overlays(ctx, hs, st, t)
    motes(ctx, t)
    K.captions(ctx, t, y=1560)

_FZ = {}
class _Layers:                                    # collects ctx.add() calls to bake them into the frozen frame
    add = E.Ctx.add
    def __init__(self): self.behind = []

def _frozen_world(t):
    """the frozen frame: (house image, CTA-callout image) with state, camera and window films stopped at T_FZ, both
    drained of colour (cached); the kit's REPARA sheen still sweeps across the house."""
    sheen = HS.state_at(t)['sheen']
    key = round(sheen, 4) if sheen >= 0 else -1
    if key not in _FZ:
        if len(_FZ) > 3: _FZ.clear()
        st = dict(HS.state_at(T_FZ)); st['sheen'] = sheen
        hs = K.House(st, cam3(T_FZ), HSIZE, (0, 0), t=T_FZ, fade=HFADE)
        w0 = win0_pane(hs, st, T_FZ)
        if w0 is not None: hs.img = hs.img.copy(); E._paste(hs.img, dict(img=w0[0], xy=(w0[1], w0[2]), glass=0))
        L = _Layers(); overlays(L, hs, st, T_FZ)
        ui = Image.new('RGBA', HSIZE, (0, 0, 0, 0))
        for l in L.behind: E._paste(ui, dict(l, glass=0))
        f = lambda im: K.grade(K.desat(im, .36, cool=1.0), mul=.80, gamma=1.15)
        _FZ[key] = (f(hs.img), f(ui))
    return _FZ[key]

def freeze(ctx, t):
    u = (t - T_FZ) / (END - T_FZ)
    ctx.bg_img = K.studio_bg(.50, 14.0, sat=.36, tint=(.95, .97, 1.04))
    fw, ui = _frozen_world(t)
    k = K.smooth((t - (T_FZ + .08)) / .62)                    # focus racks onto him as the camera pushes in: the house
    if k > .07: fw = fw.filter(ImageFilter.GaussianBlur(4.6 * k))   # defocuses, the overlay (nearest the lens) more
    ctx.add('behind', fw, 0, 0, center=False)
    ua = 1 - K.smooth((t - (T_FZ + .05)) / .30)               # the frozen CTA drains away before the push carries it
    if ua > .01:                                              # out of the top of frame (no half-cropped text)
        if k > .07: ui = ui.filter(ImageFilter.GaussianBlur(11 * k))
        ctx.add('behind', ui, 0, 0, center=False, alpha=ua)
    motes(ctx, T_FZ, sat=.36)
    ctx.avatar = dict(AV3)
    # slow creep through "Agora…", then ON "REPARA" the camera leans in on his face (eased, lands on the last frame)
    z = 1.10 + .10 * K.clamp((t - T_FZ) / (K.O_REPARA - T_FZ)) ** 1.4
    if t >= K.O_REPARA - .015: z += .21 * K.eout((t - (K.O_REPARA - .015)) / (T_OUT - K.O_REPARA + .015))
    ctx.cam = dict(z=z, x=FACE[0], y=FACE[1], dx=0., dy=0., rot=0.)
    fl = (t - T_FZ) / .16
    if fl < 1: ctx.post['flash'] = .42 * (1 - fl) ** 2
    ctx.post['vignette'] = .40 + .26 * K.smooth(u)
    lt = t - T_FZ + 1 / 30                                    # pause chip pops ON the tick frame (screen layer, not zoomed)
    s_ = .55 + .45 * K.back(lt / .2, 2.0); pc = K.pause_chip()
    pc = pc.resize((max(1, int(pc.width * s_)), max(1, int(pc.height * s_))), Image.BILINEAR)
    ctx.add('screen', pc, 540, 350, alpha=K.clamp(lt / .06) * (1 - .35 * K.smooth((lt - .5) / .3)), glass=10 if lt > .05 else 0)
    if t >= T_OUT - 1e-6: ctx.post['flash'] = .75              # time resumes: a white frame hides his pose jump (seg 10)
    K.captions(ctx, t, y=1560)
