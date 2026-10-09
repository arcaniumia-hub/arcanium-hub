// SILENCE ONE — procedural 3D model + exploded-view teardown (three.js).
// Bundled to teardown.bundle.js (npm run build). Exposes window.TD = { canvas, render(lt) -> anchors }.
// lt runs 0 → 10 s:  0–1.3 assembled (scan-in) · 1.3–3.4 global explode · 3.4–4.4 isolate right cup
//                    4.4–8.0 driver-stack tower · 8.0–9.0 snap back together · 9.0–10 hero hold
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const W = 1080, H = 1920;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const eout = x => { x = clamp(x); return 1 - Math.pow(1 - x, 3); };
let seed = 7; const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

// ---------- renderer
const canvas = document.createElement('canvas'); canvas.width = W; canvas.height = H;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = .82;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x000000);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
scene.environmentIntensity = .5;
const key = new THREE.DirectionalLight(0xfff1dc, 1.7); key.position.set(8, 14, 12); scene.add(key);
const rim = new THREE.DirectionalLight(0xffd9a0, 3.2); rim.position.set(-10, 6, -10); scene.add(rim);
const fill = new THREE.DirectionalLight(0xbfcfff, .5); fill.position.set(-8, -4, 10); scene.add(fill);
const camera = new THREE.PerspectiveCamera(26, W / H, .1, 600);
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), .28, .45, .93));
composer.addPass(new OutputPass());

// ---------- procedural textures
function tex(w, h, draw, repeat) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); }
  return t;
}
const fabricTex = tex(512, 512, (x, w, h) => {
  x.fillStyle = '#7c756b'; x.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 4) for (let i = 0; i < w; i += 4) {
    const v = 104 + rand() * 30 + (((i + y) / 4) % 2 ? 12 : -12); x.fillStyle = `rgb(${v + 8},${v + 2},${v - 8})`; x.fillRect(i, y, 4, 2);
  }
}, [10, 1]);
const leatherTex = tex(512, 512, (x, w, h) => {
  x.fillStyle = '#2d2c2b'; x.fillRect(0, 0, w, h);
  for (let i = 0; i < 9000; i++) {
    const v = 30 + rand() * 26; x.fillStyle = `rgba(${v},${v},${v - 2},.7)`;
    x.beginPath(); x.ellipse(rand() * w, rand() * h, 1 + rand() * 4, 1 + rand() * 3, rand() * 3, 0, 7); x.fill();
  }
}, [6, 2]);
const meshTex = tex(256, 256, (x, w, h) => {
  x.fillStyle = '#18181a'; x.fillRect(0, 0, w, h); x.fillStyle = '#3a3a3e';
  for (let y = 4; y < h; y += 8) for (let i = (y / 8 % 2) * 4 + 4; i < w; i += 8) { x.beginPath(); x.arc(i, y, 2.2, 0, 7); x.fill(); }
}, [5, 5]);
const pcbTex = tex(1024, 1024, (x, w, h) => {
  x.fillStyle = '#0c2219'; x.fillRect(0, 0, w, h);
  x.strokeStyle = '#c9a463'; x.lineCap = 'round';
  for (let i = 0; i < 160; i++) {
    let px = rand() * w, py = rand() * h; x.lineWidth = 2 + rand() * 4; x.globalAlpha = .55 + rand() * .4; x.beginPath(); x.moveTo(px, py);
    for (let k = 0; k < 4; k++) { if (rand() > .5) px += (rand() - .5) * 300; else py += (rand() - .5) * 300; x.lineTo(px, py); }
    x.stroke(); x.fillStyle = '#e2bf7d'; x.beginPath(); x.arc(px, py, 6, 0, 7); x.fill();
  }
  x.globalAlpha = 1; x.fillStyle = 'rgba(255,255,255,.75)'; x.font = '600 34px sans-serif'; x.textAlign = 'center';
  x.fillText('SILENCE ONE  ·  ANC-H2', w / 2, h * .8);
});
const batteryTex = tex(1024, 640, (x, w, h) => {
  x.fillStyle = '#2b3036'; x.fillRect(0, 0, w, h);
  x.fillStyle = '#d8b783'; x.fillRect(0, h * .72, w, 18);
  x.fillStyle = '#e9e6df'; x.textAlign = 'left'; x.font = '600 84px sans-serif'; x.fillText('SILENCE CELL', 70, 200);
  x.font = '400 50px sans-serif'; x.fillStyle = '#a9adb3'; x.fillText('Li-ion  3.85 V  ·  40 h', 70, 300); x.fillText('Made for silence', 70, 380);
});

