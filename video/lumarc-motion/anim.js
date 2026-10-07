// LUMARC motion graphics reel — "E se ao invés de apresentar sua empresa assim..." (1080x1920, 30s)
// window.renderAt(t) draws one deterministic frame.
const W = 1080, H = 1920;
const ctx = document.getElementById('c').getContext('2d');
const IMG = { before: document.getElementById('before'), after: document.getElementById('after'), logo: document.getElementById('logo') };
const C = { bg: '#0e0e14', bg2: '#12121b', bg3: '#181826', white: '#faf9f6', muted: '#a6a6b8', blue: '#3b5bff', violet: '#8b3dff', g1: '#4f6bff', g2: '#6a55ff', g3: '#9a4dff' };
let T = 0;

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
const inOut = (t, a, b, fi = .35, fo = .3) => eout(seg(t, a, a + fi)) * (1 - eio(seg(t, b - fo, b)));

// ---------- drawing helpers
function grad(x0, y0, x1, y1, a = C.g1, m = C.g2, b = C.g3) {
  const g = ctx.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, a); g.addColorStop(.45, m); g.addColorStop(1, b); return g;
}
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function glass(x, y, w, h, r = 28, a = 1) {
  ctx.save(); ctx.globalAlpha *= a;
  rr(x, y, w, h, r); ctx.fillStyle = 'rgba(255,255,255,0.055)'; ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.14)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.restore();
}
function font(size, w = 400) { return `${w} ${size}px Outfit`; }
function text(s, x, y, o = {}) {
  const { size = 60, w = 400, color = C.white, align = 'center', alpha = 1, blur = 0, gradient = false, spacing = 0, shadow = 0 } = o;
  if (alpha <= .003) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  ctx.font = font(size, w); ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.letterSpacing = spacing + 'px';
  if (blur > .3) ctx.filter = `blur(${blur}px)`;
  let fill = color;
  if (gradient) { const tw = ctx.measureText(s).width; const x0 = align === 'center' ? x - tw / 2 : align === 'right' ? x - tw : x; fill = grad(x0, y - size, x0 + tw, y); }
  if (shadow) { ctx.shadowColor = gradient ? 'rgba(122,85,255,.75)' : 'rgba(0,0,0,.6)'; ctx.shadowBlur = shadow; }
  ctx.fillStyle = fill; ctx.fillText(s, x, y);
  ctx.restore();
}
// text that rises from behind a mask line
function maskText(s, x, y, k, o = {}) {
  const size = o.size || 60;
  ctx.save(); ctx.beginPath(); ctx.rect(0, y - size * 1.05, W, size * 1.35); ctx.clip();
  text(s, x, y + (1 - expo(k)) * size * 1.2, o); ctx.restore();
}
function fitSize(s, w, size, max) { ctx.font = font(size, w); const tw = ctx.measureText(s).width; return tw > max ? size * max / tw : size; }

// ---------- background
function bgDark(t, glow = 1) {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  // drifting glow orbs
  const orbs = [[.2, .25, 700, '59,91,255'], [.85, .7, 760, '139,61,255'], [.5, 1.05, 650, '106,85,255']];
  orbs.forEach(([x, y, r, c], i) => {
    const cx = x * W + Math.sin(t * .4 + i * 2) * 90, cy = y * H + Math.cos(t * .33 + i) * 80;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    g.addColorStop(0, `rgba(${c},${.22 * glow})`); g.addColorStop(1, `rgba(${c},0)`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  });
  // grid
  ctx.strokeStyle = 'rgba(255,255,255,0.035)'; ctx.lineWidth = 1;
  const off = (t * 18) % 90;
  ctx.beginPath();
  for (let x = 0; x <= W; x += 90) { ctx.moveTo(x + .5, 0); ctx.lineTo(x + .5, H); }
  for (let y = -90; y <= H; y += 90) { ctx.moveTo(0, y + off + .5); ctx.lineTo(W, y + off + .5); }
  ctx.stroke();
  // dust
  for (let i = 0; i < 70; i++) {
    const x = rnd(i) * W + Math.sin(t * .5 + i) * 12, y = ((rnd(i + 99) * H - t * (20 + 40 * rnd(i + 7))) % H + H) % H;
    ctx.fillStyle = `rgba(${rnd(i + 3) > .5 ? '143,162,255' : '184,140,255'},${.15 + .35 * rnd(i + 5)})`;
    ctx.fillRect(x, y, 2 + 2 * rnd(i + 2), 2 + 2 * rnd(i + 2));
  }
}
function vignette(a = .5) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * .3, W / 2, H / 2, H * .75);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
let NOISE = [];
function makeNoise() {
  for (let n = 0; n < 4; n++) {
    const c = document.createElement('canvas'); c.width = 540; c.height = 960; const x = c.getContext('2d'); const d = x.createImageData(540, 960);
    for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
    x.putImageData(d, 0, 0); NOISE.push(c);
  }
}
function grain(a) { ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = a; ctx.drawImage(NOISE[Math.floor(T * 15) % 4], 0, 0, W, H); ctx.restore(); }
function flash(a, col = '255,255,255') { if (a > 0) { ctx.fillStyle = `rgba(${col},${a})`; ctx.fillRect(0, 0, W, H); } }

