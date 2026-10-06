/* "Nem toda birra é só birra" — 30s vertical reel, rendered deterministically.
   window.renderAt(t) draws the frame for time t (seconds) on #c. */

const W = 1080, H = 1920, DUR = 30;
const main = document.getElementById('c').getContext('2d');
const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
const bufA = mk(), bufB = mk(), lay = mk();
let ctx = main;
let CAM = new DOMMatrix();
let T = 0;

// ---------- palette
const P = {
  cream: '#F7F0E6', cream2: '#F0E5D5', wall: '#F4EBDF', wall2: '#EEE2D2',
  floor: '#E8D9C4', floor2: '#DFCCB2', beige: '#D9C6AB',
  blue: '#A8C1D4', blueL: '#D6E3EC', blueM: '#8EABC2',
  pink: '#DDA89F', pinkL: '#F1D7CF', pinkD: '#B9776F',
  deep: '#1F3A5F', deep2: '#2C4D76', ink: '#231915',
  cSkin: '#9A6447', cSkinD: '#7C4C34', cHair: '#2A1D18', cShirt: '#DCA197', cShirtD: '#C88A80',
  cPants: '#2F4E76', shoe: '#F6EEE3', shoeD: '#E2D6C6',
  pSkin: '#D7A07C', pSkinD: '#B98262', pHair: '#3A2820', pTop: '#A9C2D5', pTopD: '#90ACC2',
  pPants: '#BFA587', pPantsD: '#A88E70', pShoe: '#5B4637',
};

// ---------- math
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => { t = clamp(t); return 1 - Math.pow(1 - t, 3); };
const eback = t => { t = clamp(t); const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const S = (t, a, b) => eio(seg(t, a, b));
const TAU = Math.PI * 2;
function mix(a, b, k) {
  if (typeof a === 'number') return lerp(a, b, k);
  if (Array.isArray(a)) return a.map((v, i) => mix(v, b[i], k));
  const r = {};
  for (const key in a) r[key] = (key in b) ? mix(a[key], b[key], k) : a[key];
  return r;
}
// deterministic pseudo random
const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
// keyframed value [[t, ...values]]
function keys(t, ks) {
  if (t <= ks[0][0]) return ks[0].slice(1);
  for (let i = 0; i < ks.length - 1; i++) {
    const a = ks[i], b = ks[i + 1];
    if (t <= b[0]) { const k = eio((t - a[0]) / (b[0] - a[0])); return a.slice(1).map((v, j) => lerp(v, b[j + 1], k)); }
  }
  return ks[ks.length - 1].slice(1);
}

// ---------- drawing primitives
function ell(x, y, rx, ry, fill, rot = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(.01, rx), Math.max(.01, ry), rot, 0, TAU); ctx.fillStyle = fill; ctx.fill(); }
const circ = (x, y, r, fill) => ell(x, y, r, r, fill);
function poly(pts, w, col) {
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.lineWidth = w; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();
}
function curve(pts, w, col) { // smooth polyline through points (quadratic midpoints)
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length - 1; i++) {
    const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2;
    ctx.quadraticCurveTo(pts[i][0], pts[i][1], mx, my);
  }
  const l = pts[pts.length - 1]; ctx.lineTo(l[0], l[1]);
  ctx.lineWidth = w; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();
}
// two-bone IK; returns elbow/knee and end point
function ik(Sp, Tg, L1, L2, sgn) {
  const dx = Tg[0] - Sp[0], dy = Tg[1] - Sp[1];
  const dist = Math.hypot(dx, dy) || .001;
  const ux = dx / dist, uy = dy / dist;
  const d = clamp(dist, Math.abs(L1 - L2) + .01, L1 + L2 - .01);
  const a = (L1 * L1 - L2 * L2 + d * d) / (2 * d);
  const h = Math.sqrt(Math.max(0, L1 * L1 - a * a));
  return { e: [Sp[0] + ux * a - uy * h * sgn, Sp[1] + uy * a + ux * h * sgn], h: [Sp[0] + ux * d, Sp[1] + uy * d] };
}
// convert a world point into the current local drawing space
function toLocal(wp) {
  const m = ctx.getTransform().inverse().multiply(CAM);
  const p = m.transformPoint(new DOMPoint(wp[0], wp[1]));
  return [p.x, p.y];
}

// arm target: [dx,dy] relative to shoulder, {w:[x,y]} world point, or {blend,rest,target}
function armTarget(Sh, a) {
  if (Array.isArray(a)) return [Sh[0] + a[0], Sh[1] + a[1]];
  if (a.w) return toLocal(a.w);
  return mix([Sh[0] + a.rest[0], Sh[1] + a.rest[1]], toLocal(a.target), a.blend);
}

// ---------- faces
function face(ex, k, eyeY) {
  const eyX = 29 * k, eyY = eyeY * k;
  const lx = (ex.lx || 0) * 5 * k, ly = (ex.ly || 0) * 4 * k;
  // blush
  ctx.fillStyle = `rgba(205,110,100,${0.22 + 0.12 * (ex.tr || 0)})`;
  [-1, 1].forEach(sd => { ctx.beginPath(); ctx.ellipse(sd * 46 * k, eyY + 27 * k, 15 * k, 9 * k, 0, 0, TAU); ctx.fill(); });
  // eyes
  const blink = ex.blink || 0;
  [-1, 1].forEach(sd => {
    const cx = sd * eyX + lx, cy = eyY + ly;
    const open = ex.eo * (1 - blink);
    if (open > .12) {
      ctx.beginPath(); ctx.ellipse(cx, cy, 8.6 * k, 10.6 * k * open, 0, 0, TAU); ctx.fillStyle = P.ink; ctx.fill();
      const wet = 1 + .5 * (ex.tr || 0);
      circ(cx + 2.6 * k, cy - 3.6 * k * open, 2.7 * k * wet, 'rgba(255,255,255,.92)');
      circ(cx - 2.6 * k, cy + 3.6 * k * open, 1.3 * k * wet, 'rgba(255,255,255,.55)');
      if ((ex.tr || 0) > .02) { // watery lower lid
        ctx.beginPath(); ctx.moveTo(cx - 9 * k, cy + 9 * k * open); ctx.quadraticCurveTo(cx, cy + 14 * k * open, cx + 9 * k, cy + 9 * k * open);
        ctx.strokeStyle = `rgba(190,220,240,${.8 * ex.tr})`; ctx.lineWidth = 2.6 * k; ctx.stroke();
      }
    } else {
      ctx.beginPath(); ctx.moveTo(cx - 9 * k, cy); ctx.quadraticCurveTo(cx, cy + 4 * k, cx + 9 * k, cy);
      ctx.strokeStyle = P.ink; ctx.lineWidth = 3.4 * k; ctx.lineCap = 'round'; ctx.stroke();
    }
  });
  // brows
  [-1, 1].forEach(sd => {
    const bi = ex.bi + sd * (ex.ba || 0);
    const by = eyY - 24 * k;
    const ix = sd * 13 * k + lx * .4, ox = sd * 41 * k + lx * .4;
    const iy = by - bi * 8 * k, oy = by + bi * 2.5 * k - 1 * k;
    ctx.beginPath(); ctx.moveTo(ix, iy); ctx.quadraticCurveTo((ix + ox) / 2, Math.min(iy, oy) - 3.5 * k, ox, oy);
    ctx.strokeStyle = ex.browCol || P.cHair; ctx.lineWidth = 5 * k; ctx.lineCap = 'round'; ctx.stroke();
  });
  // nose
  ctx.beginPath(); ctx.moveTo(-5 * k, eyY + 22 * k); ctx.quadraticCurveTo(0, eyY + 27 * k, 5 * k, eyY + 22 * k);
  ctx.strokeStyle = ex.noseCol || 'rgba(90,50,35,.55)'; ctx.lineWidth = 3 * k; ctx.stroke();
  // mouth
  const my = eyY + 43 * k, c = ex.mc, o = ex.mo;
  const w = (14 + 6 * o) * k, cy = -c * 5 * k;
  if (o < .08) {
    ctx.beginPath(); ctx.moveTo(-w, my + cy); ctx.quadraticCurveTo(0, my + c * 9 * k, w, my + cy);
    ctx.strokeStyle = '#5c2b27'; ctx.lineWidth = 3.8 * k; ctx.lineCap = 'round'; ctx.stroke();
  } else {
    ctx.beginPath(); ctx.moveTo(-w, my + cy);
    ctx.quadraticCurveTo(0, my - o * 6 * k + c * 6 * k, w, my + cy);
    ctx.quadraticCurveTo(0, my + o * 26 * k + c * 9 * k, -w, my + cy);
    ctx.closePath(); ctx.fillStyle = '#6b2c2a'; ctx.fill();
    ctx.save(); ctx.clip(); ell(0, my + o * 16 * k, w * .7, 8 * k, '#c9706b'); ctx.restore();
  }
  // tears
  const tr = ex.tr || 0;
  if (tr > .02) {
    [-1, 1].forEach(sd => {
      const x0 = sd * (eyX + 3 * k) + lx, y0 = eyY + 11 * k;
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.quadraticCurveTo(x0 + sd * 7 * k, y0 + 18 * k, x0 + sd * 4 * k, y0 + 40 * k);
      ctx.strokeStyle = `rgba(170,208,234,${.75 * tr})`; ctx.lineWidth = 5 * k; ctx.lineCap = 'round'; ctx.stroke();
      const ph = (T * 1.25 + (sd > 0 ? .45 : 0)) % 1;
      const dy = y0 + 24 * k + ph * 52 * k;
      ctx.globalAlpha *= 1; ell(x0 + sd * 5 * k, dy, 4.2 * k, 5.6 * k, `rgba(185,218,240,${.9 * tr * (1 - ph)})`);
    });
  }
}

