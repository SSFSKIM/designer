#!/usr/bin/env node
/* global process, Buffer, console, fetch -- a build-time script, run by Node, never shipped */
/**
 * The terminal page's environment, a relief map of the Lake Tahoe basin, built from real
 * elevation data into three files the page fetches.
 *
 *   node apps/demo/scripts/build-terminal-relief.mjs
 *
 * The source is Terrain Tiles on AWS (the Tilezen/Mapzen "terrarium" encoding, zoom 12, about
 * 30 m a pixel here), which over the United States is the USGS 3D Elevation Program, a public
 * domain dataset; its required attribution (`ATTRIBUTION` below) is carried by
 * `src/gallery/terminal/data/CREDITS.md`, written into `relief.json`, and shown on the page.
 * Tiles are cached under `tmp/terminal-relief/tiles` at the repository root, which is gitignored.
 * The hillshade is encoded by `cwebp` (libwebp's encoder), which has to be on the PATH.
 *
 * It writes, under `src/gallery/terminal/data/`:
 *
 * - `relief.webp`: a grey hillshade of the whole region (Horn's method, light from the
 *   north-west at 45°), which the page tints per colour scheme;
 * - `relief.bin`: the vector layers, as polylines in the hillshade's own pixel space: contour
 *   lines every 50 m and the shorelines of the lakes. The layout is described at `writeVectors`;
 * - `relief.json`: the source and its attribution line, the region's geometry and elevation
 *   range, the lakes, the labelled summits with the elevation the data itself reads at each (a
 *   30 m grid rounds a summit down; these are not survey heights), the towns, and the
 *   California–Nevada line.
 *
 * Every lake is flood-filled from a seed on its surface and checked to be flat and large, and
 * every summit is found as the highest point near where it is named, so a wrong coordinate fails
 * the build rather than drawing a lake in a valley or a peak on a slope.
 */
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { PNG } from "pngjs";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "../../..");
const out = resolve(here, "../src/gallery/terminal/data");
const cache = resolve(repo, "tmp/terminal-relief/tiles");

/** Progress goes to stdout; the lint allows the console only its warnings and errors. */
const say = (line) => process.stdout.write(`${line}\n`);

/** The line the source's attribution terms ask for, word for word. */
const ATTRIBUTION =
  "United States 3DEP (formerly NED) and global GMTED2010 and SRTM terrain data courtesy of the " +
  "U.S. Geological Survey";
const ZOOM = 12;
const TILE = 256;
/** The region: the basin with room to crop any viewport's aspect around the lake. */
const BOUNDS = { west: -120.4, east: -119.66, south: 38.78, north: 39.4 };
const CONTOUR_INTERVAL = 50;
const INDEX_EVERY = 5;
/** The lakes, each seeded on its own surface. */
const LAKES = [
  { name: "Lake Tahoe", lat: 39.09, lon: -120.03 },
  { name: "Fallen Leaf Lake", lat: 38.895, lon: -120.058 },
  { name: "Donner Lake", lat: 39.323, lon: -120.265 },
  { name: "Marlette Lake", lat: 39.175, lon: -119.905 },
];
/** Summits, searched for within `SUMMIT_SEARCH_M` of the named coordinate. */
const SUMMITS = [
  { name: "Freel Peak", lat: 38.8577, lon: -119.8994 },
  { name: "Mount Rose", lat: 39.3438, lon: -119.9179 },
  { name: "Mount Tallac", lat: 38.9063, lon: -120.0985 },
  { name: "Pyramid Peak", lat: 38.8474, lon: -120.1621 },
  { name: "Castle Peak", lat: 39.3667, lon: -120.3464 },
];
const SUMMIT_SEARCH_M = 1200;
const TOWNS = [
  { name: "Tahoe City", lat: 39.1677, lon: -120.1452 },
  { name: "South Lake Tahoe", lat: 38.9332, lon: -119.9844 },
  { name: "Incline Village", lat: 39.2513, lon: -119.9724 },
  { name: "Kings Beach", lat: 39.2377, lon: -120.0266 },
  { name: "Truckee", lat: 39.328, lon: -120.1833 },
  { name: "Glenbrook", lat: 39.088, lon: -119.9396 },
];
const FEATURES = [{ name: "Emerald Bay", lat: 38.953, lon: -120.105 }];

