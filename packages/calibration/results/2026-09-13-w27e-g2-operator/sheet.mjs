/**
 * The W27e G2 landing sheet: the playground's tint-and-ink band and one demo
 * surface, over both grounds, on a measured hardware adapter.
 *
 * Run once per side against two checkouts of the same repository, so the
 * before/after pair differs by the operator and by nothing else:
 *
 *   node sheet.mjs --root <repo> --label before --port 5311 --out <dir>
 *   node sheet.mjs --root <repo> --label after  --port 5312 --out <dir>
 *
 * It starts the demo's own dev server in `<root>/apps/demo`, which is what the
 * demo's Playwright config does, and launches the full Chromium binary with
 * Dawn's flags — the headless shell hands back SwiftShader and would sheet the
 * CSS tier while claiming the GPU one. The adapter it actually got, and whether
 * it was a fallback, are written into `readings-<label>.json` beside the PNGs,
 * because a sheet that does not name its adapter is not evidence.
 *
 * The contrast numbers it records are the demo harness's method, inlined: the
 * ink is read back through a canvas over black and over white so a translucent
 * or function-serialised colour recovers exactly, the surface is the median
 * luminance of the element's own pixels, and the ink is composited over that
 * surface before the ratio is taken. Inlined rather than imported because this
 * script runs outside the demo's Playwright project and against a checkout that
 * may not have the harness at all — the `before` side does not.
 */

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";

import { chromium } from "@playwright/test";
import { PNG } from "pngjs";

const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
  args.set(process.argv[i].replace(/^--/, ""), process.argv[i + 1]);
}
const ROOT = args.get("root");
const LABEL = args.get("label");
const PORT = Number(args.get("port") ?? 5311);
const OUT = args.get("out");
if (!ROOT || !LABEL || !OUT) throw new Error("usage: --root <repo> --label <name> --out <dir>");

const SHOTS = join(OUT, "sheets");
mkdirSync(SHOTS, { recursive: true });

const BASE = `http://localhost:${String(PORT)}`;

const server = spawn("npx", ["vite", "--port", String(PORT), "--strictPort"], {
  cwd: join(ROOT, "apps", "demo"),
  stdio: ["ignore", "pipe", "pipe"],
});
server.stdout.on("data", () => {});
server.stderr.on("data", (chunk) => process.stderr.write(`[vite] ${String(chunk)}`));

async function waitForServer() {
  for (let attempt = 0; attempt < 120; attempt += 1) {
    try {
      const response = await fetch(`${BASE}/`);
      if (response.ok) return;
    } catch {
      /* not up yet */
    }
    await sleep(500);
  }
  throw new Error("the demo's dev server never came up");
}

/* --------------------------------------------------------------- the harness */

/**
 * Every matching element's ink and box, read inside the page.
 *
 * The colour is recovered by painting it over an opaque black and an opaque
 * white and solving the pair, which is what the demo's own harness does: a
 * colour authored in OKLCH or produced by `color-mix()` serialises as a function
 * call, and no arithmetic over that string is a luminance. It also recovers the
 * **alpha**, which is not optional here — the ink is translucent on the `after`
 * side and reading three channels would score pure black against the surface.
 */
const inksIn = (selector) =>
  [...document.querySelectorAll(selector)].map((element) => {
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const ctx = canvas.getContext("2d");
    const read = (colour, ground) => {
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = ground;
      ctx.fillRect(0, 0, 1, 1);
      ctx.fillStyle = colour;
      ctx.fillRect(0, 0, 1, 1);
      const d = ctx.getImageData(0, 0, 1, 1).data;
      return [d[0], d[1], d[2]];
    };
    const colour = getComputedStyle(element).color;
    const onBlack = read(colour, "#000");
    const onWhite = read(colour, "#fff");
    const alpha = Math.max(0, Math.min(1, 1 - (onWhite[1] - onBlack[1]) / 255));
    const rgb = alpha === 0 ? [0, 0, 0] : [0, 1, 2].map((c) => onBlack[c] / alpha);
    const box = element.getBoundingClientRect();
    return {
      text: (element.textContent ?? "").trim(),
      colour,
      alpha,
      rgb,
      box: { x: box.x, y: box.y, width: box.width, height: box.height },
    };
  });

