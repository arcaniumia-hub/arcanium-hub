// s05-grid — DROP 1 (b24-28): the frame multiplies 1 -> 2 -> 4 -> 8 -> 16 -> 32 -> 64 -> 128 cells of photoreal orbit
// frames. Every split is a "mitosis": the children of a cell start as the parent image and separate into their own
// cells over 5 frames, while new gold gutters grow from the centre. 128 cells = a stadium wave of rotation with gold
// tiles spelling S-I-L-E-N-C-E; then a Droste dive into the target cell (orbit frame 39, front view), hand-off to s06.
//
// Layers: bg2d all cells (no 3D at all) · fg2d gold gutters + lock-on frame. Both share the dive transform.
// Sharpness: every orbit frame is pre-cut from its sprite sheet into a mip chain (520 sharpened / 260 / 130 / 65,
// each unsharp-masked) so every cell is drawn at ~1:1 from the right level (no aliasing at 128 cells, no mush at 1).
import { W, H, BEAT, clamp, lerp, seg, eout, ein, expoOut, rnd, text, font, measure, fitSize, goldGrad, kickPump,
  COL, FONT } from '../lib.js';

const B0 = 24;                                            // scene start (absolute beat)
const SPLIT = [24, 24.5, 25, 25.5, 26, 26.5, 26.75, 27];  // layout steps (absolute beats)
const DIMS = [[1, 1], [1, 2], [2, 2], [2, 4], [4, 4], [4, 8], [8, 8], [8, 16]];
const TARGET = { c: 4, r: 8 };                            // in the 8x16 grid: centre (607.5, 1020)
const TX = 607.5, TY = 1020;
const DIVE_F0 = 330 - 288;                                // local frame of b27.5
const MITOSIS = 5;
const DIVE_S = 16.8;                                       // the target cell (135x120) ends at 2160x1920: it IS the frame
const DIVE_IN = 960 / .64 / DIVE_S / (120 * 1.06);        // inner contra-zoom so the product is ~960 px wide at f335                                        // frames for children to separate
const LETTERS = 'SILENCE';
const MINUS = '\u2212';
const TW = '#ebe6dc';                                     // warm white kept just under the bloom threshold

// ------------------------------------------------------------------ orbit frame mip chain
let MIP = null;                    // MIP[level][frame] -> canvas ; sizes 520, 260, 130, 65
const SIZES = [520, 260, 130, 65];
let SCR = null;                    // scratch canvases for crossfades (per level)

function sharpen(c, amount, radius) {
  const w = c.width, h = c.height, x = c.getContext('2d', { willReadFrequently: true });
  const b = document.createElement('canvas'); b.width = w; b.height = h; const bx = b.getContext('2d');
  bx.filter = `blur(${radius}px)`; bx.drawImage(c, 0, 0); bx.filter = 'none';
  const o = x.getImageData(0, 0, w, h), bl = bx.getImageData(0, 0, w, h).data, d = o.data;
  for (let i = 0; i < d.length; i += 4) {
    d[i] = d[i] + amount * (d[i] - bl[i]); d[i + 1] = d[i + 1] + amount * (d[i + 1] - bl[i + 1]); d[i + 2] = d[i + 2] + amount * (d[i + 2] - bl[i + 2]);
  }
  x.putImageData(o, 0, 0);
}
function buildMips(E) {
  const sheets = [E.img.orbit0, E.img.orbit1, E.img.orbit2, E.img.orbit3];
  MIP = SIZES.map(() => []);
  for (let f = 0; f < 40; f++) {
    const sh = sheets[Math.floor(f / 10)], j = f % 10, sx = (j % 5) * 520, sy = Math.floor(j / 5) * 520;
    let prev = null;
    SIZES.forEach((s, lv) => {
      const c = document.createElement('canvas'); c.width = c.height = s; const x = c.getContext('2d', { willReadFrequently: true });
      x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
      // 1 px inset on the source so no neighbouring sprite cell bleeds in
      if (lv === 0) x.drawImage(sh, sx + 1, sy + 1, 518, 518, 0, 0, s, s); else x.drawImage(prev, 0, 0, s, s);
      prev = c;
      const keep = document.createElement('canvas'); keep.width = keep.height = s; keep.getContext('2d').drawImage(c, 0, 0);
      sharpen(keep, [.7, .45, .55, .4][lv], [1.4, 1, .8, .6][lv]);
      MIP[lv][f] = keep;
    });
  }
  SCR = SIZES.map(s => { const c = document.createElement('canvas'); c.width = c.height = s; return c; });
}
const reflect = f => { f = ((f % 78) + 78) % 78; return f <= 39 ? f : 78 - f; };   // ping-pong into 0..39

