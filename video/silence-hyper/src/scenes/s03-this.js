// s03-this — THIS. : the slam, the letters become windows, the Swiss shear, and the gold period that draws the ear-cup ring (b16-20).
//
// Layers: bg2d ink + warm haze · 3D (a) gold/glass shards + dust from the detonating point (b16-18.5),
//         3D (b) the right ear cup in darkness + an emissive tube drawing the cup's ring (b19-20) · fg2d the type, period, streak, sparks.
// Hand-off: the last frame is exactly CUP_CAM (exported below) with the closed ring at emissive 6 — s04 starts on this framing.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoIn, expoOut, rnd, text, measure, font, fitSize, goldGrad,
  orbitFrame, ADDITIVE, dotTexture, COL, FONT } from '../lib.js';
import { createHeadphone } from '../model.js';

// ------------------------------------------------------------------ shared camera pose (s04's first frame)
// Right ear cup seen straight onto its outer face. Cup ring centre-line (world) = centre (7.2,-4.5,0), semi-axes 4.788 (Y) x 3.99 (Z).
// fov 30, distance 44.67 -> the ring is ~640 px across (Z) and ~768 px tall, centred on (540,960).
export const CUP_RING = { center: [7.2, -4.5, 0], ay: 3.99 * 1.2, az: 3.99 };
export const CUP_CAM = { fov: 30, position: [7.2 + 44.67, -4.5, 0], target: [7.2, -4.5, 0], up: [0, 1, 0], near: .5, far: 400 };

const Q = lt => lt * 30;                      // frames since b16.0 (float; f192 = 0)
const GOLD_L = new THREE.Color(COL.gold).convertSRGBToLinear();
const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
const tri = (a, b) => Math.max(0, 1 - Math.abs(a) / b);

let L = null;                                  // type layout
let SOLID, EDGE, WIN;                          // canvases
let S3 = null, CUP = null;                     // 3D rigs

// ------------------------------------------------------------------ layout of 'THIS.'
function layout() {
  const c = document.createElement('canvas').getContext('2d');
  const size = Math.round(fitSize(c, 'THIS.', 980, 900, 400, FONT.impact));
  c.font = font(size, 400, FONT.impact); c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.letterSpacing = '0px';
  const mH = c.measureText('H'), capH = mH.actualBoundingBoxAscent;
  const total = c.measureText('THIS.').width, wThis = c.measureText('THIS').width;
  const x0 = 540 - total / 2, base = Math.round(960 + capH / 2);
  const mp = c.measureText('.');
  const px0 = x0 + wThis - mp.actualBoundingBoxLeft, px1 = x0 + wThis + mp.actualBoundingBoxRight;
  const py0 = base - mp.actualBoundingBoxAscent, py1 = base + mp.actualBoundingBoxDescent;
  // ink extents of THIS (for the window content rect)
  const mt = c.measureText('THIS');
  return { size, capH, x0, base, wThis, rect: [x0 - mt.actualBoundingBoxLeft, base - mt.actualBoundingBoxAscent, mt.actualBoundingBoxLeft + mt.actualBoundingBoxRight, mt.actualBoundingBoxAscent + Math.max(0, mt.actualBoundingBoxDescent)],
    pcx: (px0 + px1) / 2, pcy: (py0 + py1) / 2, pw: px1 - px0, ph: py1 - py0 };
}

