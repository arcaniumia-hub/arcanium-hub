// s04-reveal — REVEAL: light floods the ring's framing, the camera rockets back to the whole product floating over a
// violent SOUND SEA, the gold ANC ring expands on the sea and flattens it; two macro cut-ins (gold slider light-sweep,
// woven headband skim) and a whip pan into the grid (b20-24).
//
// Layers: bg2d ink + warm volumetric beam · 3D one scene (product, sea line-terrain, ring plane, dust/bokeh) lit per shot
//         · fg2d 'Introducing' / 'SILENCE ONE', part labels + leader lines, whip streaks.
// First frame == s03's last frame (CUP_CAM framing, ring white-hot at emissive 6, the rest of the model black).
import * as THREE from 'three';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoIn, expoOut, rnd, text, font, measure, orbitFrame,
  ADDITIVE, COL, FONT } from '../lib.js';
import { createHeadphone } from '../model.js';

// shared with s03 (its exported CUP_CAM): right ear cup seen straight onto its outer face
const CUP_CAM = { fov: 30, position: [7.2 + 44.67, -4.5, 0], target: [7.2, -4.5, 0] };
const DEG = Math.PI / 180;
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const GOLD = lin(COL.gold);
const SEA_Y = -13.2;                 // calm water level (world)
// shot boundaries in frames since b20.0
const QB = 24, QC = 36, QW = 42, QE = 48;

// ------------------------------------------------------------------ value-noise fbm (deterministic)
function hash2(i, j) { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); }
function vn(x, z) {
  const i = Math.floor(x), j = Math.floor(z), fx = x - i, fz = z - j;
  const u = fx * fx * (3 - 2 * fx), v = fz * fz * (3 - 2 * fz);
  const a = hash2(i, j), b = hash2(i + 1, j), c = hash2(i, j + 1), d = hash2(i + 1, j + 1);
  return (a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v) * 2 - 1;
}
const fbm = (x, z) => vn(x, z) * .55 + vn(x * 2.03 + 5.2, z * 2.03 - 1.7) * .28 + vn(x * 4.1 - 3.3, z * 4.1 + 8.1) * .17;

