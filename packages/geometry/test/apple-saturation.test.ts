/**
 * The Apple reference above the saturation ratio: the shoulder compressed, the
 * capsule exact, and the crossing measured (W20 G1; claims §5.84, W20 Decision
 * Log 2 ruling 1).
 *
 * G0 measured natively that Apple keeps the requested radius past the ratio and
 * compresses the shoulder — `reach = min(APPLE_REACH * r, budget)`, effective
 * smoothing `reach / r - 1` — and that the radius clamp the render path applied
 * instead is refuted from ratio 0.364 up by six times the grid's floor. This
 * file is the geometry side of that policy: what the RENDER path resolves (the
 * renderer never calls `resolveShape`), what its contour is, and what happens at
 * the crossing between the two constructions the policy switches at.
 *
 * The crossing is the one thing the policy adds that the probe could not see. At
 * `r = budget / APPLE_REACH` the reach is the budget from both sides, so the
 * reach and the effective smoothing are continuous there; but the curve is
 * Apple's own dump below and the reference family's construction above, and
 * those are two different curves at the same reach. The distance between them is
 * pinned below, in units of the radius, so a change to either construction has
 * to come back through this number.
 */

import { describe, expect, it } from "vitest";

import {
  APPLE_CONTINUOUS_SMOOTHING_SEED,
  APPLE_REACH,
  APPLE_SATURATION_RADIUS_RATIO,
  buildAppleContour,
} from "../src/apple";
import { uniformRadii, type ShapeChannels, type Vec2 } from "../src/channels";
import { APPLE_RSUPN, coefficientsAt, FIGMA_RSUPN_TABLE } from "../src/coefficients";
import { buildReferenceContour, type Contour, segmentLength, segmentPoint } from "../src/contour";
import { resolveCornerConstruction } from "../src/corner";
import { resolveCorner, resolveFromChannels, resolveShape, toContour } from "../src/shape";
import { say } from "./harness/say";

type Point2 = readonly [number, number];

/** The channel vector `registerHost` builds for a surface of this size and radius. */
function channels(size: Vec2, radius: number, smoothing = 0): ShapeChannels {
  return { center: [0, 0], size, radii: uniformRadii(radius), smoothing, thickness: 8 };
}

// ---------------------------------------------------------------------------
// contour distance
// ---------------------------------------------------------------------------

/** Dense polyline of a contour, at most `step` between consecutive points. */
function sample(contour: Contour, step: number): Point2[] {
  const points: Point2[] = [];
  for (const segment of contour.segments) {
    const count = Math.max(2, Math.ceil(segmentLength(segment, 128) / step));
    for (let index = 0; index < count; index += 1) {
      const point = segmentPoint(segment, index / count);
      points.push([point.x, point.y]);
    }
  }
  return points;
}

/**
 * A uniform-grid nearest-point index. The polylines here run to tens of
 * thousands of points and the honest Hausdorff is quadratic in that, which is
 * minutes rather than the milliseconds a unit suite may spend; bucketing the
 * target at one pixel makes it linear without approximating anything, because
 * the search only stops once the best distance found is inside the ring already
 * scanned.
 */
class NearestIndex {
  private readonly cell = 1;
  private readonly buckets = new Map<string, Point2[]>();

  constructor(points: readonly Point2[]) {
    for (const point of points) {
      const key = `${Math.floor(point[0] / this.cell)},${Math.floor(point[1] / this.cell)}`;
      const bucket = this.buckets.get(key);
      if (bucket === undefined) this.buckets.set(key, [point]);
      else bucket.push(point);
    }
  }

  distanceTo(x: number, y: number): number {
    const cx = Math.floor(x / this.cell);
    const cy = Math.floor(y / this.cell);
    let best = Number.POSITIVE_INFINITY;
    for (let ring = 0; ring < 4096; ring += 1) {
      for (let i = cx - ring; i <= cx + ring; i += 1) {
        for (let j = cy - ring; j <= cy + ring; j += 1) {
          if (ring > 0 && Math.abs(i - cx) !== ring && Math.abs(j - cy) !== ring) continue;
          const bucket = this.buckets.get(`${i},${j}`);
          if (bucket === undefined) continue;
          for (const [ox, oy] of bucket) {
            const distance = (x - ox) * (x - ox) + (y - oy) * (y - oy);
            if (distance < best) best = distance;
          }
        }
      }
      if (best < Number.POSITIVE_INFINITY && Math.sqrt(best) <= ring * this.cell) break;
    }
    return Math.sqrt(best);
  }
}

