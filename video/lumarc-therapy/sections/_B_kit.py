"""_B_kit — private helpers for s03_xmas / s04_flyer (author B).

* paper_sheet()      the hideous flyer as a REAL printed sheet: home-printer white margins, ink that never reaches pure
                     white/black, paper fibre + mottling, quarter-fold creases with panel shading, a dog-eared corner,
                     warm window light falloff and a soft contact shadow (RGBA, cached, hi-res).
* marker strokes     hand-drawn red-marker ellipses (wobble, overshoot, pressure taper) and handwritten digits drawn
                     progressively (frac 0..1) — the "count the fonts" telestrator.
* place()            affine placement of a paper-space image on the 1080x1920 screen (point -> point, scale, rotation).
* ig2021_screen()    dark-mode Instagram post screen of Kevin's last post (Dec 24, 2021 · 3 likes), fictional handles,
                     generic chrome (no official logos/wordmarks).
Everything is a pure function of its arguments (cached by key) so the sections stay pure functions of t.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import engine as E

W, H = E.W, E.H
_INTER = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
_EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'

def inter(size, weight='Regular'):
    return E.cached(('B_inter', size, weight), lambda: ImageFont.truetype(_INTER % weight, size))

def emoji(ch, size):
    """colour emoji glyph as RGBA of height ~size (Noto Color Emoji is a bitmap font at 109 px)."""
    def mk():
        try:
            f = ImageFont.truetype(_EMOJI, 109)
            im = Image.new('RGBA', (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
            bb = im.getbbox(); im = im.crop(bb)
            return im.resize((max(1, int(im.width * size / im.height)), size), Image.LANCZOS)
        except Exception:
            return Image.new('RGBA', (size, size), (0, 0, 0, 0))
    return E.cached(('B_emoji', ch, size), mk)

# ------------------------------------------------------------------------------------------------ captions
# B_review: word onsets measured on src/voice16k.raw (10 ms RMS envelope + 35 ms-window band energies / zero-crossing
# rate / spectral centroid, edit-timeline seconds), one entry per caption word in order. Notes: LAST = the voiced /l/
# after "your" (10.63); POST = /p/ release after the "st"-less pause (10.97); CHRISTMAS = /k/ burst (11.55);
# TWENTY-ONE = second /t/ (13.00, vowel 13.10); I'VE = 13.95 (vowel 13.96); BEEN /b/ 14.16; BUSY /b/ release 14.37;
# DO = its affricated release 15.64; SHOW = /sh/ 15.86; UP = vowel 16.10; FLYER = the long /f/ 17.13 (the voiced "FLY"
# only starts at 17.35 — the slap lands there); LOVE = /l/ 18.54 (vowel 18.59); FLYERS = /f/ 18.86; SEVEN = /s/ hiss
# 19.83 (voiced "SE" 20.15); FONTS = /f/ 20.62; KEVIN = /k/ 21.13; SEVEN. = /s/ hiss 21.67 (voiced 21.95, "VEN" peak 22.19).
MEASURED = {
    4: [('YOUR', 10.50), ('LAST', 10.63), ('POST', 10.97), ('WAS', 11.36), ('CHRISTMAS.', 11.55), ('TWENTY', 12.56),
        ('TWENTY-ONE.', 13.00)],
    5: [("I'VE", 13.95), ('BEEN', 14.16), ('BUSY!', 14.37)],
    6: [('AND', 15.09), ('WHEN', 15.24), ('YOU', 15.40), ('DO', 15.64), ('SHOW', 15.86), ('UP…', 16.10), ("IT'S", 16.89),
        ('A', 17.07), ('FLYER.', 17.13)],
    7: [('PEOPLE', 18.12), ('LOVE', 18.54), ('FLYERS!', 18.86)],
    8: [('SEVEN', 19.83), ('FONTS,', 20.62), ('KEVIN.', 21.13), ('SEVEN.', 21.67)],
}
def wt(seg, text, nth=0):
    return [t for w, t in MEASURED[seg] if w == text][nth]
WORD_FIX = {(seg, w): t for seg, lst in MEASURED.items() for w, t in lst}     # for the integrator (engine.WORD_FIX)

def _pages():
    """engine caption pages with the measured onsets applied; t1 and page in/out recomputed exactly as engine._pages
    does, and a page never spills onto the first frame of the next line's picture."""
    import copy
    pages = copy.deepcopy(E.PAGES); words = [w for p in pages for w in p['words']]
    for seg, lst in MEASURED.items():
        ws = [w for w in words if w['seg'] == seg]
        if len(ws) != len(lst) or any(w['text'] != x for w, (x, _) in zip(ws, lst)):
            raise ValueError(f'caption words of line {seg} changed: {[w["text"] for w in ws]}')
        for w, (_, t0) in zip(ws, lst): w['t0'] = t0
    for k, w in enumerate(words[:-1]):
        if words[k + 1]['seg'] == w['seg']: w['t1'] = max(w['t0'] + .06, words[k + 1]['t0'])
    for w in words: w['t1'] = max(w['t1'], w['t0'] + .06)
    for j, p in enumerate(pages):
        nxt = pages[j + 1]['words'][0]['t0'] if j + 1 < len(pages) else E.DUR; last = p['words'][-1]['t1']
        p['a'] = p['words'][0]['t0'] - .04; p['z'] = nxt - .02 if nxt - last < .5 else last + .35
    return [p for p in pages if p['seg'] in MEASURED]
PAGES = _pages()

