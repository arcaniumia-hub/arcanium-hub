// LUMARC — "What if instead of presenting your business like this…" — 3D motion graphics (EN), 1080x1920, 30 s.
// Three.js scene (bloom, particles, neon rings, warp tunnel, orbiting glass panels) + 2D typography overlay.
// window.renderAt(t) draws one deterministic frame onto #out.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RGBShiftShader } from 'three/addons/shaders/RGBShiftShader.js';

const W = 1080, H = 1920;
const out = document.getElementById('out');
const o = out.getContext('2d');
const IMG = { before: document.getElementById('before'), logo: document.getElementById('logo') };
const C = { bg: '#0e0e14', white: '#faf9f6', muted: '#a6a6b8', blue: '#3b5bff', violet: '#8b3dff', g1: '#4f6bff', g2: '#6a55ff', g3: '#9a4dff' };
let ctx = o, T = 0;

// ---------- math
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const eout = x => { x = clamp(x); return 1 - Math.pow(1 - x, 3); };
const expo = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
const eback = x => { x = clamp(x); const c1 = 1.6, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const TAU = Math.PI * 2, DEG = Math.PI / 180;

// ---------- 2D helpers (draw into `ctx`)
function grad(x0, y0, x1, y1, a = C.g1, m = C.g2, b = C.g3) { const g = ctx.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, a); g.addColorStop(.45, m); g.addColorStop(1, b); return g; }
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function glass(x, y, w, h, r = 28, a = 1) {
  ctx.save(); ctx.globalAlpha *= a; rr(x, y, w, h, r); ctx.fillStyle = 'rgba(255,255,255,0.055)'; ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.14)'; ctx.lineWidth = 2; ctx.stroke(); ctx.restore();
}
const font = (size, w = 400) => `${w} ${size}px Outfit`;
function text(s, x, y, op = {}) {
  const { size = 60, w = 400, color = C.white, align = 'center', alpha = 1, blur = 0, gradient = false, spacing = 0, shadow = 0 } = op;
  if (alpha <= .003) return;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.font = font(size, w); ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.letterSpacing = spacing + 'px';
  if (blur > .3) ctx.filter = `blur(${blur}px)`;
  let fill = color;
  if (gradient) { const tw = ctx.measureText(s).width; const x0 = align === 'center' ? x - tw / 2 : align === 'right' ? x - tw : x; fill = grad(x0, y - size, x0 + tw, y); }
  if (shadow) { ctx.shadowColor = gradient ? 'rgba(122,85,255,.8)' : 'rgba(0,0,0,.65)'; ctx.shadowBlur = shadow; }
  ctx.fillStyle = fill; ctx.fillText(s, x, y); ctx.restore();
}
function maskText(s, x, y, k, op = {}) {
  const size = op.size || 60;
  ctx.save(); ctx.beginPath(); ctx.rect(0, y - size * 1.05, W, size * 1.35); ctx.clip();
  text(s, x, y + (1 - expo(k)) * size * 1.2, op); ctx.restore();
}
function fitSize(s, w, size, max) { ctx.font = font(size, w); const tw = ctx.measureText(s).width; return tw > max ? size * max / tw : size; }

// ---------- three.js setup
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, .05, 300);
const composer = new EffectComposer(renderer); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), .8, .45, .5); composer.addPass(bloom);
const rgb = new ShaderPass(RGBShiftShader); rgb.uniforms.amount.value = 0; composer.addPass(rgb);
composer.addPass(new OutputPass());

const LBLUE = new THREE.Vector3(.044, .105, 1.0), LVIOL = new THREE.Vector3(.258, .047, 1.0);
const glsl = v => `vec3(${v.x},${v.y},${v.z})`;

