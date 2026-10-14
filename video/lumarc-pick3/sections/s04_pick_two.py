"""s04 — PICK TWO (12.20–19.28): the body opens with the three "pick two" jokes, then the old rule shatters on "AI".

  Q = question round: the glass TRIANGLE (kit) beside him, the picked pair lights ON the spoken words, the beam draws
      on "and", the third node gets the red ✗; captions in the free column under the triangle (never over his face).
  A = answer gag: a full framing change on every JUMP, readable muted in a split second.

 12.20 Q1 "FAST and CHEAP?" — BODY FRAME 1 (works after any hook): flash cut, the camera settles (1.24 -> 1.12), the dim
       triangle pops in beside him.  12.29 FAST lights (overdrive + pop) · 12.54 "and": beam FAST -> CHEAP ·
       12.66 CHEAP lights, the beam lands · 12.80 ✗ GOOD.
 13.00 A1 "It looks CHEAP." — SMASH CUT (record scratch): the ad itself turns cheap — lime/magenta sunburst, the 7-font
       bakery flyer (its "50% OFF" covered by a "WOW!!!" burst, cropped above its phone number), a stretched pixelated
       "YOUR LOGO HERE", bouncing clip-art, JPEG crunch, and HIS photo slapped over the clip-art chef as a crooked
       white-bordered sticker.  The caption is rainbow WordArt: "IT LOOKS" PowerPoint-spins in on IT (13.08), "CHEAP."
       bounces in on its word (13.42, buzzer) over a starburst.
 13.70 Q2 "GOOD and FAST?" — hard cut back to the clean LUMARC world, tight on his face.  13.84 GOOD · 13.95 beam
       GOOD -> FAST · 14.06 FAST ("good'n FAAST?") · 14.24 ✗ CHEAP.
 14.60 A2 "It costs A FORTUNE." — an agency INVOICE scroll hangs beside him (BIG AGENCY CO., "BILL TO: YOU"); 14.72 its
       bottom roller DROPS and unrolls past the bottom of the frame (line items, every amount "$$$$", no digits);
       FORTUNE: a red "$$$$$$" rubber stamp slams from the f (15.23) and lands at 15.30 (stamp + ka-ching), then the
       endless paper scrolls up (the stamp is inked on it and rides with it).
 15.80 Q3 "GOOD and CHEAP?" — mirrored: he moves left, the triangle right, dutch angle.  15.90 GOOD · 16.00 beam
       GOOD -> CHEAP · 16.14 CHEAP · 16.30 ✗ FAST.
 16.47 A3 "Get in LINE." — cut to a real street queue; the deli LED "NOW SERVING:" drops in, 16.56 GET: it flips to
       "SOMEONE ELSE" (deli bell; the LED line blinks on/off/on frame by frame) · 16.77 LINE: a "YOU" tag + hourglass
       pops at the back of the line, arrow pointing off-frame (you're even further back); clock ticks, crickets.
 17.37 THE RULE "That rule was written before AI." — an ancient stone tablet (THE RULE / FAST CHEAP GOOD / PICK TWO.
       carved; the labels + bed are cut from the kit's own render, the kit's glass triangle sits in it, aged sepia and
       dusty) drops into a dark vault and lands on THAT (stone thud, dust, shake) · 17.58 RULE: a warm glint runs over
       "THE RULE" · 18.04 WRITTEN: a chisel carves "PICK TWO." letter by letter (chips fly) · 18.36 BEFORE: the
       tablet trembles, a hairline crack glows violet (riser) · 18.63 AI: IMPACT — flash, the age drains off the glass,
       the triangle CRACKS (kit crack) while the stone fractures (glasskit Fracture) with violet light racing through
       the cracks · 18.80 the rule SHATTERS toward the lens (kit shatter + glasskit 3-D stone shards + glitter + dust)
       (the shards are cut to the tablet's silhouette, so no void corners fly) · 19.12–19.28 one beat of stillness:
       lights almost out, a few motes (the 19.267 frame already shows seg 20's pose -> the avatar is hidden here).

Word onsets measured on src/tight16k.raw (10 ms band envelopes 80-1000 Hz / >3 kHz + spectrogram), see ON.
Captions: my own pages in the engine look on the measured onsets (the engine's estimates run up to .23 s late here).
Safe zone (checked with a label-extent probe over every Q frame): triangle labels Q1 x 74-618, Q2 77-633, Q3 423-954,
y 468-1018; the rule's camera push is anchored low (R_ZC) so the carved PICK TWO. never meets the caption (R_CAP).
"""
import math, os, io
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import engine as E
from sections import _tri as TRI
from sections import _shared as SH

START, END = E.span(13, 19)                     # 12.20 – 19.28
W, H, FPS = E.W, E.H, E.FPS
clamp = E.clamp

ON = dict(
    # seg 13 "Fast and cheap?"
    FAST1=12.29, AND1=12.54, CHEAP1=12.66, END13=12.97,
    # seg 14 "It looks cheap."
    IT14=13.08, LOOKS=13.15, CHEAP2=13.42, END14=13.69,
    # seg 15 "Good and fast?"   ("good'n FAAST?": the f-noise starts at 14.06)
    GOOD1=13.84, AND2=13.95, FAST2=14.06, END15=14.50,
    # seg 16 "It costs a fortune."
    IT16=14.72, COSTS=14.84, A16=15.16, FORTUNE=15.24, END16=15.71,
    # seg 17 "Good and cheap?"
    GOOD2=15.90, AND3=16.00, CHEAP3=16.14, END17=16.46,
    # seg 18 "Get in line."
    GET=16.56, IN=16.65, LINE=16.77, END18=17.13,
    # seg 19 "That rule was written before AI."   (AI = "eɪ" at 18.64, "aɪ" at 18.87)
    THAT=17.47, RULE=17.58, WAS=17.87, WRITTEN=18.04, BEFORE=18.36, AI=18.64, AI_I=18.87, END19=19.07,
)

# first frame of each beat (the avatar shows a segment's pose on the nearest 25 fps source frame: seg 15 / 18 / 19
# start one frame early, seg 20's pose already shows on 19.267 = my last frame)
J_Q1, J_A1, J_Q2, J_A2, J_Q3, J_A3, J_RULE, J_END = 366, 390, 411, 438, 474, 494, 521, 579
T_Q1, T_A1, T_Q2, T_A2, T_Q3, T_A3, T_RULE = (j / FPS for j in (J_Q1, J_A1, J_Q2, J_A2, J_Q3, J_A3, J_RULE))
T_IMPACT = 559 / FPS                            # 18.633 "AI"
T_SHAT = 564 / FPS                              # 18.800 the rule shatters
T_STILL = 19.12                                 # the beat of stillness
R_CAP = 1205                                    # rule captions (glyphs ~1165-1245, under the tablet's PICK TWO. <= ~1136)