// draw orbit frame f (fractional: crossfade) centred at (cx,cy), `size` px in canvas units, `scale` = canvas->screen
function sprite(ctx, f, cx, cy, size, scale, { alpha = 1, fade = true } = {}) {
  const px = size * scale; let lv = 0;
  for (let i = SIZES.length - 1; i >= 0; i--) if (SIZES[i] >= px * .92) { lv = i; break; }
  f = clamp(f, 0, 39);
  const f0 = Math.floor(f), fr = f - f0;
  let src = MIP[lv][f0];
  if (fade && fr > .08 && f0 < 39) {
    const s = SCR[lv], x = s.getContext('2d'); x.globalAlpha = 1; x.globalCompositeOperation = 'copy'; x.drawImage(MIP[lv][f0], 0, 0);
    x.globalCompositeOperation = 'source-over'; x.globalAlpha = fr; x.drawImage(MIP[lv][f0 + 1], 0, 0); x.globalAlpha = 1; src = s;
  } else if (fr > .5 && f0 < 39) src = MIP[lv][f0 + 1];
  ctx.save(); ctx.globalAlpha *= alpha; ctx.globalCompositeOperation = 'lighten';
  ctx.drawImage(src, cx - size / 2, cy - size / 2, size, size); ctx.restore();
}

// ------------------------------------------------------------------ typography helpers
// text vertically centred on its cap height
function capText(ctx, s, cx, cy, o) {
  ctx.save(); ctx.font = font(o.size, o.weight || 400, o.family || FONT.impact); ctx.letterSpacing = (o.spacing || 0) + 'px';
  const m = ctx.measureText(s); ctx.restore();
  const asc = m.actualBoundingBoxAscent, dsc = m.actualBoundingBoxDescent;
  text(ctx, s, cx, cy + (asc - dsc) / 2, o);
}

// ------------------------------------------------------------------ layout model
const cellRect = (st, c, r) => { const [nc, nr] = DIMS[st]; const w = W / nc, h = H / nr; return { x: c * w, y: r * h, w, h, cx: c * w + w / 2, cy: r * h + h / 2 }; };
// global ping-pong: frame 0 on even beats, 39 on odd beats (cosine ease = the product nods to the groove)
const P = b => 19.5 - 19.5 * Math.cos(Math.PI * (b - B0));

// content of a cell at a layout step: { kind, ... }
function content(st, c, r, b) {
  const R = cellRect(st, c, r);
  const spr = (frame, size, extra = {}) => ({ kind: 'sprite', frame, size, cx: R.cx, cy: R.cy, ...extra });
  const fitSq = R.w / R.h > 1 ? R.h * 1.06 : R.w * 1.22;           // sprite size that frames the product in this cell
  switch (st) {
    case 0: return spr(P(b) * .55, 1080, { ghost: true });
    case 1: return r === 0 ? spr(reflect(P(b)), 940, { cx: 540, cy: 480 }) : { kind: 'word' };
    case 2: return c === 0 && r === 0 ? spr(reflect(P(b) + 4), 600) : c === 1 && r === 0 ? { kind: 'one' } : c === 0 ? { kind: 'macro' } : { kind: 'tile', s: MINUS + '42 dB', gold: true };
    case 3: {
      if (c === 0) return r === 2 ? { kind: 'macro' } : spr(reflect(P(b) + r * 5), fitSq);
      return { kind: 'tile', s: ['40 H', '360°', '250 G', 'ANC-H2'][r], gold: r % 2 === 0 };
    }
    case 4: case 5: case 6: {
      // diagonal rotation wave in screen space (2.5 frames per 270x480 block), continuous across the splits
      const off = 2.5 * (R.cx / 270 + R.cy / 480) - 2.5;
      return spr(reflect(P(b) + off), fitSq);
    }
    case 7: {
      const i = r * 8 + c;
      if (c === TARGET.c && r === TARGET.r) return spr(39, fitSq, { target: true });
      for (let k = 0; k < 7; k++) if (c === k && r === 2 * k + 1) return { kind: 'letter', s: LETTERS[k], k };
      // STADIUM WAVE sweeping bottom-left -> top-right (phase lag grows with col and with distance from the bottom row)
      const ph = 2 * Math.PI * 1.25 * (b - 27) - .55 * (c + .6 * (15 - r));
      return spr(20 + 19 * Math.sin(ph), fitSq, { gold: i % 7 === 0, crest: Math.max(0, Math.sin(ph)) });
    }
  }
}

