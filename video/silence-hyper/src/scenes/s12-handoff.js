// s12-handoff — HANDOFF: the ring becomes LUMARC (b70-76)
//
// b70.0-71.0 CONTRACT: the LUMARC gradient ring (conic #4f6bff -> #6a55ff -> #9a4dff, spinning) collapses from r 1500
//   (off-frame, where s11 left it) onto the logo's ring block, with a speed smear of ghost rings, and SHEDS 60k particles
//   along its circumference (hot gold sparks at birth, turning to the brand gradient by screen x over b70.5-71.5) that
//   swirl in a differential vortex around the logo. Brand flash .15 + liquid displace on the first frames.
// b70.7-71.0 the circle TILTS in 3D and splits into the two interlocked ellipses of the LUMARC mark (fitted to the PNG),
// b71.0 lands on the logo: chime -> shockwave rings, a star glint on the rings' crossing, bloom kick; the drawn ellipses
//   cross-fade (6 frames) into the PNG's rings.
// b71.5-73.0 WORDMARK BUILD: the particles converge (bent spiral paths, ease-in-out) onto the 'lumarc' letters sampled from
//   the PNG's alpha, one letter per 1/4 beat (l u m a r c), each landing with a white heat flash, a micro-burst and a bloom pulse.
// b73.0-73.5 the particle wordmark cross-fades into the crisp PNG; a white -> violet glint sweeps across the logo; the
//   leftover particles spiral outward and twinkle out by b74.
// b73.5-76 the logo floats (breathing 1 %/bar, glow + anamorphic flare on every beat), 24 bokeh discs start drifting up.
//   The post levels ease into the end card's, so s13 builds around it without a cut.
import * as THREE from 'three';
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, ein, eio, expoOut, rnd, COL, ADDITIVE } from '../lib.js';
import { LOGO, LOGO_SPLIT, lp, brandBackdrop, drawBokeh, drawLogo, logoBreath, beatGlow, logoFlare, STAR, END_FX, endZoom } from './s13-lumarc.js';

const B0 = 70;
const N_LET = 42000, N_FREE = 14000, N = N_LET + N_FREE;
// ring block of the logo: circle centre / radius the ring lands on, and the two ellipses of the mark (fitted to the PNG)
const CF = lp(113.5, 112), RL = 100 * LOGO.s;
const ELL = [
  { c: lp(121, 93), a: 96 * LOGO.s, b: 45 * LOGO.s, rot: 52 * Math.PI / 180 },
  { c: lp(115, 144), a: 104 * LOGO.s, b: 44 * LOGO.s, rot: -27 * Math.PI / 180 },
];
const C0 = [540, 930], R0 = 1500;
// letters of the wordmark (logo px x-ranges) and their landing beats (one per 1/4 beat)
const LET = [[246, 266], [272, 338], [342, 444], [446, 518], [524, 564], [564, 628]];
const LAND = [71.5, 71.75, 72.0, 72.25, 72.5, 72.75];

// ring contraction (closed form) and its inverse
const EXP = 6, EN = 1 - Math.pow(2, -EXP);
const ringE = b => (1 - Math.pow(2, -EXP * seg(b, 70, 71))) / EN;
const ringR = b => lerp(R0, RL, ringE(b));
const ringC = b => { const e = ringE(b); return [lerp(C0[0], CF[0], e), lerp(C0[1], CF[1], e)]; };
const beatOfR = r => 70 - Math.log2(1 - (R0 - r) / (R0 - RL) * EN) / EXP;

const lin = hex => new THREE.Color(hex).convertSRGBToLinear();
const V3 = c => new THREE.Vector3(c.r, c.g, c.b);

