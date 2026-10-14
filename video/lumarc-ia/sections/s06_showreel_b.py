"""s06 — THE SHOWREEL, PART B (37.04–43.40).  "Um clone seu… ou três." / "Uma casa que se constrói na sua frente." /
"E um vídeo que você não consegue parar de assistir."

A  CLONES (37.04 JUMP).  Punch into a centred close-up in the studio.  "CLONE" (37.32): a light seam slices the frame
   down the middle and he SPLITS in two — the halves slide apart (cell division) and the right one, a MIRRORED twin,
   lands in a real location from the LUMARC portfolio (the cosy office of the "Couples Therapy" film: window + leather
   armchair, warm daylight grade, DOF, light wrap).  The pause after "seu…" is DEAD SILENT (the beat stops): both of
   him just stare at you while the camera creeps in.  "OU" (38.35) both panels lean left (making room) and on "TRÊS"
   (38.565) a third panel slams in (the beach — clone #3 is on vacation) — the three clones POP one after another
   (pop pop pop, L -> R, each with a flash): a triptych studio / office / beach (purple / amber / cyan).  The location
   plates differ from s05's set swaps on purpose (Paris/café/rooftop/boardroom were just seen there; only the beach
   repeats, as the punchline).
B  THE HOUSE (39.00 JUMP).  New shot: low, wider; he sits behind the desk line.  "CASA" (39.375): the LUMARC maquette
   (the casa film's house kit) rises into frame in front of him and the focus racks onto it (he goes soft).  Its build
   is a 2-s time-lapse of the casa timeline: light-line trace -> plinth on "QUE" -> wall blocks rain down on
   "CONSTRÓI" -> the roof slams on its stressed "TRÓI" (40.11) -> windows switch on "NA… SUA" -> the windows start
   playing LUMARC films -> "FRENTE" (40.535): the door slams and the camera pushes in toward YOU (in front of you);
   the purple CTA light flickers on and a sheen sweeps the finished, lit house.  The house light spills onto him.
C  THE FEED (41.08 JUMP).  Tight on him (we are INSIDE a Reel).  "VÍDEO" (41.35): crash pull-back — the frame
   becomes the @lumarc_studio Reel in a dark Instagram feed (full-screen phone UI).  "que VOCÊ" a fingertip lands
   and flicks the feed up... it SPRINGS BACK on "NÃO".  "conSEgue": a harder fling, the feed whizzes past three
   posts (scroll blur)... and gets yanked back and SLAMS into place on "PARAR".  "ASSISTIR" (42.785): the slam
   cracked the screen (impact star at his chest), "-SSIS-" the cracks race to the edges and the web closes, and on
   "-TIR" (43.075) the glass SHATTERS toward the lens — he's out of the phone, back in the real studio (camera dolly
   forward) for s07.
Captions: own word pops (engine look) on onsets measured on src/tight16k.raw (bottom for A/C, top for B, never on
his face).
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _D_kit as K

START, END = E.span(15, 18)                   # 37.04 – 43.40
T15, T17, T18 = E.TL[15]['t0'], E.TL[17]['t0'], E.TL[18]['t0']     # 37.04, 39.00, 41.08 (JUMP cuts)
W, H = E.W, E.H
clamp, eout, ein, back, lerp, smooth, expo = K.clamp, K.eout, K.ein, K.back, K.lerp, K.smooth, K.expo

# word onsets measured on src/tight16k.raw (5 ms STFT spectrogram + 10 ms RMS of 80-900 Hz / 1-3 kHz / >3.5 kHz
# bands, out/D/spec.png): plosive bursts after their closure, fricative starts, vowel onsets after a pause
O = dict(UM=37.13, CLONE=37.32, SEU=37.66, SEU_END=37.96,         # k burst 37.32 | s of "seu" 37.665 (vowel 37.81)
         OU=38.35, TRES=38.565, TRES_END=38.90,                     # t burst 38.565 (vowel 38.585, s 38.745)
         UMA=39.09, CASA=39.375, QUE=39.665, SE=39.705,             # k 39.375 | k 39.665 | s 39.705
         CONSTROI=39.865, TROI=40.11, NA=40.245, SUA=40.335,        # k 39.865, "-TRÓI" t 40.105 | n 40.245 | s 40.335
         FRENTE=40.535, FRENTE_END=40.95,                           # f 40.535 (vowel 40.665)
         E=41.175, UM2=41.26, VIDEO=41.345, VI=41.445,              # v 41.345, stressed í 41.445
         QUE2=41.665, VOCE=41.745, NAO=41.95,                       # k 41.665 | v 41.745 | n 41.95
         CONSEGUE=42.14, SE2=42.285, GUE=42.465,                    # k 42.14 | s 42.285 | g 42.465
         PARAR=42.585, DE=42.695, ASSISTIR=42.785, SSIS=42.885,     # p burst 42.585 | d 42.695 | a 42.785 | s 42.885
         TIR=43.075, END=43.30)                                      # "-TIR" affricate 43.075

# ---------------------------------------------------------------- A: clones
SPLIT = O['CLONE'] - .02                       # the seam lands on "CLONE"
SPLIT_D = .17
TRI0 = O['TRES'] - .045                        # third panel slams in, lands on "TRÊS"
TRI_D = .13
POPS = [O['TRES'] + .01, O['TRES'] + .075, O['TRES'] + .14]
# ---------------------------------------------------------------- B: house
RISE0 = O['CASA'] - .06
PUSH0 = O['FRENTE'] - .03
HOUSE_KNOTS = [(T17, 3.40), (O['CASA'], 3.89), (39.53, 4.50), (39.53, 6.38), (O['QUE'], 7.00), (39.79, 7.45),
               (39.79, 9.38), (O['CONSTROI'], 9.56), (O['TROI'], 11.22), (O['NA'], 11.59), (O['SUA'], 12.24),
               (40.40, 12.90), (40.40, 13.38), (O['FRENTE'], 13.72), (40.62, 14.00), (40.62, 15.38), (40.72, 15.62),
               (40.72, 16.30), (T18 + .05, 17.15)]
# ---------------------------------------------------------------- C: feed
PULL0, PULL_D = O['VIDEO'] - .05, .17          # crash pull-back into the feed, lands on the stressed "VÍ"
K0 = 1.48                                      # media-fills-the-frame scale of the feed before the pull-back
TOUCH1, FLICK1, BACK1 = O['QUE2'] - .04, O['VOCE'] + .07, O['NAO']
TOUCH2, FLICK2, YANK2, SLAM = O['CONSEGUE'] - .05, O['SE2'] - .03, O['GUE'] + .02, O['PARAR']
IMPACT = (566.0, 1190.0)                       # his upper chest in the Reel (where the slam cracks the glass)
BREAK = O['TIR']

CUES = [
    (T15, 'whoosh', {'gain': -14}),                                   # punch into the close-up
    (SPLIT - .01, 'shing', {'gain': -9}),                             # light seam slices the frame
    (SPLIT + .02, 'swipe', {'gain': -5}),                            # he splits in two
    (SPLIT + .12, 'pop', {'gain': -8, 'pan': .45}),                   # the clone lands in the office
    (O['OU'] + .02, 'flick', {'gain': -16, 'pan': -.3}),              # panels lean (anticipation)
    (TRI0 + .02, 'swipe', {'gain': -6, 'pan': .5}),                  # third panel slams in
    (POPS[0], 'pop', {'gain': -5, 'pan': -.55}),                      # pop
    (POPS[1], 'pop', {'gain': -5, 'pan': 0.0}),                       # pop
    (POPS[2], 'pop', {'gain': -5, 'pan': .55}),                       # pop
    (RISE0 + .02, 'swoosh_up', {'gain': -5}),                         # the lot rises into frame on "CASA"
    (O['CASA'] + .16, 'thud', {'gain': -8}),                          # ...and settles
    (39.53, 'shimmer', {'gain': -6}),                                 # light-line trace
    (O['QUE'] + .01, 'stone', {'gain': -2}),                          # plinth extrudes
    (O['CONSTROI'] + .005, 'block', {'seed': 0, 'gain': -1}),         # wall rows rain down
    (O['CONSTROI'] + .05, 'block', {'seed': 1, 'gain': -3}),
    (O['CONSTROI'] + .095, 'block', {'seed': 2, 'gain': -4}),
    (40.036, 'flick', {'gain': -9}),                                  # content panels ripple in (casa 10.72)
    (O['TROI'] - .04, 'whoosh', {'gain': -12}),                       # the roof drops...
    (O['TROI'], 'thud', {'gain': 0}),                                 # ...and slams on "-TRÓI"
    (O['TROI'] + .02, 'stone', {'gain': -9}),
    (O['NA'], 'switch', {'gain': -3, 'pan': -.35}),                   # windows on, one by one
    (O['NA'] + .03, 'switch', {'gain': -5, 'pan': .1}),
    (O['NA'] + .06, 'switch', {'gain': -6, 'pan': .35}),
    (O['SUA'], 'switch', {'gain': -6, 'pan': .55}),
    (40.393, 'flick', {'gain': -7}),                                  # the windows start playing films
    (O['FRENTE'], 'door', {'gain': 0}),                               # the door slams on "FRENTE"
    (PUSH0 + .01, 'zoom', {'gain': -9}),                              # push-in toward you
    (40.637, 'switch', {'gain': -6}),                                 # CTA light
    (40.74, 'shimmer', {'gain': -9}),                                 # sheen over the lit house
    (T18, 'whoosh', {'gain': -11}),                                   # cut: tight, inside a Reel
    (PULL0 + .02, 'zoom', {'gain': -4}),                              # crash pull-back into the feed
    (PULL0 + PULL_D, 'notify', {'gain': -12}),                        # ...the feed lands
    (TOUCH1, 'click', {'gain': -4}),                                  # fingertip on the glass
    (FLICK1, 'swipe', {'gain': -3}),                                  # flick 1
    (BACK1, 'rewind', {'dur': .16, 'gain': -6}),                      # ...it springs back on "NÃO"
    (BACK1 + .10, 'thud', {'gain': -12}),
    (TOUCH2, 'click', {'gain': -4}),
    (FLICK2, 'swipe', {'gain': 0}),                                   # flick 2, harder
    (FLICK2 + .03, 'ff', {'dur': .24, 'gain': -6}),                   # the feed whizzes past
    (YANK2, 'rewind', {'dur': .12, 'gain': -3}),                      # yanked back...
    (SLAM, 'impact', {'gain': -2}),                                   # ...SLAMS into place on "PARAR"
    (SLAM + .01, 'knock', {'seed': 2, 'gain': -6}),
    (O['ASSISTIR'], 'crack', {'dur': .3, 'seed': 7, 'gain': -1}),     # the screen cracks
    (O['SSIS'], 'crack', {'dur': .22, 'seed': 9, 'gain': -4}),        # cracks race to the edges
    (O['SSIS'] + .02, 'glass', {'seed': 4, 'gain': -10}),
    (BREAK, 'shatter', {'dur': 1.3, 'gain': 0}),                      # SHATTER on "-TIR"
    (BREAK, 'boom', {'gain': -3}),
    (BREAK + .04, 'whoosh', {'gain': -6}),                            # shards fly past the lens
]

# ---------------------------------------------------------------- captions (measured onsets)
F, T = False, True
PAGES_A = [(O['UM'] - .04, O['OU'] - .04, [('UM', O['UM'], F), ('CLONE', O['CLONE'], T), ('SEU…', O['SEU'], F)]),
           (O['OU'] - .04, T17, [('OU', O['OU'], F), ('TRÊS.', O['TRES'], T)])]
PAGES_B = [(O['UMA'] - .04, O['QUE'] - .02, [('UMA', O['UMA'], F), ('CASA', O['CASA'], T)]),
           (O['QUE'] - .02, O['NA'] - .02, [('QUE', O['QUE'], F), ('SE', O['SE'], F), ('CONSTRÓI', O['CONSTROI'], F)]),
           (O['NA'] - .02, T18, [('NA', O['NA'], F), ('SUA', O['SUA'], F), ('FRENTE.', O['FRENTE'], T)])]
PAGES_C = [(O['E'] - .04, O['QUE2'] - .02, [('E', O['E'], F), ('UM', O['UM2'], F), ('VÍDEO', O['VIDEO'], F)]),
           (O['QUE2'] - .02, O['CONSEGUE'] - .02, [('QUE', O['QUE2'], F), ('VOCÊ', O['VOCE'], F), ('NÃO', O['NAO'], T)]),
           (O['CONSEGUE'] - .02, O['PARAR'] - .02, [('CONSEGUE', O['CONSEGUE'], F)]),
           (O['PARAR'] - .02, END, [('PARAR', O['PARAR'], F), ('DE', O['DE'], F), ('ASSISTIR.', O['ASSISTIR'], T)])]


def bump(u, d=.16):
    """0 -> 1 -> 0 pop envelope (fast attack, damped)."""
    if u < 0 or u > d * 1.6: return 0.0
    x = u / d
    return math.sin(math.pi * min(x, 1.0)) * (1 - .35 * min(x, 1.0)) if x < 1 else -.08 * math.sin(math.pi * (x - 1) / .6)


# ================================================================ A: clones
def seam_img():
    def mk():
        w = 64; im = Image.new('RGBA', (w, H), (0, 0, 0, 0)); a = np.zeros((H, w), np.float32)
        xx = np.arange(w, dtype=np.float32) - w / 2
        sh = np.exp(-(xx / 14) ** 2) * .55                                # soft contact shadow
        a[:] = sh[None]
        rgb = np.zeros((H, w, 3), np.float32) + 6
        core = (np.abs(xx) < 2.6).astype(np.float32)                       # the gap
        a = np.maximum(a, core * .92)
        hl = np.exp(-((np.abs(xx) - 3.2) / .9) ** 2) * .55                # glass edge highlights
        rgb = rgb + hl[None, :, None] * np.array([235, 232, 255], np.float32)
        a = np.maximum(a, hl[None] * .9)
        return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8), 'RGBA')
    return K.C('seam', mk)


def seam_flash():
    def mk():
        w = 260; xx = np.arange(w, dtype=np.float32) - w / 2
        a = np.exp(-(xx / 5) ** 2) + .45 * np.exp(-(xx / 40) ** 2)
        a = np.repeat(a[None], H, 0) * np.clip(1 - np.abs(np.linspace(-1, 1, H, dtype=np.float32)) ** 6, 0, 1)[:, None]
        rgb = np.zeros((H, w, 3), np.float32) + np.array([226, 214, 255], np.float32)
        return Image.fromarray(np.dstack([rgb, np.clip(a * 255, 0, 255)]).astype(np.uint8), 'RGBA')
    return K.C('seamflash', mk)


def draw_clones(ctx, t):
    av = K.av_frame(ctx, t)
    if av is None: av = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    creep = .035 * smooth((t - O['SEU_END']) / (O['OU'] - O['SEU_END']))     # the camera creeps in during the silence
    fr = None
    if t < SPLIT:
        # single centred close-up in the studio (punched in at the JUMP — tighter than the house/default framings)
        z = 1.28 + .05 * math.exp(-(t - T15) / .07) + .03 * smooth((t - T15) / .3)
        fr = K.panel(av, 'studio', W, 540 + 12, z=z, pz=1.0 + .5 * (z - 1), oy=700 * (z - 1))
    else:
        e = expo((t - SPLIT) / SPLIT_D)
        q = expo((t - TRI0) / TRI_D) if t >= TRI0 else 0.0
        lean = 26 * smooth((t - O['OU']) / .12) * (1 - q)                     # "ou": both lean left (making room)
        zs = lerp(1.31, 1.0, e); oys = 700 * (zs - 1)
        z2 = zs + creep
        z3 = 0.93 * (1 + .035 * smooth((t - TRI0 - .10) / .45))           # keeps pushing after the pops (no static hold)
        s1 = lerp(540 - lean, 360, q)                                          # seams
        s2 = lerp(W + 40, 720, q)
        cxL = lerp(540, s1 / 2 + 6, e)                                         # faces: centred in their panels
        cxR = lerp(540, (s1 + min(s2, W)) / 2 + 6, e)
        z = lerp(z2, z3, q)
        pops = [bump(t - p) for p in POPS]
        fr = Image.new('RGB', (W, H))
        # left: the original, in his studio
        p1 = K.panel(av, 'studio', int(round(s1)), cxL, z=z * (1 + .08 * pops[0]), pz=1.0 + .5 * (z - 1), oy=oys)
        fr.paste(p1, (0, 0))
        # right/middle: the clone in the therapy office (slides apart from the centre on "CLONE")
        x0 = int(round(s1)); w2 = int(round(min(s2, W) - s1))
        if w2 > 2:
            p2 = K.panel(av, 'office', w2, cxR - x0, z=z * (1 + .08 * pops[1]), pz=1.0 + .4 * (z - 1), pdx=-120 * (1 - e) + 40 * q, flip=True, oy=oys)
            fr.paste(p2, (x0, 0))
        # third: the beach clone slams in from the right on "TRÊS"
        if q > 0 and s2 < W - 1:
            x3 = int(round(s2)); w3 = W - x3
            cx3 = (W - s2) / 2 + 6 + 160 * (1 - q)
            p3 = K.panel(av, 'beach', w3, cx3, z=z * (1 + .08 * pops[2]), pz=1.0 + .4 * (z - 1), pdx=0)
            fr.paste(p3, (x3, 0))
        fr = fr.convert('RGBA')
        # per-panel pop flash
        for i, (p, xa, xb) in enumerate(zip(POPS, (0, s1, s2), (s1, s2, W))):
            u = t - p
            if 0 <= u < .2 and xb > xa + 2:
                k = .30 * math.exp(-u / .045)
                fl = Image.new('RGBA', (int(xb - xa), H), (236, 230, 255, int(255 * k)))
                fr.alpha_composite(fl, (int(xa), 0))
        # seams (+ a light flash running down the cut on "CLONE")
        for s in (s1, s2):
            if 2 < s < W - 2: K.paste(fr, seam_img(), s, H / 2)
        u = t - SPLIT
        if -.01 < u < .25:
            k = math.exp(-max(0, u) / .08)                                     # full strength on the split frame
            K.paste(fr, seam_flash(), s1, H / 2, alpha=min(1, k))
        if t >= TRI0 and t < TRI0 + .25:
            k = clamp((t - TRI0) / .03) * math.exp(-(t - TRI0 - .03) / .07) * .8
            K.paste(fr, seam_flash(), s2, H / 2, alpha=min(1, max(0, k)))
    ctx.full = fr
    ctx.post['vignette'] = .28
    K.caps_layer(ctx, t, PAGES_A, y=1500)


# ================================================================ B: house
def house_t(t): return K.piecewise(HOUSE_KNOTS, t)


def house_cam(t):
    """3/4 orbit while it builds (ridge stays under his chin); on "FRENTE" a decisive push-in to the front door —
    the lit house comes at you and fills the frame."""
    u = smooth((t - T17) / (T18 - T17))
    p = expo((t - PUSH0) / .40) if t >= PUSH0 else 0.0
    yaw = lerp(10, 25, u); pitch = lerp(18, 14.5, u); dist = lerp(26.0, 24.5, u)
    creep = 1.1 * smooth((t - 40.86) / .26)              # keeps drifting in after the push settles (no static hold)
    return dict(yaw=lerp(yaw, yaw + 5, p), pitch=lerp(pitch, 5.5, p), dist=lerp(dist, 15.0, p) - creep * p, fov=HS_FOV,
                target=(0.0, lerp(1.7, 1.75, p), lerp(0.0, 3.0, p)), shift=(0.0, lerp(.261, .175, p)))


HS_W, HS_H = 1080, 1700
HS_FOV = 2 * math.degrees(math.atan(HS_H / 1400 * math.tan(math.radians(15))))   # same scale as a 1400-px fov-30 layer


def house_layer(t):
    HSk = E.house(); ct = house_t(t); st = HSk.state_at(ct)
    return HSk.render(st, house_cam(t), size=(HS_W, HS_H), t=ct, ss=2, shadow=False), st


def warm_glow():
    return K.glow_sprite(900, 520, (255, 196, 128), 120, .9)


def purple_glow():
    return K.glow_sprite(1100, 700, (130, 90, 255), 150, .9)


def kick(t):
    """camera kick (screen dy) when the roof slams on "-TRÓI" and the door slams on "FRENTE"."""
    for tk, amp in ((O['TROI'], 9), (O['FRENTE'], 6)):
        u = t - tk
        if 0 <= u < .17:
            k = int(u * E.FPS); tab = [0, 1, -.6, .3, -.1]
            if k < len(tab): return tab[k] * amp
    return 0.0


def draw_house(ctx, t):
    lt = t - T17
    # him: lower, wider shot (snap in at the JUMP), slow push; focus racks to the house on "CASA"
    z = 1.02 + .03 * smooth(lt / 2.1) + .05 * math.exp(-lt / .07)
    ky = kick(t)
    ctx.cam.update(z=z, x=540., y=900., dy=ky)
    rack = smooth((t - O['CASA'] - .02) / .32)
    hl, st = house_layer(t)
    lights = float(st['lights']) if t >= O['NA'] - .01 else 0.0
    rise = 1 - expo((t - RISE0) / .34) if t >= RISE0 else 1.0
    p = expo((t - PUSH0) / .42) if t >= PUSH0 else 0.0
    hx, hy = 540, H - HS_H / 2 + 1100 * rise ** 1.2 + ky
    # once the pushed-in house hides him completely, skip him (saves the key)
    if p > .3:
        a = np.asarray(hl.getchannel('A')); lx0, ly0 = int(hx - HS_W / 2), int(hy - HS_H / 2)
        def covered(x0, x1, y0, y1):          # take-coordinate box -> screen (world camera) -> house layer
            X0, X1 = int(540 + (x0 - 540) * z) - lx0, int(540 + (x1 - 540) * z) - lx0
            Y0, Y1 = int(900 + (y0 - 900) * z + ky) - ly0, int(900 + (y1 - 900) * z + ky) - ly0
            if X0 < 0 or Y0 < 0 or X1 > a.shape[1] or Y1 > a.shape[0] + 400: return False
            sub = a[Y0:min(Y1, a.shape[0]):16, X0:X1:16]
            return sub.size > 0 and sub.min() > 250
        if covered(380, 700, 530, 1000) and covered(120, 960, 1000, 1500): ctx.avatar['show'] = False
    def wrap(fr):
        fr = fr.convert('RGB')
        r = 6.0 * rack + 2.5 * p
        if r > .2:   # rack focus (half-res blur)
            fr = fr.resize((W // 2, H // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / 2)).resize((W, H), Image.BILINEAR)
        # pull the eye to the house: darken the lower frame a touch under it
        g = K.C('lowdark', lambda: Image.fromarray((np.clip((np.arange(H, dtype=np.float32) - 900) / 1000, 0, 1) ** 1.3 * 120)
                                                   .astype(np.uint8)[:, None].repeat(W, 1)))
        kd = clamp(1.4 * (1 - rise))
        if kd > .01: fr = Image.composite(Image.new('RGB', (W, H), (6, 5, 12)), fr, g if kd >= .999 else g.point(lambda v: int(v * kd)))
        ant = .5 * smooth((t - (T17 + .10)) / .25)          # anticipation: the bounce glows up from below before the lot
        fr = K.add_light(fr, purple_glow(), hx, min(hy - 120, H + 60), .38 * max(1 - rise, ant))
        if lights > .01: fr = K.add_light(fr, warm_glow(), hx + 30, hy - 260, .30 * lights)    # house light on him
        return fr.convert('RGBA')
    ctx.wrap = wrap
    if t >= RISE0 - .01:
        ctx.add('screen', hl, hx, hy)
    ctx.captions = False
    K.caps_layer(ctx, t, PAGES_B, y=330)


# ================================================================ C: feed + glass
def fk(): return K.feedkit()
def gk(): return K.glasskit()


def snapback(u, A, dur=.11, ov=.07, settle=.16):
    """content offset A springing back to 0 (ease-in snap, small overshoot past 0, settle)."""
    if u < 0: return A
    if u < dur: return A * (1 - ein(u / dur))
    v = (u - dur) / settle
    return -A * ov * math.sin(math.pi * min(v, 1)) * (1 - min(v, 1)) if v < 1 else 0.0


def scroll(t):
    """extra feed scroll (content px, + = content moves up) — the two failed swipes."""
    if t < TOUCH1: return 0.0
    if t < FLICK1: return 70 * smooth((t - TOUCH1) / (FLICK1 - TOUCH1))
    if t < BACK1: return 70 + 560 * eout((t - FLICK1) / (BACK1 - FLICK1))
    if t < TOUCH2: return snapback(t - BACK1, 630)
    if t < FLICK2: return 85 * smooth((t - TOUCH2) / (FLICK2 - TOUCH2))
    if t < YANK2: return 85 + 2650 * (1 - (1 - clamp((t - FLICK2) / (YANK2 - FLICK2))) ** 2.2)
    return snapback(t - YANK2, 2735, dur=SLAM - YANK2, ov=.025, settle=.14)


def scroll_speed(t):
    return (scroll(t + 1 / 120) - scroll(t - 1 / 120)) * 60          # px per second


def media_cam(t):
    """camera of the Reel's content (his studio world): a gentle push."""
    return dict(z=1.0 + .03 * smooth((t - T18) / 2.3), x=540., y=960., dx=0., dy=0., rot=0.)


