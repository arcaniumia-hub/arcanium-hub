"""s04 — PINCEL (22.20–28.00).  "Um pincel não pinta um quadro sozinho. A IA é a ferramenta. A diferença tá em quem usa."

SET  A primed canvas on a walnut French box easel stands on the desk in the foreground (left), the founder sits beside
     it (right; the easel hides the take's left edge).  The set is drawn in world space at 2x and filmed by a virtual
     camera (canvas/easel at native resolution even in macro; parallax: the studio moves less than the founder, the
     founder less than the easel).  The photoreal brush = src/assets/brush_green.png keyed with E.key, light-matched,
     soft shadow on the canvas, smeared motion blur; the stock photo's printed handle text is retouched away.
SHOT A (22.20 JUMP) whip-pan (edge-clamped motion blur) onto the two-shot.  "Um PINCEL" (22.44): the brush drops into
     frame and hovers in front of the blank canvas (bob, shadow on the canvas).  "não PINTA" (23.28): it leans in until
     its tip touches the canvas (shadow meets the tip)… nothing… backs off.  "soZInho" (24.00/24.07 two dying twitches,
     24.13): the 'magic' dies, it tips over and clatters onto the ledge (24.33 'knock'), crickets.
SHOT B (24.48 JUMP) macro punch-in (Z≈3.3, Dutch roll 7°, shallow DOF, slow dolly) on the brush lying on the ledge.
     "IA" (24.66): a dot pings on the ferrule, a leader line draws up to a glass chip "IA".  "FERRAMENTA" (25.29): a
     design-tool selection box with handles draws around the brush, a specular glint runs along it and a wrench glyph
     slides into the chip ("IA" = the tool).
SHOT C (26.24 JUMP) the canvas fills the frame.  "DIFERENÇA" (26.40): the brush springs up into the middle of the
     canvas with a spin, hangs, then dashes off and paints five bold gestural strokes (26.55–27.32) — wet
     LUMARC-gradient paint at the stroke head that dries into the LUMARC croissant film still under the stroke mask
     (bristle streaks, impasto relief, combed dry-brush edges, dry-brush tails; the five strokes overlap so the
     finished canvas is fully covered).  "QUEM" (27.28): the last stroke lands and the
     LUMARC signature writes on in the corner ('shing'); the brush lands back on the ledge; "USA" (27.50) a varnish
     glint sweeps the painting while the camera pulls back to the two-shot: the founder beside the finished painting.
Captions: own word pops (engine look) on onsets measured on src/tight16k.raw (shot A at the top, over the dark wall).
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _B_kit as K

START, END = E.span(8, 10)                    # 22.20 – 28.00
T9, T10 = E.TL[9]['t0'], E.TL[10]['t0']       # 24.48, 26.24 (both JUMP)
W, H = E.W, E.H
clamp, eout, ein, back, lerp, smooth, expo, sio = K.clamp, K.eout, K.ein, K.back, K.lerp, K.smooth, K.expo, K.sio

# word onsets measured on src/tight16k.raw (5 ms spectrogram + low/high band envelopes, see out/B/spec8-10.png)
O = dict(UM=22.30, PINCEL=22.44, NAO=22.93, PINTA=23.28, UM2=23.60, QUADRO=23.66, SOZINHO=23.89, ZI=24.13, SOZ_END=24.37,
         A=24.57, IA=24.66, E=24.93, A2=25.12, FERRAMENTA=25.29, MEN=25.72, FERR_END=26.10,
         A3=26.28, DIFERENCA=26.40, TA=26.96, EM=27.08, QUEM=27.28, USA=27.50, USA_END=27.78)

T_DROPIN = O['PINCEL'] - .10           # brush drops into frame
T_FALL = O['ZI']                       # the hover dies
T_LAND = T_FALL + .20                  # clatters onto the ledge
T_WAKE = O['DIFERENCA']                # the brush springs up
# five strokes (start, end) — the last one lands on "QUEM"
STROKE_T = [(26.55, 26.70), (26.72, 26.87), (26.89, 27.03), (27.05, 27.17), (27.19, O['QUEM'] + .04)]
T_SIGN = O['QUEM'] + .02
T_PULL = O['USA'] - .04

CUES = [
    (START, 'whoosh', {'gain': -9, 'pan': -.3}),        # whip-pan onto the two-shot
    (T_DROPIN, 'swoosh_up', {'gain': -14}),             # brush drops in
    (O['PINCEL'] + .02, 'pop', {'gain': -12}),          # …and settles into its hover
    (O['PINTA'] + .02, 'tick', {'gain': -16}),          # leans in to paint… nothing
    (24.00, 'flick', {'gain': -14}),                    # twitch
    (T_LAND, 'knock', {'gain': -6}),                    # clatters onto the ledge
    (T_LAND + .09, 'knock', {'gain': -14}),             # small bounce
    (T_LAND + .06, 'crickets', {'dur': .55, 'gain': -15}),
    (T9, 'zoom', {'gain': -10}),                        # macro punch-in
    (O['IA'] - .02, 'tick', {'gain': -10}),             # dot pings on the ferrule
    (O['IA'] + .02, 'pop', {'gain': -6}),               # "IA" chip
    (O['FERRAMENTA'], 'swipe', {'gain': -12}),          # selection box draws
    (O['FERRAMENTA'] + .10, 'click', {'gain': -12}),    # wrench glyph
    (T10, 'whoosh', {'gain': -9}),                      # cut to the canvas
    (T_WAKE, 'swoosh_up', {'gain': -5}),                # the brush springs up
] + [((a + b) / 2 - .03, 'swoosh', {'gain': -5 - 2 * (i % 2), 'pan': (-.4 if i % 2 == 0 else .4)}) for i, (a, b) in enumerate(STROKE_T)] + [
    (T_SIGN, 'shing', {'gain': -3}),                    # LUMARC signature
    (STROKE_T[-1][1] + .22, 'knock', {'gain': -15}),    # the brush lands back on the ledge
    (O['USA'], 'shimmer', {'gain': -9}),                # varnish glint
    (T_PULL, 'whoosh', {'gain': -13}),                  # pull back to the two-shot
]

# ---------------------------------------------------------------- captions (measured onsets)
PAGES = [
    (O['UM'] - .04, O['NAO'] - .02, [('UM', O['UM'], False), ('PINCEL', O['PINCEL'], True)]),
    (O['NAO'] - .02, O['UM2'] - .02, [('NÃO', O['NAO'], False), ('PINTA', O['PINTA'], False)]),
    (O['UM2'] - .02, O['SOZINHO'] - .02, [('UM', O['UM2'], False), ('QUADRO', O['QUADRO'], False)]),
    (O['SOZINHO'] - .02, T9, [('SOZINHO.', O['SOZINHO'], False)]),
    (O['A'] - .04, O['FERRAMENTA'] - .02, [('A', O['A'], False), ('IA', O['IA'], False), ('É', O['E'], False), ('A', O['A2'], False)]),
    (O['FERRAMENTA'] - .02, T10, [('FERRAMENTA.', O['FERRAMENTA'], True)]),
    (O['A3'] - .04, O['TA'] - .02, [('A', O['A3'], False), ('DIFERENÇA', O['DIFERENCA'], False)]),
    (O['TA'] - .02, END, [('TÁ', O['TA'], False), ('EM', O['EM'], False), ('QUEM', O['QUEM'], True), ('USA.', O['USA'], True)]),
]

# ================================================================ the set (world px; avatar at s=1, x=+AV_X)
AV_X = 262.
CV = (70., 790., 500., 700.)            # canvas face x, y, w, h
SIDE = 16.                              # stretcher depth seen on the right
LEDGE = (40., 1490., 604., 1532.)
BOXR = (100., 1532., 544., 1920.)
MAST = (303., 628., 337., 800.)
CLAMP = (272., 768., 368., 806.)
SX0, SY0, SX1, SY1 = 0, 560, 680, 1920   # region of the set image
SS = 2                                    # set image scale (px per world px)


def _noise(shape, scale, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((max(2, shape[0] // scale + 2), max(2, shape[1] // scale + 2))).astype(np.float32)
    return np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC), np.float32) / 255


def canvas_base():
    """blank primed canvas face at 2x (1000x1400): warm gesso + linen weave, lit like a gallery piece in a dark room —
    a soft key from the top-left with real falloff, violet bounce from the monitors (right) and the desk (bottom)."""
    def mk():
        w, h = int(CV[2] * SS), int(CV[3] * SS)
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        weave = (np.sin(x * 2 * math.pi / 4.2) * .5 + np.sin(y * 2 * math.pi / 4.6) * .5)
        weave = weave * (.6 + .4 * _noise((h, w), 3, 1)) * 2.4
        gesso = (_noise((h, w), 60, 2) - .5) * 6 + (_noise((h, w), 9, 3) - .5) * 3.5
        u, v = x / w, y / h
        d = np.sqrt(((u - .30) / 1.0) ** 2 + ((v - .18) / 1.05) ** 2)
        L = .96 - .52 * np.clip(d, 0, 1.25) ** 1.35
        base = np.array([232, 227, 218], np.float32)
        rgb = base * L[..., None] + (weave + gesso)[..., None] * (.5 + .5 * L[..., None])
        bounce_r = np.clip((u - .70) / .30, 0, 1) ** 2 * (.5 + .5 * v)
        bounce_b = np.clip((v - .78) / .22, 0, 1) ** 2
        rgb = rgb + bounce_r[..., None] * np.array([16, -10, 46], np.float32) + bounce_b[..., None] * np.array([-6, -10, 18], np.float32)
        e = np.minimum.reduce([x, y, w - 1 - x, h - 1 - y]) / 7
        rgb = rgb * (.78 + .22 * np.clip(e, 0, 1))[..., None]
        return np.clip(rgb, 0, 255).astype(np.float32)
    return K.C('canvas_base2', mk)


def walnut(w, h, seed, vertical=False, dark=1.0):
    """dark walnut with fine grain (RGB float), lit from the top-left."""
    def mk():
        ww, hh = (h, w) if vertical else (w, h)
        rng = np.random.default_rng(seed)
        n = rng.random((hh // 3 + 2, ww // 90 + 2)).astype(np.float32)
        g = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((ww, hh), Image.BICUBIC), np.float32) / 255
        fine = rng.random((hh, 1)).astype(np.float32); fine = np.repeat(fine, ww, 1)
        fine = np.asarray(Image.fromarray((fine * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8)), np.float32) / 255
        grain = .55 * g + .45 * fine
        c0 = np.array([66, 42, 30], np.float32); c1 = np.array([34, 21, 16], np.float32)
        rgb = c1 + (c0 - c1) * grain[..., None]
        if vertical: rgb = rgb.transpose(1, 0, 2)
        return rgb * dark
    return K.C(('walnut', w, h, seed, vertical, dark), mk)


def set_image(canvas_rgb=None):
    """the whole easel set (world region SX0..SX1 x SY0..SY1 at SS) as RGBA; canvas face = canvas_rgb (float h,w,3)."""
    def static():
        w, h = (SX1 - SX0) * SS, (SY1 - SY0) * SS
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        def R(x0, y0, x1, y1): return ((x0 - SX0) * SS, (y0 - SY0) * SS, (x1 - SX0) * SS - 1, (y1 - SY0) * SS - 1)
        def wood(rect, seed, vertical=False, light=(1.0, .55), rim=True, dark=1.0):
            x0, y0, x1, y1 = rect; ww, hh = int((x1 - x0) * SS), int((y1 - y0) * SS)
            rgb = walnut(ww, hh, seed, vertical, dark).copy()
            yy = np.linspace(0, 1, hh, dtype=np.float32)[:, None, None]; xx = np.linspace(0, 1, ww, dtype=np.float32)[None, :, None]
            rgb = rgb * (light[0] + (light[1] - light[0]) * yy) * (1.06 - .16 * xx)
            if rim: rgb = rgb + np.clip((xx - .94) / .06, 0, 1) * np.array([70, 40, 140], np.float32) * .8
            rgb[:, :max(1, SS)] *= .6; rgb[:max(1, SS)] = rgb[:max(1, SS)] * .7 + 30
            im.alpha_composite(Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA'), (int((x0 - SX0) * SS), int((y0 - SY0) * SS)))
        # soft cast shadow of the canvas towards the founder (key from the left)
        sh = Image.new('L', (w, h)); ImageDraw.Draw(sh).rectangle(R(CV[0] + 40, CV[1] + 30, CV[0] + CV[2] + 70, LEDGE[3]), fill=255)
        sh = sh.filter(ImageFilter.GaussianBlur(40 * SS)).point(lambda v: int(v * .42))
        shi = Image.new('RGBA', (w, h), (4, 3, 10, 0)); shi.putalpha(sh); im.alpha_composite(shi)
        # mast (above the canvas)
        wood(MAST, 5, vertical=True, light=(.75, 1.0))
        d.rounded_rectangle(R(MAST[0] - 5, MAST[1] - 9, MAST[2] + 5, MAST[1] + 5), 3 * SS, fill=(40, 26, 20, 255))
        # box easel (French easel box) + drawer seam + brass pull
        wood(BOXR, 7, light=(.95, .40))
        bx0, by0, bx1, by1 = BOXR
        d.line([((bx0 - SX0) * SS, (1700 - SY0) * SS), ((bx1 - SX0) * SS, (1700 - SY0) * SS)], fill=(14, 9, 8, 255), width=2 * SS)
        d.line([((bx0 - SX0) * SS, (1701 - SY0) * SS), ((bx1 - SX0) * SS, (1701 - SY0) * SS)], fill=(92, 64, 48, 255), width=1 * SS)
        d.rounded_rectangle(R(300, 1608, 344, 1622), 4 * SS, fill=(150, 118, 64, 255))
        d.rounded_rectangle(R(300, 1608, 344, 1612), 2 * SS, fill=(212, 182, 120, 255))
        for cx_ in (bx0 + 14, bx1 - 14):                                    # brass corner plates
            d.rectangle(R(cx_ - 8, by0 + 6, cx_ + 8, by0 + 22), fill=(120, 94, 54, 255))
        # ledge (canvas tray)
        lx0, ly0, lx1, ly1 = LEDGE
        wood((lx0, ly0 + 9, lx1, ly1), 9, light=(1.0, .7))
        wood((lx0, ly0, lx1, ly0 + 9), 10, light=(1.5, 1.3), rim=False)
        d.rectangle(R(lx0, ly1 - 3, lx1, ly1), fill=(10, 8, 8, 255))
        # ledge -> box contact shadow
        cs = Image.new('L', (w, h)); ImageDraw.Draw(cs).rectangle(R(bx0, ly1, bx1, ly1 + 26), fill=255)
        cs = cs.filter(ImageFilter.GaussianBlur(9 * SS)).point(lambda v: int(v * .7))
        csi = Image.new('RGBA', (w, h), (0, 0, 0, 0)); csi.putalpha(cs); im.alpha_composite(csi)
        # canvas side (stretcher depth, slight perspective): raw linen in shadow
        x1 = CV[0] + CV[2]
        side = [((x1 - SX0) * SS, (CV[1] - SY0) * SS), ((x1 + SIDE - SX0) * SS, (CV[1] + 7 - SY0) * SS),
                ((x1 + SIDE - SX0) * SS, (CV[1] + CV[3] - 2 - SY0) * SS), ((x1 - SX0) * SS, (CV[1] + CV[3] - SY0) * SS)]
        d.polygon(side, fill=(96, 86, 104, 255))
        d.line([side[1], side[2]], fill=(140, 110, 210, 255), width=2 * SS)
        # canvas-on-ledge contact shadow
        cs = Image.new('L', (w, h)); ImageDraw.Draw(cs).rectangle(R(CV[0], LEDGE[1] - 2, CV[0] + CV[2] + SIDE, LEDGE[1] + 8), fill=255)
        cs = cs.filter(ImageFilter.GaussianBlur(3 * SS)).point(lambda v: int(v * .8))
        csi = Image.new('RGBA', (w, h), (0, 0, 0, 0)); csi.putalpha(cs); im.alpha_composite(csi)
        return im
    st = K.C('set_static', static)
    im = st.copy()
    c = canvas_rgb if canvas_rgb is not None else canvas_base()
    cim = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)).convert('RGBA')
    im.alpha_composite(cim, (int((CV[0] - SX0) * SS), int((CV[1] - SY0) * SS)))
    # clamp over the canvas top edge
    def clamp_img():
        x0, y0, x1, y1 = CLAMP; ww, hh = int((x1 - x0) * SS), int((y1 - y0) * SS)
        rgb = walnut(ww, hh, 12).copy() * np.linspace(1.3, .7, hh, dtype=np.float32)[:, None, None]
        out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
        dd = ImageDraw.Draw(out); dd.rectangle((0, 0, ww, 2 * SS), fill=(120, 90, 70, 255)); dd.rectangle((ww - 3 * SS, 0, ww, hh), fill=(100, 70, 160, 255))
        dd.ellipse((ww / 2 - 6 * SS, hh / 2 - 6 * SS, ww / 2 + 6 * SS, hh / 2 + 6 * SS), fill=(160, 128, 70, 255))
        return out
    cl = K.C('clamp_img', clamp_img)
    sh = K.soft_shadow(cl.width, cl.height, 4, 8, .5, 20)
    im.alpha_composite(sh, (int((CLAMP[0] - SX0) * SS) - 20 + 4, int((CLAMP[1] - SY0) * SS) - 20 + 10))
    im.alpha_composite(cl, (int((CLAMP[0] - SX0) * SS), int((CLAMP[1] - SY0) * SS)))
    return im


def set_static_canvas():
    return K.C('set_blank', lambda: set_image(None))


# ================================================================ virtual camera
class VCam:
    """world -> screen: s + (p - c) * Z for the easel (then rolled by `roll` deg about the frame centre); the founder
    and the studio use damped zooms (parallax)."""
    REF = (372. - 330., 1062. - 1130.)       # shot A mapping offset (background at rest)
    def __init__(self, Z, c, s=(540., 960.), roll=0.):
        self.Z, self.c, self.s, self.roll = Z, c, s, roll
        self.Za = 1 + (Z - 1) * .93
        self.Zb = 1.08 + (Z - 1) * .55
        r = math.radians(roll); self.cr, self.sr = math.cos(r), math.sin(r)
    def P(self, x, y, z=None):
        z = z or self.Z; X, Y = self.s[0] + (x - self.c[0]) * z, self.s[1] + (y - self.c[1]) * z
        if self.roll:
            dx, dy = X - 540, Y - 960; X, Y = 540 + dx * self.cr + dy * self.sr, 960 - dx * self.sr + dy * self.cr
        return X, Y


def apply_cam(ctx, cam, blur_bg=6., dim=0.0, set_img=None, set_soft=0.):
    """studio, founder and the easel set through the virtual camera."""
    ctx.cam = dict(z=1.0, x=540., y=960., dx=0., dy=0., rot=0.)
    mx, my = (cam.Zb - 1) * 540 - 2, (cam.Zb - 1) * 760 - 2
    px = max(-mx, min(mx, .30 * ((cam.s[0] - cam.c[0]) - VCam.REF[0])))
    py = max(-my, min(my, .30 * ((cam.s[1] - cam.c[1]) - VCam.REF[1])))
    ctx.bg_img = K.studio_at(cam.Zb, (540., 760.), (px, py), blur=blur_bg, dim=dim)
    # founder: bottom-centre of the take (540+AV_X, H) through the camera
    bx, by = cam.P(540 + AV_X, H, cam.Za)
    show = (bx - 540 * cam.Za < W + 10) and not cam.roll
    ctx.avatar.update(show=show, s=cam.Za, x=bx - 540, y=by - H)
    # the set: crop the visible world rect from the 2x set image, scale to screen
    grow = 1.0 if not cam.roll else 1.0 + abs(cam.sr) * 1.9
    hw, hh = W / 2 * grow / cam.Z, H / 2 * grow / cam.Z
    wcx, wcy = cam.c[0] + (540 - cam.s[0]) / cam.Z, cam.c[1] + (960 - cam.s[1]) / cam.Z
    x0w, y0w, x1w, y1w = wcx - hw, wcy - hh, wcx + hw, wcy + hh
    ax0, ay0, ax1, ay1 = max(SX0, x0w), max(SY0, y0w), min(SX1, x1w), min(SY1, y1w)
    if ax1 <= ax0 or ay1 <= ay0: return
    im = set_img or set_static_canvas()
    box = ((ax0 - SX0) * SS, (ay0 - SY0) * SS, (ax1 - SX0) * SS, (ay1 - SY0) * SS)
    sx0, sy0 = cam.s[0] + (ax0 - cam.c[0]) * cam.Z, cam.s[1] + (ay0 - cam.c[1]) * cam.Z
    sx1, sy1 = cam.s[0] + (ax1 - cam.c[0]) * cam.Z, cam.s[1] + (ay1 - cam.c[1]) * cam.Z
    tw, th = max(1, int(round(sx1 - sx0))), max(1, int(round(sy1 - sy0)))
    if set_soft > .3:
        crop = im.resize((max(1, int(tw / set_soft)), max(1, int(th / set_soft))), Image.BILINEAR, box=box).resize((tw, th), Image.BILINEAR)
    else:
        crop = im.resize((tw, th), Image.BILINEAR, box=box)
    if cam.roll:
        # rotate about the frame centre: paste into a padded canvas centred on the frame centre, rotate, crop
        pw, ph = int(W * grow) + 4, int(H * grow) + 4
        canvas = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
        ox, oy = (pw - W) // 2, (ph - H) // 2
        canvas.alpha_composite(crop, (int(round(sx0)) + ox, int(round(sy0)) + oy)) if sx0 + ox >= 0 and sy0 + oy >= 0 else canvas.paste(crop, (int(round(sx0)) + ox, int(round(sy0)) + oy), crop)
        rot = canvas.rotate(cam.roll, Image.BICUBIC, center=(540 + ox, 960 + oy))
        ctx.add('front', rot.crop((ox, oy, ox + W, oy + H)), 0, 0, center=False)
        return
    ctx.add('front', crop, int(round(sx0)), int(round(sy0)), center=False)


# ================================================================ the brush (keyed photo, light-matched)
BR_TIP = (29., 940.); BR_END = (990., 44.)
BR_ANG = math.degrees(math.atan2(BR_TIP[1] - BR_END[1], BR_END[0] - BR_TIP[0]))     # ≈ 43° (handle up-right)
BR_LEN = 440.                                                                       # world length (px)


def brush_base():
    """horizontal keyed brush (tip at left), light-matched to the dark violet set -> (RGBA, tip_xy, length_px)."""
    def mk():
        src = Image.open(os.path.join(E.ASSETS, 'brush_green.png')).convert('RGB')
        rgb, al = E.key(src)
        # the stock photo prints 'ARTIST BRUSH', a leaf mark and a size number in gold on the handle: mask them
        a0 = np.asarray(src, np.float32); r_, g_, b_ = a0[..., 0], a0[..., 1], a0[..., 2]
        txt = np.zeros(al.shape, bool); txt[230:480, 520:770] = True
        txt &= (r_ > 52) & (r_ > b_ + 14) & (r_ > g_ - 4)
        txt &= (al > .9)
        tm = Image.fromarray((txt * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
        rgb = rgb * np.array([.86, .84, .92], np.float32) + np.array([2, 0, 8], np.float32)
        im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8), 'RGBA')
        im = im.rotate(-BR_ANG, Image.BICUBIC, expand=True)
        tm = np.asarray(tm.rotate(-BR_ANG, Image.BILINEAR, expand=True), np.float32) / 255
        if tm.any():          # fill along the (now horizontal) handle: lacquer shading is constant along its length
            a = np.asarray(im, np.float32); ok = (1 - tm) * (a[..., 3] > 240)
            from scipy.ndimage import uniform_filter1d
            num = uniform_filter1d(a[..., :3] * ok[..., None], 81, axis=1); den = uniform_filter1d(ok, 81, axis=1)[..., None]
            fill = num / np.maximum(den, 1e-3); m = np.clip(tm * 1.6, 0, 1)[..., None]
            a[..., :3] = a[..., :3] * (1 - m) + fill * m
            im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
        # find the tip / end in the rotated image
        a = np.asarray(im.getchannel('A'))
        ys, xs = np.where(a > 100)
        x0, x1 = xs.min(), xs.max(); y0, y1 = ys.min(), ys.max()
        im = im.crop((x0 - 4, y0 - 4, x1 + 5, y1 + 5))
        a = np.asarray(im.getchannel('A')); ys, xs = np.where(a > 100)
        tipx = xs.min(); tipy = float(ys[xs == tipx].mean())
        return im, (float(tipx), tipy), float(xs.max() - tipx)
    return K.C('brush_base2', mk)


def brush_img(length, ang, glint=None):
    """brush of `length` px with its handle pointing at screen angle `ang` (deg, counter-clockwise from +x);
    glint = position (0..1 along the brush) of a specular sweep.  -> (RGBA, tip_xy_in_img)."""
    base, (tx, ty), L = brush_base()
    s = length / L
    im = base.resize((max(1, int(base.width * s)), max(1, int(base.height * s))), Image.BICUBIC)
    tx, ty = tx * s, ty * s
    if glint is not None and -.2 < glint < 1.2:
        a = np.asarray(im, np.float32)
        xs = np.arange(im.width, dtype=np.float32)[None, :]; ys = np.arange(im.height, dtype=np.float32)[:, None]
        band = np.exp(-((xs - (tx + glint * length) - (ys - ty) * .6) / (length * .035)) ** 2)
        top = np.clip(1 - np.abs(ys - (ty - im.height * .12)) / (im.height * .28), 0, 1)
        k = (band * (.35 + .65 * top) * .75)[..., None]
        a[..., :3] = a[..., :3] + (255 - a[..., :3]) * k
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    cx, cy = im.width / 2, im.height / 2
    rot = im.rotate(ang, Image.BICUBIC, expand=True)
    a = math.radians(ang); vx, vy = tx - cx, ty - cy
    rx = vx * math.cos(a) + vy * math.sin(a); ry = -vx * math.sin(a) + vy * math.cos(a)
    return rot, (rot.width / 2 + rx, rot.height / 2 + ry)


def brush_shadow(im, blur, op):
    a = im.getchannel('A').filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op))
    sh = Image.new('RGBA', im.size, (8, 6, 16, 0)); sh.putalpha(a); return sh


def add_brush(ctx, tip, ang, length, shadow=None, layer='front', blur_v=None, alpha=1.0, glint=None):
    """tip = screen xy of the bristle tip; shadow = (dx, dy, blur, opacity) in screen px."""
    im, (tx, ty) = brush_img(length, ang, glint)
    if shadow is not None:
        dx, dy, bl, op = shadow
        pad = int(bl * 2)
        big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); big.alpha_composite(im, (pad, pad))
        ctx.add(layer, brush_shadow(big, bl, op), tip[0] - tx - pad + dx, tip[1] - ty - pad + dy, center=False, alpha=alpha)
    if blur_v is not None and math.hypot(*blur_v) > 6:
        # motion blur: one smeared copy (several offsets composited into a single image) behind the sharp brush
        sp = math.hypot(*blur_v); n = int(min(18, max(5, sp / 5)))
        pad = int(sp * .75) + 4
        sm = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        acc = np.zeros((sm.height, sm.width, 4), np.float32)
        src = np.asarray(im, np.float32); src[..., :3] *= src[..., 3:] / 255          # premultiplied
        for g in range(n):
            f = (g + 1) / n * .75
            ox, oy = int(round(pad - blur_v[0] * f)), int(round(pad - blur_v[1] * f))
            acc[oy:oy + im.height, ox:ox + im.width] += src
        acc /= n
        acc[..., :3] /= np.maximum(acc[..., 3:], 1) / 255
        sm = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8), 'RGBA')
        ctx.add(layer, sm, tip[0] - tx - pad, tip[1] - ty - pad, center=False, alpha=.85 * alpha)
    ctx.add(layer, im, tip[0] - tx, tip[1] - ty, center=False, alpha=alpha)


# ---------------------------------------------------------------- brush choreography (world coords)
HOVER_TIP = (318., 1300.)
HOVER_ANG = 72.
REST_TIP = (128., 1478.)                 # lying on the ledge, tip left
REST_ANG = 3.0


def lean_k(t):
    """'não PINTA': the brush leans in until its tip touches the canvas (shadow meets the tip)… nothing… backs off."""
    u = (t - O['PINTA'] + .06) / .62
    if not 0 <= u < 1: return 0.
    return smooth(u / .3) if u < .55 else 1 - smooth((u - .55) / .45)


def brush_pose_A(t):
    """-> (tip world xy, ang, alpha) for shot A."""
    if t < T_DROPIN: return None
    if t < O['PINCEL'] + .10:                                         # drops in from above, overshoots, settles
        u = (t - T_DROPIN) / (O['PINCEL'] + .10 - T_DROPIN)
        y = lerp(HOVER_TIP[1] - 760, HOVER_TIP[1], back(u, 1.6)); return (HOVER_TIP[0], y), HOVER_ANG - 14 * (1 - eout(u)), 1.0
    bob = 7 * math.sin((t - O['PINCEL']) * 2 * math.pi * 1.1); sway = 2.2 * math.sin((t - O['PINCEL']) * 2 * math.pi * .7)
    x, y, ang = HOVER_TIP[0], HOVER_TIP[1] + bob, HOVER_ANG + sway
    # "não PINTA um quadro": leans in towards the canvas… and backs off
    k = lean_k(t)
    y += 34 * k; x += 10 * k; ang -= 9 * k
    # twitch before falling
    for tj, aj in ((24.00, 11.), (24.07, -8.)):                       # two dying twitches
        v = (t - tj) / .06
        if 0 <= v < 1: ang += aj * math.sin(math.pi * v); x += aj * .5 * math.sin(math.pi * v)
    if t >= T_FALL:                                                   # gravity: tips over and falls onto the ledge
        u = clamp((t - T_FALL) / (T_LAND - T_FALL))
        fy = lerp(y, REST_TIP[1], u * u); fx = lerp(x, REST_TIP[0], eout(u))
        fang = lerp(ang, REST_ANG - 4, ein(u))
        if t >= T_LAND:                                               # small bounce + settle
            v = (t - T_LAND)
            b = 14 * math.exp(-v * 18) * abs(math.sin(v * 34))
            fx, fy, fang = REST_TIP[0], REST_TIP[1] - b, REST_ANG + 4 * math.exp(-v * 14) * math.cos(v * 40)
        return (fx, fy), fang, 1.0
    return (x, y), ang, 1.0


# ================================================================ paint (shot C)
STROKES = [  # canvas px at 1x (500x700): bezier p0, c1, c2, p1, half-width (spaced ~142 px apart, overlapping)
    ((-45, 66), (150, -22), (330, 150), (545, 58), 132),
    ((545, 212), (330, 272), (170, 152), (-45, 206), 124),
    ((-45, 357), (160, 296), (340, 432), (545, 342), 122),
    ((545, 500), (320, 548), (170, 448), (-45, 516), 120),
    ((-45, 650), (180, 600), (330, 690), (545, 626), 122),
]
PAINT_SCALE = 1.0                        # maps are computed at 1x and upsampled to 2x


def bez(p0, c1, c2, p1, u):
    a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; c = 3 * (1 - u) * u * u; d = u ** 3
    return (a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1])


def stroke_u(t, i):
    a, b = STROKE_T[i]; return sio((t - a) / (b - a))


def paint_maps():
    """per-pixel paint data at 2x (1000x1400): first/last stroke time, alpha and relief."""
    cache = os.path.join(E.OUT, 'B', 'cache'); os.makedirs(cache, exist_ok=True)
    fn = os.path.join(cache, 'paint_v9.npz')
    def mk():
        if os.path.exists(fn):
            z = np.load(fn); return {k: z[k] for k in z.files}
        from scipy.spatial import cKDTree
        w1, h1 = int(CV[2]), int(CV[3]); w2, h2 = w1 * SS, h1 * SS
        yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32) / SS
        P = np.stack([xx.ravel(), yy.ravel()], 1)
        T1 = np.full(h2 * w2, np.inf, np.float32); A1 = np.zeros(h2 * w2, np.float32); R1 = np.ones(h2 * w2, np.float32)
        T2 = np.full(h2 * w2, np.inf, np.float32); A2 = np.zeros(h2 * w2, np.float32); R2 = np.ones(h2 * w2, np.float32)
        for i, (p0, c1, c2, p1, hw) in enumerate(STROKES):
            n = 900; us = np.linspace(0, 1, n)
            pts = np.array([bez(p0, c1, c2, p1, u) for u in us], np.float32)
            tan = np.gradient(pts, axis=0); tan /= np.linalg.norm(tan, axis=1, keepdims=True) + 1e-6
            nrm = np.stack([-tan[:, 1], tan[:, 0]], 1)
            seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); arc = np.concatenate([[0], np.cumsum(seg)]); arc /= arc[-1]
            tree = cKDTree(pts)
            dist, idx = tree.query(P, distance_upper_bound=hw * 1.35)
            ok = np.isfinite(dist)
            j = np.where(ok, idx, 0)
            dv = P - pts[j]
            u_perp = np.where(ok, (dv * nrm[j]).sum(1) / hw, 9.)                  # -1..1 across the stroke
            s_arc = arc[j]                                                       # 0..1 along
            rng = np.random.default_rng(11 + i)
            # width wobble + ragged edges
            ph = rng.random(3) * 6.283                                            # smooth width breathing (no zigzag)
            wob = 1 + .045 * np.sin(6.283 * 1.3 * s_arc + ph[0]) + .03 * np.sin(6.283 * 3.2 * s_arc + ph[1]) + .015 * np.sin(6.283 * 7.7 * s_arc + ph[2])
            # bristle streaks (1-D texture across the stroke)
            K_ = 700; tex = np.zeros(K_, np.float32)
            for f, a in ((7, .35), (19, .25), (43, .2), (97, .12)):
                tex += a * np.sin(np.linspace(0, f * 2 * math.pi, K_) + rng.random() * 6.28)
            tex += .25 * rng.standard_normal(K_).astype(np.float32); tex = np.convolve(tex, np.ones(3) / 3, 'same')
            tex = (tex - tex.min()) / (tex.max() - tex.min())
            ti = np.clip(((u_perp + 1.2) / 2.4 * (K_ - 1)).astype(np.int32), 0, K_ - 1)
            streak = tex[ti] * (.72 + .28 * np.interp(s_arc * 23 + u_perp * 3.1, np.arange(40), rng.random(40)))
            en = rng.random(420).astype(np.float32); en = np.convolve(en, np.exp(-np.linspace(-3, 3, 13) ** 2), 'same') / 3.0
            en = (en - en.min()) / (en.max() - en.min())
            side = np.where(u_perp > 0, 0, 210)
            # edge: a slow undulation along the stroke + bristle fray (the streak texture runs ALONG the stroke, so the
            # edge breaks into combed dry-brush lines instead of the torn-paper spikes of a per-sample noise)
            edge_n = np.interp(s_arc * 16 + side, np.arange(420), en) * .07 + np.interp(s_arc * 6, np.arange(12), rng.random(12)) * .05
            fray = np.clip((np.abs(u_perp) - .55) / .35, 0, 1)
            NL = 170; line = np.clip(((u_perp + 1.2) / 2.4 * NL).astype(np.int32), 0, NL - 1)       # bristle lines
            lph = rng.random(NL).astype(np.float32); lfr = 1.5 + 3 * rng.random(NL).astype(np.float32)
            comb = .5 + .5 * np.sin(6.283 * (s_arc * lfr[line] + lph[line]))                         # each line runs dry / wet
            r_edge = wob - edge_n - .08 * streak - .20 * fray * comb ** 2
            cov = np.clip((r_edge - np.abs(u_perp)) / .06, 0, 1)
            # dry-brush tail + soft start
            tail = np.clip((s_arc - .86) / .14, 0, 1)
            dry = np.clip(1 - tail * 1.25 * (1.1 - streak), 0, 1)
            start = np.clip(s_arc / .05, 0, 1)
            A = cov * dry * (.86 + .14 * streak) * np.maximum(start, .7)
            A[~ok] = 0
            # impasto height -> relief (light from top-left)
            Hh = (streak * .9 + .8 * np.clip(np.abs(u_perp) - .7, 0, .3) / .3 * cov) * A
            Hh = Hh.reshape(h2, w2)
            gy, gx = np.gradient(Hh)
            rel = (1 + 1.1 * (-gx * .6 - gy * .8)).ravel()
            rel = np.clip(rel, .88, 1.12)
            a_, b_ = STROKE_T[i]
            tt = a_ + (b_ - a_) * (np.arccos(np.clip(1 - 2 * s_arc, -1, 1)) / math.pi)
            m = A > .02
            first = m & ~np.isfinite(T1)
            T1[first] = tt[first]; A1[first] = A[first]; R1[first] = rel[first]
            later = m & ~first
            T2[later] = tt[later]; A2[later] = A[later]; R2[later] = rel[later]
        out = dict(T1=T1.reshape(h2, w2), A1=A1.reshape(h2, w2), R1=R1.reshape(h2, w2),
                   T2=T2.reshape(h2, w2), A2=A2.reshape(h2, w2), R2=R2.reshape(h2, w2))
        np.savez_compressed(fn, **out)
        return out
    return K.C('paint_maps', mk)


def _inv_sio(y): return math.acos(1 - 2 * y) / math.pi


def artwork():
    """the LUMARC croissant film still, cover-fit to the canvas at 2x, gently graded for 'paint'."""
    def mk():
        src = Image.open(os.path.join(E.THERAPY_A, 'croissant_hero.jpg')).convert('RGB')
        w, h = int(CV[2] * SS), int(CV[3] * SS)
        sc = w / src.width; ch = h / sc
        y0 = 470.
        im = src.crop((0, int(y0), src.width, int(y0 + ch))).resize((w, h), Image.LANCZOS)
        a = np.asarray(im, np.float32)
        a = (a - 128) * 1.06 + 128 + 4
        return np.clip(a, 0, 255)
    return K.C('artwork', mk)


def paint_grad():
    def mk():
        w, h = int(CV[2] * SS), int(CV[3] * SS)
        g = np.asarray(E.gradient(w, 1, [(110, 138, 255), (138, 116, 255), (190, 112, 255)]), np.float32)
        return np.repeat(g, h, 0)
    return K.C('paint_grad', mk)


_PC = {}
def painted_canvas(t):
    """canvas face (float RGB 2x) painted up to time t."""
    t = min(t, STROKE_T[-1][1] + .6)
    key = round(t, 4)
    if _PC.get('k') == key: return _PC['v']
    M = paint_maps(); base = canvas_base()
    if t < STROKE_T[0][0]: return base
    T1, A1, R1, T2, A2, R2 = M['T1'], M['A1'], M['R1'], M['T2'], M['A2'], M['R2']
    c1 = np.clip((t - T1) / .025, 0, 1) * A1
    c2 = np.clip((t - T2) / .025, 0, 1) * A2
    al = c1 + c2 * (1 - c1)
    rows = np.where(al.max(1) > .002)[0]
    out = base.copy()
    if len(rows):
        r0, r1 = rows[0], rows[-1] + 1
        sl = slice(r0, r1)
        use2 = (T2[sl] <= t)
        Tc = np.where(use2, T2[sl], T1[sl]); Rc = np.where(use2, R2[sl], R1[sl])
        age = t - Tc
        wet = 1 - np.clip((age - .02) / .17, 0, 1); wet = wet * wet * (3 - 2 * wet)
        art = artwork()[sl]; pg = paint_grad()[sl]
        col = art * (1 - wet[..., None]) + pg * wet[..., None]
        # wet sheen on fresh paint
        col = col * Rc[..., None] + (wet * np.clip(Rc - 1, 0, 1) * 260)[..., None]
        a = al[sl][..., None]
        out[sl] = np.clip(base[sl] * (1 - a) + col * a, 0, 255)
    _PC.update(k=key, v=out)
    return out


def logo_sign(w):
    def mk():
        lg = E.logo(w); return lg
    return K.C(('sign', w), mk)


def finished_canvas(t):
    """painted canvas + the LUMARC signature (wipe-on) + varnish glint, float RGB 2x."""
    c = painted_canvas(t)
    if t < T_SIGN: return c
    c = c.copy()
    w = int(CV[2] * SS * .36); lg = logo_sign(w)
    k = eout((t - T_SIGN) / .26)
    x0 = int(CV[2] * SS - w - 40); y0 = int(CV[3] * SS - lg.height - 132)      # clear of the brush resting on the ledge
    a = np.asarray(lg, np.float32); al = a[..., 3:] / 255
    xs = np.arange(lg.width, dtype=np.float32)[None, :, None]
    edge = k * (lg.width + 60) - 30
    al = al * np.clip((edge - xs) / 30, 0, 1)
    reg = c[y0:y0 + lg.height, x0:x0 + lg.width]
    glint = np.exp(-((xs - edge) / 10) ** 2) * (1 - k) * 1.5
    c[y0:y0 + lg.height, x0:x0 + lg.width] = reg * (1 - al) + (a[..., :3] * 1.05 + glint * 255 * (a[..., 3:] > 30)) * al
    # varnish glint (diagonal soft band) on "USA"
    g = (t - O['USA']) / .55
    if 0 <= g < 1:
        h_, w_ = c.shape[:2]
        yy, xx = np.mgrid[0:h_:4, 0:w_:4].astype(np.float32)
        pos = (xx / w_ * .55 + yy / h_ * .45)
        band = np.exp(-((pos - lerp(-.2, 1.2, eout(g))) / .06) ** 2) * .22 * math.sin(math.pi * g)
        band = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).resize((w_, h_), Image.BILINEAR), np.float32) / 255
        c = c + (255 - c) * band[..., None]
    return c


T_READY = T_WAKE + .11                 # the brush hangs upright in the middle of the canvas, ready
T_HOME = STROKE_T[-1][1] + .22         # …after the last stroke it lands back on the ledge


def _stroke_ang(dx, dy):
    hx, hy = -dx * .55, -dy * .55 - .85                                 # handle trails the motion and leans up
    return math.degrees(math.atan2(-hy, hx))


def brush_pose_C(t):
    """-> (tip world xy, ang, direction) for shot C."""
    cx0, cy0 = CV[0], CV[1]
    if t < T_WAKE:
        return (REST_TIP[0], REST_TIP[1]), REST_ANG, (0, 0)
    t_go = STROKE_T[0][0]
    mid = (cx0 + 250., cy0 + 430.)
    if t < T_READY:                                                    # springs up into the canvas centre with a spin
        u = (t - T_WAKE) / (T_READY - T_WAKE); e = eout(u)
        x = lerp(REST_TIP[0], mid[0], e); y = lerp(REST_TIP[1], mid[1], e) - 60 * math.sin(math.pi * u)
        return (x, y), REST_ANG + (360 + 90 - REST_ANG) * e, (0, 0)
    p1 = (cx0 + STROKES[0][0][0], cy0 + STROKES[0][0][1])
    a1 = _stroke_ang(1, 0)
    if t < t_go:                                                       # tiny anticipation, then dashes to the first stroke
        u = (t - T_READY) / (t_go - T_READY)
        if u < .35:
            k = math.sin(math.pi * u / .35); return (mid[0] + 8 * k, mid[1] + 14 * k), 90 + 6 * k, (0, 0)
        v = sio((u - .35) / .65)
        return (lerp(mid[0], p1[0], v), lerp(mid[1], p1[1], v)), lerp(90, a1, v), (0, 0)
    for i, (a, b) in enumerate(STROKE_T):
        nb = STROKE_T[i + 1][0] if i + 1 < len(STROKE_T) else None
        if t < b or nb is None or t < nb:
            p0, c1, c2, p1_, hw = STROKES[i]
            if t < b:
                u = stroke_u(t, i); x, y = bez(p0, c1, c2, p1_, u); q = bez(p0, c1, c2, p1_, min(1, u + .02))
                d = (q[0] - x, q[1] - y + 1e-6)
            elif nb is not None:                                       # quick turn at the canvas edge
                v = (t - b) / (nb - b); q0 = p1_; q1 = STROKES[i + 1][0]
                x, y = lerp(q0[0], q1[0], sio(v)), lerp(q0[1], q1[1], sio(v))
                d = ((1 if i % 2 == 0 else -1) * (1 - 2 * sio(v)), .6)
            else:                                                      # after the last stroke: lands back on the ledge
                v = clamp((t - b) / (T_HOME - b)); e = v * v
                x0, y0 = cx0 + p1_[0], cy0 + p1_[1]
                X = lerp(x0, REST_TIP[0], eout(v)); Y = lerp(y0, REST_TIP[1], e) - 120 * math.sin(math.pi * v)
                if t >= T_HOME:
                    w_ = t - T_HOME; bb = 10 * math.exp(-w_ * 18) * abs(math.sin(w_ * 34))
                    return (REST_TIP[0], REST_TIP[1] - bb), REST_ANG + 3 * math.exp(-w_ * 14) * math.cos(w_ * 40), (0, 0)
                return (X, Y), lerp(_stroke_ang(1, 0), REST_ANG, eout(v)), (0, 0)
            n = math.hypot(*d) + 1e-6
            return (cx0 + x, cy0 + y), _stroke_ang(d[0] / n, d[1] / n), (d[0] / n, d[1] / n)
    return (REST_TIP[0], REST_TIP[1]), REST_ANG, (0, 0)


# ================================================================ shot B annotation
def chip_ia(wrench=0.):
    def mk():
        g = K.grad_text('IA', 100, 800); h = 146; w = g.width + 90
        im = Image.new('RGBA', (w + 80, h), (0, 0, 0, 0))
        body = K.dark_glass(w, h, 38, .74, .0); im.alpha_composite(body)
        bd = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(bd).rounded_rectangle((2, 2, w * 2 - 3, h * 2 - 3), 76, outline=255, width=6)
        bd = bd.resize((w, h), Image.LANCZOS); gg = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); gg.putalpha(bd); im.alpha_composite(gg)
        im.alpha_composite(g, (45, (h - g.height) // 2 + 2))
        return im, w
    base, w0 = K.C('chip_ia', mk)
    if wrench <= .01: return base.crop((0, 0, w0, base.height)), w0
    # wider chip with a wrench glyph sliding in on the left
    def mk2():
        g = K.grad_text('IA', 100, 800); h = 146; w = g.width + 90 + 100
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        body = K.dark_glass(w, h, 38, .74, .0); im.alpha_composite(body)
        bd = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(bd).rounded_rectangle((2, 2, w * 2 - 3, h * 2 - 3), 76, outline=255, width=6)
        bd = bd.resize((w, h), Image.LANCZOS); gg = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); gg.putalpha(bd); im.alpha_composite(gg)
        im.alpha_composite(wrench_glyph(70), (38, (h - 70) // 2))
        im.alpha_composite(g, (45 + 100, (h - g.height) // 2 + 2))
        return im
    wide = K.C('chip_ia_w', mk2)
    k = eout(wrench)
    ww = int(lerp(w0, wide.width, k))
    im = Image.new('RGBA', (ww, wide.height), (0, 0, 0, 0))
    # body stretches, contents slide
    body = K.C(('chipbody', ww), lambda: _chip_body(ww, wide.height))
    im.alpha_composite(body)
    g = K.grad_text('IA', 100, 800)
    im.alpha_composite(g, (int(45 + 100 * k), (wide.height - g.height) // 2 + 2))
    if k > .05:
        wg = K.fade(wrench_glyph(70), clamp((k - .2) / .6))
        wg = K.scale_im(wg, .5 + .5 * back(clamp(wrench * 1.2), 2.5))
        im.alpha_composite(wg, (int(38 + 35 - wg.width / 2), int((wide.height - wg.height) / 2)))
    return im, ww


def _chip_body(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    im.alpha_composite(K.dark_glass(w, h, 38, .74, .0))
    bd = Image.new('L', (w * 2, h * 2)); ImageDraw.Draw(bd).rounded_rectangle((2, 2, w * 2 - 3, h * 2 - 3), 76, outline=255, width=6)
    bd = bd.resize((w, h), Image.LANCZOS); gg = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); gg.putalpha(bd); im.alpha_composite(gg)
    return im


def wrench_glyph(d):
    def mk():
        S = 4; D = d * S; m = Image.new('L', (D, D)); dr = ImageDraw.Draw(m)
        # handle (diagonal bar) + open-jaw head (ring with a notch)
        dr.line((D * .22, D * .80, D * .60, D * .42), fill=255, width=int(D * .16))
        dr.ellipse((D * .48, D * .10, D * .92, D * .54), fill=255)
        dr.ellipse((D * .60, D * .22, D * .80, D * .42), fill=0)
        dr.polygon([(D * .70, D * .32), (D * 1.0, D * .02), (D * 1.0, D * .40)], fill=0)
        dr.ellipse((D * .14, D * .72, D * .30, D * .88), fill=255)
        m = m.resize((d, d), Image.LANCZOS); g = E.gradient(d, d, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m); return g
    return K.C(('wrench', d), mk)


def selection_box(ctx, t, cam, tip, ang, length):
    """design-tool selection around the brush: rotated rectangle drawn on, corner handles pop."""
    k = (t - O['FERRAMENTA']) / .30
    if k <= 0: return
    a = math.radians(ang); ux, uy = math.cos(a), -math.sin(a); nx, ny = -uy, ux
    pad_l, pad_w = 26, 40
    corners = []
    for s_, n_ in ((-pad_l, -pad_w), (length + pad_l, -pad_w), (length + pad_l, pad_w), (-pad_l, pad_w)):
        corners.append((tip[0] + ux * s_ + nx * n_, tip[1] + uy * s_ + ny * n_))
    per = [math.dist(corners[i], corners[(i + 1) % 4]) for i in range(4)]; tot = sum(per)
    draw_len = eout(k) * tot
    x0 = int(min(c[0] for c in corners)) - 20; y0 = int(min(c[1] for c in corners)) - 20
    x1 = int(max(c[0] for c in corners)) + 20; y1 = int(max(c[1] for c in corners)) + 20
    S = 2; m = Image.new('L', ((x1 - x0) * S, (y1 - y0) * S)); d = ImageDraw.Draw(m)
    acc = 0
    for i in range(4):
        p, q = corners[i], corners[(i + 1) % 4]
        if acc >= draw_len: break
        f = min(1, (draw_len - acc) / per[i]); e_ = (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)
        # dashed
        L_ = per[i] * f; nd = int(L_ / 18)
        for j in range(nd + 1):
            s0 = j * 18 / per[i]; s1 = min(f, (j * 18 + 11) / per[i])
            if s0 >= f: break
            a0 = (p[0] + (q[0] - p[0]) * s0, p[1] + (q[1] - p[1]) * s0); a1 = (p[0] + (q[0] - p[0]) * s1, p[1] + (q[1] - p[1]) * s1)
            d.line([((a0[0] - x0) * S, (a0[1] - y0) * S), ((a1[0] - x0) * S, (a1[1] - y0) * S)], fill=255, width=4 * S)
        acc += per[i]
    m = m.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    g = Image.new('RGBA', m.size, (236, 232, 255, 0)); g.putalpha(m)
    gl = Image.new('RGBA', m.size, (130, 100, 255, 0)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(4)))
    ctx.add('screen', gl, x0, y0, center=False); ctx.add('screen', g, x0, y0, center=False)
    for i, c in enumerate(corners):
        u = (t - O['FERRAMENTA'] - .05 - .05 * i) / .16
        if u <= 0: continue
        hs = int(28 * (.5 + .5 * back(u, 2.6)))
        h_ = K.C(('handle', hs), lambda hs=hs: _handle(hs))
        ctx.add('screen', h_, c[0], c[1])


def _handle(s):
    im = Image.new('RGBA', (s + 8, s + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((4, 4, 4 + s, 4 + s), fill=(250, 249, 246, 255), outline=(120, 98, 255, 255), width=3)
    return im


# ================================================================ draw
def whip(dx_px):
    """horizontal motion blur (whip-pan): edge-clamped box blur of width dx_px."""
    def wrap(fr):
        a = np.asarray(fr.convert('RGB'), np.float32); r = max(1, int(dx_px / 2))
        pad = np.concatenate([np.repeat(a[:, :1], r + 1, 1), a, np.repeat(a[:, -1:], r, 1)], 1)
        cs = np.cumsum(pad, axis=1, dtype=np.float32)
        out = (cs[:, 2 * r + 1:] - cs[:, :-(2 * r + 1)]) / (2 * r + 1)
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    return wrap


def cam_A(t):
    u = (t - START) / .24
    Z = 1.02 - .02 * clamp((t - START) / (T9 - START))
    c = (330., 1130.)
    sx = 372. + 360 * (1 - expo(u))          # whip-pan arriving from the right
    v = 360 * 10 * math.log(2) * 2 ** (-10 * clamp(u)) / .24 / 30          # px per frame
    return VCam(Z, c, (sx, 1062.)), (v * .9 if u < 1 else 0)


def cam_B(t):
    """macro: tight on the brush lying on the ledge, Dutch roll, slow dolly along it (bristles -> ferrule)."""
    u = (t - T9) / (T10 - T9)
    Z = 3.05 + .25 * sio(u) + .45 * (1 - expo((t - T9) / .22))
    c = (lerp(215., 300., sio(u)), 1470.)
    return VCam(Z, c, (540., 1000.), roll=7.0 + 1.5 * u)


def cam_C(t):
    Z0 = 1.78
    c0 = (CV[0] + CV[2] / 2, CV[1] + CV[3] / 2)
    s0 = (565., 790.)
    Z = Z0 + .05 * (1 - expo((t - T10) / .25)) + .03 * clamp((t - T10) / 1.2)
    if t >= T_PULL:                                    # pull back to the two-shot
        k = expo((t - T_PULL) / .42)
        Z = lerp(Z, 1.0, k)
        c = (lerp(c0[0], 330., k), lerp(c0[1], 1130., k)); s = (lerp(s0[0], 372., k), lerp(s0[1], 1062., k))
        return VCam(Z, c, s)
    return VCam(Z, c0, s0)


def draw(ctx, lt, t):
    ctx.captions = False
    P = ctx.post

    if t < T9:
        # ---------------- SHOT A: two-shot, the brush alone
        cam, wv = cam_A(t)
        apply_cam(ctx, cam, blur_bg=6.)
        P['vignette'] = .40
        if wv > 2: ctx.wrap = whip(wv)
        pose = brush_pose_A(t)
        if pose is not None:
            (wx, wy), ang, al = pose
            tip = cam.P(wx, wy)
            # shadow on the canvas while hovering (offset grows with the distance to the surface); on the ledge: contact
            hover = t < T_LAND
            kl = lean_k(t)
            sh = (lerp(24, 3, kl) * cam.Z, lerp(30, 5, kl) * cam.Z, lerp(9, 3, kl), lerp(.34, .55, kl)) if hover else (4, 8, 4, .55)
            vel = None
            if T_FALL <= t < T_LAND or t < O['PINCEL'] + .1:
                q = brush_pose_A(t - 1 / 30)
                if q is not None: qp = cam.P(*q[0]); vel = (tip[0] - qp[0], tip[1] - qp[1])
            add_brush(ctx, tip, ang, BR_LEN * cam.Z, shadow=sh, blur_v=vel)
        K.caps(ctx, t, PAGES, y=330)
        return

    if t < T10:
        # ---------------- SHOT B: macro on the fallen brush, "IA" / "FERRAMENTA"
        cam = cam_B(t)
        apply_cam(ctx, cam, blur_bg=16., dim=.2, set_soft=1.5)
        P['vignette'] = .52
        P['zoom_blur'] = .5 * clamp(1 - (t - T9) / .1)
        tip = cam.P(*REST_TIP); L = BR_LEN * cam.Z; ang = REST_ANG + cam.roll
        gl = (t - O['FERRAMENTA'] + .02) / .5
        add_brush(ctx, tip, ang, L, shadow=(8, 18, 10, .6), glint=lerp(-.1, 1.1, eout(gl)) if 0 <= gl < 1 else None)
        # annotation: dot on the ferrule -> leader -> chip
        a = math.radians(ang)
        fer = (tip[0] + math.cos(a) * L * .30, tip[1] - math.sin(a) * L * .30)
        kd = (t - O['IA'] + .03) / .14
        if kd > 0:
            ds = .3 + .7 * back(kd, 3)
            ctx.add('screen', K.scale_im(K.glow_dot(10, (150, 120, 255)), ds), fer[0], fer[1])
            u = (t - O['IA'] + .03) / .36
            if 0 <= u < 1:
                rg = K.ring(int(30 + 140 * eout(u)), 3, (200, 180, 255), .9 * (1 - u)); ctx.add('screen', rg, fer[0], fer[1])
            chip_c = (fer[0] + 40, fer[1] - 380)
            kl = eout((t - O['IA']) / .16)
            p_end = (fer[0] + (chip_c[0] - fer[0]) * kl, fer[1] + (chip_c[1] + 73 - fer[1]) * kl)
            ln, lx, ly = K.line_img(fer, p_end, (220, 210, 255), 3, .95)
            ctx.add('screen', ln, lx, ly, center=False)
            if t >= O['IA'] + .06:
                wr = clamp((t - O['FERRAMENTA'] - .08) / .3)
                ch, cw = chip_ia(wr)
                s_ = .6 + .4 * back((t - O['IA'] - .06) / .2, 2.6)
                ctx.add('screen', K.scale_im(ch, s_), chip_c[0], chip_c[1], glass=10)
        selection_box(ctx, t, cam, tip, ang, L)
        K.caps(ctx, t, PAGES, y=1500)
        return

    # ---------------- SHOT C: the painting
    cam = cam_C(t)
    painting = finished_canvas(t)
    set_img = set_image(painting)
    apply_cam(ctx, cam, blur_bg=7., set_img=set_img)
    P['vignette'] = .38
    if t < T10 + .08: P['zoom_blur'] = .45 * (1 - (t - T10) / .08)
    (wx, wy), ang, d = brush_pose_C(t)
    tip = cam.P(wx, wy)
    q = brush_pose_C(t - 1 / 30)[0]; qp = cam.P(*q)
    vel = (tip[0] - qp[0], tip[1] - qp[1])
    resting = t < T_WAKE or t >= T_HOME
    sh = (4, 8, 4, .55) if resting else (14 * cam.Z / 2, 20 * cam.Z / 2, 6, .32)
    add_brush(ctx, tip, ang, BR_LEN * cam.Z * (1.0 if resting else .92), shadow=sh,
              blur_v=vel if math.hypot(*vel) > 8 and not resting else None)
    K.caps(ctx, t, PAGES, y=lerp(1590, 1600, clamp((t - T_PULL) / .4)), base=86)      # 86: 'TÁ EM QUEM USA.' on one line
