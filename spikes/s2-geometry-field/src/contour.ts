/**
 * Ground-truth contour family: the iOS-style smoothed ("continuous") corner as
 * parameterized by Figma ("Desperately seeking squircles"), which is the
 * construction the vitrea spec names as the seed for `smoothing`.
 *
 * One corner is: straight edge -> cubic Bezier -> circular arc -> cubic Bezier
 * -> straight edge. The cubics ramp curvature from 0 (at the straight edge) up
 * to 1/r (at the arc), which is what makes the corner read as "continuous
 * curvature" rather than the curvature step of a plain circular arc.
 *
 * `smoothing = 0` degenerates the cubics to zero length and reproduces the plain
 * circular rounded rectangle exactly -- exercised as a test.
 *
 * Coordinates: shape centered at the origin, y up, half-extents (W, H).
 * The contour is emitted CLOCKWISE in this y-up frame, so the outward normal of
 * a segment with unit tangent T is (-T.y, T.x).
 */

export interface Vec2 {
  x: number;
  y: number;
}

export const v = (x: number, y: number): Vec2 => ({ x, y });
export const add = (a: Vec2, b: Vec2): Vec2 => ({ x: a.x + b.x, y: a.y + b.y });
export const sub = (a: Vec2, b: Vec2): Vec2 => ({ x: a.x - b.x, y: a.y - b.y });
export const mul = (a: Vec2, s: number): Vec2 => ({ x: a.x * s, y: a.y * s });
export const dot = (a: Vec2, b: Vec2): number => a.x * b.x + a.y * b.y;
export const len = (a: Vec2): number => Math.hypot(a.x, a.y);
export const norm = (a: Vec2): Vec2 => {
  const l = Math.hypot(a.x, a.y);
  return l === 0 ? { x: 0, y: 0 } : { x: a.x / l, y: a.y / l };
};

const toRad = (deg: number) => (deg * Math.PI) / 180;

/** A shape in the v1 `fixed rounded rectangle` family. */
export interface ShapeSpec {
  /** half-width */
  W: number;
  /** half-height */
  H: number;
  /** requested corner radius (uniform across corners in this spike) */
  r: number;
  /** requested corner smoothing in [0, 1]; 0 = circular arc */
  smoothing: number;
  /**
   * Figma's `preserveSmoothing`. Default false, which is Figma's own default:
   * when the requested radius eats the whole side, smoothing is reduced rather
   * than the corner overflowing.
   */
  preserveSmoothing?: boolean;
}

export interface CornerParams {
  /** radius actually used */
  r: number;
  /** smoothing actually used after the rounding-and-smoothing budget clamp */
  smoothingEff: number;
  /** how far the corner reaches along each adjacent edge from the corner vertex */
  p: number;
  /** cubic control-offset scalars, per Figma's construction */
  a: number;
  b: number;
  c: number;
  d: number;
  /** axis-aligned extent of the circular arc section (equal in x and y) */
  arcSectionLength: number;
  /** central angle of the circular arc, radians */
  arcMeasure: number;
  /** min(W, H): the per-corner rounding-and-smoothing budget for a uniform radius */
  budget: number;
}

/**
 * The rounding-and-smoothing budget for a corner. Figma splits each side
 * between its two corners in proportion to their radii; with a uniform radius
 * that is half the side, and the corner's budget is the min over its two sides.
 * With half-extents (W, H) the sides are 2W and 2H, so the budget is min(W, H).
 */
export function cornerBudget(W: number, H: number): number {
  return Math.min(W, H);
}

