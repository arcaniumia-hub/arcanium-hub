// s02-break — BREAK: record scratch, tape stop, glass crack, the ANC ring erases the ad, true silence, inhale (b11-16).
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoIn, rnd, text, measure, font, ancRing, FONT, COL } from '../lib.js';
import { renderBefore, renderNarrator, beforeInit } from './s01-before.js';

const f30 = t => Math.round(t * 30);           // frame index of a (sub-)frame time
let SLIDE = null, CHAN = null;                  // offscreen canvases (contents redrawn every frame)
let CRACK = null;                               // crack geometry (seed 1337), built once
const LINE = '...you presented it like';
const WORDS = [['...you', 13.0], ['presented', 13.5], ['it', 14.0], ['like', 14.5]];
let SZ = 76;                                    // narrator line size: fitted at init so the line is 760 px wide (<= ~870 px after the push-in + tracking)

// ------------------------------------------------------------------ where the slide-2 photo's right ear cup lands on screen
// photo: centre (540,1000), width 900, rot -4 deg, zoom z; cup centre in before.jpg ~ (468,298) of 800x452
function cupPoint(z, sag) {
  const s = 900 / 800 * z, px = (468 - 400) * s, py = (298 - 226) * s, a = -4 * Math.PI / 180;
  let x = 540 + px * Math.cos(a) - py * Math.sin(a), y = 1000 + px * Math.sin(a) + py * Math.cos(a);
  x = 540 + (x - 540) * sag.s; y = 960 + (y - 960) * sag.s + sag.dy;
  return [x, y];
}

