/**
 * Parametric morph over the full X8 channel vector.
 *
 * The three properties that matter: the endpoints come back exactly, nothing
 * jumps in between, and every intermediate shape is inside the smoothing budget —
 * which is what keeps the whole morph inside the declared error bound rather than
 * only its ends.
 */

import { describe, expect, it } from "vitest";

import { APPLE_BEST_FIGMA_SMOOTHING } from "../src/apple";
import { flattenShapeChannels, SHAPE_CHANNEL_COUNT } from "../src/channels";
import { smoothingCeiling } from "../src/corner";
import { GeometryError } from "../src/errors";
import { rsupnField } from "../src/field";
import { morphShapes, sampleMorph } from "../src/morph";
import { fieldParams, resolveShape } from "../src/shape";

const button = resolveShape({
  family: "fixed-rounded-rect",
  center: [40, 20],
  size: [80, 40],
  radii: 20,
  profile: 0.6,
  thickness: 4,
});

const platter = resolveShape({
  family: "fixed-rounded-rect",
  center: [120, 90],
  size: [240, 180],
  radii: 28,
  profile: 0.6,
  thickness: 10,
});

const capsule = resolveShape({
  family: "capsule",
  center: [40, 20],
  size: [160, 40],
  thickness: 4,
});

const rect = resolveShape({
  family: "fixed-rounded-rect",
  center: [40, 20],
  size: [160, 40],
  radii: 8,
  profile: 0,
  thickness: 4,
});

describe("every channel interpolates", () => {
  it("reproduces both endpoints exactly", () => {
    expect(morphShapes(button, platter, 0).channels).toEqual(button.channels);
    expect(morphShapes(button, platter, 1).channels).toEqual(platter.channels);
    // and the derived corner comes back identical, not merely close
    expect(morphShapes(button, platter, 0).corner).toEqual(button.corner);
    expect(morphShapes(button, platter, 1).corner).toEqual(platter.corner);
  });

  it("moves the whole channel vector, with nothing left behind", () => {
    const mid = morphShapes(button, platter, 0.5);
    expect(mid.channels.center).toEqual([80, 55]);
    expect(mid.channels.size).toEqual([160, 110]);
    expect(mid.channels.radii).toEqual([24, 24, 24, 24]);
    expect(mid.channels.thickness).toBe(7);
    expect(flattenShapeChannels(mid.channels).length).toBe(SHAPE_CHANNEL_COUNT);
  });

  it("interpolates a capsule into a rounded rect as one continuous shape", () => {
    // The headline X8 claim. A capsule's radius is its budget, which is what makes
    // the t=0 end an exact stadium without a special case anywhere.
    const path = sampleMorph(capsule, rect, 40);
    expect(path[0]!.corner.smoothingEff).toBe(0);
    expect(path[0]!.corner.radius).toBe(20);
    expect(path[40]!.corner.radius).toBe(8);
    for (const s of path) {
      expect(Number.isFinite(s.corner.reach)).toBe(true);
      expect(s.corner.k.every(Number.isFinite)).toBe(true);
    }
  });

  it("does not clamp t, so a spring's overshoot produces the shape it asks for", () => {
    const over = morphShapes(button, platter, 1.2);
    expect(over.channels.size[0]).toBeGreaterThan(platter.channels.size[0]);
    // and a radius driven negative still resolves to a legal shape
    const under = morphShapes(platter, button, 3);
    expect(under.corner.radius).toBeGreaterThanOrEqual(0);
    expect(Number.isFinite(under.corner.reach)).toBe(true);
  });
});

