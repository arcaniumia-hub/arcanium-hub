// s01-before — BEFORE: the PowerPoint ad (b0-11).
// The whole cheap deck lives in the pure function renderBefore(ctx, beat) so s02 can redraw any (remapped) beat.
// The narrator caption pill (the only elegant element) lives in renderNarrator(ctx, alpha).
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, eio, elastic, back, rnd, text, measure, FONT, COL } from '../lib.js';

const CHEAP = FONT.cheap;
let PHOTO = null;            // E.img.before
let BG1 = null, BG2 = null;  // pre-rendered static slide backgrounds
let LOWPHOTO = null;         // the photo pre-scaled with low-quality smoothing (soft, 2009-listing look)

// ------------------------------------------------------------------ setup (idempotent; s02 calls it too)
export function beforeInit(E) {
  if (BG1) return;
  PHOTO = E.img.before;
  const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
  // slide 1 background: #d6e6ff -> #ffffff (y 900) -> #eef3fb + cheesy swoosh bands
  BG1 = mk(W, H); {
    const x = BG1.getContext('2d');
    const g = x.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#d6e6ff'); g.addColorStop(900 / H, '#ffffff'); g.addColorStop(1, '#eef3fb');
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    x.fillStyle = 'rgba(59,123,255,.25)';
    x.beginPath(); x.moveTo(0, 1700); x.bezierCurveTo(300, 1610, 640, 1790, 1080, 1660); x.lineTo(1080, 1730); x.bezierCurveTo(660, 1850, 320, 1700, 0, 1770); x.closePath(); x.fill();
    x.beginPath(); x.moveTo(0, 1745); x.bezierCurveTo(360, 1690, 700, 1830, 1080, 1720); x.lineTo(1080, 1800); x.bezierCurveTo(700, 1900, 330, 1760, 0, 1810); x.closePath(); x.fill();
    // a thin white "gloss" line on the swoosh (very 2009)
    x.strokeStyle = 'rgba(255,255,255,.7)'; x.lineWidth = 3;
    x.beginPath(); x.moveTo(0, 1735); x.bezierCurveTo(330, 1650, 660, 1815, 1080, 1695); x.stroke();
  }
  // slide 2 background: #7b3bff -> #2fa8ff
  BG2 = mk(W, H); {
    const x = BG2.getContext('2d');
    const g = x.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#7b3bff'); g.addColorStop(1, '#2fa8ff');
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    // tacky radial "sunburst" rays behind the product (classic clip-art background)
    x.save(); x.translate(540, 1000); x.globalAlpha = .09; x.fillStyle = '#ffffff';
    for (let i = 0; i < 24; i += 2) { const a0 = i / 24 * TAU, a1 = (i + 1) / 24 * TAU; x.beginPath(); x.moveTo(0, 0); x.arc(0, 0, 1500, a0, a1); x.closePath(); x.fill(); }
    x.restore();
  }
  // soft photo: downscale to 60% with low smoothing, it gets upscaled again at draw time with low quality
  LOWPHOTO = mk(Math.round(PHOTO.width * .6), Math.round(PHOTO.height * .6)); {
    const x = LOWPHOTO.getContext('2d'); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'low';
    x.drawImage(PHOTO, 0, 0, LOWPHOTO.width, LOWPHOTO.height);
  }
}