// ------------------------------------------------------------------ the SOUND SEA (own line grid with vertex colours)
function buildSea(width, z0, z1, nx, nz) {
  const n = nx * nz, pos = new Float32Array(n * 3), col = new Float32Array(n * 3), idx = [];
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    pos.set([(i / (nx - 1) - .5) * width, 0, lerp(z0, z1, j / (nz - 1))], (j * nx + i) * 3);
    if (i < nx - 1) idx.push(j * nx + i, j * nx + i + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.setIndex(idx);
  const mat = new THREE.LineBasicMaterial({ vertexColors: true, ...ADDITIVE });
  const mesh = new THREE.LineSegments(g, mat); mesh.frustumCulled = false;
  const ROUGH = lin('#9a978f').lerp(lin('#8e989f'), .35), CALM = lin('#b9ab92');
  // world-space (x,z) of each vertex is needed for the ring distance: the mesh is rotated about Y by `rotY`
  function update(t, R, rotY, alpha) {
    const cs = Math.cos(rotY), sn = Math.sin(rotY), A = 3.0;
    for (let j = 0; j < nz; j++) {
      const zl = lerp(z0, z1, j / (nz - 1));
      const farFade = Math.pow(seg(zl, z0, z0 + 30), 1.5) * (1 - .35 * seg(zl, z1 - 18, z1));
      for (let i = 0; i < nx; i++) {
        const k = j * nx + i, xl = pos[k * 3];
        const wx = xl * cs + zl * sn, wz = -xl * sn + zl * cs;
        const d = Math.hypot(wx, wz);
        // violent rolling noise toward camera (+z local) + chop
        let h = A * fbm(xl * .085 + t * .15, (zl - t * 3) * .085) + .55 * vn(xl * .33 + t * 1.1, (zl - t * 7) * .33);
        const calm = R > .01 ? clamp((d - R) / 6) : 1, cs2 = calm * calm * (3 - 2 * calm);
        const edge = R > .01 ? Math.exp(-Math.pow((d - R - .9) / 1.3, 2)) : 0;
        const y = h * cs2 + .95 * edge * (R < 58 ? 1 : 0);
        pos[k * 3 + 1] = y;
        const side = 1 - seg(Math.abs(xl), width * .36, width * .5);
        const a = alpha * farFade * side;
        const crest = clamp(.55 + .45 * h / A);
        const glint = (1 - cs2) * Math.exp(-xl * xl / 9) * (.35 + .65 * Math.max(0, vn(xl * .9 + t * 2.5, zl * .45 - t * 1.5))) * seg(zl, z0 + 6, -4) * (1 - seg(zl, 4, 12));
        const rough = (.45 + 3.6 * crest * crest) * cs2, calmK = (1 - cs2) * .42 + glint * 1.6, g = 3 * Math.exp(-Math.pow((d - R) / 1.5, 2)) * (R > .01 ? 1 : 0);
        col[k * 3] = a * (ROUGH.r * rough + CALM.r * calmK + GOLD.r * g);
        col[k * 3 + 1] = a * (ROUGH.g * rough + CALM.g * calmK + GOLD.g * g);
        col[k * 3 + 2] = a * (ROUGH.b * rough + CALM.b * calmK + GOLD.b * g);
      }
    }
    g.attributes.position.needsUpdate = true; g.attributes.color.needsUpdate = true;
  }
  return { mesh, update };
}

// ------------------------------------------------------------------ the ANC ring lying on the sea (analytic, additive)
const RING_V = `varying vec3 vW; void main(){ vec4 w = modelMatrix*vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }`;
const RING_F = `uniform float uR, uI, uBirth; uniform vec3 uCol; uniform mat3 uInv; uniform vec4 uBox; varying vec3 vW;
void main(){
  float d = length(vW.xz);
  float core = exp(-pow((d-uR)/.13, 2.)), halo = exp(-pow((d-uR)/1.1, 2.))*.28, wide = exp(-pow((d-uR)/4.5, 2.))*.06;
  // inside: a faint warm sheen of the calmed water
  float sheen = smoothstep(uR, uR*.2, d)*.012*step(.01, uR);
  vec3 l = uInv*vW; float box = smoothstep(uBox.x, uBox.x+26., l.z)*(1.-smoothstep(uBox.y-10., uBox.y, l.z))*(1.-smoothstep(uBox.z*.36, uBox.z*.5, abs(l.x)));
  float birth = uBirth*exp(-d*d/6.);
  vec3 c = uCol*(core*2.6 + halo + wide + sheen + birth*3.)*uI*box;
  gl_FragColor = vec4(c, 1.);
}`;

// ------------------------------------------------------------------ dust motes in the beam (and macro bokeh in B/C)
const DUST_V = `attribute float aR; uniform float uT, uPx, uSize; uniform vec3 uB0, uBd; varying float vA; varying float vS;
void main(){
  vec3 p = position;
  p.y = mod(p.y + uT*(.35+.6*aR) + 20., 46.) - 20.;
  p.x += sin(uT*.6 + aR*40.)*.7; p.z += cos(uT*.5 + aR*31.)*.7;
  vec3 q = p - uB0; float along = dot(q, uBd); float perp = length(q - uBd*along);
  float beam = exp(-pow(perp/7.5, 2.));
  vec4 mv = modelViewMatrix*vec4(p, 1.);
  float s = uSize*(.45+.9*aR)*uPx/max(-mv.z, .5);
  vS = clamp(s, 1.5, 90.); gl_PointSize = vS;
  vA = (.03 + beam)*(.5+.5*sin(uT*2.3 + aR*60.))*min(1., pow(9./vS, 1.3)) * step(.5, -mv.z);
  gl_Position = projectionMatrix*mv;
}`;
const DUST_F = `uniform float uAlpha; uniform vec3 uCol; varying float vA; varying float vS;
void main(){
  float d = length(gl_PointCoord - .5)*2.;
  float gauss = exp(-d*d*4.), disc = smoothstep(1., .82, d)*(.65+.35*smoothstep(.5, .95, d));
  float a = mix(gauss, disc, smoothstep(10., 30., vS));
  gl_FragColor = vec4(uCol*a*vA*uAlpha, 1.);
}`;

// ------------------------------------------------------------------ hi-frequency woven texture for the macro skim
function weaveTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d');
  x.fillStyle = '#6f685f'; x.fillRect(0, 0, 512, 512);
  const S = 16;
  for (let j = 0; j < 512 / S; j++) for (let i = 0; i < 512 / S; i++) {
    const over = (i + j) % 2 === 0, v = 92 + 26 * rnd(i * 7.1 + j * 13.3);
    const g = over ? x.createLinearGradient(i * S, 0, i * S + S, 0) : x.createLinearGradient(0, j * S, 0, j * S + S);
    g.addColorStop(0, `rgb(${v - 40},${v - 44},${v - 50})`); g.addColorStop(.5, `rgb(${v + 22},${v + 16},${v + 6})`); g.addColorStop(1, `rgb(${v - 40},${v - 44},${v - 50})`);
    x.fillStyle = g; x.fillRect(i * S + .5, j * S + .5, S - 1, S - 1);
    // fibres
    x.strokeStyle = `rgba(255,245,225,${.08 + .08 * rnd(i + j * 3.3)})`; x.lineWidth = 1;
    for (let f = 0; f < 3; f++) { x.beginPath(); if (over) { const fx = i * S + 3 + f * 4; x.moveTo(fx, j * S + 1); x.lineTo(fx, j * S + S - 1); } else { const fy = j * S + 3 + f * 4; x.moveTo(i * S + 1, fy); x.lineTo(i * S + S - 1, fy); } x.stroke(); }
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
  t.repeat.set(24, 6); return t;
}

let R = null;   // rig

function build(E) {
  RectAreaLightUniformsLib.init();
  const scene = new THREE.Scene(); scene.userData._envSet = true; scene.environmentIntensity = 0;
  const cam = new THREE.PerspectiveCamera(30, W / H, .1, 600);
  const prod = new THREE.Group(); scene.add(prod);
  const hp = createHeadphone(); prod.add(hp.root);
  const cup = hp.cups[1], ring = cup.userData.parts.ring;
  hp.cups.forEach(c => { ['pcb', 'battery', 'magnet', 'coil', 'driver'].forEach(k => { c.userData.parts[k].visible = false; }); });   // internals never shown here
  // glowing overlay riding the real PBR ring (child: inherits its 1.2 x scale), fades 6 -> 0
  const gG = new THREE.TorusGeometry(3.99, .16, 12, 200); gG.rotateX(Math.PI / 2);
  const glowMat = new THREE.MeshBasicMaterial({ color: GOLD.clone().lerp(new THREE.Color(1, 1, 1), .3), ...ADDITIVE });
  glowMat.depthTest = false; const glow = new THREE.Mesh(gG, glowMat); glow.renderOrder = 10; ring.add(glow);
  // lights
  const key = new THREE.DirectionalLight(0xffe2b0, 0); key.position.set(34, 30, 22); scene.add(key);
  const rim = new THREE.DirectionalLight(0xe6c896, 0); rim.position.set(-30, 12, -26); scene.add(rim);
  const under = new THREE.DirectionalLight(0xffd9a0, 0); under.position.set(5, -30, 12); scene.add(under);
  const ringL = new THREE.PointLight(0xffd9a0, 0, 16, 2); scene.add(ringL);
  const sweep = new THREE.RectAreaLight(0xfff0dc, 0, .7, 26); scene.add(sweep);
  const graze = new THREE.DirectionalLight(0xffe6c4, 0); scene.add(graze); scene.add(graze.target);
  // sea
  const sea = buildSea(84, -58, 70, 170, 130);
  const seaG = new THREE.Group(); seaG.position.y = SEA_Y; seaG.add(sea.mesh); scene.add(seaG);
  const ringMat = new THREE.ShaderMaterial({ vertexShader: RING_V, fragmentShader: RING_F, ...ADDITIVE, depthTest: true,
    uniforms: { uR: { value: 0 }, uI: { value: 0 }, uBirth: { value: 0 }, uCol: { value: GOLD.clone() }, uInv: { value: new THREE.Matrix3() }, uBox: { value: new THREE.Vector4(-58, 70, 84, 0) } } });
  const ringPlane = new THREE.Mesh(new THREE.PlaneGeometry(84, 128).rotateX(-Math.PI / 2), ringMat);
  ringPlane.position.set(0, .02, 6); ringPlane.frustumCulled = false; seaG.add(ringPlane);
  // dust
  const ND = 3000, dp = new Float32Array(ND * 3), dr = new Float32Array(ND);
  for (let i = 0; i < ND; i++) { dp.set([(rnd(i * 1.7 + 3) - .5) * 70, (rnd(i * 2.3 + 5) - .5) * 46 + 3, (rnd(i * 3.9 + 7) - .5) * 70], i * 3); dr[i] = rnd(i * 5.1 + 11); }
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(dp, 3)); dg.setAttribute('aR', new THREE.BufferAttribute(dr, 1));
  const dustMat = new THREE.ShaderMaterial({ vertexShader: DUST_V, fragmentShader: DUST_F, ...ADDITIVE,
    uniforms: { uT: { value: 0 }, uPx: { value: H * .5 / Math.tan(15 * DEG) }, uSize: { value: .16 }, uAlpha: { value: 1 },
      uB0: { value: new THREE.Vector3(40, 46, 18) }, uBd: { value: new THREE.Vector3(-40, -46, -18).normalize() }, uCol: { value: lin('#ffe2b0').multiplyScalar(1.6) } } });
  const dust = new THREE.Points(dg, dustMat); dust.frustumCulled = false; scene.add(dust);
  // macro fabric
  const sleeve = hp.band.sleeve, fabricA = sleeve.material, fabricB = fabricA.clone();
  const wt = weaveTexture(); fabricB.map = wt; fabricB.bumpMap = wt; fabricB.bumpScale = 3; fabricB.roughness = .9; fabricB.color = new THREE.Color(1.05, 1.0, .95);
  // macro DOF stand-in: weave contrast and bump fade with view distance (kills moire/sparkle at the band's horizon)
  fabricB.customProgramCacheKey = () => 's04-weave';
  fabricB.onBeforeCompile = sh => {
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <bumpmap_pars_fragment>', 'float s04Far(){ return smoothstep(1.6, 3.4, length(vViewPosition)); }\n#include <bumpmap_pars_fragment>')
      .replace('#include <map_fragment>', '#include <map_fragment>\n diffuseColor.rgb = mix(diffuseColor.rgb, vec3(.16, .145, .125), s04Far()*.85);')
      .replace('#include <normal_fragment_maps>', 'float s04k = 1. - s04Far();\n' + THREE.ShaderChunk.normal_fragment_maps.replace('dHdxy_fwd()', 'dHdxy_fwd()*s04k'));
  };
  return { scene, cam, prod, hp, ring, glow, glowMat, key, rim, under, ringL, sweep, graze, sea, seaG, ringMat, ringPlane, dust, dustMat, sleeve, fabricA, fabricB };
}

