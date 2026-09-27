// Per-line rendered contrast for Daybreak. Tooling for the record, not a deliverable.
// node measure.mjs --tiers webgpu,css --schemes light,dark --phases dawn,day,dusk,night --poses active,inactive --rt 0,1 --variants rest,top,bottom,search,platter --out file
import { gpuBrowser, decodePng, frames } from "./pw.mjs";
import { writeFileSync } from "node:fs";
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i < 0 ? d : process.argv[i + 1]; };
const tiers = arg("tiers", "webgpu").split(",");
const schemes = arg("schemes", "light,dark").split(",");
const phases = arg("phases", "dawn,day,dusk,night").split(",");
const poses = arg("poses", "active,inactive").split(",");
const rts = arg("rt", "0").split(",").map(Number);
const variants = arg("variants", "rest").split(",");
const at = arg("at", "15:10");
const W = +arg("w", "1440"), H = +arg("h", "900"), DPR = +arg("dpr", "1");
const outFile = arg("out", "/tmp/sp/contrast.json");
const shotDir = arg("shots", "");

const dec = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const lum = (r, g, b) => 0.2126 * dec(r) + 0.7152 * dec(g) + 0.0722 * dec(b);
const ratio = (a, b) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);

const HIDE = `
[data-vitrea-node] *, [data-vitrea-node] { color: transparent !important; -webkit-text-fill-color: transparent !important; caret-color: transparent !important; text-decoration-color: transparent !important; }
[data-vitrea-node] ::placeholder { color: transparent !important; }
[data-vitrea-node] svg { visibility: hidden !important; }
[data-vitrea-node] .task-mark, [data-vitrea-node] .switch { visibility: hidden !important; }
[data-vitrea-node] *:focus-visible { outline-color: transparent !important; }
`;

async function collect(page) {
  return page.evaluate(() => {
    const out = [];
    const canvas = document.createElement("canvas"); canvas.width = canvas.height = 1;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    const rgba = (color) => { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = "#000"; ctx.fillStyle = color; ctx.fillRect(0, 0, 1, 1); const d = ctx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
    const scroller = document.querySelector(".today-scroll");
    const sr = scroller?.getBoundingClientRect();
    const clipOf = (el) => {
      if (scroller && scroller.contains(el)) {
        return { top: sr.top + (scroller.hasAttribute("data-edge-top") ? 28 : 0), bottom: sr.bottom - (scroller.hasAttribute("data-edge-bottom") ? 36 : 0), hardTop: sr.top, hardBottom: sr.bottom };
      }
      return null;
    };
    for (const host of document.querySelectorAll("[data-vitrea-node]")) {
      const role = host.getAttribute("data-glass-role");
      const hostName = host.getAttribute("aria-label") || (host.querySelector("h2")?.textContent ?? host.className);
      const hr = host.getBoundingClientRect();
      const walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const text = node.textContent.replace(/\s+/g, " ").trim();
        if (!text) continue;
        const el = node.parentElement;
        if (el.closest(".visually-hidden")) continue;
        const cs = getComputedStyle(el);
        if (cs.visibility === "hidden" || cs.display === "none") continue;
        const range = document.createRange(); range.selectNodeContents(node);
        const rects = [...range.getClientRects()].filter((r) => r.width > 1 && r.height > 1);
        const lines = [];
        for (const r of rects) {
          const same = lines.find((l) => Math.abs(l.top - r.top) < 2);
          if (same) { same.left = Math.min(same.left, r.left); same.right = Math.max(same.right, r.right); same.bottom = Math.max(same.bottom, r.bottom); }
          else lines.push({ left: r.left, right: r.right, top: r.top, bottom: r.bottom });
        }
        const size = parseFloat(cs.fontSize), weight = parseInt(cs.fontWeight, 10);
        lines.forEach((l, i) => {
          if (l.right < hr.left || l.left > hr.right || l.bottom < hr.top || l.top > hr.bottom) return;
          const clip = clipOf(el);
          let state = "visible";
          if (clip) {
            if (l.bottom <= clip.hardTop || l.top >= clip.hardBottom) return;
            if (l.top < clip.top || l.bottom > clip.bottom) state = "scroll-edge";
          }
          out.push({ kind: "text", role, host: hostName, cls: el.className?.baseVal ?? el.className, text: lines.length > 1 ? `${text.slice(0, 40)} [line ${i + 1}]` : text.slice(0, 48), size, weight, large: size >= 24 || (size >= 18.66 && weight >= 700), color: cs.color, rgba: rgba(cs.color), rect: l, state });
        });
      }
      const input = host.querySelector("input.search-field");
      if (input && input.value === "") {
        const pcs = getComputedStyle(input, "::placeholder");
        const ir = input.getBoundingClientRect();
        const m = document.createElement("canvas").getContext("2d"); m.font = `${getComputedStyle(input).fontWeight} ${getComputedStyle(input).fontSize} ${getComputedStyle(input).fontFamily}`;
        const width = m.measureText(input.placeholder).width;
        const size = parseFloat(getComputedStyle(input).fontSize);
        out.push({ kind: "text", role, host: hostName, cls: "search-field::placeholder", text: input.placeholder, size, weight: 500, large: false, color: pcs.color, rgba: rgba(pcs.color), rect: { left: ir.left, right: ir.left + width, top: ir.top + ir.height / 2 - size * 0.62, bottom: ir.top + ir.height / 2 + size * 0.62 }, state: "visible" });
      }
      // Marks: the checkbox ring and the switch track are graphical objects in the ink colour
      // against the body (3:1); a glyph drawn ON a filled mark is measured against that fill.
      for (const mark of host.querySelectorAll(".task-mark, .switch")) {
        const cs = getComputedStyle(mark); const r = mark.getBoundingClientRect(); if (r.width < 2) continue;
        const clip = clipOf(mark);
        if (clip && (r.bottom <= clip.hardTop || r.top >= clip.hardBottom)) continue;
        out.push({ kind: "icon", role, host: hostName, cls: mark.className, text: `mark ${mark.className}`, size: r.height, weight: 0, large: true, color: cs.borderTopColor, rgba: rgba(cs.borderTopColor), rect: { left: r.left, right: r.right, top: r.top, bottom: r.bottom }, state: clip && (r.top < clip.top || r.bottom > clip.bottom) ? "scroll-edge" : "visible" });
      }
      for (const svg of host.querySelectorAll("svg")) {
        const cs = getComputedStyle(svg); if (cs.visibility === "hidden") continue;
        const fillEl = svg.closest(".task-mark");
        const fill = fillEl ? rgba(getComputedStyle(fillEl).backgroundColor) : null;
        const r = svg.getBoundingClientRect(); if (r.width < 2) continue;
        const clip = clipOf(svg);
        if (clip && (r.bottom <= clip.hardTop || r.top >= clip.hardBottom)) continue;
        out.push({ kind: "icon", role, host: hostName, fill, cls: svg.getAttribute("class") ?? svg.parentElement.className, text: `icon in ${svg.parentElement.className}`, size: r.height, weight: 0, large: true, color: cs.color, rgba: rgba(cs.color), rect: { left: r.left, right: r.right, top: r.top, bottom: r.bottom }, state: clip && (r.top < clip.top || r.bottom > clip.bottom) ? "scroll-edge" : "visible" });
      }
    }
    const bodies = [...document.querySelectorAll("[data-vitrea-node]")].map((h) => { const r = h.getBoundingClientRect(); return { role: h.getAttribute("data-glass-role"), host: h.getAttribute("aria-label") || h.querySelector("h2")?.textContent || h.className, rect: { left: r.left, top: r.top, right: r.right, bottom: r.bottom } }; });
    return { lines: out, bodies };
  });
}

