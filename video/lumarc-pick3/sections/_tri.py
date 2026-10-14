"""_tri — THE TRIANGLE: the brand device of the "Pick three." ad (shared kit, read-only for section authors).

A premium glass triangle: three frosted-glass ORBS at the vertices — FAST (top, lightning bolt), CHEAP (bottom-left,
price tag), GOOD (bottom-right, star) — each with a bold Outfit label outside the triangle (FAST above, CHEAP / GOOD
below), joined by LIGHT BEAMS (white-hot core + LUMARC-gradient halo) over a thin dark-glass plate. Cool grey when
dim, LUMARC gradient light when lit, red ✗ for the excluded vertex, crack -> shatter, assemble, complete (blaze +
shockwave + bloom) and a morph into the LUMARC logo.  Everything is a PURE FUNCTION of the state dict (seeded
randomness only); sprites are cached.

    from sections import _tri as TRI

    img = TRI.render(state, size=900, canvas=None, at=None)      # -> PIL RGBA, transparent background
        size    the triangle's box (orbs + labels fit inside a size x size square; triangle side = .62 size)
        canvas  (w, h) of the returned image (default (size, size)); the box is centred at `at` (default canvas centre).
                Use canvas=(E.W, E.H), at=(x, y) when shock rings / shards / logo must not be clipped by the box
                (only the content's bbox is processed, so a full-frame canvas costs about the same).
    TRI.anchor(name, state, size=900, canvas=None, at=None) -> (x, y)   in the same pixel space as render()
        names: 'fast' 'cheap' 'good' (orb centres), 'center' (centroid), edge midpoints 'fc' 'cg' 'gf',
               'fast_label' 'cheap_label' 'good_label', 'top' (top of the FAST label), 'bottom' (bottom of the lower
               labels), 'logo' (logo centre), 'logo_core' (the glowing core of the logo mark = where the triangle
               collapses), 'impact' (crack origin).
    TRI.radius(state, size=900, node='fast')   -> on-screen orb radius (px) incl. depth / pop
    TRI.paste(base, state, size, x, y, frost=10) -> base with the triangle composited at box centre (x, y); `frost`
               blurs the base under the glass plate + orbs (real frosted glass).  base: PIL RGB/RGBA (modified copy).
    TRI.state(**kw) -> full state dict (defaults filled; per-node / per-edge values may be given as dicts by name)
    TRI.pick(a, b, k=1., x=1., draw=1.) -> state for "pick two": nodes a, b lit k, their edge lit k and drawn from a
               to b (draw 0..1), the third node dimmed with a red ✗ (x 0..1)
    TRI.mix(s1, s2, k) -> per-key interpolation of two states (numbers and tuples; others switch at k = .5)
    TRI.drift(t, amp=1.) -> dict(yaw, pitch, roll): slow organic idle float (pure function of t) — merge into a state

STATE KEYS (defaults)            per-node tuples are ordered (fast, cheap, good); per-edge tuples (fc, cg, gf)
    lit     (0, 0, 0)    node light 0..1 (dim grey glass -> gradient-lit orb, white icon, white label);
                         values up to ~1.6 OVERDRIVE the halo for a hit on the word (decay it back to 1 in ~.2 s)
    x       (0, 0, 0)    red ✗ 0..1 over the node (stamp-in: ramp 0 -> 1 in ~.18 s; it scales 1.9x -> 1 with a back
                         ease); the orb turns smoky red, its label red-grey
    pop     (1, 1, 1)    per-node scale (orb + icon; label follows with sqrt) — e.g. 1 + .25*bump on the word
    edge    (0, 0, 0)    beam light per edge: fc = FAST-CHEAP (left), cg = CHEAP-GOOD (bottom), gf = GOOD-FAST (right)
    draw    (1, 1, 1)    how much of each edge exists, -1..1: + grows from its first node (fc: from FAST, cg: from
                         CHEAP, gf: from GOOD), - from the second. A hot spark rides the head while 0 < |draw| < 1.
    crack   0            0..1 fracture: impact flash, radial cracks race out, then spider-web rings (light leaks in)
    shatter 0            0..1 the plate + orbs burst into shards (3-D tumble, light catches, glints, dust), labels
                         drop; all gone by 1 (think "seconds": ramp it over ~1.0-1.3 s). Use with crack=1 before it.
    assemble 1           0..1 build-in: orbs fly in from the lens (FAST, CHEAP, GOOD; lock pops + rings at .34/.46/.58),
                         labels pop, the beams draw one after the other (fc .50-.64, cg .62-.76, gf .74-.88) with an
                         energy trace that settles to `edge`, the plate fades in (.82 -> 1)
    complete 0           0..1 "Pick three.": everything blazes (overdrive peak at ~.04), shockwave rings run out
                         through the plate (gone at .6), bloom; complete = 1 is the settled all-lit hero state
    logo     0           0..1 morph: the triangle spins + collapses into the logo mark's core (.0-.42), flash + orbit
                         ring (.36-.75), the LUMARC logo blooms out of the core (.44-.84), wordmark wipes in (.58-.88),
                         a light sweep (.8-1). logo = 1 is the static logo (width .86 size, centred on the box).
    yaw, pitch, roll  0  3-D tilt in degrees (yaw: vertical axis; pitch > 0 tips the top toward the viewer; roll: in
                         screen plane). Keep |yaw|, |pitch| <= ~25 for legibility; drift(t) gives ~±7 / ±4.
    glow     1           global light gain (beams, halos, bloom)        label  1   labels alpha
    plate    1           glass plate alpha                               alpha  1   whole-image alpha
    scale    1           extra scale of the triangle inside its box (keeps the box/canvas; e.g. .7 + canvas for rings)
    flow     None        float phase (e.g. t * .9): energy pulses travel along lit beams (alive idle) — None = off
    ring     1.25        max radius of the complete shockwave in circumradii (raise it with a big canvas)
    impact   (.08, .12)  crack origin, in circumradius units from the centroid (x right, y down)
    seed     7           crack / shard pattern seed
    labels   ('FAST', 'CHEAP', 'GOOD')

PLACEMENTS in the 1080x1920 frame (safe zone x 70-960, y 280-1250 for all labels; on the default camera his head top is
at y ~ 530 and his shoulders fill the frame from y ~ 1100 — never put the triangle over his face).  Checked in
out/tri/place_*.jpg (`python3 sections/_tri.py frame`):
    FULL-SCREEN cutaway (bg darkened / blurred, avatar hidden or pushed back): size 900 at (540, 760) -> labels span
        x 150-930, y 373 (top of FAST) - 1147 (bottom of CHEAP/GOOD). The hero size for the rule, the crack/shatter,
        "Pick three." and the logo. Use canvas=(E.W, E.H), at=(540, 760) so shockwaves / shards / the orbit ring are
        not clipped (ring=2.2-2.6 reads as a full-frame shockwave).
    OVER HIS HEAD: avatar pushed down (ctx.avatar s=.80, y=+90 -> head top ~ y 880): size 640 at (540, 585) -> labels
        y ~ 300-865.
    BESIDE HIM: avatar x=+260 (he sits right): size 560 at (330, 760) -> labels x 88-572.
    LOGO end state: size 860 -> logo 740 px wide, centred on the box (anchor 'logo').
    Labels are .078 x size (70 px at 900, 50 px at 640); below ~520 px they stop reading on a phone.
    Layer: 'screen' (after the camera, stays crisp) for UI-like use; 'front' to ride the camera moves with him;
    TRI.paste(frame, ...) for real frost behind the glass (e.g. inside ctx.wrap or on ctx.full).

SUGGESTED CUES (kinds in sections/README.md)
    node lit on its word        'ding' {'note': 'E6'|'C6'|'G6' (fast|cheap|good)}, gain -10, + 'pop' -14
    edge draw a -> b            'swoosh' -12 at the start, 'shing' -10 when it lands (|draw| reaches 1)
    red ✗ stamp                 'buzzer' -8 (or 'stamp' -6 + 'thud' -12) on the stamp frame
    lit overdrive hit           'impact' -10
    crack                       'crack' 0 at crack = 0+ (impact), 'glass' -10 when the rings form (~.5)
    shatter                     'shatter' 0 + 'boom' -4 at shatter = 0+, 'sub' -8
    assemble                    'whoosh' -12 per orb flight (a = 0, .12, .24), 'lock' -6 at each lock (.34/.46/.58),
                                'shing' -12 per beam landing (.64/.76/.88)
    complete                    'boom' 0 + 'braam' {'note': 'D2', 'dur': 2.0} -4 + 'shimmer' -10 at complete = 0+
    logo                        'swoosh_up' -10 at 0, 'sting' -6 at the flash (.42), 'shimmer' -12 at the sweep (.8)

PERFORMANCE (900 px box, one core, measured): dim / pick / lit ~30-45 ms, assemble ~27, crack ~40, complete ~40
(full-frame canvas with a 2.4 ring: ~85 ms for the few ring frames), logo ~30, shatter ~10-35 ms per frame after a
one-off ~0.15-0.35 s build of the shard kit on the first shatter frame (it is cached on lit/x/edge/draw/pop/glow/
plate/complete/scale/seed/impact: keep those constant while shattering).  The first render in a process costs
~0.15-0.2 s (orb / icon / label sprites).  A 600 px box is ~2x cheaper.  Output is byte-identical for equal states
whatever the call history.  `python3 sections/_tri.py demo` writes strips of every state to out/tri/ and prints
timings; `bench` only times; `frame` renders the placements over a real frame of the take; `clip a b` renders
TRI.story(t) — a reference 8 s animation of every state driven from time — between a and b to out/tri/clip.mp4.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E

NODES = ('fast', 'cheap', 'good')
EDGES = ('fc', 'cg', 'gf')
EDGE_NODES = ((0, 1), (1, 2), (2, 0))
ICONS = ('bolt', 'tag', 'star')
RED = (255, 62, 78)

DEFAULTS = dict(lit=(0., 0., 0.), x=(0., 0., 0.), pop=(1., 1., 1.), edge=(0., 0., 0.), draw=(1., 1., 1.),
                crack=0., shatter=0., assemble=1., complete=0., logo=0., yaw=0., pitch=0., roll=0.,
                glow=1., label=1., plate=1., alpha=1., scale=1., flow=None, ring=1.25, impact=(.08, .12), seed=7,
                labels=('FAST', 'CHEAP', 'GOOD'))
_TRIPLES = ('lit', 'x', 'pop', 'edge', 'draw')

# geometry in units of the box size S
K_R, K_ORB, K_LAB, K_FOC = .36, .088, .078, 2.6
S60 = math.sin(math.pi / 3)
LOGO_CORE = (94 / 640, 113 / 218)          # glowing core of the logo mark (fraction of the logo image)
LOGO_SPLIT = 238 / 640                      # mark | wordmark split
LOGO_W = .86

clamp = E.clamp
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def eout4(x): x = clamp(x); return 1 - (1 - x) ** 4
def ein(x): x = clamp(x); return x ** 2.4
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7): x = clamp(x) - 1; return 1 + x * x * ((s + 1) * x + s)
def bump(x): x = clamp(x); return math.sin(math.pi * x)
def lerp(a, b, k): return a + (b - a) * k
def hrand(i, s=0): return (math.sin(i * 127.1 + s * 311.7) * 43758.5453) % 1.0

_C = {}
def _c(key, fn):
    if key not in _C: _C[key] = fn()
    return _C[key]


# ================================================================================================ state helpers
def _norm(st_in):
    st = dict(DEFAULTS)
    for k, v in (st_in or {}).items():
        if k not in DEFAULTS: raise KeyError(f'_tri: unknown state key {k!r} (known: {sorted(DEFAULTS)})')
        if k in _TRIPLES and isinstance(v, dict):
            names = EDGES if k in ('edge', 'draw') else NODES
            base = list(DEFAULTS[k]); bad = [n for n in v if n not in names]
            if bad: raise KeyError(f'_tri: {k} names must be in {names}, got {bad}')
            for n, val in v.items(): base[names.index(n)] = val
            v = base
        st[k] = v
    for k in _TRIPLES: st[k] = tuple(float(v) for v in st[k])
    return st


def state(**kw):
    """full state dict with defaults; per-node / per-edge values may be dicts keyed by name, e.g.
    state(lit=dict(fast=1, cheap=1), edge=dict(fc=1))."""
    return _norm(kw)


EDGE_OF = {('fast', 'cheap'): (0, 1.), ('cheap', 'fast'): (0, -1.), ('cheap', 'good'): (1, 1.),
           ('good', 'cheap'): (1, -1.), ('good', 'fast'): (2, 1.), ('fast', 'good'): (2, -1.)}


def pick(a, b, k=1., x=1., draw=1., **kw):
    """'pick two' state: a and b lit k, their edge lit k and drawn from a to b, the third node red-✗ (x)."""
    i, j = NODES.index(a), NODES.index(b); o = 3 - i - j
    lit = [0., 0., 0.]; lit[i] = lit[j] = k
    xx = [0., 0., 0.]; xx[o] = x
    e, sgn = EDGE_OF[(a, b)]
    edge = [0., 0., 0.]; edge[e] = k
    dr = [1., 1., 1.]; dr[e] = sgn * draw
    s = dict(lit=tuple(lit), x=tuple(xx), edge=tuple(edge), draw=tuple(dr)); s.update(kw)
    return _norm(s)


def mix(s1, s2, k):
    a, b = _norm(s1), _norm(s2); out = {}
    for key in DEFAULTS:
        u, v = a[key], b[key]
        if isinstance(u, tuple) and isinstance(v, tuple) and all(isinstance(q, (int, float)) for q in u + v) and len(u) == len(v):
            out[key] = tuple(p + (q - p) * k for p, q in zip(u, v))
        elif isinstance(u, (int, float)) and isinstance(v, (int, float)) and not isinstance(u, bool):
            out[key] = u + (v - u) * k
        else:
            out[key] = v if k >= .5 else u
    return out


def drift(t, amp=1.):
    """slow organic float for idle shots (pure function of t): ~±7° yaw, ±4° pitch, ±1.5° roll."""
    return dict(yaw=amp * (5.5 * math.sin(.71 * t + .4) + 1.6 * math.sin(1.37 * t + 2.1)),
                pitch=amp * (3.2 * math.sin(.53 * t + 1.3) + .9 * math.sin(1.11 * t)),
                roll=amp * (1.3 * math.sin(.43 * t + 2.7)))


# ================================================================================================ geometry
def _rotm(yaw, pitch, roll):
    a, b, c = math.radians(yaw), math.radians(pitch), math.radians(roll)
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rz @ Rx @ Ry


def _axis_rot(axis, ang):
    x, y, z = axis; c, s = math.cos(ang), math.sin(ang); C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


class _G:
    """per-render geometry: projection, node placements, beams, plate, extra lights."""
    def __init__(self, st, S, ox, oy):
        self.st, self.S = st, S
        sc = st['scale']; R = self.R = K_R * S * sc; self.r = K_ORB * S * sc; self.f = K_FOC * S
        self.box = (ox, oy); self.C = np.array([ox, oy + .25 * R])
        self.LW = LOGO_W * S * sc; lh = self.LW * 218 / 640
        self.T = np.array([ox + (LOGO_CORE[0] - .5) * self.LW, oy + (LOGO_CORE[1] - .5) * lh])
        lg = st['logo']; u1 = clamp(lg / .42); self.col = ein(u1) if lg > 0 else 0.
        self.m = 1 - .97 * self.col                 # homothety toward the logo core (nothing leaves the box)
        self.tri_a = 1 - clamp((lg - .37) / .05) if lg > 0 else 1.
        self.M = _rotm(st['yaw'], st['pitch'], st['roll'] + (170 * self.col if lg > 0 else 0))
        c = st['complete']
        self.boost = 1 + 1.25 * math.exp(-c / .10) * clamp(c * 25) if c > 0 else 1.
        self.boost *= 1 + 1.4 * self.col
        self.Vl = np.array([[0, -R, 0], [-R * S60, R / 2, 0], [R * S60, R / 2, 0]], np.float64)
        # ---- nodes
        a = st['assemble']; self.nodes = []
        P, K = self.proj(self.Vl)
        lab_px = K_LAB * S * sc
        for i in range(3):
            pos, k, alpha, la, popx = P[i], K[i], 1., 1., 1.
            lit = st['lit'][i]
            if c > 0: lit = max(lit, clamp(c * 14))
            if a < 1:
                d0 = .12 * i; p = clamp((a - d0) / .34); e = eout4(p)
                out = self.Vl[i] / np.linalg.norm(self.Vl[i])
                sw = math.radians(40 * (1 - e) * (1 if i != 1 else -1))
                ox_, oy_ = out[0] * math.cos(sw) - out[1] * math.sin(sw), out[0] * math.sin(sw) + out[1] * math.cos(sw)
                Lp = self.Vl[i] + np.array([ox_ * 1.25 * R * (1 - e), oy_ * 1.25 * R * (1 - e), -.62 * self.f * (1 - e)])
                Pp, Kp = self.proj(Lp[None]); pos, k = Pp[0], Kp[0]
                alpha = clamp(p * 3.5)
                lk = d0 + .34; q = (a - lk) / .11
                popx = 1 + .2 * bump(q) if 0 < q < 1 else 1.
                la = clamp((a - lk - .02) / .1)
            pop = st['pop'][i] * popx
            self.nodes.append(dict(i=i, p=np.array(pos, float), k=float(k), z=float((self.Vl[i] @ self.M.T)[2]),
                                   s=self.r * k * pop, pop=pop, a=alpha * self.tri_a, la=la * st['label'] * self.tri_a * (1 - clamp(lg / .12) if lg > 0 else 1),
                                   lit=lit, x=st['x'][i], lab_px=lab_px, lab_k=k * math.sqrt(st['pop'][i] * popx)))
        # ---- edges
        self.edges = []
        for j, (i0, i1) in enumerate(EDGE_NODES):
            d = st['draw'][j]; I = st['edge'][j]
            if c > 0: I = max(I, clamp(c * 14))
            if a < 1:
                s0 = .50 + .12 * j; q = clamp((a - s0) / .14)
                d = math.copysign(abs(d) * eout(q), d if d != 0 else 1)
                I = max(I, .85 * (1 - smooth((a - s0 - .14) / .12)) * (q > 0))     # energy trace, gone by a = .98
            n0, n1 = self.nodes[i0], self.nodes[i1]
            if d < 0: n0, n1 = n1, n0
            p0, p1 = n0['p'], n1['p']; L = float(np.hypot(*(p1 - p0)))
            if L > 1e-3:                                    # beams start at the orbs' glass, not their centres
                dv = (p1 - p0) / L; t0_, t1_ = n0['s'] * .86, n1['s'] * .86
                if t0_ + t1_ < L - 1: p0, p1 = p0 + dv * t0_, p1 - dv * t1_
                else: d = 0.
            self.edges.append(dict(j=j, a=p0, b=p1, d=abs(d), I=I * self.boost * st['glow'] * self.tri_a,
                                   rod=self.tri_a * min(self.nodes[i0]['a'], self.nodes[i1]['a'])))
        self.plate_a = st['plate'] * self.tri_a * (clamp((a - .82) / .18) if a < 1 else 1.)
        self.plate_glow = .55 * clamp(c * 4) + .12 * st['crack']
        self.bloom = (.45 * clamp(c * 4) + .5 * (self.boost - 1)) if c > 0 else .25 * self.col
        self.lab_cap = None

    def proj(self, Pl):
        """local (N,3) px around the centroid -> screen (N,2) and depth scale (N,) (logo morph applied)."""
        Q = np.asarray(Pl, np.float64) @ self.M.T
        k = self.f / np.maximum(self.f + Q[:, 2], self.f * .08)
        xy = self.C + Q[:, :2] * k[:, None]
        if self.col > 0: xy = self.T + self.m * (xy - self.T); k = k * self.m
        return xy, k

    def label_pos(self, n):
        cap = _label_cap(n['lab_px'])
        gap = .016 * self.S * self.st['scale']
        off = (n['s'] + gap + cap / 2 * n['lab_k'])
        return n['p'] + np.array([0, -off if n['i'] == 0 else off])

    def bbox(self):
        """content bbox (canvas px) of the light layer."""
        pts = [n['p'] for n in self.nodes]
        P = np.array(pts); m = self.r * 2.2 + max(n['s'] for n in self.nodes) * 1.4
        x0, y0 = P.min(0) - m; x1, y1 = P.max(0) + m
        c = self.st['complete']
        if 0 < c < .62:
            rr = self.R * (.15 + self.st['ring']) * 1.05 + 30
            x0, y0, x1, y1 = min(x0, self.C[0] - rr), min(y0, self.C[1] - rr), max(x1, self.C[0] + rr), max(y1, self.C[1] + rr)
        if self.st['logo'] > .3:
            hw = self.LW * .62
            x0, y0, x1, y1 = min(x0, self.box[0] - hw), min(y0, self.box[1] - hw * .6), max(x1, self.box[0] + hw), max(y1, self.box[1] + hw * .6)
        if self.bloom > 0:
            g = self.R * .5; x0, y0, x1, y1 = x0 - g, y0 - g, x1 + g, y1 + g
        return x0, y0, x1, y1


# ================================================================================================ sprites
def _field_cols():
    return np.array([(92, 122, 255), (124, 98, 255), (182, 96, 255)], np.float32)


def _grad_x(u):
    c = _field_cols(); u = np.clip(u, 0, 1)[..., None]
    return np.where(u < .5, c[0] + (c[1] - c[0]) * (u / .5), c[1] + (c[2] - c[1]) * ((u - .5) / .5))


def _orb_master(D, kind):
    """glass orb sprite (RGBA, D x D). kind: 'dim' smoky grey glass | 'lit' gradient light inside | 'red' (✗)."""
    def mk():
        ss = 2; N = D * ss
        yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
        c = (N - 1) / 2; R = N / 2 - 1.0 * ss
        nx, ny = (xx - c) / R, (yy - c) / R; r2 = nx * nx + ny * ny; r = np.sqrt(r2)
        inside = np.clip((1 - r) * R / ss + .5, 0, 1)
        nz = np.sqrt(np.clip(1 - r2, 0, 1)); fres = 1 - nz
        rgb = np.zeros((N, N, 3), np.float32); a = np.zeros((N, N), np.float32)
        def over(col, al):
            nonlocal rgb, a
            al = np.clip(al, 0, 1); col = np.asarray(col, np.float32)
            rgb = col * al[..., None] + rgb * (1 - al[..., None]); a = al + a * (1 - al)
        def add(col, k):
            nonlocal rgb, a
            col = np.asarray(col, np.float32); k = np.clip(k, 0, None)
            rgb = rgb + col * k[..., None]; a = np.clip(a + k * .6, 0, 1)
        gx = _grad_x(nx * .5 + .5) / 255
        if kind == 'dim':
            over((.050, .052, .075), .58 + .36 * fres ** 1.6)
            add((.16, .17, .22), np.clip(ny, 0, 1) ** 2 * (r < 1) * .55)                    # transmitted light pooling low
            band = np.exp(-((ny + .02) / .09) ** 2) * fres ** 2.2
            add(gx * .55, band * .55)                                                         # monitor strip reflected
            rim = np.exp(-((1 - r) / .045) ** 2)
            over((.78, .80, .88), rim * .55)
        elif kind == 'red':
            over((.10, .025, .04), .66 + .30 * fres ** 1.6)
            add((.55, .08, .12), np.clip(ny, 0, 1) ** 2 * (r < 1) * .55)
            band = np.exp(-((ny + .02) / .09) ** 2) * fres ** 2.2
            add((.6, .25, .3), band * .45)
            rim = np.exp(-((1 - r) / .05) ** 2)
            over((1.0, .42, .46), rim * .75)
        else:   # lit
            over((.10, .07, .30), .80 + .18 * fres)
            vol = np.exp(-(r / .78) ** 2) * .55 + np.exp(-((r - .78) / .2) ** 2) * .55
            add(gx * 1.05, vol)
            caus = np.exp(-((r - .74) / .13) ** 2) * np.clip(ny, 0, 1) ** 1.6                  # caustic crescent at the bottom
            add(np.clip(gx * .55 + .55, 0, 1.2), caus * 1.25)
            band = np.exp(-((ny + .02) / .1) ** 2) * fres ** 1.8
            add((.75, .72, 1.0), band * .35)
            rim = np.exp(-((1 - r) / .06) ** 2)
            over(np.clip(gx * .55 + .5, 0, 1), rim * .95)
        # glass highlights: a curved softbox 'window' hugging the upper-left inside rim + a crisp glint + a kicker
        th = np.arctan2(ny, nx); dth = np.angle(np.exp(1j * (th - math.radians(-128))))
        win = np.exp(-((r - .80) / .085) ** 2) * np.clip(1 - (np.abs(dth) / .62) ** 2, 0, 1) ** 1.5
        over((1, 1, 1), win * (.62 if kind != 'dim' else .50))
        gl = np.exp(-(((nx + .40) / .075) ** 2 + ((ny + .47) / .060) ** 2))
        over((1, 1, 1), gl * .95)
        kick = np.exp(-((r - .86) / .06) ** 2) * np.clip(1 - (np.abs(np.angle(np.exp(1j * (th - math.radians(55))))) / .45) ** 2, 0, 1)
        over((1, 1, 1), kick * .30)
        rgb = rgb * inside[..., None]; a = a * inside
        # downsample (premultiplied) -> straight RGBA
        pm = rgb * a[..., None]
        pm = pm.reshape(D, ss, D, ss, 3).mean((1, 3)); a2 = a.reshape(D, ss, D, ss).mean((1, 3))
        col = np.where(a2[..., None] > 1e-4, pm / np.maximum(a2[..., None], 1e-4), 0)
        out = np.dstack([np.clip(col * 255, 0, 255), np.clip(a2 * 255, 0, 255)]).astype(np.uint8)
        return Image.fromarray(out, 'RGBA')
    return _c(('orb', D, kind), mk)


def _icon_mask(name, s):
    """white icon mask (L, s x s), drawn at 4x and rounded."""
    def mk():
        n = s * 4; m = Image.new('L', (n, n)); d = ImageDraw.Draw(m)
        P = lambda x, y: (x * n, y * n)
        if name == 'bolt':
            d.polygon([P(.50, .02), P(.80, .02), P(.58, .40), P(.84, .40), P(.30, .99), P(.45, .58), P(.18, .58)], fill=255)
        elif name == 'star':
            pts = []
            for k in range(10):
                ang = -math.pi / 2 + k * math.pi / 5; rr = .50 if k % 2 == 0 else .215
                pts.append(P(.5 + rr * math.cos(ang), .54 + rr * math.sin(ang)))
            d.polygon(pts, fill=255)
        elif name == 'tag':
            t = Image.new('L', (n, n)); dt = ImageDraw.Draw(t)
            dt.rounded_rectangle((*P(.30, .22), *P(.97, .78)), int(n * .08), fill=255)
            dt.polygon([P(.02, .50), P(.36, .22), P(.36, .78)], fill=255)
            dt.ellipse((*P(.20, .43), *P(.34, .57)), fill=0)
            f = E.font(int(n * .46), 800); dt.text(P(.64, .50), '$', font=f, fill=0, anchor='mm')
            t = t.filter(ImageFilter.GaussianBlur(n * .006)).point(lambda v: 255 if v > 127 else 0)
            t = t.rotate(-38, Image.BICUBIC, center=(n / 2, n / 2))
            m = t; d = None
        if d is not None:
            m = m.filter(ImageFilter.GaussianBlur(n * .012)).point(lambda v: 255 if v > 110 else 0)
        return m.resize((s, s), Image.LANCZOS)
    return _c(('icon', name, s), mk)


def _icon_sprite(name, s, kind):
    def mk():
        m = _icon_mask(name, s); pad = int(s * .35); W2 = s + 2 * pad
        out = Image.new('RGBA', (W2, W2), (0, 0, 0, 0))
        mm = Image.new('L', (W2, W2)); mm.paste(m, (pad, pad))
        if kind == 'lit':
            gl = mm.filter(ImageFilter.GaussianBlur(s * .12))
            g = Image.new('RGBA', (W2, W2), (176, 150, 255, 0)); g.putalpha(gl.point(lambda v: min(255, int(v * 2.0))))
            out.alpha_composite(g)
            sh = mm.filter(ImageFilter.GaussianBlur(s * .03))
            d = Image.new('RGBA', (W2, W2), (20, 10, 60, 0)); d.putalpha(sh.point(lambda v: int(v * .55)))
            out.alpha_composite(d, (0, int(s * .02)))
            gr = np.linspace(0, 1, W2, dtype=np.float32)[:, None, None]
            col = (np.array([255, 255, 255], np.float32) * (1 - gr * .55) + np.array([214, 204, 255], np.float32) * gr * .55)
            col = np.repeat(col, W2, 1)
            body = Image.fromarray(np.dstack([col, np.asarray(mm, np.float32)]).astype(np.uint8), 'RGBA')
            out.alpha_composite(body)
        else:
            col = (158, 160, 180) if kind == 'dim' else (222, 150, 158)
            sh = mm.filter(ImageFilter.GaussianBlur(s * .03))
            d = Image.new('RGBA', (W2, W2), (0, 0, 0, 0)); d.putalpha(sh.point(lambda v: int(v * .45)))
            out.alpha_composite(d, (0, int(s * .02)))
            body = Image.new('RGBA', (W2, W2), col + (0,)); body.putalpha(mm.point(lambda v: int(v * .86)))
            out.alpha_composite(body)
        return out
    return _c(('icon_s', name, s, kind), mk)


def _label_cap(px):
    def mk():
        f = E.font(int(px), 800); l, t, r, b = f.getbbox('FHE'); return float(b - t)
    return _c(('cap', int(px)), mk)


def _label_sprite(text, px, kind):
    """bold Outfit label; centred on the cap height. kind: lit | dim | red."""
    def mk():
        px_ = int(px); f = E.font(px_, 800); pad = int(px_ * .55)
        l, t, r, b = f.getbbox(text); lc, tc, rc, bc = f.getbbox('FHE')
        tr = px_ * .045; wds = [f.getbbox(ch)[2] - f.getbbox(ch)[0] for ch in text]
        tw = int(f.getlength(text) + tr * (len(text) - 1))
        W2, H2 = tw + 2 * pad, int(bc - tc) + 2 * pad
        m = Image.new('L', (W2, H2)); d = ImageDraw.Draw(m); x = pad
        for ch in text:
            d.text((x, pad - tc), ch, font=f, fill=255); x += f.getlength(ch) + tr
        out = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
        sh = m.filter(ImageFilter.GaussianBlur(px_ * .10))
        dk = Image.new('RGBA', (W2, H2), (6, 4, 16, 0)); dk.putalpha(sh.point(lambda v: int(v * .85)))
        out.alpha_composite(dk, (0, int(px_ * .04)))
        if kind == 'lit':
            gl = m.filter(ImageFilter.GaussianBlur(px_ * .22))
            g = Image.new('RGBA', (W2, H2), (128, 104, 255, 0)); g.putalpha(gl.point(lambda v: min(255, int(v * 1.25))))
            out.alpha_composite(g)
            gr = np.linspace(0, 1, H2, dtype=np.float32)[:, None, None]
            col = np.array([255, 255, 255], np.float32) * (1 - gr * .5) + np.array([206, 196, 255], np.float32) * gr * .5
            col = np.repeat(col, W2, 1)
            out.alpha_composite(Image.fromarray(np.dstack([col, np.asarray(m, np.float32)]).astype(np.uint8), 'RGBA'))
        else:
            col = (150, 152, 172) if kind == 'dim' else (214, 128, 138)
            body = Image.new('RGBA', (W2, H2), col + (0,)); body.putalpha(m.point(lambda v: int(v * .92)))
            out.alpha_composite(body)
        return out
    return _c(('label', text, int(px), kind), mk)


def _x_sprite(D):
    """the red ✗ (RGBA): a neon cross — red tube with a hot pink-white core, red glow, dark separation halo."""
    def mk():
        s = int(D * .90); pad = int(s * .45); N = s + 2 * pad; n = N * 3
        def bars(wf):
            m = Image.new('L', (n, n)); d = ImageDraw.Draw(m); c = n / 2; L = s * 3 * .5 - s * 3 * wf / 2; w = s * 3 * wf
            for sg in (1, -1):
                a, b = (c - L, c - sg * L), (c + L, c + sg * L)
                d.line([a, b], fill=255, width=int(w))
                for p in (a, b): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=255)
            return m.resize((N, N), Image.LANCZOS)
        tube, core = bars(.15), bars(.055)
        out = Image.new('RGBA', (N, N), (0, 0, 0, 0))
        dk = Image.new('RGBA', (N, N), (20, 0, 4, 0)); dk.putalpha(tube.filter(ImageFilter.GaussianBlur(s * .05)).point(lambda v: int(v * .7)))
        out.alpha_composite(dk)
        g = Image.new('RGBA', (N, N), (255, 30, 56, 0)); g.putalpha(tube.filter(ImageFilter.GaussianBlur(s * .13)).point(lambda v: min(255, int(v * 1.5))))
        out.alpha_composite(g)
        t_ = Image.new('RGBA', (N, N), (240, 36, 62, 0)); t_.putalpha(tube); out.alpha_composite(t_)
        c_ = Image.new('RGBA', (N, N), (255, 196, 204, 0)); c_.putalpha(core.filter(ImageFilter.GaussianBlur(.6))); out.alpha_composite(c_)
        return out
    return _c(('xmark', D), mk)


def _star_mask(R, rays=4, aniso=1.0):
    """star glint intensity (L, (2R+1)^2): hot core + thin rays (horizontal rays `aniso` x longer)."""
    def mk():
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32) / R
        r = np.hypot(xx, yy) + 1e-6
        core = np.exp(-(r / .07) ** 2) + .4 * np.exp(-(r / .2) ** 2)
        ray = np.zeros_like(r)
        for k in range(rays // 2):
            a = math.pi * k / (rays // 2)
            dd = np.abs(xx * math.sin(a) - yy * math.cos(a)); al = np.abs(xx * math.cos(a) + yy * math.sin(a))
            Lr = 1.0 if k == 0 else 1 / aniso
            ray += np.exp(-(dd / (.010 + .018 * al)) ** 2) * np.clip(1 - al / Lr, 0, 1) ** 2
        return Image.fromarray((np.clip(core + ray * .9, 0, 1) * 255).astype(np.uint8))
    return _c(('star', R, rays, aniso), mk)


def _lighter_at(canvas, sprite, x, y, k=1.0):
    """max-blend an L sprite (centred at x, y) into an L canvas, scaled by k."""
    if k <= .01: return
    if k < .999: sprite = sprite.point(lambda v, k=k: int(v * k))
    x0, y0 = int(round(x - sprite.width / 2)), int(round(y - sprite.height / 2))
    bx0, by0 = max(0, x0), max(0, y0); bx1, by1 = min(canvas.width, x0 + sprite.width), min(canvas.height, y0 + sprite.height)
    if bx1 <= bx0 or by1 <= by0: return
    reg = canvas.crop((bx0, by0, bx1, by1)); sp = sprite.crop((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0))
    canvas.paste(ImageChops.lighter(reg, sp), (bx0, by0))


def _falloff(R):
    """radial light falloff (L): gaussian core + long tail, radius scale R px."""
    R = max(2, int(R))
    def mk():
        n = int(R * 3.2); yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32) / R
        r2 = xx * xx + yy * yy
        v = .75 * np.exp(-r2 * 1.1) + .25 / (1 + r2 * 2.2)
        v *= np.clip(1.25 - np.sqrt(r2) / 3.2 * 1.25, 0, 1)
        return Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8))
    return _c(('falloff', R), mk)


def _add_at(canvas, sprite, x, y, k=1.0):
    """additively blend an L sprite (centred at x, y) into an L canvas, scaled by k."""
    if k <= .01: return
    if abs(k - 1) > .004: sprite = sprite.point(lambda v, k=k: int(min(255, v * k)))
    x0, y0 = int(round(x - sprite.width / 2)), int(round(y - sprite.height / 2))
    bx0, by0 = max(0, x0), max(0, y0); bx1, by1 = min(canvas.width, x0 + sprite.width), min(canvas.height, y0 + sprite.height)
    if bx1 <= bx0 or by1 <= by0: return
    reg = canvas.crop((bx0, by0, bx1, by1)); sp = sprite.crop((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0))
    canvas.paste(ImageChops.add(reg, sp), (bx0, by0))


def _scaled(im, s):
    if abs(s - 1) < .012: return im
    return im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.BILINEAR)


def _fade(im, k):
    if k >= .999: return im
    out = im.copy(); out.putalpha(im.getchannel('A').point(lambda v, k=max(0., k): int(v * k))); return out


def _put(base, im, x, y, alpha=1.0):
    """alpha-composite RGBA `im` centred at (x, y), clipped to base."""
    if im is None or alpha <= .01: return
    if alpha < .999: im = _fade(im, alpha)
    x0, y0 = int(round(x - im.width / 2)), int(round(y - im.height / 2))
    E._paste(base, dict(img=im, xy=(x0, y0), glass=0))


# ================================================================================================ crack network
def _net(seed, imp):
    """crack network in circumradius units (centroid origin): radial polylines, ring segments, cells (shards)."""
    def mk():
        rng = np.random.default_rng(seed)
        V = np.array([[0, -1], [-S60, .5], [S60, .5]]); Vx = V * 1.16          # real plate / expanded (halo) boundary
        P = np.array(imp, float)
        def hit(Vb, d):
            best = 1e9
            for i in range(3):
                a, b = Vb[i], Vb[(i + 1) % 3]; e = b - a
                den = d[0] * (-e[1]) - d[1] * (-e[0])
                if abs(den) < 1e-9: continue
                w = a - P; t = (w[0] * (-e[1]) - w[1] * (-e[0])) / den; u = (d[0] * w[1] - d[1] * w[0]) / den
                if t > 1e-6 and -1e-6 <= u <= 1 + 1e-6: best = min(best, t)
            return best
        N = 10; th = np.sort((np.arange(N) + rng.uniform(-.3, .3, N)) * 2 * math.pi / N + rng.uniform(0, 2 * math.pi))
        LV = [0., .14, .32, .58, 1.0]
        rad, Dreal = [], []
        for i in range(N):
            d = np.array([math.cos(th[i]), math.sin(th[i])]); nrm = np.array([-d[1], d[0]])
            Dx, Dr = hit(Vx, d), hit(V, d); Dreal.append(Dr)
            lv = [0.] + [LV[j] + rng.uniform(-.035, .035) for j in range(1, len(LV) - 1)] + [1.]
            pts, levels = [P.copy()], [0]
            for j in range(1, len(lv)):
                f0, f1 = lv[j - 1], lv[j]
                for q in (1 / 3, 2 / 3):
                    f = f0 + (f1 - f0) * q
                    pts.append(P + d * Dx * f + nrm * rng.normal(0, .016)); levels.append(-1)
                pts.append(P + d * Dx * f1 + (nrm * rng.normal(0, .012) if j < len(lv) - 1 else 0)); levels.append(j)
            rad.append(dict(pts=np.array(pts), lev=levels, Dx=Dx, Dr=Dr, th=th[i], delay=rng.uniform(0, .22)))
        # ring segments between radial i and i+1 at level j (one jittered midpoint)
        rings = {}
        for i in range(N):
            a_, b_ = rad[i], rad[(i + 1) % N]
            for j in range(1, len(LV) - 1):
                pa = a_['pts'][a_['lev'].index(j)]; pb = b_['pts'][b_['lev'].index(j)]
                mid = (pa + pb) / 2 + (P - (pa + pb) / 2) * rng.uniform(-.12, .12)
                rings[(i, j)] = dict(pts=np.array([pa, mid, pb]), t=.36 + .13 * j + rng.uniform(0, .14), show=rng.random() > .22)
        # cells
        cells = []
        for i in range(N):
            a_, b_ = rad[i], rad[(i + 1) % N]
            for j in range(len(LV) - 1):
                ia0, ia1 = a_['lev'].index(j), a_['lev'].index(j + 1); ib0, ib1 = b_['lev'].index(j), b_['lev'].index(j + 1)
                poly = list(a_['pts'][ia0:ia1 + 1])
                if j + 1 < len(LV) - 1: poly.append(rings[(i, j + 1)]['pts'][1])
                else:   # outer cell: expanded-boundary corners between the two rays
                    t0, t1 = a_['th'], b_['th'] + (2 * math.pi if i == N - 1 else 0)
                    cs = []
                    for v in Vx:
                        ph = math.atan2(v[1] - P[1], v[0] - P[0])
                        while ph < t0: ph += 2 * math.pi
                        if ph < t1: cs.append((ph, v))
                    poly += [v for _, v in sorted(cs, key=lambda q: q[0])]
                poly += list(b_['pts'][ib0:ib1 + 1][::-1])
                if j > 0: poly.append(rings[(i, j)]['pts'][1])
                poly = np.array(poly)
                cen = poly.mean(0)
                cells.append(dict(poly=poly, c=cen, j=j, r=[rng.random() for _ in range(8)]))
        return dict(P=P, rad=rad, rings=rings, cells=cells, N=N)
    return _c(('net', seed, tuple(imp)), mk)


def _polyline_part(pts, frac):
    """leading part of a polyline (by arc length)."""
    if frac >= 1: return pts
    if frac <= 0: return pts[:1]
    seg = np.hypot(*np.diff(pts, axis=0).T); L = seg.sum() * frac; acc = 0.; out = [pts[0]]
    for k, s in enumerate(seg):
        if acc + s >= L:
            out.append(pts[k] + (pts[k + 1] - pts[k]) * ((L - acc) / max(s, 1e-9))); break
        out.append(pts[k + 1]); acc += s
    return np.array(out)


def _crack_paths(st, G):
    """visible crack polylines in local px (N,3) with intensities, for crack value c."""
    c = st['crack']; net = _net(st['seed'], tuple(st['impact'])); R = G.R; out = []
    if c <= 0: return out
    for rd in net['rad']:
        g = eout(clamp((c - rd['delay']) / .42))
        if g <= 0: continue
        pts = rd['pts']; frac_real = rd['Dr'] / rd['Dx']
        # cut at the plate edge
        seg = np.hypot(*np.diff(pts, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)])
        P0 = net['P']; dist = np.hypot(*(pts - P0).T) / rd['Dx']
        k = int(np.searchsorted(dist, frac_real)); k = max(1, min(k, len(pts) - 1))
        a_, b_ = pts[k - 1], pts[k]; da, db = dist[k - 1], dist[k]
        cut = a_ + (b_ - a_) * clamp((frac_real - da) / max(db - da, 1e-9))
        real = np.vstack([pts[:k], cut[None]])
        out.append((_polyline_part(real, g), 1.0))
    for (i, j), rg in net['rings'].items():
        if not rg['show']: continue
        q = eout(clamp((c - rg['t']) / .12))
        if q <= 0: continue
        pts = rg['pts']
        # skip ring pieces outside the plate (beyond the real boundary)
        if not all(_in_tri(p) for p in pts): continue
        out.append((_polyline_part(pts, q), .8))
    res = []
    for pts, I in out:
        P3 = np.zeros((len(pts), 3)); P3[:, :2] = pts * R; res.append((P3, I))
    return res


def _in_tri(p, m=1.0):
    V = np.array([[0, -1], [-S60, .5], [S60, .5]]) * m
    s = []
    for i in range(3):
        a, b = V[i], V[(i + 1) % 3]
        s.append((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))
    return all(v >= -1e-6 for v in s) or all(v <= 1e-6 for v in s)


# ================================================================================================ field cache
def _field(cw2, ch2, Cx, Cy, R):
    """LUMARC gradient light field (ch2, cw2, 3) float32 over the whole half-res canvas (callers slice their region);
    cached per (canvas, centroid, radius) — constant while the triangle only rotates."""
    Cx, Cy, R = int(round(Cx)), int(round(Cy)), max(1, int(round(R)))      # rounded: independent of call history
    key = ('field', cw2, ch2, Cx, Cy, R)
    if key in _C: return _C[key]
    old = [k for k in _C if k[0] == 'field']
    if len(old) > 6:
        for k in old: del _C[k]
    xs = (np.arange(cw2, dtype=np.float32) - Cx) / R; ys = (np.arange(ch2, dtype=np.float32) - Cy) / R
    u = .5 + .40 * xs[None, :] - .10 * ys[:, None]
    _C[key] = _grad_x(u).astype(np.float32); return _C[key]


# ================================================================================================ the light + glass layer
HOT = np.array([255, 250, 255], np.float32)


def _light_layer(st, G, cw, ch, crack_override=None, skip_extra=False):
    """RGBA (canvas size) with the glass plate, rods, beams, halos, cracks, rings, stars, bloom."""
    x0, y0, x1, y1 = G.bbox()
    x0 = max(0, int(x0) // 8 * 8); y0 = max(0, int(y0) // 8 * 8)
    x1 = min(cw, int(math.ceil(x1 / 8) * 8)); y1 = min(ch, int(math.ceil(y1 / 8) * 8))
    w, h = (x1 - x0) // 8 * 8, (y1 - y0) // 8 * 8
    if w < 8 or h < 8: return None, (0, 0)
    S = G.S; u = S / 900.
    # crisp cores: 2x supersampled over the triangle's own bbox; big transient rings go to a 1x canvas
    P_ = np.array([n['p'] for n in G.nodes]); mg = max(n['s'] for n in G.nodes) * 2.8 + 130 * u
    cx0 = max(x0, int(P_[:, 0].min() - mg)); cy0 = max(y0, int(P_[:, 1].min() - mg))
    cx1 = min(x0 + w, int(P_[:, 0].max() + mg) + 1); cy1 = min(y0 + h, int(P_[:, 1].max() + mg) + 1)
    if cx1 <= cx0 or cy1 <= cy0: cx0, cy0, cx1, cy1 = x0, y0, x0 + 2, y0 + 2
    core = Image.new('L', (2 * (cx1 - cx0), 2 * (cy1 - cy0))); dc = ImageDraw.Draw(core)
    core1 = None
    def Tc(x, y): return ((x - cx0) * 2, (y - cy0) * 2)
    gh = Image.new('L', (w // 2, h // 2)); dh = ImageDraw.Draw(gh)
    gq = Image.new('L', (w // 4, h // 4)); dq = ImageDraw.Draw(gq)
    g8 = Image.new('L', (w // 8, h // 8)); d8 = ImageDraw.Draw(g8)
    plate = Image.new('L', (w // 2, h // 2)); dp = ImageDraw.Draw(plate)
    def T(p, s):
        if s == .5: return ((p[0] - cx0) * 2, (p[1] - cy0) * 2)
        return ((p[0] - x0) / s, (p[1] - y0) / s)
    def line(dr, a, b, s, width, val, caps=True):
        if val <= .5: return
        A, B = T(a, s), T(b, s); dr.line([A, B], fill=int(min(255, val)), width=max(1, int(round(width))))
        if caps and width >= 3:
            rr = width / 2
            for p in (A, B): dr.ellipse((p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr), fill=int(min(255, val)))
    glow = st['glow']
    # ---- plate
    if G.plate_a > .01:
        pts, _ = G.proj(G.Vl)
        dp.polygon([T(p, 2) for p in pts], fill=int(255 * G.plate_a))
    # ---- rods (dim glass edges) + beams
    order = sorted(G.edges, key=lambda e: e['I'])
    for e in order:
        if e['d'] <= .002 or e['rod'] <= .01: continue
        a, b = e['a'], e['b']; hd = a + (b - a) * e['d']
        line(dc, a, hd, .5, 2 * 1.8 * u, 255 * .32 * e['rod'])
        I = e['I']
        if I > .01:
            line(dc, a, hd, .5, 2 * 3.4 * u * min(1.5, .75 + .25 * I), 255 * min(1, .6 + .4 * I))
            line(dh, a, hd, 2, 10 * u / 2, 255 * min(1, 1.0 * I))
            line(dq, a, hd, 4, 28 * u / 4, 255 * min(1, .78 * I))
            line(d8, a, hd, 8, 44 * u / 8, 255 * min(1, (.35 + .9 * G.bloom) * I))
            if st['flow'] is not None and e['d'] > .99:
                for q in range(2):
                    ph = (st['flow'] * 1.0 + q * .5 + e['j'] * .29) % 1.0
                    c0, c1 = a + (b - a) * max(0, ph - .07), a + (b - a) * min(1, ph + .07)
                    line(dc, c0, c1, .5, 2 * 3.6 * u, 255 * min(1, .8 * I))
                    line(dh, c0, c1, 2, 12 * u / 2, 255 * min(1, I))
        if 0 < e['d'] < 1:     # hot spark at the head of a drawing edge
            k = max(.6, I) * glow
            _lighter_at(core, _star_mask(int(26 * u * 2), 4, 1.4), *Tc(hd[0], hd[1]), min(1, k))
            rr = 10 * u / 2; p = T(hd, 2); dh.ellipse((p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr), fill=int(255 * min(1, k)))
    # ---- node halos (lit) + assemble lock rings
    for n in G.nodes:
        if n['a'] <= .01: continue
        L = n['lit'] * glow * G.boost * n['a'] * (1 - .8 * clamp(n['x']))
        if L > .01:
            p = T(n['p'], 4); _add_at(gq, _falloff(n['s'] * 1.05 / 4), p[0], p[1], min(1.6, .62 * L))
            p = T(n['p'], 2); rr = n['s'] * 1.03 / 2
            dh.ellipse((p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr), fill=int(255 * min(1, .5 * L)))
            p = T(n['p'], 8); _add_at(g8, _falloff(n['s'] * 1.6 / 8), p[0], p[1], min(1.5, (.2 + .7 * G.bloom) * L))
        a = st['assemble']
        if a < 1:
            q = (a - (.12 * n['i'] + .34)) / .12
            if 0 < q < 1:
                rr = n['s'] * (1.05 + 1.5 * eout(q)); I = (1 - q) ** 1.5
                p = T(n['p'], .5); dc.ellipse((p[0] - 2 * rr, p[1] - 2 * rr, p[0] + 2 * rr, p[1] + 2 * rr), outline=int(255 * I), width=max(2, int(4 * u)))
                p = T(n['p'], 2); dh.ellipse((p[0] - rr / 2, p[1] - rr / 2, p[0] + rr / 2, p[1] + rr / 2), outline=int(255 * I * .8), width=max(1, int(5 * u)))
    # ---- cracks (light leaking through the fissures) + impact
    cst = dict(st, crack=crack_override) if crack_override is not None else st
    if cst['crack'] > 0 and G.tri_a > .01:
        for P3, I in _crack_paths(cst, G):
            pts, _ = G.proj(P3)
            if len(pts) < 2: continue
            dc.line([T(p, .5) for p in pts], fill=int(255 * .95 * I), width=max(2, int(2.4 * u)), joint='curve')
            dh.line([T(p, 2) for p in pts], fill=int(255 * .62 * I), width=max(1, int(6 * u / 2)))
        if not skip_extra:
            c = cst['crack']; net = _net(st['seed'], tuple(st['impact']))
            ip, _ = G.proj(np.array([[net['P'][0] * G.R, net['P'][1] * G.R, 0]]))
            k = math.exp(-c / .12) * clamp(c * 30) * 1.0 + .35 * clamp(c * 6)
            _lighter_at(core, _star_mask(int(60 * u * 2), 8, 1.3), *Tc(ip[0][0], ip[0][1]), min(1, k))
            p = T(ip[0], 4); _add_at(gq, _falloff(30 * u / 4 * (1 + 2 * math.exp(-c / .1))), p[0], p[1], min(1.3, 1.2 * math.exp(-c / .15) + .25))
    # ---- complete: shockwave rings + node stars
    c = st['complete']
    if 0 < c and not skip_extra:
        ang = np.linspace(0, 2 * math.pi, 97)
        for (dur, rmul, I0, wd) in ((.6, 1.0, 1.0, 1.0), (.42, .78, .7, .6)):
            q = c / dur
            if q >= 1: continue
            rr = G.R * (.15 + st['ring'] * rmul * eout(q)); I = I0 * (1 - q) ** 1.6
            P3 = np.stack([np.cos(ang) * rr, np.sin(ang) * rr, np.zeros_like(ang)], 1)
            pts, _ = G.proj(P3)
            if core1 is None: core1 = Image.new('L', (w, h)); dc1 = ImageDraw.Draw(core1)
            dc1.line([T(p, 1) for p in pts], fill=int(255 * I * .7), width=max(2, int(2.5 * u * wd)), joint='curve')
            dh.line([T(p, 2) for p in pts], fill=int(255 * I * .9), width=max(1, int(16 * u * wd / 2)))
            P3t = P3 * (1 - .10 * (1 - q)); pt2, _ = G.proj(P3t)          # trailing wake behind the front
            dq.line([T(p, 4) for p in pt2], fill=int(255 * I * .55), width=max(1, int(70 * u * wd / 4)))
        k = bump(c / .3)
        if k > .01:
            for n in G.nodes:
                _lighter_at(core, _star_mask(int(110 * u * 2), 4, 1.6), *Tc(n['p'][0], n['p'][1]), k)
    # ---- logo: collapse flash + orbit ring
    lg = st['logo']
    if lg > .3 and not skip_extra:
        k = bump((lg - .33) / .26)
        if k > .01:
            _lighter_at(core, _star_mask(int(150 * u * 2), 4, 1.8), *Tc(G.T[0], G.T[1]), k)
            p = T(G.T, 4); _add_at(gq, _falloff(60 * u / 4), p[0], p[1], 1.4 * k)
        kg = .55 * smooth((lg - .45) / .3)
        if kg > .01:
            p = T(G.T, 8); _add_at(g8, _falloff(G.LW * .2 / 8), p[0], p[1], kg)
        q = (lg - .40) / .36
        if 0 < q < 1:
            rr = G.LW * (.06 + .5 * eout(q)); I = (1 - q) ** 1.4
            ang = np.linspace(0, 2 * math.pi, 97); tl = math.radians(-28)
            ex, ey = np.cos(ang) * rr, np.sin(ang) * rr * .42
            pts = np.stack([G.T[0] + ex * math.cos(tl) - ey * math.sin(tl), G.T[1] + ex * math.sin(tl) + ey * math.cos(tl)], 1)
            if core1 is None: core1 = Image.new('L', (w, h)); dc1 = ImageDraw.Draw(core1)
            dc1.line([T(p, 1) for p in pts], fill=int(255 * I), width=max(2, int(2.5 * u)), joint='curve')
            dh.line([T(p, 2) for p in pts], fill=int(255 * I * .8), width=max(1, int(7 * u)))
    # ---- bloom
    if G.bloom > .01 and G.tri_a > .01:
        pts, _ = G.proj(G.Vl)
        d8.polygon([T(p, 8) for p in pts], fill=int(255 * min(1, .55 * G.bloom * glow)))
    # ---- compose (half res for the glows, full res for the cores)
    gh = gh.filter(ImageFilter.GaussianBlur(3.0 * u))
    gq = gq.filter(ImageFilter.GaussianBlur(4.5 * u))
    g8 = g8.filter(ImageFilter.GaussianBlur(5.5 * u))
    w2, h2 = w // 2, h // 2
    gl = ImageChops.add(ImageChops.add(gh, gq.resize((w2, h2), Image.BILINEAR)), g8.resize((w2, h2), Image.BILINEAR))
    Gm = np.asarray(gl, np.float32) * (1 / 255)
    fx0, fy0 = x0 // 2, y0 // 2
    F = _field((cw + 1) // 2 + 8, (ch + 1) // 2 + 8, G.C[0] / 2, G.C[1] / 2, G.R / 2)[fy0:fy0 + h2, fx0:fx0 + w2]
    hot = .34 * Gm * Gm
    rgb = F * Gm[..., None]; rgb += (hot * 255)[..., None]
    la = np.minimum(Gm + hot, 1.0)                     # the field's blue channel is always 255 -> max channel
    a_half = la
    pb = plate.getbbox() if G.plate_a > .01 else None
    if pb:                                             # glass plate: only inside its own bbox
        px0, py0, px1, py1 = max(0, pb[0] - 2), max(0, pb[1] - 2), min(w2, pb[2] + 2), min(h2, pb[3] + 2)
        Pm = np.asarray(plate.crop((px0, py0, px1, py1)), np.float32) * (1 / 255)
        xs = np.arange(px0, px1, dtype=np.float32)[None, :] - (G.C[0] - x0) / 2; ys = np.arange(py0, py1, dtype=np.float32)[:, None] - (G.C[1] - y0) / 2
        Rh = G.R / 2; ph = (st['yaw'] * .022 + st['roll'] * .012 - st['pitch'] * .01)
        q = (xs * .5 + ys * .866) * (1 / Rh)
        sheen = .8 * np.exp(-((q - (-.02 + ph)) * (1 / .36)) ** 2) + .55 * np.exp(-((q - (.40 + ph)) * (1 / .06)) ** 2)
        topl = np.clip(.5 - .3 * (ys / Rh + 1), 0, .5)
        pg = G.plate_glow
        ga = Pm * (.20 + .11 * sheen + .10 * topl + .30 * pg)
        lw_ = la[py0:py1, px0:px1]
        gpm = Pm[..., None] * ((.09 * sheen + .06 * topl + .002)[..., None] * 255 + (.30 * pg) * F[py0:py1, px0:px1])
        rgb[py0:py1, px0:px1] += gpm * (1 - lw_)[..., None]
        a_half = la.copy(); a_half[py0:py1, px0:px1] = 1 - (1 - ga) * (1 - lw_)
    rgbh = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), 'RGB').resize((w, h), Image.BILINEAR)
    ah = Image.fromarray(np.clip(a_half * 255, 0, 255).astype(np.uint8), 'L').resize((w, h), Image.BILINEAR)
    crs = core.reduce(2)
    if core1 is None and (cx0, cy0, crs.width, crs.height) == (x0, y0, w, h): cr = crs
    else:
        cr = core1 if core1 is not None else Image.new('L', (w, h))
        bx, by = cx0 - x0, cy0 - y0; reg = cr.crop((bx, by, bx + crs.width, by + crs.height))
        cr.paste(ImageChops.lighter(reg, crs), (bx, by))
    rgbf = ImageChops.add(rgbh, Image.merge('RGB', (cr, cr, cr)))
    af = ImageChops.lighter(ah, cr)
    img = Image.merge('RGBa', (*rgbf.split(), af)).convert('RGBA')
    return img, (x0, y0)


# ================================================================================================ orbs, icons, ✗, labels
def _orb_img(n, S, kind_mix=True):
    """composited orb (+ icon + ✗) sprite for node n at its current size."""
    D = int(round(2 * K_ORB * S * 1.7))
    lit, x = clamp(n['lit']), clamp(n['x'])
    dim = _orb_master(D, 'dim')
    o = dim if lit < .01 else (_orb_master(D, 'lit') if lit > .99 else Image.blend(dim, _orb_master(D, 'lit'), lit))
    if x > .01: o = Image.blend(o, _orb_master(D, 'red'), min(1, x * 1.4) * .85)
    o = o.copy()
    s_ic = int(D * .56); ic_d = _icon_sprite(ICONS[n['i']], s_ic, 'dim')
    if lit > .01:
        ic = ic_d if lit < .01 else Image.blend(ic_d, _icon_sprite(ICONS[n['i']], s_ic, 'lit'), lit)
    else: ic = ic_d
    if x > .01: ic = Image.blend(ic, _icon_sprite(ICONS[n['i']], s_ic, 'red'), min(1, x * 1.4) * .7)
    pad = max(0, (ic.width - D) // 2 + 1)
    base = Image.new('RGBA', (D + 2 * pad, D + 2 * pad), (0, 0, 0, 0)); base.alpha_composite(o, (pad, pad))
    off = {0: (-.005, .0), 1: (.0, .0), 2: (.0, -.02)}[n['i']]
    base.alpha_composite(ic, (int(base.width / 2 - ic.width / 2 + off[0] * D), int(base.height / 2 - ic.height / 2 + off[1] * D)))
    return base, D


def _draw_nodes(out, st, G, ox=0, oy=0, with_labels=True, with_orbs=True):
    S = G.S
    for n in sorted(G.nodes, key=lambda q: -q['z']):
        if n['a'] <= .01: continue
        if with_orbs:
            img, D = _orb_img(n, S)
            s = 2 * n['s'] / (D * 1.0) if D else 1
            im = _scaled(img, s * img.width / img.width)
            _put(out, im, n['p'][0] - ox, n['p'][1] - oy, n['a'])
            x = clamp(n['x'])
            if x > .01:
                xs = _x_sprite(D); k = 1 + .9 * (1 - back(clamp(x / .9), 2.2))
                _put(out, _scaled(xs, s * k), n['p'][0] - ox, n['p'][1] - oy, n['a'] * clamp(x * 3))
    if with_labels:
        for n in G.nodes:
            if n['la'] <= .01: continue
            lit, x = clamp(n['lit']), clamp(n['x']); text = st['labels'][n['i']]; px = n['lab_px']
            lab = _label_sprite(text, px, 'dim')
            if lit > .01: lab = Image.blend(lab, _label_sprite(text, px, 'lit'), lit)
            if x > .01: lab = Image.blend(lab, _label_sprite(text, px, 'red'), x * .8)
            p = G.label_pos(n)
            _put(out, _scaled(lab, n['lab_k']), p[0] - ox, p[1] - oy, n['la'])


# ================================================================================================ shatter
def _star_rgba(R, rays=4, aniso=1.0, col=(240, 234, 255)):
    def mk():
        m = _star_mask(R, rays, aniso); im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m); return im
    return _c(('star_rgba', R, rays, aniso, col), mk)


def _shard_kit(st, G):
    """the intact triangle rendered FLAT (no yaw/pitch/roll, cracks complete) and cut into its shards — cached, so a
    shatter only pays for the per-piece transforms.  Pieces: plate cells (carry plate + beams + cracks) and 6 wedges
    per orb (carry the orb, its icon and ✗)."""
    key = ('shards', G.S, round(st['scale'], 4), st['lit'], st['x'], st['edge'], st['draw'], st['pop'], round(st['glow'], 3),
           round(st['plate'], 3), round(st['complete'], 3), st['seed'], tuple(st['impact']))
    if key in _C: return _C[key]
    for k in [k for k in _C if k[0] == 'shards']: del _C[k]
    S = G.S; cw = ch = int(S * 1.7) // 8 * 8
    flat = dict(st, shatter=0., yaw=0., pitch=0., roll=0., assemble=1., logo=0., crack=1.0, flow=None)
    G0 = _G(flat, S, cw / 2, ch / 2)
    A, (ax, ay) = _light_layer(flat, G0, cw, ch, skip_extra=True)
    B = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); _draw_nodes(B, flat, G0, with_labels=False)
    net = _net(st['seed'], tuple(st['impact'])); R = G0.R
    def cut(img, offx, offy, P2):
        bx0, by0 = np.floor(P2.min(0)).astype(int) - 1; bx1, by1 = np.ceil(P2.max(0)).astype(int) + 1
        crop = img.crop((bx0 - offx, by0 - offy, bx1 - offx, by1 - offy))
        m = Image.new('L', crop.size); ImageDraw.Draw(m).polygon([(p[0] - bx0, p[1] - by0) for p in P2], fill=255)
        crop.putalpha(ImageChops.multiply(crop.getchannel('A'), m))
        return crop, P2 - np.array([bx0, by0])
    pieces = []
    if A is not None:
        for cell in net['cells']:
            P3 = np.zeros((len(cell['poly']), 3)); P3[:, :2] = cell['poly'] * R
            crop, sp = cut(A, ax, ay, G0.C + P3[:, :2])
            pieces.append(dict(src='A', P=P3, img=crop, sp=sp, rn=cell['r']))
    for n in G0.nodes:
        i = n['i']; cen = G0.Vl[i]; rr = n['s'] * 1.1
        nw = 6; ph0 = hrand(i, 3) * 6.28
        for w_ in range(nw):
            a0 = ph0 + 2 * math.pi * (w_ + .18 * (hrand(w_, i) - .5)) / nw
            a1 = ph0 + 2 * math.pi * (w_ + 1 + .18 * (hrand(w_ + 1, i) - .5)) / nw
            cj = np.array([(hrand(w_, 9) - .5) * .1 * rr, (hrand(w_, 11) - .5) * .1 * rr, 0])
            pts = np.array([cen + cj] + [cen + np.array([math.cos(t) * rr, math.sin(t) * rr, 0]) for t in np.linspace(a0, a1, 7)])
            crop, sp = cut(B, 0, 0, G0.C + pts[:, :2])
            pieces.append(dict(src='B', P=pts, img=crop, sp=sp, rn=[hrand(w_ * 7 + k, i + 20) for k in range(8)]))
    _C[key] = pieces
    return pieces


def _shatter(out, st, G, cw, ch):
    """plate cells + orb wedges fly apart in 3-D (released by a wave from the impact, drag + gravity + tumble),
    light catches as raking gradients + bright bevels + star glints, glass dust, the burst flash; labels drop."""
    s = st['shatter']; Tm = s * 1.15; u = G.S / 900.
    pieces = _shard_kit(st, G)
    net = _net(st['seed'], tuple(st['impact'])); R = G.R; f = G.f; M = G.M
    Pc = np.array([net['P'][0] * R, net['P'][1] * R, 0.]) @ M.T
    Lh = np.array([-.42, -.62, -1.0]); Lh /= np.linalg.norm(Lh); H = Lh + np.array([0, 0, -1.]); H /= np.linalg.norm(H)
    n0 = M @ np.array([0, 0, -1.])
    def project(Q):
        k = f / np.maximum(f + Q[:, 2], f * .08); return G.C + Q[:, :2] * k[:, None]
    drawn = []
    for pc in pieces:
        rn = pc['rn']; Q = pc['P'] @ M.T
        c = Q.mean(0); dist = np.linalg.norm((c - Pc)[:2]) / R
        t0 = .05 * dist + (.02 if pc['src'] == 'B' else 0); tau = max(0., Tm - t0)
        dxy = (c - Pc)[:2]; nd = np.linalg.norm(dxy); dxy = dxy / nd if nd > 1e-6 else np.array([rn[0] - .5, rn[1] - .5])
        sp = R * (1.5 + 1.9 * rn[2]) * (1.15 if pc['src'] == 'B' else 1)
        vel = np.array([dxy[0] * sp, dxy[1] * sp - R * .5 * rn[3], -R * (.6 + 2.4 * rn[4])])
        disp = vel * (1 - math.exp(-1.7 * tau)) / 1.7 + np.array([0, .9 * R * tau * tau, 0])
        ax_ = np.array([rn[5] - .5, rn[6] - .5, rn[7] - .5 + .2]); ax_ /= max(np.linalg.norm(ax_), 1e-6)
        Rk = _axis_rot(ax_, (2.5 + 7 * rn[1]) * tau * (1 if rn[0] > .5 else -1))
        Q2 = c + (Q - c) @ Rk.T + disp
        if np.min(f + Q2[:, 2]) < f * .2: continue
        alpha = 1 - smooth((Tm - .45 - .3 * rn[2]) / .3)          # every piece is gone by shatter = 1
        if alpha <= .01: continue
        catch = clamp((abs(float((Rk @ n0) @ H)) - .93) / .07) ** 2 if tau > 0 else 0.
        drawn.append((float(c[2] + disp[2]), pc, project(Q2), alpha, catch, tau))
    drawn.sort(key=lambda q: -q[0])
    edges, glints = [], []
    for z, pc, P1, alpha, catch, tau in drawn:
        dx0, dy0 = np.floor(P1.min(0)).astype(int) - 1; dx1, dy1 = np.ceil(P1.max(0)).astype(int) + 1
        if dx1 < 0 or dy1 < 0 or dx0 > cw or dy0 > ch: continue
        sp_ = pc['sp']; n_ = len(sp_); ids = [0, n_ // 3, (2 * n_) // 3]
        Am = np.array([[P1[i][0] - dx0, P1[i][1] - dy0, 1] for i in ids], float)
        if abs(np.linalg.det(Am)) < 1e-3: continue
        cx_ = np.linalg.solve(Am, [sp_[i][0] for i in ids]); cy_ = np.linalg.solve(Am, [sp_[i][1] for i in ids])
        piece = pc['img'].transform((int(dx1 - dx0), int(dy1 - dy0)), Image.AFFINE, (*cx_, *cy_), Image.BILINEAR)
        if catch > .02:     # light catch: a raking gradient across the face (not a flat fill)
            rn = pc['rn']; pw, ph_ = piece.size
            gx_ = np.linspace(0, 1, pw, dtype=np.float32)[None, :]; gy_ = np.linspace(0, 1, ph_, dtype=np.float32)[:, None]
            ramp = np.clip(.5 + (gx_ - .5) * (rn[5] - .5) * 2.4 + (gy_ - .5) * (rn[6] - .5) * 2.4, 0, 1) ** 1.6
            fa = np.asarray(piece.getchannel('A'), np.float32) * ramp * (.75 * catch)
            fl = Image.new('RGBA', piece.size, (250, 246, 255, 0)); fl.putalpha(Image.fromarray(fa.astype(np.uint8)))
            piece.alpha_composite(fl)
        _put(out, piece, (dx0 + dx1) / 2, (dy0 + dy1) / 2, alpha)
        if tau > 0:
            ea = int(255 * alpha * min(1, .22 + .75 * catch))
            if ea > 4: edges.append((P1, ea))
            if catch > .5: glints.append((P1[int(np.argmin(P1[:, 1]))], catch * alpha))
    # bevels, glints, dust, burst: one overlay limited to the canvas
    dust = []
    rng = np.random.default_rng(st['seed'] + 99)
    for q in range(70):
        ang = rng.uniform(0, 2 * math.pi); rr = rng.uniform(.05, .9) * R; sp = R * rng.uniform(1.4, 3.6); a_r = rng.uniform(.4, 1)
        tau = Tm - .05 * rr / R
        if tau <= 0: continue
        a_ = clamp(1 - tau / .7) * a_r
        if a_ <= .02: continue
        d = np.array([math.cos(ang), math.sin(ang)]); p0 = Pc[:2] + d * rr
        pos = lambda tt: G.C + p0 + d * sp * (1 - math.exp(-2 * tt)) / 2 + np.array([0, .8 * R * tt * tt])
        dust.append((pos(tau), pos(max(0, tau - .025)), a_))
    od = ImageDraw.Draw(out, 'RGBA')
    for P1, ea in edges: od.line([tuple(p) for p in P1] + [tuple(P1[0])], fill=(255, 255, 255, ea), width=max(1, int(2 * u)))
    for pa, pb, a_ in dust: od.line([tuple(pa), tuple(pb)], fill=(236, 228, 255, int(255 * a_)), width=max(1, int(2 * u)))
    for p, k in glints: _put(out, _star_rgba(int(44 * u), 4, 1.5), p[0], p[1], k)
    ip = project(Pc[None])[0]; k = math.exp(-Tm / .07) * clamp(Tm * 40)
    if k > .01:
        _put(out, _star_rgba(int(260 * u), 8, 1.4), ip[0], ip[1], k)
        _put(out, _star_rgba(int(120 * u), 4, 1.0, (190, 170, 255)), ip[0], ip[1], k)
    # labels drop + fade
    for n in G.nodes:
        k = clamp(1 - Tm * 5.0) * n['la']
        if k <= .01: continue
        lit, x = clamp(n['lit']), clamp(n['x']); text = st['labels'][n['i']]
        lab = _label_sprite(text, n['lab_px'], 'dim')
        if lit > .01: lab = Image.blend(lab, _label_sprite(text, n['lab_px'], 'lit'), lit)
        if x > .01: lab = Image.blend(lab, _label_sprite(text, n['lab_px'], 'red'), x * .8)
        p = G.label_pos(n) + np.array([0, G.R * .5 * Tm * Tm + G.R * .15 * Tm])
        _put(out, _scaled(lab, n['lab_k']), p[0], p[1], k)


# ================================================================================================ logo
def _logo_layer(out, st, G):
    lg = st['logo']; v = clamp((lg - .44) / .40)
    if v <= 0: return
    LW = int(round(G.LW)); logo = E.logo(LW); lh = logo.height
    sp = int(LW * LOGO_SPLIT); mark, word = logo.crop((0, 0, sp, lh)), logo.crop((sp, 0, LW, lh))
    core = (LOGO_CORE[0] * LW, LOGO_CORE[1] * lh)
    s = .25 + .75 * back(v, 1.9); rot = -40 * (1 - eout(v)); a = clamp(v * 3.5)
    # mark: scale + rotate about its core, core lands on G.T
    rr = math.radians(rot); cs, sn = math.cos(rr), math.sin(rr)
    corners = [(0, 0), (sp, 0), (sp, lh), (0, lh)]
    dst = [(G.T[0] + s * ((x - core[0]) * cs - (y - core[1]) * sn), G.T[1] + s * ((x - core[0]) * sn + (y - core[1]) * cs)) for x, y in corners]
    dx0, dy0 = int(min(p[0] for p in dst)) - 2, int(min(p[1] for p in dst)) - 2
    dx1, dy1 = int(max(p[0] for p in dst)) + 2, int(max(p[1] for p in dst)) + 2
    # output -> input: inverse similarity
    ic, isn = math.cos(-rr) / s, math.sin(-rr) / s
    a_ = ic; b_ = -isn; d_ = isn; e_ = ic
    ox_, oy_ = dx0 - G.T[0], dy0 - G.T[1]
    c_ = core[0] + a_ * ox_ + b_ * oy_; f_ = core[1] + d_ * ox_ + e_ * oy_
    mk = mark.transform((dx1 - dx0, dy1 - dy0), Image.AFFINE, (a_, b_, c_, d_, e_, f_), Image.BICUBIC)
    # sheen on the mark + wordmark
    sh = clamp((lg - .80) / .2)
    _put(out, mk, (dx0 + dx1) / 2, (dy0 + dy1) / 2, a * st['alpha'] if False else a)
    w = clamp((lg - .58) / .30)
    if w > 0:
        ww, wh = word.size
        xs = np.arange(ww, dtype=np.float32) / ww
        ramp = np.clip((w * 1.25 - xs) / .25, 0, 1)
        wa = np.asarray(word.getchannel('A'), np.float32) * ramp[None, :]
        wd = word.copy(); wd.putalpha(Image.fromarray(wa.astype(np.uint8)))
        slide = (1 - eout(w)) * .04 * LW
        x_left = G.box[0] - LW / 2 + sp
        _put(out, wd, x_left + ww / 2 + slide, G.box[1], 1.0)
    if 0 < sh < 1:     # light sweep over the logo's own pixels
        x_l = G.box[0] - LW / 2; y_t = G.box[1] - lh / 2
        reg = out.crop((int(x_l), int(y_t), int(x_l) + LW, int(y_t) + lh))
        al = np.asarray(logo.getchannel('A'), np.float32) / 255
        xx = np.arange(LW, dtype=np.float32)[None, :] / LW; yy = np.arange(lh, dtype=np.float32)[:, None] / lh
        band = np.exp(-((xx + yy * .35 - (-.2 + 1.5 * sh)) / .06) ** 2) * bump(sh) * .85
        add = (band * al * 255).astype(np.uint8)
        L = Image.fromarray(add)
        col = Image.new('RGBA', (LW, lh), (255, 255, 255, 0)); col.putalpha(L)
        reg.alpha_composite(col); out.paste(reg, (int(x_l), int(y_t)))


# ================================================================================================ public API
def _setup(state, size, canvas, at):
    st = _norm(state); S = int(round(size))
    cw, ch = (canvas if canvas else (S, S)); ox, oy = (at if at else (cw / 2, ch / 2))
    return st, S, int(cw), int(ch), _G(st, S, float(ox), float(oy))


def render(state=None, size=900, canvas=None, at=None):
    """the triangle for `state` -> PIL RGBA (transparent bg), see the module docstring."""
    st, S, cw, ch, G = _setup(state, size, canvas, at)
    out = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    if st['alpha'] <= .01: return out
    if st['shatter'] >= 1: return out
    if st['shatter'] > 0:
        _shatter(out, st, G, cw, ch)
    else:
        img, (x0, y0) = _light_layer(st, G, cw, ch)
        if img is not None: out.paste(img, (x0, y0))
        if G.tri_a > .01: _draw_nodes(out, st, G)
        if st['logo'] > .44: _logo_layer(out, st, G)
    if st['alpha'] < .999: out = _fade(out, st['alpha'])
    return out


def anchor(name, state=None, size=900, canvas=None, at=None):
    """(x, y) of a named point in render()'s pixel space (see the module docstring)."""
    st, S, cw, ch, G = _setup(state, size, canvas, at)
    if name in NODES: p = G.nodes[NODES.index(name)]['p']
    elif name == 'center': p, _ = G.proj(np.zeros((1, 3))); p = p[0]
    elif name in EDGES:
        i0, i1 = EDGE_NODES[EDGES.index(name)]; p = (G.nodes[i0]['p'] + G.nodes[i1]['p']) / 2
    elif name.endswith('_label') and name[:-6] in NODES: p = G.label_pos(G.nodes[NODES.index(name[:-6])])
    elif name == 'top':
        n = G.nodes[0]; p = G.label_pos(n) - np.array([0, _label_cap(n['lab_px']) * n['lab_k'] / 2])
    elif name == 'bottom':
        n = G.nodes[1]; p = G.label_pos(n) + np.array([0, _label_cap(n['lab_px']) * n['lab_k'] / 2]); p = np.array([G.box[0], p[1]])
    elif name == 'logo': p = np.array(G.box)
    elif name == 'logo_core': p = G.T
    elif name == 'impact':
        net = _net(st['seed'], tuple(st['impact'])); p, _ = G.proj(np.array([[net['P'][0] * G.R, net['P'][1] * G.R, 0]])); p = p[0]
    else: raise KeyError(f'_tri.anchor: unknown name {name!r}')
    return float(p[0]), float(p[1])


