/**
 * W27e G0 — the foreground composite probe's driver.
 *
 * A script rather than a Playwright `test`, for the same reason
 * `scripts/capture-web.ts` is one: this reports WHAT HAPPENED — which buffer
 * Chromium blended against, in code values — and a pass/fail harness would
 * throw that away.
 *
 * The launch recipe is `capture-web.ts`'s unchanged (`channel: "chromium"` plus
 * Dawn's flags), because the WebGPU tier on Playwright's bundled headless shell
 * is a CPU rasteriser and a composite measured there is a composite of
 * something nobody ships. Readings come off a compositor SCREENSHOT, never a
 * canvas readback: `mix-blend-mode` happens in the compositor, and a WebGPU
 * canvas is unreadable after present anyway (K2).
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
const PORT = 5231;
const VIEWPORT = { width: 1000, height: 760 };

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

/** Mean and per-channel standard deviation over a region of the screenshot. */
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
    // One number for "is the checkerboard still sharp in this buffer".
    sdMax: Math.round(Math.max(...sd) * 100) / 100,
  };
}

async function capture(page, name, outDir) {
  const buffer = await page.screenshot({ clip: { x: 0, y: 0, ...VIEWPORT } });
  await writeFile(resolve(outDir, `${name}.png`), buffer);
  return PNG.sync.read(buffer);
}

