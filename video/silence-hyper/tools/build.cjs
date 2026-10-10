// node tools/build.cjs            -> full film: bundle.js (index.html)
// node tools/build.cjs <sceneId>  -> that scene alone: tmp/<sceneId>/bundle.js + tmp/<sceneId>/index.html
//                                    (render it with PAGE=tmp/<sceneId>/index.html node tools/render.cjs ...)
const esbuild = require('esbuild'); const fs = require('fs'); const path = require('path');
const root = path.resolve(__dirname, '..'); const id = process.argv[2];
const loader = { '.jpg': 'dataurl', '.png': 'dataurl', '.woff2': 'dataurl' };
(async () => {
  let outfile = path.join(root, 'bundle.js'); const plugins = [];
  if (id) {
    const dir = path.join(root, 'tmp', id); fs.mkdirSync(dir, { recursive: true });
    const sceneFile = path.join(root, 'src', 'scenes', id + '.js');
    if (!fs.existsSync(sceneFile)) { console.error('no such scene file', sceneFile); process.exit(1); }
    const idx = path.join(dir, 'index-single.js');
    fs.writeFileSync(idx, `import s from ${JSON.stringify(sceneFile)};\nexport default [s];\n`);
    plugins.push({ name: 'single-scene', setup(b) { b.onResolve({ filter: /scenes[\\/]index\.js$/ }, () => ({ path: idx })); } });
    outfile = path.join(dir, 'bundle.js');
    fs.writeFileSync(path.join(dir, 'index.html'), fs.readFileSync(path.join(root, 'index.html'), 'utf8'));
  }
  await esbuild.build({ entryPoints: [path.join(root, 'src', 'main.js')], bundle: true, format: 'iife', minify: !id, sourcemap: false,
    loader, outfile, plugins, logLevel: 'warning', tsconfigRaw: '{}' });
  console.log('built', path.relative(root, outfile));
})().catch(e => { console.error(e.message); process.exit(1); });
