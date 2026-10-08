/** W50 DL4: fixed compact support, measured rows, and a join at the actual span. */
import { describe, expect, it } from "vitest";
import {
  DEFAULT_MATERIAL_PROFILE, backdropToneResponse, backdropToneSolveWeight,
  materialDigestInput, withMaterialOverrides, type MaterialProfilePatch,
} from "../src/material";

const old = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
  backdropToneResponseThin: [0.003, 0.04, 0.2, 0.3],
  backdropToneResponseThick: [0.001, 0.03, 0.15, 0.25],
  backdropToneBlackStrength: 1, backdropToneBlackThin: 0.01, backdropToneBlackThick: 0.006,
});
const chart: MaterialProfilePatch = {
  lowEndStrength: 1,
  lowEnd44: [20, 28, 48, 60].map(v => v / 255) as [number, number, number, number],
  lowEnd96: [21, 29, 49, 61].map(v => v / 255) as [number, number, number, number],
  lowEnd160: [22, 30, 50, 62].map(v => v / 255) as [number, number, number, number],
};
const decode = (v: number) => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const encode = (v: number) => v <= 0.0031308 ? v * 12.92 : 1.055 * v ** (1 / 2.4) - 0.055;

describe("W50 low-end chart", () => {
  it("owns target and authority together; input and physical span interpolate linearly", () => {
    const on = withMaterialOverrides(old, chart);
    expect(backdropToneResponse(4 / 255, 1, on, 0, 70)).toBeCloseTo(decode(24.5 / 255), 14);
    expect(backdropToneResponse(20 / 255, 0, on, 0, 128)).toBeCloseTo(decode(41.5 / 255), 14);
    expect(backdropToneResponse(0, 1, on, 0, 224)).toBeCloseTo(decode(22 / 255), 14);
    expect(backdropToneSolveWeight(0.0035, on)).toBe(1);
  });
  it("joins the old response at actual span, never an interpolated row join", () => {
    const on = withMaterialOverrides(old, chart);
    // Nonlinear thickness and far-level terms are already evaluated for this span.
    const join = encode(backdropToneResponse(64 / 255, 0.71, old, 0.007, 128));
    const t40 = 61.5 / 255;
    expect(backdropToneResponse(52 / 255, 0.71, on, 0.007, 128))
      .toBeCloseTo(decode((t40 + join) / 2), 14);
    for (const x of [64 / 255, 0.5, 1]) {
      expect(backdropToneResponse(x, 0.71, on, 0.007, 128))
        .toBe(backdropToneResponse(x, 0.71, old, 0.007, 128));
      expect(backdropToneSolveWeight(x, on)).toBe(backdropToneSolveWeight(x, old));
    }
  });
  it("drops the entire chart at identity and preserves exact old arithmetic", () => {
    const off = withMaterialOverrides(old, { ...chart, lowEndStrength: 0 });
    expect(materialDigestInput(off)).toEqual(materialDigestInput(old));
    for (const x of [0, 0.002, 0.0035, 0.004, 8 / 255, 40 / 255, 64 / 255, 1]) {
      expect(backdropToneSolveWeight(x, off)).toBe(backdropToneSolveWeight(x, old));
      expect(backdropToneResponse(x, 0.71, off, 0.007, 224))
        .toBe(backdropToneResponse(x, 0.71, old, 0.007, 224));
    }
  });
  it("rejects malformed active charts and never claims clamping is validation", () => {
    for (const lowEnd44 of [[0, 0.1, NaN, 0.3], [0, 0.2, 0.1, 0.3], [0, 0.1, 0.2, 1.1], [0, 0.1]]) {
      expect(() => withMaterialOverrides(old, { ...chart, lowEnd44 } as unknown as MaterialProfilePatch)).toThrow();
    }
    for (const lowEndStrength of [NaN, -1, 1.1]) {
      expect(() => withMaterialOverrides(old, { ...chart, lowEndStrength })).toThrow();
    }
  });
});
