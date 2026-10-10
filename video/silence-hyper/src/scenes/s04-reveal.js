// s04-reveal — REVEAL: light floods the ring's framing, the camera rockets back to the whole product floating over a
// violent SOUND SEA, the gold ANC ring expands on the sea and flattens it; two macro cut-ins (gold slider light-sweep,
// woven headband skim) and a whip pan into the grid (b20-24).
//
// Layers: bg2d ink + warm volumetric beam · 3D one scene (product, sea line-terrain, ring plane, dust/bokeh) lit per shot;
//         macros B/C go through a local depth-of-field pass · fg2d 'Introducing' / 'SILENCE ONE', part labels, whip streaks.
// First frame == s03's last frame: CUP_CAM framing, the same emissive ring tube (radius .12, intensity ~6.8), s03's post levels.
// Product look (shared film preset, relit but never recoloured here): stone-grey shell #8e8b85 r.5, champagne-gold metal
// r.22 brushed/anisotropic, charcoal cushions, neutral warm-grey woven band.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, rnd, text, font, measure, ADDITIVE, COL, FONT } from '../lib.js';
import { createHeadphone } from '../model.js';
// s03's exported hand-off (copied verbatim so this scene builds on its own): right ear cup seen straight onto its face
const CUP_RING = { center: [7.2, -4.5, 0], ay: 3.99 * 1.2, az: 3.99 };
const CUP_CAM = { fov: 30, position: [7.2 + 44.67, -4.5, 0], target: [7.2, -4.5, 0], up: [0, 1, 0], near: .5, far: 400 };

