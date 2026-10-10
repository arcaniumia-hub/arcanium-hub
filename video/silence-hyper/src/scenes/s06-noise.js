// s06-noise — THE NOISE (b28-36): the only cold stretch of the film. The live 3D product (match of s05's Droste cell)
// spins exactly 4 accelerating turns over a violent cold SOUND SEA while a storm of noise words doubles on every beat
// (1 -> 256) and buries it; the AMBIENT NOISE HUD climbs 38 -> 118 dB. b34 dead stop on a CHUNK; the villain word
// 'NOISE' bursts between the cups and shoves them apart (the band stretches like rubber); b35.5 the cups CLAMP shut,
// crushing the word into a 6 px white hairline while the storm is sucked into the centre. s07 detonates on the click.
//
// Layers: bg2d cold haze + searchlights, even storm words, villain 'NOISE' (behind the product: the cups cover its ends)
//         3D product (cold studio light, gold rings pulsing on the kick) + cold line-terrain sea with beat shockwaves
//         fg2d odd storm words (big ones defocused = near the lens), HUD.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoIn, expoOut, rnd, noise1, text, font, measure, ADDITIVE,
  downbeatPunch, b2s, COL, FONT } from '../lib.js';
import { createHeadphone } from '../model.js';

const B0 = 28;
const DEG = Math.PI / 180;
const COLD = '#e9eef2';
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const FOV = 30;
const TILT = 8 * DEG;                       // product tilted toward camera
const LB_STOP = 6, LB_PUSH1 = 7.5, LB_END = 7.5 + 5 / 12;   // spin stop b34 · clamp b35.5 · cups shut at f431
const NOISE_C = [540, 1000];                // storm suck-in point
const BLUR_RES = .5;                        // resolution of the motion-blur samples

// ------------------------------------------------------------------ the word table (exported so s07 can rebuild b36)
const LIST = ['TRAFFIC', 'SIRENS', 'HONK', 'DRILLS', 'CHATTER', 'ALARMS', 'NOTIFICATIONS', '+99', 'SUBWAY', 'CONSTRUCTION', 'JET ENGINE', 'OPEN OFFICE'];
const WAVES = [[0, 0], [1, 1], [2, 2], [4, 3], [8, 4], [16, 4.5], [32, 5], [64, 5.5], [128, 6]];   // [first index, local beat]
// hand-composed first words (big, legible), the rest on an R2 low-discrepancy scatter
const HAND = [
  { word: 'NOISE', fam: 0, v: 0, x: 540, y: 1470, size: 190, rot: 0 },          // bottom <= ~1600 (Reels UI safe)
  { word: 'TRAFFIC', fam: 1, v: 0, x: 255, y: 640, size: 74, rot: 0 },
  { word: 'SIRENS', fam: 0, v: 1, x: 905, y: 700, size: 150, rot: -90 * DEG },
  { word: 'HONK', fam: 2, v: 3, x: 205, y: 1330, size: 112, rot: 6 * DEG },
  { word: 'NOISE', fam: 0, v: 2, x: 150, y: 905, size: 170, rot: 90 * DEG },
  { word: '+99', fam: 2, v: 0, x: 860, y: 1440, size: 120, rot: -6 * DEG },
  { word: 'JET ENGINE', fam: 1, v: 1, x: 690, y: 515, size: 58, rot: 0 },
  { word: 'NOISE', fam: 0, v: 3, x: 760, y: 1215, size: 96, rot: 0 },
];
const FAMS = [[FONT.impact, 400], [FONT.mono, 700], [FONT.ui, 900]];
export function wordTable() {
  const out = [];
  for (let i = 0; i < 256; i++) {
    const r = k => rnd(i * 7.13 + k * 1.71 + 3.3);
    let wv = 0; for (let k = 0; k < WAVES.length; k++) if (i >= WAVES[k][0]) wv = k;
    let o;
    if (i < HAND.length) o = { ...HAND[i] };
    else {
      const word = r(1) < .5 ? 'NOISE' : LIST[Math.floor(r(2) * LIST.length) % LIST.length];
      const fam = r(3) < .6 ? 0 : r(3) < .85 ? 1 : 2;
      let v = r(4) < .4 ? 0 : r(4) < .7 ? 1 : r(4) < .85 ? 2 : 3;
      const maxS = lerp(200, 100, wv / 8);
      let size = 30 + (maxS - 30) * Math.pow(r(5), 2.1);
      if (r(6) < .045) size = 150 + 70 * r(7);                      // big, rare
      if (v === 3 && size > 110) v = 1;                               // loud boxes stay small
      if (fam === 1 && word.length > 9) size = Math.min(size, 120);
      const rr = r(8), rot = rr < .5 ? 0 : rr < .64 ? 90 * DEG : rr < .78 ? -90 * DEG : (rr < .89 ? 6 : -6) * DEG;
      const fx = (.31 + i * .7548776662) % 1, fy = (.62 + i * .5698402910) % 1;
      o = { word, fam, v, x: fx * 1080, y: 200 + fy * 1520, size, rot };
    }
    o.i = i; o.wave = wv; o.lb = WAVES[wv][1];
    o.delay = wv >= 5 ? Math.floor(r(10) * 3) : 0;                   // frames: a spray on the beat, not a stamp
    o.alpha = i < HAND.length ? .55 + .35 * r(9) : .3 + .6 * r(9);
    o.layer = i % 2;                                                   // 0 = bg (behind product), 1 = fg
    o.dof = o.layer === 1 && o.size >= 140;                            // near the lens: defocused
    out.push(o);
  }
  return out;
}

