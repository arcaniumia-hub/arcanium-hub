# LUMARC "Pick three." — PAID AD (US, Meta Reels/Stories) — section author guide

**Goal.** A ~32 s vertical ad (1080×1920, 30 fps) in **American English** that will run on Meta (Instagram/Facebook
Reels + Stories) in the US to bring LUMARC NEW CLIENTS (small-business owners). Real money is spent on it: every
second must earn the next. The founder's HeyGen avatar (green take keyed into his purple-monitor studio, seated waist-up
at a dark desk) sells one idea:

> Fast. Cheap. Good — you've always had to **pick two**. Fast + cheap looks cheap; good + fast costs a fortune; good +
> cheap means get in line. That rule was written before AI. LUMARC is **AI-first, not AI-only**: AI does the heavy
> lifting, the team does the thinking. So you get content that's faster, costs less… *and looks like this* (portfolio
> montage). You don't have to pick two anymore. **Pick three.** → Tap "Send message" or call the number on screen.

**THE AD RULES (non-negotiable):**
1. **Muted autoplay.** Most people see it without sound for the first seconds. Every beat must read SILENTLY: big bold
   captions always on, visuals that literally show the line. Sound is a bonus layer.
2. **Frame 1 stops the scroll.** No logo intro, no fade-in. Motion + a bold word + his face in the first 0.3 s.
3. **Meta safe zones.** Reels ads cover the top ~14 % and the bottom ~35 % with UI (account name, ad copy, CTA button)
   and the right edge with buttons. ALL key text (captions, labels, the phone number, the end card lines) must sit inside
   **x 70–960, y 280–1250**. Decorative motion may go anywhere. Engine captions default to `cap_y = 1150`.
4. **No prices, no deadlines, no digits that look like either.** "$" glyphs are fine as a symbol; invoices/queues/
   timers must not show numbers. The only number on screen is the phone **(854) 295-2249** (`from sections import
   _shared as SH; SH.PHONE`) — shown on screen, never spoken.
5. **Never name real brands** (AI tools, Meta, agencies, stock sites). The CTA button is a generic chat-bubble
   "Send message" pill.
6. It must look like a top studio made it (it IS the proof of what LUMARC sells): photographic compositing, LUMARC
   design language, every effect landing ON its word (±2 frames) with a sound cue, eased motion, no static frame, no
   dead air. Quality bar: `../lumarc-showcase` and `../lumarc-ia`.

Run everything from `video/lumarc-pick3/` with `python3`.

## The MASTER timeline (`python3 engine.py info`) — three hooks, then the body
The take contains three alternative hooks. The master timeline plays A1 | A2 | A3 | BODY; `versions.py` (integrator)
splices **hook_k + BODY** into three ads (A1 31.4 s, A2 33.4 s, A3 32.6 s). So:
- **each hook is the FIRST thing a stranger sees** — it must stop the scroll on its own frame 1 (0.00 / 3.00 / 8.00);
- **each hook ends with a clean hard cut into the body at its block end** (3.00 / 8.00 / 12.20) — nothing may animate
  across a block boundary, captions of a hook must be gone by its block end, and the BODY's first frame (12.20) must
  be a strong framing change that works after ANY of the three hooks.

