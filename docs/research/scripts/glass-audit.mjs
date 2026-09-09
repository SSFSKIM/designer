#!/usr/bin/env node
// The mechanical audit for the Liquid Glass demos
// (docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-skill.md, "C. The audit").
//
//   node docs/research/scripts/glass-audit.mjs <demo-dir> [<demo-dir>…] [--port 8787]
//
// Renders each demo in Chromium over http://localhost with WebGPU reachable, captures the first
// viewport, the full page, two native-resolution tiles and — where the page offers one — the open
// menu and a reduced-transparency pass, and reads what actually drew: page errors, overflow taken
// from the capture's own width, the contrast sample, and the glass root's resolved state through
// devMode — the renderer and sampling backend per group, every diagnostic the runtime reported,
// and the count of glass surfaces. JSON goes to stdout and to `audit.json` beside the captures;
// the captures go into the demo directory. The rule reading and the quality reading are separate
// passes over these captures and are not this script's business.
//
// ## Two page conventions
//
// vitrea puts nothing on `window` — a page can hold a `GlassRoot` and the runtime leaves no global
// handle to it (checked against `packages/platform-web/src` at 0.14.0; the only thing it publishes
// outward is the `data-vitrea-*` attribute set of `host.ts`, which is public "because tests and dev
// tooling both read them"). So a demo that wants to be audited says so, in two lines:
//
//   window.__vitrea = root;                       // the GlassRoot, for state and diagnostics
//   window.__glassDemo = { openMenu: () => … };   // optional: open the menu or platter, for one capture
//
// A demo that assigns neither is still audited — the captures, the errors, the overflow and the
// contrast are all page-level reads — and reports `rootFound: false` for everything that needs the
// runtime. `apps/demo` is that case: it is a React app whose root lives inside `GlassProvider`, and
// it is the fixture this script's `rootFound: false` path was verified against.
//
// ## What is read through the root, and where
//
//   root.capabilities(groupId)   → GlassGroupState: activeRenderer, samplingBackend, refraction,
//                                  analysis, health, demotionReason, cssBody/cssTint/cssShadow
//                                  (packages/core/src/state.ts:47-114)
//   root.diagnostics.reported    → the PLATFORM channel: glass-inside-glass, glass-in-content-layer,
//                                  host-outside-plane, backdrop-root-broken, non-uniform-radii,
//                                  tint-unparseable, webgpu-*, proxy-* …
//                                  (packages/platform-web/src/diagnostics.ts)
//   root.scene.diagnostics.reported → the CORE channel: same-plane-overlap, tint-mixing,
//                                  variant-mixing, backdrop-hint-out-of-range, …
//                                  (packages/core/src/diagnostics.ts:42)
//   root.accessibility           → ResolvedAccessibilityPolicy, for the reduced pass
//   root.renderInput()           → per-surface geometry, for the surface inventory
//   [data-vitrea-node] in the DOM → the surface count and the group ids, without the root
//
// Two things the runtime gives no diagnostic for, so the audit derives them and says it did:
//
//  - **A missing hint.** A DOM-sampled group that declared neither `backdrop` nor a texture does not
//    adapt to its backdrop at all, and nothing is reported — the vanilla descriptor's tone field is
//    `backdrop`, so a group written with `hint:` silently lands here (research memo §2). Derived as
//    `analysis: "none"` on a group whose configured source is `dom`, and listed under
//    `derivedFindings` rather than under `diagnostics`.
//  - **Reduced transparency.** Playwright can emulate `prefers-reduced-motion`, `prefers-contrast`
//    and forced colours; it cannot emulate `prefers-reduced-transparency`, which is not Baseline and
//    which vitrea reports as `reduced-transparency-undetectable` where it cannot be queried. The
//    reduced pass therefore emulates reduced motion through the browser and asks the runtime for
//    reduced transparency through its own override API — `setAccessibilityOverrides`, the seam the
//    memo calls load-bearing precisely because the media query cannot be relied on.

import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");

const argv = process.argv.slice(2);
const portArg = argv.indexOf("--port");
const port = portArg === -1 ? 8787 : Number(argv[portArg + 1]);
const dirs = argv
  .filter((a, i) => !a.startsWith("--") && i !== portArg + 1)
  .map((d) => path.resolve(d));
