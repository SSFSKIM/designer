import { describe, expect, it } from "vitest";

import { CalibrationError } from "../src/errors";
import { contourCurvature, contourDistance, cornerCurvature, silhouetteIoU } from "../src/metrics/shape";
import {
  distanceToSeeds,
  extractSilhouette,
  silhouetteArea,
  squaredEuclideanDistanceTransform,
  traceContour,
} from "../src/silhouette";
import { alphaMaskImage, discPredicate, maskFromPredicate, rectPredicate, solidLuminance } from "./synthesise";

describe("silhouette extraction", () => {
  it("reads alpha when the capture was taken over transparency", () => {
    const image = alphaMaskImage(20, 20, rectPredicate(5, 5, 14, 14));
    const silhouette = extractSilhouette(image, { kind: "alpha", threshold: 0.5 });
    expect(silhouetteArea(silhouette)).toBe(100);
  });

  it("differences against the background when the capture is an opaque composite", () => {
    // The native case: a screen capture has no alpha, so the silhouette is
    // recovered from the known raster background the harness composited over.
    const background = solidLuminance(20, 20, 0.2);
    const composite = alphaMaskImage(20, 20, () => false);
    const inside = rectPredicate(5, 5, 14, 14);
    const data = new Uint8Array(background.data);
    for (let y = 0; y < 20; y += 1) {
      for (let x = 0; x < 20; x += 1) {
        if (!inside(x, y)) continue;
        const offset = (y * 20 + x) * 4;
        data[offset] = 240;
        data[offset + 1] = 240;
        data[offset + 2] = 240;
      }
    }
    const opaque = { width: 20, height: 20, data };

    const silhouette = extractSilhouette(opaque, {
      kind: "luminance-delta",
      background,
      threshold: 0.05,
    });
    expect(silhouetteArea(silhouette)).toBe(100);
    expect(composite.data[3]).toBe(0);
  });
});

describe("distance transform", () => {
  it("is exact, not an approximation — including on the diagonal", () => {
    // A single seed at the centre of a 9x9 grid: every cell's distance is known
    // in closed form, and a chamfer approximation would be wrong at (3,4).
    const seeds = new Uint8Array(81);
    seeds[4 * 9 + 4] = 1;
    const squared = squaredEuclideanDistanceTransform(seeds, 9, 9);

    expect(squared[4 * 9 + 4]).toBe(0);
    expect(squared[4 * 9 + 7]).toBe(9);
    expect(squared[7 * 9 + 7]).toBe(18);
    expect(squared[0]).toBe(32);

    const distance = distanceToSeeds(seeds, 9, 9);
    expect(distance[7 * 9 + 7]).toBeCloseTo(Math.SQRT2 * 3, 12);
  });
});

describe("silhouetteIoU", () => {
  it("is exactly 1 for identical silhouettes", () => {
    const mask = maskFromPredicate(40, 40, discPredicate(20, 20, 12));
    expect(silhouetteIoU(mask, mask)).toBe(1);
  });

  it("is 0 for disjoint silhouettes", () => {
    const a = maskFromPredicate(40, 20, rectPredicate(0, 0, 9, 19));
    const b = maskFromPredicate(40, 20, rectPredicate(20, 0, 29, 19));
    expect(silhouetteIoU(a, b)).toBe(0);
  });

  it("matches the closed-form value for a known half overlap", () => {
    // 10x10 squares offset by 5: intersection 50, union 150.
    const a = maskFromPredicate(40, 20, rectPredicate(0, 0, 9, 9));
    const b = maskFromPredicate(40, 20, rectPredicate(5, 0, 14, 9));
    expect(silhouetteIoU(a, b)).toBeCloseTo(50 / 150, 12);
  });

  it("refuses to call two empty silhouettes a perfect match", () => {
    const empty = maskFromPredicate(10, 10, () => false);
    expect(() => silhouetteIoU(empty, empty)).toThrowError(CalibrationError);
  });
});

