/**
 * X9's result side: what a measurement is *about*, and where measurements live.
 *
 * X9's rule is that fixtures version the native capture but **results version
 * the whole render cell** — native profile × web cell × scene. That is not
 * bookkeeping pedantry. The same web build measured on two GPU adapter classes,
 * or through two capture paths, produces genuinely different pixels, and a
 * result matrix keyed only by scene would silently overwrite one with the
 * other. Every claim in the spec is required to cite its cell, and this is the
 * structure that makes citing it the path of least resistance.
 *
 * Two things this module deliberately does not have:
 *
 *   - **No thresholds, and no verdicts.** Every leaf is a `MetricValue`: a
 *     number and its unit. Deciding which numbers are good enough is C9's, per
 *     tier and per engine cell; a `pass: boolean` here would be C7 tuning
 *     against its own fixtures, which is the exact failure the
 *     calibration/validation/holdout split exists to prevent.
 *   - **No aggregate score.** There is no single fidelity number, because a
 *     shape win must never be able to mask a material loss (§Calibration).
 */

import { CalibrationError } from "./errors";
import type { ContourDistanceReport, CornerCurvatureReport } from "./metrics/shape";
import type {
  EdgeSpreadReport,
  InteriorLevelReport,
  LuminanceTransferReport,
  RimIntensityReport,
  ShadowFalloffReport,
  TintResponseReport,
} from "./metrics/material";
import type { MorphSilhouetteTrajectoryReport } from "./metrics/motion";
import type { EdgeWeightedDifferenceReport, OklabDeltaEReport, SsimReport } from "./metrics/perceptual";
import { parseProfileKey, type FidelityTier, type FixtureSet } from "./profile";

// ---------------------------------------------------------------------------
// Metric values
// ---------------------------------------------------------------------------

/**
 * The units this package reports in. A closed set, so a report cannot carry a
 * number whose meaning is only in a comment somewhere.
 */
export const METRIC_UNITS = ["ratio", "px", "px^2", "1/px", "luminance", "oklab", "ms", "degrees", "px/ms"] as const;

export type MetricUnits = (typeof METRIC_UNITS)[number];

/** A measured number and what it is measured in. Never a verdict. */
export interface MetricValue {
  readonly value: number;
  readonly units: MetricUnits;
}

export function metricValue(value: number, units: MetricUnits): MetricValue {
  return { value, units };
}

// ---------------------------------------------------------------------------
// Cell keying
// ---------------------------------------------------------------------------

/**
 * The web half of a result cell, exactly as X9 enumerates it.
 *
 * `engine`, `samplingBackend` and `gpuAdapter` are free-form strings rather
 * than unions on purpose: they name things outside this repo's control (a new
 * browser, a new backdrop-sampling route, an adapter class nobody has seen),
 * and a union here would mean a schema change every time the world adds one,
 * with old committed results failing to parse. `renderer` and `colorSpace` are
 * closed, because those are vitrea's own decisions — and `colorSpace` is closed
 * to a single value by X5's v1 lock, which is a statement worth having the type
 * system carry.
 */
export interface WebCell {
  /** Browser engine identity, e.g. "chromium", "gecko", "webkit". */
  readonly engine: string;
  readonly engineVersion: string;
  /** Which tier actually drew: vitrea's shader math, or the engine's blur. */
  readonly renderer: "webgpu" | "css";
  /** How the backdrop reached the effect, e.g. "element-capture", "dom-hybrid". */
  readonly samplingBackend: string;
  /** Adapter class, not a serial number, e.g. "apple-m-series", "software". */
  readonly gpuAdapter: string;
  /** X5: sRGB is the locked v1 calibration space. */
  readonly colorSpace: "srgb";
  /** How the pixels were obtained, e.g. "playwright-screenshot", "screencapture". */
  readonly capturePath: string;
}

/** Native profile × web cell × scene: what one row of results is about. */
export interface ResultCellKey {
  /** A key matching X9's grammar — see `PROFILE_KEY_PATTERN`. */
  readonly profileKey: string;
  readonly web: WebCell;
  /** Canonical scene identity, e.g. "impulse-dark-toolbar-rest-medium". */
  readonly sceneId: string;
}

