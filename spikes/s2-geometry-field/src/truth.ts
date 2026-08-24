/**
 * Ground truth for the continuous-corner contour: exact signed distance and
 * exact field gradient.
 *
 * Two independent paths, deliberately:
 *
 *  1. `exactSignedDistance(contour, P)` -- the general solver. Closed form for
 *     lines and arcs; for cubics, dense seeding plus Newton refinement on
 *     d/dt |C(t) - P|^2 = 0, which converges to machine precision. This is the
 *     "dense adaptive sampling + Newton refinement on a grid" reference.
 *
 *  2. `sampleBand(contour, ...)` -- the efficient band sampler. Points are
 *     generated as `contourPoint + delta * outwardNormal`, so the ground-truth
 *     distance is exactly `delta` and the ground-truth gradient is exactly that
 *     normal, with no solver in the loop. Valid while |delta| stays below the
 *     local medial-axis reach, which the sampler enforces and the tests verify
 *     against path 1.
 *
 * The true signed distance field has |grad d| = 1 and grad d(P) equals the
 * outward unit normal at the closest contour point -- inside as well as
 * outside. That identity is what makes path 2 exact.
 */

import {
  type Contour,
  type Segment,
  type Vec2,
  dot,
  len,
  norm,
  segCurvature,
  segDeriv,
  segDeriv2,
  segLength,
  segNormal,
  segPoint,
  sub,
} from './contour.js';

export interface ClosestResult {
  /** signed distance: negative inside, positive outside */
  d: number;
  /** unsigned distance to the contour */
  dist: number;
  /** closest point on the contour */
  point: Vec2;
  /** exact field gradient == outward unit normal at the closest point */
  grad: Vec2;
  segIndex: number;
  t: number;
}

function closestOnLine(s: Extract<Segment, { kind: 'line' }>, P: Vec2): number {
  const dir = sub(s.p1, s.p0);
  const l2 = dot(dir, dir);
  if (l2 === 0) return 0;
  const t = dot(sub(P, s.p0), dir) / l2;
  return Math.max(0, Math.min(1, t));
}

function closestOnArc(s: Extract<Segment, { kind: 'arc' }>, P: Vec2): number {
  const rel = sub(P, s.center);
  if (rel.x === 0 && rel.y === 0) return 0.5;
  const ang = Math.atan2(rel.y, rel.x);
  // Solve a0 + sweep*t == ang (mod 2pi) for t in [0, 1].
  let delta = ang - s.a0;
  // Bring delta into the same rotational sense as sweep.
  if (s.sweep < 0) {
    while (delta > 0) delta -= 2 * Math.PI;
    while (delta < s.sweep - 2 * Math.PI + 1e-15) delta += 2 * Math.PI;
  } else {
    while (delta < 0) delta += 2 * Math.PI;
    while (delta > s.sweep + 2 * Math.PI - 1e-15) delta -= 2 * Math.PI;
  }
  const t = delta / s.sweep;
  if (t >= 0 && t <= 1) return t;
  // Outside the angular span: the closest point is whichever endpoint is nearer.
  const d0 = len(sub(P, segPoint(s, 0)));
  const d1 = len(sub(P, segPoint(s, 1)));
  return d0 <= d1 ? 0 : 1;
}

const CUBIC_SEEDS = 48;