/** Symmetric Hausdorff distance between two contours, in the contours' units. */
function hausdorff(a: Contour, b: Contour, step = 0.01): number {
  const pa = sample(a, step);
  const pb = sample(b, step);
  const ia = new NearestIndex(pa);
  const ib = new NearestIndex(pb);
  let worst = 0;
  for (const [x, y] of pa) worst = Math.max(worst, ib.distanceTo(x, y));
  for (const [x, y] of pb) worst = Math.max(worst, ia.distanceTo(x, y));
  return worst;
}

/** Exact signed distance to a circular rounded rectangle at the origin, negative inside. */
function stadiumDistance(x: number, y: number, halfW: number, halfH: number, r: number): number {
  const qx = Math.abs(x) - (halfW - r);
  const qy = Math.abs(y) - (halfH - r);
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - r;
}

function maxDistanceToStadium(contour: Contour, halfW: number, halfH: number): number {
  const r = Math.min(halfW, halfH);
  let worst = 0;
  for (const [x, y] of sample(contour, 0.01)) {
    worst = Math.max(worst, Math.abs(stadiumDistance(x, y, halfW, halfH, r)));
  }
  return worst;
}

// ---------------------------------------------------------------------------
// the capsule on the render path
// ---------------------------------------------------------------------------

describe("a capsule is a stadium on the render path, under either reference", () => {
  const CAPSULES: readonly Vec2[] = [
    [120, 44],
    [44, 44],
  ];

  for (const size of CAPSULES) {
    for (const reference of ["apple-continuous", "figma-smoothing"] as const) {
      it(`${size[0]}x${size[1]} under ${reference}: r 22, reach 22, smoothing 0`, () => {
        const radius = Math.min(size[0], size[1]) / 2;
        // What the renderer does: channels in, family carried but never read.
        const shape = resolveFromChannels(channels(size, radius), reference, "capsule");
        expect(shape.corner.radius).toBe(radius);
        expect(shape.corner.reach).toBe(radius);
        expect(shape.corner.smoothingEff).toBe(0);
        // Smoothing 0 is the row the coefficient table holds exactly zero at, so
        // the field is exact on a stadium under either reference — the property
        // `corner.ts` calls the capsule limit, now reachable from the render path.
        expect(shape.corner.k).toEqual([0, 0, 0, 0, 0]);
        expect(maxDistanceToStadium(toContour(shape), size[0] / 2, size[1] / 2)).toBeLessThan(1e-9);
      });
    }
  }

  it("carries the compressed shoulder as a flag on the resolved corner, not only the contour", () => {
    // Half of why the defect survived nineteen waves: the renderer resolves and
    // never builds a contour, and only the contour builder said anything.
    const apple = resolveFromChannels(channels([120, 44], 22), "apple-continuous", "capsule");
    expect(apple.corner.saturated).toBe(true);
    const figma = resolveFromChannels(channels([120, 44], 22), "figma-smoothing", "capsule");
    expect(figma.corner.saturated).toBe(false);
    // The reference is not rewritten by the policy: an Apple corner stays Apple's.
    expect(apple.corner.reference).toBe("apple-continuous");
  });

  it("resolves a capsule the same way from the spec path and the render path", () => {
    const spec = resolveShape({ family: "capsule", center: [0, 0], size: [120, 44], thickness: 8 });
    const render = resolveFromChannels(channels([120, 44], 22), "apple-continuous", "capsule");
    expect(render.corner.radius).toBe(spec.corner.radius);
    expect(render.corner.reach).toBe(spec.corner.reach);
    expect(render.corner.smoothingEff).toBe(spec.corner.smoothingEff);
    expect(render.corner.k).toEqual(spec.corner.k);
    expect(hausdorff(toContour(render), toContour(spec))).toBeLessThan(1e-9);
  });
});

