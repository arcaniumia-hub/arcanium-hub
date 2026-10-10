// s07-mute — THE MUTE (b36-40): the clamped product detonates on the click, the ANC ring freezes the explosion mid-air,
// the dB counter dives 118 -> 64 -> 11 -> −42 dB on 1/16 steps while every post effect switches off one per step and the
// colour drains. Then 1.0 s of real digital silence: bullet time, nothing moves but the camera (a slow dolly / orbit / roll
// into the suspended parts and 100k dust particles) and a cold key light gliding over the metal. b39 the debris trembles;
// b39.5 REWIND-SNAP: every part, particle and word rushes back and the product is whole exactly on the DROP 2 downbeat.
//
// Everything is a pure function of t. Each object (part pivot, particle, word) has a designed FROZEN offset O and a
// freeze time τF = 0.1 s + d / v (d = its screen distance from the centre in the freeze camera, v = 1400 px / 4 frames).
// Flight: offset(τ) = O · h(min(τ, τF)) / h(τF), h(τ) = 1 − exp(−τ / TC)  (still flying fast when the ring hits it).
// Rewind: offset · P, P = 1 − ease(seg(b, 39.5, 40)).
//
// Layers: bg2d ink + cold glow + the blasted/frozen noise words (half-res, defocused, parallax with the camera)
//         3D   the 22 parts of the exploded headphone (pivots at their own centres) + 100k debris points (one ShaderMaterial)
//         fg2d s06 HUD tail, dive numerals (slot rolls), −42 dB, ANC ● ON, the italic line, the gold freeze ring.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoIn, expoOut, rnd, text, measure, ancRing, b2s, COL, FONT, ADDITIVE, dotTexture } from '../lib.js';
import { createHeadphone } from '../model.js';
import { wordTable, camState } from './s06-noise.js';

const B0 = 36, T0 = b2s(36), TFR = b2s(36.25);
const DEG = Math.PI / 180;
const FOV = 30, TILT = 8 * DEG;
const RING_V = 1400 / (4 / 30);             // px per second (1400 px in 4 frames)
const TC = .2;                              // flight time constant (s)
const hF = tau => 1 - Math.exp(-Math.max(0, tau) / TC);
const C_SCR = [540, 960];                   // ring centre / freeze reference
const NOISE_C = [540, 1000];                // where s06 sucked the storm in
const COLD = '#e9eef2';
const MINUS = '−';
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const NP = 100000;
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const C0 = V3(0, -2, 0);                    // detonation centre (prod-local)

// rewind ease: accelerating suck into the downbeat (visible over all 6 frames, unlike expoIn which waits 3 frames)
const rewindEase = x => { x = clamp(x); return Math.pow(x, 2.4); };

// ------------------------------------------------------------------ the frozen composition
// Designed in the screen space of the END of the silent drift (camera K1): a two-armed spiral galaxy around a clear
// centre where the −42 dB sits. Arm 0 starts left of the type and curls over the top to the right; arm 1 starts right
// and curls under the bottom to the left. Small precious parts sit on the inner turns, big shells/cushions on the
// outer turns (cropped by the frame = depth). Depth alternates near / far for parallax during the orbit.
// ORIENT: [normal tilt x, normal tilt y, spin deg] relative to facing the K1 camera.
const ARMS = [
  ['L.magnet', 'L.coil', 'L.driver', 'L.battery', 'L.pcb', 'L.ring', 'L.mesh', 'L.cushion', 'L.shell'],
  ['R.magnet', 'R.coil', 'R.driver', 'R.battery', 'R.pcb', 'R.ring', 'R.mesh', 'R.cushion', 'R.shell'],
];
const DEPTH = [.84, .68, .92, .72, .82, 1.06, 1.18, 1.5, 1.45];        // × K0 distance (mesh / cushion / shell pushed back: smaller, calmer)
// hero parts brought toward the lens (big, sharp, caught by the gliding key one after the other)
const HERO_DEPTH = { 'L.ring': .5, 'L.pcb': .6, 'R.driver': .56 };
// text-safe zones (screen px, in every camera of the silent drift): the −42 dB / italic line block and ANC ● ON
const SAFE = [{ cx: 540, cy: 995, rx: 390, ry: 230 }, { cx: 540, cy: 292, rx: 230, ry: 64 }];
const ORIENT = {
  magnet: [.5, .6, 0], coil: [.9, .7, 0], driver: [-.35, .45, 0], battery: [.2, .15, -8], pcb: [.12, .2, 4],
  ring: [.95, .35, 0], mesh: [-.55, .3, 0], cushion: [.6, -.25, 0], shell: [-.5, -.45, 0],
};
// free parts: [screen x, screen y, depth ×]
const FREE = { sleeve: [560, 170, 1.3], core: [1000, 560, 1.15], slider0: [90, 1060, .75], slider1: [990, 1330, .8] };
function spiralSlot(arm, j, n) {
  const u = j / (n - 1);
  const th = (arm ? 0 : Math.PI) - .42 - u * 1.0 * Math.PI;      // arms start above-left / below-right of the type
  const rx = lerp(350, 500, Math.pow(u, .9)), ry = lerp(330, 820, Math.pow(u, .8));
  return [540 + rx * Math.cos(th), 930 - ry * Math.sin(th)];
}

