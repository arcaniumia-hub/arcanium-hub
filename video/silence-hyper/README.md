# SILENCE ONE — "On Mute" (hyper motion film)

34.4 s vertical (1080×1920, 30 fps, 150 BPM) before/after product film for LUMARC, rendered entirely in code.

- Open `index.html` to play it live (self-contained: all images and fonts are inlined in `bundle.js`; `music.mp3` next to it).
- `storyboard.json` — the shot list + music cue sheet (produced by a 3-pitch / 2-judge creative panel).
- `GUIDE.md` — engine contract for scene authors.
- `src/engine.js` — layer compositor (bg 2D → 3D → fg 2D), 2-level bloom, final FX shader (aberration, zoom blur, punch, shake,
  glitch, liquid warp, pixelate, grade, flash, vignette, grain, letterbox), sub-frame motion blur.
- `src/model.js` procedural headphone · `src/fx3d.js` particles/text rings/wave terrain/streaks · `src/lib.js` helpers, ANC ring motif.
- `src/scenes/s01…s13` — one file per scene. `sound/score.py` (+ `sound/lib.py`) renders `music.wav` / `music.mp3`.

Build & render (needs `npm install`, ffmpeg, and Playwright on NODE_PATH):
```
node tools/build.cjs                                   # bundle.js
python3 sound/score.py                                 # music.wav + music.mp3
node tools/render.cjs video master.mp4 music.wav       # full film
tools/review.sh                                        # contact sheets per scene -> review/
```