const DEG = Math.PI / 180;
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const GOLD = lin(COL.gold);
const SEA_Y = -13.2;                 // calm water level (world)
// shot boundaries in frames since b20.0
const QB = 24, QC = 36, QW = 42, QE = 48;
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };

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
  const ROUGH = lin('#9a978f').lerp(lin('#8e989f'), .35), CALM = lin('#a99f8c');
  // world-space (x,z) of each vertex is needed for the ring distance: the mesh is rotated about Y by `rotY`.
  // cam = camera position in the sea's local frame (for the distance fog to ink)
  function update(t, R, rotY, alpha, cam) {
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
        // exponential fog to ink with camera distance (the gold crest is exempt: it stays the one bright line)
        const dc = Math.hypot(xl - cam.x, y - cam.y, zl - cam.z);
        const fog = Math.exp(-Math.max(0, dc - 40) / 34);
        const side = 1 - seg(Math.abs(xl), width * .36, width * .5);
        const a = alpha * farFade * side;
        const crest = clamp(.55 + .45 * h / A);
        const glint = (1 - cs2) * Math.exp(-xl * xl / 9) * (.35 + .65 * Math.max(0, vn(xl * .9 + t * 2.5, zl * .45 - t * 1.5))) * seg(zl, z0 + 6, -4) * (1 - seg(zl, 4, 12));
        // calmed water: 15 % lines + a faint shimmer path -> reads as dark, still water
        const rough = (.45 + 3.6 * crest * crest) * cs2 * fog, calmK = ((1 - cs2) * .15 + glint * .55) * fog;
        const g = 3 * Math.exp(-Math.pow((d - R) / 1.5, 2)) * (R > .01 ? 1 : 0) * (.35 + .65 * Math.sqrt(fog));
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
  float sheen = smoothstep(uR, uR*.2, d)*.006*step(.01, uR);
  vec3 l = uInv*vW; float box = smoothstep(uBox.x, uBox.x+26., l.z)*(1.-smoothstep(uBox.y-10., uBox.y, l.z))*(1.-smoothstep(uBox.z*.36, uBox.z*.5, abs(l.x)));
  float birth = uBirth*exp(-d*d/6.);
  vec3 c = uCol*(core*2.6 + halo + wide + sheen + birth*3.)*uI*box;
  gl_FragColor = vec4(c, 1.);
}`;

// ------------------------------------------------------------------ s03's emissive ring tube (identical shader), fades out
const TUBE_V = `varying vec3 vN; varying vec3 vV;
void main(){ vN = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); vV = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }`;
const TUBE_F = `uniform float uInt; uniform vec3 uCol; varying vec3 vN; varying vec3 vV;
void main(){ float fres = .55 + .45*abs(dot(normalize(vN), normalize(vV))); gl_FragColor = vec4(uCol*uInt*fres, 1.); }`;

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

// ------------------------------------------------------------------ product look: textures (built once)
function cnv(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function toTex(c, repeat, srgb = true, aniso = 4) {
  const t = new THREE.CanvasTexture(c); t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; t.anisotropy = aniso;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; if (repeat) t.repeat.set(...repeat); return t;
}
// stone: fine mineral grain + soft mottling (bump only, mean 0.5)
function stoneGrain() {
  const N = 512, c = cnv(N, N), x = c.getContext('2d'), im = x.createImageData(N, N);
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const v = .5 + .22 * (hash2(i, j) - .5) + .18 * (hash2(i >> 1, (j >> 1) + 900) - .5) + .12 * vn(i / 23, j / 23) + .06 * vn(i / 7 + 40, j / 7);
    const k = (j * N + i) * 4, b = Math.round(clamp(v) * 255); im.data[k] = im.data[k + 1] = im.data[k + 2] = b; im.data[k + 3] = 255;
  }
  x.putImageData(im, 0, 0); return toTex(c, [3, 3], false);
}
// brushed metal: fine streaks along u
function brushed() {
  const c = cnv(1024, 128), x = c.getContext('2d'); x.fillStyle = '#808080'; x.fillRect(0, 0, 1024, 128);
  for (let i = 0; i < 900; i++) {
    const y = rnd(i * 3.7) * 128, v = Math.round(128 + (rnd(i * 5.3) - .5) * 90), l = 120 + rnd(i * 1.9) * 900;
    x.fillStyle = `rgba(${v},${v},${v},.55)`; x.fillRect(rnd(i * 7.1) * 1024 - 100, y, l, .6 + rnd(i * 2.2) * .9);
  }
  return toTex(c, [6, 1], false);
}
// fine, irregular woven fabric (warm stone grey). One tile = 128 x 128 thread cells with per-thread colour/width jitter + slubs.
function knit() {
  const N = 1024, S = 8, c = cnv(N, N), x = c.getContext('2d');
  x.fillStyle = '#5d5952'; x.fillRect(0, 0, N, N);
  const rowV = j => 128 + 22 * (rnd(j * 3.13 + 1) - .5) + 10 * vn(j / 9, 3.3);
  const colV = i => 126 + 22 * (rnd(i * 7.77 + 2) - .5) + 10 * vn(7.7, i / 11);
  for (let j = 0; j < N / S; j++) for (let i = 0; i < N / S; i++) {
    const over = ((i + 2 * j) % 4) < 2;            // 2/2 twill
    const v = (over ? colV(i) : rowV(j)) + 14 * (rnd(i * 13.1 + j * 7.3) - .5);
    const x0 = i * S, y0 = j * S, ins = .6 + .7 * rnd(i * 1.3 + j * 9.1);
    const g = over ? x.createLinearGradient(x0, 0, x0 + S, 0) : x.createLinearGradient(0, y0, 0, y0 + S);
    const r = Math.round(v + 6), gg = Math.round(v + 2), b = Math.round(v - 5);
    g.addColorStop(0, `rgb(${r - 46},${gg - 46},${b - 46})`); g.addColorStop(.5, `rgb(${r + 14},${gg + 14},${b + 12})`); g.addColorStop(1, `rgb(${r - 46},${gg - 46},${b - 46})`);
    x.fillStyle = g;
    if (over) x.fillRect(x0 + ins, y0, S - 2 * ins, S); else x.fillRect(x0, y0 + ins, S, S - 2 * ins);
  }
  // slubs + stray fibres
  for (let i = 0; i < 2600; i++) {
    const px = rnd(i * 2.71) * N, py = rnd(i * 6.13) * N, a = rnd(i * 4.4) < .5 ? 0 : Math.PI / 2, l = 6 + rnd(i * 8.8) * 22;
    x.strokeStyle = rnd(i * 1.1) < .5 ? 'rgba(235,228,214,.16)' : 'rgba(20,18,16,.18)'; x.lineWidth = .7 + rnd(i * 3.9);
    x.beginPath(); x.moveTo(px, py); x.lineTo(px + Math.cos(a) * l, py + Math.sin(a) * l); x.stroke();
  }
  return c;
}

let LOOKM = null;
function lookMaterials() {
  if (LOOKM) return LOOKM;
  const grain = stoneGrain(), brush = brushed(), kc = knit();
  const knitMap = toTex(kc, [18, 5]), knitBump = toTex(kc, [18, 5], false);
  const shell = new THREE.MeshPhysicalMaterial({ color: '#8e8b85', roughness: .5, metalness: .02, clearcoat: .12, clearcoatRoughness: .5,
    bumpMap: grain, bumpScale: .35, side: THREE.DoubleSide });
  const gold = new THREE.MeshPhysicalMaterial({ color: '#dcbf93', metalness: 1, roughness: .22, anisotropy: .55, bumpMap: brush, bumpScale: .12 });
  const leather = new THREE.MeshStandardMaterial({ color: '#2a2a2c', roughness: .62, bumpMap: grain, bumpScale: .9 });
  const fabric = new THREE.MeshStandardMaterial({ map: knitMap, bumpMap: knitBump, bumpScale: .5, roughness: .93, color: new THREE.Color(1.0, .99, .97) });
  const knitC = toTex(kc, [18, 5], true, 4), knitCB = toTex(kc, [18, 5], false, 4);
  const fabricMacro = new THREE.MeshStandardMaterial({ map: knitC, bumpMap: knitCB, bumpScale: 1.2, roughness: .9, color: new THREE.Color(1.0, .99, .97) });
  LOOKM = { shell, gold, leather, fabric, fabricMacro };
  return LOOKM;
}

// ------------------------------------------------------------------ studio strip-light reflection (narrow specular band)
// A long softbox in reflection space: directions r with |dot(r, N)| < w (a great circle) inside the hemisphere around F.
const STRIP = { uStripN: { value: new THREE.Vector3(1, 0, 0) }, uStripF: { value: new THREE.Vector3(0, 0, 1) },
  uStripW: { value: .05 }, uStripI: { value: 0 }, uStripCol: { value: new THREE.Color(1, .93, .82) } };
function addStrip(mat, gain, key) {
  const uG = { value: gain };
  mat.customProgramCacheKey = () => 's04strip-' + key;
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, STRIP, { uStripG: uG });
    sh.fragmentShader = sh.fragmentShader
      .replace('void main() {', 'uniform vec3 uStripN, uStripF, uStripCol; uniform float uStripW, uStripI, uStripG;\nvoid main() {')
      .replace('#include <opaque_fragment>', `{
        vec3 s4v = normalize(vViewPosition);
        vec3 s4r = inverseTransformDirection(reflect(-s4v, normal), viewMatrix);
        float s4w = uStripW + roughnessFactor*roughnessFactor*.5;
        float s4 = exp(-pow(dot(s4r, uStripN)/s4w, 2.))*(uStripW/s4w)*smoothstep(-.35, .35, dot(s4r, uStripF));
        vec3 s4spec = mix(vec3(.04), diffuseColor.rgb, metalnessFactor);
        outgoingLight += uStripCol*uStripI*uStripG*s4*s4spec;
      }
      #include <opaque_fragment>`);
  };
  mat.needsUpdate = true;
}
// orient the strip from the camera: a vertical softbox at horizontal angle a (0 = behind the camera)
function aimStrip(cam, a, w, I) {
  const m = cam.matrixWorld, rt = new THREE.Vector3().setFromMatrixColumn(m, 0), bk = new THREE.Vector3().setFromMatrixColumn(m, 2);
  STRIP.uStripN.value.copy(rt).multiplyScalar(Math.cos(a)).addScaledVector(bk, -Math.sin(a)).normalize();
  STRIP.uStripF.value.copy(bk).multiplyScalar(Math.cos(a)).addScaledVector(rt, Math.sin(a)).normalize();
  STRIP.uStripW.value = w; STRIP.uStripI.value = I;
}