if (dirs.length === 0) {
  console.error("usage: glass-audit.mjs <demo-dir> [<demo-dir>…] [--port 8787]");
  process.exit(1);
}

/* ------------------------------------------------------------------ the server */

const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8", ".map": "application/json; charset=utf-8",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".webp": "image/webp", ".avif": "image/avif", ".gif": "image/gif", ".ico": "image/x-icon",
  ".mp4": "video/mp4", ".webm": "video/webm", ".woff2": "font/woff2", ".woff": "font/woff",
  ".ttf": "font/ttf", ".wasm": "application/wasm", ".txt": "text/plain; charset=utf-8",
};

/**
 * A static server on the repo root, so that `/packages/core/dist/index.js`, the import map's other
 * half and the demo's own `index.html` all resolve from one origin. `http://localhost` is a secure
 * context, which is the whole reason this exists: `navigator.gpu` is undefined outside one and a
 * page opened from `file://` would not load an ES module at all (research memo §4).
 *
 * Range requests are answered because a demo whose live plane is a video needs 206 to seek; nothing
 * else here is more than a file read.
 */
function startServer() {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, "http://localhost");
    let file = path.join(repo, decodeURIComponent(url.pathname));
    if (!file.startsWith(repo)) { res.writeHead(403).end(); return; }
    let stat;
    try { stat = fs.statSync(file); } catch {
      // A missing favicon is the browser's own request, not the page's, and a 404 for it would
      // land in every demo's console-error list as a finding about the demo. Nothing else is
      // forgiven: a 404 the page asked for is a real result and travels as one.
      if (url.pathname === "/favicon.ico") { res.writeHead(204).end(); return; }
      res.writeHead(404).end("not found");
      return;
    }
    if (stat.isDirectory()) {
      file = path.join(file, "index.html");
      try { stat = fs.statSync(file); } catch { res.writeHead(404).end("not found"); return; }
    }
    const type = MIME[path.extname(file).toLowerCase()] ?? "application/octet-stream";
    const range = req.headers.range && /^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
    if (range) {
      const start = range[1] === "" ? Math.max(0, stat.size - Number(range[2])) : Number(range[1]);
      const end = range[1] === "" || range[2] === "" ? stat.size - 1 : Number(range[2]);
      res.writeHead(206, {
        "content-type": type, "accept-ranges": "bytes",
        "content-range": `bytes ${start}-${end}/${stat.size}`, "content-length": end - start + 1,
      });
      fs.createReadStream(file, { start, end }).pipe(res);
      return;
    }
    res.writeHead(200, {
      "content-type": type, "content-length": stat.size, "accept-ranges": "bytes",
      "cache-control": "no-store",
    });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve, reject) => {
    server.on("error", reject);
    server.listen(port, "127.0.0.1", () => resolve(server));
  });
}

/* ------------------------------------------------------------------ the browser */

/**
 * A Playwright module whose Chromium is actually installed, launched as the **full browser binary**
 * (`channel: "chromium"`). The bundled headless shell hands back a SwiftShader adapter and would
 * report a GPU tier that never touched a GPU — the repo's own `chromium-gpu` project takes the
 * channel for exactly that reason, with the same two Dawn flags.
 */
const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];

async function launch() {
  // The workspace's own pin first — it is the version the repo's browser cache was filled for, and
  // it ships as `@playwright/test` here rather than as bare `playwright`. An npx cache can hold a
  // newer Playwright than the browser cache has a binary for, so each candidate is test-launched
  // and a candidate that cannot produce the full binary is passed over rather than downgraded to.
  const cands = [process.env.PLAYWRIGHT_MODULE, "playwright", "@playwright/test"].filter(Boolean);
  const npx = path.join(process.env.HOME, ".npm/_npx");
  if (fs.existsSync(npx)) {
    for (const d of fs.readdirSync(npx)) {
      const p = path.join(npx, d, "node_modules/playwright");
      if (fs.existsSync(p)) cands.push(p);
    }
  }
  const require = createRequire(path.join(repo, "packages/platform-web/package.json"));
  const failures = [];
  for (const c of cands) {
    let m;
    try { m = require(c); } catch { continue; }
    try {
      const b = await m.chromium.launch({ channel: "chromium", args: GPU_ARGS });
      return { browser: b, module: c };
    } catch (e) { failures.push(`${c}: ${String(e.message).split("\n")[0]}`); }
  }
  throw new Error(
    "no Playwright module could launch channel:\"chromium\" — the full browser binary is what " +
    "produces a real WebGPU adapter, so install it (npx playwright install chromium) rather " +
    "than falling back to the headless shell's SwiftShader.\n  " + failures.join("\n  "),
  );
}

