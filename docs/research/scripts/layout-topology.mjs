#!/usr/bin/env node
// Layout-topology measurement over rendered HTML builds.
//
// Research instrument for docs/research/2026-09-05-composition-grammar-prior-art.md, and the
// prototype of the composition-QA "layout clone check". It renders each build in Chromium at a
// desktop viewport and decomposes the page into a block tree: an element splits into its children
// when at least two of them are visibly large; a wrapper whose single large child covers it is
// passed through; a parent whose children are three or more repeated siblings (same tag and
// classes, near-uniform boxes) becomes one region labelled by the repetition kind (list, card
// grid, stat row, table) rather than being split into rows; an SVG or canvas is one region. Every
// leaf region gets a coarse role, and the first viewport is rasterised into a 24 x 16 map twice,
// once by region identity and once by role. From those it derives four pairwise distances:
//
//   partition  fraction of first-viewport cell adjacencies whose same-region relation differs
//              (a label-free measure of the geometric partition, after Rico's layout raster)
//   raster     fraction of first-viewport cells whose role differs
//   pqgram     pq-gram distance (p=2, q=3) between the role-labelled block trees, an
//              approximation of tree edit distance (Augsten, Böhlen & Gamper 2005)
//   sig        Hamming distance over a twelve-slot coarse topology signature (top nav, sidebar
//              or rail, hero form, dominant first-viewport role, stat row, card grids, 3-up, ...)
//
// Usage: node docs/research/scripts/layout-topology.mjs [--out file.json] <html files...>
// Runs against the gitignored eval workspace; the JSON it writes is committed evidence.

import { createRequire } from "node:module";
import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");
// Playwright comes from the workspace install; PLAYWRIGHT_MODULE overrides it with any other
// installed copy (the version must match the Chromium build in the Playwright browser cache).
const require = createRequire(path.join(repoRoot, "packages/platform-web/package.json"));
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

const VW = 1440;
const VH = 900;
const RASTER_COLS = 24;
const RASTER_ROWS = 16;

const args = process.argv.slice(2);
let outPath = null;
const files = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--out") outPath = args[++i];
  else files.push(args[i]);
}
if (files.length === 0) {
  console.error("no html files given");
  process.exit(1);
}

