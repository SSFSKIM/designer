#!/usr/bin/env node
// Settling experiment: measure every build under figma-design-workspace/settling/builds/<id>/.
// (docs/doperpowers/specs/2026-09-05-settling-experiment.md, "Measures": V and the token reads for D2–D3.)
//
// For each build with index.html: renders in Chromium at 1440 × 900, records uncaught errors,
// horizontal overflow, placeholder text, a contrast sample, the rendered ground, the most chromatic
// interactive colour (the accent), the h1 / body / mono families, and writes shot-full.png and
// shot-fv.png beside the build. Then runs layout-topology.mjs over every measured build so the
// pairwise matrices cover the whole set. Output: <ws>/measurements.json and <ws>/topology.json.
//
//   node measure.mjs [--only id,id] [--skip-topology]

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");
const ws = process.env.SETTLING_WS || path.join(repo, "figma-design-workspace/settling");
const buildsDir = path.join(ws, "builds");
const outPath = path.join(ws, "measurements.json");
const args = process.argv.slice(2);
const only = args.includes("--only") ? args[args.indexOf("--only") + 1].split(",") : null;
const skipTopology = args.includes("--skip-topology");

// A Playwright module whose Chromium is actually installed: each candidate is test-launched, because
// an npx cache can hold a newer Playwright than the browser cache has a binary for.
async function playwright() {
  const cands = [process.env.PLAYWRIGHT_MODULE].filter(Boolean);
  const npx = path.join(process.env.HOME, ".npm/_npx");
  if (fs.existsSync(npx)) for (const d of fs.readdirSync(npx)) { const p = path.join(npx, d, "node_modules/playwright"); if (fs.existsSync(p)) cands.push(p); }
  cands.push("playwright");
  const require = createRequire(path.join(repo, "packages/platform-web/package.json"));
  for (const c of cands) {
    let m; try { m = require(c); } catch { continue; }
    try { const b = await m.chromium.launch(); await b.close(); return { chromium: m.chromium, module: c }; } catch {}
  }
  throw new Error("no Playwright module with an installed Chromium");
}

