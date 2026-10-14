# LUMARC "Edição que faz o olho ficar" (PT-BR) — section author guide

**Goal.** A 40.6 s vertical Reel (1080×1920, 30 fps) in **Brazilian Portuguese** for @lumarc_studio. The founder
(HeyGen take on green, keyed into his purple-monitor studio) explains what good editing is: **"Edição boa não é
enfeite. Ela mostra o que você fala."** — and the film PROVES it: every phrase is literally illustrated by motion
design. The spine is a metaphor: **"Pensa na sua marca como uma casa"** — a premium stylised 3D house builds itself
piece by piece ON THE WORDS (alicerce = posicionamento, paredes = conteúdo, janelas = vídeos, porta = chamado pra
ação), then "Agora repara… você assistiu até aqui porque a casa tava sendo construída na sua frente" (the meta point:
editing holds attention), "Sem edição, você tem um terreno vazio" (the house vanishes, wind), "Com edição… as pessoas
entram" (the house returns lit, people walk in), CTA "Comenta LUMARC", end card.
Same bar as `../lumarc-showcase` ("Esse é o nível que eu quero!"): every effect motivated by a word, landing ON it
(±2 frames), with a sound cue; photographic compositing of him; never a static frame; restraint between beats.

Run everything from `video/lumarc-casa/` with `python3`.

## The words (edit timeline, seconds) — `python3 engine.py info`
| seg | t0–t1 | line | owner |
|---|---|---|---|
| 0 | 0.00–2.08 | Edição boa não é enfeite. | s01 |
| 1 | 2.08–3.84 | Ela mostra o que você fala. | s01 |
| 2 | 3.84–4.40 | Olha só. | s01 |
| 3 | 4.40–4.72 | (silent beat — the empty lot appears) | s01 |
| 4 | 4.72–6.88 | Pensa na sua marca como uma casa. | s02 |
| 5 | 6.88–9.32 | O alicerce é o seu posicionamento. | s02 |
| 6 | 9.32–11.40 | As paredes são o seu conteúdo. | s03 |
| 7 | 11.40–13.40 | As janelas são os seus vídeos. | s03 |
| 8 | 13.40–15.84 | E a porta é o seu chamado pra ação. | s04 |
| 9 | 15.84–16.68 | Agora repara… | s04 |
| 10 | 16.68–21.00 | você assistiu até aqui porque a casa tava sendo construída na sua frente. | s05 |
| 11 | 21.00–22.88 | É isso que uma boa edição faz: | s05 |
| 12 | 22.88–24.72 | dá um motivo pro seu olho ficar. | s05 |
| 13 | 24.72–26.40 | Cada frase, uma imagem. | s05 |
| 14 | 26.40–28.32 | Cada palavra, um movimento. | s05 |
| 15 | 28.32–30.80 | Sem edição, você tem um terreno vazio… | s06 |
| 16 | 30.80–32.80 | e ninguém para pra olhar um terreno vazio. | s06 |
| 17 | 32.80–35.16 | Com edição… as pessoas entram. | s07 |
| 18 | 35.16–37.96 | Quer construir a sua? Comenta "LUMARC". | s07 |
| — | 37.96–40.56 | end card (avatar holds his last frame) | s07 |

Word onsets: `E.word_time('ALICERCE')` is an automatic estimate (0.1–0.3 s off). **Measure the onsets you key effects
on** from `src/tight16k.raw` (mono 16 kHz float32, edit timeline; 10 ms RMS envelope / spectrogram) and report them.
**Jump cuts:** `src/tight.mov` is the take with pauses removed; the pose JUMPS at every segment start except 3→4
(contiguous). Every jump must coincide with a framing change (camera snap, cutaway, a 3D camera move…).

## The house (shared kit — `sections/_house.py`, built first by the kit author, then READ-ONLY for everyone else)
One stylised 3D house model (premium architectural-model look: matte white/cream with LUMARC purple accents, soft
shadows, glowing windows; NOT cartoon) rendered by a pure numpy/PIL 3D renderer with a camera. Its build state is a
single function of time, `state_at(t)`, keyed to the measured words — so the house is the same object in every section.
Sections choose WHERE and HOW BIG it is (placement, camera angle, cutaways) but never change its state timeline.
Read its docstring for the API.

