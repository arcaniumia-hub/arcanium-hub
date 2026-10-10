// PLACEHOLDER — to be implemented from storyboard.json (s12-handoff: HANDOFF — the ring becomes LUMARC)
import { text, COL, FONT } from '../lib.js';
export default {
  id: 's12-handoff', start: 70, end: 76,
  draw(E, lt) { text(E.fg, 's12-handoff', 540, 960, { size: 60, weight: 700, family: FONT.mono, color: COL.gold }); },
};
