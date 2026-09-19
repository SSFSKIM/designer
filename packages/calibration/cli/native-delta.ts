/**
 * `native-delta` — one bed of Apple's own material against another.
 *
 *   npx tsx cli/native-delta.ts verify-readers
 *   npx tsx cli/native-delta.ts bar    --runs ~/vitrea-w29-27-run --out <dir>/noise-bar.json
 *   npx tsx cli/native-delta.ts delta  --bar <dir>/noise-bar.json --out <dir>
 *   npx tsx cli/native-delta.ts tables --dir <dir>
 *   npx tsx cli/native-delta.ts sheets --dir <dir> [--gain 8] [--per-profile 4]
 *
 * ## Why this is a different measurement from `compare` and from `tier-delta`
 *
 * Every number in `results/matrix.json` is web against native: `ResultCellKey`
 * requires a `WebCell`, so the result matrix cannot hold a native-against-native
 * row and this instrument's rows live beside it, never in it. `tier-delta` is
 * the precedent — a pair diff with no fixture in it — and this is its mirror: a
 * pair diff with **nothing but** fixtures in it, and no web capture anywhere.
 *
 * The question is what Apple changed between two operating systems. Two beds of
 * the same scene declaration, captured on one machine over byte-identical
 * backdrops (W29 G1 Part B §6), are the only way to ask it, and the answer is
 * only a measurement if it is stated against a bar. That bar is the 27 bed's own
 * run-to-run behaviour, taken from the sitting's seven raw runs per pass, and it
 * is declared per cell and per metric **before** any 26.5 pair is read (W29
 * acceptance clause 3; Decision Log 1 (ii)). `bar` writes it; `delta` consumes
 * it and refuses to run without it.
 *
 * ## What the bar can and cannot say
 *
 * It is a 27-against-27 bar. The 26.5 bed's own run-to-run variation is **not**
 * in it and cannot be: the 26.5 plurality record is byte-level and transient,
 * it carries no SSIM, ΔE or contour distribution, and 38 % of that bed can be
 * attributed no capture bar at all (§5.149 §6). So a verdict of "moved" is
 * "moved beyond what the 27 bed does against itself", and the bar understates
 * the combined spread of a cross-bed pair by whatever the 26.5 side's own
 * spread was. That is a floor on the claim, not a ceiling, and it is stated on
 * every reading rather than buried here.
 */

import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { PNG } from "pngjs";

import {
  createImage,
  decodePng,
  interiorLevel,
  parseProfileKey,
  tintResponse,
  type CalibrationImage,
} from "../src/index";
import {
  activeTwinOf,
  cellGeometry,
  counterpartKey,
  pairMetrics,
  poseOf,
  readCapture,
  NATIVE_DELTA_METRICS,
  type CaptureReading,
  type CellGeometry,
  type MetricVector,
  type NativeDeltaMetric,
  type PairReadings,
} from "./native-delta-metrics";
import {
  angularRead,
  contourRimRead,
  declaredBox,
  rasterOf,
  RIM_SIDES,
} from "./native-delta-readers";
import { declaredComponentOf, componentRegionFor, readSceneGeometry } from "./scene-geometry";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const REFERENCE = resolve(REPO_ROOT, "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const say = (line: string): void => void process.stdout.write(`${line}\n`);

// ---------------------------------------------------------------------------
// The manifest, the beds and the pairing
// ---------------------------------------------------------------------------

interface FixtureEntry {
  readonly sceneId: string;
  readonly file: string;
  readonly fixtureSet: string;
}

interface ProfileEntry {
  readonly profileKey: string;
  readonly colorScheme: "light" | "dark";
  readonly a11yMode: string;
  readonly fixtures: readonly FixtureEntry[];
}

interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly ProfileEntry[];
}