/** The median-luminance pixel of one element's own render, as a colour. */
async function surfaceOf(page, box) {
  if (box.width < 1 || box.height < 1) return [0, 0, 0];
  const shot = await page.screenshot({
    clip: { x: box.x, y: box.y, width: box.width, height: box.height },
  });
  const png = PNG.sync.read(shot);
  const pixels = [];
  const channel = (v) => {
    const x = v / 255;
    return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
  };
  const lum = (r, g, b) => 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
  for (let i = 0; i < png.data.length; i += 4) {
    if (png.data[i + 3] < 200) continue;
    const rgb = [png.data[i], png.data[i + 1], png.data[i + 2]];
    pixels.push({ rgb, y: lum(rgb[0], rgb[1], rgb[2]) });
  }
  pixels.sort((a, b) => a.y - b.y);
  return pixels[Math.floor(pixels.length / 2)]?.rgb ?? [0, 0, 0];
}

function ratioOf(ink, surface) {
  const channel = (v) => {
    const x = v / 255;
    return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
  };
  const lum = (rgb) => 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2]);
  const composited = [0, 1, 2].map((c) => ink.alpha * ink.rgb[c] + (1 - ink.alpha) * surface[c]);
  const a = lum(composited);
  const b = lum(surface);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

async function readingsFor(page, selector) {
  const inks = await page.evaluate(inksIn, selector);
  const out = [];
  for (const ink of inks) {
    const surface = await surfaceOf(page, ink.box);
    out.push({
      text: ink.text,
      colour: ink.colour,
      alpha: Number(ink.alpha.toFixed(6)),
      surface,
      ratio: Number(ratioOf(ink, surface).toFixed(4)),
    });
  }
  return out;
}

/* ------------------------------------------------------------------- the run */

await waitForServer();

const browser = await chromium.launch({
  channel: "chromium",
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: 1,
  colorScheme: "light",
});
const page = await context.newPage();

const record = { label: LABEL, root: ROOT, takenAt: new Date().toISOString() };

record.reduceTransparency = process.env.W27E_REDUCE_TRANSPARENCY ?? "unrecorded";
record.increaseContrast = process.env.W27E_INCREASE_CONTRAST ?? "unrecorded";

await page.goto(`${BASE}/playground/`);
await page.waitForSelector("[data-vitrea-root]", { state: "attached" });

record.adapter = await page.evaluate(async () => {
  if (navigator.gpu === undefined) return { available: false };
  const adapter = await navigator.gpu.requestAdapter();
  if (adapter === null) return { available: false };
  return {
    available: true,
    isFallbackAdapter: adapter.isFallbackAdapter,
    info: {
      vendor: adapter.info?.vendor ?? null,
      architecture: adapter.info?.architecture ?? null,
      device: adapter.info?.device ?? null,
      description: adapter.info?.description ?? null,
    },
  };
});
record.userAgent = await page.evaluate(() => navigator.userAgent);

// The band's own readout, which names the tier that actually drew each ground.
await page.waitForFunction(() => {
  const nodes = [...document.querySelectorAll("[data-testid^='ink-tier-']")];
  return nodes.length > 0 && nodes.every((node) => (node.textContent ?? "").trim() !== "resolving");
});
// Two seconds of settle: the backdrop adaptation's own time constant is 500 ms
// and the ink's crossfade is 180, so a sheet taken sooner can catch a transit.
await sleep(2000);

record.tiers = await page.evaluate(() =>
  Object.fromEntries(
    [...document.querySelectorAll("[data-testid^='ink-tier-']")].map((node) => [
      node.getAttribute("data-testid"),
      (node.textContent ?? "").trim(),
    ]),
  ),
);

record.tokens = await page.evaluate(() =>
  Object.fromEntries(
    ["light", "dark"].map((ground) => {
      const host = document.querySelector(`[data-testid="ink-plate-${ground}"]`);
      const style = host === null ? null : host.style;
      return [
        ground,
        style === null
          ? null
          : {
              foreground: style.getPropertyValue("--vitrea-foreground"),
              secondary: style.getPropertyValue("--vitrea-foreground-secondary"),
              tertiary: style.getPropertyValue("--vitrea-foreground-tertiary"),
              quaternary: style.getPropertyValue("--vitrea-foreground-quaternary"),
              tint: style.getPropertyValue("--vitrea-tint"),
            },
      ];
    }),
  ),
);

