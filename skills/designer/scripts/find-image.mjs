#!/usr/bin/env node
// scripts/find-image.mjs — the imagery ladder's first three rungs: the project's own image assets,
// an Unsplash search when an access key is present, an Openverse search otherwise. Every search
// candidate is verified to resolve before it is reported, because a guessed photo URL ships as a
// broken image. The fourth rung, drawing the artifact as content, is the agent's own work.
//
//   node find-image.mjs inventory [dir]
//       image files already in the project, with dimensions — these outrank any search
//   node find-image.mjs search "<query>" [--n 6] [--orientation landscape|portrait|squarish]
//                              [--source auto|unsplash|openverse] [--width 1600]
//       verified candidates as JSON: url, size, colour, alt, creator, licence, credit line
//   node find-image.mjs pick <id>
//       the chosen photo's <figure> snippet and credit; for Unsplash this also registers the use,
//       which its API terms require when a photo is placed
//
// The Unsplash key is read from UNSPLASH_ACCESS_KEY, else from ~/.config/designer/unsplash-key.
// Without a key the search rung is Openverse (Creative Commons, no key, lower editorial quality).
// Both services meter anonymous or demo use by the hour (Unsplash demo: 50 requests), so results
// are cached under ~/.cache/designer/find-image for a day — a repeated query costs nothing, a
// pick costs one request instead of two — and an exhausted Unsplash falls through to Openverse.
import { readFileSync, readdirSync, statSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, extname, relative } from "node:path";
import { homedir } from "node:os";
import { createHash } from "node:crypto";

const IMAGE_EXT = new Set([".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg"]);
const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".next", "out", "coverage", ".cache"]);
const APP_NAME = "designer";
const UTM = `?utm_source=${APP_NAME}&utm_medium=referral`;

