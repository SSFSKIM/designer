/**
 * The shadow axis: what the material does to the backdrop it does *not* cover.
 *
 * ## Why this is an axis and not a material sub-metric
 *
 * Through schema 4 the exterior shadow was one radial number on the material
 * axis, profiled outward from the *extracted* silhouette — which, on a reference
 * whose shadow the extractor had already swallowed, started beyond the shadow
 * and measured the bare backdrop. The active-pose bed made the shadow the
 * largest unmodelled facet in the project (claims §5.11: a downward-offset
 * occlusion covering 8.5–29.6% of the canvas, which vitrea renders as exactly
 * zero), and Decision Log 15 ruled it its own measured axis, fitted like any
 * other facet. So it is profiled from the **declared** contour, in four
 * directions, on both sides, with the same estimator.
 *
 * ## The quantity: occlusion, not darkening
 *
 * The reference's shadow is multiplicative — it removes a fraction of the light
 * the backdrop was sending, so the same shadow is a large absolute drop over a
 * bright backdrop and an invisible one over a dark one. Every directional figure
 * here is therefore normalised: `occlusion = (backdrop − rendered) / backdrop`,
 * in linear light. That makes a shadow's *description* comparable across the
 * five backdrops the bed puts the same surface over, which an absolute
 * darkening is not.
 *
 * The normalisation has an analytic floor. Over `dark-solid` (backdrop
 * luminance 0.0117) and `impulse` (0.0037) there is no light to remove, so no
 * shadow of any strength is recoverable — the axis reports its backdrop support
 * and leaves every normalised field **absent**, which is the honest reading and
 * not a zero. `meanDeparture` stays present on every scene because an absolute
 * difference is defined even where a ratio is not, and it is the figure claims
 * §5.11 quoted.
 *
 * ## The falloff is fitted in two families, not one
 *
 * A shadow is a filled shape convolved with a blur kernel, so the profile
 * outside it should be a blurred *edge* — `1 − Φ(d/σ)` — and σ is the parameter
 * a renderer's shadow actually takes. The obvious alternative, an
 * ambient-occlusion-shaped exponential, is a different family with the same
 * number of free parameters, so both are fitted over the same points with the
 * same objective and both residuals are reported. On this bed the blurred edge
 * wins on every cell, by 1.1× to 6.9× in RMS, and returns one σ — about 17.8 pt,
 * doubling in device pixels between 1× and 2× — across every backdrop, span,
 * colour scheme and accessibility state. Reporting the pair rather than the
 * winner is what keeps that a finding instead of an assumption.
 *
 * ## Beside the ratio, the affine pair (W14 X7)
 *
 * Occlusion is a *multiplicative* description, and it was adopted because the
 * reference's shadow looked multiplicative where W8 measured it. It is not the
 * whole shadow. W14 G0 read the reference's exterior as an affine map of the
 * backdrop the capture was taken over, `y = a·bg + c`, and found a lift — `c`
 * about +0.0038 in linear luminance below `checkerboard__rrect-lg__rest`, where
 * vitrea's `c` is 0 (claims §5.62). A ratio `(bg − y)/bg` cannot report a lift
 * on a black square at all: the denominator is the thing that is missing, which
 * is why the axis's backdrop floor exists and why the lift lived outside every
 * number this axis wrote. So the pair is fitted beside the ratio, by least
 * squares over each band's pixels, per direction, in **linear light** — the
 * space matters by an order of magnitude, the same lift reading +0.048 encoded
 * and +0.0038 linear because it sits where the transfer function is steepest —
 * and it is absent, never zero, where the band's backdrop has no contrast to
 * identify it. See `ShadowAffineSample`.
 *
 * ## No thresholds
 *
 * Two constants below select *where a measurement is possible* — the backdrop
 * level beneath which a ratio is arithmetic on no information, and the occlusion
 * level beneath which a ring is indistinguishable from an unshadowed one. They
 * are conditions on the estimator, not bounds on fidelity: nothing here decides
 * whether a shadow matches, and the axis has no adopted bound at all until the
 * cascade fits one after W8.
 */

import { CalibrationError } from "../errors";
import { assertComparable, linearLuminance, type CalibrationImage } from "../image";
import { minimiseGoldenSection, normalCdf } from "../stats";
import type { ComponentRegion } from "../component-region";

/** Which side of the component a ring sample sits on. */
export const SHADOW_DIRECTIONS = ["above", "below", "left", "right"] as const;
export type ShadowDirection = (typeof SHADOW_DIRECTIONS)[number];

/**
 * Backdrop luminance beneath which the multiplicative normalisation is not
 * identifiable, in linear light.
 *
 * 0.05 is a measured separation on this bed rather than a round number: it
 * places `light-solid` (0.891), the checkerboard's light squares (1.0), `photo`
 * (0.214) and `mid-dark-solid` (0.0595) inside the measurable set and
 * `dark-solid` (0.0117) and `impulse` (0.0037) outside it, which is exactly the
 * split the physics implies. At the floor itself a 1% occlusion is about a third
 * of an 8-bit code, so a per-pixel reading there is beneath the capture's
 * resolution and only the ring means below are meaningful.
 */
export const DEFAULT_SHADOW_BACKDROP_FLOOR = 0.05;

/**
 * The occlusion a ring must reach to count as shadowed, as a fraction of the
 * backdrop's own level.
 *
 * 1% is the smallest departure that survives the capture at the backdrop floor
 * once a ring's samples are averaged. It is what "the departure falls below
 * threshold" in the extent definition means, and it is deliberately expressed in
 * the normalised quantity so that the same shadow yields the same extent over
 * every backdrop bright enough to show it.
 */
