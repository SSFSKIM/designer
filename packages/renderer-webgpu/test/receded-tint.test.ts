import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  tintedMaterialColour,
  tintShadeLayer,
  withMaterialOverrides,
} from "../src/index";

describe("the receded tint's hue and strength are independent", () => {
  it("removes seed saturation rather than preserving unequal hue luminances", () => {
    const patch = { tintChromaScale: 0, tintShadeDark: 0.03, tintShadeLight: 0.73 };
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    // Both seeds have the same peak light, but very different luminance. A
    // luminance-preserving desaturation would retain a hue-dependent grey.
    for (const seed of [[1, 0.3, 0], [0.01, 0.2, 1]] as const) {
      for (const channel of tintShadeLayer(seed, 0.6, 1, profile)) {
        expect(channel).toBeCloseTo(0.45, 12);
      }
    }
    const half = tintedMaterialColour([0.6, 0.6, 0.6], {
      color: [1, 0.3, 0], strength: 0.5,
    }, 1, profile);
    expect(half[0]).toBeGreaterThan(0.45);
    expect(half[0]).toBeLessThan(0.6);
    expect(half[1]).toBe(half[0]);
    expect(half[2]).toBe(half[0]);
  });

  it("canonicalizes explicit identities without changing the resolved active document", () => {
    const patch = { tintChromaScale: 1, tintShadeCollapseRetention: 0, tintShadeStrength: 1 };
    expect(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch))
      .toEqual(DEFAULT_MATERIAL_PROFILE);
    const receded = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      ...patch, tintChromaScale: 0, tintShadeCollapseRetention: 1,
    });
    expect(tintShadeLayer([1, 0.3, 0], 0.6, 1, receded)[1])
      .toBe(tintShadeLayer([1, 0.3, 0], 0.6, 1, receded)[0]);
    expect(withMaterialOverrides(receded, patch)).toEqual(DEFAULT_MATERIAL_PROFILE);
  });
});
