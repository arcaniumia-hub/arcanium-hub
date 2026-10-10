// s11-hero — HERO LOCKUP "Feel everything." (b64-70)
//
// b64.0 FINAL HIT: the filter rips open; out of the muffled 'Hear nothing.' card the product CRASHES in (drops, whips the
//   last 14 deg into its 3/4 pose and settles) under a warm volumetric key beam from top-right with a gold rim, a
//   dimmed mirror reflection on a perfectly flat, still sound-sea horizon (gold glint path under the reflection) and
//   3k dust motes in the beam. 'Hear nothing.' leaps up and shrinks (with motion trails); 'Feel everything.' blurs in.
// b65 wordmark light-wipe from the centre · b66 spec line types on · b66.5 price rises with rolling digits ·
// b67-68 diagonal light sweep: a real 3D strip light grazes the materials + additive haze band + shine on the type;
//   4-point star glints on the gold sliders b67.5 / b68.0.
// b68.5-69.75 THE LAST ANC RING: from the product centre, r 0 -> 1500; inside the frame becomes LUMARC #0e0e14; a 40 px
//   refraction band rides the edge on ALL layers (bg + fg in 2D, the 3D layer through an offscreen target + lens shader);
//   b69-69.5 the stroke crossfades champagne gold -> LUMARC gradient. b69.75: the whole frame is #0e0e14.
import * as THREE from 'three';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, expoIn, rnd, text, font, measure, goldGrad,
  ancRing, downbeatPunch, ADDITIVE, COL, FONT } from '../lib.js';
import { createHeadphone } from '../model.js';

const B0 = 64;
const DEG = Math.PI / 180;
const FOV = 30;
const PC = .7;                       // model-space centre height of the product
const FLOOR = -10.0;                 // calm sea level (world), product centre at y=0
const CAM = { az: 34 * DEG, el: 4.2 * DEG, dist: 84 };
const RING_C = [540, 930];
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const MINUS = '−';
const SPEC = MINUS + '42 dB ANC · 40 H · 360° · 250 G';

// ------------------------------------------------------------------ reflection: premultiplied, depth-correct, screen-faded
const REFL = { value: new THREE.Vector3(.22, 1400, 1700) };   // amount, fade start y, fade end y (screen px, top origin)
function patchReflection(root) {
  // cheap Lambert stand-ins (the reflection is seen at <= 22 %, faded): same colour/map, premultiplied output, depth-correct
  const cache = new Map();
  const conv = m => {
    if (cache.has(m)) return cache.get(m);
    const l = new THREE.MeshLambertMaterial({ color: m.color ? m.color.clone() : 0xffffff, map: m.map || null, side: m.side });
    if (m.metalness > .5) l.color.multiplyScalar(1.6);          // metals have no diffuse: fake their brightness
    l.blending = THREE.NoBlending; l.customProgramCacheKey = () => 's11-refl';
    l.onBeforeCompile = sh => {
      sh.uniforms.uRefl = REFL;
      sh.fragmentShader = 'uniform vec3 uRefl;\n' + sh.fragmentShader.replace('void main() {', `void main() {\n if (${H}.0 - gl_FragCoord.y > uRefl.z) discard;`).replace('#include <dithering_fragment>',
        `#include <dithering_fragment>
        { float sy = ${H}.0 - gl_FragCoord.y; float k = uRefl.x*(1. - smoothstep(uRefl.y, uRefl.z, sy));
          gl_FragColor = vec4(gl_FragColor.rgb*k, k); }`);
    };
    cache.set(m, l); return l;
  };
  root.traverse(o => { if (o.material) o.material = Array.isArray(o.material) ? o.material.map(conv) : conv(o.material); });
}

// ------------------------------------------------------------------ the calm SOUND SEA: flat, still horizon lines
function buildSea() {
  // rows evenly spaced in 1/depth (as seen from the camera, CAMZ units away) -> a true perspective water plane out to the horizon
  const nx = 120, nz = 150, CAMZ = 82, n = nx * nz;
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), base = new Float32Array(n), glint = new Float32Array(n), idx = [];
  for (let j = 0; j < nz; j++) {
    const u = j / (nz - 1), d = 1 / lerp(1 / 1400, 1 / 15, Math.pow(u, 1.6)), z = CAMZ - d;
    const half = .19 * d + 16;
    for (let i = 0; i < nx; i++) {
      const x = (i / (nx - 1) - .5) * 2 * half, k = j * nx + i;
      pos.set([x, 0, z], k * 3);
      if (i < nx - 1) idx.push(k, k + 1);
      const far = Math.pow(1 - seg(d, 200, 1400), 1.5), near = .12 + .88 * Math.pow(seg(d, 16, 75), 1.6);
      const side = 1 - seg(Math.abs(x) / half, .55, 1);
      base[k] = far * near * side;
      // glint path: from under the product toward the camera, widening, strongest just under the reflection
      const sx = 2.0 + Math.max(0, z) * .07;
      glint[k] = Math.exp(-x * x / (sx * sx)) * seg(z, -30, -6) * (1 - seg(z, 34, 62));
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.setIndex(idx);
  const mesh = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, ...ADDITIVE })); mesh.frustumCulled = false;
  const MU = lin(COL.muted), GO = lin(COL.gold), HI = lin(COL.goldHi);
  function update(t, alpha, glintAmt) {
    for (let k = 0; k < n; k++) {
      const x = pos[k * 3], z = pos[k * 3 + 2];
      // a slow shimmer travelling toward the camera along the glint path (the lines themselves never move)
      const sh = .55 + .45 * Math.sin(z * .55 - t * 3.1 + Math.sin(x * .7 + t * .9) * 1.4);
      const gl = glint[k] * glintAmt * (.45 + .55 * sh);
      const a = alpha * base[k] * .42;
      col[k * 3] = a * MU.r + gl * lerp(GO.r, HI.r, sh) * 1.9;
      col[k * 3 + 1] = a * MU.g + gl * lerp(GO.g, HI.g, sh) * 1.9;
      col[k * 3 + 2] = a * MU.b + gl * lerp(GO.b, HI.b, sh) * 1.9;
    }
    g.attributes.color.needsUpdate = true;
  }
  return { mesh, update };
}