export const DEFAULT_SHADOW_OCCLUSION_THRESHOLD = 0.01;

/** Fewer samples than this in a ring and the ring is skipped, not averaged. */
const DEFAULT_MIN_RING_SAMPLES = 4;

/**
 * Fraction of the exterior whose backdrop must clear the floor before any
 * normalised figure is reported.
 */
const DEFAULT_MIN_BACKDROP_SUPPORT = 0.1;

/**
 * Fraction of the supported exterior that must carry occlusion above the
 * threshold before the mass centroid is reported.
 *
 * Below it the centroid describes the backdrop's own support pattern rather than
 * the shadow: measured on `checkerboard__capsule-button__rest`, vitrea's 3 px
 * edge halo covers 1.7% of the supported exterior and its centroid lands 39 px
 * from the component's centre — an artefact of which checkerboard squares happen
 * to be light — where the reference's shadow covers 34% and lands 16 px below
 * centre, which is the real displacement.
 */
const DEFAULT_MIN_CENTROID_MASS_FRACTION = 0.1;

/**
 * The band edges the affine pair is fitted over, in CSS px outside the declared
 * contour.
 *
 * These are W14 G0's rings (`results/2026-09-03-w14-shadow/g0/w14lib.py`,
 * `RINGS`), taken verbatim so this axis's pair and claims §5.62's tables can be
 * read side by side without either being re-binned. They are stated in CSS px
 * rather than device px because the reference's shadow is a CSS-px quantity —
 * G0 measured the lift as scale-free to 0.0008 across 1x and 2x — so a band
 * that meant a different physical distance at each scale would make the two
 * scales' rows incomparable.
 *
 * Bands rather than the occlusion profile's unit-wide rings, over the same
 * signed distance field and the same four sectors: an affine pair is two
 * parameters and needs the backdrop to *vary* across the pixels it is fitted
 * over, where a ring mean is one parameter and needs only pixels. A unit ring
 * on one side of a small component holds a few dozen pixels of a pitch-16
 * checkerboard, which is a fit on two or three squares.
 *
 * The list is not a partition. `0-6` overlaps `0-3` and `3-6` deliberately, and
 * it is in G0's list for the same reason it is here: claims §5.60 §3 and §5.62
 * both quote the lift over 0–6 px, and a reader who had to pool two bands to
 * reach it would be re-binning a published number by hand.
 */
export const SHADOW_AFFINE_BANDS_CSS_PX: readonly (readonly [number, number])[] = [
  [0, 3],
  [3, 6],
  [6, 12],
  [12, 24],
  [24, 48],
  [0, 6],
];

/** Fewer pixels than this in a band and the pair is not identified, only the level. */
export const DEFAULT_SHADOW_AFFINE_MIN_SAMPLES = 32;

/**
 * Linear-luminance standard deviation of the backdrop under a band beneath
 * which `a` and `c` are not separable.
 *
 * The design matrix's two columns are collinear on a constant backdrop, so the
 * pair is not identified there at any sample count; 0.02 is G0's `MIN_BG_STD`,
 * and it separates this bed cleanly — a checkerboard band's backdrop standard
 * deviation is about 0.5 and `photo`'s about 0.15, against 0 on every solid.
 * Like the axis's other two constants this selects *where a measurement is
 * possible* and is not a bound on fidelity.
 */
export const DEFAULT_SHADOW_AFFINE_MIN_BACKDROP_STDDEV = 0.02;

export interface ShadowFieldOptions {
  /**
   * Device pixels per CSS px — the profile's backing scale. Only the affine
   * bands read it, because they are the one part of this axis defined in CSS px
   * (`SHADOW_AFFINE_BAND_EDGES_CSS_PX`); everything else here is in device px
   * and says so in its name. Defaults to 1, which is the identity for a 1x
   * capture and makes the option invisible to every caller that does not care.
   */
  readonly scale?: number;
  readonly backdropFloor?: number;
  readonly occlusionThreshold?: number;
  readonly minRingSamples?: number;
  readonly minBackdropSupport?: number;
  readonly minCentroidMassFraction?: number;
  readonly affineMinSamples?: number;
  readonly affineMinBackdropStdDev?: number;
}

/** One ring of the occlusion profile, indexed by distance from the contour. */
export interface ShadowProfileSample {
  /** Inner edge of the one-pixel ring, in pixels outside the declared contour. */
  readonly distancePx: number;
  /** Mean occlusion over the ring's supported pixels, 0..1. */
  readonly occlusion: number;
  readonly sampleCount: number;
}

