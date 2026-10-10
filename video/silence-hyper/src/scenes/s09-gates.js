// s09-gates — GATE RUN (b48-56): wearing the corridor.
// b48 match cut: the acoustic-mesh dots of s08 blast outward as warp streaks and reveal a receding SPIRAL CORRIDOR of
// complete SILENCE ONE headphones (8 gates, 24 units apart, each one turned 30° further than the last, exp fog to ink), all
// converging on a gold vanishing-point glow. The camera does not drift through them at a constant speed: on every beat it
// HOLDS (slow creep, the next gate framed complete with 3-5 smaller gates receding behind it), then RUSHES through the
// band opening in the last ~4 frames, so each gate pass lands on the beat (b49 ... b56 = exit into s10). The camera rolls
// 0 -> 180° on a ratchet. Gates use the one product look (stone-grey shells, champagne-gold PBR metal, charcoal cushions,
// greige band); the warm / cool alternation is done with LIGHT colour only (#ffe2b0 vs neutral #d4d5d6).
// Spec slams b48/50/52/54 (slot-machine Anton numerals + gold Unbounded units + Instrument Serif descriptors) are drawn
// on fg, below the corridor, bloom-free and razor sharp; each descriptor is complete by +0.75 beat and held to +1.83.
//
// Layers: bg2d ink + gold vanishing-point glow (beat-pulsed, opens up at the exit)
//         3D   8 headphone gates (internal parts hidden, exp fog to ink, per-gate parity light) + 300 additive spiral streaks
//         fg2d the b48 mesh-dot burst, the spec slams, the staircase HUD.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, rnd, noise1, text, measure, font, COL, FONT, ADDITIVE } from '../lib.js';
import { createHeadphone } from '../model.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const B0 = 48, B1 = 56;
const DEG = Math.PI / 180;
const FOV = 78;                       // vertical
const VPY = 790;                      // vanishing point (screen y): the corridor lives in the upper 2/3, the type below it
const S = 24;                         // gate spacing (units) = camera travel per beat
const OFF = 6;                        // on each downbeat the camera is OFF units past the gate it just went through
const NG = 8;                         // gates k = 1..8 (gate k is passed ~1 frame before beat 48 + k)
const GS = .5;                         // gate scale (~11.7 units wide): ~9.75 units wide: complete in frame from d >= ~11
const PIV = -2.2;                     // model-space y that sits on the flight axis (between the cups, under the band)
const YAW = 0;
const TWIST = 30;                     // each gate is turned 30° further than the previous one: a spiral, not a cross
const NUM = 380;                      // Anton numeral size
const BASE = 1330;                    // numeral baseline (screen y)
const DESC_Y = 1452, DESC_SIZE = 84;  // serif descriptor baseline / size
const SY0 = 900, SH = 640;            // the spec canvas covers screen y SY0 .. SY0+SH
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
// #eeebe4 = .855 linear: under the .91 knee, so the slams get no bloom halo (#f6f3ec at .92 would, over its huge area)
const TYPE_WHITE = '#eeebe4';
const KEY_WARM = lin('#ffe2b0'), KEY_COOL = lin('#d4d5d6');

// order chosen so every slam visibly changes number: 40 h -> 250 g -> 40 mm -> 360°
const SPECS = [
  { b: 48, num: '40', unit: 'h', desc: 'of battery' },
  { b: 50, num: '250', unit: 'g', desc: 'of almost nothing' },
  { b: 52, num: '40', unit: 'mm', desc: 'titanium driver' },
  { b: 54, num: '360', unit: '°', desc: 'spatial audio' },
];
const NOTES = ['D4', 'E4', 'F4', 'G4', 'A4', 'B♭4', 'C5', 'D5'];

