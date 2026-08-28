// S1 follow-up driver: cross-group backdrop leak as a function of group separation.
//
//   node harness/run.mjs            # full sweep + the sigma=20 replication of S1
//   node harness/run.mjs --quick    # checker only, fewer separations
//
// For every (backdrop class, separation) cell it captures three renderings of the
// same page — one proxy covering both groups, two proxies painted A-then-B, the
// same two painted B-then-A — and diffs them. The three diffs separate the two
// things a split-vs-single comparison can be measuring:
//
//   split(AB) vs single  : the whole error a two-group topology introduces
//   split(BA) vs single  : the same, with paint order reversed
//   split(AB) vs split(BA): identical geometry, opposite order, so this is the
//                           chaining signature alone with no padding component
//
// Every capture runs twice; the two passes must be byte-identical or the cell is
// flagged. That is the experiment's own noise floor, and it is meant to be zero.

import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { createHash } from 'node:crypto';
import { readFileSync, mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, extname } from 'node:path';
import { diffROI, heatmap, load } from './diff.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const PAGES = join(ROOT, 'pages');
const SHOTS = join(ROOT, 'shots');
const RESULTS = join(ROOT, 'results');

const QUICK = process.argv.includes('--quick');

// S1's capture window, widened on the right only (S1 used 660): the widest cell
// here is sigma 40 at a 6-sigma separation, which puts B's right edge at 740.
const CAP = { x: 0, y: 240, width: 900, height: 240 };
const VIEW = { width: 1000, height: 800 };

// --------------------------------------------------------------- static server

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };
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

// -------------------------------------------------------------------- the grid

// Separations as multiples of sigma. The interesting range is entirely below the
// current trigger: the check fires whenever the padded boxes intersect, which at
// the shipped padding of 3 sigma per side is any separation under 6 sigma.
const SIGMA_MULTIPLES = QUICK
  ? [0.25, 0.5, 1, 2, 3, 4, 6]
  : [0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 6, 8];

const BACKDROPS = QUICK ? ['checker'] : ['checker', 'image', 'gradient'];

// The same sweep at two more radii. S1's own doctrine for the padding rule was
// that one radius cannot tell a real rule from a coincidence, so the separation
// boundary gets the same treatment: sigma 8, 20 and 40 span 5x. The multiples
// stop at 6 because 6 sigma is where the padded boxes stop intersecting at all,
// which is the current trigger — past it there is nothing left to measure.
const SCALE_MULTIPLES = [0.4, 1, 1.5, 2, 2.5, 3, 4, 6];

/** One measured cell: a sigma, a padding, a backdrop, a separation. */
function cells() {
  const out = [];
  for (const bg of BACKDROPS) {
    for (const m of SIGMA_MULTIPLES) {
      const sigma = 8;
      out.push({ label: `s8/${bg}/${m}sigma`, sigma, pad: 3 * sigma, bg, gap: Math.round(m * sigma), mult: m });
    }
  }
  if (!QUICK) {
    for (const sigma of [20, 40]) {
      for (const bg of ['mixed', 'checker']) {
        for (const m of SCALE_MULTIPLES) {
          out.push({
            // `s20/mixed/0.4sigma` and `s20/mixed/2sigma` are S1's own two
            // published leak-table rows (an 8px and a 40px gap at padding 60 on
            // S1's scene) — the replication check, not a new condition.
            label: `s${sigma}/${bg}/${m}sigma`, sigma, pad: 3 * sigma, bg,
            gap: Math.round(m * sigma), mult: m,
            repro: sigma === 20 && bg === 'mixed' && (m === 0.4 || m === 2),
          });
        }
      }
    }
    // The nominal radius on S1's scene, so the backdrop class is not confounded
    // with the radius when the sigma=20 rows are read against the sigma=8 ones.
    for (const m of SCALE_MULTIPLES) {
      out.push({
        label: `s8/mixed/${m}sigma`, sigma: 8, pad: 24, bg: 'mixed', gap: Math.round(m * 8), mult: m,
      });
    }
    // The demo's actual warning. apps/demo's `toolbar` and `toolbar-menu` groups
    // sit 56 CSS px apart (styles.css `.toolbar__menu { margin-left: 3.5rem }`),
    // and the warning fires only under `reducedTransparency`, which multiplies
    // frost by 1.75: sigma 14, padding 42 each, so 84 px of clearance is wanted
    // and 56 is authored. 56/14 = 4 sigma. Bracketed by the 88 px the package's
    // own e2e uses as the clean case, by the padding itself, and by 2 sigma.
    for (const bg of ['checker', 'image']) {
      for (const gap of [28, 42, 56, 84]) {
        out.push({
          label: `demo-s14/${bg}/${gap}px`, sigma: 14, pad: 42, bg, gap, mult: gap / 14,
          demo: gap === 56,
        });
      }
    }
  }
  return out;
}

// ----------------------------------------------------------------------- ROIs

// Capture-local coordinates: page y minus CAP.y.
const local = (r) => ({ ...r, y: r.y - CAP.y });

/**
 * S1's ROI rule, generalised. The "inner" band is the padding-wide strip of each
 * shape nearest the gap — exactly where a sibling's already-filtered pixels would
 * land — starting one padding in from the gap-facing edge and stopping 6px short
 * of it, vertically inset 6px. At sigma 20 / pad 60 this reproduces S1's
 * NA_inner and NB_inner rectangles exactly.
 *
 * `core` is the same band with the vertical inset raised to the corner radius, so
 * no pixel in it was ever clipped away by the rounded corners. The S1-rule band
 * dilutes its mean with those corner pixels (identical in both renderings); the
 * core band does not. Both are reported.
 */
