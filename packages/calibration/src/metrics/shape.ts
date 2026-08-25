/**
 * The shape axis: is the surface *where* and *shaped how* the reference is?
 *
 * Three numbers that fail in different ways on purpose. IoU is a global area
 * agreement and is nearly blind to a one-pixel contour offset on a large
 * surface. Contour distance sees exactly that offset and is blind to whether
 * the corner curve has the right *profile*. Corner curvature sees the profile
 * and nothing else. Reporting one of them would let a squircle that is the
 * wrong squircle pass as a match, which is the specific failure this axis
 * exists to catch.
 *
 * No threshold appears here. Every function returns pixels, ratios, or inverse
 * pixels, and what counts as close enough is C9's to decide per tier.
 */

import { CalibrationError } from "../errors";
import {
  assertSameGrid,
  boundaryMask,
  distanceToSeeds,
  sampleContourAt,
  traceContour,
  type ContourPath,
  type Silhouette,
} from "../silhouette";
import { aggregate } from "../stats";

/**
 * Intersection over union of two silhouettes, in 0..1. 1 is identical
 * coverage; two disjoint silhouettes give 0.
 *
 * Two empty silhouettes are refused rather than called a perfect match — a
 * scene where neither side rendered anything is a harness failure, and 1.0 is
 * the most misleading number available.
 */
export function silhouetteIoU(a: Silhouette, b: Silhouette): number {
  assertSameGrid(a, b, "silhouetteIoU");

  let intersection = 0;
  let union = 0;
  for (let i = 0; i < a.mask.length; i += 1) {
    const inA = (a.mask[i] ?? 0) !== 0;
    const inB = (b.mask[i] ?? 0) !== 0;
    if (inA && inB) intersection += 1;
    if (inA || inB) union += 1;
  }
  if (union === 0) {
    throw new CalibrationError(
      "empty-region",
      "silhouetteIoU: both silhouettes are empty — nothing rendered on either side, which is not a match.",
    );
  }
  return intersection / union;
}

/** Symmetric contour distance, all four statistics in pixels. */
export interface ContourDistanceReport {
  /** Symmetric Hausdorff distance: the worst boundary point on either side. */
  readonly maxPx: number;
  readonly p95Px: number;
  readonly meanPx: number;
  readonly rmsPx: number;
  /** Boundary pixels pooled from both sides — the population behind the stats. */
  readonly sampleCount: number;
}

/**
 * Distance between two silhouette boundaries, measured both ways and pooled.
 *
 * Symmetry is not decoration: the one-sided distance from A to B is small
 * whenever A's contour lies *inside* B's, so a surface that is uniformly too
 * small scores well one way round and badly the other. Pooling both directions
 * makes `maxPx` the true Hausdorff distance and keeps the mean from hiding a
 * one-sided shrink.
 *
 * Distances come from an exact Euclidean distance transform between pixel
 * centres (see `squaredEuclideanDistanceTransform`); the grid is the floor, so
 * sub-0.5px figures mean "within the raster", not "measured".
 */
export function contourDistance(a: Silhouette, b: Silhouette): ContourDistanceReport {
  assertSameGrid(a, b, "contourDistance");

  const boundaryA = boundaryMask(a);
  const boundaryB = boundaryMask(b);
  const distanceToA = distanceToSeeds(boundaryA, a.width, a.height);
  const distanceToB = distanceToSeeds(boundaryB, b.width, b.height);

  const samples: number[] = [];
  for (let i = 0; i < boundaryA.length; i += 1) {
    if ((boundaryA[i] ?? 0) !== 0) samples.push(distanceToB[i] ?? 0);
    if ((boundaryB[i] ?? 0) !== 0) samples.push(distanceToA[i] ?? 0);
  }
  if (samples.length === 0) {
    throw new CalibrationError(
      "empty-region",
      "contourDistance: neither silhouette has a boundary — both are empty.",
    );
  }

  const stats = aggregate(samples, "contourDistance");
  return {
    maxPx: stats.max,
    p95Px: stats.p95,
    meanPx: stats.mean,
    rmsPx: stats.rms,
    sampleCount: stats.count,
  };
}