// ------------------------------------------------------------------ camera helpers
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function orbitPos(target, az, el, dist) { return target.clone().add(V(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)).multiplyScalar(dist)); }
function setCam(cam, pos, target, fov, up = V(0, 1, 0)) {
  cam.fov = fov; cam.position.copy(pos); cam.up.copy(up); cam.lookAt(target); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
}
const tmpV = new THREE.Vector3();
function project(cam, p) { tmpV.copy(p).project(cam); return [(tmpV.x + 1) / 2 * W, (1 - tmpV.y) / 2 * H]; }

// SHOT A camera (frames q 0..24): cup face -> 3/4 hero over the sea
const A1 = { az: 34 * DEG, el: 13 * DEG, dist: 74, target: V(0, -2.6, 0), fov: 30 };
function shotA(q) {
  const u = seg(q, 0, 12);
  const kd = 1 - Math.pow(1 - u, 4.2);                 // distance: brutal pull
  const ka = eio(seg(q, .4, 11.5)) * .55 + kd * .45;   // orbit lags a hair -> a swooping arc
  const T0 = V(...CUP_CAM.target);
  const target = T0.clone().lerp(A1.target, kd);
  const dist = Math.exp(lerp(Math.log(44.67), Math.log(A1.dist), kd)) * (1 + .035 * seg(q, 10, 24));  // + slow drift back
  const az = lerp(90 * DEG, A1.az, ka) - 3 * DEG * seg(q, 10, 24), el = lerp(0, A1.el, ka) + 1.2 * DEG * seg(q, 10, 24);
  return { pos: orbitPos(target, az, el, dist), target, fov: A1.fov, vel: Math.pow(1 - u, 3.2) * (u < 1 ? 1 : 0) };
}