function evaluate(png, item, dpr) {
  const x0 = Math.max(0, Math.floor(item.rect.left * dpr)), x1 = Math.min(png.width, Math.ceil(item.rect.right * dpr));
  const y0 = Math.max(0, Math.floor(item.rect.top * dpr)), y1 = Math.min(png.height, Math.ceil(item.rect.bottom * dpr));
  const px = [];
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { const i = (y * png.width + x) * 4; px.push([png.data[i], png.data[i + 1], png.data[i + 2]]); }
  if (!px.length) return null;
  px.sort((a, b) => lum(...a) - lum(...b));
  const pick = (q) => px[Math.min(px.length - 1, Math.max(0, Math.round(q * (px.length - 1))))];
  const [ir, ig, ib, ia] = item.rgba;
  if (item.fill) {
    // The glyph sits on a filled mark: its surface is that fill composited over the body.
    const [fr, fg, fb, fa] = item.fill;
    for (const p of px) { p[0] = fa * fr + (1 - fa) * p[0]; p[1] = fa * fg + (1 - fa) * p[1]; p[2] = fa * fb + (1 - fa) * p[2]; }
  }
  const cr = (s) => { const ink = [ia * ir + (1 - ia) * s[0], ia * ig + (1 - ia) * s[1], ia * ib + (1 - ia) * s[2]]; return ratio(lum(...ink), lum(...s)); };
  const med = pick(0.5), p10 = pick(0.1), p90 = pick(0.9);
  const rs = [cr(p10), cr(med), cr(p90)];
  const enc = (s) => (0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2]) / 255;
  return { median: +rs[1].toFixed(2), worst: +Math.min(...rs).toFixed(2), surface: +enc(med).toFixed(3), surfaceRange: [+enc(p10).toFixed(3), +enc(p90).toFixed(3)] };
}

function bodyLevel(png, b, dpr) {
  const inset = 28;
  const x0 = Math.floor((b.rect.left + inset) * dpr), x1 = Math.floor((b.rect.right - inset) * dpr), y0 = Math.floor((b.rect.top + inset) * dpr), y1 = Math.floor((b.rect.bottom - inset) * dpr);
  const v = [];
  for (let y = y0; y < y1; y += 2) for (let x = x0; x < x1; x += 2) { const i = (y * png.width + x) * 4; v.push((0.2126 * png.data[i] + 0.7152 * png.data[i + 1] + 0.0722 * png.data[i + 2]) / 255); }
  v.sort((a, b) => a - b);
  return v.length ? { p10: +v[Math.floor(v.length * 0.1)].toFixed(3), median: +v[Math.floor(v.length / 2)].toFixed(3), p90: +v[Math.floor(v.length * 0.9)].toFixed(3) } : null;
}