// background dome with soft brand glows
const bgMat = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false, uniforms: { uGlow: { value: 1 } },
  vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }`,
  fragmentShader: `varying vec3 vDir; uniform float uGlow;
    void main(){ vec3 base = vec3(.0044,.0044,.0070);
      float b = pow(max(dot(vDir, normalize(vec3(-.55,.7,-1.))),0.), 5.);
      float v = pow(max(dot(vDir, normalize(vec3(.6,-.6,-1.))),0.), 5.);
      float c = pow(max(dot(vDir, normalize(vec3(0.,.1,1.))),0.), 7.);
      gl_FragColor = vec4(base + uGlow*(${glsl(LBLUE)}*b*.07 + ${glsl(LVIOL)}*v*.08 + ${glsl(LVIOL)}*c*.04), 1.); }`,
});
const dome = new THREE.Mesh(new THREE.SphereGeometry(150, 32, 16), bgMat); scene.add(dome);

// ---------- neon rings (logo mark)
function ringMaterial(phase) {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uI: { value: 0 }, uT: { value: 0 }, uPhase: { value: phase } },
    vertexShader: `varying vec3 vN; varying vec3 vV; varying float vA;
      void main(){ vA = atan(position.y, position.x); vec4 mv = modelViewMatrix * vec4(position,1.); vV = mv.xyz; vN = normalize(normalMatrix * normal); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `varying vec3 vN; varying vec3 vV; varying float vA; uniform float uI; uniform float uT; uniform float uPhase;
      void main(){ float k = .5 + .5*sin(vA + uT*.9 + uPhase);
        vec3 c = mix(${glsl(LBLUE)}, ${glsl(LVIOL)}, k);
        float f = 1. - abs(dot(normalize(vN), normalize(-vV)));
        vec3 col = c*(.35 + 1.5*pow(f,1.6)) + vec3(.75,.7,1.)*pow(f,6.)*.7 + vec3(1.)*pow(1.-f,12.)*.25;
        gl_FragColor = vec4(col*uI, 1.); }`,
  });
}
const ringGroup = new THREE.Group(); scene.add(ringGroup);
const ringEulers = [new THREE.Euler(1.15, 0, -.5), new THREE.Euler(1.0, 1.15, .55)];
const ringR = [1.6, 1.42], ringTube = .085;
const rings = ringEulers.map((e, i) => {
  const m = new THREE.Mesh(new THREE.TorusGeometry(ringR[i], ringTube, 48, 360), ringMaterial(i * 2.2));
  m.rotation.copy(e); ringGroup.add(m); return m;
});
// star flare at the core
function flareTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d');
  const g = x.createRadialGradient(256, 256, 0, 256, 256, 256);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.08, 'rgba(230,220,255,.9)'); g.addColorStop(.3, 'rgba(150,120,255,.25)'); g.addColorStop(1, 'rgba(120,90,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, 512, 512);
  x.globalCompositeOperation = 'lighter';
  [[0, 1], [1, 0]].forEach(([a, b]) => { const lg = x.createLinearGradient(256 - a * 256, 256 - b * 256, 256 + a * 256, 256 + b * 256);
    lg.addColorStop(0, 'rgba(255,255,255,0)'); lg.addColorStop(.5, 'rgba(255,255,255,.9)'); lg.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = lg; if (a) x.fillRect(0, 252, 512, 8); else x.fillRect(252, 0, 8, 512); });
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const flare = new THREE.Sprite(new THREE.SpriteMaterial({ map: flareTexture(), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
flare.material.color.setScalar(1.1); ringGroup.add(flare);

// points sampled on the two torus surfaces (ringGroup space)
function torusPoint(i, rI) {
  const u = rnd(i * 3.1) * TAU, v = rnd(i * 7.7) * TAU, R = ringR[rI], r = ringTube * 1.6 * Math.sqrt(rnd(i * 1.3));
  const p = new THREE.Vector3((R + r * Math.cos(v)) * Math.cos(u), (R + r * Math.cos(v)) * Math.sin(u), r * Math.sin(v));
  return p.applyEuler(ringEulers[rI]);
}

// ---------- particles that form the rings
const NP = 7000;
const pGeo = new THREE.BufferGeometry();
{
  const st = new Float32Array(NP * 3), tg = new Float32Array(NP * 3), rd = new Float32Array(NP * 3);
  for (let i = 0; i < NP; i++) {
    const th = rnd(i + .1) * TAU, ph = Math.acos(2 * rnd(i + .2) - 1), r = 5 + 11 * Math.pow(rnd(i + .3), .6);
    st.set([r * Math.sin(ph) * Math.cos(th), r * Math.sin(ph) * Math.sin(th) * .8, r * Math.cos(ph)], i * 3);
    const p = i % 10 < 8 ? torusPoint(i, i % 2) : new THREE.Vector3(Math.cos(th) * (2 + 1.5 * rnd(i + .4)), (rnd(i + .5) - .5) * .6, Math.sin(th) * (2 + 1.5 * rnd(i + .4)));
    tg.set([p.x, p.y, p.z], i * 3);
    rd.set([rnd(i + .6), rnd(i + .7), rnd(i + .8)], i * 3);
  }
  pGeo.setAttribute('position', new THREE.BufferAttribute(st, 3));
  pGeo.setAttribute('aTarget', new THREE.BufferAttribute(tg, 3));
  pGeo.setAttribute('aRand', new THREE.BufferAttribute(rd, 3));
}
const pMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uMorph: { value: 0 }, uTime: { value: 0 }, uSize: { value: 1 }, uAlpha: { value: 1 }, uSwirl: { value: 3 }, uPush: { value: 0 } },
  vertexShader: `attribute vec3 aTarget; attribute vec3 aRand; uniform float uMorph; uniform float uTime; uniform float uSize; uniform float uSwirl; uniform float uPush;
    varying vec3 vCol; varying float vM;
    void main(){ float d = aRand.x*.45; float m = clamp((uMorph - d)/.55, 0., 1.); m = m<.5 ? 4.*m*m*m : 1.-pow(-2.*m+2.,3.)/2.;
      vec3 p = mix(position, aTarget, m);
      float ang = (1.-m)*uSwirl*(.6+aRand.z); float cs = cos(ang), sn = sin(ang); p.xz = mat2(cs,-sn,sn,cs)*p.xz;
      p += (.02+.25*(1.-m))*vec3(sin(uTime*1.3+aRand.z*20.), cos(uTime*1.1+aRand.y*17.), sin(uTime*.9+aRand.x*13.));
      p.z += uPush*(1.-m)*(.5+aRand.y);
      vec4 mv = modelViewMatrix*vec4(p,1.);
      gl_PointSize = min(uSize*(.4+aRand.y*1.2)*(95./max(.2,-mv.z)), 10.);
      vCol = (mix(${glsl(LBLUE)}, ${glsl(LVIOL)}, aRand.z)*(.6 + .45*m) + vec3(.35)*step(.94,aRand.y))*.9; vM = m;
      gl_Position = projectionMatrix*mv; }`,
  fragmentShader: `uniform float uAlpha; varying vec3 vCol; varying float vM;
    void main(){ float r = length(gl_PointCoord-.5); float a = smoothstep(.5,0.,r); gl_FragColor = vec4(vCol*a*uAlpha, 1.); }`,
});
const particles = new THREE.Points(pGeo, pMat); ringGroup.add(particles);

// ---------- streaming star field (warp)
const NS = 2600;
const sGeo = new THREE.BufferGeometry();
{
  const a = new Float32Array(NS * 3), rd = new Float32Array(NS);
  for (let i = 0; i < NS; i++) { const th = rnd(i + 50) * TAU, r = .8 + 9 * Math.pow(rnd(i + 51), .7); a.set([Math.cos(th) * r, Math.sin(th) * r * 1.6, -rnd(i + 52) * 80], i * 3); rd[i] = rnd(i + 53); }
  sGeo.setAttribute('position', new THREE.BufferAttribute(a, 3)); sGeo.setAttribute('aR', new THREE.BufferAttribute(rd, 1));
}
const sMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uDist: { value: 0 }, uAlpha: { value: 0 }, uStretch: { value: 0 } },
  vertexShader: `attribute float aR; uniform float uDist; uniform float uStretch; varying float vA; varying float vR;
    void main(){ vec3 p = position; p.z = mod(p.z + uDist, 80.) - 78.;
      vec4 mv = modelViewMatrix*vec4(p,1.); gl_PointSize = min((1. + 1.6*aR + uStretch*2.)*(14./max(.3,-mv.z)), 5.);
      vA = smoothstep(-78.,-60.,p.z)*smoothstep(1.,-3.,p.z); vR = aR; gl_Position = projectionMatrix*mv; }`,
  fragmentShader: `uniform float uAlpha; varying float vA; varying float vR;
    void main(){ float r = length(gl_PointCoord-.5); float a = smoothstep(.5,0.,r);
      vec3 c = mix(vec3(.35,.45,1.), vec3(.6,.35,1.), vR)*.9; gl_FragColor = vec4(c*a*vA*uAlpha,1.); }`,
});
const stars = new THREE.Points(sGeo, sMat); scene.add(stars);

