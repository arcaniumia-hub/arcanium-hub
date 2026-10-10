// s13-lumarc — LUMARC END CARD (b76-86)
//
// No cut from s12: the big LUMARC logo the particles assembled (800 px wide, centred (540,900)) GLIDES up to its end-card
// place (600 px, centred (540,620)) over b75.5-76.25 (eio; it starts in s12 on the riser and has cleared the headline row
// by b76.0) while the copy builds underneath it. The block (logo, headline, pill, tagline, handle) is centred around y 955.
// b75.5-78.0 THE RING BECOMES THE BUTTON: the ANC ring halo (lib ancRing while it is a circle) that breathed around the logo
//   in s12 drops as the logo rises, flattens into a capsule and squeezes into the pill's rounded rectangle; it locks on the
//   pill at b78.0 exactly as the pill pops out of it, and stays as a breathing gradient halo around the CTA.
// b76.0-77.5 headline word by word on 1/4 beats, on the storyboard grid (Want 76.0 · your 76.25 · product 76.5 · to 76.75 ·
//   look 77.0 · like 77.25 · this? 77.5), so the score's word ticks (b76.0/76.5/77.0/77.5) land on Want/product/look/this?.
//   Outfit 600, 82 px, rise 28 px, blur 8 -> 0; 'this?' lands in the brand gradient. b76.5-77.6 a ghost of the hero product
//   (a pure rim-light line drawing in the brand gradient, held down behind the text rows) fades in behind the copy;
//   b77.5 a bright rim-light sweep runs across it with 'this?' — the question points at it. Rim sweeps return with the pill
//   sheens (b80 / b82 / b84).
// b78.0 CTA pill pops (.6 -> 1.06 -> 1, 8 frames) out of the ring · b78.5 'Be seen.' · b79.0 'Be remembered.' · b79.25
//   handle · from b80 the pill breathes once per bar. Everything is legible from b79.75 (31.9 s) to the last frame (34.4 s).
//
// Shared with s12 (exported): logo placements, brandBackdrop(), dust, drawLogo(), haloRing(), logo flare, haloAt() ring journey, post levels.
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, back, rnd, text, measure, ancRing, COL, FONT } from '../lib.js';

// ------------------------------------------------------------------ shared brand system (used by s12 too)
export const LOGO_SPLIT = 233;                          // logo px: rings block | wordmark
export function place(cx, cy, w) { const s = w / 640, h = 218 * s; return { cx, cy, w, s, h, x: cx - w / 2, y: cy - h / 2 }; }
export const LOGO_A = place(540, 900, 800);              // s12: built and held big, centred
export const LOGO_B = place(540, 620, 600);              // s13: end-card place
// the glide starts in s12 on the riser (b75.5) and settles at b76.25, so the logo has cleared the headline row before
// 'Want' (b76.0) begins: the copy builds as it rises. Both scenes place the logo with logoAt(b).
export const GLIDE = [75.5, 76.25];
// logo placement at beat b
export const logoAt = b => { const k = eio(seg(b, GLIDE[0], GLIDE[1])); return place(540, lerp(LOGO_A.cy, LOGO_B.cy, k), lerp(LOGO_A.w, LOGO_B.w, k)); };
// logo px -> screen px (for a placement)
export const lp = (x, y, P = LOGO_A) => [P.x + x * P.s, P.y + y * P.s];
// the halo ring around the logo (s12 hold): centre / radius
export const HALO = { cx: 540, cy: 900, r: 480 };           // stroke + glow stay inside x 0-1080 even at endZoom max

const CACHE = {};
function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function logoParts(img) {
  if (CACHE.logo) return CACHE.logo;
  const rings = canvas(img.width, img.height), word = canvas(img.width, img.height);
  let x = rings.getContext('2d'); x.drawImage(img, 0, 0, LOGO_SPLIT, img.height, 0, 0, LOGO_SPLIT, img.height);
  x = word.getContext('2d'); x.drawImage(img, LOGO_SPLIT, 0, img.width - LOGO_SPLIT, img.height, LOGO_SPLIT, 0, img.width - LOGO_SPLIT, img.height);
  return (CACHE.logo = { rings, word });
}
// beat-locked logo glow: snaps to 1 on every beat, decays (shadowBlur 0 <-> 18)
export const beatGlow = b => Math.exp(-(b - Math.floor(b)) * BEAT / .17);
// bar breathing 0..1..0 from b73.5
export const barBreath = b => .5 - .5 * Math.cos(Math.max(0, b - 73.5) / 4 * TAU);

