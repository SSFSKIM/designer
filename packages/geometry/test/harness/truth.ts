/**
 * Ground truth for the reference contour: exact signed distance and exact field
 * gradient. Ported from `spikes/s2-geometry-field/src/truth.ts` — this is the
 * harness S2 designated as C3's regression base.
 *
 * Two independent paths, deliberately, because they check each other:
 *
 *  1. `exactSignedDistance` — the general solver. Closed form for lines and
 *     arcs; for cubics, dense seeding plus Newton refinement on
 *     `d/dt |C(t) - P|^2 = 0`, which converges to machine precision.
 *
 *  2. `sampleBand` — the band sampler used for the sweep. Points are generated
 *     as `contourPoint + delta * outwardNormal`, so the ground-truth distance is
 *     EXACTLY `delta` and the ground-truth gradient is EXACTLY that normal, with
 *     no solver in the loop.
 *
 * Path 2 is exact because a true signed distance field has `|grad d| = 1` and
 * `grad d(P)` equals the outward unit normal at the closest contour point —
 * inside as well as outside. It holds only while the offset stays below the
 * local medial-axis reach, which the sampler enforces.
 *
 * Living in `test/` rather than `src/` is the point: an exact-distance solver is
 * how the shipped approximation is judged, and shipping it would invite someone
 * to call it at runtime, which is the one thing §Geometry says cannot work.
 */

import {
  type Contour,
  type ContourSegment,
  type Point,
  segmentCurvature,
  segmentDerivative,
  segmentLength,
  segmentNormal,
  segmentPoint,
  segmentSecondDerivative,
} from "../../src/contour";

const sub = (a: Point, b: Point): Point => ({ x: a.x - b.x, y: a.y - b.y });
const dot = (a: Point, b: Point): number => a.x * b.x + a.y * b.y;
const len = (a: Point): number => Math.hypot(a.x, a.y);

export interface ClosestResult {
  /** signed distance: negative inside, positive outside */
  readonly d: number;
  readonly distance: number;
  readonly point: Point;
  /** exact field gradient == outward unit normal at the closest point */
  readonly grad: Point;
  readonly segIndex: number;
  readonly t: number;
}

function closestOnLine(s: Extract<ContourSegment, { kind: "line" }>, P: Point): number {
  const dir = sub(s.p1, s.p0);
  const l2 = dot(dir, dir);
  if (l2 === 0) return 0;
  return Math.max(0, Math.min(1, dot(sub(P, s.p0), dir) / l2));
}

function closestOnArc(s: Extract<ContourSegment, { kind: "arc" }>, P: Point): number {
  const rel = sub(P, s.center);
  if (rel.x === 0 && rel.y === 0) return 0.5;
  const ang = Math.atan2(rel.y, rel.x);
  let delta = ang - s.a0;
  if (s.sweep < 0) {
    while (delta > 0) delta -= 2 * Math.PI;
    while (delta < s.sweep - 2 * Math.PI + 1e-15) delta += 2 * Math.PI;
  } else {
    while (delta < 0) delta += 2 * Math.PI;
    while (delta > s.sweep + 2 * Math.PI - 1e-15) delta -= 2 * Math.PI;
  }
  const t = delta / s.sweep;
  if (t >= 0 && t <= 1) return t;
  // Outside the angular span: whichever endpoint is nearer.
  return len(sub(P, segmentPoint(s, 0))) <= len(sub(P, segmentPoint(s, 1))) ? 0 : 1;
}

const CUBIC_SEEDS = 48;

function closestOnCubic(s: Extract<ContourSegment, { kind: "cubic" }>, P: Point): number {
  const vals = new Array<number>(CUBIC_SEEDS + 1);
  for (let i = 0; i <= CUBIC_SEEDS; i++) {
    const q = segmentPoint(s, i / CUBIC_SEEDS);
    vals[i] = (q.x - P.x) ** 2 + (q.y - P.y) ** 2;
  }

  let bestT = 0;
  let bestV = Number.POSITIVE_INFINITY;

  const consider = (seedT: number): void => {
    let t = seedT;
    for (let it = 0; it < 64; it++) {
      const C = segmentPoint(s, t);
      const D1 = segmentDerivative(s, t);
      const D2 = segmentSecondDerivative(s, t);
      const e = sub(C, P);
      const g = 2 * dot(e, D1);
      const h = 2 * (dot(D1, D1) + dot(e, D2));
      if (!Number.isFinite(g) || !Number.isFinite(h)) break;
      let step = h > 0 ? g / h : g / Math.max(1e-30, dot(D1, D1) * 2);
      if (!Number.isFinite(step)) break;
      step = Math.max(-0.25, Math.min(0.25, step));
      const next = Math.max(0, Math.min(1, t - step));
      if (Math.abs(next - t) < 1e-16) {
        t = next;
        break;
      }
      t = next;
    }
    const q = segmentPoint(s, t);
    const vv = (q.x - P.x) ** 2 + (q.y - P.y) ** 2;
    if (vv < bestV) {
      bestV = vv;
      bestT = t;
    }
  };

  consider(0);
  consider(1);
  for (let i = 1; i < CUBIC_SEEDS; i++) {
    if ((vals[i] as number) <= (vals[i - 1] as number) && (vals[i] as number) <= (vals[i + 1] as number)) {
      consider(i / CUBIC_SEEDS);
    }
  }
  return bestT;
}

