/** W52 DL3: numeric DC accounting; source plumbing is not a rendered identity proof. */
import { describe, expect, it } from "vitest";
import {
  DEFAULT_MATERIAL_PROFILE, lowEndDcDelta, withMaterialOverrides,
} from "../src/material";
import { WGSL_OPTICS_PASS as OPTICS_WGSL } from "../src/wgsl/optics";

const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
  lowEndStrength: 1,
  lowEnd44: [0.2, 0.3, 0.4, 0.5],
  lowEnd96: [0.2, 0.3, 0.4, 0.5],
  lowEnd160: [0.2, 0.3, 0.4, 0.5],
});
const target = ((0.2 + 0.055) / 1.055) ** 2.4;

describe("W52 actual old DC", () => {
  it("subtracts the achieved clamped/partial-authority composite, not the old target", () => {
    // The shader supplies its solved values, including authority and neutral/alpha clamps.
    // mu=.02, a=.8, N=.1 gives M=.084; k=.25 gives DC=.068.
    expect(lowEndDcDelta(0, 0.02, 0.1, 0.8, 0.25, 0.7, profile))
      .toBeCloseTo(target - 0.068, 15);
    // Clipped black neutral and solved opacity are distinct achieved DCs.
    expect(lowEndDcDelta(0, 0.02, 0, 0.8, 0.25, 0.7, profile))
      .toBeCloseTo(target - 0.008, 15);
    expect(lowEndDcDelta(0, 0.02, 1, 1, 0.25, 0.7, profile))
      .toBeCloseTo(target - 0.755, 15);
  });

  it("weights the signed difference in linear light, not the encoded ordinate", () => {
    const half = withMaterialOverrides(profile, { lowEndStrength: 0.5 });
    expect(lowEndDcDelta(0, 0.02, 1, 1, 0.25, 0.7, half))
      .toBeCloseTo((target - 0.755) / 2, 15);
  });

  it("returns exact zero at identity and outside compact support without reading old DC", () => {
    const off = withMaterialOverrides(profile, { lowEndStrength: 0 });
    for (const x of [0, 8 / 255, 40 / 255]) {
      expect(lowEndDcDelta(x, NaN, NaN, NaN, NaN, 0.7, off)).toBe(0);
    }
    for (const x of [64 / 255, 0.5, 1]) {
      expect(lowEndDcDelta(x, NaN, NaN, NaN, NaN, 0.7, profile)).toBe(0);
    }
  });

  it("holds fixed-mean pairwise linear residuals even with spatially varying old appearance", () => {
    const delta = lowEndDcDelta(0, 0.02, 0.1, 0.8, 0.25, 0.7, profile);
    const oldPixels = [0.15, 0.3, 0.55].map((v, i) => v * [0.9, 0.85, 1][i]! + [0.04, 0.01, 0][i]!);
    const moved = oldPixels.map(v => v + delta * 0.6);
    for (let i = 1; i < oldPixels.length; i++) {
      expect(moved[i]! - moved[0]!).toBeCloseTo(oldPixels[i]! - oldPixels[0]!, 15);
    }
  });
});

describe("W52 GPU correction plumbing (rendered proof is separate)", () => {
  it("uses achieved OLD solve values under the old stand-downs and sampled guard", () => {
    const solve = OPTICS_WGSL.slice(OPTICS_WGSL.indexOf("var solvedNeutral = neutral;"),
      OPTICS_WGSL.indexOf("var toneTarget = toneColour.rgb;"));
    expect(solve).toContain("sizedAlpha > 1e-3 && toneAdapt < 0.995");
    expect(solve).toContain("toneStrength > 0.0 && ou.toneRowThin.w > 0.0");
    expect(solve).toContain("ou.flags.x > 0.5 && ou.lowEnd.x > 0.0 && encodedInput < 64.0 / 255.0");
    expect(solve).toContain("(1.0 - solvedAlpha) * toneLinearMean + solvedAlpha * solvedLuma");
    expect(solve).toContain("lowEndDelta = vec3f(ou.lowEnd.x * (target - oldDC) * mat)");
    expect(solve).not.toContain("authority = mix(authority, clamp(ou.toneRowThin.w, 0.0, 1.0), ou.lowEnd.x)");
    expect(solve).not.toContain("response = mix(response, low_end_response");
  });

  it("transports paint at the OLD shade and adds only after shadow and rim", () => {
    expect(OPTICS_WGSL).toContain("linear_to_srgb(clamp(colour + lowEndDelta, vec3f(0.0), vec3f(1.0)))");
    expect(OPTICS_WGSL).toContain("lowEndDelta = srgb_to_linear(mix(correctedEncoded, encodedLayer, vec3f(s))) - paintedOld");
    expect(OPTICS_WGSL).toContain("if (s >= 1.0) { lowEndDelta = vec3f(0.0); }");
    const late = OPTICS_WGSL.lastIndexOf("colour = colour + lowEndDelta;");
    expect(late).toBeGreaterThan(OPTICS_WGSL.indexOf("let rimLight = rim * rimTintColour;"));
    expect(late).toBeLessThan(OPTICS_WGSL.lastIndexOf("let body = encode_output("));
  });
});
