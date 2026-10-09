// SILENCE ONE — product launch motion graphics (1080x1920, 30 fps, 30 s) + LUMARC CTA.
// window.renderAt(t) draws one deterministic frame; opened normally, the page plays itself in real time.
const W = 1080, H = 1920, DUR = 30;
const ctx = document.getElementById('c').getContext('2d');
const $ = id => document.getElementById(id);
const IMG = { hero: $('hero'), macro: $('macro'), logo: $('logo'), o0: $('o0'), o1: $('o1'), o2: $('o2'), o3: $('o3') };
const GOLD = '#e6c896', GOLD2 = '#b8925a', INK = '#050506', MUTED = '#9a978f', WHITE = '#f6f3ec';
const C = { bg: '#0e0e14', muted: '#a6a6b8', g1: '#4f6bff', g2: '#6a55ff', g3: '#9a4dff' };

// ---------- math
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const eout = x => { x = clamp(x); return 1 - Math.pow(1 - x, 3); };
const expo = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
const eback = x => { x = clamp(x); const c1 = 1.6, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const TAU = Math.PI * 2;

// ---------- text
function font(size, w = 400) { return `${w} ${size}px Outfit`; }
function goldGrad(x0, x1, shift = 0) {
  const g = ctx.createLinearGradient(x0, 0, x1, 0);
  g.addColorStop(0, GOLD2); g.addColorStop(clamp(.35 + shift), '#f7e2b8'); g.addColorStop(clamp(.55 + shift), GOLD); g.addColorStop(1, GOLD2); return g;
}
function brandGrad(x0, y0, x1, y1) { const g = ctx.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, C.g1); g.addColorStop(.45, C.g2); g.addColorStop(1, C.g3); return g; }
function text(s, x, y, o = {}) {
  const { size = 60, w = 400, color = WHITE, align = 'center', alpha = 1, blur = 0, gold = false, spacing = 0, shadow = 0, shine = 0 } = o;
  if (alpha <= .003) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  ctx.font = font(size, w); ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.letterSpacing = spacing + 'px';
  if (blur > .3) ctx.filter = `blur(${blur}px)`;
  let fill = color;
  if (gold) { const tw = ctx.measureText(s).width; const x0 = align === 'center' ? x - tw / 2 : align === 'right' ? x - tw : x; fill = goldGrad(x0, x0 + tw, shine); }
  if (shadow) { ctx.shadowColor = 'rgba(230,200,150,.45)'; ctx.shadowBlur = shadow; }
  ctx.fillStyle = fill; ctx.fillText(s, x, y);
  ctx.restore();
}
function maskText(s, x, y, k, o = {}) {
  const size = o.size || 60;
  ctx.save(); ctx.beginPath(); ctx.rect(0, y - size * 1.05, W, size * 1.4); ctx.clip();
  text(s, x, y + (1 - expo(k)) * size * 1.25, o); ctx.restore();
}
// per-letter reveal (blur → sharp, tracking tightens)
function letters(s, cx, y, t0, t, o = {}) {
  const { size = 200, w = 200, sp0 = 70, sp1 = 26, stagger = .07, dur = .55, gold = false } = o;
  const k = eout(seg(t, t0, t0 + stagger * s.length + dur));
  const sp = lerp(sp0, sp1, k);
  ctx.save(); ctx.font = font(size, w);
  const ws = [...s].map(ch => ctx.measureText(ch).width); const tw = ws.reduce((a, b) => a + b, 0) + sp * (s.length - 1);
  let x = cx - tw / 2;
  [...s].forEach((ch, i) => {
    const li = eout(seg(t, t0 + i * stagger, t0 + i * stagger + dur));
    text(ch, x + ws[i] / 2, y + (1 - li) * 40, { size, w, alpha: li, blur: (1 - li) * 16, gold });
    x += ws[i] + sp;
  });
  ctx.restore();
}