/* ------------------------------------------------------------------ the page reads */

/**
 * The contrast sample, ported from `docs/research/scripts/settling/measure.mjs` — that file is a
 * script with top-level side effects and exports nothing, so the extraction is carried here rather
 * than imported, and only the contrast half of it is: the ground, the accent, the hue count and the
 * font families belong to the settling measures, not to this one.
 *
 * The one addition is `onGlass`. A DOM composite walks background colours upward and cannot see
 * what the material drew, so a label on a WebGPU-tier surface has no readable background here at
 * all; on the CSS tier the host's own `background` is the runtime's and does read. Both are kept in
 * the sample and tagged, so a fail on glass is legible as a fail whose ground the DOM could not
 * confirm rather than as a silently clean number.
 */
function extractContrast() {
  const srgb = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const cv = document.createElement("canvas"); cv.width = cv.height = 1;
  const cx = cv.getContext("2d", { willReadFrequently: true });
  const cache = new Map();
  const parse = (s) => {
    if (!s || s === "transparent") return null;
    if (cache.has(s)) return cache.get(s);
    let out = null;
    const m = s.match(/^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)$/);
    if (m) out = { r: +m[1], g: +m[2], b: +m[3], a: m[4] == null ? 1 : +m[4] };
    else {
      cx.clearRect(0, 0, 1, 1); cx.fillStyle = "#000"; cx.fillStyle = s;
      if (cx.fillStyle !== "#000000" || /black|#000/i.test(s)) {
        cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data;
        out = { r: d[0], g: d[1], b: d[2], a: d[3] / 255 };
      }
    }
    cache.set(s, out); return out;
  };
  const lum = ({ r, g, b }) => 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b);
  const contrast = (a, b) => {
    const x = lum(a), y = lum(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  };
  const over = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1,
  });
  const visible = (el) => el.checkVisibility
    ? el.checkVisibility({ contentVisibilityAuto: true, visibilityProperty: true, opacityProperty: true })
    : true;
  const effectiveBg = (el) => {
    let acc = null, node = el;
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

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const texts = []; let t;
  while ((t = walker.nextNode())) {
    if (t.textContent.trim().length >= 2 && t.parentElement
      && !["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"].includes(t.parentElement.tagName)) {
      texts.push(t.parentElement);
    }
  }
  const uniq = [...new Set(texts)].filter(visible);
  const step = Math.max(1, Math.floor(uniq.length / 300));
  const sample = uniq.filter((_, i) => i % step === 0);
  let checked = 0, pass = 0, unknown = 0, onGlass = 0, onGlassPass = 0;
  const fails = [];
  for (const el of sample) {
    const cs = getComputedStyle(el);
    const fg = parse(cs.color); if (!fg) continue;
    const glass = !!el.closest("[data-vitrea-node]");
    const bg = effectiveBg(el);
    if (!bg) { unknown++; continue; }
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
    const large = size >= 24 || (size >= 18.66 && bold);
    const c = contrast(fg.a < 1 ? over(fg, bg) : fg, bg);
    const ok = c >= (large ? 3 : 4.5);
    checked++; if (ok) pass++;
    if (glass) { onGlass++; if (ok) onGlassPass++; }
    if (!ok && fails.length < 12) {
      fails.push({ text: el.textContent.trim().slice(0, 40), ratio: +c.toFixed(2), size, onGlass: glass });
    }
  }
  const text = document.body.innerText || "";
  return {
    contrast: {
      checked, pass, unknown, rate: checked ? +(pass / checked).toFixed(3) : null,
      onGlass, onGlassPass, fails,
    },
    overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
    placeholder: /lorem ipsum|placeholder text|\bTODO\b|\bTBD\b/i.test(text),
    docHeight: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
    words: text.split(/\s+/).filter(Boolean).length,
    title: document.title,
  };
}

