/**
 * Playwright driver for the WebGPU shader-cost benchmark.
 *
 * Serves bench/ over a throwaway localhost http server (more reliable for
 * WebGPU than file://), walks a launch fallback chain until one browser mode
 * actually exposes `navigator.gpu`, runs the benchmark defined in
 * bench/page.html, and prints the result as JSON on stdout. All progress goes
 * to stderr so stdout stays machine-readable.
 *
 * Usage:
 *   npm run bench                          # full run, writes bench/results.json
 *   npx tsx bench/run.ts --quick           # fast smoke run
 *   npx tsx bench/run.ts --out none        # stdout only
 *   npx tsx bench/run.ts --f32-check path.json
 *
 * f32 cross-check input schema (default bench/f32-check.json, optional):
 *   {
 *     "shapes":  [ { "half": [halfW, halfH], "re": number, "k": [k0,k1,k2,k3,k4] } ],
 *     "points":  [ { "shape": shapeIndex, "p": [x, y] } ],
 *     "expected": { "rsupn": [f64...], "roundbox": [f64...] }
 *   }
 * `points` may also be given as [[x, y, shapeIndex], ...] and `expected` as a
 * flat array (interpreted as rsupn). Points are in shape-local coordinates
 * (shape centred on the origin), matching src/candidates.ts `evalAt(p, x, y)`.
 */

import { chromium, type Browser, type LaunchOptions, type Page } from 'playwright';
import * as fs from 'node:fs';
import * as http from 'node:http';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const BENCH_DIR = path.dirname(fileURLToPath(import.meta.url));

const err = (...a: unknown[]) => process.stderr.write(a.map(String).join(' ') + '\n');

// ---------------------------------------------------------------------------
// args
// ---------------------------------------------------------------------------

interface Args {
  quick: boolean;
  allowFallback: boolean;
  reps: number;
  minMs: number;
  out: string;
  f32Check: string;
  ks: number[];
  resolutions: { label: string; width: number; height: number }[];
}

function parseArgs(argv: string[]): Args {
  const a: Args = {
    quick: false,
    allowFallback: false,
    reps: 15,
    minMs: 50,
    out: path.join(BENCH_DIR, 'results.json'),
    f32Check: path.join(BENCH_DIR, 'f32-check.json'),
    ks: [1, 2, 4, 8, 16, 32],
    resolutions: [
      { label: 'mobile-390x844@3', width: 1170, height: 2532 },
      { label: 'desktop-2880x1800', width: 2880, height: 1800 },
    ],
  };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const next = () => argv[++i];
    if (k === '--quick') a.quick = true;
    else if (k === '--allow-fallback-adapter') a.allowFallback = true;
    else if (k === '--reps') a.reps = Number(next());
    else if (k === '--min-ms') a.minMs = Number(next());
    else if (k === '--out') a.out = next();
    else if (k === '--f32-check') a.f32Check = next();
    else if (k === '--ks') a.ks = next().split(',').map(Number);
    else throw new Error(`unknown argument: ${k}`);
  }
  if (a.quick) {
    a.reps = Math.min(a.reps, 5);
    a.minMs = Math.min(a.minMs, 12);
    a.ks = [1, 4, 32];
    a.resolutions = a.resolutions.slice(0, 1);
  }
  return a;
}

// ---------------------------------------------------------------------------
// static server
// ---------------------------------------------------------------------------

const MIME: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.wgsl': 'text/plain; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
};

async function serve(dir: string): Promise<{ origin: string; close: () => Promise<void> }> {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent((req.url ?? '/').split('?')[0]).replace(/^\/+/, '') || 'page.html';
    const file = path.join(dir, rel);
    if (!file.startsWith(dir) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404).end('not found');
      return;
    }
    res.writeHead(200, { 'content-type': MIME[path.extname(file)] ?? 'application/octet-stream' });
    res.end(fs.readFileSync(file));
  });
  await new Promise<void>((ok) => server.listen(0, '127.0.0.1', ok));
  const addr = server.address();
  if (!addr || typeof addr === 'string') throw new Error('server address unavailable');
  return {
    origin: `http://127.0.0.1:${addr.port}`,
    close: () => new Promise<void>((ok) => server.close(() => ok())),
  };
}

