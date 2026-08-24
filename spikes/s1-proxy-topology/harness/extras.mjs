// Things the screenshot matrix cannot answer:
//  1. does the semantic host stay hittable/focusable through the sandwich (X1)
//  2. Chromium only: composited layer count + compositing reasons for the proxies
//  3. Chromium only: *real* page zoom (Emulation.setPageScaleFactor), which CSS
//     `zoom` and deviceScaleFactor each only half-simulate
import { chromium, firefox, webkit } from 'playwright';
import { createServer } from 'node:http';
import { readFileSync, existsSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, extname } from 'node:path';
import { diffROI, load } from './diff.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const PAGES = join(ROOT, 'pages');
const SHOTS = join(ROOT, 'shots');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };
const F = 'blur(20px) saturate(1.8)';

function serve() {
  return new Promise((res) => {
    const s = createServer((req, r) => {
      const u = new URL(req.url, 'http://x');
      const f = join(PAGES, u.pathname === '/' ? 'bench.html' : u.pathname.slice(1));
      if (!existsSync(f)) { r.writeHead(404); r.end(); return; }
      r.writeHead(200, { 'content-type': MIME[extname(f)] || 'application/octet-stream' });
      r.end(readFileSync(f));
    });
    s.listen(0, '127.0.0.1', () => res({ server: s, port: s.address().port }));
  });
}

async function hitTest(engine, port) {
  const b = await engine.launch();
  const ctx = await b.newContext({ viewport: { width: 1000, height: 800 } });
  const page = await ctx.newPage();
  const q = new URLSearchParams({ mode: 'proxy', pad: '60', groups: 'split', tint: '0.28', hi: '0.35', text: 'on', filter: F });
  await page.goto(`http://127.0.0.1:${port}/bench.html?${q}`);
  await page.waitForSelector('html[data-s1-ready="1"]');
  const res = await page.evaluate(() => {
    const out = {};
    window.__clicks = [];
    document.querySelectorAll('button.glass-host').forEach((b, i) => {
      b.dataset.idx = String(i);
      b.addEventListener('click', () => window.__clicks.push(i));
    });
    const s = window.__s1.SHAPES.a;
    const cx = s.x + s.w / 2, cy = s.y + s.h / 2;
    const el = document.elementFromPoint(cx, cy);
    out.elementFromPointTag = el ? el.tagName + '.' + el.className : null;
    out.stack = document.elementsFromPoint(cx, cy).map((e) => e.tagName + '.' + (e.className || e.id));
    out.center = [cx, cy];
    return out;
  });
  const s = { x: 100, y: 300, w: 200, h: 120 };
  await page.mouse.click(s.x + s.w / 2, s.y + s.h / 2);
  res.clicksReceived = await page.evaluate(() => window.__clicks);
  await page.keyboard.press('Tab');
  res.focusAfterTab = await page.evaluate(() => {
    const a = document.activeElement;
    return a ? a.tagName + '.' + a.className : null;
  });
  // the proxy must never be the hit target
  res.proxyPointerEvents = await page.evaluate(() =>
    getComputedStyle(document.querySelector('.proxy')).pointerEvents);
  await b.close();
  return res;
}

async function chromiumLayersAndZoom(port) {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1000, height: 800 } });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);

  const out = {};
  const q = (o) => new URLSearchParams(o).toString();

  // --- composited layers for split proxies + canvases
  for (const [label, params] of Object.entries({
    'split-pad60': { mode: 'proxy', pad: '60', groups: 'split', tint: '0.28', hi: '0.35', filter: F },
    'single-pad60': { mode: 'proxy', pad: '60', groups: 'single', tint: '0.28', hi: '0.35', filter: F },
    'padfull': { mode: 'proxy', pad: 'full', tint: '0.28', hi: '0.35', filter: F },
    'inplace': { mode: 'inplace', tint: '0.28', hi: '0.35', filter: F },
  })) {
    await page.goto(`http://127.0.0.1:${port}/bench.html?${q(params)}`);
    await page.waitForSelector('html[data-s1-ready="1"]');
    await page.waitForTimeout(300);
    const layers = await new Promise(async (res) => {
      const seen = [];
      const handler = (e) => seen.push(e);
      cdp.on('LayerTree.layerTreeDidChange', handler);
      await cdp.send('LayerTree.enable');
      setTimeout(async () => {
        cdp.off('LayerTree.layerTreeDidChange', handler);
        await cdp.send('LayerTree.disable');
        res(seen.length ? seen[seen.length - 1].layers || [] : []);
      }, 700);
    });
    const reasons = [];
    for (const l of layers.slice(0, 40)) {
      try {
        const r = await cdp.send('LayerTree.compositingReasons', { layerId: l.layerId });
        reasons.push({ w: l.width, h: l.height, ids: r.compositingReasonIds || r.compositingReasons });
      } catch { /* layer may be gone */ }
    }
    out['layers:' + label] = { count: layers.length, reasons };
  }

  // --- real page zoom via CDP, proxy vs inplace
  mkdirSync(join(SHOTS, 'chromium'), { recursive: true });
  const CAP = { x: 0, y: 240, width: 660, height: 240 };
  for (const scale of [1.5, 2]) {
    const shots = {};
    for (const [label, params] of Object.entries({
      inplace: { mode: 'inplace', filter: F },
      padfull: { mode: 'proxy', pad: 'full', filter: F },
      pad60: { mode: 'proxy', pad: '60', filter: F },
    })) {
      await page.goto(`http://127.0.0.1:${port}/bench.html?${q(params)}`);
      await page.waitForSelector('html[data-s1-ready="1"]');
      await cdp.send('Emulation.setPageScaleFactor', { pageScaleFactor: scale });
      await page.waitForTimeout(300);
      const p = join(SHOTS, 'chromium', `pagezoom${scale}-${label}.png`);
      await page.screenshot({ path: p, clip: CAP });
      shots[label] = p;
      await cdp.send('Emulation.setPageScaleFactor', { pageScaleFactor: 1 });
    }
    const A = load(shots.inplace), Bp = load(shots.padfull), C = load(shots.pad60);
    out['pageZoom' + scale] = {
      'inplace vs padfull': diffROI(A, Bp, { x: 0, y: 0, w: CAP.width, h: CAP.height }),
      'padfull vs pad60': diffROI(Bp, C, { x: 0, y: 0, w: CAP.width, h: CAP.height }),
    };
  }
  await b.close();
  return out;
}

const { server, port } = await serve();
const res = { hitTest: {} };
for (const [name, e] of Object.entries({ chromium, firefox, webkit })) {
  try { res.hitTest[name] = await hitTest(e, port); }
  catch (err) { res.hitTest[name] = { error: err.message }; }
}
try { res.chromium = await chromiumLayersAndZoom(port); }
catch (err) { res.chromium = { error: err.message }; }
server.close();
mkdirSync(SHOTS, { recursive: true });
writeFileSync(join(SHOTS, 'extras.json'), JSON.stringify(res, null, 2));
console.log(JSON.stringify(res.hitTest, null, 2));
console.log('wrote shots/extras.json');