def radius(state=None, size=900, node='fast', canvas=None, at=None):
    st, S, cw, ch, G = _setup(state, size, canvas, at)
    return float(G.nodes[NODES.index(node)]['s'])


def paste(base, state, size, x, y, frost=10):
    """composite the triangle (box centre x, y) onto a copy of `base`; frost = blur radius of what is behind the plate
    and the orbs (0 = none)."""
    base = base.convert('RGBA') if base.mode != 'RGBA' else base.copy()
    st, S, cw, ch, G = _setup(state, size, base.size, (x, y))
    if frost and st['shatter'] <= 0 and G.tri_a > .01 and st['alpha'] > .01:
        m = Image.new('L', base.size); d = ImageDraw.Draw(m)
        if G.plate_a > .01:
            pts, _ = G.proj(G.Vl); d.polygon([tuple(p) for p in pts], fill=int(255 * min(1, G.plate_a * st['alpha'])))
        for n in G.nodes:
            if n['a'] > .01:
                r_ = n['s'] * .97; d.ellipse((n['p'][0] - r_, n['p'][1] - r_, n['p'][0] + r_, n['p'][1] + r_), fill=int(255 * n['a'] * st['alpha']))
        bb = m.getbbox()
        if bb:
            pad = int(frost * 2); bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(base.width, bb[2] + pad), min(base.height, bb[3] + pad))
            reg = base.crop(bb).filter(ImageFilter.GaussianBlur(frost)); base.paste(reg, bb[:2], m.crop(bb))
    base.alpha_composite(render(state, size, canvas=base.size, at=(x, y)))
    return base


