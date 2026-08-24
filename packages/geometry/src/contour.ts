/**
 * The Contour IR — cubic Bezier / arc segments, corner metadata, winding.
 *
 * §Geometry is explicit that this is the **interchange** representation, for
 * export, tessellation and future arbitrary shapes, and **not** the per-pixel
 * render form: exact distance to a cubic Bezier needs quintic root-finding, so
 * no practical closed-form SDF of the raw contour exists. What renders is the
 * parametric pseudo-SDF in `field.ts`, with a measured error bound against this.
 *
 * That makes the IR two things and only two things:
 *   - what tooling and tessellation consumers read;
 *   - the ground truth the error bound is measured against.
 *
 * ## Frame
 *
 * Segments are emitted **clockwise in a y-up frame**, which makes the outward
 * normal of a segment with unit tangent `T` equal `(-T.y, T.x)`. A y-down
 * consumer (the DOM) sees the same ring as counter-clockwise; `winding` records
 * which convention the data is in rather than leaving it to be inferred. The
 * ground-truth distance solver depends on this, so it is not cosmetic.
 *
 * ## The construction
 *
 * One corner is: straight edge -> cubic -> circular arc -> cubic -> straight
 * edge. The cubics ramp curvature from 0 at the straight edge up to 1/r at the
 * arc, which is what makes the corner read as "continuous curvature" rather than
 * the curvature step of a plain circular arc. `smoothing = 0` degenerates the
 * cubics to zero length and reproduces the plain circular rounded rectangle
 * exactly.
 *
 * The family is **G1 but not G2**: the cubic meets the circular arc with a
 * curvature step of 0.39-0.57 / r, and smoothing 1.0 is the only
 * curvature-continuous member (the arc vanishes there). Nothing in this kernel
 * may assume G2 — S2 says so explicitly, and `contourCurvatureBreaks` reports
 * the step rather than asserting it away.
 */

import type { CornerConstruction } from "./corner";
import type { Vec2 } from "./channels";

export interface Point {
  readonly x: number;
  readonly y: number;
}

export type ContourSegment =
  | { readonly kind: "line"; readonly p0: Point; readonly p1: Point }
  | {
      readonly kind: "cubic";
      readonly p0: Point;
      readonly p1: Point;
      readonly p2: Point;
      readonly p3: Point;
    }
  | {
      readonly kind: "arc";
      readonly center: Point;
      readonly radius: number;
      /** start angle, radians */
      readonly a0: number;
      /** signed sweep, radians; negative is clockwise in the y-up frame */
      readonly sweep: number;
    };

export interface Contour {
  readonly segments: readonly ContourSegment[];
  /** Always closed in v1: every shape family is a single closed ring. */
  readonly closed: true;
  readonly winding: "clockwise-y-up";
  /** Corner metadata, so a consumer can re-derive the corner without the spec. */
  readonly corner: CornerConstruction;
  /** Where the shape sits, since segments already have it applied. */
  readonly center: Vec2;
}

const pt = (x: number, y: number): Point => ({ x, y });
const sub = (a: Point, b: Point): Point => pt(a.x - b.x, a.y - b.y);
const dot = (a: Point, b: Point): number => a.x * b.x + a.y * b.y;
const len = (a: Point): number => Math.hypot(a.x, a.y);
const norm = (a: Point): Point => {
  const l = Math.hypot(a.x, a.y);
  return l === 0 ? pt(0, 0) : pt(a.x / l, a.y / l);
};

const EPS_LEN = 1e-12;

// ---------------------------------------------------------------------------
// segment evaluation
// ---------------------------------------------------------------------------

function arcPoint(s: Extract<ContourSegment, { kind: "arc" }>, t: number): Point {
  const ang = s.a0 + s.sweep * t;
  return pt(s.center.x + s.radius * Math.cos(ang), s.center.y + s.radius * Math.sin(ang));
}