// ------------------------------------------------------------------ cell painters
function paintCell(E, ctx, st, c, r, b, d, scale, parent) {
  const R = cellRect(st, c, r), C = content(st, c, r, b);
  ctx.save(); ctx.beginPath(); ctx.rect(R.x, R.y, R.w, R.h); ctx.clip();
  ctx.fillStyle = COL.ink; ctx.fillRect(R.x, R.y, R.w, R.h);
  const life = d;                                         // frames since this layout appeared
  const nb = b - SPLIT[st];                               // beats since this layout appeared

  if (C.kind === 'sprite') {
    let { cx, cy, size, frame } = C;
    if (C.crest) size *= 1 + .1 * C.crest * C.crest;     // the stadium "stands up"
    // mitosis: start from the parent's image (same place, same size) and separate
    if (parent && parent.kind === 'sprite' && life < MITOSIS + 1) {
      const e = expoOut(clamp(life / MITOSIS));
      cx = lerp(parent.cx, cx, e); cy = lerp(parent.cy, cy, e); size = lerp(parent.size, size, e); frame = lerp(parent.frame, frame, e);
    } else if (parent && life < 4) {
      // the parent was a type tile / photo: the product pops in (cut on the beat, settles in 4 frames)
      size *= 1 + .22 * (1 - expoOut(clamp(life / 4)));
    }
    if (C.ghost) {
      // ghost 'SILENCE' running vertically behind the product
      ctx.save(); ctx.translate(540, 960); ctx.rotate(-Math.PI / 2);
      const gs = fitSize(ctx, 'SILENCE', 1760, 300, 900, FONT.display);
      capText(ctx, 'SILENCE', -40 + 60 * nb, 0, { size: gs, weight: 900, family: FONT.display, color: COL.white, alpha: .08 });
      ctx.restore();
      size *= 1 + .05 * nb;                               // slow push
    }
    // contra-zoom inside the target during the dive: the product lands ~960 px wide at f335 while the grid rushes out
    if (C.target && b >= 27.5) { const k = seg(b, 27.5, 27.5 + 5 / 12); size *= lerp(1, DIVE_IN, k * k); }
    sprite(ctx, frame, cx, cy, size, scale, { fade: size * scale > 300 });
    if (C.gold) {
      ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = COL.gold; ctx.fillRect(R.x, R.y, R.w, R.h);
      ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = '#3a2a14'; ctx.fillRect(R.x, R.y, R.w, R.h);
      ctx.globalCompositeOperation = 'source-over';
    }
    if (C.crest) { ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = `rgba(230,200,150,${.2 * Math.pow(C.crest, 5)})`; ctx.fillRect(R.x, R.y, R.w, R.h); ctx.globalCompositeOperation = 'source-over'; }
  } else if (C.kind === 'word') {
    // 'SILENCE' rising out of the gutter, tracking in
    const k = expoOut(clamp(life / 5));
    const sp = lerp(70, 6, eout(clamp(life / 14)));
    const sz = fitSize(ctx, 'SILENCE', 960, 220, 900, FONT.display, sp);
    ctx.save(); ctx.beginPath(); ctx.rect(0, 1500 - sz * 1.05, W, sz * 1.3); ctx.clip();
    text(ctx, 'SILENCE', 540 + sp * .5, 1500 + (1 - k) * sz * 1.2, { size: sz, weight: 900, family: FONT.display, color: TW, spacing: sp });
    ctx.restore();
    text(ctx, 'SILENCE ONE  ·  ACTIVE NOISE CANCELLING', 540, 1600, { size: 30, weight: 400, family: FONT.mono, color: COL.gold, spacing: 4, alpha: seg(life, 1, 4) * .9 });
  } else if (C.kind === 'one') {
    const k = expoOut(clamp(life / 4));
    ctx.save(); ctx.translate(R.cx, R.cy); const s = lerp(1.35, 1, k) * (1 + .03 * nb); ctx.scale(s, s);
    capText(ctx, 'ONE', 0, 0, { size: 330, family: FONT.impact, gold: true, shine: -.3 + .6 * seg(life, 0, 24) });
    ctx.restore();
  } else if (C.kind === 'macro') {
    const k = expoOut(clamp(life / 5));
    drawCoverC(ctx, E.img.macro, R, { zoom: lerp(1.5, 1.18, k) + .08 * nb, fx: .72, fy: .45 });
  } else if (C.kind === 'tile') {
    const k = expoOut(clamp(life / 4));
    if (C.gold) { ctx.fillStyle = tileGold(ctx, R); ctx.fillRect(R.x, R.y, R.w, R.h); }
    const sz = Math.min(150, fitSize(ctx, C.s, R.w * .82, 150, 400, FONT.impact));
    ctx.save(); ctx.translate(R.cx, R.cy); const s = lerp(1.3, 1, k) * (1 + .03 * nb); ctx.scale(s, s);
    capText(ctx, C.s, 0, 0, { size: sz, family: FONT.impact, color: C.gold ? COL.ink : TW });
    ctx.restore();
    if (life < 1 && C.gold) { ctx.fillStyle = 'rgba(255,240,210,.35)'; ctx.fillRect(R.x, R.y, R.w, R.h); }
  } else if (C.kind === 'letter') {
    // the diagonal letters slam in one per frame from the top
    const on = life - C.k;
    if (on >= 0) {
      ctx.fillStyle = tileGold(ctx, R); ctx.fillRect(R.x, R.y, R.w, R.h);
      const k = expoOut(clamp(on / 3));
      ctx.save(); ctx.translate(R.cx, R.cy); const s = lerp(1.6, 1, k); ctx.scale(s, s);
      capText(ctx, C.s, 0, 0, { size: 96, family: FONT.impact, color: COL.ink });
      ctx.restore();
      if (on < 1) { ctx.fillStyle = 'rgba(255,244,220,.4)'; ctx.fillRect(R.x, R.y, R.w, R.h); }
    } else {
      // before its slam it still shows the wave
      const ph = 2 * Math.PI * 1.25 * (b - 27) - .55 * (c + .6 * (15 - r));
      sprite(ctx, 20 + 19 * Math.sin(ph), R.cx, R.cy, R.h * 1.06, scale, { fade: false });
    }
  }
  ctx.restore();
  return C;
}
function tileGold(ctx, R) {
  const g = ctx.createLinearGradient(R.x, R.y, R.x + R.w, R.y + R.h);
  g.addColorStop(0, '#ebd2a3'); g.addColorStop(.45, COL.gold); g.addColorStop(1, '#c9a46c'); return g;
}
function drawCoverC(ctx, img, R, { zoom = 1, fx = .5, fy = .5 } = {}) {
  if (!img) return;
  const s = Math.max(R.w / img.width, R.h / img.height) * zoom, iw = img.width * s, ih = img.height * s;
  ctx.drawImage(img, R.x + (R.w - iw) * fx, R.y + (R.h - ih) * fy, iw, ih);
}