# ================================================================================================ demo
def _demo(bench_only=False):
    import time
    out_dir = os.path.join(E.HERE, 'out', 'tri'); os.makedirs(out_dir, exist_ok=True)
    S = 900
    bg_full = E.studio().convert('RGBA')
    bg = bg_full.crop((90, 380, 990, 1280)).filter(ImageFilter.GaussianBlur(6))
    bg = Image.blend(bg, Image.new('RGBA', bg.size, (8, 8, 14, 255)), .35)
    rows = [
        ('states', [state(), state(lit=(1, 1, 1)), pick('fast', 'cheap'), pick('good', 'fast'), pick('good', 'cheap', **drift(2.0)),
                    state(lit=(1, 1, 1), edge=(1, 1, 1), yaw=18, pitch=10), state(lit=(1, 0, 0), pop=(1.3, 1, 1), x=(0, 0, .5))]),
        ('pick', [pick('fast', 'cheap', draw=d, x=clamp(d * 1.5 - .3)) for d in (0, .2, .45, .7, 1.0)] + [mix(pick('fast', 'cheap'), state(lit=(1.6, 1.6, 0), edge=(1, 0, 0), x=(0, 0, 1)), .5), pick('fast', 'cheap', flow=.3)]),
        ('assemble', [state(assemble=a, lit=(1, 1, 1), edge=(1, 1, 1)) for a in (.06, .2, .36, .5, .62, .76, .9)]),
        ('crack', [state(crack=c, lit=(1, 1, 0), edge=(1, 0, 0), x=(0, 0, 1)) for c in (.04, .15, .3, .45, .6, .8, 1.0)]),
        ('shatter', [state(crack=1, shatter=s, lit=(1, 1, 0), edge=(1, 0, 0), x=(0, 0, 1)) for s in (.02, .06, .12, .22, .35, .5, .7)]),
        ('complete', [state(complete=c, lit=(1, 1, 0)) for c in (.02, .06, .12, .2, .35, .55, 1.0)]),
        ('logo', [state(complete=1, logo=l) for l in (.1, .25, .38, .46, .55, .7, 1.0)]),
    ]
    tile = 300; times = {}
    for name, sts in rows:
        strip = Image.new('RGB', (tile * len(sts), tile))
        for k, s_ in enumerate(sts):
            t0 = time.perf_counter(); im = render(s_, S); dt = time.perf_counter() - t0
            times.setdefault(name, []).append(dt)
            if bench_only: continue
            fr = bg.copy(); fr.alpha_composite(im)
            strip.paste(fr.convert('RGB').resize((tile, tile), Image.LANCZOS), (k * tile, 0))
            if name in ('states', 'shatter', 'complete', 'logo', 'crack') and k in (2, 3, 4, 5):
                fr.convert('RGB').save(os.path.join(out_dir, f'full_{name}_{k}.jpg'), quality=90)
        if not bench_only: strip.save(os.path.join(out_dir, f'strip_{name}.jpg'), quality=88)
    for k, v in times.items(): print(f'{k:10s} ' + ' '.join(f'{x * 1000:5.0f}' for x in v) + f'   (ms, mean {np.mean(v) * 1000:.0f})')