// ------------------------------------------------------------------ word sprites (pre-rendered, scaled per instance)
const BUCKETS = [64, 128, 256];
function wordSprite(word, fam, v, fs, blurPx) {
  const [family, weight] = FAMS[fam];
  const tmp = document.createElement('canvas').getContext('2d');
  const tw = measure(tmp, word, fs, weight, family, fam === 1 ? fs * .04 : 0);
  const padX = fs * (v === 3 ? .28 : .12) + blurPx * 2, padY = fs * (v === 3 ? .16 : .1) + blurPx * 2;
  const capH = fs * (fam === 0 ? .86 : .74);
  const c = document.createElement('canvas'); c.width = Math.ceil(tw + padX * 2); c.height = Math.ceil(capH + padY * 2);
  const x = c.getContext('2d');
  if (blurPx > 0) x.filter = `blur(${blurPx}px)`;
  const cy = c.height / 2 + capH * .5;                               // alphabetic baseline under the caps
  const o = { size: fs, weight, family, align: 'center', spacing: fam === 1 ? fs * .04 : 0 };
  if (v === 3) {
    x.fillStyle = COLD; x.fillRect(blurPx * 2, blurPx * 2, c.width - blurPx * 4, c.height - blurPx * 4);
    text(x, word, c.width / 2, cy, { ...o, color: COL.ink });
  } else if (v === 2) {
    text(x, word, c.width / 2, cy, { ...o, fill: false, stroke: Math.max(2, fs * .03), strokeColor: COL.muted });
  } else text(x, word, c.width / 2, cy, { ...o, color: v === 0 ? COLD : COL.muted });
  return { c, fs };
}

// ------------------------------------------------------------------ value-noise fbm (deterministic)
function hash2(i, j) { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); }
function vn(x, z) {
  const i = Math.floor(x), j = Math.floor(z), fx = x - i, fz = z - j;
  const u = fx * fx * (3 - 2 * fx), v = fz * fz * (3 - 2 * fz);
  const a = hash2(i, j), b = hash2(i + 1, j), c = hash2(i, j + 1), d = hash2(i + 1, j + 1);
  return (a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v) * 2 - 1;
}
const fbm = (x, z) => vn(x, z) * .55 + vn(x * 2.03 + 5.2, z * 2.03 - 1.7) * .28 + vn(x * 4.1 - 3.3, z * 4.1 + 8.1) * .17;

// ------------------------------------------------------------------ the cold SOUND SEA (line grid, vertex colours)
const SEA_Y = -15.5;
function buildSea(width, z0, z1, nx, nz) {
  const n = nx * nz, pos = new Float32Array(n * 3), col = new Float32Array(n * 3), idx = [];
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    pos.set([(i / (nx - 1) - .5) * width, 0, lerp(z0, z1, j / (nz - 1))], (j * nx + i) * 3);
    if (i < nx - 1) idx.push(j * nx + i, j * nx + i + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.setIndex(idx);
  const mesh = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, ...ADDITIVE })); mesh.frustumCulled = false;
  const C = lin(COLD), M = lin('#7f8a94');
  // amp: global amplitude · shocks: [[age (s), strength]] radial rings from under the product · pull: 0..1 suck to centre
  function update(t, amp, shocks, pull, alpha) {
    for (let j = 0; j < nz; j++) {
      const zl = lerp(z0, z1, j / (nz - 1));
      const farFade = Math.pow(seg(zl, z0, z0 + 40), 1.4) * (1 - .4 * seg(zl, z1 - 15, z1));
      for (let i = 0; i < nx; i++) {
        const k = j * nx + i, xl = (i / (nx - 1) - .5) * width;
        const d = Math.hypot(xl, zl);
        let h = amp * (fbm(xl * .07 + t * .22, (zl - t * 4.2) * .07) + .45 * vn(xl * .3 + t * 1.6, (zl - t * 9) * .3) * (.4 + .6 * amp / 2.8));
        let sh = 0;
        for (const [age, s] of shocks) { const R = 6 + age * 70; sh += s * Math.exp(-Math.pow((d - R) / (2.2 + age * 6), 2)) * Math.exp(-age * 2.2); }
        h += sh * 3.2;
        if (pull > 0) h *= 1 - .7 * pull * Math.exp(-d / 30);
        pos[k * 3 + 1] = h;
        const side = 1 - seg(Math.abs(xl), width * .34, width * .5);
        const a = alpha * farFade * side;
        const crest = clamp(.5 + .5 * h / Math.max(.8, amp));
        const kk = (.16 + 1.1 * crest * crest * crest) * a, ks = Math.min(2.5, sh * 1.4) * a;
        col[k * 3] = C.r * kk + M.r * .05 * a + C.r * ks; col[k * 3 + 1] = C.g * kk + M.g * .05 * a + C.g * ks; col[k * 3 + 2] = C.b * kk + M.b * .05 * a + C.b * ks;
      }
    }
    g.attributes.position.needsUpdate = true; g.attributes.color.needsUpdate = true;
  }
  return { mesh, update };
}