// ---------- child
function childHead(ex, back) {
  const R = 78;
  // afro volume
  ctx.fillStyle = P.cHair; ctx.beginPath();
  for (let i = 0; i <= 18; i++) {
    const a = Math.PI * (.80 + 1.40 * i / 18);
    const x = Math.cos(a) * 82, y = Math.sin(a) * 80 - 8, r = 34 + 4 * rnd(i);
    ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, TAU);
  }
  ctx.moveTo(95, -18); ctx.arc(0, -18, 95, 0, TAU);
  ctx.fill();
  // curl texture
  ctx.strokeStyle = 'rgba(255,240,225,.07)'; ctx.lineWidth = 3;
  for (let i = 0; i < 14; i++) {
    const a = Math.PI * (.95 + 1.1 * rnd(i + 40)), rr = 70 + 35 * rnd(i + 80);
    const x = Math.cos(a) * rr, y = Math.sin(a) * rr - 14;
    ctx.beginPath(); ctx.arc(x, y, 9, a, a + 2.4); ctx.stroke();
  }
  // ears
  circ(-77, 14, 15, P.cSkin); circ(77, 14, 15, P.cSkin);
  if (back) { // back of head: all hair
    circ(0, 0, R + 4, P.cHair);
    return;
  }
  circ(0, 0, R, P.cSkin);
  // front hairline
  ctx.save(); ctx.beginPath(); ctx.arc(0, 0, R, 0, TAU); ctx.clip();
  ctx.fillStyle = P.cHair; ctx.fillRect(-R, -R - 10, 2 * R, R - 30);
  for (let x = -R - 4; x <= R + 4; x += 19) { ctx.beginPath(); ctx.arc(x, -40 + Math.abs(x) * .32, 15, 0, TAU); ctx.fill(); }
  ctx.restore();
  face(ex, 1, 14);
}

function drawChild(x, y, s, p, ex, back = false) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ell(0, 2, p.shW || 165, 20, 'rgba(70,45,30,0.13)');
  const hip = p.hip;
  // legs
  [[-1, p.fL, p.kL], [1, p.fR, p.kR]].forEach(([sd, f, ks]) => {
    const Hh = [hip[0] + sd * 30, hip[1]];
    const k = ik(Hh, f, 110, 104, ks);
    poly([Hh, k.e, k.h], 44, P.cPants);
    ell(k.h[0] + sd * 6, k.h[1] - 2, 27, 15, back ? P.shoeD : P.shoe);
  });
  // torso
  ctx.save(); ctx.translate(hip[0] + (p.shake || 0), hip[1] + (p.bob || 0)); ctx.rotate(p.lean || 0);
  const TL = 150, br = 1 + .012 * Math.sin(T * 2.4);
  ctx.scale(1, br);
  ctx.fillStyle = P.cSkin; ctx.fillRect(-14, -TL - 32, 28, 40);
  ctx.beginPath(); ctx.moveTo(-63, 10); ctx.quadraticCurveTo(-70, -70, -60, -TL + 20);
  ctx.quadraticCurveTo(-56, -TL - 2, -28, -TL - 4); ctx.lineTo(28, -TL - 4);
  ctx.quadraticCurveTo(56, -TL - 2, 60, -TL + 20); ctx.quadraticCurveTo(70, -70, 63, 10);
  ctx.quadraticCurveTo(0, 20, -63, 10); ctx.fillStyle = P.cShirt; ctx.fill();
  if (!back) { // collar
    ctx.beginPath(); ctx.moveTo(-20, -TL - 3); ctx.quadraticCurveTo(0, -TL + 14, 20, -TL - 3);
    ctx.strokeStyle = P.cShirtD; ctx.lineWidth = 5; ctx.stroke();
  }
  // head (drawn before arms so hands can rise in front of face)
  ctx.save(); ctx.translate(0, -TL - 64); ctx.rotate(p.tilt || 0); childHead(ex, back); ctx.restore();
  // arms
  [[-1, p.aL, p.eL], [1, p.aR, p.eR]].forEach(([sd, a, es]) => {
    const Sh = [sd * 50, -TL + 14];
    const tgt = armTarget(Sh, a);
    const k = ik(Sh, tgt, 64, 60, es);
    poly([Sh, k.e, k.h], 25, P.cSkin);
    const sl = [lerp(Sh[0], k.e[0], .5), lerp(Sh[1], k.e[1], .5)];
    poly([Sh, sl], 40, P.cShirt);
    circ(k.h[0], k.h[1], 16, P.cSkin);
  });
  ctx.restore();
  ctx.restore();
}