// ---------- logo rings (vector, animated)
function rings(cx, cy, R, prog, spin = 0, alpha = 1) {
  ctx.save(); ctx.globalAlpha *= alpha; ctx.translate(cx, cy);
  const lw = R * .085;
  const defs = [[-.62 + spin * .3, 1, .40 + .08 * Math.sin(T * 1.3)], [.18 - spin * .25, .86, .44 + .07 * Math.cos(T * 1.1)]];
  defs.forEach(([rot, s, sq], i) => {
    const p = clamp(prog * 1.15 - i * .15);
    if (p <= 0) return;
    ctx.save(); ctx.rotate(rot);
    const g = ctx.createLinearGradient(-R * s, 0, R * s, 0);
    g.addColorStop(0, i ? C.violet : C.blue); g.addColorStop(1, i ? '#b88cff' : '#6a8bff');
    ctx.strokeStyle = g; ctx.lineWidth = lw; ctx.lineCap = 'round';
    ctx.shadowColor = i ? 'rgba(139,61,255,.9)' : 'rgba(59,91,255,.9)'; ctx.shadowBlur = R * .25;
    ctx.beginPath(); ctx.ellipse(0, 0, R * s, R * s * sq, 0, -Math.PI / 2, -Math.PI / 2 + TAU * eio(p)); ctx.stroke();
    ctx.shadowBlur = 0; ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = lw * .25;
    ctx.beginPath(); ctx.ellipse(0, -lw * .15, R * s, R * s * sq, 0, -Math.PI / 2, -Math.PI / 2 + TAU * eio(p)); ctx.stroke();
    ctx.restore();
  });
  // star flare at the crossing
  const f = eout(seg(prog, .75, 1));
  if (f > 0) {
    const sx = -R * .08, sy = -R * .05, s = R * (.55 + .1 * Math.sin(T * 5)) * f;
    const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, s);
    g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.15, 'rgba(200,190,255,.8)'); g.addColorStop(1, 'rgba(140,110,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(sx, sy, s, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,.8)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(sx - s * 1.6, sy); ctx.lineTo(sx + s * 1.6, sy); ctx.moveTo(sx, sy - s * 1.6); ctx.lineTo(sx, sy + s * 1.6); ctx.stroke();
  }
  ctx.restore();
}