// --- Web Mercator ------------------------------------------------------------------------------

const worldX = (lon) => ((lon + 180) / 360) * 2 ** ZOOM * TILE;
const worldY = (lat) => {
  const s = Math.sin((lat * Math.PI) / 180);
  return (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * 2 ** ZOOM * TILE;
};

const x0 = Math.floor(worldX(BOUNDS.west));
const x1 = Math.ceil(worldX(BOUNDS.east));
const y0 = Math.floor(worldY(BOUNDS.north));
const y1 = Math.ceil(worldY(BOUNDS.south));
const W = x1 - x0;
const H = y1 - y0;
const px = (lat, lon) => ({ x: worldX(lon) - x0, y: worldY(lat) - y0 });
/** Ground metres per pixel at the region's middle latitude. */
const midLat = (BOUNDS.north + BOUNDS.south) / 2;
const METRES_PER_PX = (40075016.686 * Math.cos((midLat * Math.PI) / 180)) / (2 ** ZOOM * TILE);

// --- Tiles -------------------------------------------------------------------------------------

async function tile(tx, ty) {
  const path = resolve(cache, `${ZOOM}-${tx}-${ty}.png`);
  if (!existsSync(path)) {
    const url = `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${ZOOM}/${tx}/${ty}.png`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`${url} answered ${response.status}`);
    writeFileSync(path, Buffer.from(await response.arrayBuffer()));
  }
  return PNG.sync.read(readFileSync(path));
}

async function elevation() {
  mkdirSync(cache, { recursive: true });
  const grid = new Float32Array(W * H);
  const jobs = [];
  for (let ty = Math.floor(y0 / TILE); ty <= Math.floor((y1 - 1) / TILE); ty++) {
    for (let tx = Math.floor(x0 / TILE); tx <= Math.floor((x1 - 1) / TILE); tx++) {
      jobs.push([tx, ty]);
    }
  }
  for (let i = 0; i < jobs.length; i += 8) {
    const batch = jobs.slice(i, i + 8);
    const pngs = await Promise.all(batch.map(([tx, ty]) => tile(tx, ty)));
    batch.forEach(([tx, ty], k) => {
      const { data } = pngs[k];
      for (let v = 0; v < TILE; v++) {
        const gy = ty * TILE + v - y0;
        if (gy < 0 || gy >= H) continue;
        for (let u = 0; u < TILE; u++) {
          const gx = tx * TILE + u - x0;
          if (gx < 0 || gx >= W) continue;
          const o = (v * TILE + u) * 4;
          // Terrarium: metres = R × 256 + G + B / 256 − 32768.
          grid[gy * W + gx] = data[o] * 256 + data[o + 1] + data[o + 2] / 256 - 32768;
        }
      }
    });
  }
  say(`${jobs.length} tiles, ${W} × ${H} px, ${METRES_PER_PX.toFixed(1)} m/px`);
  return grid;
}

// --- Lakes and summits -------------------------------------------------------------------------

/** Flood-fills a lake's flat surface from its seed; throws if the seed is not on one. */
function floodLake(grid, lake) {
  const seed = px(lake.lat, lake.lon);
  const start = Math.round(seed.y) * W + Math.round(seed.x);
  const level = grid[start];
  const mask = new Uint8Array(W * H);
  const stack = [start];
  mask[start] = 1;
  let area = 0;
  while (stack.length > 0) {
    const i = stack.pop();
    area++;
    const x = i % W;
    const y = (i - x) / W;
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx;
      const ny = y + dy;
      if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
      const n = ny * W + nx;
      if (mask[n] === 0 && Math.abs(grid[n] - level) < 0.8) {
        mask[n] = 1;
        stack.push(n);
      }
    }
  }
  const km2 = (area * METRES_PER_PX ** 2) / 1e6;
  if (km2 < 0.3) throw new Error(`${lake.name}: the seed is not on a lake (${km2.toFixed(2)} km²)`);
  say(`${lake.name}: ${level.toFixed(1)} m, ${km2.toFixed(1)} km²`);
  return { mask, level, km2 };
}