## Files
- `engine.py` (fork of the breakout engine: deterministic frame reads) — **do not edit**. `timeline.py`,
  `build_plate.py`, `sound.py` — integrator-owned.
- `sections/sNN_name.py` — ONE file per section; only edit your own files (+ an optional `sections/_<tag>_kit.py`).
- Studio: `src/studio_plate.png` (his purple-monitor studio). He is seated waist-up at a dark desk along the frame
  bottom (head top ≈ y 560, hands ≈ y 1800 at avatar s=1).
- LUMARC work to show (e.g. in the windows / wall blocks): `../lumarc-showcase/src/assets/*.png` (carousel_1/2,
  design_post, close_food, close_service, close_skill, website…), `../lumarc-breakout/src/assets/loc1..7.png`,
  `../lumarc-therapy/src/assets/` (croissant_hero.jpg, croissant_oven.jpg, storefront_line.jpg, croissant_pull.mp4),
  `E.TEARDOWN`, `E.HYPER` (SILENCE ONE films), `E.logo(w)`. Read frames with `E.clip(path, size).at(src_t)`.

## Section contract (same as the showcase/breakout)
```python
import engine as E
START, END = E.span(i0, i1)
CUES = [(t, 'stone', {}), ...]
def draw(ctx, lt, t): ...          # pure function of t
```
`ctx.cam`, `ctx.bg_img/bg_z/bg_dim/bg_blur`, `ctx.avatar = dict(show, s, x, y, alpha, copies, bright)` (scale around
bottom centre — he is seated at a desk: scaling him down shows the take's bottom edge/desk — hide it), `ctx.add(layer,
img, x, y, center=True, glass=0, alpha=1)` with 'behind' (between studio and him — the house BEHIND him, text behind
him) / 'front' (in front of him, e.g. a model on his desk) / 'screen'; `ctx.wrap`, `ctx.compose(cam=…, avatar=…)`,
`ctx.full`; `ctx.captions/cap_y/cap_size` (Portuguese captions, word-pop, gradient emphasis — keep the spoken words
readable at all times; engine captions or your own kinetic type of the SAME words, never stacked); `ctx.post`.
Helpers: see engine.py (font, word_img, gradient, glass_panel, rounded, shadow, phone, ig_post, pill, put, popin,
fade, eout/ein/back/clamp, zoom, word_time, cached). Proven code: `../lumarc-showcase/sections/*`,
`../lumarc-breakout/sections/*` (feedkit, glasskit).

**Sound.** Declare CUES for every hit. Kinds: whoosh, swoosh_up, swipe, flick, impact, boom, thud, tick, clock,
glass, knock, crack, shatter, pop, glitch, riser (`{'to': t}`), shimmer, rewind, cash, click, type, heart, shutter,
notify, plus construction: **stone** (heavy slab lands), **block** (`{'seed': n}` one wall block snaps in), **wind**
(`{'dur': s}`), **door** (latch/thump), **switch** (a light switches on), **murmur** (`{'dur': s}` people arriving).
Optional `{'gain': dB, 'pan': -1..1}`. The score is BUILT LIKE THE HOUSE (sound.py): bare pulse on the empty lot,
+kick/sub on "alicerce" (seg 5), +claps/hats on "paredes" (6), +keys/arp on "janelas" (7), full on "porta" (8),
SILENCE for "Agora repara…" (seg 9, hard), groove back for 10–14, nothing but your wind for 15–16, riser + full
drop for 17–18, end boom + shimmer at 37.96.

**Design language.** LUMARC: night #0e0e14, gradient #4f6bff → #6a55ff → #9a4dff, white #faf9f6, font Outfit,
frosted glass, soft purple glow, expo-out motion. The house: architectural maquette, clean, lit by the studio's purple/
blue monitors (rim light) with warm interior light in the windows. Phone safe area: key text inside x 80–1000,
y 220–1640; text ≥ 34 px. Never say anything is AI-made.

**Budget.** ≤ 0.9 s/frame average. Cache static art; the house renderer must be fast (cache per-state geometry).

## Tools
```
python3 engine.py info
python3 engine.py sheet <t0> <t1> <step> out/<you>/sheet.jpg 6
python3 engine.py stills out/<you> <t1> <t2> ...
python3 engine.py render <t0> <t1> out/<you>/clip.mp4
```
4 shared CPUs. Read every image you render and judge it like a Motion Awards juror. Iterate until world-class.