// ---------- backgrounds / fx
function bgInk(t, warm = 1) {
  ctx.fillStyle = INK; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, H * .47, 0, W / 2, H * .47, 900);
  g.addColorStop(0, `rgba(230,200,150,${.07 * warm})`); g.addColorStop(1, 'rgba(230,200,150,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function dust(t, n = 60, a = 1) {
  for (let i = 0; i < n; i++) {
    const x = rnd(i) * W + Math.sin(t * .6 + i) * 18, y = ((rnd(i + 50) * H - t * (14 + 30 * rnd(i + 7))) % H + H) % H;
    const s = 1.5 + 3 * rnd(i + 2), al = (.1 + .4 * rnd(i + 5)) * a * (.6 + .4 * Math.sin(t * 2 + i));
    ctx.fillStyle = `rgba(240,215,170,${al})`; ctx.beginPath(); ctx.arc(x, y, s, 0, TAU); ctx.fill();
  }
}
function sweep(x, y, w, h, k, a = .22, ang = .35) {  // diagonal light band
  if (k <= 0 || k >= 1) return;
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip(); ctx.globalCompositeOperation = 'lighter';
  const cx = lerp(x - w * .6, x + w * 1.6, k);
  ctx.translate(cx, y + h / 2); ctx.rotate(ang);
  const g = ctx.createLinearGradient(-140, 0, 140, 0);
  g.addColorStop(0, 'rgba(255,240,210,0)'); g.addColorStop(.5, `rgba(255,240,210,${a})`); g.addColorStop(1, 'rgba(255,240,210,0)');
  ctx.fillStyle = g; ctx.fillRect(-140, -h * 1.5, 280, h * 3); ctx.restore();
}
// soft elliptical alpha edge so the black plates never show a rectangle
const FEATHER = new Map();
function feathered(im, sx = 0, sy = 0, sw = im.naturalWidth, sh = im.naturalHeight, key = im.id) {
  if (FEATHER.has(key)) return FEATHER.get(key);
  const c = document.createElement('canvas'); c.width = sw; c.height = sh; const x = c.getContext('2d');
  x.drawImage(im, sx, sy, sw, sh, 0, 0, sw, sh);
  x.globalCompositeOperation = 'destination-in'; x.translate(sw / 2, sh / 2); x.scale(1, sh / sw);
  const g = x.createRadialGradient(0, 0, sw * .3, 0, 0, sw * .5); g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = g; x.fillRect(-sw / 2, -sw / 2, sw, sw);
  FEATHER.set(key, c); return c;
}
function product(im, cx, cy, w, alpha = 1, flip = false) {  // product shots are on black → 'lighten' melts them into the scene
  if (!im.naturalWidth || alpha <= 0) return;
  const h = w * im.naturalHeight / im.naturalWidth; im = feathered(im);
  ctx.save(); ctx.globalAlpha *= alpha; ctx.globalCompositeOperation = 'lighten';
  if (flip) { ctx.translate(cx, cy); ctx.scale(1, -1); ctx.drawImage(im, -w / 2, -h / 2, w, h); }
  else ctx.drawImage(im, cx - w / 2, cy - h / 2, w, h);
  ctx.restore();
}
function orbitFrame(f, cx, cy, size, alpha = 1) {
  const draw = (i, a) => {
    i = clamp(Math.round(i), 0, 39); const sh = IMG['o' + Math.floor(i / 10)], j = i % 10;
    if (!sh.naturalWidth) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.globalCompositeOperation = 'lighten';
    ctx.drawImage(feathered(sh, (j % 5) * 520, Math.floor(j / 5) * 520, 520, 520, 'o' + i), cx - size / 2, cy - size / 2, size, size); ctx.restore();
  };
  const f0 = Math.floor(f), fr = f - f0;
  draw(f0, alpha); if (fr > .01) draw(f0 + 1, alpha * fr);
}
function vignette(a = .55) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * .28, W / 2, H / 2, H * .78);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
let NOISE = [];
function makeNoise() {
  for (let n = 0; n < 4; n++) {
    const c = document.createElement('canvas'); c.width = 540; c.height = 960; const x = c.getContext('2d'); const d = x.createImageData(540, 960);
    let s = n * 9973 + 1;
    for (let i = 0; i < d.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = s % 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
    x.putImageData(d, 0, 0); NOISE.push(c);
  }
}
function grain(a = .05) {
  ctx.save(); ctx.globalAlpha = a; ctx.globalCompositeOperation = 'overlay';
  ctx.drawImage(NOISE[Math.floor(T * 30) % 4], 0, 0, W, H); ctx.restore();
}
function flash(a, rgb = '255,244,225') { if (a <= 0) return; ctx.fillStyle = `rgba(${rgb},${a})`; ctx.fillRect(0, 0, W, H); }
function line(x0, y0, x1, y1, k, col = GOLD, lw = 2, a = 1) {
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = col; ctx.lineWidth = lw;
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(lerp(x0, x1, k), lerp(y0, y1, k)); ctx.stroke(); ctx.restore();
}
let T = 0;

// ---------- 1: intro (0 – 3)
function sIntro(t) {
  bgInk(t, .6);
  const out = eio(seg(t, 2.55, 3.0));
  ctx.save(); ctx.translate(W / 2, 960); const z = 1 + 2.2 * out * out; ctx.scale(z, z); ctx.translate(-W / 2, -960);
  ctx.globalAlpha = 1 - out;
  const lw = 880 * expo(seg(t, .15, .85));
  const g = ctx.createLinearGradient(W / 2 - lw / 2, 0, W / 2 + lw / 2, 0);
  g.addColorStop(0, 'rgba(230,200,150,0)'); g.addColorStop(.5, GOLD); g.addColorStop(1, 'rgba(230,200,150,0)');
  ctx.fillStyle = g; ctx.fillRect(W / 2 - lw / 2, 1040, lw, 2);
  const px = W / 2 + Math.sin(t * 2.2) * lw * .45;  // spark running along the line
  const sg = ctx.createRadialGradient(px, 1041, 0, px, 1041, 36); sg.addColorStop(0, `rgba(255,240,210,${.8 * seg(t, .3, .8)})`); sg.addColorStop(1, 'rgba(255,240,210,0)');
  ctx.save(); ctx.scale(1, 1); ctx.fillStyle = sg; ctx.fillRect(px - 36, 1005, 72, 72); ctx.restore();
  text('INTRODUCING', W / 2, 800, { size: 30, w: 400, spacing: 16, color: MUTED, alpha: eout(seg(t, .55, 1.0)) });
  letters('SILENCE', W / 2, 990, .85, t, { size: 158, w: 200, sp0: 60, sp1: 20 });
  letters('ONE', W / 2, 1160, 1.55, t, { size: 64, w: 300, sp0: 70, sp1: 36, gold: true, stagger: .1 });
  ctx.restore();
  dust(t, 40, .6);
}

// ---------- 2: hero reveal (3 – 8)
function sHero(t) {
  const lt = t - 3; bgInk(t, 1);
  const k = eout(seg(lt, 0, 2.4)), s = lerp(1.2, 1.0, k) + .015 * lt;
  const out = eio(seg(lt, 4.65, 5.0));
  product(IMG.hero, W / 2, 1010 - 30 * k, 1000 * s * (1 + .15 * out), eout(seg(lt, 0, 1.1)) * (1 - out));
  sweep(40, 460, 1000, 1100, seg(lt, .35, 1.7), .2);
  sweep(40, 460, 1000, 1100, seg(lt, 3.3, 4.4), .12);
  dust(t, 70, .9);
  maskText('Hear nothing.', W / 2, 300, seg(lt, 1.2, 1.7), { size: 100, w: 250 });
  maskText('Feel everything.', W / 2, 415, seg(lt, 1.6, 2.1), { size: 100, w: 250, gold: true, shine: Math.sin(lt) * .2 });
  const a = eout(seg(lt, 2.3, 2.8)) * (1 - out);
  line(W / 2 - 160, 1648, W / 2 + 160, 1648, eout(seg(lt, 2.3, 2.9)), GOLD, 1.5, .7 * (1 - out));
  text('SILENCE ONE', W / 2, 1715, { size: 34, w: 500, spacing: 16, alpha: a });
  text('Adaptive noise-cancelling headphones', W / 2, 1770, { size: 28, w: 300, color: MUTED, alpha: a, spacing: 1 });
}

// ---------- 3: turntable + specs (8 – 14)
const SPECS = [
  { t: .6, num: '−42', unit: 'dB', label: 'ADAPTIVE NOISE CANCELLING', side: 'L', y: 330, px: 395, py: 820 },
  { t: 1.5, num: 40, unit: 'h', label: 'BATTERY LIFE', side: 'R', y: 330, px: 700, py: 690 },
  { t: 2.4, num: '360°', unit: '', label: 'SPATIAL AUDIO', side: 'L', y: 1560, px: 405, py: 1180 },
  { t: 3.3, num: 250, unit: 'g', label: 'FEATHERWEIGHT BUILD', side: 'R', y: 1560, px: 690, py: 1150 },
];
function sOrbit(t) {
  const lt = t - 8; bgInk(t, .9);
  const out = eio(seg(lt, 5.6, 6.0));
  const cx = W / 2, cy = 960;
  // HUD rings
  ctx.save(); ctx.globalAlpha = (1 - out) * .9; ctx.strokeStyle = 'rgba(230,200,150,.28)'; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.arc(cx, cy, 470, -Math.PI / 2, -Math.PI / 2 + TAU * eio(seg(lt, 0, 1.2))); ctx.stroke();
  ctx.setLineDash([3, 14]); ctx.lineDashOffset = -lt * 40; ctx.strokeStyle = 'rgba(230,200,150,.35)';
  ctx.beginPath(); ctx.arc(cx, cy, 430, 0, TAU * eout(seg(lt, .2, 1.2))); ctx.stroke(); ctx.setLineDash([]);
  for (let i = 0; i < 72; i++) {
    const a = i / 72 * TAU + lt * .08, r0 = i % 6 === 0 ? 488 : 496; if (i / 72 > eout(seg(lt, .1, 1.3))) continue;
    ctx.strokeStyle = `rgba(230,200,150,${i % 6 === 0 ? .55 : .2})`; ctx.beginPath();
    ctx.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0); ctx.lineTo(cx + Math.cos(a) * 508, cy + Math.sin(a) * 508); ctx.stroke();
  }
  ctx.restore();
  const f = 39 * eio(seg(lt, 0, 5.8));
  orbitFrame(f, cx, cy, 800 * (1 + .04 * eout(seg(lt, 0, 6))) * (1 + .1 * out), eout(seg(lt, 0, .5)) * (1 - out));
  dust(t, 45, .7);
  SPECS.forEach((s, i) => {
    const k = seg(lt, s.t, s.t + .9), a = eout(seg(lt, s.t, s.t + .3)) * (1 - out);
    if (a <= 0) return;
    const L = s.side === 'L', tx = L ? 90 : 990, ly = s.y + (s.y < 900 ? 150 : -150);
    // anchor dot with pulse
    ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(s.px, s.py, 7, 0, TAU); ctx.fill();
    const pr = 7 + 30 * ((lt - s.t) % 1.2) / 1.2; ctx.strokeStyle = `rgba(230,200,150,${.6 * (1 - ((lt - s.t) % 1.2) / 1.2)})`; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(s.px, s.py, pr, 0, TAU); ctx.stroke(); ctx.restore();
    // leader: dot → elbow → under label
    const ex = L ? 300 : 780;
    line(s.px, s.py, ex, ly, eout(seg(k, 0, .45)), GOLD, 1.5, a * .8);
    if (k > .45) line(ex, ly, tx, ly, eout(seg(k, .45, .8)), GOLD, 1.5, a * .8);
    const ta = eout(seg(k, .5, 1)) * (1 - out), al = L ? 'left' : 'right';
    const n = typeof s.num === 'number' ? Math.round(s.num * eout(seg(lt, s.t + .4, s.t + 1.4))) + '' : s.num;
    const ny = s.y < 900 ? ly - 40 : ly + 120;
    ctx.save(); ctx.font = font(120, 200); const nw = ctx.measureText(n).width; ctx.restore();
    ctx.save(); ctx.font = font(44, 300); const uw = s.unit ? ctx.measureText(s.unit).width + 12 : 0; ctx.restore();
    text(n, L ? tx : tx - uw, ny, { size: 120, w: 200, align: al, alpha: ta });
    if (s.unit) text(s.unit, L ? tx + nw + 12 : tx, ny, { size: 44, w: 300, align: 'left' === al ? 'left' : 'right', gold: true, alpha: ta });
    text(s.label, tx, s.y < 900 ? ly + 46 : ly - 22, { size: 24, w: 500, spacing: 4, color: MUTED, align: al, alpha: ta });
  });
}

