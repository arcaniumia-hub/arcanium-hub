// s11-hero — HERO LOCKUP "Feel everything." (b64-70)
//
// b64.0 FINAL HIT (designed, not a white-out): the image is fully there on frame 0. A vertical light bar sweeps the frame
//   left -> right in ~5 frames (2D/3D overlay + a real strip light that grazes the materials) while the product crashes into
//   a true 3/4 pose; exposure/bloom LIFT on frames 0-1 only (no linear flash), zoom/rgb/zoomBlur back to rest in 8 frames.
//   'Hear nothing.' (60 px) leaps up out of the s10 card; 'Feel everything.' (132 px gold) blurs in letter by letter as the
//   bar crosses each letter, the whole line settling 1.08 -> 1.
// Set: warm key beam, glossy dark floor with 13 perspective hairlines (the calm sound sea), dimmed mirror reflection that
//   fades out by y 1450 so the type block (wordmark 1500 / spec 1564 / price 1638) sits on clean ink.
// Product look: stone-grey shells, taupe-grey fabric, charcoal cushions, champagne-gold metal (matched to hero.jpg/orbit sprites).
// b65 wordmark light-wipe · b66 spec line types on (real minus bar) · b66.5 price rolls in · b67-68 diagonal light sweep + glints.
// b68.5-70 THE LAST ANC RING: r 0 -> 1040 (still moving, reaching the frame corners at b70); inside -> LUMARC #0e0e14, 40 px
//   refraction band on all layers, stroke gold -> LUMARC gradient b69-69.5; leftovers outside sink to navy b69.45-69.9.
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
const REFL = { value: new THREE.Vector3(.24, 1300, 1450) };   // amount, fade start y, fade end y (screen px, top origin)
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
  float sy = ${H}.0 - gl_FragCoord.y; if (sy > 1450.) discard;
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
const Y = { hear: 262, fe: 412, wm: 1500, spec: 1564, price: 1638 };
const FE_SIZE = 132, HEAR_SIZE = 60, SPEC_SIZE = 34;
let L = null;
function layout(ctx) {
  const o = {};
  const fe = 'Feel everything.'; o.fe = fe;
  o.feSize = Math.min(FE_SIZE, FE_SIZE * 900 / measure(ctx, fe, FE_SIZE, 400, FONT.serif, 0, true));
  ctx.save(); ctx.font = font(o.feSize, 400, FONT.serif, true); ctx.letterSpacing = '0px';
  o.feW = ctx.measureText(fe).width; o.feX = [];
  for (let i = 0; i < fe.length; i++) o.feX.push(ctx.measureText(fe.slice(0, i)).width);
  ctx.restore();
  // wordmark: Unbounded 800, tracking .18em, auto-fit to max 900 px
  const wm = 'SILENCE ONE';
  const w100 = measure(ctx, wm, 100, 800, FONT.display, 18) - 18;
  o.wmSize = Math.min(64, 100 * 900 / w100);
  o.wmSp = .18 * o.wmSize;
  o.wmW = measure(ctx, wm, o.wmSize, 800, FONT.display, o.wmSp) - o.wmSp;
  o.wmX0 = 540 - o.wmW / 2;
  // spec line (mono: every glyph one advance); the minus is drawn as an explicit bar in its own cell
  o.spSp = 3; o.spAdv = measure(ctx, 'M', SPEC_SIZE, 400, FONT.mono, 0);
  o.spW = SPEC.length * (o.spAdv + o.spSp) - o.spSp; o.spX0 = 540 - o.spW / 2;
  // price
  const pr = '$349'; o.pr = pr; o.prX = []; o.prCW = [];
  ctx.save(); ctx.font = font(64, 500, FONT.display); ctx.letterSpacing = '0px';
  o.prW = ctx.measureText(pr).width;
  for (let i = 0; i < pr.length; i++) { o.prX.push(ctx.measureText(pr.slice(0, i)).width); o.prCW.push(ctx.measureText(pr[i]).width); }
  ctx.restore();
  o.prX0 = 540 - o.prW / 2;
  // sprites: 'Hear nothing.' at 120 px (the s10 card size); 'Feel everything.' per letter with one continuous gold gradient
  const PAD = 50;
  const hw = measure(ctx, 'Hear nothing.', 120, 400, FONT.serif, 0, true);
  o.hear = makeSprite(hw + PAD * 2 + 40, 120 * 1.5 + PAD * 2, (hw + PAD * 2 + 40) / 2, PAD + 120 * 1.05,
    x => text(x, 'Hear nothing.', (hw + PAD * 2 + 40) / 2, PAD + 120 * 1.05, { size: 120, family: FONT.serif, italic: true, color: COL.white }));
  const S = o.feSize, x0 = 540 - o.feW / 2; o.feS = [];
  for (let i = 0; i < fe.length; i++) {
    if (fe[i] === ' ') { o.feS.push(null); continue; }
    const lw = measure(ctx, fe[i], S, 400, FONT.serif, 0, true), w = lw + PAD * 2 + 50, h = S * 1.55 + PAD * 2, ay = PAD + S * 1.1;
    const lx = x0 + o.feX[i];
    const sp = makeSprite(w, h, PAD + 10 + lw / 2, ay, x => {
      const g = x.createLinearGradient(x0 - lx + PAD + 10, 0, x0 - lx + PAD + 10 + o.feW, 0);
      g.addColorStop(0, COL.gold2); g.addColorStop(.3, COL.goldHi); g.addColorStop(.52, COL.gold); g.addColorStop(.8, '#d9b47c'); g.addColorStop(1, COL.gold2);
      x.font = font(S, 400, FONT.serif, true); x.textAlign = 'left'; x.fillStyle = g; x.fillText(fe[i], PAD + 10, ay);
    });
    sp.x = lx + lw / 2;
    // the hit light-bar crosses this letter at frame sp.f0 (inverse of hitBarX)
    const p = clamp((sp.x + 260) / 1560, 0, .999); sp.f0 = (1 - Math.pow(1 - p, 1 / 3)) * HB_T - HB_D;
    o.feS.push(sp);
  }
  return o;
}
// b64 hit: a vertical light bar sweeps the frame left -> right (frames since the hit -> screen x)
const HB_T = 10.5, HB_D = 2.0;
const hitBarX = f => lerp(-260, 1300, eout(seg(f + HB_D, 0, HB_T)));

