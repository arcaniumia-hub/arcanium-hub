// Shared helpers for every scene: math/easing, beat grid, palette, fonts, 2D typography, photos, textures.
import * as THREE from 'three';

// ---------------------------------------------------------------- frame / beat grid
export const W = 1080, H = 1920, FPS = 30;
export const BPM = 150, BEAT = 60 / BPM;            // 0.4 s = 12 frames
export const BAR = BEAT * 4;                        // 1.6 s
export const b2s = b => b * BEAT;                   // beats -> seconds
export const s2b = s => s / BEAT;                   // seconds -> beats

// ---------------------------------------------------------------- math & easing
export const TAU = Math.PI * 2;
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const seg = (t, a, b) => clamp((t - a) / (b - a));          // 0..1 progress of t inside [a,b]
export const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
export const ein = x => { x = clamp(x); return x * x * x; };
export const eout = x => { x = clamp(x); return 1 - Math.pow(1 - x, 3); };
export const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
export const expoIn = x => { x = clamp(x); return x === 0 ? 0 : Math.pow(2, 10 * x - 10); };
export const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
export const expoIO = x => { x = clamp(x); return x === 0 ? 0 : x === 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2; };
export const back = (x, s = 1.7) => { x = clamp(x); const c3 = s + 1; return 1 + c3 * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); };
export const elastic = x => { x = clamp(x); if (x === 0 || x === 1) return x; return Math.pow(2, -10 * x) * Math.sin((x * 10 - .75) * (TAU / 3)) + 1; };
// decaying pulse: 1 at t==at, falls with time constant `decay` seconds; 0 before `at`
export const pulse = (t, at, decay = .12) => t < at ? 0 : Math.exp(-(t - at) / decay);
// strongest pulse among several hit times
export const pulses = (t, ats, decay = .12) => ats.reduce((m, a) => Math.max(m, pulse(t, a, decay)), 0);
// deterministic hash noise
export const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const rnd2 = (i, j) => rnd(i * 57.3 + j * 13.7);
export function noise1(x) { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(rnd(i), rnd(i + 1), u) * 2 - 1; }

// ---------------------------------------------------------------- palette
export const COL = {
  ink: '#050506', ink2: '#0b0b0d', gold: '#e6c896', gold2: '#b8925a', goldHi: '#f7e2b8', white: '#f6f3ec', muted: '#9a978f',
  // LUMARC brand (end card only)
  lmBg: '#0e0e14', lm1: '#4f6bff', lm2: '#6a55ff', lm3: '#9a4dff', lmWhite: '#faf9f6', lmMuted: '#a6a6b8',
};
// families registered by the engine (see engine.loadFonts)
export const FONT = {
  display: 'Unbounded',          // wide display: 300 500 700 800 900
  impact: 'Anton',               // condensed impact: 400
  brand: 'Outfit',               // LUMARC brand geometric: 100-900 (variable)
  ui: 'Inter',                   // UI: 100-900 (variable)
  mono: 'JetBrains Mono',        // HUD: 400 700
  serif: 'Instrument Serif',     // elegant: 400 normal + italic
  cheap: 'Comic Neue',           // BEFORE only: 700
};