function findSummit(grid, summit) {
  const at = px(summit.lat, summit.lon);
  const r = SUMMIT_SEARCH_M / METRES_PER_PX;
  let best = { x: 0, y: 0, z: -Infinity };
  for (let y = Math.max(0, Math.floor(at.y - r)); y <= Math.min(H - 1, Math.ceil(at.y + r)); y++) {
    for (let x = Math.max(0, Math.floor(at.x - r)); x <= Math.min(W - 1, Math.ceil(at.x + r)); x++) {
      if ((x - at.x) ** 2 + (y - at.y) ** 2 > r * r) continue;
      const z = grid[y * W + x];
      if (z > best.z) best = { x, y, z };
    }
  }
  // A summit found on the search circle's edge is a slope, not the named peak.
  if (Math.hypot(best.x - at.x, best.y - at.y) > r - 1.5) {
    throw new Error(`${summit.name}: the highest point near it is on the search edge`);
  }
  say(`${summit.name}: ${Math.round(best.z)} m, ${(Math.hypot(best.x - at.x, best.y - at.y) * METRES_PER_PX).toFixed(0)} m from the named point`);
  return { name: summit.name, x: best.x + 0.5, y: best.y + 0.5, elevation: Math.round(best.z) };
}

// --- Hillshade ---------------------------------------------------------------------------------

function blur(grid, sigma) {
  const radius = Math.ceil(sigma * 3);
  const kernel = [];
  let sum = 0;
  for (let k = -radius; k <= radius; k++) {
    const w = Math.exp(-(k * k) / (2 * sigma * sigma));
    kernel.push(w);
    sum += w;
  }
  const norm = kernel.map((w) => w / sum);
  const tmp = new Float32Array(W * H);
  const res = new Float32Array(W * H);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let acc = 0;
      for (let k = -radius; k <= radius; k++) {
        acc += grid[y * W + Math.min(W - 1, Math.max(0, x + k))] * norm[k + radius];
      }
      tmp[y * W + x] = acc;
    }
  }
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let acc = 0;
      for (let k = -radius; k <= radius; k++) {
        acc += tmp[Math.min(H - 1, Math.max(0, y + k)) * W + x] * norm[k + radius];
      }
      res[y * W + x] = acc;
    }
  }
  return res;
}

/**
 * Horn's hillshade, the sun at azimuth 315° (the north-west) and 45° up, with a soft floor so no
 * slope is black. The gradients are ESRI's: `dzdx` rises to the east and `dzdy` to the SOUTH (a
 * row down the grid), so the aspect `atan2(dzdy, −dzdx)` is a mathematical angle, counter-clockwise
 * from east, and the compass azimuth is turned into the same frame, `450° − az`, before the two
 * are compared. A north-west-facing slope then reads brightest and a south-east-facing one darkest.
 */
function hillshade(grid) {
  const png = new PNG({ width: W, height: H, colorType: 0 });
  const az = (((450 - 315) % 360) * Math.PI) / 180;
  const alt = (45 * Math.PI) / 180;
  const z = (x, y) => grid[Math.min(H - 1, Math.max(0, y)) * W + Math.min(W - 1, Math.max(0, x))];
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const dzdx =
        (z(x + 1, y - 1) + 2 * z(x + 1, y) + z(x + 1, y + 1) -
          (z(x - 1, y - 1) + 2 * z(x - 1, y) + z(x - 1, y + 1))) /
        (8 * METRES_PER_PX);
      const dzdy =
        (z(x - 1, y + 1) + 2 * z(x, y + 1) + z(x + 1, y + 1) -
          (z(x - 1, y - 1) + 2 * z(x, y - 1) + z(x + 1, y - 1))) /
        (8 * METRES_PER_PX);
      const slope = Math.atan(Math.hypot(dzdx, dzdy));
      const aspect = Math.atan2(dzdy, -dzdx);
      const lit =
        Math.cos(Math.PI / 2 - alt) * Math.cos(slope) +
        Math.sin(Math.PI / 2 - alt) * Math.sin(slope) * Math.cos(az - aspect);
      // pngjs holds RGBA whatever colour type it writes, so the grey goes to all three channels.
      const o = (y * W + x) * 4;
      const grey = Math.round(255 * Math.max(0, Math.min(1, 0.12 + 0.88 * Math.max(0, lit))));
      png.data[o] = grey;
      png.data[o + 1] = grey;
      png.data[o + 2] = grey;
      png.data[o + 3] = 255;
    }
  }
  return png;
}

