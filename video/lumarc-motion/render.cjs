// Renders all 900 frames to lumarc-motion.mp4 (needs before.png, after.png, logo.png and music.wav next to index.html).
// node render.cjs            -> video
// node render.cjs stills 2 9.8 -> JPEG stills
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path');
(async () => {
  const mode = process.argv[2] || 'video';
  const b = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security'] });
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => console.error('PAGEERR', e.message));
  await pg.goto('file://' + path.resolve(__dirname, 'index.html')); await pg.evaluate(() => window.ready);
  if (mode === 'stills') {
    for (const t of process.argv.slice(3)) { const d = await pg.evaluate(t => { renderAt(+t); return document.getElementById('c').toDataURL('image/jpeg', .8); }, t);
      require('fs').writeFileSync('s' + t + '.jpg', Buffer.from(d.split(',')[1], 'base64')); }
    await b.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-', '-i', 'music.wav',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-movflags', '+faststart', '-shortest', 'lumarc-motion.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < 900; f++) {
    const d = await pg.evaluate(t => { renderAt(t); return document.getElementById('c').toDataURL('image/jpeg', .96); }, f / 30);
    if (!ff.stdin.write(Buffer.from(d.slice(23), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log('frame', f);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('render-done');
})();