// ------------------------------------------------------------------ small drawing helpers
function starPath(ctx, cx, cy, n, ro, ri, rot = -Math.PI / 2) {
  ctx.beginPath();
  for (let i = 0; i < n * 2; i++) { const r = i % 2 ? ri : ro, a = rot + i * Math.PI / n; const px = cx + Math.cos(a) * r, py = cy + Math.sin(a) * r; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
  ctx.closePath();
}
function roundRect(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
// cheap text: optional hard shadow + fill + outline
function ctext(ctx, s, x, y, { size = 46, color = '#222', stroke = 0, strokeColor = '#000', shadow = null, align = 'center', alpha = 1 } = {}) {
  if (alpha <= .003) return;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.font = `700 ${size}px "${CHEAP}"`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.letterSpacing = '0px';
  if (shadow) { ctx.fillStyle = shadow[2]; ctx.fillText(s, x + shadow[0], y + shadow[1]); }
  ctx.fillStyle = color; ctx.fillText(s, x, y);
  if (stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = stroke; ctx.strokeStyle = strokeColor; ctx.strokeText(s, x, y); }
  ctx.restore();
}
// photo with a border + hard (unblurred) drop shadow, rotation and scale about its centre
function framedPhoto(ctx, cx, cy, w, { border = 4, borderColor = '#9a9a9a', shadow = [16, 16], rot = 0, scale = 1 } = {}) {
  const h = w * PHOTO.height / PHOTO.width;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(scale, scale);
  const bw = w + border * 2, bh = h + border * 2;
  ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillRect(-bw / 2 + shadow[0], -bh / 2 + shadow[1], bw, bh);
  ctx.fillStyle = borderColor; ctx.fillRect(-bw / 2, -bh / 2, bw, bh);
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'low';
  ctx.drawImage(LOWPHOTO, -w / 2, -h / 2, w, h);
  ctx.restore();
}
// clip-art 4-point sparkle
function sparkle(ctx, x, y, r, color) {
  ctx.save(); ctx.translate(x, y);
  ctx.beginPath();
  for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 - Math.PI / 2, rr = i % 2 ? r * .22 : r; i ? ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : ctx.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); }
  ctx.closePath(); ctx.fillStyle = color; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = '#d9a400'; ctx.stroke();
  ctx.restore();
}
// rainbow WordArt with a cheap grey extrusion, per-letter wavy baseline (gradient in canvas space so it spans the word)
const RAINBOW = ['#ff0000', '#ff9900', '#ffee00', '#33cc33', '#3399ff', '#9933ff'];
function wordArt(ctx, s, cx, y, size, tSec, phase = 0) {
  ctx.save(); ctx.font = `700 ${size}px "${CHEAP}"`; ctx.letterSpacing = '0px'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  const ch = [...s], ws = ch.map(c => ctx.measureText(c).width), tw = ws.reduce((a, b) => a + b, 0) + 4 * (ch.length - 1);
  const x0 = cx - tw / 2;
  const g = ctx.createLinearGradient(x0, 0, x0 + tw, 0); RAINBOW.forEach((c, i) => g.addColorStop(i / (RAINBOW.length - 1), c));
  const pos = []; let x = x0;
  ch.forEach((c, i) => { pos.push([x, y + 18 * Math.sin((i + phase) * .7 + tSec * 6)]); x += ws[i] + 4; });
  // extrusion (WordArt "3-D style 1")
  ctx.fillStyle = '#3a2a6a';
  for (let d = 7; d >= 1; d--) ch.forEach((c, i) => ctx.fillText(c, pos[i][0] + d, pos[i][1] + d));
  ctx.fillStyle = g; ch.forEach((c, i) => ctx.fillText(c, pos[i][0], pos[i][1]));
  ctx.lineJoin = 'round'; ctx.lineWidth = 3; ctx.strokeStyle = '#000'; ch.forEach((c, i) => ctx.strokeText(c, pos[i][0], pos[i][1]));
  // glossy white highlight on the top half of every glyph (cheap "bevel")
  ctx.save(); ctx.globalAlpha = .28; ctx.fillStyle = '#fff';
  ch.forEach((c, i) => { ctx.save(); ctx.beginPath(); ctx.rect(pos[i][0] - 4, pos[i][1] - size * .78, ws[i] + 8, size * .3); ctx.clip(); ctx.fillText(c, pos[i][0], pos[i][1]); ctx.restore(); });
  ctx.restore();
  ctx.restore();
}
// the classic link-cursor hand (pointing up in local space), white with black outline
function pointerHand(ctx, x, y, s, rot) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.translate(-8.5, -11);
  ctx.beginPath();
  ctx.moveTo(5, 1.5); ctx.quadraticCurveTo(6.5, -.2, 8, 1.5); ctx.lineTo(8, 8.6);
  ctx.quadraticCurveTo(9.6, 7.2, 11, 8.9); ctx.quadraticCurveTo(12.6, 7.6, 14, 9.4); ctx.quadraticCurveTo(15.8, 8.6, 17, 10.4);
  ctx.lineTo(17, 16); ctx.quadraticCurveTo(17, 19, 15, 21.5); ctx.lineTo(6.5, 21.5); ctx.quadraticCurveTo(4.6, 19.5, 2.6, 15.6);
  ctx.lineTo(.6, 12.4); ctx.quadraticCurveTo(0, 10.6, 1.6, 10.4); ctx.quadraticCurveTo(3.2, 10.4, 5, 13); ctx.closePath();
  ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.lineJoin = 'round'; ctx.lineWidth = 1.1; ctx.strokeStyle = '#000'; ctx.stroke();
  ctx.beginPath(); ctx.moveTo(11, 9); ctx.lineTo(11, 13); ctx.moveTo(14, 9.5); ctx.lineTo(14, 13); ctx.lineWidth = .8; ctx.stroke();
  ctx.restore();
}
// PowerPoint "Bounce" entrance: fall from y0 to y1 between b0..b1 with 2 decaying bounces (parabolic, no squash: cheap)
function bounceY(beat, b0, b1, y0, y1) {
  const T = b1 - b0, u = (beat - b0) / T;
  if (u <= 0) return y0; if (u >= 1) return y1;
  const d0 = .5, d1 = .3, d2 = .2;                 // fractions of T: fall, bounce 1, bounce 2
  const g = 2 * (y1 - y0) / (d0 * d0);             // per T^2
  if (u < d0) return y0 + .5 * g * u * u;
  const par = (v, d) => y1 - .5 * g * v * (d - v); // parabola touching y1 at 0 and d
  if (u < d0 + d1) return par(u - d0, d1);
  return par(u - d0 - d1, d2);
}
function easeOutBounce(x) {
  const n1 = 7.5625, d1 = 2.75; x = clamp(x);
  if (x < 1 / d1) return n1 * x * x; if (x < 2 / d1) return n1 * (x -= 1.5 / d1) * x + .75;
  if (x < 2.5 / d1) return n1 * (x -= 2.25 / d1) * x + .9375; return n1 * (x -= 2.625 / d1) * x + .984375;
}