// ------------------------------------------------------------------ particles: one draw call, everything closed-form in the shader
const VS = `
attribute vec2 aP0; attribute vec2 aTgt; attribute vec4 aR; attribute vec2 aT;
uniform float uB; uniform vec2 uC; uniform vec3 uGold, uL1, uL2, uL3, uWhite;
varying vec3 vCol; varying float vA;
void main(){
  float te = aT.x, tl = aT.y;
  float tau = max(uB - te, 0.)*.4;                          // seconds since it peeled off the ring
  vec2 rel = aP0 - uC; float r = length(rel), ang = atan(rel.y, rel.x);
  float w = (1.25 + .3*aR.x)*240./(r + 120.);               // differential vortex (rad/s), clockwise on screen
  ang += w*(.8*(1. - exp(-tau/.8)) + .3*tau);
  r += (24. + 80.*aR.y)*(1. - exp(-tau/.45));                // peel outward
  if (tl < 1.) { float o = clamp((uB - 72.9 - .2*aR.x)/1.2, 0., 1.); r += 520.*o*o*(.4 + aR.z); ang += .5*o; }
  vec2 p = uC + r*vec2(cos(ang), sin(ang));
  float nA = (3. + 7.*aR.z)*min(tau, 1.2);                  // curl-ish wander
  p += nA*vec2(sin(tau*2.3 + aR.w*40. + p.y*.007), cos(tau*1.9 + aR.x*40. + p.x*.007));
  float alpha = step(te, uB);
  float sx = clamp(p.x/1080., 0., 1.);
  vec3 brand = sx < .5 ? mix(uL1, uL2, sx*2.) : mix(uL2, uL3, sx*2. - 1.);
  vec3 col = mix(uGold, brand, smoothstep(70.5 + .5*aR.y, 71.0 + .5*aR.y, uB));
  float bright = 1. + 3.*exp(-tau/.07);                      // sparks are hot when they are shed
  float size = 2. + 3.*aR.w;
  if (tl > 1.) {
    float fs = max(te + .25, tl - 1.15 - .35*aR.y);
    float k = clamp((uB - fs)/(tl - fs), 0., 1.);
    float e = k*k*(1.6 - .6*k);                               // leaves gently, arrives at speed (then the landing burst)
    // spiral in: polar interpolation around the target (radius -> 0 while the angle keeps winding) = whirlpool streams
    vec2 rl = p - aTgt; float rr = length(rl)*(1. - e), aa = atan(rl.y, rl.x) + (1.1 + .9*aR.z)*e;
    vec2 q = aTgt + rr*vec2(cos(aa), sin(aa));
    float since = uB - tl;
    if (since > 0.) { float s = since/.06; vec2 bd = normalize(vec2(aR.x - .5, aR.y - .5) + 1e-4); q += bd*(3. + 7.*aR.z)*s*exp(1. - s); }
    q += vec2(sin(uB*9. + aR.x*60.), cos(uB*8. + aR.y*60.))*.45*step(0., since);
    p = q;
    bright *= 1. + 1.2*e*e;                                    // streams heat up as they close in
    float heat = smoothstep(tl - .3, tl, uB);
    col = mix(col, uWhite, heat);
    bright *= 1. + 1.5*exp(-max(since, 0.)/.12)*step(0., since);
    bright *= mix(1., .55, heat);
    alpha *= 1. - smoothstep(73.0, 73.5, uB);
    size = mix(size, 1.4 + 1.1*aR.w, heat);
  } else {
    alpha *= 1. - smoothstep(73.1 + .4*aR.x, 74.0, uB);
    alpha *= (.5 + .5*sin(uB*7.3 + aR.y*50.))*mix(1., .3, smoothstep(70.9, 71.7, uB));   // twinkle, much dimmer once it is dust
  }
  // once the sparks have settled into a vortex, it glows around the logo and falls off toward the frame edges (depth)
  float fall = mix(.18, 1., exp(-length(p - uC)/420.));
  alpha *= mix(1., fall, smoothstep(70.85, 71.35, uB));
  vCol = col*bright; vA = alpha;
  gl_PointSize = size;
  gl_Position = vec4(p.x/540. - 1., 1. - p.y/960., 0., 1.);
}`;
const FS = `
uniform float uI; varying vec3 vCol; varying float vA;
void main(){ float d = length(gl_PointCoord - .5)*2.; float a = clamp(1. - d, 0., 1.); a *= a; if (a*vA < .003) discard;
  gl_FragColor = vec4(vCol*uI*a, vA); }`;