// Runs inside the page. Everything it returns is plain JSON.
function extract({ vw, vh, cols, rows }) {
  const SKIP = new Set(["SCRIPT", "STYLE", "TEMPLATE", "NOSCRIPT", "LINK", "META", "TITLE", "HEAD", "BR"]);
  const docH = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
  const rect = (el) => {
    const r = el.getBoundingClientRect();
    return { x: r.left + window.scrollX, y: r.top + window.scrollY, w: r.width, h: r.height };
  };
  const isVisible = (el) => {
    if (!(el instanceof Element) || SKIP.has(el.tagName)) return false;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) === 0) return false;
    const r = rect(el);
    return r.w >= 4 && r.h >= 4;
  };
  const kids = (el) => [...el.children].filter(isVisible);
  const sig = (el) => {
    const cls = (typeof el.className === "string" ? el.className : "").trim().split(/\s+/).filter(Boolean).slice(0, 2).join(".");
    return el.tagName.toLowerCase() + (cls ? "." + cls : "");
  };
  const MIN_AREA = vw * vh * 0.005;
  const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;

  const numberish = (el) =>
    [...el.querySelectorAll("*")].some((n) => parseFloat(getComputedStyle(n).fontSize) >= 20 && /\d/.test(n.textContent || "")) &&
    /(^|\s)[$€£]?\d[\d,.]*\s?(%|k|M|ms|min|h|°)?(\s|$)/.test(el.innerText || "");
  const currency = (el) => /[$€£]\s?\d|\d\s?(USD|EUR|GBP|\/mo|\/month|per month)/.test(el.innerText || "");

  // Repeated-sibling detection (the MDR idea of Liu, Grossman & Zhai 2003 reduced to siblings):
  // three or more visible children of one parent sharing tag, first classes and child count, with
  // near-uniform boxes. Returns the dominant group or null.
  function repeatedGroup(el) {
    const ks = kids(el);
    if (ks.length < 3) return null;
    const bySig = new Map();
    ks.forEach((k) => {
      const r = rect(k);
      if (r.w * r.h < vw * vh * 0.002) return;
      const s = sig(k) + "|" + k.children.length;
      if (!bySig.has(s)) bySig.set(s, []);
      bySig.get(s).push({ el: k, r });
    });
    let best = null;
    bySig.forEach((members, s) => {
      if (members.length < 3) return;
      const mw = mean(members.map((m) => m.r.w));
      const mh = mean(members.map((m) => m.r.h));
      const uniform = members.every((m) => Math.abs(m.r.w - mw) <= 0.2 * mw && Math.abs(m.r.h - mh) <= 0.35 * mh);
      if (!uniform) return;
      const colsN = new Set(members.map((m) => Math.round(m.r.x / 8))).size;
      const top = Math.min(...members.map((m) => m.r.y));
      const nums = members.filter((m) => numberish(m.el)).length;
      const cur = members.filter((m) => currency(m.el)).length;
      let kind;
      if (el.closest("table") || el.tagName === "TABLE") kind = "table";
      else if (mh <= 200 && colsN === members.length && nums >= Math.ceil(members.length / 2)) kind = "stat-row";
      else if (colsN >= 2 && mh >= 120 && cur >= Math.ceil(members.length / 2)) kind = "pricing";
      else if (colsN >= 2 && mh >= 120) kind = "card-grid";
      else if (colsN === 1) kind = "list";
      else kind = "row";
      const g = {
        sig: s, kind, count: members.length, cols: colsN, w: Math.round(mw), h: Math.round(mh), top: Math.round(top),
        inFirstViewport: top < vh, areaShare: +((members.length * mw * mh) / (vw * vh)).toFixed(3),
        coverage: (members.length * mw * mh) / Math.max(1, rect(el).w * rect(el).h),
      };
      if (!best || g.count * g.w * g.h > best.count * best.w * best.h) best = g;
    });
    return best;
  }

  function role(el, r) {
    const tag = el.tagName.toLowerCase();
    const ar = el.getAttribute("role");
    const tall = r.h >= vh * 0.5;
    const narrow = r.w >= 150 && r.w <= 460;
    if (tag === "nav" || ar === "navigation") return tall && narrow ? "sidebar" : "nav";
    if (narrow && tall && r.x <= vw * 0.02) return "sidebar";
    if (narrow && tall && r.x + r.w >= vw * 0.98) return "rail";
    if (tag === "header" || ar === "banner") return r.h <= 140 ? "topbar" : "header";
    if (tag === "footer" || ar === "contentinfo") return "footer";
    if (tag === "table" || ar === "table" || ar === "grid" || el.closest("table") || el.querySelector("table, [role=table], [role=grid]")) return "table";
    let mediaArea = 0, chartArea = 0;
    el.querySelectorAll("img, video, picture").forEach((m) => { const mr = m.getBoundingClientRect(); mediaArea += mr.width * mr.height; });
    el.querySelectorAll("svg, canvas").forEach((m) => {
      if (m.closest("svg") !== m && m.tagName.toLowerCase() === "svg") return;
      const mr = m.getBoundingClientRect();
      if (mr.width * mr.height >= 0.02 * vw * vh) chartArea += mr.width * mr.height;
    });
    if (tag === "svg" || tag === "canvas") return el.querySelectorAll("path, rect, circle, line, polyline").length >= 6 ? "chart" : "media";
    if (mediaArea >= 0.5 * r.w * r.h) return "media";
    if (chartArea >= 0.3 * r.w * r.h) return "chart";
    if (tag === "form" || el.querySelectorAll("input, select, textarea").length >= 3) return "form";
    const h = el.matches("h1, h2") ? el : el.querySelector("h1, h2");
    const text = (el.innerText || "").trim();
    if (h && parseFloat(getComputedStyle(h).fontSize) >= 32 && text.length <= 700) return "heading";
    if (numberish(el) && r.w * r.h <= 0.06 * vw * vh && text.length <= 80) return "kpi";
    if (text.length / Math.max(1, (r.w * r.h) / 1000) > 1.2) return "text";
    const cs = getComputedStyle(el);
    const bg = cs.backgroundColor;
    const parentBg = el.parentElement ? getComputedStyle(el.parentElement).backgroundColor : "";
    const framed = (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== parentBg) || parseFloat(cs.borderTopWidth) > 0 || cs.boxShadow !== "none";
    return framed ? "panel" : "block";
  }

  function build(el, depth) {
    const r = rect(el);
    const area = r.w * r.h;
    const tag = el.tagName.toLowerCase();
    const node = { sig: sig(el), r: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.w), h: Math.round(r.h) }, depth, kids: [] };
    if (tag === "svg" || tag === "canvas" || tag === "table") {
      node.role = role(el, r);
      return node;
    }
    const group = repeatedGroup(el);
    if (group && group.coverage >= 0.5) {
      node.role = group.kind;
      node.group = group;
      return node;
    }
    const ks = kids(el).filter((k) => {
      const kr = rect(k);
      return kr.w * kr.h >= MIN_AREA;
    });
    if (ks.length === 1) {
      const kr = rect(ks[0]);
      if (kr.w * kr.h >= 0.6 * area) return build(ks[0], depth);
    }
    if (ks.length >= 2) {
      const kidsArea = ks.reduce((a, k) => { const kr = rect(k); return a + kr.w * kr.h; }, 0);
      if (kidsArea >= 0.3 * area || ks.length >= 3) node.kids = ks.map((k) => build(k, depth + 1));
    }
    if (node.kids.length === 0) node.role = role(el, r);
    return node;
  }
  const tree = build(document.body, 0);

  // Every repeated group on the page, for the signature (a group nested inside a region the block
  // tree did not split still counts).
  const groups = [];
  document.querySelectorAll("body *").forEach((p) => {
    if (p.closest("svg")) return;
    const g = repeatedGroup(p);
    if (g && g.kind !== "row") groups.push(g);
  });

  // Resolved grid tracks on large grids.
  const grids = [];
  document.querySelectorAll("body *").forEach((el) => {
    const cs = getComputedStyle(el);
    if (cs.display !== "grid" && cs.display !== "inline-grid") return;
    const r = rect(el);
    if (r.w * r.h < 0.12 * vw * vh) return;
    const tracks = cs.gridTemplateColumns.split(" ").map(parseFloat).filter((n) => !isNaN(n) && n > 0);
    if (tracks.length < 2) return;
    const min = Math.min(...tracks);
    grids.push({
      sig: sig(el), top: Math.round(r.y), w: Math.round(r.w), tracks: tracks.map((t) => Math.round(t)),
      ratios: tracks.map((t) => +(t / min).toFixed(2)), equal: tracks.every((t) => Math.abs(t - tracks[0]) <= 0.05 * tracks[0]),
    });
  });

  const leaves = [];
  (function walk(n) {
    if (n.kids.length === 0) leaves.push(n);
    n.kids.forEach(walk);
  })(tree);
  leaves.forEach((l, i) => (l.id = i));
  const firstViewport = leaves
    .filter((l) => l.r.y < vh && l.r.y + l.r.h > 0)
    .map((l) => ({ ...l, area: l.r.w * (Math.min(l.r.y + l.r.h, vh) - Math.max(0, l.r.y)) }));
  firstViewport.sort((a, b) => b.area - a.area);

  const rasterRole = [];
  const rasterId = [];
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const cx = ((col + 0.5) * vw) / cols;
      const cy = ((row + 0.5) * vh) / rows;
      let best = null;
      for (const l of leaves) {
        if (cx >= l.r.x && cx <= l.r.x + l.r.w && cy >= l.r.y && cy <= l.r.y + l.r.h) {
          if (!best || l.r.w * l.r.h < best.r.w * best.r.h) best = l;
        }
      }
      rasterRole.push(best ? best.role : "empty");
      rasterId.push(best ? best.id : -1);
    }
  }

  // Hero form in the top band of the first viewport.
  const band = firstViewport.filter((l) => l.r.y < vh * 0.35 && l.r.h >= vh * 0.35 && !["nav", "topbar", "sidebar", "rail"].includes(l.role));
  let hero = "none";
  if (band.some((l) => l.r.w >= vw * 0.6)) hero = "full";
  else if (band.filter((l) => l.r.w >= vw * 0.3).length >= 2) hero = "split";
  const fvColumns = (() => {
    const tallLeaves = firstViewport.filter((l) => l.r.h >= vh * 0.5 && l.r.w >= 120).sort((a, b) => a.r.x - b.r.x);
    let n = 0, lastRight = -1;
    for (const l of tallLeaves) { if (l.r.x >= lastRight - 8) { n++; lastRight = l.r.x + l.r.w; } }
    return n;
  })();
  const h1 = document.querySelector("h1");
  const h1r = h1 ? rect(h1) : null;

  return {
    docH, tree, groups, grids, leafCount: leaves.length, hero, fvColumns,
    firstViewport: firstViewport.map((l) => ({ id: l.id, role: l.role, sig: l.sig, r: l.r, share: +(l.area / (vw * vh)).toFixed(3) })),
    rasterRole, rasterId,
    h1: h1r ? { x: Math.round(h1r.x), y: Math.round(h1r.y), w: Math.round(h1r.w), size: Math.round(parseFloat(getComputedStyle(h1).fontSize)), text: (h1.innerText || "").trim().slice(0, 60) } : null,
    maxDepth: (function d(n) { return n.kids.length ? 1 + Math.max(...n.kids.map(d)) : 0; })(tree),
  };
}

