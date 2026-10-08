// node render.mjs stills <dir> t1 t2 ...   |   node render.mjs video <out.mp4> <music.wav> [fps]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import http from 'http'; import fs from 'fs'; import path from 'path'; import url from 'url';
const dir = path.dirname(url.fileURLToPath(import.meta.url));
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.woff2': 'font/woff2', '.json': 'application/json' };
const srv = http.createServer((q, r) => { const f = path.join(dir, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0, '127.0.0.1');
await new Promise(r => srv.once('listening', r));
const port = srv.address().port;
const [mode, outArg, ...rest] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
pg.on('pageerror', e => console.error('PAGEERR', e.message));
pg.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('console:', m.text().slice(0, 200)); });
await pg.goto(`http://127.0.0.1:${port}/index.html`); await pg.evaluate(() => window.ready);
const grab = q => pg.evaluate(([t, q]) => { renderAt(t); return document.getElementById('out').toDataURL('image/jpeg', q); }, q);
if (mode === 'stills') {
  fs.mkdirSync(outArg, { recursive: true });
  for (const t of rest) { const d = await pg.evaluate(t => { renderAt(+t); return document.getElementById('out').toDataURL('image/jpeg', .85); }, t); fs.writeFileSync(path.join(outArg, `t${(+t).toFixed(2)}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
} else {
  const [music, fpsArg] = rest; const FPS = +(fpsArg || 30);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', music,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-movflags', '+faststart', '-shortest', outArg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = 0; f < 30 * FPS; f++) {
    const d = await pg.evaluate(t => { renderAt(t); return document.getElementById('out').toDataURL('image/jpeg', .95); }, f / FPS);
    if (!ff.stdin.write(Buffer.from(d.slice(23), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log('frame', f, Math.round((Date.now() - t0) / 1000) + 's');
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('render-done');
}
await b.close(); srv.close();