// ------------------------------------------------------------------ deterministic spider-web crack
function buildCrack() {
  let k = 0; const R = () => rnd(1337 + (k++) * 1.618);
  const rays = [];
  for (let i = 0; i < 14; i++) {
    let a = (i + (R() - .5) * .6) / 14 * TAU, x = 0, y = 0; const pts = [[0, 0]];
    const nseg = 5 + Math.floor(R() * 4), total = 380 + R() * 620;
    for (let j = 0; j < nseg; j++) {
      a += (R() - .5) * .42; const l = total / nseg * (.6 + R() * .8) * (j === 0 ? .55 : 1);
      x += Math.cos(a) * l; y += Math.sin(a) * l; pts.push([x, y]);
    }
    // cumulative lengths
    const cum = [0]; for (let j = 1; j < pts.length; j++) cum.push(cum[j - 1] + Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]));
    // a short side branch or two
    const br = [];
    for (let b = 0; b < 2; b++) if (R() < .7) {
      const j = 1 + Math.floor(R() * (pts.length - 2)); const [bx, by] = pts[j]; let ba = Math.atan2(by, bx) + (R() < .5 ? -1 : 1) * (.5 + R() * .5);
      const bp = [[bx, by]]; let cx = bx, cy = by; for (let m = 0; m < 3; m++) { ba += (R() - .5) * .5; const l = 30 + R() * 70; cx += Math.cos(ba) * l; cy += Math.sin(ba) * l; bp.push([cx, cy]); }
      br.push({ at: cum[j], pts: bp });
    }
    rays.push({ pts, cum, len: cum[cum.length - 1], br });
  }
  // point where a ray crosses radius r
  const cross = (ray, r) => { for (let j = 1; j < ray.pts.length; j++) { const d0 = Math.hypot(...ray.pts[j - 1]), d1 = Math.hypot(...ray.pts[j]); if (d0 <= r && d1 >= r) { const u = (r - d0) / (d1 - d0); return [lerp(ray.pts[j - 1][0], ray.pts[j][0], u), lerp(ray.pts[j - 1][1], ray.pts[j][1], u), ray.cum[j - 1] + u * (ray.cum[j] - ray.cum[j - 1])]; } } return null; };
  // two broken concentric rings: jagged chords between neighbouring rays, some missing
  const rings = [];
  for (const r of [120, 260]) for (let i = 0; i < 14; i++) {
    if (R() < .28) continue;
    const p = cross(rays[i], r * (.92 + R() * .16)), q = cross(rays[(i + 1) % 14], r * (.92 + R() * .16)); if (!p || !q) continue;
    const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2, ml = Math.hypot(mx, my) || 1, bulge = (R() - .3) * 16;
    rings.push({ at: Math.max(p[2], q[2]), pts: [[p[0], p[1]], [mx + mx / ml * bulge, my + my / ml * bulge], [q[0], q[1]]] });
  }
  // glass shards near the impact (faint sheen polygons between neighbouring rays)
  const shards = [];
  for (let i = 0; i < 14; i++) if (R() < .55) {
    const r0 = 15 + R() * 30, r1 = 90 + R() * 150; const p0 = cross(rays[i], r0), p1 = cross(rays[i], r1), q1 = cross(rays[(i + 1) % 14], r1 * (.8 + R() * .3)), q0 = cross(rays[(i + 1) % 14], r0);
    if (p0 && p1 && q1 && q0) shards.push({ a: .05 + R() * .12, pts: [p0, p1, q1, q0] });
  }
  return { rays, rings, shards };
}
function polyPartial(ctx, pts, cum, L) {   // stroke a polyline up to length L
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let j = 1; j < pts.length; j++) {
    if (cum[j] <= L) ctx.lineTo(pts[j][0], pts[j][1]);
    else { const u = (L - cum[j - 1]) / (cum[j] - cum[j - 1]); ctx.lineTo(lerp(pts[j - 1][0], pts[j][0], u), lerp(pts[j - 1][1], pts[j][1], u)); break; }
  }
}
function drawCrack(ctx, cx, cy, p) {
  if (p <= 0) return;
  const C = CRACK, maxL = 1100 * eout(p);
  ctx.save(); ctx.translate(cx, cy); ctx.lineJoin = 'miter'; ctx.lineCap = 'round';
  // sheen of the broken pane
  for (const s of C.shards) { ctx.fillStyle = `rgba(255,255,255,${s.a * p})`; ctx.beginPath(); s.pts.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])); ctx.closePath(); ctx.fill(); }
  const path = () => {
    ctx.beginPath();
    for (const r of C.rays) {
      polyPartial(ctx, r.pts, r.cum, maxL);
      for (const b of r.br) if (maxL > b.at) { const bc = [0]; for (let j = 1; j < b.pts.length; j++) bc.push(bc[j - 1] + Math.hypot(b.pts[j][0] - b.pts[j - 1][0], b.pts[j][1] - b.pts[j - 1][1])); polyPartial(ctx, b.pts, bc, (maxL - b.at) * .7); }
    }
    for (const g of C.rings) if (maxL > g.at) { ctx.moveTo(...g.pts[0]); ctx.lineTo(...g.pts[1]); ctx.lineTo(...g.pts[2]); }
  };
  path(); ctx.strokeStyle = 'rgba(20,22,30,.7)'; ctx.lineWidth = 4; ctx.stroke();
  ctx.strokeStyle = 'rgba(255,255,255,.96)'; ctx.lineWidth = 2; ctx.stroke();
  // impact point: crushed glass
  ctx.fillStyle = 'rgba(255,255,255,.9)'; ctx.beginPath();
  for (let i = 0; i < 12; i++) { const a = i / 12 * TAU, r = (i % 2 ? 4 : 12) * (.7 + rnd(1337 + i) * .6); i ? ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r) : ctx.moveTo(Math.cos(a) * r, Math.sin(a) * r); }
  ctx.closePath(); ctx.fill();
  ctx.restore();
}