/**
 * Build a cell key, refusing a profile string the X9 grammar does not accept.
 *
 * The check is here rather than at serialisation because a bad profile key is a
 * harness configuration mistake, and the cheapest place to find it is the first
 * time a result is created — not months later when a committed matrix turns out
 * to be keyed on a typo.
 */
export function resultCellKey(profileKey: string, web: WebCell, sceneId: string): ResultCellKey {
  if (!parseProfileKey(profileKey)) {
    throw new CalibrationError(
      "invalid-profile-key",
      `resultCellKey: "${profileKey}" is not a profile key. Expected the X9 grammar, ` +
        `e.g. apple-macos-26.5-2x-light-standard.`,
    );
  }
  return { profileKey, web, sceneId };
}

/**
 * `|` separates fields and `%` escapes, so no field's content can forge a
 * separator and make two different cells collide on one key.
 */
function escapeField(value: string): string {
  return value.replace(/%/g, "%25").replace(/\|/g, "%7C");
}

/**
 * Serialise a cell key to a stable string.
 *
 * Stable in both senses that matter: the same key always produces the same
 * string (fields in a fixed order, nothing derived from object property
 * ordering or a clock), and different keys always produce different strings
 * (every field escaped). The result is the identity a result matrix is indexed
 * by and the string a fidelity claim quotes, so it has to be both.
 */
export function serializeResultCellKey(key: ResultCellKey): string {
  return [
    key.profileKey,
    key.sceneId,
    key.web.engine,
    key.web.engineVersion,
    key.web.renderer,
    key.web.samplingBackend,
    key.web.gpuAdapter,
    key.web.colorSpace,
    key.web.capturePath,
  ]
    .map(escapeField)
    .join("|");
}

// ---------------------------------------------------------------------------
// Axis reports
// ---------------------------------------------------------------------------

export interface ShapeAxisReport {
  readonly axis: "shape";
  readonly silhouetteIoU: MetricValue;
  readonly contourDistanceMax: MetricValue;
  readonly contourDistanceP95: MetricValue;
  readonly contourDistanceMean: MetricValue;
  readonly contourDistanceRms: MetricValue;
  readonly cornerCurvatureMaxDelta: MetricValue;
  readonly cornerCurvatureP95Delta: MetricValue;
  /** Characteristic corner curvature of each side — the corner tightness. */
  readonly cornerCurvatureNative: MetricValue;
  readonly cornerCurvatureWeb: MetricValue;
}

export function shapeAxisReport(input: {
  readonly silhouetteIoU: number;
  readonly contourDistance: ContourDistanceReport;
  readonly cornerCurvature: CornerCurvatureReport;
}): ShapeAxisReport {
  return {
    axis: "shape",
    silhouetteIoU: metricValue(input.silhouetteIoU, "ratio"),
    contourDistanceMax: metricValue(input.contourDistance.maxPx, "px"),
    contourDistanceP95: metricValue(input.contourDistance.p95Px, "px"),
    contourDistanceMean: metricValue(input.contourDistance.meanPx, "px"),
    contourDistanceRms: metricValue(input.contourDistance.rmsPx, "px"),
    cornerCurvatureMaxDelta: metricValue(input.cornerCurvature.cornerMaxDeltaPerPx, "1/px"),
    cornerCurvatureP95Delta: metricValue(input.cornerCurvature.cornerP95DeltaPerPx, "1/px"),
    cornerCurvatureNative: metricValue(input.cornerCurvature.cornerCurvaturePerPxA, "1/px"),
    cornerCurvatureWeb: metricValue(input.cornerCurvature.cornerCurvaturePerPxB, "1/px"),
  };
}

