"""Private helpers for s01_open + s02_support (author A): measured word onsets -> own caption pages (engine look,
engine maths), mockumentary lower-third name chips, the prestige title card, and small camera/cut utilities.
Everything here is a pure function of t (no per-frame state)."""
import copy, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

W, H, FPS = E.W, E.H, E.FPS
CREAM = (250, 246, 238)
LAV = (164, 142, 255)

# ------------------------------------------------------------------ measured word onsets (voice16k.raw, 10 ms RMS
# envelope + 2.5 ms-hop spectrogram; edit-timeline seconds). Listed per line IN ORDER, one entry per caption word, so
# repeated words (line 2 has YOU twice) are unambiguous.
MEASURED = {
    0: [('SO…', .42), ('WHAT', 1.13), ('BRINGS', 1.43), ('YOU', 1.75), ('TWO', 1.92), ('HERE', 2.14), ('TODAY?', 2.43)],
    1: [('MY', 3.05), ('INSTAGRAM', 3.37), ("DOESN'T", 3.75), ('SUPPORT', 4.04), ('ME', 4.40), ('ANYMORE.', 4.52)],
    2: [('SUPPORT', 5.63), ('YOU?', 6.27), ('YOU', 7.07), ('ONLY', 7.32), ('TALK', 7.58), ('TO', 7.84), ('ME', 7.90),
        ('WHEN', 8.12), ('YOU', 8.28), ('NEED', 8.44), ('SOMETHING.', 8.72)],
    3: [("THAT'S", 9.37), ('NOT', 9.59), ('TRUE!', 9.80)],
}
# review notes (A_review): DOESN'T = the /d/ release after the dip at 3.745 (was 3.80); ME = the voiced /m/-/i/ after
# the long /t/ aspiration of "support" 4.30-4.40 (was 4.31, 3 frames early); ONLY = F1 jump of the /o/ at 7.32 (polish_sync: 7.16-7.32 is still
# the /ju/ glide of "you", F2 ~2700 -> 1000 Hz; was 7.16, 5 frames early); NEED = /n/ after the /u/ of "you"
# (centroid track; vowel at 8.50); WHEN = the /w/ glide (centroid falls from 8.11). YOU? 6.27 verified: 5.92-6.07 is
# the aspirated /p/, 6.09-6.24 "-or-", the /t/ flap 6.25-6.28, then "you?" with the rising question pitch 180->207 Hz.
def wt(seg, text, nth=0):
    hits = [t for w, t in MEASURED[seg] if w == text]
    return hits[nth]

def _pages():
    """engine caption pages with the measured onsets applied (by occurrence), t1 / page in-out recomputed exactly as
    engine._pages does. Only pages of the lines in MEASURED are returned."""
    pages = copy.deepcopy(E.PAGES)
    words = [w for p in pages for w in p['words']]
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
        # a line's words never spill onto the next speaker's picture: clear by the first frame of the next line
        if p['seg'] + 1 < len(E.TL):
            p['z'] = min(p['z'], math.ceil(E.TL[p['seg'] + 1]['t0'] * FPS - 1e-6) / FPS)
    return [p for p in pages if p['seg'] in MEASURED]
PAGES = _pages()

def captions(ctx, t, segs, cuts=()):
    """the engine's word-pop captions for lines `segs`, on the measured onsets (replaces ctx.captions for the frame).
    `cuts` = picture cut times: a page whose end falls within 0.12 s after a cut ends ON the cut (clean swap, no
    half-faded words of the previous page over the new shot). Call LAST in draw() so the words sit above other layers."""
    ctx.captions = False
    base, cy0 = ctx.cap_size, ctx.cap_y
    for p in PAGES:
        z = p['z']
        for c in cuts:
            if p['a'] < c < z and z - c < .12: z = c
        if p['seg'] not in segs or not (p['a'] <= t < z): continue
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img = E.cap_word(w['text'], sz, w['spk'] if w['emph'] else None)
            if lt < .05: img = E.fade(img, lt / .05)
            if z == p['z'] and z - t < .06: img = E.fade(img, max(0., (z - t) / .06))
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2), center=False)

