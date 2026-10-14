# LUMARC "IA só faz conteúdo genérico?" (PT-BR) — section author guide

**Goal.** A 76.5 s vertical Reel (1080×1920, 30 fps) in **Brazilian Portuguese** for @lumarc_studio. The founder's HeyGen
avatar (green take keyed into his purple-monitor studio, seated waist-up at a dark desk) calls out a myth — *"IA só faz
conteúdo genérico, né?"* — and answers it. The film itself is the proof: **a SHOWREEL of the editing level AI delivers
when the right people use it**. Every phrase triggers a different signature technique, landing exactly on the spoken
word, and the LUMARC portfolio (SILENCE ONE films, the croissant movie, the 3D house, the feed/glass-shatter Reel,
real-location plates, the showcase mockups) appears as the work. Then LUMARC presents itself as **AI-first** (AI does the
heavy lifting, the team brings strategy, creativity, taste and *the right AI used the right way*) → result: **faster
delivery, lower price, nothing generic** (NEVER show numbers for price or time) → twist: *"e o resto desse vídeo? …
também foi feito noventa por cento com IA"* → CTA *"Entre em contato com a gente. O número tá aqui na tela."* with the
phone **(854) 295-2249** on screen → end card.

The quality bar is `../lumarc-showcase` (the owner: "Esse é o nível que eu quero!") and `../lumarc-casa` (motion that
literally illustrates each word). The owner likes HUMOR — the self-aware AI-avatar beat must be genuinely funny. He wants
the WORK shown more than the talking head, real-looking compositing (DOF, light match, rim, grain), fast tight cuts,
no dead air, never a static frame. This film must look like a reel a top studio would post to win clients.

Run everything from `video/lumarc-ia/` with `python3`.

## The words (edit timeline, seconds) — `python3 engine.py info`
| seg | t0–t1 | line | jump | owner |
|---|---|---|---|---|
| 0 | 0.00–4.48 | Você já deve ter ouvido… ou até concorda… que IA só faz conteúdo genérico, né? | | s01 (A) |
| 1 | 4.48–7.68 | Imagem que parece banco de imagem… texto sem alma… | | s01 (A) |
| 2 | 7.68–9.84 | vídeo que parece todos os outros. | | s01 (A) |
| 3 | 9.84–11.96 | Mas será que o problema é a IA… | JUMP | s02 (A) |
| 4 | 11.96–15.72 | ou você só não encontrou alguém que saiba usar o potencial máximo dela? | | s02 (A) |
| 5 | 15.72–17.84 | Ah, e pode me desconsiderar nesse vídeo… | JUMP | s03 (B) |
| 6 | 17.84–19.60 | eu claramente sou IA, né? | | s03 (B) |
| 7 | 19.60–22.20 | Só tô aqui pra prender a sua atenção por alguns segundos. | | s03 (B) |
| 8 | 22.20–24.48 | Um pincel não pinta um quadro sozinho. | JUMP | s04 (B) |
| 9 | 24.48–26.24 | A IA é a ferramenta. | JUMP | s04 (B) |
| 10 | 26.24–28.00 | A diferença tá em quem usa. | JUMP | s04 (B) |
| 11 | 28.00–30.76 | Deixa eu te mostrar o que acontece quando a IA tá na mão certa. | JUMP | s05 (C) |
| 12 | 30.76–32.96 | Um produto com cara de comercial de cinema. | JUMP | s05 (C) |
| 13 | 32.96–35.24 | Um texto que dança no ritmo da sua fala. | JUMP | s05 (C) |
| 14 | 35.24–37.04 | Um cenário que muda num estalo. | JUMP | s05 (C) |
| 15 | 37.04–38.08 | Um clone seu… | JUMP | s06 (D) |
| 16 | 38.08–39.00 | ou três. | | s06 (D) |
| 17 | 39.00–41.08 | Uma casa que se constrói na sua frente. | JUMP | s06 (D) |
| 18 | 41.08–43.40 | E um vídeo que você não consegue parar de assistir. | JUMP | s06 (D) |
| 19 | 43.40–45.92 | Aqui na LUMARC, a gente é AI-first: | JUMP | s07 (E) |
| 20 | 45.92–48.20 | a IA faz grande parte do trabalho pesado… | JUMP | s07 (E) |
| 21 | 48.20–50.20 | e o nosso time coloca o que ela não tem: | JUMP | s07 (E) |
| 22 | 50.20–51.08 | estratégia, | JUMP | s07 (E) |
| 23 | 51.08–52.20 | criatividade, | | s07 (E) |
| 24 | 52.20–53.24 | bom gosto… | | s07 (E) |
| 25 | 53.24–55.36 | e, principalmente, a IA certa, | | s07 (E) |
| 26 | 55.36–57.08 | usada do jeito certo. | | s07 (E) |
| 27 | 57.08–58.00 | O resultado? | JUMP | s08 (F) |
| 28 | 58.00–59.20 | Entrega mais rápida. | JUMP | s08 (F) |
| 29 | 59.20–60.40 | Preço mais baixo. | | s08 (F) |
| 30 | 60.40–62.84 | E um conteúdo que ninguém diria que é genérico. | JUMP | s08 (F) |
| 31 | 62.84–64.48 | Ah… e o resto desse vídeo? | JUMP | s09 (F) |
| 32 | 64.48–66.92 | A edição, os efeitos, a trilha… | JUMP | s09 (F) |
| 33 | 66.92–69.32 | Também foi feito noventa por cento com IA. | JUMP | s09 (F) |
| 34 | 69.32–70.56 | Quer o mesmo pra sua marca? | JUMP | s10 (F) |
| 35 | 70.56–71.72 | Entre em contato com a gente. | JUMP | s10 (F) |
| 36 | 71.72–73.28 | O número tá aqui na tela. (he points down) | | s10 (F) |
| 37 | 73.28–76.48 | (silent confident smile — the END CARD) | | s10 (F) |