function closestOnSegment(s: ContourSegment, P: Point): number {
  switch (s.kind) {
    case "line":
      return closestOnLine(s, P);
    case "arc":
      return closestOnArc(s, P);
    case "cubic":
      return closestOnCubic(s, P);
  }
}

export function exactSignedDistance(contour: Contour, P: Point): ClosestResult {
  let bi = 0;
  let bt = 0;
  let bd2 = Number.POSITIVE_INFINITY;
  for (let i = 0; i < contour.segments.length; i++) {
    const s = contour.segments[i] as ContourSegment;
    const t = closestOnSegment(s, P);
    const q = segmentPoint(s, t);
    const d2 = (q.x - P.x) ** 2 + (q.y - P.y) ** 2;
    if (d2 < bd2) {
      bd2 = d2;
      bi = i;
      bt = t;
    }
  }
  const s = contour.segments[bi] as ContourSegment;
  const point = segmentPoint(s, bt);
  const grad = segmentNormal(s, bt);
  const distance = Math.sqrt(bd2);
  const sign = dot(sub(P, point), grad) >= 0 ? 1 : -1;
  return { d: sign * distance, distance, point, grad, segIndex: bi, t: bt };
}

/**
 * Independent inside test by even-odd ray crossing on a dense polyline. Used to
 * cross-check the normal-based sign: two different ways of answering "inside?"
 * agreeing is what makes the sign trustworthy rather than assumed.
 */
export function insideByRayCast(contour: Contour, P: Point, perCurve = 4096): boolean {
  let crossings = 0;
  const cast = (x0: number, y0: number, x1: number, y1: number): void => {
    if (y0 === y1) return;
    if (P.y < Math.min(y0, y1) || P.y >= Math.max(y0, y1)) return;
    if (x0 + ((P.y - y0) / (y1 - y0)) * (x1 - x0) > P.x) crossings++;
  };
  for (const s of contour.segments) {
    const n = s.kind === "line" ? 1 : perCurve;
    let prev = segmentPoint(s, 0);
    for (let i = 1; i <= n; i++) {
      const cur = segmentPoint(s, i / n);
      cast(prev.x, prev.y, cur.x, cur.y);
      prev = cur;
    }
  }
  return crossings % 2 === 1;
}

// ---------------------------------------------------------------------------
// band sampler
// ---------------------------------------------------------------------------

export interface BandSample {
  readonly P: Point;
  /** exact signed distance — the offset used to construct P */
  readonly d: number;
  /** exact field gradient (unit) */
  readonly grad: Point;
  readonly base: Point;
  readonly segIndex: number;
  readonly t: number;
  readonly curvature: number;
}

export interface BandOptions {
  readonly halfBand: number;
  /** number of signed offsets across the band (odd includes 0) */
  readonly offsets: number;
  readonly minPerCurve: number;
  /** contour samples per px of arc length on straight segments */
  readonly perPxStraight: number;
}

export const DEFAULT_BAND: BandOptions = {
  halfBand: 8,
  offsets: 33,
  minPerCurve: 384,
  perPxStraight: 0.5,
};

/**
 * How far inward the "distance == offset" identity survives. Outward it always
 * holds for a convex contour; inward the limit is the local radius of curvature
 * and, near the straight edges, the shape's inradius.
 */
export function inwardReach(
  halfW: number,
  halfH: number,
  base: Point,
  curvature: number,
): number {
  const byCurvature = curvature > 0 ? 1 / curvature : Number.POSITIVE_INFINITY;
  const byOpposite = Math.min(
    halfW - Math.abs(base.x),
    halfH - Math.abs(base.y),
    Math.min(halfW, halfH),
  );
  return Math.min(byCurvature, Math.max(0, byOpposite));
}

export function sampleBand(
  contour: Contour,
  halfW: number,
  halfH: number,
  opts: BandOptions = DEFAULT_BAND,
): BandSample[] {
  const out: BandSample[] = [];
  const segs = contour.segments;

  for (let i = 0; i < segs.length; i++) {
    const s = segs[i] as ContourSegment;
    const L = segmentLength(s);
    const n =
      s.kind === "line"
        ? Math.max(2, Math.ceil(L * opts.perPxStraight))
        : Math.max(opts.minPerCurve, Math.ceil(L * 4));

    for (let k = 0; k <= n; k++) {
      // Skip the shared endpoint so adjacent segments do not duplicate it.
      if (k === n && i !== segs.length - 1) continue;
      const t = k / n;
      const base = segmentPoint(s, t);
      const nrm = segmentNormal(s, t);
      const kappa = segmentCurvature(s, t);
      const inLimit = Math.min(opts.halfBand, 0.98 * inwardReach(halfW, halfH, base, kappa));

      for (let j = 0; j < opts.offsets; j++) {
        const u = opts.offsets === 1 ? 0 : (j / (opts.offsets - 1)) * 2 - 1;
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

/** Angle between two vectors, degrees. */
export function angleDeg(a: Point, b: Point): number {
  const la = Math.hypot(a.x, a.y);
  const lb = Math.hypot(b.x, b.y);
  if (la === 0 || lb === 0) return 90;
  const c = Math.max(-1, Math.min(1, (a.x * b.x + a.y * b.y) / (la * lb)));
  return (Math.acos(c) * 180) / Math.PI;
}
