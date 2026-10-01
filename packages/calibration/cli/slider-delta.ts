/**
 * `slider-delta` — Apple's own material at one position of the Glass slider, read against another.
 *
 *   npx tsx cli/slider-delta.ts delta  --bar <subject noise-bar.json> --reference-bar <reference noise-bar.json>
 *                                      --out <dir> [--subject-glass 0.25] [--reference-glass 0.5]
 *                                      [--only <subject profile key>]
 *   npx tsx cli/slider-delta.ts pairs  --list <pairs.json> --reference-bar <bar.json> [--bar <bar.json>]
 *                                      --out <file> [--subject-glass 0.25]
 *   npx tsx cli/slider-delta.ts sheets --dir <dir> [--gain 4] [--per-profile 4]
 *
 * W43 G2, charter clause 7 (`docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md`);
 * claims §5.200. The bar it judges against is declared in
 * `results/2026-10-02-w43-g2-reading/bar/bar-declaration.md` before the first pair is read.
 *
 * ## Why a command of its own, and what it shares with `native-delta`
 *
 * `native-delta` reads one operating system against another. Its rows name their sides
 * `profileKey27` and `profileKey26`, and its bar is one-sided: the 26.5 bed's run-to-run spread is
 * not derivable (§5.149 §6), so the bar is the 27 bed's alone. Here both sides are macOS 27 beds at
 * two slider positions, each with seven raw runs per cell, so the bar is TWO-sided and a row names
 * its sides by position. Writing that into `native-delta`'s rows would have put a 0.5 key in a field
 * called `profileKey26`.
 *
 * Everything that turns pixels into numbers is imported from the native delta and not restated:
 * `readCapture`, `pairMetrics`, the per-capture readings the recede is built from, and the cell
 * context (declared region, declared box, backdrop). The bar declaration's reason for porting the
 * rim readers applies unchanged: the bar and the delta must be the same function of a pair of
 * captures, or the bar does not bound the delta.
 *
 * ## The pair
 *
 * The reference side is the `-glass<reference>` fixture: its silhouette masks the material rows and
 * defines the SSIM depth windows, because it is the bed the shipped generation was fitted against.
 * Every signed reading is `[reference, subject]`, so `subject − reference` is Apple's change when the
 * slider moves from the reference position to the subject position.
 *
 * ## The bar, per cell and per metric
 *
 * Each side's bound is the native delta's three-level rule over that side's own bar file: the
 * cell's own pairwise max over its seven runs, else that bed's smallest non-zero pairwise max, else
 * exactly zero. The verdict bar is the LARGER of the two sides' bounds, and `barSource` names the
 * side and the level it came from. A metric neither side's bar file carries for the cell is not
 * judged and is said to be unbarred, never judged against something else's spread.
 *
 * ## The radial difference profile
 *
 * Beside the metrics, each row carries where the two captures differ, by band of signed distance
 * from the declared contour (`ComponentRegion.signedDistancePx`, in CSS px): the deep body, the
 * shoulder, the edge, the near exterior, the exterior and the far field. It needs no silhouette
 * and no reader, so it attributes a change to the body, the edge or the exterior without either
 * reader's relative-to-body construction. It is descriptive, never a verdict.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { srgbByteToLinear } from "../src/color";
import { createImage, type CalibrationImage } from "../src/index";
import {
  activeTwinOf,
  pairMetrics,
  poseOf,
  readCapture,
  sliderCounterpartKey,
  NATIVE_DELTA_METRICS,
  type MetricVector,
  type NativeDeltaMetric,
  type PairReadings,
} from "./native-delta-metrics";
import {
  amplifiedDifference,
  captureReadings,
  contextFor,
  encodedMeanOf,
  load,
  readJson,
  writeSheet,
  CAPTURE_READINGS,
  FIXTURES,
  REFERENCE,
  type BarCell,
  type BarFile,
  type CaptureReadingName,
  type CaptureReadingVector,
  type CellContext,
  type Manifest,
} from "./native-delta";
import { readSceneGeometry } from "./scene-geometry";

const say = (line: string): void => void process.stdout.write(`${line}\n`);

// ---------------------------------------------------------------------------
// The two-sided bar
// ---------------------------------------------------------------------------

export type BarLevel = "cell" | "bed-minimum" | "bed-zero";

export interface SideBound {
  readonly value: number;
  readonly level: BarLevel;
}

/** One side's bound on a pair metric: the native delta's three-level rule over that side's bar. */
export function metricBound(
  bar: Pick<BarFile, "bedMinimumNonZeroBar">,
  cell: Pick<BarCell, "pairwise"> | undefined,
  metric: NativeDeltaMetric,
): SideBound | undefined {
  const own = cell?.pairwise[metric]?.max;
  if (own === undefined) return undefined;
  if (own > 0) return { value: own, level: "cell" };
  const floor = bar.bedMinimumNonZeroBar[metric];
  return floor === undefined ? { value: 0, level: "bed-zero" } : { value: floor, level: "bed-minimum" };
}

