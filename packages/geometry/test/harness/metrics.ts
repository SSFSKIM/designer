/**
 * Error measurement in the optical band, and the shape matrix it runs over.
 * Ported from `spikes/s2-geometry-field/src/{metrics,sweep}.ts`.
 *
 * Two quantities matter, because the optics read two different things off the
 * field:
 *   - field VALUE error, in px       -> where the rim sits, how wide it reads
 *   - field GRADIENT direction, in degrees -> which way refraction bends
 *
 * Sub-bands are reported separately because rim lighting reads a much thinner
 * band than refraction does.
 *
 * Two properties of the measurement are worth keeping in mind when reading the
 * numbers, both inherited from S2:
 *
 *  - The reported **max is locally refined** by pattern search over (segment,
 *    parameter, offset) from the worst grid samples, so it is the continuous
 *    field's real worst case rather than the worst point that happened to be
 *    sampled.
 *  - **p95 is aggregated as the worst shape's p95** over a contour-uniform x
 *    offset-uniform measure. That measure over-weights corners relative to area,
 *    which is the right bias for a rim (a contour-length quantity) and a
 *    conservative one for the value statistic.
 */

import { type Contour, segmentCurvature, segmentNormal, segmentPoint } from "../../src/contour";
import { buildReferenceContour } from "../../src/contour";
import { type FieldParams, centralGradient, rsupnFieldAndGradient } from "../../src/field";
import { halfExtents, type Vec2 } from "../../src/channels";
import { fieldParams, type ResolvedShape, resolveFromChannels } from "../../src/shape";
import { uniformRadii } from "../../src/channels";
import {
  angleDeg,
  type BandOptions,
  DEFAULT_BAND,
  inwardReach,
  sampleBand,
} from "./truth";

/** The band half-widths S2 reports, in px. */
export const SUB_BANDS = [1, 4, 8] as const;

export interface BandStats {
  readonly half: number;
  readonly n: number;
  readonly valueMax: number;
  readonly valueP95: number;
  readonly gradMaxDeg: number;
  readonly gradP95Deg: number;
  /** max |grad| deviation from 1 — the eikonal defect */
  readonly eikonalMax: number;
  /** fraction of samples sitting on a C1 kink of the field */
  readonly kinkFraction: number;
}

export interface MeasureResult {
  readonly bands: readonly BandStats[];
  readonly radius: number;
  readonly reach: number;
  readonly smoothingEff: number;
}

function percentile(sorted: readonly number[], q: number): number {
  if (sorted.length === 0) return 0;
  const i = Math.min(sorted.length - 1, Math.max(0, Math.ceil(q * sorted.length) - 1));
  return sorted[i] as number;
}

export interface MeasureOptions {
  readonly band?: BandOptions;
  /** finite-difference step as a fraction of the radius, for `central` */
  readonly gradStepFrac?: number;
  readonly refineTop?: number;
}

/**
 * Measure one shape. `evaluate` and `gradientAt` are passed the shape-local
 * point, matching how the field is actually called.
 */
export function measureShape(
  shape: ResolvedShape,
  contour: Contour,
  evaluate: (p: FieldParams, x: number, y: number) => number,
  gradientAt: (p: FieldParams, x: number, y: number, h: number) => { gx: number; gy: number; kink: boolean },
  opts: MeasureOptions = {},
): MeasureResult {
  const band = opts.band ?? DEFAULT_BAND;
  const { halfW, halfH } = halfExtents(shape.channels.size);
  const prep = fieldParams(shape);
  const h = Math.max(1e-6, (opts.gradStepFrac ?? 1e-3) * Math.max(shape.corner.radius, 1));

  interface Rec {
    absd: number;
    ve: number;
    ge: number;
    kink: boolean;
    eik: number;
  }
  const recs: Rec[] = [];

  for (const s of sampleBand(contour, halfW, halfH, band)) {
    const fv = evaluate(prep, s.P.x, s.P.y);
    const g = gradientAt(prep, s.P.x, s.P.y, h);
    const mag = Math.hypot(g.gx, g.gy);
    recs.push({
      absd: Math.abs(s.d),
      ve: Math.abs(fv - s.d),
      ge: mag > 0 ? angleDeg({ x: g.gx, y: g.gy }, s.grad) : 90,
      kink: g.kink,
      eik: Math.abs(mag - 1),
    });
  }

  const bands: BandStats[] = [];
  for (const half of SUB_BANDS) {
    if (half > band.halfBand) continue;
    const inBand = recs.filter((r) => r.absd <= half + 1e-12);
    const vals = inBand.map((r) => r.ve).sort((a, b) => a - b);
    const nonKink = inBand.filter((r) => !r.kink);
    const grads = nonKink.map((r) => r.ge).sort((a, b) => a - b);

    const sampled = vals.length ? (vals[vals.length - 1] as number) : 0;
    const refined = refineMaxValueError(
      prep,
      contour,
      halfW,
      halfH,
      half,
      evaluate,
      opts.refineTop ?? 24,
    );

    bands.push({
      half,
      n: inBand.length,
      valueMax: Math.max(sampled, refined),
      valueP95: percentile(vals, 0.95),
      gradMaxDeg: grads.length ? (grads[grads.length - 1] as number) : 0,
      gradP95Deg: percentile(grads, 0.95),
      eikonalMax: nonKink.reduce((a, r) => Math.max(a, r.eik), 0),
      kinkFraction: inBand.length ? (inBand.length - nonKink.length) / inBand.length : 0,
    });
  }

  return {
    bands,
    radius: shape.corner.radius,
    reach: shape.corner.reach,
    smoothingEff: shape.corner.smoothingEff,
  };
}