// ------------------------------------------------------------------ dust motes in the key beam
const DUST_V = `attribute float aR; uniform float uT, uPx, uSize; uniform vec3 uB0, uBd; varying float vA; varying float vS;
void main(){
  vec3 p = position;
  p.y = mod(p.y - uT*(.25+.5*aR) + 26., 52.) - 26.;
  p.x += sin(uT*.5 + aR*40.)*.8; p.z += cos(uT*.42 + aR*31.)*.8;
  vec3 q = p - uB0; float along = dot(q, uBd); float perp = length(q - uBd*along);
  float beam = exp(-pow(perp/8.5, 2.));
  vec4 mv = modelViewMatrix*vec4(p, 1.);
  float s = uSize*(.45+.9*aR)*uPx/max(-mv.z, .5);
  vS = clamp(s, 1.5, 70.); gl_PointSize = vS;
  vA = (.04 + beam)*(.45+.55*sin(uT*2.1 + aR*60.))*min(1., pow(9./vS, 1.3))*step(.5, -mv.z);
  gl_Position = projectionMatrix*mv;
}`;
const DUST_F = `uniform float uAlpha; uniform vec3 uCol; varying float vA; varying float vS;
void main(){
  float d = length(gl_PointCoord - .5)*2.;
  float gauss = exp(-d*d*4.), disc = smoothstep(1., .82, d)*(.65+.35*smoothstep(.5, .95, d));
  float a = mix(gauss, disc, smoothstep(10., 30., vS));
  gl_FragColor = vec4(uCol*a*vA*uAlpha, 1.);
}`;

