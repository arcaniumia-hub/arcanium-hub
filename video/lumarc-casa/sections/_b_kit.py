"""_b_kit.py — shared helpers for s03_paredes + s04_porta (author B).  Pure functions of t; nothing here changes the
house's state timeline (sections/_house.py is read-only and is only CALLED: state_at / render / its camera projection).

  * measured word onsets (src/tight16k.raw, 5 ms spectrogram + 80-900 Hz / >3.5 kHz band envelopes) and the caption
    pages they drive (the engine's automatic estimates run 0.1-0.25 s late on PORTA / CHAMADO / VÍDEOS, so these
    sections draw their own captions with the engine's exact look: word_img, pop, emphasis gradient)
  * house layer: HS.render through a camera path, placed in the 1080x1920 world, + projection of 3-D points / tiles
  * callouts: architectural annotation (anchor dot + pulse, drawn leader line, frosted label pill)
  * flying post cards (projective warp into a wall tile's quad, motion-blurred)
"""
import math, os, sys
_PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJ not in sys.path: sys.path.insert(0, _PROJ)          # also runnable as `python3 sections/_b_kit.py ...`
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import engine as E
from sections import _house as HS

W, H, FPS = E.W, E.H, E.FPS
clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back

# ------------------------------------------------------------------------------------------------ measured onsets
# seg 6  "As paredes são o seu conteúdo."
O_AS6, O_PAREDES, O_SAO6, O_O6, O_SEU6, O_CONTEUDO = 9.39, 9.56, 10.25, 10.40, 10.48, 10.72
# seg 7  "As janelas são os seus vídeos."   (JA-: the j fricative 11.59, vowel 11.63; -NE- 11.79)
O_AS7, O_JANELAS, O_SAO7, O_OS7, O_SEUS7, O_VIDEOS = 11.445, 11.59, 12.36, 12.50, 12.60, 12.84
# seg 8  "E a porta é o seu chamado pra ação."  (PORTA p burst 13.70 | é 14.35 | s of seu 14.51 | ʃ of chamado 14.71 |
#         p of pra 15.29 | ç of ação 15.45 (kit CTA 15.42), -ÃO vowel 15.59)
O_E8, O_A8, O_PORTA, O_E8B, O_O8, O_SEU8, O_CHAMADO, O_PRA, O_ACAO = 13.44, 13.50, 13.70, 14.35, 14.45, 14.51, 14.71, 15.29, 15.42
# seg 9  "Agora repara…"
O_AGORA, O_REPARA = 15.89, 16.36

# caption pages (words: (text, onset, emphasis)); a page shows [a, z)
PAGES = [
    dict(a=9.35, z=10.23, words=[('AS', O_AS6, 0), ('PAREDES', O_PAREDES, 1)]),
    dict(a=10.21, z=10.70, words=[('SÃO', O_SAO6, 0), ('O', O_O6, 0), ('SEU', O_SEU6, 0)]),
    dict(a=11.40, z=12.34, words=[('AS', O_AS7, 0), ('JANELAS', O_JANELAS, 1)]),
    dict(a=12.32, z=12.82, words=[('SÃO', O_SAO7, 0), ('OS', O_OS7, 0), ('SEUS', O_SEUS7, 0)]),
    dict(a=13.40, z=14.33, words=[('E', O_E8, 0), ('A', O_A8, 0), ('PORTA', O_PORTA, 1)]),
    dict(a=14.31, z=14.69, words=[('É', O_E8B, 0), ('O', O_O8, 0), ('SEU', O_SEU8, 0)]),
    dict(a=15.84, z=16.68, words=[('AGORA', O_AGORA, 0), ('REPARA…', O_REPARA, 1)]),
]
# (CONTEÚDO / VÍDEOS / CHAMADO PRA AÇÃO are drawn as callout labels on the house — the same spoken words, one place)