/*
 * The fold reaching the pixel, checked rather than asserted.
 *
 * The operator is folded into the published token on both tiers and no per-pixel
 * filter is installed, so what a reader sees should be the token and nothing
 * else. Both sides are canonicalised through the same canvas read — over an
 * opaque black and an opaque white — so a token written as `rgb(r g b / a)` and a
 * computed `color` serialised as `rgba(r, g, b, a)` compare as numbers rather
 * than as strings, and the alpha is recovered rather than dropped.
 */
record.tokenVsRendered = await page.evaluate(() => {
  const canvas = document.createElement("canvas");
  canvas.width = 1;
  canvas.height = 1;
  const ctx = canvas.getContext("2d");
  const read = (colour, ground) => {
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = ground;
    ctx.fillRect(0, 0, 1, 1);
    ctx.fillStyle = colour;
    ctx.fillRect(0, 0, 1, 1);
    const d = ctx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2]];
  };
  const solve = (colour) => {
    const onBlack = read(colour, "#000");
    const onWhite = read(colour, "#fff");
    const alpha = Math.max(0, Math.min(1, 1 - (onWhite[1] - onBlack[1]) / 255));
    const rgb = alpha === 0 ? [0, 0, 0] : [0, 1, 2].map((c) => Math.round(onBlack[c] / alpha));
    return { rgb, alpha: Math.round(alpha * 1000) / 1000 };
  };
  return [...document.querySelectorAll(".ink-plate, .ink-row .control")].map((host) => {
    const token = host.style.getPropertyValue("--vitrea-foreground");
    const rendered = getComputedStyle(host).color;
    const a = solve(token);
    const b = solve(rendered);
    return {
      testId: host.getAttribute("data-testid"),
      token,
      rendered,
      agrees:
        a.alpha === b.alpha && a.rgb.every((channel, index) => channel === b.rgb[index]),
    };
  });
});

record.contrast = await bandReadings();

/*
 * The same band on the CSS tier, because X1 makes the two tiers two different
 * answers and the ink's floor is solved against whichever composite is drawing.
 * The renderer's composite and the tier's conversion of it differ by up to 0.08
 * of the foreground level, and the secondary alpha is solved against one of them
 * and then read on the other's pixels — so a reading taken on one tier says
 * nothing about the other. Two passes, one per tier, and each says which.
 */
async function bandReadings() {
  return {
    tiers: await page.evaluate(() =>
      Object.fromEntries(
        [...document.querySelectorAll("[data-testid^='ink-tier-']")].map((node) => [
          node.getAttribute("data-testid"),
          (node.textContent ?? "").trim(),
        ]),
      ),
    ),
    names: await readingsFor(page, ".ink-level__name"),
    levels: await levelsOnPlates(),
    controls: await readingsFor(page, ".ink-row .control"),
  };
}

/**
 * Each level's ratio against **the plate the specimen sits on**, per ground.
 *
 * `readingsFor` takes the surface from the selected element's own pixels, which
 * on a two-character specimen is the ink measuring itself: the box is mostly
 * glyph, the median lands inside the antialiasing, and the ratio comes out under
 * what a reader sees by a few hundredths. The plate is the surface the runtime
 * solved the alpha against and the surface an eye integrates, so the three
 * pieces are composed by hand here. The specimen-box readings stay beside these
 * under `names` and `controls`, where the element really is mostly material.
 */
async function levelsOnPlates() {
  const out = {};
  for (const ground of ["light", "dark"]) {
    const plate = `[data-testid="ink-plate-${ground}"]`;
    const box = await page.evaluate((selector) => {
      const node = document.querySelector(selector);
      if (node === null) return null;
      const rect = node.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    }, plate);
    if (box === null) continue;
    const surface = await surfaceOf(page, box);
    const levels = {};
    for (const level of ["primary", "secondary", "tertiary", "quaternary"]) {
      const inks = await page.evaluate(
        inksIn,
        `${plate} .ink-level--${level} .ink-level__specimen`,
      );
      levels[level] = inks.map((ink) => ({
        alpha: Number(ink.alpha.toFixed(6)),
        colour: ink.colour,
        ratio: Number(ratioOf(ink, surface).toFixed(4)),
      }));
    }
    out[ground] = { surface, levels };
  }
  return out;
}

