#!/usr/bin/env node
// Run from any directory: node docs/research/scripts/capsule-responsive-regression.mjs
// Uses the workspace build and real Chromium; never writes baseline captures or audits.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFile, mkdir } from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const require = createRequire(path.join(repo, 'packages/platform-web/package.json'));
const { chromium } = require('@playwright/test');
const output = path.join(repo, 'figma-design-workspace/capsule-responsive-fix');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
const server = http.createServer(async (req, res) => {
  const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  const file = path.resolve(repo, `.${pathname.endsWith('/') ? `${pathname}index.html` : pathname}`);
  if (!file.startsWith(`${repo}${path.sep}`)) { res.writeHead(403).end(); return; }
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch { res.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
let browser;
let checks = 0;
try {
  await mkdir(output, { recursive: true });
  browser = await chromium.launch({ channel: 'chromium', headless: true });
  for (const slug of ['park-trails', 'music-player', 'transit-ops']) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`${origin}/apps/demos/${slug}/`);
    await page.waitForFunction(() => window.__vitrea?.renderInput().planes.length > 0);
    await page.evaluate(() => document.fonts.ready);
    const widths = slug === 'park-trails' ? [720, 721, 731, 732, 733, 748, 749, 900, 1440]
      : slug === 'music-player' ? [349, 350, 351, 399, 400, 401, 900, 1440]
      : [1022, 1023, 1024, 1025, 1440];
    // Three complete round trips on the same document catch stale host handles.
    for (let round = 0; round < 3; round++) {
      for (const width of [...widths, ...widths.slice(0, -1).reverse()]) {
        await page.setViewportSize({ width, height: 900 });
        await page.waitForTimeout(180);
        const result = await page.evaluate(slug => {
          const root = window.__vitrea;
          const nodes = root.renderInput().planes.flatMap(p => p.nodes);
          function element(selector) {
            const el = document.querySelector(selector);
            const bounds = el.getBoundingClientRect().toJSON();
            const matching = nodes.filter(n => Math.abs(n.bounds.x - bounds.x) < 0.5
              && Math.abs(n.bounds.y - bounds.y) < 0.5
              && Math.abs(n.bounds.width - bounds.width) < 0.5
              && Math.abs(n.bounds.height - bounds.height) < 0.5);
            return { bounds, display: getComputedStyle(el).display,
              padding: parseFloat(getComputedStyle(el).paddingLeft),
              nodes: matching.map(n => ({ shape: n.shapeFamily, radii: [...n.radii] })),
              registered: el.hasAttribute('data-vitrea-node') };
          }
          return slug === 'park-trails' ? { planner: element('.planner'), cta: element('.cta'),
            inline: element('.cta-inline') }
            : slug === 'music-player' ? { transport: element('#transport'),
              times: [...document.querySelectorAll('#transport .time')].map(el => el.getBoundingClientRect().toJSON()),
              scrub: element('#transport .slider') }
            : { view: element('#view') };
        }, slug);
        const label = `${slug} ${width}px round ${round + 1}`;
        function shape(surface, family, radius) {
          assert.equal(surface.nodes.length, 1, `${label}: exactly one live host`);
          assert.equal(surface.nodes[0].shape, family, label);
          assert.deepEqual(surface.nodes[0].radii, [radius, radius, radius, radius], label);
        }
        if (slug === 'park-trails') {
          const narrow = width <= 748;
          shape(result.planner, narrow ? 'fixed-rounded-rect' : 'capsule', narrow ? 22 : 40);
          assert.equal(result.cta.registered, !narrow, `${label}: CTA registration`);
          if (narrow) {
            assert.equal(result.cta.display, 'none', label);
            assert.notEqual(result.inline.display, 'none', label);
          } else {
            shape(result.cta, 'capsule', 24);
            assert.ok(result.cta.bounds.left - result.planner.bounds.right >= 16,
              `${label}: planner/CTA gap must preserve 16px`);
            assert.equal(result.planner.padding, 16, label);
          }
        } else if (slug === 'music-player') {
          shape(result.transport, 'capsule', 44);
          for (const time of result.times) {
            // Readout corners, not just its centre, must stay inside the rounded silhouette.
            const b = result.transport.bounds;
            const dy = Math.max(Math.abs(time.top - (b.top + 44)), Math.abs(time.bottom - (b.top + 44)));
            const inset = 44 - Math.sqrt(44 ** 2 - dy ** 2);
            assert.ok(time.left >= b.left + inset && time.right <= b.right - inset,
              `${label}: time text must stay inside curved ends`);
          }
          assert.ok(result.scrub.bounds.width >= 20, `${label}: usable scrub track`);
          assert.equal(result.transport.padding, width <= 400 ? 12 : 24, label);
        } else {
          const narrow = width < 1024;
          shape(result.view, narrow ? 'capsule' : 'fixed-rounded-rect', narrow ? 22 : 14);
          assert.equal(result.view.bounds.width, narrow ? 140 : 44, label);
          assert.equal(result.view.bounds.height, narrow ? 44 : 140, label);
        }
        assert.deepEqual(errors, [], `${label}: no page exceptions`);
        if (round === 0 && widths.includes(width)) {
          await page.screenshot({ path: path.join(output, `${slug}-${width}-after.png`) });
        }
        checks++;
      }
    }
    await page.close();
    console.log(`PASS ${slug}: boundary widths and three responsive round trips`);
  }
  console.log(`PASS ${checks} layout states; captures: ${output}`);
} finally {
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}
