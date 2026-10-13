# LUMARC showcase Reel — section author guide

**Goal.** A 59 s vertical Reel (1080×1920, 30 fps) where the LUMARC founder (HeyGen avatar, keyed from green and
composited into his purple-monitor studio) explains why content quality wins customers. The edit itself IS the
portfolio: it must look like the most premium motion-design studio made it — "outro nível". Every effect is
*motivated* by a word, lands *on* that word (±2 frames), and has a sound cue. Restraint between signature moments;
never a static frame.

Run everything from `video/lumarc-showcase/` with `python3`.

## Files
- `engine.py` — compositor + helpers. **Do not edit** (ask the integrator if you need something). Read it.
- `timeline.py` / `python3 engine.py info` — the 33 speech segments (`TL[i]` with `t0, t1` on the edit timeline) and captions.
- `sections/sNN_name.py` — ONE file per section. Only edit your own files. Put helpers inside them.
- `src/assets/*.png` — bad_blurry_photo, bad_shaky_video, bad_flyer (896×1120, 4:5), close_food, close_service,
  close_skill (752×1344, 9:16), carousel_1, carousel_2, design_post (4:5), website (1344×752). Load with `E.asset('close_food')`.
- Other footage: `E.TEARDOWN` (SILENCE ONE teardown motion film, vertical 34.5 s — premium product Reel), `E.HYPER`
  (SILENCE ONE hyper film; LUMARC logo card at 28.3–34.4 s). Read frames with `E.clip(path, size).at(src_t)`.
  LUMARC logo: `E.logo(width)` (RGBA, 640×218 source).

## Section contract
```python
import engine as E
START, END = E.span(i0, i1)          # covers TL segments i0..i1 (boundaries are fixed — do not change them)
CUES = [(t, 'impact', {}), ...]      # absolute timeline seconds; kinds below
def draw(ctx, lt, t):                # called every frame; lt = t - START. MUST be a pure function of t
    ...
```
`ctx` (fresh every frame — see `Ctx` in engine.py):
- `ctx.cam = dict(z, x, y, dx, dy, rot)` virtual camera over the world (z ≥ 1; default z=1.12 around (540, 820)).
- `ctx.bg_img` (replace the studio with your own RGB 1080×1920 image), `ctx.bg_z` (zoom of the background ONLY — dolly
  zoom / parallax), `ctx.bg_dim`, `ctx.bg_blur`.
- `ctx.avatar = dict(show, s, x, y, alpha, copies=[{x, y, s, alpha}], bright)` — the keyed founder. Scale is around the
  bottom centre (his waist is cut by the frame bottom: keep his bottom edge at/below 1920, i.e. `y >= 0`).
- `ctx.add(layer, img, x, y, center=True, glass=0, alpha=1)` with layer `'behind'` (between studio and avatar — text
  BEHIND the person), `'front'` (over the avatar, still moved by the camera) or `'screen'` (screen space, after camera).
  `glass=12` blurs whatever is under the card (frosted glass). Use `E.glass_panel(w, h)` for the card art.
- `ctx.wrap = fn(frame_rgba) -> frame_rgba` — gets the fully composed camera frame; return any new frame
  (frame-in-frame inside a phone, swipe, glass slats, shatter…). `ctx.compose(cam={...}, avatar={...})` renders the
  world again through another camera (for two framings in one frame, e.g. a swipe revealing the next framing).
- `ctx.full = img` replaces the whole world (no avatar) — use for full-screen inserts.
- `ctx.captions` (bool), `ctx.cap_y` (default 1420), `ctx.cap_size` (92). Captions are word-pop, gradient on emphasis.
  Keep the spoken words readable at all times — either the engine captions, or your own big kinetic type of the SAME
  words (then turn captions off). Never stack two texts on top of each other.
- `ctx.post = dict(flash, flash_col, glitch, rgb, zoom_blur, vignette, grain, bright, sat)`.

Helpers in engine: `font(size, wght)`, `word_img(text, size, 'white'|'grad')` (stroked/shadowed word), `big_text`,
`kinetic(text, size, style, t, t0)`, `gradient(w, h, E.GRAD)`, `glass_panel`, `rounded`, `shadow`, `phone(content, w)`,
`laptop(content, w)`, `ig_post(img, user, w)`, `pill(text, size, wght, fill, grad=True)`, `put`, `popin(lt)`, `fade`,
`text_im`, easing `eout/ein/back/clamp`, `zoom(img, s, anchor, dx, dy, rot)`, `word_time('TASTE')` (start time of a
caption word), `E.seg_t(i, frac)`, `E.cached(key, fn)` (cache static art — never per-frame-unique keys).

**Jump cuts.** The plate is the take with the pauses removed: the founder's pose JUMPS at every `TL[i]['t0']`.
Every segment start inside your span must coincide with a framing change (camera z/position snap, a transition, a
cutaway) so the jump reads as an intentional multicam cut.

**Sound.** Declare `CUES` for every hit. Kinds: whoosh, swoosh_up, swipe, impact, boom, tick, clock (one tick),
glass (shimmering glass slide), shatter, pop, glitch, riser (`{'to': t_end}`), shimmer, cash, click, type (one key),
heart, shutter, notify. The integrator scores the music (120 BPM, anchored so the LUMARC reveal is a downbeat).

**Design language.** LUMARC: deep night background (#0e0e14), gradient #4f6bff → #6a55ff → #9a4dff, white #faf9f6,
font Outfit (`font()`), frosted glass UI, soft purple glow, expo-out motion, generous negative space, crisp type.
Phone safe area: keep key text inside x 80–1000, y 220–1640; text ≥ 34 px. Never say the video/clone is AI-made.

**Budget.** ≤ 0.9 s per frame on average (engine baseline 0.3 s). Cache static art; avoid per-pixel Python loops.

## Tools
```
python3 engine.py info                                   # timeline
python3 engine.py sheet <t0> <t1> <step> out/<you>/sheet.jpg 6   # contact sheet (labels = timeline seconds)
python3 engine.py stills out/<you> <t1> <t2> ...          # full-res frames
python3 engine.py render <t0> <t1> out/<you>/clip.mp4     # silent preview clip (only if needed; slow)
```
Read every image you render and judge it like a Motion Awards juror. Iterate until it is world-class.
