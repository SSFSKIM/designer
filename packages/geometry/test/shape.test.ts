/**
 * ShapeSpec -> ResolvedShape: the three v1 families, the X8 channel vector, and
 * the v1 uniform-radii refusal.
 */

import { describe, expect, it } from "vitest";

import { APPLE_CONTINUOUS_SMOOTHING_SEED, APPLE_REACH } from "../src/apple";
import { APPLE_RSUPN, FIGMA_RSUPN_TABLE, ZERO_COEFFICIENTS } from "../src/coefficients";
import { flattenShapeChannels, SHAPE_CHANNEL_COUNT, SHAPE_FAMILIES } from "../src/channels";
import { GeometryError } from "../src/errors";
import { rsupnField } from "../src/field";
import {
  assertUniformRadii,
  fieldParams,
  governorFieldParams,
  resolveShape,
} from "../src/shape";
import { resolveConcentric } from "../src/concentric";

describe("the three v1 shape families", () => {
  it("names exactly the families §Geometry lists", () => {
    expect(SHAPE_FAMILIES).toEqual([
      "fixed-rounded-rect",
      "capsule",
      "concentric-rounded-rect",
    ]);
  });

  it("resolves all three, each to the same channel vector shape", () => {
    const rect = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 24,
      profile: 0.6,
      thickness: 6,
    });
    const capsule = resolveShape({
      family: "capsule",
      center: [0, 0],
      size: [200, 100],
      thickness: 6,
    });
    const concentric = resolveConcentric(rect, { inset: 4 }).shape;

    for (const s of [rect, capsule, concentric]) {
      expect(flattenShapeChannels(s.channels).length).toBe(SHAPE_CHANNEL_COUNT);
      expect(flattenShapeChannels(s.channels).every(Number.isFinite)).toBe(true);
    }
    expect(rect.family).toBe("fixed-rounded-rect");
    expect(capsule.family).toBe("capsule");
    expect(concentric.family).toBe("concentric-rounded-rect");
  });
});

describe("the capsule family", () => {
  it("takes the whole budget as its radius, which forces a true stadium", () => {
    const capsule = resolveShape({ family: "capsule", center: [0, 0], size: [200, 100] });
    expect(capsule.channels.radii).toEqual([50, 50, 50, 50]);
    expect(capsule.corner.smoothingEff).toBe(0);
    expect(capsule.corner.reach).toBe(50);
    // zero coefficients means the corner correction is not applied at all — the
    // field reduces to the exact analytic stadium distance
    expect(capsule.corner.k).toEqual(ZERO_COEFFICIENTS);
  });

  it("is a stadium whichever way round it is", () => {
    const tall = resolveShape({ family: "capsule", center: [0, 0], size: [100, 200] });
    expect(tall.channels.radii).toEqual([50, 50, 50, 50]);
    expect(tall.corner.smoothingEff).toBe(0);
  });
});

describe("the corner profile sugar", () => {
  it('maps "continuous" onto the Apple-direct reference, per Decision Log #20', () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 20,
      profile: "continuous",
    });
    expect(s.corner.reference).toBe("apple-continuous");
    expect(s.channels.smoothing).toBeCloseTo(APPLE_CONTINUOUS_SMOOTHING_SEED, 12);
    expect(s.corner.k).toEqual(APPLE_RSUPN.k);
    expect(s.corner.reach).toBeCloseTo(APPLE_REACH * 20, 9);
  });

  it('maps "circular" onto smoothing 0, the member both references share', () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 20,
      profile: "circular",
    });
    expect(s.channels.smoothing).toBe(0);
    expect(s.corner.smoothingEff).toBe(0);
    expect(s.corner.k).toEqual(ZERO_COEFFICIENTS);
    expect(s.corner.reach).toBe(20);
  });

  it("puts a numeric profile on the interpolable Figma axis", () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [400, 400],
      radii: 40,
      profile: 0.6,
    });
    expect(s.corner.reference).toBe("figma-smoothing");
    expect(s.corner.smoothingEff).toBeCloseTo(0.6, 12);
    expect(s.corner.k).toEqual(FIGMA_RSUPN_TABLE.find((r) => r.sEff === 0.6)?.k);
  });

  it("defaults to the continuous profile", () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 20,
    });
    expect(s.corner.reference).toBe("apple-continuous");
  });
});