// --- Contours: marching squares, then chains, then Douglas–Peucker -----------------------------

/**
 * Traces every level in `levels` across `grid`. Each cell edge the level crosses becomes a point,
 * keyed by the edge, so two cells that share an edge share the point exactly and chains join on
 * integer keys rather than on floating-point coordinates. A grid sample stands for its pixel's
 * CENTRE, so every point is written half a pixel on in both axes: the hillshade raster and the
 * labels (`px`, and a summit's `+ 0.5`) are in the same space, where pixel x covers [x, x + 1].
 */
function trace(grid, levels) {
  const lines = [];
  for (const level of levels) {
    const points = new Map();
    const links = new Map();
    const link = (a, b) => {
      (links.get(a) ?? links.set(a, []).get(a)).push(b);
      (links.get(b) ?? links.set(b, []).get(b)).push(a);
    };
    const edgePoint = (id) => {
      if (points.has(id)) return;
      const cell = id >> 1;
      const x = cell % W;
      const y = (cell - x) / W;
      const horizontal = (id & 1) === 0;
      const va = grid[cell];
      const vb = horizontal ? grid[cell + 1] : grid[cell + W];
      const t = (level - va) / (vb - va);
      points.set(id, horizontal ? [x + t + 0.5, y + 0.5] : [x + 0.5, y + t + 0.5]);
    };
    for (let y = 0; y < H - 1; y++) {
      for (let x = 0; x < W - 1; x++) {
        const i = y * W + x;
        const a = grid[i];
        const b = grid[i + 1];
        const c = grid[i + W + 1];
        const d = grid[i + W];
        const index = (a > level ? 8 : 0) | (b > level ? 4 : 0) | (c > level ? 2 : 0) | (d > level ? 1 : 0);
        if (index === 0 || index === 15) continue;
        const top = 2 * i;
        const bottom = 2 * (i + W);
        const left = 2 * i + 1;
        const right = 2 * (i + 1) + 1;
        const segments = [];
        switch (index) {
          case 1: case 14: segments.push([left, bottom]); break;
          case 2: case 13: segments.push([bottom, right]); break;
          case 3: case 12: segments.push([left, right]); break;
          case 4: case 11: segments.push([top, right]); break;
          case 6: case 9: segments.push([top, bottom]); break;
          case 7: case 8: segments.push([left, top]); break;
          case 5: case 10: {
            // A saddle: the cell's centre decides which diagonal the level keeps.
            const centreAbove = (a + b + c + d) / 4 > level;
            if ((index === 5) === centreAbove) segments.push([left, top], [bottom, right]);
            else segments.push([left, bottom], [top, right]);
            break;
          }
        }
        for (const [p, q] of segments) {
          edgePoint(p);
          edgePoint(q);
          link(p, q);
        }
      }
    }
    const seen = new Set();
    const walk = (from, first) => {
      const chain = [from];
      let prev = from;
      let at = first;
      while (at !== undefined && !seen.has(at)) {
        seen.add(at);
        chain.push(at);
        const next = links.get(at).find((n) => n !== prev && !seen.has(n));
        prev = at;
        at = next;
      }
      return chain;
    };
    // Open chains start at an end (an edge with one link); what is left is closed.
    for (const pass of ["open", "closed"]) {
      for (const [id, ns] of links) {
        if (seen.has(id) || (pass === "open" && ns.length !== 1)) continue;
        seen.add(id);
        const chain = walk(id, ns[0]);
        const closed = pass === "closed";
        if (closed) chain.push(chain[0]);
        lines.push({ level, closed, points: chain.map((e) => points.get(e)) });
      }
    }
  }
  return lines;
}

