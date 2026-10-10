// PLACEHOLDER — to be implemented from storyboard.json (s08-gyro: DROP 2 — the 360° type gyroscope)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's08-gyro', start: 40, end: 48,
  draw(E, lt) { text(E.fg, 's08-gyro', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
