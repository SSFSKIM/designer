/**
 * The author tint's tone map, and the two properties everything else rests on:
 * an untinted material is untouched, and a tinted one is a *range* rather than
 * a fill.
 *
 * The curve's constants are advisory and calibration-delegated, so nothing here
 * asserts a number the tinted-capture extension will fit. What it asserts is
 * shape — monotonicity in the backdrop, hue preserved at the dark end, the seed
 * reachable, the excursion bounded, and the accessibility fold collapsing the
 * response without touching the colour.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  tintedTintColour,
  tintTone,
  tintToneAdaptation,
  withMaterialOverrides,
  type MaterialPolicyView,
  type Rgb,
} from "../src/index";

const seed: Rgb = [0.8, 0.2, 0.05];
const white: Rgb = [1, 1, 1];

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

const luminance = (rgb: Rgb): number => 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];

describe("tintTone", () => {
  it("rises with the backdrop — the range is mapped to content brightness", () => {
    const levels = [0, 0.1, 0.3, 0.6, 0.9, 1].map((backdrop) =>
      luminance(tintTone(seed, backdrop, 1)),
    );
    for (let i = 1; i < levels.length; i += 1) {
      expect(levels[i] as number).toBeGreaterThanOrEqual(levels[i - 1] as number);
    }
    expect(levels[levels.length - 1] as number).toBeGreaterThan(levels[0] as number);
  });

  it("keeps the seed's hue at the dark end, where the tone is a shade of it", () => {
    const dark = tintTone(seed, 0, 1);
    // A scalar multiple in linear light: chromaticity, and therefore hue, is the
    // same colour seen with less light.
    expect(dark[0] / seed[0]).toBeCloseTo(dark[1] / seed[1], 10);
    expect(dark[1] / seed[1]).toBeCloseTo(dark[2] / seed[2], 10);
    expect(dark[0]).toBeLessThan(seed[0]);
  });

  it("washes toward white at the bright end rather than clipping the seed", () => {
    const bright = tintTone(seed, 1, 1);
    for (const index of [0, 1, 2] as const) {
      expect(bright[index]).toBeGreaterThanOrEqual(seed[index]);
      expect(bright[index]).toBeLessThanOrEqual(1);
    }
    // Saturation falls: the dimmest channel gains proportionally the most.
    expect(bright[2] / seed[2]).toBeGreaterThan(bright[0] / seed[0]);
  });

  it("stays near the intended colour — the whole range is a tone of the seed", () => {
    for (const backdrop of [0, 0.25, 0.5, 0.75, 1]) {
      const tone = tintTone(seed, backdrop, 1);
      // Ordering of the channels is what makes a colour recognisable as itself.
      expect(tone[0]).toBeGreaterThan(tone[1]);
      expect(tone[1]).toBeGreaterThan(tone[2]);
    }
  });

  it("collapses to the bare seed when the contrast regime allows no excursion", () => {
    for (const backdrop of [0, 0.5, 1]) {
      expect(tintTone(seed, backdrop, 0)).toEqual(seed);
    }
  });

  it("narrows, without moving the colour, at a partial adaptation", () => {
    const full = tintTone(seed, 0, 1);
    const partial = tintTone(seed, 0, 0.35);
    expect(partial[0]).toBeGreaterThan(full[0]);
    expect(partial[0]).toBeLessThan(seed[0]);
  });

  it("follows a patched profile, so the curve is a data change", () => {
    const flat = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      tintToneFloor: 1,
      tintToneCeilMix: 0,
    });
    expect(tintTone(seed, 0, 1, flat)).toEqual(seed);
    expect(tintTone(seed, 1, 1, flat)).toEqual(seed);
  });
});

describe("tintedTintColour", () => {
  it("is the identity with no tint — the untinted material is not touched", () => {
    expect(tintedTintColour(white, undefined, 0.3, 1)).toBe(white);
  });

  it("is the identity at zero strength", () => {
    expect(tintedTintColour(white, { color: seed, strength: 0 }, 0.3, 1)).toEqual(white);
  });

  it("displaces the neutral tint by the strength, and only by the strength", () => {
    const tone = tintTone(seed, 0.3, 1);
    const half = tintedTintColour(white, { color: seed, strength: 0.5 }, 0.3, 1);
    for (const index of [0, 1, 2] as const) {
      expect(half[index]).toBeCloseTo((white[index] + tone[index]) / 2, 12);
    }
  });

  it("reaches the tone at full strength", () => {
    const full = tintedTintColour(white, { color: seed, strength: 1 }, 0.3, 1);
    const tone = tintTone(seed, 0.3, 1);
    for (const index of [0, 1, 2] as const) {
      expect(full[index]).toBeCloseTo(tone[index], 12);
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