/** How the curvature profile is sampled and where "corner" starts. */
export interface CornerCurvatureOptions {
  /**
   * Equally spaced arc-length samples around each contour. The default gives
   * roughly sub-pixel spacing on a several-hundred-pixel perimeter.
   */
  readonly sampleCount?: number;
  /**
   * Scale of the Gaussian the contour is smoothed at, in pixels. This is the
   * single knob that trades rasterisation noise against corner resolution: see
   * the estimator note below.
   */
  readonly smoothingSigmaPx?: number;
  /**
   * A sample is "in a corner region" when curvature there is at least this
   * fraction of the peak curvature. A region selector, not a pass criterion.
   */
  readonly cornerFraction?: number;
}

/** Curvature sampled at equal arc-length intervals around a closed contour. */
export interface CurvatureProfile {
  /** Unsigned curvature in 1/px, one entry per equally spaced sample. */
  readonly curvature: Float64Array;
  readonly perimeterPx: number;
  readonly smoothingSigmaPx: number;
}

const DEFAULT_SAMPLE_COUNT = 512;
const DEFAULT_SMOOTHING_SIGMA_PX = 3;
const DEFAULT_CORNER_FRACTION = 0.5;

/**
 * Curvature from Gaussian-smoothed contour derivatives.
 *
 * ## The estimator, and why not a simpler one
 *
 * The contour is resampled at equal steps, then `x(s)` and `y(s)` are
 * differentiated by convolution with the first and second derivatives of a
 * Gaussian of scale σ, and curvature comes from the parameterisation-invariant
 * form `|x'y'' - y'x''| / (x'² + y'²)^(3/2)` — the classic curvature-scale-space
 * estimator.
 *
 * Two properties are why it has to be this rather than a three-point stencil.
 * First, a rasterised contour is a *staircase*: every sampled point sits up to
 * half a pixel off the true curve, and that error is concentrated at the pixel
 * frequency. A three-point estimator (Menger curvature, finite differences)
 * has no attenuation at that frequency at all — measured on a radius-40 disc,
 * whose true curvature is 0.025 1/px, a 3px Menger stencil reports a mean of
 * 0.052, i.e. the *noise is twice the signal*. A Gaussian at the default
 * σ = 3px brings the same disc back to 0.0276.
 *
 * Second, the staircase is *longer* than the curve it approximates — about 5%
 * on that disc — so its arc length is not the true arc length, and the run
 * lengths that cause the inflation vary around the shape. The invariant form
 * above divides that out; any estimator that assumes a unit-speed
 * parameterisation does not.
 *
 * The sign is dropped: a signed curvature would encode the traversal direction
 * of the trace, which is not a property of the shape being compared.
 *
 * ## Accuracy, bias, and the noise floor
 *
 * Measured against rasterised ground truth at the default σ = 3px:
 *
 *   - A radius-40 disc (true curvature 0.025 1/px) comes back at a mean of
 *     0.0276 — about 10% high, from smoothing a curve whose sampled boundary
 *     sits a fraction of a pixel inside the true circle.
 *   - The **peak** curvature at a rounded-rect corner overshoots badly: 0.065
 *     against a true 0.042 at radius 24. This is real and expected. The corner
 *     joins its straight edge at a curvature *step*, and smoothing a curvature
 *     step rings, the same way any low-pass filter does. So the peak is
 *     reported for context, and the *characteristic* corner curvature — the
 *     median inside the corner region — is the number to read: it lands within
 *     about 12% of `1/r` across radii from 8px to 24px.
 *   - The floor is set by the worst rasterisation case, a 45° staircase, where
 *     true curvature is 0: median about 0.0002 1/px, p80 about 0.006. An
 *     axis-aligned edge measures essentially 0.
 *
 * The headline output of `cornerCurvature` is a *difference* between two
 * contours put through this identical pipeline, and every bias above is shared
 * by both sides and therefore largely cancels there. That is why the biases can
 * be documented rather than corrected: correcting them would mean fitting a
 * model of the raster, which is a worse thing to depend on than a bias that
 * subtracts out.
 *
 * Smoothing rounds real corners as well as fake ones: σ = 3px resolves corner
 * radii down to roughly 6-8px and progressively flattens anything tighter.
 * Lower σ and raise `sampleCount` to chase a tighter corner, and expect the
 * floor to rise steeply as you do — at σ = 1px the disc above reads 0.10, four
 * times its true curvature.
 */