// ---------- scene 0: the "before" (generic AI flyer)
function sceneBefore(t) {
  ctx.fillStyle = '#1b1b1f'; ctx.fillRect(0, 0, W, H);
  const z = 1 + .03 * t / 4;
  const sz = 960 * z;
  let glitch = seg(t, 4.0, 4.45), collapse = eio(seg(t, 4.4, 4.62));
  ctx.save(); ctx.translate(W / 2, 1010); ctx.scale(1 - collapse, 1 - collapse);
  if (IMG.before.complete && IMG.before.naturalWidth) {
    if (glitch > 0) { // sliced RGB glitch
      for (let i = 0; i < 14; i++) {
        const sy = i * sz / 14, dx = (rnd(i + Math.floor(t * 30)) - .5) * 160 * glitch;
        ctx.drawImage(IMG.before, 0, i * IMG.before.naturalHeight / 14, IMG.before.naturalWidth, IMG.before.naturalHeight / 14, -sz / 2 + dx, -sz / 2 + sy, sz, sz / 14 + 1);
      }
      ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = .5 * glitch;
      ctx.drawImage(IMG.before, -sz / 2 + 18 * glitch, -sz / 2, sz, sz);
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    } else ctx.drawImage(IMG.before, -sz / 2, -sz / 2, sz, sz);
  } else { ctx.fillStyle = '#c9a23a'; ctx.fillRect(-sz / 2, -sz / 2, sz, sz); }
  ctx.restore();
  // top chip
  const a = eout(seg(t, .15, .5)) * (1 - seg(t, 3.9, 4.1));
  if (a > 0) {
    ctx.save(); ctx.globalAlpha = a; ctx.font = font(50, 500);
    const l1 = 'E se ao invés de apresentar', l2 = 'sua empresa assim...';
    const w = Math.max(ctx.measureText(l1).width, ctx.measureText(l2).width) + 80;
    rr(W / 2 - w / 2, 270, w, 150, 28); ctx.fillStyle = '#fff'; ctx.fill(); ctx.restore();
    text(l1, W / 2, 333, { size: 50, w: 500, color: '#111', alpha: a });
    text(l2, W / 2, 395, { size: 50, w: 500, color: '#111', alpha: a });
  }
  text('(igual a todo mundo)', W / 2, 1600, { size: 44, w: 300, color: '#9a9aa6', alpha: eout(seg(t, 1.6, 2.0)) * (1 - seg(t, 3.9, 4.1)) });
  // collapse into a point of light
  const pt = seg(t, 4.5, 4.75);
  if (pt > 0) {
    const r = 260 * Math.sin(pt * Math.PI);
    const g = ctx.createRadialGradient(W / 2, 1010, 0, W / 2, 1010, r + 1);
    g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.3, 'rgba(160,140,255,.7)'); g.addColorStop(1, 'rgba(100,80,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
}

// ---------- transition text "...você apresentasse ASSIM?"
function sceneAssim(t) {
  ctx.fillStyle = '#07070b'; ctx.fillRect(0, 0, W, H);
  maskText('...você apresentasse', W / 2, 860, seg(t, 4.55, 4.85), { size: 78, w: 300, color: C.white });
  if (t > 4.72) {
    const k = seg(t, 4.72, 4.86), sc = 1.8 - .8 * eout(k);
    ctx.save(); ctx.translate(W / 2 + (t < 4.95 ? (rnd(Math.floor(t * 60)) - .5) * 14 : 0), 1060); ctx.scale(sc, sc);
    text('ASSIM?', 0, 0, { size: 230, w: 700, gradient: true, shadow: 60 }); ctx.restore();
  }
}

// ---------- scene 1: logo reveal (5.0 - 8.0)
function sceneLogo(t) {
  const lt = t - 5;
  bgDark(t, eout(lt / .8));
  const pr = eout(seg(lt, .05, 1.3));
  const R = 250 * (1 + .04 * Math.sin(lt * 2)) * (1 - .25 * eio(seg(lt, 2.4, 3)));
  rings(W / 2, 880 - 120 * eio(seg(lt, 2.4, 3)), R, pr, Math.sin(lt * 1.4) * .3);
  // wordmark letters
  const word = 'lumarc';
  ctx.font = font(170, 300); const tw = ctx.measureText(word).width; let x = W / 2 - tw / 2;
  for (let i = 0; i < word.length; i++) {
    const k = seg(lt, 1.0 + i * .07, 1.45 + i * .07);
    const cw = ctx.measureText(word[i]).width;
    text(word[i], x + cw / 2, 1310 + (1 - expo(k)) * 60 - 80 * eio(seg(lt, 2.4, 3)), { size: 170, w: 300, alpha: k, blur: (1 - k) * 14 });
    x += cw;
  }
  text('Seja visto. Seja lembrado.', W / 2, 1420 - 80 * eio(seg(lt, 2.4, 3)), { size: 52, w: 300, color: C.muted, alpha: eout(seg(lt, 1.7, 2.1)), spacing: 2 });
  // shockwave ring at the drop
  const sw = seg(lt, 0, .9);
  if (sw > 0 && sw < 1) { ctx.beginPath(); ctx.arc(W / 2, 880, 100 + 900 * eout(sw), 0, TAU); ctx.strokeStyle = `rgba(143,120,255,${.6 * (1 - sw)})`; ctx.lineWidth = 6; ctx.stroke(); }
  flash(.85 * (1 - seg(lt, 0, .35)), '200,190,255');
}

// ---------- scene 2: headline + the scroll that stops (8.0 - 11.0)
function feedCard(x, y, w, h, i) {
  glass(x, y, w, h, 30);
  const hues = [[59, 91, 255], [139, 61, 255], [255, 120, 80], [40, 200, 170], [255, 90, 160]];
  const c1 = hues[i % 5], c2 = hues[(i + 2) % 5];
  const g = ctx.createLinearGradient(x, y, x + w, y + h * .6);
  g.addColorStop(0, `rgba(${c1},.85)`); g.addColorStop(1, `rgba(${c2},.75)`);
  rr(x + 22, y + 90, w - 44, h * .58, 18); ctx.fillStyle = g; ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.25)'; ctx.beginPath(); ctx.arc(x + 52, y + 46, 22, 0, TAU); ctx.fill();
  rr(x + 88, y + 34, 200, 22, 11); ctx.fill();
  rr(x + 22, y + h - 92, w * .6, 20, 10); ctx.fill(); rr(x + 22, y + h - 56, w * .4, 20, 10); ctx.fill();
}
function sceneHeadline(t) {
  const lt = t - 8;
  bgDark(t);
  // feed scrolling fast, then stopping at 9.5
  const stopT = 1.5;
  const v = lt < stopT ? 1 : 0;
  const pos = lt < stopT ? lt * 2600 : stopT * 2600 + 120 * (1 - Math.exp(-(lt - stopT) * 9)) * Math.cos((lt - stopT) * 14) * 0 + 0;
  const settle = lt >= stopT ? Math.exp(-(lt - stopT) * 7) * Math.sin((lt - stopT) * 22) * 40 : 0;
  const cardW = 760, cardH = 900, gap = 60;
  const base = -((pos) % (cardH + gap)) + settle;
  const blurN = lt < stopT ? 5 : 1;
  for (let b = 0; b < blurN; b++) {
    ctx.save(); ctx.globalAlpha = (lt < stopT ? .28 : .9) * eout(seg(lt, 0, .3));
    for (let k = -1; k < 4; k++) {
      const y = base + k * (cardH + gap) + b * 40 + 200;
      feedCard((W - cardW) / 2, y, cardW, cardH, k + Math.floor(pos / (cardH + gap)) + 7);
    }
    ctx.restore();
  }
  // dark scrim so type reads
  ctx.fillStyle = `rgba(10,10,16,${.55 * eout(seg(lt, stopT, stopT + .3))})`; ctx.fillRect(0, 0, W, H);
  if (lt >= stopT) { const k = seg(lt, stopT, stopT + .6); ctx.beginPath(); ctx.arc(W / 2, H / 2, 80 + 700 * eout(k), 0, TAU); ctx.strokeStyle = `rgba(143,120,255,${.5 * (1 - k)})`; ctx.lineWidth = 5; ctx.stroke(); }
  flash(.4 * (1 - seg(lt, stopT, stopT + .25)), '180,170,255');
  const out = eio(seg(lt, 2.75, 3));
  ctx.save(); ctx.globalAlpha = 1 - out;
  maskText('Conteúdo que faz', W / 2, 820, seg(lt, .15, .55), { size: 112, w: 400 });
  maskText('o seu negócio', W / 2, 950, seg(lt, .4, .8), { size: 112, w: 400 });
  ctx.save(); const s = 1 + .25 * (1 - eback(seg(lt, stopT, stopT + .45)));
  ctx.translate(W / 2, 1110); ctx.scale(lt >= stopT ? s : 1, lt >= stopT ? s : 1);
  text('parar o scroll.', 0, 0, { size: 128, w: 600, gradient: true, shadow: 40, alpha: eout(seg(lt, stopT, stopT + .15)) });
  ctx.restore(); ctx.restore();
}

