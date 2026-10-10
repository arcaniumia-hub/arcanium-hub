// s08-gyro — DROP 2 (b40-48): the 360° type gyroscope.
// The product lands whole and front-facing on the downbeat (s07's rewind-snap end pose), the gold cup rings flare, and a
// gyroscope of three counter-rotating 3D type rings snaps open around it, one per 1/8 (A b40.0, B b40.5, C b41.0).
// CAMERA: 120° whip (b40-40.5) + 60° glide (b40.5-44) with a crane up / dolly out; b44 GYRO LOCK: the three rings snap
// coplanar (hidden by the hard cut) and the edit hard-cuts every 1/8 between 4 presets (TOP target / LOW hero / MACRO /
// WIDE); b46 the rings unlock during a second 120° whip, then tighten around the product while spinning 3× faster;
// b47.5 the camera rushes through the gap between the cups into the right cup's acoustic mesh (dot pattern fills the frame
// at f575 for the s09 match cut).
//
// Layers: bg2d warm radial glow + giant rotating '360°' + a faint yaw dial
//         3D   the product (opaque) + 3 type rings (custom shader: back faces 35 %, front faces drawn after, nested-shell
//              painter order so every ring/product overlap is depth-correct) + gold hairline rails + 22k gold dust
//         fg2d live yaw readout, compass strip, multi-cam label.
// Everything is a pure function of t.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, back, rnd, noise1, text, measure, b2s, COL, FONT, ADDITIVE, dotTexture, goldGrad } from '../lib.js';
import { createHeadphone } from '../model.js';

const B0 = 40, T0 = b2s(40);
const DEG = Math.PI / 180;
const FOV = 30, TILT = 8 * DEG;
const PROD_Y = .25 * Math.sin(8 * BEAT * 2.1);       // = s07 / s06 product pose at b36..40
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();

// whip ease: normalised tanh sigmoid, peak velocity ~2.5x average (expoIO's 7x strobes even with 4 motion samples)
const whip = x => { x = clamp(x); const s = 2.6; return (Math.tanh(s * (2 * x - 1)) / Math.tanh(s) + 1) / 2; };
// rush: accelerating dolly that lands (a 1-frame settle) so the mesh dots read on f575
const rushEase = x => { x = clamp(x); return x < .8 ? .9 * Math.pow(x / .8, 2.3) : .9 + .1 * eout((x - .8) / .2); };

// ------------------------------------------------------------------ the three rings
const RINGS = [
  { str: '360° SPATIAL AUDIO  ·  ', family: FONT.display, weight: 900, size: 168, ch: 290, spacing: 6, color: COL.white, gold: false,
    intensity: 2.1, r: 13, rT: 10.6, band: 3.0, snap: 40.0, speed: 90, prec: 9, lockY: 2.5, bandTint: [1, .86, .62], bandA: .07 },
  { str: 'SILENCE ONE  ·  ', family: FONT.impact, weight: 400, size: 230, ch: 300, spacing: 10, color: COL.gold, gold: true,
    intensity: 1.5, r: 14.5, rT: 11.6, band: 3.4, snap: 40.5, speed: -120, prec: 0, lockY: -5.3, bandTint: [1, .8, .5], bandA: .06 },
  { str: '40 H  ·  −42 dB  ·  250 G  ·  40 MM  ·  ANC-H2  ·  ', family: FONT.mono, weight: 700, size: 96, ch: 150, spacing: 4, color: COL.gold, gold: false,
    intensity: 1.7, r: 16, rT: 12.6, band: 1.3, snap: 41.0, speed: 60, prec: -11, lockY: -2.1, bandTint: [1, .82, .55], bandA: .09 },
];
// gyroscope tilts (see report: the 'Saturn' ring is read as an open ellipse so its type stays legible)
const TILTS = [
  new THREE.Quaternion().setFromEuler(new THREE.Euler(17 * DEG, 0, 7 * DEG, 'ZXY')),
  new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 24 * DEG, 70 * DEG, 'YXZ')),
  new THREE.Quaternion().setFromEuler(new THREE.Euler(32 * DEG, 0, -45 * DEG, 'ZXY')),
];

const RV = `
varying vec2 vUv; varying vec3 vN; varying vec3 vV;
void main(){ vUv = uv; vec4 mv = modelViewMatrix*vec4(position, 1.); vN = normalize(normalMatrix*normal); vV = -mv.xyz;
  gl_Position = projectionMatrix*mv; }`;