// ------------------------------------------------------------------ gutters
// lines of a layout: [{v:true,x} | {v:false,y}]
function lines(st) { const [nc, nr] = DIMS[st], L = []; for (let j = 1; j < nc; j++) L.push({ v: true, p: W * j / nc }); for (let i = 1; i < nr; i++) L.push({ v: false, p: H * i / nr }); return L; }
const key = l => (l.v ? 'v' : 'h') + Math.round(l.p * 4);
const BORN = (() => {          // step at which each line first appears
  const m = new Map();
  DIMS.forEach((_, st) => lines(st).forEach(l => { if (!m.has(key(l))) m.set(key(l), st); }));
  return m;
})();
function gutters(ctx, st, lf, scale, fade = 1) {
  if (fade <= 0) return;
  const lw = 4 / Math.pow(scale, .55);
  for (const l of lines(st)) {
    const born = BORN.get(key(l)), d = lf - SPLIT[born] * 12 + B0 * 12;   // frames since this line was born
    // grow from the frame centre outward; lines further from the centre start a little later (ripple)
    const dist = l.v ? Math.abs(l.p - 540) / 540 : Math.abs(l.p - 960) / 960;
    const g = clamp((d - dist * 1.2) / 3);
    if (g <= 0) continue;
    const g2 = eout(g), flash = d < 1 ? 1 : d < 2 ? .5 : 0;
    ctx.save();
    ctx.globalAlpha = (.6 + .4 * flash) * fade; ctx.strokeStyle = flash > .9 ? COL.goldHi : COL.gold; ctx.lineWidth = lw * (1 + .5 * flash);
    if (flash) { ctx.shadowColor = 'rgba(230,200,150,.9)'; ctx.shadowBlur = 18 * flash; }
    ctx.beginPath();
    if (l.v) { ctx.moveTo(l.p, 960 - 960 * g2); ctx.lineTo(l.p, 960 + 960 * g2); }
    else { ctx.moveTo(540 - 540 * g2, l.p); ctx.lineTo(540 + 540 * g2, l.p); }
    ctx.stroke(); ctx.restore();
  }
}

