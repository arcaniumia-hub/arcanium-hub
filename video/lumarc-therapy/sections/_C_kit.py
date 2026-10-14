"""_C_kit — private helpers for s05_feel + s06_needs (author C). Everything is a pure function of its arguments
(static art cached by key), so the sections stay pure functions of t.

* MEASURED / captions()  word onsets measured on src/voice16k.raw (10 ms RMS envelope + 2.5 ms-hop spectrogram) applied
                         to the engine's word-pop captions; pages can be skipped (they are handwritten on the notepad)
                         or cut short at a picture cut.
* cam helpers            face_cam(), cam_map() / cam_img() (world -> screen exactly like engine.compose_world).
* insights_frame(t)      the "screen recording" insert: dark-mode Instagram Insights, Accounts reached — the daily line
                         falls off a cliff and the big number counts down to 3 on "cried".
* notepad(t)             the therapist's yellow legal pad (real paper: rules, red margin, gum binding, fibre, light
                         falloff, contact shadow) with Instagram's needs handwritten in blue ballpoint as she says them.
* lamp_plate / lamp_take / lamp_bloom   the "Good lighting." gag: the brass floor lamp behind Instagram clicks on —
                         bulb bloom, warm pool on the bookcase, a warm key on his face, a soft beauty glow. The light is
                         applied in world space (lit plate cached per level, light on the keyed take inside its matte
                         box) + a post-camera bloom; lamp_wrap(L, cam) is the equivalent (slower) screen-space version.
"""
import copy, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import engine as E

W, H, FPS = E.W, E.H, E.FPS
HERE = os.path.dirname(os.path.abspath(__file__))
def fr(t): return int(round(t * FPS))
def F(j): return j / FPS
def smooth(x):
    x = E.clamp(x); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ measured word onsets (edit-timeline seconds)
# one entry per caption word, in order (the integrator can merge these into engine.WORD_FIX)
# (review pass: re-measured with 10 ms band energies — MUCH was keyed on its "ch" (36.03 -> nasal 35.86), HIM? on
#  the "o" of "from" (30.80 -> 30.89), YOU/NEED a little early; lip smacks / breaths before CONSISTENCY, REELS skipped)
# (polish pass: line 9 re-segmented on 5 ms band energies — "how" = breathy /h/ 23.85 + modal /aU/ 23.99-24.08;
#  DID /d/ closure 24.09 (release 24.125); THAT /dh/ 24.21, /ae/ 24.235-24.32; MAKE /m/ murmur 24.35 after the /t/ gap;
#  YOU /k/ release 24.545, /u/ 24.595; FEEL? /f/ frication 24.655-24.785 — the old values were one word early)
MEASURED = {
    9: [('KEVIN…', 23.00), ('HOW', 23.84), ('DID', 24.09), ('THAT', 24.20), ('MAKE', 24.35), ('YOU', 24.56), ('FEEL?', 24.66)],
    10: [('…CREATIVE?', 25.68)],
    11: [('MY', 26.89), ('ALGORITHM', 27.07), ('CRIED.', 27.67)],
    12: [('INSTAGRAM,', 28.74), ('WHAT', 29.83), ('DO', 30.02), ('YOU', 30.15), ('NEED', 30.36), ('FROM', 30.67), ('HIM?', 30.89)],
    13: [('CONSISTENCY.', 31.44), ('GOOD', 32.89), ('LIGHTING.', 33.07), ('REELS.', 34.19), ('IS', 35.45), ('THAT', 35.56),
         ('TOO', 35.74), ('MUCH', 35.86), ('TO', 36.15), ('ASK?', 36.25)],
}
def wt(seg, text, nth=0):
    return [t for w, t in MEASURED[seg] if w == text][nth]

def _pages():
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
        if p['seg'] + 1 < len(E.TL):        # never spill onto the next line's picture
            p['z'] = min(p['z'], math.ceil(E.TL[p['seg'] + 1]['t0'] * FPS - 1e-6) / FPS)
    return [p for p in pages if p['seg'] in MEASURED]
PAGES = _pages()

def captions(ctx, t, segs, skip=(), zmax=None, cap_y=None, base=None):
    """engine word-pop captions of lines `segs` on the measured onsets (replaces ctx.captions for this frame).
    skip: {(seg, first word)} pages not drawn; zmax: {(seg, first word): t} cut a page short (at a picture cut)."""
    ctx.captions = False
    base = base or ctx.cap_size; cy0 = cap_y if cap_y is not None else ctx.cap_y; zmax = zmax or {}
    for p in PAGES:
        key = (p['seg'], p['words'][0]['text'])
        if p['seg'] not in segs or key in skip: continue
        z = min(p['z'], zmax.get(key, 1e9))
        if not (p['a'] <= t < z): continue
        for w, sz, cx, cy in E._layout(p, base):
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img = E.cap_word(w['text'], sz, w['spk'] if w['emph'] else None)
            if lt < .05: img = E.fade(img, lt / .05)
            if z - t < .06: img = E.fade(img, max(0., (z - t) / .06))
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, int(W / 2 + cx - img.width / 2), int(cy0 + cy - img.height / 2), center=False)