/**
 * The material axis, reported **per side wherever a side exists**.
 *
 * Every sub-metric that describes one image — the blur width, the rim, the
 * exterior shadow, the interior level and spread — carries a `Native` and a
 * `Web` figure measured by the same estimator over the same mask. C7 shipped the
 * blur, rim and shadow figures for the web side alone, which was enough to
 * describe vitrea's own material and not enough to tune it: a target needs a
 * number on the reference side too, and "the gap" is not a quantity until both
 * halves are measured the same way.
 *
 * The comparative sub-metrics (`tint*`, and the `luminance*` pair) keep their
 * existing shape, since those estimators were already two-sided.
 *
 * Optional fields mean **not identifiable on this scene**, never zero:
 *
 *   - `luminance*` is absent on a solid-colour backdrop, where no slope exists
 *     to fit (`tryLinearFit` refuses a constant regressor by design).
 *   - `blur*` is absent where the backdrop supplies no single resolvable step
 *     edge inside the silhouette.
 *
 * `interiorMean*` and `interiorStdDev*` are the two that are always defined, on
 * every scene and both sides, which is why they carry the frosting comparison
 * that the blur fit cannot on this fixture set.
 */
export interface MaterialAxisReport {
  readonly axis: "material";
  /** Gaussian-equivalent σ of the backdrop step seen through each side. */
  readonly blurSigmaNative?: MetricValue;
  readonly blurSigmaWeb?: MetricValue;
  /** Fit residual as a fraction of the step height. Large means σ is not identifiable. */
  readonly blurFitResidualNative?: MetricValue;
  readonly blurFitResidualWeb?: MetricValue;
  readonly luminanceSlopeNative?: MetricValue;
  readonly luminanceSlopeWeb?: MetricValue;
  readonly luminanceOffsetNative?: MetricValue;
  readonly luminanceOffsetWeb?: MetricValue;
  readonly luminanceR2Native?: MetricValue;
  readonly luminanceR2Web?: MetricValue;
  /** Interior level and spread, linear light, over the shared mask. Always present. */
  readonly interiorMeanNative: MetricValue;
  readonly interiorMeanWeb: MetricValue;
  readonly interiorMeanBackdrop: MetricValue;
  readonly interiorStdDevNative: MetricValue;
  readonly interiorStdDevWeb: MetricValue;
  readonly interiorStdDevBackdrop: MetricValue;
  readonly tintDeltaLNative: MetricValue;
  readonly tintDeltaLWeb: MetricValue;
  readonly tintDeltaANative: MetricValue;
  readonly tintDeltaAWeb: MetricValue;
  readonly tintDeltaBNative: MetricValue;
  readonly tintDeltaBWeb: MetricValue;
  readonly tintChromaDeltaNative: MetricValue;
  readonly tintChromaDeltaWeb: MetricValue;
  readonly tintHueShiftNative: MetricValue;
  readonly tintHueShiftWeb: MetricValue;
  readonly rimPeakLuminanceNative: MetricValue;
  readonly rimPeakLuminanceWeb: MetricValue;
  readonly rimPeakDistanceNative: MetricValue;
  readonly rimPeakDistanceWeb: MetricValue;
  readonly rimFwhmNative: MetricValue;
  readonly rimFwhmWeb: MetricValue;
  readonly shadowPeakDarkeningNative: MetricValue;
  readonly shadowPeakDarkeningWeb: MetricValue;
  readonly shadowPeakDistanceNative: MetricValue;
  readonly shadowPeakDistanceWeb: MetricValue;
  readonly shadowDecayLengthNative: MetricValue;
  readonly shadowDecayLengthWeb: MetricValue;
}

/** One side's single-image material measurements. */
export interface MaterialSideInput {
  readonly blur?: EdgeSpreadReport;
  readonly interior: InteriorLevelReport;
  readonly tint: TintResponseReport;
  readonly rim: RimIntensityReport;
  readonly shadow: ShadowFalloffReport;
}

