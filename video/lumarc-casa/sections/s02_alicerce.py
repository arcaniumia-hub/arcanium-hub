"""s02 — ALICERCE (4.72–9.32): "Pensa na sua marca como uma casa. / O alicerce é o seu posicionamento."

Beats (edit timeline s, onsets measured on src/tight16k.raw — see _A_kit):
  4.72  (contiguous with s01's silent beat, identical first frame) the camera cranes down from the high view of the
        empty lot to the two-shot: the lot rises to the top half while its perspective flattens (pitch 36 -> 22, dist
        24 -> 34.5 with a longer lens), he rises into frame from below, the studio slides up behind (parallax), the
        focus pulls from the lot to the room.  Lands on 5.40 "MARCA".
  5.40  "MARCA": a location ping on the empty lot — two light rings ripple out across the grass from its centre and
        a pin of light rises (the spot where YOUR brand goes).
  6.40  "CASA": the kit's light-line trace draws the house; the camera pushes in (expo), the trace's light spills on
        the studio wall behind it.
  6.87  jump -> low close-up on the plinth (house only): 6.99 "alicerce" the concrete plinth extrudes out of the lot
        (kit) with a white-hot rim flash (its top rim + corner edges) so the 0.4 m rise reads — the stone hit (7.02)
        kicks the camera (decaying shake, RGB, a breath of zoom blur, a light hit), the dust ring rolls.
  7.62  "é o seu": crane up to a high 3/4 of the plinth that keeps it BIG (the lot bleeds off both edges, as s03).
  8.36  "POSICIONAMENTO": the plinth's LED edge ignites (kit) as two light comets running round its rim from the
        callout corner, and the film's callout pins the word to it (same grammar as s03/s04): dot + pulse on the
        plinth corner, the leader drops (0.16 s expo), the frosted pill pops at its end.  The pill IS the caption.
  Seg 4's two-shot frames the house as big as s03's opening (two_e: lot off both edges, traced house ~780 px).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _A_kit as K
from sections import _house as HS
from sections import s01_hook as S1

START, END = E.span(4, 5)
W, H = E.W, E.H
lerp, clamp, eio, expo, eo = K.lerp, E.clamp, K.eio, K.expo, K.eo

T_CRANE1 = .68                        # crane duration from 4.72 (lands on MARCA)
T_PULL0, T_PULL1 = 7.62, 8.32         # crane up for "é o seu"

CUES = [
    (K.T_PENSA + .1, 'swoosh_up', {'gain': -16}),                       # crane down
    (K.T_MARCA, 'notify', {'gain': -9}), (K.T_MARCA + .14, 'pop', {'gain': -14}),    # location ping
    (K.T_O5 - .05, 'whoosh', {'gain': -12}),                            # cut to the close-up
    (HS.W_ALICERCE + .03, 'impact', {'gain': -9}),                       # the stone hit gets a body
    (T_PULL0 + .08, 'swoosh_up', {'gain': -14}),                         # crane up
    (K.T_POSIC + .01, 'click', {'gain': -3}), (K.T_POSIC + .08, 'swipe', {'gain': -15}),   # callout pins on
    (K.T_POSIC + .02, 'pop', {'gain': -10}), (K.T_POSIC + .03, 'shimmer', {'gain': -15}),   # LED rim comets
] + [c for c in HS.BUILD_CUES if START <= c[0] < END]                    # trace (6.40/6.45), stone (7.02), LED (8.36)

CAP_E = [K.page(K.SEG4, K.T_MARCA, [('PENSA', K.T_PENSA, 0), ('NA', K.T_NA, 0), ('SUA', K.T_SUA, 0)]),
         K.page(K.T_MARCA, K.T_COMO, [('MARCA', K.T_MARCA, 0)]),
         K.page(K.T_COMO, K.CUT5, [('COMO', K.T_COMO, 0), ('UMA', K.T_UMA, 0), ('CASA.', K.T_CASA, 1)])]
CAP_F = [K.page(K.CUT5, K.T_E5, [('O', K.T_O5, 0), ('ALICERCE', K.T_ALICERCE, 1)]),
         K.page(K.T_E5, K.T_POSIC, [('É', K.T_E5, 0), ('O', K.T_O5b, 0), ('SEU', K.T_SEU, 0)])]

# ------------------------------------------------------------------------------------------- cameras
def _crane(t): return K.eio5((t - K.SEG4) / T_CRANE1)

def two_e(t):
    """seg 4's two-shot: the house floats BIG behind/above him (same scale family as s03's opening: the lot bleeds off
    both frame edges, the traced house ~780 px wide, ridge ~y 390)."""
    b = S1.two_cam(t)
    b.update(f=2250, target=(0, 2.0, -0.6), px=560, py=640)
    return b

def cam_e(t):
    """two-shot camera of seg 4: crane from s01's lot close-up, then the push-in on CASA."""
    a = S1.lot_close_cam(t); b = two_e(t)
    push = expo(clamp((t - K.T_CASA) / .9))
    b['f'] *= 1 + .07 * push; b['py'] += 18 * push
    return K.fmix(a, b, _crane(t))

