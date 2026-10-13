"""s07 — "I sell croissants, not movies!" / "Kevin… your croissants deserve a movie." + THE MOVIE (36.84–46.50)

36.84  Kevin MS, exasperated, slow push.
38.50  CRASH ZOOM on "MOVIES!" (3-frame snap to a CU, zoom-blur on the snap frames, 'zoom' cue), held with a creep
       through his silent glare until the therapist's line.
39.60  CUT to the therapist MS, calm: "Kevin…" (39.64) — slow push, the pause is his.
40.43  REACTION CUT on "your" (40.45): Kevin CU, suspicious squint (silent take src 23.05…) under "your croissants…".
41.50  CUT back to the therapist on "deserve" (41.54), push continues.
42.14  "MOVIE." (nasal onset 42.13–42.14): the frame BECOMES a movie — scope bars close in to a 2.39:1 slit while the camera pushes
       to his eyes (Leone close-up); the line's last words sit on the black bar like subtitles. Riser under the hold.
42.90  THE MOVIE (braam + taiko in the score). Inside the 2.39 slit: the oven glow fades up, A LUMARC FILM.
43.62  The croissant pull (slit), fingers press.
44.05  On the taiko the frame EXPANDS (slit -> 1080x1320 scope) as the crust cracks; speed-ramped tear, slow-mo
       reveal of the honeycomb by 44.65.
44.65  Taiko: hero croissant, rack focus + push.
45.10  Taiko: the storefront with the line of customers, golden hour (framed so the real gold KEVIN'S BAKERY sign reads).
45.35  IMPACT: KEVIN'S BAKERY gold trailer title slams (flash, anamorphic streak, shake); the street dims behind it.
45.62  Gold light sweep across the title.  45.72 THIS SATURDAY.
45.80  Notifications rain in on top (likes, comment, views, "+1,284 new followers" lands 46.13 and holds) — proof it
       worked. Hard cut at 46.50.
Office shots draw the take through K.clean_take (2 px matte choke: no key fringe on the crash zooms / Leone push).
Film look throughout the movie: warm S-curve grade, halation, light leaks, gate weave, heavier grain.
"""
import math
import numpy as np
from PIL import Image, ImageFilter
import engine as E
from sections import _D_kit as K

START, END = E.span(14, 15)                       # 36.84 – 46.50
W, H, FPS = E.W, E.H, E.FPS
L14, L15 = E.TL[14], E.TL[15]
M0, M1 = E.MOVIE                                   # 42.90, 46.50
clamp, eout, ein, lerp, smooth, expo = E.clamp, E.eout, E.ein, K.lerp, K.smooth, K.expo

# ---------------------------------------------------------------- measured onsets (see _D_kit.MEASURED)
W_MOVIES = K.wt(14, 'MOVIES!')                     # 38.50
W_KEVIN, W_YOUR = K.wt(15, 'KEVIN…'), K.wt(15, 'YOUR')       # 39.64, 40.45
W_DESERVE, W_MOVIE = K.wt(15, 'DESERVE'), K.wt(15, 'MOVIE.')  # 41.54, 42.20

F_ZOOM = K.fr(W_MOVIES)                            # 1155  38.500  crash zoom lands
F_T15 = math.ceil(L15['t0'] * FPS - 1e-6)          # 1188  39.600  therapist (line start 39.58)
F_KR = K.fr(W_YOUR) - 1                            # 1213  40.433  Kevin reaction (one frame before "your")
F_TB = K.fr(W_DESERVE) - 1                         # 1245  41.500  back to the therapist ("deserve" 41.54)
F_BARS = K.fr(W_MOVIE)                             # 1266  42.200  bars start closing on "movie"
T_BARS1 = 42.78                                    # slit reached (hold ~4 frames before the cut)
F_M0 = K.fr(M0)                                    # 1287  42.900  THE MOVIE

# movie beats (score: braam + taiko M0, taikos 44.05 / 44.65 / 45.10, impact 45.35)
T_PULL = 43.62
T_EXP = 44.05
T_HERO = 44.65
T_STORE = 45.10
T_HIT = 45.35
T_SHEEN = 45.62
T_SAT = 45.72
NOTIFS = [(45.80, 'kevinsbakery', 'maria.eats and 2,431 others liked your reel.', False),
          (45.93, 'kevinsbakery', 'nyc.croissant.club commented: “WHERE IS THIS??”', False),
          (46.04, 'kevinsbakery', 'Your reel is getting more views than usual.', False),
          (46.13, 'kevinsbakery', '+1,284 new followers', True)]          # lands, then holds ~.37 s to the cut

