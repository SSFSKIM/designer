// Second browser run, after the light scheme's lifts were returned to the scheme's own in clear
// mode (DESIGN.md part two, deferred item 1) and once the machine was free. Re-measures the
// clear matrix (both tiers, both schemes, four phases, rest and platter), compares every cell's
// canvas and pixels with the first run's, re-captures the light Day pair, and adds the pair the
// user's screenshot showed: dark scheme, the Day photograph chosen in the platter, 02:45, at
// rest and with the platter open. Scratch tooling; paths under /tmp/sp-clear/.
import { gpuBrowser, frames, measureState, fingerprint, keepFor, CARET, PORT } from "./lib.mjs";
import { readFileSync, writeFileSync, existsSync, renameSync, mkdirSync } from "node:fs";
const FIRST = JSON.parse(readFileSync("/tmp/sp-clear/final.json", "utf8"));
const { chosen } = JSON.parse(readFileSync("/tmp/sp-clear/sweep.json", "utf8"));
const PHASES = ["dawn", "day", "dusk", "night"];
const t0 = Date.now();
const log = (...a) => console.log(`[${((Date.now() - t0) / 1000).toFixed(0)}s]`, ...a);
const out = { chosen, matrix: [], comparisons: [], errors: [] };
mkdirSync("/tmp/sp-clear/clear-shots-2", { recursive: true });
// Keep the first run's light Day captures under another name; compose reads the new ones.
for (const f of ["light-day-regular", "light-day-clear"]) {
  const p = `/tmp/sp-clear/cmp/${f}.png`;
  if (existsSync(p) && !existsSync(`/tmp/sp-clear/cmp/${f}-v1.png`)) renameSync(p, `/tmp/sp-clear/cmp/${f}-v1.png`);
}
const browser = await gpuBrowser();
const open = async (scheme, query, dpr = 1) => {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, colorScheme: scheme, deviceScaleFactor: dpr });
  const page = await ctx.newPage();
  page.on("pageerror", (e) => out.errors.push(`${scheme} ${query}: pageerror ${e.message}`));
  page.on("console", (m) => { if (m.type() === "error") out.errors.push(`${scheme} ${query}: console ${m.text()}`); });
  await page.goto(`http://localhost:${PORT}/gallery/start-page/${query}`);
  await page.waitForFunction(() => window.__vitrea && window.__glassDemo);
  await page.addStyleTag({ content: CARET });
  return { ctx, page };
};
try {
  // A: the clear matrix again, each cell beside the first run's.
  for (const tier of ["webgpu", "css"]) for (const scheme of ["light", "dark"]) {
    const q = `?at=15:10${tier === "css" ? "&tier=css" : ""}&glass=clear`;
    const { ctx, page } = await open(scheme, q);
    for (const phase of PHASES) {
      await page.evaluate((phase) => window.__glassDemo.setPhase(phase), phase);
      await page.waitForTimeout(900); await frames(page, 4);
      for (const state of ["rest", "platter"]) {
        if (state === "platter") { await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(1000); }
        const r = await measureState(page, { keep: keepFor(state), shot: `/tmp/sp-clear/clear-shots-2/${tier}-${scheme}-${phase}-${state}.png` });
        const prev = FIRST.matrix.find((m) => m.glass === "clear" && m.tier === tier && m.scheme === scheme && m.phase === phase && m.state === state);
        const lifts = await page.evaluate(() => { const cs = getComputedStyle(document.documentElement); return [cs.getPropertyValue("--lift").trim(), cs.getPropertyValue("--lift-strong").trim()]; });
        out.matrix.push({ glass: "clear", tier, scheme, phase, state, lifts, ...r, first: prev ? { canvas: prev.fp.canvas, pixels: prev.pixels } : null });
        if (state === "platter") { await page.keyboard.press("Escape"); await page.waitForTimeout(800); }
      }
    }
    const rows = out.matrix.filter((m) => m.tier === tier && m.scheme === scheme);
    const lines = rows.flatMap((m) => m.lines.filter((l) => l.lineState === "visible"));
    log("clear", tier, scheme, "gated", lines.length, "failing", lines.filter((l) => !l.pass).length, "diags", rows.flatMap((m) => m.fp.diags.map((d) => d.code)).join(",") || "none",
      "canvas same as run 1:", rows.filter((m) => m.first && m.first.canvas === m.fp.canvas).length, "/", rows.length, "pixels same:", rows.filter((m) => m.first && m.first.pixels === m.pixels).length, "lifts", rows[0].lifts.join(" "));
    await ctx.close();
  }

  // B: the comparison pairs, 1440 x 900 at 2x, WebGPU tier. `phase` is chosen after load, as the
  // platter's picker does; without it the photograph follows the clock.
  const pairs = [
    { name: "light-day", scheme: "light", at: "15:10", phase: null, platter: false },
    { name: "dark-day", scheme: "dark", at: "02:45", phase: "day", platter: false },
    { name: "dark-day-platter", scheme: "dark", at: "02:45", phase: "day", platter: true },
  ];
  for (const p of pairs) for (const glass of ["regular", "clear"]) {
    const { ctx, page } = await open(p.scheme, `?at=${p.at}${glass === "clear" ? "&glass=clear" : ""}`, 2);
    await page.waitForTimeout(1500); await frames(page, 4);
    if (p.phase) { await page.evaluate((phase) => window.__glassDemo.setPhase(phase), p.phase); await page.waitForTimeout(1200); await frames(page, 4); }
    if (p.platter) { await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(1400); await frames(page, 4); }
    const fp = await fingerprint(page);
    const photograph = await page.evaluate(() => document.querySelector("canvas.environment")?.dataset.phase ?? document.documentElement.dataset.phase ?? null);
    await page.screenshot({ path: `/tmp/sp-clear/cmp/${p.name}-${glass}.png` });
    out.comparisons.push({ ...p, glass, fp, photograph });
    log("comparison", p.name, glass, Object.values(fp.groups).map((g) => g.caps?.activeRenderer).join("/"), "diags", fp.diags.map((d) => d.code).join(",") || "none", "inks", Object.values(fp.inks).join(","));
    await ctx.close();
  }

  // Label strips, as in the first run.
  {
    const ctx = await browser.newContext({ viewport: { width: 2886, height: 60 }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    const scene = { "light-day": "light scheme · Day · 15:10", "dark-day": "dark scheme · Day photograph chosen · 02:45", "dark-day-platter": "dark scheme · Day photograph chosen · 02:45 · platter open" };
    for (const p of pairs) for (const [size, half, h, fs] of [["wide", 1440, 40, 19], ["narrow", 717, 30, 12]]) {
      const pct = Math.round((p.scheme === "light" ? chosen.light : chosen.dark) * 100);
      const cell = (strong, rest) => `<div style="width:${half}px;height:${h}px;display:flex;align-items:center;gap:${fs * 0.6}px;padding:0 ${fs}px;box-sizing:border-box;white-space:nowrap;overflow:hidden"><b style="font-weight:700">${strong}</b><span style="opacity:.72;font-weight:500">${rest}</span></div>`;
      await page.setContent(`<body style="margin:0;background:#1c1c1e;color:#f2f2f7;font:600 ${fs}px -apple-system,BlinkMacSystemFont,system-ui,sans-serif;-webkit-font-smoothing:antialiased"><div style="display:flex;width:${half * 2 + 6}px">${cell("regular", `shipped · ${scene[p.name]} · WebGPU`)}<div style="width:6px;height:${h}px;background:#000"></div>${cell("clear: uncalibrated", `page-painted black ${pct} % under each host · ${scene[p.name]} · WebGPU`)}</div></body>`);
      await page.screenshot({ path: `/tmp/sp-clear/cmp/strip-${p.name}-${size}.png`, clip: { x: 0, y: 0, width: half * 2 + 6, height: h } });
    }
    log("label strips drawn");
    await ctx.close();
  }
} finally {
  await browser.close();
  writeFileSync("/tmp/sp-clear/recapture.json", JSON.stringify(out));
  log("done; errors", out.errors.length, out.errors.slice(0, 5).join(" | "));
}
