/** The CSS solve must carry the same low-end branch without weakening its guards (§5.179). */
import { describe, expect, it } from "vitest";
import { MATERIAL_SOURCE_OPTICS, resolvedBackdropToneResponse, toneRespondedSourceOptics } from "../src/optics";
import type { RendererMaterialProfile } from "../src/renderer-bridge";
const source = { ...MATERIAL_SOURCE_OPTICS.regular, tint: [1, 1, 1] as const, tintAlpha: 0.46 };
const patch = {
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
  backdropToneResponseThin: [0.214, 0.2835, 0.5383, 0.937],
  backdropToneResponseThick: [0.242, 0.3074, 0.5554, 0.957],
  backdropToneBlackStrength: 1, backdropToneBlackThin: 0.2, backdropToneBlackThick: 0.3,
} as RendererMaterialProfile;
const decode = (x: number) => x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
describe("W36 CSS black branch", () => {
  it("lands black on the requested level rather than sizedAlpha times neutral", () => {
    const result = toneRespondedSourceOptics(source, { luminance: 0, linearLuminance: 0 },
      0, 0, 1, resolvedBackdropToneResponse(patch));
    expect(result.tintAlpha * result.tint[0]).toBeCloseTo(0.2, 12);
  });
  it("preserves alpha, collapse and no-tone stand-downs on the on-state", () => {
    const response = resolvedBackdropToneResponse(patch);
    for (const [alpha, k, strength] of [[0, 0, 1], [0.001, 0, 1], [0.46, 0.995, 1],
      [0.46, 1, 1], [0.46, 0, 0]]) {
      const input = { ...source, tintAlpha: alpha! };
      expect(toneRespondedSourceOptics(input, { luminance: 0, linearLuminance: 0 },
        0, k!, strength!, response)).toBe(input);
    }
    expect(toneRespondedSourceOptics(source, { luminance: 0, linearLuminance: 0 },
      0, 0, 1, { ...response, strength: 0 })).toBe(source);
  });
  it("keeps the identified domain exact and rejoins continuously", () => {
    const on = resolvedBackdropToneResponse(patch);
    const off = resolvedBackdropToneResponse({ ...patch, backdropToneBlackStrength: 0 });
    const solve = (x: number, r: typeof on) => toneRespondedSourceOptics(source,
      { luminance: decode(x), linearLuminance: decode(x) }, 0.09228515625, 0, 1, r);
    for (const x of [0.003, 0.003195, 0.003284, 0.00375, 0.004, 0.11, 0.425, 1]) {
      expect(solve(x, on)).toEqual(solve(x, off));
    }
    expect(solve(0.003 - 1e-10, on).tint[0]).toBeCloseTo(solve(0.003, off).tint[0], 7);
  });
});