// camera travel (units down -Z) at beat b: hold (slow creep) then rush through the next gate on the beat
const ease = f => .22 * f + .78 * f * f * f * f;
function camDist(b) {
  const x = clamp(b - B0, 0, 8), n = Math.floor(x), f = x - n;
  return S * (n + ease(f)) + OFF;
}
const gateZ = k => -S * k;
// camera roll: 0 -> 180° over the scene; ~45 % of every 22.5° step snaps in on the beat (ratchet), the rest glides
function rollAt(b) {
  const x = clamp(b - B0, 0, 8), n = Math.floor(x), f = x - n;
  const step = .55 * f + .45 * expoOut(f * 3.2);
  return -(n + step) * 22.5 * DEG;
}

// ------------------------------------------------------------------ streaks (own instanced system: per-instance colour, helix)
function buildStreaks(n) {
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mat = new THREE.MeshBasicMaterial({ ...ADDITIVE, color: 0xffffff, fog: true });
  const mesh = new THREE.InstancedMesh(geo, mat, n); mesh.frustumCulled = false; mesh.renderOrder = 1;
  // glow sleeve: a soft additive ribbon around every streak (tangential width x length, gaussian across, soft ends).
  // A 2 px streak carries too little energy for the post bloom to show a halo, so the glow is built in 3D.
  const gc = document.createElement('canvas'); gc.width = 64; gc.height = 64;
  { const x = gc.getContext('2d'), id = x.createImageData(64, 64);
    for (let j = 0; j < 64; j++) for (let i = 0; i < 64; i++) {
      const v = (j + .5) / 32 - 1, u = (i + .5) / 64;
      const a = (.62 * Math.exp(-v * v * 30) + .38 * Math.exp(-v * v * 6)) * (1 - v * v) * Math.min(1, u / .25, (1 - u) / .12);   // hot core + soft tail
      const o = (j * 64 + i) * 4; id.data[o] = id.data[o + 1] = id.data[o + 2] = 255; id.data[o + 3] = Math.round(255 * a);
    }
    x.putImageData(id, 0, 0); }
  const gtex = new THREE.CanvasTexture(gc); gtex.colorSpace = THREE.NoColorSpace;
  const ggeo = new THREE.PlaneGeometry(1, 1); ggeo.rotateY(Math.PI / 2);         // spans local y (tangent) x z, faces the axis
  const glow = new THREE.InstancedMesh(ggeo, new THREE.MeshBasicMaterial({ ...ADDITIVE, map: gtex, color: 0xffffff, fog: true, side: THREE.DoubleSide }), n);
  glow.frustumCulled = false; glow.renderOrder = 1; mesh.add(glow);
  const gold = lin(COL.gold), goldHi = lin(COL.goldHi), white = lin(COL.white), c = new THREE.Color();
  const base = [];
  for (let i = 0; i < n; i++) {
    const kind = rnd(i * 4.7 + 1.3);
    const col = kind < .62 ? gold : kind < .85 ? goldHi : white;
    const inten = 3.6 + 3.4 * rnd(i * 6.1 + .2);   // HDR: clears the .93 bright-pass threshold after ACES (the type does not)
    c.copy(col).multiplyScalar(inten); mesh.setColorAt(i, c);
    c.copy(col).multiplyScalar(.2 + .1 * inten / 7); glow.setColorAt(i, c);
    base.push({ a0: rnd(i * 1.1 + .7) * TAU, r: 8 + 10 * Math.sqrt(rnd(i * 2.3 + .4)), z0: rnd(i * 3.7 + .9) * 260, v: 40 + 110 * rnd(i * 5.9 + .3), th: .03 + .045 * rnd(i * 8.3) });
  }
  mesh.instanceColor.needsUpdate = true; glow.instanceColor.needsUpdate = true;
  const d = new THREE.Object3D(), L = 260;
  return {
    mesh,
    // b: beat, cz: camera z, vel: camera speed (units / s), boost: exit speed-up
    update(b, cz, vel, boost) {
      const tau = (b - B0) * BEAT, cd = -cz;
      for (let i = 0; i < n; i++) {
        const s = base[i];
        const rel = 8 - L + ((s.z0 + tau * s.v * boost + cd * 1.15) % L);   // races toward the camera, lurches with each rush
        const z = cz + rel, a = s.a0 + .011 * z;                                // helix in world space -> spirals as we fly
        const len = (s.v * boost * .4 + vel * .9) * .055 + .4;
        const fade = clamp((rel + L - 8) / 40) * clamp((8 - rel) / 4);
        d.position.set(Math.cos(a) * s.r, Math.sin(a) * s.r, z - len / 2);
        d.rotation.set(0, 0, a);
        d.scale.set(s.th * fade + 1e-4, s.th * fade + 1e-4, len); d.updateMatrix(); mesh.setMatrixAt(i, d.matrix);
        d.scale.set(1, s.th * 13 * fade + 1e-4, len * 1.15); d.updateMatrix(); glow.setMatrixAt(i, d.matrix);
      }
      mesh.instanceMatrix.needsUpdate = true; glow.instanceMatrix.needsUpdate = true;
    },
  };
}