// ------------------------------------------------------------------ particles shader
const PV = `
attribute vec3 aOff; attribute vec3 aCol; attribute float aTF; attribute float aHN; attribute float aRnd;
uniform float uTau, uP, uTrem, uFrame, uScale, uSize, uHot;
varying vec3 vCol; varying float vA;
vec3 hash3(float n){ return fract(sin(vec3(n, n+1.7, n+3.1))*43758.5453)*2.-1.; }
uniform float uSafe; uniform vec2 uSafeC; uniform vec2 uSafeR;
float safeK(vec4 cp){ vec2 nd = cp.xy/max(cp.w, 1e-4); vec2 sp = vec2((nd.x+1.)*.5*${W}., (1.-nd.y)*.5*${H}.);
  float e = length((sp - uSafeC)/uSafeR); return mix(1., .1 + .9*smoothstep(.72, 1.12, e), uSafe); }
void main(){
  float tau = min(uTau, aTF);
  float h = (1. - exp(-max(tau, 0.)/${TC.toFixed(3)}))*aHN;
  vec3 p = position + aOff*h*uP;
  p += hash3(aRnd*917.3 + uFrame*13.17)*uTrem;
  vec4 mv = modelViewMatrix*vec4(p, 1.);
  float z = max(-mv.z, .05);
  float ps = uSize*(.45 + 1.1*aRnd)*uScale/z;
  float a = 1.;
  if (ps < 1.4) { a *= ps/1.4; ps = 1.4; }
  if (ps > 6.) { a *= pow(6./ps, 1.6); }
  ps = min(ps, 48.);
  a *= smoothstep(.4, 3., z);
  float hot = uHot*(1. - smoothstep(0., aTF, tau));
  vCol = aCol*(1. + hot*2.5); vA = a*smoothstep(0., .012, uTau);
  gl_PointSize = ps;
  gl_Position = projectionMatrix*mv;
  vA *= safeK(gl_Position);
}`;
// frozen motion trails: the same flight, drawn as radial hairlines (tail = an earlier point of the same path)
const LV = `
attribute vec3 aOff; attribute vec3 aCol; attribute float aTF; attribute float aHN; attribute float aRnd; attribute float aEnd;
uniform float uTau, uP, uTrem, uFrame, uHot;
varying vec3 vCol; varying float vA;
vec3 hash3(float n){ return fract(sin(vec3(n, n+1.7, n+3.1))*43758.5453)*2.-1.; }
uniform float uSafe; uniform vec2 uSafeC; uniform vec2 uSafeR;
float safeK(vec4 cp){ vec2 nd = cp.xy/max(cp.w, 1e-4); vec2 sp = vec2((nd.x+1.)*.5*${W}., (1.-nd.y)*.5*${H}.);
  float e = length((sp - uSafeC)/uSafeR); return mix(1., .1 + .9*smoothstep(.72, 1.12, e), uSafe); }
void main(){
  float tau = min(uTau, aTF);
  float h = (1. - exp(-max(tau, 0.)/${TC.toFixed(3)}))*aHN;
  float len = .18 + .5*aRnd;
  float hh = aEnd > .5 ? h : h*(1. - len);
  vec3 p = position + aOff*hh*uP;
  p += hash3(aRnd*917.3 + uFrame*13.17)*uTrem;
  vec4 mv = modelViewMatrix*vec4(p, 1.);
  float hot = uHot*(1. - smoothstep(0., aTF, tau));
  vCol = aCol*(1. + hot*2.5); vA = aEnd*smoothstep(0., .012, uTau)*smoothstep(1., 6., -mv.z);
  gl_Position = projectionMatrix*mv;
  vA *= safeK(gl_Position);
}`;
const PF = `
uniform sampler2D uDot; uniform float uBright; varying vec3 vCol; varying float vA;
void main(){ float d = texture2D(uDot, gl_PointCoord).r; gl_FragColor = vec4(vCol*uBright*d*vA, d*vA); }`;

const LF = `uniform float uBright; varying vec3 vCol; varying float vA; void main(){ gl_FragColor = vec4(vCol*uBright*vA, vA); }`;

// ------------------------------------------------------------------ s06 word sprites (same table as s06)
const FAMS = [[FONT.impact, 400], [FONT.mono, 700], [FONT.ui, 900]];
const BUCKETS = [64, 128, 256];
function wordSprite(word, fam, v, fs) {
  const [family, weight] = FAMS[fam];
  const tmp = document.createElement('canvas').getContext('2d');
  const tw = measure(tmp, word, fs, weight, family, fam === 1 ? fs * .04 : 0);
  const padX = fs * (v === 3 ? .28 : .12), padY = fs * (v === 3 ? .16 : .1);
  const capH = fs * (fam === 0 ? .86 : .74);
  const c = document.createElement('canvas'); c.width = Math.ceil(tw + padX * 2); c.height = Math.ceil(capH + padY * 2);
  const x = c.getContext('2d');
  const cy = c.height / 2 + capH * .5;
  const o = { size: fs, weight, family, align: 'center', spacing: fam === 1 ? fs * .04 : 0 };
  if (v === 3) { x.fillStyle = COLD; x.fillRect(0, 0, c.width, c.height); text(x, word, c.width / 2, cy, { ...o, color: COL.ink }); }
  else if (v === 2) text(x, word, c.width / 2, cy, { ...o, fill: false, stroke: Math.max(2, fs * .03), strokeColor: COL.muted });
  else text(x, word, c.width / 2, cy, { ...o, color: v === 0 ? COLD : COL.muted });
  return { c, fs };
}

// ------------------------------------------------------------------ deterministic Math.random during hp.sample
function seeded(fn, seed = 12345) {
  const orig = Math.random; let s = seed;
  Math.random = () => (s = (s * 16807) % 2147483647) / 2147483647;
  try { return fn(); } finally { Math.random = orig; }
}

// ------------------------------------------------------------------ build
let R = null;
const tv = new THREE.Vector3();
function project(cam, p) { tv.copy(p).project(cam); return [(tv.x + 1) / 2 * W, (1 - tv.y) / 2 * H, tv.z]; }

