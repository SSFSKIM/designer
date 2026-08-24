/**
 * Apple's measured `.continuous` corner, re-derived from the control points
 * alone.
 *
 * Every claim the kernel makes about Apple's curve is recomputed here from the
 * dump, so the dump is checked rather than trusted. The one that matters most is
 * the 2.4532-degree tangent break: it is the reference curve's OWN normal
 * discontinuity, and it is what makes the field's 1.55-degree rim-band gradient
 * error sufficient rather than merely small. If this number moved, the argument
 * for the declared bound would need re-making.
 */

import { describe, expect, it } from "vitest";

import {
  APPLE_BEST_FIGMA_SMOOTHING,
  APPLE_CONTINUOUS_SMOOTHING_SEED,
  APPLE_CORNER_DUMP,
  APPLE_REACH,
  APPLE_SATURATION_RADIUS_RATIO,
  buildAppleContour,
} from "../src/apple";
import { APPLE_RSUPN } from "../src/coefficients";
import {
  contourGap,
  type ContourSegment,
  contourTangentBreak,
  segmentCurvature,
  segmentPoint,
} from "../src/contour";
import { fieldParams, resolveShape } from "../src/shape";
import { rsupnField, rsupnFieldAndGradient } from "../src/field";
import { angleDeg, sampleBand } from "./harness/truth";

const DEG = 180 / Math.PI;

describe("the control-point dump, checked rather than trusted", () => {
  it("is three cubics per corner and nothing else", () => {
    expect(APPLE_CORNER_DUMP.length).toBe(10); // 3 cubics sharing endpoints
    const c = buildAppleContour(200, 120, 30);
    const corners = c.segments.filter((s) => s.kind === "cubic");
    expect(corners.length).toBe(12); // 4 corners x 3 cubics
    expect(c.segments.some((s) => s.kind === "arc")).toBe(false);
  });

  it("starts and ends on the straight edges at exactly the published reach", () => {
    const first = APPLE_CORNER_DUMP[0] as readonly [number, number];
    const last = APPLE_CORNER_DUMP[9] as readonly [number, number];
    expect(first[0]).toBe(0);
    expect(first[1]).toBeCloseTo(APPLE_REACH, 8);
    expect(last[1]).toBe(0);
    expect(last[0]).toBeCloseTo(APPLE_REACH, 8);
  });

  it("has a MIDDLE cubic that is a genuine circular arc, by the handle identity", () => {
    // The handle identity is the real proof. Radius and centre alone could be a
    // coincidence of the corner's symmetry; a control-handle length matching
    // (4/3)tan(sweep/4)*R to 1e-7 cannot be.
    const p0 = APPLE_CORNER_DUMP[3] as readonly [number, number];
    const p1 = APPLE_CORNER_DUMP[4] as readonly [number, number];
    const p2 = APPLE_CORNER_DUMP[5] as readonly [number, number];
    const p3 = APPLE_CORNER_DUMP[6] as readonly [number, number];

    // The arc is symmetric about the corner diagonal, so its centre lies on it.
    const chord = Math.hypot(p3[0] - p0[0], p3[1] - p0[1]);
    const handle = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);

    // Solve for (radius, sweep) from the chord and the handle, then check the
    // identity closes. sweep = 2*asin(chord/2R); handle = (4/3)tan(sweep/4)*R.
    let lo = chord / 2;
    let hi = 10 * chord;
    for (let i = 0; i < 200; i++) {
      const R = (lo + hi) / 2;
      const sweep = 2 * Math.asin(Math.min(1, chord / (2 * R)));
      const predicted = (4 / 3) * Math.tan(sweep / 4) * R;
      if (predicted > handle) lo = R;
      else hi = R;
    }
    const radius = (lo + hi) / 2;
    const sweep = 2 * Math.asin(Math.min(1, chord / (2 * radius)));

    // 4 decimals, not 5, and the reason is worth recording: this recovers the
    // radius by solving the handle identity against the chord, which is a
    // different estimator from the arc fit S2 ran. They agree to 5.2e-6 r
    // (0.9312478 here against S2's 0.931253) — two independent recoveries of the
    // same number, which is stronger evidence for "this cubic is an arc" than
    // either one alone would be.
    expect(radius).toBeCloseTo(0.931253, 4);
    expect(sweep * DEG).toBeCloseTo(50.0, 3);
    // and the identity really does close at that radius
    expect((4 / 3) * Math.tan(sweep / 4) * radius).toBeCloseTo(handle, 7);

    // the centre sits on the diagonal at 0.950002 r
    const mid = [(p0[0] + p3[0]) / 2, (p0[1] + p3[1]) / 2] as const;
    const h = Math.sqrt(Math.max(0, radius * radius - (chord / 2) ** 2));
    const centre = [mid[0] + h / Math.SQRT2, mid[1] + h / Math.SQRT2] as const;
    expect(centre[0]).toBeCloseTo(0.950002, 5);
    expect(centre[1]).toBeCloseTo(0.950002, 5);
    // p2 is the mirror of p1 about that diagonal, which is what makes it symmetric
    expect(p2[0]).toBeCloseTo(p1[1], 8);
    expect(p2[1]).toBeCloseTo(p1[0], 8);
  });

  it("meets the straight edge with ZERO curvature — G2 at the join that reads", () => {
    // The first two control points share the edge's x, which forces the first
    // cubic's second derivative along the edge to vanish. This is the join Apple
    // gets right, and the reason `.continuous` looks the way it does.
    const p0 = APPLE_CORNER_DUMP[0] as readonly [number, number];
    const p1 = APPLE_CORNER_DUMP[1] as readonly [number, number];
    const p2 = APPLE_CORNER_DUMP[2] as readonly [number, number];
    expect(p0[0]).toBe(0);
    expect(p1[0]).toBe(0);
    expect(p2[0]).toBe(0);

    const c = buildAppleContour(200, 120, 30);
    const shoulder = c.segments.find((s) => s.kind === "cubic") as ContourSegment;
    expect(segmentCurvature(shoulder, 0)).toBeLessThan(1e-12);
  });

  it("breaks tangent by 2.4532 degrees at the shoulder/arc joins", () => {
    // The number that calibrates the whole gradient budget. Apple's own path is
    // not G1 there, so "continuous curvature" holds at the straight-edge join and
    // nowhere else — and a pseudo-SDF whose rim-band gradient error peaks at 1.55
    // degrees is already below the target's own normal discontinuity.
    const c = buildAppleContour(200, 120, 30);
    expect(contourTangentBreak(c) * DEG).toBeCloseTo(2.4532, 3);
  });

  it("closes as a ring", () => {
    expect(contourGap(buildAppleContour(200, 120, 30))).toBeLessThan(1e-9);
  });
});

