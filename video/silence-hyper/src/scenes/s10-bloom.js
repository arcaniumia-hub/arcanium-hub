// s10-bloom — PEAK (b56-64): particle bloom, cut cascade, 'Hear nothing.'
//
// PART 1 b56-59 PARTICLE BLOOM: we burst out of the last gate into open dark space; the camera whips back while 150k points
//   carrying the model's own colours converge (swirling, per-point delay) into the product. 40k of them also draw velocity
//   trails (line segments evaluated at t and t-1.5 frames in the same vertex function) so every move — the assembly, the b57
//   BREATH, the b58 TORSION twist, the b58.5 SHIMMER ripple — leaves streaks of light. The real mesh fades in inside the
//   cloud (b58.5-59) and the points stay as an aura. Below: the violent gold SOUND SEA, every kick launching a ring swell.
// PART 2 b59-62 CUT CASCADE: 8ths (macro photo with liquid warp / 3D grazing close-up on slider+sleeve / mirrored orbit
//   frame = 'double headphone' / hero photo with zoom blur) then 16ths (SILENCE gold card / 3D front rim-lit / ONE /
//   orbit frame 10 + −42 dB). Only one bright field (the SILENCE card).
// PART 3 b62-64: pure ink + 'Hear nothing.' (muffled score) — the cleanest frame since the mute.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, expoIn, elastic, rnd, text, fitSize, drawCover, orbitFrame,
  COL, FONT, ADDITIVE, dotTexture, kickPump } from '../lib.js';
import { createHeadphone } from '../model.js';

const B0 = 56;
const DEG = Math.PI / 180;
const N = 150000, NL = 14000;   // trails: SwiftShader rasterises long lines slowly, keep them few and capped
const FOV = 32;
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const PC = .7;                         // model-space centre height of the product

// ------------------------------------------------------------------ deterministic Math.random during hp.sample
function seeded(fn, seed = 4242) {
  const orig = Math.random; let s = seed;
  Math.random = () => (s = (s * 16807) % 2147483647) / 2147483647;
  try { return fn(); } finally { Math.random = orig; }
}

// ------------------------------------------------------------------ particle state as a pure function of the beat
// returns [mix, breath, twist(rad), shimmerRadius, shimmerAmp]
function pState(b) {
  const mix = 1 - Math.pow(1 - seg(b, 56, 56.75), 3.5);
  // BREATH b57: 1 -> 1.25 (expoOut, 4 frames) then snapped back by b57.5 (expoIn)
  const fb = (b - 57) * 12;
  const breath = fb < 0 ? 0 : .25 * (expoOut(seg(fb, 0, 4)) - expoIn(seg(fb, 3.2, 6)));
  // TWIST b58: +35° in 3 frames (torsion: top twists most), spring back over 6
  const ft = (b - 58) * 12;
  const twist = ft < 0 ? 0 : ft < 3 ? 35 * DEG * expoOut(ft / 3) : 35 * DEG * (1 - elastic(seg(ft, 3, 9)));
  // SHIMMER b58.5: scatter pulse .8 -> 0 over 6 frames, a ripple running out from the centre
  const fs = (b - 58.5) * 12;
  const shR = fs < 0 ? -10 : fs * 2.6;
  const shA = fs < 0 ? 0 : .8 * Math.max(0, 1 - fs / 6) * clamp(fs * 2);
  return [mix, breath, twist, shR, shA];
}

const PFUNC = `
attribute vec3 aDir; attribute vec3 aCol; attribute vec4 aR;
uniform vec4 uS0, uS1; uniform float uA0, uA1, uSwirl, uTime, uAura;
vec3 hash3(float n){ return fract(sin(vec3(n, n+1.7, n+3.1))*43758.5453)*2.-1.; }
mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }
vec3 P(vec4 S, float shA){
  float m = smoothstep(0., 1., clamp((S.x - aR.x*.35)/.65, 0., 1.));
  vec3 p = mix(position + aDir, position, m);
  p.xz = rot(uSwirl*(1.-m)*(.5+aR.x))*p.xz;
  vec3 c = vec3(0., ${PC.toFixed(2)}, 0.);
  vec3 d = p - c; vec3 dn = normalize(d + vec3(1e-4));
  p += dn*uAura*(.1 + .9*aR.y*aR.y)*m;
  p = c + (p - c)*(1. + S.y*(.5 + 1.0*aR.z));
  float tw = S.z*(.15 + .85*clamp((p.y + 8.6)/18.6, 0., 1.));
  p.xz = rot(tw)*p.xz;
  float r = length(p - c);
  float w = exp(-pow((r - S.w)/2.4, 2.))*shA;
  p += hash3(aR.x*917.)*w*1.6 + dn*w*1.1;
  p += .07*sin(uTime*1.7 + aR.x*40.)*hash3(aR.y*331.);
  return p;
}`;
const PTS_V = `${PFUNC}
uniform float uSize, uPx, uKick; varying vec3 vCol; varying float vA;
void main(){
  vec3 p = P(uS0, uA0);
  vec4 mv = modelViewMatrix*vec4(p, 1.);
  float z = -mv.z;
  gl_PointSize = clamp(uSize*uPx*(.55 + .9*aR.y)/max(z, .1), 1., 14.);
  vA = smoothstep(1.5, 9., z);
  // near points grow (1/z) but keep their energy: they turn into soft bokeh instead of a white-out
  vCol = aCol*(1. + uKick*(.4 + aR.w*2.))*clamp(pow(z/34., 1.6), .05, 1.);
  gl_Position = projectionMatrix*mv;
}`;
const PTS_F = `
uniform sampler2D uDot; uniform float uAlpha, uBright; varying vec3 vCol; varying float vA;
void main(){ vec2 q = gl_PointCoord*2. - 1.; float r2 = dot(q, q); if (r2 > 1.) discard;
  float d = (1. - r2); d *= d; gl_FragColor = vec4(vCol*uBright*d, d*uAlpha*vA); }`;