describe("contourDistance", () => {
  it("is zero everywhere for identical silhouettes", () => {
    const mask = maskFromPredicate(60, 60, rectPredicate(10, 10, 49, 49));
    const report = contourDistance(mask, mask);
    expect(report.maxPx).toBe(0);
    expect(report.meanPx).toBe(0);
    expect(report.rmsPx).toBe(0);
  });

  it("recovers a known 3px translation exactly at the max and the p95", () => {
    // A 40x40 square translated 3px in x. The left and right edges are exactly
    // 3px from their counterparts; the top and bottom edges mostly coincide,
    // so the mean must sit strictly between 0 and 3 while the Hausdorff
    // distance is exactly the translation.
    const a = maskFromPredicate(100, 100, rectPredicate(20, 20, 59, 59));
    const b = maskFromPredicate(100, 100, rectPredicate(23, 20, 62, 59));
    const report = contourDistance(a, b);

    expect(report.maxPx).toBeCloseTo(3, 12);
    expect(report.p95Px).toBeCloseTo(3, 12);
    expect(report.meanPx).toBeGreaterThan(0);
    expect(report.meanPx).toBeLessThan(3);
    expect(report.rmsPx).toBeGreaterThan(report.meanPx);
  });

  it("is symmetric, so a uniformly undersized silhouette cannot hide", () => {
    // Concentric squares: the inner contour is 5px inside the outer one all
    // round. A one-sided distance from the *outer* to the inner would still be
    // 5, but a one-sided distance measured the convenient way round on a
    // nested pair is what symmetry exists to rule out.
    const outer = maskFromPredicate(80, 80, rectPredicate(10, 10, 69, 69));
    const inner = maskFromPredicate(80, 80, rectPredicate(15, 15, 64, 64));
    expect(contourDistance(outer, inner).maxPx).toBeCloseTo(contourDistance(inner, outer).maxPx, 12);
    expect(contourDistance(outer, inner).maxPx).toBeCloseTo(Math.hypot(5, 5), 12);
  });
});