export function cornerParams(spec: ShapeSpec): CornerParams {
  const budget = cornerBudget(spec.W, spec.H);
  // A radius larger than the budget cannot be honoured; clamp it first.
  const r = Math.max(0, Math.min(spec.r, budget));
  let smoothing = Math.max(0, Math.min(1, spec.smoothing));

  let p = (1 + smoothing) * r;
  if (!spec.preserveSmoothing) {
    const maxSmoothing = r > 0 ? budget / r - 1 : Infinity;
    smoothing = Math.min(smoothing, Math.max(0, maxSmoothing));
    p = Math.min(p, budget);
  }

  const arcMeasureDeg = 90 * (1 - smoothing);
  const arcSectionLength = Math.sin(toRad(arcMeasureDeg / 2)) * r * Math.SQRT2;

  const angleAlpha = (90 - arcMeasureDeg) / 2;
  const p3ToP4Distance = r * Math.tan(toRad(angleAlpha / 2));

  const angleBeta = 45 * smoothing;
  const c = p3ToP4Distance * Math.cos(toRad(angleBeta));
  const d = c * Math.tan(toRad(angleBeta));

  const b = (p - arcSectionLength - c - d) / 3;
  const a = 2 * b;

  return {
    r,
    smoothingEff: smoothing,
    p,
    a,
    b,
    c,
    d,
    arcSectionLength,
    arcMeasure: toRad(arcMeasureDeg),
    budget,
  };
}

// ---------------------------------------------------------------------------
// Contour segments
// ---------------------------------------------------------------------------

export type Segment =
  | { kind: 'line'; p0: Vec2; p1: Vec2 }
  | { kind: 'cubic'; p0: Vec2; p1: Vec2; p2: Vec2; p3: Vec2 }
  | {
      kind: 'arc';
      center: Vec2;
      radius: number;
      /** start angle, radians */
      a0: number;
      /** signed sweep, radians; negative = clockwise in the y-up frame */
      sweep: number;
    };

export function segStart(s: Segment): Vec2 {
  switch (s.kind) {
    case 'line':
    case 'cubic':
      return s.p0;
    case 'arc':
      return arcPoint(s, 0);
  }
}

export function segEnd(s: Segment): Vec2 {
  switch (s.kind) {
    case 'line':
      return s.p1;
    case 'cubic':
      return s.p3;
    case 'arc':
      return arcPoint(s, 1);
  }
}

function arcPoint(s: Extract<Segment, { kind: 'arc' }>, t: number): Vec2 {
  const ang = s.a0 + s.sweep * t;
  return { x: s.center.x + s.radius * Math.cos(ang), y: s.center.y + s.radius * Math.sin(ang) };
}

export function segPoint(s: Segment, t: number): Vec2 {
  switch (s.kind) {
    case 'line':
      return add(s.p0, mul(sub(s.p1, s.p0), t));
    case 'cubic': {
      const u = 1 - t;
      const w0 = u * u * u;
      const w1 = 3 * u * u * t;
      const w2 = 3 * u * t * t;
      const w3 = t * t * t;
      return {
        x: w0 * s.p0.x + w1 * s.p1.x + w2 * s.p2.x + w3 * s.p3.x,
        y: w0 * s.p0.y + w1 * s.p1.y + w2 * s.p2.y + w3 * s.p3.y,
      };
    }
    case 'arc':
      return arcPoint(s, t);
  }
}

/** d/dt of segPoint (not unit length). */
export function segDeriv(s: Segment, t: number): Vec2 {
  switch (s.kind) {
    case 'line':
      return sub(s.p1, s.p0);
    case 'cubic': {
      const u = 1 - t;
      const w0 = -3 * u * u;
      const w1 = 3 * u * u - 6 * u * t;
      const w2 = 6 * u * t - 3 * t * t;
      const w3 = 3 * t * t;
      return {
        x: w0 * s.p0.x + w1 * s.p1.x + w2 * s.p2.x + w3 * s.p3.x,
        y: w0 * s.p0.y + w1 * s.p1.y + w2 * s.p2.y + w3 * s.p3.y,
      };
    }
    case 'arc': {
      const ang = s.a0 + s.sweep * t;
      return { x: -s.radius * s.sweep * Math.sin(ang), y: s.radius * s.sweep * Math.cos(ang) };
    }
  }
}

