"""s05 — RETENÇÃO (16.68–28.32).  "você assistiu até aqui porque a casa tava sendo construída na sua frente. / É isso que
uma boa edição faz: dá um motivo pro seu olho ficar. / Cada frase, uma imagem. Cada palavra, um movimento."
Onsets measured on src/tight16k.raw: see _c_kit (O_*).

SHOT A (16.70, after s04's freeze + flash) — PLAY.  A ▶ chip pops where s04's ⏸ was and colour floods back out of it
     (radial wipe); time resumes, the camera drifts round the finished house.  "ASSISTIU" (16.93): the Reel's own progress
     bar draws across the frame and fills — "ATÉ AQUI" — the playhead lands on 0:17 ON "-QUI" (17.85), the real time of
     the film (punch + ring + time bubble).  "PORQUE" (18.335): a scrub-preview card pops above the playhead (the live
     house racks out of focus) and the playhead is dragged BACK (◀◀ rewind): the miniature un-builds and lands on the
     glowing light-line trace exactly ON "CASA" (18.72) — the frame where the house first appeared.  "TAVA SENDO
     CONSTRUÍDA" (19.07 → 19.97): ▶▶ timelapse — the build replays (slab, walls row by row, roof, windows, door, each
     with its own tiny sound, chapter dots lighting on the bar) and catches up with the present ON "-Í-" (19.97).
     "NA SUA FRENTE" (20.27 → 20.585): the card rushes at the lens (opaque, centred, fills the frame and whites out
     in a light dip), and on the switch frame (20.567) the real house is revealed sharp and pushed in, landing ON
     "FREN-" (no double exposure).
SHOT B (21.00 jump, punch-in on him: s 1.08) — a glass "Retenção" insights card rises on "É"; the grid draws on "ISSO"; from "QUE" the COM EDIÇÃO
     line (brand gradient) draws across and stays high, 91 % chip ON "FAZ".
SHOT C (22.867 jump, pull-back to s 1, card lifted) — "DÁ UM MOTIVO": the dotted SEM EDIÇÃO line starts at 100 % and falls off the cliff
     ON "-TI-" (23.36), flattening at 8 %; "OLHO" (24.04): an eye opens at the head of the high line; "FICAR"
     (-CAR 24.425): a lock reticle snaps onto it (ring + glow + camera kick).
SHOT D/E (24.70 / 26.40 jumps) — the edit demonstrates its own rule at max tempo: a cut + a different micro-visual on
     every word, and every word IS the caption: CADA slams in behind his head · FRASE, an empty image card (placeholder)
     snaps in with the word in its caption strip · UMA it loads (AF brackets hunt) · IMAGEM. shutter — the photo snaps in
     and takes over the background · CADA (hollow outline type) · PALAVRA, typed letter by letter · UM · MOVIMENTO. a
     light beam shoots in, the word whips in along it and lands ON "-MEN-" (27.77).  Underneath, an edit-timeline HUD
     (his real waveform, a playhead, a razor cut + a new clip block placed on every word).
The last frame (28.30) already shows seg 15's pose, so it is drawn by s06 (its first framing).
Captions (A-C) sit at y 1605 and every framing keeps his beard bottom above ~1541 (take chin row <= ~1141), so no text
ever covers his face; every jump cut is a framing change on him (A s1 -> B s1.08 -> C s1 -> D/E cuts).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS
from sections import _c_kit as K

START, END = E.span(10, 14)                   # 16.68 – 28.32
W, H = E.W, E.H
clamp, lerp, expo, eo, sio, smooth = E.clamp, K.lerp, K.expo, K.eo, K.sio, K.smooth

# ================================================================================================ SHOT A timing
T_A = START + 1 / 60                          # first frame 16.70
R0 = K.O_PORQUE + .03                  # rewind starts (card already popping)
SRC_TRACE = 6.86                              # rewind lands on the light-line trace (the kit's CASA, 6.40 + .46)
FF_SRC = [SRC_TRACE, 7.45, 9.45, 10.32, 11.02, 11.42, 12.36, 13.86, K.O_IDA]
_n = len(FF_SRC) - 1
FF_OUT = [K.O_TAVA + (K.O_IDA - K.O_TAVA) * i / _n for i in range(_n + 1)]

def ff_src(t):
    """timelapse mapping (output t -> source t): every build stage gets the same screen time."""
    for i in range(_n):
        if t <= FF_OUT[i + 1]:
            u = (t - FF_OUT[i]) / (FF_OUT[i + 1] - FF_OUT[i]); return lerp(FF_SRC[i], FF_SRC[i + 1], u)
    return t

def ff_out(s):
    """inverse of ff_src (source t -> output t), for the replayed build sounds."""
    for i in range(_n):
        if FF_SRC[i] <= s <= FF_SRC[i + 1]:
            return lerp(FF_OUT[i], FF_OUT[i + 1], (s - FF_SRC[i]) / (FF_SRC[i + 1] - FF_SRC[i]))
    return None

def playhead(t):
    """film time shown by the scrubber + miniature (s)."""
    if t < K.O_ASSISTIU: return 0.0
    if t < K.O_QUI: return K.O_QUI * eo((t - K.O_ASSISTIU) / (K.O_QUI - K.O_ASSISTIU), 2.3)
    if t < R0: return t
    if t < K.O_CASA:                                          # rewind: smooth start, lands at speed ON "CASA"
        u = clamp((t - R0) / (K.O_CASA - R0)); return lerp(R0, SRC_TRACE, u * u * (2 - u))
    if t < K.O_TAVA: return SRC_TRACE
    if t < K.O_IDA: return ff_src(t)
    return t

def mode(t):
    if t < R0: return 'play'
    if t < K.O_CASA: return 'rew'
    if t < K.O_TAVA: return 'pause'
    if t < K.O_IDA: return 'ff'
    return 'play'

CUES = [
    (T_A, 'click', {'gain': 6}),                              # PLAY (s04's freeze ends)
    (T_A + .02, 'swoosh_up', {'gain': -12}),                  # colour floods back
    (K.O_ASSISTIU, 'swipe', {'gain': -14}),                   # progress bar draws on
    (K.O_QUI, 'pop', {'gain': -6}),                           # playhead lands on 0:17 ON "-QUI"
    (K.O_QUI, 'tick', {'gain': -8}),
    (K.O_PORQUE, 'swipe', {'gain': -10}),                     # preview card pops
    (R0, 'rewind', {'dur': K.O_CASA - R0 + .06, 'gain': -2}), # ◀◀
    (K.O_CASA, 'shimmer', {'gain': -9}),                      # lands on the light-line trace ON "CASA"
    (K.O_CASA, 'tick', {'gain': -6}),
    (K.O_TAVA, 'click', {'gain': -4}),                        # ▶▶
    (K.O_IDA, 'shimmer', {'gain': -10}),                      # caught up with the present ON "-Í-"
    (K.O_SUA - .03, 'riser', {'to': round(K.O_FREN - 1 / 30, 3), 'gain': -16}),   # the card rushes at the lens ...
    (K.O_FREN - .03, 'whoosh', {'gain': -7}),                 # ... and hits it (light flash, the real house)
    (K.O_FREN, 'impact', {'gain': -12}),
] + [(round(ff_out(s), 3), k, dict(p)) for s, k, p in (     # the build replays with its own sounds (timelapse)
    (HS.W_ALICERCE + .03, 'stone', {'gain': -12}),
    (HS.W_PAREDES, 'block', {'seed': 6, 'gain': -11}), (HS.W_PAREDES + .26, 'block', {'seed': 7, 'gain': -12}),
    (HS.W_PAREDES + .52, 'block', {'seed': 8, 'gain': -13}),
    (HS.ROOF_LAND, 'thud', {'gain': -11}),
    (HS.W_JANELAS, 'switch', {'gain': -10, 'pan': -.3}), (12.02, 'switch', {'gain': -12, 'pan': .4}),
    (HS.W_PORTA, 'door', {'gain': -12}))]
CUES += [
    (K.J11 + .05, 'swipe', {'gain': -10}),                    # retention card rises on "É"
    (K.O_ISSO, 'tick', {'gain': -12}),                        # grid
    (K.O_QUE, 'riser', {'to': K.O_FAZ, 'gain': -10}),         # COM EDIÇÃO line draws (stays high)
    (K.O_FAZ, 'pop', {'gain': -7}),                           # 91 %
    (K.J12, 'whoosh', {'gain': -14}),                         # punch-in
    (K.O_DA, 'tick', {'gain': -12}),                          # SEM EDIÇÃO starts
    (K.O_TI - .04, 'whoosh', {'gain': -6}),                   # ...and falls off the cliff ON "-TI-"
    (K.O_TI + .02, 'glitch', {'gain': -18}),
    (23.98, 'pop', {'gain': -14}),                            # 8 %
    (K.O_OLHO, 'shimmer', {'gain': -14}),                     # the eye opens
    (K.O_CAR, 'click', {'gain': 4}), (K.O_CAR, 'impact', {'gain': -12}),   # lock ON "-CAR"
    (K.O_CADA13 - .02, 'impact', {'gain': -6}),               # CADA slams (lands on its k-burst)
    (K.O_FRASE, 'swipe', {'gain': -6}),                       # image card flies in
    (K.O_UMA13, 'tick', {'gain': -10}),                       # it loads
    (K.O_IMAGEM, 'shutter', {'gain': 4}), (K.O_IMAGEM + .01, 'pop', {'gain': -10}),
    (K.O_CADA14 - .02, 'impact', {'gain': -8}),               # CADA (outline) lands
] + [(round(K.O_PALAVRA + i * .034, 3), 'type', {'i': i, 'gain': 2}) for i in range(8)] + [
    (K.O_UM14, 'pop', {'gain': -14}),
    (K.O_MOVIMENTO, 'riser', {'to': K.O_MEN, 'gain': -18}),   # the light beam shoots in (anticipation)
    (K.O_MEN - .02, 'whoosh', {'gain': -2}),                  # MOVIMENTO whips in on its streak
    (K.O_MEN, 'impact', {'gain': -8}),
]

# ================================================================================================ SHOT A
HSIZE = (1080, 1400); HFADE = (1110, 1340)
def sy(y, h=HSIZE[1]): return (y - h / 2) / h
AV_A = dict(show=True, s=1.0, x=0., y=400., alpha=1.0, copies=[], bright=1.0)     # chin <= 1541: captions clear his face
CA0 = dict(yaw=-37.0, pitch=15.5, dist=28.5, fov=30, target=(0.0, 2.0, 0.0), shift=(0, sy(530)))
CA1 = dict(yaw=-22.0, pitch=12.5, dist=23.5, fov=30, target=(0.0, 2.1, 0.3), shift=(0, sy(515)))
T_PUSH0, T_PUSH1 = K.O_SUA - .03, K.O_FREN               # "NA SUA FRENTE": the card rushes at the lens
def cam_a(t):
    c = K.cam_mix(CA0, CA1, eo((t - T_A) / (K.J11 - T_A), 1.8))
    if t > T_PUSH0:                                           # the real house comes forward as the card hits the lens
        k = K.eio3((t - T_PUSH0) / (T_PUSH1 - T_PUSH0 + .12))
        c['dist'] *= 1 - .20 * k - .015 * K.kick(t, T_PUSH1, 1.0, .3); c['pitch'] -= 2.5 * k
    return c

T_SW = T_PUSH1 - 1 / 30                     # the card has filled the frame and whited out: switch to the real house
def focus_a(t):
    """0 = live house sharp, 1 = racked out of focus (preview card up).  The card rushes at the lens and fills the
    frame (opaque, whiting out); the real house is revealed sharp on the switch frame (no double exposure)."""
    if t >= T_SW: return 0.0
    return smooth((t - (K.O_PORQUE - .02)) / .22)

def live_house(t, f):
    st = HS.state_at(t); cam = cam_a(t)
    if f < .02: return K.House(st, cam, HSIZE, fade=HFADE, t=t).img
    lr = 2 if f > .5 else 1
    im = K.House(st, cam, HSIZE, fade=HFADE, t=t, lowres=lr).img
    im = im.filter(ImageFilter.GaussianBlur(7.5 * f))
    return K.desat(im, 1 - .25 * f, mul=1 - .38 * f)

# ---------------------------------------------------------------------------------------- scrubber
BX0, BX1, BY = 110, 970, 892                  # just above his head (head top >= 944 in seg 10)
CHAPTERS = [HS.W_ALICERCE, HS.W_PAREDES, HS.W_JANELAS, HS.W_PORTA]
def bx(ph): return BX0 + (BX1 - BX0) * clamp(ph / E.DUR)

def scrub_img(t, ph, draw_k, alpha):
    """progress bar art (world-frame RGBA crop): track, watched fill, chapter gaps, knob (+ landing pulse)."""
    S = 2; x0, y0 = BX0 - 60, BY - 60; w, h = BX1 - BX0 + 120, 120
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def X(x): return (x - x0) * S
    cy = (BY - y0) * S; th = 5 * S
    xe = BX0 + (BX1 - BX0) * draw_k
    if xe > BX0 + 2:
        sh = Image.new('L', im.size); ImageDraw.Draw(sh).rounded_rectangle((X(BX0) - 4 * S, cy - th - 4 * S, X(xe) + 4 * S, cy + th + 6 * S), th + 4 * S, fill=150)
        shi = Image.new('RGBA', im.size, (6, 4, 14, 0)); shi.putalpha(sh.filter(ImageFilter.GaussianBlur(6 * S))); im.alpha_composite(shi)
        d.rounded_rectangle((X(BX0), cy - th, X(xe), cy + th), th, fill=(255, 255, 255, 96))
    kx = min(bx(ph), xe)
    if kx > BX0 + 1:
        g = E.gradient(int(X(kx) - X(BX0)) + 1, 2 * th + 1, E.GRAD).convert('RGBA')
        m = Image.new('L', g.size); ImageDraw.Draw(m).rounded_rectangle((0, 0, g.width - 1, g.height - 1), th, fill=255); g.putalpha(m)
        im.alpha_composite(g, (int(X(BX0)), int(cy - th)))
    for i, c in enumerate(CHAPTERS):                          # chapter gaps (YouTube-style) + lit dots once replayed
        cx = X(bx(c))
        if cx > X(xe): continue
        d.rectangle((cx - 2 * S, cy - th - 2, cx + 2 * S, cy + th + 2), fill=(0, 0, 0, 0))
    out = im.resize((w, h), Image.LANCZOS)
    if alpha < 1: out = E.fade(out, alpha)
    return out, x0, y0

def knob_img(r=17, glow=1.0):
    def mk():
        R = r * 4; S = 3; im = Image.new('RGBA', (2 * R * S, 2 * R * S), (0, 0, 0, 0))
        g = Image.new('L', im.size); ImageDraw.Draw(g).ellipse((R * S - r * 2.2 * S, R * S - r * 2.2 * S, R * S + r * 2.2 * S, R * S + r * 2.2 * S), fill=255)
        gl = Image.new('RGBA', im.size, (150, 100, 255, 0)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(r * 1.3 * S)).point(lambda v: int(v * .9)))
        im.alpha_composite(gl); d = ImageDraw.Draw(im)
        d.ellipse((R * S - r * S, R * S - r * S, R * S + r * S, R * S + r * S), fill=(250, 249, 246, 255))
        return im.resize((2 * R, 2 * R), Image.LANCZOS)
    return K.C(('knob', r), mk)

def bubble(txt, size=44):
    """frosted time bubble with a little pointer (RGBA; pointer tip at the bottom centre)."""
    def mk():
        f = E.font(size, 800); l, t_, r, b = f.getbbox(txt); tw, th = r - l, b - t_
        w, h = tw + 44, th + 30; G = 40; ptr = 14
        out = Image.new('RGBA', (w + 2 * G, h + ptr + 2 * G), (0, 0, 0, 0))
        out.alpha_composite(K.soft_shadow(w, h, h // 2, 16, .45, G), (0, 6))
        out.alpha_composite(E.glass_panel(w, h, radius=h // 2, alpha=.20, border=.6), (G, G))
        d = ImageDraw.Draw(out)
        d.polygon([(G + w / 2 - ptr, G + h - 1), (G + w / 2 + ptr, G + h - 1), (G + w / 2, G + h + ptr)], fill=(255, 255, 255, 60))
        d.text((G + 22 - l, G + 15 - t_), txt, font=f, fill=(250, 249, 246, 255))
        return out
    return K.C(('bubble', txt, size), mk)

def draw_scrubber(ctx, t, alpha):
    if t < K.O_ASSISTIU - .02 or alpha <= .01: return
    ph = playhead(t)
    dk = expo((t - K.O_ASSISTIU + .02) / .34)
    im, x0, y0 = scrub_img(t, ph, dk, alpha)
    ctx.add('behind', im, x0, y0, center=False)
    for i, c in enumerate(CHAPTERS):                          # chapter dots light as the timelapse passes them
        to = ff_out(c + .02)
        if to is None or t < to: continue
        lt = t - to
        ctx.add('behind', K.glow_spot(26, (170, 120, 255), alpha * (.35 + .65 * math.exp(-lt / .25))), bx(c), BY)
        if lt < .4: ctx.add('behind', K.ring(30, lt / .4, width=4), bx(c), BY, alpha=alpha)
    kx = bx(ph); kp = K.kick(t, K.O_QUI, .55, .26) + K.kick(t, K.O_CASA, .4, .24)
    ctx.add('behind', K.scaled(knob_img(), 1 + kp), kx, BY, alpha=alpha * clamp((t - K.O_ASSISTIU) / .1))
    for t0 in (K.O_QUI, K.O_CASA):
        if t0 <= t < t0 + .45: ctx.add('behind', K.ring(46, (t - t0) / .45), kx, BY, alpha=alpha)
    # time bubble: pops ON "-QUI" (0:17), hands over to the card's timecode on PORQUE
    if K.O_QUI - .01 <= t < K.O_PORQUE + .10:
        lt = t - K.O_QUI + .02; s = .55 + .45 * E.back(lt / .22, 2.0)
        a = clamp(lt / .05) * (1 - clamp((t - K.O_PORQUE) / .10)) * alpha
        b = bubble(K.mmss(ph))
        ctx.add('behind', K.scaled(b, s), kx, BY - 30 - (b.height - 80) * s / 2 - 10, alpha=a)

# ---------------------------------------------------------------------------------------- preview card (miniature)
CW, CHh = 600, 600                            # card
MW, MH = 600, 900                             # reference framing of the miniature (the card shows its bottom CHh rows)
MCAM0 = dict(yaw=33.0, pitch=24.0, dist=35.0, fov=30, target=(0.0, 1.5, -0.4), shift=(0, sy(MH - CHh / 2 + 22, MH)))
MCAM1 = dict(yaw=16.0, pitch=5.0, dist=13.5, fov=30, target=(0.0, 2.7, 1.2), shift=(0, sy(MH - CHh * .42, MH)))

def mini_render(st, t, ph):
    """the card's miniature (CW x CHh): the bottom CHh rows of the MW x MH framing, rendered directly at CW x CHh
    (same projection: fov narrowed for the smaller height, centre moved up by the cropped rows) — 1/3 fewer pixels."""
    c = dict(mini_cam(t)); top = MH - CHh
    c['fov'] = 2 * math.degrees(math.atan(math.tan(math.radians(c['fov']) / 2) * CHh / MH))
    sx_, sy_ = c.get('shift', (0, 0)); cy = MH / 2 + sy_ * MH - top
    c['shift'] = (sx_, (cy - CHh / 2) / CHh)
    return HS.render(st, c, size=(CW, CHh), t=ph, ss=2)

def mini_cam(t):
    k = K.eio3((t - T_PUSH0) / (T_PUSH1 - T_PUSH0)) * .25
    c = K.cam_mix(MCAM0, MCAM1, k)
    c['yaw'] += 4.0 * math.sin(t * .9)
    return c

def card_bg():
    def mk():
        yy, xx = np.mgrid[0:CHh, 0:CW].astype(np.float32)
        r = np.hypot((xx - CW * .5) / CW, (yy - CHh * .52) / CHh)
        c0, c1 = np.array([44, 34, 78], np.float32), np.array([12, 11, 18], np.float32)
        k = np.clip(r / .75, 0, 1)[..., None] ** 1.2
        a = c0 + (c1 - c0) * k
        return Image.fromarray(a.astype(np.uint8)).convert('RGBA')
    return K.C('cardbg', mk)

def card_glass():
    def mk():
        g = E.glass_panel(CW, CHh, radius=34, alpha=.0, border=.55)
        yy = np.linspace(0, 1, CHh, dtype=np.float32)[:, None]
        vig = Image.fromarray((np.clip((yy - .55) / .45, 0, 1) ** 1.5 * 150 * np.ones((1, CW), np.float32)).astype(np.uint8))
        v = Image.new('RGBA', (CW, CHh), (6, 5, 12, 0)); v.putalpha(vig); out = v; out.alpha_composite(g); return out
    return K.C('cardglass', mk)

def chip_img(kind, label=None):
    """small dark glass chip with a transport glyph (+ label)."""
    def mk():
        f = E.font(34, 800); lw = 0
        if label: l, t_, r, b = f.getbbox(label); lw = r - l + 14
        w, h = 74 + lw, 60; out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        m = K.rr_mask(w, h, 30); body = Image.new('RGBA', (w, h), (10, 9, 18, 170)); body.putalpha(m.point(lambda v: int(v * .70)))
        out.alpha_composite(body)
        if kind == 'pause':
            d = ImageDraw.Draw(out); d.rounded_rectangle((25, 17, 33, 43), 2, fill=WHITE + (255,)); d.rounded_rectangle((41, 17, 49, 43), 2, fill=WHITE + (255,))
        else:
            gi = K.glyph_img(kind, 30); out.alpha_composite(gi, (37 - gi.width // 2, 30 - gi.height // 2))
        if label: ImageDraw.Draw(out).text((70 - l, 30 - (b + t_) / 2), label, font=f, fill=WHITE + (255,))
        return out
    return K.C(('chip', kind, label), mk)
WHITE = K.WHITE

def tc_img(ph):
    txt = K.mmss(ph)
    def mk():
        f = E.font(38, 800); l, t_, r, b = f.getbbox(txt); w, h = r - l + 36, 58
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); m = K.rr_mask(w, h, 29)
        body = Image.new('RGBA', (w, h), (10, 9, 18, 0)); body.putalpha(m.point(lambda v: int(v * .70))); out.alpha_composite(body)
        ImageDraw.Draw(out).text((18 - l, 29 - (b + t_) / 2), txt, font=f, fill=WHITE + (255,)); return out
    return K.C(('tc', txt), mk)

def card_geom(t):
    """card centre x, bottom y, scale, alpha."""
    kx = bx(playhead(t))
    cx = min(max(kx, 84 + CW / 2), 996 - CW / 2)
    lt = t - K.O_PORQUE
    s = .5 + .5 * E.back(lt / .26, 1.6) if lt < .26 else 1.0
    a = clamp(lt / .06)
    by = BY - 44
    if t >= T_SW: return cx, by, s, 0.0
    if t > T_PUSH0:                                           # flies at the lens: grows past the frame edges (opaque)
        u = clamp((t - T_PUSH0) / (T_SW - T_PUSH0)); k = K.ei(u, 2.2)
        s *= 1 + 3.0 * k
        cx = lerp(cx, 540, K.eio3(u)); by = lerp(by, 820 + CHh / 2 * s, K.eio3(u))    # centred: covers the frame
    return cx, by, s, a

def push_u(t):
    """0..1 progress of the card's rush at the lens (0 before / 1 at the switch)."""
    return clamp((t - T_PUSH0) / (T_SW - T_PUSH0)) if t > T_PUSH0 else 0.0

