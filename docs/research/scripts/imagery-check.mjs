#!/usr/bin/env node
// Acceptance check for the imagery path (docs/doperpowers/specs/2026-09-08-imagery-path.md, A1–A4).
//
//   node imagery-check.mjs <build-dir> [<build-dir>…]
//
// For each build: renders index.html in Chromium at 1440 × 900, writes shot-fv.png and
// shot-full.png beside it, and reports every <img> — whether it loaded, its alt, intrinsic size
// attributes, the container's background — plus a HEAD check of each remote src, whether that
// src appears in the build's saved images/*.json (so nothing was guessed), whether a credit line
// is present, whether DESIGN.md §4 names a rung, and the mechanical gate (no page error, no
// horizontal overflow, no placeholder text). Output is JSON on stdout.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("/Users/new/.npm/_npx/e41f203b7505f1fb/node_modules/playwright");

async function head(url) {
  const ac = new AbortController(); const t = setTimeout(() => ac.abort(), 10000);
  try {
    const r = await fetch(url, { method: "HEAD", redirect: "follow", signal: ac.signal });
    return { ok: r.ok && (r.headers.get("content-type") || "").startsWith("image/"), status: r.status };
  } catch (e) { return { ok: false, status: String(e.message) }; }
  finally { clearTimeout(t); }
}

function savedCreators(dir) {
  const d = path.join(dir, "images"); const names = new Set();
  if (!fs.existsSync(d)) return names;
  for (const f of fs.readdirSync(d)) {
    if (!f.startsWith("pick") || !f.endsWith(".json")) continue;
    try { const j = JSON.parse(fs.readFileSync(path.join(d, f), "utf8")); if (j.creator) names.add(j.creator); } catch { /* not evidence */ }
  }
  return names;
}

function savedUrls(dir) {
  const d = path.join(dir, "images"); const urls = new Set();
  if (!fs.existsSync(d)) return urls;
  for (const f of fs.readdirSync(d)) {
    if (!f.endsWith(".json")) continue;
    try {
      const j = JSON.parse(fs.readFileSync(path.join(d, f), "utf8"));
      const walk = (x) => { if (!x) return; if (typeof x === "string" && /^https?:\/\//.test(x)) urls.add(x.split("&w=")[0].split("?")[0]); else if (typeof x === "object") Object.values(x).forEach(walk); };
      walk(j);
    } catch { /* a partial file is simply not evidence */ }
  }
  return urls;
}

async function check(browser, dir) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e.message)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto("file://" + path.join(dir, "index.html"), { waitUntil: "load" });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(dir, "shot-fv.png"), fullPage: false });
  // Lazy-loaded images only fetch when they near the viewport; walk the page so the full
  // capture and the loaded flags reflect the page as a reader scrolls it, then return to top.
  const total = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < total; y += 700) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(150); }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(dir, "shot-full.png"), fullPage: true });
  const r = await page.evaluate(() => {
    const imgs = [...document.querySelectorAll("img")].map((el) => {
      let p = el.parentElement, bg = null;
      while (p && p !== document.body) { const b = getComputedStyle(p).backgroundColor; if (b && b !== "rgba(0, 0, 0, 0)" && b !== "transparent") { bg = b; break; } p = p.parentElement; }
      const own = getComputedStyle(el).backgroundColor;
      return {
        src: el.currentSrc || el.getAttribute("src"), loaded: el.complete && el.naturalWidth > 0, natural: [el.naturalWidth, el.naturalHeight],
        alt: el.getAttribute("alt"), width: el.getAttribute("width"), height: el.getAttribute("height"),
        containerBg: (own && own !== "rgba(0, 0, 0, 0)" && own !== "transparent") ? own : bg,
        rendered: [Math.round(el.getBoundingClientRect().width), Math.round(el.getBoundingClientRect().height)],
        inFigure: !!el.closest("figure"), captioned: !!el.closest("figure")?.querySelector("figcaption"),
      };
    });
    const text = document.body.innerText || "";
    return {
      imgs,
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      placeholder: /lorem ipsum|placeholder/i.test(text),
      creditLines: (text.match(/Photo by [^\n]{2,60}on Unsplash|licensed under CC|\bCC BY\b/g) || []).length,
      text,
      svgCount: document.querySelectorAll("svg").length,
      height: document.documentElement.scrollHeight,
    };
  });
  await page.close();
  const saved = savedUrls(dir);
  for (const im of r.imgs) {
    if (im.src && /^https?:\/\//.test(im.src)) {
      im.remote = true; im.head = await head(im.src);
      im.inSavedSearch = saved.has(im.src.split("&w=")[0].split("?")[0]);
    } else { im.remote = false; im.head = null; im.inSavedSearch = null; }
  }
  const design = fs.existsSync(path.join(dir, "DESIGN.md")) ? fs.readFileSync(path.join(dir, "DESIGN.md"), "utf8") : "";
  const rung = (design.match(/\b(project asset|unsplash|openverse|drawn)\b/gi) || []).map((s) => s.toLowerCase());
  const photos = r.imgs.filter((i) => i.remote);
  // Every photographer the build picked must be named on the page; "via Unsplash" is not a credit.
  const creators = [...savedCreators(dir)];
  const uncredited = creators.filter((n) => !r.text.includes(n));
  return {
    creators: creators.length, uncredited,
    dir: path.basename(dir), errors: errors.slice(0, 5), overflow: r.overflow, placeholder: r.placeholder, height: r.height, svgCount: r.svgCount,
    images: r.imgs.length, photographs: photos.length,
    A1_photograph: photos.some((i) => i.loaded && i.head?.ok) && rung.length > 0,
    A2_attributes: r.imgs.length > 0 && r.imgs.every((i) => i.alt && i.alt.trim() && i.width && i.height && i.containerBg) && (photos.length === 0 || (creators.length > 0 && uncredited.length === 0)),
    A3_notGuessed: photos.every((i) => i.inSavedSearch),
    A4_gate: errors.length === 0 && !r.overflow && !r.placeholder,
    creditLines: r.creditLines, rungsNamed: [...new Set(rung)],
    imgs: r.imgs,
  };
}

const dirs = process.argv.slice(2).map((d) => path.resolve(d));
if (!dirs.length) { console.error("usage: imagery-check.mjs <build-dir>…"); process.exit(1); }
const browser = await chromium.launch();
const out = [];
for (const d of dirs) out.push(await check(browser, d));
await browser.close();
process.stdout.write(JSON.stringify(out, null, 1) + "\n");