/**
 * Douglas–Peucker. A closed line's ends are the same point, which leaves the first chord no length
 * and every point at distance zero from it, so a ring is split at its point farthest from the start
 * and each half simplified on its own.
 */
function simplify(points, tolerance) {
  if (points.length < 3) return points;
  const [fx, fy] = points[0];
  const [lx, ly] = points[points.length - 1];
  if (fx === lx && fy === ly) {
    let far = 1;
    for (let k = 1; k < points.length - 1; k++) {
      if (Math.hypot(points[k][0] - fx, points[k][1] - fy) > Math.hypot(points[far][0] - fx, points[far][1] - fy)) far = k;
    }
    return [...simplifyOpen(points.slice(0, far + 1), tolerance).slice(0, -1), ...simplifyOpen(points.slice(far), tolerance)];
  }
  return simplifyOpen(points, tolerance);
}

function simplifyOpen(points, tolerance) {
  if (points.length < 3) return points;
  const keep = new Uint8Array(points.length);
  keep[0] = 1;
  keep[points.length - 1] = 1;
  const stack = [[0, points.length - 1]];
  while (stack.length > 0) {
    const [s, e] = stack.pop();
    const [ax, ay] = points[s];
    const [bx, by] = points[e];
    const len = Math.hypot(bx - ax, by - ay) || 1;
    let far = -1;
    let worst = tolerance;
    for (let k = s + 1; k < e; k++) {
      const [px2, py2] = points[k];
      const d = Math.abs((bx - ax) * (ay - py2) - (ax - px2) * (by - ay)) / len;
      if (d > worst) {
        worst = d;
        far = k;
      }
    }
    if (far >= 0) {
      keep[far] = 1;
      stack.push([s, far], [far, e]);
    }
  }
  return points.filter((_, k) => keep[k] === 1);
}

/** Two rounds of Chaikin's corner cutting, which turns a mask's staircase into a shore. */
function chaikin(points, closed) {
  let p = points;
  for (let round = 0; round < 2; round++) {
    const next = closed ? [] : [p[0]];
    for (let k = 0; k < p.length - 1; k++) {
      const [ax, ay] = p[k];
      const [bx, by] = p[k + 1];
      next.push([0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by], [0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by]);
    }
    if (closed) next.push(next[0]);
    else next.push(p[p.length - 1]);
    p = next;
  }
  return p;
}

// --- Output ------------------------------------------------------------------------------------

const QUANT = 4;

/**
 * `relief.bin`, little-endian: the ASCII magic "RLF1", Uint32 line count, then per line an Int16
 * key (a contour's elevation in metres, or −1 − n for the shore of lake n), a Uint8 flag (1 for a
 * closed line), a Uint32 point count, the first point as two Uint16 in quarter pixels, and every
 * further point as two zig-zag varint deltas in quarter pixels.
 */
function writeVectors(lines) {
  const bytes = [];
  const u8 = (v) => bytes.push(v & 0xff);
  const u16 = (v) => { u8(v); u8(v >> 8); };
  const u32 = (v) => { u16(v & 0xffff); u16(v >>> 16); };
  const varint = (v) => {
    let z = v >= 0 ? v * 2 : -v * 2 - 1;
    while (z >= 0x80) {
      u8((z & 0x7f) | 0x80);
      z = Math.floor(z / 128);
    }
    u8(z);
  };
  for (const c of "RLF1") u8(c.charCodeAt(0));
  u32(lines.length);
  let total = 0;
  for (const line of lines) {
    const q = line.points.map(([x, y]) => [Math.round(x * QUANT), Math.round(y * QUANT)]);
    u16(line.key & 0xffff);
    u8(line.closed ? 1 : 0);
    u32(q.length);
    u16(q[0][0]);
    u16(q[0][1]);
    for (let k = 1; k < q.length; k++) {
      varint(q[k][0] - q[k - 1][0]);
      varint(q[k][1] - q[k - 1][1]);
    }
    total += q.length;
  }
  writeFileSync(resolve(out, "relief.bin"), Buffer.from(bytes));
  say(`relief.bin: ${lines.length} lines, ${total} points, ${(bytes.length / 1024).toFixed(0)} KB`);
}