// ------------------------------------------------------------------ local depth of field for the macros
// Quarter-resolution gather DOF, noise-free: (1) the sharp frame is rendered at full res (MSAA + depth texture);
// (2) PREP: a 4x4 box-prefiltered quarter-res colour, and a quarter-res map of (signed CoC, view z) taken from the nearest of 4 depths in the block;
// (3) DIL: the near-field CoC is spread over the pixels it can reach (so a blurred foreground has a soft edge over sharp detail);
// (4) GATHER: 24 fixed golden-spiral taps (no per-pixel random rotation -> no grit), scatter-as-gather weights;
// (5) COMP: full-res mix of the sharp frame and the bilinear-upsampled blur by max(own CoC, near reach).
const QV = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`;
const DOF_COMMON = `uniform sampler2D tCol, tDep, tHalf, tK, tK2, tBlur; uniform float uNear, uFar, uFocus, uAp, uMaxR; uniform vec2 uPx; varying vec2 vUv;
float vz(vec2 uv){ float d = texture2D(tDep, uv).x; float z = d*2. - 1.; return 2.*uNear*uFar/(uFar + uNear - z*(uFar - uNear)); }
float coc(float z){ return clamp(uAp*(1. - uFocus/z), -uMaxR, uMaxR); }`;   // signed: < 0 in front of the focus plane
const DOF_PREPC = `${DOF_COMMON}
void main(){ vec2 o = uPx; gl_FragColor = .25*(texture2D(tCol, vUv + vec2(-o.x, -o.y)) + texture2D(tCol, vUv + vec2(o.x, -o.y)) + texture2D(tCol, vUv + vec2(-o.x, o.y)) + texture2D(tCol, vUv + vec2(o.x, o.y))); }`;
const DOF_PREPK = `${DOF_COMMON}
void main(){ vec2 o = uPx*1.5;
  float z = min(min(vz(vUv + vec2(-o.x, -o.y)), vz(vUv + vec2(o.x, -o.y))), min(vz(vUv + vec2(-o.x, o.y)), vz(vUv + vec2(o.x, o.y))));
  gl_FragColor = vec4(coc(z), z, 0., 1.); }`;
const DOF_DIL = `${DOF_COMMON}
void main(){
  vec4 k = texture2D(tK, vUv); float reach = max(0., -k.x);
  for (int i = 0; i < 8; i++) {
    float fi = float(i) + .5; float r = sqrt(fi/8.)*uMaxR; float a = fi*2.39996;
    float c = -texture2D(tK, vUv + vec2(cos(a), sin(a))*r*uPx).x;
    reach = max(reach, c*smoothstep(r - 3., r + 3., c));
  }
  gl_FragColor = vec4(k.x, k.y, reach, 1.); }`;
const DOF_GATHER = `${DOF_COMMON}
void main(){
  vec4 kc = texture2D(tK, vUv); float cc = abs(kc.x), zc = kc.y;
  float R = clamp(max(cc, texture2D(tK2, vUv).z), 1., uMaxR);   // taps spread over this pixel's own / incoming blur only
  vec4 acc = texture2D(tHalf, vUv); float wsum = 1.;
  for (int i = 0; i < 24; i++) {
    float fi = float(i) + .5; float r = sqrt(fi/24.)*R; float a = fi*2.39996;
    vec2 uv = vUv + vec2(cos(a), sin(a))*r*uPx;
    vec4 ks = texture2D(tK, uv); float cs = abs(ks.x);
    float w = smoothstep(r - 2., r + 1., cs);
    if (ks.y > zc*1.02) w = min(w, smoothstep(r - 2., r + 1., cc));   // background never bleeds over a sharper foreground
    vec4 c4 = texture2D(tHalf, uv); w /= 1. + max(c4.r, max(c4.g, c4.b))*.08;
    acc += c4*w; wsum += w;
  }
  gl_FragColor = acc/wsum; }`;
// (4b) FILL: closes the gaps between the 24 taps (a small bright highlight would otherwise print the tap pattern)
const DOF_FILL = `${DOF_COMMON}
void main(){
  float r = clamp(max(abs(texture2D(tK, vUv).x), texture2D(tK2, vUv).z), 1., uMaxR)*.38; vec4 acc = texture2D(tBlur, vUv)*2.; float ws = 2.;
  for (int i = 0; i < 12; i++) { float a = float(i)*1.0472 + (i < 6 ? .26 : .78); float rr = i < 6 ? r*.5 : r;
    acc += texture2D(tBlur, vUv + vec2(cos(a), sin(a))*rr*uPx); ws += 1.; }
  gl_FragColor = acc/ws; }`;
const DOF_COMP = `${DOF_COMMON}
void main(){
  float f = max(abs(coc(vz(vUv))), texture2D(tK2, vUv).z);
  gl_FragColor = mix(texture2D(tCol, vUv), texture2D(tBlur, vUv), smoothstep(1., 4.5, f)); }`;
function buildDOF() {
  const dt = new THREE.DepthTexture(W, H); dt.type = THREE.UnsignedIntType;
  const rtS = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 2, depthBuffer: true, depthTexture: dt });
  const half = () => new THREE.WebGLRenderTarget(W / 4, H / 4, { type: THREE.HalfFloatType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: false });
  const rtC = half(), rtK = half(), rtK2 = half(), rtB = half(), rtF = half();
  const U = { tCol: { value: rtS.texture }, tDep: { value: dt }, tHalf: { value: rtC.texture }, tK: { value: rtK.texture }, tK2: { value: rtK2.texture },
    tBlur: { value: rtB.texture }, uNear: { value: .1 }, uFar: { value: 600 },
    uFocus: { value: 10 }, uAp: { value: 20 }, uMaxR: { value: 26 }, uPx: { value: new THREE.Vector2(1 / W, 1 / H) } };
  const sm = frag => new THREE.ShaderMaterial({ vertexShader: QV, fragmentShader: frag, uniforms: U, depthTest: false, depthWrite: false, blending: THREE.NoBlending });
  const qs = new THREE.Scene(), qc = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const P = { prepC: sm(DOF_PREPC), prepK: sm(DOF_PREPK), dil: sm(DOF_DIL), gather: sm(DOF_GATHER), fill: sm(DOF_FILL), comp: sm(DOF_COMP) };
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), P.comp); quad.frustumCulled = false; qs.add(quad);
  const pass = (r, m, rt) => { quad.material = m; r.setRenderTarget(rt); r.render(qs, qc); };
  // render `scene` through the DOF into the engine's 3D layer (focus = view distance in focus, ap = CoC px scale, maxR px)
  function render(E, scene, cam, focus, ap, maxR = 26) {
    const r = E.renderer, prevRT = r.getRenderTarget();
    U.uNear.value = cam.near; U.uFar.value = cam.far; U.uFocus.value = focus; U.uAp.value = ap; U.uMaxR.value = maxR;
    r.setRenderTarget(rtS); r.setClearColor(0x000000, 0); r.clear(true, true, true); r.render(scene, cam);
    pass(r, P.prepC, rtC); pass(r, P.prepK, rtK); pass(r, P.dil, rtK2); pass(r, P.gather, rtB);
    U.tBlur.value = rtB.texture; pass(r, P.fill, rtF); U.tBlur.value = rtF.texture;
    r.setRenderTarget(prevRT);
    quad.material = P.comp; E.render3D(qs, qc);
  }
  return { render };
}

// ------------------------------------------------------------------ machined parts + a product-photography strip environment
const lathe = (pts, seg = 96) => new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r, y)), seg);
// rounded edge from (r0,y0) going outward-then-up: a quarter-round of radius c sampled in n steps (corner at (r1, y1))
function bevel(rc, yc, c, a0, a1, n = 4) { const o = []; for (let i = 0; i <= n; i++) { const a = lerp(a0, a1, i / n); o.push([rc + Math.cos(a) * c, yc + Math.sin(a) * c]); } return o; }
// collar closing the band sleeve: chamfered faces, a cut parting line, a knurl-free brushed body
function ferruleGeo() {
  const r = .665, h = .17, c = .035;
  return lathe([[0, -h], ...bevel(r - c, -h + c, c, -Math.PI / 2, 0), [r, -.035], [r - .012, -.028], [r - .012, -.012], [r, -.005],
    ...bevel(r - c, h - c, c, 0, Math.PI / 2), [.56, h], [.56, h + .02]], 128);
}
function rodGeo() {   // slider rod (local y -.65..+.65) with a machined stop line
  const r = .3, c = .03;
  return lathe([[0, -.65], ...bevel(r - c, -.65 + c, c, -Math.PI / 2, 0), [r, .2], [r - .01, .206], [r - .01, .222], [r, .228], [r, .65], [0, .65]], 96);
}
function capGeo() {   // stop collar under the band collar
  const r = .45, c = .04;
  return lathe([[0, -.25], ...bevel(r - c, -.25 + c, c, -Math.PI / 2, 0), [r, .25], [0, .25]], 96);
}
function barrelGeo() {   // hinge barrel (axis y), chamfered both ends
  const r = .21, h = .43, c = .03;
  return lathe([[0, -h], ...bevel(r - c, -h + c, c, -Math.PI / 2, 0), ...bevel(r - c, h - c, c, 0, Math.PI / 2), [0, h]], 64);
}
// a black studio with long softboxes: polished metal shows crisp dark / bright bands instead of a flat cream
function stripEnv(renderer) {
  const s = new THREE.Scene(); s.background = new THREE.Color(.004, .0036, .003);
  const box = (w, h, pos, k, col = [1, .96, .9]) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(col[0] * k, col[1] * k, col[2] * k), side: THREE.DoubleSide }));
    m.position.set(...pos); m.lookAt(0, 0, 0); s.add(m);
  };
  box(1.1, 14, [6, 0, 3.5], 7);                       // key strip, front right
  box(.7, 14, [-5.5, 0, -3], 5, [1, .9, .74]);        // warm rim strip, back left
  box(.5, 14, [-4, 0, 5.5], 2.2);                     // thin fill strip, front left
  box(6, 2.2, [0, 6, -1], 2.6);                       // top softbox
  box(14, .35, [0, -1.2, 6.5], 1.6, [1, .92, .8]);    // low horizon line in front
  box(30, 30, [0, -8, 0], .05, [1, .85, .65]);        // warm floor bounce
  const pm = new THREE.PMREMGenerator(renderer), rt = pm.fromScene(s, .012); pm.dispose();
  return rt.texture;
}

let R = null;   // rig
const SB = { cx: 6.4, cy: -3.4, cz: 9.6, fov: 24, up: -.1, ap: 55 };   // shot B lens
// lights at zero intensity are switched off entirely (fewer lights in every shader on the software renderer)
function lightsOn(L) { [L.key, L.rim, L.under, L.ringL, L.graze].forEach(l => { l.visible = l.intensity > 1e-4; }); }

function build(E) {
  const scene = new THREE.Scene(); scene.userData._envSet = true; scene.environmentIntensity = 0; scene.environment = E.env;
  const cam = new THREE.PerspectiveCamera(30, W / H, .1, 600);
  const prod = new THREE.Group(); scene.add(prod);
  const hp = createHeadphone(); prod.add(hp.root);
  const cup = hp.cups[1], ring = cup.userData.parts.ring;
  hp.cups.forEach(c => { ['pcb', 'battery', 'magnet', 'coil', 'driver'].forEach(k => { c.userData.parts[k].visible = false; }); });   // internals never shown here
  // ---- the shared product look
  const M = lookMaterials();
  addStrip(M.gold, 1, 'gold'); addStrip(M.shell, .9, 'shell');
  hp.cups.forEach(c => {
    const p = c.userData.parts;
    p.shell.material = M.shell; p.ring.material = M.gold; p.cushion.material = M.leather;
    p.mesh.children.forEach(o => { o.material = M.gold; });
  });
  hp.band.core.material = M.gold; hp.band.sleeve.material = M.fabric;
  const ferrules = [];
  // gold ferrules closing the open ends of the band sleeve (the collar of hero.jpg)
  [1, -1].forEach(s => {
    const a = s > 0 ? .17 : Math.PI - .17, fe = new THREE.Mesh(s > 0 ? ferruleGeo() : ferruleGeo().rotateX(Math.PI), M.gold);
    fe.scale.set(1, 1, 1.95); fe.rotation.z = a;
    fe.position.set(Math.cos(a) * 8.1, Math.sin(a) * 8.1, 0).add(new THREE.Vector3(-Math.sin(a), Math.cos(a), 0).multiplyScalar(.07 * s));
    hp.band.group.add(fe); ferrules.push(fe);
  });
  // ---- sliders: no pivot ball jammed into the dome. The rod stops on a machined hinge barrel resting on the cup's shoulder.
  const hinges = [];
  hp.sliders.forEach((g, i) => {
    const s = i ? 1 : -1, [rod, cap, ball] = g.children;
    rod.material = M.gold; cap.material = M.gold; ball.visible = false;
    rod.geometry = rodGeo(); rod.position.y = .5;             // local y -.15 .. 1.15
    cap.geometry = capGeo();
    const hinge = new THREE.Group(); hinge.position.set(-s * .14, -.2, 0); g.add(hinge); hinges.push(hinge);
    const pin = new THREE.Mesh(barrelGeo().rotateX(Math.PI / 2), M.gold); hinge.add(pin);
    [-.43, .43].forEach(z => { const face = new THREE.Mesh(new THREE.CircleGeometry(.15, 48), M.shell); face.position.z = z + Math.sign(z) * .004; if (z < 0) face.rotation.y = Math.PI; hinge.add(face); });
  });
  // s03's ring tube (same curve, radius, shader); additive so the PBR ring shows through as it fades
  hp.root.updateMatrixWorld(true);
  const pts = [], v = new THREE.Vector3();
  for (let i = 0; i < 360; i++) { const a = i / 360 * TAU; v.set(3.99 * Math.cos(a), 0, 3.99 * Math.sin(a)); pts.push(ring.localToWorld(v.clone())); }
  const tubeMat = new THREE.ShaderMaterial({ vertexShader: TUBE_V, fragmentShader: TUBE_F, ...ADDITIVE, depthTest: false,
    uniforms: { uInt: { value: 6.8 }, uCol: { value: GOLD.clone().lerp(new THREE.Color(1, 1, 1), .08).multiplyScalar(.5) } } });
  const tube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 360, .12, 16, true), tubeMat);
  tube.renderOrder = 10; tube.frustumCulled = false; prod.add(tube);   // built in hp.root space == prod space
  // lights
  const key = new THREE.DirectionalLight(0xfff0de, 0); key.position.set(34, 30, 22); scene.add(key);
  const rim = new THREE.DirectionalLight(0xe6c896, 0); rim.position.set(-30, 12, -26); scene.add(rim);
  const under = new THREE.DirectionalLight(0xffd9a0, 0); under.position.set(5, -30, 12); scene.add(under);
  const ringL = new THREE.PointLight(0xffd9a0, 0, 14, 2); scene.add(ringL);
  const graze = new THREE.SpotLight(0xffe6c4, 0, 9, 22 * DEG, .85, 1.6); scene.add(graze); scene.add(graze.target);
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
  // macros: the motes are drawn AFTER the depth of field (their own shader already makes soft bokeh discs; a gather blur
  // of a tiny bright point would only print the tap pattern)
  const dustScene = new THREE.Scene(); dustScene.userData._envSet = true; dustScene.userData.autoEnv = false;
  const dust2 = new THREE.Points(dg, dustMat); dust2.frustumCulled = false; dustScene.add(dust2);
  // macro fabric: bump fades with view distance (no sparkle at the band's far edge; the DOF does the rest)
  const fabricB = M.fabricMacro;
  fabricB.customProgramCacheKey = () => 's04-weave';
  fabricB.onBeforeCompile = sh => {
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <bumpmap_pars_fragment>', 'float s04Far(){ return smoothstep(1.4, 3.2, length(vViewPosition)); }\n#include <bumpmap_pars_fragment>')
      .replace('#include <normal_fragment_maps>', 'float s04k = 1. - s04Far();\n' + THREE.ShaderChunk.normal_fragment_maps.replace('dHdxy_fwd()', 'dHdxy_fwd()*s04k'));
  };
  // macro look for the polished gold (same colour, relit): crisp strip-studio reflections, a touch glossier
  const senv = stripEnv(E.renderer);
  const goldB = M.gold.clone(); goldB.roughness = .17; goldB.anisotropy = .35; goldB.bumpScale = .06;
  goldB.envMap = senv; goldB.envMapIntensity = .95; addStrip(goldB, 1, 'goldB');
  const goldMeshes = []; hp.root.traverse(o => { if (o.isMesh && o.material === M.gold) goldMeshes.push(o); });
  const setGold = m => goldMeshes.forEach(o => { o.material = m; });
  return { scene, cam, prod, hp, ring, tube, tubeMat, key, rim, under, ringL, graze, sea, seaG, ringMat, ringPlane, dust, dustMat,
    senv, goldB, setGold, M, ferrules, hinges, dustScene, rodR: hp.sliders[1].children[0],
    sleeve: hp.band.sleeve, fabricA: M.fabric, fabricB, dof: buildDOF() };
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
const D0 = Math.hypot(CUP_CAM.position[0] - CUP_CAM.target[0], CUP_CAM.position[1] - CUP_CAM.target[1], CUP_CAM.position[2] - CUP_CAM.target[2]);
function shotA(q) {
  const u = seg(q, 0, 12);
  const kd = 1 - Math.pow(1 - u, 4.2);                 // distance: brutal pull
  const ka = eio(seg(q, .4, 11.5)) * .55 + kd * .45;   // orbit lags a hair -> a swooping arc
  const T0 = V(...CUP_CAM.target);
  const target = T0.clone().lerp(A1.target, kd);
  const dist = Math.exp(lerp(Math.log(D0), Math.log(A1.dist), kd)) * (1 + .035 * seg(q, 10, 24));  // + slow drift back
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
// soft ink pool (darkens what is under type)
function inkPool(ctx, x, y, rx, ry, alpha) {
  if (alpha <= .003) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(rx / ry, 1);
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, ry);
  g.addColorStop(0, `rgba(5,5,6,${alpha})`); g.addColorStop(.55, `rgba(5,5,6,${alpha * .8})`); g.addColorStop(1, 'rgba(5,5,6,0)');
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
// part label (left aligned at x 80) on a soft dark backing: index Unbounded 300 34 #f6f3ec @1470, name JetBrains Mono 700 32 gold @1520
function partLabel(fg, idx, name, q0, q, F, { wipeOut = null, wipeLen = 3, target = null, lineFrom = null, nameDelay = .5, rate = 8, lineLen = 6 } = {}) {
  const d = q - q0; if (d < 0) return;
  let clipX = W;
  if (wipeOut !== null && q >= wipeOut) clipX = lerp(W, 60, eio(seg(q, wipeOut, wipeOut + wipeLen)));
  if (clipX <= 62) return;
  fg.save(); fg.beginPath(); fg.rect(0, 0, clipX, H); fg.clip();
  // backing: soft ink slab behind x 60-760, y 1420-1560 (feathered ellipse, no canvas filter: cheap)
  {
    const kb = eout(seg(d, 0, 3));
    fg.save(); fg.translate(400, 1490); fg.scale(500 / 120, 1);
    const g = fg.createRadialGradient(0, 0, 0, 0, 0, 120);
    g.addColorStop(0, `rgba(5,5,6,${.64 * kb})`); g.addColorStop(.62, `rgba(5,5,6,${.56 * kb})`); g.addColorStop(1, 'rgba(5,5,6,0)');
    fg.fillStyle = g; fg.fillRect(-120, -120, 240, 240); fg.restore();
  }
  // index rises in
  const ki = expoOut(seg(d, 0, 3));
  fg.save(); fg.beginPath(); fg.rect(60, 1420, 600, 64); fg.clip();
  text(fg, idx, 80, 1470 + (1 - ki) * 44, { size: 34, weight: 300, family: FONT.display, color: COL.white, align: 'left', spacing: 2 });
  fg.restore();
  const iw = measure(fg, idx, 34, 300, FONT.display, 2);
  fg.fillStyle = COL.gold; fg.globalAlpha = .9; fg.fillRect(80 + iw + 18, 1458, 90 * eout(seg(d, .5, 4)), 2); fg.globalAlpha = 1;
  // name decodes on (rate chars per frame) -> complete within ~3 frames
  if (d >= nameDelay) {
    const n = Math.floor((d - nameDelay) * rate + 1);
    text(fg, decode(name, n, idx.length * 7, F), 80, 1522, { size: 32, weight: 700, family: FONT.mono, color: COL.gold, align: 'left', spacing: 5.5 });
  }
  // leader line (1.5 px gold2) + target reticle
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
  motionBlur(lt) { const q = lt * 30; return q >= .5 && q < 5 ? 2 : q >= QW ? 2 : 1; },
  draw(E, lt, t) {
    const q = lt * 30, F = Math.floor(q + 1e-4), fx = E.fx, bg = E.bg, fg = E.fg, b = lt / BEAT;
    const { scene, cam, prod } = R;
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
    L.key.intensity = L.rim.intensity = L.under.intensity = L.ringL.intensity = L.graze.intensity = 0;
    L.seaG.visible = L.ringPlane.visible = false; L.sleeve.material = L.fabricA; L.tube.visible = false;
    L.hp.sliders.forEach(g => { g.visible = true; }); L.hinges.forEach(h => { h.visible = true; }); L.rodR.scale.y = 1; L.rodR.position.y = .5; L.hp.cups.forEach(c => { c.visible = true; }); L.hp.band.group.visible = true;
    L.dust.visible = true; L.dustMat.uniforms.uT.value = t; L.dustMat.uniforms.uAlpha.value = q < QB ? eout(seg(q, 6, 14)) : 1;
    STRIP.uStripI.value = 0; scene.environment = E.env;

    bg.fillStyle = COL.ink; bg.fillRect(0, 0, W, H);

    if (shot === 'A') {
      // light floods in over f240-246 (smooth from 0: frame 0 is s03's dark frame)
      const flood = smooth(seg(q, 0, 6));
      const c = shotA(q); setCam(cam, c.pos, c.target, c.fov);
      // s03 hid the band + right slider; they come back once the camera is moving
      if (q < 1.5) { L.hp.sliders[1].visible = false; L.hp.band.group.visible = false; }
      L.key.intensity = 2.7 * flood; L.rim.intensity = 3.2 * flood; L.under.intensity = .35 * flood;
      scene.environmentIntensity = .25 * flood;
      // the ring: s03's emissive tube (intensity ~6.8 on its last frame) cools into the real PBR ring over 8 frames
      const tI = 6.8 * Math.pow(1 - seg(q, 0, 8), 1.6);
      L.tube.visible = tI > .02; L.tubeMat.uniforms.uInt.value = tI;
      // s03's warm fill riding in front of the cup face (same place, same falloff), decays
      L.ringL.position.copy(Lw(V(CUP_RING.center[0] + 5.5, CUP_RING.center[1], 0))); L.ringL.intensity = q < 14 ? 4.9 * Math.exp(-q / 5) : 0;
      // sea + ring
      const ur = seg(b, .5, 2.5), Rr = 60 * lerp(eout(ur), ur * ur, .55);
      L.seaG.visible = true; L.seaG.rotation.y = A1.az; L.seaG.updateMatrixWorld(true);
      const camLocal = L.seaG.worldToLocal(cam.position.clone());
      L.sea.update(t, Rr, A1.az, smooth(seg(q, 1, 9)), camLocal);
      L.ringPlane.visible = true;
      const u = L.ringMat.uniforms; u.uR.value = Rr; u.uI.value = seg(b, .5, .56); u.uBirth.value = b >= .5 ? Math.exp(-(b - .5) / .12) : 0;
      u.uInv.value.setFromMatrix4(new THREE.Matrix4().copy(L.seaG.matrixWorld).invert());
      // a slow studio strip glides over the gold of the hero pose
      if (q > 8) aimStrip(cam, lerp(-35, 25, eio(seg(q, 8, 24))) * DEG, .06, 2.2 * smooth(seg(q, 8, 13)));
      // background beam + horizon warmth (ramped from 0)
      beam(bg, 1150, -160, 520, 900, .2, .55 * flood);
      const hg = bg.createRadialGradient(540, 1180, 0, 540, 1180, 820);
      hg.addColorStop(0, `rgba(90,70,44,${.16 * flood})`); hg.addColorStop(1, 'rgba(5,5,6,0)');
      bg.fillStyle = hg; bg.fillRect(0, 0, W, H);
      lightsOn(L);
      E.render3D(scene, cam);
      // fg: s03's close flare at the bottom of the ring, continued (starts at s03's last values) and decaying
      if (q < 10) {
        const p = project(cam, Lw(V(CUP_RING.center[0], CUP_RING.center[1] - CUP_RING.ay, 0))), k = Math.exp(-q / 2.6);
        halo(fg, p[0], p[1], 395 * k + 40, 12, .4 * k, '255,236,200');
        halo(fg, p[0], p[1], 70, 70, .26 * k, '255,220,160');
      }
      drawLockup(fg, q, F, null);
      // post: frame 0 = s03's last-frame levels, easing into this scene's over the flood
      const m = smooth(seg(q, 0, 6));
      fx.exposure = lerp(.88, .8, m); fx.vignette = lerp(.4, .5, m); fx.sat = lerp(1.05, .92, m);
      fx.bloom = q < 6 ? lerp(1.0, 1.15, smooth(seg(q, 0, 3))) : lerp(1.15, .6, eout(seg(q, 6, 16)));
      fx.bloomThreshold = lerp(.7, .72, seg(q, 0, 12));
      fx.rgb = Math.max(fx.rgb, .0015 + .012 * c.vel * seg(q, 0, 1.5));
      // b20.5 ring birth + b21 heartbeat pump
      if (b >= .5 && b < .75) { const k = 1 - (b - .5) / .25; fx.zoom *= 1 + .012 * k; fx.rgb = Math.max(fx.rgb, .0015 + .004 * k); }
      if (q >= 12 && q < 16) { const k = 1 - (q - 12) / 4; fx.zoom *= 1 + .012 * k; }
    } else if (shot === 'B') {
      // SHOT B: low macro looking up at the right slider entering the band collar. The cup's stone shoulder + gold ring
      // sit soft in the foreground (they hide the hinge), the collar is in focus, the band arcs away out of focus.
      // A narrow studio strip sweeps L -> R across the beat over polished gold in a black strip-light studio.
      const d = q - QB, u = d / 12;
      const tgtL = V(7.99, 1.02 + .1 * eio(u), .35);
      const camL = V(SB.cx, SB.cy, SB.cz);
      const tw = Lw(tgtL), cw0 = Lw(camL);
      const pos = tw.clone().lerp(cw0, 1 - .06 * eio(u));
      setCam(cam, pos, tw, SB.fov, V(SB.up, 1, 0).normalize());
      const sw = eio(seg(d, -1, 13));
      aimStrip(cam, lerp(-58, 58, sw) * DEG, .04, 9);
      L.setGold(L.goldB); scene.environment = L.senv;
      L.key.intensity = 1.1; L.rim.intensity = 2.4; L.under.intensity = .1; scene.environmentIntensity = .35;
      // bg: dark studio + the strip glimpsed behind
      const gx = lerp(-200, 1280, sw);
      const g = bg.createLinearGradient(gx - 260, 0, gx + 260, 0);
      g.addColorStop(0, 'rgba(70,56,38,0)'); g.addColorStop(.5, 'rgba(70,56,38,.22)'); g.addColorStop(1, 'rgba(70,56,38,0)');
      bg.fillStyle = g; bg.fillRect(0, 0, W, H);
      L.hinges.forEach(h => { h.visible = false; });   // the rod runs down into the cup's shoulder (no stub end in frame)
      L.rodR.scale.y = 2.2; L.rodR.position.y = -.28;
      L.dust.visible = false; lightsOn(L);
      const fP = Lw(V(8.03, 1.2, 1.0));
      L.dof.render(E, scene, cam, pos.distanceTo(fP), SB.ap, 30);
      L.dustMat.uniforms.uAlpha.value = .7; E.render3D(L.dustScene, cam);
      L.setGold(L.M.gold); scene.environment = E.env;
      drawLockup(fg, q, F, QB);
      const target2d = project(cam, Lw(V(7.97, .29, .3)));
      partLabel(fg, '01', 'CHAMPAGNE GOLD ALUMINUM', QB + 1.5, q, F, { wipeOut: QC - 1.5, wipeLen: 1.5, rate: 12, nameDelay: .5, lineLen: 4, target: target2d, lineFrom: [300, 1420] });
      if (d < 3) { fx.zoom *= 1 + .04 * (1 - d / 3); if (d < 1) fx.rgb = .008; }
      fx.vignette = .55; fx.bloom = .5; fx.bloomThreshold = .86;
    } else {
      // SHOT C (+ WHIP): macro skim along the woven headband, grazing spot; then a 70-degree whip pan
      const d = q - QC, u = clamp(d / 6);
      const R0 = 8.1 + .62;
      const th = lerp(1.12, .9, u) - (shot === 'W' ? .03 * seg(q, QW, QE) : 0);
      const radial = th2 => V(Math.cos(th2), Math.sin(th2), 0);
      const camL = radial(th).multiplyScalar(R0 + .55).add(V(0, 0, .75));
      const lookL = radial(th - .22).multiplyScalar(R0 - .55).add(V(0, 0, -.25));
      const pos = Lw(camL), look = Lw(lookL);
      const upW = Lw(radial(th).multiplyScalar(30)).sub(Lw(V(0, 0, 0))).normalize();
      let dir = look.clone().sub(pos);
      if (shot === 'W') dir.applyAxisAngle(upW, -70 * DEG * ein(seg(q, QW, QE)));
      setCam(cam, pos, pos.clone().add(dir), 42, upW);
      L.sleeve.material = L.fabricB;
      // the whip dissolves into light: the cups/sliders swinging into view would only leave sub-frame ghosts
      if (shot === 'W' && q >= QW + 2) { L.hp.cups.forEach(c => { c.visible = false; }); L.hp.sliders.forEach(g => { g.visible = false; }); }
      // grazing spot from the side, tight falloff: a pool of light travelling with the skim
      L.graze.position.copy(Lw(radial(th - .5).multiplyScalar(R0 + 1.5).add(V(0, 0, -2.2))));
      L.graze.target.position.copy(Lw(radial(th - .2).multiplyScalar(R0))); L.graze.target.updateMatrixWorld();
      L.graze.intensity = 70; L.key.intensity = .12; L.rim.intensity = 1.0; scene.environmentIntensity = .05;
      aimStrip(cam, lerp(30, 55, u) * DEG, .05, shot === 'C' ? 6 : 0);
      const g = bg.createRadialGradient(780, 520, 0, 780, 520, 900);
      g.addColorStop(0, 'rgba(84,66,42,.4)'); g.addColorStop(1, 'rgba(5,5,6,0)'); bg.fillStyle = g; bg.fillRect(0, 0, W, H);
      const focus = pos.distanceTo(Lw(radial(th - .16).multiplyScalar(R0)));
      lightsOn(L);
      if (shot === 'C') { L.dust.visible = false; L.dof.render(E, scene, cam, focus, 9, 22); E.render3D(L.dustScene, cam); } else { L.dust.visible = false; E.render3D(scene, cam); }
      const target2d = project(cam, Lw(radial(th - .16).multiplyScalar(R0)));
      partLabel(fg, '01', 'CHAMPAGNE GOLD ALUMINUM', QB + 1.5, q, F, { wipeOut: QC - 1.5, wipeLen: 1.5, rate: 9 });
      partLabel(fg, '02', 'WOVEN STONE FABRIC', QC, q, F, { wipeOut: QW + 1, wipeLen: 2, nameDelay: .2, rate: 12, lineLen: 3, target: shot === 'C' ? target2d : null, lineFrom: [300, 1420] });
      if (d < 3) { fx.zoom *= 1 + .04 * (1 - d / 3); if (d < 1) fx.rgb = .008; }
      fx.vignette = .55;
      if (shot === 'W') {
        const k = seg(q, QW, QE);
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
        // the whip lands in light: an anamorphic bar + warm haze peaking on the last frame (s05 opens on a warm haze)
        const kb = Math.pow(seg(k, .45, 1), 2);
        fx.exposure *= lerp(1, .35, Math.pow(seg(k, .35, 1), 1.4));   // the band dissolves into the light
        halo(fg, 540, 960, 1300 * kb + 100, 26, .9 * kb, '255,244,225');
        halo(fg, 540, 960, 900, 900, .3 * kb, '255,226,176');
      }
    }
  },
};

// 'Introducing' + 'SILENCE ONE': 'Introducing' writes from b20.5 (2 letters / frame), 'SILENCE ONE' opens from b20.9;
// both complete by ~b21.2 and hold over the b22 cut, then wipe out left -> right (the label 01 chases the wipe).
let IN = null;
const T_IN = 5, T_SO = 10, T_SIZE = 108;
function drawLockup(fg, q, F, qCut) {
  const s = 'Introducing', size = T_SIZE;
  if (q < T_IN) return;
  if (!IN) {
    fg.save(); fg.font = font(size, 400, FONT.serif, true); fg.letterSpacing = '0px';
    const tw = fg.measureText(s).width, xs = [];
    for (let i = 0; i < s.length; i++) xs.push(fg.measureText(s.slice(0, i)).width);
    fg.restore(); IN = { tw, xs };
  }
  let clipL = 0;
  if (qCut !== null && q >= qCut) clipL = lerp(0, W + 40, eio(seg(q, qCut, qCut + 1.5)));
  if (clipL >= W - 1) return;
  fg.save(); fg.beginPath(); fg.rect(clipL, 0, W - clipL, H); fg.clip();
  // soft ink pool under the title: the gold horizon / sea lines never run through the type
  inkPool(fg, 540, 1452, 560, 150, .62 * eout(seg(q, T_IN - 1, T_IN + 4)));
  const x0 = 540 - IN.tw / 2;
  for (let i = 0; i < s.length; i++) {
    const qi = T_IN + i * .5, k = seg(q, qi, qi + 3.5); if (k <= 0) continue;
    const e = expoOut(k);
    fg.save(); fg.translate(x0 + IN.xs[i], 1420 + (1 - e) * 26);
    const g = fg.createLinearGradient(0, -80, 0, 10); g.addColorStop(0, COL.white); g.addColorStop(1, COL.gold);
    text(fg, s[i], 0, 0, { size, weight: 400, family: FONT.serif, italic: true, color: g, align: 'left', alpha: e, blur: (1 - e) * 10 });
    fg.restore();
  }
  // glint travelling along the word as it writes
  if (q > T_IN + .5 && q < T_IN + 9) { const gx = x0 + IN.tw * clamp((q - T_IN) / 6.5); halo(fg, gx, 1390, 90, 26, .18 * (1 - seg(q, T_IN + 6, T_IN + 9)), '255,236,200'); }
  // 'SILENCE ONE' — Unbounded 500 52 gold, wipes open from the centre while its tracking tightens
  if (q >= T_SO) {
    const k = expoOut(seg(q, T_SO, T_SO + 4)), half = 600 * k, sp = lerp(30, 18, k);
    fg.save(); fg.beginPath(); fg.rect(540 - half, 1462, half * 2, 84); fg.clip();
    text(fg, 'SILENCE ONE', 540 + sp / 2, 1522, { size: 52, weight: 500, family: FONT.display, color: COL.gold, spacing: sp });
    fg.restore();
    if (k < .98) { halo(fg, 540 - half, 1504, 10, 40, .7, '255,236,200'); halo(fg, 540 + half, 1504, 10, 40, .7, '255,236,200'); }
  }
  fg.restore();
}