const LIN_V = `${PFUNC}
attribute float aEnd; varying vec3 vCol; varying float vA; uniform float uLine;
void main(){
  vec3 p0 = P(uS0, uA0), p1 = P(uS1, uA1);
  vec3 dd = p1 - p0; float L = length(dd); p1 = p0 + dd*min(1., 3.2/max(L, 1e-4));
  vec3 p = aEnd < .5 ? p0 : p1;
  vec4 mv = modelViewMatrix*vec4(p, 1.);
  float len = length(p0 - p1);
  vA = clamp(len*.9 - .15, 0., 1.)*min(1., 2./max(len, .01))*(aEnd < .5 ? 1. : 0.)*smoothstep(1.5, 9., -mv.z)*uLine;
  vCol = aCol*clamp(pow(-mv.z/34., 1.6), .05, 1.);
  gl_Position = projectionMatrix*mv;
}`;
const LIN_F = `varying vec3 vCol; varying float vA; uniform float uBright; void main(){ gl_FragColor = vec4(vCol*uBright, vA); }`;

function buildParticles(hp) {
  const smp = seeded(() => hp.sample(N));
  const pos = smp.positions, col = new Float32Array(N * 3), dir = new Float32Array(N * 3), aR = new Float32Array(N * 4);
  const gold = lin(COL.gold), goldHi = lin(COL.goldHi);
  for (let i = 0; i < N; i++) {
    const r = k => rnd(i * 1.618 + k * 7.31 + .29);
    // scattered start: sample + random direction × 30 (biased toward the camera side: we fly out of the gate into it)
    const u = r(1) * 2 - 1, th = r(2) * TAU, s = Math.sqrt(1 - u * u);
    const m = 30 * (.25 + .75 * Math.pow(r(3), .6));
    dir.set([s * Math.cos(th) * m, u * m * .8, (s * Math.sin(th) * .6 + .55) * m], i * 3);
    let cr = smp.colors[i * 3], cg = smp.colors[i * 3 + 1], cb = smp.colors[i * 3 + 2];
    const isGold = cr > .6 && cb < .45;
    const spark = r(4) < .035 ? 1 : 0;
    let k = isGold ? 2.4 : 1;
    if (spark) { cr = goldHi.r; cg = goldHi.g; cb = goldHi.b; k = 3.2; }
    else if (cr < .06) k = 2.2;                 // charcoal leather: lift it so the cups read as a dark-grey glow
    col.set([cr * k, cg * k, cb * k], i * 3);
    aR.set([r(5), r(6), r(7), spark ? 1 : r(8) * .3], i * 4);
  }
  const mkGeo = (idx, line) => {
    const n = idx.length * (line ? 2 : 1), g = new THREE.BufferGeometry();
    const P = new Float32Array(n * 3), D = new Float32Array(n * 3), C = new Float32Array(n * 3), R4 = new Float32Array(n * 4), E = new Float32Array(n);
    let v = 0;
    for (const i of idx) for (let e = 0; e < (line ? 2 : 1); e++, v++) {
      P.set(pos.subarray(i * 3, i * 3 + 3), v * 3); D.set(dir.subarray(i * 3, i * 3 + 3), v * 3);
      C.set(col.subarray(i * 3, i * 3 + 3), v * 3); R4.set(aR.subarray(i * 4, i * 4 + 4), v * 4); E[v] = e;
    }
    g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('aDir', new THREE.BufferAttribute(D, 3));
    g.setAttribute('aCol', new THREE.BufferAttribute(C, 3)); g.setAttribute('aR', new THREE.BufferAttribute(R4, 4));
    if (line) g.setAttribute('aEnd', new THREE.BufferAttribute(E, 1));
    return g;
  };
  const U = { uS0: { value: new THREE.Vector4() }, uS1: { value: new THREE.Vector4() }, uA0: { value: 0 }, uA1: { value: 0 }, uSwirl: { value: 0 },
    uTime: { value: 0 }, uAura: { value: 0 }, uSize: { value: .42 }, uPx: { value: 960 }, uKick: { value: 0 }, uDot: { value: dotTexture() },
    uAlpha: { value: 1 }, uBright: { value: .5 }, uLine: { value: 1 } };
  const all = Array.from({ length: N }, (_, i) => i);
  const pts = new THREE.Points(mkGeo(all, false), new THREE.ShaderMaterial({ vertexShader: PTS_V, fragmentShader: PTS_F, uniforms: U, ...ADDITIVE }));
  const sub = []; for (let i = 0; i < N && sub.length < NL; i++) if (rnd(i * 2.71 + .5) < NL / N * 1.02) sub.push(i);
  const LU = { ...U, uBright: { value: .6 } };
  const lines = new THREE.LineSegments(mkGeo(sub, true), new THREE.ShaderMaterial({ vertexShader: LIN_V, fragmentShader: LIN_F, uniforms: LU, ...ADDITIVE }));
  pts.frustumCulled = lines.frustumCulled = false;
  return { pts, lines, U, LU };
}

