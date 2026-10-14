"""_A_kit.py — helpers shared by s01_hook and s02_alicerce (author A).  Read-only for everybody else.

* measured word onsets (src/tight16k.raw, 5 ms spectrogram + RMS / 80-900 Hz / 1-3 kHz / >3.5 kHz envelopes)
* a 2.5-D rig: studio plate view (zoom/pan with parallax), avatar placement by face position, the house kit rendered
  through a FRAME camera (focal length in px + principal point in frame px) into a tight region -> any camera move is
  a real 3-D move of the house (no resampling), and projection of any model point for annotations
* captions with the engine look on the measured onsets (pages switch on the cuts)
* anti-aliased brand-gradient hairlines with glow, motion blur, light hit, dust motes, light beam
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS

W, H, FPS = E.W, E.H, E.FPS
clamp = E.clamp
def lerp(a, b, k): return a + (b - a) * k
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def eio5(x): x = clamp(x); return x * x * x * (x * (6 * x - 15) + 10)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def eo(x, p=3): x = clamp(x); return 1 - (1 - x) ** p
def ei(x, p=2): x = clamp(x); return x ** p
def back(x, s=1.7): return E.back(x, s)
def decay(t, t0, tau):
    """0 before t0, then exp decay from 1."""
    return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def rnd(seed): return np.random.default_rng(seed)

# ------------------------------------------------------------------------------------------- measured onsets (s)
# seg 0 "Edição boa não é enfeite."
T_EDICAO, T_BOA, T_NAO, T_E0, T_ENFEITE, T_FEI, T_TE = 0.05, 0.60, 0.80, 1.15, 1.27, 1.49, 1.855
# seg 1 "Ela mostra o que você fala."
T_ELA, T_MOSTRA, T_MOS_S, T_TRA, T_O1, T_QUE, T_VOCE, T_FALA = 2.13, 2.44, 2.60, 2.745, 2.82, 2.95, 3.00, 3.32
# seg 2 "Olha só."
T_OLHA, T_SO = HS.W_OLHA, HS.W_SO            # 3.89 / 4.07-4.08
# seg 4 "Pensa na sua marca como uma casa."
T_PENSA, T_NA, T_SUA, T_MARCA, T_COMO, T_UMA, T_CASA = 4.785, 5.15, 5.20, 5.40, 5.89, 6.17, HS.W_CASA
# seg 5 "O alicerce é o seu posicionamento."
T_O5, T_ALICERCE, T_CER, T_E5, T_O5b, T_SEU, T_POSIC, T_MEN = 6.93, HS.W_ALICERCE, HS.W_CER, 7.69, 7.88, 8.06, HS.W_POSIC, 8.92

def jump_t(i):
    """timeline time of the first 30 fps frame that shows segment i's pose: the avatar takes the NEAREST 25 fps
    source frame, so the pose can jump one frame before the segment start -> framing changes must land here."""
    t0 = E.TL[i]['t0']; k = int(round(t0 * 25))
    return next(j for j in range(int(t0 * 30) - 3, int(t0 * 30) + 4) if E.Avatar._k_of(j / 30) >= k) / 30
CUT1, CUT2, CUT3 = jump_t(1), jump_t(2), jump_t(3)                  # 2.0667, 3.8333, 4.40 (jump cuts)
SEG4, CUT5, END2 = E.TL[4]['t0'], jump_t(5), E.TL[6]['t0']          # 4.72 (contiguous), 6.8667 (jump), 9.32

# ------------------------------------------------------------------------------------------- avatar
FACE = (540, 815)            # plate point used as the face anchor (between the eyes and the mouth)
SHOULDER_ROW = 1290          # from this plate row down his shoulders touch the plate's side edges
def avatar_at(ctx, s, fx, fy, alpha=1.0, show=True):
    """place him so that his face anchor lands at (fx, fy) at scale s (the engine scales around the bottom centre)."""
    ctx.avatar.update(show=show, s=s, x=fx - 540 - (FACE[0] - 540) * s, y=fy - 1920 + (1920 - FACE[1]) * s, alpha=alpha)

def cut_row(s, fy):
    """screen row where the plate's side cut starts (should sit at the frame bottom, in the dark)."""
    y = fy - 1920 + (1920 - FACE[1]) * s
    return 1920 + (SHOULDER_ROW - 1920) * s + y

