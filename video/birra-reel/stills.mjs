// usage: node stills.mjs outdir t1 t2 ...
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path'; import url from 'url';
const dir = path.dirname(url.fileURLToPath(import.meta.url));
const [out, ...times] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch();
const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
pg.on('pageerror', e => console.error('PAGEERR', e.message));
pg.on('console', m => console.log('console:', m.text()));
await pg.goto('file://' + path.join(dir, 'index.html'));
await pg.evaluate(() => window.ready);
for (const t of times) {
  const d = await pg.evaluate(t => { renderAt(+t); return document.getElementById('c').toDataURL('image/jpeg', .85); }, t);
  fs.writeFileSync(path.join(out, `t${(+t).toFixed(2)}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
}
await b.close();
