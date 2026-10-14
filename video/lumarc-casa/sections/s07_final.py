"""s07 — FINAL: "Com edição… as pessoas entram. Quer construir a sua? Comenta “LUMARC”." + END CARD (32.80–40.56).

SHOT A (32.80, jump cut -> a wide 3/4 on the empty lot, the last wind dust still blowing right).
     COM (32.87): the plinth pops back (kit) — on the word the dust REVERSES (sucked back like tape rewinding), a glass
     ◀◀ chip pops (the same chip family as s04's pause), RGB split + camera kick.  EDIÇÃO (32.98–33.54): every piece
     rewinds into place (kit) with real shutter motion blur while the camera swings back round the house (yaw 50 -> 27).
     -ÇÃO (33.38): all lights on — the chip turns into ▶, bloom punch, anamorphic flares on the windows facing us, a
     warm light sweep crosses the house (hull-masked), exposure lift.  The score's riser keeps building.
     AS PESSOAS (34.10/34.27): on the groove's drop (34.20) the camera dollies in on the door (expo) as it swings open
     (kit) — warm light floods the path, the little figures walk in; ENTRAM (34.70): the first one steps through, the
     doorway light pulses.
SHOT B (35.17, jump cut -> high wide crane: the finished house left, an empty plot beside it).
     QUER (35.20): a second floating lot — "a sua" — pops up beside the house (the kit's lot rise, replayed 3x);
     CONSTRUIR (35.36): the CASA light-line trace replays on it (callback to 6.40: your house starts as the same drawing);
     SUA (35.79): a glass ＋ chip pops inside the blueprint (the empty slot); the camera drifts in on it.  COMENTA (36.78): the word pops and an Instagram comment
     composer (PT-BR UI: avatar, "Adicione um comentário…", Publicar) rises; the field focuses (caret);
     LUMARC (37.21–37.735): the comment types itself, each letter ON its phoneme (L-U-M … -A- on -MAR- 37.50 … C on the
     final k 37.735) — meanwhile the LUMARC sign on the finished house lights (kit, 37.20) with a lens flare.
     37.80 Publicar is tapped -> the word LUMARC flies out of the field into the blueprint lot (light trail)…
END CARD (37.96 = his last word; boom in the score).  …the blueprint PRINTS into the finished, lit house (a scan of
     light rising through it), the studio and he dissolve into LUMARC night space, the camera swings round the new house
     into the end-card hero; logo (light-sweep reveal), "Edição que faz o olho ficar.", CTA pill Comenta “LUMARC”,
     @lumarc_studio · slumarc.com, "SEJA VISTO. SEJA LEMBRADO."; a last light sweep over logo + pill.
Captions: own word pops (engine look) on the measured onsets; COMENTA is a kinetic word above the composer and
“LUMARC” is the typed comment itself (never stacked).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS
from sections import _D_kit as K

START, END = E.span(17, 18)                   # 32.80 – 40.56
J17, J18 = K.J17, K.J18                       # 32.80, 35.1667 (pose jumps -> framing changes)
T_POST = 37.80                                # Publicar tapped
T_HIT = E.VOICE_END                           # 37.96 end card (score boom)
T_PRINT0, T_PRINT1 = 37.97, 38.40             # blueprint -> built house scan
T_LOGO, T_HEAD, T_PILL, T_HANDLE, T_TAG, T_SWEEP = 38.06, 38.36, 38.66, 38.86, 39.06, 39.72

CUES = [c for c in HS.BUILD_CUES if START <= c[0] < END] + [
    (K.O_COM + .01, 'pop', {'gain': -14}),                  # rewind chip
    (33.24, 'whoosh', {'gain': -15}),                       # camera swings back round the house
    (K.O_CAO + .02, 'shimmer', {'gain': -11}),              # lights on: bloom + window flares + light sweep
    (34.27, 'whoosh', {'gain': -13}),                       # dolly in on the door (on the drop; peak mid-move)
    (K.O_ENTRAM, 'shimmer', {'gain': -13}),                 # ENTRAM: the doorway light pulses (review: had no cue)
    (35.22, 'swoosh_up', {'gain': -8}),                     # "a sua": the second lot pops up
    (35.27, 'thud', {'gain': -12}),
    (K.O_CONSTRUIR, 'shimmer', {'gain': -6}),               # blueprint trace (callback to CASA)
    (K.O_CONSTRUIR + .05, 'swoosh_up', {'gain': -15}),
    (K.O_SUA + .01, 'pop', {'gain': -10}),                  # ＋ chip
    (K.O_COMENTA + .02, 'swipe', {'gain': -9}),             # comment composer rises
    (36.98, 'click', {'gain': -8}),                         # field focus
] + [(tt, 'type', {'i': i, 'gain': 5}) for i, tt in enumerate(K.TYPE_T)] + [   # review: +5 dB, -22 dB sat under the drop
    (T_POST, 'click', {'gain': -2}),                        # Publicar
    (T_POST + .01, 'pop', {'gain': -9}),
    (T_POST + .10, 'whoosh', {'gain': -10}),                # the word flies into the lot
    (T_PRINT0 + .01, 'shimmer', {'gain': -6}),              # the house prints (score boom at 37.96)
    (T_LOGO + .04, 'swoosh_up', {'gain': -13}),             # logo light-sweep reveal
    (T_PILL, 'pop', {'gain': -8}),                          # CTA pill
    (T_HANDLE, 'tick', {'gain': -12}),
    (T_TAG, 'tick', {'gain': -16}),                         # tagline (review: landed silently)
    (T_SWEEP, 'shimmer', {'gain': -10}),                    # last sweep
]

HSZ = (1080, 1400)                            # house layer (top of the world frame)
HFADE = (1180, 1400)                          # the lot falls off into the dark behind his shoulders
def sy(y): return (y - HSZ[1] / 2) / HSZ[1]   # frame row -> camera shift
def eio3(x): x = K.clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2

# =============================================================================================== SHOT A
# seg 17's take sits ~60 px lower than segs 8/10 (chin at y≈1600 when placed at +440): raise him so the captions sit on
# the hoodie under his beard, as in s03/s04 (review fix: COM EDIÇÃO… / AS PESSOAS were drawn across his mouth and chin)
AVA = dict(show=True, s=1.00, x=0., y=350., alpha=1.0, copies=[], bright=1.0)
CAP_A = 1592
CA0 = dict(yaw=50.0, pitch=21.0, dist=33.0, fov=30, target=(0.0, 1.3, -0.3), shift=(0, sy(650)))
CA0b = dict(yaw=51.5, pitch=21.5, dist=32.2, fov=30, target=(0.0, 1.3, -0.3), shift=(0, sy(650)))
CA1 = dict(yaw=27.0, pitch=18.0, dist=31.0, fov=30, target=(0.0, 1.9, 0.0), shift=(0, sy(640)))
CA1b = dict(yaw=23.5, pitch=16.5, dist=29.6, fov=30, target=(0.0, 1.85, 0.4), shift=(0, sy(644)))
CA2 = dict(yaw=15.0, pitch=8.5, dist=15.0, fov=30, target=(0.0, 1.55, 2.9), shift=(0, sy(625)))
CA2b = dict(yaw=11.0, pitch=7.0, dist=13.4, fov=30, target=(0.1, 1.50, 3.0), shift=(0, sy(628)))
T_SW0, T_SW1 = 32.95, 33.58                   # camera swing with the rewind
T_P0 = 34.17                                  # dolly to the door, on the groove's drop (34.20)

def camA(t):
    c = K.cam_mix(CA0, CA0b, K.smooth((t - J17) / (T_SW0 - J17)))
    if t >= T_SW0: c = K.cam_mix(c, CA1, eio3((t - T_SW0) / (T_SW1 - T_SW0)))
    if t >= T_SW1: c = K.cam_mix(c, CA1b, K.sio((t - T_SW1) / (T_P0 + .5 - T_SW1)))
    if t >= T_P0:
        c = K.cam_mix(c, CA2, K.expo((t - T_P0) / .62))
        if t >= T_P0 + .5: c = K.cam_mix(c, CA2b, K.smooth((t - T_P0 - .5) / (J18 - T_P0 - .5)))
    return c

BLUR_A = (K.O_COM - .01, 33.62)               # shutter motion blur while the pieces rewind
SHUTTER = tuple(k / 360 for k in range(1, 6))   # 6 samples over a 180-degree shutter (1/60 s)

# wind dust: blowing right (the gust of s06) -> REVERSES on "COM" (rewind) and is sucked back left, gone by 33.5
MOTES = [(K.hrand(i, 41), K.hrand(i, 42), K.hrand(i, 43), K.hrand(i, 44)) for i in range(34)]
def wind_dust(ctx, t):
    if t > 33.55: return
    for i, (a, b, c, d) in enumerate(MOTES):
        sp = .55 + .9 * c
        y = 120 + b * 980 + 22 * math.sin(i * 1.7 + t * 3)
        if t < K.O_COM:
            x = a * 1300 - 110 + 760 * sp * (t - 32.40); v = 760 * sp
        else:
            x0 = a * 1300 - 110 + 760 * sp * (K.O_COM - 32.40)
            u = t - K.O_COM
            x = x0 - (2600 * sp) * (u - .5 * u * u / .7 if u < .7 else .35); v = -2600 * sp * max(0, 1 - u / .7)
        x = (x + 200) % 1480 - 200
        a_ = (.14 + .30 * d) * (1 - K.smooth((t - 33.25) / .3))
        if a_ <= .01: continue
        L = int(min(260, max(12, abs(v) * .022 * (1 + d))))
        r = 1.2 + 2.2 * d
        st = streak(L, r)
        ctx.add('behind', st, x, y, alpha=a_)

def streak(L, r):
    def mk():
        w, h = L + int(4 * r) + 4, int(4 * r) + 4
        im = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(im).rounded_rectangle((4, h - r * 2 + 2, w * 2 - 4, h + r * 2 - 2), r * 2, fill=255)
        im = im.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(r * .6))
        out = Image.new('RGBA', (w, h), (232, 224, 214, 0)); out.putalpha(im); return out
    return K.C(('streak', int(L), round(r, 1)), mk)

def chipA(ctx, t):
    """◀◀ on COM, morphs to ▶ on -ÇÃO, then leaves."""
    if not K.O_COM - .01 <= t < 34.0: return
    lt = t - K.O_COM
    s = .5 + .5 * K.back(lt / .2, 2.2)
    kp = K.clamp((t - K.O_CAO) / .10)
    out = K.smooth((t - 33.72) / .22)
    bump = 1 + .10 * K.kick(t, K.O_CAO, .26)
    x, y = 540, 172 - 16 * out
    a = K.clamp(lt / .05) * (1 - out)
    if kp < 1: ctx.add('screen', K.scale_im(K.chip('rew', 104), s * bump), x, y, alpha=a * (1 - kp), glass=10 if a > .6 else 0)
    if kp > 0: ctx.add('screen', K.scale_im(K.chip('play', 104), s * bump), x, y, alpha=a * kp, glass=10 if a * kp > .6 else 0)

def window_flares(ctx, hs, st, t, cam):
    """anamorphic flares on the windows that face the camera, as the lights come back on (-ÇÃO)."""
    k0 = K.decay(t, K.O_CAO, .30)
    if k0 <= .02: return
    Cw = hs._c.C
    nrm = {0: (0, 0, 1), 1: (0, 0, 1), 2: (1, 0, 0), 3: (1, 0, 0)}
    for i in range(4):
        P = np.array(HS.ANCHORS['win%d' % i], float)
        if np.dot(np.array(nrm[i], float), Cw - P) <= .3: continue
        x, y = hs.anchor('win%d' % i)
        k = k0 * float(st['win'][i])
        if k <= .02: continue
        ctx.add('behind', K.flare(560, 22, (255, 214, 160)), x, y, alpha=min(1, .85 * k))
        ctx.add('behind', K.glow_spot(70, (255, 200, 140), .6 * k), x, y)

def shotA(ctx, t):
    st = HS.state_at(t)
    cam = camA(t)
    ctx.bg_img = K.studio_bg(.42, 12.0)
    glow = 1.0 + .9 * K.decay(t, K.O_CAO, .22) * K.clamp((t - K.O_CAO) / .04) + .45 * K.kick(t, K.O_ENTRAM, .34)
    blur = None
    if BLUR_A[0] <= t < BLUR_A[1]:
        blur = [(HS.state_at(t - d), camA(t - d)) for d in SHUTTER]
    hs = K.House(st, cam, HSZ, (0, 0), t=t, glow=glow, fade=HFADE, blur=blur)
    img = hs.img
    sk = (t - (K.O_CAO + .04)) / .58                             # the light sweep after the lights come on
    if 0 < sk < 1: img = K.sheen_house(img, hs.hull(), K.sio(sk), org=hs.org, half=85, strength=.42)
    ctx.add('behind', img, hs.org[0], hs.org[1], center=False)
    window_flares(ctx, hs, st, t, cam)
    if t >= HS.W_PESSOAS - .1:                                   # the doorway light spills toward the lens
        dx, dy = hs.anchor('door')
        kd = K.smooth((t - (HS.W_PESSOAS - .1)) / .4) * (1 + .5 * K.kick(t, K.O_ENTRAM, .34))
        ctx.add('behind', K.glow_spot(150, (255, 196, 128), min(1, .30 * kd)), dx, dy + 30)
    wind_dust(ctx, t)
    chipA(ctx, t)
    # 2-D camera: kicks on COM, -ÇÃO and the drop
    z = 1.03 + .028 * K.kick(t, K.O_COM, .26) + .016 * K.kick(t, K.O_CAO, .3) + .02 * K.kick(t, 34.20, .32)
    ctx.cam = dict(z=z, x=540., y=800., dx=0., dy=0., rot=0.)
    ctx.avatar = dict(AVA)
    P = ctx.post; P['vignette'] = .34
    if K.O_COM <= t < K.O_COM + .08: P['rgb'] = 5 * (1 - (t - K.O_COM) / .08)
    # s06 ends drained of colour with the studio's monitors dead: on "COM" the colour and the studio light rewind back
    kc = K.expo((t - K.O_COM) / .45) if t >= K.O_COM else 0.0
    P['sat'] = .30 + .70 * kc
    ctx.bg_dim = .40 * (1 - kc)
    P['bright'] = 1 + .06 * K.decay(t, K.O_CAO, .25) * K.clamp((t - K.O_CAO) / .04)
    K.captions(ctx, t, y=CAP_A)

# =============================================================================================== SHOT B + END CARD
AVB = dict(show=True, s=1.00, x=0., y=500., alpha=1.0, copies=[], bright=1.0)
CAP_B = 880                                   # shot B reads in a middle band: lots / words / him
# "a sua": the second lot sits behind-right of the finished house (world offset), so the vertical frame stacks them:
# his lit house big in front, yours (the blueprint) up-right behind it.  Framing solved numerically (review): both
# houses whole, main house ~540 px wide (was ~320), the door + path clear of the word band (y > 760).
O2 = (13.0, 0.0, -15.5)
_TB = (O2[0] / 2, 1.5, O2[2] / 2)
CB0 = dict(yaw=-22.0, pitch=19.0, dist=62.0, fov=30, target=_TB, shift=(52 / 1080, -331 / 1400))
CB1 = dict(yaw=-20.0, pitch=19.0, dist=59.0, fov=30, target=_TB, shift=(52 / 1080, -331 / 1400))   # drifts in on "a sua"
CE0 = dict(yaw=24.0, pitch=21.0, dist=46.0, fov=30, target=(O2[0], 2.0, O2[2] - .2), shift=(0, sy(880)))
CE1 = dict(yaw=30.0, pitch=21.5, dist=45.0, fov=30, target=(O2[0], 2.0, O2[2] - .2), shift=(0, sy(876)))
T_CAM0, T_CAM1 = 37.80, 38.22                 # swing onto the new lot (review: was 37.78-38.42, the lot sat
                                              # top-right over an empty frame until ~38.15)

def camB(t):
    c = K.cam_mix(CB0, CB1, K.sio((t - J18) / (T_CAM0 - J18)))
    if t >= T_CAM0:
        c = K.cam_mix(c, CE0, eio3((t - T_CAM0) / (T_CAM1 - T_CAM0)))
        if t >= T_CAM1: c = K.cam_mix(CE0, CE1, K.smooth((t - T_CAM1) / (END - T_CAM1)) ** .9)
    return c

def blue_state(t):
    """the second lot: the kit's own lot rise (3.89 ->) replayed 3x on QUER, then the CASA light-line trace (6.40 ->)
    replayed 1.25x on CONSTRUIR; the trace channel runs on to complete (no plinth) and holds as a blueprint."""
    if t < 35.19: return None
    if t < K.O_CONSTRUIR: return HS.state_at(min(4.6, HS.W_OLHA + (t - 35.19) * 3.0))
    tp = 6.40 + (t - K.O_CONSTRUIR) * 1.25
    if tp < 6.989: return HS.state_at(tp)
    st = dict(HS.state_at(6.989)); st['outline'] = K.clamp((tp - 6.40) / .62)
    return st

def print_mix(bp, fin, k):
    """scan of light rising through the house: below the scan line the built house, above it the blueprint.
    bp / fin: K.House renders of the same lot + camera (same band)."""
    hull = [(x - fin.org[0], y - fin.org[1]) for x, y in fin.hull()]
    bp, fin = _same_band(bp, fin)
    ys = [p[1] for p in hull]; y0, y1 = min(ys) - 20, max(ys) + 26
    yl = K.lerp(y1, y0, k)
    w, h = bp.size
    yy = np.arange(h, dtype=np.float32)
    m = np.clip((yy - yl) / 14 + .5, 0, 1)                       # 1 below the line
    M = Image.fromarray((np.repeat(m[:, None], w, 1) * 255).astype(np.uint8))
    out = Image.composite(fin, bp, M)
    # the glowing scan line, clipped to the house hull (+ a soft band of light under it)
    hm = Image.new('L', (w, h)); ImageDraw.Draw(hm).polygon([tuple(p) for p in hull], fill=255)
    band = np.exp(-((yy - yl) / 5) ** 2) * 1.0 + np.exp(-((yy - yl) / 26) ** 2) * .35 * (yy > yl)
    B = Image.fromarray((np.clip(np.repeat(band[:, None], w, 1), 0, 1) * 255).astype(np.uint8))
    B = ImageChops.multiply(B, hm.filter(ImageFilter.GaussianBlur(3)))
    a = 1 - K.smooth((k - .85) / .15)
    light = Image.new('RGBA', (w, h), (236, 226, 255, 0)); light.putalpha(B.point(lambda v: int(v * a)))
    out.alpha_composite(light)
    return out, yl

def _same_band(bp, fin):
    """the blueprint render placed into the built render's band (they share lot + camera; normally the same rows)."""
    if bp.org == fin.org and bp.img.size == fin.img.size: return bp.img, fin.img
    out = Image.new('RGBA', fin.img.size, (0, 0, 0, 0))
    out.alpha_composite(bp.img, (int(bp.org[0] - fin.org[0]), int(bp.org[1] - fin.org[1]))) if bp.org[1] >= fin.org[1] else \
        out.paste(bp.img.crop((0, int(fin.org[1] - bp.org[1]), bp.img.width, int(fin.org[1] - bp.org[1]) + fin.img.height)), (0, 0))
    return out, fin.img

