"""s01 — HOOK (0.00–9.84): "Você já deve ter ouvido… ou até concorda… que IA só faz conteúdo genérico, né?
Imagem que parece banco de imagem… texto sem alma… vídeo que parece todos os outros."

THE GENERIC WORLD (cold, flat, all slightly the same): he sits in front of a dense, living WALL of generic-AI posts
(src/assets + drawn clichés: purple-gradient quotes, "10 DICAS 🚀" carousels, clickbait, emoji captions, "A IA VAI
SUBSTITUIR VOCÊ?"…) with DOF + parallax (2.5-D rig in _A_kit), engagement pings and ❤ pops on random tiles, and a cold
flat grade over everything.  Beats (ONSETS below, measured on src/tight16k.raw):
  0.00  open: 2-frame lights-up, camera rockets back from his face (Z 1.48 -> 1.06, expo) with a speed-driven zoom blur
        (world only: captions stay crisp) + RGB settle; the wall's screens refresh in a blink cascade from his head.
  0.88  "OUVIDO" (+1.04 "-VI-", 1.18, 1.30): iOS-style notification pings drop in above his head and pile into a stack
        (older ones pushed back, dimmer) — tiles flash with each ping; 1.40 "OU" the stack is swiped away.
  1.96  "conCORda" (2.00): a giant glossy 👍 reaction springs in beside him (+1), the CAMERA NODS twice (agreeing),
        a wave of 👍 badges pops on every tile from the centre out, live reactions stream up the right edge.
  2.55  "IA": every AI-brain tile glows cyan.  2.87 "SÓ FAZ": the wall starts scrolling like an endless feed; on
        "CONTEÚDO" it races (motion-blurred).
  3.70  "geNÉrico": the red GENÉRICO rubber stamp SLAMS on the frame (it IS the caption word): the feed stops dead,
        camera shake, ink specks, a red light hit, everything drains to grey.  4.12 "NÉ?" cheeky push-in on his face.
  4.47  the stamp lifts off, colour back; the camera cranes him down while a stock-photo tile peels out of the wall
        (3-D flight, rack focus) and lands as a big card on 4.75 "IMAGEM"; 5.22 "PARECE" the plastic smiles go
        *ting* (✨ on each set of teeth); 5.55 "BANCO" shutter flash + a stock watermark lattice; 5.86 PREVIEW strip.
  6.50  the card flicks away; 6.62 "TEXTO" a generated caption types itself in token bursts ("🚀 Desbloqueie seu
        potencial!…") over an EKG strip "ALMA ♥" beating with the flatline cue's beeps (6.22 pre-lap, 6.64); 7.06 "ALMA": the next
        beat never comes -> FLATLINE tone + trace flat + red, "SEM SINAL", the card greys.
  7.84  vertical whip -> 7.93 "VÍDEO" full frame: one phone playing a generic AI reel; 8.24 "PARECE" x3, 8.77 "TODOS"
        x9 (every reel cuts to the same next shot in sync), 9.16 "OUTROS" x25; 9.42 all 25 get the same ❤ at once.
  9.8333 (first frame of seg 3's pose) -> s02 draws it (the scratch).
Captions: own word pops (engine look) on the measured onsets; "GENÉRICO" is the stamp itself.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _A_kit as K
from sections import _shared as SH

START, END = E.span(0, 2)                       # 0.00 – 9.84
W, H = E.W, E.H

# word onsets (timeline s) measured on src/tight16k.raw: 5 ms STFT with 80-900 Hz / 1-3 kHz / >3.5 kHz band envelopes +
# a 1024-pt narrow-band formant view for vowel boundaries (the engine's syllable estimate runs up to .2 s late here)
ONSETS = dict(
    # seg 0  "Você já deve ter ouvido… ou até concorda… que IA só faz conteúdo genérico, né?"
    VOCE=0.09, JA=0.38, DEVE=0.52, TER=0.745, OUVIDO=0.88, VI=1.04, OU0=1.40, ATE=1.56, CONCORDA=1.78, COR=2.00,
    QUE0=2.46, IA0=2.55, SO0=2.87, FAZ=3.06, CONTEUDO=3.22, GENERICO=3.60, NE_ST=3.70, NE=4.12, END0=4.37,
    # seg 1  "Imagem que parece banco de imagem… texto sem alma…"
    IMAGEM=4.75, QUE1=5.12, PARECE1=5.22, BANCO=5.55, DE=5.78, IMAGEM2=5.86, MA2=5.98, TEXTO=6.62, SEM=6.91,
    ALMA=7.06, END1=7.56,
    # seg 2  "vídeo que parece todos os outros."
    VIDEO=7.93, QUE2=8.14, PARECE2=8.24, TODOS=8.77, OS=9.02, OUTROS=9.16, END2=9.57,
)
Wd = ONSETS
lerp, clamp, eio, expo, eo = K.lerp, E.clamp, K.eio, K.expo, K.eo

T_STAMP = Wd['NE_ST']                           # 3.70 the stamp lands (stressed "NÉ" of genérico)
T_LIFT = 4.47                                   # stamp lifts off, colour back
T_FLY0, T_LAND = 4.50, Wd['IMAGEM']             # stock tile peels out of the wall -> lands on "IMAGEM"
T_FLICK = 6.50                                  # stock card flicks away
T_TYPE = Wd['TEXTO']                            # caption types itself
T_FLAT = Wd['ALMA']                             # flatline
T_WHIP = 7.84                                   # whip up into the phones
T_PH = Wd['VIDEO']                              # 7.93 phone stage
STAGES = [(T_PH, 1), (Wd['PARECE2'], 3), (Wd['TODOS'], 9), (Wd['OUTROS'], 25)]
NOTIF_T = [Wd['OUVIDO'], Wd['VI'], 1.18, 1.30]
SCROLL0, SCROLL_D = Wd['SO0'], 1.0             # feed scroll starts on "SÓ"; distance in rows

CUES = [
    (0.00, 'boom', {'gain': -6}), (0.00, 'whoosh', {'gain': -5}), (0.03, 'glitch', {'gain': -16}),
    (NOTIF_T[0], 'notify', {'gain': -3, 'pan': -.25}), (NOTIF_T[1], 'notify', {'gain': -5, 'pan': .25}),
    (NOTIF_T[2], 'notify', {'gain': -7, 'pan': -.15}), (NOTIF_T[3], 'notify', {'gain': -8, 'pan': .2}),
    (1.42, 'swipe', {'gain': -12}),
    (Wd['COR'] - .02, 'pop', {'gain': 0}), (Wd['COR'], 'ding', {'note': 'E6', 'gain': -10}),
    (2.06, 'pop', {'gain': -14, 'pan': .5}), (2.12, 'pop', {'gain': -15, 'pan': -.4}), (2.19, 'pop', {'gain': -16, 'pan': .3}),
    (Wd['IA0'], 'shimmer', {'gain': -13}),
    (3.02, 'ff', {'dur': .68, 'gain': -9}),
    (T_STAMP, 'stamp', {'gain': 0}), (T_STAMP, 'thud', {'gain': -5}),
    (Wd['NE'], 'swoosh_up', {'gain': -13}), (Wd['NE'] + .02, 'pop', {'gain': -12}),
    (T_LIFT, 'whoosh', {'gain': -10}), (T_FLY0 + .06, 'swoosh_up', {'gain': -9}), (T_LAND, 'flick', {'gain': -6}),
    (Wd['PARECE1'], 'shimmer', {'gain': -11}), (Wd['PARECE1'] + .02, 'ding', {'note': 'B6', 'gain': -15}),
    (Wd['BANCO'], 'shutter', {'gain': -3}), (Wd['BANCO'] + .02, 'stamp', {'gain': -13}),
    (Wd['IMAGEM2'], 'click', {'gain': -8}),
    (T_FLICK + .08, 'swipe', {'gain': -4}),                         # peak on the flick's fastest frames
] + [(T_TYPE + .03 + i * .055, 'type', {'i': i, 'gain': -11}) for i in range(7)] + [
    # the EKG: sound.py's flatline = beep (+0) · beep (+.42) · flat tone from +.84 -> the cue starts .84 s early so the
    # FLAT tone lands exactly on "ALMA" (the first beep pre-laps the card; the trace shows that beat in its history)
    (T_FLAT - .84, 'flatline', {'dur': 1.6, 'gain': -5}),
    (T_WHIP, 'whoosh', {'gain': -5}),
    (T_PH, 'pop', {'gain': -4}),
    (STAGES[1][0], 'pop', {'gain': -6, 'pan': -.5}), (STAGES[1][0] + .03, 'pop', {'gain': -6, 'pan': .5}),
    (STAGES[2][0], 'whoosh', {'gain': -12}),
] + [(STAGES[2][0] + .02 * i, 'pop', {'gain': -9 - i, 'pan': (-.6, .6, -.3, .3, -.8, .8)[i]}) for i in range(6)] + [
    (STAGES[3][0], 'whoosh', {'gain': -11}),
] + [(STAGES[3][0] + .015 * i, 'pop', {'gain': -12 - .5 * i, 'pan': ((i * .37) % 1.6) - .8}) for i in range(10)] + [
    (Wd['OUTROS'] + .26, 'pop', {'gain': -4}), (Wd['OUTROS'] + .26, 'heart', {'gain': -12})]

# =========================================================================================== captions
def _pages():
    def mk():
        P = K.page
        pg = [P([('VOCÊ', Wd['VOCE'], 0), ('JÁ', Wd['JA'], 0), ('DEVE', Wd['DEVE'], 0)]),
              P([('TER', Wd['TER'], 0), ('OUVIDO…', Wd['OUVIDO'], 0)]),
              P([('OU', Wd['OU0'], 0), ('ATÉ', Wd['ATE'], 0), ('CONCORDA…', Wd['CONCORDA'], 1)]),
              P([('QUE', Wd['QUE0'], 0), ('IA', Wd['IA0'], 0), ('SÓ', Wd['SO0'], 0), ('FAZ', Wd['FAZ'], 0)]),
              P([('CONTEÚDO', Wd['CONTEUDO'], 0)]),
              P([('NÉ?', Wd['NE'], 0)], z=T_LIFT + .06),
              P([('IMAGEM', Wd['IMAGEM'], 0), ('QUE', Wd['QUE1'], 0), ('PARECE', Wd['PARECE1'], 0)]),
              P([('BANCO', Wd['BANCO'], 1), ('DE', Wd['DE'], 0), ('IMAGEM…', Wd['IMAGEM2'], 0)]),
              P([('TEXTO', Wd['TEXTO'], 0), ('SEM', Wd['SEM'], 0), ('ALMA…', Wd['ALMA'], 1)], z=T_WHIP + .02),
              P([('VÍDEO', Wd['VIDEO'], 0), ('QUE', Wd['QUE2'], 0), ('PARECE', Wd['PARECE2'], 0)]),
              P([('TODOS', Wd['TODOS'], 0), ('OS', Wd['OS'], 0), ('OUTROS.', Wd['OUTROS'], 1)])]
        return K.chain(pg, K.CUT3)
    return E.cached('A1_pages', mk)

def cap_y(t):
    if t < Wd['CONTEUDO'] - .05: return 1440
    if t < T_LIFT + .1: return 1262
    if t < T_PH - .05: return 1545
    return 1540

# =========================================================================================== camera
R1 = K.Cam(1.06, 540, 930)
def shot_cam(t):
    """him-plane virtual camera for the wall beats (0 – 7.93)."""
    if t < .62:
        u = clamp(t / .62); k = 1 - (1 - u) ** 4
        c = K.mix_cam(K.Cam(1.48, 540, 888), R1, k)
    elif t < Wd['OU0']:
        c = K.Cam(1.06 + .03 * eio((t - .62) / .78), 540, 930)
    elif t < Wd['QUE0']:
        a = K.Cam(1.09, 540, 930); b = K.Cam(1.13, 558, 922)
        c = K.mix_cam(a, b, eio((t - Wd['OU0']) / .22)); c.Z += .02 * clamp((t - 1.62) / .84)
    elif t < T_STAMP:
        a = K.Cam(1.15, 558, 922); b = K.Cam(1.17, 540, 930)
        c = K.mix_cam(a, b, eio((t - Wd['QUE0']) / .25)); c.Z += .045 * eio((t - 2.7) / 1.0)
    elif t < Wd['NE']:
        c = K.Cam(1.215, 540, 930)
    elif t < T_LIFT:
        c = K.mix_cam(K.Cam(1.215, 540, 930), K.Cam(1.36, 540, 902), 1 - (1 - clamp((t - Wd['NE']) / .24)) ** 4)
    else:
        G0 = K.Cam(1.0, 540, 668); G1 = K.Cam(1.035, 540, 676)
        if t < T_LAND:
            c = K.mix_cam(K.Cam(1.36, 540, 902), G0, eio((t - T_LIFT) / (T_LAND - T_LIFT - .02)))
        else:
            c = K.mix_cam(G0, G1, clamp((t - T_LAND) / (T_PH - T_LAND)))
    # nod (agreeing) on "concorda": two quick vertical bobs
    for tn, amp in ((Wd['COR'] - .03, 20.), (Wd['COR'] + .19, 14.)):
        u = t - tn
        if 0 <= u < .2: c.sy += amp * math.sin(math.pi * u / .2) ** 2
    # stamp impact shake
    dx, dy = K.shake(t, T_STAMP, 26., tau=.13, f=17., seed=.7); c.sx += dx; c.sy += dy
    dx, dy = K.shake(t, T_LAND, 5., tau=.08, f=14.); c.sx += dx; c.sy += dy
    return c

def scroll_at(t):
    """feed scroll (texture px): accelerates from "SÓ", races on "CONTEÚDO", stops dead on the stamp."""
    if t < SCROLL0: return 0.0
    u = (min(t, T_STAMP) - SCROLL0) / (T_STAMP - SCROLL0)
    return SCROLL_D * K.STEP_Y * (u ** 2.6) * 2.4

def scroll_speed(t):
    if t < SCROLL0 or t >= T_STAMP: return 0.0
    return (scroll_at(t + .5 / 30) - scroll_at(t - .5 / 30)) * 30

# =========================================================================================== wall life
def _tile_center_d(cam, c, r):
    x0, y0, x1, y1 = K.tile_screen(cam, c, r)
    return math.hypot((x0 + x1) / 2 - 540, (y0 + y1) / 2 - 720)

def _power_on(c, r):
    """screen power-on time of tile (c, r): from his head outward + a little jitter."""
    d = math.hypot(c - 3, (r - 2.6) * 1.15); j = ((c * 7 + r * 13) % 5) / 5
    return .015 + d * .055 + j * .035

PING_T = None
def _pings():
    """seeded random 'engagement' pings on tiles (living wall) + bursts synced to the notifications."""
    def mk():
        r = K.rnd(5); out = []
        for i in range(26):
            out.append((float(r.uniform(.35, 7.6)), int(r.integers(0, K.COLS)), int(r.integers(0, K.ROWS)), 'flash'))
        for tn in NOTIF_T:
            for j in range(3): out.append((tn + .015 * j, int(r.integers(1, K.COLS - 1)), int(r.integers(0, 5)), 'flash'))
        for i in range(18):
            out.append((float(r.uniform(.4, 7.6)), int(r.integers(0, K.COLS)), int(r.integers(0, K.ROWS)), 'heart'))
        return out
    return E.cached('A1_pings', mk)

def like_badge(sz):
    def mk():
        S = sz * 3; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((0, 0, S - 1, S - 1), fill=(37, 99, 235, 255), outline=(255, 255, 255, 255), width=int(S * .06))
        th = K.silhouette('👍', int(S * .54)); im.alpha_composite(th, ((S - th.width) // 2, (S - th.height) // 2 - int(S * .02)))
        return im.resize((sz, sz), Image.LANCZOS)
    return E.cached(('A1_lb', sz), mk)

def heart_badge(sz):
    def mk():
        S = sz * 3; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((0, 0, S - 1, S - 1), fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=int(S * .06))
        th = K.silhouette('❤', int(S * .5)); im.alpha_composite(th, ((S - th.width) // 2, (S - th.height) // 2 + int(S * .02)))
        return im.resize((sz, sz), Image.LANCZOS)
    return E.cached(('A1_hb', sz), mk)

def wall_life(ctx, t, wc, scroll):
    """overlays on the wall tiles (behind him): power-on, pings, 👍 wave, IA glow."""
    tiles = K.visible_tiles(wc, scroll, margin=10)
    can = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(can)
    lay = K.wall_layout()
    # opening: the screens refresh in a blink cascade from his head outward (frame 0 stays clean)
    if .02 < t < .5:
        for (c, r), kv, (x0, y0, x1, y1) in tiles:
            u = t - _power_on(c, r) - .02
            if 0 <= u < .09: d.rectangle((x0, y0, x1, y1), fill=(235, 242, 255, int(170 * (1 - u / .09) ** 1.4)))
    # pings: a tile flashes like a new notification
    for (tp, c, r, kind) in _pings():
        u = t - tp
        if kind == 'flash' and 0 <= u < .22:
            x0, y0, x1, y1 = K.tile_screen(wc, c, r, scroll)
            d.rectangle((x0, y0, x1, y1), fill=(240, 246, 255, int(150 * (1 - u / .22) ** 1.5)))
    ctx.add('behind', can, 0, 0, center=False)
    # IA: every AI-brain tile lights up cyan (soft glow + crisp neon frame), the rest of the wall dims a touch
    u = t - Wd['IA0']
    if -.02 < u < .75:
        k = clamp((u + .02) / .05) * (1 - clamp((u - .35) / .4))
        flick = 1.0 if u > .1 else (.55 + .45 * (int(u * 60) % 2))      # neon tubes flicker on
        k *= flick
        dim = Image.new('RGBA', (W, H), (8, 12, 26, int(70 * k)))
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(gl)
        cr = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(cr)
        for (c, r), (kind, v), (x0, y0, x1, y1) in tiles:
            if kind in ('ai_brain', 'substituir'):
                ImageDraw.Draw(dim).rectangle((x0 - 10, y0 - 10, x1 + 10, y1 + 10), fill=(0, 0, 0, 0))
                dg.rounded_rectangle((x0 - 10, y0 - 10, x1 + 10, y1 + 10), 14, outline=(90, 225, 255, int(255 * k)), width=22)
                dg.rectangle((x0, y0, x1, y1), fill=(60, 200, 255, int(95 * k)))
                dc.rounded_rectangle((x0 - 5, y0 - 5, x1 + 5, y1 + 5), 10, outline=(200, 248, 255, int(240 * k)), width=4)
        ctx.add('behind', dim, 0, 0, center=False)
        ctx.add('behind', gl.filter(ImageFilter.GaussianBlur(9)), 0, 0, center=False)
        ctx.add('behind', cr, 0, 0, center=False)
    # hearts + 👍 badges popping on tiles (sprites)
    for (tp, c, r, kind) in _pings():
        u = t - tp
        if kind == 'heart' and 0 <= u < .5:
            x0, y0, x1, y1 = K.tile_screen(wc, c, r, scroll); sz = max(16, int((x1 - x0) * .26))
            s = .5 + .5 * K.back(u / .14, 2.4); b = K.scaled(heart_badge(sz), s)
            ctx.add('behind', b, x1 - sz * .55, y1 - sz * .55, alpha=1 - clamp((u - .35) / .15))
    u0 = Wd['COR']
    if u0 - .05 < t < 2.46:                             # the 👍 wave pops out (shrink + fade) before "IA" so that beat reads clean
        for (c, r), kv, (x0, y0, x1, y1) in tiles:
            tp = u0 + _tile_center_d(wc, c, r) / 2600.
            u = t - tp
            if u < 0: continue
            o = clamp((t - 2.30) / .15)
            sz = max(20, int((x1 - x0) * .36)); s = (.4 + .6 * K.back(u / .13, 2.6)) * (1 - .5 * K.ei(o))
            ctx.add('behind', K.scaled(like_badge(sz), s), (x0 + x1) / 2, (y0 + y1) / 2, alpha=1 - o)

# =========================================================================================== notifications ("ouvido")
NOTIFS = [('✨', [(168, 85, 247), (236, 72, 153)], 'IA Mágica', 'Seus 100 posts estão prontos! 🚀'),
          ('🔥', [(249, 115, 22), (239, 68, 68)], 'ViralizaJá', 'Gere conteúdo infinito em 1 clique'),
          ('🤖', [(59, 130, 246), (14, 165, 233)], 'Robô de Posts', 'Novo template: “Bom dia, sucesso!” ☀️'),
          ('📈', [(34, 197, 94), (16, 185, 129)], 'Guru do Digital', 'A IA vai substituir você? Veja…')]
NW, NH = 900, 140
def notif_img(i):
    def mk():
        emo, cols, title, body = NOTIFS[i]
        im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
        m = Image.new('L', (NW, NH)); ImageDraw.Draw(m).rounded_rectangle((0, 0, NW - 1, NH - 1), 30, fill=238)
        bg = Image.new('RGBA', (NW, NH), (246, 247, 250, 0)); bg.putalpha(m); im.alpha_composite(bg)
        ic = K._grad_img(86, 86, cols).convert('RGBA'); im.alpha_composite(E.rounded(ic, 22), (20, 24))
        e = K.emoji(emo, 50); im.alpha_composite(e, (20 + (86 - e.width) // 2, 24 + (86 - e.height) // 2))
        im.alpha_composite(K.rich(title, K.inter(36, 'SemiBold'), (17, 17, 20)), (122, 13))
        ag = K.rich('agora', K.inter(24, 'Regular'), (120, 120, 130)); im.alpha_composite(ag, (NW - ag.width - 26, 20))
        im.alpha_composite(K.rich(body, K.inter(34, 'Regular'), (55, 55, 62), esize=34), (122, 68))
        return K.soft_shadow(im, 22, .35, (0, 12))
    return E.cached(('A1_notif', i), mk)

def notifications(ctx, t):
    """iOS-style stack: each new ping drops in front, the older ones are pushed back (peeking below, smaller, dimmer)."""
    if t < NOTIF_T[0] - .02 or t > 1.62: return
    out = clamp((t - 1.40) / .16)                       # the whole stack swipes away up on "ou"
    n = len([tn for tn in NOTIF_T if t >= tn - .02])
    for i in range(n):                                   # oldest first = furthest back
        u = t - NOTIF_T[i]
        slot = 0.0
        for j in range(i + 1, n): slot += eo((t - NOTIF_T[j] + .02) / .14, 3)
        y = 300 + 30 * slot
        s = 1 - .055 * slot
        k = K.back(u / .2, 1.5); y = lerp(-150, y, k)
        y -= 1000 * K.ei(out, 2.2) * (1 - .08 * slot)
        im = notif_img(i)
        if slot > .05:                                   # pushed back: dimmer
            im = E.cached(('A1_notif_dim', i), lambda i=i: K.grade(notif_img(i), bright=.78, sat=.8))
        a = clamp((u + .02) / .05) * (1 - clamp((slot - 2.4) / .6))
        if out > 0: a *= 1 - clamp((out - .6) / .4)
        img = K.scaled(im, s)
        if u < .12:
            img, ox, oy = K.mblur(img, 0, 30 * (1 - u / .12)); y += oy
        ctx.add('front', img, 540, y, alpha=a)

# =========================================================================================== 👍 "concorda"
def like_big(sz):
    def mk():
        S = sz * 2; im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        g = K._grad_img(S, S, [(96, 165, 250), (37, 99, 235), (29, 78, 216)]).convert('RGBA')
        m = Image.new('L', (S, S)); ImageDraw.Draw(m).ellipse((4, 4, S - 5, S - 5), fill=255); g.putalpha(m); im.alpha_composite(g)
        ring = Image.new('L', (S, S)); ImageDraw.Draw(ring).ellipse((4, 4, S - 5, S - 5), outline=255, width=int(S * .035))
        wr = Image.new('RGBA', (S, S), (255, 255, 255, 0)); wr.putalpha(ring); im.alpha_composite(wr)
        th = K.silhouette('👍', int(S * .56)); im.alpha_composite(th, ((S - th.width) // 2 - int(S * .01), (S - th.height) // 2 - int(S * .03)))
        gl = Image.new('L', (S, S)); ImageDraw.Draw(gl).ellipse((S * .18, S * .07, S * .82, S * .42), fill=70)
        gls = Image.new('RGBA', (S, S), (255, 255, 255, 0)); gls.putalpha(Image.fromarray(np.minimum(np.asarray(gl), np.asarray(m))).filter(ImageFilter.GaussianBlur(S * .02)))
        im.alpha_composite(gls)
        im = im.resize((sz, sz), Image.LANCZOS)
        return K.soft_shadow(im, 24, .45, (0, 16))
    return E.cached(('A1_likebig', sz), mk)

def plus_one():
    return E.cached('A1_plus1', lambda: K.soft_shadow(K.rich('+1', K.inter(64, 'Black'), (255, 255, 255), stroke=5, stroke_col=(29, 78, 216)), 10, .4, (0, 6)))

def concorda(ctx, t, cam):
    t0 = Wd['COR'] - .04
    u = t - t0
    if u < 0 or t > 2.56: return
    out = clamp((t - 2.36) / .14)
    sz = 262
    s = K.spring(u, 3.0, 6.5) * (1 - .25 * K.ei(out))
    sq = 1 + .14 * math.exp(-u / .08) * math.sin(u * 50)            # squash & stretch
    im = like_big(sz)
    im = im.resize((max(1, int(im.width * s / sq)), max(1, int(im.height * s * sq))), Image.BILINEAR)
    im = K.rotated(im, 10 * math.exp(-u / .18) * math.sin(u * 26))
    x, y = cam.scr(822, 560)
    ctx.add('front', im, x, y - 30 * K.ei(out), alpha=clamp(u / .04) * (1 - out))
    if u > .1:
        v = u - .1; p1 = plus_one()
        ctx.add('front', p1, x + 112, y - 128 - 60 * eo(v / .5), alpha=clamp(v / .06) * (1 - clamp((v - .3) / .2)))
    # live reactions streaming up the right edge
    # (they rise from just above the caption's right end — never across "CONCORDA…" — and clear out before "IA")
    r = K.rnd(17)
    for i in range(11):
        tb = t0 + .03 + i * .036; v = t - tb
        sz2 = int(r.uniform(62, 86))
        x0 = 952 + r.uniform(-18, 26); ph = r.uniform(0, 6.28)
        if v < 0 or v > .75: continue
        yy = 1395 - 1080 * eo(v / .75, 2); xx = x0 + 22 * math.sin(v * 7 + ph)
        b = like_badge(sz2) if i % 3 != 2 else heart_badge(sz2)
        a = clamp(v / .06) * (1 - clamp((v - .5) / .25)) * (1 - clamp((t - 2.40) / .12))
        ctx.add('front', K.scaled(b, .6 + .4 * K.back(v / .15, 2)), xx, yy, alpha=a)

# =========================================================================================== the stamp
def stamp(ctx, t):
    if t < T_STAMP - .085 or t > T_LIFT + .2: return
    st = SH.generic_stamp(760)
    cx, cy = 540, 1468
    if t < T_STAMP:
        u = clamp((t - (T_STAMP - .085)) / .085); k = u ** 2.2
        s = lerp(2.7, 1.0, k); a = clamp(u * 2.2); rot = lerp(7, 0, k)
        im = K.rotated(K.scaled(st, s), rot)
        if s > 1.4: im = im.filter(ImageFilter.GaussianBlur((s - 1) * 3))
        ctx.add('screen', im, cx, cy, alpha=a * .9)
        return
    u = t - T_STAMP
    lift = clamp((t - T_LIFT) / .14)
    s = 1 + .035 * math.exp(-u / .05) * math.cos(u * 60) + .22 * K.ei(lift)
    im = K.scaled(st, s)
    if u < .12:      # ink squish: a soft wet halo right at the impact
        halo = st.filter(ImageFilter.GaussianBlur(7)); ctx.add('screen', K.scaled(halo, 1.03), cx, cy, alpha=.5 * (1 - u / .12))
    ctx.add('screen', im, cx, cy - 40 * K.ei(lift), alpha=1 - lift)
    # ink specks thrown off by the slam
    if u < .5:
        r = K.rnd(23)
        for i in range(16):
            ang = r.uniform(0, 6.28); dist = r.uniform(380, 520) * (1 + .25 * eo(u / .3)); sz = int(r.uniform(5, 14))
            x = cx + math.cos(ang) * dist * .9; y = cy + math.sin(ang) * dist * .34
            dot = E.cached(('A1_ink', sz), lambda sz=sz: _ink_dot(sz))
            ctx.add('screen', dot, x, y, alpha=(1 - clamp(u / .5)) * .9)

_RED_M = None
def red_hit(fr, k):
    """stamp impact: the frame keeps its contrast (punched a little), red light floods in from the edges."""
    global _RED_M
    if _RED_M is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((xx - W / 2) / (W * .62)) ** 2 + ((yy - H * .52) / (H * .6)) ** 2
        _RED_M = (np.clip(r2 - .25, 0, 1) ** .8)[..., None].astype(np.float32)
    a = np.asarray(fr.convert('RGB'), np.float32)
    a = (a - 118) * (1 + .22 * k) + 118                              # contrast punch
    m = _RED_M * k
    a = a * (1 - .55 * m) + np.array(SH.STAMP_RED, np.float32) * (.75 * m)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')

def _ink_dot(sz):
    im = Image.new('RGBA', (sz * 2, sz * 2), (0, 0, 0, 0)); ImageDraw.Draw(im).ellipse((sz * .5, sz * .5, sz * 1.5, sz * 1.5), fill=SH.STAMP_RED + (220,))
    return im.filter(ImageFilter.GaussianBlur(.8))

# =========================================================================================== stock photo card
CW, CH = 580, 725
CARD_C = (540, 506)
TEETH = [(232, 160), (420, 193), (100, 325), (500, 345)]           # the four plastic smiles on the card
def stock_card(stage):
    """stage 0: clean photo, 1: + watermark lattice, 2: + PREVIEW strip."""
    def mk():
        im = K._cover(E.asset('stock_team'), CW, CH, .5, .35, 1.02).convert('RGBA')
        if stage >= 1:
            lat = Image.new('RGBA', (CW * 2, CH * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lat)
            f = K.inter(30, 'SemiBold')
            for j in range(-2, 16):
                for i in range(-2, 8):
                    x = i * 250 + (j % 2) * 125; y = j * 92
                    d.text((x, y), 'bancodeimagem', font=f, fill=(255, 255, 255, 150))
            lat = lat.rotate(28, Image.BICUBIC)
            im.alpha_composite(lat.crop((CW // 2, CH // 2, CW // 2 + CW, CH // 2 + CH)))
            # centre mark: aperture glyph + wordmark
            mk_ = Image.new('RGBA', (CW, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(mk_)
            cx, cy, R = CW // 2, 70, 52
            d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(255, 255, 255, 200), width=7)
            for k in range(6):
                a = k * math.pi / 3; d.line((cx + R * .9 * math.cos(a), cy + R * .9 * math.sin(a), cx + R * .35 * math.cos(a + 1.2), cy + R * .35 * math.sin(a + 1.2)), fill=(255, 255, 255, 200), width=6)
            wm = K.rich('bancodeimagem', K.inter(58, 'Bold'), (255, 255, 255))
            wm2 = wm.copy(); wm2.putalpha(wm.getchannel('A').point(lambda v: int(v * .78)))
            mk_.alpha_composite(wm2, ((CW - wm.width) // 2, 132))
            sh = Image.new('RGBA', mk_.size, (0, 0, 0, 0)); sh.putalpha(mk_.getchannel('A').filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * .35)))
            im.alpha_composite(sh, (0, CH // 2 - 120)); im.alpha_composite(mk_, (0, CH // 2 - 124))
        if stage >= 2:
            bar = Image.new('RGBA', (CW, 74), (12, 12, 16, 190)); d = ImageDraw.Draw(bar)
            d.text((24, 18), 'PREVIEW', font=K.inter(32, 'ExtraBold'), fill=(255, 255, 255, 255))
            d.text((196, 22), '·  bancodeimagem  ·  amostra', font=K.inter(25, 'Medium'), fill=(200, 200, 210, 255))
            im.alpha_composite(bar, (0, CH - 74))
        im = E.rounded(im, 26)
        b = Image.new('L', (CW, CH)); ImageDraw.Draw(b).rounded_rectangle((1, 1, CW - 2, CH - 2), 26, outline=255, width=3)
        bo = Image.new('RGBA', (CW, CH), (255, 255, 255, 0)); bo.putalpha(b.point(lambda v: int(v * .5))); im.alpha_composite(bo)
        return im
    return E.cached(('A1_stock', stage), mk)

def stock(ctx, t, cam):
    if t < T_FLY0 or t > T_FLICK + .2: return
    wc = cam.wall()
    if t < T_LAND:                                     # peel out of the wall: 3-D flight + rack focus
        u = clamp((t - T_FLY0) / (T_LAND - T_FLY0)); k = 1 - (1 - u) ** 3
        x0, y0, x1, y1 = K.tile_screen(wc, 3, 2, scroll_at(t))
        s0 = (x1 - x0) / CW
        cx = lerp((x0 + x1) / 2, CARD_C[0], k); cy = lerp((y0 + y1) / 2, CARD_C[1], k) - 60 * math.sin(math.pi * k)
        s = lerp(s0, 1.0, k) * (1 + .06 * math.sin(math.pi * k))
        rx = -38 * math.sin(math.pi * u); ry = 16 * math.sin(math.pi * u); rz = -4 * math.sin(math.pi * u)
        im, ox, oy = K.card3d(stock_card(0), cx, cy, s, rx, ry, rz)
        blur = 3.2 * (1 - k) ** 1.5
        if blur > .4: im = im.filter(ImageFilter.GaussianBlur(blur))
        ctx.add('front', im, ox, oy, center=False, alpha=clamp(u / .08))
        return
    u = t - T_LAND
    stage = 2 if t >= Wd['IMAGEM2'] else 1 if t >= Wd['BANCO'] else 0
    fy = 6 * math.sin(u * 2.2); rz = .9 * math.sin(u * 1.6 + .5); ry = 3.0 * math.sin(u * 1.3)
    s = 1 + .05 * math.exp(-u / .07) * math.cos(u * 45)                 # landing settle
    if t >= Wd['BANCO']: s += .03 * math.exp(-(t - Wd['BANCO']) / .06)
    cx, cy = CARD_C[0], CARD_C[1] + fy
    fl = clamp((t - T_FLICK) / .16)
    if fl > 0:
        cx -= 1100 * K.ei(fl, 2.2); cy -= 120 * K.ei(fl); rz += 28 * K.ei(fl); ry -= 30 * fl
    im, ox, oy = K.card3d(stock_card(stage), cx, cy, s, 0, ry, rz)
    if fl > .05:
        im, mx, my = K.mblur(im, -90 * fl, -10 * fl); ox += mx; oy += my
    sh = shadow_for(im)
    ctx.add('front', sh, ox - 40, oy - 10, center=False, alpha=.85 * (1 - fl))
    ctx.add('front', im, ox, oy, center=False)
    # "parece": the plastic stock smiles go *ting* (teeth glints, staggered)
    for i, (px, py) in enumerate(TEETH):
        w = t - (Wd['PARECE1'] + .035 * i)
        if 0 <= w < .34 and fl <= 0:
            k = clamp(w / .03) * (1 - clamp((w - .24) / .1))
            sp = E.cached('A1_sparkle', lambda: K.soft_shadow(K.emoji('✨', 96), 6, .4, (0, 3)))
            sp = K.rotated(K.scaled(sp, .35 + .5 * K.back(w / .1, 2.4)), -25 * w / .34)
            ctx.add('front', sp, cx + (px - CW / 2) * s + 18, cy + (py - CH / 2) * s - 8, alpha=k)
    if Wd['BANCO'] <= t < Wd['BANCO'] + .2:             # shutter flash on the card
        k = 1 - (t - Wd['BANCO']) / .2
        fl_im = E.cached('A1_cardflash', lambda: E.rounded(Image.new('RGBA', (CW, CH), (255, 255, 255, 255)), 26))
        ctx.add('front', fl_im, cx, cy, alpha=.75 * k ** 2)

def shadow_for(im):
    a = im.getchannel('A').resize((im.width // 4 + 1, im.height // 4 + 1), Image.BILINEAR)
    pad = 20; m = Image.new('L', (a.width + 2 * pad, a.height + 2 * pad)); m.paste(a, (pad, pad + 4))
    m = m.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .5))
    sh = Image.new('RGBA', m.size, (4, 6, 14, 0)); sh.putalpha(m)
    return sh.resize((m.width * 4, m.height * 4), Image.BILINEAR)

# =========================================================================================== "texto sem alma" card
TW_, TH_ = 700, 590
TXT = '🚀 Desbloqueie seu potencial! No mundo acelerado de hoje, a inovação é a chave… ✨ #sucesso #mindset #IA'
def _txt_tokens():
    def mk():
        f = K.inter(38, 'Medium'); lines = K.wrap_words(TXT, f, TW_ - 84)
        toks = []
        for li, ln in enumerate(lines):
            for w in ln.split(' '): toks.append((li, w))
        return f, lines, toks
    return E.cached('A1_toks', mk)

def text_base():
    def mk():
        im = Image.new('RGBA', (TW_, TH_), (0, 0, 0, 0))
        m = Image.new('L', (TW_, TH_)); ImageDraw.Draw(m).rounded_rectangle((0, 0, TW_ - 1, TH_ - 1), 34, fill=242)
        bg = Image.new('RGBA', (TW_, TH_), (250, 250, 252, 0)); bg.putalpha(m); im.alpha_composite(bg)
        d = ImageDraw.Draw(im)
        av = K._grad_img(56, 56, [(168, 85, 247), (59, 130, 246)]).convert('RGBA')
        mm = Image.new('L', (56, 56)); ImageDraw.Draw(mm).ellipse((0, 0, 55, 55), fill=255); av.putalpha(mm)
        im.alpha_composite(av, (36, 30)); e = K.emoji('✨', 30); im.alpha_composite(e, (36 + 28 - e.width // 2, 30 + 28 - e.height // 2))
        im.alpha_composite(K.rich('Legenda gerada', K.inter(30, 'SemiBold'), (20, 20, 26)), (108, 28))
        im.alpha_composite(K.rich('automática · agora mesmo', K.inter(23, 'Regular'), (120, 120, 132)), (108, 64))
        d.rounded_rectangle((TW_ - 160, 38, TW_ - 36, 84), 23, fill=(234, 236, 242)); d.text((TW_ - 136, 46), 'Copiar', font=K.inter(25, 'SemiBold'), fill=(60, 60, 72))
        d.line((36, 112, TW_ - 36, 112), fill=(225, 226, 232), width=2)
        return im
    return E.cached('A1_txtbase', mk)

def text_body(n):
    """first n tokens of the generated caption, hashtags blue."""
    def mk():
        f, lines, toks = _txt_tokens()
        im = Image.new('RGBA', (TW_ - 72, 280), (0, 0, 0, 0)); xs = {}; y0 = 0
        last = (0, 0, 0)
        for k, (li, w) in enumerate(toks[:n]):
            x = xs.get(li, 0)
            col = (37, 99, 235) if w.startswith('#') else (30, 30, 36)
            r = K.rich(w, f, col, esize=39); im.alpha_composite(r, (int(x), int(li * 52)))
            xs[li] = x + r.width + f.getlength(' ') - 4; last = (xs[li], li * 52, r.height)
        return im, last
    return E.cached(('A1_txtbody', n), mk)

EKG_BEATS = [T_FLAT - .42 * k for k in range(5, 0, -1)]      # 4.96 … 6.22, 6.64 — the next one (7.06) never comes
def ekg_panel(t):
    """EKG strip: sweep trace, beats until "alma", then flat + red."""
    pw, ph = TW_ - 72, 166
    base = E.cached('A1_ekgbase', lambda: _ekg_base(pw, ph))
    im = base.copy()
    tr = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(tr)   # own layer: ImageDraw doesn't blend on RGBA
    flat = t >= T_FLAT
    col = (239, 68, 68) if flat else (52, 211, 153)
    # trace: x in [24, pw-24]; write head moves at 380 px/s, wraps
    x0, x1 = 24, pw - 24; L = x1 - x0; v = 420.0
    head = ((t - T_TYPE + .25) * v) % L
    pts = []
    beats = [b - .03 for b in EKG_BEATS]                 # R peak (q = .03) on each beep of the flatline cue
    for i in range(0, int(L), 3):
        # time at which pixel i was written (latest pass)
        dt = (head - i) / v
        if dt < 0: dt += L / v
        tw = t - dt
        y = ph * .7
        if tw < T_FLAT:
            for b in beats:
                q = tw - b
                if -.02 < q < .12:
                    y += (-8 * math.exp(-((q + .005) / .012) ** 2) - 54 * math.exp(-((q - .03) / .009) ** 2)
                          + 26 * math.exp(-((q - .05) / .01) ** 2) - 10 * math.exp(-((q - .1) / .02) ** 2))
        fade_ = 1 - clamp(dt / (L / v))
        pts.append((x0 + i, y, fade_, tw))
    for a, b in zip(pts[:-1], pts[1:]):
        if abs(a[0] - b[0]) > 6 or abs(a[3] - b[3]) > .3: continue        # (no segment across the write head)
        if 0 < (a[0] - x0 - head) % L < 30: continue                       # sweep monitor: erase gap ahead of the head
        c = (239, 68, 68) if a[3] >= T_FLAT else (52, 211, 153)            # only what was written after "alma" is red
        al = int(255 * (.25 + .75 * a[2]))
        if flat and a[3] < T_FLAT: al = int(al * (1 - .6 * clamp((t - T_FLAT) / .3)))   # the old life fades away
        d.line((a[0], a[1], b[0], b[1]), fill=c + (al,), width=4)
    hx = x0 + head
    d.ellipse((hx - 7, ph * .7 - 7 if flat else pts[min(len(pts) - 1, int(head / 3))][1] - 7, hx + 7, (ph * .7 if flat else pts[min(len(pts) - 1, int(head / 3))][1]) + 7), fill=col + (255,))
    im.alpha_composite(tr.filter(ImageFilter.GaussianBlur(3)))                      # phosphor glow
    im.alpha_composite(tr)
    lab = K.rich('ALMA', K.inter(30, 'Bold'), col)
    im.alpha_composite(lab, (22, 14))
    hs = K.silhouette('❤', 28, col); beat = 1 + (.3 * math.exp(-(t - max([b for b in EKG_BEATS if b <= t] or [-9])) / .06) if not flat else 0)
    im.alpha_composite(K.scaled(hs, beat), (26 + lab.width + 6, 18))
    if flat:
        k = clamp((t - T_FLAT) / .1)
        ss = K.rich('SEM SINAL', K.inter(30, 'ExtraBold'), (239, 68, 68))
        if (t - T_FLAT) % .5 < .32: im.alpha_composite(ss, (pw - ss.width - 22, 14))
    return im

def _ekg_base(pw, ph):
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), 22, fill=(10, 16, 26, 255))
    for x in range(20, pw, 30): d.line((x, 8, x, ph - 8), fill=(22, 40, 44, 255), width=1)
    for y in range(15, ph, 30): d.line((8, y, pw - 8, y), fill=(22, 40, 44, 255), width=1)
    return im

def text_card(ctx, t, cam):
    if t < T_FLICK + .04 or t > T_WHIP + .1: return
    u = t - (T_FLICK + .04)
    k = K.back(clamp(u / .2), 1.3)
    cx = lerp(1300, 540, k); cy = 520 + 5 * math.sin(u * 2)
    im = text_base().copy()
    # typing: token bursts (1-3 tokens per frame)
    f, lines, toks = _txt_tokens()
    tt = t - T_TYPE
    n = 0 if tt < 0 else min(len(toks), int(2 + tt * 44))
    body, last = text_body(n)
    im.alpha_composite(body, (36, 136))
    if n < len(toks) or (t - T_TYPE) % .5 < .28:                        # block cursor
        cx_, cy_, ch_ = last
        if n == 0: cx_, cy_, ch_ = 0, 0, 44
        ImageDraw.Draw(im).rectangle((36 + cx_ + 2, 136 + cy_ + 8, 36 + cx_ + 17, 136 + cy_ + 48), fill=(124, 58, 237, 255))
    ek = ekg_panel(t)
    im.alpha_composite(ek, (36, TH_ - ek.height - 34))
    if t >= T_FLAT:                                                       # soulless: the card greys out
        g = clamp((t - T_FLAT) / .25) * .7
        im = Image.merge('RGBA', (*K.grade(im.convert('RGB'), sat=1 - g, bright=1 - .08 * g).split(), im.getchannel('A')))
        im.alpha_composite(ek, (36, TH_ - ek.height - 34))                 # the red flat line stays red
    ex = clamp((t - (T_WHIP - .1)) / .14)
    s = 1 - .1 * ex
    rz = 0.0
    img, ox, oy = K.card3d(im, cx, cy - 300 * K.ei(ex, 2), s, 0, -14 * (1 - k), rz)
    sh = shadow_for(img)
    ctx.add('front', sh, ox - 40, oy - 10, center=False, alpha=.8)
    ctx.add('front', img, ox, oy, center=False)

# =========================================================================================== phones (vídeo… todos os outros)
PW_ = 560
def reel_ui():
    """static generic reel chrome (RGBA, 520x1066 screen)."""
    def mk():
        w, h = 520, 1066
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        g = np.linspace(0, .62, 300, dtype=np.float32)[:, None]
        bot = Image.new('RGBA', (w, 300), (0, 0, 0, 0)); bot.putalpha(Image.fromarray((np.repeat(g, w, 1) * 255).astype(np.uint8)))
        im.alpha_composite(bot, (0, h - 300))
        t_ = K.rich('ISSO VAI', K.ffont(K.ANTON, 74), (255, 255, 255), stroke=4)
        t2 = K.rich('MUDAR TUDO 🤯', K.ffont(K.ANTON, 74), (255, 255, 255), stroke=4, esize=70)
        im.alpha_composite(t_, ((w - t_.width) // 2, 170)); im.alpha_composite(t2, ((w - t2.width) // 2, 252))
        for i, (ch, lab) in enumerate((('❤', 'curtir'), ('💬', ''), ('➤', ''))):
            y = 560 + i * 110
            if ch == '➤':
                d.polygon([(w - 70, y), (w - 30, y + 18), (w - 70, y + 36), (w - 62, y + 18)], fill=(255, 255, 255, 240))
            else:
                s = K.silhouette(ch, 46); im.alpha_composite(s, (w - 50 - s.width // 2, y))
        d.ellipse((24, h - 196, 72, h - 148), fill=(168, 85, 247, 255))
        im.alpha_composite(K.rich('@ia.viral', K.inter(28, 'Bold'), (255, 255, 255)), (84, h - 192))
        d.rounded_rectangle((232, h - 194, 320, h - 152), 10, outline=(255, 255, 255, 230), width=2)
        d.text((246, h - 188), 'Seguir', font=K.inter(22, 'SemiBold'), fill=(255, 255, 255, 255))
        im.alpha_composite(K.rich('a IA faz tudo por você ✨ #ia #viral', K.inter(25, 'Regular'), (240, 240, 245), esize=26), (26, h - 132))
        d.rectangle((0, h - 8, w, h), fill=(255, 255, 255, 70))
        return im
    return E.cached('A1_reelui', mk)

def reel_frame(t):
    """the generic AI reel at timeline t (same for every phone = perfect sync): ken-burns planet, hard cut to the brain."""
    w, h = 520, 1066
    if t < STAGES[2][0]:
        u = clamp((t - T_PH) / (STAGES[2][0] - T_PH)); src = E.asset('ai_planet'); z = 1.0 + .16 * u; fx, fy = .45 + .1 * u, .4
    else:
        u = clamp((t - STAGES[2][0]) / 1.2); src = E.asset('ai_brain'); z = 1.12 + .14 * u; fx, fy = .5, .35 + .1 * u
    sc = max(w / src.width, h / src.height) * z
    vw, vh = w / sc, h / sc; x0 = (src.width - vw) * fx; y0 = (src.height - vh) * fy
    im = src.transform((w, h), Image.AFFINE, (1 / sc, 0, x0, 0, 1 / sc, y0), Image.BILINEAR).convert('RGBA')
    im.alpha_composite(reel_ui())
    pr = ImageDraw.Draw(im); pr.rectangle((0, h - 8, int(w * clamp((t - T_PH) / 2.1)), h), fill=(255, 255, 255, 230))
    return im

def phone_img(t):
    return E.phone(reel_frame(t).convert('RGB'), PW_)

def _layout_stage(n):
    """[(x, y, w)] for 25 phone slots at stage n (unborn phones sit behind the centre one)."""
    if n == 1: P = [(540, 860, 560)]
    elif n == 3: P = [(540, 880, 330), (175, 880, 330), (905, 880, 330)]
    elif n == 9:
        P = [(540, 900, 288)] + [(540 + dx * 335, 900 + dy * 640, 288) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx, dy) != (0, 0)]
        P = [P[0], P[4], P[5]] + [p for i, p in enumerate(P) if i not in (0, 4, 5)]
    else:
        P = [(540, 960, 192)]
        ring = [(540 + dx * 212, 960 + dy * 426, 192) for dy in (-2, -1, 0, 1, 2) for dx in (-2, -1, 0, 1, 2) if (dx, dy) != (0, 0)]
        ring.sort(key=lambda p: (abs(p[0] - 540) / 212 + abs(p[1] - 960) / 426, p[1], p[0]))
        P = P + [ring[2], ring[1]] + ring[:1] + ring[3:]  # keep the 3-row neighbours first
    while len(P) < 25: P.append((P[0][0], P[0][1], P[0][2] * .9))
    return P

def phones(ctx, t):
    """full-frame: identical reels multiply 1 -> 3 -> 9 -> 25 (clones slide out from behind the centre one)."""
    si = max(i for i, (ts, n) in enumerate(STAGES) if t >= ts - .001)
    ts, n = STAGES[si]
    prev = STAGES[si - 1][1] if si else 1
    k = 1 - (1 - clamp((t - ts) / .2)) ** 4 if si else 1.0
    A, B = _layout_stage(prev), _layout_stage(n)
    # backdrop: the slop wall, defocused + dim, slow pull-back
    bz = lerp(1.25, 1.0, clamp((t - T_PH) / 1.9))
    bg = K.wall_view(K.Cam(bz, 540, 1010), backdrop=True).convert('RGBA')
    sm = phone_img(t)
    cache = {}
    order = list(range(25))[::-1]
    for i in order:
        if i >= n: continue
        ax, ay, aw = A[i] if i < prev else (A[0][0], A[0][1], A[0][2] * .92)
        bx, by, bw = B[i]
        x, y, w = lerp(ax, bx, k), lerp(ay, by, k), lerp(aw, bw, k)
        a = 1.0 if i < prev else clamp(k * 3)
        if si == 0: w *= .7 + .3 * K.back(clamp((t - ts) / .18), 1.8); a = clamp((t - ts + .01) / .04)
        key = int(w)
        if key not in cache:
            ph = sm.resize((key, int(sm.height * key / sm.width)), Image.BILINEAR)
            cache[key] = ph
        ph = cache[key]
        shd = E.cached(('A1_phsh', key), lambda key=key, ph=ph: shadow_for(ph))
        bg.alpha_composite(K.scaled(shd, 1.0) if a >= .99 else E.fade(shd, a), (int(x - shd.width / 2 + 6), int(y - shd.height / 2 + 14)))
        bg.alpha_composite(ph if a >= .99 else E.fade(ph, a), (int(x - ph.width / 2), int(y - ph.height / 2)))
    # perfect sync gag: every reel gets the same ❤ at the same instant
    hb = Wd['OUTROS'] + .26
    if t >= hb and n == 25:
        u = t - hb
        if u < .45:
            sz = 74; hs = E.cached('A1_synch', lambda: K.soft_shadow(K.silhouette('❤', sz, (255, 255, 255)), 6, .45, (0, 3)))
            s_ = .4 + .6 * K.back(u / .14, 2.6); a = 1 - clamp((u - .3) / .15)
            im = K.scaled(hs, s_)
            for (x, y, w) in _layout_stage(25):
                bg.alpha_composite(im if a >= .99 else E.fade(im, a), (int(x - im.width / 2), int(y - 10 - im.height / 2)))
    ctx.full = bg

# =========================================================================================== draw
def draw(ctx, lt, t):
    if t >= K.CUT3 - 1e-6:                              # seg 3's pose already shows on this frame -> s02's shot
        from sections import s02_virada as S2
        return S2.draw(ctx, t - S2.START, t)
    ctx.cam.update(z=1.0, x=540, y=960, dx=0, dy=0, rot=0)
    P = ctx.post; P['vignette'] = .28
    wraps = []
    if t < T_PH:
        _world(ctx, t, P, wraps)
    else:
        phones(ctx, t)
        u = t - T_PH
        if u < .11:                                      # arriving from the whip: smear + travel decay
            k = (1 - u / .11) ** 1.6; wraps.append(lambda fr, k=k: K.vwhip(fr, 320 * k, -170 * k))
        wraps.append(lambda fr: K.cold(fr, .55))
    pages = _pages()
    special = {'GENÉRICO,': lambda *a: True}
    stamp(ctx, t)                                        # under the caption: the 2 anticipation frames never cover a word
    K.captions(ctx, t, pages, cap_y(t), special=special)
    ctx.wrap = K.compose_wraps(*wraps)

def _world(ctx, t, P, wraps):
    cam = shot_cam(t)
    sc = scroll_at(t); wc = cam.wall()
    bg = K.wall_view(wc, sc)
    v = scroll_speed(t)
    if v > 60: bg = K.vblur(bg, v / 30 * .5 * wc.Z * K.WALL_S0)
    ctx.bg_img = bg
    cam.place_avatar(ctx)
    wall_life(ctx, t, wc, sc)
    notifications(ctx, t)
    concorda(ctx, t, cam)
    stock(ctx, t, cam)
    text_card(ctx, t, cam)
    # ---- opening: lights up + zoom blur + RGB settle
    fi = int(round(t * E.FPS))
    if fi < 2: P['bright'] = [.95, 1.0][fi]
    # frame 0 is the cover / scroll-stopper: crisp (no blur, no RGB split); the pull-back's motion blur starts on frame 1
    if .5 > t and fi >= 1:                               # zoom blur follows the pull-back's speed (world only)
        z0, z1 = shot_cam(max(0, t - 1 / 60)).Z, shot_cam(t + 1 / 60).Z
        zb = min(.7, abs(z1 - z0) * 30 / max(z0, 1) * .42)
        if zb > .04: wraps.append(lambda fr, zb=zb: K.zblur(fr, zb))
    P['rgb'] = 0.0 if fi == 0 else max(0.0, 6 * (1 - t / .3))
    # ---- grade: cold flat generic look; after the stamp everything drains
    dr = clamp((t - T_STAMP) / .07) * (1 - clamp((t - T_LIFT) / .12))
    wraps.append(lambda fr: K.cold(fr, 1.0))
    if dr > .01: wraps.append(lambda fr, dr=dr: K.drained(fr, dr * .92))
    if T_STAMP <= t < T_STAMP + .2:                      # slam: red ink-light from the edges + contrast punch (no wash-out)
        k = (1 - (t - T_STAMP) / .2) ** 1.6; wraps.append(lambda fr, k=k: red_hit(fr, k))
    if Wd['NE'] <= t < Wd['NE'] + .12: wraps.append(lambda fr, k=.45 * (1 - (t - Wd['NE']) / .12): K.zblur(fr, k))
    # ---- whip up into the phones
    if t >= T_WHIP:
        u = clamp((t - T_WHIP) / (T_PH - T_WHIP)); amt = 30 + 330 * u ** 1.5
        wraps.append(lambda fr, amt=amt, u=u: K.vwhip(fr, amt, 300 * u ** 2))