def draw_card(ctx, t):
    if t < K.O_PORQUE - .01: return
    cx, by, s, a = card_geom(t)
    if a <= .01: return
    ph = playhead(t); md = mode(t)
    st = HS.state_at(ph)
    mini = K.house_grade(mini_render(st, t, ph))
    sp = 0.0                                                    # scrub speed -> horizontal smear
    if md in ('rew', 'ff'):
        dp = playhead(t + 1 / 60) - playhead(t - 1 / 60)
        sp = clamp(abs(dp) * 30 / 40, 0, 1)
        if sp > .05: mini = K.mblur_h(mini, (-1 if md == 'rew' else 1) * 26 * sp)
    # card body (canvas = card + shadow margin G; the card's bottom edge sits on `by`)
    G = 70
    out = Image.new('RGBA', (CW + 2 * G, CHh + 2 * G + 10), (0, 0, 0, 0))
    out.alpha_composite(K.soft_shadow(CW, CHh, 34, 26, .65, G), (0, 14))
    body = card_bg().copy(); body.alpha_composite(mini)
    if md == 'rew' or (md == 'ff' and sp > .05):              # scrub tint (cool on rewind, warm-violet on ff)
        tint = Image.new('RGBA', (CW, CHh), ((70, 120, 255) if md == 'rew' else (160, 110, 255)) + (int(34 * sp),))
        body.alpha_composite(tint)
    body.alpha_composite(card_glass())
    fl = math.exp(-(t - K.O_CASA) / .18) if t >= K.O_CASA else 0
    fl += math.exp(-(t - K.O_IDA) / .22) if t >= K.O_IDA else 0
    if fl > .02: body.alpha_composite(Image.new('RGBA', (CW, CHh), (235, 225, 255, int(70 * min(1, fl)))))
    pu = push_u(t)
    wo = smooth((pu - .40) / .60)                              # rushing at the lens: the card whites out (light hits it)
    if wo > .01: body.alpha_composite(Image.new('RGBA', (CW, CHh), (246, 242, 255, int(190 * wo))))
    body.putalpha(ImageChops.multiply(body.getchannel('A'), K.rr_mask(CW, CHh, 34)))
    out.alpha_composite(body, (G, G))
    # chips: transport glyph (top-left), timecode (bottom-right) — they fade as the card rushes at the lens
    cf = (1.0 if md != 'pause' else (.55 + .45 * math.cos((t - K.O_CASA) * 14))) * (1 - smooth(pu / .35))
    if cf > .01:
        chip = chip_img(md, None); out.alpha_composite(E.fade(chip, cf) if cf < 1 else chip, (G + 18, G + 18))
        tc = tc_img(ph); tf = 1 - smooth(pu / .35)
        out.alpha_composite(E.fade(tc, tf) if tf < 1 else tc, (G + CW - tc.width - 18, G + CHh - tc.height - 18))
    # pointer notch to the knob
    kx = bx(ph); d = ImageDraw.Draw(out); px = G + CW / 2 + (kx - cx)
    px = min(max(px, G + 40), G + CW - 40)
    d.polygon([(px - 13, G + CHh - 1), (px + 13, G + CHh - 1), (px, G + CHh + 13)], fill=(255, 255, 255, 70))
    place_scaled(ctx, 'behind', out, s, cx - out.width * s / 2, by - (G + CHh) * s, a)     # card bottom edge on `by`