def comment_layout(t):
    """composer position (centre) + the kinetic COMENTA row; rises on COMENTA, sinks out after the post."""
    k_in = K.expo((t - (K.O_COMENTA - .02)) / .42)
    k_out = K.smooth((t - (T_POST + .02)) / .16)                 # review: leaves with the word (was gone at 38.07)
    y = 935 + 150 * (1 - k_in) + 170 * k_out ** 1.4
    return y, k_in, k_out

def draw_comment(ctx, t):
    if t < K.O_COMENTA - .03: return
    y, k_in, k_out = comment_layout(t)
    if k_out >= 1: return
    n = sum(1 for tt in K.TYPE_T if t >= tt)
    active = t >= 36.98
    card = K.comment_base(active, n > 0).copy()
    g, xs = K.typed_lumarc()
    ox, oy = 60, 60                                               # card margin in comment_base
    cy = oy + K.CB_H // 2
    tx = ox + K.CB_TX
    flying = t >= T_POST + .02
    if n == 0:
        ph = K.placeholder(); card.alpha_composite(ph, (tx + 4, cy - ph.height // 2))
    elif not flying:
        cut = g.crop((0, 0, int(xs[n]) + (8 if n == 6 else 0), g.height))
        card.alpha_composite(cut, (tx, cy - g.height // 2))
        lt = t - K.TYPE_T[n - 1]
        if lt < .08:                                               # the newest letter pops from its baseline
            li = g.crop((int(xs[n - 1]), 0, int(xs[n]) + (8 if n == 6 else 0), g.height)); s = 1.3 - .3 * K.eout(lt / .08)
            card.paste(Image.new('RGBA', li.size, (26, 26, 36, 215)), (tx + int(xs[n - 1]), cy - g.height // 2))
            li2 = K.scale_im(li, s)
            card.alpha_composite(li2, (int(tx + xs[n - 1] + li.width / 2 - li2.width / 2), int(cy + g.height / 2 - li2.height)))
    # caret: solid while typing, blinks while the field waits
    if active and not flying:
        typing = K.TYPE_T[0] - .05 <= t <= K.TYPE_T[-1] + .12
        if typing or int((t - 36.98) / .27) % 2 == 0:
            cx_ = tx + (xs[n] if n else 6) + 6
            cr = K.C('caret', lambda: E.gradient(5, K.CB_TS + 4, E.GRAD_LIGHT).convert('RGBA'))
            card.alpha_composite(cr, (int(cx_), cy - cr.height // 2))
    # Publicar tap
    s = 1.0
    tp = (t - T_POST) / .34
    px, py = K.publicar_center()
    if 0 <= tp < 1:
        card.alpha_composite(K.ring(70, tp, (120, 190, 255)), (int(px - 78), int(py - 78)))
        s = 1 - .035 * math.sin(math.pi * min(1, tp * 2.2))
    a = K.clamp(k_in * 1.6) * (1 - k_out) ** 1.5
    ctx.add('screen', K.scale_im(card, s), 540, y, alpha=a, glass=16 if a > .6 else 0)
    # COMENTA: kinetic word above the composer
    if t < T_POST + .06:                                          # gone before the typed word flies past it
        ko = K.smooth((t - (T_POST - .03)) / .08)
        K.kinetic_word(ctx, t, 'COMENTA', K.O_COMENTA, 795 - 24 * ko, size=96, alpha=1 - ko)

def lumarc_fly(ctx, t, target):
    """the typed LUMARC leaves the field on Publicar and flies into the blueprint lot (arrives on T_HIT).
    Review rework: one bright projectile with real shutter blur + a tapered light streak (the old trail stacked four
    ghost copies of the word, and the flight crossed COMENTA while it was still on screen)."""
    if not T_POST + .02 <= t < T_HIT + .02: return
    T0, dur = T_POST + .02, T_HIT - T_POST - .02
    y, _, _ = comment_layout(T0)
    g, xs = K.typed_lumarc()
    A = np.array([540 - K.CB_W / 2 + K.CB_TX + g.width / 2, y], float)
    B = np.array(target, float)
    Cc = np.array([K.lerp(A[0], B[0], .25), min(A[1], B[1]) - 60], float)       # lifts out of the field, curves in
    def at(u):
        u = K.clamp(u); e = u ** 1.5                                              # accelerates into the lot
        return (1 - e) ** 2 * A + 2 * (1 - e) * e * Cc + e * e * B, 1.12 - .62 * e
    k = (t - T0) / dur
    # light streak along the path behind the word (additive-looking violet light, tapered)
    us = np.linspace(max(0.0, k - .55), min(1.0, k), 18)
    if len(us) > 1 and k > .02:
        P = np.array([at(u)[0] for u in us])
        x0, y0 = P.min(0) - 40; x1, y1 = P.max(0) + 40
        cw, ch = int(x1 - x0) + 1, int(y1 - y0) + 1
        m = Image.new('L', (cw, ch)); d = ImageDraw.Draw(m)
        for i in range(len(P) - 1):
            q = i / (len(P) - 1); wdt = 3 + 22 * q ** 1.4
            d.line([tuple(P[i] - (x0, y0)), tuple(P[i + 1] - (x0, y0))], fill=int(255 * (.15 + .85 * q)), width=int(wdt))
        m = m.filter(ImageFilter.GaussianBlur(7))
        a_st = (1 - K.smooth((k - .85) / .15))
        st = Image.new('RGBA', (cw, ch), (170, 140, 255, 0)); st.putalpha(m.point(lambda v: int(min(255, v * 1.25) * a_st)))
        core = Image.new('RGBA', (cw, ch), (246, 242, 255, 0)); core.putalpha(m.point(lambda v: int(max(0, v - 150) * 2.2 * a_st)))
        st.alpha_composite(core)
        ctx.add('screen', st, x0, y0, center=False)
    gl = K.C('lumglow', lambda: _glowed(g))
    p, sc = at(k)                                                                 # one crisp word (discrete shutter
    ctx.add('screen', K.scale_im(gl, sc), p[0], p[1], alpha=1 - K.smooth((k - .86) / .14))   # samples strobed as copies)

def _glowed(g):
    pad = 40; out = Image.new('RGBA', (g.width + 2 * pad, g.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new('L', out.size); a.paste(g.getchannel('A'), (pad, pad))
    gl = Image.new('RGBA', out.size, (130, 100, 255, 0)); gl.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .9)))
    out.alpha_composite(gl); out.alpha_composite(g, (pad, pad)); return out

def sign_flare(ctx, hs, st, t):
    """lens flare on the facade sign as it lights (kit: LUMARC 37.20)."""
    k = st['logo'] * K.decay(t, HS.W_LUMARC + .2, .5) if t >= HS.W_LUMARC else 0.0
    if k <= .02: return
    x, y = hs.anchor('sign')
    ctx.add('behind', K.flare(300, 16, (190, 160, 255)), x, y, alpha=min(1, .8 * k))
    ctx.add('behind', K.glow_spot(46, (170, 120, 255), .7 * k), x, y)

def end_overlays(ctx, t):
    """end card type: logo (light-sweep reveal), headline, CTA pill, handle, tagline; last sweep."""
    cx = 540
    LW = 560; LY = 318
    if t >= T_LOGO:
        lg = K.logo_img(LW); k = (t - T_LOGO) / .34
        gl = K.logo_glow(LW)
        s = 1 + .035 * (1 - K.expo((t - T_LOGO) / .5))
        if k < 1:                                                 # feathered wipe left->right behind a soft light bar
            e = K.eout(k); cut = (lg.width + 60) * e - 30
            im = _wipe(lg, cut)
            gp = (gl.width - lg.width) // 2
            gi = _wipe(gl, gp + cut, 80)
            ctx.add('screen', K.scale_im(gi, s), cx, LY, alpha=.9)
            ctx.add('screen', K.scale_im(im, s), cx, LY)
            ex = cx - lg.width / 2 * s + cut * s
            ctx.add('screen', K.flare(460, 20, (200, 180, 255)), ex, LY, alpha=.8 * (1 - k))
            ctx.add('screen', K.C('edge', lambda: _edge(lg.height + 30)), ex, LY, alpha=(1 - k ** 2) * .9)
        else:
            ba = .55 + .12 * math.sin((t - T_LOGO) * 2.4)
            ctx.add('screen', K.scale_im(gl, s), cx, LY, alpha=ba)
            for t0, d in ((T_SWEEP, .7),):
                sk = (t - t0) / d
                if 0 < sk < 1: lg = K.sheen(lg, sk, K.ink_mask(('logo', LW), lg, 90, 200), 40, .6)
            ctx.add('screen', K.scale_im(lg, s), cx, LY)
    if t >= T_HEAD:
        im, m = K.headline(); r = K.rise(im, K.expo((t - T_HEAD) / .45), 36)
        if r is not None:
            sk = (t - (T_SWEEP + .18)) / .6
            if 0 < sk < 1: r = K.sheen(r, sk, m, 30, .5)
            ctx.add('screen', r, cx, 466)
    if t >= T_PILL:
        k = t - T_PILL
        s = (.55 + .45 * K.back(k / .32, 2.4)) * (1 + .016 * (1 - math.cos((t - T_PILL - .32) * 2.6)) if k > .32 else 1)
        py = 1368
        pg = K.cta_glow(); ctx.add('screen', pg, cx, py + 14, alpha=K.clamp(k / .3) * (.75 + .2 * math.sin(t * 2.6)))
        p = K.cta_pill()
        ps = (t - (T_SWEEP + .3)) / .6
        if 0 < ps < 1: p = K.sheen(p, ps, K.ink_mask('pill', K.cta_pill(), 200, 230), 40, .45)
        ctx.add('screen', K.scale_im(p, s), cx, py, alpha=K.clamp(k / .08))
    if t >= T_HANDLE:
        k = K.eout((t - T_HANDLE) / .5); hd = K.handle_im()
        ctx.add('screen', hd, cx, 1490 + 16 * (1 - k), alpha=k)
    if t >= T_TAG:
        k = K.eout((t - T_TAG) / .6); tg = K.tagline_im()
        ctx.add('screen', tg, cx, 1572 + 14 * (1 - k), alpha=k * .9)

def _edge(h):
    """soft light bar riding the logo's wipe edge."""
    w = 70; x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]; y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    a = (np.exp(-(x / .10) ** 2) * .9 + np.exp(-(x / .45) ** 2) * .35) * np.clip(1 - y ** 2, 0, 1) ** 1.5
    im = Image.new('RGBA', (w, h), (236, 230, 255, 0)); im.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))); return im

def _wipe(img, cut, feather=46):
    """img revealed left->right up to column `cut` with a feathered edge."""
    w, h = img.size
    x = np.arange(w, dtype=np.float32)
    m = np.clip((cut - x) / feather + .5, 0, 1)
    a = np.asarray(img.getchannel('A'), np.float32) * m[None, :]
    out = img.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8))); return out

