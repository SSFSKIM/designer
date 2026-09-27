// Shared measurement for the clear-variant comparison. Line enumeration, the glyph-suppressed
// surface and the 10/50/90 gate are the maker's (review/start-page-maker-contrast/measure.mjs).
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
const require = createRequire("/Users/new/Developer/GitHub/designer/apps/demo/package.json");
export const { chromium } = require("@playwright/test");
export const { PNG } = require("pngjs");
export const PORT = 5191;
export async function gpuBrowser() {
  return chromium.launch({ channel: "chromium", args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"] });
}
export const frames = (page, n = 2) => page.evaluate((n) => new Promise((r) => { let k = 0; const f = () => (++k >= n ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }), n);
export const sha = (b) => createHash("sha256").update(b).digest("hex").slice(0, 16);
const dec = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const lum = (r, g, b) => 0.2126 * dec(r) + 0.7152 * dec(g) + 0.0722 * dec(b);
const ratio = (a, b) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);

export const CARET = "* { caret-color: transparent !important; }";
export const HIDE = `
[data-vitrea-node] *, [data-vitrea-node] { color: transparent !important; -webkit-text-fill-color: transparent !important; caret-color: transparent !important; text-decoration-color: transparent !important; }
[data-vitrea-node] ::placeholder { color: transparent !important; }
[data-vitrea-node] svg { visibility: hidden !important; }
[data-vitrea-node] .task-mark, [data-vitrea-node] .switch { visibility: hidden !important; }
[data-vitrea-node] *:focus-visible { outline-color: transparent !important; }
`;

export async function collect(page) {
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
      // The checked switch's knob, a mark drawn ON the ink-filled track: against that fill.
      for (const knob of host.querySelectorAll('.setting[aria-checked="true"] .switch-knob')) {
        const track = knob.parentElement; const r = knob.getBoundingClientRect(); if (r.width < 2) continue;
        out.push({ kind: "icon", role, host: hostName, fill: rgba(getComputedStyle(track).backgroundColor), cls: "switch-knob (on)", text: `knob on ${knob.closest(".setting").querySelector(".setting-label").textContent}`, size: r.height, weight: 0, large: true, color: getComputedStyle(knob).backgroundColor, rgba: rgba(getComputedStyle(knob).backgroundColor), rect: { left: r.left, right: r.right, top: r.top, bottom: r.bottom }, state: "visible" });
      }
    }
    return out;
  });
}

export function evaluate(png, item, dpr) {
  const x0 = Math.max(0, Math.floor(item.rect.left * dpr)), x1 = Math.min(png.width, Math.ceil(item.rect.right * dpr));
  const y0 = Math.max(0, Math.floor(item.rect.top * dpr)), y1 = Math.min(png.height, Math.ceil(item.rect.bottom * dpr));
  const px = [];
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { const i = (y * png.width + x) * 4; px.push([png.data[i], png.data[i + 1], png.data[i + 2]]); }
  if (!px.length) return null;
  px.sort((a, b) => lum(...a) - lum(...b));
  const pick = (q) => px[Math.min(px.length - 1, Math.max(0, Math.round(q * (px.length - 1))))];
  const [ir, ig, ib, ia] = item.rgba;
  if (item.fill) {
    const [fr, fg, fb, fa] = item.fill;
    for (const p of px) { p[0] = fa * fr + (1 - fa) * p[0]; p[1] = fa * fg + (1 - fa) * p[1]; p[2] = fa * fb + (1 - fa) * p[2]; }
  }
  const cr = (s) => { const ink = [ia * ir + (1 - ia) * s[0], ia * ig + (1 - ia) * s[1], ia * ib + (1 - ia) * s[2]]; return ratio(lum(...ink), lum(...s)); };
  const med = pick(0.5), p10 = pick(0.1), p90 = pick(0.9);
  const rs = [cr(p10), cr(med), cr(p90)];
  const enc = (s) => (0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2]) / 255;
  return { median: +rs[1].toFixed(2), worst: +Math.min(...rs).toFixed(2), surface: +enc(med).toFixed(3), surfaceRange: [+enc(p10).toFixed(3), +enc(p90).toFixed(3)] };
}

