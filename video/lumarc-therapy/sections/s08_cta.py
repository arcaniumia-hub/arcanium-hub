"""s08 — Instagram: "…Oh. OH. Okay… I'm listening."  Therapist: "If your Instagram stopped talking to you… comment
L-U-M-A-R-C. We do couples therapy. [For brands.]" + END CARD   (46.50–DUR)

46.50  HARD CUT out of the movie: Instagram MS, stunned (arms still crossed). His phone keeps pinging: every ping drops
       a notification banner (the movie's iOS card, same account) over his crossed arms — never over his face, which
       sits high in the MS — with the follower count climbing (+3,517 -> +8,902 -> +14,377 -> +21,450 on the double
       ping); each banner pops out as the next crash zoom snaps in.
47.73  "OH."      crash zoom #1 (z 1.30)          — each preceded by a notification ping
48.60  "Okay…"    crash zoom #2 (z 1.58)          — captions grow with every zoom
49.67  "I'm listening." crash zoom #3 (ECU z 1.90), held through his silent lean-in.
50.67  CUT to the therapist, to camera. 52.60 punch-in on "you…".
53.10  "comment": a real Instagram comment sheet slides up (emoji reactions, 'Add a comment for lumarc_studio…',
       Post, iOS dark keyboard). He SPELLS the name and every letter is typed on its spoken onset with the iOS key
       balloon: L 53.94 · U 54.17 · M 54.62 · A 54.94 · R 55.23 · C 55.44 (type cues).
55.72  dead air: the therapist's deadpan stare, caret blinking.  56.16 Post (click) -> the sheet drops.
56.44  "We do couples therapy." — wider again; LUMARC lower third (wordmark + 'couples therapy' on "couples").
       If TL[17] includes "For brands." (take src 25.28–25.88): deadpan beat with a slow creep, then "FOR BRANDS.".
VOICE_END  END CARD: the frame frosts into LUMARC glass on the boom, logo slams (bloom + shockwave), the session
       dissolves into brand space; "Couples therapy / for brands.", Comment "LUMARC" pill, "Be seen. Be remembered.",
       @lumarc_studio · slumarc.com; light sweep; holds to the end.
"""
import math
import numpy as np
from PIL import Image
import engine as E
from sections import _D_kit as K

START, END = E.span(16, 17)                       # 46.50 – DUR
W, H, FPS = E.W, E.H, E.FPS
L16, L17 = E.TL[16], E.TL[17]
clamp, eout, ein, lerp, smooth, expo = E.clamp, E.eout, E.ein, K.lerp, K.smooth, K.expo
T_END = E.VOICE_END                                # end card (57.62 on the current timeline)

# ---------------------------------------------------------------- measured onsets (see _D_kit.MEASURED)
W_OH1, W_OH2, W_OKAY, W_IM = K.wt(16, '…OH.'), K.wt(16, 'OH.'), K.wt(16, 'OKAY…'), K.wt(16, "I'M")
W_YOU = K.wt(17, 'YOU…')
W_COMMENT = K.wt(17, 'COMMENT')
W_WE, W_COUPLES, W_THERAPY = K.wt(17, 'WE'), K.wt(17, 'COUPLES'), K.wt(17, 'THERAPY.')
W_BRANDS = K.wt(17, 'BRANDS.')
SPELL = K.SPELL

F_Z = [K.fr(W_OH2), K.fr(W_OKAY), K.fr(W_IM)]     # 1432, 1458, 1490 — the snaps land here
Z = [1.0, 1.30, 1.58, 1.90]
TO = [(540, 600), (540, 630), (540, 660), (540, 690)]
F_T17 = math.ceil(L17['t0'] * FPS - 1e-6)          # 1520  therapist
F_YOU = K.fr(W_YOU)                                # 1578  punch-in on "you…"
T_UP = W_COMMENT - .02                             # sheet rises on "comment"
T_POST = W_WE - .28                                # 56.16 Post tap at the end of the dead air
T_DOWN = T_POST + .04
F_WE = K.fr(W_WE) - 1                              # wider framing for "We do couples therapy."
PINGS = [47.22, 48.20, 49.06, 49.24]
# the banner each ping drops (groups: one banner per zoom; the double ping ticks the same banner's count up)
PING_CARDS = [(PINGS[0], ['+3,517 new followers']), (PINGS[1], ['+8,902 new followers']),
              (PINGS[2], ['+14,377 new followers', '+21,450 new followers'])]
PING_OUT = [W_OH2 - .12, W_OKAY - .12, W_IM - .12]          # flick up as each crash zoom snaps in
PING_TOP = 1140                                             # card 1140-1308: above the captions (1424+)