// ------------------------------------------------------------------ the scene
export default {
  id: 's05-grid', start: 24, end: 28,
  cutIn: 'none',
  init(E) { buildMips(E); },
  motionBlur(lt) { const q = lt * 30; return q < 3 ? 4 : q >= DIVE_F0 + .5 && q < DIVE_F0 + 4.6 ? 3 : 1; },
  draw(E, lt, t) {
    const fx = E.fx, bg = E.bg, fg = E.fg;
    const lf = lt * 30;                                   // local frames (fractional)
    const b = B0 + lt / BEAT;                             // absolute beat
    let st = 0; for (let i = 0; i < SPLIT.length; i++) if (b >= SPLIT[i] - 1e-6) st = i;
    const d = (b - SPLIT[st]) * 12;                       // frames since the current layout appeared

    // ---------------- base post
    fx.bloom = .55; fx.bloomThreshold = .88; fx.bloomKnee = .12; fx.grain = .05; fx.vignette = .4; fx.sat = 1.06; fx.rgb = .0015; fx.contrast = 1.03;

    // ---------------- global transform: whip landing (from the right) + Droste dive about the target cell
    let s = 1, tx = 0, ty = 0;
    if (lf < 5) tx = 260 * (1 - expoOut(lf / 4));                 // residual momentum of s04's whip
    const kd = clamp((lf - DIVE_F0) / 5);
    if (lf >= DIVE_F0) {
      s = Math.pow(DIVE_S, kd * kd);
      const m = (s - 1) / (DIVE_S - 1);
      const cx = lerp(TX, 540, m), cy = lerp(TY, 960, m);
      tx = cx - TX * s; ty = cy - TY * s;
    }
    bg.fillStyle = COL.ink; bg.fillRect(0, 0, W, H);
    bg.save(); bg.setTransform(s, 0, 0, s, tx, ty);
    bg.imageSmoothingEnabled = true; bg.imageSmoothingQuality = 'high';

    // ---------------- cells (+ parent lookup for mitosis)
    const [nc, nr] = DIMS[st];
    const [pc, pr] = st > 0 ? DIMS[st - 1] : [1, 1];
    // visible range only (the dive pushes most cells off screen)
    const inv = (X, Y) => [(X - tx) / s, (Y - ty) / s];
    const [x0, y0] = inv(0, 0), [x1, y1] = inv(W, H);
    for (let r = 0; r < nr; r++) for (let c = 0; c < nc; c++) {
      const R = cellRect(st, c, r);
      if (R.x > x1 || R.x + R.w < x0 || R.y > y1 || R.y + R.h < y0) continue;
      let parent = null;
      if (st > 0 && d < MITOSIS + 1) {
        const pcol = Math.floor(c * pc / nc), prow = Math.floor(r * pr / nr);
        parent = content(st - 1, pcol, prow, b);
      }
      paintCell(E, bg, st, c, r, b, d, s, parent);
    }
    bg.restore();

    // ---------------- fg: gutters + lock-on frame around the target
    fg.save(); fg.setTransform(s, 0, 0, s, tx, ty);
    gutters(fg, st, lf, s, 1 - clamp(kd * 2.5));
    if (st === 7 && b >= 27.25 && lf < DIVE_F0) {
      const R = cellRect(7, TARGET.c, TARGET.r), k = expoOut(seg(b, 27.25, 27.25 + 4 / 12));
      const pad = lerp(26, 0, k);
      fg.strokeStyle = COL.goldHi; fg.lineWidth = 4 / Math.pow(s, .55); fg.globalAlpha = k;
      fg.shadowColor = 'rgba(247,226,184,.9)'; fg.shadowBlur = 16;
      fg.strokeRect(R.x - pad + 2, R.y - pad + 2, R.w + 2 * pad - 4, R.h + 2 * pad - 4);
    }
    fg.restore();
    // darken everything but the target during the dive
    if (lf >= DIVE_F0) {
      const R = cellRect(7, TARGET.c, TARGET.r);
      const X0 = R.x * s + tx, Y0 = R.y * s + ty, X1 = (R.x + R.w) * s + tx, Y1 = (R.y + R.h) * s + ty;
      fg.save(); fg.fillStyle = `rgba(5,5,6,${Math.min(.84, kd * 2.4)})`; fg.beginPath(); fg.rect(0, 0, W, H); fg.rect(X0, Y0, X1 - X0, Y1 - Y0); fg.fill('evenodd'); fg.restore();
    }

    // ---------------- edit FX
    // b24 downbeat punch
    if (lf < 8) {
      const k = 1 - expoOut(lf / 8);
      fx.zoom *= 1 + .08 * k; fx.rgb = Math.max(fx.rgb, .0015 + .0185 * Math.max(0, 1 - lf / 8));
      if (lf < 1) { fx.flash = .03 * (1 - lf); fx.flashColor = [1, .93, .8]; }
      fx.zoomBlur = Math.max(fx.zoomBlur, .3 * Math.max(0, 1 - lf / 5));
    }
    // each split: zoom 1.03 -> 1 (3 frames), rgb .008 (2 frames), shake 6 px
    if (st > 0 && d < 3) {
      fx.zoom *= 1 + .03 * (1 - d / 3);
      fx.rgb = Math.max(fx.rgb, d < 1 ? .008 : d < 2 ? .004 : 0);
      const sh = .004 * (1 - d / 3), F = Math.floor(lf);
      fx.shake = [fx.shake[0] + (rnd(F * 3.1 + 5) - .5) * 2 * sh, fx.shake[1] + (rnd(F * 7.7 + 9) - .5) * 2 * sh];
    }
    kickPump(fx, t, [25.5, 26, 27.5].map(x => x * BEAT));
    // b27.0: 2-frame glitch
    if (st === 7 && d < 2) { fx.glitch = .2 * (1 - d / 2.5); fx.glitchSeed = 11 + Math.floor(lf); }
    // the dive: zoom blur toward the target cell
    if (lf >= DIVE_F0) {
      const m = (s - 1) / (DIVE_S - 1), cx = lerp(TX, 540, m), cy = lerp(TY, 960, m);
      fx.zoomBlur = Math.max(fx.zoomBlur, .24 * Math.sin(Math.PI * Math.min(1, kd * .9 + .05))); fx.zoomCenter = [cx / W, 1 - cy / H];
      fx.rgb = Math.max(fx.rgb, .0015 + .0075 * Math.sin(Math.PI * Math.min(1, kd * .85 + .1)));
    }
  },
};