// ------------------------------------------------------------------ narrator line layout (per letter, so the inhale can pull each one)
function layoutLine(ctx, track) {
  const size = SZ, fam = FONT.serif; const ch = [...LINE];
  ctx.save(); ctx.font = font(size, 400, fam, true); ctx.letterSpacing = '0px';
  const xs = ch.map((c, i) => ctx.measureText(LINE.slice(0, i)).width + i * track), ws = ch.map(c => ctx.measureText(c).width);
  const tw = ctx.measureText(LINE).width + (ch.length - 1) * track; ctx.restore();
  const x0 = 540 - tw / 2;
  // word index per letter
  const wi = []; let w = 0; ch.forEach((c, i) => { wi.push(w); if (c === ' ') w++; });
  return ch.map((c, i) => ({ c, x: x0 + xs[i] + ws[i] / 2, w: wi[i] }));
}

export default {
  id: 's02-break', start: 11, end: 16,
  cutIn: 'none',
  init(E) {
    beforeInit(E);
    const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
    SLIDE = mk(); CHAN = [mk(), mk()];
    CRACK = buildCrack();
    SZ = Math.round(76 * 760 / measure(SLIDE.getContext('2d'), LINE, 76, 400, FONT.serif, 0, true));
  },
  motionBlur(lt, t) { const b = t / BEAT; return b >= 15.6 && f30(t) < 191 ? 3 : 1; },
  draw(E, lt, t) {
    const beat = t / BEAT, fr = f30(t), ctx = E.bg, fx = E.fx;
    // ---------------- post: cheap look carried over, then the break FX
    fx.bloom = 0; fx.vignette = 0; fx.grain = .02; fx.rgb = 0; fx.sat = 1.08; fx.contrast = .96;

    if (beat < 13.05) {
      // ---------------- TAPE STOP: the deck's clock grinds to zero, then frozen at 11.375 (recomputed every frame)
      const u = seg(beat, 11, 11.75), bl = 11 + .375 * (1 - (1 - u) * (1 - u));
      // sag: the slide drops 14 px and droops; scaled UP 2% (not down) so no frame edge ever shows
      const k = eio(u), sag = { s: 1 + .02 * k, dy: 14 * k };
      renderBefore(SLIDE.getContext('2d'), bl);
      const jerk = { 132: 38, 133: -30, 134: 18 }[fr] || 0;
      ctx.save();
      ctx.translate(540 + jerk, 960 + sag.dy); ctx.scale(sag.s, sag.s); ctx.translate(-540, -960);
      ctx.filter = `saturate(${1 - .7 * k}) brightness(${1 - .1 * k})`;
      if (fr === 132 || fr === 133) {
        // hard RGB split of the slide (one frame of channel tearing per jerk)
        const d = fr === 132 ? 22 : -16;
        for (let c = 0; c < 2; c++) { const x = CHAN[c].getContext('2d'); x.globalCompositeOperation = 'source-over'; x.drawImage(SLIDE, 0, 0); x.globalCompositeOperation = 'multiply'; x.fillStyle = c ? '#00ffff' : '#ff0000'; x.fillRect(0, 0, W, H); }
        ctx.drawImage(CHAN[1], -d, 0); ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(CHAN[0], d, 0); ctx.globalCompositeOperation = 'source-over';
      } else ctx.drawImage(SLIDE, 0, 0);
      ctx.restore();

      // ---------------- GLASS CRACK from the ear cup (b11.75, drawn over 3 frames)
      const [cx, cy] = cupPoint(1 + .04 * (bl - 9), sag);
      const cp = clamp((fr - 141 + 1) / 3);
      if (fr >= 141) drawCrack(ctx, cx, cy, cp);

      // ---------------- the narrator pill stays (it is not part of the cheap world)
      renderNarrator(ctx, 1);

      // ---------------- ANC RING ERASE b12-13
      if (beat >= 12) {
        const r = 2200 * ein(seg(beat, 12, 13));
        // refraction band: the (not yet erased) slide + cracks + pill magnified 1.05 about the ring centre, clipped to [r, r+36]:
        // a visible lens step right outside the ring
        if (r > 2) {
          ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r + 36, 0, TAU); ctx.arc(cx, cy, r, 0, TAU, true); ctx.clip();
          ctx.translate(cx, cy); ctx.scale(1.05, 1.05); ctx.translate(-cx, -cy); ctx.drawImage(ctx.canvas, 0, 0); ctx.restore();
          // the glass of the lens: warm sheen across the band + a 1 px bright outer edge at r+36
          const g = ctx.createRadialGradient(cx, cy, r, cx, cy, r + 36); g.addColorStop(0, 'rgba(255,248,232,.22)'); g.addColorStop(.4, 'rgba(255,248,232,.07)'); g.addColorStop(1, 'rgba(255,248,232,.02)');
          ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r + 36, 0, TAU); ctx.arc(cx, cy, r, 0, TAU, true); ctx.fill();
          ctx.save(); ctx.strokeStyle = 'rgba(255,250,238,.75)'; ctx.lineWidth = 1; ctx.shadowColor = 'rgba(255,250,238,.6)'; ctx.shadowBlur = 4;
          ctx.beginPath(); ctx.arc(cx, cy, r + 36, 0, TAU); ctx.stroke(); ctx.restore();
        }
        // inside: the cheap world, the cracks and the pill are deleted -> one clean, solid ink disc (opaque: nothing survives inside r)
        ctx.fillStyle = COL.ink; ctx.beginPath(); ctx.arc(cx, cy, Math.max(0, r), 0, TAU); ctx.fill();
        // the ring itself: constant 5 px #e6c896, glow 30, full alpha (+ a wide soft halo pass so it holds at full-frame size)
        if (r > 2) { ctx.save(); ctx.strokeStyle = 'rgba(230,200,150,.22)'; ctx.lineWidth = 14; ctx.shadowColor = 'rgba(230,200,150,.55)'; ctx.shadowBlur = 40;
          ctx.beginPath(); ctx.arc(cx, cy, r, 0, TAU); ctx.stroke(); ctx.restore(); }
        ancRing(ctx, cx, cy, r, { refract: false, width: 5, glow: 30, alpha: 1 });
        // HUD label riding the ring top (mono 700, .25em); it fades before it would cross the narrator pill
        const ly = cy - r - 30, la = clamp((ly - 380) / 120) * clamp(r / 60);
        if (la > 0) text(ctx, 'ANC ON \u00b7 \u221242 dB', cx, ly, { size: 30, weight: 700, family: FONT.mono, color: COL.gold, spacing: 7.5, alpha: la, glow: 14, glowColor: 'rgba(5,5,6,.9)' });
        { const q = eio(seg(beat, 12, 12.5)); fx.bloom = lerp(.4, .9, q); fx.bloomThreshold = lerp(.75, .6, q); } fx.displace = .006 * (1 - seg(beat, 12.85, 13)); fx.displaceScale = 2; fx.rgb = .0025;
        fx.vignette = .5 * seg(beat, 12, 13); fx.grain = lerp(.02, .05, seg(beat, 12, 13)); fx.sat = lerp(1.08, 1, seg(beat, 12, 13)); fx.contrast = lerp(.96, 1, seg(beat, 12, 13));
      }
      // b11.0-11.75 FX: rgb kick, glitch slices, scanlines
      if (beat < 11.75) fx.scanlines = .15;
      if (fr === 132 || fr === 133) { fx.rgb = .02; fx.glitch = .25; fx.glitchSeed = fr * 7.3; fx.shake = [jerk / W * .4, 0]; }
      if (fr === 138 || fr === 139) { fx.glitch = .15; fx.glitchSeed = fr * 3.1; }
      if (fr >= 141 && fr <= 143) { const d = fr - 141; fx.rgb = .008 * (1 - d / 3); fx.flash = .14 * (1 - d / 2); fx.zoom = 1 + .02 * (1 - d / 3); fx.shake = [(rnd(fr) - .5) * .008 * (1 - d / 3), (rnd(fr + 9) - .5) * .008 * (1 - d / 3)]; }
    } else {
      // ---------------- TRUE SILENCE: ink + grain, the line builds word by word
      fx.bloom = .3; fx.bloomThreshold = .85; fx.vignette = .5; fx.grain = .05; fx.rgb = .0015; fx.sat = 1; fx.contrast = 1;
    }

    // ---------------- the narrator line (b13-15.92) and the inhale into one gold point
    if (beat >= 13 && fr < 191) {
      const track = SZ * .04 * eio(seg(beat, 14.5, 15.5));
      const L = layoutLine(ctx, track);
      const push = beat < 14.5 ? lerp(.99, 1, seg(beat, 13, 14.5)) : lerp(1, 1.04, eio(seg(beat, 14.5, 15.5)));
      const ui = clamp((t - b2t(15.5)) / (191 / 30 - b2t(15.5))), e = ui * ui;   // inhale 0..1 (accelerating: 64% of the way on the last frame)
      ctx.save(); ctx.translate(540, 960); ctx.scale(push, push); ctx.translate(-540, -960);
      // inner glow building at the centre as the line is sucked in
      if (e > 0) { const g = ctx.createRadialGradient(540, 960, 0, 540, 960, 160); g.addColorStop(0, `rgba(230,200,150,${.5 * e})`); g.addColorStop(1, 'rgba(230,200,150,0)'); ctx.fillStyle = g; ctx.fillRect(380, 800, 320, 320); }
      for (const l of L) {
        if (l.c === ' ') continue;
        const wb = WORDS[l.w][1], a = clamp((t - b2t(wb)) * 30 / 4);
        if (a <= 0) continue;
        const ea = eout(a), blur = 10 * (1 - ea), dy = 14 * (1 - ea);
        const s = lerp(1, .05, e), x = lerp(l.x, 540, e), y = lerp(985 + dy, 960 + 26 * s, e);
        const col = e > 0 ? mixHex(COL.white, COL.goldHi, clamp(e * 2.5)) : COL.white;
        ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
        text(ctx, l.c, 0, 0, { size: SZ, family: FONT.serif, italic: true, color: col, alpha: ea, blur, glow: e > .2 ? 20 * e : 0 });
        ctx.restore();
      }
      ctx.restore();
      if (beat >= 15.5) { const q = seg(beat, 15.5, 15.92); fx.zoomBlur = .4 * q; fx.rgb = .0015 + .0085 * q; fx.bloom = lerp(.3, .9, q); fx.bloomThreshold = lerp(.85, .55, q); }
    }
    // ---------------- f191: only the gold point remains (the seed of THIS. and of the ring)
    if (fr >= 191) {
      ctx.save(); ctx.shadowColor = COL.gold; ctx.shadowBlur = 20; ctx.fillStyle = COL.goldHi;
      ctx.beginPath(); ctx.arc(540, 960, 4, 0, TAU); ctx.fill(); ctx.shadowBlur = 40; ctx.fill(); ctx.restore();
      const g = ctx.createRadialGradient(540, 960, 0, 540, 960, 46); g.addColorStop(0, 'rgba(230,200,150,.35)'); g.addColorStop(1, 'rgba(230,200,150,0)'); ctx.fillStyle = g; ctx.fillRect(494, 914, 92, 92);
      fx.zoomBlur = .4; fx.rgb = .01; fx.bloom = .9; fx.bloomThreshold = .6;
    }
  },
};
const b2t = b => b * BEAT;
function mixHex(a, b, k) {
  const pa = [1, 3, 5].map(i => parseInt(a.slice(i, i + 2), 16)), pb = [1, 3, 5].map(i => parseInt(b.slice(i, i + 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], k))).join(',')})`;
}
