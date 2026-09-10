import { describe, expect, it } from "vitest";
import type { ResolvedMaterialPolicy } from "@vitreajs/vitrea";

import { materialAtBackdrop } from "../src/optics";

const policy: ResolvedMaterialPolicy = {
  glass: "material", colorSource: "material", frost: "nominal", refraction: "nominal",
  occlusion: "nominal", border: "nominal", ambientTint: "nominal", foreground: "adaptive",
};
const decode = (v: number): number => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const dark = decode(0.1104);
const tone = { rgb: [dark, dark, dark] as const, luminance: dark, linearLuminance: dark };

describe("the profile material at a DOM backdrop tone", () => {
  it("lands the thick dark body on the response, rather than solving at an encoded alpha", () => {
    const result = materialAtBackdrop(undefined, "regular", tone, 96, policy);
    expect(result.level).toBeCloseTo(0.4953, 8);
    expect(result.shade).toBeCloseTo(0.5289 + (1.0175 - 0.5289) * 0.4953, 8);
  });

  it("keeps the small surface's collapse distinct from the thick member of the same group", () => {
    const small = materialAtBackdrop(undefined, "regular", tone, 32, policy);
    const thick = materialAtBackdrop(undefined, "regular", tone, 96, policy);
    expect(small.adaptation).toBe(1);
    expect(small.level).toBeCloseTo(dark, 10);
    expect(small.shade).toBe(1);
    expect(thick.level - small.level).toBeGreaterThan(0.45);
  });

  it("does not manufacture a tone or a collapse when no source can state one", () => {
    const unknown = materialAtBackdrop(undefined, "regular", undefined, 32, policy);
    expect(unknown.tone).toBeUndefined();
    expect(unknown.adaptation).toBe(0);
    expect(unknown.adapted.tintAlpha).toBeCloseTo(0.46, 10);
  });

  it("takes the dark scheme's difference document and both shadow terms through the same law", () => {
    const result = materialAtBackdrop({
      optics: { regular: { tint: [0.03, 0.03, 0.03], tintAlpha: 0.8 } },
      backdropToneResponseStrength: 0,
      backdropToneMax: 0,
      tintShadeStrength: 0,
      sizeOcclusionGain: 0,
      outerShadow: { liftAmplitude: 0.02 },
    }, "regular", { rgb: [0.5, 0.5, 0.5], luminance: 0.5, linearLuminance: 0.5 }, 128, policy);
    expect(result.level).toBeCloseTo(0.124, 10);
    expect(result.shade).toBe(1);
    expect(result.shadow.occlusion).toBeCloseTo(0.448, 10);
    expect(result.shadow.lift).toBeCloseTo(0.01, 10);
  });
});