# ------------------------------------------------------------------ camera
FACE = {'T': (528, 455), 'K': (556, 430), 'I': (470, 380)}      # face centres of each take in its own angle (z=1)
def face_cam(face, z, to=(540, 640)):
    """camera that scales by z around world point `face` and carries it towards screen point `to`."""
    fx, fy = face; k = min(1., max(0., (z - 1) / .5))
    return dict(z=z, x=fx, y=fy, dx=(to[0] - fx) * k, dy=(to[1] - fy) * k, rot=0.)
def cam_params(cam):
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return z, X, Y
def cam_map(cam, wx, wy):
    z, X, Y = cam_params(cam); return X + z * (wx - cam['x']), Y + z * (wy - cam['y'])
def cam_img(img, cam):
    """a world-space image (1080x1920) seen through `cam`, exactly as engine.compose_world transforms the world."""
    z, X, Y = cam_params(cam)
    return E.zoom(img, z, (cam['x'], cam['y']), dx=X - cam['x'], dy=Y - cam['y'], rot=cam.get('rot', 0.))

T_ENTER = 849 / 30                   # 28.300: the therapist's silent pre-roll before line 12 (s05 -> s06, one shot)
def t_cam(t):
    """camera of the therapist shot that runs from s05 (28.30) through his line 12 in s06 (continuous push)."""
    return dict(z=1.0 + .022 * (t - T_ENTER), x=528., y=500., dx=0., dy=0., rot=0.)

def zoom_blur(amount, anchor=(540, 640), n=7):
    """ctx.wrap: radial motion blur of the picture (screen layers / captions stay crisp)."""
    def wrap(frame):
        rgb = frame.convert('RGB'); acc = np.asarray(rgb, np.float32).copy()
        for i in range(1, n):
            acc += np.asarray(E.zoom(rgb, 1 + amount * .18 * i / (n - 1), anchor), np.float32)
        return Image.fromarray((acc / n).astype(np.uint8)).convert('RGBA')
    return wrap
def chain(*fns):
    fns = [f for f in fns if f is not None]
    if not fns: return None
    def wrap(frame):
        for f in fns: frame = f(frame)
        return frame
    return wrap

# ------------------------------------------------------------------ fonts
_INTER = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
def inter(size, weight='Regular'):
    return E.cached(('C_inter', size, weight), lambda: ImageFont.truetype(_INTER % weight, size))
_CAVEAT = os.path.join(HERE, '_C_caveat.ttf')                     # Caveat (OFL) — ballpoint handwriting
def caveat(size):
    return E.cached(('C_cav', size), lambda: ImageFont.truetype(_CAVEAT, size))

# ================================================================== INSIGHTS insert ("My algorithm cried.")
FG, SUB, DIM, BGc = (245, 245, 245), (168, 168, 168), (38, 38, 38), (0, 0, 0)
RED = (255, 70, 86)
MX = 92                                                             # content margin: key numbers inside the safe area
CH = dict(x0=MX + 8, x1=878, y0=730, y1=1220, vmax=300)             # chart plot box (screen px) + y scale
NDAYS = 30
def _series():
    r = np.random.default_rng(7)
    prev = 182 + 26 * np.sin(np.arange(NDAYS) * .7) + r.normal(0, 14, NDAYS)
    cur = 168 + 30 * np.sin(np.arange(NDAYS) * .55 + 1.3) + r.normal(0, 16, NDAYS)
    cliff = [150, 14, 4, 3, 3, 3, 3, 3]                                # the algorithm cries
    cur[22:] = cliff[:NDAYS - 22]
    return np.clip(prev, 40, 290), np.clip(cur, 0, 290)
PREV, CUR = _series()
def _cx(d): return CH['x0'] + (CH['x1'] - CH['x0']) * d / (NDAYS - 1)
def _cy(v): return CH['y1'] - (CH['y1'] - CH['y0']) * v / CH['vmax']

def _status(d):
    d.rounded_rectangle((40, 25, 144, 63), 19, fill=(235, 52, 45))                  # iOS: screen recording
    d.text((92, 44), '9:41', font=inter(34, 'SemiBold'), fill=FG, anchor='mm')
    for k in range(4): d.rounded_rectangle((W - 238 + k * 13, 52 - 6 - k * 5, W - 229 + k * 13, 54), 2, fill=FG)
    for r, w_ in ((26, 4), (17, 4)): d.arc((W - 168 - r, 56 - r, W - 168 + r, 56 + r), 225, 315, fill=FG, width=w_)
    d.pieslice((W - 177, 47, W - 159, 65), 225, 315, fill=FG)
    d.rounded_rectangle((W - 126, 34, W - 66, 60), 8, outline=(150, 150, 150), width=3)
    d.rounded_rectangle((W - 121, 39, W - 110, 55), 4, fill=(255, 69, 58))            # low battery, of course
    d.rounded_rectangle((W - 63, 42, W - 58, 52), 2, fill=(150, 150, 150))

