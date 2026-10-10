# SILENCE ONE — hyper motion: scene author guide

Vertical 1080×1920, 30 fps, 150 BPM (beat = 0.4 s = 12 frames, ⅛ = 6 frames, 1/16 = 3 frames, bar = 1.6 s).
Every frame is rendered deterministically by `window.renderAt(t)`.

## Files
- `src/engine.js` — layer compositor + post FX (do not edit unless asked).
- `src/lib.js` — math/easing, beat grid, palette, fonts, 2D text helpers, photos, textures (do not edit unless asked).
- `src/model.js` — procedural SILENCE ONE headphone (`createHeadphone()`), see header comment.
- `src/fx3d.js` — reusable 3D blocks: `morphPoints` (GPU particles morphing between point sets: text → product → logo…),
  `samplePhoto` / `sampleText` / `spherePoints` / `boxPoints`, `textRing` (cylindrical band of type), `textPlane`,
  `waveTerrain` (line-grid sound-wave terrain), `streaks` (additive warp light streaks). Read its header comment.
- `src/scenes/<id>.js` — ONE file per scene. Only edit your own scene file. Put any helper you need inside it.
- `src/scenes/index.js` — ordered list of scenes (the timeline). Scenes are contiguous in beats.
- `storyboard.json` — the final shot list + music cue sheet (source of truth for timing and content).

