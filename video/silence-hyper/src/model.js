// SILENCE ONE — procedural headphone model (three.js). Every call to createHeadphone() builds an independent instance.
//
//   const hp = createHeadphone();  scene.add(hp.root);
//   hp.explode(e)            0..1 global explode (sleeve lifts, sliders extend, cups drop and open a little)
//   hp.explodeCup(cup, e)    0..1 spreads one cup's 9 layers along its own axis (local +Y = outward)
//   hp.cups[0|1]             left / right cup groups; cup.userData.parts = { shell, ring, pcb, battery, magnet, coil, driver, mesh, cushion }
//   hp.band.sleeve / hp.band.core / hp.sliders[0|1]
//   hp.setOpacity(obj, a)    fades any sub-tree (clones materials per instance, so instances are independent)
//   hp.sample(n)             -> { positions: Float32Array(n*3), colors: Float32Array(n*3) } points on the assembled surface
//                              (model space of hp.root), for particle effects
// Assembled size: ~19.5 units wide, ~17 units tall, centred near the origin (y from about -8.6 to +10).
import * as THREE from 'three';
import { MeshSurfaceSampler } from 'three/addons/math/MeshSurfaceSampler.js';

const lerp = (a, b, k) => a + (b - a) * k;
let seed = 7; const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

function tex(w, h, draw, repeat) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); }
  return t;
}
let TEX = null;
function textures() {
  if (TEX) return TEX;
  TEX = {
    fabric: tex(512, 512, (x, w, h) => {
      x.fillStyle = '#7c756b'; x.fillRect(0, 0, w, h);
      for (let y = 0; y < h; y += 4) for (let i = 0; i < w; i += 4) {
        const v = 104 + rand() * 30 + (((i + y) / 4) % 2 ? 12 : -12); x.fillStyle = `rgb(${v + 8},${v + 2},${v - 8})`; x.fillRect(i, y, 4, 2);
      }
    }, [10, 1]),
    leather: tex(512, 512, (x, w, h) => {
      x.fillStyle = '#2d2c2b'; x.fillRect(0, 0, w, h);
      for (let i = 0; i < 9000; i++) {
        const v = 30 + rand() * 26; x.fillStyle = `rgba(${v},${v},${v - 2},.7)`;
        x.beginPath(); x.ellipse(rand() * w, rand() * h, 1 + rand() * 4, 1 + rand() * 3, rand() * 3, 0, 7); x.fill();
      }
    }, [6, 2]),
    mesh: tex(256, 256, (x, w, h) => {
      x.fillStyle = '#18181a'; x.fillRect(0, 0, w, h); x.fillStyle = '#3a3a3e';
      for (let y = 4; y < h; y += 8) for (let i = (y / 8 % 2) * 4 + 4; i < w; i += 8) { x.beginPath(); x.arc(i, y, 2.2, 0, 7); x.fill(); }
    }, [5, 5]),
    pcb: tex(1024, 1024, (x, w, h) => {
      x.fillStyle = '#0c2219'; x.fillRect(0, 0, w, h); x.strokeStyle = '#c9a463'; x.lineCap = 'round';
      for (let i = 0; i < 160; i++) {
        let px = rand() * w, py = rand() * h; x.lineWidth = 2 + rand() * 4; x.globalAlpha = .55 + rand() * .4; x.beginPath(); x.moveTo(px, py);
        for (let k = 0; k < 4; k++) { if (rand() > .5) px += (rand() - .5) * 300; else py += (rand() - .5) * 300; x.lineTo(px, py); }
        x.stroke(); x.fillStyle = '#e2bf7d'; x.beginPath(); x.arc(px, py, 6, 0, 7); x.fill();
      }
      x.globalAlpha = 1; x.fillStyle = 'rgba(255,255,255,.75)'; x.font = '600 34px sans-serif'; x.textAlign = 'center';
      x.fillText('SILENCE ONE  ·  ANC-H2', w / 2, h * .8);
    }),
    battery: tex(1024, 640, (x, w, h) => {
      x.fillStyle = '#2b3036'; x.fillRect(0, 0, w, h); x.fillStyle = '#d8b783'; x.fillRect(0, h * .72, w, 18);
      x.fillStyle = '#e9e6df'; x.textAlign = 'left'; x.font = '600 84px sans-serif'; x.fillText('SILENCE CELL', 70, 200);
      x.font = '400 50px sans-serif'; x.fillStyle = '#a9adb3'; x.fillText('Li-ion  3.85 V  ·  40 h', 70, 300); x.fillText('Made for silence', 70, 380);
    }),
  };
  return TEX;
}
let BASE = null;
export function materials() {
  if (BASE) return BASE;
  const T = textures();
  BASE = {
    stone: new THREE.MeshPhysicalMaterial({ color: 0x9d9488, roughness: .52, metalness: .05, clearcoat: .25, clearcoatRoughness: .4 }),
    gold: new THREE.MeshPhysicalMaterial({ color: 0xdcb98a, metalness: 1, roughness: .2 }),
    fabric: new THREE.MeshStandardMaterial({ map: T.fabric, bumpMap: T.fabric, bumpScale: 1.2, roughness: .95 }),
    leather: new THREE.MeshStandardMaterial({ map: T.leather, bumpMap: T.leather, bumpScale: 1.5, roughness: .6 }),
    titanium: new THREE.MeshPhysicalMaterial({ color: 0xb3ada3, metalness: .95, roughness: .3, side: THREE.DoubleSide }),
    copper: new THREE.MeshStandardMaterial({ color: 0xc27a43, metalness: 1, roughness: .3, side: THREE.DoubleSide }),
    magnet: new THREE.MeshStandardMaterial({ color: 0x8e9197, metalness: 1, roughness: .22 }),
    mesh: new THREE.MeshStandardMaterial({ map: T.mesh, roughness: .9 }),
    pcb: new THREE.MeshStandardMaterial({ map: T.pcb, roughness: .45, metalness: .25 }),
    pcbEdge: new THREE.MeshStandardMaterial({ color: 0x14302a, roughness: .6 }),
    chip: new THREE.MeshStandardMaterial({ color: 0x0b0b0c, roughness: .3, metalness: .4 }),
    battery: new THREE.MeshStandardMaterial({ map: T.battery, roughness: .5, metalness: .15 }),
    batEdge: new THREE.MeshStandardMaterial({ color: 0x23272c, roughness: .5, metalness: .2 }),
  };
  return BASE;
}
// representative particle colours (sRGB) per material
const SAMPLE_COL = { stone: 0xb5ab9c, gold: 0xe6c896, fabric: 0x8f877c, leather: 0x3a3836 };