// ---------- materials
const MAT = {
  stone: new THREE.MeshPhysicalMaterial({ color: 0x9d9488, roughness: .52, metalness: .05, clearcoat: .25, clearcoatRoughness: .4 }),
  gold: new THREE.MeshPhysicalMaterial({ color: 0xdcb98a, metalness: 1, roughness: .2 }),
  fabric: new THREE.MeshStandardMaterial({ map: fabricTex, bumpMap: fabricTex, bumpScale: 1.2, roughness: .95 }),
  leather: new THREE.MeshStandardMaterial({ map: leatherTex, bumpMap: leatherTex, bumpScale: 1.5, roughness: .6 }),
  titanium: new THREE.MeshPhysicalMaterial({ color: 0xb3ada3, metalness: .95, roughness: .3, side: THREE.DoubleSide }),
  copper: new THREE.MeshStandardMaterial({ color: 0xc27a43, metalness: 1, roughness: .3, side: THREE.DoubleSide }),
  magnet: new THREE.MeshStandardMaterial({ color: 0x8e9197, metalness: 1, roughness: .22 }),
  mesh: new THREE.MeshStandardMaterial({ map: meshTex, roughness: .9 }),
  pcb: new THREE.MeshStandardMaterial({ map: pcbTex, roughness: .45, metalness: .25 }),
  pcbEdge: new THREE.MeshStandardMaterial({ color: 0x14302a, roughness: .6 }),
  chip: new THREE.MeshStandardMaterial({ color: 0x0b0b0c, roughness: .3, metalness: .4 }),
  battery: new THREE.MeshStandardMaterial({ map: batteryTex, roughness: .5, metalness: .15 }),
  batEdge: new THREE.MeshStandardMaterial({ color: 0x23272c, roughness: .5, metalness: .2 }),
};
const FADERS = [];  // every material instance, so whole groups can fade
const M = m => { const c = m.clone(); FADERS.push(c); return c; };
function setOpacity(obj, a) {
  obj.traverse(o => { if (!o.material) return; (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => {
    m.opacity = a; m.transparent = a < .999; m.depthWrite = a > .5; }); o.visible = a > .01; });
}
const V2 = (x, y) => new THREE.Vector2(x, y);