def feed_k(t):
    if t < PULL0: return K0 * (1 + .025 * smooth((t - T18) / .3))
    return lerp(K0 * 1.025, 1.0, expo((t - PULL0) / PULL_D))


def slam_shake(t):
    u = t - SLAM
    if not (0 <= u < .25): return 0.0, 0.0
    k = int(u * E.FPS); tab = [(0, 0), (0, 22), (-10, -12), (6, 7), (-3, -3), (1, 2), (0, 0)]
    return tab[k] if k < len(tab) else (0, 0)


def feed_frame(ctx, t, with_chrome=True):
    """the full-screen phone feed at t (RGBA): chrome + posts, his Reel live in post SPECIAL, scroll blur, pull-back."""
    FK = fk()
    k = feed_k(t); sc = FK.center_scroll(FK.SPECIAL) + scroll(t)
    cam = media_cam(t)
    mx, my, mw, mh = FK.media_rect(FK.SPECIAL, sc)
    if k <= 1.0005:
        media = None
        if my < H and my + mh > 0:
            media = ctx.compose(cam=cam).convert('RGB').crop((0, 300, W, 300 + mh))
        scr = FK.screen(sc, special=media, t=t, chrome=False)
        # scroll blur on the content only (box shutter ~1/50 s); the app chrome stays crisp
        v = scroll_speed(t)
        L = clamp(abs(v) / 50.0, 0, 340) * (1 if v > 0 else -1)
        if abs(L) > 3: scr = K.vsmear(scr, L).convert('RGBA')
        scr.alpha_composite(FK.chrome_top(), (0, 0)); scr.alpha_composite(FK.chrome_nav(), (0, FK.NAV_Y))
    else:
        # zoomed into the media: render the world straight at screen resolution (crisp), feed scaled around it
        Mx, My = 540.0, my + mh / 2.0
        base = FK.screen(sc, special=Image.new('RGB', (W, mh), (0, 0, 0)), t=t).convert('RGB')
        scr = E.zoom(base, k, (Mx, My)).convert('RGBA')
        A = (cam['x'], cam['y'])
        z = cam['z'] * k
        # world point A maps to media pixel (A[0], A[1] - 300 + my) at scale 1 -> screen M + (that - M) * k
        Sx = Mx + (A[0] - Mx) * k; Sy = My + (A[1] - 300 + my - My) * k
        wf = ctx.compose(cam=dict(z=z, x=A[0], y=A[1], dx=Sx - A[0], dy=Sy - A[1], rot=0.)).convert('RGB')
        x0 = int(round(Mx - mw / 2 * k)); y0 = int(round(My - mh / 2 * k))
        x1 = int(round(Mx + mw / 2 * k)); y1 = int(round(My + mh / 2 * k))
        x0c, y0c, x1c, y1c = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1c > x0c and y1c > y0c: scr.paste(wf.crop((x0c, y0c, x1c, y1c)), (x0c, y0c))
        ov = FK._reel_overlay()                                    # the reel badges, scaled
        E._paste(scr, dict(img=ov.resize((int(ov.width * k), int(ov.height * k)), Image.BILINEAR), xy=(x0, y0), glass=0))
        # crash pull-back: radial smear while the scale is moving fast
        dk = abs(feed_k(t + 1 / 60) - feed_k(t - 1 / 60)) * 30 / max(k, 1e-3)
        if dk > .05: scr = K.zoom_smear(scr, min(.06, dk / E.FPS * .6), (Mx, My))
    return scr