// ------------------------------------------------------------------ the violent gold SOUND SEA
const h2 = (i, j) => { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); };
function vn(x, z) {
  const i = Math.floor(x), j = Math.floor(z), fx = x - i, fz = z - j, u = fx * fx * (3 - 2 * fx), v = fz * fz * (3 - 2 * fz);
  const a = h2(i, j), b = h2(i + 1, j), c = h2(i, j + 1), d = h2(i + 1, j + 1);
  return (a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v) * 2 - 1;
}
const KICKS = [56, 57, 58, 59];
function buildSea(width, z0, z1, nx, nz) {
  const n = nx * nz, pos = new Float32Array(n * 3), col = new Float32Array(n * 3), idx = [];
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    pos.set([(i / (nx - 1) - .5) * width, 0, lerp(z0, z1, j / (nz - 1))], (j * nx + i) * 3);
    if (i < nx - 1) idx.push(j * nx + i, j * nx + i + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.setIndex(idx);
  const mesh = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, ...ADDITIVE })); mesh.frustumCulled = false;
  const G = lin(COL.gold), G2 = lin(COL.gold2), HI = lin(COL.goldHi);
  function update(b, alpha) {
    const t = (b - B0) * BEAT, A = 4.5;
    const sw = KICKS.filter(k => b >= k).map(k => ({ r: 4 + 42 * (b - k) * BEAT * 2.2, a: Math.exp(-(b - k) * BEAT / .55) }));
    for (let j = 0; j < nz; j++) {
      const z = lerp(z0, z1, j / (nz - 1));
      const far = Math.pow(seg(z, z0, z0 + 45), 1.4) * (1 - .5 * seg(z, z1 - 15, z1));
      for (let i = 0; i < nx; i++) {
        const k = j * nx + i, x = pos[k * 3];
        const d = Math.hypot(x, z);
        let h = A * (.6 * vn(x * .07 + t * .4, z * .07 - t * 1.6) + .28 * vn(x * .16 - t * .9, z * .16 - t * 2.6) + .12 * vn(x * .4 + t * 2, z * .4 - t * 4));
        let ring = 0;
        for (const s of sw) { const e = Math.exp(-Math.pow((d - s.r) / 3.2, 2)) * s.a; ring += e; }
        h += 4.2 * ring;
        pos[k * 3 + 1] = h;
        const side = 1 - seg(Math.abs(x), width * .3, width * .5);
        const a = alpha * far * side;
        const crest = clamp(.5 + .5 * h / A);
        const base = .25 + 3.4 * crest * crest * crest, rg = 4.5 * ring;
        col[k * 3] = a * (G2.r * base + G.r * crest * .5 + HI.r * rg);
        col[k * 3 + 1] = a * (G2.g * base + G.g * crest * .5 + HI.g * rg);
        col[k * 3 + 2] = a * (G2.b * base + G.b * crest * .5 + HI.b * rg);
      }
    }
    g.attributes.position.needsUpdate = true; g.attributes.color.needsUpdate = true;
  }
  return { mesh, update };
}