def lerp(a, b, k): return a + (b - a) * k
def eo(x, p=3): x = clamp(x); return 1 - (1 - x) ** p
def ei(x, p=2): x = clamp(x); return x ** p
def sm(x): x = clamp(x); return x * x * (3 - 2 * x)
def bump(x): x = clamp(x); return math.sin(math.pi * x)
def dec(t, t0, tau): return math.exp(-(t - t0) / tau) if t >= t0 else 0.0
def backo(x, s=1.7): x = clamp(x) - 1; return 1 + x * x * ((s + 1) * x + s)
def hr(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def shake(t, t0, amp, tau=.18, f=19., seed=0):
    if t < t0: return 0.0, 0.0
    k = amp * math.exp(-(t - t0) / tau); u = t - t0
    return k * math.sin(2 * math.pi * f * u + seed), k * math.sin(2 * math.pi * f * 1.37 * u + 1.7 + seed)
def scaled(im, s):
    if abs(s - 1) < .004: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
def rotated(im, deg):
    return im if abs(deg) < .05 else im.rotate(deg, Image.BICUBIC, expand=True)
def ffont(path, size):
    return E.cached(('P_font', path, size), lambda: ImageFont.truetype(path, size))
FONTS = '/usr/share/fonts/truetype/'
F_SERIF_B = FONTS + 'crosextra/Caladea-Bold.ttf'
F_CHEAP = FONTS + 'dejavu/DejaVuSans-Bold.ttf'
F_CHEAP_I = FONTS + 'liberation/LiberationSerif-BoldItalic.ttf'
F_MONO = FONTS + 'dejavu/DejaVuSansMono-Bold.ttf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
def emoji(ch, size):
    def mk():
        try:
            f = ImageFont.truetype(EMOJI, 109)
            im = Image.new('RGBA', (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
            im = im.crop(im.getbbox()); return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
        except Exception:
            return Image.new('RGBA', (size, size), (0, 0, 0, 0))
    return E.cached(('P_emoji', ch, size), mk)

# ================================================================================================ captions
# own pages in the engine look (E.word_img pop-in), keyed on the measured onsets above; explicit lines + column so a
# caption never crosses his face (Q rounds: the left column under the triangle)
def _pages():
    P = []
    def page(lines, z, cx=540, cy=1170, base=92, maxw=900, plate=0.0):
        ws = [dict(text=tx, emph=em, t0=t0, line=li) for li, ln in enumerate(lines) for tx, em, t0 in ln]
        for k, w in enumerate(ws): w['t1'] = ws[k + 1]['t0'] if k + 1 < len(ws) else z - .12
        P.append(dict(words=ws, a=ws[0]['t0'] - .04, z=z, cx=cx, cy=cy, base=base, maxw=maxw, n=len(lines), plate=plate))
    QX, QY, QB, QW = 352, 1132, 86, 516
    page([[('FAST', 1, ON['FAST1']), ('AND', 0, ON['AND1'])], [('CHEAP?', 1, ON['CHEAP1'])]], T_A1 - .001, QX, QY, QB, QW)
    # seg 14: the cheap WordArt IS the caption (drawn by the gag)
    page([[('GOOD', 1, ON['GOOD1']), ('AND', 0, ON['AND2'])], [('FAST?', 1, ON['FAST2'])]], T_A2 - .001, QX, QY, QB, QW)
    page([[('IT', 0, ON['IT16']), ('COSTS', 0, ON['COSTS'])]], ON['A16'] - .02, 540, 1185, plate=1.0)
    page([[('A', 0, ON['A16']), ('FORTUNE.', 1, ON['FORTUNE'])]], T_Q3 - .001, 540, 1185, plate=1.0)
    page([[('GOOD', 1, ON['GOOD2']), ('AND', 0, ON['AND3'])], [('CHEAP?', 1, ON['CHEAP3'])]], T_A3 - .001, 690, QY, QB, 490)
    page([[('GET', 0, ON['GET']), ('IN', 0, ON['IN']), ('LINE.', 1, ON['LINE'])]], T_RULE - .001, 540, 1165)
    page([[('THAT', 0, ON['THAT']), ('RULE', 0, ON['RULE'])]], ON['WAS'] - .02, 540, R_CAP)
    page([[('WAS', 0, ON['WAS']), ('WRITTEN', 0, ON['WRITTEN'])]], ON['BEFORE'] - .02, 540, R_CAP)
    page([[('BEFORE', 1, ON['BEFORE']), ('AI.', 1, ON['AI'] - .01)]], T_STILL - .02, 540, R_CAP)
    return P
PAGES = _pages()

def _layout(p):
    """[(word, size, x, y)] for page p: words on their explicit lines, each line centred on p['cx'] (shrunk to maxw)."""
    def mk():
        base = p['base']; out = []; lh = base * 1.13; y0 = -(p['n'] - 1) * lh / 2
        for li in range(p['n']):
            ws = [w for w in p['words'] if w['line'] == li]
            def widths(k): return [font_w(w['text'], int(base * k * (1.2 if w['emph'] else 1.0))) for w in ws]
            k = 1.0; tot = sum(widths(1.0)) + base * .34 * (len(ws) - 1)
            if tot > p['maxw']: k = p['maxw'] / tot
            wd = widths(k); tot = sum(wd) + base * k * .34 * (len(ws) - 1); x = p['cx'] - tot / 2
            for w, ww in zip(ws, wd):
                out.append((w, int(base * k * (1.2 if w['emph'] else 1.0)), x + ww / 2, p['cy'] + y0 + li * lh)); x += ww + base * k * .34
        return out
    return E.cached(('P_lay', id(p)), mk)

def font_w(text, sz):
    l, t, r, b = E.font(sz).getbbox(text); return r - l

def plate_img(w, h):
    def mk():
        m = Image.new('L', (w + 160, h + 160)); ImageDraw.Draw(m).rounded_rectangle((80, 80, w + 80, h + 80), h // 2, fill=255)
        im = Image.new('RGBA', m.size, (8, 8, 14, 0)); im.putalpha(m.filter(ImageFilter.GaussianBlur(34)).point(lambda v: int(v * .62))); return im
    return E.cached(('P_plate', w, h), mk)

def captions(ctx, t, dy=0.0):
    for p in PAGES:
        if not (p['a'] <= t < p['z']): continue
        L = _layout(p)
        if p['plate']:      # soft dark plate behind captions that sit on busy, bright art (the invoice)
            xs = [x for w, sz, x, y in L]; k = clamp((t - p['a']) / .06) * clamp((p['z'] - t) / .06)
            pw = int(max(xs) - min(xs) + p['base'] * 3.2); ph = int(p['base'] * 1.6)
            ctx.add('screen', E.fade(plate_img(pw, ph), k * p['plate']), (max(xs) + min(xs)) / 2, p['cy'] + dy)
        for w, sz, cx, cy in L:
            if t < w['t0'] - .02: continue
            lt = t - w['t0'] + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if w['t0'] - .02 <= t < w['t1'] + .04: s *= 1.03
            img, _ = E.word_img(w['text'], sz, 'grad' if w['emph'] else 'white')
            if lt < .05: img = E.fade(img, lt / .05)
            if p['z'] - t < .06: img = E.fade(img, max(0, (p['z'] - t) / .06))
            ctx.add('screen', scaled(img, s), cx, cy + dy)

# ================================================================================================ shared looks
def bg_soft():
    """the studio plate, defocused + dimmed: the Q rounds' depth of field (the glass triangle pops, he stays sharp)."""
    def mk():
        im = E.studio().filter(ImageFilter.GaussianBlur(6))
        return Image.blend(im, Image.new('RGB', im.size, (8, 7, 14)), .30)
    return E.cached('P_bg_soft', mk)

# ================================================================================================ Q rounds
SZ, TX, TY = 590, 356, 742                      # the triangle box beside him (labels inside x 70-640 incl. pops)
QR = [
    dict(t0=T_Q1, t1=T_A1, pair=('fast', 'cheap'), w=(ON['FAST1'], ON['AND1'], ON['CHEAP1']), tx=12.80, yaw=-9., pitch=4., box=(SZ, TX, TY)),
    dict(t0=T_Q2, t1=T_A2, pair=('good', 'fast'), w=(ON['GOOD1'], ON['AND2'], ON['FAST2']), tx=14.24, yaw=8., pitch=-3., box=(SZ, TX, TY)),
    dict(t0=T_Q3, t1=T_A3, pair=('good', 'cheap'), w=(ON['GOOD2'], ON['AND3'], ON['CHEAP3']), tx=16.30, yaw=7., pitch=7., box=(566, 690, 740)),
]
NOTE = dict(fast='E6', cheap='C6', good='G6')

def q_state(t, q, k):
    a, b = q['pair']; ta, tand, tb = q['w']
    i, j = TRI.NODES.index(a), TRI.NODES.index(b); o = 3 - i - j
    lit = [0., 0., 0.]; pop = [1., 1., 1.]; x = [0., 0., 0.]; edge = [0., 0., 0.]; draw = [1., 1., 1.]
    for n, tn in ((i, ta), (j, tb)):
        if t >= tn - 1 / FPS:
            u = max(0.0, t - tn); lit[n] = 1 + .65 * math.exp(-u / .11) * min(1, (t - tn + 1 / FPS) * FPS)
            pop[n] = 1 + .24 * bump(u / .24)
    e, sgn = TRI.EDGE_OF[(a, b)]
    if t >= tand:
        d = eo((t - tand) / max(.06, tb - tand), 2.2); draw[e] = sgn * d; edge[e] = 1.0
    else:
        draw[e] = 0.0
    x[o] = clamp((t - q['tx']) / .18)
    lt = t - q['t0']; d = TRI.drift(t, .55)
    yaw = q['yaw'] * (1 - .35 * eo(lt / .8)) + d['yaw']; pitch = q['pitch'] + d['pitch']
    if k == 0:   # BODY frame 1: the triangle slams in (scale 1.35 -> 1)
        sc = 1 + .06 * (1 - eo(lt / .2, 3)); al = 1.0
    else:
        sc = 1 + .07 * (1 - eo(lt / .14, 3)); al = 1.0
    return TRI.state(lit=tuple(lit), pop=tuple(pop), x=tuple(x), edge=tuple(edge), draw=tuple(draw), flow=t * .9,
                     yaw=yaw, pitch=pitch, roll=d['roll'], scale=sc, alpha=al)

def q_round(ctx, t, k):
    q = QR[k]; lt = t - q['t0']
    ctx.bg_img = bg_soft(); ctx.avatar.update(x=265.)
    if k == 0:      # body frame 1: flash cut + the camera settles (snap-out 1.24 -> 1.12, then a slow push)
        z = 1.24 - .12 * eo(lt / .26, 3) + .04 * eo((lt - .26) / .55, 2)
        ctx.cam.update(z=z, x=600., y=800.)
        ctx.post['flash'] = .24 * dec(t, T_Q1, .045); ctx.post['flash_col'] = (214, 200, 255)
    elif k == 1:    # tight on his face (right), slow push
        ctx.avatar.update(x=330.)
        ctx.cam.update(z=1.40 + .06 * eo(lt / .9, 2), x=800., y=790.)
    else:           # mirrored: he moves to the LEFT, the triangle to the right, slight dutch angle (k == 2)
        ctx.avatar.update(x=-270., y=20.)
        ctx.cam.update(z=1.16 + .05 * eo(lt / .7, 2), x=470., y=850., rot=math.radians(2.2 - 1.0 * eo(lt / .7)))
    st = q_state(t, q, k)
    sz, tx, ty = q['box']
    ctx.wrap = lambda fr, st=st: TRI.paste(fr, st, sz, tx, ty, frost=9)
    captions(ctx, t)

def q_cues():
    C = []
    for k, q in enumerate(QR):
        a, b = q['pair']; ta, tand, tb = q['w']
        C += [(ta, 'ding', {'note': NOTE[a], 'gain': -9}), (ta, 'pop', {'gain': -15}),
              (tand, 'swoosh', {'gain': -13, 'pan': -.3}),
              (tb, 'ding', {'note': NOTE[b], 'gain': -9}), (tb + .01, 'shing', {'gain': -11}),
              (q['tx'], 'stamp', {'gain': -9}), (q['tx'] + .01, 'buzzer', {'dur': .22, 'gain': -17})]
    return C

# ================================================================================================ A1 — it looks CHEAP
RAINBOW = [(255, 40, 40), (255, 150, 0), (255, 235, 0), (40, 210, 60), (30, 140, 255), (170, 60, 255)]
def _rainbow(w, h, vertical=True):
    n = h if vertical else w; x = np.linspace(0, 1, n)[:, None] * (len(RAINBOW) - 1)
    c = np.array(RAINBOW, np.float32); i = np.clip(x.astype(int), 0, len(RAINBOW) - 2); f = x - i
    g = c[i[:, 0]] * (1 - f) + c[i[:, 0] + 1] * f
    a = np.repeat(g[:, None, :], w, 1) if vertical else np.repeat(g[None, :, :], h, 0)
    return Image.fromarray(a.astype(np.uint8), 'RGB')

def wordart(text, size, wave=.0, seed=0):
    """cheap 90s WordArt: rainbow fill, fat black outline, white outer outline, 3-D extrusion, wavy baseline."""
    def mk():
        f = ffont(F_CHEAP, size); sw = max(4, size // 13)
        l, tp, r, b = f.getbbox(text, stroke_width=sw); pad = size // 2 + 30
        w, h = r - l + 2 * pad, b - tp + 2 * pad
        def mask(stroke):
            m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((pad - l, pad - tp), text, font=f, fill=255, stroke_width=stroke, stroke_fill=255); return m
        fill, inner, outer = mask(0), mask(sw), mask(sw + max(4, size // 18))
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ext = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        for k in range(size // 9, 0, -1):          # chunky extrusion down-right
            col = (int(60 + 2 * k), int(20 + k), int(90 + 3 * k), 255)
            layer = Image.new('RGBA', (w, h), col); layer.putalpha(inner); ext.alpha_composite(layer, (k, k))
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sh.putalpha(outer.point(lambda v: int(v * .55)))
        im.alpha_composite(sh, (size // 7, size // 6))
        wh = Image.new('RGBA', (w, h), (255, 255, 255, 255)); wh.putalpha(outer); im.alpha_composite(wh)
        im.alpha_composite(ext)
        bk = Image.new('RGBA', (w, h), (10, 10, 10, 255)); bk.putalpha(inner); im.alpha_composite(bk)
        rb = _rainbow(w, h, vertical=True).convert('RGBA'); rb.putalpha(fill); im.alpha_composite(rb)
        hl = Image.new('RGBA', (w, h), (255, 255, 255, 0))      # cheesy glossy top highlight
        gm = np.zeros((h, w), np.float32); gm[: int(pad + (b - tp) * .45)] = .38
        hl.putalpha(Image.fromarray((np.asarray(fill, np.float32) * gm).astype(np.uint8))); im.alpha_composite(hl)
        if wave:      # wavy baseline: shift every column
            a = np.asarray(im); out = np.zeros_like(a); amp = size * wave
            for x in range(w):
                dy = int(round(amp * math.sin(x / w * 2 * math.pi * 1.1 + seed)))
                if dy >= 0: out[dy:, x] = a[:h - dy, x]
                else: out[:h + dy, x] = a[-dy:, x]
            im = Image.fromarray(out, 'RGBA')
        return im.crop(im.getbbox())
    return E.cached(('P_wordart', text, size, wave, seed), mk)

def starburst(r, col=(255, 230, 0), edge=(220, 20, 30), n=14, text=None, tcol=(220, 20, 30), tsize=60, rot=0):
    def mk():
        S = 2 * r + 20; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = []
        for i in range(2 * n):
            a = math.pi * i / n + rot; rr = r if i % 2 == 0 else r * .72
            pts.append((S / 2 + rr * math.cos(a), S / 2 + rr * math.sin(a)))
        d.polygon(pts, fill=edge); pts2 = [(S / 2 + (x - S / 2) * .86, S / 2 + (y - S / 2) * .86) for x, y in pts]
        d.polygon(pts2, fill=col)
        if text:
            f = ffont(F_CHEAP, tsize); l, tp, rr, b = f.getbbox(text, stroke_width=3)
            d.text((S / 2 - (l + rr) / 2, S / 2 - (tp + b) / 2), text, font=f, fill=tcol, stroke_width=3, stroke_fill=(255, 255, 255))
        return im
    return E.cached(('P_burst', r, col, edge, n, text, tcol, tsize, rot), mk)

def flyer_card():
    """the bakery flyer, cropped above its phone number, the '50% OFF' starburst covered by a 'WOW!!!' burst,
    white photo-print border + hard drop shadow."""
    def mk():
        f = Image.open(os.path.join(E.THERAPY_A, 'flyer.png')).convert('RGBA').crop((0, 0, 896, 836))
        wow = rotated(starburst(178, text='WOW!!!', tsize=70, rot=.1), 12)
        f.alpha_composite(wow, (int(196 - wow.width / 2), int(532 - wow.height / 2)))
        b = 16; card = Image.new('RGBA', (f.width + 2 * b, f.height + 2 * b), (255, 255, 255, 255)); card.alpha_composite(f, (b, b))
        return card
    return E.cached('P_flyer', mk)

def logo_here():
    """'YOUR LOGO HERE' template badge, rendered tiny then blown up nearest-neighbour + stretched (pixelated)."""
    def mk():
        im = Image.new('RGBA', (92, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, 91, 29), 6, fill=(30, 60, 200, 255), outline=(255, 255, 255, 255), width=2)
        f = ffont(F_CHEAP, 11); d.text((8, 2), 'YOUR LOGO', font=f, fill=(255, 255, 0, 255)); d.text((26, 15), 'HERE', font=f, fill=(255, 255, 255, 255))
        im = im.resize((92 * 4, 30 * 4), Image.NEAREST).resize((92 * 4 + 70, 30 * 3 - 6), Image.NEAREST)   # stretched
        return im
    return E.cached('P_logo_here', mk)

def cheap_bg():
    """lime -> yellow -> magenta flyer gradient (full frame)."""
    def mk():
        y = np.linspace(0, 1, H)[:, None]
        c0, c1, c2 = np.array([90, 230, 40]), np.array([250, 240, 60]), np.array([250, 40, 210])
        g = np.where(y < .5, c0 + (c1 - c0) * (y / .5), c1 + (c2 - c1) * ((y - .5) / .5))
        g = g.reshape(H, 1, 3).repeat(W, 1); return Image.fromarray(g.astype(np.uint8), 'RGB')
    return E.cached('P_cheap_bg', mk)

def sunburst_rays():
    def mk():
        S = 2400; im = Image.new('L', (S, S), 0); d = ImageDraw.Draw(im); n = 18
        for i in range(n):
            a0 = 2 * math.pi * i / n; a1 = a0 + math.pi / n
            d.polygon([(S / 2, S / 2), (S / 2 + S * math.cos(a0), S / 2 + S * math.sin(a0)), (S / 2 + S * math.cos(a1), S / 2 + S * math.sin(a1))], fill=255)
        return im
    return E.cached('P_rays', mk)

def _solid(col): return E.cached(('P_solid', col), lambda: Image.new('RGB', (W, H), col))
def avatar_rgba(ctx):
    """his keyed + lit frame at ctx.t as RGBA: the engine composes him over black and over white, alpha = difference."""
    cam = dict(z=1.0, x=540., y=960., dx=0., dy=0., rot=0.); keep = ctx.bg_img
    ctx.bg_img = _solid((0, 0, 0)); b = np.asarray(ctx.compose(cam=cam).convert('RGB'), np.float32)
    ctx.bg_img = _solid((255, 255, 255)); w = np.asarray(ctx.compose(cam=cam).convert('RGB'), np.float32)
    ctx.bg_img = keep
    a = np.clip(1 - (w - b).mean(2) / 255, 0, 1)
    rgb = np.clip(b / np.maximum(a[..., None], 1 / 255), 0, 255)
    return Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), 'RGBA')

def jpeg_crunch(im, q=12):
    b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=q); b.seek(0); return Image.open(b).convert('RGB')

def a1_cheap(ctx, t):
    lt = t - T_A1
    fr = cheap_bg().copy().convert('RGBA')
    # sunburst rays, rotating (linear = cheap)
    rays = sunburst_rays().rotate(lt * 38, Image.NEAREST, center=(1200, 1200))
    ray = Image.new('RGBA', (2400, 2400), (255, 255, 255, 0)); ray.putalpha(rays.point(lambda v: int(v * .22)))
    fr.alpha_composite(ray, (540 - 1200, 760 - 1200))
    # the flyer card, wobbling (cheap 'pulse' animation)
    card = flyer_card(); wob = 1.6 * math.sin(lt * 2 * math.pi * 2.2)
    cs = .98 + .02 * math.sin(lt * 2 * math.pi * 2.2)
    cr = rotated(scaled(card, cs * .86), -3.5 + wob)
    sh = Image.new('RGBA', cr.size, (0, 0, 0, 0)); sh.putalpha(cr.getchannel('A').point(lambda v: int(v * .55)))
    cx, cy = 540, 640
    fr.alpha_composite(sh, (int(cx - cr.width / 2 + 22), int(cy - cr.height / 2 + 26)))
    fr.alpha_composite(cr, (int(cx - cr.width / 2), int(cy - cr.height / 2)))
    # his photo slapped on as a crooked sticker (bottom right, face clear of every text)
    st = sticker(avatar_rgba(ctx))
    im = rotated(st, 7 + 1.5 * math.sin(lt * 2 * math.pi * 1.6))
    fr.alpha_composite(im, (int(842 - im.width / 2), int(770 - im.height / 2)))
    # stretched pixelated logo + clip-art (snappy, linear bounces)
    lg = rotated(logo_here(), 4); fr.alpha_composite(lg, (int(800 - lg.width / 2), int(318 - lg.height / 2 + 6 * abs(math.sin(lt * 9)))))
    for k, (ch, x, y, s0, ph) in enumerate((('✨', 110, 1010, 120, 0), ('\U0001F44D', 930, 1010, 130, 1.3), ('⭐', 120, 330, 96, 2.1),
                                            ('\U0001F389', 960, 600, 110, .6), ('✨', 980, 250, 90, 1.7))):
        e = emoji(ch, s0); bob = 14 * abs(math.sin(lt * 7 + ph)); ang = 12 * math.sin(lt * 5 + ph)
        e = rotated(e, ang); fr.alpha_composite(e, (int(x - e.width / 2), int(y - e.height / 2 - bob)))
    # cheesy lens flare
    fr = ImageChops.add(fr.convert('RGB'), flare().convert('RGB'))
    fr = fr.convert('RGBA')
    # WordArt caption: "IT LOOKS" PowerPoint spin-in on IT, "CHEAP." bounce-zoom on its word (burst behind both)
    k1 = clamp((t - (ON['IT14'] - .02)) / .22); k2 = t - (ON['CHEAP2'] - .02)
    if k2 > 0:
        b = starburst(205, col=(255, 240, 40), edge=(230, 30, 40), n=16)
        bi = rotated(scaled(b, max(.05, backo(k2 / .16, 2.6))), lt * 90)
        fr.alpha_composite(bi, (int(560 - bi.width / 2), int(1158 - bi.height / 2)))
    if k1 > 0:
        wa = wordart('IT LOOKS', 96, wave=.10, seed=.4)
        im = rotated(scaled(wa, .15 + .85 * k1), (1 - k1) * 340)
        fr.alpha_composite(im, (int(510 - im.width / 2), int(1030 - im.height / 2)))
    if k2 > 0:
        wa = wordart('CHEAP.', 150, wave=.06, seed=1.9)
        s = max(.05, backo(k2 / .14, 3.0)) * (1 + .05 * math.sin(k2 * 30) * math.exp(-k2 / .3))
        im = rotated(scaled(wa, s), -4)
        fr.alpha_composite(im, (int(540 - im.width / 2), int(1154 - im.height / 2)))
    # crude cheap camera: linear zoom, and the whole frame JPEG-crunched
    z = 1.0 + .05 * lt
    fr = E.zoom(fr.convert('RGB'), z, (540, 900))
    fr = jpeg_crunch(fr, 14)
    ctx.full = fr
    ctx.captions = False
    ctx.post.update(vignette=.0, grain=.6, sat=1.12)

STK_S = .40
def sticker(av):
    """keyed RGBA frame -> crooked head-and-shoulders cut-out sticker (white border, hard shadow), at STK_S scale."""
    a = av.getchannel('A'); bb = a.point(lambda v: 255 if v > 60 else 0).getbbox()
    if bb is None: return Image.new('RGBA', (10, 10))
    x0, y0, x1, y1 = bb; crop = av.crop((max(0, x0), max(0, y0 - 12), min(W, x1), 1290))
    crop = scaled(crop, STK_S)
    pad = 26; im = Image.new('RGBA', (crop.width + 2 * pad, crop.height + 2 * pad), (0, 0, 0, 0))
    am = Image.new('L', im.size); am.paste(crop.getchannel('A').point(lambda v: 255 if v > 90 else 0), (pad, pad))
    border = am.filter(ImageFilter.GaussianBlur(6)).point(lambda v: 255 if v > 14 else 0).filter(ImageFilter.GaussianBlur(.8))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    shd = Image.new('RGBA', im.size, (0, 0, 0, 0)); shd.putalpha(border.point(lambda v: int(v * .55)))
    out.alpha_composite(shd, (10, 12))
    wh = Image.new('RGBA', im.size, (255, 255, 255, 255)); wh.putalpha(border); out.alpha_composite(wh)
    out.alpha_composite(crop, (pad, pad))
    return out

def flare():
    def mk():
        im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
        cx, cy = 880, 240
        for k, (r, col) in enumerate(((180, (90, 80, 40)), (60, (160, 150, 120)), (34, (60, 90, 120)), (90, (50, 30, 70)), (24, (90, 110, 60)))):
            f = [0, .0, .45, .75, 1.05][k]; x = cx + (540 - cx) * f * 2; y = cy + (960 - cy) * f * 2
            d.ellipse((x - r, y - r, x + r, y + r), fill=col)
        return im.filter(ImageFilter.GaussianBlur(10))
    return E.cached('P_flare', mk)

# ================================================================================================ A2 — the invoice
PW = 560; P_X0 = 110; P_TOP = 300                # paper on the left, him on the right
ITEMS = [("Kickoff meeting", "$$$"), ("Meeting about the meeting", "$$$$"), ("Strategy deck (final_FINAL)", "$$$$"),
         ("Rush fee", "$$$$"), ("Another rush fee", "$$$$$"), ("Moodboard of vibes", "$$$"), ("Logo, but bigger", "$$$$"),
         ("“Synergy”", "$$$"), ("Revisions (again)", "$$$$"), ("Rush fee for the rush fee", "$$$$$$"),
         ("Account manager’s lunch", "$$$"), ("Thinking about your brand", "$$$$"), ("Out-of-office reply", "$$"),
         ("Meeting to recap the meeting", "$$$$"), ("Executive “vibe check”", "$$$$$"), ("Font that looks the same", "$$$"),
         ("Brainstorm (nobody came)", "$$$$"), ("Overtime for the overtime", "$$$$$"), ("Re-sending the deck", "$$$"),
         ("Another kickoff meeting", "$$$$"), ("Rush fee (premium)", "$$$$$$"), ("Pivot fee", "$$$$"),
         ("Meeting about the pivot", "$$$$"), ("More synergy", "$$$$$"), ("Stock photo of a handshake", "$$$"),
         ("Even more rush", "$$$$$$"), ("Celebratory lunch", "$$$$"), ("Post-launch meeting", "$$$$"),
         ("Meeting about the invoice", "$$$$"), ("Invoice formatting", "$$$"), ("Rush fee (again)", "$$$$$"),
         ("Second opinion on the logo", "$$$$"), ("Third opinion on the logo", "$$$$$"), ("Vibes (extra)", "$$$"),
         ("Coffee for the coffee meeting", "$$$"), ("Alignment session", "$$$$"), ("Realignment session", "$$$$$"),
         ("Strategy deck (REAL_final)", "$$$$"), ("Rush fee (deluxe)", "$$$$$$"), ("Meeting to plan the meeting", "$$$$"),
         ("Thinking about it more", "$$$$"), ("Synergy (premium)", "$$$$$"), ("One more small change", "$$$$$$"),
         ("Another one more small change", "$$$$$$")]
HEAD_H = 196; ROW = 60
T_STAMP = 459 / FPS                             # 15.30: the $$$$$$ stamp lands (f of FORTUNE 15.21-.33, vowel 15.34)

def paper_tall():
    def mk():
        n = len(ITEMS); h = HEAD_H + n * ROW + 40
        im = Image.new('RGBA', (PW, h), (247, 244, 236, 255)); d = ImageDraw.Draw(im)
        rng = np.random.default_rng(5); nz = rng.normal(0, 3.2, (h, PW, 1)).astype(np.float32)
        a = np.asarray(im, np.float32); a[..., :3] += nz; a[..., :3] *= (1 - .06 * np.abs(np.linspace(-1, 1, PW))[None, :, None] ** 2)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'); d = ImageDraw.Draw(im)
        d.text((30, 26), 'INVOICE', font=E.font(78, 900), fill=(22, 20, 30))
        d.text((32, 118), 'BIG AGENCY CO.', font=E.font(25, 700), fill=(120, 116, 130))
        f = E.font(25, 600); txt = 'BILL TO: YOU'; l, tp, r, b = f.getbbox(txt)
        d.text((PW - 30 - r, 118), txt, font=f, fill=(120, 116, 130))
        d.line((30, 166, PW - 30, 166), fill=(40, 38, 48), width=3)
        fi = E.font(29, 500); fa = E.font(30, 800)
        for i, (name, amt) in enumerate(ITEMS):
            y = HEAD_H + i * ROW
            d.text((30, y), name, font=fi, fill=(34, 32, 42))
            l, tp, r, b = fa.getbbox(amt); ax = PW - 30 - r
            d.text((ax, y - 1), amt, font=fa, fill=(170, 30, 40))
            l2, tp2, r2, b2 = fi.getbbox(name); x0 = 30 + r2 + 10
            for xx in range(int(x0), int(ax - 10), 11): d.ellipse((xx, y + 25, xx + 3, y + 28), fill=(170, 166, 176))
            if i % 2 == 1: d.line((30, y + ROW - 12, PW - 30, y + ROW - 12), fill=(228, 224, 216), width=1)
        return im
    return E.cached('P_paper', mk)

def roller(w, d=64, wood=(98, 52, 30)):
    def mk():
        im = Image.new('RGBA', (w + 2 * d, d), (0, 0, 0, 0))
        y = np.linspace(-1, 1, d)[:, None]; sh = np.clip(1 - y ** 2, 0, 1) ** .5
        body = (np.array([240, 236, 226], np.float32)[None, None] * (.55 + .5 * sh[..., None]) - 60 * (y[..., None] > .3) * (y[..., None] - .3))
        body = np.clip(np.repeat(body, w, 1), 0, 255).astype(np.uint8)
        im.paste(Image.fromarray(body, 'RGB'), (d, 0))
        cap = np.clip(np.array(wood, np.float32)[None, None] * (.5 + .9 * sh[..., None]), 0, 255).astype(np.uint8)
        capi = Image.fromarray(np.repeat(cap, d, 1), 'RGB').convert('RGBA')
        m = Image.new('L', (d, d)); ImageDraw.Draw(m).rounded_rectangle((0, 4, d - 1, d - 5), 14, fill=255); capi.putalpha(m)
        im.alpha_composite(capi, (0, 0)); im.alpha_composite(capi, (w + d, 0))
        return im
    return E.cached(('P_roller', w, d), mk)

def roll_y(t):
    """centre y of the falling bottom roller (paper top at P_TOP)."""
    y0 = P_TOP + HEAD_H + 6
    if t < ON['IT16']: return y0
    u = t - ON['IT16']; return y0 + 120 * u + .5 * 7800 * u * u

def a2_invoice(ctx, t):
    lt = t - T_A2
    ctx.bg_img = bg_soft(); ctx.avatar.update(x=330.)
    ctx.cam.update(z=1.10 + .03 * eo(lt / 1.2, 2), x=600., y=820.)
    # the camera tilts down the endless paper after the roll is gone (paper moves up)
    tilt = 0.0
    if t > 15.30: tilt = 520 * (t - 15.30) + 600 * ei((t - 15.30) / .5, 2) * (t - 15.30)
    ry = roll_y(t)
    paper = paper_tall(); L = int(max(HEAD_H, min(paper.height, ry - P_TOP)))
    vis = paper.crop((0, 0, PW, L))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    top = P_TOP - tilt
    # soft shadow of the paper on the set
    sm_ = Image.new('L', (PW, L), 140).filter(ImageFilter.GaussianBlur(0))
    shd = Image.new('RGBA', (PW + 60, L + 60), (0, 0, 0, 0)); m = Image.new('L', shd.size); m.paste(sm_, (30, 30))
    shd.putalpha(m.filter(ImageFilter.GaussianBlur(18)))
    lay.alpha_composite(shd, (P_X0 + 18 - 30, int(top) + 22 - 30)) if top + 22 - 30 > -L - 60 else None
    lay.alpha_composite(vis, (P_X0, int(top)))
    # top roller (holds the header) + the falling bottom roller
    rt = roller(PW, 58); lay.alpha_composite(rt, (P_X0 - 58, int(top) - 40))
    if ry - tilt < H + 80:
        rb = roller(PW, 70); spin = ((ry * .25) % 8) - 4
        lay.alpha_composite(rb, (P_X0 - 70, int(ry - tilt - 35 + spin * 0)))
    # $$$$$$ rubber stamp on FORTUNE
    # (it slams from 2.4x on the f of FORTUNE and lands on frame T_STAMP; it is inked ON the paper -> scrolls with it)
    k = t - (T_STAMP - .07)
    if k > 0:
        stp = SH.generic_stamp(w=470, angle=-12, word='$$$$$$', seed=11)
        s = 1 + 1.4 * (1 - eo(k / .07, 2)); al = clamp(k / .03)
        im = scaled(stp, s); im = E.fade(im, al)
        lay.alpha_composite(im, (int(P_X0 + PW / 2 - im.width / 2 + 10), int(P_TOP + 520 - tilt - im.height / 2)))
    sx, sy = shake(t, T_STAMP, 9, .16, 23, 1.0)
    sx2, sy2 = shake(t, ON['IT16'] + .02, 4, .2, 17, 2.0)
    ctx.add('screen', lay, sx + sx2, sy + sy2, center=False)
    captions(ctx, t)

# ================================================================================================ A3 — get in LINE
def line_bg():
    def mk():
        im = Image.open(os.path.join(E.THERAPY_A, 'storefront_line.jpg')).convert('RGB')
        sc = max(W / im.width, H / im.height); im = im.resize((int(im.width * sc + .5), int(im.height * sc + .5)), Image.LANCZOS)
        x0 = (im.width - W) // 2; im = im.crop((x0, 0, x0 + W, H))
        a = np.asarray(im, np.float32); g = a.mean(2, keepdims=True); a = g + (a - g) * .88       # slight desat, cooler
        a = a * np.array([.96, .97, 1.02]); return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return E.cached('P_line_bg', mk)

def _led_grid(text, cols):
    f = ffont(F_MONO, 15); im = Image.new('L', (cols, 13), 0)
    l, tp, r, b = f.getbbox(text); ImageDraw.Draw(im).text(((cols - (r - l)) // 2 - l, 1 - tp), text, font=f, fill=255)
    return (np.asarray(im) > 110)

def led_sign(line2, on=1.0):
    def mk():
        P = 7; cols = 118; rows = 13
        g1 = _led_grid('NOW SERVING:', cols); g2 = _led_grid(line2, cols) if line2 else np.zeros((rows, cols), bool)
        Wd, Hd = cols * P + 60, 2 * rows * P + 70
        im = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, Wd - 1, Hd - 1), 22, fill=(18, 14, 16, 245), outline=(70, 66, 72, 255), width=4)
        glow = Image.new('L', (Wd, Hd)); gd = ImageDraw.Draw(glow); dots = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); dd = ImageDraw.Draw(dots)
        for li, g in enumerate((g1, g2)):
            oy = 30 + li * (rows * P + 10)
            for r_ in range(rows):
                for c in range(cols):
                    x, y = 30 + c * P, oy + r_ * P
                    if g[r_, c]:
                        dd.ellipse((x, y, x + P - 2, y + P - 2), fill=(255, 92, 40, 255)); gd.ellipse((x - 1, y - 1, x + P, y + P), fill=255)
                    else:
                        dd.ellipse((x + 1, y + 1, x + P - 3, y + P - 3), fill=(52, 22, 18, 255))
        gl = Image.new('RGBA', (Wd, Hd), (255, 70, 30, 0)); gl.putalpha(glow.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .75)))
        im.alpha_composite(dots); im.alpha_composite(gl)
        return im
    return E.cached(('P_led', line2), mk)

def you_tag():
    def mk():
        f = E.font(54, 900); l, tp, r, b = f.getbbox('YOU'); w, h = r - l + 70, b - tp + 40
        im = Image.new('RGBA', (w + 120, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        g = E.gradient(w, h, E.GRAD).convert('RGBA'); m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
        g.putalpha(m); im.alpha_composite(g, (0, 15))
        d.text((35 - l, 15 + 20 - tp), 'YOU', font=f, fill=(250, 249, 246))
        # arrow pointing off-frame (right): the line goes on way past the edge
        ax = w + 14; ay = 15 + h // 2
        d.line((ax, ay, ax + 78, ay), fill=(250, 249, 246), width=9); d.polygon([(ax + 100, ay), (ax + 70, ay - 22), (ax + 70, ay + 22)], fill=(250, 249, 246))
        return E.shadow(im, 14, .6, (0, 8))
    return E.cached('P_you', mk)

def a3_line(ctx, t):
    lt = t - T_A3
    z = 1.0 + .07 * eo(lt / .9, 2) + .03 * dec(t, ON['LINE'], .2) * 0
    fr = E.zoom(line_bg(), z, (820, 980)).convert('RGBA')
    # NOW SERVING sign (flips on GET with the deli bell)
    on = t >= ON['GET'] - .01
    if on and t < ON['GET'] + .1:             # the new LED line blinks in frame by frame (on / off / on), housing stays solid
        on = int(math.floor((t - (ON['GET'] - .01)) * FPS + 1e-6)) % 2 == 0
    sgi = led_sign('SOMEONE ELSE' if on else '', 1.0)
    sy = 420 - 260 * (1 - eo(lt / .12, 3))
    fr.alpha_composite(sgi, (int(540 - sgi.width / 2), int(sy - sgi.height / 2)))
    # chain lines holding the sign
    d = ImageDraw.Draw(fr)
    for x in (540 - sgi.width / 2 + 60, 540 + sgi.width / 2 - 60): d.line((x, 0, x, sy - sgi.height / 2 + 4), fill=(40, 38, 44), width=5)
    # YOU tag + hourglass way back at the end of the line, pointing off-frame
    k = t - (ON['LINE'] - .02)
    if k > 0:
        tg = scaled(you_tag(), 1.2 * max(.05, backo(k / .2, 2.2)))
        fr.alpha_composite(tg, (int(800 - tg.width / 2), int(820 - tg.height / 2)))
        hg = rotated(emoji('⏳', 84), 180 * eo((k - .3) / .25) if k > .3 else 0)
        hg = scaled(hg, max(.05, backo((k - .08) / .2, 2.2)))
        fr.alpha_composite(hg, (int(562 - hg.width / 2), int(822 - hg.height / 2)))    # just left of the pill
    ctx.full = fr.convert('RGB')
    ctx.captions = False
    captions(ctx, t)
    ctx.post.update(vignette=.42)

# ================================================================================================ THE RULE
GK = E._load('_glasskit_P', os.path.join(E.V, 'lumarc-breakout/sections/_glasskit.py'))   # stone fracture + 3-D shards
TB_W, TB_H = 860, 900; TB_X0, TB_Y0 = 110, 240  # the tablet in the frame (x 110-970, y 240-1140)
ARCH = 150
R_SZ = 560; R_LX, R_LY = 430, 548               # the triangle set into the tablet (box centre, tablet-local)
R_AT = (TB_X0 + R_LX, TB_Y0 + R_LY)
HEAD_Y, PICK_Y = 150, 848
R_ST = dict(label=0., lit=(0., 0., 0.), x=(0., 0., 0.), edge=(0., 0., 0.), draw=(1., 1., 1.), glow=1.25)
T_LAND = ON['THAT'] - .02
T_PRE = ON['BEFORE'] + .06                      # hairline pre-crack
R_ZC = (540, 980)                               # camera push anchor: low, so the carved PICK TWO. never sinks onto the caption

def fbm(w, h, seed, octaves=((160, .40), (80, .24), (40, .15), (20, .09), (10, .06), (5, .04), (2, .02))):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32)
    for s, a in octaves:
        gh, gw = h // s + 3, w // s + 3
        g = Image.fromarray(rng.random((gh, gw)).astype(np.float32), 'F').resize((gw * s, gh * s), Image.BICUBIC)
        acc += np.asarray(g)[s:s + h, s:s + w] * a
    return acc / sum(a for _, a in octaves)

def _tablet_mask():
    def mk():
        m = Image.new('L', (TB_W, TB_H), 0); d = ImageDraw.Draw(m)
        d.rectangle((6, ARCH, TB_W - 7, TB_H - 6), fill=255); d.ellipse((6, 4, TB_W - 7, 2 * ARCH + 4), fill=255)
        n = fbm(TB_W, TB_H, 21, ((60, .45), (18, .3), (6, .25)))
        a = np.asarray(m.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255 + (n - .5) * .5
        a = np.clip((a - .5) * 7 + .5, 0, 1)
        return Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))
    return E.cached('P_tab_mask', mk)

def _engrave_masks():
    """(heading, triangle bed + labels, [PICK TWO. letters]) engraving depth masks (float 0..1, tablet-local).
    The labels and the bed are cut from the kit's own render (label=1 minus label=0), so they match the glass."""
    def mk():
        hd = Image.new('L', (TB_W, TB_H)); d = ImageDraw.Draw(hd)
        f = ffont(F_SERIF_B, 118); txt = 'THE RULE'; tr = 16
        tw = sum(f.getlength(c) for c in txt) + tr * (len(txt) - 1); x = (TB_W - tw) / 2
        for c in txt:
            l, tp, r, b = f.getbbox(c); d.text((x, HEAD_Y - (tp + b) / 2), c, font=f, fill=255); x += f.getlength(c) + tr
        d.line((170, 232, TB_W - 170, 232), fill=255, width=6); d.line((200, 246, TB_W - 200, 246), fill=170, width=3)
        lab1 = np.asarray(TRI.render(TRI.state(**dict(R_ST, label=1.)), R_SZ).getchannel('A'), np.float32) / 255
        lab0 = np.asarray(TRI.render(TRI.state(**R_ST), R_SZ).getchannel('A'), np.float32) / 255
        labels = np.clip((lab1 - lab0 - .3) / .35, 0, 1)
        bed = np.clip((lab0 - .06) / .12, 0, 1) * .45 + np.clip((lab0 - .7) / .2, 0, 1) * .45
        tm = np.zeros((TB_H, TB_W), np.float32); ox, oy = R_LX - R_SZ // 2, R_LY - R_SZ // 2
        tm[oy:oy + R_SZ, ox:ox + R_SZ] = np.maximum(labels, bed)
        f2 = ffont(F_SERIF_B, 88); txt = 'PICK TWO.'; track = 14
        tw = sum(f2.getlength(c) for c in txt) + track * (len(txt) - 1); x = (TB_W - tw) / 2; letters = []
        _, ctp, _, cb = f2.getbbox('PICK TWO')                 # one shared baseline (caps centred on PICK_Y)
        for c in txt:
            if c != ' ':
                m = Image.new('L', (TB_W, TB_H)); l, tp, r, b = f2.getbbox(c)
                ImageDraw.Draw(m).text((x, PICK_Y - (ctp + cb) / 2), c, font=f2, fill=255)
                letters.append((np.asarray(m, np.float32) / 255, (int(x + l) - 8, int(PICK_Y - 64), int(x + r) + 8, int(PICK_Y + 64))))
            x += f2.getlength(c) + track
        return np.asarray(hd, np.float32) / 255, tm, letters
    return E.cached('P_engr', mk)

def _shade_stone(eng):
    """stone tablet RGBA (tablet-local) with the depth mask `eng` carved in, raking warm light from the top-left."""
    from scipy.ndimage import gaussian_filter
    m = np.asarray(_tablet_mask(), np.float32) / 255
    n1 = fbm(TB_W, TB_H, 3); n3 = fbm(TB_W, TB_H, 12, ((12, .5), (4, .3), (2, .2)))
    n2 = fbm(TB_W, TB_H, 8, ((90, .5), (30, .3), (8, .2)))
    vein = np.clip(1 - np.abs(n2 - .5) / .010, 0, 1) * .6
    k = np.clip((n1 - .35) / .3, 0, 1)
    alb = np.array([108, 99, 88], np.float32) * (1 - k[..., None]) + np.array([176, 166, 148], np.float32) * k[..., None]
    alb = alb * (.9 + .2 * n3[..., None]) * (1 - .4 * vein[..., None])
    rng = np.random.default_rng(4); pits = gaussian_filter((rng.random((TB_H, TB_W)) > .993).astype(np.float32), 1.0) * 5
    e = gaussian_filter(eng, 1.3)
    hgt = gaussian_filter(m, 9) * 1.4 - e * .85 + n1 * .10 + n3 * .05 - pits * .03
    gy, gx = np.gradient(hgt)
    L = np.array([-.6, -.8])
    sh = (gx * L[0] + gy * L[1]) * -46
    lit = 1 + np.clip(sh, -.8, 1.1)
    ao = 1 - .55 * np.clip(e * 1.3, 0, 1) - .3 * np.clip(gaussian_filter(e, 5) - e, 0, 1)
    edge_ao = .62 + .38 * np.clip((gaussian_filter(m, 22) - .45) / .4, 0, 1)
    yy = np.linspace(0, 1, TB_H)[:, None]; xx = np.linspace(-1, 1, TB_W)[None, :]
    spot = 1.12 - .42 * yy ** 1.3 - .16 * xx ** 2 - .08 * xx
    rgb = alb * (lit * ao * edge_ao * spot)[..., None] * np.array([1.07, .98, .86])
    dirt = np.clip(e * 1.2, 0, 1) * (.5 + .5 * n3)                 # dust packed in the cuts
    rgb = rgb * (1 - .18 * dirt[..., None]) + np.array([150, 136, 116]) * .14 * dirt[..., None]
    a = np.clip(m, 0, 1) * 255
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a]).astype(np.uint8), 'RGBA')

N_LET = 8
def tablet(n_letters):
    def mk():
        hd, tm, letters = _engrave_masks()
        eng = np.maximum(hd, tm)
        for k in range(n_letters): eng = np.maximum(eng, letters[k][0])
        return _shade_stone(eng)
    return E.cached(('P_tablet', n_letters), mk)

def tablet_at(n):
    """tablet with the first n letters of PICK TWO. carved (bare render + the full render pasted per letter box)."""
    n = max(0, min(N_LET, n))
    if n in (0, N_LET): return tablet(n)
    def mk():
        base = tablet(0).copy(); full = tablet(N_LET); letters = _engrave_masks()[2]
        for k in range(n):
            bb = letters[k][1]; base.paste(full.crop(bb), bb[:2])
        return base
    return E.cached(('P_tab_n', n), mk)

def void_bg():
    """dark ancient vault: warm top spotlight cone on a deep shadow."""
    def mk():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - 540) / 640) ** 2 + ((yy - 700) / 780) ** 2)
        glow = np.clip(1 - r, 0, 1) ** 1.7
        cone = np.clip(1 - np.abs(xx - 540) / (190 + yy * .42), 0, 1) * np.clip(1 - yy / 1800, 0, 1)
        rgb = np.array([10, 9, 13], np.float32) + glow[..., None] * np.array([62, 46, 34]) + cone[..., None] ** 2 * np.array([40, 32, 24])
        n = fbm(W // 2, H // 2, 31, ((60, .6), (16, .4)))
        n = np.asarray(Image.fromarray(n, 'F').resize((W, H), Image.BILINEAR))
        rgb = rgb * (.82 + .36 * n[..., None])
        return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    return E.cached('P_void', mk)

def motes(t, n=80, seed=3, bright=1.0):
    """dust motes floating in the light cone (pure function of t), soft."""
    S = 2; lay = Image.new('L', (W // S, H // S), 0); d = ImageDraw.Draw(lay)
    for i in range(n):
        x0 = 120 + hr(i, seed) * 840; y0 = 60 + hr(i, seed + 1) * 1500
        x = x0 + 34 * math.sin(t * (.3 + .4 * hr(i, seed + 2)) + i); y = (y0 + t * (14 + 22 * hr(i, seed + 3))) % 1600 + 80
        r = (1.0 + 3.2 * hr(i, seed + 4) ** 2) / S; a = (.3 + .7 * hr(i, seed + 5)) * bright
        a *= .5 + .5 * math.sin(t * 2.1 + i * 1.7) ** 2
        cone = clamp(1 - abs(x - 540) / (220 + y * .42))
        a *= .25 + .75 * cone
        d.ellipse((x / S - r, y / S - r, x / S + r, y / S + r), fill=int(255 * min(1, a)))
    lay = lay.filter(ImageFilter.GaussianBlur(.9)).resize((W, H), Image.BILINEAR)
    out = Image.new('RGBA', (W, H), (255, 228, 196, 0)); out.putalpha(lay.point(lambda v: int(v * .8))); return out

def puff(t0, t, x0, y0, n=60, seed=2, spread=1.0, col=(214, 198, 178), w=1.0):
    """soft stone-dust cloud (blurred particles) blown sideways from (x0, y0)."""
    u = t - t0
    if u < 0 or u > 1.1: return None
    S = 3; L_ = Image.new('L', (W // S, H // S), 0); d = ImageDraw.Draw(L_)
    for i in range(n):
        side = -1 if hr(i, seed) < .5 else 1; ang = (hr(i, seed + 1) * .7 - .1) * math.pi * .5
        v = (300 + 900 * hr(i, seed + 2)) * spread
        x = x0 + side * math.cos(ang) * v * u * (1 - .45 * min(1, u)) * w
        y = y0 - math.sin(ang) * v * u * .55 * (1 - .5 * min(1, u))
        r = (10 + 30 * hr(i, seed + 3)) * (1 + 2.2 * u) / S
        a = clamp(1 - u / (.6 + .5 * hr(i, seed + 4))) * clamp(u / .03)
        d.ellipse((x / S - r, y / S - r, x / S + r, y / S + r), fill=int(95 * a))
    L_ = L_.filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
    out = Image.new('RGBA', (W, H), col + (0,)); out.putalpha(L_); return out

def chips(lay, t, t0, x0, y0, n=10, seed=40):
    """chisel chips + a puff of grit at (x0, y0)."""
    u = t - t0
    if u < 0 or u > .3: return
    d = ImageDraw.Draw(lay)
    for i in range(n):
        a = -math.pi * (.1 + .8 * hr(i, seed)); v = 300 + 700 * hr(i, seed + 1)
        x = x0 + math.cos(a) * v * u; y = y0 + math.sin(a) * v * u + 2600 * u * u
        r = 1.5 + 3 * hr(i, seed + 2); al = clamp(1 - u / .3)
        d.polygon([(x - r, y), (x, y - r * .8), (x + r, y + r * .3), (x - r * .2, y + r)], fill=(196, 182, 160, int(255 * al)))

def frac():
    def mk():
        imp = TRI.anchor('impact', TRI.state(**R_ST), R_SZ, canvas=(W, H), at=R_AT)
        return GK.Fracture(center=imp, size=(W, H), seed=5, radials=15,
                           hits=[(T_PRE, 6, 46, .3, .22), (T_IMPACT, 70, 430, .9, .05)],
                           race=(T_IMPACT + .035, 5600.), web=(T_IMPACT + .05, .14))
    return E.cached('P_frac', mk)

def tab_outline(d=5.0, n=56):
    """the tablet's (convex) silhouette in frame px, inset d: elliptical arch + straight sides + flat base."""
    cx = TB_X0 + (TB_W - 1) / 2; a = (TB_W - 13) / 2 - d; b = ARCH - d; ey = TB_Y0 + ARCH + 4
    pts = [(cx + a * math.cos(th), ey - b * math.sin(th)) for th in np.linspace(0, math.pi, n)]
    return pts + [(TB_X0 + 6 + d, TB_Y0 + TB_H - 6 - d), (TB_X0 + TB_W - 7 - d, TB_Y0 + TB_H - 6 - d)]

def clip_convex(poly, clip):
    """Sutherland-Hodgman: polygon clipped by a convex polygon (either winding)."""
    n = len(clip); A = sum(clip[i][0] * clip[(i + 1) % n][1] - clip[(i + 1) % n][0] * clip[i][1] for i in range(n))
    def side(a, b, p): return ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) * A
    out = [tuple(map(float, p)) for p in poly]
    for i in range(n):
        a, b = clip[i], clip[(i + 1) % n]; inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]; sp, sq = side(a, b, p), side(a, b, q)
            if (sp >= 0) != (sq >= 0):
                k = sp / (sp - sq); out.append((p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k))
            if sq >= 0: out.append(q)
        if not out: break
    return out

def shards():
    def mk():
        F = frac(); S = GK.Shatter(F, seed=4, focal=1600., vp=F.C, rect=(TB_X0, TB_Y0, TB_X0 + TB_W, TB_Y0 + TB_H),
                                   speed=1.5, wave=6000.)
        sil = tab_outline(); keep = []
        for sh in S.shards:          # cut every piece to the stone: no void corners, no bevel along the clip box
            polys = [q for q in (clip_convex(p, sil) for p in sh['polys']) if len(q) >= 3 and GK.poly_area(q) > 6]
            if not polys: continue
            xs = [p[0] for q in polys for p in q]; ys = [p[1] for q in polys for p in q]
            sh.update(polys=polys, poly=[p for q in polys for p in q],
                      bbox=(int(math.floor(min(xs))) - 2, int(math.floor(min(ys))) - 2, int(math.ceil(max(xs))) + 3, int(math.ceil(max(ys))) + 3))
            keep.append(sh)
        S.shards = keep; return S
    return E.cached('P_shards', mk)

def tab_layer(n_let):
    """frame-sized RGBA with the tablet at rest."""
    def mk():
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); im.alpha_composite(tablet_at(n_let), (TB_X0, TB_Y0)); return im
    return E.cached(('P_tab_layer', n_let), mk)

def leak_at(t):
    if t < T_PRE: return 0.0
    if t < T_IMPACT: return .35 + .4 * clamp((t - T_PRE) / (T_IMPACT - T_PRE))
    return .75 + 1.0 * dec(t, T_IMPACT, .10)

def cracked(t):
    """the tablet layer with the stone fracture at t (cracks, violet light leaking through)."""
    tab = tab_layer(N_LET)
    if t < T_PRE: return tab
    rgb = frac().composite(tab, t, refr=.7, leak=leak_at(t), glint=.5, sparks=.4, powder=.7)
    out = rgb.convert('RGBA'); out.putalpha(tab.getchannel('A')); return out

def ancient(im, k):
    """age the glass triangle: sepia, flat, dusty (k 0..1)."""
    if k <= .01: return im
    bb = im.getbbox()
    if bb is None: return im
    sub = im.crop(bb); a = np.asarray(sub, np.float32); rgb = a[..., :3]; lum = rgb.mean(2, keepdims=True)
    sep = lum * np.array([.92, .82, .66]) * .85 + np.array([34, 28, 18])
    dn = E.cached(('P_dust_tex', sub.size), lambda: fbm(sub.width, sub.height, 77, ((6, .5), (2, .5))))
    sep = sep * (1 - .25 * dn[..., None]) + 60 * dn[..., None] * .3
    rgb2 = rgb * (1 - k) + sep * k
    out = im.copy(); out.paste(Image.fromarray(np.dstack([np.clip(rgb2, 0, 255), a[..., 3:]]).astype(np.uint8), 'RGBA'), bb[:2])
    return out

def tri_rule(t, dx=0., dy=0.):
    """the kit triangle set into the tablet: aged until AI, then it cracks (kit crack) and shatters (kit shatter)."""
    if t < T_IMPACT: st = TRI.state(**R_ST)
    elif t < T_SHAT: st = TRI.state(crack=clamp((t - T_IMPACT) / (T_SHAT - T_IMPACT - 1 / FPS)), **R_ST)
    else:
        u = t - T_SHAT; st = TRI.state(crack=1., shatter=clamp(.12 * (1 - math.exp(-u / .03)) + 2.3 * u), **R_ST)
    im = TRI.render(st, R_SZ, canvas=(W, H), at=(R_AT[0] + dx, R_AT[1] + dy))
    k = 1.0 if t < T_IMPACT else clamp(1 - (t - T_IMPACT) / .1)
    return ancient(im, k)

def rule(ctx, t):
    lt = t - T_RULE
    ctx.avatar['show'] = False
    fr = void_bg().copy().convert('RGBA')
    # the tablet drops in from above and lands on THAT
    if t < T_LAND:
        u = clamp((t - T_RULE) / (T_LAND - T_RULE)); dy = -900 * (1 - u) ** 1.7
    else:
        dy = -10 * math.exp(-(t - T_LAND) / .07) * math.sin((t - T_LAND) * 38)
    tx = ty = 0.0
    if ON['BEFORE'] <= t < T_IMPACT:          # tremble: something is pushing from inside
        k = ei((t - ON['BEFORE']) / (T_IMPACT - ON['BEFORE']), 1.4) * 3.6
        tx = k * math.sin(t * 97); ty = k * math.sin(t * 131 + 1)
    ox, oy = tx, dy + ty
    if t < T_SHAT:
        # contact shadow under the tablet
        sh = shadow_tab(); fr.alpha_composite(E.fade(sh, clamp(1 - abs(dy) / 500)), (0, int(oy * .2)))
        n_let = 0
        if t >= ON['WRITTEN'] - .02: n_let = min(N_LET, 1 + int((t - (ON['WRITTEN'] - .02)) / .036))
        lay = cracked(t) if t >= T_PRE else tab_layer(n_let)
        if dy < -60:                           # falling: vertical motion smear
            for k in range(3, 0, -1): fr.alpha_composite(E.fade(lay, .22), (int(ox), int(oy - k * 34)))
        fr.alpha_composite(lay, (int(ox), int(oy)))
        # warm glint across THE RULE on RULE
        g = t - ON['RULE']
        if 0 <= g < .55:
            fr.alpha_composite(head_glint(g), (int(TB_X0 + ox), int(TB_Y0 + oy)))
        # chisel: chips fly from the letter being cut
        if ON['WRITTEN'] - .02 <= t < ON['WRITTEN'] + .40:
            k = min(N_LET - 1, int((t - (ON['WRITTEN'] - .02)) / .036)); bb = _engrave_masks()[2][k][1]
            ch = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            for j in range(max(0, k - 2), k + 1):
                bj = _engrave_masks()[2][j][1]
                chips(ch, t, ON['WRITTEN'] - .02 + j * .036, TB_X0 + ox + (bj[0] + bj[2]) / 2, TB_Y0 + oy + PICK_Y - 30, n=9, seed=40 + j)
            fr.alpha_composite(ch)
        fr.alpha_composite(tri_rule(t, ox, oy))
    else:
        u = t - T_SHAT; tau = .95 * u + .10 * (1 - math.exp(-u / .04)); dz = 520 * u ** 1.3
        dzp = 520 * max(0, u - 1 / FPS) ** 1.3
        S = shards()
        glass = E.cached('P_glass_at_shat', lambda: Image.alpha_composite(void_bg().convert('RGBA'), cracked(T_SHAT - .001)).convert('RGB'))
        fr = S.render(fr, glass, tau, dz=dz, focus_z=1600., dof=3., shutter_dtau=.014, dz_prev=dzp, spec_gain=.35,
                      img_alpha=1.0, cull_scale=3.6)
        D = E.cached('P_gkdust', lambda: GK.Dust(frac(), n=220, seed=6, focal=1600., vp=frac().C))
        fr.alpha_composite(D.render((W, H), tau, dz, .03, dzp, alpha=clamp(1 - u / .45), sparkle=.25, gain=1.1))
        fr.alpha_composite(tri_rule(t))
    p = puff(T_LAND, t, TB_X0 + TB_W / 2, TB_Y0 + TB_H - 30 + oy * 0, n=56, seed=2)
    if p is not None: fr.alpha_composite(p)
    if t >= T_SHAT:
        p2 = burst_cloud(T_SHAT, t, frac().C[0], frac().C[1])
        if p2 is not None: fr.alpha_composite(p2)
    fr.alpha_composite(motes(t, bright=1.0 if t < T_SHAT else .5 + .5 * dec(t, T_SHAT, .4)))
    # camera: slow push, punch on AI, shake on the landing + the impact
    z = 1.0 + .06 * eo(lt / 1.75, 1.6) + .06 * dec(t, T_IMPACT, .16) * (t >= T_IMPACT)
    sx, sy = shake(t, T_LAND, 13, .13, 21, .3); sx2, sy2 = shake(t, T_IMPACT, 17, .15, 26, 2.2)
    out = E.zoom(fr.convert('RGB'), z, R_ZC, dx=sx + sx2, dy=sy + sy2)
    if t >= T_STILL - .12:                     # the beat of stillness: lights almost out
        k = eo((t - (T_STILL - .12)) / .16); out = Image.blend(out, Image.new('RGB', out.size, (3, 2, 5)), .62 * k)
    ctx.full = out
    if t >= T_IMPACT:
        ctx.post['flash'] = .7 * dec(t, T_IMPACT, .05); ctx.post['flash_col'] = (226, 212, 255)
    if t >= T_SHAT: ctx.post['flash'] = max(ctx.post['flash'], .3 * dec(t, T_SHAT, .05))
    fl = .035 * math.sin(t * 23.0) * math.sin(t * 7.3 + 1.1) + .02 * math.sin(t * 41.0)      # torch-like flicker
    ctx.post.update(vignette=.5, grain=1.2, bright=1.0 + fl)
    captions(ctx, t)

def burst_cloud(t0, t, x0, y0, n=46, seed=8, col=(196, 182, 172)):
    """radial stone-dust cloud from the impact (soft, expanding, thinning)."""
    u = t - t0
    if u < 0 or u > 1.0: return None
    S = 3; L_ = Image.new('L', (W // S, H // S), 0); d = ImageDraw.Draw(L_)
    for i in range(n):
        a = hr(i, seed) * 2 * math.pi; v = 260 + 900 * hr(i, seed + 1)
        rr = v * u * (1 - .5 * min(1, u))
        x = x0 + math.cos(a) * rr; y = y0 + math.sin(a) * rr * .85 + 160 * u * u
        r = (16 + 40 * hr(i, seed + 3)) * (1 + 2.6 * u) / S
        al = clamp(1 - u / (.45 + .45 * hr(i, seed + 4))) * clamp(u / .03)
        d.ellipse((x / S - r, y / S - r, x / S + r, y / S + r), fill=int(70 * al))
    L_ = L_.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
    out = Image.new('RGBA', (W, H), col + (0,)); out.putalpha(L_); return out

def shadow_tab():
    def mk():
        im = Image.new('L', (W, H)); d = ImageDraw.Draw(im)
        d.ellipse((TB_X0 - 40, TB_Y0 + TB_H - 40, TB_X0 + TB_W + 40, TB_Y0 + TB_H + 60), fill=200)
        im = im.filter(ImageFilter.GaussianBlur(30)); out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.putalpha(im); return out
    return E.cached('P_shadow_tab', mk)

def head_glint(g):
    hd = _engrave_masks()[0]; gx = -260 + 1400 * eo(g / .5, 2)
    xx = np.arange(TB_W, dtype=np.float32)[None, :]; yy = np.arange(TB_H, dtype=np.float32)[:, None]
    band = np.clip(1 - np.abs(xx + (yy - HEAD_Y) * .35 - gx) / 95, 0, 1) * clamp(1.4 - g / .55)
    near = np.clip(1 - np.abs(yy - HEAD_Y) / 140, 0, 1)
    mm = np.clip(band * near * (.30 + 1.3 * (hd > .2)), 0, 1)
    gl = Image.new('RGBA', (TB_W, TB_H), (255, 220, 160, 0))
    gl.putalpha(ImageChops.multiply(Image.fromarray((mm * 235).astype(np.uint8)), _tablet_mask())); return gl

# ================================================================================================ draw
def draw(ctx, lt, t):
    j = int(round(t * FPS)); ctx.captions = False          # own captions on the measured onsets (see PAGES)
    if j < J_A1: q_round(ctx, t, 0)
    elif j < J_Q2: a1_cheap(ctx, t)
    elif j < J_A2: q_round(ctx, t, 1)
    elif j < J_Q3: a2_invoice(ctx, t)
    elif j < J_A3: q_round(ctx, t, 2)
    elif j < J_RULE: a3_line(ctx, t)
    else: rule(ctx, t)

# ================================================================================================ cues
CUES = sorted(q_cues() + [
    (T_Q1, 'snap', {'gain': -9}), (T_Q1 + .01, 'shing', {'gain': -15}),          # the body cuts in (no pre-roll into the hooks)
    # A1 cheap
    (T_A1, 'scratch', {'gain': -5}), (T_A1 + .01, 'pop', {'gain': -12}),
    (ON['IT14'], 'swipe', {'gain': -14}),
    (ON['CHEAP2'], 'buzzer', {'dur': .5, 'gain': -8}), (ON['CHEAP2'], 'pop', {'gain': -10}),
    (T_Q2, 'swoosh', {'gain': -11}),
    # A2 invoice
    (T_A2, 'film', {'dur': .35, 'gain': -14}),
    (ON['IT16'], 'swoosh', {'gain': -10}), (ON['IT16'] + .02, 'film', {'dur': .9, 'gain': -10}),
    (ON['COSTS'], 'counter', {'dur': .4, 'gain': -16}),
    (T_STAMP, 'stamp', {'gain': -4}), (T_STAMP + .01, 'cash', {'gain': -6}),
    (15.32, 'swoosh', {'gain': -15}),
    (T_Q3, 'swoosh', {'gain': -11}),
    # A3 line
    (T_A3, 'swipe', {'gain': -12}), (ON['GET'], 'ding', {'note': 'A6', 'gain': -7}),
    (ON['IN'], 'clock', {'i': 0, 'gain': -12}), (ON['LINE'], 'pop', {'gain': -11}), (ON['LINE'] + .02, 'clock', {'i': 1, 'gain': -12}),
    (16.98, 'crickets', {'dur': .4, 'gain': -16}), (17.12, 'clock', {'i': 0, 'gain': -13}),
    # the rule
    (T_RULE, 'whoosh', {'gain': -13}), (ON['THAT'] - .02, 'stone', {'gain': -3}), (ON['THAT'] - .02, 'thud', {'gain': -8}),
    (ON['RULE'], 'braam', {'note': 'D2', 'dur': 1.0, 'gain': -12}),
    (ON['WRITTEN'] - .02, 'snap', {'gain': -12}), (ON['WRITTEN'] + .07, 'snap', {'gain': -14}),
    (ON['WRITTEN'] + .14, 'snap', {'gain': -14}), (ON['WRITTEN'] + .22, 'snap', {'gain': -13}),
    (ON['BEFORE'], 'riser', {'to': T_IMPACT, 'gain': -10}), (ON['BEFORE'] + .1, 'crack', {'gain': -16, 'seed': 3}),
    (ON['AI'], 'impact', {'gain': 0}), (ON['AI'], 'crack', {'gain': -1, 'seed': 1}), (ON['AI'] + .06, 'glass', {'gain': -9}),
    (T_SHAT, 'shatter', {'gain': 0, 'dur': 1.0}), (T_SHAT, 'sub', {'gain': -8}), (T_SHAT + .01, 'impact', {'gain': -8}),
], key=lambda c: c[0])