def _demo_frame():
    """the documented placements over a real frame of the take (out/tri/place_*.jpg)."""
    out_dir = os.path.join(E.HERE, 'out', 'tri'); os.makedirs(out_dir, exist_ok=True)
    t = 13.5; F = E.Film(t)
    def world(**av):
        ctx = E.Ctx(t); ctx.avatar.update(av); ctx.compose = lambda cam=None, avatar=None: F.compose_world(ctx, cam, avatar)
        return F.compose_world(ctx), ctx
    def safe(im):
        d = ImageDraw.Draw(im); d.rectangle((70, 280, 960, 1250), outline=(255, 220, 0), width=2)
        d.rectangle((0, 1250, 1080, 1920), outline=(255, 80, 80), width=2); return im
    fr, ctx = world(s=.80, y=90)
    im = paste(fr, pick('fast', 'cheap', **drift(1.0)), 640, 540, 585, frost=8)
    safe(E.post(im.convert('RGB'), ctx.post, t)).save(os.path.join(out_dir, 'place_overhead.jpg'), quality=88)
    fr, ctx = world(x=260)
    im = paste(fr, state(lit=(1, 0, 1), edge=(0, 0, 1), x=(0, 1, 0), **drift(2.0)), 560, 330, 760, frost=8)
    safe(E.post(im.convert('RGB'), ctx.post, t)).save(os.path.join(out_dir, 'place_beside.jpg'), quality=88)
    fr, ctx = world()
    b = Image.blend(fr, Image.new('RGBA', fr.size, (6, 6, 12, 255)), .72).filter(ImageFilter.GaussianBlur(8))
    b = paste(b, state(complete=.1, ring=2.2), 900, 540, 760, frost=10)
    safe(E.post(b.convert('RGB'), ctx.post, t)).save(os.path.join(out_dir, 'place_full.jpg'), quality=88)
    b = Image.blend(fr, Image.new('RGBA', fr.size, (6, 6, 12, 255)), .72).filter(ImageFilter.GaussianBlur(8))
    b = paste(b, state(complete=1, logo=1), 860, 540, 760, frost=0)
    safe(E.post(b.convert('RGB'), ctx.post, t)).save(os.path.join(out_dir, 'place_logo.jpg'), quality=88)
    print('ok')