// ------------------------------------------------------------------ SLIDE 1
function slide1(ctx, beat) {
  const tSec = beat * BEAT, frame = Math.floor(beat * 12 + 1e-6);
  ctx.drawImage(BG1, 0, 0);
  // photo (teeter b6-8)
  const teeter = beat >= 6 && beat < 8 ? 3 * Math.PI / 180 * Math.sin(TAU * (beat - 6)) : 0;
  framedPhoto(ctx, 540, 905, 980, { rot: teeter });
  // sparkles b3-4 at the photo corners, blinking every 1/8
  if (beat >= 3 && beat < 4) {
    const k = Math.floor((beat - 3) * 8);
    const corners = [[50, 628], [1030, 628], [50, 1182], [1030, 1182]];
    corners.forEach(([cx, cy], i) => {
      if ((k + i) % 2) return;
      const jx = (rnd(i * 3.1 + k * .7) - .5) * 70, jy = (rnd(i * 5.3 + k * 1.3) - .5) * 70;
      sparkle(ctx, clamp(cx + jx, 40, 1040), cy + jy, 26 * (.8 + .4 * rnd(i + k * 9)), (i + k) % 2 ? '#ffe600' : '#ffffff');
    });
  }
  // title bounce b1-2
  if (beat >= 1) {
    const y = bounceY(beat, 1, 2, -100, 470);
    ctext(ctx, 'SILENCE ONE', 540, y, { size: 96, color: '#1f4fd8', stroke: 3, strokeColor: '#000', shadow: [6, 6, 'rgba(0,0,0,.45)'] });
  }
  // 'Wireless Headphones' pops in with the first landing (b1.5)
  if (beat >= 1.5) {
    const s = back(seg(beat, 1.5, 1.75), 2.2);
    ctx.save(); ctx.translate(540, 550); ctx.scale(s, s); ctext(ctx, 'Wireless Headphones', 0, 0, { size: 52, color: '#444444' }); ctx.restore();
  }
  // NEW!!! starburst b2
  if (beat >= 2) {
    const s = elastic(seg(beat, 2, 2.75));
    const wob = 7 * Math.PI / 180 * Math.sin(TAU * 1.25 * (tSec - b2t(2)));
    ctx.save(); ctx.translate(868, 650); ctx.rotate(wob); ctx.scale(s, s);
    ctx.fillStyle = 'rgba(0,0,0,.3)'; starPath(ctx, 8, 8, 14, 128, 92); ctx.fill();
    starPath(ctx, 0, 0, 14, 128, 92); ctx.fillStyle = '#ff2b2b'; ctx.fill(); ctx.lineJoin = 'round'; ctx.lineWidth = 4; ctx.strokeStyle = '#ffe600'; ctx.stroke();
    ctx.rotate(-14 * Math.PI / 180); ctext(ctx, 'NEW!!!', 0, 19, { size: 54, color: '#ffe600', stroke: 2, strokeColor: '#8a0000' });
    ctx.restore();
  }
  // 50% OFF!!! banner flies in b4-4.75 (ease-out with 6% overshoot), text blinks from b5
  if (beat >= 4) {
    const u = seg(beat, 4, 4.75);
    const k = u < .7 ? 1.06 * eout(u / .7) : lerp(1.06, 1, eio((u - .7) / .3));
    const x = lerp(-1100, 540, k);
    ctx.save(); ctx.translate(x, 1296); ctx.rotate(-3 * Math.PI / 180);
    ctx.fillStyle = 'rgba(0,0,0,.28)'; ctx.fillRect(-640 + 10, -66 + 10, 1280, 132);
    ctx.fillStyle = '#ffe600'; ctx.fillRect(-640, -66, 1280, 132);
    ctx.fillStyle = '#ff2b2b'; ctx.fillRect(-640, -66, 1280, 8); ctx.fillRect(-640, 58, 1280, 8);
    const vis = beat < 5 || Math.floor(frame / 6) % 2 === 0;
    if (vis) ctext(ctx, '50% OFF!!!', 0, 34, { size: 98, color: '#e01010', stroke: 2, strokeColor: '#000' });
    ctx.restore();
  }
  // bullets 'Appear' (instant)
  const bul = [[5, '• Good sound', 1440], [5.5, '• Wireless', 1500], [6, '• Very comfortable!!', 1560]];
  for (const [b, s, y] of bul) if (beat >= b) ctext(ctx, s, 190, y, { size: 46, color: '#222222', align: 'left' });
}
const b2t = b => b * BEAT;