export function materialAxisReport(input: {
  readonly native: MaterialSideInput;
  readonly web: MaterialSideInput;
  readonly backdropInterior: InteriorLevelReport;
  /** Absent on a solid-colour backdrop, where no transfer slope is identifiable. */
  readonly luminance?: LuminanceTransferReport;
}): MaterialAxisReport {
  const { native, web, luminance } = input;
  return {
    axis: "material",
    ...(native.blur === undefined
      ? {}
      : {
          blurSigmaNative: metricValue(native.blur.sigmaPx, "px"),
          blurFitResidualNative: metricValue(native.blur.residualRms, "ratio"),
        }),
    ...(web.blur === undefined
      ? {}
      : {
          blurSigmaWeb: metricValue(web.blur.sigmaPx, "px"),
          blurFitResidualWeb: metricValue(web.blur.residualRms, "ratio"),
        }),
    ...(luminance === undefined
      ? {}
      : {
          luminanceSlopeNative: metricValue(luminance.native.slope, "ratio"),
          luminanceSlopeWeb: metricValue(luminance.web.slope, "ratio"),
          luminanceOffsetNative: metricValue(luminance.native.offset, "luminance"),
          luminanceOffsetWeb: metricValue(luminance.web.offset, "luminance"),
          luminanceR2Native: metricValue(luminance.native.r2, "ratio"),
          luminanceR2Web: metricValue(luminance.web.r2, "ratio"),
        }),
    interiorMeanNative: metricValue(native.interior.mean, "luminance"),
    interiorMeanWeb: metricValue(web.interior.mean, "luminance"),
    interiorMeanBackdrop: metricValue(input.backdropInterior.mean, "luminance"),
    interiorStdDevNative: metricValue(native.interior.stdDev, "luminance"),
    interiorStdDevWeb: metricValue(web.interior.stdDev, "luminance"),
    interiorStdDevBackdrop: metricValue(input.backdropInterior.stdDev, "luminance"),
    tintDeltaLNative: metricValue(native.tint.deltaL, "oklab"),
    tintDeltaLWeb: metricValue(web.tint.deltaL, "oklab"),
    tintDeltaANative: metricValue(native.tint.deltaA, "oklab"),
    tintDeltaAWeb: metricValue(web.tint.deltaA, "oklab"),
    tintDeltaBNative: metricValue(native.tint.deltaB, "oklab"),
    tintDeltaBWeb: metricValue(web.tint.deltaB, "oklab"),
    tintChromaDeltaNative: metricValue(native.tint.chromaDelta, "oklab"),
    tintChromaDeltaWeb: metricValue(web.tint.chromaDelta, "oklab"),
    tintHueShiftNative: metricValue(native.tint.hueShiftDegrees, "degrees"),
    tintHueShiftWeb: metricValue(web.tint.hueShiftDegrees, "degrees"),
    rimPeakLuminanceNative: metricValue(native.rim.peakLuminance, "luminance"),
    rimPeakLuminanceWeb: metricValue(web.rim.peakLuminance, "luminance"),
    rimPeakDistanceNative: metricValue(native.rim.peakDistancePx, "px"),
    rimPeakDistanceWeb: metricValue(web.rim.peakDistancePx, "px"),
    rimFwhmNative: metricValue(native.rim.fwhmPx, "px"),
    rimFwhmWeb: metricValue(web.rim.fwhmPx, "px"),
    shadowPeakDarkeningNative: metricValue(native.shadow.peakDarkening, "luminance"),
    shadowPeakDarkeningWeb: metricValue(web.shadow.peakDarkening, "luminance"),
    shadowPeakDistanceNative: metricValue(native.shadow.peakDistancePx, "px"),
    shadowPeakDistanceWeb: metricValue(web.shadow.peakDistancePx, "px"),
    shadowDecayLengthNative: metricValue(native.shadow.decayLengthPx, "px"),
    shadowDecayLengthWeb: metricValue(web.shadow.decayLengthPx, "px"),
  };
}

export interface PerceptualAxisReport {
  readonly axis: "perceptual";
  readonly edgeWeightedMean: MetricValue;
  readonly edgeWeightedP95: MetricValue;
  readonly unweightedMean: MetricValue;
  readonly ssimMean: MetricValue;
  readonly ssimMin: MetricValue;
  readonly oklabDeltaEMean: MetricValue;
  readonly oklabDeltaEP95: MetricValue;
  readonly oklabDeltaEMax: MetricValue;
}