def touch_layer(fr, t):
    """the fingertip: lands, drags with the content, flicks up and lifts off (twice)."""
    for t0, t1, (x, y) in ((TOUCH1, FLICK1, (770.0, 1300.0)), (TOUCH2, FLICK2, (735.0, 1360.0))):
        if not (t0 - .01 <= t < t1 + .10): continue
        land = clamp((t - t0) / .05)
        dy = -(scroll(min(t, t1)) - scroll(t0))
        a = land
        if t > t1:                                        # flick + lift-off: keeps going up, fades and shrinks
            u = (t - t1) / .10; dy -= 420 * u; a *= (1 - u)
        sp = K.touch_sprite(48)
        s = 1.12 - .12 * land
        img = K.scale_im(sp, s)
        if t > t1:
            L = int(120 * clamp((t - t1) / .03))
            if L > 4:                                     # motion smear of the flick (continuous, not stacked copies)
                img = K.vsmear_rgba(img, L); dy += L / 2
        K.paste(fr, img, x, y + dy, alpha=a)
        rk = (t - t0) / .32                               # contact ripple
        if 0 <= rk < 1:
            R = 50 + 70 * eout(rk); ring = K.ring_sprite(R, 2.2, .7)
            K.paste(fr, ring, x, y - (scroll(min(t, t1)) - scroll(t0)), alpha=(1 - rk) ** 2)
    return fr


