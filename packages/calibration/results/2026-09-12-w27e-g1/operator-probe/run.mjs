/**
 * W27e G1 — the label operator probe's driver.
 *
 * A script rather than a Playwright `test`, for W27e G0's reason unchanged:
 * this reports WHAT HAPPENED in code values, and a pass/fail harness would
 * throw that away. The launch recipe is G0's, which is `capture-web.ts`'s
 * (`channel: "chromium"` plus Dawn's flags), because a composite measured on
 * Playwright's bundled headless shell is a composite of something nobody ships.
 * Readings come off a compositor SCREENSHOT, never a canvas readback.
 *
 * What it decides: whether vitrea's closed form for Apple's label operator is
 * the arithmetic Chromium performs, to the code value; and how far the two
 * surviving readings of `inputBackdropAware` are apart where they are apart.
 * The tolerance it publishes bounds the analytic operator against the browser's
 * composite of it. It is NOT a bound between vitrea and macOS — there is no
 * native label fixture and the no-text fixture rule means there cannot be one.
 *
 * Writes `results.json` and one PNG per case beside itself.
 */

import { mkdir, writeFile } from "node:fs/promises";
import { createServer as netServer } from "node:net";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

import { chromium } from "@playwright/test";
import { PNG } from "pngjs";
import { createServer } from "vite";

const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];

const HERE = fileURLToPath(new URL(".", import.meta.url));
const CONFIG = resolve(HERE, "vite.config.mjs");
const PORT = 5232;
const VIEWPORT = { width: 1120, height: 1000 };

const say = (line) => void process.stdout.write(`${line}\n`);

/** Refuse to start on a port somebody else already holds. */
async function portFree(port) {
  return await new Promise((done) => {
    const probe = netServer();
    probe.once("error", () => done(false));
    probe.once("listening", () => probe.close(() => done(true)));
    probe.listen(port, "127.0.0.1");
  });
}

/** Mean, per-channel standard deviation, min and max over a screenshot region. */
function readRegion(png, region) {
  const sums = [0, 0, 0];
  const squares = [0, 0, 0];
  const min = [255, 255, 255];
  const max = [0, 0, 0];
  let count = 0;
  for (let y = region.y; y < region.y + region.height; y += 1) {
    for (let x = region.x; x < region.x + region.width; x += 1) {
      const index = (png.width * y + x) << 2;
      for (let c = 0; c < 3; c += 1) {
        const value = png.data[index + c];
        sums[c] += value;
        squares[c] += value * value;
        if (value < min[c]) min[c] = value;
        if (value > max[c]) max[c] = value;
      }
      count += 1;
    }
  }
  const mean = sums.map((s) => s / count);
  const sd = squares.map((s, c) => Math.sqrt(Math.max(0, s / count - mean[c] * mean[c])));
  return {
    mean: mean.map((v) => Math.round(v * 100) / 100),
    sd: sd.map((v) => Math.round(v * 100) / 100),
    min,
    max,
    sdMax: Math.round(Math.max(...sd) * 100) / 100,
  };
}

async function capture(page, name, outDir) {
  const buffer = await page.screenshot({ clip: { x: 0, y: 0, ...VIEWPORT } });
  await writeFile(resolve(outDir, `${name}.png`), buffer);
  return PNG.sync.read(buffer);
}

async function readCase(page, name, outDir) {
  const png = await capture(page, name, outDir);
  const regions = await page.evaluate(() => window.probe.regions());
  const readings = {};
  for (const region of regions) readings[region.id] = { ...region, ...readRegion(png, region) };
  return readings;
}

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const hex = (value) => {
  const n = value.replace("#", "");
  return [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16) / 255);
};

/**
 * The operator's closed form and the two composites, recorded into
 * `results.json` beside every cell so the reading carries its own model.
 *
 * This is NOT the independent check on Apple's matrix, and does not claim to
 * be: it consumes `reading.filtered`, which `probe.js` evaluated inside the
 * browser under test, so the matrix arithmetic it rests on is the engine's own.
 * `verdict.py` re-derives the filtered ink from `results.json`'s `matrices`
 * outside this process, scores against that, and publishes the disagreement
 * between the two derivations. It also scores each arm against the ink that arm
 * actually paints, which the model here does not: `blendonly` carries no
 * `filter`, and its cells here are built from a colour those cells never show.
 */
