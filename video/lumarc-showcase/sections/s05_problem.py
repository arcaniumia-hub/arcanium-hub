"""s05 — THE PROBLEM (18.00–25.24).
"Here's the problem. Your work might be amazing. But online, nobody can taste your food, feel your service,
or see your skill."

TL10  punch-in cut; on "PROBLEM" a snap zoom slams onto his face (zoom blur, white flash, RGB split, shake).
TL11  cut wide; on "amazing" a warm golden bloom + anamorphic light leak blooms BEHIND him and gold sparkles
      twinkle around his silhouette — the work is great.
TL12  cut tighter; "But" drains the warmth (cold grade); on "online" a thin pane of glass slides across the frame
      between us and him (refraction strip + prism fringe on its leading edge, screen sheen) — now he's behind a screen.
TL13-15  SIGNATURE — GLASS LAYERS. Three frosted-glass panes, one per sense:
      TASTE (22.19) pane slides in from the left beside him; FEEL (23.18) it narrows to a third while a second pane
      slides in from the right — he's framed in the gap; SEE (24.42) the third pane drops in over him and the three
      lock into a full-screen triptych (food / service / skill close-ups with parallax, prism edges, moving specular).
Handoff to s06 (25.24): the triptych at TRIP_* geometry, scaled by trip_scale(END), is on screen.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E

START, END = E.span(10, 15)                   # 18.00 – 25.24
T10, T11, T12, T13, T14, T15 = (E.TL[i]['t0'] for i in range(10, 16))
# onsets measured on the voice track (10 ms spectral envelope: stop bursts, fricative onsets, vowel nuclei)
W_PROBLEM, W_AMAZING, W_MA, W_BUT, W_ONLINE = 18.34, 19.96, 20.21, 20.72, 20.86
W_WORK = 19.11
W_TASTE, W_YOURFOOD, W_FEEL, W_YOURSERV, W_SEE, W_YOURSKILL = 22.19, 22.50, 23.18, 23.47, 24.42, 24.66

CUES = [
    (T10 + .01, 'whoosh', {'gain': -8}),        # punch-in cut
    (W_PROBLEM, 'impact', {}),                   # snap zoom on PROBLEM
    (W_WORK, 'shimmer', {'gain': -12}),         # warm light starts on "work"
    (W_AMAZING, 'swoosh_up', {'gain': -6}),      # back-light + streak bloom
    (W_MA, 'shimmer', {'gain': -6}),             # bokeh drift
    (W_BUT, 'tick', {'gain': -6}),               # warmth drains
    (W_ONLINE - .04, 'glass', {}),               # screen pane slides across
    (T13 + .01, 'whoosh', {'gain': -12}),         # cut wider, still behind the screen
    (21.60, 'click', {'gain': -4}),          # tap on the glass ("nobody")
    (21.96, 'click', {'gain': -6}),          # second tap ("can")
    (W_TASTE - .04, 'glass', {}),                # pane 1 shoves the screen away
    (T14 + .01, 'whoosh', {'gain': -12}),         # z-snap cut
    (W_FEEL - .04, 'glass', {}),                 # pane 2
    (W_SEE - .04, 'glass', {}),                  # pane 3
    (W_SEE + .30, 'click', {'gain': -4}),        # triptych locks
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H
def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def expo(x): x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0


def w2o(cam, wx, wy):
    """world -> output coordinates for a camera dict (mirrors the engine's clamp)."""
    z = max(1.0, cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return X + (wx - cam['x']) * z, Y + (wy - cam['y']) * z


def cam_for_face(z, fx, fy, wx=520., wy=690.):
    """camera (anchor = default centre) that puts world point (wx, wy) at output (fx, fy) at zoom z."""
    return dict(z=z, x=540., y=820., dx=fx - 540. - (wx - 540.) * z, dy=fy - 820. - (wy - 820.) * z, rot=0.)


def graded(fr, sat=1., br=1., tint=(1., 1., 1.)):
    """saturation + exposure + per-channel tint, done with PIL blend / LUTs (≈15 ms instead of a float pass)."""
    fr = fr.convert('RGB')
    if abs(sat - 1) > .004: fr = Image.blend(fr.convert('L').convert('RGB'), fr, sat)
    m = [br * c for c in tint]
    if max(abs(v - 1) for v in m) > .002:
        fr = fr.point([min(255, int(v * k + .5)) for k in m for v in range(256)])
    return fr


# ================================================================ captions on the voice (shared with s06)
# The engine's caption onsets are syllable estimates snapped to energy dips; inside TL11/13/16 they drift by up to
# 9 frames ("might be amazing" pops a word early, "can" lands on "taste" and never shows, "see" pops on "only").
# These sections draw the SAME caption pages with the engine's own layout / pop / art, re-timed to measured onsets,
# and only the pages of the segment on screen (no ghost of the previous page over a cut).
VOICE = {10: (18.06, 18.25, 18.33), 11: (18.84, 19.11, 19.51, 19.79, 19.96), 12: (20.72, 20.87),
         13: (21.59, 21.96, 22.16, 22.47, 22.62), 14: (23.15, 23.47, 23.58), 15: (24.32, 24.41, 24.68, 24.76),
         16: (25.29, 25.51, 25.80, 26.29, 26.41), 17: (26.92, 27.07, 27.61, 27.70, 27.84, 28.28)}


def voice_pages():
    def mk():
        pages = [dict(p, words=[dict(w) for w in p['words']]) for p in E.PAGES if p['seg'] in VOICE]
        for sg, ts in VOICE.items():
            ws = [w for p in pages if p['seg'] == sg for w in p['words']]
            assert len(ws) == len(ts), (sg, [w['text'] for w in ws])
            for w, t0 in zip(ws, ts): w['t0'] = t0
            for a, b in zip(ws[:-1], ws[1:]): a['t1'] = max(a['t0'] + .06, b['t0'])
            ws[-1]['t1'] = max(ws[-1]['t1'], ws[-1]['t0'] + .2)
        for j, p in enumerate(pages):
            nxt = pages[j + 1]['words'][0]['t0'] if j + 1 < len(pages) else E.DUR; last = p['words'][-1]['t1']
            p['a'] = p['words'][0]['t0'] - .04; p['z'] = nxt - .02 if nxt - last < .5 else last + .35
        return pages
    return E.cached('s05_vpages', mk)


def seg_at(t):
    i = 0
    while i + 1 < len(E.TL) and E.TL[i + 1]['t0'] <= t: i += 1
    return i


def page_start(seg, k):
    # time the k-th caption page of a segment starts
    return [p for p in voice_pages() if p['seg'] == seg][k]['a']


def page_end(seg, k):
    return [p for p in voice_pages() if p['seg'] == seg][k]['z']


def voice_captions(ctx, t):
    # replaces the engine captions for this frame (same look, measured timing, current segment only)
    if not ctx.captions: return
    ctx.captions = False; sg = seg_at(t); base = ctx.cap_size
    for p in voice_pages():
        if p['seg'] != sg or not (p['a'] <= t < p['z']): continue
        for w, sz, cx, cy in E._layout(p, base):          # mirrors engine.draw_captions
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.06
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = E.fade(img, lt / .05)
            if p['z'] - t < .06: img = E.fade(img, (p['z'] - t) / .06)
            w0 = img.width
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            # the pop grows a word AWAY from the line centre (anchored on its inner edge), so the overshoot never
            # eats the word gap ("YOURCONTENT."); a word on the centre line grows symmetrically
            x = W / 2 + cx - img.width / 2
            if cx < -40: x = W / 2 + cx + w0 / 2 - img.width
            elif cx > 40: x = W / 2 + cx - w0 / 2
            ctx.screen.append(dict(img=img, xy=(int(x), int(ctx.cap_y + cy - img.height / 2)), glass=0))


# ================================================================ glass panes (shared with s06)
TRIP_Y, TRIP_H, TRIP_W, TRIP_M, TRIP_G = 120, 1680, 324, 36, 18
SLOTS = [TRIP_M, TRIP_M + TRIP_W + TRIP_G, TRIP_M + 2 * (TRIP_W + TRIP_G)]       # 36, 378, 720
RIM, R_OUT, R_IN = 13, 34, 22
PANES = dict(food=('close_food', 'TASTE', 'YOUR FOOD', .50, .58),
             service=('close_service', 'FEEL', 'YOUR SERVICE', .52, .44),
             skill=('close_skill', 'SEE', 'YOUR SKILL', .42, .5))


def rrect_mask(w, h, r):
    def mk():
        m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
    return E.cached(('s05_rr', w, h, r), mk)


def pane_shadow(w, h):
    def mk():
        pad = 70; m = Image.new('L', (w + 2 * pad, h + 2 * pad))
        ImageDraw.Draw(m).rounded_rectangle((pad, pad, pad + w, pad + h), R_OUT, fill=255)
        return m.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * .62)), pad
    return E.cached(('s05_sh', w, h), mk)


