"""s01 — HOOK (0.00–4.72): "Edição boa não é enfeite. / Ela mostra o que você fala. / Olha só." + the silent beat.

Beats (edit timeline s, onsets measured on src/tight16k.raw — see _A_kit; jump cuts land on the first frame that shows
the new pose, K.jump_t: 2.0667 / 3.8333 / 4.40):
  0.00  hard open: 3-frame lights-up ramp (.46 -> 1, never a black first frame), punch-in z 1.55 -> 1.16 (expo), rack focus on the studio (blur 14 -> 2.5),
        a light sweep crosses the wall behind him.  Clean, premium = "edição boa".
  1.27  "en-": one cheap sparkle sticker sneaks in next to his head (foreshadow).
  1.49  "-FEI-" (stressed): THE CHEESE BOMB — glitter photo-frame, die-cut emoji stickers, a rainbow "WOW!" starburst,
        the caption word turns into rainbow WordArt, the camera does a cheap template wobble, saturation goes garish.
  1.855 "-TE" (t burst): a clean LUMARC gradient line SLASHES across the frame in 3 frames: every sticker is swatted
        out of the frame (spin + motion blur), the glitter frame bursts outward into glitter, the WordArt is sliced
        in half and falls away, leaving the clean word — the line settles into its strikethrough (2.00).
  2.07  jump -> tight on his face.  2.44 "MOSTRA": a giant extruded gradient MOSTRA slams in BEHIND him (his head
        overlaps it); on "-TRA" (2.745) it splits like two sliding doors (MOS <- -> TRA) while the camera dollies
        back + cranes up (parallax: he 1.32 -> 1.0, the studio 1.30 -> 1.08): the doors reveal an empty lit space above
        him — a light beam, floating dust — and on "o que você" (2.82) a surveyor's dashed footprint of a lot draws
        itself in perspective: corner markers on "que", survey stakes on "você", a pulse on "fala".
  3.83  jump "OLHA": the camera orbits (yaw 74 -> 33, expo whip, first frames smeared): he sweeps left (near), the
        wall right (far) — the floating lot rises into the footprint (3.89, kit), lands on 4.07 "SÓ" (thud): the
        dashes flash and lock onto its edges, the beam lays a pool of light on the grass.
  4.40  jump (silent beat): high 3/4 on the empty floating lot alone, a visible slow push-in + orbit drift (~5 % and 1.6 deg
        over the beat), beam + dust.  s02 continues this shot.
Captions: own word pops (engine look, baseline-aligned) on the measured onsets, at y 1560 on his chest whenever he is
in frame (same as s03/s04); ENFEITE is restyled by the gag itself (WordArt -> sliced -> struck through).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import engine as E
from sections import _A_kit as K
from sections import _house as HS

START, END = E.span(0, 3)
W, H = E.W, E.H
lerp, clamp, eio, expo, eo = K.lerp, E.clamp, K.eio, K.expo, K.eo

T_SLASH0 = 1.80                                          # slash head enters (passes the word centre at K.T_TE)
T_STRIKE = 2.00                                          # line settled as the word's strikethrough
CAP_Y_A = 1440

CUES = [
    (0.0, 'boom', {'gain': -4}), (0.02, 'whoosh', {'gain': -4}), (0.06, 'shimmer', {'gain': -12}),
    (K.T_ENFEITE, 'shimmer', {'gain': -15}),                                     # one sneaky sparkle
    (K.T_FEI, 'pop', {'gain': 2}), (K.T_FEI + .01, 'shimmer', {'gain': -3}),     # cheese bomb
    (K.T_FEI + .04, 'pop', {'gain': -3, 'pan': .45}), (K.T_FEI + .08, 'pop', {'gain': -4, 'pan': -.45}),
    (K.T_FEI + .12, 'cash', {'gain': -9}),
    (K.T_TE, 'swipe', {'gain': 2}), (K.T_TE, 'impact', {'gain': -7}),            # the slash
    (K.T_TE + .02, 'glass', {'gain': -10, 'seed': 4}),
    (K.T_MOSTRA, 'impact', {'gain': -5}), (K.T_MOSTRA - .02, 'swoosh_up', {'gain': -10}),
    (K.T_TRA, 'whoosh', {'gain': -4}),                                           # doors part / dolly back
    (K.T_O1 + .04, 'shimmer', {'gain': -16}),                                    # footprint draws
    (K.T_QUE, 'tick', {'gain': -6}), (K.T_VOCE + .06, 'tick', {'gain': -9}), (K.T_FALA, 'tick', {'gain': -8}),
    (K.CUT2, 'whoosh', {'gain': -6}),                                            # orbit whip on "OLHA"
] + [c for c in HS.BUILD_CUES if START <= c[0] < END]                           # lot rises (3.94) + settles (4.08)

# ------------------------------------------------------------------------------------------- shared shot rig (s02 reuses)
def lot_close_cam(t):
    """the silent-beat close-up on the empty lot (4.40 ->), slow push; s02 starts from exactly this camera."""
    u = (t - K.CUT3) / 1.0
    return K.fcam(41 - 5 * u, 36 - 2 * u, 24 - 3.6 * u, 1180, (0, 0, 0), 540, 1000)

TWO_F = dict(s=1.0, fx=540, fy=1255)                 # him in the two-shot (bottom centre; same scale as s03/s04)
CAP_Y = 1572                                          # captions on his chest whenever he is in frame (as s03/s04)
def two_cam(t, yaw=None):
    """two-shot frame camera: house above him."""
    y = 27 + 2.0 * math.sin(t * .23) if yaw is None else yaw
    return K.fcam(y, 22 + 1.2 * math.sin(t * .17 + 1), 34.5, 1800, (0, 1.6, -0.3), 595, 560)

# ------------------------------------------------------------------------------------------- cheese assets
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
INTER_BI = '/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf'

def _emoji(ch):
    def mk():
        f = ImageFont.truetype(EMOJI, 109); im = Image.new('RGBA', (180, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        return im.crop(im.getbbox())
    return E.cached(('A_emoji', ch), mk)

def sticker(ch, size):
    """die-cut sticker: emoji + fat white outline + soft drop shadow (the cheap Instagram-sticker look)."""
    def mk():
        e = _emoji(ch); s = size / max(e.size); e = e.resize((max(1, int(e.width * s)), max(1, int(e.height * s))), Image.LANCZOS)
        pad = int(size * .16); w, h = e.width + 2 * pad, e.height + 2 * pad
        a = Image.new('L', (w, h)); a.paste(e.getchannel('A'), (pad, pad))
        ol = a.filter(ImageFilter.MaxFilter(int(size * .07) * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 90 else int(v * 2.8))
        out = Image.new('RGBA', (w + 24, h + 24), (0, 0, 0, 0))
        sh = Image.new('RGBA', (w, h), (20, 10, 30, 0)); sh.putalpha(ol.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .55)))
        out.alpha_composite(sh, (16, 20))
        wh = Image.new('RGBA', (w, h), (255, 255, 255, 0)); wh.putalpha(ol); out.alpha_composite(wh, (12, 12))
        out.alpha_composite(e, (12 + pad, 12 + pad))
        return out
    return E.cached(('A_sticker', ch, size), mk)

def _rainbow(w, h, vertical=True):
    cols = np.array([(255, 60, 90), (255, 150, 30), (255, 230, 40), (60, 220, 90), (40, 170, 255), (190, 80, 255)], np.float32)
    n = h if vertical else w; u = np.linspace(0, len(cols) - 1, n)
    i = np.clip(u.astype(int), 0, len(cols) - 2); f = (u - i)[:, None]
    line = cols[i] * (1 - f) + cols[i + 1] * f
    arr = np.repeat(line[:, None, :], w, 1) if vertical else np.repeat(line[None, :, :], h, 0)
    return Image.fromarray(arr.astype(np.uint8), 'RGB')

def wordart(text, size, extrude=10):
    """1998 WordArt: rainbow fill, white + black outline, purple 3-D extrusion, hard drop shadow."""
    def mk():
        f = ImageFont.truetype(INTER_BI, size); sw = max(4, size // 14)
        l, t, r, b = f.getbbox(text, stroke_width=sw * 2); pad = size // 3 + extrude
        w, h = r - l + 2 * pad, b - t + 2 * pad; org = (pad - l, pad - t)
        fill = Image.new('L', (w, h)); ImageDraw.Draw(fill).text(org, text, font=f, fill=255)
        s1 = Image.new('L', (w, h)); ImageDraw.Draw(s1).text(org, text, font=f, fill=255, stroke_width=sw, stroke_fill=255)
        s2 = Image.new('L', (w, h)); ImageDraw.Draw(s2).text(org, text, font=f, fill=255, stroke_width=sw * 2, stroke_fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sh = Image.new('RGBA', (w, h), (30, 0, 40, 0)); sh.putalpha(s2.point(lambda v: int(v * .7)))
        out.alpha_composite(sh.transform((w, h), Image.AFFINE, (1, 0, -extrude - 6, 0, 1, -extrude - 8)))    # hard drop shadow
        for i in range(extrude, 0, -1):
            k = i / extrude; col = (int(90 - 40 * k), int(20 + 10 * (1 - k)), int(150 - 60 * k))
            L = Image.new('RGBA', (w, h), col + (0,)); L.putalpha(s2); out.alpha_composite(L.transform((w, h), Image.AFFINE, (1, 0, -i * .8, 0, 1, -i)))
        bk = Image.new('RGBA', (w, h), (15, 5, 30, 0)); bk.putalpha(s2); out.alpha_composite(bk)
        wh = Image.new('RGBA', (w, h), (255, 255, 255, 0)); wh.putalpha(s1); out.alpha_composite(wh)
        rb = _rainbow(w, h).convert('RGBA'); rb.putalpha(fill); out.alpha_composite(rb)
        hl = Image.new('RGBA', (w, h), (255, 255, 255, 0))
        top = np.asarray(fill, np.float32) * np.clip(1 - np.linspace(0, 2.2, h), 0, 1)[:, None] * .55
        hl.putalpha(Image.fromarray(top.astype(np.uint8))); out.alpha_composite(hl)
        return out
    return E.cached(('A_wordart', text, size), mk)

def wow():
    """rainbow 'WOW!' on a yellow comic starburst."""
    def mk():
        txt = wordart('WOW!', 120, 8); w, h = txt.width + 120, txt.height + 120
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cx, cy, n = w / 2, h / 2, 14; pts = []
        for i in range(2 * n):
            a = math.pi * i / n; r = (w * .49 if i % 2 == 0 else w * .36), (h * .49 if i % 2 == 0 else h * .34)
            pts.append((cx + r[0] * math.cos(a), cy + r[1] * math.sin(a)))
        d.polygon(pts, fill=(255, 226, 40, 255), outline=(230, 30, 60, 255), width=7)
        im.alpha_composite(txt, ((w - txt.width) // 2, (h - txt.height) // 2))
        return K_shadow(im)
    return E.cached('A_wow', mk)

def K_shadow(im, off=(10, 14), blur=8, a=.5):
    out = Image.new('RGBA', (im.width + 40, im.height + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (20, 0, 30, 0)); sh.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * a)))
    out.alpha_composite(sh, (20 + off[0], 20 + off[1])); out.alpha_composite(im, (20, 20)); return out

FR_IN, FR_W, FR_R = 30, 46, 70          # glitter frame inset, band width, corner radius
def glitter_frame(v):
    """tacky gold/pink glitter photo-frame (full frame RGBA), twinkle variant v."""
    def mk():
        r = np.random.default_rng(40 + v)
        m = Image.new('L', (W, H)); d = ImageDraw.Draw(m)
        d.rounded_rectangle((FR_IN, FR_IN, W - FR_IN, H - FR_IN), FR_R, fill=255)
        d.rounded_rectangle((FR_IN + FR_W, FR_IN + FR_W, W - FR_IN - FR_W, H - FR_IN - FR_W), FR_R - 20, fill=0)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        ang = (np.arctan2(yy - H / 2, xx - W / 2) / (2 * math.pi) + .5) * 3
        k = (ang % 1.0)[..., None]
        cA = np.array([255, 205, 70], np.float32); cB = np.array([255, 105, 200], np.float32); cC = np.array([120, 230, 255], np.float32)
        seg = np.floor(ang % 3)[..., None]
        base = np.where(seg == 0, cA * (1 - k) + cB * k, np.where(seg == 1, cB * (1 - k) + cC * k, cC * (1 - k) + cA * k))
        noise = r.random((H, W)).astype(np.float32)
        spark = (noise > .965).astype(np.float32) * r.uniform(.6, 1.0, (H, W)).astype(np.float32)
        rgb = base * (.55 + .45 * r.random((H, W, 1)).astype(np.float32)) + spark[..., None] * 255
        ma = np.asarray(m, np.float32) / 255.
        edge = np.asarray(m.filter(ImageFilter.FIND_EDGES), np.float32) / 255.
        rgb = rgb * (1 - edge[..., None] * .6)
        im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), ma * 255]).astype(np.uint8), 'RGBA')
        # big 4-point glints along the band
        gl = _glint(46)
        for (x, y) in [(FR_IN + 20, FR_IN + 30), (W - FR_IN - 30, FR_IN + 60), (FR_IN + 30, H - FR_IN - 90), (W - FR_IN - 24, H - FR_IN - 30),
                       (W // 2, FR_IN + 20), (FR_IN + 22, H // 2 - 200), (W - FR_IN - 22, H // 2 + 260), (W // 2 + 180, H - FR_IN - 22)]:
            s = .6 + .8 * r.random(); g = gl.resize((int(gl.width * s), int(gl.height * s)), Image.BILINEAR)
            im.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        return im
    return E.cached(('A_glitter', v), mk)

def _glint(r):
    def mk():
        n = r * 4; im = Image.new('L', (n, n)); d = ImageDraw.Draw(im); c = n / 2
        d.polygon([(c, 0), (c + r * .16, c - r * .16), (n, c), (c + r * .16, c + r * .16), (c, n), (c - r * .16, c + r * .16), (0, c), (c - r * .16, c - r * .16)], fill=255)
        g = im.filter(ImageFilter.GaussianBlur(r * .25))
        a = ImageChops.lighter(im.filter(ImageFilter.GaussianBlur(1)), g)
        out = Image.new('RGBA', (n, n), (255, 250, 220, 0)); out.putalpha(a); return out
    return E.cached(('A_glint', r), mk)

# stickers: (emoji, x, y, size, rot deg, delay s, side)  — around him, never on his face
STICKERS = [('✨', 210, 470, 190, -12, .00), ('😍', 880, 520, 180, 12, .07), ('💯', 175, 1110, 200, -9, .03),
            ('🔥', 905, 1130, 205, 9, .10), ('💖', 945, 840, 150, 15, .05), ('⭐', 120, 790, 140, -6, .12),
            ('🌈', 830, 300, 170, 14, .09)]
WOW_POS = (300, 300, -11)

# ------------------------------------------------------------------------------------------- slash geometry
SL_ANG = math.radians(-15.5)
SL_D = np.array([math.cos(SL_ANG), math.sin(SL_ANG)])          # direction (rising to the right)
SL_N = np.array([-SL_D[1], SL_D[0]])                            # normal (points down-right)
def _word_c():
    return K.word_box(CAP, 'ENFEITE.', CAP_Y_A)
def slash_head(t):
    """distance of the slash head along SL_D from the word centre (px); 0 at K.T_TE."""
    return (t - K.T_TE) * 26000
def slash_tail(t):
    return (t - (K.T_TE + .045)) * 26000 if t > K.T_TE + .045 else -1e9

# ------------------------------------------------------------------------------------------- MOSTRA doors
def mostra_halves():
    """giant extruded gradient MOSTRA split into the two door leaves MOS | TRA (RGBA each + split x)."""
    def mk():
        text = 'MOSTRA'; size = 300
        l, t, r, b = E.font(size, 900).getbbox(text); size = int(size * 930 / (r - l))
        f = E.font(size, 900); l, t, r, b = f.getbbox(text); pad = 110; w, h = r - l + 2 * pad, b - t + 2 * pad + 30
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        glow = Image.new('RGBA', (w, h), (110, 70, 255, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(50)).point(lambda v: int(v * .8)))
        out.alpha_composite(glow)
        depth = 20
        for i in range(depth, 0, -1):
            k = i / depth; col = (int(26 + 40 * (1 - k)), int(18 + 24 * (1 - k)), int(70 + 90 * (1 - k)))
            L = Image.new('RGBA', (w, h), col + (0,)); L.putalpha(m); out.alpha_composite(L, (int(i * .45), int(i * .9)))
        g = np.asarray(E.gradient(w, h, [(150, 170, 255), (140, 110, 255), (196, 120, 255)]), np.float32)
        vy = np.linspace(1.25, .66, h, dtype=np.float32)[:, None, None]
        face = Image.fromarray(np.clip(g * vy, 0, 255).astype(np.uint8)).convert('RGBA'); face.putalpha(m); out.alpha_composite(face)
        sh = ImageChops.subtract(m, m.transform(m.size, Image.AFFINE, (1, 0, 0, 0, 1, 5)))
        hl = Image.new('RGBA', (w, h), (255, 255, 255, 0)); hl.putalpha(sh.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: int(v * .8)))
        out.alpha_composite(hl)
        xs = int(pad - l + f.getlength('MOS') + 3)
        return out.crop((0, 0, xs, h)), out.crop((xs, 0, w, h)), xs, w, h
    return E.cached('A_mostra', mk)

# ------------------------------------------------------------------------------------------- captions
CAP = [K.page(0.02, K.T_NAO, [('EDIÇÃO', K.T_EDICAO, 0), ('BOA', K.T_BOA, 0)]),
       K.page(K.T_NAO, K.CUT1, [('NÃO', K.T_NAO, 0), ('É', K.T_E0, 0), ('ENFEITE.', K.T_ENFEITE, 1)])]
CAP_B = [K.page(K.CUT1, K.T_O1, [('ELA', K.T_ELA, 0), ('MOSTRA', K.T_MOSTRA, 1)]),
         K.page(K.T_O1, K.CUT2, [('O', K.T_O1, 0), ('QUE', K.T_QUE, 0), ('VOCÊ', K.T_VOCE, 0), ('FALA.', K.T_FALA, 0)])]
CAP_C = [K.page(K.CUT2, K.CUT3, [('OLHA', K.T_OLHA, 0), ('SÓ.', K.T_SO, 1)])]

# ------------------------------------------------------------------------------------------- draw
def draw(ctx, lt, t):
    P = ctx.post; ctx.light = 0.0
    if t < K.CUT1: _shot_a(ctx, t, P)
    elif t < K.CUT2: _shot_b(ctx, t, P)
    elif t < K.CUT3: _shot_c(ctx, t, P)
    else: _shot_d(ctx, t, P)
    if ctx.light > .03 and ctx.wrap is None:
        k = min(.5, ctx.light); ctx.wrap = lambda fr: K.light_hit(fr, k)

# ---- A: "Edição boa não é enfeite."
def _sweep_bg(c, amp):
    st = E.cached('A_studio_f', lambda: np.asarray(E.studio(), np.float32))
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); return xx * .82 + yy * .42
    u = E.cached('A_sweep_u', mk)
    k = (np.exp(-((u - c) / 170.) ** 2) + .35 * np.exp(-((u - c - 260) / 60.) ** 2)) * amp
    out = st + k[..., None] * np.array([150, 130, 255], np.float32) + st * k[..., None] * 1.2
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def _shot_a(ctx, t, P):
    cam = ctx.cam; fi = int(round(t * E.FPS))
    if fi < 3: P['bright'] = [.46, .78, 1.0][fi]                                   # lights-up open, never a black frame
    if fi >= 2: ctx.light = .30 * math.exp(-max(0, t - 2 / 30) / .06)
    P['zoom_blur'] = max(0, 1.2 * (1 - t / .2)) ** 1.5
    P['rgb'] = max(0, 10 * (1 - t / .24))
    k = 1 - (1 - clamp(t / .42)) ** 4
    z = lerp(1.55, 1.16, k) + .025 * eio((t - K.T_BOA) / .5) + .035 * eio((t - K.T_NAO) / .9)
    rot = lerp(-.03, 0, k)
    bb = lerp(14, 2.5, eo(t / .6))                                                 # rack focus: the room settles
    if t < .78: ctx.bg_img = K.soft(_sweep_bg(lerp(-300, 2500, eio(t / .75)), .85 * (1 - clamp((t - .58) / .2))), bb)
    else: ctx.bg_img = E.cached('A_plate_soft', lambda: K.soft(E.studio(), 2.5))
    # ---- cheese: wobble (cheap template zoom-shake) until the slash
    ch = clamp((t - K.T_FEI) / .06) if t < K.T_TE else 0.0
    if ch > 0:
        u = t - K.T_FEI
        z += .07 * E.back(clamp(u / .18), 2.6) - .07 * clamp(u / .18) + .03 * math.sin(u * 2 * math.pi * 2.6)
        rot += .028 * math.sin(u * 2 * math.pi * 3.1) * ch
        P['sat'] = 1.45; P['bright'] = 1.06
    if K.T_TE <= t:
        u = t - K.T_TE
        z += .035 * math.exp(-u / .08); rot += .012 * math.exp(-u / .05) * math.sin(u * 60)
        ctx.light = max(ctx.light, .32 * math.exp(-u / .055))
        P['rgb'] = max(P['rgb'], 9 * math.exp(-u / .07))
    cam.update(z=z, x=540, y=800, dx=0, dy=0, rot=rot)
    ctx.avatar.update(s=1.0, x=0, y=0)
    # ---- the sneaky sparkle on "en-"
    if K.T_ENFEITE - .02 <= t < K.T_FEI + .1:
        u = t - (K.T_ENFEITE - .02); k = E.back(clamp(u / .14), 2.4) * (1 - clamp((t - K.T_FEI) / .06))
        sp = sticker('✨', 120); s = .3 + .7 * k
        if k > .02: ctx.add('screen', K.scaled(sp.rotate(-12 + 25 * u, Image.BILINEAR, expand=True), s), 770, 560, alpha=min(1, k * 1.4))
    _cheese(ctx, t)
    special = {'ENFEITE.': _enfeite}
    K.captions(ctx, t, CAP, CAP_Y_A, special=special)
    _slash(ctx, t)

def _sticker_state(i, t):
    """(x, y, scale, rot, alpha, vx, vy) of sticker i at t (None if not visible)."""
    ch, x, y, size, rot, dl = STICKERS[i]
    t_in = K.T_FEI + dl
    if t < t_in: return None
    u = t - t_in
    s = E.back(clamp(u / .16), 2.8); a = clamp(u / .04)
    bob = 6 * math.sin(u * 9 + i)
    r = rot + 6 * math.sin(u * 7 + i * 2)
    th = _hit_time((x, y))
    if t < th: return (x, y + bob, s, r, a, 0.0, 0.0)
    v = t - th                                                     # swatted: along the slash + out of the frame
    vel = swat_vel((x, y))
    x2 = x + vel[0] * v; y2 = y + vel[1] * v + 1800 * v * v
    side = 1 if vel[0] > 0 else -1
    return (x2, y2 + bob, s * (1 - .3 * clamp(v / .18)), r + side * 1300 * v, a * (1 - clamp((v - .06) / .12)), vel[0] / 30, (vel[1] + 3600 * v) / 30)

FACE_C = np.array([540., 780.])
def swat_vel(p):
    """velocity (px/s) of a swatted sticker: mostly radially out of the frame (away from his face) + along the slash."""
    rd = np.array(p, float) - FACE_C; rd /= (np.linalg.norm(rd) + 1e-6)
    v = rd * 4200 + SL_D * 1900
    return v

def _wc():
    cx, cy, w_, h_ = _word_c(); return np.array([cx, cy])

def _hit_time(p):
    """when the slash head passes point p (projection on the slash direction)."""
    d = float(np.dot(np.array(p, float) - _wc(), SL_D))
    return K.T_TE + d / 26000

def _cheese(ctx, t):
    if t < K.T_FEI - .01 or t > K.T_TE + .5: return
    # glitter frame: pops in with an overshoot, twinkles, bursts outward when the slash passes
    u = t - K.T_FEI
    if u >= 0:
        th = K.T_TE + .01
        v = glitter_frame(int(t * 15) % 3)
        if t < th:
            s = 1 + .06 * (1 - E.back(clamp(u / .14), 2.2))
            ctx.add('screen', K.scaled(v, s), W / 2, H / 2, alpha=clamp(u / .05))
        else:
            q = t - th
            if q < .22:
                a = 1 - clamp(q / .2); grow = 1 + .5 * K.eo(q / .2)
                ctx.add('screen', K.scaled(v, grow), W / 2, H / 2, alpha=a)
    # WOW starburst
    if u >= .02:
        wx, wy, wr = WOW_POS; uu = u - .02
        th = _hit_time((wx, wy))
        im = wow(); s = E.back(clamp(uu / .18), 2.6)
        r = wr + 5 * math.sin(uu * 11)
        if t < th:
            img = im.rotate(r, Image.BILINEAR, expand=True)
            ctx.add('screen', K.scaled(img, .62 * s), wx, wy, alpha=clamp(uu / .04))
        else:
            q = t - th; vel = swat_vel((wx, wy)); side = 1 if vel[0] > 0 else -1
            if q < .2:
                img = im.rotate(r + side * 900 * q, Image.BILINEAR, expand=True)
                img = K.scaled(img, .62 * (1 - .3 * clamp(q / .2)))
                img, ox, oy = K.mblur(img, vel[0] / 60, (vel[1] + 3600 * q) / 60)
                ctx.add('screen', img, wx + vel[0] * q + ox, wy + vel[1] * q + 1800 * q * q + oy, alpha=1 - clamp((q - .06) / .12))
    for i in range(len(STICKERS)):
        stt = _sticker_state(i, t)
        if stt is None: continue
        x, y, s, r, a, vx, vy = stt
        if a <= .01 or s <= .01: continue
        ch, _, _, size, _, _ = STICKERS[i]
        img = sticker(ch, size).rotate(r, Image.BILINEAR, expand=True)
        img = K.scaled(img, s)
        ox = oy = 0.0
        if abs(vx) + abs(vy) > 2: img, ox, oy = K.mblur(img, vx * .5, vy * .5)
        ctx.add('screen', img, x + ox, y + oy, alpha=a)
    # glitter particles from the frame burst
    if t >= K.T_TE + .01:
        q = t - (K.T_TE + .01)
        if q < .45: _glitter_burst(ctx, q)

def _glitter_burst(ctx, q):
    r = np.random.default_rng(11); n = 90
    side = r.integers(0, 4, n); u = r.random(n)
    x0 = np.where(side == 0, u * W, np.where(side == 1, u * W, np.where(side == 2, FR_IN + 20, W - FR_IN - 20)))
    y0 = np.where(side == 0, FR_IN + 20, np.where(side == 1, H - FR_IN - 20, u * H))
    vx = (x0 - W / 2) * r.uniform(.6, 1.6, n) + r.normal(0, 200, n); vy = (y0 - H / 2) * r.uniform(.3, .9, n) + r.normal(0, 200, n)
    cols = [(255, 215, 90), (255, 120, 210), (140, 235, 255), (255, 255, 255)]
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(canvas)
    a = 1 - clamp(q / .42)
    for i in range(n):
        x = x0[i] + vx[i] * q * 1.4; y = y0[i] + vy[i] * q * 1.4 + 1600 * q * q
        rr = 2 + (i % 4)
        c = cols[i % 4]; d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=c + (int(255 * a),))
    ctx.add('screen', canvas, 0, 0, center=False)

def _enfeite(ctx, t, img, cx, cy, s, a):
    """the caption word ENFEITE: clean -> WordArt on -FEI- -> sliced in half by the slash -> clean, struck through."""
    if t < K.T_FEI:
        return False                                                  # normal engine look
    if t < K.T_TE:
        u = t - K.T_FEI
        wa = wordart('ENFEITE.', 112, 10)
        k = E.back(clamp(u / .16), 2.6); r = 4.5 * math.sin(u * 2 * math.pi * 2.8)
        im = K.scaled(wa.rotate(r, Image.BILINEAR, expand=True), .80 + .18 * k)
        ctx.add('screen', im, cx + 34, cy - 4, alpha=a)
        return True
    q = t - K.T_TE
    # the clean word underneath (muted: struck), pops back
    clean = E.word_img('ENFEITE.', 110, 'white')[0]
    clean = Image.merge('RGBA', (*Image.eval(clean.convert('RGB'), lambda v: int(v * .62)).split(), clean.getchannel('A')))
    ks = .9 + .1 * E.back(clamp(q / .14), 2.0)
    ctx.add('screen', K.scaled(clean, ks), cx, cy, alpha=a * clamp(q / .05))
    if q < .12:                                                       # the WordArt sliced along the slash, halves fall away
        wa = wordart('ENFEITE.', 112, 10); ww, wh = wa.size
        yy, xx = np.mgrid[0:wh, 0:ww].astype(np.float32)
        side = ((xx - ww / 2) * SL_N[0] + (yy - wh / 2) * SL_N[1]) > 0
        for sgn in (1, -1):
            msk = (side if sgn > 0 else ~side)
            half = wa.copy(); half.putalpha(Image.fromarray((np.asarray(wa.getchannel('A')) * msk).astype(np.uint8)))
            off = SL_N * sgn * (260 * q + 1400 * q * q) + SL_D * sgn * 300 * q
            rot = sgn * 70 * q
            im = half.rotate(rot, Image.BILINEAR, expand=True)
            ctx.add('screen', im, cx + off[0], cy + off[1] + 1500 * q * q, alpha=a * (1 - clamp(q / .12)) ** 1.5)
    return True

def _slash(ctx, t):
    """the clean LUMARC line: slash across the frame, then settles as ENFEITE's strikethrough."""
    if t < T_SLASH0 or t >= K.CUT1: return
    cx, cy, ww, wh = _word_c(); C = np.array([cx, cy])
    hd = slash_head(t); tl = slash_tail(t)
    far = 1500
    if t < T_STRIKE - .06:
        a_ = max(-far, tl if tl > -1e8 else -far); b_ = min(far, hd)
        if b_ <= -far: return
        lim = ww * .62
        if tl > -1e8:                                    # tail catches up, the line retracts onto the word
            k = clamp((t - (K.T_TE + .045)) / (T_STRIKE - .06 - K.T_TE - .045))
            a_ = lerp(-far, -lim, eo(k, 4)); b_ = lerp(far, lim, eo(k, 4)) if hd > far else min(b_, lerp(far, lim, eo(k, 4)))
        p0 = C + SL_D * a_; p1 = C + SL_D * b_
        wd = 14 if t < K.T_TE + .06 else lerp(14, 7, clamp((t - K.T_TE - .06) / .1))
        K.add_strokes(ctx, 'screen', [(tuple(p0), tuple(p1), 1.0, wd)], glow=20, glow_a=1.0, core=.95)
    else:                                                # rotate down to a horizontal strikethrough
        k = eo(clamp((t - (T_STRIKE - .06)) / .1), 3)
        ang = lerp(SL_ANG, 0.0, k); dvec = np.array([math.cos(ang), math.sin(ang)])
        half = lerp(ww * .62, ww * .56, k)
        yc = cy + lerp(0, 4, k)
        p0 = np.array([cx, yc]) - dvec * half; p1 = np.array([cx, yc]) + dvec * half
        K.add_strokes(ctx, 'screen', [(tuple(p0), tuple(p1), 1.0, 7)], glow=10, glow_a=.9, core=.6)