function bucketShare(s) {
  return s >= 0.35 ? "L" : s >= 0.12 ? "M" : "S";
}
function shape(r) {
  const ar = r.w / Math.max(1, r.h);
  return ar >= 2.2 ? "wide" : ar <= 0.55 ? "tall" : "box";
}
function label(n) {
  if (n.kids.length) return "G";
  return `${n.role}:${shape(n.r)}:${bucketShare((n.r.w * n.r.h) / (VW * VH))}`;
}

// pq-grams, p=2 q=3, over the role-labelled block tree.
function pqgrams(tree, p = 2, q = 3) {
  const bag = new Map();
  const add = (k) => bag.set(k, (bag.get(k) || 0) + 1);
  (function walk(n, anc) {
    const a = [...anc, label(n)].slice(-p);
    while (a.length < p) a.unshift("*");
    const sib = n.kids.map(label);
    const padded = [...Array(q - 1).fill("*"), ...sib, ...Array(q - 1).fill("*")];
    for (let i = 0; i + q <= padded.length; i++) add([...a, ...padded.slice(i, i + q)].join("/"));
    n.kids.forEach((k) => walk(k, [...anc, label(n)]));
  })(tree, []);
  return bag;
}
function pqDist(a, b) {
  let inter = 0, na = 0, nb = 0;
  a.forEach((c) => (na += c));
  b.forEach((c) => (nb += c));
  a.forEach((c, k) => { if (b.has(k)) inter += Math.min(c, b.get(k)); });
  return 1 - (2 * inter) / (na + nb);
}
function rasterDist(a, b) {
  let d = 0;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) d++;
  return d / a.length;
}
// Same-region relation between each cell and its right and lower neighbour.
function edges(ids) {
  const out = [];
  for (let row = 0; row < RASTER_ROWS; row++) {
    for (let col = 0; col < RASTER_COLS; col++) {
      const i = row * RASTER_COLS + col;
      if (col + 1 < RASTER_COLS) out.push(ids[i] === ids[i + 1]);
      if (row + 1 < RASTER_ROWS) out.push(ids[i] === ids[i + RASTER_COLS]);
    }
  }
  return out;
}
function partitionDist(a, b) {
  const ea = edges(a), eb = edges(b);
  let d = 0;
  for (let i = 0; i < ea.length; i++) if (ea[i] !== eb[i]) d++;
  return d / ea.length;
}

