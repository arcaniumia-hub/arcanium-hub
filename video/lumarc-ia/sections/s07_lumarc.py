"""s07 — LUMARC TAKES THE STAGE (43.40–57.08).  "Aqui na LUMARC, a gente é AI-first: a IA faz grande parte do trabalho
pesado… e o nosso time coloca o que ela não tem: estratégia, criatividade, bom gosto… e, principalmente, a IA certa,
usada do jeito certo."

SEG 19  THE STAGE (43.40 JUMP: CLUNK, the studio lights go out).  He sits lower in a dark stage under a spot, the dead
        LUMARC glass sign above him.  "LU-" (43.92) the sign strikes like neon (flicker), "-MARC" (44.00) CLUNK: the studio
        lights slam on with it (flash, bloom).  "a gente é" the logo lifts to the top and on "AI" (44.95, after his pause)
        a huge gradient "AI-" rises from BEHIND him (BOOM, shake, the wall glows), "FIRST" (45.32) rises under it,
        tucked behind his head; the brand line "AI-first. Not AI-only." pops in at the bottom on the vowel of "FIRST"
        (45.42).  Dust drifts in the top light while the stage is dark.
SEG 20  THE AGENT (45.90 JUMP — the pose surfaces one frame early: tight cut, he sits left, a frosted-glass "Agente IA"
        dashboard swoops up over his chest).  The agent RACES through the heavy lifting: Cortes, Legendas, Cor,
        Trilha, Versões, Formatos — each bar zips and ticks ✓ on a syllable (FAZ, GRAN, -DE, PAR, DO, TRA).  The fall
        starts at 47.66 so the cast-iron weight engraved PESADO enters the frame on "PE-" (47.72; short smear, readable
        for 4 frames) and on "-SA-" (47.87) the agent CATCHES it in a tractor
        beam (THUD: the panel and camera jolt, shock ring, sparks) — the AI literally does the heavy lifting.
SEG 21  THE TEAM (48.20 JUMP: whip — the dashboard and the floating weight fly out left, the camera settles on a wider
        shot).  "e o / NOS- / -so" three team avatars pop in, "TIME" (48.71) the glass LUMARC badge forms around them;
        "coLOca / QUE / NÃO" three empty glass slots click in;
        "TEM" they shimmer (anticipation, riser).
SEG 22-24  THE HUMAN PART (50.20 JUMP: snap closer + rack focus to the cards, he goes soft).  Each word fills its card ON the
        word — ESTRATÉGIA (50.27) chess knight, CRIATIVIDADE (51.29) spark, BOM GOSTO (52.43) faceted gem: gradient
        flood from the bottom, icon pop + ring, label, light sweep on the stressed syllable, the camera leans to the card.
SEG 25  THE RIGHT AI.  "e," the cards fold into three mini tiles; "PRINCIPALMENTE" (53.72) a slot machine of generic AI
        tool chips (Imagem, Vídeo, Voz, 3D, Texto, Motion, Upscale, Avatar, Música) springs up and spins (a tick per
        chip), a target reticle hunts from "IA" and LOCKS the reel on "CER-" (54.94).
SEG 26  USED RIGHT.  "usada" the reel dissolves around the chosen chip, the team tiles spread and a cursor clicks the
        chip (55.77); "do / jei- / -to" the three tiles plug light lines into it one per syllable (strategy, creativity
        and taste drive the AI); "CER-to" (56.61) a dark-glass seal with a giant gradient ✓ STAMPS over it (ding +
        stamp, ring, the rest steps back).  The last frame (57.067, s08's pose surfaces early) is a crash-zoom exit.
Captions: own word pops in the engine look on measured onsets (bottom in 19, top in 20/21/25/26; in 22-24 the card
labels are the words: one 40 px size for all three, the active card lifted 1.08x and drawn on top).
Motion blur is continuous (cumulative-sum box smear in _E_kit); the 50.20 snap-in and the 57.067 exit use a smooth
multi-sample crash-zoom blur (K.zoom_smear) instead of the engine's 4-copy zoom_blur, which ghosts sharp UI/type.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _E_kit as K

START, END = E.span(19, 26)                       # 43.40 – 57.08
W, H = E.W, E.H
clamp, eout, ein, back, lerp, smooth, expo, decay = K.clamp, K.eout, K.ein, K.back, K.lerp, K.smooth, K.expo, K.decay


def pose_t(T):
    """first timeline frame showing the take's pose after the jump at T (30 fps -> nearest 25 fps source frame)."""
    for j in range(int(T * 30) - 3, int(T * 30) + 4):
        if E.Avatar._k_of(j / 30) / 25 >= T - 1e-6: return j / 30 - 1e-6
    return T


T19 = START
T20 = pose_t(E.TL[20]['t0'])                      # 45.8999 (one frame before the segment)
T21 = pose_t(E.TL[21]['t0'])                      # 48.1999
T22 = pose_t(E.TL[22]['t0'])                      # 50.1999
T_EXIT = pose_t(END)                              # 57.0666: s08's pose already shows on our last frame

# word / syllable onsets measured on src/tight16k.raw (5 ms STFT spectrogram + 10 ms RMS, out/E/sp_*.png):
# vowel onsets after pauses, plosive bursts after their closure, fricative starts.
O = dict(AQUI=43.47, NA=43.79, LUMARC=43.92, MARC=44.00, RC=44.21,
         A=44.45, GENTE=44.54, E=44.77, AI=44.95, FIRST=45.32, FIRST_V=45.47, END19=45.78,
         A2=45.98, IA=46.05, FAZ=46.31, GRANDE=46.59, DE=46.85, PARTE=47.02, DO=47.21, TRABALHO=47.38, BA=47.48,
         PESADO=47.72, SA=47.87, END20=48.07,
         E3=48.29, O3=48.36, NOSSO=48.44, TIME=48.71, COLOCA=49.00, LO=49.08, O4=49.27, QUE=49.37, ELA=49.45,
         NAO=49.63, TEM=49.92, END21=50.07,
         ESTRATEGIA=50.27, TE=50.62, CRIATIVIDADE=51.29, DA=51.79, BOM=52.43, GOSTO=52.75, END24=53.10,
         E5=53.55, PRINCIPALMENTE=53.72, MEN=54.15, A5=54.41, IA5=54.47, CERTA=54.74, CER=54.94, TA=55.17,
         USADA=55.62, SA6=55.77, DO6=55.97, JEITO=56.10, CERTO=56.47, CER6=56.61, TO=56.82, END26=56.87)

# ---------------------------------------------------------------- seg 19 timing
LIGHTS_ON = 44.0                                  # "-MARC": the studio lights slam on (frame 1320)
LOGO_UP0, LOGO_UP1 = 44.66, 44.95                 # the logo lifts to the top (makes room for the type)
AY19 = 250.0                                      # he sits lower: the type owns the top
TAG_T = O['FIRST_V'] - .05                        # the brand line pops on the vowel of "FIRST" (readable ~0.5 s before the cut)
# ---------------------------------------------------------------- seg 20
TICKS = [O['FAZ'], O['GRANDE'], O['DE'], O['PARTE'], O['DO'], O['TRABALHO']]
TASKS = [('cut', 'Cortes'), ('cc', 'Legendas'), ('color', 'Cor'), ('music', 'Trilha'), ('versions', 'Versões'), ('formats', 'Formatos')]
CATCH = O['SA'] - .005                            # caught by the agent's beam on the stressed "-SA-"
DROP0 = O['PESADO'] - .06                         # the fall starts 2 frames early so the weight's body enters on "PE-"
# ---------------------------------------------------------------- seg 21-24
SLOT_IN = [O['COLOCA'], O['QUE'], O['NAO']]
BADGE_Y = 1116                                    # under his chin (clear of the beard), above the slots
AV_T = [O['E3'], O['NOSSO'], O['NOSSO'] + .14]      # "e o / NOS- / -so": the team gathers, one avatar per beat
FILL = [O['ESTRATEGIA'], O['CRIATIVIDADE'], O['BOM']]
STRESS = [O['TE'], O['DA'], O['GOSTO']]
CARDS = [('knight', 'ESTRATÉGIA'), ('spark', 'CRIATIVIDADE'), ('gem', 'BOM GOSTO')]
CX = [204, 540, 876]; CY = 1384; CW, CH = 316, 420
LABEL_PX = 40                                     # one size for the three card labels (they are the captions here)
FOLD0, FOLD1 = 53.47, 53.74                       # "e," the cards fold into mini tiles
MINI_X = [410, 540, 670]; MINI_Y = 1110; MINI_S = .32
SPREAD_X = [318, 540, 762]                        # "usada": the tiles spread to feed the chosen AI
# ---------------------------------------------------------------- seg 25-26
CHIPS = [('image', 'Imagem'), ('video', 'Vídeo'), ('voice', 'Voz'), ('cube', '3D'), ('text', 'Texto'), ('motion', 'Motion'),
         ('upscale', 'Upscale'), ('avatar', 'Avatar'), ('music', 'Música')]
