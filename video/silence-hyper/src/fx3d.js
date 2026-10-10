// Reusable 3D building blocks for scenes (all deterministic, GPU-side where it matters).
//
//   const P = morphPoints(n)                   GPU particles that morph between two point sets
//     P.setA(positions, colors?) / P.setB(...) Float32Array n*3 (colors linear 0..1; default champagne gold)
//     P.update({ mix, time, size, alpha, scatter, swirl, brightness })   per frame
//     scene.add(P.points)
//   samplePhoto(img, n, opts)  -> {positions, colors}  points from the bright pixels of a photo/logo (centered plane, width `width`)
//   sampleText(str, n, opts)   -> {positions, colors}  points filling the glyphs of a string (centered plane)
//   spherePoints(n, r) / boxPoints(n, sx, sy, sz) / linePoints(n, len) -> Float32Array
//   textRing(str, opts)        -> Mesh: a cylindrical band with repeating text (rotate it; passes in front of/behind objects)
//   textPlane(str, opts)       -> Mesh: a flat plane with text (MeshBasic, unlit; colour multiplier for HDR glow)
//   waveTerrain(opts)          -> { mesh, update(fn(x, z) -> y) }  line-grid terrain for sound waves
//   streaks(n, opts)           -> { mesh, update(time, speed) }    additive light streaks flying along -Z (warp / tunnel)
import * as THREE from 'three';
import { rnd, COL, FONT, text, measure, ADDITIVE, dotTexture } from './lib.js';

const GOLD = new THREE.Color(COL.gold).convertSRGBToLinear();

// ------------------------------------------------------------------ morphing particles
const PV = `
attribute vec3 aPos1; attribute vec3 aCol0; attribute vec3 aCol1; attribute float aRnd;
uniform float uMix, uTime, uSize, uScatter, uSwirl, uPx;
varying vec3 vCol; varying float vR;
vec3 hash3(float n){ return fract(sin(vec3(n, n+1.7, n+3.1))*43758.5453)*2.-1.; }
void main(){
  float m = smoothstep(0., 1., clamp((uMix - aRnd*.35)/.65, 0., 1.));
  vec3 p = mix(position, aPos1, m);
  // mid-flight scatter (strongest halfway) + persistent scatter
  float mid = sin(3.14159*m);
  p += hash3(aRnd*917.)*(uScatter + mid*uScatter*2.);
  float a = uSwirl*(1.-m)*(.5+aRnd);
  p.xz = mat2(cos(a), -sin(a), sin(a), cos(a))*p.xz;
  p += .15*sin(uTime*1.7 + aRnd*40.)*vec3(.3, .5, .3)*uScatter;
  vCol = mix(aCol0, aCol1, m); vR = aRnd;
  vec4 mv = modelViewMatrix*vec4(p, 1.);
  gl_PointSize = uSize*uPx*(.6+.8*aRnd)/max(-mv.z, .1);
  gl_Position = projectionMatrix*mv;
}`;
const PF = `
uniform sampler2D uDot; uniform float uAlpha, uBright; varying vec3 vCol; varying float vR;
void main(){ float d = texture2D(uDot, gl_PointCoord).r; gl_FragColor = vec4(vCol*uBright*d, d*uAlpha); }`;
export function morphPoints(n, { size = .4, brightness = .9 } = {}) {  // dense additive clouds blow out fast: tune size/brightness per scene
  const g = new THREE.BufferGeometry();
  const p0 = new Float32Array(n * 3), p1 = new Float32Array(n * 3), c0 = new Float32Array(n * 3), c1 = new Float32Array(n * 3), r = new Float32Array(n);
  for (let i = 0; i < n; i++) { r[i] = rnd(i * 1.37 + .5); c0.set([GOLD.r, GOLD.g, GOLD.b], i * 3); c1.set([GOLD.r, GOLD.g, GOLD.b], i * 3); }
  g.setAttribute('position', new THREE.BufferAttribute(p0, 3)); g.setAttribute('aPos1', new THREE.BufferAttribute(p1, 3));
  g.setAttribute('aCol0', new THREE.BufferAttribute(c0, 3)); g.setAttribute('aCol1', new THREE.BufferAttribute(c1, 3)); g.setAttribute('aRnd', new THREE.BufferAttribute(r, 1));
  const mat = new THREE.ShaderMaterial({
    vertexShader: PV, fragmentShader: PF, ...ADDITIVE,
    uniforms: { uMix: { value: 0 }, uTime: { value: 0 }, uSize: { value: size }, uScatter: { value: 0 }, uSwirl: { value: 0 }, uPx: { value: 1920 * .5 },
      uDot: { value: dotTexture() }, uAlpha: { value: 1 }, uBright: { value: brightness } },
  });
  const points = new THREE.Points(g, mat); points.frustumCulled = false;
  const fill = (attr, arr) => { const a = g.getAttribute(attr); const L = arr.length / 3; for (let i = 0; i < n; i++) { const j = (i % L) * 3; a.array[i * 3] = arr[j]; a.array[i * 3 + 1] = arr[j + 1]; a.array[i * 3 + 2] = arr[j + 2]; } a.needsUpdate = true; };
  return {
    points, n, material: mat,
    setA(pos, col) { fill('position', pos); if (col) fill('aCol0', col); g.computeBoundingSphere(); },
    setB(pos, col) { fill('aPos1', pos); if (col) fill('aCol1', col); },
    setColor(which, color) { const c = new THREE.Color(color).convertSRGBToLinear(); const a = g.getAttribute(which === 'A' ? 'aCol0' : 'aCol1'); for (let i = 0; i < n; i++) a.array.set([c.r, c.g, c.b], i * 3); a.needsUpdate = true; },
    update({ mix, time, size, alpha, scatter, swirl, brightness } = {}) {
      const u = mat.uniforms;
      if (mix !== undefined) u.uMix.value = mix; if (time !== undefined) u.uTime.value = time; if (size !== undefined) u.uSize.value = size;
      if (alpha !== undefined) u.uAlpha.value = alpha; if (scatter !== undefined) u.uScatter.value = scatter; if (swirl !== undefined) u.uSwirl.value = swirl;
      if (brightness !== undefined) u.uBright.value = brightness;
    },
  };
}

