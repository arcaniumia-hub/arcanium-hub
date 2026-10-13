# LUMARC "Break out of the feed" Reel — section author guide

**Goal.** A ~29 s vertical Reel (1080×1920, 30 fps) for @lumarc_studio. The founder (HeyGen take on green, keyed) is
TRAPPED INSIDE A REEL POST IN THE VIEWER'S OWN INSTAGRAM FEED. He knocks on the glass from the inside, the viewer's
screen cracks, it SHATTERS toward the camera and he steps out into his real purple-monitor studio. Then everything LUMARC
makes "leaves the screen" (the product pops out of the phone, content orbits his head, the reel replays itself, the brand
stays tomorrow) → LUMARC logo → "Comment LUMARC" CTA → end card. It must feel like the most premium motion studio in
the world made it — same bar as `../lumarc-showcase` ("outro nível"): every effect is *motivated* by a word, lands *on*
that word (±2 frames), has a sound cue, and the compositing is photographic (light match, DOF, motion blur, glints,
grain). Never a static frame. Restraint between signature moments.

Run everything from `video/lumarc-breakout/` with `python3`.

## The words (edit timeline, seconds) — `python3 engine.py info`
| seg | t0–t1 | line | owner |
|---|---|---|---|
| 0 | 0.00–0.52 | Hey. | s01 |
| 1 | 0.52–1.40 | Yeah, you. | s01 |
| 2 | 1.40–2.16 | Down here. | s01 |
| 3 | 2.16–4.00 | Your content lives in here. | s01 |
| 4 | 4.00–4.72 | Tiny. | s02 |
| 5 | 4.72–5.32 | Flat. | s02 |
| 6 | 5.32–6.20 | One swipe... | s03 |
| 7 | 6.20–7.08 | and it's gone. | s03 |
| 8 | 7.08–7.80 | (silence — knock, knock) | s03 |
| 9 | 7.80–8.56 | Not mine. | s04 |
| 10 | 8.56–9.28 | (silence — the glass shatters) | s04 |
| 11 | 9.28–11.96 | Good content doesn't stay on the screen. | s04 |
| 12 | 11.96–13.32 | It stays in your head. | s05 |
| 13 | 13.32–15.40 | The product you can almost touch. | s06 |
| 14 | 15.40–17.48 | The video you watch twice. | s07 |
| 15 | 17.48–19.96 | The brand you still remember tomorrow. | s08 |
| 16 | 19.96–22.04 | That's what we build at LUMARC. | s09 |
| 17 | 22.04–24.28 | Want your brand to break out of the feed? | s10 |
| 18 | 24.28–25.64 | Comment "LUMARC" | s10 |
| 19 | 25.64–26.84 | and I'll show you how. | s10 |
| — | 26.84–29.44 | end card hold (no voice; avatar holds last frame) | s10 |

Word onsets: `E.word_time('TOUCH')` is an automatic estimate (can be off by 0.1–0.3 s). **Measure the onsets you key
effects on** from `src/tight16k.raw` (mono 16 kHz float32, edit timeline): 10 ms RMS envelope / spectrogram around the
estimate. Put measured values in a dict at the top of your section and report them (the integrator merges them into
`engine.WORD_FIX`, which drives the captions).

**Jump cuts.** `src/tight.mov` is the take with pauses removed: his pose JUMPS at every segment start EXCEPT 7.08, 7.80,
8.56 and 9.28 (segs 7→11 are one continuous take). Every jump must coincide with a framing change (camera snap, cutaway,
transition, a different scale inside the post…) so it reads as an intentional multicam cut.

## Files
- `engine.py` — compositor + helpers (forked from the showcase). **Do not edit** (the integrator owns it).
- `sections/feedkit.py` — the full-screen dark Instagram-style feed (status bar, top bar, stories, post cards, bottom
  nav) with his Reel as post `FK.SPECIAL`. **Do not edit**; wrap/extend in your own file. Read its docstring.
- `sections/sNN_name.py` — ONE file per section. Only edit your own files. Helpers go inside them (or in a
  `sections/_<yourname>_kit.py` you own — not matched by the section loader).
- `src/assets/*.png` — feed photos: loc1 (desk studio), loc2 (café), loc3 (rooftop sunset), loc4 (Paris street),
  loc5 (boardroom), loc6 (classroom), loc7 (beach) — 752×1344; bad_blurry_photo, bad_shaky_video, bad_flyer (896×1120);
  close_food, close_service, close_skill (752×1344); carousel_1, carousel_2, design_post (4:5); website (1344×752).
  Load with `E.asset('loc2')`.
- LUMARC-made work (the "premium" content): `E.TEARDOWN` (SILENCE ONE headphone teardown motion film, vertical 34.5 s),
  `E.HYPER` (SILENCE ONE hyper film, vertical 34.4 s; LUMARC logo card at 28.3–34.4 s) — read frames with
  `E.clip(path, size).at(src_t)`. Stills: `../silence-motion/img/hero.jpg` (headphone hero on black, 1000×1075 — easy
  luminance key), `macro.jpg` (ear-cup macro), `orbit0..3.jpg` (5×2 turntable sprite sheets 2600×1040 → 10 angles each,
  on black), `../silence-hyper/img/before.jpg` (plain packshot on grey). LUMARC logo: `E.logo(width)` (RGBA).
  `../lumarc-motion-en/lumarc-3d-en.mp4` (LUMARC 3D motion: service cards 12–18 s, post wall ~8 s, logo reveal ~6–8 s).

