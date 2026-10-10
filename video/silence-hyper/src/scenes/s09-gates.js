// s09-gates — GATE RUN (b48-56): wearing the corridor.
// b48 match cut: the acoustic-mesh dots of s08 blast outward as warp streaks and reveal a corridor of SILENCE ONE
// headphones used as gates. The camera flies down -Z at 24 units/beat, passing UNDER the headband and BETWEEN the cups of
// one gate on every beat (b49 ... b56 = exit), rolling 0 -> 180° (a ratchet: part of each 22.5° step snaps on the beat).
// Gates alternate 0/90/180/270° about the axis and warm-gold / cool stone-grey light; their gold flares as they pass.
// Spec slams b48/50/52/54 (slot-machine Anton numerals + gold Unbounded units + serif descriptors) live on a camera-locked
// 3D plane INSIDE the corridor, so the nearest gate sweeps over the type with true depth while far gates sit behind it.
//
// Layers: bg2d ink + gold vanishing-point glow (beat-pulsed)
//         3D   8 headphone gates (internal parts hidden, fog to ink) + 300 additive spiral streaks + the type plane
//              (custom shader: inverse-ACES so the 2D-designed colours land exactly after the 3D tone map)
//         fg2d the b48 mesh-dot burst, the staircase HUD.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, expoIn, rnd, noise1, text, measure, font, b2s, COL, FONT, ADDITIVE, goldGrad } from '../lib.js';
import { createHeadphone } from '../model.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const B0 = 48, B1 = 56;
const DEG = Math.PI / 180;
const FOV = 78;                       // vertical
const VPY = 900;                      // vanishing point (screen y)
const SPEED = 24;                     // units per beat
const NG = 8;                         // gates k = 1..8
const LEAD = .33;                     // gate k reaches the lens at b48 + k + LEAD, so its cushions leave the frame edges ON the beat
const GS = 1.0;                       // gate scale
const PIV = -2.2;                     // model-space y that sits on the flight axis (between the cups, under the band)
const DT = 14;                        // camera-space distance of the type plane
const TY0 = 600, TH = 700;            // the type canvas covers screen y TY0 .. TY0+TH
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const camZ = b => -SPEED * (b - B0);
const gateZ = k => -SPEED * (k + LEAD);

const SPECS = [
  { b: 48, num: '40', unit: 'h', desc: 'of battery' },
  { b: 50, num: '40', unit: 'mm', desc: 'titanium driver' },
  { b: 52, num: '250', unit: 'g', desc: 'of almost nothing' },
  { b: 54, num: '360', unit: '°', desc: 'spatial audio' },
];
const NOTES = ['D4', 'E4', 'F4', 'G4', 'A4', 'B♭4', 'C5', 'D5'];

// camera roll: 0 -> 180° over the scene; ~45 % of every 22.5° step snaps in on the beat (ratchet), the rest glides
function rollAt(b) {
  const x = clamp(b - B0, 0, 8), n = Math.floor(x), f = x - n;
  const step = .55 * f + .45 * expoOut(f * 3.2);
  return -(n + step) * 22.5 * DEG;
}

// ------------------------------------------------------------------ type plane shader (inverse ACES)
const TV = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position, 1.); }`;
const TF = `
uniform sampler2D map; uniform float uExp, uAlpha; varying vec2 vUv;
vec3 s2l(vec3 c){ return mix(c/12.92, pow((c+.055)/1.055, vec3(2.4)), step(.04045, c)); }
vec3 invAces(vec3 y){ y = clamp(y, 0., .975); vec3 A = 2.43*y - 2.51, Bq = .59*y - .03, C = .14*y;
  return (-Bq - sqrt(max(Bq*Bq - 4.*A*C, 0.)))/(2.*A); }