# ------------------------------------------------------------------------------------------------ small maths
def lerp(a, b, k): return a + (b - a) * k
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def sio(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def expo(x): x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0
def C(k, fn): return E.cached(('B',) + (k if isinstance(k, tuple) else (k,)), fn)

def shake(t, t0, amp, dur=.32, freq=19.0, seed=0):
    """decaying camera shake (dx, dy) px after an impact at t0."""
    if t < t0 or t > t0 + dur: return 0.0, 0.0
    u = clamp((t - t0) / dur); e = (1 - u) ** 2.2 * amp
    ph = seed * 1.7
    return (e * .55 * math.sin(2 * math.pi * freq * (t - t0) + ph),
            e * math.sin(2 * math.pi * freq * 1.13 * (t - t0) + ph + 1.1))

def kick(t, t0, amp, dur=.22):
    """quick punch (0 -> amp -> 0) after t0."""
    if t < t0 or t > t0 + dur: return 0.0
    u = clamp((t - t0) / dur)
    return amp * math.sin(math.pi * min(1, u * 2.2)) * (1 - u) if u < 1 else 0.0

# ------------------------------------------------------------------------------------------------ backgrounds
def studio_bg(dim=.30, blur=5.0, sat=1.0, tint=None):
    """the studio plate, defocused + dimmed (depth of field: the house and he are in front of it). Cached."""
    def mk():
        im = E.studio().convert('RGB')
        if blur > .3: im = im.filter(ImageFilter.GaussianBlur(blur))
        a = np.asarray(im, np.float32)
        if sat != 1: g = a.mean(2, keepdims=True); a = g + (a - g) * sat
        a = a * (1 - dim)
        if tint is not None: a = a * np.array(tint, np.float32)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return C(('studio', dim, blur, sat, tint), mk)

def desat(img, s, cool=0.0):
    """RGBA/RGB saturation s (+ optional cool grade), alpha kept."""
    a = np.asarray(img, np.float32); rgb = a[..., :3]
    g = (rgb @ np.array([.299, .587, .114], np.float32))[..., None]
    rgb = g + (rgb - g) * s
    if cool: rgb = rgb * np.array([1 - .06 * cool, 1 - .02 * cool, 1 + .05 * cool], np.float32)
    out = np.concatenate([np.clip(rgb, 0, 255), a[..., 3:]], 2) if a.shape[2] == 4 else np.clip(rgb, 0, 255)
    return Image.fromarray(out.astype(np.uint8), img.mode)

def grade(img, mul=1.0, gamma=1.0):
    """exposure (mul) + contrast-ish gamma on RGB (alpha kept)."""
    lut = [int(min(255, 255 * ((v / 255) ** gamma) * mul)) for v in range(256)]
    ch = img.split(); rgb = Image.merge('RGB', ch[:3]).point(lut * 3)
    return Image.merge(img.mode, (*rgb.split(), *ch[3:])) if img.mode == 'RGBA' else rgb

# ------------------------------------------------------------------------------------------------ house layer
def cam_mix(a, b, k):
    """interpolate two house camera dicts."""
    out = {}
    for key in ('yaw', 'pitch', 'dist', 'fov', 'roll'):
        out[key] = lerp(a.get(key, 0.0 if key == 'roll' else 30.0), b.get(key, 0.0 if key == 'roll' else 30.0), k)
    out['target'] = tuple(lerp(np.array(a['target'], float), np.array(b['target'], float), k))
    sa, sb = a.get('shift', (0, 0)), b.get('shift', (0, 0))
    out['shift'] = (lerp(sa[0], sb[0], k), lerp(sa[1], sb[1], k))
    return out

def house_grade(img, haze=(7, 5, 16), mul=(.97, .96, 1.0)):
    """sit the maquette in the dark purple studio: a touch of atmospheric haze in the blacks (light match)."""
    luts = []
    for c in range(3):
        luts += [int(min(255, v * mul[c] + haze[c] * (1 - v / 255))) for v in range(256)]
    r, g, b, a = img.split()
    rgb = Image.merge('RGB', (r, g, b)).point(luts)
    return Image.merge('RGBA', (*rgb.split(), a))

def _fade_mask(w, h, y0, y1):
    def mk():
        g = np.clip((y1 - np.arange(h, dtype=np.float32)) / max(1, y1 - y0), 0, 1)
        g = g * g * (3 - 2 * g)
        return Image.fromarray((np.repeat(g[:, None], w, 1) * 255).astype(np.uint8))
    return C(('fade', w, h, y0, y1), mk)

class House:
    """one render of the house: image + a projector into the WORLD frame (the render is pasted at `org`).
    `fade` = (y0, y1): the layer fades out between these rows (the lot falls off into the dark studio below)."""
    def __init__(self, st, cam, size, org=(0, 0), t=None, ss=2, glow=1.0, grade=True, fade=None):
        self.st, self.cam, self.size, self.org = st, cam, size, org
        im = HS.render(st, cam, size=size, t=st['t'] if t is None else t, ss=ss, glow=glow)
        im = house_grade(im) if grade else im
        if fade is not None:
            a = ImageChops.multiply(im.getchannel('A'), _fade_mask(size[0], size[1], fade[0], fade[1])); im.putalpha(a)
        self.img = im
        self._c = HS._Cam(cam, size[0], size[1])
    def proj(self, P):
        """world-frame (x, y) of model-space 3-D points (N, 3) (follows the lot's rise like HS.anchor)."""
        lot = self.st['lot']
        P = np.asarray(P, float).reshape(-1, 3) * lot['s'] + np.array([0, lot['dy'], 0])
        S, Z = self._c.proj(P)
        return S + np.array(self.org, float), Z
    def cam_model(self):
        lot = self.st['lot']; return (self._c.C - np.array([0, lot['dy'], 0])) / lot['s']

# door handle (closed door, front face) — mirrors the kit's LED handle position on the door leaf
_DQ = HS.G.door_pane['open']
_DW = (_DQ[1][0] - _DQ[0][0]) - .06
HANDLE = np.array([_DQ[0][0] + .03 + _DW * (1 - .14), HS.YS + (2.0 - .03) * .5, HS.FRONT - .04])

def tile_faces(hs):
    """visible content tiles: list of dict(k, tex, t_tex, quad (TL TR BR BL world px), z) for the walls facing the camera."""
    Cc, A = HS._piece_transforms(hs.st)
    Cw = hs.cam_model(); out = []
    for k in HS.G.tiles:
        p = HS.PIECES[k]
        n = np.array(HS.WALL_N[p['wall']], float)
        if n @ (Cw - Cc[k]) <= 0.05: continue
        corners = Cc[k][None, :] + (A[k] @ HS._S8.T).T
        Q = corners[p['tc']] + n * .004
        S, Z = hs.proj(Q)
        if Z.min() < .5: continue
        out.append(dict(k=k, tex=p['tex'], t_tex=float(HS.G.t_tex[k]), quad=S, z=float(Z.mean()), wall=p['wall'],
                        center=S.mean(0)))
    return out

# ------------------------------------------------------------------------------------------------ warping
def homography(src, dst):
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()

def warp(src, quad, pad=2):
    """projectively map `src` (RGBA) onto the 4-corner quad (TL TR BR BL). Returns (img, x0, y0) or None."""
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    x0, y0 = int(math.floor(min(xs))) - 2, int(math.floor(min(ys))) - 2
    x1, y1 = int(math.ceil(max(xs))) + 2, int(math.ceil(max(ys))) + 2
    if x1 - x0 < 3 or y1 - y0 < 3 or x1 - x0 > 4000 or y1 - y0 > 4000: return None
    ew = max(math.hypot(quad[1][0] - quad[0][0], quad[1][1] - quad[0][1]), math.hypot(quad[2][0] - quad[3][0], quad[2][1] - quad[3][1]))
    sc = min(1.0, 1.5 * ew / src.width)
    if sc < .9: src = src.resize((max(4, int(src.width * sc)), max(4, int(src.height * sc))), Image.BILINEAR, reducing_gap=2.0)
    s2 = Image.new('RGBA', (src.width + 2 * pad, src.height + 2 * pad), (0, 0, 0, 0)); s2.paste(src, (pad, pad))
    sq = [(pad, pad), (s2.width - pad, pad), (s2.width - pad, s2.height - pad), (pad, s2.height - pad)]
    co = homography(sq, [(x - x0, y - y0) for x, y in quad])
    return s2.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BILINEAR), x0, y0

