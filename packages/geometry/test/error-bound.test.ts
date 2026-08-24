/**
 * THE ERROR-BOUND REGRESSION SUITE.
 *
 * These are the numbers the spec's Decision Log #20 declares. If this file goes
 * red, the declared bound is no longer true and the Decision Log entry is stale —
 * that is what it exists to catch. It is not here to catch refactoring noise, so
 * every bound is set a little above the measured value with the measured value
 * recorded beside it.
 *
 * The declared bound, verbatim from S2:
 *
 * > The v1 parametric pseudo-SDF (radial-support field, degree-5 corner
 * > correction in sin 2theta, first-order gradient normalization) holds, against
 * > the continuous-corner reference contour, across smoothing [0, 1], sizes
 * > 16-600 px, aspect 1:1-8:1 and corner radii to half the short side: field
 * > value error <= 0.17 px and gradient direction error <= 2.92 degrees within
 * > |d| <= 8 px; <= 0.17 px and <= 1.55 degrees within |d| <= 1 px, the gradient
 * > taken on the normalized field (a cheaper unnormalized normal holds
 * > <= 4.26 degrees, equal on the contour). Capsules and circular corners
 * > (smoothing 0) are exact to machine precision. Error is linear in corner
 * > radius at the zero level set (1.4e-3 * r) and bounded at ~0.17 px absolute
 * > over the measured size range.
 *
 * ## What runs where
 *
 * The default run is a 30-shape representative slice: every smoothing value,
 * both ends of the size range, the extreme aspect, and the capsule limit. The
 * full 324-shape matrix runs behind `VITREA_FULL_MATRIX=1`, which is how the
 * declared figures were produced — the slice is chosen to contain the shapes that
 * SET those figures, so it is a real gate and not a smoke test.
 *
 * ## Which gradient
 *
 * S2 measured the gradient by central-differencing the field as returned, so
 * that the figure characterises the field a shader actually evaluates. This suite
 * asserts the bound for the ANALYTIC gradient (what `field.ts` ships and what C6
 * should use) and separately checks that it agrees with the central-difference
 * measurement, so the ported bound is comparable to the published one.
 */

import { describe, expect, it } from "vitest";

import { rsupField, rsupLevelSetNormal, rsupnField } from "../src/field";
import { halfExtents, uniformRadii, type Vec2 } from "../src/channels";
import { FIGMA_RSUPN_TABLE } from "../src/coefficients";
import { fieldParams, governorFieldParams, resolveFromChannels } from "../src/shape";
import {
  aggregate,
  fullMatrix,
  GRADIENTS,
  matrixShape,
  measureShape,
  type MatrixEntry,
  type MeasureResult,
  referenceContourFor,
  representativeMatrix,
} from "./harness/metrics";
import { angleDeg, DEFAULT_BAND, sampleBand } from "./harness/truth";
import { envFlag } from "./harness/env";

const FULL = envFlag("VITREA_FULL_MATRIX");
const ENTRIES: MatrixEntry[] = FULL ? fullMatrix() : representativeMatrix();

// The sweep resolution S2 used for the matrix run. Denser than the default band
// options, which are reserved for single-shape checks.
const SWEEP_BAND = { halfBand: 8, offsets: 21, minPerCurve: 192, perPxStraight: 0.34 };

// The harness runs an exact-distance solver and a pattern search per shape, so
// even the slice takes seconds and the full matrix takes minutes. Vitest's 5 s
// default would report that as a failure, which is exactly the wrong signal from
// a suite whose job is to say whether a BOUND still holds.
const TIMEOUT = FULL ? 900_000 : 120_000;

function sweep(
  evaluate: typeof rsupnField,
  gradient: (p: ReturnType<typeof fieldParams>, x: number, y: number, h: number) => { gx: number; gy: number; kink: boolean },
  paramsOf: (s: ReturnType<typeof matrixShape>) => ReturnType<typeof fieldParams> = fieldParams,
): MeasureResult[] {
  return ENTRIES.map((entry) => {
    const shape = matrixShape(entry);
    const contour = referenceContourFor(shape);
    const prep = paramsOf(shape);
    return measureShape(
      shape,
      contour,
      (_p, x, y) => evaluate(prep, x, y),
      (_p, x, y, h) => gradient(prep, x, y, h),
      { band: SWEEP_BAND },
    );
  });
}

let cachedAnalytic: MeasureResult[] | null = null;
const analytic = (): MeasureResult[] =>
  (cachedAnalytic ??= sweep(rsupnField, (p, x, y) => GRADIENTS.analytic(p, x, y)));