/**
 * Per signed capture reading, the bed's smallest non-zero run-to-run spread — the recede's
 * fallback, derived from the bar file's own cells exactly as `native-delta delta` derives it.
 */
export function bedMinimumSpread(bar: Pick<BarFile, "cells">): Partial<Record<CaptureReadingName, number>> {
  const out: Partial<Record<CaptureReadingName, number>> = {};
  for (const cell of bar.cells) {
    for (const name of CAPTURE_READINGS) {
      const spread = cell.readingSpread[name];
      if (spread === undefined || spread <= 0) continue;
      const best = out[name];
      if (best === undefined || spread < best) out[name] = spread;
    }
  }
  return out;
}

/**
 * One side's bound on a recede reading: the two cells' spreads summed, each taking the bed's
 * smallest non-zero spread where its own seven runs agreed exactly (native delta, §5.151 §12).
 */
export function recedeBound(
  inactive: Pick<BarCell, "readingSpread"> | undefined,
  active: Pick<BarCell, "readingSpread"> | undefined,
  name: CaptureReadingName,
  floor: number | undefined,
): SideBound | undefined {
  if (inactive === undefined || active === undefined) return undefined;
  const i = inactive.readingSpread[name] ?? 0;
  const a = active.readingSpread[name] ?? 0;
  const value = (i > 0 ? i : (floor ?? 0)) + (a > 0 ? a : (floor ?? 0));
  const level: BarLevel = i > 0 && a > 0 ? "cell" : floor === undefined ? "bed-zero" : "bed-minimum";
  return { value, level };
}

/** The verdict bar: the larger of the two sides' bounds, and which side and level it came from. */
export function twoSided(
  subject: SideBound | undefined,
  reference: SideBound | undefined,
): { readonly value: number; readonly source: string } | undefined {
  if (subject === undefined && reference === undefined) return undefined;
  if (subject === undefined) return { value: reference!.value, source: `reference:${reference!.level}` };
  if (reference === undefined) return { value: subject.value, source: `subject:${subject.level}` };
  if (subject.value === reference.value) {
    return {
      value: subject.value,
      source: subject.level === reference.level ? `both:${subject.level}` : `both:${subject.level}/${reference.level}`,
    };
  }
  return subject.value > reference.value
    ? { value: subject.value, source: `subject:${subject.level}` }
    : { value: reference.value, source: `reference:${reference.level}` };
}

// ---------------------------------------------------------------------------
// The radial difference profile
// ---------------------------------------------------------------------------

/** Bands of signed distance from the declared contour, CSS px, negative inside. */
export const RADIAL_BANDS: readonly { readonly name: string; readonly from: number; readonly to: number }[] = [
  { name: "deep", from: Number.NEGATIVE_INFINITY, to: -6 },
  { name: "shoulder", from: -6, to: -2 },
  { name: "edge", from: -2, to: 0 },
  { name: "near-exterior", from: 0, to: 2 },
  { name: "exterior", from: 2, to: 12 },
  { name: "far", from: 12, to: Number.POSITIVE_INFINITY },
];

export interface RadialBand {
  readonly band: string;
  readonly pixels: number;
  /** Pixels where any of the three channels differs. */
  readonly differing: number;
  /** Mean over the band of subject − reference linear luminance (Rec.709 on linearised sRGB). */
  readonly meanSignedLuminance: number;
  /** Mean over the band's pixels and channels of |subject − reference| in codes. */
  readonly meanAbsCode: number;
  readonly maxAbsCode: number;
}

const luminanceOf = (data: ArrayLike<number>, at: number): number =>
  0.2126 * srgbByteToLinear(data[at] ?? 0) +
  0.7152 * srgbByteToLinear(data[at + 1] ?? 0) +
  0.0722 * srgbByteToLinear(data[at + 2] ?? 0);