def mblur(img, dx, dy):
    """directional motion blur along (dx, dy) px (premultiplied average). Returns (img, pad_x, pad_y)."""
    L = math.hypot(dx, dy)
    if L < 3: return img, 0, 0
    n = int(clamp(L / 4, 4, 18))
    a = np.asarray(img, np.float32); al = a[..., 3:4] / 255.; pm = np.concatenate([a[..., :3] * al, al], 2)
    px, py = int(math.ceil(abs(dx) / 2)) + 1, int(math.ceil(abs(dy) / 2)) + 1
    big = np.zeros((a.shape[0] + 2 * py, a.shape[1] + 2 * px, 4), np.float32)
    for i in range(n):
        k = i / (n - 1) - .5; ox, oy = int(round(px + dx * k)), int(round(py + dy * k))
        big[oy:oy + a.shape[0], ox:ox + a.shape[1]] += pm
    big /= n; al2 = big[..., 3:4]
    rgb = np.where(al2 > 1e-4, big[..., :3] / np.maximum(al2, 1e-4), 0)
    return Image.fromarray(np.clip(np.concatenate([rgb, al2 * 255], 2), 0, 255).astype(np.uint8), 'RGBA'), px, py

# ------------------------------------------------------------------------------------------------ post cards
def post_card(tex, w=300):
    """the LUMARC post that wall tile `tex` shows (same image as the kit's tile), as a printed 4:5 card: white border,
    rounded corners, a soft inner vignette."""
    def mk():
        h = int(w * 1.25); p = HS.POSTS[tex % len(HS.POSTS)]
        try: im = HS._cover(Image.open(p), w, h)
        except Exception: im = Image.new('RGB', (w, h), (120, 100, 200))
        im = im.convert('RGBA'); d = ImageDraw.Draw(im)
        b = max(4, w // 30)
        d.rectangle((0, 0, w - 1, h - 1), outline=(240, 236, 228, 255), width=b)
        return E.rounded(im, max(6, w // 26))
    return C(('card', tex, w), mk)

# ------------------------------------------------------------------------------------------------ captions
_CAP_BASE = 92
def _layout(words, base):
    items = []
    for (txt, t0, em) in words:
        sz = int(base * (1.2 if em else 1.0)); l, t_, r, b = E.font(sz).getbbox(txt)
        if r - l > 900: sz = int(sz * 900 / (r - l)); l, t_, r, b = E.font(sz).getbbox(txt)
        items.append([txt, t0, em, sz, r - l])
    tot = sum(it[4] for it in items) + base * .34 * (len(items) - 1)
    x = -tot / 2; out = []
    for it in items:
        out.append((it, x + it[4] / 2)); x += it[4] + base * .34
    return out

def captions(ctx, t, y=1480, base=_CAP_BASE, pages=PAGES, x=540):
    """the engine's caption look (word pop, gradient emphasis) with the measured onsets. Screen layer."""
    for p in pages:
        if not (p['a'] <= t < p['z']): continue
        ws = p['words']
        for k, (it, cx) in enumerate(_layout(ws, base)):
            txt, t0, em, sz, _ = it
            if t < t0 - .02: continue
            t1 = ws[k + 1][1] if k + 1 < len(ws) else p['z']
            lt = t - t0 + .02; s = .72 + .28 * back(lt / .16, 1.4)
            if t0 - .02 <= t < t1 + .04: s *= 1.03
            img, _ = E.word_img(txt, sz, 'grad' if em else 'white')
            a = 1.0
            if lt < .05: a = lt / .05
            if p['z'] - t < .06: a *= max(0, (p['z'] - t) / .06)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, x + cx, y, alpha=a)

# ------------------------------------------------------------------------------------------------ callouts
def label_pill(words, size=78, cta=0.0, pad_x=40, pad_y=22, icon=None):
    """frosted label pill with the label words (list of (text, style)); cta>0 morphs it into a lit CTA button
    (LUMARC gradient fill + glow). Returns RGBA (glass layer friendly)."""
    key = ('pill', tuple(words), size, round(cta, 2), icon)
    def mk():
        f = E.font(size); gap = size * .30
        ims = [E.word_img(txt, size, st)[0] for txt, st in words]
        pads = [E.word_img(txt, size, st)[1] for txt, st in words]
        tws = []
        for txt, st in words:
            l, t_, r, b = f.getbbox(txt); tws.append(r - l)
        iw = int(size * .78) if icon else 0
        tw = sum(tws) + gap * (len(words) - 1) + (iw + gap * .8 if icon else 0)
        l, t_, r, b = f.getbbox('ÁG'); th = b - t_
        w = int(tw + 2 * pad_x); h = int(th + 2 * pad_y + size * .10)
        G = 70                                               # room for the glow
        out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
        rad = h // 2
        if cta > 0.01:                                        # lit CTA button: glow + gradient body
            m = Image.new('L', out.size); ImageDraw.Draw(m).rounded_rectangle((G, G, G + w - 1, G + h - 1), rad, fill=255)
            glow = Image.new('RGBA', out.size, (130, 90, 255, 0))
            glow.putalpha(m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * .95 * cta)))
            out.alpha_composite(glow)
            body = E.gradient(w, h, E.GRAD).convert('RGBA')
            bm = Image.new('L', (w, h)); ImageDraw.Draw(bm).rounded_rectangle((0, 0, w - 1, h - 1), rad, fill=int(255 * cta))
            body.putalpha(bm); out.alpha_composite(body, (G, G))
            hl = Image.new('L', (w, h)); ImageDraw.Draw(hl).rounded_rectangle((3, 3, w - 4, h // 2), rad - 3, fill=int(46 * cta))
            out.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [hl]), (G, G))
        gp = E.glass_panel(w, h, radius=rad, alpha=.14 * (1 - cta) + .02, border=.55 + .3 * cta)
        out.alpha_composite(gp, (G, G))
        x = G + pad_x
        cy = G + h / 2
        if icon == 'play':
            r_ = iw / 2; cx_ = x + r_
            d = ImageDraw.Draw(out)
            d.ellipse((cx_ - r_, cy - r_, cx_ + r_, cy + r_), fill=(250, 249, 246, 235))
            tri = [(cx_ - r_ * .30, cy - r_ * .42), (cx_ - r_ * .30, cy + r_ * .42), (cx_ + r_ * .48, cy)]
            d.polygon(tri, fill=(106, 85, 255, 255))
            x += iw + gap * .8
        for im, pd, tw_ in zip(ims, pads, tws):
            out.alpha_composite(im, (int(x - pd), int(cy - im.height / 2)))
            x += tw_ + gap
        return out
    return C(key, mk)