export function perceptualAxisReport(input: {
  readonly edgeWeighted: EdgeWeightedDifferenceReport;
  readonly ssim: SsimReport;
  readonly oklabDeltaE: OklabDeltaEReport;
}): PerceptualAxisReport {
  return {
    axis: "perceptual",
    edgeWeightedMean: metricValue(input.edgeWeighted.weightedMean, "luminance"),
    edgeWeightedP95: metricValue(input.edgeWeighted.weightedP95, "luminance"),
    unweightedMean: metricValue(input.edgeWeighted.unweightedMean, "luminance"),
    ssimMean: metricValue(input.ssim.mean, "ratio"),
    ssimMin: metricValue(input.ssim.min, "ratio"),
    oklabDeltaEMean: metricValue(input.oklabDeltaE.mean, "oklab"),
    oklabDeltaEP95: metricValue(input.oklabDeltaE.p95, "oklab"),
    oklabDeltaEMax: metricValue(input.oklabDeltaE.max, "oklab"),
  };
}

/**
 * The motion axis. The morph-trajectory fields are always present — C7
 * implements that metric — and the five timing fields are optional because they
 * need C9's event-to-frame timebase. Absent means "not measured yet", never
 * "measured as zero".
 */
export interface MotionAxisReport {
  readonly axis: "motion";
  readonly morphCentroidDistanceMax: MetricValue;
  readonly morphCentroidDistanceP95: MetricValue;
  readonly morphAreaRatioMin: MetricValue;
  readonly morphAreaRatioMax: MetricValue;
  readonly morphBoundsDeltaMax: MetricValue;
  readonly morphSilhouetteIoUMin: MetricValue;
  readonly morphFrameTimeDeltaMax: MetricValue;
  /** C9. */
  readonly responseLatency?: MetricValue;
  /** C9. */
  readonly peakCompression?: MetricValue;
  /** C9. */
  readonly overshoot?: MetricValue;
  /** C9. */
  readonly settlingTime?: MetricValue;
  /** C9. */
  readonly redirectContinuity?: MetricValue;
}

export function motionAxisReport(input: {
  readonly morph: MorphSilhouetteTrajectoryReport;
}): MotionAxisReport {
  return {
    axis: "motion",
    morphCentroidDistanceMax: metricValue(input.morph.centroidDistancePx.max, "px"),
    morphCentroidDistanceP95: metricValue(input.morph.centroidDistancePx.p95, "px"),
    morphAreaRatioMin: metricValue(input.morph.areaRatio.min, "ratio"),
    morphAreaRatioMax: metricValue(input.morph.areaRatio.max, "ratio"),
    morphBoundsDeltaMax: metricValue(input.morph.boundsDeltaPx.max, "px"),
    morphSilhouetteIoUMin: metricValue(input.morph.silhouetteIoU.min, "ratio"),
    morphFrameTimeDeltaMax: metricValue(input.morph.frameTimeDeltaMaxMs, "ms"),
  };
}

export type AxisReport = ShapeAxisReport | MaterialAxisReport | PerceptualAxisReport | MotionAxisReport;

// ---------------------------------------------------------------------------
// Cells and the matrix
// ---------------------------------------------------------------------------

/**
 * One measured cell. An axis is absent when that axis was not measured for this
 * cell — a still scene has no motion axis, and saying so by omission beats
 * inventing zeros.
 */
export interface CellResult {
  readonly key: ResultCellKey;
  readonly fixtureSet: FixtureSet;
  readonly tier: FidelityTier;
  /** ISO 8601 instant the measurement was taken. */
  readonly capturedAt: string;
  readonly shape?: ShapeAxisReport;
  readonly material?: MaterialAxisReport;
  readonly perceptual?: PerceptualAxisReport;
  readonly motion?: MotionAxisReport;
}

/**
 * Bumped only when the on-disk shape changes incompatibly.
 *
 * 2 (C9a): the material axis became two-sided. Its single-image sub-metrics —
 * blur, rim, shadow, interior level — grew required `Native`/`Web` pairs where
 * version 1 carried one unlabelled figure that was in fact the web side only.
 * A version-1 cell cannot be read as a version-2 cell, and silently treating a
 * web-only figure as a comparison is exactly the misreading the bump prevents.
 */
export const RESULT_MATRIX_SCHEMA_VERSION = 2;