def cam_f1(t):
    u = clamp((t - K.CUT5) / 1.2)
    return K.fcam(20 + 4 * u, 8.5 - 1.0 * u, 13.4 - .8 * u, 1150, (0, 0.8, 1.0), 540, 1000)

def cam_f2(t):
    """high 3/4 on the plinth for the callout: the slab big (~830 px), the lot bleeding off both edges like s03."""
    u = (t - T_PULL1)
    return K.fcam(34 + 2.4 * u, 26, 30, 2200 * (1 + .03 * u), (0.4, 1.0, 0.0), 540, 800)

def cam_f(t):
    k = K.eio5((t - T_PULL0) / (T_PULL1 - T_PULL0))
    return K.fmix(cam_f1(t), cam_f2(t), k), k

# ------------------------------------------------------------------------------------------- draw
def draw(ctx, lt, t):
    P = ctx.post; ctx.light = 0.0
    if t < K.CUT5: _shot_e(ctx, t, P)
    else: _shot_f(ctx, t, P)
    if ctx.light > .03 and ctx.wrap is None:
        k = min(.5, ctx.light); ctx.wrap = lambda fr: K.light_hit(fr, k)

def _shot_e(ctx, t, P):
    ctx.cam.update(z=1.0, x=540, y=960, dx=0, dy=0, rot=0)
    kc = _crane(t)
    st = HS.state_at(t)
    fc = cam_e(t)
    # him: rises into frame from below as the camera tilts down
    tf = S1.TWO_F
    K.avatar_at(ctx, tf['s'], tf['fx'], lerp(tf['fy'] + 860, tf['fy'], kc), show=kc > .02)
    # studio: slides up behind (far layer: less travel), focus pulls from the lot to the room
    tr = clamp((t - K.T_CASA) / .62) * st['outline_a']
    gx, gy = fc['px'], fc['py'] + 120
    z0, x0_, y0_ = S1.D_STUDIO; g0 = S1.D_GLOW
    ctx.bg_img = K.studio_view(lerp(z0, 1.08, kc), lerp(x0_, 540, kc), lerp(y0_, 700, kc),
                               glows=[(lerp(g0[0], gx, kc), lerp(g0[1], gy, kc), lerp(g0[2], 560, kc), g0[3], lerp(g0[4], .6, kc)),
                                      (gx, gy - 140, 420, (170, 140, 255), .55 * tr)], blur=lerp(7.0, 2.5, kc), dim=.18 * (1 - kc))
    # beam fades into a soft ambient as we leave the close-up; the light pool stays on the empty lot until the trace
    S1._beam(ctx, t, lerp(540, fc['px'], kc), lerp(860, 700, kc), lerp(.95, .45, kc), wt=170, wb=int(lerp(700, 600, kc)))
    M = S1.D_MOTES
    K.motes(ctx, t, M['box'], n=M['n'], seed=M['seed'], alpha=lerp(1.0, .6, kc), beam=M['beam'])
    K.house(ctx, t, fc, st=st)
    S1.light_pool(ctx, fc, st, lerp(1.0, .7, kc) * (1 - clamp((t - K.T_CASA + .1) / .4)))
    _ping(ctx, t, fc, st)
    if K.T_CASA <= t < K.T_CASA + .3: ctx.light = max(ctx.light, .10 * math.exp(-(t - K.T_CASA) / .08))
    # captions: while he rises into frame the first page rides just above his head (never across his face); from
    # "MARCA" on they sit on his chest like everywhere else
    fy = lerp(tf['fy'] + 860, tf['fy'], kc)
    if t < K.T_MARCA: K.captions(ctx, t, CAP_E, min(S1.CAP_Y, fy - 267 - 80))
    else: K.captions(ctx, t, CAP_E, S1.CAP_Y)