def leader(size, A, B, k, col=(250, 249, 246), width=4, glow=True, elbow=None):
    """leader line from A to B (local px in an RGBA of `size`), drawn on to fraction k; optional elbow point."""
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    pts = [A] + ([elbow] if elbow is not None else []) + [B]
    segs = list(zip(pts[:-1], pts[1:])); Ls = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
    tot = sum(Ls) * clamp(k); path = [A]
    for (a, b), L in zip(segs, Ls):
        if tot <= 0: break
        u = min(1.0, tot / max(L, 1e-6)); path.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)); tot -= L
    if len(path) < 2: return im
    if glow:
        g = Image.new('L', size); ImageDraw.Draw(g).line(path, fill=255, width=width * 4, joint='curve')
        gl = Image.new('RGBA', size, (150, 110, 255, 0)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * .7)))
        im.alpha_composite(gl)
    ImageDraw.Draw(im).line(path, fill=col + (235,), width=width, joint='curve')
    return im

def dot(r=9, pulse=0.0, col=(250, 249, 246)):
    """anchor dot (white core, purple glow, optional expanding ring)."""
    key = ('dot', r, round(pulse, 2))
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
    return C(key, mk)

def callout(ctx, t, t0, A, L, pill, layer='front', elbow=None, alpha=1.0, glass=10, dot_r=9, side=None):
    """architectural callout: dot on the 3-D anchor A, leader drawn to the label centre L, pill pops at the end.
    Timeline: t0 = the word (dot + pulse), leader 0..0.16 s, pill pops on t0 (anchored to the leader end)."""
    if t < t0 - .01 or alpha <= .01: return
    lt = t - t0
    hw = pill.width / 2 - 70                                  # pill has a 70 px glow margin
    L = (min(max(L[0], 80 + hw), 1000 - hw), L[1])
    # leader
    k = expo(lt / .16)
    x0 = int(min(A[0], L[0], (elbow or A)[0])) - 40; y0 = int(min(A[1], L[1], (elbow or A)[1])) - 40
    x1 = int(max(A[0], L[0], (elbow or A)[0])) + 40; y1 = int(max(A[1], L[1], (elbow or A)[1])) + 40
    if x1 - x0 > 4 and y1 - y0 > 4:
        ld = leader((x1 - x0, y1 - y0), (A[0] - x0, A[1] - y0), (L[0] - x0, L[1] - y0), k,
                    elbow=None if elbow is None else (elbow[0] - x0, elbow[1] - y0))
        ctx.add(layer, ld, x0, y0, center=False, alpha=alpha)
    ctx.add(layer, dot(dot_r, clamp(lt / .5)), A[0], A[1], alpha=alpha)
    # pill (scale pop from 0.6 with overshoot, slight rise)
    s = .55 + .45 * back(lt / .22, 1.6)
    p = pill if abs(s - 1) < .01 else pill.resize((max(1, int(pill.width * s)), max(1, int(pill.height * s))), Image.BILINEAR)
    a = clamp(lt / .07) * alpha
    ctx.add(layer, p, L[0], L[1] + 10 * (1 - eout(lt / .22)), glass=glass if a > .6 else 0, alpha=a)

