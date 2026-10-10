// Headless renderer (Playwright + Chromium, CPU WebGL via SwiftShader). Run `npm run build` first.
//   node tools/render.cjs stills <outDir> <t1> <t2> ...            full-res JPEG frames  <outDir>/t<sec>.jpg
//   node tools/render.cjs sheet  <out.jpg> <from> <to> <step> [cols] contact sheet (270x480 cells, time labels)
//   node tools/render.cjs video  <out.mp4> [audio.wav|-] [from] [to] video at 30 fps (no audio if '-')
//   node tools/render.cjs info                                       prints scene list + DUR
// PAGE=tmp/<id>/index.html renders a single-scene build (node tools/build.cjs <id>).
// Times are in seconds (beats * 0.4). Needs NODE_PATH to contain playwright (e.g. /opt/node-tools/node_modules).
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path'); const fs = require('fs');
(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--allow-file-access-from-files', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 540, height: 960 } });
  await pg.addInitScript(() => { window.__RENDER = true; });
  pg.on('pageerror', e => console.error('PAGEERR', e.message));
  pg.on('console', m => { if ((m.type() === 'error' || m.type() === 'warning') && !/ERR_FILE_NOT_FOUND/.test(m.text())) console.error('console:', m.text().slice(0, 300)); });
  await pg.goto('file://' + path.resolve(process.env.PAGE || path.join(__dirname, '..', 'index.html')));
  await pg.evaluate(() => window.ready);
  const grab = (t, q) => pg.evaluate(([t, q]) => { renderAt(t); return E.canvas.toDataURL('image/jpeg', q); }, [t, q]);
  const t0 = Date.now();
  if (mode === 'info') {
    console.log(JSON.stringify(await pg.evaluate(() => ({ DUR, scenes: SCENE_LIST })), null, 1));
  } else if (mode === 'stills') {
    fs.mkdirSync(out, { recursive: true });
    for (const t of rest) { const d = await grab(+t, .88); fs.writeFileSync(path.join(out, `t${(+t).toFixed(2)}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
  } else if (mode === 'sheet') {
    const [from, to, step, cols = 6] = rest.map(Number);
    const times = []; for (let t = from; t <= to + 1e-6; t += step) times.push(+t.toFixed(3));
    const d = await pg.evaluate(([times, cols]) => {
      const cw = 270, ch = 480, rows = Math.ceil(times.length / cols);
      const c = document.createElement('canvas'); c.width = cw * cols; c.height = ch * rows; const x = c.getContext('2d');
      times.forEach((t, i) => {
        renderAt(t); const cx = (i % cols) * cw, cy = Math.floor(i / cols) * ch;
        x.drawImage(E.canvas, cx, cy, cw, ch);
        x.fillStyle = 'rgba(0,0,0,.6)'; x.fillRect(cx, cy, 120, 26); x.fillStyle = '#ff0'; x.font = '16px monospace';
        x.fillText(t.toFixed(2) + 's b' + (t / .4).toFixed(1), cx + 4, cy + 18);
      });
      return c.toDataURL('image/jpeg', .85);
    }, [times, cols]);
    fs.writeFileSync(out, Buffer.from(d.split(',')[1], 'base64'));
  } else if (mode === 'video') {
    const [audio = '-', fromS, toS] = rest; const DUR = await pg.evaluate(() => DUR);
    const from = fromS ? +fromS : 0, to = toS ? +toS : DUR, N = Math.round((to - from) * 30);
    const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-'];
    if (audio !== '-') args.push('-ss', String(from), '-i', audio);
    args.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p');
    if (audio !== '-') args.push('-c:a', 'aac', '-b:a', '192k', '-shortest');
    args.push('-movflags', '+faststart', out);
    const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < N; f++) {
      const d = await grab(from + f / 30, .95);
      if (!ff.stdin.write(Buffer.from(d.slice(23), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 60 === 0) console.log('frame', f, '/', N, Math.round((Date.now() - t0) / 1000) + 's');
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('render-done');
  }
  console.error(`[${mode}] ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await b.close();
})();
