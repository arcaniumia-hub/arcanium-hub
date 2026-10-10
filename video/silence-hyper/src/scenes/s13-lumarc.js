// s13-lumarc — LUMARC END CARD (b76-86)
//
// No cut from s12: the LUMARC logo the particles assembled stays at (540,600) w600, breathing 1 % per bar with a glow
// pulsing on every beat, over the #0e0e14 field with a breathing violet radial glow and drifting brand bokeh (two depth
// planes: soft far discs behind everything, a few huge out-of-focus discs drifting in front at 3-4 %).
// b76.0-77.5 headline word by word on 1/4 beats (rise 24 px, blur 8 -> 0, 6 frames) · b78.0 CTA pill pops (.6 -> 1.06 -> 1,
// 8 frames) with a violet bloom kick + zoom 1.015 punch · b78.5 'Be seen.' · b79.0 'Be remembered.' · b79.25 handle ·
// sheens across the pill b80 / b82 / b84 · from b80 the pill breathes once per bar. Everything is legible from b79.75
// (31.9 s) to the last frame (34.4 s): a 2.5 s fully-composed hold with micro-motion only.
//
// Shared with s12 (exported): LOGO placement, brandBackdrop() (bg + glow + bokeh) and drawLogo() so the hand-off is exact.
import { W, H, BEAT, TAU, clamp, lerp, seg, eout, eio, expoOut, back, rnd, text, measure, font, COL, FONT } from '../lib.js';

// ------------------------------------------------------------------ shared brand system (used by s12 too)
export const LOGO = { cx: 540, cy: 600, w: 600, s: 600 / 640 };
LOGO.h = 218 * LOGO.s; LOGO.x = LOGO.cx - LOGO.w / 2; LOGO.y = LOGO.cy - LOGO.h / 2;
export const LOGO_SPLIT = 233;                         // logo px: rings block | wordmark
// logo px -> screen px
export const lp = (x, y) => [LOGO.x + x * LOGO.s, LOGO.y + y * LOGO.s];

const CACHE = {};
function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function logoParts(img) {
  if (CACHE.logo) return CACHE.logo;
  const rings = canvas(img.width, img.height), word = canvas(img.width, img.height);
  let x = rings.getContext('2d'); x.drawImage(img, 0, 0, LOGO_SPLIT, img.height, 0, 0, LOGO_SPLIT, img.height);
  x = word.getContext('2d'); x.drawImage(img, LOGO_SPLIT, 0, img.width - LOGO_SPLIT, img.height, LOGO_SPLIT, 0, img.width - LOGO_SPLIT, img.height);
  return (CACHE.logo = { rings, word });
}
// bokeh sprites: soft optical discs (flat body, slightly brighter rim, feathered edge)
function bokehSprite(hex) {
  const k = 'bk' + hex; if (CACHE[k]) return CACHE[k];
  const c = canvas(160, 160), x = c.getContext('2d');
  const g = x.createRadialGradient(80, 80, 0, 80, 80, 78);
  g.addColorStop(0, hex + 'b8'); g.addColorStop(.7, hex + 'c8'); g.addColorStop(.86, hex + 'e8'); g.addColorStop(.95, hex + '60'); g.addColorStop(1, hex + '00');
  x.fillStyle = g; x.beginPath(); x.arc(80, 80, 79, 0, TAU); x.fill();
  return (CACHE[k] = c);
}
// beat-locked logo glow: snaps to 1 on every beat, decays (shadowBlur 0 <-> 18)
export const beatGlow = b => Math.exp(-(b - Math.floor(b)) * BEAT / .17);

