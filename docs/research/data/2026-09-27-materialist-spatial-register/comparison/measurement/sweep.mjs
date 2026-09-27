// Clear mode, GPU tier: raise the dimming per scheme from black 0.30 until every gated line
// (4.5:1 / 3:1) and mark (3:1) at rest and in the open platter passes, over the four phases.
import { gpuBrowser, frames, measureState, keepFor, CARET, PORT } from "./lib.mjs";
import { writeFileSync } from "node:fs";
const STRENGTHS = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7];
const PHASES = ["dawn", "day", "dusk", "night"];
const t0 = Date.now();
const browser = await gpuBrowser();
const out = { steps: [], chosen: {} };
try {
  for (const scheme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, colorScheme: scheme, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(`http://localhost:${PORT}/gallery/start-page/?at=15:10&glass=clear`);
    await page.waitForFunction(() => window.__vitrea && window.__glassDemo);
    await page.addStyleTag({ content: CARET });
    let best;
    for (const s of STRENGTHS) {
      await page.evaluate((s) => window.__glassDemo.setDimming(s), s);
      const fails = [], diags = new Set(); let gated = 0, worst = null;
      for (const phase of PHASES) {
        await page.evaluate((phase) => window.__glassDemo.setPhase(phase), phase);
        await page.waitForTimeout(900); await frames(page, 4);
        for (const state of ["rest", "platter"]) {
          if (state === "platter") { await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(1000); }
          const r = await measureState(page, { keep: keepFor(state) });
          r.fp.diags.forEach((d) => diags.add(d.code));
          const scrims = Object.values(r.fp.groups).map((g) => g.material?.dimming?.scrim);
          if (scrims.some((x) => x !== s)) diags.add(`scrim-mismatch:${scrims.join("/")}`);
          for (const l of r.lines.filter((l) => l.lineState === "visible")) {
            gated++;
            if (!worst || l.worst / l.floor < worst.worst / worst.floor) worst = { ...l, phase, state };
            if (!l.pass) fails.push({ phase, state, host: l.host, text: l.text, worst: l.worst, floor: l.floor, median: l.median, surface: l.surface, range: l.surfaceRange, color: l.color });
          }
          if (state === "platter") { await page.keyboard.press("Escape"); await page.waitForTimeout(800); }
        }
      }
      const step = { scheme, strength: s, gated, failing: fails.length, worst: worst && { text: worst.text, host: worst.host, phase: worst.phase, state: worst.state, ratio: worst.worst, floor: worst.floor }, fails, diags: [...diags], errors: [...errors] };
      out.steps.push(step);
      console.log(`${scheme} ${s.toFixed(2)} gated ${gated} failing ${fails.length} worst ${worst?.worst}/${worst?.floor} "${worst?.text}" [${worst?.host} ${worst?.phase} ${worst?.state}] diags ${[...diags].join(",") || "none"} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
      for (const f of fails.slice(0, 12)) console.log(`   FAIL ${f.phase}/${f.state} ${f.worst}<${f.floor} "${f.text}" [${f.host}] surf ${f.surface} ${JSON.stringify(f.range)} ink ${f.color}`);
      if (!best || fails.length < best.failing) best = step;
      if (fails.length === 0) break;
    }
    out.chosen[scheme] = best.strength;
    await ctx.close();
  }
} finally {
  await browser.close();
}
writeFileSync("/tmp/sp-clear/sweep.json", JSON.stringify(out, null, 1));
console.log("CHOSEN", JSON.stringify(out.chosen), `${((Date.now() - t0) / 1000).toFixed(0)} s`);