export function segmentPoint(s: ContourSegment, t: number): Point {
  switch (s.kind) {
    case "line":
      return pt(s.p0.x + (s.p1.x - s.p0.x) * t, s.p0.y + (s.p1.y - s.p0.y) * t);
    case "cubic": {
      const u = 1 - t;
      const w0 = u * u * u;
      const w1 = 3 * u * u * t;
      const w2 = 3 * u * t * t;
      const w3 = t * t * t;
      return pt(
        w0 * s.p0.x + w1 * s.p1.x + w2 * s.p2.x + w3 * s.p3.x,
        w0 * s.p0.y + w1 * s.p1.y + w2 * s.p2.y + w3 * s.p3.y,
      );
    }
    case "arc":
      return arcPoint(s, t);
  }
}

/** d/dt of `segmentPoint` — not unit length. */
export function segmentDerivative(s: ContourSegment, t: number): Point {
  switch (s.kind) {
    case "line":
      return sub(s.p1, s.p0);
    case "cubic": {
      const u = 1 - t;
      const w0 = -3 * u * u;
      const w1 = 3 * u * u - 6 * u * t;
      const w2 = 6 * u * t - 3 * t * t;
      const w3 = 3 * t * t;
      return pt(
        w0 * s.p0.x + w1 * s.p1.x + w2 * s.p2.x + w3 * s.p3.x,
        w0 * s.p0.y + w1 * s.p1.y + w2 * s.p2.y + w3 * s.p3.y,
      );
    }
    case "arc": {
      const ang = s.a0 + s.sweep * t;
      return pt(-s.radius * s.sweep * Math.sin(ang), s.radius * s.sweep * Math.cos(ang));
    }
  }
}

/** d2/dt2 of `segmentPoint`. */
export function segmentSecondDerivative(s: ContourSegment, t: number): Point {
  switch (s.kind) {
    case "line":
      return pt(0, 0);
    case "cubic": {
      const u = 1 - t;
      return pt(
        6 * u * s.p0.x + (-12 * u + 6 * t) * s.p1.x + (6 * u - 12 * t) * s.p2.x + 6 * t * s.p3.x,
        6 * u * s.p0.y + (-12 * u + 6 * t) * s.p1.y + (6 * u - 12 * t) * s.p2.y + 6 * t * s.p3.y,
      );
    }
    case "arc": {
      const ang = s.a0 + s.sweep * t;
      const k = -s.radius * s.sweep * s.sweep;
      return pt(k * Math.cos(ang), k * Math.sin(ang));
    }
  }
}

/** Outward unit normal, given the clockwise y-up winding. */
export function segmentNormal(s: ContourSegment, t: number): Point {
  const T = norm(segmentDerivative(s, t));
  return pt(-T.y, T.x);
}

/** |curvature| at parameter t. */
export function segmentCurvature(s: ContourSegment, t: number): number {
  const d1 = segmentDerivative(s, t);
  const d2 = segmentSecondDerivative(s, t);
  const cross = d1.x * d2.y - d1.y * d2.x;
  const sp = Math.hypot(d1.x, d1.y);
  return sp === 0 ? 0 : Math.abs(cross) / (sp * sp * sp);
}

export function segmentStart(s: ContourSegment): Point {
  return s.kind === "arc" ? arcPoint(s, 0) : s.p0;
}

export function segmentEnd(s: ContourSegment): Point {
  switch (s.kind) {
    case "line":
      return s.p1;
    case "cubic":
      return s.p3;
    case "arc":
      return arcPoint(s, 1);
  }
}

const GAUSS_X = [
  -0.906179845938664, -0.538469310105683, 0, 0.538469310105683, 0.906179845938664,
];
const GAUSS_W = [
  0.236926885056189, 0.478628670499366, 0.568888888888889, 0.478628670499366, 0.236926885056189,
];