// ---------------------------------------------------------------------------
// the general case above and below the crossing
// ---------------------------------------------------------------------------

describe("the Apple reference keeps the radius and compresses the shoulder", () => {
  it("resolves a 120x44 at r 18 (ratio 0.409) at r 18, reach 22, smoothing 0.2222", () => {
    // The rung G0 measured natively: the radius clamp put this corner at 14.39
    // and stood a whole pixel and a half outside Apple's rim through the corner.
    const shape = resolveFromChannels(channels([120, 44], 18), "apple-continuous");
    expect(shape.corner.radius).toBe(18);
    expect(shape.corner.reach).toBe(22);
    expect(shape.corner.smoothingEff).toBeCloseTo(22 / 18 - 1, 12);
    expect(shape.corner.smoothingEff).toBeCloseTo(0.222222, 6);
    expect(shape.corner.saturated).toBe(true);
    // The curve above the crossing is the reference family's, so its correction
    // coefficients are that family's table at the compressed smoothing rather
    // than S2's Apple-direct fit against a dump this curve is no longer.
    expect(shape.corner.k).toEqual(coefficientsAt(FIGMA_RSUPN_TABLE, shape.corner.smoothingEff).k);
  });

  it("leaves everything below the crossing exactly where it was", () => {
    // The bed's rounded rectangles and the r 14 rung: the Apple-direct fit, the
    // published reach, and the dump's own contour, unchanged by this wave.
    const rows: readonly (readonly [Vec2, number])[] = [
      [[64, 32], 8],
      [[160, 96], 20],
      [[224, 128], 27],
      [[280, 160], 34],
      [[220, 130], 24],
      [[120, 56], 16],
      [[120, 44], 14],
    ];
    for (const [size, radius] of rows) {
      const shape = resolveFromChannels(channels(size, radius), "apple-continuous");
      expect(shape.corner.radius).toBe(radius);
      expect(shape.corner.reach).toBeCloseTo(APPLE_REACH * radius, 12);
      expect(shape.corner.smoothingEff).toBe(APPLE_CONTINUOUS_SMOOTHING_SEED);
      expect(shape.corner.k).toEqual(APPLE_RSUPN.k);
      expect(shape.corner.saturated).toBe(false);
      // and the contour is still Apple's dump, not the family's construction
      const dump = buildAppleContour(size[0] / 2, size[1] / 2, radius);
      expect(dump.saturated).toBe(false);
      expect(hausdorff(toContour(shape), dump)).toBeLessThan(1e-9);
    }
  });

  it("never lets the reach overflow the side, at any radius", () => {
    for (const radius of [0, 1, 8, 14, 14.4, 18, 22, 30, 1000]) {
      const corner = resolveCorner([120, 44], radius, 0, "apple-continuous");
      expect(corner.radius).toBeLessThanOrEqual(22);
      expect(corner.reach).toBeLessThanOrEqual(22 + 1e-12);
      expect(corner.smoothingEff).toBeGreaterThanOrEqual(0);
    }
  });
});

// ---------------------------------------------------------------------------
// the crossing
// ---------------------------------------------------------------------------

/**
 * The two curves at the crossing, in units of the radius.
 *
 * Below `r = budget / APPLE_REACH` the corner is Apple's dump; above it, the
 * reference family's construction at the same reach. The two are similar in r,
 * so the distance between them is a constant fraction of the radius, and it is
 * pinned here as that fraction. W20 Decision Log 2 made a blend conditional on
 * this exceeding the calibration grid's 0.5 px floor at the bed's sizes; it does
 * not, at either, so there is no blend and the switch is taken as it stands.
 */
const CROSSING_PER_R = 0.0064609;

