// Every asset is inlined as a data: URL by esbuild, so index.html works offline from file:// (no tainted canvases).
import before from '../img/before.jpg';
import hero from '../img/hero.jpg';
import macro from '../img/macro.jpg';
import orbit0 from '../img/orbit0.jpg';
import orbit1 from '../img/orbit1.jpg';
import orbit2 from '../img/orbit2.jpg';
import orbit3 from '../img/orbit3.jpg';
import logo from '../img/logo.png';
import unb300 from '../fonts/unbounded-latin-300-normal.woff2';
import unb500 from '../fonts/unbounded-latin-500-normal.woff2';
import unb700 from '../fonts/unbounded-latin-700-normal.woff2';
import unb800 from '../fonts/unbounded-latin-800-normal.woff2';
import unb900 from '../fonts/unbounded-latin-900-normal.woff2';
import anton from '../fonts/anton-latin-400-normal.woff2';
import outfit from '../fonts/outfit.woff2';
import inter from '../fonts/inter-latin-wght-normal.woff2';
import mono4 from '../fonts/jetbrains-mono-latin-400-normal.woff2';
import mono7 from '../fonts/jetbrains-mono-latin-700-normal.woff2';
import serif from '../fonts/instrument-serif-latin-400-normal.woff2';
import serifI from '../fonts/instrument-serif-latin-400-italic.woff2';
import comic from '../fonts/comic-neue-latin-700-normal.woff2';

export const IMAGES = { before, hero, macro, orbit0, orbit1, orbit2, orbit3, logo };
// [family, src, weight, style]
export const FONTS = [
  ['Unbounded', unb300, 300], ['Unbounded', unb500, 500], ['Unbounded', unb700, 700], ['Unbounded', unb800, 800], ['Unbounded', unb900, 900],
  ['Anton', anton, 400], ['Outfit', outfit, '100 900'], ['Inter', inter, '100 900'],
  ['JetBrains Mono', mono4, 400], ['JetBrains Mono', mono7, 700],
  ['Instrument Serif', serif, 400], ['Instrument Serif', serifI, 400, 'italic'], ['Comic Neue', comic, 700],
];