function build(E) {
  const scene = new THREE.Scene(); scene.userData._envSet = true; scene.environmentIntensity = .38; scene.environment = E.env;
  const cam = new THREE.PerspectiveCamera(FOV, W / H, .3, 900);
  const prod = new THREE.Group(); scene.add(prod);
  const hp = createHeadphone(); prod.add(hp.root);
  hp.explode(0);
  prod.rotation.set(TILT, 0, 0); prod.position.set(0, .25 * Math.sin(8 * BEAT * 2.1), 0);   // = s06 at b36 (spin 8π)
  prod.updateMatrixWorld(true);
  // sample the debris NOW, on the assembled product: hp.sample() runs explode(0), which rewrites the local positions of
  // sleeve / core / sliders / cup layers — after the pivot re-parenting below that would break the assembled pose
  const smp = seeded(() => hp.sample(NP));

  // lights: s06's cold studio at the clamp, a detonation light, the gliding cold key of the silence
  const key = new THREE.DirectionalLight(0xe4edf7, 3.8); key.position.set(30, 34, 30); scene.add(key);
  const rimL = new THREE.DirectionalLight(0xd6e4f2, 8); rimL.position.set(-34, 14, -30); scene.add(rimL);
  const rimR = new THREE.DirectionalLight(0xd6e4f2, 6); rimR.position.set(36, -6, -26); scene.add(rimR);
  const fill = new THREE.DirectionalLight(0x9fb2c4, .5); fill.position.set(-10, -30, 20); scene.add(fill);
  const strobe = new THREE.DirectionalLight(0xffffff, 3); strobe.position.set(0, 4, 40); scene.add(strobe);
  const boom = new THREE.PointLight(0xffd29a, 0, 70, 1.4); boom.position.copy(C0); prod.add(boom);
  const glide = new THREE.PointLight(0xdfeaff, 0, 34, 2); scene.add(glide);
  const rings = hp.cups.map(c => c.userData.parts.ring.material);
  rings.forEach(m => { m.emissive = lin(COL.gold); m.emissiveIntensity = 0; });

  // freeze camera = s06's last camera
  const cs = camState(8);
  cam.fov = FOV; cam.position.set(0, 2.5, cs.d); cam.up.set(0, 1, 0); cam.lookAt(0, 0, 0); cam.clearViewOffset(); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  const cupMid = hp.cups[0].getWorldPosition(V3()).add(hp.cups[1].getWorldPosition(V3())).multiplyScalar(.5);
  const p0 = project(cam, cupMid);
  const K0 = { T: V3(0, 0, 0), dist: Math.hypot(cs.d, 2.5), yaw: 0, pitch: Math.atan2(2.5, cs.d), roll: 0, Ys: 960 + (cs.cupY - p0[1]) };
  cam.setViewOffset(W, H, 0, -(K0.Ys - 960), W, H); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  // s08 start: product whole, front-facing, ~880 px wide, centred (540, 980)
  const ctr = prod.localToWorld(V3(0, .7, 0));
  const dist8 = H / (2 * Math.tan(FOV / 2 * DEG) * (880 / 19.5));
  const K1 = { T: V3(0, -1.2, 0), dist: K0.dist * .65, yaw: 28 * DEG, pitch: K0.pitch + 3 * DEG, roll: 3 * DEG, Ys: 935 };
  const K2 = { T: ctr, dist: dist8, yaw: 0, pitch: Math.atan2(2.5, dist8), roll: 0, Ys: 980 };

  // ---- parts -> pivots at their own centres (prod-local), each with its frozen offset + tumble
  const named = {};
  hp.cups.forEach((c, i) => Object.entries(c.userData.parts).forEach(([k, p]) => { named[(i ? 'R.' : 'L.') + k] = p; }));
  named.sleeve = hp.band.sleeve; named.core = hp.band.core; named.slider0 = hp.sliders[0]; named.slider1 = hp.sliders[1];
  const invProd = new THREE.Matrix4().copy(prod.matrixWorld).invert();
  const parts = [];
  let idx = 0;
  // screen-space design -> prod-local targets
  const toWorld = (K, sx, sy, depth) => {
    setCam(cam, K);
    const v = V3(sx / W * 2 - 1, 1 - sy / H * 2, .5).unproject(cam).sub(cam.position).normalize();
    return prod.worldToLocal(cam.position.clone().addScaledVector(v, depth));
  };
  const TGT = {}, NRM = {};
  const Km = lerpK(K0, K1, .4);                                           // designed at ~b38 (when the line lands); the dolly flies through it
  const camK1 = (() => { setCam(cam, Km); return cam.position.clone(); })();
  ARMS.forEach((arm, a) => arm.forEach((n, j) => {
    const [sx, sy] = spiralSlot(a, j, arm.length);
    // parts right of centre sit deeper: the orbit (camera to +x) slides near things leftward, across the type
    TGT[n] = toWorld(Km, sx, sy, Km.dist * (HERO_DEPTH[n] || DEPTH[j] * (a ? 1.04 : 1) * (1 + .15 * clamp((sx - 470) / 400))));
  }));
  for (const [n, [sx, sy, dk]] of Object.entries(FREE)) TGT[n] = toWorld(Km, sx, sy, Km.dist * dk);
  // keep the type block clear: in every camera of the silent drift (b37.5 -> b39.5) each part's projected disc
  // (centre ± its screen radius) is pushed radially out of the safe ellipses, at constant distance from the lens
  {
    const fpx = H / (2 * Math.tan(FOV / 2 * DEG));
    const checks = [0, .15, .3, .45, .6, .75, .9, 1].map(k => lerpK(K0, K1, k));
    const wp = V3();
    let moved = 1;
    for (let it = 0; it < 16 && moved; it++) { moved = 0; for (const n of Object.keys(TGT)) {
      const sz = new THREE.Box3().setFromObject(named[n]).getSize(V3());
      const rad = Math.max(sz.x, sz.y, sz.z) * .5;
      for (const Kc of checks) {
        setCam(cam, Kc);
        wp.copy(TGT[n]); prod.localToWorld(wp);
        const z = wp.distanceTo(cam.position);
        const [sx, sy, sz2] = project(cam, wp);
        if (sz2 > 1) continue;
        const rs = rad * fpx / z * .9;
        for (const Z of HERO_DEPTH[n] ? SAFE.slice(0, 1) : SAFE) {   // heroes may pass behind the small ANC label
          const dx = (sx - Z.cx) / (Z.rx + rs), dy = (sy - Z.cy) / (Z.ry + rs), e = Math.hypot(dx, dy);
          if (e >= 1) continue;
          let nx, ny;
          if (HERO_DEPTH[n]) {                       // near heroes swing sideways with the orbit: clear them vertically only
            nx = sx; ny = Z.cy + Math.sign(dy || -1) * (Z.ry + rs) * Math.sqrt(Math.max(0, 1 - dx * dx)) * 1.08;
          } else {
            const ux = e > .05 ? dx / e : (sx < Z.cx ? -1 : 1), uy = e > .05 ? dy / e : 0;
            nx = Z.cx + ux * (Z.rx + rs) * 1.04; ny = Z.cy + uy * (Z.ry + rs) * 1.04;
          }
          TGT[n] = toWorld(Kc, nx, ny, z);
          moved++;
          break;
        }
      }
    } }
  }
  for (const n of Object.keys(TGT)) {
    const o = ORIENT[n.slice(2)] || [0, 0, 0];
    const toCam = prod.worldToLocal(camK1.clone()).sub(TGT[n]).normalize();
    const right = V3(0, 1, 0).cross(toCam).normalize(), up = toCam.clone().cross(right);
    NRM[n] = [toCam.clone().addScaledVector(right, o[0]).addScaledVector(up, o[1]).normalize(), o[2]];
  }
  // restore the freeze camera (K0) for the freeze-time projections
  cam.position.set(0, 2.5, cs.d); cam.up.set(0, 1, 0); cam.lookAt(0, 0, 0);
  cam.setViewOffset(W, H, 0, -(K0.Ys - 960), W, H); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  for (const [name, obj] of Object.entries(named)) {
    if (!TGT[name]) continue;
    const box = new THREE.Box3().setFromObject(obj); const cW = box.getCenter(V3());
    const base = cW.clone().applyMatrix4(invProd);
    const pivot = new THREE.Group(); pivot.position.copy(base); prod.add(pivot); pivot.updateMatrixWorld(true);
    pivot.attach(obj);
    const target = TGT[name].clone();
    const O = target.clone().sub(base);
    // tumble: discs turn their faces toward the camera (normal tilted by L[3], L[4]) + spin; others: free tumble
    let q = new THREE.Quaternion();
    if (name.startsWith('L.') || name.startsWith('R.')) {
      const n0 = V3(0, 1, 0).transformDirection(obj.matrixWorld).transformDirection(invProd).normalize();
      const nf = NRM[name][0];
      const qa = new THREE.Quaternion().setFromUnitVectors(n0, nf);
      const qs = new THREE.Quaternion().setFromAxisAngle(nf, (NRM[name][1] + (rnd(idx * 3.3) - .5) * 60) * DEG);
      q = qs.multiply(qa);
    } else {
      const ax = V3(rnd(idx * 1.7) - .5, rnd(idx * 2.9) - .5, rnd(idx * 4.3) - .5).normalize();
      q.setFromAxisAngle(ax, (70 + 80 * rnd(idx * 5.1)) * DEG);
    }
    // axis-angle form so the flight can scale the angle (tumble) — the path ends exactly on the designed orientation
    const ang = 2 * Math.acos(clamp(q.w, -1, 1)); const s = Math.sqrt(Math.max(1e-9, 1 - q.w * q.w));
    const axis = V3(q.x / s, q.y / s, q.z / s);
    // freeze time from the target's screen position in the freeze camera
    const ps = project(cam, prod.localToWorld(target.clone()));
    const d = ps[2] > 1 ? 1400 : Math.min(1400, Math.hypot(ps[0] - C_SCR[0], ps[1] - C_SCR[1]));
    const tF = .1 + d / RING_V;
    parts.push({ name, pivot, base, O, axis, ang, tF, hn: 1 / hF(tF), i: idx });
    idx++;
  }

  // ---- 100k debris particles from the assembled surface (sampled above, before the re-parenting)
  const g = new THREE.BufferGeometry();
  const pos = smp.positions, col = new Float32Array(NP * 3), off = new Float32Array(NP * 3), aTF = new Float32Array(NP), aHN = new Float32Array(NP), aR = new Float32Array(NP);
  const armPts = ARMS.map(a => [C0.clone(), ...a.map(n => TGT[n].clone())]);
  const pt = V3(), bp = V3();
  const gold = lin(COL.gold), stone = lin('#b5ab9c');
  for (let i = 0; i < NP; i++) {
    const r = k => rnd(i * 1.371 + k * 7.13 + .37);
    bp.set(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]);
    const kind = r(1);
    if (kind < .4) {                                   // dust shell, radial from the core
      const dir = bp.clone().sub(C0).add(V3(r(2) - .5, r(3) - .5, r(4) - .5).multiplyScalar(3)).normalize();
      const m = 2 + 12 * Math.pow(r(5), 1.6);
      pt.copy(bp).addScaledVector(dir, m);
    } else if (kind < .88) {                            // the two spiral arms (follow the parts)
      const arm = armPts[bp.x < 0 ? 0 : 1];  // left cup's dust follows the left arm
      const u = Math.pow(r(6), .8) * (arm.length - 1.001), j = Math.floor(u), f = u - j;
      pt.copy(arm[j]).lerp(arm[j + 1], f);
      const sp = .8 + 3.2 * r(7) * (.4 + u / arm.length);
      pt.add(V3(r(8) - .5, r(9) - .5, r(10) - .5).multiplyScalar(2 * sp));
    } else {                                            // wide field; some in front, passing the lens on the dolly
      const th = r(11) * TAU, u2 = r(12) * 2 - 1, s2 = Math.sqrt(1 - u2 * u2), rr = 12 + 40 * Math.pow(r(13), .7);
      pt.set(rr * s2 * Math.cos(th), rr * u2 * 1.3, rr * s2 * Math.sin(th));
      if (r(14) < .35) pt.z = 10 + 70 * r(15);
    }
    off.set([pt.x - bp.x, pt.y - bp.y, pt.z - bp.z], i * 3);
    const sp2 = project(cam, prod.localToWorld(pt.clone()));
    const d = sp2[2] > 1 || sp2[2] < -1 ? 1400 : Math.min(1400, Math.hypot(sp2[0] - C_SCR[0], sp2[1] - C_SCR[1]));
    aTF[i] = .1 + d / RING_V; aHN[i] = 1 / hF(aTF[i]); aR[i] = r(16);
    // colour: surface colour lifted (dark leather would vanish additively), a share of gold sparks
    const cr = smp.colors[i * 3], cg = smp.colors[i * 3 + 1], cb = smp.colors[i * 3 + 2];
    const lum = .2126 * cr + .7152 * cg + .0722 * cb;
    const lift = lum < .1 ? .1 / Math.max(lum, .01) : 1;
    let c = [cr * lift, cg * lift, cb * lift];
    if (r(17) < .14) c = [gold.r * 2.2, gold.g * 2.2, gold.b * 2.2];
    else if (r(17) < .3) c = [stone.r * 1.4, stone.g * 1.4, stone.b * 1.4];
    col.set(c, i * 3);
  }
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aOff', new THREE.BufferAttribute(off, 3)); g.setAttribute('aCol', new THREE.BufferAttribute(col, 3));
  g.setAttribute('aTF', new THREE.BufferAttribute(aTF, 1)); g.setAttribute('aHN', new THREE.BufferAttribute(aHN, 1)); g.setAttribute('aRnd', new THREE.BufferAttribute(aR, 1));
  const pmat = new THREE.ShaderMaterial({ vertexShader: PV, fragmentShader: PF, ...ADDITIVE,
    uniforms: { uTau: { value: 0 }, uP: { value: 1 }, uTrem: { value: 0 }, uFrame: { value: 0 }, uScale: { value: 1 }, uSize: { value: .065 },
      uHot: { value: 0 }, uDot: { value: dotTexture() }, uBright: { value: .5 },
      uSafe: { value: 0 }, uSafeC: { value: new THREE.Vector2(540, 1000) }, uSafeR: { value: new THREE.Vector2(400, 230) } } });
  const points = new THREE.Points(g, pmat); points.frustumCulled = false; prod.add(points);
  // streaks: the first NS particles of the shell + arm kinds again, as 2-vertex lines
  const NS = 6000, lg = new THREE.BufferGeometry();
  const L = { position: [3, pos], aOff: [3, off], aCol: [3, col], aTF: [1, aTF], aHN: [1, aHN], aRnd: [1, aR] };
  const sel = []; for (let i = 0; i < NP && sel.length < NS; i++) if (rnd(i * 1.371 + 7.13 + .37) < .88) sel.push(i);
  for (const [k, [n, src]] of Object.entries(L)) {
    const a = new Float32Array(sel.length * 2 * n);
    sel.forEach((i, j) => { for (let e = 0; e < 2; e++) for (let c = 0; c < n; c++) a[(j * 2 + e) * n + c] = src[i * n + c] * (k === 'aCol' ? .5 : 1); });
    lg.setAttribute(k, new THREE.BufferAttribute(a, n));
  }
  const ae = new Float32Array(sel.length * 2); for (let j = 0; j < sel.length; j++) ae[j * 2 + 1] = 1; lg.setAttribute('aEnd', new THREE.BufferAttribute(ae, 1));
  const lmat = new THREE.ShaderMaterial({ vertexShader: LV, fragmentShader: LF, ...ADDITIVE,
    uniforms: { uTau: pmat.uniforms.uTau, uP: pmat.uniforms.uP, uTrem: pmat.uniforms.uTrem, uFrame: pmat.uniforms.uFrame, uHot: pmat.uniforms.uHot,
      uSafe: pmat.uniforms.uSafe, uSafeC: pmat.uniforms.uSafeC, uSafeR: pmat.uniforms.uSafeR,
      uDot: { value: null }, uBright: { value: .5 } } });
  const lines = new THREE.LineSegments(lg, lmat); lines.frustumCulled = false; prod.add(lines);

  // ---- noise words (s06 table): blast targets + freeze times (screen space)
  const table = wordTable(), sprites = new Map();
  for (const w of table) {
    const fs = BUCKETS.find(b => b >= w.size * 1.02) || 256;
    const key = `${w.word}|${w.fam}|${w.v}|${fs}`;
    if (!sprites.has(key)) sprites.set(key, wordSprite(w.word, w.fam, w.v, fs));
    w.sprite = sprites.get(key);
    const dx = w.x - NOISE_C[0], dy = w.y - NOISE_C[1], dl = Math.hypot(dx, dy) || 1;
    const push = 1.2 + .3 * rnd(w.i * 3.7 + 1) + 260 / dl;           // clear the centre a little more
    w.tx = NOISE_C[0] + dx * push; w.ty = NOISE_C[1] + dy * push;
    w.spin = (rnd(w.i * 5.1 + 2) - .5) * 40 * DEG;
    const d = Math.min(1400, Math.hypot(w.tx - C_SCR[0], w.ty - C_SCR[1]));
    w.tF = .1 + d / RING_V; w.hn = 1 / hF(w.tF);
    w.depth = w.layer ? 1.6 : 1;
  }
  const WQ = .25;                                                          // words render at quarter res (they are defocused anyway)
  const wc = document.createElement('canvas'); wc.width = W * WQ; wc.height = H * WQ;
  const wb = document.createElement('canvas'); wb.width = W * WQ; wb.height = H * WQ;

  // ---- dive numerals: glyph metrics
  const mx = document.createElement('canvas').getContext('2d');
  mx.font = `400 300px "${FONT.impact}"`; const capA = mx.measureText('0').actualBoundingBoxAscent;
  mx.font = `400 240px "${FONT.serif}"`; const capS = mx.measureText('42').actualBoundingBoxAscent;
  // the gliding cold key visits the hero parts one by one (positions in prod-local, nudged toward the lens)
  const heroPath = ['L.pcb', 'L.ring', 'R.driver'].map(n => TGT[n].clone().add(prod.worldToLocal(camK1.clone()).sub(TGT[n]).normalize().multiplyScalar(7)));
  return { heroPath, wb, scene, cam, prod, hp, key, rimL, rimR, fill, strobe, boom, glide, rings, parts, points, lines, pmat, lmat, table, wc, K0, K1, K2, capA, capS };
}

