"""s06 — FIRST IMPRESSION (25.24–28.92).  "They only see your content. Your content is your first impression."

TL16  the s05 triptych (food / service / skill glass panes, rebuilt with s05's own pane code so the handoff is
      seamless) cracks from the centre outwards — radial/concentric fracture lines that REFRACT the image (each cell is
      displaced a few px, dark 3 px fissure + 1 px glint) — and on "They" the glass SHATTERS toward the lens: thick
      bevelled shards (one-side lit edges, rotating specular, slight 3D tilt, refraction offset) spin, fall and fade,
      revealing him in a new framing while the cold grade thaws.
      "CONTENT": the frame snaps into a rounded 4:5 feed post (IG-style header slides in, the world outside dims and
      blurs) and a phone-screen glare sweeps the post.
TL17  SIGNATURE DOLLY ZOOM: cut wide; he is locked at exactly the same size while the studio (crisp plate) rushes at
      the lens behind him (background-only zoom 1.0 -> 1.7, ease-in), with radial speed streaks emanating from behind
      his head and an edge zoom-blur ramp peaking just before "FIRST". BOOM on "FIRST": giant gradient FIRST rises
      BEHIND him with glow + exposure punch + shake; IMPRESSION lands on its own word under it, his head overlapping.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import s05_problem as P5

START, END = E.span(16, 17)                   # 25.24 – 28.92
T16, T17 = E.TL[16]['t0'], E.TL[17]['t0']
# onsets measured on the voice track
W_THEY, W_CONTENT, W_FIRST, W_IMPRESSION = 25.30, 26.41, 27.86, 28.29
TS = 25.30                                    # shards start flying (two frames of spreading cracks first)

CUES = [
    (T16 + .01, 'glass', {'gain': -4}),        # cracks spread through the panes
    (TS, 'shatter', {}),                       # triptych breaks on "They"
    (TS + .03, 'whoosh', {'gain': -4}),        # shards fly at the lens
    (W_CONTENT - .03, 'shutter', {}),          # frame snaps into a feed post
    (W_CONTENT + .06, 'swipe', {'gain': -10}), # glare sweep
    (T17 + .02, 'riser', {'to': W_FIRST}),     # dolly zoom builds
    (W_FIRST, 'boom', {}),                     # FIRST
    (W_IMPRESSION, 'impact', {'gain': -7}),    # IMPRESSION
]

clamp, eout, ein, back = E.clamp, E.eout, E.ein, E.back
W, H = E.W, E.H
lerp, smooth, cam_for_face, graded = P5.lerp, P5.smooth, P5.cam_for_face, P5.graded
COLD = (.6, .92, (.92, .98, 1.1))
def C(k, fn): return E.cached(('s06',) + (k if isinstance(k, tuple) else (k,)), fn)


def cap_scrim():
    """soft night-blue capsule shadow that sits behind the caption line during the shatter."""
    def mk():
        w, h = 980, 330; m = Image.new('L', (w, h))
        ImageDraw.Draw(m).rounded_rectangle((150, 115, w - 150, h - 115), 50, fill=235)
        im = Image.new('RGBA', (w, h), (6, 5, 16, 0)); im.putalpha(m.filter(ImageFilter.GaussianBlur(42))); return im
    return C('capscrim', mk)


# ================================================================ fracture geometry
IMPACT = (540., 760.)
SS = 4                                        # supersampling for anti-aliased shard masks


def pane_rects():
    return [(x, y, w, h) for k, x, y, w, h, *_ in P5.pane_states(P5.END - 1e-3)]


def clip_poly(poly, x0, y0, x1, y1):
    """Sutherland–Hodgman clip of a polygon to an axis-aligned rectangle."""
    def clip(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia: out.append(inter(a, b))
                out.append(b)
            elif ia: out.append(inter(a, b))
        return out
    def ix(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / ((b[0] - a[0]) or 1e-6))
    def iy(yc):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / ((b[1] - a[1]) or 1e-6), yc)
    pts = poly
    for inside, inter in ((lambda p: p[0] >= x0, ix(x0)), (lambda p: p[0] <= x1, ix(x1)),
                          (lambda p: p[1] >= y0, iy(y0)), (lambda p: p[1] <= y1, iy(y1))):
        if not pts: break
        pts = clip(pts, inside, inter)
    return pts


def pane_mask_full():
    """anti-aliased union mask of the three rounded panes (full frame)."""
    def mk():
        m = Image.new('L', (W * 2, H * 2)); d = ImageDraw.Draw(m); r = P5.R_OUT * P5.trip_scale(P5.END) * 2
        for x, y, w, h in pane_rects(): d.rounded_rectangle((x * 2, y * 2, (x + w) * 2 - 1, (y + h) * 2 - 1), r, fill=255)
        return np.asarray(m.resize((W, H), Image.LANCZOS))
    return C('pmask', mk)


def cells():
    """radial + concentric fracture cells around the impact point (like real tempered glass), outer cells split."""
    def mk():
        rng = np.random.default_rng(23)
        n = 15
        ang = np.sort((np.arange(n) + rng.uniform(-.32, .32, n)) * 2 * math.pi / n)
        radii = [0, 60, 150, 290, 480, 740, 1080, 1600, 2400]
        # per-vertex jittered radius (cracks wander)
        R = [[r * (1 + rng.uniform(-.16, .16)) if r else 0 for _ in range(n)] for r in radii]
        def P(j, i): i %= n; return (IMPACT[0] + math.cos(ang[i]) * R[j][i], IMPACT[1] + math.sin(ang[i]) * R[j][i] * 1.1)
        polys = []
        for j in range(len(radii) - 1):
            for i in range(n):
                if j == 0: polys.append([IMPACT, P(1, i), P(1, i + 1)]); continue
                a, b, c, d = P(j, i), P(j, i + 1), P(j + 1, i + 1), P(j + 1, i)
                if j >= 3 and rng.random() < .75:     # split outer cells along a wandering diagonal
                    if rng.random() < .5: polys += [[a, b, c], [a, c, d]]
                    else: polys += [[a, b, d], [b, c, d]]
                else: polys.append([a, b, c, d])
        return polys
    return C('cells', mk)


def shards():
    def mk():
        rng = np.random.default_rng(11); pm = pane_mask_full(); out = []
        for poly in cells():
            for (x, y, w, h) in pane_rects():
                q = clip_poly(poly, x, y, x + w, y + h)
                if len(q) < 3: continue
                xs, ys = [p[0] for p in q], [p[1] for p in q]
                x0, y0, x1, y1 = int(math.floor(min(xs))), int(math.floor(min(ys))), int(math.ceil(max(xs))) + 1, int(math.ceil(max(ys))) + 1
                if (x1 - x0) * (y1 - y0) < 300: continue
                m = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS))
                ImageDraw.Draw(m).polygon([((px - x0) * SS, (py - y0) * SS) for px, py in q], fill=255)
                m = np.asarray(m.resize((x1 - x0, y1 - y0), Image.LANCZOS)).astype(np.float32)
                m = m * pm[max(0, y0):y1, max(0, x0):x1][:m.shape[0], :m.shape[1]] / 255 if (x0 >= 0 and y0 >= 0) else m
                if m.max() < 40: continue
                cx, cy = float(np.mean(xs)), float(np.mean(ys))
                dx, dy = cx - IMPACT[0], cy - IMPACT[1]; dist = math.hypot(dx, dy) + 1
                out.append(dict(box=(x0, y0, x1, y1), mask=m.astype(np.uint8), poly=q, c=(cx, cy),
                                dir=(dx / dist, dy / dist), dist=dist,
                                v=rng.uniform(1500, 2600) * (1.25 - .5 * min(1, dist / 1000)),
                                rot=rng.uniform(-240, 240), tilt=rng.uniform(-9, 9), tilt0=rng.uniform(0, 3),
                                zs=rng.uniform(.5, 1.5), delay=min(.07, dist / 1000 * .07),
                                refr=(rng.uniform(-6, 6), rng.uniform(-6, 6)), ph=rng.uniform(0, 6.28)))
        return out
    return C('shards', mk)


def crack_art():
    """fissure network (supersampled): 3 px dark line + 1 px bright glint offset toward the light; with dist map."""
    def mk():
        S = 2; dk = Image.new('L', (W * S, H * S)); gl = Image.new('L', (W * S, H * S))
        dd, dg = ImageDraw.Draw(dk), ImageDraw.Draw(gl)
        rng = np.random.default_rng(5)
        for poly in cells():
            pts = [(x * S, y * S) for x, y in poly] + [(poly[0][0] * S, poly[0][1] * S)]
            dd.line(pts, fill=255, width=3 * S, joint='curve')
            for a, b in zip(pts[:-1], pts[1:]):      # glint brightness follows the fissure's angle to the light
                ang = math.atan2(b[1] - a[1], b[0] - a[0])
                f = (.3 + .7 * abs(math.sin(ang - math.atan2(LIGHT[1], LIGHT[0]))) ** 1.5) * rng.uniform(.6, 1)
                dg.line([(a[0] - 1.5 * S, a[1] - 1.5 * S), (b[0] - 1.5 * S, b[1] - 1.5 * S)], fill=int(255 * f), width=1 * S)
        dk = np.asarray(dk.resize((W, H), Image.LANCZOS), np.float32) / 255
        gl = np.asarray(gl.resize((W, H), Image.LANCZOS), np.float32) / 255
        pm = pane_mask_full().astype(np.float32) / 255
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dist = np.hypot(xx - IMPACT[0], (yy - IMPACT[1]) / 1.1)
        return dk * pm, gl * pm, dist
    return C('crack', mk)


def pane_layer(lab=0):
    """the s05 triptych at its final (END) state as a static RGBA layer (panes drawn over the cold, dimmed studio;
    alpha = the anti-aliased pane mask). Static, so the shards' content can be cached. lab=1 keeps the sense labels
    (s05 dissolves them over P5.LAB_OUT, so the flying shards carry none: "THEY" is the only text once it pops)."""
    def mk():
        bg = Image.blend(E.studio(), Image.new('RGB', (W, H), (0, 0, 0)), .2)
        bg = graded(bg, COLD[0], COLD[1], COLD[2]).convert('RGBA')
        st = [(k, x, y, w, h, 0., 0., land) for k, x, y, w, h, vx, vy, land in P5.pane_states(P5.END - 1e-3)]
        P5.draw_panes(bg, P5.END - 1e-3, states=st, lab_a=float(lab))
        bg.putalpha(Image.fromarray(pane_mask_full())); return bg
    return C(('players', lab), mk)


def triptych_frame(fr, t):
    a = P5.label_alpha(t)
    L = pane_layer(0) if a <= .004 else Image.blend(pane_layer(0), pane_layer(1), a)
    tf = fr.copy(); tf.alpha_composite(L); return tf


def cracked(src, t):
    """cracks racing out from the impact: each cell refracts (shifted by its own offset) inside the grown radius."""
    k = clamp((t - T16 + 1 / 30) / (TS - T16 + 1 / 30))
    Rr = 260 + 1900 * k ** 1.3
    out = src.copy()
    for s in shards():
        if s['dist'] > Rr: continue
        x0, y0, x1, y1 = s['box']; dx, dy = s['refr']
        piece = src.crop((int(x0 - dx), int(y0 - dy), int(x1 - dx), int(y1 - dy)))
        piece.putalpha(Image.fromarray(s['mask'])); E._paste(out, dict(img=piece, xy=(x0, y0), glass=0))
    dk, gl, dist = crack_art()
    reach = np.clip((Rr - dist) / 120, 0, 1)
    a = np.asarray(out.convert('RGB'), np.float32)
    a = a * (1 - (dk * reach * .6)[..., None])
    a = a + (gl * reach)[..., None] * np.array([240, 244, 255], np.float32) * 1.0
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def shift(a, dx, dy):
    """integer shift of a 2D array (zero fill)."""
    out = np.zeros_like(a); h, w = a.shape; dx, dy = int(round(dx)), int(round(dy))
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = a[ys, xs]; return out


LIGHT = (-.55, -.83)                          # light from the top-left (screen space)


def shard_sprite(src, s, ang, tiltc, thick, spec, q=1):
    """RGBA sprite of one shard in its LOCAL frame: refracted content, thickness bevel, one-side-lit edges, specular.
    q = 2 builds it at half resolution (flying shards: they move 30-90 px/frame, so the half-res layer reads as the
    same glass, and costs a quarter)."""
    x0, y0, x1, y1 = s['box']; dx, dy = s['refr']
    R = s.setdefault('r%d' % q, {})
    if 'piece' not in R:   # static (the pane layer never changes): cache content, mask, grids
        pc = src.crop((int(x0 - dx), int(y0 - dy), int(x1 - dx), int(y1 - dy))).convert('RGB'); mk = Image.fromarray(s['mask'])
        if q > 1:
            sz = (max(2, round(pc.width / q)), max(2, round(pc.height / q)))
            pc, mk = pc.resize(sz, Image.BOX), mk.resize(sz, Image.BOX)
        R['piece'] = np.asarray(pc, np.float32); R['m'] = np.asarray(mk, np.float32) / 255
        hh, ww = R['m'].shape; yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32); R['u'] = (xx * .7 + yy * .7) / max(1, (ww + hh) * .7)
    s = dict(s, **R)
    piece, m, u = s['piece'], s['m'], s['u']
    h, w = m.shape; pad = 10 // q; ls = 2.2 if q == 1 else 1.4
    # light direction in the shard's local frame (inverse rotation)
    r = math.radians(ang); c, si = math.cos(r), math.sin(r)
    lx, ly = c * LIGHT[0] + si * LIGHT[1], -si * LIGHT[0] + c * LIGHT[1]
    lit = np.clip(m - shift(m, -lx * ls, -ly * ls), 0, 1)            # edges facing the light
    shd = np.clip(m - shift(m, lx * ls, ly * ls), 0, 1)              # edges facing away
    # rotating specular sheen: a soft band across the shard whose strength follows the shard's orientation
    band = np.exp(-((u - (.5 + .35 * math.sin(ang * .05 + s['ph']))) / .18) ** 2) * spec
    rgb = piece * (1 - .1 * (1 - tiltc)); rgb += band[..., None] * 105
    rgb *= (1 - shd * .55)[..., None]; rgb += (lit * 229.5)[..., None]
    if 'a8' not in R:      # static: alpha + the dark glass body (tinted by what it carries)
        R['a8'] = s['a8'] = (m * 255 + .5).astype(np.uint8)
        body = np.empty((h, w, 4), np.uint8); body[..., :3] = np.clip(piece * .28 + np.array([18, 18, 40], np.float32), 0, 255)
        body[..., 3] = (m * 225 + .5).astype(np.uint8); R['body'] = s['body'] = Image.fromarray(body, 'RGBA')
    top = np.empty((h, w, 4), np.uint8); top[..., :3] = np.clip(rgb, 0, 255); top[..., 3] = s['a8']
    # canvas with thickness (dark glass body offset along the fall direction, in local coords), lit face on top
    tx, ty = (c * thick[0] + si * thick[1]) / q, (-si * thick[0] + c * thick[1]) / q
    Cw, Ch = w + 2 * pad, h + 2 * pad
    out = Image.new('RGBA', (Cw, Ch), (0, 0, 0, 0))
    ox, oy = pad + int(round(tx)), pad + int(round(ty))
    if 0 <= ox and ox + w <= Cw and 0 <= oy and oy + h <= Ch: out.paste(s['body'], (ox, oy))
    out.alpha_composite(Image.fromarray(top, 'RGBA'), (pad, pad))
    return out, pad


def affine2(img, sx, sy, ang_deg):
    """non-uniform scale (local) then rotate, in one bicubic resample; output expanded to fit."""
    w, h = img.size; r = math.radians(ang_deg); c, si = math.cos(r), math.sin(r)
    M = np.array([[c * sx, -si * sy], [si * sx, c * sy]])
    corners = np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]]) @ M.T
    ow, oh = int(np.ptp(corners[:, 0])) + 3, int(np.ptp(corners[:, 1])) + 3
    Mi = np.linalg.inv(M); ox, oy = ow / 2, oh / 2
    a, b, d, e = Mi[0, 0], Mi[0, 1], Mi[1, 0], Mi[1, 1]
    return img.transform((ow, oh), Image.AFFINE, (a, b, w / 2 - a * ox - b * oy, d, e, h / 2 - d * ox - e * oy), Image.BILINEAR)


def shatter(fr, t):
    """fr = the revealed world (graded). returns the frame with cracks (before TS) or flying shards."""
    if t < TS: return cracked(triptych_frame(fr, t), t)
    src = pane_layer()
    u = t - TS
    out = fr.copy(); half = None
    for s in sorted(shards(), key=lambda s: s['zs']):
        uu = max(0., u - s['delay'])
        k = 1 - math.exp(-uu * 3.0)
        dist = s['v'] * k / 3.0
        zsc = min(2.5, 1 + s['zs'] * (uu * 1.5 + uu * uu * 1.6))        # toward the lens
        cx = s['c'][0] + s['dir'][0] * dist * (1 + .5 * (zsc - 1)) + s['refr'][0]
        cy = s['c'][1] + s['dir'][1] * dist * (1 + .5 * (zsc - 1)) + 2400 * uu * uu + s['refr'][1]
        ang = s['rot'] * uu
        tilt = s['tilt0'] * .15 + s['tilt'] * uu                           # radians of 3D tilt about the local y axis
        tiltc = abs(math.cos(tilt)) * .8 + .2
        a = clamp(1 - (uu - .32) / .16)
        if a <= .02: continue
        x0, y0, x1, y1 = s['box']; pw, ph = x1 - x0, y1 - y0
        rad = math.hypot(pw, ph) * zsc / 2
        if cx + rad < 0 or cx - rad > W or cy + rad < 0 or cy - rad > H: continue
        if uu <= 0:   # not yet released: sits in place (refracted)
            if 'static' not in s: s['static'] = shard_sprite(src, s, 0, 1, (0, 0), .0)   # identical every frame
            spr, pad = s['static']
            E._paste(out, dict(img=spr, xy=(x0 - pad, y0 - pad), glass=0)); continue
        th = 3 + 3 * min(1, uu / .12) * zsc
        fall = (s['dir'][0] * .6, s['dir'][1] * .6 + .8); fn = math.hypot(*fall) or 1
        spec = .25 + .75 * max(0, math.cos(math.radians(ang) * 2 + s['ph'])) ** 6
        q = 2 if uu > .04 else 1                                           # in flight -> half-res layer
        spr, pad = shard_sprite(src, s, ang, tiltc, (fall[0] / fn * th, fall[1] / fn * th), spec, q)
        spr = affine2(spr, zsc * tiltc, zsc, ang)
        if a < 1: spr = E.fade(spr, a)
        if q == 1:
            E._paste(out, dict(img=spr, xy=(int(cx - spr.width / 2), int(cy - spr.height / 2)), glass=0)); continue
        if half is None: half = Image.new('RGBA', (W // 2, H // 2), (0, 0, 0, 0))
        E._paste(half, dict(img=spr, xy=(int(cx / 2 - spr.width / 2), int(cy / 2 - spr.height / 2)), glass=0))
    if half is not None: out.alpha_composite(half.resize((W, H), Image.BILINEAR))
    return out


# ================================================================ "content": the frame becomes a feed post
CARD = (90, 330, 990, 1455)                   # 4:5 image area (900 x 1125); header top 234 — caption fits under it
HDR = 96


def header_art():
    def mk():
        w = CARD[2] - CARD[0]; im = Image.new('RGBA', (w, HDR), (0, 0, 0, 0))
        m = Image.new('L', (w, HDR + 40)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, HDR + 39), 34, fill=255)
        body = Image.new('RGBA', (w, HDR), (16, 16, 22, 255)); body.putalpha(m.crop((0, 0, w, HDR))); im.alpha_composite(body)
        d = ImageDraw.Draw(im)
        ring = E.gradient(64, 64, E.GRAD).convert('RGBA'); rm = Image.new('L', (64 * 4, 64 * 4))
        ImageDraw.Draw(rm).ellipse((0, 0, 255, 255), fill=255); ImageDraw.Draw(rm).ellipse((16, 16, 239, 239), fill=0)
        ring.putalpha(rm.resize((64, 64), Image.LANCZOS)); im.alpha_composite(ring, (24, 16))
        av = Image.new('L', (52 * 4, 52 * 4)); ImageDraw.Draw(av).ellipse((0, 0, 207, 207), fill=255)
        avc = Image.new('RGBA', (52, 52), (58, 60, 84, 255)); avc.putalpha(av.resize((52, 52), Image.LANCZOS)); im.alpha_composite(avc, (30, 22))
        d.text((104, 18), 'yourbusiness', font=E.font(34, 700), fill=(242, 242, 247))
        d.text((104, 56), 'Original audio', font=E.font(24, 400), fill=(160, 160, 172))
        for i in range(3): d.ellipse((w - 70 + i * 16, 44, w - 62 + i * 16, 52), fill=(225, 225, 232))
        return im
    return C('hdr', mk)


def round_mask(w, h, r):
    def mk():
        m = Image.new('L', (w * 3, h * 3)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), r * 3, fill=255)
        return m.resize((w, h), Image.LANCZOS)
    return C(('rm', w, h, int(r)), mk)


def glare(fr, p):
    """diagonal phone-screen glare at progress p (0..1), additive."""
    if not 0 < p < 1: return fr
    S = 4; sw, sh = W // S, H // S
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32) * S
    u = xx * .55 + yy * .83
    c = -300 + p * (W * .55 + H * .83 + 600)
    a = np.exp(-((u - c) / 120) ** 2) * .30 + np.exp(-((u - c - 210) / 26) ** 2) * .26
    a *= math.sin(math.pi * p) ** .5
    A = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    fr = fr.copy(); fr.paste(Image.new('RGBA', (W, H), (240, 244, 255, 255)), (0, 0), A); return fr


def post_card(fr, t):
    k = P5.expo((t - W_CONTENT + .03) / .2)
    if k <= 0: return fr
    # outside: the same world, blurred + dimmed like a feed behind the post
    bg = fr.convert('RGB').resize((W // 6, H // 6), Image.BOX).filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    bg = Image.fromarray((np.asarray(bg, np.float32) * lerp(1, .32, k)).astype(np.uint8)).convert('RGBA')
    x0, y0, x1, y1 = [lerp(a, b, k) for a, b in zip((0, 0, W, H), (CARD[0], CARD[1] - HDR, CARD[2], CARD[3]))]
    img_top = y0 + HDR * k
    s = lerp(1, (CARD[2] - CARD[0]) / W * 1.06, k)                     # the frame scales into the post
    cy = (img_top + y1) / 2
    inner = E.zoom(fr.convert('RGB'), s, (540, 860), dx=0, dy=cy - 860)
    inner = glare(inner.convert('RGBA'), (t - W_CONTENT - .06) / .5)
    iw, ih = int(round(x1 - x0)), int(round(y1 - img_top))
    crop = inner.crop((int(round(x0)), int(round(img_top)), int(round(x0)) + iw, int(round(img_top)) + ih))
    out = bg
    # soft shadow under the card
    q = 4; sh = Image.new('L', (W // q, H // q))                      # shadow at quarter res (blur 30 -> 7.5)
    ImageDraw.Draw(sh).rounded_rectangle((x0 / q, (y0 + 20) / q, x1 / q, (y1 + 20) / q), 34 / q, fill=int(200 * k))
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(7.5)).resize((W, H), Image.BILINEAR))
    r = lerp(0, 34, k)
    full = Image.new('RGBA', (iw, int(round(y1 - y0))), (16, 16, 22, 255))
    full.paste(crop, (0, int(round(img_top - y0))))
    if k > .02:
        hd = header_art()
        if hd.width != iw: hd = hd.resize((iw, int(HDR * iw / hd.width)), Image.BILINEAR)
        ha = clamp((t - W_CONTENT - .02) / .14); hy = int(-24 * (1 - eout(ha)))
        hdr = E.fade(hd, ha)
        hcan = Image.new('RGBA', full.size, (0, 0, 0, 0)); hcan.alpha_composite(hdr, (0, max(0, hy)) if hy >= 0 else (0, 0))
        full.alpha_composite(hcan)
    m = round_mask(full.width, full.height, max(1, r)) if r > 1 else Image.new('L', full.size, 255)
    out.paste(full, (int(round(x0)), int(round(y0))), m)
    bd = Image.new('RGBA', full.size, (0, 0, 0, 0)); ImageDraw.Draw(bd).rounded_rectangle((0, 0, full.width - 1, full.height - 1), r, outline=(255, 255, 255, int(40 * k)), width=2)
    out.alpha_composite(bd, (int(round(x0)), int(round(y0))))
    return out


# ================================================================ dolly zoom
def sharp_plate():
    def mk():
        import os
        p = os.path.join(E.SRC, 'studio_plate_sharp.png')
        im = Image.open(p).convert('RGB') if os.path.exists(p) else E.studio()
        return im.filter(ImageFilter.UnsharpMask(4, 120, 2))
    return C('plate', mk)


def bgz(t):
    """background-only zoom: accelerates into FIRST (ease-in), kicks on the boom, then keeps drifting."""
    x = clamp((t - T17) / (W_FIRST - T17))
    a = 1 + .95 * x ** 1.7
    if t >= W_FIRST: a += .1 * eout((t - W_FIRST) / .3) + .05 * smooth((t - W_FIRST - .3) / 1.0)
    return a


def _zoom_box(im, z, ax, ay, size):
    """im scaled by z around (ax, ay) (in im's own pixels) -> `size`; a box resize (3x faster than an affine)."""
    w, h = im.size; bw, bh = w / z, h / z; x0, y0 = ax - ax / z, ay - ay / z
    return im.resize(size, Image.BILINEAR, box=(x0, y0, x0 + bw, y0 + bh))


def dolly_bg(z, speed):
    st = sharp_plate()
    im = _zoom_box(st, z, 540, 700, (W, H))
    if speed > .15:   # a touch of radial motion blur on the background only (the smeared copy is built at half res)
        z2 = z * (1 + min(.03, speed * .02))
        sm = C('plate_half', lambda: st.resize((W // 2, H // 2), Image.BOX))
        im2 = _zoom_box(sm, z2, 270, 350, (W // 2, H // 2))
        im = Image.blend(im, im2.resize((W, H), Image.BILINEAR), .5)
    return im


def streaks(t, amt):
    """~30 thin radial speed lines emanating from behind his head (output space == world space at this camera)."""
    if amt < .02: return None
    S = 2; im = Image.new('L', (W // S, H // S)); d = ImageDraw.Draw(im)
    cx, cy = 540 / S, 700 / S
    rng = np.random.default_rng(3)
    for i in range(46):
        th = -math.pi * 1.12 + (i + rng.uniform(-.45, .45)) / 46 * math.pi * 1.24;   # upper fan, around his head
        sp = rng.uniform(.6, 1.4); L = rng.uniform(160, 420)
        ph = rng.uniform(0, 1); wd = 1 if rng.random() < .7 else 2
        q = (t * 2.0 * sp + ph) % 1.0
        r0 = 240 + q * 1100; L *= .5 + q                                  # lines stretch as they fly out
        a0 = min(1, amt * rng.uniform(.7, 1.1) * math.sin(math.pi * q) ** .5)
        for k in range(4):   # tail faint -> head bright
            ra, rb = r0 + L * k / 4, r0 + L * (k + 1) / 4
            p0 = (cx + math.cos(th) * ra / S, cy + math.sin(th) * ra * 1.15 / S)
            p1 = (cx + math.cos(th) * rb / S, cy + math.sin(th) * rb * 1.15 / S)
            d.line([p0, p1], fill=int(255 * a0 * (k + 1) / 4), width=wd)
    im = im.filter(ImageFilter.GaussianBlur(.4)).resize((W, H), Image.BILINEAR)
    out = Image.new('RGBA', (W, H), (215, 205, 255, 0)); out.putalpha(im); return out


_R = None
def edge_mask():
    def mk():
        yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32) * 2
        r = np.sqrt(((xx - 540) / 620) ** 2 + ((yy - 760) / 980) ** 2)
        return np.clip((r - .55) / .5, 0, 1)
    return C('edge', mk)


def edge_mask_img(half):
    def mk():
        m = Image.fromarray((edge_mask() * 255).astype(np.uint8))
        return m if half else m.resize((W, H), Image.BILINEAR)
    return C(('edge_img', half), mk)


def edge_zoom_blur(fr, amt):
    """radial zoom smear on the frame edges (half res, PIL-only: 3 scaled copies averaged, masked by the edge ramp)."""
    if amt < .03: return fr
    sm = fr.convert('RGB').resize((W // 2, H // 2), Image.BILINEAR); w, h = sm.size
    z = [_zoom_box(sm, 1 + amt * .035 * i, 270, 380, (w, h)) for i in (1, 2, 3)]
    acc = Image.blend(Image.blend(sm, z[0], .5), Image.blend(z[1], z[2], .5), .5)
    a = min(1., amt); lut = [int(v * a + .5) for v in range(256)]
    small = Image.composite(acc, sm, edge_mask_img(True).point(lut))
    out = fr.convert('RGB'); out.paste(small.resize((W, H), Image.BILINEAR), (0, 0), edge_mask_img(False).point(lut))
    return out                                       # the engine converts the wrap result to RGBA


# ================================================================ FIRST IMPRESSION type
def type_art(text, size, track, fit):
    def mk():
        m = P5.tracked(text, size, 900, track)
        if m.width > fit: m = m.resize((fit, int(m.height * fit / m.width)), Image.LANCZOS)
        pad = int(m.height * .6)
        M = Image.new('L', (m.width + 2 * pad, m.height + 2 * pad)); M.paste(m, (pad, pad))
        out = Image.new('RGBA', M.size, (0, 0, 0, 0))
        glow = Image.new('RGBA', M.size, (120, 80, 255, 0)); glow.putalpha(M.filter(ImageFilter.GaussianBlur(m.height * .22)).point(lambda v: int(v * .85)))
        out.alpha_composite(glow)
        sh = Image.new('RGBA', M.size, (4, 4, 12, 0)); sh.putalpha(M.filter(ImageFilter.GaussianBlur(m.height * .06)).point(lambda v: int(v * .6)))
        out.alpha_composite(sh, (0, int(m.height * .04)))
        g = np.asarray(E.gradient(M.width, M.height, E.GRAD_LIGHT), np.float32)
        v = np.linspace(1.18, .9, M.height)[:, None, None]
        g = Image.fromarray(np.clip(g * v, 0, 255).astype(np.uint8)).convert('RGBA'); g.putalpha(M); out.alpha_composite(g)
        return out, m.width
    return C(('type', text, size, track, fit), mk)


def rise(img, k, blur_from=14, scale_from=1.1):
    if k <= 0: return None
    e = eout(k); s = scale_from + (1 - scale_from) * e
    w, h = img.size
    im = img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BILINEAR) if abs(s - 1) > .005 else img
    r = blur_from * (1 - e) ** 2
    if r > .4: im = im.filter(ImageFilter.GaussianBlur(r))
    return E.fade(im, clamp(k * 3))


# ================================================================ draw
ZD = 1.03                                      # dolly camera (constant: he never changes size)
AY = 90


def draw(ctx, lt, t):
    _draw(ctx, lt, t); P5.voice_captions(ctx, t)          # captions re-timed to the voice, current segment only


def _draw(ctx, lt, t):
    P = ctx.post
    if t < T17:
        # ------------------------------------------ TL16 "They only see your content."
        z = lerp(1.2, 1.26, smooth((t - T16) / 1.6))
        if t >= W_CONTENT - .03: z += .04 * eout((t - W_CONTENT + .03) / .2)
        ctx.cam = cam_for_face(z, 540, 720)
        ctx.bg_dim = .15
        thaw = smooth((t - TS - .15) / .6)
        sat, br = lerp(COLD[0], 1, thaw), lerp(COLD[1], 1, thaw); tint = tuple(lerp(c, 1, thaw) for c in COLD[2])
        u = t - TS
        if -.001 < u < .25:   # hit: shake + a short exposure punch (light, not a grey veil)
            k = clamp(1 - u / .25)
            ctx.cam['dx'] += 16 * k * math.sin(u * 90); ctx.cam['dy'] += 9 * k * math.cos(u * 70)
            P['bright'] = 1 + .3 * clamp(1 - u / .12) ** 2
        # "THEY" pops on the voice (25.29) right over the breaking glass; a soft dark scrim behind the caption line
        # keeps it legible while the shards stream through, and dissolves once they have cleared
        sk = clamp((t - TS + .07) / .06) * clamp(1 - (t - TS - .42) / .25)
        if sk > .01: ctx.add('screen', cap_scrim(), 540, ctx.cap_y + 4, alpha=.9 * sk)
        if t >= P5.page_end(16, 0): ctx.cap_y = 1546        # 'YOUR CONTENT.' page sits under the post card (glyphs ≈1506–1590)
        def wrap(fr):
            fr = graded(fr, sat, br, tint).convert('RGBA')
            if t < TS + .75: fr = shatter(fr, t)
            if t >= W_CONTENT - .03: fr = post_card(fr, t)
            return fr
        ctx.wrap = wrap
        P['vignette'] = .38
        return

    # ------------------------------------------ TL17 dolly zoom + FIRST IMPRESSION
    ctx.cam = dict(z=ZD, x=540., y=820., dx=0., dy=0., rot=0.)
    ctx.avatar['y'] = AY                                               # sits a little lower: the title owns the top
    z = bgz(t); speed = (bgz(t) - bgz(t - 1 / 30)) * 30                # bg zoom speed (per s)
    ctx.bg_img = dolly_bg(z, speed)
    ctx.bg_dim = .1 + .18 * smooth((t - T17) / (W_FIRST - T17))
    build = clamp((t - T17) / (W_FIRST - T17))
    sk = clamp(speed / 1.3) * (1 if t < W_FIRST + .35 else clamp(1 - (t - W_FIRST - .35) / .3))
    ctx.add('behind', streaks(t, .95 * sk), 0, 0, center=False)    # world ~= output at this camera
    u = t - W_FIRST
    def o2w(ox, oy): return 540 + (ox - 540) / ZD, 820 + (oy - 820) / ZD
    if u >= -.02:
        ctx.captions = False
        k = clamp(1 - u / .3)
        ctx.cam['dx'] += 13 * k * math.sin(u * 85); ctx.cam['dy'] += 9 * k * math.cos(u * 64)
        e = clamp(1 - u / .14) ** 2 if u >= 0 else 0
        P['bright'] = 1 + .55 * e; P['flash'] = .05 * e; P['flash_col'] = (190, 170, 255)
        P['rgb'] = 6 * clamp(1 - u / .14)
        art, tw = type_art('FIRST', 300, 6, 820)
        F = rise(art, (u + .02) / .32, scale_from=1.09)              # 820 * 1.09 = 894 px: stays inside x 93–987
        if F is not None:
            F = F.resize((int(F.width / ZD), int(F.height / ZD)), Image.BILINEAR)
            ctx.add('behind', F, *o2w(540, 340 + 36 * (1 - eout((u + .02) / .32))))
        art, tw = type_art('IMPRESSION', 160, 4, 860)
        I = rise(art, (t - W_IMPRESSION + .02) / .3, scale_from=1.06)
        if I is not None:
            I = I.resize((int(I.width / ZD), int(I.height / ZD)), Image.BILINEAR)
            ctx.add('behind', I, *o2w(540, 512 + 28 * (1 - eout((t - W_IMPRESSION + .02) / .3))))
    if t >= W_IMPRESSION - .02:
        v = t - W_IMPRESSION
        P['rgb'] = max(P['rgb'], 4 * clamp(1 - v / .1))
    eb = build ** 2.2 if t < W_FIRST else clamp(1 - (t - W_FIRST) / .12)
    ctx.wrap = (lambda fr, eb=eb: edge_zoom_blur(fr, eb * 1.0)) if eb > .03 else None
    P['vignette'] = .45