// Runs in the page. Returns the token reads and the mechanical checks.
function extract() {
  const srgb = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const parse = (s) => { const m = s && s.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/); return m ? { r: +m[1], g: +m[2], b: +m[3], a: m[4] == null ? 1 : +m[4] } : null; };
  const oklch = ({ r, g, b }) => {
    const R = srgb(r), G = srgb(g), B = srgb(b);
    const l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B), m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B), n = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B);
    const A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * n, Bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * n;
    let H = Math.atan2(Bb, A) * 180 / Math.PI; if (H < 0) H += 360;
    return { L: +(0.2104542553 * l + 0.793617785 * m - 0.0040720468 * n).toFixed(3), C: +Math.hypot(A, Bb).toFixed(3), H: +H.toFixed(1) };
  };
  const lum = ({ r, g, b }) => 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b);
  const contrast = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const over = (fg, bg) => ({ r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a), b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1 });
  const hex = ({ r, g, b }) => "#" + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, "0")).join("").toUpperCase();
  const visible = (el) => el.checkVisibility ? el.checkVisibility({ contentVisibilityAuto: true, visibilityProperty: true, opacityProperty: true }) : true;

  // Effective background: composite upward until an opaque colour; a background-image is unknown.
  const effectiveBg = (el) => {
    let acc = null; let node = el;
    while (node && node !== document.documentElement.parentNode) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== "none") return null;
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { acc = acc ? over(acc, c) : c; if (c.a >= 0.99) return acc; }
      node = node.parentElement;
    }
    const white = { r: 255, g: 255, b: 255, a: 1 };
    return acc ? over(acc, white) : white;
  };

  // Ground.
  const bodyBg = parse(getComputedStyle(document.body).backgroundColor), htmlBg = parse(getComputedStyle(document.documentElement).backgroundColor);
  const ground = bodyBg && bodyBg.a > 0.5 ? bodyBg : htmlBg && htmlBg.a > 0.5 ? htmlBg : { r: 255, g: 255, b: 255, a: 1 };

  // Text sample and contrast.
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const texts = []; let t;
  while ((t = walker.nextNode())) { if (t.textContent.trim().length >= 2 && t.parentElement && !["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"].includes(t.parentElement.tagName)) texts.push(t.parentElement); }
  const uniq = [...new Set(texts)].filter(visible);
  const step = Math.max(1, Math.floor(uniq.length / 300));
  const sample = uniq.filter((_, i) => i % step === 0);
  let checked = 0, pass = 0, unknown = 0; const fails = [];
  for (const el of sample) {
    const cs = getComputedStyle(el); const fg = parse(cs.color); if (!fg) continue;
    const bg = effectiveBg(el); if (!bg) { unknown++; continue; }
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
    const large = size >= 24 || (size >= 18.66 && bold);
    const c = contrast(fg.a < 1 ? over(fg, bg) : fg, bg);
    checked++; if (c >= (large ? 3 : 4.5)) pass++; else if (fails.length < 12) fails.push({ text: el.textContent.trim().slice(0, 40), ratio: +c.toFixed(2), size });
  }

  // Accent: most chromatic colour on interactive elements (background, text or border).
  const interactive = [...document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="tab"], [role="link"], summary, label')].filter(visible);
  const chroma = [];
  const consider = (col, where) => { const c = parse(col); if (!c || c.a < 0.5) return; const o = oklch(c); if (o.C >= 0.06 && o.L >= 0.2 && o.L <= 0.9) chroma.push({ ...o, hex: hex(c), where }); };
  for (const el of interactive) { const cs = getComputedStyle(el); consider(cs.backgroundColor, "bg"); consider(cs.color, "fg"); consider(cs.borderTopColor, "border"); }
  chroma.sort((a, b) => b.C - a.C);
  let accent = chroma[0] || null;
  if (!accent) { // fallback: any visible element
    const all = [...document.querySelectorAll("body *")].filter(visible).slice(0, 4000);
    for (const el of all) { const cs = getComputedStyle(el); consider(cs.backgroundColor, "any-bg"); consider(cs.color, "any-fg"); }
    chroma.sort((a, b) => b.C - a.C); accent = chroma[0] || null;
  }
  // Distinct chromatic hues in use (clustered at 20°), for the palette count.
  const hues = []; for (const c of chroma) { if (!hues.some((h) => Math.min(Math.abs(h - c.H), 360 - Math.abs(h - c.H)) < 20)) hues.push(c.H); }

  // Families.
  const fam = (el) => el ? getComputedStyle(el).fontFamily.split(",")[0].replace(/["']/g, "").trim() : null;
  const h1 = document.querySelector("h1");
  const mono = [...document.querySelectorAll("body *")].find((el) => /mono|courier|consolas|menlo|code/i.test(getComputedStyle(el).fontFamily) && visible(el));
  const families = { display: fam(h1), body: fam(document.body), mono: mono ? fam(mono) : null };

  const text = document.body.innerText || "";
  return {
    ground: { hex: hex(ground), ...oklch(ground) },
    accent,
    hueCount: hues.length,
    families,
    contrast: { checked, pass, unknown, rate: checked ? +(pass / checked).toFixed(3) : null, fails },
    overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
    placeholder: /lorem ipsum|\bipsum\b|placeholder text|\bTODO\b|\bTBD\b|\blorem\b/i.test(text),
    docHeight: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
    words: text.split(/\s+/).filter(Boolean).length,
    h1: h1 ? h1.textContent.trim().slice(0, 120) : null,
    title: document.title,
  };
}

async function measureOne(chromium, id) {
  const dir = path.join(buildsDir, id); const file = path.join(dir, "index.html");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const errors = [], consoleErrors = [], failedRequests = [];
  page.on("pageerror", (e) => errors.push(String(e.message || e).slice(0, 200)));
  page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text().slice(0, 200)); });
  page.on("requestfailed", (r) => failedRequests.push(r.url().slice(0, 120)));
  await page.goto(pathToFileURL(file).href, { waitUntil: "load" });
  await page.waitForTimeout(1200);
  // Scroll through to trigger reveal-on-scroll, then return to the top.
  await page.evaluate(async () => { await new Promise((res) => { let y = 0; const step = () => { window.scrollTo(0, y); y += Math.round(window.innerHeight * 0.75); if (y < document.body.scrollHeight) setTimeout(step, 90); else { window.scrollTo(0, 0); setTimeout(res, 300); } }; step(); }); });
  await page.waitForTimeout(400);
  const data = await page.evaluate(extract);
  await page.screenshot({ path: path.join(dir, "shot-fv.png"), fullPage: false });
  await page.screenshot({ path: path.join(dir, "shot-full.png"), fullPage: true });
  await browser.close();
  const bytes = fs.statSync(file).size;
  const hasDesign = fs.existsSync(path.join(dir, "DESIGN.md"));
  return { id, ...data, errors, consoleErrors, failedRequests: failedRequests.length, bytes, hasDesign, measuredAt: new Date().toISOString(),
    gateMechanical: errors.length === 0 && !data.overflow && !data.placeholder && (data.contrast.rate == null || data.contrast.rate >= 0.9) };
}

const { chromium, module } = await playwright();
console.log("playwright: " + module);
const prev = fs.existsSync(outPath) ? JSON.parse(fs.readFileSync(outPath, "utf8")) : { builds: {} };
const ids = fs.readdirSync(buildsDir).filter((d) => fs.existsSync(path.join(buildsDir, d, "index.html"))).filter((d) => !only || only.includes(d)).sort();
for (const id of ids) {
  const stamp = fs.statSync(path.join(buildsDir, id, "index.html")).mtimeMs;
  if (prev.builds[id] && prev.builds[id].mtimeMs === stamp && !prev.builds[id].error && !only) { continue; }
  process.stdout.write(`measure ${id} … `);
  try { prev.builds[id] = { ...(await measureOne(chromium, id)), mtimeMs: stamp }; console.log(prev.builds[id].gateMechanical ? "ok" : "gate-fail"); }
  catch (e) { console.log("ERROR " + e.message); prev.builds[id] = { id, error: String(e.message), mtimeMs: stamp, gateMechanical: false }; }
}
fs.writeFileSync(outPath, JSON.stringify(prev, null, 1));
console.log(`${Object.keys(prev.builds).length} builds → ${outPath}`);

if (!skipTopology) {
  const files = Object.keys(prev.builds).filter((id) => !prev.builds[id].error).map((id) => path.join(buildsDir, id, "index.html"));
  if (files.length >= 1) {
    execFileSync("node", [path.join(repo, "docs/research/scripts/layout-topology.mjs"), "--out", path.join(ws, "topology.json"), ...files], { env: { ...process.env, PLAYWRIGHT_MODULE: module }, stdio: ["ignore", "ignore", "inherit"] });
    console.log(`topology over ${files.length} builds → ${path.join(ws, "topology.json")}`);
  }
}
