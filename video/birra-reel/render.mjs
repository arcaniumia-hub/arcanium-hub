// Renders all frames and pipes them to ffmpeg -> out/frames.mp4 (silent)
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs'; import path from 'path'; import url from 'url';
const dir = path.dirname(url.fileURLToPath(import.meta.url));
const FPS = 30, DUR = 30;
fs.mkdirSync(path.join(dir, 'out'), { recursive: true });
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high', path.join(dir, 'out', 'frames.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
const b = await chromium.launch();
const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
pg.on('pageerror', e => console.error('PAGEERR', e.message));
await pg.goto('file://' + path.join(dir, 'index.html'));
await pg.evaluate(() => window.ready);
for (let f = 0; f < FPS * DUR; f++) {
  const d = await pg.evaluate(t => { renderAt(t); return document.getElementById('c').toDataURL('image/png'); }, f / FPS);
  if (!ff.stdin.write(Buffer.from(d.slice(22), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  if (f % 150 === 0) console.log('frame', f);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await b.close();
