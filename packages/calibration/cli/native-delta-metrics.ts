/**
 * One pair of native captures of the same declared cell, measured.
 *
 * This is the whole instrument behind the native delta, and it has exactly one
 * job: turn two captures of one scene into a vector of **non-negative
 * distances**, one per named law, so that the same function can be applied to
 * a 27-against-27 pair (the noise bar) and to a 27-against-26.5 pair (the
 * delta). The bar bounds the delta only if it was taken with the same reader,
 * the same masks and the same windows, so there is one reader here and not two.
 *
 * ## Why every metric is a distance
 *
 * The fidelity read reports similarities (`ssimMean`, `silhouetteIoU`) beside
 * differences (`contourDistanceMean`, `oklabDeltaEMean`) because a bound on it
 * points in a direction. A bar does not: "beyond the cell's own spread" needs
 * one comparison for every metric. So a similarity enters as its complement —
 * `1 - ssim`, `1 - IoU` — and a level enters as the absolute difference of the
 * two readings. The signed readings of both sides are carried beside the
 * distances, because a verdict of "Apple darkened the edge" needs the sign and
 * the bar cannot supply one.
 *
 * ## Which capture is the reference
 *
 * The **first** argument's silhouette masks every material statistic, exactly
 * as `measure.ts` masks with the native silhouette and for the same reason: two
 * masks would let the two sides report levels over different pixel sets, and
 * the question is what the other capture does where this one's material is. In
 * the delta the reference is the 26.5 fixture, which is the bed every adopted
 * bound was fitted against; in the bar it is the lower-numbered run of the
 * pair. Within a bed the two masks agree to a handful of pixels, so the choice
 * costs the bar nothing and keeps the delta framed on the frozen bed.
 *
 * ## What is absent, and why absence is not zero
 *
 * A cell whose component is a composite (`toolbar-group`, `glass-over-glass`)
 * has no single declared box, so the two declared-geometry readers have nothing
 * to say and their rows are `null`. A solid backdrop identifies no luminance
 * transfer. A silhouette that comes out empty — the reference within the
 * extractor's threshold of its own backdrop — leaves the shape and material
 * rows absent. In every case the row is `null` and the reason is recorded;
 * `null` never becomes 0, which would read as "measured, and identical".
 */

import {
  contourDistance,
  cornerCurvature,
  decidableRegion,
  edgeWeightedDifference,
  extractSilhouette,
  fitLuminanceTransfer,
  hueDifferenceDegrees,
  interiorLevel,
  oklabDistance,
  oklabDeltaE,
  rimIntensity,
  silhouetteArea,
  silhouetteIoU,
  srgbByteToOklab,
  ssimDepthWindows,
  ssimFromMap,
  ssimMap,
  SSIM_BAND_SPLIT_CSS_PX,
  tintResponse,
  type CalibrationImage,
  type ComponentRegion,
  type RimIntensityReport,
  type Silhouette,
} from "../src/index";
import {
  angularRead,
  contourRimRead,
  declaredBox,
  rasterOf,
  wrapDegrees,
  ANGULAR_BINS,
  RIM_SIDES,
  type AngularRead,
  type ContourRimRead,
  type DeclaredBox,
} from "./native-delta-readers";

// ---------------------------------------------------------------------------
// Which cells form a pair
// ---------------------------------------------------------------------------

/**
 * The 26.5 key a 27 key names the same configuration as: the OS token moved
 * back and the slider token dropped. The slider axis does not exist before 27,
 * so dropping it is not losing an axis — these are the two keys that differ in
 * exactly the thing being measured, plus the one axis 26.5 had no way to carry.
 *
 * `-coupled` drops with it, and for the same reason: macOS 26.5 had no way to
 * carry that axis either. Contrast force-enabled transparency reduction there,
 * so `apple-macos-26.5-1x-light-increased-contrast` IS the coupled state and the
 * token would be redundant on it (claims §5.150 Part B §3). The consequence is
 * that the two 27 contrast keys both name that one 26.5 key, which is the shape
 * of the question: one 26.5 state split into two on 27, and the pair worth
 * reading like-for-like is the coupled one (W29 Decision Log 4 (b), §5.152).
 */
