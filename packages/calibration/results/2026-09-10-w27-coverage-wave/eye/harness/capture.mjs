/**
 * The 0.16.0 eye sheet's capture pass.
 *
 * Real Chromium (`channel: "chromium"`), a real Metal adapter, device pixel
 * ratio 2, one colour scheme per run of the loop. Every panel is a `clip`
 * screenshot taken at `scale: "device"`, so a panel's pixels are the browser's
 * pixels and nothing resamples them.
 *
 * Two refusals rather than two warnings: the run aborts if `navigator.gpu`
 * hands back no adapter (or a fallback one), and it aborts if any group on a
 * page it is about to photograph did not resolve `activeRenderer: "webgpu"`. A
 * sheet of CSS-tier pictures labelled WebGPU would be worse than no sheet.
 *
 * Transition frames are *stepped*, not slept through. The harness mounts its
 * root with `autoStart={false}` and the script drives `root.runFrame` and the
 * bindings' ticker by hand through `window.__eye`, so the time printed under a
 * frame is that frame's own time at the shipped durations — nothing here
 * changes an easing or a duration.
 */

import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "@playwright/test";

const here = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(
  here,
  "../../packages/calibration/results/2026-09-10-w27-coverage-wave/eye/panels",
);
const BASE = "http://localhost:5189";

const meta = { capturedAt: new Date().toISOString(), schemes: {} };

async function shot(page, path, clip) {
  await mkdir(dirname(path), { recursive: true });
  await page.screenshot({
    path,
    clip: {
      x: Math.round(clip.x),
      y: Math.round(clip.y),
      width: Math.round(clip.width),
      height: Math.round(clip.height),
    },
    scale: "device",
    animations: "allow",
  });
}

async function adapterInfo(page) {
  return page.evaluate(async () => {
    if (navigator.gpu === undefined) return null;
    const adapter = await navigator.gpu.requestAdapter();
    if (adapter === null) return null;
    const info = adapter.info ?? (await adapter.requestAdapterInfo?.());
    return {
      vendor: info?.vendor ?? "",
      architecture: info?.architecture ?? "",
      device: info?.device ?? "",
      description: info?.description ?? "",
      isFallbackAdapter: adapter.isFallbackAdapter ?? false,
    };
  });
}

const settle = (page, frames = 90) => page.evaluate((n) => window.__eye.settle(n), frames);
const run = (page, ms) => page.evaluate((n) => window.__eye.run(n), ms);

async function hostReading(page, selector) {
  return page.evaluate((sel) => {
    const host = document.querySelector(sel);
    if (host === null) return null;
    const style = getComputedStyle(host);
    const raw = style.getPropertyValue("--vitrea-materialization").trim();
    return {
      materialization: raw === "" ? null : Number(Number(raw).toFixed(4)),
      opacity: style.opacity,
      lens: style.getPropertyValue("--vitrea-lens").trim() || null,
    };
  }, selector);
}

/**
 * A strip of frames across one transition, on the hand-driven clock.
 *
 * `times` are cumulative frame-milliseconds from the flip; the first is taken
 * before any frame runs, so it is the surface as the flip found it.
 */
async function strip(page, { flip, times, clip, out, name, hostSelector }) {
  await flip();
  const frames = [];
  let last = 0;
  for (const t of times) {
    if (t > last) await run(page, t - last);
    last = t;
    const reading = hostSelector === undefined ? null : await hostReading(page, hostSelector);
    const file = `${out}/${name}-${String(t).padStart(4, "0")}.png`;
    await shot(page, file, clip);
    frames.push({ t, file: file.slice(OUT.length + 1), ...(reading ?? {}) });
  }
  return frames;
}

