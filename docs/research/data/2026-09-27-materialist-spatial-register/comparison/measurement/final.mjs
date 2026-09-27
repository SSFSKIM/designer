// The one browser run after the sweep: default and clear matrices (both tiers, both schemes,
// four phases, rest and platter), the Reduce Transparency platter, the live toggle with a
// morph trace, and the three comparison pairs at 2x. Scratch tooling.
import { gpuBrowser, frames, measureState, fingerprint, keepFor, CARET, PORT } from "./lib.mjs";
import { readFileSync, writeFileSync } from "node:fs";
const { chosen } = JSON.parse(readFileSync("/tmp/sp-clear/sweep.json", "utf8"));
const PHASES = ["dawn", "day", "dusk", "night"];
const t0 = Date.now();
const log = (...a) => console.log(`[${((Date.now() - t0) / 1000).toFixed(0)}s]`, ...a);
const out = { chosen, matrix: [], rtPlatter: [], toggle: null, trace: null, comparisons: [], errors: [] };
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
  // A and B: the matrices.
  for (const glass of ["regular", "clear"]) for (const tier of ["webgpu", "css"]) for (const scheme of ["light", "dark"]) {
    const q = `?at=15:10${tier === "css" ? "&tier=css" : ""}${glass === "clear" ? "&glass=clear" : ""}`;
    const { ctx, page } = await open(scheme, q);
    for (const phase of PHASES) {
      await page.evaluate((phase) => window.__glassDemo.setPhase(phase), phase);
      await page.waitForTimeout(900); await frames(page, 4);
      for (const state of ["rest", "platter"]) {
        if (state === "platter") { await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(1000); }
        const dir = glass === "regular" ? "after-shots" : "clear-shots";
        const r = await measureState(page, { keep: keepFor(state), shot: `/tmp/sp-clear/${dir}/${tier}-${scheme}-${phase}-${state}.png` });
        out.matrix.push({ glass, tier, scheme, phase, state, ...r });
        if (state === "platter") { await page.keyboard.press("Escape"); await page.waitForTimeout(800); }
      }
    }
    const rows = out.matrix.filter((m) => m.glass === glass && m.tier === tier && m.scheme === scheme);
    const lines = rows.flatMap((m) => m.lines.filter((l) => l.lineState === "visible"));
    log(glass, tier, scheme, "gated", lines.length, "failing", lines.filter((l) => !l.pass).length, "diags", rows.flatMap((m) => m.fp.diags.map((d) => d.code)).join(",") || "none");
    await ctx.close();
  }

  // C: the platter under Reduce Transparency, default mode, GPU.
  for (const scheme of ["light", "dark"]) {
    const { ctx, page } = await open(scheme, "?at=15:10");
    for (const phase of ["dawn", "day"]) {
      await page.evaluate((phase) => window.__glassDemo.setPhase(phase), phase);
      for (const rt of [false, true]) {
        await page.evaluate((rt) => window.__glassDemo.setReducedTransparency(rt), rt);
        await page.waitForTimeout(1000); await frames(page, 4);
        await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(1200);
        const m = await page.evaluate(() => { const p = document.querySelector(".platter"); const h = document.querySelector(".photograph-morph").getBoundingClientRect(); return { scrollHeight: p.scrollHeight, clientHeight: p.clientHeight, overflow: p.scrollHeight - p.clientHeight, host: [h.x, h.y, h.width, h.height].map(Math.round), bottomMargin: Math.round(innerHeight - h.bottom) }; });
        out.rtPlatter.push({ scheme, phase, rt, ...m });
        log("platter", scheme, phase, rt ? "RT" : "nominal", JSON.stringify(m));
        await page.keyboard.press("Escape"); await page.waitForTimeout(800);
      }
      await page.evaluate(() => window.__glassDemo.setReducedTransparency(false)); await page.waitForTimeout(600);
    }
    await ctx.close();
  }

  // D: the live toggle from the platter's switch, and the dimming following the morph.
  {
    const { ctx, page } = await open("dark", "?at=15:10");
    await page.waitForTimeout(900);
    await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(1200);
    const probe = () => page.evaluate(() => { const c = document.querySelector("canvas.environment"); const h = document.querySelector(".photograph-morph").getBoundingClientRect(); const x = Math.round(h.x + 30), y = Math.round(h.bottom - 8); const d = c.getContext("2d").getImageData(x, y, 1, 1).data; return { x, y, rgb: [d[0], d[1], d[2]] }; });
    const before = await fingerprint(page); const pBefore = await probe();
    const sw = page.getByRole("switch", { name: "Clear glass (uncalibrated)" });
    await sw.click(); await page.waitForTimeout(1500); await frames(page, 4);
    const on = await fingerprint(page); const pOn = await probe();
    const focusOn = await page.evaluate(() => ({ active: document.activeElement?.textContent ?? null, checked: document.activeElement?.getAttribute("aria-checked") ?? null, platterOpen: document.querySelector(".platter") !== null }));
    // The morph trace in clear mode: close, then open, reading the host and its hint each frame.
    const trace = (n) => page.evaluate(async (n) => {
      const dec = (v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
      const res = [];
      for (let k = 0; k < n; k++) {
        await new Promise((r) => requestAnimationFrame(r));
        const c = document.querySelector("canvas.environment"); const el = document.querySelector(".photograph-morph"); if (!el) continue;
        const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4) continue;
        const sx = c.width / innerWidth, sy = c.height / innerHeight;
        const x0 = Math.floor(r.x * sx), y0 = Math.floor(r.y * sy), w = Math.ceil((r.x + r.width) * sx) - x0, h = Math.ceil((r.y + r.height) * sy) - y0;
        const d = c.getContext("2d").getImageData(x0, y0, w, h).data; let R = 0, G = 0, B = 0, m = 0;
        for (let i = 0; i < d.length; i += 4) { R += d[i]; G += d[i + 1]; B += d[i + 2]; m++; }
        const lum = 0.2126 * dec(R / m / 255) + 0.7152 * dec(G / m / 255) + 0.0722 * dec(B / m / 255);
        const hint = window.__vitrea.scene.glassGroup("photograph").descriptor.backdrop?.luminance ?? null;
        res.push([Math.round(r.width), Math.round(r.height), +lum.toFixed(4), hint]);
      }
      return res;
    }, n);
    await page.keyboard.press("Escape"); const closing = await trace(50);
    await page.evaluate(() => window.__glassDemo.openMenu()); const opening = await trace(50);
    await page.waitForTimeout(800);
    await page.getByRole("switch", { name: "Clear glass (uncalibrated)" }).click(); await page.waitForTimeout(1500); await frames(page, 4);
    const off = await fingerprint(page); const pOff = await probe();
    out.toggle = { before, on, off, pBefore, pOn, pOff, focusOn };
    out.trace = { closing, opening };
    const lag = (t) => t.map((f) => Math.abs(f[2] - f[3])).reduce((a, b) => Math.max(a, b), 0);
    log("toggle urls", before.url, "->", on.url, "->", off.url, "attr", on.glassAttr, off.glassAttr, "focus", JSON.stringify(focusOn));
    log("probe under platter", JSON.stringify(pBefore.rgb), JSON.stringify(pOn.rgb), JSON.stringify(pOff.rgb), "trace frames", closing.length, opening.length, "max |canvas-hint|", lag(closing).toFixed(4), lag(opening).toFixed(4));
    await ctx.close();
  }

  // E: the comparison pairs, 1440 x 900 at 2x, WebGPU tier.
  const pairs = [
    { name: "light-day", scheme: "light", at: "15:10", platter: false },
    { name: "dark-night", scheme: "dark", at: "02:45", platter: false },
    { name: "dark-night-platter", scheme: "dark", at: "02:45", platter: true },
  ];
  for (const p of pairs) for (const glass of ["regular", "clear"]) {
    const { ctx, page } = await open(p.scheme, `?at=${p.at}${glass === "clear" ? "&glass=clear" : ""}`, 2);
    await page.waitForTimeout(1500); await frames(page, 4);
    if (p.platter) { await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(1400); await frames(page, 4); }
    const fp = await fingerprint(page);
    await page.screenshot({ path: `/tmp/sp-clear/cmp/${p.name}-${glass}.png` });
    out.comparisons.push({ ...p, glass, fp });
    log("comparison", p.name, glass, Object.values(fp.groups).map((g) => g.caps?.activeRenderer).join("/"), "diags", fp.diags.map((d) => d.code).join(",") || "none");
    await ctx.close();
  }

  // Label strips for the composites, drawn now because no browser runs after this script:
  // "wide" for halves at 1440 (composite 2886 wide), "narrow" for halves at 717 (1440 wide).
  {
    const ctx = await browser.newContext({ viewport: { width: 2886, height: 60 }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    const scene = { "light-day": "light scheme · Day · 15:10", "dark-night": "dark scheme · Night · 02:45", "dark-night-platter": "dark scheme · Night · 02:45 · platter open" };
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
  writeFileSync("/tmp/sp-clear/final.json", JSON.stringify(out));
  log("done; errors", out.errors.length, out.errors.slice(0, 5).join(" | "));
}