async function readCase(page, name, outDir, wantBench) {
  const png = await capture(page, name, outDir);
  const regions = await page.evaluate(() => window.probe.regions());
  const readings = {};
  for (const region of regions) {
    if (!wantBench && region.variant !== undefined) continue;
    readings[region.id] = { ...region, ...readRegion(png, region) };
  }
  return readings;
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
    cases: {},
  };

  const fresh = async () => {
    await page.goto(url, { waitUntil: "load" });
    await page.waitForSelector("[data-probe-ready]");
  };

  // -- Q2 first: the flat feColorMatrix bench needs no glass at all. ---------
  await fresh();
  results.matrices = await page.evaluate(() => window.probe.matrices);
  results.operators = await page.evaluate(() => window.probe.operators);
  results.cases["bench"] = { readings: await readCase(page, "bench", outDir, true) };
  results.adapter = await page.evaluate(() => window.h.adapter());
  say(`adapter: ${JSON.stringify(results.adapter)}`);

  // -- Q1: which buffer does a blended patch see, per tier. -----------------
  const tiers = [
    { name: "css", renderer: "css", sampling: "dom" },
    { name: "gpu-dom", renderer: "webgpu", sampling: "dom" },
    { name: "gpu-texture", renderer: "webgpu", sampling: "texture" },
  ];

  /**
   * One mount point per page load. Mixing them was the first run's mistake: a
   * blending element inside the glass root collapses the material for every
   * group in it, so a shared capture answers the blending question with a
   * picture of broken glass.
   */
  const mounts = [
    { mount: "host", over: "glass" },
    { mount: "host-layer", over: "glass" },
    { mount: "plane-root", over: "page" },
    { mount: "glass-root", over: "page" },
    { mount: "body", over: "page" },
  ];

  const buildGlass = async (tier) =>
    await page.evaluate(
      (spec) => window.probe.glass(spec),
      { renderer: tier.renderer, sampling: tier.sampling },
    );

  for (const tier of tiers) {
    await fresh();
    const state = await buildGlass(tier);
    say(`${tier.name}: ${JSON.stringify(state)}`);
    results.cases[`${tier.name}--baseline`] = {
      state,
      readings: await readCase(page, `${tier.name}--baseline`, outDir, false),
    };

    for (const spot of mounts) {
      await fresh();
      await buildGlass(tier);
      await page.evaluate(
        (spec) => window.probe.mountPair(spec.mount, spec.over),
        spot,
      );
      const name = `${tier.name}--pair-${spot.mount}`;
      results.cases[name] = {
        mount: spot,
        state: await page.evaluate(() => window.probe.state()),
        readings: await readCase(page, name, outDir, false),
      };
    }

    await fresh();
    await buildGlass(tier);
    await page.evaluate(() => window.probe.addLabels());
    results.cases[`${tier.name}--labels`] = {
      state: await page.evaluate(() => window.probe.state()),
      readings: await readCase(page, `${tier.name}--labels`, outDir, false),
    };

    /*
     * One declaration at a time on a label inside the host. `filter` and
     * `mix-blend-mode` have different reach and the combined capture cannot say
     * which one moved the material, so each gets its own page — and `plain` is
     * the control that proves an extra element is not itself the cause.
     */
    const solos = [
      { id: "solo-plain", color: "#ffffff" },
      { id: "solo-filter", color: "#000000", filter: "url(#vib-default)" },
      { id: "solo-blend", color: "#ffffff", blend: "multiply" },
      {
        id: "solo-bg-blend",
        backgrounds: ["#000000", "#cfd8e0"],
        backgroundBlend: "multiply",
      },
      {
        id: "solo-filter-blend",
        color: "#000000",
        filter: "url(#vib-default)",
        blend: "multiply",
      },
    ];
    for (const spec of solos) {
      await fresh();
      await buildGlass(tier);
      await page.evaluate((s) => window.probe.mountSolo(s), spec);
      const name = `${tier.name}--${spec.id}`;
      results.cases[name] = {
        spec,
        state: await page.evaluate(() => window.probe.state()),
        readings: await readCase(page, name, outDir, false),
      };
    }

    /*
     * The two escape hatches worth ruling in or out: a boundary on the host
     * that is NOT itself a backdrop-root trigger. If one of them confines the
     * isolation a blending label forces, a group whose proxy sits outside the
     * host would survive it — which would be the difference between "the tier
     * may blend" and "the tier may not".
     */
    for (const boundary of ["isolation", "contain"]) {
      await fresh();
      await buildGlass(tier);
      await page.evaluate(
        (property) =>
          window.probe.setStyle("host", property, property === "isolation" ? "isolate" : "paint"),
        boundary,
      );
      await page.evaluate(
        (s) => window.probe.mountSolo(s),
        { id: "solo-blend", color: "#ffffff", blend: "multiply" },
      );
      const name = `${tier.name}--${boundary}-host-blend`;
      results.cases[name] = {
        state: await page.evaluate(() => window.probe.state()),
        readings: await readCase(page, name, outDir, false),
      };
    }

    // Reversibility: the same page, blend on then off. A material that comes
    // back is a causal claim; one that does not would mean the collapse was
    // something else that happened to coincide.
    await fresh();
    await buildGlass(tier);
    await page.evaluate(
      (s) => window.probe.mountSolo(s),
      { id: "solo-blend", color: "#ffffff", blend: "multiply" },
    );
    const during = await readCase(page, `${tier.name}--reversible-on`, outDir, false);
    await page.evaluate(() => window.probe.unmount("solo-blend"));
    results.cases[`${tier.name}--reversible`] = {
      during: during["bare-material"],
      readings: await readCase(page, `${tier.name}--reversible-off`, outDir, false),
    };
  }

  // -- Q3: what re-roots the backdrop and kills the group's sampling. -------
  const triggers = [
    { target: "host", property: "mix-blend-mode", value: "multiply" },
    { target: "host", property: "opacity", value: "0.99" },
    { target: "host", property: "filter", value: "blur(0px)" },
    { target: "host", property: "isolation", value: "isolate" },
    { target: "host", property: "contain", value: "paint" },
    { target: "glass-root", property: "opacity", value: "0.99" },
    { target: "glass-root", property: "filter", value: "blur(0px)" },
    { target: "glass-root", property: "mix-blend-mode", value: "multiply" },
    { target: "body", property: "opacity", value: "0.99" },
    { target: "body", property: "filter", value: "blur(0px)" },
  ];

  for (const trigger of triggers) {
    await fresh();
    await page.evaluate(() => window.probe.glass({ renderer: "css", sampling: "dom" }));
    const applied = await page.evaluate(
      async (spec) => await window.probe.setStyle(spec.target, spec.property, spec.value),
      trigger,
    );
    const name = `q3--${trigger.target}--${trigger.property}`;
    results.cases[name] = {
      trigger: { ...trigger, computed: applied },
      state: await page.evaluate(() => window.probe.state()),
      readings: await readCase(page, name, outDir, false),
    };
  }

  await browser.close();
  await server.close();

  await writeFile(resolve(outDir, "results.json"), `${JSON.stringify(results, null, 2)}\n`);
  say(`wrote ${resolve(outDir, "results.json")}`);
};

await main();