def captions(ctx, t, segs, cuts=(), hide=(), at=None):
    """the engine's word-pop captions (same look, same maths) for lines `segs` on the measured onsets; replaces the
    engine captions for this frame. A page that would still be on screen at a picture cut in `cuts` ends ON the cut
    (no previous page over the new shot). `hide` = (t0, t1) spans with no captions (own kinetic type there).
    `at` = {(seg, WORD): t} pops a word deliberately later than its acoustic onset (e.g. on its stressed syllable)."""
    ctx.captions = False
    if any(a <= t < b for a, b in hide): return
    base, cy0 = ctx.cap_size, ctx.cap_y
    for p in PAGES:
        z = p['z']
        for c in cuts:
            if p['a'] < c < z and z - c < .5 and not any(w['t0'] - .02 >= c for w in p['words']): z = c
        if p['seg'] not in segs or not (p['a'] <= t < z): continue
        for w, sz, cx, cy in E._layout(p, base):
            w0 = (at or {}).get((w['seg'], w['text']), w['t0'])
            if t < w0 - .02: continue
            lt = t - w0 + .02; s_ = .72 + .28 * E.back(lt / .16, 1.4)
            if w0 - .02 <= t < max(w['t1'], w0 + .06) + .04: s_ *= 1.03
            img = E.cap_word(w['text'], sz, w['spk'] if w['emph'] else None)
            if lt < .05: img = E.fade(img, lt / .05)
            if z == p['z'] and z - t < .06: img = E.fade(img, max(0., (z - t) / .06))
            if abs(s_ - 1) > .01: img = img.resize((max(1, int(img.width * s_)), max(1, int(img.height * s_))), Image.BILINEAR)
            ctx.add('screen', img, int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2), center=False)

# ------------------------------------------------------------------------------------------------ clean matte
# B_review: engine.graded() leaves a cream rim band + green-contaminated edge (very visible on the crash-zoom CUs).
# Same cure as s01/s02 (copied from the A kit so the film matches): hard despill, edge colour decontamination,
# 1 px choke, rim only on the window side, softer light wrap. Drop-in for E.graded(spk, src_t, angle).
from scipy.ndimage import minimum_filter as _minf
_gx1 = np.linspace(-1, 1, W, dtype=np.float32)
def _clean_consts(angle):
    def mk():
        A = E.ANGLES[angle]; sharp, wrap, mean = E.plate(angle)
        lit = np.clip(.5 + .5 * A['side'] * _gx1, 0, 1)
        mul = (1 - A['amt'] * .6 + A['amt'] * 1.2 * lit)[:, None] * np.array(A['grade'], np.float32)[None, :]
        add = np.array(A['key'], np.float32)[None, :] * A['amt'] * .22 * lit[:, None]
        side = np.clip(A['rside'] * _gx1 * 1.6 - .1, 0, 1)
        return dict(mul=mul.astype(np.float32), add=add.astype(np.float32), rimL=(side * A['ramt'] * .45).astype(np.float32),
                    rim=Image.new('RGB', (W, H), A['rim']), wrap=wrap, mean=mean.astype(np.float32),
                    grade=np.array(A['grade'], np.float32))
    return E.cached(('B_clean_consts', angle), mk)