describe("Apple's budget policy is its own", () => {
  it("saturates the radius at r/side = 0.327083, not by reducing smoothing", () => {
    // The reference family clamps SMOOTHING; Apple clamps the RADIUS. C7 should
    // not compare shapes above this ratio to Apple at all — past it the real
    // corner warps in a way this construction does not reproduce.
    expect(APPLE_SATURATION_RADIUS_RATIO).toBeCloseTo(0.327083, 6);

    const halfShort = 60;
    const atLimit = buildAppleContour(200, halfShort, halfShort / APPLE_REACH);
    expect(atLimit.saturated).toBe(false);
    expect(atLimit.corner.reach).toBeCloseTo(halfShort, 9);

    const past = buildAppleContour(200, halfShort, halfShort);
    expect(past.saturated).toBe(true);
    // clamped, never overflowing the side
    expect(past.corner.reach).toBeLessThanOrEqual(halfShort + 1e-9);
  });

  it("keeps smoothing pinned, because Apple's curve has no smoothing parameter", () => {
    expect(APPLE_CONTINUOUS_SMOOTHING_SEED).toBeCloseTo(0.52866495, 8);
    const shape = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 120],
      radii: 30,
      profile: "continuous",
    });
    expect(shape.corner.reference).toBe("apple-continuous");
    expect(shape.corner.smoothingEff).toBeCloseTo(APPLE_CONTINUOUS_SMOOTHING_SEED, 12);
    expect(shape.corner.reach).toBeCloseTo(APPLE_REACH * 30, 9);
    expect(shape.corner.k).toEqual(APPLE_RSUPN.k);
  });
});

describe("the Apple-direct fit is what earns Decision Log #20", () => {
  it("holds a tight value bound against Apple's OWN contour", () => {
    // S2 measured 0.104 px max / 0.090 px p95 for this configuration, against
    // 0.670 px for the same field routed through Figma at smoothing 0.66. This is
    // the 6.4x that decided the reference.
    const shape = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [400, 240],
      radii: 60,
      profile: "continuous",
    });
    const contour = buildAppleContour(200, 120, shape.corner.radius);
    const prep = fieldParams(shape);

    let worst = 0;
    for (const seg of contour.segments) {
      for (let t = 0; t <= 1; t += 0.01) {
        const p = segmentPoint(seg, t);
        worst = Math.max(worst, Math.abs(rsupnField(prep, p.x, p.y)));
      }
    }
    // on-contour deviation: the declared Apple-direct contour fit is 6.06e-4 r
    expect(worst).toBeLessThan(0.0012 * shape.corner.radius);
  });

  it("is closer to Apple than any member of the Figma family can be", () => {
    // The finding that reframed the spike: the reference gap (1.96e-3 r at Figma's
    // best smoothing) EXCEEDS the field's own worst-case contour deviation
    // (1.38e-3 r). The intermediate family costs more accuracy than the field
    // approximation does.
    expect(APPLE_RSUPN.contourDevPerR).toBeLessThan(
      APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.hausdorffPerR,
    );
    // and the commonly cited 0.6 is nearly 2x worse than 0.66
    expect(APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing).toBe(0.66);
  });

  it("holds the Apple-direct band bound, inside the reference's own tangent break", () => {
    // The sufficiency argument made measurable. S2 reported 0.104 px / 1.752 deg
    // max for the Apple-direct fit; the point is not just that those are small
    // but that the gradient figure sits inside Apple's OWN 2.4532-degree normal
    // discontinuity, so the normal is not where fidelity is being lost.
    const shape = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [400, 240],
      radii: 60,
      profile: "continuous",
    });
    const contour = buildAppleContour(200, 120, shape.corner.radius);
    const prep = fieldParams(shape);

    let worstValue = 0;
    let worstGrad = 0;
    for (const sample of sampleBand(contour, 200, 120, {
      halfBand: 8,
      offsets: 17,
      minPerCurve: 128,
      perPxStraight: 0.3,
    })) {
      worstValue = Math.max(
        worstValue,
        Math.abs(rsupnField(prep, sample.P.x, sample.P.y) - sample.d),
      );
      const g = rsupnFieldAndGradient(prep, sample.P.x, sample.P.y);
      if (g.kink) continue;
      worstGrad = Math.max(worstGrad, angleDeg({ x: g.gx, y: g.gy }, sample.grad));
    }

    expect(worstValue).toBeLessThan(0.15);
    expect(worstGrad).toBeLessThan(2.4532);
  });
});