const RF = `
uniform sampler2D map; uniform float uRep, uInt, uAlpha, uGlintPos, uGlint, uBandA, uFlash, uDim, uFlip; uniform vec3 uBandCol;
varying vec2 vUv; varying vec3 vN; varying vec3 vV;
void main(){
  vec4 tx = texture2D(map, vec2(vUv.x*uRep*uFlip, vUv.y));
  float facing = abs(dot(vN, normalize(vV)));
  float shade = mix(.42, 1.12, smoothstep(.05, .85, facing));
  float d = fract(vUv.x - uGlintPos + .5) - .5;
  float g = uGlint*exp(-d*d*900.);
  float edge = smoothstep(0., .06, vUv.y)*smoothstep(1., .94, vUv.y);
  vec3 txt = tx.rgb*(uInt*shade*(1. + uFlash) + g*4.);
  vec3 band = uBandCol*(.35 + g*2.)*shade;
  float ba = uBandA*edge*(.5 + .5*facing) + g*.12*edge;
  vec3 col = mix(band, txt, tx.a);
  float a = max(tx.a, ba);
  gl_FragColor = vec4(col*uDim, a*uAlpha);
}`;

function bandCanvas(R) {
  const tmp = document.createElement('canvas').getContext('2d');
  const w = Math.ceil(measure(tmp, R.str, R.size, R.weight, R.family, R.spacing));
  const c = document.createElement('canvas'); c.width = w; c.height = R.ch; const x = c.getContext('2d');
  x.font = `${R.weight} ${R.size}px "${R.family}"`;
  const cap = x.measureText('H').actualBoundingBoxAscent;
  x.letterSpacing = R.spacing + 'px'; x.textBaseline = 'alphabetic'; x.textAlign = 'left';
  x.fillStyle = R.gold ? (() => { const g = x.createLinearGradient(0, R.ch / 2 - cap / 2, 0, R.ch / 2 + cap / 2); g.addColorStop(0, COL.goldHi); g.addColorStop(.45, COL.gold); g.addColorStop(1, COL.gold2); return g; })() : R.color;
  x.fillText(R.str, 0, R.ch / 2 + cap / 2);
  return c;
}

function buildRing(R, i) {
  const c = bandCanvas(R);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 16; tex.wrapS = THREE.RepeatWrapping;
  tex.minFilter = THREE.LinearMipmapLinearFilter; tex.generateMipmaps = true;
  const rep = Math.max(1, Math.round(TAU * R.r / (R.band * c.width / c.height)));
  const uniforms = { map: { value: tex }, uRep: { value: rep }, uInt: { value: R.intensity }, uAlpha: { value: 1 }, uGlintPos: { value: 0 },
    uGlint: { value: 0 }, uBandA: { value: R.bandA }, uFlash: { value: 0 }, uBandCol: { value: new THREE.Vector3(...R.bandTint) } };
  const geo = new THREE.CylinderGeometry(R.r, R.r, R.band, 320, 1, true);
  const mk = (side, alpha) => new THREE.ShaderMaterial({ vertexShader: RV, fragmentShader: RF, side, transparent: true, depthWrite: false,
    // back faces (inner surface) are flipped so type reads correctly from inside the gyroscope too
    uniforms: { ...uniforms, uAlpha: { value: alpha }, uDim: { value: alpha < 1 ? .5 : 1 }, uFlip: { value: side === THREE.BackSide ? -1 : 1 } } });
  const mBack = mk(THREE.BackSide, .35), mFront = mk(THREE.FrontSide, 1);
  const back = new THREE.Mesh(geo, mBack), front = new THREE.Mesh(geo, mFront);
  // painter order for nested shells: backs outer->inner, product (opaque), fronts inner->outer
  back.renderOrder = 10 + (2 - i); front.renderOrder = 20 + i;
  const pivot = new THREE.Group(), spin = new THREE.Group(); pivot.add(spin); spin.add(back); spin.add(front);
  // gold hairline rails on both band edges (the ANC-ring language in 3D)
  const railMat = new THREE.MeshStandardMaterial({ color: lin('#dcb98a'), metalness: 1, roughness: .22, emissive: lin(COL.gold), emissiveIntensity: 2.4 });
  [-1, 1].forEach(s => { const tg = new THREE.TorusGeometry(R.r, .04, 8, 320); tg.rotateX(Math.PI / 2); const m = new THREE.Mesh(tg, railMat); m.position.y = s * R.band / 2; spin.add(m); });
  // snap shockwave: a hairline that leaves the ring and fades
  const waveMat = new THREE.MeshBasicMaterial({ color: lin(COL.gold).multiplyScalar(4), ...ADDITIVE, opacity: 0 });
  const wg = new THREE.TorusGeometry(R.r, .06, 6, 320); wg.rotateX(Math.PI / 2); const wave = new THREE.Mesh(wg, waveMat); pivot.add(wave);
  return { R, pivot, spin, back, front, mBack, mFront, railMat, wave, waveMat, rep };
}

