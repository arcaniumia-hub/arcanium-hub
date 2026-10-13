"""_glasskit — deterministic glass fracture + 3-D shard toolkit (author: B, used by s03/s04; other sections may import).

Everything is seeded and cached on first use; every per-frame call is a pure function of the time you pass in.

    import sections._glasskit as GK

    F = GK.Fracture(center=(566, 1052), size=(1080, 1920), seed=7, radials=16,
                    hits=[(7.24, 40, 120, .45, .05),      # knock 1: (t, rmin, rmax, frac of radials, grow dur)
                          (7.50, 150, 380, .8, .08)],     # knock 2: bigger star (keeps the first one)
                    race=(7.90, 14000),                  # (t, px/s): every radial races to the edge of the glass
                    web=(8.09, .14))                     # (t, dur): concentric spiderweb rings complete inner -> outer
    out = F.composite(img, t, refr=1.0, leak=0.0, glint=1.0, sweep=None, powder=1.0, sparks=1.0, leak_falloff=(.4, 650))
        # img: PIL RGB/RGBA (same size as F) -> PIL RGB with the cracks at time t: dark 2-3 px fissures, 1 px specular
        # glint on the lit side (angle-dependent + a moving light band `sweep`), refraction (each wedge / cell of the
        # glass shifts the image a few px, scaled by `refr`), the crushed white impact point, sparkle stars on the
        # cracks, and `leak` (0..1): light from behind bleeding through the cracks (fissures turn into light + glow).
        # ring_p=(a, b, lo, hi): probability a - b*j (clamped) that a segment of web ring j forms (default keeps far rings)
    F.reach(t)     -> np.array of each radial crack's length (px) at t
    F.cells        -> list of polygons [(x, y), ...] (spiderweb cells; outer cells split by diagonal break lines)

    S = GK.Shatter(F, seed=3, focal=1600, vp=(540, 880), group=None, wave=20000)
        # shards = F.cells clipped to the glass rect; group(i, ring, wedge) -> key merges cells into one piece;
        # wave = px per sim-second of the release shock wave from the impact
    S.render(dst_rgba, glass_rgba, tau, dz=0, focus_z=focal, dof=10, shutter_dtau=0, dz_prev=None, img_alpha=1.0,
             near=140, cull_scale=4.2, alpha=1, alpha_fn=None) -> RGBA
        # glass_rgba = the image printed on the glass (what the shards carry, mapped 1:1 at tau=0). Each shard is a
        # rigid planar polygon: released by the shock wave (centre first), flies outward + toward the lens with 3-D
        # tumble; projected with a pinhole camera (focal px, vanishing point vp; the glass plane sits at Z = focal so
        # tau=0 maps 1:1); the camera itself moves forward by dz (Z units). True perspective via a homography per
        # shard, Fresnel density, bright lit bevel edges, moving specular sheen + star glints, thin-lens defocus around
        # focus_z (camera-relative), motion blur from the shard + camera motion over the shutter (big/near pieces are
        # rendered at 1/2 or 1/4 res). img_alpha (float or fn(shard, u)) = how much of the printed image a piece
        # still carries; the rest of it is clear glass.
    S.render_refract(dst, glass, tau, ..., refract=22, glyph_alpha=0, veil=1, env_col, absorb=.07, edge=1) -> RGBA
        # photographic variant: each shard REFRACTS what is behind it (dst displaced by the piece's tilt, via a
        # half-res offset map; defocused pieces distort softly), clear glass shows only a faint Fresnel reflection
        # (env_col) + moving sheen + a bevel that is bright on the lit side and dark on the other. img_alpha = how
        # much of the printed image (glass RGB) a piece still carries; if `glass` is RGBA its alpha marks pixels that
        # stay printed at `glyph_alpha` (e.g. white UI glyphs on the cover glass).
        #   reflect=k + env_img (default GK.env_map()): the room mirrored by each piece (picked by its reflection
        #   vector, so it slides as the piece tumbles); bevel=px width; backlight=k: light from behind the glass
        #   glowing through the bevels (e.g. right after a break). Big pieces are shaded at half texture res.
    GK.env_map(size)  -> RGB float32 dark room (softboxes, monitor strips, specks) used for the reflections
    S.visible(tau, dz, near) -> bool                   # any shard still on screen (skip building the glass image)
    S.shards       -> list of dicts (polys, bbox, c, dist, motion params)
    class Floaters(Shatter) pattern: subclass, give your own `shards` + override pose(s, tau) for free-floating pieces.

    D = GK.Dust(F, n=200, seed=5, focal=1600, vp=(540, 880))
    D.render((W, H), tau, dz, dtau, dz_prev, alpha) -> RGBA   # glittering glass dust blown off the cracks (3-D, streaked)

    GK.homography(src, dst)  -> PIL PERSPECTIVE coefficients (maps output dst quad -> input src quad)
    GK.project(w, h, cx, cy, s, rx, ry, rz, f) -> 4 projected corners of a w x h card rotated in 3-D (degrees)
    GK.star(size, rays=4)    -> RGBA anamorphic star glint sprite (cached)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

INF = 1e9
_CACHE = {}


def _c(key, fn):
    if key not in _CACHE: _CACHE[key] = fn()
    return _CACHE[key]


def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3


# ------------------------------------------------------------------------------------------------ small helpers
def homography(src, dst):
    """coeffs for PIL PERSPECTIVE mapping output (dst) -> input (src)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def rot3(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]); Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def axis_angle(axis, ang):
    x, y, z = axis; c, s = math.cos(ang), math.sin(ang); C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def project(w, h, cx, cy, s, rx, ry, rz, f=2600.):
    """screen corners of a w x h card (scaled s) centred at (cx, cy), rotated rx/ry/rz degrees, pinhole focal f."""
    R = rot3(*(math.radians(v) for v in (rx, ry, rz))); pts = []
    for x, y in [(0, 0), (w, 0), (w, h), (0, h)]:
        X, Y, Z = R @ np.array([(x - w / 2) * s, (y - h / 2) * s, 0.])
        k = f / (f + Z); pts.append((cx + X * k, cy + Y * k))
    return pts


def star(size=64, rays=4, soft=1.0):
    """anamorphic star glint (white, RGBA): hot core + thin tapering rays (rays = 4 or 8)."""
    def mk():
        S = size; yy, xx = np.mgrid[-S:S + 1, -S:S + 1].astype(np.float32) / S
        r = np.hypot(xx, yy) + 1e-6
        core = np.exp(-(r / (.07 * soft)) ** 2) + .35 * np.exp(-(r / (.22 * soft)) ** 2)
        ray = np.zeros_like(r); lines = max(1, rays // 2)
        for k in range(lines):
            a = math.pi * k / lines
            d = np.abs(xx * math.sin(a) - yy * math.cos(a)); along = np.abs(xx * math.cos(a) + yy * math.sin(a))
            L = 1.0 if (k % 2 == 0 or lines <= 2) else .55
            ray += np.exp(-(d / (.012 + .02 * along)) ** 2) * np.clip(1 - along / L, 0, 1) ** 2
        a = np.clip(core + ray * .9, 0, 1)
        im = Image.new('RGBA', (2 * S + 1, 2 * S + 1), (255, 255, 255, 0))
        im.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return im
    return _c(('star', size, rays, soft), mk)


def clip_poly(poly, x0, y0, x1, y1):
    """Sutherland-Hodgman clip of a polygon to an axis-aligned rectangle."""
    def clip(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]; ia, ib = inside(a), inside(b)
            if ib:
                if not ia: out.append(inter(a, b))
                out.append(b)
            elif ia: out.append(inter(a, b))
        return out
    def ix(xc): return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / ((b[0] - a[0]) or 1e-6))
    def iy(yc): return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / ((b[1] - a[1]) or 1e-6), yc)
    pts = list(poly)
    for inside, inter in ((lambda p: p[0] >= x0, ix(x0)), (lambda p: p[0] <= x1, ix(x1)),
                          (lambda p: p[1] >= y0, iy(y0)), (lambda p: p[1] <= y1, iy(y1))):
        if not pts: break
        pts = clip(pts, inside, inter)
    return pts


def poly_area(p):
    a = 0.0
    for i in range(len(p)):
        x0, y0 = p[i - 1]; x1, y1 = p[i]; a += x0 * y1 - x1 * y0
    return abs(a) / 2


# ------------------------------------------------------------------------------------------------ fracture
LIGHT2 = (-.55, -.83)            # key light direction on the glass (screen space): from the top-left