CUES = [
    (W_MOVIES, 'zoom', {}),                                        # crash zoom "MOVIES!"
    (W_MOVIE + .04, 'riser', {'to': M0 - .02, 'gain': -5}),        # bars close: tension into the braam
    (T_EXP, 'whoosh', {'gain': -8}),                               # the frame expands (taiko is in the score)
    (T_HIT, 'shing', {'gain': -5}),                                # gold title slam (score impact)
    (T_SHEEN, 'shimmer', {'gain': -9}),                            # light sweep on the gold
] + [(ta, 'notify', {'gain': g}) for (ta, *_), g in zip(NOTIFS, (-3, -4, -5, 0))]

# faces (world px, z=1, own angle)
FACE_K = (550, 545)                                # Kevin line 14 (nose)
FACE_KR = (520, 530)                               # Kevin reaction src 23.x
FACE_T = (520, 470)
EYES_T = [(15.30, 540, 436), (15.70, 530, 428), (16.00, 505, 405), (16.20, 488, 392)]   # therapist eyes by src


def eyes_t(src):
    xs = [e[0] for e in EYES_T]
    return float(np.interp(src, xs, [e[1] for e in EYES_T])), float(np.interp(src, xs, [e[2] for e in EYES_T]))


def src15(t): return L15['s0'] + (t - L15['t0'])


# ================================================================ office part
def kevin(ctx, t, f):
    src = L14['s0'] + (t - L14['t0'])
    ctx.shot.update(show=True, spk='K', angle='K', src=src)
    u = t - START
    z0 = 1.0 + .025 * u
    if f < F_ZOOM - 2:
        ctx.cam.update(z=z0, x=FACE_K[0], y=470.)
    else:
        z0h = 1.0 + .025 * ((F_ZOOM - 3) / FPS - START)
        k = K.snap(f, F_ZOOM)
        z = lerp(z0h, 1.60, k) + .04 * max(0., t - F_ZOOM / FPS)
        ctx.cam.update(K.face_cam(FACE_K, z, to=(540, 700)))
        if f in (F_ZOOM - 2, F_ZOOM - 1):
            ctx.wrap = K.zoom_blur(1.0 if f == F_ZOOM - 2 else .55, anchor=(540, 640))


def therapist_a(ctx, t):
    ctx.shot.update(show=True, spk='T', angle='T', src=src15(t))
    u = t - F_T15 / FPS
    ctx.cam.update(z=1.02 + .035 * u, x=FACE_T[0], y=430.)


def kevin_reaction(ctx, t):
    u = t - F_KR / FPS
    ctx.shot.update(show=True, spk='K', angle='K', src=23.05 + u)
    ctx.cam.update(K.face_cam(FACE_KR, 1.32 + .05 * u, to=(540, 660)))


def therapist_b(ctx, t):
    """the push to his eyes + scope bars closing (camera done in the wrap: no world clamp, bars hide the edges)."""
    src = src15(t)
    ctx.shot.update(show=True, spk='T', angle='T', src=src)
    ex, ey = eyes_t(src)
    zb = 1.08 + .035 * (t - F_TB / FPS)
    kb = smooth((t - W_MOVIE) / (T_BARS1 - W_MOVIE))
    kz = eout((t - W_MOVIE) / (T_BARS1 - W_MOVIE + .05))
    z = zb + (1.44 - zb) * kz + .02 * max(0., t - T_BARS1)
    bar = K.SLIT * kb
    Y = min(960., bar + z * ey - 6)                          # world top edge stays hidden under the closing bar
    X = 540.
    def wrap(frame):
        out = E.zoom(frame.convert('RGB'), z, (ex, ey), dx=X - ex, dy=Y - ey).convert('RGBA')
        return K.letterbox(out, bar)
    ctx.wrap = wrap
    if kb > 0:
        ctx.post['vignette'] = .32 + .2 * kb