// ------------------------------------------------------------------ point samplers
function pixelsOf(draw, w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); draw(x, w, h); return x.getImageData(0, 0, w, h).data; }
function pick(data, w, h, n, weightFn, width, colorFn) {
  const cand = []; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const i = (y * w + x) * 4; const wt = weightFn(data[i], data[i + 1], data[i + 2], data[i + 3]); if (wt > 0) cand.push([x, y, wt, i]); }
  const positions = new Float32Array(n * 3), colors = new Float32Array(n * 3), s = width / w;
  if (!cand.length) return { positions, colors };
  const tot = cand.reduce((a, c) => a + c[2], 0); const cum = []; let acc = 0; for (const c of cand) { acc += c[2]; cum.push(acc); }
  for (let k = 0; k < n; k++) {
    const r = rnd(k * 3.17 + .11) * tot; let lo = 0, hi = cum.length - 1; while (lo < hi) { const m = (lo + hi) >> 1; if (cum[m] < r) lo = m + 1; else hi = m; }
    const [x, y, , i] = cand[lo]; const jx = rnd(k * 7.1) - .5, jy = rnd(k * 9.3) - .5;
    positions.set([(x + jx - w / 2) * s, -(y + jy - h / 2) * s, (rnd(k * 1.9) - .5) * s * 2], k * 3);
    const c = colorFn(data[i], data[i + 1], data[i + 2]); colors.set(c, k * 3);
  }
  return { positions, colors };
}
const lin = v => { v /= 255; return v <= .04045 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); };
export function samplePhoto(img, n, { width = 20, res = 260, threshold = 40, crop } = {}) {
  const [sx, sy, sw, sh] = crop || [0, 0, img.width, img.height]; const w = res, h = Math.round(res * sh / sw);
  const d = pixelsOf(x => x.drawImage(img, sx, sy, sw, sh, 0, 0, w, h), w, h);
  return pick(d, w, h, n, (r, g, b, a) => { const l = Math.max(r, g, b) * a / 255; return l > threshold ? l - threshold : 0; }, width, (r, g, b) => [lin(r), lin(g), lin(b)]);
}
export function sampleText(str, n, { width = 20, size = 200, weight = 900, family = FONT.display, color = COL.gold, spacing = 0 } = {}) {
  const tmp = document.createElement('canvas').getContext('2d');
  const w = Math.ceil(measure(tmp, str, size, weight, family, spacing) + 40), h = Math.ceil(size * 1.3);
  const d = pixelsOf((x) => text(x, str, w / 2, h / 2, { size, weight, family, color: '#fff', spacing, baseline: 'middle' }), w, h);
  const c = new THREE.Color(color).convertSRGBToLinear();
  return pick(d, w, h, n, (r, g, b, a) => a > 128 ? 1 : 0, width, () => [c.r, c.g, c.b]);
}
export function spherePoints(n, r = 10, seed = 0) { const a = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const u = rnd(i * 2.1 + seed) * 2 - 1, th = rnd(i * 3.7 + seed) * Math.PI * 2, rr = r * Math.cbrt(rnd(i * 5.3 + seed)); const s = Math.sqrt(1 - u * u); a.set([rr * s * Math.cos(th), rr * u, rr * s * Math.sin(th)], i * 3); } return a; }
export function boxPoints(n, sx = 20, sy = 20, sz = 20, seed = 0) { const a = new Float32Array(n * 3); for (let i = 0; i < n; i++) a.set([(rnd(i * 1.3 + seed) - .5) * sx, (rnd(i * 2.9 + seed) - .5) * sy, (rnd(i * 4.1 + seed) - .5) * sz], i * 3); return a; }
export function linePoints(n, len = 20, seed = 0) { const a = new Float32Array(n * 3); for (let i = 0; i < n; i++) a.set([(rnd(i * 1.3 + seed) - .5) * len, (rnd(i * 2.9 + seed) - .5) * .05, 0], i * 3); return a; }