// ---------- 4: materials (14 – 18.5)
function sMaterials(t) {
  const lt = t - 14; bgInk(t, .7);
  const out = eio(seg(lt, 4.15, 4.5));
  ctx.save(); ctx.globalAlpha = 1 - out;
  maskText('Crafted,', W / 2, 300, seg(lt, .15, .6), { size: 104, w: 200 });
  maskText('not assembled.', W / 2, 418, seg(lt, .35, .8), { size: 104, w: 200, gold: true });
  // macro window: opens from a gold line
  const x = 60, y = 540, w = 960, h = 860, k = eio(seg(lt, .2, 1.1));
  const hh = h * k;
  ctx.save(); ctx.beginPath(); ctx.roundRect(x, y + (h - hh) / 2, w, Math.max(2, hh), 34); ctx.clip();
  ctx.fillStyle = '#000'; ctx.fillRect(x, y, w, h);
  if (IMG.macro.naturalWidth) {
    const s = lerp(1.18, 1.0, eout(seg(lt, .2, 4.4))), iw = w * 1.04 * s, ih = iw * IMG.macro.naturalHeight / IMG.macro.naturalWidth;
    ctx.drawImage(IMG.macro, x + w / 2 - iw / 2 - 30 * seg(lt, 0, 4.5), y + h / 2 - ih / 2, iw, ih);
  }
  ctx.restore();
  sweep(x, y, w, h, seg(lt, 1.2, 2.4), .18, -.5);
  ctx.save(); ctx.strokeStyle = 'rgba(230,200,150,.35)'; ctx.lineWidth = 1.5; ctx.globalAlpha = k;
  ctx.beginPath(); ctx.roundRect(x, y + (h - hh) / 2, w, Math.max(2, hh), 34); ctx.stroke(); ctx.restore();
  const MAT = [['01', 'Protein leather cushions'], ['02', 'Champagne anodized aluminum'], ['03', 'Woven acoustic fabric']];
  MAT.forEach(([n, s], i) => {
    const a = eout(seg(lt, 1.3 + i * .35, 1.8 + i * .35)), yy = 1500 + i * 110, dx = (1 - a) * -60;
    text(n, 90 + dx, yy, { size: 30, w: 500, gold: true, align: 'left', alpha: a, spacing: 2 });
    text(s, 170 + dx, yy, { size: 40, w: 300, align: 'left', alpha: a });
    line(90, yy + 36, 990, yy + 36, eout(seg(lt, 1.4 + i * .35, 2.2 + i * .35)), 'rgba(230,200,150,.25)', 1);
  });
  ctx.restore();
}

