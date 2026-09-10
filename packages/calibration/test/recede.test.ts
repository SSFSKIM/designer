import { describe, expect, it } from "vitest";
import { readInterior, difference } from "../scripts/recede";
import { createImage } from "../src/image";
import { componentRegion } from "../src/component-region";

const image = (values: number[]) => createImage(values.length, 1,
  Uint8Array.from(values.flatMap((v) => [v, v, v, 255])));
const mask = { width: 4, height: 1, mask: Uint8Array.of(0, 1, 1, 0) };

describe("W27c recovered-bed instrument", () => {
  it("uses the declared population even when the material is invisible", () => {
    const backdrop = image([255, 32, 32, 255]);
    const measured = readInterior(backdrop, backdrop, mask);
    expect(measured.sampleCount).toBe(2);
    expect(measured.meanEncoded).toBeCloseTo(32 / 255, 12);
    expect(measured.stdDevLinear).toBe(0);
    expect(measured.encodedRange).toBe(0);
    expect(difference(backdrop, backdrop, mask).differentRgbPixels).toBe(0);
  });

  it("keeps encoded and linear means distinct rather than encoding a light mean", () => {
    const backdrop = image([0, 0, 255, 0]);
    const measured = readInterior(backdrop, backdrop, mask);
    expect(measured.meanLinear).toBeCloseTo(0.5, 12);
    expect(measured.meanEncoded).toBeCloseTo(0.5, 12);
    expect(measured.stdDevLinear).toBeCloseTo(0.5, 12);
    expect(measured.stdDevEncoded).toBeCloseTo(0.5, 12);
    expect(measured.meanOklabChroma).toBeLessThan(1e-7);
  });

  it("counts exterior change at strictly more than one code, not interior change", () => {
    const backdrop = image([10, 10, 10, 10]);
    const measured = difference(image([11, 255, 10, 12]), backdrop, mask);
    expect(measured.differentRgbPixels).toBe(3);
    expect(measured.exteriorBeyondOneCode).toBe(1);
    expect(measured.changed).toEqual([3]);
    expect(measured.maxChannelDelta).toBe(245);
  });

  it("does not cancel chroma by averaging complementary pixels first", () => {
    const painted = createImage(4, 1, Uint8Array.from([
      0, 0, 0, 255, 255, 0, 0, 255, 0, 255, 255, 255, 0, 0, 0, 255,
    ]));
    const measured = readInterior(painted, image([0, 0, 0, 0]), mask);
    expect(measured.meanOklabChroma).toBeGreaterThan(0.1);
    expect(measured.chromaOfMeanLight).toBeLessThan(1e-7);
  });

  it("scales the declared union without letting a stack double-count its overlap", () => {
    const region = componentRegion({ kind: "stack",
      base: { kind: "rrect", size: [8, 8], radius: 0 },
      over: { kind: "rrect", size: [4, 4], radius: 0 } },
    { canvas: { width: 12, height: 12 }, scale: 2, width: 24, height: 24 });
    expect(region.areaPx).toBe(16 * 16);
    expect(region.silhouette.mask.reduce((a, b) => a + b, 0)).toBe(16 * 16);
  });
});
