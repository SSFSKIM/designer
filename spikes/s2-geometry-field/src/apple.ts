/**
 * Apple's actual `.continuous` corner, as a second reference contour family.
 *
 * The spec seeds `smoothing` from Figma-squircle fitting, so Figma's family is
 * the primary reference. But Figma's family is not Apple's curve, and the point
 * of a fidelity-first material is to know how far the reference itself is from
 * the thing being replicated. So this module carries Apple's curve too, and
 * `src/reference.ts` measures the gap.
 *
 * Provenance. The control points below are a CGPath dump of
 * `RoundedRectangle(cornerRadius:style:.continuous)` on macOS 26, normalized by
 * the corner radius. The edge reach 1.528665 is not reverse-engineered: Apple
 * publishes it as `+[CALayer cornerCurveExpansionFactor:]` for
 * `kCACornerCurveContinuous`. Every derived property asserted in
 * test/apple.test.ts is recomputed from these numbers alone, so the dump is
 * checked rather than trusted:
 *
 *   - three cubics per corner, no arcs and no quadratics;
 *   - the MIDDLE cubic is a circular arc to within 1.5e-7 -- its handle length
 *     matches the exact arc-as-cubic formula (4/3)tan(sweep/4)R -- of radius
 *     0.931253r, centre (0.950002r, 0.950002r), sweep 50.0000 degrees;
 *   - the shoulder cubics meet the straight edge with zero curvature (G2 there);
 *   - and they meet the arc with a 2.4532-degree TANGENT break. Apple's own path
 *     is not G1 at those two joins, so "continuous curvature" holds at the join
 *     with the straight edge and nowhere else.
 *
 * That last number is the useful one for S2: it is the reference's own normal
 * discontinuity, and it bounds how precise a gradient is worth chasing.
 */

import {
  type Contour,
  type Segment,
  type ShapeSpec,
  segEnd,
  segStart,
  v,
  type Vec2,
} from './contour.js';

/** Apple's published corner-curve expansion factor for `.continuous`. */
export const APPLE_REACH = 1.52866495;

/**
 * Radius above which Apple can no longer honour the reach and the corner shape
 * warps: reach * r must fit in half the side.
 */
export const APPLE_SATURATION_R_OVER_SIDE = 1 / (2 * APPLE_REACH);

/**
 * One corner, normalized by r, in a frame whose origin is the box corner and
 * whose interior lies toward +x/+y. Listed in the dump's own order: from the
 * vertical edge round to the horizontal edge.
 */
const DUMP: number[][] = [
  [0, 1.52866495], // on the vertical edge
  [0, 1.08849001],
  [0, 0.86840701],
  [0.07491140, 0.63149399], // shoulder -> arc join
  [0.16906001, 0.37282401],
  [0.37282401, 0.16906001],
  [0.63149399, 0.07491140], // arc -> shoulder join
  [0.86840701, 0],
  [1.08849001, 0],
  [1.52866495, 0], // on the horizontal edge
];

export const APPLE_DUMP = DUMP;

/**
 * Top-right corner in the centred, y-up frame, emitted CLOCKWISE (from the top
 * edge to the right edge) to match `buildContour`'s orientation.
 *
 * The dump runs the other way round the corner, so it is reversed here: dump
 * point (u, v) maps to (W - u*r, H - v*r), and reversing the list makes the
 * traversal start on the top edge.
 */
function appleTopRight(W: number, H: number, r: number): Segment[] {
  const pts: Vec2[] = DUMP.map(([u, w]) => v(W - u * r, H - w * r));
  pts.reverse(); // now index 0 is on the top edge, index 9 on the right edge
  const out: Segment[] = [];
  for (let i = 0; i + 3 < pts.length; i += 3) {
    out.push({ kind: 'cubic', p0: pts[i], p1: pts[i + 1], p2: pts[i + 2], p3: pts[i + 3] });
  }
  return out;
}

function mirror(s: Segment, mx: boolean, my: boolean): Segment {
  const m = (q: Vec2): Vec2 => ({ x: mx ? -q.x : q.x, y: my ? -q.y : q.y });
  if (s.kind !== 'cubic') throw new Error('apple corners are all cubics');
  const p0 = m(s.p0);
  const p1 = m(s.p1);
  const p2 = m(s.p2);
  const p3 = m(s.p3);
  // a single mirror flips orientation, so reverse to stay clockwise
  return mx !== my
    ? { kind: 'cubic', p0: p3, p1: p2, p2: p1, p3: p0 }
    : { kind: 'cubic', p0, p1, p2, p3 };
}

/**
 * Apple's continuous-corner rounded rectangle. `spec.smoothing` is ignored --
 * Apple's curve has no smoothing parameter, which is exactly the point.
 *
 * Apple clamps the reach at half the side; past `APPLE_SATURATION_R_OVER_SIDE`
 * the real thing warps in a way this construction does not attempt to reproduce,
 * so `saturated` is reported and such configurations are excluded from the
 * comparison rather than silently mismodelled.
 */
export function buildAppleContour(spec: ShapeSpec): Contour & { saturated: boolean } {
  const { W, H } = spec;
  const budget = Math.min(W, H);
  const r = Math.max(0, Math.min(spec.r, budget / APPLE_REACH));
  const saturated = spec.r > budget / APPLE_REACH + 1e-12;
  const p = APPLE_REACH * r;

  const tr = appleTopRight(W, H, r);
  const br = tr.map((s) => mirror(s, false, true)).reverse();
  const bl = tr.map((s) => mirror(s, true, true));
  const tl = tr.map((s) => mirror(s, true, false)).reverse();

  const segs: Segment[] = [];
  segs.push({ kind: 'line', p0: v(0, H), p1: v(W - p, H) });
  segs.push(...tr);
  segs.push({ kind: 'line', p0: v(W, H - p), p1: v(W, -(H - p)) });
  segs.push(...br);
  segs.push({ kind: 'line', p0: v(W - p, -H), p1: v(-(W - p), -H) });
  segs.push(...bl);
  segs.push({ kind: 'line', p0: v(-W, -(H - p)), p1: v(-W, H - p) });
  segs.push(...tl);
  segs.push({ kind: 'line', p0: v(-(W - p), H), p1: v(0, H) });

  return {
    spec,
    // a/b/c/d are Figma's cubic offset scalars and have no Apple analogue
    params: {
      r,
      smoothingEff: APPLE_REACH - 1,
      p,
      a: 0,
      b: 0,
      c: 0,
      d: 0,
      arcSectionLength: 0,
      arcMeasure: (50 * Math.PI) / 180,
      budget,
    },
    segments: segs.filter((s) => Math.hypot(segEnd(s).x - segStart(s).x, segEnd(s).y - segStart(s).y) > 1e-12),
    saturated,
  };
}