def place_scaled(ctx, layer, img, s, x0, y0, alpha=1.0):
    """paste `img` scaled by s with its top-left at (x0, y0), resizing only the part that lands inside the frame
    (the card grows to ~4x as it rushes at the lens)."""
    if s < 1.3: im = K.scaled(img, s); ctx.add(layer, im, x0, y0, center=False, alpha=alpha); return
    sx0, sy0 = max(0.0, -x0 / s), max(0.0, -y0 / s)
    sx1, sy1 = min(img.width, (W - x0) / s), min(img.height, (H - y0) / s)
    if sx1 - sx0 < 1 or sy1 - sy0 < 1: return
    ix0, iy0, ix1, iy1 = int(sx0), int(sy0), min(img.width, int(math.ceil(sx1)) + 1), min(img.height, int(math.ceil(sy1)) + 1)
    cr = img.crop((ix0, iy0, ix1, iy1))
    cr = cr.resize((max(1, int(round((ix1 - ix0) * s))), max(1, int(round((iy1 - iy0) * s)))), Image.BILINEAR)
    ctx.add(layer, cr, x0 + ix0 * s, y0 + iy0 * s, center=False, alpha=alpha)

_DRAIN_LUT = [int(min(255, v * f * .82)) for f in (.94, .98, 1.05) for v in range(256)]
def colour_wipe(fr, t):
    """PLAY: colour floods back out of the ▶ chip (radial), from s04's drained, cool freeze grade (PIL ops)."""
    u = (t - T_A + 1 / 30) / .36
    if u >= 1: return fr
    R = 2300 * eo(u, 2.2)
    D = K.C('dist350', lambda: np.hypot(*np.mgrid[0:H, 0:W].astype(np.float32)[::-1] - np.array([540., 350.])[:, None, None]))
    m = Image.fromarray(np.clip((D - R) * (255 / 140), 0, 255).astype(np.uint8))
    rgb = fr.convert('RGB')
    dr = Image.blend(rgb.convert('L').convert('RGB'), rgb, .36).point(_DRAIN_LUT)
    return Image.composite(dr, rgb, m).convert('RGBA')

