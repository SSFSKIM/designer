/**
 * W27f G2's eye sheet: photograph the shipped demo's `/#page` stage, both schemes.
 *
 * The rest of the sheet is made of images this gate already has — the native
 * fixtures and the calibration captures under the run's scratch root — so this
 * script only takes the one panel that needs a browser: the live site drawing
 * the page material over its own paragraph text, which is the thing the user is
 * being asked to look at.
 *
 * Three rules it refuses to run without.
 *
 * 1. **A measured hardware adapter.** `isFallbackAdapter` lives on
 *    `GPUAdapterInfo`, not on `GPUAdapter` (root spec Decision Log #36(b)), and
 *    reading it off the adapter yields `undefined` — which `?? false` then
 *    launders into a pass. The 0.16.0 sheet's harness does exactly that
 *    (`2026-09-10-w27-coverage-wave/eye/harness/capture.mjs`), so its recorded
 *    `isFallbackAdapter: false` is an unmeasured value; its vendor/architecture
 *    pair is what actually established hardware there. This reads the flag off
 *    the info object and keeps it tri-state: only a measured `false` passes,
 *    and `undefined` means unverified, which refuses.
 * 2. **The GPU tier.** The site's own readout must say `webgpu`, scraped from
 *    the shipped page rather than a test attribute. Photographing the CSS
 *    fallback and calling it the material is the failure this guards.
 * 3. **The scheme actually applied.** The site's colour scheme is a `<select>`
 *    whose initial state is hard-coded `light`; Playwright's `colorScheme`
 *    context option alone changes nothing. The select is driven, and
 *    `documentElement.dataset.colorScheme` is read back before the shot.
 *
 * Usage, with the demo's dev server already listening on PORT:
 *
 *     node capture-demo.mjs --base http://localhost:5233 --out <panels dir>
 */
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "@playwright/test";

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(name);
  if (i === -1) return fallback;
  const value = args[i + 1];
  if (value === undefined) throw new Error(`${name} needs a value`);
  return value;
};

const BASE = flag("--base", "http://localhost:5233");
const OUT = resolve(flag("--out", resolve(import.meta.dirname, "panels")));
const SCHEMES = ["light", "dark"];

/**
 * The adapter, read the way the repo's e2e harnesses read it.
 *
 * Returns `isFallbackAdapter: undefined` when the browser does not expose the
 * flag, which is a refusal and not a pass — an unverified adapter could be
 * SwiftShader, and SwiftShader would draw something that looks like a material.
 */
async function adapterInfo(page) {
  return page.evaluate(async () => {
    const gpu = navigator.gpu;
    if (gpu === undefined) return null;
    const adapter = await gpu.requestAdapter();
    if (adapter === null) return null;
    const info = adapter.info ?? (await adapter.requestAdapterInfo?.());
    const flagged = info?.isFallbackAdapter;
    return {
      vendor: info?.vendor ?? "",
      architecture: info?.architecture ?? "",
      device: info?.device ?? "",
      description: info?.description ?? "",
      isFallbackAdapter: typeof flagged === "boolean" ? flagged : null,
    };
  });
}

/** Every `dt`/`dd` pair of a section's readout, by its published label. */
async function readout(page, section) {
  return page.evaluate((id) => {
    const rows = [...document.querySelectorAll(`#${id} .readout__row`)];
    return Object.fromEntries(
      rows.map((row) => [
        row.querySelector("dt")?.textContent?.trim() ?? "",
        row.querySelector("dd")?.textContent?.trim() ?? "",
      ]),
    );
  }, section);
}

async function capture() {
  const browser = await chromium.launch({
    channel: "chromium",
    headless: false,
    args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
  });
  const meta = { capturedAt: new Date().toISOString(), chromium: browser.version(), base: BASE,
                 schemes: {} };
  try {
    for (const scheme of SCHEMES) {
      const context = await browser.newContext({
        deviceScaleFactor: 2,
        viewport: { width: 1440, height: 900 },
        colorScheme: scheme,
        reducedMotion: "no-preference",
      });
      const page = await context.newPage();
      const problems = [];
      page.on("console", (message) => {
        if (message.type() === "warning" || message.type() === "error") {
          problems.push(`${message.type()}: ${message.text()}`);
        }
      });
      page.on("pageerror", (error) => problems.push(`pageerror: ${error.message}`));

      await page.goto(`${BASE}/`, { waitUntil: "networkidle" });

      const adapter = await adapterInfo(page);
      if (adapter === null) throw new Error("no WebGPU adapter: refusing to photograph the CSS tier");
      if (adapter.isFallbackAdapter !== false) {
        throw new Error(
          `adapter ${adapter.vendor}/${adapter.architecture} is not measured hardware ` +
          `(isFallbackAdapter=${adapter.isFallbackAdapter}); refusing`,
        );
      }

      await page.getByTestId("color-scheme-select").selectOption(scheme);
      await page.waitForTimeout(900);
      const applied = await page.evaluate(() => document.documentElement.dataset.colorScheme);
      if (applied !== scheme) throw new Error(`asked for ${scheme}, the site applied ${applied}`);

      await page.evaluate(() =>
        document.getElementById("page")?.scrollIntoView({ block: "center", behavior: "instant" }));
      await page.locator("#page").waitFor({ state: "visible" });
      await page.waitForTimeout(2800);

      const rows = await readout(page, "page");
      if (rows["What is drawing"] !== "webgpu") {
        throw new Error(`/#page drew on ${rows["What is drawing"]}, not webgpu`);
      }

      const stage = page.locator(".stage").first();
      const box = await stage.boundingBox();
      if (box === null) throw new Error("the stage has no box");
      await mkdir(resolve(OUT, scheme), { recursive: true });
      await page.screenshot({
        path: resolve(OUT, scheme, "demo-page-stage.png"),
        clip: { x: Math.round(box.x), y: Math.round(box.y),
                width: Math.round(box.width), height: Math.round(box.height) },
        scale: "device",
        animations: "allow",
      });

      meta.schemes[scheme] = { adapter, readout: rows, stageBox: box, problems,
                              devicePixelRatio: 2 };
      await context.close();
      console.log(`${scheme}: ${JSON.stringify(rows)}`);
      if (problems.length > 0) console.log(`${scheme}: console said ${JSON.stringify(problems)}`);
    }
  } finally {
    await browser.close();
  }
  await writeFile(resolve(OUT, "demo-meta.json"), `${JSON.stringify(meta, null, 2)}\n`);
  console.log(`wrote ${resolve(OUT, "demo-meta.json")}`);
}

await capture();
