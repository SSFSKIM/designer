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
import type { ShadowFieldReport } from "./metrics/shadow";
import type {
  EdgeWeightedDifferenceReport,
  OklabDeltaEReport,
  SsimReport,
  SsimWindowReport,
} from "./metrics/perceptual";
import { parseProfileKey, type FidelityTier, type FixtureSet } from "./profile";

// ---------------------------------------------------------------------------
// Metric values
// ---------------------------------------------------------------------------

/**
 * The units this package reports in. A closed set, so a report cannot carry a
 * number whose meaning is only in a comment somewhere.
 */
// "count" is a cardinality rather than a measurement — the silhouette hole
// counts, whose whole point is how MANY extra boundaries a contour trace meets.
export const METRIC_UNITS = ["ratio", "px", "px^2", "1/px", "luminance", "oklab", "ms", "degrees", "px/ms", "count"] as const;

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

/**
 * The shape axis, **bounded to the declared component region** from schema 5.
 *
 * What it claims: each side fills, and stays inside, the geometry the scene
 * matrix declares — coverage, contour position and corner profile within that
 * region, which is the corner-and-edge fidelity the axis exists for.
 *
 * What it no longer claims: area recovery. The search region is the declaration
 * itself (see `component-region.ts`), so a surface drawn *larger* than declared
 * is clipped to the declaration and reads as a match, and the reference's own
 * silhouette saturates the region wherever its shadow does. Both sides' areas
 * are therefore bounded above by `componentRegionArea` by construction — which
 * is why that number is on the record, and why the conditioning predicate reads
 * as a floor with an *assumed* ceiling rather than as a two-sided measurement.
 */