function buildParticles(img) {
  // wordmark samples from the PNG alpha (letter by x-range)
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const x = c.getContext('2d'); x.drawImage(img, 0, 0);
  const d = x.getImageData(0, 0, img.width, img.height).data;
  const cand = LET.map(() => []), tot = LET.map(() => 0);
  for (let py = 0; py < img.height; py++) for (let px = LOGO_SPLIT; px < img.width; px++) {
    const a = d[(py * img.width + px) * 4 + 3]; if (a < 40) continue;
    const li = LET.findIndex(([x0, x1]) => px >= x0 && px < x1); if (li < 0) continue;
    tot[li] += a / 255; cand[li].push([px, py, tot[li]]);
  }
  const all = tot.reduce((s, v) => s + v, 0);
  const P0 = new Float32Array(N * 2), TG = new Float32Array(N * 2), R = new Float32Array(N * 4), T = new Float32Array(N * 2);
  let i = 0;
  const emit = (j, tl, tgt) => {
    // emission radius log-distributed -> emission beat on the closed-form ring. Letter particles peel off the outer
    // part (they stream in from afar on long arcs), the dust from everywhere (dense near the logo, sparse far out)
    const u = rnd(j * 1.71 + .3);
    const r0 = tl > 0 ? 240 * Math.pow(4.2, u) : RL * 1.03 * Math.pow(10, Math.pow(u, 1.25));
    const te = beatOfR(Math.min(r0, R0 - 1)), [cx, cy] = ringC(te);
    // particles peel off in 40 strands: after the differential swirl each strand becomes a spiral arm
    const th = (Math.floor(rnd(j * 2.93 + .7) * 40) + (rnd(j * 4.41 + .2) - .5) * .22) / 40 * TAU;
    P0.set([cx + r0 * Math.cos(th), cy + r0 * Math.sin(th)], j * 2);
    TG.set(tgt, j * 2); T.set([te, tl], j * 2);
    R.set([rnd(j * 3.1 + .1), rnd(j * 5.7 + .2), rnd(j * 7.3 + .4), rnd(j * 9.9 + .6)], j * 4);
  };
  LET.forEach((_, li) => {
    const n = li === LET.length - 1 ? N_LET - i : Math.round(N_LET * tot[li] / all), cs = cand[li], T1 = tot[li];
    for (let k = 0; k < n; k++, i++) {
      const rr = rnd(i * 4.37 + .9) * T1; let lo = 0, hi = cs.length - 1; while (lo < hi) { const m = (lo + hi) >> 1; if (cs[m][2] < rr) lo = m + 1; else hi = m; }
      const [px, py] = cs[lo];
      const tl = LAND[li] + .06 * rnd(i * 6.1 + .5);                    // tiny stagger inside the landing
      emit(i, tl, lp(px + rnd(i * 8.3) - .5, py + rnd(i * 9.7) - .5));
    }
  });
  for (; i < N; i++) emit(i, 0, [0, 0]);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
  g.setAttribute('aP0', new THREE.BufferAttribute(P0, 2)); g.setAttribute('aTgt', new THREE.BufferAttribute(TG, 2));
  g.setAttribute('aR', new THREE.BufferAttribute(R, 4)); g.setAttribute('aT', new THREE.BufferAttribute(T, 2));
  const mat = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, ...ADDITIVE, depthTest: false,
    uniforms: { uB: { value: 70 }, uC: { value: new THREE.Vector2(...CF) }, uI: { value: 1 },
      uGold: { value: V3(lin(COL.gold)) }, uL1: { value: V3(lin(COL.lm1)) }, uL2: { value: V3(lin(COL.lm2)) }, uL3: { value: V3(lin(COL.lm3)) },
      uWhite: { value: V3(lin('#e8e9f2')) } } });
  const pts = new THREE.Points(g, mat); pts.frustumCulled = false;
  return { pts, mat };
}