## Scene contract
```js
import * as THREE from 'three';
import { W, H, BEAT, b2s, seg, eio, eout, expoOut, back, pulse, rnd, text, maskText, letters, drawPhoto, COL, FONT } from '../lib.js';
import { createHeadphone } from '../model.js';
export default {
  id: 's05-tunnel', start: 40, end: 48,      // absolute BEATS (from storyboard.json)
  cutIn: 'punch',                            // 'punch' (default: tiny zoom + aberration kick on the first frames) or 'none'
  init(E) { /* build three.js scenes, materials, textures, particle buffers ONCE. May be async. */ },
  draw(E, lt, t, k) { /* lt = seconds since scene start, t = global seconds, k = 0..1 progress */ },
  motionBlur(lt, t) { return 1; },           // optional: sub-frames (2-6) for whip pans / fast moves; costs N× render time
};
```
`draw` is called every frame (and once per motion-blur sub-frame). Inside it:
- `E.bg` — 2D context BEHIND the 3D layer. Already filled with `E.clearColor` (#050506). Fill it with any colour you like.
- `E.render3D(scene, camera)` — renders a three.js scene into the 3D layer (transparent background). Call 0..n times;
  later calls draw over earlier ones (depth cleared between calls). Lit materials get the studio env map automatically
  (`scene.environmentIntensity` defaults to .5; set `scene.userData.envIntensity` before the first call to change it).
- `E.fg` — 2D context IN FRONT of the 3D layer (cleared to transparent).
- `E.fx` — post FX for this frame (reset to defaults every frame). Knobs (see `FX_DEFAULTS` in engine.js):
  `exposure` (3D only, .85) · `bloom` (.55) `bloomThreshold` (.72) · `rgb` chromatic aberration (.0015; .006 punchy, .02 heavy) ·
  `zoomBlur` 0..1 + `zoomCenter` [x,y] uv · `zoom` punch scale (1 = none, 1.08 = punch-in) · `rot` roll (rad) · `shake` [dx,dy] uv ·
  `glitch` 0..1 + `glitchSeed` (change per frame for animated glitch) · `displace` liquid warp (uv, .01-.08) + `displaceScale` ·
  `pixelate` (px) · `scanlines` 0..1 · `invert` 0..1 · `flash` 0..1 + `flashColor` [r,g,b] linear 0..1 ·
  `sat` `contrast` `brightness` `tint` [r,g,b] · `vignette` (.35) · `grain` (.045) · `letterbox` (fraction per side) · `mirror` (0..3).
- `E.img` — `before` (800×452 cheap e-commerce photo on light grey), `hero` (1000×1075 product on black), `macro` (1100×909),
  `orbit0..3` (40-frame photoreal turntable sprite sheets; use `orbitFrame(ctx, [E.img.orbit0..3], f, cx, cy, size)`), `logo` (LUMARC, 640×218 RGBA).
- `E.THREE`, `E.renderer`, `E.env` are exposed if needed.

Colour pipeline: 2D layers are sRGB and composited exactly. The 3D layer is linear HDR and goes through ACES with
`E.fx.exposure` — so an unlit white (MeshBasicMaterial 0xffffff) lands at ~0.8; for crisp white/emissive 3D text or
glowing lines use colour values 1.5–4 (they also feed the bloom). Use `ADDITIVE` (lib) for particles / light streaks so they
add light without occluding.

## Fonts (`FONT` in lib.js)
`display` Unbounded (300/500/700/800/900) · `impact` Anton (400) · `brand` Outfit (variable, LUMARC) · `ui` Inter (variable) ·
`mono` JetBrains Mono (400/700) · `serif` Instrument Serif (400, italic) · `cheap` Comic Neue (700, BEFORE only).
The recurring ANC RING motif MUST be drawn with `ancRing(ctx, cx, cy, r, {alpha, progress, label, gradient, ...})` (lib) so it is
identical in every scene. Standard edit punches: `downbeatPunch(E.fx, t, at, {...})` and `kickPump(E.fx, t, kickTimes)` (lib).
Use `text(ctx, s, x, y, {size, weight, family, color, align, alpha, spacing, blur, gold, glow, stroke, italic})`,
`maskText`, `letters` (per-letter animation), `fitSize` (auto-fit width), `measure`.

## Rules
- Deterministic: never use `Math.random()` / `Date`. Use `rnd(i)`, `rnd2(i,j)`, `noise1(x)` from lib.
- Timing: hits land on the beat grid. Global seconds of beat n = `b2s(n)`; inside a scene, beat-relative time is `lt / BEAT`.
- Phone legibility: key copy inside x 80–1000, y 220–1640 (Reels UI covers the bottom ~280 px and the right edge).
  Minimum text size ~30 px; headline copy should be big and bold.
- Budget: a frame must render in ≲2.5 s on CPU WebGL (SwiftShader). ≤150k particles, avoid per-pixel JS loops on full-res
  canvases, prefer GPU (three.js) for heavy stuff, cache canvases/textures in `init`, keep `motionBlur` ≤ 4 and only where it matters.
- Never leave the frame static: every frame should have motion (camera drift, particles, parallax), except deliberate
  freeze/silence moments called for by the storyboard.
- The product is SILENCE ONE (stone-grey + champagne-gold). Never write that anything is AI-made.

## Tools (run from `video/silence-hyper`, with `export NODE_PATH=/opt/node-tools/node_modules`)
Build and render YOUR scene alone (other scenes may be half-written by other agents at the same time):
```
node tools/build.cjs <id>                                                   # -> tmp/<id>/bundle.js + tmp/<id>/index.html
PAGE=tmp/<id>/index.html node tools/render.cjs sheet tmp/<id>/sheet.jpg <from> <to> <step> [cols]   # contact sheet, time+beat labels
PAGE=tmp/<id>/index.html node tools/render.cjs stills tmp/<id>/stills <t1> <t2> ...                 # full-res frames
PAGE=tmp/<id>/index.html node tools/render.cjs video tmp/<id>/clip.mp4 - <from> <to>                # silent preview clip
```
Times are GLOBAL seconds (beat n = n*0.4). LOOK at every sheet/still you render (Read the jpg) and judge it honestly.
`node tools/build.cjs` (no id) builds the whole film into bundle.js — only the integrator does that.
Rendering costs ~1–3 s per frame and only two agents run at a time: keep sheets ≤ 24 frames while iterating.