// ------------------------------------------------------------------ gold dust
const DV = `
attribute float aRnd; uniform float uTime, uPx, uSize, uSpin; varying float vA; varying vec3 vC;
void main(){
  float a = uTime*(.08 + .35*aRnd)*(aRnd > .5 ? 1. : -.7) + uSpin*(.4 + aRnd);
  vec3 p = position; p.xz = mat2(cos(a), -sin(a), sin(a), cos(a))*p.xz;
  p.y += .4*sin(uTime*.9 + aRnd*40.);
  vec4 mv = modelViewMatrix*vec4(p, 1.); float z = max(-mv.z, .1);
  float ps = uSize*uPx*(.5 + 1.2*aRnd)/z; float al = 1.;
  if (ps < 1.3) { al = ps/1.3; ps = 1.3; } al *= clamp(1.7 - ps/9., 0., 1.); ps = min(ps, 14.);
  vA = al*(.45 + .55*sin(uTime*3. + aRnd*90.)*.5 + .3)*smoothstep(.8, 6., z);
  vC = mix(vec3(1., .78, .5), vec3(1., .95, .85), step(.85, aRnd));
  gl_PointSize = ps; gl_Position = projectionMatrix*mv;
}`;
const DF = `uniform sampler2D uDot; uniform float uBright; varying float vA; varying vec3 vC;
void main(){ float d = texture2D(uDot, gl_PointCoord).r; gl_FragColor = vec4(vC*uBright*d*vA, d*vA); }`;

// ------------------------------------------------------------------ build
let R = null;
function build(E) {
  const scene = new THREE.Scene(); scene.userData._envSet = true; scene.environment = E.env; scene.environmentIntensity = .42;
  const cam = new THREE.PerspectiveCamera(FOV, W / H, .08, 2000);
  const prod = new THREE.Group(); scene.add(prod);
  const hp = createHeadphone(); prod.add(hp.root); hp.explode(0);
  prod.rotation.set(TILT, 0, 0); prod.position.set(0, PROD_Y, 0); prod.updateMatrixWorld(true);
  // this instance's stone: a touch darker / cooler + more clearcoat so it reads stone-grey (not cream) under the warm studio
  hp.root.traverse(o => { const ms = o.material ? (Array.isArray(o.material) ? o.material : [o.material]) : [];
    ms.forEach(m => { if (m.color && m.color.getHex() === 0x9d9488 && m.clearcoat !== undefined) { m.color.setHex(0x8b867f); m.clearcoat = .4; m.clearcoatRoughness = .3; m.roughness = .46; } }); });
  const ringMats = hp.cups.map(c => c.userData.parts.ring.material);
  ringMats.forEach(m => { m.emissive = lin(COL.gold); m.emissiveIntensity = 0; });
  const meshMat = hp.cups[1].userData.parts.mesh.material;
  meshMat.emissive = new THREE.Color(1, 1, 1); meshMat.emissiveMap = meshMat.map; meshMat.emissiveIntensity = 0;

  // studio: warm key, gold rims (they become the key when the camera orbits behind), cool low fill
  const key = new THREE.DirectionalLight(0xfff0dc, 1.9); key.position.set(26, 30, 38); scene.add(key);
  const rimL = new THREE.DirectionalLight(0xffd49c, 7); rimL.position.set(-34, 14, -30); scene.add(rimL);
  const rimR = new THREE.DirectionalLight(0xffe2b8, 6); rimR.position.set(36, -6, -26); scene.add(rimR);
  // (fill / front folded into the key + env: every extra light costs ~10% of the frame on SwiftShader)
  const core = new THREE.PointLight(0xffc98a, 0, 60, 1.3); core.position.set(0, 0, 4); scene.add(core);
  const camLight = new THREE.PointLight(0xffe0b0, 0, 40, 1.4); scene.add(camLight);

  const rings = RINGS.map((r, i) => { const o = buildRing(r, i); scene.add(o.pivot); return o; });

  // dust
  const N = 7000, pos = new Float32Array(N * 3), rr = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    const u = rnd(i * 2.1 + 3) * 2 - 1, th = rnd(i * 3.7 + 1) * TAU, rad = 6 + 26 * Math.pow(rnd(i * 5.3 + 2), .8);
    const s = Math.sqrt(1 - u * u); pos.set([rad * s * Math.cos(th), rad * u * .75, rad * s * Math.sin(th)], i * 3); rr[i] = rnd(i * 1.37 + .5);
  }
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(pos, 3)); dg.setAttribute('aRnd', new THREE.BufferAttribute(rr, 1));
  const dmat = new THREE.ShaderMaterial({ vertexShader: DV, fragmentShader: DF, ...ADDITIVE,
    uniforms: { uTime: { value: 0 }, uPx: { value: H / (2 * Math.tan(FOV / 2 * DEG)) }, uSize: { value: .055 }, uSpin: { value: 0 }, uDot: { value: dotTexture() }, uBright: { value: .9 } } });
  const dust = new THREE.Points(dg, dmat); dust.frustumCulled = false; dust.renderOrder = 30; scene.add(dust);

  // reference points
  const ctr = prod.localToWorld(V3(0, .7, 0));
  const dist8 = H / (2 * Math.tan(FOV / 2 * DEG) * (880 / 19.5));
  const meshObj = hp.cups[1].userData.parts.mesh;
  const meshC = meshObj.getWorldPosition(V3());
  const inward = V3(0, -1, 0).applyQuaternion(hp.cups[1].getWorldQuaternion(new THREE.Quaternion())).normalize();
  const capC = meshC.clone().addScaledVector(inward, .05);
  const cupMid = hp.cups[0].getWorldPosition(V3()).add(hp.cups[1].getWorldPosition(V3())).multiplyScalar(.5);
  const ringC = hp.cups[1].userData.parts.ring.getWorldPosition(V3());
  const rg = hp.cups[1].userData.parts.ring; rg.updateMatrixWorld(true);
  const macroT = rg.localToWorld(V3(-3.99 * Math.sin(38 * DEG), .1, 3.99 * Math.cos(38 * DEG)));

  return { scene, cam, prod, hp, key, rimL, rimR, core, camLight, ringMats, meshMat, rings, dust, dmat, ctr, dist8, capC, inward, cupMid, ringC, macroT, cupR: hp.cups[1].getWorldPosition(V3()), mbGain: probeMB(E) };
}

