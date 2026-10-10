// PLACEHOLDER — to be implemented from storyboard.json (s03-this: THIS. — windows, shear, and the period that draws the ring)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's03-this', start: 16, end: 20,
  draw(E, lt) { text(E.fg, 's03-this', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