export function counterpartKey(key27: string): string {
  return key27
    .replace(/^apple-macos-27\.0-/, "apple-macos-26.5-")
    .replace(/-glass[\d.]+$/, "")
    .replace(/-increased-contrast-coupled$/, "-increased-contrast");
}

/** Active or receded, read off the scene's own state token (X3: the pose is a scene state). */
export function poseOf(sceneId: string): "active" | "inactive" {
  return sceneId.split("__")[2]?.startsWith("inactive") === true ? "inactive" : "active";
}

/** The active id a receded id is the recede OF, or null where the scene has no active twin. */
export function activeTwinOf(sceneId: string): string | null {
  const parts = sceneId.split("__");
  const state = parts[2];
  if (parts.length !== 3 || state === undefined || !state.startsWith("inactive")) return null;
  const rest = state.slice("inactive".length);
  const active = rest === "" ? "rest" : rest === "-pressed" ? "pressed" : `rest${rest}`;
  return `${parts[0] ?? ""}__${parts[1] ?? ""}__${active}`;
}

/** The same detection threshold `compare` defaults to, so the masks agree with the matrix's. */
export const SILHOUETTE_THRESHOLD = 0.02;
/** The chroma arm (W11b, claims §5.40), at the value `measure` declares. */
export const SILHOUETTE_CHROMA_THRESHOLD = 0.03;

/**
 * Every metric this instrument reports, in the order the tables print them.
 *
 * The list is exported and iterated rather than written out per call site, so
 * the bar file, the delta file and the sheets can never disagree about which
 * metrics exist.
 */
export const NATIVE_DELTA_METRICS = [
  // Silhouette and geometry.
  "silhouetteIoUComplement",
  "contourDistanceMeanPx",
  "contourDistanceP95Px",
  "silhouetteAreaDeltaPx",
  "cornerCurvatureDeltaPerPx",
  // Perceptual, whole cell as the fidelity read defines it, plus the body.
  "ssimComplement",
  "ssimBandComplement",
  "ssimInteriorComplement",
  "ssimOutsideComplement",
  "oklabDeltaEMean",
  "oklabDeltaEP95",
  "oklabDeltaEBodyMean",
  "edgeWeightedMean",
  // Interior level, tone response and scatter.
  "interiorMeanDelta",
  "interiorStdDevDelta",
  "bodyLevelDelta",
  "transferSlopeDelta",
  "transferOffsetDelta",
  // The rim band: W23's contour reader and the radial profile.
  "rimContourDeltaMax",
  "rimLocalDeltaMax",
  "rimRow0DeltaMax",
  "rimPeakDelta",
  "rimPeakDepthDeltaPx",
  "rimFwhmDeltaPx",
  // The highlight: W24's angular reader.
  "highlightBinDeltaMax",
  "highlightBinDeltaMean",
  "highlightIntegralDeltaMax",
  "highlightRatioDelta",
  "highlightPeakAngleDeltaDeg",
  // Tint shade.
  "tintDeltaLDelta",
  "tintChromaDelta",
  "tintHueShiftDeltaDeg",
] as const;

export type NativeDeltaMetric = (typeof NATIVE_DELTA_METRICS)[number];

/** A metric vector. `null` is "not measurable on this cell", never zero. */
export type MetricVector = Readonly<Record<NativeDeltaMetric, number | null>>;

/** What one capture says about itself, read once and reused across every pair it is in. */
export interface CaptureReading {
  readonly image: CalibrationImage;
  readonly silhouette: Silhouette;
  readonly area: number;
  /** The radial rim profile under this capture's own silhouette. */
  readonly rim: RimIntensityReport | null;
  /** W23's per-side contour read off the declared box. */
  readonly contour: ContourRimRead | null;
  /** W24's angular read off the declared boundary. */
  readonly angular: AngularRead | null;
}