def _ping(ctx, t, fc, st):
    """'sua marca': two light rings ripple out over the lot from its centre + a pin of light."""
    u = t - K.T_MARCA
    if u < 0 or u > 1.1: return
    segs = []
    for j, d in enumerate((0.0, .16)):
        q = u - d
        if q <= 0: continue
        r = .4 + 6.6 * eo(q / .8, 2.4); a = (1 - clamp(q / .8)) ** 1.4
        n = 48; ang = np.linspace(0, 2 * math.pi, n + 1)
        P3 = np.stack([r * np.cos(ang), np.full(n + 1, .02), r * np.sin(ang)], 1)
        S, Z = K.project(fc, st, P3)
        if Z.min() < .3: continue
        for i in range(n): segs.append((tuple(S[i]), tuple(S[i + 1]), a, 3.2 - 1.2 * j))
    # the pin: a short vertical light rising from the centre, its head a bright dot
    kp = E.back(clamp(u / .22), 2.0) * (1 - clamp((u - .7) / .3))
    if kp > .01:
        S, Z = K.project(fc, st, np.array([[0, 0, 0], [0, 1.6 * kp, 0]]))
        if Z.min() > .3:
            segs.append((tuple(S[0]), tuple(S[1]), min(1, kp), 3.4)); segs.append((tuple(S[1]), tuple(S[1] + .1), min(1, kp), 12.0))
    K.add_strokes(ctx, 'behind', segs, glow=10, glow_a=1.0)

def _shot_f(ctx, t, P):
    fc, kf = cam_f(t)
    st = HS.state_at(t)
    ctx.avatar['show'] = False
    # stone hit: decaying camera shake + a breath of RGB (the plinth thumps out of the ground)
    sh = 0.0; dx = dy = 0.0
    if t >= HS.W_ALICERCE + .03:
        u = t - (HS.W_ALICERCE + .03); sh = math.exp(-u / .11)
        dx = 9 * sh * math.sin(u * 83); dy = 15 * sh * math.cos(u * 71)
        P['rgb'] = max(P['rgb'], 4 * sh)
        if u < .08: P['zoom_blur'] = max(P['zoom_blur'], .14 * (1 - u / .08))
    ctx.cam.update(z=1.03, x=540, y=960, dx=dx, dy=dy, rot=.004 * sh * math.sin(t * 50))
    lt = t - K.CUT5
    if lt < .08: ctx.light = max(ctx.light, .12 * (1 - lt / .08))
    if 0 <= t - (HS.W_ALICERCE + .03) < .2: ctx.light = max(ctx.light, .16 * math.exp(-(t - HS.W_ALICERCE - .03) / .05))
    gx, gy = fc['px'], fc['py']
    led = st['led']
    ctx.bg_img = K.studio_view(lerp(1.30, 1.16, kf), 540, lerp(840, 760, kf),
                               glows=[(gx, gy, 600, (120, 90, 255), .55), (gx, gy + 120, 520, (150, 110, 255), .45 * led)],
                               blur=lerp(8.0, 5.0, kf), dim=.16)
    K.motes(ctx, t, (40, 80, 1040, 1500), n=34, seed=13, alpha=.6)
    K.house(ctx, t, fc, st=st)
    _slab_flash(ctx, t, fc, st)
    _led_run(ctx, t, fc, st)
    K.captions(ctx, t, CAP_F, S1.CAP_Y)
    _callout(ctx, t, fc, st)

# ------------------------------------------------------------------------------------------- slab accents
SX, SZ0, SZ1 = HS.HX + .32, HS.ZH - (HS.HZ + .32), HS.ZH + (HS.HZ + .32)       # plinth footprint (x half, z back/front)
def _slab_y(st): return HS.YS * max(0.0, st['slab']) * (1 - st['sink'])

def _slab_flash(ctx, t, fc, st):
    """'a-LI-cerce': the plinth pushes out of the ground white-hot — its top rim and the visible corner edges flash
    (decays in ~0.3 s) so the 0.4 m extrusion reads as a RISE, not a plate appearing."""
    u = t - HS.W_ALICERCE
    if u < 0 or u > .45 or st['slab'] <= 0: return
    a = clamp(u / .03) * math.exp(-max(0.0, u - .03) / .13)
    if a < .02: return
    y = _slab_y(st)
    FR, FL, BL, BR = (SX, y, SZ1), (-SX, y, SZ1), (-SX, y, SZ0), (SX, y, SZ0)
    pts = np.array([FR, FL, BL, BR, (SX, 0, SZ1), (-SX, 0, SZ1), (SX, 0, SZ0)])
    S, Z = K.project(fc, st, pts)
    if Z.min() < .3: return
    P = [tuple(q) for q in S]
    segs = [(P[0], P[1], a, 3.4), (P[1], P[2], a * .7, 2.6), (P[2], P[3], a * .7, 2.6), (P[3], P[0], a, 3.0),
            (P[4], P[0], a, 3.0), (P[5], P[1], a, 3.0), (P[6], P[3], a * .8, 2.6)]
    K.add_strokes(ctx, 'behind', segs, cols=K.WHITE3, glow=16, glow_a=1.0, core=.7)