/** Arc length of one segment, by Gauss-Legendre on subintervals. */
export function segmentLength(s: ContourSegment, subdivisions = 16): number {
  if (s.kind === "line") return len(sub(s.p1, s.p0));
  if (s.kind === "arc") return Math.abs(s.sweep) * s.radius;
  let total = 0;
  for (let i = 0; i < subdivisions; i++) {
    const t0 = i / subdivisions;
    const t1 = (i + 1) / subdivisions;
    const half = (t1 - t0) / 2;
    const mid = (t0 + t1) / 2;
    let acc = 0;
    for (let k = 0; k < GAUSS_X.length; k++) {
      acc += (GAUSS_W[k] as number) * len(segmentDerivative(s, mid + half * (GAUSS_X[k] as number)));
    }
    total += acc * half;
  }
  return total;
}

export function contourLength(c: Contour): number {
  return c.segments.reduce((acc, s) => acc + segmentLength(s), 0);
}

// ---------------------------------------------------------------------------
// building the ring
// ---------------------------------------------------------------------------

/**
 * The first-quadrant (top-right) corner, clockwise: it starts on the top edge at
 * `(halfW - reach, halfH)` and ends on the right edge at `(halfW, halfH - reach)`.
 */
function topRightCorner(halfW: number, halfH: number, cp: CornerConstruction): ContourSegment[] {
  const { a, b, c, d, arcSectionLength: L, radius: r, reach } = cp;
  const out: ContourSegment[] = [];
  if (r <= EPS_LEN || reach <= EPS_LEN) return out; // sharp corner: the edges meet

  const P1 = pt(halfW - reach, halfH);
  const P2 = pt(P1.x + a + b + c, P1.y - d);
  const P3 = pt(P2.x + L, P2.y - L);
  const P4 = pt(P3.x + d, P3.y - (a + b + c));

  const hasShoulder = a + b + c > EPS_LEN || d > EPS_LEN;

  if (hasShoulder) {
    out.push({ kind: "cubic", p0: P1, p1: pt(P1.x + a, P1.y), p2: pt(P1.x + a + b, P1.y), p3: P2 });
  }

  if (L > EPS_LEN) {
    // The arc is symmetric about the corner's 45-degree diagonal. Its centre
    // sits on the perpendicular bisector of the chord P2->P3, offset inward.
    const mid = pt((P2.x + P3.x) / 2, (P2.y + P3.y) / 2);
    const halfChord = (L * Math.SQRT2) / 2;
    const h = Math.sqrt(Math.max(0, r * r - halfChord * halfChord));
    const center = pt(mid.x - h / Math.SQRT2, mid.y - h / Math.SQRT2);
    const a0 = Math.atan2(P2.y - center.y, P2.x - center.x);
    const a1 = Math.atan2(P3.y - center.y, P3.x - center.x);
    let sweep = a1 - a0;
    while (sweep > 0) sweep -= 2 * Math.PI;
    while (sweep < -2 * Math.PI) sweep += 2 * Math.PI;
    out.push({ kind: "arc", center, radius: r, a0, sweep });
  }

  if (hasShoulder) {
    out.push({
      kind: "cubic",
      p0: P3,
      p1: pt(P3.x + d, P3.y - c),
      p2: pt(P3.x + d, P3.y - (b + c)),
      p3: P4,
    });
  }

  return out;
}

/**
 * Mirror a segment across x=0, y=0, or both. A single mirror flips orientation,
 * so the segment is reversed to keep the ring consistently clockwise; two
 * mirrors preserve it.
 */
