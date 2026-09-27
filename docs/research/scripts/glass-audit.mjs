#!/usr/bin/env node
// The mechanical audit for the materialist demos
// (docs/doperpowers/specs/2026-09-27-materialist-proof.md, "B. The instrument", reading 1).
//
//   node docs/research/scripts/glass-audit.mjs <url> [<url>…] --out <dir> [--slug <a,b,…>]
//                                              [--audit-dir <dir>]
//
// Renders each page in Chromium with WebGPU on a real adapter and reads what actually drew. The
// caller serves the pages; this script starts no server. The demo site's is
// `cd apps/demo && npx vite --port 5177 --strictPort`, and a gallery page is then
// `http://localhost:5177/gallery/<slug>/`. A page's slug is its URL's last path segment
// (`/gallery/music-player/` → `music-player`, an `index.html` passed over) unless `--slug` names
// it, one slug per URL in order. Captures and `audit.json` go to `<out>/<slug>/`, the whole run to
// `<out>/run-<timestamp>.json`, and with `--audit-dir` each audit is also written to
// `<audit-dir>/<slug>.json`, which is where `glass-rules-analyze.py` reads it from. A summary goes
// to stdout.
//
// Per page, the run is seven fresh browser contexts, so a preference one pass sets (a page that
// persists its reduced-transparency switch, say) cannot leak into the next:
//
//  - **Two scheme passes**, under `emulateMedia({ colorScheme })` light and then dark. The spec's
//    audit contract has the page's tokens follow `prefers-color-scheme` and the root on
//    `colorScheme="auto"`, so one emulation flips both halves, and the pass records whether the
//    root's resolved `colorScheme` did follow. Each captures the first viewport, the full page,
//    the second and third screens and the open menu (`shot-fv-<scheme>.png`, `shot-full-…`,
//    `tile-2-…`, `tile-3-…`, `shot-menu-…`), and reads page errors, console errors, failed and
//    ≥ 400 requests, overflow from the full capture's width, both contrast samples, the resolved
//    state of every group, every diagnostic on both channels, the surface inventory and the ban
//    subset.
//  - **The reduced-transparency pass**, light scheme: the page's own switch
//    `window.__glassDemo.setReducedTransparency(true)` where the page offers one, which is what
//    the materialist asks a page to carry, and otherwise the runtime's
//    `setAccessibilityOverrides({ reducedTransparency: true })`. The pass says which it used,
//    captures `shot-reduced.png`, and records whether the resolved policy changed and whether each
//    group's material moved. No browser lets a driver emulate `prefers-reduced-transparency`,
//    which is why the switch exists at all.
//  - **Three emulation passes**, light scheme: `contrast: "more"`, `reducedMotion: "reduce"` and
//    `forcedColors: "active"`, each checked against `matchMedia` so an option the installed
//    Playwright ignores reads `not-applied` rather than passing silently, and one it rejects reads
//    `unsupported`. Each reports errors, the accessibility policy the runtime resolved and whether
//    it is the one asked for; increased contrast captures `shot-contrast.png`, and forced colours
//    captures `shot-forced.png` and counts the glass still drawn, which must be zero.
//
// ## Two page conventions
//
// vitrea puts nothing on `window`: a page holds its `GlassRoot` and the runtime leaves no global
// handle to it; the only thing it publishes outward is the `data-vitrea-*` attribute set of
// `host.ts` (public "because tests and dev tooling both read them") and the `data-vitrea-root`
// marker on the root element. So a demo that wants to be audited says so, as the spec's audit
// contract asks:
//
//   window.__vitrea = root;       // the GlassRoot; in React, useGlassRootHandle().root, mounted
//   window.__glassDemo = {
//     openMenu,                   // optional: open the menu or platter, one capture per scheme
//     setReducedTransparency,     // the page's own switch, for the reduced pass
//   };
//
// A page that assigns neither is still audited — captures, errors, overflow, both contrast
// samples, the DOM-derived inventory and the CSS half of the ban subset are page-level reads — and
// reports `rootFound: false` for everything that needs the runtime. The site's own `/laws/` page is
// that case (its root lives inside `GlassRoot` and is never exposed) and is the fixture the
// `rootFound: false` path was exercised on.
//
// ## What is read through the root, and where (0.24.0)
//
//   root.capabilities(groupId)   → GlassGroupState: activeRenderer, samplingBackend, refraction,
//                                  analysis, health, demotionReason, cssBody/cssTint/cssShadow,
//                                  materialDocument {name, platform, profileKey,
//                                  resolvedMaterialSha256, tuned} (packages/core/src/state.ts)
//   root.probeReport(groupId)    → GroupProbeReport: verdict, breaks, engineDefects, reach
//   root.diagnostics.reported    → the PLATFORM channel (packages/platform-web/src/diagnostics.ts)
//   root.scene.diagnostics.reported → the CORE channel (packages/core/src/diagnostics.ts)
//   root.accessibility           → ResolvedAccessibilityPolicy (packages/core/src/accessibility.ts)
//   root.renderInput()           → per-surface bounds, shape, material (variant, tint) and optics
//                                  (blurRadius, tintAlpha: the occlusion knob, under the policy)
//   root.setAccessibilityOverrides, root.material, root.colorScheme, root.windowActivation,
//   root.webgpu {available, deviceHealth, ownership, unavailableReason}, root.platformProbe
//   [data-vitrea-node], [data-vitrea-root] in the DOM → the inventory and the ban subset,
//                                  without the root
//
// Checked against `packages/platform-web/src/root.ts` at 0.24.0 when this was ported from the
// 0.14.0 script (f13ab38c). The one rename on this surface is `webgpu.reason` →
// `webgpu.unavailableReason`; the rest held, and `material` and `windowActivation` are new since.
// Every run re-checks the names on the live object (`api.missing`), and at start-up checks the
// diagnostic codes this script names against the two code lists in source, so drift fails loudly.
//
// ## Two contrast samples
//
// `contrast` is the 2.3 audit's DOM sample, kept as it was: every visible text element's colour
// against its composited ancestor backgrounds, tagged `onGlass`. It cannot see what the material
// drew — a WebGPU-tier body is on a canvas and the walk lands on the page ground behind it — so
// it is a page-level reading. `glassContrast` is the reading the spec's r18 asks for, taken on
// rendered pixels: for every text run inside a glass host on screen in the first viewport, the
// two tiles and the open menu, the label's computed colour against the median of the captured
// pixels behind its line boxes that are not the ink, with the worst decile of that ground beside
// it. It is sampled in both schemes, which is the whole of r18's "in both light and dark".
//
// ## The ban subset (skills/materialist/SKILL.md §7, "Mechanical subset")
//
// Reported under `banSubset.findings`, each with the element's selector path:
//
//  - `authored-host-style`: a painting `background`, `border`, `box-shadow` or `backdrop-filter`
//    on a registered host. The CSS tier writes its own values for exactly these properties inline
//    on the host (css-tier.ts, `cssTierDeclarations().host`), so on a host that carries its
//    `--vitrea-occlusion` token those inline writes are lifted for one synchronous read and put
//    back byte for byte; the WebGPU tier writes only custom properties, `transform` and
//    `pointer-events`, and its hosts are read as they stand. A reset (a transparent background,
//    `border: 0`) paints nothing and is not a finding, which is the skill's one allowed
//    background. A value equal to the user agent's default for that element is labelled
//    `user-agent` and counted only where the runtime does not overwrite it — a native button's
//    grey face left on a WebGPU-tier host is on screen, the same face under the CSS tier is not.
//  - `content-role-on-glass`: a list, listitem, row, table or article role on a host, explicit or
//    implicit from `ul`, `ol`, `menu`, `li`, `tr`, `table` or `article`.
//  - `two-tint-hues`: two tint seeds more than 20° of hue apart resolving in one sampling group,
//    read from `renderInput()`; without the root the tint is not on the DOM and it is unmeasured.
//  - `opacity-motion-on-host` / `opacity-motion-on-root-ancestor`: an `opacity` (or `all`)
//    transition with a duration, a CSS animation whose keyframes set opacity, or a running
//    animation that does.
//  - `root-ancestor-effect`: `filter`, `backdrop-filter`, `opacity < 1`, `mask-image`,
//    `clip-path` or `mix-blend-mode` on any ancestor of a `[data-vitrea-root]`.
//  - `span-under-32`: a surface whose shorter span is under 32 CSS px. The family's deliberate
//    exceptions are the page record's to argue; the audit cannot see them and reports every one.
//
// The ban read runs at rest and again with the menu open, in both schemes, and findings are merged.
// A running animation is seen only if it is running at the read; that and cross-origin stylesheets
// (whose keyframes cannot be read) are the limits, and the latter are counted in `unmeasured`.
// Every kind above was seen to fire, on both tiers (`?tier=css` and the default), on a scratch copy
// of the 2.3 park-trails page served against the 0.24.0 dists with one of each violation seeded,
// and to stay silent on the unseeded copy (2026-09-27, at the port).
//
// Two things the runtime gives no diagnostic for, derived and listed under `derivedFindings`
// rather than under `diagnostics`: a DOM-sampled group with neither a hint nor a texture
// (`analysis: "none"` on `configuredSource: "dom"`, which never adapts to its backdrop), and a
// demoted group.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");
const VIEWPORT = { width: 1440, height: 900 };
const SCHEMES = ["light", "dark"];