/** Everything the runtime says about the page, plus the hint-against-canvas check. */
export async function fingerprint(page) {
  return page.evaluate(async () => {
    const c = document.querySelector("canvas.environment");
    const cx = c.getContext("2d");
    const all = cx.getImageData(0, 0, c.width, c.height).data;
    const h = new Uint8Array(await crypto.subtle.digest("SHA-256", all));
    const root = window.__vitrea;
    const dec = (v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
    const sx = c.width / innerWidth, sy = c.height / innerHeight, step = Math.min(2, devicePixelRatio) >= 2 ? 2 : 1;
    const hostOf = { now: 'section[aria-label="Now"]', places: "section.places", today: "section.today", search: "form.search", photograph: ".photograph-morph" };
    const groups = {};
    for (const id of Object.keys(hostOf)) {
      const g = root.scene.glassGroup(id);
      const el = document.querySelector(hostOf[id]);
      const r = el.getBoundingClientRect();
      const x0 = Math.max(0, Math.floor(r.x * sx)), y0 = Math.max(0, Math.floor(r.y * sy)), x1 = Math.min(c.width, Math.ceil((r.x + r.width) * sx)), y1 = Math.min(c.height, Math.ceil((r.y + r.height) * sy));
      let R = 0, G = 0, B = 0, n = 0;
      for (let y = y0; y < y1; y += step) for (let x = x0; x < x1; x += step) { const i = (y * c.width + x) * 4; R += all[i]; G += all[i + 1]; B += all[i + 2]; n++; }
      const canvasLum = 0.2126 * dec(R / n / 255) + 0.7152 * dec(G / n / 255) + 0.0722 * dec(B / n / 255);
      groups[id] = { backdrop: g.descriptor.backdrop, material: g.descriptor.material ?? null, caps: root.capabilities(id), canvasLum: +canvasLum.toFixed(4), hintDelta: g.descriptor.backdrop ? +(canvasLum - g.descriptor.backdrop.luminance).toFixed(4) : null, rect: [r.x, r.y, r.width, r.height].map(Math.round) };
    }
    const input = root.renderInput();
    const nodes = input ? input.planes.flatMap((p) => p.nodes.map((n) => ({ node: n.nodeId, group: n.groupId, variant: n.material.variant, adaptation: n.material.adaptation, dimming: n.material.dimming ?? null, blurSigma: n.optics?.blurSigma, tintAlpha: n.optics?.tintAlpha }))) : null;
    const groupInputs = input ? input.groups.map((g) => ({ group: g.groupId, variant: g.variant, samplingPadding: +g.samplingPadding.toFixed(2) })) : null;
    const diags = [...root.diagnostics.reported, ...root.scene.diagnostics.reported].map((e) => ({ code: e.code, message: e.message ?? "" }));
    const inks = {};
    for (const id of Object.keys(hostOf)) { const el = document.querySelector(hostOf[id]); inks[id] = getComputedStyle(el).getPropertyValue("--vitrea-foreground").trim(); }
    return { canvas: [...h.slice(0, 8)].map((b) => b.toString(16).padStart(2, "0")).join(""), canvasSize: [c.width, c.height], groups, nodes, groupInputs, diags, inks, url: location.search, glassAttr: document.documentElement.dataset.glass ?? null };
  });
}

/** One state: fingerprint, a normal screenshot, then the glyph-suppressed one and its lines. */
export async function measureState(page, { keep, dpr = 1, shot }) {
  await frames(page, 3);
  const fp = await fingerprint(page);
  const normal = await page.screenshot();
  if (shot) (await import("node:fs")).writeFileSync(shot, normal);
  const items = await collect(page);
  const tag = await page.addStyleTag({ content: HIDE });
  await frames(page, 3);
  const png = PNG.sync.read(await page.screenshot());
  await tag.evaluate((el) => el.remove());
  await frames(page, 2);
  const lines = [];
  for (const l of items.filter(keep)) {
    const e = evaluate(png, l, dpr); if (!e) continue;
    const floor = l.kind === "icon" || l.large ? 3 : 4.5;
    lines.push({ kind: l.kind, role: l.role, host: l.host, cls: l.cls, text: l.text, size: l.size, weight: l.weight, color: l.color, floor, lineState: l.state, ...e, pass: e.worst >= floor });
  }
  return { fp, pixels: sha(PNG.sync.read(normal).data), lines };
}
export const keepFor = (state) => (l) => (state === "platter" ? l.role === "platter" : true);
