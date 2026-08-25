import { describe, expect, it } from "vitest";

import { srgbByteToOklab, oklabDistance } from "../src/color";
import { CalibrationError } from "../src/errors";
import { createImage } from "../src/image";
import { edgeEnergy, edgeWeightedDifference, oklabDeltaE, ssim } from "../src/metrics/perceptual";
import { fromLinearLuminance, fromLinearRgb, gaussianStep, solidLuminance } from "./synthesise";

/** A soft step so edge energy spreads over enough pixels to weight a block. */
function softStep(sigma = 4) {
  return fromLinearLuminance(128, 64, (x) => 0.05 + 0.8 * gaussianStep(x, 64, sigma));
}

/** Copy an image, adding a linear-light delta over a rectangle. */
function withBlock(
  base: ReturnType<typeof softStep>,
  x0: number,
  x1: number,
  y0: number,
  y1: number,
  delta: number,
): ReturnType<typeof softStep> {
  const data = new Uint8Array(base.data);
  for (let y = y0; y < y1; y += 1) {
    for (let x = x0; x < x1; x += 1) {
      const offset = (y * base.width + x) * 4;
      for (let channel = 0; channel < 3; channel += 1) {
        const index = offset + channel;
        data[index] = Math.min(255, Math.max(0, (data[index] ?? 0) + delta));
      }
    }
  }
  return createImage(base.width, base.height, data);
}

describe("edgeEnergy", () => {
  it("is zero on a flat field and positive at a step", () => {
    const flat = edgeEnergy(solidLuminance(16, 16, 0.4));
    for (const value of flat) expect(value).toBeCloseTo(0, 12);

    const step = edgeEnergy(fromLinearLuminance(16, 16, (x) => (x < 8 ? 0.05 : 0.9)));
    expect(step[8 * 16 + 7]).toBeGreaterThan(0.2);
    expect(step[8 * 16 + 2]).toBe(0);
  });
});

describe("edgeWeightedDifference", () => {
  it("is exactly zero for identical images", () => {
    const image = softStep();
    const report = edgeWeightedDifference(image, image);
    expect(report.weightedMean).toBe(0);
    expect(report.weightedP95).toBe(0);
    expect(report.unweightedMean).toBe(0);
  });

  it("weighs an error on the contour above the same error in a flat interior", () => {
    // The point of the axis: two errors of the same magnitude over the same
    // number of pixels, one across the soft edge and one far from it. What must
    // differ is how much the weighting *amplifies* each one relative to its own
    // plain mean — comparing the plain means themselves would only be comparing
    // where the perturbation happened to sit on the transfer curve.
    const base = softStep();
    const onEdge = withBlock(base, 56, 72, 12, 52, 12);
    const inFlat = withBlock(base, 8, 24, 12, 52, 12);

    const edgeReport = edgeWeightedDifference(base, onEdge);
    const flatReport = edgeWeightedDifference(base, inFlat);
    const edgeAmplification = edgeReport.weightedMean / edgeReport.unweightedMean;
    const flatAmplification = flatReport.weightedMean / flatReport.unweightedMean;

    expect(edgeAmplification).toBeGreaterThan(flatAmplification * 1.5);
    expect(edgeReport.weightedP95).toBeGreaterThan(0);
    expect(flatReport.weightedP95).toBeGreaterThan(0);
    expect(edgeReport.weightedP95).toBeGreaterThan(flatReport.weightedP95);
  });

  it("falls back to an unweighted mean when the scene has no edges at all", () => {
    const a = solidLuminance(32, 32, 0.4);
    const b = solidLuminance(32, 32, 0.5);
    const report = edgeWeightedDifference(a, b);
    // Every weight is 1, so the weighted and plain means must coincide.
    expect(report.weightedMean).toBeCloseTo(report.unweightedMean, 12);
  });

  it("honours the gain, and gain zero is the plain mean", () => {
    const base = softStep();
    const perturbed = withBlock(base, 60, 68, 20, 44, 12);
    const plain = edgeWeightedDifference(base, perturbed, { edgeGain: 0 });
    expect(plain.weightedMean).toBeCloseTo(plain.unweightedMean, 12);
    expect(edgeWeightedDifference(base, perturbed, { edgeGain: 16 }).weightedMean).toBeGreaterThan(
      plain.weightedMean,
    );
  });
});

describe("ssim", () => {
  it("is exactly 1 in mean and in the worst window for identical images", () => {
    const image = softStep();
    const report = ssim(image, image);
    expect(report.mean).toBeCloseTo(1, 12);
    expect(report.min).toBeCloseTo(1, 12);
    expect(report.windowCount).toBe((128 - 10) * (64 - 10));
  });

  it("drops when structure is lost, and the worst window drops further", () => {
    const sharp = softStep(1);
    const blurred = softStep(6);
    const report = ssim(sharp, blurred);
    expect(report.mean).toBeLessThan(0.99);
    expect(report.min).toBeLessThan(report.mean);
    expect(report.min).toBeGreaterThan(-1);
  });

  it("notices a blur of the wrong width even when the mean level is right", () => {
    // Both have the same total light and the same plateaus; only the width of
    // the transition differs. This is the material failure SSIM is here for.
    const narrow = ssim(softStep(2), softStep(3));
    const wide = ssim(softStep(2), softStep(8));
    expect(wide.mean).toBeLessThan(narrow.mean);
  });

  it("refuses an image smaller than its own window", () => {
    expect(() => ssim(solidLuminance(8, 8, 0.5), solidLuminance(8, 8, 0.5))).toThrowError(CalibrationError);
  });
});

describe("oklabDeltaE", () => {
  it("is exactly zero for identical images", () => {
    const image = fromLinearRgb(16, 16, (x, y) => [x / 16, y / 16, 0.3]);
    const report = oklabDeltaE(image, image);
    expect(report.mean).toBe(0);
    expect(report.p95).toBe(0);
    expect(report.max).toBe(0);
    expect(report.sampleCount).toBe(256);
  });

  it("matches the closed-form distance between two flat primaries", () => {
    const red = createImage(4, 4, new Uint8Array(64).fill(0).map((_, i) => (i % 4 === 0 || i % 4 === 3 ? 255 : 0)));
    const green = createImage(
      4,
      4,
      new Uint8Array(64).fill(0).map((_, i) => (i % 4 === 1 || i % 4 === 3 ? 255 : 0)),
    );
    const expected = oklabDistance(srgbByteToOklab(255, 0, 0), srgbByteToOklab(0, 255, 0));

    const report = oklabDeltaE(red, green);
    expect(report.mean).toBeCloseTo(expected, 10);
    expect(report.max).toBeCloseTo(expected, 10);
  });

  it("orders a small tint below a large one", () => {
    const neutral = fromLinearRgb(16, 16, () => [0.25, 0.25, 0.25]);
    const slight = fromLinearRgb(16, 16, () => [0.25, 0.25, 0.28]);
    const strong = fromLinearRgb(16, 16, () => [0.25, 0.25, 0.5]);
    expect(oklabDeltaE(neutral, slight).mean).toBeLessThan(oklabDeltaE(neutral, strong).mean);
    expect(oklabDeltaE(neutral, slight).mean).toBeGreaterThan(0);
  });
});