// ---------- flyer: 12x12 tiles that shatter
const flyerTex = new THREE.Texture(IMG.before); flyerTex.colorSpace = THREE.SRGBColorSpace;
const flyerGroup = new THREE.Group(); scene.add(flyerGroup);
const NT = 12, FS = 2.18, tiles = [];
const tileMat = new THREE.MeshBasicMaterial({ map: flyerTex, transparent: true, side: THREE.DoubleSide, depthWrite: false });
for (let r = 0; r < NT; r++) for (let c = 0; c < NT; c++) {
  const g = new THREE.PlaneGeometry(FS / NT, FS / NT);
  const uv = g.attributes.uv; for (let k = 0; k < uv.count; k++) uv.setXY(k, (c + uv.getX(k)) / NT, 1 - (r + 1 - uv.getY(k)) / NT);
  const m = new THREE.Mesh(g, tileMat.clone());
  const bx = -FS / 2 + (c + .5) * FS / NT, by = FS / 2 - (r + .5) * FS / NT;
  m.userData = { bx, by, i: r * NT + c, d: Math.hypot(bx, by) / (FS * .7) };
  flyerGroup.add(m); tiles.push(m);
}
// desaturated flyer (before/after) + its dissolve particles
const desat = document.createElement('canvas'); desat.width = desat.height = 1024;
const desatTex = new THREE.CanvasTexture(desat); desatTex.colorSpace = THREE.SRGBColorSpace;
const flyerFlat = new THREE.Mesh(new THREE.PlaneGeometry(2.3, 2.3), new THREE.MeshBasicMaterial({ map: desatTex, transparent: true, depthWrite: false }));
scene.add(flyerFlat);
const ND = 90 * 90;
const dGeo = new THREE.BufferGeometry();
const dMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uK: { value: 0 }, uRing: { value: new THREE.Matrix4() }, uFlyer: { value: new THREE.Matrix4() }, uAlpha: { value: 0 }, uTime: { value: 0 } },
  vertexShader: `attribute vec3 aTarget; attribute vec3 aCol; attribute float aD; uniform float uK; uniform mat4 uRing; uniform mat4 uFlyer; uniform float uTime;
    varying vec3 vCol; varying float vK;
    void main(){ float k = clamp((uK - aD*.5)/.5, 0., 1.); float e = k<.5 ? 4.*k*k*k : 1.-pow(-2.*k+2.,3.)/2.;
      vec3 a = (uFlyer*vec4(position,1.)).xyz; vec3 b = (uRing*vec4(aTarget,1.)).xyz;
      vec3 mid = mix(a,b,.5) + vec3(sin(aD*40.)*1.2, 1.2 + cos(aD*30.), 1.5);
      vec3 p = mix(mix(a,mid,e), mix(mid,b,e), e);
      vec4 mv = modelViewMatrix*vec4(p,1.); gl_PointSize = min((2.8 - 1.2*e)*(30./max(.2,-mv.z)), 8.);
      vCol = mix(aCol*.85, mix(${glsl(LBLUE)}, ${glsl(LVIOL)}, aD)*1.1, smoothstep(.0,.6,e)); vK = k; gl_Position = projectionMatrix*mv; }`,
  fragmentShader: `uniform float uAlpha; varying vec3 vCol; varying float vK;
    void main(){ float r = length(gl_PointCoord-.5); float a = smoothstep(.5,.1,r); gl_FragColor = vec4(vCol*a*uAlpha*step(.001,vK), 1.); }`,
});
const dissolve = new THREE.Points(dGeo, dMat); scene.add(dissolve);
function buildDissolve() {
  const x = desat.getContext('2d');
  x.filter = 'grayscale(.8) brightness(.72)'; x.drawImage(IMG.before, 0, 0, 1024, 1024); x.filter = 'none'; desatTex.needsUpdate = true;
  const sm = document.createElement('canvas'); sm.width = sm.height = 90; const sx = sm.getContext('2d'); sx.drawImage(desat, 0, 0, 90, 90);
  const px = sx.getImageData(0, 0, 90, 90).data;
  const pos = new Float32Array(ND * 3), tg = new Float32Array(ND * 3), col = new Float32Array(ND * 3), dd = new Float32Array(ND);
  for (let i = 0; i < ND; i++) {
    const cx = i % 90, cy = Math.floor(i / 90);
    pos.set([(cx / 89 - .5) * 2.3, (.5 - cy / 89) * 2.3, 0], i * 3);
    const tp = torusPoint(i + 9000, i % 2); tg.set([tp.x, tp.y, tp.z], i * 3);
    const lin = v => Math.pow(v / 255, 2.2);
    col.set([lin(px[i * 4]), lin(px[i * 4 + 1]), lin(px[i * 4 + 2])], i * 3);
    dd[i] = clamp(1 - cy / 89 * .7 + (rnd(i + 77) - .5) * .3);
  }
  dGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); dGeo.setAttribute('aTarget', new THREE.BufferAttribute(tg, 3));
  dGeo.setAttribute('aCol', new THREE.BufferAttribute(col, 3)); dGeo.setAttribute('aD', new THREE.BufferAttribute(dd, 1));
}

// ---------- warp-tunnel feed cards
const cardTex = [];
for (let k = 0; k < 8; k++) {
  const c = document.createElement('canvas'); c.width = 300; c.height = 380; ctx = c.getContext('2d');
  rr(4, 4, 292, 372, 26); ctx.fillStyle = 'rgba(22,22,34,.92)'; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.22)'; ctx.lineWidth = 3; ctx.stroke();
  const pal = [['#3b5bff', '#8b3dff'], ['#8b3dff', '#ff5aa0'], ['#25c8aa', '#3b5bff'], ['#ff8c50', '#8b3dff'], ['#ff5aa0', '#ffb347'], ['#3b5bff', '#25c8aa'], ['#6a55ff', '#ff8c50'], ['#9a4dff', '#3b5bff']][k];
  const g = ctx.createLinearGradient(0, 60, 300, 290); g.addColorStop(0, pal[0]); g.addColorStop(1, pal[1]);
  rr(18, 62, 264, 230, 18); ctx.fillStyle = g; ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.18)'; for (let j = 0; j < 3; j++) { ctx.beginPath(); ctx.arc(40 + rnd(k * 9 + j) * 220, 90 + rnd(k * 7 + j) * 180, 30 + 40 * rnd(k + j), 0, TAU); ctx.fill(); }
  ctx.fillStyle = 'rgba(255,255,255,.35)'; ctx.beginPath(); ctx.arc(36, 34, 14, 0, TAU); ctx.fill(); rr(58, 26, 110, 14, 7); ctx.fill();
  rr(18, 310, 180, 14, 7); ctx.fill(); rr(18, 336, 120, 14, 7); ctx.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; cardTex.push(t);
}
ctx = o;
const tunnel = new THREE.Group(); scene.add(tunnel);
const cards = [];
const TROWS = 18, TGAP = 2.6, TLEN = TROWS * TGAP;
for (let r = 0; r < TROWS; r++) for (let k = 0; k < 4; k++) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(1.25, 1.58), new THREE.MeshBasicMaterial({ map: cardTex[(r * 4 + k) % 8], transparent: true, depthWrite: false, side: THREE.DoubleSide }));
  const ang = (k / 4) * TAU + r * .7 + .4;
  m.userData = { ang, z0: r * TGAP + rnd(r * 4 + k) * 1.2, rad: 1.85 + .5 * rnd(r * 9 + k) };
  tunnel.add(m); cards.push(m);
}

// ---------- service panels (glass, animated canvas textures)
const SERV = [
  ['Social Media Management', 'Your feed, alive every single week.'],
  ['Designs & Posts', 'A big-brand look on every post.'],
  ['Carousels', 'Swipeable posts that get saved.'],
  ['Reels & Video', 'Videos that stop the thumb.'],
  ['Video Editing', 'From raw clips to scroll-stoppers.'],
  ['Custom Websites', 'Live in up to 2 weeks.'],
];
const S0 = 11.0, SD = 1.5;
const panels = [];
for (let i = 0; i < 6; i++) {
  const c = document.createElement('canvas'); c.width = 720; c.height = 900;
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 2.75), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, side: THREE.DoubleSide }));
  m.userData = { c, t }; m.renderOrder = 5; scene.add(m); panels.push(m);
}