/**
 * One band's affine map of the backdrop, `y = a·bg + c`, in **linear
 * luminance**, on one side of the component.
 *
 * The pair complements the occlusion ratio rather than replacing it. Occlusion
 * says what fraction of the backdrop's light the render removed and is blind to
 * anything the render *added*; `a` is that same transmission read as a slope,
 * and `c` is the part occlusion cannot express — light that arrived from a term
 * which is not a multiply. A pure black multiply gives `c = 0` and
 * `a = 1 − occlusion` exactly, which is what vitrea's own shadow reads back
 * (claims §5.62, X4).
 *
 * Every field whose name ends in `Linear` is in linear luminance, the space the
 * charter binds and this axis already normalises in. The same fit run on the
 * encoded values would return a `c` an order of magnitude larger and would mean
 * something else — the amplitude a `box-shadow` or a premultiplied canvas
 * composites — so the space is in the name and not only in a comment.
 *
 * Optional fields mean **not identifiable in this band**, never zero:
 *
 *   - `slopeALinear`, `interceptCLinear` and `rSquared` are absent together
 *     where the band's backdrop standard deviation is below
 *     `DEFAULT_SHADOW_AFFINE_MIN_BACKDROP_STDDEV` — a solid backdrop makes the
 *     two columns of the design matrix collinear, so `a` and `c` trade off
 *     freely along a line and no amount of data separates them — or where the
 *     band holds fewer than `DEFAULT_SHADOW_AFFINE_MIN_SAMPLES` pixels.
 *     `unidentifiableReason` says which. On a solid the honest reading is the
 *     one quantity that *is* identified there, so `renderedLevelLinear` and
 *     `backdropMeanLinear` are reported and the pair is left out: their ratio
 *     is `a + c/bg` and nothing in the band decides the split.
 *   - `rSquared` is absent on its own where the band's rendered values are
 *     constant, because the total sum of squares it normalises by is zero.
 *
 * A band with no exterior pixel at all is not emitted, which is the frame
 * having eaten it rather than a reading.
 */
export interface ShadowAffineSample {
  /** One of the axis's four sectors, or `"all"` for the four pooled. */
  readonly direction: ShadowDirection | "all";
  /** The band's own name, e.g. `"6-12"`, in CSS px — G0's labels. */
  readonly ringLabel: string;
  readonly innerDistanceCssPx: number;
  readonly outerDistanceCssPx: number;
  readonly sampleCount: number;
  readonly backdropMeanLinear: number;
  /** Population standard deviation of the backdrop — what identifies the pair. */
  readonly backdropStdDevLinear: number;
  /** Mean rendered luminance over the band. Present wherever the band is. */
  readonly renderedLevelLinear: number;
  /** `a`: the transmission the band applies to its backdrop. */
  readonly slopeALinear?: number;
  /** `c`: the light the band adds independently of its backdrop — the lift. */
  readonly interceptCLinear?: number;
  /** Coefficient of determination of that fit, so a reader can weigh the pair. */
  readonly rSquared?: number;
  /** Why the pair is absent, when it is. */
  readonly unidentifiableReason?: string;
}

/**
 * One side's shadow, measured outside the declared component region.
 *
 * Optional fields mean **not identifiable on this scene**, never zero:
 *
 *   - everything normalised is absent when the backdrop cannot support a ratio
 *     (`backdropSupport` says how far short it fell);
 *   - `extent*` is absent on a side whose walk runs into the canvas edge, because
 *     what it would report there is the size of the window and not the reach of
 *     the shadow — `clearance*` is the window it ran out of;
 *   - `offset*` is absent when no direction reached the occlusion threshold at
 *     all, which is what a renderer that draws no shadow produces — an undefined
 *     displacement, recorded as undefined rather than as (0, 0) — and absent per
 *     pair when either of that pair's two sides is truncated;
 *   - `centroidOffset*` is absent when too little of the exterior is occluded
 *     for a mass centroid to describe the shadow rather than the backdrop;
 *   - each falloff pair is absent when fewer than three rings past ring 0 clear
 *     the threshold, or when that family's fit lands on an impossible amplitude
 *     or a sub-pixel scale.
 */