/** Where two captures of one cell differ, by distance from the declared contour. */
export function radialProfile(
  reference: CalibrationImage,
  subject: CalibrationImage,
  signedDistancePx: Float64Array,
  scale: number,
): readonly RadialBand[] {
  const out: RadialBand[] = [];
  const count = reference.width * reference.height;
  const sums = RADIAL_BANDS.map(() => ({ pixels: 0, differing: 0, luminance: 0, abs: 0, max: 0 }));
  for (let i = 0; i < count; i += 1) {
    const css = (signedDistancePx[i] ?? 0) / scale;
    const index = RADIAL_BANDS.findIndex((band) => css > band.from && css <= band.to);
    const sum = sums[index];
    if (sum === undefined) continue;
    const at = i * 4;
    let differs = false;
    let abs = 0;
    for (let c = 0; c < 3; c += 1) {
      const delta = Math.abs((subject.data[at + c] ?? 0) - (reference.data[at + c] ?? 0));
      if (delta > 0) differs = true;
      abs += delta;
      if (delta > sum.max) sum.max = delta;
    }
    sum.pixels += 1;
    if (differs) sum.differing += 1;
    sum.abs += abs / 3;
    sum.luminance += luminanceOf(subject.data, at) - luminanceOf(reference.data, at);
  }
  RADIAL_BANDS.forEach((band, index) => {
    const sum = sums[index];
    if (sum === undefined || sum.pixels === 0) return;
    out.push({
      band: band.name,
      pixels: sum.pixels,
      differing: sum.differing,
      meanSignedLuminance: sum.luminance / sum.pixels,
      meanAbsCode: sum.abs / sum.pixels,
      maxAbsCode: sum.max,
    });
  });
  return out;
}

// ---------------------------------------------------------------------------
// One pair, measured and judged
// ---------------------------------------------------------------------------

export interface SliderDeltaRow {
  /** The subject position's key (e.g. `-glass0.25`). */
  readonly profileKey: string;
  /** The reference position's key (e.g. `-glass0.5`); its fixture is the reference side. */
  readonly counterpartProfileKey: string;
  readonly sceneId: string;
  readonly label?: string;
  readonly pose: "active" | "inactive";
  readonly fixtureSet: string;
  readonly background: string;
  readonly component: string;
  readonly backdropEncodedMean: number;
  readonly scale: number;
  readonly metrics: MetricVector;
  readonly bar: Readonly<Partial<Record<NativeDeltaMetric, number>>>;
  readonly barSides: Readonly<
    Partial<Record<NativeDeltaMetric, { readonly subject: number | null; readonly reference: number | null }>>
  >;
  readonly barSource: Readonly<Partial<Record<NativeDeltaMetric, string>>>;
  readonly moved: Readonly<Partial<Record<NativeDeltaMetric, boolean>>>;
  /** `[reference, subject]`, so `subject − reference` is Apple's change. */
  readonly readings: PairReadings;
  /** Each capture under its OWN silhouette and declared box, the readings the recede is built from. */
  readonly captureReadings: { readonly reference: CaptureReadingVector; readonly subject: CaptureReadingVector };
  readonly radial: readonly RadialBand[];
  readonly notes: readonly string[];
}

interface Bed {
  readonly manifest: Manifest;
  readonly spec: {
    readonly scenes: readonly { readonly id: string; readonly background: string; readonly component: string }[];
  };
  readonly geometry: ReturnType<typeof readSceneGeometry>;
  readonly backgrounds: Map<string, CalibrationImage>;
  readonly encodedMeans: Map<string, number>;
  readonly fileOf: Map<string, { readonly file: string; readonly fixtureSet: string }>;
}

function openBed(): Bed {
  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  const fileOf = new Map<string, { readonly file: string; readonly fixtureSet: string }>();
  for (const profile of manifest.profiles) {
    for (const fixture of profile.fixtures) {
      fileOf.set(`${profile.profileKey} ${fixture.sceneId}`, { file: fixture.file, fixtureSet: fixture.fixtureSet });
    }
  }
  return {
    manifest,
    spec: readJson(resolve(REFERENCE, "scenes.json")),
    geometry: readSceneGeometry(REFERENCE),
    backgrounds: new Map(),
    encodedMeans: new Map(),
    fileOf,
  };
}

interface Bars {
  readonly subject: BarFile | undefined;
  readonly reference: BarFile;
  readonly subjectCells: Map<string, BarCell>;
  readonly referenceCells: Map<string, BarCell>;
}