// ------------------------------------------------------------------ text meshes
function textCanvas(str, { size = 160, weight = 900, family = FONT.display, color = COL.white, gold = false, spacing = 0, pad = 30, repeat = 1, sep = '   ·   ' } = {}) {
  const s = Array.from({ length: repeat }, () => str).join(sep) + (repeat > 1 ? sep : '');
  const tmp = document.createElement('canvas').getContext('2d');
  const w = Math.ceil(measure(tmp, s, size, weight, family, spacing) + pad * 2), h = Math.ceil(size * 1.35 + pad * 2);
  const c = document.createElement('canvas'); c.width = Math.min(w, 8192); c.height = h; const x = c.getContext('2d');
  if (w > 8192) x.scale(8192 / w, 1);
  text(x, s, pad, h / 2, { size, weight, family, color, gold, spacing, align: 'left', baseline: 'middle' });
  return c;
}
export function textPlane(str, { height = 2, intensity = 1.6, opacity = 1, side = THREE.DoubleSide, ...o } = {}) {
  const c = textCanvas(str, o); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  const m = new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity, side, depthWrite: false, color: new THREE.Color(intensity, intensity, intensity) });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(height * c.width / c.height, height), m); mesh.userData.aspect = c.width / c.height; return mesh;
}
export function textRing(str, { radius = 12, height = 1.6, repeat = 3, intensity = 1.8, opacity = 1, inward = false, ...o } = {}) {
  const c = textCanvas(str, { repeat, ...o }); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  t.wrapS = THREE.RepeatWrapping; if (!inward) { t.repeat.x = -1; }
  const m = new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity, side: THREE.DoubleSide, depthWrite: false, color: new THREE.Color(intensity, intensity, intensity) });
  const geo = new THREE.CylinderGeometry(radius, radius, height, 160, 1, true);
  return new THREE.Mesh(geo, m);
}

// ------------------------------------------------------------------ wave terrain (line grid)
export function waveTerrain({ width = 60, depth = 60, nx = 120, nz = 60, color = COL.gold, intensity = 2, opacity = .9 } = {}) {
  const pos = new Float32Array(nx * nz * 3); const idx = [];
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) { pos.set([(i / (nx - 1) - .5) * width, 0, (j / (nz - 1) - .5) * depth], (j * nx + i) * 3); if (i < nx - 1) idx.push(j * nx + i, j * nx + i + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(idx);
  const c = new THREE.Color(color).convertSRGBToLinear().multiplyScalar(intensity);
  const mesh = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: c, transparent: true, opacity, ...ADDITIVE })); mesh.frustumCulled = false;
  return { mesh, update(fn) { const a = g.getAttribute('position'); for (let k = 0; k < nx * nz; k++) a.array[k * 3 + 1] = fn(a.array[k * 3], a.array[k * 3 + 2]); a.needsUpdate = true; } };
}

// ------------------------------------------------------------------ light streaks
export function streaks(n = 400, { radius = 14, length = 40, color = COL.gold, intensity = 3, thickness = .05 } = {}) {
  const geo = new THREE.BoxGeometry(thickness, thickness, 1); const c = new THREE.Color(color).convertSRGBToLinear().multiplyScalar(intensity);
  const mesh = new THREE.InstancedMesh(geo, new THREE.MeshBasicMaterial({ color: c, ...ADDITIVE }), n); mesh.frustumCulled = false;
  const d = new THREE.Object3D(); const base = [];
  for (let i = 0; i < n; i++) { const a = rnd(i * 1.1) * Math.PI * 2, r = radius * (.35 + .65 * Math.sqrt(rnd(i * 2.3))); base.push([Math.cos(a) * r, Math.sin(a) * r, rnd(i * 3.7) * length, .3 + rnd(i * 5.9)]); }
  return {
    mesh, update(time, speed = 40, stretch = 1) {
      for (let i = 0; i < n; i++) { const [x, y, z0, s] = base[i]; const z = -(((z0 + time * speed * s) % length)) + 5; d.position.set(x, y, z); d.scale.set(1, 1, Math.max(.01, stretch * speed * s * .12)); d.updateMatrix(); mesh.setMatrixAt(i, d.matrix); }
      mesh.instanceMatrix.needsUpdate = true;
    },
  };
}