export interface ShadowFieldReport {
  /** Pixels outside the declared region — the population every figure is over. */
  readonly exteriorAreaPx: number;
  /** Mean backdrop luminance over that exterior, linear light. */
  readonly backdropMeanLuminance: number;
  /** Fraction of the exterior whose backdrop clears the floor, 0..1. */
  readonly backdropSupport: number;
  /**
   * Mean `backdrop − rendered` over the whole exterior, linear light, signed.
   * Absolute, so it is defined over every backdrop; negative means the side
   * *brightens* its surround on balance.
   */
  readonly meanDeparture: number;
  /** Deepest ring-mean occlusion, and where it sits. */
  readonly strengthPeak?: number;
  readonly strengthPeakDistancePx?: number;
  readonly extentAbovePx?: number;
  readonly extentBelowPx?: number;
  readonly extentLeftPx?: number;
  readonly extentRightPx?: number;
  /**
   * Distance from the declared contour to the canvas edge on each side, device
   * px — the measuring window itself, always present.
   *
   * Reported because it is the datum the truncation rule is decided on: an
   * extent that is absent beside a clearance of 20 says "the shadow was still
   * going when the capture ended 20 px out", where absence alone would not
   * distinguish that from a scene with no shadow to measure.
   */
  readonly clearanceAbovePx: number;
  readonly clearanceBelowPx: number;
  readonly clearanceLeftPx: number;
  readonly clearanceRightPx: number;
  /**
   * Sides whose extent walk reached the canvas edge, in the order of
   * `SHADOW_DIRECTIONS`; empty when the window held the whole departure.
   *
   * Non-empty is a caveat on the *pooled* figures too, not just on the sides it
   * names: rings past a truncated side's clearance are averaged over an
   * incomplete annulus, which pulls `falloffSigmaPx` toward the window. Measured
   * on this bed at roughly 8% low for a σ ≈ 17 px shadow read through a 20 px
   * margin. The pooled figures are still reported — a biased σ with its bias
   * named is worth more than a hole — but a fit that takes σ as ground truth
   * should exclude cells where this is non-empty.
   */
  readonly truncatedSides: readonly ShadowDirection[];
  /** Displacement implied by the reach: half the difference of opposing extents. */
  readonly offsetXPx?: number;
  readonly offsetYPx?: number;
  /** Occlusion-mass centroid minus the component's centre, device px. */
  readonly centroidOffsetXPx?: number;
  readonly centroidOffsetYPx?: number;
  /**
   * Gaussian blur radius of the blurred-edge model, in pixels — the parameter a
   * renderer's shadow takes, and on this bed the family the profile is actually
   * in. Read `falloffSigmaResidual` beside it.
   */
  readonly falloffSigmaPx?: number;
  readonly falloffSigmaResidual?: number;
  /**
   * The blurred-edge model's occlusion at the declared contour.
   *
   * The amplitude half of the same fit, and the honest strength figure: it is
   * estimated from the profile beyond the body's own edge ring, where
   * `strengthPeak` is a raw ring maximum that the edge — or an accessibility
   * border — can capture. Separating it from σ is what lets a difference between
   * two cells be read as "same shadow, dimmer" or "different shadow".
   */
  readonly falloffAmplitude?: number;
  /**
   * Exponential decay length, in pixels, fitted over the same points with the
   * same objective and the same number of free parameters. Kept as the
   * falsifier: two families with two residuals let the profile say which one it
   * is in, where one family with one residual only says how well that one did.
   */
  readonly falloffLengthPx?: number;
  readonly falloffResidual?: number;
  /** The ring means the figures above are read off. */
  readonly profile: readonly ShadowProfileSample[];
  /**
   * The affine pair per band and direction (W14 X7), recorded beside the
   * occlusion and never gating it.
   *
   * Present even where `unmeasurableReason` is set and the whole normalised
   * block is absent, which is the point: over `impulse` and `dark-solid` there
   * is no light to remove and no ratio to report, and those are exactly the
   * backdrops on which a lift is measured cleanly, because a multiply is inert
   * over black and whatever light sits there arrived from something else.
   */
  readonly affine: readonly ShadowAffineSample[];
  /** Why the normalised block is absent, when it is. */
  readonly unmeasurableReason?: string;
}

/** Sector of the exterior a pixel belongs to, by its own aspect-normalised angle. */
function directionOf(region: ComponentRegion, x: number, y: number): ShadowDirection {
  // Normalising by the component's own half-extents puts the sector boundaries
  // on the diagonals of its bounding box, so "beside" a wide capsule is the
  // region past its caps rather than a sliver level with its flat edges — which
  // an unnormalised angle would give, leaving the cap surrounds in no sector.
  const nx = (x + 0.5 - region.centreX) / region.halfWidth;
  const ny = (y + 0.5 - region.centreY) / region.halfHeight;
  if (Math.abs(nx) >= Math.abs(ny)) return nx < 0 ? "left" : "right";
  return ny < 0 ? "above" : "below";
}

/**
 * How far the departure reaches in one direction, in pixels from the declared
 * contour: the outermost ring of a qualifying *adjacent pair*.
 *
 * A pair rather than a first crossing, because the innermost ring is where each
 * side's own edge lives and it can read anything — the reference's rim spills
 * one pixel past the contour on `photo__capsule-button__rest` and reads −0.276
 * there, which a first-crossing rule would report as a shadow of zero extent —
 * while requiring two consecutive rings keeps one noisy far ring from inventing
 * reach.
 *
 * The pair is strict in both directions. A lone qualifying ring 0 is exactly the
 * edge-halo case the rule exists to reject, so the walk starts *unqualified*
 * rather than crediting ring 0 with a phantom predecessor; and an unmeasurable
 * ring breaks adjacency rather than being stepped over, since two rings either
 * side of a gap are not evidence that the departure was continuous across it.
 * A side with no shadow reads 0, which is a measurement.
 */
function extentOf(means: readonly (number | undefined)[], threshold: number): number {
  let extent = 0;
  let previousQualified = false;
  for (let ring = 0; ring < means.length; ring += 1) {
    const mean = means[ring];
    if (mean === undefined) {
      previousQualified = false;
      continue;
    }
    const qualified = mean >= threshold;
    if (qualified && previousQualified) extent = ring + 1;
    previousQualified = qualified;
  }
  return extent;
}

/**
 * How far the exterior runs before the capture ends, per side, in pixels from
 * the declared contour.
 *
 * The minimum over the whole border line rather than the distance at its middle:
 * the frame comes closest to the contour somewhere along that line, and that is
 * where the walk runs out of pixels first.
 */
function clearanceOf(
  region: ComponentRegion,
  width: number,
  height: number,
): Map<ShadowDirection, number> {
  const at = (x: number, y: number): number => region.signedDistancePx[y * width + x] ?? 0;
  let above = Number.POSITIVE_INFINITY;
  let below = Number.POSITIVE_INFINITY;
  for (let x = 0; x < width; x += 1) {
    above = Math.min(above, at(x, 0));
    below = Math.min(below, at(x, height - 1));
  }
  let left = Number.POSITIVE_INFINITY;
  let right = Number.POSITIVE_INFINITY;
  for (let y = 0; y < height; y += 1) {
    left = Math.min(left, at(0, y));
    right = Math.min(right, at(width - 1, y));
  }
  // Negative where the declared region overruns the frame: there is no exterior
  // on that side at all, which is a clearance of zero and truncation of anything.
  return new Map<ShadowDirection, number>([
    ["above", Math.max(0, above)],
    ["below", Math.max(0, below)],
    ["left", Math.max(0, left)],
    ["right", Math.max(0, right)],
  ]);
}