# ------------------------------------------------------------------ cuts / camera
def fr(t): return int(round(t * FPS))
def at_frame(t, k): return fr(t) >= k                       # frame-exact cut test
def lerp(a, b, k): return a + (b - a) * k
def face_cam(face, z, to=(540, 640)):
    """camera that scales by z around world point `face` and puts it at screen point `to` (engine clamps edges)."""
    fx, fy = face
    return dict(z=z, x=fx, y=fy, dx=(to[0] - fx) * min(1., (z - 1) / .5), dy=(to[1] - fy) * min(1., (z - 1) / .5), rot=0.)
FACE = {'T': (528, 455), 'K': (556, 430), 'I': (470, 380)}   # face centres of each take in its own angle (z=1)

def zoom_blur(amount, anchor=(540, 640), n=9):
    """ctx.wrap: radial motion blur of the WORLD only (before chips/captions, which stay crisp), centred on `anchor`."""
    def wrap(frame):
        rgb = frame.convert('RGB'); acc = np.asarray(rgb, np.float32).copy()
        for i in range(1, n):
            acc += np.asarray(E.zoom(rgb, 1 + amount * .18 * i / (n - 1), anchor), np.float32)
        return Image.fromarray((acc / n).astype(np.uint8)).convert('RGBA')
    return wrap

# ------------------------------------------------------------------ clean matte (A_review)
# engine.graded() leaves a cream "sticker" outline (15 px all-round rim band + 9 px light-wrap from a bright plate) and
# an olive/grey fringe (edge pixels keep their green-contaminated colour). Very visible on the CUs (crash zoom z 1.6,
# Kevin's reaction CU). Same key, same grade + light match, but: hard despill, edge colour decontamination (soft-edge
# pixels take the colour of the nearby solid interior), 1 px choke, rim only on the window side and narrow, softer
# light wrap. PIL/uint8 pipeline, about the cost of engine.graded().
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
    return E.cached(('A_clean_consts', angle), mk)
_LUT_CORE = [255 if v >= 251 else 0 for v in range(256)]
_LUT_W = [int(max(0, min(255, (v / 255 - .80) / .18 * 255))) for v in range(256)]
_LUT_CHOKE = [int(max(0, min(255, (v - 31) * 255 / 224))) for v in range(256)]
def clean_take(spk, src_t, angle=None):
    """keyed + graded take frame (RGBA 1080x1920) with a clean edge; drop-in for E.graded(spk, src_t, angle)."""
    angle = angle or spk; f = E.take(spk).raw(src_t)
    hit = E._C.get(('A_clean_last', spk, angle))
    if hit is not None and hit[0] is f: return hit[1]
    C = _clean_consts(angle)
    a = np.asarray(f); r = a[..., 0].astype(np.int32); g = a[..., 1].astype(np.int32); b = a[..., 2].astype(np.int32)
    m = np.maximum(r, b); diff = g - m
    al8 = np.clip((100 - diff) * 255 // 70, 0, 255).astype(np.uint8)              # = engine.key alpha
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
    E._C[('A_clean_last', spk, angle)] = (f, im); return im

def show(ctx, spk, src, angle=None):
    """put take `spk` at source second `src` on screen in `angle` through clean_take (engine's own take switched off)."""
    angle = angle or spk
    ctx.shot.update(show=False, spk=spk, src=src, angle=angle)
    ctx.add('behind', clean_take(spk, src, angle), 0, 0, center=False)

# ------------------------------------------------------------------ typography
def spaced(text, size, wght, track_em=0.0, col=CREAM):
    """RGBA line of letter-spaced text, tight bbox + pad 4."""
    f = E.font(size, wght); tr = track_em * size
    adv = [f.getlength(c) for c in text]
    wtot = int(sum(adv) + tr * (len(text) - 1)) + 8
    l, tp, r, b = f.getbbox(text)
    im = Image.new('L', (wtot, b + 8)); d = ImageDraw.Draw(im); x = 4.
    for c, a in zip(text, adv):
        d.text((x, 4), c, font=f, fill=255); x += a + tr
    im = im.crop((0, max(0, tp), wtot, b + 8))
    out = Image.new('RGBA', im.size, col + (0,)); out.putalpha(im); return out

def soft_shadow(img, blur=14, op=.55, grow=6, only=False):
    """img over a soft dark halo (legibility on bright clothes / windows), same centre (only=True: the halo alone)."""
    pad = blur * 2 + grow
    a = Image.new('L', (img.width + 2 * pad, img.height + 2 * pad)); a.paste(img.getchannel('A'), (pad, pad))
    a = a.filter(ImageFilter.MaxFilter(grow * 2 + 1 if grow else 1)).filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op))
    out = Image.new('RGBA', a.size, (8, 6, 10, 0)); out.putalpha(a)
    if not only: out.alpha_composite(img, (pad, pad))
    return out