/** Cells indexed by their serialised key. */
export interface ResultMatrix {
  readonly schemaVersion: number;
  readonly cells: ReadonlyMap<string, CellResult>;
}

export function createResultMatrix(cells: Iterable<CellResult> = []): ResultMatrix {
  const map = new Map<string, CellResult>();
  for (const cell of cells) map.set(serializeResultCellKey(cell.key), cell);
  return { schemaVersion: RESULT_MATRIX_SCHEMA_VERSION, cells: map };
}

/**
 * Insert or replace a cell, returning a new matrix.
 *
 * Replace, not merge: a re-measured cell supersedes the old one whole. Merging
 * axis-by-axis would let a matrix accumulate a shape report from one run and a
 * material report from another, and a cell that never existed as a single
 * measurement is not evidence for anything.
 */
export function upsertCellResult(matrix: ResultMatrix, result: CellResult): ResultMatrix {
  const cells = new Map(matrix.cells);
  cells.set(serializeResultCellKey(result.key), result);
  return { schemaVersion: matrix.schemaVersion, cells };
}

export function getCellResult(matrix: ResultMatrix, key: ResultCellKey): CellResult | undefined {
  return matrix.cells.get(serializeResultCellKey(key));
}

/** Every cell, in serialised-key order. */
export function listCellResults(matrix: ResultMatrix): readonly CellResult[] {
  return [...matrix.cells.keys()].sort().flatMap((key) => {
    const cell = matrix.cells.get(key);
    return cell ? [cell] : [];
  });
}

/**
 * Serialise to JSON, key-sorted and pretty-printed by default.
 *
 * Both defaults are for git. Result matrices are committed and CI-diffable per
 * the methodology, so a stable order and one field per line turn "this cell
 * moved" into a two-line diff instead of a whole-file rewrite.
 */
export function serializeResultMatrix(matrix: ResultMatrix, options: { readonly pretty?: boolean } = {}): string {
  const envelope = { schemaVersion: matrix.schemaVersion, cells: listCellResults(matrix) };
  return JSON.stringify(envelope, null, options.pretty === false ? undefined : 2);
}

/**
 * Parse a serialised matrix.
 *
 * The envelope is checked — this is a file boundary, and a wrong file is a
 * plausible mistake. The axis payloads are not re-validated field by field:
 * they are written by the builders above and nothing else produces them, so a
 * deep schema check here would be defending against a scenario that cannot
 * arise while making the round trip lossy the moment an axis grows a field.
 */
export function deserializeResultMatrix(json: string): ResultMatrix {
  let parsed: unknown;
  try {
    parsed = JSON.parse(json);
  } catch (error) {
    throw new CalibrationError("malformed-report", `deserializeResultMatrix: not JSON — ${String(error)}`);
  }

  if (typeof parsed !== "object" || parsed === null) {
    throw new CalibrationError("malformed-report", "deserializeResultMatrix: expected a JSON object.");
  }
  const envelope = parsed as { schemaVersion?: unknown; cells?: unknown };
  if (typeof envelope.schemaVersion !== "number") {
    throw new CalibrationError("malformed-report", "deserializeResultMatrix: no numeric schemaVersion.");
  }
  if (envelope.schemaVersion !== RESULT_MATRIX_SCHEMA_VERSION) {
    throw new CalibrationError(
      "malformed-report",
      `deserializeResultMatrix: schemaVersion ${envelope.schemaVersion}, this build writes ${RESULT_MATRIX_SCHEMA_VERSION}.`,
    );
  }
  if (!Array.isArray(envelope.cells)) {
    throw new CalibrationError("malformed-report", "deserializeResultMatrix: cells is not an array.");
  }

  const cells = new Map<string, CellResult>();
  for (const raw of envelope.cells as readonly CellResult[]) {
    if (typeof raw?.key?.profileKey !== "string" || typeof raw.key.sceneId !== "string") {
      throw new CalibrationError("malformed-report", "deserializeResultMatrix: a cell has no well-formed key.");
    }
    cells.set(serializeResultCellKey(raw.key), raw);
  }
  return { schemaVersion: envelope.schemaVersion, cells };
}