// ------------------------------------------------------------------ 2D helpers
let S = null;   // scene state
function conic(ctx, cx, cy, a0) {
  const g = ctx.createConicGradient(a0, cx, cy);
  g.addColorStop(0, COL.lm1); g.addColorStop(.25, COL.lm2); g.addColorStop(.5, COL.lm3); g.addColorStop(.75, COL.lm2); g.addColorStop(1, COL.lm1);
  return g;
}
function ellipsePath(ctx, e) { ctx.beginPath(); ctx.ellipse(e.c[0], e.c[1], Math.max(.1, e.a), Math.max(.1, e.b), e.rot, 0, TAU); }
// ring geometry at beat b: before b70.7 one circle; b70.7-71.0 it tilts and splits into the two ellipses of the mark
function ringShapes(b) {
  const R = ringR(b), C = ringC(b), m = eio(seg(b, 70.7, 71.0));
  if (m <= 0) return [{ c: C, a: R, b: R, rot: 0 }];
  return ELL.map(E => ({ c: [lerp(C[0], E.c[0], m), lerp(C[1], E.c[1], m)], a: lerp(R, E.a, m), b: lerp(R, E.b, m), rot: E.rot }));
}
function star(ctx, x, y, k, len) {
  if (k <= .003) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(x, y);
  for (const [ang, l] of [[0, len], [Math.PI / 2, len * .62], [Math.PI / 4, len * .22], [-Math.PI / 4, len * .22]]) {
    ctx.save(); ctx.rotate(ang);
    const g = ctx.createLinearGradient(-l, 0, l, 0);
    g.addColorStop(0, 'rgba(154,77,255,0)'); g.addColorStop(.5, `rgba(255,255,255,${.9 * k})`); g.addColorStop(1, 'rgba(154,77,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-l, 0); ctx.lineTo(0, -3.2); ctx.lineTo(l, 0); ctx.lineTo(0, 3.2); ctx.closePath(); ctx.fill();
    ctx.restore();
  }
  const r = len * .35, c = ctx.createRadialGradient(0, 0, 0, 0, 0, r);
  c.addColorStop(0, `rgba(255,255,255,${.8 * k})`); c.addColorStop(.25, `rgba(170,150,255,${.35 * k})`); c.addColorStop(1, 'rgba(106,85,255,0)');
  ctx.fillStyle = c; ctx.fillRect(-r, -r, 2 * r, 2 * r);
  ctx.restore();
}
// diagonal glint clipped to the logo's own pixels (white core -> violet edges), drawn additively
function logoGlint(ctx, img, k) {
  if (k <= 0 || k >= 1 || !img) return;
  const c = S.glintC, x = S.glintX;
  x.globalCompositeOperation = 'source-over'; x.clearRect(0, 0, c.width, c.height); x.drawImage(img, 0, 0);
  x.globalCompositeOperation = 'source-in';
  const cx = lerp(-120, c.width + 120, k);           // constant speed: it reads on every letter
  x.save(); x.translate(cx, c.height / 2); x.rotate(.38);
  const g = x.createLinearGradient(-70, 0, 70, 0);
  g.addColorStop(0, 'rgba(154,77,255,0)'); g.addColorStop(.3, 'rgba(154,77,255,.45)'); g.addColorStop(.5, 'rgba(255,255,255,.95)'); g.addColorStop(.7, 'rgba(154,77,255,.45)'); g.addColorStop(1, 'rgba(154,77,255,0)');
  x.fillStyle = g; x.fillRect(-70, -400, 140, 800); x.restore();
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = Math.sin(Math.PI * k);
  ctx.drawImage(c, LOGO.x, LOGO.y, LOGO.w, LOGO.h);
  // the white wordmark cannot get brighter: a blurred violet-white halo of the same glint makes the sweep read on it
  ctx.filter = 'blur(9px)'; ctx.globalAlpha = .9 * Math.sin(Math.PI * k);
  ctx.drawImage(c, LOGO.x, LOGO.y, LOGO.w, LOGO.h); ctx.drawImage(c, LOGO.x, LOGO.y, LOGO.w, LOGO.h);
  ctx.restore();
}

export default {
  id: 's12-handoff', start: 70, end: 76, cutIn: 'none',
  init(E) {
    const scene = new THREE.Scene(); scene.userData.autoEnv = false;
    const cam = new THREE.OrthographicCamera(-540, 540, 960, -960, -10, 10);
    const P = buildParticles(E.img.logo); scene.add(P.pts);
    const glintC = document.createElement('canvas'); glintC.width = E.img.logo.width; glintC.height = E.img.logo.height;
    S = { scene, cam, P, glintC, glintX: glintC.getContext('2d') };
  },
  draw(E, lt, t) {
    const b = t / BEAT, fg = E.fg, fx = E.fx, img = E.img.logo;
    // ---------------- background: #0e0e14 + radial brand glow growing in, bokeh from b73.5
    const bokehK = eout(seg(b, 73.5, 74.75));
    brandBackdrop(E, b, { glow: eio(seg(b, 70, 71.5)), bokehK });

    // ---------------- particles (3D layer, pixel-exact orthographic mapping)
    if (b < 74.05) {
      const u = S.P.mat.uniforms; u.uB.value = b;
      u.uI.value = .62;
      E.render3D(S.scene, S.cam);
    }

    // ---------------- the gradient ring: contract, smear, tilt/split into the mark's ellipses, land
    const ringA = 1 - eio(seg(b, 71.0, 71.5));
    if (ringA > 0) {
      const shapes = ringShapes(b), m = eio(seg(b, 70.7, 71.0));
      const spin = -Math.PI / 2 + 5.5 * eout(seg(b, 70, 71.2));
      fg.save(); fg.lineCap = 'round';
      // speed smear: ghost rings covering the last frame interval while the radius is collapsing fast
      const dR = ringR(b - 1 / 12) - ringR(b);
      if (dR > 6 && m === 0) {
        const C = ringC(b);
        for (let i = 1; i <= 10; i++) {
          const rb = b - i / 120, r = ringR(rb), cc = ringC(rb);
          fg.globalAlpha = .28 * (1 - i / 11) * ringA; fg.lineWidth = 3; fg.strokeStyle = conic(fg, cc[0], cc[1], spin - i * .05);
          fg.beginPath(); fg.arc(cc[0], cc[1], r, 0, TAU); fg.stroke();
        }
      }
      const lw = lerp(5, 8.5, m) * (1 + .4 * seg(b, 70.95, 71.0));
      shapes.forEach((sh, si) => {
        fg.globalAlpha = ringA;
        fg.shadowColor = 'rgba(106,85,255,.85)'; fg.shadowBlur = 24 + 16 * m;
        fg.lineWidth = lw;
        if (m < 1) { fg.strokeStyle = conic(fg, sh.c[0], sh.c[1], spin + si * 1.3); ellipsePath(fg, sh); fg.stroke(); }
        if (m > 0) {
          // the mark's rings are lit blue (left) -> violet (right): fade into that linear look as they tilt
          const g = fg.createLinearGradient(sh.c[0] - sh.a, 0, sh.c[0] + sh.a, 0);
          g.addColorStop(0, COL.lm1); g.addColorStop(.55, COL.lm2); g.addColorStop(1, COL.lm3);
          fg.globalAlpha = ringA * m; fg.strokeStyle = g; ellipsePath(fg, sh); fg.stroke();
        }
        // hot core line
        fg.shadowBlur = 0; fg.globalAlpha = ringA * .55; fg.lineWidth = Math.max(1, lw * .28); fg.strokeStyle = '#d9d4ff'; ellipsePath(fg, sh); fg.stroke();
      });
      fg.restore();
    }

    // ---------------- b71.0 landing: PNG rings cross-fade in (with a tiny settle), shockwaves, star glint
    const rk = eio(seg(b, 71.0, 71.5));
    const breath = logoBreath(b);
    const glowAmt = 18 * beatGlow(b) * seg(b, 71.5, 73.5);
    const wordA = eio(seg(b, 73.0, 73.5));
    if (rk > 0) drawLogo(fg, img, { rings: rk, word: wordA, scale: breath * (1 + .05 * (1 - eout(seg(b, 71.0, 71.75)))), glow: glowAmt });
    for (const [sb, amp, w0] of [[71.0, .5, 4], [71.125, .3, 2.5], [71.25, .18, 1.5]]) {
      const sk = seg(b, sb, sb + 1.4); if (sk <= 0 || sk >= 1) continue;
      const r = lerp(RL, 1250, eout(sk)), a = amp * Math.pow(1 - sk, 2.2);
      fg.save(); fg.globalAlpha = a; fg.lineWidth = w0 * (1 - sk) + .8; fg.strokeStyle = conic(fg, CF[0], CF[1], 1 + sb);
      fg.shadowColor = 'rgba(106,85,255,.7)'; fg.shadowBlur = 18; fg.beginPath(); fg.arc(CF[0], CF[1], r, 0, TAU); fg.stroke(); fg.restore();
    }
    const sp = b >= 71 ? Math.exp(-(b - 71) * BEAT / .16) : 0;
    star(fg, STAR[0], STAR[1], sp, 300);
    // per-letter landing flashes (small soft bursts on the letters)
    LAND.forEach((lb, li) => {
      const p = b >= lb ? Math.exp(-(b - lb) * BEAT / .08) : 0; if (p < .01) return;
      const [x0, x1] = LET[li], [cx, cy] = lp((x0 + x1) / 2, 150), r = 70 + (x1 - x0) * .6;
      const g = fg.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0, `rgba(255,255,255,${.22 * p})`); g.addColorStop(.35, `rgba(150,120,255,${.14 * p})`); g.addColorStop(1, 'rgba(106,85,255,0)');
      fg.save(); fg.globalCompositeOperation = 'lighter'; fg.fillStyle = g; fg.fillRect(cx - r, cy - r, 2 * r, 2 * r); fg.restore();
    });
    // b73.0 glint sweep across rings + wordmark; flare on beats once the logo is complete
    logoGlint(fg, img, seg(b, 73.0, 73.0 + 8 / 12 * 1.1));
    logoFlare(fg, Math.max(sp * 1.2, (.3 + .7 * beatGlow(b)) * seg(b, 73.25, 73.75)), { scale: breath });
    drawBokeh(fg, b, bokehK, true);

    // ---------------- post
    const fr = lt * 30;
    fx.exposure = .9;
    fx.flash = .035 * Math.max(0, 1 - fr / 5); fx.flashColor = [.42, .42, 1.0];
    fx.displace = .02 * Math.exp(-lt / .25); fx.displaceScale = 2;
    const late2 = eio(seg(b, 74, 76));
    fx.bloom = lerp(.9, lerp(.45, END_FX.bloom, late2), eio(seg(b, 73.25, 73.75)));
    fx.bloomThreshold = lerp(.6, END_FX.threshold, eio(seg(b, 73.25, 74.5)));
    fx.bloomKnee = lerp(.25, END_FX.knee, eio(seg(b, 73.25, 74.5)));
    for (const lb of LAND) { const f = (b - lb) * 12; if (f >= 0 && f < 3) fx.bloom += .4 * (1 - f / 3); }
    { const f = (b - 71) * 12; if (f >= 0 && f < 6) fx.bloom += .5 * (1 - f / 6); }
    fx.vignette = lerp(.42, END_FX.vignette, eio(seg(b, 70, 73.5)));
    fx.grain = lerp(.04, END_FX.grain, eio(seg(b, 70, 73.5)));
    fx.rgb = lerp(.004, END_FX.rgb, eio(seg(b, 70, 71.5)));
    fx.sat = 1;
    fx.zoom *= endZoom(b);
  },
};