REEL0 = O['PRINCIPALMENTE'] + .02                 # spin starts as the slot machine springs up
LOCK = O['CER']                                   # the reel LOCKS on "CER-"
P_END, P_DIST, P_OVER = 19.0, 18.0, .14           # lands on chip 19 % 9 = 1 ('Vídeo')
RX, RY = 540, 1428; RWIN = (900, 420); PITCH = 142
LIFT0 = O['USADA'] - .02
CLICK = O['SA6']
STAMP = O['CER6']
LINE_T = [O['DO6'], O['JEITO'], O['JEITO'] + .15]     # "do / jei- / -to": one team line plugs in per syllable


def reel_p(t):
    """reel position (chips): eases to just past the lock target with zero speed, then the lock latches it back."""
    if t < REEL0: return P_END - P_DIST
    if t < LOCK:
        u = (t - REEL0) / (LOCK - REEL0)
        return P_END + P_OVER - (P_DIST + P_OVER) * (1 - u) ** 2.2
    return P_END + P_OVER * math.exp(-(t - LOCK) / .03)


def _reel_ticks():
    """one 'tick' per chip crossing the payline, once the crossings are far enough apart to hear separately (the
    fast part is the 'ff' zip)."""
    ts = []
    for k in range(int(P_END - P_DIST) + 1, int(P_END) + 1):
        q = (P_END + P_OVER - (k - .5)) / (P_DIST + P_OVER)            # solve p(t) = k - .5 on the ease
        if 0 < q < 1: ts.append(REEL0 + (1 - q ** (1 / 2.2)) * (LOCK - REEL0))
    return [t for i, t in enumerate(ts) if i and t - ts[i - 1] >= .05 and t < LOCK - .04]
REEL_TICKS = _reel_ticks()

CUES = [
    (T19, 'switch', {'gain': -2}),                                 # CLUNK: the studio lights go out (covers the jump)
    (O['LUMARC'] - .01, 'shimmer', {'gain': -7}),                  # the neon sign strikes
    (LIGHTS_ON, 'switch', {'gain': 0}),                            # CLUNK: lights on with "-MARC"
    (LIGHTS_ON + .01, 'impact', {'gain': -12}),
    (LOGO_UP0, 'swoosh_up', {'gain': -14}),                       # logo lifts
    (O['AI'], 'boom', {}),                                         # "AI-" rises behind him
    (O['AI'], 'impact', {'gain': -7}),
    (O['FIRST'] + .06, 'impact', {'gain': -5}),                    # "FIRST"
    (TAG_T, 'pop', {'gain': -12}),                                 # brand line
    (T20, 'swoosh_up', {'gain': -6}),                              # cut: the dashboard swoops up
    (O['IA'], 'notify', {'gain': -14}),                            # the agent wakes
] + [(tk, 'tick', {'gain': -4, 'pan': -.3 + .12 * i}) for i, tk in enumerate(TICKS)] + [
    (DROP0, 'whoosh', {'gain': -9}),                               # the weight drops
    (CATCH, 'thud', {}),                                           # caught by the beam
    (CATCH + .01, 'sub', {'gain': -10}),
    (T21, 'swipe', {'gain': -4, 'pan': -.4}),                      # whip: the dashboard flies out left
] + [(t_, 'pop', {'gain': -15, 'pan': (-.25, 0, .25)[i]}) for i, t_ in enumerate(AV_T)] + [   # the team gathers
    (O['TIME'], 'pop', {'gain': -8}),                              # LUMARC team badge
] + [(t_, 'click', {'gain': -5, 'pan': (-.45, 0, .45)[i]}) for i, t_ in enumerate(SLOT_IN)] + [
    (O['TEM'] - .02, 'riser', {'to': O['ESTRATEGIA'], 'gain': -8}),
] + [(t_, 'pop', {'gain': -2, 'pan': (-.35, 0, .35)[i]}) for i, t_ in enumerate(FILL)] + [
    (O['TE'], 'shing', {'gain': -14, 'pan': -.35}),
    (O['DA'], 'shing', {'gain': -14}),
    (O['GOSTO'], 'shimmer', {'gain': -9, 'pan': .35}),
    (FOLD0, 'whoosh', {'gain': -13}),                              # cards fold into tiles
    (REEL0 - .02, 'swoosh_up', {'gain': -8}),                      # slot machine springs up
] + [(tk, 'tick', {'gain': -11}) for tk in REEL_TICKS] + [
    (REEL0, 'ff', {'dur': .5, 'gain': -14}),                       # the reel's fast first spin
    (LOCK, 'lock', {}),                                            # LOCK on "CER-"
    (LIFT0, 'swoosh_up', {'gain': -14}),                           # the chip lifts out
    (CLICK, 'click', {'gain': -3}),                                # the cursor clicks it
] + [(t_, 'tick', {'gain': -12, 'pan': (-.4, 0, .4)[i]}) for i, t_ in enumerate(LINE_T)] + [   # team lines plug in
    (STAMP, 'ding', {'note': 'E6'}),                               # ✓ STAMP on "CER-to"
    (STAMP, 'stamp', {'gain': -6}),
]


# ================================================================ helpers
def shake(t, t0, amp, tau=.16, f=19.0, seed=0):
    u = t - t0
    if u < 0 or u > tau * 5: return 0.0, 0.0
    k = amp * math.exp(-u / tau)
    return k * math.sin(u * f * 2 * math.pi + seed), k * math.cos(u * f * 1.7 * 2 * math.pi + seed * 2)


def spot_mask():
    """dark-stage spotlight: 1 on his face/chest, falling to .2 at the frame edges (H x W x 1 float32)."""
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - 540) / 560) ** 2 + ((yy - 1080) / 760) ** 2)
        return (.2 + .8 * (1 - np.clip((r - .35) / .75, 0, 1)) ** 1.6)[..., None]
    return K.C('spot', mk)


def cone():
    """soft top-light cone falling on him in the dark (behind layer, world)."""
    def mk():
        w, h = 1080, 1150
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        v = yy / h; half = 90 + 330 * v
        e = np.clip(1 - np.abs(xx - w / 2) / half, 0, 1) ** 1.8
        a = e * (.10 + .22 * v) * np.clip(v * 6, 0, 1)
        col = np.dstack([np.full_like(a, 200), np.full_like(a, 190), np.full_like(a, 255)])
        im = Image.fromarray(np.dstack([col, a * 255]).astype(np.uint8), 'RGBA')
        return im.filter(ImageFilter.GaussianBlur(6))
    return K.C('cone', mk)


def w2s(cam, x, y):
    """world point -> (screen x, screen y, scale) through the engine's camera (same clamp as compose_world)."""
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return X + (x - cam['x']) * z, Y + (y - cam['y']) * z, z


def dark_stage(fr, k):
    if k < .01: return fr
    a = np.asarray(fr.convert('RGB'), np.float32)
    m = 1 - (1 - spot_mask()) * k
    return Image.fromarray(np.clip(a * m, 0, 255).astype(np.uint8)).convert('RGBA')


# ================================================================ seg 19: THE STAGE
def logo_lit():
    def mk():
        lg = E.logo(560); pad = 90; a = lg.getchannel('A')
        out = K.glow_of(a, (110, 80, 255), 34, 1.5, pad)
        out.alpha_composite(K.glow_of(a, (170, 150, 255), 10, 1.15, pad))
        out.alpha_composite(lg, (pad, pad))
        return out
    return K.C('logo_lit', mk)


def logo_dead():
    def mk():
        lg = E.logo(560); pad = 90
        g = Image.merge('RGBA', [lg.convert('L').point(lambda v: int(v * .5 + 30))] * 3 + [lg.getchannel('A').point(lambda v: int(v * .32))])
        out = Image.new('RGBA', (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0)); out.alpha_composite(g, (pad, pad))
        return out
    return K.C('logo_dead', mk)


def neon_level(t):
    """the sign strikes like a neon tube on 'LU-' and is solid from '-MARC' on (frame-exact)."""
    j = int(round(t * E.FPS))
    seq = {1317: .18, 1318: .85, 1319: .25}
    if j < 1317: return 0.0
    return seq.get(j, 1.0)