/**
 * Everything the resolved runtime knows about itself, read through `window.__vitrea`.
 *
 * The group ids come from the DOM's own `data-vitrea-group` markers first, so a root whose frame
 * loop has not produced a `renderInput()` yet still yields a full per-group state table; the render
 * input, when there is one, adds the surface geometry and any group with no registered host.
 */
function readGlass() {
  const root = window.__vitrea;
  const input = (() => { try { return root?.renderInput?.(); } catch { return undefined; } })();
  // The shape a surface was REGISTERED with, which is the one the size family is read against. The
  // DOM's own `border-radius` is only the CSS tier's; a WebGPU-tier surface draws its capsule on
  // the optics canvas and leaves the element square, so the element cannot be asked.
  const frameNodes = (input?.planes ?? []).flatMap((p) => p.nodes);
  const nodes = [...document.querySelectorAll("[data-vitrea-node]")];
  const surfaces = nodes.map((el, i) => {
    const r = el.getBoundingClientRect();
    const n = frameNodes.find(
      (x) => Math.abs(x.bounds.x - r.x) < 1 && Math.abs(x.bounds.y - r.y) < 1
        && Math.abs(x.bounds.width - r.width) < 1,
    ) ?? frameNodes[i];
    return {
      nodeId: el.getAttribute("data-vitrea-node"),
      groupId: el.getAttribute("data-vitrea-group"),
      plane: el.getAttribute("data-vitrea-host-plane"),
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute("role"),
      rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      /** The size law's input: it is exactly inert below 32 CSS px (research memo §2). */
      span: Math.round(Math.min(r.width, r.height)),
      shapeFamily: n?.shapeFamily ?? null,
      radii: n?.radii ? [...n.radii] : null,
      smoothing: n?.smoothing ?? null,
      thickness: n?.thickness ?? null,
      cssRadius: getComputedStyle(el).borderTopLeftRadius,
      label: (el.getAttribute("aria-label") ?? el.textContent ?? "").trim().slice(0, 40),
    };
  });
  if (!root) {
    return {
      rootFound: false, surfaces: surfaces.length, surfaceDetail: surfaces,
      groups: [], diagnostics: [], derivedFindings: surfaces.length > 0
        ? ["no-root-handle: the page has vitrea surfaces but never assigned window.__vitrea"]
        : [],
    };
  }

  const diag = (channel, origin) => (channel?.reported ?? []).map((d) => ({
    origin, code: d.code, severity: d.severity, subjects: [...(d.subjects ?? [])],
    message: String(d.message ?? "").slice(0, 220),
  }));
  const diagnostics = [
    ...diag(root.diagnostics, "platform"),
    ...diag(root.scene?.diagnostics, "core"),
  ];

  const ids = new Set(surfaces.map((s) => s.groupId).filter(Boolean));
  for (const g of input?.groups ?? []) ids.add(g.groupId);

  const groups = [...ids].map((id) => {
    const state = root.capabilities?.(id);
    const ri = (input?.groups ?? []).find((g) => g.groupId === id);
    const members = surfaces.filter((s) => s.groupId === id);
    return {
      id,
      members: members.length,
      state: state ? { ...state } : null,
      backdropSourceId: ri?.backdropSourceId ?? null,
      variant: ri?.variant ?? null,
      samplingPadding: ri?.samplingPadding ?? null,
      blurRadius: ri?.blurRadius == null ? null : +ri.blurRadius.toFixed(2),
      hasBackdropTone: ri?.backdropTone !== undefined,
      probeVerdict: (() => { try { return root.probeReport?.(id)?.verdict ?? null; } catch { return null; } })(),
      // A diagnostic names whichever subject it is about, and most of them are about a NODE rather
      // than the group — `glass-inside-glass` names the two hosts, `same-plane-overlap` names the
      // overlapping pair. Matching on the group id alone would leave every per-group list empty
      // while the page-level list was full.
      diagnostics: [...new Set(diagnostics
        .filter((d) => d.subjects.some((s) => s === id || members.some((m) => m.nodeId === s)))
        .map((d) => d.code))],
    };
  });

  // The findings the runtime has no code for. A DOM-sampled group at `analysis: "none"` declared
  // neither a `backdrop` hint nor a texture, so it does not adapt to its backdrop on either tier
  // and nothing is reported (research memo §2); it is the vanilla path's easiest mistake, because
  // the descriptor field is `backdrop` and `hint:` is silently ignored.
  const derivedFindings = [];
  for (const g of groups) {
    if (!g.state) { derivedFindings.push(`no-state:${g.id}`); continue; }
    if (g.state.configuredSource === "dom" && g.state.analysis === "none") {
      derivedFindings.push(`missing-hint:${g.id}`);
    }
    if (g.state.health === "demoted") {
      derivedFindings.push(`demoted:${g.id}:${g.state.demotionReason ?? "unnamed"}`);
    }
  }

  const nodeCount = (input?.planes ?? []).reduce((n, p) => n + p.nodes.length, 0);
  return {
    rootFound: true,
    surfaces: surfaces.length,
    surfacesInFrame: input ? nodeCount : null,
    surfaceDetail: surfaces,
    planes: (input?.planes ?? []).map((p) => ({ plane: p.plane, nodes: p.nodes.length })),
    colorScheme: root.colorScheme ?? null,
    // The status without the `GPUDevice` itself, which serialises to `{}` and says nothing.
    webgpu: root.webgpu
      ? {
        available: root.webgpu.available ?? null, ownership: root.webgpu.ownership ?? null,
        deviceHealth: root.webgpu.deviceHealth ?? null, reason: root.webgpu.reason ?? null,
        hasDevice: root.webgpu.device !== undefined,
      }
      : null,
    accessibility: root.accessibility ? { ...root.accessibility } : null,
    groups,
    diagnostics,
    derivedFindings,
  };
}