// ------------------------------------------------------------------ build
let R = null;
function build(E) {
  const scene = new THREE.Scene(); scene.userData._envSet = true; scene.environmentIntensity = .38; scene.environment = E.env;
  const seaScene = new THREE.Scene(); seaScene.userData.autoEnv = false; seaScene.userData._envSet = true;
  const cam = new THREE.PerspectiveCamera(FOV, W / H, .5, 900);
  const prod = new THREE.Group(); scene.add(prod);
  const hp = createHeadphone(); prod.add(hp.root);
  // cold studio: key top-right, two hard cold rims, a low fill and a front strobe that fires on the kick
  const key = new THREE.DirectionalLight(0xe4edf7, 2.4); key.position.set(30, 34, 30); scene.add(key);
  const rimL = new THREE.DirectionalLight(0xd6e4f2, 4.2); rimL.position.set(-34, 14, -30); scene.add(rimL);
  const rimR = new THREE.DirectionalLight(0xd6e4f2, 3.2); rimR.position.set(36, -6, -26); scene.add(rimR);
  const fill = new THREE.DirectionalLight(0x9fb2c4, .5); fill.position.set(-10, -30, 20); scene.add(fill);
  const strobe = new THREE.DirectionalLight(0xffffff, 0); strobe.position.set(0, 4, 40); scene.add(strobe);
  const sweep = new THREE.PointLight(0xe9f1ff, 0, 60, 1.6); scene.add(sweep);
  // gold rings: emissive pulse (the ANC fighting back)
  const rings = hp.cups.map(c => c.userData.parts.ring.material);
  rings.forEach(m => { m.emissive = lin(COL.gold); m.emissiveIntensity = 0; });
  // sea
  const sea = buildSea(150, -150, 40, 160, 120);
  const seaG = new THREE.Group(); seaG.position.y = SEA_Y; seaG.add(sea.mesh); seaScene.add(seaG);
  // own motion blur for the spin / the slam: the product alone is rendered N times at half resolution into a float
  // target and averaged (premultiplied), then laid over the 3D layer — 2D layers and post are not re-run per sample
  const rtOpt = { type: THREE.HalfFloatType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: true };
  const rtS = new THREE.WebGLRenderTarget(W * BLUR_RES, H * BLUR_RES, rtOpt);
  const rtAcc = new THREE.WebGLRenderTarget(W * BLUR_RES, H * BLUR_RES, { ...rtOpt, depthBuffer: false });
  const QV = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }';
  const accMat = new THREE.ShaderMaterial({ vertexShader: QV, fragmentShader: 'uniform sampler2D tSrc; uniform float uW; varying vec2 vUv; void main(){ gl_FragColor = texture2D(tSrc, vUv)*uW; }',
    uniforms: { tSrc: { value: rtS.texture }, uW: { value: 1 } }, depthTest: false, depthWrite: false, transparent: true,
    blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor });
  // composite with a horizontal smear that fills the gaps between samples (spin and slam both move mostly sideways)
  const compMat = new THREE.ShaderMaterial({ vertexShader: QV, fragmentShader: `uniform sampler2D tSrc; uniform float uBlur; varying vec2 vUv;
    void main(){ vec4 c = vec4(0.); for (int k = 0; k < 12; k++) { float f = float(k)/11. - .5; c += texture2D(tSrc, vUv + vec2(f*uBlur, 0.)); } gl_FragColor = c/12.; }`,
    uniforms: { tSrc: { value: rtAcc.texture }, uBlur: { value: 0 } }, depthTest: false, depthWrite: false, transparent: true,
    blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor });
  const quadGeo = new THREE.PlaneGeometry(2, 2);
  const accScene = new THREE.Scene(); const accQ = new THREE.Mesh(quadGeo, accMat); accQ.frustumCulled = false; accScene.add(accQ);
  // the composite quad lives in the sea scene (clip-space vertex shader, drawn last): one render3D call per frame
  const compQ = new THREE.Mesh(quadGeo, compMat); compQ.frustumCulled = false; compQ.renderOrder = 999; compQ.visible = false; seaScene.add(compQ);
  const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  // word sprites
  const table = wordTable(), sprites = new Map();
  for (const w of table) {
    const fs = BUCKETS.find(b => b >= w.size * 1.02) || 256;
    const blur = w.dof ? Math.round(fs * .035) : 0;
    const key = `${w.word}|${w.fam}|${w.v}|${fs}|${blur}`;
    if (!sprites.has(key)) sprites.set(key, wordSprite(w.word, w.fam, w.v, fs, blur));
    w.sprite = sprites.get(key);
  }
  // villain 'NOISE' (white + red + blue ghosts) at 400 px
  const vil = {};
  const vtmp = document.createElement('canvas').getContext('2d');
  const vw = Math.ceil(measure(vtmp, 'NOISE', 400, 400, FONT.impact)), vcap = 400 * .86;
  for (const [k, c] of [['w', COL.white], ['r', '#ff4040'], ['b', '#4060ff']]) {
    const cv = document.createElement('canvas'); cv.width = vw + 40; cv.height = Math.ceil(vcap + 40);
    text(cv.getContext('2d'), 'NOISE', cv.width / 2, 20 + vcap, { size: 400, weight: 400, family: FONT.impact, color: c });
    vil[k] = cv;
  }
  vil.capW = vw; vil.capH = vcap;
  // cold haze: two fbm cloud canvases, drawn big and drifting
  const haze = [0, 1].map(s => {
    const c = document.createElement('canvas'); c.width = 180; c.height = 320; const x = c.getContext('2d');
    const id = x.createImageData(180, 320);
    for (let j = 0; j < 320; j++) for (let i = 0; i < 180; i++) {
      const v = clamp(.5 + .55 * (vn(i * .035 + s * 9, j * .035) * .6 + vn(i * .09 + 3 + s, j * .09 - 2) * .3 + vn(i * .2, j * .2 + s * 4) * .1));
      const k = (j * 180 + i) * 4; const a = Math.pow(v, 2.2);
      id.data[k] = 200; id.data[k + 1] = 212; id.data[k + 2] = 224; id.data[k + 3] = a * 255;
    }
    x.putImageData(id, 0, 0); return c;
  });
  return { scene, seaScene, rtS, rtAcc, accMat, compMat, accScene, compQ, ortho, cam, prod, hp, key, rimL, rimR, fill, strobe, sweep, rings, sea, seaG, table, vil, haze };
}