def tagline():
    def mk():
        f = E.font(58, 600); a, b = 'AI-first.', '  Not AI-only.'
        wa = f.getbbox(a)[2]; wb = f.getbbox(b)[2]; w = wa + wb + 100; h = 122
        p, pad = K.panel(w, h, h // 2, fill=(16, 14, 32), a=.72, border=.6)
        im = p.copy(); d = ImageDraw.Draw(im)
        d.text((pad + 48, pad + h / 2), a, font=f, fill=K.WHITE, anchor='lm')
        m = Image.new('L', im.size); ImageDraw.Draw(m).text((pad + 48 + wa, pad + h / 2), b, font=f, fill=255, anchor='lm')
        im.alpha_composite(K.colorize(m, K.grad_img(im.width, im.height, K.GRAD_L)))
        return im
    return K.C('tagline', mk)


def draw_stage(ctx, t):
    P = ctx.post
    on = 1.0 if t >= LIGHTS_ON - .001 else 0.0                    # the lights SLAM on (one frame)
    zc = 1.085 + .045 * smooth((t - T19) / (T20 - T19)) + .03 * decay(t, O['AI'], .18) * (1 - decay(t, O['AI'], .02))
    ctx.cam = dict(z=zc, x=540., y=960., dx=0., dy=0., rot=0.)
    sx, sy = shake(t, O['AI'], 13, .17); sx2, sy2 = shake(t, O['FIRST'] + .06, 8, .12, seed=1.3)
    ctx.cam['dx'] += sx + sx2; ctx.cam['dy'] += sy + sy2
    ctx.avatar['y'] = AY19
    ctx.avatar['bright'] = lerp(.80, 1.0, on) + .14 * decay(t, O['AI'], .2)
    ai_k = clamp((t - O['AI'] + .02) / .06)
    ctx.bg_dim = lerp(.82, .06, on) + .26 * smooth((t - O['AI']) / .3)
    if on < .99:
        ctx.add('behind', cone(), 540, 575 + AY19 * .3, alpha=1 - on)
        lt = t - T19                               # dust drifting in the top light (the dark stage is never static)
        for i in range(28):
            v = (K.hrand(i, 1) + lt * .05 * (.5 + K.hrand(i, 5))) % 1.0
            y = 75 + 1150 * v; half = 90 + 330 * v
            x = 540 + half * .8 * (2 * K.hrand(i, 2) - 1) + 14 * math.sin(lt * 1.3 + 6 * K.hrand(i, 3))
            a = (.25 + .5 * K.hrand(i, 4)) * (.6 + .4 * math.sin(lt * 5 + i)) * min(1.0, v * 4, (1 - v) * 8) * (1 - on)
            ctx.add('behind', K.blob(3 + int(4 * K.hrand(i, 6)), 3 + int(4 * K.hrand(i, 6)), (225, 218, 255), 1.5, 1.0), x, y, alpha=a)
    # ---- the LUMARC sign (world, above his head)
    up = expo((t - LOGO_UP0) / (LOGO_UP1 - LOGO_UP0)) if t >= LOGO_UP0 else 0.0
    ly = lerp(468, 340, up); ls = lerp(1.0, .50, up)
    nl = neon_level(t)
    # light the sign throws on the wall
    wall = K.blob(820, 420, (90, 60, 230), 110, .55)
    ctx.add('behind', wall, 540, ly + 10, alpha=nl * lerp(.9, .35, up) + .25 * decay(t, LIGHTS_ON, .25))
    # in the dark the sign is its own light source: drawn in screen space (the dark-stage grade must not dim it)
    lay, lx_, ly_, lz = ('behind', 540, ly, 1.0) if on > .5 else ('screen',) + w2s(ctx.cam, 540, ly)
    if nl < .999: ctx.add(lay, K.scale_im(logo_dead(), ls * lz), lx_, ly_, alpha=1 - nl * .7)
    if nl > .01:
        lit = logo_lit()
        sw = (t - 44.12) / .42
        if 0 < sw < 1: lit = K.sheen(lit, sw, .12, .65)
        ctx.add(lay, K.scale_im(lit, ls * lz), lx_, ly_, alpha=nl)
    # ---- giant type behind him: "AI-" (on "AI") and "FIRST" (on "FIRST")
    if t >= O['AI'] - .02:
        k = expo((t - O['AI'] + .02) / .30)
        glow = K.blob(980, 560, (100, 70, 255), 130, .7)
        ctx.add('behind', glow, 540, 620, alpha=.55 * k + .35 * decay(t, O['AI'], .25))
        img, pad = K.giant('AI-', 380)
        img = K.scale_im(img, .93 + .07 * k)
        ctx.add('behind', img, 540 + 8, 552 + 150 * (1 - k), alpha=ai_k)
    if t >= O['FIRST'] - .02:
        k = expo((t - O['FIRST'] + .02) / .26)
        img, pad = K.giant('FIRST', 268)
        img = K.scale_im(img, .95 + .05 * k)
        ctx.add('behind', img, 540, 826 + 120 * (1 - k), alpha=clamp((t - O['FIRST'] + .02) / .05))
    # ---- post: dark stage, flashes
    ds = 1 - on
    ctx.wrap = (lambda fr, ds=ds: dark_stage(fr, ds)) if ds > .01 else None
    fl = .10 * decay(t, LIGHTS_ON, .05) if t >= LIGHTS_ON - .001 else 0.0
    fa = .14 * decay(t, O['AI'], .06) if t >= O['AI'] else 0.0
    P['flash'] = fl + fa; P['flash_col'] = (232, 224, 255)
    P['bright'] = 1 + .30 * (decay(t, LIGHTS_ON - .001, .07) if t >= LIGHTS_ON - .001 else 0) + .12 * (decay(t, O['FIRST'] + .06, .08) if t >= O['FIRST'] + .06 else 0)
    P['rgb'] = 6 * clamp(1 - (t - O['AI']) / .12) if t >= O['AI'] else 0.0
    P['vignette'] = .32 + .2 * ds
    # ---- captions (bottom) + the brand line
    K.caps_layer(ctx, t, [(O['AQUI'] - .04, O['A'] - .02, [('AQUI', O['AQUI'], False), ('NA', O['NA'], False)]),
                          (O['A'] - .04, O['AI'] - .03, [('A', O['A'], False), ('GENTE', O['GENTE'], False), ('É', O['E'], False)])],
                 y=1500)
    if t >= TAG_T:
        k = back((t - TAG_T) / .22, 1.6)
        ctx.add('screen', K.scale_im(tagline(), .7 + .3 * k), 540, 1500, glass=12, alpha=clamp((t - TAG_T) / .06))


# ================================================================ seg 20: THE AGENT
PW, PH = 860, 580
PX, PY = 540, 1356
ROW0, ROWP = 112, 76
BAR0, BAR1 = 318, 724
STAT_X = 786
ORB = (770, 52)


def dash_base():
    def mk():
        p, pad = K.panel(PW, PH, 44, fill=(14, 12, 30), a=.66, border=.6)
        im = p.copy(); d = ImageDraw.Draw(im); o = pad
        sp = K.icon('spark', 40, K.GRAD_L); im.alpha_composite(sp, (o + 34, o + 32))
        d.text((o + 86, o + 52), 'Agente IA', font=E.font(42, 700), fill=K.WHITE, anchor='lm')
        d.line((o + 30, o + 100, o + PW - 30, o + 100), fill=(255, 255, 255, 34), width=2)
        for i, (ic, lab) in enumerate(TASKS):
            cy = o + ROW0 + ROWP * i + ROWP // 2
            d.rounded_rectangle((o + 34, cy - 25, o + 84, cy + 25), 14, fill=(255, 255, 255, 18), outline=(255, 255, 255, 40), width=1)
            im.alpha_composite(K.icon(ic, 32, (225, 220, 250)), (o + 43, cy - 16))
            d.rounded_rectangle((o + BAR0, cy - 6, o + BAR1, cy + 6), 6, fill=(255, 255, 255, 26))
        return im, pad
    return K.C('dash_base', mk)


def _row_hl(ft):
    m = Image.new('L', (PW - 40, ROWP - 10)); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 41, ROWP - 11), 18, fill=int(40 * int(ft * 20) / 20))
    return K.colorize(m, (150, 130, 255))


def label_img(text, done):
    return K.C(('dlab', text, done), lambda: E.text_im(text, 38, 600, K.WHITE if done else (170, 168, 196)))


def check_badge(r=23):
    def mk():
        S = 4; n = 2 * r * S; m = Image.new('L', (n, n)); ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
        m = m.resize((2 * r, 2 * r), Image.LANCZOS)
        im = K.colorize(m, K.grad_img(2 * r, 2 * r, E.GRAD, .3))
        im.alpha_composite(K.icon('check', int(r * 1.5), (255, 255, 255), .1), (int(r * .25), int(r * .28)))
        pad = 16; out = K.glow_of(m, (120, 90, 255), 8, 1.2, pad); out.alpha_composite(im, (pad, pad)); return out
    return K.C(('chk', r), mk)


def spinner(ang, r=17):
    im = Image.new('RGBA', (2 * r + 8, 2 * r + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 4 + 2 * r, 4 + 2 * r), outline=(255, 255, 255, 40), width=4)
    d.arc((4, 4, 4 + 2 * r, 4 + 2 * r), ang, ang + 110, fill=(190, 176, 255, 255), width=4)
    return im


def bar_fill(w):
    def mk():
        g = K.grad_img(BAR1 - BAR0, 12, E.GRAD_LIGHT); m = Image.new('L', g.size)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, g.width - 1, 11), 6, fill=255); return K.colorize(m, g)
    full = K.C('barfull', mk)
    if w < 4: return None
    return full.crop((0, 0, int(w), 12))