_LUT_CORE = [255 if v >= 251 else 0 for v in range(256)]
_LUT_W = [int(max(0, min(255, (v / 255 - .80) / .18 * 255))) for v in range(256)]
_LUT_CHOKE = [int(max(0, min(255, (v - 31) * 255 / 224))) for v in range(256)]
def clean_take(spk, src_t, angle=None):
    angle = angle or spk; f = E.take(spk).raw(src_t)
    hit = E._C.get(('B_clean_last', spk, angle))
    if hit is not None and hit[0] is f: return hit[1]
    C = _clean_consts(angle)
    a = np.asarray(f); r = a[..., 0].astype(np.int32); g = a[..., 1].astype(np.int32); b = a[..., 2].astype(np.int32)
    m = np.maximum(r, b); diff = g - m
    al8 = np.clip((100 - diff) * 255 // 70, 0, 255).astype(np.uint8)
    R, G, B = Image.fromarray(a[..., 0]), Image.fromarray(np.minimum(g, m).astype(np.uint8)), Image.fromarray(a[..., 2])
    AL = Image.fromarray(al8)
    small = Image.merge('RGBA', (R, G, B, AL.point(_LUT_CORE))).convert('RGBa').resize((W // 4, H // 4), Image.BOX)
    ext = small.filter(ImageFilter.GaussianBlur(2.5)).convert('RGBA').convert('RGB').resize((W, H), Image.BILINEAR)
    im = Image.composite(Image.merge('RGB', (R, G, B)), ext, AL.point(_LUT_W))
    x = np.asarray(im, np.float32); msk = al8 > 128
    cm = (x[msk].mean(0) if msk.any() else x.reshape(-1, 3).mean(0)) * C['grade']
    lm = (1 + .12 * (C['mean'] / (cm + 1e-3) - 1)).astype(np.float32)
    x = x * (C['mul'] * lm[None, :])[None] + C['add'][None]
    im = Image.fromarray(np.clip(x, 0, 255).astype(np.uint8))
    a8 = AL.point(_LUT_CHOKE).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2)); A8 = np.asarray(a8)
    band = (A8 - _minf(A8, size=9)).astype(np.float32) * C['rimL'][None, :]
    im = Image.composite(C['rim'], im, Image.fromarray(band.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)))
    edge = ((A8 - _minf(A8, size=5)).astype(np.uint16) * 56 // 255).astype(np.uint8)
    im = Image.composite(C['wrap'], im, Image.fromarray(edge))
    im.putalpha(a8)
    E._C[('B_clean_last', spk, angle)] = (f, im); return im

def show(ctx, spk, src, angle=None):
    """put take `spk` at source second `src` on screen in `angle` through clean_take (engine's own take switched off)."""
    angle = angle or spk
    ctx.shot.update(show=False, spk=spk, src=src, angle=angle)
    ctx.add('behind', clean_take(spk, src, angle), 0, 0, center=False)

# ------------------------------------------------------------------------------------------------ placement
def place(img, ox, oy, s, rot, cx, cy, size=(W, H), resample=Image.BICUBIC):
    """render `img` so that its point (ox, oy) lands on screen (cx, cy), scaled by s and rotated by `rot` degrees
    (positive = clockwise on screen)."""
    th = math.radians(rot); c, si = math.cos(th), math.sin(th)
    # forward: X = cx + s*(c*(x-ox) - si*(y-oy)), Y = cy + s*(si*(x-ox) + c*(y-oy))
    a, b, d, e = c / s, si / s, -si / s, c / s
    return img.transform(size, Image.AFFINE, (a, b, ox - a * cx - b * cy, d, e, oy - d * cx - e * cy), resample)

def to_screen(px, py, ox, oy, s, rot, cx, cy):
    th = math.radians(rot); c, si = math.cos(th), math.sin(th)
    return cx + s * (c * (px - ox) - si * (py - oy)), cy + s * (si * (px - ox) + c * (py - oy))

# ------------------------------------------------------------------------------------------------ the printed flyer
ART_W, ART_H = 896, 1120          # src/assets/flyer.png
MARGIN = 26                       # home-printer white border (art px)
PAD = 70                          # transparent padding around the sheet for the shadow (art px)
SHEET_W, SHEET_H = ART_W + 2 * MARGIN, ART_H + 2 * MARGIN
DOG = 74                          # dog-eared bottom-left corner (art px)

def _pblur(a, r):
    """gaussian blur of a float array in [0,1] or [-1,1] via PIL (fast)."""
    lo, hi = float(a.min()), float(a.max()); sc = 255 / max(hi - lo, 1e-6)
    im = Image.fromarray(((a - lo) * sc).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im, np.float32) / sc + lo

def paper_base(S=2):
    """the sheet's RGB (uint8, sheet px * S) and alpha (0..1 float) — no marker, no shadow."""
    def mk():
        pw, ph = SHEET_W * S, SHEET_H * S; m = MARGIN * S
        art = np.asarray(E.asset('flyer').resize((ART_W * S, ART_H * S), Image.LANCZOS), np.float32)
        g = art.mean(2, keepdims=True); art = g + (art - g) * .90                 # inkjet gamut: a little less saturated
        art = 14 + art * .90                                                      # ink never reaches pure white / black
        P = np.empty((ph, pw, 3), np.float32); P[:] = (244, 241, 233)
        P[m:m + ART_H * S, m:m + ART_W * S] = art
        rng = np.random.default_rng(11)
        fib = (_pblur(rng.normal(0, 1, (ph, pw)).clip(-3, 3).astype(np.float32), .8 * S) * 9.0)          # fibre
        mot = Image.fromarray(((rng.normal(0, 1, (ph // 24, pw // 24)) * 40) + 128).clip(0, 255).astype(np.uint8))
        mot = mot.filter(ImageFilter.GaussianBlur(.8)).resize((pw, ph), Image.BICUBIC)
        mot = (np.asarray(mot, np.float32) - 128) / 40 * .022                                 # mottling
        yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
        cx, cy = pw / 2 + 3 * S, ph / 2 - 5 * S                                           # folds (not perfectly centred)
        dx, dy = (xx - cx) / S, (yy - cy) / S
        shade = (1 + .028 * np.tanh(-dx / 60)) * (1 + .022 * np.tanh(-dy / 70))         # re-flattened quarter folds
        crease = (1 - .20 * np.exp(-(dx / 1.3) ** 2) - .18 * np.exp(-(dy / 1.3) ** 2))
        hl = .07 * np.exp(-((dx + 3.2) / 1.6) ** 2) + .06 * np.exp(-((dy + 3.2) / 1.6) ** 2)
        light = (.93 + .09 * xx / pw) * (1.015 - .035 * yy / ph)                          # warm window from the right
        k = shade * crease * light * (1 + mot)
        P = P * k[..., None] + 255 * hl[..., None] + fib[..., None]
        P *= np.array([1.0, .985, .95], np.float32)                                       # warm afternoon light
        edge = np.minimum.reduce([xx, yy, pw - 1 - xx, ph - 1 - yy]) / S
        P *= (1 - .10 * np.exp(-edge / 1.2))[..., None]
        # alpha: rectangle minus the dog-eared corner; the folded flap (paper back) + its shadow on the print
        d = DOG * S
        cut = Image.new('L', (pw, ph), 255); ImageDraw.Draw(cut).polygon([(0, ph - d), (d, ph), (0, ph)], fill=0)
        flap = Image.new('L', (pw, ph)); ImageDraw.Draw(flap).polygon([(0, ph - d), (d, ph), (d, ph - d)], fill=255)
        fl = np.asarray(flap.filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255
        fsh = np.asarray(flap.transform(flap.size, Image.AFFINE, (1, 0, -6 * S, 0, 1, 4 * S)).filter(ImageFilter.GaussianBlur(5 * S)), np.float32) / 255 * .45
        P *= (1 - fsh * (1 - fl))[..., None]
        back = (226 + 18 * xx / max(1, d)).clip(0, 250)
        P = P * (1 - fl[..., None]) + np.dstack([back, back * .985, back * .955]) * fl[..., None]
        A = np.maximum(np.asarray(cut.filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255, fl)
        return P.clip(0, 255).astype(np.uint8), A
    return E.cached(('B_paper_base', S), mk)

def paper_rgba(S=2):
    """the clean sheet as RGBA, padded by PAD*S (cached); shadows are cast by table_scene()."""
    def mk():
        if S != 2:
            big = paper_rgba(2); return big.resize((big.width * S // 2, big.height * S // 2), Image.LANCZOS)
        P, A = paper_base(S)
        ph, pw = A.shape; p = PAD * S; Hh, Ww = ph + 2 * p, pw + 2 * p
        sh = 0.0
        a = np.zeros((Hh, Ww), np.float32); a[p:p + ph, p:p + pw] = A
        rgb = np.zeros((Hh, Ww, 3), np.float32); rgb[p:p + ph, p:p + pw] = P
        fa = a + sh * (1 - a)
        col = np.where(a[..., None] > 0, rgb, np.array([235, 232, 224], np.float32))     # no dark fringe
        return Image.fromarray(np.dstack([col, fa * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
    return E.cached(('B_paper', S), mk)

INK = (194, 16, 30)
def sheet_origin(S=2):
    """paper-RGBA pixel of art point (0, 0)."""
    return (PAD + MARGIN) * S, (PAD + MARGIN) * S

# ------------------------------------------------------------------------------------------------ marker strokes
def _catmull(pts, n=14):
    pts = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = map(np.array, (pts[i - 1], pts[i], pts[i + 1], pts[i + 2]))
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(np.array(pts[-2])); return np.array(out, np.float32)

def circle_pts(cx, cy, rx, ry, rot, seed, n=120, ex=2.0):
    """hand-drawn loop: starts upper-left, runs counter-clockwise, overshoots past the start, wobbles. ex > 2 makes it a
    superellipse (a capsule that hugs a line of type instead of bulging into its neighbours)."""
    r = np.random.default_rng(seed)
    a0 = r.uniform(-2.5, -2.0); sweep = 2 * math.pi + r.uniform(.45, .7)
    ts = np.linspace(0, 1, n)
    ang = a0 - sweep * ts
    p1, p2 = r.uniform(0, 6.28, 2)
    wob = 1 + .03 * np.sin(2 * ang + p1) + .015 * np.sin(3 * ang + p2)
    spi = 1 + .06 * (ts - .5)
    ca, sa = np.cos(ang), np.sin(ang); e = 2.0 / ex
    x = rx * wob * spi * np.sign(ca) * np.abs(ca) ** e; y = ry * wob * spi * np.sign(sa) * np.abs(sa) ** e
    th = math.radians(rot); c, s = math.cos(th), math.sin(th)
    return np.stack([cx + c * x - s * y, cy + s * x + c * y], 1).astype(np.float32)

# handwritten digits as control points in a unit box (x right, y down); one stroke each (7 gets a second, the bar)
_DIG = {
    '1': [[(.25, .22), (.52, .02), (.50, .55), (.47, 1.0)]],
    '2': [[(.08, .28), (.30, .02), (.70, .02), (.86, .28), (.55, .62), (.08, .98), (.50, .95), (.95, .97)]],
    '3': [[(.10, .12), (.55, .0), (.85, .20), (.45, .46), (.88, .66), (.62, .98), (.10, .88)]],
    '4': [[(.70, .98), (.66, .02), (.05, .66), (.98, .64)]],
    '5': [[(.88, .02), (.26, .04), (.18, .46), (.62, .40), (.90, .66), (.62, .98), (.08, .88)]],
    '6': [[(.78, .04), (.38, .22), (.12, .62), (.30, .98), (.76, .92), (.80, .58), (.40, .50), (.14, .68)]],
    '7': [[(.04, .05), (.50, .02), (.96, .06), (.62, .45), (.38, 1.0)], [(.24, .52), (.80, .47)]],
}
def digit_strokes(ch, x, y, h, seed, slant=8):
    """list of polylines for digit `ch` with top-left (x, y), height h (art px)."""
    r = np.random.default_rng(seed); w = h * .62; sl = math.tan(math.radians(slant))
    out = []
    for stroke in _DIG[ch]:
        pts = []
        for (u, v) in stroke:
            u += r.normal(0, .025); v += r.normal(0, .02)
            pts.append((x + u * w + (1 - v) * h * sl, y + v * h))
        out.append(_catmull(pts))
    return out

def draw_poly(d, pts, width, frac=1.0, taper=True):
    """progressively draw polyline pts (N x 2) up to `frac` of its length with round joins and pressure taper."""
    if frac <= 0 or len(pts) < 2: return
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1)); L = np.concatenate([[0], np.cumsum(seg)]); tot = L[-1]
    end = frac * tot
    k = int(np.searchsorted(L, end, 'right'))
    q = [tuple(p) for p in pts[:k]]
    if k < len(pts) and k > 0:
        f = (end - L[k - 1]) / max(seg[k - 1], 1e-6); q.append(tuple(pts[k - 1] + (pts[k] - pts[k - 1]) * f))
    for i in range(len(q)):
        u = L[min(i, len(L) - 1)] / tot
        wv = width * ((.55 + .45 * min(1, u / .06)) * (.6 + .4 * min(1, (1 - u) / .08)) if taper else 1)
        x, y = q[i]; rr = wv / 2
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=255)
        if i: d.line([q[i - 1], q[i]], fill=255, width=int(round(wv)))

# The seven fonts (art px coords of flyer.png): loop (cx, cy, rx, ry, rot, superellipse exponent), digit (x, y, h).
# B_review: capsule loops that hug each block (the old ellipses crossed each other into a scribble), digits moved off
# the busy art (4 sat on the chef, 6 was invisible on the yellow "(555)"), the 7 left of the fine print, half on the
# white printer margin, where the crash zoom frames it next to its loop.
FONTS = [
    dict(c=(449, 121, 446, 98, -2.6, 2.7), d=(14, -16, 88)),       # 1 GRAND OPENING!!! (rainbow bubble)
    dict(c=(452, 300, 428, 74, -3.6, 2.7), d=(642, 334, 88)),      # 2 KEVIN'S BAKERY (rounded outline)
    dict(c=(182, 532, 180, 166, 0.0, 2.0), d=(368, 352, 90)),      # 3 50% OFF* (the starburst)
    dict(c=(352, 722, 346, 92, -12.0, 2.5), d=(0, 806, 78)),       # 4 BEST CROISSANTS IN TOWN!!! (script)
    dict(c=(382, 897, 270, 60, -3.0, 2.8), d=(6, 890, 78)),        # 5 CALL NOW
    dict(c=(459, 1002, 398, 66, -5.0, 2.8), d=(-4, 976, 80)),      # 6 (555) 012-3456
    dict(c=(757, 1076, 140, 34, -4.0, 2.4), d=(684, 782, 126)),    # 7 *some exclusions apply (the fine print)
]
STROKE = 16.0        # marker width (art px) — a bold felt-tip

def marks_image(S, states):
    """'L' marker coverage at sheet px * S. states: list of (circle_frac, digit_frac) per font (0..1)."""
    im = Image.new('L', (SHEET_W * S, SHEET_H * S)); d = ImageDraw.Draw(im); o = MARGIN
    for i, (cf, df) in enumerate(states):
        if cf <= 0 and df <= 0: continue
        F = FONTS[i]; cx, cy, rx, ry, rot = F['c'][:5]
        pts = (circle_pts(cx, cy, rx, ry, rot, 31 + i, ex=F['c'][5]) + o) * S
        draw_poly(d, pts, STROKE * S, cf)
        if df > 0:
            x, y, h = F['d']; strokes = digit_strokes(str(i + 1), x, y, h, 77 + i)
            lens = [np.sqrt(((s_[1:] - s_[:-1]) ** 2).sum(1)).sum() for s_ in strokes]; tot = sum(lens); acc = 0
            for s_, ln in zip(strokes, lens):
                f = (df * tot - acc) / ln; acc += ln
                draw_poly(d, (s_ + o) * S, (STROKE * (1.35 if i == 6 else 1.1)) * S, min(1, f))
    return im                                     # (blurred by marked_paper on its bounding box only)

INK_T = np.array([.80, .075, .12], np.float32)    # red marker transmittance (multiply: dark on magenta/green, red on white)
def marked_paper(S, states):
    """paper RGBA with the marker states, the ink MULTIPLIED into the print like real felt-tip ink (the last result is
    cached, so held frames are free)."""
    key = tuple((round(a, 3), round(b, 3)) for a, b in states)
    if all(a <= 0 and b <= 0 for a, b in key): return paper_rgba(S)
    hit = E._C.get(('B_marked_last', S))
    if hit is not None and hit[0] == key: return hit[1]
    base = paper_rgba(S); m = marks_image(S, states); o = PAD * S
    bb = m.getbbox()
    im = base.copy()
    if bb is not None:
        x0, y0, x1, y1 = max(0, bb[0] - 4 * S), max(0, bb[1] - 4 * S), min(m.width, bb[2] + 4 * S), min(m.height, bb[3] + 4 * S)
        bb = (x0, y0, x1, y1); m = m.crop(bb).filter(ImageFilter.GaussianBlur(.55 * S)); bb = (0, 0, x1 - x0, y1 - y0)
        reg = np.asarray(base.crop((o + x0, o + y0, o + x1, o + y1)), np.float32)
        cov = np.asarray(m.crop(bb), np.float32)[..., None] / 255 * .96
        mul = reg[..., :3] * INK_T                                    # felt-tip: mostly multiplied into the print,
        ink = mul * .45 + np.array(INK, np.float32) * .55               # partly opaque dye (stays RED on the green)
        reg[..., :3] = reg[..., :3] * (1 - cov) + ink * cov
        im.paste(Image.fromarray(reg.clip(0, 255).astype(np.uint8), 'RGBA'), (o + x0, o + y0))
    E._C[('B_marked_last', S)] = (key, im); return im

# ------------------------------------------------------------------------------------------------ IG post screen
# B_review: rebuilt at any scale S (S=2 for the punch-in, so the date/likes stay crisp at 1.7x), with the real
# "Posts" navigation bar (the scroll now slides UNDER a fixed bar instead of chopping the header under the status bar)
# and the red screen-recording pill behind the clock. Layout in 1x screen px:
FG, SUB, BG_ = (245, 245, 245), (168, 168, 168), (0, 0, 0)
IG = dict(nav=60, head=150, photo=240, act=1320, likes=1408, cap=1454, com=1500, date=1550, next=1700)
def _icon(name, size, col=FG):
    def mk():
        SS = 3
        im = Image.new('L', (size * SS, size * SS)); d = ImageDraw.Draw(im); s = SS * size / 56
        if name in ('heart', 'heart_fill'):
            pts = []
            for j in range(64):
                a = 2 * math.pi * j / 64; x = 16 * math.sin(a) ** 3; y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
                pts.append((28 * s + x * 1.45 * s, 29 * s + y * 1.45 * s))
            if name == 'heart_fill': d.polygon(pts, fill=255)
            else: d.line(pts + [pts[0]], fill=255, width=int(3.6 * s), joint='curve')
        elif name == 'comment':
            d.ellipse((7 * s, 6 * s, 49 * s, 48 * s), outline=255, width=int(3.6 * s)); d.polygon([(10 * s, 38 * s), (4 * s, 52 * s), (20 * s, 46 * s)], fill=255)
        elif name == 'share':
            d.line([(6 * s, 10 * s), (50 * s, 10 * s), (24 * s, 50 * s), (20 * s, 26 * s), (6 * s, 10 * s)], fill=255, width=int(3.6 * s), joint='curve')
            d.line([(20 * s, 26 * s), (50 * s, 10 * s)], fill=255, width=int(3.6 * s))
        elif name == 'save':
            d.line([(12 * s, 6 * s), (44 * s, 6 * s), (44 * s, 50 * s), (28 * s, 36 * s), (12 * s, 50 * s), (12 * s, 6 * s)], fill=255, width=int(3.6 * s), joint='curve')
        elif name == 'dots':
            for x in (12, 28, 44): d.ellipse(((x - 3.5) * s, 24.5 * s, (x + 3.5) * s, 31.5 * s), fill=255)
        elif name == 'back':
            d.line([(34 * s, 8 * s), (14 * s, 28 * s), (34 * s, 48 * s)], fill=255, width=int(4.2 * s), joint='curve')
        a = im.resize((size, size), Image.LANCZOS); out = Image.new('RGBA', (size, size), col + (0,)); out.putalpha(a); return out
    return E.cached(('B_icon', name, size, col), mk)

def _default_avatar(size, bg=(54, 54, 54), fg=(120, 120, 120)):
    """the grey 'no profile photo' silhouette — the account looks abandoned."""
    def mk():
        SS = 3; S_ = size * SS; im = Image.new('RGBA', (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((0, 0, S_ - 1, S_ - 1), fill=bg + (255,))
        layer = Image.new('L', (S_, S_)); dl = ImageDraw.Draw(layer)
        dl.ellipse((S_ * .33, S_ * .17, S_ * .67, S_ * .51), fill=255)
        dl.ellipse((S_ * .14, S_ * .58, S_ * .86, S_ * 1.18), fill=255)
        m = Image.new('L', (S_, S_)); ImageDraw.Draw(m).ellipse((0, 0, S_ - 1, S_ - 1), fill=255)
        from PIL import ImageChops
        layer = ImageChops.multiply(layer, m)
        im.alpha_composite(Image.merge('RGBA', [Image.new('L', (S_, S_), c) for c in fg] + [layer]))
        return im.resize((size, size), Image.LANCZOS)
    return E.cached(('B_defav', size), mk)

def _rich(d, im, x, y, parts, size):
    """parts: [(text, weight, colour) | ('emoji', ch)] on one line; returns end x."""
    for p in parts:
        if p[0] == 'emoji':
            e = emoji(p[1], int(size * 1.05)); im.alpha_composite(e, (int(x + 2), int(y + size * .05))); x += e.width + 6; continue
        txt, wt, col = p; f = inter(size, wt); d.text((x, y), txt, font=f, fill=col); x += f.getlength(txt)
    return x

def ig_bars(S=1):
    """the fixed top of the screen (status bar with the screen-recording pill + 'Posts' nav bar), RGB W*S x 150*S."""
    def mk():
        w = W * S; im = Image.new('RGBA', (w, IG['head'] * S), BG_ + (255,)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((44 * S, 20 * S, 152 * S, 58 * S), 19 * S, fill=(235, 52, 48))          # recording pill
        d.text((98 * S, 39 * S), '2:17', font=inter(32 * S, 'SemiBold'), fill=(255, 255, 255), anchor='mm')
        for k in range(4): d.rounded_rectangle(((W - 238 + k * 13) * S, (46 - 6 - k * 5) * S, (W - 229 + k * 13) * S, 48 * S), 2 * S, fill=FG)
        for r, w_ in ((26, 4), (17, 4)):
            d.arc(((W - 168 - r) * S, (50 - r) * S, (W - 168 + r) * S, (50 + r) * S), 225, 315, fill=FG, width=w_ * S)
        d.pieslice(((W - 177) * S, 41 * S, (W - 159) * S, 59 * S), 225, 315, fill=FG)
        d.rounded_rectangle(((W - 126) * S, 28 * S, (W - 66) * S, 54 * S), 8 * S, outline=(150, 150, 150), width=3 * S)
        d.rounded_rectangle(((W - 121) * S, 33 * S, (W - 104) * S, 49 * S), 4 * S, fill=(255, 214, 10))
        d.rounded_rectangle(((W - 63) * S, 36 * S, (W - 58) * S, 46 * S), 2 * S, fill=(150, 150, 150))
        im.alpha_composite(_icon('back', 50 * S), (22 * S, 80 * S))
        d.text((W // 2 * S, 86 * S), 'KEVINSBAKERY', font=inter(22 * S, 'SemiBold'), fill=SUB, anchor='mm')
        d.text((W // 2 * S, 118 * S), 'Posts', font=inter(34 * S, 'Bold'), fill=FG, anchor='mm')
        return im.convert('RGB')
    return E.cached(('B_igbars', S), mk)

def ig2021_content(S=1, extra=120):
    """the scrolling content under the bars (y from IG['head']): @kevinsbakery's last post + the older one (the flyer)
    peeking in below. RGB, W*S x (H - head + extra)*S."""
    def mk():
        HH = H - IG['head'] + extra; o = IG['head']
        im = Image.new('RGBA', (W * S, HH * S), BG_ + (255,)); d = ImageDraw.Draw(im)
        def P(v): return int(round(v * S))
        y = IG['head'] - o
        im.alpha_composite(_default_avatar(P(68)), (P(26), P(y + 10)))
        d.text((P(112), P(y + 13)), 'kevinsbakery', font=inter(P(30), 'SemiBold'), fill=FG)
        d.text((P(112), P(y + 49)), 'Kevin’s Bakery', font=inter(P(24), 'Regular'), fill=FG)
        im.alpha_composite(_icon('dots', P(44)), (P(W - 74), P(y + 22)))
        ph = E.asset('xmas2021'); crop = ph.crop((0, 60, 896, 956)).resize((P(W), P(W)), Image.LANCZOS)
        im.paste(crop, (0, P(IG['photo'] - o)))
        y = IG['act'] - o + 22
        im.alpha_composite(_icon('heart', P(58)), (P(28), P(y))); im.alpha_composite(_icon('comment', P(56)), (P(122), P(y + 1)))
        im.alpha_composite(_icon('share', P(56)), (P(214), P(y + 1))); im.alpha_composite(_icon('save', P(56)), (P(W - 86), P(y + 1)))
        _rich(d, im, P(32), P(IG['likes'] - o), [('3 likes', 'SemiBold', FG)], P(31))
        _rich(d, im, P(32), P(IG['cap'] - o), [('kevinsbakery', 'SemiBold', FG), (' Merry Xmas from Kevin’s Bakery!! ', 'Regular', FG), ('emoji', '\U0001F384')], P(31))
        _rich(d, im, P(32), P(IG['com'] - o), [('kevins_mom', 'SemiBold', FG), (' so proud of you sweetie ', 'Regular', FG), ('emoji', '❤️')], P(31))
        d.text((P(32), P(IG['date'] - o)), 'December 24, 2021', font=inter(P(27), 'Regular'), fill=SUB)
        y = IG['next'] - o                                                   # the next (older) post: the flyer
        d.line([(0, P(y - 2)), (P(W), P(y - 2))], fill=(30, 30, 30), width=max(1, S))
        im.alpha_composite(_default_avatar(P(68)), (P(26), P(y + 12)))
        d.text((P(112), P(y + 30)), 'kevinsbakery', font=inter(P(30), 'SemiBold'), fill=FG)
        im.alpha_composite(_icon('dots', P(44)), (P(W - 74), P(y + 24)))
        fl = E.asset('flyer'); fl = fl.resize((P(W), P(fl.height * W / fl.width)), Image.LANCZOS)
        top = P(y + 96); im.paste(fl.crop((0, 0, P(W), P(HH) - top)), (0, top))
        return im.convert('RGB')
    return E.cached(('B_igcontent', S, extra), mk)

def ig2021_screen(scroll=0.0, z=1.0, anchor=(16, 1565)):
    """RGB 1080x1920 frame of the post screen: content scrolled by `scroll` px (negative = still moving up into
    place) under the fixed bars, the whole screen punched in by z about `anchor` (screen px). z > 1 samples the 2x
    render, so the type stays crisp."""
    S = 2 if z > 1.001 else 1
    sy = int(round(-scroll * S)); key = ('B_igfull_last', S)
    hit = E._C.get(key)
    if hit is not None and hit[0] == sy: full = hit[1]
    else:
        cont = ig2021_content(S); bars = ig_bars(S)
        full = Image.new('RGB', (W * S, H * S)); o = IG['head'] * S
        full.paste(cont.crop((0, sy, W * S, sy + (H - IG['head']) * S)), (0, o)); full.paste(bars, (0, 0))
        E._C[key] = (sy, full)
    if S == 1: return full.copy()
    ax, ay = anchor; x0, y0 = ax - ax / z, ay - ay / z                  # visible window in 1x screen px
    box = (x0 * S, y0 * S, (x0 + W / z) * S, (y0 + H / z) * S)
    return full.resize((W, H), Image.BICUBIC, box=box, reducing_gap=None)

# ------------------------------------------------------------------------------------------------ the coffee table
# World space = flyer art px (the sheet at rest lies with its art origin at world (0, 0)). The table texture covers
# world x [TX0, TX0+TW], y [TY0, TY0+TH] at TR px per art px.
TX0, TY0, TW, TH, TR = -420, -700, 1740, 2800, 1.4      # B_review: wider (no black corners in the slap)
TABLE_ROT = 6.0              # boards run at a slight angle to the paper

def table_world():
    """walnut coffee-table top (RGB, top-down): flat-sawn boards with cathedral grain, seams, pores, satin sheen."""
    def mk():
        w, h = int(TW * TR), int(TH * TR)
        X = (np.arange(w, dtype=np.float32) / TR + TX0)[None, :]
        Y = (np.arange(h, dtype=np.float32) / TR + TY0)[:, None]
        def lowres(nx, ny, sig=1.0, seed=0):
            r = np.random.default_rng(seed); a = r.normal(0, 1, (ny, nx)).astype(np.float32)
            im = Image.fromarray(((a * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
            return (np.asarray(im.resize((w, h), Image.BICUBIC), np.float32) - 128) / 40
        seams = [-230, 300, 860]                                                          # board joints (world x)
        edges = [TX0 - 10] + seams + [TX0 + TW + 10]
        warp = lowres(8, 14, 1.2, 1) * 16 + lowres(30, 12, 1.0, 2) * 3
        r = np.zeros((h, w), np.float32); tone = np.ones((h, w), np.float32)
        rng = np.random.default_rng(3)
        for k in range(len(edges) - 1):
            m = (X >= edges[k]) & (X < edges[k + 1]); m = np.broadcast_to(m, (h, w))
            lo, hi = edges[k] + 60, edges[k + 1] - 60; xc = rng.uniform(min(lo, hi), max(lo, hi) + 1); yc = rng.uniform(-900, 2400)
            sl = rng.uniform(.045, .075); ph = rng.uniform(0, 30)
            rr = np.sqrt((X - xc) ** 2 + (sl * (Y - yc)) ** 2 + 30.0 ** 2) + ph            # cathedral arches
            r = np.where(m, rr, r); tone = np.where(m, 1 + rng.uniform(-.08, .08), tone)
        u = (r + warp) / 13.0
        frac = u - np.floor(u)
        late = np.clip(1 - np.abs(frac - .82) / .16, 0, 1) ** 1.5                         # dark late-wood bands
        streak = lowres(w // 3, max(2, h // 90), .6, 4)
        pores = np.clip(lowres(w // 2, h // 6, .3, 5) - 1.5, 0, 1)
        f = (.58 - .26 * late + .07 * streak - .18 * pores) * tone + .05 * lowres(5, 8, 1, 6)
        f = np.clip(f, 0, 1)
        dark = np.array([52, 30, 18], np.float32); light = np.array([156, 104, 64], np.float32)
        img = dark + (light - dark) * f[..., None]
        for sx in seams:                                                                  # joint: dark gap + bevel light
            img *= (1 - .6 * np.exp(-((X - sx) / 1.2) ** 2) + .10 * np.exp(-((X - sx - 2.8) / 1.5) ** 2))[..., None]
        sheen = np.exp(-((X - 1000) / 300) ** 2) * (.3 + .7 * np.clip((1000 - Y) / 1700, 0, 1))
        img = img + 46 * sheen[..., None] * np.array([1.0, .93, .82], np.float32)
        return Image.fromarray(img.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6))
    return E.cached('B_table', mk)

LR = .25                     # light map px per art px
def light_world():
    """warm window light on the table: a big soft sun wedge from the upper right with fiddle-leaf shadows and a
    mullion line, cooler and darker outside it (RGB multiplier image, 128 = x1.0)."""
    def mk():
        w, h = int(TW * LR), int(TH * LR); rng = np.random.default_rng(21)
        def W2P(x, y): return ((x - TX0) * LR, (y - TY0) * LR)
        patch = Image.new('L', (w, h)); d = ImageDraw.Draw(patch)
        d.polygon([W2P(*p) for p in ((-260, -900), (1700, -900), (1700, 2300), (700, 2300))], fill=255)
        bars = Image.new('L', (w, h), 255); db = ImageDraw.Draw(bars)
        db.line([W2P(820, -900), W2P(1500, 2300)], fill=0, width=int(30 * LR))
        leaves = Image.new('L', (w, h), 255); dl = ImageDraw.Draw(leaves)
        for k in range(15):
            cx, cy = rng.uniform(-120, 560), rng.uniform(-420, 380); a = rng.uniform(-.6, 2.2)
            L_, Wd = rng.uniform(190, 300), rng.uniform(100, 150)
            pts = []
            for j in range(32):
                tt = 2 * math.pi * j / 32; ex, ey = L_ / 2 * math.cos(tt), Wd / 2 * math.sin(tt) * (1 + .3 * math.cos(tt))
                pts.append(W2P(cx + ex * math.cos(a) - ey * math.sin(a), cy + ex * math.sin(a) + ey * math.cos(a)))
            dl.polygon(pts, fill=0)
            dl.line([W2P(cx - L_ / 2 * math.cos(a), cy - L_ / 2 * math.sin(a)), W2P(cx - (L_ / 2 + 120) * math.cos(a), cy - (L_ / 2 + 120) * math.sin(a))], fill=0, width=max(1, int(10 * LR)))
        patch = np.asarray(patch.filter(ImageFilter.GaussianBlur(60 * LR)), np.float32) / 255
        sh = np.minimum(np.asarray(bars.filter(ImageFilter.GaussianBlur(22 * LR)), np.float32),
                        np.asarray(leaves.filter(ImageFilter.GaussianBlur(15 * LR)), np.float32)) / 255
        lit = patch * (.50 + .50 * sh)
        warm = np.array([1.17, 1.05, .88], np.float32); cool = np.array([.62, .61, .68], np.float32)
        m = cool + (warm - cool) * lit[..., None]
        return Image.fromarray((m * 128).clip(0, 255).astype(np.uint8))
    return E.cached('B_light', mk)

def cam_place(img, px_per_art, wx0, wy0, F, s, rot, C, extra_rot=0.0, resample=Image.BILINEAR):
    """place a world-space image (pixel (0,0) = world (wx0, wy0), px_per_art px per art px) through the camera:
    world F -> screen C, scale s (screen px per art px), rotation rot (deg)."""
    ox, oy = (F[0] - wx0) * px_per_art, (F[1] - wy0) * px_per_art
    return place(img, ox, oy, s / px_per_art, rot + extra_rot, C[0], C[1], resample=resample)

def art_to_world(ax, ay, pose):
    wx, wy, prot, psc = pose; th = math.radians(prot); c, si = math.cos(th), math.sin(th)
    dx, dy = (ax - ART_W / 2) * psc, (ay - ART_H / 2) * psc
    return wx + c * dx - si * dy, wy + si * dx + c * dy

def table_scene(F, s, rot, C, paper=None, poses=(), h=0.0, light_shift=(0, 0)):
    """composite: table -> paper shadow -> paper -> window light. poses = [(wx, wy, prot, pscale), ...] = world
    position of the sheet's art centre, its extra rotation and scale; several poses are averaged (motion blur).
    h (0..1) = height of the sheet above the table (drives the shadow's offset, softness and density).
    Returns RGB 1080x1920."""
    fr = cam_place(table_world(), TR, TX0, TY0, F, s, rot, C, TABLE_ROT)
    if paper is not None and poses:
        S = 2 if paper.width > 1500 else 1
        th = math.radians(rot); c, si = math.cos(th), math.sin(th)
        acx, acy = (PAD + MARGIN + ART_W / 2) * S, (PAD + MARGIN + ART_H / 2) * S
        acc = None
        for (wx, wy, prot, psc) in poses:
            dx, dy = wx - F[0], wy - F[1]
            cx, cy = C[0] + s * (c * dx - si * dy), C[1] + s * (si * dx + c * dy)
            pl = place(paper, acx, acy, s * psc / S, rot + prot, cx, cy, resample=Image.BICUBIC if len(poses) == 1 else Image.BILINEAR)
            if len(poses) == 1: break
            ar = np.asarray(pl, np.float32); ar[..., :3] *= ar[..., 3:4] / 255
            acc = ar if acc is None else acc + ar
        if acc is not None:
            acc /= len(poses); al = acc[..., 3:4]
            acc[..., :3] /= np.maximum(al / 255, 1e-3)
            pl = Image.fromarray(acc.clip(0, 255).astype(np.uint8), 'RGBA')
        if h > .05:                                                   # close to the lens: out of focus
            pl = pl.filter(ImageFilter.GaussianBlur(14 * h))
        a = pl.getchannel('A')
        sm = a.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur((3 + 46 * h) / 4))
        offx, offy = -(5 + 80 * h), 9 + 120 * h
        sh = Image.new('L', (W // 4, H // 4)); sh.paste(sm, (int(round(offx / 4)), int(round(offy / 4))))
        op = .64 * (1 - .5 * h)
        sh = np.asarray(sh.resize((W, H), Image.BILINEAR), np.float32) / 255 * op
        fr = Image.fromarray((np.asarray(fr, np.float32) * (1 - sh[..., None])).astype(np.uint8))
        fr = fr.convert('RGBA'); fr.alpha_composite(pl); fr = fr.convert('RGB')
    Lm = cam_place(light_world(), LR, TX0, TY0, (F[0] - light_shift[0], F[1] - light_shift[1]), s, rot, C)
    out = np.asarray(fr, np.uint16) * np.asarray(Lm, np.uint16) // 128
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def zoom_blur(fr, amount, center=(540, 760), n=7):
    """smooth radial (crash-zoom) blur of a frame — applied through ctx.wrap so the captions stay crisp.
    amount = scale spread (e.g. .06 = the sharpest copy to +6 %)."""
    if amount <= .002: return fr
    rgb = fr.convert('RGB'); acc = np.zeros((H, W, 3), np.float32)
    for i in range(n):
        acc += np.asarray(E.zoom(rgb, 1 + amount * i / (n - 1), center), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8)).convert('RGBA')