function indexBars(subject: BarFile | undefined, reference: BarFile): Bars {
  const cells = (bar: BarFile | undefined): Map<string, BarCell> => {
    const out = new Map<string, BarCell>();
    for (const cell of bar?.cells ?? []) out.set(`${cell.profileKey} ${cell.sceneId}`, cell);
    return out;
  };
  return { subject, reference, subjectCells: cells(subject), referenceCells: cells(reference) };
}

function measure(
  bed: Bed,
  bars: Bars,
  subjectImage: CalibrationImage,
  subjectKey: string,
  referenceKey: string,
  sceneId: string,
  label: string | undefined,
): { readonly row: SliderDeltaRow; readonly context: CellContext } {
  const referenceFile = bed.fileOf.get(`${referenceKey} ${sceneId}`);
  if (referenceFile === undefined) throw new Error(`slider-delta: no fixture ${referenceKey}/${sceneId}`);
  const referenceImage = load(resolve(FIXTURES, referenceFile.file));
  if (referenceImage.width !== subjectImage.width || referenceImage.height !== subjectImage.height) {
    throw new Error(`slider-delta: ${sceneId} differs in size between ${subjectKey} and ${referenceKey}`);
  }
  const context = contextFor(
    sceneId,
    referenceKey,
    bed.manifest,
    bed.spec,
    bed.geometry,
    referenceImage.width,
    referenceImage.height,
    bed.backgrounds,
  );
  if (context === null) throw new Error(`slider-delta: no backdrop or scale on record for ${sceneId}`);

  const referenceReading = readCapture(referenceImage, context.background, context.geometry);
  const subjectReading = readCapture(subjectImage, context.background, context.geometry);
  const result = pairMetrics(referenceReading, subjectReading, context.background, context.geometry);

  const subjectCell = bars.subjectCells.get(`${subjectKey} ${sceneId}`);
  const referenceCell = bars.referenceCells.get(`${referenceKey} ${sceneId}`);
  const bar: Partial<Record<NativeDeltaMetric, number>> = {};
  const barSides: Partial<Record<NativeDeltaMetric, { subject: number | null; reference: number | null }>> = {};
  const barSource: Partial<Record<NativeDeltaMetric, string>> = {};
  const moved: Partial<Record<NativeDeltaMetric, boolean>> = {};
  for (const metric of NATIVE_DELTA_METRICS) {
    const value = result.metrics[metric];
    if (value === null || !Number.isFinite(value)) continue;
    const subject = bars.subject === undefined ? undefined : metricBound(bars.subject, subjectCell, metric);
    const reference = metricBound(bars.reference, referenceCell, metric);
    const verdict = twoSided(subject, reference);
    if (verdict === undefined) continue;
    bar[metric] = verdict.value;
    barSides[metric] = { subject: subject?.value ?? null, reference: reference?.value ?? null };
    barSource[metric] = verdict.source;
    moved[metric] = value > verdict.value;
  }

  let encodedMean = bed.encodedMeans.get(context.backgroundId);
  if (encodedMean === undefined) {
    encodedMean = encodedMeanOf(context.background);
    bed.encodedMeans.set(context.backgroundId, encodedMean);
  }
  const scene = bed.spec.scenes.find((entry) => entry.id === sceneId);
  return {
    context,
    row: {
      profileKey: subjectKey,
      counterpartProfileKey: referenceKey,
      sceneId,
      ...(label === undefined ? {} : { label }),
      pose: poseOf(sceneId),
      fixtureSet: referenceFile.fixtureSet,
      background: scene?.background ?? "?",
      component: scene?.component ?? "?",
      backdropEncodedMean: encodedMean,
      scale: context.scale,
      metrics: result.metrics,
      bar,
      barSides,
      barSource,
      moved,
      readings: result.readings,
      captureReadings: {
        reference: captureReadings(referenceImage, referenceReading, context),
        subject: captureReadings(subjectImage, subjectReading, context),
      },
      radial: radialProfile(referenceImage, subjectImage, context.geometry.region.signedDistancePx, context.scale),
      notes: result.notes,
    },
  };
}

// ---------------------------------------------------------------------------
// The delta over a whole position
// ---------------------------------------------------------------------------