// ------------------------------------------------------------------ SLIDE 2
function slide2(ctx, beat) {
  const tSec = beat * BEAT;
  ctx.drawImage(BG2, 0, 0);
  // polaroid photo, rotated -4 deg, cheesy slow zoom (keeps creeping after b11 so a tape-stop can grind it to a halt)
  const z = 1 + .04 * Math.max(0, beat - 9);
  framedPhoto(ctx, 540, 1000, 900, { border: 10, borderColor: '#ffffff', shadow: [18, 18], rot: -4 * Math.PI / 180, scale: z });
  // WordArt
  wordArt(ctx, 'AMAZING', 540, 430, 80, tSec, 0);
  wordArt(ctx, 'SOUND!!!', 540, 530, 80, tSec, 3);
  // 40 HRS!! red circle
  ctx.save(); ctx.translate(230, 1380);
  ctx.fillStyle = 'rgba(0,0,0,.3)'; ctx.beginPath(); ctx.arc(8, 8, 120, 0, TAU); ctx.fill();
  ctx.fillStyle = '#e01010'; ctx.beginPath(); ctx.arc(0, 0, 120, 0, TAU); ctx.fill();
  ctx.lineWidth = 5; ctx.strokeStyle = '#ffe600'; ctx.beginPath(); ctx.arc(0, 0, 108, 0, TAU); ctx.stroke();
  ctx.rotate(10 * Math.PI / 180); ctext(ctx, '40 HRS!!', 0, 16, { size: 46, color: '#ffe600', stroke: 2, strokeColor: '#5a0000' });
  ctx.restore();
  // five stars (drawn as paths: no glyph fallback surprises)
  for (let i = 0; i < 5; i++) {
    const sx = 690 - 2 * 66 + i * 66, sy = 1420;
    ctx.save(); starPath(ctx, sx, sy, 5, 30, 12.5); ctx.fillStyle = '#ffcc00'; ctx.fill(); ctx.lineJoin = 'round'; ctx.lineWidth = 2.5; ctx.strokeStyle = '#000'; ctx.stroke(); ctx.restore();
  }
  // BUY NOW! button bounces in at b9.75, then pulses on the beat; pointer hand wiggles at its right
  if (beat >= 9.75) {
    const u = seg(beat, 9.75, 10.25);
    const y = lerp(2050, 1560, easeOutBounce(u));
    const pulseS = 1 + .045 * Math.max(0, Math.sin(Math.PI * clamp((beat % 1) * 2.2)));
    ctx.save(); ctx.translate(540, y); ctx.scale(pulseS, pulseS);
    ctx.fillStyle = 'rgba(0,0,0,.35)'; roundRect(ctx, -240 + 8, -55 + 8, 480, 110, 24); ctx.fill();
    const g = ctx.createLinearGradient(0, -55, 0, 55); g.addColorStop(0, '#4cd964'); g.addColorStop(1, '#1e9e3a');
    ctx.fillStyle = g; roundRect(ctx, -240, -55, 480, 110, 24); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,.45)'; roundRect(ctx, -228, -49, 456, 46, 18); ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = '#0d5a1e'; roundRect(ctx, -240, -55, 480, 110, 24); ctx.stroke();
    ctext(ctx, 'BUY NOW!', 0, 19, { size: 54, color: '#ffffff', stroke: 2, strokeColor: '#0d5a1e' });
    ctx.restore();
    const hx = 540 + 270 + 28 + 14 * Math.sin(TAU * 2.5 * tSec), hy = y + 34 + 6 * Math.sin(TAU * 2.5 * tSec + 1);
    pointerHand(ctx, hx, hy, 4.4, -1.15);
  }
}

