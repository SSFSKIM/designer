/**
 * The author tint's shade law (W10), and the properties everything else rests
 * on: an untinted material is untouched, a tinted one is an OPAQUE shade of the
 * seed rather than a wash of it, and the author's strength is a layer opacity.
 *
 * The law was measured per pixel on the reference (claims §5.36): the tinted
 * pixel is the seed times a scalar linear in the untinted pixel's luminance,
 * hue intact, composited at the author's opacity in the encoded space. The
 * constants are fitted on the W9 probe's tinted cells alone and refereed by the
 * canonical bed; what is asserted here is the SHAPE, on the default profile,
 * because the shape is what the shader mirrors line for line.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  tintedMaterialColour,
  tintShade,
  tintShadeLayer,
  tintToneAdaptation,
  withMaterialOverrides,
  type MaterialPolicyView,
  type Rgb,
} from "../src/index";

const seed: Rgb = [0.8, 0.2, 0.05];
const white: Rgb = [1, 1, 1];
const grey: Rgb = [0.3, 0.3, 0.3];

const policy = (patch: Partial<MaterialPolicyView> = {}): MaterialPolicyView => ({
  glass: "material",
  frost: "nominal",
  refraction: "nominal",
  occlusion: "nominal",
  border: "nominal",
  ambientTint: "nominal",
  foreground: "adaptive",
  ...patch,
});

const encode = (c: number): number =>
  c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;

describe("tintShade", () => {
  it("is about half the seed over black content and the seed itself over white", () => {
    // The measured range of tones: 0.5289 at u = 0, reaching 1 before u = 1 and
    // clamped there — a shade brighter than the seed is not a shade.
    expect(tintShade(0, 1)).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.tintShadeDark, 12);
    expect(tintShade(1, 1)).toBe(1);
    expect(DEFAULT_MATERIAL_PROFILE.tintShadeLight).toBeGreaterThanOrEqual(1);
  });

  it("rises with the material's luminance — the range is mapped to content brightness", () => {
    const levels = [0, 0.1, 0.3, 0.6, 0.9, 1].map((u) => tintShade(u, 1));
    for (let i = 1; i < levels.length; i += 1) {
      expect(levels[i] as number).toBeGreaterThanOrEqual(levels[i - 1] as number);
    }
    expect(levels[levels.length - 1] as number).toBeGreaterThan(levels[0] as number);
  });

  it("is linear in the luminance between its ends", () => {
    const mid = tintShade(0.5, 1);
    expect(mid).toBeCloseTo(
      DEFAULT_MATERIAL_PROFILE.tintShadeDark +
        (DEFAULT_MATERIAL_PROFILE.tintShadeLight - DEFAULT_MATERIAL_PROFILE.tintShadeDark) * 0.5,
      12,
    );
  });

  it("collapses to the bare seed at zero grip, and narrows toward it at a partial one", () => {
    expect(tintShade(0, 0)).toBe(1);
    const partial = tintShade(0, 0.35);
    expect(partial).toBeGreaterThan(tintShade(0, 1));
    expect(partial).toBeLessThan(1);
  });

  it("follows a patched profile, so the law is a data change", () => {
    const flat = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      tintShadeDark: 1,
      tintShadeLight: 1,
    });
    expect(tintShade(0, 1, flat)).toBe(1);
    expect(tintShade(0.5, 1, flat)).toBe(1);
  });
});

describe("tintShadeLayer", () => {
  it("keeps the seed's hue — the layer is a scalar multiple in linear light", () => {
    const dark = tintShadeLayer(seed, 0, 1);
    expect(dark[0] / seed[0]).toBeCloseTo(dark[1] / seed[1], 10);
    expect(dark[1] / seed[1]).toBeCloseTo(dark[2] / seed[2], 10);
    expect(dark[0]).toBeLessThan(seed[0]);
  });

  it("never brightens a channel past the seed", () => {
    const bright = tintShadeLayer(seed, 1, 1);
    for (const index of [0, 1, 2] as const) {
      expect(bright[index]).toBeLessThanOrEqual(seed[index]);
    }
  });
});

describe("tintedMaterialColour", () => {
  it("is the identity with no tint — the untinted material is not touched", () => {
    expect(tintedMaterialColour(grey, undefined, 1)).toBe(grey);
  });

  it("is the identity at zero strength", () => {
    expect(tintedMaterialColour(grey, { color: seed, strength: 0 }, 1)).toBe(grey);
  });

  it("is OPAQUE at full strength: the material underneath decides the shade, not the colour", () => {
    // Two very different materials, one seed, one hue: both results are scalar
    // multiples of the seed, and the darker material gets the darker shade.
    const overGrey = tintedMaterialColour(grey, { color: seed, strength: 1 }, 1);
    const overWhite = tintedMaterialColour(white, { color: seed, strength: 1 }, 1);
    for (const result of [overGrey, overWhite]) {
      expect(result[0] / seed[0]).toBeCloseTo(result[1] / seed[1], 6);
      expect(result[1] / seed[1]).toBeCloseTo(result[2] / seed[2], 6);
    }
    expect(overGrey[0]).toBeLessThan(overWhite[0]);
    // Over white the layer IS the seed.
    for (const index of [0, 1, 2] as const) {
      expect(overWhite[index]).toBeCloseTo(seed[index], 6);
    }
  });

  it("composites the author's strength in the ENCODED space, as the reference measures", () => {
    // claims §5.36 finding 3: the half-strength cell is the 0.501 mix in sRGB
    // of the untinted and full-tinted twins, per channel — and NOT the mix in
    // linear light, which fits at a different weight per channel.
    const full = tintedMaterialColour(grey, { color: seed, strength: 1 }, 1);
    const half = tintedMaterialColour(grey, { color: seed, strength: 0.5 }, 1);
    for (const index of [0, 1, 2] as const) {
      expect(encode(half[index])).toBeCloseTo((encode(grey[index]) + encode(full[index])) / 2, 10);
    }
  });
});

describe("tintToneAdaptation", () => {
  it("runs the full range at the nominal regime", () => {
    expect(tintToneAdaptation(policy())).toBe(1);
  });

  it("narrows under increased contrast, on the axis that already governs response", () => {
    expect(tintToneAdaptation(policy({ ambientTint: "reduced" }))).toBe(
      DEFAULT_MATERIAL_PROFILE.reducedTintAdaptation,
    );
  });

  it("stops responding where the policy stops the material responding at all", () => {
    expect(tintToneAdaptation(policy({ ambientTint: "none" }))).toBe(0);
  });
});