// ---------- parent
function parentHead(ex, back) {
  const R = 64;
  circ(10, -70, 30, P.pHair); // bun
  ell(0, -6, 71, 70, P.pHair);
  circ(-62, 10, 12, P.pSkin); circ(62, 10, 12, P.pSkin);
  if (back) { ell(0, -4, 66, 66, P.pHair); ctx.strokeStyle = 'rgba(255,240,225,.08)'; ctx.lineWidth = 3;
    for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.arc(10, -70, 18 - i * 3, i, i + 2.5); ctx.stroke(); }
    return; }
  circ(0, 0, R, P.pSkin);
  ctx.save(); ctx.beginPath(); ctx.arc(0, 0, R, 0, TAU); ctx.clip();
  ctx.beginPath(); ctx.moveTo(-R - 5, 18); ctx.quadraticCurveTo(-58, -46, -6, -50);
  ctx.quadraticCurveTo(44, -50, R + 5, 8); ctx.lineTo(R + 5, -R - 5); ctx.lineTo(-R - 5, -R - 5); ctx.closePath();
  ctx.fillStyle = P.pHair; ctx.fill();
  ctx.restore();
  face(Object.assign({ browCol: P.pHair, noseCol: 'rgba(130,75,50,.5)' }, ex), .8, 12);
}

function drawParent(x, y, s, p, ex, back = false) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ell(p.hip[0] * .5, 2, 190, 24, 'rgba(70,45,30,0.13)');
  const hip = p.hip;
  [[-1, p.fL, p.kL], [1, p.fR, p.kR]].forEach(([sd, f, ks]) => {
    const Hh = [hip[0] + sd * 34, hip[1]];
    const k = ik(Hh, f, 216, 212, ks);
    poly([Hh, k.e, k.h], 58, P.pPants);
    ell(k.h[0] + sd * 8 + (p.footDir || 0) * 12, k.h[1] - 3, 34, 15, P.pShoe);
  });
  ctx.save(); ctx.translate(hip[0], hip[1] + (p.bob || 0)); ctx.rotate(p.lean || 0);
  const TL = 300, br = 1 + .008 * Math.sin(T * 2.0 + 1);
  ctx.scale(1, br);
  ctx.fillStyle = P.pSkin; ctx.fillRect(-16, -TL - 38, 32, 50);
  ctx.beginPath(); ctx.moveTo(-66, 14); ctx.quadraticCurveTo(-78, -150, -84, -TL + 34);
  ctx.quadraticCurveTo(-84, -TL - 2, -40, -TL - 6); ctx.lineTo(40, -TL - 6);
  ctx.quadraticCurveTo(84, -TL - 2, 84, -TL + 34); ctx.quadraticCurveTo(78, -150, 66, 14);
  ctx.quadraticCurveTo(0, 26, -66, 14); ctx.fillStyle = P.pTop; ctx.fill();
  // ribbed hem + neckline
  ctx.beginPath(); ctx.moveTo(-66, 0); ctx.quadraticCurveTo(0, 12, 66, 0); ctx.strokeStyle = P.pTopD; ctx.lineWidth = 6; ctx.stroke();
  if (!back) { ctx.beginPath(); ctx.moveTo(-26, -TL - 5); ctx.quadraticCurveTo(0, -TL + 20, 26, -TL - 5); ctx.strokeStyle = P.pTopD; ctx.lineWidth = 6; ctx.stroke(); }
  ctx.save(); ctx.translate(0, -TL - 78); ctx.rotate(p.tilt || 0); parentHead(ex, back); ctx.restore();
  [[-1, p.aL, p.eL], [1, p.aR, p.eR]].forEach(([sd, a, es]) => {
    const Sh = [sd * 72, -TL + 22];
    const tgt = armTarget(Sh, a);
    const k = ik(Sh, tgt, 140, 132, es);
    poly([Sh, k.e, k.h], 40, P.pTop);
    const cuff = [lerp(k.e[0], k.h[0], .88), lerp(k.e[1], k.h[1], .88)];
    poly([cuff, k.h], 20, P.pSkin);
    circ(k.h[0], k.h[1], 18, P.pSkin);
  });
  ctx.restore();
  ctx.restore();
}

// ---------- poses
const C_SIT = { hip: [0, -34], lean: 0, tilt: 0, shW: 170,
  fL: [-128, -6], fR: [128, -6], kL: 1, kR: -1,
  aL: [-14, 132], aR: [14, 132], eL: -1, eR: 1 };
const C_TALK = Object.assign({}, C_SIT, { aL: [-62, 40], aR: [62, 40], eL: -1, eR: 1 });
const C_LAP = Object.assign({}, C_SIT, { aL: [44, 112], aR: [-44, 112] });
const C_STAND = { hip: [0, -212], lean: 0, tilt: 0, shW: 90,
  fL: [-30, -6], fR: [30, -6], kL: 1, kR: -1,
  aL: [-12, 120], aR: [12, 120], eL: 1, eR: -1 };

const P_CONF = { hip: [0, -428], lean: 0, tilt: .06, footDir: 0,
  fL: [-48, -8], fR: [48, -8], kL: 1, kR: -1,
  aL: [70, -132], aR: [-14, 250], eL: -1, eR: -1 };
const P_STAND = Object.assign({}, P_CONF, { tilt: .05, aL: [-6, 262], aR: [6, 262], eL: 1, eR: -1 });
const P_KNEEL = { hip: [0, -150], lean: .42, tilt: .14, footDir: 1,
  fL: [-74, -10], fR: [150, -8], kL: -1, kR: -1,
  aL: [70, 190], aR: [40, 230], eL: 1, eR: 1 };

// ---------- symbol icons (line art, centered, ~70px)
function iconMoon() {
  ctx.beginPath(); ctx.arc(0, 0, 30, Math.PI / 4, Math.PI * 7 / 4, false);
  ctx.arc(14, 0, 22.4, -71.2 * Math.PI / 180, 71.2 * Math.PI / 180, true); ctx.closePath(); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(26, -30); ctx.lineTo(26, -18); ctx.moveTo(20, -24); ctx.lineTo(32, -24); ctx.stroke();
}
function iconCloud() {
  ctx.beginPath(); ctx.moveTo(-30, 8); ctx.arc(-18, -2, 14, Math.PI * .75, Math.PI * 1.55);
  ctx.arc(2, -12, 18, Math.PI * 1.15, Math.PI * 1.95); ctx.arc(22, 0, 13, Math.PI * 1.4, Math.PI * .5);
  ctx.lineTo(-24, 13); ctx.quadraticCurveTo(-33, 12, -30, 8); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(2, 18); ctx.lineTo(-6, 30); ctx.lineTo(4, 30); ctx.lineTo(-4, 42); ctx.stroke();
}
function iconScribble(pr) {
  ctx.beginPath(); const n = 120;
  for (let i = 0; i <= n * pr; i++) {
    const th = i / n * TAU * 1.6;
    const x = 26 * Math.sin(2.2 * th) + 8 * Math.cos(5.1 * th), y = 20 * Math.cos(3.1 * th) + 6 * Math.sin(4.3 * th);
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }
  ctx.stroke();
}
function iconBowl() {
  ctx.beginPath(); ctx.moveTo(-32, 4); ctx.lineTo(32, 4); ctx.quadraticCurveTo(30, 34, 0, 36); ctx.quadraticCurveTo(-30, 34, -32, 4); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-10, 30 - 8 + 18); ctx.stroke();
  for (const sx of [-10, 6]) {
    ctx.beginPath(); const ph = T * 3 + sx;
    for (let i = 0; i <= 10; i++) { const yy = -6 - i * 2.6; const xx = sx + Math.sin(i * .8 + ph) * 4; i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
    ctx.stroke();
  }
}
function heartPath(sc, cx = 0, cy = 0) {
  ctx.beginPath();
  for (let i = 0; i <= 80; i++) {
    const t = i / 80 * TAU;
    const x = 16 * Math.pow(Math.sin(t), 3), y = -(13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t));
    i ? ctx.lineTo(cx + x * sc, cy + y * sc) : ctx.moveTo(cx + x * sc, cy + y * sc);
  }
  ctx.closePath();
}
function iconHeart() {
  heartPath(1.9, 0, 2); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-2, -16); ctx.lineTo(5, -4); ctx.lineTo(-4, 6); ctx.lineTo(3, 18); ctx.stroke();
}
const SYMS = [
  { f: iconMoon, ang: 205, col: 'rgba(214,227,236,.85)' },
  { f: iconCloud, ang: 250, col: 'rgba(168,193,212,.62)' },
  { f: iconScribble, ang: 295, col: 'rgba(241,215,207,.88)' },
  { f: iconBowl, ang: 340, col: 'rgba(240,229,213,.92)' },
  { f: iconHeart, ang: 22, col: 'rgba(221,168,159,.55)' },
];

