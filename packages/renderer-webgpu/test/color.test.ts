/**
 * X5 — the colour pipeline.
 *
 * The load-bearing assertions here are not "sRGB round-trips" (it does, and that
 * would be a test of `Math.pow`). They are:
 *
 *  1. **The WGSL and the TypeScript carry the same curve.** A golden regenerated
 *     on the GPU and asserted against a CPU expectation must not drift by a code
 *     unit, and the only thing standing between those two is that both use the
 *     exact piecewise sRGB definition rather than one of them taking the 2.2
 *     shortcut.
 *  2. **Premultiplication happens in the encoded space.** Getting that backwards
 *     darkens every antialiased edge in the whole renderer, and it is invisible
 *     in a solid-colour test.
 */

import { describe, expect, it } from "vitest";

import {
  alphaNormalisationMode,
  BACKDROP_ALPHA_MODES,
  displayP3ToSrgbLinear,
  encodeOutput,
  encodeOutputBytes,
  importColorMatrix,
  linearToSrgb,
  linearToSrgbChannel,
  LUMINANCE_WEIGHTS,
  OUTPUT_TEXTURE_FORMAT,
  relativeLuminance,
  srgbToLinear,
  srgbToLinearChannel,
  WORKING_TEXTURE_FORMAT,
} from "../src/color";
import { WGSL_PRELUDE } from "../src/wgsl/prelude";

describe("the sRGB transfer function", () => {
  it("round-trips across the whole range", () => {
    for (let i = 0; i <= 255; i += 1) {
      const encoded = i / 255;
      expect(srgbToLinearChannel(linearToSrgbChannel(srgbToLinearChannel(encoded)))).toBeCloseTo(
        srgbToLinearChannel(encoded),
        12,
      );
    }
  });

  it("is continuous across the piecewise join", () => {
    // The join at 0.04045 / 0.0031308 is where a mismatched constant shows up as a
    // visible step in a gradient rather than as a rounding difference.
    const below = srgbToLinearChannel(0.04045 - 1e-9);
    const above = srgbToLinearChannel(0.04045 + 1e-9);
    expect(Math.abs(above - below)).toBeLessThan(1e-7);

    const encodedBelow = linearToSrgbChannel(0.0031308 - 1e-12);
    const encodedAbove = linearToSrgbChannel(0.0031308 + 1e-12);
    expect(Math.abs(encodedAbove - encodedBelow)).toBeLessThan(1e-7);
  });

  it("is not the 2.2-gamma approximation", () => {
    // 0.5 encoded is 0.2140 linear under the real curve and 0.2176 under 2.2.
    expect(srgbToLinearChannel(0.5)).toBeCloseTo(0.21404114, 7);
    expect(srgbToLinearChannel(0.5)).not.toBeCloseTo(Math.pow(0.5, 2.2), 4);
  });

  it("shares every constant with the WGSL prelude", () => {
    // The whole point of X5's lock: one curve, two implementations, no drift.
    for (const constant of ["12.92", "0.04045", "1.055", "0.055", "2.4", "0.0031308"]) {
      expect(WGSL_PRELUDE, `WGSL must use ${constant}`).toContain(constant);
    }
    // The exponent pair of the real curve, not a single gamma.
    expect(WGSL_PRELUDE).toContain("vec3f(2.4)");
    expect(WGSL_PRELUDE).toContain("vec3f(1.0 / 2.4)");
  });
});

describe("luminance", () => {
  it("uses Rec.709 weights that sum to one", () => {
    const sum = LUMINANCE_WEIGHTS[0] + LUMINANCE_WEIGHTS[1] + LUMINANCE_WEIGHTS[2];
    expect(sum).toBeCloseTo(1, 6);
  });

  it("weights linear light, so a mid-grey is not mid-luminance", () => {
    const midEncoded = srgbToLinear([0.5, 0.5, 0.5]);
    expect(relativeLuminance(midEncoded)).toBeCloseTo(0.21404114, 6);
    // Weighting the ENCODED value would give 0.5, which is the bug this guards.
    expect(relativeLuminance([0.5, 0.5, 0.5])).toBeCloseTo(0.5, 6);
  });

  it("matches the weights the WGSL uses", () => {
    expect(WGSL_PRELUDE).toContain("vec3f(0.2126, 0.7152, 0.0722)");
  });
});