// ------------------------------------------------------------------ product look (stone-grey shells, champagne-gold metal, charcoal cushions)
// matched to hero.jpg / before.jpg / the orbit sprites; per-instance material clones, so this never leaks into other scenes
function productLook(hp) {
  const shell = lin('#babcbd'), fabric = new THREE.Color(.8, .88, 1.0), leather = new THREE.Color(.8, .9, 1.06);
  hp.cups.forEach(c => {
    const P = c.userData.parts;
    P.shell.material.color.copy(shell); P.shell.material.roughness = .55; P.shell.material.clearcoat = .2; P.shell.material.clearcoatRoughness = .45;
    P.cushion.material.color.copy(leather);
  });
  hp.band.sleeve.material.color.copy(fabric);
}

// ------------------------------------------------------------------ rig
let R = null;
function build(E) {
  RectAreaLightUniformsLib.init();
  const scene = new THREE.Scene();
  scene.environment = E.env; scene.environmentIntensity = .16; scene.userData._envSet = true;
  const cam = new THREE.PerspectiveCamera(FOV, W / H, .5, 700);
  const prod = new THREE.Group(); scene.add(prod);
  const hp = createHeadphone(); hp.root.position.y = -PC; prod.add(hp.root);
  const reflG = new THREE.Group(); reflG.scale.y = -1; reflG.position.y = 2 * FLOOR; scene.add(reflG);
  const reflP = new THREE.Group(); reflG.add(reflP);
  const hp2 = createHeadphone(); hp2.root.position.y = -PC; reflP.add(hp2.root);
  [hp, hp2].forEach(h => h.cups.forEach(c => ['pcb', 'battery', 'magnet', 'coil', 'driver'].forEach(k => { c.userData.parts[k].visible = false; })));
  productLook(hp); productLook(hp2);
  patchReflection(hp2.root);
  hp2.band.group.visible = false; hp2.sliders.forEach(g => { g.visible = false; });
  // dust
  const ND = 3000, dp = new Float32Array(ND * 3), dr = new Float32Array(ND);
  for (let i = 0; i < ND; i++) { dp.set([(rnd(i * 1.7 + 3) - .5) * 80, (rnd(i * 2.3 + 5) - .5) * 52 + 4, (rnd(i * 3.9 + 7) - .5) * 70], i * 3); dr[i] = rnd(i * 5.1 + 11); }
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(dp, 3)); dg.setAttribute('aR', new THREE.BufferAttribute(dr, 1));
  const dustMat = new THREE.ShaderMaterial({ vertexShader: DUST_V, fragmentShader: DUST_F, ...ADDITIVE,
    uniforms: { uT: { value: 0 }, uPx: { value: H * .5 / Math.tan(FOV / 2 * DEG) }, uSize: { value: .15 }, uAlpha: { value: 1 },
      uB0: { value: V3(42, 46, 30) }, uBd: { value: V3(-42, -46, -30).normalize() }, uCol: { value: lin('#ffe9c8').multiplyScalar(1.5) } } });
  const dust = new THREE.Points(dg, dustMat); dust.frustumCulled = false; scene.add(dust);
  // lights: neutral-warm key (keeps the shells stone-grey), warmth lives in the gold rims
  const key = new THREE.DirectionalLight(0xffe9c8, 1.1); key.position.set(40, 34, 30); scene.add(key);
  const spot = new THREE.SpotLight(0xfff2e2, 9000, 0, 16 * DEG, 1, 2); spot.position.set(46, 60, 34); spot.target.position.set(-3, -2, 0); scene.add(spot); scene.add(spot.target);
  const rim = new THREE.DirectionalLight(0xe6c896, 3.4); rim.position.set(-34, 14, -26); scene.add(rim);
  const rim2 = new THREE.DirectionalLight(0xfff0d8, 1.6); rim2.position.set(30, 22, -34); scene.add(rim2);
  const fill = new THREE.DirectionalLight(0xdfe4ee, .35); fill.position.set(-30, 4, 40); scene.add(fill);
  const sweep = new THREE.RectAreaLight(0xfff0dc, 0, 1.1, 60); scene.add(sweep);
  // overlay scene (pixel space: x right, y DOWN as negative world y)
  const ov = new THREE.Scene(); ov.userData.autoEnv = false;
  const ovCam = new THREE.OrthographicCamera(0, W, 0, -H, -10, 10);
  const band = ovMesh(BAND_F, '#fff4e4', 220 * 1.7, 3400); ov.add(band);
  const bar = ovMesh(BAND_F, '#fff1dc', 240, 3400); ov.add(bar);
  const stars = [0, 1].map(() => { const m = ovMesh(STAR_F, '#fff2d8', 300, 300); ov.add(m); return m; });
  const flare = ovMesh(FLARE_F, '#ffd9a8', 2600, 120); ov.add(flare);
  // offscreen target + lens pass for the ANC ring
  const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
  const lensMat = new THREE.ShaderMaterial({ vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`,
    fragmentShader: LENS_F, blending: THREE.NoBlending, depthTest: false, depthWrite: false,
    uniforms: { tSrc: { value: rt.texture }, uC: { value: new THREE.Vector2(...RING_C) }, uR: { value: 0 }, uBand: { value: 40 }, uScale: { value: 1.04 } } });
  const lensScene = new THREE.Scene(); lensScene.userData.autoEnv = false;
  const lq = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), lensMat); lq.frustumCulled = false; lensScene.add(lq);
  return { spot, scene, cam, prod, hp, hp2, reflP, dust, dustMat, key, rim, rim2, fill, sweep, ov, ovCam, band, bar, stars, flare, rt, lensMat, lensScene };
}

const tmpV = new THREE.Vector3();
function project(cam, p) { tmpV.copy(p).project(cam); return [(tmpV.x + 1) / 2 * W, (1 - tmpV.y) / 2 * H]; }
function place(mesh, x, y, sx = 1, sy = 1, rot = 0) { mesh.position.set(x, -y, 0); mesh.scale.set(sx, sy, 1); mesh.rotation.z = -rot; }
// put the strip light on the camera ray through screen point (sx,sy), rolled by `roll`
function aimSweep(cam, dist, sx, sy, roll) {
  const ndc = V3(sx / W * 2 - 1, -(sy / H * 2 - 1), .5).unproject(cam);
  const dir = ndc.sub(cam.position).normalize();
  R.sweep.position.copy(cam.position).addScaledVector(dir, dist * .45);
  R.sweep.lookAt(0, 0, 0); R.sweep.rotateZ(-roll);
}

// sweep: band centre as a signed distance (px) along the normal n = (cos25, sin25) from RING_C
const SW_A = 25 * DEG, SW_N = [Math.cos(SW_A), Math.sin(SW_A)];
const sdist = (x, y) => (x - RING_C[0]) * SW_N[0] + (y - RING_C[1]) * SW_N[1];
// the last ANC ring: still travelling when it reaches the frame corners at b70 (r 1040) - s12 bounces it back from there
const RING_END = 1040;
const ringRadius = b => b < 68.5 ? 0 : RING_END * Math.pow(seg(b, 68.5, 70), 1.2);

// ------------------------------------------------------------------ the calm sound sea, rebuilt as a glossy dark floor + 13 perspective hairlines
function floor(ctx, cam, t, hz) {
  // glossy floor: faint warm sheen from the horizon fading to ink before the type block
  { const g = ctx.createLinearGradient(0, hz, 0, 1450);
    g.addColorStop(0, 'rgba(236,214,176,.045)'); g.addColorStop(.25, 'rgba(236,214,176,.02)'); g.addColorStop(1, 'rgba(236,214,176,0)');
    ctx.fillStyle = g; ctx.fillRect(0, hz, W, 1450 - hz); }
  // hairlines at constant world spacing on the floor plane (projected): they drift toward the camera very slowly
  const cx = cam.position.x, cz = cam.position.z, ln = Math.hypot(cx, cz), fx = -cx / ln, fz = -cz / ln;
  const ph = (t * .22) % 1;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = -1; i < 14; i++) {
    const d = 46 * Math.pow(1.3, i + 1 - ph);
    const y = project(cam, V3(cx + fx * d, FLOOR, cz + fz * d))[1];
    if (y > 1452 || y < hz + 2) continue;
    const a = .19 * seg(y - hz, 4, 70) * (1 - seg(y, 1290, 1450)) * (.8 + .2 * Math.sin(i * 1.7 - t * 1.6));
    if (a < .004) continue;
    const g = ctx.createLinearGradient(0, 0, W, 0);
    g.addColorStop(0, 'rgba(154,151,143,0)'); g.addColorStop(.2, `rgba(170,164,152,${a * .7})`);
    g.addColorStop(.5, `rgba(240,214,166,${a * 1.25})`);
    g.addColorStop(.8, `rgba(170,164,152,${a * .7})`); g.addColorStop(1, 'rgba(154,151,143,0)');
    ctx.fillStyle = g; ctx.fillRect(0, Math.round(y), W, y > 1100 ? 2 : 1);
  }
  ctx.restore();
  // horizon line + haze, glint path under the reflection
  glow(ctx, 540, hz, 1000, 120, .07, '230,200,150');
  { const g = ctx.createLinearGradient(0, 0, W, 0); g.addColorStop(0, 'rgba(230,200,150,0)'); g.addColorStop(.5, 'rgba(240,215,170,.13)'); g.addColorStop(1, 'rgba(230,200,150,0)');
    ctx.fillStyle = g; ctx.fillRect(0, hz - 1, W, 2); }
  glow(ctx, 540, 1350, 90, 150, .07 * (.85 + .15 * Math.sin(t * 2.3)), '235,205,155');
}

export default {
  id: 's11-hero', start: 64, end: 70,
  cutIn: 'none',
  init(E) { R = build(E); },
  draw(E, lt, t) {
    const b = B0 + lt / BEAT + 1e-6, f = lt * 30, fx = E.fx, bg = E.bg, fg = E.fg, fi = Math.round(f);
    if (!L) L = layout(fg);
    const { scene, cam, prod, hp, reflP, dustMat } = R;

    // ---------------- post: base hero grade
    fx.exposure = .9; fx.bloom = .62; fx.bloomThreshold = .8; fx.vignette = .45; fx.grain = .04; fx.sat = 1.0; fx.rgb = .0015;
    // b64 HIT, designed: the image is fully there on frame 0. Light LIFT (exposure + bloom), not a white-out; a light bar sweeps
    // the frame left -> right and reveals the product; zoom / fringe / blur punch back to rest within 8 frames.
    if (f < 10) {
      const lift = [.38, .14, .04][fi] || 0;
      fx.exposure += lift; fx.bloom = lerp(fx.bloom, .95, clamp(lift / .38)); fx.bloomThreshold = lerp(.8, .7, clamp(lift / .38));
      fx.flash = [0, .02][fi] || 0; fx.flashColor = [1, .93, .8];
      fx.zoom = 1 + .085 * (1 - expoOut(clamp(f / 8)));
      fx.rgb = .0015 + .016 * Math.max(0, 1 - f / 7);
      fx.zoomBlur = .16 * Math.max(0, 1 - f / 4);
      const sh = .007 * Math.max(0, 1 - f / 8);
      fx.shake = [(rnd(fi + 911) - .5) * 2 * sh, (rnd(fi + 977) - .5) * 2 * sh];
    }
    // half-time kicks: tiny pump
    for (const k of [65.5, 66, 67.5]) { const fr = (b - k) * 12; if (fr >= 0 && fr < 4) fx.zoom *= 1 + .012 * (1 - fr / 4); }

    // ---------------- product pose: crash-in settle + a real 3/4 turn (48 -> 28 deg off front) + float
    const land = expoOut(seg(f, 0, 14));
    const ang = (lerp(58, 38, eio(seg(b, 64, 70)) * .7 + seg(b, 64, 70) * .3) + 12 * (1 - land)) * DEG;
    prod.rotation.set(-3 * DEG * (1 - land), CAM.az - ang, 2.5 * DEG * (1 - land));
    prod.position.y = .1 * Math.sin(lt * 2.3) + 1.6 * (1 - land);
    prod.scale.setScalar(1 + .07 * (1 - land));
    reflP.position.copy(prod.position); reflP.rotation.copy(prod.rotation); reflP.scale.copy(prod.scale);

    // ---------------- camera: slow push-in + crane up, slight orbit drift
    const kc = eio(seg(b, 64, 70));
    const dist = lerp(88, 81, kc), az = CAM.az + 1.5 * DEG * Math.sin(lt * .6) - 2 * DEG * kc, el = lerp(2.4, 4.6, kc) * DEG;
    cam.position.set(Math.sin(az) * Math.cos(el) * dist, Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
    cam.lookAt(0, -1, 0);
    cam.setViewOffset(W, H, 0, 92, W, H);
    cam.updateMatrixWorld();

    // ---------------- lights
    const kicks = [65.5, 66, 67.5].map(k => b >= k ? Math.exp(-(b - k) * BEAT / .16) : 0);
    const kick = Math.max(...kicks) * .5;
    const hit = Math.exp(-f / 5);
    R.key.intensity = 1.1 * (1 + .5 * hit); R.spot.intensity = 9000 * (1 + .4 * hit + .15 * kick); R.rim.intensity = 3.4 * (1 + .8 * hit); R.rim2.intensity = 1.6;
    prod.updateMatrixWorld(true);
    const slL = project(cam, hp.sliders[0].localToWorld(V3(0, .4, 0))), slR = project(cam, hp.sliders[1].localToWorld(V3(0, .4, 0)));
    const dL = sdist(...slL), dR = sdist(...slR);
    const sPos = b < 67.5 ? lerp(-900, dL, eio(seg(b, 66.85, 67.5)) * .25 + seg(b, 66.85, 67.5) * .75) : b < 68 ? lerp(dL, dR, seg(b, 67.5, 68)) : lerp(dR, 1100, ein(seg(b, 68, 68.6)) * .4 + seg(b, 68, 68.6) * .6);
    const swOn = seg(b, 66.85, 67.05) * (1 - seg(b, 68.35, 68.6));
    const hbx = hitBarX(f), hbOn = f < 12 ? 1 - seg(f, 6, 11) : 0;
    // one strip light serves both sweeps (always in the scene: no shader recompiles mid-scene)
    if (hbOn > 0) { aimSweep(cam, dist, hbx, 900, 0); R.sweep.intensity = 85 * hbOn; }
    else if (swOn > 0) { aimSweep(cam, dist, RING_C[0] + SW_N[0] * sPos, RING_C[1] + SW_N[1] * sPos, SW_A); R.sweep.intensity = 70 * swOn; }
    else R.sweep.intensity = 0;

    // ---------------- bg: ink, warm key beam from top-right, glossy floor
    bg.fillStyle = COL.ink; bg.fillRect(0, 0, W, H);
    beam(bg, 1180, -200, 560, 930, .19, .5 * (1 + .4 * hit + .15 * kick), '255,232,196');
    const hz = project(cam, V3(-Math.sin(az) * 3000, FLOOR, -Math.cos(az) * 3000))[1];
    floor(bg, cam, t, hz);
    glow(bg, 760, 380, 520, 520, .05 * (1 + hit), '255,232,196');

    // ---------------- 3D
    dustMat.uniforms.uT.value = t + 3; dustMat.uniforms.uAlpha.value = 1 + .4 * kick;
    {
      const bx = RING_C[0] + SW_N[0] * sPos, by = RING_C[1] + SW_N[1] * sPos;
      R.band.visible = swOn > .01; place(R.band, bx, by, 1, 1, SW_A); R.band.material.uniforms.uI.value = .085 * swOn;
      R.bar.visible = hbOn > .01; place(R.bar, hbx, 960, 1, 1, 0); R.bar.material.uniforms.uI.value = .3 * hbOn;
      [[67.5, slL], [68.0, slR]].forEach(([at, p], i) => {
        const g = (b - at) * 12, m = R.stars[i];
        const k = g < 0 ? 0 : g < 1.5 ? expoOut(g / 1.5) : Math.exp(-(g - 1.5) / 3.2);
        m.visible = k > .01; place(m, p[0], p[1], .4 + .8 * k, .4 + .8 * k, 12 * DEG + g * 2.5 * DEG);
        m.material.uniforms.uI.value = 3.2 * k;
      });
      // anamorphic kiss off the right cup's gold ring as the bar passes it
      const rp = project(cam, hp.cups[1].localToWorld(V3(0, -.2, 4.4)));
      const fk = Math.exp(-Math.pow((hbx - rp[0]) / 160, 2)) * hbOn;
      R.flare.visible = fk > .01; place(R.flare, rp[0], rp[1], .8 + .4 * fk, 1, 0); R.flare.material.uniforms.uI.value = .9 * fk;
    }
    const ringR = ringRadius(b), rk = seg(b, 68.5, 70);
    if (ringR > 0) {
      const r = E.renderer;
      r.setRenderTarget(R.rt); r.setClearColor(0x000000, 0); r.clear(true, true, true); r.render(scene, cam); r.clearDepth(); r.render(R.ov, R.ovCam);
      R.lensMat.uniforms.uR.value = ringR; R.lensMat.uniforms.uBand.value = 40;
      E.render3D(R.lensScene, R.ovCam);
    } else { E.render3D(scene, cam); E.render3D(R.ov, R.ovCam); }

    // ---------------- fg typography
    // 'Hear nothing.' leaps out of the s10 card (540,990,120 px) to its line above the payoff (60 px) - already mid-leap on frame 0
    {
      const F0 = -2.6, D = 6;
      const kf = q => expoOut(seg(q - F0, 0, D));
      if (f >= D + F0) text(fg, 'Hear nothing.', 540, Y.hear, { size: HEAR_SIZE, family: FONT.serif, italic: true, color: COL.white });
      else {
        const v = kf(f + .5) - kf(f - .5);
        for (let i = 6; i >= 1; i--) {
          const kk = kf(f - i * .25);
          drawSprite(fg, L.hear, 540, lerp(990, Y.hear, kk), lerp(120, HEAR_SIZE, kk) / 120, 3 + i * 2.2, .22 * (1 - i / 7) * clamp(v * 5));
        }
        const k = kf(f);
        drawSprite(fg, L.hear, 540, lerp(990, Y.hear, k), lerp(120, HEAR_SIZE, k) / 120, v * 18, 1);
      }
    }
    // 'Feel everything.' 132 px gold: each letter blurs in as the hit light-bar crosses it; the whole line settles 1.08 -> 1
    {
      const gs = 1 + .08 * (1 - expoOut(seg(f, 0, 12))), cy = Y.fe - L.feSize * .32;
      const settled = f >= 16;
      fg.save();
      if (!settled) { fg.translate(540, cy); fg.scale(gs, gs); fg.translate(-540, -cy); }
      for (let i = 0; i < L.fe.length; i++) {
        const sp = L.feS[i]; if (!sp) continue;
        const k = seg(f, sp.f0 - .6, sp.f0 + 5); if (k <= 0) continue;
        const e = expoOut(k);
        if (settled) { fg.drawImage(sp.lv[0], Math.round(sp.x - sp.ax), Math.round(Y.fe - sp.ay)); continue; }
        drawSprite(fg, sp, sp.x, Y.fe - (1 - e) * 14, lerp(1.25, 1, e), (1 - e) * 20, Math.min(1, e * 1.3));
      }
      fg.restore();
    }
    // wordmark: light-wipe from the centre outward over 1 beat (b65-66), tracking settles
    if (b >= 65) {
      const k = seg(b, 65, 66), e = eio(k) * .4 + expoOut(k) * .6, half = (L.wmW / 2 + 40) * e;
      const sp = lerp(L.wmSp * 1.9, L.wmSp, expoOut(k)), shift = (sp - L.wmSp) * 5;
      const x0 = L.wmX0 - shift, y = Y.wm;
      fg.save(); fg.beginPath(); fg.rect(540 - half, y - 90, half * 2, 130); fg.clip();
      text(fg, 'SILENCE', x0, y, { size: L.wmSize, weight: 800, family: FONT.display, color: COL.white, align: 'left', spacing: sp });
      const xa = x0 + measure(fg, 'SILENCE ', L.wmSize, 800, FONT.display, sp);
      const ow = measure(fg, 'ONE', L.wmSize, 800, FONT.display, sp) - sp;
      fg.save(); fg.font = font(L.wmSize, 800, FONT.display); fg.letterSpacing = sp + 'px'; fg.textAlign = 'left';
      fg.fillStyle = goldGrad(fg, xa, xa + ow, .1 * Math.sin(lt * 1.3)); fg.fillText('ONE', xa, y); fg.restore();
      fg.restore();
      if (k > 0 && k < 1) {
        const a = .9 * (1 - seg(k, .35, .8));
        [540 - half, 540 + half].forEach(xe => {
          const g = fg.createLinearGradient(0, y - 95, 0, y + 45); g.addColorStop(0, 'rgba(255,236,200,0)'); g.addColorStop(.5, `rgba(255,236,200,${a})`); g.addColorStop(1, 'rgba(255,236,200,0)');
          fg.fillStyle = g; fg.fillRect(xe - 1, y - 95, 2, 140);
          glow(fg, xe, y - 24, 16, 70, .35 * a, '255,226,176');
        });
      }
    }
    // spec line types on (2 chars / frame) from b66.0 with a gold cursor; the minus is a real bar (U+2212 reads as a hyphen in mono)
    if (b >= 66) {
      const fs = (b - 66) * 12, n = Math.min(SPEC.length, Math.floor(fs * 2) + 1);
      const s = SPEC.slice(0, n), adv = L.spAdv + L.spSp;
      text(fg, s.replace(MINUS, ' '), L.spX0, Y.spec, { size: SPEC_SIZE, weight: 400, family: FONT.mono, color: '#d6d1c6', align: 'left', spacing: L.spSp });
      const mi = SPEC.indexOf(MINUS);
      if (mi >= 0 && mi < n) { fg.fillStyle = '#d6d1c6'; fg.fillRect(L.spX0 + mi * adv + L.spAdv * .08, Y.spec - SPEC_SIZE * .33, L.spAdv * .84, Math.max(2.5, SPEC_SIZE * .075)); }
      const done = fs * 2 >= SPEC.length;
      const ca = done ? (1 - seg(fs, SPEC.length / 2 + 4, SPEC.length / 2 + 7)) * (Math.floor(fs / 3) % 2 ? .25 : 1) : 1;
      if (ca > .01) { fg.save(); fg.globalAlpha = ca; fg.fillStyle = COL.gold; fg.fillRect(L.spX0 + n * adv + 2, Y.spec - SPEC_SIZE * .8, SPEC_SIZE * .5, SPEC_SIZE); fg.restore(); }
    }
    // price rises in (y +20 -> 0, 6 frames) with fast rolling digits $000 -> $349
    if (b >= 66.5) {
      const fp = (b - 66.5) * 12, e = eout(seg(fp, 0, 6)), y = Y.price + 20 * (1 - e), size = 64;
      fg.save(); fg.globalAlpha = e;
      text(fg, '$', L.prX0, y, { size, weight: 500, family: FONT.display, color: COL.white, align: 'left' });
      fg.beginPath(); fg.rect(L.prX0 + L.prX[1] - 6, y - size * .86, L.prW, size * .96); fg.clip();
      const step = size * 1.05;
      for (let i = 1; i < 4; i++) {
        const tgt = +L.pr[i], cyc = 10, dur = 5 + 1.5 * i;
        const p = (tgt + cyc) * expoOut(seg(fp, 0, dur));
        const cx = L.prX0 + L.prX[i] + L.prCW[i] / 2, base = Math.floor(p), fr = p - base;
        for (let j = -1; j <= 1; j++) {
          const d = ((base + j) % 10 + 10) % 10, yy = y + (j - fr) * -step;
          text(fg, String(d), cx, yy, { size, weight: 500, family: FONT.display, color: COL.white, align: 'center' });
        }
      }
      fg.restore();
    }
    // type shine as the b67 sweep passes (only over the letters)
    if (swOn > .01) {
      const bx = RING_C[0] + SW_N[0] * sPos, by = RING_C[1] + SW_N[1] * sPos;
      fg.save(); fg.globalCompositeOperation = 'source-atop'; fg.translate(bx, by); fg.rotate(SW_A);
      const g = fg.createLinearGradient(-130, 0, 130, 0);
      g.addColorStop(0, 'rgba(255,244,220,0)'); g.addColorStop(.5, `rgba(255,248,232,${.85 * swOn})`); g.addColorStop(1, 'rgba(255,244,220,0)');
      fg.fillStyle = g; fg.fillRect(-130, -2000, 260, 4000); fg.restore();
    }
    // the hit reveal: ahead of the light bar the frame is still held down (soft edge), behind it the lockup is fully lit
    if (hbOn > .01 && f < 8) {
      const a = .42 * (1 - seg(f, 3, 7));
      const g = fg.createLinearGradient(hbx - 40, 0, hbx + 220, 0);
      g.addColorStop(0, 'rgba(5,5,6,0)'); g.addColorStop(1, `rgba(5,5,6,${a})`);
      fg.fillStyle = g; fg.fillRect(hbx - 40, 0, W - hbx + 40, H);
    }

    // ---------------- THE LAST ANC RING (b68.5-70): erases the lockup into LUMARC navy and parks on the frame corners
    if (ringR > 0) {
      const [cx, cy] = RING_C;
      refractLayer(bg, cx, cy, ringR, 40, 1.04, false);
      refractLayer(fg, cx, cy, ringR, 40, 1.04, true);
      fg.save(); fg.fillStyle = COL.lmBg; fg.beginPath(); fg.arc(cx, cy, ringR, 0, TAU); fg.fill();
      // what is still outside the ring sinks into navy as the ring reaches the corners
      const out = eio(seg(b, 69.45, 69.9));
      if (out > 0) { fg.globalAlpha = out; fg.beginPath(); fg.rect(0, 0, W, H); fg.arc(cx, cy, ringR, 0, TAU, true); fg.fill('evenodd'); fg.globalAlpha = 1; }
      const mixB = eio(seg(b, 69, 69.5));
      const wake = fg.createRadialGradient(cx, cy, Math.max(0, ringR - 340), cx, cy, ringR);
      const wc = [lerp(230, 106, mixB), lerp(200, 85, mixB), lerp(150, 255, mixB)].map(Math.round).join(',');
      wake.addColorStop(0, `rgba(${wc},0)`); wake.addColorStop(.7, `rgba(${wc},${.03 + .03 * mixB})`); wake.addColorStop(1, `rgba(${wc},${.16 + .1 * mixB})`);
      fg.fillStyle = wake; fg.beginPath(); fg.arc(cx, cy, ringR, 0, TAU); fg.fill();
      fg.restore();
      ancRing(fg, cx, cy, ringR, { refract: false, gradient: mixB > 0 ? [COL.lm1, COL.lm2, COL.lm3] : null, gradientMix: mixB });
      fx.rgb = Math.max(fx.rgb, .003); fx.displace = .006 * Math.sin(Math.PI * clamp(rk * 1.6)); fx.displaceScale = 2;
      fx.vignette = lerp(.45, .3, rk); fx.grain = lerp(.04, .045, rk); fx.bloom = lerp(fx.bloom, .8, rk);
    }
    fx.bloom += .2 * swOn;
  },
};