async function captureHarness(context, scheme, out) {
  const page = await context.newPage();
  const warnings = [];
  page.on("console", (m) => {
    if (m.type() === "warning" || m.type() === "error") warnings.push(m.text().slice(0, 260));
  });
  page.on("pageerror", (e) => warnings.push(`pageerror: ${e.message}`));
  await page.goto(`${BASE}/eye/?scheme=${scheme}&stepped=1`, { waitUntil: "load" });

  const adapter = await adapterInfo(page);
  if (adapter === null) throw new Error("no WebGPU adapter: refusing to photograph the CSS tier");
  if (adapter.isFallbackAdapter === true) throw new Error("fallback (software) adapter: refusing");

  await page.waitForFunction(() => window.__eye !== undefined, undefined, { timeout: 20000 });
  await page.evaluate(() => window.__eye.ready());
  await settle(page, 180);
  await page.waitForTimeout(400);
  await settle(page, 90);

  const states = await page.evaluate(() =>
    [...document.querySelectorAll("[data-eye-state]")].map((n) => ({
      id: n.getAttribute("data-eye-state"),
      renderer: n.getAttribute("data-renderer"),
      backend: n.getAttribute("data-backend"),
      health: n.getAttribute("data-health"),
      demotion: n.getAttribute("data-demotion"),
    })),
  );
  const notGpu = states.filter((s) => s.renderer !== "webgpu");
  if (notGpu.length > 0) throw new Error(`not on the GPU tier: ${JSON.stringify(notGpu)}`);

  const clips = Object.fromEntries(
    await page.evaluate(() =>
      [...document.querySelectorAll("[data-eye-clip]")].map((n) => [
        n.getAttribute("data-eye-clip"),
        n.getBoundingClientRect().toJSON(),
      ]),
    ),
  );

  // 1 — the toolbar split, and the same items unsplit.
  await shot(page, `${out}/toolbar-split.png`, clips["toolbar-split"]);
  // 2 — tinted buttons, a tinted group, the four ink levels.
  await shot(page, `${out}/tint-ink.png`, clips["tint-ink"]);

  // 5 — the lens answering the pointer, on one capsule, on both backends.
  const lens = {};
  for (const [key, host, clip] of [
    ["dom", '[data-eye-host="lens"]', { x: 60, y: 1106, width: 300, height: 132 }],
    ["texture", '[data-eye-host="lens-texture"]', { x: 670, y: 1106, width: 300, height: 132 }],
  ]) {
    const box = await page.locator(host).boundingBox();
    lens[key] = {};
    await page.mouse.move(5, 1350);
    await settle(page, 60);
    lens[key].rest = await hostReading(page, host);
    await shot(page, `${out}/lens-${key}-rest.png`, clip);
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await settle(page, 60);
    lens[key].hover = await hostReading(page, host);
    await shot(page, `${out}/lens-${key}-hover.png`, clip);
    await page.mouse.down();
    await settle(page, 60);
    lens[key].press = await hostReading(page, host);
    await shot(page, `${out}/lens-${key}-press.png`, clip);
    await page.mouse.up();
    await page.mouse.move(5, 1350);
    await settle(page, 60);
  }

  // 4a — presence: `present={true}` → `false`, six frames across the channel.
  const presenceClip = { x: 60, y: 760, width: 360, height: 200 };
  const presenceRest = await hostReading(page, '[data-eye-host="presence"]');
  await shot(page, `${out}/presence-rest.png`, presenceClip);
  const presenceFrames = await strip(page, {
    flip: () => page.locator('[data-eye="presence-toggle"]').evaluate((n) => n.click()),
    times: [0, 40, 80, 120, 160, 240],
    clip: presenceClip,
    out,
    name: "presence-leave",
    hostSelector: '[data-eye-host="presence"]',
  });
  await settle(page, 60);
  const presenceIdentity = await hostReading(page, '[data-eye-host="presence"]');
  await shot(page, `${out}/presence-identity.png`, presenceClip);
  await page.locator('[data-eye="presence-toggle"]').evaluate((n) => n.click());
  await settle(page, 90);

  // 4b — the two morph transitions, opening, on the same clock.
  const morphTimes = [0, 60, 120, 180, 260, 420];
  const materialize = await strip(page, {
    flip: () => page.locator('[data-eye="materialize-toggle"]').evaluate((n) => n.click()),
    times: morphTimes,
    clip: { x: 440, y: 742, width: 340, height: 280 },
    out,
    name: "morph-materialize",
  });
  await settle(page, 90);
  await page.locator('[data-eye="materialize-toggle"]').evaluate((n) => n.click());
  await settle(page, 120);

  const matched = await strip(page, {
    flip: () => page.locator('[data-eye="matched-toggle"]').evaluate((n) => n.click()),
    times: morphTimes,
    clip: { x: 800, y: 742, width: 340, height: 280 },
    out,
    name: "morph-matched",
  });
  await settle(page, 90);

  await page.close();
  return {
    adapter,
    states,
    clips,
    lens,
    presence: { rest: presenceRest, identity: presenceIdentity, frames: presenceFrames },
    morph: { materialize, matched },
    warnings: [...new Set(warnings)].slice(0, 12),
  };
}

