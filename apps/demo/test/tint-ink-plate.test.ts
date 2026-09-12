/**
 * The band's two grounds state the level they are painted at.
 *
 * A backdrop hint is a *declared fact* about what is behind a group, and the
 * runtime has no way to check one: a hint that is plausible but wrong moves the
 * body, the tint's shade and the ink with it, silently. So the one thing worth
 * asserting about `TintInkPlate` outside a browser is that its arithmetic is the
 * sRGB transfer function and nothing else — the ground is painted from the byte
 * the stated luminance is decoded from, so the two cannot drift apart.
 */

import { describe, expect, it } from "vitest";

import { INK_GROUNDS, linearLevel, tintDeclaration } from "../src/TintInkPlate";

describe("the grounds' declared levels", () => {
  it("decodes each ground's byte with sRGB's own transfer function", () => {
    // Two independent readings of the same two greys: the piecewise standard
    // above the linear segment, computed here from the specification's constants.
    expect(linearLevel(231)).toBeCloseTo(((231 / 255 + 0.055) / 1.055) ** 2.4, 12);
    expect(linearLevel(29)).toBeCloseTo(((29 / 255 + 0.055) / 1.055) ** 2.4, 12);
    // The linear segment, which no ground uses but the function must still get
    // right for anyone who paints one darker than 0.04045 encoded.
    expect(linearLevel(5)).toBeCloseTo(5 / 255 / 12.92, 12);
  });

  it("keeps the two grounds at opposite ends and in their declared tones", () => {
    const [light, dark] = INK_GROUNDS;
    expect(light.tone).toBe("light");
    expect(dark.tone).toBe("dark");
    expect(linearLevel(light.byte)).toBeGreaterThan(0.5);
    expect(linearLevel(dark.byte)).toBeLessThan(0.05);
  });
});

describe("a seed and a strength as one CSS colour", () => {
  it("puts the strength in the colour's own alpha", () => {
    expect(tintDeclaration("#ff9500", 100)).toBe("rgb(255 149 0 / 100%)");
    expect(tintDeclaration("#ff9500", 50)).toBe("rgb(255 149 0 / 50%)");
    expect(tintDeclaration("#000000", 0)).toBe("rgb(0 0 0 / 0%)");
  });
});