// ------------------------------------------------------------------ the gold period / dot / streak body
function goldBody(ctx, x, y, w, h, round, alpha, glow, hot = 0) {
  if (alpha <= .003) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  const r = Math.min(w, h) / 2 * round;
  const g = ctx.createLinearGradient(x - w / 2, y - h / 2, x + w / 2, y + h / 2);
  g.addColorStop(0, hot > 0 ? mix(COL.goldHi, '#fff7e6', hot) : COL.goldHi); g.addColorStop(.45, hot > 0 ? mix(COL.gold, COL.goldHi, hot) : COL.gold); g.addColorStop(1, COL.gold2);
  ctx.fillStyle = g; ctx.shadowColor = 'rgba(230,200,150,.85)'; ctx.shadowBlur = glow;
  ctx.beginPath(); ctx.roundRect(x - w / 2, y - h / 2, w, h, r); ctx.fill();
  ctx.shadowBlur = 0;
  // specular highlight (top-left)
  const s = ctx.createRadialGradient(x - w * .22, y - h * .25, 0, x - w * .22, y - h * .25, Math.max(w, h) * .55);
  s.addColorStop(0, `rgba(255,248,232,${.55 + .4 * hot})`); s.addColorStop(1, 'rgba(255,248,232,0)');
  ctx.fillStyle = s; ctx.beginPath(); ctx.roundRect(x - w / 2, y - h / 2, w, h, r); ctx.fill();
  ctx.restore();
}
function halo(ctx, x, y, rx, ry, alpha, color = '230,200,150') {
  if (alpha <= .003 || rx <= 0 || ry <= 0) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(x, y); ctx.scale(rx / ry, 1);
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, ry);
  g.addColorStop(0, `rgba(${color},${alpha})`); g.addColorStop(.4, `rgba(${color},${alpha * .35})`); g.addColorStop(1, `rgba(${color},0)`);
  ctx.fillStyle = g; ctx.fillRect(-ry, -ry, ry * 2, ry * 2); ctx.restore();
}
function mix(a, b, k) {
  const pa = [1, 3, 5].map(i => parseInt(a.slice(i, i + 2), 16)), pb = [1, 3, 5].map(i => parseInt(b.slice(i, i + 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], clamp(k)))).join(',')})`;
}
// cover-fit with zoom, focal point and pixel offset
function cover(ctx, img, rx, ry, rw, rh, zoom, fx, fy, dx = 0, dy = 0) {
  if (!img) return;
  const s = Math.max(rw / img.width, rh / img.height) * zoom, w = img.width * s, h = img.height * s;
  ctx.drawImage(img, rx + (rw - w) * fx + dx, ry + (rh - h) * fy + dy, w, h);
}

// ------------------------------------------------------------------ 3D (a): detonation shards + dust
function buildShards(E) {
  const scene = new THREE.Scene(); scene.userData.envIntensity = 1.6;
  const cam = new THREE.PerspectiveCamera(35, W / H, .1, 300); cam.position.set(0, 0, 40); cam.lookAt(0, 0, 0);
  const key = new THREE.DirectionalLight(0xffe2b0, 2.2); key.position.set(10, 14, 12); scene.add(key);
  const rim = new THREE.DirectionalLight(0xe6c896, 1.4); rim.position.set(-12, -6, -8); scene.add(rim);
  const geo = new THREE.TetrahedronGeometry(1, 0);
  const gold = new THREE.MeshPhysicalMaterial({ color: 0xe0bd8a, metalness: 1, roughness: .16 });
  const glass = new THREE.MeshPhysicalMaterial({ color: 0xfff6e8, metalness: .1, roughness: .04, clearcoat: 1, transparent: true, opacity: .22, side: THREE.DoubleSide });
  const NG = 90, NC = 46;
  const mG = new THREE.InstancedMesh(geo, gold, NG), mC = new THREE.InstancedMesh(geo, glass, NC);
  mG.frustumCulled = mC.frustumCulled = false; scene.add(mG); scene.add(mC);
  const mkData = (n, seed) => Array.from({ length: n }, (_, i) => {
    const r = j => rnd(seed + i * 7.13 + j * 1.91);
    const u = r(1) * 2 - 1, th = r(2) * TAU, s = Math.sqrt(1 - u * u);
    const dir = new THREE.Vector3(s * Math.cos(th), u * 1.25, s * Math.sin(th) * .6 + .55).normalize();
    return { dir, speed: 22 + 90 * Math.pow(r(3), 1.3), size: .07 + .38 * Math.pow(r(4), 2.4), axis: new THREE.Vector3(r(5) - .5, r(6) - .5, r(7) - .5).normalize(),
      spin: 6 + r(8) * 22, flat: .06 + r(9) * .12, stretch: .5 + r(10) * 1.2, a0: r(11) * TAU };
  });
  const dG = mkData(NG, 11), dC = mkData(NC, 503);
  // dust motes (additive), pushed out by the blast then drifting
  const ND = 700, dp = new Float32Array(ND * 3), base = [];
  for (let i = 0; i < ND; i++) base.push([(rnd(i * 1.3 + 9) - .5) * 46, (rnd(i * 2.7 + 9) - .5) * 80, (rnd(i * 3.1 + 9) - .5) * 50 - 5, rnd(i * 4.9 + 9)]);
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(dp, 3));
  const dm = new THREE.PointsMaterial({ size: .16, map: dotTexture(), color: GOLD_L.clone().multiplyScalar(1.6), sizeAttenuation: true, ...ADDITIVE, opacity: .8 });
  const dust = new THREE.Points(dg, dm); dust.frustumCulled = false; scene.add(dust);
  const o = new THREE.Object3D(), q = new THREE.Quaternion();
  function place(mesh, data, tau) {
    const k = 1.3, travel = (1 - Math.exp(-k * tau)) / k;
    data.forEach((d, i) => {
      o.position.copy(d.dir).multiplyScalar(d.speed * travel);
      o.position.y -= 1.2 * tau * tau;
      q.setFromAxisAngle(d.axis, d.a0 + d.spin * travel * 2.2 + tau * 1.5); o.quaternion.copy(q);
      const sz = d.size * (tau < .03 ? tau / .03 : 1);
      o.scale.set(sz * d.stretch, sz, sz * d.flat); o.updateMatrix(); mesh.setMatrixAt(i, o.matrix);
    });
    mesh.instanceMatrix.needsUpdate = true;
  }
  function update(lt) {
    const tau = Math.max(0, lt);
    place(mG, dG, tau); place(mC, dC, tau);
    const fade = 1 - seg(lt, .4, .95);
    gold.opacity = fade; gold.transparent = fade < 1; glass.opacity = .22 * fade;
    mG.visible = mC.visible = fade > .01;
    const a = dp; const push = (1 - Math.exp(-3 * tau)) * 6;
    for (let i = 0; i < ND; i++) {
      const [x, y, z, r] = base[i]; const d = Math.hypot(x, y) + 1e-3;
      a[i * 3] = x + x / d * push * (1 - d / 60) + Math.sin(lt * .6 + r * 20) * .4;
      a[i * 3 + 1] = y + y / d * push * (1 - d / 60) + lt * (.5 + r) * .8;
      a[i * 3 + 2] = z + lt * 1.5;
    }
    dg.attributes.position.needsUpdate = true;
    dm.opacity = .6 * (1 - seg(lt, 1.05, 1.35)) * (.35 + .65 * seg(lt, 0, .1));
  }
  return { scene, cam, update };
}

// ------------------------------------------------------------------ 3D (b): the cup in darkness + the ring tube
const TUBE_V = `attribute float aU; varying float vA; varying vec3 vN; varying vec3 vV;
void main(){ vA = min(aU, 1.-aU)*2.; vN = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); vV = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }`;
const TUBE_F = `uniform float uProg, uInt; uniform vec3 uCol; varying float vA; varying vec3 vN; varying vec3 vV;
void main(){
  if (vA > uProg + .0005) discard;
  float head = uProg < .999 ? exp(-(uProg - vA)*38.) : 0.;
  float fres = .55 + .45*abs(dot(normalize(vN), normalize(vV)));
  vec3 c = uCol*uInt*fres*(1. + head*2.2) + vec3(1., .93, .8)*head*uInt*.9;
  gl_FragColor = vec4(c, 1.);
}`;
function buildCup(E) {
  const scene = new THREE.Scene(); scene.userData.envIntensity = 0;
  const hp = createHeadphone(); scene.add(hp.root);
  const cup = hp.cups[1], ring = cup.userData.parts.ring;
  hp.root.updateMatrixWorld(true);
  // ring centre-line in world space, parametrised from 12 o'clock (u = 0) all the way round (u = 1)
  const pts = [], v = new THREE.Vector3();
  for (let i = 0; i <= 360; i++) { const a = i / 360 * TAU; v.set(3.99 * Math.cos(a), 0, 3.99 * Math.sin(a)); pts.push(ring.localToWorld(v.clone())); }
  let top = 0; pts.forEach((p, i) => { if (p.y > pts[top].y) top = i; });
  const seq = []; for (let i = 0; i < 360; i++) seq.push(pts[(top + i) % 360]);
  const curve = new THREE.CatmullRomCurve3(seq, true);
  hp.sliders[1].visible = false; hp.band.group.visible = false;
  ring.visible = false;   // the tube takes its place (s04 brings the PBR ring back)
  const TS = 360, RS = 16;
  const geo = new THREE.TubeGeometry(curve, TS, .12, RS, true);
  const au = new Float32Array(geo.attributes.position.count);
  for (let i = 0; i < au.length; i++) au[i] = Math.floor(i / (RS + 1)) / TS;
  geo.setAttribute('aU', new THREE.BufferAttribute(au, 1));
  const mat = new THREE.ShaderMaterial({ vertexShader: TUBE_V, fragmentShader: TUBE_F, depthTest: false, depthWrite: false,
    uniforms: { uProg: { value: 0 }, uInt: { value: 3 }, uCol: { value: GOLD_L.clone().lerp(new THREE.Color(1, 1, 1), .08).multiplyScalar(.5) } } });
  const tube = new THREE.Mesh(geo, mat); tube.renderOrder = 10; tube.frustumCulled = false; scene.add(tube);
  // warm spill riding the two drawing heads (the ring's own light grazing the stone shell)
  const lights = [0, 1].map(() => { const l = new THREE.PointLight(0xffd9a0, 0, 9, 2); scene.add(l); return l; });
  const fill = new THREE.PointLight(0xffd9a0, 0, 14, 2); scene.add(fill);
  const cam = new THREE.PerspectiveCamera(CUP_CAM.fov, W / H, CUP_CAM.near, CUP_CAM.far);
  const C = new THREE.Vector3(...CUP_CAM.target), P = new THREE.Vector3(...CUP_CAM.position);
  const out = P.clone().sub(C).normalize();
  // point on the ring at angle-from-top fraction a (0..1) on side s (+1 / -1)
  const at = (a, s) => curve.getPointAt(s > 0 ? a / 2 : 1 - a / 2);
  function setCam(dist) { cam.position.copy(C).addScaledVector(out, dist); cam.up.set(...CUP_CAM.up); cam.lookAt(C); cam.updateMatrixWorld(); cam.updateProjectionMatrix(); }
  const tmp = new THREE.Vector3();
  const project = p => { tmp.copy(p).project(cam); return [(tmp.x + 1) / 2 * W, (1 - tmp.y) / 2 * H]; };
  return { scene, cam, tube, mat, lights, fill, at, setCam, project, out, C, dist0: P.distanceTo(C) };
}

// ------------------------------------------------------------------ timings (frames since b16.0)
const QW1 = 6, QW2 = 12, QW3 = 15, QSH = 18, QG0 = 24, QG1 = 30, QHB = 30, QST = 33, QB0 = 36, QB1 = 39, QCL = 45, QEND = 48;
const ARC0 = .22;   // ring fraction covered by the bent streak at the end of the bend
// tube progress (fraction of the half-ring drawn on each side, 0..1)
function ringProg(q) {
  if (q < QB0) return 0;
  if (q < QB1) return ARC0 * eio(seg(q, QB0, QB1));
  const u = seg(q, QB1, QCL); return ARC0 + (1 - ARC0) * (1.6 * u - .6 * u * u);
}
// period glide path (quadratic bezier from its typeset spot to the centre, bowing upward)
function glidePos(k) {
  const a = [540 + (L.pcx - 540) * 1.035, 960 + (L.pcy - 960) * 1.035], c = [lerp(L.pcx, 540, .35) + 60, Math.min(L.pcy, 960) - 260], b = [540, 960];
  const u = 1 - k; return [u * u * a[0] + 2 * u * k * c[0] + k * k * b[0], u * u * a[1] + 2 * u * k * c[1] + k * k * b[1]];
}

export default {
  id: 's03-this', start: 16, end: 20,
  cutIn: 'none',
  init(E) {
    L = layout();
    SOLID = mk(); EDGE = mk(); WIN = mk();
    const s = SOLID.getContext('2d');
    text(s, 'THIS', L.x0, L.base, { size: L.size, weight: 400, family: FONT.impact, color: COL.white, align: 'left' });
    const e = EDGE.getContext('2d');
    text(e, 'THIS', L.x0, L.base, { size: L.size, weight: 400, family: FONT.impact, fill: false, stroke: 4.5, strokeColor: COL.gold, align: 'left' });
    e.globalCompositeOperation = 'destination-in'; e.drawImage(SOLID, 0, 0);
    S3 = buildShards(E); CUP = buildCup(E);
  },
  draw(E, lt, t) {
    const q = Q(lt), fx = E.fx, bg = E.bg, fg = E.fg, F = Math.floor(q + 1e-4);
    // ---------------- post: the AFTER look switches on
    fx.exposure = .88; fx.grain = .05; fx.vignette = .4; fx.bloom = .7; fx.bloomThreshold = .72; fx.sat = 1.05;

    // ---------------- background: ink + warm haze (blooms on the hit, breathes, dims for the darkness of b19)
    bg.fillStyle = COL.ink; bg.fillRect(0, 0, W, H);
    {
      const hit = Math.exp(-q / 5), dark = 1 - .7 * seg(q, QG0, QB0);
      const a = (.05 + .05 * Math.sin(q * .09)) * dark + .35 * hit;
      const g = bg.createRadialGradient(560 + 40 * Math.sin(q * .03), 900, 0, 540, 960, 1150);
      g.addColorStop(0, `rgba(120,96,64,${a})`); g.addColorStop(.45, `rgba(60,46,30,${a * .5})`); g.addColorStop(1, 'rgba(5,5,6,0)');
      bg.fillStyle = g; bg.fillRect(0, 0, W, H);
      if (q >= QB0) { // faint warm glow behind the cup so its black silhouette just reads
        const k = seg(q, QB0, QEND) * .9 + .1 * Math.exp(-(q - QCL) / 3) * (q >= QCL ? 1 : 0);
        const g2 = bg.createRadialGradient(540, 960, 200, 540, 960, 760);
        g2.addColorStop(0, 'rgba(70,52,30,0)'); g2.addColorStop(.55, `rgba(90,68,40,${.025 * k})`); g2.addColorStop(1, 'rgba(5,5,6,0)');
        bg.fillStyle = g2; bg.fillRect(0, 0, W, H);
      }
    }

    // ---------------- 3D (a): shards + dust from the detonation
    if (q < 42) { S3.update(lt); E.render3D(S3.scene, S3.cam); }

    // ---------------- 3D (b): the cup + the ring tube
    const prog = ringProg(q);
    if (q >= QB0 - 1) {
      const dist = CUP.dist0 * lerp(1.075, 1, eout(seg(q, QB0 - 1, QEND)));
      CUP.setCam(dist);
      const inten = q < QCL ? 3 : lerp(3, 6, eout(seg(q, QCL, QCL + 2.5)));
      CUP.mat.uniforms.uProg.value = prog; CUP.mat.uniforms.uInt.value = inten * (1 + .5 * Math.exp(-Math.max(0, q - QCL) / 1.5) * (q >= QCL ? 1 : 0));
      CUP.tube.visible = prog > .001 && q >= QB0 + 2;
      [1, -1].forEach((sd, i) => {
        const p = CUP.at(clamp(prog, 0, 1), sd), l = CUP.lights[i];
        l.position.copy(p).addScaledVector(CUP.out, 1.6); l.intensity = q >= QB0 + 2 && prog < 1 ? 3.2 * seg(q, QB0 + 2, QB0 + 3) : 0;
      });
      CUP.fill.position.copy(CUP.C).addScaledVector(CUP.out, 5.5);
      CUP.fill.intensity = q >= QCL ? 3 * eout(seg(q, QCL, QEND)) + 5 * Math.exp(-(q - QCL) / 2) : 0;
      E.render3D(CUP.scene, CUP.cam);
    }

    // ---------------- 2D type
    const push = q < QW1 ? 1 : 1 + .035 * eio(seg(q, QW1, QSH + 4));
    if (q < QW1) {
      // THE HIT: solid THIS. arriving as horizontal slices, scale 1.12 -> 1
      const sc = 1 + .12 * (1 - expoOut(q / 8)), off = 40 * clamp(1 - q / 3);
      fg.save(); fg.translate(540, 960); fg.scale(sc, sc); fg.translate(-540, -960);
      const top = L.base - L.capH - 30, bandH = 34, nb = Math.ceil((L.capH + 60) / bandH);
      for (let k = 0; k < nb; k++) {
        const y = top + k * bandH, dx = off > 0 ? (k % 2 ? 1 : -1) * off * (.4 + 1.2 * rnd(k * 3.3 + F)) : 0;
        fg.drawImage(SOLID, 0, y, W, bandH, dx, y, W, bandH);
      }
      fg.restore();
    } else if (q < QSH + 14) {
      // WINDOWS: the letters show the product (hero -> macro -> orbit spin)
      const w = WIN.getContext('2d'); w.setTransform(1, 0, 0, 1, 0, 0); w.globalCompositeOperation = 'source-over'; w.globalAlpha = 1;
      w.fillStyle = '#000'; w.fillRect(0, 0, W, H);
      const [rx, ry, rw, rh] = L.rect;
      let seg0, seg1;
      if (q < QW2) { seg0 = QW1; seg1 = QW2; const u = seg(q, QW1, QW1 + 12); cover(w, E.img.hero, rx, ry, rw, rh, 2.4, .66, .74, 0, 60 - 120 * u); }
      else if (q < QW3) { seg0 = QW2; seg1 = QW3; const u = seg(q, QW2, QW2 + 12); cover(w, E.img.macro, rx, ry, rw, rh, 2.2, .72, .45, 70 - 120 * u, 0); }
      else {
        seg0 = QW3; seg1 = QSH + 6;
        const f = q < QSH ? 39 * seg(q, QW3, QSH) : (39 + (q - QSH) * 1.2) % 40;
        orbitFrame(w, [E.img.orbit0, E.img.orbit1, E.img.orbit2, E.img.orbit3], f, 540, ry + rh * .5 + 40, 1250, { mode: 'source-over' });
      }
      // a light sweep gliding across each window segment
      {
        const u = seg(q, seg0, seg1 + 2), sx = lerp(rx - 300, rx + rw + 300, eio(u));
        const g = w.createLinearGradient(sx - 160, ry, sx + 160, ry + rh * .4);
        g.addColorStop(0, 'rgba(255,230,190,0)'); g.addColorStop(.5, 'rgba(255,230,190,.28)'); g.addColorStop(1, 'rgba(255,230,190,0)');
        w.globalCompositeOperation = 'lighter'; w.fillStyle = g; w.fillRect(rx - 50, ry - 50, rw + 100, rh + 100); w.globalCompositeOperation = 'source-over';
      }
      // a short white-hot bloom of the glyphs on each window cut
      const cutK = Math.max(...[QW1, QW2, QW3].map(c => q >= c ? Math.exp(-(q - c) / 1.2) : 0));
      if (cutK > .02) { w.globalAlpha = .55 * cutK; w.drawImage(SOLID, 0, 0); w.globalAlpha = 1; }
      w.globalCompositeOperation = 'destination-in'; w.drawImage(SOLID, 0, 0);
      w.globalCompositeOperation = 'source-over'; w.drawImage(EDGE, 0, 0);
      // outline echoes radiating from the word on every window cut
      for (const c of [QW1, QW2, QW3]) {
        const d = q - c; if (d < 0 || d >= 7) continue;
        const sc = push * (1 + .14 * eout(d / 7));
        fg.save(); fg.globalAlpha = .45 * Math.pow(1 - d / 7, 1.5); fg.translate(540, 960); fg.scale(sc, sc); fg.translate(-540, -960); fg.drawImage(EDGE, 0, 0); fg.restore();
      }
      fg.save(); fg.translate(540, 960); fg.scale(push, push); fg.translate(-540, -960);
      if (q < QSH) fg.drawImage(WIN, 0, 0);
      else {
        // SWISS SHEAR: 12 columns of 90 px, even up / odd down, 2200 px, expoIn over 8 frames, staggered 1 frame, 3 ghosts
        for (let i = 0; i < 12; i++) {
          const dir = i % 2 ? 1 : -1, x = i * 90;
          const offAt = qq => dir * 2200 * ein(seg(qq, QSH + i * .4, QSH + 6 + i * .4));
          for (let g = 3; g >= 0; g--) {
            const oy = offAt(q - g * .55); if (g > 0 && Math.abs(offAt(q) - oy) < 2) continue;
            fg.globalAlpha = g === 0 ? 1 : [0, .42, .22, .1][g];
            fg.drawImage(WIN, x, 0, 90, H, x, oy, 90, H);
          }
          fg.globalAlpha = 1;
        }
      }
      fg.restore();
    }

    // ---------------- shockwave from the detonating point (b16.0)
    if (q < 10) {
      const k = expoOut(q / 9), r = lerp(30, 1500, k);
      fg.save(); fg.globalCompositeOperation = 'lighter'; fg.strokeStyle = `rgba(255,236,200,${.9 * (1 - q / 10)})`; fg.lineWidth = lerp(10, 1.5, k);
      fg.shadowColor = 'rgba(230,200,150,.9)'; fg.shadowBlur = 30; fg.beginPath(); fg.arc(540, 960, r, 0, TAU); fg.stroke(); fg.restore();
    }

    // ---------------- the period: typeset -> glide -> heartbeat -> anamorphic streak -> bends into the ring
    {
      const pushP = (x, y) => [540 + (x - 540) * push, 960 + (y - 960) * push];
      let [x, y] = pushP(L.pcx, L.pcy), w = L.pw * push, h = L.ph * push, round = .18, glow = 34, hot = 0;
      if (q < QW1) { const sc = 1 + .12 * (1 - expoOut(q / 8)); x = 540 + (L.pcx - 540) * sc; y = 960 + (L.pcy - 960) * sc; w = L.pw * sc; h = L.ph * sc; hot = Math.exp(-q / 3); }
      const D = 74;
      if (q >= QG0) {
        const k = eio(seg(q, QG0, QG1));
        // smooth tapered comet trail along the path (replaces discrete ghosts)
        if (q < QG1 + 5) {
          const kt = eio(seg(q - 5, QG0, QG1)), N = 32, P = [], Lf = [], Rt = [];
          for (let i = 0; i <= N; i++) P.push(glidePos(lerp(kt, k, i / N)));
          for (let i = 0; i <= N; i++) {
            const a = P[Math.max(0, i - 1)], b = P[Math.min(N, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], dl = Math.hypot(dx, dy) || 1;
            const hw = lerp(L.pw * 1.035, D, lerp(kt, k, i / N)) * .42 * Math.pow(i / N, 1.4);
            Lf.push([P[i][0] - dy / dl * hw, P[i][1] + dx / dl * hw]); Rt.push([P[i][0] + dy / dl * hw, P[i][1] - dx / dl * hw]);
          }
          const [ax, ay] = P[0], [bx, by] = P[N];
          if (Math.hypot(bx - ax, by - ay) > 4) {
            fg.save(); fg.globalCompositeOperation = 'lighter';
            const g = fg.createLinearGradient(ax, ay, bx, by); g.addColorStop(0, 'rgba(230,200,150,0)'); g.addColorStop(1, 'rgba(240,212,165,.55)');
            fg.fillStyle = g; fg.shadowColor = 'rgba(230,200,150,.6)'; fg.shadowBlur = 24;
            fg.beginPath(); Lf.forEach(([x1, y1], i) => i ? fg.lineTo(x1, y1) : fg.moveTo(x1, y1)); for (let i = N; i >= 0; i--) fg.lineTo(Rt[i][0], Rt[i][1]); fg.closePath(); fg.fill();
            fg.shadowBlur = 0; const g2 = fg.createLinearGradient(ax, ay, bx, by); g2.addColorStop(0, 'rgba(255,244,220,0)'); g2.addColorStop(1, 'rgba(255,244,220,.9)');
            fg.strokeStyle = g2; fg.lineWidth = 3; fg.beginPath(); P.forEach(([x1, y1], i) => i ? fg.lineTo(x1, y1) : fg.moveTo(x1, y1)); fg.stroke();
            fg.restore();
          }
        }
        [x, y] = glidePos(k);
        w = lerp(L.pw * push, D, k); h = lerp(L.ph * push, D, k); round = lerp(.18, 1, k); glow = lerp(34, 46, k);
      }
      // heartbeat: 1 -> 1.7 -> 1
      let hb = 1;
      if (q >= QHB) hb = q < QHB + 1.5 ? 1 + .7 * eout(seg(q, QHB, QHB + 1.5)) : 1 + .7 * (1 - eio(seg(q, QHB + 1.5, QHB + 5)));
      if (q >= QHB) { w *= hb; h *= hb; hot = Math.max(hot, (hb - 1) / .7 * .8); }
      // sonar ripples off the heartbeat (the first breath of the ANC ring)
      if (q >= QHB && q < QHB + 7) for (const [d0, amp] of [[0, .7]]) {
        const u = seg(q, QHB + d0, QHB + d0 + 6); if (u <= 0 || u >= 1) continue;
        fg.save(); fg.globalCompositeOperation = 'lighter'; fg.strokeStyle = `rgba(230,200,150,${.55 * amp * (1 - u)})`; fg.lineWidth = lerp(3, .8, u);
        fg.shadowColor = 'rgba(230,200,150,.7)'; fg.shadowBlur = 16; fg.beginPath(); fg.arc(540, 960, lerp(40, 330, eout(u)), 0, TAU); fg.stroke(); fg.restore();
      }
      if (q < QST) {
        halo(fg, x, y, w * 1.6, h * 1.6, .25 + .35 * hot + (q >= QG0 ? .15 : 0));
        goldBody(fg, x, y, w, h, round, 1, glow, hot);
      } else if (q < QB0 + 4) {
        // ANAMORPHIC STREAK (3 frames) then the BEND into the top arc of the ring
        const e = eout(seg(q, QST, QST + 3));
        const len = lerp(D * hb, 1080, e), core = lerp(D * hb, 3, e);
        const m = q < QB0 ? 0 : eio(seg(q, QB0, QB1));
        const fadeOut = 1 - seg(q, QB1 - .5, QB0 + 4);
        if (m <= 0) {
          // straight streak: halo 60 px + white-gold core + long faint flare
          halo(fg, 540, 960, len * .55, lerp(D, 34, e), .8);
          halo(fg, 540, 960, 900, 6, .35 * e, '255,240,215');
          fg.save(); fg.globalCompositeOperation = 'lighter'; fg.shadowColor = 'rgba(230,200,150,.95)'; fg.shadowBlur = 30;
          if (e < .999) goldBody(fg, 540, 960, len, core, 1, 1, 40, 1);
          else { fg.fillStyle = '#fff4dc'; fg.beginPath(); fg.roundRect(540 - len / 2, 960 - 1.5, len, 3, 1.5); fg.fill(); }
          fg.restore();
          // flicker of the flare
          const fl = .5 + .5 * Math.sin(q * 2.7);
          halo(fg, 540, 960, 140 + 40 * fl, 22, .4 * e);
        } else {
          // bend: each streak point lerps to its point on the projected ring arc (centre leads, ends follow)
          const N = 72, pts = [];
          for (let i = 0; i <= N; i++) {
            const s = i / N * 2 - 1, ms = eio(clamp(m * 1.35 - Math.abs(s) * .35));
            const p = CUP.project(CUP.at(Math.abs(s) * ARC0, s >= 0 ? 1 : -1));
            pts.push([lerp(540 + s * 540, p[0], ms), lerp(960, p[1], ms)]);
          }
          fg.save(); fg.globalCompositeOperation = 'lighter'; fg.globalAlpha = fadeOut; fg.lineCap = 'round'; fg.lineJoin = 'round';
          const path = () => { fg.beginPath(); pts.forEach(([px, py], i) => i ? fg.lineTo(px, py) : fg.moveTo(px, py)); };
          path(); fg.strokeStyle = 'rgba(230,200,150,.16)'; fg.lineWidth = 46; fg.stroke();
          path(); fg.strokeStyle = 'rgba(230,200,150,.35)'; fg.lineWidth = 14; fg.stroke();
          path(); fg.strokeStyle = '#fff4dc'; fg.lineWidth = 3; fg.shadowColor = 'rgba(230,200,150,.95)'; fg.shadowBlur = 26; fg.stroke();
          fg.restore();
        }
      }
    }

    // ---------------- ring heads: flares + shed sparks; the close burst at b19.75
    if (q >= QB0 + 2 && prog > .001) {
      fg.save(); fg.globalCompositeOperation = 'lighter';
      // sparks: emitted from each head, 5 per frame, life 11 frames
      const RATE = 5, LIFE = 11;
      const n0 = Math.max(0, Math.floor((q - LIFE - QB0 - 2) * RATE)), n1 = Math.floor((Math.min(q, QCL) - QB0 - 2) * RATE);
      for (let n = n0; n <= n1; n++) {
        const qe = QB0 + 2 + n / RATE, age = q - qe; if (age < 0 || age > LIFE) continue;
        for (const sd of [1, -1]) {
          const id = n * 2 + (sd > 0 ? 0 : 1);
          const a = ringProg(qe), p = CUP.project(CUP.at(a, sd));
          const ang = (rnd(id * 3.1) - .5) * TAU, sp = 2 + 9 * Math.pow(rnd(id * 5.7), 2);
          const vx = Math.cos(ang) * sp, vy = Math.sin(ang) * sp - 1.5;
          const x = p[0] + vx * age, y = p[1] + vy * age + .35 * age * age;
          const al = (1 - age / LIFE) * (.5 + .5 * rnd(id * 9.1));
          fg.strokeStyle = `rgba(255,${226 + Math.round(20 * rnd(id))},${170 + Math.round(40 * rnd(id * 2))},${al})`; fg.lineWidth = 1.6 + 1.6 * rnd(id * 4.4);
          fg.beginPath(); fg.moveTo(x, y); fg.lineTo(x - vx * 1.6, y - (vy + .7 * age) * 1.6); fg.stroke();
        }
      }
      // head flares
      if (prog < 1) for (const sd of [1, -1]) {
        const p = CUP.project(CUP.at(prog, sd));
        halo(fg, p[0], p[1], 70, 70, .55, '255,226,176');
        halo(fg, p[0], p[1], 150, 8, .45, '255,240,215');
        halo(fg, p[0], p[1], 18, 18, .9, '255,248,235');
      }
      fg.restore();
    }
    if (q >= QCL) {
      const d = q - QCL, p = CUP.project(CUP.at(1, 1));
      fg.save(); fg.globalCompositeOperation = 'lighter';
      const k = Math.exp(-d / 2.2);
      halo(fg, p[0], p[1], 520 * (.6 + .4 * k), 12, .7 * k + .12, '255,236,200');
      halo(fg, p[0], p[1], 12, 220 * k + 20, .5 * k, '255,236,200');
      halo(fg, p[0], p[1], 70, 70, .6 * k + .1, '255,220,160');
      // burst sparks
      for (let i = 0; i < 34; i++) {
        const age = d; if (age > 12) break;
        const ang = -Math.PI / 2 + (rnd(i * 7.7 + 900) - .5) * Math.PI * 1.9 + Math.PI, sp = 4 + 16 * Math.pow(rnd(i * 3.9 + 900), 1.5);
        const vx = Math.cos(ang) * sp, vy = Math.sin(ang) * sp;
        const x = p[0] + vx * age, y = p[1] + vy * age + .5 * age * age, al = (1 - age / 12);
        fg.strokeStyle = `rgba(247,214,160,${al})`; fg.lineWidth = 2; fg.beginPath(); fg.moveTo(x, y); fg.lineTo(x - vx * 1.4, y - vy * 1.4); fg.stroke();
      }
      fg.restore();
    }

    // ---------------- post FX choreography
    // b16.0 HIT: flash (warm white), punch zoom, heavy rgb, zoom blur, glitch, shake over one beat
    {
      if (q < 6) { fx.flash = Math.pow(1 - q / 6, 3.2); fx.flashColor = [.92, .9, .84]; }
      fx.zoom *= 1 + .12 * (1 - expoOut(clamp(q / 8)));
      fx.rgb = Math.max(fx.rgb, .0015 + .0285 * Math.max(0, 1 - q / 12));
      fx.zoomBlur = Math.max(fx.zoomBlur, .6 * Math.max(0, 1 - q / 6));
      if (q < 3) { fx.glitch = .5; fx.glitchSeed = F + 1; }
      const sh = .012 * Math.max(0, 1 - q / 12);
      fx.shake = [(rnd(F + 11) - .5) * 2 * sh, (rnd(F + 77) - .5) * 2 * sh];
      fx.displace = .03 * Math.max(0, 1 - q / 7); fx.displaceScale = 2.5;
    }
    // window cuts: 2-frame glitch slices + rgb kick + micro punch
    for (const c of [QW1, QW2, QW3]) {
      const d = q - c; if (d < 0 || d >= 3) continue;
      if (d < 2) { fx.glitch = Math.max(fx.glitch, .2); fx.glitchSeed = 40 + F; }
      fx.rgb = Math.max(fx.rgb, .0015 + .0065 * (1 - d / 3)); fx.zoom *= 1 + .02 * (1 - d / 3);
    }
    // shear: zoom blur + shake
    if (q >= QSH && q < QSH + 12) {
      const d = q - QSH;
      fx.zoomBlur = Math.max(fx.zoomBlur, .25 * tri(d - 7, 5));
      const sh = .006 * tri(d - 7, 5); fx.shake = [fx.shake[0] + (rnd(F + 5) - .5) * 2 * sh, fx.shake[1] + (rnd(F + 9) - .5) * 2 * sh];
      fx.rgb = Math.max(fx.rgb, .0015 + .006 * tri(d - 7, 5));
    }
    // heartbeat pump
    if (q >= QHB && q < QHB + 5) { const k = 1 - (q - QHB) / 5; fx.zoom *= 1 + .03 * k; fx.rgb = Math.max(fx.rgb, .0015 + .005 * k); }
    // streak + ring: big bloom
    if (q >= QST) { fx.bloom = q < QB0 ? 1.2 : lerp(1.2, 1.0, seg(q, QB0, QEND)); fx.bloomThreshold = q < QB0 ? .6 : .7; }
    if (q >= QST && q < QST + 4) { const k = 1 - (q - QST) / 4; fx.rgb = Math.max(fx.rgb, .0015 + .01 * k); }
    // the ring closes: a warm micro-flash + kick
    if (q >= QCL && q < QCL + 4) { const k = 1 - (q - QCL) / 4; fx.zoom *= 1 + .015 * k; fx.rgb = Math.max(fx.rgb, .0015 + .006 * k); }
  },
};