async function main() {
  mkdirSync(out, { recursive: true });
  const raw = await elevation();

  const lakes = LAKES.map((lake) => ({ ...lake, ...floodLake(raw, lake) }));
  // Lakes are drawn flat at their own level, and their surfaces carry no contour noise.
  const smooth = blur(raw, 2);
  const flat = new Float32Array(smooth);
  for (const lake of lakes) {
    for (let i = 0; i < W * H; i++) if (lake.mask[i] === 1) flat[i] = lake.level;
  }

  const shade = hillshade(blur(raw, 0.8));
  const pngPath = resolve(repo, "tmp/terminal-relief/relief.png");
  writeFileSync(pngPath, PNG.sync.write(shade, { colorType: 0 }));
  const webp = spawnSync("cwebp", ["-quiet", "-q", "82", "-m", "6", pngPath, "-o", resolve(out, "relief.webp")]);
  if (webp.status !== 0) throw new Error(`cwebp failed: ${webp.stderr}`);

  // The contour levels span the smoothed field they are traced on; the range the page reports
  // is the data's own, read off the raw grid, which the blur would pull in at both ends.
  const range = (grid) => {
    let low = Infinity;
    let high = -Infinity;
    for (const v of grid) {
      low = Math.min(low, v);
      high = Math.max(high, v);
    }
    return [low, high];
  };
  const [lo, hi] = range(flat);
  const [rawLo, rawHi] = range(raw);
  const levels = [];
  for (let l = Math.ceil(lo / CONTOUR_INTERVAL) * CONTOUR_INTERVAL; l <= hi; l += CONTOUR_INTERVAL) {
    levels.push(l);
  }
  const minSpan = 6;
  const contours = trace(flat, levels)
    .map((line) => ({ key: line.level, closed: line.closed, points: simplify(line.points, 0.35) }))
    .filter((line) => {
      const xs = line.points.map((p) => p[0]);
      const ys = line.points.map((p) => p[1]);
      return Math.max(...xs) - Math.min(...xs) + Math.max(...ys) - Math.min(...ys) >= minSpan;
    });

  const shores = [];
  lakes.forEach((lake, n) => {
    const field = new Float32Array(W * H);
    for (let i = 0; i < W * H; i++) field[i] = lake.mask[i];
    for (const line of trace(field, [0.5])) {
      if (line.points.length < 12) continue;
      shores.push({ key: -1 - n, closed: line.closed, points: simplify(chaikin(line.points, line.closed), 0.2) });
    }
  });
  say(`shores: ${shores.length}`);
  writeVectors([...shores, ...contours]);

  const border = [
    px(BOUNDS.north, -120),
    px(39, -120),
    // The oblique line runs from 39° N 120° W toward the Colorado at 35° N 114.63° W.
    (() => {
      const t = (39 - BOUNDS.south) / (39 - 35);
      return px(39 - t * 4, -120 + t * (120 - 114.6333));
    })(),
  ];

  const meta = {
    source: "Terrain Tiles on AWS (terrarium, zoom 12): USGS 3D Elevation Program",
    attribution: ATTRIBUTION,
    width: W,
    height: H,
    metresPerPixel: Number(METRES_PER_PX.toFixed(3)),
    bounds: BOUNDS,
    contourInterval: CONTOUR_INTERVAL,
    indexEvery: INDEX_EVERY,
    elevationRange: [Math.round(rawLo), Math.round(rawHi)],
    lakes: lakes.map((lake) => {
      const p = px(lake.lat, lake.lon);
      return { name: lake.name, x: p.x, y: p.y, level: Math.round(lake.level), areaKm2: Number(lake.km2.toFixed(1)) };
    }),
    summits: SUMMITS.map((s) => findSummit(raw, s)),
    towns: TOWNS.map((t) => ({ name: t.name, ...px(t.lat, t.lon) })),
    features: FEATURES.map((f) => ({ name: f.name, ...px(f.lat, f.lon) })),
    border,
  };
  writeFileSync(resolve(out, "relief.json"), `${JSON.stringify(meta, null, 2)}\n`);
  say(`relief.json: ${meta.elevationRange.join("–")} m`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