// ---------- background pieces
function room(warm) {
  // wall
  let g = ctx.createLinearGradient(0, 0, 0, 1150);
  g.addColorStop(0, P.wall); g.addColorStop(1, P.wall2);
  ctx.fillStyle = g; ctx.fillRect(-900, -600, 2900, 1752);
  // floor
  g = ctx.createLinearGradient(0, 1150, 0, 2300);
  g.addColorStop(0, P.floor); g.addColorStop(1, P.floor2);
  ctx.fillStyle = g; ctx.fillRect(-900, 1150, 2900, 1300);
  ctx.fillStyle = '#EADFD0'; ctx.fillRect(-900, 1128, 2900, 24);
  ctx.fillStyle = 'rgba(120,90,60,.10)'; ctx.fillRect(-900, 1150, 2900, 4);
  // arched window
  const wx = 700, wy = 470, ww = 270, wh = 540, r = ww / 2;
  const arch = (pad) => { ctx.beginPath(); ctx.moveTo(wx - pad, wy + wh + pad); ctx.lineTo(wx - pad, wy + r);
    ctx.arc(wx + r, wy + r, r + pad, Math.PI, 0); ctx.lineTo(wx + ww + pad, wy + wh + pad); ctx.closePath(); };
  ctx.save(); ctx.shadowColor = 'rgba(120,90,60,.12)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
  arch(18); ctx.fillStyle = '#FBF7F1'; ctx.fill(); ctx.restore();
  arch(0); g = ctx.createLinearGradient(0, wy, 0, wy + wh);
  g.addColorStop(0, lerpCol('#C9DBE7', '#F6D9BC', warm)); g.addColorStop(1, lerpCol('#EAF1F5', '#FBE9D3', warm));
  ctx.fillStyle = g; ctx.fill();
  ctx.fillStyle = '#FBF7F1'; ctx.fillRect(wx + r - 7, wy, 14, wh); ctx.fillRect(wx, wy + 300, ww, 14);
  ctx.fillStyle = '#EFE6DA'; ctx.fillRect(wx - 34, wy + wh + 14, ww + 68, 18);
  // window light on floor
  ctx.beginPath(); ctx.moveTo(wx + 10, 1160); ctx.lineTo(wx + ww - 10, 1160); ctx.lineTo(wx + ww + 230, 1900); ctx.lineTo(wx - 40, 1900); ctx.closePath();
  g = ctx.createLinearGradient(0, 1160, 0, 1900);
  g.addColorStop(0, `rgba(255,248,232,${.45 + .25 * warm})`); g.addColorStop(1, 'rgba(255,248,232,0)');
  ctx.fillStyle = g; ctx.fill();
}
function lerpCol(a, b, k) {
  const pa = [1, 3, 5].map(i => parseInt(a.substr(i, 2), 16)), pb = [1, 3, 5].map(i => parseInt(b.substr(i, 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], k))).join(',')})`;
}
function rug(cx, cy) {
  ell(cx, cy, 330, 70, 'rgba(232,196,186,.75)');
  ctx.beginPath(); ctx.ellipse(cx, cy, 300, 58, 0, 0, TAU); ctx.strokeStyle = 'rgba(255,248,240,.6)'; ctx.lineWidth = 3; ctx.stroke();
}
function abstractBG(a, hx, hy) { // screen space dreamy field
  if (a <= 0) return;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a;
  let g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#F6EEE6'); g.addColorStop(.5, '#F1DED8'); g.addColorStop(1, '#DCE6EE');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const blobs = [[.25, .3, 520, 'rgba(214,227,236,'], [.8, .55, 600, 'rgba(241,215,207,'], [.4, .82, 560, 'rgba(168,193,212,'], [.75, .18, 420, 'rgba(240,229,213,']];
  blobs.forEach(([bx, by, br, col], i) => {
    const x = bx * W + Math.sin(T * .35 + i * 2) * 60, y = by * H + Math.cos(T * .3 + i) * 50;
    const rg = ctx.createRadialGradient(x, y, 0, x, y, br);
    rg.addColorStop(0, col + '.85)'); rg.addColorStop(1, col + '0)');
    ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  });
  // concentric breathing rings around the child
  for (let i = 0; i < 4; i++) {
    const rr = 260 + i * 120 + Math.sin(T * 1.2 - i * .7) * 10;
    ctx.beginPath(); ctx.arc(hx, hy, rr, 0, TAU);
    ctx.strokeStyle = `rgba(255,255,255,${.35 - i * .07})`; ctx.lineWidth = 2; ctx.stroke();
  }
  const rg = ctx.createRadialGradient(hx, hy, 0, hx, hy, 420);
  rg.addColorStop(0, 'rgba(255,252,247,.75)'); rg.addColorStop(1, 'rgba(255,252,247,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  ctx.restore();
}

// ---------- overlays
let NOISE = [];
function makeNoise() {
  for (let n = 0; n < 4; n++) {
    const c = document.createElement('canvas'); c.width = 540; c.height = 960;
    const x = c.getContext('2d'), id = x.createImageData(540, 960);
    for (let i = 0; i < id.data.length; i += 4) { const v = Math.random() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    x.putImageData(id, 0, 0); NOISE.push(c);
  }
}
function grain(amount) {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = amount;
  ctx.drawImage(NOISE[Math.floor(T * 12) % 4], 0, 0, W, H); ctx.restore();
}
function vignette(a, col = '70,45,30') {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  const g = ctx.createRadialGradient(W / 2, H * .5, H * .28, W / 2, H * .5, H * .78);
  g.addColorStop(0, `rgba(${col},0)`); g.addColorStop(1, `rgba(${col},${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
}
function grade(color, a, mode = 'soft-light') {
  if (a <= 0) return;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = mode; ctx.globalAlpha = a;
  ctx.fillStyle = color; ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ---------- text
function txt(lines, o) {
  const { x = 540, y, size, font = 'Corm', weight = 600, style = 'normal', color = P.deep, alpha = 1, lh = 1.1, spacing = 0, blur = 0, rise = 0 } = o;
  if (alpha <= 0.002) return;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha;
  if (blur > .2) ctx.filter = `blur(${blur}px)`;
  ctx.font = `${style} ${weight} ${size}px ${font}`; ctx.letterSpacing = spacing + 'px';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = color;
  lines.forEach((l, i) => ctx.fillText(l, x + spacing / 2, y + rise + i * size * lh));
  ctx.restore();
}
function reveal(t, a, o1, o2) { // alpha/blur/rise for an elegant blur-in
  const i = eout(seg(t, a, a + .8)), out = S(t, o1, o2);
  return { alpha: i * (1 - out), blur: (1 - i) * 12 + out * 6, rise: (1 - i) * 26 - out * 10 };
}

// ---------- layers (for fading whole characters without seams)
function inLayer(alpha, fn) {
  if (alpha <= .003) return;
  if (alpha >= .997) { fn(); return; }
  const prev = ctx, lc = lay.getContext('2d');
  lc.setTransform(1, 0, 0, 1, 0, 0); lc.clearRect(0, 0, W, H);
  ctx = lc; ctx.setTransform(prev.getTransform()); fn();
  ctx = prev; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha; ctx.drawImage(lay, 0, 0); ctx.restore();
}

// =====================================================================
// SCENES 1–4: one continuous story shot
// =====================================================================
const CHILD = { x: 640, y: 1450, s: 1.1 };
function camMatrix(z, fx, fy) { return new DOMMatrix().translate(W / 2, 1000).scale(z).translate(-fx, -fy); }

function story(t) {
  const A = S(t, 3.7, 5.3) * (1 - S(t, 14.3, 15.9));
  const warm = S(t, 16.2, 19.6);
  const [z, fx, fy] = keys(t, [[0, 1.03, 545, 950], [4.0, 1.30, 612, 1120], [5.6, 1.52, 640, 1180], [14.2, 1.6, 640, 1192], [16.0, 1.24, 470, 1175], [21.5, 1.31, 478, 1190]]);
  CAM = camMatrix(z, fx, fy);
  const zb = 1 + (z - 1) * .55;
  const CAMB = camMatrix(zb, lerp(540, fx, .7), lerp(1000, fy, .7));
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = P.wall; ctx.fillRect(0, 0, W, H);

  // room (parallax background)
  ctx.setTransform(CAMB); room(warm);
  ctx.setTransform(CAM);
  inLayer(1 - A, () => rug(CHILD.x, CHILD.y + 10));
  const headW = CAM.transformPoint(new DOMPoint(CHILD.x, CHILD.y - 1.1 * 248));
  abstractBG(A, headW.x, headW.y);
  ctx.setTransform(CAM);

  // ----- parent
  const pv = clamp(1 - S(t, 3.5, 4.7) + S(t, 14.7, 15.6));
  let pp = mix(P_CONF, P_STAND, S(t, 9, 10));
  const kn = S(t, 15.7, 17.1);
  pp = mix(pp, P_KNEEL, kn);
  pp.tilt += Math.sin(T * 1.7) * .025 * (1 - kn);
  if (t < 9) { pp.aL = [70 + Math.sin(T * 2.2) * 6, -132 + Math.sin(T * 2.2) * 5]; }
  // reach to the child's shoulder
  const childShoulder = [CHILD.x - 1.1 * 50, CHILD.y - 1.1 * (34 + 136) + 6];
  const reach = S(t, 16.9, 18.0);
  const px = 300, py = lerp(1430, 1500, kn);
  let pe = mix({ bi: -.35, ba: .55, mc: -.4, mo: 0, eo: 1, tr: 0, lx: .8, ly: .7 }, { bi: .45, ba: 0, mc: -.15, mo: 0, eo: 1, tr: 0, lx: .9, ly: .6 }, S(t, 9, 10));
  pe = mix(pe, { bi: .3, ba: 0, mc: .55, mo: 0, eo: .82, tr: 0, lx: 1, ly: .5 }, S(t, 17.2, 19.0));
  pe.blink = blinkAt(t, [2.3, 16.4, 19.9]);
  if (reach > 0) pp.aR = { blend: reach, rest: pp.aR, target: childShoulder };
  inLayer(pv, () => drawParent(px, py, .95, pp, pe));

  // ----- child
  const cry = { bi: 1, ba: 0, mc: -1, mo: .62, eo: .55, tr: 1, lx: 0, ly: .4 };
  const look = { bi: .7, ba: 0, mc: -.5, mo: .12, eo: .9, tr: .55, lx: 0, ly: -.5 };
  const talk = { bi: .45, ba: 0, mc: -.25, mo: .2, eo: 1, tr: .3, lx: 0, ly: -.3 };
  const frus = { bi: -.85, ba: 0, mc: -.85, mo: .38, eo: .72, tr: .45, lx: 0, ly: .2 };
  const sad = { bi: .9, ba: 0, mc: -.7, mo: .22, eo: .62, tr: .7, lx: -.4, ly: .3 };
  const calm = { bi: .12, ba: 0, mc: .6, mo: 0, eo: .92, tr: 0, lx: -1, ly: -.35 };
  let ce = cry;
  ce = mix(ce, look, S(t, 4.2, 5.6));
  ce = mix(ce, talk, S(t, 9.0, 9.6));
  ce = mix(ce, frus, S(t, 12.0, 12.6));
  ce = mix(ce, sad, S(t, 14.3, 15.6));
  ce = mix(ce, calm, S(t, 17.4, 19.6));
  if (t > 5 && t < 9.4) ce.lx = Math.sin((t - 5) * 1.3) * .9 * S(t, 5, 5.8);
  if (t > 9.5 && t < 12.2) ce.mo = .12 + .32 * Math.abs(Math.sin((t - 9.5) * 6.5)) * (1 - S(t, 11.9, 12.2));
  ce.blink = blinkAt(t, [6.1, 8.2, 10.8, 18.6]);

  let cp = C_SIT;
  cp = mix(cp, C_TALK, S(t, 9.3, 9.9) * (1 - S(t, 11.9, 12.4)));
  if (t > 9.6 && t < 12.2) { const g = Math.sin((t - 9.6) * 4.2) * 14; cp.aL = [cp.aL[0] + g, cp.aL[1] - g]; cp.aR = [cp.aR[0] - g, cp.aR[1] + g]; }
  // tantrum beats: arms up then pound down
  const pound = tt => { const a = seg(t, tt, tt + .28), b = seg(t, tt + .28, tt + .42); return eout(a) * (1 - eio(b)); };
  const up = Math.max(pound(12.55), pound(13.2), pound(13.85)) * (1 - S(t, 14.1, 14.4));
  if (t > 12.3 && t < 14.6) { cp = Object.assign({}, cp); cp.aL = mix(cp.aL, [-30, -70], up); cp.aR = mix(cp.aR, [30, -70], up); }
  cp = mix(cp, C_LAP, S(t, 17.6, 19.4));
  const sob = (1 - S(t, 4.4, 6)) + (S(t, 14.3, 15) * (1 - S(t, 17.5, 19)) * .6);
  cp = Object.assign({}, cp);
  cp.shake = Math.sin(T * 11) * 2.2 * sob;
  cp.bob = -Math.abs(Math.sin(T * 5.5)) * 5 * sob;
  cp.tilt = Math.sin(T * 1.6) * .05 * sob + (-.13) * S(t, 17.6, 19.6) + Math.sin(T * 2) * .02;
  cp.lean = -.04 * S(t, 17.6, 19.6);
  drawChild(CHILD.x, CHILD.y, CHILD.s, cp, ce);

  // ----- emotional symbols (scene 2)
  const hw = [CHILD.x, CHILD.y - CHILD.s * 248];
  SYMS.forEach((sy, i) => {
    const a0 = 5.0 + i * .34;
    const k = eback(seg(t, a0, a0 + .7)), out = S(t, 8.9, 9.6);
    if (k <= 0 || out >= 1) return;
    const ang = (sy.ang + Math.sin(T * .6 + i) * 4) * Math.PI / 180;
    const rad = 232 + Math.sin(T * .9 + i * 1.7) * 8 + out * 40;
    const x = hw[0] + Math.cos(ang) * rad, y = hw[1] + Math.sin(ang) * rad + Math.sin(T * 1.3 + i) * 6;
    ctx.save(); ctx.setTransform(CAM); ctx.translate(x, y); ctx.scale(.74 * k, .74 * k);
    ctx.globalAlpha = clamp(seg(t, a0, a0 + .5)) * (1 - out);
    ctx.shadowColor = 'rgba(80,60,40,.10)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8;
    circ(0, 0, 74, sy.col); ctx.shadowColor = 'transparent';
    ctx.beginPath(); ctx.arc(0, 0, 74, 0, TAU); ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 2.5; ctx.stroke();
    ctx.strokeStyle = P.deep; ctx.lineWidth = 4.5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    sy.f(clamp(seg(t, a0 + .2, a0 + 1.4)));
    ctx.restore();
  });

  // ----- trying to speak: bubbles that dissolve (scene 3)
  const mouthW = [CHILD.x, CHILD.y - CHILD.s * 190];
  const BUB = [[9.6, 790, 1015, 1], [10.45, 488, 990, -1], [11.3, 700, 905, 1]];
  BUB.forEach(([t0, bx, by, sd], i) => {
    const life = t - t0; if (life < 0 || life > 1.55) return;
    const grow = eback(seg(life, 0, .45)), pop = seg(life, 1.0, 1.5);
    ctx.save(); ctx.setTransform(CAM);
    if (pop <= 0) {
      ctx.translate(bx, by); ctx.scale(grow, grow); ctx.globalAlpha = clamp(life / .25);
      ctx.beginPath(); ctx.roundRect(-92, -58, 184, 116, 50);
      ctx.moveTo(-sd * 30, 50); ctx.lineTo(-sd * 64, 92); ctx.lineTo(-sd * 6, 56);
      ctx.fillStyle = 'rgba(255,252,247,.92)'; ctx.fill();
      ctx.strokeStyle = 'rgba(31,58,95,.55)'; ctx.lineWidth = 3; ctx.stroke();
      ctx.strokeStyle = P.deep; ctx.lineWidth = 4.5; ctx.lineCap = 'round';
      const pr = clamp(life / .9);
      if (i === 0) { // tangled line
        ctx.beginPath(); for (let j = 0; j <= 60 * pr; j++) { const u = j / 60; const xx = -60 + u * 120, yy = Math.sin(u * 19) * 14 * Math.sin(u * 3.1); j ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.stroke();
      } else if (i === 1) { // stuttering dots
        for (let j = 0; j < 3; j++) { const on = clamp((pr - j * .25) * 4); circ(-36 + j * 36, Math.sin(T * 8 + j) * 4, 9 * on, P.deep); }
      } else { // knot
        ctx.save(); ctx.scale(1.25, 1.1); iconScribble(pr); ctx.restore();
      }
    } else { // dissolve into particles
      for (let j = 0; j < 14; j++) {
        const a = rnd(j + i * 20) * TAU, sp = 60 + rnd(j + 7 + i * 20) * 120;
        const xx = bx + Math.cos(a) * sp * eout(pop), yy = by + Math.sin(a) * sp * eout(pop) + pop * 40;
        ctx.globalAlpha = (1 - pop) * .8; circ(xx, yy, (4 + 6 * rnd(j + 3)) * (1 - pop * .6), j % 2 ? P.pink : P.blueM);
      }
    }
    ctx.restore();
  });
  // behaviour: impact ripples on the floor + tension marks
  [12.97, 13.62, 14.27].forEach(t0 => {
    const u = seg(t, t0, t0 + 1.0); if (u <= 0 || u >= 1) return;
    ctx.save(); ctx.setTransform(CAM);
    ctx.beginPath(); ctx.ellipse(CHILD.x, CHILD.y + 6, 170 + 260 * eout(u), 34 + 52 * eout(u), 0, 0, TAU);
    ctx.strokeStyle = `rgba(31,58,95,${.45 * (1 - u)})`; ctx.lineWidth = 4; ctx.stroke();
    ctx.restore();
  });
  const tense = S(t, 12.3, 12.7) * (1 - S(t, 14.2, 14.8));
  if (tense > 0) {
    ctx.save(); ctx.setTransform(CAM); ctx.strokeStyle = `rgba(185,119,111,${.8 * tense})`; ctx.lineWidth = 5; ctx.lineCap = 'round';
    for (let j = 0; j < 6; j++) {
      const a = (-150 + j * 24 + (j > 2 ? 48 : 0)) * Math.PI / 180, j2 = Math.sin(T * 14 + j) * 6;
      const r1 = 135 + j2, r2 = 165 + j2;
      ctx.beginPath(); ctx.moveTo(hw[0] + Math.cos(a) * r1, hw[1] + Math.sin(a) * r1); ctx.lineTo(hw[0] + Math.cos(a) * r2, hw[1] + Math.sin(a) * r2); ctx.stroke();
    }
    ctx.restore();
  }

  // ----- light & grade
  grade('#9FB9D0', .28 * (1 - S(t, 3.5, 5)) * (1 - A)); // slightly cool, tense opening
  if (warm > 0) {
    ctx.save(); ctx.setTransform(CAM);
    const g = ctx.createRadialGradient(560, 1150, 40, 560, 1150, 760);
    g.addColorStop(0, `rgba(255,214,170,${.42 * warm})`); g.addColorStop(1, 'rgba(255,214,170,0)');
    ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = g; ctx.fillRect(-600, 0, 2400, 2400);
    ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = .35 * warm;
    const g2 = ctx.createRadialGradient(840, 760, 10, 840, 760, 700);
    g2.addColorStop(0, 'rgba(255,226,190,.9)'); g2.addColorStop(1, 'rgba(255,226,190,0)');
    ctx.fillStyle = g2; ctx.fillRect(-600, 0, 2400, 2400);
    ctx.restore();
  }
  vignette(.16);

  // ----- text
  let r = reveal(t, .45, 3.35, 3.85);
  txt(['É SÓ BIRRA?'], { y: 372, size: 122, weight: 600, spacing: 7, color: P.deep, ...r });
  r = reveal(t, 5.3, 8.7, 9.2);
  txt(['Nem sempre.'], { y: 372, size: 118, weight: 500, style: 'italic', color: P.deep, ...r });
}

function blinkAt(t, list) { let b = 0; list.forEach(t0 => { const u = (t - t0) / .16; if (u > 0 && u < 1) b = Math.max(b, Math.sin(u * Math.PI)); }); return b; }

// =====================================================================
// SCENE 5: heart ↔ brain
// =====================================================================
const brainPts = (() => {
  const pts = [];
  for (let i = 0; i <= 220; i++) {
    const th = i / 220 * TAU;
    const bump = 9 * Math.pow(Math.abs(Math.sin(th * 4.5)), .7);
    const rx = 128 + bump, ry = 96 + bump;
    pts.push([Math.cos(th) * rx, Math.sin(th) * ry * (Math.sin(th) > 0 ? .86 : 1)]);
  }
  return pts;
})();
const sulci = [
  [[-6, -100], [-14, -60], [4, -30], [-8, 10], [6, 50], [0, 80]],
  [[-100, -30], [-70, -46], [-52, -14], [-80, 18], [-56, 46]],
  [[100, -24], [72, -48], [54, -14], [84, 14], [62, 50]],
  [[-40, -84], [-36, -50], [-60, -66]],
  [[40, -86], [44, -52], [64, -70]],
  [[-30, 30], [-20, 60], [-44, 70]],
  [[34, 26], [24, 62], [48, 70]],
];
function partialPath(pts, pr) {
  const n = Math.max(1, Math.floor((pts.length - 1) * pr));
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i <= n; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.stroke();
}
function bez(p0, p1, p2, p3, n = 120) {
  const out = [];
  for (let i = 0; i <= n; i++) { const u = i / n, v = 1 - u;
    out.push([v * v * v * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u * u * u * p3[0], v * v * v * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u * u * u * p3[1]]); }
  return out;
}
function smoothPts(arr, n = 14) { // catmull-rom-ish densify
  const out = [];
  for (let i = 0; i < arr.length - 1; i++) {
    const p0 = arr[Math.max(0, i - 1)], p1 = arr[i], p2 = arr[i + 1], p3 = arr[Math.min(arr.length - 1, i + 2)];
    for (let j = 0; j < n; j++) { const u = j / n, u2 = u * u, u3 = u2 * u;
      out.push([0, 1].map(k => .5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u3))); }
  }
  out.push(arr[arr.length - 1]); return out;
}
const sulciS = sulci.map(s => smoothPts(s));
const LINK = bez([540, 1395], [600, 1320], [470, 1250], [540, 1168]);

function scene5(t) {
  const lt = t - 21; // local time
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const drift = Math.sin(t * .5) * 10;
  let g = ctx.createRadialGradient(540, 1100, 60, 540, 1100, 1250);
  g.addColorStop(0, '#2F5280'); g.addColorStop(.55, P.deep); g.addColorStop(1, '#162B48');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // floating motes
  for (let i = 0; i < 46; i++) {
    const x = rnd(i) * W + Math.sin(t * .4 + i) * 20, y = ((rnd(i + 100) * H - t * (12 + 20 * rnd(i + 50))) % H + H) % H;
    circ(x, y, 1.5 + 2.5 * rnd(i + 9), `rgba(247,240,230,${.08 + .18 * rnd(i + 3)})`);
  }
  const z = 1 + .05 * eio(seg(t, 20.6, 26.4));
  ctx.setTransform(new DOMMatrix().translate(540, 1150).scale(z).translate(-540, -1150 + drift * .3));
  // bust silhouette
  ctx.beginPath(); ctx.arc(540, 1050, 215, 0, TAU);
  ctx.moveTo(240, 1800); ctx.bezierCurveTo(240, 1500, 330, 1380, 492, 1350); ctx.lineTo(500, 1258); ctx.lineTo(580, 1258); ctx.lineTo(588, 1350);
  ctx.bezierCurveTo(750, 1380, 840, 1500, 840, 1800); ctx.closePath();
  const sil = eout(seg(t, 20.8, 21.8));
  ctx.fillStyle = `rgba(255,255,255,${.045 * sil})`; ctx.fill();
  ctx.strokeStyle = `rgba(247,240,230,${.22 * sil})`; ctx.lineWidth = 2.5; ctx.stroke();
  // halo behind head
  const halo = ctx.createRadialGradient(540, 1050, 40, 540, 1050, 330);
  halo.addColorStop(0, `rgba(214,227,236,${.16 * sil})`); halo.addColorStop(1, 'rgba(214,227,236,0)');
  ctx.fillStyle = halo; ctx.fillRect(0, 600, W, 900);

  const pulseHit = (() => { let m = 0; for (let k = 0; k < 5; k++) { const t0 = 23.0 + k * .75 + .55; const u = (t - t0) / .5; if (u > 0 && u < 1) m = Math.max(m, Math.sin(u * Math.PI)); } return m; })();
  // brain
  ctx.save(); ctx.translate(540, 1040); ctx.scale(.98, .98);
  ctx.shadowColor = `rgba(214,227,236,${.7 + .3 * pulseHit})`; ctx.shadowBlur = 18 + 22 * pulseHit;
  ctx.strokeStyle = `rgba(247,240,230,${.92})`; ctx.lineWidth = 5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const bp = eio(seg(t, 21.1, 22.4));
  if (bp > 0) partialPath(brainPts, bp);
  sulciS.forEach((s, i) => { const sp = eio(seg(t, 21.6 + i * .08, 22.6 + i * .08)); if (sp > 0) partialPath(s, sp); });
  ctx.restore();
  // heart
  const hp = eback(seg(t, 21.5, 22.3)), beat = 1 + .06 * Math.max(0, Math.sin(t * 2 * Math.PI * 1.1)) * S(t, 22.5, 23);
  if (hp > 0) {
    ctx.save(); ctx.translate(540, 1440); ctx.scale(hp * beat, hp * beat);
    const hg = ctx.createRadialGradient(0, 0, 10, 0, 0, 190);
    hg.addColorStop(0, 'rgba(221,168,159,.45)'); hg.addColorStop(1, 'rgba(221,168,159,0)');
    ctx.fillStyle = hg; ctx.fillRect(-200, -200, 400, 400);
    ctx.shadowColor = 'rgba(241,215,207,.9)'; ctx.shadowBlur = 30;
    heartPath(4.4, 0, 6); ctx.fillStyle = P.pink; ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(255,240,234,.9)'; ctx.stroke();
    ctx.restore();
  }
  // connecting line
  const lp = eio(seg(t, 22.2, 23.1));
  if (lp > 0) {
    ctx.save(); ctx.shadowColor = 'rgba(255,226,200,.95)'; ctx.shadowBlur = 22;
    ctx.strokeStyle = 'rgba(255,240,228,.95)'; ctx.lineWidth = 4.5; ctx.lineCap = 'round';
    partialPath(LINK, lp); ctx.restore();
    // pulses travelling heart → brain
    for (let k = 0; k < 5; k++) {
      const u = (t - (23.0 + k * .75)) / .6; if (u <= 0 || u >= 1) continue;
      const idx = Math.floor(eio(u) * (LINK.length - 1)); const [x, y] = LINK[idx];
      ctx.save(); ctx.shadowColor = 'rgba(255,230,210,1)'; ctx.shadowBlur = 30;
      circ(x, y, 9, 'rgba(255,248,240,.95)'); ctx.restore();
    }
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  vignette(.35, '8,18,34');
  let r = reveal(t, 21.35, 23.45, 23.9);
  txt(['Acolher não é', 'permitir tudo.'], { y: 360, size: 96, weight: 600, color: P.cream, lh: 1.08, ...r });
  r = reveal(t, 23.85, 25.6, 26.2);
  txt(['É ensinar a criança', 'a entender o que sente.'], { y: 360, size: 84, weight: 500, style: 'italic', color: P.cream, lh: 1.12, ...r });
}

// =====================================================================
// SCENE 6: final frame
// =====================================================================
function scene6(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  let g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#F8F2E9'); g.addColorStop(1, '#F2E8DA');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const lt = t - 26;
  // soft sun disc & arcs
  const sr = 300 + Math.sin(t * .8) * 6;
  const sg = ctx.createRadialGradient(540, 1170, 0, 540, 1170, sr);
  sg.addColorStop(0, 'rgba(214,227,236,.95)'); sg.addColorStop(.7, 'rgba(214,227,236,.75)'); sg.addColorStop(1, 'rgba(214,227,236,0)');
  ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(540, 1170, sr, 0, TAU); ctx.fill();
  ctx.beginPath(); ctx.arc(540, 1170, sr + 46, Math.PI * 1.08, Math.PI * 1.92); ctx.strokeStyle = 'rgba(221,168,159,.55)'; ctx.lineWidth = 3; ctx.stroke();
  // ground line
  ctx.beginPath(); ctx.moveTo(170, 1420); ctx.lineTo(910, 1420); ctx.strokeStyle = 'rgba(185,160,130,.35)'; ctx.lineWidth = 2; ctx.stroke();
  // drifting dots
  for (let i = 0; i < 16; i++) {
    const x = 120 + rnd(i + 300) * 840 + Math.sin(t * .6 + i) * 14;
    const y = 900 + rnd(i + 400) * 520 - ((t * 14 * (0.5 + rnd(i))) % 120);
    circ(x, y, 3 + 4 * rnd(i + 500), i % 2 ? 'rgba(221,168,159,.45)' : 'rgba(142,171,194,.45)');
  }
  // walking pair (back view, receding)
  const recede = eio(seg(t, 25.6, 30));
  const sc = lerp(1, .9, recede), gy = lerp(1424, 1402, recede);
  const ph = t * 2 * Math.PI * .95;
  const step = (amp, off) => Math.max(0, Math.sin(ph + off)) * amp;
  const handW = [548, gy - 312 * sc];
  CAM = new DOMMatrix();
  const pPose = Object.assign({}, P_STAND, {
    fL: [-42, -8 - step(16, 0)], fR: [42, -8 - step(16, Math.PI)], kL: 1, kR: -1,
    bob: -Math.abs(Math.sin(ph)) * 6, tilt: .03, eL: 1, eR: -1,
    aL: [-14 + Math.sin(ph) * 16, 262], aR: { w: handW },
  });
  // parent is mirrored in back view: their right hand is on our left; keep layout simple: parent on left
  drawParent(470, gy, .7 * sc, pPose, {}, true);
  const cPose = Object.assign({}, C_STAND, {
    fL: [-30, -6 - step(11, Math.PI)], fR: [30, -6 - step(11, 0)],
    bob: -Math.abs(Math.sin(ph + .5)) * 5, tilt: -.06,
    aL: { w: handW }, aR: [12 + Math.sin(ph + Math.PI) * 14, 120], eL: -1, eR: -1,
  });
  drawChild(645, gy, .8 * sc, cPose, {}, true);
  // clasped hands on top
  circ(handW[0], handW[1], 13, P.pSkin);

  // text
  const a1 = reveal(t, 26.5, 99, 100), a2 = reveal(t, 26.8, 99, 100), a3 = reveal(t, 27.1, 99, 100);
  txt(['Por trás de todo'], { y: 360, size: 86, weight: 600, color: P.deep, ...a1 });
  txt(['comportamento,'], { y: 455, size: 86, weight: 600, color: P.deep, ...a2 });
  // mixed-style last line
  ctx.save(); ctx.globalAlpha = a3.alpha; if (a3.blur > .2) ctx.filter = `blur(${a3.blur}px)`;
  ctx.textBaseline = 'middle';
  ctx.font = `normal 600 86px Corm`; const w1 = ctx.measureText('existe uma ').width;
  ctx.font = `italic 600 90px Corm`; const w2 = ctx.measureText('necessidade.').width;
  const x0 = 540 - (w1 + w2) / 2, yy = 550 + a3.rise;
  ctx.textAlign = 'left'; ctx.font = `normal 600 86px Corm`; ctx.fillStyle = P.deep; ctx.fillText('existe uma ', x0, yy);
  ctx.font = `italic 600 90px Corm`; ctx.fillStyle = P.pinkD; ctx.fillText('necessidade.', x0 + w1, yy);
  ctx.restore();
  const a4 = reveal(t, 27.7, 99, 100);
  ctx.save(); ctx.globalAlpha = a4.alpha; ctx.beginPath(); const lw = 70 * eout(seg(t, 27.7, 28.5));
  ctx.moveTo(540 - lw, 648); ctx.lineTo(540 + lw, 648); ctx.strokeStyle = P.pink; ctx.lineWidth = 2.5; ctx.stroke(); ctx.restore();
  txt(['PSICOLOGIA INFANTIL'], { y: 708, size: 30, font: 'Mont', weight: 500, spacing: 9, color: P.deep2, ...a4 });
  vignette(.08);
}

// soft circular reveal of a buffer (k: 0 → 1)
function maskRadial(buf, k, cx, cy) {
  const c = buf.getContext('2d'); c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  c.globalCompositeOperation = 'destination-in';
  const R = k * 1900, f = 420;
  const g = c.createRadialGradient(cx, cy, Math.max(0, R - f), cx, cy, R + 1);
  g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore();
}

// =====================================================================
function renderAt(t) {
  T = t;
  const parts = [];
  // [scene fn, start, end] with crossfade windows
  const X1 = [20.4, 21.5], X2 = [25.6, 26.4];
  const draw = (fn, buf) => { ctx = buf.getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); fn(t); };
  main.setTransform(1, 0, 0, 1, 0, 0);
  if (t < X1[0]) { draw(story, bufA); main.drawImage(bufA, 0, 0); }
  else if (t < X1[1]) { draw(story, bufA); draw(scene5, bufB); maskRadial(bufB, eio(seg(t, X1[0], X1[1])), 560, 1180); main.drawImage(bufA, 0, 0); main.drawImage(bufB, 0, 0); }
  else if (t < X2[0]) { draw(scene5, bufA); main.drawImage(bufA, 0, 0); }
  else if (t < X2[1]) { draw(scene5, bufA); draw(scene6, bufB); main.drawImage(bufA, 0, 0); main.globalAlpha = eio(seg(t, X2[0], X2[1])); main.drawImage(bufB, 0, 0); main.globalAlpha = 1; }
  else { draw(scene6, bufA); main.drawImage(bufA, 0, 0); }
  ctx = main; T = t; grain(.07);
  // open from / close to nothing harsh: tiny fade-in at start
  if (t < .35) { main.fillStyle = `rgba(247,240,230,${1 - t / .35})`; main.fillRect(0, 0, W, H); }
}

window.ready = (async () => {
  makeNoise();
  await Promise.all([document.fonts.load('600 40px Corm'), document.fonts.load('italic 500 40px Corm'), document.fonts.load('500 20px Mont')]);
  window.renderAt = renderAt;
  if (location.hash === '#play') {
    document.body.classList.add('preview');
    const t0 = performance.now();
    const loop = () => { renderAt(((performance.now() - t0) / 1000) % DUR); requestAnimationFrame(loop); };
    loop();
  } else renderAt(0.6);
  return true;
})();