def shot_a(ctx, t):
    f = focus_a(t)
    ctx.bg_img = K.studio_bg(.42 + .12 * f, 11.0 + 4 * f)
    ctx.cam = dict(z=1.0 + .02 * K.kick(t, K.O_QUI, 1, .3), x=540., y=900., dx=0., dy=0., rot=0.)
    ctx.avatar = dict(AV_A)
    ctx.add('behind', live_house(t, f), 0, 0, center=False)
    alpha_ui = 1 - smooth((t - T_PUSH0) / .22)
    draw_scrubber(ctx, t, alpha_ui)
    draw_card(ctx, t)
    if t < T_A + .55:                                           # ▶ chip where s04's ⏸ was
        lt = t - T_A + 1 / 30
        s = (.75 + .25 * E.back(lt / .14, 2.4)) * (1 + .7 * eo((lt - .12) / .25))
        a = 1 - clamp((lt - .12) / .22)
        ctx.add('screen', K.scaled(K.play_chip(112, 'play'), s), 540, 350, alpha=a, glass=10 if a > .5 else 0)
        ctx.wrap = lambda fr: colour_wipe(fr, t)
    fl = (t - T_A + 1 / 30) / .14
    if fl < 1: ctx.post['flash'] = .32 * (1 - fl) ** 2
    pu = push_u(t)                                              # light dip: builds as the card fills the frame ...
    if pu > .55 and t < T_SW: ctx.post['flash'] = .42 * smooth((pu - .55) / .45); ctx.post['flash_col'] = (246, 242, 255)
    if t >= T_SW:                                               # ... the card hit the lens -> the real house, in focus
        u = (t - T_SW) / .17
        if u < 1: ctx.post['flash'] = .48 * (1 - u) ** 2; ctx.post['flash_col'] = (246, 242, 255)
    ctx.post['vignette'] = .34 + .10 * f
    K.captions(ctx, t)

# ================================================================================================ SHOT B / C — retention
RCW, RCH = 900, 760
PX0, PX1, PY0, PY1 = 150, 760, 246, 640          # plot box in card px (PY0 = 100 %, PY1 = 0 %)
def com_curve(x): return 100 - 7.6 * x ** .75 - 1.4 * math.sin(7.5 * x) * x
def sem_curve(x): return 8 + 92 * math.exp(-((x / .075) ** 1.12)) + 2.0 * math.sin(11 * x) * x
def P(x, v): return (PX0 + (PX1 - PX0) * x, PY1 - (PY1 - PY0) * v / 100)

def sem_head(t):
    """draw head of the SEM EDIÇÃO line (0..1 along x): creeps along the top, falls off the cliff ON -TI-."""
    if t < K.O_DA: return 0.0
    if t < K.O_TI - .06: return .028 * eo((t - K.O_DA) / (K.O_TI - .06 - K.O_DA), 1.5)
    if t < K.O_TI + .16: return lerp(.028, .30, eo((t - (K.O_TI - .06)) / .22, 1.6))
    return lerp(.30, 1.0, eo((t - (K.O_TI + .16)) / (23.98 - (K.O_TI + .16)), 1.4))

def rcard_static():
    def mk():
        im = Image.new('RGBA', (RCW, RCH), (0, 0, 0, 0))
        im.alpha_composite(E.glass_panel(RCW, RCH, radius=44, alpha=.13, border=.5))
        tint = Image.new('RGBA', (RCW, RCH), (16, 12, 30, 0)); tint.putalpha(K.rr_mask(RCW, RCH, 44).point(lambda v: int(v * .70)))
        im.alpha_composite(tint)
        d = ImageDraw.Draw(im)
        # header: chart glyph + title + "Reels" pill
        g = E.gradient(46, 46, E.GRAD).convert('RGBA'); gm = Image.new('L', (46, 46)); dg = ImageDraw.Draw(gm)
        for i, hh in enumerate((18, 30, 42)): dg.rounded_rectangle((4 + i * 14, 44 - hh, 13 + i * 14, 44), 3, fill=255)
        g.putalpha(gm); im.alpha_composite(g, (52, 44))
        f = E.font(44, 700); d.text((116, 40), 'Retenção', font=f, fill=WHITE + (255,))
        f2 = E.font(34, 600); l, t_, r, b = f2.getbbox('Reels · 0:40'); pw = r - l + 40
        pm = K.rr_mask(pw, 56, 28); pb = Image.new('RGBA', (pw, 56), (255, 255, 255, 0)); pb.putalpha(pm.point(lambda v: int(v * .12)))
        im.alpha_composite(pb, (RCW - 52 - pw, 44)); d.text((RCW - 52 - pw + 20 - l, 72 - (b + t_) / 2), 'Reels · 0:40', font=f2, fill=MUTED + (255,))
        d.line([(52, 128), (RCW - 52, 128)], fill=(255, 255, 255, 40), width=2)
        return im
    return K.C('rcard', mk)
MUTED = K.MUTED

def grid_img(k):
    """gridlines + axis labels, drawn on to k."""
    k = round(k, 2)
    def mk():
        im = Image.new('RGBA', (RCW, RCH), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = E.font(34, 600)
        for v, lab in ((100, '100%'), (50, '50%'), (0, '0%')):
            y = P(0, v)[1]; xe = PX0 + (PX1 - PX0) * k
            x = PX0
            while x < xe:
                d.line([(x, y), (min(x + 12, xe), y)], fill=(255, 255, 255, 55 if v else 80), width=2); x += 22
            l, t_, r, b = f.getbbox(lab); d.text((PX0 - 22 - (r - l) - l, y - (b + t_) / 2), lab, font=f, fill=MUTED + (int(255 * k),))
        for x, lab in ((0, '0:00'), (1, '0:40')):
            l, t_, r, b = f.getbbox(lab); xx = P(x, 0)[0]
            d.text((xx - l if x == 0 else xx - (r - l) - l, PY1 + 30 - t_), lab, font=f, fill=MUTED + (int(255 * k),))
        return im
    return K.C(('grid', k), mk)

def curve_pts(fn, x1, n=90):
    xs = np.linspace(0, x1, max(2, int(n * x1) + 2)); return [P(x, fn(x)) for x in xs]

def com_layer(x1, glow=0.0):
    """COM EDIÇÃO: brand-gradient line (+ soft area fill + glow), drawn to x1."""
    S = 2; im = Image.new('RGBA', (RCW, RCH), (0, 0, 0, 0))
    if x1 <= .002: return im
    pts = curve_pts(com_curve, x1)
    # area under the line
    am = Image.new('L', (RCW * S, RCH * S)); ImageDraw.Draw(am).polygon([(x * S, y * S) for x, y in pts] + [(pts[-1][0] * S, PY1 * S), (PX0 * S, PY1 * S)], fill=255)
    am = am.resize((RCW, RCH), Image.LANCZOS)
    yy = np.linspace(0, 1, RCH, dtype=np.float32)[:, None]
    fade_v = Image.fromarray((np.clip(1.0 - (yy * RCH - PY0) / (PY1 - PY0), 0, 1) ** 2.2 * 92 * np.ones((1, RCW), np.float32)).astype(np.uint8))
    grad = E.gradient(RCW, RCH, E.GRAD_LIGHT).convert('RGBA'); grad.putalpha(ImageChops.multiply(am, fade_v)); im.alpha_composite(grad)
    # glow + line
    lm = Image.new('L', (RCW * S, RCH * S)); ImageDraw.Draw(lm).line([(x * S, y * S) for x, y in pts], fill=255, width=9 * S, joint='curve')
    lm = lm.resize((RCW, RCH), Image.LANCZOS)
    gl = Image.new('RGBA', (RCW, RCH), (130, 100, 255, 0)); gl.putalpha(lm.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(min(255, v * (.85 + .9 * glow)))))
    im.alpha_composite(gl)
    gr = E.gradient(RCW, RCH, E.GRAD_LIGHT if glow > .3 else E.GRAD).convert('RGBA'); gr.putalpha(lm); im.alpha_composite(gr)
    hx, hy = pts[-1]
    im.alpha_composite(K.glow_spot(30, (170, 130, 255), .9), (int(hx - 30), int(hy - 30)))
    ImageDraw.Draw(im).ellipse((hx - 9, hy - 9, hx + 9, hy + 9), fill=WHITE + (255,))
    return im

