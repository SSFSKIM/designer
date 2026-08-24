/**
 * Validation of the ground-truth contour construction. These tests are what
 * make the error numbers trustworthy: if the reference contour is wrong, every
 * downstream figure is wrong in the same direction and nothing catches it.
 */

import { describe, expect, it } from 'vitest';
import {
  buildContour,
  contourArea,
  contourCurvatureBreaks,
  contourGap,
  contourLength,
  cornerParams,
  segCurvature,
  segDeriv,
  segPoint,
  contourTangentBreak,
  norm,
  type ShapeSpec,
} from '../src/contour.js';
import { exactSignedDistance, insideByRayCast } from '../src/truth.js';

const SMOOTHINGS = [0, 0.2, 0.4, 0.6, 0.8, 1.0];

describe('Figma-squircle corner construction', () => {
  it('closes exactly, for every smoothing', () => {
    for (const s of SMOOTHINGS) {
      const c = buildContour({ W: 60, H: 40, r: 16, smoothing: s });
      expect(contourGap(c), `smoothing=${s}`).toBeLessThan(1e-9);
    }
  });

  it('is G1 continuous: no tangent break between segments', () => {
    for (const s of SMOOTHINGS) {
      const c = buildContour({ W: 60, H: 40, r: 16, smoothing: s });
      // 1e-9 rad; this is the property that proves the arc/cubic joins were
      // derived consistently rather than merely joined positionally.
      expect(contourTangentBreak(c), `smoothing=${s}`).toBeLessThan(1e-9);
    }
  });

  it('reaches p = (1 + s) * r along each edge and is tangent to the bounding box', () => {
    for (const s of SMOOTHINGS) {
      const spec: ShapeSpec = { W: 60, H: 40, r: 12, smoothing: s };
      const cp = cornerParams(spec);
      expect(cp.p).toBeCloseTo((1 + cp.smoothingEff) * cp.r, 10);
      // the contour touches x = W at y = 0 and y = H at x = 0
      const c = buildContour(spec);
      expect(exactSignedDistance(c, { x: spec.W, y: 0 }).dist).toBeLessThan(1e-9);
      expect(exactSignedDistance(c, { x: 0, y: spec.H }).dist).toBeLessThan(1e-9);
    }
  });

  it('has zero curvature where the corner meets the straight edge', () => {
    for (const s of [0.2, 0.4, 0.6, 0.8, 1.0]) {
      const c = buildContour({ W: 60, H: 40, r: 12, smoothing: s });
      const cubic = c.segments.find((seg) => seg.kind === 'cubic');
      expect(cubic, `smoothing=${s}`).toBeDefined();
      expect(segCurvature(cubic!, 0), `smoothing=${s}`).toBeLessThan(1e-9);
    }
  });

  it('is G1 but NOT G2: the cubic meets the arc with a curvature step', () => {
    // Characterization, not aspiration. The family's cubics arrive at the
    // circular arc with curvature ~1.3-1.6 / r against the arc's own 1 / r, so
    // "continuous corner" here means continuous TANGENT plus a curvature RAMP,
    // not curvature continuity. C7 should expect a residual against Apple on
    // any metric that differentiates the normal (specular rim), and C3 should
    // not assume G2 anywhere.
    const r = 12;
    for (const s of [0.1, 0.2, 0.4, 0.6, 0.8]) {
      const c = buildContour({ W: 60, H: 40, r, smoothing: s });
      const breaks = contourCurvatureBreaks(c, r);
      expect(Math.max(...breaks), `smoothing=${s}`).toBeGreaterThan(0.35);
      expect(Math.max(...breaks), `smoothing=${s}`).toBeLessThan(0.6);
    }
  });

  it('smoothing = 1.0 is the only curvature-continuous member: the arc vanishes', () => {
    const r = 12;
    const c = buildContour({ W: 60, H: 40, r, smoothing: 1.0 });
    expect(c.segments.some((seg) => seg.kind === 'arc')).toBe(false);
    expect(Math.max(...contourCurvatureBreaks(c, r))).toBeLessThan(1e-9);
  });

  it('smoothing = 0 degenerates to the plain circular rounded rectangle', () => {
    const spec: ShapeSpec = { W: 50, H: 30, r: 10, smoothing: 0 };
    const c = buildContour(spec);
    expect(c.segments.some((s) => s.kind === 'cubic')).toBe(false);
    const arcs = c.segments.filter((s) => s.kind === 'arc');
    expect(arcs).toHaveLength(4);
    for (const a of arcs) {
      if (a.kind !== 'arc') continue;
      expect(a.radius).toBeCloseTo(10, 12);
      expect(Math.abs(a.sweep)).toBeCloseTo(Math.PI / 2, 12);
      expect(Math.abs(Math.abs(a.center.x) - (spec.W - 10))).toBeLessThan(1e-12);
      expect(Math.abs(Math.abs(a.center.y) - (spec.H - 10))).toBeLessThan(1e-12);
    }
  });

  it('the middle arc is the inscribed circle of radius r, tangent to both edges', () => {
    for (const s of SMOOTHINGS) {
      const spec: ShapeSpec = { W: 70, H: 45, r: 14, smoothing: s };
      const c = buildContour(spec);
      for (const seg of c.segments) {
        if (seg.kind !== 'arc') continue;
        expect(seg.radius).toBeCloseTo(14, 10);
        expect(Math.abs(seg.center.x), `s=${s}`).toBeCloseTo(spec.W - 14, 8);
        expect(Math.abs(seg.center.y), `s=${s}`).toBeCloseTo(spec.H - 14, 8);
      }
    }
  });

  it('area and perimeter both shrink monotonically as smoothing rises', () => {
    // The smoothed corner cuts more area than a circular arc of the same radius
    // and takes a shorter path doing it. Monotone in both, which is what makes
    // `smoothing` safe to interpolate as a morph channel (X8).
    let prevA = Infinity;
    let prevL = Infinity;
    for (const s of SMOOTHINGS) {
      const c = buildContour({ W: 60, H: 60, r: 15, smoothing: s });
      const A = contourArea(c);
      const L = contourLength(c);
      expect(A, `area at s=${s}`).toBeLessThan(prevA);
      expect(L, `perimeter at s=${s}`).toBeLessThan(prevL);
      prevA = A;
      prevL = L;
    }
  });
});