def story(t):
    """reference animation (8 s) showing how to drive the states from time — `python3 sections/_tri.py clip a b`:
    0-1.2 assemble (dim) | 1.2 FAST lights (overdrive) | 1.55 CHEAP lights + beam FAST->CHEAP | 1.9 ✗ stamps GOOD |
    2.4-3.0 crack | 3.0-4.2 shatter | 4.2-5.4 assemble again | 5.4 complete (ring 2.4) | 6.6-8.0 logo."""
    d = drift(t)
    if t < 1.2: return state(assemble=t / 1.2, **d)
    if t < 2.4:
        u = t - 1.2
        lf = 1 + .6 * math.exp(-u / .12)
        lc = (1 + .6 * math.exp(-(u - .35) / .12)) if u >= .35 else 0
        dr = eout((u - .35) / .25) if u >= .35 else 0
        return state(lit=(lf, lc, 0), edge=(1 if u >= .35 else 0, 0, 0), draw=(dr, 1, 1), x=(0, 0, clamp((u - .7) / .18)), flow=t, **d)
    base = dict(lit=(1, 1, 0), edge=(1, 0, 0), x=(0, 0, 1))
    if t < 3.0: return state(crack=(t - 2.4) / .6, **base, **d)
    if t < 4.2: return state(crack=1, shatter=(t - 3.0) / 1.2, **base, **d)
    if t < 5.4: return state(assemble=(t - 4.2) / 1.2, **d)
    if t < 6.6: return state(complete=min(1, (t - 5.4) / 1.0), ring=2.4, flow=t, **d)
    return state(complete=1, logo=min(1, (t - 6.6) / 1.4), **d)


def _clip(t0, t1):
    import subprocess
    out_dir = os.path.join(E.HERE, 'out', 'tri'); os.makedirs(out_dir, exist_ok=True)
    bg = E.studio().convert('RGBA').filter(ImageFilter.GaussianBlur(5))
    bg = Image.blend(bg, Image.new('RGBA', bg.size, (6, 6, 12, 255)), .4)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{E.W}x{E.H}', '-r', str(E.FPS), '-i', '-',
                            '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', os.path.join(out_dir, 'clip.mp4')], stdin=subprocess.PIPE)
    for j in range(int(round(t0 * E.FPS)), int(round(t1 * E.FPS))):
        fr = bg.copy(); fr.alpha_composite(render(story(j / E.FPS), 900, canvas=(E.W, E.H), at=(540, 760)))
        enc.stdin.write(fr.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); print(os.path.join(out_dir, 'clip.mp4'))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    if cmd == 'demo': _demo()
    elif cmd == 'bench': _demo(bench_only=True)
    elif cmd == 'frame': _demo_frame()
    elif cmd == 'clip': _clip(float(sys.argv[2]), float(sys.argv[3]))