describe("the crossing between the two constructions", () => {
  const SIZES: readonly Vec2[] = [
    [120, 44],
    [64, 30],
    [44, 44],
    [160, 96],
    [280, 160],
  ];

  it("is 0.0064609 r — 0.093 px on the bed's 44 px side, 0.063 px on its 30 px side", () => {
    const rows = SIZES.map((size) => {
      const halfW = size[0] / 2;
      const halfH = size[1] / 2;
      const budget = Math.min(halfW, halfH);
      const rStar = budget / APPLE_REACH;
      const below = buildAppleContour(halfW, halfH, rStar);
      const above = buildReferenceContour(
        halfW,
        halfH,
        resolveCornerConstruction(halfW, halfH, rStar, APPLE_CONTINUOUS_SMOOTHING_SEED),
      );
      // the crossing is where the constant names it: r / shortSide = 0.327083
      expect(rStar / Math.min(size[0], size[1])).toBeCloseTo(APPLE_SATURATION_RADIUS_RATIO, 12);
      return { size, rStar, distance: hausdorff(below, above) };
    });
    say(
      "\n=== the crossing: Apple's dump against the reference construction at the same reach ===\n" +
        rows
          .map(
            (entry) =>
              `${`${entry.size[0]}x${entry.size[1]}`.padEnd(9)} r* ${entry.rStar.toFixed(4).padStart(8)}` +
              `  hausdorff ${entry.distance.toFixed(6).padStart(9)} px` +
              `  = ${(entry.distance / entry.rStar).toFixed(8)} r`,
          )
          .join("\n"),
    );
    for (const entry of rows) {
      // 1e-5 r is the polyline's own spread: the curves are similar in r but the
      // 0.01 px sampling lands on them differently at different scales, and the
      // number being pinned is a shape property rather than a sampling one.
      expect(Math.abs(entry.distance / entry.rStar - CROSSING_PER_R)).toBeLessThan(1e-5);
      // The grid's floor, declared by G0 before it read anything.
      expect(entry.distance).toBeLessThan(0.5);
    }
    // The two bed sizes the wave's stops are stated on, in px.
    expect((rows[0] as { distance: number }).distance).toBeCloseTo(0.0930, 3);
    expect((rows[1] as { distance: number }).distance).toBeCloseTo(0.0635, 3);
  });

  it("is continuous in reach and in effective smoothing across it", () => {
    const rStar = 22 / APPLE_REACH;
    for (const delta of [-1e-9, -1e-12, 1e-12, 1e-9]) {
      const corner = resolveCorner([120, 44], rStar + delta, 0, "apple-continuous");
      expect(corner.reach).toBeCloseTo(22, 8);
      expect(corner.smoothingEff).toBeCloseTo(APPLE_CONTINUOUS_SMOOTHING_SEED, 8);
    }
    // and monotone, with the reach pinned at the budget the whole way up
    let previousSmoothing = Number.POSITIVE_INFINITY;
    for (let r = rStar; r <= 22; r += 0.05) {
      const corner = resolveCorner([120, 44], r, 0, "apple-continuous");
      expect(corner.reach).toBeCloseTo(22, 9);
      expect(corner.smoothingEff).toBeLessThanOrEqual(previousSmoothing + 1e-12);
      previousSmoothing = corner.smoothingEff;
    }
    expect(resolveCorner([120, 44], 22, 0, "apple-continuous").smoothingEff).toBe(0);
  });

  it("moves the contour by no more than the crossing itself as r sweeps through it", () => {
    // A morph that crosses the ratio must not snap. The step in contour position
    // per 0.002 px of radius is the crossing's own 0.093 px at the one step that
    // straddles it and nothing anywhere else.
    const rStar = 22 / APPLE_REACH;
    let worst = 0;
    let worstAt = 0;
    let previous: Contour | undefined;
    for (let index = -20; index <= 20; index += 1) {
      const r = rStar + index * 0.002;
      const contour = toContour(
        resolveFromChannels(channels([120, 44], r), "apple-continuous"),
      );
      if (previous !== undefined) {
        const step = hausdorff(previous, contour, 0.02);
        if (step > worst) {
          worst = step;
          worstAt = r;
        }
      }
      previous = contour;
    }
    say(`\ncontour step per 0.002 px of r across the crossing: ${worst.toFixed(6)} px at r ${worstAt.toFixed(4)}`);
    expect(worst).toBeCloseTo(CROSSING_PER_R * rStar, 3);
    expect(worst).toBeLessThan(0.5);
  });
});
