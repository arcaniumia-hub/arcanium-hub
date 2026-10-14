"""s10 — CTA + END CARD (69.32–76.48).  "Quer o mesmo pra sua marca?" / "Entre em contato com a gente." /
"O número tá aqui na tela." / (silent smile = the END CARD)

A  69.32 JUMP — out of the AI-tinted frame into a WARM, human push-in (z 1.16 -> 1.36, golden key from the left, a soft
   light leak).  "QUER O MESMO | PRA SUA MARCA?" (bottom).  70.18 "MARCA": an empty glass "brand slot" pops above his
   head — dashed outline, a placeholder logo mark and a "+": the next piece of work is waiting for YOUR brand.
B  70.56 JUMP — snap back to a medium shot (the slot flicks up and away).  Captions move to the top.  "CONTATO"
   (70.925): a premium frosted-glass contact card rises from the bottom over his chest and lands on the stressed "TA"
   (71.07): gradient phone badge + (854) 295-2249 huge and crisp (revealed by a light wipe), @lumarc_studio ·
   slumarc.com under it.
C  (71.72, same shot) "O NÚMERO" (72.12): a light sheen runs through the digits; "TÁ AQUI" (72.445) as his palms open
   toward it the card BOUNCES and a gradient underline sweeps under the number; "NA TELA" (72.795) a fingertip TAP
   ripples on the glass right on the number and a chevron arrow bounces down at it.
D  73.28 END CARD (his silent smile; the take's own frames): BOOM + SHIMMER — the LUMARC logo is drawn by a light wipe
   that lands on 73.28 (bloom, shock ring), the studio melts into the brand space behind him (deep defocus, violet
   duotone, drifting bokeh) while he settles lower; "AI-first. Not AI-only." rises under the logo; the contact card
   stays (the PHONE never leaves the screen) and breathes; when his hands open (74.8) the card is right above them;
   75.60 one last light sweep over logo + number.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _F_kit as K
from sections import _shared as SH

START, END = E.span(34, 37)                      # 69.32 – 76.48
T34, T35, T36, T37 = (E.TL[i]['t0'] for i in (34, 35, 36, 37))     # 69.32, 70.56 (JUMP), 71.72, 73.28
W, H = E.W, E.H
clamp, eout, ein, back, lerp, smooth, expo, eio = E.clamp, E.eout, E.ein, E.back, K.lerp, K.smooth, K.expo, K.eio

# word onsets measured on src/tight16k.raw (5 ms STFT, 3 band envelopes; out/F/sp_i, sp_j, sp_k)
O = dict(QUER=69.38, O=69.55, MESMO=69.645, PRA=69.90, SUA=69.99, MARCA=70.18, MAR=70.20, MARCA_END=70.45,
         ENTRE=70.65, TRE=70.80, EM=70.84, CONTATO=70.925, TA=71.07, COM=71.28, A=71.38, GENTE=71.50, GENTE_END=71.68,
         O2=72.045, NUMERO=72.12, NU=72.265, TA2=72.445, AQUI=72.52, QUI=72.57, NA=72.72, TELA=72.795, TELA_END=73.00)
LAND = O['TA']                                     # card lands
BOUNCE = O['TA2']
TAP = O['TELA']
END0 = T37                                         # 73.28 end card
LOGO0 = END0 - .17                                 # the logo's light wipe lands on 73.28
TAG0 = 73.62
SWEEP = 75.60

CUES = [
    (T34, 'whoosh', {'gain': -13}),                            # warm push-in
    (T34 + .01, 'shimmer', {'gain': -17}),                     # light leak
    (O['MARCA'], 'pop', {'gain': -7}),                         # brand slot
    (O['MARCA'] + .03, 'click', {'gain': -13}),
    (T35, 'swipe', {'gain': -9}),                              # snap back, slot flicks away
    (O['CONTATO'] - .06, 'swoosh_up', {'gain': -6}),           # contact card rises
    (LAND, 'thud', {'gain': -8}),                              # ...lands on "TA"
    (LAND, 'pop', {'gain': -6}),
    (LAND + .03, 'type', {'i': 0, 'gain': -14}),               # number wipes in
    (LAND + .08, 'type', {'i': 1, 'gain': -15}),
    (LAND + .13, 'type', {'i': 2, 'gain': -16}),
    (O['NU'], 'shimmer', {'gain': -10}),                       # sheen through the digits
    (BOUNCE, 'pop', {'gain': -6}),                             # card bounces as he presents it
    (BOUNCE + .02, 'swipe', {'gain': -13}),                    # underline sweep
    (TAP, 'click', {'gain': -5}),                              # tap on the glass
    (TAP + .01, 'ding', {'note': 'E6', 'gain': -13}),
    (LOGO0, 'riser', {'to': END0, 'gain': -9}),
    (END0, 'boom', {'gain': 0}),                               # END CARD
    (END0, 'shimmer', {'gain': -4}),
    (END0 + .02, 'impact', {'gain': -9}),
    (TAG0, 'swipe', {'gain': -13}),                            # tagline
    (74.45, 'shimmer', {'gain': -16}),                         # sheen over the number
    (SWEEP, 'shimmer', {'gain': -10}),                         # last light sweep
]

F_, T_ = False, True
PAGES_A = [(O['QUER'] - .04, O['PRA'] - .02, [('QUER', O['QUER'], F_), ('O', O['O'], F_), ('MESMO', O['MESMO'], F_)]),
           (O['PRA'] - .02, T35, [('PRA', O['PRA'], F_), ('SUA', O['SUA'], F_), ('MARCA?', O['MARCA'], T_)])]
PAGES_B = [(O['ENTRE'] - .04, O['COM'] - .02, [('ENTRE', O['ENTRE'], F_), ('EM', O['EM'], F_), ('CONTATO', O['CONTATO'], T_)]),
           (O['COM'] - .02, O['O2'] - .03, [('COM', O['COM'], F_), ('A', O['A'], F_), ('GENTE.', O['GENTE'], F_)])]
PAGES_C = [(O['O2'] - .03, O['TA2'] - .02, [('O', O['O2'], F_), ('NÚMERO', O['NUMERO'], T_)]),
           (O['TA2'] - .02, LOGO0 - .03, [('TÁ', O['TA2'], F_), ('AQUI', O['AQUI'], F_), ('NA', O['NA'], F_), ('TELA.', O['TELA'], T_)])]


def C(k, fn): return K.C(('s10',) + (k if isinstance(k, tuple) else (k,)), fn)


# =========================================================================================== the contact card
CW, CH = 944, 316
CARD_Y = 1392                                      # card centre (B/C)
CARD_Y_END = 1372                                  # card centre (end card)
ICON_C = (128, 128)                                # badge centre in card px
NUM_X, NUM_Y = 238, 128                            # number left edge / centre in card px
NUM_SIZE = 92


def card_base():
    def mk():
        p = E.glass_panel(CW, CH, 52, tint=(160, 150, 255), alpha=.14, border=.55)
        # gradient badge with the handset
        b = 148; disc = Image.new('L', (b * 3, b * 3)); ImageDraw.Draw(disc).ellipse((0, 0, b * 3 - 1, b * 3 - 1), fill=255)
        disc = disc.resize((b, b), Image.LANCZOS)
        g = E.gradient(b, b, E.GRAD).convert('RGBA'); g.putalpha(disc)
        gl = K.glow_sprite(b, b, (120, 90, 255), 22, .9)
        K.paste(p, gl, ICON_C[0], ICON_C[1] + 6, alpha=.8)
        K.paste(p, g, *ICON_C)
        hs = K.icon_phone(78, E.WHITE)
        K.paste(p, hs, *ICON_C)
        # divider + handle line
        d = ImageDraw.Draw(p)
        d.line([(NUM_X, 196), (CW - 54, 196)], fill=(255, 255, 255, 46), width=2)
        hd = K.text_line('@lumarc_studio  ·  slumarc.com', 38, 500, (214, 211, 236), shadow=0)
        K.paste(p, hd, NUM_X - int(38 * .4) + hd.width / 2, 250)
        return p
    return C('card', mk)


def number():
    """(854) 295-2249 — white, crisp, with a soft violet glow. -> (RGBA, glyph mask)"""
    return K.display(SH.PHONE, NUM_SIZE, 800, 'white', glow=.35, shadow=.6)


def card_img(t):
    """the full card at time t: base + number (light wipe in, sheens) + underline."""
    p = card_base().copy()
    num, nm = number()
    pad = int(NUM_SIZE * .42)
    # light wipe reveal from the left, landing just after the card lands
    k = clamp((t - (LAND - .02)) / .30)
    if k <= 0: return p
    for t0, d in ((O['NU'] - .04, .42), (74.45, .6), (SWEEP + .25, .7)):
        sk = (t - t0) / d
        if 0 < sk < 1: num = K.sheen(num, sk, nm, 30, .65)
    if k < 1:
        wv = int((num.width + 60) * eout(k))
        m = np.zeros((num.height, num.width), np.float32)
        xs = np.arange(num.width, dtype=np.float32)
        m[:] = np.clip((wv - xs) / 40, 0, 1)[None, :]
        a = np.asarray(num.getchannel('A'), np.float32) * m
        num2 = num.copy(); num2.putalpha(Image.fromarray(a.astype(np.uint8)))
        edge = np.exp(-((xs - wv + 20) / 14) ** 2)[None, :] * nm
        n2 = np.asarray(num2, np.float32); n2[..., :3] += (255 - n2[..., :3]) * edge[..., None] * .8
        n2[..., 3] = np.maximum(n2[..., 3], edge * 255 * (1 - k))
        num = Image.fromarray(np.clip(n2, 0, 255).astype(np.uint8), 'RGBA')
    K.paste(p, num, NUM_X - pad, NUM_Y - num.height / 2, center=False)
    # gradient underline sweep on "TÁ AQUI"
    if t >= BOUNCE:
        u = eout((t - BOUNCE) / .26)
        x0 = NUM_X; x1 = NUM_X + (num.width - 2 * pad) * u
        ul = E.gradient(max(2, int(x1 - x0)), 7, E.GRAD_LIGHT).convert('RGBA')
        ul = E.rounded(ul, 3)
        K.paste(p, ul, x0, 178, center=False)
        if u < 1:
            K.paste(p, K.glow_sprite(40, 18, (200, 190, 255), 6), x1, 181, alpha=.9)
    return p


def card_glow():
    def mk():
        a = Image.new('L', (CW + 240, CH + 240)); ImageDraw.Draw(a).rounded_rectangle((120, 120, 120 + CW, 120 + CH), 52, fill=255)
        g = Image.new('RGBA', a.size, (110, 80, 255, 0)); g.putalpha(a.filter(ImageFilter.GaussianBlur(50)).point(lambda v: int(v * .55)))
        return g
    return C('cglow', mk)


def draw_card(ctx, t):
    if t < O['CONTATO'] - .08: return
    k = clamp((t - (O['CONTATO'] - .08)) / (LAND - O['CONTATO'] + .08))
    y = lerp(H + 260, CARD_Y, eout(k)) if t < LAND else CARD_Y
    s = 1.0
    if t >= LAND:
        u = t - LAND
        y += 10 * math.exp(-u / .08) * math.cos(u * 40) - 10 * math.exp(-u / .08)
        s *= 1 + .03 * math.exp(-u / .07) * math.cos(u * 42)
    if t >= BOUNCE:                                                   # he presents it: hop
        u = t - BOUNCE
        y -= 34 * math.sin(math.pi * clamp(u / .22)) * (1 if u < .22 else 0) - 6 * math.exp(-max(0, u - .22) / .06) * math.sin(max(0, u - .22) * 45)
        s *= 1 + .04 * K.bump(u, .11)
    if t >= END0:                                                     # end card: settles a touch higher
        ke = eio((t - END0) / .6)
        y = lerp(y, CARD_Y_END, ke)
        s *= 1 + .012 * math.sin((t - END0) * 2.6) * ke                 # breathing
    if t < LAND:
        y += 0
    im = card_img(t)
    if abs(s - 1) > .003: im = K.scale_im(im, s)
    gk = .55 + .25 * K.bump(t - LAND, .14) + .35 * K.bump(t - BOUNCE, .14) + .4 * K.bump(t - TAP, .14)
    if t >= END0: gk = .65 + .15 * math.sin((t - END0) * 2.6)
    ctx.add('screen', card_glow(), 540, y + 16, alpha=clamp(k * 2) * min(1, gk))
    ctx.add('screen', im, 540, y, glass=18, alpha=clamp(k * 4))
    # tap ripple right on the number
    if TAP - .02 <= t < TAP + .5:
        u = t - (TAP - .02)
        tx, ty = 540 - CW / 2 + NUM_X + 300, y - CH / 2 + NUM_Y
        r1 = K.ring_sprite(30 + 150 * eout(u / .45), 3.0, .95 * (1 - u / .5))
        ctx.add('screen', r1, tx, ty)
        if u > .06:
            r2 = K.ring_sprite(20 + 110 * eout((u - .06) / .4), 2.4, .7 * (1 - u / .5))
            ctx.add('screen', r2, tx, ty)
        if u < .16: ctx.add('screen', K.glow_sprite(70, 70, (235, 230, 255), 10), tx, ty, alpha=.8 * (1 - u / .16))
    # chevron arrow bouncing down at the card ("tá aqui na tela")
    if O['AQUI'] - .04 <= t < END0 + .1:
        k2 = clamp((t - (O['AQUI'] - .04)) / .14) * (1 - clamp((t - (LOGO0 - .06)) / .12))   # gone before the logo
        bob = 14 * abs(math.sin((t - O['AQUI']) * 2 * math.pi * 1.6))
        ch = K.grad_fill(K.chevron(64, (255, 255, 255), .17))
        for i in range(2):
            ctx.add('screen', ch, 540, y - CH / 2 - 70 + i * 24 + bob, alpha=k2 * (.55 + .45 * i))


# =========================================================================================== A: the brand slot
def brand_slot():
    def mk():
        w, h = 470, 196
        im = E.glass_panel(w, h, 40, tint=(170, 160, 255), alpha=.08, border=0.0, shine=True)
        d = ImageDraw.Draw(im)
        # dashed outline
        r = 40; per = []
        def dash_line(p0, p1):
            L = math.dist(p0, p1); n = int(L // 22)
            for i in range(n):
                a0 = i / n; a1 = (i + .55) / n
                d.line([(p0[0] + (p1[0] - p0[0]) * a0, p0[1] + (p1[1] - p0[1]) * a0), (p0[0] + (p1[0] - p0[0]) * a1, p0[1] + (p1[1] - p0[1]) * a1)],
                       fill=(225, 220, 255, 220), width=3)
        dash_line((r, 2), (w - r, 2)); dash_line((r, h - 3), (w - r, h - 3)); dash_line((2, r), (2, h - r)); dash_line((w - 3, r), (w - 3, h - r))
        for (cx, cy, a0) in ((r, r, 180), (w - r, r, 270), (w - r, h - r, 0), (r, h - r, 90)):
            for j in range(3):
                d.arc((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), a0 + j * 30, a0 + j * 30 + 16, fill=(225, 220, 255, 220), width=3)
        # placeholder logo mark: circle + two bars, and a "+" badge
        d.ellipse((150, 58, 230, 138), outline=(235, 232, 255, 230), width=4)
        d.rounded_rectangle((252, 70, 352, 86), 8, fill=(235, 232, 255, 200))
        d.rounded_rectangle((252, 108, 322, 122), 7, fill=(235, 232, 255, 130))
        pb = 58; disc = Image.new('L', (pb * 3, pb * 3)); ImageDraw.Draw(disc).ellipse((0, 0, pb * 3 - 1, pb * 3 - 1), fill=255)
        disc = disc.resize((pb, pb), Image.LANCZOS); g = E.gradient(pb, pb, E.GRAD).convert('RGBA'); g.putalpha(disc)
        K.paste(im, g, w - 62, 62)
        dd = ImageDraw.Draw(im); c = (w - 62, 62)
        dd.line([(c[0] - 13, c[1]), (c[0] + 13, c[1])], fill=(255, 255, 255, 255), width=5)
        dd.line([(c[0], c[1] - 13), (c[0], c[1] + 13)], fill=(255, 255, 255, 255), width=5)
        return im
    return C('slot', mk)


def warm_key():
    """golden key light from the left + a soft leak (additive float field)."""
    def mk():
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        f = np.exp(-(((xx + 120) / 620) ** 2 + ((yy - 760) / 900) ** 2))[..., None] * np.array([70, 42, 10], np.float32)
        f += np.exp(-(((xx - 1150) / 300) ** 2 + ((yy - 300) / 500) ** 2))[..., None] * np.array([40, 18, 50], np.float32)
        return np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
    return C('warm', mk)


def leak_field():
    """a warm film light-leak band (2W wide, diagonal), slid across the frame on the cut."""
    def mk():
        yy, xx = np.mgrid[0:H // 4, 0:(2 * W) // 4].astype(np.float32) * 4
        d = (xx - W) + (yy - 960) * .35
        b = np.exp(-(d / 260) ** 2)[..., None]
        core = np.exp(-(d / 90) ** 2)[..., None]
        f = b * np.array([150, 70, 40], np.float32) + core * np.array([90, 60, 50], np.float32)
        f *= (.55 + .45 * np.exp(-((yy - 700) / 900) ** 2))[..., None]
        return np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).resize((2 * W, H), Image.BILINEAR), np.float32)
    return C('leak', mk)


def beat_a(ctx, t):
    P = ctx.post
    u = t - T34
    z = 1.16 + .20 * eio(clamp(u / (T35 - T34)))
    ctx.cam = dict(z=z, x=540., y=860., dx=0., dy=0., rot=0.)
    P['sat'] = 1.06; P['vignette'] = .4
    lk = clamp(u / .55)
    def wrap(fr, u=u, lk=lk):
        fr = K.add_field(fr, warm_key(), .75)
        if lk < 1:                                              # light leak sweeps across on the cut
            x0 = int(lerp(W * .95, 0, eout(lk)))
            fr = K.add_field(fr, leak_field()[:, x0:x0 + W], .9 * math.sin(math.pi * lk) ** .7)
        return fr
    ctx.wrap = wrap
    if t >= O['MARCA'] - .03:
        k = clamp((t - (O['MARCA'] - .03)) / .18)
        sl = brand_slot()
        s = (.55 + .45 * back(k, 2.6)) * (1 + .015 * math.sin((t - O['MARCA']) * 9))
        ctx.add('screen', K.scale_im(sl, s), 540, 318 + 30 * (1 - eout(k)), glass=14, alpha=clamp(k * 3))
    K.caps_layer(ctx, t, PAGES_A, y=1450)


# =========================================================================================== B/C: the contact card
def beat_bc(ctx, t):
    P = ctx.post
    u = t - T35
    z = lerp(1.0, 1.08, eout(u / .45)) + .03 * smooth((t - T35) / 2.7)          # hard cut WIDE, then settle
    dx, dy = K.shake(t, LAND, 8., tau=.07, f=18.)
    ctx.cam = dict(z=z, x=540., y=930., dx=dx, dy=dy, rot=0.)
    P['vignette'] = .38; P['sat'] = 1.04
    ctx.wrap = lambda fr: K.add_field(fr, warm_key(), .4)
    if u < .12:                                                         # the slot flicks up and away
        k = clamp(u / .10)
        ctx.add('screen', K.vsmear(brand_slot(), 60 * (1 - k)) if k < 1 else brand_slot(), 540, 318 - 520 * ein(k), alpha=1 - k)
    draw_card(ctx, t)
    K.caps_layer(ctx, t, PAGES_B + PAGES_C, y=360)


# =========================================================================================== D: END CARD
LOGO_W = 640
LOGO_Y = 318
TAG_Y = 520


def brand_plate():
    """the studio melted into the brand space: deep defocus, violet duotone, crushed blacks, halo behind his head."""
    def mk():
        im = E.studio().resize((W // 6, H // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BICUBIC)
        a = np.asarray(im, np.float32) / 255
        L = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
        L = np.clip((L - .04) * 1.3, 0, 1) ** 1.3
        c0 = np.array([9, 8, 16], np.float32); c1 = np.array([32, 22, 82], np.float32); c2 = np.array([112, 92, 216], np.float32)
        col = c0 + (c1 - c0) * np.clip(L * 2.3, 0, 1)[..., None] + (c2 - c1) * (np.clip(L * 2.3 - 1, 0, 1) * .5)[..., None]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        halo = np.exp(-(((xx - 540) / 420) ** 2 + ((yy - 900) / 460) ** 2))[..., None] * np.array([34, 24, 96], np.float32)
        top = np.exp(-(((xx - 540) / 600) ** 2 + ((yy - 330) / 260) ** 2))[..., None] * np.array([34, 26, 90], np.float32)
        col = col + halo + top
        v = 1 - .62 * np.clip(((xx - 540) / 760) ** 2 + ((yy - 900) / 1150) ** 2 - .08, 0, 1)
        return Image.fromarray(np.clip(col * v[..., None], 0, 255).astype(np.uint8))
    return C('bplate', mk)


BOKEH = [(150, 380, 42, .18, 6, -9, (70, 100, 255)), (930, 300, 28, .2, -5, -7, (150, 80, 255)), (960, 1080, 52, .14, -4, -6, (110, 80, 255)),
         (120, 1180, 20, .22, 7, -10, (120, 130, 255)), (650, 180, 14, .24, 3, -8, (170, 140, 255)), (1010, 760, 32, .15, -6, -9, (140, 70, 255)),
         (90, 820, 26, .16, 4, -12, (90, 110, 255)), (420, 120, 22, .18, -3, -6, (160, 120, 255))]


def bokeh(r, col):
    def mk():
        s = int(r * 2 + 8); y, x = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
        d = np.sqrt(x * x + y * y) / r
        a = np.clip((1.0 - d) / .35, 0, 1) ** 1.5 * (.7 + .3 * np.clip((d - .5) / .4, 0, 1))
        im = Image.new('RGBA', (s, s), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.filter(ImageFilter.GaussianBlur(r * .08 + .8))
    return C(('bokeh', r, col), mk)


def logo_assets():
    def mk():
        lg = E.logo(LOGO_W)
        a = lg.getchannel('A'); pad = 140
        big = Image.new('L', (lg.width + 2 * pad, lg.height + 2 * pad)); big.paste(a, (pad, pad))
        glow = Image.new('RGBA', big.size, (0, 0, 0, 0))
        for r, col, m in ((60, (100, 70, 255), 1.2), (18, (170, 150, 255), .9)):
            g = Image.new('RGBA', big.size, col + (0,)); g.putalpha(big.filter(ImageFilter.GaussianBlur(r)).point(lambda v, m=m: int(min(255, v * m * 1.5))))
            glow.alpha_composite(g)
        mask = np.clip((np.asarray(a, np.float32) - 90) / 110, 0, 1)
        return lg, glow, pad, mask
    return C('logo', mk)


def tagline():
    def mk():
        f1, f2 = E.font(64, 500), E.font(64, 800)
        s1, s2 = 'AI-first.', 'Not AI-only.'
        w1, w2 = f1.getlength(s1), f2.getlength(s2); gap = 20
        w = int(w1 + gap + w2) + 60; h = 110
        _, t, _, b = f1.getbbox('AIH')
        m1 = Image.new('L', (w, h)); ImageDraw.Draw(m1).text((30, h / 2 - (t + b) / 2), s1, font=f1, fill=255)
        m2 = Image.new('L', (w, h)); ImageDraw.Draw(m2).text((30 + w1 + gap, h / 2 - (t + b) / 2), s2, font=f2, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sh = Image.new('RGBA', (w, h), (4, 2, 14, 0)); sh.putalpha(Image.fromarray(np.maximum(np.asarray(m1), np.asarray(m2))).filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .8)))
        out.alpha_composite(sh, (0, 3))
        c = Image.new('RGBA', (w, h), E.WHITE + (0,)); c.putalpha(m1); out.alpha_composite(c)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(m2); out.alpha_composite(g)
        return out, np.asarray(m2, np.float32) / 255
    return C('tag', mk)


def draw_logo(ctx, t):
    if t < LOGO0: return
    lg, glow, pad, mask = logo_assets()
    k = clamp((t - LOGO0) / (END0 - LOGO0))
    u = t - END0
    s = 1.0
    if t >= END0: s = 1 + .08 * math.exp(-u / .09) * math.cos(u * 30)
    img = lg
    for t0, d in ((END0 + .04, .45), (SWEEP, .7)):
        sk = (t - t0) / d
        if 0 < sk < 1: img = K.sheen(img, sk, mask, 40, .6)
    if k < 1:                                                          # light wipe draws the logo (landing on 73.28)
        wv = (img.width + 80) * ein(k) - 40
        xs = np.arange(img.width, dtype=np.float32)
        m = np.clip((wv - xs) / 30, 0, 1)[None, :]
        a = np.asarray(img.getchannel('A'), np.float32) * m
        im2 = img.copy(); im2.putalpha(Image.fromarray(a.astype(np.uint8)))
        img = im2
        streak = K.glow_sprite(36, img.height + 140, (215, 205, 255), 10)
        ctx.add('screen', streak, 540 - lg.width / 2 + wv, LOGO_Y, alpha=.95)
        ctx.add('screen', K.glow_sprite(14, img.height + 60, (255, 255, 255), 3), 540 - lg.width / 2 + wv, LOGO_Y, alpha=1)
    ga = (.55 + .1 * math.sin(t * 2.4)) * clamp(k * 1.5)
    if t >= END0: ga += .6 * (1 - eout(u / .5))
    ctx.add('screen', K.scale_im(glow, s), 540, LOGO_Y, alpha=min(1, ga))
    ctx.add('screen', K.scale_im(img, s, lanczos=True), 540, LOGO_Y)
    if 0 <= u < .7:                                                   # shock ring + anamorphic streak
        r = K.ring_sprite(80 + 700 * eout(u / .7), 4, .8 * (1 - u / .7))
        ctx.add('screen', r, 540, LOGO_Y)
        st = K.glow_sprite(1100, 30, (150, 140, 255), 12)
        ctx.add('screen', st, 540, LOGO_Y, alpha=.9 * (1 - eout(u / .35)))


def beat_d(ctx, t):
    P = ctx.post
    u = t - END0
    ke = eio(clamp(u / .6))
    ctx.cam = dict(z=lerp(1.08 + .03 * smooth(2.7 / 2.7), 1.0, ke) + .04 * smooth((t - END0 - .3) / 2.9), x=540., y=lerp(930., 960., ke), dx=0., dy=0., rot=0.)
    if t >= END0:
        ctx.avatar['y'] = 150 * ke
        ctx.bg_img = Image.blend(E.studio(), brand_plate(), clamp(u / .35)) if u < .35 else brand_plate()
        ctx.bg_z = 1 + .05 * smooth(u / 3.2)                         # the brand space drifts deeper: parallax on the hold
        P['flash'] = .06 * (1 - clamp(u / .07)); P['flash_col'] = (232, 222, 255)
        P['bright'] = 1 + .45 * (1 - eout(u / .2))                                # exposure punch (no grey veil)
        P['rgb'] = 5 * (1 - clamp(u / .1))
        # bokeh motes drifting in the brand space
        for i, (x, y, r, a, vx, vy, col) in enumerate(BOKEH):
            px = x + vx * u + 10 * math.sin(u * .6 + i); py = y + vy * u
            tw = .8 + .2 * math.sin(t * 1.3 + i * 1.7)
            ctx.add('behind', bokeh(r, col), px, py, alpha=min(1, a * clamp(u / .6) * tw * 2.0))
    else:
        ctx.wrap = lambda fr: K.add_field(fr, warm_key(), .4)
    P['vignette'] = .34
    draw_logo(ctx, t)
    if t >= TAG0:
        k = clamp((t - TAG0) / .45)
        tg, tm = tagline()
        sk = (t - (SWEEP + .15)) / .6
        if 0 < sk < 1: tg = K.sheen(tg, sk, tm, 30, .55)
        dy = 34 * (1 - expo(k))
        ctx.add('screen', tg, 540, TAG_Y + dy, alpha=clamp(k * 2.2))
    draw_card(ctx, t)


# =========================================================================================== draw
def draw(ctx, lt, t):
    ctx.captions = False
    if t < T35: beat_a(ctx, t)
    elif t < END0 - .2: beat_bc(ctx, t)
    else:
        beat_d(ctx, t)
        if t < END0: K.caps_layer(ctx, t, PAGES_C, y=360)