export function mirrorSegment(s: ContourSegment, mx: boolean, my: boolean): ContourSegment {
  const m = (q: Point): Point => pt(mx ? -q.x : q.x, my ? -q.y : q.y);
  const reverse = mx !== my;
  switch (s.kind) {
    case "line": {
      const p0 = m(s.p0);
      const p1 = m(s.p1);
      return reverse ? { kind: "line", p0: p1, p1: p0 } : { kind: "line", p0, p1 };
    }
    case "cubic": {
      const p0 = m(s.p0);
      const p1 = m(s.p1);
      const p2 = m(s.p2);
      const p3 = m(s.p3);
      return reverse
        ? { kind: "cubic", p0: p3, p1: p2, p2: p1, p3: p0 }
        : { kind: "cubic", p0, p1, p2, p3 };
    }
    case "arc": {
      const center = m(s.center);
      const start = m(arcPoint(s, 0));
      const end = m(arcPoint(s, 1));
      const from = reverse ? end : start;
      const to = reverse ? start : end;
      const a0 = Math.atan2(from.y - center.y, from.x - center.x);
      const a1 = Math.atan2(to.y - center.y, to.x - center.x);
      let sweep = a1 - a0;
      while (sweep > 0) sweep -= 2 * Math.PI;
      while (sweep < -2 * Math.PI) sweep += 2 * Math.PI;
      return { kind: "arc", center, radius: s.radius, a0, sweep };
    }
  }
}

/**
 * Assemble a closed ring from one corner by mirroring, with the four straight
 * edges between. Shared by the reference-family construction and Apple's, which
 * differ only in what one corner looks like.
 */
export function ringFromCorner(
  halfW: number,
  halfH: number,
  reach: number,
  topRight: readonly ContourSegment[],
): ContourSegment[] {
  const tr = [...topRight];
  const br = tr.map((s) => mirrorSegment(s, false, true)).reverse();
  const bl = tr.map((s) => mirrorSegment(s, true, true));
  const tl = tr.map((s) => mirrorSegment(s, true, false)).reverse();

  const segs: ContourSegment[] = [];
  segs.push({ kind: "line", p0: pt(0, halfH), p1: pt(halfW - reach, halfH) });
  segs.push(...tr);
  segs.push({ kind: "line", p0: pt(halfW, halfH - reach), p1: pt(halfW, -(halfH - reach)) });
  segs.push(...br);
  segs.push({ kind: "line", p0: pt(halfW - reach, -halfH), p1: pt(-(halfW - reach), -halfH) });
  segs.push(...bl);
  segs.push({ kind: "line", p0: pt(-halfW, -(halfH - reach)), p1: pt(-halfW, halfH - reach) });
  segs.push(...tl);
  segs.push({ kind: "line", p0: pt(-(halfW - reach), halfH), p1: pt(0, halfH) });

  return segs.filter((s) => len(sub(segmentEnd(s), segmentStart(s))) > EPS_LEN);
}

export function translateSegment(s: ContourSegment, dx: number, dy: number): ContourSegment {
  const m = (q: Point): Point => pt(q.x + dx, q.y + dy);
  switch (s.kind) {
    case "line":
      return { kind: "line", p0: m(s.p0), p1: m(s.p1) };
    case "cubic":
      return { kind: "cubic", p0: m(s.p0), p1: m(s.p1), p2: m(s.p2), p3: m(s.p3) };
    case "arc":
      return { kind: "arc", center: m(s.center), radius: s.radius, a0: s.a0, sweep: s.sweep };
  }
}

/**
 * Build the reference-family contour for a corner construction, centred at
 * `center`. This is the curve the declared error bound is measured against.
 */
export function buildReferenceContour(
  halfW: number,
  halfH: number,
  corner: CornerConstruction,
  center: Vec2 = [0, 0],
): Contour {
  const local = ringFromCorner(halfW, halfH, corner.reach, topRightCorner(halfW, halfH, corner));
  const segments =
    center[0] === 0 && center[1] === 0
      ? local
      : local.map((s) => translateSegment(s, center[0], center[1]));
  return { segments, closed: true, winding: "clockwise-y-up", corner, center };
}

// ---------------------------------------------------------------------------
// integrity and reporting
// ---------------------------------------------------------------------------

/** Max gap between consecutive segment endpoints — a closure check. */
export function contourGap(c: Contour): number {
  let worst = 0;
  for (let i = 0; i < c.segments.length; i++) {
    const cur = c.segments[i] as ContourSegment;
    const next = c.segments[(i + 1) % c.segments.length] as ContourSegment;
    worst = Math.max(worst, len(sub(segmentEnd(cur), segmentStart(next))));
  }
  return worst;
}

