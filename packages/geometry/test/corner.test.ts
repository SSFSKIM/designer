/**
 * The budget clamp (X8 rider 1). Three properties carry weight, and each of them
 * is load-bearing somewhere else in the kernel.
 */

import { describe, expect, it } from "vitest";

import { cornerBudget, resolveCornerConstruction, smoothingCeiling } from "../src/corner";

describe("the rounding-and-smoothing budget", () => {
  it("is half the short side", () => {
    expect(cornerBudget(50, 20)).toBe(20);
    expect(cornerBudget(20, 50)).toBe(20);
    expect(cornerBudget(30, 30)).toBe(30);
  });

  it("clamps the radius before the smoothing, since an over-budget radius is honourable at no smoothing", () => {
    const c = resolveCornerConstruction(50, 20, 999, 1);
    expect(c.radius).toBe(20);
    expect(c.smoothingEff).toBe(0);
    expect(c.reach).toBe(20);
  });

  it("forces effective smoothing to exactly 0 at the capsule limit", () => {
    // This is why a capsule is exact rather than approximated: r == budget makes
    // the ceiling budget/r - 1 == 0. Every pseudo-SDF family is exact on a
    // stadium, so the exactness is structural and not a special case.
    for (const requested of [0, 0.25, 0.5, 0.75, 1]) {
      const c = resolveCornerConstruction(90, 24, 24, requested);
      expect(c.smoothingEff, `requested ${requested}`).toBe(0);
      expect(c.arcSectionLength).toBeCloseTo(24 * Math.SQRT2 * Math.sin(Math.PI / 4), 12);
    }
  });

  it("reaches smoothing 1.0 only when the radius is at most a quarter of the short side", () => {
    // The other half of what the clamp buys: it bounds the worst-case radius, and
    // the field's contour deviation is linear in radius. Without this the r-linear
    // error would be unbounded at high smoothing.
    expect(smoothingCeiling(25, 100)).toBe(3);
    expect(smoothingCeiling(50, 100)).toBe(1);
    expect(smoothingCeiling(60, 100)).toBeCloseTo(2 / 3, 12);
    // at exactly a quarter of the short side (budget = half the side)
    const c = resolveCornerConstruction(200, 100, 50, 1);
    expect(c.smoothingEff).toBe(1);
  });

  it("is continuous in size, so a shrinking morph does not snap", () => {
    // S2: d s_eff / d size = 1/r while clamped, 0 after. A discontinuity here
    // would show as a visible pop mid-morph, so it is asserted rather than
    // reasoned about — sweep the size right through the point where the clamp
    // starts biting and check the effective smoothing never jumps.
    const radius = 20;
    const requested = 1;
    let prev: number | null = null;
    let maxJump = 0;
    const step = 0.05;
    for (let halfH = 15; halfH <= 60; halfH += step) {
      const s = resolveCornerConstruction(300, halfH, radius, requested).smoothingEff;
      if (prev !== null) maxJump = Math.max(maxJump, Math.abs(s - prev));
      prev = s;
    }
    // While clamped the slope is 1/r = 0.05 per unit of halfW/halfH, so a step of
    // 0.05 moves s_eff by at most 0.0025. Anything larger is a discontinuity.
    expect(maxJump).toBeLessThan(0.003);
  });

  it("releases the clamp exactly where the reach fits the budget", () => {
    // budget 40, r 20, requested 0.8 -> reach 36 <= 40, so unclamped.
    expect(resolveCornerConstruction(300, 40, 20, 0.8).smoothingEff).toBeCloseTo(0.8, 12);
    // budget 30, r 20, requested 0.8 -> ceiling is 30/20 - 1 = 0.5.
    expect(resolveCornerConstruction(300, 30, 20, 0.8).smoothingEff).toBeCloseTo(0.5, 12);
  });

  it("degenerates cleanly at radius 0 — a plain rectangle", () => {
    const c = resolveCornerConstruction(50, 20, 0, 1);
    expect(c.radius).toBe(0);
    expect(c.reach).toBe(0);
    expect(c.arcSectionLength).toBe(0);
  });

  it("keeps the cubic offsets consistent with the reach", () => {
    // The construction's invariant: the shoulder cubics plus the arc section plus
    // the joining offsets exactly span the reach. If this drifts, the corner no
    // longer meets the straight edge where the field's corner sector begins.
    for (const smoothing of [0, 0.2, 0.5, 0.8, 1]) {
      const c = resolveCornerConstruction(120, 80, 25, smoothing);
      // a = 2b and b = (reach - L - c - d)/3, so a+b+c+d+L collapses to exactly
      // the reach. That identity is what puts the corner's end on the straight
      // edge precisely where the field's corner sector begins.
      expect(c.a + c.b + c.c + c.d + c.arcSectionLength, `smoothing ${smoothing}`).toBeCloseTo(
        c.reach,
        9,
      );
      expect(c.a).toBeCloseTo(2 * c.b, 12);
    }
  });
});