// ------------------------------------------------------------------ 2D helpers
function halo(ctx, x, y, rx, ry, alpha, color = '230,200,150') {
  if (alpha <= .003 || rx <= 0 || ry <= 0) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(x, y); ctx.scale(rx / ry, 1);
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, ry);
  g.addColorStop(0, `rgba(${color},${alpha})`); g.addColorStop(.4, `rgba(${color},${alpha * .35})`); g.addColorStop(1, `rgba(${color},0)`);
  ctx.fillStyle = g; ctx.fillRect(-ry, -ry, ry * 2, ry * 2); ctx.restore();
}
// volumetric beam wedge from a point (soft edges by stacking)
function beam(ctx, sx, sy, tx, ty, spread, alpha, color = '255,226,176') {
  if (alpha <= .003) return;
  const ang = Math.atan2(ty - sy, tx - sx), len = Math.hypot(tx - sx, ty - sy) * 1.9;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(sx, sy); ctx.rotate(ang);
  for (let i = 0; i < 6; i++) {
    const s = spread * (.35 + i * .2);
    const g = ctx.createLinearGradient(0, 0, len, 0);
    g.addColorStop(0, `rgba(${color},${alpha * .3})`); g.addColorStop(.45, `rgba(${color},${alpha * .14})`); g.addColorStop(1, `rgba(${color},0)`);
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(0, -18); ctx.lineTo(len, -len * s); ctx.lineTo(len, len * s); ctx.lineTo(0, 18); ctx.closePath(); ctx.globalAlpha = .3; ctx.fill();
  }
  ctx.restore();
}
const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/#%+=<>';
function decode(s, n, seed, F) {   // first n chars resolved, next 3 scrambled
  let out = '';
  for (let i = 0; i < s.length; i++) {
    if (i < n) out += s[i];
    else if (i < n + 3 && s[i] !== ' ') out += GLYPHS[Math.floor(rnd(i * 13.7 + F * 3.1 + seed) * GLYPHS.length)];
    else if (i < n + 3) out += ' ';
  }
  return out;
}
// part label (left aligned at x 80): index Unbounded 300 34 #9a978f @1470, name JetBrains Mono 700 30 gold .2em @1520
function partLabel(fg, idx, name, q0, q, F, { wipeOut = null, wipeLen = 3, target = null, lineFrom = null, nameDelay = 1, rate = 3, lineLen = 8 } = {}) {
  const d = q - q0; if (d < 0) return;
  let clipX = W;
  if (wipeOut !== null && q >= wipeOut) clipX = lerp(W, 60, eio(seg(q, wipeOut, wipeOut + wipeLen)));
  if (clipX <= 62) return;
  fg.save(); fg.beginPath(); fg.rect(0, 0, clipX, H); fg.clip();
  // index rises in
  const ki = expoOut(seg(d, 0, 4));
  fg.save(); fg.beginPath(); fg.rect(60, 1420, 600, 64); fg.clip();
  text(fg, idx, 80, 1470 + (1 - ki) * 44, { size: 34, weight: 300, family: FONT.display, color: COL.muted, align: 'left', spacing: 2 });
  fg.restore();
  // hairline next to the index
  const iw = measure(fg, idx, 34, 300, FONT.display, 2);
  fg.fillStyle = COL.gold2; fg.globalAlpha = .9; fg.fillRect(80 + iw + 18, 1458, 90 * eout(seg(d, 1, 6)), 2); fg.globalAlpha = 1;
  // name decodes on, 3 chars per frame
  const n = Math.floor(clamp(d - nameDelay, 0, 99) * rate); if (d < nameDelay) { fg.restore(); return; }
  const s = decode(name, n, idx.length * 7, F);
  text(fg, s, 80, 1520, { size: 30, weight: 700, family: FONT.mono, color: COL.gold, align: 'left', spacing: 6 });
  // leader line (1.5 px #b8925a) drawn over 8 frames + target reticle
  if (target && lineFrom) {
    const kl = eio(seg(d, 0, lineLen));
    const [ax, ay] = lineFrom, [bx, by] = target;
    const ex = lerp(ax, bx, kl), ey = lerp(ay, by, kl);
    fg.strokeStyle = COL.gold2; fg.lineWidth = 1.5; fg.beginPath(); fg.moveTo(ax, ay); fg.lineTo(ex, ey); fg.stroke();
    fg.fillStyle = COL.gold; fg.beginPath(); fg.arc(ax, ay, 3.5, 0, TAU); fg.fill();
    if (kl > .98) {
      const kr = expoOut(seg(d, lineLen, lineLen + 4));
      fg.strokeStyle = COL.gold; fg.lineWidth = 2; fg.globalAlpha = kr;
      fg.beginPath(); fg.arc(bx, by, lerp(40, 14, kr), 0, TAU); fg.stroke();
      fg.beginPath(); fg.arc(bx, by, 4, 0, TAU); fg.fillStyle = COL.goldHi; fg.fill(); fg.globalAlpha = 1;
    }
  }
  fg.restore();
}