// ------------------------------------------------------------------ camera
function setCam(cam, pos, target, fov, roll = 0, Ys = 960) {
  cam.fov = fov; cam.position.copy(pos); cam.up.set(0, 1, 0); cam.lookAt(target); if (roll) cam.rotateZ(roll);
  cam.setViewOffset(W, H, 0, -(Ys - 960), W, H); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
}
const orbitPos = (T, dist, yaw, pitch) => V3(T.x + dist * Math.sin(yaw) * Math.cos(pitch), T.y + dist * Math.sin(pitch), T.z + dist * Math.cos(yaw) * Math.cos(pitch));

// orbit yaw (degrees, continuous) outside the cut block
function orbitYaw(b) {
  if (b < 46) return 120 * whip(seg(b, 40, 40.5)) + 60 * eio(seg(b, 40.5, 44)) * .35 + 60 * seg(b, 40.5, 44) * .65;
  return 180 + 120 * whip(seg(b, 46, 46.5)) + 45 * seg(b, 46.5, 47.5) + 20 * seg(b, 47.5, 48);
}
// orbit framing
function orbitK(b) {
  const D = R.dist8;
  if (b < 46) {
    const o = eout(seg(b, 40, 41.2));
    return { dist: lerp(D, 104, o) - 6 * eio(seg(b, 41.2, 44)), pitch: lerp(Math.atan2(2.5, D), 9 * DEG, o) + 5 * DEG * eio(seg(b, 41.2, 44)),
      Ys: lerp(980, 955, o), fov: FOV, roll: 0 };
  }
  const k = eio(seg(b, 46, 47.5));
  return { dist: lerp(100, 74, k), pitch: lerp(13, 7, k) * DEG, Ys: 960, fov: FOV, roll: -4 * DEG * Math.sin(Math.PI * seg(b, 46, 46.5)) };
}
// b44-46 hard-cut presets [pos, target, fov, roll, drift]
const PRESETS = [
  { name: 'TOP', pos: [0, 52, 10], tgt: [0, -1, 0], fov: 50, roll: 0, drift: [0, -6, -1.5], spinRoll: 14 },
  { name: 'LOW', pos: [-14, -21, 30], tgt: [0, 3.5, 0], fov: 46, roll: -9, drift: [-2.5, 1.5, -3] },
  { name: 'MACRO', pos: [.45, .02, .89], tgt: [0, 0, 0], fov: 11, roll: 9, drift: [0, 0, 0] },
  { name: 'WIDE', pos: [52, 30, 102], tgt: [0, -1, 0], fov: 24, roll: -6, drift: [-4, 2, -8] },
];