def orb(t, hot=0.0):
    """the agent: a glowing gradient sphere with an orbiting ring."""
    def base():
        r = 24; S = 4; n = 2 * r * S
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n - .5
        d = np.sqrt(xx ** 2 + yy ** 2) / .5
        hi = np.exp(-(((xx + .16) ** 2 + (yy + .18) ** 2) / .03))
        col = np.dstack([lerp(95, 175, 1 - d) + 80 * hi, lerp(80, 150, 1 - d) + 80 * hi, np.full_like(d, 255)])
        al = np.clip((1 - d) * 40, 0, 1) * 255
        im = Image.fromarray(np.dstack([np.clip(col, 0, 255), al]).astype(np.uint8), 'RGBA').resize((2 * r, 2 * r), Image.LANCZOS)
        pad = 40; out = K.glow_of(im.getchannel('A'), (120, 90, 255), 14, 1.6, pad); out.alpha_composite(im, (pad, pad)); return out
    b = K.C('orb', base)
    s = 1 + .06 * math.sin(t * 9) + .35 * hot
    im = K.scale_im(b, s).copy(); d = ImageDraw.Draw(im); c = im.width / 2
    a0 = (t * 400) % 360; R = 34 * s
    d.arc((c - R, c - R * .42, c + R, c + R * .42), a0, a0 + 240, fill=(210, 200, 255, 220), width=3)
    return im


def draw_dashboard(ctx, t, ox=0.0, oy=0.0, alpha=1.0, smear=0.0):
    """the glass agent panel at (PX + ox, PY + oy) (screen space)."""
    base, pad = dash_base()
    im = base.copy(); o = pad
    hot_rows = sum(1 for tk in TICKS if t >= tk)
    act = min(hot_rows, len(TASKS) - 1)
    # active-row highlight glides between rows
    ft = clamp((t - O['A2']) / .2)
    hy = 0.0
    for i, tk in enumerate(TICKS):
        if t >= tk: hy = min(i + 1, len(TASKS) - 1) - (1 - expo((t - tk) / .1))
    if hot_rows < len(TASKS) and t >= O['A2']:
        cy = o + ROW0 + ROWP * hy + ROWP // 2
        hl = K.C(('rowhl', int(ft * 20)), lambda: _row_hl(ft))
        im.alpha_composite(hl, (o + 20, int(cy - hl.height / 2)))
    for i, (ic, lab) in enumerate(TASKS):
        cy = o + ROW0 + ROWP * i + ROWP // 2
        tk = TICKS[i]; d0 = .30 + .04 * i
        f = smooth((t - (tk - d0)) / d0) if t < tk else 1.0
        f = f ** 1.4 if t < tk else 1.0
        done = t >= tk
        li = label_img(lab, done)
        im.alpha_composite(li, (o + 100 - 10, int(cy - li.height / 2)))
        bf = bar_fill((BAR1 - BAR0) * f)
        if bf is not None:
            im.alpha_composite(bf, (o + BAR0, cy - 6))
            if f < 1:     # glowing head of the bar
                hx = o + BAR0 + (BAR1 - BAR0) * f
                gl = K.blob(26, 26, (200, 190, 255), 7, .9); im.alpha_composite(gl, (int(hx - gl.width / 2), int(cy - gl.height / 2)))
        if done:
            k = back((t - tk) / .18, 2.2)
            cb = K.scale_im(check_badge(), max(.05, .4 + .6 * k))
            im.alpha_composite(cb, (int(o + STAT_X - cb.width / 2), int(cy - cb.height / 2)))
            if t - tk < .25:
                rg = K.ring(18 + 40 * eout((t - tk) / .25), 2.5, (220, 210, 255), 1 - (t - tk) / .25)
                im.alpha_composite(rg, (int(o + STAT_X - rg.width / 2), int(cy - rg.height / 2)))
        elif t >= tk - d0 - .2:
            sp = spinner((t * 720 + i * 50) % 360); im.alpha_composite(sp, (int(o + STAT_X - sp.width / 2), int(cy - sp.height / 2)))
    # the agent orb (header right) — flares on "IA" and on every tick
    hot = .9 * decay(t, O['IA'], .12) if t >= O['IA'] else 0.0
    for tk in TICKS:
        if t >= tk: hot = max(hot, .35 * decay(t, tk, .08))
    if t >= DROP0: hot = max(hot, .6 * smooth((t - DROP0) / .12))
    if t >= CATCH: hot = max(hot, 1.2 * decay(t, CATCH, .1))
    ob = orb(t, hot); im.alpha_composite(ob, (int(o + ORB[0] - ob.width / 2), int(o + ORB[1] - ob.height / 2)))
    if smear: im = K.hsmear(im, smear, 12)
    ctx.add('screen', im, PX + ox, PY + oy, glass=16 if alpha > .5 and not smear else 0, alpha=alpha)


def beam_img(h, k):
    """tractor beam: a soft lilac cone from the orb up to the weight, scanlines rising."""
    w = 300; im = Image.new('RGBA', (w, max(2, int(h))), (0, 0, 0, 0))
    if h < 4: return im
    hh = im.height; yy, xx = np.mgrid[0:hh, 0:w].astype(np.float32)
    v = yy / max(1, hh - 1)                                      # 0 top (weight) .. 1 bottom (orb)
    half = lerp(118, 16, v)
    edge = np.clip(1 - np.abs(xx - w / 2) / half, 0, 1) ** 1.3
    lines = .75 + .25 * np.sin((yy + k * 900) / 7.0)
    a = edge * lines * .47
    core = np.exp(-((xx - w / 2) / (half * .25)) ** 2) * .5
    al = np.clip(a + core, 0, 1)
    col = np.dstack([np.full_like(al, 190), np.full_like(al, 176), np.full_like(al, 255)])
    return Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), 'RGBA')


def weight_state(t):
    """(x, y, sx, sy, smear) of the weight in screen space (centre), None before the drop."""
    if t < DROP0: return None
    X = PX - PW / 2 + ORB[0]; YC = 842.0; Y0 = -170.0
    if t < CATCH:
        u = (t - DROP0) / (CATCH - DROP0); y = Y0 + (YC - Y0) * u * u
        v = 2 * (YC - Y0) * u / (CATCH - DROP0) / E.FPS     # px per frame
        return X, y, .97, 1.04, min(44, v * .14)          # a short smear: the cartoon weight must stay readable
    u = t - CATCH
    dip = 26 * math.exp(-u / .07) * math.cos(u * 2 * math.pi * 5.5)
    sq = .12 * math.exp(-u / .05)
    bob = 7 * math.sin(u * 2 * math.pi * 1.4) * (1 - math.exp(-u / .1))
    return X, YC + dip + bob, 1 + sq * .6, 1 - sq, 0.0


def draw_agent(ctx, t, exit_k=0.0, exit_v=0.0):
    """seg 20 contents (also used for the whip exit at the start of seg 21: exit_k = 0..1 offset, exit_v = smear px)."""
    ox = -1150 * exit_k
    sx, sy = shake(t, CATCH, 11, .12, 23)
    jolt = 22 * math.exp(-(t - CATCH) / .08) * math.cos((t - CATCH) * 2 * math.pi * 4) if t >= CATCH else 0.0
    if t < T20 + .26:      # swoop up on the cut
        k = expo((t - T20) / .26); oy = 340 * (1 - k); al = clamp(.35 + k)
    else: oy, al = 0.0, 1.0
    draw_dashboard(ctx, t, ox + sx, oy + sy + jolt, al, smear=exit_v)
    ws = weight_state(t)
    if ws is None: return
    x, y, wsx, wsy, sm = ws
    wimg = K.weight_img(300)
    # beam (after the catch; charging just before)
    orb_y = PY - PH / 2 + ORB[1] + oy + sy + jolt
    if t >= CATCH - .06:
        bk = clamp((t - CATCH + .06) / .06)
        top = y + wimg.height * wsy / 2 - 12
        bm = beam_img(orb_y - top, t)
        if exit_v: bm = K.hsmear(bm, exit_v)                      # the whip drags the beam with the panel
        ctx.add('screen', bm, x + ox + sx, (orb_y + top) / 2, alpha=bk * (.8 + .2 * math.sin(t * 40)) * (1 - exit_k) ** 1.5)
        if t >= CATCH:
            u = t - CATCH
            if u < .35:
                rg = K.ring(30 + 200 * eout(u / .35), 4, (230, 220, 255), (1 - u / .35) * .9)
                ctx.add('screen', K.scale_im(rg, 1, .35), x + ox + sx, top + 6)
            # sparks thrown sideways from the contact point
            if u < .3:
                for i in range(14):
                    a = math.pi * (1.05 + .9 * K.hrand(i, 3)); sp = 260 + 520 * K.hrand(i, 4)
                    px = x + ox + sx + math.cos(a) * sp * u; py = top + math.sin(a) * sp * u * .55 + 900 * u * u
                    ctx.add('screen', K.blob(10, 10, (225, 215, 255), 3, 1.0), px, py, alpha=(1 - u / .3))
    if t < CATCH:          # its shadow grows on the panel as it falls (cartoon cue)
        u = (t - DROP0) / (CATCH - DROP0)
        ctx.add('screen', K.scale_im(K.blob(240, 44, (0, 0, 0), 12, .85), .3 + .7 * u, 1), x + ox + sx, PY - PH / 2 + oy + 8, alpha=u * u)
    wi = K.scale_im(wimg, wsx, wsy)
    if sm > 1.5: wi = K.vsmear(wi, sm)
    if exit_v: wi = K.hsmear(wi, exit_v, 12)
    ctx.add('screen', wi, x + ox + sx, y + sy)