/* ------------------------------------------------------------------ arguments */

function usage(message) {
  if (message) console.error(`glass-audit: ${message}`);
  console.error("usage: glass-audit.mjs <url> [<url>…] --out <dir> [--slug <a,b,…>] "
    + "[--audit-dir <dir>]");
  process.exit(1);
}

const opts = { urls: [], out: null, slugs: [], auditDir: null };
{
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--out") opts.out = argv[++i];
    else if (a === "--slug") opts.slugs.push(...String(argv[++i] ?? "").split(",").filter(Boolean));
    else if (a === "--audit-dir") opts.auditDir = argv[++i];
    else if (a === "--help" || a === "-h") usage();
    else if (a.startsWith("--")) usage(`unknown option ${a}`);
    else opts.urls.push(a);
  }
  if (opts.urls.length === 0) usage("no URL given");
  if (!opts.out) usage("--out <dir> is required");
  if (opts.slugs.length > 0 && opts.slugs.length !== opts.urls.length) {
    usage(`--slug named ${opts.slugs.length} slug(s) for ${opts.urls.length} URL(s)`);
  }
  for (const u of opts.urls) {
    try { new URL(u); } catch { usage(`not a URL: ${u}`); }
  }
}

/** The page's slug: its URL's last path segment, with a trailing `index.html` passed over. */
function slugFromUrl(u) {
  const segments = new URL(u).pathname.split("/").filter(Boolean);
  if (segments.length > 0 && /^index\.html?$/i.test(segments.at(-1))) segments.pop();
  const last = segments.at(-1);
  return last ? last.replace(/\.html?$/i, "") : "root";
}

/* ------------------------------------------------------------------ the code lists */

/**
 * The diagnostic codes this script names, checked at start-up against the two lists in source.
 * A code that left the runtime would otherwise read as "never reported" for ever, which is a
 * clean result for the wrong reason.
 */
const NAMED = {
  nestedGlass: "glass-inside-glass",
  samePlaneOverlap: "same-plane-overlap",
  contentLayerHost: "glass-in-content-layer",
  demotedBackdropRoot: "backdrop-root-broken",
  hostOutsidePlane: "host-outside-plane",
  nonUniformRadii: "non-uniform-radii",
  tintUnparseable: "tint-unparseable",
  tintMixing: "tint-mixing",
  variantMixing: "variant-mixing",
};

function codeList(file, name) {
  const text = fs.readFileSync(path.join(repo, file), "utf8");
  const body = text.split(`export const ${name} = [`)[1]?.split("] as const")[0];
  if (!body) throw new Error(`glass-audit: no ${name} array in ${file}`);
  return [...body.matchAll(/^\s*"([a-z0-9-]+)",?\s*$/gm)].map((m) => m[1]);
}

const KNOWN_CODES = {
  platform: codeList("packages/platform-web/src/diagnostics.ts", "PLATFORM_DIAGNOSTIC_CODES"),
  core: codeList("packages/core/src/diagnostics.ts", "DIAGNOSTIC_CODES"),
};
{
  const all = new Set([...KNOWN_CODES.platform, ...KNOWN_CODES.core]);
  const gone = Object.values(NAMED).filter((c) => !all.has(c));
  if (gone.length > 0) {
    throw new Error(`glass-audit: named diagnostic code(s) gone from source: ${gone.join(", ")}`);
  }
}

/* ------------------------------------------------------------------ the browser */

/**
 * A Playwright module whose Chromium is actually installed, launched as the **full browser
 * binary** (`channel: "chromium"`). The bundled headless shell hands back a SwiftShader adapter
 * and would report a GPU tier that never touched a GPU — the repo's own `chromium-gpu` projects
 * (apps/demo, packages/platform-web) take the channel for exactly that reason, with the same two
 * Dawn flags. The workspace's own pin is tried first, resolved from the packages that depend on
 * it, and each candidate is test-launched rather than trusted.
 */
const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];

async function launch() {
  const names = [process.env.PLAYWRIGHT_MODULE, "@playwright/test", "playwright"].filter(Boolean);
  const bases = ["apps/demo/package.json", "packages/platform-web/package.json", "package.json"];
  const failures = [];
  for (const base of bases) {
    const require = createRequire(path.join(repo, base));
    for (const name of names) {
      let m;
      try { m = require(name); } catch { continue; }
      let version = null;
      try { version = require(`${name}/package.json`).version; } catch { /* unexported */ }
      try {
        const browser = await m.chromium.launch({ channel: "chromium", args: GPU_ARGS });
        return { browser, module: name, version };
      } catch (e) { failures.push(`${name} from ${base}: ${String(e.message).split("\n")[0]}`); }
    }
  }
  throw new Error(
    "no Playwright module could launch channel:\"chromium\" — the full browser binary is what "
    + "produces a real WebGPU adapter, so install it (npx playwright install chromium) rather "
    + "than falling back to the headless shell's SwiftShader.\n  " + failures.join("\n  "),
  );
}

/* ------------------------------------------------------------------ the page library */

/**
 * Everything the audit reads inside the page, installed as `window.__glassAuditLib` by an init
 * script before the page's own code runs. Written as one self-contained function because
 * Playwright serialises what it evaluates: nothing here may close over the Node side.
 */