_FR = {}


def fracture():
    if 'F' not in _FR:
        GK = gk()
        _FR['F'] = GK.Fracture(center=IMPACT, seed=11, radials=16, ring_p=(1.05, .12, .05, .95),
                               hits=[(O['ASSISTIR'], 34, 120, .5, .03), (O['SSIS'], 150, 420, .85, .05)],
                               race=(O['SSIS'] + .05, 15000), web=(O['TIR'] - .07, .07))
        def _group(i, j, k):
            if j <= 1: return ('a', j, k // 4)
            if j <= 6: return ('b', j, k // 2)
            return ('c', i)
        _FR['S'] = GK.Shatter(_FR['F'], seed=3, focal=1600., vp=IMPACT, group=_group, wave=22000., speed=1.5)
        for s in _FR['S'].shards: s['vz'] *= 1.7                      # blown toward the lens
        _FR['D'] = GK.Dust(_FR['F'], n=260, seed=5, focal=1600., vp=IMPACT)
    return _FR['F'], _FR['S'], _FR['D']


def tau(t):
    u = max(0.0, t - BREAK); return .07 * (1 - math.exp(-u / .03)) + .55 * u


def cam_c(t):
    """camera dolly forward through the hole after the break (FOC units), expo-out."""
    u = t - BREAK
    if u <= 0: return 0.0
    return .55 * (1 - math.exp(-u / .14))


def leak(t):
    if t < O['SSIS']: return .12 * smooth((t - O['ASSISTIR']) / .05) if t >= O['ASSISTIR'] else 0.0
    return .12 + .75 * smooth((t - O['SSIS']) / (BREAK - O['SSIS'])) ** 1.4


def glass_screen(ctx, t):
    """what is printed on the glass at the break (feed + his Reel, cracked)."""
    F, S, D = fracture()
    scr = feed_frame(ctx, t)
    return F.composite(scr.convert('RGB'), t, refr=1.0 + 2.0 * smooth((t - O['SSIS']) / .15), leak=leak(t), glint=1.6,
                       sweep=200 + (t - O['ASSISTIR']) * 2400, leak_falloff=(.12, 430.0))


def real_world(ctx, t):
    """the real studio behind the glass: exactly where the Reel showed him at the break, then a dolly forward through
    the hole (z around the impact) with studio parallax."""
    c = cam_c(t); zd = 4.5 / (4.5 - c)
    sx = sy = 0.0
    u = t - BREAK
    if 0 <= u < .2:
        k = int(u * E.FPS); tab = [(0, 0), (0, 14), (-9, -8), (5, 4), (-2, -2), (1, 1)]
        if k < len(tab): sx, sy = tab[k]
    ctx.bg_z = (7.0 / (7.0 - c)) / zd
    FK = fk(); dmy = FK.media_rect(FK.SPECIAL, FK.center_scroll(FK.SPECIAL))[1] - 300
    mc = media_cam(t); cx, cy = mc['x'], mc['y']
    X = IMPACT[0] + (cx - IMPACT[0]) * zd; Y = IMPACT[1] + (cy + dmy - IMPACT[1]) * zd
    return ctx.compose(cam=dict(z=mc['z'] * zd, x=cx, y=cy, dx=X - cx + sx, dy=Y - cy + sy, rot=0.))


GLASS_KW = dict(dof=1.3, near=120.0, cull_scale=4.2, glyph_alpha=.0, refract=24.0, edge=2.0, veil=.05, sheen=.6,
                reflect=1.0, refl_cap=.5, env_q=2, env_pow=3.0, bevel=2.4, shade=.25, absorb=.10, tint=(12, 10, 30), rim=1.0,
                blur_cap=4.0, blur_fade=30.0, max_smear=7, smear_div=4.0, star_scale=3.5, smear_soft=True,
                q_blur=5.0, tex_r_area=90000)


FACE_S = (545.0, 850.0)                        # his face on the glass at the break


def shard_ink(s, u):
    """how much of the screen image a flying shard still carries: pieces over his face clear at once (the real him
    reads through the burst), the rest keep the printed feed for ~4 frames, then clear glass."""
    d = math.hypot(s['c'][0] - FACE_S[0], (s['c'][1] - FACE_S[1]) * .8)
    tg = u + s['delay'] if u > 0 else 0.0
    return 1 - smooth(tg / .03) if d < 280 else 1 - smooth((tg - .06) / .14)


def draw_feed(ctx, t):
    P = ctx.post; ctx.captions = False
    if t < O['ASSISTIR']:
        scr = feed_frame(ctx, t)
        sx, sy = slam_shake(t)
        if sx or sy: scr = E.zoom(scr.convert('RGB'), 1.02, (540, 960), dx=sx, dy=sy).convert('RGBA')
        scr = touch_layer(scr, t)
        ctx.full = scr
        P['vignette'] = .12; P['grain'] = .7
        if 0 <= t - SLAM < .1: P['bright'] = 1 + .10 * math.exp(-(t - SLAM) / .03)
    elif t < BREAK:
        g = glass_screen(ctx, t)
        lk = leak(t)
        # tremor building to the break
        if t > O['SSIS']:
            i = int(round(t * E.FPS)); r = np.random.default_rng(i * 7 + 3); k = 4.0 * smooth((t - O['SSIS']) / (BREAK - O['SSIS']))
            g = E.zoom(g, 1.0 + .004 * k, IMPACT, dx=float(r.normal(0, 1)) * k, dy=float(r.normal(0, 1)) * k)
        for tk in (O['ASSISTIR'], O['SSIS']):                      # each crack = a jolt
            u = t - tk
            if 0 <= u < .12:
                j = int(u * E.FPS); tab = [(0, 0), (0, 9), (-5, -5), (2, 2)]
                if j < len(tab): g = E.zoom(g, 1.0, IMPACT, dx=tab[j][0], dy=tab[j][1])
        ctx.full = g.convert('RGBA')
        P['vignette'] = .14 + .2 * lk; P['grain'] = .7 + .3 * lk
        if t > BREAK - .05: P['bright'] = 1 + .25 * smooth((t - BREAK + .05) / .05)
    else:
        F, S, D = fracture()
        u = t - BREAK
        c = cam_c(t)
        g = None
        if S.visible(tau(t), c * 1600., 120.0, 4.2):
            # what the shards carry: the cracked feed while the display layer still lives, then clear glass
            if any(shard_ink(s, max(0.0, tau(t) - s['delay'])) > .004 for s in S.shards): g = glass_screen(ctx, t)
            else: g = K.C('blackglass', lambda: Image.new('RGB', (W, H), (0, 0, 0)))
        rw = real_world(ctx, t).convert('RGBA')
        if g is not None:
            dtau = tau(t) - tau(t - .2 / E.FPS)
            fr = S.render_refract(rw, g, tau(t), dz=c * 1600., focus_z=1600. / (1 / (1 - .8 * c)), shutter_dtau=dtau,
                                  dz_prev=cam_c(t - .3 / E.FPS) * 1600., img_alpha=shard_ink, backlight=1.0 * math.exp(-u / .08),
                                  **GLASS_KW)
        else: fr = rw
        da = smooth(u / .03) * (1 - smooth((u - .22) / .15))
        if da > .01:
            fr.alpha_composite(D.render((W, H), tau(t), c * 1600., tau(t) - tau(t - .5 / E.FPS), cam_c(t - .5 / E.FPS) * 1600.,
                                        alpha=da, taper=True, sparkle=.3, gain=1.3))
        ctx.full = fr
        P['flash'] = .18 * math.exp(-u / .03); P['flash_col'] = (236, 228, 255); P['bright'] = 1 + .2 * math.exp(-u / .04)
        P['vignette'] = .32
    K.caps_layer(ctx, t, PAGES_C, y=1450)


# ================================================================ draw
def draw(ctx, lt, t):
    if t < T17: draw_clones(ctx, t); ctx.captions = False
    elif t < T18: draw_house(ctx, t)
    else: draw_feed(ctx, t)