// ---------- 5: the silence demo (18.5 – 23)
const ANC = 1.5;  // lt when the switch flips
function sSilence(t) {
  const lt = t - 18.5; bgInk(t, lt > ANC ? 1 : .3);
  const out = eio(seg(lt, 4.15, 4.5)), on = eout(seg(lt, ANC, ANC + .7));
  const shake = lt < ANC ? (1 - seg(lt, 0, .2) * 0) * 6 : 0;
  ctx.save(); ctx.translate((rnd(Math.floor(t * 30)) - .5) * shake, (rnd(Math.floor(t * 30) + 7) - .5) * shake); ctx.globalAlpha = 1 - out;
  product(IMG.hero, W / 2, 1000, 760, .18 + .5 * on);
  // waveform
  const N = 90, bw = W / N;
  for (let i = 0; i < N; i++) {
    const x = i * bw + bw / 2, env = Math.sin(Math.PI * (i + .5) / N);
    const noise = (Math.sin(t * 23 + i * 1.7) * .5 + Math.sin(t * 37 + i * .6) * .3 + (rnd(i + Math.floor(t * 30) * 13) - .5) * .9);
    const calm = Math.sin(t * 3 + i * .25) * .04;
    const amp = lerp(Math.abs(noise) * 330 * env + 20, Math.abs(calm) * 120 * env + 2, on);
    ctx.fillStyle = on > .5 ? `rgba(230,200,150,${.5 + .4 * env})` : `rgba(${235 - 30 * on},${150 + 60 * on},${140 + 20 * on},${.55 + .35 * env})`;
    ctx.fillRect(x - bw * .28, 960 - amp, bw * .56, amp * 2);
  }
  // copy
  text('The world is loud.', W / 2, 330, { size: 90, w: 250, alpha: eout(seg(lt, .1, .5)) * (1 - eout(seg(lt, ANC, ANC + .3))), blur: 0 });
  maskText('Silence it.', W / 2, 330, seg(lt, ANC + .25, ANC + .75), { size: 110, w: 250, gold: true });
  const db = lt < ANC ? 82 + Math.round(rnd(Math.floor(t * 8)) * 6) : Math.round(lerp(85, 43, eout(seg(lt, ANC, ANC + 1.2))));
  text(db + ' dB', W / 2, 1420, { size: 64, w: 200, color: lt < ANC ? '#e8a090' : GOLD, alpha: eout(seg(lt, .2, .5)) });
  text(lt < ANC ? 'AMBIENT NOISE' : 'WHAT REACHES YOU', W / 2, 1470, { size: 22, w: 500, spacing: 5, color: MUTED, alpha: eout(seg(lt, .2, .5)) });
  // ANC switch
  const sx = W / 2, sy = 1620, sw = 220, sh = 104, kk = eback(seg(lt, ANC, ANC + .4));
  ctx.save(); ctx.globalAlpha *= eout(seg(lt, .3, .6));
  ctx.beginPath(); ctx.roundRect(sx - sw / 2, sy - sh / 2, sw, sh, sh / 2);
  ctx.fillStyle = on > .01 ? `rgba(230,200,150,${.15 + .75 * on})` : 'rgba(255,255,255,.1)'; ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,.25)'; ctx.lineWidth = 2; ctx.stroke();
  const kx = lerp(sx - sw / 2 + sh / 2, sx + sw / 2 - sh / 2, kk);
  ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 20; ctx.fillStyle = WHITE; ctx.beginPath(); ctx.arc(kx, sy, sh / 2 - 10, 0, TAU); ctx.fill();
  ctx.restore();
  text('ANC', sx - sw / 2 - 40, sy + 14, { size: 40, w: 500, align: 'right', alpha: eout(seg(lt, .3, .6)) });
  text(lt < ANC ? 'OFF' : 'ON', sx + sw / 2 + 40, sy + 14, { size: 40, w: 500, align: 'left', gold: lt >= ANC, color: MUTED, alpha: eout(seg(lt, .3, .6)) });
  ctx.restore();
  if (lt > ANC) flash(.35 * (1 - seg(lt, ANC, ANC + .25)), '255,240,215');
}

