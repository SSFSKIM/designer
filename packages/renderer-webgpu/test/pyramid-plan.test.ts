/**
 * The pyramid plan.
 *
 * §Performance envelope: "Effect-texture resolution is decoupled from DOM DPR."
 * That is the property these tests are about — the plan is a function of the
 * SOURCE's size and the resolution policy, never of the viewport, and the
 * analysis level's spatial frequency band stays fixed as the resolution moves so
 * the governor's own degradation cannot look like a change in the backdrop.
 */

import { describe, expect, it } from "vitest";

import {
  ANALYSIS_TARGET_EXTENT,
  bodyBlurPlan,
  CHAIN_SIGMA_AT_LEVEL_1,
  MAX_CHAIN_LEVELS,
  MIN_LEVEL_EXTENT,
  planPyramid,
} from "../src/pyramid-plan";

const full = { scale: 1, maxDimension: 2048 };

describe("planPyramid", () => {
  it("halves each level and stops before the shorter side goes unusable", () => {
    const plan = planPyramid(512, 256, full);

    expect(plan.levels[0]).toEqual({ width: 512, height: 256 });
    expect(plan.levels[1]).toEqual({ width: 256, height: 128 });
    for (const level of plan.levels) {
      expect(Math.min(level.width, level.height)).toBeGreaterThanOrEqual(MIN_LEVEL_EXTENT);
    }
    expect(plan.maxLod).toBe(plan.levelCount - 1);
  });

  it("scales level 0 by the resolution policy, not by the viewport", () => {
    const half = planPyramid(1000, 500, { scale: 0.5, maxDimension: 2048 });
    expect(half.width).toBe(500);
    expect(half.height).toBe(250);
  });

  it("caps the longest side and keeps the aspect ratio", () => {
    const plan = planPyramid(4000, 2000, { scale: 1, maxDimension: 1024 });
    expect(plan.width).toBe(1024);
    expect(plan.height).toBe(512);
  });

  it("gives a 4K source behind a phone viewport no more pyramid than the cap allows", () => {
    // The decoupling, concretely: the plan never sees a viewport.
    const plan = planPyramid(3840, 2160, { scale: 1, maxDimension: 1024 });
    expect(Math.max(plan.width, plan.height)).toBeLessThanOrEqual(1024);
  });

  it("survives a one-pixel source without looping", () => {
    const plan = planPyramid(1, 1, full);
    expect(plan.levelCount).toBe(1);
    expect(plan.maxLod).toBe(0);
    expect(plan.analysisLevel).toBe(0);
  });

  it("never exceeds the level cap", () => {
    const plan = planPyramid(8192, 8192, { scale: 1, maxDimension: 8192 });
    expect(plan.levelCount).toBeLessThanOrEqual(MAX_CHAIN_LEVELS);
  });

  it("picks an analysis level near the target extent, not the coarsest", () => {
    // The coarsest level has had every edge blurred out of it, so an edge
    // measurement there reports the same small number for a photograph and for a
    // flat colour.
    const plan = planPyramid(2048, 2048, full);
    const level = plan.levels[plan.analysisLevel];
    expect(level).toBeDefined();
    const shorter = Math.min(level?.width ?? 0, level?.height ?? 0);
    expect(shorter).toBeGreaterThanOrEqual(ANALYSIS_TARGET_EXTENT / 2);
    expect(shorter).toBeLessThanOrEqual(ANALYSIS_TARGET_EXTENT * 2);
    expect(plan.analysisLevel).toBeLessThan(plan.levelCount - 1);
  });

  it("keeps the analysis band fixed as the resolution policy moves", () => {
    const fullPlan = planPyramid(2048, 2048, full);
    const halfPlan = planPyramid(2048, 2048, { scale: 0.5, maxDimension: 2048 });

    const extentOf = (plan: ReturnType<typeof planPyramid>): number => {
      const level = plan.levels[plan.analysisLevel];
      return Math.min(level?.width ?? 0, level?.height ?? 0);
    };

    // Same band, one level shallower into a chain that starts one octave lower.
    expect(extentOf(fullPlan)).toBe(extentOf(halfPlan));
    expect(halfPlan.analysisLevel).toBe(fullPlan.analysisLevel - 1);
  });
});

describe("bodyBlurPlan", () => {
  it("asks for nothing when the material does not frost", () => {
    const plan = planPyramid(512, 512, full);
    expect(bodyBlurPlan(0, plan)).toEqual({ level: 0, residualSigmaTexels: 0 });
  });

  it("lands the body blur on the material's exact sigma, not on a power of two", () => {
    const plan = planPyramid(512, 512, full);
    const sigma = 8;
    const body = bodyBlurPlan(sigma, plan);

    // Chain level `n` covers sigma 1.2 * 2^(n-1) in level-0 texels; the residual
    // is what the separable pass adds on top, measured at that level's own scale.
    const covered = CHAIN_SIGMA_AT_LEVEL_1 * Math.pow(2, body.level - 1);
    const residualLevel0 = body.residualSigmaTexels * Math.pow(2, body.level);
    expect(Math.hypot(covered, residualLevel0)).toBeCloseTo(sigma, 6);
  });

  it("never picks a level whose own blur already overshoots", () => {
    const plan = planPyramid(512, 512, full);
    for (const sigma of [0.5, 1, 2, 4, 8, 16, 32]) {
      const body = bodyBlurPlan(sigma, plan);
      const covered = body.level === 0 ? 0 : CHAIN_SIGMA_AT_LEVEL_1 * Math.pow(2, body.level - 1);
      expect(covered).toBeLessThanOrEqual(sigma + 1e-9);
      expect(body.residualSigmaTexels).toBeGreaterThanOrEqual(0);
    }
  });

  it("stays inside the chain it was given", () => {
    const shallow = planPyramid(32, 32, full);
    const body = bodyBlurPlan(1000, shallow);
    expect(body.level).toBeLessThan(shallow.levelCount);
  });
});