// ------------------------------------------------------------------ gates
// Eight full createHeadphone() trees are too heavy on CPU WebGL, so ONE headphone is built and baked into shared merged
// geometries per material family, in two LODs (hi: model resolution; lo: re-tessellated from the geometries' parameters).
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
// ONE product look, identical on every gate (hero.jpg / orbit sprites): stone-grey shell, champagne-gold metal,
// charcoal cushions, greige woven band. Only the lights differ between gates.
function buildMats(kit) {
  return {
    gold: new THREE.MeshStandardMaterial({ color: lin('#dcc7a2'), metalness: 1, roughness: .26, emissive: lin('#f0dcb6'), emissiveIntensity: 0 }),
    stone: new THREE.MeshStandardMaterial({ color: lin('#b0afab'), metalness: .04, roughness: .44, side: THREE.DoubleSide }),
    fabric: new THREE.MeshStandardMaterial({ map: kit.maps.fabric, color: new THREE.Color(1.02, 1.01, 1.0), roughness: .95, metalness: 0 }),
    leather: new THREE.MeshStandardMaterial({ map: kit.maps.leather, color: new THREE.Color(1.05, 1.05, 1.05), roughness: .62, metalness: 0 }),
    mesh: new THREE.MeshLambertMaterial({ map: kit.maps.mesh }),
    dark: new THREE.MeshLambertMaterial({ color: 0x0b0b0c }),
  };
}
function buildGate(k, kit) {
  // one gold material per gate (its emissive flares as it passes); the rest is shared
  const mats = { ...kit.mats, gold: kit.mats.gold.clone() };
  const piv = new THREE.Group(); piv.scale.setScalar(GS);
  piv.position.set(0, 0, gateZ(k));
  const yaw = new THREE.Group(); yaw.rotation.y = YAW * DEG; piv.add(yaw);   // square to the axis: the classic front silhouette
  const meshes = [];
  for (const f of Object.keys(kit.hi)) { const m = new THREE.Mesh(kit.hi[f], mats[f]); m.userData.f = f; m.frustumCulled = false; yaw.add(m); meshes.push(m); }
  return { k, piv, warm: k % 2 === 1, mats, meshes, lod: 'hi', setLod(l) { if (l === this.lod) return; this.lod = l; meshes.forEach(m => { m.geometry = kit[l][m.userData.f]; }); } };
}

// ------------------------------------------------------------------ 2D helpers
function makeCanvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }

// ---- glyph caches (380 px fillText and per-letter blur filters are far too slow per frame on CPU canvas)
const GC = { digits: null, desc: new Map(), plate: null, glow: null, exitGlow: null };
function buildCaches() {
  const m = makeCanvas(8, 8).getContext('2d'); m.font = font(NUM, 400, FONT.impact);
  const asc = Math.ceil(m.measureText('0').actualBoundingBoxAscent), pad = 30;
  GC.asc = asc;
  GC.digits = [...'0123456789'].map(d => {
    const w = Math.ceil(m.measureText(d).width), c = makeCanvas(w + pad * 2, asc + pad * 2);
    const x = c.getContext('2d');
    // baked soft ink shadow: separates the white numeral from a gate crossing behind it, without any glow halo
    x.shadowColor = 'rgba(5,5,6,.6)'; x.shadowBlur = 22; x.shadowOffsetY = 4;
    text(x, d, c.width / 2, asc + pad, { size: NUM, family: FONT.impact, color: TYPE_WHITE });
    return { c, w, pad };
  });
  for (const sp of SPECS) {
    const size = DESC_SIZE; m.font = font(size, 400, FONT.serif, true);
    const ch = [...sp.desc], ws = ch.map(c => m.measureText(c).width);
    const cells = ch.map((c, i) => [0, 2, 4, 7].map(bl => {
      const pd = 30, cv = makeCanvas(Math.ceil(ws[i] + pd * 2 + 24), size + pd * 2);
      const x = cv.getContext('2d');
      if (!bl) { x.shadowColor = 'rgba(5,5,6,.75)'; x.shadowBlur = 14; x.shadowOffsetY = 2; }
      text(x, c, cv.width / 2, size * .8 + pd, { size, family: FONT.serif, italic: true, color: TYPE_WHITE, blur: bl });
      return cv;
    }));
    GC.desc.set(sp.b, { ws, cells, size, pd: 30 });
  }
  // text-safe pool: a soft ink ellipse under the whole spec block (keeps gates / streaks quiet behind the type)
  GC.plate = makeCanvas(W, SH);
  { const x = GC.plate.getContext('2d'), g = x.createRadialGradient(0, 0, 0, 0, 0, 560);
    g.addColorStop(0, 'rgba(5,5,6,.62)'); g.addColorStop(.6, 'rgba(5,5,6,.34)'); g.addColorStop(1, 'rgba(5,5,6,0)');
    x.translate(540, (BASE + DESC_Y) / 2 - 70 - SY0); x.scale(1, .5); x.fillStyle = g; x.fillRect(-560, -560, 1120, 1120); }
  const radial = (r, stops) => { const c = makeCanvas(r * 2, r * 2), x = c.getContext('2d'), g = x.createRadialGradient(r, r, 0, r, r, r);
    stops.forEach(([p, a]) => g.addColorStop(p, a)); x.fillStyle = g; x.fillRect(0, 0, r * 2, r * 2); return c; };
  GC.glow = radial(640, [[0, 'rgba(240,212,160,.85)'], [.12, 'rgba(230,200,150,.5)'], [.38, 'rgba(230,200,150,.18)'], [.7, 'rgba(184,146,90,.05)'], [1, 'rgba(184,146,90,0)']]);
  GC.exitGlow = radial(420, [[0, 'rgba(255,240,214,1)'], [.25, 'rgba(246,224,182,.55)'], [.6, 'rgba(230,200,150,.12)'], [1, 'rgba(230,200,150,0)']]);
}