Word onsets: `E.word_time('GENÉRICO')` is an automatic syllable estimate (0.1–0.3 s off). **Measure the onsets you key
effects on** from `src/tight16k.raw` (mono 16 kHz float32 on the edit timeline; 10 ms RMS envelope / spectrogram; HeyGen
silences are clean, floor −68 dB) and put them in a dict at the top of your section; report them.
**Jump cuts:** `src/tight.mov` is the take with pauses removed; the pose JUMPS at every segment marked JUMP. Every jump
must coincide with a framing change (camera snap, cutaway, full-frame insert, background swap, whip…). Inside a section
the same rule applies.

## Files
- `engine.py` (fork of the casa engine: deterministic frame reads) — **do not edit**. `timeline.py`, `build_plate.py`,
  `sound.py` — integrator-owned.
- `sections/sNN_name.py` — ONE file per section; only edit your own files (+ an optional `sections/_<tag>_kit.py`).
- Studio: `src/studio_plate.png` (his purple-monitor studio). He is seated waist-up at a dark desk along the frame
  bottom (head top ≈ y 560, hands on the desk ≈ y 1800 at avatar s=1). Scaling him down shows the take's bottom edge —
  hide it (desk/foreground element, frame-in-frame, crop).

## Assets (all on disk; read through `E.img(path)` / `E.asset(name)` / `E.clip(path, size).at(src_t)`)
- **This film** `src/assets/` (generated): `stock_team` (the cheesiest corporate stock photo: high-fives, plastic
  smiles, "Better Together"), `ai_brain` (glowing circuit brain + binary rain — THE generic-AI cliché), `robot_hand`
  (robot finger touching a human finger), `brush_green` (a photoreal artist paintbrush on pure #00FF00 — key it with
  `E.key`, 1024²), `ai_selfie` (waxy plastic-skin "AI influencer" selfie with a latte), `ai_planet` (lone silhouette vs
  giant glowing planet — the AI-wallpaper cliché). All 896×1120 except the brush. Generic AI text, quote cards, slop
  grids: draw them.