// ---------------------------------------------------------------- 2D typography
// text(ctx, 'HELLO', x, y, { size, weight, family, color, align, baseline, alpha, spacing, blur, gold, shine, glow, glowColor, stroke, strokeColor, italic })
export function font(size, weight = 400, family = FONT.display, italic = false) { return `${italic ? 'italic ' : ''}${weight} ${size}px "${family}"`; }
export function goldGrad(ctx, x0, x1, shift = 0) {
  const g = ctx.createLinearGradient(x0, 0, x1, 0);
  g.addColorStop(0, COL.gold2); g.addColorStop(clamp(.35 + shift), COL.goldHi); g.addColorStop(clamp(.55 + shift), COL.gold); g.addColorStop(1, COL.gold2);
  return g;
}
export function brandGrad(ctx, x0, y0, x1, y1) { const g = ctx.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, COL.lm1); g.addColorStop(.45, COL.lm2); g.addColorStop(1, COL.lm3); return g; }
export function measure(ctx, s, size, weight = 400, family = FONT.display, spacing = 0, italic = false) {
  ctx.save(); ctx.font = font(size, weight, family, italic); ctx.letterSpacing = spacing + 'px';
  const m = ctx.measureText(s); ctx.restore(); return m.width;
}
// largest size (<= max) so that s fits in maxWidth
export function fitSize(ctx, s, maxWidth, max, weight = 400, family = FONT.display, spacing = 0) {
  const w = measure(ctx, s, 100, weight, family, spacing * 100 / max);
  return Math.min(max, 100 * maxWidth / w);
}
export function text(ctx, s, x, y, o = {}) {
  const { size = 60, weight = 400, family = FONT.display, color = COL.white, align = 'center', baseline = 'alphabetic', alpha = 1, spacing = 0,
    blur = 0, gold = false, shine = 0, glow = 0, glowColor = 'rgba(230,200,150,.6)', stroke = 0, strokeColor = COL.white, italic = false, fill = true } = o;
  if (alpha <= .003 || !s) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  ctx.font = font(size, weight, family, italic); ctx.textAlign = align; ctx.textBaseline = baseline; ctx.letterSpacing = spacing + 'px';
  if (blur > .3) ctx.filter = `blur(${blur}px)`;
  let paint = color;
  if (gold) { const tw = ctx.measureText(s).width; const x0 = align === 'center' ? x - tw / 2 : align === 'right' ? x - tw : x; paint = goldGrad(ctx, x0, x0 + tw, shine); }
  if (glow) { ctx.shadowColor = glowColor; ctx.shadowBlur = glow; }
  if (fill) { ctx.fillStyle = paint; ctx.fillText(s, x, y); }
  if (stroke) { ctx.shadowBlur = 0; ctx.lineWidth = stroke; ctx.strokeStyle = strokeColor; ctx.strokeText(s, x, y); }
  ctx.restore();
}
// text rising from behind an invisible mask line (k: 0..1)
export function maskText(ctx, s, x, y, k, o = {}) {
  const size = o.size || 60;
  ctx.save(); ctx.beginPath(); ctx.rect(0, y - size * 1.1, W, size * 1.45); ctx.clip();
  text(ctx, s, x, y + (1 - expoOut(k)) * size * 1.3, o); ctx.restore();
}
// per-letter animation: fn(i, n) -> { dx, dy, alpha, scale, rot, blur }   (letters laid out with `spacing`)
export function letters(ctx, s, cx, y, fn, o = {}) {
  const { size = 120, weight = 800, family = FONT.display, spacing = 0, align = 'center' } = o;
  ctx.save(); ctx.font = font(size, weight, family); ctx.letterSpacing = '0px';
  const ch = [...s], ws = ch.map(c => ctx.measureText(c).width); ctx.restore();
  const tw = ws.reduce((a, b) => a + b, 0) + spacing * (ch.length - 1);
  let x = align === 'center' ? cx - tw / 2 : align === 'right' ? cx - tw : cx;
  ch.forEach((c, i) => {
    const f = fn(i, ch.length) || {};
    const a = f.alpha === undefined ? 1 : f.alpha;
    if (a > .003 && c !== ' ') {
      ctx.save(); ctx.translate(x + ws[i] / 2 + (f.dx || 0), y + (f.dy || 0)); if (f.rot) ctx.rotate(f.rot); if (f.scale !== undefined) ctx.scale(f.scale, f.scale);
      text(ctx, c, 0, 0, { ...o, align: 'center', spacing: 0, alpha: a, blur: f.blur || 0, color: f.color || o.color });
      ctx.restore();
    }
    x += ws[i] + spacing;
  });
  return tw;
}

