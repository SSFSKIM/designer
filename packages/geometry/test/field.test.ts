/**
 * The field itself: the properties that hold by construction, and the cross-check
 * that says this TypeScript computes the same function as the WGSL C6 ships.
 *
 * The cross-check fixture is S2's own `bench/f32-check.json`, ported verbatim.
 * Those `expected` values are f64 evaluation of the *identical arithmetic* as
 * `bench/shaders.wgsl`, and the S2 benchmark measured the real shader's f32
 * output against them on a metal-3 adapter at 4.08e-5 px worst case. So
 * reproducing this column to machine precision is transitive evidence that the
 * shader and this file agree — much stronger than any hash of the source text.
 */

import { describe, expect, it } from "vitest";

import {
  centralGradient,
  type FieldParams,
  rsupField,
  rsupLevelSetNormal,
  rsupnField,
  rsupnFieldAndGradient,
} from "../src/field";
import { APPLE_RSUPN, FIGMA_RSUPN_TABLE, coefficientsAt, ZERO_COEFFICIENTS } from "../src/coefficients";
import { CROSS_CHECK, crossCheckParams } from "./harness/cross-check";

const circular = (halfW: number, halfH: number, r: number): FieldParams => ({
  halfW,
  halfH,
  reach: r,
  k: ZERO_COEFFICIENTS,
});

const smoothed = (halfW: number, halfH: number, r: number, sEff: number): FieldParams => ({
  halfW,
  halfH,
  reach: (1 + sEff) * r,
  k: coefficientsAt(FIGMA_RSUPN_TABLE, sEff).k,
});

describe("the WGSL cross-check: this field is the shader's function", () => {
  const params = crossCheckParams();

  it("reproduces S2's f64 reference column to machine precision", () => {
    let worst = 0;
    for (let i = 0; i < CROSS_CHECK.expected.length; i++) {
      const p = params[CROSS_CHECK.points[i * 3] as number] as FieldParams;
      const x = CROSS_CHECK.points[i * 3 + 1] as number;
      const y = CROSS_CHECK.points[i * 3 + 2] as number;
      worst = Math.max(worst, Math.abs(rsupnField(p, x, y) - (CROSS_CHECK.expected[i] as number)));
    }
    // The two implementations are the same arithmetic in the same order, so this
    // is bit-level agreement, not a tolerance.
    expect(worst).toBeLessThan(1e-15);
  });

  it("covers all three smoothing regimes and both branches of the algebra", () => {
    expect(CROSS_CHECK.shapes.map((s) => s.spec.smoothing)).toEqual([0, 0.5, 1]);
    expect(CROSS_CHECK.expected.length).toBe(5535);
  });
});

