// Entry: builds the engine, loads assets, runs the scene timeline. window.renderAt(t) renders one deterministic frame.
import { createEngine } from './engine.js';
import { b2s, FPS, clamp } from './lib.js';
import { IMAGES, FONTS } from './assets.js';
import SCENES from './scenes/index.js';

const E = createEngine();
SCENES.forEach(s => { s.t0 = b2s(s.start); s.t1 = b2s(s.end); });
const DUR = SCENES[SCENES.length - 1].t1;
const sceneAt = t => SCENES.find(s => t >= s.t0 && t < s.t1) || SCENES[SCENES.length - 1];

// global edit layer: a short punch on every hard cut unless the incoming scene opts out (cutIn: 'none')
function editFX(t, s) {
  const d = t - s.t0;
  if (s === SCENES[0] || s.cutIn === 'none' || d > .25) return;
  const k = Math.exp(-d / .07);
  E.fx.zoom *= 1 + .045 * k; E.fx.rgb += .008 * k;
}
function drawFrame(t) {
  const s = sceneAt(t);
  s.draw(E, t - s.t0, t, clamp((t - s.t0) / (s.t1 - s.t0)));
  editFX(t, s);
}
function renderAt(t) {
  t = clamp(t, 0, DUR - 1e-4);
  const s = sceneAt(t);
  const mb = s.motionBlur ? s.motionBlur(t - s.t0, t) : 1;
  E.renderFrame(t, drawFrame, mb);
}

window.E = E; window.DUR = DUR; window.FPS = FPS;
window.SCENE_LIST = SCENES.map(s => ({ id: s.id, start: s.start, end: s.end, t0: s.t0, t1: s.t1 }));
window.ready = (async () => {
  await E.loadFonts(FONTS);
  await E.loadImages(IMAGES);
  for (const s of SCENES) if (s.init) await s.init(E);
  window.renderAt = renderAt;
  return true;
})();

// live playback (tools/render.cjs sets window.__RENDER before load)
window.ready.then(() => {
  document.body.appendChild(E.canvas);
  if (window.__RENDER) return;
  const cv = E.canvas, au = document.getElementById('music'), btn = document.getElementById('play');
  const fit = () => { const s = Math.min(innerWidth / cv.width, innerHeight / cv.height); cv.style.width = cv.width * s + 'px'; cv.style.height = cv.height * s + 'px'; };
  fit(); addEventListener('resize', fit);
  let t0 = null;
  const loop = now => {
    if (t0 === null) t0 = now;
    const t = au && !au.paused ? au.currentTime : ((now - t0) / 1000) % DUR;
    renderAt(Math.min(t, DUR - .001)); requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
  if (btn) btn.onclick = () => { btn.style.display = 'none'; if (au) { au.currentTime = 0; au.loop = true; au.play().catch(() => {}); } };
});