describe("Figma's rounding-and-smoothing budget", () => {
  it('clamps smoothing to 0 at the capsule limit, so a capsule is an exact stadium', () => {
    for (const s of SMOOTHINGS) {
      // r == half the short side == the budget
      const cp = cornerParams({ W: 120, H: 20, r: 20, smoothing: s });
      expect(cp.smoothingEff, `requested s=${s}`).toBeCloseTo(0, 12);
      expect(cp.p).toBeCloseTo(20, 12);
    }
  });

  it('caps effective smoothing at budget/r - 1', () => {
    // r / budget = 0.6 -> max smoothing 0.6667
    const cp = cornerParams({ W: 100, H: 25, r: 15, smoothing: 1 });
    expect(cp.smoothingEff).toBeCloseTo(25 / 15 - 1, 10);
    expect(cp.p).toBeLessThanOrEqual(25 + 1e-12);
  });

  it('never lets the corner reach exceed the budget, so corners cannot overlap', () => {
    for (const s of SMOOTHINGS) {
      for (const rFrac of [0.05, 0.15, 0.3, 0.45, 0.5]) {
        for (const [W, H] of [
          [8, 8],
          [60, 20],
          [300, 37.5],
        ]) {
          const budget = Math.min(W, H);
          const r = rFrac * 2 * budget;
          const cp = cornerParams({ W, H, r, smoothing: s });
          expect(cp.p).toBeLessThanOrEqual(budget + 1e-9);
        }
      }
    }
  });

  it('effective smoothing is continuous in size, so morphs do not snap', () => {
    const eff = (H: number) => cornerParams({ W: 200, H, r: 20, smoothing: 0.8 }).smoothingEff;
    const step = 0.25;
    let prev = eff(20);
    for (let H = 20 + step; H <= 60; H += step) {
      const cur = eff(H);
      // d(sEff)/dH = budget'/r = 1/r = 0.05 per px while capped, 0 after
      expect(Math.abs(cur - prev), `H=${H}`).toBeLessThan(0.05 * step + 1e-12);
      prev = cur;
    }
  });
});