function expectations(reading) {
  const ink = [...hex(reading.inkColor), reading.inkAlpha];
  const ground = hex(reading.ground);
  const filtered = reading.filtered;
  const a = filtered[3];
  const sourceOver = [0, 1, 2].map((i) => a * filtered[i] + (1 - a) * ground[i]);
  // The alternative reading's blends, on the opaque grounds this bench paints
  // (αb = 1 throughout). `plus-lighter` is the CSS Compositing 2 form,
  // Co = αs·Cs + αb·Cb clamped to 1. `plus-darker` is NOT taken from that spec:
  // its §9.1.14 text is the broken Apple-derived one (w3c/fxtf-drafts#447), and
  // Apple's own two published formulas disagree with each other. The form below
  // is the one measured against Safari in that issue and endorsed by the CSSWG
  // for the spec — co = min(1, αs + αb) − min(1, αs(1 − Cs) + αb(1 − Cb)) —
  // evaluated at αb = 1, where it reduces to the expression written here.
  const plusLighter = [0, 1, 2].map((i) => clamp01(a * filtered[i] + ground[i]));
  const plusDarker = [0, 1, 2].map((i) => clamp01(1 - (a * (1 - filtered[i]) + (1 - ground[i]))));
  return {
    sourceOver: sourceOver.map((v) => Math.round(v * 255 * 100) / 100),
    plusLighter: plusLighter.map((v) => Math.round(v * 255 * 100) / 100),
    plusDarker: plusDarker.map((v) => Math.round(v * 255 * 100) / 100),
  };
}

const main = async () => {
  if (!(await portFree(PORT))) throw new Error(`port ${PORT} is taken — pick another`);

  const outDir = HERE;
  await mkdir(outDir, { recursive: true });

  const server = await createServer({ configFile: CONFIG });
  await server.listen(PORT);
  const url = `http://localhost:${PORT}/index.html`;
  say(`probe server on ${url}`);

  const browser = await chromium.launch({ channel: "chromium", args: GPU_ARGS });
  const context = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: 1,
    colorScheme: "light",
    reducedMotion: "no-preference",
  });
  const page = await context.newPage();
  page.on("console", (message) => {
    if (message.type() === "error") say(`  [page error] ${message.text()}`);
  });
  page.on("pageerror", (error) => say(`  [page throw] ${error.message}`));

  const results = {
    generatedAt: new Date().toISOString(),
    engine: `chromium/${browser.version()}`,
    viewport: VIEWPORT,
    deviceScaleFactor: 1,
    declaredTolerance: {
      unit: "code values of 255, per channel",
      bound: 1,
      bounds: "the analytic operator against the browser's composite of it",
      doesNotBound: "vitrea against macOS — there is no native label fixture",
      declaredIn: "packages/calibration/results/2026-09-12-w27e-g1/declaration.md §3",
    },
    cases: {},
  };

  const fresh = async () => {
    await page.goto(url, { waitUntil: "load" });
    await page.waitForSelector("[data-probe-ready]");
  };

  // -- The bench: the operator's arithmetic, with no glass anywhere near it. --
  await fresh();
  await page.evaluate(() => window.probe.showBench());
  results.matrices = await page.evaluate(() => window.probe.LABEL_MATRICES);
  results.grounds = await page.evaluate(() => window.probe.GROUNDS);
  results.inks = await page.evaluate(() => window.probe.INKS);
  results.adapter = await page.evaluate(() => window.h.adapter());
  results.blendSupport = await page.evaluate(() => window.probe.blendSupport());
  say(`blend support: ${JSON.stringify(results.blendSupport)}`);
  say(`adapter: ${JSON.stringify(results.adapter)}`);
  const bench = await readCase(page, "bench", outDir);
  for (const reading of Object.values(bench)) {
    if (reading.kind !== "bench") continue;
    reading.expected = expectations(reading);
  }
  results.cases["bench"] = { readings: bench };

  // -- The glass arm, per tier. The declared path and its CPU fold share a
  //    page because neither declares a blend; the alternative reading gets its
  //    own page, because §5.133 §5 measured that a blend inside the host
  //    collapses a DOM-proxied group's sampling and a shared capture would
  //    answer this gate's question with a picture of broken glass.
  const tiers = [
    { name: "css", renderer: "css", sampling: "dom" },
    { name: "gpu-dom", renderer: "webgpu", sampling: "dom" },
    { name: "gpu-texture", renderer: "webgpu", sampling: "texture" },
  ];

  for (const tier of tiers) {
    for (const scheme of ["light", "dark"]) {
      await fresh();
      const state = await page.evaluate(
        (spec) => window.probe.glass(spec),
        { renderer: tier.renderer, sampling: tier.sampling },
      );
      await page.evaluate((s) => window.probe.mountDeclared(s), scheme);
      await page.evaluate(() => window.probe.settle(8));
      const name = `${tier.name}--${scheme}--declared`;
      results.cases[name] = { tier: tier.name, scheme, state, readings: await readCase(page, name, outDir) };
      say(`${name}: ${JSON.stringify(state)}`);

      await fresh();
      await page.evaluate(
        (spec) => window.probe.glass(spec),
        { renderer: tier.renderer, sampling: tier.sampling },
      );
      await page.evaluate((s) => window.probe.mountPlusBlend(s), scheme);
      await page.evaluate(() => window.probe.settle(8));
      const alt = `${tier.name}--${scheme}--plusblend`;
      results.cases[alt] = {
        tier: tier.name,
        scheme,
        state: await page.evaluate(() => window.probe.state()),
        readings: await readCase(page, alt, outDir),
      };
    }
  }

  await browser.close();
  await server.close();

  await writeFile(resolve(outDir, "results.json"), `${JSON.stringify(results, null, 2)}\n`);
  say(`wrote ${resolve(outDir, "results.json")}`);
};

await main();