// bg: #0e0e14 + breathing radial brand glow centred on the logo. `b` = global beat.
export function brandBackdrop(E, b, { glow = 1, P = LOGO_A } = {}) {
  const bg = E.bg;
  bg.fillStyle = COL.lmBg; bg.fillRect(0, 0, W, H);
  if (glow > 0) {
    const br = 1 + .07 * barBreath(b) + .05 * beatGlow(b) * seg(b, 73.5, 74);
    const R = 820 * P.s / .9375 * .78;
    const g = bg.createRadialGradient(P.cx, P.cy, 0, P.cx, P.cy, R * (1 + .03 * barBreath(b)));
    const a = .14 * glow * br;
    g.addColorStop(0, `rgba(106,85,255,${a})`); g.addColorStop(.45, `rgba(106,85,255,${a * .42})`); g.addColorStop(1, 'rgba(106,85,255,0)');
    bg.fillStyle = g; bg.fillRect(0, 0, W, H);
    // faint second lobe low in the frame (depth under the copy)
    const g2 = bg.createRadialGradient(540, 1250, 0, 540, 1250, 700);
    g2.addColorStop(0, `rgba(79,107,255,${.045 * glow})`); g2.addColorStop(1, 'rgba(79,107,255,0)');
    bg.fillStyle = g2; bg.fillRect(0, 0, W, H);
  }
}
// fine luminous dust (replaces the old uniform bokeh): 90 motes rising slowly, twinkling, a few out-of-focus. k 0..1
export function drawDust(ctx, b, k) {
  if (k <= .003) return;
  const t = (b - 73.5) * BEAT;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 90; i++) {
    const s = i * 3.71 + 5, far = rnd(s + .3);
    const sp = 6 + 22 * far, span = H + 80;
    let y = rnd(s + .5) * span - sp * t; y = ((y % span) + span) % span - 40;
    const x = rnd(s) * W + 14 * Math.sin(t * .4 + i * 1.3);
    const tw = .55 + .45 * Math.sin(t * (1.2 + 1.6 * rnd(s + .8)) + i * 2.3);
    const r = .9 + 1.8 * far * far, a = (.10 + .30 * far) * tw * k;
    const c = rnd(s + .11); const col = c < .4 ? '120,140,255' : c < .8 ? '170,120,255' : '235,232,255';
    ctx.globalAlpha = a; ctx.fillStyle = `rgb(${col})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
    if (far > .9) { ctx.globalAlpha = a * .18; ctx.beginPath(); ctx.arc(x, y, r * 5, 0, TAU); ctx.fill(); }
  }
  ctx.restore();
}
// LUMARC logo (never recoloured): rings / wordmark alphas separately, breathing scale, violet glow (shadowBlur)
export function drawLogo(ctx, img, { P = LOGO_A, rings = 1, word = 1, scale = 1, glow = 0 } = {}) {
  if (!img) return;
  const L = logoParts(img);
  ctx.save(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  ctx.translate(P.cx, P.cy); ctx.scale(scale, scale); ctx.translate(-P.w / 2, -P.h / 2);
  if (glow > .3) { ctx.shadowColor = 'rgba(106,85,255,.75)'; ctx.shadowBlur = glow * P.s / .9375; }
  if (rings > .003) { ctx.globalAlpha = rings; ctx.drawImage(L.rings, 0, 0, P.w, P.h); }
  if (word > .003) { ctx.globalAlpha = word; ctx.drawImage(L.word, 0, 0, P.w, P.h); }
  ctx.restore();
}
// anamorphic flare on the logo's white star (where the two rings cross): thin horizontal streak + soft core, additive
export const STAR_PX = [95, 112];
export function logoFlare(ctx, k, { P = LOGO_A, scale = 1 } = {}) {
  if (k <= .003) return;
  const [sx, sy] = lp(STAR_PX[0], STAR_PX[1], P), x = P.cx + (sx - P.cx) * scale, y = P.cy + (sy - P.cy) * scale;
  const u = P.s / .9375, len = 170 * u;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const h = ctx.createLinearGradient(x - len, 0, x + len, 0);
  h.addColorStop(0, 'rgba(120,110,255,0)'); h.addColorStop(.42, `rgba(170,160,255,${.22 * k})`); h.addColorStop(.5, `rgba(255,255,255,${.45 * k})`);
  h.addColorStop(.58, `rgba(170,160,255,${.22 * k})`); h.addColorStop(1, 'rgba(120,110,255,0)');
  ctx.fillStyle = h; ctx.fillRect(x - len, y - 1.5 * u, len * 2, 3 * u);
  ctx.fillStyle = `rgba(150,140,255,${.08 * k})`; ctx.fillRect(x - len * .6, y - 5 * u, len * 1.2, 10 * u);
  const r = 46 * u, c = ctx.createRadialGradient(x, y, 0, x, y, r);
  c.addColorStop(0, `rgba(255,255,255,${.35 * k})`); c.addColorStop(.3, `rgba(160,140,255,${.16 * k})`); c.addColorStop(1, 'rgba(106,85,255,0)');
  ctx.fillStyle = c; ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
  ctx.restore();
}
// logo breathing (1 % per bar from b73.5) — identical in s12 and s13
export const logoBreath = b => 1 + .01 * barBreath(b);

// THE HALO RING: the film's ANC ring, in the LUMARC gradient. While it is a circle it IS lib ancRing (GUIDE rule: identical
// in every scene; refract off because the fg band under it is empty, exactly as s11 draws its last ring). To squeeze from a
// circle into the CTA pill it continues as a rounded rect with ancRing's exact stroke recipe (5 px, round cap, glow 30
// rgba(122,85,255,.7), diagonal lm1 -> lm2 -> lm3 gradient over its bounding box), so there is no visible switch.
const LM = [COL.lm1, COL.lm2, COL.lm3];
export function haloRing(ctx, { cx, cy, w, h, rr, alpha = 1, width = 5 }) {
  if (alpha <= .003) return;
  if (Math.abs(w - h) < .5 && rr >= w / 2 - .5) { ancRing(ctx, cx, cy, w / 2, { alpha, width, refract: false, gradient: LM }); return; }
  const g = ctx.createLinearGradient(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2);
  g.addColorStop(0, LM[0]); g.addColorStop(.5, LM[1]); g.addColorStop(1, LM[2]);
  ctx.save(); ctx.globalAlpha *= alpha; ctx.lineCap = 'round'; ctx.strokeStyle = g; ctx.lineWidth = width;
  ctx.shadowColor = 'rgba(122,85,255,.7)'; ctx.shadowBlur = 30;
  ctx.beginPath(); ctx.roundRect(cx - w / 2, cy - h / 2, w, h, Math.min(rr, w / 2, h / 2)); ctx.stroke();
  ctx.restore();
}
// halo around the logo during the s12 hold (b73.5-76): breathing on the bar, alpha .07
export function logoHalo(b) {
  const br = barBreath(b);
  const r = HALO.r * (1 + .018 * br) * (1 - .03 * eio(seg(b, 74, GLIDE[0])));  // gathers in a touch on the riser
  return { cx: HALO.cx, cy: HALO.cy, w: 2 * r, h: 2 * r, rr: r, alpha: .07 + .02 * br };
}
// the halo ring's whole journey (shared by s12 and s13): logo halo (circle) -> on the glide, while the logo rises, the ring
// drops to the pill line and flattens into a wide capsule (contrary motion; its top edge passes under the headline row
// before 'Want' appears) -> squeezes (ease-in = it SNAPS) onto the pill outline and locks on b78.0 as the pill pops.
const POP = 78.0;
const PILL = { cx: 540, cy: 1150, w: 660, h: 128, r: 64, pad: 110, label: 'DM us “VIDEO”' };
const MID = { w: 980, h: 240 };
export function haloAt(b) {
  const A = logoHalo(Math.min(b, GLIDE[0]));
  const k1 = eio(seg(b, GLIDE[0], GLIDE[1])), k2 = ein(seg(b, GLIDE[1], POP));
  if (k1 <= 0) return A;
  const HW = PILL.w + 34, HH = PILL.h + 34;
  const w = lerp(lerp(A.w, MID.w, k1), HW, k2), h = lerp(lerp(A.h, MID.h, k1), HH, k2);
  return { cx: 540, cy: lerp(A.cy, PILL.cy, k1), w, h, rr: Math.min(w, h) / 2, alpha: lerp(lerp(A.alpha, .12, k1), .55, k2) };
}

// post levels of the end card (s12 eases into these by b76)
export const END_FX = { bloom: .4, threshold: .93, knee: .05, vignette: .3, grain: .03, rgb: .001 };   // hard knee: logo/pill bloom, type stays crisp
// one continuous, barely-perceptible camera push from the finished logo (b73.5) to the last frame (shared with s12)
export const endZoom = b => 1 + .022 * eio(seg(b, 73.5, 86));

// ------------------------------------------------------------------ end card
const HS = 82;   // headline size
const HEAD = [
  { line: 'Want your product', y: 890, words: ['Want', 'your', 'product'], beats: [76.0, 76.25, 76.5] },
  { line: 'to look like this?', y: 985, words: ['to', 'look', 'like', 'this?'], beats: [76.75, 77.0, 77.25, 77.5] },
];
const TAG = { y: 1308, a: 'Be seen.', b: 'Be remembered.', ba: 78.5, bb: 79.0 };
const HANDLE = { y: 1382, s: '@lumarc_studio · slumarc.com', b: 79.25 };
const SHEENS = [80, 82, 84];
// ghost hero product (behind the copy): a pure rim-light line drawing in the brand gradient. `a` = peak alpha.
const GHOST = { cx: 540, cy: 1255, w: 900, a: .62 };
// text-safe rows (screen y bands) where the ghost is held down to 22 %: headline, tagline, handle
const SAFE = [[812, 1012], [1258, 1330], [1338, 1404]];

function roundRect(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function pillCanvas() {
  if (CACHE.pill) return CACHE.pill;
  const { w, h, r, pad } = PILL, c = canvas(w + pad * 2, h + pad * 2), x = c.getContext('2d');
  const gr = x.createLinearGradient(pad, 0, pad + w, 0); gr.addColorStop(0, COL.lm1); gr.addColorStop(.5, COL.lm2); gr.addColorStop(1, COL.lm3);
  x.save(); x.shadowColor = 'rgba(106,85,255,.6)'; x.shadowBlur = 40; x.fillStyle = gr; roundRect(x, pad, pad, w, h, r); x.fill(); x.restore();
  x.fillStyle = gr; roundRect(x, pad, pad, w, h, r); x.fill();
  x.save(); roundRect(x, pad, pad, w, h, r); x.clip();
  const hl = x.createLinearGradient(0, pad, 0, pad + h); hl.addColorStop(0, 'rgba(255,255,255,.20)'); hl.addColorStop(.48, 'rgba(255,255,255,.04)'); hl.addColorStop(.5, 'rgba(255,255,255,0)'); hl.addColorStop(1, 'rgba(20,10,60,.10)');
  x.fillStyle = hl; x.fillRect(pad, pad, w, h); x.restore();
  x.strokeStyle = 'rgba(255,255,255,.22)'; x.lineWidth = 1.5; roundRect(x, pad + .75, pad + .75, w - 1.5, h - 1.5, r - .75); x.stroke();
  text(x, PILL.label, pad + w / 2, pad + h / 2 + 2, { size: 54, weight: 700, family: FONT.brand, color: COL.lmWhite, baseline: 'middle', spacing: .5 });
  return (CACHE.pill = c);
}
// the hero photo turned into a rim-light ghost: only the gold trims (warm + bright) and the silhouette / part edges
// (gradient of the blurred luminance) survive, as lines of light in the LUMARC gradient; no grey body fill at all.
function ghostCanvas(img) {
  if (CACHE.ghost || !img) return CACHE.ghost;
  const w = img.width, h = img.height, c = canvas(w, h), x = c.getContext('2d');
  x.drawImage(img, 0, 0); const id = x.getImageData(0, 0, w, h), d = id.data, N = w * h;
  const sm = (v, a, b) => { v = clamp((v - a) / (b - a)); return v * v * (3 - 2 * v); };
  const L = new Float32Array(N), Lb = new Float32Array(N), tmp = new Float32Array(N);
  for (let i = 0; i < N; i++) L[i] = (.2126 * d[4 * i] + .7152 * d[4 * i + 1] + .0722 * d[4 * i + 2]) / 255;
  // separable box blur r 3 (kills the fabric / leather micro-texture so only part edges give gradient)
  const R = 3;
  for (let py = 0; py < h; py++) { let acc = 0; const o = py * w;
    for (let px = -R; px <= R; px++) acc += L[o + clamp(px, 0, w - 1)];
    for (let px = 0; px < w; px++) { tmp[o + px] = acc / (2 * R + 1); acc += L[o + Math.min(w - 1, px + R + 1)] - L[o + Math.max(0, px - R)]; } }
  for (let px = 0; px < w; px++) { let acc = 0;
    for (let py = -R; py <= R; py++) acc += tmp[clamp(py, 0, h - 1) * w + px];
    for (let py = 0; py < h; py++) { Lb[py * w + px] = acc / (2 * R + 1); acc += tmp[Math.min(h - 1, py + R + 1) * w + px] - tmp[Math.max(0, py - R) * w + px]; } }
  const L1 = [79, 107, 255], L2 = [120, 92, 255], L3 = [170, 90, 255];
  for (let py = 0; py < h; py++) for (let px = 0; px < w; px++) {
    const i = py * w + px, q = 4 * i, r = d[q], bl = d[q + 2], l = L[i];
    const xm = Math.max(0, px - 1), xp = Math.min(w - 1, px + 1), ym = Math.max(0, py - 1) * w, yp = Math.min(h - 1, py + 1) * w;
    const gx = Lb[py * w + xp] - Lb[py * w + xm], gy = Lb[yp + px] - Lb[ym + px];
    const edge = sm(Math.hypot(gx, gy), .025, .09) * sm(Math.max(Lb[i], l), .1, .3);
    const gold = sm((r - bl) / 255, .16, .3) * sm(l, .42, .8);
    let v = Math.max(gold, .7 * edge);
    const ex = (px / w - .5) / .58, ey = (py / h - .5) / .58; v *= clamp(1.4 - 1.1 * Math.hypot(ex, ey));
    const sx = px / w, base = sx < .5 ? L1.map((a, k) => lerp(a, L2[k], sx * 2)) : L2.map((a, k) => lerp(a, L3[k], sx * 2 - 1));
    const wm = .75 * gold * sm(l, .7, .95);                       // the hottest trims burn to violet-white
    d[q] = lerp(base[0], 236, wm); d[q + 1] = lerp(base[1], 232, wm); d[q + 2] = lerp(base[2], 255, wm); d[q + 3] = 255 * v;
  }
  x.putImageData(id, 0, 0);
  CACHE.sweep = canvas(w, h);
  CACHE.gl = canvas(W, H);
  return (CACHE.ghost = c);
}
function drawGhost(ctx, b, a, sweeps) {
  const g = CACHE.ghost; if (!g || a <= .003) return;
  const t = (b - 76) * BEAT;
  const sc = GHOST.w / g.width * (1 + .012 * t / 4), w = g.width * sc, h = g.height * sc;
  const x = GHOST.cx - w / 2, y = GHOST.cy - h / 2 - 3 * t;          // slow rise + scale: parallax against the push-in
  // compose on a screen-size layer, then carve the text-safe rows out of it before adding it to the backdrop
  const L = CACHE.gl, lx = L.getContext('2d');
  lx.globalCompositeOperation = 'source-over'; lx.globalAlpha = 1; lx.clearRect(0, 0, W, H);
  lx.globalAlpha = a; lx.drawImage(g, x, y, w, h);
  for (const [sb, amt, dur] of sweeps) {                            // rim-light sweeps through a moving diagonal band
    const k = seg(b, sb, sb + dur); if (k <= 0 || k >= 1) continue;
    const c = CACHE.sweep, cx = c.getContext('2d');
    cx.globalCompositeOperation = 'source-over'; cx.clearRect(0, 0, c.width, c.height); cx.drawImage(g, 0, 0);
    cx.globalCompositeOperation = 'destination-in';
    cx.save(); cx.translate(lerp(-300, c.width + 300, eio(k)), c.height / 2); cx.rotate(.5);
    const gr = cx.createLinearGradient(-170, 0, 170, 0);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(.5, 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
    cx.fillStyle = gr; cx.fillRect(-170, -1200, 340, 2400); cx.restore();
    lx.globalCompositeOperation = 'lighter'; lx.globalAlpha = Math.min(1, amt * Math.sin(Math.PI * k)); lx.drawImage(c, x, y, w, h);
  }
  lx.globalCompositeOperation = 'destination-out'; lx.globalAlpha = 1;
  const m = lx.createLinearGradient(0, 0, 0, H), F = 26;
  for (const [y0, y1] of SAFE) {
    m.addColorStop((y0 - F) / H, 'rgba(0,0,0,0)'); m.addColorStop(y0 / H, 'rgba(0,0,0,.78)');
    m.addColorStop(y1 / H, 'rgba(0,0,0,.78)'); m.addColorStop((y1 + F) / H, 'rgba(0,0,0,0)');
  }
  lx.fillStyle = m; lx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(L, 0, 0); ctx.restore();
}
function lineLayout(ctx, s, words, size, weight) {
  const tw = measure(ctx, s, size, weight, FONT.brand); const x0 = 540 - tw / 2; const out = []; let pre = '';
  for (const w of words) { out.push(x0 + measure(ctx, pre, size, weight, FONT.brand)); pre += w + ' '; }
  return out;
}
export default {
  id: 's13-lumarc', start: 76, end: 86, cutIn: 'none',
  init(E) { if (E.img.logo) logoParts(E.img.logo); pillCanvas(); ghostCanvas(E.img.hero); },
  draw(E, lt, t) {
    const b = t / BEAT, fg = E.fg, fx = E.fx;
    if (!CACHE.layout) {
      CACHE.layout = HEAD.map(L => lineLayout(fg, L.line, L.words, HS, 600));
      const tw = measure(fg, TAG.a + ' ' + TAG.b, 46, 400, FONT.brand);
      CACHE.tag = [540 - tw / 2, 540 - tw / 2 + measure(fg, TAG.a + ' ', 46, 400, FONT.brand)];
    }
    const P = logoAt(b);
    brandBackdrop(E, b, { P });
    drawDust(E.bg, b, 1);

    // ghost hero product behind the copy: fades in with the second line, rim sweep on 'this?' and with every pill sheen
    ghostCanvas(E.img.hero);
    const ga = GHOST.a * eio(seg(b, 76.5, 77.6)) * (1 + .12 * Math.sin((b - 78) / 4 * TAU));
    drawGhost(E.bg, b, ga, [[77.5, .9, 1.1], ...SHEENS.map(s => [s - .15, .22, 1.0])]);

    // logo: glides up (b75.5-76.25, started in s12), breathing + beat glow (kicks on b76/78/80/82/84 a touch stronger)
    const kick = [76, 78, 80, 82, 84].reduce((m, k) => Math.max(m, b >= k ? Math.exp(-(b - k) * BEAT / .25) : 0), 0);
    const gp = Math.max(beatGlow(b), kick);
    drawLogo(fg, E.img.logo, { P, scale: logoBreath(b), glow: 18 * gp });
    logoFlare(fg, .3 + .7 * gp, { P, scale: logoBreath(b) });

    // the ring travels down and squeezes into the pill outline; after the pop it stays as the pill's breathing halo
    let pillSc = 1;
    const pk = seg(b, POP, POP + 8 / 12);
    if (pk > 0) { pillSc = lerp(.6, 1, back(pk, 2.5)); if (b > 80) pillSc *= 1 + .0125 * (1 - Math.cos((b - 80) / 4 * TAU)); }
    if (b < POP) haloRing(fg, haloAt(b));
    else {
      const lock = Math.exp(-(b - POP) * BEAT / .1);                 // contact flash on the lock
      const sc = b > 80 ? 1 + .0125 * (1 - Math.cos((b - 80) / 4 * TAU)) : 1;
      const ex = 34 + 26 * eout(seg(b, POP, POP + 1.5));              // the halo eases a little off the pill
      const br = .5 + .5 * Math.cos((b - 80) / 4 * TAU);
      haloRing(fg, { cx: PILL.cx, cy: PILL.cy, w: (PILL.w + ex) * sc, h: (PILL.h + ex) * sc, rr: (PILL.h + ex) * sc / 2,
        alpha: lerp(.55, .2 + .06 * br, eout(seg(b, POP, POP + 1.5))) + .45 * lock, width: 5 - 2 * eout(seg(b, POP, POP + 1.5)) });
    }

    // headline: word by word, rising 28 px, blur 8 -> 0, 6 frames; 'this?' in the brand gradient
    HEAD.forEach((L, li) => L.words.forEach((w, wi) => {
      const k = seg(b, L.beats[wi], L.beats[wi] + .5); if (k <= 0) return;
      const x = CACHE.layout[li][wi];
      let color = COL.lmWhite;
      if (w === 'this?') {
        const tw = measure(fg, w, HS, 600, FONT.brand), g = fg.createLinearGradient(x, 0, x + tw, 0);
        g.addColorStop(0, '#8fa0ff'); g.addColorStop(.5, '#a08cff'); g.addColorStop(1, '#c28cff'); color = g;
      }
      text(fg, w, x, L.y + 28 * (1 - expoOut(k)), { size: HS, weight: 600, family: FONT.brand, color, align: 'left',
        alpha: eout(k * 1.15), blur: k < 1 ? 8 * (1 - eout(k)) : 0, glow: w === 'this?' ? 14 * (1 - .6 * eout(seg(b, 77.5, 78.5))) : 0,
        glowColor: 'rgba(130,100,255,.55)' });
    }));

    // CTA pill (pops out of the ring at b78.0)
    if (pk > 0) {
      const pc = pillCanvas();
      fg.save(); fg.translate(PILL.cx, PILL.cy); fg.scale(pillSc, pillSc); fg.globalAlpha = clamp(pk * 4);
      fg.drawImage(pc, -pc.width / 2, -pc.height / 2);
      const fr = (b - POP) * 12;
      if (fr < 3) {
        roundRect(fg, -PILL.w / 2, -PILL.h / 2, PILL.w, PILL.h, PILL.r);
        fg.globalCompositeOperation = 'lighter'; fg.fillStyle = `rgba(255,255,255,${.28 * (1 - fr / 3)})`; fg.fill();
        if (fr < 1.5) {
          fg.save(); fg.globalCompositeOperation = 'lighter'; fg.scale(1, .42);
          const g = fg.createRadialGradient(0, 0, 0, 0, 0, 520); g.addColorStop(0, 'rgba(106,85,255,.16)'); g.addColorStop(1, 'rgba(106,85,255,0)');
          fg.fillStyle = g; fg.fillRect(-520, -520, 1040, 1040); fg.restore();
        }
      }
      for (const sb of SHEENS) {
        const sk = seg(b, sb, sb + 8 / 12); if (sk <= 0 || sk >= 1) continue;
        fg.save(); fg.globalCompositeOperation = 'source-over'; fg.globalAlpha = 1;
        roundRect(fg, -PILL.w / 2, -PILL.h / 2, PILL.w, PILL.h, PILL.r); fg.clip();
        const cx = lerp(-PILL.w / 2 - 140, PILL.w / 2 + 140, eio(sk));
        fg.translate(cx, 0); fg.rotate(.42);
        const g = fg.createLinearGradient(-40, 0, 40, 0);
        g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(.5, 'rgba(255,255,255,.3)'); g.addColorStop(1, 'rgba(255,255,255,0)');
        fg.fillStyle = g; fg.fillRect(-40, -260, 80, 520);
        fg.fillStyle = 'rgba(255,255,255,.12)'; fg.fillRect(54, -260, 10, 520);
        fg.restore();
      }
      fg.restore();
      fx.zoom *= 1 + .015 * (1 - expoOut(clamp(fr / 8)));
    }

    // 'Be seen. Be remembered.'
    const ta = seg(b, TAG.ba, TAG.ba + .5), tb = seg(b, TAG.bb, TAG.bb + .5);
    text(fg, TAG.a, CACHE.tag[0], TAG.y + 16 * (1 - expoOut(ta)), { size: 46, weight: 400, family: FONT.brand, color: '#b2b2c4', align: 'left', alpha: eout(ta) });
    text(fg, TAG.b, CACHE.tag[1], TAG.y + 16 * (1 - expoOut(tb)), { size: 46, weight: 400, family: FONT.brand, color: '#b2b2c4', align: 'left', alpha: eout(tb) });
    // handle
    const hk = seg(b, HANDLE.b, HANDLE.b + .5);
    text(fg, HANDLE.s, 540, HANDLE.y + 10 * (1 - expoOut(hk)), { size: 40, weight: 500, family: FONT.brand, color: '#c4c4d4', alpha: eout(hk), spacing: .5 });

    // post: clean brand grade, the slow push-in continues from s12 (never static)
    fx.bloom = END_FX.bloom; fx.bloomThreshold = END_FX.threshold; fx.bloomKnee = END_FX.knee; fx.vignette = END_FX.vignette; fx.grain = END_FX.grain; fx.rgb = END_FX.rgb;
    fx.zoom *= endZoom(b);
  },
};