function roisFor(cell) {
  const A = { x: 100, y: 300, w: 200, h: 120 };
  const B = { x: A.x + A.w + cell.gap, y: 300, w: 200, h: 120 };
  const R = 32;
  const pad = cell.pad;
  const band = (x0) => ({ x: x0, y: A.y + 6, w: pad - 6, h: A.h - 12 });
  const core = (x0) => ({ x: x0, y: A.y + R, w: pad - 6, h: A.h - 2 * R });
  return {
    A_inner: local(band(A.x + A.w - pad)),
    B_inner: local(band(B.x + 6)),
    A_inner_core: local(core(A.x + A.w - pad)),
    B_inner_core: local(core(B.x + 6)),
    A_all: local(A),
    B_all: local(B),
    // Controls. The gap strip and the region left of A are outside every clip, so
    // nothing paints there in any variant; a non-zero reading is a harness fault.
    GAP: cell.gap >= 4 ? local({ x: A.x + A.w, y: A.y, w: cell.gap, h: A.h }) : null,
    OUTSIDE: local({ x: 20, y: A.y, w: 60, h: A.h }),
  };
}

// -------------------------------------------------------------------- capture

function urlFor(port, q) {
  return `http://127.0.0.1:${port}/bench.html?${new URLSearchParams(q)}`;
}

const VARIANTS = [
  { id: 'single', q: { groups: 'single' } },
  { id: 'split-ab', q: { groups: 'split', order: 'ab' } },
  { id: 'split-ba', q: { groups: 'split', order: 'ba' } },
];

async function capture(browser, port, cell, variant, pass) {
  const dir = join(SHOTS, 'pass' + pass);
  mkdirSync(dir, { recursive: true });
  const out = join(dir, `${cell.label.replace(/\//g, '_')}__${variant.id}.png`);
  const ctx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.goto(urlFor(port, {
    sigma: cell.sigma, pad: cell.pad, gap: cell.gap, bg: cell.bg, ...variant.q,
  }), { waitUntil: 'load' });
  await page.waitForSelector('html[data-bench-ready="1"]');
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.waitForTimeout(220);
  await page.screenshot({ path: out, clip: CAP, animations: 'disabled' });
  await ctx.close();
  return out;
}

const sha = (p) => createHash('sha256').update(readFileSync(p)).digest('hex').slice(0, 16);

// ----------------------------------------------------------------------- main

const HEAT_FOR = new Set([
  's8/checker/0.25sigma', 's8/checker/1sigma', 's8/checker/2sigma', 's8/checker/3sigma',
  // The floor: at 6 sigma the boxes do not even touch, so whatever this shows is
  // what a split-vs-single comparison costs before any leak exists.
  's8/checker/6sigma',
  'demo-s14/checker/56px',
  'S1-repro/mixed/8px',
]);

async function main() {
  const { server, port } = await serve();
  const browser = await chromium.launch();
  const version = browser.version();
  console.log(`chromium ${version}`);
  mkdirSync(RESULTS, { recursive: true });

  const rows = [];
  for (const cell of cells()) {
    const shots = {};
    let deterministic = true;
    for (const v of VARIANTS) {
      const p1 = await capture(browser, port, cell, v, 1);
      const p2 = await capture(browser, port, cell, v, 2);
      if (sha(p1) !== sha(p2)) deterministic = false;
      shots[v.id] = p1;
    }
    const png = Object.fromEntries(Object.entries(shots).map(([k, p]) => [k, load(p)]));
    const rois = roisFor(cell);

    const compare = (a, b) => {
      const out = {};
      for (const [name, roi] of Object.entries(rois)) {
        if (roi) out[name] = diffROI(png[a], png[b], roi);
      }
      return out;
    };

    const row = {
      ...cell,
      deterministic,
      boxesOverlap: cell.gap < 2 * cell.pad,
      paintReachesNeighbour: cell.gap < cell.pad,
      'split-ab vs single': compare('single', 'split-ab'),
      'split-ba vs single': compare('single', 'split-ba'),
      'split-ab vs split-ba': compare('split-ab', 'split-ba'),
    };
    rows.push(row);

    if (HEAT_FOR.has(cell.label)) {
      mkdirSync(join(RESULTS, 'heat'), { recursive: true });
      heatmap(png.single, png['split-ab'],
        join(RESULTS, 'heat', `${cell.label.replace(/\//g, '_')}__single-vs-split-ab.png`));
    }

    const s = row['split-ab vs single'];
    console.log(
      `${cell.label.padEnd(24)} gap=${String(cell.gap).padStart(3)}px  ` +
      `A_inner ${String(s.A_inner.mean).padStart(6)}/${String(s.A_inner.max).padStart(3)}  ` +
      `B_inner ${String(s.B_inner.mean).padStart(6)}/${String(s.B_inner.max).padStart(3)}  ` +
      `${deterministic ? '' : '  NON-DETERMINISTIC'}`,
    );
  }

  await browser.close();
  server.close();
  writeFileSync(join(RESULTS, 'results.json'), JSON.stringify({ version, rows }, null, 2));
  console.log('\nwrote', join(RESULTS, 'results.json'));
}

main().catch((e) => { console.error(e); process.exit(1); });