export function contourCurvature(silhouette: Silhouette, options: CornerCurvatureOptions = {}): CurvatureProfile {
  const path = traceContour(silhouette);
  return curvatureOfPath(path, options);
}

function curvatureOfPath(path: ContourPath, options: CornerCurvatureOptions): CurvatureProfile {
  const sampleCount = options.sampleCount ?? DEFAULT_SAMPLE_COUNT;
  const sigma = options.smoothingSigmaPx ?? DEFAULT_SMOOTHING_SIGMA_PX;
  const perimeter = path.perimeterPx;
  if (perimeter <= 0 || sampleCount < 8 || sigma <= 0) {
    throw new CalibrationError(
      "empty-region",
      `contourCurvature: a ${perimeter.toFixed(2)}px contour sampled ${sampleCount} times at σ=${sigma} carries no curvature.`,
    );
  }

  const step = perimeter / sampleCount;
  const xs = new Float64Array(sampleCount);
  const ys = new Float64Array(sampleCount);
  for (let i = 0; i < sampleCount; i += 1) {
    const point = sampleContourAt(path, i * step);
    xs[i] = point.x;
    ys[i] = point.y;
  }

  // Derivative-of-Gaussian kernels, sampled at the resampling step and scaled
  // by it so the convolutions approximate the continuous derivatives. Truncated
  // at 4σ, where the Gaussian has under 1e-4 of its mass left.
  const radius = Math.max(1, Math.min(Math.floor((sampleCount - 1) / 2), Math.ceil((4 * sigma) / step)));
  const firstKernel = new Float64Array(2 * radius + 1);
  const secondKernel = new Float64Array(2 * radius + 1);
  for (let k = -radius; k <= radius; k += 1) {
    const s = k * step;
    const g = Math.exp(-(s * s) / (2 * sigma * sigma)) / (sigma * Math.sqrt(2 * Math.PI));
    firstKernel[k + radius] = ((-s / (sigma * sigma)) * g) * step;
    secondKernel[k + radius] = (((s * s - sigma * sigma) / sigma ** 4) * g) * step;
  }

  const curvature = new Float64Array(sampleCount);
  for (let i = 0; i < sampleCount; i += 1) {
    let dx = 0;
    let dy = 0;
    let ddx = 0;
    let ddy = 0;
    for (let k = -radius; k <= radius; k += 1) {
      // The contour is a loop, so the convolution wraps rather than padding.
      const index = (((i - k) % sampleCount) + sampleCount) % sampleCount;
      const x = xs[index] ?? 0;
      const y = ys[index] ?? 0;
      const w1 = firstKernel[k + radius] ?? 0;
      const w2 = secondKernel[k + radius] ?? 0;
      dx += w1 * x;
      dy += w1 * y;
      ddx += w2 * x;
      ddy += w2 * y;
    }
    const speed = dx * dx + dy * dy;
    curvature[i] = speed > 0 ? Math.abs(dx * ddy - dy * ddx) / Math.pow(speed, 1.5) : 0;
  }

  return { curvature, perimeterPx: perimeter, smoothingSigmaPx: sigma };
}

/** Curvature agreement, in 1/px, over the corner regions and overall. */
export interface CornerCurvatureReport {
  /** Worst absolute curvature difference inside a corner region, 1/px. */
  readonly cornerMaxDeltaPerPx: number;
  readonly cornerP95DeltaPerPx: number;
  /** The same statistics over the whole contour, for context. */
  readonly overallMaxDeltaPerPx: number;
  readonly overallP95DeltaPerPx: number;
  /**
   * Characteristic corner curvature of each contour, 1/px: the median inside
   * that contour's own corner region. This is the unbiased reading of "how
   * tight are the corners" — within ~12% of `1/r` on rasterised ground truth.
   */
  readonly cornerCurvaturePerPxA: number;
  readonly cornerCurvaturePerPxB: number;
  /**
   * Peak curvature each contour reached, 1/px. Biased high near the
   * arc-to-straight junction by the smoothing — context, not a measurement of
   * corner radius.
   */
  readonly peakCurvaturePerPxA: number;
  readonly peakCurvaturePerPxB: number;
  readonly cornerSampleCount: number;
  readonly sampleCount: number;
  readonly smoothingSigmaPx: number;
  readonly perimeterPxA: number;
  readonly perimeterPxB: number;
}

