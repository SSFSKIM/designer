/** W49b DL2: bandwidth is a second sample, capture density is upstream of every sample. */
import { describe, expect, it } from "vitest";
import {
  DEFAULT_MATERIAL_PROFILE, heavySecondFarTapSigmaAtScale, materialDigestInput,
  withMaterialOverrides,
} from "../src/material";

describe("W49b W identity and bandwidth domain", () => {
  it("allocates no far endpoint at identity, including live signed secondary shares", () => {
    for (const share of [-0.25, 0, 0.25, 1]) {
      const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
        sizeHeavySecondShare: share, sizeHeavySecondSigma: 5, sizeHeavySecondSigma2x: 8,
      });
      for (const dpr of [0.75, 1, 1.5, 2, 3]) {
        expect(heavySecondFarTapSigmaAtScale(material, dpr)).toBe(0);
      }
      const digest = materialDigestInput(material);
      expect(digest).not.toHaveProperty("sizeHeavySecondSigmaFar1x");
      expect(digest).not.toHaveProperty("sizeHeavySecondSigmaFar2x");
      expect(digest).not.toHaveProperty("backdropCaptureScale");
    }
  });

  it("resolves physical bandwidth before the pyramid and preserves the share gate", () => {
    const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeHeavySecondShare: -0.25, sizeHeavySecondSigma: 5, sizeHeavySecondSigma2x: 8,
      sizeHeavySecondSigmaFar1x: 4, sizeHeavySecondSigmaFar2x: 2,
    });
    expect(heavySecondFarTapSigmaAtScale(material, 1)).toBe(9);
    expect(heavySecondFarTapSigmaAtScale(material, 1.5)).toBe(9.5);
    expect(heavySecondFarTapSigmaAtScale(material, 2)).toBe(10);
    expect(heavySecondFarTapSigmaAtScale({ ...material, sizeHeavySecondShare: 0 }, 1.5)).toBe(0);
    const digest = materialDigestInput(material);
    expect(digest).toHaveProperty("sizeHeavySecondSigmaFar1x", 4);
    expect(digest).toHaveProperty("sizeHeavySecondSigmaFar2x", 2);
  });

  it("rejects a live nonpositive far width rather than silently substituting an identity", () => {
    expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeHeavySecondShare: 0.25, sizeHeavySecondSigma: 5, sizeHeavySecondSigmaFar1x: -5,
    })).toThrow();
  });
});

describe("W49b S material identity and domain", () => {
  it("drops only the unchanged capture density and retains every live density", () => {
    expect(materialDigestInput(DEFAULT_MATERIAL_PROFILE)).not.toHaveProperty("backdropCaptureScale");
    for (const scale of [0.5, 0.25, 0.125]) {
      const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { backdropCaptureScale: scale });
      expect(materialDigestInput(material)).toHaveProperty("backdropCaptureScale", scale);
    }
  });

  it("refuses impossible densities at the profile boundary", () => {
    for (const scale of [0, -1, 1.1, Infinity, NaN]) {
      expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
        backdropCaptureScale: scale,
      })).toThrow();
    }
  });
});