// ---------------------------------------------------------------------------
// launch chain
// ---------------------------------------------------------------------------

const GPU_ARGS = [
  '--enable-unsafe-webgpu',
  '--enable-features=Vulkan,WebGPU',
  // Chrome quantizes timestamp-query results to 100us by default; without this
  // a short pass reads as 0. Harmless (and ignored) where unsupported.
  '--disable-dawn-features=timestamp_quantization',
];

interface Attempt { name: string; opts: LaunchOptions }

const ATTEMPTS: Attempt[] = [
  { name: 'a: playwright chromium, headless', opts: { headless: true, args: GPU_ARGS } },
  { name: 'a2: playwright chromium (full binary), headless', opts: { headless: true, channel: 'chromium', args: GPU_ARGS } },
  { name: 'b: playwright chromium, headed', opts: { headless: false, args: GPU_ARGS } },
  { name: 'c: google chrome, headed', opts: { headless: false, channel: 'chrome', args: GPU_ARGS } },
];

interface Probe { ok: boolean; why?: string; timestamp?: boolean; adapter?: unknown; fallback?: boolean }

/**
 * A launch mode counts as usable only if it hands back a HARDWARE adapter.
 * Headless Chrome happily serves SwiftShader (CPU) through the same API, which
 * would produce numbers that look like a benchmark and mean nothing.
 */
async function probeWebGPU(page: Page, allowFallback: boolean): Promise<Probe> {
  return await page.evaluate(async (allowFallback) => {
    // @webgpu/types is not a dependency of this spike; the probe only needs
    // these few members, so name them locally rather than pull in the package.
    type AdapterInfoish = { vendor?: string; architecture?: string; device?: string; description?: string; isFallbackAdapter?: boolean };
    type Adapterish = {
      isFallbackAdapter?: boolean;
      features: { has(f: string): boolean };
      info?: AdapterInfoish;
      requestAdapterInfo?: () => Promise<AdapterInfoish>;
    };
    const gpu = (navigator as unknown as { gpu?: { requestAdapter(o?: unknown): Promise<Adapterish | null> } }).gpu;
    if (!gpu) return { ok: false, why: 'navigator.gpu is undefined' };
    try {
      const ad = await gpu.requestAdapter({ powerPreference: 'high-performance' });
      if (!ad) return { ok: false, why: 'requestAdapter() returned null' };
      const info: AdapterInfoish = ad.info ?? (ad.requestAdapterInfo ? await ad.requestAdapterInfo() : {});
      const blob = `${info.vendor ?? ''} ${info.architecture ?? ''} ${info.description ?? ''}`;
      const fallback = !!(ad.isFallbackAdapter || info.isFallbackAdapter ||
        /swiftshader|software|llvmpipe|lavapipe|warp/i.test(blob));
      const adapter = { vendor: info.vendor, architecture: info.architecture, device: info.device, description: info.description };
      if (fallback && !allowFallback) {
        return { ok: false, fallback: true, adapter, why: `software/fallback adapter (${blob.trim() || 'unnamed'}) — not a GPU measurement` };
      }
      return { ok: true, timestamp: ad.features.has('timestamp-query'), adapter, fallback };
    } catch (e) {
      return { ok: false, why: String(e) };
    }
  }, allowFallback);
}

interface Session {
  browser: Browser;
  page: Page;
  attempt: string;
  browserVersion: string;
  probe: Probe;
  attempts: { name: string; ok: boolean; why?: string }[];
  pageErrors: string[];
}

