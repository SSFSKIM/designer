/**
 * `probe-score` — the W9 probe's hypothesis scoring, exactly as claims §5.30
 * declared it before the first capture.
 *
 *   pnpm --filter @vitrea/calibration exec tsx scripts/probe-score.ts \
 *     --scenes ../../apps/reference-apple/scenes-w9-probe.json \
 *     --snapshots '/path/w9snap-probe-*' --out /path/probe-scores.json
 *
 * What it computes, and what it deliberately does not:
 *
 * - Interior level `L` per cell per run: `interiorLevel` over the NATIVE
 *   silhouette bounded to the declared region — the coherence metric's own
 *   interior definition, nothing re-derived.
 * - The empirical response curve `R_c(l)`: monotone (Fritsch–Carlson) PCHIP
 *   through the three solid anchors measured in the same runs, per anchored
 *   component; log-area interpolation between anchored curves for the two
 *   unanchored components. NO vitrea constant participates in any score.
 * - Predictions P0 (current model), P1 (map-then-average), P3 (encoded-space
 *   averaging) from backdrop statistics measured UNDER THE INTERIOR MASK of
 *   the rendered background raster — levels and weights, never assumed.
 *   P2 (band-limited) mixes P0→P1 by smoothstep(pitch/(k·span)), k
 *   grid-searched on CALIBRATION cells only over the declared grid.
 * - Scores: RMS(P − L) over structured, non-`recorded` rest cells, overall
 *   and per pitch. H4's statistic: the best luminance-only model's residual
 *   on the equal-mean pair against 3× the pooled run σ of those cells.
 * - Attestation is asserted per fixture read (`presentedActive`); a cell
 *   with any unattested run is reported, not silently averaged.
 *
 * It fits nothing to the reference beyond P2's single declared parameter,
 * writes one JSON, and prints the tables a findings section quotes.
 */

import { createHash } from "node:crypto";
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { basename, dirname, join } from "node:path";

import {
  componentRegion,
  decodePng,
  extractSilhouette,
  interiorLevel,
  linearLuminance,
  type CalibrationImage,
  type Silhouette,
} from "../src/index";
import { DEFAULT_SILHOUETTE_THRESHOLD } from "../cli/measure";

const PROFILE = "apple-macos-26.5-1x-light-standard";
const K_GRID = [0.005, 0.01, 0.02, 0.04, 0.08, 0.16, 0.32];
const SOLID_ANCHORS = ["dark-solid", "mid-dark-solid", "light-solid"];
/** Structured backgrounds carry the pitch their kind declares; solids and photo do not. */
const PITCH: Record<string, number> = {
  "checkerboard-4": 4,
  "checkerboard-8": 8,
  checkerboard: 16,
  "checkerboard-32": 32,
  "checkerboard-64": 64,
  "checkerboard-lc16": 16,
  "hc-text-7": 7,
  "hc-text": 14,
  "hc-text-28": 28,
};

interface SceneRow {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
  readonly tint?: string;
}

