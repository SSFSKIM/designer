import { describe, expect, it } from "vitest";

import {
  hueDifferenceDegrees,
  linearRgbLuminance,
  linearRgbToOklab,
  linearToSrgbEncoded,
  oklabChroma,
  oklabDistance,
  srgbByteToLinear,
  srgbByteToOklab,
  srgbEncodedToLinear,
} from "../src/color";

describe("sRGB transfer (X5)", () => {
  it("round-trips through the encoded and linear domains", () => {
    // The published sRGB constants put the linear-segment breakpoint at 0.04045
    // encoded but 0.0031308 linear, which are not exact inverses of each other
    // — a ~3e-8 discontinuity that is in the standard, not in this code.
    for (const encoded of [0, 0.02, 0.04045, 0.2, 0.5, 0.735, 1]) {
      expect(linearToSrgbEncoded(srgbEncodedToLinear(encoded))).toBeCloseTo(encoded, 7);
    }
  });

  it("is not the identity — the gap is what makes linear-light math a choice", () => {
    // Mid-grey: 0.5 encoded is 21.4% of the light, not 50% of it. Averaging in
    // the wrong domain is a ~29-point error at the worst point, which is why
    // every optical metric converts explicitly.
    expect(srgbEncodedToLinear(0.5)).toBeCloseTo(0.21404114, 7);
    expect(srgbByteToLinear(128)).toBeCloseTo(0.21586, 4);
    expect(srgbByteToLinear(0)).toBe(0);
    expect(srgbByteToLinear(255)).toBe(1);
  });

  it("weights luminance so that a neutral grey has the luminance it was built from", () => {
    expect(linearRgbLuminance(0.37, 0.37, 0.37)).toBeCloseTo(0.37, 12);
  });
});

describe("OKLab", () => {
  // Reference values from Björn Ottosson's published implementation.
  it("maps linear white to L = 1 on the neutral axis", () => {
    const white = linearRgbToOklab(1, 1, 1);
    expect(white.L).toBeCloseTo(1, 6);
    expect(white.a).toBeCloseTo(0, 6);
    expect(white.b).toBeCloseTo(0, 6);
  });

  it("maps black to the origin", () => {
    const black = linearRgbToOklab(0, 0, 0);
    expect(black.L).toBeCloseTo(0, 12);
    expect(black.a).toBeCloseTo(0, 12);
    expect(black.b).toBeCloseTo(0, 12);
  });

  it("reproduces the reference values for the sRGB primaries", () => {
    const red = srgbByteToOklab(255, 0, 0);
    expect(red.L).toBeCloseTo(0.62796, 4);
    expect(red.a).toBeCloseTo(0.22486, 4);
    expect(red.b).toBeCloseTo(0.12585, 4);

    const green = srgbByteToOklab(0, 255, 0);
    expect(green.L).toBeCloseTo(0.86644, 4);
    expect(green.a).toBeCloseTo(-0.23389, 4);
    expect(green.b).toBeCloseTo(0.1795, 4);

    const blue = srgbByteToOklab(0, 0, 255);
    expect(blue.L).toBeCloseTo(0.45201, 4);
    expect(blue.a).toBeCloseTo(-0.03246, 4);
    expect(blue.b).toBeCloseTo(-0.31153, 4);
  });

  it("gives a neutral zero chroma and a colour a positive one", () => {
    expect(oklabChroma(srgbByteToOklab(120, 120, 120))).toBeCloseTo(0, 6);
    expect(oklabChroma(srgbByteToOklab(255, 0, 0))).toBeGreaterThan(0.25);
  });

  it("measures ΔE as zero for identical colours and matches the primaries' separation", () => {
    expect(oklabDistance(srgbByteToOklab(10, 20, 30), srgbByteToOklab(10, 20, 30))).toBe(0);

    const red = srgbByteToOklab(255, 0, 0);
    const green = srgbByteToOklab(0, 255, 0);
    const expected = Math.sqrt(
      (0.86644 - 0.62796) ** 2 + (-0.23389 - 0.22486) ** 2 + (0.1795 - 0.12585) ** 2,
    );
    expect(oklabDistance(red, green)).toBeCloseTo(expected, 4);
  });

  it("wraps hue differences the short way round", () => {
    expect(hueDifferenceDegrees(350, 10)).toBeCloseTo(20, 12);
    expect(hueDifferenceDegrees(10, 350)).toBeCloseTo(-20, 12);
    expect(hueDifferenceDegrees(0, 180)).toBeCloseTo(180, 12);
  });
});
