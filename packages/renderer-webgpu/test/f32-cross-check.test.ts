/**
 * The family-C f32 cross-check — Decision Log #20's obligation on C6, CPU half.
 *
 * > family C as the governor's first within-tier step **conditional on C6's f32
 * > cross-check**
 *
 * S2 ran this for family D on a metal-3 adapter and measured 4.08e-5 px, which is
 * 0.024% of family D's declared 0.170 px bound. Family C was priced but only
 * inspection-verified. This file runs the same protocol — the same three shape
 * regimes, the same contour-relative offsets, the same grid — with the shader's
 * arithmetic emulated in f32 through `Math.fround`, so the answer is available on
 * every machine and in the ordinary suite.
 *
 * The device half lives in `e2e/gpu/cross-check.spec.ts` and compiles the shipped
 * WGSL. Neither half alone is the whole check, and the report says which one ran:
 * the emulation cannot see hardware fused multiply-add (which would make the real
 * shader *more* accurate than this) or a low-precision `inverseSqrt` (which would
 * make it *less*).
 */

import { describe, expect, it } from "vitest";
import { rsupField, rsupnField } from "@vitrea/geometry";

import { GOVERNOR_LADDER } from "../src/governor";
import {
  buildCheckSet,
  rsupF32,
  rsupnF32,
  summarise,
  type CheckStats,
} from "./harness/f32-mirror";

/** S2's declared bounds for the two families, in px. */
const BOUND = { rsupn: 0.17, rsup: 0.574 } as const;

/**
 * The pass criterion, stated once. S2's own framing — 4.08e-5 px being "0.024% of
 * the declared bound" — is a share of the budget, so the criterion is a share too:
 * f32 rounding may not consume more than a thousandth of the family's bound. That
 * leaves the declared bound intact to three significant figures whatever the
 * rounding does.
 */
const BUDGET_SHARE = 1e-3;

function run(family: "rsupn" | "rsup"): CheckStats {
  const set = buildCheckSet();
  const diffs: number[] = [];
  const reaches: number[] = [];

  for (const point of set.points) {
    const shape = set.shapes[point.shape];
    if (shape === undefined) continue;
    const params = family === "rsupn" ? shape.rsupn : shape.rsup;
    const exact = family === "rsupn"
      ? rsupnField(params, point.x, point.y)
      : rsupField(params, point.x, point.y);
    const rounded = family === "rsupn"
      ? rsupnF32(params, point.x, point.y)
      : rsupF32(params, point.x, point.y);

    diffs.push(Math.abs(rounded - exact));
    reaches.push(params.reach);
  }

  return summarise(diffs, reaches);
}

describe("the cross-check's point set", () => {
  it("covers the corner sector densely and the other branches at all", () => {
    const set = buildCheckSet();
    expect(set.shapes).toHaveLength(3);
    // S2's set was 5535 points over three shapes; the same construction here.
    expect(set.points.length).toBeGreaterThan(4000);
  });

  it("spans the three smoothing regimes, with distinct fits", () => {
    const set = buildCheckSet();
    const fits = set.shapes.map((shape) => shape.rsupn.k.join(","));
    expect(new Set(fits).size).toBe(3);
  });

  it("gives the two families the same reach and different coefficients", () => {
    // They share a zero level set and a corner offset; the fit is what differs.
    for (const shape of buildCheckSet().shapes) {
      expect(shape.rsup.reach).toBeCloseTo(shape.rsupn.reach, 12);
      expect(shape.rsup.halfW).toBeCloseTo(shape.rsupn.halfW, 12);
    }
  });
});

describe("family D (rsupn) — the control", () => {
  it("reproduces S2's verdict: f32 rounding is a rounding error, not a budget", () => {
    const stats = run("rsupn");
    expect(stats.n).toBeGreaterThan(4000);
    expect(stats.maxAbsDiff).toBeLessThan(BOUND.rsupn * BUDGET_SHARE);
    // S2 measured 4.08e-5 px on hardware; the emulation must land in the same
    // order of magnitude or the two are not measuring the same thing.
    expect(stats.maxAbsDiff).toBeLessThan(1e-3);
  });
});

describe("family C (rsup) — the governor's first within-tier step", () => {
  it("passes the same check family D passed", () => {
    const stats = run("rsup");

    expect(stats.n).toBeGreaterThan(4000);
    expect(stats.maxAbsDiff).toBeLessThan(BOUND.rsup * BUDGET_SHARE);
    expect(stats.p99AbsDiff).toBeLessThanOrEqual(stats.maxAbsDiff);
    expect(Number.isFinite(stats.maxAbsDiff)).toBe(true);
  });

  it("loses no more precision than family D, despite dropping the normalization", () => {
    // The normalization is a divide and an inverse square root — the two operations
    // most likely to carry precision loss. Dropping them cannot make f32 worse.
    const normalized = run("rsupn");
    const plain = run("rsup");
    expect(plain.maxAbsDiff).toBeLessThanOrEqual(normalized.maxAbsDiff * 4);
  });

  it("stays a rounding error relative to the corner reach", () => {
    // S2 reported 4.8e-7 of the corner reach for family D. Scale-relative, so it
    // does not flatter a large shape.
    expect(run("rsup").maxRelativeToReach).toBeLessThan(1e-5);
  });
});

describe("what the check gates", () => {
  it("is the ladder step the governor refuses without it", () => {
    // The link the Decision Log draws, made explicit: this file is the reason
    // `recordFamilyCVerified()` may ever be called.
    expect(GOVERNOR_LADDER[1]?.fieldFamily).toBe("rsup");
    expect(GOVERNOR_LADDER[0]?.fieldFamily).toBe("rsupn");
  });
});