def _shade_img():
    """dark falloff at the bottom of the frame (his desk in shadow): swallows the plate's side cut when he is scaled.
    2160 px wide, centred on him."""
    def mk():
        h = 640; w = 2 * W; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        v = np.clip((yy - 40) / (h - 40), 0, 1) ** 1.6
        side = np.clip((np.abs(xx - w / 2) - 250) / 290, 0, 1) ** 1.3
        a = np.clip(v * (.55 + .45 * side) + side * v * .5, 0, .97)
        im = Image.new('RGBA', (w, h), (7, 6, 12, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im
    return E.cached('A_shade', mk)
def desk_shade(ctx, k=1.0, lift=0, x=W / 2):
    if k > .01:
        im = _shade_img(); x0 = int(round(x - W)); c0 = max(0, -x0); c1 = min(im.width, W - x0)
        ctx.add('front', im.crop((c0, 0, c1, im.height)), x0 + c0, H - 640 + lift, center=False, alpha=min(1.0, k))

# ------------------------------------------------------------------------------------------- studio plate view
def studio_view(z=1.0, fx=540., fy=760., glows=(), blur=0.0, dim=0.0):
    """the studio plate scaled by z (>= 1) about plate point (540, 760), which lands at (fx, fy); clamped so the plate
    always covers the frame.  glows: [(cx, cy, r, (r,g,b), k)] additive light spill on the wall (screen px).
    blur/dim are applied here (at half resolution when blurred: the plate is soft anyway, 4x cheaper) -> leave
    ctx.bg_blur / ctx.bg_dim at 0."""
    z = max(1.0, z); dx, dy = fx - 540, fy - 760
    dx = min(max(dx, -540 * (z - 1)), 540 * (z - 1)); dy = min(max(dy, -1160 * (z - 1)), 760 * (z - 1))
    if blur >= 1.2:
        q = 2                                              # output pixel (x, y) at half res <- plate point
        a = 1 / z; ax, ay = 540, 760; cx, cy = ax + dx, ay + dy
        im = E.studio().transform((W // q, H // q), Image.AFFINE, (a * q, 0, ax - a * cx, 0, a * q, ay - a * cy), Image.BILINEAR)
        for (gx, gy, r, col, k) in glows:
            if k > .01: im = add_glow(im, gx / q, gy / q, r / q, col, k)
        im = im.filter(ImageFilter.GaussianBlur(blur / q))
        if dim > .01: im = Image.blend(im, Image.new('RGB', im.size), dim)
        return im.resize((W, H), Image.BILINEAR)
    im = E.zoom(E.studio(), z, (540, 760), dx, dy) if (z > 1.0005 or abs(dx) > .3 or abs(dy) > .3) else E.studio()
    for (cx, cy, r, col, k) in glows:
        if k > .01: im = add_glow(im, cx, cy, r, col, k)
    if blur > .3: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dim > .01: im = Image.blend(im, Image.new('RGB', im.size), dim)
    return im

def soft(im, blur):
    """gaussian blur at half resolution (for already-soft plates)."""
    if blur < .3: return im
    w, h = im.size
    return im.resize((w // 2, h // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur / 2)).resize((w, h), Image.BILINEAR)

def _glow_sprite(r):
    def mk():
        n = 2 * r; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + .5
        d = np.hypot(xx - r, (yy - r) * 1.15) / r
        return np.clip(np.exp(-d * d * 3.2) - .02, 0, 1).astype(np.float32)
    return E.cached(('A_glow', r), mk)
def add_glow(img, cx, cy, r, col, k):
    """additive soft light (screen-ish) on an RGB image."""
    r = int(max(8, round(r / 8) * 8)); g = _glow_sprite(r)
    x0, y0 = int(cx - r), int(cy - r); x1, y1 = x0 + 2 * r, y0 + 2 * r
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(img.width, x1), min(img.height, y1)
    if cx1 <= cx0 or cy1 <= cy0: return img
    sub = g[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0][..., None] * (np.array(col, np.float32) * k)
    reg = np.asarray(img.crop((cx0, cy0, cx1, cy1)), np.float32)
    out = reg + sub * (1 - reg / 300)
    img = img.copy(); img.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), (cx0, cy0)); return img

# ------------------------------------------------------------------------------------------- the house through a frame camera
def fcam(yaw, pitch, dist, f, target, px, py, roll=0.0):
    """frame camera: f = focal length in frame px, (px, py) = where `target` lands in the 1080x1920 frame."""
    return dict(yaw=yaw, pitch=pitch, dist=dist, f=f, target=tuple(target), px=px, py=py, roll=roll)

def fmix(a, b, k):
    """interpolate two frame cameras (angles/dist/focal/target/principal point)."""
    out = {}
    for key in ('yaw', 'pitch', 'dist', 'f', 'px', 'py', 'roll'): out[key] = lerp(a.get(key, 0.0), b.get(key, 0.0), k)
    out['target'] = tuple(lerp(np.array(a['target'], float), np.array(b['target'], float), k))
    return out

def kitcam(fc, x0, y0, w, h):
    """the kit camera dict that renders exactly the frame-camera view inside the region (x0, y0, w, h)."""
    fov = 2 * math.degrees(math.atan((h / 2) / fc['f']))
    return dict(yaw=fc['yaw'], pitch=fc['pitch'], dist=fc['dist'], fov=fov, target=fc['target'], roll=fc.get('roll', 0.0),
                shift=((fc['px'] - x0 - w / 2) / w, (fc['py'] - y0 - h / 2) / h))

def project(fc, st, P):
    """model-space points (N,3) -> frame px (N,2), depth (N,).  Follows the lot's rise like HS.anchor."""
    c = HS._Cam(kitcam(fc, 0, 0, W, H), W, H)
    lot = st['lot']; P = np.asarray(P, float).reshape(-1, 3) * lot['s'] + np.array([0, lot['dy'], 0])
    return c.proj(P)

LOT = HS.LOT
def house_region(fc, st, pad=46, roof=True):
    """tight frame-space bbox of everything the kit can draw (lot, its floating shadow, house up to the chimney)."""
    pts = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            pts += [(sx * LOT * 1.06, -HS.LOT_TH - .65, sz * LOT * 1.06), (sx * LOT, 0.0, sz * LOT)]
            if roof and (st['outline'] > 0 or st['slab'] > 0):
                pts += [(sx * (HS.HX + .6), 6.5, HS.ZH + sz * (HS.HZ + .7))]
    S, Z = project(fc, st, pts)
    if Z.min() < .4: return 0, 0, W, H
    x0, y0 = S.min(0) - pad; x1, y1 = S.max(0) + pad
    x0, y0 = int(max(0, math.floor(x0))), int(max(0, math.floor(y0))); x1, y1 = int(min(W, math.ceil(x1))), int(min(H, math.ceil(y1)))
    return x0, y0, x1, y1

def rgba_blur(img, r):
    if r < .3: return img
    return img.convert('RGBa').filter(ImageFilter.GaussianBlur(r)).convert('RGBA')

def house(ctx, t, fc, st=None, layer='behind', ss=2, alpha=1.0, blur=0.0, glow=1.0, gap=0.6, region=None):
    """render the shared house (state at t) through frame camera fc into ctx; returns (state, region)."""
    st = HS.state_at(t) if st is None else st
    if st['lot']['a'] <= 0 or alpha <= .01: return st, None
    x0, y0, x1, y1 = region or house_region(fc, st)
    if x1 - x0 < 8 or y1 - y0 < 8: return st, None
    img = HS.render(st, kitcam(fc, x0, y0, x1 - x0, y1 - y0), size=(x1 - x0, y1 - y0), t=t, ss=ss, glow=glow, gap=gap)
    img = rgba_blur(img, blur)
    ctx.add(layer, img, x0, y0, center=False, alpha=alpha)
    return st, (x0, y0, x1, y1)

# ------------------------------------------------------------------------------------------- captions (engine look, measured onsets)
def page(a, z, words, base=92):
    return dict(a=a, z=z, words=[dict(text=w, t0=t0, emph=bool(e)) for (w, t0, e) in words], base=base)

def _layout(p):
    key = ('A_lay', tuple(w['text'] for w in p['words']), p['base'])
    return E.cached(key, lambda: E._layout(dict(words=p['words']), p['base']))

def base_dy(text, sz):
    """vertical offset that puts every word image on a common baseline (word_img centres its padded ink box, so an
    accent (Ê, Ã) or a cedilla shifts the text; the engine shows the step, we correct it)."""
    def mk():
        f = E.font(sz); sw = max(3, sz // 22)
        l, t, r, b = f.getbbox(text, stroke_width=sw); l2, t2, r2, b2 = f.getbbox('A', stroke_width=sw)
        return (t + b) / 2 - (t2 + b2) / 2
    return E.cached(('A_bdy', text, sz), mk)

def captions(ctx, t, pages, y, x=W / 2, special=None, alpha=1.0):
    """draw the active page at centre (x, y) like the engine (word pop on its onset, gradient for emphasis).
    special: {TEXT: fn(ctx, t, img, cx, cy, s, a) -> True if it drew the word itself}."""
    ctx.captions = False
    for p in pages:
        if not (p['a'] <= t < p['z']): continue
        ws = p['words']
        for i, (w, sz, cx, cy) in enumerate(_layout(p)):
            t0 = w['t0']
            if t < t0 - .02: continue
            t1 = ws[i + 1]['t0'] if i + 1 < len(ws) else min(p['z'], t0 + .5)
            lt = t - t0 + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            a = clamp(lt / .05) * alpha
            if p['z'] - t < .06: a *= clamp((p['z'] - t) / .06)
            img = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')[0]
            yy = y + cy + base_dy(w['text'], sz) * s
            if special and w['text'] in special and special[w['text']](ctx, t, img, x + cx, yy, s, a): continue
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, x + cx, yy, alpha=a)

def word_box(pages, text, y, x=W / 2):
    """(cx, cy, w, h) of a caption word's ink in frame px (for strikes / annotations)."""
    for p in pages:
        for w, sz, cx, cy in _layout(p):
            if w['text'] == text:
                l, tt, r, b = E.font(sz).getbbox(text); return x + cx, y + cy + base_dy(text, sz), r - l, b - tt
    return None

# ------------------------------------------------------------------------------------------- hairlines
def strokes(segs, width=3.0, cols=None, glow=9.0, glow_a=.9, core=0.0, ss=3, pad=None):
    """anti-aliased brand-gradient hairlines.  segs: [((x0, y0), (x1, y1), alpha)] or [((x0,y0),(x1,y1),alpha,width)]
    in frame px.  Returns (RGBA, x, y) top-left, or (None, 0, 0)."""
    cols = cols or E.GRAD_LIGHT
    segs = [s for s in segs if s[2] > .01]
    if not segs: return None, 0, 0
    P = np.array([[s[0][0], s[0][1], s[1][0], s[1][1]] for s in segs], float)
    wmax = max([s[3] if len(s) > 3 else width for s in segs])
    pad = pad if pad is not None else int(wmax + glow * 2.6 + 4)
    x0 = int(math.floor(min(P[:, 0].min(), P[:, 2].min()) - pad)); y0 = int(math.floor(min(P[:, 1].min(), P[:, 3].min()) - pad))
    x1 = int(math.ceil(max(P[:, 0].max(), P[:, 2].max()) + pad)); y1 = int(math.ceil(max(P[:, 1].max(), P[:, 3].max()) + pad))
    x0, y0, x1, y1 = max(x0, -200), max(y0, -200), min(x1, W + 200), min(y1, H + 200)
    bw, bh = x1 - x0, y1 - y0
    if bw < 2 or bh < 2: return None, 0, 0
    m = Image.new('L', (bw * ss, bh * ss)); d = ImageDraw.Draw(m)
    for s in segs:
        (ax, ay), (bx, by), a = s[0], s[1], s[2]; wd = (s[3] if len(s) > 3 else width) * ss
        A = ((ax - x0) * ss, (ay - y0) * ss); B = ((bx - x0) * ss, (by - y0) * ss); v = int(255 * min(1.0, a))
        d.line((A, B), fill=v, width=max(1, int(round(wd))))
        r = wd / 2
        for c in (A, B): d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=v)
    m = m.reduce(ss)
    out = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    if glow > 0:
        q = max(1, int(glow // 3))
        gm = m.reduce(q) if q > 1 else m
        gm = gm.filter(ImageFilter.GaussianBlur(max(1, glow / q))).resize((bw, bh), Image.BILINEAR)
        gl = Image.new('RGBA', (bw, bh), (140, 105, 255, 0)); gl.putalpha(gm.point(lambda v: min(255, int(v * glow_a * 1.6))))
        out.alpha_composite(gl)
    g = E.gradient(bw, bh, cols).convert('RGBA'); g.putalpha(m); out.alpha_composite(g)
    if core > 0:
        c = Image.new('RGBA', (bw, bh), (255, 255, 255, 0)); c.putalpha(m.filter(ImageFilter.MinFilter(3)).point(lambda v: int(v * core)))
        out.alpha_composite(c)
    return out, x0, y0

WHITE3 = [E.WHITE, E.WHITE, E.WHITE]

def label_pill(text, size=78, style='grad', pad_x=40, pad_y=22):
    """frosted label pill (the film's callout grammar, same look as s03/s04): glass body + caption-look word.
    70 px glow margin around the pill."""
    def mk():
        f = E.font(size); im, pd = E.word_img(text, size, style)
        l, t_, r, b = f.getbbox(text); tw = r - l
        l2, t2, r2, b2 = f.getbbox('ÁG'); th = b2 - t2
        w = int(tw + 2 * pad_x); h = int(th + 2 * pad_y + size * .10); G = 70; rad = h // 2
        out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
        m = Image.new('L', out.size); ImageDraw.Draw(m).rounded_rectangle((G, G, G + w - 1, G + h - 1), rad, fill=255)
        sh = Image.new('RGBA', out.size, (4, 4, 10, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .45)))
        out.alpha_composite(sh, (0, 8))
        out.alpha_composite(E.glass_panel(w, h, radius=rad, alpha=.16, border=.55), (G, G))
        out.alpha_composite(im, (int(G + pad_x - pd), int(G + h / 2 - im.height / 2 + base_dy(text, size))))
        return out
    return E.cached(('A_pill', text, size, style), mk)

def anchor_dot(r=9, pulse=0.0, col=(250, 249, 246)):
    """anchor dot: white core, purple centre, glow, optional expanding ring (same grammar as s03/s04)."""
    def mk():
        R = int(r * 7); im = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        g = Image.new('L', im.size); ImageDraw.Draw(g).ellipse((R - r * 2.6, R - r * 2.6, R + r * 2.6, R + r * 2.6), fill=255)
        gl = Image.new('RGBA', im.size, (150, 100, 255, 0)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(r * 1.2)).point(lambda v: int(v * .85)))
        im.alpha_composite(gl)
        if pulse > 0:
            rr = r * (1.2 + 5.2 * pulse); a = int(255 * (1 - pulse) ** 1.5)
            d.ellipse((R - rr, R - rr, R + rr, R + rr), outline=col + (a,), width=max(2, int(r * .35)))
        d.ellipse((R - r, R - r, R + r, R + r), fill=col + (255,))
        d.ellipse((R - r * .45, R - r * .45, R + r * .45, R + r * .45), fill=(154, 77, 255, 255))
        return im
    return E.cached(('A_adot', r, round(pulse, 2)), mk)

def add_strokes(ctx, layer, segs, **kw):
    im, x, y = strokes(segs, **kw)
    if im is not None: ctx.add(layer, im, x, y, center=False)

def dashes(p, q, n, phase=0.0, duty=.55):
    """split segment p->q (3-D model points) into n dashes: list of (a, b) 3-D points."""
    p, q = np.asarray(p, float), np.asarray(q, float); out = []
    for i in range(n):
        u0 = (i + phase) / n; u1 = u0 + duty / n
        u0, u1 = max(0.0, u0), min(1.0, u1)
        if u1 > u0: out.append((p + (q - p) * u0, p + (q - p) * u1))
    return out

# ------------------------------------------------------------------------------------------- motion blur / light
def mblur(im, vx, vy):
    """directional motion blur along -(vx, vy) px (premultiplied). Returns (img, ox, oy) centre offset."""
    L = math.hypot(vx, vy)
    if L < 1.5: return im, 0.0, 0.0
    n = int(min(18, max(3, L / 2.4)))
    a = np.asarray(im, np.float32).copy(); a[..., :3] *= a[..., 3:] / 255.
    h, w = a.shape[:2]; px, py = int(math.ceil(abs(vx))), int(math.ceil(abs(vy)))
    acc = np.zeros((h + py, w + px, 4), np.float32)
    x0, y0 = (px if vx > 0 else 0), (py if vy > 0 else 0)
    for i in range(n):
        f = i / (n - 1); ox, oy = int(round(x0 - vx * f)), int(round(y0 - vy * f))
        acc[oy:oy + h, ox:ox + w] += a
    acc /= n
    rgb = np.where(acc[..., 3:] > .5, acc[..., :3] * 255. / np.maximum(acc[..., 3:], 1e-3), 0)
    out = Image.fromarray(np.clip(np.dstack([rgb, acc[..., 3:]]), 0, 255).astype(np.uint8), 'RGBA')
    return out, (acc.shape[1] / 2 - x0 - w / 2), (acc.shape[0] / 2 - y0 - h / 2)

def light_hit(fr, k, col=(196, 182, 255)):
    """a flash that reads as LIGHT: exposure push + highlight bloom + a faint violet lift (k <= ~.5)."""
    rgb = fr.convert('RGB'); a = np.asarray(rgb, np.float32)
    sm = np.asarray(rgb.resize((W // 4, H // 4), Image.BILINEAR), np.float32)
    lum = sm.mean(2, keepdims=True); hb = sm * np.clip((lum - 80) / 110, 0, 1)
    bloom = np.asarray(Image.fromarray(hb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32)
    y = (a * (1 + 1.7 * k) + bloom * (2.4 * k) + np.array(col, np.float32) * (.20 * k)) / 255.
    y = np.where(y < .72, y, .72 + .28 * (1 - np.exp(-(y - .72) / .28)))
    return Image.fromarray(np.clip(y * 255, 0, 255).astype(np.uint8)).convert('RGBA')

def _dot(r):
    def mk():
        n = int(r * 6) + 2; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + .5
        d = np.hypot(xx - n / 2, yy - n / 2) / r
        a = np.clip(np.exp(-d * d * 1.4), 0, 1)
        im = Image.new('RGBA', (n, n), (236, 228, 255, 0)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return E.cached(('A_dot', r), mk)

def motes(ctx, t, box, n=34, seed=7, alpha=1.0, layer='behind', drift=(6, -14), beam=None):
    """floating dust motes in a screen box (x0, y0, x1, y1): slow drift + twinkle, pure function of t.
    beam = (cx, top_y, bottom_y, half_w_top, half_w_bottom): motes inside the light beam glow brighter."""
    if alpha <= .01: return
    x0, y0, x1, y1 = box; r = rnd(seed)
    bx = r.uniform(0, 1, n); by = r.uniform(0, 1, n); sp = r.uniform(.5, 1.4, n); ph = r.uniform(0, 6.28, n)
    sz = r.choice([1.2, 1.6, 2.2, 3.0], n, p=[.35, .3, .22, .13])
    cw, chh = x1 - x0, y1 - y0
    canvas = Image.new('RGBA', (int(cw), int(chh)), (0, 0, 0, 0))
    for i in range(n):
        x = (bx[i] * cw + drift[0] * sp[i] * t + 9 * math.sin(t * .7 * sp[i] + ph[i])) % cw
        y = (by[i] * chh + drift[1] * sp[i] * t) % chh
        a = (.35 + .65 * (.5 + .5 * math.sin(t * 2.1 * sp[i] + ph[i] * 3))) * alpha
        if beam is not None:
            bcx, bt, bb, wt, wb = beam; u = clamp((y + y0 - bt) / max(1, bb - bt)); hw = lerp(wt, wb, u)
            a *= .35 + .9 * clamp(1 - abs(x + x0 - bcx) / max(1, hw))
        d = _dot(float(sz[i]))
        im = d if a >= .99 else E.fade(d, a)
        canvas.alpha_composite(im, (int(x - d.width / 2), int(y - d.height / 2))) if 0 <= x - d.width / 2 and x + d.width / 2 < cw and 0 <= y - d.height / 2 and y + d.height / 2 < chh else None
    ctx.add(layer, canvas, x0, y0, center=False)

def beam_img(wt, wb, h, col=(178, 160, 255), a_top=.30, a_bot=.0):
    """soft volumetric light cone (RGBA): top half-width wt, bottom half-width wb, height h."""
    def mk():
        w = int(2 * max(wt, wb) + 160); yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        u = yy / h; hw = wt + (wb - wt) * u
        edge = np.clip(1 - (np.abs(xx - w / 2) - hw * .55) / (hw * .6 + 30), 0, 1) ** 1.6
        fall = (a_top + (a_bot - a_top) * u) * (1 - np.exp(-u * 9))
        a = np.clip(edge * fall, 0, 1)
        im = Image.new('RGBA', (w, h), col + (0,)); im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        return im.filter(ImageFilter.GaussianBlur(6))
    return E.cached(('A_beam', wt, wb, h, col, a_top, a_bot), mk)

def scaled(im, s):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)

def text_tracked(s, size, wght, col, track):
    f = E.font(size, wght); w = int(sum(f.getlength(c) for c in s) + track * (len(s) - 1)) + 8
    asc, desc = f.getmetrics(); im = Image.new('RGBA', (w, asc + desc), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
    for c in s: d.text((x, 0), c, font=f, fill=col + (255,)); x += f.getlength(c) + track
    return im