/** Below one pixel a falloff describes the raster, not the material. */
const RASTER_SCALE_FLOOR_PX = 1;

/** A falloff model fitted to the occlusion profile, and how well it describes it. */
interface FalloffFit {
  /** The model's scale parameter, in pixels. */
  readonly scalePx: number;
  /** Fitted amplitude at the declared contour, in occlusion. */
  readonly amplitude: number;
  /** RMS residual as a fraction of the profile's peak — how right the family is. */
  readonly residual: number;
}

/**
 * The rings a falloff is fitted over: from **ring 1** outward, while the
 * occlusion clears the threshold.
 *
 * Ring 0 is excluded on principle rather than by taste. It is the one ring that
 * belongs to the body's own edge as much as to the shadow — antialiasing, the
 * specular rim, and under `increased-contrast` a hard border stroke that reads
 * 0.560 occlusion against a shadow of 0.096 one pixel further out. Anchoring a
 * falloff there fits the border instead of the shadow: with ring 0 in, the two
 * accessibility profiles return a blur scale under a pixel and a residual forty
 * times the rest of the bed's; with it out they return the same σ as every other
 * profile. `strengthPeak` still reports the raw maximum over every ring, with
 * its distance, so the spike itself stays visible.
 */
function falloffPoints(
  profile: readonly ShadowProfileSample[],
  threshold: number,
): readonly ShadowProfileSample[] {
  return profile.filter((sample) => sample.distancePx >= 1 && sample.occlusion > threshold);
}

/**
 * Least squares in the data domain, with the amplitude solved in closed form.
 *
 * Both families are `amplitude × shape(distance / scale)` with the amplitude
 * entering linearly through the origin, so for any trial scale the best
 * amplitude has a one-line solution and the search is one-dimensional. That is
 * what makes the two fits *comparable*: same points, same objective, two free
 * parameters each, so the residuals decide which family the profile is in
 * rather than the parameter count deciding it for them.
 */
function fitScaledShape(
  points: readonly ShadowProfileSample[],
  peak: number,
  shape: (distance: number, scale: number) => number,
  searchTo: number,
): FalloffFit | undefined {
  if (points.length < 3 || peak <= 0 || searchTo <= RASTER_SCALE_FLOOR_PX) return undefined;

  const amplitudeFor = (scale: number): number => {
    let numerator = 0;
    let denominator = 0;
    for (const point of points) {
      const basis = shape(point.distancePx, scale);
      numerator += basis * point.occlusion;
      denominator += basis * basis;
    }
    return denominator > 0 ? numerator / denominator : 0;
  };
  const rmsAt = (scale: number): number => {
    const amplitude = amplitudeFor(scale);
    let squares = 0;
    for (const point of points) {
      squares += (amplitude * shape(point.distancePx, scale) - point.occlusion) ** 2;
    }
    return Math.sqrt(squares / points.length);
  };

  const scalePx = minimiseGoldenSection(rmsAt, RASTER_SCALE_FLOOR_PX, searchTo);
  const amplitude = amplitudeFor(scalePx);

  // Two refusals, both physical rather than tuned. An amplitude above 1 would
  // have the material removing more light than the backdrop emits, which is the
  // signature of a degenerate fit trading amplitude against scale on a truncated
  // tail; and a scale at the raster floor describes the grid, not the shadow.
  if (!Number.isFinite(scalePx) || !Number.isFinite(amplitude)) return undefined;
  if (amplitude > 1 || scalePx <= RASTER_SCALE_FLOOR_PX * 1.001) return undefined;

  return { scalePx, amplitude, residual: rmsAt(scalePx) / peak };
}

/**
 * The blurred-edge model: `amplitude × (1 − Φ(distance / σ))`.
 *
 * This is what a shadow *is* — a filled shape convolved with a Gaussian — so σ
 * is the blur radius a renderer is given, and `box-shadow` and a GPU shadow pass
 * both take exactly that parameter. The shadow's own edge is pinned to the
 * declared contour rather than fitted, which keeps the model at two free
 * parameters and, more importantly, keeps it identified: only the tail beyond
 * the component is visible, and with a free edge position the amplitude, the
 * offset and σ trade against one another along a valley. The price of pinning it
 * is that σ absorbs the shadow's spread and the spread of its own directional
 * offset, so it reads somewhat above the blur radius a renderer would be given.
 */
const blurredEdgeShape = (distance: number, sigma: number): number => 1 - normalCdf(distance / sigma);

/** The ambient-occlusion-shaped alternative: `amplitude × e^(−distance/λ)`. */
const exponentialShape = (distance: number, length: number): number => Math.exp(-distance / length);

/**
 * Fit `y = a·bg + c` over one band's pixels by ordinary least squares.
 *
 * The closed form rather than a solver: two parameters through a mean-centred
 * design have a one-line solution, and writing it out keeps the identifiability
 * condition visible — the denominator is the backdrop's own variance, which is
 * the quantity a solid backdrop sets to zero.
 */
