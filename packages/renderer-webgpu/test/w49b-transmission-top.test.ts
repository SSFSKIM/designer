/** W49b D: transmission has its own top, without moving the scatter or the identity path. */
import { describe, expect, it } from "vitest";
import {
  DEFAULT_MATERIAL_PROFILE,
  materialDigestDroppedLeaves,
  materialDigestInput,
  scatterSpanMaxAtScale,
  spanGradedTintAlpha,
  tintAlphaFarAtScale,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "../src/material";
import { createWebGPURenderer } from "../src/renderer";
import { createFakeGpu } from "./harness/fake-gpu";

const ACTIVE: MaterialProfilePatch = {
  tintAlphaFar1x: 0.2, tintAlphaFar2x: 0.2,
  sizeScatterSpanMax: 256, sizeScatterSpanMax2x: 256,
};

function uniform(patch: MaterialProfilePatch, dpr = 1): Float32Array {
  const gpu = createFakeGpu();
  const renderer = createWebGPURenderer({ viewport: {
    widthCss: 240, heightCss: 160, devicePixelRatio: dpr,
  } });
  renderer.attachDevice(gpu.device, "vitrea");
  renderer.setMaterialProfile(patch);
  renderer.setGroup({ groupId: "g", refraction: "true", variant: "regular", analysisExact: true,
    surfaces: [{
    nodeId: "s", family: "fixed-rounded-rect",
    shape: { center: [100, 70], size: [120, 44], radii: [22, 22, 22, 22],
      smoothing: 0, thickness: 8 },
  }] });
  renderer.drawFrame({ frame: { id: 1, timeMs: 1 }, optics: {} as GPUTextureView,
    highlight: {} as GPUTextureView });
  const writes = gpu.uniformWrites.filter(w => w.label.includes("uniform:optics"));
  expect(writes).toHaveLength(1);
  const data = writes[0]!.data;
  renderer.destroy();
  return data;
}

describe("W49b D — independent transmission top", () => {
  it("reaches the transmission above the knee without changing the scatter top", () => {
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      ...ACTIVE, tintAlphaSpanMax: 160, tintAlphaSpanMax2x: 160,
    });
    for (const dpr of [1, 1.5, 2]) {
      expect(scatterSpanMaxAtScale(profile, dpr)).toBe(256);
      expect(spanGradedTintAlpha(0.7, 128, profile, dpr)).toBeCloseTo(0.8, 14);
      expect(spanGradedTintAlpha(0.7, 160, profile, dpr)).toBeCloseTo(0.9, 14);
      for (const span of [0, 32, 44, 56, 96]) {
        expect(spanGradedTintAlpha(0.7, span, profile, dpr)).toBe(0.7);
      }
    }
  });

  it("resolves zero anchors to their own scatter tops BEFORE dpr interpolation", () => {
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      ...ACTIVE, sizeScatterSpanMax2x: 192, tintAlphaSpanMax: 160, tintAlphaSpanMax2x: 0,
    });
    // The resolved 1.5x top is (160 + 192)/2 = 176; at 136 the ramp is exactly halfway.
    expect(spanGradedTintAlpha(0.7, 136, profile, 1.5)).toBeCloseTo(0.8, 14);
    expect(spanGradedTintAlpha(0.7, 144, profile, 2)).toBeCloseTo(0.8, 14);
    expect(spanGradedTintAlpha(0.7, 128, profile, 0.5)).toBeCloseTo(0.8, 14);
    const other = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      ...ACTIVE, sizeScatterSpanMax: 192, tintAlphaSpanMax: 0, tintAlphaSpanMax2x: 160,
    });
    expect(spanGradedTintAlpha(0.7, 136, other, 1.5)).toBeCloseTo(0.8, 14);
    expect(spanGradedTintAlpha(0.7, 144, other, 1)).toBeCloseTo(0.8, 14);
    expect(spanGradedTintAlpha(0.7, 128, other, 3)).toBeCloseTo(0.8, 14);
  });

  it("follows the old expression exactly at zero, including unequal scatter anchors", () => {
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      ...ACTIVE, sizeScatterSpanMax2x: 192, tintAlphaSpanMax: 0, tintAlphaSpanMax2x: 0,
    });
    const clamp = (x: number) => Math.min(1, Math.max(0, x));
    for (const dpr of [0.5, 1, 1.25, 1.5, 2, 3]) {
      for (const span of [0, 44, 96, 96.001, 128, 144, 160, 192, 256, 1024]) {
        const t = clamp((span - profile.sizeSpanMax)
          / Math.max(scatterSpanMaxAtScale(profile, dpr) - profile.sizeSpanMax, 1e-6));
        const old = clamp(0.7 + tintAlphaFarAtScale(profile, dpr) * (t * t * (3 - 2 * t)));
        expect(spanGradedTintAlpha(0.7, span, profile, dpr)).toBe(old);
      }
    }
  });

  it("rejects each nonzero top unless finite and strictly above the resolved thickness knee", () => {
    for (const leaf of ["tintAlphaSpanMax", "tintAlphaSpanMax2x"] as const) {
      for (const top of [-1, 32, 96, Number.NaN, Number.POSITIVE_INFINITY]) {
        expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { [leaf]: top }))
          .toThrow(/tintAlphaSpanMax/);
      }
      expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { [leaf]: 96.001 }))
        .not.toThrow();
      const base = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { [leaf]: 160 });
      expect(() => withMaterialOverrides(base, { sizeSpanMax: 160 })).toThrow(/tintAlphaSpanMax/);
      expect(() => withMaterialOverrides(base, { [leaf]: 0, sizeSpanMax: 160 }))
        .not.toThrow();
    }
  });

  it("drops both identity tops separately, carrying either nonzero anchor in the digest", () => {
    const before = materialDigestInput(DEFAULT_MATERIAL_PROFILE);
    for (const leaf of ["tintAlphaSpanMax", "tintAlphaSpanMax2x"] as const) {
      expect(materialDigestDroppedLeaves(DEFAULT_MATERIAL_PROFILE)).toContain(leaf);
      const changed = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { [leaf]: 160 });
      expect(materialDigestDroppedLeaves(changed)).not.toContain(leaf);
      expect(materialDigestInput(changed)).not.toEqual(before);
      const other = leaf === "tintAlphaSpanMax" ? "tintAlphaSpanMax2x" : "tintAlphaSpanMax";
      expect(materialDigestDroppedLeaves(changed)).toContain(other);
    }
    expect(materialDigestInput(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      tintAlphaSpanMax: 0, tintAlphaSpanMax2x: 0,
    }))).toEqual(before);
  });

  it("appends a transmission-only uniform and leaves every old lane unchanged", () => {
    const off = uniform(ACTIVE);
    const on = uniform({ ...ACTIVE, tintAlphaSpanMax: 160, tintAlphaSpanMax2x: 160 });
    expect([...on.slice(0, 152)]).toEqual([...off.slice(0, 152)]);
    expect([...off.slice(152, 156)]).toEqual([0, 0, 0, 0]);
    expect([...on.slice(152, 156)]).toEqual([160, 0, 0, 0]);
    const mixed = uniform({ ...ACTIVE, sizeScatterSpanMax2x: 192,
      tintAlphaSpanMax: 160, tintAlphaSpanMax2x: 0 }, 1.5);
    expect(mixed[152]).toBe(176);
    // A zero anchor at a pure scale must also take the old shader expression.
    expect(uniform({ ...ACTIVE, tintAlphaSpanMax2x: 160 }, 1)[152]).toBe(0);
    expect(uniform({ ...ACTIVE, tintAlphaSpanMax: 160 }, 2)[152]).toBe(0);
  });
});