def draw_agent_seg(ctx, t):
    P = ctx.post
    z = 1.20 + .04 * smooth((t - T20) / (T21 - T20)) + .02 * decay(t, CATCH, .1) * (t >= CATCH)
    ctx.cam = dict(z=z, x=540., y=700., dx=0., dy=-40., rot=0.)
    sx, sy = shake(t, CATCH, 11, .12, 23); ctx.cam['dx'] += sx; ctx.cam['dy'] += sy
    ctx.avatar['x'] = -60.0
    ctx.bg_dim = .10
    draw_agent(ctx, t)
    K.caps_layer(ctx, t, [(O['A2'] - .04, O['GRANDE'] - .02, [('A', O['A2'], False), ('IA', O['IA'], True), ('FAZ', O['FAZ'], False)]),
                          (O['GRANDE'] - .04, O['DO'] - .02, [('GRANDE', O['GRANDE'], False), ('PARTE', O['PARTE'], False)]),
                          (O['DO'] - .04, T21 - .02, [('DO', O['DO'], False), ('TRABALHO', O['TRABALHO'], False)])], y=330)
    # light from the panel / beam on him
    def wrap(fr):
        k = .16 + .22 * (decay(t, CATCH, .2) if t >= CATCH else 0)
        fr = K.add_light(fr, K.blob(900, 340, (70, 50, 170), 90, 1.0), 540, 1210, k)
        if t >= CATCH:      # the beam's contact flash spills on the side of his head
            fr = K.add_light(fr, K.blob(380, 420, (120, 100, 230), 80, 1.0), 860, 860, .38 * decay(t, CATCH, .12))
        return fr
    ctx.wrap = wrap
    P['bright'] = 1 + .14 * (decay(t, CATCH, .06) if t >= CATCH else 0)
    P['vignette'] = .34