function signature(m) {
  const fv = m.firstViewport;
  const content = fv.filter((l) => !["nav", "topbar", "sidebar", "rail", "footer"].includes(l.role));
  const largest = content[0];
  const second = content[1];
  const heroRatio = largest && second ? largest.share / Math.max(0.001, second.share) : largest ? 99 : 0;
  const cardGrids = m.groups.filter((g) => g.kind === "card-grid" || g.kind === "pricing");
  const statRows = m.groups.filter((g) => g.kind === "stat-row");
  const roles = new Set(fv.map((l) => l.role));
  return {
    topnav: roles.has("nav") || roles.has("topbar"),
    side: roles.has("sidebar") ? "sidebar" : roles.has("rail") ? "rail" : "none",
    hero: m.hero,
    dominant: largest ? largest.role : "none",
    dominance: heroRatio >= 3 ? "hero" : heroRatio >= 1.5 ? "dominant" : "peers",
    fvStatRow: statRows.some((g) => g.inFirstViewport),
    fvCardGrid: cardGrids.some((g) => g.inFirstViewport),
    cardGrids: cardGrids.length >= 2 ? "2+" : String(cardGrids.length),
    threeUp: cardGrids.some((g) => g.count === 3 && g.cols === 3),
    fvRegions: fv.length <= 3 ? "≤3" : fv.length <= 7 ? "4–7" : "8+",
    fvColumns: m.fvColumns >= 3 ? "3+" : String(m.fvColumns),
    length: m.docH / VH >= 6 ? "long" : m.docH / VH >= 2.5 ? "mid" : "short",
  };
}
function sigDist(a, b) {
  const keys = Object.keys(a);
  return keys.filter((k) => a[k] !== b[k]).length / keys.length;
}
function topologyString(m) {
  const parts = [];
  const s = signature(m);
  if (s.topnav) parts.push("topnav");
  if (s.side !== "none") parts.push(s.side);
  if (s.hero !== "none") parts.push(`hero-${s.hero}`);
  parts.push(`fv[${m.firstViewport.slice(0, 4).map((l) => `${l.role}${Math.round(l.share * 100)}`).join(" ")}]`);
  m.groups
    .filter((g) => g.kind !== "list" && g.kind !== "table")
    .sort((a, b) => a.top - b.top)
    .forEach((g) => parts.push(`${g.kind}×${g.count}${g.kind !== "stat-row" ? `(${g.cols}col)` : ""}${g.inFirstViewport ? "^" : ""}`));
  const grid = m.grids.find((g) => !g.equal);
  if (grid) parts.push(`tracks ${grid.ratios.join(":")}`);
  return parts.join(" · ");
}

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1, reducedMotion: "reduce" });
await context.route("**/*", (route) => {
  const url = route.request().url();
  if (url.startsWith("file:") || url.startsWith("data:")) return route.continue();
  return route.abort();
});
const results = [];
for (const f of files) {
  const page = await context.newPage();
  const abs = path.resolve(f);
  try {
    await page.goto(pathToFileURL(abs).href, { waitUntil: "load", timeout: 20000 });
    await page.waitForTimeout(300);
    const m = await page.evaluate(extract, { vw: VW, vh: VH, cols: RASTER_COLS, rows: RASTER_ROWS });
    const rel = path.relative(repoRoot, abs);
    results.push({ file: rel, title: await page.title(), ...m, signature: signature(m), topology: topologyString(m) });
    console.error(`ok  ${rel}`);
  } catch (e) {
    console.error(`ERR ${f}: ${e.message}`);
  }
  await page.close();
}
await browser.close();

