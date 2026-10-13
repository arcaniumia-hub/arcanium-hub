"""s01 — HOOK (0.00–6.04): "In the next two seconds, you'll decide if this video is worth your time." + 2.0 s countdown.

Beats (timeline seconds, measured on the voice track, not the syllable estimate):
  0.00  hard open: 3-frame flash-in from black, zoom-blur + RGB settle, camera punch z 1.62 -> 1.20 (expo-out .35 s),
        a diagonal light sweep crosses the studio wall.
  0.70  "TWO": cut wide (avatar lowered/scaled = new camera), a giant extruded gradient "2" slams in BEHIND him (impact).
  1.66  "YOU'LL DECIDE": cut tight on the face; the "2" recedes behind him.
  2.38  "THIS VIDEO": a LUMARC framing reticle (gradient hairline corners, live FRAME 01 timecode, logo) snaps on.
  3.47  "YOUR TIME": whip to a left-weighted framing; a frosted stopwatch card pops in on the right (lands on "TIME").
  4.04  TL[1] silent hold = COUNTDOWN: studio dims, camera creeps in on his eyes, a dial ring around his face depletes,
        precise tabular 2.00 -> 0.00 in a glass panel, accelerating clock ticks, pressure builds (rgb/zoom-blur) into 6.04.
Handoff: s02 owns the 6.04 hit (flash + glitch + RGB) and starts tight on the face.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

START, END = E.span(0, 1)
T_TWO, T_SEC, T_YOU, T_THIS, T_IS, T_YOUR, T_TIME = 0.70, 0.91, 1.66, 2.38, 2.99, 3.47, 3.62
T_CD = E.TL[1]['t0']            # 4.04
T_HIT = END                      # 6.04
TICKS = [4.04, 4.54, 5.00, 5.40, 5.70, 5.90]

CUES = [(0.0, 'boom', {}), (0.02, 'whoosh', {}), (0.08, 'shimmer', {}),
        (T_TWO, 'impact', {}), (T_TWO - .12, 'swoosh_up', {}),
        (T_YOU, 'swipe', {}),
        (T_THIS, 'shutter', {}),
        (T_YOUR, 'whoosh', {}), (T_YOUR + .04, 'glass', {}), (T_TIME, 'pop', {}),
        (T_CD, 'impact', {}), (5.0, 'riser', {'to': T_HIT})] + [(t, 'clock', {}) for t in TICKS]

W, H = E.W, E.H
eout, clamp = E.eout, E.clamp
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x): x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0
def lerp(a, b, k): return a + (b - a) * k

# ---------------------------------------------------------------- art (cached)
def _studio_f():
    return E.cached('a_studio_f', lambda: np.asarray(E.studio(), np.float32))
def _sweep_u():
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        return (xx * .82 + yy * .42)
    return E.cached('a_sweep_u', mk)

def sweep_bg(c, amp=1.0, width=170.):
    """studio plate with an additive diagonal light band centred on diagonal coordinate c."""
    st = _studio_f(); u = _sweep_u()
    k = np.exp(-((u - c) / width) ** 2) * amp
    k2 = np.exp(-((u - c - 260) / 60.) ** 2) * amp * .35          # thin trailing glint
    g = (k + k2)[..., None]
    out = st + g * np.array([150, 130, 255], np.float32) + (st * g * 1.2)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def big_two():
    """giant extruded gradient '2' with depth glow (RGBA)."""
    def mk():
        size = 1180; f = E.font(size, 800)
        l, t, r, b = f.getbbox('2'); gw, gh = r - l, b - t
        pad = 220; w, h = gw + 2 * pad, gh + 2 * pad + 60
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - t), '2', font=f, fill=255)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        # depth glow (big soft purple bloom)
        glow = Image.new('RGBA', (w, h), (110, 70, 255, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(90)).point(lambda v: int(v * .85)))
        out.alpha_composite(glow)
        # extrusion: stacked copies towards bottom-right, deep indigo -> near black
        depth = 34
        for i in range(depth, 0, -1):
            k = i / depth
            col = (int(30 + 40 * (1 - k)), int(20 + 26 * (1 - k)), int(80 + 90 * (1 - k)))
            layer = Image.new('RGBA', (w, h), col + (0,)); layer.putalpha(m)
            out.alpha_composite(layer, (int(i * .55), int(i * 1.0)))
        # face: vertical+horizontal gradient, light at top
        g = np.asarray(E.gradient(w, h, [(150, 170, 255), (140, 110, 255), (196, 120, 255)]), np.float32)
        vy = np.linspace(1.22, .62, h, dtype=np.float32)[:, None, None]
        face = Image.fromarray(np.clip(g * vy, 0, 255).astype(np.uint8)).convert('RGBA'); face.putalpha(m)
        out.alpha_composite(face)
        # inner top highlight (bevel)
        sh = ImageChops_sub(m, m.transform(m.size, Image.AFFINE, (1, 0, 0, 0, 1, 6)))
        hl = Image.new('RGBA', (w, h), (255, 255, 255, 0)); hl.putalpha(sh.filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * .8)))
        out.alpha_composite(hl)
        return out, m
    return E.cached('a_big_two', mk)

def ImageChops_sub(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)

RX0, RY0, RX1, RY1 = 92, 262, W - 92, 1652
def reticle():
    """LUMARC framing reticle: hairline brand-gradient corners with a soft glow + edge ticks (RGBA, full frame)."""
    def mk():
        ss = 2; m = Image.new('L', (W * ss, H * ss)); d = ImageDraw.Draw(m); L, th = 78 * ss, 4 * ss
        x0, y0, x1, y1 = RX0 * ss, RY0 * ss, RX1 * ss, RY1 * ss
        for (x, y, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line((x, y, x + sx * L, y), fill=255, width=th); d.line((x, y, x, y + sy * L), fill=255, width=th)
            d.ellipse((x - th, y - th, x + th, y + th), fill=255)
        for (xa, ya, xb, yb) in [(W // 2 * ss, y0, W // 2 * ss, y0 + 18 * ss), (W // 2 * ss, y1, W // 2 * ss, y1 - 18 * ss),
                                 (x0, (y0 + y1) // 2, x0 + 18 * ss, (y0 + y1) // 2), (x1, (y0 + y1) // 2, x1 - 18 * ss, (y0 + y1) // 2)]:
            d.line((xa, ya, xb, yb), fill=150, width=3 * ss)
        m = m.resize((W, H), Image.LANCZOS)
        g = E.gradient(W, H, [(150, 172, 255), (176, 150, 255), (220, 156, 255)]).convert('RGBA')
        glow = Image.new('RGBA', (W, H), (130, 100, 255, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, int(v * 1.6))))
        out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(glow); g.putalpha(m); out.alpha_composite(g)
        return out
    return E.cached('a_reticle', mk)

def reticle_label(t):
    """'FRAME 01 · 00:02:14' — live timecode in tabular Outfit 500."""
    sec = int(t); fr = int(round((t - sec) * E.FPS)) % E.FPS
    head = E.cached('a_rl_head', lambda: text_tracked('FRAME 01', 36, 500, (236, 234, 248), 5))
    sep = E.cached('a_rl_sep', lambda: text_tracked('\u00b7', 36, 500, (190, 180, 240), 0))
    tc = digits(f'00:{sec:02d}:{fr:02d}', 36, 500, col=(236, 234, 248), track=1)
    w = head.width + sep.width + tc.width + 36; h = max(head.height, tc.height)
    im = Image.new('RGBA', (w + 40, h + 24), (0, 0, 0, 0))
    im.alpha_composite(head, (20, 12)); im.alpha_composite(sep, (20 + head.width + 14, 12)); im.alpha_composite(tc, (20 + head.width + sep.width + 32, 12))
    sh = Image.new('RGBA', im.size, (0, 0, 8, 0)); sh.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * .6)))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, 2)); out.alpha_composite(im); return out

def light_hit(fr, k, col=(196, 182, 255)):
    """a flash that reads as LIGHT, not fog: exposure push + highlight bloom + a faint violet lift (k <= ~.5)."""
    rgb = fr.convert('RGB'); a = np.asarray(rgb, np.float32)
    sm = np.asarray(rgb.resize((W // 4, H // 4), Image.BILINEAR), np.float32)
    lum = sm.mean(2, keepdims=True); hb = sm * np.clip((lum - 80) / 110, 0, 1)
    bloom = np.asarray(Image.fromarray(hb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32)
    y = (a * (1 + 1.7 * k) + bloom * (2.4 * k) + np.array(col, np.float32) * (.20 * k)) / 255.
    y = np.where(y < .72, y, .72 + .28 * (1 - np.exp(-(y - .72) / .28)))      # filmic shoulder: highlights glow, faces keep detail
    return Image.fromarray(np.clip(y * 255, 0, 255).astype(np.uint8)).convert('RGBA')

# ---- tabular digits
def _cell(ch, size, wght, col):
    def mk():
        f = E.font(size, wght); asc, desc = f.getmetrics()
        cw = int(max(f.getlength(d) for d in '0123456789')) if ch.isdigit() else int(f.getlength(ch))
        im = Image.new('RGBA', (cw, asc + desc), (0, 0, 0, 0))
        ImageDraw.Draw(im).text(((cw - f.getlength(ch)) / 2, 0), ch, font=f, fill=col + (255,))
        return im
    return E.cached(('a_cell', ch, size, wght, col), mk)

def digits(s, size, wght=600, col=E.WHITE, track=0):
    cells = [_cell(c, size, wght, col) for c in s]
    w = sum(c.width for c in cells) + track * (len(cells) - 1); h = cells[0].height
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for c in cells: im.alpha_composite(c, (x, 0)); x += c.width + track
    return im

def grad_fill(im, cols=E.GRAD_LIGHT):
    g = E.gradient(im.width, im.height, cols).convert('RGBA'); g.putalpha(im.getchannel('A')); return g

def text_tracked(s, size, wght, col, track):
    f = E.font(size, wght); w = int(sum(f.getlength(c) for c in s) + track * (len(s) - 1)) + 8
    asc, desc = f.getmetrics(); im = Image.new('RGBA', (w, asc + desc), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
    for c in s: d.text((x, 0), c, font=f, fill=col + (255,)); x += f.getlength(c) + track
    return im

# ---- dial ring (angle-mask trick: per-frame progress is one numpy multiply)
def ring(R, thick, nticks, tick_len, major_every=5, ss=2):
    def mk():
        pad = tick_len + 70; S = 2 * (R + pad); S2 = S * ss
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) + .5
        cx = cy = S / 2; dx, dy = xx - cx, yy - cy
        rad = np.hypot(dx, dy); ang = (np.arctan2(dx, -dy) / (2 * math.pi)) % 1.0     # 0 at top, clockwise
        band = np.clip(1 - np.abs(rad - R) / (thick / 2) , 0, 1); band = np.clip(band * (thick / 2), 0, 1)
        # arc colour along the angle: brand gradient
        c = np.array(E.GRAD_LIGHT, np.float32)
        t = ang[..., None]
        col = np.where(t < .5, c[0] + (c[1] - c[0]) * (t / .5), c[1] + (c[2] - c[1]) * ((t - .5) / .5))
        arc = np.dstack([col, band * 255]).astype(np.uint8)
        arc_im = Image.fromarray(arc, 'RGBA')
        glow = arc_im.filter(ImageFilter.GaussianBlur(thick * 1.6))
        track = np.dstack([np.full_like(band, 255)] * 3 + [band * 40]).astype(np.uint8)
        # ticks, drawn supersampled
        ti = Image.new('L', (S2, S2)); d = ImageDraw.Draw(ti)
        for i in range(nticks):
            a = 2 * math.pi * i / nticks; maj = i % major_every == 0
            r0 = (R + thick / 2 + 16) * ss; r1 = r0 + (tick_len if maj else tick_len * .55) * ss
            s_, c_ = math.sin(a), math.cos(a)
            d.line((S2 / 2 + s_ * r0, S2 / 2 - c_ * r0, S2 / 2 + s_ * r1, S2 / 2 - c_ * r1), fill=255, width=int((4 if maj else 2.5) * ss))
        ti = ti.resize((S, S), Image.LANCZOS)
        return dict(S=S, ang=ang, arc=np.asarray(arc_im, np.float32), glow=np.asarray(glow, np.float32), track=Image.fromarray(track, 'RGBA'),
                    ticks=np.asarray(ti, np.float32) / 255.)
    return E.cached(('a_ring', R, thick, nticks, tick_len), mk)

def ring_img(rg, prog, flash=0.0, tick_flash=0.0):
    """RGBA dial: track + remaining arc (0..prog clockwise from top) + glow + ticks (passed ones dim) + head dot."""
    S, ang = rg['S'], rg['ang']
    m = np.clip((prog - ang) * 400, 0, 1)[..., None]
    arc = rg['arc'].copy(); arc[..., 3:] *= m
    gl = rg['glow'].copy(); gl[..., 3:] *= m * (1.0 + .8 * flash)
    tk_on = rg['ticks'] * np.clip((prog - ang) * 400, 0, 1); tk = rg['ticks'] * (.22 + .78 * 0) + tk_on * (.7 + .3 * tick_flash)
    tk = np.clip(tk, 0, 1)
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0)); out.alpha_composite(rg['track'])
    out.alpha_composite(Image.fromarray(np.clip(gl, 0, 255).astype(np.uint8), 'RGBA'))
    out.alpha_composite(Image.fromarray(np.clip(arc, 0, 255).astype(np.uint8), 'RGBA'))
    ticks = Image.new('RGBA', (S, S), (250, 249, 246, 0)); ticks.putalpha(Image.fromarray((np.clip(tk * .55 + rg['ticks'] * .18, 0, 1) * 255).astype(np.uint8)))
    out.alpha_composite(ticks)
    return out

def dot(r, col=(255, 255, 255), glow=(160, 130, 255)):
    def mk():
        S = r * 8; im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        g = Image.new('L', (S, S)); ImageDraw.Draw(g).ellipse((S / 2 - r * 2, S / 2 - r * 2, S / 2 + r * 2, S / 2 + r * 2), fill=255)
        gl = Image.new('RGBA', (S, S), glow + (0,)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(r * 1.2)))
        im.alpha_composite(gl)
        c = Image.new('L', (S * 4, S * 4)); ImageDraw.Draw(c).ellipse((S * 2 - r * 4, S * 2 - r * 4, S * 2 + r * 4, S * 2 + r * 4), fill=255)
        ci = Image.new('RGBA', (S, S), col + (0,)); ci.putalpha(c.resize((S, S), Image.LANCZOS)); im.alpha_composite(ci)
        return im
    return E.cached(('a_dot', r), mk)

def stopwatch_card(prog, label_a=1.0):
    """frosted glass card: mini dial with crown + '2.00' + label."""
    cw, ch = 330, 410
    base = E.cached('a_sw_base', lambda: _sw_base(cw, ch))
    im = base.copy()
    rg = ring(104, 10, 40, 14, 5)
    r = ring_img(rg, prog)
    im.alpha_composite(r, (cw // 2 - rg['S'] // 2, 182 - rg['S'] // 2))
    dg = digits('2.00', 68, 600)
    im.alpha_composite(dg, (cw // 2 - dg.width // 2, 182 - dg.height // 2 + 4))
    a = math.sin(2 * math.pi * prog - math.pi / 2 * 0)
    hx, hy = cw / 2 + 104 * math.sin(2 * math.pi * prog), 182 - 104 * math.cos(2 * math.pi * prog)
    d = dot(9); im.alpha_composite(d, (int(hx - d.width / 2), int(hy - d.height / 2)))
    return im

def _sw_base(cw, ch):
    im = E.glass_panel(cw, ch, 44, alpha=.12, border=.5)
    d = ImageDraw.Draw(im)
    # crown + side button
    d.rounded_rectangle((cw // 2 - 22, 40, cw // 2 + 22, 54), 5, fill=(250, 249, 246, 230))
    d.rounded_rectangle((cw // 2 - 7, 52, cw // 2 + 7, 66), 3, fill=(250, 249, 246, 230))
    lab = text_tracked('SECONDS', 34, 600, (226, 224, 240), 7)
    im.alpha_composite(lab, (cw // 2 - lab.width // 2, ch - 92))
    return im

def _shadow_only(w, h):
    m = Image.new('L', (w + 120, h + 120)); ImageDraw.Draw(m).rounded_rectangle((60, 60, 60 + w, 60 + h), 44, fill=255)
    im = Image.new('RGBA', m.size, (0, 0, 8, 0)); im.putalpha(m.filter(ImageFilter.GaussianBlur(24)).point(lambda v: int(v * .5)))
    return im

def cd_panel_base(w, h):
    def mk():
        im = E.glass_panel(w, h, 60, alpha=.10, border=.42)
        return im
    return E.cached(('a_cdp', w, h), mk)

# ---------------------------------------------------------------- draw
def draw(ctx, lt, t):
    P = ctx.post
    ctx.light = 0.0
    if t < T_CD:
        _speech(ctx, t, P)
    else:
        _countdown(ctx, t, P)
    P['flash'] = 0.0                       # every flash in this section is real light (light_hit), never a grey mix
    if ctx.light > .01:
        k = min(.5, ctx.light); ctx.wrap = lambda fr: light_hit(fr, k)

def _speech(ctx, t, P):
    cam = ctx.cam
    # ---- hard open (frames 0..2) + settle
    fi = int(round(t * E.FPS))
    if fi < 3:
        P['bright'] = [.16, .5, 1.0][fi]
    if fi >= 2: ctx.light = .34 * math.exp(-max(0, t - 2 / 30) / .05)
    P['zoom_blur'] = max(0, 1.3 * (1 - t / .2)) ** 1.5
    P['rgb'] = max(0, 12 * (1 - t / .24))
    # light sweep across the studio wall (behind him)
    if t < .75:
        c = lerp(-300, 2400, eio(t / .72)); ctx.bg_img = sweep_bg(c, amp=.9 * (1 - clamp((t - .55) / .2)))

    if t < T_TWO:                               # A: punch-in open
        k = 1 - (1 - clamp(t / .42)) ** 4
        z = lerp(1.70, 1.20, k) + .03 * clamp((t - .42) / .28)
        cam.update(z=z, x=518, y=760, dx=22, dy=0, rot=lerp(-.035, 0, k))
    elif t < T_YOU:                             # B: wide + the giant 2 behind him
        lt = t - T_TWO
        z = 1.0 + .05 * lt / (T_YOU - T_TWO) + .06 * math.exp(-lt / .09)
        cam.update(z=z, x=540, y=820, dx=0, dy=0, rot=0)
        ctx.avatar.update(s=1.0, y=150)
        ctx.bg_dim = .45 * eout(lt / .15)
        _two(ctx, lt, 1.0, (540, 610))
        ctx.light = max(ctx.light, .38 * math.exp(-lt / .06))
        P['rgb'] = max(P['rgb'], 10 * math.exp(-lt / .07))
        if lt < .12: cam['dy'] = (6 * math.sin(lt * 90)) * (1 - lt / .12)
    elif t < T_THIS:                            # C: tight on the face; the 2 recedes behind him
        lt = t - T_YOU
        z = 1.38 + .05 * lt / (T_THIS - T_YOU)
        cam.update(z=z, x=518, y=720, dx=22, dy=50, rot=0)
        ctx.bg_dim = .45 * (1 - clamp(lt / .5)) * 0 + .3 * (1 - clamp(lt / .6))
        a = 1 - clamp((lt - .15) / .5)
        if a > 0: _two(ctx, 1.0 + lt, a, (540, 470), extra_s=-.10 * eout(lt / .7))
    elif t < T_YOUR:                            # D: "this video" — viewfinder
        lt = t - T_THIS
        z = 1.12 + .05 * lt / (T_YOUR - T_THIS)
        cam.update(z=z, x=540, y=820, dx=0, dy=0, rot=0)
        if lt < T_IS - T_THIS + .25:
            k = eout(lt / .22); out = clamp((lt - (T_IS - T_THIS)) / .2)
            b = reticle(); s = lerp(1.07, 1.0, k) + .04 * E.ein(out)
            bi = b if abs(s - 1) < .002 else b.resize((int(b.width * s), int(b.height * s)), Image.BILINEAR)
            cy = (RY0 + RY1) / 2; ctx.add('screen', bi, W / 2, H / 2 + (cy - H / 2) * s, alpha=k * (1 - out))
            lb = reticle_label(t); lx = W / 2 + (RX0 + 6 - W / 2) * s + lb.width / 2 - 20
            ctx.add('screen', lb, lx, cy + (RY0 + 50 - cy) * s, alpha=k * (1 - out))
            lg = E.logo(220); ctx.add('screen', lg, W / 2 + (RX1 - 18 - W / 2) * s - lg.width / 2, cy + (RY0 + 50 - cy) * s, alpha=.9 * k * (1 - out))
            ctx.light = max(ctx.light, .26 * math.exp(-lt / .05))
    else:                                       # E: "your time" — stopwatch card on the right
        lt = t - T_YOUR
        k = expo(lt / .16)
        z = lerp(1.12 + .05, 1.24, k) + .03 * clamp(lt / .57)
        cam.update(z=z, x=540, y=820, dx=lerp(0, -112, k), dy=0, rot=0)
        if lt < .16: P['zoom_blur'] = max(P['zoom_blur'], .7 * (1 - lt / .16))
        lc = t - (T_TIME - .14)
        if lc > 0:
            pk = E.back(lc / .26, 1.8); s = .55 + .45 * pk
            prog = eout((t - T_TIME) / .3) if t > T_TIME else 0.0
            card = stopwatch_card(prog)
            ci = card.resize((max(1, int(card.width * s)), max(1, int(card.height * s))), Image.BILINEAR) if abs(s - 1) > .01 else card
            fy = 4 * math.sin(lc * 3)
            # into the cut: the card dives towards where the big countdown panel will land
            m = E.ein(clamp((t - 3.90) / (T_CD - 3.90)))
            cx, cy = lerp(836, 540, m), lerp(640 + fy, 1462, m); s2 = 1 + .9 * m
            if m > 0: ci = ci.resize((int(ci.width * s2), int(ci.height * s2)), Image.BILINEAR); P['zoom_blur'] = max(P['zoom_blur'], .5 * m)
            sh = E.cached('a_sw_sh', lambda: _shadow_only(330, 410))
            shi = sh if abs(s * s2 - 1) < .01 else sh.resize((int(sh.width * s * s2), int(sh.height * s * s2)), Image.BILINEAR)
            ctx.add('screen', shi, cx, cy + 16 * s * s2, alpha=clamp(lc / .08) * .9)
            ctx.add('screen', ci, cx, cy, glass=14, alpha=clamp(lc / .08))
        # caption fades out into the cut
        if t > T_CD - .05: ctx.captions = False

def _two(ctx, lt, alpha, pos, extra_s=0.0):
    im, m = big_two()
    k = expo(lt / .22)
    s = (lerp(1.45, 1.0, k) + .03 * lt + extra_s) * 1.0
    sz = (max(1, int(im.width * s)), max(1, int(im.height * s)))
    img = im.resize(sz, Image.BILINEAR)
    sp = (lt - .12) / .55                       # specular sweep across the face of the 2 after it lands
    if 0 < sp < 1:
        mm = np.asarray(m.resize(sz, Image.BILINEAR), np.float32) / 255.
        yy, xx = np.mgrid[0:sz[1]:4, 0:sz[0]:4].astype(np.float32)
        u = (xx / sz[0]) * .8 + (yy / sz[1]) * .5
        band = np.exp(-((u - lerp(-.2, 1.5, eio(sp))) / .07) ** 2)
        band = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).resize(sz, Image.BILINEAR), np.float32) / 255.
        a = (band * mm * .55 * 255).astype(np.uint8)
        hl = Image.new('RGBA', sz, (255, 255, 255, 0)); hl.putalpha(Image.fromarray(a)); img = img.copy(); img.alpha_composite(hl)
    ctx.add('behind', img, pos[0] + 6, pos[1] + lerp(-60, 0, k), alpha=alpha * clamp(lt / .05))

def _countdown(ctx, t, P):
    lt = t - T_CD; dur = T_HIT - T_CD; p = clamp(lt / dur)
    rem = max(0.0, T_HIT - t)
    ctx.captions = False
    # studio dims, he is lit a touch lower, tension vignette
    ctx.bg_dim = .30 + .32 * eout(lt / .5)
    ctx.bg_blur = 3 * eout(lt / .6)
    ctx.avatar['bright'] = .9
    P['vignette'] = .5 + .2 * p; P['sat'] = .9
    # tick pulses
    tk = max([math.exp(-(t - x) / .09) for x in TICKS if x <= t] + [0])
    last = max([x for x in TICKS if x <= t] + [T_CD])
    # camera creeps onto his eyes (ease-in = mounting pressure)
    z = 1.42 + .72 * (p ** 1.7) + .012 * tk
    sh = 3 * tk
    ex, ey = 518, 690
    ctx.cam.update(z=z, x=ex, y=ey, dx=540 - ex + sh * math.sin(t * 97), dy=742 - ey + sh * math.cos(t * 83), rot=.002 * tk * math.sin(t * 50))
    # pressure into the hit (s02 lands it at 6.04)
    pre = clamp((t - (T_HIT - .22)) / .22)
    P['rgb'] = 6 * pre ** 2 + 2.5 * tk
    P['zoom_blur'] = .22 * pre ** 2
    ctx.light = max(ctx.light, .32 * math.exp(-lt / .05), .07 * tk)
    # the dial around his face
    k = expo(lt / .3)
    rg = ring(420, 12, 60, 26, 5)
    r = ring_img(rg, 1 - p, flash=tk, tick_flash=tk)
    # the dial is locked to his head in world space: it scales and travels with the push-in (never cuts his face)
    rs = lerp(1.12, 1.0, k) * (1 + .012 * tk) * (z / 1.42)
    ri = r.resize((int(r.width * rs), int(r.height * rs)), Image.BILINEAR) if abs(rs - 1) > .002 else r
    RC = (540 + sh * math.sin(t * 97), 742 + sh * math.cos(t * 83) + 33.8 * z)
    ctx.add('screen', ri, RC[0], RC[1], alpha=k * .95)
    a = 2 * math.pi * (1 - p); R = 420 * rs
    d = dot(13); ctx.add('screen', d, RC[0] + R * math.sin(a), RC[1] - R * math.cos(a), alpha=k)
    # glass panel with the precise countdown
    pw, ph = 760, 330; py = 1462
    pk = E.back(clamp(lt / .3), 1.6); ps = .82 + .18 * pk
    panel = cd_panel_base(pw, ph).copy()
    hot = clamp((.6 - rem) / .6)
    s = f'{math.floor(rem * 100 + 1e-6) / 100:.2f}'
    dg = digits(s, 214, 600, track=-2)
    if hot > 0:                                  # last 0.6 s: digits charge into the brand gradient
        gd = grad_fill(dg); dg = Image.blend(dg, gd, hot) if True else dg
    sec = E.cached('a_seclab', lambda: text_tracked('SECONDS', 34, 600, (200, 198, 222), 8))
    dx0 = pw // 2 - dg.width // 2
    panel.alpha_composite(dg, (dx0, 4))
    panel.alpha_composite(sec, (pw // 2 - sec.width // 2, ph - 76))
    sc = ps * (1 + .015 * tk + .05 * pre ** 2)
    pi = panel.resize((int(pw * sc), int(ph * sc)), Image.BILINEAR) if abs(sc - 1) > .002 else panel
    ctx.add('screen', pi, W / 2, py, glass=18, alpha=clamp(lt / .06))
