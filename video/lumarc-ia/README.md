# LUMARC — "IA só faz conteúdo genérico?" (PT-BR, AI-first showreel Reel)

76.5 s vertical Reel (1080×1920, 30 fps) for @lumarc_studio, in Brazilian Portuguese. The founder's HeyGen avatar
(green take, keyed into his purple-monitor studio) calls out the myth "IA só faz conteúdo genérico, né?" and the film
answers it by BEING a showreel: every phrase gets its own signature technique, and the LUMARC portfolio is the work
shown. Arc: generic-AI slop wall + GENÉRICO stamp → record scratch, potential gauge slams to MÁXIMO, the wall shatters →
self-aware "eu claramente sou IA" comedy → paintbrush metaphor → SHOWREEL (cinema product, dancing type, scene swaps,
clones, the 3D house, the unscrollable Reel that shatters) → LUMARC is AI-first (agent does the heavy lifting; team
brings strategy, creativity, taste, the right AI) → faster / cheaper (no numbers) / nothing generic → twist "90% feito
com IA" → CTA with the phone (854) 295-2249 on screen → end card.

Built with an ultracode workflow: 6 section builders (A–F), each followed by an adversarial reviewer that owned and fixed
the files. Output: `out/lumarc-ia.mp4` (gitignored).

## Rebuild
```
python3 build_plate.py                       # src/take.mp4 (the HeyGen take, 88.9 s, 25 fps) -> src/tight.mov + tight16k.raw
python3 -c "import engine as E; E.house().prewarm()"     # casa 3D house kit caches (out/house/cache)
GRAIN_K=0.55 python3 engine.py prender 4     # out/video.mp4 (silent)
python3 sound.py && python3 sound.py mux     # music.wav + sfx.wav -> out/lumarc-ia.mp4 (-14 LUFS, < 30 MB)
```

## Files
- `timeline.py` — EDL built from the 38 speech islands of the take (`ISL`: start, end, caption, join, hold). Joined
  islands keep the natural pause (no jump); the last SEG is his silent smile (the end card).
- `engine.py` — compositor (fork of lumarc-casa/engine.py) + asset paths for the whole LUMARC portfolio
  (`E.FILMS`, `E.LOCS`, `E.CLONE_BG`, `E.HYPER`, `E.CROISSANT_PULL`, `E.house()` …).
- `sections/README.md` — the creative brief + word timeline every builder followed.
- `sections/_shared.py` — PHONE + the red GENÉRICO stamp (s01 slams it, s08 shatters it).
- `sections/s01_hook` · `s02_virada` (A) · `s03_sou_ia` · `s04_pincel` (B) · `s05_showreel_a` (C) · `s06_showreel_b` (D)
  · `s07_lumarc` (E) · `s08_resultado` · `s09_twist` · `s10_cta` (F), each with its `_X_kit.py`.
- `sound.py` — score (cheesy stock ukulele → scratch → tension → pizzicato → artist motif → showreel trap drop → LUMARC
  groove → results → tape-stop → pulse → warm CTA groove → end boom) + all cue SFX (new: stamp, snap, flatline, scan,
  lock, ff, counter, sub, film) + mux.
- `src/assets/` (gitignored, generated with Higgsfield gpt_image_2_5): stock_team, ai_brain, robot_hand, ai_selfie,
  ai_planet, brush_green. They were fetched through the Higgsfield sandbox `image_paths` channel (the tool result saves the
  full-resolution JPEG under the session's tool-results folder) because the container cannot reach the Higgsfield CDN.