describe("continuity", () => {
  it("has no channel jump anywhere along the path", () => {
    const steps = 400;
    const path = sampleMorph(button, platter, steps);
    const deltas = new Array<number>(SHAPE_CHANNEL_COUNT).fill(0);
    for (let i = 1; i < path.length; i++) {
      const a = flattenShapeChannels(path[i - 1]!.channels);
      const b = flattenShapeChannels(path[i]!.channels);
      for (let c = 0; c < SHAPE_CHANNEL_COUNT; c++) {
        deltas[c] = Math.max(deltas[c] as number, Math.abs((b[c] as number) - (a[c] as number)));
      }
    }
    // Linear interpolation over `steps` gives each channel exactly
    // |b - a| / steps per step; anything larger is a discontinuity.
    const spanA = flattenShapeChannels(button.channels);
    const spanB = flattenShapeChannels(platter.channels);
    for (let c = 0; c < SHAPE_CHANNEL_COUNT; c++) {
      const expected = Math.abs((spanB[c] as number) - (spanA[c] as number)) / steps;
      expect(deltas[c], `channel ${c}`).toBeLessThanOrEqual(expected + 1e-12);
    }
  });

  it("keeps the DERIVED corner continuous, including through the budget clamp", () => {
    // The channels being continuous is not enough: the corner is derived, and the
    // clamp is where a discontinuity could hide. This morph shrinks a shape past
    // the point where its radius stops fitting, which is exactly that case.
    const big = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [400, 400],
      radii: 40,
      profile: 1,
    });
    const small = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [70, 70],
      radii: 40,
      profile: 1,
    });

    const steps = 2000;
    const path = sampleMorph(big, small, steps);
    let maxSJump = 0;
    let maxReachJump = 0;
    let maxKJump = 0;
    let clampEngaged = false;
    for (let i = 1; i < path.length; i++) {
      const a = path[i - 1]!.corner;
      const b = path[i]!.corner;
      maxSJump = Math.max(maxSJump, Math.abs(b.smoothingEff - a.smoothingEff));
      maxReachJump = Math.max(maxReachJump, Math.abs(b.reach - a.reach));
      for (let j = 0; j < 5; j++) {
        maxKJump = Math.max(maxKJump, Math.abs((b.k[j] as number) - (a.k[j] as number)));
      }
      if (b.smoothingEff < 0.999) clampEngaged = true;
    }

    // the clamp really did bite somewhere along this path
    expect(clampEngaged).toBe(true);
    expect(path[steps]!.corner.smoothingEff).toBeLessThan(1);
    // and nothing snapped
    expect(maxSJump).toBeLessThan(0.01);
    expect(maxReachJump).toBeLessThan(0.5);
    expect(maxKJump).toBeLessThan(0.2);
  });

  it("keeps every interpolated shape inside the smoothing budget", () => {
    // The safety claim. If an intermediate shape could exceed the budget, the
    // declared error bound would only cover the endpoints — the clamp is applied
    // at derivation precisely so it covers the whole path.
    for (const [a, b] of [
      [button, platter],
      [capsule, rect],
      [platter, capsule],
    ] as const) {
      for (const s of sampleMorph(a, b, 200)) {
        const ceiling = smoothingCeiling(s.corner.radius, s.corner.budget);
        expect(s.corner.smoothingEff).toBeLessThanOrEqual(Math.min(1, ceiling) + 1e-12);
        expect(s.corner.reach).toBeLessThanOrEqual(s.corner.budget + 1e-9);
      }
    }
  });

  it("keeps the field finite and correctly signed all along the path", () => {
    for (const s of sampleMorph(capsule, platter, 100)) {
      const p = fieldParams(s);
      expect(rsupnField(p, 0, 0)).toBeLessThanOrEqual(0);
      expect(rsupnField(p, p.halfW + 50, 0)).toBeGreaterThan(0);
      expect(Number.isFinite(rsupnField(p, p.halfW, p.halfH))).toBe(true);
    }
  });
});

describe("what a morph refuses", () => {
  it("will not blend two different corner references", () => {
    // They are separate fits, not two points on one axis, so an interpolated
    // coefficient set would describe a corner whose error nobody has measured.
    const appleProfiled = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 20,
      profile: "continuous",
    });
    const figmaProfiled = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 20,
      profile: 0.6,
    });

    expect(() => morphShapes(appleProfiled, figmaProfiled, 0.5)).toThrow(GeometryError);
    try {
      morphShapes(appleProfiled, figmaProfiled, 0.5);
    } catch (e) {
      expect((e as GeometryError).code).toBe("corner-reference-mismatch");
    }
  });

  it("offers the documented way onto the interpolable axis instead", () => {
    // S2 measured 0.66 as the Figma smoothing that best matches Apple. Once the
    // Apple-like endpoint is expressed there, the morph is ordinary.
    const onAxis = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 20,
      profile: APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing,
    });
    expect(onAxis.corner.reference).toBe("figma-smoothing");
    expect(() => morphShapes(onAxis, capsule, 0.5)).not.toThrow();
  });

  it("morphs two Apple-profiled shapes without complaint", () => {
    const a = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [200, 100],
      radii: 20,
      profile: "continuous",
    });
    const b = resolveShape({
      family: "fixed-rounded-rect",
      center: [50, 50],
      size: [400, 300],
      radii: 40,
      profile: "continuous",
    });
    const path = sampleMorph(a, b, 50);
    for (const s of path) {
      expect(s.corner.reference).toBe("apple-continuous");
      // Apple's corner has no smoothing parameter, so it stays pinned throughout —
      // which is itself continuity, just of the least interesting kind.
      expect(s.corner.smoothingEff).toBeCloseTo(a.corner.smoothingEff, 12);
    }
  });
});