const browser = await gpuBrowser();
const results = [];
for (const tier of tiers) for (const scheme of schemes) for (const rt of rts) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, colorScheme: scheme, deviceScaleFactor: DPR });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(`http://localhost:5188/gallery/start-page/?at=${at}${tier === "css" ? "&tier=css" : ""}`);
  await page.waitForFunction(() => window.__vitrea && window.__glassDemo);
  if (rt) await page.evaluate(() => window.__glassDemo.setReducedTransparency(true));
  for (const phase of phases) for (const pose of poses) {
    await page.evaluate(({ phase, pose }) => { window.__glassDemo.setPhase(phase); window.__vitrea.setWindowActivation(pose); }, { phase, pose });
    await page.waitForTimeout(900); await frames(page, 4);
    for (const variant of variants) {
      // Prepare the variant.
      await page.evaluate((variant) => {
        const s = document.querySelector(".today-scroll");
        if (variant === "top" && s) s.scrollTop = 0;
        if (variant === "bottom" && s) s.scrollTop = s.scrollHeight;
      }, variant);
      if (variant === "search") { await page.fill(".search-field", "gi"); }
      if (variant === "platter") { await page.evaluate(() => window.__glassDemo.openMenu()); await page.waitForTimeout(900); }
      await page.waitForTimeout(350); await frames(page, 3);
      const data = await collect(page);
      if (shotDir) await page.screenshot({ path: `${shotDir}/${tier}-${scheme}-${rt ? "rt" : "std"}-${phase}-${pose}-${variant}.png` });
      await page.addStyleTag({ content: HIDE }).then((h) => page.evaluate((el) => { el.id = "__measure_hide"; }, h));
      await frames(page, 3);
      const png = decodePng(await page.screenshot());
      await page.evaluate(() => document.getElementById("__measure_hide")?.remove());
      const keep = (l) => variant === "rest" ? true : variant === "platter" ? l.role === "platter" : variant === "search" ? (l.host?.includes("Search") || l.host === "Places") : l.host === "Today";
      const state = { tier, scheme, rt: !!rt, phase, pose, variant };
      for (const b of data.bodies) results.push({ ...state, kind: "body", host: b.host, role: b.role, level: bodyLevel(png, b, DPR) });
      for (const l of data.lines.filter(keep)) {
        const e = evaluate(png, l, DPR); if (!e) continue;
        const floor = l.kind === "icon" || l.large ? 3 : 4.5;
        results.push({ ...state, kind: l.kind, role: l.role, host: l.host, cls: l.cls, text: l.text, size: l.size, weight: l.weight, color: l.color, floor, lineState: l.state, ...e, pass: e.worst >= floor });
      }
      // Undo the variant.
      if (variant === "search") await page.fill(".search-field", "");
      if (variant === "platter") { await page.keyboard.press("Escape"); await page.waitForTimeout(700); }
    }
  }
  if (errors.length) console.log("page errors", errors);
  await ctx.close();
}
await browser.close();
writeFileSync(outFile, JSON.stringify(results, null, 0));
// Summary
const lines = results.filter((r) => r.kind !== "body");
const gated = lines.filter((r) => r.lineState === "visible");
const fails = gated.filter((r) => !r.pass);
console.log(`lines measured ${lines.length}, gated ${gated.length}, failing ${fails.length}`);
const by = {};
for (const r of gated) { const k = `${r.tier}/${r.scheme}/${r.rt ? "rt" : "std"}/${r.phase}/${r.pose}`; (by[k] ??= []).push(r); }
for (const [k, rs] of Object.entries(by)) { const w = rs.reduce((a, b) => (b.worst / b.floor < a.worst / a.floor ? b : a)); console.log(`${k.padEnd(34)} n=${String(rs.length).padStart(3)} worst ${w.worst} (floor ${w.floor}) "${w.text}" [${w.host}/${w.cls}] surface ${w.surface}`); }
for (const f of fails.slice(0, 60)) console.log(`FAIL ${f.tier}/${f.scheme}/${f.rt ? "rt" : "std"}/${f.phase}/${f.pose}/${f.variant} ${f.worst}<${f.floor} med ${f.median} "${f.text}" [${f.host}/${f.cls}] ${f.size}px/${f.weight} surf ${f.surface} ${JSON.stringify(f.surfaceRange)} ink ${f.color}`);
const bodies = results.filter((r) => r.kind === "body" && r.variant === "rest");
for (const b of bodies) if (b.level) console.log(`body ${b.tier}/${b.scheme}/${b.rt ? "rt" : "std"}/${b.phase}/${b.pose} ${b.host.padEnd(12)} p10 ${b.level.p10} med ${b.level.median} p90 ${b.level.p90}`);