def insights_base():
    """static screen (RGB): status bar, nav, filter, metric label, chart grid + previous-period line, legend, the
    follower breakdown below (the caption band y≈1420-1540 is left calm)."""
    def mk():
        S = 2; im = Image.new('RGB', (W * S, H * S), BGc); d = ImageDraw.Draw(im)
        def L(pts, col, w): d.line([(x * S, y * S) for x, y in pts], fill=col, width=int(w * S), joint='curve')
        # nav
        L([(64, 168), (44, 148), (64, 128)], FG, 4.5)
        d.text((W / 2 * S, 148 * S), 'Accounts reached', font=inter(40 * S, 'SemiBold'), fill=FG, anchor='mm')
        d.ellipse(((W - 74) * S, 128 * S, (W - 34) * S, 168 * S), outline=FG, width=int(3.5 * S))
        d.text(((W - 54) * S, 149 * S), 'i', font=inter(26 * S, 'Bold'), fill=FG, anchor='mm')
        # filter row
        d.rounded_rectangle(((MX - 6) * S, 222 * S, (MX + 306) * S, 292 * S), 35 * S, fill=DIM)
        d.text(((MX + 26) * S, 257 * S), 'Last 30 days', font=inter(31 * S, 'SemiBold'), fill=FG, anchor='lm')
        L([(MX + 254, 250), (MX + 266, 262), (MX + 278, 250)], FG, 3.5)
        d.text(((W - MX) * S, 257 * S), 'Sep 13 – Oct 12', font=inter(30 * S, 'Regular'), fill=SUB, anchor='rm')
        # metric label
        d.text((MX * S, 340 * S), 'Accounts reached', font=inter(36 * S, 'Regular'), fill=SUB, anchor='lm')
        # chart grid
        for v in (0, 100, 200, 300):
            y = _cy(v)
            if v == 0: d.line((CH['x0'] * S, y * S, CH['x1'] * S, y * S), fill=(70, 70, 70), width=2 * S)
            else:
                for x in range(CH['x0'], CH['x1'], 18): d.line((x * S, y * S, (x + 9) * S, y * S), fill=(44, 44, 44), width=S * 2)
            d.text(((CH['x1'] + 22) * S, y * S), str(v), font=inter(26 * S, 'Regular'), fill=SUB, anchor='lm')
        for d_, lab in ((0, 'Sep 13'), (10, 'Sep 23'), (20, 'Oct 3'), (29, 'Oct 12')):
            d.text((_cx(d_) * S, (CH['y1'] + 44) * S), lab, font=inter(26 * S, 'Regular'), fill=SUB,
                   anchor='lm' if d_ == 0 else ('rm' if d_ == 29 else 'mm'))
        # previous period (dashed grey)
        pts = [(_cx(i), _cy(v)) for i, v in enumerate(PREV)]
        dense = []
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            for k in range(12): dense.append((xa + (xb - xa) * k / 12, ya + (yb - ya) * k / 12))
        for k in range(0, len(dense) - 4, 8): L(dense[k:k + 5], (110, 110, 110), 3.5)
        # legend
        y = 1336
        d.ellipse(((MX + 2) * S, (y - 9) * S, (MX + 20) * S, (y + 9) * S), fill=(160, 70, 230))
        d.text(((MX + 34) * S, y * S), 'Current period', font=inter(28 * S, 'Regular'), fill=SUB, anchor='lm')
        for k in range(3): d.line(((MX + 286 + k * 16) * S, y * S, (MX + 296 + k * 16) * S, y * S), fill=(110, 110, 110), width=4 * S)
        d.text(((MX + 348) * S, y * S), 'Previous period', font=inter(28 * S, 'Regular'), fill=SUB, anchor='lm')
        d.line((0, 1394 * S, W * S, 1394 * S), fill=(30, 30, 30), width=2 * S)
        # follower breakdown (below the caption band)
        y = 1612
        d.text((MX * S, y * S), 'Followers and non-followers', font=inter(34 * S, 'SemiBold'), fill=FG, anchor='lm')
        y = 1690
        d.rounded_rectangle((MX * S, y * S, (W - MX) * S, (y + 14) * S), 7 * S, fill=DIM)
        d.rounded_rectangle((MX * S, y * S, (W - MX) * S, (y + 14) * S), 7 * S, fill=(160, 70, 230))
        d.text((MX * S, (y + 58) * S), 'Followers', font=inter(28 * S, 'Regular'), fill=SUB, anchor='lm')
        d.text(((W - MX) * S, (y + 58) * S), '100%', font=inter(28 * S, 'SemiBold'), fill=FG, anchor='rm')
        d.text((MX * S, (y + 108) * S), 'Non-followers', font=inter(28 * S, 'Regular'), fill=SUB, anchor='lm')
        d.text(((W - MX) * S, (y + 108) * S), '0%', font=inter(28 * S, 'SemiBold'), fill=FG, anchor='rm')
        d.rounded_rectangle(((W / 2 - 140) * S, 1880 * S, (W / 2 + 140) * S, 1890 * S), 5 * S, fill=(200, 200, 200))
        return im.resize((W, H), Image.LANCZOS)
    return E.cached('C_ins_base', mk)

STATUS_H = 72                                                       # status-bar strip height (screen px)
PILL_BOT = 63                                                       # bottom edge of the red screen-recording pill
def status_layer():
    """the iOS status bar (RGBA strip, W x STATUS_H) — composited separately so it can fade as a punch-in pushes it
    off the top edge (a 1-8 px sliver of the red pill otherwise reads as a glitch line)."""
    def mk():
        im = Image.new('RGBA', (W, STATUS_H), (0, 0, 0, 0)); _status(ImageDraw.Draw(im)); return im
    return E.cached('C_ins_status', mk)