describe("channels preserve what the author wrote", () => {
  it("keeps the authored smoothing even when the budget clamps the derivation", () => {
    // X8 rider 1: the authored value rides on the channel, the clamp lands in the
    // derivation. This is what makes shrinking and re-growing a shape lossless —
    // clamping the channel itself would quietly destroy the authored intent.
    const small = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [60, 30],
      radii: 13,
      profile: 1,
    });
    expect(small.channels.smoothing).toBe(1);
    expect(small.corner.smoothingEff).toBeCloseTo(15 / 13 - 1, 12);

    // grow it back and the corner returns to the authored value exactly
    const grown = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [600, 300],
      radii: 13,
      profile: small.channels.smoothing,
    });
    expect(grown.corner.smoothingEff).toBe(1);
  });

  it("preserves the Vec4 radii shape even though v1 requires them uniform", () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: [16, 16, 16, 16],
      profile: 0.5,
    });
    expect(s.channels.radii).toEqual([16, 16, 16, 16]);
    expect(s.channels.radii.length).toBe(4);
  });
});

describe("the v1 uniform-radii restriction (X8 rider 3)", () => {
  it("refuses per-corner radii in dev mode, naming why", () => {
    // The corner algebra reads |x| and |y|, so it is mirror-symmetric by
    // construction and literally cannot express four different corners. S2 asked
    // for this to be an explicit scope decision, so it is a refusal rather than a
    // silent average of the four.
    const spec = {
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: [16, 8, 16, 8],
      profile: 0.5,
    } as const;
    expect(() => resolveShape(spec)).toThrow(GeometryError);
    try {
      resolveShape(spec);
    } catch (e) {
      expect((e as GeometryError).code).toBe("non-uniform-radii");
      expect((e as GeometryError).message).toContain("mirror-symmetric");
    }
  });

  it("accepts radii that differ only by floating-point noise", () => {
    expect(() => assertUniformRadii([16, 16 + 1e-12, 16, 16 - 1e-12])).not.toThrow();
    expect(assertUniformRadii([16, 16, 16, 16])).toBe(16);
  });

  it("lets a caller opt out of the check, but not out of the consequence", () => {
    // devMode false takes the first radius, which is the honest degradation: the
    // evaluator has one radius to work with either way.
    const s = resolveShape(
      {
        family: "fixed-rounded-rect",
        center: [0, 0],
        size: [200, 100],
        radii: [16, 8, 16, 8],
        profile: 0.5,
      },
      { devMode: false },
    );
    expect(s.corner.radius).toBe(16);
  });
});

describe("derived field parameters", () => {
  it("are the six floats C6's instance buffer widens by", () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [10, 20],
      size: [200, 100],
      radii: 24,
      profile: 0.6,
    });
    const p = fieldParams(s);
    expect(p.halfW).toBe(100);
    expect(p.halfH).toBe(50);
    expect(typeof p.reach).toBe("number");
    expect(p.k.length).toBe(5);
    // shape-local: the centre is NOT baked in, since the shader subtracts it
    expect(rsupnField(p, 100, 0)).toBeCloseTo(0, 9);
  });

  it("offers family C's parameters for the governor's first step", () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [400, 400],
      radii: 40,
      profile: 0.6,
    });
    const d = fieldParams(s);
    const c = governorFieldParams(s);
    // same corner offset and same zero level set, different fitted correction
    expect(c.reach).toBe(d.reach);
    expect(c.k).not.toEqual(d.k);
  });

  it("zeroes the correction for a degenerate corner", () => {
    const s = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 0,
      profile: "continuous",
    });
    expect(s.corner.k).toEqual(ZERO_COEFFICIENTS);
    expect(s.corner.reach).toBe(0);
    // a plain rectangle: the field is the exact box distance
    const p = fieldParams(s);
    expect(rsupnField(p, 120, 0)).toBeCloseTo(20, 9);
    expect(rsupnField(p, 100, 50)).toBeCloseTo(0, 9);
  });
});