def sem_layer(x1, t):
    """SEM EDIÇÃO: dotted muted line drawn to x1 (+ falling head)."""
    im = Image.new('RGBA', (RCW, RCH), (0, 0, 0, 0))
    if x1 <= .001: return im
    S = 2; big = Image.new('RGBA', (RCW * S, RCH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    xs = np.linspace(0, x1, 1200); pts = np.array([P(x, sem_curve(x)) for x in xs])
    seg = np.hypot(*np.diff(pts, axis=0).T); L = np.concatenate([[0], np.cumsum(seg)])
    for s_ in np.arange(0, L[-1], 19.0):
        i = min(len(pts) - 1, int(np.searchsorted(L, s_)))
        x, y = pts[i]; d.ellipse(((x - 4.2) * S, (y - 4.2) * S, (x + 4.2) * S, (y + 4.2) * S), fill=(200, 200, 214, 235))
    im = big.resize((RCW, RCH), Image.LANCZOS)
    hx, hy = pts[-1]
    ImageDraw.Draw(im).ellipse((hx - 9, hy - 9, hx + 9, hy + 9), fill=(214, 214, 226, 255), outline=(120, 120, 136, 255), width=2)
    return im

def label_chip(txt, val, grad):
    """line label: name + value (gradient pill for COM, muted glass for SEM)."""
    def mk():
        f, f2 = E.font(34, 700), E.font(40, 800)
        l, t_, r, b = f.getbbox(txt); l2, t2, r2, b2 = f2.getbbox(val)
        w = (r - l) + (r2 - l2) + 22 + 48; h = 64; G = 30
        out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0)); m = K.rr_mask(w, h, 32)
        if grad:
            gl = Image.new('RGBA', out.size, (130, 90, 255, 0)); mm = Image.new('L', out.size); mm.paste(m, (G, G))
            gl.putalpha(mm.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .7))); out.alpha_composite(gl)
            body = E.gradient(w, h, E.GRAD).convert('RGBA'); body.putalpha(m); out.alpha_composite(body, (G, G))
            col, col2 = WHITE, WHITE
        else:
            body = Image.new('RGBA', (w, h), (70, 70, 84, 0)); body.putalpha(m.point(lambda v: int(v * .85))); out.alpha_composite(body, (G, G))
            col, col2 = (214, 214, 226), (240, 240, 246)
        d = ImageDraw.Draw(out)
        d.text((G + 24 - l, G + h / 2 - (b + t_) / 2), txt, font=f, fill=col + (255,))
        d.text((G + 24 + (r - l) + 22 - l2, G + h / 2 - (b2 + t2) / 2), val, font=f2, fill=col2 + (255,))
        return out
    return K.C(('lchip', txt, val, grad), mk)

def eye_img(open_k, look=0.0):
    """line-art eye (white, purple iris glow); open_k 0..1 opens the lids."""
    ok = round(clamp(open_k), 2); lk = round(look, 2)
    def mk():
        S = 3; Z = 1.3; w, h = int(150 * Z), int(100 * Z); im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cx, cy = w / 2 * S, h / 2 * S; hw = 62 * S * Z; hh = 34 * S * Z * max(.06, ok)
        top = [(cx + hw * math.cos(a), cy - hh * math.sin(a)) for a in np.linspace(0, math.pi, 40)]
        bot = [(cx - hw * math.cos(a), cy + hh * math.sin(a)) for a in np.linspace(0, math.pi, 40)]
        m = Image.new('L', im.size); ImageDraw.Draw(m).polygon(top + bot, fill=255)
        inner = Image.new('RGBA', im.size, (18, 14, 34, 255)); inner.putalpha(m); im.alpha_composite(inner)
        ir = 24 * S * Z; ix = cx + lk * 10 * S * Z
        iris = Image.new('RGBA', im.size, (0, 0, 0, 0)); di = ImageDraw.Draw(iris)
        di.ellipse((ix - ir, cy - ir, ix + ir, cy + ir), fill=(130, 100, 255, 255))
        di.ellipse((ix - ir * .5, cy - ir * .5, ix + ir * .5, cy + ir * .5), fill=(14, 12, 24, 255))
        di.ellipse((ix + ir * .1, cy - ir * .55, ix + ir * .45, cy - ir * .2), fill=(255, 255, 255, 230))
        iris.putalpha(ImageChops.multiply(iris.getchannel('A'), m)); im.alpha_composite(iris)
        d.line(top + bot + [top[0]], fill=(250, 249, 246, 255), width=int(5.5 * S * Z), joint='curve')
        return im.resize((w, h), Image.LANCZOS)
    return K.C(('eye', ok, lk), mk)

def reticle(k, lock=0.0):
    """lock-on brackets (k 1 -> 0 = far -> snapped), lock flash 0..1."""
    S = 2; R = 210; im = Image.new('RGBA', (2 * R * S, 2 * R * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = (118 + 80 * k) * S; L = 34 * S; c = R * S; wd = int(6 * S)
    col = (250, 249, 246, 255)
    for sx in (-1, 1):
        for sy_ in (-1, 1):
            x, y = c + sx * r, c + sy_ * r * .78
            d.line([(x, y - sy_ * L), (x, y), (x - sx * L, y)], fill=col, width=wd, joint='curve')
    out = im.resize((2 * R, 2 * R), Image.LANCZOS)
    if lock > .01:
        gl = out.filter(ImageFilter.GaussianBlur(8)); gl = Image.merge('RGBA', [Image.new('L', out.size, 170), Image.new('L', out.size, 120), Image.new('L', out.size, 255), gl.getchannel('A').point(lambda v: int(min(255, v * 1.6 * lock)))])
        gl.alpha_composite(out); out = gl
    return out

RC_X, RC_Y = 540, 640                        # retention card centre (world)
# B punches in on him (s 1.08) after shot A (s 1), C pulls back (s 1) — every jump cut is a framing change; both keep
# his beard bottom above the caption line (take chin row <= ~1141)
AV_B = dict(show=True, s=1.08, x=0., y=455., alpha=1.0, copies=[], bright=1.0)
AV_C = dict(show=True, s=1.0, x=0., y=350., alpha=1.0, copies=[], bright=1.0)

def bg_house_soft(t):
    """the finished house, far out of focus behind the glass card (cheap low-res render)."""
    st = HS.state_at(t)
    cam = dict(yaw=-14 + 3 * math.sin(t * .3), pitch=11, dist=21, fov=30, target=(0, 2.2, 0.4), shift=(0, sy(600)))
    im = K.House(st, cam, HSIZE, fade=HFADE, t=t, lowres=3).img
    return K.desat(im.filter(ImageFilter.GaussianBlur(12)), .85, mul=.50)

def shot_bc(ctx, t):
    c = t >= K.J12
    ctx.bg_img = K.studio_bg(.52, 14.0)
    ctx.add('behind', bg_house_soft(t), 0, 0, center=False)
    # camera: B = him punched in, slow drift; C = pulled back, the card up + lock jolt (jump cuts = framing changes)
    if not c:
        ctx.avatar = dict(AV_B)
        z = 1.0 + .010 * (t - K.J11)
        ctx.cam = dict(z=z, x=540., y=1305., dx=0., dy=0., rot=0.)
        rcy = RC_Y
    else:
        ctx.avatar = dict(AV_C)
        z = 1.02 + .012 * (t - K.J12) + .045 * K.kick(t, K.O_CAR, 1.0, .30)
        dx, dy = K.shake(t, K.O_TI, 7.0, .3, 15, 2)
        ctx.cam = dict(z=z, x=540., y=900., dx=dx, dy=dy, rot=0.)
        rcy = RC_Y - 40
    # the card
    lt = t - K.O_E11
    rise = expo(lt / .34)
    card = rcard_static().copy()
    gk = expo((t - K.O_ISSO) / .30) if t >= K.O_ISSO else 0.0
    if gk > 0: card.alpha_composite(grid_img(gk))
    # COM EDIÇÃO
    x1 = K.eio3((t - K.O_QUE) / (K.O_FAZ - K.O_QUE)) if t >= K.O_QUE else 0.0
    lock = math.exp(-(t - K.O_CAR) / .35) if t >= K.O_CAR else 0.0
    card.alpha_composite(com_layer(x1, glow=lock + (.4 if t >= K.O_CAR else 0)))
    # SEM EDIÇÃO
    sx = sem_head(t)
    if sx > 0: card.alpha_composite(sem_layer(sx, t))
    # value chips
    if t >= K.O_FAZ - .01:
        lt2 = t - K.O_FAZ; ch = label_chip('COM EDIÇÃO', '91%', True); s = .6 + .4 * E.back(lt2 / .22, 1.8)
        im = K.scaled(ch, s); im = E.fade(im, clamp(lt2 / .06)) if lt2 < .06 else im
        ex, ey = P(1, com_curve(1))
        card.alpha_composite(im, (int(ex - 300 - im.width / 2), int(ey + 80 - im.height / 2)))
    if t >= 23.98 - .01:
        lt2 = t - 23.98; ch = label_chip('SEM EDIÇÃO', '8%', False); s = .6 + .4 * E.back(lt2 / .22, 1.8)
        im = K.scaled(ch, s); im = E.fade(im, clamp(lt2 / .06)) if lt2 < .06 else im
        ex, ey = P(1, sem_curve(1))
        card.alpha_composite(im, (int(ex - im.width / 2 - 120), int(ey - 64 - im.height / 2)))
    s = .90 + .10 * rise
    img = K.scaled(card, s)
    cy0 = rcy + 90 * (1 - rise)
    ctx.add('behind', img, RC_X, cy0, alpha=clamp(lt / .1), glass=14 if lt > .08 else 0)
    def wpt(x, y): return RC_X + (x - RCW / 2) * s, cy0 + (y - RCH / 2) * s
    # the eye at the head of the high line + the lock reticle (world layers: free to overhang the card)
    if t >= K.O_OLHO - .02:
        ex, ey = wpt(*P(1, com_curve(1)))
        ok = E.back((t - K.O_OLHO + .02) / .2, 1.6)
        look = -1.0 + 1.0 * expo((t - K.O_CAR) / .2) if t >= K.O_CAR else -1.0 + .6 * math.sin((t - K.O_OLHO) * 6)
        ctx.add('behind', K.glow_spot(150, (140, 100, 255), .65 + .35 * lock), ex, ey)
        ctx.add('behind', eye_img(ok, look), ex, ey)
        if t >= K.O_CAR - .1:
            rk = 1 - expo((t - (K.O_CAR - .1)) / .12)
            ctx.add('behind', reticle(rk, lock), ex, ey, alpha=clamp((t - (K.O_CAR - .1)) / .04))
            if K.O_CAR <= t < K.O_CAR + .5: ctx.add('behind', K.ring(170, (t - K.O_CAR) / .5, width=5), ex, ey)
    ctx.post['vignette'] = .36
    K.captions(ctx, t)

# ================================================================================================ SHOT D / E — every word
AV_D = dict(show=True, s=1.0, x=0., y=470., alpha=1.0, copies=[], bright=1.0)
PHOTO = E.V + '/lumarc-showcase/src/assets/close_food.png'
IC_W, IC_H, IC_S = 500, 560, 116             # image card: picture area + caption strip height
IC_X, IC_Y, IC_SC = 540, 640, .92            # card centre (world) + scale

# framings: one cut per word (t_cut, cam z, cam x, cam y, studio zoom)
CUTS = [(K.J13, 1.00, 540, 900, 1.00), (K.O_FRASE, 1.10, 540, 1120, 1.08), (K.O_IMAGEM, 1.22, 540, 1150, 1.16),
        (K.J14, 1.00, 540, 900, 1.00), (K.O_PALAVRA, 1.13, 540, 1150, 1.07), (K.O_UM14, 1.04, 540, 1100, 1.03)]
def framing(t):
    cur = CUTS[0]
    for c in CUTS:
        if t >= c[0] - 1e-6: cur = c
    return cur

def placeholder():
    """empty image placeholder (mountain + sun glyph, dashed frame)."""
    def mk():
        w, h = IC_W, IC_H; im = Image.new('RGBA', (w, h), (36, 34, 50, 255)); d = ImageDraw.Draw(im)
        g = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        sh = Image.fromarray((g * 40 * np.ones((1, w), np.float32)).astype(np.uint8)); im.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 8)] * 3 + [sh]))
        m = 26; x = m
        while x < w - m: d.line([(x, m), (min(x + 18, w - m), m)], fill=(255, 255, 255, 90), width=3); d.line([(x, h - m), (min(x + 18, w - m), h - m)], fill=(255, 255, 255, 90), width=3); x += 32
        y = m
        while y < h - m: d.line([(m, y), (m, min(y + 18, h - m))], fill=(255, 255, 255, 90), width=3); d.line([(w - m, y), (w - m, min(y + 18, h - m))], fill=(255, 255, 255, 90), width=3); y += 32
        S = 3; gm = Image.new('L', (w * S, h * S)); dg = ImageDraw.Draw(gm); cx, cy = w / 2 * S, h / 2 * S; s = 66 * S
        dg.rounded_rectangle((cx - s * 1.25, cy - s, cx + s * 1.25, cy + s), 18 * S, outline=255, width=8 * S)
        dg.polygon([(cx - s * 1.0, cy + s * .72), (cx - s * .25, cy - s * .2), (cx + s * .25, cy + s * .35), (cx + s * .55, cy + s * .05), (cx + s * 1.0, cy + s * .72)], fill=255)
        dg.ellipse((cx + s * .35, cy - s * .65, cx + s * .75, cy - s * .25), fill=255)
        gm = gm.resize((w, h), Image.LANCZOS); gi = Image.new('RGBA', (w, h), (190, 186, 210, 0)); gi.putalpha(gm.point(lambda v: int(v * .75)))
        im.alpha_composite(gi); return im
    return K.C('ph', mk)