async function openSession(origin: string, shaderSrc: string, allowFallback: boolean): Promise<Session> {
  const log: { name: string; ok: boolean; why?: string }[] = [];
  for (const att of ATTEMPTS) {
    let browser: Browser | undefined;
    try {
      err(`[launch] trying ${att.name}`);
      browser = await chromium.launch(att.opts);
      const page = await browser.newPage();
      const pageErrors: string[] = [];
      page.on('console', (m) => err(`[page:${m.type()}] ${m.text()}`));
      page.on('pageerror', (e) => { pageErrors.push(String(e)); err(`[page:error] ${e}`); });
      // Also hand the WGSL to the page directly so it works even off file://.
      await page.addInitScript(`window.__SHADER_SRC__ = ${JSON.stringify(shaderSrc)};`);
      await page.goto(`${origin}/page.html`, { waitUntil: 'load' });
      await page.waitForFunction('window.__pageReady === true', null, { timeout: 30_000 });
      const probe = await probeWebGPU(page, allowFallback);
      if (!probe.ok) {
        log.push({ name: att.name, ok: false, why: probe.why });
        err(`[launch] ${att.name}: unusable (${probe.why})`);
        await browser.close();
        continue;
      }
      log.push({ name: att.name, ok: true });
      err(`[launch] ${att.name}: WebGPU OK on ${JSON.stringify(probe.adapter)} (timestamp-query: ${probe.timestamp})`);
      return { browser, page, attempt: att.name, browserVersion: browser.version(), probe, attempts: log, pageErrors };
    } catch (e) {
      log.push({ name: att.name, ok: false, why: String(e) });
      err(`[launch] ${att.name}: failed (${e})`);
      if (browser) await browser.close().catch(() => {});
    }
  }
  const detail = log.map((l) => `  - ${l.name}: ${l.why}`).join('\n');
  throw new Error(
    `no launch mode exposed a hardware WebGPU adapter. Tried:\n${detail}\n` +
    `(pass --allow-fallback-adapter to measure a software adapter anyway — the numbers would be CPU, not GPU)`
  );
}

// ---------------------------------------------------------------------------
// in-page invocation
// ---------------------------------------------------------------------------

async function callInPage<T>(page: Page, fnName: string, arg: unknown, timeoutMs: number): Promise<T> {
  await page.evaluate(
    ({ fnName, arg }) => {
      const w = window as unknown as Record<string, unknown>;
      w.__result = null;
      const fn = w[fnName] as (a: unknown) => Promise<unknown>;
      fn(arg).then(
        (r) => { w.__result = { ok: true, value: r }; },
        (e: unknown) => {
          const err = e as Error;
          w.__result = { ok: false, error: String(err && err.message ? err.message : err), stack: err?.stack };
        }
      );
    },
    { fnName, arg }
  );
  await page.waitForFunction('window.__result !== null', null, { timeout: timeoutMs });
  const res = (await page.evaluate(() => (window as unknown as Record<string, unknown>).__result)) as
    { ok: true; value: T } | { ok: false; error: string; stack?: string };
  if (!res.ok) throw new Error(`in-page ${fnName}() failed: ${res.error}\n${res.stack ?? ''}`);
  return res.value;
}

// ---------------------------------------------------------------------------
// f32 accuracy cross-check
// ---------------------------------------------------------------------------

interface CheckFile {
  shapes: { half: [number, number]; re: number; k: number[] }[];
  points: ({ shape: number; p: [number, number] } | number[])[];
  expected: Record<string, number[]> | number[];
  note?: string;
}

function absStats(shader: number[], expected: number[], scale: number[]) {
  let maxAbs = 0, maxRel = 0, maxAt = -1, sum = 0;
  const abs: number[] = [];
  for (let i = 0; i < expected.length; i++) {
    const d = Math.abs(shader[i] - expected[i]);
    abs.push(d);
    sum += d;
    if (d > maxAbs) { maxAbs = d; maxAt = i; }
    const rel = scale[i] > 0 ? d / scale[i] : 0;
    if (rel > maxRel) maxRel = rel;
  }
  abs.sort((x, y) => x - y);
  const q = (p: number) => abs[Math.min(abs.length - 1, Math.max(0, Math.round(p * (abs.length - 1))))];
  return {
    n: expected.length,
    maxAbsDiff: maxAbs,
    maxAbsDiffAtIndex: maxAt,
    maxAbsDiffRelativeToRe: maxRel,
    p50AbsDiff: q(0.5),
    p99AbsDiff: q(0.99),
    meanAbsDiff: sum / expected.length,
  };
}