# ================================================================ seg 21-24: THE TEAM + THE CARDS
def card_empty():
    def mk():
        p, pad = K.panel(CW, CH, 34, fill=(16, 14, 34), a=.40, border=0.0)
        im = p.copy(); dash = K.dashed_rrect(CW, CH, 34, (196, 182, 255), .75, 3)
        im.alpha_composite(dash, (pad, pad))
        c = K.icon('plus', 56, (196, 182, 255), .07)
        cm = Image.new('L', (96, 96)); ImageDraw.Draw(cm).ellipse((0, 0, 95, 95), outline=255, width=3)
        im.alpha_composite(K.colorize(cm.point(lambda v: int(v * .45)), (196, 182, 255)), (pad + CW // 2 - 48, pad + CH // 2 - 70))
        im.alpha_composite(c, (pad + CW // 2 - 28, pad + CH // 2 - 50))
        return im, pad
    return K.C('card_empty', mk)


def card_icon(i, s=170):
    name = CARDS[i][0]
    if name == 'gem': ic = K.gem_icon(s)
    else: ic = K.icon(name, s, K.GRAD_L)
    return K.icon_glow(ic, 18, (120, 90, 255), 1.4)


def label_font():
    """one size for all three labels: the largest <= LABEL_PX at which the longest (CRIATIVIDADE) fits the card."""
    def mk():
        s = LABEL_PX
        for _, text in CARDS:
            l, tp, r, b = E.font(LABEL_PX, 800).getbbox(text); s = min(s, int(LABEL_PX * (CW - 28) / (r - l)))
        return E.font(s, 800)
    return K.C(('card_label_font', CW, LABEL_PX), mk)


def card_full(i, label=True):
    def mk():
        p, pad = K.panel(CW, CH, 34, fill=(20, 16, 44), a=.82, border=.9, glow=.9)
        im = p.copy()
        # brand-gradient wash rising from the bottom
        g = np.asarray(K.grad_img(CW, CH, E.GRAD), np.float32)
        v = np.linspace(0, 1, CH, dtype=np.float32)[:, None]
        al = np.broadcast_to((np.clip(v - .15, 0, 1) / .85) ** 1.6 * .62 * 255, (CH, CW))
        m = Image.new('L', (CW, CH)); ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 1, CH - 1), 34, fill=255)
        wash = Image.fromarray(np.dstack([g, al]).astype(np.uint8), 'RGBA'); wash.putalpha(ImageChops.multiply(wash.getchannel('A'), m))
        im.alpha_composite(wash, (pad, pad))
        bm = Image.new('L', (CW, CH)); ImageDraw.Draw(bm).rounded_rectangle((1, 1, CW - 2, CH - 2), 34, outline=255, width=3)
        im.alpha_composite(K.colorize(bm, K.grad_img(CW, CH, K.GRAD_L)), (pad, pad))
        if label:
            text = CARDS[i][1]; f = label_font()
            ImageDraw.Draw(im).text((pad + CW / 2, pad + 336), text, font=f, fill=K.WHITE, anchor='mm')
            ImageDraw.Draw(im).rounded_rectangle((pad + CW / 2 - 28, pad + 372, pad + CW / 2 + 28, pad + 377), 3, fill=(255, 255, 255, 170))
        return im, pad
    return K.C(('card_full', i, label), mk)




def badge():
    """the LUMARC team badge pill (logo; the three team avatars are drawn on top, see avatar_bub)."""
    def mk():
        lg = E.logo(210); w, h = 430, 96
        p, pad = K.panel(w, h, h // 2, fill=(16, 14, 32), a=.72, border=.6)
        im = p.copy(); im.alpha_composite(lg, (pad + 26, pad + (h - lg.height) // 2))
        return im, pad
    return K.C('badge', mk)


def avatar_bub(k, r=30):
    def mk():
        m = Image.new('L', (8 * r, 8 * r)); ImageDraw.Draw(m).ellipse((0, 0, 8 * r - 1, 8 * r - 1), fill=255)
        m = m.resize((2 * r, 2 * r), Image.LANCZOS)
        out = Image.new('RGBA', (2 * r + 8, 2 * r + 8), (0, 0, 0, 0))
        out.alpha_composite(K.colorize(m, (14, 12, 30)), (1, 4))
        c = K.colorize(m, K.grad_img(2 * r, 2 * r, [E.GRAD[(k + j) % 3] for j in range(3)], .3))
        c.alpha_composite(K.icon('avatar', 40, (250, 249, 255)), (r - 20, r - 18))
        out.alpha_composite(c, (4, 4)); return out
    return K.C(('avbub', k, r), mk)


def draw_badge(ctx, t, alpha=1.0, dx=0.0):
    """the team gathers (three avatars pop on 'e o / NOS- / -so'), then on 'TIME' the LUMARC pill forms around them."""
    if t < AV_T[0] - .02 or alpha <= .01: return
    bk = back((t - O['TIME'] + .02) / .24, 1.8) if t >= O['TIME'] - .02 else 0.0
    gk = expo((t - O['TIME'] + .02) / .22) if t >= O['TIME'] - .02 else 0.0
    if t >= O['TIME'] - .02:
        im, pad = badge()
        ctx.add('screen', K.scale_im(im, .6 + .4 * bk), 540 + dx, BADGE_Y, glass=10, alpha=clamp((t - O['TIME'] + .02) / .06) * alpha)
    for k in range(3):
        if t < AV_T[k] - .02: continue
        pk = back((t - AV_T[k] + .02) / .2, 2.2)
        x0 = 540 + (k - 1) * 84; x1 = 540 - 255 + 40 + 290 + 46 * k
        x = lerp(x0, x1, gk)
        ctx.add('screen', K.scale_im(avatar_bub(k), max(.05, pk) * lerp(1.45, 1.0, gk)), x + dx, BADGE_Y,
                alpha=clamp((t - AV_T[k] + .02) / .05) * alpha)


def card_pose(i, t):
    """(x, y, scale, label_alpha) of card i at t."""
    x, y, s = CX[i], CY, 1.0
    if t >= FILL[i]:
        nxt = FILL[i + 1] if i + 1 < 3 else FOLD0
        k_in = back((t - FILL[i]) / .24, 2.0); k_out = smooth((t - nxt) / .2)
        act = (k_in - 1) * 1.0 + 1 if t < nxt else 1 - k_out
        s += .08 * act; y -= 18 * act
    c = expo((t - FOLD0) / (FOLD1 - FOLD0)) if t >= FOLD0 else 0.0
    if c > 0:
        st = clamp((t - FOLD0 - .03 * i) / (FOLD1 - FOLD0))
        c = expo(st)
        x = lerp(x, MINI_X[i], c); y = lerp(y, MINI_Y, c); s = lerp(s, MINI_S, c)
    return x, y, s, 1 - clamp(c * 3)


def active_card(t):
    """index of the card being filled / spoken (lifted, drawn on top), None outside 50.27 – fold."""
    for i in (2, 1, 0):
        if t >= FILL[i] - .03 and t < FOLD0: return i
    return None


def draw_cards(ctx, t, dx=0.0, dy=0.0, stamp_k=0.0):
    a_ = active_card(t)
    for i in [j for j in range(3) if j != a_] + ([a_] if a_ is not None else []):     # the active card on top
        if t < SLOT_IN[i] - .01: continue
        x, y, s, la = card_pose(i, t)
        x += dx; y += dy
        a_in = clamp((t - SLOT_IN[i] + .01) / .06)
        if t < FILL[i] - .03:
            k = back((t - SLOT_IN[i]) / .22, 1.8); im, pad = card_empty()
            sc = (.62 + .38 * k) * s
            pulse = 0.0
            if t >= O['TEM'] - .02: pulse = .06 * math.sin(clamp((t - O['TEM'] + .02) / .3) * math.pi) * (1 - .3 * i)
            img = K.scale_im(im, sc * (1 + pulse))
            sw = (t - O['TEM'] - .04 * i) / .34
            if 0 < sw < 1: img = K.sheen(img, sw, .18, .5)
            ctx.add('screen', img, x, y + 30 * (1 - k), glass=10, alpha=a_in)
            if t - SLOT_IN[i] < .3:
                u = (t - SLOT_IN[i]) / .3
                ctx.add('screen', K.ring(60 + 140 * eout(u), 3, (210, 200, 255), (1 - u) * .8), x, y)
            continue
        # filling: the full card is revealed from the bottom up (bright edge line), the empty one stays above it
        f = expo((t - (FILL[i] - .03)) / .18)
        full, pad = card_full(i, True) if la > .99 else card_full(i, False)
        if la < .99 and la > .01:
            fl, _ = card_full(i, True); full = Image.blend(full, fl, la) if full.size == fl.size else full
        if f < .999:
            emp, _ = card_empty(); mix = emp.copy()
            cut = int(pad + CH * (1 - f))
            mix.paste(full.crop((0, cut, full.width, full.height)), (0, cut))
            ed = Image.new('RGBA', (CW, 4), (235, 228, 255, 230))
            mix.alpha_composite(ed, (pad, max(0, cut - 2)))
            full = mix
        img = full
        sw = (t - STRESS[i] + .02) / .36
        if 0 < sw < 1: img = K.sheen(img, sw, .16, .7)
        if stamp_k > 0:     # the final ✓: tiles light up one after another
            fk = decay(t, STAMP + .05 * i, .12) if t >= STAMP + .05 * i else 0
            if fk > .01: img = K.sheen(img, clamp((t - STAMP - .05 * i) / .25), .3, .9 * fk)
        img = K.scale_im(img, s)
        ctx.add('screen', img, x, y)       # filling / filled cards are near-opaque: no frosting (the glass blur pad
                                           # reaches 40 px past the card and would soften a neighbour's label)
        # icon pop (drawn separately so it can overshoot)
        if True:
            k = back((t - FILL[i]) / .24, 2.4) if t >= FILL[i] else 0.0
            ic = card_icon(i)
            isc = s * (.35 + .65 * k) * lerp(1.3, 1.0, la)
            if t >= STRESS[i] and CARDS[i][0] == 'gem':
                isc *= 1 + .06 * decay(t, STRESS[i], .1)
            ic_y = y - (CH / 2 - 168) * s * la
            ctx.add('screen', K.scale_im(ic, isc), x, ic_y, alpha=clamp((t - FILL[i] + .02) / .05))
            if 0 <= t - FILL[i] < .32:
                u = (t - FILL[i]) / .32
                ctx.add('screen', K.ring(50 + 170 * eout(u), 4, (230, 222, 255), (1 - u) * .9), x, ic_y)
            if CARDS[i][0] == 'gem' and t >= STRESS[i] - .02:       # glints on "GOSTO"
                for g in range(3):
                    gt = t - STRESS[i] - .07 * g
                    if 0 <= gt < .3:
                        gx = x + (-40 + 45 * g) * s; gy = ic_y + (-38 + 22 * (g % 2)) * s
                        st = K.icon('spark', int(70 * (1 - abs(gt - .12) / .3)) + 6, (255, 255, 255))
                        ctx.add('screen', st, gx, gy, alpha=1 - gt / .3)


def draw_team_seg(ctx, t):
    """seg 21 (48.20 – 50.20): whip from the agent, team badge, empty slots."""
    P = ctx.post
    u = t - T21
    z = 1.03 + .06 * smooth((t - T21) / (T22 - T21))
    whip = 1 - expo(u / .24)
    ctx.cam = dict(z=z, x=540., y=820., dx=170 * whip, dy=-30., rot=0.)
    ctx.bg_dim = .10
    if u < .26:
        k = expo(u / .22); v = (expo((u + 1 / 30) / .22) - k) * 1150 * .6
        draw_agent(ctx, t, exit_k=k, exit_v=-v)
    if whip > .05:
        L = 150 * whip
        ctx.wrap = lambda fr, L=L: K.hsmear(fr, L, 14, keep=True)
    draw_badge(ctx, t)
    draw_cards(ctx, t)
    K.caps_layer(ctx, t, [(O['E3'] - .04, O['COLOCA'] - .02, [('E', O['E3'], False), ('O', O['O3'], False), ('NOSSO', O['NOSSO'], False), ('TIME', O['TIME'], True)]),
                          (O['COLOCA'] - .04, O['ELA'] - .02, [('COLOCA', O['COLOCA'], False), ('O', O['O4'], False), ('QUE', O['QUE'], False)]),
                          (O['ELA'] - .04, T22 - .02, [('ELA', O['ELA'], False), ('NÃO', O['NAO'], True), ('TEM:', O['TEM'], False)])], y=330)
    P['vignette'] = .34


def cards_cam(t):
    """seg 22-24 camera: snap closer on the cut, lean toward the card being filled, a micro punch per word."""
    z = 1.26 + .10 * (1 - expo((t - T22) / .3)); dx = 0.0          # snap in on the cut, settle
    for i, f in enumerate(FILL):
        if t >= f - .04:
            k = expo((t - f + .04) / .3); dx = lerp(dx, (CX[i] - 540) * -.10, k)
            z += .028 * decay(t, f, .12) * (1 - decay(t, f, .02)) if t >= f else 0
    z += .03 * smooth((t - T22) / (FOLD0 - T22))
    return dict(z=z, x=540., y=760., dx=dx, dy=0., rot=0.)


def dof_wrap(r, lights=(), under=(), zb=0.0, zc=(540, 800)):
    """rack focus on the world (his plane): `under` = screen layers that belong to his plane (pasted before the blur),
    zb = smooth crash-zoom blur amount (the snap-in on a jump frame)."""
    def wrap(fr):
        for L in under: E._paste(fr, L)
        out = K.soft_blur(fr, r) if r > .4 else fr
        if zb > .004: out = K.zoom_smear(out, zb, *zc)
        for (spr, x, y, k) in lights: out = K.add_light(out, spr, x, y, k)
        return out
    return wrap


def draw_cards_seg(ctx, t):
    """seg 22-24 (50.20 – 53.24)."""
    P = ctx.post
    ctx.cam = cards_cam(t)
    ctx.bg_dim = .14
    rk = expo((t - T22) / .2)
    lights = []
    for i, f in enumerate(FILL):
        if t >= f: lights.append((K.blob(520, 420, (110, 70, 255), 90, 1.0), CX[i], 1290, .26 * decay(t, f, .25) + .07))
    # the snap-in on the jump frame: a smooth crash-zoom blur of his plane (strong on the cut frame, a trace on the next)
    zb = .10 if t < T22 + .5 / E.FPS else (.04 if t < T22 + 1.5 / E.FPS else 0.0)
    under = []
    if t < T22 + .12:      # the badge sits in his plane: it snaps, goes soft with the rack focus and fades
        n0 = len(ctx.screen); draw_badge(ctx, t, alpha=clamp(1 - (t - T22) / .12)); under = ctx.screen[n0:]; del ctx.screen[n0:]
    ctx.wrap = dof_wrap(3.2 * rk, lights, under, zb)
    draw_cards(ctx, t)
    for f in FILL:
        if t >= f: P['bright'] = max(P['bright'], 1 + .10 * decay(t, f, .07))
    P['vignette'] = .36


# ================================================================ seg 25-26: THE RIGHT AI, USED RIGHT
CHW, CHH = 740, 116


def chip(i, sel=False):
    def mk():
        ic, lab = CHIPS[i]; w, h = CHW, CHH
        p, pad = K.panel(w, h, h // 2, fill=(36, 31, 72) if not sel else (40, 30, 92), a=.96, border=.6 if not sel else 0.0, glow=0 if not sel else 1.3)
        im = p.copy(); d = ImageDraw.Draw(im)
        tile = Image.new('L', (82, 82)); ImageDraw.Draw(tile).rounded_rectangle((0, 0, 81, 81), 24, fill=255)
        hue = [(60, 120, 255), (106, 85, 255), (154, 77, 255), (70, 150, 255), (190, 90, 255), (120, 100, 255)][i % 6]
        tb = K.colorize(tile, K.grad_img(82, 82, E.GRAD, .3)) if sel else K.colorize(tile.point(lambda v: int(v * .85)), hue)
        im.alpha_composite(tb, (pad + 17, pad + 17))
        im.alpha_composite(K.icon(ic, 52, (250, 249, 255)), (pad + 32, pad + 32))
        d.text((pad + 128, pad + h / 2), lab, font=E.font(56, 700), fill=K.WHITE, anchor='lm')
        if sel:
            bm = Image.new('L', (w, h)); ImageDraw.Draw(bm).rounded_rectangle((1, 1, w - 2, h - 2), h // 2, outline=255, width=4)
            im.alpha_composite(K.colorize(bm, K.grad_img(w, h, K.GRAD_L)), (pad, pad))
        return im, pad
    return K.C(('chip', i, sel), mk)


def reel_shade():
    """cylinder shading over the reel window (dark top/bottom, glass highlight band) + the window's rounded mask."""
    def mk():
        w, h = RWIN[0] - 36, RWIN[1] - 36
        v = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
        a = np.clip(np.abs(v) ** 2.4 * 1.1, 0, 1) * 225
        im = np.zeros((h, w, 4), np.float32); im[..., :3] = (10, 8, 22); im[..., 3] = np.broadcast_to(a, (h, w))
        out = Image.fromarray(im.astype(np.uint8), 'RGBA')
        hi = np.exp(-((np.linspace(0, 1, h)[:, None] - .17) / .05) ** 2) * 18
        out.alpha_composite(Image.fromarray(np.dstack([np.full((h, w, 3), 255, np.float32), np.broadcast_to(hi, (h, w))]).astype(np.uint8), 'RGBA'))
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=255)
        return out, m
    return K.C('reel_shade', mk)


def reel_canvas(t, others=1.0, hide_sel=False):
    """the spinning reel (inside the window), RGBA of the window's inner size."""
    w, h = RWIN[0] - 36, RWIN[1] - 36
    can = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    p = reel_p(t)
    v = (reel_p(t + .5 / E.FPS) - reel_p(t - .5 / E.FPS)) * PITCH      # px per frame
    base = math.floor(p)
    for j in range(base - 2, base + 3):
        d = j - p                                                         # chip offset from the centre (chips)
        if abs(d) > 1.9: continue
        ci = j % len(CHIPS)
        is_sel = abs(d) < .5 and t >= LOCK
        if is_sel and hide_sel: continue
        im, pad = chip(ci, sel=is_sel)
        y = h / 2 + PITCH * math.sin(d * .6) / .6 * (1 - .03 * d * d)
        sy = max(.2, math.cos(d * .6)); sx = 1 - .05 * abs(d)
        a = (1 - .38 * abs(d)) * (1 if abs(d) < .5 else others)
        if a <= .02: continue
        K.paste(can, K.scale_im(im, sx, sy), w / 2, y, alpha=a)
    if abs(v) > 2: can = K.vsmear(can, min(abs(v) * .7, 220), 8)
    if can.size != (w, h): can = can.crop(((can.width - w) // 2, (can.height - h) // 2, (can.width - w) // 2 + w, (can.height - h) // 2 + h))
    sh, m = reel_shade(); can.alpha_composite(sh)
    can.putalpha(ImageChops.multiply(can.getchannel('A'), m))
    return can


def reel_window():
    """the slot machine's glass window with its payline pointers (gradient triangles left/right of the centre row)."""
    def mk():
        im, pad = K.panel(RWIN[0], RWIN[1], 52, fill=(14, 12, 30), a=.88, border=.85, glow=1.0)
        im = im.copy(); cy = pad + RWIN[1] / 2
        m = Image.new('L', im.size); d = ImageDraw.Draw(m)
        for sgn, x in ((1, pad - 6), (-1, pad + RWIN[0] + 6)):
            d.polygon([(x, cy - 24), (x + sgn * 30, cy), (x, cy + 24)], fill=255)
        im.alpha_composite(K.colorize(m.filter(ImageFilter.GaussianBlur(8)), (120, 90, 255)))
        im.alpha_composite(K.colorize(m, K.grad_img(im.width, im.height, K.GRAD_L)))
        return im, pad
    return K.C('reel_win', mk)


def seal(d=430):
    """the approval seal: dark glass disc, gradient ring + glow, the big gradient check inside."""
    def mk():
        S = 3; n = d * S; pad = 70
        out = Image.new('RGBA', (d + 2 * pad, d + 2 * pad), (0, 0, 0, 0))
        m = Image.new('L', (n, n)); ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255); m = m.resize((d, d), Image.LANCZOS)
        mp = Image.new('L', out.size); mp.paste(m, (pad, pad))
        out.alpha_composite(K.colorize(mp.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * .7)), (2, 2, 8)), (0, 14))
        body = np.zeros((d, d, 4), np.float32); yy = np.linspace(0, 1, d, dtype=np.float32)[:, None]
        body[..., :3] = np.array([16, 13, 36], np.float32) + (np.clip(1 - yy / .5, 0, 1) ** 2 * 26)[..., None]
        body[..., 3] = 240
        bi = Image.fromarray(np.clip(body, 0, 255).astype(np.uint8), 'RGBA'); bi.putalpha(ImageChops.multiply(bi.getchannel('A'), m))
        out.alpha_composite(bi, (pad, pad))
        rm = Image.new('L', (n, n)); ImageDraw.Draw(rm).ellipse((6 * S, 6 * S, n - 6 * S, n - 6 * S), outline=255, width=10 * S)
        ImageDraw.Draw(rm).ellipse((30 * S, 30 * S, n - 30 * S, n - 30 * S), outline=110, width=2 * S)
        rm = rm.resize((d, d), Image.LANCZOS); rp = Image.new('L', out.size); rp.paste(rm, (pad, pad))
        out.alpha_composite(K.colorize(rp.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(min(255, v * 1.4))), (110, 80, 255)))
        out.alpha_composite(K.colorize(rp, K.grad_img(out.width, out.height, K.GRAD_L, .2)))
        ck = K.big_check(int(d * .66)); out.alpha_composite(ck, ((out.width - ck.width) // 2, (out.height - ck.height) // 2 + 6))
        return out
    return K.C(('seal', d), mk)


def feed_lines(t, tiles, chip_xy, glow_k=0.0):
    """light lines from the three team tiles into the chosen AI (draw-on + a travelling pulse). RGBA full frame-sized
    canvas region (x0, y0, img)."""
    x0, y0, x1, y1 = 180, 1040, 900, 1420
    can = Image.new('L', ((x1 - x0) // 2, (y1 - y0) // 2)); d = ImageDraw.Draw(can)
    pul = Image.new('L', can.size); dp = ImageDraw.Draw(pul)
    cx, cy = chip_xy
    for i, (tx, ty) in enumerate(tiles):
        if t < LINE_T[i]: continue
        k = expo((t - LINE_T[i]) / .16)
        ex, ey = cx + (tx - cx) * .35, cy - CHH / 2 + 4
        px, py = lerp(tx, ex, k), lerp(ty, ey, k)
        a = int(200 + 55 * glow_k)
        d.line(((tx - x0) / 2, (ty - y0) / 2, (px - x0) / 2, (py - y0) / 2), fill=a, width=2)
        u = (t - LINE_T[i] - .1) / .3
        if 0 < u < 1:
            qx, qy = lerp(tx, ex, u), lerp(ty, ey, u)
            dp.ellipse(((qx - x0) / 2 - 5, (qy - y0) / 2 - 5, (qx - x0) / 2 + 5, (qy - y0) / 2 + 5), fill=255)
    if not can.getbbox(): return None
    core = can.resize((x1 - x0, y1 - y0), Image.BILINEAR)
    glow = can.filter(ImageFilter.GaussianBlur(5)).resize(core.size, Image.BILINEAR).point(lambda v: int(min(255, v * 2.2)))
    pg = pul.filter(ImageFilter.GaussianBlur(3)).resize(core.size, Image.BILINEAR).point(lambda v: int(min(255, v * 2.5)))
    out = K.colorize(glow, (120, 90, 255))
    out.alpha_composite(K.colorize(core, K.grad_img(core.width, core.height, K.GRAD_L)))
    out.alpha_composite(K.colorize(pg, (250, 248, 255)))
    return x0, y0, out


def tile_pose_f(i, t):
    """team tiles in seg 25-26: mini row, spreading on "usada" to feed the chosen AI."""
    x, y, s, la = card_pose(i, t)
    if t >= LIFT0:
        k = expo((t - LIFT0 - .04 * i) / .3)
        x = lerp(x, SPREAD_X[i], k); y = lerp(y, MINI_Y + 6, k); s = lerp(s, MINI_S * 1.12, k)
    return x, y, s


def draw_right_ai(ctx, t):
    """seg 25-26 (53.47 – 57.08)."""
    P = ctx.post
    # camera: from the cards' close shot back to a calmer medium; punch on the lock and on the stamp
    c0 = cards_cam(min(t, FOLD0))
    k = expo((t - FOLD0) / .4) if t >= FOLD0 else 0.0
    z = lerp(c0['z'], 1.06, k) + .04 * smooth((t - FOLD1) / (END - FOLD1))
    if t >= LOCK: z += .03 * decay(t, LOCK, .12)
    if t >= STAMP: z += .05 * expo((t - STAMP) / .1) * (1 - .5 * smooth((t - STAMP - .12) / .3))
    ctx.cam = dict(z=z, x=540., y=lerp(760, 700, k), dx=lerp(c0['dx'], 0, k), dy=lerp(0, -34, k), rot=0.)
    sx, sy = shake(t, LOCK, 9, .1, 21); sx2, sy2 = shake(t, STAMP, 15, .14, 17, 2.0)
    ctx.cam['dx'] += sx + sx2; ctx.cam['dy'] += sy + sy2
    ctx.bg_dim = .14 + .3 * smooth((t - STAMP + .05) / .12)
    ctx.avatar['bright'] = 1 - .25 * smooth((t - STAMP + .05) / .12)
    lights = []
    if t >= LOCK: lights.append((K.blob(760, 300, (110, 70, 255), 90, 1.0), 540, RY, .6 * decay(t, LOCK, .2) + .1))
    if t >= STAMP: lights.append((K.blob(760, 640, (110, 70, 255), 110, 1.0), 540, RY - 10, .45 * decay(t, STAMP, .25) + .13))
    ctx.wrap = dof_wrap(3.2 + 1.5 * smooth((t - STAMP) / .15), lights)
    ux, uy = sx + sx2, sy + sy2
    after = 1 - .82 * smooth((t - STAMP + .02) / .1) if t >= STAMP - .02 else 1.0     # the rest steps back for the seal
    # ---- team tiles
    if t < LIFT0: draw_cards(ctx, t, ux, uy)
    else:
        for i in range(3):
            x, y, s = tile_pose_f(i, t)
            full, pad = card_full(i, False)
            img = K.scale_im(full, s)
            if t >= O['CERTO'] - .02 and t < STAMP + .3:
                img = K.sheen(img, clamp((t - O['CERTO'] + .02 - .04 * i) / .3), .3, .8)
            ctx.add('screen', img, x + ux, y + uy, glass=8, alpha=after)
            ctx.add('screen', K.scale_im(card_icon(i), s * 1.3), x + ux, y + uy, alpha=after)
    # ---- the slot machine
    lift = expo((t - LIFT0) / .3) if t >= LIFT0 else 0.0
    if t >= REEL0 - .04:
        kk = back((t - REEL0 + .04) / .26, 1.7)
        win, pad = reel_window()
        wa = clamp((t - REEL0 + .04) / .06) * (1 - smooth((t - LIFT0) / .22))
        oy = 40 * (1 - kk)
        if wa > .01:
            ws = (.7 + .3 * kk) * lerp(1, 1.06, lift)
            ctx.add('screen', K.scale_im(win, ws), RX + ux, RY + uy + oy, glass=14, alpha=wa)
            can = reel_canvas(t, others=1 - smooth((t - LIFT0) / .15), hide_sel=t >= LIFT0 - .01)
            ctx.add('screen', K.scale_im(can, ws), RX + ux, RY + uy + oy, alpha=wa)
        # reticle: hunts from "IA", contracts, LOCKS on "CER-"
        if O['IA5'] - .02 <= t < LIFT0 + .2:
            ra = clamp((t - O['IA5'] + .02) / .08) * (1 - smooth((t - LIFT0) / .15))
            if t < LOCK:
                q = clamp((t - O['IA5']) / (LOCK - O['IA5']))
                s = lerp(1.3, 1.07, ein(q)); jx = 12 * math.sin(t * 23) * (1 - q); jy = 7 * math.cos(t * 17) * (1 - q)
                br = K.brackets(int((CHW + 40) * s), int((CHH + 22) * s), 46, 5, (235, 230, 255), .85)
            else:
                u = t - LOCK; s = 1 - .05 * math.exp(-u / .05) * math.cos(u * 60); jx = jy = 0
                br = K.brackets(int((CHW + 40) * s), int((CHH + 22) * s), 54, 7, (250, 249, 255), 1.0)
            ctx.add('screen', br, RX + ux + jx, RY + uy + jy, alpha=ra)
            if LOCK <= t < LOCK + .3:
                u = (t - LOCK) / .3
                ctx.add('screen', K.scale_im(K.ring(400 + 200 * eout(u), 5, (235, 228, 255), (1 - u) * .9), 1, .32), RX + ux, RY + uy)
        # the chosen chip stays, grows a little; the cursor clicks it; the team lines feed it
        if t >= LIFT0 - .01:
            ci = int(round(P_END)) % len(CHIPS)
            im, pad = chip(ci, True)
            cs = lerp(1.0, 1.06, lift)
            if t >= CLICK: cs *= 1 - .05 * math.exp(-(t - CLICK) / .05) * (t - CLICK < .2)
            cy = RY + 10 * lift
            img = K.scale_im(im, cs)
            if t >= CLICK and t - CLICK < .45: img = K.sheen(img, (t - CLICK) / .45, .2, .8)
            ctx.add('screen', img, RX + ux, cy + uy, alpha=after)
            tiles = []
            for i in range(3):
                x, y, s = tile_pose_f(i, t); tiles.append((x + ux, y + uy + CH * s / 2 + 4))
            gk = smooth((t - O['CERTO'] + .02) / .1)
            fl = feed_lines(t, tiles, (RX + ux, cy + uy), gk)
            if fl is not None: ctx.add('screen', fl[2], fl[0], fl[1], center=False, alpha=after)
            if CLICK - .2 <= t < CLICK + .45:
                ck = expo((t - CLICK + .2) / .2)
                cxp, cyp = lerp(990, 760, ck), lerp(1780, RY + 26, ck)
                cur = K.cursor(70)
                if t >= CLICK: cur = K.scale_im(cur, 1 - .14 * math.exp(-(t - CLICK) / .05))
                ctx.add('screen', cur, cxp + 18 + ux, cyp + 24 + uy, alpha=clamp(1 - (t - CLICK - .25) / .2))
                if t >= CLICK and t - CLICK < .3:
                    u = (t - CLICK) / .3
                    ctx.add('screen', K.ring(14 + 74 * eout(u), 3, (240, 236, 255), 1 - u), cxp + ux, cyp + uy)
    # ---- the ✓ seal STAMPS on "CER-to"
    if t >= STAMP - .07:
        u = t - STAMP + .07
        if u < .07: s = lerp(1.8, 1.0, ein(clamp(u / .07))); rot = lerp(-14, 0, ein(clamp(u / .07)))
        else: s = 1 - .07 * math.exp(-(u - .07) / .06) * math.cos((u - .07) * 45); rot = 0.0
        sl = seal(470)
        sw = (t - STAMP - .14) / .45
        if 0 < sw < 1: sl = K.sheen(sl, sw, .12, .6)
        sl = K.scale_im(sl, s)
        if rot: sl = sl.rotate(rot, Image.BICUBIC, expand=True)
        ctx.add('screen', sl, 540 + ux, RY - 20 + uy, alpha=clamp(u / .05))
        if t >= STAMP and t - STAMP < .42:
            v = (t - STAMP) / .42
            ctx.add('screen', K.ring(240 + 420 * eout(v), 7, (236, 230, 255), (1 - v) * .85), 540 + ux, RY - 20 + uy)
        if t >= STAMP:
            P['flash'] = .05 * decay(t, STAMP, .05); P['flash_col'] = (236, 228, 255)
            P['bright'] = 1 + .10 * decay(t, STAMP, .07)
    if t >= LOCK:
        P['bright'] = max(P['bright'], 1 + .10 * decay(t, LOCK, .06))
        P['rgb'] = max(P['rgb'], 4 * clamp(1 - (t - LOCK) / .1))
    # ---- captions (top)
    K.caps_layer(ctx, t, [(O['E5'] - .04, O['A5'] - .02, [('E,', O['E5'], False), ('PRINCIPALMENTE,', O['PRINCIPALMENTE'], False)]),
                          (O['A5'] - .04, O['USADA'] - .02, [('A', O['A5'], False), ('IA', O['IA5'], False), ('CERTA,', O['CERTA'], True)]),
                          (O['USADA'] - .04, O['JEITO'] - .02, [('USADA', O['USADA'], False), ('DO', O['DO6'], False)]),
                          (O['JEITO'] - .04, END, [('JEITO', O['JEITO'], False), ('CERTO.', O['CERTO'], True)])], y=330)
    P['vignette'] = .36 + .1 * smooth((t - STAMP) / .2)
    # ---- exit frame (s08's pose surfaces one frame early): crash-zoom blur + light
    if t >= T_EXIT:
        # s08 opens on a hard stop (the lights die).  This frame already shows s08's pose: a smooth crash-zoom into the
        # seal that takes everything with it (UI + captions) and drops the exposure into s08's dark stage.
        layers = ctx.screen; ctx.screen = []; prev = ctx.wrap
        def exit_wrap(fr, layers=layers, prev=prev):
            fr = prev(fr) if prev else fr
            for L in layers: E._paste(fr, L)
            return K.zoom_smear(fr, .30, 540 + ux, RY - 20 + uy, n=14, dark=.62)
        ctx.wrap = exit_wrap
        P['zoom_blur'] = 0.0; P['flash'] = 0.0; P['rgb'] = 0.0; P['vignette'] = .55


# ================================================================ draw
def draw(ctx, lt, t):
    ctx.captions = False
    if t < T20: draw_stage(ctx, t)
    elif t < T21: draw_agent_seg(ctx, t)
    elif t < T22: draw_team_seg(ctx, t)
    elif t < FOLD0: draw_cards_seg(ctx, t)
    else: draw_right_ai(ctx, t)