def photo_img(w=IC_W, h=IC_H):
    def mk():
        im = Image.open(PHOTO).convert('RGB'); s = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        x0, y0 = (im.width - w) // 2, int((im.height - h) * .40)
        return im.crop((x0, y0, x0 + w, y0 + h)).convert('RGBA')
    return K.C(('photo', w, h), mk)

def photo_bg():
    """IMAGEM: the photo takes over the background (huge, defocused, darkened)."""
    def mk():
        im = Image.open(PHOTO).convert('RGB'); s_ = max(W / im.width, H / im.height) * 1.15
        im = im.resize((int(im.width * s_) + 1, int(im.height * s_) + 1), Image.LANCZOS)
        x0, y0 = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(26))
        return K.desat(im, .85, mul=.42)
    return K.C('photobg', mk)

def focus_brackets(k, hunt, col=WHITE):
    """camera AF brackets around the picture area: k = 0..1 visibility, hunt = scale wobble."""
    w, h = IC_W + 80, IC_H + 80; S = 2; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sc = 1 + hunt; hw, hh = IC_W / 2 * .78 * sc * S, IC_H / 2 * .78 * sc * S; cx, cy = w / 2 * S, h / 2 * S; L = 46 * S
    a = int(255 * k)
    for sx in (-1, 1):
        for sy_ in (-1, 1):
            x, y = cx + sx * hw, cy + sy_ * hh
            d.line([(x, y - sy_ * L), (x, y), (x - sx * L, y)], fill=col + (a,), width=6 * S, joint='curve')
    d.ellipse((cx - 10 * S, cy - 10 * S, cx + 10 * S, cy + 10 * S), outline=col + (a,), width=4 * S)
    return im.resize((w, h), Image.LANCZOS)

