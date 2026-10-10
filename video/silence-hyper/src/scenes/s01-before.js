// PLACEHOLDER — to be implemented from storyboard.json (s01-before: BEFORE — the PowerPoint ad)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's01-before', start: 0, end: 11,
  draw(E, lt) { text(E.fg, 's01-before', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
