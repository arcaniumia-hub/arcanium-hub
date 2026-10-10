// PLACEHOLDER — to be implemented from storyboard.json (s06-noise: THE NOISE — 4 turns, 256 words, the clamp)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's06-noise', start: 28, end: 36,
  draw(E, lt) { text(E.fg, 's06-noise', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