function camAt(b) {
  // returns { pos, tgt, fov, roll, Ys, yaw (deg, continuous), cut (preset index or -1) }
  if (b >= 44 && b < 46) {
    const i = Math.min(3, Math.floor((b - 44) * 2)), P = PRESETS[i], k = eout(seg(b, 44 + i * .5, 44.5 + i * .5));
    const T = R.ctr;
    const pos = V3(P.pos[0] + P.drift[0] * k, P.pos[1] + P.drift[1] * k, P.pos[2] + P.drift[2] * k).add(T);
    const tgt = V3(...P.tgt).add(T);
    if (P.name === 'MACRO') { tgt.copy(R.macroT); pos.copy(R.macroT).addScaledVector(V3(...P.pos).normalize(), 21 - 2.5 * k); }
    const yaw = 180 + (((Math.atan2(pos.x - T.x, pos.z - T.z) / DEG) - 180 + 540) % 360 - 180);
    return { pos, tgt, fov: P.fov, roll: (P.roll + (P.spinRoll || 0) * k) * DEG, Ys: 960, yaw, cut: i };
  }
  const yaw = orbitYaw(b), K = orbitK(b);
  const T = R.ctr.clone();
  T.y += .35 * Math.sin(b * .9);
  let pos = orbitPos(T, K.dist, yaw * DEG, K.pitch + .25 * DEG * noise1(b * 1.3));
  let tgt = T, fov = K.fov, roll = K.roll + .6 * DEG * noise1(b * .9 + 7);
  if (b >= 47.5) {
    // RUSH into the right cup's acoustic mesh: cubic path front-left -> gap between the cups -> along the cup axis
    const p = seg(b, 47.5, 47.5 + 5 / 12), e = rushEase(p);
    const E = R.capC.clone().addScaledVector(R.inward, 1.05);
    const C2 = R.capC.clone().addScaledVector(R.inward, 6.5);
    const C1 = R.cupMid.clone().add(V3(-3, 1.5, 15));
    const u = 1 - e;
    pos = pos.clone().multiplyScalar(u * u * u).addScaledVector(C1, 3 * u * u * e).addScaledVector(C2, 3 * u * e * e).addScaledVector(E, e * e * e);
    const lk = eio(seg(p, 0, .8));
    tgt = T.clone().lerp(R.capC, lk);
    fov = lerp(FOV, 46, e); roll = lerp(roll, 0, e) + 9 * DEG * Math.sin(Math.PI * e);
  }
  return { pos, tgt, fov, roll, Ys: K.Ys, yaw, cut: -1 };
}

// continuous yaw for the score's pan law (sound/score.py reads sound/yaw.json: one value per frame b40-48)
export function yawDeg(b) { return R ? camAt(b).yaw : 0; }

// ------------------------------------------------------------------ ring state
function ringState(i, b, lt) {
  const r = RINGS[i];
  // spin: base speed, x3 over b46-47.5 (closed-form integral of a linear ramp), beat + downbeat impulses
  const d = 1.5 * BEAT, x = seg(b, 46, 47.5);
  const extra = 2 * (b < 47.5 ? d * x * x / 2 : d / 2 + (b - 47.5) * BEAT);
  let ang = r.speed * DEG * (lt + extra);
  const dir = Math.sign(r.speed);
  for (const db of [40, 44]) ang += dir * 70 * DEG * expoOut(seg(b, db, db + .6));
  for (let k = 41; k <= 47; k++) if (k !== 44) ang += dir * 9 * DEG * eout(seg(b, k, k + .3));
  // snap open (back easing, 6 frames)
  const sn = b < r.snap ? 0 : back(seg(b, r.snap, r.snap + .5), 2.2);
  // tighten
  const rad = lerp(r.r, r.rT, eio(seg(b, 46, 47.5))) / r.r;
  // gyro lock b44-46 (hard cut in, whip out)
  const L = b < 44 ? 0 : b < 46 ? 1 : 1 - whip(seg(b, 46, 46.5));
  return { ang, sn, rad, L };
}

// ------------------------------------------------------------------ 2D layers
function drawBG(bg, b, lt, yaw, kick) {
  bg.fillStyle = '#060506'; bg.fillRect(0, 0, W, H);
  const g = bg.createRadialGradient(540, 960, 0, 540, 960, 1150);
  const gl = .26 + .08 * kick + .1 * Math.exp(-lt / .2);
  g.addColorStop(0, `rgba(150,112,62,${gl})`); g.addColorStop(.42, `rgba(70,50,28,${gl * .45})`); g.addColorStop(1, 'rgba(6,5,6,0)');
  bg.fillStyle = g; bg.fillRect(0, 0, W, H);
  // giant 360°
  bg.save(); bg.translate(540, 960); bg.rotate(-6 * DEG * lt);
  const s = 1 + .025 * kick; bg.scale(s, s);
  text(bg, '360°', 0, 0, { size: 760, weight: 400, family: FONT.impact, color: COL.white, alpha: .1, baseline: 'middle' });
  bg.restore();
  // yaw dial: 120 ticks on r 860, rotating with the camera (parallax cue for the orbit)
  bg.save(); bg.translate(540, 960); bg.rotate(-yaw * DEG);
  bg.strokeStyle = 'rgba(230,200,150,.2)'; bg.lineWidth = 2;
  for (let i = 0; i < 120; i++) {
    const a = i / 120 * TAU, L = i % 10 === 0 ? 46 : 18;
    bg.beginPath(); bg.moveTo(Math.cos(a) * 860, Math.sin(a) * 860); bg.lineTo(Math.cos(a) * (860 + L), Math.sin(a) * (860 + L)); bg.stroke();
  }
  bg.beginPath(); bg.arc(0, 0, 840, 0, TAU); bg.strokeStyle = 'rgba(230,200,150,.12)'; bg.lineWidth = 1.5; bg.stroke();
  bg.restore();
}