function pageLib() {
  const round = (v, d = 3) => (typeof v === "number" ? Math.round(v * 10 ** d) / 10 ** d : v);
  const safe = (f) => { try { return f(); } catch { return undefined; } };
  const clone = (v) => (v === undefined ? null : JSON.parse(JSON.stringify(v)));

  /** A readable path to an element: ids and vitrea's own markers anchor it, classes name it. */
  function selectorPath(el) {
    if (!el || el.nodeType !== 1) return null;
    if (el === document.documentElement) return "html";
    const parts = [];
    for (let n = el; n && n.nodeType === 1 && n !== document.documentElement; n = n.parentElement) {
      const tag = n.tagName.toLowerCase();
      if (n.id) { parts.unshift(`${tag}#${CSS.escape(n.id)}`); break; }
      let s = tag;
      if (n.hasAttribute("data-vitrea-node")) {
        s += `[data-vitrea-node="${n.getAttribute("data-vitrea-node")}"]`;
      } else if (n.hasAttribute("data-vitrea-root")) s += "[data-vitrea-root]";
      else if (n.hasAttribute("data-vitrea-plane-root")) {
        s += `[data-vitrea-plane-root="${n.getAttribute("data-vitrea-plane-root")}"]`;
      } else if (n.hasAttribute("data-vitrea-layer")) {
        s += `[data-vitrea-layer="${n.getAttribute("data-vitrea-layer")}"]`;
      }
      const cls = [...n.classList].filter((c) => /^[A-Za-z_-]/.test(c)).slice(0, 2);
      if (cls.length > 0) s += "." + cls.map((c) => CSS.escape(c)).join(".");
      const same = n.parentElement
        ? [...n.parentElement.children].filter((c) => c.tagName === n.tagName) : [];
      if (same.length > 1) s += `:nth-of-type(${same.indexOf(n) + 1})`;
      parts.unshift(s);
    }
    return parts.join(" > ");
  }

  const cv = document.createElement("canvas"); cv.width = cv.height = 1;
  let cx = null;
  const colorCache = new Map();
  /** Any CSS colour as sRGB bytes and an alpha, through the canvas so every syntax parses. */
  function parseColor(s) {
    if (!s || s === "transparent") return s === "transparent" ? { r: 0, g: 0, b: 0, a: 0 } : null;
    if (colorCache.has(s)) return colorCache.get(s);
    let out = null;
    const m = s.match(/^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)$/);
    if (m) out = { r: +m[1], g: +m[2], b: +m[3], a: m[4] == null ? 1 : +m[4] };
    else {
      cx ??= cv.getContext("2d", { willReadFrequently: true });
      cx.clearRect(0, 0, 1, 1); cx.fillStyle = "#000"; cx.fillStyle = s;
      if (cx.fillStyle !== "#000000" || /black|#000/i.test(s)) {
        cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data;
        out = { r: d[0], g: d[1], b: d[2], a: d[3] / 255 };
      }
    }
    colorCache.set(s, out); return out;
  }
  const srgb = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const lum = ({ r, g, b }) => 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b);
  const ratio = (x, y) => (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  const contrast = (a, b) => ratio(lum(a), lum(b));
  const over = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1,
  });
  const visible = (el) => (el.checkVisibility
    ? el.checkVisibility({
      contentVisibilityAuto: true, visibilityProperty: true, opacityProperty: true,
    })
    : true);
  const largeText = (cs) => {
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
    return { size, bold, large: size >= 24 || (size >= 18.66 && bold) };
  };

  /**
   * The 2.3 audit's contrast sample, unchanged: a DOM composite that walks background colours
   * upward. It cannot see what the material drew, so a label on a WebGPU-tier surface is read
   * against whatever ground the walk reaches; `onGlass` tags those so the reading stays legible.
   */
  function extractContrast() {
    const effectiveBg = (el) => {
      let acc = null, node = el;
      while (node && node !== document.documentElement.parentNode) {
        const cs = getComputedStyle(node);
        if (cs.backgroundImage && cs.backgroundImage !== "none") return null;
        const c = parseColor(cs.backgroundColor);
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
      const fg = parseColor(cs.color); if (!fg) continue;
      const glass = !!el.closest("[data-vitrea-node]");
      const bg = effectiveBg(el);
      if (!bg) { unknown++; continue; }
      const { size, large } = largeText(cs);
      const c = contrast(fg.a < 1 ? over(fg, bg) : fg, bg);
      const ok = c >= (large ? 3 : 4.5);
      checked++; if (ok) pass++;
      if (glass) { onGlass++; if (ok) onGlassPass++; }
      if (!ok && fails.length < 12) {
        fails.push({
          text: el.textContent.trim().slice(0, 40), ratio: +c.toFixed(2), size, onGlass: glass,
        });
      }
    }
    const text = document.body.innerText || "";
    return {
      contrast: {
        method: "dom-composite", checked, pass, unknown,
        rate: checked ? +(pass / checked).toFixed(3) : null, onGlass, onGlassPass, fails,
      },
      overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      placeholder: /lorem ipsum|placeholder text|\bTODO\b|\bTBD\b/i.test(text),
      docHeight: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
      words: text.split(/\s+/).filter(Boolean).length,
      title: document.title,
    };
  }

  /**
   * Text on glass against the pixels actually behind it, from a capture of the current viewport
   * (the caller hands in the PNG it just took, so the page has not moved in between).
   *
   * Per text run inside a registered host: its line boxes from a Range, clipped to the viewport;
   * the pixels inside them split into those near the label's computed colour (the glyphs) and the
   * rest (the ground); the ground's per-channel median is the reading, and the decile of the
   * ground's luminance nearest the ink is reported beside it as the worst the label meets. The
   * ink is the computed colour rather than a glyph pixel because antialiasing never reaches the
   * ink on a 1x stem, which would under-read every small label.
   */
  async function sampleGlassText(b64, phase) {
    const img = new Image();
    img.src = "data:image/png;base64," + b64;
    await img.decode();
    const W = img.naturalWidth, H = img.naturalHeight;
    const canvas = document.createElement("canvas"); canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(img, 0, 0);
    const px = ctx.getImageData(0, 0, W, H).data;
    const scale = W / window.innerWidth;
    const pairs = [];
    for (const host of document.querySelectorAll("[data-vitrea-node]")) {
      const walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT);
      let t;
      while ((t = walker.nextNode())) {
        const text = t.textContent.trim();
        const el = t.parentElement;
        if (!text || !el || ["SCRIPT", "STYLE"].includes(el.tagName) || !visible(el)) continue;
        const range = document.createRange(); range.selectNodeContents(t);
        const rects = [...range.getClientRects()]
          .map((r) => ({
            x0: Math.max(0, Math.floor(r.left * scale)),
            y0: Math.max(0, Math.floor(r.top * scale)),
            x1: Math.min(W, Math.ceil(r.right * scale)),
            y1: Math.min(H, Math.ceil(r.bottom * scale)),
          }))
          .filter((r) => r.x1 - r.x0 >= 2 && r.y1 - r.y0 >= 4);
        if (rects.length === 0) continue;
        const cs = getComputedStyle(el);
        const ink = parseColor(cs.color); if (!ink) continue;
        const at = (x, y) => { const i = (y * W + x) * 4; return [px[i], px[i + 1], px[i + 2]]; };
        const dist = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
        const inkRgb = [ink.r, ink.g, ink.b];
        const median = (list, k) => {
          const v = list.map((p) => p[k]).sort((a, b) => a - b);
          return v[v.length >> 1];
        };
        // First a rough ground (everything well away from the ink), then the glyphs as every pixel
        // nearer the ink than that ground, grown by one pixel so the antialiasing ring around each
        // stem is not read as ground; what is left is the ground behind the label.
        const all = [], rough = [];
        for (const r of rects) {
          for (let y = r.y0; y < r.y1; y++) {
            for (let x = r.x0; x < r.x1; x++) {
              const p = at(x, y); all.push(p);
              if (dist(p, inkRgb) > 60) rough.push(p);
            }
          }
        }
        const seed = rough.length >= all.length * 0.2 ? rough : all;
        const g0 = [median(seed, 0), median(seed, 1), median(seed, 2)];
        const glyph = (x, y) => { const p = at(x, y); return dist(p, inkRgb) < dist(p, g0); };
        const ground = [];
        for (const r of rects) {
          for (let y = r.y0; y < r.y1; y++) {
            for (let x = r.x0; x < r.x1; x++) {
              let near = false;
              for (let dy = -1; dy <= 1 && !near; dy++) {
                for (let dx = -1; dx <= 1 && !near; dx++) {
                  const xx = x + dx, yy = y + dy;
                  if (xx >= 0 && yy >= 0 && xx < W && yy < H && glyph(xx, yy)) near = true;
                }
              }
              if (!near) ground.push(at(x, y));
            }
          }
        }
        const use = ground.length >= all.length * 0.1 ? ground : seed;
        const g = { r: median(use, 0), g: median(use, 1), b: median(use, 2), a: 1 };
        const inkC = ink.a < 1 ? over(ink, g) : ink;
        const inkL = lum(inkC);
        const gl = use.map((p) => lum({ r: p[0], g: p[1], b: p[2] })).sort((a, b) => a - b);
        const worstL = gl[Math.floor(gl.length * (inkL < lum(g) ? 0.1 : 0.9))];
        const { size, bold, large } = largeText(cs);
        const r = ratio(inkL, lum(g));
        pairs.push({
          phase, text: text.slice(0, 40), nodeId: host.getAttribute("data-vitrea-node"),
          size, bold, large, ratio: +r.toFixed(2), worstRatio: +ratio(inkL, worstL).toFixed(2),
          pass: r >= (large ? 3 : 4.5),
          ink: [Math.round(inkC.r), Math.round(inkC.g), Math.round(inkC.b)],
          ground: [g.r, g.g, g.b], pixels: all.length, groundPixels: ground.length,
        });
      }
    }
    return pairs;
  }

  const ROOT_API = ["capabilities", "probeReport", "diagnostics", "scene", "accessibility",
    "renderInput", "setAccessibilityOverrides", "material", "colorScheme", "windowActivation",
    "webgpu", "ready", "platformProbe"];

  /**
   * Everything the resolved runtime knows about itself, and the surface inventory.
   *
   * Surfaces come from the DOM's `[data-vitrea-node]` hosts, each measured from `renderInput()`'s
   * node of the same id when the root is reachable (the registered bounds and shape, which is what
   * the size family is read against) and from the element's own box otherwise. Group ids come from
   * the DOM first, so a root whose frame loop has not produced a render input still yields a full
   * per-group state table.
   */
  function readGlass() {
    const root = window.__vitrea;
    const input = root ? safe(() => root.renderInput()) : undefined;
    const frameNodes = new Map();
    for (const p of input?.planes ?? []) for (const n of p.nodes) frameNodes.set(n.nodeId, n);
    const surfaces = [...document.querySelectorAll("[data-vitrea-node]")].map((el) => {
      const nodeId = el.getAttribute("data-vitrea-node");
      const n = frameNodes.get(nodeId);
      const b = n ? n.bounds : el.getBoundingClientRect();
      return {
        nodeId, groupId: el.getAttribute("data-vitrea-group"),
        plane: n?.plane ?? el.getAttribute("data-vitrea-host-plane"),
        selector: selectorPath(el), tag: el.tagName.toLowerCase(), role: el.getAttribute("role"),
        rect: [round(b.x, 1), round(b.y, 1), round(b.width, 1), round(b.height, 1)],
        /** The size law's input: it is exactly inert below 32 CSS px. */
        span: round(Math.min(b.width, b.height), 1),
        boundsFrom: n ? "renderInput" : "dom",
        shapeFamily: n?.shapeFamily ?? null, radii: n?.radii ? [...n.radii] : null,
        smoothing: n?.smoothing ?? null, thickness: n?.thickness ?? null,
        variant: n?.material?.variant ?? null, tinted: n ? n.material?.tint !== undefined : null,
        cssRadius: getComputedStyle(el).borderTopLeftRadius,
        label: (el.getAttribute("aria-label") ?? el.textContent ?? "").trim().slice(0, 40),
      };
    });
    const domGroups = [...new Set(surfaces.map((s) => s.groupId).filter(Boolean))];
    if (!root) {
      return {
        rootFound: false, surfaces,
        groups: domGroups.map((id) => ({
          id, members: surfaces.filter((s) => s.groupId === id).length, state: null,
        })),
        diagnostics: [],
        derivedFindings: surfaces.length > 0
          ? ["no-root-handle: the page has vitrea surfaces but never assigned window.__vitrea"] : [],
      };
    }

    const diag = (channel, origin) => (safe(() => channel?.reported) ?? []).map((d) => ({
      origin, code: d.code, severity: d.severity, subjects: [...(d.subjects ?? [])],
      message: String(d.message ?? "").slice(0, 220),
    }));
    const diagnostics = [
      ...diag(root.diagnostics, "platform"), ...diag(root.scene?.diagnostics, "core"),
    ];
    const ids = new Set(domGroups);
    for (const g of input?.groups ?? []) ids.add(g.groupId);

    const groups = [...ids].map((id) => {
      const state = safe(() => root.capabilities(id));
      const ri = (input?.groups ?? []).find((g) => g.groupId === id);
      const probe = safe(() => root.probeReport(id));
      const members = surfaces.filter((s) => s.groupId === id);
      const { backdropToneAbscissae, ...rest } = state ?? {};
      return {
        id, members: members.length,
        state: state ? clone(rest) : null,
        abscissae: backdropToneAbscissae
          ? [...new Set(backdropToneAbscissae.map((a) => a.kind))] : null,
        backdropSourceId: ri?.backdropSourceId ?? null, variant: ri?.variant ?? null,
        samplingPadding: ri?.samplingPadding ?? null,
        blurRadius: ri?.blurRadius == null ? null : round(ri.blurRadius, 2),
        hasBackdropTone: ri ? ri.backdropTone !== undefined : null,
        backdropToneHint: ri?.backdropToneHint ?? null,
        probe: probe ? {
          verdict: probe.verdict, breaks: probe.breaks?.length ?? 0, reach: probe.reach,
          engineDefects: (probe.engineDefects ?? []).map((h) => h.defect?.id ?? "unnamed"),
        } : null,
        // A diagnostic names whichever subject it is about, and most are about a NODE rather
        // than the group, so the per-group list matches either.
        diagnostics: [...new Set(diagnostics
          .filter((d) => d.subjects.some((s) => s === id || members.some((m) => m.nodeId === s)))
          .map((d) => d.code))],
      };
    });

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
    const wg = safe(() => root.webgpu);
    return {
      rootFound: true,
      api: { missing: ROOT_API.filter((k) => !(k in root)) },
      surfaces,
      surfacesInFrame: input ? frameNodes.size : null,
      planes: (input?.planes ?? []).map((p) => ({ plane: p.plane, nodes: p.nodes.length })),
      colorScheme: safe(() => root.colorScheme) ?? null,
      windowActivation: safe(() => root.windowActivation) ?? null,
      material: clone(safe(() => root.material)),
      // The status without the `GPUDevice` itself, which serialises to `{}` and says nothing.
      webgpu: wg ? {
        available: wg.available ?? null, ownership: wg.ownership ?? null,
        deviceHealth: wg.deviceHealth ?? null, unavailableReason: wg.unavailableReason ?? null,
        hasDevice: wg.device !== undefined,
      } : null,
      platformProbe: clone(safe(() => ({
        engine: root.platformProbe.engine, reach: root.platformProbe.reach,
      }))),
      accessibility: clone(safe(() => root.accessibility)),
      groups, diagnostics, derivedFindings,
    };
  }

  /** The material as the reduced pass compares it: policy, per-group state and per-node optics. */
  function readMaterial() {
    const root = window.__vitrea;
    if (!root) return { rootFound: false };
    const input = safe(() => root.renderInput());
    const nodes = (input?.planes ?? []).flatMap((p) => p.nodes);
    const ids = new Set([...document.querySelectorAll("[data-vitrea-node]")]
      .map((e) => e.getAttribute("data-vitrea-group")).filter(Boolean));
    for (const g of input?.groups ?? []) ids.add(g.groupId);
    return {
      rootFound: true,
      accessibility: clone(safe(() => root.accessibility)),
      groups: [...ids].map((id) => {
        const s = safe(() => root.capabilities(id));
        const ri = (input?.groups ?? []).find((g) => g.groupId === id);
        return {
          id, renderer: s?.activeRenderer ?? null, refraction: s?.refraction ?? null,
          cssBody: s?.cssBody ?? null, cssTint: s?.cssTint ?? null,
          blurRadius: ri ? round(ri.blurRadius) : null,
          nodes: nodes.filter((n) => n.groupId === id).map((n) => ({
            nodeId: n.nodeId, blurRadius: round(n.optics?.blurRadius),
            tintAlpha: round(n.optics?.tintAlpha), borderAlpha: round(n.optics?.borderAlpha),
            refraction: n.refraction?.effective ?? null,
          })),
        };
      }),
    };
  }

  /* ---- the ban subset ---- */

  /** What the CSS tier writes inline on a host (css-tier.ts, `cssTierDeclarations().host`). */
  const CSS_TIER_HOST_PROPERTIES = ["background-color", "background-image", "backdrop-filter",
    "-webkit-backdrop-filter", "border-style", "border-width", "border-color", "box-shadow",
    "transition", "isolation", "border-radius"];
  const SNAPSHOT = ["backgroundColor", "backgroundImage", "boxShadow", "backdropFilter",
    "webkitBackdropFilter", "transitionProperty", "transitionDuration", "animationName",
    "colorScheme",
    ...["Top", "Right", "Bottom", "Left"].flatMap((s) =>
      [`border${s}Width`, `border${s}Style`, `border${s}Color`])];
  const pick = (cs) => Object.fromEntries(SNAPSHOT.map((k) => [k, cs[k] ?? ""]));

  /**
   * The host's computed style without the runtime's own writes: on a CSS-tier host (the one
   * carrying `--vitrea-occlusion`) the tier's inline declarations are lifted for one synchronous
   * read and the style attribute is put back exactly. vitrea's style observer ignores mutations
   * inside its root, and no frame runs in between.
   */
  function authoredSnapshot(el) {
    const cssTier = el.style.getPropertyValue("--vitrea-occlusion") !== "";
    if (!cssTier) return { cssTier, snap: pick(getComputedStyle(el)) };
    const saved = el.getAttribute("style");
    for (const p of CSS_TIER_HOST_PROPERTIES) el.style.removeProperty(p);
    const snap = pick(getComputedStyle(el));
    if (saved === null) el.removeAttribute("style"); else el.setAttribute("style", saved);
    return { cssTier, snap };
  }

  /** The user agent's own values for a tag, from an element in an unstyled frame. */
  function uaBaseline() {
    const cache = new Map();
    let frame = null;
    return {
      get(tag, scheme) {
        const key = `${tag}|${scheme}`;
        if (cache.has(key)) return cache.get(key);
        if (!frame) {
          frame = document.createElement("iframe");
          frame.setAttribute("aria-hidden", "true");
          frame.style.cssText = "position:fixed;left:-10000px;top:0;width:10px;height:10px;border:0";
          document.documentElement.appendChild(frame);
        }
        const d = frame.contentDocument;
        d.documentElement.style.colorScheme = scheme || "normal";
        const probe = d.createElement(tag);
        (d.body ?? d.documentElement).appendChild(probe);
        const snap = pick(frame.contentWindow.getComputedStyle(probe));
        probe.remove();
        cache.set(key, snap);
        return snap;
      },
      dispose() { frame?.remove(); },
    };
  }

  /** Keyframe names that set opacity, from every stylesheet the page can read. */
  function opacityKeyframes() {
    const names = new Set();
    let unreadable = 0;
    const walk = (rules) => {
      for (const rule of rules) {
        if (rule instanceof CSSKeyframesRule) {
          if ([...rule.cssRules].some((k) => k.style.getPropertyValue("opacity") !== "")) {
            names.add(rule.name);
          }
        } else if (rule.cssRules) walk(rule.cssRules);
      }
    };
    for (const sheet of document.styleSheets) {
      try { walk(sheet.cssRules); } catch { unreadable++; }
    }
    return { names, unreadable };
  }

  const ms = (s) => (s.trim().endsWith("ms") ? parseFloat(s) : parseFloat(s) * 1000);

  function opacityMotion(el, snap, keyframes) {
    const out = [];
    const props = snap.transitionProperty.split(",").map((s) => s.trim());
    const durations = snap.transitionDuration.split(",").map(ms);
    props.forEach((p, i) => {
      const d = durations[i % durations.length];
      if ((p === "opacity" || p === "all") && d > 0) {
        out.push({ property: "transition", value: `${p} ${d}ms` });
      }
    });
    for (const n of snap.animationName.split(",").map((s) => s.trim())) {
      if (n && n !== "none" && keyframes.names.has(n)) {
        out.push({ property: "animation", value: n });
      }
    }
    for (const a of safe(() => el.getAnimations()) ?? []) {
      if (typeof a.transitionProperty === "string") {
        if (a.transitionProperty === "opacity") {
          out.push({ property: "running-transition", value: "opacity" });
        }
        continue;
      }
      const frames = safe(() => a.effect.getKeyframes()) ?? [];
      if (frames.some((k) => "opacity" in k)) {
        out.push({
          property: "running-animation", value: a.animationName || a.id || "web-animation",
        });
      }
    }
    return out;
  }

  const CONTENT_ROLES = ["list", "listitem", "row", "table", "article"];
  const IMPLICIT_ROLES = { ul: "list", ol: "list", menu: "list", li: "listitem", tr: "row",
    table: "table", article: "article" };

  function contentRole(el) {
    const explicit = (el.getAttribute("role") ?? "").trim().split(/\s+/)[0];
    if (explicit) {
      return CONTENT_ROLES.includes(explicit) ? { role: explicit, source: "explicit" } : null;
    }
    const tag = el.tagName.toLowerCase();
    return IMPLICIT_ROLES[tag] ? { role: IMPLICIT_ROLES[tag], source: `implicit <${tag}>` } : null;
  }

  const alphaOf = (s) => parseColor(s)?.a ?? 1;
  /** A live backdrop filter, prefixed or not, or null. */
  const liveBackdrop = (cs) => (cs.backdropFilter && cs.backdropFilter !== "none" ? cs.backdropFilter
    : (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== "none" ? cs.webkitBackdropFilter : null));

  /** The materialist's mechanical ban subset, less the span rule (read from the inventory). */
  function readBan() {
    const findings = [], unmeasured = [];
    const keyframes = opacityKeyframes();
    if (keyframes.unreadable > 0) {
      unmeasured.push(`opacity keyframes: ${keyframes.unreadable} cross-origin sheet(s) unreadable`);
    }
    const ua = uaBaseline();
    let cssTierHosts = 0;
    const hosts = [...document.querySelectorAll("[data-vitrea-node]")];
    for (const el of hosts) {
      const base = {
        selector: selectorPath(el), nodeId: el.getAttribute("data-vitrea-node"),
        groupId: el.getAttribute("data-vitrea-group"),
      };
      const { cssTier, snap } = authoredSnapshot(el);
      if (cssTier) cssTierHosts++;
      const uaSnap = ua.get(el.tagName.toLowerCase(), snap.colorScheme);
      const origin = (keys) => (keys.every((k) => snap[k] === uaSnap[k]) ? "user-agent" : "author");
      const report = (property, value, keys) => {
        const o = origin(keys);
        // A user-agent default the CSS tier overwrites inline is not on screen; one the WebGPU
        // tier leaves alone is, and a page must reset it.
        if (o === "author" || !cssTier) {
          findings.push({ kind: "authored-host-style", ...base, property, value, origin: o,
            tier: cssTier ? "css" : "webgpu-or-unwritten" });
        }
      };
      if (snap.backgroundImage !== "none" || alphaOf(snap.backgroundColor) > 0) {
        report("background", `${snap.backgroundColor} ${snap.backgroundImage}`.trim(),
          ["backgroundColor", "backgroundImage"]);
      }
      const sides = ["Top", "Right", "Bottom", "Left"].filter((s) =>
        parseFloat(snap[`border${s}Width`]) > 0
        && !["none", "hidden"].includes(snap[`border${s}Style`])
        && alphaOf(snap[`border${s}Color`]) > 0);
      if (sides.length > 0) {
        const s = sides[0];
        report("border",
          `${sides.map((x) => x.toLowerCase()).join("/")}: ${snap[`border${s}Width`]} `
          + `${snap[`border${s}Style`]} ${snap[`border${s}Color`]}`,
          sides.flatMap((x) => [`border${x}Width`, `border${x}Style`, `border${x}Color`]));
      }
      if (snap.boxShadow !== "none") report("box-shadow", snap.boxShadow, ["boxShadow"]);
      const bf = liveBackdrop(snap);
      if (bf) report("backdrop-filter", bf, ["backdropFilter"]);
      const role = contentRole(el);
      if (role) {
        findings.push({ kind: "content-role-on-glass", ...base, property: "role",
          value: role.role, origin: role.source });
      }
      for (const m of opacityMotion(el, snap, keyframes)) {
        findings.push({ kind: "opacity-motion-on-host", ...base, ...m });
      }
    }
    ua.dispose();

    const roots = [...document.querySelectorAll("[data-vitrea-root]")];
    if (roots.length === 0) unmeasured.push("root ancestors: no [data-vitrea-root] on the page");
    const seen = new Set();
    for (const r of roots) {
      for (let a = r.parentElement; a; a = a.parentElement) {
        if (seen.has(a)) continue;
        seen.add(a);
        const cs = getComputedStyle(a);
        const base = { selector: selectorPath(a) };
        const effect = (property, value) =>
          findings.push({ kind: "root-ancestor-effect", ...base, property, value });
        if (cs.filter !== "none") effect("filter", cs.filter);
        if (cs.backdropFilter !== "none") effect("backdrop-filter", cs.backdropFilter);
        if (parseFloat(cs.opacity) < 1) effect("opacity", cs.opacity);
        const mask = cs.maskImage && cs.maskImage !== "none" ? cs.maskImage
          : (cs.webkitMaskImage && cs.webkitMaskImage !== "none" ? cs.webkitMaskImage : null);
        if (mask) effect("mask-image", mask.slice(0, 120));
        if (cs.clipPath !== "none") effect("clip-path", cs.clipPath);
        if (cs.mixBlendMode !== "normal") effect("mix-blend-mode", cs.mixBlendMode);
        for (const m of opacityMotion(a, pick(cs), keyframes)) {
          findings.push({ kind: "opacity-motion-on-root-ancestor", ...base, ...m });
        }
      }
    }

    // Two hues in one sampling group. The tint is a registration option and is not on the DOM,
    // so this needs the root; an achromatic seed has no hue and is passed over.
    const root = window.__vitrea;
    const input = root ? safe(() => root.renderInput()) : undefined;
    if (!root) unmeasured.push("two-tint-hues: no window.__vitrea, and the tint is not on the DOM");
    else if (!input) unmeasured.push("two-tint-hues: renderInput() returned nothing");
    else {
      const byGroup = new Map();
      for (const p of input.planes) {
        for (const n of p.nodes) {
          const t = n.material?.tint;
          if (!t || !(t.strength > 0)) continue;
          const [r, g, b] = t.color, mx = Math.max(r, g, b), mn = Math.min(r, g, b), c = mx - mn;
          if (c < 0.04) continue;
          let h = mx === r ? ((g - b) / c) % 6 : mx === g ? (b - r) / c + 2 : (r - g) / c + 4;
          h = (h * 60 + 360) % 360;
          if (!byGroup.has(n.groupId)) byGroup.set(n.groupId, []);
          byGroup.get(n.groupId).push({
            nodeId: n.nodeId, hue: Math.round(h), color: t.color.map((v) => round(v)),
          });
        }
      }
      for (const [groupId, list] of byGroup) {
        const clusters = [];
        for (const e of list) {
          const apart = (cl) => Math.min(Math.abs(cl - e.hue), 360 - Math.abs(cl - e.hue));
          const near = clusters.find((cl) => apart(cl) <= 20);
          if (near === undefined) clusters.push(e.hue);
        }
        if (clusters.length > 1) {
          findings.push({ kind: "two-tint-hues", groupId, selector: null, property: "tint",
            value: clusters.map((h) => `${h}°`).join(", "), nodes: list });
        }
      }
    }
    return { findings, unmeasured, hostsRead: hosts.length, cssTierHosts };
  }

  /**
   * Under forced colours: how much glass still draws. The runtime's own count is the surfaces
   * whose resolved policy still draws a body (zero when `material.glass` is `"none"`); the DOM's
   * is every element with a live `backdrop-filter`, classed as the runtime's sampling proxy (not
   * glass), a host or its tier layers, or the author's own hand-rolled blur.
   */
  function readForced() {
    const root = window.__vitrea;
    const input = root ? safe(() => root.renderInput()) : undefined;
    const hosts = [...document.querySelectorAll("[data-vitrea-node]")].map((el) => {
      const cs = getComputedStyle(el);
      return {
        nodeId: el.getAttribute("data-vitrea-node"), selector: selectorPath(el),
        backdropFilter: cs.backdropFilter, backgroundColor: cs.backgroundColor,
        backgroundImage: cs.backgroundImage.slice(0, 80), borderColor: cs.borderTopColor,
        forcedColorAdjust: cs.forcedColorAdjust,
      };
    });
    const backdrop = [];
    for (const el of document.querySelectorAll("*")) {
      const cs = getComputedStyle(el);
      const v = liveBackdrop(cs);
      if (!v) continue;
      const where = el.closest("[data-vitrea-proxy]") ? "runtime-proxy"
        : el.closest("[data-vitrea-node]") ? "glass-host"
          : el.closest("[data-vitrea-root]") ? "runtime-other" : "author";
      backdrop.push({ selector: selectorPath(el), where, value: v.slice(0, 80) });
    }
    const policyGlass = root ? safe(() => root.accessibility.material.glass) ?? null : null;
    const nodes = input
      ? (input.planes ?? []).reduce((n, p) => n + p.nodes.length, 0) : hosts.length;
    const runtimeGlassSurfaces = root ? (policyGlass === "none" ? 0 : nodes) : null;
    const domGlass = backdrop.filter((b) => b.where !== "runtime-proxy").length;
    return {
      policyGlass, runtimeGlassSurfaces,
      backdropFilterElements: backdrop.slice(0, 20), backdropFilterCount: backdrop.length,
      glassDrawn: (runtimeGlassSurfaces ?? 0) + domGlass,
      runtimeRead: root !== undefined, hosts,
    };
  }

  async function adapterInfo() {
    if (!navigator.gpu) return { available: false };
    try {
      const a = await navigator.gpu.requestAdapter();
      if (!a) return { available: false, reason: "no adapter" };
      const i = a.info ?? {};
      return {
        available: true, vendor: i.vendor ?? null, architecture: i.architecture ?? null,
        device: i.device ?? null, description: i.description ?? null,
        isFallbackAdapter: i.isFallbackAdapter ?? a.isFallbackAdapter ?? null,
      };
    } catch (e) { return { available: false, reason: String(e.message).slice(0, 120) }; }
  }

  return {
    extractContrast, sampleGlassText, readGlass, readMaterial, readBan, readForced, adapterInfo,
  };
}