/** d2/dt2 of segPoint. */
export function segDeriv2(s: Segment, t: number): Vec2 {
  switch (s.kind) {
    case 'line':
      return { x: 0, y: 0 };
    case 'cubic': {
      const u = 1 - t;
      const w0 = 6 * u;
      const w1 = -12 * u + 6 * t;
      const w2 = 6 * u - 12 * t;
      const w3 = 6 * t;
      return {
        x: w0 * s.p0.x + w1 * s.p1.x + w2 * s.p2.x + w3 * s.p3.x,
        y: w0 * s.p0.y + w1 * s.p1.y + w2 * s.p2.y + w3 * s.p3.y,
      };
    }
    case 'arc': {
      const ang = s.a0 + s.sweep * t;
      const k = -s.radius * s.sweep * s.sweep;
      return { x: k * Math.cos(ang), y: k * Math.sin(ang) };
    }
  }
}

/** Outward unit normal, given the contour is emitted clockwise in the y-up frame. */
export function segNormal(s: Segment, t: number): Vec2 {
  const T = norm(segDeriv(s, t));
  return { x: -T.y, y: T.x };
}

/** Signed curvature magnitude |k| at parameter t. */
export function segCurvature(s: Segment, t: number): number {
  const d1 = segDeriv(s, t);
  const d2 = segDeriv2(s, t);
  const cross = d1.x * d2.y - d1.y * d2.x;
  const sp = Math.hypot(d1.x, d1.y);
  return sp === 0 ? 0 : Math.abs(cross) / (sp * sp * sp);
}

// ---------------------------------------------------------------------------
// Full contour
// ---------------------------------------------------------------------------

const EPS_LEN = 1e-12;

/**
 * Build the first-quadrant (top-right) corner, clockwise: it starts on the top
 * edge at (W - p, H) and ends on the right edge at (W, H - p).
 */
function topRightCorner(W: number, H: number, cp: CornerParams): Segment[] {
  const { a, b, c, d, arcSectionLength: L, r, p } = cp;
  const out: Segment[] = [];

  if (r <= EPS_LEN || p <= EPS_LEN) {
    return out; // sharp corner: the edge lines meet at the vertex
  }

  const P1 = v(W - p, H);
  const P2 = v(P1.x + a + b + c, P1.y - d);
  const P3 = v(P2.x + L, P2.y - L);
  const P4 = v(P3.x + d, P3.y - (a + b + c));

  if (a + b + c > EPS_LEN || d > EPS_LEN) {
    out.push({
      kind: 'cubic',
      p0: P1,
      p1: v(P1.x + a, P1.y),
      p2: v(P1.x + a + b, P1.y),
      p3: P2,
    });
  }

  if (L > EPS_LEN) {
    // The arc is symmetric about the 45-degree diagonal of the corner. Its
    // center sits on the perpendicular bisector of the chord P2->P3, offset
    // toward the shape interior.
    const mid = v((P2.x + P3.x) / 2, (P2.y + P3.y) / 2);
    const halfChord = (L * Math.SQRT2) / 2;
    const h = Math.sqrt(Math.max(0, r * r - halfChord * halfChord));
    const center = v(mid.x - h / Math.SQRT2, mid.y - h / Math.SQRT2);
    const a0 = Math.atan2(P2.y - center.y, P2.x - center.x);
    const a1 = Math.atan2(P3.y - center.y, P3.x - center.x);
    // Clockwise (negative) sweep of magnitude arcMeasure.
    let sweep = a1 - a0;
    while (sweep > 0) sweep -= 2 * Math.PI;
    while (sweep < -2 * Math.PI) sweep += 2 * Math.PI;
    out.push({ kind: 'arc', center, radius: r, a0, sweep });
  }

  if (a + b + c > EPS_LEN || d > EPS_LEN) {
    out.push({
      kind: 'cubic',
      p0: P3,
      p1: v(P3.x + d, P3.y - c),
      p2: v(P3.x + d, P3.y - (b + c)),
      p3: P4,
    });
  }

  return out;
}