class Fracture:
    def __init__(self, center, size=(1080, 1920), seed=7, radials=16, rings=None, hits=(), race=None, web=None,
                 split=.55, early_rings=(1, 3), ring_p=(1.02, .085, .22, .95)):
        self.C = (float(center[0]), float(center[1])); self.size = size; self.seed = seed
        self.ring_p = ring_p          # web ring j appears with p = clamp(a - b*j, lo, hi): steeper b = rings only near the impact
        self.W, self.H = size
        self.hits, self.race, self.web = list(hits), race, web
        rng = np.random.default_rng(seed)
        cx, cy = self.C; W, H = size
        self.rmax = max(math.hypot(x - cx, y - cy) for x in (0, W) for y in (0, H)) * 1.08 + 40
        n = self.n = radials
        base = (np.arange(n) + rng.uniform(-.28, .28, n)) * 2 * math.pi / n + rng.uniform(0, 2 * math.pi)
        self.base = base
        STEP = self.STEP = 5.0
        rs = self.rs = np.arange(0, self.rmax + STEP, STEP)
        self.rad = []
        for k in range(n):
            drift = np.zeros_like(rs)
            for amp, lam in ((.030, 420.), (.014, 160.), (.006, 48.)):
                drift += amp * np.sin(rs / lam + rng.uniform(0, 6.3))
            # kinks: piecewise random heading changes every 18-40 px (real fissures are straight runs + small kinks)
            kink = np.zeros_like(rs); pos = 0.0; cur = 0.0
            for i, r in enumerate(rs):
                if r >= pos: cur += rng.normal(0, .035); cur *= .6; pos = r + rng.uniform(18, 40)
                kink[i] = cur
            ang = base[k] + drift - drift[0] + np.cumsum(kink) * STEP / 400.0
            px = cx + rs * np.cos(ang); py = cy + rs * np.sin(ang)
            jag = rng.normal(0, .22, len(rs)); jag[0] = 0
            px += -np.sin(ang) * jag; py += np.cos(ang) * jag
            self.rad.append(np.stack([px, py], 1))
        # concentric rings (radius per radial, jittered); the last ring lies beyond the glass corners
        if rings is None:
            rings = [24, 62, 120, 200, 305, 440, 610, 830, 1100, 1450, 1900, 2500]
        rings = [r for r in rings if r < self.rmax - 10] + [self.rmax - 6]
        self.M = len(rings)
        self.rho = np.array([[r * (1 + rng.uniform(-.10, .10)) if j < len(rings) - 1 else r for _ in range(n)]
                             for j, r in enumerate(rings)])
        self.ring_base = rings
        self._rng = rng
        self._schedule(rng, early_rings)
        self._cells(rng, split)

    # ---------------------------------------------------------------- geometry
    def rpt(self, k, r):
        """point on radial k at radius r (interpolated)."""
        P = self.rad[k % self.n]; f = r / self.STEP; i = int(min(len(P) - 2, max(0, math.floor(f)))); u = f - i
        return (P[i, 0] * (1 - u) + P[i + 1, 0] * u, P[i, 1] * (1 - u) + P[i + 1, 1] * u)

    def rseg(self, k, r0, r1):
        """polyline of radial k from radius r0 to r1 (either direction)."""
        a, b = sorted((r0, r1)); i0, i1 = int(math.ceil(a / self.STEP + 1e-6)), int(math.floor(b / self.STEP - 1e-6))
        P = self.rad[k % self.n]
        pts = [self.rpt(k, a)] + [tuple(P[i]) for i in range(max(0, i0), min(len(P), i1 + 1))] + [self.rpt(k, b)]
        return pts if r0 <= r1 else pts[::-1]

    def ring_pts(self, j, k):
        """arc of ring j from radial k to k+1 (spiderweb rings follow circles around the impact, with jitter)."""
        key = ('ring', j, k)
        if not hasattr(self, '_rp'): self._rp = {}
        if key in self._rp: return self._rp[key]
        A = self.rpt(k, self.rho[j, k % self.n]); B = self.rpt(k + 1, self.rho[j, (k + 1) % self.n])
        cx, cy = self.C
        a0 = math.atan2(A[1] - cy, A[0] - cx); a1 = math.atan2(B[1] - cy, B[0] - cx)
        while a1 < a0: a1 += 2 * math.pi
        r0, r1 = math.hypot(A[0] - cx, A[1] - cy), math.hypot(B[0] - cx, B[1] - cy)
        L = (a1 - a0) * (r0 + r1) / 2; m = max(2, int(L / 16))
        rng = np.random.default_rng(self.seed * 1000 + j * 97 + k)
        sag = rng.uniform(-.04, .02)
        pts = [A]
        for i in range(1, m):
            s = i / m; a = a0 + (a1 - a0) * s; r = (r0 + (r1 - r0) * s) * (1 + sag * math.sin(math.pi * s)) + rng.normal(0, 1.1)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pts.append(B); self._rp[key] = pts; return pts

    def _cells(self, rng, split):
        cells, meta, diags = [], [], []
        for j in range(self.M):
            for k in range(self.n):
                k1 = (k + 1) % self.n
                ro0, ro1 = self.rho[j, k], self.rho[j, k1]
                if j == 0:
                    poly = self.rseg(k, 0, ro0) + self.ring_pts(0, k)[1:-1] + self.rseg(k1, ro1, 0)[:-1]
                    cells.append(poly); meta.append((j, k)); continue
                ri0, ri1 = self.rho[j - 1, k], self.rho[j - 1, k1]
                left = self.rseg(k, ri0, ro0); outer = self.ring_pts(j, k); right = self.rseg(k1, ro1, ri1)
                inner = self.ring_pts(j - 1, k)[::-1]
                if j >= 3 and rng.random() < split:
                    # split along a wandering diagonal break line (inner-left -> outer-right or outer-left -> inner-right)
                    if rng.random() < .5: A, B = left[0], outer[-1]
                    else: A, B = left[-1], inner[0]
                    m = max(2, int(math.hypot(B[0] - A[0], B[1] - A[1]) / 18)); d = [A]
                    for i in range(1, m):
                        s = i / m; d.append((A[0] + (B[0] - A[0]) * s + rng.normal(0, 2.2), A[1] + (B[1] - A[1]) * s + rng.normal(0, 2.2)))
                    d.append(B); diags.append((j, k, d))
                    ring = left[:-1] + outer[:-1] + right[:-1] + inner[:-1]
                    ia = 0 if A == left[0] else len(left) - 1
                    ib = (len(left) - 1 + len(outer) - 1) if B == outer[-1] else (len(left) - 1 + len(outer) - 1 + len(right) - 1)
                    i0, i1 = sorted((ia, ib)); dd = d if ia < ib else d[::-1]
                    p1 = ring[i0:i1 + 1] + dd[::-1][1:-1]
                    p2 = ring[i1:] + ring[:i0 + 1] + dd[1:-1]
                    cells += [p1, p2]; meta += [(j, k), (j, k)]
                else:
                    cells.append(left[:-1] + outer[:-1] + right[:-1] + inner[:-1]); meta.append((j, k))
        self.cells, self.cell_meta, self.diags = cells, meta, diags

    # ---------------------------------------------------------------- timing
    def _schedule(self, rng, early_rings):
        n = self.n; self.sel = []; self.targets = []
        prev = np.zeros(n)
        for h, (t, rmin, rmax, frac, dur) in enumerate(self.hits):
            s = rng.random(n) < frac
            if h > 0: s |= self.sel[-1]
            if s.sum() < 4: s[rng.choice(n, 4, replace=False)] = True
            tg = np.where(s, np.maximum(prev, rng.uniform(rmin, rmax, n)), prev)
            self.sel.append(s); self.targets.append(tg); prev = tg
        if self.race:
            self.race_delay = rng.uniform(0, .025, n); self.race_v = self.race[1] * rng.uniform(.8, 1.2, n)
        t_first = self.hits[0][0] if self.hits else (self.race[0] if self.race else 0)
        t_last = (self.race[0] + .03 + self.rmax / (self.race[1] * .8) + .02) if self.race else (self.hits[-1][0] + self.hits[-1][4] + .02)
        self.tgrid = np.arange(t_first - .002, t_last + .002, .001)
        self.reach_grid = np.stack([self._reach_raw(t) for t in self.tgrid], 1)       # (n, T)
        # ring births
        M = self.M; self.ring_birth = np.full((M, n), INF)
        wt, wd = (self.web if self.web else (None, None))
        for j in range(M):
            for k in range(n):
                k1 = (k + 1) % n
                need = max(self.birth_at(k, self.rho[j, k]), self.birth_at(k1, self.rho[j, k1]))
                if need >= INF: continue
                b = INF
                for h, (t, rmin, rmax, frac, dur) in enumerate(self.hits):
                    upto = early_rings[min(h, len(early_rings) - 1)]
                    if j < upto and self.sel[h][k] and self.sel[h][k1] \
                            and min(self.targets[h][k], self.targets[h][k1]) > self.rho[j].max() * 1.05 and rng.random() < .8:
                        b = min(b, max(need, t + dur * .6 + rng.uniform(0, .02)))
                if b >= INF and wt is not None:
                    a_, b_, lo_, hi_ = self.ring_p; p = clamp(a_ - b_ * j, lo_, hi_)
                    if rng.random() < p:
                        rv = self.ring_base[j] / 1300.0
                        b = max(need + .004, wt + wd * clamp(rv) ** .7 + rng.uniform(0, .025))
                self.ring_birth[j, k] = b

    def _reach_raw(self, t):
        r = np.zeros(self.n); prev = np.zeros(self.n)
        for h, (th, rmin, rmax, frac, dur) in enumerate(self.hits):
            tg = self.targets[h]; k = eout((t - th) / dur) if t > th else 0.0
            r = prev + (tg - prev) * k; prev = tg
        if self.race:
            tr = self.race[0]; base = prev
            u = np.clip(t - tr - self.race_delay, 0, None)
            r = np.maximum(r, np.where(u > 0, base + self.race_v * u, 0))
        return np.minimum(r, self.rmax)

    def reach(self, t):
        if t <= self.tgrid[0]: return np.zeros(self.n)
        if t >= self.tgrid[-1]: return self.reach_grid[:, -1].copy()
        i = int((t - self.tgrid[0]) / .001); return self.reach_grid[:, min(i, self.reach_grid.shape[1] - 1)].copy()

    def birth_at(self, k, r):
        """time at which radial k's crack reaches radius r (INF if never)."""
        g = self.reach_grid[k % self.n]
        if r <= 1e-6: return self.tgrid[0] if g[-1] > 0 else INF
        i = int(np.searchsorted(g, r - 1e-6))
        return INF if i >= len(g) else float(self.tgrid[i])

    # ---------------------------------------------------------------- raster art (cached)
    def _key(self): return ('frac', self.C, self.size, self.seed, self.n, tuple(self.ring_p), len(self.hits))

    def art(self):
        def mk():
            W, H = self.size; S = 2
            segs = []          # birth map: (birth, x0, y0, x1, y1, width_px)
            strokes = []       # art: (pts, width_px, glint_strength) — drawn as continuous polylines (no caps / ticks)
            la = math.atan2(LIGHT2[1], LIGHT2[0])
            rng = np.random.default_rng(self.seed + 5)
            def add(pts, births, wfun, gmul=1.0, chunk=7, grp=0):
                for i in range(len(pts) - 1):
                    if births[i] < INF: segs.append((births[i], pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], wfun(i), grp))
                ph, lam = rng.uniform(0, 6.3), rng.uniform(60, 160)
                i = 0
                while i < len(pts) - 1:
                    j = min(len(pts) - 1, i + chunk)
                    if births[i] < INF:
                        (x0, y0), (x1, y1) = pts[i], pts[j]
                        ang = math.atan2(y1 - y0, x1 - x0)
                        along = i * 5.0
                        g = (.18 + .82 * abs(math.sin(ang - la)) ** 1.6) * (.35 + .65 * (.5 + .5 * math.sin(along / lam + ph)) ** 1.5) * gmul
                        strokes.append((pts[i:j + 1], wfun(i), g, grp))
                    i = j
            cx, cy = self.C
            for k in range(self.n):
                P = self.rad[k]; rs = self.rs
                bt = [self.birth_at(k, r) for r in rs[1:]]
                add([tuple(p) for p in P], bt, lambda i, rs=rs: 2.9 - 1.3 * clamp(rs[i] / 800.0))
            for j in range(self.M):
                for k in range(self.n):
                    b0 = self.ring_birth[j, k]
                    if b0 >= INF: continue
                    pts = self.ring_pts(j, k); m = len(pts) - 1
                    add(pts, [b0 + .03 * i / m for i in range(m)], lambda i, j=j: 2.2 - .7 * clamp(j / 8), .85, chunk=4, grp=1)
            if self.web:
                wt, wd = self.web
                for (j, k, d) in self.diags:
                    if rng.random() < .4:
                        b0 = wt + wd + rng.uniform(.02, .12); m = len(d) - 1
                        add(d, [b0 + .03 * i / m for i in range(m)], lambda i: 1.5, .7, chunk=4, grp=1)
            # crushed zone: micro fissures around the impact
            if self.hits:
                t1 = self.hits[0][0]; t2 = self.hits[1][0] if len(self.hits) > 1 else t1
                for i in range(80):
                    a = rng.uniform(0, 2 * math.pi); r0 = abs(rng.normal(0, 15)); L = rng.uniform(4, 15)
                    a2 = a + rng.normal(0, .9)
                    x0, y0 = cx + r0 * math.cos(a), cy + r0 * math.sin(a); x1, y1 = x0 + L * math.cos(a2), y0 + L * math.sin(a2)
                    b = (t1 + rng.uniform(0, .03)) if r0 < 14 else (t2 + rng.uniform(0, .04))
                    segs.append((b, x0, y0, x1, y1, 1.1, 0)); strokes.append(([(x0, y0), (x1, y1)], 1.1, rng.uniform(.4, 1.0), 0))
            ox, oy = LIGHT2[0] * 1.1, LIGHT2[1] * 1.1
            parts = []
            for grp in (0, 1):          # radials and rings get separate birth maps (a ring never inherits a radial's birth)
                dark = Image.new('L', (W * S, H * S)); glint = Image.new('L', (W * S, H * S)); birth = Image.new('F', (W, H), INF)
                dd, dg, db = ImageDraw.Draw(dark), ImageDraw.Draw(glint), ImageDraw.Draw(birth)
                for pts, w, g, gr in strokes:
                    if gr != grp: continue
                    dd.line([(x * S, y * S) for x, y in pts], fill=255, width=max(1, int(round(w * S))), joint='curve')
                    dg.line([((x + ox) * S, (y + oy) * S) for x, y in pts], fill=int(255 * min(1, g)), width=S, joint='curve')
                for b, x0, y0, x1, y1, w, gr in sorted([q for q in segs if q[6] == grp], key=lambda q: -q[0]):
                    db.line([(x0, y0), (x1, y1)], fill=float(b), width=int(w + 3.5))
                dark = np.asarray(dark.resize((W, H), Image.BOX), np.float32) / 255
                glint = np.asarray(glint.resize((W, H), Image.BOX), np.float32) / 255
                birth = np.asarray(birth, np.float32)
                m = (dark > .02) | (glint > .02)
                idx = np.flatnonzero(m); bs = birth.ravel()[idx]; ok = bs < INF / 2
                idx, bs = idx[ok], bs[ok]
                parts.append((idx, bs, dark.ravel()[idx], glint.ravel()[idx]))
            idx = np.concatenate([p[0] for p in parts]); bs = np.concatenate([p[1] for p in parts])
            ys, xs = np.divmod(idx, W)
            A = dict(idx=idx, birth=bs, dark=np.concatenate([p[2] for p in parts]), glint=np.concatenate([p[3] for p in parts]),
                     u=(xs * .6 + ys * .8).astype(np.float32), q=((ys // 4) * ((W + 3) // 4) + xs // 4),
                     r=np.hypot(xs - self.C[0], ys - self.C[1]).astype(np.float32))
            # sparkle points: on radials, mid distance, appear with their crack
            sp = []
            for i in range(26):
                k = int(rng.integers(0, self.n)); r = rng.uniform(40, 900) ** 1.0
                x, y = self.rpt(k, r)
                if 0 <= x < W and 0 <= y < H: sp.append((x, y, self.birth_at(k, r), rng.uniform(0, 6.3), rng.uniform(5, 14), rng.uniform(.5, 1)))
            A['sparks'] = sp
            return A
        return _c(self._key() + ('art',), mk)

    def labels(self):
        """static per-pixel tables for refraction: cell id, (wedge, radius-bin) id."""
        def mk():
            W, H = self.size
            lab = Image.new('I', (W, H), -1); d = ImageDraw.Draw(lab)
            for i, p in enumerate(self.cells):
                d.polygon([(float(x), float(y)) for x, y in p], fill=i, outline=i)
            lab = np.asarray(lab, np.int32).copy(); lab[lab < 0] = 0
            wedge = np.array([m[1] for m in self.cell_meta], np.int32)[lab]
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            r = np.hypot(xx - self.C[0], yy - self.C[1])
            NB = int(self.rmax / 4) + 2
            wr = (wedge * NB + np.minimum(NB - 1, (r / 4).astype(np.int32))).astype(np.int32)
            rng = np.random.default_rng(self.seed + 11)
            nc = len(self.cells)
            return dict(lab=lab.ravel(), wr=wr.ravel(), NB=NB, rb=(np.arange(NB) * 4 + 2).astype(np.float32),
                        wo=rng.normal(0, 1, (self.n, 2)).astype(np.float32), wb=rng.normal(0, .035, self.n).astype(np.float32),
                        co=rng.normal(0, 1, (nc, 2)).astype(np.float32), cb=rng.normal(0, .03, nc).astype(np.float32),
                        cell_ring=np.array([m[0] for m in self.cell_meta]), cell_k=np.array([m[1] for m in self.cell_meta]),
                        base=np.arange(W * H, dtype=np.int32))
        return _c(self._key() + ('lab',), mk)

    def powder(self):
        """crushed-glass spot at the impact: frosted white core with grainy edge (RGBA)."""
        def mk():
            R = 46; yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
            r = np.hypot(xx, yy); rng = np.random.default_rng(self.seed + 3)
            n = rng.random(r.shape).astype(np.float32)
            a = np.clip(1 - r / (18 + 10 * n), 0, 1) ** 1.3 * (.55 + .45 * n) + np.exp(-(r / 6) ** 2) * .6
            a = np.clip(a, 0, 1)
            im = Image.new('RGBA', (2 * R + 1, 2 * R + 1), (236, 238, 255, 0)); im.putalpha(Image.fromarray((a * 230).astype(np.uint8)))
            return im.filter(ImageFilter.GaussianBlur(.6))
        return _c(self._key() + ('powder',), mk)

    # ---------------------------------------------------------------- per frame
    def refract(self, a, t, amt):
        """shift the image under each fragment (a: float32 HxWx3) -> new array. Inside a wedge (between two radial
        cracks) the shift grows smoothly behind the crack tips; once a cell's ring crack exists it moves on its own."""
        L = self.labels(); reach = self.reach(t)
        if reach.max() <= 0 or amt <= 0: return a
        H, W = a.shape[:2]
        Rw = np.minimum(reach, np.roll(reach, -1)).astype(np.float32)
        G = np.clip((Rw[:, None] - L['rb'][None]) / 160.0, 0, 1) * np.clip((L['rb'][None] - 6) / 40.0, 0, 1)   # (n, NB)
        s1 = 1.6 * amt; s2 = 1.8 * amt
        TX = np.rint(L['wo'][:, 0:1] * G * s1).astype(np.int32); TY = np.rint(L['wo'][:, 1:2] * G * s1).astype(np.int32)
        rb = self.ring_birth
        act = (rb[np.minimum(L['cell_ring'], self.M - 1), L['cell_k']] <= t).astype(np.float32)
        CX = np.rint(L['co'][:, 0] * act * s2).astype(np.int32); CY = np.rint(L['co'][:, 1] * act * s2).astype(np.int32)
        offT = (TY * W + TX).ravel(); offC = CY * W + CX
        idx = L['base'] + offT[L['wr']] + offC[L['lab']]
        np.clip(idx, 0, W * H - 1, out=idx)
        flat = a.reshape(-1, 3)
        out = flat[idx]
        bk = min(1.5, amt)
        BT = (L['wb'][:, None] * G * bk).ravel(); BC = L['cb'] * act * bk
        out *= (1 + BT[L['wr']] + BC[L['lab']])[:, None]
        return out.reshape(H, W, 3)

    def composite(self, img, t, refr=1.0, leak=0.0, glint=1.0, sweep=None, powder=1.0, leak_col=(205, 170, 255), sparks=1.0,
                  leak_falloff=(.4, 650.0)):
        A = self.art(); W, H = self.size
        if not self.hits and not self.race: return img.convert('RGB')
        t0 = self.hits[0][0] if self.hits else self.race[0]
        if t < t0: return img.convert('RGB')
        a = np.asarray(img.convert('RGB'), np.float32)
        if refr > 0: a = self.refract(a, t, refr)
        else: a = a.copy()
        flat = a.reshape(-1, 3)
        vis = np.clip((t - A['birth']) / .012, 0, 1)
        on = vis > 0
        idx = A['idx'][on]; v = vis[on]
        d = A['dark'][on] * v; g = A['glint'][on] * v
        lo, R = leak_falloff
        lk = leak * (lo + (1 - lo) * np.exp(-A['r'][on] / R)) if leak > 0 else 0.0     # most light where it is most broken
        px = flat[idx]
        lc = np.array(leak_col, np.float32)
        hot = np.array([255, 250, 255], np.float32)
        lum = px.mean(1)
        dk = np.clip((105 - lum) / 105, 0, 1)                    # on a dark display a fissure scatters light: reads pale
        lkc = lk[:, None] if isinstance(lk, np.ndarray) else lk
        px = px * (1 - d[:, None] * (.8 - .55 * lkc)) + d[:, None] * (dk[:, None] * 118 * (1 - lkc)) \
            + d[:, None] * (lc * .7 + hot * .3) * lkc * 1.15
        sw = 1.0
        if sweep is not None:
            sw = .45 + 1.1 * np.exp(-((A['u'][on] - sweep) / 240.0) ** 2)
        px = px + (g * sw * glint * (.75 + .6 * dk))[:, None] * np.array([235, 240, 255], np.float32)
        flat[idx] = px
        if leak > .01:   # glow around the cracks (quarter res)
            qw, qh = (W + 3) // 4, (H + 3) // 4
            acc = np.bincount(A['q'][on], weights=d * (lk / max(leak, 1e-6)), minlength=qw * qh)[:qw * qh].reshape(qh, qw).astype(np.float32) / 16
            from scipy.ndimage import gaussian_filter
            gl = gaussian_filter(acc, 1.6) * 2.2 + gaussian_filter(acc, 7.0) * 3.0
            gl = 1 - np.exp(-gl * leak * 1.6)                                    # saturating: a halo, never a white-out
            gl = np.asarray(Image.fromarray(np.clip(gl * 255, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
            a = a + gl[..., None] * lc[None, None] * .85
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        # crushed impact point
        if powder > 0 and self.hits:
            k = 0.0
            for i, (th, *_r) in enumerate(self.hits): k = max(k, (.55 + .25 * i) * clamp((t - th) / .03))
            if self.race: k = max(k, clamp((t - self.race[0]) / .05))
            k *= powder
            if k > .01:
                p = self.powder(); s = .7 + .3 * k
                if abs(s - 1) > .01: p = p.resize((int(p.width * s), int(p.height * s)), Image.BILINEAR)
                o = out.convert('RGBA'); E._paste(o, dict(img=E.fade(p, min(1, k)), xy=(int(self.C[0] - p.width / 2), int(self.C[1] - p.height / 2)), glass=0))
                out = o.convert('RGB')
        # sparkles on the cracks (twinkle, flare up with `glint`)
        if sparks > 0:
            o = None
            for (x, y, b, ph, sz, st) in A['sparks']:
                if t < b + .02: continue
                tw = (.5 + .5 * math.sin(t * 9 + ph)) ** 6 * st * glint * sparks
                if tw < .08: continue
                s_ = star(48)
                sc = sz * (.6 + .8 * tw) / 48
                im = s_.resize((max(3, int(s_.width * sc)), max(3, int(s_.height * sc))), Image.BILINEAR)
                if o is None: o = out.convert('RGBA')
                E._paste(o, dict(img=E.fade(im, min(1, tw)), xy=(int(x - im.width / 2), int(y - im.height / 2)), glass=0))
            if o is not None: out = o.convert('RGB')
        return out


# ------------------------------------------------------------------------------------------------ 3-D shatter
LIGHT3 = np.array([-.45, -.75, -.48]); LIGHT3 = LIGHT3 / np.linalg.norm(LIGHT3)     # toward the light (camera side)


class Shatter:
    def __init__(self, F, seed=3, focal=1600., vp=(540., 880.), rect=None, min_area=260, speed=1.0, group=None, wave=20000.):
        """group(i, j, k) -> key (cell index, ring, wedge): cells sharing a key fly as ONE shard (e.g. merge tiny
        inner cells). wave: px per sim-second of the release shock wave from the impact."""
        self.F, self.f, self.vp = F, float(focal), (float(vp[0]), float(vp[1]))
        W, H = F.size; self.rect = rect or (0, 0, W, H)
        rng = np.random.default_rng(seed); out = []
        x0r, y0r, x1r, y1r = self.rect
        groups = {}
        for i, poly in enumerate(F.cells):
            j, k = F.cell_meta[i]
            key = group(i, j, k) if group else i
            q = clip_poly(poly, x0r, y0r, x1r, y1r)
            if len(q) < 3 or poly_area(q) < 2: continue
            groups.setdefault(key, []).append(q)
        for gi, (key, polys) in enumerate(sorted(groups.items(), key=lambda kv: str(kv[0]))):
            area = sum(poly_area(q) for q in polys)
            xs = [p[0] for q in polys for p in q]; ys = [p[1] for q in polys for p in q]
            bx0, by0, bx1, by1 = int(math.floor(min(xs))) - 2, int(math.floor(min(ys))) - 2, int(math.ceil(max(xs))) + 3, int(math.ceil(max(ys))) + 3
            cx = sum(poly_area(q) * np.mean([p[0] for p in q]) for q in polys) / max(area, 1e-6)
            cy = sum(poly_area(q) * np.mean([p[1] for p in q]) for q in polys) / max(area, 1e-6)
            dx, dy = cx - F.C[0], cy - F.C[1]; dist = math.hypot(dx, dy) + 1
            ax = rng.normal(0, 1, 3); ax[2] *= .5; ax /= np.linalg.norm(ax)
            near = math.exp(-dist / 420)
            out.append(dict(i=gi, polys=polys, poly=[p for q in polys for p in q], bbox=(bx0, by0, bx1, by1), c=(cx, cy),
                            dist=dist, dir=(dx / dist, dy / dist), area=area,
                            vr=rng.uniform(420, 950) * (1 + .8 * near) * speed,
                            vz=-rng.uniform(250, 800) * (.5 + .9 * near) * speed,
                            axis=ax, w=rng.uniform(2.5, 7.5) * rng.choice([-1, 1]) * speed,
                            delay=dist / wave + rng.uniform(0, .008), ph=rng.uniform(0, 6.3),
                            grav=rng.uniform(150, 420), side=rng.uniform(-1, 1)))
        self.shards = out

    def masks(self, s, r=1, bevel=2.2):
        """AA polygon mask + bevel edge mask in the shard's bbox (cached per shard; r = texture downscale 1 or 2)."""
        def mk():
            bx0, by0, bx1, by1 = s['bbox']; w, h = bx1 - bx0, by1 - by0; S = 3
            w, h = max(2, -(-w // r)), max(2, -(-h // r))
            m = Image.new('L', (w * S, h * S)); e = Image.new('L', (w * S, h * S))
            for poly in s.get('polys', [s['poly']]):
                pts = [((x - bx0) * S / r, (y - by0) * S / r) for x, y in poly]
                ImageDraw.Draw(m).polygon(pts, fill=255)
            # bevel edge = outline of the union (mask minus its erosion)
            from scipy.ndimage import minimum_filter
            ma = np.asarray(m, np.uint8)
            e = Image.fromarray(np.clip(ma.astype(np.int16) - minimum_filter(ma, size=max(3, int(bevel * S / r)) | 1).astype(np.int16), 0, 255).astype(np.uint8))
            m = m.resize((w, h), Image.LANCZOS); e = e.resize((w, h), Image.BOX)
            mm = np.asarray(m, np.float32) / 255; ee = np.asarray(e, np.float32) / 255 * mm
            # lit / shadow sides of the bevel (screen-space light from the top-left)
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            gx = np.zeros_like(mm); gy = np.zeros_like(mm)
            gx[:, 1:-1] = mm[:, 2:] - mm[:, :-2]; gy[1:-1] = mm[2:] - mm[:-2]
            lit = np.clip(-(gx * LIGHT2[0] + gy * LIGHT2[1]) * r, 0, 1)
            band = (xx / max(1, w) * .6 + yy / max(1, h) * .8) / 1.4
            return mm, ee, lit, band
        return _c(('shm', id(self), s['i']) + ((r, bevel) if (r, bevel) != (1, 2.2) else ()), mk)

    def pose(self, s, tau):
        """(centre 3D, rotation) of shard s at sim time tau (tau=0 -> in the glass plane)."""
        u = max(0.0, tau - s['delay'])
        f = self.f; cx, cy = s['c']
        X = cx - self.vp[0] + s['dir'][0] * s['vr'] * u
        Y = cy - self.vp[1] + s['dir'][1] * s['vr'] * u + .5 * s['grav'] * u * u
        Z = f + s['vz'] * u
        R = axis_angle(s['axis'], s['w'] * u)
        return np.array([X, Y, Z]), R, u

    def corners(self, s, tau, dz):
        P, R, u = self.pose(s, tau)
        bx0, by0, bx1, by1 = s['bbox']; cx, cy = s['c']
        loc = np.array([[bx0 - cx, by0 - cy, 0], [bx1 - cx, by0 - cy, 0], [bx1 - cx, by1 - cy, 0], [bx0 - cx, by1 - cy, 0]], float)
        Q = P[None] + loc @ R.T
        Q[:, 2] -= dz
        return Q, P - np.array([0, 0, dz]), R, u

    def visible(self, tau, dz=0.0, near=140.0, cull_scale=4.2):
        """True while at least one shard is still in front of the camera and on screen (cheap test)."""
        W, H = self.F.size if self.F is not None else (1080, 1920)
        for s in self.shards:
            Q, P, R, u = self.corners(s, tau, dz)
            if Q[:, 2].min() < near or self.f / P[2] > cull_scale + 1.6: continue
            pp = self.proj(Q)
            if pp[:, 0].max() > 0 and pp[:, 0].min() < W and pp[:, 1].max() > 0 and pp[:, 1].min() < H: return True
        return False

    def proj(self, Q):
        z = np.maximum(Q[:, 2], 1e-3)
        return np.stack([self.vp[0] + self.f * Q[:, 0] / z, self.vp[1] + self.f * Q[:, 1] / z], 1)

    def render(self, dst, glass, tau, dz=0.0, focus_z=None, dof=10.0, shutter_dtau=0.0, near=140.0, alpha=1.0,
               spec_gain=1.0, cull_scale=4.2, keep=None, dz_prev=None, alpha_fn=None, img_alpha=1.0):
        """draw the flying shards over dst (RGBA, full frame) -> RGBA. glass: RGBA/RGB image printed on the glass."""
        W, H = dst.size; f = self.f
        if focus_z is None: focus_z = f
        out = dst.copy(); half = None; quarter = None
        g_arr = None
        items = []
        for s in self.shards:
            if keep is not None and not keep(s): continue
            Q, P, R, u = self.corners(s, tau, dz)
            if Q[:, 2].min() < near: continue
            items.append((P[2], s, Q, P, R, u))
        items.sort(key=lambda it: -it[0])                     # far -> near
        glass_rgb = glass.convert('RGB')
        for Zc, s, Q, P, R, u in items:
            pts = self.proj(Q)
            scale = f / Zc
            # polygon bbox on screen (all poly vertices, through the same transform)
            bx0, by0, bx1, by1 = s['bbox']; cx, cy = s['c']
            loc = np.array([[x - cx, y - cy, 0] for x, y in s['poly']], float)
            PP = P[None] + loc @ R.T
            if PP[:, 2].min() < near: continue
            pp = self.proj(PP)
            x0, y0 = pp[:, 0].min(), pp[:, 1].min(); x1, y1 = pp[:, 0].max(), pp[:, 1].max()
            if x1 < 0 or y1 < 0 or x0 > W or y0 > H: continue
            fade = 1.0
            if scale > cull_scale: fade = clamp(1 - (scale - cull_scale) / 1.6)
            if fade <= .02: continue
            # lighting
            n = R @ np.array([0, 0, -1.0])
            V = -P / (np.linalg.norm(P) + 1e-6)
            if n @ V < 0: n = -n
            fres = abs(float(n @ V))
            Hh = LIGHT3 + V; Hh /= np.linalg.norm(Hh)
            spec = max(0.0, float(n @ Hh)) ** 36 * spec_gain
            diff = .82 + .25 * max(0.0, float(n @ LIGHT3))
            # resolution for this shard
            area = (x1 - x0) * (y1 - y0)
            blur = float(dof * abs(f / Zc - f / focus_z))
            q = 1 if (area < 300000 and blur < 3.0) else (2 if area < 800000 else 4)
            # sprite in texture space
            mm, ee, lit, band = self.masks(s)
            tex = np.asarray(glass_rgb.crop((bx0, by0, bx1, by1)), np.float32)
            sh = .55 + .45 * fres
            ia = img_alpha(s, u) if callable(img_alpha) else img_alpha          # opacity of the printed image
            rgb = tex * (diff * sh)
            rgb = rgb * ia + np.array([205, 210, 240], np.float32) * (1 - ia)     # clear glass: a faint cool reflection
            sb = np.exp(-((band - (.5 + .45 * math.sin(s['ph'] + u * s['w'] * .8))) / .16) ** 2)
            shine = sb * (.14 + .9 * spec)
            rgb = rgb + shine[..., None] * np.array([235, 238, 255], np.float32) * .6
            edge_l = ee * (.5 + .5 * lit) * (.9 + 1.8 * spec + .6 * (1 - fres))
            rgb = rgb * (1 - ee[..., None] * .35) + edge_l[..., None] * np.array([240, 245, 255], np.float32)
            body = ia * (.93 + .07 * fres) + (1 - ia) * (.05 + .13 * (1 - fres))      # glass gets denser at grazing angles
            a = np.clip(mm * body + ee * .9 * (1 - ia) + mm * shine * .45, 0, 1) * mm
            a = a * fade * alpha * (alpha_fn(s, u) if alpha_fn else 1.0) / (1 + blur / 12.0)     # defocused glass all but vanishes
            spr = np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)
            spr = Image.fromarray(spr, 'RGBA')
            # projection (output box clipped to screen), at 1/q resolution
            ox0, oy0 = max(0, int(math.floor(x0)) - 2), max(0, int(math.floor(y0)) - 2)
            ox1, oy1 = min(W, int(math.ceil(x1)) + 3), min(H, int(math.ceil(y1)) + 3)
            if ox1 - ox0 < 2 or oy1 - oy0 < 2: continue
            dstp = [((px - ox0) / q, (py - oy0) / q) for px, py in pts]
            srcp = [(0, 0), (bx1 - bx0, 0), (bx1 - bx0, by1 - by0), (0, by1 - by0)]
            try: co = homography(srcp, dstp)
            except np.linalg.LinAlgError: continue
            ow, oh = max(1, (ox1 - ox0 + q - 1) // q), max(1, (oy1 - oy0 + q - 1) // q)
            im = spr.transform((ow, oh), Image.PERSPECTIVE, co, Image.BILINEAR)
            # motion blur: smear along the projected motion of the centre over the shutter
            if shutter_dtau > 0 or dz_prev is not None:
                Q2, P2, R2, u2 = self.corners(s, max(0.0, tau - shutter_dtau), dz if dz_prev is None else dz_prev)
                if P2[2] > near:
                    c1 = self.proj(P[None])[0]; c0 = self.proj(P2[None])[0]
                    mv = (c1 - c0) / q
                    L = math.hypot(*mv)
                    if L > 2.5:
                        pd = int(L / 2) + 2; im = _pad(im, pd); ox0 -= pd * q; oy0 -= pd * q
                        im = smear(im, mv[0], mv[1], min(12, int(L / 2.5) + 2))
            if blur / q > .7:
                r_ = float(min(30, blur / q)); pd = int(r_ * 2.6) + 2
                im = _pad(im, pd); ox0 -= pd * q; oy0 -= pd * q
                im = im.filter(ImageFilter.GaussianBlur(r_))
            # specular star glint at the corner facing the light
            if spec > .35 and q <= 2 and scale < 3.0:
                st = star(56); k = min(1.0, (spec - .35) / .5)
                sz = int((26 + 50 * k) * min(1.6, scale) / q) | 1
                gimg = E.fade(st.resize((sz, sz), Image.BILINEAR), k)
                vi = int(np.argmin(pp[:, 0] * LIGHT2[0] * -1 + pp[:, 1] * LIGHT2[1] * -1))
                gx_, gy_ = (pp[vi, 0] - ox0) / q, (pp[vi, 1] - oy0) / q
                im.alpha_composite(gimg, (int(max(0, min(im.width - 1, gx_ - sz / 2))), int(max(0, min(im.height - 1, gy_ - sz / 2))))) if (gx_ - sz / 2 >= 0 and gy_ - sz / 2 >= 0 and gx_ + sz / 2 < im.width and gy_ + sz / 2 < im.height) else None
            if q == 1:
                E._paste(out, dict(img=im, xy=(ox0, oy0), glass=0))
            elif q == 2:
                if half is None: half = Image.new('RGBA', ((W + 1) // 2, (H + 1) // 2), (0, 0, 0, 0))
                E._paste(half, dict(img=im, xy=(ox0 // 2, oy0 // 2), glass=0))
            else:
                if quarter is None: quarter = Image.new('RGBA', ((W + 3) // 4, (H + 3) // 4), (0, 0, 0, 0))
                E._paste(quarter, dict(img=im, xy=(ox0 // 4, oy0 // 4), glass=0))
        if half is not None: out.alpha_composite(half.resize((W, H), Image.BILINEAR))
        if quarter is not None: out.alpha_composite(quarter.resize((W, H), Image.BILINEAR))
        return out

    # ---------------------------------------------------------------- refractive (photographic) shard render
    def _gather(self, tau, dz, near, cull_scale, keep, alpha, alpha_fn, dof, focus_z, shutter_dtau, dz_prev, W, H):
        """visible shards with their projection, lighting vectors and motion (far -> near)."""
        f = self.f; items = []
        for s in self.shards:
            if keep is not None and not keep(s): continue
            Q, P, R, u = self.corners(s, tau, dz)
            if Q[:, 2].min() < near: continue
            items.append((P[2], s, Q, P, R, u))
        items.sort(key=lambda it: -it[0])
        G = []
        for Zc, s, Q, P, R, u in items:
            scale = f / Zc
            if '_loc' not in s:
                cx, cy = s['c']; s['_loc'] = np.array([[x - cx, y - cy, 0] for x, y in s['poly']], float)
                s['_lens'] = [len(q) for q in s.get('polys', [s['poly']])]
            PP = P[None] + s['_loc'] @ R.T
            if PP[:, 2].min() < near: continue
            pp = self.proj(PP)
            x0, y0 = pp[:, 0].min(), pp[:, 1].min(); x1, y1 = pp[:, 0].max(), pp[:, 1].max()
            if x1 < 0 or y1 < 0 or x0 > W or y0 > H: continue
            fade = 1.0 if scale <= cull_scale else clamp(1 - (scale - cull_scale) / 1.6)
            a_s = fade * alpha * (alpha_fn(s, u) if alpha_fn else 1.0)
            if a_s <= .01: continue
            n = R @ np.array([0, 0, -1.0]); V = -P / (np.linalg.norm(P) + 1e-6)
            if n @ V < 0: n = -n
            mv = np.zeros(2); P2 = None
            if shutter_dtau > 0 or dz_prev is not None:
                Q2, P2, R2, u2 = self.corners(s, max(0.0, tau - shutter_dtau), dz if dz_prev is None else dz_prev)
                if P2[2] > near: mv = self.proj(P[None])[0] - self.proj(P2[None])[0]
            G.append(dict(s=s, Q=Q, P=P, R=R, u=u, Zc=Zc, scale=scale, pp=pp, box=(x0, y0, x1, y1), a=a_s, n=n, V=V,
                          blur=float(dof * abs(f / Zc - f / focus_z)), mv=mv))
        return G

    def _refract_bg(self, dst, G, refract, absorb, tint):
        """what is BEHIND each shard, seen through it: the background displaced by the shard's tilt (a thick slab shifts
        the view) and a touch darker, pasted through the shard's projected outline (union with its shutter-start
        position for fast pieces; defocused pieces get a soft outline). Far -> near, so near pieces win."""
        W, H = dst.size; out = dst.copy()
        dim = Image.blend(dst.convert('RGB'), Image.new('RGB', (W, H), tuple(int(c) for c in tint)), absorb).convert('RGBA')
        for g in G:
            n = g['n']; k = refract * min(1.9, .6 + .4 * g['scale'])
            ddx, ddy = int(round(float(n[0]) * k)), int(round(float(n[1]) * k))
            mv = g['mv']; L = math.hypot(*mv); soft = g['blur'] > 7
            x0, y0, x1, y1 = g['box']
            if L > 3: x0, y0, x1, y1 = min(x0, x0 - mv[0]), min(y0, y0 - mv[1]), max(x1, x1 - mv[0]), max(y1, y1 - mv[1])
            pad = int(min(30, g['blur'] * .8)) + 3 if soft else 2
            bx0, by0 = max(0, int(x0) - pad), max(0, int(y0) - pad); bx1, by1 = min(W, int(x1) + pad + 1), min(H, int(y1) + pad + 1)
            if bx1 - bx0 < 2 or by1 - by0 < 2: continue
            m = Image.new('L', (bx1 - bx0, by1 - by0)); D = ImageDraw.Draw(m); a8 = int(255 * min(1.0, g['a']))
            shifts = [(0.0, 0.0)] + ([(-mv[0] * .5, -mv[1] * .5), (-mv[0], -mv[1])] if L > 3 else [])
            i0 = 0
            for ln in g['s']['_lens']:
                poly = g['pp'][i0:i0 + ln]; i0 += ln
                for sx, sy in shifts: D.polygon([(x + sx - bx0, y + sy - by0) for x, y in poly], fill=a8)
            if soft: m = m.filter(ImageFilter.GaussianBlur(min(25, g['blur'] * .5)))
            ddx = min(max(ddx, -bx0), W - bx1); ddy = min(max(ddy, -by0), H - by1)        # stay inside the frame
            src = dim.crop((bx0 + ddx, by0 + ddy, bx1 + ddx, by1 + ddy))
            out.paste(src, (bx0, by0), m)
        return out

    def render_refract(self, dst, glass, tau, dz=0.0, focus_z=None, dof=10.0, shutter_dtau=0.0, near=140.0, alpha=1.0,
                       spec_gain=1.0, cull_scale=4.2, keep=None, dz_prev=None, alpha_fn=None, img_alpha=1.0,
                       refract=22.0, glyph_alpha=0.0, veil=1.0, env_col=(150, 132, 255), absorb=.07, tint=(120, 100, 220),
                       edge=1.0, sheen=1.0, max_smear=6, stars=True, reflect=0.0, env_img=None, bevel=2.2, backlight=0.0, back_col=(225, 210, 255)):
        """photographic glass: like render(), but each shard REFRACTS what is behind it (dst seen through the piece,
        displaced by its tilt) instead of a milky tint; the printed image (glass RGB) is `img_alpha` opaque, and where
        `glass` has an alpha channel those pixels (e.g. white UI glyphs) stay printed at `glyph_alpha`; clear glass only
        shows a faint Fresnel reflection of the room (env_col) at grazing angles, a moving specular sheen, and a bevel
        edge that is bright on the lit side and dark on the other. Defocused shards distort softly (bokeh glass)."""
        W, H = dst.size; f = self.f
        if focus_z is None: focus_z = f
        G = self._gather(tau, dz, near, cull_scale, keep, alpha, alpha_fn, dof, focus_z, shutter_dtau, dz_prev, W, H)
        if not G: return dst.copy()
        out = self._refract_bg(dst, G, refract, absorb, tint) if refract > 0 else dst.copy()
        has_a = glass.mode == 'RGBA'; glass_rgb = glass.convert('RGB'); glass_a = glass.getchannel('A') if has_a else None
        half = quarter = None
        env = np.array(env_col, np.float32); dark = np.array([10, 10, 18], np.float32); edc = np.array([244, 246, 255], np.float32)
        EM = env_img if env_img is not None else (env_map() if reflect > 0 else None)
        EMim = Image.fromarray(EM.astype(np.uint8)) if EM is not None else None
        for g in G:
            s, P, u, scale, blur, n, V = g['s'], g['P'], g['u'], g['scale'], g['blur'], g['n'], g['V']
            x0, y0, x1, y1 = g['box']; pts = self.proj(g['Q']); pp = g['pp']
            fres = abs(float(n @ V)); gr = 1 - fres
            Hh = LIGHT3 + V; Hh /= np.linalg.norm(Hh)
            spec = max(0.0, float(n @ Hh)) ** 36 * spec_gain
            diff = .82 + .25 * max(0.0, float(n @ LIGHT3))
            area = (x1 - x0) * (y1 - y0)
            q = 1 if (area < 300000 and blur < 3.0) else (2 if area < 800000 else 4)
            bx0, by0, bx1, by1 = s['bbox']
            r = 2 if (bx1 - bx0) * (by1 - by0) > 40000 else 1
            mm, ee, lit, band = self.masks(s, r, bevel)
            th, tw = mm.shape
            crop = (lambda im: im.crop((bx0, by0, bx1, by1))) if r == 1 else (lambda im: im.crop((bx0, by0, bx1, by1)).resize((tw, th), Image.BILINEAR))
            ia = img_alpha(s, u) if callable(img_alpha) else img_alpha
            ink = np.full(mm.shape, float(ia), np.float32)
            if has_a and glyph_alpha > 0:
                ink = np.maximum(ink, np.asarray(crop(glass_a), np.float32) / 255 * glyph_alpha)
            ink3 = ink[..., None]
            # 1 clear glass: faint reflection of the room, stronger at grazing angles
            dfo = 1 / (1 + blur / 8.0)                                          # defocused glass: reflections smear out
            va = min(.6, veil * (.03 + .34 * gr ** 1.5)) * dfo
            A = np.full(mm.shape, va, np.float32); Cp = (env * (.45 + .9 * band[..., None])) * va
            # 2 printed image (the display layer)
            if ia > .004 or (has_a and glyph_alpha > 0):
                tex = np.asarray(crop(glass_rgb), np.float32) * diff
                Cp = tex * ink3 + Cp * (1 - ink3); A = ink + A * (1 - ink)
            # 2b reflection of the room: the mirror direction picks a patch of the env map (moves as the piece tumbles)
            refl_peak = 0.0
            if EMim is not None:
                Rv = -V - 2 * float(n @ -V) * n                              # mirror of the view ray
                es = EMim.width; hw_, hh_ = bx1 - bx0, by1 - by0
                m = .55 * es / 1080 * max(1.0, 1.0 / max(.35, scale))       # patch size: planar mirror shows a wide view
                cxe, cye = es * (.5 + .55 * float(Rv[0])), es * (.5 + .55 * float(Rv[1]))
                pw, ph = max(2, hw_ * m), max(2, hh_ * m)
                small = EMim.transform((max(2, tw // 4), max(2, th // 4)), Image.EXTENT,
                                       (cxe - pw / 2, cye - ph / 2, cxe + pw / 2, cye + ph / 2), Image.BILINEAR)
                Fr = reflect * (.07 + .9 * gr ** 3) * dfo
                refl_peak = small.getextrema()[2][1] / 255 * Fr                 # blue channel: max of white + purple light
                patch = np.asarray(small.resize((tw, th), Image.BILINEAR), np.float32)
                Lr = patch * Fr                                              # additive light
                la_ = np.clip(Lr[..., 2] / 255, 0, 1)
                Cp = Lr + Cp * (1 - la_[..., None]); A = la_ + A * (1 - la_)
            # 3 moving specular sheen
            sb = np.exp(-((band - (.5 + .45 * math.sin(s['ph'] + u * s['w'] * .8))) / .13) ** 2)
            sa = np.clip(sb * (.09 + .9 * spec) * sheen, 0, 1) * .7
            Cp = 245 * sa[..., None] + Cp * (1 - sa[..., None]); A = sa + A * (1 - sa)
            # 4 bevel: dark on the shadow side, catching the light on the lit side
            da = ee * (1 - lit) * .45 * edge
            Cp = dark * da[..., None] + Cp * (1 - da[..., None]); A = da + A * (1 - da)
            la = np.clip(ee * (.3 + .7 * lit) * (.8 + 2.2 * spec + .7 * gr) * edge, 0, 1)
            Cp = edc * la[..., None] + Cp * (1 - la[..., None]); A = la + A * (1 - la)
            if backlight > .01:                                  # light from behind glowing through the bevel + a faint body
                bl = np.clip(ee * backlight + mm * backlight * .06, 0, 1)
                Cp = np.array(back_col, np.float32) * bl[..., None] + Cp * (1 - bl[..., None]); A = bl + A * (1 - bl)
            rgb = Cp / np.maximum(A, 1e-4)[..., None]
            a = A * mm * g['a'] / (1 + blur / 10.0)
            spr = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8), 'RGBA')
            ox0, oy0 = max(0, int(math.floor(x0)) - 2), max(0, int(math.floor(y0)) - 2)
            ox1, oy1 = min(W, int(math.ceil(x1)) + 3), min(H, int(math.ceil(y1)) + 3)
            if ox1 - ox0 < 2 or oy1 - oy0 < 2: continue
            dstp = [((px - ox0) / q, (py - oy0) / q) for px, py in pts]
            srcp = [(0, 0), ((bx1 - bx0) / r, 0), ((bx1 - bx0) / r, (by1 - by0) / r), (0, (by1 - by0) / r)]
            try: co = homography(srcp, dstp)
            except np.linalg.LinAlgError: continue
            ow, oh = max(1, (ox1 - ox0 + q - 1) // q), max(1, (oy1 - oy0 + q - 1) // q)
            im = spr.transform((ow, oh), Image.PERSPECTIVE, co, Image.BILINEAR)
            mv = g['mv'] / q; L = math.hypot(*mv)
            if L > 3:
                pd = int(L / 2) + 2; im = _pad(im, pd); ox0 -= pd * q; oy0 -= pd * q
                im = smear(im, mv[0], mv[1], min(max_smear, int(L / 5) + 2))
            if blur / q > .7:
                r_ = float(min(30, blur / q)); pd = int(r_ * 2.6) + 2
                im = _pad(im, pd); ox0 -= pd * q; oy0 -= pd * q
                im = im.filter(ImageFilter.GaussianBlur(r_))
            spk = max(spec, refl_peak * 1.15)
            if stars and spk > .35 and q <= 2 and scale < 3.0:
                st = star(56); k = min(1.0, (spk - .35) / .5)
                sz = int((26 + 50 * k) * min(1.6, scale) / q) | 1
                gimg = E.fade(st.resize((sz, sz), Image.BILINEAR), k * g['a'])
                vi = int(np.argmin(pp[:, 0] * -LIGHT2[0] + pp[:, 1] * -LIGHT2[1]))
                gx_, gy_ = (pp[vi, 0] - ox0) / q, (pp[vi, 1] - oy0) / q
                if gx_ - sz / 2 >= 0 and gy_ - sz / 2 >= 0 and gx_ + sz / 2 < im.width and gy_ + sz / 2 < im.height:
                    im.alpha_composite(gimg, (int(gx_ - sz / 2), int(gy_ - sz / 2)))
            if q == 1: E._paste(out, dict(img=im, xy=(ox0, oy0), glass=0))
            elif q == 2:
                if half is None: half = Image.new('RGBA', ((W + 1) // 2, (H + 1) // 2), (0, 0, 0, 0))
                E._paste(half, dict(img=im, xy=(ox0 // 2, oy0 // 2), glass=0))
            else:
                if quarter is None: quarter = Image.new('RGBA', ((W + 3) // 4, (H + 3) // 4), (0, 0, 0, 0))
                E._paste(quarter, dict(img=im, xy=(ox0 // 4, oy0 // 4), glass=0))
        if half is not None: out.alpha_composite(half.resize((W, H), Image.BILINEAR))
        if quarter is not None: out.alpha_composite(quarter.resize((W, H), Image.BILINEAR))
        return out


def env_map(size=768, key=(255, 250, 244), strips=((150, 120, 255), (90, 140, 255))):
    """a dark room as seen BY the glass (for reflections): a big soft key light top-left, a smaller fill, coloured light
    strips (the monitors) and a few hot specks. RGB float32 (size x size)."""
    def mk():
        S = size; yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
        a = np.zeros((S, S, 3), np.float32) + np.array([6, 6, 12], np.float32)
        def box(cx, cy, w, h, col, soft, gain=1.0):
            dx = np.clip((np.abs(xx - cx) - w / 2) / soft, 0, None); dy = np.clip((np.abs(yy - cy) - h / 2) / soft, 0, None)
            return np.exp(-(dx * dx + dy * dy))[..., None] * np.array(col, np.float32) * gain
        a += box(.28, .24, .30, .18, key, .035)                      # key softbox
        a += box(.80, .30, .10, .26, key, .03, .55)                   # fill strip
        a += box(.50, .66, .90, .025, strips[0], .02, .9)             # monitor light strips
        a += box(.42, .74, .60, .018, strips[1], .02, .7)
        a += box(.15, .88, .12, .05, key, .03, .4)
        a += box(.74, .60, .20, .12, key, .03, .7)                    # second softbox (lower right)
        a += box(.10, .50, .035, .40, strips[0], .02, .8)              # vertical practical strip (left)
        a += box(.90, .82, .05, .20, strips[1], .02, .6)
        rng = np.random.default_rng(9)
        for _ in range(26):
            cx, cy = rng.uniform(.05, .95, 2); r = rng.uniform(.004, .01)
            a += np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)))[..., None] * 255 * rng.uniform(.3, 1)
        return np.clip(a, 0, 255)
    return _c(('env', size, key, strips), mk)


def _grid(W, H):
    return _c(('grid', W, H), lambda: (np.arange(H, dtype=np.int32)[:, None].repeat(W, 1), np.arange(W, dtype=np.int32)[None, :].repeat(H, 0)))


def _pad(im, p):
    out = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); out.paste(im, (p, p)); return out


def smear(im, dx, dy, n):
    """directional motion blur of an RGBA sprite (premultiplied average of n shifted copies, centred)."""
    a = np.asarray(im, np.float32); al = a[..., 3:4] / 255; pm = np.concatenate([a[..., :3] * al, al], 2)
    h, w = pm.shape[:2]; acc = np.zeros_like(pm)
    for i in range(n):
        s = i / (n - 1) - .5; ox, oy = int(round(dx * s)), int(round(dy * s))
        ys0, ys1 = max(0, -oy), min(h, h - oy); xs0, xs1 = max(0, -ox), min(w, w - ox)
        if ys1 <= ys0 or xs1 <= xs0: continue
        acc[ys0 + oy:ys1 + oy, xs0 + ox:xs1 + ox] += pm[ys0:ys1, xs0:xs1]
    acc /= n; al = acc[..., 3:4]
    rgb = np.where(al > 1e-4, acc[..., :3] / np.maximum(al, 1e-4), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al * 255, 0, 255)]).astype(np.uint8), 'RGBA')


# ------------------------------------------------------------------------------------------------ glass dust
class Dust:
    """tiny glittering glass particles blown off the cracks at the break, flying toward the lens (3-D, streaked).

        D = GK.Dust(F, n=240, seed=5, focal=1600, vp=(540, 880))
        layer = D.render(size, tau, dz, dtau, dz_prev, alpha)   -> RGBA additive-looking sparkle layer
    """
    def __init__(self, F, n=240, seed=5, focal=1600., vp=(540., 880.)):
        self.f, self.vp = float(focal), (float(vp[0]), float(vp[1])); rng = np.random.default_rng(seed)
        W, H = F.size; P = []
        while len(P) < n:
            k = int(rng.integers(0, F.n)); r = rng.uniform(5, 1300) ** 1.0 * rng.uniform(.3, 1) ** .5
            x, y = F.rpt(k, r)
            if 0 <= x < W and 0 <= y < H:
                d = math.hypot(x - F.C[0], y - F.C[1]) + 1
                P.append((x, y, (x - F.C[0]) / d, (y - F.C[1]) / d, d))
        self.p = np.array(P, float)
        self.vr = rng.uniform(300, 1500, n) * (1 + 1.5 * np.exp(-self.p[:, 4] / 300))
        self.vz = -rng.uniform(400, 2200, n) * (.4 + np.exp(-self.p[:, 4] / 400))
        self.size = rng.uniform(.7, 2.0, n); self.ph = rng.uniform(0, 6.3, n); self.tw = rng.uniform(18, 45, n)
        self.delay = self.p[:, 4] / 22000.0

    def proj(self, tau, dz):
        u = np.maximum(0, tau - self.delay)
        X = self.p[:, 0] - self.vp[0] + self.p[:, 2] * self.vr * u
        Y = self.p[:, 1] - self.vp[1] + self.p[:, 3] * self.vr * u + 160 * u * u
        Z = self.f + self.vz * u - dz
        return X, Y, Z, u

    def render(self, size, tau, dz, dtau, dz_prev, alpha=1.0, near=90.0):
        W, H = size; S = 2
        im = Image.new('L', (W * S, H * S)); d = ImageDraw.Draw(im)
        X1, Y1, Z1, u = self.proj(tau, dz); X0, Y0, Z0, _ = self.proj(max(0.0, tau - dtau), dz_prev)
        for i in range(len(X1)):
            if Z1[i] < near or Z0[i] < near or u[i] <= 0: continue
            x1, y1 = self.vp[0] + self.f * X1[i] / Z1[i], self.vp[1] + self.f * Y1[i] / Z1[i]
            x0, y0 = self.vp[0] + self.f * X0[i] / Z0[i], self.vp[1] + self.f * Y0[i] / Z0[i]
            if not (-50 < x1 < W + 50 and -50 < y1 < H + 50): continue
            sc = self.f / Z1[i]
            tw = (.35 + .65 * (.5 + .5 * math.sin(self.ph[i] + tau * self.tw[i] * 6)) ** 4)
            a = min(1.0, tw * alpha * min(1.0, 1.6 / max(.6, sc ** .5)))
            w = max(1, int(round(self.size[i] * min(3.0, sc) * S)))
            L = math.hypot(x1 - x0, y1 - y0)
            if L > 1.5:   # short streak (shutter), brightest at the head
                k = min(1.0, 10.0 / L); xa, ya = x1 - (x1 - x0) * min(1.0, 18.0 / L), y1 - (y1 - y0) * min(1.0, 18.0 / L)
                d.line([(xa * S, ya * S), (x1 * S, y1 * S)], fill=int(255 * a * .45), width=max(1, w - 1))
            r_ = w * .9 + .5
            d.ellipse((x1 * S - r_, y1 * S - r_, x1 * S + r_, y1 * S + r_), fill=int(255 * a))
        im = im.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(.6))
        out = Image.new('RGBA', (W, H), (238, 232, 255, 0)); out.putalpha(im); return out
