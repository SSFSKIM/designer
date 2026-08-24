/**
 * Group union: bounded smooth-min.
 *
 * The spec's requirement is that union aesthetics are **capped** so nothing reads
 * as jelly. "Jelly" has two distinct causes and both are tested here:
 *
 *  - a neck that is too fat — bounded by `maxBulge`;
 *  - material appearing between members that are nowhere near each other —
 *    bounded by `separationThreshold`.
 *
 * A smooth min of two EQUAL values dips even when both are large, so without the
 * separation gate two members 100 px apart still depress the field on the segment
 * between them. That is the second failure mode, and it is the one a naive
 * smooth-min ships with.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_GROUP_UNION,
  type GroupUnionParams,
  groupUnion,
  groupUnionField,
  memberField,
  smoothUnion2,
} from "../src/union";
import { resolveShape } from "../src/shape";

const P: GroupUnionParams = DEFAULT_GROUP_UNION;

const chip = (cx: number, cy: number, w = 60, h = 40) =>
  resolveShape({
    family: "fixed-rounded-rect",
    center: [cx, cy],
    size: [w, h],
    radii: 12,
    profile: 0.6,
  });

describe("the two-member union", () => {
  it("is commutative, so a group never depends on instance order", () => {
    for (const [a, b] of [
      [0, 0],
      [1, 3],
      [-2, 5],
      [0.5, 0.6],
      [-4, -9],
      [20, 21],
    ] as const) {
      expect(smoothUnion2(a, b, P)).toBeCloseTo(smoothUnion2(b, a, P), 15);
    }
  });

  it("never exceeds min, and never dips more than maxBulge below it", () => {
    for (let a = -20; a <= 20; a += 0.37) {
      for (let b = -20; b <= 20; b += 0.53) {
        const u = smoothUnion2(a, b, P);
        const m = Math.min(a, b);
        expect(u).toBeLessThanOrEqual(m + 1e-12);
        expect(u).toBeGreaterThanOrEqual(m - P.maxBulge - 1e-12);
      }
    }
  });

  it("equals min exactly when one member is far nearer than the other", () => {
    // |a - b| >= k saturates the blend. This is the gate that keeps the field
    // exact right next to one member when another is far away.
    const k = Math.min(P.neckWidth, 4 * P.maxBulge);
    expect(smoothUnion2(0, k + 1, P)).toBe(0);
    expect(smoothUnion2(-3, -3 + k + 1, P)).toBe(-3);
  });

  it("dips by exactly k/4 at a real seam, which is what caps k", () => {
    // Two coincident surfaces: h = 1/2 and the deviation is k/4. Capping the
    // deviation at maxBulge is therefore the same statement as capping k at 4x it.
    const k = Math.min(P.neckWidth, 4 * P.maxBulge);
    expect(smoothUnion2(0, 0, P)).toBeCloseTo(-k / 4, 12);
    expect(-k / 4).toBeGreaterThanOrEqual(-P.maxBulge);
  });

  it("honours the bulge cap when neckWidth is raised past it", () => {
    // The cap is a guard against a raised neck width, not a re-parameterization of
    // the default — so at the default it must not already be binding.
    const wide: GroupUnionParams = { ...P, neckWidth: 400 };
    expect(smoothUnion2(0, 0, wide)).toBeCloseTo(-wide.maxBulge, 12);
    expect(smoothUnion2(0, 0, P)).toBeCloseTo(-P.neckWidth / 4, 12);
  });
});

describe("the separation gate — where the jelly would come from", () => {
  it("leaves the field exactly min between two distant members", () => {
    // Without the gate, `min(a,b)` equal at the midpoint means the smooth min dips
    // there regardless of how far apart the members are: material out of nowhere.
    const a = chip(0, 0);
    const b = chip(400, 0);
    for (const x of [150, 200, 250]) {
      const fa = memberField(a, [x, 0]);
      const fb = memberField(b, [x, 0]);
      expect(groupUnionField([a, b], [x, 0])).toBe(Math.min(fa, fb));
    }
  });

  it("still blends where two members nearly touch", () => {
    // The gate must not switch off the thing the union is for.
    const a = chip(0, 0);
    const b = chip(64, 0); // a 4 px gap between 60-wide chips
    const mid = groupUnionField([a, b], [32, 0]);
    const plainMin = Math.min(memberField(a, [32, 0]), memberField(b, [32, 0]));
    expect(mid).toBeLessThan(plainMin);
    expect(plainMin - mid).toBeLessThanOrEqual(P.maxBulge + 1e-12);
  });

  it("forms a neck only once the gap is small enough to warrant one", () => {
    // A neck means the union actually reaches zero between the members. That
    // should happen for a touching pair and not for a well-separated one.
    const touching = groupUnionField([chip(0, 0), chip(62, 0)], [31, 0]);
    const separated = groupUnionField([chip(0, 0), chip(120, 0)], [60, 0]);
    expect(touching).toBeLessThan(0);
    expect(separated).toBeGreaterThan(0);
  });
});

describe("the n-member union", () => {
  it("holds the bulge cap for any member count", () => {
    // A left fold would drift by up to (n-1)*maxBulge without the final clamp, and
    // "nothing reads as jelly" would stop being true at high member counts.
    const many = [0, 0, 0, 0, 0, 0, 0, 0];
    expect(groupUnion(many, P)).toBeGreaterThanOrEqual(-P.maxBulge - 1e-12);
    expect(groupUnion(many, P)).toBeLessThanOrEqual(0);

    const mixed = [3, 3.2, 2.9, 3.1, 3.05, 2.95];
    const m = Math.min(...mixed);
    expect(groupUnion(mixed, P)).toBeGreaterThanOrEqual(m - P.maxBulge - 1e-12);
    expect(groupUnion(mixed, P)).toBeLessThanOrEqual(m + 1e-12);
  });

  it("is permutation-bounded, and exactly permutation-invariant far from seams", () => {
    const values = [0.4, 3.1, -2.2, 9.7, 0.35];
    const permutations = [
      [0.4, 3.1, -2.2, 9.7, 0.35],
      [9.7, 0.35, 0.4, -2.2, 3.1],
      [-2.2, 0.35, 9.7, 3.1, 0.4],
      [0.35, 0.4, 3.1, 9.7, -2.2],
    ];
    const results = permutations.map((v) => groupUnion(v, P));
    const spread = Math.max(...results) - Math.min(...results);
    expect(spread).toBeLessThanOrEqual(P.maxBulge + 1e-12);

    // far from any seam — all members widely separated — every order gives min
    const far = [40, 80, 120, 200];
    for (const perm of [far, [...far].reverse(), [120, 40, 200, 80]]) {
      expect(groupUnion(perm, P)).toBe(40);
    }
    void values;
  });

  it("returns the single member's field for a one-member group", () => {
    expect(groupUnion([2.5], P)).toBe(2.5);
    const only = chip(0, 0);
    expect(groupUnionField([only], [10, 5])).toBe(memberField(only, [10, 5]));
  });

  it("evaluates each member in its own frame, so the group can sit anywhere", () => {
    const here = groupUnionField([chip(0, 0), chip(70, 0)], [35, 0]);
    const there = groupUnionField([chip(500, 300), chip(570, 300)], [535, 300]);
    expect(there).toBeCloseTo(here, 12);
  });
});

describe("the union is a field, not a coverage mask", () => {
  it("agrees with min far outside the group, where nothing is blending", () => {
    const members = [chip(0, 0), chip(90, 0), chip(45, 70)];
    for (const pt of [
      [-300, 0],
      [400, 0],
      [0, -300],
      [45, 400],
    ] as const) {
      const values = members.map((m) => memberField(m, pt));
      expect(groupUnionField(members, pt)).toBe(Math.min(...values));
    }
  });

  it("is negative inside any member and positive well outside all of them", () => {
    const members = [chip(0, 0), chip(90, 0)];
    expect(groupUnionField(members, [0, 0])).toBeLessThan(0);
    expect(groupUnionField(members, [90, 0])).toBeLessThan(0);
    expect(groupUnionField(members, [45, 300])).toBeGreaterThan(0);
  });
});