interface SliderRecedeRow {
  readonly profileKey: string;
  readonly counterpartProfileKey: string;
  readonly activeSceneId: string;
  readonly inactiveSceneId: string;
  readonly scale: number;
  readonly fixtureSet: string;
  readonly recedeSubject: Readonly<Partial<Record<CaptureReadingName, number>>>;
  readonly recedeReference: Readonly<Partial<Record<CaptureReadingName, number>>>;
  /** (subject inactive − subject active) − (reference inactive − reference active). */
  readonly deltaOfRecede: Readonly<Partial<Record<CaptureReadingName, number>>>;
  readonly bar: Readonly<Partial<Record<CaptureReadingName, number>>>;
  readonly barSource: Readonly<Partial<Record<CaptureReadingName, string>>>;
  readonly moved: Readonly<Partial<Record<CaptureReadingName, boolean>>>;
}

function buildDelta(
  subjectBarPath: string,
  referenceBarPath: string,
  outDir: string,
  subjectGlass: string,
  referenceGlass: string,
  only: string | undefined,
): void {
  const bed = openBed();
  const subjectBar = readJson<BarFile>(subjectBarPath);
  const referenceBar = readJson<BarFile>(referenceBarPath);
  const bars = indexBars(subjectBar, referenceBar);

  const suffix = `-glass${subjectGlass}`;
  const profiles = bed.manifest.profiles.filter(
    (profile) =>
      profile.profileKey.startsWith("apple-macos-27.0-")
      && profile.profileKey.endsWith(suffix)
      && (only === undefined || profile.profileKey === only),
  );
  if (profiles.length === 0) throw new Error(`slider-delta: no published profile at glass${subjectGlass}`);

  const rows: SliderDeltaRow[] = [];
  const onlyOnSubject: string[] = [];
  const unbarred: string[] = [];
  const total = profiles.reduce((sum, profile) => sum + profile.fixtures.length, 0);
  let done = 0;
  for (const profile of profiles) {
    const referenceKey = sliderCounterpartKey(profile.profileKey, referenceGlass);
    for (const fixture of profile.fixtures) {
      done += 1;
      if (done % 50 === 0) say(`  ${String(done)} / ${String(total)} cells read`);
      if (!bed.fileOf.has(`${referenceKey} ${fixture.sceneId}`)) {
        onlyOnSubject.push(`${profile.profileKey}/${fixture.sceneId}`);
        continue;
      }
      if (
        !bars.subjectCells.has(`${profile.profileKey} ${fixture.sceneId}`)
        || !bars.referenceCells.has(`${referenceKey} ${fixture.sceneId}`)
      ) {
        unbarred.push(`${profile.profileKey}/${fixture.sceneId}`);
      }
      const subjectImage = load(resolve(FIXTURES, fixture.file));
      const { row } = measure(bed, bars, subjectImage, profile.profileKey, referenceKey, fixture.sceneId, undefined);
      rows.push(row);
    }
  }

  // The recede, as its own row set, so the slider's change and the recede are never read as each
  // other: (subject inactive − subject active) − (reference inactive − reference active).
  const subjectFloor = bedMinimumSpread(subjectBar);
  const referenceFloor = bedMinimumSpread(referenceBar);
  const byCell = new Map(rows.map((row) => [`${row.profileKey} ${row.sceneId}`, row]));
  const recedeRows: SliderRecedeRow[] = [];
  for (const row of rows) {
    const activeId = activeTwinOf(row.sceneId);
    if (activeId === null) continue;
    const active = byCell.get(`${row.profileKey} ${activeId}`);
    if (active === undefined) continue;
    const recedeSubject: Partial<Record<CaptureReadingName, number>> = {};
    const recedeReference: Partial<Record<CaptureReadingName, number>> = {};
    const deltaOfRecede: Partial<Record<CaptureReadingName, number>> = {};
    const bar: Partial<Record<CaptureReadingName, number>> = {};
    const barSource: Partial<Record<CaptureReadingName, string>> = {};
    const moved: Partial<Record<CaptureReadingName, boolean>> = {};
    for (const name of CAPTURE_READINGS) {
      const iS = row.captureReadings.subject[name];
      const aS = active.captureReadings.subject[name];
      const iR = row.captureReadings.reference[name];
      const aR = active.captureReadings.reference[name];
      if (iS === null || aS === null || iR === null || aR === null) continue;
      recedeSubject[name] = iS - aS;
      recedeReference[name] = iR - aR;
      const difference = iS - aS - (iR - aR);
      deltaOfRecede[name] = difference;
      const verdict = twoSided(
        recedeBound(
          bars.subjectCells.get(`${row.profileKey} ${row.sceneId}`),
          bars.subjectCells.get(`${row.profileKey} ${activeId}`),
          name,
          subjectFloor[name],
        ),
        recedeBound(
          bars.referenceCells.get(`${row.counterpartProfileKey} ${row.sceneId}`),
          bars.referenceCells.get(`${row.counterpartProfileKey} ${activeId}`),
          name,
          referenceFloor[name],
        ),
      );
      if (verdict === undefined) continue;
      bar[name] = verdict.value;
      barSource[name] = verdict.source;
      moved[name] = Math.abs(difference) > verdict.value;
    }
    recedeRows.push({
      profileKey: row.profileKey,
      counterpartProfileKey: row.counterpartProfileKey,
      activeSceneId: activeId,
      inactiveSceneId: row.sceneId,
      scale: row.scale,
      fixtureSet: row.fixtureSet,
      recedeSubject,
      recedeReference,
      deltaOfRecede,
      bar,
      barSource,
      moved,
    });
  }

  mkdirSync(outDir, { recursive: true });
  const pairing = {
    subjectGlass,
    referenceGlass,
    reference:
      `the glass${referenceGlass} fixture is the reference side of every pair: its silhouette masks ` +
      `the material rows, and every signed reading is [glass${referenceGlass}, glass${subjectGlass}]`,
    bar:
      "per cell and metric, the LARGER of the two sides' three-level bounds (the cell's own " +
      "pairwise max over its seven runs, else that bed's smallest non-zero pairwise max, else zero); " +
      "moved means the pair's value exceeds it",
  };
  writeFileSync(
    resolve(outDir, "slider-delta.json"),
    `${JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        pairing,
        subjectBarFile: subjectBarPath,
        referenceBarFile: referenceBarPath,
        metrics: NATIVE_DELTA_METRICS,
        captureReadings: CAPTURE_READINGS,
        radialBands: RADIAL_BANDS.map((band) => ({ ...band, from: String(band.from), to: String(band.to) })),
        onlyOnSubject,
        unbarred,
        rows,
      },
      null,
      1,
    )}\n`,
  );
  writeFileSync(
    resolve(outDir, "slider-recede-delta.json"),
    `${JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        pairing,
        construction:
          `(glass${subjectGlass} inactive − glass${subjectGlass} active) − (glass${referenceGlass} ` +
          `inactive − glass${referenceGlass} active), per signed capture reading. Each side's bar is ` +
          "the sum of its two cells' run-to-run spreads with the native delta's bed-minimum fallback; " +
          "the verdict bar is the larger side's.",
        readings: CAPTURE_READINGS,
        rows: recedeRows,
      },
      null,
      1,
    )}\n`,
  );
  say(
    `slider-delta: ${String(rows.length)} pair rows, ${String(recedeRows.length)} recede rows, ` +
      `${String(onlyOnSubject.length)} cells only at glass${subjectGlass}, ${String(unbarred.length)} cells with no bar`,
  );
}

// ---------------------------------------------------------------------------
// Arbitrary pairs against the same bar: the null rehearsal
// ---------------------------------------------------------------------------

interface PairSpec {
  readonly label: string;
  readonly subjectImage: string;
  /** The reference fixture's profile key. */
  readonly profileKey: string;
  readonly sceneId: string;
}

/**
 * Pairs that are not a slider pair — a 0.5 capture through another bundle against its 0.5 fixture —
 * measured by the same function and judged by the bar the delta would give that cell. This is how a
 * declared bar is rehearsed on a known null before any real pair is read.
 */
function buildPairs(
  listPath: string,
  referenceBarPath: string,
  subjectBarPath: string | undefined,
  subjectGlass: string,
  outPath: string,
): void {
  const bed = openBed();
  const bars = indexBars(
    subjectBarPath === undefined ? undefined : readJson<BarFile>(subjectBarPath),
    readJson<BarFile>(referenceBarPath),
  );
  const list = readJson<readonly PairSpec[]>(listPath);
  const rows: SliderDeltaRow[] = [];
  for (const spec of list) {
    const subjectKey = sliderCounterpartKey(spec.profileKey, subjectGlass);
    const { row } = measure(bed, bars, load(spec.subjectImage), subjectKey, spec.profileKey, spec.sceneId, spec.label);
    rows.push(row);
  }
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(
    outPath,
    `${JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        list: listPath,
        referenceBarFile: referenceBarPath,
        subjectBarFile: subjectBarPath ?? null,
        subjectGlassForBarLookup: subjectGlass,
        metrics: NATIVE_DELTA_METRICS,
        rows,
      },
      null,
      1,
    )}\n`,
  );
  say(`slider-delta pairs: ${String(rows.length)} rows written to ${outPath}`);
}

// ---------------------------------------------------------------------------
// Sheets: reference | subject | difference, for the eye
// ---------------------------------------------------------------------------

/** Where any channel differs, white on black: the shape of the change at any amplitude. */
function whereDiffers(a: CalibrationImage, b: CalibrationImage): CalibrationImage {
  const count = a.width * a.height;
  const data = new Uint8Array(count * 4);
  for (let i = 0; i < count; i += 1) {
    const at = i * 4;
    const differs =
      a.data[at] !== b.data[at] || a.data[at + 1] !== b.data[at + 1] || a.data[at + 2] !== b.data[at + 2];
    const value = differs ? 255 : 0;
    data[at] = value;
    data[at + 1] = value;
    data[at + 2] = value;
    data[at + 3] = 255;
  }
  return createImage(a.width, a.height, data);
}

const escapeHtml = (text: string): string =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function buildSheets(dir: string, gain: number, perProfile: number): void {
  const delta = readJson<{
    readonly pairing: { readonly subjectGlass: string; readonly referenceGlass: string };
    readonly rows: readonly SliderDeltaRow[];
  }>(resolve(dir, "slider-delta.json"));
  const bed = openBed();
  const sheetDir = resolve(dir, "sheets");
  const { subjectGlass, referenceGlass } = delta.pairing;
  const byProfile = new Map<string, SliderDeltaRow[]>();
  for (const row of delta.rows) {
    const list = byProfile.get(row.profileKey) ?? [];
    list.push(row);
    byProfile.set(row.profileKey, list);
  }
  const short = (key: string): string => key.replace("apple-macos-27.0-", "").replace(/-glass[\d.]+$/, "");
  const index: string[] = [];
  for (const [profileKey, rows] of [...byProfile.entries()].sort()) {
    const name = short(profileKey);
    const pageDir = resolve(sheetDir, name);
    mkdirSync(resolve(pageDir, "diff"), { recursive: true });
    mkdirSync(resolve(pageDir, "where"), { recursive: true });
    const ordered = [...rows].sort(
      (x, y) =>
        x.background.localeCompare(y.background)
        || x.component.localeCompare(y.component)
        || x.sceneId.localeCompare(y.sceneId),
    );
    const lines: string[] = [];
    lines.push("<!doctype html><meta charset=utf-8>");
    lines.push(`<title>${escapeHtml(name)}: glass${referenceGlass} | glass${subjectGlass} | difference</title>`);
    lines.push(
      "<style>body{background:#181818;color:#ddd;font:12px -apple-system,sans-serif;margin:16px}" +
        "td{vertical-align:top;padding:4px}img{display:block;image-rendering:pixelated}" +
        "tr:nth-child(even){background:#202020}th{text-align:left;color:#aaa}</style>",
    );
    lines.push(
      `<h1>${escapeHtml(profileKey.replace(/-glass[\d.]+$/, ""))}: Apple at glass${referenceGlass} | at ` +
        `glass${subjectGlass} | |difference| ×${String(gain)} | where any channel differs</h1>`,
    );
    lines.push(
      "<p>Native fixtures only; no vitrea render. The difference column is |glass" +
        `${subjectGlass} − glass${referenceGlass}| per channel times ${String(gain)}, clamped. The last ` +
        "column is white wherever any channel differs at all. W43 G2, charter clause 7; claims §5.200.</p>",
    );
    lines.push("<table><tr><th>cell</th><th>glass" + referenceGlass + "</th><th>glass" + subjectGlass +
      "</th><th>|Δ| ×" + String(gain) + "</th><th>differs</th></tr>");
    for (const row of ordered) {
      const referenceFile = bed.fileOf.get(`${row.counterpartProfileKey} ${row.sceneId}`)?.file;
      const subjectFile = bed.fileOf.get(`${row.profileKey} ${row.sceneId}`)?.file;
      if (referenceFile === undefined || subjectFile === undefined) continue;
      const referencePath = resolve(FIXTURES, referenceFile);
      const subjectPath = resolve(FIXTURES, subjectFile);
      const reference = load(referencePath);
      const subject = load(subjectPath);
      const diffName = `diff/${row.sceneId}__x${String(gain)}.png`;
      const whereName = `where/${row.sceneId}.png`;
      writeSheet(resolve(pageDir, diffName), [amplifiedDifference(subject, reference, gain)]);
      writeSheet(resolve(pageDir, whereName), [whereDiffers(subject, reference)]);
      const body = row.captureReadings;
      const level = (vector: CaptureReadingVector): string =>
        vector.bodyLevel === null ? "—" : vector.bodyLevel.toFixed(4);
      const width = reference.width / row.scale;
      const cell = (src: string): string => `<td><img src="${escapeHtml(src)}" width="${String(width)}"></td>`;
      lines.push(
        `<tr><td><b>${escapeHtml(row.sceneId)}</b><br>${escapeHtml(row.fixtureSet)}<br>` +
          `body ${level(body.reference)} → ${level(body.subject)}<br>` +
          `ΔE mean ${(row.metrics.oklabDeltaEMean ?? NaN).toFixed(4)}</td>` +
          cell(relative(pageDir, referencePath)) +
          cell(relative(pageDir, subjectPath)) +
          cell(diffName) +
          cell(whereName) +
          "</tr>",
      );
    }
    lines.push("</table>");
    writeFileSync(resolve(pageDir, "index.html"), `${lines.join("\n")}\n`);
    index.push(`<li><a href="${name}/index.html">${escapeHtml(name)}</a> (${String(rows.length)} cells)</li>`);

    // A few full-resolution triptychs per profile, as W29 G2's sheets were: the cells whose
    // whole-cell ΔE moved most, so a sheet can be cited from the ledger without the page.
    const ranked = [...rows].sort((x, y) => (y.metrics.oklabDeltaEMean ?? 0) - (x.metrics.oklabDeltaEMean ?? 0));
    ranked.slice(0, perProfile).forEach((row, rank) => {
      const referenceFile = bed.fileOf.get(`${row.counterpartProfileKey} ${row.sceneId}`)?.file;
      const subjectFile = bed.fileOf.get(`${row.profileKey} ${row.sceneId}`)?.file;
      if (referenceFile === undefined || subjectFile === undefined) return;
      const reference = load(resolve(FIXTURES, referenceFile));
      const subject = load(resolve(FIXTURES, subjectFile));
      writeSheet(
        resolve(sheetDir, `profile__${name}__${String(rank + 1).padStart(2, "0")}__${row.sceneId}__x${String(gain)}.png`),
        [reference, subject, amplifiedDifference(subject, reference, gain)],
      );
    });
  }
  writeFileSync(
    resolve(sheetDir, "index.html"),
    `<!doctype html><meta charset=utf-8><title>W43 G2 sheets</title><h1>Apple at glass${referenceGlass} against ` +
      `glass${subjectGlass}, per profile</h1><ul>\n${index.join("\n")}\n</ul>\n`,
  );
  say(`slider-delta sheets: written under ${sheetDir}`);
}

// ---------------------------------------------------------------------------

function main(): void {
  const argv = process.argv.slice(2);
  const mode = argv[0];
  const flag = (name: string): string | undefined => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const subjectGlass = flag("subject-glass") ?? "0.25";
  const referenceGlass = flag("reference-glass") ?? "0.5";
  if (mode === "delta") {
    const bar = flag("bar");
    const referenceBar = flag("reference-bar");
    const out = flag("out");
    if (bar === undefined || referenceBar === undefined || out === undefined) {
      throw new Error("slider-delta delta: --bar, --reference-bar and --out are required");
    }
    buildDelta(resolve(bar), resolve(referenceBar), resolve(out), subjectGlass, referenceGlass, flag("only"));
    return;
  }
  if (mode === "pairs") {
    const list = flag("list");
    const referenceBar = flag("reference-bar");
    const out = flag("out");
    if (list === undefined || referenceBar === undefined || out === undefined) {
      throw new Error("slider-delta pairs: --list, --reference-bar and --out are required");
    }
    const bar = flag("bar");
    buildPairs(resolve(list), resolve(referenceBar), bar === undefined ? undefined : resolve(bar), subjectGlass, resolve(out));
    return;
  }
  if (mode === "sheets") {
    const dir = flag("dir");
    if (dir === undefined) throw new Error("slider-delta sheets: --dir <results dir> is required");
    buildSheets(resolve(dir), Number(flag("gain") ?? 4), Number(flag("per-profile") ?? 4));
    return;
  }
  throw new Error("slider-delta: one of delta | pairs | sheets");
}

const invokedAsScript =
  process.argv[1] !== undefined && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invokedAsScript) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`slider-delta: ${error instanceof Error ? error.message : String(error)}\n`);
    process.exit(1);
  }
}

