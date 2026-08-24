// Does the engine actually rasterise backdrop-filter into a screenshot?
// Controls (filter, mix-blend-mode, opacity) separate "backdrop-filter is a no-op"
// from "this build composites nothing".
import { chromium, firefox, webkit } from 'playwright';
import { PNG } from 'pngjs';
import { createServer } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, extname } from 'node:path';

const PAGES = join(dirname(fileURLToPath(import.meta.url)), '..', 'pages');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };
const { port } = await new Promise((res) => {
  const s = createServer((req, r) => {
    const u = new URL(req.url, 'http://x');
    const f = join(PAGES, u.pathname.slice(1));
    if (!existsSync(f)) { r.writeHead(404); r.end(); return; }
    r.writeHead(200, { 'content-type': MIME[extname(f)] || 'application/octet-stream' });
    r.end(readFileSync(f));
  });
  s.listen(0, '127.0.0.1', () => res({ server: s, port: s.address().port }));
});

const CASES = {
  'pw-chromium':      [chromium, {}],
  'retail-chrome':    [chromium, { channel: 'chrome' }],
  'pw-firefox':       [firefox, {}],
  'pw-firefox-prefs': [firefox, { firefoxUserPrefs: {
      'gfx.webrender.all': true,
      'layout.css.backdrop-filter.enabled': true,
      'gfx.webrender.compositor': true,
      'layers.acceleration.force-enabled': true,
    } }],
  'pw-firefox-headed':[firefox, { headless: false }],
  'pw-webkit':        [webkit, {}],
  'pw-webkit-headed': [webkit, { headless: false }],
};

console.log('row values at x=150; expected 128 / 128 / 128 / 159 on a #404040 ground\n');
for (const [name, [L, opts]] of Object.entries(CASES)) {
  try {
    const b = await L.launch(opts);
    const ctx = await b.newContext({ viewport: { width: 400, height: 300 } });
    const p = await ctx.newPage();
    await p.goto(`http://127.0.0.1:${port}/min.html`);
    await p.waitForTimeout(400);
    const png = PNG.sync.read(await p.screenshot());
    const at = (x, y) => png.data[(png.width * y + x) << 2];
    console.log(
      name.padEnd(20), (b.version() + '').padEnd(20),
      'backdrop-filter=' + at(150, 30),
      'filter=' + at(150, 90),
      'mix-blend=' + at(150, 150),
      'opacity=' + at(150, 210));
    await b.close();
  } catch (e) {
    console.log(name.padEnd(20), 'ERR', e.message.split('\n')[0]);
  }
}
process.exit(0);