function flag(name: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

function srgbEncode(linear: number): number {
  const c = Math.min(1, Math.max(0, linear));
  return c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
}
function srgbDecode(encoded: number): number {
  const c = Math.min(1, Math.max(0, encoded));
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}
function smoothstep(t: number): number {
  const x = Math.min(1, Math.max(0, t));
  return x * x * (3 - 2 * x);
}

/** Monotone cubic (Fritsch–Carlson) through sorted (x, y) points. */
function pchip(xs: readonly number[], ys: readonly number[]): (x: number) => number {
  const n = xs.length;
  const h = xs.slice(1).map((x, i) => x - (xs[i] ?? 0));
  const delta = h.map((hi, i) => ((ys[i + 1] ?? 0) - (ys[i] ?? 0)) / hi);
  const m: number[] = new Array(n).fill(0);
  m[0] = delta[0] ?? 0;
  m[n - 1] = delta[n - 2] ?? 0;
  for (let i = 1; i < n - 1; i += 1) {
    const a = delta[i - 1] ?? 0;
    const b = delta[i] ?? 0;
    m[i] = a * b <= 0 ? 0 : (2 * a * b) / (a + b);
  }
  return (x: number) => {
    const clamped = Math.min(xs[n - 1] ?? 1, Math.max(xs[0] ?? 0, x));
    let i = 0;
    while (i < n - 2 && clamped > (xs[i + 1] ?? 0)) i += 1;
    const hi = h[i] ?? 1;
    const t = (clamped - (xs[i] ?? 0)) / hi;
    const y0 = ys[i] ?? 0;
    const y1 = ys[i + 1] ?? 0;
    const m0 = m[i] ?? 0;
    const m1 = m[i + 1] ?? 0;
    return (
      y0 * (1 + 2 * t) * (1 - t) * (1 - t) +
      m0 * hi * t * (1 - t) * (1 - t) +
      y1 * t * t * (3 - 2 * t) +
      m1 * hi * t * t * (t - 1)
    );
  };
}

function rms(values: readonly number[]): number {
  return Math.sqrt(values.reduce((s, v) => s + v * v, 0) / values.length);
}

const scenesPath = flag("scenes") ?? "../../apps/reference-apple/scenes-w9-probe.json";
const snapshotsGlob = flag("snapshots") ?? "/Users/new/.claude/jobs/5c70e47f/tmp/w9snap-probe-*";
const outPath = flag("out") ?? "/Users/new/.claude/jobs/5c70e47f/tmp/probe-scores.json";

const spec = JSON.parse(readFileSync(scenesPath, "utf8")) as {
  canvas: { width: number; height: number };
  components: Record<string, unknown>;
  scenes: readonly SceneRow[];
  split: Record<string, readonly string[]>;
};
const recorded = new Set(spec.split["recorded"] ?? []);
const calibration = new Set(spec.split["calibration"] ?? []);

const snapDirParent = dirname(snapshotsGlob);
const snapPrefix = basename(snapshotsGlob).replace(/\*$/, "");
const snapshots = readdirSync(snapDirParent)
  .filter((d) => d.startsWith(snapPrefix))
  .sort()
  .map((d) => join(snapDirParent, d));
if (snapshots.length === 0) throw new Error(`no snapshots under ${snapshotsGlob}`);

// Background rasters live beside the campaign fixtures; any snapshot's parent
// tree does not carry them, so read them from the fixtures dir the chain used.
const backgroundsDir = flag("backgrounds") ?? join(snapDirParent, "w9-probe-fixtures", "backgrounds");
const backgroundCache = new Map<string, CalibrationImage>();
function backgroundOf(name: string): CalibrationImage {
  let image = backgroundCache.get(name);
  if (!image) {
    image = decodePng(readFileSync(join(backgroundsDir, `${name}@1x.png`)));
    backgroundCache.set(name, image);
  }
  return image;
}

interface CellRun {
  readonly run: string;
  readonly level: number;
  readonly attested: boolean;
  readonly bytes: string;
}
interface CellAggregate {
  readonly scene: SceneRow;
  readonly runs: CellRun[];
  mean: number;
  sigma: number;
  states?: ReadonlyArray<{ share: number; level: number }>;
  unattestedRuns: string[];
  /** Backdrop under this cell's interior mask: linear levels + weights. */
  bgMeanLinear: number;
  bgMeanEncoded: number;
  bgLevels: ReadonlyArray<{ level: number; weight: number }>;
}

const cells = new Map<string, CellAggregate>();
const silhouetteCache = new Map<string, Silhouette>();

for (const snap of snapshots) {
  const run = basename(snap);
  const manifest = JSON.parse(readFileSync(join(snap, "manifest.json"), "utf8")) as {
    profiles: ReadonlyArray<{
      profileKey: string;
      fixtures: ReadonlyArray<{ file: string; presentedActive?: boolean }>;
    }>;
  };
  const profile = manifest.profiles.find((p) => p.profileKey === PROFILE);
  if (!profile) throw new Error(`${run}: profile ${PROFILE} missing from manifest`);
  const attested = new Map(profile.fixtures.map((f) => [basename(f.file, ".png"), f.presentedActive === true]));

  for (const scene of spec.scenes) {
    const png = join(snap, PROFILE, `${scene.id}.png`);
    let native: CalibrationImage;
    let buffer: Buffer;
    try {
      buffer = readFileSync(png);
      native = decodePng(buffer);
    } catch {
      continue;
    }
    const bytes = createHash("sha256").update(buffer).digest("hex").slice(0, 10);
    const background = backgroundOf(scene.background);
    const region = componentRegion(spec.components[scene.component] as never, {
      canvas: spec.canvas,
      scale: 1,
      width: native.width,
      height: native.height,
    });
    const sil = extractSilhouette(native, {
      kind: "luminance-delta",
      background,
      threshold: DEFAULT_SILHOUETTE_THRESHOLD,
      region: region.silhouette,
    });
    const level = interiorLevel(native, { interior: sil }).mean;

    let cell = cells.get(scene.id);
    if (!cell) {
      // Backdrop statistics under the mask, from the FIRST run's silhouette —
      // silhouettes are byte-stable across settled runs, and one mask keeps the
      // backdrop statistic identical across runs of the same cell.
      silhouetteCache.set(scene.id, sil);
      const bgLum = linearLuminance(background);
      const histogram = new Map<number, number>();
      let sumLinear = 0;
      let sumEncoded = 0;
      let count = 0;
      for (let i = 0; i < bgLum.length; i += 1) {
        if ((sil.mask[i] ?? 0) === 0) continue;
        const l = bgLum[i] ?? 0;
        const key = Math.round(l * 1e4) / 1e4;
        histogram.set(key, (histogram.get(key) ?? 0) + 1);
        sumLinear += l;
        sumEncoded += srgbEncode(l);
        count += 1;
      }
      cell = {
        scene,
        runs: [],
        mean: 0,
        sigma: 0,
        unattestedRuns: [],
        bgMeanLinear: sumLinear / count,
        bgMeanEncoded: sumEncoded / count,
        bgLevels: [...histogram.entries()]
          .map(([l, n]) => ({ level: l, weight: n / count }))
          .sort((a, b) => b.weight - a.weight)
          .slice(0, 64),
      };
      cells.set(scene.id, cell);
    }
    const isAttested = attested.get(scene.id) === true;
    cell.runs.push({ run, level, attested: isAttested, bytes });
    if (!isAttested) cell.unattestedRuns.push(run);
  }
}

/*
 * Frequency-settled aggregation, the doctrine's own move (DL21): a two-state
 * cell takes its MAJORITY state's value with the observed shares recorded, and
 * a tie refuses rather than votes. A mean across states would manufacture a
 * level the reference never rendered — the dark-solid rrect-sm anchor's one
 * light-state run would drag 0.035 to 0.177 and corrupt every small-component
 * prediction downstream. σ is still reported across ALL attested runs (state
 * flips included), because that is the run-to-run noise the declared H4 bar
 * reads — conservative exactly where bimodality is present.
 */
for (const cell of cells.values()) {
  const used = cell.runs.filter((r) => r.attested);
  const pool = used.length > 0 ? used : cell.runs;
  const byState = new Map<string, CellRun[]>();
  for (const run of pool) {
    const group = byState.get(run.bytes) ?? [];
    group.push(run);
    byState.set(run.bytes, group);
  }
  const groups = [...byState.values()].sort((a, b) => b.length - a.length);
  const top = groups[0] ?? pool;
  if (groups.length > 1 && groups[1]?.length === top.length) {
    throw new Error(`${cell.scene.id}: state TIE at ${top.length}:${top.length} — refused, top up before scoring`);
  }
  cell.mean = top[0]?.level ?? 0;
  const all = pool.map((r) => r.level);
  const meanAll = all.reduce((s, v) => s + v, 0) / all.length;
  cell.sigma = Math.sqrt(all.reduce((s, v) => s + (v - meanAll) ** 2, 0) / all.length);
  cell.states = groups.map((g) => ({ share: g.length / pool.length, level: g[0]?.level ?? 0 }));
}

// ---- The empirical response curves ------------------------------------------

const AREAS: Record<string, number> = {
  "rrect-sm": 64 * 32,
  "capsule-button": 120 * 44,
  "rrect-md": 160 * 96,
  "rrect-ml": 224 * 128,
  "rrect-lg": 280 * 160,
};
const SPANS: Record<string, number> = {
  "rrect-sm": 32,
  "capsule-button": 44,
  "rrect-md": 96,
  "rrect-ml": 128,
  "rrect-lg": 160,
};
const ANCHORED = ["rrect-sm", "rrect-md", "rrect-lg"];

const anchorCurves = new Map<string, (l: number) => number>();
for (const component of ANCHORED) {
  const points = SOLID_ANCHORS.map((bg) => {
    const cell = cells.get(`${bg}__${component}__rest`);
    if (!cell) throw new Error(`anchor cell ${bg}__${component}__rest missing`);
    return { x: cell.bgMeanLinear, y: cell.mean };
  }).sort((a, b) => a.x - b.x);
  anchorCurves.set(
    component,
    pchip(points.map((p) => p.x), points.map((p) => p.y)),
  );
}
function responseCurve(component: string): (l: number) => number {
  const anchored = anchorCurves.get(component);
  if (anchored) return anchored;
  const area = Math.log(AREAS[component] ?? 1);
  const below = ANCHORED.filter((c) => (AREAS[c] ?? 0) <= (AREAS[component] ?? 0)).pop() ?? "rrect-sm";
  const above = ANCHORED.find((c) => (AREAS[c] ?? 0) > (AREAS[component] ?? 0)) ?? "rrect-lg";
  const t =
    (area - Math.log(AREAS[below] ?? 1)) / (Math.log(AREAS[above] ?? 2) - Math.log(AREAS[below] ?? 1));
  const lo = anchorCurves.get(below);
  const hi = anchorCurves.get(above);
  if (!lo || !hi) throw new Error(`no anchors bracket ${component}`);
  return (l: number) => lo(l) * (1 - t) + hi(l) * t;
}

// ---- Predictions ------------------------------------------------------------

interface Scored {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly set: string;
  readonly measured: number;
  readonly sigma: number;
  readonly p0: number;
  readonly p1: number;
  readonly p3: number;
  p2?: number;
}

const structured = [...cells.values()].filter(
  (c) => PITCH[c.scene.background] !== undefined && c.scene.tint === undefined,
);
const scoredRows: Scored[] = structured.map((cell) => {
  const R = responseCurve(cell.scene.component);
  const p1 = cell.bgLevels.reduce((s, { level, weight }) => s + R(level) * weight, 0);
  const setOf = recorded.has(cell.scene.id)
    ? "recorded"
    : calibration.has(cell.scene.id)
      ? "calibration"
      : (spec.split["validation"] ?? []).includes(cell.scene.id)
        ? "validation"
        : "holdout";
  return {
    id: cell.scene.id,
    background: cell.scene.background,
    component: cell.scene.component,
    set: setOf,
    measured: cell.mean,
    sigma: cell.sigma,
    p0: R(cell.bgMeanLinear),
    p1,
    p3: R(srgbDecode(cell.bgMeanEncoded)),
  };
});

// P2: one parameter, calibration cells only, declared grid.
let bestK = K_GRID[0] ?? 0.02;
let bestRms = Number.POSITIVE_INFINITY;
for (const k of K_GRID) {
  const residuals = scoredRows
    .filter((row) => row.set === "calibration")
    .map((row) => {
      const g = smoothstep((PITCH[row.background] ?? 0) / (k * (SPANS[row.component] ?? 1)));
      return row.p0 + g * (row.p1 - row.p0) - row.measured;
    });
  const value = rms(residuals);
  if (value < bestRms) {
    bestRms = value;
    bestK = k;
  }
}
for (const row of scoredRows) {
  const g = smoothstep((PITCH[row.background] ?? 0) / (bestK * (SPANS[row.component] ?? 1)));
  row.p2 = row.p0 + g * (row.p1 - row.p0);
}

// ---- Scores and verdict inputs ----------------------------------------------

const scoringSet = scoredRows.filter((row) => row.set !== "recorded");
const hypotheses = {
  "P0 current-model": scoringSet.map((r) => r.p0 - r.measured),
  "P1 map-then-average": scoringSet.map((r) => r.p1 - r.measured),
  "P2 band-limited": scoringSet.map((r) => (r.p2 ?? r.p0) - r.measured),
  "P3 encoded-mean": scoringSet.map((r) => r.p3 - r.measured),
};
const overall = Object.fromEntries(
  Object.entries(hypotheses).map(([name, residuals]) => [name, rms(residuals)]),
);

// H4: the equal-mean pair, per component, against 3× pooled run σ.
const h4 = ["rrect-sm", "capsule-button", "rrect-md", "rrect-ml", "rrect-lg"].map((component) => {
  const full = cells.get(`checkerboard__${component}__rest`);
  const lc = cells.get(`checkerboard-lc16__${component}__rest`);
  if (!full || !lc) return { component, note: "pair incomplete" };
  const sigmaPooled = Math.sqrt((full.sigma ** 2 + lc.sigma ** 2) / 2);
  return {
    component,
    fullContrast: full.mean,
    lowContrast: lc.mean,
    measuredGap: full.mean - lc.mean,
    sigmaPooled,
  };
});

const unattested = [...cells.values()]
  .filter((c) => c.unattestedRuns.length > 0)
  .map((c) => ({ id: c.scene.id, runs: c.unattestedRuns }));

const multiState = [...cells.values()]
  .filter((c) => (c.states?.length ?? 0) > 1)
  .map((c) => ({ id: c.scene.id, states: c.states }));

const output = {
  declaredIn: "claims 5.30",
  snapshots: snapshots.map((s) => basename(s)),
  silhouetteThreshold: DEFAULT_SILHOUETTE_THRESHOLD,
  bandLimitedK: bestK,
  overallRms: overall,
  rows: scoredRows.sort((a, b) => a.id.localeCompare(b.id)),
  equalMeanPair: h4,
  multiState,
  unattested,
};
writeFileSync(outPath, JSON.stringify(output, null, 2));

console.log(`runs: ${snapshots.length}, cells: ${cells.size}, scored (non-recorded structured): ${scoringSet.length}`);
console.log(`\nRMS per hypothesis (P2 at k=${bestK}):`);
for (const [name, value] of Object.entries(overall)) console.log(`  ${name}: ${value.toFixed(4)}`);
console.log("\npitch × component (measured | P0 | P1):");
for (const row of scoredRows.filter((r) => r.background.startsWith("checkerboard"))) {
  console.log(
    `  ${row.id.padEnd(44)} ${row.measured.toFixed(4)} | ${row.p0.toFixed(4)} | ${row.p1.toFixed(4)} (${row.set})`,
  );
}
console.log("\nequal-mean pair (full | lc | gap | 3σ):");
for (const pair of h4) {
  if ("note" in pair) {
    console.log(`  ${pair.component}: ${pair.note ?? ""}`);
  } else {
    console.log(
      `  ${pair.component.padEnd(16)} ${pair.fullContrast?.toFixed(4)} | ${pair.lowContrast?.toFixed(4)} | ${pair.measuredGap?.toFixed(4)} | ${(3 * (pair.sigmaPooled ?? 0)).toFixed(4)}`,
    );
  }
}
if (multiState.length > 0) {
  console.log(`\nmulti-state cells (majority level used, shares recorded): ${multiState.length}`);
  for (const m of multiState) {
    const shares = (m.states ?? []).map((s) => `${(s.share * 100).toFixed(0)}%@${s.level.toFixed(4)}`).join(" vs ");
    console.log(`  ${m.id}: ${shares}`);
  }
}
if (unattested.length > 0) {
  console.log(`\nUNATTESTED cells (excluded from means): ${unattested.length}`);
  for (const u of unattested) console.log(`  ${u.id}: ${u.runs.join(", ")}`);
}
console.log(`\n→ ${outPath}`);