// ------------------------------------------------------------------ overlay (pixel-space ortho, additive HDR light)
const OV_V = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position, 1.); }`;
// soft band: gaussian across x, soft ends along y
const BAND_F = `uniform vec3 uCol; uniform float uI; varying vec2 vUv;
void main(){ float x = (vUv.x - .5)*2.; float a = exp(-x*x*3.2) + .35*exp(-x*x*40.); float e = smoothstep(0., .25, vUv.y)*smoothstep(1., .75, vUv.y);
  gl_FragColor = vec4(uCol*a*e*uI, 1.); }`;
// 4-point star glint: core + long thin cross rays + short diagonal rays
const STAR_F = `uniform vec3 uCol; uniform float uI, uRot; varying vec2 vUv;
void main(){ vec2 p = (vUv - .5)*2.; float c = cos(uRot), s = sin(uRot); p = mat2(c, -s, s, c)*p;
  float r = length(p);
  float core = exp(-r*r*120.)*2. + exp(-r*r*14.)*.35;
  float rays = exp(-abs(p.y)*90.)*pow(max(0., 1.-abs(p.x)), 3.) + exp(-abs(p.x)*90.)*pow(max(0., 1.-abs(p.y)), 3.);
  vec2 q = mat2(.7071, -.7071, .7071, .7071)*p;
  float diag = (exp(-abs(q.y)*140.)*pow(max(0., 1.-abs(q.x)*2.2), 3.) + exp(-abs(q.x)*140.)*pow(max(0., 1.-abs(q.y)*2.2), 3.))*.45;
  gl_FragColor = vec4(uCol*(core + rays + diag)*uI, 1.); }`;
// anamorphic streak: thin horizontal line with a wide soft halo
const FLARE_F = `uniform vec3 uCol; uniform float uI; varying vec2 vUv;
void main(){ vec2 p = (vUv - .5)*2.; float fx = pow(max(0., 1.-abs(p.x)), 2.2);
  float a = (exp(-p.y*p.y*900.) + .25*exp(-p.y*p.y*30.))*fx + exp(-dot(p*vec2(6., 1.), p*vec2(6., 1.))*3.)*.4;
  gl_FragColor = vec4(uCol*a*uI, 1.); }`;
function ovMesh(frag, col, w, h) {
  const m = new THREE.ShaderMaterial({ vertexShader: OV_V, fragmentShader: frag, ...ADDITIVE, depthTest: false,
    uniforms: { uCol: { value: lin(col) }, uI: { value: 0 }, uRot: { value: 0 } } });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m); mesh.frustumCulled = false; mesh.visible = false;
  return mesh;
}

// ------------------------------------------------------------------ 3D lens pass: refraction band + erase (ANC ring)
const LENS_F = `uniform sampler2D tSrc; uniform vec2 uC; uniform float uR, uBand, uScale; varying vec2 vUv;
void main(){
  vec2 px = vec2(vUv.x*${W}., (1. - vUv.y)*${H}.);
  vec2 d = px - uC; float r = length(d);
  if (uR > 0. && r < uR) { gl_FragColor = vec4(0.); return; }
  vec2 uv = vUv;
  if (uR > 0. && r < uR + uBand) { vec2 sp = uC + d/uScale; uv = vec2(sp.x/${W}., 1. - sp.y/${H}.); }
  gl_FragColor = texture2D(tSrc, uv);
}`;

// ------------------------------------------------------------------ 2D helpers
const SCR = {};
function scratch(name) {
  if (!SCR[name]) { const c = document.createElement('canvas'); c.width = W; c.height = H; SCR[name] = { c, x: c.getContext('2d') }; }
  return SCR[name];
}
// redraw the layer at `scale` about (cx,cy) inside the annulus [r, r+band] (replacing what was there)
function refractLayer(ctx, cx, cy, r, band, scale, transparent) {
  const s = scratch('refr'); s.x.setTransform(1, 0, 0, 1, 0, 0); s.x.clearRect(0, 0, W, H); s.x.drawImage(ctx.canvas, 0, 0);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.beginPath(); ctx.arc(cx, cy, r + band, 0, TAU); ctx.arc(cx, cy, Math.max(0, r), 0, TAU, true); ctx.clip();
  if (transparent) ctx.clearRect(0, 0, W, H);
  ctx.translate(cx, cy); ctx.scale(scale, scale); ctx.translate(-cx, -cy);
  ctx.drawImage(s.c, 0, 0); ctx.restore();
}
// volumetric beam wedge (bg)
function beam(ctx, sx, sy, tx, ty, spread, alpha, color = '255,226,176') {
  if (alpha <= .003) return;
  const ang = Math.atan2(ty - sy, tx - sx), len = Math.hypot(tx - sx, ty - sy) * 1.9;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(sx, sy); ctx.rotate(ang);
  for (let i = 0; i < 6; i++) {
    const s = spread * (.35 + i * .2);
    const g = ctx.createLinearGradient(0, 0, len, 0);
    g.addColorStop(0, `rgba(${color},${alpha * .3})`); g.addColorStop(.45, `rgba(${color},${alpha * .13})`); g.addColorStop(1, `rgba(${color},0)`);
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(0, -18); ctx.lineTo(len, -len * s); ctx.lineTo(len, len * s); ctx.lineTo(0, 18); ctx.closePath(); ctx.globalAlpha = .3; ctx.fill();
  }
  ctx.restore();
}
function glow(ctx, x, y, rx, ry, alpha, color) {
  if (alpha <= .003) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(x, y); ctx.scale(rx / ry, 1);
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, ry);
  g.addColorStop(0, `rgba(${color},${alpha})`); g.addColorStop(.45, `rgba(${color},${alpha * .3})`); g.addColorStop(1, `rgba(${color},0)`);
  ctx.fillStyle = g; ctx.fillRect(-ry, -ry, ry * 2, ry * 2); ctx.restore();
}

// ------------------------------------------------------------------ pre-blurred sprites (canvas blur filters are far too slow per frame)
const BLURS = [0, 2.5, 6, 12, 22];
function makeSprite(w, h, ax, ay, paint) {
  const lv = BLURS.map(bl => {
    const c = document.createElement('canvas'); c.width = Math.ceil(w); c.height = Math.ceil(h); const x = c.getContext('2d');
    if (bl > 0) x.filter = `blur(${bl}px)`; paint(x); return c;
  });
  return { lv, ax, ay, w, h };
}
// draw sprite anchored at (x,y) (anchor = ax,ay inside the sprite), scaled, with blur `bl` (crossfade of the nearest levels)
function drawSprite(ctx, sp, x, y, sc, bl, alpha) {
  if (alpha <= .003) return;
  bl = clamp(bl, 0, BLURS[BLURS.length - 1]);
  let i = 0; while (i < BLURS.length - 2 && bl > BLURS[i + 1]) i++;
  const u = clamp((bl - BLURS[i]) / (BLURS[i + 1] - BLURS[i]));
  ctx.save();
  const put = (c, a) => { if (a <= .003) return; ctx.globalAlpha = alpha * a; ctx.drawImage(c, x - sp.ax * sc, y - sp.ay * sc, sp.w * sc, sp.h * sc); };
  put(sp.lv[i], 1 - u); put(sp.lv[i + 1], u);
  ctx.restore();
}

// ------------------------------------------------------------------ layout (computed once fonts are ready)
let L = null;
function layout(ctx) {
  const o = {};
  // 'Feel everything.' per-letter x (left edges) at 72 px italic serif
  ctx.save(); ctx.font = font(72, 400, FONT.serif, true); ctx.letterSpacing = '0px';
  const fe = 'Feel everything.'; o.feW = ctx.measureText(fe).width; o.feX = [];
  for (let i = 0; i < fe.length; i++) o.feX.push(ctx.measureText(fe.slice(0, i)).width);
  ctx.restore();
  o.fe = fe;
  // wordmark: Unbounded 800, tracking .18em, auto-fit to max 900 px
  const wm = 'SILENCE ONE';
  const w100 = measure(ctx, wm, 100, 800, FONT.display, 18) - 18;     // minus the trailing tracking
  o.wmSize = Math.min(64, 100 * 900 / w100);
  o.wmSp = .18 * o.wmSize;
  o.wmA = measure(ctx, 'SILENCE ', o.wmSize, 800, FONT.display, o.wmSp);
  o.wmW = measure(ctx, wm, o.wmSize, 800, FONT.display, o.wmSp) - o.wmSp;
  o.wmX0 = 540 - o.wmW / 2;
  // spec line: JetBrains Mono 400 30 px, tracking .1em
  o.spSp = 3; o.spW = measure(ctx, SPEC, 30, 400, FONT.mono, o.spSp) - o.spSp; o.spX0 = 540 - o.spW / 2;
  // price: Unbounded 500 64 px
  const pr = '$349'; o.pr = pr; o.prX = []; o.prCW = [];
  ctx.save(); ctx.font = font(64, 500, FONT.display); ctx.letterSpacing = '0px';
  o.prW = ctx.measureText(pr).width;
  for (let i = 0; i < pr.length; i++) { o.prX.push(ctx.measureText(pr.slice(0, i)).width); o.prCW.push(ctx.measureText(pr[i]).width); }
  o.digW = []; for (let d = 0; d < 10; d++) o.digW.push(ctx.measureText(String(d)).width);
  ctx.restore();
  o.prX0 = 540 - o.prW / 2;
  // sprites: 'Hear nothing.' at 120 px; 'Feel everything.' per letter with one continuous gold gradient
  const PAD = 50;
  const hw = measure(ctx, 'Hear nothing.', 120, 400, FONT.serif, 0, true);
  o.hear = makeSprite(hw + PAD * 2 + 40, 120 * 1.5 + PAD * 2, (hw + PAD * 2 + 40) / 2, PAD + 120 * 1.05,
    x => text(x, 'Hear nothing.', (hw + PAD * 2 + 40) / 2, PAD + 120 * 1.05, { size: 120, family: FONT.serif, italic: true, color: COL.white }));
  const x0 = 540 - o.feW / 2; o.feS = [];
  for (let i = 0; i < fe.length; i++) {
    if (fe[i] === ' ') { o.feS.push(null); continue; }
    const lw = measure(ctx, fe[i], 72, 400, FONT.serif, 0, true), w = lw + PAD * 2 + 30, h = 72 * 1.5 + PAD * 2, ay = PAD + 72 * 1.08;
    const lx = x0 + o.feX[i];
    const sp = makeSprite(w, h, PAD + 10 + lw / 2, ay, x => {
      const g = x.createLinearGradient(x0 - lx + PAD + 10, 0, x0 - lx + PAD + 10 + o.feW, 0);
      g.addColorStop(0, COL.gold2); g.addColorStop(.35, COL.goldHi); g.addColorStop(.55, COL.gold); g.addColorStop(1, COL.gold2);
      x.font = font(72, 400, FONT.serif, true); x.textAlign = 'left'; x.fillStyle = g; x.fillText(fe[i], PAD + 10, ay);
    });
    sp.x = lx + lw / 2; o.feS.push(sp);
  }
  return o;
}

// ------------------------------------------------------------------ rig
let R = null;
function build(E) {
  RectAreaLightUniformsLib.init();
  const scene = new THREE.Scene();
  scene.environment = E.env; scene.environmentIntensity = .16; scene.userData._envSet = true;
  const cam = new THREE.PerspectiveCamera(FOV, W / H, .5, 700);
  // product
  const prod = new THREE.Group(); scene.add(prod);
  const hp = createHeadphone(); hp.root.position.y = -PC; prod.add(hp.root);
  // mirrored reflection (second instance) about the sea plane
  const reflG = new THREE.Group(); reflG.scale.y = -1; reflG.position.y = 2 * FLOOR; scene.add(reflG);
  const reflP = new THREE.Group(); reflG.add(reflP);
  const hp2 = createHeadphone(); hp2.root.position.y = -PC; reflP.add(hp2.root);
  [hp, hp2].forEach(h => h.cups.forEach(c => ['pcb', 'battery', 'magnet', 'coil', 'driver'].forEach(k => { c.userData.parts[k].visible = false; })));
  patchReflection(hp2.root);
  hp2.band.group.visible = false; hp2.sliders.forEach(g => { g.visible = false; });   // below the fade: never seen
  // sea
  const sea = buildSea(); const seaG = new THREE.Group(); seaG.position.y = FLOOR + .01; seaG.rotation.y = CAM.az; seaG.add(sea.mesh); scene.add(seaG);
  // dust
  const ND = 3000, dp = new Float32Array(ND * 3), dr = new Float32Array(ND);
  for (let i = 0; i < ND; i++) { dp.set([(rnd(i * 1.7 + 3) - .5) * 80, (rnd(i * 2.3 + 5) - .5) * 52 + 4, (rnd(i * 3.9 + 7) - .5) * 70], i * 3); dr[i] = rnd(i * 5.1 + 11); }
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(dp, 3)); dg.setAttribute('aR', new THREE.BufferAttribute(dr, 1));
  const dustMat = new THREE.ShaderMaterial({ vertexShader: DUST_V, fragmentShader: DUST_F, ...ADDITIVE,
    uniforms: { uT: { value: 0 }, uPx: { value: H * .5 / Math.tan(FOV / 2 * DEG) }, uSize: { value: .15 }, uAlpha: { value: 1 },
      uB0: { value: V3(42, 46, 30) }, uBd: { value: V3(-42, -46, -30).normalize() }, uCol: { value: lin('#ffe2b0').multiplyScalar(1.5) } } });
  const dust = new THREE.Points(dg, dustMat); dust.frustumCulled = false; scene.add(dust);
  // lights
  const key = new THREE.DirectionalLight(0xffe2b0, 1.1); key.position.set(40, 34, 30); scene.add(key);
  const spot = new THREE.SpotLight(0xffe4b8, 9000, 0, 16 * DEG, 1, 2); spot.position.set(46, 60, 34); spot.target.position.set(-3, -2, 0); scene.add(spot); scene.add(spot.target);
  const rim = new THREE.DirectionalLight(0xe6c896, 3.4); rim.position.set(-34, 14, -26); scene.add(rim);
  const rim2 = new THREE.DirectionalLight(0xfff0d8, 1.6); rim2.position.set(30, 22, -34); scene.add(rim2);
  const under = new THREE.DirectionalLight(0xffd9a0, .3); under.position.set(5, -30, 14); scene.add(under);
  const sweep = new THREE.RectAreaLight(0xfff0dc, 0, 1.1, 60); scene.add(sweep);
  // overlay scene (pixel space: x right, y DOWN as negative world y)
  const ov = new THREE.Scene(); ov.userData.autoEnv = false;
  const ovCam = new THREE.OrthographicCamera(0, W, 0, -H, -10, 10);
  const band = ovMesh(BAND_F, '#fff4e4', 220 * 1.7, 3400); ov.add(band);
  const stars = [0, 1].map(() => { const m = ovMesh(STAR_F, '#fff2d8', 300, 300); ov.add(m); return m; });
  const flare = ovMesh(FLARE_F, '#ffd9a8', 2600, 120); ov.add(flare);
  // offscreen target + lens pass for the ANC ring
  const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
  const lensMat = new THREE.ShaderMaterial({ vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`,
    fragmentShader: LENS_F, blending: THREE.NoBlending, depthTest: false, depthWrite: false,
    uniforms: { tSrc: { value: rt.texture }, uC: { value: new THREE.Vector2(...RING_C) }, uR: { value: 0 }, uBand: { value: 40 }, uScale: { value: 1.04 } } });
  const lensScene = new THREE.Scene(); lensScene.userData.autoEnv = false;
  const lq = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), lensMat); lq.frustumCulled = false; lensScene.add(lq);
  return { spot, scene, cam, prod, hp, hp2, reflP, sea, seaG, dust, dustMat, key, rim, rim2, under, sweep, ov, ovCam, band, stars, flare, rt, lensMat, lensScene };
}