def grow_pill(words, t, size=74, cta=0.0, pad_x=40, pad_y=22):
    """a label pill that GROWS word by word: words = [(text, onset)]; each word pops in on its onset and the pill
    widens to fit it (expo-out 0.14 s).  cta 0..1 lights it as the LUMARC CTA button.  Returns (RGBA, glow margin G)
    — the pill's left edge sits at G in the image (it grows to the right)."""
    f = E.font(size); gap = size * .30
    LEAD = .05                                           # the pill starts widening just before the word lands
    vis = [(txt, t0) for txt, t0 in words if t >= t0 - .01]
    if not vis: return None, 0
    tws = []
    for txt, _ in words:
        l, t_, r, b = f.getbbox(txt); tws.append(r - l)
    def content_w(n): return sum(tws[:n]) + gap * (n - 1)
    grow = [(j, t0) for j, (txt, t0) in enumerate(words) if j > 0 and t >= t0 - LEAD]
    n = len(vis)
    if grow:
        j, t0 = grow[-1]; k = expo((t - (t0 - LEAD)) / .14)
        cw = lerp(content_w(j), content_w(j + 1), k)
    else: cw = content_w(1)
    l, t_, r, b = f.getbbox('ÁG'); th = b - t_
    w = int(cw + 2 * pad_x); h = int(th + 2 * pad_y + size * .10); G = 80; rad = h // 2
    out = Image.new('RGBA', (int(content_w(len(words)) + 2 * pad_x) + 2 * G, h + 2 * G), (0, 0, 0, 0))
    if cta > .01:
        m = Image.new('L', out.size); ImageDraw.Draw(m).rounded_rectangle((G, G, G + w - 1, G + h - 1), rad, fill=255)
        glow = Image.new('RGBA', out.size, (130, 90, 255, 0))
        glow.putalpha(m.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * cta)))
        out.alpha_composite(glow)
        body = E.gradient(w, h, E.GRAD).convert('RGBA')
        bm = Image.new('L', (w, h)); ImageDraw.Draw(bm).rounded_rectangle((0, 0, w - 1, h - 1), rad, fill=int(255 * cta))
        body.putalpha(bm); out.alpha_composite(body, (G, G))
        hl = Image.new('L', (w, h)); ImageDraw.Draw(hl).rounded_rectangle((4, 4, w - 5, h // 2), rad - 4, fill=int(50 * cta))
        out.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 255)] * 3 + [hl]), (G, G))
    out.alpha_composite(E.glass_panel(w, h, radius=rad, alpha=.14 * (1 - cta) + .03, border=.55 + .35 * cta), (G, G))
    x = G + pad_x; cy = G + h / 2
    for j, (txt, t0) in enumerate(vis):
        im, pd = E.word_img(txt, size, 'white')
        lt = t - t0; s_ = .6 + .4 * back(lt / .16, 1.8)
        if abs(s_ - 1) > .01: im = im.resize((max(1, int(im.width * s_)), max(1, int(im.height * s_))), Image.BILINEAR)
        a = clamp(lt / .05)
        if a < 1: im = E.fade(im, a)
        cx_ = x + tws[j] / 2
        out.alpha_composite(im, (int(cx_ - im.width / 2), int(cy - im.height / 2)))
        x += tws[j] + gap
    return out, G