// mini-graphics, drawn in a 1080-wide reference frame (region x 110..970, y 700..1520)
function gSocial(lt) {
  const cw = 104, gx = W / 2 - 3.5 * cw, gy = 950;
  glass(gx - 30, gy - 110, cw * 7 + 60, cw * 5 + 140, 30);
  text('OCTOBER', W / 2, gy - 45, { size: 34, w: 500, color: C.muted, spacing: 6 });
  const on = [1, 3, 5, 8, 10, 12, 15, 17, 19, 22, 24, 26, 29, 31, 33];
  for (let i = 0; i < 35; i++) {
    const x = gx + (i % 7) * cw, y = gy + Math.floor(i / 7) * cw;
    rr(x + 8, y + 8, cw - 16, cw - 16, 16); ctx.fillStyle = 'rgba(255,255,255,.05)'; ctx.fill();
    const k = on.indexOf(i);
    if (k >= 0) { const p = eback(seg(lt, .15 + k * .05, .4 + k * .05)); if (p > 0) { ctx.save(); ctx.translate(x + cw / 2, y + cw / 2); ctx.scale(p, p); rr(-34, -34, 68, 68, 16); ctx.fillStyle = grad(-34, -34, 34, 34); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-14, 0); ctx.lineTo(-3, 11); ctx.lineTo(16, -10); ctx.stroke(); ctx.restore(); } }
  }
}
function cursor(x, y) { ctx.save(); ctx.translate(x, y); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 44); ctx.lineTo(12, 33); ctx.lineTo(22, 54); ctx.lineTo(30, 50); ctx.lineTo(20, 30); ctx.lineTo(36, 30); ctx.closePath(); ctx.fill(); ctx.restore(); }
function gArt(lt) {
  const x = W / 2 - 330, y = 760, s = 660; glass(x, y, s, s, 34);
  const p = i => eback(seg(lt, .1 + i * .12, .55 + i * .12));
  ctx.save(); ctx.translate((1 - p(0)) * -300, 0); ctx.globalAlpha = clamp(p(0) * 2); ctx.beginPath(); ctx.arc(x + s * .68, y + s * .38, 170, 0, TAU); ctx.fillStyle = grad(x + 300, y, x + s, y + 400); ctx.fill(); ctx.restore();
  ctx.save(); ctx.translate(0, (1 - p(1)) * 260); ctx.globalAlpha = clamp(p(1) * 2); rr(x + 50, y + 70, 290, 46, 12); ctx.fillStyle = '#fff'; ctx.fill(); rr(x + 50, y + 135, 220, 46, 12); ctx.fill(); ctx.restore();
  ctx.save(); ctx.translate((1 - p(2)) * 300, 0); ctx.globalAlpha = clamp(p(2) * 2); rr(x + 50, y + 420, 400, 22, 11); ctx.fillStyle = 'rgba(255,255,255,.45)'; ctx.fill(); rr(x + 50, y + 462, 320, 22, 11); ctx.fill(); ctx.restore();
  ctx.save(); const q = p(3); ctx.translate(x + 150, y + 570); ctx.scale(q, q); rr(-100, -38, 200, 76, 38); ctx.fillStyle = grad(-100, 0, 100, 0); ctx.fill(); ctx.restore();
  const c = eout(seg(lt, .9, 1.2)); cursor(lerp(x + s + 60, x + 175, c), lerp(y + s + 60, y + 585, c));
}
function gCarousel(lt) {
  const cw = 560, ch = 640, cy = 800, idx = clamp((lt - .2) / .38, 0, 3), f = Math.floor(idx), pos = f + eio(idx - f);
  ctx.save(); ctx.beginPath(); ctx.rect(110, cy - 40, 860, ch + 80); ctx.clip();
  for (let i = 0; i < 5; i++) {
    const x = W / 2 - cw / 2 + (i - pos) * (cw + 40); glass(x, cy, cw, ch, 30);
    const cols = [[C.blue, C.violet], [C.violet, '#ff5aa0'], ['#25c8aa', C.blue], ['#ff8c50', C.violet], [C.blue, '#25c8aa']][i];
    const g = ctx.createLinearGradient(x, cy, x + cw, cy + ch); g.addColorStop(0, cols[0]); g.addColorStop(1, cols[1]);
    rr(x + 30, cy + 30, cw - 60, ch * .55, 20); ctx.fillStyle = g; ctx.fill();
    text(String(i + 1).padStart(2, '0') + '/05', x + 60, cy + ch * .55 + 110, { size: 40, w: 500, align: 'left' });
    ctx.fillStyle = 'rgba(255,255,255,.3)'; rr(x + 60, cy + ch * .55 + 140, cw - 160, 18, 9); ctx.fill(); rr(x + 60, cy + ch * .55 + 175, cw - 260, 18, 9); ctx.fill();
  }
  ctx.restore();
  for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.arc(W / 2 - 60 + i * 30, cy + ch + 50, Math.abs(i - pos) < .5 ? 9 : 6, 0, TAU); ctx.fillStyle = Math.abs(i - pos) < .5 ? C.white : 'rgba(255,255,255,.3)'; ctx.fill(); }
}
function gReel(lt) {
  const pw = 420, ph = 760, x = W / 2 - pw / 2, y = 730;
  rr(x - 14, y - 14, pw + 28, ph + 28, 64); ctx.fillStyle = '#1d1d29'; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.18)'; ctx.lineWidth = 3; ctx.stroke();
  ctx.save(); rr(x, y, pw, ph, 52); ctx.clip();
  const g = ctx.createLinearGradient(x, y + Math.sin(lt * 2) * 200, x + pw, y + ph); g.addColorStop(0, C.violet); g.addColorStop(.5, '#ff5aa0'); g.addColorStop(1, C.blue);
  ctx.fillStyle = g; ctx.fillRect(x, y, pw, ph);
  for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.arc(x + pw * rnd(i), y + ph * rnd(i + 9) - lt * 120 * (1 + rnd(i)), 60 + 80 * rnd(i + 3), 0, TAU); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fill(); }
  rr(x + 30, y + ph - 40, pw - 60, 8, 4); ctx.fillStyle = 'rgba(255,255,255,.3)'; ctx.fill(); rr(x + 30, y + ph - 40, (pw - 60) * clamp(lt / 1.4), 8, 4); ctx.fillStyle = '#fff'; ctx.fill();
  ctx.restore();
  const p = eback(seg(lt, .1, .45)) * (1 - eio(seg(lt, .7, .9)));
  if (p > 0) { ctx.save(); ctx.translate(W / 2, y + ph / 2); ctx.scale(p, p); ctx.beginPath(); ctx.arc(0, 0, 70, 0, TAU); ctx.fillStyle = 'rgba(255,255,255,.25)'; ctx.fill(); ctx.beginPath(); ctx.moveTo(-20, -32); ctx.lineTo(36, 0); ctx.lineTo(-20, 32); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill(); ctx.restore(); }
  for (let i = 0; i < 7; i++) {
    const u = seg(lt, .5 + i * .1, 1.3 + i * .1); if (u <= 0 || u >= 1) continue;
    ctx.save(); ctx.translate(x + pw - 60 + Math.sin(u * 6 + i) * 30, y + ph - 160 - u * 420); ctx.globalAlpha = 1 - u;
    ctx.beginPath(); ctx.moveTo(0, 12); ctx.bezierCurveTo(-34, -12, -16, -38, 0, -20); ctx.bezierCurveTo(16, -38, 34, -12, 0, 12); ctx.fillStyle = '#ff4f7a'; ctx.fill(); ctx.restore();
  }
}
function gEdit(lt) {
  const x = 120, y = 820, w = W - 240, h = 520; glass(x, y, w, h, 30);
  [[C.blue, [0, .32, .55, .8]], [C.violet, [.1, .45, .7]], ['#25c8aa', [0, .6]]].forEach(([col, starts], ti) => {
    const ty = y + 120 + ti * 120;
    text(['V1', 'V2', 'A1'][ti], x + 50, ty + 52, { size: 30, w: 500, color: C.muted, align: 'left' });
    starts.forEach((s0, ci) => {
      const s1 = ci + 1 < starts.length ? starts[ci + 1] - .02 : 1, p = expo(seg(lt, .05 + ti * .1 + ci * .07, .45 + ti * .1 + ci * .07));
      const cx = x + 120 + (w - 160) * s0 + (1 - p) * 500, cwid = (w - 160) * (s1 - s0);
      ctx.save(); ctx.globalAlpha = p; rr(cx, ty, cwid, 76, 14); ctx.fillStyle = col; ctx.fill(); ctx.fillStyle = 'rgba(255,255,255,.2)';
      if (ti === 2) for (let b = 0; b < cwid / 10; b++) { const bh = 10 + 40 * Math.abs(Math.sin(b * .7 + ci)); ctx.fillRect(cx + 6 + b * 10, ty + 38 - bh / 2, 5, bh); }
      ctx.restore();
    });
  });
  const ph = x + 120 + (w - 160) * clamp((lt - .5) / .9);
  ctx.fillStyle = '#fff'; ctx.fillRect(ph - 2, y + 70, 4, h - 110); ctx.beginPath(); ctx.moveTo(ph - 16, y + 60); ctx.lineTo(ph + 16, y + 60); ctx.lineTo(ph, y + 84); ctx.closePath(); ctx.fill();
  const cut = seg(lt, .95, 1.15); if (cut > 0 && cut < 1) { ctx.fillStyle = `rgba(255,255,255,${1 - cut})`; ctx.fillRect(x + 120 + (w - 160) * .55 - 4, y + 100, 8, 360); }
  text('00:00:' + String(Math.floor(clamp((lt - .5) / .9) * 24)).padStart(2, '0') + ':12', W / 2, y + 60, { size: 34, w: 500, color: C.muted, spacing: 3 });
}
function gSite(lt) {
  const x = 120, y = 740, w = W - 240, h = 760; glass(x, y, w, h, 30);
  ctx.fillStyle = 'rgba(255,255,255,.06)'; rr(x, y, w, 70, [30, 30, 0, 0]); ctx.fill();
  ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => { ctx.beginPath(); ctx.arc(x + 46 + i * 34, y + 35, 10, 0, TAU); ctx.fillStyle = c; ctx.fill(); });
  rr(x + 170, y + 18, w - 340, 34, 17); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fill();
  text('yourbusiness.com', x + w / 2, y + 45, { size: 24, color: C.muted });
  const p = i => expo(seg(lt, .1 + i * .13, .5 + i * .13));
  ctx.save(); ctx.globalAlpha = p(0); rr(x + 40, y + 110 + (1 - p(0)) * 60, w - 80, 280, 22); ctx.fillStyle = grad(x, y, x + w, y + 300); ctx.fill(); ctx.restore();
  ctx.save(); ctx.globalAlpha = p(1); ctx.fillStyle = '#fff'; rr(x + 80, y + 180, 380, 40, 10); ctx.fill(); rr(x + 80, y + 240, 280, 40, 10); ctx.fill(); ctx.restore();
  for (let i = 0; i < 3; i++) { ctx.save(); ctx.globalAlpha = p(2 + i * .5); rr(x + 40 + i * ((w - 80) / 3), y + 430 + (1 - p(2 + i * .5)) * 80, (w - 80) / 3 - 24, 190, 18); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fill(); ctx.restore(); }
  const bp = eback(seg(lt, .75, 1.05)); ctx.save(); ctx.translate(x + w / 2, y + 680); ctx.scale(bp, bp); rr(-140, -36, 280, 72, 36); ctx.fillStyle = '#fff'; ctx.fill(); text('Book now', 0, 12, { size: 30, w: 600, color: '#111' }); ctx.restore();
  const c = eout(seg(lt, 1.0, 1.25)); cursor(lerp(x + w - 40, x + w / 2 + 40, c), lerp(y + h + 80, y + 690, c));
  const rp = seg(lt, 1.25, 1.5); if (rp > 0 && rp < 1) { ctx.beginPath(); ctx.arc(x + w / 2 + 40, y + 690, 20 + 80 * rp, 0, TAU); ctx.strokeStyle = `rgba(255,255,255,${1 - rp})`; ctx.lineWidth = 4; ctx.stroke(); }
}
const GFX = [gSocial, gArt, gCarousel, gReel, gEdit, gSite];
function drawPanel(i, lt, active) {
  const { c, t } = panels[i].userData; ctx = c.getContext('2d');
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, 720, 900);
  rr(6, 6, 708, 888, 46); ctx.fillStyle = 'rgba(14,14,22,.9)'; ctx.fill();
  const hg = ctx.createLinearGradient(0, 0, 720, 900); hg.addColorStop(0, 'rgba(110,120,255,.16)'); hg.addColorStop(.5, 'rgba(255,255,255,0)'); hg.addColorStop(1, 'rgba(154,77,255,.14)');
  ctx.fillStyle = hg; ctx.fill();
  ctx.lineWidth = 4; ctx.strokeStyle = active ? grad(0, 0, 720, 900) : 'rgba(255,255,255,.18)'; ctx.stroke();
  text(String(i + 1).padStart(2, '0'), 48, 92, { size: 46, w: 300, gradient: true, align: 'left' });
  text(SERV[i][0].toUpperCase(), 672, 84, { size: 24, w: 500, color: C.muted, align: 'right', spacing: 3 });
  ctx.save(); const s = .78; ctx.setTransform(s, 0, 0, s, (720 - 860 * s) / 2 - 110 * s, 120 + (780 - 820 * s) / 2 - 700 * s);
  GFX[i](lt); ctx.restore();
  t.needsUpdate = true; ctx = o;
}