- **LUMARC work:** `E.HYPER` (SILENCE ONE hyper film, 30 fps; LUMARC end card at 28.3–34.4 s — don't show that part),
  `E.TEARDOWN` (SILENCE ONE teardown motion film), `E.CROISSANT_PULL` (1080×1912, **24 fps**, 5.04 s slow-motion
  pull-apart), `E.THERAPY_A/croissant_hero.jpg, croissant_oven.jpg, storefront_line.jpg`, `E.MOTION3D` (LUMARC 3D motion
  film), `E.FILMS[...]` (finished LUMARC Reels: showcase, breakout, therapy — croissant movie ≈ 42.9–46.5 s, casa, clones;
  captions burned in — fine inside phone mockups), `E.SHOWCASE_A/*.png` (carousel_1/2, design_post, close_food,
  close_service, close_skill, website), `E.LOCS` + `E.CLONE_BG` (14 real-location plates 752×1344: studio, café, rooftop
  sunset, Paris, boardroom, classroom, beach + 7 more — scale up with care, add DOF), `E.logo(w)`.
- **Kits you may import (read-only):** `E.house()` → the casa 3D maquette kit (`state_at(t)` is keyed to the CASA film's
  timeline: lot rises 3.89, outline 6.40, slab 6.99, walls ~9.6–11, windows ~11.6–12.9, door ~13.7, lit/people ~32.9–35;
  map your own time onto it for a time-lapse; `render(state, cam, size, t)`; run `python3 -c "import engine as E;
  E.house().prewarm()"` once). `../lumarc-breakout/sections/feedkit.py` (dark Instagram feed/post UI) and
  `../lumarc-breakout/sections/_glasskit.py` (glass crack + shatter) — import with `E._load(name, path)` or copy what you
  need into your own kit. Proven code to read: `../lumarc-showcase/sections/*` (phone frame-in-frame, glass UI, text
  behind him, clone split, typed comment, end card s12), `../lumarc-casa/sections/*`, `../lumarc-clones/edit_real.py`.

## Section contract
```python
import engine as E
START, END = E.span(i0, i1)
CUES = [(t, 'kind', {}), ...]
def draw(ctx, lt, t): ...          # pure function of t
```
`ctx.cam = dict(z, x, y, dx, dy, rot)`, `ctx.bg_img/bg_z/bg_dim/bg_blur`, `ctx.avatar = dict(show, s, x, y, alpha,
copies, bright)` (scale around bottom centre), `ctx.add(layer, img, x, y, center=True, glass=0, alpha=1)` with 'behind'
(between studio and him — text behind him), 'front' (in front of him, moved by the camera), 'screen' (screen space);
`ctx.wrap = fn(frame_rgba) -> frame_rgba` (freeze, letterbox, frame-in-frame, wipes), `ctx.compose(cam=…, avatar=…)`
(render the world again through another camera/avatar — clone panels, whips), `ctx.full = img` (full-frame inserts);
`ctx.captions/cap_y/cap_size` (Portuguese word-pop captions, emphasis in the LUMARC gradient — keep the spoken words
readable at all times: engine captions OR your own kinetic type of the SAME words, never both); `ctx.post = dict(flash,
flash_col, glitch, rgb, zoom_blur, vignette, grain, bright, sat)`. Helpers: font, word_img, gradient, glass_panel,
rounded, shadow, phone, laptop, ig_post, pill, put, popin, fade, text_im, eout/ein/back/clamp, zoom, key, word_time,
cached, img, clip.

**Sound.** Declare CUES for every hit (absolute timeline seconds; `{'gain': dB, 'pan': -1..1}` optional). Kinds:
whoosh, swoosh_up, swipe, flick, zoom (crash-zoom whoosh), impact, boom, braam (`{'note': 'D1', 'dur': 2.4}`), taiko,
thud, tick, clock (`{'i': n}`), glass, knock, crack, shatter, pop, ding (`{'note': 'E6'}`), glitch, riser (`{'to': t}`),
shimmer, rewind (`{'dur': s}`), cash, click, type (`{'i': n}`), heart, shutter, notify, scratch (record scratch),
crickets (`{'dur': s}`), sting, shing, stone, block (`{'seed': n}`), door, switch, wind (`{'dur': s}`), murmur, plus NEW
for this film: **stamp** (rubber stamp slam), **snap** (finger snap), **flatline** (`{'dur': s}` EKG beep → flat tone),
**scan** (`{'dur': s}` sci-fi scan sweep), **lock** (padlock clunk), **ff** (`{'dur': s}` fast-forward zip), **counter**
(`{'dur': s}` rolling-digit ticks), **sub** (deep sub drop), **film** (`{'dur': s}` projector rattle). Use stingers
sparingly. **The score** (sound.py, integrator): 0–9.84 a deliberately CHEESY generic stock-music loop (ukulele/claps —
the "generic" world, a joke); a record SCRATCH + silence at 9.84 ("Mas será que…"); a tense pulse + riser into "máximo"
(~15.0) → hit; light playful beat 15.72–22.2 (the AI-avatar joke; leave room for crickets/a sting); a single piano/strings
"artist" motif 22.2–28.0; on "mão certa" (~30.3) the SHOWREEL DROP — hybrid trap/cinematic beat 30.76–43.4 (stops dead
for the crickets-free pause in "um clone seu… ou três"); LUMARC groove 43.4–57.08; hard stop on "O resultado?" 57.08
(one hit); punchy 58.0–62.84; tape-stop/rewind at 62.84; low pulse building 64.5–69.3 ("noventa por cento" lands on a
hit); warm final groove 69.32–73.28; end boom + shimmer at 73.28.

**Design language.** LUMARC: night #0e0e14, gradient #4f6bff → #6a55ff → #9a4dff, white #faf9f6, font Outfit, frosted
glass, soft purple glow, expo-out motion. The generic-AI world (hook) is the anti-brand: cold blue clichés, flat stock
light, Comic-ish defaults, sameness — then LUMARC's world takes over. Phone safe area: key text inside x 80–1000,
y 220–1640; text ≥ 34 px; never put text over his face. NEVER show a number for price or delivery time; never name real
AI products or stock-photo brands. The phone number (854) 295-2249 is the only number with a "price/contact" meaning.

**Budget.** ≤ 0.9 s/frame average. Cache static art (`E.cached`); avoid per-pixel Python loops; video readers are
sequential (Clip.at) — read monotonically.

## Tools
```
python3 engine.py info
python3 engine.py sheet <t0> <t1> <step> out/<you>/sheet.jpg 6
python3 engine.py stills out/<you> <t1> <t2> ...
python3 engine.py render <t0> <t1> out/<you>/clip.mp4
```
4 shared CPUs (several authors at once — be frugal: sheets and stills first, short clips). Read every image you render
and judge it like a Motion Awards juror AND a comedy editor. Iterate until world-class.