// spec layout (number + unit centred as one block)
function layout(sp) {
  if (sp._L) return sp._L;
  const m = makeCanvas(8, 8).getContext('2d');
  const ds = [...sp.num].map(d => GC.digits[+d]);
  const wN = ds.reduce((a, d) => a + d.w, 0) + 6 * (ds.length - 1);
  const deg = sp.unit === '°', uSize = deg ? 160 : 104;
  const wU = measure(m, sp.unit, uSize, 700, FONT.display);
  const gap = deg ? 8 : 18;
  const x0 = Math.round(540 - (wN + gap + wU) / 2);
  return (sp._L = { ds, wN, wU, gap, x0, uSize, deg });
}
// one spec slam drawn into ctx (spec-canvas coordinates: screen y - SY0); lf = frames since its downbeat
function drawSpec(ctx, sp, lf, numOnly = false) {
  const base = BASE - SY0, asc = GC.asc, L = layout(sp);
  let x = L.x0;
  L.ds.forEach((D, i) => {
    const target = +sp.num[i], n = L.ds.length;
    const fi = 3 + 3 * (n > 1 ? i / (n - 1) : 1);                 // column i resolves at frame 3 .. 6 (left -> right)
    const p = clamp(lf / fi), spins = 10 * (1 + i) + 3.5 + 2 * i;   // half-integer: frame 0 is already mid-roll (no crisp wrong counter)
    const v = target + spins * (1 - eout(p));
    const fast = p < .55;                                          // smear ghost from frame 0
    const pitch = asc * 1.22;
    ctx.save(); ctx.beginPath(); ctx.rect(x - 8, base - asc - 18, D.w + 16, asc + 36); ctx.clip();
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
  text(ctx, sp.unit, L.x0 + L.wN + L.gap, L.deg ? base - asc + 120 : base, { size: L.uSize, weight: 700, family: FONT.display, gold: true, align: 'left', shine, alpha: .93 * clamp(lf / 2) });   // goldHi peak x .93 stays under the bloom knee
}
// serif descriptor: starts at +0.25 beat (frame 3), ~4 letters per frame, every letter sharp 1.5 frames after it starts,
// so even 'of almost nothing' is complete by frame ~8.5 (+0.7 beat)
function drawDesc(ctx, sp, lf) {
  if (lf < 3) return;
  const D = GC.desc.get(sp.b), tw = D.ws.reduce((a, b) => a + b, 0);
  const stag = Math.min(.3, 5 / D.ws.length);
  let x = 540 - tw / 2;
  D.ws.forEach((w, i) => {
    const l = lf - 3 - i * stag;
    if (l > 0) {
      const k = eout(clamp(l / 1.5));
      const lv = k > .97 ? 0 : k > .75 ? 1 : k > .45 ? 2 : 3, cv = D.cells[i][lv];
      ctx.save(); ctx.globalAlpha = clamp(l / 1.1);
      ctx.drawImage(cv, x + w / 2 - cv.width / 2, DESC_Y - SY0 + 10 * (1 - k) - D.size * .8 - D.pd);
      ctx.restore();
    }
    x += w;
  });
}

// mesh-dot burst (b48 match cut from s08's acoustic mesh: same pitch / offset rows / colours as its last frame); lf 0..3
function drawDots(ctx, lf) {
  if (lf >= 3) return;
  const p = lf / 3;
  const bgA = Math.max(0, 1 - lf * .75);
  if (bgA > 0) { ctx.save(); ctx.globalAlpha = bgA; ctx.fillStyle = 'rgb(22,9,4)'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  const Sc = f => 1 + .55 * f + .9 * f * f;                // scale at frame f
  const s1 = Sc(lf), s0 = Sc(Math.max(0, lf - .7));
  const P = 95, cx = 540, cy = 960, ox = 505 - cx, oy = 1012 - cy;
  ctx.save(); ctx.lineCap = 'round';
  for (let r = -12; r <= 12; r++) for (let c = -8; c <= 8; c++) {
    const px = ox + c * P + (r & 1 ? P / 2 : 0), py = oy + r * P;
    const x1 = cx + px * s1, y1 = cy + py * s1; if (x1 < -200 || x1 > W + 200 || y1 < -200 || y1 > H + 200) continue;
    const x0 = cx + px * s0, y0 = cy + py * s0;
    const a = lf < .5 ? 1 : .6 * (1 - p * .8), wdt = lf < .5 ? 52 : 14 * (1 - p * .4);   // frame 0 = s08's dots, then thin warp lines
    ctx.globalAlpha = a; ctx.strokeStyle = lf < .5 ? 'rgb(88,68,42)' : 'rgb(236,206,150)'; ctx.lineWidth = wdt;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1 + .01, y1); ctx.stroke();
  }
  ctx.restore();
}

// staircase HUD (top-left, out of the corridor's way): 8 rising steps, one per gate (the tuned whooshes D4 ... D5)
function drawHUD(ctx, b, alpha) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  const cur = clamp(Math.floor(b - B0 + .04), 0, 8);
  const lab = cur === 0 ? 'GATE 00 / 08' : `GATE 0${cur} / 08  ·  ${NOTES[cur - 1]}`;
  text(ctx, lab, 80, 268, { size: 34, weight: 700, family: FONT.mono, color: COL.gold, align: 'left', spacing: 2 });
  const x0 = 80, yb = 360, sw = 40, sg = 10;
  for (let i = 0; i < 8; i++) {
    const at = 49 + i - .04, on = b >= at, hit = on ? Math.exp(-(b - at) * 4) : 0;
    const h = 22 + i * 7;
    const x = x0 + i * (sw + sg);
    ctx.fillStyle = on ? COL.gold : 'rgba(154,151,143,.4)';
    ctx.globalAlpha = alpha * (on ? .6 + .4 * hit : 1);
    ctx.fillRect(x, yb - h, sw, h);
    if (hit > .05) { ctx.globalAlpha = alpha * .25 * hit; ctx.fillRect(x - 5, yb - h - 5, sw + 10, h + 10); }
  }
  ctx.restore();
}

let R = null;
// motion blur only on the rush frames (the nearest gate fills the frame and whips off its edges)
function mbAt(lt) {
  const f = Math.round(lt * 30), fb = f % 12;                // integer frame -> stable across sub-frames
  return fb === 11 ? 3 : fb === 9 || fb === 10 ? 2 : 1;
}

export default {
  id: 's09-gates', start: 48, end: 56,
  cutIn: 'none',
  init(E) {
    const scene = new THREE.Scene();
    scene.userData.envIntensity = .45;
    scene.fog = new THREE.FogExp2(new THREE.Color(COL.ink), .0072);
    const cam = new THREE.PerspectiveCamera(FOV, W / H, .1, 400);
    cam.setViewOffset(W, H, 0, 960 - VPY, W, H);             // principal point (the corridor axis) lands on y = VPY
    scene.add(cam);
    const kit = buildKit(); kit.mats = buildMats(kit);
    const gates = []; for (let k = 1; k <= NG; k++) { const g = buildGate(k, kit); scene.add(g.piv); gates.push(g); }
    const hemi = new THREE.HemisphereLight(0xf6f4f0, 0x202226, .85); scene.add(hemi);
    const camLight = new THREE.PointLight(0xfff0dc, 0, 0, 2); scene.add(camLight);
    // four gate lights, re-assigned per frame to the four gates ahead; colour and strength depend on the gate only (no pops)
    const gl = [0, 1, 2, 3].map(() => { const L = new THREE.PointLight(0xffffff, 0, 0, 2); scene.add(L); return L; });
    const st = buildStreaks(300); scene.add(st.mesh);
    const specC = makeCanvas(W, SH);
    buildCaches();
    R = { scene, cam, gates, camLight, gl, st, specC };
  },
  motionBlur(lt) { return mbAt(lt); },
  draw(E, lt, t) {
    const { scene, cam, gates, camLight, gl, st } = R;
    const b = B0 + lt / BEAT, fx = E.fx, bg = E.bg, fg = E.fg;
    const lfq = Math.round(lt * 30);                             // integer frame (identical in every motion-blur sub-frame)
    const Fr = Math.floor(t * 30 + .5);
    const beatIn = b - Math.floor(b);
    // bright pass runs on the ACES-clamped composite (max 1.0): threshold .93 keeps the #f6f3ec type (~.92 linear) out, while the
    // HDR streaks / gate flares / exit light (ACES >= .95) glow; the gain makes up for the narrow .93-1.0 window
    fx.exposure = .85; fx.bloom = 4.2; fx.bloomThreshold = .93; fx.bloomKnee = .02;
    fx.sat = 1.0; fx.contrast = 1.05; fx.grain = .045; fx.vignette = .4;

    // ---------------- camera
    const cd = camDist(b), cz = -cd;
    const vel = (camDist(b + .01) - cd) / (.01 * BEAT);         // units / s
    const rush = clamp((vel - 20) / 160);                        // 0 while holding, 1 at the peak of the rush
    const sway = V3(.3 * noise1(b * .7 + 3), .25 * noise1(b * .6 + 11), 0).multiplyScalar(1 - rush);
    cam.position.set(sway.x, sway.y, cz);
    cam.rotation.set(0, 0, rollAt(b));
    cam.updateMatrixWorld();
    camLight.position.set(0, 0, cz + 1);
    camLight.intensity = 30 + 260 * rush;

    // ---------------- gates
    const ahead = [];
    gates.forEach(g => {
      const d = cz - g.piv.position.z;                           // > 0 ahead of the camera
      g.piv.visible = d > -4 && d < 200;
      // each gate screws itself into its slot on approach (-25° -> its (k-1)*30° slot by the time it is the next gate)
      g.piv.rotation.z = ((g.k - 1) * TWIST - 25 * (1 - eio(clamp((100 - d) / 70)))) * DEG;
      const flare = d > 0 ? Math.exp(-d / 6) : Math.exp(d / 1.5);
      g.mats.gold.emissiveIntensity = .16 + 4.6 * flare;          // every gate keeps a faint gold line: the row reads in depth
      g.setLod(d < 40 ? 'hi' : 'lo');
      if (d > -2) ahead.push([d, g]);
    });
    ahead.sort((a, c) => a[0] - c[0]);
    gl.forEach((L, i) => {
      const e = ahead[i];
      if (!e) { L.intensity = 0; return; }
      const [d, g] = e;
      // key in front of the gate, a little above and to the side of the axis (relative to the gate's own twist)
      const a = g.piv.rotation.z + 2.0;
      L.position.set(Math.cos(a) * 4, Math.sin(a) * 4, g.piv.position.z + 7);
      L.color.copy(g.warm ? KEY_WARM : KEY_COOL);
      L.intensity = (g.warm ? 125 : 135) * clamp((150 - d) / 60);
    });

    // ---------------- streaks
    const boost = 1 + 1.2 * ein(seg(b, 55, 56));
    st.update(b, cz, vel, boost);

    // ---------------- bg: ink + VP glow (pulses on the beat, opens into the exit light over b55-56)
    {
      const hit = b >= 49 ? Math.exp(-beatIn * BEAT / .1) : 0;
      const ex = ein(seg(b, 54.8, 56));
      bg.save();
      bg.globalAlpha = clamp(.62 + .18 * hit + .2 * ex);
      const s = 1 + .5 * ex, r = 640 * s;
      bg.drawImage(GC.glow, 540 - r, VPY - r, r * 2, r * 2);
      if (ex > 0) { const r2 = 420 * (.4 + 1.2 * ex); bg.globalAlpha = ex; bg.drawImage(GC.exitGlow, 540 - r2, VPY - r2, r2 * 2, r2 * 2); }
      bg.restore();
    }

    E.render3D(scene, cam);

    // ---------------- fg: dots, spec slams, HUD
    drawDots(fg, lt * 30 < 3 ? lfq : 3);
    {
      const bt = B0 + lfq / 12;                                   // type animates per whole frame
      const sp = SPECS.find(s => bt >= s.b - 1e-6 && bt < s.b + 2 - 1e-6);
      const sl0 = sp ? lfq - (sp.b - B0) * 12 : -1;
      if (sp && !(sp.b === B0 && sl0 === 0)) {                    // f576 stays a clean mesh-dot frame (protects the match cut)
        const sl = sl0;                                            // frames since slam
        const sc = R.specC.getContext('2d');
        sc.setTransform(1, 0, 0, 1, 0, 0); sc.clearRect(0, 0, W, SH);
        sc.save(); sc.globalAlpha = clamp(sl / 3); sc.drawImage(GC.plate, 0, 0); sc.restore();
        // stutter ghost on 16ths (+1.0 and +1.25 beats)
        const st1 = sl === 12 || sl === 15;
        if (st1) { sc.save(); sc.globalAlpha = .4; sc.translate(18, 0); drawSpec(sc, sp, sl, true); sc.restore(); }
        drawSpec(sc, sp, sl);
        drawDesc(sc, sp, sl);
        // composite: slam scale (1.4 -> 1 over 3 frames), slow push, slice wipe-out over the last 2 frames (+1.83 beat)
        const slam = 1 + .4 * (1 - expoOut(clamp(sl / 3)));
        const push = 1 + .03 * seg(sl, 3, 22);
        const s = slam * push, ox = 540, oy = BASE - GC.asc / 2 - SY0;
        fg.save(); fg.translate(0, SY0);
        if (sl < 22) {
          fg.translate(ox, oy); fg.scale(s, s); fg.translate(-ox, -oy); fg.drawImage(R.specC, 0, 0);
        } else {
          const w = (sl - 21) / 2.4, n = 22, hS = SH / n;
          fg.translate(ox, oy); fg.scale(s, s); fg.translate(-ox, -oy);
          for (let i = 0; i < n; i++) {
            const dir = rnd(i * 3.3 + sp.b) < .5 ? -1 : 1;
            const dx = dir * (40 + 900 * rnd(i * 7.7 + sp.b)) * ein(w) + dir * 30 * w;
            fg.globalAlpha = 1 - w * .7;
            fg.drawImage(R.specC, 0, i * hS, W, hS, dx, i * hS, W, hS);
          }
        }
        fg.restore();
      }
    }
    drawHUD(fg, b, seg(lt * 30, 2, 8) * (1 - seg(b, 55.6, 56)));

    // ---------------- post
    fx.zoomCenter = [.5, 1 - VPY / H];
    // speed blur on the exit rush only (the radial blur is expensive on CPU)
    fx.zoomBlur = b >= 55.6 ? .32 * ein(seg(b, 55.6, 56)) : 0;     // starts after the last descriptor's read
    // gate passes (land on b49 ... b56): rgb kick .012, zoom 1.04 punch, short shake; no flash (keeps the image readable)
    if (b >= 49) {
      const fr = beatIn * 12;
      fx.rgb = Math.max(fx.rgb, .0015 + .0105 * Math.max(0, 1 - fr / 6));
      fx.zoom *= 1 + .04 * (1 - expoOut(clamp(fr / 6)));
      const sh = .006 * Math.max(0, 1 - fr / 6);
      fx.shake = [fx.shake[0] + (rnd(Fr * 1.7) - .5) * 2 * sh, fx.shake[1] + (rnd(Fr * 2.9 + 4) - .5) * 2 * sh];
    }
    // the rush into each gate: rgb builds over the last 3 frames before the beat
    if (beatIn > .75) fx.rgb = Math.max(fx.rgb, .0015 + .008 * seg(beatIn, .75, 1));
    // spec slams b48, 50, 52, 54: zoom 1.06, rgb, glitch slices on frames 1-2 (frame 0 stays a clean punch)
    for (const sp of SPECS) {
      const fr = (b - sp.b) * 12;
      if (fr >= 0 && fr < 8) fx.zoom *= 1 + .06 * (1 - expoOut(fr / 8));
      if (fr >= 0 && fr < 3) { fx.rgb = Math.max(fx.rgb, .02 * (1 - fr / 3)); }
      if (fr >= 1 && fr < 3) { fx.glitch = Math.max(fx.glitch, fr < 2 ? .2 : .1); fx.glitchSeed = sp.b * 17 + Math.floor(fr) * 5; }
      if (fr >= 22 && fr < 24) { fx.rgb = Math.max(fx.rgb, .008); }
    }
    // b48 match-cut kick
    // frame 0 stays close to s08's crisp last frame (light blur); the blast peaks on frame 1
    if (lt * 30 < 4.5) { const zf = lt * 30; fx.zoomBlur = Math.max(fx.zoomBlur, zf < .5 ? .22 : .6 * (1 - (zf - .5) / 4)); fx.zoomCenter = [.5, .5]; }
  },
};