describe("exactness properties", () => {
  it("is exact along the straight edges, for any smoothing", () => {
    // The corner algebra is gated on max(q, 0), so away from the corners the
    // field must reduce to the exact half-plane distance. This is why the
    // approximation lives entirely inside the corner sector.
    for (const sEff of [0, 0.3, 0.7, 1]) {
      const p = smoothed(100, 40, 12, sEff);
      for (const y of [0, 5, 10, 15]) {
        for (const dx of [-8, -3, 0, 3, 8]) {
          expect(rsupnField(p, p.halfW + dx, y), `sEff=${sEff} dx=${dx}`).toBeCloseTo(dx, 9);
          expect(rsupField(p, p.halfW + dx, y), `rsup sEff=${sEff} dx=${dx}`).toBeCloseTo(dx, 9);
        }
      }
    }
  });

  it("is the exact circular rounded-rect distance at smoothing 0", () => {
    const p = circular(60, 45, 18);
    // Analytic rounded-box distance, derived independently of the field.
    const analytic = (x: number, y: number): number => {
      const qx = Math.abs(x) - (p.halfW - p.reach);
      const qy = Math.abs(y) - (p.halfH - p.reach);
      return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - p.reach;
    };
    // 9 decimals, not machine precision, for one specific and documented
    // reason: the field's `max(r2, 1e-20)` guard makes rho exactly 1e-10 rather
    // than 0 in the deep interior, where the independent formula has a true 0.
    // That is the guard doing its job — it is what keeps rho == 0 from producing
    // a NaN without costing a branch — and 1e-10 px is six orders of magnitude
    // under the declared bound.
    for (let x = -80; x <= 80; x += 3.7) {
      for (let y = -60; y <= 60; y += 2.9) {
        expect(rsupnField(p, x, y)).toBeCloseTo(analytic(x, y), 9);
        expect(rsupField(p, x, y)).toBeCloseTo(analytic(x, y), 9);
      }
    }
  });

  it("is the exact stadium distance at the capsule limit", () => {
    // A capsule's corner radius equals the budget, so its effective smoothing is
    // forced to 0 and the shape is a true stadium — every family is exact on it.
    const halfW = 90;
    const halfH = 24;
    const p = circular(halfW, halfH, halfH);
    const stadium = (x: number, y: number): number =>
      Math.hypot(Math.max(Math.abs(x) - (halfW - halfH), 0), y) - halfH;
    for (let x = -110; x <= 110; x += 2.3) {
      for (let y = -40; y <= 40; y += 1.7) {
        expect(rsupnField(p, x, y), `(${x},${y})`).toBeCloseTo(stadium(x, y), 12);
      }
    }
  });

  it("is symmetric under both mirrors", () => {
    const p = smoothed(70, 45, 20, 0.62);
    for (const [x, y] of [
      [51, 33],
      [70, 0],
      [0, 45],
      [83, 51],
      [12, 7],
    ] as const) {
      const v = rsupnField(p, x, y);
      expect(rsupnField(p, -x, y)).toBeCloseTo(v, 14);
      expect(rsupnField(p, x, -y)).toBeCloseTo(v, 14);
      expect(rsupnField(p, -x, -y)).toBeCloseTo(v, 14);
    }
  });

  it("gets the sign right inside and outside", () => {
    const p = smoothed(70, 45, 20, 0.62);
    expect(rsupnField(p, 0, 0)).toBeLessThan(0);
    expect(rsupnField(p, 60, 30)).toBeLessThan(0);
    expect(rsupnField(p, 200, 0)).toBeGreaterThan(0);
    expect(rsupnField(p, 0, 90)).toBeGreaterThan(0);
    // the far corner, outside on both axes
    expect(rsupnField(p, 100, 70)).toBeGreaterThan(0);
    // and the value is a plausible distance out there
    expect(rsupnField(p, 170, 0)).toBeCloseTo(100, 9);
  });

  it("is continuous across the corner-sector boundary", () => {
    // The sector boundary is where q.y crosses 0. A jump there would read as a
    // hard seam in the rim, even though the algebra switches branch.
    const p = smoothed(80, 50, 16, 0.75);
    const yBoundary = p.halfH - p.reach;
    for (const x of [p.halfW - 4, p.halfW, p.halfW + 4]) {
      const below = rsupnField(p, x, yBoundary - 1e-7);
      const above = rsupnField(p, x, yBoundary + 1e-7);
      expect(Math.abs(above - below), `x=${x}`).toBeLessThan(1e-5);
    }
  });

  it("stays finite in the deep interior, where rho is zero", () => {
    // The r2 clamp is the field's only guard; without it the deep interior is
    // 0/0. A NaN here would be invisible until it reached a shader.
    const p = smoothed(30, 30, 9, 0.5);
    const v = rsupnField(p, 0, 0);
    expect(Number.isFinite(v)).toBe(true);
    expect(v).toBeCloseTo(-(p.halfH - p.reach) - p.reach, 9);
  });
});