describe('exact signed distance solver', () => {
  it('agrees with the closed form on a circle', () => {
    // a square with r == half the side is a circle
    const c = buildContour({ W: 20, H: 20, r: 20, smoothing: 0 });
    for (const [x, y] of [
      [0, 0],
      [5, 5],
      [19, 3],
      [25, 0],
      [14, 14],
      [30, 30],
    ]) {
      const got = exactSignedDistance(c, { x, y }).d;
      const want = Math.hypot(x, y) - 20;
      expect(got, `(${x},${y})`).toBeCloseTo(want, 9);
    }
  });

  it('agrees with the closed-form rounded-box SDF at smoothing 0', () => {
    const spec: ShapeSpec = { W: 47, H: 23, r: 9, smoothing: 0 };
    const c = buildContour(spec);
    const sdRoundBox = (x: number, y: number) => {
      const qx = Math.abs(x) - (spec.W - spec.r);
      const qy = Math.abs(y) - (spec.H - spec.r);
      return (
        Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - spec.r
      );
    };
    let worst = 0;
    for (let x = -60; x <= 60; x += 0.7) {
      for (let y = -35; y <= 35; y += 0.7) {
        worst = Math.max(worst, Math.abs(exactSignedDistance(c, { x, y }).d - sdRoundBox(x, y)));
      }
    }
    // The strongest single check available: two independent implementations of
    // the same shape must agree to machine precision.
    expect(worst).toBeLessThan(1e-9);
  });

  it('gradient is unit length and matches a finite-difference of the field', () => {
    const c = buildContour({ W: 55, H: 30, r: 14, smoothing: 0.6 });
    const h = 1e-5;
    for (const [x, y] of [
      [50, 25],
      [56, 28],
      [44, 31],
      [20, 33],
      [58, 5],
      [40, 20],
    ]) {
      const r0 = exactSignedDistance(c, { x, y });
      expect(Math.hypot(r0.grad.x, r0.grad.y)).toBeCloseTo(1, 12);
      const gx =
        (exactSignedDistance(c, { x: x + h, y }).d - exactSignedDistance(c, { x: x - h, y }).d) /
        (2 * h);
      const gy =
        (exactSignedDistance(c, { x, y: y + h }).d - exactSignedDistance(c, { x, y: y - h }).d) /
        (2 * h);
      const g = norm({ x: gx, y: gy });
      expect(g.x, `(${x},${y}) gx`).toBeCloseTo(r0.grad.x, 5);
      expect(g.y, `(${x},${y}) gy`).toBeCloseTo(r0.grad.y, 5);
    }
  });

  it('sign agrees with an independent even-odd ray cast', () => {
    for (const s of [0, 0.6, 1.0]) {
      const c = buildContour({ W: 40, H: 24, r: 11, smoothing: s });
      for (let x = -50; x <= 50; x += 1.3) {
        for (let y = -34; y <= 34; y += 1.1) {
          const r0 = exactSignedDistance(c, { x, y });
          if (r0.dist < 1e-3) continue; // ambiguous exactly on the contour
          expect(r0.d < 0, `s=${s} (${x},${y}) d=${r0.d}`).toBe(insideByRayCast(c, { x, y }, 512));
        }
      }
    }
  });

  it('Newton refinement actually converges: the closest point is a true local minimum', () => {
    const c = buildContour({ W: 33, H: 33, r: 12, smoothing: 0.75 });
    for (const [x, y] of [
      [30, 30],
      [26, 31],
      [35, 22],
      [24, 24],
    ]) {
      const r0 = exactSignedDistance(c, { x, y });
      const seg = c.segments[r0.segIndex];
      // stationarity of |C(t) - P|^2 unless the minimum is at an endpoint
      if (r0.t > 1e-6 && r0.t < 1 - 1e-6) {
        const d1 = segDeriv(seg, r0.t);
        const e = { x: segPoint(seg, r0.t).x - x, y: segPoint(seg, r0.t).y - y };
        const gradF = 2 * (e.x * d1.x + e.y * d1.y);
        expect(Math.abs(gradF) / Math.max(1, r0.dist)).toBeLessThan(1e-6);
      }
    }
  });
});