def _grad_line(x):
    """IG-ish magenta -> violet along the chart."""
    k = E.clamp((x - CH['x0']) / (CH['x1'] - CH['x0']))
    a, b = np.array((226, 52, 140), np.float32), np.array((146, 72, 236), np.float32)
    return tuple(int(v) for v in a + (b - a) * k)

def _fmt(n): return f'{n:,}'

def insights_frame(t, T_CUT, T_PL0, T_PL1, status_a=1.0):
    """RGB screen at time t. T_CUT: first frame of the insert; T_PL0..T_PL1: the plunge (the head of the line races
    over the cliff, the total counts down 1,204 -> 3); the red delta lands at T_PL1. status_a: status-bar opacity."""
    base = insights_base().copy()
    if status_a > .002:
        st = status_layer()
        if status_a < .998: st = E.fade(st, status_a)
        base.paste(st, (0, 0), st)
    S = 2
    # head position (in days): already drawn to the cliff edge at the cut, creeping; races over the cliff on "cried"
    if t < T_PL0: head = 21.3 + .9 * E.clamp((t - T_CUT) / max(.01, T_PL0 - T_CUT))
    else: head = 22.2 + (NDAYS - 1 - 22.2) * E.eout(E.clamp((t - T_PL0) / (T_PL1 - T_PL0)), )
    head = min(head, NDAYS - 1)
    # line + soft fill, drawn at 2x in a local strip
    x0, x1, y0, y1 = CH['x0'] - 10, CH['x1'] + 10, CH['y0'] - 40, CH['y1'] + 6
    strip = Image.new('RGBA', ((x1 - x0) * S, (y1 - y0) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(strip)
    n = int(math.floor(head)); pts = [(_cx(i), _cy(CUR[i])) for i in range(n + 1)]
    if head > n and n + 1 < NDAYS:
        f_ = head - n; pts.append((_cx(n) + (_cx(n + 1) - _cx(n)) * f_, _cy(CUR[n] + (CUR[n + 1] - CUR[n]) * f_)))
    loc = [((x - x0) * S, (y - y0) * S) for x, y in pts]
    if len(loc) >= 2:
        fill = Image.new('L', strip.size); ImageDraw.Draw(fill).polygon(loc + [(loc[-1][0], (CH['y1'] - y0) * S), (loc[0][0], (CH['y1'] - y0) * S)], fill=255)
        gy = np.linspace(.30, 0, strip.size[1], dtype=np.float32)[:, None]
        fa = (np.asarray(fill, np.float32) * gy).astype(np.uint8)
        tint = Image.new('RGBA', strip.size, (170, 60, 220, 0)); tint.putalpha(Image.fromarray(fa)); strip.alpha_composite(tint)
        for (xa, ya), (xb, yb) in zip(loc[:-1], loc[1:]):
            d.line([(xa, ya), (xb, yb)], fill=_grad_line(x0 + xa / S) + (255,), width=5 * S)
            d.ellipse((xb - 2.5 * S, yb - 2.5 * S, xb + 2.5 * S, yb + 2.5 * S), fill=_grad_line(x0 + xb / S) + (255,))
        hx, hy = loc[-1]
        d.ellipse((hx - 9 * S, hy - 9 * S, hx + 9 * S, hy + 9 * S), fill=(255, 255, 255, 255), outline=_grad_line(x0 + hx / S) + (255,), width=4 * S)
    strip = strip.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    base.paste(strip, (x0, y0), strip)
    # the big number
    d = ImageDraw.Draw(base)
    k = E.clamp((t - T_PL0) / (T_PL1 - T_PL0)) if t >= T_PL0 else 0.0
    val = int(round(math.exp(math.log(1204) + (math.log(3) - math.log(1204)) * E.eout(k) ** 1.2)))
    d.text((MX - 6, 528), _fmt(val), font=inter(166, 'Bold'), fill=FG, anchor='ls')
    # delta: grey "vs previous" until the plunge lands, then the red arrow + % drops in
    if t < T_PL1:
        d.text((MX, 592), 'vs Aug 14 – Sep 12', font=inter(34, 'Regular'), fill=SUB, anchor='lm')
    else:
        a = E.clamp((t - T_PL1) / .08)
        col = tuple(int(SUB[i] + (RED[i] - SUB[i]) * a) for i in range(3))
        d.polygon([(MX + 2, 576), (MX + 34, 576), (MX + 18, 608)], fill=col)
        d.text((MX + 46, 592), '99.8%', font=inter(40, 'SemiBold'), fill=col, anchor='lm')
        d.text((MX + 46 + inter(40, 'SemiBold').getlength('99.8%') + 16, 592), 'vs Aug 14 – Sep 12', font=inter(34, 'Regular'), fill=SUB, anchor='lm')
    return base

# ================================================================== the therapist's legal pad
PAD_W, PAD_H, STRIP = 660, 446, 46
RULE0, RULE = 112, 72                    # first rule y, rule spacing (pad px)
MARGIN_X = 92
INK = (22, 34, 104)
def _rule_y(k): return RULE0 + k * RULE

def pad_paper():
    """the legal pad (RGBA, PAD_W x PAD_H): canary paper, blue rules, red double margin, maroon gum binding with the
    torn stubs of earlier sheets, fibre/mottle, warm light falloff, a soft curl at the bottom-right corner."""
    def mk():
        r = np.random.default_rng(11)
        h, w = PAD_H, PAD_W
        base = np.zeros((h, w, 3), np.float32) + np.array((251, 240, 160), np.float32)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        light = 1.03 - .10 * ((xx / w) * .6 + (yy / h) * .7)                       # window light from top-left
        mott = np.asarray(Image.fromarray((r.normal(128, 40, (h // 8, w // 8))).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255 - .5
        fib = r.normal(0, 1, (h, w)).astype(np.float32)
        fib = np.asarray(Image.fromarray(((fib * 30) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255 - .5
        base = base * (light + .035 * mott + .035 * fib)[..., None]
        im = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
        for k in range(6):                                                           # rules
            y = _rule_y(k); d.line((0, y, w, y), fill=(98, 150, 205, 150), width=2)
        for x in (MARGIN_X - 7, MARGIN_X):                                           # margin
            d.line((x, STRIP, x, h), fill=(214, 92, 96, 165), width=2)
        # gum binding + torn stubs of the sheets already used this session
        d.rectangle((0, 0, w, STRIP), fill=(112, 30, 36, 255))
        g = np.asarray(im, np.float32)
        g[:STRIP, :, :3] *= (1 + .10 * r.normal(0, 1, (STRIP, w, 1)).astype(np.float32)).clip(.7, 1.3)
        g[:STRIP, :, :3] *= np.linspace(1.15, .82, STRIP, dtype=np.float32)[:, None, None]
        im = Image.fromarray(g.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
        x = 0; stub = []
        while x < w:
            stub.append((x, STRIP + 2 + r.uniform(0, 7))); x += r.uniform(5, 14)
        stub.append((w, STRIP + 3))
        d.polygon([(0, STRIP)] + stub + [(w, STRIP)], fill=(246, 236, 168, 255))
        d.line(stub, fill=(205, 192, 120, 255), width=1)
        d.line((0, STRIP, w, STRIP), fill=(70, 18, 22, 255), width=2)
        # corner curl shadow
        a = np.asarray(im, np.float32); cy_, cx_ = h - 1, w - 1
        dist = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2); curl = np.clip(1 - dist / 90, 0, 1) ** 2
        a[..., :3] *= (1 - .18 * curl)[..., None]
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 7, fill=255)
        im.putalpha(m)
        return im
    return E.cached('C_pad', mk)

def _ink_text(text, size, rot=0.0, seed=0):
    """handwritten line in ballpoint (RGBA, tight + pad 10): slight pressure mottle, soft edge, a tiny tilt."""
    def mk():
        f = caveat(size * 2); l, t_, r_, b = f.getbbox(text)
        im = Image.new('L', (r_ - l + 40, b - t_ + 40)); ImageDraw.Draw(im).text((20 - l, 20 - t_), text, font=f, fill=255)
        im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
        if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
        a = np.asarray(im, np.float32) / 255
        rng = np.random.default_rng(seed)
        press = np.asarray(Image.fromarray((rng.normal(128, 50, (max(1, im.height // 6), max(1, im.width // 6)))).clip(0, 255).astype(np.uint8)).resize(im.size, Image.BICUBIC), np.float32) / 255
        a = a * (.80 + .20 * press)
        out = Image.new('RGBA', im.size, INK + (0,)); out.putalpha(Image.fromarray((a * 240).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.35)))
        return out, (20 - l) / 2, (20 - t_) / 2      # offsets of the font origin inside the image
    return E.cached(('C_ink', text, size, rot, seed), mk)

def _stroke_poly(pts, frac):
    """the first `frac` (0..1) of a polyline by length."""
    if frac <= 0 or len(pts) < 2: return []
    L = [0.0]
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]): L.append(L[-1] + math.hypot(xb - xa, yb - ya))
    tot = L[-1] * min(1., frac); out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= tot: out.append(pts[i])
        else:
            k = (tot - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); xa, ya = pts[i - 1]; xb, yb = pts[i]
            out.append((xa + (xb - xa) * k, ya + (yb - ya) * k)); break
    return out

def _wob(pts, seed, amp=1.1, n=6):
    """resample a polyline and add a hand wobble."""
    rng = np.random.default_rng(seed); out = []
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        for k in range(n): out.append((xa + (xb - xa) * k / n, ya + (yb - ya) * k / n))
    out.append(pts[-1])
    ph = rng.uniform(0, 6.28, 2)
    return [(x + amp * math.sin(i * .9 + ph[0]), y + amp * math.sin(i * .7 + ph[1])) for i, (x, y) in enumerate(out)]

# pad lines: (key, text, size, x, rule index, tilt deg)
PAD_LINES = [
    ('note', 'Kevin: feels "creative" ??', 44, MARGIN_X + 18, 0, .6),
    ('head', 'Instagram needs:', 60, MARGIN_X + 18, 1, -.4),
    ('n1', '1. Consistency', 66, MARGIN_X + 34, 2, .5),
    ('n2', '2. Good lighting', 66, MARGIN_X + 34, 3, -.3),
    ('n3', '3. Reels', 66, MARGIN_X + 34, 4, .4),
]
def _line_layer(key):
    for i, (k, text, size, x, ri, tilt) in enumerate(PAD_LINES):
        if k == key:
            im, ox, oy = _ink_text(text, size, tilt, seed=i + 3)
            f = caveat(size); asc = f.getmetrics()[0]
            return im, int(x - ox), int(_rule_y(ri) - 7 - asc - oy)
    raise KeyError(key)

def _reveal(im, frac, soft=26):
    """left-to-right write-on of an ink layer (frac 0..1)."""
    if frac >= 1: return im
    if frac <= 0: return None
    a = np.asarray(im.getchannel('A'), np.float32)
    x = np.arange(im.width, dtype=np.float32); edge = -soft + (im.width + soft) * frac
    ramp = np.clip((edge - x) / soft + 1, 0, 1)
    out = im.copy(); out.putalpha(Image.fromarray((a * ramp[None, :]).astype(np.uint8))); return out

def _reel_strokes(x, y, s=56):
    """the Reels glyph, doodled: rounded square, clapper band with two slashes, play triangle (pad px)."""
    r = s * .22; pts = []
    for k in range(9): a = math.pi + k / 8 * math.pi / 2; pts.append((x + r + r * math.cos(a), y + r + r * math.sin(a)))
    for k in range(9): a = 1.5 * math.pi + k / 8 * math.pi / 2; pts.append((x + s - r + r * math.cos(a), y + r + r * math.sin(a)))
    for k in range(9): a = k / 8 * math.pi / 2; pts.append((x + s - r + r * math.cos(a), y + s - r + r * math.sin(a)))
    for k in range(9): a = math.pi / 2 + k / 8 * math.pi / 2; pts.append((x + r + r * math.cos(a), y + s - r + r * math.sin(a)))
    pts.append(pts[0])
    band = [(x + 2, y + s * .30), (x + s - 2, y + s * .30)]
    sl1 = [(x + s * .30, y + 2), (x + s * .42, y + s * .29)]
    sl2 = [(x + s * .60, y + 2), (x + s * .72, y + s * .29)]
    tri = [(x + s * .40, y + s * .45), (x + s * .40, y + s * .84), (x + s * .72, y + s * .645), (x + s * .40, y + s * .45)]
    return [(_wob(pts, 1, .9, 2), .40), (_wob(band, 2), .12), (_wob(sl1, 3), .08), (_wob(sl2, 4), .08), (_wob(tri, 5, .8), .32)]

def _draw_strokes(layer, strokes, frac, width=3.6):
    """draw a list of (polyline, share) strokes progressively (frac 0..1 of the whole doodle), 2x supersampled."""
    S = 2; big = Image.new('L', (layer.width * S, layer.height * S)); d = ImageDraw.Draw(big); acc = 0.0
    for pts, share in strokes:
        f = E.clamp((frac - acc) / share); acc += share
        if f <= 0: break
        seg = _stroke_poly(pts, f)
        if len(seg) >= 2: d.line([(px * S, py * S) for px, py in seg], fill=230, width=int(width * S), joint='curve')
    a = big.resize(layer.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(.35))
    ink = Image.new('RGBA', layer.size, INK + (0,)); ink.putalpha(a); layer.alpha_composite(ink)

def _shadow_for(w, h, blur=22, op=.50, off=(8, 20)):
    def mk():
        pad = blur * 3
        a = Image.new('L', (w + 2 * pad, h + 2 * pad)); ImageDraw.Draw(a).rounded_rectangle((pad + off[0], pad + off[1], pad + off[0] + w, pad + off[1] + h), 8, fill=int(255 * op))
        a = a.filter(ImageFilter.GaussianBlur(blur))
        sh = Image.new('RGBA', a.size, (20, 12, 6, 0)); sh.putalpha(a); return sh, pad
    return E.cached(('C_padsh', w, h, blur, op, off), mk)

def notepad(t, sched):
    """the pad at time t (RGBA, with its contact shadow; centre = pad centre). sched: dict key -> (t0, dur) write-on
    times for 'head', 'ul', 'n1', 'n2', 'n3', 'reel' ('note' is already written)."""
    pad = pad_paper().copy()
    for key, *_ in PAD_LINES:
        im, x, y = _line_layer(key)
        if key == 'note': frac = 1.0
        else:
            t0, dur = sched[key]; frac = E.clamp((t - t0) / dur)
            frac = 1 - (1 - frac) ** 1.6 if frac < 1 else 1.0      # pen speeds up then eases out
        piece = _reveal(im, frac)
        if piece is not None: pad.alpha_composite(piece, (x, y))
    # underline under the heading
    t0, dur = sched['ul']
    if t >= t0:
        im, x, y = _line_layer('head'); x1 = x + im.width - 14; yu = _rule_y(1) + 6
        ul = [(x + 22, yu + 2), (x1 * .5 + x * .5, yu - 1), (x1, yu + 3)]
        _draw_strokes(pad, [(_wob(ul, 9, .7, 10), 1.0)], E.clamp((t - t0) / dur), 3.2)
    # the Reels doodle after "3. Reels"
    t0, dur = sched['reel']
    if t >= t0:
        im, x, y = _line_layer('n3')
        _draw_strokes(pad, _reel_strokes(x + im.width + 14, _rule_y(4) - 64, 54), E.clamp((t - t0) / dur), 3.4)
    sh, p = _shadow_for(PAD_W, PAD_H)
    out = sh.copy(); out.alpha_composite(pad, (p, p))
    return out

# ================================================================== the lamp ("Good lighting.")
LAMP = (764, 668)                    # the bright opening of the brass floor lamp's shade, world px in angle 'I'
def _radial(cx, cy, rx, ry, power=2.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - d, 0, 1) ** power
def lamp_maps():
    """world-space light maps (L images): 'pool' warm spill on the bookcase/wall, 'cone' the light thrown down from
    the shade, 'bulb' the hot opening, 'key' the warm key on Instagram's face/shoulder."""
    def mk():
        pool = _radial(LAMP[0] + 10, LAMP[1] - 30, 420, 470, 1.8)
        key = _radial(560, 470, 430, 520, 1.6)
        cone = Image.new('L', (W, H)); ImageDraw.Draw(cone).polygon([(LAMP[0] - 70, LAMP[1]), (LAMP[0] + 75, LAMP[1]), (LAMP[0] + 260, 1500), (LAMP[0] - 250, 1500)], fill=120)
        cone = np.asarray(cone.filter(ImageFilter.GaussianBlur(60)), np.float32) / 255 * np.clip(1 - (np.mgrid[0:H, 0:W][0] - LAMP[1]) / 900, 0, 1)
        bulb = Image.new('L', (W, H)); ImageDraw.Draw(bulb).ellipse((LAMP[0] - 74, LAMP[1] - 9, LAMP[0] + 74, LAMP[1] + 9), fill=255)
        bulb = np.maximum(np.asarray(bulb.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255,
                          np.asarray(bulb.filter(ImageFilter.GaussianBlur(26)), np.float32) / 255 * .8)
        to = lambda a: Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
        return dict(pool=to(pool), key=to(key), cone=to(cone), bulb=to(bulb))
    return E.cached('C_lamp_maps', mk)

def lamp_off_plate():
    """angle 'I' plate with the lamp off: the hot opening of the shade and its spill dimmed."""
    def mk():
        sharp = E.plate('I')[0]; a = np.asarray(sharp, np.float32)
        m = np.asarray(lamp_maps()['bulb'], np.float32) / 255; p = np.asarray(lamp_maps()['pool'], np.float32) / 255
        a = a * (1 - .72 * m[..., None]) * (1 - .14 * p[..., None])
        return Image.fromarray(a.clip(0, 255).astype(np.uint8))
    return E.cached('C_lamp_off', mk)

def lamp_level(t, t_on):
    """the switch: on, a one-frame stutter, on (incandescent: no fade-in beyond a frame)."""
    if t < t_on - 1e-6: return 0.0
    j = fr(t) - fr(t_on)
    return {0: .85, 1: .30, 2: 1.0, 3: .82}.get(j, 1.0)

_LCOL = np.array((1.0, .86, .62), np.float32)
def _lamp_light():
    """world-space light, cached: key (H,W,1) and additive spill (pool + cone + bulb) (H,W,3), float32."""
    def mk():
        M = lamp_maps(); g = lambda k: np.asarray(M[k], np.float32)[..., None] / 255
        add = g('pool') * np.array((70, 42, 14), np.float32) + g('cone') * np.array((60, 40, 18), np.float32) \
            + g('bulb') * np.array((255, 236, 196), np.float32) * 1.1
        return g('key'), add
    return E.cached('C_lamp_light', mk)

KEY_GAIN = .18                       # warm key on his face (polish: .30 clipped the skin's red channel flat orange)
KNEE = 196.                          # soft highlight shoulder on the take: identity below, rolls off toward 255
def shoulder(a, knee=KNEE):
    """C1-continuous film shoulder: values above `knee` roll off exponentially toward 255 (no hard clip on skin)."""
    hi = a > knee
    if hi.any():
        r = 255. - knee; a[hi] = knee + r * (1 - np.exp(-(a[hi] - knee) / r))
    return a

def _light(a, L, box=None, roll=False):
    """the lamp's exposure + warm key + spill on a world-space RGB float array (in place where possible).
    roll: apply the highlight shoulder (the take — keeps pore / forehead texture under the key)."""
    key, add = _lamp_light()
    if box is not None: y0, y1, x0, x1 = box; key, add = key[y0:y1, x0:x1], add[y0:y1, x0:x1]
    a *= 1 + L * .06 * _LCOL + key * (L * KEY_GAIN * _LCOL)
    a += L * add
    if roll: shoulder(a)
    return a

def lamp_plate(L):
    """angle 'I' plate lit by the lamp at level L (cached per level: on, and the stutter levels)."""
    def mk():
        a = np.asarray(E.plate('I')[0], np.float32).copy()
        return Image.fromarray(np.clip(_light(a, L), 0, 255).astype(np.uint8))
    return E.cached(('C_lamp_plate', round(L, 3)), mk)

def lamp_take(L):
    """fx for cu_take: the lamp's light on the keyed take (world space, inside the matte's bounding box)."""
    def fx(img):
        al = img.getchannel('A'); bb = al.getbbox()
        if bb is None: return img
        x0, y0, x1, y1 = bb
        a = np.asarray(img.crop(bb).convert('RGB'), np.float32).copy()
        out = img.copy()
        out.paste(Image.fromarray(np.clip(_light(a, L, (y0, y1, x0, x1), roll=True), 0, 255).astype(np.uint8)), (x0, y0))
        out.putalpha(al)
        return out
    return fx

def lamp_bloom(L):
    """ctx.wrap: soft beauty bloom of the lit picture's highlights (screen space). Screen-blended, not added: the
    glow lifts the shade/bulb halo but rolls off on bright skin instead of clipping it flat (polish pass)."""
    if L <= .001: return None
    def wrap(frame):
        rgb = frame.convert('RGB')
        hi = np.clip(np.asarray(rgb.resize((W // 6, H // 6), Image.BILINEAR), np.float32) - 170, 0, None)
        bl = Image.fromarray(np.clip(hi * 2.2 * .40 * L, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
        from PIL import ImageChops
        return ImageChops.screen(rgb, bl).convert('RGBA')
    return wrap

def lamp_wrap(L, cam):
    """ctx.wrap: the lamp's light on the picture (screen space via `cam`); L = 0..1. (slow path; s06 uses the
    world-space lamp_plate / lamp_take / lamp_bloom, which give the same light at a third of the cost)"""
    if L <= .001: return None
    def wrap(frame):
        M = lamp_maps(); g = lambda k: np.asarray(cam_img(M[k], cam), np.float32)[..., None] / 255
        a = np.asarray(frame.convert('RGB'), np.float32)
        key, pool, cone, bulb = g('key'), g('pool'), g('cone'), g('bulb')
        a = a * (1 + L * (.06 + KEY_GAIN * key) * np.array((1.0, .86, .62), np.float32))     # exposure + warm key
        a = a + L * (pool * np.array((70, 42, 14), np.float32) + cone * np.array((60, 40, 18), np.float32))
        a = a + L * bulb * np.array((255, 236, 196), np.float32) * 1.1
        # beauty glow: blooming highlights
        sm = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W // 6, H // 6), Image.BILINEAR)
        hi = np.clip(np.asarray(sm, np.float32) - 170, 0, None)
        bl = Image.fromarray(np.clip(hi * 2.2, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
        a = a + L * .40 * np.asarray(bl, np.float32)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return wrap

# ================================================================== close-up matte (tighter rim for CUs)
_gx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]
def graded_cu(spk, src_t, angle=None, rim_px=7, wrap_px=5):
    """engine.graded() for close shots: same key, grade and light match, but a narrower window rim / light-wrap band
    and a 1 px tighter matte, so the edge doesn't read as a cut-out outline when the camera is at z 1.3-1.7."""
    angle = angle or spk; f = E.take(spk).raw(src_t)
    hit = E._C.get(('C_gcu', spk, angle))
    if hit is not None and hit[0] is f: return hit[1]
    from scipy.ndimage import minimum_filter
    A = E.ANGLES[angle]; sharp, wrap, mean = E.plate(angle)
    rgb, al = E.key(f)
    rgb = rgb * np.array(A['grade'], np.float32)
    cm = rgb[al > .5].mean(0) if (al > .5).any() else rgb.reshape(-1, 3).mean(0)
    rgb = rgb * (1 + .12 * (mean / (cm + 1e-3) - 1))
    lit = np.clip(.5 + .5 * A['side'] * _gx, 0, 1)
    rgb = rgb * (1 - A['amt'] * .6 + A['amt'] * 1.2 * lit) + np.array(A['key'], np.float32) * A['amt'] * .22 * lit
    band = np.clip(al - minimum_filter(al, size=rim_px), 0, 1)[..., None]
    side = np.clip(.5 + A['rside'] * _gx * 1.5, 0, 1)
    e = band * side * A['ramt'] * .55
    rgb = rgb * (1 - e) + np.array(A['rim'], np.float32) * e
    a8 = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    al = np.asarray(a8, np.float32) / 255
    edge = np.clip(al - minimum_filter(al, size=wrap_px), 0, 1)[..., None]
    rgb = rgb * (1 - .30 * edge) + np.asarray(wrap, np.float32) * .30 * edge
    out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); out.putalpha(a8)
    E._C[('C_gcu', spk, angle)] = (f, out); return out

def cu_take(ctx, spk, src_t, angle=None, fx=None):
    """show take `spk` through graded_cu (as the 'behind' layer, the engine's own take switched off).
    fx: optional fn(RGBA) -> RGBA applied to the take in world space (e.g. the lamp light)."""
    ctx.shot.update(show=False, spk=spk, src=src_t, angle=angle or spk)
    img = graded_cu(spk, src_t, angle)
    if fx is not None: img = fx(img)
    ctx.add('behind', img, 0, 0, center=False)