// ------------------------------------------------------------------ foreground bokeh (depth between lens and product)
const BK_V = `attribute vec4 aR; uniform float uTime, uPx; varying float vB;
void main(){
  vec3 p = position + .6*vec3(sin(uTime*.7 + aR.x*30.), sin(uTime*.5 + aR.y*20.), 0.);
  vec4 mv = modelViewMatrix*vec4(p, 1.); float z = max(-mv.z, .5);
  gl_PointSize = clamp((1.2 + 2.2*aR.z)*uPx/z, 4., 220.);
  vB = (.35 + .65*aR.w)*smoothstep(2., 10., z)*clamp(30./gl_PointSize, .15, 1.);
  gl_Position = projectionMatrix*mv; }`;
const BK_F = `uniform sampler2D uDot; uniform vec3 uCol; varying float vB;
void main(){ vec2 q = gl_PointCoord*2. - 1.; float r = length(q);
  float d = smoothstep(1., .82, r)*(.55 + .45*smoothstep(.5, .95, r));
  gl_FragColor = vec4(uCol*vB*d, d); }`;
function buildBokeh(n = 260) {
  const g = new THREE.BufferGeometry(), P = new Float32Array(n * 3), A = new Float32Array(n * 4);
  for (let i = 0; i < n; i++) {
    const r = k => rnd(i * 3.913 + k * 1.77 + 9.1);
    P.set([(r(1) - .5) * 60, -10 + 30 * r(2), 14 + 36 * r(3)], i * 3); A.set([r(4), r(5), r(6), r(7)], i * 4);
  }
  g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('aR', new THREE.BufferAttribute(A, 4));
  const U = { uTime: { value: 0 }, uPx: { value: 960 }, uDot: { value: dotTexture() }, uCol: { value: lin(COL.gold).multiplyScalar(.16) } };
  const pts = new THREE.Points(g, new THREE.ShaderMaterial({ vertexShader: BK_V, fragmentShader: BK_F, uniforms: U, ...ADDITIVE }));
  pts.frustumCulled = false;
  return { pts, U };
}

// ------------------------------------------------------------------ b56 HIT: an IRIS BURST out of the gate's vanishing point
// A 7-blade aperture snaps open from (540,900) on three crisp frames (r 300 -> 750 -> 1875); a hot gold core and
// radial rays fill the opening. The 3D image is never washed out: no linear flash, only an exposure/bloom lift.
const VP = [540, 900], NB = 7;
function irisBurst(ctx, f) {               // f = whole frames since b56 (0, 1, 2)
  if (f > 2) return;
  const [cx, cy] = VP, r = 300 * Math.pow(2.5, f), rot = .42 + f * .19, k = 1 - f / 3, kc = [1, .5, 0][f];
  const v = Array.from({ length: NB }, (_, i) => { const a = rot + i / NB * TAU; return [cx + Math.cos(a) * r, cy + Math.sin(a) * r]; });
  const poly = () => { ctx.beginPath(); v.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); };
  ctx.save();
  // blades: brushed dark metal outside the opening
  ctx.beginPath(); ctx.rect(0, 0, W, H); v.slice().reverse().forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath();
  let g = ctx.createRadialGradient(cx, cy, r * .85, cx, cy, r * 2.4);
  g.addColorStop(0, '#2a241b'); g.addColorStop(.25, '#120f0b'); g.addColorStop(1, '#050506');
  ctx.fillStyle = g; ctx.fill('evenodd');
  // blade seams: each aperture edge continues out as the edge of its blade (the pinwheel)
  ctx.lineWidth = 2.5; ctx.strokeStyle = `rgba(230,200,150,${.4 * k})`;
  for (let i = 0; i < NB; i++) {
    const [x0, y0] = v[(i + NB - 1) % NB], [x1, y1] = v[i], dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x1 + dx / L * 2600, y1 + dy / L * 2600); ctx.stroke();
  }
  // light through the opening: hot core + rays, clipped to the aperture
  ctx.globalCompositeOperation = 'lighter';
  ctx.save(); poly(); ctx.clip();
  if (kc > 0) {
    const rc = Math.min(r, 420) * .9;
    g = ctx.createRadialGradient(cx, cy, 0, cx, cy, rc);
    g.addColorStop(0, `rgba(255,246,228,${.95 * kc})`); g.addColorStop(.15, `rgba(247,226,184,${.5 * kc})`);
    g.addColorStop(.5, `rgba(230,200,150,${.1 * kc})`); g.addColorStop(1, 'rgba(184,146,90,0)');
    ctx.fillStyle = g; ctx.fillRect(cx - rc, cy - rc, rc * 2, rc * 2);
  }
  for (let i = 0; i < 90; i++) {
    const a = rnd(i * 3.17 + 1.3) * TAU, r0 = r * (.06 + .25 * rnd(i * 5.1 + 2)), r1 = r * (.45 + .9 * rnd(i * 7.7 + 3)) * (1 + .5 * f);
    const hot = rnd(i * 9.3) < .3;
    ctx.strokeStyle = hot ? `rgba(255,244,222,${.7 * k})` : `rgba(230,200,150,${.45 * k})`; ctx.lineWidth = hot ? 2 : 1.4;
    ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0); ctx.lineTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1); ctx.stroke();
  }
  ctx.restore();
  // the aperture rim: a crisp gold hairline with a soft glow (strokes, no shadowBlur)
  poly(); ctx.lineJoin = 'round';
  ctx.lineWidth = 34; ctx.strokeStyle = `rgba(230,200,150,${.16 * k})`; ctx.stroke();
  ctx.lineWidth = 12; ctx.strokeStyle = `rgba(230,200,150,${.3 * k})`; ctx.stroke();
  ctx.lineWidth = 3.5; ctx.strokeStyle = `rgba(255,240,210,${.95 * k})`; ctx.stroke();
  ctx.restore();
}
// '−42 dB' in Anton with a TRUE minus: Anton has no U+2212 (it falls back to a short hyphen), so the bar is drawn
function dbLabel(ctx, cx, base, size, o = {}) {
  ctx.save(); ctx.font = `400 ${size}px "${FONT.impact}"`;
  const s = '42 dB', w = ctx.measureText(s).width, cap = ctx.measureText('4').actualBoundingBoxAscent || size * .72;
  const mw = size * .46, gap = size * .08, th = Math.max(4, size * .095), x0 = cx - (mw + gap + w) / 2;
  ctx.fillStyle = o.color || COL.white; ctx.fillRect(x0, base - cap * .5 - th / 2, mw, th);
  ctx.restore();
  text(ctx, s, x0 + mw + gap, base, { size, family: FONT.impact, color: o.color || COL.white, align: 'left' });
}