// ------------------------------------------------------------------ camera
function lerpK(a, b, k) {
  return { T: a.T.clone().lerp(b.T, k), dist: lerp(a.dist, b.dist, k), yaw: lerp(a.yaw, b.yaw, k), pitch: lerp(a.pitch, b.pitch, k),
    roll: lerp(a.roll, b.roll, k), Ys: lerp(a.Ys, b.Ys, k) };
}
function setCam(cam, K) {
  const { T, dist, yaw, pitch, roll } = K;
  cam.position.set(T.x + dist * Math.sin(yaw) * Math.cos(pitch), T.y + dist * Math.sin(pitch), T.z + dist * Math.cos(yaw) * Math.cos(pitch));
  cam.up.set(0, 1, 0); cam.lookAt(T);
  cam.rotateZ(roll);
  cam.setViewOffset(W, H, 0, -(K.Ys - 960), W, H); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
}

// ------------------------------------------------------------------ dive numerals (slot rolls)
const DIVE = [[0, '118'], [3, '64'], [6, '11']];          // local frame (from b36.25 = f3) offsets: f435, f438, f441
function rollString(ctx, s, cx, base, yOff, alpha, smear) {
  if (alpha <= .003) return;
  const o = { size: 300, weight: 400, family: FONT.impact, color: COL.white, align: 'center' };
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.75)'; ctx.shadowBlur = 50;
  if (smear > .5) {
    text(ctx, s, cx, base + yOff + smear * .35, { ...o, alpha: alpha * .3 });
    text(ctx, s, cx, base + yOff, { ...o, alpha: alpha * .85 });
  } else text(ctx, s, cx, base + yOff, { ...o, alpha });
  ctx.restore();
}
function drawDive(fg, lf, capA, jx, jy, collapse) {
  const cx = 540 + jx, cy = 930 + jy, base = cy + capA / 2;
  const fl = lf - 3;                                     // frames since b36.25
  if (fl < 0 || fl >= 3 * 3 + 4) return;
  const step = Math.min(2, Math.floor(fl / 3)), kf = fl - step * 3;
  const rowH = capA * 1.12;
  fg.save(); fg.beginPath(); fg.rect(0, cy - capA / 2 - 8, W, capA + 16); fg.clip();
  let alpha = 1;
  if (fl >= 9) alpha = 1 - seg(fl, 9, 13);               // b37: dissolve into the serif
  // roll: new value in from below over 3 frames (expoOut), the old one out to the top; vertical smear while moving
  const ro = x => eout(clamp((x + .7) / 2.2));
  const k = ro(kf);
  const vel = (ro(kf + .5) - ro(kf - .5)) * rowH;
  const cur = DIVE[step][1], prev = step > 0 ? DIVE[step - 1][1] : null;
  if (fl < 9) {
    rollString(fg, cur, cx, base, (1 - k) * rowH, alpha, vel);
    if (prev) rollString(fg, prev, cx, base, -k * rowH, alpha, vel);
  } else {
    fg.translate(cx, cy); const s = 1 + .22 * eout(seg(fl, 9, 13)); fg.scale(s, s); fg.translate(-cx, -cy);
    text(fg, cur, cx, base, { size: 300, weight: 400, family: FONT.impact, color: COL.white, alpha: alpha * alpha, blur: 14 * seg(fl, 9, 13) });
  }
  fg.restore();
}

