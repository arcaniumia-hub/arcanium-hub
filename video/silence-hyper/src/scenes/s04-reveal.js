// PLACEHOLDER — to be implemented from storyboard.json (s04-reveal: REVEAL — the ring calms the sound sea)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's04-reveal', start: 20, end: 24,
  draw(E, lt) { text(E.fg, 's04-reveal', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
