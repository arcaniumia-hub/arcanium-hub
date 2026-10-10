// Deterministic frame engine: bg 2D canvas -> 3D (three.js, HDR, ACES only on the 3D layer) -> fg 2D canvas
// -> bloom (2 levels) -> final FX shader (aberration, zoom blur, punch zoom, shake, glitch, liquid warp, pixelate,
// scanlines, grade, invert, flash, vignette, grain, letterbox) -> canvas.  Optional sub-frame motion blur.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { W, H, FPS, clamp } from './lib.js';

// every FX knob a scene (or the edit layer) may set on E.fx during draw(); reset to these defaults each frame
export const FX_DEFAULTS = {
  exposure: .85,          // 3D exposure before ACES (materials were tuned for .82-.9)
  bloom: .55, bloomThreshold: .72, bloomKnee: .25,
  rgb: .0015,             // radial chromatic aberration (uv units at the frame edge), .004 subtle .02 heavy
  zoomBlur: 0, zoomCenter: [.5, .5],   // radial blur amount 0..1
  zoom: 1, rot: 0, shake: [0, 0],      // punch-in scale, roll (rad), offset (uv)
  glitch: 0, glitchSeed: 0,            // 0..1 slice + block displacement
  displace: 0, displaceScale: 3,       // liquid noise warp amount (uv) and frequency
  pixelate: 0,                         // block size in px (0/1 = off)
  scanlines: 0, invert: 0,
  flash: 0, flashColor: [1, 1, 1],     // full-frame mix to colour (linear-ish 0..1)
  sat: 1, contrast: 1, brightness: 0, tint: [1, 1, 1],
  vignette: .35, grain: .045, letterbox: 0,   // letterbox: fraction of height covered at top AND bottom
  mirror: 0,                           // 0 off, 1 mirror left->right, 2 mirror top->bottom, 3 both
};

const VERT = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`;
const GLSL_COMMON = `
float hash(vec2 p){ p = fract(p*vec2(123.34, 456.21)); p += dot(p, p+45.32); return fract(p.x*p.y); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); vec2 u=f*f*(3.-2.*f);
  return mix(mix(hash(i),hash(i+vec2(1,0)),u.x), mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),u.x), u.y); }
vec3 s2l(vec3 c){ return mix(c/12.92, pow((c+.055)/1.055, vec3(2.4)), step(.04045, c)); }
vec3 l2s(vec3 c){ c = max(c, 0.); return mix(c*12.92, 1.055*pow(c, vec3(1./2.4))-.055, step(.0031308, c)); }
vec3 aces(vec3 x){ return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14), 0., 1.); }
`;
const COMPOSE = `${GLSL_COMMON}
uniform sampler2D tBg, tFg, t3d; uniform float has3d, exposure, weight; varying vec2 vUv;
void main(){
  vec3 c = s2l(texture2D(tBg, vUv).rgb);
  if (has3d > .5) { vec4 d = texture2D(t3d, vUv); c = c*(1.-clamp(d.a,0.,1.)) + aces(max(d.rgb,0.)*exposure); }
  vec4 f = texture2D(tFg, vUv); c = mix(c, s2l(f.rgb), f.a);
  gl_FragColor = vec4(c*weight, weight);
}`;
const BRIGHT = `uniform sampler2D tSrc; uniform vec2 texel; uniform float threshold, knee; varying vec2 vUv;
void main(){
  vec3 c = .25*(texture2D(tSrc, vUv+texel*vec2(-1.,-1.)).rgb + texture2D(tSrc, vUv+texel*vec2(1.,-1.)).rgb
              + texture2D(tSrc, vUv+texel*vec2(-1.,1.)).rgb + texture2D(tSrc, vUv+texel*vec2(1.,1.)).rgb);
  float l = max(c.r, max(c.g, c.b)); float s = clamp((l - threshold + knee)/(2.*knee), 0., 1.); s = s*s*knee*2.;
  float w = max(s, l - threshold)/max(l, 1e-4); gl_FragColor = vec4(c*w, 1.);
}`;
const BLUR = `uniform sampler2D tSrc; uniform vec2 dir; varying vec2 vUv;
void main(){ vec3 c = texture2D(tSrc, vUv).rgb*.2270270;
  c += (texture2D(tSrc, vUv+dir*1.3846).rgb + texture2D(tSrc, vUv-dir*1.3846).rgb)*.3162162;
  c += (texture2D(tSrc, vUv+dir*3.2308).rgb + texture2D(tSrc, vUv-dir*3.2308).rgb)*.0702703;
  gl_FragColor = vec4(c, 1.); }`;
const FINAL = `${GLSL_COMMON}
uniform sampler2D tComp, tB1, tB2; uniform vec2 res; uniform float seed;
uniform float bloom, rgb, zoomBlur, zoom, rot, glitch, glitchSeed, displace, displaceScale, pixelate, scanlines, invert, flash,
  sat, contrast, brightness, vignette, grain, letterbox, mirror;