## The avatar (important — different from the showcase take)
The HeyGen take is a **floating bust** (no body below the chest). The engine pre-frames it (`engine.AV_VF`): at
`avatar.s = 1` his head top is at y≈615, eyes y≈760, the bust's cut edge lies just BELOW the frame bottom (y≈1950) and
his elbows touch the frame edges. If you scale him down (`s < 1`) or move him up (`y < 0`), the cut edge and elbows
become visible — hide them (inside a post/phone crop, behind a foreground element, under a gradient) or don't do it.
He is lit to sit in the dark purple studio (`src/studio_plate.png`, rim light from the monitors).

## Section contract (same as the showcase)
```python
import engine as E
START, END = E.span(i0, i1)          # covers TL segments i0..i1 (boundaries are fixed — do not change them)
CUES = [(t, 'impact', {}), ...]      # absolute timeline seconds; kinds below
def draw(ctx, lt, t):                # called every frame; lt = t - START. MUST be a pure function of t
    ...
```
`ctx` (fresh every frame — see `Ctx` in engine.py):
- `ctx.cam = dict(z, x, y, dx, dy, rot)` virtual camera over the world (z ≥ 1; default z=1.12 around (540, 820)).
- `ctx.bg_img` (replace the studio with your own RGB 1080×1920 image), `ctx.bg_z`, `ctx.bg_dim`, `ctx.bg_blur`.
- `ctx.avatar = dict(show, s, x, y, alpha, copies=[{x, y, s, alpha}], bright)` — scale is around the bottom centre.
- `ctx.add(layer, img, x, y, center=True, glass=0, alpha=1)` with layer `'behind'` (between studio and avatar),
  `'front'` (over the avatar, moved by the camera) or `'screen'` (screen space, after camera + wrap). `glass=12` blurs
  what is under the card (frosted glass). `E.glass_panel(w, h)` for card art.
- `ctx.wrap = fn(frame_rgba) -> frame_rgba` — gets the fully composed camera frame; return any new frame. This is how
  the feed act works: `FK.special_media(ctx)` / `ctx.compose(cam=…)` renders his world, you place it in the feed.
  `ctx.full = img` replaces the whole world (no avatar).
- `ctx.captions` (bool), `ctx.cap_y` (default 1420), `ctx.cap_size` (92). Captions are word-pop, gradient on emphasis.
  Keep the spoken words readable at all times — either the engine captions, or your own big kinetic type of the SAME
  words (then turn captions off). Never stack two texts on top of each other.
- `ctx.post = dict(flash, flash_col, glitch, rgb, zoom_blur, vignette, grain, bright, sat)`.

Helpers in engine: `font(size, wght)`, `word_img(text, size, 'white'|'grad')`, `big_text`, `kinetic`, `gradient(w, h,
E.GRAD)`, `glass_panel`, `rounded`, `shadow`, `phone(content, w)`, `laptop(content, w)`, `ig_post(img, user, w)`,
`pill`, `put`, `popin`, `fade`, `text_im`, easing `eout/ein/back/clamp`, `zoom(img, s, anchor, dx, dy, rot)`,
`word_time('TOUCH')`, `E.seg_t(i, frac)`, `E.cached(key, fn)` (cache static art — never per-frame-unique keys).
`../lumarc-showcase/sections/*.py` contain proven code for: phone frame-in-frame with a real homography (s02), glass
triptych shatter (s06), fluted glass slats + logo (s08), Reel phone / before→after / mockups (s09), typed comment +
profile grid (s11), end card (s12). Reuse ideas and code freely (copy into your file).

**Sound.** Declare `CUES` for every hit. Kinds: whoosh, swoosh_up, swipe, flick (finger flick on the screen), impact,
boom, thud, tick, clock, glass (shimmering glass slide), knock (knuckle on the inside of the phone glass), crack (glass
cracking, `{'dur': .45, 'seed': n}`), shatter (`{'dur': 1.6}`), pop, glitch, riser (`{'to': t_end}`), shimmer, rewind
(tape rewind, `{'dur': .7}`), cash, click, type (one key, `{'i': n}`), heart, shutter, notify. Optional `{'gain': dB,
'pan': -1..1}`. The score (sound.py) is fixed: feed music plays small/band-passed "inside the phone" until 7.08, dead
silence 7.08–7.80 (only your knocks), drone+riser on "Not mine.", full-range 120 BPM groove from 9.28, riser into the
LUMARC downbeat on the word "LUMARC" (seg 16), CTA groove, end boom + shimmer at 26.84.

**Design language.** LUMARC: deep night (#0e0e14), gradient #4f6bff → #6a55ff → #9a4dff, white #faf9f6, font Outfit
(`font()`), frosted glass, soft purple glow, expo-out motion, crisp type. The feed act uses Instagram's own dark UI look
(pure black, white glyphs) — generic, no official logos/wordmarks, fictional handles. Phone safe area: the real Reels UI
covers the right rail (x > 960, y 1000–1750) and the bottom (y > 1700): keep key text inside x 80–1000, y 220–1640;
text ≥ 34 px. Never say the video/clone is AI-made.

**Budget.** ≤ 0.9 s per frame on average (engine baseline ≈ 0.3 s). Cache static art; avoid per-pixel Python loops.

## Tools
```
python3 engine.py info                                       # timeline
python3 engine.py sheet <t0> <t1> <step> out/<you>/sheet.jpg 6   # contact sheet (labels = timeline seconds)
python3 engine.py stills out/<you> <t1> <t2> ...              # full-res frames
python3 engine.py render <t0> <t1> out/<you>/clip.mp4         # silent preview clip (slow; only if needed)
```
The machine has 4 CPUs shared by several authors: prefer sheets/stills; render clips only for motion checks.
Read every image you render and judge it like a Motion Awards juror. Iterate until it is world-class.