| seg | block | t0–t1 | line | jump |
|---|---|---|---|---|
| 0 | A1 | 0.00–0.56 | FAST. |  |
| 1 | A1 | 0.56–1.00 | CHEAP. | JUMP |
| 2 | A1 | 1.00–1.44 | GOOD. | JUMP |
| 3 | A1 | 1.44–3.00 | You've always · had to · pick two. | JUMP |
| 4 | A2 | 3.00–4.36 | Every agency · says: | JUMP |
| 5 | A2 | 4.36–5.08 | fast, |  |
| 6 | A2 | 5.08–5.64 | cheap |  |
| 7 | A2 | 5.64–6.28 | or good — |  |
| 8 | A2 | 6.28–6.96 | pick two. | JUMP |
| 9 | A2 | 6.96–8.00 | They're wrong. |  |
| 10 | A3 | 8.00–9.20 | Content that's · fast, | JUMP |
| 11 | A3 | 9.20–10.08 | cheap · AND good? |  |
| 12 | A3 | 10.08–12.20 | Everyone says · that's impossible. | JUMP |
| 13 | B | 12.20–13.00 | Fast · and cheap? | JUMP |
| 14 | B | 13.00–13.72 | It looks · cheap. | JUMP |
| 15 | B | 13.72–14.60 | Good · and fast? | JUMP |
| 16 | B | 14.60–15.80 | It costs · a fortune. | JUMP |
| 17 | B | 15.80–16.48 | Good · and cheap? | JUMP |
| 18 | B | 16.48–17.36 | Get in line. | JUMP |
| 19 | B | 17.36–19.28 | That rule was written · before AI. | JUMP |
| 20 | B | 19.28–21.32 | At LUMARC, · we're AI-first. | JUMP |
| 21 | B | 21.32–22.32 | Not AI-only. | JUMP |
| 22 | B | 22.32–23.88 | AI does the · heavy lifting… | JUMP |
| 23 | B | 23.88–25.60 | our team does · the thinking. |  |
| 24 | B | 25.60–27.28 | So you get content · that's faster, | JUMP |
| 25 | B | 27.28–28.36 | costs less… |  |
| 26 | B | 28.36–30.12 | and looks · like this. |  |
| 27 | B | 30.12–31.72 | (silent INSERT — the PORTFOLIO MONTAGE; the avatar must be hidden) | JUMP |
| 28 | B | 31.72–33.24 | You don't have to · pick two · anymore. | JUMP |
| 29 | B | 33.24–34.44 | Pick three. |  |
| 30 | B | 34.44–34.84 | Tap | JUMP |
| 31 | B | 34.84–35.88 | "Send message", |  |
| 32 | B | 35.88–37.48 | or call the number · on the screen. |  |
| 33 | B | 37.48–40.60 | (his silent confident smile — the END CARD) |  |

`E.BLOCK_SPAN` = {'A1': (0, 3.0), 'A2': (3.0, 8.0), 'A3': (8.0, 12.2), 'B': (12.2, 40.6)}.
Word onsets: `E.word_time(...)` is a syllable estimate (0.1–0.3 s off) — **measure the onsets you key on** from
`src/tight16k.raw` (mono 16 kHz float32, master timeline; 10 ms RMS / spectrogram; HeyGen silences are clean) and keep
them in a dict at the top of your file. **Jumps:** the pose jumps at every JUMP segment — cover each with a framing
change (snap zoom, cutaway, full-frame insert, whip, background change).

## THE TRIANGLE (shared kit `sections/_tri.py`, built FIRST by the kit author, then read-only for everyone)
The ad's brand device: a premium glass triangle whose three vertices are **FAST** (top, ⚡ bolt), **CHEAP** (bottom-left,
price-tag icon) and **GOOD** (bottom-right, ★/diamond) — the labels match the spoken words. Edges are light beams. "Pick two" = two vertices + their edge lit, the third
dims and gets a red ✗. The rule "cracks" and shatters; at "Pick three." all three light, the triangle completes with a
shockwave and resolves into the LUMARC logo. Read `_tri.py`'s docstring for the API (pure function of a state dict).

## Assets (all on disk)
- LUMARC work for the montage + inserts: `E.HYPER` (SILENCE ONE hyper film, 30 fps; LUMARC end card at 28.3–34.4 s — don't
  use that part), `E.TEARDOWN`, `E.CROISSANT_PULL` (1080×1912, **24 fps**, 5.04 s), `E.THERAPY_A` (croissant_hero.jpg,
  croissant_oven.jpg, storefront_line.jpg, **flyer.png** = a hideous 7-font flyer, xmas2021.png), `E.SHOWCASE_A`
  (carousel_1/2, design_post, close_food, close_service, close_skill, website, bad_flyer, bad_blurry_photo,
  bad_shaky_video), `E.LOCS` + `E.CLONE_BG` (real-location plates), `E.MOTION3D`, `E.FILMS[...]` (finished LUMARC Reels:
  showcase, breakout, therapy (croissant "movie" ≈ 42.9–46.5 s), casa, clones, + `../lumarc-ia/out/lumarc-ia.mp4`),
  `E.house()` (the 3D maquette kit: `state_at(t)` keyed to the CASA timeline 3.8–35 s), `E.logo(w)`.