uniform vec2 zoomCenter, shake; uniform vec3 flashColor, tint; varying vec2 vUv;
vec2 warp(vec2 uv){
  if (mirror > .5) { if (mod(mirror, 2.) > .5 && uv.x > .5) uv.x = 1.-uv.x; if (mirror > 1.5 && uv.y < .5) uv.y = 1.-uv.y; }
  vec2 p = uv - .5; float asp = res.x/res.y; p.x *= asp;
  float cr = cos(rot), sr = sin(rot); p = mat2(cr, -sr, sr, cr)*p / zoom; p.x /= asp; uv = p + .5 + shake;
  if (displace > 0.) { vec2 q = uv*displaceScale; uv += displace*vec2(vnoise(q+seed*.01)-.5, vnoise(q+vec2(7.3, 2.1)-seed*.01)-.5); }
  if (glitch > 0.) {
    float row = floor(uv.y*48.); float h = hash(vec2(row, glitchSeed));
    if (h < glitch*.55) uv.x += (hash(vec2(row*3.1, glitchSeed+1.))-.5)*.3*glitch;
    vec2 blk = floor(uv*vec2(10., 22.)); float hb = hash(blk + glitchSeed*1.7);
    if (hb < glitch*.22) uv += (vec2(hash(blk+3.3), hash(blk+5.1))-.5)*.12*glitch;
  }
  if (pixelate > 1.) uv = (floor(uv*res/pixelate)+.5)*pixelate/res;
  return clamp(uv, vec2(.0005), vec2(.9995));
}
vec3 scene(vec2 uv){
  vec2 c = uv - .5; float k = rgb + glitch*.012;
  vec3 col = vec3(texture2D(tComp, clamp(uv + c*k, 0., 1.)).r, texture2D(tComp, uv).g, texture2D(tComp, clamp(uv - c*k, 0., 1.)).b);
  col += bloom*(texture2D(tB1, uv).rgb*1.0 + texture2D(tB2, uv).rgb*1.2);
  return col;
}
void main(){
  vec2 uv = warp(vUv); vec3 col;
  if (zoomBlur > .001) { vec2 d = zoomCenter - uv; col = vec3(0.);
    for (int i = 0; i < 14; i++) { float f = float(i)/13.; col += scene(uv + d*zoomBlur*.22*f); } col /= 14.; }
  else col = scene(uv);
  col *= tint;
  col = (col - .18)*contrast + .18 + brightness;
  float l = dot(col, vec3(.2126, .7152, .0722)); col = mix(vec3(l), col, sat);
  col = mix(col, 1. - clamp(col, 0., 1.), invert);
  col = mix(col, flashColor, clamp(flash, 0., 1.));
  if (scanlines > 0.) col *= 1. - scanlines*.4*step(.5, fract(vUv.y*res.y/4.));
  vec2 vq = (vUv - .5)*vec2(1., 1.25); col *= 1. - vignette*smoothstep(.25, .85, length(vq)*1.25);
  vec3 s = l2s(col);
  s += (hash(vUv*res + seed) - .5)*grain;
  if (abs(vUv.y - .5) > .5 - letterbox) s = vec3(0.);
  gl_FragColor = vec4(clamp(s, 0., 1.), 1.);
}`;

export function createEngine() {
  const canvas = document.createElement('canvas'); canvas.width = W; canvas.height = H; canvas.id = 'out';
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, alpha: false });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.autoClear = false;
  const env = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), .04).texture;

  const mk2d = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.NoColorSpace; t.minFilter = t.magFilter = THREE.LinearFilter; t.generateMipmaps = false; return { c, x: c.getContext('2d'), t }; };
  const BG = mk2d(), FG = mk2d();
  const rtOpt = { type: THREE.HalfFloatType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: false };
  const rt3d = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
  const rtComp = new THREE.WebGLRenderTarget(W, H, rtOpt);
  const q = [W / 4, H / 4], e = [W / 8, H / 8];
  const rtQa = new THREE.WebGLRenderTarget(q[0], q[1], rtOpt), rtQb = new THREE.WebGLRenderTarget(q[0], q[1], rtOpt);
  const rtEa = new THREE.WebGLRenderTarget(e[0], e[1], rtOpt), rtEb = new THREE.WebGLRenderTarget(e[0], e[1], rtOpt);

  const quadScene = new THREE.Scene(), quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2)); quad.frustumCulled = false; quadScene.add(quad);
  const sm = (frag, uniforms, extra = {}) => new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: frag, uniforms, depthTest: false, depthWrite: false, ...extra });
  const mCompose = sm(COMPOSE, { tBg: { value: BG.t }, tFg: { value: FG.t }, t3d: { value: rt3d.texture }, has3d: { value: 0 }, exposure: { value: 1 }, weight: { value: 1 } });
  // sub-frame accumulation: plain ONE/ONE add of (c*w) so the weights sum to exactly 1 (AdditiveBlending would square them)
  const mComposeAcc = sm(COMPOSE, mCompose.uniforms, { transparent: true, blending: THREE.CustomBlending, blendEquation: THREE.AddEquation,
    blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor });
  const mBright = sm(BRIGHT, { tSrc: { value: rtComp.texture }, texel: { value: new THREE.Vector2(1 / W, 1 / H) }, threshold: { value: .7 }, knee: { value: .25 } });
  const mBlur = sm(BLUR, { tSrc: { value: null }, dir: { value: new THREE.Vector2() } });
  const U = { tComp: { value: rtComp.texture }, tB1: { value: rtQa.texture }, tB2: { value: rtEa.texture }, res: { value: new THREE.Vector2(W, H) }, seed: { value: 0 } };
  for (const [k, v] of Object.entries(FX_DEFAULTS)) U[k] = { value: Array.isArray(v) ? (v.length === 3 ? new THREE.Vector3(...v) : new THREE.Vector2(...v)) : v };
  const mFinal = sm(FINAL, U);
  const pass = (mat, target) => { quad.material = mat; renderer.setRenderTarget(target); renderer.render(quadScene, quadCam); };

  const E = {
    W, H, FPS, canvas, renderer, env, THREE,
    bg: BG.x, fg: FG.x, fx: { ...FX_DEFAULTS }, img: {}, clearColor: '#050506',
    _used3d: false,
    // render a three.js scene into the 3D layer (call any number of times per frame; the first call clears it)
    render3D(scene, camera) {
      renderer.setRenderTarget(rt3d);
      if (!E._used3d) { renderer.setClearColor(0x000000, 0); renderer.clear(true, true, true); E._used3d = true; }
      else renderer.clearDepth();
      if (scene.environment === null && scene.userData.autoEnv !== false) scene.environment = env;
      if (!scene.userData._envSet) { scene.environmentIntensity = scene.userData.envIntensity ?? .5; scene.userData._envSet = true; }
      renderer.render(scene, camera);
    },
  };

  async function loadImages(map) { await Promise.all(Object.entries(map).map(([k, src]) => new Promise(r => { const im = new Image(); im.onload = () => { E.img[k] = im; r(); }; im.onerror = () => { console.error('img fail', k); r(); }; im.src = src; }))); }
  async function loadFonts(list) {
    for (const [family, src, weight, style] of list) { const f = new FontFace(family, `url(${src})`, { weight: String(weight), style: style || 'normal' }); await f.load(); document.fonts.add(f); }
  }
  E.loadImages = loadImages; E.loadFonts = loadFonts;

  // drawFrame(t) is provided by main.js (timeline): draws bg/fg canvases, calls render3D, mutates E.fx
  function layers(t, drawFrame, weight, accumulate) {
    E.fx = { ...FX_DEFAULTS, zoomCenter: [.5, .5], shake: [0, 0], flashColor: [1, 1, 1], tint: [1, 1, 1] };
    E._used3d = false;
    const b = E.bg, f = E.fg;
    // full context reset every frame: clears pixels AND any state a scene leaked (unbalanced save(), clip, transform, filter...)
    for (const c of [b, f]) {
      if (c.reset) c.reset();
      else { c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; c.filter = 'none'; c.clearRect(0, 0, W, H); }
    }
    b.fillStyle = E.clearColor; b.fillRect(0, 0, W, H);
    drawFrame(t);
    BG.t.needsUpdate = true; FG.t.needsUpdate = true;
    mCompose.uniforms.has3d.value = E._used3d ? 1 : 0; mCompose.uniforms.exposure.value = E.fx.exposure; mCompose.uniforms.weight.value = weight;
    quad.material = accumulate ? mComposeAcc : mCompose; renderer.setRenderTarget(rtComp); renderer.render(quadScene, quadCam);
  }
  E.renderFrame = function (t, drawFrame, motionSamples = 1, shutter = .5) {
    const n = Math.max(1, Math.round(motionSamples));
    renderer.setRenderTarget(rtComp); renderer.setClearColor(0x000000, 1); renderer.clear(true, true, true);
    if (n === 1) layers(t, drawFrame, 1, false);
    else for (let i = 0; i < n; i++) layers(t + ((i + .5) / n - .5) * shutter / FPS, drawFrame, 1 / n, true);
    // NB: with motion blur the last sub-frame (t + shutter/2) set E.fx — scenes should keep FX smooth in time
    const fx = E.fx;
    mBright.uniforms.threshold.value = fx.bloomThreshold; mBright.uniforms.knee.value = fx.bloomKnee;
    mBright.uniforms.texel.value.set(1 / W, 1 / H); mBright.uniforms.tSrc.value = rtComp.texture; pass(mBright, rtQa);
    for (let i = 0; i < 2; i++) {
      mBlur.uniforms.tSrc.value = rtQa.texture; mBlur.uniforms.dir.value.set((1 + i) / q[0], 0); pass(mBlur, rtQb);
      mBlur.uniforms.tSrc.value = rtQb.texture; mBlur.uniforms.dir.value.set(0, (1 + i) / q[1]); pass(mBlur, rtQa);
    }
    mBright.uniforms.tSrc.value = rtQa.texture; mBright.uniforms.threshold.value = 0; mBright.uniforms.knee.value = .0001;
    mBright.uniforms.texel.value.set(1 / q[0], 1 / q[1]); pass(mBright, rtEa);
    for (let i = 0; i < 2; i++) {
      mBlur.uniforms.tSrc.value = rtEa.texture; mBlur.uniforms.dir.value.set((1 + i) / e[0], 0); pass(mBlur, rtEb);
      mBlur.uniforms.tSrc.value = rtEb.texture; mBlur.uniforms.dir.value.set(0, (1 + i) / e[1]); pass(mBlur, rtEa);
    }
    for (const k of Object.keys(FX_DEFAULTS)) {
      const v = fx[k]; if (v === undefined) continue;
      if (Array.isArray(v)) U[k].value.set(...v); else U[k].value = k === 'bloom' ? Math.max(0, v) : v;
    }
    U.seed.value = Math.floor(t * FPS + .5) % 997 + 1;
    renderer.setRenderTarget(null); quad.material = mFinal; renderer.render(quadScene, quadCam);
  };
  return E;
}
export { clamp };