describe("contour tracing and curvature", () => {
  it("traces a closed loop whose perimeter matches the rasterised square", () => {
    const square = maskFromPredicate(40, 40, rectPredicate(10, 10, 29, 29));
    const path = traceContour(square);
    // 20x20 square: 76 boundary pixels, unit steps all round.
    expect(path.xs.length).toBe(76);
    expect(path.perimeterPx).toBeCloseTo(76, 6);
    expect(path.xs[0]).toBe(10);
    expect(path.ys[0]).toBe(10);
  });

  it("recovers the curvature of a rasterised circle to within the documented bias", () => {
    // A radius-40 disc has true curvature 0.025 1/px everywhere. The estimator
    // reads ~10% high because the traced boundary sits a fraction of a pixel
    // inside the true circle; nothing here is allowed to drift past that.
    const disc = maskFromPredicate(100, 100, discPredicate(50, 50, 40));
    const profile = contourCurvature(disc);

    let sum = 0;
    let lowest = Number.POSITIVE_INFINITY;
    let highest = 0;
    for (const value of profile.curvature) {
      sum += value;
      lowest = Math.min(lowest, value);
      highest = Math.max(highest, value);
    }
    const mean = sum / profile.curvature.length;

    expect(mean).toBeGreaterThan(0.025 * 0.95);
    expect(mean).toBeLessThan(0.025 * 1.15);
    expect(lowest).toBeGreaterThan(0.025 * 0.35);
    expect(highest).toBeLessThan(0.025 * 1.8);
  });

  it("is four times worse at σ = 1px, which is why the default is 3", () => {
    // The three-point-stencil failure mode, reproduced: at σ = 1px the Gaussian
    // no longer suppresses pixel-frequency staircase noise, and the reported
    // curvature of a radius-40 disc is dominated by it.
    const disc = maskFromPredicate(100, 100, discPredicate(50, 50, 40));
    const noisy = contourCurvature(disc, { smoothingSigmaPx: 1 });
    let sum = 0;
    for (const value of noisy.curvature) sum += value;
    expect(sum / noisy.curvature.length).toBeGreaterThan(0.025 * 3);
  });

  it("keeps the noise floor far below the curvature it has to resolve", () => {
    // The worst case for a rasterised straight edge is 45°, where the staircase
    // puts every sample up to half a pixel off the true line. True curvature
    // there is 0, so whatever the estimator reports is the floor under every
    // corner comparison. An axis-aligned edge is the best case and reports
    // essentially 0, which is why this measures the diagonal instead.
    const wedge = maskFromPredicate(160, 160, (x, y) => x + y <= 150 && x >= 4 && y >= 4);
    const profile = contourCurvature(wedge, { sampleCount: 1024 });

    const sorted = [...profile.curvature].sort((left, right) => left - right);
    const median = sorted[Math.floor(sorted.length * 0.5)] ?? 0;
    const p80 = sorted[Math.floor(sorted.length * 0.8)] ?? 0;
    expect(median).toBeLessThan(0.003);
    expect(p80).toBeLessThan(0.012);
  });

  it("recovers 1/r from the characteristic corner curvature across four radii", () => {
    // The number the axis report carries. Peak curvature rings at the
    // arc-to-straight junction; the corner-region median does not.
    for (const radius of [8, 12, 16, 24]) {
      const shape = maskFromPredicate(140, 140, roundedRect(20, 20, 119, 119, radius));
      const report = cornerCurvature(shape, shape, { sampleCount: 1024 });
      expect(report.cornerCurvaturePerPxA).toBeGreaterThan((1 / radius) * 0.85);
      expect(report.cornerCurvaturePerPxA).toBeLessThan((1 / radius) * 1.15);
    }
  });

  it("reports zero curvature difference against itself", () => {
    const disc = maskFromPredicate(100, 100, discPredicate(50, 50, 30));
    const report = cornerCurvature(disc, disc);
    expect(report.cornerMaxDeltaPerPx).toBe(0);
    expect(report.cornerP95DeltaPerPx).toBe(0);
    expect(report.overallMaxDeltaPerPx).toBe(0);
  });

  it("separates two corner radii that IoU would call nearly identical", () => {
    // This is the failure the axis exists for: a rounded square whose corners
    // are twice as tight as the reference's still overlaps it by ~94%, and the
    // shape axis has to say so through curvature rather than through area.
    const gentle = maskFromPredicate(120, 120, roundedRect(20, 20, 99, 99, 24));
    const tight = maskFromPredicate(120, 120, roundedRect(20, 20, 99, 99, 12));

    expect(silhouetteIoU(gentle, tight)).toBeGreaterThan(0.93);

    const report = cornerCurvature(gentle, tight);
    expect(report.cornerCurvaturePerPxA).toBeLessThan((1 / 24) * 1.15);
    expect(report.cornerCurvaturePerPxB).toBeLessThan((1 / 12) * 1.15);
    // Twice the radius reads as roughly half the curvature.
    expect(report.cornerCurvaturePerPxA / report.cornerCurvaturePerPxB).toBeGreaterThan(0.42);
    expect(report.cornerCurvaturePerPxA / report.cornerCurvaturePerPxB).toBeLessThan(0.6);
    // Two orders of magnitude above the 0.006 1/px raster floor.
    expect(report.cornerMaxDeltaPerPx).toBeGreaterThan(0.02);
  });
});

/** Rasterised rounded rectangle: an analytic rounded-rect region test. */
function roundedRect(
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  radius: number,
): (x: number, y: number) => boolean {
  return (x, y) => {
    if (x < x0 || x > x1 || y < y0 || y > y1) return false;
    const dx = Math.max(x0 + radius - x, 0, x - (x1 - radius));
    const dy = Math.max(y0 + radius - y, 0, y - (y1 - radius));
    return Math.hypot(dx, dy) <= radius;
  };
}
