"""s02 — "My Instagram doesn't support me anymore." / "Support you? You only talk to me when you need something." /
"That's not true!"  (3.02–10.46)

3.02  Kevin MS, earnest slow push (soap-opera sincerity). Chip KEVIN · owns a bakery (3.08).
5.567 CUT to his Instagram MS (arms crossed, chin up). Chip HIS INSTAGRAM · 37 followers (5.62).
6.267 CRASH ZOOM on "YOU?" (6.27): 3-frame snap into a CU (z 1.6) anchored ON his face (measured in the take at
      src 0.95: nose ~(556, 420)), so the face punches straight at the lens and settles at (540, 610) — no lateral
      slide. Radial blur centred on the face (world only; chip + caption stay crisp). Held through his head-turn.
7.067 CUT back to the Instagram MS on "You only talk to me…" (he turns back to camera).
8.10  REACTION CUT on "when" (8.12): Kevin close-up, guilty — eyes slide down and away (silent take src 21.95…);
      the accusation "…when you need something." plays over his face. The caption page swaps ON the cut.
9.333 CUT to Kevin MS for "That's not true!"; 2-frame snap push on "TRUE!" (9.80), anchored on his face, low thud.
All takes go through K.show() (clean matte: no cream outline / green fringe, which the CUs made obvious).
Measured onsets (voice16k.raw): MY 3.05 · INSTAGRAM 3.37 · DOESN'T 3.75 · SUPPORT 4.04 · ME 4.40 · ANYMORE 4.52 ·
SUPPORT 5.63 · YOU? 6.27 · YOU 7.07 · ONLY 7.16 · TALK 7.58 · TO 7.84 · ME 7.90 · WHEN 8.12 · YOU 8.28 · NEED 8.44 ·
SOMETHING 8.72 · THAT'S 9.37 · NOT 9.59 · TRUE! 9.80
"""
import engine as E
from sections import _A_kit as K

START, END = E.span(1, 3)
W, H, FPS = E.W, E.H, E.FPS
L1, L2, L3 = E.TL[1], E.TL[2], E.TL[3]

F_I = K.fr(L2['t0'])            # 167  5.567  Instagram (line start 5.56)
F_ZOOM = 188                    # 6.267  "YOU?" 6.27 — the snap lands here
F_IMS = 212                     # 7.067  back to the Instagram MS ("YOU" 7.07)
F_KCU = 243                     # 8.100  Kevin reaction CU ("WHEN" 8.12)
F_K3 = 280                      # 9.333  Kevin "That's not true!" ("THAT'S" 9.37)
F_TRUE = 294                    # 9.800  "TRUE!" 9.80 — push lands here
CUTS = [F_I / FPS, F_IMS / FPS, F_KCU / FPS, F_K3 / FPS]
CHIP_Y = 1160

I_FACE = (556., 420.)           # Instagram's face in his take around src 0.9-1.2 (nose bridge)
K_FACE = (560., 470.)           # Kevin's face in line 3 (src 4.6-5.3)
Z_CU = 1.60
CU_TO = (540., 610.)
SNAP = {F_ZOOM - 2: .55, F_ZOOM - 1: .88}      # eased crash-zoom progress per frame (lands = 1.0 on F_ZOOM)

CUES = [
    (3.08, 'tick', {'gain': -4}),                         # chip KEVIN
    (5.62, 'tick', {'gain': -4}),                         # chip HIS INSTAGRAM
    (F_ZOOM / FPS, 'zoom', {}),                           # crash zoom on "YOU?"
    (F_TRUE / FPS, 'thud', {'gain': -3}),                 # "TRUE!"
]

def src_of(line, t): return line['s0'] + (t - line['t0'])

def ms_cam_I(t):
    return dict(z=1.0 + .02 * (t - L2['t0']), x=470., y=380., dx=0., dy=0., rot=0.)
def screen_of(cam, p):
    """where world point p lands on screen through camera `cam` (engine maths incl. the edge clamp)."""
    z = max(1., cam['z']); X, Y = cam['x'] + cam['dx'], cam['y'] + cam['dy']
    X = min(max(X, W - z * (W - cam['x'])), z * cam['x']); Y = min(max(Y, H - z * (H - cam['y'])), z * cam['y'])
    return X + (p[0] - cam['x']) * z, Y + (p[1] - cam['y']) * z

def draw(ctx, lt, t):
    f = K.fr(t)
    if f < F_I:
        # ---------------- Kevin: "My Instagram doesn't support me anymore." — slow sincere push
        K.show(ctx, 'K', src_of(L1, t), 'K')
        u = t - START
        ctx.cam.update(z=1.0 + .028 * u, x=556., y=470.)
        K.chip(ctx, t, 3.08, 4.80, 'KEVIN', 'owns a bakery', y=CHIP_Y)
    elif f < F_IMS:
        # ---------------- Instagram MS -> crash zoom on "YOU?" -> held CU through the head-turn
        K.show(ctx, 'I', src_of(L2, t), 'I')
        if f < F_ZOOM - 2:
            ctx.cam.update(ms_cam_I(t))
        else:
            c0 = ms_cam_I((F_ZOOM - 3) / FPS); s0 = screen_of(c0, I_FACE)
            k = SNAP.get(f, 1.0)
            z = c0['z'] + (Z_CU - c0['z']) * k + .03 * max(0., t - F_ZOOM / FPS)        # tiny creep while held
            sx, sy = K.lerp(s0[0], CU_TO[0], k), K.lerp(s0[1], CU_TO[1], k)
            ctx.cam.update(z=z, x=I_FACE[0], y=I_FACE[1], dx=sx - I_FACE[0], dy=sy - I_FACE[1])
            if f in SNAP:                                    # motion blur on the world only, centred on the face
                ctx.wrap = K.zoom_blur(.9 if f == F_ZOOM - 2 else .45, anchor=(sx, sy))
        K.chip(ctx, t, 5.62, 6.88, 'HIS INSTAGRAM', '37 followers', y=CHIP_Y)
    elif f < F_KCU:
        # ---------------- Instagram MS: "You only talk to me…"
        K.show(ctx, 'I', src_of(L2, t), 'I')
        ctx.cam.update(z=1.03 + .02 * (t - F_IMS / FPS), x=470., y=380.)
    elif f < F_K3:
        # ---------------- REACTION: Kevin close-up, guilty, under "when you need something."
        u = t - F_KCU / FPS
        K.show(ctx, 'K', 21.95 + u, 'K')
        ctx.cam.update(K.face_cam(K.FACE['K'], 1.48 + .05 * u, to=(540, 660)))
    else:
        # ---------------- Kevin MS: "That's not true!" + snap push on TRUE! (anchored on his face)
        K.show(ctx, 'K', src_of(L3, t), 'K')
        k = {F_TRUE - 1: .62}.get(f, 1.0 if f >= F_TRUE else 0.0)
        ctx.cam.update(z=1.0 + .13 * k + .025 * max(0., t - F_TRUE / FPS), x=K_FACE[0], y=K_FACE[1])
        if f == F_TRUE - 1:
            sx, sy = screen_of(ctx.cam, K_FACE); ctx.wrap = K.zoom_blur(.18, anchor=(sx, sy))
    K.captions(ctx, t, (1, 2, 3), cuts=CUTS)