/** The union box of the page band and the glass overlaying it, in page space. */
const bandBox = await page.evaluate(() => {
  const boxes = [".region--ink", ".ink-overlay"]
    .map((selector) => document.querySelector(selector))
    .filter((node) => node !== null)
    .map((node) => node.getBoundingClientRect());
  if (boxes.length === 0) return null;
  const left = Math.min(...boxes.map((box) => box.left));
  const top = Math.min(...boxes.map((box) => box.top));
  const right = Math.max(...boxes.map((box) => box.right));
  const bottom = Math.max(...boxes.map((box) => box.bottom));
  return { x: left - 8, y: top - 8, width: right - left + 16, height: bottom - top + 16 };
});

if (bandBox !== null) {
  await page.screenshot({ path: join(SHOTS, `band-${LABEL}.png`), clip: bandBox });
}

for (const ground of ["light", "dark"]) {
  const box = await page.evaluate((key) => {
    const row = document.querySelectorAll(".ink-row")[key === "light" ? 0 : 1];
    if (row === undefined) return null;
    const rect = row.getBoundingClientRect();
    return { x: rect.x - 6, y: rect.y - 6, width: rect.width + 12, height: rect.height + 12 };
  }, ground);
  if (box !== null) {
    await page.screenshot({ path: join(SHOTS, `band-${ground}-${LABEL}.png`), clip: box });
  }
}

/* The band again, on the CSS tier this time. */
await page.goto(`${BASE}/playground/?renderer=css`);
await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
await page.waitForFunction(() => {
  const nodes = [...document.querySelectorAll("[data-testid^='ink-tier-']")];
  return nodes.length > 0 && nodes.every((node) => (node.textContent ?? "").trim() !== "resolving");
});
await sleep(2000);
record.contrastCss = await bandReadings();
for (const ground of ["light", "dark"]) {
  const box = await page.evaluate((key) => {
    const row = document.querySelectorAll(".ink-row")[key === "light" ? 0 : 1];
    if (row === undefined) return null;
    const rect = row.getBoundingClientRect();
    return { x: rect.x - 6, y: rect.y - 6, width: rect.width + 12, height: rect.height + 12 };
  }, ground);
  if (box !== null) {
    await page.screenshot({ path: join(SHOTS, `band-css-${ground}-${LABEL}.png`), clip: box });
  }
}

/* One demo surface, on the site's own page, over its own moving backdrop. */
await page.goto(`${BASE}/`);
await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
await page.evaluate(() => {
  document.getElementById("behavior")?.scrollIntoView({ block: "center", behavior: "instant" });
});
await sleep(2500);
/*
 * The controls, not the section. The site's glass lives in the base plane's host
 * layer — a portal outside `#behavior`'s subtree — so a clip taken from the
 * section's own box catches the page's copy and none of the labels this gate
 * moved, and the two sides come out byte-identical for the wrong reason.
 */
const behaviour = await page.evaluate(() => {
  const boxes = [...document.querySelectorAll(".control")]
    .map((node) => node.getBoundingClientRect())
    .filter((rect) => rect.width > 0 && rect.height > 0 && rect.bottom > 0 && rect.top < 1000);
  if (boxes.length === 0) return null;
  const left = Math.max(0, Math.min(...boxes.map((box) => box.left)) - 16);
  const top = Math.max(0, Math.min(...boxes.map((box) => box.top)) - 16);
  const right = Math.min(1440, Math.max(...boxes.map((box) => box.right)) + 16);
  const bottom = Math.min(1000, Math.max(...boxes.map((box) => box.bottom)) + 16);
  return { x: left, y: top, width: right - left, height: bottom - top };
});
if (behaviour !== null) {
  await page.screenshot({ path: join(SHOTS, `demo-controls-${LABEL}.png`), clip: behaviour });
}
/*
 * `.control` and not `#behavior .control`: the site's glass lives in the base
 * plane's host layer, which is a portal outside the section's own subtree, so a
 * descendant selector finds nothing. `contrast.spec.ts` selects the same way and
 * for the same reason.
 */
record.demoContrast = await readingsFor(page, ".control");

writeFileSync(join(OUT, `readings-${LABEL}.json`), `${JSON.stringify(record, null, 2)}\n`);

await browser.close();
server.kill("SIGTERM");
console.log(`wrote ${join(OUT, `readings-${LABEL}.json`)}`);