/** Median curvature among the samples at or above `fraction` of the peak. */
function characteristicCornerCurvature(profile: CurvatureProfile, fraction: number): number {
  let peak = 0;
  for (const value of profile.curvature) peak = Math.max(peak, value);
  const region: number[] = [];
  for (const value of profile.curvature) {
    if (value >= peak * fraction) region.push(value);
  }
  region.sort((left, right) => left - right);
  return region[Math.floor(region.length / 2)] ?? 0;
}

/**
 * Compare two contours' curvature, concentrating on the corners.
 *
 * The two contours are aligned by *normalised arc length* from each one's
 * canonical start (see `traceContour`), which assumes the two silhouettes are
 * the same nominal shape at the same nominal position. That is exactly the
 * calibration setup — native and web renders of the same scene over the same
 * raster background — and it is why this metric is a comparison of profiles
 * rather than a registration problem. A gross positional or rotational
 * mismatch will show up as a large contour distance first; read that number
 * before trusting this one.
 *
 * A perimeter difference between the two shows up in `perimeterPxA/B`: the
 * normalised alignment absorbs it, so a large gap there means the curvature
 * samples are being compared at slightly different places along the shape.
 */
export function cornerCurvature(
  a: Silhouette,
  b: Silhouette,
  options: CornerCurvatureOptions = {},
): CornerCurvatureReport {
  assertSameGrid(a, b, "cornerCurvature");

  const sampleCount = options.sampleCount ?? DEFAULT_SAMPLE_COUNT;
  const cornerFraction = options.cornerFraction ?? DEFAULT_CORNER_FRACTION;
  const profileA = contourCurvature(a, { ...options, sampleCount });
  const profileB = contourCurvature(b, { ...options, sampleCount });

  let peakA = 0;
  let peakB = 0;
  for (let i = 0; i < sampleCount; i += 1) {
    peakA = Math.max(peakA, profileA.curvature[i] ?? 0);
    peakB = Math.max(peakB, profileB.curvature[i] ?? 0);
  }
  const peak = Math.max(peakA, peakB);
  const cutoff = peak * cornerFraction;

  const allDeltas = new Float64Array(sampleCount);
  const cornerDeltas: number[] = [];
  for (let i = 0; i < sampleCount; i += 1) {
    const ka = profileA.curvature[i] ?? 0;
    const kb = profileB.curvature[i] ?? 0;
    const delta = Math.abs(ka - kb);
    allDeltas[i] = delta;
    if (Math.max(ka, kb) >= cutoff) cornerDeltas.push(delta);
  }

  const overall = aggregate(allDeltas, "cornerCurvature(overall)");
  // A perfect circle has uniform curvature, so the corner selector can take
  // every sample; it can never take none, because the peak sample qualifies.
  const corner = aggregate(cornerDeltas, "cornerCurvature(corners)");

  return {
    cornerMaxDeltaPerPx: corner.max,
    cornerP95DeltaPerPx: corner.p95,
    overallMaxDeltaPerPx: overall.max,
    overallP95DeltaPerPx: overall.p95,
    cornerCurvaturePerPxA: characteristicCornerCurvature(profileA, cornerFraction),
    cornerCurvaturePerPxB: characteristicCornerCurvature(profileB, cornerFraction),
    peakCurvaturePerPxA: peakA,
    peakCurvaturePerPxB: peakB,
    cornerSampleCount: corner.count,
    sampleCount,
    smoothingSigmaPx: profileA.smoothingSigmaPx,
    perimeterPxA: profileA.perimeterPx,
    perimeterPxB: profileB.perimeterPx,
  };
}