// ------------------------------------------------------------------ pose (pure function of local beat lb)
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const backIn = (x, s) => { x = clamp(x); return (s + 1) * x * x * x - s * x * x; };
// cup spread factor sx (1 = base, 1.55 = pushed apart)
function spread(lb) {
  if (lb < LB_STOP) return 1;
  if (lb < LB_PUSH1) {
    const u = seg(lb, LB_STOP + 1 / 12, LB_PUSH1);
    const kick35 = lb >= 7 ? .07 * Math.exp(-(lb - 7) * BEAT / .1) * (1 - Math.exp(-(lb - 7) * BEAT / .015)) * 1.5 * (1 - seg(lb, 7.25, LB_PUSH1)) : 0;   // b35: a second shove
    return 1 + .55 * (eout(u) * .82 + u * .18) + kick35;
  }
  return lerp(1.55, 1, backIn(seg(lb, LB_PUSH1, LB_END), .8));  // anticipation, then the slam (hard stop f431)
}
// cup yaw: cushions turned toward camera (front match), splayed by the push, jaws shut on the clamp
function cupYaw(lb) {
  if (lb < LB_STOP) return lerp({ ...OPEN, ...PRB() }.yaw, 20 * DEG, openK(lb));
  if (lb < LB_PUSH1) return lerp(20, 30, eout(seg(lb, LB_STOP, LB_PUSH1))) * DEG;
  return lerp(30, 0, backIn(seg(lb, LB_PUSH1, LB_END), .8)) * DEG;
}
function spinY(lb) {
  let y = 8 * Math.PI * ein(seg(lb, 0, LB_STOP));
  if (lb >= LB_STOP) { const d = (lb - LB_STOP) * BEAT; y += 4.5 * DEG * Math.sin(d * 38) * Math.exp(-d * 9); }   // CHUNK recoil
  return y;
}
// camera: product ~960 px wide at b28 (match of the Droste cell) -> 760 px by b29 -> slow pressure push-in ->
// eases back on the push so the splayed cups stay in frame -> lunges in on the clamp
// OPENING MATCH (b28.0 = f336): the projected product equals s05's last Droste frame (f335: ~1010 px wide, headband
// top y~380, cups y~960-1530, raised 3/4 front with the cushions turned toward the lens), then eases to 760 px by b29.
const PRB = () => (globalThis.__S06P || {});
const OPEN = { px: 54, cupY: 1235, yaw: 34 * DEG, elev: 14 * DEG };
const openK = lb => eout(seg(lb, 0, 1));
export function camState(lb) {
  const O = { ...OPEN, ...PRB() };
  let px = lerp(O.px, 39, openK(lb));                            // px per world unit at the product
  px *= 1 + .07 * eio(seg(lb, 1, LB_STOP));
  px *= 1 - .09 * eout(seg(lb, LB_STOP, LB_PUSH1));
  px *= 1 + .16 * expoIn(seg(lb, LB_PUSH1, LB_END));
  const d = H / (2 * Math.tan(FOV / 2 * DEG) * px);
  const cupY = lerp(O.cupY, 1030, openK(lb)) - 20 * eio(seg(lb, LB_STOP, LB_PUSH1)) + 10 * expoIn(seg(lb, LB_PUSH1, LB_END));
  const elev = lerp(O.elev, Math.atan2(2.5, d), openK(lb));       // raised camera at the match, 2.5 units after b29
  return { d, cupY, camY: lb >= 1 ? 2.5 : Math.tan(elev) * d };
}

// b36 hand-off (for s07): the clamped pose — product rotation (TILT, 8pi ≡ 0, 0), cups at base (x ±7.4, y -4.5, yaw 0),
// sliders x ±7.95, band scale 1; camera at (0, 2.5, camState(LB_END).d) looking at the origin, fov 30, then
// setViewOffset so the cups' midpoint lands on screen y = camState(LB_END).cupY. The crushed hairline sits there.
export const END_POSE = { tilt: TILT, fov: FOV, camY: 2.5, lb: LB_END };

function pose(lb, Fr) {
  const { hp, prod } = R;
  prod.rotation.set(TILT, spinY(lb), 0);
  prod.position.set(0, .25 * Math.sin(lb * BEAT * 2.1), 0);
  const sx = spread(lb), yaw = cupYaw(lb);
  const trem = lb >= LB_STOP && lb < LB_PUSH1 ? .08 : lb >= LB_PUSH1 && lb < LB_END ? .05 : 0;
  hp.band.group.scale.x = sx;
  hp.sliders.forEach((g, i) => { const s = i ? 1 : -1; g.position.set(s * 7.95 * sx, .1, 0); });
  hp.cups.forEach((c, i) => {
    const s = i ? 1 : -1;
    const tx = trem * (rnd(Fr * 3.7 + i * 11) - .5) * 2, ty = trem * (rnd(Fr * 5.3 + i * 17) - .5) * 2;
    c.position.set(s * 7.4 * sx + tx, -4.5 + ty, 0);
    c.rotation.set(0, s * yaw, -s * Math.PI / 2);
  });
  prod.updateMatrixWorld(true);
}
const tv = new THREE.Vector3();
function project(cam, p) { tv.copy(p).project(cam); return [(tv.x + 1) / 2 * W, (1 - tv.y) / 2 * H]; }

// ------------------------------------------------------------------ 2D: background
function drawBg(bg, lb, t, press, kick) {
  bg.fillStyle = '#060708'; bg.fillRect(0, 0, W, H);
  // cold glow behind the product + horizon haze
  let g = bg.createRadialGradient(540, 980, 0, 540, 980, 980);
  g.addColorStop(0, `rgba(120,134,150,${.2 + .1 * press + .08 * kick})`); g.addColorStop(.55, 'rgba(40,46,54,.12)'); g.addColorStop(1, 'rgba(6,7,8,0)');
  bg.fillStyle = g; bg.fillRect(0, 0, W, H);
  // drifting fog
  bg.save(); bg.globalCompositeOperation = 'lighter'; bg.imageSmoothingQuality = 'high';
  R.haze.slice(0, 1).forEach((c, i) => {
    bg.globalAlpha = (.07 + .035 * press + .035 * kick) * (i ? .8 : 1);
    const dx = (i ? -1 : 1) * t * (18 + 40 * press) - 200, dy = -t * 12 * (i ? 1.4 : 1) - 150;
    bg.drawImage(c, dx, dy, 1500, 2666);
  });
  // two searchlights scanning from below (the city)
  for (let i = 0; i < 2; i++) {
    const sxp = i ? 1180 : -100, ang = -Math.PI / 2 + (i ? -1 : 1) * (.32 + .22 * Math.sin(t * (1.1 + press * 2.2) + i * 2));
    bg.save(); bg.translate(sxp, 1900); bg.rotate(ang + Math.PI / 2);
    const lg = bg.createLinearGradient(0, 0, 0, -2200);
    lg.addColorStop(0, `rgba(210,222,235,${.07 + .05 * press})`); lg.addColorStop(1, 'rgba(210,222,235,0)');
    bg.fillStyle = lg; bg.globalAlpha = 1; bg.beginPath(); bg.moveTo(-12, 0); bg.lineTo(-230, -2200); bg.lineTo(230, -2200); bg.lineTo(12, 0); bg.fill();
    bg.restore();
  }
  bg.restore();
}