// ---------- ear cup (local +Y = outward axis; oval along local X)
function earCup() {
  const g = new THREE.Group(), parts = {};
  const add = (name, obj, y0, y1, label) => { obj.userData = { y0, y1, r: obj.userData.r || 3.6 }; obj.position.y = y0; g.add(obj); parts[name] = obj; };
  // shell
  const shell = new THREE.Mesh(new THREE.LatheGeometry([V2(0, .95), V2(1.4, .9), V2(2.6, .7), V2(3.4, .42), V2(3.85, .12), V2(3.97, -.12), V2(3.97, -.34), V2(3.75, -.36)], 128), M(MAT.stone));
  shell.material.side = THREE.DoubleSide; shell.scale.set(1.2, 1, 1); shell.userData.r = 4.6;
  add('shell', shell, 0, 7.8);
  // champagne ring (+ two ANC mic ports)
  const ringG = new THREE.TorusGeometry(3.99, .13, 20, 160); ringG.rotateX(Math.PI / 2);
  const ring = new THREE.Mesh(ringG, M(MAT.gold)); ring.scale.set(1.2, 1, 1); ring.userData.r = 4.8;
  [-.6, .6].forEach(a => { const mic = new THREE.Mesh(new THREE.CylinderGeometry(.16, .16, .14, 24), M(MAT.chip)); mic.position.set(Math.cos(a) * 3.99, .06, Math.sin(a) * 3.99); ring.add(mic); });
  add('ring', ring, -.2, 5.9);
  // logic board
  const pcbG = new THREE.CylinderGeometry(2.9, 2.9, .08, 96);
  const pcb = new THREE.Mesh(pcbG, [M(MAT.pcbEdge), M(MAT.pcb), M(MAT.pcbEdge)]); pcb.scale.set(1.12, 1, 1); pcb.userData.r = 3.3;
  [[0, 0, 1.0, .9], [1.4, .6, .5, .5], [-1.3, -.7, .6, .4], [.9, -1.2, .35, .35], [-1.5, .9, .3, .45]].forEach(([x, z, w, d]) => {
    const c = new THREE.Mesh(new THREE.BoxGeometry(w, .14, d), M(MAT.chip)); c.position.set(x, .1, z); pcb.add(c); });
  add('pcb', pcb, -.45, 4.1);
  // battery
  const bat = new THREE.Mesh(new THREE.BoxGeometry(3.3, .42, 2.05), [M(MAT.batEdge), M(MAT.batEdge), M(MAT.battery), M(MAT.batEdge), M(MAT.batEdge), M(MAT.batEdge)]);
  bat.userData.r = 1.7; add('battery', bat, -.8, 2.5);
  // magnet assembly
  const mag = new THREE.Group();
  mag.add(new THREE.Mesh(new THREE.CylinderGeometry(1.35, 1.35, .55, 96), M(MAT.magnet)));
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(1.42, 1.42, .07, 96), M(MAT.titanium)); plate.position.y = .31; mag.add(plate);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(.55, .55, .25, 64), M(MAT.gold)); pole.position.y = .45; mag.add(pole);
  mag.userData.r = 1.45; add('magnet', mag, -1.15, .9);
  // voice coil
  const coil = new THREE.Group();
  coil.add(new THREE.Mesh(new THREE.CylinderGeometry(.8, .8, .5, 64, 1, true), M(MAT.copper)));
  for (let i = 0; i < 7; i++) { const w = new THREE.Mesh(new THREE.TorusGeometry(.81, .028, 8, 64), M(MAT.copper)); w.rotation.x = Math.PI / 2; w.position.y = -.2 + i * .066; coil.add(w); }
  coil.userData.r = .9; add('coil', coil, -1.35, -.55);
  // 40 mm driver diaphragm
  const dia = new THREE.Group();
  dia.add(new THREE.Mesh(new THREE.LatheGeometry([V2(0, .36), V2(.35, .34), V2(.6, .28), V2(1.1, .18), V2(1.7, .07), V2(2.05, 0), V2(2.15, .06), V2(2.26, 0)], 96), M(MAT.titanium)));
  const cap = new THREE.Mesh(new THREE.SphereGeometry(.62, 48, 16, 0, Math.PI * 2, 0, Math.PI / 3.2), M(MAT.gold)); cap.position.y = -.17; dia.add(cap);
  dia.userData.r = 2.3; add('driver', dia, -1.5, -2.05);
  // acoustic mesh + frame
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(3.5, 3.5, .1, 128), M(MAT.mesh)); mesh.scale.set(1.2, 1, 1);
  const fr = new THREE.Mesh(new THREE.TorusGeometry(3.5, .07, 10, 128), M(MAT.gold)); fr.rotation.x = Math.PI / 2; mesh.add(fr);
  mesh.userData.r = 4.2; add('mesh', mesh, -1.65, -3.6);
  // memory-foam cushion
  const cg = new THREE.TorusGeometry(3.05, .88, 32, 160); cg.rotateX(Math.PI / 2);
  const cush = new THREE.Mesh(cg, M(MAT.leather)); cush.scale.set(1.2, .85, 1); cush.userData.r = 4.7;
  add('cushion', cush, -2.2, -5.7);
  g.userData.parts = parts;
  return g;
}
function explodeCup(cup, e) { Object.values(cup.userData.parts).forEach(p => { p.position.y = lerp(p.userData.y0, p.userData.y1, e); }); }

// ---------- assemble the product
const product = new THREE.Group(); scene.add(product);
const R_ARC = 8.1, A0 = .17, A1 = Math.PI - .17;
class Arc extends THREE.Curve { getPoint(u, o = new THREE.Vector3()) { const a = lerp(A0, A1, u); return o.set(Math.cos(a) * R_ARC, Math.sin(a) * R_ARC, 0); } }
const coreG = new THREE.TubeGeometry(new Arc(), 160, .2, 16); const core = new THREE.Mesh(coreG, M(MAT.gold)); core.scale.z = 4.2;
const sleeveG = new THREE.TubeGeometry(new Arc(), 200, .62, 32); const sleeve = new THREE.Mesh(sleeveG, M(MAT.fabric)); sleeve.scale.z = 2.0;
const band = new THREE.Group(); band.add(core); band.add(sleeve); product.add(band);
const sliders = [-1, 1].map(s => {
  const g = new THREE.Group();
  const rod = new THREE.Mesh(new THREE.CylinderGeometry(.3, .3, 2.4, 32), M(MAT.gold)); g.add(rod);
  const cap = new THREE.Mesh(new THREE.CylinderGeometry(.45, .45, .5, 32), M(MAT.gold)); cap.position.y = 1.3; g.add(cap);
  const pivot = new THREE.Mesh(new THREE.SphereGeometry(.42, 32, 16), M(MAT.gold)); pivot.position.y = -1.3; g.add(pivot);
  g.position.set(s * 7.95, .1, 0); product.add(g); return g;
});
const cups = [-1, 1].map(s => { const c = earCup(); c.rotation.z = -s * Math.PI / 2; c.position.set(s * 7.4, -4.5, 0); product.add(c); return c; });
const [cupL, cupR] = cups;
product.position.y = 1.5;