/** Mirror a segment across x=0, y=0, or both, reversing orientation as needed. */
function mirrorSegment(s: Segment, mx: boolean, my: boolean): Segment {
  const m = (q: Vec2): Vec2 => ({ x: mx ? -q.x : q.x, y: my ? -q.y : q.y });
  // A single mirror flips orientation, so the segment must be reversed to keep
  // the contour consistently clockwise. Two mirrors preserve orientation.
  const reverse = mx !== my;
  switch (s.kind) {
    case 'line': {
      const p0 = m(s.p0);
      const p1 = m(s.p1);
      return reverse ? { kind: 'line', p0: p1, p1: p0 } : { kind: 'line', p0, p1 };
    }
    case 'cubic': {
      const p0 = m(s.p0);
      const p1 = m(s.p1);
      const p2 = m(s.p2);
      const p3 = m(s.p3);
      return reverse
        ? { kind: 'cubic', p0: p3, p1: p2, p2: p1, p3: p0 }
        : { kind: 'cubic', p0, p1, p2, p3 };
    }
    case 'arc': {
      const center = m(s.center);
      const start = m(arcPoint(s, 0));
      const end = m(arcPoint(s, 1));
      const from = reverse ? end : start;
      const to = reverse ? start : end;
      const a0 = Math.atan2(from.y - center.y, from.x - center.x);
      const a1 = Math.atan2(to.y - center.y, to.x - center.x);
      let sweep = a1 - a0;
      // Preserve magnitude, force clockwise.
      while (sweep > 0) sweep -= 2 * Math.PI;
      while (sweep < -2 * Math.PI) sweep += 2 * Math.PI;
      return { kind: 'arc', center, radius: s.radius, a0, sweep };
    }
  }
}

export interface Contour {
  spec: ShapeSpec;
  params: CornerParams;
  segments: Segment[];
}

/**
 * Full closed contour, clockwise in the y-up frame, starting at the top edge
 * midpoint.
 */
export function buildContour(spec: ShapeSpec): Contour {
  const params = cornerParams(spec);
  const { W, H } = spec;
  const p = params.p;

  const tr = topRightCorner(W, H, params);
  const br = tr.map((s) => mirrorSegment(s, false, true)).reverse();
  const bl = tr.map((s) => mirrorSegment(s, true, true));
  const tl = tr.map((s) => mirrorSegment(s, true, false)).reverse();

  const segs: Segment[] = [];
  // top edge, from the midpoint rightwards
  segs.push({ kind: 'line', p0: v(0, H), p1: v(W - p, H) });
  segs.push(...tr);
  // right edge, downwards
  segs.push({ kind: 'line', p0: v(W, H - p), p1: v(W, -(H - p)) });
  segs.push(...br);
  // bottom edge, leftwards
  segs.push({ kind: 'line', p0: v(W - p, -H), p1: v(-(W - p), -H) });
  segs.push(...bl);
  // left edge, upwards
  segs.push({ kind: 'line', p0: v(-W, -(H - p)), p1: v(-W, H - p) });
  segs.push(...tl);
  // close back to the start
  segs.push({ kind: 'line', p0: v(-(W - p), H), p1: v(0, H) });

  const kept = segs.filter((s) => len(sub(segEnd(s), segStart(s))) > EPS_LEN);
  return { spec, params, segments: kept };
}

/** Max gap between consecutive segment endpoints — a closure/consistency check. */
export function contourGap(c: Contour): number {
  let worst = 0;
  for (let i = 0; i < c.segments.length; i++) {
    const cur = c.segments[i];
    const next = c.segments[(i + 1) % c.segments.length];
    worst = Math.max(worst, len(sub(segEnd(cur), segStart(next))));
  }
  return worst;
}