// ---------- 6: final hero (23 – 26.5)
function sFinal(t) {
  const lt = t - 23; bgInk(t, 1.2);
  const out = eio(seg(lt, 3.15, 3.5)), k = eout(seg(lt, 0, 1.6)), s = lerp(1.1, 1.0, k);
  const pw = 860 * s, cy = 800;
  const ph = pw * 1075 / 1000;
  // floor reflection
  ctx.save(); ctx.beginPath(); ctx.rect(0, cy + ph / 2 - 20, W, 420); ctx.clip();
  product(IMG.hero, W / 2, cy + ph - 40, pw, .16 * k * (1 - out), true);
  const fg = ctx.createLinearGradient(0, cy + ph / 2 - 20, 0, cy + ph / 2 + 300); fg.addColorStop(0, 'rgba(5,5,6,0)'); fg.addColorStop(1, 'rgba(5,5,6,1)');
  ctx.fillStyle = fg; ctx.fillRect(0, cy + ph / 2 - 20, W, 420); ctx.restore();
  product(IMG.hero, W / 2, cy, pw, eout(seg(lt, 0, .5)) * (1 - out));
  sweep(80, 300, 920, 1000, seg(lt, .4, 1.6), .2);
  dust(t, 60, 1);
  ctx.save(); ctx.globalAlpha = 1 - out;
  letters('SILENCE', W / 2, 1530, .5, t - 23, { size: 150, w: 200, sp0: 60, sp1: 26, stagger: .05, dur: .45 });
  text('ONE', W / 2, 1610, { size: 46, w: 300, spacing: 30, gold: true, shine: Math.sin(lt * 1.5) * .25, alpha: eout(seg(lt, 1.0, 1.4)) });
  text('Hear nothing. Feel everything.', W / 2, 1700, { size: 34, w: 300, color: MUTED, alpha: eout(seg(lt, 1.4, 1.8)), spacing: 1 });
  text('$349  ·  AVAILABLE NOW', W / 2, 1775, { size: 28, w: 500, spacing: 6, gold: true, alpha: eout(seg(lt, 1.7, 2.1)) });
  ctx.restore();
  flash(.55 * (1 - seg(lt, 0, .3)), '255,240,215');
}

