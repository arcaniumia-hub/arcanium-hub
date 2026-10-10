// PLACEHOLDER — to be implemented from storyboard.json (s02-break: BREAK — the noise-cancelled ad)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's02-break', start: 11, end: 16,
  draw(E, lt) { text(E.fg, 's02-break', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