async function captureSite(context, scheme, out) {
  const page = await context.newPage();
  await page.goto(`${BASE}/`, { waitUntil: "load" });
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await page.getByTestId("color-scheme-select").selectOption(scheme);
  await page.waitForTimeout(900);

  const readouts = {};
  const stageBox = async () => {
    const b = await page.locator(".stage").first().boundingBox();
    return {
      x: Math.round(b.x),
      y: Math.round(b.y),
      width: Math.round(b.width),
      height: Math.round(b.height),
    };
  };

  for (const [section, file] of [
    ["page", "page-stage.png"],
    ["material", "texture-stage.png"],
  ]) {
    await page.evaluate((id) => {
      document.getElementById(id)?.scrollIntoView({ block: "center", behavior: "instant" });
    }, section);
    await page.waitForTimeout(2800);
    const rows = await page.evaluate((id) => {
      const found = {};
      for (const row of document.querySelectorAll(`#${id} .readout__row`)) {
        const dt = row.querySelector("dt")?.textContent?.trim();
        const dd = row.querySelector("dd")?.textContent?.trim();
        if (dt !== undefined) found[dt] = dd;
      }
      return found;
    }, section);
    readouts[section] = rows;
    if (rows["What is drawing"] !== "webgpu") {
      throw new Error(`site #${section} drew on ${rows["What is drawing"]}, not webgpu`);
    }
    readouts[`${section}Box`] = await stageBox();
    await shot(page, `${out}/${file}`, readouts[`${section}Box`]);
  }

  await page.close();
  return { readouts };
}

async function capturePlayground(context, out) {
  const page = await context.newPage();
  await page.goto(`${BASE}/playground/`, { waitUntil: "load" });
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await page.waitForTimeout(2800);

  const renderers = await page.evaluate(() =>
    [...document.querySelectorAll(".state-table")].map((table) => {
      const caption = table.querySelector("caption")?.textContent?.trim();
      const row = [...table.querySelectorAll("tr")].find(
        (r) => r.querySelector("th")?.textContent?.trim() === "activeRenderer",
      );
      return [caption ?? null, row?.querySelector("td")?.textContent?.trim() ?? null];
    }),
  );
  // The accessibility table is a `state-table` too and has no renderer row; the
  // groups are the tables that answer the question.
  const css = renderers.filter(([, r]) => r !== null && r !== "webgpu");
  if (renderers.every(([, r]) => r === null)) throw new Error("no group readout on the playground");
  if (css.length > 0) throw new Error(`playground not on the GPU tier: ${JSON.stringify(css)}`);

  const bar = await page.locator(".toolbar").first().boundingBox();
  const barClip = {
    x: Math.max(0, Math.round(bar.x) - 24),
    y: Math.max(0, Math.round(bar.y) - 24),
    width: Math.round(bar.width) + 48,
    height: Math.round(bar.height) + 48,
  };
  await shot(page, `${out}/live-toolbar-split.png`, barClip);

  const plate = await page.locator('[data-testid="dom-plate"]').boundingBox();
  const plateClip = {
    x: Math.max(0, Math.round(plate.x) - 32),
    y: Math.max(0, Math.round(plate.y) - 32),
    width: Math.round(plate.width) + 64,
    height: Math.round(plate.height) + 64,
  };
  await shot(page, `${out}/live-presence-on.png`, plateClip);
  const before = await hostReading(page, '[data-testid="dom-plate"]');
  await page.locator('[data-testid="presence-toggle"]').click();
  await page.waitForTimeout(1000);
  const after = await hostReading(page, '[data-testid="dom-plate"]');
  await shot(page, `${out}/live-presence-identity.png`, plateClip);
  await page.locator('[data-testid="presence-toggle"]').click();

  await page.close();
  return { renderers, presence: { before, after }, barClip, plateClip };
}

const browser = await chromium.launch({
  channel: "chromium",
  headless: false,
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
});
meta.chromium = browser.version();

for (const scheme of ["light", "dark"]) {
  const context = await browser.newContext({
    deviceScaleFactor: 2,
    viewport: { width: 1280, height: 1360 },
    colorScheme: scheme,
    reducedMotion: "no-preference",
  });
  const out = `${OUT}/${scheme}`;
  const harness = await captureHarness(context, scheme, out);
  await context.close();

  const siteContext = await browser.newContext({
    deviceScaleFactor: 2,
    viewport: { width: 1440, height: 900 },
    colorScheme: scheme,
    reducedMotion: "no-preference",
  });
  const site = await captureSite(siteContext, scheme, out);
  const playground = scheme === "light" ? await capturePlayground(siteContext, out) : null;
  await siteContext.close();

  meta.schemes[scheme] = { harness, site, playground };
  console.log(`— ${scheme}: done`);
}

await browser.close();
await mkdir(OUT, { recursive: true });
await writeFile(`${OUT}/meta.json`, `${JSON.stringify(meta, null, 2)}\n`);
console.log("meta written");