const V2 = (x, y) => new THREE.Vector2(x, y);
export function setOpacity(obj, a) {
  obj.traverse(o => {
    if (!o.material) return;
    (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => { m.opacity = a; m.transparent = a < .999; m.depthWrite = a > .5; });
    o.visible = a > .01;
  });
}

export function createHeadphone() {
  const B = materials();
  const M = m => m.clone();
  const tagged = [];  // [mesh, kind] for surface sampling (assembled outer surfaces only)
  function earCup() {
    const g = new THREE.Group(), parts = {};
    const add = (name, obj, y0, y1) => { obj.userData = { y0, y1, r: obj.userData.r || 3.6, name }; obj.position.y = y0; g.add(obj); parts[name] = obj; };
    const shell = new THREE.Mesh(new THREE.LatheGeometry([V2(0, .95), V2(1.4, .9), V2(2.6, .7), V2(3.4, .42), V2(3.85, .12), V2(3.97, -.12), V2(3.97, -.34), V2(3.75, -.36)], 128), M(B.stone));
    shell.material.side = THREE.DoubleSide; shell.scale.set(1.2, 1, 1); shell.userData.r = 4.6; add('shell', shell, 0, 7.8); tagged.push([shell, 'stone']);
    const ringG = new THREE.TorusGeometry(3.99, .13, 20, 160); ringG.rotateX(Math.PI / 2);
    const ring = new THREE.Mesh(ringG, M(B.gold)); ring.scale.set(1.2, 1, 1); ring.userData.r = 4.8;
    [-.6, .6].forEach(a => { const mic = new THREE.Mesh(new THREE.CylinderGeometry(.16, .16, .14, 24), M(B.chip)); mic.position.set(Math.cos(a) * 3.99, .06, Math.sin(a) * 3.99); ring.add(mic); });
    add('ring', ring, -.2, 5.9); tagged.push([ring, 'gold']);
    const pcb = new THREE.Mesh(new THREE.CylinderGeometry(2.9, 2.9, .08, 96), [M(B.pcbEdge), M(B.pcb), M(B.pcbEdge)]); pcb.scale.set(1.12, 1, 1); pcb.userData.r = 3.3;
    [[0, 0, 1.0, .9], [1.4, .6, .5, .5], [-1.3, -.7, .6, .4], [.9, -1.2, .35, .35], [-1.5, .9, .3, .45]].forEach(([x, z, w, d]) => {
      const c = new THREE.Mesh(new THREE.BoxGeometry(w, .14, d), M(B.chip)); c.position.set(x, .1, z); pcb.add(c); });
    add('pcb', pcb, -.45, 4.1);
    const bat = new THREE.Mesh(new THREE.BoxGeometry(3.3, .42, 2.05), [M(B.batEdge), M(B.batEdge), M(B.battery), M(B.batEdge), M(B.batEdge), M(B.batEdge)]);
    bat.userData.r = 1.7; add('battery', bat, -.8, 2.5);
    const mag = new THREE.Group();
    mag.add(new THREE.Mesh(new THREE.CylinderGeometry(1.35, 1.35, .55, 96), M(B.magnet)));
    const plate = new THREE.Mesh(new THREE.CylinderGeometry(1.42, 1.42, .07, 96), M(B.titanium)); plate.position.y = .31; mag.add(plate);
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(.55, .55, .25, 64), M(B.gold)); pole.position.y = .45; mag.add(pole);
    mag.userData.r = 1.45; add('magnet', mag, -1.15, .9);
    const coil = new THREE.Group();
    coil.add(new THREE.Mesh(new THREE.CylinderGeometry(.8, .8, .5, 64, 1, true), M(B.copper)));
    for (let i = 0; i < 7; i++) { const w = new THREE.Mesh(new THREE.TorusGeometry(.81, .028, 8, 64), M(B.copper)); w.rotation.x = Math.PI / 2; w.position.y = -.2 + i * .066; coil.add(w); }
    coil.userData.r = .9; add('coil', coil, -1.35, -.55);
    const dia = new THREE.Group();
    dia.add(new THREE.Mesh(new THREE.LatheGeometry([V2(0, .36), V2(.35, .34), V2(.6, .28), V2(1.1, .18), V2(1.7, .07), V2(2.05, 0), V2(2.15, .06), V2(2.26, 0)], 96), M(B.titanium)));
    const cap = new THREE.Mesh(new THREE.SphereGeometry(.62, 48, 16, 0, Math.PI * 2, 0, Math.PI / 3.2), M(B.gold)); cap.position.y = -.17; dia.add(cap);
    dia.userData.r = 2.3; add('driver', dia, -1.5, -2.05);
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(3.5, 3.5, .1, 128), M(B.mesh)); mesh.scale.set(1.2, 1, 1);
    const fr = new THREE.Mesh(new THREE.TorusGeometry(3.5, .07, 10, 128), M(B.gold)); fr.rotation.x = Math.PI / 2; mesh.add(fr);
    mesh.userData.r = 4.2; add('mesh', mesh, -1.65, -3.6);
    const cg = new THREE.TorusGeometry(3.05, .88, 32, 160); cg.rotateX(Math.PI / 2);
    const cush = new THREE.Mesh(cg, M(B.leather)); cush.scale.set(1.2, .85, 1); cush.userData.r = 4.7; add('cushion', cush, -2.2, -5.7); tagged.push([cush, 'leather']);
    g.userData.parts = parts;
    return g;
  }
  const root = new THREE.Group();
  const R_ARC = 8.1, A0 = .17, A1 = Math.PI - .17;
  class Arc extends THREE.Curve { getPoint(u, o = new THREE.Vector3()) { const a = lerp(A0, A1, u); return o.set(Math.cos(a) * R_ARC, Math.sin(a) * R_ARC, 0); } }
  const core = new THREE.Mesh(new THREE.TubeGeometry(new Arc(), 160, .2, 16), M(B.gold)); core.scale.z = 4.2;
  const sleeve = new THREE.Mesh(new THREE.TubeGeometry(new Arc(), 200, .62, 32), M(B.fabric)); sleeve.scale.z = 2.0; tagged.push([sleeve, 'fabric']);
  const bandG = new THREE.Group(); bandG.add(core); bandG.add(sleeve); root.add(bandG);
  const sliders = [-1, 1].map(s => {
    const g = new THREE.Group();
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(.3, .3, 2.4, 32), M(B.gold)); g.add(rod); tagged.push([rod, 'gold']);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(.45, .45, .5, 32), M(B.gold)); cap.position.y = 1.3; g.add(cap);
    const pivot = new THREE.Mesh(new THREE.SphereGeometry(.42, 32, 16), M(B.gold)); pivot.position.y = -1.3; g.add(pivot);
    g.position.set(s * 7.95, .1, 0); root.add(g); return g;
  });
  const cups = [-1, 1].map(s => { const c = earCup(); c.rotation.z = -s * Math.PI / 2; c.position.set(s * 7.4, -4.5, 0); c.userData.side = s; root.add(c); return c; });

  function explodeCup(cup, e) { Object.values(cup.userData.parts).forEach(p => { p.position.y = lerp(p.userData.y0, p.userData.y1, e); }); }
  function explode(e, cupSpread = .22) {
    sleeve.position.y = 2.6 * e; core.position.y = .5 * e;
    sliders.forEach((g, i) => { const s = i ? 1 : -1; g.position.set(s * (7.95 + 1.2 * e), .1 - .6 * e, 0); });
    cups.forEach((c, i) => { const s = i ? 1 : -1; c.position.set(s * (7.4 + 2.2 * e), -4.5 - 1.4 * e, 0); c.rotation.set(0, 0, -s * Math.PI / 2); explodeCup(c, cupSpread * e); });
  }
  function sample(n) {
    explode(0); root.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(root.matrixWorld).invert();
    // weight meshes by rough surface area
    const items = tagged.map(([m, kind]) => {
      const g = m.geometry.clone(); g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, m.matrixWorld));
      const mm = new THREE.Mesh(g); const s = new MeshSurfaceSampler(mm).build();
      let area = 0; const p = g.attributes.position, idx = g.index; const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
      const tri = idx ? idx.count / 3 : p.count / 3;
      for (let i = 0; i < tri; i++) {
        const i0 = idx ? idx.getX(i * 3) : i * 3, i1 = idx ? idx.getX(i * 3 + 1) : i * 3 + 1, i2 = idx ? idx.getX(i * 3 + 2) : i * 3 + 2;
        a.fromBufferAttribute(p, i0); b.fromBufferAttribute(p, i1); c.fromBufferAttribute(p, i2);
        area += b.sub(a).cross(c.sub(a)).length() / 2;
      }
      return { s, kind, area };
    });
    const total = items.reduce((q, it) => q + it.area, 0);
    const positions = new Float32Array(n * 3), colors = new Float32Array(n * 3); const v = new THREE.Vector3(), col = new THREE.Color();
    let k = 0;
    items.forEach((it, j) => {
      const cnt = j === items.length - 1 ? n - k : Math.round(n * it.area / total);
      col.setHex(SAMPLE_COL[it.kind]);
      for (let i = 0; i < cnt && k < n; i++, k++) { it.s.sample(v); positions.set([v.x, v.y, v.z], k * 3); colors.set([col.r, col.g, col.b], k * 3); }
    });
    return { positions, colors };
  }
  explode(0);
  return { root, band: { group: bandG, sleeve, core }, sliders, cups, explode, explodeCup, setOpacity, sample, R_ARC };
}
