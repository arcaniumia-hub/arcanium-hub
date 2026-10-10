// PLACEHOLDER — to be implemented from storyboard.json (s07-mute: THE MUTE — frozen explosion, −42 dB)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's07-mute', start: 36, end: 40,
  draw(E, lt) { text(E.fg, 's07-mute', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