CUES = [(p, 'notify', {'gain': g}) for p, g in zip(PINGS, (-7, -6, -6, -4))] + [
    (W_OH2, 'zoom', {}), (W_OKAY, 'zoom', {'gain': 1}), (W_IM, 'zoom', {'gain': 2}),   # escalating crash zooms
    (W_YOU, 'tick', {'gain': -8}),                                                    # punch-in
    (W_COMMENT, 'swipe', {'gain': -4}),                                               # comment sheet up
] + [(ts, 'type', {'i': i, 'gain': 7}) for i, (_, ts) in enumerate(SPELL)] + [
    (T_POST, 'click', {'gain': 2}),                                                   # Post
    (T_DOWN + .06, 'swipe', {'gain': -12}),                                           # sheet down
    (W_WE + .06, 'tick', {'gain': -9}),                                               # lower third
    (T_END + .50, 'pop', {}),                                                         # pill
    (T_END + .74, 'swipe', {'gain': -11}),                                            # tagline
    (T_END + 1.70, 'shimmer', {'gain': -7}),                                          # light sweep
]

FACE_I = [(30.96, 522, 455), (31.6, 528, 452), (32.2, 534, 450), (33.1, 514, 468), (34.2, 500, 460), (34.9, 500, 460)]


def face_i(src):
    xs = [p[0] for p in FACE_I]
    return float(np.interp(src, xs, [p[1] for p in FACE_I])), float(np.interp(src, xs, [p[2] for p in FACE_I]))


# ================================================================ line 16: escalating crash zooms
def ping_banners(ctx, t):
    """one iOS banner per ping group, popping in place on the ping (scale .9 -> 1 with a little overshoot, 0.16 s; it
    never travels through the captions); a later ping in the group bumps it and ticks the number; it pops out (fade +
    slight drop) as the zoom snaps in. Same card art as the movie's notification stack."""
    NH = K.NH
    for (ta, bodies), t_out in zip(PING_CARDS, PING_OUT):
        if not ta <= t < t_out + .12: continue
        k_in = clamp((t - ta) / .16); k_out = ein(clamp((t - t_out) / .12))
        hits = [p for p in PINGS if ta - 1e-6 <= p <= t + 1e-6]
        j = min(len(bodies), len(hits)) - 1
        sc = (.9 + .1 * E.back(k_in, 1.6)) * (1 - .04 * k_out)
        if j > 0: sc *= 1 + .035 * (1 - eout((t - hits[j]) / .16))     # the count ticks: a small bump on the ping
        card = K.scale_im(K.notif_card('kevinsbakery', bodies[j], True), sc)
        a = min(1., k_in * 4) * (1 - k_out)
        y = PING_TOP + NH / 2 + 26 * k_out
        ctx.add('screen', K.scale_im(K.notif_shadow(), sc), W / 2, y, alpha=a * .9)
        ctx.add('screen', card, W / 2, y, glass=18, alpha=a)



def level_z(t, f):
    """z for the frame: piecewise holds with a creep, 3-frame snaps landing on each word."""
    def hold(i, tt):
        t0 = START if i == 0 else F_Z[i - 1] / FPS
        return Z[i] + .03 * max(0., tt - t0)
    i = sum(1 for fz in F_Z if f >= fz - 2)              # level being reached / held
    if i == 0: return hold(0, t), 0, 1.0
    fz = F_Z[i - 1]
    k = K.snap(f, fz)
    if k >= 1: return hold(i, t), i, 1.0
    z_prev = hold(i - 1, (fz - 3) / FPS)
    return lerp(z_prev, Z[i], k), i, k


def instagram(ctx, t, f):
    src = L16['s0'] + (t - L16['t0'])
    ctx.shot.update(show=True, spk='I', angle='I', src=src)
    z, i, k = level_z(t, f)
    to = TO[i] if k >= 1 or i == 0 else tuple(lerp(a, b, k) for a, b in zip(TO[i - 1], TO[i]))
    ctx.cam.update(K.face_cam(face_i(src), z, to=to))
    if i > 0 and k < 1:
        ctx.wrap = K.zoom_blur(.8 + .2 * i if k < .6 else .45 + .1 * i, anchor=to)
    ctx.post['vignette'] = .32 + .06 * i
    sizes = {'…OH.': 78, 'OH.': 104, 'OKAY…': 112, "I'M LISTENING.": 100}
    K.clean_take(ctx)                                        # choked matte: the ECU magnifies the key fringe
    K.captions(ctx, t, (16,), sizes=sizes)
    ping_banners(ctx, t)


# ================================================================ line 17: the CTA
def therapist(ctx, t, f):
    src = L17['s0'] + (t - L17['t0'])
    ctx.shot.update(show=True, spk='T', angle='T', src=src)
    u = t - F_T17 / FPS
    if f < F_YOU: z = 1.02 + .02 * u
    elif f < F_WE: z = 1.15 + .012 * (t - F_YOU / FPS)
    else:
        z = 1.03 + .01 * (t - F_WE / FPS)
        if K.FB and t > W_THERAPY + .40:                  # the deadpan beat before "For brands.": slow creep
            z += .09 * smooth((t - (W_THERAPY + .40)) / .6)
    ctx.cam.update(z=z, x=500., y=440.)
    # the comment sheet
    sh, y = K.comment_sheet(t, T_UP, SPELL, T_POST, T_DOWN)
    if sh is not None:
        ctx.add('screen', sh, 0, int(y), center=False)
    if t >= W_WE + .06:
        K.lower_third(ctx, t, W_WE + .06, x=60, y=1130)
    K.clean_take(ctx)
    K.captions(ctx, t, (17,), skip=('COMMENT', '“LUMARC”.'))