# ================================================================ the movie
def native_pull(t):
    pts = [(T_PULL, 3.27), (T_EXP, 3.70), (44.36, 4.60), (T_HERO, 4.86)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return float(np.interp(t, xs, ys))


def weave(f):
    return (K.hrand(f, 1) - .5) * 2.0, (K.hrand(f, 2) - .5) * 2.0


def movie_picture(t, f):
    """(RGB picture 1080x1920, bar height, look params)"""
    wx, wy = weave(f)
    if t < T_PULL:                                           # 1  OVEN in the scope slit
        u = t - M0
        img = K.frame_from(K.plate_src('croissant_oven'), z=1.16 + .10 * u, cx=.50, cy=.47 + .07 * smooth(u / .65), dx=-24 * u + wx, dy=wy)
        expo_ = smooth((u - .17) / .36)                       # credit over black, then the oven glow fades up
        flick = 1 + .035 * math.sin(t * 31) + .02 * math.sin(t * 17 + 1)
        return img, K.SLIT, dict(bright=expo_ * flick, leak=.35 * smooth((u - .3) / .3), leak_dx=.25 - .2 * u)
    if t < T_HERO:                                           # 2  PULL: slit -> expand on the taiko
        img = K.pull_frame(native_pull(t))
        ke = eout((t - T_EXP) / .20) if t >= T_EXP else 0.
        z = lerp(1.30, 1.12, ke) + .03 * max(0., t - T_EXP)
        cy = lerp(.585, .56, ke)
        img = K.frame_from(img, z=z, cx=.52, cy=cy, dx=wx, dy=wy)
        bar = lerp(K.SLIT, K.SCOPE, ke)
        return img, bar, dict(bright=1.0, leak=.25 * (1 - ke) + .45 * clamp(1 - abs(t - T_EXP) / .12), leak_dx=.05)
    if t < T_STORE:                                          # 3  HERO croissant, rack focus + push
        u = t - T_HERO
        img = K.frame_from(K.plate_src('croissant_hero'), z=1.16 + .16 * u, cx=.36, cy=.66, dx=wx, dy=wy)
        rb = 9 * (1 - eout(u / .2))
        if rb > .5: img = img.filter(ImageFilter.GaussianBlur(rb))
        return img, K.SCOPE, dict(bright=1.0, leak=.5 * clamp(1 - u / .25), leak_dx=-.05)
    # 4  STOREFRONT + title
    u = t - T_STORE
    sx = sy = 0.
    if t >= T_HIT:
        ks = 1 - eout((t - T_HIT) / .3)
        sx, sy = 14 * ks * (K.hrand(f, 7) - .5), 14 * ks * (K.hrand(f, 8) - .5)
    img = K.frame_from(K.plate_src('storefront_line'), z=1.0 + .07 * u, cx=.52, cy=.352 + .05 * K.smooth(u / 1.4),
                       dx=wx + sx, dy=wy + sy, vis=(K.SCOPE, H - K.SCOPE))     # the real gold sign reads, then the title
    dim = .52 * eout((t - T_HIT) / .18) if t >= T_HIT else 0.
    return img, K.SCOPE, dict(bright=1 - dim, leak=.3 * clamp(1 - u / .3), leak_dx=.1, dim=dim)


def movie(ctx, t, f):
    img, bar, P = movie_picture(t, f)
    img = K.film_look(img, t, leak=P.get('leak', 0), leak_dx=P.get('leak_dx', 0), halation=.32)
    if P.get('bright', 1) != 1:
        img = Image.eval(img, lambda v, b=P['bright']: int(min(255, v * b)))
    if t >= T_HIT:                                           # flash frame on the impact: additive light, picture only
        img = K.add_light(img, 235 / 255 * math.exp(-(t - T_HIT) / .05))
    if T_EXP - 1 / FPS <= t < T_EXP + 2 / FPS:
        img = K.zoom_blur(.55, anchor=(540, 960))(img).convert('RGB')
    out = K.letterbox(img.convert('RGBA'), bar)
    cx = W / 2
    # "A LUMARC FILM"
    if M0 <= t < T_PULL:
        a = smooth((t - (M0 + .02)) / .10) * (1 - smooth((t - 43.14) / .13))
        if a > .01:
            cr = K.small_caps('A LUMARC FILM', 58, .44, col=(252, 246, 234), wght=600)
            s = 1 + .03 * (t - M0)
            cr2 = K.scale_im(cr, s)
            out.alpha_composite(E.fade(cr2, a), (int(cx - cr2.width / 2), int(H / 2 - cr2.height / 2)))
    # title
    if t >= T_HIT:
        ti, ink = K.title_img()
        kh = (t - T_HIT)
        s = (1 + .26 * (1 - expo(kh / .2))) * (1 + .018 * kh)
        if T_SHEEN < t < T_SHEEN + .45: ti = K.sheen(ti, (t - T_SHEEN) / .45, ink, 40, .65)
        ti2 = K.scale_im(ti, s)
        ty = 1030
        out.alpha_composite(E.fade(ti2, clamp(kh / .05)), (int(cx - ti2.width / 2), int(ty - ti2.height / 2)))
        fk = 1.15 * (1 - eout(kh / .55)) + .12
        out = K.add_field(out, K.flare_field(), fk, ty + 40)
        if t >= T_SAT:
            sa = K.small_caps('THIS SATURDAY', 52, .40, col=(246, 228, 188), wght=700, rules=64)
            k = eout((t - T_SAT) / .3)
            out.alpha_composite(E.fade(sa, k), (int(cx - sa.width / 2), int(1290 + 18 * (1 - k) - sa.height / 2)))
    ctx.full = out
    K.notif_stack(ctx, t, NOTIFS, top=236)
    ctx.captions = False
    ctx.post.update(vignette=.18, grain=1.35)


# ================================================================ draw
def draw(ctx, lt, t):
    f = K.fr(t)
    if f >= F_M0:
        movie(ctx, t, f); return
    if f < F_T15: kevin(ctx, t, f)
    elif f < F_KR: therapist_a(ctx, t)
    elif f < F_TB: kevin_reaction(ctx, t)
    else: therapist_b(ctx, t)
    K.clean_take(ctx)                                        # choked matte: no key fringe on the zooms
    K.captions(ctx, t, (14, 15))