// ---------- 2D overlays
let NOISE = [];
function makeNoise() {
  for (let n = 0; n < 4; n++) { const c = document.createElement('canvas'); c.width = 540; c.height = 960; const x = c.getContext('2d'); const d = x.createImageData(540, 960);
    for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); NOISE.push(c); }
}
function grain(a) { o.save(); o.globalCompositeOperation = 'overlay'; o.globalAlpha = a; o.drawImage(NOISE[Math.floor(T * 15) % 4], 0, 0, W, H); o.restore(); }
function vignette(a) { const g = o.createRadialGradient(W / 2, H / 2, H * .3, W / 2, H / 2, H * .75); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`); o.fillStyle = g; o.fillRect(0, 0, W, H); }
function flash(a, col = '255,255,255') { if (a > 0) { o.fillStyle = `rgba(${col},${a})`; o.fillRect(0, 0, W, H); } }
function scrim(y0, y1, a) { const g = o.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, `rgba(8,8,14,${a})`); g.addColorStop(1, 'rgba(8,8,14,0)'); o.fillStyle = g; o.fillRect(0, Math.min(y0, y1), W, Math.abs(y1 - y0)); }
function chroma(s, x, y, size, w, k) { // RGB-split slam text
  const off = 14 * k;
  o.save(); o.globalCompositeOperation = 'lighter';
  text(s, x - off, y, { size, w, color: 'rgba(255,40,90,.85)' }); text(s, x + off, y, { size, w, color: 'rgba(40,200,255,.85)' });
  o.restore(); text(s, x, y, { size, w, gradient: true, shadow: 50 });
}
function speedLines(a) {
  if (a <= 0) return; o.save(); o.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 60; i++) {
    const ang = rnd(i) * TAU, r0 = 260 + ((rnd(i + 9) * 900 + T * 2600 * (0.6 + rnd(i + 3))) % 900), len = 120 + 260 * rnd(i + 4);
    o.strokeStyle = `rgba(${rnd(i + 5) > .5 ? '140,160,255' : '190,140,255'},${.35 * a})`; o.lineWidth = 2 + 2 * rnd(i + 6);
    o.beginPath(); o.moveTo(W / 2 + Math.cos(ang) * r0, H / 2 + Math.sin(ang) * r0 * 1.4); o.lineTo(W / 2 + Math.cos(ang) * (r0 + len), H / 2 + Math.sin(ang) * (r0 + len) * 1.4); o.stroke();
  }
  o.restore();
}

// ---------- the "before" (pure 2D)
const FLY_Y = 1010, FLY_PX = 960;
function drawBefore(t, alpha) {
  o.save(); o.globalAlpha = alpha;
  o.fillStyle = '#1b1b1f'; o.fillRect(0, 0, W, H);
  const z = 1 + .03 * Math.min(t, 3.6) / 3.6, sz = FLY_PX * z;
  if (IMG.before.naturalWidth) o.drawImage(IMG.before, W / 2 - sz / 2, FLY_Y - sz / 2, sz, sz);
  o.restore();
}
function beforeText(t) {
  const a = eout(seg(t, .15, .5)) * (1 - seg(t, 3.75, 3.95));
  if (a > 0) {
    o.save(); o.globalAlpha = a; o.font = font(50, 500);
    const l1 = 'What if instead of presenting', l2 = 'your business like this...';
    const w = Math.max(o.measureText(l1).width, o.measureText(l2).width) + 80;
    rr(W / 2 - w / 2, 270, w, 150, 28); o.fillStyle = '#fff'; o.fill(); o.restore();
    text(l1, W / 2, 333, { size: 50, w: 500, color: '#111', alpha: a }); text(l2, W / 2, 395, { size: 50, w: 500, color: '#111', alpha: a });
  }
  text('(just like everyone else)', W / 2, 1600, { size: 44, w: 300, color: '#9a9aa6', alpha: eout(seg(t, 1.6, 2.0)) * (1 - seg(t, 3.6, 3.8)) });
}

// ---------- per-frame 3D state
const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
const FLY_SCREEN = { x: W / 2, y: 600, bottom: 840 };
function hideAll() {
  ringGroup.visible = particles.visible = flare.visible = false; flyerGroup.visible = false; flyerFlat.visible = false; dissolve.visible = false;
  tunnel.visible = false; stars.visible = false; panels.forEach(p => p.visible = false);
}
function setRings(I, t) { ringGroup.visible = true; rings.forEach(r => { r.material.uniforms.uI.value = I; r.material.uniforms.uT.value = t; }); }
function placeCamera(pos, look, roll = 0) { camera.position.copy(pos); camera.up.set(Math.sin(roll), Math.cos(roll), 0); camera.lookAt(look); }
function warpDist(lt) { // distance flown in the tunnel; hard stop at 1.6 s
  const v = 34, acc = .3, stop = 1.6, tau = .07;
  const d = u => u < acc ? v * u * u / (2 * acc) : v * acc / 2 + v * (u - acc);
  return lt < stop ? d(lt) : d(stop) + v * tau * (1 - Math.exp(-(lt - stop) / tau));
}

function render3D(t) {
  hideAll();
  bloom.strength = .8; bloom.radius = .45; rgb.uniforms.amount.value = 0; bgMat.uniforms.uGlow.value = 1;
  pMat.uniforms.uTime.value = t; pMat.uniforms.uPush.value = 0; pMat.uniforms.uAlpha.value = 1; pMat.uniforms.uSize.value = 1;
  ringGroup.position.set(0, 0, 0); ringGroup.scale.setScalar(1); ringGroup.rotation.set(0, t * .35, 0);
  flare.scale.setScalar(1.6 + .2 * Math.sin(t * 5)); flare.material.opacity = 1;

  if (t < 4.9) { // shatter + warp into darkness
    const lt = t - 3.6, k = expo(seg(lt, .1, .9));
    placeCamera(v3(0, 0, lerp(6, 4.2, eio(seg(lt, .1, 1.3)))), v3(0, 0, -10));
    flyerGroup.visible = true; flyerGroup.position.set(0, -(FLY_Y - H / 2) * (.728 * 6 / H), 0); flyerGroup.scale.setScalar(1.03);
    tiles.forEach(m => {
      const { bx, by, i, d } = m.userData, e = eout(seg(lt, .12 + d * .35, 1.3 + d * .35));
      const dir = v3(bx, by, 0).normalize();
      m.position.set(bx + dir.x * e * 1.5 * (.4 + rnd(i)), by + dir.y * e * 1.9 * (.4 + rnd(i + 1)) - e * e * .5, e * (.8 + 2.4 * rnd(i + 2)));
      m.rotation.set(e * (rnd(i + 3) - .5) * 9, e * (rnd(i + 4) - .5) * 9, e * (rnd(i + 5) - .5) * 4);
      m.material.opacity = 1 - seg(lt, .75 + d * .3, 1.25 + d * .3);
    });
    stars.visible = true; sMat.uniforms.uAlpha.value = eout(seg(lt, .2, .6)); sMat.uniforms.uDist.value = 30 * eio(seg(lt, .1, 1.3)) * 1.3; sMat.uniforms.uStretch.value = 1;
    ringGroup.visible = true; particles.visible = true; ringGroup.position.set(0, 0, -6); pMat.uniforms.uMorph.value = 0; pMat.uniforms.uAlpha.value = eout(seg(lt, .4, 1.0)) * .7;
    rgb.uniforms.amount.value = .006 * Math.max(Math.exp(-Math.abs(lt - .12) * 14), Math.exp(-Math.abs(lt - .9) * 10));
    bloom.strength = .35 + .5 * seg(lt, .1, .5);
  } else if (t < 8.0) { // particles converge into the neon rings
    const lt = t - 4.9, a = -.3 + lt * .14;
    placeCamera(v3(Math.sin(a) * 8.6, .5 + .3 * Math.sin(lt * .6), Math.cos(a) * 8.6), v3(0, .8 - .5 * eio(seg(lt, 2.3, 3.1)), 0));
    ringGroup.position.set(0, 1.0, 0); ringGroup.rotation.set(.12 * Math.sin(lt * .7), t * .35, 0);
    particles.visible = true; pMat.uniforms.uMorph.value = eio(seg(lt, 0, 1.6)); pMat.uniforms.uSwirl.value = 3.5; pMat.uniforms.uAlpha.value = 1 - .45 * seg(lt, 1.6, 2.6);
    setRings(eout(seg(lt, 1.0, 1.7)) * (1 + .6 * Math.exp(-(lt - 1.7) * 3) * (lt > 1.7)), t);
    flare.visible = lt > 1.3; flare.material.opacity = eout(seg(lt, 1.3, 1.8));
    stars.visible = true; sMat.uniforms.uAlpha.value = .5; sMat.uniforms.uDist.value = 30 * 1.3 + lt * 1.5; sMat.uniforms.uStretch.value = 0;
    bloom.strength = .8 + .8 * Math.exp(-lt * 3);
  } else if (t < 11.0) { // warp tunnel of posts, then a hard stop
    const lt = t - 8, dist = warpDist(lt), moving = lt < 1.6;
    placeCamera(v3(0, 0, 0), v3(0, 0, -1), Math.sin(lt * 1.3) * .06 * (moving ? 1 : Math.exp(-(lt - 1.6) * 4)));
    tunnel.visible = true;
    cards.forEach(m => {
      const { ang, z0, rad } = m.userData, z = -(((z0 - dist) % TLEN) + TLEN) % TLEN - .6;
      m.position.set(Math.cos(ang) * rad, Math.sin(ang) * rad * 1.35, z); m.rotation.set(0, -Math.cos(ang) * .5, 0);
      m.material.opacity = smoothFar(z) * eout(seg(lt, 0, .25));
    });
    stars.visible = true; sMat.uniforms.uAlpha.value = .9; sMat.uniforms.uDist.value = 40 + dist * 1.2; sMat.uniforms.uStretch.value = moving ? 1.5 : 0;
    setRings(1.4, t); ringGroup.position.set(0, 0, -60); ringGroup.scale.setScalar(4);
    rgb.uniforms.amount.value = moving ? .0035 * seg(lt, .2, .6) : .006 * Math.exp(-(lt - 1.6) * 9);
    bloom.strength = moving ? .9 : .7 + .6 * Math.exp(-(lt - 1.6) * 5);
  } else if (t < 20.0) { // services on a carousel around the rings
    const lt = t - S0, k = clamp(Math.floor(lt / SD), 0, 5), l = lt - k * SD;
    const ang = k > 0 ? -(k - 1 + eio(seg(l, 0, .55))) * 60 * DEG : (1 - expo(seg(l, 0, .7))) * 40 * DEG;
    placeCamera(v3(Math.sin(lt * .25) * .4, .45, 11.2), v3(0, -.15, 0));
    setRings(.9, t); ringGroup.position.set(0, -.2, 0); ringGroup.scale.setScalar(.85); flare.visible = true; particles.visible = true;
    pMat.uniforms.uMorph.value = 1; pMat.uniforms.uAlpha.value = .45;
    layoutPanels(ang, -.35, 1, t);
    stars.visible = true; sMat.uniforms.uAlpha.value = .45; sMat.uniforms.uDist.value = 60 + lt * .8; sMat.uniforms.uStretch.value = 0;
  } else if (t < 23.0) { // pull back: the whole orbit
    const lt = t - 20, e = eio(seg(lt, 0, 1.6));
    placeCamera(v3(0, lerp(.45, 6.2, e), lerp(11.2, 13.8, e)), v3(0, lerp(-.15, -.9, e), 0));
    setRings(lerp(.9, 1.25, e), t); ringGroup.position.set(0, -.2, 0); ringGroup.scale.setScalar(lerp(.85, 1.15, e)); flare.visible = true; particles.visible = true;
    pMat.uniforms.uMorph.value = 1; pMat.uniforms.uAlpha.value = .6;
    layoutPanels(-300 * DEG - lt * 28 * DEG, -.35, 1, t);
    stars.visible = true; sMat.uniforms.uAlpha.value = .5; sMat.uniforms.uDist.value = 67 + lt; sMat.uniforms.uStretch.value = 0;
  } else if (t < 26.5) { // same business vs different league
    const lt = t - 23, e = eio(seg(lt, 0, .8));
    placeCamera(v3(0, lerp(6.2, .4, e), lerp(13.8, 10.5, e)), v3(0, lerp(-.9, 0, e), 0));
    layoutPanels(-384 * DEG - lt * 28 * DEG, -.35, 1 - seg(lt, 0, .5), t);
    const pulse = Math.exp(-Math.max(0, lt - 2.7) * 3) * (lt > 2.7);
    setRings(.7 + .9 * pulse + .3 * seg(lt, 2.7, 2.95), t); ringGroup.position.set(0, -1.2, 0); ringGroup.scale.setScalar(.82); flare.visible = true; particles.visible = true;
    pMat.uniforms.uMorph.value = 1; pMat.uniforms.uAlpha.value = .45;
    flyerFlat.visible = lt < 1.95; flyerFlat.position.set(0, 1.35, 0); flyerFlat.scale.setScalar(.8 * eback(seg(lt, .25, .7)));
    flyerFlat.material.opacity = 1 - seg(lt, 1.6, 1.9); flyerFlat.lookAt(camera.position);
    dissolve.visible = lt > 1.55; flyerFlat.updateMatrixWorld(); ringGroup.updateMatrixWorld();
    dMat.uniforms.uFlyer.value.copy(flyerFlat.matrixWorld); dMat.uniforms.uRing.value.copy(ringGroup.matrixWorld);
    dMat.uniforms.uK.value = seg(lt, 1.6, 2.75); dMat.uniforms.uAlpha.value = 1 - .85 * seg(lt, 2.6, 2.95);
    stars.visible = true; sMat.uniforms.uAlpha.value = .45; sMat.uniforms.uDist.value = 70 + lt; sMat.uniforms.uStretch.value = 0;
    bloom.strength = .8 + .7 * pulse;
    const pc = flyerFlat.position.clone().project(camera); FLY_SCREEN.x = (pc.x + 1) / 2 * W; FLY_SCREEN.y = (1 - pc.y) / 2 * H;
    const pe = flyerFlat.position.clone().add(v3(0, -1.15 * flyerFlat.scale.x, 0)).project(camera); FLY_SCREEN.bottom = (1 - pe.y) / 2 * H;
  } else { // end card backdrop
    const lt = t - 26.5;
    placeCamera(v3(Math.sin(lt * .3) * .6, .4, lerp(10.5, 9.4, eio(seg(lt, 0, 3.5)))), v3(0, .3, 0));
    setRings(lerp(1.1, 0, eout(seg(lt, 0, .7))), t); ringGroup.position.set(0, lerp(-1.2, .6, eio(seg(lt, 0, .9))), -2); ringGroup.scale.setScalar(1.2);
    flare.visible = true; flare.material.opacity = 1 - seg(lt, 0, .6); particles.visible = true; pMat.uniforms.uMorph.value = 1; pMat.uniforms.uAlpha.value = .35;
    stars.visible = true; sMat.uniforms.uAlpha.value = .4; sMat.uniforms.uDist.value = 74 + lt; sMat.uniforms.uStretch.value = 0;
    bloom.strength = .8 + .6 * Math.exp(-lt * 4);
  }
  composer.render();
}
function smoothFar(z) { return clamp((z + 46) / 10) * clamp((-z - .2) / 1.2); }
function layoutPanels(base, y, alpha, t) {
  for (let i = 0; i < 6; i++) {
    const a = base + i * 60 * DEG, p = panels[i];
    p.visible = alpha > .01; p.position.set(Math.sin(a) * 4.6, y + Math.sin(t * 1.1 + i) * .05, Math.cos(a) * 4.6); p.rotation.set(0, a, 0);
    const facing = Math.cos(a);
    p.material.opacity = alpha * clamp(.35 + .65 * facing);
    const lt = clamp(t - (S0 + i * SD), 0, SD);
    if (p.visible && facing > -.3) drawPanel(i, lt, Math.abs(Math.sin(a)) < .2 && facing > 0);
  }
}

// ---------- 2D typography per section
function overlay(t) {
  if (t >= 3.6 && t < 4.9) {
    const lt = t - 3.6;
    maskText('...you presented it like', W / 2, 860, seg(lt, .45, .75), { size: 74, w: 300 });
    if (lt > .9) { const k = seg(lt, .9, 1.02), sc = 1.9 - .9 * eout(k);
      o.save(); o.translate(W / 2 + (lt < 1.15 ? (rnd(Math.floor(t * 60)) - .5) * 16 : 0), 1070); o.scale(sc, sc); chroma('THIS?', 0, 0, 240, 700, 1 - seg(lt, .95, 1.25)); o.restore(); }
    flash(.6 * Math.exp(-Math.abs(lt - .12) * 20));
  } else if (t < 8.0 && t >= 4.9) {
    const lt = t - 4.9, rise = 70 * eio(seg(lt, 2.3, 3.1));
    const word = 'lumarc'; o.font = font(168, 300); const tw = o.measureText(word).width; let x = W / 2 - tw / 2;
    for (let i = 0; i < word.length; i++) {
      const k = seg(lt, 1.55 + i * .07, 2.0 + i * .07), cw = o.measureText(word[i]).width;
      text(word[i], x + cw / 2, 1390 + (1 - expo(k)) * 60 - rise, { size: 168, w: 300, alpha: k, blur: (1 - k) * 14, shadow: 30 }); x += cw;
    }
    text('Be seen. Be remembered.', W / 2, 1495 - rise, { size: 52, w: 300, color: C.muted, alpha: eout(seg(lt, 2.15, 2.5)), spacing: 3 });
    flash(.9 * (1 - seg(lt, 0, .3)), '200,190,255');
  } else if (t < 11.0 && t >= 8.0) {
    const lt = t - 8; speedLines(lt < 1.6 ? seg(lt, .1, .5) : 0);
    const st = 1.6, k = eout(seg(lt, st, st + .3)), outK = eio(seg(lt, 2.75, 3));
    o.save(); o.globalAlpha = k * (1 - outK); const g = o.createRadialGradient(W / 2, 960, 50, W / 2, 960, 760); g.addColorStop(0, 'rgba(8,8,14,.9)'); g.addColorStop(1, 'rgba(8,8,14,0)'); o.fillStyle = g; o.fillRect(0, 0, W, H); o.restore();
    o.save(); o.globalAlpha = 1 - outK;
    maskText('Content that makes', W / 2, 780, seg(lt, st + .05, st + .4), { size: 92, w: 400 });
    maskText('your business', W / 2, 890, seg(lt, st + .15, st + .5), { size: 92, w: 400 });
    o.save(); const s = 1 + .22 * (1 - eback(seg(lt, st + .3, st + .75))); o.translate(W / 2, 1040); o.scale(s, s);
    text('impossible', 0, 0, { size: 132, w: 700, gradient: true, shadow: 40, alpha: eout(seg(lt, st + .3, st + .42)) }); o.restore();
    maskText('to scroll past.', W / 2, 1160, seg(lt, st + .45, st + .8), { size: 92, w: 400 });
    o.restore();
    flash(.45 * Math.exp(-Math.max(0, lt - st) * 9) * (lt > st), '170,160,255');
  } else if (t < 20.0 && t >= 11.0) {
    const lt = t - S0, i = clamp(Math.floor(lt / SD), 0, 5), l = lt - i * SD;
    const inK = expo(seg(l, 0, .4)), outK = eio(seg(l, SD - .2, SD)) * (i < 5 ? 1 : 0), al = inK * (1 - outK);
    scrim(0, 760, .55);
    o.save(); o.globalAlpha = al; o.translate((1 - inK) * 120 - outK * 120, 0);
    text(String(i + 1).padStart(2, '0'), W / 2, 330, { size: 150, w: 200, gradient: true, shadow: 30 });
    const sz = fitSize(SERV[i][0], 500, 86, 960); maskText(SERV[i][0], W / 2, 460, seg(l, .05, .4), { size: sz, w: 500 });
    text(SERV[i][1], W / 2, 535, { size: 42, w: 300, color: C.muted, alpha: eout(seg(l, .2, .5)) });
    o.restore();
    for (let j = 0; j < 6; j++) { const x = W / 2 - 210 + j * 70; rr(x, 1760, 56, 6, 3); o.fillStyle = 'rgba(255,255,255,.15)'; o.fill();
      const f = j < i ? 1 : j === i ? clamp(l / SD) : 0; if (f > 0) { rr(x, 1760, 56 * f, 6, 3); o.fillStyle = grad(x, 0, x + 56, 0); o.fill(); } }
  } else if (t < 23.0 && t >= 20.0) {
    const lt = t - 20; scrim(0, 620, .5); scrim(H, H - 520, .5);
    maskText('Everything your brand', W / 2, 300, seg(lt, .3, .7), { size: 82, w: 400 });
    maskText('needs to stand out.', W / 2, 400, seg(lt, .42, .82), { size: 82, w: 400 });
    o.save(); const s = 1 + .2 * (1 - eback(seg(lt, 1.2, 1.6))); o.translate(W / 2, 1700); o.scale(s, s);
    text('One studio.', 0, 0, { size: 120, w: 700, gradient: true, shadow: 40, alpha: eout(seg(lt, 1.2, 1.4)) }); o.restore();
  } else if (t < 26.5 && t >= 23.0) {
    const lt = t - 23;
    const la = eout(seg(lt, .7, 1.0)) * (1 - seg(lt, 1.5, 1.75));
    o.save(); o.globalAlpha = la; rr(FLY_SCREEN.x - 105, FLY_SCREEN.bottom + 22, 210, 60, 30); o.fillStyle = '#3a3a44'; o.fill(); o.restore();
    text('BEFORE', FLY_SCREEN.x, FLY_SCREEN.bottom + 63, { size: 30, w: 600, color: '#d0d0d8', alpha: la, spacing: 4 });
    text('Same business.', W / 2, 250, { size: 84, w: 400, alpha: eout(seg(lt, .4, .8)) * (1 - .4 * seg(lt, 2.7, 3)), blur: (1 - eout(seg(lt, .4, .8))) * 10 });
    o.save(); const s = 1 + .2 * (1 - eback(seg(lt, 2.7, 3.1))); o.translate(W / 2, 1720); o.scale(s, s);
    text('Different league.', 0, 0, { size: 104, w: 700, gradient: true, shadow: 40, alpha: eout(seg(lt, 2.7, 2.9)) }); o.restore();
    const lb = eout(seg(lt, 2.85, 3.1)); o.save(); o.globalAlpha = lb; rr(W / 2 - 100, 1770, 200, 60, 30); o.fillStyle = grad(W / 2 - 100, 0, W / 2 + 100, 0); o.fill(); o.restore();
    text('AFTER', W / 2, 1811, { size: 30, w: 600, alpha: lb, spacing: 4 });
    flash(.35 * Math.exp(-Math.max(0, lt - 2.7) * 8) * (lt > 2.7), '170,160,255');
  } else if (t >= 26.5) {
    const lt = t - 26.5;
    o.fillStyle = `rgba(8,8,14,${.45 * eout(seg(lt, 0, .6))})`; o.fillRect(0, 0, W, H);
    const k = eout(seg(lt, .2, .8));
    if (IMG.logo.naturalWidth) { const lw = 720 * (.9 + .1 * k), lh = lw * IMG.logo.naturalHeight / IMG.logo.naturalWidth; o.save(); o.globalAlpha = k; o.drawImage(IMG.logo, W / 2 - lw / 2, 700 - lh / 2, lw, lh); o.restore(); }
    maskText('Ready to be impossible', W / 2, 980, seg(lt, .55, .9), { size: 70, w: 400 });
    maskText('to scroll past?', W / 2, 1070, seg(lt, .65, 1.0), { size: 70, w: 400 });
    const b = eback(seg(lt, .95, 1.35)), pl = 1 + .03 * Math.max(0, Math.sin(lt * 5));
    o.save(); o.translate(W / 2, 1250); o.scale(b * pl, b * pl); o.shadowColor = 'rgba(122,85,255,.85)'; o.shadowBlur = 50;
    rr(-280, -62, 560, 124, 62); o.fillStyle = grad(-280, 0, 280, 0); o.fill(); o.shadowBlur = 0; text('Get a Free Quote', 0, 16, { size: 48, w: 500 }); o.restore();
    text('@lumarc_studio  ·  slumarc.com', W / 2, 1440, { size: 44, color: C.muted, alpha: eout(seg(lt, 1.25, 1.6)) });
    flash(.7 * Math.exp(-lt * 6), '180,170,255');
  }
}

// =====================================================================
function renderAt(t) {
  T = t; ctx = o;
  o.setTransform(1, 0, 0, 1, 0, 0);
  if (t < 3.6) { drawBefore(t, 1); beforeText(t); return; }
  render3D(t);
  o.drawImage(renderer.domElement, 0, 0, W, H);
  if (t < 3.8) { drawBefore(3.6, 1 - seg(t, 3.6, 3.8)); }
  beforeText(t);
  overlay(t);
  [8.0, 11.0, 20.0, 23.0].forEach(c => { const d = 1 - Math.abs(t - c) / .1; if (d > 0) flash(.55 * d, '8,8,14'); });
  vignette(.42); grain(.055);
}

window.ready = (async () => {
  makeNoise();
  await Promise.all(['300', '400', '500', '700', '200'].map(w => document.fonts.load(`${w} 40px Outfit`)));
  await Promise.all(Object.values(IMG).map(im => im.complete && im.naturalWidth ? 1 : new Promise(r => { im.onload = im.onerror = r; })));
  flyerTex.needsUpdate = true; buildDissolve();
  window.renderAt = renderAt; renderAt(5.0); return true;
})();
