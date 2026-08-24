/**
 * Everything asserted about Apple's `.continuous` corner is RECOMPUTED here from
 * the raw control-point dump in src/apple.ts. Nothing is taken on trust from the
 * research that found the dump: if a control point were mistranscribed, the arc
 * identity below would fail.
 *
 * The load-bearing check is the handle-length identity. A cubic is a circular
 * arc only if its control handles have length (4/3)*tan(sweep/4)*R; that this
 * holds to 1.5e-7 for the middle cubic is what proves the middle segment is a
 * genuine circular arc rather than something arc-like.
 */

import { describe, expect, it } from 'vitest';
import {
  APPLE_DUMP,
  APPLE_REACH,
  APPLE_SATURATION_R_OVER_SIDE,
  buildAppleContour,
} from '../src/apple.js';
import {
  contourCurvatureBreaks,
  contourGap,
  contourTangentBreak,
  segCurvature,
} from '../src/contour.js';
import { APPLE_BEST_FIGMA_SMOOTHING, APPLE_TABLES } from '../src/coefficients.js';
import { figmaVsApple } from '../src/reference.js';

const sub = (a: number[], b: number[]) => [a[0] - b[0], a[1] - b[1]];
const dot = (a: number[], b: number[]) => a[0] * b[0] + a[1] * b[1];
const len = (a: number[]) => Math.hypot(a[0], a[1]);
const cross = (a: number[], b: number[]) => a[0] * b[1] - a[1] * b[0];
const deg = (r: number) => (r * 180) / Math.PI;

const [P0, C0a, C0b, J1, C1a, C1b, J2, C2a, C2b, P3] = APPLE_DUMP;

describe("Apple's continuous corner, recomputed from the control points", () => {
  it('reaches Apple\'s published cornerCurveExpansionFactor along each edge', () => {
    expect(P0[1]).toBeCloseTo(APPLE_REACH, 8);
    expect(P3[0]).toBeCloseTo(APPLE_REACH, 8);
    expect(P0[0]).toBe(0);
    expect(P3[1]).toBe(0);
  });

  it('meets the straight edge with zero curvature (G2 at that join only)', () => {
    // the first handle is axis-aligned with the edge...
    expect(sub(C0a, P0)[0]).toBe(0);
    // ...and the first two handles are collinear with it, forcing curvature 0
    expect(sub(C0b, P0)[0]).toBe(0);
    const seg = { kind: 'cubic' as const, p0: xy(P0), p1: xy(C0a), p2: xy(C0b), p3: xy(J1) };
    expect(segCurvature(seg, 0)).toBeLessThan(1e-12);
  });

  it('has a middle cubic that is a circular arc of radius 0.931253 r', () => {
    const mid = [0, 1].map((i) => (J1[i] + 3 * C1a[i] + 3 * C1b[i] + J2[i]) / 8);
    // by the corner's diagonal symmetry the centre lies on x == y
    const A = J1[0];
    const B = J1[1];
    const M = mid[0];
    const a = (2 * M * M - A * A - B * B) / (4 * M - 2 * (A + B));
    const centre = [a, a];
    expect(a).toBeCloseTo(0.950002, 6);

    const R = len(sub(J1, centre));
    expect(R).toBeCloseTo(0.931253, 6);
    expect(len(sub(J2, centre))).toBeCloseTo(R, 9);
    expect(len(sub(mid, centre))).toBeCloseTo(R, 9);

    const sweep = Math.acos(dot(sub(J1, centre), sub(J2, centre)) / (R * R));
    expect(deg(sweep)).toBeCloseTo(50, 3);

    // THE check: a cubic is a circular arc iff its handles have this length
    const wantHandle = (4 / 3) * Math.tan(sweep / 4) * R;
    expect(len(sub(C1a, J1))).toBeCloseTo(wantHandle, 6);
    expect(len(sub(C1b, J2))).toBeCloseTo(wantHandle, 6);
  });

  it('is NOT G1 at the shoulder/arc joins: a 2.4532 degree tangent break', () => {
    // Apple's documented "continuous curvature" does not hold here. vitrea
    // cannot be more faithful than this without deliberately departing from the
    // reference, and it bounds how precise a normal is worth chasing.
    for (const [tIn, tOut] of [
      [sub(J1, C0b), sub(C1a, J1)],
      [sub(J2, C1b), sub(C2a, J2)],
    ]) {
      const ang = deg(Math.abs(Math.atan2(cross(tIn, tOut), dot(tIn, tOut))));
      expect(ang).toBeCloseTo(2.4532, 3);
    }
  });

  it('saturates once the reach no longer fits in half the side', () => {
    expect(APPLE_SATURATION_R_OVER_SIDE).toBeCloseTo(0.327083, 6);
    const ok = buildAppleContour({ W: 250, H: 250, r: 160, smoothing: 0 });
    expect(ok.saturated).toBe(false);
    const sat = buildAppleContour({ W: 250, H: 250, r: 200, smoothing: 0 });
    expect(sat.saturated).toBe(true);
  });
});

describe('Apple contour assembly', () => {
  it('closes and is mirror-consistent', () => {
    const c = buildAppleContour({ W: 90, H: 55, r: 18, smoothing: 0 });
    expect(contourGap(c)).toBeLessThan(1e-9);
  });

  it('carries its tangent and curvature breaks through the assembly', () => {
    const c = buildAppleContour({ W: 64, H: 64, r: 1, smoothing: 0 });
    expect(deg(contourTangentBreak(c))).toBeCloseTo(2.4532, 3);
    const breaks = contourCurvatureBreaks(c, 1);
    expect(Math.max(...breaks)).toBeCloseTo(0.355, 2);
    // zero at the joins with the straight edges
    expect(Math.min(...breaks)).toBeLessThan(1e-9);
  });
});

describe('the reference gap dominates the field error', () => {
  it("Figma's family cannot reach Apple's curve closer than ~2e-3 r", () => {
    const best = APPLE_BEST_FIGMA_SMOOTHING.radiusFixed;
    expect(best.smoothing).toBeGreaterThan(0.6);
    expect(best.smoothing).toBeLessThan(0.72);
    expect(best.hausdorffPerR).toBeGreaterThan(1.5e-3);
    expect(best.hausdorffPerR).toBeLessThan(2.5e-3);
  });

  it('the widely cited smoothing 0.6 is not the best match', () => {
    // 0.6 is folklore; the fitted value is ~0.66 and 0.6 is nearly 2x worse.
    const at06 = figmaVsApple(0.6, 1, 1, 500);
    const atBest = figmaVsApple(APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing, 1, 1, 500);
    expect(at06).toBeGreaterThan(atBest * 1.5);
  });

  it('fitting the field to Apple directly beats routing through Figma', () => {
    // This is the recommendation: the field family is reference-agnostic, so it
    // should be fit against whichever contour calibration designates rather than
    // inheriting the Figma family's own error.
    const direct = APPLE_TABLES['rsupn'].devPerR;
    const viaFigma = APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.hausdorffPerR;
    expect(direct).toBeLessThan(viaFigma);
    expect(direct).toBeLessThan(1e-3);
  });

  it('Figma at smoothing 0 is just a circular corner, far from Apple', () => {
    expect(figmaVsApple(0, 1, 1, 400)).toBeGreaterThan(1e-2);
  });
});

function xy(a: number[]) {
  return { x: a[0], y: a[1] };
}