export interface CellGeometry {
  readonly region: ComponentRegion;
  readonly box: DeclaredBox | null;
  readonly scale: number;
}

export function cellGeometry(
  region: ComponentRegion,
  component: Parameters<typeof declaredBox>[0],
  canvas: Parameters<typeof declaredBox>[1],
  scale: number,
): CellGeometry {
  return { region, box: declaredBox(component, canvas, scale), scale };
}

/**
 * Read one capture: its silhouette inside the declared region, its radial rim,
 * and the two declared-geometry readings.
 *
 * Separated from the pair so that a cell with seven runs pays for seven reads
 * and not for twenty-one — the bar's pairwise construction would otherwise
 * re-derive the same per-capture quantities three times over.
 */
export function readCapture(
  image: CalibrationImage,
  background: CalibrationImage,
  geometry: CellGeometry,
): CaptureReading {
  const silhouette = extractSilhouette(image, {
    kind: "luminance-delta",
    background,
    threshold: SILHOUETTE_THRESHOLD,
    chromaThreshold: SILHOUETTE_CHROMA_THRESHOLD,
    region: geometry.region.silhouette,
  });
  const area = silhouetteArea(silhouette);
  let rim: RimIntensityReport | null = null;
  if (area > 0) {
    try {
      rim = rimIntensity(image, silhouette);
    } catch {
      rim = null;
    }
  }
  let contour: ContourRimRead | null = null;
  let angular: AngularRead | null = null;
  if (geometry.box !== null) {
    const raster = rasterOf(image);
    contour = contourRimRead(raster, geometry.box, geometry.scale);
    angular = angularRead(raster, geometry.box, geometry.scale);
  }
  return { image, silhouette, area, rim, contour, angular };
}

function absMaxOverSides(
  a: ContourRimRead,
  b: ContourRimRead,
  pick: (side: ContourRimRead["sides"][keyof ContourRimRead["sides"]]) => number,
): number | null {
  let worst: number | null = null;
  for (const side of RIM_SIDES) {
    const left = pick(a.sides[side]);
    const right = pick(b.sides[side]);
    if (!Number.isFinite(left) || !Number.isFinite(right)) continue;
    const delta = Math.abs(left - right);
    worst = worst === null ? delta : Math.max(worst, delta);
  }
  return worst;
}

/** ΔE over one mask only — `oklabDeltaE` is whole-canvas by construction. */
function maskedDeltaEMean(
  a: CalibrationImage,
  b: CalibrationImage,
  mask: Silhouette,
): number | null {
  const count = a.width * a.height;
  let sum = 0;
  let taken = 0;
  for (let i = 0; i < count; i += 1) {
    if ((mask.mask[i] ?? 0) === 0) continue;
    const src = i * 4;
    sum += oklabDistance(
      srgbByteToOklab(a.data[src] ?? 0, a.data[src + 1] ?? 0, a.data[src + 2] ?? 0),
      srgbByteToOklab(b.data[src] ?? 0, b.data[src + 1] ?? 0, b.data[src + 2] ?? 0),
    );
    taken += 1;
  }
  return taken === 0 ? null : sum / taken;
}

/** The signed readings both sides carried, so a verdict can state a direction. */
export interface PairReadings {
  readonly interiorMean: readonly [number, number] | null;
  readonly interiorStdDev: readonly [number, number] | null;
  readonly bodyLevel: readonly [number, number] | null;
  readonly transferSlope: readonly [number, number] | null;
  readonly transferOffset: readonly [number, number] | null;
  readonly transferR2: readonly [number, number] | null;
  readonly rimContourMeanSide: readonly [number, number] | null;
  readonly rimPeak: readonly [number, number] | null;
  readonly rimPeakDepthPx: readonly [number, number] | null;
  readonly rimFwhmPx: readonly [number, number] | null;
  readonly highlightBins: readonly [readonly (number | null)[], readonly (number | null)[]] | null;
  readonly highlightRatio: readonly [number, number] | null;
  readonly highlightPeakAngleDeg: readonly [number, number] | null;
  readonly cornerCurvaturePerPx: readonly [number, number] | null;
  readonly silhouetteAreaPx: readonly [number, number];
  readonly tintDeltaL: readonly [number, number] | null;
  readonly tintChroma: readonly [number, number] | null;
  readonly tintHueShiftDeg: readonly [number, number] | null;
}