// ------------------------------------------------------------------ 2D: sound-pressure streaks
// cold specks converging on the product from everywhere (faster and longer with the pressure), blasted outward by the
// villain's burst at b34, then sucked into the clamp. Pure function of lb.
function pressureStreaks(ctx, lb, t, press) {
  const n = 150, cx = NOISE_C[0], cy = NOISE_C[1];
  const blast = seg(lb, LB_STOP, LB_STOP + 1.2), suck = ein(seg(lb, LB_PUSH1, LB_END));
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const a = rnd(i * 3.71 + .3) * TAU, sp = .5 + rnd(i * 1.93 + .7);
    // radial phase: 1 = far rim, 0 = centre; inward travel speed grows with pressure
    const rate = (.18 + 1.6 * press) * sp;
    let ph = 1 - ((rnd(i * 5.17) + t * rate * .45 + press * sp * 1.6) % 1);
    let r = 120 + ph * 1150, dir = -1, len = (6 + 140 * press * sp) * (.4 + .6 * ph);
    if (blast > 0 && blast < 1) { r = 200 + (ph * 300 + 1400 * eout(blast)) ; dir = 1; len = 220 * (1 - blast) * sp + 10; }
    else if (blast >= 1 && suck <= 0) { r = 1300 + ph * 300; len = 0; }
    if (suck > 0) { r = lerp(1300 + ph * 300, 30, suck); dir = -1; len = 420 * Math.sin(Math.PI * suck) * sp; }
    if (len < 1) continue;
    const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r * 1.15;
    if (x < -50 || x > W + 50 || y < -50 || y > H + 50) continue;
    const ex = x - Math.cos(a) * len * dir, ey = y - Math.sin(a) * len * dir * 1.15;
    const al = (.12 + .4 * rnd(i * 8.3)) * (.35 + .65 * press + suck) * Math.min(1, ph * 4 + .2);
    const g = ctx.createLinearGradient(x, y, ex, ey);
    g.addColorStop(0, `rgba(225,235,245,${al})`); g.addColorStop(1, 'rgba(225,235,245,0)');
    ctx.strokeStyle = g; ctx.lineWidth = .8 + 2.2 * rnd(i * 6.1);
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ex, ey); ctx.stroke();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ 2D: storm words
function drawWords(ctx, layer, lb, Fr, lf) {
  const suck = expoIn(seg(lb, LB_PUSH1, LB_END));
  const pushOut = eout(seg(lb, LB_STOP, LB_PUSH1)) * (1 - suck);
  const jit = lb >= 4 ? 8 : 0, jIdx = Math.floor(Fr / 3);
  ctx.save(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  for (const w of R.table) {
    if (w.layer !== layer) continue;
    const life = lf - (w.lb * 12 + w.delay);              // frames since birth
    if (life < 0) continue;
    let sc = w.size / w.sprite.fs;
    sc *= 1 + .3 * (1 - expoOut(clamp(life / 3)));        // pop 1.3 -> 1 over 3 frames
    sc *= 1 + .0016 * life * (layer ? 1.4 : 1);           // pressure: the noise creeps toward the lens
    let x = w.x, y = w.y;
    const dx = x - NOISE_C[0], dy = y - NOISE_C[1], dl = Math.hypot(dx, dy) || 1;
    // b34: the villain's burst blasts the storm outward (central words furthest), clearing the product for the push
    const blast = pushOut * (90 + 420 * (1 - clamp(dl / 1000))) * (layer ? 1.25 : 1);
    const drift = life * (layer ? .9 : .45) + blast;
    x += dx / dl * drift; y += dy / dl * drift;
    if (jit) { x += (rnd(w.i * 3.1 + jIdx * 7.7) - .5) * 2 * jit; y += (rnd(w.i * 5.9 + jIdx * 3.3) - .5) * 2 * jit; }
    let a = w.alpha * (layer ? .85 : w.i < 8 ? .85 : .7) * (1 - .3 * pushOut);
    if (lb >= 5) a *= (jIdx + w.i) % 2 ? .6 : 1;            // strobe 1 <-> .6 every 3 frames
    const sp = w.sprite.c;
    if (suck > 0) {
      // sucked into the clamp along a slight spiral, with a 2-step ghost trail (2D layers get no motion blur)
      const u = clamp(seg(lb, LB_PUSH1 + (w.i % 7) * .012, LB_END));
      for (let g = 2; g >= 0; g--) {
        const k = ein(clamp(u - g * .07)); if (g && k <= 0) continue;
        const sw = .5 * k * (w.i % 2 ? 1 : -1);
        const rx = (x - NOISE_C[0]) * (1 - k), ry = (y - NOISE_C[1]) * (1 - k);
        const px = NOISE_C[0] + rx * Math.cos(sw) - ry * Math.sin(sw), py = NOISE_C[1] + rx * Math.sin(sw) + ry * Math.cos(sw);
        const s2 = sc * (1 - k); if (s2 <= .002) continue;
        ctx.globalAlpha = a * (g ? .3 / g : 1);
        ctx.setTransform(s2, 0, 0, s2, px, py); if (w.rot) ctx.rotate(w.rot);
        ctx.drawImage(sp, -sp.width / 2, -sp.height / 2);
      }
      continue;
    }
    ctx.globalAlpha = a;
    ctx.setTransform(sc, 0, 0, sc, x, y);
    if (w.rot) { ctx.rotate(w.rot); }
    ctx.drawImage(sp, -sp.width / 2, -sp.height / 2);
  }
  ctx.restore();
}

// ------------------------------------------------------------------ 2D: villain 'NOISE' (bg, behind the cups)
function drawVillain(bg, lb, Fr, gap, gap0, gapMax, cx, cy) {
  if (lb < LB_STOP) return;
  const V2 = R.vil;
  const born = expoOut(seg(lb, LB_STOP, LB_STOP + 2 / 12));
  let wW, hH;
  if (lb < LB_PUSH1) {
    wW = Math.max(gap * 1.32, 240) * born;                   // wider than the gap: the cushions hide its ends
    hH = 290 * lerp(1, 1.12, eout(seg(lb, LB_STOP, LB_PUSH1))) * lerp(.5, 1, born);
  } else {
    const k = clamp((gap - gap0) / Math.max(1, gapMax - gap0));
    wW = Math.max(6, gapMax * 1.32 * Math.max(.015, k));
    hH = 290 * lerp(1.15, 1.12, k);
  }
  const trem = lb < LB_END ? 1 : 0;
  const ox = (rnd(Fr * 2.3 + 1) - .5) * 20 * trem, oy = (rnd(Fr * 4.1 + 2) - .5) * 20 * trem;
  const rot = (rnd(Fr * 6.7 + 3) - .5) * 8 * DEG * trem * clamp(wW / 300);
  bg.save(); bg.translate(cx + ox, cy + oy); bg.rotate(rot);
  const sx = wW / V2.capW, sy = hH / V2.capH;
  const dw = V2.w.width * sx, dh = V2.w.height * sy;
  if (wW <= 14) {
    // the crushed word: a hot white hairline
    bg.shadowColor = 'rgba(235,242,255,.95)'; bg.shadowBlur = 24; bg.fillStyle = '#ffffff';
    bg.fillRect(-wW / 2, -hH / 2, wW, hH); bg.fillRect(-wW / 2, -hH / 2, wW, hH);
    bg.restore(); return;
  }
  // R / B ghosts
  bg.globalCompositeOperation = 'lighter'; bg.globalAlpha = .5;
  const gs = 8 + 10 * (1 - born);
  bg.drawImage(V2.r, -dw / 2 - gs, -dh / 2, dw, dh);
  bg.drawImage(V2.b, -dw / 2 + gs, -dh / 2, dw, dh);
  bg.globalCompositeOperation = 'source-over'; bg.globalAlpha = 1;
  // white core, sliced: every other frame a few bands shear sideways
  const bands = 7, bh = V2.w.height / bands;
  for (let k = 0; k < bands; k++) {
    const sh = Fr % 2 === 0 && rnd(Fr * 1.3 + k * 9.1) < .35 ? (rnd(Fr * 2.9 + k * 3.7) - .5) * 60 : 0;
    bg.drawImage(V2.w, 0, k * bh, V2.w.width, bh, -dw / 2 + sh, -dh / 2 + k * bh * sy, dw, bh * sy + .5);
  }
  bg.restore();
}

// ------------------------------------------------------------------ 2D: HUD
const HUD_X = 80;
function drawHud(fg, lb, Fr, lf, t) {
  const intro = seg(lf, 0, 6);
  // scrim so the HUD stays legible over the storm
  const g = fg.createLinearGradient(0, 160, 0, 500);
  g.addColorStop(0, 'rgba(5,6,7,.82)'); g.addColorStop(.55, 'rgba(5,6,7,.55)'); g.addColorStop(1, 'rgba(5,6,7,0)');
  fg.fillStyle = g; fg.fillRect(0, 0, W, 500);
  const crush = seg(lb, LB_PUSH1, LB_END);
  const tr = lb >= 4 ? 2 * (1 + crush * 2) : 0;
  const jx = (rnd(Fr * 9.1) - .5) * tr, jy = (rnd(Fr * 4.4) - .5) * tr;
  fg.save(); fg.translate(jx, jy);
  // label (decodes on)
  const L = 'AMBIENT NOISE', n = Math.floor(clamp(lf * 3.5, 0, 13));
  let s = L.slice(0, n); if (n < 13) s += '#%/'.charAt(Fr % 3);
  text(fg, s, HUD_X, 262, { size: 30, weight: 700, family: FONT.mono, color: COL.muted, align: 'left', spacing: 6 });
  // live dot + 'LIVE'
  const blink = Math.floor(lf / 6) % 2 === 0 ? 1 : .35;
  fg.fillStyle = COLD; fg.globalAlpha = blink * intro; fg.beginPath(); fg.arc(870, 252, 7, 0, TAU); fg.fill(); fg.globalAlpha = 1;
  text(fg, 'LIVE', 1000, 262, { size: 30, weight: 700, family: FONT.mono, color: COLD, align: 'right', spacing: 6, alpha: intro });
  // counter 38 -> 118 dB (ein), fixed-advance digits; flickers at 118 once the spin stops
  const lvl = ein(seg(lb, 0, LB_STOP));
  let val = Math.round(38 + 80 * lvl);
  let ca = 1;
  if (lb >= LB_STOP) { ca = (Fr % 4 < 2) ? 1 : .45; if (lb >= LB_PUSH1 && Fr % 3 === 1) ca = .2; }
  const ds = String(val), adv = measure(fg, '0', 96, 400, FONT.impact) + 2;
  for (let i = 0; i < ds.length; i++) text(fg, ds[i], HUD_X + adv * (i + .5), 360, { size: 96, weight: 400, family: FONT.impact, color: COLD, alpha: ca });
  text(fg, 'dB', HUD_X + adv * ds.length + 16, 360, { size: 40, weight: 500, family: FONT.display, color: COL.gold, align: 'left' });
  // segmented meter: 40 segments over 920 px at y 400, jittering front edge, peak hold
  const segs = 40, sw = 920 / segs, y = 396;
  const draw = intro;
  fg.fillStyle = 'rgba(154,151,143,.28)';
  for (let i = 0; i < segs * draw; i++) fg.fillRect(HUD_X + i * sw, y + 5, sw - 4, 2);
  let level = lerp(.02, 1, Math.pow(lvl, .85));
  const jit = (rnd(Fr * 1.7 + 3) - .5) * (.03 + .1 * lvl);
  if (lb >= LB_STOP) level = Fr % 2 ? 1 : .94 + .06 * rnd(Fr);
  const on = clamp(level + jit) * segs;
  for (let i = 0; i < segs; i++) {
    if (i >= on) break;
    const hot = i / segs > .82;
    fg.fillStyle = hot ? '#ffffff' : COLD; fg.globalAlpha = (hot ? 1 : .85) * (i + 1 > on ? on - i : 1);
    fg.fillRect(HUD_X + i * sw, y, sw - 4, 12);
  }
  fg.globalAlpha = 1;
  const peak = Math.min(segs - 1, Math.floor(clamp(lerp(.04, 1, Math.pow(lvl, .7)) + .04) * segs));
  fg.fillStyle = COLD; fg.fillRect(HUD_X + peak * sw, y - 6, 3, 24);
  fg.restore();
}

// samples of the product-only motion blur (the spin becomes a blur; the slam)
function blurSamples(lb) {
  if (lb >= 4 && lb < LB_STOP + .02) return lb < 4.75 ? 3 : 4;
  if (lb >= LB_PUSH1 + 2.5 / 12 && lb < LB_END + .02) return 3;
  return 1;
}

// ------------------------------------------------------------------ the scene
export default {
  id: 's06-noise', start: 28, end: 36,
  cutIn: 'none',
  init(E) { R = build(E); },

  draw(E, lt, t) {
    const fx = E.fx, bg = E.bg, fg = E.fg;
    // snap to the frame grid: b2s(28) = 11.200000000000001, so lt*30 can come out as 71.99999 on the b34 hit frame
    let lf = lt * 30; if (Math.abs(lf - Math.round(lf)) < 1e-3) lf = Math.round(lf);
    lf = Math.max(0, lf); lt = lf / 30;
    const Fr = Math.round(lf), lb = lf / 12;
    const { scene, cam, prod, hp } = R;
    const press = ein(seg(lb, 0, LB_STOP));                 // pressure 0..1
    const beatPh = lb - Math.floor(lb), kick = Math.exp(-beatPh * BEAT / .09);

    // ---------------- pose + camera
    pose(lb, Fr);
    const cs = camState(lb);
    cam.fov = FOV; cam.position.set(0, cs.camY, cs.d); cam.up.set(0, 1, 0); cam.lookAt(0, 0, 0);
    cam.clearViewOffset(); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const cupMid = hp.cups[0].getWorldPosition(new THREE.Vector3()).add(hp.cups[1].getWorldPosition(new THREE.Vector3())).multiplyScalar(.5);
    const p0 = project(cam, cupMid);
    cam.setViewOffset(W, H, 0, -(cs.cupY - p0[1]), W, H); cam.updateProjectionMatrix();
    // inner faces of the cushions -> screen gap (drives the villain's width)
    const inner = hp.cups.map(c => project(cam, c.localToWorld(V(0, -2.95, 0))));
    const gap = Math.abs(inner[1][0] - inner[0][0]), midX = (inner[0][0] + inner[1][0]) / 2, midY = (inner[0][1] + inner[1][1]) / 2;
    // reference gaps (base pose and fully pushed) for the crush mapping — computed analytically from the pose functions
    const gapAt = s => { const save = [hp.cups[0].position.x, hp.cups[1].position.x]; hp.cups.forEach((c, i) => { c.position.x = (i ? 1 : -1) * 7.4 * s; c.updateMatrixWorld(true); });
      const q = hp.cups.map(c => project(cam, c.localToWorld(V(0, -2.95, 0)))); hp.cups.forEach((c, i) => { c.position.x = save[i]; c.updateMatrixWorld(true); }); return Math.abs(q[1][0] - q[0][0]); };
    const gap0 = lb >= LB_PUSH1 ? gapAt(1) : 0, gapMax = lb >= LB_PUSH1 ? gapAt(1.55) : 0;
    if (PRB().bbox) {                                                // probe (dev only): projected product bbox
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; const v = new THREE.Vector3();
      prod.traverse(o => { if (!o.isMesh || !o.visible) return; const pa = o.geometry.attributes.position;
        for (let i = 0; i < pa.count; i += 3) { v.fromBufferAttribute(pa, i).applyMatrix4(o.matrixWorld); const q = project(cam, v);
          x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); } });
      const cy = hp.cups.map(c => { let a = 1e9, b = -1e9; c.traverse(o => { if (!o.isMesh) return; const pa = o.geometry.attributes.position;
        for (let i = 0; i < pa.count; i += 3) { v.fromBufferAttribute(pa, i).applyMatrix4(o.matrixWorld); const q = project(cam, v); a = Math.min(a, q[1]); b = Math.max(b, q[1]); } }); return [a, b]; });
      globalThis.__S06BB = { x0, x1, y0, y1, w: x1 - x0, cups: cy };
    }

    // ---------------- lights
    R.strobe.intensity = 3.2 * kick * (.4 + .6 * press) + (lb >= LB_STOP ? 4 * Math.exp(-(lb - LB_STOP) * BEAT / .07) : 0);
    const swA = t * 2.4 + press * 6;
    R.sweep.position.set(Math.sin(swA) * 26, 10 + 6 * Math.cos(swA * .7), 18 + 8 * Math.cos(swA)); R.sweep.intensity = 260 * (.3 + .7 * press);
    const slam = lb >= LB_PUSH1 ? ein(seg(lb, LB_PUSH1, LB_END)) : 0;
    R.rimL.intensity = 4.2 + 2 * press + 5 * slam; R.rimR.intensity = 3.2 + 5 * slam; R.key.intensity = 2.3 + .6 * kick + 1.5 * slam;
    R.strobe.intensity += 3 * slam;
    const ringI = .15 + 1.4 * kick * (.4 + .6 * press) + (lb >= LB_PUSH1 ? 2.5 * seg(lb, LB_PUSH1, LB_END) : 0);
    R.rings.forEach(m => { m.emissiveIntensity = ringI; });

    // ---------------- sea
    const shocks = [];
    for (let k = 0; k <= 7; k++) { const age = (lb - k) * BEAT; if (age >= 0 && age < 1.6) shocks.push([age, k === 6 ? 1.6 : .45 + .5 * k / 7]); }
    const amp = lerp(.6, 2.8, ein(seg(lb, 0, LB_STOP))) * (1 + .25 * seg(lb, LB_STOP, LB_PUSH1));
    R.sea.update(t, amp, shocks, expoIn(seg(lb, LB_PUSH1, LB_END)), .32 * seg(lf, 0, 4) + .02);

    // ---------------- bg2d: haze, back half of the storm, villain
    drawBg(bg, lb, t, press, kick);
    pressureStreaks(bg, lb, t, press);
    drawWords(bg, 0, lb, Fr, lf);
    drawVillain(bg, lb, Fr, gap, gap0, gapMax, midX, midY);

    // ---------------- 3D
    {
      const N = blurSamples(lb);
      if (N > 1) {
        const r = E.renderer, shutter = lb >= LB_PUSH1 ? .9 : .75;   // in frames
        // smear width (uv) ~ screen travel between two samples
        const pxu = H / (2 * Math.tan(FOV / 2 * DEG) * camState(lb).d);
        const travel = lb < LB_STOP + .02 ? 8 * Math.PI * 3 * Math.pow(seg(lb, 0, LB_STOP), 2) / 72 * 8.5 * pxu
          : Math.abs(spread(lb + .5 / 12) - spread(lb - .5 / 12)) * 7.4 * pxu;
        R.compMat.uniforms.uBlur.value = Math.min(160, travel * shutter / N * 1.15) / W;
        r.setClearColor(0x000000, 0); r.setRenderTarget(R.rtAcc); r.clear(true, true, true);
        R.accMat.uniforms.uW.value = 1 / N;
        for (let i = 0; i < N; i++) {
          const lbi = lb + ((i + .5) / N - .5) * shutter / 12;
          pose(lbi, Fr);
          r.setRenderTarget(R.rtS); r.clear(true, true, true); r.render(scene, cam);
          r.setRenderTarget(R.rtAcc); r.render(R.accScene, R.ortho);
        }
        pose(lb, Fr);
        R.compQ.visible = true; E.render3D(R.seaScene, cam); R.compQ.visible = false;
      } else { scene.add(R.seaG); E.render3D(scene, cam); R.seaScene.add(R.seaG); }
    }

    // ---------------- fg2d: front half of the storm (defocused giants), HUD
    drawWords(fg, 1, lb, Fr, lf);
    drawHud(fg, lb, Fr, lf, t);

    // ---------------- post: the cold grade
    fx.exposure = .88; fx.bloom = .45; fx.bloomThreshold = .84;
    fx.sat = .3; fx.tint = [.92, .96, 1.04]; fx.contrast = 1.05; fx.vignette = .45;
    fx.grain = lerp(.05, .15, ein(seg(lb, 2, 6)));
    fx.rgb = lerp(.003, .02, ein(seg(lb, 2, 6)));
    fx.scanlines = .3 * ein(seg(lb, 2, 6)) * (lb < LB_END ? 1 : 0);
    // b28 downbeat punch (match cut from the Droste cell)
    downbeatPunch(fx, t, b2s(28) - .5 / 30, { flash: .25, flashFrames: 1, zoom: 1.08, rgb: .02, zoomBlur: .22, shake: .008 });
    // every beat: zoom 1.03 (4 frames) + rgb kick
    for (let k = 1; k <= 7; k++) {
      const fr = (lb - k) * 12; if (fr < 0 || fr >= 4) continue;
      const kk = 1 - fr / 4; fx.zoom *= 1 + .03 * kk; fx.rgb = Math.max(fx.rgb, .005 + .003 * kk);
    }
    // doublings: a 2-frame glitch blip (b29, 30, 31, 32, 32.5, 33, 33.5)
    for (const d of [1, 2, 3, 4, 4.5, 5, 5.5]) {
      const fr = (lb - d) * 12; if (fr >= 0 && fr < 1.5) { fx.glitch = Math.max(fx.glitch, .1 + .08 * d / 5.5); fx.glitchSeed = 31 + d * 7; }
    }
    // b32-34 glitch ramp, seed every 3 frames
    if (lb >= 4 && lb < LB_STOP) { fx.glitch = Math.max(fx.glitch, lerp(.05, .4, ein(seg(lb, 4, 6)))); fx.glitchSeed = Math.floor(Fr / 3) * 7.13 + 1; }
    // pixelate for 1 frame at b33.0 and b34.0
    if (Fr === 60 || Fr === 72) fx.pixelate = 24;
    // b34 dead stop: CHUNK
    if (lb >= LB_STOP) {
      const fr = (lb - LB_STOP) * 12;
      if (fr < 8) {
        const k = 1 - fr / 8;
        fx.shake = [(rnd(Fr * 3.3) - .5) * 2 * .012 * k, (rnd(Fr * 7.9) - .5) * 2 * .012 * k];
        fx.zoom *= 1 + .06 * (1 - expoOut(fr / 6));
        fx.rgb = Math.max(fx.rgb, .03 * k);
      }
      fx.glitch = Math.max(fx.glitch, .25 * Math.max(0, 1 - fr / 4));
      fx.glitchSeed = Math.floor(Fr / 2) * 3.7 + 5;
    }
    // b34-35.5 push: liquid displace + continuous shake
    if (lb >= LB_STOP && lb < LB_END + .1) {
      const k = lb < LB_PUSH1 ? 1 : 1 - seg(lb, LB_PUSH1, LB_END) * .5;
      fx.displace = .01 * k; fx.displaceScale = 3.5;
      fx.shake = [fx.shake[0] + (rnd(Fr * 1.9 + 4) - .5) * .006, fx.shake[1] + (rnd(Fr * 2.7 + 8) - .5) * .006];
      fx.rot = .012 * noise1(lb * 6) * k;
    } else fx.rot = .008 * noise1(lb * 3.3) * press;
    // b35.5-36 clamp: zoom blur into the centre, glitch fades out
    if (lb >= LB_PUSH1) {
      const k = seg(lb, LB_PUSH1, LB_END);
      fx.zoomBlur = Math.max(fx.zoomBlur, .3 * ein(k)); fx.zoomCenter = [midX / W, 1 - midY / H];
      fx.glitch = .15 * (1 - k); fx.rgb = Math.max(fx.rgb, .012 + .02 * ein(k));
    }
  },
};