const bags = results.map((r) => pqgrams(r.tree));
const n = results.length;
const matrix = { partition: [], raster: [], pqgram: [], sig: [] };
for (let i = 0; i < n; i++) {
  for (const k of Object.keys(matrix)) matrix[k].push([]);
  for (let j = 0; j < n; j++) {
    matrix.partition[i].push(+partitionDist(results[i].rasterId, results[j].rasterId).toFixed(3));
    matrix.raster[i].push(+rasterDist(results[i].rasterRole, results[j].rasterRole).toFixed(3));
    matrix.pqgram[i].push(+pqDist(bags[i], bags[j]).toFixed(3));
    matrix.sig[i].push(+sigDist(results[i].signature, results[j].signature).toFixed(3));
  }
}

const out = {
  viewport: { width: VW, height: VH }, raster: { cols: RASTER_COLS, rows: RASTER_ROWS }, generated: new Date().toISOString(),
  builds: results.map((r) => ({
    file: r.file, title: r.title, docH: r.docH, leafCount: r.leafCount, maxDepth: r.maxDepth, hero: r.hero, fvColumns: r.fvColumns,
    h1: r.h1, signature: r.signature, topology: r.topology, firstViewport: r.firstViewport, groups: r.groups, grids: r.grids,
    rasterRole: r.rasterRole, rasterId: r.rasterId,
  })),
  matrix,
};
if (outPath) {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(out));
  console.error(`wrote ${outPath}`);
}

console.log("| # | build | topology | signature |");
console.log("|---|---|---|---|");
results.forEach((r, i) => {
  const s = r.signature;
  const sigStr = [s.topnav ? "topnav" : "", s.side !== "none" ? s.side : "", `hero=${s.hero}`, `dom=${s.dominant}/${s.dominance}`, s.fvStatRow ? "fv-stat" : "", s.fvCardGrid ? "fv-cards" : "", `cards=${s.cardGrids}`, s.threeUp ? "3-up" : "", `fv=${s.fvRegions}`, `cols=${s.fvColumns}`, s.length].filter(Boolean).join(" ");
  console.log(`| ${i} | ${r.file.replace("figma-design-workspace/", "")} | ${r.topology} | ${sigStr} |`);
});