def _led_run(ctx, t, fc, st):
    """'POSICIONAMENTO': the LED edge ignites as two light comets that run from the callout corner around the plinth's
    rim (0.5 s, cubic ease-out) and meet at the far corner; the lit rim then holds and breathes under the callout."""
    u = t - K.T_POSIC
    if u < 0 or st['led'] <= 0 and u < .05: return
    y = HS.YS * min(1.0, max(0.0, st['slab'])) + .01
    FR, FL, BL, BR = (SX, y, SZ1), (-SX, y, SZ1), (-SX, y, SZ0), (SX, y, SZ0)
    paths = [(FR, FL, BL), (FR, BR, BL)]
    L = 2 * SX + (SZ1 - SZ0)
    hd = eo(u / .5, 3) * L                                   # head arc length (m): fast off the corner, eases in
    hold = .62 + .08 * math.sin(max(0.0, u - .5) * 5.0)        # lit rim afterwards
    segs = []
    for path in paths:
        pts = []
        for (p0, p1) in ((path[0], path[1]), (path[1], path[2])):
            p0, p1 = np.array(p0), np.array(p1); n = max(2, int(np.linalg.norm(p1 - p0) / .45))
            for i in range(n): pts.append(p0 + (p1 - p0) * i / n)
        pts.append(np.array(path[2], float))
        pts = np.array(pts); d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        S, Z = K.project(fc, st, pts)
        if Z.min() < .3: return
        for i in range(len(pts) - 1):
            if d[i] >= hd: break
            b = S[i + 1] if d[i + 1] <= hd else S[i] + (S[i + 1] - S[i]) * (hd - d[i]) / (d[i + 1] - d[i])
            near = math.exp(-(hd - d[i]) / 1.6) * (1 - clamp((u - .45) / .3))
            a = max(hold * clamp((u - .02) / .08), min(1.0, .4 + .9 * near))
            segs.append((tuple(S[i]), tuple(b), a, 3.2 + 2.6 * near))
        if u < .55 and hd < L - .05:                           # the comet head
            j = int(np.searchsorted(d, hd)) - 1; j = max(0, min(j, len(pts) - 2))
            h = S[j] + (S[j + 1] - S[j]) * clamp((hd - d[j]) / max(1e-6, d[j + 1] - d[j]))
            segs.append((tuple(h), tuple(h + .1), 1.0, 13.0))
    if segs: K.add_strokes(ctx, 'behind', segs, glow=12, glow_a=1.0, core=.45)

# ------------------------------------------------------------------------------------------- callout
CORNER = (HS.HX + .32, HS.YS, HS.FRONT + .32)          # plinth front-right top corner (nearest the camera)
LBL = (540, 1452)                                       # label centre (below the lot, inside the safe area)

def _callout(ctx, t, fc, st):
    """the film's callout grammar (as s03/s04): dot + pulse on the plinth corner ON the word, the leader draws down
    (0.16 s, expo), the frosted pill pops at its end with the word.  The pill IS the caption of that page."""
    u = t - K.T_POSIC
    if u < -.01: return
    S, Z = K.project(fc, st, np.array([CORNER]))
    if Z.min() < .3: return
    D = (float(S[0][0]), float(S[0][1]))
    pill = K.label_pill('POSICIONAMENTO.', 76)
    ph = pill.height - 140
    top = (D[0], LBL[1] - ph / 2 - 4)                   # the leader meets the pill's top edge
    k = expo(clamp(u / .16))
    if k > 0:
        K.add_strokes(ctx, 'screen', [(D, (D[0], lerp(D[1], top[1], k)), 1.0, 4.0)], cols=K.WHITE3, glow=7, glow_a=.75)
    pk = clamp(u / .5)
    ctx.add('screen', K.anchor_dot(9, round(pk * 50) / 50), D[0], D[1])
    if u > 1.2:                                         # a second, softer pulse while it holds
        q = clamp((u - 1.2) / .6); ctx.add('screen', K.anchor_dot(9, round(q * 50) / 50), D[0], D[1], alpha=.7)
    s = .55 + .45 * E.back(clamp(u / .22), 1.6)
    s *= 1 + .02 * clamp((u - .3) / 1.0)                # slow breathe while it holds
    p = K.scaled(pill, s); a = clamp(u / .07)
    ctx.add('screen', p, LBL[0], LBL[1] + 10 * (1 - eo(u / .22)), glass=10 if a > .6 else 0, alpha=a)
