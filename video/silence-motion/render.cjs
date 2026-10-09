// Renders every frame (DUR × 30) to silence-motion.mp4 (needs music.wav from sound.py and teardown.bundle.js from `npm run build`).
// node render.cjs              -> video
// node render.cjs stills 2 9.8 -> JPEG stills (s<t>.jpg)
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path');
(async () => {
  const mode = process.argv[2] || 'video';
  const b = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.addInitScript(() => { window.__RENDER = true; });
  pg.on('pageerror', e => console.error('PAGEERR', e.message));
  await pg.goto('file://' + path.resolve(__dirname, 'index.html')); await pg.evaluate(() => window.ready);
  if (mode === 'stills') {
    for (const t of process.argv.slice(3)) {
      const d = await pg.evaluate(t => { renderAt(+t); return document.getElementById('c').toDataURL('image/jpeg', .8); }, t);
      require('fs').writeFileSync('s' + t + '.jpg', Buffer.from(d.split(',')[1], 'base64'));
    }
    await b.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-', '-i', 'music.wav',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000',
    '-movflags', '+faststart', '-shortest', 'silence-motion.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(await pg.evaluate(() => DUR) * 30);
  for (let f = 0; f < N; f++) {
    const d = await pg.evaluate(t => { renderAt(t); return document.getElementById('c').toDataURL('image/jpeg', .95); }, f / 30);
    if (!ff.stdin.write(Buffer.from(d.slice(23), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log('frame', f);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('render-done');
})();