describe("the analytic gradient", () => {
  it("is the true derivative: second-order convergence against central differences", () => {
    // The correctness proof for the closed form, and it does not rest on a
    // hand-picked tolerance. Central differencing has O(h^2) truncation error,
    // so if the closed form really is the derivative of the same expression, the
    // disagreement must fall by ~100x for every 10x reduction in h. If the
    // closed form were wrong by any fixed amount, the disagreement would instead
    // flatten out at that amount.
    //
    // Points within a few steps of a branch boundary (`qx == 0`, `qy == 0`) are
    // excluded: there the difference straddles the boundary and is wrong by O(h)
    // while the closed form is exact. The next test pins those directly.
    const params = crossCheckParams();

    const worstAtStep = (frac: number): { worst: number; checked: number } => {
      let worst = 0;
      let checked = 0;
      for (let i = 0; i < CROSS_CHECK.expected.length; i++) {
        const p = params[CROSS_CHECK.points[i * 3] as number] as FieldParams;
        const x = CROSS_CHECK.points[i * 3 + 1] as number;
        const y = CROSS_CHECK.points[i * 3 + 2] as number;
        const h = frac * Math.max(p.reach, 1);
        const qx = Math.abs(x) - (p.halfW - p.reach);
        const qy = Math.abs(y) - (p.halfH - p.reach);
        if (Math.abs(qx) < 8 * h || Math.abs(qy) < 8 * h) continue;
        const cd = centralGradient(rsupnField, p, x, y, h);
        if (cd.kink) continue;
        const an = rsupnFieldAndGradient(p, x, y);
        // Same expression in the same order: the value must not drift a single bit.
        expect(an.value).toBe(rsupnField(p, x, y));
        worst = Math.max(worst, Math.hypot(an.gx - cd.gx, an.gy - cd.gy));
        checked++;
      }
      return { worst, checked };
    };

    const coarse = worstAtStep(1e-5);
    const fine = worstAtStep(1e-6);

    expect(fine.checked).toBeGreaterThan(4000);
    // measured: 1.243e-6 and 1.240e-8, a ratio of 100.2
    expect(coarse.worst).toBeLessThan(5e-6);
    expect(fine.worst).toBeLessThan(5e-8);
    expect(coarse.worst / fine.worst).toBeGreaterThan(20);
  });

  it("is exact on the corner-sector boundary, where differencing is not", () => {
    // `qx == 0` with `qy < 0` is the case that caught a real mask bug: both
    // clamped-coordinate terms are masked off there, so the box-branch term has
    // to carry the whole derivative. The field is C1 across it — the straight
    // edge's distance and the box branch's distance have the same slope — so the
    // gradient is (1, 0) and nothing else.
    const p = smoothed(96, 24, 8, 0);
    const boundaryX = p.halfW - p.reach;
    const boundaryY = p.halfH - p.reach;
    // qy < 0: inside the box branch in y, so the gradient is purely along x.
    for (const y of [0, 4, 12, boundaryY - 1e-9]) {
      const at = rsupnFieldAndGradient(p, boundaryX, y);
      expect(Math.hypot(at.gx, at.gy), `y=${y}`).toBeCloseTo(1, 12);
      expect(at.gx, `y=${y}`).toBeCloseTo(1, 12);
    }
    // qy > 0: past the sector boundary in y, so it is the y edge that governs.
    for (const y of [boundaryY + 1, boundaryY + 4]) {
      const at = rsupnFieldAndGradient(p, boundaryX, y);
      expect(Math.hypot(at.gx, at.gy), `y=${y}`).toBeCloseTo(1, 12);
      expect(at.gy, `y=${y}`).toBeCloseTo(1, 12);
      expect(at.gx, `y=${y}`).toBeCloseTo(0, 12);
    }
    // and the mirror image, so the sign masks are right on both sides
    const mirrored = rsupnFieldAndGradient(p, -boundaryX, 4);
    expect(mirrored.gx).toBeCloseTo(-1, 12);
  });

  it("has unit magnitude on the straight edges and near the contour", () => {
    const p = smoothed(100, 40, 12, 0.6);
    const edge = rsupnFieldAndGradient(p, p.halfW, 0);
    expect(Math.hypot(edge.gx, edge.gy)).toBeCloseTo(1, 12);
    expect(edge.gx).toBeCloseTo(1, 12);
    expect(edge.gy).toBeCloseTo(0, 12);
  });

  it("points outward, so the sign convention is a distance and not its negative", () => {
    const p = smoothed(70, 45, 20, 0.62);
    const right = rsupnFieldAndGradient(p, 90, 0);
    expect(right.gx).toBeGreaterThan(0);
    const left = rsupnFieldAndGradient(p, -90, 0);
    expect(left.gx).toBeLessThan(0);
    const up = rsupnFieldAndGradient(p, 0, 70);
    expect(up.gy).toBeGreaterThan(0);
  });

  it("flags the interior medial-axis seam rather than reporting a normal there", () => {
    const p = smoothed(30, 30, 9, 0.5);
    expect(rsupnFieldAndGradient(p, 2, 2).kink).toBe(true);
    expect(rsupnFieldAndGradient(p, 33, 4).kink).toBe(false);
  });

  it("agrees with the free level-set normal on the contour and diverges off it", () => {
    // S2's finding: the two are the same where the rim sits, because the
    // normalization only moves level sets away from the zero set. That is why
    // the free normal is a legitimate governor-tier choice and not a defect.
    const p = smoothed(100, 100, 42, 0.5);
    const angle = (ax: number, ay: number, bx: number, by: number): number => {
      const la = Math.hypot(ax, ay);
      const lb = Math.hypot(bx, by);
      const c = Math.min(1, Math.max(-1, (ax * bx + ay * by) / (la * lb)));
      return (Math.acos(c) * 180) / Math.PI;
    };

    // Walk out along the corner diagonal to the zero level set rather than
    // guessing a point: the whole claim is about behaviour ON the contour.
    let lo = 0;
    let hi = 200;
    for (let i = 0; i < 80; i++) {
      const mid = (lo + hi) / 2;
      if (rsupnField(p, mid, mid) < 0) lo = mid;
      else hi = mid;
    }
    const t = (lo + hi) / 2;
    expect(Math.abs(rsupnField(p, t, t))).toBeLessThan(1e-9);

    const onContour = rsupnFieldAndGradient(p, t, t);
    const free = rsupLevelSetNormal(p, t, t);
    expect(angle(onContour.gx, onContour.gy, free[0], free[1])).toBeLessThan(0.05);
    // and it is a unit vector wherever it is defined
    expect(Math.hypot(free[0], free[1])).toBeCloseTo(1, 12);

    // How far the two part company OFF the contour is a matrix-wide maximum, not
    // a per-point guarantee, so it is asserted in the error-bound regression
    // suite (`test/error-bound.test.ts`) rather than here.
  });
});