# ------------------------------------------------------------------ lower-third name chip (mockumentary)
def _chip_parts(name, desc):
    def mk():
        nm = spaced(name, 56, 640, .10)
        ds = spaced(desc, 40, 440, .02, col=(238, 232, 222)) if desc else None
        gap = 14
        tw = max(nm.width, ds.width if ds else 0); th = nm.height + (gap + ds.height if ds else 0)
        bar_h = th + 10
        bar = E.gradient(6, bar_h, [(120, 140, 255), (150, 120, 255), (190, 130, 255)]).convert('RGBA')
        bar = E.rounded(bar, 3)
        halo = Image.new('RGBA', (tw + 40, th + 10), (0, 0, 0, 0))
        halo.alpha_composite(nm, (20, 0))
        if ds: halo.alpha_composite(ds, (20, nm.height + gap))
        halo = soft_shadow(halo, blur=24, op=.58, grow=12, only=True)
        return dict(nm=nm, ds=ds, bar=bar, gap=gap, tw=tw, th=th, halo=halo)
    return E.cached(('A_chip', name, desc), mk)

def chip(ctx, t, t_in, t_out, name, desc='', x=84, y=1196, layer='screen', speed=1.0):
    """animated lower third: lavender bar grows, name wipes on, descriptor follows; slides/fades out at t_out.
    (x, y) = top-left of the bar. Cut-safe: returns silently outside [t_in, t_out + .2]."""
    if t < t_in or t > t_out + .2: return
    P = _chip_parts(name, desc); k = (t - t_in) * speed
    a_out = 1 - E.clamp((t - t_out) / .18); dx_out = -14 * E.ein(E.clamp((t - t_out) / .18))
    if a_out <= .01: return
    kb = E.eout(E.clamp(k / .22)); kn = E.eout(E.clamp((k - .04) / .30)); kd = E.eout(E.clamp((k - .12) / .30))
    canvas = Image.new('RGBA', (P['tw'] + 60, P['th'] + 40), (0, 0, 0, 0))
    # halo behind the text, revealed with the name
    halo = P['halo']; hp = (halo.width - (P['tw'] + 40)) // 2
    ha = E.fade(halo, .9 * max(kn, kd) * 1.0)
    big = Image.new('RGBA', (canvas.width + 2 * hp, canvas.height + 2 * hp), (0, 0, 0, 0))
    big.alpha_composite(ha, (0, 0))
    bh = max(1, int(P['bar'].height * kb))
    bar = P['bar'].crop((0, 0, 6, bh))
    big.alpha_composite(bar, (hp, hp + 2 + (P['bar'].height - bh) // 2))
    for im, kk, yy in ((P['nm'], kn, 0), (P['ds'], kd, P['nm'].height + P['gap'])):
        if im is None or kk <= .01: continue
        ww = max(1, int(im.width * kk)); piece = im.crop((0, 0, ww, im.height))
        piece = E.fade(piece, min(1., kk * 1.6))
        big.alpha_composite(piece, (hp + 24 + int(-18 * (1 - kk)), hp + 5 + yy))
    if a_out < 1: big = E.fade(big, a_out)
    ctx.add(layer, big, x - hp + dx_out, y - hp, center=False)

# ------------------------------------------------------------------ hook title card (over Instagram's side-eye)
TITLE_BIG = 104          # 'HIS INSTAGRAM' ~870 px wide (inside the 80-1000 safe area)
IG_GRAD = [(214, 150, 255), (255, 118, 186), (255, 178, 104)]   # engine SPK_GRAD['I'], lifted for the dark hoodie
def _hook_art():
    """static art of the hook title: small kicker 'COUPLES THERAPY · SESSION 1' (lavender ticks), then the premise in
    big type 'KEVIN & / HIS INSTAGRAM' ('&' in LUMARC lavender). Returns (rgba, y of the big lines' top, kicker rule y,
    kicker half width)."""
    def mk():
        kick = spaced('COUPLES THERAPY  ·  SESSION 1', 34, 560, .24, col=(236, 228, 255))
        l1a = spaced('KEVIN', TITLE_BIG, 700, .05); amp = spaced('&', TITLE_BIG, 500, 0., col=LAV)
        l2 = spaced('HIS INSTAGRAM', TITLE_BIG, 700, .05)
        # 'INSTAGRAM' in his own hoodie gradient (violet -> pink -> orange): the word points at the man on screen
        f = E.font(TITLE_BIG, 700); xs = int(4 + sum(f.getlength(c) for c in 'HIS ') + .05 * TITLE_BIG * 4) - 3
        g = E.gradient(l2.width - xs, l2.height, IG_GRAD).convert('RGBA'); g.putalpha(l2.getchannel('A').crop((xs, 0, l2.width, l2.height)))
        l2.paste(g, (xs, 0))
        gap_amp = int(TITLE_BIG * .26)
        w1 = l1a.width + gap_amp + amp.width
        wmax = max(kick.width + 2 * 70, w1, l2.width)
        lead = int(TITLE_BIG * .16)
        h = kick.height + 40 + l1a.height + lead + l2.height
        im = Image.new('RGBA', (wmax + 40, h + 40), (0, 0, 0, 0)); cx = im.width // 2; y = 20
        im.alpha_composite(kick, (cx - kick.width // 2, y)); ry = y + kick.height // 2
        y += kick.height + 40; ytop = y
        x = cx - w1 // 2; im.alpha_composite(l1a, (x, y))
        im.alpha_composite(amp, (x + l1a.width + gap_amp, y + (l1a.height - amp.height)))
        y += l1a.height + lead
        im.alpha_composite(l2, (cx - l2.width // 2, y))
        return im, ytop, ry, kick.width // 2
    return E.cached(('A_hook_art', TITLE_BIG), mk)

def hook_title(t, t_end):
    """the hook title, crisp from frame 0. Life: lavender ticks draw outward beside the kicker, a slow 2.5 % scale
    drift and a faint warm light sweep across the letters (window light catching the type)."""
    art, ytop, ry, kw = _hook_art(); k = E.clamp(t / max(.5, t_end))
    def ticks(im, rl):
        d = ImageDraw.Draw(im); cx = im.width // 2
        if rl > 1:
            d.line((cx - kw - 18 - rl, ry, cx - kw - 18, ry), fill=LAV + (235,), width=3)
            d.line((cx + kw + 18, ry, cx + kw + 18 + rl, ry), fill=LAV + (235,), width=3)
        return im
    halo = E.cached(('A_hook_halo', TITLE_BIG), lambda: soft_shadow(ticks(art.copy(), 46), blur=26, op=.62, grow=6, only=True))
    im = ticks(art.copy(), int(46 * E.eout(E.clamp(.35 + t / .5))))
    A = np.asarray(im.getchannel('A'), np.float32) / 255
    yy, xx = np.mgrid[0:im.height, 0:im.width].astype(np.float32)
    pos = -300 + (im.width + 600) * k
    band = np.exp(-(((xx + .45 * (yy - ytop)) - pos) / 90) ** 2) * .45
    rgb = np.asarray(im.convert('RGB'), np.float32)
    rgb = rgb + (np.array((255, 236, 205), np.float32) - rgb) * (band * (A > 0))[..., None]
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((A * 255).astype(np.uint8)))
    out = halo.copy(); pad = (halo.width - im.width) // 2; out.alpha_composite(im, (pad, pad))
    s = 1.0 + .025 * k
    if s > 1.001: out = out.resize((int(out.width * s), int(out.height * s)), Image.BICUBIC)
    return out

def dim_wrap(top=.86, mid=.46, y0=560, y1=900, bot=.52):
    """ctx.wrap: darken the WORLD (not chips/captions/title) with a vertical ramp: face zone ~top, title zone ~mid."""
    def mk():
        ys = np.arange(H, dtype=np.float32)
        g = np.where(ys < y0, top, np.where(ys < y1, top + (mid - top) * np.clip((ys - y0) / (y1 - y0), 0, 1) ** .8,
                     mid + (bot - mid) * np.clip((ys - 1500) / 420, 0, 1)))
        col = np.repeat((g * 255).astype(np.uint8)[:, None], W, 1)
        return Image.merge('RGB', [Image.fromarray(col)] * 3)
    m = E.cached(('A_dim_ramp', top, mid, y0, y1, bot), mk)
    from PIL import ImageChops
    return lambda fr: ImageChops.multiply(fr.convert('RGB'), m).convert('RGBA')