function fitAffineBand(
  rendered: readonly number[],
  backdrop: readonly number[],
): { slope: number; intercept: number; rSquared?: number } {
  const n = rendered.length;
  let backdropMean = 0;
  let renderedMean = 0;
  for (let i = 0; i < n; i += 1) {
    backdropMean += backdrop[i] ?? 0;
    renderedMean += rendered[i] ?? 0;
  }
  backdropMean /= n;
  renderedMean /= n;

  let covariance = 0;
  let variance = 0;
  for (let i = 0; i < n; i += 1) {
    const db = (backdrop[i] ?? 0) - backdropMean;
    covariance += db * ((rendered[i] ?? 0) - renderedMean);
    variance += db * db;
  }
  const slope = variance > 0 ? covariance / variance : 0;
  const intercept = renderedMean - slope * backdropMean;

  let residualSquares = 0;
  let totalSquares = 0;
  for (let i = 0; i < n; i += 1) {
    const fitted = slope * (backdrop[i] ?? 0) + intercept;
    residualSquares += ((rendered[i] ?? 0) - fitted) ** 2;
    totalSquares += ((rendered[i] ?? 0) - renderedMean) ** 2;
  }
  // A band whose render is constant has no variation for the fit to explain, so
  // the ratio R² normalises by is 0/0. Absent is the reading; a 1 there would
  // say the model described something.
  return totalSquares > 0
    ? { slope, intercept, rSquared: 1 - residualSquares / totalSquares }
    : { slope, intercept };
}

/**
 * The affine pair over every band and direction, plus the four pooled.
 *
 * One pass over the exterior collecting each band's pixels, then one fit each.
 * The distance field and the sectors are the axis's own — the same
 * `signedDistancePx` the occlusion rings are cut from and the same
 * `directionOf` — so the pair sits over the pixels whose occlusion it
 * complements; only the binning differs, and `SHADOW_AFFINE_BAND_EDGES_CSS_PX`
 * says why.
 *
 * The backdrop floor is deliberately **not** applied. It is a condition on a
 * ratio, and this is not one: a fit over a dark backdrop is exactly as
 * identified as a fit over a bright one so long as the backdrop varies, and the
 * dark backdrops are where a lift shows up alone.
 */
function affineBands(
  rendered: Float64Array,
  backdrop: Float64Array,
  region: ComponentRegion,
  width: number,
  height: number,
  scale: number,
  minSamples: number,
  minBackdropStdDev: number,
): readonly ShadowAffineSample[] {
  const bands = SHADOW_AFFINE_BANDS_CSS_PX;
  const bandCount = bands.length;
  const groups: ("all" | ShadowDirection)[] = ["all", ...SHADOW_DIRECTIONS];
  const renderedBy = new Map<string, number[]>();
  const backdropBy = new Map<string, number[]>();
  const keyOf = (group: string, band: number): string => `${group}:${band}`;
  for (const group of groups) {
    for (let band = 0; band < bandCount; band += 1) {
      renderedBy.set(keyOf(group, band), []);
      backdropBy.set(keyOf(group, band), []);
    }
  }

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = y * width + x;
      if ((region.silhouette.mask[i] ?? 0) !== 0) continue;
      const distanceCssPx = (region.signedDistancePx[i] ?? 0) / scale;
      const value = rendered[i] ?? 0;
      const base = backdrop[i] ?? 0;
      const direction = directionOf(region, x, y);
      for (let band = 0; band < bandCount; band += 1) {
        const edges = bands[band];
        if (edges === undefined) continue;
        if (distanceCssPx < edges[0] || distanceCssPx >= edges[1]) continue;
        for (const group of ["all", direction] as const) {
          renderedBy.get(keyOf(group, band))?.push(value);
          backdropBy.get(keyOf(group, band))?.push(base);
        }
      }
    }
  }

  const out: ShadowAffineSample[] = [];
  for (const group of groups) {
    for (let band = 0; band < bandCount; band += 1) {
      const ys = renderedBy.get(keyOf(group, band)) ?? [];
      const bgs = backdropBy.get(keyOf(group, band)) ?? [];
      const n = ys.length;
      if (n === 0) continue;

      let backdropMean = 0;
      let renderedMean = 0;
      for (let i = 0; i < n; i += 1) {
        backdropMean += bgs[i] ?? 0;
        renderedMean += ys[i] ?? 0;
      }
      backdropMean /= n;
      renderedMean /= n;
      let variance = 0;
      for (let i = 0; i < n; i += 1) variance += ((bgs[i] ?? 0) - backdropMean) ** 2;
      const stdDev = Math.sqrt(variance / n);

      const [inner, outer] = bands[band] ?? [0, 0];
      const common = {
        direction: group,
        ringLabel: `${inner}-${outer}`,
        innerDistanceCssPx: inner,
        outerDistanceCssPx: outer,
        sampleCount: n,
        backdropMeanLinear: backdropMean,
        backdropStdDevLinear: stdDev,
        renderedLevelLinear: renderedMean,
      } as const;

      if (n < minSamples) {
        out.push({
          ...common,
          unidentifiableReason:
            `${n} pixels in this band, fewer than the ${minSamples} an affine pair is fitted over — ` +
            `the frame runs out before the outer bands do on the large spans, and a fit on a handful ` +
            `of pixels describes the corner of the capture rather than the shadow.`,
        });
        continue;
      }
      if (stdDev < minBackdropStdDev) {
        out.push({
          ...common,
          unidentifiableReason:
            `the backdrop's standard deviation over this band is ${stdDev.toFixed(4)} linear, below ` +
            `${minBackdropStdDev}, so a and c are collinear and only the level ` +
            `${renderedMean.toFixed(4)} over a backdrop of ${backdropMean.toFixed(4)} is identified.`,
        });
        continue;
      }

      const fit = fitAffineBand(ys, bgs);
      out.push({
        ...common,
        slopeALinear: fit.slope,
        interceptCLinear: fit.intercept,
        ...(fit.rSquared === undefined ? {} : { rSquared: fit.rSquared }),
      });
    }
  }
  return out;
}