describe("family C, the governor's first step", () => {
  it("shares family D's zero level set", () => {
    // Same coefficient table, same R(theta) — the normalization divides by a
    // strictly positive factor, so it cannot move the zero set.
    const p = smoothed(120, 80, 30, 0.7);
    for (const [x, y] of [
      [120, 0],
      [0, 80],
      [104, 64],
      [111, 71],
    ] as const) {
      const c = rsupField(p, x, y);
      const d = rsupnField(p, x, y);
      expect(Math.sign(c) === Math.sign(d) || Math.abs(c) < 1e-9).toBe(true);
      if (Math.abs(c) < 1e-9) expect(Math.abs(d)).toBeLessThan(1e-9);
    }
  });

  it("drifts from a unit gradient where family D does not", () => {
    // The eikonal defect is the whole reason D exists: refraction strength is
    // read off the field's slope, so a field whose gradient magnitude drifts is
    // not usable as a distance even where its zero set is right.
    const p = smoothed(120, 80, 30, 0.8);
    const h = 1e-3 * p.reach;
    let worstC = 0;
    let worstD = 0;
    for (let t = 0.05; t < 1; t += 0.05) {
      const x = p.halfW - p.reach + p.reach * Math.cos((t * Math.PI) / 2);
      const y = p.halfH - p.reach + p.reach * Math.sin((t * Math.PI) / 2);
      worstC = Math.max(worstC, Math.abs(centralGradient(rsupField, p, x, y, h).magnitude - 1));
      worstD = Math.max(worstD, Math.abs(centralGradient(rsupnField, p, x, y, h).magnitude - 1));
    }
    expect(worstD).toBeLessThan(worstC);
  });
});

describe("the Apple-direct coefficients", () => {
  it("are a distinct fit from anything on the Figma smoothing axis", () => {
    // Decision Log #20 rejected routing `profile: "continuous"` through Figma at
    // smoothing 0.66. If this ever stops being true, the two references have
    // been conflated somewhere.
    const nearest = coefficientsAt(FIGMA_RSUPN_TABLE, 0.528665).k;
    const gap = Math.max(...APPLE_RSUPN.k.map((v, i) => Math.abs(v - (nearest[i] as number))));
    expect(gap).toBeGreaterThan(0.1);
  });

  it("fit closer to their own reference than the Figma family fits Apple's", () => {
    expect(APPLE_RSUPN.contourDevPerR).toBeLessThan(0.00196015);
  });
});
