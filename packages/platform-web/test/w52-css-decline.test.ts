/** W52-DL3 request math is not the CSS or unsampled DOM-GPU runtime projection. */
import { describe, expect, it } from "vitest";
import {
  CSS_DECLINED_LOW_END_STRENGTH,
  cssProjectedBackdropToneResponse,
  lowEndChartTarget,
  lowEndDcDelta,
  resolvedBackdropToneResponse,
} from "../src/optics";

const decode = (x: number): number =>
  x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
const chart = {
  lowEndStrength: 1,
  lowEnd44: [20 / 255, 28 / 255, 50 / 255, 64 / 255] as const,
  lowEnd96: [24 / 255, 32 / 255, 54 / 255, 68 / 255] as const,
  lowEnd160: [28 / 255, 36 / 255, 58 / 255, 72 / 255] as const,
};

describe("W52 CSS decline and scalar request", () => {
  it("separates a nonzero chart request from the actual gate-off CSS projection", () => {
    const requested = resolvedBackdropToneResponse(chart);
    const projected = cssProjectedBackdropToneResponse(requested);
    expect(CSS_DECLINED_LOW_END_STRENGTH).toBe(0);
    expect(projected.lowEndStrength).toBe(CSS_DECLINED_LOW_END_STRENGTH);
    expect(requested.lowEndStrength).toBe(1);
    expect(lowEndChartTarget(4 / 255, 0, requested)).toBeCloseTo(decode(24 / 255), 14);
    expect(projected).toEqual({ ...requested, lowEndStrength: 0 });
    const off = resolvedBackdropToneResponse({ ...chart, lowEndStrength: 0 });
    expect(cssProjectedBackdropToneResponse(off)).toBe(off);
  });

  it("subtracts achieved old DC, including partial collapse and the independent linear mean", () => {
    const requested = resolvedBackdropToneResponse({ ...chart, lowEndStrength: 0.4 });
    // Encoded mean is code 4, but the structured source's independent linear mean is 0.1.
    // Old DC = 0.75 * (0.2 * 0.1 + 0.8 * 0.03) + 0.25 * 0.1 = 0.058.
    const target = decode(24 / 255);
    expect(lowEndChartTarget(4 / 255, 0, requested)).toBeCloseTo(target, 14);
    const delta = lowEndDcDelta(4 / 255, 0.1, 0.03, 0.8, 0.25, 0, requested);
    expect(delta).toBeCloseTo(0.4 * (target - 0.058), 14);
    expect(delta).toBeLessThan(0);
    // No clamping of a signed request, nor use of old response target as achieved DC.
    expect(lowEndDcDelta(4 / 255, 0, 0, 0.8, 0, 0, requested))
      .toBeCloseTo(0.4 * target, 14);
  });

  it("returns exact zero at identity and in the protected input64 domain without reading rows", () => {
    const unread = resolvedBackdropToneResponse(chart);
    Object.defineProperty(unread, "lowEnd44", { get: () => { throw new Error("read chart"); } });
    for (const code of [64, 69, 255]) {
      expect(lowEndDcDelta(code / 255, 0.1, 0.03, 0.8, 0.25, 0, unread)).toBe(0);
    }
    expect(lowEndDcDelta(0, 0.1, 0.03, 0.8, 0.25, 0,
      { ...resolvedBackdropToneResponse(chart), lowEndStrength: 0 })).toBe(0);
  });
});