/**
 * Max tangent-direction discontinuity between consecutive segments, radians.
 *
 * `atan2(cross, dot)` rather than `acos(dot)`: near-zero angles are recovered to
 * full precision instead of the sqrt(eps) ~ 1e-8 floor `acos` would impose,
 * which matters because the claim being checked is G1 to 1e-15.
 */
export function contourTangentBreak(c: Contour): number {
  let worst = 0;
  for (let i = 0; i < c.segments.length; i++) {
    const cur = c.segments[i] as ContourSegment;
    const next = c.segments[(i + 1) % c.segments.length] as ContourSegment;
    const t0 = norm(segmentDerivative(cur, 1));
    const t1 = norm(segmentDerivative(next, 0));
    worst = Math.max(worst, Math.abs(Math.atan2(t0.x * t1.y - t0.y * t1.x, dot(t0, t1))));
  }
  return worst;
}

/**
 * Curvature discontinuity at each join, as `|k_after - k_before| * r`. Reported
 * rather than asserted away: the family is G1 and not G2, and pretending
 * otherwise is how a kernel ends up assuming curvature continuity it does not
 * have.
 */
export function contourCurvatureBreaks(c: Contour, radius: number): number[] {
  const out: number[] = [];
  for (let i = 0; i < c.segments.length; i++) {
    const cur = c.segments[i] as ContourSegment;
    const next = c.segments[(i + 1) % c.segments.length] as ContourSegment;
    out.push(Math.abs(segmentCurvature(next, 0) - segmentCurvature(cur, 1)) * radius);
  }
  return out;
}

/** Enclosed area via Green's theorem, 0.5 * closed integral of (x dy - y dx). */
export function contourArea(c: Contour): number {
  let total = 0;
  for (const s of c.segments) {
    const subN = s.kind === "line" ? 1 : 24;
    for (let i = 0; i < subN; i++) {
      const t0 = i / subN;
      const t1 = (i + 1) / subN;
      const half = (t1 - t0) / 2;
      const mid = (t0 + t1) / 2;
      let acc = 0;
      for (let k = 0; k < GAUSS_X.length; k++) {
        const t = mid + half * (GAUSS_X[k] as number);
        const P = segmentPoint(s, t);
        const D = segmentDerivative(s, t);
        acc += (GAUSS_W[k] as number) * (P.x * D.y - P.y * D.x);
      }
      total += acc * half;
    }
  }
  return Math.abs(total / 2);
}

// ---------------------------------------------------------------------------
// pure-Bezier export
// ---------------------------------------------------------------------------

/**
 * The same ring with every arc replaced by one cubic, for consumers that want
 * Beziers only (SVG path export, most tessellators).
 *
 * One cubic per arc is exact enough to be uninteresting here: the standard
 * `(4/3)*tan(sweep/4)*R` handle identity is what Apple's own `.continuous` path
 * uses for its mid-corner arc, and S2 measured that match at 1.5e-7. It holds
 * because these sweeps never exceed 90 degrees — a corner arc spans
 * `90 * (1 - smoothing)` degrees at most.
 */
export function contourToCubics(c: Contour): Contour {
  const segments = c.segments.map((s): ContourSegment => {
    if (s.kind !== "arc") return s;
    const p0 = arcPoint(s, 0);
    const p3 = arcPoint(s, 1);
    // |sweep|: the unit tangents already carry the direction of travel, so the
    // handle length must be a positive scalar or the controls point backwards.
    const k = (4 / 3) * Math.tan(Math.abs(s.sweep) / 4) * s.radius;
    const t0 = segmentDerivative(s, 0);
    const t1 = segmentDerivative(s, 1);
    const u0 = norm(t0);
    const u1 = norm(t1);
    return {
      kind: "cubic",
      p0,
      p1: pt(p0.x + u0.x * k, p0.y + u0.y * k),
      p2: pt(p3.x - u1.x * k, p3.y - u1.y * k),
      p3,
    };
  });
  return { ...c, segments };
}
