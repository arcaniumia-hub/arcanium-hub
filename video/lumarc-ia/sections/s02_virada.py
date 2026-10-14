"""s02 — A VIRADA (9.84–15.72): "Mas será que o problema é a IA… ou você só não encontrou alguém que saiba usar o
potencial máximo dela?"  (s01's last frame, 9.8333, already shows seg 3's pose -> s01 hands it to this draw.)

  9.8333 JUMP — HARD STOP: record scratch. Cut to him in front of the 25 identical reels, now FROZEN as a wall behind
        him (a pause glyph on every one), the wall stutters back and forth (scratch + RGB tear), the colour drains out
        of everything (he keeps a little life).
 10.30  "SERÁ": the camera snaps in on his face (3 frames, zoom blur on the world only).
 10.71  "PROblema": the frozen wall cracks (impact star, jolt).   11.42 "IA": second, bigger hit — the web spreads —
        and the word IA? DROPS in on two cables above his head and hangs there, swinging (the question hangs).
 12.05  the sign is yanked away; the camera eases back; a sleek LUMARC smoked-glass gauge "POTENCIAL DA IA" slides in
        idling at ~12 % (needle twitching) — the only colour in the grey world.  13.20 "ALGUÉM": the LUMARC mark on the
        gauge lights up (someone who knows how).
 13.38  "QUE SAIBA USAR": the needle climbs with his voice (readout counts), the cracks creep to the edges, violet light
        starts leaking through them from behind, tremor builds, the camera leans in.
 14.76  "MÁximo": the needle SLAMS into MÁX (overshoot, flash, shockwave) and the cracked slop wall SHATTERS toward the
        lens — behind it, the clean purple LUMARC studio; colour floods back.  15.16 "DELA?" + the held beat: glass
        settling, glints, gauge glowing.  15.52 the held beat is over: the gauge flies out (up), the camera starts an
        ease-in push toward his face; 15.70 (seg 5's pose already shows) = mid-push smear frame (Z 1.30 + radial
        blur) that s03's 15.73 close-up snap-in completes -> the jump hides inside one continuous push.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from sections import _A_kit as K

START, END = E.span(3, 4)                       # 9.84 – 15.72
W, H = E.W, E.H

# word onsets (timeline s) measured on src/tight16k.raw (5 ms STFT band envelopes + narrow-band formant view)
ONSETS = dict(
    # seg 3  "Mas será que o problema é a IA…"
    MAS=9.92, SERA=10.30, QUE3=10.59, O3=10.67, PROBLEMA=10.71, E3=11.15, A3=11.30, IA3=11.42, END3=11.83,
    # seg 4  "ou você só não encontrou alguém que saiba usar o potencial máximo dela?"
    OU4=12.11, VOCE4=12.25, SO4=12.46, NAO=12.55, ENCONTROU=12.76, ALGUEM=13.20, QUE4=13.38, SAIBA=13.46,
    USAR=13.93, O4=14.15, POTENCIAL=14.21, MAXIMO=14.73, MA4=14.76, DELA=15.16, END4=15.42,
)
Wd = ONSETS
lerp, clamp, eio, expo, eo = K.lerp, E.clamp, K.eio, K.expo, K.eo

T_CUT = K.CUT3                                  # 9.8333
T_SNAP = Wd['SERA']                             # 10.30 camera snaps in
T_C1, T_C2 = Wd['PROBLEMA'], Wd['IA3']          # cracks
T_SIGN_OUT = 12.03
T_BACK = 12.05                                  # camera eases back, gauge in
T_GAUGE = 12.17
T_CLIMB0, T_CLIMB1 = Wd['QUE4'], 14.68          # needle climbs with the voice
T_SLAM = Wd['MA4']                              # 14.76
T_END = K.CUT5                                  # 15.70 last frame = whip
T_OUT = 15.52                                   # held beat over: the gauge flies out, the camera starts pushing in
IMPACT = (336, 400)                             # on the wall plane (rest coords), up-left of his head

CUES = [
    (T_CUT, 'scratch', {'gain': 0}),
    (T_SNAP - .03, 'zoom', {'gain': -5}),
    (T_C1, 'crack', {'gain': -2}), (T_C1 + .01, 'glass', {'gain': -14}),
    (T_C2 - .06, 'whoosh', {'gain': -12}), (T_C2, 'crack', {'gain': 0}), (T_C2 + .04, 'thud', {'gain': -10}),
    (T_SIGN_OUT + .07, 'swoosh_up', {'gain': -10}),             # peak while the sign is yanked out
    (T_GAUGE, 'swoosh_up', {'gain': -9}), (T_GAUGE + .05, 'shimmer', {'gain': -14}),
    (T_CLIMB0, 'counter', {'dur': round(T_CLIMB1 - T_CLIMB0, 2), 'gain': -11}),
    (13.55, 'riser', {'to': T_SLAM, 'gain': -6}),
    (14.05, 'crack', {'gain': -12}), (14.42, 'crack', {'gain': -10}),
    (T_SLAM, 'impact', {'gain': 0}), (T_SLAM, 'sub', {'gain': -2}), (T_SLAM + .01, 'shatter', {'gain': 0}),
    (Wd['ALGUEM'], 'shimmer', {'gain': -16}),
    (Wd['DELA'], 'shimmer', {'gain': -13}),
    (T_OUT + .12, 'swoosh_up', {'gain': -15}),                            # the gauge clears the stage
]

# =========================================================================================== the frozen wall
def frozen_wall():
    """s01's 25 identical reels, frozen on the scratch frame (rest/screen coords of the wall plane), every one of them
    showing a pause glyph (everything froze)."""
    def mk():
        from sections import s01_hook as S1
        class _C: full = None
        c = _C(); S1.phones(c, T_CUT - 1 / 30)
        im = c.full.convert('RGBA')
        g = _pause_glyph(64)
        for (x, y, w) in S1._layout_stage(25):
            im.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        return im.convert('RGB')
    return E.cached('A2_frozen', mk)

def _pause_glyph(r):
    def mk():
        S = 4 * r; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((0, 0, S - 1, S - 1), fill=(0, 0, 0, 120))
        bw, bh = S * .12, S * .42
        for sx in (-1, 1):
            cx = S / 2 + sx * S * .12
            d.rounded_rectangle((cx - bw / 2, S / 2 - bh / 2, cx + bw / 2, S / 2 + bh / 2), bw * .3, fill=(255, 255, 255, 240))
        return im.resize((2 * r, 2 * r), Image.LANCZOS)
    return E.cached(('A2_pause', r), mk)

def drained_wall():
    return E.cached('A2_drained', lambda: K.grade(K.drained(frozen_wall(), 1.0), contrast=.92, bright=.86).filter(ImageFilter.GaussianBlur(2.2)))
def frozen_soft():
    return E.cached('A2_frozen_soft', lambda: frozen_wall().filter(ImageFilter.GaussianBlur(2.2)))

FR = K.GK.Fracture(center=IMPACT, size=(W, H), seed=11, radials=15,
                   hits=[(T_C1, 30, 300, .75, .05), (T_C2, 300, 620, .95, .07)],
                   race=(13.42, 1050.0), web=(14.40, .30))

def _group(i, j, k):
    if j <= 1: return ('a', j, k // 4)
    if j <= 5: return ('b', j, k // 2)
    return ('c', i)
SHAT = K.GK.Shatter(FR, seed=3, focal=1600., vp=(540., 900.), group=_group, wave=16000., speed=1.15)

def tau_at(t):
    """shatter sim time: explosive first frames, then slow motion."""
    u = t - T_SLAM
    if u < 0: return 0.0
    return .085 * (1 - math.exp(-u / .045)) + .62 * u

def leak_at(t):
    if t < T_C1: return 0.0
    base = .22 + .5 * math.exp(-(t - T_C1) / .12) + (.5 * math.exp(-(t - T_C2) / .14) + .12 if t >= T_C2 else 0)
    if t < T_CLIMB0: return base
    return base + 1.5 * K.ei(clamp((t - T_CLIMB0) / (T_SLAM - T_CLIMB0)), 2.2)

def studio_wall():
    return E.cached('A2_studio', lambda: E.studio().convert('RGBA'))

def wall_plane(t):
    """RGB(A) image of the wall plane at t (rest coords): frozen/drained/cracked -> shattering -> clean studio."""
    if t < T_SLAM:
        k = clamp((t - (T_CUT + .02)) / .2)
        base = drained_wall() if k >= 1 else Image.blend(frozen_soft(), drained_wall(), k)
        return FR.composite(base, t, refr=1.1, leak=leak_at(t), glint=2.2, sweep=(t - 10.6) * 520, sparks=1.0)
    tau = tau_at(t)
    st = studio_wall()
    if not SHAT.visible(tau, 0.0, 140.0): return st.convert('RGB')
    glass = E.cached('A2_glass_at_slam', lambda: FR.composite(drained_wall(), T_SLAM - .001, refr=.9, leak=leak_at(T_SLAM - .001), glint=1.3).convert('RGBA'))
    out = SHAT.render(st, glass, tau, focus_z=1600., dof=6., shutter_dtau=.012, alpha=1.0,
                      img_alpha=max(.22, 1 - tau / .09), spec_gain=1.6)
    return out.convert('RGB')

# =========================================================================================== camera
def shot_cam(t):
    A = K.Cam(1.04, 540, 935)
    Bc = K.Cam(1.32, 540, 905)
    Cc = K.Cam(1.05, 540, 815)
    if t < T_SNAP - .02:
        c = K.Cam(1.04 + .015 * clamp((t - T_CUT) / .45), 540, 935)
    elif t < T_BACK:
        k = expo((t - (T_SNAP - .02)) / .12)
        c = K.mix_cam(K.Cam(1.055, 540, 935), Bc, k); c.Z += .03 * clamp((t - T_SNAP) / 1.7)
    else:
        k = eo((t - T_BACK) / .3, 3)
        c = K.mix_cam(K.Cam(1.35, 540, 905), Cc, k)
        c.Z += .025 * eio((t - 12.35) / 1.05)          # slow creep while the gauge idles (never a locked-off second)
        c.Z += .055 * K.ei(clamp((t - T_CLIMB0) / (T_SLAM - T_CLIMB0)), 1.5)
        if t >= T_SLAM:
            u = t - T_SLAM; c.Z += .07 * math.exp(-u / .16) - .015 * clamp(u / .9) * 0
            c.Z += .02 * clamp((t - 15.0) / .7)
    if t >= T_OUT:                                  # after the held beat: the camera starts the push-in that s03's
        k = K.ei(clamp((t - T_OUT) / (T_END - T_OUT)), 3)          # snap-in close-up completes (last frame = mid-move)
        c = K.mix_cam(c, K.Cam(1.30, 540, 950), k)
    # jolts, tremor, slam shake
    for (t0, amp, tau) in ((T_C1, 9., .1), (T_C2, 14., .12), (T_SLAM, 24., .2)):
        dx, dy = K.shake(t, t0, amp, tau=tau, f=19., seed=t0); c.sx += dx; c.sy += dy
    if T_CLIMB0 < t < T_SLAM:
        a = 5.0 * K.ei(clamp((t - T_CLIMB0) / (T_SLAM - T_CLIMB0)), 2)
        c.sx += a * math.sin(t * 71); c.sy += a * .8 * math.sin(t * 89 + 1)
    if T_SLAM - .06 <= t < T_SLAM: c.Z -= .012 * (t - (T_SLAM - .06)) / .06       # anticipation
    return c

def scratch_dy(t):
    u = t - T_CUT
    if u < 0 or u > .2: return 0.0
    return 34 * math.sin(2 * math.pi * u / .07) * math.exp(-u / .06)

# =========================================================================================== the hanging "IA?"
SW_, SH_ = 500, 236
def sign_img():
    def mk():
        im = Image.new('RGBA', (SW_, SH_), (0, 0, 0, 0))
        m = Image.new('L', (SW_, SH_)); ImageDraw.Draw(m).rounded_rectangle((0, 0, SW_ - 1, SH_ - 1), 34, fill=226)
        bg = Image.new('RGBA', (SW_, SH_), (16, 15, 24, 0)); bg.putalpha(m); im.alpha_composite(bg)
        b = Image.new('L', (SW_, SH_)); ImageDraw.Draw(b).rounded_rectangle((2, 2, SW_ - 3, SH_ - 3), 32, outline=255, width=3)
        g = E.gradient(SW_, SH_, E.GRAD_LIGHT).convert('RGBA'); g.putalpha(b.point(lambda v: int(v * .8))); im.alpha_composite(g)
        f = E.font(176, 900)
        ia = Image.new('RGBA', (SW_, SH_), (0, 0, 0, 0)); d = ImageDraw.Draw(ia)
        wia = f.getlength('IA'); wq = f.getlength('?'); x0 = (SW_ - wia - wq - 8) / 2
        l, t_, r, bb = f.getbbox('IA'); y0 = (SH_ - (bb - t_)) / 2 - t_
        d.text((x0, y0), 'IA', font=f, fill=E.WHITE + (255,))
        qm = Image.new('L', (SW_, SH_)); ImageDraw.Draw(qm).text((x0 + wia + 8, y0), '?', font=f, fill=255)
        qg = E.gradient(SW_, SH_, E.GRAD_LIGHT).convert('RGBA'); qg.putalpha(qm)
        glow = Image.new('RGBA', (SW_, SH_), (140, 100, 255, 0)); glow.putalpha(qm.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .7)))
        im.alpha_composite(glow); im.alpha_composite(ia); im.alpha_composite(qg)
        for x in (70, SW_ - 70):                                     # cable eyelets
            ImageDraw.Draw(im).ellipse((x - 9, 12, x + 9, 30), fill=(30, 30, 40, 255), outline=(200, 200, 215, 255), width=3)
        return im
    return E.cached('A2_sign', mk)

PIV = (540., -420.)
def sign(ctx, t):
    t0 = T_C2 - .09                                   # (drops early enough to be readable ON "IA", 11.42)
    if t < t0 or t > T_SIGN_OUT + .2: return
    u = t - t0
    rest = 318.0
    yd = lerp(-260, rest, K.spring(u * .9, 1.6, 7.0)) if u < 1.6 else rest
    if t > T_SIGN_OUT: yd -= 900 * K.ei(clamp((t - T_SIGN_OUT) / .17), 2.2)
    th = math.radians(6.5) * math.exp(-u / 1.1) * math.sin(2 * math.pi * u / 1.15 + .3)
    L = yd - PIV[1]
    cx = PIV[0] + L * math.sin(th); cy = PIV[1] + L * math.cos(th)
    im = K.rotated(sign_img(), math.degrees(th))
    # cables from the eyelets up and out of frame (towards the pivot)
    can = Image.new('RGBA', (W, int(max(10, cy + 10))), (0, 0, 0, 0)) if cy > 0 else None
    if can is not None:
        d = ImageDraw.Draw(can)
        for ex in (70 - SW_ / 2, SW_ / 2 - 70):
            ey = 21 - SH_ / 2
            px = cx + ex * math.cos(th) + ey * math.sin(th); py = cy - ex * math.sin(th) + ey * math.cos(th)
            d.line((px, py, PIV[0] + ex * .55, PIV[1]), fill=(205, 205, 220, 230), width=3)
        ctx.add('screen', can, 0, 0, center=False)
    ctx.add('screen', im, cx, cy)

# =========================================================================================== the LUMARC gauge
GW, GH = 760, 470
HUB = (380, 300); GR = 214; GT = 24
A0, SPAN = 210.0, 240.0                         # v=0 at 210° (lower left), v=1 at -30° (lower right)
def _ang_field():
    def mk():
        yy, xx = np.mgrid[0:GH, 0:GW].astype(np.float32) + .5
        dx, dy = xx - HUB[0], HUB[1] - yy
        ang = np.degrees(np.arctan2(dy, dx))                      # -180..180, ccw from +x
        v = ((A0 - ang) % 360.0) / SPAN                           # 0 at A0, increases clockwise
        rad = np.hypot(dx, dy)
        band = np.clip(1 - np.abs(rad - GR) / (GT / 2), 0, 1); band = np.clip(band * GT / 2, 0, 1)
        on = (v <= 1.0).astype(np.float32)
        return v.astype(np.float32), band * on, rad
    return E.cached('A2_angf', mk)

def _arc_cols():
    def mk():
        v, band, rad = _ang_field()
        c = np.array([(79, 107, 255), (106, 85, 255), (154, 77, 255)], np.float32)
        t = np.clip(v, 0, 1)[..., None]
        col = np.where(t < .5, c[0] + (c[1] - c[0]) * (t / .5), c[1] + (c[2] - c[1]) * ((t - .5) / .5))
        cl = np.array(E.GRAD_LIGHT, np.float32)
        coll = np.where(t < .5, cl[0] + (cl[1] - cl[0]) * (t / .5), cl[1] + (cl[2] - cl[1]) * ((t - .5) / .5))
        return col, coll
    return E.cached('A2_arccols', mk)

def gauge_base():
    def mk():
        im = E.glass_panel(GW, GH, 46, tint=(14, 12, 24), alpha=.58, border=.55)
        v, band, rad = _ang_field()
        track = np.dstack([np.full_like(band, 255)] * 3 + [band * 34]).astype(np.uint8)
        im.alpha_composite(Image.fromarray(track, 'RGBA'))
        S = 2; ti = Image.new('L', (GW * S, GH * S)); d = ImageDraw.Draw(ti)
        for i in range(41):
            vv = i / 40; a = math.radians(A0 - SPAN * vv); maj = i % 10 == 0
            r0 = (GR - GT / 2 - 14) * S; r1 = r0 - (22 if maj else 11) * S
            d.line((HUB[0] * S + math.cos(a) * r0, HUB[1] * S - math.sin(a) * r0, HUB[0] * S + math.cos(a) * r1, HUB[1] * S - math.sin(a) * r1),
                   fill=255 if maj else 150, width=(5 if maj else 3) * S // 2 * 2)
        ti = ti.resize((GW, GH), Image.LANCZOS)
        tk = Image.new('RGBA', (GW, GH), (236, 234, 248, 0)); tk.putalpha(ti.point(lambda x: int(x * .6))); im.alpha_composite(tk)
        lab = K.text_tracked('POTENCIAL DA IA', 36, 600, (230, 228, 244), 5); im.alpha_composite(lab, (34, 22))
        lg = E.logo(170); lg2 = lg.copy(); lg2.putalpha(lg.getchannel('A').point(lambda x: int(x * .85))); im.alpha_composite(lg2, (GW - lg.width - 34, 24))
        for vv, s in ((0.0, 'MÍN'), (1.0, 'MÁX')):
            a = math.radians(A0 - SPAN * vv); r = GR + 34
            tl = K.text_tracked(s, 30, 600, (206, 204, 228), 3)
            im.alpha_composite(tl, (int(HUB[0] + math.cos(a) * r - tl.width / 2), int(HUB[1] - math.sin(a) * r + 6)))
        return im
    return E.cached('A2_gbase', mk)

def _digits(s, size=92, col=E.WHITE):
    def mk():
        f = E.font(size, 700); cw = int(max(f.getlength(d) for d in '0123456789')); asc, desc = f.getmetrics()
        cells = []
        for ch in s:
            w = cw if ch.isdigit() else int(f.getlength(ch))
            im = Image.new('RGBA', (w, asc + desc), (0, 0, 0, 0)); ImageDraw.Draw(im).text(((w - f.getlength(ch)) / 2, 0), ch, font=f, fill=col + (255,))
            cells.append(im)
        out = Image.new('RGBA', (sum(c.width for c in cells), asc + desc), (0, 0, 0, 0)); x = 0
        for c in cells: out.alpha_composite(c, (x, 0)); x += c.width
        return out
    return E.cached(('A2_dg', s, size, col), mk)

def _max_word():
    def mk():
        im = E.word_img('MÁX', 96, 'grad')[0]; return im
    return E.cached('A2_maxw', mk)

_VOX = None
def voice_env(t):
    """0..1 loudness of his voice at t (50 ms RMS on the edit-timeline voice track)."""
    global _VOX
    if _VOX is None:
        x = np.fromfile(E.os.path.join(E.SRC, 'tight16k.raw'), np.float32); h = 160
        r = np.sqrt(np.convolve(x ** 2, np.ones(800) / 800, 'same')[::h]); db = 20 * np.log10(r + 1e-6)
        _VOX = np.clip((db + 46) / 26, 0, 1)
    i = int(t * 100); return float(_VOX[min(max(i, 0), len(_VOX) - 1)])

def gauge_value(t):
    idle = .12 + .012 * math.sin(t * 23) + .008 * math.sin(t * 37 + 1) + .006 * math.sin(t * 61 + 2)
    if t < T_CLIMB0: return idle
    if t < T_SLAM - .06:
        u = clamp((t - T_CLIMB0) / (T_CLIMB1 - T_CLIMB0))
        return min(.86, idle + .70 * (u ** 1.15) + .045 * voice_env(t) * (u > 0))
    if t < T_SLAM:
        return .80 - .03 * (t - (T_SLAM - .06)) / .06                        # anticipation: a hair back
    u = t - T_SLAM
    return 1.0 + .045 * math.exp(-u / .09) * math.sin(u * 55) - .03 * math.exp(-u / .03)

def _logo_glow():
    def mk():
        lg = E.logo(170); im = Image.new('RGBA', (GW, GH), (0, 0, 0, 0))
        m = Image.new('L', (GW, GH)); m.paste(lg.getchannel('A'), (GW - lg.width - 34, 24))
        g = Image.new('RGBA', (GW, GH), (170, 140, 255, 0)); g.putalpha(m.filter(ImageFilter.GaussianBlur(10)).point(lambda x: min(255, int(x * 1.8))))
        im.alpha_composite(g); w = Image.new('RGBA', (GW, GH), (255, 255, 255, 0)); w.putalpha(m.point(lambda x: int(x * .55))); im.alpha_composite(w)
        return im
    return E.cached('A2_logoglow', mk)

def _sheen(x):
    """diagonal light sweep across the glass at band position x (px), masked to the panel."""
    def mk():
        yy, xx = np.mgrid[0:GH, 0:GW].astype(np.float32)
        return xx + yy * .55
    u = E.cached('A2_sheen_u', mk)
    a = np.exp(-((u - x) / 46.) ** 2) * .32 + np.exp(-((u - x - 90) / 14.) ** 2) * .22
    m = np.asarray(gauge_base().getchannel('A'), np.float32) / 255
    im = Image.new('RGBA', (GW, GH), (255, 255, 255, 0)); im.putalpha(Image.fromarray((np.clip(a * m, 0, 1) * 255).astype(np.uint8)))
    return im

def gauge_img(t, v, slam):
    im = gauge_base().copy()
    lp = t - Wd['ALGUEM']
    if 0 <= lp < .8:                                   # "alguém": the LUMARC mark lights up (someone who knows how)
        im = Image.alpha_composite(im, E.fade(_logo_glow(), math.sin(math.pi * lp / .8) ** .8))
    sw = t - 15.22
    if 0 <= sw < .45: im.alpha_composite(_sheen(-200 + 1400 * eio(sw / .45)))
    vf, band, rad = _ang_field(); col, coll = _arc_cols()
    vv = min(1.0, v)
    m = np.clip((vv - vf) * 160, 0, 1) * band
    glow_k = 1.0 + 1.6 * slam
    arc = np.dstack([col, m * 255]).astype(np.uint8)
    arc_im = Image.fromarray(arc, 'RGBA')
    gl = np.dstack([coll, np.clip(m * 255 * .9 * glow_k, 0, 255)]).astype(np.uint8)
    gl_im = Image.fromarray(gl, 'RGBA').resize((GW // 4, GH // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3.5)).resize((GW, GH), Image.BILINEAR)
    im.alpha_composite(gl_im); im.alpha_composite(arc_im)
    # needle (2x supersampled)
    a = math.radians(A0 - SPAN * clamp(v, -.02, 1.04)); S = 2
    nd = Image.new('L', (GW * S, GH * S)); d = ImageDraw.Draw(nd)
    L0, L1 = -26, GR - GT / 2 - 30
    ca, sa = math.cos(a), math.sin(a); px, py = -sa, -ca
    tip = (HUB[0] + ca * L1, HUB[1] - sa * L1); tail = (HUB[0] + ca * L0, HUB[1] - sa * L0)
    w0 = 7.0
    poly = [(tail[0] + px * w0, tail[1] + py * w0), (tip[0] + px * 1.5, tip[1] + py * 1.5), (tip[0] - px * 1.5, tip[1] - py * 1.5), (tail[0] - px * w0, tail[1] - py * w0)]
    d.polygon([(x * S, y * S) for x, y in poly], fill=255)
    d.ellipse(((HUB[0] - 17) * S, (HUB[1] - 17) * S, (HUB[0] + 17) * S, (HUB[1] + 17) * S), fill=255)
    nd = nd.resize((GW, GH), Image.LANCZOS)
    ng = Image.new('RGBA', (GW, GH), (190, 170, 255, 0)); ng.putalpha(nd.filter(ImageFilter.GaussianBlur(6)).point(lambda x: int(x * (.5 + .4 * slam))))
    im.alpha_composite(ng)
    nw = Image.new('RGBA', (GW, GH), E.WHITE + (0,)); nw.putalpha(nd); im.alpha_composite(nw)
    dh = ImageDraw.Draw(im); dh.ellipse((HUB[0] - 8, HUB[1] - 8, HUB[0] + 8, HUB[1] + 8), fill=(106, 85, 255, 255))
    # readout
    if slam <= 0:
        dg = _digits(f'{int(round(clamp(v) * 100))}%', 84)
        im.alpha_composite(dg, (HUB[0] - dg.width // 2, HUB[1] + 54))
    else:
        mw = _max_word(); s = .7 + .3 * K.back(clamp(slam * 3), 2.2)
        mi = K.scaled(mw, s); im.alpha_composite(mi, (int(HUB[0] - mi.width / 2), int(HUB[1] + 84 - mi.height / 2)))
    return im

def gauge(ctx, t, cam):
    if t < T_GAUGE: return
    u = t - T_GAUGE
    k = 1 - (1 - clamp(u / .26)) ** 3
    v = gauge_value(t)
    slam = clamp((t - T_SLAM) / .3) if t >= T_SLAM else 0.0
    im = gauge_img(t, v, slam)
    s = lerp(.86, 1.0, k)
    if t >= T_SLAM: s *= 1 + .06 * math.exp(-(t - T_SLAM) / .1)
    cx = 540 + cam.sx * .35; cy = 436 + 40 * (1 - k) + cam.sy * .35
    if t > T_SLAM + .5: cy -= 10 * eio((t - T_SLAM - .5) / .6)
    if t > T_OUT + .03:                                                   # clears the stage before the cut
        q = clamp((t - T_OUT - .03) / (T_END - T_OUT - .04)); cy -= 820 * K.ei(q, 2.4); s *= 1 - .1 * q
        if q >= 1: return
    img = K.scaled(im, s)
    ctx.add('screen', img, cx, cy, glass=14 if k > .3 else 0, alpha=clamp(u / .1))
    if t >= T_SLAM:                                                       # shockwave ring from the hub
        w = t - T_SLAM
        if w < .45:
            r = int(40 + 900 * eo(w / .45, 2.5)); ring = _ring(r)
            hx = cx + (HUB[0] - GW / 2) * s; hy = cy + (HUB[1] - GH / 2) * s
            ctx.add('screen', ring, hx, hy, alpha=(1 - w / .45) ** 1.5)
        if w < .3:
            st = K.GK.star(64, 8).resize((360, 360), Image.BILINEAR)
            tx = cx + (HUB[0] + math.cos(math.radians(A0 - SPAN)) * (GR - 40) - GW / 2) * s
            ty = cy + (HUB[1] - math.sin(math.radians(A0 - SPAN)) * (GR - 40) - GH / 2) * s
            ctx.add('screen', st, tx, ty, alpha=(1 - w / .3))

def _ring(r):
    r = max(10, (r // 8) * 8)
    def mk():
        S = 2 * r + 40; m = Image.new('L', (S, S)); ImageDraw.Draw(m).ellipse((20, 20, S - 20, S - 20), outline=255, width=6)
        m = m.filter(ImageFilter.GaussianBlur(3))
        im = Image.new('RGBA', (S, S), (190, 160, 255, 0)); im.putalpha(m); return im
    return E.cached(('A2_ring', r), mk)

# =========================================================================================== captions
def _pages():
    def mk():
        P = K.page
        pg = [P([('MAS', Wd['MAS'], 0), ('SERÁ', Wd['SERA'], 0)]),
              P([('QUE', Wd['QUE3'], 0), ('O', Wd['O3'], 0), ('PROBLEMA', Wd['PROBLEMA'], 0)]),
              P([('É', Wd['E3'], 0), ('A', Wd['A3'], 0)], z=T_SIGN_OUT + .06),
              P([('OU', Wd['OU4'], 0), ('VOCÊ', Wd['VOCE4'], 0), ('SÓ', Wd['SO4'], 0)]),
              P([('NÃO', Wd['NAO'], 0), ('ENCONTROU', Wd['ENCONTROU'], 0)]),
              P([('ALGUÉM', Wd['ALGUEM'], 1), ('QUE', Wd['QUE4'], 0), ('SAIBA', Wd['SAIBA'], 0), ('USAR', Wd['USAR'], 0)]),
              P([('O', Wd['O4'], 0), ('POTENCIAL', Wd['POTENCIAL'], 0)]),
              P([('MÁXIMO', Wd['MAXIMO'], 1), ('DELA?', Wd['DELA'], 0)])]
        return K.chain(pg, T_END)
    return E.cached('A2_pages', mk)

# =========================================================================================== draw
def draw(ctx, lt, t):
    ctx.cam.update(z=1.0, x=540, y=960, dx=0, dy=0, rot=0)
    P = ctx.post; P['vignette'] = .3
    cam = shot_cam(t)
    wc = cam.wall()
    wc.sy += scratch_dy(t)
    plane = wall_plane(t)
    # plane coords = rest screen coords of the wall -> screen through the wall camera
    Zt = wc.Z + .05; ox = 540 - wc.fx * Zt + wc.sx; oy = 960 - wc.fy * Zt + wc.sy     # +5 %: room for shakes
    ox = min(0.0, max(W - W * Zt, ox)); oy = min(0.0, max(H - H * Zt, oy))     # the plane always covers the frame
    a = 1 / Zt
    bg = plane.transform((W, H), Image.AFFINE, (a, 0, -ox * a, 0, a, -oy * a), Image.BILINEAR)
    ctx.bg_img = bg
    cam.place_avatar(ctx)
    wraps = []
    # colour: drained (he keeps a little life) until the slam, then everything floods back
    dr = clamp((t - (T_CUT + .02)) / .2) * (1 - clamp((t - T_SLAM) / .05))
    if dr > .01: wraps.append(lambda fr, dr=dr: K.drained(fr, dr, keep=.30))
    # scratch: RGB tear on the cut
    u = t - T_CUT
    if 0 <= u < .12: P['rgb'] = 10 * (1 - u / .12); P['glitch'] = .5 * (1 - u / .12)
    # snap-in zoom blur (world only)
    us = t - (T_SNAP - .02)
    if 0 <= us < .14:
        zb = .9 * (1 - us / .14)
        wraps.append(lambda fr, zb=zb: K.zblur(fr, zb))
    # light leak / slam flash
    if t >= T_SLAM:
        w = t - T_SLAM
        if w < .16: k = .62 * (1 - w / .16) ** 1.3; wraps.append(lambda fr, k=k: K.light_hit(fr, k, (200, 170, 255)))
    ctx.wrap = K.compose_wraps(*wraps)
    for ti, sz in ((T_C1, 300), (T_C2, 460)):                      # light catch on each impact
        w = t - ti
        if -.01 < w < .2:
            st = K.GK.star(64, 8).resize((sz, sz), Image.BILINEAR)
            x = ox + IMPACT[0] * Zt; y = oy + IMPACT[1] * Zt
            ctx.add('behind', st, x, y, alpha=clamp((w + .01) / .02) * math.exp(-max(0, w) / .06))
    sign(ctx, t)
    gauge(ctx, t, cam)
    K.captions(ctx, t, _pages(), 1470)
    # last frame: seg 5's pose already shows -> it becomes the first frame of s03's snap-in (heavy zoom blur toward
    # his face, everything smeared together), so the jump is hidden inside the move
    fx, fy = cam.scr(*K.FACE)
    if T_OUT + .08 <= t < T_END - 1e-6:                                  # the push-in gathers speed: world-only zoom blur
        zk = .7 * K.ei(clamp((t - T_OUT - .08) / (T_END - T_OUT - .08)), 2)
        prev0 = ctx.wrap
        ctx.wrap = lambda fr, zk=zk: K.zblur(prev0(fr) if prev0 else fr, zk, anchor=(fx, fy))
    if t >= T_END - 1e-6:
        prev = ctx.wrap
        ctx.front += ctx.screen; ctx.screen = []
        ctx.wrap = lambda fr: K.zblur_range(prev(fr) if prev else fr, .24, n=12, anchor=(fx, fy))

def _zblur(fr, k):
    acc = np.asarray(fr.convert('RGB'), np.float32).copy(); n = 4
    for i in range(1, n):
        acc += np.asarray(E.zoom(fr.convert('RGB'), 1 + k * .05 * i), np.float32)
    return Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8))