# ================================================================ end card
def end_card(ctx, t):
    lt = t - T_END
    ctx.shot.update(show=True, spk='T', angle='T', src=26.20 + lt)        # silent, hands clasped (no ghost lip-sync)
    ctx.cam.update(z=1.05 + .03 * lt, x=500., y=440.)
    ctx.captions = False
    k_frost = clamp((lt + .03) / .06)                     # the glass hits on the boom (no grey half-frost frame)
    gone = smooth((lt - .30) / .55)
    cx = W / 2

    def wrap(fr):
        if gone < 1:
            out = K.frost(fr, k_frost)
            if gone > 0: out = Image.blend(out, K.space(), gone)
        else:
            out = K.space().copy()
        K.end_motes(out, lt, gone)                        # slow defocused motes in brand space
        # logo slam (on the boom), bloom, shockwave
        LY = 610
        s = (1 + .22 * (1 - expo(lt / .26))) * (1 + .012 * lt)
        out = K.shock(out, t, T_END, cx, LY)
        gl = K.scale_im(K.logo_glow(), s)
        ga = (.62 + .12 * math.sin(lt * 2.4)) * clamp(lt / .12)
        out.alpha_composite(E.fade(gl, ga), (int(cx - gl.width / 2), int(LY - gl.height / 2)))
        lg = K.logo_img()
        sk = (lt - 1.70) / .7
        if 0 < sk < 1: lg = K.sheen(lg, sk, K.ink_mask('logo', K.logo_img(), 90, 200), 40, .6)
        lg = K.scale_im(lg, s, Image.LANCZOS)
        out.alpha_composite(E.fade(lg, clamp(lt / .04)), (int(cx - lg.width / 2), int(LY - lg.height / 2)))
        kb = .95 * (1 - eout(lt / .45))
        if kb > .01:
            fld = K.hit_field(); out = K.add_light_field(out, fld, kb, int(cx - fld.shape[1] / 2), int(LY - fld.shape[0] / 2))
        # headline: Couples therapy / for brands.
        for words, t0, y in (([('Couples', 86, 600, False), ('therapy', 86, 600, False)], T_END + .20, 862),
                             ([('for', 86, 300, False), ('brands.', 86, 700, True)], T_END + .32, 962)):
            for im, xo, _ in K.end_line([(w, sz, wg, g) for w, sz, wg, g in words], gap=20):
                r = K.rise(im, expo((t - t0) / .42))
                if r is not None: out.alpha_composite(r, (int(cx + xo - r.width / 2), int(y - r.height / 2)))
        # pill
        PT = T_END + .50
        if t >= PT:
            k = t - PT
            sp = (.55 + .45 * E.back(k / .32, 2.4)) * (1 + .016 * (1 - math.cos((k - .32) * 2.6)) if k > .32 else 1)
            py = 1158
            pg = K.end_pill_glow()
            out.alpha_composite(E.fade(pg, clamp(k / .3) * (.8 + .2 * math.sin(t * 2.6))), (int(cx - pg.width / 2), int(py - pg.height / 2 + 14)))
            p = K.end_pill()
            ps = (lt - 1.95) / .6
            if 0 < ps < 1: p = K.sheen(p, ps, K.ink_mask('pill', K.end_pill(), 200, 230), 40, .45)
            p = K.scale_im(p, sp)
            out.alpha_composite(E.fade(p, clamp(k / .08)), (int(cx - p.width / 2), int(py - p.height / 2)))
        # tagline + handle
        TT = T_END + .74
        if t >= TT:
            k = eout((t - TT) / .45)
            tg = K.end_small('Be seen. Be remembered.', 48, 500, (210, 204, 242))
            out.alpha_composite(E.fade(tg, k), (int(cx - tg.width / 2), int(1318 + 14 * (1 - k) - tg.height / 2)))
        HT = T_END + .90
        if t >= HT:
            k = eout((t - HT) / .45)
            hd = K.end_small('@lumarc_studio  ·  slumarc.com', 42, 500, (176, 172, 210))
            out.alpha_composite(E.fade(hd, k), (int(cx - hd.width / 2), int(1394 + 14 * (1 - k) - hd.height / 2)))
        return out

    ctx.wrap = wrap
    ctx.post['vignette'] = .3
    if lt < .08: ctx.post['rgb'] = 4 * (1 - lt / .08)


# ================================================================ draw
def draw(ctx, lt, t):
    f = K.fr(t)
    if t >= T_END - 1e-6:
        end_card(ctx, t)
    elif f < F_T17:
        instagram(ctx, t, f)
    else:
        therapist(ctx, t, f)