def photo_src(name, h):
    """close-up scaled to a little taller than the pane (room for parallax)."""
    def mk():
        im = E.asset(name); s = h * 1.14 / im.height
        return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return E.cached(('s05_ph', name, h), mk)


def tracked(text, size, wght, track):
    def mk():
        f = E.font(size, wght); ws = [f.getlength(c) for c in text]; asc, desc = f.getmetrics()
        m = Image.new('L', (int(sum(ws) + track * len(text)) + 40, asc + desc + 30)); d = ImageDraw.Draw(m); x = 20
        for c, w in zip(text, ws): d.text((x, 12), c, font=f, fill=255); x += w + track
        return m.crop(m.getbbox())
    return E.cached(('s05_trk', text, size, wght, track), mk)


def label_art(word, sub):
    """big white sense word + tracked gradient sub line, with a soft dark halo for legibility."""
    def mk():
        big = tracked(word, 82, 800, 3); sm = tracked(sub, 34, 600, 3)
        w = max(big.width, sm.width) + 80; h = big.height + sm.height + 22 + 80
        M = Image.new('L', (w, h)); M.paste(big, ((w - big.width) // 2, 40)); M2 = Image.new('L', (w, h))
        M2.paste(sm, ((w - sm.width) // 2, 40 + big.height + 22))
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        halo = Image.new('RGBA', (w, h), (4, 4, 10, 0)); halo.putalpha(Image.fromarray(np.maximum(np.asarray(M), np.asarray(M2))).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .8)))
        out.alpha_composite(halo, (0, 4))
        c = Image.new('RGBA', (w, h), E.WHITE + (0,)); c.putalpha(M); out.alpha_composite(c)
        g = E.gradient(w, h, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(M2); out.alpha_composite(g)
        return out, 40 + big.height + 11          # split row between big word and sub line
    return E.cached(('s05_lab', word, sub), mk)


def fringe_art(w, h):
    """prismatic refraction edges + bevel: warm fringe on one side, cyan on the other, white top bevel."""
    def mk():
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        # outer bevel
        d.rounded_rectangle((1, 1, w - 2, h - 2), R_OUT, outline=(255, 255, 255, 120), width=2)
        # inner image border (refraction): cyan inside-left/top, warm inside-right/bottom
        x0, y0, x1, y1 = RIM - 2, RIM - 2, w - RIM + 1, h - RIM + 1
        lay = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.line([(x0, y0 + R_IN), (x0, y1 - R_IN)], fill=(90, 210, 255, 210), width=3)
        dl.line([(x1, y0 + R_IN), (x1, y1 - R_IN)], fill=(255, 120, 70, 200), width=3)
        dl.line([(x0 + R_IN, y0), (x1 - R_IN, y0)], fill=(200, 230, 255, 200), width=2)
        dl.line([(x0 + R_IN, y1), (x1 - R_IN, y1)], fill=(255, 150, 210, 160), width=3)
        dl.line([(x0 + 4, y0 + R_IN), (x0 + 4, y1 - R_IN)], fill=(255, 90, 200, 90), width=2)
        dl.line([(x1 - 4, y0 + R_IN), (x1 - 4, y1 - R_IN)], fill=(120, 140, 255, 110), width=2)
        im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.6)))
        # top-left catch light on the rim
        cl = Image.new('L', (w, h)); dc = ImageDraw.Draw(cl)
        dc.rounded_rectangle((3, 3, w - 4, h - 4), R_OUT - 2, outline=255, width=3)
        g = np.clip(1.2 - np.linspace(0, 1, h)[:, None] * 1.6 - np.linspace(0, 1, w)[None, :] * .5, 0, 1)
        cl = Image.fromarray((np.asarray(cl) * g).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
        wh = Image.new('RGBA', (w, h), (255, 255, 255, 0)); wh.putalpha(cl); im.alpha_composite(wh)
        return im
    return E.cached(('s05_fr', w, h), mk)


def label_grad(w, h):
    """dark gradient at the bottom of the photo so the label reads on any image."""
    def mk():
        g = np.clip((np.linspace(0, 1, h) - .52) / .48, 0, 1) ** 1.4 * 215
        a = Image.fromarray(np.repeat(g[:, None], w, 1).astype(np.uint8))
        im = Image.new('RGBA', (w, h), (8, 6, 16, 0)); im.putalpha(a); return im
    return E.cached(('s05_lg', w, h), mk)


def specular(w, h, pos, amp):
    """soft diagonal glare band (alpha L image). pos 0..1 travels from top-left to bottom-right."""
    if amp <= .01: return None
    sw, sh = max(8, w // 4), max(8, h // 4)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    u = (xx * 4 * .94 + yy * 4 * .34)                     # steep diagonal
    span = w * .94 + h * .34; c = -260 + pos * (span + 520)
    band = np.exp(-((u - c) / 70) ** 2) * .55 + np.exp(-((u - c - 150) / 24) ** 2) * .35
    a = Image.fromarray(np.clip(band * 255 * amp, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    return a


def draw_pane(fr, blur, key, x, y, w, h, t, vx=0., vy=0., land=0., label_k=0., sub_k=0., spec=None, flash=0., par=(0., 0.), lab_a=1.):
    """composite one glass pane onto output frame `fr` (RGBA, in place). blur = frosted version of fr."""
    name, word, sub, fx, fy = PANES[key]
    x, y, w, h = int(round(x)), int(round(y)), int(round(w)), int(round(h))
    if x > W or y > H or x + w < 0 or y + h < 0 or w < 2 * RIM + 4: return
    # 1. shadow on the world
    sm, pad = pane_shadow(w, h)
    fr.paste((0, 0, 0, 255), (x - pad, y - pad + 22), sm)
    # 2. frosted rim: blurred world, lifted and cooled
    m = rrect_mask(w, h, R_OUT)
    box = (x, y, x + w, y + h)
    fz = blur.crop(box)
    fr.paste(fz, (x, y), m)
    # 3. photo inside (parallax: the image lags behind the pane and drifts slowly)
    iw, ih = w - 2 * RIM, h - 2 * RIM
    REF = TRIP_H - 2 * RIM
    src = photo_src(name, REF)                 # one cached source; the slow triptych push resamples a box of it
    sc = ih / REF; bw, bh = iw / sc, ih / sc
    cx = src.width * fx - bw / 2 + par[0] / sc; cy = (src.height - bh) * fy + par[1] / sc
    cx = clamp(cx, 0, src.width - bw); cy = clamp(cy, 0, src.height - bh)
    if abs(sc - 1) < 1e-3: ph = src.crop((int(cx), int(cy), int(cx) + iw, int(cy) + ih))
    else: ph = src.resize((iw, ih), Image.BILINEAR, box=(cx, cy, cx + bw, cy + bh))
    sp = math.hypot(vx, vy)
    if sp > 4:   # chromatic split along the motion (glass refraction at speed)
        k = min(16, sp * .22); ux, uy = vx / sp, vy / sp
        r, g, b = ph.split()
        r = r.transform(r.size, Image.AFFINE, (1, 0, -ux * k, 0, 1, -uy * k), Image.BILINEAR)
        b = b.transform(b.size, Image.AFFINE, (1, 0, ux * k, 0, 1, uy * k), Image.BILINEAR)
        ph = Image.merge('RGB', (r, g, b))
    if flash > .01: ph = Image.blend(ph, Image.new('RGB', ph.size, (255, 246, 236)), flash * .55)
    ph = ph.convert('RGBA'); ph.alpha_composite(label_grad(iw, ih))
    # label
    if label_k > 0 and lab_a > .01:
        lab, split = label_art(word, sub)
        lab = lab.copy()
        if sub_k < 1:   # sub line reveals on its own words
            a = np.asarray(lab.getchannel('A')).copy(); a[split:] = (a[split:] * clamp(sub_k)).astype(np.uint8)
            lab.putalpha(Image.fromarray(a))
        k = eout(label_k); off = int(46 * (1 - k))
        if k < 1 or lab_a < 1: lab = E.fade(lab, clamp(label_k * 2) * clamp(lab_a))
        lx = (iw - lab.width) // 2; ly = ih - lab.height - 70 + off
        ph.alpha_composite(lab, (lx, max(0, ly)))
    im = rrect_mask(iw, ih, R_IN)
    fr.paste(ph, (x + RIM, y + RIM), im)
    # 4. prism edges + bevel + moving specular
    fr.alpha_composite(fringe_art(w, h), (x, y)) if (x >= 0 and y >= 0 and x + w <= W and y + h <= H) else E._paste(fr, dict(img=fringe_art(w, h), xy=(x, y), glass=0))
    if spec is not None:
        a = specular(w, h, *spec)
        if a is not None:
            a = Image.fromarray(np.minimum(np.asarray(a), np.asarray(m)))
            fr.paste(Image.new('RGBA', (w, h), (255, 252, 248, 255)), (x, y), a)


def frosted(fr):
    """cheap frosted-glass version of the whole frame (blur at quarter res, lifted + cooled)."""
    s = fr.convert('RGB').resize((W // 4, H // 4), Image.BOX).filter(ImageFilter.GaussianBlur(5))
    s = s.point(E.cached('s05_frost_lut', lambda: [min(255, int(v * .78 + o + .5)) for o in (44, 44, 62) for v in range(256)]))
    return s.resize((W, H), Image.BILINEAR)        # lift + cool at quarter res (a LUT), then upscale (RGB; pasted by mask)


# ---------------------------------------------------------------- pane choreography
TA0, TB0, TC0 = W_TASTE - .08, W_FEEL - .08, W_SEE - .08   # entry starts
SLIDE = .42
LOCK = TC0 + SLIDE                                         # triptych complete ≈ 24.78 ("skill")


def slide(t, t0, d=SLIDE):
    """position 0..1 with a tiny settle; returns (k, velocity per frame)."""
    def f(tt):
        u = clamp((tt - t0) / d)
        return back(u, 1.15) if u < 1 else 1.0
    return f(t), f(t) - f(t - 1 / 30)


def trip_scale(t):
    return 1 + .03 * smooth((t - LOCK) / (END - LOCK + .4))


def pane_states(t):
    """list of (key, x, y, w, h, vx, vy, land_t, entry_dir)."""
    out = []
    S = trip_scale(t)
    def sc(x, y, w, h):   # triptych slow push around frame centre
        return 540 + (x - 540) * S, 960 + (y - 960) * S, w * S, h * S
    if t >= TA0:
        k, dk = slide(t, TA0)
        nw = lerp(480, TRIP_W, eout((t - (W_FEEL - .03)) / .34))
        x = lerp(-560, SLOTS[0], k)
        out.append(('food',) + sc(x, TRIP_Y, nw, TRIP_H) + (dk * 596, 0., TA0 + SLIDE))
    if t >= TB0:   # FEEL rises from below into the centre slot
        k, dk = slide(t, TB0)
        y = lerp(H + 60, TRIP_Y, k)
        out.append(('service',) + sc(SLOTS[1], y, TRIP_W, TRIP_H) + (0., dk * (TRIP_Y - H - 60), TB0 + SLIDE))
    if t >= TC0:   # SEE closes in from the right, over him
        k, dk = slide(t, TC0)
        x = lerp(W + 40, SLOTS[2], k)
        out.append(('skill',) + sc(x, TRIP_Y, TRIP_W, TRIP_H) + (dk * (SLOTS[2] - W - 40), 0., TC0 + SLIDE))
    return out


LAB_OUT = (25.17, 25.30)       # the sense labels dissolve as s06 cracks the triptych (gone before "THEY" pops)


def label_alpha(t):
    return 1 - smooth((t - LAB_OUT[0]) / (LAB_OUT[1] - LAB_OUT[0]))


def draw_panes(fr, t, states=None, sweep_t=None, lab_a=None):
    blur = frosted(fr)
    lab_a = label_alpha(t) if lab_a is None else lab_a
    sub_on = dict(food=W_YOURFOOD, service=W_YOURSERV, skill=W_YOURSKILL)
    for key, x, y, w, h, vx, vy, land in (states if states is not None else pane_states(t)):
        lt = t - land
        # specular: one sweep right after landing, then a slow idle drift; one unified sweep when the triptych locks
        pos = clamp((lt + .1) / .7)
        amp = .9 * math.sin(math.pi * pos) if lt < .6 else 0
        if sweep_t is not None and t >= sweep_t:
            p2 = clamp((t - sweep_t) / .8); u_off = (x - 36) / 1100
            pos = clamp(p2 * 1.4 - u_off * .4); amp = max(amp, .8 * math.sin(math.pi * pos))
        if amp < .02: pos, amp = (.5 + .5 * math.sin(t * .9 + x * .01)) * .6 + .2, .16
        fl = .6 * clamp(1 - (lt + .02) / .16) if lt > -.02 else 0
        par = (-vx * 2.2 + 18 * math.sin(t * .7 + x * .02), -vy * .6 + 14 * math.sin(t * .5))
        draw_pane(fr, blur, key, x, y, w, h, t, vx, vy, land, label_k=(t - (land - SLIDE + .1)) / .3,
                  sub_k=(t - sub_on[key]) / .16, spec=(pos, amp), flash=fl, par=par, lab_a=lab_a)


# ---------------------------------------------------------------- warm light (work / amazing)
GOLD, VIOLET = np.array([255, 207, 138], np.float32), np.array([154, 77, 255], np.float32)


def film_of(ctx):
    """the engine's Film (to read the keyed avatar frame for a rim light that hugs his silhouette)."""
    for c in (ctx.compose.__closure__ or ()):
        v = c.cell_contents
        if hasattr(v, 'av') and hasattr(v.av, 'frame'): return v
    return None


def rim_light(ctx, t, amt):
    """warm back-light: a THIN (~3 px) bright edge that catches only the top-facing silhouette of his crown and the
    tops of his shoulders (light from behind/above) — no temples, no ears. world-space RGBA for the 'front' layer."""
    F = film_of(ctx)
    if F is None or amt <= .01: return None
    RH = 1190                                                              # nothing is lit below the shoulders
    A8 = np.asarray(F.av.frame(t).getchannel('A'))[:RH]
    a = A8.astype(np.float32) / 255
    band = a.copy(); band[3:] -= a[:-3]; np.clip(band, 0, 1, out=band)     # silhouette minus itself pushed down 3 px
    band *= rim_rows()[:RH]
    band = np.asarray(Image.fromarray((np.clip(band * 1.6, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.9)), np.float32)
    al = np.minimum(band * amt * .95, A8)
    im = Image.new('RGBA', (W, RH), (255, 236, 205, 0)); im.putalpha(Image.fromarray(al.astype(np.uint8))); return im


def rim_rows():
    def mk():
        yy = np.arange(H, dtype=np.float32)[:, None]
        crown = np.clip((600 - yy) / 70, 0, 1)                             # crown only (fades out above the temples)
        shoulders = np.clip((yy - 860) / 60, 0, 1) * np.clip((1180 - yy) / 120, 0, 1) * .55
        return crown + shoulders
    return E.cached('s05_rimrows', mk)


def halo_behind():
    """soft warm glow + anamorphic streak (gold core -> violet tails) that sits BEHIND him (world space)."""
    def mk():
        S = 4; w, h = 1600 // S, 1300 // S
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) * S
        cx, cy = 800, 560
        r = np.sqrt(((xx - cx) / 430) ** 2 + ((yy - cy) / 400) ** 2)
        glow = np.exp(-r ** 2 * 2.6) * .9 + np.exp(-r ** 2 * .9) * .18
        ax = np.abs(xx - cx) / 800
        streak = np.exp(-((yy - cy) / 7) ** 2) * np.exp(-ax ** 2 * 1.6) + np.exp(-((yy - cy) / 40) ** 2) * np.exp(-ax ** 2 * 3) * .4
        k = np.clip(ax * 1.7, 0, 1)[..., None]
        col_s = np.array([255, 244, 220], np.float32) * np.clip(1 - k * 3, 0, 1) + GOLD * (1 - k) * np.clip(k * 3, 0, 1) + VIOLET * k
        rr = np.clip(r * .8, 0, 1)[..., None]; col_g = np.array([255, 236, 200], np.float32) * (1 - rr) + GOLD * rr * .6 + VIOLET * rr * .4
        a = np.clip(glow + streak, 0, 1)
        col = (col_g * glow[..., None] + col_s * streak[..., None]) / np.maximum(glow + streak, 1e-4)[..., None]
        im = np.dstack([col, a * 255]).clip(0, 255).astype(np.uint8)
        return Image.fromarray(im, 'RGBA').resize((1600, 1300), Image.BICUBIC)
    return E.cached('s05_halo', mk)


def bokeh_disc(d, warm):
    """out-of-focus highlight: flat disc with a slightly brighter rim, softness by size."""
    d = max(8, int(d) // 2 * 2)
    def mk():
        S = 3; n = d * S + 8 * S; im = Image.new('L', (n, n)); dr = ImageDraw.Draw(im); c = n / 2; r = d * S / 2
        dr.ellipse((c - r, c - r, c + r, c + r), fill=150)
        dr.ellipse((c - r, c - r, c + r, c + r), outline=255, width=max(2, int(r * .12)))
        im = im.filter(ImageFilter.GaussianBlur(S * (1 + d * .05))).resize((n // S, n // S), Image.LANCZOS)
        col = tuple(int(v) for v in (GOLD * warm + VIOLET * (1 - warm) * 1.0 + np.array([0, 0, 0]) ))
        out = Image.new('RGBA', im.size, col + (0,)); out.putalpha(im); return out
    return E.cached(('s05_bk', d, round(warm, 1)), mk)


def bokeh_field():
    def mk():
        rng = np.random.default_rng(7); out = []
        for i in range(22):
            depth = rng.uniform(0, 1)                                 # 0 far .. 1 near
            front = depth > .82
            if front:   # near discs only at the frame edges, never over his face
                x = rng.choice([rng.uniform(-40, 170), rng.uniform(910, 1120)])
            else:
                x = rng.uniform(40, 1040)
            out.append(dict(x=x, y=rng.uniform(180, 1500), d=14 + depth * 60 + (50 if front else 0), a=.4 + .45 * (1 - depth) - (.1 if front else 0),
                            v=30 + depth * 90, warm=round(float(rng.uniform(.3, 1)), 1), ph=rng.uniform(0, 6.28), front=front))
        return out
    return E.cached('s05_bkf', mk)


# ---------------------------------------------------------------- screen glass (online)
# A whole pane of glass (a phone / monitor screen seen edge-on to us) slides in from the right on "online" and holds
# over the full frame: rounded bevel with thickness (refracted, prism-split rim), cool tint + haze, frosted margins,
# a slight lens magnification of him, drifting room reflections and a landing glint. Screen space, so the TL13 cut
# happens BEHIND the glass. On TASTE the first sense pane shoves it off to the right.
SG_M, SG_R, SG_BEV = 30, 74, 24                 # inset from the frame edge, corner radius, bevel thickness


def _sg_rr(inset, r, blur=0, val=255, S=2):
    m = Image.new('L', (W // S, H // S))
    ImageDraw.Draw(m).rounded_rectangle((inset / S, inset / S, (W - inset) / S - 1, (H - inset) / S - 1), r / S, fill=val)
    m = m.resize((W, H), Image.BILINEAR)
    return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m


def sg_masks():
    """pane mask, bevel band, frosted-margin falloff, outer contact shadow (all L, pane resting at offset 0)."""
    def mk():
        pane = _sg_rr(SG_M, SG_R, S=1)
        inner = _sg_rr(SG_M + SG_BEV, SG_R - SG_BEV + 6, blur=1.2, S=1)
        band = ImageChops.subtract(pane, inner)
        deep = _sg_rr(SG_M + 120, SG_R + 40, blur=55)
        frost = Image.fromarray((np.clip(np.asarray(pane, np.float32) - np.asarray(deep, np.float32), 0, 255) * .8).astype(np.uint8))
        sh = _sg_rr(SG_M - 6, SG_R + 6, blur=16)
        shadow = Image.fromarray((np.clip(np.asarray(sh, np.float32) - np.asarray(pane, np.float32), 0, 255) * .75).astype(np.uint8))
        return pane, band, frost, shadow
    return E.cached('s05_sgm', mk)


def sg_art():
    """static overlay: cool fill, top-left sheen, lit bevel (bright outer rim + dark inner step + inner glint), corner glints."""
    def mk():
        pane, band, frost, _ = sg_masks()
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        P = np.asarray(pane, np.float32) / 255
        u = (xx / W * .55 + yy / H * .45)                                   # 0 top-left .. 1 bottom-right
        sheen = (np.clip(1 - u * 1.5, 0, 1) ** 2 * .16 + .035) * P          # frosted sheen, strongest top-left
        col = np.zeros((H, W, 4), np.float32); col[..., :3] = (226, 236, 255); col[..., 3] = sheen * 255
        out = Image.fromarray(col.astype(np.uint8), 'RGBA')
        lit = np.clip(1.05 - u * 1.1, .28, 1)                               # light from the top-left
        def ring(inset, r, width, alpha, rgb, blur):
            m = Image.new('L', (W, H)); ImageDraw.Draw(m).rounded_rectangle((inset, inset, W - inset - 1, H - inset - 1), r, outline=255, width=width)
            if blur: m = m.filter(ImageFilter.GaussianBlur(blur))
            a = np.asarray(m, np.float32) * alpha * (lit if rgb[0] > 128 else (1.25 - lit))
            L = Image.new('RGBA', (W, H), rgb + (0,)); L.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))); return L
        out.alpha_composite(ring(SG_M + 1, SG_R, 9, .30, (235, 242, 255), 4))           # soft bloom of the rim
        out.alpha_composite(ring(SG_M + 1, SG_R, 3, .95, (255, 255, 255), .7))          # outer specular rim
        out.alpha_composite(ring(SG_M + 5, SG_R - 4, 2, .55, (120, 210, 255), .8))      # cyan prism fringe
        out.alpha_composite(ring(SG_M + SG_BEV - 2, SG_R - SG_BEV + 2, 3, .55, (6, 8, 22), 1.2))   # inner step (shadow side)
        out.alpha_composite(ring(SG_M + SG_BEV + 1, SG_R - SG_BEV - 1, 2, .45, (255, 236, 250), .8))   # inner glint
        # corner catch-lights (top-left strong, bottom-right faint)
        g = Image.new('L', (W, H)); d = ImageDraw.Draw(g)
        d.arc((SG_M, SG_M, SG_M + 2 * SG_R, SG_M + 2 * SG_R), 190, 260, fill=255, width=5)
        d.arc((W - SG_M - 2 * SG_R, H - SG_M - 2 * SG_R, W - SG_M, H - SG_M), 10, 80, fill=120, width=4)
        gl = Image.new('RGBA', (W, H), (255, 255, 255, 0)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(3))); out.alpha_composite(gl)
        return out
    return E.cached('s05_sga', mk)


def sg_streaks():
    """room reflections: two soft diagonal bands + a crisp thin one (RGB, additive), wider than the frame to drift."""
    def mk():
        S = 4; ww = W + 1400
        yy, xx = np.mgrid[0:H // S, 0:ww // S].astype(np.float32) * S
        u = xx * .82 + yy * .42
        a = (np.exp(-((u - 1150) / 150) ** 2) * 21 + np.exp(-((u - 1370) / 26) ** 2) * 26 +
             np.exp(-((u - 1440) / 9) ** 2) * 22 + np.exp(-((u - 2350) / 220) ** 2) * 16)
        a = a * (.75 + .25 * np.cos(yy / H * 3.1))
        rgb = a[..., None] * np.array([.86, .92, 1.0], np.float32)
        return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((ww, H), Image.BILINEAR)
    return E.cached('s05_sgs', mk)


def _solid(rgb):
    return E.cached(('s05_solid', rgb), lambda: Image.new('RGB', (W, H), rgb))


def _shift(img, off):
    if off == 0: return img
    out = Image.new(img.mode, img.size, 0); out.paste(img, (off, 0)); return out


def _lens(fr, s, cx, cy, ca):
    """frame magnified by s around (cx, cy) with a chromatic split of ca px (R out, B in)."""
    cx, cy = clamp(cx, 0, W), clamp(cy, 0, H)
    bw, bh = W / s, H / s; box = (cx - bw * cx / W, cy - bh * cy / H)
    im = fr.resize((W, H), Image.BILINEAR, box=(box[0], box[1], box[0] + bw, box[1] + bh))
    if ca:
        r, g, b = im.split(); im = Image.merge('RGB', (ImageChops.offset(r, ca, 0), g, ImageChops.offset(b, -ca, 0)))
    return im


def screen_glass(fr, off, vel, t, glint=None):
    """composite the screen pane at horizontal offset `off` (0 = resting over the full frame). vel in px/frame."""
    off = int(round(off))
    if off >= W - SG_M: return fr
    pane, band, frost, shadow = sg_masks()
    mb = min(90., abs(vel) * .35)
    if mb > 6:   # horizontal motion blur of the glass body / frost / bevel masks while it travels (soft leading edge)
        def smear(m, k=max(1, int(W / mb))): return m.resize((k, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        pane, band, frost = smear(pane), smear(band), smear(frost)
    rgb = fr.convert('RGB'); cx = off + W / 2
    # body: slight magnification (thick glass), faint chroma, cool tint, haze lift, frosted margins
    body = _lens(rgb, 1.022, cx, 900, 0)
    body = ImageChops.add(ImageChops.multiply(body, _solid((228, 238, 255))), _solid((5, 7, 16)))
    fb = body.resize((W // 4, H // 4), Image.BOX).filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    bev = fb.point(lambda v: min(255, int(v * 1.25 + 30)))             # bevel: thick frosted edge catching light
    fb = ImageChops.add(fb, _solid((10, 12, 20)))
    body = Image.composite(fb, body, _shift(frost, off))
    so = int(380 + 160 * math.sin(t * .7)) + 700 - int(off * .35)        # reflections drift (and lag the moving pane)
    so = max(0, min(sg_streaks().width - W, so))
    body = ImageChops.add(body, sg_streaks().crop((so, 0, so + W, H)))
    if glint is not None and glint[1] > .01:                            # landing glint: one bright diagonal sweep
        a = specular(W, H, glint[0], glint[1])
        body.paste(_solid((255, 252, 246)), (0, 0), a.point(lambda v: int(v * .55)))
    body = Image.composite(bev, body, _shift(band, off))
    out = fr.convert('RGBA')
    out.paste((0, 0, 0, 255), (0, 0), _shift(shadow, off))
    out.paste(body, (0, 0), _shift(pane, off))
    art = sg_art()
    sm = abs(vel)
    if sm > 6:   # motion smear on the rim / sheen while it travels
        k = min(14., sm / 7)
        art = art.resize((int(W / k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    if off: art = _shift(art, off)
    out.alpha_composite(art)
    return out


def _sg_push(t):
    """where the TASTE pane's right edge pushes the screen pane's left rim (offset units)."""
    tk, _ = slide(t, TA0); return lerp(-560, SLOTS[0], tk) + 480 + 26 - SG_M


def sg_contact():
    """(time, velocity px/s) at which the incoming TASTE pane reaches the screen pane's left rim."""
    def mk():
        a, b = TA0, TA0 + SLIDE
        for _ in range(40):
            m = (a + b) / 2
            if _sg_push(m) < 0: a = m
            else: b = m
        return b, (_sg_push(b + .004) - _sg_push(b - .004)) / .008
    return E.cached('s05_sgc', mk)


SG_KICK, SG_BOUNCE = 16000., 1.3                  # struck screen: leaves faster than the striker, keeps accelerating


def sg_offset(t):
    """pane offset: flies in from the right on "online" (expo, crosses his face in ~2 frames, tiny settle) and is
    STRUCK by the TASTE pane: from the moment of contact it carries the pane's speed and keeps accelerating
    (ballistic, monotonic), so it clears his face in ~4 frames and never stalls on it while TASTE settles."""
    if t < TA0:
        u = (t - W_ONLINE + .05) / .5
        if u <= 0: return W + 40.
        k = expo(u) + .012 * math.sin(clamp(u) * math.pi * 1.0) * (1 - clamp(u))
        return lerp(W + 40, 0, k)
    tc, v0 = sg_contact()
    if t < tc: return 0.
    d = t - tc
    return max(_sg_push(t), SG_BOUNCE * v0 * d + .5 * SG_KICK * d * d)


TAPS = [(21.60, 300, 1010), (21.96, 850, 450)]      # "NO-body can" — fingers tap the screen; it doesn't reach him


def tap_ripple(fr, cx, cy, u):
    """a touch on the glass: a refractive ring (lens-displaced annulus) with a prism-tinted highlight."""
    D = .75
    if not 0 <= u < D: return fr
    k = u / D; r = 18 + 330 * eout(k); fade_ = (1 - k) ** 1.6
    R = int(r + 34); x0, y0 = int(cx - R), int(cy - R); box = (x0, y0, x0 + 2 * R, y0 + 2 * R)
    reg = fr.crop(box)
    lens = reg.resize((int(2 * R * 1.08), int(2 * R * 1.08)), Image.BILINEAR)
    o = (lens.width - 2 * R) // 2; lens = lens.crop((o, o, o + 2 * R, o + 2 * R))
    S = 2; m = Image.new('L', (2 * R * S, 2 * R * S)); d = ImageDraw.Draw(m); c = R * S
    w = max(6, int(26 * (1 - k * .5)))
    d.ellipse((c - r * S, c - r * S, c + r * S, c + r * S), outline=int(255 * fade_), width=w * S)
    m = m.resize((2 * R, 2 * R), Image.LANCZOS).filter(ImageFilter.GaussianBlur(4))
    out = fr.copy(); out.paste(lens, (x0, y0), m)
    hl = Image.new('L', (2 * R * S, 2 * R * S)); dh = ImageDraw.Draw(hl)
    dh.ellipse((c - r * S, c - r * S, c + r * S, c + r * S), outline=255, width=2 * S)
    r2 = r * .72
    if r2 > 10: dh.ellipse((c - r2 * S, c - r2 * S, c + r2 * S, c + r2 * S), outline=110, width=2 * S)
    hl = hl.resize((2 * R, 2 * R), Image.LANCZOS).filter(ImageFilter.GaussianBlur(.8))
    yy, xx = np.mgrid[0:2 * R, 0:2 * R].astype(np.float32) - R
    lit = np.clip(.15 + .85 * (-(xx * .45 + yy * .9) / np.maximum(np.hypot(xx, yy), 1)), 0, 1)   # lit from the top-left
    hla = np.asarray(hl, np.float32) * fade_
    lay = np.zeros((2 * R, 2 * R, 4), np.float32)
    lay[..., :3] = (240, 245, 255); lay[..., 3] = hla * lit * .9
    dk = np.zeros_like(lay); dk[..., 3] = np.roll(hla, -3, 0) * (1 - lit) * .45                   # shadowed side
    sh = np.roll(hla, 3, 0) * .45 * lit
    cyan = np.zeros_like(lay); cyan[..., :3] = (90, 200, 255); cyan[..., 3] = sh
    for L_ in (dk, cyan, lay):
        E._paste(out, dict(img=Image.fromarray(np.clip(L_, 0, 255).astype(np.uint8), 'RGBA'), xy=(x0, y0), glass=0))
    if u < .14:   # the press itself
        p = 1 - u / .14; dot = Image.new('L', (80, 80)); ImageDraw.Draw(dot).ellipse((22, 22, 58, 58), fill=int(150 * p))
        dl = Image.new('RGBA', (80, 80), (230, 238, 255, 0)); dl.putalpha(dot.filter(ImageFilter.GaussianBlur(8)))
        E._paste(out, dict(img=dl, xy=(int(cx - 40), int(cy - 40)), glass=0))
    return out


def plate_feather(ctx, ax, dim):
    """hide the plate's left border when the avatar is shifted right: the studio itself, feathered over the cut."""
    def mk():
        st = E.studio(); w = 110
        crop_al = np.ones((H, w), np.float32)
        crop_al *= np.clip(1 - (np.arange(w) - 8) / (w - 8), 0, 1)[None, :] ** 1.3
        return crop_al
    al = E.cached('s05_pf', mk)
    x0 = int(round(ax)) - 8
    if x0 < 0: return
    piece = E.studio().crop((x0, 0, x0 + al.shape[1], H))
    if dim > .01: piece = Image.blend(piece, Image.new('RGB', piece.size, (0, 0, 0)), dim)
    piece = piece.convert('RGBA'); piece.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    ctx.add('front', piece, x0, 0, center=False)


# ================================================================ draw
SEE_OFF = .35                                              # screen glass slides off as the TASTE pane arrives


def ax_for(t):
    """avatar shift (world px, s=1) that keeps his face in the gap to the right of the TASTE pane (TL13)."""
    k, _ = slide(t, TA0); return 140 * clamp((k - .2) / .8) if t >= TA0 else 0.


GAP_CX = (SLOTS[1] + TRIP_W + W) / 2 + 2      # centre of the free column right of the FEEL pane (≈ 893)
HEAD_WX, HEAD_WY = 520., 690.                 # his face centre in the plate (s = 1)


def gap_framing(s, z, t0, dur):
    """FEEL / SEE framings: he is scaled to sit INSIDE the free column with air on both sides (head ≈ 330·s·z px
    wide in a 370 px gap) and the camera breathes in on his face. returns (avatar dict, cam dict)."""
    ax = GAP_CX - 540 - (HEAD_WX - 540) * s
    fwx, fwy = 540 + ax + (HEAD_WX - 540) * s, H - (H - HEAD_WY) * s
    zz = lerp(z, z + .02, smooth((t0) / dur))
    return dict(s=s, x=ax), cam_for_face(zz, GAP_CX, fwy, fwx, fwy)


def draw(ctx, lt, t):
    _draw(ctx, lt, t); voice_captions(ctx, t)


def _draw(ctx, lt, t):
    P = ctx.post
    # ------------------------------------------------ TL10 "Here's the problem."
    if t < T11:
        base = cam_for_face(lerp(1.28, 1.36, smooth((t - T10) / .8)), 540, 760)
        if t >= W_PROBLEM - .02:
            k = expo((t - W_PROBLEM + .02) / .16)
            face = cam_for_face(lerp(2.25, 2.4, smooth((t - W_PROBLEM) / .5)), 540, 640)
            cam = {kk: lerp(base[kk], face[kk], k) for kk in base}
            u = t - W_PROBLEM
            sh = 18 * math.exp(-max(0, u) * 14)
            cam['dx'] += sh * math.sin(u * 95); cam['dy'] += sh * .6 * math.cos(u * 77)
            P['zoom_blur'] = 2.0 if 0 <= u < .04 else 0
            # light, not fog: an exposure punch that keeps the blacks, plus a whisper of violet
            e = clamp(1 - u / .16) ** 2 if u >= 0 else 0
            P['bright'] = 1 + .85 * e; P['flash'] = .07 * e; P['flash_col'] = (200, 180, 255)
            P['rgb'] = 10 * clamp(1 - u / .16)
            P['vignette'] = .45
        else:
            cam = base
        ctx.cam = cam
        ctx.bg_dim = .15
        if t >= W_PROBLEM - .02: ctx.captions = False
        if t >= W_PROBLEM + .035:  # own type: PROBLEM slams one frame after the smeared hit frame (stays crisp)
            u = t - W_PROBLEM - .035
            ctx.add('screen', E.word_img("HERE'S THE", 84, 'white')[0], 540, 1352 - 30 * eout(u / .2))
            im = E.word_img('PROBLEM.', 150, 'grad')[0]
            sc = 1.5 - .5 * back(u / .18, 1.6)
            im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
            ctx.add('screen', im, 540, 1470, alpha=clamp(u / .04))
        return

    # ------------------------------------------------ TL11 "Your work might be amazing."
    if t < T12:
        u = (t - T11) / (T12 - T11)
        ctx.cam = cam_for_face(lerp(1.06, 1.16, smooth(u)), 540, 700)
        pre = .42 * smooth((t - W_WORK) / .7)                              # "work": the light starts to come up
        g = smooth(clamp((t - W_AMAZING + .06) / .45))
        g = max(pre, g * (1 + .05 * math.sin((t - W_AMAZING) * 5)))
        ctx.bg_dim = .14 - .1 * g
        if g > .005:
            ctx.add("behind", halo_behind(), 520, 760, alpha=clamp(g))
            for b in bokeh_field():
                life = clamp((t - W_WORK - b['ph'] * .05) / .4)
                y = b['y'] - b['v'] * (t - W_WORK) - 8 * math.sin(t * 1.3 + b['ph'])
                x = b['x'] + 10 * math.sin(t * .9 + b['ph'] * 2)
                al = b['a'] * g ** .7 * life * (.8 + .2 * math.sin(t * 3 + b['ph']))
                ctx.add('front' if b['front'] else 'behind', bokeh_disc(b['d'], b['warm']), x, y, alpha=clamp(al))
            rim = rim_light(ctx, t, g)
            if rim is not None: ctx.add('front', rim, 0, 0, center=False)
            ctx.avatar['bright'] = 1 + .03 * g
        def wrap(fr, g=g):
            if g <= .005: return fr
            return graded(fr, 1., 1., (1 + .05 * g, 1 + .015 * g, 1 - .04 * g))       # warm tint via a per-channel LUT
        ctx.wrap = wrap
        P['sat'] = 1 + .1 * g
        return

    # ------------------------------------------------ TL12 "But online," + TL13 "nobody can" (behind the screen)
    cold = dict(sat=.6, br=.92, tint=(.92, .98, 1.1))
    if t < TA0 + SEE_OFF:
        if t < T13:
            u = (t - T12) / (T13 - T12)
            ctx.cam = cam_for_face(lerp(1.3, 1.36, smooth(u)), 470, 700)
            ctx.bg_dim = .18
            drain = clamp((t - T12) / .25)
        else:   # cut wider: he is stuck behind the glass; on TASTE the first pane shoves the screen away
            ctx.cam = cam_for_face(lerp(1.16, 1.19, smooth((t - T13) / 1.6)), 770, 690)
            ax = ax_for(t)
            if ax > .5: ctx.avatar['x'] = ax; plate_feather(ctx, ax, .2)
            ctx.bg_dim = .2; drain = 1
        edge = sg_offset(t); vel = sg_offset(t) - sg_offset(t - 1 / 30); on = edge < W - SG_M
        gl = (t - W_ONLINE - .42) / .75                                   # glint sweeps the pane once it has landed
        glint = (clamp(gl), .85 * math.sin(math.pi * clamp(gl))) if 0 < gl < 1 else None
        sat = lerp(1.0, cold['sat'], drain); br = lerp(1, cold['br'], drain)
        tint = tuple(lerp(1, c, drain) for c in cold['tint'])
        def wrap(fr):
            fr = graded(fr, sat, br, tint).convert('RGBA')
            if on: fr = screen_glass(fr, edge, vel, t, glint)
            if t >= T13 and t < TA0:
                for tt, tx, ty in TAPS: fr = tap_ripple(fr, tx, ty, t - tt)
            if t >= TA0: draw_panes(fr, t, sweep_t=LOCK - .05)
            return fr
        ctx.wrap = wrap
        if t >= W_TASTE - .03: ctx.captions = False
        P['vignette'] = .38
        return

    # ------------------------------------------------ TL13-15 GLASS LAYERS
    if t < T14:      # "nobody can taste your food" — he sits right; the first pane takes the left
        ctx.cam = cam_for_face(lerp(1.16, 1.2, smooth((t - T13) / 1.6)), 770, 690)
        ax = ax_for(t); ctx.avatar['x'] = ax; plate_feather(ctx, ax, .2)
    else:            # "feel your service" / "or see your skill" — cut: he steps back into the free third column
        A, ctx.cam = gap_framing(.84, 1.0, t - T14, 1.1) if t < T15 else gap_framing(.92, 1.0, t - T15, .6)
        ctx.avatar.update(A); plate_feather(ctx, 540 + A['x'] - W * A['s'] / 2, .2)
    ctx.bg_dim = .2
    ctx.captions = False                                   # the pane labels carry the words from here
    def wrap(fr):
        fr = graded(fr, cold['sat'], cold['br'], cold['tint']).convert('RGBA')
        draw_panes(fr, t, sweep_t=LOCK - .05)
        return fr
    ctx.wrap = wrap
    P['vignette'] = .4