// ---------------------------------------------------------------- images
// soft elliptical alpha edge for photos shot on black (so no rectangle ever shows)
const FEATHER = new Map();
export function feathered(img, sx = 0, sy = 0, sw = img.width, sh = img.height, key = img.src + sx + ',' + sy, inner = .3) {
  if (FEATHER.has(key)) return FEATHER.get(key);
  const c = document.createElement('canvas'); c.width = sw; c.height = sh; const x = c.getContext('2d');
  x.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh);
  x.globalCompositeOperation = 'destination-in'; x.translate(sw / 2, sh / 2); x.scale(1, sh / sw);
  const g = x.createRadialGradient(0, 0, sw * inner, 0, 0, sw * .5); g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = g; x.fillRect(-sw / 2, -sw / 2, sw, sw);
  FEATHER.set(key, c); return c;
}
// photo on black, melted into the scene with 'lighten' (default) or normal compositing
export function drawPhoto(ctx, img, cx, cy, w, { alpha = 1, mode = 'lighten', feather = true, rot = 0 } = {}) {
  if (!img || alpha <= 0) return;
  const src = feather ? feathered(img) : img; const h = w * img.height / img.width;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.globalCompositeOperation = mode; ctx.translate(cx, cy); if (rot) ctx.rotate(rot);
  ctx.drawImage(src, -w / 2, -h / 2, w, h); ctx.restore();
}
// cover-fit an image inside a rect (with zoom and focal point)
export function drawCover(ctx, img, x, y, w, h, { zoom = 1, fx = .5, fy = .5, alpha = 1 } = {}) {
  if (!img) return;
  const s = Math.max(w / img.width, h / img.height) * zoom, iw = img.width * s, ih = img.height * s;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  ctx.drawImage(img, x + (w - iw) * fx, y + (h - ih) * fy, iw, ih); ctx.restore();
}
// orbit turntable: 40 photoreal frames (0..39, fractional = crossfade) from 4 sprite sheets of 5x2 cells of 520px
export function orbitFrame(ctx, sheets, f, cx, cy, size, { alpha = 1, mode = 'lighten' } = {}) {
  const draw = (i, a) => {
    i = clamp(Math.round(i), 0, 39); const sh = sheets[Math.floor(i / 10)], j = i % 10;
    if (!sh) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.globalCompositeOperation = mode;
    ctx.drawImage(feathered(sh, (j % 5) * 520, Math.floor(j / 5) * 520, 520, 520, 'orbit' + i), cx - size / 2, cy - size / 2, size, size); ctx.restore();
  };
  const f0 = Math.floor(clamp(f, 0, 39)), fr = clamp(f, 0, 39) - f0;
  draw(f0, alpha); if (fr > .01) draw(f0 + 1, alpha * fr);
}