/**
 * Pattern search in (segment, t, offset) space from the worst grid samples, so
 * the reported max is the field's real worst case and not a sampling artifact.
 *
 * Inward offsets past the medial axis break the "distance == offset" identity, so
 * they are excluded from the search domain exactly as the band sampler excludes
 * them.
 */
function refineMaxValueError(
  prep: FieldParams,
  contour: Contour,
  halfW: number,
  halfH: number,
  half: number,
  evaluate: (p: FieldParams, x: number, y: number) => number,
  topN: number,
): number {
  const segs = contour.segments;

  const inLimit = (i: number, t: number): number => {
    const s = segs[i]!;
    return Math.min(half, 0.98 * inwardReach(halfW, halfH, segmentPoint(s, t), segmentCurvature(s, t)));
  };

  const errAt = (i: number, t: number, delta: number): number => {
    const s = segs[i]!;
    const b = segmentPoint(s, t);
    const n = segmentNormal(s, t);
    return Math.abs(evaluate(prep, b.x + n.x * delta, b.y + n.y * delta) - delta);
  };

  const seeds: { i: number; t: number; delta: number; err: number }[] = [];
  for (let i = 0; i < segs.length; i++) {
    // Straight edges are exact for both families by construction.
    if ((segs[i] as { kind: string }).kind === "line") continue;
    const n = 96;
    for (let k = 0; k <= n; k++) {
      const t = k / n;
      const lim = inLimit(i, t);
      for (const d of [-lim, -lim * 0.5, 0, half * 0.5, half]) {
        seeds.push({ i, t, delta: d, err: errAt(i, t, d) });
      }
    }
  }
  seeds.sort((a, b) => b.err - a.err);

  let best = 0;
  for (const seed of seeds.slice(0, topN)) {
    let t = seed.t;
    let delta = seed.delta;
    let cur = errAt(seed.i, t, delta);
    let stepT = 1 / 96;
    let stepD = half / 4;
    for (let it = 0; it < 300; it++) {
      let improved = false;
      for (const dt of [stepT, -stepT]) {
        const nt = Math.min(1, Math.max(0, t + dt));
        const nd = Math.max(-inLimit(seed.i, nt), delta);
        const e = errAt(seed.i, nt, nd);
        if (e > cur) {
          t = nt;
          delta = nd;
          cur = e;
          improved = true;
        }
      }
      for (const dd of [stepD, -stepD]) {
        const nd = Math.min(half, Math.max(-inLimit(seed.i, t), delta + dd));
        const e = errAt(seed.i, t, nd);
        if (e > cur) {
          delta = nd;
          cur = e;
          improved = true;
        }
      }
      if (!improved) {
        stepT *= 0.5;
        stepD *= 0.5;
        if (stepT < 1e-10 && stepD < 1e-10) break;
      }
    }
    best = Math.max(best, cur);
  }
  return best;
}

// ---------------------------------------------------------------------------
// the matrix
// ---------------------------------------------------------------------------