// bg: #0e0e14, breathing radial brand glow, far bokeh plane. `b` = global beat. bokehK 0..1 (s12 fades them in at b73.5)
export function brandBackdrop(E, b, { glow = 1, bokehK = 1 } = {}) {
  const bg = E.bg;
  bg.fillStyle = COL.lmBg; bg.fillRect(0, 0, W, H);
  if (glow > 0) {
    // breathing radial glow centred on the logo (#6a55ff @14 %), plus a faint second lobe lower down so the card has depth
    const br = 1 + .06 * Math.sin((b - 73.5) / 8 * TAU) + .05 * beatGlow(b);
    const g = bg.createRadialGradient(540, 600, 0, 540, 600, 700 * (1 + .03 * Math.sin((b - 73.5) / 4 * TAU)));
    const a = .14 * glow * br;
    g.addColorStop(0, `rgba(106,85,255,${a})`); g.addColorStop(.45, `rgba(106,85,255,${a * .45})`); g.addColorStop(1, 'rgba(106,85,255,0)');
    bg.fillStyle = g; bg.fillRect(0, 0, W, H);
    const g2 = bg.createRadialGradient(540, 1180, 0, 540, 1180, 620);
    g2.addColorStop(0, `rgba(79,107,255,${.05 * glow})`); g2.addColorStop(1, 'rgba(79,107,255,0)');
    bg.fillStyle = g2; bg.fillRect(0, 0, W, H);
  }
  if (bokehK > 0) drawBokeh(bg, b, bokehK, false);
}
// 24 far discs (r 20-70, 6-10 %) drifting up ~20 px/s from b73.5; `front` = 4 big near discs (fg, 3-4 %)
export function drawBokeh(ctx, b, k, front) {
  const t = (b - 73.5) * BEAT;
  const n = front ? 4 : 24;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const s = front ? i * 7.31 + 101 : i * 3.17 + 11;
    const r = front ? 150 + rnd(s + .3) * 110 : 20 + 50 * rnd(s + .3);
    const sp = front ? 34 + 10 * rnd(s + .9) : 14 + 12 * (r - 20) / 50;      // parallax: bigger = nearer = faster
    const span = H + 2 * r + 120;
    let y = rnd(s + .5) * span - sp * t; y = ((y % span) + span) % span - r - 60;
    const x = (front ? (i % 2 ? 980 : 100) + (rnd(s + .7) - .5) * 260 : rnd(s) * W) + 18 * Math.sin(t * .5 + i * 1.7);
    const a = (front ? .03 + .012 * rnd(s + .2) : .06 + .04 * rnd(s + .2)) * k * (.85 + .15 * Math.sin(t * 1.3 + i * 2.1));
    const spr = bokehSprite(rnd(s + .11) < .5 ? COL.lm1 : COL.lm3);
    ctx.globalAlpha = a; ctx.drawImage(spr, x - r, y - r, 2 * r, 2 * r);
  }
  ctx.restore();
}
// LUMARC logo (never recoloured): rings / wordmark alphas separately, breathing scale, violet glow (shadowBlur)
export function drawLogo(ctx, img, { rings = 1, word = 1, scale = 1, glow = 0, dx = 0, dy = 0 } = {}) {
  if (!img) return;
  const P = logoParts(img);
  ctx.save(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  ctx.translate(LOGO.cx + dx, LOGO.cy + dy); ctx.scale(scale, scale); ctx.translate(-LOGO.w / 2, -LOGO.h / 2);
  if (glow > .3) { ctx.shadowColor = 'rgba(106,85,255,.75)'; ctx.shadowBlur = glow; }
  if (rings > .003) { ctx.globalAlpha = rings; ctx.drawImage(P.rings, 0, 0, LOGO.w, LOGO.h); }
  if (word > .003) { ctx.globalAlpha = word; ctx.drawImage(P.word, 0, 0, LOGO.w, LOGO.h); }
  ctx.restore();
}
// anamorphic flare on the logo's white star (where the two rings cross): thin horizontal streak + soft core, additive
export const STAR = lp(95, 112);
export function logoFlare(ctx, k, { scale = 1, len = 170 } = {}) {
  if (k <= .003) return;
  const [sx, sy] = STAR, x = LOGO.cx + (sx - LOGO.cx) * scale, y = LOGO.cy + (sy - LOGO.cy) * scale;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const h = ctx.createLinearGradient(x - len, 0, x + len, 0);
  h.addColorStop(0, 'rgba(120,110,255,0)'); h.addColorStop(.42, `rgba(170,160,255,${.22 * k})`); h.addColorStop(.5, `rgba(255,255,255,${.45 * k})`);
  h.addColorStop(.58, `rgba(170,160,255,${.22 * k})`); h.addColorStop(1, 'rgba(120,110,255,0)');
  ctx.fillStyle = h; ctx.fillRect(x - len, y - 1.5, len * 2, 3);
  ctx.fillStyle = `rgba(150,140,255,${.08 * k})`; ctx.fillRect(x - len * .6, y - 5, len * 1.2, 10);
  const c = ctx.createRadialGradient(x, y, 0, x, y, 46);
  c.addColorStop(0, `rgba(255,255,255,${.35 * k})`); c.addColorStop(.3, `rgba(160,140,255,${.16 * k})`); c.addColorStop(1, 'rgba(106,85,255,0)');
  ctx.fillStyle = c; ctx.fillRect(x - 46, y - 46, 92, 92);
  ctx.restore();
}
// logo breathing (1 % per bar from b73.5) and the beat glow — identical in s12 and s13
export const logoBreath = b => 1 + .005 * (1 - Math.cos(Math.max(0, b - 73.5) / 4 * TAU));

// post levels of the end card (s12 eases into these by b76)
export const END_FX = { bloom: .4, threshold: .93, knee: .05, vignette: .3, grain: .03, rgb: .001 };   // hard knee: logo/pill bloom, type stays crisp

// one continuous, barely-perceptible camera push from the finished logo (b73.5) to the last frame (shared with s12)
export const endZoom = b => 1 + .022 * eio(seg(b, 73.5, 86));

// ------------------------------------------------------------------ end card
const B0 = 76;
const HEAD = [
  { line: 'Want your product', y: 880, words: ['Want', 'your', 'product'], beats: [76.0, 76.25, 76.5] },
  { line: 'to look like this?', y: 960, words: ['to', 'look', 'like', 'this?'], beats: [76.75, 77.0, 77.25, 77.5] },
];
const PILL = { cx: 540, cy: 1140, w: 660, h: 128, r: 64, pad: 110, label: 'DM us "VIDEO"' };
const TAG = { y: 1310, a: 'Be seen.', b: 'Be remembered.', ba: 78.5, bb: 79.0 };
const HANDLE = { y: 1400, s: '@lumarc_studio · slumarc.com', b: 79.25 };
const POP = 78.0;
const SHEENS = [80, 82, 84];

function roundRect(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function pillCanvas() {
  if (CACHE.pill) return CACHE.pill;
  const { w, h, r, pad } = PILL, c = canvas(w + pad * 2, h + pad * 2), x = c.getContext('2d');
  const gr = x.createLinearGradient(pad, 0, pad + w, 0); gr.addColorStop(0, COL.lm1); gr.addColorStop(.5, COL.lm2); gr.addColorStop(1, COL.lm3);
  // outer violet glow (shadowBlur 40, #6a55ff @60 %), then the clean body on top
  x.save(); x.shadowColor = 'rgba(106,85,255,.6)'; x.shadowBlur = 40; x.fillStyle = gr; roundRect(x, pad, pad, w, h, r); x.fill(); x.restore();
  x.fillStyle = gr; roundRect(x, pad, pad, w, h, r); x.fill();
  // glass: soft top highlight + hairline inner rim
  x.save(); roundRect(x, pad, pad, w, h, r); x.clip();
  const hl = x.createLinearGradient(0, pad, 0, pad + h); hl.addColorStop(0, 'rgba(255,255,255,.20)'); hl.addColorStop(.48, 'rgba(255,255,255,.04)'); hl.addColorStop(.5, 'rgba(255,255,255,0)'); hl.addColorStop(1, 'rgba(20,10,60,.10)');
  x.fillStyle = hl; x.fillRect(pad, pad, w, h); x.restore();
  x.strokeStyle = 'rgba(255,255,255,.22)'; x.lineWidth = 1.5; roundRect(x, pad + .75, pad + .75, w - 1.5, h - 1.5, r - .75); x.stroke();
  text(x, PILL.label, pad + w / 2, pad + h / 2 + 2, { size: 54, weight: 700, family: FONT.brand, color: COL.lmWhite, baseline: 'middle', spacing: .5 });
  return (CACHE.pill = c);
}
function lineLayout(ctx, s, words, size, weight) {
  const tw = measure(ctx, s, size, weight, FONT.brand); const x0 = 540 - tw / 2; const out = []; let pre = '';
  for (const w of words) { out.push(x0 + measure(ctx, pre, size, weight, FONT.brand)); pre += w + ' '; }
  return out;
}

export default {
  id: 's13-lumarc', start: 76, end: 86, cutIn: 'none',
  init(E) { if (E.img.logo) logoParts(E.img.logo); pillCanvas(); bokehSprite(COL.lm1); bokehSprite(COL.lm3); },
  draw(E, lt, t) {
    const b = t / BEAT, fg = E.fg, fx = E.fx;
    if (!CACHE.layout) {
      CACHE.layout = HEAD.map(L => lineLayout(fg, L.line, L.words, 64, 600));
      const tw = measure(fg, TAG.a + ' ' + TAG.b, 46, 400, FONT.brand);
      CACHE.tag = [540 - tw / 2, 540 - tw / 2 + measure(fg, TAG.a + ' ', 46, 400, FONT.brand)];
    }
    brandBackdrop(E, b);

    // logo: breathing + beat glow (kicks on b76/78/80/82 a touch stronger)
    const kick = [76, 78, 80, 82, 84].reduce((m, k) => Math.max(m, b >= k ? Math.exp(-(b - k) * BEAT / .25) : 0), 0);
    const gp = Math.max(beatGlow(b), kick);
    drawLogo(fg, E.img.logo, { scale: logoBreath(b), glow: 18 * gp });
    logoFlare(fg, .3 + .7 * gp, { scale: logoBreath(b) });

    // headline: word by word, rising 24 px, blur 8 -> 0, 6 frames
    HEAD.forEach((L, li) => L.words.forEach((w, wi) => {
      const k = seg(b, L.beats[wi], L.beats[wi] + .5); if (k <= 0) return;
      text(fg, w, CACHE.layout[li][wi], L.y + 24 * (1 - expoOut(k)), { size: 64, weight: 600, family: FONT.brand, color: COL.lmWhite, align: 'left',
        alpha: eout(k * 1.15), blur: 8 * (1 - eout(k)) });
    }));

    // CTA pill
    const pk = seg(b, POP, POP + 8 / 12);
    if (pk > 0) {
      const pc = pillCanvas();
      let sc = lerp(.6, 1, back(pk, 2.5));
      if (b > 80) sc *= 1 + .0125 * (1 - Math.cos((b - 80) / 4 * TAU));
      fg.save(); fg.translate(PILL.cx, PILL.cy); fg.scale(sc, sc); fg.globalAlpha = clamp(pk * 4);
      fg.drawImage(pc, -pc.width / 2, -pc.height / 2);
      // pop flash: 1 frame of violet light + a 2-frame white lift on the body only
      const fr = (b - POP) * 12;
      if (fr < 3) {
        roundRect(fg, -PILL.w / 2, -PILL.h / 2, PILL.w, PILL.h, PILL.r);
        fg.globalCompositeOperation = 'lighter'; fg.fillStyle = `rgba(255,255,255,${.28 * (1 - fr / 3)})`; fg.fill();
        if (fr < 1.5) {   // 1-frame violet light around the pill (soft elliptical, no edges)
          fg.save(); fg.globalCompositeOperation = 'lighter'; fg.scale(1, .42);
          const g = fg.createRadialGradient(0, 0, 0, 0, 0, 520); g.addColorStop(0, 'rgba(106,85,255,.16)'); g.addColorStop(1, 'rgba(106,85,255,0)');
          fg.fillStyle = g; fg.fillRect(-520, -520, 1040, 1040); fg.restore();
        }
      }
      // sheens: diagonal white band (80 px, 30 %) sweeping across, clipped to the pill, 8 frames
      for (const sb of SHEENS) {
        const sk = seg(b, sb, sb + 8 / 12); if (sk <= 0 || sk >= 1) continue;
        fg.save(); fg.globalCompositeOperation = 'source-over'; fg.globalAlpha = 1;
        roundRect(fg, -PILL.w / 2, -PILL.h / 2, PILL.w, PILL.h, PILL.r); fg.clip();
        const cx = lerp(-PILL.w / 2 - 140, PILL.w / 2 + 140, eio(sk));
        fg.translate(cx, 0); fg.rotate(.42);
        const g = fg.createLinearGradient(-40, 0, 40, 0);
        g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(.5, 'rgba(255,255,255,.3)'); g.addColorStop(1, 'rgba(255,255,255,0)');
        fg.fillStyle = g; fg.fillRect(-40, -260, 80, 520);
        fg.fillStyle = 'rgba(255,255,255,.12)'; fg.fillRect(54, -260, 10, 520);       // thin trailing glint line
        fg.restore();
      }
      fg.restore();
      // zoom punch with the pop
      fx.zoom *= 1 + .015 * (1 - expoOut(clamp(fr / 8)));
    }

    // 'Be seen. Be remembered.'
    const ta = seg(b, TAG.ba, TAG.ba + .5), tb = seg(b, TAG.bb, TAG.bb + .5);
    text(fg, TAG.a, CACHE.tag[0], TAG.y + 16 * (1 - expoOut(ta)), { size: 46, weight: 400, family: FONT.brand, color: COL.lmMuted, align: 'left', alpha: eout(ta) });
    text(fg, TAG.b, CACHE.tag[1], TAG.y + 16 * (1 - expoOut(tb)), { size: 46, weight: 400, family: FONT.brand, color: COL.lmMuted, align: 'left', alpha: eout(tb) });
    // handle
    const hk = seg(b, HANDLE.b, HANDLE.b + .5);
    text(fg, HANDLE.s, 540, HANDLE.y + 10 * (1 - expoOut(hk)), { size: 36, weight: 500, family: FONT.brand, color: COL.lmMuted, alpha: eout(hk), spacing: .5 });

    // near bokeh plane drifting in front of everything (very faint: depth, never legibility)
    drawBokeh(fg, b, 1, true);

    // post: clean brand grade, a slow 1 % push-in over the whole card (never static)
    fx.bloom = END_FX.bloom; fx.bloomThreshold = END_FX.threshold; fx.bloomKnee = END_FX.knee; fx.vignette = END_FX.vignette; fx.grain = END_FX.grain; fx.rgb = END_FX.rgb;
    fx.zoom *= endZoom(b);
  },
};
