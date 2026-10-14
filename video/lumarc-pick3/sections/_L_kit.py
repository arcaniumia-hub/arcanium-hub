"""_L_kit — art for s05_lumarc (author L; read-only for other sections).  Everything cached + deterministic.

    from sections import _L_kit as LK
    LK.K                      lumarc-ia's _E_kit (panel, icon, giant, blob, ring, glow_of, hsmear, vsmear, sheen ...)
    LK.logo_lit(w) / logo_dead(w)        the LUMARC sign, neon-lit (glow baked) / unlit glass
    LK.fingerprint(d, k)                  human thumbprint, ridges revealed centre-out by k (0..1), gradient + glow
    LK.pill_base(w, h)                    dark frosted caption pill
    LK.agent_base() + LK.TASKS            the AI agent panel (6 task rows) — layout constants AP_*
    LK.barbell(w)                         loaded Olympic barbell (side view), lilac rim light
    LK.beam(h, phase, w, ht, hb)          tractor beam / lift column sprite (source below -> load on top)
    LK.card(i, lit)                       the human cards STRATEGY / CREATIVITY / TASTE (glass, icon disc, label)
    LK.tag(n)                             paper price tag with n "$" signs (no digits)
    LK.Clip24(path)                       24 fps reader (croissant pull): .at(src_t) -> RGB 1080x1920
    LK.house_shot(t, u)                   the CASA maquette at night (montage)
    LK.mockups(u)                         laptop (website) + phone (carousel) on the LUMARC night background
    LK.made_by(s)                         "MADE BY lumarc" credit (s = size factor)
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E

K = E._load('_E_kit_L', os.path.join(E.V, 'lumarc-ia/sections/_E_kit.py'))
W, H = E.W, E.H
clamp = E.clamp
WHITE, GRAD, GRAD_L = E.WHITE, E.GRAD, E.GRAD_LIGHT
NIGHT = (14, 14, 20)


def C(key, fn): return E.cached(('L5',) + (key if isinstance(key, tuple) else (key,)), fn)
def lerp(a, b, k): return a + (b - a) * k
def hr(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def colorize(m, col): return K.colorize(m, col)


def cover(im, w, h, cx=.5, cy=.5):
    """cover-fit an image to w x h (crop around the relative centre cx, cy)."""
    im = im.convert('RGB'); s = max(w / im.width, h / im.height)
    r = im.resize((max(w, int(im.width * s + .5)), max(h, int(im.height * s + .5))), Image.BICUBIC)
    x0 = int((r.width - w) * cx); y0 = int((r.height - h) * cy)
    return r.crop((x0, y0, x0 + w, y0 + h))


# ================================================================================================ the LUMARC sign
def logo_lit(w=620):
    def mk():
        lg = E.logo(w); pad = int(w * .16); a = lg.getchannel('A')
        out = K.glow_of(a, (100, 70, 255), w * .055, 1.6, pad)
        out.alpha_composite(K.glow_of(a, (175, 155, 255), w * .016, 1.2, pad))
        out.alpha_composite(lg, (pad, pad))
        return out
    return C(('logo_lit', w), mk)


def logo_dead(w=620):
    """the unlit sign: smoky glass tube, faint."""
    def mk():
        lg = E.logo(w); pad = int(w * .16)
        g = Image.merge('RGBA', [lg.convert('L').point(lambda v: int(v * .45 + 26))] * 3 + [lg.getchannel('A').point(lambda v: int(v * .38))])
        out = Image.new('RGBA', (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0)); out.alpha_composite(g, (pad, pad))
        return out
    return C(('logo_dead', w), mk)


def kicker(text, size=66, col=(236, 232, 255), track=.16):
    """letter-spaced small caps line with a soft dark halo (RGBA)."""
    def mk():
        f = E.font(size, 700); xs = []; x = 0
        for ch in text:
            l, t, r, b = f.getbbox(ch); xs.append(x); x += (r if ch != ' ' else size * .32) + size * track
        w = int(x - size * track) + 2; pad = int(size * .6); h = int(size * 1.3)
        m = Image.new('L', (w + 2 * pad, h + 2 * pad)); d = ImageDraw.Draw(m)
        for ch, x0 in zip(text, xs): d.text((pad + x0, pad + h / 2), ch, font=f, fill=255, anchor='lm')
        m = m.crop(m.getbbox()); pad2 = int(size * .5)
        out = Image.new('RGBA', (m.width + 2 * pad2, m.height + 2 * pad2), (0, 0, 0, 0))
        mm = Image.new('L', out.size); mm.paste(m, (pad2, pad2))
        out.alpha_composite(colorize(mm.filter(ImageFilter.GaussianBlur(size * .22)).point(lambda v: int(v * .8)), (4, 3, 12)))
        out.alpha_composite(colorize(mm, col))
        return out
    return C(('kicker', text, size, col, track), mk)


# ================================================================================================ the human touch
def fingerprint(d=96, k=1.0):
    """thumbprint (whorl): ~13 distorted loops, ridges broken like real skin; revealed centre-out by k."""
    n_rings = 13; kq = int(round(clamp(k) * 24))

    def rings():
        S = 4; n = d * S; out = []
        rng = np.random.default_rng(11)
        for r in range(n_rings):
            rr = (r + 1.1) / (n_rings + .6)
            th = np.linspace(0, 2 * np.pi, 160)
            wob = 1 + .05 * np.sin(3 * th + r * .7) + .03 * np.sin(5 * th + r * 1.3)
            x = .5 + .40 * rr * np.cos(th) * wob * .86
            y = .52 + .46 * rr * np.sin(th) * wob - .05 * rr * (np.sin(th) < 0) * np.abs(np.sin(th))
            gaps = sorted(rng.uniform(0, 160, 2 if r > 2 else 1).astype(int))
            out.append((rr, [(float(x[i]) * n, float(y[i]) * n) for i in range(160)], gaps))
        return out
    R = C('fp_rings', rings)

    def mk():
        S = 4; n = d * S; m = Image.new('L', (n, n)); dr = ImageDraw.Draw(m)
        lw = max(2, int(n * .022)); lim = kq / 24
        for rr, pts, gaps in R:
            if rr > lim + .02: continue
            g0 = gaps[0]; seg = pts[g0 + 9:] + pts[:g0] if len(gaps) == 1 else pts[gaps[0] + 7:gaps[1]]
            if len(seg) > 2: dr.line(seg, fill=255, width=lw, joint='curve')
            if len(gaps) > 1:
                seg2 = pts[gaps[1] + 7:] + pts[:gaps[0]]
                if len(seg2) > 2: dr.line(seg2, fill=255, width=lw, joint='curve')
        m = m.resize((d, d), Image.LANCZOS)
        pad = int(d * .3)
        out = K.glow_of(m, (120, 90, 255), d * .06, 1.5, pad)
        g = K.grad_img(d, d, GRAD_L, .3)
        out.alpha_composite(colorize(m, g), (pad, pad))
        return out
    return C(('fp', d, kq), mk)


def disc(d=118, alpha=.9):
    """dark glass button disc with a gradient rim (holds the fingerprint)."""
    def mk():
        S = 4; n = d * S; m = Image.new('L', (n, n)); ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
        rim = Image.new('L', (n, n)); ImageDraw.Draw(rim).ellipse((2, 2, n - 3, n - 3), outline=255, width=int(n * .035))
        m = m.resize((d, d), Image.LANCZOS); rim = rim.resize((d, d), Image.LANCZOS)
        out = colorize(m.point(lambda v: int(v * alpha)), (20, 17, 40))
        yy = np.linspace(0, 1, d, dtype=np.float32)[:, None]
        sh = (np.clip(1 - yy / .5, 0, 1) ** 2 * 60 * np.asarray(m, np.float32) / 255).astype(np.uint8)
        out.alpha_composite(colorize(Image.fromarray(np.repeat(sh, d, 1) if sh.shape[1] == 1 else sh), (255, 255, 255)))
        out.alpha_composite(colorize(rim, K.grad_img(d, d, GRAD_L, .2)))
        return out
    return C(('disc', d, alpha), mk)


def pill_base(w, h, alpha=.74):
    p, pad = K.panel(w, h, h // 2, fill=(16, 13, 34), a=alpha, border=.7)
    return p, pad


# ================================================================================================ the AI agent panel
TASKS = [('cut', 'Editing'), ('cc', 'Captions'), ('color', 'Color'), ('versions', 'Versions'), ('formats', 'Formats'), ('upscale', 'Resizing')]
AP_W, AP_H = 548, 586
AP_ROW0, AP_ROWP = 118, 74
AP_BAR0, AP_BAR1 = 286, 438
AP_STAT = 494
AP_ORB = (486, 56)


def agent_base():
    def mk():
        p, pad = K.panel(AP_W, AP_H, 40, fill=(14, 12, 30), a=.70, border=.65)
        im = p.copy(); d = ImageDraw.Draw(im); o = pad
        sp = K.icon('spark', 42, GRAD_L); im.alpha_composite(sp, (o + 30, o + 35))
        d.text((o + 86, o + 57), 'AI Agent', font=E.font(44, 700), fill=WHITE, anchor='lm')
        d.line((o + 28, o + 104, o + AP_W - 28, o + 104), fill=(255, 255, 255, 34), width=2)
        for i, (ic, lab) in enumerate(TASKS):
            cy = o + AP_ROW0 + AP_ROWP * i + AP_ROWP // 2
            d.rounded_rectangle((o + 28, cy - 25, o + 78, cy + 25), 14, fill=(255, 255, 255, 18), outline=(255, 255, 255, 40), width=1)
            im.alpha_composite(K.icon(ic, 32, (225, 220, 250)), (o + 37, cy - 16))
            d.rounded_rectangle((o + AP_BAR0, cy - 6, o + AP_BAR1, cy + 6), 6, fill=(255, 255, 255, 26))
        return im, pad
    return C('agent_base', mk)


def row_label(text, done):
    return C(('rowlab', text, done), lambda: E.text_im(text, 38, 600, WHITE if done else (168, 166, 194)))


def check_badge(r=23):
    def mk():
        S = 4; n = 2 * r * S; m = Image.new('L', (n, n)); ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
        m = m.resize((2 * r, 2 * r), Image.LANCZOS)
        im = colorize(m, K.grad_img(2 * r, 2 * r, GRAD, .3))
        im.alpha_composite(K.icon('check', int(r * 1.5), (255, 255, 255), .1), (int(r * .25), int(r * .28)))
        pad = 16; out = K.glow_of(m, (120, 90, 255), 8, 1.2, pad); out.alpha_composite(im, (pad, pad)); return out
    return C(('chk', r), mk)


def spinner(ang, r=17):
    im = Image.new('RGBA', (2 * r + 8, 2 * r + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 4 + 2 * r, 4 + 2 * r), outline=(255, 255, 255, 40), width=4)
    d.arc((4, 4, 4 + 2 * r, 4 + 2 * r), ang, ang + 110, fill=(190, 176, 255, 255), width=4)
    return im


def bar_fill(w):
    full = C('barfull', lambda: (lambda g, m: colorize(m, g))(K.grad_img(AP_BAR1 - AP_BAR0, 12, GRAD_L),
                                                               _rr_mask(AP_BAR1 - AP_BAR0, 12, 6)))
    if w < 4: return None
    return full.crop((0, 0, int(w), 12))


def _rr_mask(w, h, r):
    m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m


def orb(t, hot=0.0):
    """the agent: a glowing gradient sphere with an orbiting ring."""
    def base():
        r = 22; S = 4; n = 2 * r * S
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n - .5
        dd = np.sqrt(xx ** 2 + yy ** 2) / .5
        hi = np.exp(-(((xx + .16) ** 2 + (yy + .18) ** 2) / .03))
        col = np.dstack([lerp(95, 175, 1 - dd) + 80 * hi, lerp(80, 150, 1 - dd) + 80 * hi, np.full_like(dd, 255)])
        al = np.clip((1 - dd) * 40, 0, 1) * 255
        im = Image.fromarray(np.dstack([np.clip(col, 0, 255), al]).astype(np.uint8), 'RGBA').resize((2 * r, 2 * r), Image.LANCZOS)
        pad = 40; out = K.glow_of(im.getchannel('A'), (120, 90, 255), 14, 1.6, pad); out.alpha_composite(im, (pad, pad)); return out
    b = C('orb', base)
    s = 1 + .06 * math.sin(t * 9) + .35 * hot
    im = K.scale_im(b, s).copy(); d = ImageDraw.Draw(im); c = im.width / 2
    a0 = (t * 400) % 360; R = 32 * s
    d.arc((c - R, c - R * .42, c + R, c + R * .42), a0, a0 + 240, fill=(210, 200, 255, 220), width=3)
    return im


def barbell(w=470):
    """loaded Olympic barbell, side view: chrome bar, two dark iron plates + a collar each side, lilac rim light.
    Returns RGBA; centre = bar centre."""
    def mk():
        S = 3; n = w * S; h = int(n * .44); im = Image.new('RGBA', (n, h), (0, 0, 0, 0)); cy = h / 2
        def cyl(x0, x1, hh, lo, hi, rim=True, r=None):
            """vertical-gradient rounded slab from x0..x1, height hh (a plate / collar / bar seen from the side)."""
            ww, H2 = int(x1 - x0), int(hh)
            m = Image.new('L', (ww, H2)); ImageDraw.Draw(m).rounded_rectangle((0, 0, ww - 1, H2 - 1), r if r is not None else min(ww, H2) // 4, fill=255)
            yy = np.linspace(-1, 1, H2, dtype=np.float32)[:, None]
            xx = np.linspace(-1, 1, ww, dtype=np.float32)[None, :]
            v = lo + (hi - lo) * np.clip(1 - (yy + .45) ** 2, 0, 1) + 26 * np.exp(-((yy + .55) / .12) ** 2)
            v = v + 12 * xx * (-1)
            rgb = np.dstack([v * .95, v * .97, v * 1.08])
            if rim: rgb = rgb + np.clip((xx - .55) / .45, 0, 1)[..., None] * np.array([120, 95, 230]) * .8
            sl = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA'); sl.putalpha(m)
            im.alpha_composite(sl, (int(x0), int(cy - H2 / 2)))
        cyl(n * .01, n * .99, h * .07, 110, 215, rim=False, r=int(h * .03))                  # the bar (chrome)
        for sgn in (-1, 1):
            def X(f): return n / 2 + sgn * f * n / 2
            xa, xb = sorted((X(.50), X(.545))); cyl(xa, xb, h * .24, 110, 215, rim=False, r=6)  # collar
            for f0, f1, hh in ((.545, .68, .98), (.68, .79, .80), (.79, .87, .62)):          # iron plates
                xa, xb = sorted((X(f0), X(f1))); cyl(xa, xb, h * hh, 14, 46, rim=False, r=int(n * .014))
                im2 = Image.new('L', (n, h)); ImageDraw.Draw(im2).line([(xb if sgn > 0 else xa, cy - h * hh * .42), (xb if sgn > 0 else xa, cy + h * hh * .42)], fill=255, width=S * 3)
                im.alpha_composite(colorize(im2.filter(ImageFilter.GaussianBlur(S)).point(lambda v: int(v * .75)), (160, 135, 255)))
            xa, xb = sorted((X(.87), X(.90))); cyl(xa, xb, h * .20, 110, 215, rim=False, r=6)   # outer clip
        a = im.getchannel('A')
        top = ImageChops.subtract(a, ImageChops.offset(a, 0, S * 3))
        im.alpha_composite(colorize(top.point(lambda v: int(v * .5)), (220, 220, 240)))
        return im.resize((w, int(h / S)), Image.LANCZOS)
    return C(('barbell', w), mk)


def beam(h, phase, w=300, ht=122, hb=14):
    """tractor beam: soft lilac cone / column (half-width ht at the load on top, hb at the source below), scanlines
    rising."""
    h = max(2, int(h)); im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if h < 4: return im
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = yy / max(1, h - 1)
    half = lerp(ht, hb, v)
    edge = np.clip(1 - np.abs(xx - w / 2) / half, 0, 1) ** 1.3
    lines = .72 + .28 * np.sin((yy + phase * 900) / 7.0)
    al = np.clip(edge * lines * .5 + np.exp(-((xx - w / 2) / (half * .22)) ** 2) * .55, 0, 1)
    col = np.dstack([np.full_like(al, 196), np.full_like(al, 182), np.full_like(al, 255)])
    return Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), 'RGBA')


# ================================================================================================ the human cards
CARDS = [('knight', 'STRATEGY'), ('spark', 'CREATIVITY'), ('gem', 'TASTE')]
CARD_W, CARD_H = 476, 150


def card(i, lit=1.0):
    """horizontal glass card: gradient icon disc + bold label. lit is quantised (0..1 in 8 steps)."""
    q = int(round(clamp(lit) * 8))

    def mk():
        k = q / 8
        p, pad = K.panel(CARD_W, CARD_H, 38, fill=(16, 13, 34), a=.72, border=.55 + .4 * k, glow=.9 * k)
        im = p.copy(); o = pad
        if k > 0:   # gradient flood from the left (lit)
            g = K.grad_img(CARD_W, CARD_H, GRAD, 0); m = _rr_mask(CARD_W, CARD_H, 38)
            ramp = np.clip(1.15 - np.linspace(0, 1, CARD_W, dtype=np.float32)[None, :] * 1.25, 0, 1) * .42 * k
            m = Image.fromarray((np.asarray(m, np.float32) * ramp).astype(np.uint8))
            im.alpha_composite(colorize(m, g), (o, o))
        dd = 100; cx, cy = o + 26 + dd // 2, o + CARD_H // 2
        dm = Image.new('L', (dd * 4, dd * 4)); ImageDraw.Draw(dm).ellipse((0, 0, dd * 4 - 1, dd * 4 - 1), fill=255)
        dm = dm.resize((dd, dd), Image.LANCZOS)
        im.alpha_composite(K.glow_of(dm, (120, 90, 255), 12, .9 + .9 * k, 30), (cx - dd // 2 - 30, cy - dd // 2 - 30))
        im.alpha_composite(colorize(dm, K.grad_img(dd, dd, GRAD if k > .5 else [(60, 56, 100)] * 3, .3)), (cx - dd // 2, cy - dd // 2))
        ic, lab = CARDS[i]
        icn = K.gem_icon(64) if ic == 'gem' else K.icon(ic, 60, (255, 255, 255))
        im.alpha_composite(icn, (cx - icn.width // 2, cy - icn.height // 2 + (2 if ic == 'knight' else 0)))
        f = E.font(50, 800); col = WHITE if k > .5 else (200, 198, 222)
        ImageDraw.Draw(im).text((o + 150, cy + 2), lab, font=f, fill=col, anchor='lm')
        return im
    return C(('card', i, q), mk)


# ================================================================================================ the price tag
def tag(n=4, w=250):
    """cream paper price tag (notched left end, eyelet), n dollar signs in dark ink (no digits). Pivot = eyelet."""
    def mk():
        S = 3; tw, th = w * S, int(w * .5 * S); pad = 26 * S
        im = Image.new('RGBA', (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
        m = Image.new('L', im.size); d = ImageDraw.Draw(m)
        x0, y0, x1, y1 = pad, pad, pad + tw, pad + th; nt = th * .5
        d.polygon([(x0 + nt, y0), (x1, y0), (x1, y1), (x0 + nt, y1), (x0, y0 + th / 2)], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(S * 2)).point(lambda v: 255 if v > 128 else 0)
        sh = m.filter(ImageFilter.GaussianBlur(S * 9)).point(lambda v: int(v * .55))
        im.alpha_composite(colorize(sh, (0, 0, 8)), (0, S * 8))
        yy = np.linspace(0, 1, im.height, dtype=np.float32)[:, None, None]
        paper = np.broadcast_to(np.array([248, 242, 228], np.float32), (im.height, im.width, 3)) * (1.02 - .1 * yy)
        pim = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert('RGBA'); pim.putalpha(m)
        im.alpha_composite(pim)
        ex, ey, er = x0 + nt * .78, y0 + th / 2, th * .085                # eyelet
        dd = ImageDraw.Draw(im)
        dd.ellipse((ex - er * 1.6, ey - er * 1.6, ex + er * 1.6, ey + er * 1.6), fill=(205, 196, 176, 255))
        dd.ellipse((ex - er, ey - er, ex + er, ey + er), fill=(0, 0, 0, 0))
        if n:
            txt = '$' * n; fs = int(th * .62)
            while fs > 10 and E.font(fs, 800).getbbox(txt)[2] > (tw - nt) * .80: fs -= 4
            f = E.font(fs, 800)
            dd.text(((x0 + nt + x1) / 2 + nt * .1, ey + S * 2), txt, font=f, fill=(24, 22, 44, 255), anchor='mm')
        rim = ImageChops.subtract(m, ImageChops.offset(m, -S * 4, 0))
        im.alpha_composite(colorize(rim.point(lambda v: int(v * .7)), (170, 150, 255)))
        out = im.resize((im.width // S, im.height // S), Image.LANCZOS)
        out.info['pivot'] = (ex / S, ey / S)
        return out
    return C(('tag', n, w), mk)


def dollar(size=70):
    return C(('dollar', size), lambda: E.text_im('$', size, 800, (24, 22, 44)))


# ================================================================================================ sparkles / streaks
def star(size=60, col=(255, 255, 255)):
    """4-point glint with a soft core (RGBA)."""
    def mk():
        n = size * 3; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
        r = np.hypot(xx, yy) / (n / 2)
        a = np.exp(-np.abs(xx) / (n * .022)) * np.exp(-np.abs(yy) / (n * .30)) + np.exp(-np.abs(yy) / (n * .022)) * np.exp(-np.abs(xx) / (n * .30))
        a = np.clip(a * 1.1 + np.exp(-(r / .12) ** 2), 0, 1) * np.clip(1 - r, 0, 1)
        im = Image.fromarray(np.dstack([np.broadcast_to(np.array(col, np.float32), (n, n, 3)), a * 255]).astype(np.uint8), 'RGBA')
        return im.resize((size, size), Image.LANCZOS)
    return C(('star', size, col), mk)


def streak(length, thick, col=(226, 220, 255), a=1.0):
    """horizontal speed line: hot white head on the left, gradient tail fading right (RGBA)."""
    def mk():
        L, T = int(length), max(2, int(thick)); pad = T * 3
        x = np.linspace(0, 1, L, dtype=np.float32)[None, :]
        y = np.linspace(-1, 1, T + 2 * pad, dtype=np.float32)[:, None]
        prof = np.exp(-(y * (T + 2 * pad) / (T * 1.1)) ** 2)
        al = prof * (1 - x) ** 1.6 * a
        core = np.broadcast_to(np.array(col, np.float32), (T + 2 * pad, L, 3))
        tail = np.array(GRAD_L[1], np.float32)
        rgb = core * (1 - x[..., None] * .8) + tail * (x[..., None] * .8)
        return Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), 'RGBA')
    return C(('streak', int(length), int(thick), col, round(a, 2)), mk)


# ================================================================================================ montage sources
class Clip24:
    """native-frame reader for 24 fps sources (the croissant pull): at(src_t) -> frame floor(src_t * 24), RGB W x H.
    Monotonic reads reuse one ffmpeg pipe; a pure function of src_t."""
    def __init__(self, path, fps=24, size=(W, H)): self.path, self.fps, self.size, self.r, self.k0 = path, fps, size, None, None
    def at(self, src_t):
        k = max(0, int(math.floor(src_t * self.fps + 1e-6)))
        if self.r is not None and (k < self.k0 + self.r.n - 1 or k > self.k0 + self.r.n + 40): self.r.close(); self.r = None
        if self.r is None:
            self.k0 = k
            self.r = E.Reader(self.path, (k - .5) / self.fps, 3.0, vf=f'scale={self.size[0]}:{self.size[1]}', exact=True)
        return self.r.get(k - self.k0, self.size)
_c24 = {}
def clip24(path):
    if path not in _c24: _c24[path] = Clip24(path)
    return _c24[path]


def night_bg():
    """deep LUMARC night: radial violet glow low, black at the top, fine stars."""
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.hypot((xx - 540) / 900, (yy - 1250) / 760)
        g = np.clip(1 - r, 0, 1) ** 1.6
        base = np.array(NIGHT, np.float32) * .7
        col = base + g[..., None] * np.array([70, 44, 170], np.float32) * .9
        rng = np.random.default_rng(5); im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        for i in range(140):
            x, y = rng.uniform(0, W), rng.uniform(0, H * .55); b = int(rng.uniform(60, 200))
            d.point((x, y), fill=(b, b, min(255, b + 30)))
        return im
    return C('night_bg', mk)


def house_state():
    def mk():
        HS = E.house(); st = dict(HS.state_at(37.6))
        st['vid'] = [0.0] * len(st['vid']); st['people_t'] = -1.0
        return st
    return C('house_st', mk)


def house_shot(u):
    """the CASA maquette at night, fast orbit (u = 0..1 over the shot) -> RGB frame."""
    HS = E.house()
    yaw = lerp(22, 38, u); cam = dict(yaw=yaw, pitch=lerp(15, 12, u), dist=lerp(27.0, 24.5, u), fov=30, target=(0.0, 1.6, 0.0))
    im = HS.render(house_state(), cam, size=(1080, 1080), t=37.6, ss=2)
    fr = night_bg().copy().convert('RGBA')
    fr.alpha_composite(K.blob(1100, 420, (90, 60, 220), 130, .6), (540 - 680, 1180 - 420))
    fr.alpha_composite(im, (0, 380))
    return fr.convert('RGB')


def mockups(u):
    """laptop (OLIVA website) + phone (coffee carousel) on the LUMARC night (u 0..1 over the shot) -> RGB."""
    def lap():
        im = E.laptop(Image.open(os.path.join(E.SHOWCASE_A, 'website.png')), 920)
        return E.shadow(im, 40, .7, (0, 30))
    def ph():
        im = E.phone(Image.open(os.path.join(E.SHOWCASE_A, 'carousel_1.png')), 380)
        return E.shadow(im, 40, .75, (0, 30))
    L, P = C('mk_lap', lap), C('mk_ph', ph)
    fr = night_bg().copy().convert('RGBA')
    fr.alpha_composite(K.blob(900, 700, (100, 70, 240), 160, .5), (540 - 630, 900 - 520))
    s1 = .94 + .05 * u; s2 = .98 + .07 * u
    l2 = K.scale_im(L, s1); p2 = K.scale_im(P, s2)
    fr.alpha_composite(l2, (int(540 - 24 * u - l2.width / 2), int(700 - l2.height / 2)))
    fr.alpha_composite(p2, (int(790 + 18 * u - p2.width / 2), int(1120 - 50 * u - p2.height / 2)))
    return fr.convert('RGB')


def burger(u):
    """the burger close-up (showcase still), slow push + warm light."""
    b = C('burger', lambda: cover(Image.open(os.path.join(E.SHOWCASE_A, 'close_food.png')), W, H, .5, .45))
    return E.zoom(b, 1.0 + .10 * u, (540, 900), rot=math.radians(-1.2 * u))


def made_by(s=1.0):
    """'MADE BY  lumarc' credit (letter-spaced caps + the logo), for the letterbox bar (s = size factor)."""
    def mk():
        lw = int(230 * s); kk = kicker('MADE BY', int(30 * s), (205, 200, 230), .34); lg = logo_lit(lw)
        lp = int(lw * .16); gap = int(26 * s); x2 = kk.width - int(15 * s) + gap - lp
        w = x2 + lg.width; h = max(kk.height, lg.height)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        im.alpha_composite(kk, (0, (h - kk.height) // 2 + 3)); im.alpha_composite(lg, (x2, (h - lg.height) // 2))
        return im
    return C(('made_by', s), mk)