/** The full S2 matrix: 6 x 6 x 3 x 3 = 324 shapes. */
export const SMOOTHINGS = [0, 0.2, 0.4, 0.6, 0.8, 1.0] as const;
export const SIZES = [16, 32, 64, 120, 320, 600] as const;
export const ASPECTS = [1, 3, 8] as const;
/** radius as a fraction of the short dimension; 0.5 is the capsule limit */
export const R_FRACS = [0.15, 0.3, 0.5] as const;

export interface MatrixEntry {
  readonly size: number;
  readonly aspect: number;
  readonly rFrac: number;
  readonly smoothing: number;
}

/**
 * A shape on the Figma smoothing axis — the axis the declared bound is measured
 * on. `size` is the SHORT dimension; width is `size * aspect`.
 */
export function matrixShape(entry: MatrixEntry): ResolvedShape {
  const size: Vec2 = [entry.size * entry.aspect, entry.size];
  const radius = entry.rFrac * entry.size;
  return resolveFromChannels(
    {
      center: [0, 0],
      size,
      radii: uniformRadii(radius),
      smoothing: entry.smoothing,
      thickness: 0,
    },
    "figma-smoothing",
  );
}

export function fullMatrix(): MatrixEntry[] {
  const out: MatrixEntry[] = [];
  for (const smoothing of SMOOTHINGS) {
    for (const size of SIZES) {
      for (const aspect of ASPECTS) {
        for (const rFrac of R_FRACS) out.push({ size, aspect, rFrac, smoothing });
      }
    }
  }
  return out;
}

/**
 * A representative slice: every smoothing, both ends of the size range, the
 * extreme aspect, and the capsule limit. Fast enough for every CI run; the full
 * 324-shape matrix runs behind `VITREA_FULL_MATRIX=1`.
 */
export function representativeMatrix(): MatrixEntry[] {
  const out: MatrixEntry[] = [];
  for (const smoothing of SMOOTHINGS) {
    out.push({ size: 32, aspect: 1, rFrac: 0.15, smoothing });
    out.push({ size: 120, aspect: 3, rFrac: 0.15, smoothing });
    out.push({ size: 600, aspect: 1, rFrac: 0.15, smoothing });
    out.push({ size: 64, aspect: 8, rFrac: 0.3, smoothing });
    out.push({ size: 320, aspect: 1, rFrac: 0.5, smoothing }); // capsule limit
  }
  return out;
}

export interface Aggregate {
  readonly n: number;
  readonly valueMax: number;
  readonly valueP95: number;
  readonly gradMaxDeg: number;
  readonly gradP95Deg: number;
  readonly eikonalMax: number;
}

/**
 * Aggregate across shapes: max of maxima, and the worst shape's p95 (see the
 * module note on why p95 aggregates that way).
 */
export function aggregate(results: readonly MeasureResult[], half: number): Aggregate {
  let valueMax = 0;
  let valueP95 = 0;
  let gradMaxDeg = 0;
  let gradP95Deg = 0;
  let eikonalMax = 0;
  let n = 0;
  for (const r of results) {
    const b = r.bands.find((x) => x.half === half);
    if (!b) continue;
    n++;
    valueMax = Math.max(valueMax, b.valueMax);
    valueP95 = Math.max(valueP95, b.valueP95);
    gradMaxDeg = Math.max(gradMaxDeg, b.gradMaxDeg);
    gradP95Deg = Math.max(gradP95Deg, b.gradP95Deg);
    eikonalMax = Math.max(eikonalMax, b.eikonalMax);
  }
  return { n, valueMax, valueP95, gradMaxDeg, gradP95Deg, eikonalMax };
}

/** The reference contour for a matrix shape, which is the ground truth. */
export function referenceContourFor(shape: ResolvedShape): Contour {
  const { halfW, halfH } = halfExtents(shape.channels.size);
  return buildReferenceContour(halfW, halfH, shape.corner);
}

/** Gradient accessors matching the three shipping options. */
export const GRADIENTS = {
  analytic: (p: FieldParams, x: number, y: number): { gx: number; gy: number; kink: boolean } => {
    const s = rsupnFieldAndGradient(p, x, y);
    return { gx: s.gx, gy: s.gy, kink: s.kink };
  },
  central:
    (field: (p: FieldParams, x: number, y: number) => number) =>
    (p: FieldParams, x: number, y: number, h: number): { gx: number; gy: number; kink: boolean } =>
      centralGradient(field, p, x, y, h),
} as const;