// ------------------------------------------------------------------ shot table (beats)
const SHOTS = [
  { id: 'bloom', a: 56, z: 59 },
  { id: 'macro', a: 59, z: 59.5 },
  { id: 'graze', a: 59.5, z: 60 },
  { id: 'mirror', a: 60, z: 60.5 },
  { id: 'hero', a: 60.5, z: 61 },
  { id: 'silence', a: 61, z: 61.25 },
  { id: 'front', a: 61.25, z: 61.5 },
  { id: 'one', a: 61.5, z: 61.75 },
  { id: 'db', a: 61.75, z: 62 },
  { id: 'hear', a: 62, z: 64 },
];
const shotAt = b => b < 56 ? SHOTS[0] : SHOTS.find(s => b >= s.a && b < s.z) || SHOTS[SHOTS.length - 1];
function mbAt(lt) {
  const b = B0 + lt / BEAT + 1e-6;
  if (b < 56.25) return 3;
  if (b < 56.5) return 2;
  if (b >= 59.5 && b < 60) return 4;   // 2D-only shot: 4 sub-frames are cheap and smooth the whip
  return 1;
}

let R = null;
export default {
  id: 's10-bloom', start: 56, end: 64,
  cutIn: 'none',
  init(E) {
    const scene = new THREE.Scene();
    scene.userData.envIntensity = .4;
    const cam = new THREE.PerspectiveCamera(FOV, W / H, .1, 600);
    const prod = new THREE.Group(); scene.add(prod);
    const hp = createHeadphone();
    hp.cups.forEach(c => ['pcb', 'battery', 'magnet', 'coil', 'driver'].forEach(nm => { c.userData.parts[nm].visible = false; }));
    hp.root.position.y = -PC; prod.add(hp.root);
    const P = buildParticles(hp);
    P.pts.position.y = P.lines.position.y = -PC; prod.add(P.pts); prod.add(P.lines);
    const sea = buildSea(150, -110, 52, 150, 104);
    sea.mesh.position.y = -14; scene.add(sea.mesh);
    // lights (re-weighted per shot)
    const key = new THREE.DirectionalLight(0xfff4ea, 2.2); key.position.set(30, 40, 30); scene.add(key);
    const rimL = new THREE.DirectionalLight(0xffd9a0, 0); rimL.position.set(-40, 15, -30); scene.add(rimL);
    const rimR = new THREE.DirectionalLight(0xfff2de, 0); rimR.position.set(40, 10, -30); scene.add(rimR);
    const under = new THREE.PointLight(0xffc070, 0, 0, 2); under.position.set(0, -12, 6); scene.add(under);
    const sweep = new THREE.PointLight(0xfff0d8, 0, 0, 2); scene.add(sweep);
    const hemi = new THREE.HemisphereLight(0xf4f1ec, 0x16140f, .3); scene.add(hemi);
    const BK = buildBokeh(); scene.add(BK.pts);
    R = { bokeh: BK.pts, bokehU: BK.U, scene, cam, prod, hp, P, sea, key, rimL, rimR, under, sweep, hemi, hpA: -1 };
  },
  motionBlur(lt) { return mbAt(lt); },
  draw(E, lt, t) {
    const b = B0 + lt / BEAT + 1e-6, fx = E.fx, bg = E.bg, fg = E.fg;
    // always issue a real draw op on fg: Chromium can skip re-uploading a canvas that was only reset(), which leaked
    // the b56 iris (and the graze flare) into later frames that draw nothing on fg
    fg.clearRect(0, 0, W, H); fg.fillStyle = 'rgba(0,0,0,0.004)'; fg.fillRect(0, 0, 1, 1);
    // the SHOT is picked from the frame's own time (so motion-blur sub-frames never mix two shots on a cut);
    // the animation inside it uses the sub-frame time
    const S = shotAt(B0 + Math.round(lt * 30) / 30 / BEAT + 1e-6), sf = (b - S.a) * 12;   // frames into the current shot
    const Fr = Math.floor(t * 30 + .5);
    const { scene, cam, prod, hp, P, sea } = R;
    fx.exposure = .88; fx.bloom = .6; fx.bloomThreshold = .72; fx.grain = .045; fx.vignette = .4; fx.sat = 1.05;
    scene.environmentIntensity = S.id === 'front' ? .05 : .4;
    const setHP = a => { if (Math.abs(a - R.hpA) > 1e-4) { hp.setOpacity(hp.root, a); R.hpA = a; } };

    if (S.id === 'bloom') {
      // ---------------- PART 1: PARTICLE BLOOM
      fx.bloom = lerp(.5, 1.0, seg(b, 56, 56.75)); fx.bloomThreshold = lerp(.8, .55, seg(b, 56, 56.75));
      const st = pState(b), sp = pState(b - 1.5 / 12);
      P.U.uS0.value.set(st[0], st[1], st[2], st[3]); P.U.uA0.value = st[4];
      P.U.uS1.value.set(sp[0], sp[1], sp[2], sp[3]); P.U.uA1.value = sp[4];
      P.U.uSwirl.value = 2.4; P.U.uTime.value = t;
      P.U.uAura.value = .25 + .5 * eout(seg(b, 58.5, 59));
      const kick = KICKS.reduce((m, k) => Math.max(m, b >= k ? Math.exp(-(b - k) * BEAT / .1) : 0), 0);
      P.U.uKick.value = kick * .6;
      P.U.uBright.value = .155 * (.15 + .85 * st[0] * st[0]) * (1 - .3 * eout(seg(b, 58.5, 59)));
      P.LU.uBright.value = .3 * (.35 + .65 * seg(b, 56.12, 56.4)); P.U.uLine.value = 1;
      P.U.uSize.value = .34;
      P.pts.visible = P.lines.visible = true; sea.mesh.visible = true;
      // product orbit + the real mesh fading in inside the cloud
      prod.rotation.set(0, st[2] * .5, 0);
      const az = (46 - 42 * eio(seg(b, 56, 59.2))) * DEG;
      prod.scale.setScalar(1);
      const ma = eio(seg(b, 58.5, 59));
      setHP(ma);
      // camera: whip pull-back b56-56.5 (dist 13 -> 66, roll 28° -> 0), then a slow push
      const pull = expoOut(seg(b, 56, 56.55));
      const dist = lerp(13, 63, pull) - 4 * eio(seg(b, 56.5, 59));
      const el = (lerp(4, -4.5, pull) + 2.5 * eio(seg(b, 56.5, 59))) * DEG;
      cam.position.set(Math.sin(az) * Math.cos(el) * dist, Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
      cam.lookAt(0, -.3, 0);
      cam.rotateZ(28 * DEG * (1 - expoOut(seg(b, 56, 56.6))));
      cam.setViewOffset(W, H, 0, 60, W, H);
      // sea
      sea.update(b, eout(seg(b, 56, 56.6)));
      sea.mesh.rotation.y = az * .75; R.bokeh.rotation.y = az * .55; R.bokeh.visible = true;
      R.bokehU.uTime.value = t;
      // lights for the real mesh
      R.key.intensity = 2.4; R.rimL.intensity = 3; R.rimR.intensity = 2; R.under.intensity = 900 * (1 + kick); R.sweep.intensity = 0; R.hemi.intensity = .25;
      // bg: a low warm horizon glow
      { const g = bg.createRadialGradient(540, 1180, 0, 540, 1180, 900); g.addColorStop(0, 'rgba(230,200,150,.16)'); g.addColorStop(.5, 'rgba(184,146,90,.05)'); g.addColorStop(1, 'rgba(5,5,6,0)');
        bg.save(); bg.scale(1, 1); bg.fillStyle = g; bg.fillRect(0, 0, W, H); bg.restore(); }
      E.render3D(scene, cam);
      // FX: b56 gold flash + zoom blur; kicks; b57/b58 rgb kicks
      const f0 = (b - 56) * 12;
      // HIT b56: iris burst (crisp, frame-quantised) + exposure/bloom lift; no linear flash, so the frame keeps its contrast
      const fq = Math.round((B0 + Math.round(lt * 30) / 30 / BEAT - 56) * 12);
      irisBurst(fg, fq);
      if (fq <= 1) { fx.exposure *= fq === 0 ? 1.6 : 1.25; fx.bloom = Math.max(fx.bloom, fq === 0 ? 1.5 : 1.2); }
      if (f0 < 4) { fx.zoomBlur = .3 * Math.pow(1 - f0 / 4, 2); fx.zoomCenter = [.5, 1 - VP[1] / H]; }
      fx.zoom *= 1 + .06 * (1 - expoOut(clamp(f0 / 8)));
      fx.rgb = Math.max(fx.rgb, .0015 + .007 * Math.max(0, 1 - f0 / 8));
      // the assembling cloud is a dense web of hairlines: keep its blacks deep on the frames right after the hit
      if (f0 > .5 && f0 < 6) fx.contrast = 1 + .22 * (1 - f0 / 6);
      kickPump(fx, t, KICKS.slice(1).map(k => k * BEAT), { zoom: 1.03, rgb: .008 });
      for (const k of [57, 58]) { const f = (b - k) * 12; if (f >= 0 && f < 6) fx.rgb = Math.max(fx.rgb, .015 * Math.pow(1 - f / 6, 2)); }
      { const f = (b - 58.5) * 12; if (f >= 0 && f < 6) fx.rgb = Math.max(fx.rgb, .008 * (1 - f / 6)); }
      // the sea is 1-px hairlines: strong radial aberration splits them into rainbows, so cap it once the burst is over
      if (f0 > 6) fx.rgb = Math.min(fx.rgb, .005);
    } else if (S.id === 'macro') {
      const k = sf / 6;
      drawCover(bg, E.img.macro, 0, 0, W, H, { zoom: lerp(1.2, 1.3, k), fx: lerp(.66, .72, k), fy: .5 });
      fx.displace = .04 * (1 - .5 * k); fx.displaceScale = 2.5;
    } else if (S.id === 'graze') {
      // b59.5: macro of the real product (hero.jpg): headband sleeve, left gold slider and cushion, whipping sideways;
      // a hot anamorphic streak rides the slider's top edge (frame-quantised so the motion blur does not double it)
      const e = lerp(sf / 6, eio(sf / 6), .5), Z = 1.55, sc = Math.max(W / 1000, H / 1075) * Z, iw = 1000 * sc, ih = 1075 * sc;
      const fxp = lerp(.10, .26, e), fyp = lerp(.37, .34, e);
      drawCover(bg, E.img.hero, 0, 0, W, H, { zoom: Z, fx: fxp, fy: fyp });
      const fq6 = clamp((Math.round(lt * 30) / 30 / BEAT + B0 - S.a) * 2), fe = lerp(fq6, eio(fq6), .5);
      const ox = (W - iw) * lerp(.10, .26, fe), oy = (H - ih) * lerp(.37, .34, fe);
      const x = 207 * sc + ox, y = 440 * sc + oy;
      fg.save(); fg.globalCompositeOperation = 'lighter';
      fg.save(); fg.translate(x, y); fg.scale(1, .045);
      let g = fg.createRadialGradient(0, 0, 0, 0, 0, 760);
      g.addColorStop(0, 'rgba(255,236,200,.5)'); g.addColorStop(.4, 'rgba(230,200,150,.16)'); g.addColorStop(1, 'rgba(230,200,150,0)');
      fg.fillStyle = g; fg.fillRect(-760, -760, 1520, 1520); fg.restore();
      g = fg.createLinearGradient(x - 1000, 0, x + 1000, 0);
      g.addColorStop(0, 'rgba(255,240,215,0)'); g.addColorStop(.5, 'rgba(255,244,225,.8)'); g.addColorStop(1, 'rgba(255,240,215,0)');
      fg.fillStyle = g; fg.fillRect(x - 1000, y - 1.5, 2000, 3);
      g = fg.createRadialGradient(x, y, 0, x, y, 80); g.addColorStop(0, 'rgba(255,248,235,.85)'); g.addColorStop(1, 'rgba(255,230,190,0)');
      fg.fillStyle = g; fg.fillRect(x - 80, y - 80, 160, 160);
      fg.restore();
      fx.vignette = .5;
    } else if (S.id === 'front') {
      P.pts.visible = P.lines.visible = false; sea.mesh.visible = false; R.bokeh.visible = false;
      setHP(1); prod.scale.setScalar(1);
      // front-on, rim-lit on ink
      const k = sf / 3;
      // 3/4 front (the hero.jpg angle) so the cup faces and gold rings read, instead of edge-on discs
      prod.rotation.set(0, lerp(-.62, -.56, k), 0);
      const d = lerp(58, 54, k);
      cam.position.set(0, 3.2, d); cam.lookAt(0, -.3, 0);
      cam.setViewOffset(W, H, 0, 0, W, H);
      R.key.intensity = .05; R.rimL.intensity = 9; R.rimR.intensity = 9; R.under.intensity = 0; R.sweep.intensity = 0; R.hemi.intensity = .05;
      R.rimL.position.set(-30, 25, -40); R.rimR.position.set(30, 25, -40);
      E.render3D(scene, cam);
      R.rimL.position.set(-40, 15, -30); R.rimR.position.set(40, 10, -30);
    } else if (S.id === 'mirror') {
      const k = sf / 6;
      const sh = [E.img.orbit0, E.img.orbit1, E.img.orbit2, E.img.orbit3];
      // the mirror axis runs through the headband centre (x 540): a perfectly symmetrical front view, centred on y 960
      orbitFrame(bg, sh, Math.round(lerp(31, 34, k)), 540, 960, lerp(1500, 1580, eout(k)), { mode: 'source-over' });
      fx.mirror = 1; fx.tint = [1.04, 1, .95]; fx.sat = 1.05;
    } else if (S.id === 'hero') {
      const k = sf / 6;
      drawCover(bg, E.img.hero, 0, 0, W, H, { zoom: lerp(1.4, 1.52, k), fx: .62, fy: .55 });
      fx.rgb = .025; fx.zoomBlur = .3 * (1 - .6 * k); fx.zoomCenter = [.55, .5];
    } else if (S.id === 'silence') {
      bg.fillStyle = COL.gold; bg.fillRect(0, 0, W, H);
      const s = fitSize(bg, 'SILENCE', 1000, 900, 400, FONT.impact);
      const sc = lerp(1.07, 1, eout(sf / 3)), lh = s * .86;
      bg.save(); bg.translate(540, 960); bg.scale(sc, sc);
      for (let r = -4; r <= 4; r++) {
        const dx = (r % 2 ? 1 : -1) * (60 + 40 * Math.abs(r)) * (1 - eout(sf / 3)) * (r ? 1 : 0);
        if (r === 0) text(bg, 'SILENCE', dx, s * .36, { size: s, family: FONT.impact, color: COL.ink });
        else text(bg, 'SILENCE', dx, s * .36 + r * lh, { size: s, family: FONT.impact, fill: false, stroke: 2.5, strokeColor: 'rgba(5,5,6,.55)', alpha: 1 - Math.abs(r) * .16 });
      }
      bg.restore();
      fx.bloom = .3; fx.vignette = .25;
    } else if (S.id === 'one') {
      const s = fitSize(bg, 'ONE', 900, 1200, 400, FONT.impact);
      const sc = lerp(1.1, 1, eout(sf / 3));
      bg.save(); bg.translate(540, 960); bg.scale(sc, sc);
      text(bg, 'ONE', 0, s * .36, { size: s, family: FONT.impact, gold: true, alpha: 1 });
      bg.restore();
    } else if (S.id === 'db') {
      const sh = [E.img.orbit0, E.img.orbit1, E.img.orbit2, E.img.orbit3];
      orbitFrame(bg, sh, 10, 540, 780, lerp(1150, 1200, sf / 3), { mode: 'source-over' });
      const sc = lerp(1.25, 1, expoOut(sf / 2));
      fg.save(); fg.translate(540, 1450); fg.scale(sc, sc);
      dbLabel(fg, 0, 0, 200);
      fg.restore();
    } else {
      // ---------------- PART 3: 'Hear nothing.'
      text(bg, 'Hear nothing.', 540, 990, { size: 120, family: FONT.serif, italic: true, color: COL.white });
      fx.bloom = 0; fx.rgb = 0; fx.grain = .05; fx.vignette = .5; fx.sat = 1;
      fx.zoom = 1 + .03 * seg(b, 62, 64);
    }

    // ---------------- cascade cut kicks
    if (b >= 59 && b < 62) {
      if (sf < 1) fx.rgb = Math.max(fx.rgb, .012);
      fx.zoom *= 1 + .04 * (1 - expoOut(clamp(sf / 3)));
      if (b >= 61) {
        if (Math.round(sf) < 1) { fx.glitch = .15; fx.glitchSeed = Fr * 7 + 3; }   // the cut frame only; the next 2 frames are clean
        fx.rgb = Math.min(fx.rgb, .006);
        if (S.id === 'one' || S.id === 'db') { fx.bloomThreshold = .9; fx.bloom = Math.min(fx.bloom, S.id === 'db' ? .2 : .45); }
      }
    }
  },
};