/** The seven codes the audit calls out by name; the rest travel in `diagnostics` untouched. */
const NAMED = {
  nestedGlass: "glass-inside-glass",
  samePlaneOverlap: "same-plane-overlap",
  contentLayerHost: "glass-in-content-layer",
  demotedBackdropRoot: "backdrop-root-broken",
  hostOutsidePlane: "host-outside-plane",
  nonUniformRadii: "non-uniform-radii",
  tintUnparseable: "tint-unparseable",
};

/* ------------------------------------------------------------------ one demo */

async function auditOne(browser, dir) {
  const rel = path.relative(repo, dir);
  const url = `http://127.0.0.1:${port}/${rel.split(path.sep).join("/")}/index.html`;
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1,
  });
  const errors = [], consoleErrors = [], consoleWarnings = [], failedRequests = [];
  page.on("pageerror", (e) => errors.push(String(e.message || e).slice(0, 240)));
  page.on("console", (m) => {
    const line = m.text().slice(0, 240);
    if (m.type() === "error") consoleErrors.push(line);
    else if (m.type() === "warning") consoleWarnings.push(line);
  });
  page.on("requestfailed", (r) => failedRequests.push(r.url().slice(0, 140)));

  await page.goto(url, { waitUntil: "load" });
  // The fixed capture protocol (imagery-check.mjs, settling/measure.mjs): fonts settled, the first
  // viewport taken at scroll 0 BEFORE any walk — a page that scrolls itself during the walk
  // otherwise photographs its own second screen — then the walk for lazy and reveal-on-scroll
  // content, the full page, and two native-resolution tiles. 1500 ms is the settling wait, and it
  // is also long enough for the WebGPU handshake; `ready()` is awaited where a root is reachable.
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1500);
  const readyState = await page.evaluate(async () => {
    if (!window.__vitrea?.ready) return "no-root";
    try { await window.__vitrea.ready(); return "settled"; } catch (e) { return "ready-threw: " + e.message; }
  });
  const scrolledOnLoad = await page.evaluate(() => { const y = window.scrollY; window.scrollTo(0, 0); return y; });
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(dir, "shot-fv.png"), fullPage: false });

  await page.evaluate(async () => {
    await new Promise((res) => {
      let y = 0;
      const step = () => {
        window.scrollTo(0, y);
        y += Math.round(window.innerHeight * 0.75);
        if (y < document.body.scrollHeight) setTimeout(step, 90);
        else { window.scrollTo(0, 0); setTimeout(res, 300); }
      };
      step();
    });
  });
  await page.waitForTimeout(400);

  const measured = await page.evaluate(extractContrast);
  const glass = await page.evaluate(readGlass);
  await page.screenshot({ path: path.join(dir, "shot-full.png"), fullPage: true });
  for (const n of [2, 3]) {
    const y = (n - 1) * 900, tile = path.join(dir, `tile-${n}.png`);
    if (measured.docHeight > y + 100) {
      await page.screenshot({
        path: tile, fullPage: true,
        clip: { x: 0, y, width: 1440, height: Math.min(900, measured.docHeight - y) },
      });
    } else if (fs.existsSync(tile)) fs.unlinkSync(tile);
  }

  // The transient platter, where the page offers a way to open one. A menu that morphs out of the
  // control that opened it is the language's own move, and it is the one state the resting captures
  // cannot show.
  const menuPath = path.join(dir, "shot-menu.png");
  let menu = "not-offered";
  const hasMenu = await page.evaluate(() => typeof window.__glassDemo?.openMenu === "function");
  if (hasMenu) {
    try {
      await page.evaluate(() => window.__glassDemo.openMenu());
      await page.waitForTimeout(600);
      await page.screenshot({ path: menuPath, fullPage: false });
      menu = "captured";
    } catch (e) { menu = "openMenu threw: " + String(e.message).slice(0, 160); }
  } else if (fs.existsSync(menuPath)) fs.unlinkSync(menuPath);
  const menuGlass = menu === "captured" ? await page.evaluate(readGlass) : null;
  await page.close();

  // Overflow read from the capture itself rather than from the load-time scrollWidth: a page can be
  // 1440 wide at load and wider once its content has revealed.
  const png = fs.readFileSync(path.join(dir, "shot-full.png"));
  const captureWidth = png.readUInt32BE(16);

  const reduced = await reducedPass(browser, dir, url);

  const codes = new Set(glass.diagnostics.map((d) => d.code));
  const named = Object.fromEntries(
    Object.entries(NAMED).map(([k, code]) => [k, codes.has(code)]),
  );
  const groupSummary = glass.groups.map((g) => ({
    id: g.id, members: g.members,
    renderer: g.state?.activeRenderer ?? null,
    sampling: g.state?.samplingBackend ?? null,
    analysis: g.state?.analysis ?? null,
    refraction: g.state?.refraction ?? null,
    health: g.state?.health ?? null,
    demotionReason: g.state?.demotionReason ?? null,
    cssBody: g.state?.cssBody ?? null,
    cssTint: g.state?.cssTint ?? null,
    cssShadow: g.state?.cssShadow ?? null,
    diagnostics: g.diagnostics,
  }));

  return {
    dir: path.basename(dir), url, auditedAt: new Date().toISOString(),
    rootFound: glass.rootFound,
    readyState,
    errors, consoleErrors: consoleErrors.slice(0, 10), failedRequests: failedRequests.length,
    captureWidth, overflowCapture: captureWidth > 1440, overflowAtLoad: measured.overflow,
    scrolledOnLoad, docHeight: measured.docHeight, words: measured.words, title: measured.title,
    placeholder: measured.placeholder,
    contrast: measured.contrast,
    surfaces: glass.surfaces,
    surfacesInFrame: glass.surfacesInFrame ?? null,
    planes: glass.planes ?? [],
    colorScheme: glass.colorScheme ?? null,
    webgpu: glass.webgpu ?? null,
    groups: groupSummary,
    diagnostics: glass.diagnostics,
    named,
    derivedFindings: glass.derivedFindings,
    menu, menuSurfaces: menuGlass?.surfaces ?? null,
    // The platter is a second group on the overlay plane and it resolves its own tier; a menu that
    // demoted while the bar behind it did not is exactly what the resting captures cannot show.
    menuGroups: menuGlass
      ? menuGlass.groups.map((g) => ({
        id: g.id, members: g.members, renderer: g.state?.activeRenderer ?? null,
        sampling: g.state?.samplingBackend ?? null, health: g.state?.health ?? null,
      }))
      : null,
    // The same shape as the resting `diagnostics` (code, subjects, message), minus what was
    // already reported at rest: a menu-pass diagnostic is about the platter's arrival.
    menuDiagnostics: menuGlass
      ? menuGlass.diagnostics.filter((d) => !glass.diagnostics.some((p) => p.code === d.code
        && p.subjects.join() === d.subjects.join()))
      : null,
    reduced,
    captures: ["shot-fv.png", "shot-full.png", "tile-2.png", "tile-3.png", "shot-menu.png",
      "shot-reduced.png"].filter((f) => fs.existsSync(path.join(dir, f))),
    surfaceDetail: glass.surfaceDetail,
    gateMechanical: errors.length === 0 && captureWidth <= 1440 && !measured.placeholder
      && (measured.contrast.rate == null || measured.contrast.rate >= 0.9),
  };
}