def image_card(t):
    """the FRASE/UMA/IMAGEM card: picture area (placeholder -> photo) + caption strip with the spoken word."""
    G = 70; w, h = IC_W, IC_H + IC_S
    out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
    out.alpha_composite(K.soft_shadow(w, h, 30, 30, .6, G), (0, 16))
    body = Image.new('RGBA', (w, h), (22, 20, 32, 255))
    if t < K.O_IMAGEM:
        pic = placeholder()
        if t >= K.O_UMA13:                                     # it loads: spinner arc
            pic = pic.copy(); d = ImageDraw.Draw(pic); cx, cy = IC_W / 2, IC_H / 2; r = 128
            a0 = ((t - K.O_UMA13) * 900) % 360
            d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 110, fill=(170, 130, 255, 255), width=9)
    else:
        k = (t - K.O_IMAGEM) / .30
        if k < 1:
            sc = 1.12 - .12 * expo(k); pw, ph_ = int(IC_W * sc), int(IC_H * sc)
            big = photo_img().resize((pw, ph_), Image.BILINEAR)
            pic = big.crop(((pw - IC_W) // 2, (ph_ - IC_H) // 2, (pw - IC_W) // 2 + IC_W, (ph_ - IC_H) // 2 + IC_H))
            fl = (1 - clamp(k * 1.8)) ** 2
            if fl > .01: pic = Image.blend(pic, Image.new('RGBA', pic.size, (255, 255, 255, 255)), fl * .8)
        else: pic = photo_img()
    body.alpha_composite(pic)
    # caption strip: the spoken word, live
    word, t0, sty = 'FRASE,', K.O_FRASE, 'white'
    if t >= K.O_UMA13: word, t0, sty = 'UMA', K.O_UMA13, 'white'
    if t >= K.O_IMAGEM: word, t0, sty = 'IMAGEM.', K.O_IMAGEM, 'grad'
    wi, _ = E.word_img(word, 88, sty); lt = t - t0
    wi = K.scaled(wi, .7 + .3 * E.back(lt / .16, 1.5))
    if lt < .05: wi = E.fade(wi, clamp(lt / .05))
    body.alpha_composite(wi, (int(w / 2 - wi.width / 2), int(IC_H + IC_S / 2 - wi.height / 2 + 4)))
    body.alpha_composite(E.glass_panel(w, h, radius=30, alpha=.0, border=.5))
    body.putalpha(ImageChops.multiply(body.getchannel('A'), K.rr_mask(w, h, 30)))
    out.alpha_composite(body, (G, G))
    # AF brackets hunt on UMA, lock + shutter blink on IMAGEM
    if K.O_UMA13 - .02 <= t < K.O_IMAGEM + .30:
        u = t - K.O_UMA13
        hunt = .16 * math.exp(-u / .09) * math.cos(u * 46) if t < K.O_IMAGEM else -.04 * math.exp(-(t - K.O_IMAGEM) / .06)
        ka = clamp(u / .04) * (1 - clamp((t - K.O_IMAGEM - .12) / .18))
        col = WHITE if t < K.O_IMAGEM else (180, 150, 255)
        fb = focus_brackets(ka, hunt, col)
        out.alpha_composite(fb, (G + w // 2 - fb.width // 2, G + IC_H // 2 - fb.height // 2))
    if K.O_IMAGEM - 1 / 30 <= t < K.O_IMAGEM + .001:           # shutter: one dark frame over the picture
        sh = Image.new('RGBA', (IC_W, IC_H), (0, 0, 0, 210)); out.alpha_composite(sh, (G, G))
    return out

def outline_word(txt, size):
    """hollow display type: gradient outline + faint fill (CADA, take 2)."""
    def mk():
        f = E.font(size, 900); sw = max(4, size // 34); pad = size // 3
        l, t_, r, b = f.getbbox(txt, stroke_width=sw); w, h = r - l + 2 * pad, b - t_ + 2 * pad
        st = Image.new('L', (w, h)); ImageDraw.Draw(st).text((pad - l, pad - t_), txt, font=f, fill=0, stroke_width=sw, stroke_fill=255)
        fi = Image.new('L', (w, h)); ImageDraw.Draw(fi).text((pad - l, pad - t_), txt, font=f, fill=255)
        ring_ = ImageChops.subtract(st, fi)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        gl = Image.new('RGBA', (w, h), (120, 90, 255, 0)); gl.putalpha(ring_.filter(ImageFilter.GaussianBlur(size * .06)).point(lambda v: int(v * .9))); out.alpha_composite(gl)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(ring_); out.alpha_composite(g)
        ff = Image.new('RGBA', (w, h), (250, 249, 246, 0)); ff.putalpha(fi.point(lambda v: int(v * .10))); out.alpha_composite(ff)
        return out
    return K.C(('outline', txt, size), mk)

TF_W, TF_H, TF_SIZE = 820, 190, 122
def type_field(n, caret_on):
    """glass text field with the first n characters of PALAVRA, typed (+ caret)."""
    def mk():
        w, h = TF_W, TF_H; G = 60; out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
        out.alpha_composite(K.soft_shadow(w, h, 44, 24, .5, G), (0, 12))
        body = Image.new('RGBA', (w, h), (14, 12, 24, 0)); body.putalpha(K.rr_mask(w, h, 44).point(lambda v: int(v * .62)))
        out.alpha_composite(body, (G, G)); out.alpha_composite(E.glass_panel(w, h, radius=44, alpha=.10, border=.55), (G, G))
        return out
    return K.C('tf', mk)

def typed_letters(t):
    """per-letter images + x offsets of PALAVRA, (each letter pops on its keystroke)."""
    full = 'PALAVRA,'; f = E.font(TF_SIZE, 800); l, t_, r, b = f.getbbox(full); x0 = -(r - l) / 2 - l
    fw = E.font(TF_SIZE); sw = max(3, TF_SIZE // 22); _, T0, _, B0 = fw.getbbox(full, stroke_width=sw); mid = (T0 + B0) / 2
    out = []
    for i, ch in enumerate(full):
        ts = K.O_PALAVRA + i * .034
        if t < ts - .005: break
        xa = x0 + f.getlength(full[:i]); wch = f.getlength(ch)
        wi, pad = E.word_img(ch, TF_SIZE, 'white')
        lt = t - ts; s = .55 + .45 * E.back(lt / .10, 2.4)
        _, tc_, _, bc_ = fw.getbbox(ch, stroke_width=sw)          # word_img centres each glyph on its own bbox
        out.append((K.scaled(wi, s), xa + wch / 2, clamp(lt / .03), (tc_ + bc_) / 2 - mid))
    caret_x = x0 + f.getlength(full[:len(out)]) + 10
    return out, caret_x

def light_trail(w, k):
    """horizontal gradient light streak (k = intensity), w px long, bright end on the right."""
    w = max(8, int(w // 20 * 20)); kk = round(k, 2)
    def mk():
        h = 70; x = np.linspace(0, 1, w, dtype=np.float32)[None, :]; y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
        a = (x ** 1.6) * np.exp(-(y / .14) ** 2) + .40 * (x ** 2.5) * np.exp(-(y / .5) ** 2)
        g = np.asarray(E.gradient(w, h, E.GRAD_LIGHT), np.float32)
        core = np.exp(-(y / .08) ** 2)[..., None]
        rgb = g * (1 - .55 * core) + 255 * .55 * core
        return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255 * kk, 0, 255)]).astype(np.uint8), 'RGBA')
    return K.C(('trail', w, kk), mk)

def trail_l(w, k):
    """light streak with its bright end on the LEFT (behind a word moving left)."""
    w = max(8, int(w // 20 * 20)); kk = round(k, 2)
    return K.C(('trail_l', w, kk), lambda: light_trail(w, kk).transpose(Image.FLIP_LEFT_RIGHT))

def speed_lines(t, k):
    """faint horizontal speed lines (screen layer, 1080 x 900 band), k intensity."""
    im = Image.new('RGBA', (W, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(24):
        y = 40 + K.hrand(i, 3) * 820; L = 160 + 520 * K.hrand(i, 4); v = 5200 + 3000 * K.hrand(i, 5)
        x = (K.hrand(i, 6) * 2400 - v * (t - K.O_MOVIMENTO)) % 2400 - 600
        a = int(120 * k * (.4 + .6 * K.hrand(i, 7)))
        if a > 2: d.line([(x, y), (x + L, y)], fill=(235, 228, 255, a), width=2 + int(2 * K.hrand(i, 8)))
    return im

def smeared_studio(level):
    """the studio plate smeared horizontally (camera whip), cached per level."""
    def mk():
        im = K.studio_bg(.34, 5.0).convert('RGBA')
        return K.mblur_h(im, 30 * level).convert('RGB') if level else im.convert('RGB')
    return K.C(('smear', level), mk)

# ---------------------------------------------------------------------------------------- the edit timeline HUD
TLH_W, TLH_H = 940, 178
TLH_X, TLH_Y = 540, 1712                      # centre (screen)
TR_X0, TR_X1 = 34, TLH_W - 34                 # track span in HUD px
V1_Y0, V1_Y1, A1_Y0, A1_Y1 = 44, 98, 112, 156
SEG_T0, SEG_T1 = K.J13, K.J15
WORD_CUTS = [K.O_CADA13, K.O_FRASE, K.O_UMA13, K.O_IMAGEM, K.O_CADA14, K.O_PALAVRA, K.O_UM14, K.O_MOVIMENTO]
CLIP_KIND = ['type', 'card', 'card', 'photo', 'outline', 'type', 'type', 'streak']
def hx(t): return TR_X0 + (TR_X1 - TR_X0) * (t - SEG_T0) / (SEG_T1 - SEG_T0)

def tl_env():
    """voice RMS envelope (dB, 100 Hz) over the D/E span, normalised 0..1."""
    def mk():
        x = np.fromfile(E.SRC + '/tight16k.raw', np.float32); h = 160
        a, b = int(SEG_T0 * 16000), int(SEG_T1 * 16000)
        seg = x[a:b]; n = len(seg) // h
        r = np.sqrt((seg[:n * h].reshape(n, h) ** 2).mean(1)); db = 20 * np.log10(r + 1e-6)
        return np.clip((db + 50) / 38, 0, 1)
    return K.C('tlenv', mk)

def tl_static():
    """HUD panel + dim waveform + track beds (cached)."""
    def mk():
        G = 50; w, h = TLH_W, TLH_H; out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
        out.alpha_composite(K.soft_shadow(w, h, 30, 24, .55, G), (0, 10))
        body = Image.new('RGBA', (w, h), (12, 10, 22, 0)); body.putalpha(K.rr_mask(w, h, 30).point(lambda v: int(v * .72)))
        out.alpha_composite(body, (G, G)); out.alpha_composite(E.glass_panel(w, h, radius=30, alpha=.06, border=.45), (G, G))
        d = ImageDraw.Draw(out)
        d.rounded_rectangle((G + TR_X0, G + V1_Y0, G + TR_X1, G + V1_Y1), 8, fill=(255, 255, 255, 14))
        d.rounded_rectangle((G + TR_X0, G + A1_Y0, G + TR_X1, G + A1_Y1), 8, fill=(255, 255, 255, 10))
        for i in range(0, 37):                                  # ruler ticks
            x = G + TR_X0 + (TR_X1 - TR_X0) * i / 36; d.line([(x, G + 16), (x, G + (30 if i % 6 == 0 else 24))], fill=(255, 255, 255, 70), width=2)
        return out
    return K.C('tlstatic', mk)

def tl_wave(bright):
    """waveform bars over the full track (dim or bright), HUD-panel sized."""
    def mk():
        G = 50; out = Image.new('RGBA', (TLH_W + 2 * G, TLH_H + 2 * G), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
        env = tl_env(); cy = G + (A1_Y0 + A1_Y1) / 2; amp = (A1_Y1 - A1_Y0) / 2 - 3
        for x in range(TR_X0 + 3, TR_X1 - 2, 5):
            tt = SEG_T0 + (x - TR_X0) / (TR_X1 - TR_X0) * (SEG_T1 - SEG_T0)
            i = int((tt - SEG_T0) * 100); v = float(env[max(0, min(len(env) - 1, i))])
            hh = max(1.5, v * amp)
            col = (160, 130, 255, 230) if bright else (255, 255, 255, 46)
            d.rounded_rectangle((G + x - 1.2, cy - hh, G + x + 1.2, cy + hh), 1, fill=col)
        return out
    return K.C(('tlwave', bright), mk)

def tl_clips():
    """V1 clip blocks (one per word, cut on its onset), full length (cropped to the playhead at draw time)."""
    def mk():
        G = 50; out = Image.new('RGBA', (TLH_W + 2 * G, TLH_H + 2 * G), (0, 0, 0, 0))
        cols = [(79, 107, 255), (106, 85, 255), (154, 77, 255), (120, 96, 255), (90, 100, 255), (140, 80, 255), (110, 90, 255), (154, 77, 255)]
        edges = WORD_CUTS + [SEG_T1]
        for i, kind in enumerate(CLIP_KIND):
            x0, x1 = G + hx(edges[i]) + 2, G + hx(edges[i + 1]) - 2
            if x1 - x0 < 3: continue
            bw, bh = int(x1 - x0), V1_Y1 - V1_Y0
            blk = Image.new('RGBA', (bw, bh), cols[i] + (205,))
            if kind == 'photo':
                ph = photo_img(120, 150).resize((bh * 4 // 5, bh), Image.LANCZOS)
                for xx in range(0, bw, ph.width): blk.alpha_composite(ph.crop((0, 0, min(ph.width, bw - xx), bh)), (xx, 0))
            hl = Image.new('RGBA', (bw, bh), (255, 255, 255, 0)); dh = ImageDraw.Draw(hl); dh.rectangle((0, 0, bw, 2), fill=(255, 255, 255, 120))
            if kind in ('type', 'outline'):
                for k_ in range(3): dh.rounded_rectangle((8, 12 + k_ * 12, max(10, bw * (.8 - .2 * k_)), 17 + k_ * 12), 2, fill=(255, 255, 255, 120))
            if kind == 'card': dh.rounded_rectangle((bw / 2 - 12, 10, bw / 2 + 12, bh - 10), 4, outline=(255, 255, 255, 150), width=2)
            if kind == 'streak': dh.line([(6, bh / 2), (bw - 6, bh / 2)], fill=(255, 255, 255, 170), width=3)
            blk.alpha_composite(hl)
            blk.putalpha(ImageChops.multiply(blk.getchannel('A'), K.rr_mask(bw, bh, 7)))
            out.alpha_composite(blk, (int(x0), G + V1_Y0))
        return out
    return K.C('tlclips', mk)

def tl_hud(t):
    G = 50; out = tl_static().copy()
    px = hx(t); cx = int(G + px)
    out.alpha_composite(tl_wave(False))
    out.alpha_composite(tl_wave(True).crop((0, 0, cx, out.height)), (0, 0))
    out.alpha_composite(tl_clips().crop((0, 0, cx, out.height)), (0, 0))
    d = ImageDraw.Draw(out)
    for tc in WORD_CUTS:                                        # razor marks: flash when the playhead cuts
        if t < tc - .005: continue
        x = G + hx(tc); fl = math.exp(-(t - tc) / .16)
        d.line([(x, G + V1_Y0 - 6), (x, G + A1_Y1 + 4)], fill=(255, 255, 255, int(110 + 145 * fl)), width=2 + int(2 * fl))
        if fl > .05:
            sp = K.glow_spot(34, (200, 170, 255), fl); out.alpha_composite(sp, (int(x - 34), int(G + V1_Y0 - 40)))
    # playhead
    gl = K.glow_spot(26, (150, 110, 255), .8)
    out.alpha_composite(K.scaled(gl, 1.0), (cx - 26, G + 6))
    d.line([(cx, G + 30), (cx, G + A1_Y1 + 8)], fill=(250, 249, 246, 255), width=3)
    d.polygon([(cx - 11, G + 14), (cx + 11, G + 14), (cx + 11, G + 26), (cx, G + 36), (cx - 11, G + 26)], fill=(250, 249, 246, 255))
    return out

def shot_de(ctx, t):
    tc, z, cx, cy, bz = framing(t)
    ctx.avatar = dict(AV_D)
    ctx.bg_img = K.studio_bg(.34, 5.0, z=bz)
    dx, dy = K.shake(t, K.O_CADA13, 10, .26, 17, 1)
    ex, ey = K.shake(t, K.O_CADA14, 8, .24, 17, 2); dx += ex; dy += ey
    ex, ey = K.shake(t, K.O_MEN, 12, .32, 16, 3); dx += ex; dy += ey
    ctx.cam = dict(z=z * (1 + .04 * K.kick(t, tc, 1.0, .22)), x=float(cx), y=float(cy), dx=dx, dy=dy, rot=0.)
    lt_cut = t - tc
    if lt_cut < .1: ctx.post['flash'] = .14 * (1 - lt_cut / .1) ** 2
    ctx.add('behind', K.glow_spot(520, (110, 80, 255), .30), 540 + 160 * math.sin(t * 1.3), 760 + 60 * math.cos(t * .9))
    if t < K.O_FRASE:                                           # CADA slams in behind him (his head overlaps it)
        lt = t - K.J13 + 1 / 30                                 # slams in on the cut, lands on its k-burst (24.755)
        if lt > 0:
            wi, _ = E.word_img('CADA', 320, 'white'); s = 1.35 - .35 * eo(lt / .09, 3)
            ctx.add('behind', K.scaled(wi, s), 540, 1005, alpha=clamp(lt / .04))
    elif t < K.J14:                                            # FRASE, -> UMA -> IMAGEM. (the image card)
        lt = t - K.O_FRASE + 1 / 30                            # snaps in ON the word (visible on its frame)
        k = expo(lt / .20); x = lerp(IC_X + 230, IC_X, k); rot = lerp(9, -3, k) + 1.2 * math.sin(t * 2.0) * k
        card = image_card(t)
        if k < .9: card = K.mblur_h(card, -120 * (1 - k))
        s = IC_SC * (1 + .14 * (1 - k)) * (1 + .05 * K.kick(t, K.O_IMAGEM, 1.0, .25))
        card = K.scaled(card, s).rotate(rot, Image.BICUBIC, expand=True)
        ctx.add('behind', card, x, IC_Y + 6 * math.sin(t * 1.7), alpha=clamp(lt / .04))
        if K.O_IMAGEM <= t < K.O_IMAGEM + .07: ctx.post['flash'] = .38 * (1 - (t - K.O_IMAGEM) / .07)
        if t >= K.O_IMAGEM: ctx.bg_img = photo_bg()
    elif t < K.O_PALAVRA:                                      # CADA, take 2: hollow outline type behind him
        lt = t - K.J14 + 1 / 30                                 # on the cut (no empty frames), lands on 26.47
        if lt > 0:
            wi = outline_word('CADA', 320); s = 1.28 - .28 * eo(lt / .10, 3)
            ctx.add('behind', K.scaled(wi, s), 540, 1005, alpha=clamp(lt / .04))
    elif t < K.O_UM14:                                         # PALAVRA, typed letter by letter
        fy = 720
        ctx.add('behind', type_field(0, False), 540, fy)
        lets, caret_x = typed_letters(t)
        for im, x, a, dy in lets: ctx.add('behind', im, 540 + x, fy + 6 + dy, alpha=a)
        done = len(lets) >= 8
        if not done or int((t - K.O_PALAVRA) * 3.4) % 2 == 0:
            ctx.add('behind', K.glow_spot(30, (170, 130, 255), .8), 540 + caret_x + 4, fy)
            car = Image.new('RGBA', (9, 104), (190, 160, 255, 255)); ctx.add('behind', car, 540 + caret_x + 4, fy)
    else:                                                      # UM ... MOVIMENTO. whips in on a light streak
        lt = t - K.O_UM14; fy = 740
        um, _ = E.word_img('UM', 104, 'white')
        ctx.add('behind', K.scaled(um, .7 + .3 * E.back(lt / .16, 1.5)), 540, 560, alpha=clamp(lt / .05))
        if t >= K.O_MOVIMENTO:
            wi0, _ = E.word_img('MOVIMENTO.', 140, 'grad')
            T_IN = K.O_MEN - .092                             # the word whips in, crosses its mark ON "-MEN-", settles
            if t < T_IN:                                       # anticipation: a light beam shoots in along its path
                u = (t - K.O_MOVIMENTO) / (T_IN - K.O_MOVIMENTO)
                hx_ = lerp(1110, 540 - wi0.width / 2 + 70, K.eo(u, 2.4))     # its bright head leads (moving left)
                beam = trail_l(1300, round(.70 + .30 * u, 2))   # bright end on the LEFT = the head
                ctx.add('behind', beam, hx_ + beam.width / 2, fy, alpha=clamp(u * 4))
                ctx.add('behind', K.glow_spot(70, (200, 175, 255), .85 * clamp(u * 4)), hx_ + 8, fy)
                ctx.add('screen', speed_lines(t, .5 * u), 0, 300, center=False)
            else:
                u = (t - T_IN) / .16
                k = E.back(u, .75) if u < 1 else 1.0
                x = lerp(1720, 540, k)
                kp = E.back(min(1, u + .06), .75) - E.back(max(0, u - .06), .75) if u < 1 else 0.0
                vel = abs(kp) * (1720 - 540) / (.12 / .16 * .16 * 30) if u < 1 else 0.0
                sm = clamp(vel * 1.4, 0, 320)
                wi = K.mblur_h(wi0, sm) if sm > 3 else wi0
                v = t - K.O_MEN
                if v > 0:                                      # squash on the hit
                    sx = 1 + .09 * math.exp(-v / .10) * math.cos(v * 40)
                    wi = wi.resize((max(1, int(wi.width * sx)), max(1, int(wi.height / sx ** .6))), Image.BILINEAR)
                tl_ = 1.0 if v <= 0 else math.exp(-v / .18)
                if tl_ > .03:
                    tr = trail_l(1500, round(tl_, 2)); ctx.add('behind', tr, x + wi0.width * .30 + tr.width / 2 + (600 * (1 - math.exp(-v / .22)) if v > 0 else 0), fy)
                if v > 0:
                    ctx.add('behind', K.glow_spot(380, (130, 90, 255), .55 * math.exp(-v / .25)), 540, fy)
                ctx.add('behind', wi, x, fy)
                sl = .9 if v <= 0 else .9 * (1 - clamp(v / .25))
                if sl > .02: ctx.add('screen', speed_lines(t, sl), 0, 300, center=False)
                if v < .10: ctx.bg_img = smeared_studio(3 if v <= 0 else 1)
    # the edit timeline: a cut placed on every word, the voice waveform underneath
    lt0 = t - K.J13
    hud = tl_hud(t)
    ctx.add('screen', hud, TLH_X, TLH_Y + 240 * (1 - expo(lt0 / .26)), alpha=clamp(lt0 / .08))
    ctx.post['vignette'] = .36
    ctx.captions = False

# ================================================================================================ draw
def draw(ctx, lt, t):
    if t >= K.J15 - 1e-6:                                      # 28.30: seg 15's pose -> s06's first framing
        from sections import s06_vazio as S6
        return S6.shot_f(ctx, t)
    if t < K.J11: shot_a(ctx, t)
    elif t < K.J13: shot_bc(ctx, t)
    else: shot_de(ctx, t)