# ---- B: "Ela mostra o que você fala."
def _dolly(t):
    return K.eio5((t - 2.54) / .60)
def _doors(t):
    return K.eio5((t - (K.T_TRA - .05)) / .36)

def footprint_segs(fc, st, t, draw_k, alpha, phase=0.0, corner_k=1.0, flash=0.0, stake_k=0.0):
    """surveyor's dashed footprint of the lot top (y = 0) + corner L-markers + survey stakes, projected through fc."""
    L = HS.LOT; segs = []
    C = [(-L, 0, L), (L, 0, L), (L, 0, -L), (-L, 0, -L)]
    for e in range(4):
        p, q = np.array(C[e], float), np.array(C[(e + 1) % 4], float)
        k = clamp(draw_k * 4 - e) if draw_k < 1 else 1.0            # edges draw one after another
        if k <= 0: continue
        q2 = p + (q - p) * k
        for a3, b3 in K.dashes(p, q2, max(1, int(13 * k)), phase=phase, duty=.52):
            S, Z = K.project(fc, st, np.array([a3, b3]))
            if Z.min() > .3: segs.append((tuple(S[0]), tuple(S[1]), alpha * (.8 + .2 * flash), 3.4 + 2.4 * flash))
    if corner_k > 0:
        for i in range(4):
            c = np.array(C[i], float); n1 = np.array(C[(i + 1) % 4], float) - c; n2 = np.array(C[(i - 1) % 4], float) - c
            ln = 1.7 * corner_k
            for n in (n1, n2):
                S, Z = K.project(fc, st, np.array([c, c + n / np.linalg.norm(n) * ln]))
                if Z.min() > .3: segs.append((tuple(S[0]), tuple(S[1]), alpha, 5.0 + 2 * flash))
        S, Z = K.project(fc, st, np.array([[-0.8, 0, 0], [0.8, 0, 0], [0, 0, -0.8], [0, 0, 0.8]]))
        if Z.min() > .3:
            segs.append((tuple(S[0]), tuple(S[1]), alpha * .8 * corner_k, 3.0)); segs.append((tuple(S[2]), tuple(S[3]), alpha * .8 * corner_k, 3.0))
    if stake_k > 0:                                                   # survey stakes: posts with a glowing tip
        for i, c in enumerate(C):
            kk = E.back(clamp(stake_k * 1.6 - i * .2), 2.2)
            if kk <= 0: continue
            S, Z = K.project(fc, st, np.array([c, (c[0], 1.5 * kk, c[2])]))
            if Z.min() > .3:
                segs.append((tuple(S[0]), tuple(S[1]), alpha, 3.4))
                segs.append((tuple(S[1]), tuple(S[1] + .1), alpha, 11.0))
    return segs