const INIT_SCRIPT = `window.__glassAuditLib = (${pageLib.toString()})();`;

/* ------------------------------------------------------------------ one pass */

const CAPTURE_NAMES = [
  ...SCHEMES.flatMap((s) => [`shot-fv-${s}.png`, `shot-full-${s}.png`, `tile-2-${s}.png`,
    `tile-3-${s}.png`, `shot-menu-${s}.png`]),
  "shot-reduced.png", "shot-contrast.png", "shot-forced.png",
];

/**
 * A fresh context and page under the given media emulation, loaded and settled. The settle is the
 * 2.3 protocol's: fonts ready, 1500 ms (long enough for the WebGPU handshake), then the root's own
 * `ready()` where one is reachable.
 */
async function openPage(browser, url, media) {
  const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const log = { errors: [], consoleErrors: [], failedRequests: [], badResponses: [] };
  page.on("pageerror", (e) => log.errors.push(String(e.message || e).slice(0, 240)));
  page.on("console", (m) => {
    if (m.type() === "error") log.consoleErrors.push(m.text().slice(0, 240));
  });
  page.on("requestfailed", (r) =>
    log.failedRequests.push(`${r.url().slice(0, 140)} ${r.failure()?.errorText ?? ""}`.trim()));
  page.on("response", (r) => {
    if (r.status() >= 400) log.badResponses.push(`${r.status()} ${r.url().slice(0, 140)}`);
  });
  await page.addInitScript(INIT_SCRIPT);
  let emulation = { ok: true };
  try { await page.emulateMedia(media); } catch (e) {
    emulation = { ok: false, error: String(e.message).split("\n")[0].slice(0, 200) };
  }
  await page.goto(url, { waitUntil: "load", timeout: 60_000 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1500);
  const readyState = await page.evaluate(async () => {
    if (!window.__vitrea?.ready) return "no-root";
    try { await window.__vitrea.ready(); return "settled"; }
    catch (e) { return "ready-threw: " + e.message; }
  });
  return { context, page, log, emulation, readyState };
}

/** An expression calling one library function; Playwright awaits a returned promise. */
const lib = (name) => `window.__glassAuditLib.${name}()`;

async function shootAndSample(page, file, phase) {
  const buf = await page.screenshot({ path: file, fullPage: false });
  return page.evaluate(([b64, p]) => window.__glassAuditLib.sampleGlassText(b64, p),
    [buf.toString("base64"), phase]);
}

/** Summarise one scheme's glass-text pairs. */
function glassContrastSummary(pairs) {
  const byPhase = {};
  for (const p of pairs) {
    byPhase[p.phase] ??= { pairs: 0, pass: 0 };
    byPhase[p.phase].pairs++; if (p.pass) byPhase[p.phase].pass++;
  }
  return {
    method: "rendered-pixels", pairs: pairs.length, pass: pairs.filter((p) => p.pass).length,
    minRatio: pairs.length ? Math.min(...pairs.map((p) => p.ratio)) : null,
    byPhase, fails: pairs.filter((p) => !p.pass).slice(0, 12), sample: pairs.slice(0, 40),
  };
}

function groupSummary(g) {
  const s = g.state ?? {};
  return {
    id: g.id, members: g.members,
    renderer: s.activeRenderer ?? null, sampling: s.samplingBackend ?? null,
    configuredSource: s.configuredSource ?? null, analysis: s.analysis ?? null,
    refraction: s.refraction ?? null, health: s.health ?? null,
    demotionReason: s.demotionReason ?? null, cssBody: s.cssBody ?? null,
    cssTint: s.cssTint ?? null, cssShadow: s.cssShadow ?? null,
    materialDocument: s.materialDocument ?? null, abscissae: g.abscissae ?? null,
    variant: g.variant ?? null, blurRadius: g.blurRadius ?? null,
    backdropToneHint: g.backdropToneHint ?? null, probe: g.probe ?? null,
    diagnostics: g.diagnostics ?? [],
  };
}

async function schemePass(browser, url, dir, scheme) {
  const { context, page, log, readyState } = await openPage(browser, url, { colorScheme: scheme });
  try {
    const at = (f) => path.join(dir, f);
    const adapter = await page.evaluate(lib("adapterInfo"));
    // The fixed capture protocol: the first viewport at scroll 0 BEFORE any walk — a page that
    // scrolls itself during the walk otherwise photographs its own second screen — then the walk
    // for lazy and reveal-on-scroll content, the full page, and two viewport tiles.
    const scrolledOnLoad = await page.evaluate(() => {
      const y = window.scrollY; window.scrollTo(0, 0); return y;
    });
    await page.waitForTimeout(300);
    const pairs = await shootAndSample(page, at(`shot-fv-${scheme}.png`), "fv");
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
    const measured = await page.evaluate(lib("extractContrast"));
    const glass = await page.evaluate(lib("readGlass"));
    await page.screenshot({ path: at(`shot-full-${scheme}.png`), fullPage: true });
    // The tiles are VIEWPORT captures with the window scrolled, not clips of the stitched page: a
    // glass page is a fixed plane with floating bars over a scrolling sheet, and each tile is the
    // screen as the reader meets it, the bars over whatever has passed beneath them.
    for (const n of [2, 3]) {
      const y = (n - 1) * VIEWPORT.height, tile = at(`tile-${n}-${scheme}.png`);
      if (measured.docHeight > y + 100) {
        await page.evaluate((top) => window.scrollTo(0, top), y);
        await page.waitForTimeout(500);
        pairs.push(...await shootAndSample(page, tile, `tile-${n}`));
      }
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(400);
    const banRest = await page.evaluate(lib("readBan"));

    // The transient platter, where the page offers a way to open one: the one state the resting
    // captures cannot show, and a second group on the overlay plane that resolves its own tier.
    let menu = "not-offered", menuGlass = null, banMenu = null;
    const hasMenu = await page.evaluate(() => typeof window.__glassDemo?.openMenu === "function");
    if (hasMenu) {
      try {
        await page.evaluate(async () => { await window.__glassDemo.openMenu(); });
        await page.waitForTimeout(700);
        pairs.push(...await shootAndSample(page, at(`shot-menu-${scheme}.png`), "menu"));
        menu = "captured";
        menuGlass = await page.evaluate(lib("readGlass"));
        banMenu = await page.evaluate(lib("readBan"));
      } catch (e) { menu = "openMenu threw: " + String(e.message).slice(0, 160); }
    }

    const png = fs.readFileSync(at(`shot-full-${scheme}.png`));
    const captureWidth = png.readUInt32BE(16);
    return {
      scheme, readyState, adapter,
      errors: log.errors, consoleErrors: log.consoleErrors.slice(0, 10),
      failedRequests: log.failedRequests.slice(0, 10), badResponses: log.badResponses.slice(0, 10),
      scrolledOnLoad, docHeight: measured.docHeight, words: measured.words, title: measured.title,
      placeholder: measured.placeholder,
      captureWidth, overflowCapture: captureWidth > VIEWPORT.width, overflowAtLoad: measured.overflow,
      contrast: measured.contrast,
      glassContrast: glassContrastSummary(pairs),
      rootFound: glass.rootFound, api: glass.api ?? null,
      colorScheme: glass.colorScheme ?? null,
      schemeFollowed: glass.rootFound ? glass.colorScheme === scheme : null,
      windowActivation: glass.windowActivation ?? null, material: glass.material ?? null,
      webgpu: glass.webgpu ?? null, platformProbe: glass.platformProbe ?? null,
      accessibility: glass.accessibility ?? null,
      surfaces: glass.surfaces, surfacesInFrame: glass.surfacesInFrame ?? null,
      planes: glass.planes ?? [],
      groups: glass.groups.map(groupSummary),
      diagnostics: glass.diagnostics, derivedFindings: glass.derivedFindings,
      menu,
      menuSurfaces: menuGlass?.surfaces ?? null,
      menuGroups: menuGlass ? menuGlass.groups.map(groupSummary) : null,
      // The same shape as the resting `diagnostics`, minus what was already reported at rest: a
      // menu-pass diagnostic is about the platter's arrival.
      menuDiagnostics: menuGlass
        ? menuGlass.diagnostics.filter((d) => !glass.diagnostics.some((p) => p.code === d.code
          && p.subjects.join() === d.subjects.join()))
        : null,
      ban: { rest: banRest, menu: banMenu },
    };
  } finally {
    await context.close();
  }
}

/**
 * The reduced-transparency pass: the page's own switch, else the runtime's override, then what
 * moved. The policy should read frost increased, refraction reduced and occlusion increased
 * (packages/core/src/accessibility.ts); each group's material has moved when its resolved
 * refraction, CSS body or tint form, its blur, or any member's optics (blur, tint alpha — the
 * occlusion knob — border alpha, effective refraction) differ from before.
 */
async function reducedPass(browser, url, dir) {
  const file = path.join(dir, "shot-reduced.png");
  const { context, page, log, readyState } = await openPage(browser, url, { colorScheme: "light" });
  try {
    const before = await page.evaluate(lib("readMaterial"));
    const method = await page.evaluate(async () => {
      try {
        if (typeof window.__glassDemo?.setReducedTransparency === "function") {
          await window.__glassDemo.setReducedTransparency(true);
          return "page-switch";
        }
        if (typeof window.__vitrea?.setAccessibilityOverrides === "function") {
          window.__vitrea.setAccessibilityOverrides({ reducedTransparency: true });
          return "runtime-override";
        }
        return "none";
      } catch (e) { return "threw: " + String(e.message).slice(0, 160); }
    });
    const applied = method === "page-switch" || method === "runtime-override";
    // The override lands on the next frame and the CSS tier transitions into it.
    await page.waitForTimeout(1200);
    const after = await page.evaluate(lib("readMaterial"));
    if (applied) await page.screenshot({ path: file, fullPage: false });
    const a = after.accessibility, m = a?.material;
    const key = (g) => JSON.stringify([g.refraction, g.cssBody, g.cssTint, g.blurRadius,
      g.nodes.map((n) => [n.blurRadius, n.tintAlpha, n.borderAlpha, n.refraction]).sort()]);
    const groups = (after.groups ?? []).map((g) => {
      const b = (before.groups ?? []).find((x) => x.id === g.id);
      return { id: g.id, moved: b ? key(b) !== key(g) : null, before: b ?? null, after: g };
    });
    return {
      method, applied, readyState, rootFound: after.rootFound,
      errors: log.errors, consoleErrors: log.consoleErrors.slice(0, 10),
      policyBefore: before.accessibility ?? null, policyAfter: a ?? null,
      policyChanged: after.rootFound
        ? JSON.stringify(before.accessibility) !== JSON.stringify(a) : null,
      policyAsAsked: m
        ? a.reducedTransparency === true && m.frost === "increased"
          && m.refraction === "reduced" && m.occlusion === "increased"
        : null,
      groups,
      materialMoved: groups.length > 0 && groups.every((g) => g.moved !== null)
        ? groups.every((g) => g.moved) : null,
      captured: applied,
    };
  } finally {
    await context.close();
  }
}

/** The three passes Playwright can emulate, each with its query and what the policy must read. */
const EMULATIONS = {
  increasedContrast: {
    media: { contrast: "more" }, query: "(prefers-contrast: more)", shot: "shot-contrast.png",
    asked: (a) => a.increasedContrast === true && a.material.border === "strong"
      && a.material.foreground === "near-monochrome",
  },
  reducedMotion: {
    media: { reducedMotion: "reduce" }, query: "(prefers-reduced-motion: reduce)", shot: null,
    asked: (a) => a.reducedMotion === true && a.motion.overshoot === "none"
      && a.motion.morph === "non-elastic",
  },
  forcedColors: {
    media: { forcedColors: "active" }, query: "(forced-colors: active)", shot: "shot-forced.png",
    asked: (a) => a.forcedColors === true && a.material.glass === "none",
  },
};

async function emulationPass(browser, url, dir, kind) {
  const spec = EMULATIONS[kind];
  const { context, page, log, emulation, readyState } =
    await openPage(browser, url, { colorScheme: "light", ...spec.media });
  try {
    if (!emulation.ok) return { status: "unsupported", error: emulation.error, errors: log.errors };
    const matches = await page.evaluate((q) => matchMedia(q).matches, spec.query);
    if (!matches) {
      return { status: "not-applied", query: spec.query, errors: log.errors,
        note: "emulateMedia accepted the option but the page's matchMedia did not see it" };
    }
    const glass = await page.evaluate(lib("readGlass"));
    const forced = kind === "forcedColors" ? await page.evaluate(lib("readForced")) : null;
    if (spec.shot) await page.screenshot({ path: path.join(dir, spec.shot), fullPage: false });
    const a = glass.accessibility;
    return {
      status: "ran", query: spec.query, readyState, rootFound: glass.rootFound,
      errors: log.errors, consoleErrors: log.consoleErrors.slice(0, 10),
      accessibility: a ?? null,
      policyAsAsked: a ? spec.asked(a) : null,
      groups: glass.groups.map(groupSummary), diagnostics: glass.diagnostics,
      ...(forced ? { forced } : {}),
      ...(forced ? { glassDrawn: forced.glassDrawn } : {}),
    };
  } finally {
    await context.close();
  }
}

/* ------------------------------------------------------------------ one page */

/** Findings from several reads, merged on what they are about, with where each was seen. */
function mergeFindings(reads) {
  const out = new Map();
  for (const [where, list] of reads) {
    for (const f of list ?? []) {
      const k = [f.kind, f.selector, f.groupId, f.property, f.value].join("|");
      if (!out.has(k)) out.set(k, { ...f, seen: [] });
      out.get(k).seen.push(where);
    }
  }
  return [...out.values()];
}

async function auditOne(browser, url, slug, dir) {
  fs.mkdirSync(dir, { recursive: true });
  for (const f of CAPTURE_NAMES) fs.rmSync(path.join(dir, f), { force: true });
  const schemes = {};
  for (const scheme of SCHEMES) schemes[scheme] = await schemePass(browser, url, dir, scheme);
  const reduced = await reducedPass(browser, url, dir);
  const emulation = {};
  for (const kind of Object.keys(EMULATIONS)) {
    emulation[kind] = await emulationPass(browser, url, dir, kind);
  }

  const light = schemes.light;
  const rootFound = SCHEMES.every((s) => schemes[s].rootFound);

  // Every diagnostic either scheme saw, at rest or with the menu open, once.
  const diagnostics = [];
  for (const s of SCHEMES) {
    const lists = [["rest", schemes[s].diagnostics], ["menu", schemes[s].menuDiagnostics]];
    for (const [state, list] of lists) {
      for (const d of list ?? []) {
        const same = diagnostics.find((x) => x.origin === d.origin && x.code === d.code
          && x.subjects.join() === d.subjects.join());
        if (same) same.seen.push(`${s}/${state}`);
        else diagnostics.push({ ...d, seen: [`${s}/${state}`] });
      }
    }
  }
  const known = new Set([...KNOWN_CODES.platform, ...KNOWN_CODES.core]);
  const codes = new Set(diagnostics.map((d) => d.code));

  const reads = [];
  for (const s of SCHEMES) {
    reads.push([`${s}/rest`, schemes[s].ban.rest?.findings]);
    if (schemes[s].ban.menu) reads.push([`${s}/menu`, schemes[s].ban.menu.findings]);
    const spans = [...schemes[s].surfaces.map((x) => ["rest", x]),
      ...(schemes[s].menuSurfaces ?? []).map((x) => ["menu", x])]
      .filter(([, x]) => x.span < 32)
      .map(([state, x]) => [`${s}/${state}`, [{
        kind: "span-under-32", selector: x.selector, nodeId: x.nodeId, groupId: x.groupId,
        property: "span", value: x.span,
        note: "under the size law's floor; a deliberate exception of the family is the page "
          + "record's to argue, and the audit cannot see one",
      }]]);
    reads.push(...spans);
  }
  const findings = mergeFindings(reads);
  const unmeasured = [...new Set(SCHEMES.flatMap((s) =>
    [schemes[s].ban.rest?.unmeasured ?? [], schemes[s].ban.menu?.unmeasured ?? []].flat()))];

  const captures = CAPTURE_NAMES.filter((f) => fs.existsSync(path.join(dir, f)));
  const captureSha256 = Object.fromEntries(captures.map((f) =>
    [f, crypto.createHash("sha256").update(fs.readFileSync(path.join(dir, f))).digest("hex")]));

  const passErrors = [...SCHEMES.flatMap((s) => schemes[s].errors), ...reduced.errors,
    ...Object.values(emulation).flatMap((e) => e.errors ?? [])];
  return {
    slug, url, auditedAt: new Date().toISOString(), viewport: VIEWPORT,
    rootFound,
    readyState: light.readyState,
    adapter: light.adapter,
    api: light.api,
    errors: passErrors,
    schemes,
    surfaces: light.surfaces,
    planes: light.planes,
    diagnostics,
    unknownDiagnosticCodes: [...codes].filter((c) => !known.has(c)),
    named: Object.fromEntries(Object.entries(NAMED).map(([k, code]) => [k, codes.has(code)])),
    banSubset: {
      findings,
      counts: findings.reduce((acc, f) => ({ ...acc, [f.kind]: (acc[f.kind] ?? 0) + 1 }), {}),
      unmeasured,
    },
    reduced,
    emulation,
    captures,
    captureSha256,
    // The 2.3 audit's page-level gate, kept for comparability: no page error in any pass, no
    // overflow, no placeholder copy, and the DOM contrast sample at 0.9 or better in both schemes.
    // It is not the pass line, which `glass-rules-analyze.py` applies to the readings.
    gateMechanical: passErrors.length === 0
      && SCHEMES.every((s) => schemes[s].captureWidth <= VIEWPORT.width && !schemes[s].placeholder
        && (schemes[s].contrast.rate == null || schemes[s].contrast.rate >= 0.9)),
  };
}

/* ------------------------------------------------------------------ run */

const { browser, module, version } = await launch();
console.error(`glass-audit: ${module} ${version ?? "(version unexported)"}, `
  + `Chromium ${browser.version()}`);
const out = path.resolve(opts.out);
fs.mkdirSync(out, { recursive: true });
if (opts.auditDir) fs.mkdirSync(path.resolve(opts.auditDir), { recursive: true });

const results = [];
for (const [i, url] of opts.urls.entries()) {
  const slug = opts.slugs[i] ?? slugFromUrl(url);
  const dir = path.join(out, slug);
  process.stderr.write(`audit ${slug} (${url}) … `);
  let r;
  try {
    r = await auditOne(browser, url, slug, dir);
    console.error(`page errors ${r.errors.length}, diagnostics ${r.diagnostics.length}, `
      + `ban findings ${r.banSubset.findings.length}, 2.3 gate ${r.gateMechanical ? "ok" : "fails"}`);
  } catch (e) {
    console.error("ERROR " + String(e.message).split("\n")[0]);
    r = { slug, url, auditedAt: new Date().toISOString(), error: String(e.message).slice(0, 400),
      gateMechanical: false };
  }
  r.tool = { playwright: { module, version }, chromium: browser.version(), gpuArgs: GPU_ARGS };
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "audit.json"), JSON.stringify(r, null, 1) + "\n");
  if (opts.auditDir) {
    fs.writeFileSync(path.join(path.resolve(opts.auditDir), `${slug}.json`),
      JSON.stringify(r, null, 1) + "\n");
  }
  results.push(r);
}
await browser.close();