function closestOnCubic(s: Extract<Segment, { kind: 'cubic' }>, P: Vec2): number {
  // Seed with a dense sweep, then Newton-refine every local minimum.
  const vals = new Array<number>(CUBIC_SEEDS + 1);
  for (let i = 0; i <= CUBIC_SEEDS; i++) {
    const t = i / CUBIC_SEEDS;
    const q = segPoint(s, t);
    const dx = q.x - P.x;
    const dy = q.y - P.y;
    vals[i] = dx * dx + dy * dy;
  }

  let bestT = 0;
  let bestV = Infinity;

  const consider = (seedT: number) => {
    let t = seedT;
    for (let it = 0; it < 64; it++) {
      const C = segPoint(s, t);
      const D1 = segDeriv(s, t);
      const D2 = segDeriv2(s, t);
      const e = sub(C, P);
      const g = 2 * dot(e, D1); // dF/dt
      const h = 2 * (dot(D1, D1) + dot(e, D2)); // d2F/dt2
      if (!Number.isFinite(g) || !Number.isFinite(h)) break;
      let step = h > 0 ? g / h : g / Math.max(1e-30, dot(D1, D1) * 2);
      // Damp runaway steps.
      if (!Number.isFinite(step)) break;
      const maxStep = 0.25;
      if (step > maxStep) step = maxStep;
      if (step < -maxStep) step = -maxStep;
      const next = Math.max(0, Math.min(1, t - step));
      if (Math.abs(next - t) < 1e-16) {
        t = next;
        break;
      }
      t = next;
    }
    const q = segPoint(s, t);
    const dx = q.x - P.x;
    const dy = q.y - P.y;
    const vv = dx * dx + dy * dy;
    if (vv < bestV) {
      bestV = vv;
      bestT = t;
    }
  };

  // endpoints always
  consider(0);
  consider(1);
  for (let i = 1; i < CUBIC_SEEDS; i++) {
    if (vals[i] <= vals[i - 1] && vals[i] <= vals[i + 1]) consider(i / CUBIC_SEEDS);
  }
  return bestT;
}

function closestOnSegment(s: Segment, P: Vec2): number {
  switch (s.kind) {
    case 'line':
      return closestOnLine(s, P);
    case 'arc':
      return closestOnArc(s, P);
    case 'cubic':
      return closestOnCubic(s, P);
  }
}

export function exactSignedDistance(contour: Contour, P: Vec2): ClosestResult {
  let best: { i: number; t: number; d2: number } | null = null;
  for (let i = 0; i < contour.segments.length; i++) {
    const s = contour.segments[i];
    const t = closestOnSegment(s, P);
    const q = segPoint(s, t);
    const dx = q.x - P.x;
    const dy = q.y - P.y;
    const d2 = dx * dx + dy * dy;
    if (best === null || d2 < best.d2) best = { i, t, d2 };
  }
  const b = best!;
  const s = contour.segments[b.i];
  const point = segPoint(s, b.t);
  const n = segNormal(s, b.t);
  const dist = Math.sqrt(b.d2);
  const outward = sub(P, point);
  const sign = dot(outward, n) >= 0 ? 1 : -1;
  return { d: sign * dist, dist, point, grad: n, segIndex: b.i, t: b.t };
}

/**
 * Independent inside test by even-odd ray crossing on a dense polyline. Used
 * only to cross-check the normal-based sign in tests -- near the contour the
 * two can disagree only within polyline discretization error, where |d| is
 * itself ~0.
 */
export function insideByRayCast(contour: Contour, P: Vec2, perCurve = 4096): boolean {
  let crossings = 0;
  const cast = (x0: number, y0: number, x1: number, y1: number) => {
    if (y0 === y1) return;
    if (P.y < Math.min(y0, y1) || P.y >= Math.max(y0, y1)) return;
    const tx = x0 + ((P.y - y0) / (y1 - y0)) * (x1 - x0);
    if (tx > P.x) crossings++;
  };
  for (const s of contour.segments) {
    const n = s.kind === 'line' ? 1 : perCurve;
    let prev = segPoint(s, 0);
    for (let i = 1; i <= n; i++) {
      const cur = segPoint(s, i / n);
      cast(prev.x, prev.y, cur.x, cur.y);
      prev = cur;
    }
  }
  return crossings % 2 === 1;
}

// ---------------------------------------------------------------------------
// Band sampler
// ---------------------------------------------------------------------------

export interface BandSample {
  /** query point */
  P: Vec2;
  /** exact signed distance (== the offset used to construct P) */
  d: number;
  /** exact field gradient (unit) */
  grad: Vec2;
  /** base point on the contour */
  base: Vec2;
  /** index of the segment the base point came from */
  segIndex: number;
  /** parameter of the base point within its segment */
  t: number;
  /** |curvature| at the base point */
  curvature: number;
}