def footprint_pad(ctx, fc, st, a, layer='behind'):
    """the plot catches the beam: a soft translucent light pad on the footprint."""
    if a <= .01: return
    L = HS.LOT
    S, Z = K.project(fc, st, np.array([(-L, 0, L), (L, 0, L), (L, 0, -L), (-L, 0, -L)]))
    if Z.min() < .3: return
    x0, y0 = S.min(0) - 30; x1, y1 = S.max(0) + 30
    w, h = int(x1 - x0), int(y1 - y0)
    if w < 4 or h < 4: return
    m = Image.new('L', (w // 2, h // 2)); ImageDraw.Draw(m).polygon([((p[0] - x0) / 2, (p[1] - y0) / 2) for p in S], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(6)).resize((w, h), Image.BILINEAR)
    im = Image.new('RGBA', (w, h), (150, 125, 255, 0)); im.putalpha(m.point(lambda v: int(v * .16 * a)))
    ctx.add(layer, im, x0, y0, center=False)

def light_pool(ctx, fc, st, a, r=5.2, layer='behind'):
    """the beam lands on the empty lot: a soft pool of violet-white light on the grass (only while the lot is empty)."""
    if a <= .01: return
    n = 40; ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    S, Z = K.project(fc, st, np.stack([r * np.cos(ang), np.full(n, .01), r * np.sin(ang)], 1))
    if Z.min() < .3: return
    ext = S.max(0) - S.min(0); pad = .22 * ext.max() + 8
    x0, y0 = S.min(0) - pad; x1, y1 = S.max(0) + pad; w, h = int(x1 - x0), int(y1 - y0)
    if w < 8 or h < 8: return
    m = Image.new('L', (w // 4, h // 4)); ImageDraw.Draw(m).polygon([((p[0] - x0) / 4, (p[1] - y0) / 4) for p in S], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(float(max(2, ext.max() / 4 * .07)))).resize((w, h), Image.BILINEAR)
    im = Image.new('RGBA', (w, h), (206, 192, 255, 0)); im.putalpha(m.point(lambda v: int(v * .22 * a)))
    ctx.add(layer, im, x0, y0, center=False)

D_STUDIO = (1.35, 540, 820)
D_GLOW = (540, 880, 640, (120, 90, 255), .55)
D_MOTES = dict(box=(40, 80, 1040, 1500), n=44, seed=9, beam=(540, 0, 900, 170, 700))

def _beam(ctx, t, cx, bottom, a, wt=150, wb=520):
    if a <= .01: return
    h = int(max(200, bottom + 60))
    b = K.beam_img(wt, wb, h, a_top=.42)
    ctx.add('behind', b, cx, h / 2 - 40, alpha=a)

def _shot_b(ctx, t, P):
    ctx.cam.update(z=1.0, x=540, y=960, dx=0, dy=0, rot=0)
    kd = _dolly(t)
    lt = t - K.CUT1
    s = lerp(1.32, TWO_F['s'], kd) + .02 * clamp(lt / .4) * (1 - kd)
    fx = 540; fy = lerp(862, TWO_F['fy'], kd)
    K.avatar_at(ctx, s, fx, fy)
    bz = lerp(1.30, 1.08, kd); bfy = lerp(640, 700, kd)
    ctx.bg_img = K.studio_view(bz, 540, bfy, glows=[(540, 700, 520, (120, 90, 255), .5 * clamp((t - 2.7) / .4))], blur=lerp(4.5, 2.5, kd))
    # the beam + motes in the revealed space
    ba = clamp((t - 2.66) / .35)
    fc = _fp_cam(t)
    st = HS.state_at(t)
    _beam(ctx, t, 540, 680, .85 * ba)
    K.motes(ctx, t, (90, 120, 990, 1050), n=36, seed=5, alpha=ba, beam=(540, 0, 700, 150, 520))
    # footprint draws on "o que você", stakes pop on "que", a pulse on "fala"
    dk = clamp((t - (K.T_O1 - .02)) / .40)
    if dk > 0:
        fl = math.exp(-max(0, t - K.T_FALA) / .16) if t >= K.T_FALA else 0.0
        footprint_pad(ctx, fc, st, dk * (1 + .8 * fl))
        segs = footprint_segs(fc, st, t, dk, 1.0, phase=(t * .6) % 1.0, corner_k=E.back(clamp((t - K.T_QUE) / .18), 2.0),
                              flash=.7 * fl, stake_k=clamp((t - K.T_VOCE) / .3))
        K.add_strokes(ctx, 'behind', segs, glow=9 + 6 * fl, glow_a=1.0)
    # MOSTRA doors
    _mostra(ctx, t, kd)
    if K.T_MOSTRA <= t < K.T_MOSTRA + .25: ctx.light = max(ctx.light, .30 * math.exp(-(t - K.T_MOSTRA) / .06))
    if lt < .1: ctx.light = max(ctx.light, .12 * (1 - lt / .1))
    K.captions(ctx, t, CAP_B, CAP_Y)

def _fp_cam(t):
    """frame camera of the footprint during the dolly (pushes in on it while he recedes) -> the two-shot camera."""
    kd = _dolly(t)
    base = two_cam(t, yaw=62 - 6 * clamp((t - 2.9) / 1.0))
    base['f'] = lerp(2050, 1680, kd); base['py'] = lerp(420, 505, kd); base['px'] = 520
    return base

def _mostra(ctx, t, kd):
    if t < K.T_MOSTRA - .04 or t > 3.12: return
    L, R, xs, w, h = mostra_halves()
    u = t - K.T_MOSTRA
    k = expo(clamp((u + .034) / .22))
    s = lerp(1.25, 1.0, k) * (1 - .06 * kd)
    op = _doors(t)                                                 # doors part on "-TRA"
    sp = 1 + .34 * op                                              # leaves swing toward the camera as they open
    gap = 780 * op
    cy = 545 + 110 * kd
    a = clamp((u + .034) / .07) * (1 - clamp((t - 3.0) / .1))
    for leaf, sgn in ((L, -1), (R, 1)):
        img = K.scaled(leaf, s * sp)
        lc = (leaf.width / 2 - w / 2) if sgn < 0 else (xs + leaf.width / 2 - w / 2)
        x = 540 + lc * s * sp + sgn * gap
        if 0 < op < 1:
            dv = 780 * (op - _doors(t - 1 / 60))
            if dv > 1.5: img, ox, oy = K.mblur(img, sgn * dv, 0); x += ox
        ctx.add('behind', img, x, cy, alpha=a)

# ---- C: "Olha só." — orbit + the lot rises into the footprint
def _orbit(t):
    return expo(clamp((t - K.CUT2) / .5))

def _shot_c(ctx, t, P):
    ctx.cam.update(z=1.0, x=540, y=960, dx=0, dy=0, rot=0)
    k = _orbit(t); lt = t - K.CUT2
    fx = lerp(800, 360, k); fy = 1255; s = 1.0
    K.avatar_at(ctx, s, fx, fy)
    K.desk_shade(ctx, 1.0, x=fx, lift=60)
    ctx.bg_img = K.studio_view(1.12, lerp(380, 640, k), 700, glows=[(lerp(520, 640, k), 720, 560, (120, 90, 255), .5)], blur=3.0)
    fc = K.fcam(lerp(74, 33, k) + 1.5 * math.sin(t * .23), 22 + 1.0 * math.sin(t * .17 + 1), 34.5, 1700, (0, 1.2, -0.3), lerp(540, 580, k), 565)
    st = HS.state_at(t)
    _beam(ctx, t, lerp(540, 580, k), 600, .85)
    K.motes(ctx, t, (90, 120, 990, 1080), n=36, seed=5, alpha=1.0, beam=(lerp(540, 580, k), 0, 700, 150, 520))
    K.house(ctx, t, fc, st=st)
    light_pool(ctx, fc, st, st['lot']['a'] * clamp((t - 3.95) / .3))
    # footprint: flashes as the lot arrives, locks on, then fades
    fl = math.exp(-max(0, t - K.T_SO) / .12) if t >= K.T_SO else 0.0
    fa = (1 - clamp((t - (K.T_SO + .05)) / .25))
    if fa > 0:
        segs = footprint_segs(fc, dict(st, lot=dict(a=1, dy=0, s=1)), t, 1.0, .95 * fa, phase=(t * .6) % 1.0, flash=fl)
        K.add_strokes(ctx, 'behind', segs, glow=8 + 8 * fl, glow_a=.9)
    if lt < .12:                                                     # whip: horizontal smear on the first frames
        sm = (1 - lt / .12) ** 1.5
        P['rgb'] = 5 * sm
        ctx.wrap = (lambda fr, sm=sm: _hsmear(fr, sm))
    if t >= K.T_SO: ctx.cam['dy'] = 0
    K.captions(ctx, t, CAP_C, CAP_Y)

def _hsmear(fr, k):
    small = fr.convert('RGB').resize((W // 14, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    return Image.blend(fr.convert('RGB'), small, min(.85, k)).convert('RGBA')

# ---- D: silent beat — the empty lot alone
def _shot_d(ctx, t, P):
    ctx.cam.update(z=1.0, x=540, y=960, dx=0, dy=0, rot=0)
    ctx.avatar['show'] = False
    ctx.bg_img = K.studio_view(*D_STUDIO, glows=[D_GLOW], blur=7.0, dim=.18)
    fc = lot_close_cam(t)
    _beam(ctx, t, 540, 860, .95, wt=170, wb=700)
    K.motes(ctx, t, D_MOTES['box'], n=D_MOTES['n'], seed=D_MOTES['seed'], alpha=1.0, beam=D_MOTES['beam'])
    st, _ = K.house(ctx, t, fc)
    light_pool(ctx, fc, st, 1.0)
    ctx.captions = False