// ---------- 7: LUMARC CTA (26.5 – 30)
function bgBrand(t) {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  [[.2, .25, 700, '59,91,255'], [.85, .7, 760, '139,61,255'], [.5, 1.05, 650, '106,85,255']].forEach(([x, y, r, c], i) => {
    const cx = x * W + Math.sin(t * .4 + i * 2) * 90, cy = y * H + Math.cos(t * .33 + i) * 80;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r); g.addColorStop(0, `rgba(${c},.24)`); g.addColorStop(1, `rgba(${c},0)`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  });
  ctx.strokeStyle = 'rgba(255,255,255,0.035)'; ctx.lineWidth = 1; const off = (t * 18) % 90; ctx.beginPath();
  for (let x = 0; x <= W; x += 90) { ctx.moveTo(x + .5, 0); ctx.lineTo(x + .5, H); }
  for (let y = -90; y <= H; y += 90) { ctx.moveTo(0, y + off + .5); ctx.lineTo(W, y + off + .5); }
  ctx.stroke();
}
function sCTA(t) {
  const lt = t - 26.5; bgBrand(t);
  const k = eout(seg(lt, .1, .7));
  if (IMG.logo.naturalWidth) {
    ctx.save(); ctx.globalAlpha = k; const lw = 700 * (.9 + .1 * k), lh = lw * IMG.logo.naturalHeight / IMG.logo.naturalWidth;
    ctx.drawImage(IMG.logo, W / 2 - lw / 2, 620 - lh / 2, lw, lh); ctx.restore();
  }
  maskText('Want your product', W / 2, 950, seg(lt, .5, .85), { size: 72, w: 400 });
  maskText('presented like this?', W / 2, 1042, seg(lt, .6, .95), { size: 72, w: 400 });
  const b = eback(seg(lt, .9, 1.3)), pulse = 1 + .03 * Math.max(0, Math.sin(lt * 5));
  ctx.save(); ctx.translate(W / 2, 1225); ctx.scale(b * pulse, b * pulse);
  ctx.shadowColor = 'rgba(122,85,255,.8)'; ctx.shadowBlur = 50; ctx.beginPath(); ctx.roundRect(-270, -62, 540, 124, 62); ctx.fillStyle = brandGrad(-270, 0, 270, 0); ctx.fill(); ctx.shadowBlur = 0;
  text('DM us "VIDEO"', 0, 16, { size: 48, w: 500 }); ctx.restore();
  text('Be seen. Be remembered.', W / 2, 1400, { size: 40, w: 300, color: C.muted, spacing: 2, alpha: eout(seg(lt, 1.2, 1.6)) });
  text('@lumarc_studio  ·  slumarc.com', W / 2, 1470, { size: 40, w: 400, color: C.muted, alpha: eout(seg(lt, 1.35, 1.75)) });
}