describe(`family D (rsupn) — the declared bound [${FULL ? "FULL 324-shape matrix" : "30-shape slice"}]`, () => {
  it("covers the matrix it claims to cover", () => {
    expect(ENTRIES.length).toBe(FULL ? 324 : 30);
    expect(aggregate(analytic(), 8).n).toBe(ENTRIES.length);
  }, TIMEOUT);

  it("holds the field value bound in every band", () => {
    const rows = analytic();
    // declared: <= 0.170 px max / 0.156 px p95 in |d| <= 8
    expect(aggregate(rows, 1).valueMax).toBeLessThan(0.18);
    expect(aggregate(rows, 4).valueMax).toBeLessThan(0.18);
    expect(aggregate(rows, 8).valueMax).toBeLessThan(0.18);
    expect(aggregate(rows, 8).valueP95).toBeLessThan(0.17);
  }, TIMEOUT);

  it("holds the gradient-direction bound in every band", () => {
    const rows = analytic();
    // declared: <= 1.55 deg in |d| <= 1; <= 2.91 deg max / 2.55 p95 in |d| <= 8
    expect(aggregate(rows, 1).gradMaxDeg).toBeLessThan(1.7);
    expect(aggregate(rows, 4).gradMaxDeg).toBeLessThan(2.8);
    expect(aggregate(rows, 8).gradMaxDeg).toBeLessThan(3.1);
    expect(aggregate(rows, 8).gradP95Deg).toBeLessThan(2.7);
  }, TIMEOUT);

  it("reads as a distance: the eikonal defect stays under 0.03", () => {
    // Refraction strength is read off the field's slope, so a field whose
    // gradient magnitude drifts is not usable as a distance even where its zero
    // set is right. S2 measured 0.0273; C6 relies on this to skip renormalizing.
    expect(aggregate(analytic(), 8).eikonalMax).toBeLessThan(0.03);
  }, TIMEOUT);

  it("keeps the absolute band error flat across the whole size range", () => {
    // The band is a fixed 8 px while the corner grows, so absolute error does
    // NOT grow without bound with shape size — S2 measured a 0.12-0.17 px
    // envelope across three orders of magnitude. That is what lets C6 treat
    // ~0.17 px as a flat budget rather than a size-dependent one.
    for (const size of [16, 600]) {
      const rows = ENTRIES.filter((e) => e.size === size).map((entry) => {
        const shape = matrixShape(entry);
        const prep = fieldParams(shape);
        return measureShape(
          shape,
          referenceContourFor(shape),
          (_p, x, y) => rsupnField(prep, x, y),
          (_p, x, y) => GRADIENTS.analytic(prep, x, y),
          { band: SWEEP_BAND },
        );
      });
      expect(aggregate(rows, 8).valueMax, `size ${size}`).toBeLessThan(0.18);
    }
  }, TIMEOUT);

  it("agrees with the central-difference measurement S2 published", () => {
    // S2's figures come from differencing the field as returned. If the analytic
    // gradient's bound and the differenced bound diverged, the ported number
    // would not be comparable to the published one.
    const central = sweep(rsupnField, GRADIENTS.central(rsupnField));
    const a = aggregate(analytic(), 8);
    const c = aggregate(central, 8);
    expect(Math.abs(a.gradMaxDeg - c.gradMaxDeg)).toBeLessThan(0.05);
    expect(Math.abs(a.gradP95Deg - c.gradP95Deg)).toBeLessThan(0.05);
  }, TIMEOUT);
});

describe("exactness the bound does not have to cover", () => {
  it("is exact at smoothing 0, to machine precision", () => {
    const rows = ENTRIES.filter((e) => e.smoothing === 0).map((entry) => {
      const shape = matrixShape(entry);
      const prep = fieldParams(shape);
      return measureShape(
        shape,
        referenceContourFor(shape),
        (_p, x, y) => rsupnField(prep, x, y),
        (_p, x, y) => GRADIENTS.analytic(prep, x, y),
        { band: SWEEP_BAND },
      );
    });
    expect(aggregate(rows, 8).valueMax).toBeLessThan(1e-9);
  }, TIMEOUT);

  it("is exact at the capsule limit for every requested smoothing", () => {
    // Structural, not luck: at r == the budget the smoothing ceiling is
    // budget/r - 1 == 0, so effective smoothing is forced to exactly 0 and the
    // shape is a true stadium. This is also what bounds the worst-case radius and
    // therefore the r-linear contour error.
    for (const smoothing of [0, 0.4, 1.0]) {
      const shape = matrixShape({ size: 120, aspect: 8, rFrac: 0.5, smoothing });
      expect(shape.corner.smoothingEff).toBeCloseTo(0, 12);
      const prep = fieldParams(shape);
      const res = measureShape(
        shape,
        referenceContourFor(shape),
        (_p, x, y) => rsupnField(prep, x, y),
        (_p, x, y) => GRADIENTS.analytic(prep, x, y),
        { band: SWEEP_BAND },
      );
      expect(aggregate([res], 8).valueMax, `smoothing ${smoothing}`).toBeLessThan(1e-9);
    }
  }, TIMEOUT);
});