/**
 * Measure one render's occlusion of its own backdrop, outside the declared
 * component region.
 *
 * Both sides of a cell are measured by this same function over the same region
 * and the same backdrop, so "the gap" is a difference of like quantities — the
 * rule the material axis learned in C9a and the reason its sub-metrics are
 * two-sided.
 */
export function shadowField(
  image: CalibrationImage,
  background: CalibrationImage,
  region: ComponentRegion,
  options: ShadowFieldOptions = {},
): ShadowFieldReport {
  assertComparable(image, background, "shadowField");
  const { width, height } = image;
  if (region.silhouette.width !== width || region.silhouette.height !== height) {
    throw new CalibrationError(
      "dimension-mismatch",
      `shadowField: a ${region.silhouette.width}x${region.silhouette.height} region cannot bound a ` +
        `${width}x${height} capture.`,
    );
  }

  const floor = options.backdropFloor ?? DEFAULT_SHADOW_BACKDROP_FLOOR;
  const threshold = options.occlusionThreshold ?? DEFAULT_SHADOW_OCCLUSION_THRESHOLD;
  const minRingSamples = options.minRingSamples ?? DEFAULT_MIN_RING_SAMPLES;
  const minSupport = options.minBackdropSupport ?? DEFAULT_MIN_BACKDROP_SUPPORT;
  const minMass = options.minCentroidMassFraction ?? DEFAULT_MIN_CENTROID_MASS_FRACTION;
  const scale = options.scale ?? 1;
  const affineMinSamples = options.affineMinSamples ?? DEFAULT_SHADOW_AFFINE_MIN_SAMPLES;
  const affineMinStdDev = options.affineMinBackdropStdDev ?? DEFAULT_SHADOW_AFFINE_MIN_BACKDROP_STDDEV;

  const rendered = linearLuminance(image);
  const backdrop = linearLuminance(background);

  let exteriorCount = 0;
  let supportedCount = 0;
  let backdropSum = 0;
  let departureSum = 0;
  let maxRing = 0;
  for (let i = 0; i < rendered.length; i += 1) {
    if ((region.silhouette.mask[i] ?? 0) !== 0) continue;
    exteriorCount += 1;
    const base = backdrop[i] ?? 0;
    backdropSum += base;
    departureSum += base - (rendered[i] ?? 0);
    if (base >= floor) {
      supportedCount += 1;
      const ring = Math.floor(region.signedDistancePx[i] ?? 0);
      if (ring > maxRing) maxRing = ring;
    }
  }
  if (exteriorCount === 0) {
    throw new CalibrationError(
      "empty-region",
      "shadowField: the declared region covers the whole capture, so there is no exterior to profile.",
    );
  }

  const clearance = clearanceOf(region, width, height);
  // Fitted before the backdrop-support gate below, not after it. The gate is a
  // condition on the ratio and the pair is not one, and the scenes the gate
  // turns away — `impulse`, `dark-solid` — are the ones on which a lift is
  // identified alone, because a multiply removes nothing from a black pixel.
  const affine = affineBands(
    rendered,
    backdrop,
    region,
    width,
    height,
    scale,
    affineMinSamples,
    affineMinStdDev,
  );
  const base: ShadowFieldReport = {
    exteriorAreaPx: exteriorCount,
    backdropMeanLuminance: backdropSum / exteriorCount,
    backdropSupport: supportedCount / exteriorCount,
    meanDeparture: departureSum / exteriorCount,
    clearanceAbovePx: clearance.get("above") ?? 0,
    clearanceBelowPx: clearance.get("below") ?? 0,
    clearanceLeftPx: clearance.get("left") ?? 0,
    clearanceRightPx: clearance.get("right") ?? 0,
    truncatedSides: [],
    profile: [],
    affine,
  };
  if (base.backdropSupport < minSupport) {
    return {
      ...base,
      unmeasurableReason:
        `only ${(base.backdropSupport * 100).toFixed(1)}% of the exterior has a backdrop above ` +
        `${floor} linear luminance, so an occlusion ratio is not identifiable here — a shadow removes a ` +
        `fraction of the light behind it, and over this backdrop there is none to remove.`,
    };
  }

  // Ring means, pooled over the whole exterior and again per direction. Rings
  // are unit-wide and indexed by the floor of the exact distance to the declared
  // contour, so ring 0 is the first pixel outside it.
  const ringSum = new Float64Array(maxRing + 1);
  const ringCount = new Float64Array(maxRing + 1);
  const directionSum = new Map<ShadowDirection, Float64Array>();
  const directionCount = new Map<ShadowDirection, Float64Array>();
  for (const direction of SHADOW_DIRECTIONS) {
    directionSum.set(direction, new Float64Array(maxRing + 1));
    directionCount.set(direction, new Float64Array(maxRing + 1));
  }

  let mass = 0;
  let massCount = 0;
  let massX = 0;
  let massY = 0;
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = y * width + x;
      if ((region.silhouette.mask[i] ?? 0) !== 0) continue;
      const level = backdrop[i] ?? 0;
      if (level < floor) continue;
      const occlusion = (level - (rendered[i] ?? 0)) / level;
      const ring = Math.floor(region.signedDistancePx[i] ?? 0);
      if (ring < 0 || ring > maxRing) continue;

      ringSum[ring] = (ringSum[ring] ?? 0) + occlusion;
      ringCount[ring] = (ringCount[ring] ?? 0) + 1;
      const direction = directionOf(region, x, y);
      const sums = directionSum.get(direction);
      const counts = directionCount.get(direction);
      if (sums && counts) {
        sums[ring] = (sums[ring] ?? 0) + occlusion;
        counts[ring] = (counts[ring] ?? 0) + 1;
      }

      const weight = occlusion - threshold;
      if (weight > 0) {
        mass += weight;
        massCount += 1;
        massX += weight * (x + 0.5);
        massY += weight * (y + 0.5);
      }
    }
  }

  const meansOf = (sums: Float64Array, counts: Float64Array): (number | undefined)[] =>
    [...counts].map((count, ring) =>
      count >= minRingSamples ? (sums[ring] ?? 0) / count : undefined,
    );

  const pooled = meansOf(ringSum, ringCount);
  const profile: ShadowProfileSample[] = [];
  for (let ring = 0; ring <= maxRing; ring += 1) {
    const mean = pooled[ring];
    if (mean === undefined) continue;
    profile.push({ distancePx: ring, occlusion: mean, sampleCount: ringCount[ring] ?? 0 });
  }
  if (profile.length === 0) {
    return {
      ...base,
      unmeasurableReason:
        `no ring outside the declared region holds ${minRingSamples} supported samples, so no ` +
        `occlusion profile exists.`,
    };
  }

  let peakIndex = 0;
  for (let i = 1; i < profile.length; i += 1) {
    if ((profile[i]?.occlusion ?? 0) > (profile[peakIndex]?.occlusion ?? 0)) peakIndex = i;
  }
  const peak = profile[peakIndex] as ShadowProfileSample;

  const extents = new Map<ShadowDirection, number>();
  for (const direction of SHADOW_DIRECTIONS) {
    const sums = directionSum.get(direction);
    const counts = directionCount.get(direction);
    extents.set(direction, sums && counts ? extentOf(meansOf(sums, counts), threshold) : 0);
  }
  const above = extents.get("above") ?? 0;
  const below = extents.get("below") ?? 0;
  const left = extents.get("left") ?? 0;
  const right = extents.get("right") ?? 0;
  const reached = Math.max(above, below, left, right) > 0;

  // A walk that was still qualifying at the frame's own reach did not end there
  // — the capture did. Reporting the number it stopped on would be a measurement
  // of the window wearing the shadow's name, so the side goes absent instead.
  //
  // The test is on the ring that *ends* the walk, not on the last one that
  // qualified: an extent of `e` says ring `e` failed to qualify, so ring `e` is
  // the reading the number rests on. Rings are unit-wide and span `[e, e + 1)`,
  // so that ring is whole only while `e + 1 ≤ clearance`; past there the frame
  // has begun to eat the annulus the mean is taken over, and a ring missing the
  // part of itself nearest the shadow is exactly the ring that stops a walk
  // early. One ring of guard band, derived from the ring's own width rather
  // than chosen.
  const truncatedSides = SHADOW_DIRECTIONS.filter(
    (direction) => (extents.get(direction) ?? 0) + 1 > (clearance.get(direction) ?? 0),
  );
  const truncated = new Set<ShadowDirection>(truncatedSides);

  // Both families over the same points, the same objective and the same two free
  // parameters, so the pair of residuals is a comparison rather than two
  // unrelated numbers. The search runs to twice the profile's own reach, which
  // is well past any scale that could describe it.
  const points = falloffPoints(profile, threshold);
  const searchTo = 2 * Math.max(...profile.map((sample) => sample.distancePx), RASTER_SCALE_FLOOR_PX);
  const gaussian = fitScaledShape(points, peak.occlusion, blurredEdgeShape, searchTo);
  const exponential = fitScaledShape(points, peak.occlusion, exponentialShape, searchTo);
  const massFraction = supportedCount > 0 ? massCount / supportedCount : 0;

  return {
    ...base,
    strengthPeak: peak.occlusion,
    strengthPeakDistancePx: peak.distancePx,
    ...(truncated.has("above") ? {} : { extentAbovePx: above }),
    ...(truncated.has("below") ? {} : { extentBelowPx: below }),
    ...(truncated.has("left") ? {} : { extentLeftPx: left }),
    ...(truncated.has("right") ? {} : { extentRightPx: right }),
    truncatedSides,
    ...(reached && !truncated.has("left") && !truncated.has("right")
      ? { offsetXPx: (right - left) / 2 }
      : {}),
    ...(reached && !truncated.has("above") && !truncated.has("below")
      ? { offsetYPx: (below - above) / 2 }
      : {}),
    ...(mass > 0 && massFraction >= minMass
      ? {
          centroidOffsetXPx: massX / mass - region.centreX,
          centroidOffsetYPx: massY / mass - region.centreY,
        }
      : {}),
    ...(gaussian === undefined
      ? {}
      : {
          falloffSigmaPx: gaussian.scalePx,
          falloffSigmaResidual: gaussian.residual,
          falloffAmplitude: gaussian.amplitude,
        }),
    ...(exponential === undefined
      ? {}
      : { falloffLengthPx: exponential.scalePx, falloffResidual: exponential.residual }),
    profile,
    affine,
  };
}
