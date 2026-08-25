/**
 * The numeric primitives every axis shares: order statistics, affine
 * least-squares, and the Gaussian integral.
 *
 * They live together because they are the places where a metric could quietly
 * become dishonest. A percentile computed by a different interpolation rule
 * shifts every reported p95; a slope fitted through a constant is arithmetic on
 * no information; an `erf` approximation with a loose error bound puts a floor
 * under every blur-sigma residual. Each one is therefore pinned here once, with
 * its definition stated, rather than re-derived per metric.
 */

import { CalibrationError } from "./errors";

/**
 * The standard summary this package reports for any pixel-wise population.
 * Metrics report the whole set rather than picking one, because which of these
 * matters is a per-claim question and answering it here would be tuning.
 */
export interface Aggregate {
  readonly count: number;
  readonly min: number;
  readonly max: number;
  readonly mean: number;
  readonly p95: number;
  readonly rms: number;
}

/**
 * Linear-interpolated percentile on an already-sorted ascending sample, the
 * "type 7" definition (NumPy's and R's default): the rank is `q * (n - 1)` and
 * fractional ranks interpolate between neighbours. Stated because p95 of a few
 * hundred boundary pixels moves visibly between the competing definitions.
 */
export function percentileOfSorted(sorted: ArrayLike<number>, q: number): number {
  if (sorted.length === 0) {
    throw new CalibrationError("empty-region", "percentileOfSorted: no samples to take a percentile of.");
  }
  const rank = q * (sorted.length - 1);
  const low = Math.floor(rank);
  const high = Math.ceil(rank);
  const loValue = sorted[low] ?? 0;
  if (low === high) return loValue;
  const hiValue = sorted[high] ?? 0;
  return loValue + (hiValue - loValue) * (rank - low);
}

/** Summarise a population. Copies and sorts, so the input is untouched. */
export function aggregate(values: ArrayLike<number>, context = "aggregate"): Aggregate {
  const count = values.length;
  if (count === 0) {
    throw new CalibrationError("empty-region", `${context}: no samples to summarise.`);
  }

  let sum = 0;
  let sumSquares = 0;
  const sorted = new Float64Array(count);
  for (let i = 0; i < count; i += 1) {
    const value = values[i] ?? 0;
    sorted[i] = value;
    sum += value;
    sumSquares += value * value;
  }
  sorted.sort();

  return {
    count,
    min: sorted[0] ?? 0,
    max: sorted[count - 1] ?? 0,
    mean: sum / count,
    p95: percentileOfSorted(sorted, 0.95),
    rms: Math.sqrt(sumSquares / count),
  };
}

/** An affine fit `y ≈ slope * x + offset` and how much of `y` it explains. */
export interface LinearFit {
  readonly slope: number;
  readonly offset: number;
  /** Coefficient of determination, 1 for an exact fit. */
  readonly r2: number;
  readonly sampleCount: number;
}

/**
 * Ordinary least squares, returning `null` when the independent variable does
 * not vary. That case is a real one for calibration — a solid-colour backdrop
 * scene has a constant backdrop luminance — and it carries no information about
 * a transfer slope, so it must not come back as a number.
 */
export function tryLinearFit(x: ArrayLike<number>, y: ArrayLike<number>): LinearFit | null {
  const n = Math.min(x.length, y.length);
  if (n < 2) return null;

  let sumX = 0;
  let sumY = 0;
  for (let i = 0; i < n; i += 1) {
    sumX += x[i] ?? 0;
    sumY += y[i] ?? 0;
  }
  const meanX = sumX / n;
  const meanY = sumY / n;

  let sxx = 0;
  let sxy = 0;
  let syy = 0;
  for (let i = 0; i < n; i += 1) {
    const dx = (x[i] ?? 0) - meanX;
    const dy = (y[i] ?? 0) - meanY;
    sxx += dx * dx;
    sxy += dx * dy;
    syy += dy * dy;
  }
  // A spread below the float noise floor of the mean is not spread: summing
  // thousands of identical samples leaves a ~1e-16 relative wobble, which would
  // otherwise pass `sxx > 0` and produce a slope fitted to rounding error.
  if (Math.sqrt(sxx / n) <= 1e-9 * (Math.abs(meanX) + 1)) return null;

  const slope = sxy / sxx;
  const offset = meanY - slope * meanX;

  let residualSquares = 0;
  for (let i = 0; i < n; i += 1) {
    const predicted = slope * (x[i] ?? 0) + offset;
    const residual = (y[i] ?? 0) - predicted;
    residualSquares += residual * residual;
  }
  // A constant `y` is explained exactly by a zero slope; calling that r² = 0
  // would be reporting failure on a perfect fit.
  const r2 = syy > 0 ? 1 - residualSquares / syy : residualSquares === 0 ? 1 : 0;

  return { slope, offset, r2, sampleCount: n };
}

/** `tryLinearFit`, refusing a degenerate fit instead of returning null. */
export function linearFit(x: ArrayLike<number>, y: ArrayLike<number>, context = "linearFit"): LinearFit {
  const fit = tryLinearFit(x, y);
  if (!fit) {
    throw new CalibrationError(
      "degenerate-fit",
      `${context}: the independent variable does not vary over ${x.length} sample(s), so no slope is identifiable. ` +
        `A constant-luminance backdrop cannot measure a transfer function — use a ramp, photo or checkerboard scene.`,
    );
  }
  return fit;
}

/**
 * Abramowitz & Stegun 7.1.26, maximum absolute error 1.5e-7 over the whole
 * real line. That bound sits three orders of magnitude below the residuals the
 * edge-spread fit reports on real captures, so the approximation is not a term
 * in any measurement.
 */
export function erf(x: number): number {
  const sign = x < 0 ? -1 : 1;
  const z = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * z);
  const poly =
    t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  return sign * (1 - poly * Math.exp(-z * z));
}

/** Standard normal CDF, the analytic edge-spread function of a Gaussian blur. */
export function normalCdf(z: number): number {
  return 0.5 * (1 + erf(z / Math.SQRT2));
}

/**
 * Golden-section minimisation of a unimodal scalar objective on a bracket.
 * Deterministic and derivative-free, which is what the edge-spread fit wants:
 * its objective is a least-squares residual over a quantised profile, so a
 * gradient method would be chasing quantisation steps.
 */
export function minimiseGoldenSection(
  objective: (value: number) => number,
  low: number,
  high: number,
  iterations = 60,
): number {
  const invPhi = (Math.sqrt(5) - 1) / 2;
  let a = low;
  let b = high;
  let c = b - invPhi * (b - a);
  let d = a + invPhi * (b - a);
  let fc = objective(c);
  let fd = objective(d);

  for (let i = 0; i < iterations; i += 1) {
    if (fc < fd) {
      b = d;
      d = c;
      fd = fc;
      c = b - invPhi * (b - a);
      fc = objective(c);
    } else {
      a = c;
      c = d;
      fc = fd;
      d = a + invPhi * (b - a);
      fd = objective(d);
    }
  }
  return (a + b) / 2;
}