const tmpV = new THREE.Vector3();
function project(cam, p) { tmpV.copy(p).project(cam); return [(tmpV.x + 1) / 2 * W, (1 - tmpV.y) / 2 * H]; }
function place(mesh, x, y, sx = 1, sy = 1, rot = 0) { mesh.position.set(x, -y, 0); mesh.scale.set(sx, sy, 1); mesh.rotation.z = -rot; }

// sweep: band centre as a signed distance (px) along the normal n = (cos25, sin25) from RING_C
const SW_A = 25 * DEG, SW_N = [Math.cos(SW_A), Math.sin(SW_A)];
const sdist = (x, y) => (x - RING_C[0]) * SW_N[0] + (y - RING_C[1]) * SW_N[1];

export default {
  id: 's11-hero', start: 64, end: 70,
  cutIn: 'none',
  init(E) { R = build(E); },
  draw(E, lt, t) {
    const b = B0 + lt / BEAT + 1e-6, f = lt * 30, fx = E.fx, bg = E.bg, fg = E.fg;
    if (!L) L = layout(fg);
    const { scene, cam, prod, hp, reflP, sea, dustMat } = R;

    // ---------------- post: base hero grade
    fx.exposure = .9; fx.bloom = .62; fx.bloomThreshold = .8; fx.vignette = .45; fx.grain = .04; fx.sat = 1.0; fx.rgb = .0008;
    downbeatPunch(fx, t, B0 * BEAT, { flash: 0, zoom: 1.1, rgb: .02, zoomBlur: .35, shake: .008 });
    if (f < 8) { fx.flash = .6 * Math.exp(-f / 1.1) * (1 - f / 8); fx.flashColor = [1, .93, .8]; }

    // ---------------- product pose: crash-in settle + slow +20 deg turn + float
    const land = expoOut(seg(f, 0, 14));
    const yaw = 20 * DEG * seg(b, 64, 70) - 14 * DEG * (1 - land);
    prod.rotation.set(-3 * DEG * (1 - land), yaw, 2.5 * DEG * (1 - land));
    prod.position.y = .1 * Math.sin(lt * 2.3) + 1.6 * (1 - land);
    prod.scale.setScalar(1 + .07 * (1 - land));
    reflP.position.copy(prod.position); reflP.rotation.copy(prod.rotation); reflP.scale.copy(prod.scale);

    // ---------------- camera: fixed 3/4 front, imperceptible push + drift
    const dist = CAM.dist * (1 - .035 * eio(seg(b, 64, 70))), az = CAM.az + 1.2 * DEG * Math.sin(lt * .6), el = CAM.el;
    cam.position.set(Math.sin(az) * Math.cos(el) * dist, Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
    cam.lookAt(0, -1, 0);
    cam.setViewOffset(W, H, 0, 62, W, H);                 // product centre lands at y 930
    cam.updateMatrixWorld();

    // ---------------- lights (key rips on at the hit, kicks breathe the beam)
    const kicks = [64, 65.5, 66, 67.5].map(k => b >= k ? Math.exp(-(b - k) * BEAT / .16) : 0);
    const kick = Math.max(...kicks.slice(1)) * .5;
    const hit = b >= 64 ? Math.exp(-f / 5) : 0;
    R.key.intensity = 1.1 * (1 + .6 * hit); R.spot.intensity = 9000 * (1 + .5 * hit + .15 * kick); R.rim.intensity = 3.4 * (1 + .8 * hit); R.rim2.intensity = 1.6; R.under.intensity = .3;
    // b67-68 SWEEP: band moves along its normal; crossing the left slider at b67.5 and the right slider at b68.0
    prod.updateMatrixWorld(true);
    const slL = project(cam, hp.sliders[0].localToWorld(V3(0, .4, 0))), slR = project(cam, hp.sliders[1].localToWorld(V3(0, .4, 0)));
    const dL = sdist(...slL), dR = sdist(...slR);
    const sPos = b < 67.5 ? lerp(-900, dL, eio(seg(b, 66.85, 67.5)) * .25 + seg(b, 66.85, 67.5) * .75) : b < 68 ? lerp(dL, dR, seg(b, 67.5, 68)) : lerp(dR, 1100, ein(seg(b, 68, 68.6)) * .4 + seg(b, 68, 68.6) * .6);
    const swOn = seg(b, 66.85, 67.05) * (1 - seg(b, 68.35, 68.6));
    {
      // strip light: on the camera ray through the band centre (screen point on the band line through RING_C), 40% of the way
      const sx = RING_C[0] + SW_N[0] * sPos, sy = RING_C[1] + SW_N[1] * sPos;
      const ndc = V3(sx / W * 2 - 1, -(sy / H * 2 - 1), .5).unproject(cam);
      const dir = ndc.sub(cam.position).normalize();
      R.sweep.position.copy(cam.position).addScaledVector(dir, dist * .45);
      R.sweep.lookAt(0, 0, 0); R.sweep.rotateZ(-SW_A);
      R.sweep.intensity = 70 * swOn; R.sweep.visible = swOn > .001;
    }

    // ---------------- bg: ink, warm key beam from top-right, horizon warmth
    bg.fillStyle = COL.ink; bg.fillRect(0, 0, W, H);
    const beamA = .5 * (1 + .5 * hit + .15 * kick);
    beam(bg, 1180, -200, 560, 930, .19, beamA);
    const hz = project(cam, V3(-Math.sin(CAM.az) * 3000, FLOOR, -Math.cos(CAM.az) * 3000))[1];
    glow(bg, 540, hz, 1000, 150, .08, '230,200,150');                     // horizon haze
    { const g = bg.createLinearGradient(0, 0, W, 0); g.addColorStop(0, 'rgba(230,200,150,0)'); g.addColorStop(.5, 'rgba(240,215,170,.22)'); g.addColorStop(1, 'rgba(230,200,150,0)');
      bg.fillStyle = g; bg.fillRect(0, hz - 1, W, 2); }
    glow(bg, 760, 380, 520, 520, .05 * (1 + hit), '255,226,176');         // light pool in the beam
    glow(bg, 540, 1420, 520, 120, .05, '230,200,150');                    // warmth under the reflection

    // ---------------- 3D
    sea.update(t, 1, 1);
    dustMat.uniforms.uT.value = t + 3; dustMat.uniforms.uAlpha.value = 1 + .4 * kick;
    // overlay: sweep haze band, glints, hit flare
    {
      const bx = RING_C[0] + SW_N[0] * sPos, by = RING_C[1] + SW_N[1] * sPos;
      R.band.visible = swOn > .01; place(R.band, bx, by, 1, 1, SW_A); R.band.material.uniforms.uI.value = .085 * swOn;
      [[67.5, slL], [68.0, slR]].forEach(([at, p], i) => {
        const g = (b - at) * 12, m = R.stars[i];                       // frames since
        const k = g < 0 ? 0 : g < 1.5 ? expoOut(g / 1.5) : Math.exp(-(g - 1.5) / 3.2);
        m.visible = k > .01; place(m, p[0], p[1], .4 + .8 * k, .4 + .8 * k, 12 * DEG + g * 2.5 * DEG);
        m.material.uniforms.uI.value = 3.2 * k;
      });
      const rp = project(cam, hp.cups[1].localToWorld(V3(0, -.2, 4.4)));
      R.flare.visible = hit > .01; place(R.flare, rp[0], rp[1], 1, 1, 0); R.flare.material.uniforms.uI.value = 2.4 * hit;
    }
    // ANC ring radius (b68.5-69.75): ease-in-out leaning toward ease-in so the brand phase is seen on screen
    const rk = seg(b, 68.5, 69.75), ringR = b < 68.5 ? 0 : 1500 * Math.pow(rk, 1.5);
    const render3D = target => {
      const r = E.renderer;
      if (target) { r.setRenderTarget(target); r.setClearColor(0x000000, 0); r.clear(true, true, true); r.render(scene, cam); r.clearDepth(); r.render(R.ov, R.ovCam); }
      else { E.render3D(scene, cam); E.render3D(R.ov, R.ovCam); }
    };
    if (ringR > 0) {
      render3D(R.rt);
      R.lensMat.uniforms.uR.value = ringR; R.lensMat.uniforms.uBand.value = 40;
      E.render3D(R.lensScene, R.ovCam);
    } else render3D(null);

    // ---------------- fg typography
    // 'Hear nothing.' leaps (990, 120 px) -> (330, 72 px), expoOut 6 frames, with motion trails (pre-blurred sprites)
    {
      const k = expoOut(seg(f, 0, 6)), y = lerp(990, 330, k), s = lerp(120, 72, k);
      const v = f < 6 ? (expoOut(seg(f + .5, 0, 6)) - expoOut(seg(f - .5, 0, 6))) : 0;     // speed (fraction / frame)
      if (f >= 6) text(fg, 'Hear nothing.', 540, 330, { size: 72, family: FONT.serif, italic: true, color: COL.white });
      else {
        for (let i = 6; i >= 1; i--) {
          const kk = expoOut(seg(f - i * .2, 0, 6));
          drawSprite(fg, L.hear, 540, lerp(990, 330, kk), lerp(120, 72, kk) / 120, 3 + i * 2.2, .2 * (1 - i / 7) * clamp(v * 6));
        }
        drawSprite(fg, L.hear, 540, y, s / 120, v * 22, 1);
      }
    }
    // 'Feel everything.' gold, letters blurring in (6 frames each, ~1-frame stagger), pre-blurred letter sprites
    for (let i = 0; i < L.fe.length; i++) {
      const sp = L.feS[i]; if (!sp) continue;
      const k = seg(f, i * .85, i * .85 + 6); if (k <= 0) continue;
      const e = expoOut(k);
      if (k >= 1) { fg.drawImage(sp.lv[0], Math.round(sp.x - sp.ax), Math.round(420 - sp.ay)); continue; }
      drawSprite(fg, sp, sp.x, 420 - (1 - e) * 10, lerp(1.35, 1, e), (1 - e) * 16, e, true);
    }
    // wordmark: light-wipe from the centre outward over 1 beat (b65-66), tracking settles
    if (b >= 65) {
      const k = seg(b, 65, 66), e = eio(k) * .4 + expoOut(k) * .6, half = (L.wmW / 2 + 40) * e;
      const sp = lerp(L.wmSp * 1.9, L.wmSp, expoOut(k)), shift = (sp - L.wmSp) * 5;   // 'SILENCE ONE' = 11 chars -> 10 gaps
      const x0 = L.wmX0 - shift, y = 1420;
      fg.save(); fg.beginPath(); fg.rect(540 - half, y - 90, half * 2, 130); fg.clip();
      text(fg, 'SILENCE', x0, y, { size: L.wmSize, weight: 800, family: FONT.display, color: COL.white, align: 'left', spacing: sp });
      const xa = x0 + measure(fg, 'SILENCE ', L.wmSize, 800, FONT.display, sp);
      const ow = measure(fg, 'ONE', L.wmSize, 800, FONT.display, sp) - sp;
      fg.save(); fg.font = font(L.wmSize, 800, FONT.display); fg.letterSpacing = sp + 'px'; fg.textAlign = 'left';
      fg.fillStyle = goldGrad(fg, xa, xa + ow, .1 * Math.sin(lt * 1.3)); fg.fillText('ONE', xa, y); fg.restore();
      fg.restore();
      // the wipe's light edges
      if (k > 0 && k < 1) {
        const a = .9 * (1 - seg(k, .35, .8));
        [540 - half, 540 + half].forEach(xe => {
          const g = fg.createLinearGradient(0, y - 95, 0, y + 45); g.addColorStop(0, 'rgba(255,236,200,0)'); g.addColorStop(.5, `rgba(255,236,200,${a})`); g.addColorStop(1, 'rgba(255,236,200,0)');
          fg.fillStyle = g; fg.fillRect(xe - 1, y - 95, 2, 140);
          glow(fg, xe, y - 24, 16, 70, .35 * a, '255,226,176');
        });
      }
    }
    // spec line types on (2 chars / frame) from b66.0 with a gold cursor
    if (b >= 66) {
      const fs = (b - 66) * 12, n = Math.min(SPEC.length, Math.floor(fs * 2) + 1);
      const s = SPEC.slice(0, n);
      text(fg, s, L.spX0, 1500, { size: 30, weight: 400, family: FONT.mono, color: COL.muted, align: 'left', spacing: L.spSp });
      const done = fs * 2 >= SPEC.length;
      const ca = done ? (1 - seg(fs, SPEC.length / 2 + 4, SPEC.length / 2 + 7)) * (Math.floor(fs / 3) % 2 ? .25 : 1) : 1;
      if (ca > .01) { const cw = measure(fg, s, 30, 400, FONT.mono, L.spSp); fg.save(); fg.globalAlpha = ca; fg.fillStyle = COL.gold; fg.fillRect(L.spX0 + cw + 2, 1476, 16, 30); fg.restore(); }
    }
    // price rises in (y +20 -> 0, 6 frames) with rolling digits $000 -> $349
    if (b >= 66.5) {
      const fp = (b - 66.5) * 12, e = eout(seg(fp, 0, 6)), y = 1590 + 20 * (1 - e), size = 64;
      fg.save(); fg.globalAlpha = e;
      text(fg, '$', L.prX0, y, { size, weight: 500, family: FONT.display, color: COL.white, align: 'left' });
      fg.beginPath(); fg.rect(L.prX0 + L.prX[1] - 6, y - size * .86, L.prW, size * .96); fg.clip();
      const step = size * 1.05;
      for (let i = 1; i < 4; i++) {
        const tgt = +L.pr[i], cyc = 10 * (i === 3 ? 2 : 1);
        const p = (tgt + cyc) * expoOut(seg(fp, 0, 7 + 2.5 * i)) ;           // reel position (digits passed)
        const cx = L.prX0 + L.prX[i] + L.prCW[i] / 2, base = Math.floor(p), fr = p - base;
        const speed = (tgt + cyc) * (expoOut(seg(fp + .5, 0, 7 + 2.5 * i)) - expoOut(seg(fp - .5, 0, 7 + 2.5 * i)));
        const gh = Math.min(.45, speed * .09);
        for (let j = -1; j <= 1; j++) {
          const d = ((base + j) % 10 + 10) % 10, yy = y + (j - fr) * -step;
          text(fg, String(d), cx, yy, { size, weight: 500, family: FONT.display, color: COL.white, align: 'center' });
        }
      }
      fg.restore();
    }
    // type shine as the sweep passes (only over the letters)
    if (swOn > .01) {
      const bx = RING_C[0] + SW_N[0] * sPos, by = RING_C[1] + SW_N[1] * sPos;
      fg.save(); fg.globalCompositeOperation = 'source-atop'; fg.translate(bx, by); fg.rotate(SW_A);
      const g = fg.createLinearGradient(-130, 0, 130, 0);
      g.addColorStop(0, 'rgba(255,244,220,0)'); g.addColorStop(.5, `rgba(255,248,232,${.85 * swOn})`); g.addColorStop(1, 'rgba(255,244,220,0)');
      fg.fillStyle = g; fg.fillRect(-130, -2000, 260, 4000); fg.restore();
    }

    // ---------------- THE LAST ANC RING (b68.5-69.75)
    if (ringR > 0) {
      const [cx, cy] = RING_C;
      refractLayer(bg, cx, cy, ringR, 40, 1.04, false);
      refractLayer(fg, cx, cy, ringR, 40, 1.04, true);
      fg.save(); fg.fillStyle = COL.lmBg; fg.beginPath(); fg.arc(cx, cy, ringR, 0, TAU); fg.fill();
      // light wake just inside the ring
      const mixB = eio(seg(b, 69, 69.5));
      const wake = fg.createRadialGradient(cx, cy, Math.max(0, ringR - 340), cx, cy, ringR);
      const wc = [lerp(230, 106, mixB), lerp(200, 85, mixB), lerp(150, 255, mixB)].map(Math.round).join(',');
      wake.addColorStop(0, `rgba(${wc},0)`); wake.addColorStop(.7, `rgba(${wc},.03)`); wake.addColorStop(1, `rgba(${wc},.16)`);
      fg.fillStyle = wake; fg.beginPath(); fg.arc(cx, cy, ringR, 0, TAU); fg.fill();
      fg.restore();
      ancRing(fg, cx, cy, ringR, { refract: false, gradient: mixB > 0 ? [COL.lm1, COL.lm2, COL.lm3] : null, gradientMix: mixB });
      fx.rgb = Math.max(fx.rgb, .004); fx.displace = .006 * Math.sin(Math.PI * rk); fx.displaceScale = 2;
      fx.vignette = lerp(.45, .35, rk); fx.grain = lerp(.04, .045, rk);
    }
    // b67-68 bloom lift with the sweep
    fx.bloom += .2 * swOn;
  },
};
