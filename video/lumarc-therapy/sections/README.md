# LUMARC "Couples Therapy — for brands" — section author guide

**Goal.** A 60 s vertical comedy Reel (1080×1920, 30 fps) for @lumarc_studio. A bakery owner (Kevin) and his own
Instagram account (personified: gradient hoodie, sunglasses, arms crossed, offended) are in couples therapy. The
therapist is LUMARC. Instagram complains like a neglected partner (last post Christmas 2021, a flyer with seven fonts,
"my algorithm cried"); the therapist prescribes "your croissants deserve a movie" → a 3.6 s cinematic croissant
trailer → Instagram: "…Oh. OH. Okay… I'm listening." → CTA "comment LUMARC — we do couples therapy. For brands."

It has to be **genuinely funny** and **look real**. The comedy language is the mockumentary / sitcom: crash zooms on
punchlines, reaction cutaways (the silent face of whoever is listening is half the joke), lower-third name chips,
comic inserts (the flyer, the 2021 post), sound stingers, dead air + crickets. Timing is everything: an effect lands
ON its word (±2 frames) or in the beat right after it — never early, never mushy. Restraint: the actors carry the scene;
effects punctuate. The compositing must stay photographic (it's a real office) — no cartoon UI over faces.
**No frame ever shows more than one of the three characters** (the owner's rule: no group shots / split screens).
The quality bar is `../lumarc-showcase` (the owner: "Esse é o nível que eu quero!").

Run everything from `video/lumarc-therapy/` with `python3`.

## The script on the edit timeline (`python3 engine.py info`)
| line | t0–t1 | who | line | owner |
|---|---|---|---|---|
| — | 0.00–0.40 | — | (title card over the empty office; "So…" starts at 0.40 under it) | s01 |
| 0 | 0.40–2.80 | T | So… what brings you two here today? | s01 |
| 1 | 3.02–5.42 | K | My Instagram doesn't support me anymore. | s02 |
| 2 | 5.56–9.24 | I | Support you? You only talk to me when you need something. | s02 |
| 3 | 9.32–10.32 | K | That's not true! | s02 |
| 4 | 10.46–13.82 | I | Your last post was Christmas. Twenty twenty-one. | s03 |
| 5 | 13.92–14.80 | K | I've been busy! | s03 |
| 6 | 15.04–17.96 | I | And when you DO show up… it's a flyer. | s04 |
| 7 | 18.08–19.64 | K | People love flyers! | s04 |
| 8 | 19.82–22.50 | I | Seven fonts, Kevin. SEVEN. | s04 |
| 9 | 22.94–25.06 | T | Kevin… how did that make you feel? | s05 |
| 10 | 25.62–26.30 | K | …Creative? | s05 |
| 11 | 26.82–28.26 | I | My algorithm cried. | s05 |
| 12 | 28.66–31.14 | T | Instagram, what do you need from him? | s06 |
| 13 | 31.38–36.70 | I | Consistency. Good lighting. Reels. Is that too much to ask? | s06 |
| 14 | 36.84–39.24 | K | I sell croissants, not movies! | s07 |
| 15 | 39.58–42.78 | T | Kevin… your croissants deserve a movie. | s07 |
| — | 42.90–46.50 | — | THE MOVIE (no dialogue) | s07 |
| 16 | 46.50–49.18 | I | …Oh. OH. Okay… I'm listening. (4 parts, pauses tightened) | s08 |
| 17 | 49.58–57.30 | T | If your Instagram stopped talking to you… comment "LUMARC". We do couples therapy. For brands. | s08 |
| — | 57.30–59.90 | — | end card | s08 |

Word onsets: `E.word_time('FLYER')` is an automatic estimate (often 0.1–0.5 s off, worst inside lines with long
internal pauses such as 4, 13, 16, 17). **Measure the onsets you key effects on** from `src/voice16k.raw` (mono 16 kHz
float32 on the edit timeline; 10 ms RMS envelope / spectrogram). Put them in a dict at the top of your section and
report them (the integrator merges them into `engine.WORD_FIX`, which drives the captions).

## The takes, the angles, the picture
- Takes (`src/therapist.mp4`, `kevin.mp4`, `instagram.mp4`, 25 fps, green screen): read through `E.take(spk).raw(src_t)`
  / `E.graded(spk, src_t, angle)` (keyed + graded + lit for that angle, RGBA 1080×1920). Silent "listening" reaction
  material: therapist src 25.9–33.3 (nods, writes, raises an eyebrow), Kevin src 18.5–25.7 (arms crossed, offended
  sigh, looks away, guilty look down), Instagram src 34.7–42.0 (eye-roll, head shake, dramatic sigh, small impressed
  smile), plus every ~2 s pause between lines in each take (mouth closed, in character). The therapist take shows a
  small lav mic on his shirt in some passages — acceptable.
- Angles = photo plates of ONE warm afternoon office (`src/assets/`): `angle_therapist` (cognac armchair, window
  behind), `angle_kevin` (left end of the sofa, painting), `angle_instagram` (right end of the sofa, bookshelf + lamp),
  `wide` (establishing, empty room). `E.ANGLES` holds the plate crop / DOF / light for each; `E.plate(angle)`.
- Default picture (`ctx.shot`): each line shows its speaker in his own angle, the take running on past the line into
  its silent pause (mouth closed) until the next line starts. Override `ctx.shot` (spk, src, angle, s, x, y, alpha,
  show) to cut to a REACTION (e.g. Kevin's face during Instagram's punchline: `ctx.shot.update(spk='K', src=19.3,
  angle='K')`) — that is the main comedic tool. Never put a speaking line's audio over a non-speaking face for long
  unless it's a deliberate reaction cut (the voice keeps running; lips not visible = fine).
- Inserts: `src/assets/flyer.png` (the hideous "GRAND OPENING!!! KEVIN'S BAKERY" flyer, 896×1120 — count its fonts),
  `xmas2021.png` (sad Christmas-tree photo with red Comic Sans "Merry Xmas from Kevin's Bakery!!", 896×1120),
  `croissant_hero.jpg` (premium croissant still), `croissant_oven.jpg` (tray out of a glowing oven),
  `storefront_line.jpg` ("KEVIN'S BAKERY" storefront at golden hour with a line of customers), and the video
  `E.CROISSANT_PULL` (1080×1912, 24 fps, 5.04 s: hands pull a warm croissant apart in slow motion — read with
  `E.clip(E.CROISSANT_PULL, size).at(src_t)` — note: 24 fps, so compute frames as `src_t` seconds). LUMARC logo `E.logo(w)`.
  `../lumarc-breakout/sections/feedkit.py` has a convincing dark Instagram feed/post UI kit you can borrow from
  (copy what you need into your own file) for the 2021 post card / notifications.

**Jump cuts.** Each line is a separate cut from its take: every line start is a natural cut (different character).
Lines 2, 4, 13, 16, 17 have long internal pauses but are continuous takes (no jumps inside).

## Section contract
```python
import engine as E
START, END = E.span(i0, i1)          # covers lines i0..i1 (boundaries fixed — do not change them)
CUES = [(t, 'zoom', {}), ...]        # absolute timeline seconds; kinds below
def draw(ctx, lt, t):                # called every frame; lt = t - START. MUST be a pure function of t
    ...
```
`ctx` (fresh every frame — see `Ctx` in engine.py):
- `ctx.shot = dict(show, spk, src, angle, s, x, y, alpha, bright)` — the take on screen (scale around its bottom centre).
  The takes fill the frame (scaling down reveals their cut edges/green — don't).
- `ctx.cam = dict(z, x, y, dx, dy, rot)` virtual camera (z ≥ 1; default z=1.0 around (540, 760)). Crash zoom = a
  2–4 frame snap to z 1.25–1.6 on the face (+ 'zoom' cue), held, then cut away. Slow comedic push = z +3%/s.
- `ctx.bg_img` (replace the plate), `ctx.bg_z`, `ctx.bg_dim`, `ctx.bg_blur`.
- `ctx.add(layer, img, x, y, center=True, glass=0, alpha=1)` layers `'behind'` (between plate and take — e.g. a
  framed photo on the wall behind him), `'front'` (over the take, moved by the camera), `'screen'` (screen space).
- `ctx.wrap = fn(frame_rgba) -> frame_rgba` (post-camera frame access: freeze frames, letterbox, wipes, film looks);
  `ctx.compose(cam={...}, shot={...})` renders the world again through another camera/take (whip pans between two
  characters = two composes sliding). `ctx.full = img` replaces everything (inserts, the movie).
- `ctx.captions` (bool), `ctx.cap_y` (default 1480), `ctx.cap_size` (84). Captions are word-pop; emphasised words in
  the speaker's colour (therapist lavender, Kevin butter-gold, Instagram pink→orange). Keep the spoken words readable at
  all times — engine captions or your own kinetic type of the SAME words (then turn captions off). Never stack texts.
- `ctx.post = dict(flash, flash_col, glitch, rgb, zoom_blur, vignette, grain, bright, sat)`.

Helpers in engine: `font(size, wght)`, `word_img(text, size, 'white'|'grad')`, `cap_word(text, size, spk)`,
`gradient`, `glass_panel`, `rounded`, `shadow`, `phone(content, w)`, `ig_post(img, user, w)`, `pill`, `put`, `popin`,
`fade`, `text_im`, easing `eout/ein/back/clamp`, `zoom(img, s, anchor, dx, dy, rot)`, `word_time(...)`,
`E.cached(key, fn)`. Proven code to copy: `../lumarc-showcase/sections/*` (phone frame-in-frame, glass UI, typed
comment, end card s12), `../lumarc-breakout/sections/*` (feed UI, glass shards), `../lumarc-clones/edit_real.py`.

**Sound.** Declare `CUES` for every hit. Kinds: whoosh, swoosh_up, swipe, zoom (crash-zoom whoosh), impact, boom,
braam (`{'note': 'D1', 'dur': 2.4}`), taiko, thud, tick, clock, pop, ding (`{'note': 'E6'}`), notify (phone ping),
heart, type (`{'i': n}`), click, shutter, scratch (record scratch), crickets (`{'dur': s}`), trombone (sad
wah-wah-wah-waaah), sting (dramatic dun-dun-DUNNN), tissue, riser (`{'to': t_end}`), shimmer, cash, glitch, shing.
Optional `{'gain': dB, 'pan': -1..1}`. Use stingers sparingly — one per joke at most. The score (sound.py): soft
waiting-room lounge under the session, it STOPS after "…Creative?" (25.62) until "My algorithm cried." (26.82) — dead
air for your crickets; the MOVIE (42.90–46.50) gets a trailer score (braam + taiko on 42.90, riser, impact at 45.35);
bright session groove from ~47.0; end boom + shimmer at 57.62. Room tone + wall clock run under all office scenes.

**Design language.** Office scenes: photographic, warm afternoon light, film grain; overlays are sitcom/mockumentary
lower-thirds (clean white/cream type, thin rules, small LUMARC-lavender accent) and real-looking objects (a phone, a
printed flyer, a notepad). Inserts may be graphic and punchy. The LUMARC brand (night #0e0e14, gradient #4f6bff →
#6a55ff → #9a4dff, white #faf9f6, font Outfit) owns the CTA and end card. Phone safe area: keep key text inside
x 80–1000, y 220–1640; text ≥ 34 px. Never say anything is AI-made.

**Budget.** ≤ 0.9 s per frame on average. Cache static art (`E.cached`); avoid per-pixel Python loops.

## Tools
```
python3 engine.py info
python3 engine.py sheet <t0> <t1> <step> out/<you>/sheet.jpg 6
python3 engine.py stills out/<you> <t1> <t2> ...
python3 engine.py render <t0> <t1> out/<you>/clip.mp4     # silent preview (slow; motion checks)
```
The machine has 4 CPUs shared by several authors. Read every image you render and judge it like a comedy editor AND
a Motion Awards juror. Iterate until it's funny, precise and world-class.