async function runF32Check(page: Page, file: string) {
  if (!fs.existsSync(file)) {
    const reason = `input file not found: ${file} (generate one with: npx tsx bench/make-f32-check.ts)`;
    err(`[f32-check] skipped — ${reason}`);
    return { ran: false, reason };
  }
  const data = JSON.parse(fs.readFileSync(file, 'utf8')) as CheckFile;

  // WGSL `Shape` is 48 bytes: centre.xy, half.xy, re, k0..k4, tail pad.
  const STRIDE = 12;
  const shapes = new Array<number>(data.shapes.length * STRIDE).fill(0);
  data.shapes.forEach((s, i) => {
    const o = i * STRIDE;
    shapes[o + 0] = 0;             // centre.x — points are shape-local
    shapes[o + 1] = 0;             // centre.y
    shapes[o + 2] = s.half[0];
    shapes[o + 3] = s.half[1];
    shapes[o + 4] = s.re;
    for (let j = 0; j < 5; j++) shapes[o + 5 + j] = s.k[j] ?? 0;
  });

  const points: number[] = [];
  const shapeOf: number[] = [];
  for (const pt of data.points) {
    const [x, y, si] = Array.isArray(pt) ? [pt[0], pt[1], pt[2] ?? 0] : [pt.p[0], pt.p[1], pt.shape];
    points.push(x, y, si, 0);
    shapeOf.push(si);
  }

  err(`[f32-check] ${data.points.length} points over ${data.shapes.length} shapes`);
  const out = await callInPage<{ n: number; rsupn: number[]; roundbox: number[] }>(
    page, 'runCheck', { shapes, points }, 300_000
  );

  const expected = Array.isArray(data.expected) ? { rsupn: data.expected } : data.expected;
  const scale = shapeOf.map((si) => data.shapes[si].re);
  const per: Record<string, unknown> = {};
  for (const [name, exp] of Object.entries(expected)) {
    const got = (out as unknown as Record<string, number[]>)[name];
    if (!got) { per[name] = { error: `shader produced no output named "${name}"` }; continue; }
    if (got.length !== exp.length) { per[name] = { error: `length mismatch: shader ${got.length} vs expected ${exp.length}` }; continue; }
    per[name] = absStats(got, exp, scale);
  }
  return {
    ran: true,
    inputFile: file,
    note: data.note,
    points: out.n,
    shapes: data.shapes.length,
    precision: 'shader f32 vs supplied f64 expected values',
    perCandidate: per,
  };
}

// ---------------------------------------------------------------------------
// human-readable summary (stderr; stdout stays pure JSON)
// ---------------------------------------------------------------------------

interface PerK { k: number; drawsPerPass: number; reps: number; timingMethod: string; msPerDraw: { median: number; p05: number; p95: number } }
interface Fit { slopeMsPerDrawPerEval: number; interceptMsPerDraw: number; r2: number; nsPerEvalPerPixel: number; netNsPerEvalPerPixel?: number; marginalShareAtMaxK: number; scalesWithK: boolean }
interface VariantRes { id: string; perK: PerK[]; fit: Fit }
interface ResBlock { label: string; width: number; height: number; pixels: number; variants?: VariantRes[]; skipped?: string }