// ------------------------------------------------------------------ 2D: noise words (blasted, frozen, parallax)
function drawWords(bg, tau, P, par, wAlpha, Fr, trem) {
  const wc = R.wc, x = wc.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, wc.width, wc.height);
  if (P <= .002 || wAlpha <= .003) return;
  x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'medium';
  for (const w of R.table) {
    const tt = Math.min(tau, w.tF);
    const h = hF(tt) * w.hn * P;
    if (h <= .01) continue;
    let px = NOISE_C[0] + (w.tx - NOISE_C[0]) * h, py = NOISE_C[1] + (w.ty - NOISE_C[1]) * h;
    // camera parallax (words live behind the debris): dolly zoom + orbit shift
    px = C_SCR[0] + (px - C_SCR[0]) * (1 + par.zoom * w.depth) + par.shift * w.depth;
    py = C_SCR[1] + (py - C_SCR[1]) * (1 + par.zoom * w.depth);
    if (trem) { px += (rnd(w.i * 3.1 + Fr * 7.7) - .5) * 2 * trem * 30; py += (rnd(w.i * 5.9 + Fr * 3.3) - .5) * 2 * trem * 30; }
    const sc = w.size / w.sprite.fs * Math.min(1, h * 1.4) * (1 + par.zoom * w.depth * .6) * .25;
    const sp = w.sprite.c;
    x.globalAlpha = w.alpha * wAlpha * (w.layer ? .7 : 1);
    x.setTransform(sc, 0, 0, sc, px * .25, py * .25);
    x.rotate(w.rot + w.spin * Math.min(1, h));
    x.drawImage(sp, -sp.width / 2, -sp.height / 2);
  }
  const wb = R.wb, y = wb.getContext('2d');
  y.setTransform(1, 0, 0, 1, 0, 0); y.clearRect(0, 0, wb.width, wb.height);
  y.filter = `blur(${(par.blur / 4).toFixed(2)}px)`; y.drawImage(wc, 0, 0); y.filter = 'none';
  bg.save();
  bg.translate(540, 960); bg.rotate(par.roll); bg.translate(-540, -960);
  bg.imageSmoothingEnabled = true; bg.imageSmoothingQuality = 'medium';
  bg.drawImage(wb, 0, 0, W, H);
  bg.restore();
}