export default {
  id: 's04-reveal', start: 20, end: 24,
  cutIn: 'none',
  init(E) { R = build(E); },
  motionBlur(lt) { const q = lt * 30; return q >= .5 && q < 5 ? 2 : q >= QW + 3 ? 3 : q >= QW ? 2 : 1; },
  draw(E, lt, t) {
    const q = lt * 30, F = Math.floor(q + 1e-4), fx = E.fx, bg = E.bg, fg = E.fg, b = lt / BEAT;
    const { scene, cam, prod, hp } = R;
    const shot = q < QB ? 'A' : q < QC ? 'B' : q < QW ? 'C' : 'W';

    // ---------------- base post (AFTER look, calm-ish reveal)
    fx.exposure = .8; fx.bloom = .6; fx.bloomThreshold = .72; fx.grain = .05; fx.vignette = .5; fx.sat = .92; fx.rgb = .0015;

    // ---------------- product pose: +12 deg over b20-22, float
    prod.rotation.set(0, 12 * DEG * eio(seg(b, 0, 2.2)) * .35 + 12 * DEG * seg(b, 0, 2) * .65, 0);
    prod.position.y = .15 * Math.sin(lt * 2.4);
    prod.updateMatrixWorld(true);
    const Lw = p => prod.localToWorld(p.clone());

    // ---------------- reset per-shot state
    const L = R;
    L.key.intensity = L.rim.intensity = L.under.intensity = L.ringL.intensity = L.sweep.intensity = L.graze.intensity = 0;
    L.seaG.visible = L.ringPlane.visible = false; L.sleeve.material = L.fabricA; L.glow.visible = false;
    L.dust.visible = true; L.sweep.visible = false; L.dustMat.uniforms.uT.value = t; L.dustMat.uniforms.uAlpha.value = q < QB ? eout(seg(q, 6, 14)) : 1;

    // ---------------- background (ink)
    bg.fillStyle = COL.ink; bg.fillRect(0, 0, W, H);

    let target2d = null;
    if (shot === 'A') {
      const flood = eout(seg(q, 0, 6));
      // 3D camera
      const c = shotA(q); setCam(cam, c.pos, c.target, c.fov);
      // lights flood in (key 0->1 over 6 frames), ring flash 6 -> 0 over 8 frames
      L.key.intensity = 2.7 * flood; L.rim.intensity = 3.2 * flood; L.under.intensity = .35 * flood;
      scene.environmentIntensity = .25 * flood;
      const gI = 6.4 * Math.pow(1 - seg(q, 0, 8), 1.6);
      L.glow.visible = gI > .01; L.glowMat.color.copy(GOLD).lerp(new THREE.Color(1, 1, 1), .3).multiplyScalar(gI);
      L.ringL.position.copy(Lw(V(9.4, -4.5, 0))); L.ringL.intensity = 6 * Math.exp(-q / 4);
      // sea + ring
      const ur = seg(b, .5, 2.5), Rr = 60 * lerp(eout(ur), ur * ur, .55);
      L.seaG.visible = true; L.seaG.rotation.y = A1.az; L.seaG.updateMatrixWorld(true);
      L.sea.update(t, Rr, A1.az, seg(q, 1, 9));
      L.ringPlane.visible = true;
      const u = L.ringMat.uniforms; u.uR.value = Rr; u.uI.value = seg(b, .5, .56); u.uBirth.value = b >= .5 ? Math.exp(-(b - .5) / .12) : 0;
      u.uInv.value.setFromMatrix4(new THREE.Matrix4().copy(L.seaG.matrixWorld).invert());
      // background beam + horizon warmth
      beam(bg, 1150, -160, 520, 900, .2, .55 * flood);
      const hg = bg.createRadialGradient(540, 1180, 0, 540, 1180, 820);
      hg.addColorStop(0, `rgba(90,70,44,${.22 * flood})`); hg.addColorStop(1, 'rgba(5,5,6,0)');
      bg.fillStyle = hg; bg.fillRect(0, 0, W, H);
      E.render3D(scene, cam);
      // fg: the ring's glow (matches s03's white-hot ring, fades with the emissive)
      if (q < 9) {
        const k = Math.pow(1 - q / 9, 1.4);
        fg.save(); fg.globalCompositeOperation = 'lighter'; fg.lineJoin = 'round';
        const pts = []; for (let i = 0; i <= 72; i++) { const a = i / 72 * TAU; pts.push(project(cam, Lw(V(7.2, -4.5 + 4.788 * Math.cos(a), 3.99 * Math.sin(a))))); }
        const path = () => { fg.beginPath(); pts.forEach(([x, y], i) => i ? fg.lineTo(x, y) : fg.moveTo(x, y)); };
        path(); fg.strokeStyle = `rgba(230,200,150,${.22 * k})`; fg.lineWidth = 40; fg.stroke();
        path(); fg.strokeStyle = `rgba(255,236,205,${.5 * k})`; fg.lineWidth = 10; fg.shadowColor = 'rgba(230,200,150,.9)'; fg.shadowBlur = 30; fg.stroke();
        fg.restore();
      }
      // fg: anamorphic flare of the ring flash (continues s03's close burst)
      if (q < 10) {
        const p = project(cam, Lw(V(7.2, -4.5 - 4.79, 0))), k = Math.exp(-q / 2.4);
        halo(fg, p[0], p[1], 620 * k + 80, 10, .6 * k, '255,236,200');
        halo(fg, 540, 960, 700 * k, 700 * k, .25 * k, '255,226,176');
      }
      // ---- type: 'Introducing' (letter per half-frame from b21.0), 'SILENCE ONE' wipe from centre at b21.5
      drawLockup(fg, q, F, null);
      // fx: b20.0 warm flash, bloom 1.2 -> .6 over a beat, zoom 1.04 -> 1, zoom blur while the camera rockets back
      
      if (q < 3) { fx.flash = .025 * (1 - q / 3); fx.flashColor = [1, .9, .7]; }
      fx.bloom = lerp(1.2, .6, eout(seg(q, 0, 12))); fx.bloomThreshold = lerp(.66, .72, seg(q, 0, 12));
      fx.zoom *= 1 + .04 * (1 - expoOut(seg(q, 0, 8)));
      fx.rgb = Math.max(fx.rgb, .0015 + .014 * c.vel * seg(q, 0, 1));
      // b20.5 ring birth + b21 heartbeat pump
      if (b >= .5 && b < .75) { const k = 1 - (b - .5) / .25; fx.zoom *= 1 + .012 * k; fx.rgb = Math.max(fx.rgb, .0015 + .004 * k); }
      if (q >= 12 && q < 16) { const k = 1 - (q - 12) / 4; fx.zoom *= 1 + .012 * k; }
    } else if (shot === 'B') {
      // SHOT B: macro on the right gold slider + top of the cup, a narrow soft light sweeping L -> R
      const d = q - QB, u = d / 12;
      const tgtL = V(7.9, -1.5, 0);
      const camL = V(10.6, 2.6, 12.6);
      const tw = Lw(tgtL), cw0 = Lw(camL);
      const pos = tw.clone().lerp(cw0, 1 - .06 * eio(u));
      setCam(cam, pos, tw, 28, V(-.22, 1, 0).normalize());
      const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0);
      const fwd = tw.clone().sub(pos).normalize();
      const sx = lerp(-7, 7, eio(seg(d, -1, 13)));
      L.sweep.position.copy(tw).addScaledVector(fwd, -7.5).addScaledVector(right, sx).add(V(0, 1.2, 0));
      L.sweep.lookAt(tw); L.sweep.intensity = 13; L.sweep.visible = true;
      L.key.intensity = .12; L.rim.intensity = 2.2; scene.environmentIntensity = .06;
      // bg: dark studio + the strip light glimpsed behind
      const gx = lerp(-200, 1280, eio(seg(d, -1, 13)));
      const g = bg.createLinearGradient(gx - 260, 0, gx + 260, 0);
      g.addColorStop(0, 'rgba(70,56,38,0)'); g.addColorStop(.5, 'rgba(70,56,38,.32)'); g.addColorStop(1, 'rgba(70,56,38,0)');
      bg.fillStyle = g; bg.fillRect(0, 0, W, H);
      E.render3D(scene, cam);
      // fg glare riding the sweep
      halo(fg, gx, 820, 60, 760, .05, '255,236,210');
      drawLockup(fg, q, F, QB);
      target2d = project(cam, Lw(V(7.95, .25, .3)));
      partLabel(fg, '01', 'CHAMPAGNE GOLD ALUMINUM', QB + 3, q, F, { wipeOut: QC, rate: 4, target: target2d, lineFrom: [300, 1420] });
      if (d < 3) { fx.zoom *= 1 + .04 * (1 - d / 3); if (d < 1) fx.rgb = .008; }
      fx.vignette = .55;
    } else {
      // SHOT C (+ WHIP): macro skim along the woven headband, grazing light; then a 70-degree whip pan
      const d = q - QC, u = clamp(d / 6);
      const R0 = 8.1 + .62;
      const th = lerp(1.12, .9, u) - (shot === 'W' ? .03 * seg(q, QW, QE) : 0);
      const radial = th2 => V(Math.cos(th2), Math.sin(th2), 0);
      const camL = radial(th).multiplyScalar(R0 + .55).add(V(0, 0, .75));
      const lookL = radial(th - .22).multiplyScalar(R0 - .55).add(V(0, 0, -.25));
      const pos = Lw(camL), look = Lw(lookL);
      const upW = Lw(radial(th).multiplyScalar(30)).sub(Lw(V(0, 0, 0))).normalize();
      // the whip: yaw the view direction about the camera's up axis (+70 deg in 6 frames, accelerating)
      let dir = look.clone().sub(pos);
      if (shot === 'W') dir.applyAxisAngle(upW, -70 * DEG * ein(seg(q, QW, QE)));
      setCam(cam, pos, pos.clone().add(dir), 42, upW);
      L.sleeve.material = L.fabricB;
      const gl = Lw(radial(th - .9).multiplyScalar(R0 + 3)).add(V(0, 0, -2));
      L.graze.position.copy(gl); L.graze.target.position.copy(Lw(radial(th - .2).multiplyScalar(R0))); L.graze.target.updateMatrixWorld();
      L.graze.intensity = 5; L.key.intensity = .25; L.rim.intensity = 1.2; scene.environmentIntensity = .08;
      L.sweep.position.copy(Lw(radial(th - .55).multiplyScalar(R0 + 2.5)).add(V(0, 0, 3))); L.sweep.lookAt(Lw(radial(th - .2).multiplyScalar(R0))); L.sweep.intensity = 6; L.sweep.visible = shot === 'C'; L.dust.visible = shot === 'C';
      const g = bg.createRadialGradient(780, 520, 0, 780, 520, 900);
      g.addColorStop(0, 'rgba(84,66,42,.4)'); g.addColorStop(1, 'rgba(5,5,6,0)'); bg.fillStyle = g; bg.fillRect(0, 0, W, H);
      E.render3D(scene, cam);
      target2d = project(cam, Lw(radial(th - .16).multiplyScalar(R0)));
      partLabel(fg, '01', 'CHAMPAGNE GOLD ALUMINUM', QB + 3, q, F, { wipeOut: QC - 1, wipeLen: 2, rate: 4 });
      partLabel(fg, '02', 'WOVEN STONE FABRIC', QC, q, F, { wipeOut: QW, nameDelay: 1.5, rate: 6, lineLen: 4, target: shot === 'C' ? target2d : null, lineFrom: [300, 1420] });
      if (d < 3) { fx.zoom *= 1 + .04 * (1 - d / 3); if (d < 1) fx.rgb = .008; }
      fx.vignette = .55;
      if (shot === 'W') {
        const k = seg(q, QW, QE), kk = ein(k);
        fx.rgb = .0015 + .0135 * Math.sin(Math.PI * clamp(k * 1.1));
        // light smear streaks racing left (the strip light and the dust whipping past)
        fg.save(); fg.globalCompositeOperation = 'lighter';
        const ks = eio(clamp(k * 1.25));
        for (let i = 0; i < 46; i++) {
          const y = 140 + rnd(i * 3.3) * 1640, len = 400 + 1200 * rnd(i * 5.1);
          const x = lerp(W + 100 + 900 * rnd(i * 9.9), -len - 200 - 600 * rnd(i * 6.6), ks);
          const a = Math.sin(Math.PI * clamp(k * 1.2)) * (.12 + .38 * rnd(i * 2.2));
          const gg = fg.createLinearGradient(x, 0, x + len, 0);
          gg.addColorStop(0, 'rgba(255,232,196,0)'); gg.addColorStop(.25, `rgba(255,232,196,${a})`); gg.addColorStop(1, 'rgba(255,232,196,0)');
          fg.fillStyle = gg; fg.fillRect(x, y, len, 1.5 + 6 * Math.pow(rnd(i * 4.4), 2));
        }
        // the beam sweeping through frame
        const bx = lerp(W + 600, -700, eio(seg(k, .05, .85)));
        const bk = Math.sin(Math.PI * seg(k, .05, .85));
        halo(fg, bx, 900, 820, 1100, .55 * bk, '255,226,176'); halo(fg, bx, 960, 1400, 60, .5 * bk, '255,240,215'); halo(fg, bx, 960, 260, 900, .35 * bk, '255,236,200');
        fg.restore();
        // the whip lands in light: an anamorphic bar + warm haze peaking on the last frame (s05 opens on a flash)
        const kb = Math.pow(seg(k, .45, 1), 2);
        fx.exposure *= lerp(1, .3, Math.pow(seg(k, .3, 1), 1.5));   // the band dissolves into the light (hides sub-frame ghosts)
        halo(fg, 540, 960, 1300 * kb + 100, 26, .9 * kb, '255,244,225');
        halo(fg, 540, 960, 900, 900, .3 * kb, '255,226,176');
      }
    }
  },
};