function readJson<T>(path: string): T {
  if (!existsSync(path)) throw new Error(`native-delta: ${path} does not exist`);
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

const load = (path: string): CalibrationImage => decodePng(readFileSync(path));

function backgroundOf(
  manifest: Manifest,
  scenes: readonly { readonly id: string; readonly background: string }[],
  sceneId: string,
  scale: number,
): string | null {
  const scene = scenes.find((entry) => entry.id === sceneId);
  if (scene === undefined) return null;
  return (
    manifest.backgrounds[`${scene.background}@${String(scale)}x`] ??
    manifest.backgrounds[scene.background] ??
    null
  );
}

interface CellContext {
  readonly geometry: CellGeometry;
  readonly background: CalibrationImage;
  readonly backgroundId: string;
  readonly scale: number;
}

function contextFor(
  sceneId: string,
  profileKey: string,
  manifest: Manifest,
  spec: { readonly scenes: readonly { readonly id: string; readonly background: string }[] },
  geometryMatrix: ReturnType<typeof readSceneGeometry>,
  width: number,
  height: number,
  backgroundCache: Map<string, CalibrationImage>,
): CellContext | null {
  const scale = parseProfileKey(profileKey)?.scale;
  if (scale === undefined) return null;
  const backgroundFile = backgroundOf(manifest, spec.scenes, sceneId, scale);
  if (backgroundFile === null) return null;
  let background = backgroundCache.get(backgroundFile);
  if (background === undefined) {
    background = load(resolve(FIXTURES, backgroundFile));
    backgroundCache.set(backgroundFile, background);
  }
  const region = componentRegionFor(geometryMatrix, sceneId, { scale, width, height });
  const component = declaredComponentOf(geometryMatrix, sceneId);
  return {
    geometry: cellGeometry(region, component, geometryMatrix.canvas, scale),
    background,
    backgroundId: backgroundFile,
    scale,
  };
}

// ---------------------------------------------------------------------------
// The per-capture signed readings the recede is a difference of
// ---------------------------------------------------------------------------

/**
 * The scalars a single capture carries on its own, with no partner.
 *
 * The recede is a difference of differences — `(27 inactive − 27 active)`
 * against `(26.5 inactive − 26.5 active)` — so it cannot be built out of pair
 * distances, which have thrown their sign away. These are the signed readings
 * it is built from, and they are led by the four that need **no silhouette at
 * all** (`bodyLevel`, the two contour rims, the highlight's peak and floor):
 * between an active and a receded capture the extracted silhouettes genuinely
 * differ, and a mask-free reading is the one a difference of differences cannot
 * be accused of having changed underneath it.
 */
export const CAPTURE_READINGS = [
  "bodyLevel",
  "rimContourMean",
  "rimLocalMean",
  "highlightPeak",
  "highlightFloor",
  "highlightRatio",
  "interiorMean",
  "interiorStdDev",
  "rimPeak",
  "rimPeakDepthPx",
  "tintDeltaL",
  "tintChroma",
  "silhouetteAreaPx",
] as const;
type CaptureReadingName = (typeof CAPTURE_READINGS)[number];
type CaptureReadingVector = Readonly<Record<CaptureReadingName, number | null>>;

function captureReadings(
  image: CalibrationImage,
  reading: CaptureReading,
  context: CellContext,
): CaptureReadingVector {
  const out: Record<CaptureReadingName, number | null> = Object.fromEntries(
    CAPTURE_READINGS.map((name) => [name, null]),
  ) as Record<CaptureReadingName, number | null>;

  if (context.geometry.box !== null) {
    const raster = rasterOf(image);
    const contour = contourRimRead(raster, context.geometry.box, context.geometry.scale);
    out.bodyLevel = contour.body;
    let rimSum = 0;
    let localSum = 0;
    let count = 0;
    for (const side of RIM_SIDES) {
      const rim = contour.sides[side].rim;
      if (!Number.isFinite(rim)) continue;
      rimSum += rim;
      localSum += contour.sides[side].rimLocal;
      count += 1;
    }
    if (count > 0) {
      out.rimContourMean = rimSum / count;
      out.rimLocalMean = localSum / count;
    }
    const angular = angularRead(raster, context.geometry.box, context.geometry.scale);
    out.highlightPeak = angular.peakBin;
    out.highlightFloor = angular.floorBin;
    out.highlightRatio = Number.isFinite(angular.ratio) ? angular.ratio : null;
  }

  out.silhouetteAreaPx = reading.area;
  if (reading.area > 0) {
    const level = interiorLevel(image, { interior: reading.silhouette });
    out.interiorMean = level.mean;
    out.interiorStdDev = level.stdDev;
    const tint = tintResponse(image, context.background, { interior: reading.silhouette });
    out.tintDeltaL = tint.deltaL;
    out.tintChroma = tint.interiorChroma;
  }
  if (reading.rim !== null) {
    out.rimPeak = reading.rim.peakLuminance;
    out.rimPeakDepthPx = reading.rim.peakDistancePx;
  }
  return out;
}

// ---------------------------------------------------------------------------
// The noise bar
// ---------------------------------------------------------------------------

interface Distribution {
  readonly n: number;
  readonly min: number;
  readonly median: number;
  readonly p95: number;
  readonly max: number;
}

function distributionOf(values: readonly number[]): Distribution | null {
  const finite = values.filter((value) => Number.isFinite(value)).sort((x, y) => x - y);
  if (finite.length === 0) return null;
  const at = (q: number): number => finite[Math.min(finite.length - 1, Math.floor(q * finite.length))] ?? 0;
  return {
    n: finite.length,
    min: finite[0] ?? 0,
    median: at(0.5),
    p95: at(0.95),
    max: finite[finite.length - 1] ?? 0,
  };
}

interface BarCell {
  readonly profileKey: string;
  readonly sceneId: string;
  readonly pose: "active" | "inactive";
  readonly runs: number;
  /** The 21 unordered run pairs, per metric. This is the declared construction. */
  readonly pairwise: Readonly<Partial<Record<NativeDeltaMetric, Distribution>>>;
  /** The 7 runs against the published fixture, per metric. Corroboration only. */
  readonly runVsPublished: Readonly<Partial<Record<NativeDeltaMetric, Distribution>>>;
  /** Max − min over the runs, per signed capture reading: the recede's bar input. */
  readonly readingSpread: Readonly<Partial<Record<CaptureReadingName, number>>>;
}

interface BarFile {
  readonly generatedAt: string;
  readonly construction: string;
  readonly rule: string;
  readonly runsRoot: string;
  readonly metrics: readonly NativeDeltaMetric[];
  readonly captureReadings: readonly CaptureReadingName[];
  /** Per metric, the smallest non-zero pairwise max anywhere in the bed. */
  readonly bedMinimumNonZeroBar: Readonly<Partial<Record<NativeDeltaMetric, number>>>;
  readonly cells: readonly BarCell[];
}

const PASS_DIRECTORIES = [
  "standard-active-1x",
  "standard-inactive-1x",
  "standard-active-2x",
  "standard-inactive-2x",
  "increased-contrast-active-1x",
  "increased-contrast-inactive-1x",
  "reduced-transparency-active-1x",
  "reduced-transparency-inactive-1x",
] as const;

function buildBar(runsRoot: string, outPath: string): void {
  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  const spec = readJson<{ readonly scenes: readonly { readonly id: string; readonly background: string }[] }>(
    resolve(REFERENCE, "scenes.json"),
  );
  const geometryMatrix = readSceneGeometry(REFERENCE);
  const backgroundCache = new Map<string, CalibrationImage>();
  const published = new Map<string, string>();
  for (const profile of manifest.profiles) {
    for (const fixture of profile.fixtures) {
      published.set(`${profile.profileKey} ${fixture.sceneId}`, fixture.file);
    }
  }

  // Gather the raw runs: pass -> run -> profileKey -> sceneId.
  const runsOf = new Map<string, string[]>();
  for (const pass of PASS_DIRECTORIES) {
    const passDir = resolve(runsRoot, pass);
    if (!existsSync(passDir)) throw new Error(`native-delta bar: ${passDir} does not exist`);
    const runDirs = readdirSync(passDir)
      .filter((name) => /^run-\d+$/.test(name))
      .sort((x, y) => Number(x.slice(4)) - Number(y.slice(4)));
    for (const run of runDirs) {
      const runDir = resolve(passDir, run);
      for (const profileKey of readdirSync(runDir)) {
        if (!profileKey.startsWith("apple-macos-27.0-")) continue;
        const profileDir = resolve(runDir, profileKey);
        for (const file of readdirSync(profileDir)) {
          if (!file.endsWith(".png")) continue;
          const sceneId = file.slice(0, -4);
          const key = `${profileKey} ${sceneId}`;
          const list = runsOf.get(key) ?? [];
          list.push(resolve(profileDir, file));
          runsOf.set(key, list);
        }
      }
    }
  }
  say(`native-delta bar: ${String(runsOf.size)} cells with raw runs under ${runsRoot}`);

  const cells: BarCell[] = [];
  const bedNonZero = new Map<NativeDeltaMetric, number>();
  let done = 0;
  for (const [key, paths] of [...runsOf.entries()].sort()) {
    const [profileKey = "", sceneId = ""] = key.split(" ");
    const first = load(paths[0] ?? "");
    const context = contextFor(
      sceneId,
      profileKey,
      manifest,
      spec,
      geometryMatrix,
      first.width,
      first.height,
      backgroundCache,
    );
    if (context === null) {
      throw new Error(`native-delta bar: no backdrop or scale on record for ${profileKey} / ${sceneId}`);
    }

    const images = paths.map((path, index) => (index === 0 ? first : load(path)));
    const readings = images.map((image) => readCapture(image, context.background, context.geometry));
    const scalars = images.map((image, index) =>
      captureReadings(image, readings[index] as CaptureReading, context),
    );

    const pairValues = new Map<NativeDeltaMetric, number[]>();
    for (const metric of NATIVE_DELTA_METRICS) pairValues.set(metric, []);
    for (let i = 0; i < images.length; i += 1) {
      for (let j = i + 1; j < images.length; j += 1) {
        const result = pairMetrics(
          readings[i] as CaptureReading,
          readings[j] as CaptureReading,
          context.background,
          context.geometry,
        );
        for (const metric of NATIVE_DELTA_METRICS) {
          const value = result.metrics[metric];
          if (value !== null && Number.isFinite(value)) pairValues.get(metric)?.push(value);
        }
      }
    }

    const publishedFile = published.get(key);
    const againstPublished = new Map<NativeDeltaMetric, number[]>();
    for (const metric of NATIVE_DELTA_METRICS) againstPublished.set(metric, []);
    if (publishedFile !== undefined) {
      const fixture = load(resolve(FIXTURES, publishedFile));
      const fixtureReading = readCapture(fixture, context.background, context.geometry);
      for (const reading of readings) {
        const result = pairMetrics(fixtureReading, reading, context.background, context.geometry);
        for (const metric of NATIVE_DELTA_METRICS) {
          const value = result.metrics[metric];
          if (value !== null && Number.isFinite(value)) againstPublished.get(metric)?.push(value);
        }
      }
    }

    const pairwise: Partial<Record<NativeDeltaMetric, Distribution>> = {};
    const versus: Partial<Record<NativeDeltaMetric, Distribution>> = {};
    for (const metric of NATIVE_DELTA_METRICS) {
      const distribution = distributionOf(pairValues.get(metric) ?? []);
      if (distribution !== null) {
        pairwise[metric] = distribution;
        if (distribution.max > 0) {
          const best = bedNonZero.get(metric);
          if (best === undefined || distribution.max < best) bedNonZero.set(metric, distribution.max);
        }
      }
      const other = distributionOf(againstPublished.get(metric) ?? []);
      if (other !== null) versus[metric] = other;
    }

    const readingSpread: Partial<Record<CaptureReadingName, number>> = {};
    for (const name of CAPTURE_READINGS) {
      const values = scalars
        .map((vector) => vector[name])
        .filter((value): value is number => value !== null && Number.isFinite(value));
      if (values.length > 0) readingSpread[name] = Math.max(...values) - Math.min(...values);
    }

    cells.push({
      profileKey,
      sceneId,
      pose: poseOf(sceneId),
      runs: images.length,
      pairwise,
      runVsPublished: versus,
      readingSpread,
    });

    done += 1;
    if (done % 25 === 0) say(`  ${String(done)} / ${String(runsOf.size)} cells barred`);
  }

  const bedMinimumNonZeroBar: Partial<Record<NativeDeltaMetric, number>> = {};
  for (const [metric, value] of bedNonZero) bedMinimumNonZeroBar[metric] = value;

  const file: BarFile = {
    generatedAt: new Date().toISOString(),
    construction:
      "Per cell and per metric, the distribution of that metric over all 21 unordered pairs of the " +
      "cell's seven raw macOS 27 runs, the lower-numbered run of each pair taken as the reference " +
      "side. Pairwise rather than run-against-published because the delta is a comparison of two " +
      "independently captured, equally valid renderings of one declared cell, and that is what a " +
      "pair of runs is; the run-against-published distribution is recorded beside it as the " +
      "charter's first-named form and as corroboration, and it is a subset of the same behaviour " +
      "because the published bytes are one of the runs'.",
    rule:
      "MOVED on a metric means the 26.5-against-27 value exceeds the MAX of that cell's own " +
      "27-against-27 pairwise distribution. Max and not a quantile: at 21 samples a tail quantile " +
      "is not better estimated than the extreme, and the strict statement the ledger needs is " +
      "'beyond anything this bed did against itself'. Where a cell's own pairwise max is exactly " +
      "zero on a metric — seven byte-identical runs — the bar is the smallest non-zero pairwise " +
      "max anywhere in the 27 bed for that metric (bedMinimumNonZeroBar), so that a cell that " +
      "happened to be perfectly stable is not given an infinitely sharp instrument. The bar is " +
      "27-against-27 only; the 26.5 bed's own run-to-run spread is not in it and is not derivable " +
      "(claims §5.149 §6), so every verdict understates the combined spread of a cross-bed pair.",
    runsRoot,
    metrics: NATIVE_DELTA_METRICS,
    captureReadings: CAPTURE_READINGS,
    bedMinimumNonZeroBar,
    cells,
  };
  mkdirSync(resolve(outPath, ".."), { recursive: true });
  writeFileSync(outPath, `${JSON.stringify(file, null, 1)}\n`);
  say(`native-delta bar: ${String(cells.length)} cells written to ${outPath}`);
}

// ---------------------------------------------------------------------------
// The delta
// ---------------------------------------------------------------------------

interface DeltaRow {
  readonly profileKey27: string;
  readonly profileKey26: string;
  readonly sceneId: string;
  readonly pose: "active" | "inactive";
  readonly fixtureSet: string;
  readonly background: string;
  readonly component: string;
  readonly backdropEncodedMean: number;
  readonly scale: number;
  readonly metrics: MetricVector;
  readonly bar: Readonly<Partial<Record<NativeDeltaMetric, number>>>;
  readonly barSource: Readonly<Partial<Record<NativeDeltaMetric, "cell" | "bed-minimum" | "bed-zero">>>;
  readonly moved: Readonly<Partial<Record<NativeDeltaMetric, boolean>>>;
  readonly readings: PairReadings;
  readonly notes: readonly string[];
}

interface RecedeRow {
  readonly profileKey27: string;
  readonly profileKey26: string;
  readonly activeSceneId: string;
  readonly inactiveSceneId: string;
  readonly scale: number;
  /** (inactive − active) on each bed, then 27's minus 26.5's, per signed reading. */
  readonly recede26: Readonly<Partial<Record<CaptureReadingName, number>>>;
  readonly recede27: Readonly<Partial<Record<CaptureReadingName, number>>>;
  readonly deltaOfRecede: Readonly<Partial<Record<CaptureReadingName, number>>>;
  readonly bar: Readonly<Partial<Record<CaptureReadingName, number>>>;
  readonly barSource: Readonly<Partial<Record<CaptureReadingName, "cell" | "bed-minimum" | "bed-zero">>>;
  readonly moved: Readonly<Partial<Record<CaptureReadingName, boolean>>>;
}

/** The backdrop's own encoded mean, which is how the tone-response law groups cells. */
function encodedMeanOf(image: CalibrationImage): number {
  const count = image.width * image.height;
  let sum = 0;
  for (let i = 0; i < count; i += 1) {
    const src = i * 4;
    sum +=
      (0.2126 * (image.data[src] ?? 0) + 0.7152 * (image.data[src + 1] ?? 0) + 0.0722 * (image.data[src + 2] ?? 0)) /
      255;
  }
  return sum / count;
}

function buildDelta(barPath: string, outDir: string): void {
  const bar = readJson<BarFile>(barPath);

  /**
   * The declared zero-spread fallback, read for the signed capture readings the
   * recede rows are built from. The bar file names the fallback per *metric*
   * only (`bedMinimumNonZeroBar`) because the recede's first cut gave a verdict
   * only where both 27 cells had a non-zero spread of their own, which left 158
   * of 231 recede rows unbarred and read the ledger's recede medians off 18 to
   * 70 rows while 219 pairs were measurable (the independent review of this
   * gate, finding 1, 2026-09-19). The fallback is derived here from the bar
   * file's own committed cells rather than by regenerating the bar, so the
   * declared bar is read and never rewritten, and it is exactly the rule the
   * pair rows already apply: the cell's own spread where it has one, the
   * bed-wide minimum non-zero spread where its seven runs agreed exactly, and
   * zero for a reading whose spread the bed never resolved at all.
   */
  const bedMinimumNonZeroSpread: Partial<Record<CaptureReadingName, number>> = {};
  for (const cell of bar.cells) {
    for (const name of CAPTURE_READINGS) {
      const spread = cell.readingSpread[name];
      if (spread === undefined || spread <= 0) continue;
      const best = bedMinimumNonZeroSpread[name];
      if (best === undefined || spread < best) bedMinimumNonZeroSpread[name] = spread;
    }
  }
  const barByCell = new Map<string, BarCell>();
  for (const cell of bar.cells) barByCell.set(`${cell.profileKey} ${cell.sceneId}`, cell);

  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  const spec = readJson<{
    readonly scenes: readonly { readonly id: string; readonly background: string; readonly component: string }[];
  }>(resolve(REFERENCE, "scenes.json"));
  const geometryMatrix = readSceneGeometry(REFERENCE);
  const backgroundCache = new Map<string, CalibrationImage>();
  const encodedMeanCache = new Map<string, number>();

  const fileOf = new Map<string, { readonly file: string; readonly fixtureSet: string }>();
  for (const profile of manifest.profiles) {
    for (const fixture of profile.fixtures) {
      fileOf.set(`${profile.profileKey} ${fixture.sceneId}`, {
        file: fixture.file,
        fixtureSet: fixture.fixtureSet,
      });
    }
  }

  const rows: DeltaRow[] = [];
  const recedeRows: RecedeRow[] = [];
  const onlyOn27: string[] = [];
  const unbarred: string[] = [];
  /** Per (profile, scene) the signed readings of both beds, for the recede pass. */
  const scalarsByCell = new Map<string, { readonly bed26: CaptureReadingVector; readonly bed27: CaptureReadingVector }>();

  const profiles27 = manifest.profiles.filter((profile) => profile.profileKey.startsWith("apple-macos-27.0-"));
  let done = 0;
  const total = profiles27.reduce((sum, profile) => sum + profile.fixtures.length, 0);

  for (const profile of profiles27) {
    const key26 = counterpartKey(profile.profileKey);
    for (const fixture of profile.fixtures) {
      done += 1;
      if (done % 50 === 0) say(`  ${String(done)} / ${String(total)} cells read`);
      const twin = fileOf.get(`${key26} ${fixture.sceneId}`);
      if (twin === undefined) {
        onlyOn27.push(`${profile.profileKey}/${fixture.sceneId}`);
        continue;
      }

      const image27 = load(resolve(FIXTURES, fixture.file));
      const image26 = load(resolve(FIXTURES, twin.file));
      if (image27.width !== image26.width || image27.height !== image26.height) {
        throw new Error(
          `native-delta: ${fixture.sceneId} is ${String(image27.width)}x${String(image27.height)} on 27 ` +
            `and ${String(image26.width)}x${String(image26.height)} on 26.5`,
        );
      }
      const context = contextFor(
        fixture.sceneId,
        profile.profileKey,
        manifest,
        spec,
        geometryMatrix,
        image27.width,
        image27.height,
        backgroundCache,
      );
      if (context === null) throw new Error(`native-delta: no backdrop for ${fixture.sceneId}`);

      const reading26 = readCapture(image26, context.background, context.geometry);
      const reading27 = readCapture(image27, context.background, context.geometry);
      // The 26.5 fixture is the reference: its silhouette masks the material
      // statistics, because it is the bed every adopted bound was fitted against.
      const result = pairMetrics(reading26, reading27, context.background, context.geometry);

      const cellBar = barByCell.get(`${profile.profileKey} ${fixture.sceneId}`);
      const barValues: Partial<Record<NativeDeltaMetric, number>> = {};
      const barSource: Partial<Record<NativeDeltaMetric, "cell" | "bed-minimum" | "bed-zero">> = {};
      const moved: Partial<Record<NativeDeltaMetric, boolean>> = {};
      if (cellBar === undefined) {
        // Every published 27 cell has seven raw runs, so this cannot happen on
        // this bed — and if it ever does, the cell must be unbarred and visible
        // rather than silently judged against something else's spread.
        unbarred.push(`${profile.profileKey}/${fixture.sceneId}`);
      }
      for (const metric of NATIVE_DELTA_METRICS) {
        const value = result.metrics[metric];
        if (value === null || !Number.isFinite(value)) continue;
        const own = cellBar?.pairwise[metric]?.max;
        if (own === undefined) continue;
        /*
         * Three levels, in the order the declaration gives them.
         *
         * The cell's own non-zero pairwise max is the bar. Where the cell's own
         * seven runs agreed exactly, the bar is the smallest non-zero pairwise
         * max anywhere in the bed — the finest difference this bed resolved on
         * that metric. And where the bed resolved NO non-zero difference at all
         * — which happens on the two p95 rows and on the rim's peak depth,
         * because a percentile over pixels and a rounded ring index are both
         * blind to the handful of pixels a re-run moves — the bar is exactly
         * zero, and it is the strongest of the three rather than the weakest: a
         * non-zero cross-bed reading is then beyond every one of the bed's
         * 21 x 624 pairs. `barSource` says which of the three a verdict rests
         * on, so none of them can be read as the others.
         */
        const floor = bar.bedMinimumNonZeroBar[metric];
        const bound = own > 0 ? own : (floor ?? 0);
        barSource[metric] = own > 0 ? "cell" : floor === undefined ? "bed-zero" : "bed-minimum";
        barValues[metric] = bound;
        moved[metric] = value > bound;
      }

      let encodedMean = encodedMeanCache.get(context.backgroundId);
      if (encodedMean === undefined) {
        encodedMean = encodedMeanOf(context.background);
        encodedMeanCache.set(context.backgroundId, encodedMean);
      }
      const scene = spec.scenes.find((entry) => entry.id === fixture.sceneId);

      rows.push({
        profileKey27: profile.profileKey,
        profileKey26: key26,
        sceneId: fixture.sceneId,
        pose: poseOf(fixture.sceneId),
        fixtureSet: fixture.fixtureSet,
        background: scene?.background ?? "?",
        component: scene?.component ?? "?",
        backdropEncodedMean: encodedMean,
        scale: context.scale,
        metrics: result.metrics,
        bar: barValues,
        barSource,
        moved,
        readings: result.readings,
        notes: result.notes,
      });

      scalarsByCell.set(`${profile.profileKey} ${fixture.sceneId}`, {
        bed26: captureReadings(image26, reading26, context),
        bed27: captureReadings(image27, reading27, context),
      });
    }
  }

  // The recede, as its own row set: (27 inactive − 27 active) against
  // (26.5 inactive − 26.5 active), so the version change and the recede cannot
  // be read as each other (c9a §5.134's warning, W29 Risks).
  for (const profile of profiles27) {
    const key26 = counterpartKey(profile.profileKey);
    for (const fixture of profile.fixtures) {
      const activeId = activeTwinOf(fixture.sceneId);
      if (activeId === null) continue;
      const inactive = scalarsByCell.get(`${profile.profileKey} ${fixture.sceneId}`);
      const active = scalarsByCell.get(`${profile.profileKey} ${activeId}`);
      if (inactive === undefined || active === undefined) continue;
      const inactiveBar = barByCell.get(`${profile.profileKey} ${fixture.sceneId}`);
      const activeBar = barByCell.get(`${profile.profileKey} ${activeId}`);

      const recede26: Partial<Record<CaptureReadingName, number>> = {};
      const recede27: Partial<Record<CaptureReadingName, number>> = {};
      const deltaOfRecede: Partial<Record<CaptureReadingName, number>> = {};
      const barValues: Partial<Record<CaptureReadingName, number>> = {};
      const barSource: Partial<Record<CaptureReadingName, "cell" | "bed-minimum" | "bed-zero">> = {};
      const moved: Partial<Record<CaptureReadingName, boolean>> = {};
      for (const name of CAPTURE_READINGS) {
        const i26 = inactive.bed26[name];
        const a26 = active.bed26[name];
        const i27 = inactive.bed27[name];
        const a27 = active.bed27[name];
        if (i26 === null || a26 === null || i27 === null || a27 === null) continue;
        recede26[name] = i26 - a26;
        recede27[name] = i27 - a27;
        const difference = i27 - a27 - (i26 - a26);
        deltaOfRecede[name] = difference;
        // Both 27 cells contribute their own spread to the difference of
        // differences, so the bar is their sum. The 26.5 pair contributes an
        // unmeasured amount on top, which is stated and not estimated. Each
        // side takes its own spread where it has one and the bed-wide minimum
        // non-zero spread where its seven runs agreed exactly, so a pair of
        // perfectly stable cells is barred rather than dropped; where the bed
        // resolved no spread at all for the reading the bar is exactly zero,
        // which is the strongest of the three and is said as `bed-zero`.
        const inactiveSpread = inactiveBar?.readingSpread[name] ?? 0;
        const activeSpread = activeBar?.readingSpread[name] ?? 0;
        const floor = bedMinimumNonZeroSpread[name];
        const own =
          (inactiveSpread > 0 ? inactiveSpread : (floor ?? 0)) + (activeSpread > 0 ? activeSpread : (floor ?? 0));
        barSource[name] =
          inactiveSpread > 0 && activeSpread > 0 ? "cell" : floor === undefined ? "bed-zero" : "bed-minimum";
        barValues[name] = own;
        moved[name] = Math.abs(difference) > own;
      }
      recedeRows.push({
        profileKey27: profile.profileKey,
        profileKey26: key26,
        activeSceneId: activeId,
        inactiveSceneId: fixture.sceneId,
        scale: parseProfileKey(profile.profileKey)?.scale ?? 1,
        recede26,
        recede27,
        deltaOfRecede,
        bar: barValues,
        barSource,
        moved,
      });
    }
  }

  mkdirSync(outDir, { recursive: true });
  writeFileSync(
    resolve(outDir, "native-delta.json"),
    `${JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        barFile: barPath,
        barRule: bar.rule,
        metrics: NATIVE_DELTA_METRICS,
        reference: "the 26.5 fixture is the reference side of every pair; its silhouette masks the material rows",
        onlyOn27,
        unbarred,
        rows,
      },
      null,
      1,
    )}\n`,
  );
  writeFileSync(
    resolve(outDir, "recede-delta.json"),
    `${JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        construction:
          "(27 inactive − 27 active) − (26.5 inactive − 26.5 active), per signed capture reading, " +
          "so that the version change and the recede are not confounded. The bar is the sum of the " +
          "two 27 cells' run-to-run reading spreads, each side taking the bed-wide minimum non-zero " +
          "spread where its own seven runs agreed exactly and the whole bar being zero where the " +
          "bed resolved no spread for that reading at all — the same three-level fallback the pair " +
          "rows take, said per reading in `barSource`. The 26.5 pair contributes an unmeasured " +
          "amount on top of it.",
        readings: CAPTURE_READINGS,
        rows: recedeRows,
      },
      null,
      1,
    )}\n`,
  );
  const recedeReadings = recedeRows.reduce((total, row) => total + Object.keys(row.bar).length, 0);
  const recedeMeasurable = recedeRows.reduce((total, row) => total + Object.keys(row.deltaOfRecede).length, 0);
  say(
    `native-delta: ${String(rows.length)} pair rows, ${String(recedeRows.length)} recede rows, ` +
      `${String(onlyOn27.length)} cells only on 27 (reported, not diffed), ` +
      `${String(unbarred.length)} pair cells with no bar; ` +
      `${String(recedeReadings)} of ${String(recedeMeasurable)} measurable recede readings barred`,
  );
}

// ---------------------------------------------------------------------------
// The tables the ledger's per-law verdicts are read off
// ---------------------------------------------------------------------------

/**
 * The laws the material names, and the metrics each one is carried by.
 *
 * The grouping is the ledger's, not the instrument's: a verdict is stated per
 * law and has to be traceable to rows, so the rows are grouped here once and
 * every table below reads this list rather than restating it.
 */
const LAWS: readonly { readonly law: string; readonly metrics: readonly NativeDeltaMetric[] }[] = [
  {
    law: "silhouette / geometry",
    metrics: ["silhouetteIoUComplement", "contourDistanceMeanPx", "contourDistanceP95Px", "silhouetteAreaDeltaPx"],
  },
  { law: "corner geometry", metrics: ["cornerCurvatureDeltaPerPx"] },
  {
    law: "rim band / edge darkening",
    metrics: ["rimContourDeltaMax", "rimLocalDeltaMax", "rimRow0DeltaMax", "rimPeakDelta", "rimPeakDepthDeltaPx", "rimFwhmDeltaPx"],
  },
  {
    law: "highlight amplitude and position",
    metrics: ["highlightBinDeltaMax", "highlightBinDeltaMean", "highlightIntegralDeltaMax", "highlightRatioDelta", "highlightPeakAngleDeltaDeg"],
  },
  { law: "interior level", metrics: ["interiorMeanDelta", "bodyLevelDelta"] },
  { law: "tone response by backdrop level", metrics: ["transferSlopeDelta", "transferOffsetDelta"] },
  { law: "scatter / diffusion", metrics: ["interiorStdDevDelta"] },
  { law: "tint shade", metrics: ["tintDeltaLDelta", "tintChromaDelta", "tintHueShiftDeltaDeg"] },
  {
    law: "the whole cell, as the fidelity read sees it",
    metrics: ["ssimComplement", "ssimBandComplement", "ssimInteriorComplement", "ssimOutsideComplement", "oklabDeltaEMean", "oklabDeltaEP95", "oklabDeltaEBodyMean", "edgeWeightedMean"],
  },
];

/** The signed 27-minus-26.5 reading behind a metric, where the pair carries one. */
const SIGNED_OF: Partial<Record<NativeDeltaMetric, keyof PairReadings>> = {
  interiorMeanDelta: "interiorMean",
  interiorStdDevDelta: "interiorStdDev",
  bodyLevelDelta: "bodyLevel",
  transferSlopeDelta: "transferSlope",
  transferOffsetDelta: "transferOffset",
  rimContourDeltaMax: "rimContourMeanSide",
  rimPeakDelta: "rimPeak",
  rimPeakDepthDeltaPx: "rimPeakDepthPx",
  rimFwhmDeltaPx: "rimFwhmPx",
  highlightRatioDelta: "highlightRatio",
  cornerCurvatureDeltaPerPx: "cornerCurvaturePerPx",
  tintDeltaLDelta: "tintDeltaL",
  tintChromaDelta: "tintChroma",
};

function signedDelta(row: DeltaRow, metric: NativeDeltaMetric): number | null {
  const name = SIGNED_OF[metric];
  if (name === undefined) return null;
  const pair = row.readings[name];
  if (!Array.isArray(pair) || pair.length !== 2) return null;
  const [before, after] = pair as readonly [number, number];
  if (typeof before !== "number" || typeof after !== "number") return null;
  return after - before;
}

function median(values: readonly number[]): number {
  if (values.length === 0) return NaN;
  const sorted = [...values].sort((x, y) => x - y);
  return sorted[Math.floor(sorted.length / 2)] as number;
}

interface Tally {
  readonly measured: number;
  readonly moved: number;
  readonly medianValue: number;
  readonly medianBar: number;
  /**
   * The median of Δ/bar over the measured cells — the number that says whether
   * a verdict is comfortable or marginal. A metric can be "moved" on every cell
   * at a ratio of 1.1, which is a different claim from moved at 50.
   */
  readonly medianRatio: number;
  readonly worstRatio: number;
  readonly worstScene: string;
  readonly medianSigned: number | null;
  readonly signedPositive: number;
  readonly signedNegative: number;
}

function tally(rows: readonly DeltaRow[], metric: NativeDeltaMetric): Tally {
  const values: number[] = [];
  const bars: number[] = [];
  const ratios: number[] = [];
  const signed: number[] = [];
  let moved = 0;
  let worstRatio = 0;
  let worstScene = "—";
  let positive = 0;
  let negative = 0;
  for (const row of rows) {
    const value = row.metrics[metric];
    const bound = row.bar[metric];
    if (value === null || value === undefined || bound === undefined) continue;
    values.push(value);
    bars.push(bound);
    if (row.moved[metric] === true) moved += 1;
    const ratio = bound === 0 ? Number.POSITIVE_INFINITY : value / bound;
    ratios.push(ratio);
    if (ratio > worstRatio) {
      worstRatio = ratio;
      worstScene = `${row.profileKey27.replace("apple-macos-27.0-", "").replace("-glass0.5", "")}/${row.sceneId}`;
    }
    const sign = signedDelta(row, metric);
    if (sign !== null) {
      signed.push(sign);
      if (row.moved[metric] === true) {
        if (sign > 0) positive += 1;
        else if (sign < 0) negative += 1;
      }
    }
  }
  return {
    measured: values.length,
    moved,
    medianValue: median(values),
    medianBar: median(bars),
    medianRatio: median(ratios),
    worstRatio,
    worstScene,
    medianSigned: signed.length === 0 ? null : median(signed),
    signedPositive: positive,
    signedNegative: negative,
  };
}

const shortKey = (key: string): string =>
  key.replace("apple-macos-27.0-", "").replace("-glass0.5", "");

function buildTables(dir: string, barPath: string): void {
  const delta = readJson<{
    readonly rows: readonly DeltaRow[];
    readonly onlyOn27: readonly string[];
    readonly unbarred: readonly string[];
  }>(resolve(dir, "native-delta.json"));
  const recede = readJson<{ readonly rows: readonly RecedeRow[] }>(resolve(dir, "recede-delta.json"));
  const bar = readJson<BarFile>(barPath);
  const lines: string[] = [];
  const out = (line: string): void => void lines.push(line);

  const profiles = [...new Set(delta.rows.map((row) => row.profileKey27))].sort();
  const poses: readonly ("active" | "inactive")[] = ["active", "inactive"];

  out("# W29 G2 — the native delta, read off the rows");
  out("");
  const recedeBarred = recede.rows.reduce((total, row) => total + Object.keys(row.bar).length, 0);
  const recedeMeasurable = recede.rows.reduce((total, row) => total + Object.keys(row.deltaOfRecede).length, 0);
  out(`${String(delta.rows.length)} pair rows; ${String(delta.unbarred.length)} PAIR cells with no bar; ${String(delta.onlyOn27.length)} cells only on 27, reported not diffed:`);
  for (const cell of delta.onlyOn27) out(`  ${cell}`);
  out("");
  out(`${String(recede.rows.length)} recede rows, on which ${String(recedeBarred)} of ${String(recedeMeasurable)} measurable readings carry a bar.`);
  out("");
  out("Every count is 'moved / measured', against the cell's own 27-against-27 bar (bar-declaration.md).");
  out("The two accessibility profiles carry a confound the material cannot be separated from:");
  out("macOS 27 decoupled Reduce Transparency from Increase Contrast, so the 27 increased-contrast");
  out("bed is a DIFFERENT STATE from the 26.5 bed of that name (§5.150 Part B §3).");
  out("");

  out("## Moved cells per metric per profile, active and inactive apart");
  out("");
  for (const pose of poses) {
    out(`### pose: ${pose}`);
    out("");
    const header = ["metric".padEnd(30), ...profiles.map((key) => shortKey(key).padStart(26))].join(" ");
    out(header);
    out("-".repeat(header.length));
    for (const metric of NATIVE_DELTA_METRICS) {
      const cells = profiles.map((key) => {
        const subset = delta.rows.filter((row) => row.profileKey27 === key && row.pose === pose);
        const stats = tally(subset, metric);
        return (stats.measured === 0 ? "—" : `${String(stats.moved)}/${String(stats.measured)}`).padStart(26);
      });
      out([metric.padEnd(30), ...cells].join(" "));
    }
    out("");
  }

  out("## Per law, over the whole bed and per pose");
  out("");
  for (const { law, metrics } of LAWS) {
    out(`### ${law}`);
    out("");
    out(
      `${"metric".padEnd(30)} ${"pose".padEnd(9)} ${"moved/meas".padStart(11)} ${"median Δ".padStart(12)} ` +
        `${"median bar".padStart(12)} ${"med Δ/bar".padStart(10)} ${"worst Δ/bar".padStart(12)} ${"median signed".padStart(14)} ` +
        `${"↑/↓ of moved".padStart(13)}  worst cell`,
    );
    for (const metric of metrics) {
      for (const pose of poses) {
        const subset = delta.rows.filter((row) => row.pose === pose);
        const stats = tally(subset, metric);
        if (stats.measured === 0) continue;
        out(
          `${metric.padEnd(30)} ${pose.padEnd(9)} ` +
            `${`${String(stats.moved)}/${String(stats.measured)}`.padStart(11)} ` +
            `${stats.medianValue.toExponential(3).padStart(12)} ` +
            `${stats.medianBar.toExponential(3).padStart(12)} ` +
            `${stats.medianRatio.toFixed(2).padStart(10)} ` +
            `${stats.worstRatio.toFixed(1).padStart(12)} ` +
            `${(stats.medianSigned === null ? "—" : stats.medianSigned.toExponential(3)).padStart(14)} ` +
            `${`${String(stats.signedPositive)}/${String(stats.signedNegative)}`.padStart(13)}  ${stats.worstScene}`,
        );
      }
    }
    out("");
  }

  // Tone response: the law is a function of the backdrop's level, so the cells
  // are grouped by their backdrop's own encoded mean rather than by scene.
  out("## Tone response, cells grouped by their backdrop's encoded mean");
  out("");
  const bands: readonly (readonly [number, number])[] = [
    [0, 0.1], [0.1, 0.25], [0.25, 0.45], [0.45, 0.65], [0.65, 0.85], [0.85, 1.01],
  ];
  out(
    `${"band".padEnd(14)} ${"cells".padStart(6)} ${"interior moved".padStart(15)} ` +
      `${"median signed ΔL".padStart(17)} ${"slope moved".padStart(12)} ${"median Δslope".padStart(14)} ` +
      `${"median Δoffset".padStart(15)}`,
  );
  for (const [low, high] of bands) {
    const subset = delta.rows.filter(
      (row) => row.backdropEncodedMean >= low && row.backdropEncodedMean < high,
    );
    if (subset.length === 0) continue;
    const level = tally(subset, "interiorMeanDelta");
    const slope = tally(subset, "transferSlopeDelta");
    const offset = tally(subset, "transferOffsetDelta");
    out(
      `${`${low.toFixed(2)}–${high.toFixed(2)}`.padEnd(14)} ${String(subset.length).padStart(6)} ` +
        `${`${String(level.moved)}/${String(level.measured)}`.padStart(15)} ` +
        `${(level.medianSigned ?? NaN).toExponential(3).padStart(17)} ` +
        `${`${String(slope.moved)}/${String(slope.measured)}`.padStart(12)} ` +
        `${(slope.medianSigned ?? NaN).toExponential(3).padStart(14)} ` +
        `${(offset.medianSigned ?? NaN).toExponential(3).padStart(15)}`,
    );
  }
  out("");

  // Scatter is only identifiable where the backdrop has structure to scatter.
  out("## Scatter, structured backdrops against solid ones");
  out("");
  const structured = (row: DeltaRow): boolean =>
    /^(checkerboard|hc-text|photo|impulse)/.test(row.background);
  for (const [label, subset] of [
    ["structured", delta.rows.filter(structured)],
    ["solid", delta.rows.filter((row) => !structured(row))],
  ] as const) {
    const stats = tally(subset, "interiorStdDevDelta");
    out(
      `${label.padEnd(12)} ${`${String(stats.moved)}/${String(stats.measured)}`.padStart(11)} moved   ` +
        `median signed ${(stats.medianSigned ?? NaN).toExponential(3)}   ` +
        `↑/↓ of moved ${String(stats.signedPositive)}/${String(stats.signedNegative)}   worst ${stats.worstScene}`,
    );
  }
  out("");
  out("By backdrop id, structured only:");
  const backgrounds = [...new Set(delta.rows.filter(structured).map((row) => row.background))].sort();
  for (const background of backgrounds) {
    const stats = tally(delta.rows.filter((row) => row.background === background), "interiorStdDevDelta");
    out(
      `  ${background.padEnd(18)} ${`${String(stats.moved)}/${String(stats.measured)}`.padStart(9)}   ` +
        `median signed ${(stats.medianSigned ?? NaN).toExponential(3)}`,
    );
  }
  out("");

  out("## Tint shade, the tinted cells only");
  out("");
  const tinted = delta.rows.filter((row) => row.sceneId.includes("-tint-"));
  for (const metric of ["tintDeltaLDelta", "tintChromaDelta", "tintHueShiftDeltaDeg"] as const) {
    const stats = tally(tinted, metric);
    out(
      `${metric.padEnd(24)} ${`${String(stats.moved)}/${String(stats.measured)}`.padStart(9)} moved   ` +
        `median Δ ${stats.medianValue.toExponential(3)}   median signed ` +
        `${(stats.medianSigned ?? NaN).toExponential(3)}   worst ${stats.worstScene}`,
    );
  }
  out("");
  out("The same three on the untinted cells, as the control:");
  const untinted = delta.rows.filter((row) => !row.sceneId.includes("-tint-"));
  for (const metric of ["tintDeltaLDelta", "tintChromaDelta", "tintHueShiftDeltaDeg"] as const) {
    const stats = tally(untinted, metric);
    out(
      `${metric.padEnd(24)} ${`${String(stats.moved)}/${String(stats.measured)}`.padStart(9)} moved   ` +
        `median Δ ${stats.medianValue.toExponential(3)}   median signed ${(stats.medianSigned ?? NaN).toExponential(3)}`,
    );
  }
  out("");

  out("## Corner geometry: the characteristic corner curvature of each bed, by component");
  out("");
  const components = [...new Set(delta.rows.map((row) => row.component))].sort();
  out(`${"component".padEnd(20)} ${"cells".padStart(6)} ${"moved".padStart(6)} ${"median κ 26.5".padStart(14)} ${"median κ 27".padStart(13)} ${"implied r 26.5→27".padStart(19)}`);
  for (const component of components) {
    const subset = delta.rows.filter(
      (row) => row.component === component && row.readings.cornerCurvaturePerPx !== null,
    );
    if (subset.length === 0) continue;
    const before = median(subset.map((row) => (row.readings.cornerCurvaturePerPx as readonly [number, number])[0]));
    const after = median(subset.map((row) => (row.readings.cornerCurvaturePerPx as readonly [number, number])[1]));
    const moved = subset.filter((row) => row.moved.cornerCurvatureDeltaPerPx === true).length;
    out(
      `${component.padEnd(20)} ${String(subset.length).padStart(6)} ${String(moved).padStart(6)} ` +
        `${before.toFixed(5).padStart(14)} ${after.toFixed(5).padStart(13)} ` +
        `${`${(1 / before).toFixed(2)} → ${(1 / after).toFixed(2)} px`.padStart(19)}`,
    );
  }
  out("");

  out("## The recede, as its own row set");
  out("");
  out("(27 inactive − 27 active) − (26.5 inactive − 26.5 active), per signed reading.");
  out(`${String(recede.rows.length)} scene pairs.`);
  out(
    "'moved/meas' is over the rows that carry the reading at all: each side of the pair takes its " +
      "own run-to-run spread where it has one and the bed-wide minimum non-zero spread where its " +
      "seven runs agreed exactly, so a reading is measured wherever both beds resolve it.",
  );
  out("");
  out(
    `${"reading".padEnd(20)} ${"moved/meas".padStart(11)} ${"median recede 26.5".padStart(19)} ` +
      `${"median recede 27".padStart(17)} ${"median difference".padStart(18)} ${"median bar".padStart(12)}`,
  );
  for (const name of CAPTURE_READINGS) {
    const usable = recede.rows.filter((row) => row.deltaOfRecede[name] !== undefined && row.bar[name] !== undefined);
    if (usable.length === 0) continue;
    const moved = usable.filter((row) => row.moved[name] === true).length;
    out(
      `${name.padEnd(20)} ${`${String(moved)}/${String(usable.length)}`.padStart(11)} ` +
        `${median(usable.map((row) => row.recede26[name] as number)).toExponential(3).padStart(19)} ` +
        `${median(usable.map((row) => row.recede27[name] as number)).toExponential(3).padStart(17)} ` +
        `${median(usable.map((row) => row.deltaOfRecede[name] as number)).toExponential(3).padStart(18)} ` +
        `${median(usable.map((row) => row.bar[name] as number)).toExponential(3).padStart(12)}`,
    );
  }
  out("");

  out("## Where the bar came from, per metric");
  out("");
  out(
    "A cell whose seven runs agreed exactly on a metric has no spread of its own and takes the " +
      "bed-wide minimum non-zero bar. That is the sharpest honest bar available and it is also the " +
      "most generous to a verdict of 'moved', so the share matters to how a verdict reads: the " +
      "median Δ/bar in the law tables is what says whether the movement is comfortable there.",
  );
  out("");
  out(
    `${"metric".padEnd(30)} ${"own bar".padStart(9)} ${"bed minimum".padStart(12)} ` +
      `${"bed zero".padStart(9)} ${"bed minimum value".padStart(18)}`,
  );
  for (const metric of NATIVE_DELTA_METRICS) {
    let fromCell = 0;
    let fromBed = 0;
    let fromZero = 0;
    for (const row of delta.rows) {
      if (row.barSource[metric] === "cell") fromCell += 1;
      if (row.barSource[metric] === "bed-minimum") fromBed += 1;
      if (row.barSource[metric] === "bed-zero") fromZero += 1;
    }
    if (fromCell + fromBed + fromZero === 0) continue;
    const floor = bar.bedMinimumNonZeroBar[metric];
    out(
      `${metric.padEnd(30)} ${String(fromCell).padStart(9)} ${String(fromBed).padStart(12)} ` +
        `${String(fromZero).padStart(9)} ${(floor === undefined ? "—" : floor.toExponential(3)).padStart(18)}`,
    );
  }
  out("");

  writeFileSync(resolve(dir, "law-tables.txt"), `${lines.join("\n")}\n`);
  say(`native-delta tables: ${resolve(dir, "law-tables.txt")}`);
}

// ---------------------------------------------------------------------------
// Sheets
// ---------------------------------------------------------------------------

/**
 * 26.5 | 27 | difference, side by side, with the difference amplified and the
 * amplification stated in the file name. The difference is `|27 − 26.5|` per
 * channel times the gain, clamped — a signed difference rendered as a colour
 * would need a legend the eye has to learn, and what a reader is looking for
 * here is WHERE the two beds differ and by how much, which an amplified
 * magnitude shows directly.
 */
function writeSheet(path: string, columns: readonly CalibrationImage[]): void {
  const gap = 8;
  const width = columns.reduce((sum, image) => sum + image.width, 0) + gap * (columns.length - 1);
  const height = Math.max(...columns.map((image) => image.height));
  const png = new PNG({ width, height });
  png.data.fill(24);
  let x0 = 0;
  for (const image of columns) {
    for (let y = 0; y < image.height; y += 1) {
      for (let x = 0; x < image.width; x += 1) {
        const src = (y * image.width + x) * 4;
        const dst = (y * width + x0 + x) * 4;
        png.data[dst] = image.data[src] ?? 0;
        png.data[dst + 1] = image.data[src + 1] ?? 0;
        png.data[dst + 2] = image.data[src + 2] ?? 0;
        png.data[dst + 3] = 255;
      }
    }
    x0 += image.width + gap;
  }
  mkdirSync(resolve(path, ".."), { recursive: true });
  writeFileSync(path, PNG.sync.write(png));
}

function amplifiedDifference(a: CalibrationImage, b: CalibrationImage, gain: number): CalibrationImage {
  const count = a.width * a.height;
  const data = new Uint8Array(count * 4);
  for (let i = 0; i < count; i += 1) {
    const src = i * 4;
    for (let c = 0; c < 3; c += 1) {
      const delta = Math.abs((a.data[src + c] ?? 0) - (b.data[src + c] ?? 0)) * gain;
      data[src + c] = Math.min(255, Math.round(delta));
    }
    data[src + 3] = 255;
  }
  return createImage(a.width, a.height, data);
}

function buildSheets(deltaDir: string, gain: number, perProfile: number): void {
  const delta = readJson<{ readonly rows: readonly DeltaRow[] }>(resolve(deltaDir, "native-delta.json"));
  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  const fileOf = new Map<string, string>();
  for (const profile of manifest.profiles) {
    for (const fixture of profile.fixtures) fileOf.set(`${profile.profileKey} ${fixture.sceneId}`, fixture.file);
  }
  const sheetDir = resolve(deltaDir, "sheets");

  const emit = (row: DeltaRow, name: string): void => {
    const file27 = fileOf.get(`${row.profileKey27} ${row.sceneId}`);
    const file26 = fileOf.get(`${row.profileKey26} ${row.sceneId}`);
    if (file27 === undefined || file26 === undefined) return;
    const image27 = load(resolve(FIXTURES, file27));
    const image26 = load(resolve(FIXTURES, file26));
    // The columns are 26.5 | 27 | the amplified difference, in that order, and
    // the gain is in the file name so a sheet cannot be read without it.
    writeSheet(resolve(sheetDir, `${name}__x${String(gain)}.png`), [
      image26,
      image27,
      amplifiedDifference(image27, image26, gain),
    ]);
  };

  // Per profile at both scales: the cells whose whole-cell ΔE moved most.
  const byProfile = new Map<string, DeltaRow[]>();
  for (const row of delta.rows) {
    const list = byProfile.get(row.profileKey27) ?? [];
    list.push(row);
    byProfile.set(row.profileKey27, list);
  }
  for (const [profileKey, list] of byProfile) {
    const ranked = [...list].sort(
      (x, y) => (y.metrics.oklabDeltaEMean ?? 0) - (x.metrics.oklabDeltaEMean ?? 0),
    );
    const short = profileKey.replace("apple-macos-27.0-", "").replace("-glass0.5", "");
    ranked.slice(0, perProfile).forEach((row, index) => {
      emit(row, `profile__${short}__${String(index + 1).padStart(2, "0")}__${row.sceneId}`);
    });
  }

  // One sheet per law, showing its clearest mover.
  const laws: readonly (readonly [string, NativeDeltaMetric])[] = [
    ["silhouette", "silhouetteIoUComplement"],
    ["corner-geometry", "cornerCurvatureDeltaPerPx"],
    ["rim-band", "rimContourDeltaMax"],
    ["highlight", "highlightBinDeltaMax"],
    ["interior-level", "interiorMeanDelta"],
    ["tone-response", "transferSlopeDelta"],
    ["scatter", "interiorStdDevDelta"],
    ["tint-shade", "tintChromaDelta"],
  ];
  for (const [law, metric] of laws) {
    const ranked = delta.rows
      .filter((row) => row.moved[metric] === true)
      .sort((x, y) => (y.metrics[metric] ?? 0) / (y.bar[metric] ?? 1) - (x.metrics[metric] ?? 0) / (x.bar[metric] ?? 1));
    ranked.slice(0, 3).forEach((row, index) => {
      const short = row.profileKey27.replace("apple-macos-27.0-", "").replace("-glass0.5", "");
      emit(row, `law__${law}__${String(index + 1)}__${short}__${row.sceneId}`);
    });
  }
  say(`native-delta sheets: written under ${sheetDir}`);
}

// ---------------------------------------------------------------------------
// The port's check against the Python originals' committed 26.5 output
// ---------------------------------------------------------------------------

interface ContourReference {
  readonly rows: readonly {
    readonly scene: string;
    readonly bodyNative: number;
    readonly rimNative: readonly (number | null)[];
    readonly rimLocalNative: readonly (number | null)[];
    readonly baseNative: readonly (number | null)[];
  }[];
}

interface AngularReference {
  readonly rows: readonly {
    readonly scene: string;
    readonly native: { readonly bins: readonly (number | null)[]; readonly integral: readonly (number | null)[] };
  }[];
}

/**
 * The Python originals wrote their JSON with `json.dump`, which emits the bare
 * tokens `NaN`, `Infinity` and `-Infinity` for the values those instruments
 * report as absent or unbounded. Those are not JSON, and they are read back
 * here as `null`, which is what this port's own vocabulary calls the same thing.
 */
function readPythonJson<T>(path: string): T {
  return JSON.parse(
    readFileSync(path, "utf8").replace(/(?<=[:,[\s])-?(?:NaN|Infinity)\b/g, "null"),
  ) as T;
}

function verifyReaders(): void {
  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  const geometryMatrix = readSceneGeometry(REFERENCE);
  const fileOf = new Map<string, string>();
  for (const profile of manifest.profiles) {
    for (const fixture of profile.fixtures) fileOf.set(`${profile.profileKey} ${fixture.sceneId}`, fixture.file);
  }

  const w23 = resolve(PACKAGE_ROOT, "results", "2026-09-08-w23-collapsed-rim", "g0", "reads");
  const w24 = resolve(PACKAGE_ROOT, "results", "2026-09-09-w24-lit-edge", "g0", "reads");
  const profiles = [
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-1x-dark-standard",
    "apple-macos-26.5-2x-light-standard",
    "apple-macos-26.5-2x-dark-standard",
    "apple-macos-26.5-1x-light-increased-contrast",
    "apple-macos-26.5-1x-light-reduced-transparency",
  ];

  let contourCells = 0;
  let contourReadings = 0;
  let contourBeyond = 0;
  let contourWorst = 0;
  let angularCells = 0;
  let angularReadings = 0;
  let angularBeyond = 0;
  let angularWorst = 0;
  let angularWorstAt = "";
  const take = (
    got: number,
    expected: number,
    where: string,
    onto: "contour" | "angular",
  ): void => {
    const delta = Math.abs(got - expected);
    if (onto === "contour") {
      contourReadings += 1;
      if (delta > 1e-9) contourBeyond += 1;
      contourWorst = Math.max(contourWorst, delta);
    } else {
      angularReadings += 1;
      if (delta > 1e-9) angularBeyond += 1;
      if (delta > angularWorst) {
        angularWorst = delta;
        angularWorstAt = where;
      }
    }
  };
  for (const profileKey of profiles) {
    const scale = parseProfileKey(profileKey)?.scale ?? 1;
    const contourPath = resolve(w23, `canonical-${profileKey}-webgpu.json`);
    if (existsSync(contourPath)) {
      const reference = readPythonJson<ContourReference>(contourPath);
      for (const row of reference.rows) {
        const file = fileOf.get(`${profileKey} ${row.scene}`);
        if (file === undefined) continue;
        const box = declaredBox(declaredComponentOf(geometryMatrix, row.scene), geometryMatrix.canvas, scale);
        if (box === null) continue;
        const mine = contourRimRead(rasterOf(load(resolve(FIXTURES, file))), box, scale);
        contourCells += 1;
        take(mine.body, row.bodyNative, `${row.scene} body`, "contour");
        RIM_SIDES.forEach((side, index) => {
          const expected = row.rimNative[index];
          const expectedLocal = row.rimLocalNative[index];
          const expectedBase = row.baseNative[index];
          const got = mine.sides[side];
          if (expected === null || expected === undefined) {
            // The original reports `NaN` where the straight span is empty. The
            // port must be absent in exactly the same places or the two readers
            // are reading different geometry, so a finite value here is fatal.
            if (Number.isFinite(got.rim)) contourWorst = Number.POSITIVE_INFINITY;
            return;
          }
          take(got.rim, expected, `${row.scene} ${side} rim`, "contour");
          if (expectedLocal !== null && expectedLocal !== undefined) {
            take(got.rimLocal, expectedLocal, `${row.scene} ${side} rimLocal`, "contour");
          }
          if (expectedBase !== null && expectedBase !== undefined) {
            take(got.base, expectedBase, `${row.scene} ${side} base`, "contour");
          }
        });
      }
    }

    const angularPath = resolve(w24, `${profileKey}__webgpu.json`);
    if (existsSync(angularPath)) {
      const reference = readPythonJson<AngularReference>(angularPath);
      for (const row of reference.rows) {
        const file = fileOf.get(`${profileKey} ${row.scene}`);
        if (file === undefined) continue;
        const box = declaredBox(declaredComponentOf(geometryMatrix, row.scene), geometryMatrix.canvas, scale);
        if (box === null) continue;
        const mine = angularRead(rasterOf(load(resolve(FIXTURES, file))), box, scale);
        angularCells += 1;
        for (let k = 0; k < mine.bins.length; k += 1) {
          const expected = row.native.bins[k];
          const got = mine.bins[k];
          if (expected === null || expected === undefined || got === null || got === undefined) continue;
          take(got, expected, `${profileKey} ${row.scene} bin[${String(k)}]`, "angular");
          const expectedBand = row.native.integral[k];
          const gotBand = mine.integral[k];
          if (expectedBand !== null && expectedBand !== undefined && gotBand !== null && gotBand !== undefined) {
            take(gotBand, expectedBand, `${profileKey} ${row.scene} integral[${String(k)}]`, "angular");
          }
        }
      }
    }
  }

  say("");
  say("The ported readers against the Python originals' committed 26.5 output");
  say(
    `  W23 contour reader: ${String(contourCells)} cells, ${String(contourReadings)} readings, ` +
      `${String(contourBeyond)} beyond 1e-9, worst ${contourWorst.toExponential(3)}`,
  );
  say(
    `  W24 angular reader: ${String(angularCells)} cells, ${String(angularReadings)} readings, ` +
      `${String(angularBeyond)} beyond 1e-9, worst ${angularWorst.toExponential(3)} at ${angularWorstAt}`,
  );
  say("");
  /*
   * Two different tolerances, and the difference is the measurement.
   *
   * The contour reader is an average over whole rows of pixels and reproduces
   * the original to floating-point noise, so anything above 1e-9 there would be
   * a real disagreement about geometry or units.
   *
   * The angular reader takes a MAXIMUM along a normal at sub-pixel steps, and
   * its sample coordinates are arithmetic on a perimeter. Where a sample lands
   * on an exact pixel boundary a last-ulp difference in that coordinate flips
   * `floor` to the neighbouring pixel, which moves one sample of one bin by one
   * code value — and a bin is a mean over hundreds of samples, so it moves by
   * ~1e-6 and its band integral, which multiplies the same offset by the
   * window's 4.25 CSS px, by ~1e-4. That is a property of the instrument at a
   * measure-zero coincidence rather than of either implementation, so the bound
   * here is on its SIZE and its INCIDENCE, not on its absence. It costs the
   * native delta nothing: the bar and the delta are computed by this code, not
   * by the original, so any such offset is inside the bar it is measured
   * against.
   */
  const angularIncidence = angularReadings === 0 ? 1 : angularBeyond / angularReadings;
  if (!(contourWorst < 1e-9)) {
    say(`REFUSED: the contour port does not reproduce the recorded readings to 1e-9.`);
    process.exitCode = 1;
  }
  if (!(angularWorst < 1e-3) || angularIncidence > 0.01) {
    say(
      `REFUSED: the angular port disagrees by ${angularWorst.toExponential(3)} on ` +
        `${(angularIncidence * 100).toFixed(2)} % of readings, beyond the 1e-3 / 1 % a single ` +
        `boundary sample crossing a pixel edge can account for.`,
    );
    process.exitCode = 1;
  }
}

// ---------------------------------------------------------------------------

function main(): void {
  const argv = process.argv.slice(2);
  const mode = argv[0];
  const flag = (name: string): string | undefined => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 ? argv[i + 1] : undefined;
  };

  if (mode === "verify-readers") {
    verifyReaders();
    return;
  }
  if (mode === "bar") {
    const runs = flag("runs") ?? resolve(homedir(), "vitrea-w29-27-run");
    const out = flag("out");
    if (out === undefined) throw new Error("native-delta bar: --out <noise-bar.json> is required");
    buildBar(runs, resolve(out));
    return;
  }
  if (mode === "delta") {
    const barPath = flag("bar");
    const out = flag("out");
    if (barPath === undefined || out === undefined) {
      throw new Error("native-delta delta: --bar <noise-bar.json> and --out <dir> are required");
    }
    buildDelta(resolve(barPath), resolve(out));
    return;
  }
  if (mode === "tables") {
    const dir = flag("dir");
    if (dir === undefined) throw new Error("native-delta tables: --dir <results dir> is required");
    buildTables(resolve(dir), resolve(flag("bar") ?? resolve(dir, "noise-bar.json")));
    return;
  }
  if (mode === "sheets") {
    const dir = flag("dir");
    if (dir === undefined) throw new Error("native-delta sheets: --dir <results dir> is required");
    buildSheets(resolve(dir), Number(flag("gain") ?? 8), Number(flag("per-profile") ?? 4));
    return;
  }
  throw new Error("native-delta: one of verify-readers | bar | delta | tables | sheets");
}

try {
  main();
} catch (error) {
  process.stderr.write(`native-delta: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}