def glow_spot(r, col=(154, 77, 255), a=1.0):
    """soft additive-looking light halo (RGBA)."""
    def mk():
        R = int(r); g = Image.new('L', (2 * R, 2 * R)); ImageDraw.Draw(g).ellipse((R * .55, R * .55, R * 1.45, R * 1.45), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(R * .28))
        im = Image.new('RGBA', g.size, col + (0,)); im.putalpha(g); return im
    im = C(('spot', int(r), col), mk)
    return E.fade(im, a) if a < 1 else im

def ripple_ring(r, k, col=(250, 249, 246)):
    """tap ripple: an expanding ring (k 0..1)."""
    R = int(r) + 6; im = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0))
    rr = r * (.15 + .85 * eout(k)); a = int(230 * (1 - k) ** 1.6)
    ImageDraw.Draw(im).ellipse((R - rr, R - rr, R + rr, R + rr), outline=col + (a,), width=max(2, int(6 * (1 - k)) + 2))
    return im

def flare(w=620, h=26, col=(255, 210, 150)):
    """anamorphic light streak (a light switching on, seen through a lens)."""
    def mk():
        x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]; y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
        a = np.exp(-(x / .38) ** 2) * np.exp(-(y / .22) ** 2) + .5 * np.exp(-(x / .9) ** 2) * np.exp(-(y / .10) ** 2)
        core = np.exp(-(x / .05) ** 2 - (y / .5) ** 2) * .8
        A = np.clip(a + core, 0, 1)
        im = Image.new('RGBA', (w, h), col + (0,)); im.putalpha(Image.fromarray((A * 255).astype(np.uint8))); return im
    return C(('flare', w, h, col), mk)

