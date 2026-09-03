import { describe, expect, it } from "vitest";

import { srgbByteToOklab, oklabDistance } from "../src/color";
import { CalibrationError } from "../src/errors";
import { createImage } from "../src/image";
import {
  edgeEnergy,
  edgeWeightedDifference,
  oklabDeltaE,
  ssim,
  ssimDepthWindows,
  ssimMap,
  SSIM_BAND_SPLIT_CSS_PX,
} from "../src/metrics/perceptual";
import {
  fromLinearLuminance,
  fromLinearRgb,
  distanceOutsideRect,
  gaussianStep,
  maskFromPredicate,
  rectPredicate,
  solidLuminance,
} from "./synthesise";

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

/**
 * The band-windowed rows (W13 X6).
 *
 * The geometry is a rectangle, whose depth from the boundary ring is exactly
 * `min(x - x0, x1 - x, y - y0, y1 - y)` — so every assertion below knows which
 * window class a perturbation lands in by algebra, not by asking the distance
 * transform to grade its own homework.
 */
describe("ssimDepthWindows", () => {
  const WIDTH = 200;
  const HEIGHT = 200;
  const X0 = 40;
  const X1 = 159;
  const Y0 = 40;
  const Y1 = 159;

  /** Depth of an interior pixel below the rectangle's boundary ring, in pixels. */
  const depth = (x: number, y: number): number => Math.min(x - X0, X1 - x, y - Y0, Y1 - y);

  /** Distance from an exterior pixel to that same ring — exact for a rectangle. */
  const outward = (x: number, y: number): number => distanceOutsideRect(x, y, X0, Y0, X1, Y1);

  const isInside = rectPredicate(X0, Y0, X1, Y1);

  const silhouette = maskFromPredicate(WIDTH, HEIGHT, rectPredicate(X0, Y0, X1, Y1));

  /** A textured field, so a perturbation has structure to destroy. */
  const base = fromLinearLuminance(WIDTH, HEIGHT, (x, y) => 0.3 + 0.2 * Math.sin(x / 3) * Math.cos(y / 5));

  /** The same field with a wave added over every pixel a predicate accepts. */
  const perturb = (inside: (x: number, y: number) => boolean) =>
    fromLinearLuminance(WIDTH, HEIGHT, (x, y) => {
      const value = 0.3 + 0.2 * Math.sin(x / 3) * Math.cos(y / 5);
      return inside(x, y) ? value + 0.15 * Math.sin(x / 2) : value;
    });

  /*
   * The 6px margins below are the SSIM window's own half-width plus one: a
   * window centred at depth d reads pixels from depth d - 5 to d + 5, so a
   * perturbation kept 6px clear of the split cannot reach a window centred on
   * the other side of it.
   */
  const SPLIT = 24;

  it("scores all three windows at 1 for identical images", () => {
    const windows = ssimDepthWindows(ssimMap(base, base), silhouette, { splitPx: SPLIT });
    expect(windows.band?.mean).toBeCloseTo(1, 12);
    expect(windows.interior?.mean).toBeCloseTo(1, 12);
    expect(windows.outside?.mean).toBeCloseTo(1, 12);
  });

  it("the three rows plus the far field partition the crop exactly", () => {
    const map = ssimMap(base, base);
    const windows = ssimDepthWindows(map, silhouette, { splitPx: SPLIT });

    // The far field, counted independently: outside the silhouette and farther
    // than the split from its contour. No row carries it, and `ssimMean` does.
    let farField = 0;
    let inside = 0;
    for (let y = map.offset; y < HEIGHT - map.offset; y += 1) {
      for (let x = map.offset; x < WIDTH - map.offset; x += 1) {
        if (silhouette.mask[y * WIDTH + x] === 1) {
          inside += 1;
        } else if (outward(x, y) > SPLIT) {
          farField += 1;
        }
      }
    }
    const counted =
      (windows.band?.windowCount ?? 0) +
      (windows.interior?.windowCount ?? 0) +
      (windows.outside?.windowCount ?? 0);
    expect(counted + farField).toBe(map.data.length);
    // The band and interior alone are the surface, not the crop, so the three
    // rows cannot average back to `ssimMean`.
    expect((windows.band?.windowCount ?? 0) + (windows.interior?.windowCount ?? 0)).toBe(inside);
    expect(counted).toBeLessThan(map.data.length);
  });

  it("a perturbation confined to the band moves ssimBand and leaves ssimInterior at 1", () => {
    const map = ssimMap(base, perturb((x, y) => depth(x, y) <= SPLIT - 6));
    const windows = ssimDepthWindows(map, silhouette, { splitPx: SPLIT });
    expect(windows.band?.mean).toBeLessThan(0.95);
    expect(windows.interior?.mean).toBeCloseTo(1, 12);
  });

  it("a perturbation confined to the deep interior moves ssimInterior and leaves ssimBand at 1", () => {
    const map = ssimMap(base, perturb((x, y) => depth(x, y) >= SPLIT + 6));
    const windows = ssimDepthWindows(map, silhouette, { splitPx: SPLIT });
    expect(windows.interior?.mean).toBeLessThan(0.95);
    expect(windows.band?.mean).toBeCloseTo(1, 12);
  });

  it("a perturbation confined to the exterior band moves only ssimOutside", () => {
    // Outside the rectangle, within the split of its contour. The inner margin
    // is 8 rather than 6 because a window centred on a corner of the boundary
    // ring reaches 5√2 ≈ 7.07 px diagonally outward, and no band window may
    // touch the change.
    const map = ssimMap(
      base,
      perturb((x, y) => !isInside(x, y) && outward(x, y) >= 8 && outward(x, y) <= SPLIT - 5),
    );
    const windows = ssimDepthWindows(map, silhouette, { splitPx: SPLIT });
    expect(windows.outside?.mean).toBeLessThan(0.95);
    expect(windows.band?.mean).toBeCloseTo(1, 12);
    expect(windows.interior?.mean).toBeCloseTo(1, 12);
  });

  it("splits at the backing scale: the same CSS-px band is twice as many device px at 2x", () => {
    // A perturbation at device depth 30-42: interior of a 24 device-px split
    // (1x), band of a 48 device-px one (the same 24 CSS px at scale 2).
    const map = ssimMap(base, perturb((x, y) => depth(x, y) >= 30 && depth(x, y) <= 42));
    const atOneX = ssimDepthWindows(map, silhouette, { splitPx: SSIM_BAND_SPLIT_CSS_PX * 1 });
    const atTwoX = ssimDepthWindows(map, silhouette, { splitPx: SSIM_BAND_SPLIT_CSS_PX * 2 });

    expect(atOneX.band?.mean).toBeCloseTo(1, 12);
    expect(atOneX.interior?.mean).toBeLessThan(0.99);
    expect(atTwoX.band?.mean).toBeLessThan(0.99);
    expect(atTwoX.interior?.mean).toBeCloseTo(1, 12);
    expect(atTwoX.band?.windowCount ?? 0).toBeGreaterThan(atOneX.band?.windowCount ?? 0);
  });

  it("reports no interior at all for a surface shallower than the split", () => {
    // Half-span 15px: every pixel is band, and the interior row is absent
    // rather than zero — `rrect-sm` and `capsule-button` on the real bed.
    const shallow = maskFromPredicate(WIDTH, HEIGHT, rectPredicate(80, 80, 109, 109));
    const windows = ssimDepthWindows(ssimMap(base, base), shallow, { splitPx: SPLIT });
    expect(windows.band?.mean).toBeCloseTo(1, 12);
    expect(windows).not.toHaveProperty("interior");
  });

  it("ignores extraction holes rather than treating their walls as contour", () => {
    // A punched-out interior pixel is not an outline (see `contourDistance`),
    // so it must not pull deep pixels into the band.
    const holed = maskFromPredicate(
      WIDTH,
      HEIGHT,
      (x, y) => rectPredicate(X0, Y0, X1, Y1)(x, y) && !rectPredicate(98, 98, 101, 101)(x, y),
    );
    const solid = ssimDepthWindows(ssimMap(base, base), silhouette, { splitPx: SPLIT });
    const withHole = ssimDepthWindows(ssimMap(base, base), holed, { splitPx: SPLIT });
    expect(withHole.band?.windowCount).toBe(solid.band?.windowCount);
    expect(withHole.interior?.windowCount).toBe(solid.interior?.windowCount);
  });

  it("refuses a silhouette that is not the grid the map came from", () => {
    const map = ssimMap(base, base);
    const wrong = maskFromPredicate(64, 64, rectPredicate(8, 8, 40, 40));
    expect(() => ssimDepthWindows(map, wrong, { splitPx: SPLIT })).toThrowError(CalibrationError);
  });
});