export interface BandOptions {
  /** half-width of the band in px */
  halfBand: number;
  /** number of signed offsets across the band (odd -> includes 0) */
  offsets: number;
  /** minimum contour samples per curved segment */
  minPerCurve: number;
  /** contour samples per px of arc length on straight segments */
  perPxStraight: number;
}

export const DEFAULT_BAND: BandOptions = {
  halfBand: 8,
  offsets: 33,
  minPerCurve: 384,
  perPxStraight: 0.5,
};

/**
 * Points offset along the outward normal have signed distance exactly equal to
 * the offset, provided the offset does not reach the medial axis. Outward that
 * is always true for a convex contour; inward the limit is the radius of
 * curvature (and, near the straight edges, the shape's inradius).
 */
export function inwardReach(contour: Contour, base: Vec2, curvature: number): number {
  const { W, H } = contour.spec;
  // Inward reach is limited by (a) the local radius of curvature and (b) how far
  // the point is from the opposite side of the shape.
  const byCurvature = curvature > 0 ? 1 / curvature : Infinity;
  const byOpposite = Math.min(W - Math.abs(base.x), H - Math.abs(base.y), Math.min(W, H));
  return Math.min(byCurvature, Math.max(0, byOpposite));
}

export function sampleBand(contour: Contour, opts: BandOptions = DEFAULT_BAND): BandSample[] {
  const out: BandSample[] = [];
  const segs = contour.segments;

  for (let i = 0; i < segs.length; i++) {
    const s = segs[i];
    const L = segLength(s);
    const n =
      s.kind === 'line'
        ? Math.max(2, Math.ceil(L * opts.perPxStraight))
        : Math.max(opts.minPerCurve, Math.ceil(L * 4));

    for (let k = 0; k <= n; k++) {
      // Skip the shared endpoint so adjacent segments do not duplicate it.
      if (k === n && i !== segs.length - 1) continue;
      const t = k / n;
      const base = segPoint(s, t);
      const nrm = segNormal(s, t);
      const kappa = segCurvature(s, t);
      const reach = inwardReach(contour, base, kappa);
      const inLimit = Math.min(opts.halfBand, 0.98 * reach);

      for (let j = 0; j < opts.offsets; j++) {
        const u = opts.offsets === 1 ? 0 : (j / (opts.offsets - 1)) * 2 - 1; // -1..1
        const delta = u >= 0 ? u * opts.halfBand : u * inLimit;
        out.push({
          P: { x: base.x + nrm.x * delta, y: base.y + nrm.y * delta },
          d: delta,
          grad: nrm,
          base,
          segIndex: i,
          t,
          curvature: kappa,
        });
      }
    }
  }
  return out;
}

/** Angle between two unit vectors, degrees. */
export function angleDeg(a: Vec2, b: Vec2): number {
  const ua = norm(a);
  const ub = norm(b);
  const c = Math.max(-1, Math.min(1, dot(ua, ub)));
  return (Math.acos(c) * 180) / Math.PI;
}

/**
 * A grid of band points found by dense area sampling + the exact solver. Slower
 * than `sampleBand` but makes no parameterization assumption; used to validate
 * the band sampler and to cover the interior near the medial axis.
 */
export function gridBandSamples(
  contour: Contour,
  step: number,
  halfBand: number
): { P: Vec2; d: number; grad: Vec2 }[] {
  const { W, H } = contour.spec;
  const out: { P: Vec2; d: number; grad: Vec2 }[] = [];
  const xMax = W + halfBand + step;
  const yMax = H + halfBand + step;
  for (let x = 0; x <= xMax; x += step) {
    for (let y = 0; y <= yMax; y += step) {
      const P = { x, y };
      const r = exactSignedDistance(contour, P);
      if (Math.abs(r.d) <= halfBand) out.push({ P, d: r.d, grad: r.grad });
    }
  }
  return out;
}