function compass(fg, yaw, alpha) {
  if (alpha <= .003) return;
  const x0 = 640, x1 = 1000, cx = 820, y = 250, ppd = 3;
  fg.save();
  // hairline baseline
  const lg = fg.createLinearGradient(x0, 0, x1, 0);
  lg.addColorStop(0, 'rgba(230,200,150,0)'); lg.addColorStop(.5, `rgba(230,200,150,${.45 * alpha})`); lg.addColorStop(1, 'rgba(230,200,150,0)');
  fg.fillStyle = lg; fg.fillRect(x0, y + 20, x1 - x0, 1.5);
  const first = Math.floor((yaw - 64) / 15) * 15;
  for (let d = first; d <= yaw + 64; d += 15) {
    const x = cx + (d - yaw) * ppd; if (x < x0 || x > x1) continue;
    const e = clamp(1 - Math.pow(Math.abs(x - cx) / 180, 2.2));
    const m = ((d % 360) + 360) % 360, major = m % 90 === 0, mid = m % 45 === 0;
    fg.globalAlpha = alpha * e; fg.fillStyle = COL.gold;
    const h = major ? 36 : mid ? 24 : 14;
    fg.fillRect(Math.round(x) - 1, y + 20 - h, 2, h);
    if (major) text(fg, String(m).padStart(3, '0'), x, y - 30, { size: 30, weight: 400, family: FONT.mono, color: COL.muted, alpha: 1 });
  }
  // index marker
  fg.globalAlpha = alpha; fg.fillStyle = COL.white;
  fg.beginPath(); fg.moveTo(cx, y + 28); fg.lineTo(cx - 9, y + 42); fg.lineTo(cx + 9, y + 42); fg.closePath(); fg.fill();
  fg.restore();
}

function drawHUD(fg, b, lt, yaw, cut, hudA, kick) {
  if (hudA <= .003) return;
  const y360 = ((Math.round(yaw) % 360) + 360) % 360;
  // reveal: characters type on over the first beat
  const on = seg(b, 40.1, 40.6);
  fg.save(); fg.globalAlpha = hudA;
  const label = 'θ ' + String(y360).padStart(3, '0') + '°';
  const nShow = Math.ceil(label.length * on);
  text(fg, label.slice(0, nShow), 80, 1560, { size: 64, weight: 700, family: FONT.mono, color: COL.white, align: 'left' });
  const sub = 'SPATIAL AUDIO · HEAD-TRACKED';
  text(fg, sub.slice(0, Math.ceil(sub.length * seg(b, 40.4, 41))), 80, 1610, { size: 30, weight: 400, family: FONT.mono, color: COL.muted, align: 'left', spacing: 1 });
  // live dot
  const blink = (Math.floor(lt * 30 / 6) % 2) ? .35 : 1;
  if (on > 0) { fg.fillStyle = COL.gold; fg.globalAlpha = hudA * blink; fg.beginPath(); fg.arc(86, 1478, 7, 0, TAU); fg.fill(); fg.globalAlpha = hudA; }
  text(fg, cut >= 0 ? `CAM 0${cut + 1} — ${PRESETS[cut].name}` : 'CAM 00 — ORBIT', 104, 1488, { size: 30, weight: 400, family: FONT.mono, color: COL.gold, align: 'left', spacing: 2, alpha: on });
  fg.restore();
  compass(fg, yaw, hudA * seg(b, 40.2, 40.8));
}

// ------------------------------------------------------------------ scene
function mbAt(lt) {
  const f = Math.round(lt * 30);
  if (f >= 1 && f <= 5) return f === 1 || f === 5 ? 2 : 4;     // whip 1 (b40.0-40.5): 4 on the fastest frames
  if (f >= 72 && f <= 77) return f === 72 || f === 77 ? 2 : 4;  // b46 cut + whip 2
  if (f >= 90 && f <= 94) return f >= 92 ? 3 : 2;              // rush into the mesh
  return 1;                                                    // f95 lands crisp: the dots must read for the match cut
}
// The engine accumulates motion-blur sub-frames with AdditiveBlending (src*alpha + dst) while also weighting colour by
// 1/n, so an n-sample frame comes out at 1/n brightness. Probe it once and compensate with fx.tint (linear, pre-grade),
// so this scene stays correct whether or not the engine gets fixed.
function probeMB(E) {
  try {
    const gl = E.renderer.getContext(), px = new Uint8Array(4);
    const draw = () => { E.bg.fillStyle = '#c0c0c0'; E.bg.fillRect(0, 0, W, H); Object.assign(E.fx, { bloom: 0, grain: 0, vignette: 0, rgb: 0 }); };
    E.renderFrame(0, draw, 1); gl.readPixels(540, 960, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); const a = px[0];
    E.renderFrame(0, draw, 2); gl.readPixels(540, 960, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); const c = px[0];
    return c < a * .85 ? 1 : 0;                      // 1: bug present -> gain n
  } catch (e) { return 0; }
}
const KICKS = [41, 42, 43, 44, 45, 46, 47].map(b2s);
const CUTS = [44, 44.5, 45, 45.5, 46];