// ------------------------------------------------------------------ the scene
export default {
  id: 's07-mute', start: 36, end: 40,
  cutIn: 'none',
  init(E) { R = build(E); },
  motionBlur(lt) { const f = lt * 30; return f < .5 ? 1 : f < 5.5 ? 2 : f >= 44.5 ? 2 : 1; },   // the rewind is also smeared by the radial zoom blur

  draw(E, lt, t) {
    const fx = E.fx, bg = E.bg, fg = E.fg;
    const lf = lt * 30, Fr = Math.round(lf), b = B0 + lt / BEAT;
    const tau = Math.max(0, t - T0);                       // seconds since the click
    const P = 1 - rewindEase(seg(b, 39.5, 40));           // explosion progress multiplier (rewind)
    const rw = 1 - P;
    const trem = ein(seg(b, 39, 39.5)) * (b < 39.5 ? 1 : 1 - seg(b, 39.5, 39.75));
    const { scene, cam, prod, parts } = R;

    // ---------------- camera: s06's pose -> silent drift (eio b36.6-39.5) -> snap to s08's opening framing
    const kd = eio(seg(b, 36.6, 39.5));
    const K = lerpK(lerpK(R.K0, R.K1, kd), R.K2, rewindEase(seg(b, 39.5, 40)));
    setCam(cam, K);

    // ---------------- parts
    for (const p of parts) {
      const tt = Math.min(tau, p.tF);
      const h = hF(tt) * p.hn * P;
      p.pivot.position.copy(p.base).addScaledVector(p.O, h);
      if (trem > 0) {
        const j = trem * .12, s = p.i * 13.7 + Fr * 3.1;
        p.pivot.position.x += (rnd(s) - .5) * 2 * j; p.pivot.position.y += (rnd(s + 1.3) - .5) * 2 * j; p.pivot.position.z += (rnd(s + 2.9) - .5) * 2 * j;
      }
      p.pivot.quaternion.setFromAxisAngle(p.axis, p.ang * h);
    }
    prod.updateMatrixWorld(true);

    // ---------------- particles
    const u = R.pmat.uniforms;
    u.uTau.value = tau; u.uP.value = P; u.uTrem.value = trem * .12; u.uFrame.value = Fr;
    u.uScale.value = H / (2 * Math.tan(FOV / 2 * DEG)); u.uHot.value = .55;
    u.uBright.value = lerp(.3, .24, seg(b, 36.25, 37)) * (1 + .6 * rw); R.lmat.uniforms.uBright.value = lerp(.4, .3, seg(b, 36.25, 37)) * (1 + .5 * rw);
    u.uSafe.value = eio(seg(b, 36.25, 37)) * (1 - rw);     // dust clears a pocket behind the type

    // ---------------- lights
    const det = Math.exp(-tau / .06);
    R.boom.intensity = 220 * det * (tau > 0 ? 1 : 0);
    const calm = seg(b, 36.25, 37);                        // studio steps down with the counter
    R.key.intensity = lerp(3.8, .5, calm); R.rimL.intensity = lerp(8, 6, calm); R.rimR.intensity = lerp(6, 4.5, calm);
    scene.environmentIntensity = lerp(.38, .13, calm) + .25 * rw;
    R.strobe.intensity = (tau < .02 ? 4.5 : 1.6) * Math.exp(-tau / .05); R.fill.intensity = .5;
    R.rings.forEach(m => { m.emissiveIntensity = 4 * Math.exp(-tau / .12) + .1; });
    // the cold key glides across the frozen parts (left -> right, high -> low, in front)
    const gk = eio(seg(b, 36.6, 39.5));
    {
      const hp3 = R.heroPath, u3 = gk * (hp3.length - 1), j3 = Math.min(hp3.length - 2, Math.floor(u3));
      const gp = hp3[j3].clone().lerp(hp3[j3 + 1], eio(u3 - j3));
      prod.localToWorld(gp); R.glide.position.copy(gp);
    }
    R.glide.intensity = 520 * seg(b, 36.4, 37) * (1 - .6 * rw);
    // the rewind: light returns warm
    R.key.intensity += 2.4 * rw; R.rimL.intensity += 4 * rw;

    // ---------------- bg2d
    bg.fillStyle = '#050607'; bg.fillRect(0, 0, W, H);
    const gl = bg.createRadialGradient(540, 940, 0, 540, 940, 1000);
    gl.addColorStop(0, `rgba(96,106,118,${.16 + .1 * det})`); gl.addColorStop(.5, 'rgba(30,34,40,.1)'); gl.addColorStop(1, 'rgba(5,6,7,0)');
    bg.fillStyle = gl; bg.fillRect(0, 0, W, H);
    const wStep = Fr < 3 ? 1 : Fr < 6 ? .6 : Fr < 9 ? .42 : Fr < 12 ? .32 : .22;
    const par = { zoom: .16 * kd, shift: 90 * Math.sin(K.yaw), roll: -K.roll, blur: Fr < 3 ? 1 : Fr < 12 ? 2 : 3 };
    drawWords(bg, tau, P, par, wStep * (1 - seg(b, 39.75, 40) * .5), Fr, trem);

    // ---------------- 3D
    E.render3D(scene, cam);

    // ---------------- fg2d
    const tj = trem * 2 + (b >= 39.5 ? 0 : 0);
    const jx = (rnd(Fr * 9.1 + 1) - .5) * 2 * tj, jy = (rnd(Fr * 4.4 + 2) - .5) * 2 * tj;
    // collapse toward the centre on the rewind
    const col = rewindEase(seg(b, 39.5, 40));
    const C = (x, y) => [lerp(x, 540, col), lerp(y, 960, col)];
    fg.save();
    // s06 HUD tail (f432-443): label + meter stepping down; the counter jumps to the centre at f435
    const hudA = Fr < 3 ? 1 : 1 - seg(lf, 3, 6);           // label + meter leave as the counter jumps to the centre (b36.25)
    if (hudA > .003) {
      fg.save(); fg.globalAlpha = hudA;
      const g2 = fg.createLinearGradient(0, 160, 0, 500);
      g2.addColorStop(0, 'rgba(5,6,7,.82)'); g2.addColorStop(.55, 'rgba(5,6,7,.55)'); g2.addColorStop(1, 'rgba(5,6,7,0)');
      fg.fillStyle = g2; fg.fillRect(0, 0, W, 500);
      const sh = Fr < 3 ? (rnd(Fr * 3.3) - .5) * 24 : 0;
      text(fg, 'AMBIENT NOISE', 80 + sh, 262, { size: 30, weight: 700, family: FONT.mono, color: COL.muted, align: 'left', spacing: 6 });
      if (Fr < 3) {
        const adv = measure(fg, '0', 96, 400, FONT.impact) + 2;
        '118'.split('').forEach((d, i) => text(fg, d, 80 + sh + adv * (i + .5), 360, { size: 96, weight: 400, family: FONT.impact, color: COLD }));
        text(fg, 'dB', 80 + sh + adv * 3 + 16, 360, { size: 40, weight: 500, family: FONT.display, color: COL.gold, align: 'left' });
      }
      const lvl = Fr < 3 ? (Fr % 2 ? 1 : .95) : Fr < 4 ? .6 : Fr < 5 ? .3 : .1;   // meter drops with the counter
      const segs = 40, sw = 920 / segs, y = 396;
      fg.fillStyle = 'rgba(154,151,143,.28)'; for (let i = 0; i < segs; i++) fg.fillRect(80 + i * sw, y + 5, sw - 4, 2);
      for (let i = 0; i < segs; i++) {
        if (i >= lvl * segs) break;
        const hot = i / segs > .82; fg.fillStyle = hot ? '#ffffff' : COLD; fg.globalAlpha = hudA * (hot ? 1 : .85);
        fg.fillRect(80 + i * sw, y, sw - 4, 12);
      }
      fg.restore();
    }
    // THE CLICK (1 frame): the crushed hairline ignites gold — a hot core, a soft halo and an anamorphic streak across
    // the frame, so the hit frame carries one designed image instead of a white-out
    if (Fr === 0) {
      fg.save();
      const hx = 540, hy = 1020;
      const hal = fg.createRadialGradient(hx, hy, 0, hx, hy, 260);
      hal.addColorStop(0, 'rgba(255,224,170,.55)'); hal.addColorStop(.35, 'rgba(230,200,150,.18)'); hal.addColorStop(1, 'rgba(230,200,150,0)');
      fg.fillStyle = hal; fg.fillRect(hx - 260, hy - 260, 520, 520);
      const st = fg.createLinearGradient(0, 0, W, 0);
      st.addColorStop(0, 'rgba(230,200,150,0)'); st.addColorStop(.3, 'rgba(230,200,150,.5)'); st.addColorStop(.5, 'rgba(255,246,226,1)');
      st.addColorStop(.7, 'rgba(230,200,150,.5)'); st.addColorStop(1, 'rgba(230,200,150,0)');
      fg.fillStyle = st; fg.fillRect(0, hy - 2, W, 4);
      fg.shadowColor = 'rgba(255,206,130,1)'; fg.shadowBlur = 50; fg.fillStyle = '#e6c896';
      fg.fillRect(hx - 6, hy - 190, 12, 380);
      fg.shadowBlur = 16; fg.fillStyle = '#fffaf0'; fg.fillRect(hx - 2.5, hy - 175, 5, 350);
      fg.restore();
    }
    // legibility: drawn BEFORE the type so the plates only darken the debris behind it, never the numerals
    // text-safe ink plate: a soft radial plate behind the counter / −42 dB, plus a band behind the italic line
    const plate = (cx, cy, rx, ry, a) => {
      if (a <= .003) return;
      fg.save(); fg.translate(cx, cy); fg.scale(1, ry / rx);
      const sg = fg.createRadialGradient(0, 0, 0, 0, 0, rx);
      sg.addColorStop(0, `rgba(5,5,6,${a})`); sg.addColorStop(.55, `rgba(5,5,6,${a * .8})`); sg.addColorStop(1, 'rgba(5,5,6,0)');
      fg.fillStyle = sg; fg.fillRect(-rx, -rx, rx * 2, rx * 2); fg.restore();
    };
    plate(540, 975, 470, 300, seg(lf, 3, 9) * .58 * (1 - col));
    plate(540, 1088, 400, 95, eio(seg(b, 37.5, 38.25)) * .65 * (1 - col));
    plate(540, 290, 300, 72, seg(lf, 12, 14) * .82 * (1 - col));             // ANC ● ON stays legible when a hero part drifts behind it
    // dive numerals
    fg.save();
    if (col > 0) { const [cx, cy] = C(540, 930); fg.translate(cx, cy); fg.scale(1 - col, 1 - col); fg.translate(-540, -930); }
    drawDive(fg, lf + 1e-4, R.capA, jx, jy);
    fg.restore();
    // −42 dB (serif, hairline), drifting +1.5% over the silence
    if (lf >= 9 + 3 - .01) {
      const a = seg(lf, 12, 16) * (1 - col);
      const s = (1.04 - .04 * eout(seg(lf, 12, 16))) * (1 + .015 * seg(b, 37, 39.5)) * (1 - col);
      if (a > .003 && s > .01) {
        const [cx, cy] = C(540 + jx, 930 + jy);
        fg.save(); fg.translate(cx, cy); fg.scale(s, s);
        text(fg, MINUS + '42 dB', 0, R.capS / 2, { size: 240, weight: 400, family: FONT.serif, color: COL.white, alpha: a, blur: 5 * (1 - seg(lf, 12, 16)) });
        fg.restore();
      }
    }
    // ANC ● ON (b37)
    if (b >= 37) {
      const a = seg(lf, 12, 14) * (1 - col);
      const [cx, cy] = C(540 + jx, 300 + jy);
      const s = 1 - col;
      if (a > .003 && s > .01) {
        fg.save(); fg.translate(cx, cy); fg.scale(s, s);
        const sp = 30 * .35, wA = measure(fg, 'ANC', 30, 700, FONT.mono, sp), wO = measure(fg, 'ON', 30, 700, FONT.mono, sp);
        const gap = 26, tot = wA + gap * 2 + 10 + wO;
        text(fg, 'ANC', -tot / 2, 0, { size: 30, weight: 700, family: FONT.mono, color: COL.gold, align: 'left', spacing: sp, alpha: a });
        fg.globalAlpha = a; fg.fillStyle = COL.gold; fg.beginPath(); fg.arc(-tot / 2 + wA + gap, -10.5, 5, 0, TAU); fg.fill(); fg.globalAlpha = 1;
        text(fg, 'ON', -tot / 2 + wA + gap * 2 + 10, 0, { size: 30, weight: 700, family: FONT.mono, color: COL.gold, align: 'left', spacing: sp, alpha: a });
        fg.restore();
      }
    }
    // the world, on mute. (b37.75 -> fades in over one beat)
    {
      const a = eio(seg(b, 37.75, 38.75)) * (1 - col);
      const [cx, cy] = C(540 + jx, 1100 + jy);
      if (a > .003) {
        fg.save(); fg.translate(cx, cy); fg.scale(1 - col, 1 - col);
        text(fg, 'the world, on mute.', 0, 0, { size: 64, weight: 400, family: FONT.serif, italic: true, color: '#ebe7de', alpha: a * .9 });
        fg.restore();
      }
    }
    // the ANC freeze ring: spawns at b36.25, r 0 -> 1400 in 4 frames (constant speed = the freeze front);
    // contracts 1400 -> 0 on the rewind
    {
      let r = -1;
      if (t >= TFR) r = (t - TFR) * RING_V;
      if (r > 1400) r = -1;
      if (b >= 39.5) r = 1400 * (1 - rewindEase(seg(b, 39.5, 40)));
      if (r > 2) ancRing(fg, 540, 960, r, { alpha: 1, width: b >= 39.5 ? 6 : 5, glow: b >= 39.5 ? 44 : 30, band: 38, scale: 1.04 });
    }
    fg.restore();

    // ---------------- post: the step-down (one effect off per 1/16), then silence
    fx.exposure = .88; fx.vignette = .45; fx.grain = .05; fx.bloomThreshold = .74;
    if (Fr < 3) {                                          // f432-434 the click + detonation
      // the hit is a LIFT (exposure + bloom) with only a light warm mix, so the clamped silhouette and the gold
      // hairline read on frame 0; frame 1 carries the blast (zoom blur + glitch), frame 2 is clean
      fx.flash = [.03, 0, 0][Fr]; fx.flashColor = Fr === 0 ? [1, .85, .6] : [1, 1, 1];
      fx.exposure = .88 * [1.4, 1, 1][Fr]; fx.brightness = 0;
      fx.zoom = [1.12, 1.07, 1.035][Fr]; fx.rgb = [.022, .03, .02][Fr]; fx.zoomBlur = [.12, .38, .2][Fr]; fx.glitch = [0, .3, .1][Fr]; fx.glitchSeed = 11 + Fr * 7;
      fx.shake = [(rnd(Fr * 3.3 + 1) - .5) * .03 * (1 - Fr / 3), (rnd(Fr * 7.9 + 2) - .5) * .03 * (1 - Fr / 3)];
      fx.sat = .55; fx.bloom = [1.2, .8, .75][Fr]; fx.bloomThreshold = [.66, .74, .74][Fr]; fx.contrast = 1.05;
    } else if (Fr < 6) {                                   // b36.25 glitch, shake, zoom off
      fx.rgb = .014; fx.zoomBlur = .18 * (1 - (Fr - 3) / 3); fx.sat = .55; fx.bloom = .7; fx.contrast = 1.05; fx.bloomThreshold = 1.15;
    } else if (Fr < 9) {                                   // b36.5 rgb, zoom blur off
      fx.rgb = .001; fx.sat = .45; fx.bloom = .55; fx.contrast = 1.05; fx.bloomThreshold = 1.15;
    } else if (Fr < 12) {                                  // b36.75 colour drains
      fx.rgb = .001; fx.sat = .12; fx.tint = [.92, .96, 1.04]; fx.bloom = .3; fx.contrast = 1.1; fx.bloomThreshold = 1.15;
    } else {                                               // b37 silence: grain + vignette only
      fx.rgb = 0; fx.sat = .12; fx.tint = [.92, .96, 1.04]; fx.bloom = .3; fx.bloomThreshold = 1.05; fx.contrast = 1.1; fx.grain = .06; fx.vignette = .55;
      fx.letterbox = .07 * eio(seg(b, 37, 37.5));
    }
    if (b >= 39) fx.sat = lerp(.12, .3, seg(b, 39, 39.5));
    if (b >= 39.5) {
      const k = seg(b, 39.5, 40);
      fx.zoomBlur = .7 * ein(k); fx.zoomCenter = [.5, .5]; fx.rgb = .025 * ein(k); fx.sat = lerp(.3, 1, k);
      fx.tint = [lerp(.92, 1, k), lerp(.96, 1, k), lerp(1.04, 1, k)]; fx.bloom = lerp(.22, .6, k);
      fx.letterbox = Fr >= 46 ? 0 : .07;
      fx.exposure = .88 + .12 * ein(k);
    }
  },
};