// 'Introducing' + 'SILENCE ONE' (from b21.0; type survives the b22 cut and wipes out to the right over 3 frames)
let IN = null;
function drawLockup(fg, q, F, qCut) {
  const q0 = 12, s = 'Introducing', size = 104;
  if (q < q0) return;
  if (!IN) {
    fg.save(); fg.font = font(size, 400, FONT.serif, true); fg.letterSpacing = '0px';
    const tw = fg.measureText(s).width, xs = [];
    for (let i = 0; i < s.length; i++) xs.push(fg.measureText(s.slice(0, i)).width);
    fg.restore(); IN = { tw, xs };
  }
  let clipL = 0;
  if (qCut !== null && q >= qCut) clipL = lerp(0, W, eio(seg(q, qCut, qCut + 3)));
  if (clipL >= W - 1) return;
  fg.save(); fg.beginPath(); fg.rect(clipL, 0, W - clipL, H); fg.clip();
  const x0 = 540 - IN.tw / 2;
  for (let i = 0; i < s.length; i++) {
    const qi = q0 + i * .5, k = seg(q, qi, qi + 4); if (k <= 0) continue;
    const e = expoOut(k);
    fg.save(); fg.translate(x0 + IN.xs[i], 1430 + (1 - e) * 26);
    const g = fg.createLinearGradient(0, -80, 0, 10); g.addColorStop(0, COL.white); g.addColorStop(1, COL.gold);
    text(fg, s[i], 0, 0, { size, weight: 400, family: FONT.serif, italic: true, color: g, align: 'left', alpha: e, blur: (1 - e) * 10 });
    fg.restore();
  }
  // glint travelling along the word as it writes
  if (q > q0 + .5 && q < q0 + 9) { const gx = x0 + IN.tw * clamp((q - q0) / 6.5); halo(fg, gx, 1400, 90, 26, .18 * (1 - seg(q, q0 + 6, q0 + 9)), '255,236,200'); }
  // 'SILENCE ONE' — Unbounded 300 48 gold, tracking .5em, wipes open from the centre
  const q1 = 18;
  if (q >= q1) {
    const k = expoOut(seg(q, q1, q1 + 5)), half = 580 * k, sp = lerp(40, 24, k);
    fg.save(); fg.beginPath(); fg.rect(540 - half, 1460, half * 2, 80); fg.clip();
    text(fg, 'SILENCE ONE', 540 + sp / 2, 1515, { size: 48, weight: 300, family: FONT.display, color: COL.gold, spacing: sp });
    fg.restore();
    // edge sparks of the wipe
    if (k < .98) { halo(fg, 540 - half, 1498, 10, 40, .7, '255,236,200'); halo(fg, 540 + half, 1498, 10, 40, .7, '255,236,200'); }
  }
  fg.restore();
}