export default {
  id: 's08-gyro', start: 40, end: 48,
  cutIn: 'none',
  init(E) {
    R = build(E);
    if (typeof window !== 'undefined') window.S08_YAW = Array.from({ length: 96 }, (_, f) => +camAt(40 + f / 12).yaw.toFixed(2));
  },
  motionBlur(lt) { return mbAt(lt); },

  draw(E, lt, t) {
    const fx = E.fx, bg = E.bg, fg = E.fg;
    const b = B0 + lt / BEAT, lf = lt * 30, Fr = Math.round(lf);
    const { scene, cam } = R;

    // kick envelope (4 frames) for 2D pulses
    let kick = 0; for (const a of KICKS) { const fr = (t - a) * 30; if (fr >= 0 && fr < 6) kick = Math.max(kick, 1 - fr / 6); }

    // ---------------- camera
    const C = camAt(b);
    setCam(cam, C.pos, C.tgt, C.fov, C.roll, C.Ys);
    R.camLight.position.copy(C.pos);

    // ---------------- rings
    R.rings.forEach((o, i) => {
      const r = RINGS[i], S = ringState(i, b, lt);
      const qT = new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), r.prec * DEG * lt).multiply(TILTS[i]);
      const q = qT.clone().slerp(new THREE.Quaternion(), S.L);
      o.pivot.quaternion.copy(q);
      o.pivot.position.copy(R.ctr).add(V3(0, r.lockY * S.L, 0));
      const s = Math.max(1e-3, S.sn);
      o.pivot.scale.set(s * S.rad, s, s * S.rad);
      o.pivot.visible = S.sn > .002;
      o.spin.rotation.y = S.ang;
      // camera inside this ring: its inner faces are all we see -> show them fully
      o.pivot.updateMatrixWorld(true); const cl = o.pivot.worldToLocal(C.pos.clone());
      const inside = 1 - clamp((Math.hypot(cl.x, cl.z) - (r.r - 1.5)) / 2);
      o.mBack.uniforms.uAlpha.value = lerp(.35, .9, inside); o.mBack.uniforms.uDim.value = lerp(.5, 1, inside);
      // glint: one sweep round the ring on its snap, then on the claps and on every cut
      const snapF = (b - r.snap) / .7;
      let glint = 0, gpos = 0;
      if (snapF >= 0 && snapF < 1) { glint = 1 - snapF * .6; gpos = snapF * 1.25 + i * .3; }
      for (const cb of [41, 43, 45, 47]) { const k = (b - cb) / .5; if (k >= 0 && k < 1 && glint < 1 - k) { glint = (1 - k) * .8; gpos = k * .9 + i * .33 + cb * .1; } }
      const flash = 2.5 * Math.exp(-Math.max(0, b - r.snap) * BEAT / .1) * (b >= r.snap ? 1 : 0);
      for (const m of [o.mBack, o.mFront]) { m.uniforms.uGlint.value = glint; m.uniforms.uGlintPos.value = gpos; m.uniforms.uFlash.value = flash + .25 * kick; }
      const rail = 3 + 9 * Math.exp(-Math.max(0, b - r.snap) * BEAT / .15) * (b >= r.snap ? 1 : 0) + 3 * kick;
      // up close the rails read as polished gold rods (reflections) instead of flat glowing bars
      const near = Math.max(.5, Math.abs(C.pos.distanceTo(o.pivot.position) - r.r * S.rad * S.sn));
      const thick = .08 * H / (2 * Math.tan(C.fov / 2 * DEG) * near);          // projected rail thickness (px)
      o.railMat.emissiveIntensity = rail * .8 * clamp((16 - thick) / 11, .06, 1);
      // snap shockwave
      const wk = seg(b, r.snap, r.snap + .75);
      o.wave.visible = wk > 0 && wk < 1;
      if (o.wave.visible) { const ws = 1 + .45 * expoOut(wk); o.wave.scale.set(ws * S.rad, 1, ws * S.rad); o.waveMat.opacity = (1 - wk) * (1 - wk); o.wave.rotation.y = S.ang; }
    });

    // ---------------- product + lights
    const drop = Math.exp(-lt / (BEAT * .45));
    R.ringMats.forEach(m => { m.emissiveIntensity = 4 * drop + .12 + .5 * kick; });
    R.core.intensity = 500 * drop;
    const rush = seg(b, 47.5, 47.5 + 5 / 12);
    // lamp on the camera, keeping the mesh's irradiance constant as we close in (decay 1.4)
    R.camLight.intensity = 4.2 * eio(seg(b, 47.45, 47.8)) * Math.min(12, Math.pow(Math.max(1, C.pos.distanceTo(R.capC) / 1.05), 1.4));
    R.meshMat.emissiveIntensity = 0;
    // entering the cup: the studio falls away, only a dim lamp on the camera
    const dark = 1 - .78 * eio(seg(b, 47.6, 47.9));
    R.key.intensity = (1.9 + 1.2 * drop) * dark; R.rimL.intensity = 7 * dark; R.rimR.intensity = 6 * dark;
    R.core.visible = R.core.intensity > 5; R.camLight.visible = R.camLight.intensity > .01;
    scene.environmentIntensity = .42 * (.4 + .6 * dark);

    // dust
    const du = R.dmat.uniforms; du.uTime.value = t; du.uSpin.value = 0; du.uPx.value = H / (2 * Math.tan(C.fov / 2 * DEG));
    du.uBright.value = .55 + .35 * kick;

    // ---------------- 2D
    drawBG(bg, b, lt, C.yaw, kick);
    E.render3D(scene, cam);
    const hudA = 1 - seg(b, 47.45, 47.75);
    drawHUD(fg, b, lt, C.yaw, C.cut, hudA, kick);

    // ---------------- post
    fx.exposure = .8; fx.sat = 1.1; fx.contrast = 1.08; fx.bloom = .9; fx.bloomThreshold = .74; fx.grain = .045; fx.vignette = .4;
    // b40 DROP 2 punch
    {
      const fr = lf;
      fx.flash = fr < 9 ? .85 * Math.exp(-fr / .8) * (1 - fr / 9) : 0; fx.flashColor = [1, .82, .55];
      fx.zoom = 1 + .18 * (1 - expoOut(clamp(fr / 8)));
      fx.rgb = .002 + .033 * Math.max(0, 1 - fr / 12);
      fx.zoomBlur = .8 * Math.max(0, 1 - fr / 6);
      const sh = .012 * Math.max(0, 1 - fr / 12);
      fx.shake = [(rnd(Fr * 1.7 + 3) - .5) * 2 * sh, (rnd(Fr * 2.9 + 5) - .5) * 2 * sh];
    }
    // kicks
    for (const a of KICKS) { const fr = (t - a) * 30; if (fr >= 0 && fr < 4) { const k = 1 - fr / 4; fx.zoom *= 1 + .02 * k; fx.rgb = Math.max(fx.rgb, .002 + .004 * k); } }
    // ring snaps B, C: small aberration kicks
    for (const sb of [40.5, 41]) { const fr = (b - sb) * 12; if (fr >= 0 && fr < 4) fx.rgb = Math.max(fx.rgb, .01 * (1 - fr / 4)); }
    // hard cuts: 2-frame glitch slices + 1-frame rgb + shake
    for (const cb of CUTS) {
      const fr = Math.round((b - cb) * 12 * 100) / 100;
      if (fr >= 0 && fr < 2) { fx.glitch = Math.max(fx.glitch, .25 * (fr < 1 ? 1 : .6)); fx.glitchSeed = cb * 13 + Math.floor(fr) * 7; }
      if (fr >= 0 && fr < 1) { fx.rgb = Math.max(fx.rgb, .015); const s = .006; fx.shake = [fx.shake[0] + (rnd(cb * 3.1) - .5) * 2 * s, fx.shake[1] + (rnd(cb * 5.7) - .5) * 2 * s]; }
      if (fr >= 0 && fr < 6 && cb === 44) fx.zoom *= 1 + .06 * (1 - expoOut(fr / 6));
    }
    // b46 second whip: zoom blur during the move
    if (b >= 46 && b < 46.5) { const k = Math.sin(Math.PI * seg(b, 46, 46.5)); fx.zoomBlur = Math.max(fx.zoomBlur, .35 * k); fx.rgb = Math.max(fx.rgb, .012 * k); }
    if (b >= 40.05 && b < 40.5) { const k = Math.sin(Math.PI * seg(b, 40, 40.5)); fx.zoomBlur = Math.max(fx.zoomBlur, .3 * k); }
    // b47-47.75: rgb pulses on every 1/16
    if (b >= 47 && b < 47.75) { const f16 = ((b - 47) * 4) % 1; fx.rgb = Math.max(fx.rgb, .002 + .008 * Math.max(0, 1 - f16 * 3)); }
    // b47.5-48: rush
    if (b >= 47.5) { fx.zoomBlur = Math.max(fx.zoomBlur, .8 * ein(seg(b, 47.5, 47.85)) * (1 - .7 * seg(lf, 94, 95))); fx.zoomCenter = [.5, .5]; fx.rgb = Math.max(fx.rgb, .006 + .02 * ein(rush) * (1 - .6 * seg(lf, 94, 95))); }
    // motion-blur brightness compensation (see probeMB)
    if (R.mbGain) { const n = mbAt(lt); if (n > 1) fx.tint = fx.tint.map(v => v * n); }
  },
};