// =====================================================================
const CUTS = [3, 8, 14, 18.5, 23, 26.5];
function renderAt(t) {
  T = t; ctx.save();
  if (t < 3) sIntro(t);
  else if (t < 8) sHero(t);
  else if (t < 14) sOrbit(t);
  else if (t < 18.5) sMaterials(t);
  else if (t < 23) sSilence(t);
  else if (t < 26.5) sFinal(t);
  else sCTA(t);
  CUTS.forEach(c => { const d = 1 - Math.abs(t - c) / .1; if (d > 0 && c !== 23) flash(.35 * d, '5,5,6'); });
  vignette(t < 26.5 ? .55 : .45);
  grain(.055);
  ctx.restore();
}

window.ready = (async () => {
  makeNoise();
  await Promise.all(['200', '250', '300', '400', '500'].map(w => document.fonts.load(`${w} 40px Outfit`)));
  await Promise.all(Object.values(IMG).map(im => im.complete ? 1 : new Promise(r => { im.onload = im.onerror = r; })));
  window.renderAt = renderAt; renderAt(0); return true;
})();

// live playback when opened in a browser (render.cjs sets window.__RENDER)
window.ready.then(() => {
  if (window.__RENDER) return;
  const cv = $('c'), au = $('music'), btn = $('play');
  const fit = () => { const s = Math.min(innerWidth / W, innerHeight / H); cv.style.width = W * s + 'px'; cv.style.height = H * s + 'px'; };
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