// ---------- services (11.0 - 20.0)
const SERV = [
  ['Gestão de mídias sociais', 'Seu perfil ativo, todo mês.'],
  ['Artes e posts', 'Cara de marca grande.'],
  ['Carrosséis', 'Posts que ensinam, vendem e são salvos.'],
  ['Reels e vídeos', 'Vídeos que fazem parar.'],
  ['Edição de vídeo', 'Do bruto ao incrível.'],
  ['Sites sob medida', 'No ar em até 2 semanas.'],
];
const S0 = 11.0, SD = 1.5;
function gSocial(k, lt) { // posting calendar filling up
  const cw = 104, gx = W / 2 - 3.5 * cw, gy = 950;
  glass(gx - 30, gy - 110, cw * 7 + 60, cw * 5 + 140, 30);
  text('OUTUBRO', W / 2, gy - 45, { size: 34, w: 500, color: C.muted, spacing: 6 });
  for (let i = 0; i < 35; i++) {
    const r = Math.floor(i / 7), c = i % 7, x = gx + c * cw, y = gy + r * cw;
    rr(x + 8, y + 8, cw - 16, cw - 16, 16); ctx.fillStyle = 'rgba(255,255,255,.05)'; ctx.fill();
    const on = [1, 3, 5, 8, 10, 12, 15, 17, 19, 22, 24, 26, 29, 31, 33].indexOf(i);
    if (on >= 0) {
      const p = eback(seg(lt, .15 + on * .05, .4 + on * .05));
      if (p > 0) { ctx.save(); ctx.translate(x + cw / 2, y + cw / 2); ctx.scale(p, p); rr(-34, -34, 68, 68, 16); ctx.fillStyle = grad(-34, -34, 34, 34); ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-14, 0); ctx.lineTo(-3, 11); ctx.lineTo(16, -10); ctx.stroke(); ctx.restore(); }
    }
  }
}
function gArt(k, lt) { // a post layout snapping together
  const x = W / 2 - 330, y = 760, s = 660;
  glass(x, y, s, s, 34);
  const p = i => eback(seg(lt, .1 + i * .12, .55 + i * .12));
  ctx.save(); ctx.translate((1 - p(0)) * -300, 0); ctx.globalAlpha = clamp(p(0) * 2);
  ctx.beginPath(); ctx.arc(x + s * .68, y + s * .38, 170, 0, TAU); ctx.fillStyle = grad(x + 300, y, x + s, y + 400); ctx.fill(); ctx.restore();
  ctx.save(); ctx.translate(0, (1 - p(1)) * 260); ctx.globalAlpha = clamp(p(1) * 2);
  rr(x + 50, y + 70, 290, 46, 12); ctx.fillStyle = '#fff'; ctx.fill(); rr(x + 50, y + 135, 220, 46, 12); ctx.fill(); ctx.restore();
  ctx.save(); ctx.translate((1 - p(2)) * 300, 0); ctx.globalAlpha = clamp(p(2) * 2);
  rr(x + 50, y + 420, 400, 22, 11); ctx.fillStyle = 'rgba(255,255,255,.45)'; ctx.fill(); rr(x + 50, y + 462, 320, 22, 11); ctx.fill(); ctx.restore();
  ctx.save(); const q = p(3); ctx.translate(x + 150, y + 570); ctx.scale(q, q);
  rr(-100, -38, 200, 76, 38); ctx.fillStyle = grad(-100, 0, 100, 0); ctx.fill(); ctx.restore();
  // cursor
  const c = eout(seg(lt, .9, 1.2)); ctx.save(); ctx.translate(lerp(x + s + 60, x + 175, c), lerp(y + s + 60, y + 585, c));
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 44); ctx.lineTo(12, 33); ctx.lineTo(22, 54); ctx.lineTo(30, 50); ctx.lineTo(20, 30); ctx.lineTo(36, 30); ctx.closePath(); ctx.fill(); ctx.restore();
}
function gCarousel(k, lt) {
  const cw = 560, ch = 640, cy = 800;
  const idx = clamp((lt - .2) / .38, 0, 3), f = Math.floor(idx), fr = eio(idx - f), pos = f + fr;
  ctx.save(); ctx.beginPath(); ctx.rect(0, cy - 40, W, ch + 80); ctx.clip();
  for (let i = 0; i < 5; i++) {
    const x = W / 2 - cw / 2 + (i - pos) * (cw + 40);
    glass(x, cy, cw, ch, 30);
    const g = ctx.createLinearGradient(x, cy, x + cw, cy + ch);
    const cols = [[C.blue, C.violet], [C.violet, '#ff5aa0'], ['#25c8aa', C.blue], ['#ff8c50', C.violet], [C.blue, '#25c8aa']][i];
    g.addColorStop(0, cols[0]); g.addColorStop(1, cols[1]);
    rr(x + 30, cy + 30, cw - 60, ch * .55, 20); ctx.fillStyle = g; ctx.fill();
    text(String(i + 1).padStart(2, '0') + '/05', x + 60, cy + ch * .55 + 110, { size: 40, w: 500, align: 'left', color: C.white });
    ctx.fillStyle = 'rgba(255,255,255,.3)'; rr(x + 60, cy + ch * .55 + 140, cw - 160, 18, 9); ctx.fill(); rr(x + 60, cy + ch * .55 + 175, cw - 260, 18, 9); ctx.fill();
  }
  ctx.restore();
  for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.arc(W / 2 - 60 + i * 30, cy + ch + 60, Math.abs(i - pos) < .5 ? 9 : 6, 0, TAU); ctx.fillStyle = Math.abs(i - pos) < .5 ? C.white : 'rgba(255,255,255,.3)'; ctx.fill(); }
  // swipe hand hint
  const hx = W / 2 + 160 - ((lt * 2.6) % 1) * 240; ctx.beginPath(); ctx.arc(hx, cy + ch * .35, 34, 0, TAU); ctx.fillStyle = `rgba(255,255,255,${.25 * (1 - (lt * 2.6) % 1)})`; ctx.fill();
}
function gReel(k, lt) {
  const pw = 420, ph = 760, x = W / 2 - pw / 2, y = 730;
  rr(x - 14, y - 14, pw + 28, ph + 28, 64); ctx.fillStyle = '#1d1d29'; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.18)'; ctx.lineWidth = 3; ctx.stroke();
  ctx.save(); rr(x, y, pw, ph, 52); ctx.clip();
  const g = ctx.createLinearGradient(x, y + Math.sin(lt * 2) * 200, x + pw, y + ph);
  g.addColorStop(0, C.violet); g.addColorStop(.5, '#ff5aa0'); g.addColorStop(1, C.blue);
  ctx.fillStyle = g; ctx.fillRect(x, y, pw, ph);
  for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.arc(x + pw * rnd(i), y + ph * rnd(i + 9) - lt * 120 * (1 + rnd(i)), 60 + 80 * rnd(i + 3), 0, TAU); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fill(); }
  // progress bar
  rr(x + 30, y + ph - 40, pw - 60, 8, 4); ctx.fillStyle = 'rgba(255,255,255,.3)'; ctx.fill();
  rr(x + 30, y + ph - 40, (pw - 60) * clamp(lt / 1.4), 8, 4); ctx.fillStyle = '#fff'; ctx.fill();
  ctx.restore();
  // play button pop
  const p = eback(seg(lt, .1, .45)) * (1 - eio(seg(lt, .7, .9)));
  if (p > 0) { ctx.save(); ctx.translate(W / 2, y + ph / 2); ctx.scale(p, p); ctx.beginPath(); ctx.arc(0, 0, 70, 0, TAU); ctx.fillStyle = 'rgba(255,255,255,.25)'; ctx.fill();
    ctx.beginPath(); ctx.moveTo(-20, -32); ctx.lineTo(36, 0); ctx.lineTo(-20, 32); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill(); ctx.restore(); }
  // floating hearts
  for (let i = 0; i < 7; i++) {
    const u = seg(lt, .5 + i * .1, 1.3 + i * .1); if (u <= 0 || u >= 1) continue;
    const hx = x + pw - 60 + Math.sin(u * 6 + i) * 30, hy = y + ph - 160 - u * 420;
    ctx.save(); ctx.translate(hx, hy); ctx.scale(.9 + .4 * rnd(i), .9 + .4 * rnd(i)); ctx.globalAlpha = 1 - u;
    ctx.beginPath(); ctx.moveTo(0, 12); ctx.bezierCurveTo(-34, -12, -16, -38, 0, -20); ctx.bezierCurveTo(16, -38, 34, -12, 0, 12); ctx.fillStyle = '#ff4f7a'; ctx.fill(); ctx.restore();
  }
}
function gEdit(k, lt) {
  const x = 120, y = 820, w = W - 240, h = 520;
  glass(x, y, w, h, 30);
  // preview monitor strip
  const tracks = [[C.blue, [0, .32, .55, .8]], [C.violet, [.1, .45, .7]], ['#25c8aa', [0, .6]]];
  tracks.forEach(([col, starts], ti) => {
    const ty = y + 120 + ti * 120;
    text(['V1', 'V2', 'A1'][ti], x + 50, ty + 52, { size: 30, w: 500, color: C.muted, align: 'left' });
    starts.forEach((s0, ci) => {
      const s1 = ci + 1 < starts.length ? starts[ci + 1] - .02 : 1;
      const p = expo(seg(lt, .05 + ti * .1 + ci * .07, .45 + ti * .1 + ci * .07));
      const cx = x + 120 + (w - 160) * s0 + (1 - p) * 500, cwid = (w - 160) * (s1 - s0);
      ctx.save(); ctx.globalAlpha = p; rr(cx, ty, cwid, 76, 14); ctx.fillStyle = col; ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,.2)'; if (ti === 2) for (let b = 0; b < cwid / 10; b++) { const bh = 10 + 40 * Math.abs(Math.sin(b * .7 + ci)); ctx.fillRect(cx + 6 + b * 10, ty + 38 - bh / 2, 5, bh); }
      ctx.restore();
    });
  });
  // playhead
  const ph = x + 120 + (w - 160) * clamp((lt - .5) / .9);
  ctx.fillStyle = '#fff'; ctx.fillRect(ph - 2, y + 70, 4, h - 110); ctx.beginPath(); ctx.moveTo(ph - 16, y + 60); ctx.lineTo(ph + 16, y + 60); ctx.lineTo(ph, y + 84); ctx.closePath(); ctx.fill();
  // cut flash
  const cut = seg(lt, .95, 1.15); if (cut > 0 && cut < 1) { ctx.fillStyle = `rgba(255,255,255,${1 - cut})`; ctx.fillRect(x + 120 + (w - 160) * .55 - 4, y + 100, 8, 360); }
  text('00:00:' + String(Math.floor(clamp((lt - .5) / .9) * 24)).padStart(2, '0') + ':12', W / 2, y + 60, { size: 34, w: 500, color: C.muted, spacing: 3 });
}
function gSite(k, lt) {
  const x = 120, y = 740, w = W - 240, h = 760;
  glass(x, y, w, h, 30);
  ctx.fillStyle = 'rgba(255,255,255,.06)'; rr(x, y, w, 70, [30, 30, 0, 0]); ctx.fill();
  ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => { ctx.beginPath(); ctx.arc(x + 46 + i * 34, y + 35, 10, 0, TAU); ctx.fillStyle = c; ctx.fill(); });
  rr(x + 170, y + 18, w - 340, 34, 17); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fill();
  text('suaempresa.com', x + w / 2, y + 45, { size: 24, w: 400, color: C.muted });
  const p = i => expo(seg(lt, .1 + i * .13, .5 + i * .13));
  ctx.save(); ctx.globalAlpha = p(0); rr(x + 40, y + 110 + (1 - p(0)) * 60, w - 80, 280, 22); ctx.fillStyle = grad(x, y, x + w, y + 300); ctx.fill(); ctx.restore();
  ctx.save(); ctx.globalAlpha = p(1); ctx.fillStyle = '#fff'; rr(x + 80, y + 180, 380, 40, 10); ctx.fill(); rr(x + 80, y + 240, 280, 40, 10); ctx.fill(); ctx.restore();
  for (let i = 0; i < 3; i++) { ctx.save(); ctx.globalAlpha = p(2 + i * .5); rr(x + 40 + i * ((w - 80) / 3), y + 430 + (1 - p(2 + i * .5)) * 80, (w - 80) / 3 - 24, 190, 18); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fill(); ctx.restore(); }
  const bp = eback(seg(lt, .75, 1.05)); ctx.save(); ctx.translate(x + w / 2, y + 680); ctx.scale(bp, bp); rr(-140, -36, 280, 72, 36); ctx.fillStyle = '#fff'; ctx.fill();
  text('Fale conosco', 0, 12, { size: 30, w: 600, color: '#111' }); ctx.restore();
  // cursor click
  const c = eout(seg(lt, 1.0, 1.25)); ctx.save(); ctx.translate(lerp(x + w - 40, x + w / 2 + 40, c), lerp(y + h + 80, y + 690, c));
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 44); ctx.lineTo(12, 33); ctx.lineTo(22, 54); ctx.lineTo(30, 50); ctx.lineTo(20, 30); ctx.lineTo(36, 30); ctx.closePath(); ctx.fill(); ctx.restore();
  const rp = seg(lt, 1.25, 1.5); if (rp > 0 && rp < 1) { ctx.beginPath(); ctx.arc(x + w / 2 + 40, y + 690, 20 + 80 * rp, 0, TAU); ctx.strokeStyle = `rgba(255,255,255,${1 - rp})`; ctx.lineWidth = 4; ctx.stroke(); }
}
const GFX = [gSocial, gArt, gCarousel, gReel, gEdit, gSite];
function sceneServices(t) {
  bgDark(t);
  const i = clamp(Math.floor((t - S0) / SD), 0, 5), lt = t - S0 - i * SD;
  const inK = expo(seg(lt, 0, .35)), outK = i < 5 ? eio(seg(lt, SD - .22, SD)) : eio(seg(lt, SD - .25, SD));
  const dx = (1 - inK) * 380 - outK * 380, al = inK * (1 - outK);
  ctx.save(); ctx.translate(dx, 0); ctx.globalAlpha = al;
  // big number
  text(String(i + 1).padStart(2, '0'), W / 2, 420, { size: 170, w: 200, gradient: true, shadow: 30 });
  const [name, desc] = SERV[i];
  const sz = fitSize(name, 500, 92, 940);
  maskText(name, W / 2, 560, seg(lt, .05, .4), { size: sz, w: 500 });
  text(desc, W / 2, 640, { size: 44, w: 300, color: C.muted, alpha: eout(seg(lt, .2, .5)) });
  GFX[i](inK, lt);
  ctx.restore();
  // light sweep at each change
  const sw = seg(lt, 0, .35);
  if (sw > 0 && sw < 1) {
    ctx.save(); ctx.globalCompositeOperation = 'screen'; const sx = lerp(-400, W + 400, eout(sw));
    const g = ctx.createLinearGradient(sx - 200, 0, sx + 200, 0); g.addColorStop(0, 'rgba(120,100,255,0)'); g.addColorStop(.5, 'rgba(150,130,255,.35)'); g.addColorStop(1, 'rgba(120,100,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
  }
  // progress dashes
  for (let j = 0; j < 6; j++) {
    const x = W / 2 - 6 * 70 / 2 + j * 70;
    rr(x, 1700, 56, 6, 3); ctx.fillStyle = 'rgba(255,255,255,.15)'; ctx.fill();
    const f = j < i ? 1 : j === i ? clamp(lt / SD) : 0;
    if (f > 0) { rr(x, 1700, 56 * f, 6, 3); ctx.fillStyle = grad(x, 0, x + 56, 0); ctx.fill(); }
  }
}

// ---------- scene 4: everything in one place (20.0 - 23.0)
function sceneGrid(t) {
  const lt = t - 20;
  bgDark(t);
  maskText('Tudo o que a sua marca', W / 2, 330, seg(lt, .05, .45), { size: 74, w: 400 });
  maskText('precisa nas redes.', W / 2, 420, seg(lt, .15, .55), { size: 74, w: 400 });
  const tw = 450, th = 300, gx = W / 2 - tw - 15, gy = 560;
  for (let i = 0; i < 6; i++) {
    const r = Math.floor(i / 2), c = i % 2;
    const tx = gx + c * (tw + 30), ty = gy + r * (th + 30);
    const p = eback(seg(lt, .25 + i * .08, .75 + i * .08));
    const fx = W / 2 + (rnd(i) - .5) * 1600, fy = H / 2 + (rnd(i + 5) - .5) * 2000;
    ctx.save(); ctx.translate(lerp(fx, tx + tw / 2, p), lerp(fy, ty + th / 2, p)); ctx.rotate((1 - p) * (rnd(i + 2) - .5) * 1.4); ctx.globalAlpha = clamp(p * 1.5);
    glass(-tw / 2, -th / 2, tw, th, 28);
    text(String(i + 1).padStart(2, '0'), -tw / 2 + 40, -th / 2 + 80, { size: 48, w: 300, gradient: true, align: 'left' });
    const nm = SERV[i][0], words = nm.split(' ');
    const l1 = words.length > 2 ? words.slice(0, 2).join(' ') : words[0], l2 = words.length > 2 ? words.slice(2).join(' ') : words.slice(1).join(' ');
    text(l1, -tw / 2 + 40, th / 2 - (l2 ? 90 : 50), { size: 46, w: 500, align: 'left' });
    if (l2) text(l2, -tw / 2 + 40, th / 2 - 40, { size: 46, w: 500, align: 'left' });
    ctx.restore();
  }
  const k = seg(lt, 1.3, 1.7);
  ctx.save(); const s = 1 + .2 * (1 - eback(k)); ctx.translate(W / 2, 1640); ctx.scale(s, s);
  text('em um só lugar.', 0, 0, { size: 100, w: 600, gradient: true, shadow: 40, alpha: eout(k) }); ctx.restore();
}

// ---------- scene 5: before vs after (23.0 - 26.5)
function sceneCompare(t) {
  const lt = t - 23;
  bgDark(t, .8);
  const S = 640;
  const pin = expo(seg(lt, 0, .45)), pin2 = expo(seg(lt, .35, .8));
  // before card (top), desaturated
  ctx.save(); ctx.translate(W / 2 + (1 - pin) * -900, 640); ctx.rotate(-.04); const sh = lt > .8 && lt < 2.2 ? Math.sin(lt * 40) * 2 : 0; ctx.translate(sh, 0);
  ctx.filter = 'grayscale(.75) brightness(.8)';
  if (IMG.before.naturalWidth) ctx.drawImage(IMG.before, -S / 2, -S / 2, S, S); else { ctx.fillStyle = '#777'; ctx.fillRect(-S / 2, -S / 2, S, S); }
  ctx.filter = 'none'; ctx.restore();
  // after card (bottom)
  ctx.save(); ctx.translate(W / 2 + (1 - pin2) * 900, 1330); ctx.rotate(.02);
  ctx.shadowColor = 'rgba(122,85,255,.7)'; ctx.shadowBlur = 80;
  if (IMG.after.naturalWidth) ctx.drawImage(IMG.after, -S / 2, -S / 2, S, S); else { ctx.fillStyle = '#223'; ctx.fillRect(-S / 2, -S / 2, S, S); }
  ctx.restore();
  // labels
  const la = eout(seg(lt, .6, .9));
  ctx.save(); ctx.globalAlpha = la; rr(W / 2 - S / 2 - 30, 300, 200, 64, 32); ctx.fillStyle = '#3a3a44'; ctx.fill(); ctx.restore();
  text('ANTES', W / 2 - S / 2 + 70, 344, { size: 32, w: 600, color: '#d0d0d8', alpha: la, spacing: 4 });
  ctx.save(); ctx.globalAlpha = la; rr(W / 2 - S / 2 - 30, 990, 220, 64, 32); ctx.fillStyle = grad(0, 0, 400, 0); ctx.fill(); ctx.restore();
  text('DEPOIS', W / 2 - S / 2 + 80, 1034, { size: 32, w: 600, alpha: la, spacing: 4 });
  text('Mesma empresa.', W / 2, 200, { size: 78, w: 400, alpha: eout(seg(lt, .9, 1.3)), blur: (1 - eout(seg(lt, .9, 1.3))) * 10 });
  text('Outra percepção.', W / 2, 1780, { size: 84, w: 600, gradient: true, shadow: 30, alpha: eout(seg(lt, 1.5, 1.9)), blur: (1 - eout(seg(lt, 1.5, 1.9))) * 10 });
}

// ---------- scene 6: end card (26.5 - 30)
function sceneEnd(t) {
  const lt = t - 26.5;
  bgDark(t, 1.1);
  const k = eout(seg(lt, .1, .7));
  ctx.save(); ctx.globalAlpha = k;
  if (IMG.logo.naturalWidth) {
    const lw = 700 * (.9 + .1 * k), lh = lw * IMG.logo.naturalHeight / IMG.logo.naturalWidth;
    ctx.drawImage(IMG.logo, W / 2 - lw / 2, 640 - lh / 2, lw, lh);
  } else { rings(W / 2 - 200, 640, 110, 1); text('lumarc', W / 2 + 80, 690, { size: 140, w: 300 }); }
  ctx.restore();
  maskText('Quer apresentar sua', W / 2, 960, seg(lt, .5, .85), { size: 70, w: 400 });
  maskText('empresa assim?', W / 2, 1050, seg(lt, .6, .95), { size: 70, w: 400 });
  const b = eback(seg(lt, .9, 1.3));
  ctx.save(); ctx.translate(W / 2, 1230); ctx.scale(b * (1 + .03 * Math.max(0, Math.sin(lt * 5))), b * (1 + .03 * Math.max(0, Math.sin(lt * 5))));
  ctx.shadowColor = 'rgba(122,85,255,.8)'; ctx.shadowBlur = 50; rr(-300, -62, 600, 124, 62); ctx.fillStyle = grad(-300, 0, 300, 0); ctx.fill(); ctx.shadowBlur = 0;
  text('Pedir orçamento grátis', 0, 16, { size: 46, w: 500 }); ctx.restore();
  text('@lumarc_studio  ·  slumarc.com', W / 2, 1420, { size: 44, w: 400, color: C.muted, alpha: eout(seg(lt, 1.2, 1.6)) });
}

// =====================================================================
function renderAt(t) {
  T = t;
  ctx.save();
  if (t < 4.5) sceneBefore(t);
  else if (t < 5.0) { if (t < 4.75) sceneBefore(t); sceneAssimLayer(t); }
  else if (t < 8.0) sceneLogo(t);
  else if (t < 11.0) sceneHeadline(t);
  else if (t < 20.0) sceneServices(t);
  else if (t < 23.0) sceneGrid(t);
  else if (t < 26.5) sceneCompare(t);
  else sceneEnd(t);
  // quick dip between big sections
  [8.0, 11.0, 20.0, 23.0, 26.5].forEach(c => { const d = 1 - Math.abs(t - c) / .12; if (d > 0) flash(.5 * d, '14,14,20'); });
  vignette(.45);
  if (t >= 5) grain(.06);
  ctx.restore();
}
function sceneAssimLayer(t) { const a = eout(seg(t, 4.5, 4.62)); ctx.save(); ctx.globalAlpha = a; sceneAssim(t); ctx.restore(); }

window.ready = (async () => {
  makeNoise();
  await document.fonts.load('400 40px Outfit'); await document.fonts.load('200 40px Outfit'); await document.fonts.load('700 40px Outfit');
  await Promise.all(Object.values(IMG).map(im => im.complete ? 1 : new Promise(r => { im.onload = im.onerror = r; })));
  window.renderAt = renderAt; renderAt(9.8); return true;
})();