const stamp = new Date().toISOString().replace(/\.\d+Z$/, "Z").replace(/:/g, "-");
const runFile = path.join(out, `run-${stamp}.json`);
fs.writeFileSync(runFile, JSON.stringify(results, null, 1) + "\n");
console.error(`glass-audit: wrote ${runFile}`);

// The summary: one line of the facts the pass line and the assigned readings turn on.
process.stdout.write(JSON.stringify(results.map((r) => (r.error ? { slug: r.slug, error: r.error } : {
  slug: r.slug, rootFound: r.rootFound, errors: r.errors.length,
  diagnostics: r.diagnostics.length, banFindings: r.banSubset.findings.length,
  surfaces: r.surfaces.length,
  glassContrast: Object.fromEntries(SCHEMES.map((s) =>
    [s, `${r.schemes[s].glassContrast.pass}/${r.schemes[s].glassContrast.pairs}`])),
  reduced: { method: r.reduced.method, policyAsAsked: r.reduced.policyAsAsked,
    materialMoved: r.reduced.materialMoved },
  emulation: Object.fromEntries(Object.entries(r.emulation).map(([k, e]) =>
    [k, e.status === "ran" ? { asked: e.policyAsAsked, errors: e.errors.length,
      ...(k === "forcedColors" ? { glassDrawn: e.glassDrawn } : {}) } : e.status])),
  captures: r.captures.length, gateMechanical: r.gateMechanical,
})), null, 1) + "\n");