// ---------- dimensions from headers, so the inventory reports a size without decoding ----------
export function dimensions(buf, ext) {
  try {
    if (ext === ".svg") {
      const s = buf.toString("utf8", 0, Math.min(buf.length, 4096));
      const vb = s.match(/viewBox\s*=\s*["']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)/i);
      if (vb) return { width: Math.round(+vb[1]), height: Math.round(+vb[2]) };
      const w = s.match(/<svg[^>]*\swidth\s*=\s*["']([\d.]+)/i), h = s.match(/<svg[^>]*\sheight\s*=\s*["']([\d.]+)/i);
      return w && h ? { width: Math.round(+w[1]), height: Math.round(+h[1]) } : null;
    }
    if (buf.length >= 24 && buf.readUInt32BE(0) === 0x89504e47) {
      return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
    }
    if (buf.length >= 10 && buf.toString("ascii", 0, 3) === "GIF") {
      return { width: buf.readUInt16LE(6), height: buf.readUInt16LE(8) };
    }
    if (buf.length >= 4 && buf[0] === 0xff && buf[1] === 0xd8) {
      let i = 2;
      while (i + 9 < buf.length) {
        if (buf[i] !== 0xff) { i++; continue; }
        const marker = buf[i + 1];
        if (marker === 0xd8 || marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) { i += 2; continue; }
        const len = buf.readUInt16BE(i + 2);
        const sof = (marker >= 0xc0 && marker <= 0xcf) && ![0xc4, 0xc8, 0xcc].includes(marker);
        if (sof) return { height: buf.readUInt16BE(i + 5), width: buf.readUInt16BE(i + 7) };
        i += 2 + len;
      }
      return null;
    }
    if (buf.length >= 30 && buf.toString("ascii", 0, 4) === "RIFF" && buf.toString("ascii", 8, 12) === "WEBP") {
      const chunk = buf.toString("ascii", 12, 16);
      if (chunk === "VP8 ") return { width: buf.readUInt16LE(26) & 0x3fff, height: buf.readUInt16LE(28) & 0x3fff };
      if (chunk === "VP8L") {
        const b = buf;
        return { width: 1 + ((b[21] | ((b[22] & 0x3f) << 8))), height: 1 + (((b[22] >> 6) | (b[23] << 2) | ((b[24] & 0x0f) << 10))) };
      }
      if (chunk === "VP8X") return { width: 1 + (buf[24] | (buf[25] << 8) | (buf[26] << 16)), height: 1 + (buf[27] | (buf[28] << 8) | (buf[29] << 16)) };
    }
  } catch { /* a truncated header reads as unknown size */ }
  return null;
}

// ---------- rung one: the project's own assets ----------
export function inventory(root, limit = 200) {
  const out = [];
  const walk = (dir, depth) => {
    if (out.length >= limit || depth > 8) return;
    let entries;
    try { entries = readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (out.length >= limit) return;
      const p = join(dir, e.name);
      if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name) && !e.name.startsWith(".")) walk(p, depth + 1); continue; }
      const ext = extname(e.name).toLowerCase();
      if (!IMAGE_EXT.has(ext)) continue;
      const bytes = statSync(p).size;
      const head = readHead(p, ext === ".svg" ? 4096 : 64 * 1024);
      out.push({ path: relative(root, p), kind: ext === ".svg" ? "svg" : "raster", bytes, ...(dimensions(head, ext) || { width: null, height: null }) });
    }
  };
  walk(root, 0);
  return out;
}

function readHead(p, n) {
  const buf = readFileSync(p);
  return buf.length > n ? buf.subarray(0, n) : buf;
}

// ---------- rungs two and three: the searches, normalised to one shape ----------
export function normalizeUnsplash(r, width) {
  const name = r.user?.name || "Unknown";
  return {
    source: "unsplash",
    id: r.id,
    url: `${r.urls.raw}&w=${width}&fit=crop&auto=format&q=80`,
    page: `${r.links.html}${UTM}`,
    width: r.width, height: r.height, color: r.color || null,
    alt: r.alt_description || r.description || null,
    description: r.description || null,
    creator: name, creatorUrl: r.user?.links?.html ? `${r.user.links.html}${UTM}` : null,
    license: "Unsplash License", licenseUrl: "https://unsplash.com/license",
    credit: `Photo by ${name} on Unsplash`,
    downloadLocation: r.links.download_location,
  };
}

export function normalizeOpenverse(r) {
  const lic = r.license ? `${String(r.license).toUpperCase()}${r.license_version ? " " + r.license_version : ""}` : null;
  return {
    source: "openverse",
    id: r.id,
    url: r.url,
    page: r.foreign_landing_url || null,
    width: r.width || null, height: r.height || null, color: null,
    alt: r.title || null, description: null,
    creator: r.creator || null, creatorUrl: r.creator_url || null,
    license: lic, licenseUrl: r.license_url || null,
    credit: r.attribution || (r.creator ? `"${r.title}" by ${r.creator}, ${lic}` : null),
    downloadLocation: null,
  };
}

export function orientationParams(o) {
  if (!o) return { unsplash: "", openverse: "" };
  const map = { landscape: "wide", portrait: "tall", squarish: "square" };
  if (!map[o]) throw new Error(`--orientation must be landscape, portrait or squarish (got ${o})`);
  return { unsplash: `&orientation=${o}`, openverse: `&aspect_ratio=${map[o]}` };
}

export function unsplashKey(env = process.env) {
  if (env.UNSPLASH_ACCESS_KEY) return env.UNSPLASH_ACCESS_KEY.trim();
  const f = join(homedir(), ".config", "designer", "unsplash-key");
  if (existsSync(f)) return readFileSync(f, "utf8").trim() || null;
  return null;
}

class HttpError extends Error { constructor(status, host) { super(`${status} from ${host}`); this.status = status; this.host = host; } }

async function fetchJson(url, headers = {}) {
  const ac = new AbortController(); const t = setTimeout(() => ac.abort(), 15000);
  try {
    const res = await fetch(url, { headers, signal: ac.signal });
    if (!res.ok) throw new HttpError(res.status, new URL(url).host);
    const remaining = res.headers.get("x-ratelimit-remaining");
    const body = await res.json();
    return { body, remaining: remaining == null ? null : +remaining };
  } finally { clearTimeout(t); }
}

// ---------- the cache: a day per query, and every candidate by id for pick ----------
const CACHE = join(homedir(), ".cache", "designer", "find-image");
const DAY = 24 * 3600 * 1000;
function cacheRead(name, maxAge = DAY) {
  const f = join(CACHE, name);
  try { if (Date.now() - statSync(f).mtimeMs > maxAge) return null; return JSON.parse(readFileSync(f, "utf8")); } catch { return null; }
}
function cacheWrite(name, value) {
  try { mkdirSync(join(CACHE, "by-id"), { recursive: true }); writeFileSync(join(CACHE, name), JSON.stringify(value)); } catch { /* a cache that cannot write is just slower */ }
}
export const cacheKey = (parts) => createHash("sha1").update(parts.join("|")).digest("hex").slice(0, 20) + ".json";

// A candidate is reported only if its URL answers with an image; a photo that 404s is worse
// than no photo, because it ships as a broken-image placeholder. Some hosts refuse HEAD, so a
// refusal is retried as a one-byte GET before the candidate is dropped.
export async function verify(c, fetchImpl = fetch) {
  const attempt = async (init) => {
    const ac = new AbortController(); const t = setTimeout(() => ac.abort(), 10000);
    try {
      const res = await fetchImpl(c.url, { ...init, redirect: "follow", signal: ac.signal });
      const type = res.headers.get("content-type") || "";
      return (res.ok || res.status === 206) && type.startsWith("image/");
    } catch { return false; }
    finally { clearTimeout(t); }
  };
  return (await attempt({ method: "HEAD" })) || (await attempt({ method: "GET", headers: { Range: "bytes=0-0" } }));
}

async function searchUnsplash(q, n, o, width, key) {
  const { body, remaining } = await fetchJson(`https://api.unsplash.com/search/photos?query=${q}&per_page=${n}&content_filter=high${o.unsplash}`,
    { Authorization: `Client-ID ${key}`, "Accept-Version": "v1" });
  return { raw: body.results.map((r) => normalizeUnsplash(r, width)), remaining };
}
async function searchOpenverse(q, n, o) {
  const { body } = await fetchJson(`https://api.openverse.org/v1/images/?q=${q}&page_size=${n}&license_type=commercial&mature=false${o.openverse}`);
  return { raw: body.results.map(normalizeOpenverse), remaining: null };
}

export async function search(query, { n = 6, orientation = null, source = "auto", width = 1600, key = unsplashKey() } = {}) {
  const o = orientationParams(orientation);
  const q = encodeURIComponent(query);
  const wantUnsplash = source === "unsplash" || (source === "auto" && key);
  const ck = cacheKey([wantUnsplash ? "unsplash" : "openverse", query, n, orientation || "", width]);
  const hit = cacheRead(ck);
  if (hit) return { ...hit, cached: true };
  let raw, used, remaining = null, fallback = null;
  if (wantUnsplash) {
    if (!key) throw new Error("no Unsplash access key: set UNSPLASH_ACCESS_KEY or write ~/.config/designer/unsplash-key");
    try { ({ raw, remaining } = await searchUnsplash(q, n, o, width, key)); used = "unsplash"; }
    catch (e) {
      if (source === "unsplash" || !(e instanceof HttpError) || ![403, 429].includes(e.status)) throw e;
      // The demo quota resets on the hour; the next rung answers now, and the record says so.
      fallback = `unsplash ${e.status} (hourly quota exhausted) → openverse`;
      process.stderr.write(`find-image: ${fallback}\n`);
    }
  }
  if (!used) {
    try { ({ raw } = await searchOpenverse(q, n, o)); used = "openverse"; }
    catch (e) {
      if (e instanceof HttpError && [403, 429].includes(e.status)) throw new Error(`${e.message}: Openverse's anonymous quota is spent for now; wait, or draw the slot (rung 4) and record it`);
      throw e;
    }
  }
  const checks = await Promise.all(raw.map((c) => verify(c)));
  const candidates = raw.filter((_, i) => checks[i]);
  for (const c of candidates) cacheWrite(join("by-id", c.id + ".json"), c);
  const out = { query, source: used, requested: raw.length, verified: candidates.length, candidates };
  if (fallback) out.fallback = fallback;
  if (remaining != null) out.rateLimitRemaining = remaining;
  cacheWrite(ck, out);
  return { ...out, cached: false };
}

// The credit, as HTML: beside the photo in a figcaption, or gathered into one credits line per
// page that names every photographer — either placement satisfies the sources' terms.
export function creditHtml(c) {
  if (c.source === "unsplash") return `Photo by <a href="${c.creatorUrl}">${c.creator}</a> on <a href="https://unsplash.com/${UTM}">Unsplash</a>`;
  if (c.creator && c.creatorUrl) return `<a href="${c.page || c.creatorUrl}">${c.alt || "Photo"}</a> by <a href="${c.creatorUrl}">${c.creator}</a>, ${c.license}`;
  return c.credit || "";
}

export function snippet(c) {
  const alt = (c.alt || "").replace(/"/g, "&quot;");
  return `<figure>\n  <img src="${c.url}" alt="${alt}" width="${c.width}" height="${c.height}" loading="lazy" style="background:${c.color || "#e5e5e5"}">\n  <figcaption>${creditHtml(c)}</figcaption>\n</figure>`;
}

export async function pick(id, { key = unsplashKey(), width = 1600 } = {}) {
  const isOpenverse = /^[0-9a-f]{8}-[0-9a-f]{4}-/i.test(id);
  let c = cacheRead(join("by-id", id + ".json"), 7 * DAY);
  if (isOpenverse) {
    if (!c) c = normalizeOpenverse((await fetchJson(`https://api.openverse.org/v1/images/${id}/`)).body);
  } else {
    if (!key) throw new Error("pick needs the Unsplash access key");
    const h = { Authorization: `Client-ID ${key}`, "Accept-Version": "v1" };
    if (!c) c = normalizeUnsplash((await fetchJson(`https://api.unsplash.com/photos/${id}`, h)).body, width);
    await fetchJson(c.downloadLocation, h); // registers the use, as the API guidelines ask
  }
  return { ...c, creditHtml: creditHtml(c), snippet: snippet(c) };
}

// ---------- CLI ----------
function flag(args, name, dflt) { const i = args.indexOf(name); return i === -1 ? dflt : args[i + 1]; }

async function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  const out = (x) => process.stdout.write(JSON.stringify(x, null, 1) + "\n");
  if (cmd === "inventory") {
    const root = rest[0] && !rest[0].startsWith("--") ? rest[0] : process.cwd();
    const files = inventory(root);
    out({ root, count: files.length, files });
  } else if (cmd === "search") {
    const query = rest[0];
    if (!query || query.startsWith("--")) throw new Error('search needs a query: search "<subject> <activity or environment> <lighting>"');
    out(await search(query, { n: +flag(rest, "--n", 6), orientation: flag(rest, "--orientation", null), source: flag(rest, "--source", "auto"), width: +flag(rest, "--width", 1600) }));
  } else if (cmd === "pick") {
    if (!rest[0]) throw new Error("pick needs a photo id from a search result");
    out(await pick(rest[0], { width: +flag(rest, "--width", 1600) }));
  } else {
    process.stderr.write("usage: find-image.mjs inventory [dir] | search \"<query>\" [--n 6] [--orientation landscape|portrait|squarish] [--source auto|unsplash|openverse] [--width 1600] | pick <id>\n");
    process.exit(1);
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  main().catch((e) => { process.stderr.write(`find-image: ${e.message}\n`); process.exit(1); });
}