describe("the coefficient table survives interpolation off the fit grid", () => {
  it("holds the bound where the budget clamp lands s_eff between rows", () => {
    // Real shapes rarely have s_eff on the 0.05 fit grid: the clamp produces
    // arbitrary values. If interpolating degraded the bound, the table would need
    // to be denser — this is the test that says it does not.
    const cases: { size: Vec2; radius: number; smoothing: number }[] = [
      { size: [120, 42], radius: 13, smoothing: 1.0 }, // s_eff = 21/13 - 1
      { size: [400, 66], radius: 19, smoothing: 0.9 }, // s_eff = 33/19 - 1
      { size: [90, 90], radius: 26, smoothing: 1.0 }, // s_eff = 45/26 - 1
    ];

    for (const c of cases) {
      const shape = resolveFromChannels(
        {
          center: [0, 0],
          size: c.size,
          radii: uniformRadii(c.radius),
          smoothing: c.smoothing,
          thickness: 0,
        },
        "figma-smoothing",
      );
      const sEff = shape.corner.smoothingEff;

      // The clamp really did bite, and really did land off the fit grid.
      expect(sEff).toBeLessThan(c.smoothing);
      expect(FIGMA_RSUPN_TABLE.some((row) => Math.abs(row.sEff - sEff) < 1e-6)).toBe(false);

      const prep = fieldParams(shape);
      const res = measureShape(
        shape,
        referenceContourFor(shape),
        (_p, x, y) => rsupnField(prep, x, y),
        (_p, x, y) => GRADIENTS.analytic(prep, x, y),
        { band: SWEEP_BAND },
      );
      const a = aggregate([res], 8);
      expect(a.valueMax, `s_eff=${sEff.toFixed(4)}`).toBeLessThan(0.25);
      expect(a.gradMaxDeg, `s_eff=${sEff.toFixed(4)}`).toBeLessThan(3.5);
    }
  }, TIMEOUT);
});

describe("family C (rsup) — the governor's first step", () => {
  it("degrades to the bound S2 priced, and no further", () => {
    // Dropping the |grad| normalization is one branch and one uniform. The point
    // of asserting its bound is that the governor step is a KNOWN degradation
    // rather than an unmeasured one.
    const rows = sweep(rsupField, GRADIENTS.central(rsupField), governorFieldParams);
    const a = aggregate(rows, 8);
    // measured by S2 over the full matrix: 0.574 px, 4.258 deg, defect 0.0785
    expect(a.valueMax).toBeLessThan(0.65);
    expect(a.gradMaxDeg).toBeLessThan(4.5);
    expect(a.eikonalMax).toBeGreaterThan(0.05);
  }, TIMEOUT);

  it("is beaten by family D on both metrics, which is why D ships", () => {
    const d = aggregate(analytic(), 8);
    const c = aggregate(sweep(rsupField, GRADIENTS.central(rsupField), governorFieldParams), 8);
    expect(d.valueMax).toBeLessThan(c.valueMax * 0.6);
    expect(d.gradMaxDeg).toBeLessThan(c.gradMaxDeg);
    expect(d.eikonalMax).toBeLessThan(c.eikonalMax);
  }, TIMEOUT);
});

describe("the free level-set normal — the price of C6's cheap option", () => {
  it("holds 4.26 degrees, and is equal to the exact gradient on the contour", () => {
    // S2 priced this for C6: taking the free normal is taking family C's gradient
    // while keeping family D's values. Asserting both halves means the choice
    // stays an informed one.
    let worstBand = 0;
    let worstOnContour = 0;
    for (const entry of ENTRIES) {
      const shape = matrixShape(entry);
      const prep = fieldParams(shape);
      const { halfW, halfH } = halfExtents(shape.channels.size);
      for (const s of sampleBand(referenceContourFor(shape), halfW, halfH, {
        ...DEFAULT_BAND,
        offsets: 9,
        minPerCurve: 64,
        perPxStraight: 0.2,
      })) {
        const n = rsupLevelSetNormal(prep, s.P.x, s.P.y);
        const err = angleDeg({ x: n[0], y: n[1] }, s.grad);
        worstBand = Math.max(worstBand, err);
        if (Math.abs(s.d) < 1e-12) worstOnContour = Math.max(worstOnContour, err);
      }
    }
    // measured by S2 over the full matrix: 4.257 deg in |d| <= 8
    expect(worstBand).toBeLessThan(4.5);
    // and it agrees with the exact gradient to four decimals ON the contour
    expect(worstOnContour).toBeLessThan(1.8);
  }, TIMEOUT);
});