- Kits to import read-only (`E._load(name, path)`) or copy from: `../lumarc-ia/sections/_E_kit.py` (AI agent task panel,
  glass cards), `../lumarc-ia/sections/_F_kit.py` (contact card, end card), `../lumarc-breakout/sections/_glasskit.py`
  (glass crack + shatter), `../lumarc-breakout/sections/feedkit.py`, `../lumarc-showcase/sections/*` (glass UI, text
  behind him, end card s12), `sections/_shared.py` (PHONE).

## Section contract
```python
import engine as E
START, END = E.span(i0, i1)
CUES = [(t, 'kind', {}), ...]
def draw(ctx, lt, t): ...          # pure function of t
```
`ctx.cam = dict(z, x, y, dx, dy, rot)`, `ctx.bg_img/bg_z/bg_dim/bg_blur`, `ctx.avatar = dict(show, s, x, y, alpha,
copies, bright)`, `ctx.add(layer, img, x, y, center=True, glass=0, alpha=1)` ('behind' | 'front' | 'screen'),
`ctx.wrap`, `ctx.compose(cam=…, avatar=…)`, `ctx.full`, `ctx.captions/cap_y/cap_size` (word-pop captions, emphasis in
the LUMARC gradient; engine captions OR your own kinetic type of the SAME words — never both, never over his face, always
inside the safe zone), `ctx.post = dict(flash, flash_col, glitch, rgb, zoom_blur, vignette, grain, bright, sat)`.
Helpers: font, word_img, gradient, glass_panel, rounded, shadow, phone, laptop, ig_post, pill, put, popin, fade, eout/
ein/back/clamp, zoom, key, word_time, cached, img, clip.

**Sound.** Declare CUES for every hit (master-timeline seconds; `{'gain': dB, 'pan': -1..1}` optional). Kinds: whoosh,
swoosh, swoosh_up, swipe, flick, zoom, impact, boom, braam (`{'note','dur'}`), taiko, thud, tick, clock, glass, knock,
crack, shatter, pop, ding (`{'note'}`), glitch, riser (`{'to': t}`), shimmer, rewind, cash, click, type (`{'i'}`), heart,
shutter, notify, scratch, crickets (`{'dur'}`), sting, shing, stamp, snap, flatline, scan, lock, ff (`{'dur'}`), counter
(`{'dur'}`), sub, film, plus NEW: **trombone** (sad wah-wah), **buzzer** (wrong-answer buzzer), **tap** (finger tap on
glass). Keep each hook's cues INSIDE its block. **The score** (sound.py, integrator): each hook has its own short
tension bed (ticks + riser) with hits on its words, ending dry at its block end; BODY: a punchy playful-confident groove
starts on 12.20 ("Fast and cheap?") under the three "pick two" jokes; it drops out at "That rule was written" (17.36) to a
tension pad; the rule SHATTERS on "AI" (~18.9) → one beat of silence → the LUMARC DROP at 19.28 (big hit, confident
groove) through 25.6; a build 25.6–28.36 ("faster… costs less…"); "this." (~29.5) → the MONTAGE gets trailer hits on
its cuts (braam/taiko) until 31.72; breakdown (pad only) for "You don't have to pick two anymore."; **"Pick three."
(~33.3) = the biggest drop of the ad**; groove under the CTA; end boom + shimmer at 37.48.

**Design language.** LUMARC: night #0e0e14, gradient #4f6bff → #6a55ff → #9a4dff, white #faf9f6, font Outfit, frosted
glass, soft purple glow, expo-out motion. The "pick two" world can be ironic (cheap flyers, absurd invoices, queues) —
the owner LOVES humor — but readable in a split second.

**Budget.** ≤ 0.9 s/frame average. Cache static art; read videos monotonically (Clip.at).

## Tools
```
python3 engine.py info
python3 engine.py sheet <t0> <t1> <step> out/<you>/sheet.jpg 6
python3 engine.py stills out/<you> <t1> <t2> ...
python3 engine.py render <t0> <t1> out/<you>/clip.mp4
```
4 shared CPUs (several authors at once): prefer sheets/stills, short clips (≤ 4 s). Read every image you render and judge
it like a Cannes Lions juror AND a performance marketer watching it muted on a phone. Iterate until world-class.
