/**
 * W16 G0 (e) — the tier's per-surface frame cost.
 *
 * `--disable-gpu-vsync --disable-frame-rate-limit` uncap the compositor so that a
 * `requestAnimationFrame` interval is the frame's real cost rather than the
 * display's cadence; without them every configuration under the budget reads
 * 16.7 ms and the measurement says nothing. Everything else is `capture-web.ts`'s
 * launch recipe, `channel: "chromium"` included.
 */
import { createServer } from "node:http";
import { readFile, writeFile } from "node:fs/promises";
import { extname, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const HERE = dirname(fileURLToPath(import.meta.url));
const PAGES = join(HERE, "pages");
/*
 * Two launch recipes, and the difference is the whole measurement. With vsync
 * DISABLED a `requestAnimationFrame` interval measures the main thread's spin
 * rate and not the frame's cost — rasterisation is the compositor's and the main
 * thread is idle, so every configuration read 0.1–0.3 ms and said nothing (G0's
 * own first attempt; recorded in the findings). With vsync ON the interval is the
 * DISPLAY's cadence until the compositor cannot hold it, so the number that
 * carries information is the surface count at which the cadence breaks.
 */
const BASE_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];
const ARGS = process.argv.includes("--no-vsync")
  ? [...BASE_ARGS, "--disable-gpu-vsync", "--disable-frame-rate-limit"]
  : BASE_ARGS;
const MIME = { ".html": "text/html", ".json": "application/json", ".png": "image/png" };
const flag = (n, d) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1] : d; };

const server = createServer(async (req, res) => {
  try {
    const p = join(PAGES, decodeURIComponent((req.url ?? "/").split("?")[0]));
    const body = await readFile(p);
    res.writeHead(200, { "content-type": MIME[extname(p)] ?? "application/octet-stream" });
    res.end(body);
  } catch { if (!res.headersSent) res.writeHead(404); res.end("no"); }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({ channel: "chromium", args: ARGS });
process.stdout.write(`engine: chromium ${browser.version()}\n`);
const out = [];
const cases = JSON.parse(await readFile(flag("cases", join(HERE, "cost-cases.json")), "utf8"));

for (const c of cases) {
  const context = await browser.newContext({
    viewport: { width: c.viewport?.[0] ?? 1280, height: c.viewport?.[1] ?? 800 },
    deviceScaleFactor: c.dpr,
  });
  const page = await context.newPage();
  const url = c.url
    ? c.url
    : `${base}/cost.html?${new URLSearchParams({ form: c.form, n: String(c.n), w: String(c.w ?? 160), h: String(c.h ?? 96) })}`;
  await page.goto(url, { waitUntil: "load" });
  if (c.inject) await page.evaluate(c.inject);
  if (c.url) await page.evaluate(await readFile(join(HERE, "cost-probe.js"), "utf8"));
  await page.waitForSelector("html[data-done='1']", { timeout: 120000 });
  const cost = await page.evaluate(() => window.__cost);
  out.push({ ...c, ...cost, inject: c.inject ? "yes" : "no" });
  process.stdout.write(
    `${(c.label ?? c.form).padEnd(34)} dpr=${c.dpr} n=${cost.n ?? c.n}  median ${cost.medianMs.toFixed(3)} ms  p90 ${cost.p90Ms.toFixed(3)} ms\n`,
  );
  await context.close();
}
await browser.close();
server.close();
await writeFile(flag("out", "/tmp/w16-cost.json"), JSON.stringify(out, null, 1));
