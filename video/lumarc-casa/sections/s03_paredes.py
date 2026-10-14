"""s03 — PAREDES + JANELAS (9.32–13.40).  "As paredes são o seu conteúdo. As janelas são os seus vídeos."

SHOT 1 (9.32, jump cut -> new framing).  The house floats big behind him in the defocused studio; a slow 3-D crane rises
     with the walls while the blocks drop in row by row (first block lands ON "PAREDES" 9.56, every row lands with a
     tiny camera jolt + its 'block' cue).  "SÃO O SEU" — on "CONTEÚDO" (10.72) the camera pushes in (expo-out) and the
     LUMARC posts are thrown into the wall: one printed post card per visible tile flies in from beyond the frame and
     stamps onto its tile exactly when the kit reveals that tile (ripple 10.72 + 0.03 s each); a callout pins the
     word CONTEÚDO to the wall.  The roof drops and lands (11.22): the camera cranes up + back while it falls so the
     whole gable + chimney land IN frame, coming to rest on the impact — camera jolt, dust out of the eaves.
SHOT 2 (11.40, jump cut -> lateral tracking shot, he moves to the left of frame).  The camera tracks along the facade
     as the windows switch on one by one (11.59 / 11.80 -NE- / 12.02 / 12.24, warm interiors).  On "VÍDEOS" (12.84) the
     windows in frame power on like screens (CRT blink: black + white-hot scan line on 12.833, opening to a cool-white
     screen that dissolves into the kit's films), the camera pushes into the right-hand pair; a ▶ callout "VÍDEOS."
     pins to a window.
Captions: own word pops (engine look) with the onsets measured on src/tight16k.raw; the key word of each line becomes
the callout label (never stacked).
"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from sections import _house as HS
from sections import _b_kit as K

START, END = E.span(6, 7)                     # 9.32 – 13.40
T_CUT2 = E.TL[7]['t0']                        # 11.40 jump cut
T_PUSH0, T_PUSH1 = 10.28, K.O_CONTEUDO + .02   # the camera closes in on "o seu", arriving on CONTEÚDO

CUES = [c for c in HS.BUILD_CUES if START <= c[0] < END] + [
    (K.O_CONTEUDO - .01, 'swipe', {'gain': -11}),          # the post cards fly in (peak on the first stamp)
    (T_PUSH1 - .10, 'whoosh', {'gain': -17}),             # camera closes in
    (K.O_VIDEOS + .03, 'whoosh', {'gain': -14}),           # camera push into the playing windows
    (K.O_VIDEOS + .02, 'pop', {'gain': -12}),              # VÍDEOS callout
]

HSIZE = (1080, 1400)                          # house layer (top of the world frame), fades out behind his shoulders
HFADE = (1180, 1400)
LABEL_Y = 312                                 # callout labels (world y; ~295 on screen: inside the safe area)
def sy(y): return (y - HSIZE[1] / 2) / HSIZE[1]        # screen row -> camera shift

# his framings (s >= 1: the take's side edges stay outside the frame; lower in frame so the house owns the top)
AV1 = dict(show=True, s=1.00, x=0., y=440., alpha=1.0, copies=[], bright=1.0)
AV2 = dict(show=True, s=1.10, x=58., y=530., alpha=1.0, copies=[], bright=1.0)

# ---------------------------------------------------------------------------------------------- shot 1 camera
CR0 = dict(yaw=43.0, pitch=17.0, dist=30.0, fov=30, target=(0.0, 1.0, -0.5), shift=(0, sy(640)))
CR1 = dict(yaw=35.0, pitch=20.0, dist=26.0, fov=30, target=(0.0, 1.9, -0.5), shift=(0, sy(610)))
CP = dict(yaw=30.0, pitch=13.0, dist=17.0, fov=30, target=(0.8, 2.15, 0.6), shift=(0, sy(640)))
CP2 = dict(yaw=27.0, pitch=12.0, dist=16.2, fov=30, target=(0.8, 2.35, 0.6), shift=(0, sy(640)))
# the roof: the camera cranes up + back while it falls, so the whole gable + chimney land IN frame (ridge ~y 180)
# and the camera comes to rest exactly as the roof slams down (11.22); then a slow settle until the cut.
T_PB0 = HS.ROOF_LAND - HS.ROOF_FALL - .02               # 10.94: the roof starts to fall
CPB = dict(yaw=28.0, pitch=13.0, dist=18.2, fov=30, target=(0.7, 2.8, 0.4), shift=(0, sy(640)))
CPB2 = dict(yaw=29.0, pitch=13.4, dist=18.9, fov=30, target=(0.7, 2.85, 0.35), shift=(0, sy(640)))

def cam1(t):
    c = K.cam_mix(CR0, CR1, K.sio((t - 9.0) / (T_PUSH1 - 9.0)))
    if t >= T_PUSH0:
        c = K.cam_mix(c, CP, K.sio((t - T_PUSH0) / (T_PUSH1 - T_PUSH0)) ** 1.15)
        if t >= T_PUSH1: c = K.cam_mix(c, CP2, K.smooth((t - T_PUSH1) / (T_CUT2 - T_PUSH1)))
        if t >= T_PB0:
            c = K.cam_mix(c, CPB, K.sio((t - T_PB0) / (HS.ROOF_LAND - T_PB0)))
            if t >= HS.ROOF_LAND: c = K.cam_mix(c, CPB2, K.eout((t - HS.ROOF_LAND) / (T_CUT2 - HS.ROOF_LAND)))
    return c

# ---------------------------------------------------------------------------------------------- shot 2 camera
CT0 = dict(yaw=5.0, pitch=7.0, dist=19.0, fov=30, target=(-1.8, 2.0, 2.2), shift=(0, sy(600)))
CT1 = dict(yaw=58.0, pitch=8.5, dist=18.5, fov=30, target=(2.4, 2.0, -0.4), shift=(0, sy(600)))
CV = dict(yaw=70.0, pitch=6.0, dist=12.6, fov=30, target=(3.6, 2.0, -0.45), shift=(0, sy(630)))
T_VPUSH = K.O_VIDEOS - .02

def cam2(t):
    c = K.cam_mix(CT0, CT1, K.sio((t - 11.2) / (12.8 - 11.2)))
    if t >= T_VPUSH: c = K.cam_mix(c, CV, K.expo((t - T_VPUSH) / .45))
    return c

# ---------------------------------------------------------------------------------------------- post cards (CONTEÚDO)
FLIGHT = .26

def _card_quad(f, k):
    """card corners at flight progress k (0 = launched near the lens, 1 = pinned on its tile): the post flies away
    from the camera into the wall (mostly a scale change, so the image stays readable in motion), turning flat."""
    q = f['quad']; qc = q.mean(0)
    e = k ** 1.7
    d = qc - np.array([540., 640.]); d = d / (np.linalg.norm(d) + 1e-6)
    c = qc + (d * 260 + np.array([0, -60])) * (1 - e)
    sc = 1 + 1.9 * (1 - e)
    rot = math.radians((-14 + 28 * K.hrand(f['k'], 3)) * (1 - e))
    R = np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]])
    return c + ((q - qc) * sc) @ R.T

def cards(ctx, faces, t):
    if t < K.O_CONTEUDO - FLIGHT - .02 or t > 11.25: return
    for f in faces:
        k = (t - (f['t_tex'] - FLIGHT)) / FLIGHT
        if k <= 0: continue
        q = f['quad']
        if k >= 1:                                            # landed: stamp flash, the card hands over to the tile
            u = (t - f['t_tex']) / .18
            if u >= 1: continue
            card = K.warp(K.post_card(f['tex'], 300), q)
            if card is not None and u < .75:
                im, x0, y0 = card; ctx.add('behind', E.fade(im, 1 - u / .75), x0, y0, center=False)
            fl = K.warp(Image.new('RGBA', (30, 38), (255, 248, 236, 255)), q)
            if fl is not None:
                im, x0, y0 = fl; ctx.add('behind', E.fade(im, .65 * (1 - u) ** 2), x0, y0, center=False)
            continue
        Q = _card_quad(f, k); Qp = _card_quad(f, max(0., k - (1 / 60) / FLIGHT))
        card = K.warp(K.post_card(f['tex'], 300), Q)
        if card is None: continue
        im, x0, y0 = card
        v = Q.mean(0) - Qp.mean(0)
        im, px, py = K.mblur(im, v[0], v[1])
        ctx.add('behind', E.fade(im, K.clamp(k * 4.5) ** 1.5), x0 - px, y0 - py, center=False)

# ---------------------------------------------------------------------------------------------- VÍDEOS: screens power on
PO_DT, PO_DUR, PO_T0 = .035, .21, .01          # stagger / length / lead (first blink on frame 12.833)

def _po_img(u, w=160, h=190):
    """a screen switching on (CRT style) in a lit window: the pane blinks to black with a white-hot scan line, the line
    opens vertically into a cool-white screen, which fades to reveal the film underneath (the kit's films ramp in
    12.85-13.10)."""
    s = u * PO_DUR
    ad = .93 * (1 - K.smooth((s - .06) / .05))                          # black screen (hides the warm interior)
    k = K.expo((s - .028) / .045) if s > .028 else 0.0                    # the scan line opens 0..1
    hh = max(2.5, h * k)
    y = np.arange(h, dtype=np.float32)[:, None]
    d = np.abs(y - h / 2) / (hh / 2)
    band = np.clip((1.15 - d) / .3, 0, 1)                              # soft-edged band
    core = np.exp(-((y - h / 2) / 1.6) ** 2) * (1 - k)                 # hot line while closed
    aw = np.clip(band * (.75 + .25 * k) + core, 0, 1) * (1 - K.smooth((s - .07) / .13))
    ao = 1 - (1 - ad) * (1 - aw)
    col = (np.array([236, 240, 255], np.float32) * aw[..., None] + np.array([8, 8, 14], np.float32) * (ad * (1 - aw))[..., None]) / np.maximum(ao, 1e-4)[..., None]
    im = np.concatenate([col, ao[..., None] * 255], 2)
    return Image.fromarray(np.clip(np.repeat(im, w, 1), 0, 255).astype(np.uint8), 'RGBA')

def power_on(ctx, hs, t):
    """ON "VÍDEOS" every window in frame powers on like a screen (staggered left to right) while the films ramp in."""
    if not (K.O_VIDEOS - PO_T0 <= t < K.O_VIDEOS - PO_T0 + 4 * PO_DT + PO_DUR): return
    Cw = hs.cam_model(); vis = []
    for i in range(4):
        p = HS.G.win_pane[i]; n = np.array(HS.WALL_N[p['wall']], float)
        if n @ (Cw - p['open'].mean(0)) <= .05: continue
        Q, Z = hs.proj(p['open'] + n * .01)
        if Z.min() < .5 or not (0 < Q[:, 0].mean() < E.W) or Q[:, 1].max() < 0: continue      # (mostly) in frame
        vis.append((Q[:, 0].mean(), i, Q))
    for j, (_, i, Q) in enumerate(sorted(vis, key=lambda v: v[0])):
        u = (t - (K.O_VIDEOS - PO_T0 + j * PO_DT)) / PO_DUR
        if not (0 <= u < 1): continue
        wp = K.warp(_po_img(u), Q)
        if wp is None: continue
        im, x0, y0 = wp; ctx.add('behind', im, x0, y0, center=False)
        c = Q.mean(0); g = K.clamp((u * PO_DUR - .028) / .03) * (1 - K.smooth((u * PO_DUR - .05) / .15))
        if g > .01: ctx.add('behind', K.glow_spot(190, (214, 224, 255), .6 * g), c[0], c[1])

# ---------------------------------------------------------------------------------------------- draw
def draw(ctx, lt, t):
    ctx.captions = False
    st = HS.state_at(t)
    if t < T_CUT2: shot1(ctx, t, st)
    else: shot2(ctx, t, st)

def _jolts(t):
    """camera jolts: one small bump per wall row landing, a bigger one when the roof lands."""
    dx = dy = 0.0
    for r in range(HS.NR):
        a, b = K.shake(t, HS.W_PAREDES + r * HS.ROW_DT, 3.0, dur=.16, freq=14, seed=r); dx += a; dy += b
    a, b = K.shake(t, HS.ROOF_LAND, 9.0, dur=.34, freq=16, seed=9); dx += a; dy += b
    return dx, dy

def shot1(ctx, t, st):
    ctx.bg_img = K.studio_bg(.40, 12.0)
    dx, dy = _jolts(t)
    ctx.cam = dict(z=1.035 + .012 * K.kick(t, HS.ROOF_LAND, 1.0, .3) + .010 * K.kick(t, K.O_CONTEUDO, 1.0, .25),
                   x=540., y=700., dx=dx, dy=dy, rot=0.)
    ctx.avatar = dict(AV1)
    ctx.post['vignette'] = .36
    hs = K.House(st, cam1(t), HSIZE, (0, 0), t=t, fade=HFADE)
    ctx.add('behind', hs.img, 0, 0, center=False)
    tiles = K.tile_faces(hs) if t >= K.O_CONTEUDO - FLIGHT - .02 else []
    cards(ctx, tiles, t)
    if t >= K.O_CONTEUDO - .01:                               # CONTEÚDO pinned to a front-wall post
        faces = {f['k']: f for f in tiles}
        pick = [k for k in HS.G.tiles if HS.PIECES[k]['wall'] == 'F' and HS.PIECES[k]['col'] == 5]
        A = faces[pick[0]]['center'] if pick and pick[0] in faces else hs.proj([HS.ANCHORS['wall_front']])[0][0]
        L = (A[0] + 150, LABEL_Y)
        K.callout(ctx, t, K.O_CONTEUDO, (A[0], A[1]), L, K.label_pill([('CONTEÚDO.', 'grad')], 80), layer='behind', glass=12)
    K.captions(ctx, t, y=1560)

def shot2(ctx, t, st):
    ctx.bg_img = K.studio_bg(.40, 12.0)
    ctx.cam = dict(z=1.03, x=540., y=900., dx=0., dy=0., rot=0.)
    ctx.avatar = dict(AV2)
    ctx.post['vignette'] = .36
    ctx.post['bright'] = 1.0 + sum(.035 * K.kick(t, tw, 1.0, .30) for tw in HS.WIN_T)
    hs = K.House(st, cam2(t), HSIZE, (0, 0), t=t, fade=HFADE)
    ctx.add('behind', hs.img, 0, 0, center=False)
    for i, tw in enumerate(HS.WIN_T):                         # each window switching on flares in the lens
        u = (t - tw) / .42
        if 0 <= u < 1:
            P = hs.proj([HS.ANCHORS['win%d' % i]])[0][0]
            a = (1 - u) ** 2 * min(1, u * 12) * .85
            ctx.add('behind', K.flare(), P[0], P[1], alpha=a)
            ctx.add('behind', K.glow_spot(70, (255, 214, 160), a * .8), P[0], P[1])
    power_on(ctx, hs, t)
    if t >= K.O_VIDEOS - .01:
        A = hs.proj([HS.ANCHORS['win2']])[0][0]
        L = (A[0] + 120, LABEL_Y)
        K.callout(ctx, t, K.O_VIDEOS, (A[0], A[1]), L, K.label_pill([('VÍDEOS.', 'grad')], 80, icon='play'), layer='behind', glass=12)
    K.captions(ctx, t, y=1560)
