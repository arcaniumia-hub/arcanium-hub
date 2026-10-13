"""s04 — "They don't think 'great business.' They think... next." (14.44–18.00)

TL7  back in the (still drained) studio, founder framed low (camera pan, plate borders never show). On "great"/"business"
     premium type rises in the headroom above him (white GREAT, gradient BUSINESS., screen-locked so it stays sharp) —
     then a red felt-tip Z (uneven width, streaky ink, no glow) strikes it out and it drains to grey.
TL8  tension: tight close-up, slow push, studio falls to black; a frosted "typing…" bubble (glass over the set) keeps
     bouncing through the silence — the viewer's verdict loading.
TL9  SIGNATURE SWIPE on "next.": the whole frame (now a rounded feed card) is flicked UP with motion
     blur and the next post — the same studio, full colour, clean framing — slides in from below and lands at ~17.86.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

START, END = E.span(7, 9)                     # 14.44 – 18.00
T7, T8, T9 = (E.TL[i]['t0'] for i in (7, 8, 9))
# onsets measured on the voice track
W_GREAT, W_BUSINESS, W_THINK_END, W_NEXT = 15.34, 15.66, 16.70, 17.51   # 'think' runs to ~15.33 (k merges into g)
TYPE_ON = W_GREAT - .06                       # big type takes over from the engine caption on the 15.30 frame
STRIKE0, STRIKE1 = 15.80, 15.98
SW0, SW1 = 17.49, 17.84                       # swipe

CUES = [
    (W_GREAT, 'shimmer', {}),
    (STRIKE0, 'tick', {}),                     # marker touches down
    (STRIKE0 + .09, 'tick', {'gain': -4}),     # zag back across
    (STRIKE1, 'impact', {'gain': -8}),         # struck out
    (W_THINK_END + .04, 'type', {}),           # typing bubble
    (16.98, 'type', {'gain': -4}),
    (17.24, 'type', {'gain': -6}),
    (W_NEXT - .03, 'swipe', {}),               # SIGNATURE swipe on "next"
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H
def lerp(a, b, k): return a + (b - a) * k
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
BUB = (830, 420)                              # typing bubble centre (screen space; top edge >= 300)
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
CLEAN_CAM = dict(z=1.12, x=540., y=820., dx=0., dy=0., rot=0.)
CLEAN_AV = dict(show=True, s=1.0, x=0., y=0., alpha=1.0, copies=[], bright=1.0)


def stale_caption(t):
    """True while an engine caption page of an EARLIER segment outlives the cut (would ghost into the new framing)."""
    sg = max(i for i in (7, 8, 9) if t >= E.TL[i]['t0'])
    return any(p['a'] <= t < p['z'] and p['seg'] < sg for p in E.PAGES)


def o2w(cam, ox, oy):
    return cam['x'] + (ox - cam['x'] - cam['dx']) / cam['z'], cam['y'] + (oy - cam['y'] - cam['dy']) / cam['z']


def graded(fr, sat, br, tint=(.97, .99, 1.04)):
    """desaturate towards the channel mean, then tint x brightness (PIL blend + LUT: ~20 ms vs ~200 ms in numpy)."""
    rgb = fr.convert('RGB')
    if abs(sat - 1) > 1e-3:
        rgb = Image.blend(rgb.convert('L', matrix=(1 / 3, 1 / 3, 1 / 3, 0)).convert('RGB'), rgb, sat)
    return rgb.point([min(255, int(v * m * br)) for m in tint for v in range(256)])


# ---------------------------------------------------------------- type art
def spaced(text, size, wght, track):
    """tracked single-line text as an L mask."""
    f = E.font(size, wght); ws = []
    for ch in text:
        l, t, r, b = f.getbbox(ch); ws.append(f.getlength(ch))
    tw = int(sum(ws) + track * (len(text) - 1)); asc, desc = f.getmetrics()
    m = Image.new('L', (tw + 40, asc + desc + 40)); d = ImageDraw.Draw(m); x = 20
    for ch, w in zip(text, ws): d.text((x, 20), ch, font=f, fill=255); x += w + track
    return m.crop(m.getbbox())


def type_img(text, size, wght, track, style):
    """premium display line: soft shadow + fill ('white' | 'grad' | 'grey')."""
    def mk():
        m = spaced(text, size, wght, track); pad = int(size * .4)
        M = Image.new('L', (m.width + 2 * pad, m.height + 2 * pad)); M.paste(m, (pad, pad))
        out = Image.new('RGBA', M.size, (0, 0, 0, 0))
        sh = Image.new('RGBA', M.size, (4, 4, 10, 0)); sh.putalpha(M.filter(ImageFilter.GaussianBlur(size * .12)).point(lambda v: int(v * .75)))
        out.alpha_composite(sh, (0, int(size * .04)))
        if style == 'grad':
            glow = Image.new('RGBA', M.size, (120, 90, 255, 0)); glow.putalpha(M.filter(ImageFilter.GaussianBlur(size * .2)).point(lambda v: int(v * .6)))
            out.alpha_composite(glow)
            g = E.gradient(M.width, M.height, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(M); out.alpha_composite(g)
        else:
            col = E.WHITE if style == 'white' else (120, 120, 132)
            c = Image.new('RGBA', M.size, col + (0,)); c.putalpha(M); out.alpha_composite(c)
        return out
    return E.cached(('s04_type', text, size, wght, track, style), mk)


def rise(img, k, blur_from=10):
    """mask-rise reveal: the line slides up out of an invisible baseline, sharpening as it lands."""
    if k <= 0: return None
    if k >= 1: return img
    w, h = img.size; off = int(h * .55 * (1 - eout(k)))
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.alpha_composite(img.crop((0, 0, w, h - off)), (0, off))
    r = blur_from * (1 - eout(k)) ** 2
    if r > .4: out = out.filter(ImageFilter.GaussianBlur(r))
    return E.fade(out, clamp(k * 3))


GY, BY = 300, 452            # screen-space centres of GREAT / BUSINESS. (fully above his hairline, inside x 90–990)
MARK = (255, 59, 74)


def scribble_pts():
    """hand-drawn Z strike across both lines (screen space): across GREAT, back down-left, across BUSINESS.
    Returns [(x, y, arc_len)] sampled every ~3 px with low-frequency hand wobble."""
    def mk():
        ctrl = [(112, GY + 16), (520, GY + 2), (968, GY - 12), (660, GY + 70), (126, BY + 2), (560, BY - 6), (982, BY - 22)]
        pts = []; L = 0.; prev = None
        for i in range(len(ctrl) - 1):
            (x0, y0), (x1, y1) = ctrl[i], ctrl[i + 1]
            n = int(math.hypot(x1 - x0, y1 - y0) / 3)
            for j in range(n):
                u = j / n; bow = 14 * math.sin(math.pi * u) * (1 if i % 2 == 0 else -1)
                x = lerp(x0, x1, u); y = lerp(y0, y1, u) + bow + 3 * math.sin(L * .021) + 1.5 * math.sin(L * .067)
                if prev: L += math.hypot(x - prev[0], y - prev[1])
                pts.append((x, y, L)); prev = (x, y)
        return pts
    return E.cached('s04_scrib', mk)


def _marker_tex():
    """felt-tip streak texture: noise smeared along x, so the ink has dry streaks and uneven density."""
    def mk():
        from scipy.ndimage import uniform_filter1d, gaussian_filter
        r = np.random.default_rng(7).random((900, W)).astype(np.float32)
        a = gaussian_filter(uniform_filter1d(r, 61, axis=1), (.8, 0))
        a = (a - a.mean()) / (a.std() + 1e-6)
        return np.clip(.86 + .09 * a, .6, 1.0)
    return E.cached('s04_mtex', mk)


def scribble(k):
    """RGBA 1080x900 marker strike drawn up to fraction k (stroke head leads, uneven width, no glow)."""
    pts = scribble_pts(); n = max(2, int(len(pts) * clamp(k)))
    def mk():
        m = Image.new('L', (W, 900)); d = ImageDraw.Draw(m)
        for x, y, L in pts[:n]:
            r = 12.5 + 3.2 * math.sin(L * .011) + 1.8 * math.sin(L * .047 + 1.3)       # pressure varies along the stroke
            r *= .55 + .45 * clamp(L / 60)                                            # pen lands: thin entry
            d.ellipse((x - r, y - r * .82, x + r, y + r * .82), fill=255)             # chisel-ish nib
        m = m.filter(ImageFilter.GaussianBlur(.7))
        a = np.asarray(m, np.float32) / 255. * _marker_tex() * .97
        rgb = np.empty((900, W, 3), np.float32); rgb[:] = MARK
        rgb *= (.9 + .1 * _marker_tex())[..., None]
        return Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
    return E.cached(('s04_scr', n), mk)


def bubble(lt):
    """frosted typing bubble with 3 bouncing dots."""
    base = E.cached('s04_bub', lambda: _bubble_base())
    im = base.copy(); d = ImageDraw.Draw(im); cx, cy = im.width // 2, im.height // 2 - 6
    for i in range(3):
        ph = (lt * 2.4 - i * .18) % 1.0; up = math.sin(min(ph, .5) * 2 * math.pi) ** 2 if ph < .5 else 0
        x = cx + (i - 1) * 48; y = cy - 16 * up; a = int(150 + 105 * up)
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(250, 249, 246, a))
    return im


def _bubble_base():
    w, h = 230, 120
    g = E.glass_panel(w, h, radius=60, alpha=.16, border=.55)
    tail = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0)); tail.alpha_composite(g, (30, 10))
    d = ImageDraw.Draw(tail)
    d.ellipse((22, h - 6, 52, h + 24), fill=(255, 255, 255, 40), outline=(255, 255, 255, 110), width=2)
    d.ellipse((6, h + 26, 22, h + 42), fill=(255, 255, 255, 40), outline=(255, 255, 255, 110), width=2)
    return tail


def round_mask(w, h, r):
    def mk():
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
    return E.cached(('s04_rm', w, h, r), mk)


# ---------------------------------------------------------------- swipe
def flick(u):
    """finger flick: quick grab, fast travel, soft expo landing (0..1)."""
    u = clamp(u)
    return 1 - (1 - u) ** 4 if u > .12 else (u / .12) ** 2 * (1 - (1 - .12) ** 4)


def swipe_y(t):
    return flick((t - SW0) / (SW1 - SW0))


def card_of(fr, sc, radius, vblur):
    """frame -> scaled rounded feed card, optionally vertically motion blurred."""
    if vblur > 1.5:
        f = clamp(vblur, 1, 40); fr = fr.resize((W, max(8, int(H / f))), Image.BOX).resize((W, H), Image.BILINEAR)
    if abs(sc - 1) > .002: fr = fr.resize((int(W * sc), int(H * sc)), Image.BILINEAR)
    fr = fr.convert('RGBA')
    if radius > 1: fr.putalpha(round_mask(fr.width, fr.height, int(radius)))
    return fr


# ---------------------------------------------------------------- TL8 tension state + frozen outgoing post
def tense(t):
    """(cam, bg_dim, sat, br) of the TL8 close-up at t."""
    u = (t - T8) / (T9 - T8 + .1)
    cam = dict(z=1.42 + .2 * clamp(u) ** 1.3, x=540., y=700., dx=0., dy=0., rot=0.)
    return cam, .35 + .4 * smooth((t - T8) / .9), .5, .84 - .06 * smooth((t - T8) / 1.0)


TF = (math.ceil(T9 * E.FPS - 1e-6) - 1) / E.FPS     # last TL8 frame (17.4333)


def frozen_out():
    """the graded TL8 world at TF, rebuilt exactly like the engine composes it (studio dimmed -> avatar -> camera),
    with its own one-frame avatar read (deterministic, cached)."""
    def mk():
        cam, dim, sat, br = tense(TF)
        av = E.Avatar(TF); a = av.frame(TF); av.r.close()
        world = Image.blend(E.studio(), Image.new('RGB', (W, H), (0, 0, 0)), dim).convert('RGBA')
        world.alpha_composite(a)
        fr = E.zoom(world.convert('RGB'), cam['z'], (cam['x'], cam['y']))
        return graded(fr, sat, br)
    return E.cached('s04_frozen', mk)


# ---------------------------------------------------------------- draw
def draw(ctx, lt, t):
    if t < T8:
        # ---------------- TL7: premium "GREAT BUSINESS." above his head (screen-locked, pin-sharp), then marker-struck
        u = (t - T7) / (T8 - T7)
        z = 1.2 + .06 * smooth(u)
        cam = dict(z=z, x=540., y=820., dx=0., dy=(z - 1) * 820 * .97, rot=0.); ctx.cam = cam     # head low: headroom for the type
        ctx.bg_dim = .32
        sat, br = .62, .9
        struck = clamp((t - STRIKE1) / .14)
        if t >= STRIKE1:   # the hit: a short camera knock
            k = clamp(1 - (t - STRIKE1) / .12)
            cam['dx'] += 10 * k * math.sin((t - STRIKE1) * 90); cam['dy'] += 5 * k
        G = type_img('GREAT', 190, 300, 22, 'white'); Gg = type_img('GREAT', 190, 300, 22, 'grey')
        B = type_img('BUSINESS.', 124, 900, 4, 'grad'); Bg = type_img('BUSINESS.', 124, 900, 4, 'grey')
        for img, img_g, oy, t0 in ((G, Gg, GY, TYPE_ON), (B, Bg, BY, W_BUSINESS - .04)):
            k = (t - t0) / .32
            if k <= 0: continue
            if struck > 0: img = Image.blend(img, img_g, struck) if struck < 1 else img_g
            im = rise(img, k)
            if im is None: continue
            sink = 10 * eout((t - STRIKE1) / .3) if t > STRIKE1 else 0
            ctx.add('screen', im, 540, oy + sink)
        if t >= STRIKE0:   # red felt-tip strike, head of the stroke leading
            sk = 1 - (1 - clamp((t - STRIKE0) / (STRIKE1 - STRIKE0))) ** 2      # pen hits fast, eases into the end
            sink = 10 * eout((t - STRIKE1) / .3) if t > STRIKE1 else 0
            ctx.add('screen', scribble(sk), 540, 450 + sink)
        if t >= TYPE_ON or stale_caption(t): ctx.captions = False   # the big type IS the caption for "great business"
        ctx.wrap = lambda fr: graded(fr, sat, br).convert('RGBA')
        ctx.post['vignette'] = .5
        return

    # ---------------- TL8 / TL9: tension close-up
    cam, ctx.bg_dim, sat, br = tense(t)
    ctx.cam = cam
    if stale_caption(t): ctx.captions = False       # TL7's 'GREAT BUSINESS.' page outlives the cut by 2 frames
    ctx.post['vignette'] = .55 + .15 * smooth((t - T8) / 1.0)
    bl = None
    if t >= W_THINK_END:   # typing bubble during the silence
        lt_ = t - W_THINK_END; k = E.popin(lt_, .25, 2.4)
        bl = bubble(lt_)
        if k < 1: bl = bl.resize((max(1, int(bl.width * k)), max(1, int(bl.height * k))), Image.BILINEAR)
        bl = E.fade(bl, clamp(lt_ / .08))

    if t < T9:
        if bl is not None: ctx.add('screen', bl, BUB[0], BUB[1], glass=14)
        ctx.wrap = lambda fr: graded(fr, sat, br).convert('RGBA')
        return

    # ---------------- TL9: the scroll. outgoing = this tense close-up; incoming = clean studio, full colour.
    ctx.captions = False
    p = swipe_y(t); p1 = swipe_y(t - 1 / 30); v = (p - p1) * H        # px/frame
    bump = math.sin(math.pi * clamp((t - SW0 + .04) / (SW1 - SW0 + .08)))
    sc = 1 - .075 * bump; rad = 64 * bump; gap = 46

    # the outgoing post HOLDS the last TL8 frame: the plate's jump cut at T9 (17.44) would otherwise pop inside the
    # unchanged close-up for the frames before the flick. The world is not composed at all (ctx.full).
    ctx.full = frozen_out()

    def wrap(fr):
        out_fr = fr.convert('RGB')
        if bl is not None:      # the typing bubble rides away with the outgoing post
            out_fr = out_fr.convert('RGBA'); E._paste(out_fr, dict(img=bl, xy=(BUB[0] - bl.width // 2, BUB[1] - bl.height // 2), glass=14))
        if t < SW0 - .001:
            return out_fr.convert('RGBA')
        ctx.front = []; ctx.behind = []; ctx.bg_dim = 0.0
        inc = ctx.compose(cam=CLEAN_CAM, avatar=CLEAN_AV)
        vb = abs(v) / 9
        A = card_of(out_fr, sc, rad, vb); Bc = card_of(inc, sc, rad, vb)
        canvas = Image.new('RGBA', (W, H), (7, 7, 10, 255))
        ch = int(H * sc); x0 = (W - A.width) // 2
        ya = int((H - ch) / 2 - p * (ch + gap)); yb = ya + ch + gap
        settle = 0
        if t > SW1: settle = -10 * math.exp(-(t - SW1) * 18) * math.sin((t - SW1) * 30)
        if ya + ch > 0: E._paste(canvas, dict(img=A, xy=(x0, ya), glass=0))
        E._paste(canvas, dict(img=Bc, xy=(x0, int(yb + settle)), glass=0))
        return canvas
    ctx.wrap = wrap

    # "NEXT." — big, screen-locked, kicked up by the flick
    if t >= W_NEXT - .02:
        lt_ = t - W_NEXT + .02
        im = E.word_img('NEXT.', 150, 'grad')[0]
        s = .7 + .3 * back(lt_ / .2, 2.2)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        kick = -40 * math.sin(math.pi * clamp(lt_ / .35))
        a = clamp(lt_ / .05) * clamp((END - .02 - t) / .07)
        ctx.add('screen', im, 540, 1420 + kick, alpha=a)