// ------------------------------------------------------------------ the deck
export function renderBefore(ctx, beat) {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none';
  if (beat < 8) {
    if (beat < 1) {
      // PowerPoint STAR WIPE from plain white
      ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H);
      const ro = 2400 * clamp(beat);
      if (ro > .5) { ctx.save(); starPath(ctx, 540, 960, 5, ro, ro * .45); ctx.clip(); slide1(ctx, beat); ctx.restore(); }
    } else slide1(ctx, beat);
  } else if (beat < 9) {
    // PowerPoint SWIVEL: slide 1 turns away (scaleX = cos 0..pi/2, shrinking 1 -> .6), slide 2 turns in from the other side
    ctx.fillStyle = '#1b1b1b'; ctx.fillRect(0, 0, W, H);
    const u = seg(beat, 8, 9);
    if (u < .5) {
      const v = u / .5, sx = Math.cos(eio(v) * Math.PI / 2), s = lerp(1, .6, eio(v));
      ctx.save(); ctx.translate(540, 960); ctx.scale(Math.max(.002, sx) * s, s); ctx.translate(-540, -960); slide1(ctx, 8);
      ctx.fillStyle = `rgba(0,0,0,${.45 * eio(v)})`; ctx.fillRect(0, 0, W, H); ctx.restore();
    } else {
      const v = (u - .5) / .5, sx = Math.sin(eio(v) * Math.PI / 2), s = lerp(.6, 1, eio(v));
      ctx.save(); ctx.translate(540, 960); ctx.scale(-Math.max(.002, sx) * s, s); ctx.scale(-1, 1); ctx.translate(-540, -960); slide2(ctx, beat);
      ctx.fillStyle = `rgba(0,0,0,${.45 * (1 - eio(v))})`; ctx.fillRect(0, 0, W, H); ctx.restore();
    }
  } else slide2(ctx, beat);
  ctx.restore();
}

// ------------------------------------------------------------------ narrator caption pill (fg)
export function renderNarrator(ctx, alpha = 1) {
  if (alpha <= .003) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  ctx.fillStyle = 'rgba(5,5,6,.97)'; ctx.beginPath(); ctx.roundRect(540 - 460, 285 - 75, 920, 150, 30); ctx.fill();
  ctx.restore();
  text(ctx, 'What if instead of presenting', 540, 262, { size: 50, family: FONT.serif, italic: true, color: COL.white, alpha });
  text(ctx, 'your product like this...', 540, 318, { size: 50, family: FONT.serif, italic: true, color: COL.white, alpha });
}

export default {
  id: 's01-before', start: 0, end: 11,
  cutIn: 'none',
  init(E) { beforeInit(E); },
  draw(E, lt, t) {
    const beat = t / BEAT;
    renderBefore(E.bg, beat);
    renderNarrator(E.fg, eio(seg(beat, .5, 1)));
    const fx = E.fx;
    fx.bloom = 0; fx.vignette = 0; fx.grain = .02; fx.rgb = 0; fx.sat = 1.08; fx.contrast = .96;
  },
};