def stage_glow():
    """soft elliptical violet light under the floating lot (end card: a product on a stage)."""
    def mk():
        w, h = 1300, 520
        y, x = np.mgrid[0:h // 2, 0:w // 2].astype(np.float32) * 2
        a = np.exp(-(((x - w / 2) / (w * .30)) ** 2 + ((y - h / 2) / (h * .26)) ** 2) * 1.2)
        im = Image.new('RGBA', (w // 2, h // 2), (104, 76, 255, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.resize((w, h), Image.BILINEAR)
    return K.C('stage', mk)

def bokeh(ctx, t, alpha):
    if alpha <= .02: return
    for i, (x, y, r, a, vx, vy, col) in enumerate(K.BOKEH):
        lt = t - T_HIT
        px = x + vx * lt + 10 * math.sin(lt * .6 + i); py = y + vy * lt
        tw = .8 + .2 * math.sin(t * 1.3 + i * 1.7)
        ctx.add('behind', K.bokeh_sprite(r, col), px, py, alpha=min(1, a * alpha * tw * 2.0))

_SPACE_MIX = {}
def bg_mix(k):
    q = round(k, 2)
    if q not in _SPACE_MIX:
        if len(_SPACE_MIX) > 8: _SPACE_MIX.clear()
        _SPACE_MIX[q] = Image.blend(K.studio_bg(.42, 12.0), K.space(), q)
    return _SPACE_MIX[q]

def shotB(ctx, t):
    cam = camB(t)
    k_sp = K.smooth((t - (K.O_VEND - .02)) / .40)                 # studio -> brand space
    ctx.bg_img = bg_mix(k_sp) if k_sp < 1 else K.space()
    k_fade = K.smooth((t - T_CAM0) / .45)                          # bottom fade of the house layer goes away
    fade = HFADE if k_fade < .02 else (int(K.lerp(HFADE[0], 1500, k_fade)), int(K.lerp(HFADE[1], 1720, k_fade)))
    # ---- main (finished) house: leaves with the camera swing
    a_main = 1 - K.smooth((t - (T_CAM0 + .04)) / .20)            # review: a short focus pull (was a 0.32 s blurred smear)
    st = HS.state_at(t)
    hs = None
    if a_main > .01:
        hs = K.House(st, cam, HSZ, (0, 0), t=t, fade=fade, alpha=a_main)
        if a_main < .99: hs.img = hs.img.filter(ImageFilter.GaussianBlur(9 * (1 - a_main) ** .7))   # leaves the focal plane
    # ---- the second lot: blueprint, then printed into the built house
    bst = blue_state(t)
    hb = None; extra = []
    if bst is not None:
        charge = K.smooth((t - (T_POST + .04)) / (T_HIT - T_POST - .04))
        gb = 1.0 + .18 * math.sin((t - 35.8) * 4.2) * K.clamp((t - 35.9) / .3) + 1.4 * charge * (1 - K.smooth((t - T_HIT) / .3))
        if t < T_PRINT0:
            hb = K.House(bst, cam, HSZ, (0, 0), t=t, O=O2, glow=gb, fade=fade)
            bimg = hb.img
        else:
            fin = K.House(st, cam, HSZ, (0, 0), t=t, O=O2, fade=fade)
            hb = fin
            if t < T_PRINT1:
                bp = K.House(bst, cam, HSZ, (0, 0), t=t, O=O2, glow=gb, fade=fade)
                kpr = K.eout((t - T_PRINT0) / (T_PRINT1 - T_PRINT0)) ** .9
                bimg, yl = print_mix(bp, fin, kpr)
            else:
                bimg = fin.img
    # order: the lot farther from the camera first
    layers = []
    if hs is not None: layers.append((float(np.linalg.norm(hs._c.C - np.array([0, 1, 0]))), hs.img, hs.org))
    if hb is not None: layers.append((float(np.linalg.norm(hb._c.C - np.array([0, 1, 0]))), bimg, hb.org))
    bokeh(ctx, t, K.smooth((t - T_HIT) / .5))
    if hb is not None and t >= T_HIT - .1:                         # end card: the lot floats over a pool of violet light
        gx, gy = hb.proj([[0, -HS.LOT_TH - .6, 0]])[0][0]
        ctx.add('behind', stage_glow(), gx, gy + 20, alpha=.55 * K.smooth((t - T_HIT) / .5))
    for _, img, org in sorted(layers, key=lambda x: -x[0]):
        ctx.add('behind', img, org[0], org[1], center=False)
    if hs is not None: sign_flare(ctx, hs, st, t)
    # hit: the word lands -> light burst on the lot
    if hb is not None and t >= T_HIT - .02:
        kb = K.decay(t, T_HIT, .22)
        p = hb.proj([[0, 2.0, HS.ZH]])[0][0]
        if kb > .02:
            ctx.add('behind', K.glow_spot(260, (170, 140, 255), min(1, .9 * kb)), p[0], p[1])
            kr = (t - T_HIT) / .42
            if kr < 1: ctx.add('behind', K.soft_ring(520, kr), p[0], p[1] + 60)
    # ＋ chip over the blueprint (SUA)
    if hb is not None and K.O_SUA - .01 <= t < T_POST + .1:
        lt = t - K.O_SUA
        px, py = hb.proj([[0, HS.YS + 1.9, HS.ZH + .6]])[0][0]     # floats INSIDE the blueprint: the empty slot
        s = .5 + .5 * K.back(lt / .22, 2.2)
        bob = 6 * math.sin((t - K.O_SUA) * 3.0)
        a = K.clamp(lt / .05) * (1 - K.smooth((t - T_POST) / .1))
        ctx.add('screen', K.scale_im(K.chip('plus', 92), s), px, py + bob, alpha=a, glass=10 if a > .6 else 0)
        kr = lt / .5
        if 0 <= kr < 1: ctx.add('screen', K.ring(90, kr), px, py + bob)
    # the comment, and the word flying into the lot
    draw_comment(ctx, t)
    if hb is not None: lumarc_fly(ctx, t, hb.proj([[0, 2.2, HS.ZH]])[0][0])
    # him: fades with his last word
    av = dict(AVB); av['alpha'] = 1 - K.smooth((t - (K.O_VEND - .02)) / .24)
    if av['alpha'] <= .01: av['show'] = False
    ctx.avatar = av
    z = 1.02 + .012 * K.kick(t, K.O_QUER, .3) + .02 * K.kick(t, T_HIT, .34) * (1 - k_sp * 0)
    ctx.cam = dict(z=z, x=540., y=820., dx=0., dy=0., rot=0.)
    P = ctx.post; P['vignette'] = .34 - .06 * k_sp
    if t >= T_HIT: P['rgb'] = 3.5 * K.clamp(1 - (t - T_HIT) / .07)
    K.captions(ctx, t, y=CAP_B)
    if t >= T_HIT - .2: end_overlays(ctx, t)

# =============================================================================================== draw
def draw(ctx, lt, t):
    ctx.captions = False
    if t < J18: shotA(ctx, t)
    else: shotB(ctx, t)
