// Default-state fingerprint: screenshot pixels, painted canvas bytes, group descriptors and
// resolved states, per tier x scheme x phase x state. Scratch tooling.
import { gpuBrowser, frames } from "./pw.mjs";
import { createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire("/Users/new/Developer/GitHub/designer/apps/demo/package.json");
const { PNG } = require("pngjs");
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i < 0 ? d : process.argv[i + 1]; };
const out = arg("out", "/tmp/sp-clear/baseline.json");
const query = arg("query", "");
const port = arg("port", "5191");
const DPR = +arg("dpr", "1");
const tiers = arg("tiers", "webgpu,css").split(",");
const schemes = arg("schemes", "light,dark").split(",");
const phases = arg("phases", "dawn,day,dusk,night").split(",");
const states = arg("states", "rest,platter").split(",");
const shots = arg("shots", "");
const sha = (b) => createHash("sha256").update(b).digest("hex").slice(0, 16);
const browser = await gpuBrowser();
const results = {};
for (const tier of tiers) for (const scheme of schemes) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, colorScheme: scheme, deviceScaleFactor: DPR });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(`http://localhost:${port}/gallery/start-page/?at=15:10${tier === "css" ? "&tier=css" : ""}${query}`);
  await page.waitForFunction(() => window.__vitrea && window.__glassDemo);
  await page.addStyleTag({ content: "* { caret-color: transparent !important; }" });
  for (const phase of phases) {
    await page.evaluate((phase) => window.__glassDemo.setPhase(phase), phase);
    await page.waitForTimeout(900); await frames(page, 4);
    for (const state of states) {
      if (state === "platter") { await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(900); }
      await page.waitForTimeout(300); await frames(page, 3);
      const png = PNG.sync.read(await page.screenshot());
      if (shots) writeFileSync(`${shots}/${tier}-${scheme}-${phase}-${state}.png`, PNG.sync.write(png));
      const info = await page.evaluate(async () => {
        const c = document.querySelector("canvas.environment");
        const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
        const h = new Uint8Array(await crypto.subtle.digest("SHA-256", d));
        const root = window.__vitrea;
        const groups = {};
        for (const id of ["now", "places", "today", "search", "photograph"]) {
          const g = root.scene.glassGroup(id);
          groups[id] = { descriptor: g ? { backdrop: g.descriptor.backdrop, material: g.descriptor.material } : null, caps: root.capabilities(id) };
        }
        const hosts = [...document.querySelectorAll("[data-vitrea-node]")].map((h) => { const r = h.getBoundingClientRect(); return [h.getAttribute("data-glass-role"), Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)]; });
        const diags = [...root.diagnostics.reported, ...root.scene.diagnostics.reported].map((e) => e.code);
        return { canvas: [...h.slice(0, 8)].map((b) => b.toString(16).padStart(2, "0")).join(""), canvasSize: [c.width, c.height], groups, hosts, diags };
      });
      results[`${tier}/${scheme}/${phase}/${state}`] = { pixels: sha(png.data), ...info };
      if (state === "platter") { await page.keyboard.press("Escape"); await page.waitForTimeout(800); }
    }
  }
  if (errors.length) console.log("page errors", tier, scheme, errors);
  await ctx.close();
}
await browser.close();
writeFileSync(out, JSON.stringify(results, null, 1));
for (const [k, v] of Object.entries(results)) console.log(k.padEnd(28), v.pixels, v.canvas, JSON.stringify(v.hosts.map((h) => h.slice(1).join("x"))), v.diags.join(",") || "no-diags");