/**
 * Max tangent-direction discontinuity between consecutive segments, radians.
 * Uses atan2(cross, dot) rather than acos(dot): near-zero angles are recovered
 * to full precision instead of the sqrt(eps) ~ 1e-8 floor acos would impose.
 */
export function contourTangentBreak(c: Contour): number {
  let worst = 0;
  for (let i = 0; i < c.segments.length; i++) {
    const cur = c.segments[i];
    const next = c.segments[(i + 1) % c.segments.length];
    const t0 = norm(segDeriv(cur, 1));
    const t1 = norm(segDeriv(next, 0));
    const cross = t0.x * t1.y - t0.y * t1.x;
    worst = Math.max(worst, Math.abs(Math.atan2(cross, dot(t0, t1))));
  }
  return worst;
}

/**
 * Curvature discontinuity at each segment join, as |k_after - k_before| * r.
 * The Figma construction is G1 but NOT G2: the cubic arrives at the circular arc
 * with markedly higher curvature than the arc's own 1/r. Reported rather than
 * asserted away, because it is a property of the reference curve family.
 */
export function contourCurvatureBreaks(c: Contour, r: number): number[] {
  const out: number[] = [];
  for (let i = 0; i < c.segments.length; i++) {
    const cur = c.segments[i];
    const next = c.segments[(i + 1) % c.segments.length];
    out.push(Math.abs(segCurvature(next, 0) - segCurvature(cur, 1)) * r);
  }
  return out;
}

/** Enclosed area via Green's theorem, 0.5 * closed integral of (x dy - y dx). */
export function contourArea(c: Contour): number {
  const xs = [-0.906179845938664, -0.538469310105683, 0, 0.538469310105683, 0.906179845938664];
  const ws = [
    0.236926885056189, 0.478628670499366, 0.568888888888889, 0.478628670499366, 0.236926885056189,
  ];
  let total = 0;
  for (const s of c.segments) {
    const subN = s.kind === 'line' ? 1 : 24;
    for (let i = 0; i < subN; i++) {
      const t0 = i / subN;
      const t1 = (i + 1) / subN;
      const half = (t1 - t0) / 2;
      const mid = (t0 + t1) / 2;
      let acc = 0;
      for (let k = 0; k < xs.length; k++) {
        const t = mid + half * xs[k];
        const P = segPoint(s, t);
        const D = segDeriv(s, t);
        acc += ws[k] * (P.x * D.y - P.y * D.x);
      }
      total += acc * half;
    }
  }
  return Math.abs(total / 2);
}

/** Arc length of one segment by Gauss-Legendre on subintervals. */
export function segLength(s: Segment, sub = 16): number {
  if (s.kind === 'line') return len(sub2(s.p1, s.p0));
  if (s.kind === 'arc') return Math.abs(s.sweep) * s.radius;
  // 5-point Gauss-Legendre per subinterval
  const xs = [-0.906179845938664, -0.538469310105683, 0, 0.538469310105683, 0.906179845938664];
  const ws = [0.236926885056189, 0.478628670499366, 0.568888888888889, 0.478628670499366, 0.236926885056189];
  let total = 0;
  for (let i = 0; i < sub; i++) {
    const t0 = i / sub;
    const t1 = (i + 1) / sub;
    const half = (t1 - t0) / 2;
    const mid = (t0 + t1) / 2;
    let acc = 0;
    for (let k = 0; k < xs.length; k++) {
      const t = mid + half * xs[k];
      acc += ws[k] * len(segDeriv(s, t));
    }
    total += acc * half;
  }
  return total;
}

const sub2 = (a: Vec2, b: Vec2): Vec2 => ({ x: a.x - b.x, y: a.y - b.y });

export function contourLength(c: Contour): number {
  return c.segments.reduce((acc, s) => acc + segLength(s), 0);
}