def jump_t(i):
    """timeline time of the first frame showing segment i's pose (the avatar picks the nearest 25 fps frame, so the
    jump can land one 30 fps frame before the segment start)."""
    t0 = E.TL[i]['t0']; k = int(round(t0 * 25))
    j = next(j for j in range(int(t0 * 30) - 3, int(t0 * 30) + 4) if E.Avatar._k_of(j / 30) >= k)
    return j / 30

def pause_chip(h=112):
    """frosted glass chip with a pause glyph (the freeze reads instantly, even on mute)."""
    def mk():
        w = h; G = 50; out = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
        m = Image.new('L', out.size); ImageDraw.Draw(m).ellipse((G, G, G + w - 1, G + h - 1), fill=255)
        sh = Image.new('RGBA', out.size, (4, 4, 10, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .5)))
        out.alpha_composite(sh, (0, 6))
        gp = E.glass_panel(w, h, radius=h // 2, alpha=.16, border=.6); out.alpha_composite(gp, (G, G))
        d = ImageDraw.Draw(out); bw, bh = h * .13, h * .38; cx, cy = G + w / 2, G + h / 2
        for sx in (-1, 1):
            x0 = cx + sx * h * .12 - bw / 2
            d.rounded_rectangle((x0, cy - bh / 2, x0 + bw, cy + bh / 2), bw * .3, fill=(250, 249, 246, 245))
        return out
    return C(('pause', h), mk)

# ------------------------------------------------------------------------------------------------ bench
if __name__ == '__main__':
    import time
    t0, t1, step = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    F = E.Film(t0); ts = []; n = int(round((t1 - t0) / step))
    for i in range(n):
        t = round(t0 + i * step, 4); a = time.time(); F.frame(t); ts.append(time.time() - a)
    print(f'frames {n}  mean {np.mean(ts):.3f}  p95 {np.percentile(ts, 95):.3f}  max {np.max(ts):.3f}')
