/**
 * W16 G0's capture driver — `capture-web.ts`'s launch recipe, pointed at G0's own
 * probe pages instead of the calibration scene app.
 *
 *   node capture.mjs --jobs jobs.json --out <dir>
 *
 * `channel: "chromium"` is the full browser binary and the same GPU flags the
 * harness uses, because the headless shell hands back SwiftShader and would
 * answer every question in this spike against a CPU rasteriser.
 * `VITREA_ALLOW_FALLBACK_ADAPTER` is deliberately not consulted: G0 has no
 * software path.
 */
import { createServer } from "node:http";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { extname, join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "@playwright/test";

const HERE = dirname(fileURLToPath(import.meta.url));
const PAGES = join(HERE, "pages");
const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];
const MIME = { ".html": "text/html", ".json": "application/json", ".png": "image/png", ".js": "text/javascript" };

const flag = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : fallback;
};

const jobs = JSON.parse(await readFile(resolve(flag("jobs", "jobs.json")), "utf8"));
const outDir = resolve(flag("out", "/tmp/w16-g0"));
await mkdir(outDir, { recursive: true });

const server = createServer(async (req, res) => {
  const path = join(PAGES, decodeURIComponent((req.url ?? "/").split("?")[0]));
  try {
    const body = await readFile(path);
    res.writeHead(200, { "content-type": MIME[extname(path)] ?? "application/octet-stream" });
    res.end(body);
  } catch {
    res.writeHead(404).end("no");
  }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;
process.stdout.write(`serving ${PAGES} at ${base}\n`);

const browser = await chromium.launch({ channel: "chromium", args: GPU_ARGS });
process.stdout.write(`engine: chromium ${browser.version()}\n`);

const manifest = { engine: browser.version(), args: GPU_ARGS, jobs: [] };
let context = null;
let currentScale = null;

for (const job of jobs) {
  const scale = job.dpr ?? 1;
  if (scale !== currentScale) {
    if (context) await context.close();
    context = await browser.newContext({
      viewport: { width: 320, height: 200 },
      deviceScaleFactor: scale,
      colorScheme: "light",
    });
    currentScale = scale;
  }
  const page = await context.newPage();
  const url = `${base}/probe.html?${new URLSearchParams({ ...job.query, dpr: String(scale) })}`;
  await page.goto(url, { waitUntil: "load" });
  await page.waitForSelector("html[data-ready='1']");
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const buffer = await page.screenshot({ clip: { x: 0, y: 0, width: 320, height: 200 }, animations: "disabled" });
  await writeFile(join(outDir, `${job.id}.png`), buffer);
  const report = await page.evaluate(() => window.__w16);
  // Two loads must agree, or the reading is not a reading (the harness's own rule).
  const again = await page.screenshot({ clip: { x: 0, y: 0, width: 320, height: 200 }, animations: "disabled" });
  manifest.jobs.push({ ...job, url, report, deterministic: Buffer.compare(buffer, again) === 0 });
  process.stdout.write(`${job.id}  ${report.form}/${report.carrier ?? "-"}  dpr=${scale}\n`);
  await page.close();
}

if (context) await context.close();
await browser.close();
server.close();
await writeFile(join(outDir, "manifest.json"), JSON.stringify(manifest, null, 1));
process.stdout.write(`\n[wrote] ${outDir}\n`);