export interface PairResult {
  readonly metrics: MetricVector;
  readonly readings: PairReadings;
  /** Everything this pair legitimately could not measure, and why. */
  readonly notes: readonly string[];
}

/**
 * Measure one pair. `a` is the reference: its silhouette masks the material
 * statistics and defines the SSIM depth windows.
 */
export function pairMetrics(
  a: CaptureReading,
  b: CaptureReading,
  background: CalibrationImage,
  geometry: CellGeometry,
): PairResult {
  const notes: string[] = [];
  const metrics: Record<NativeDeltaMetric, number | null> = Object.fromEntries(
    NATIVE_DELTA_METRICS.map((name) => [name, null]),
  ) as Record<NativeDeltaMetric, number | null>;

  // ---- perceptual, whole cell -------------------------------------------
  const field = ssimMap(a.image, b.image);
  metrics.ssimComplement = 1 - ssimFromMap(field).mean;
  const colour = oklabDeltaE(a.image, b.image);
  metrics.oklabDeltaEMean = colour.mean;
  metrics.oklabDeltaEP95 = colour.p95;
  metrics.edgeWeightedMean = edgeWeightedDifference(a.image, b.image).weightedMean;

  // ---- shape --------------------------------------------------------------
  let cornerCurvaturePerPx: readonly [number, number] | null = null;
  if (a.area === 0 || b.area === 0) {
    notes.push(
      `shape and material rows ABSENT: the ${a.area === 0 ? "reference" : "other"} silhouette is ` +
        `empty at threshold ${String(SILHOUETTE_THRESHOLD)} inside the declared region, so that ` +
        `capture is indistinguishable from its backdrop there.`,
    );
  } else {
    const decidable = decidableRegion(geometry.region.silhouette, a.silhouette, b.silhouette);
    metrics.silhouetteIoUComplement = 1 - silhouetteIoU(a.silhouette, b.silhouette, decidable);
    const contour = contourDistance(a.silhouette, b.silhouette);
    metrics.contourDistanceMeanPx = contour.meanPx;
    metrics.contourDistanceP95Px = contour.p95Px;
    metrics.silhouetteAreaDeltaPx = Math.abs(a.area - b.area);
    try {
      const curvature = cornerCurvature(a.silhouette, b.silhouette);
      cornerCurvaturePerPx = [curvature.cornerCurvaturePerPxA, curvature.cornerCurvaturePerPxB];
      metrics.cornerCurvatureDeltaPerPx = Math.abs(
        curvature.cornerCurvaturePerPxA - curvature.cornerCurvaturePerPxB,
      );
    } catch (error) {
      /*
       * A silhouette can be non-empty and still carry no traceable contour —
       * a few scattered pixels where the extractor found the material's own
       * level meeting the backdrop's. Curvature is then undefined rather than
       * zero, and a zero here would read as "the two corners agree exactly",
       * which is the opposite of what happened.
       */
      notes.push(
        `corner curvature ABSENT: ${error instanceof Error ? error.message : String(error)}`,
      );
    }

    const windows = ssimDepthWindows(field, a.silhouette, {
      splitPx: SSIM_BAND_SPLIT_CSS_PX * geometry.scale,
    });
    if (windows.band !== undefined) metrics.ssimBandComplement = 1 - windows.band.mean;
    if (windows.interior !== undefined) metrics.ssimInteriorComplement = 1 - windows.interior.mean;
    if (windows.outside !== undefined) metrics.ssimOutsideComplement = 1 - windows.outside.mean;
    metrics.oklabDeltaEBodyMean = maskedDeltaEMean(a.image, b.image, a.silhouette);
  }

  // ---- interior level, tone response, scatter, tint ------------------------
  let interiorMean: readonly [number, number] | null = null;
  let interiorStdDev: readonly [number, number] | null = null;
  let transferSlope: readonly [number, number] | null = null;
  let transferOffset: readonly [number, number] | null = null;
  let transferR2: readonly [number, number] | null = null;
  let tintDeltaL: readonly [number, number] | null = null;
  let tintChroma: readonly [number, number] | null = null;
  let tintHueShiftDeg: readonly [number, number] | null = null;
  if (a.area > 0) {
    const levelA = interiorLevel(a.image, { interior: a.silhouette });
    const levelB = interiorLevel(b.image, { interior: a.silhouette });
    interiorMean = [levelA.mean, levelB.mean];
    interiorStdDev = [levelA.stdDev, levelB.stdDev];
    metrics.interiorMeanDelta = Math.abs(levelA.mean - levelB.mean);
    metrics.interiorStdDevDelta = Math.abs(levelA.stdDev - levelB.stdDev);

    try {
      const fitA = fitLuminanceTransfer(a.image, background, { interior: a.silhouette });
      const fitB = fitLuminanceTransfer(b.image, background, { interior: a.silhouette });
      transferSlope = [fitA.slope, fitB.slope];
      transferOffset = [fitA.offset, fitB.offset];
      transferR2 = [fitA.r2, fitB.r2];
      metrics.transferSlopeDelta = Math.abs(fitA.slope - fitB.slope);
      metrics.transferOffsetDelta = Math.abs(fitA.offset - fitB.offset);
    } catch {
      // A solid backdrop identifies no slope; reporting one would be arithmetic
      // on no information. Absent, not zero.
      notes.push(
        "luminance transfer ABSENT: the backdrop under this silhouette does not vary, so no " +
          "affine transfer is identifiable on either side.",
      );
    }

    const tintA = tintResponse(a.image, background, { interior: a.silhouette });
    const tintB = tintResponse(b.image, background, { interior: a.silhouette });
    tintDeltaL = [tintA.deltaL, tintB.deltaL];
    tintChroma = [tintA.interiorChroma, tintB.interiorChroma];
    tintHueShiftDeg = [tintA.hueShiftDegrees, tintB.hueShiftDegrees];
    metrics.tintDeltaLDelta = Math.abs(tintA.deltaL - tintB.deltaL);
    metrics.tintChromaDelta = Math.abs(tintA.interiorChroma - tintB.interiorChroma);
    metrics.tintHueShiftDeltaDeg = Math.abs(
      hueDifferenceDegrees(tintA.hueShiftDegrees, tintB.hueShiftDegrees),
    );
  }

  // ---- the rim band -------------------------------------------------------
  let rimContourMeanSide: readonly [number, number] | null = null;
  let bodyLevel: readonly [number, number] | null = null;
  if (a.contour !== null && b.contour !== null) {
    metrics.rimContourDeltaMax = absMaxOverSides(a.contour, b.contour, (side) => side.rim);
    metrics.rimLocalDeltaMax = absMaxOverSides(a.contour, b.contour, (side) => side.rimLocal);
    metrics.rimRow0DeltaMax = absMaxOverSides(a.contour, b.contour, (side) => side.row0);
    bodyLevel = [a.contour.body, b.contour.body];
    metrics.bodyLevelDelta = Math.abs(a.contour.body - b.contour.body);
    const meanSide = (read: ContourRimRead): number => {
      let sum = 0;
      let count = 0;
      for (const side of RIM_SIDES) {
        const value = read.sides[side].rim;
        if (!Number.isFinite(value)) continue;
        sum += value;
        count += 1;
      }
      return count === 0 ? NaN : sum / count;
    };
    const left = meanSide(a.contour);
    const right = meanSide(b.contour);
    if (Number.isFinite(left) && Number.isFinite(right)) rimContourMeanSide = [left, right];
  } else {
    notes.push(
      "the declared-geometry rim and highlight rows are ABSENT: this component is a composite " +
        "with no single declared box, so neither W23's per-side contour reader nor W24's angular " +
        "reader has a boundary to read.",
    );
  }

  let rimPeak: readonly [number, number] | null = null;
  let rimPeakDepthPx: readonly [number, number] | null = null;
  let rimFwhmPx: readonly [number, number] | null = null;
  if (a.rim !== null && b.rim !== null) {
    rimPeak = [a.rim.peakLuminance, b.rim.peakLuminance];
    rimPeakDepthPx = [a.rim.peakDistancePx, b.rim.peakDistancePx];
    metrics.rimPeakDelta = Math.abs(a.rim.peakLuminance - b.rim.peakLuminance);
    metrics.rimPeakDepthDeltaPx = Math.abs(a.rim.peakDistancePx - b.rim.peakDistancePx);
    if (a.rim.fwhmResolved && b.rim.fwhmResolved) {
      rimFwhmPx = [a.rim.fwhmPx, b.rim.fwhmPx];
      metrics.rimFwhmDeltaPx = Math.abs(a.rim.fwhmPx - b.rim.fwhmPx);
    }
  }

  // ---- the highlight ------------------------------------------------------
  let highlightBins:
    | readonly [readonly (number | null)[], readonly (number | null)[]]
    | null = null;
  let highlightRatio: readonly [number, number] | null = null;
  let highlightPeakAngleDeg: readonly [number, number] | null = null;
  if (a.angular !== null && b.angular !== null) {
    highlightBins = [a.angular.bins, b.angular.bins];
    let worst: number | null = null;
    let sum = 0;
    let taken = 0;
    let worstIntegral: number | null = null;
    for (let k = 0; k < ANGULAR_BINS; k += 1) {
      const left = a.angular.bins[k];
      const right = b.angular.bins[k];
      if (left !== null && left !== undefined && right !== null && right !== undefined) {
        const delta = Math.abs(left - right);
        worst = worst === null ? delta : Math.max(worst, delta);
        sum += delta;
        taken += 1;
      }
      const leftBand = a.angular.integral[k];
      const rightBand = b.angular.integral[k];
      if (leftBand !== null && leftBand !== undefined && rightBand !== null && rightBand !== undefined) {
        const delta = Math.abs(leftBand - rightBand);
        worstIntegral = worstIntegral === null ? delta : Math.max(worstIntegral, delta);
      }
    }
    metrics.highlightBinDeltaMax = worst;
    metrics.highlightBinDeltaMean = taken === 0 ? null : sum / taken;
    metrics.highlightIntegralDeltaMax = worstIntegral;
    if (Number.isFinite(a.angular.ratio) && Number.isFinite(b.angular.ratio)) {
      highlightRatio = [a.angular.ratio, b.angular.ratio];
      metrics.highlightRatioDelta = Math.abs(a.angular.ratio - b.angular.ratio);
    }
    highlightPeakAngleDeg = [a.angular.brightestAngleDeg, b.angular.brightestAngleDeg];
    metrics.highlightPeakAngleDeltaDeg = Math.abs(
      wrapDegrees(a.angular.brightestAngleDeg - b.angular.brightestAngleDeg),
    );
  }

  return {
    metrics,
    readings: {
      interiorMean,
      interiorStdDev,
      bodyLevel,
      transferSlope,
      transferOffset,
      transferR2,
      rimContourMeanSide,
      rimPeak,
      rimPeakDepthPx,
      rimFwhmPx,
      highlightBins,
      highlightRatio,
      highlightPeakAngleDeg,
      cornerCurvaturePerPx,
      silhouetteAreaPx: [a.area, b.area],
      tintDeltaL,
      tintChroma,
      tintHueShiftDeg,
    },
    notes,
  };
}