function summarize(result: Record<string, unknown>) {
  const meta = result.meta as Record<string, unknown>;
  const launch = result.launch as Record<string, unknown>;
  const adapter = meta.adapter as Record<string, unknown>;
  err('');
  err('=========================================================================');
  err(`launch path     : ${launch.path}`);
  err(`browser         : Chromium ${launch.browserVersion}`);
  err(`adapter         : ${JSON.stringify(adapter)}`);
  err(`fallback adapter: ${meta.isFallbackAdapter}`);
  err(`timing          : ${(meta.timingMethods as string[]).join(', ')}  (timestamp-query available: ${meta.timestampQueryAvailable})`);
  err(`pass            : ${meta.pass}`);
  err('');
  for (const res of result.resolutions as ResBlock[]) {
    if (!res.variants) { err(`${res.label}: SKIPPED (${res.skipped})`); continue; }
    err(`--- ${res.label}  ${res.width}x${res.height} = ${res.pixels} px`);
    err('    variant     K  draws   ms/draw     p05         p95');
    for (const v of res.variants) {
      for (const r of v.perK) {
        err(`    ${v.id.padEnd(10)} ${String(r.k).padStart(2)}  ${String(r.drawsPerPass).padStart(5)}` +
            `   ${r.msPerDraw.median.toFixed(5).padStart(9)}   ${r.msPerDraw.p05.toFixed(5).padStart(9)}   ${r.msPerDraw.p95.toFixed(5).padStart(9)}`);
      }
      const f = v.fit;
      err(`      fit: slope=${f.slopeMsPerDrawPerEval.toPrecision(5)} ms/pass/eval  intercept=${f.interceptMsPerDraw.toPrecision(4)} ms` +
          `  r2=${f.r2.toFixed(5)}  scalesWithK=${f.scalesWithK}`);
      err(`           ns/eval/px = ${f.nsPerEvalPerPixel.toPrecision(4)} gross` +
          (f.netNsPerEvalPerPixel != null ? `, ${f.netNsPerEvalPerPixel.toPrecision(4)} net of the null loop` : ' (this IS the null loop)'));
      if (!f.scalesWithK && v.id !== 'null') {
        err(`      *** WARNING: ${v.id} did not scale with K. The compiler defeated the anti-hoisting; this slope is NOT a cost. ***`);
      }
    }
    err('');
  }
  const chk = result.f32Check as Record<string, unknown>;
  if (chk && chk.ran) {
    err(`f32 cross-check (${chk.points} points, ${chk.shapes} shapes) — shader f32 vs f64 reference:`);
    for (const [name, st] of Object.entries(chk.perCandidate as Record<string, Record<string, number>>)) {
      if (st.maxAbsDiff == null) { err(`    ${name}: ${JSON.stringify(st)}`); continue; }
      err(`    ${name.padEnd(9)} maxAbs=${st.maxAbsDiff.toExponential(3)} px  (${st.maxAbsDiffRelativeToRe.toExponential(3)} of the corner reach)` +
          `  p99=${st.p99AbsDiff.toExponential(3)}  mean=${st.meanAbsDiff.toExponential(3)}`);
    }
  } else if (chk) {
    err(`f32 cross-check: SKIPPED — ${chk.reason}`);
  }
  err('=========================================================================');
  err('');
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const shaderSrc = fs.readFileSync(path.join(BENCH_DIR, 'shaders.wgsl'), 'utf8');
  const server = await serve(BENCH_DIR);
  err(`[server] ${server.origin} serving ${BENCH_DIR}`);

  let session: Session | undefined;
  try {
    session = await openSession(server.origin, shaderSrc, args.allowFallback);
    const bench = await callInPage<Record<string, unknown>>(
      session.page,
      'runAll',
      { ks: args.ks, reps: args.reps, minMs: args.minMs, resolutions: args.resolutions },
      45 * 60_000
    );
    const f32Check = await runF32Check(session.page, args.f32Check);

    const result = {
      generatedAt: new Date().toISOString(),
      launch: {
        path: session.attempt,
        attempts: session.attempts,
        browserVersion: session.browserVersion,
        launchArgs: GPU_ARGS,
        adapterProbe: session.probe,
        allowFallbackAdapter: args.allowFallback,
        pageErrors: session.pageErrors,
      },
      ...bench,
      f32Check,
    };
    summarize(result);
    const json = JSON.stringify(result, null, 2);
    process.stdout.write(json + '\n');
    if (args.out && args.out !== 'none') {
      fs.writeFileSync(args.out, json + '\n');
      err(`[out] wrote ${args.out}`);
    }
  } finally {
    if (session) await session.browser.close().catch(() => {});
    await server.close();
  }
}

main().catch((e) => {
  err(`\nFATAL: ${e instanceof Error ? e.stack ?? e.message : String(e)}`);
  process.exitCode = 1;
});