/**
 * The reduced pass: a fresh load under emulated reduced motion, then reduced transparency asked for
 * through the runtime's override API, because no browser lets a driver emulate that media query.
 * What it has to show is that the page still works — no page error — and that the material actually
 * moved: `frost: "increased"`, `refraction: "reduced"`, `occlusion: "increased"` are the three axes
 * reduced transparency changes (packages/core/src/accessibility.ts).
 */
async function reducedPass(browser, dir, url) {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1,
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e.message || e).slice(0, 240)));
  await page.emulateMedia({ reducedMotion: "reduce" });
  try {
    await page.goto(url, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(1200);
    const applied = await page.evaluate(() => {
      const root = window.__vitrea;
      if (!root) return { rootFound: false, honoured: null };
      const before = { ...root.accessibility };
      if (typeof root.setAccessibilityOverrides !== "function") {
        return { rootFound: true, honoured: false, why: "no setAccessibilityOverrides" };
      }
      root.setAccessibilityOverrides({ reducedTransparency: true });
      return { rootFound: true, before, honoured: "pending" };
    });
    // The override takes effect on the next frame, which is where both tiers read the material.
    await page.waitForTimeout(500);
    const after = await page.evaluate(() => {
      const root = window.__vitrea;
      if (!root) return null;
      const nodes = [...document.querySelectorAll("[data-vitrea-node]")];
      const ids = [...new Set(nodes.map((el) => el.getAttribute("data-vitrea-group")))];
      return {
        accessibility: { ...root.accessibility },
        groups: ids.map((id) => {
          const s = root.capabilities?.(id);
          return {
            id, renderer: s?.activeRenderer ?? null, refraction: s?.refraction ?? null,
            cssBody: s?.cssBody ?? null,
          };
        }),
        reducedTransparencyUndetectable: (root.scene?.diagnostics?.reported ?? [])
          .some((d) => d.code === "reduced-transparency-undetectable"),
      };
    });
    await page.screenshot({ path: path.join(dir, "shot-reduced.png"), fullPage: false });
    await page.close();
    const m = after?.accessibility?.material;
    return {
      rootFound: applied.rootFound,
      errors,
      reducedMotionEmulated: true,
      overrideHonoured: applied.rootFound
        ? Boolean(after?.accessibility?.reducedTransparency)
        : null,
      materialMoved: m
        ? m.frost === "increased" && m.refraction === "reduced" && m.occlusion === "increased"
        : null,
      material: m ?? null,
      motion: after?.accessibility?.motion ?? null,
      groups: after?.groups ?? [],
      reducedTransparencyUndetectable: after?.reducedTransparencyUndetectable ?? null,
      ok: errors.length === 0,
    };
  } catch (e) {
    await page.close().catch(() => {});
    return { rootFound: null, errors: [...errors, String(e.message).slice(0, 240)], ok: false };
  }
}

/* ------------------------------------------------------------------ run */

const server = await startServer();
const { browser, module } = await launch();
console.error(`glass-audit: playwright ${module}, serving ${repo} on http://127.0.0.1:${port}`);
const out = [];
for (const dir of dirs) {
  if (!fs.existsSync(path.join(dir, "index.html"))) {
    out.push({ dir: path.basename(dir), error: "no index.html", gateMechanical: false });
    continue;
  }
  process.stderr.write(`audit ${path.basename(dir)} … `);
  try {
    const r = await auditOne(browser, dir);
    fs.writeFileSync(path.join(dir, "audit.json"), JSON.stringify(r, null, 1) + "\n");
    out.push(r);
    console.error(r.gateMechanical ? "ok" : "gate-fail");
  } catch (e) {
    console.error("ERROR " + e.message);
    out.push({ dir: path.basename(dir), error: String(e.message).slice(0, 400), gateMechanical: false });
  }
}
await browser.close();
server.close();
process.stdout.write(JSON.stringify(out, null, 1) + "\n");