// ---------- choreography
const tmp = new THREE.Vector3();
function proj(obj, local) {
  tmp.copy(local).applyMatrix4(obj.matrixWorld).project(camera);
  return [(tmp.x * .5 + .5) * W, (-tmp.y * .5 + .5) * H, tmp.z < 1];
}
function render(lt) {
  const ex1 = eio(seg(lt, 1.3, 3.2)) * (1 - eio(seg(lt, 8.0, 8.9)));        // global explode
  const iso = eio(seg(lt, 3.4, 4.4)) * (1 - eio(seg(lt, 7.9, 8.7)));        // isolate right cup
  const ex2 = eio(seg(lt, 4.3, 6.2)) * (1 - eio(seg(lt, 7.9, 8.6)));        // driver-stack tower
  // global explode
  sleeve.position.y = 2.6 * ex1; core.position.y = .5 * ex1;
  sliders.forEach((g, i) => { const s = i ? 1 : -1; g.position.set(s * (7.95 + 1.2 * ex1), .1 - .6 * ex1, 0); });
  cups.forEach((c, i) => { const s = i ? 1 : -1; c.position.set(s * (7.4 + 2.2 * ex1), -4.5 - 1.4 * ex1, 0); explodeCup(c, .22 * ex1); });
  // isolate: right cup flies to centre, turns its axis upward and tilts toward camera
  cupR.position.set(lerp(cupR.position.x, 0, iso), lerp(cupR.position.y, -1.6, iso), 0);
  cupR.rotation.set(lerp(0, .42, iso), lerp(0, .5 * Math.sin(lt * .6), iso * ex2), lerp(-Math.PI / 2, 0, iso));
  explodeCup(cupR, lerp(.22 * ex1, 1, ex2));
  const rest = (1 - eio(seg(lt, 3.35, 3.75))) + eio(seg(lt, 8.35, 8.8));
  [band, cupL, ...sliders].forEach(o => setOpacity(o, clamp(rest)));
  // camera: 3/4 hero → wide explode → tower close-up → back
  const az = lerp(.62, .82, seg(lt, 0, 3.4)) + .1 * Math.sin(lt * .4);
  const dist = lerp(lerp(84, 100, ex1), 66, iso), el = lerp(.12, .2, ex1);
  const tgt = new THREE.Vector3(0, lerp(1.0, -1.0, iso), 0);
  const a = lerp(az, .18, iso);
  camera.position.set(tgt.x + Math.sin(a) * Math.cos(el) * dist, tgt.y + Math.sin(el) * dist + lerp(0, 4, iso), tgt.z + Math.cos(a) * Math.cos(el) * dist);
  camera.lookAt(tgt);
  product.rotation.y = .05 * Math.sin(lt * .5);
  scene.updateMatrixWorld(); camera.updateMatrixWorld();
  composer.render();
  // label anchors (screen px)
  const P = cupR.userData.parts, an = {};
  ['shell', 'ring', 'pcb', 'battery', 'magnet', 'coil', 'driver', 'mesh', 'cushion'].forEach((n, i) => {
    const s = i % 2 ? -1 : 1; an[n] = proj(P[n], tmp.set(s * P[n].userData.r, 0, 0).clone());
  });
  an.sleeve = proj(sleeve, new THREE.Vector3(Math.cos(1.2) * R_ARC, Math.sin(1.2) * R_ARC + .6, 0));
  an.core = proj(core, new THREE.Vector3(Math.cos(2.1) * R_ARC, Math.sin(2.1) * R_ARC, 0));
  an.cushionL = proj(cupL.userData.parts.cushion, new THREE.Vector3(0, -.6, 3.6));
  an.slider = proj(sliders[1], new THREE.Vector3(0, 0, 0));
  return { ex1, iso, ex2, an };
}

window.TD = { canvas, render };