// ---------------------------------------------------------------- textures for 3D
// canvas-texture text plane material: returns { texture, aspect } (texture is sRGB, premultiplied-friendly)
export function textTexture(s, { size = 200, weight = 900, family = FONT.display, color = COL.white, gold = false, pad = 40, spacing = 0 } = {}) {
  const c = document.createElement('canvas'); const x = c.getContext('2d');
  const w = Math.ceil(measure(x, s, size, weight, family, spacing) + pad * 2), h = Math.ceil(size * 1.4 + pad * 2);
  c.width = w; c.height = h;
  text(x, s, w / 2, h / 2, { size, weight, family, color, gold, spacing, baseline: 'middle' });
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return { texture: t, aspect: w / h, canvas: c };
}
export function canvasTexture(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
// round soft sprite for particles
let DOT = null;
export function dotTexture() {
  if (DOT) return DOT;
  DOT = canvasTexture(64, 64, (x, w) => { const g = x.createRadialGradient(32, 32, 0, 32, 32, 32); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.35, 'rgba(255,255,255,.55)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, w, w); });
  DOT.colorSpace = THREE.NoColorSpace; return DOT;
}
// material options for glowing ADDITIVE 3D stuff that must not occlude what is behind (particles, light streaks)
export const ADDITIVE = {
  transparent: true, depthWrite: false, blending: THREE.CustomBlending, blendEquation: THREE.AddEquation,
  blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.ZeroFactor, blendDstAlpha: THREE.OneFactor,
};

// ---------------------------------------------------------------- the film's recurring device: the ANC RING
// Hairline champagne-gold circle (5 px, glow 30) with a refraction band just outside it: the content already drawn on THIS
// 2D layer is redrawn at `scale` inside the annulus [r, r+band]. Optional mono HUD label riding its top.
// progress: 0..1 fraction of the circle drawn (from startAngle, clockwise). gradient: [c1,c2,c3] to tint it (LUMARC handoff).
export function ancRing(ctx, cx, cy, r, { alpha = 1, width = 5, glow = 30, color = COL.gold, refract = true, band = 38, scale = 1.04,
  progress = 1, startAngle = -Math.PI / 2, label = null, labelSize = 30, gradient = null, gradientMix = 1 } = {}) {
  if (alpha <= .003 || r <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  if (refract && progress > .999) {
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r + band, 0, TAU); ctx.arc(cx, cy, Math.max(0, r), 0, TAU, true); ctx.clip();
    ctx.translate(cx, cy); ctx.scale(scale, scale); ctx.translate(-cx, -cy); ctx.globalAlpha = alpha;
    ctx.drawImage(ctx.canvas, 0, 0); ctx.restore();
  }
  let stroke = color;
  if (gradient) {
    const g = ctx.createLinearGradient(cx - r, cy - r, cx + r, cy + r);
    g.addColorStop(0, gradient[0]); g.addColorStop(.5, gradient[1]); g.addColorStop(1, gradient[2]);
    stroke = g;
    if (gradientMix < 1) { ctx.save(); ctx.globalAlpha *= 1 - gradientMix; ctx.strokeStyle = color; ctx.lineWidth = width; ctx.shadowColor = 'rgba(230,200,150,.7)'; ctx.shadowBlur = glow;
      ctx.beginPath(); ctx.arc(cx, cy, r, startAngle, startAngle + TAU * clamp(progress)); ctx.stroke(); ctx.restore(); ctx.globalAlpha *= gradientMix; }
  }
  ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.lineCap = 'round';
  ctx.shadowColor = gradient ? 'rgba(122,85,255,.7)' : 'rgba(230,200,150,.7)'; ctx.shadowBlur = glow;
  ctx.beginPath(); ctx.arc(cx, cy, r, startAngle, startAngle + TAU * clamp(progress)); ctx.stroke();
  ctx.shadowBlur = 0;
  if (label) text(ctx, label, cx, cy - r - 22, { size: labelSize, weight: 400, family: FONT.mono, color: gradient ? COL.lmWhite : COL.gold, spacing: 4 });
  ctx.restore();
}

// ---------------------------------------------------------------- standard edit punches (globalStyle "POST LEVELS")
// DOWNBEAT PUNCH at time `at` (global seconds): flash + punch zoom + aberration + zoom blur + shake, all decaying.
export function downbeatPunch(fx, t, at, { flash = .5, flashColor = [1, 1, 1], flashFrames = 4, zoom = 1.12, rgb = .028, zoomBlur = .6, shake = .012, seed = 0 } = {}) {
  const d = t - at; if (d < 0 || d > 1) return;
  const fr = d * 30;
  const fl = flash * Math.max(0, 1 - fr / flashFrames);
  if (fl > fx.flash) { fx.flash = fl; fx.flashColor = flashColor; }
  fx.zoom *= 1 + (zoom - 1) * (1 - expoOut(clamp(fr / 8)));
  fx.rgb = Math.max(fx.rgb, .0015 + (rgb - .0015) * Math.max(0, 1 - fr / 10));
  fx.zoomBlur = Math.max(fx.zoomBlur, zoomBlur * Math.max(0, 1 - fr / 6));
  const sh = shake * Math.max(0, 1 - fr / 9);
  fx.shake = [fx.shake[0] + (rnd(Math.floor(t * 30) + seed) - .5) * 2 * sh, fx.shake[1] + (rnd(Math.floor(t * 30) + 77 + seed) - .5) * 2 * sh];
}
// KICK PUMP for groove sections: every time in `kicks` (global seconds) gives zoom 1.025 + rgb .0055 over 4 frames.
export function kickPump(fx, t, kicks, { zoom = 1.025, rgb = .0055 } = {}) {
  let k = 0; for (const a of kicks) { const fr = (t - a) * 30; if (fr >= 0 && fr < 4) k = Math.max(k, 1 - fr / 4); }
  fx.zoom *= 1 + (zoom - 1) * k; fx.rgb = Math.max(fx.rgb, .0015 + (rgb - .0015) * k);
}