export interface ShapeAxisReport {
  readonly axis: "shape";
  /**
   * Extracted silhouette area per side, in pixels, inside the declared region.
   *
   * Reported because it is how a reader tells a shape *difference* from a shape
   * *measurement failure*, and the two are not distinguishable from IoU alone.
   * The luminance-delta extractor finds the component by differencing against its
   * backdrop, so it necessarily loses any part of the material whose level
   * coincides with the backdrop's — and the canonical matrix contains exactly
   * that case. A dark material over a black-and-white checkerboard is genuinely
   * indistinguishable from the black squares it covers: measured, the native
   * silhouette comes back at 4324 px where the declared capsule is 4865, holes
   * punched through its own interior. The IoU and contour figures for such a cell
   * describe the extractor, not the geometry.
   *
   * A gate can therefore condition on these: an area far from the declared
   * component's is a cell whose shape axis should not be gated. That check is
   * only possible if the areas are on the record, so they are.
   */
  readonly silhouetteAreaNative: MetricValue;
  readonly silhouetteAreaWeb: MetricValue;
  /**
   * Area of the search region both silhouettes were cut out of, in pixels — the
   * declared geometry as rasterised, dilated by `componentRegionMargin`.
   *
   * The ceiling of the conditioning predicate, and the number that makes the
   * axis's assumption auditable per cell: a silhouette at this value has been
   * clipped by the bound rather than measured to it.
   */
  readonly componentRegionArea: MetricValue;
  /** Outward dilation of the declared geometry, device px. Zero on this bed. */
  readonly componentRegionMargin: MetricValue;
  /**
   * Interior holes in each side's extracted silhouette — connected components of
   * the search region that the mask excludes and that do not touch the region's
   * border.
   *
   * The conditioning question that area cannot answer. §5.12 proposed a web-side
   * ARM on the area predicate; the recalibration cascade measured that such an
   * arm gates the wrong cells. The degenerate cell that motivated it was repaired
   * by the refit (recovery 0.888 → 1.000), while the cells that now mis-measure
   * recover 94.8…96.2% of their region — above any usable floor — and read an
   * IoU of 0.96 beside a contour distance of 65 px. What breaks the contour
   * metric is topology: the trace walks every boundary it finds, so a mask with
   * 72 interior holes reports those hole boundaries as distance from the other
   * side's outline.
   *
   * The mechanism is a tier interaction rather than a renderer error. The two
   * tiers blur in different colour spaces — this renderer in linear light,
   * `backdrop-filter` in the encoded one — so over a high-contrast backdrop the
   * CSS tier transmits enough structure that interior pixels coincide with the
   * backdrop's own level and the extractor punches them out. Measured zero on the
   * native side and on the texture tier of the very same cells.
   *
   * On the record per cell for the same reason `silhouetteArea*` is: a gate
   * cannot condition on what the matrix does not carry.
   */
  readonly silhouetteHolesNative: MetricValue;
  readonly silhouetteHolesWeb: MetricValue;
  /**
   * Connected bodies in each side's hole-filled silhouette, and in the declared
   * region itself — the conditioning statement the contour rows carry.
   *
   * A mask the extractor has broken into pieces has more outlines than the
   * surface does, and the contour metric compares outlines. The count to beat is
   * the REGION's own, not 1, so a genuinely multi-body component is not
   * penalised for being one: `toolbar-group` declares three capsules and its
   * region has three components. That is what keeps this free of a chosen
   * threshold.
   */
  readonly silhouetteBodiesNative: MetricValue;
  readonly silhouetteBodiesWeb: MetricValue;
  readonly componentRegionBodies: MetricValue;
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
  readonly silhouetteAreaNative: number;
  readonly silhouetteAreaWeb: number;
  readonly componentRegionArea: number;
  readonly componentRegionMarginPx: number;
  readonly silhouetteHolesNative: number;
  readonly silhouetteHolesWeb: number;
  readonly silhouetteBodiesNative: number;
  readonly silhouetteBodiesWeb: number;
  readonly componentRegionBodies: number;
  readonly silhouetteIoU: number;
  readonly contourDistance: ContourDistanceReport;
  readonly cornerCurvature: CornerCurvatureReport;
}): ShapeAxisReport {
  return {
    axis: "shape",
    silhouetteAreaNative: metricValue(input.silhouetteAreaNative, "px^2"),
    silhouetteAreaWeb: metricValue(input.silhouetteAreaWeb, "px^2"),
    componentRegionArea: metricValue(input.componentRegionArea, "px^2"),
    componentRegionMargin: metricValue(input.componentRegionMarginPx, "px"),
    silhouetteHolesNative: metricValue(input.silhouetteHolesNative, "count"),
    silhouetteHolesWeb: metricValue(input.silhouetteHolesWeb, "count"),
    silhouetteBodiesNative: metricValue(input.silhouetteBodiesNative, "count"),
    silhouetteBodiesWeb: metricValue(input.silhouetteBodiesWeb, "count"),
    componentRegionBodies: metricValue(input.componentRegionBodies, "count"),
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
  /**
   * The band-windowed rows (W13 X6): the same SSIM map as `ssimMean`, averaged
   * over the reference silhouette's pixels within `SSIM_BAND_SPLIT_CSS_PX` of
   * its contour and over those deeper than it. Recorded, not gated: no adopted
   * bound reads them before W13 G2's landing.
   *
   * Optional in both directions, and absent means "no such population on this
   * cell", never zero — a cell with no native silhouette has no contour to
   * measure depth from, and a surface whose half-span is under the split is all
   * band with no interior. The window counts travel with the means because the
   * two rows weigh differently in every comparison made from them: the band's
   * share of a cell's SSIM deficit is `(1 - ssimBand) * ssimBandWindows`
   * against `(1 - ssimInterior) * ssimInteriorWindows`, and a mean without its
   * support cannot be pooled or compared across spans.
   */
  readonly ssimBand?: MetricValue;
  readonly ssimBandWindows?: MetricValue;
  readonly ssimInterior?: MetricValue;
  readonly ssimInteriorWindows?: MetricValue;
  readonly oklabDeltaEMean: MetricValue;
  readonly oklabDeltaEP95: MetricValue;
  readonly oklabDeltaEMax: MetricValue;
}

export function perceptualAxisReport(input: {
  readonly edgeWeighted: EdgeWeightedDifferenceReport;
  readonly ssim: SsimReport;
  readonly depthWindows?: { readonly band?: SsimWindowReport; readonly interior?: SsimWindowReport };
  readonly oklabDeltaE: OklabDeltaEReport;
}): PerceptualAxisReport {
  const band = input.depthWindows?.band;
  const interior = input.depthWindows?.interior;
  return {
    axis: "perceptual",
    edgeWeightedMean: metricValue(input.edgeWeighted.weightedMean, "luminance"),
    edgeWeightedP95: metricValue(input.edgeWeighted.weightedP95, "luminance"),
    unweightedMean: metricValue(input.edgeWeighted.unweightedMean, "luminance"),
    ssimMean: metricValue(input.ssim.mean, "ratio"),
    ssimMin: metricValue(input.ssim.min, "ratio"),
    ...(band === undefined
      ? {}
      : {
          ssimBand: metricValue(band.mean, "ratio"),
          ssimBandWindows: metricValue(band.windowCount, "count"),
        }),
    ...(interior === undefined
      ? {}
      : {
          ssimInterior: metricValue(interior.mean, "ratio"),
          ssimInteriorWindows: metricValue(interior.windowCount, "count"),
        }),
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

/**
 * The coherence axis: how far apart the two tiers draw the same scene.
 *
 * Every other axis is a *fidelity* axis — web against native. This one has no
 * fixture in it at all: it is the dom-tier capture against its texture twin, the
 * same profile key and the same scene rendered through vitrea's own shader math
 * instead of the engine's blur. Two tiers can each sit inside their own
 * thresholds and still be visibly different from each other, and a demotion is
 * exactly where a reader sees the pair side by side rather than each beside
 * Apple. C9a measured what that costs when nobody is watching: the CSS tier's
 * `tintAlpha` was 0.28 against the renderer's 0.62, a >2× opacity change on
 * losing a GPU device.
 *
 * **It belongs to the dom-tier cell**, not the texture one, because the CSS tier
 * is the one that moves — and because a quantity stored on both halves of a pair
 * is a quantity that can disagree with itself. The direction is fixed as GPU ÷
 * CSS so the number reads the same way wherever it is quoted.
 *
 * Absent, never zeroed, in both of the ways it can be:
 *
 *   - **The whole axis is absent** when the twin capture is not on disk. A cell
 *     measured on one tier alone is not a coherence data point, and pairing it
 *     with itself would be measuring nothing.
 *   - **`interiorLevelRatioGpuOverCss` alone is absent** when the scene has no
 *     interior to sample — over a solid backdrop of the material's own tone the
 *     native silhouette is empty, so there is no shared mask for a level. The
 *     cross-tier ΔE is whole-canvas and survives that.
 */
export interface CoherenceAxisReport {
  readonly axis: "coherence";
  /** Whole-canvas OKLab ΔE between the two tiers' own captures. */
  readonly crossTierOklabDeltaEMean: MetricValue;
  /**
   * Each tier's interior level under the **native** silhouette, divided. The
   * same mask both sides, for the reason `measure.ts` gives: two masks would let
   * the tiers report levels over different pixel sets, and the whole question is
   * what each does over the same region.
   */
  readonly interiorLevelRatioGpuOverCss?: MetricValue;
}

export function coherenceAxisReport(input: {
  readonly crossTierOklabDeltaEMean: number;
  readonly interiorLevelRatioGpuOverCss?: number;
}): CoherenceAxisReport {
  return {
    axis: "coherence",
    crossTierOklabDeltaEMean: metricValue(input.crossTierOklabDeltaEMean, "oklab"),
    ...(input.interiorLevelRatioGpuOverCss === undefined
      ? {}
      : { interiorLevelRatioGpuOverCss: metricValue(input.interiorLevelRatioGpuOverCss, "ratio") }),
  };
}

/**
 * The shadow axis: what each side does to the backdrop it does not cover.
 *
 * Its own axis from schema 5, because the outer shadow turned out to be a facet
 * of Apple's material rather than a detail of it — a downward-offset
 * multiplicative occlusion over 8.5–29.6% of the canvas that vitrea renders as
 * exactly zero (claims §5.11, wave Decision Log 15). The material axis's
 * `shadow*` pair stays where it is and keeps its meaning as an isotropic summary
 * profiled from the extracted silhouette; this axis is the directional
 * description a renderer can be fitted against, measured from the *declared*
 * contour so it is not hostage to what the extractor recovered.
 *
 * Every figure is per side, by the same estimator over the same exterior, since
 * a gap is not a quantity until both halves are measured the same way.
 *
 * **Absent, never zeroed**, in four distinguishable ways:
 *
 *   - The normalised block — strength, extents, offsets, falloff — is absent
 *     where the backdrop cannot support a ratio. A shadow removes a fraction of
 *     the light behind it, and over `dark-solid` or `impulse` there is none to
 *     remove, so no shadow of any strength is recoverable there.
 *     `backdropSupport` records how far short the scene fell.
 *   - `offset*` is absent where no direction reached the occlusion threshold.
 *     That is what a renderer drawing no shadow produces, and an undefined
 *     displacement recorded as undefined is not the same claim as (0, 0).
 *   - `centroidOffset*` is absent where too little of the exterior is occluded
 *     for a mass centroid to describe the shadow rather than the backdrop.
 *   - `falloffLength`/`falloffResidual` are absent where the profile has too few
 *     rings past the body's own edge ring to fit, or when that family's fit
 *     lands on an impossible amplitude or a sub-pixel scale. The two families
 *     are absent independently: a profile can be describable as a blurred edge
 *     and not as an exponential, which on this bed is the usual case.
 *
 * `meanDeparture*` is the one figure present on every scene: an absolute
 * luminance difference is defined even where a ratio is not, and it is what
 * claims §5.11 quoted (0.0000 on vitrea's side against 0.0022…0.0153 on the
 * reference's).
 */
export interface ShadowAxisReport {
  readonly axis: "shadow";
  /** Pixels outside the declared region — the population every figure is over. */
  readonly exteriorArea: MetricValue;
  readonly backdropMeanLuminance: MetricValue;
  readonly backdropSupport: MetricValue;
  /**
   * Distance from the declared contour to the canvas edge on each side — the
   * measuring window, a property of the scene and so reported once.
   *
   * An `extent*` absent beside one of these says the walk was still qualifying
   * when the capture ran out, which is the one reading absence would otherwise
   * be indistinguishable from a scene with no shadow to find.
   */
  readonly clearanceAbove: MetricValue;
  readonly clearanceBelow: MetricValue;
  readonly clearanceLeft: MetricValue;
  readonly clearanceRight: MetricValue;
  readonly meanDepartureNative: MetricValue;
  readonly meanDepartureWeb: MetricValue;
  readonly strengthPeakNative?: MetricValue;
  readonly strengthPeakWeb?: MetricValue;
  readonly strengthPeakDistanceNative?: MetricValue;
  readonly strengthPeakDistanceWeb?: MetricValue;
  readonly extentAboveNative?: MetricValue;
  readonly extentAboveWeb?: MetricValue;
  readonly extentBelowNative?: MetricValue;
  readonly extentBelowWeb?: MetricValue;
  readonly extentLeftNative?: MetricValue;
  readonly extentLeftWeb?: MetricValue;
  readonly extentRightNative?: MetricValue;
  readonly extentRightWeb?: MetricValue;
  readonly offsetXNative?: MetricValue;
  readonly offsetXWeb?: MetricValue;
  readonly offsetYNative?: MetricValue;
  readonly offsetYWeb?: MetricValue;
  readonly centroidOffsetXNative?: MetricValue;
  readonly centroidOffsetXWeb?: MetricValue;
  readonly centroidOffsetYNative?: MetricValue;
  readonly centroidOffsetYWeb?: MetricValue;
  /**
   * The blurred-edge model's Gaussian σ — the blur radius a renderer's shadow
   * takes as a parameter, and the family this bed's profiles are in. This is the
   * figure a shadow mechanism should be fitted against.
   */
  readonly falloffSigmaNative?: MetricValue;
  readonly falloffSigmaWeb?: MetricValue;
  readonly falloffSigmaResidualNative?: MetricValue;
  readonly falloffSigmaResidualWeb?: MetricValue;
  /**
   * The same fit's amplitude at the contour — the strength figure a mechanism is
   * fitted to, separated from σ so "same shadow, dimmer" and "different shadow"
   * are different readings. `strengthPeak*` stays as the raw ring maximum.
   */
  readonly falloffAmplitudeNative?: MetricValue;
  readonly falloffAmplitudeWeb?: MetricValue;
  /**
   * The exponential alternative, fitted over the same points with the same
   * objective and the same free-parameter count — kept so the family question
   * stays answerable from the record rather than by assertion.
   */
  readonly falloffLengthNative?: MetricValue;
  readonly falloffLengthWeb?: MetricValue;
  readonly falloffResidualNative?: MetricValue;
  readonly falloffResidualWeb?: MetricValue;
}

/** Spread one side's optional figure in under its own name, or leave it out. */
function sided(
  suffix: "Native" | "Web",
  values: Readonly<Record<string, number | undefined>>,
  units: Readonly<Record<string, MetricUnits>>,
): Record<string, MetricValue> {
  const out: Record<string, MetricValue> = {};
  for (const [name, value] of Object.entries(values)) {
    const unit = units[name];
    if (value === undefined || unit === undefined) continue;
    out[`${name}${suffix}`] = metricValue(value, unit);
  }
  return out;
}

const SHADOW_FIELD_UNITS: Readonly<Record<string, MetricUnits>> = {
  strengthPeak: "ratio",
  strengthPeakDistance: "px",
  extentAbove: "px",
  extentBelow: "px",
  extentLeft: "px",
  extentRight: "px",
  offsetX: "px",
  offsetY: "px",
  centroidOffsetX: "px",
  centroidOffsetY: "px",
  falloffSigma: "px",
  falloffSigmaResidual: "ratio",
  falloffAmplitude: "ratio",
  falloffLength: "px",
  falloffResidual: "ratio",
};

const shadowFieldValues = (side: ShadowFieldReport): Readonly<Record<string, number | undefined>> => ({
  strengthPeak: side.strengthPeak,
  strengthPeakDistance: side.strengthPeakDistancePx,
  extentAbove: side.extentAbovePx,
  extentBelow: side.extentBelowPx,
  extentLeft: side.extentLeftPx,
  extentRight: side.extentRightPx,
  offsetX: side.offsetXPx,
  offsetY: side.offsetYPx,
  centroidOffsetX: side.centroidOffsetXPx,
  centroidOffsetY: side.centroidOffsetYPx,
  falloffSigma: side.falloffSigmaPx,
  falloffSigmaResidual: side.falloffSigmaResidual,
  falloffAmplitude: side.falloffAmplitude,
  falloffLength: side.falloffLengthPx,
  falloffResidual: side.falloffResidual,
});

/**
 * The exterior, the backdrop level and the backdrop support are properties of
 * the *scene* — the same region and the same backdrop on both sides — so they
 * are reported once rather than as a pair that could disagree with itself.
 */
export function shadowAxisReport(input: {
  readonly native: ShadowFieldReport;
  readonly web: ShadowFieldReport;
}): ShadowAxisReport {
  return {
    axis: "shadow",
    exteriorArea: metricValue(input.native.exteriorAreaPx, "px^2"),
    backdropMeanLuminance: metricValue(input.native.backdropMeanLuminance, "luminance"),
    backdropSupport: metricValue(input.native.backdropSupport, "ratio"),
    clearanceAbove: metricValue(input.native.clearanceAbovePx, "px"),
    clearanceBelow: metricValue(input.native.clearanceBelowPx, "px"),
    clearanceLeft: metricValue(input.native.clearanceLeftPx, "px"),
    clearanceRight: metricValue(input.native.clearanceRightPx, "px"),
    meanDepartureNative: metricValue(input.native.meanDeparture, "luminance"),
    meanDepartureWeb: metricValue(input.web.meanDeparture, "luminance"),
    ...sided("Native", shadowFieldValues(input.native), SHADOW_FIELD_UNITS),
    ...sided("Web", shadowFieldValues(input.web), SHADOW_FIELD_UNITS),
  };
}

export type AxisReport =
  | ShapeAxisReport
  | MaterialAxisReport
  | PerceptualAxisReport
  | MotionAxisReport
  | ShadowAxisReport
  | CoherenceAxisReport;

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
  /** Present wherever a backdrop and a declared region were both available. */
  readonly shadow?: ShadowAxisReport;
  /** Dom-tier cells only, and only where the texture twin was on disk. */
  readonly coherence?: CoherenceAxisReport;
}

/**
 * Bumped only when the on-disk shape changes incompatibly.
 *
 * 2 (C9a): the material axis became two-sided. Its single-image sub-metrics —
 * blur, rim, shadow, interior level — grew required `Native`/`Web` pairs where
 * version 1 carried one unlabelled figure that was in fact the web side only.
 * A version-1 cell cannot be read as a version-2 cell, and silently treating a
 * web-only figure as a comparison is exactly the misreading the bump prevents.
 *
 * 3 (C9a): the shape axis carries each side's extracted silhouette area, so a
 * reader — or a gate — can tell a shape difference from a failure of the
 * extractor to find the shape. See `ShapeAxisReport`.
 *
 * 4 (W1 G3): dom-tier cells carry the `coherence` axis. Through schema 3 the
 * cross-tier bound lived in prose only — it is a web-against-web quantity, and
 * `web-captures/` is not committed, so nothing in the repository held it and no
 * test could fail on it. A version-3 cell cannot be read as a version-4 one
 * because absent coherence means two different things across the bump: "this
 * schema has no such axis" before, "this cell's twin was not on disk" after.
 * See `CoherenceAxisReport`.
 *
 * 5 (post-v1 wave, Decision Log 15): **the instrument became two axes.** Shape
 * extraction is bounded to the declared component region, and the outer shadow
 * became a measured axis of its own. A version-4 cell cannot be read as a
 * version-5 one in either direction, and the reason is not a field list:
 *
 *   - every schema-4 `shape` and `material` figure was measured under a
 *     whole-canvas silhouette that, on the active-pose bed, contained the
 *     reference's shadow as well as its component — native areas at roughly
 *     twice the declared, interior statistics averaged over half-shadowed
 *     backdrop. Reading those beside schema-5 figures as the same quantity is
 *     the specific misreading this bump exists to prevent;
 *   - absent `shadow` means two different things across the bump: "this schema
 *     has no such axis" before, "no backdrop or no declared region was available
 *     for this cell" after.
 *
 * The band-windowed perceptual rows (W13 X6, `ssimBand` / `ssimInterior` and
 * their window counts) are a schema *addition* and do not move this number.
 * The version exists to stop a reader taking two cells as the same quantity
 * when they are not, and nothing here changes an existing quantity: every
 * schema-5 figure is measured exactly as before, the new rows are optional in
 * the same "absent means not measured" sense the axes already use, and no
 * adopted bound reads them until W13 G2 adopts one from the bed. A bump would
 * also widen the deliberate gap between this constant and the committed
 * matrix's own version, which Decision Log 15 ruling 3 (below) pins for an
 * unrelated reason.
 *
 * `results/matrix.json` is deliberately left at schema 4. Decision Log 15 ruling
 * 3 keeps the inactive-bed gate enforced, as the historically-labelled suite,
 * until the one honest post-W8 pass — so the committed matrix and the schema
 * this build writes are different versions on purpose, and
 * `test/adopted-thresholds.test.ts` pins both numbers to say so.
 */
export const RESULT_MATRIX_SCHEMA_VERSION = 5;

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