void main(){ vec4 t = texture2D(map, vUv); if (t.a < .003) discard;
  gl_FragColor = vec4(invAces(s2l(t.rgb)*.93)/uExp, t.a*uAlpha); }`;

// ------------------------------------------------------------------ streaks (own instanced system: per-instance colour, helix)
function buildStreaks(n) {
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mat = new THREE.MeshBasicMaterial({ ...ADDITIVE, color: 0xffffff, fog: true });
  const mesh = new THREE.InstancedMesh(geo, mat, n); mesh.frustumCulled = false; mesh.renderOrder = 1;
  const gold = lin(COL.gold), goldHi = lin(COL.goldHi), white = lin(COL.white), c = new THREE.Color();
  const base = [];
  for (let i = 0; i < n; i++) {
    const kind = rnd(i * 4.7 + 1.3);
    const col = kind < .62 ? gold : kind < .85 ? goldHi : white;
    const inten = 1.6 + 2.6 * rnd(i * 6.1 + .2);
    c.copy(col).multiplyScalar(inten); mesh.setColorAt(i, c);
    base.push({ a0: rnd(i * 1.1 + .7) * TAU, r: 7.5 + 9 * Math.sqrt(rnd(i * 2.3 + .4)), z0: rnd(i * 3.7 + .9) * 260, v: 70 + 170 * rnd(i * 5.9 + .3), th: .035 + .05 * rnd(i * 8.3) });
  }
  mesh.instanceColor.needsUpdate = true;
  const d = new THREE.Object3D(), L = 260;
  return {
    mesh,
    update(b, cz, boost) {
      const tau = (b - B0) * BEAT;
      for (let i = 0; i < n; i++) {
        const s = base[i], v = s.v * boost;
        const rel = 8 - L + ((s.z0 + tau * v) % L);          // from -252 (far) to +8 (behind the lens), racing toward camera
        const z = cz + rel, a = s.a0 + .011 * z;              // helix in world space -> spirals as we fly
        const len = v * .055;
        const fade = clamp((rel + L - 8) / 40) * clamp((8 - rel) / 4);
        d.position.set(Math.cos(a) * s.r, Math.sin(a) * s.r, z - len / 2);
        d.rotation.set(0, 0, a);
        d.scale.set(s.th * fade + 1e-4, s.th * fade + 1e-4, len); d.updateMatrix(); mesh.setMatrixAt(i, d.matrix);
      }
      mesh.instanceMatrix.needsUpdate = true;
    },
  };
}

// ------------------------------------------------------------------ gates
// Eight gates are too heavy as eight full createHeadphone() trees on CPU WebGL (~180 draw calls, ~250k vertices, PBR+env on
// everything). So ONE headphone is built and baked into shared merged geometries per material family, in two LODs
// (hi: model resolution; lo: re-tessellated from the geometries' own parameters). Each gate = 6 meshes with its own
// materials (gold keeps PBR + env so it reads as metal; stone is Phong, fabric / leather / mesh are Lambert).
const HIDE = ['pcb', 'battery', 'magnet', 'coil', 'driver'];
function lowRes(g) {
  const P = g.parameters, t = g.type;
  let n = null;
  if (t === 'TorusGeometry') {
    n = new THREE.TorusGeometry(P.radius, P.tube, Math.max(6, Math.round(P.radialSegments / 2.5)), Math.max(28, Math.round(P.tubularSegments / 3)), P.arc);
    g.computeBoundingBox(); const bb = g.boundingBox;
    if (bb.max.y - bb.min.y < (bb.max.z - bb.min.z) * .5) n.rotateX(Math.PI / 2);
  } else if (t === 'LatheGeometry') n = new THREE.LatheGeometry(P.points, 40, P.phiStart, P.phiLength);
  else if (t === 'TubeGeometry') n = new THREE.TubeGeometry(P.path, 56, P.radius, Math.max(8, Math.round(P.radialSegments / 2.5)), P.closed);
  else if (t === 'CylinderGeometry') n = new THREE.CylinderGeometry(P.radiusTop, P.radiusBottom, P.height, Math.max(12, Math.round(P.radialSegments / 3)), 1, P.openEnded);
  else if (t === 'SphereGeometry') n = new THREE.SphereGeometry(P.radius, 16, 10, P.phiStart, P.phiLength, P.thetaStart, P.thetaLength);
  return n || g.clone();
}
function strip(g) { const o = new THREE.BufferGeometry(); for (const k of ['position', 'normal', 'uv']) o.setAttribute(k, g.getAttribute(k)); o.setIndex(g.index); return o.index ? o : null; }
function buildKit() {
  const hp = createHeadphone();
  hp.cups.forEach(c => HIDE.forEach(nm => { c.userData.parts[nm].visible = false; }));
  hp.root.position.y = -PIV; hp.root.updateMatrixWorld(true);
  const fam = { gold: [], stone: [], fabric: [], leather: [], mesh: [], dark: [] }, maps = {};
  const isHidden = o => { for (let q = o; q; q = q.parent) if (!q.visible) return true; return false; };
  hp.root.traverse(o => {
    if (!o.isMesh || isHidden(o) || Array.isArray(o.material)) return;
    const m = o.material;
    let f = null;
    if (m.metalness === 1 && Math.abs(m.roughness - .2) < 1e-3) f = 'gold';
    else if (m.clearcoat > 0) f = 'stone';
    else if (m.map && m.bumpScale === 1.2) f = 'fabric';
    else if (m.map && m.bumpScale === 1.5) f = 'leather';
    else if (m.map) f = 'mesh';
    else f = 'dark';
    if (m.map) maps[f] = m.map;
    fam[f].push(o);
  });
  const kit = { hi: {}, lo: {}, maps };
  for (const [f, list] of Object.entries(fam)) {
    if (!list.length) continue;
    const build = lo => mergeGeometries(list.map(o => { const g = strip(lo ? lowRes(o.geometry) : o.geometry.clone()); g.applyMatrix4(o.matrixWorld); return g; }));
    kit.hi[f] = build(false); kit.lo[f] = build(true);
  }
  return kit;
}
function buildGate(k, kit) {
  const warm = k % 2 === 1;
  const mats = {
    gold: new THREE.MeshStandardMaterial({ color: 0xdcb98a, metalness: 1, roughness: .2, emissive: lin(warm ? COL.gold : '#dfe4ea'), emissiveIntensity: 0 }),
    stone: new THREE.MeshPhongMaterial({ color: lin(warm ? '#a39b93' : '#8e959c'), specular: lin(warm ? '#4a4034' : '#3a4048'), shininess: 38, side: THREE.DoubleSide }),
    fabric: new THREE.MeshLambertMaterial({ map: kit.maps.fabric, color: warm ? new THREE.Color(1.1, 1.02, .92) : new THREE.Color(.9, .95, 1.02) }),
    leather: new THREE.MeshLambertMaterial({ map: kit.maps.leather, color: warm ? new THREE.Color(1.6, 1.48, 1.36) : new THREE.Color(1.4, 1.5, 1.7) }),
    mesh: new THREE.MeshLambertMaterial({ map: kit.maps.mesh }),
    dark: new THREE.MeshLambertMaterial({ color: 0x0b0b0c }),
  };
  const piv = new THREE.Group(); piv.scale.setScalar(GS);
  piv.position.set(0, 0, gateZ(k)); piv.rotation.z = ((k - 1) % 4) * 90 * DEG;
  const meshes = [];
  for (const f of Object.keys(kit.hi)) { const m = new THREE.Mesh(kit.hi[f], mats[f]); m.userData.f = f; m.frustumCulled = false; piv.add(m); meshes.push(m); }
  return { k, piv, warm, mats, meshes, lod: 'hi', setLod(l) { if (l === this.lod) return; this.lod = l; meshes.forEach(m => { m.geometry = kit[l][m.userData.f]; }); } };
}

// ------------------------------------------------------------------ 2D helpers
function makeCanvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }

// ---- glyph caches (420 px fillText and per-letter blur filters are far too slow per frame on CPU canvas)
const GC = { digits: null, desc: new Map(), plate: null, glow: null };
function buildCaches() {
  const m = makeCanvas(8, 8).getContext('2d'); m.font = font(420, 400, FONT.impact);
  const asc = Math.ceil(m.measureText('0').actualBoundingBoxAscent), pad = 24;
  GC.asc = asc;
  GC.digits = [...'0123456789'].map(d => {
    const w = Math.ceil(m.measureText(d).width), c = makeCanvas(w + pad * 2, asc + pad * 2);
    text(c.getContext('2d'), d, c.width / 2, asc + pad, { size: 420, family: FONT.impact, color: COL.white });
    return { c, w, pad };
  });
  for (const sp of SPECS) {
    const size = 76; m.font = font(size, 400, FONT.serif, true);
    const ch = [...sp.desc], ws = ch.map(c => m.measureText(c).width);
    const cells = ch.map((c, i) => [0, 2, 4, 6.5, 10].map(bl => {
      const pd = 34, cv = makeCanvas(Math.ceil(ws[i] + pd * 2 + 20), size + pd * 2);
      text(cv.getContext('2d'), c, cv.width / 2, size * .8 + pd, { size, family: FONT.serif, italic: true, color: COL.white, blur: bl });
      return cv;
    }));
    GC.desc.set(sp.b, { ws, cells, size, pd: 34 });
  }
  GC.plate = makeCanvas(W, TH);
  { const x = GC.plate.getContext('2d'), g = x.createRadialGradient(0, 0, 0, 0, 0, 540);
    g.addColorStop(0, 'rgba(5,5,6,.55)'); g.addColorStop(.55, 'rgba(5,5,6,.25)'); g.addColorStop(1, 'rgba(5,5,6,0)');
    x.translate(540, 940 - TY0); x.scale(1, .6); x.fillStyle = g; x.fillRect(-540, -560, 1080, 1120); }
  GC.glow = makeCanvas(1080, 1200);
  { const x = GC.glow.getContext('2d'), g = x.createRadialGradient(540, 600, 0, 540, 600, 600);
    g.addColorStop(0, 'rgba(230,200,150,.4)'); g.addColorStop(.35, 'rgba(230,200,150,.16)'); g.addColorStop(.7, 'rgba(230,200,150,.04)'); g.addColorStop(1, 'rgba(230,200,150,0)');
    x.fillStyle = g; x.fillRect(0, 0, 1080, 1200); }
}

// spec layout (number + unit centred as one block)
function layout(sp) {
  if (sp._L) return sp._L;
  const m = makeCanvas(8, 8).getContext('2d');
  const ds = [...sp.num].map(d => GC.digits[+d]);
  const wN = ds.reduce((a, d) => a + d.w, 0) + 6 * (ds.length - 1);
  const wU = measure(m, sp.unit, sp.unit === '°' ? 170 : 110, 700, FONT.display);
  const gap = sp.unit === '°' ? 8 : 18;
  const x0 = Math.round(540 - (wN + gap + wU) / 2);
  return (sp._L = { ds, wN, wU, gap, x0 });
}
// one spec slam drawn into ctx (type-canvas coordinates: screen y - TY0); lf = frames since its downbeat
function drawSpec(ctx, sp, lf, numOnly = false) {
  const base = 1020 - TY0, asc = GC.asc, L = layout(sp);
  let x = L.x0;
  L.ds.forEach((D, i) => {
    const target = +sp.num[i], n = L.ds.length;
    const fi = 3 + 3 * (n > 1 ? i / (n - 1) : 1);                 // column i resolves at frame 3 .. 6 (left -> right)
    const p = clamp(lf / fi), spins = 10 * (1 + i) + 3.45 + .3 * i;
    const v = target + spins * (1 - eout(p));
    const fast = p < .55;
    const pitch = asc * 1.22;
    ctx.save(); ctx.beginPath(); ctx.rect(x - 6, base - asc - 16, D.w + 12, asc + 32); ctx.clip();
    const j0 = Math.floor(v) - 1;
    for (let j = j0; j <= j0 + 2; j++) {
      const y = base + (j - v) * pitch;
      const G = GC.digits[((j % 10) + 10) % 10];
      ctx.drawImage(G.c, x - G.pad, y - asc - G.pad);
      if (fast) { ctx.globalAlpha = .3; ctx.drawImage(G.c, x - G.pad, y - asc - G.pad - pitch * .22); ctx.globalAlpha = 1; }
    }
    ctx.restore();
    x += D.w + 6;
  });
  if (numOnly) return;
  // UNIT: Unbounded 700 gold gradient with a shine sweep
  const shine = -.4 + 1.1 * eio(seg(lf, 2, 16));
  const deg = sp.unit === '°';   // a degree sign on the baseline reads as a full stop: hang it from the cap line instead
  text(ctx, sp.unit, L.x0 + L.wN + L.gap, deg ? base - asc + 128 : base, { size: deg ? 170 : 110, weight: 700, family: FONT.display, gold: true, align: 'left', shine, alpha: clamp(lf / 2) });
}
function drawDesc(ctx, sp, lf) {
  if (lf < 6) return;
  const D = GC.desc.get(sp.b), tw = D.ws.reduce((a, b) => a + b, 0);
  let x = 540 - tw / 2;
  D.ws.forEach((w, i) => {
    const l = lf - 6 - i * .8;
    if (l > 0) {
      const k = eout(clamp(l / 4)), bl = 10 * (1 - k);
      const lv = bl > 8 ? 4 : bl > 5 ? 3 : bl > 3 ? 2 : bl > 1 ? 1 : 0, cv = D.cells[i][lv];
      ctx.save(); ctx.globalAlpha = clamp(l / 3);
      ctx.drawImage(cv, x + w / 2 - cv.width / 2, 1200 - TY0 + 12 * (1 - k) - D.size * .8 - D.pd);
      ctx.restore();
    }
    x += w;
  });
}

// mesh-dot burst (b48 match cut from s08's acoustic mesh); lf 0..3
function drawDots(ctx, lf) {
  if (lf >= 3) return;
  const p = lf / 3;
  const bgA = Math.max(0, 1 - lf * .8);
  if (bgA > 0) { ctx.save(); ctx.globalAlpha = bgA; ctx.fillStyle = 'rgb(95,72,38)'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  const S = f => 1 + .55 * f + .9 * f * f;                // scale at frame f
  const s1 = S(lf), s0 = S(Math.max(0, lf - .7));
  const P = 95, cx = 540, cy = 960, ox = 505 - cx, oy = 1012 - cy;
  ctx.save(); ctx.lineCap = 'round';
  for (let r = -12; r <= 12; r++) for (let c = -8; c <= 8; c++) {
    const px = ox + c * P + (r & 1 ? P / 2 : 0), py = oy + r * P;
    const x1 = cx + px * s1, y1 = cy + py * s1; if (x1 < -200 || x1 > W + 200 || y1 < -200 || y1 > H + 200) continue;
    const x0 = cx + px * s0, y0 = cy + py * s0;
    const a = 1 - p * .9, wdt = 54 * (1 - p * .7);
    ctx.globalAlpha = a; ctx.strokeStyle = lf < .5 ? 'rgb(160,137,100)' : 'rgb(236,206,150)'; ctx.lineWidth = wdt;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1 + .01, y1); ctx.stroke();
  }
  ctx.restore();
}

// staircase HUD: 8 rising steps, one per gate (the tuned whooshes D4 ... D5)
function drawHUD(ctx, b, alpha) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  const x0 = 80, yb = 1600, sw = 44, sg = 10;
  for (let i = 0; i < 8; i++) {
    const at = 49 + i, on = b >= at, hit = on ? Math.exp(-(b - at) * 4) : 0;
    const h = 14 + i * 9;
    const x = x0 + i * (sw + sg);
    ctx.fillStyle = on ? COL.gold : 'rgba(154,151,143,.35)';
    ctx.globalAlpha = alpha * (on ? .55 + .45 * hit : 1);
    ctx.fillRect(x, yb - h, sw, h);
    if (hit > .05) { ctx.globalAlpha = alpha * .25 * hit; ctx.fillRect(x - 6, yb - h - 6, sw + 12, h + 12); }
  }
  ctx.globalAlpha = alpha;
  const cur = clamp(Math.floor(b - 48), 0, 8);
  const lab = cur === 0 ? 'GATE 00 / 08' : `GATE 0${cur} / 08  ·  ${NOTES[cur - 1]}`;
  text(ctx, lab, x0, yb - 100, { size: 30, weight: 700, family: FONT.mono, color: COL.gold, align: 'left', spacing: 3 });
  ctx.restore();
}

// The engine's motion-blur accumulation comes out at 1/n brightness (additive blend of colour already weighted by 1/n).
// Probe once and compensate through fx.tint, so this scene stays right whether or not the engine gets fixed.
function probeMB(E) {
  try {
    const gl = E.renderer.getContext(), px = new Uint8Array(4);
    const draw = () => { E.bg.fillStyle = '#c0c0c0'; E.bg.fillRect(0, 0, W, H); Object.assign(E.fx, { bloom: 0, grain: 0, vignette: 0, rgb: 0 }); };
    E.renderFrame(0, draw, 1); gl.readPixels(540, 960, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); const a = px[0];
    E.renderFrame(0, draw, 2); gl.readPixels(540, 960, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); const c = px[0];
    return c < a * .85 ? 1 : 0;
  } catch (e) { return 0; }
}

let R = null;
// motion blur only where it matters: the 5 frames around each gate pass (the near gate whips off the frame edges)
function mbAt(lt) {
  const f = Math.round(lt * 30), fb = f % 12;                // integer frame -> stable across sub-frames
  return f >= 9 && (fb === 11 || fb === 0) ? 2 : 1;
}

export default {
  id: 's09-gates', start: 48, end: 56,
  cutIn: 'none',
  init(E) {
    const scene = new THREE.Scene();
    scene.userData.envIntensity = .35;
    scene.fog = new THREE.Fog(new THREE.Color(COL.ink), 30, 150);
    const cam = new THREE.PerspectiveCamera(FOV, W / H, .1, 400);
    cam.setViewOffset(W, H, 0, VPY - 960 + 0, W, H);
    scene.add(cam);
    const kit = buildKit(); const gates = []; for (let k = 1; k <= NG; k++) { const g = buildGate(k, kit); scene.add(g.piv); gates.push(g); }
    const hemi = new THREE.HemisphereLight(0xffe2bc, 0x1a2230, .55); scene.add(hemi);
    const camLight = new THREE.PointLight(0xfff0dc, 0, 0, 2); scene.add(camLight);
    const gl1 = new THREE.PointLight(0xffffff, 0, 0, 2); scene.add(gl1);
    const st = buildStreaks(300); scene.add(st.mesh);
    // type plane (camera-locked, 1:1 pixel mapping)
    const typeC = makeCanvas(W, TH), specC = makeCanvas(W, TH);
    const tex = new THREE.CanvasTexture(typeC); tex.colorSpace = THREE.NoColorSpace; tex.minFilter = tex.magFilter = THREE.LinearFilter; tex.generateMipmaps = false;
    const upx = 2 * DT * Math.tan(FOV / 2 * DEG) / H;
    const tmat = new THREE.ShaderMaterial({ vertexShader: TV, fragmentShader: TF, uniforms: { map: { value: tex }, uExp: { value: .85 }, uAlpha: { value: 1 } },
      transparent: true, depthTest: true, depthWrite: false });
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(W * upx, TH * upx), tmat);
    plane.position.set(0, (VPY - (TY0 + TH / 2)) * upx, -DT); plane.renderOrder = 2; plane.frustumCulled = false; cam.add(plane);
    buildCaches();
    R = { scene, cam, gates, camLight, gl1, st, typeC, specC, tex, tmat, plane, typeDirty: true, mbGain: probeMB(E) };
  },
  motionBlur(lt) { return mbAt(lt); },
  draw(E, lt, t) {
    const { scene, cam, gates, camLight, gl1, st } = R;
    const b = B0 + lt / BEAT, lf = lt * 30, fx = E.fx, bg = E.bg, fg = E.fg;
    const Fr = Math.floor(t * 30 + .5);
    const beatIn = b - Math.floor(b), passK = Math.floor(b - B0 - LEAD + 1e-6);   // last gate passed
    const hit = b >= 49 ? Math.exp(-((b - Math.floor(b)) * BEAT) / .09) : 0;    // on-beat gate pass envelope
    fx.exposure = .85; fx.bloom = .8; fx.bloomThreshold = .9; fx.sat = 1.1; fx.contrast = 1.05; fx.grain = .04; fx.vignette = .4;

    // ---------------- camera
    const cz = camZ(b);
    const sway = V3(.35 * noise1(b * .7 + 3), .3 * noise1(b * .6 + 11), 0);
    cam.position.set(sway.x, sway.y, cz);
    cam.rotation.set(0, 0, rollAt(b));
    cam.updateMatrixWorld();
    camLight.position.set(sway.x, sway.y, cz - 3);
    camLight.intensity = 520 + 700 * hit;

    // ---------------- gates
    let nearest = [];
    gates.forEach(g => {
      const d = cz - g.piv.position.z;                         // > 0 ahead of the camera
      g.piv.visible = d > -3 && d < 150;
      // each gate screws itself into place on approach (-40° -> its 0/90/180/270 slot by the time it is one gate away)
      g.piv.rotation.z = ((g.k - 1) % 4) * 90 * DEG - 40 * DEG * (1 - eio(clamp((84 - d) / 60)));
      const flare = d > 0 ? Math.exp(-d / 9) : Math.exp(d / 2);
      g.mats.gold.emissiveIntensity = (g.warm ? .25 : .12) + (g.warm ? 4.5 : 3) * flare;
      g.setLod(d < 50 ? 'hi' : 'lo');
      if (d > -1) nearest.push([d, g]);
    });
    nearest.sort((a, c) => a[0] - c[0]);
    [gl1].forEach((L, i) => {
      const e = nearest[i];
      if (!e) { L.intensity = 0; return; }
      const [d, g] = e;
      L.position.set(0, 0, g.piv.position.z + 1.5);
      L.color.copy(g.warm ? lin('#ffdcb0') : lin('#c4d4ec'));
      L.intensity = (g.warm ? 140 : 110) * clamp((70 - d) / 30);
    });

    // ---------------- streaks
    const boost = 1 + .6 * ein(seg(b, 55, 56));
    st.update(b, cz, boost);

    // ---------------- bg: ink + VP glow
    {
      const pulse = .18 + .1 * hit + .06 * seg(b, 55, 56);
      bg.save(); bg.globalAlpha = pulse / .4; bg.drawImage(GC.glow, 0, VPY - 600); bg.restore();
    }

    // ---------------- type plane
    {
      const tc = R.typeC.getContext('2d'), sc = R.specC.getContext('2d');
      const bt = B0 + Math.round(lt * 30) / 30 / BEAT;          // type animates per frame (identical in both motion-blur sub-frames)
      const sp = SPECS.find(s => bt >= s.b - 1e-6 && bt < s.b + 2 - 1e-6);
      if (sp || R.typeDirty) { tc.setTransform(1, 0, 0, 1, 0, 0); tc.clearRect(0, 0, W, TH); R.tex.needsUpdate = true; R.typeDirty = !!sp; }
      if (sp) {
        const sl = Math.round((bt - sp.b) * 12 * 1000) / 1000;      // frames since slam
        sc.setTransform(1, 0, 0, 1, 0, 0); sc.clearRect(0, 0, W, TH);
        // legibility plate: a soft dark pool under the type
        sc.save(); sc.globalAlpha = clamp(sl / 3); sc.drawImage(GC.plate, 0, 0); sc.restore();
        // stutter ghost on 16ths (+1.0 and +1.25 beats)
        const st1 = (sl >= 12 && sl < 13.5) || (sl >= 15 && sl < 16.5);
        if (st1) { sc.save(); sc.globalAlpha = .4; sc.translate(18, 0); drawSpec(sc, sp, sl, true); sc.restore(); }
        drawSpec(sc, sp, sl);
        drawDesc(sc, sp, sl);
        // composite into the type canvas: slam scale, slow push, slice wipe-out
        const slam = 1 + .4 * (1 - expoOut(clamp(sl / 3)));
        const push = 1 + .035 * seg(sl, 3, 21);
        const s = slam * push, ox = 540, oy = 880 - TY0;
        if (sl < 21) {
          tc.save(); tc.translate(ox, oy); tc.scale(s, s); tc.translate(-ox, -oy); tc.globalAlpha = clamp(sl + .5); tc.drawImage(R.specC, 0, 0); tc.restore();
        } else {
          const w = Math.min(1, (sl - 21) / 2.5), n = 22, hS = TH / n;
          for (let i = 0; i < n; i++) {
            const dir = rnd(i * 3.3 + sp.b) < .5 ? -1 : 1;
            const dx = dir * (40 + 900 * rnd(i * 7.7 + sp.b)) * ein(w) + dir * 30 * w;
            tc.save(); tc.globalAlpha = w >= 1 ? 0 : 1 - w * .8; tc.translate(ox, oy); tc.scale(s, s); tc.translate(-ox, -oy);
            tc.drawImage(R.specC, 0, i * hS, W, hS, dx, i * hS, W, hS); tc.restore();
          }
        }
      }
      R.tmat.uniforms.uExp.value = fx.exposure;
    }

    E.render3D(scene, cam);

    // ---------------- fg
    drawDots(fg, lf);
    drawHUD(fg, b, seg(lf, 2, 8) * (1 - seg(b, 55.6, 56)));

    // ---------------- post
    fx.zoomCenter = [.5, 1 - VPY / H];
    // speed blur: the radial blur costs ~2 s/frame on CPU, so it lives only on the gate passes and the exit rush
    fx.zoomBlur = b >= 55.25 ? .15 + .2 * eio(seg(b, 55.25, 56)) : 0;
    // gate passes b49 ... b56: flash .15 (3 frames), rgb .012, zoom 1.04
    if (b >= 49) {
      const fr = beatIn * 12;
      fx.rgb = Math.max(fx.rgb, .0015 + .0105 * Math.max(0, 1 - fr / 6));
      fx.zoom *= 1 + .04 * (1 - expoOut(clamp(fr / 6)));
      const sh = .006 * Math.max(0, 1 - fr / 6);
      fx.shake = [fx.shake[0] + (rnd(Fr * 1.7) - .5) * 2 * sh, fx.shake[1] + (rnd(Fr * 2.9 + 4) - .5) * 2 * sh];
    }
    // spec slams b48, 50, 52, 54: zoom 1.06, glitch .3 (3 frames)
    for (const sp of SPECS) {
      const fr = (b - sp.b) * 12;
      if (fr >= 0 && fr < 8) fx.zoom *= 1 + .06 * (1 - expoOut(fr / 8));
      if (fr >= 0 && fr < 3) { fx.rgb = Math.max(fx.rgb, .02 * (1 - fr / 3)); }
      if (fr >= 1 && fr < 3.5) { fx.glitch = Math.max(fx.glitch, fr < 2 ? .2 : .1); fx.glitchSeed = sp.b * 17 + Math.floor(fr) * 5; }   // frame 0 stays a clean punch
      // wipe-out slices: a touch of glitch too
      if (fr >= 21 && fr < 24) { fx.rgb = Math.max(fx.rgb, .008); }
    }
    // b48 match-cut kick
    if (lf < 4) { fx.zoomBlur = Math.max(fx.zoomBlur, .7 * (1 - lf / 4)); fx.zoomCenter = [.5, .5]; }
    const nMB = mbAt(lt);
    if (R.mbGain && nMB > 1) { fx.tint = fx.tint.map(v => v * nMB); fx.bloomThreshold /= nMB; }
  },
};