describe("output encoding", () => {
  it("premultiplies in the encoded space, not in linear", () => {
    const linear: [number, number, number] = [0.2, 0.2, 0.2];
    const alpha = 0.5;
    const encoded = encodeOutput(linear, alpha);

    const encodedThenMultiplied = linearToSrgb(linear)[0] * alpha;
    const multipliedThenEncoded = linearToSrgbChannel(linear[0] * alpha);

    expect(encoded[0]).toBeCloseTo(encodedThenMultiplied, 12);
    // The two differ by 12% of full scale at this alpha — which is exactly the
    // darkening a wrong order produces on every soft edge.
    expect(Math.abs(encodedThenMultiplied - multipliedThenEncoded)).toBeGreaterThan(0.05);
  });

  it("carries alpha through unchanged and clamps it", () => {
    expect(encodeOutput([1, 1, 1], 0.25)[3]).toBe(0.25);
    expect(encodeOutput([1, 1, 1], 2)[3]).toBe(1);
    expect(encodeOutput([1, 1, 1], -1)[3]).toBe(0);
  });

  it("quantises to bytes the way a golden PNG holds them", () => {
    expect(encodeOutputBytes([1, 1, 1], 1)).toEqual([255, 255, 255, 255]);
    expect(encodeOutputBytes([0, 0, 0], 1)).toEqual([0, 0, 0, 255]);
    expect(encodeOutputBytes([1, 1, 1], 0)).toEqual([0, 0, 0, 0]);
  });

  it("matches the WGSL's own encode_output", () => {
    expect(WGSL_PRELUDE).toContain("linear_to_srgb(linear) * a");
  });
});

describe("import normalisation", () => {
  it("hands the shader an identity matrix for sRGB", () => {
    expect([...importColorMatrix("srgb")]).toEqual([1, 0, 0, 0, 1, 0, 0, 0, 1]);
  });

  it("converts P3 primaries toward sRGB without changing neutral grey", () => {
    const grey = displayP3ToSrgbLinear([0.5, 0.5, 0.5]);
    expect(grey[0]).toBeCloseTo(0.5, 6);
    expect(grey[1]).toBeCloseTo(0.5, 6);
    expect(grey[2]).toBeCloseTo(0.5, 6);
  });

  it("expands a saturated P3 primary past the sRGB gamut and clamps it", () => {
    // P3 red is outside sRGB, so the honest v1 answer is a clamp — and the reason
    // the colour space is TAGGED rather than assumed, so a future profile can
    // convert differently without touching a shader.
    const red = displayP3ToSrgbLinear([1, 0, 0]);
    expect(red[0]).toBe(1);
    expect(red[1]).toBe(0);
  });

  it("gives the P3 matrix to the shader as nine floats", () => {
    expect(importColorMatrix("display-p3")).toHaveLength(9);
    expect(importColorMatrix("display-p3")[0]).toBeGreaterThan(1);
  });

  it("enumerates exactly three alpha modes, and maps each to its own flag", () => {
    expect(BACKDROP_ALPHA_MODES).toEqual(["premultiplied", "unpremultiplied", "opaque"]);
    const flags = BACKDROP_ALPHA_MODES.map(alphaNormalisationMode);
    expect(new Set(flags).size).toBe(3);
    expect(alphaNormalisationMode("premultiplied")).toBe(0);
  });
});

describe("the format lock", () => {
  it("keeps every internal texture float and every output 8-bit non-srgb", () => {
    // rgba16float internally: 8-bit linear would band visibly through a blur
    // chain. A plain (non "-srgb") output format: the shader encodes, so hardware
    // encoding on top would apply the curve twice.
    expect(WORKING_TEXTURE_FORMAT).toBe("rgba16float");
    expect(OUTPUT_TEXTURE_FORMAT).toBe("rgba8unorm");
    expect(OUTPUT_TEXTURE_FORMAT).not.toContain("srgb");
  });
});
