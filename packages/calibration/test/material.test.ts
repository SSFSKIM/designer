import { describe, expect, it } from "vitest";

import { CalibrationError } from "../src/errors";
import {
  blurEdgeSpread,
  fitLuminanceTransfer,
  luminanceTransfer,
  rimIntensity,
  shadowFalloff,
  tintResponse,
} from "../src/metrics/material";
import {
  depthInsideRect,
  distanceOutsideRect,
  fromLinearLuminance,
  fromLinearRgb,
  gaussianStep,
  maskFromPredicate,
  rectPredicate,
  solidLuminance,
} from "./synthesise";

/** A step edge blurred by an exactly-Gaussian kernel of known σ, in linear light. */
function gaussianEdge(sigma: number, low = 0.05, high = 0.9, width = 160, height = 24) {
  return fromLinearLuminance(width, height, (x) => low + (high - low) * gaussianStep(x, width / 2, sigma));
}

describe("blurEdgeSpread", () => {
  it("recovers a known Gaussian σ across an order of magnitude", () => {
    for (const sigma of [1.5, 3, 6, 12]) {
      const report = blurEdgeSpread(gaussianEdge(sigma), { axis: "x" });
      // 8-bit quantisation is the only error source; 2% is comfortably inside it.
      expect(report.sigmaPx).toBeGreaterThan(sigma * 0.98);
      expect(report.sigmaPx).toBeLessThan(sigma * 1.02);
    }
  });

  it("recovers the edge position and the plateaus it was built from", () => {
    const report = blurEdgeSpread(gaussianEdge(4), { axis: "x" });
    expect(report.edgeCentrePx).toBeCloseTo(80, 1);
    expect(report.stepLow).toBeCloseTo(0.05, 2);
    expect(report.stepHigh).toBeCloseTo(0.9, 2);
    expect(report.profileLength).toBe(160);
  });

  it("works on the other axis", () => {
    const vertical = fromLinearLuminance(24, 160, (_x, y) => 0.05 + 0.85 * gaussianStep(y, 80, 5));
    expect(blurEdgeSpread(vertical, { axis: "y" }).sigmaPx).toBeCloseTo(5, 1);
  });

  it("says so through the residual when the kernel is not Gaussian", () => {
    // A 12px box blur has the same second moment as a σ = 3.46px Gaussian, so
    // the σ estimate is meaningful — but the shape is wrong, and the residual
    // is the only thing that reveals it. It has to be an order of magnitude
    // above the Gaussian's for that signal to be usable.
    const gaussian = blurEdgeSpread(gaussianEdge(3.46), { axis: "x" });
    const box = blurEdgeSpread(
      fromLinearLuminance(160, 24, (x) => 0.05 + 0.85 * Math.min(1, Math.max(0, (x - 80) / 12 + 0.5))),
      { axis: "x" },
    );

    expect(gaussian.residualRms).toBeLessThan(0.002);
    expect(box.residualRms).toBeGreaterThan(0.008);
    expect(box.residualRms).toBeGreaterThan(gaussian.residualRms * 10);
  });

  it("refuses a flat region rather than reporting a blur width for it", () => {
    expect(() => blurEdgeSpread(solidLuminance(64, 16, 0.4), { axis: "x" })).toThrowError(CalibrationError);
  });

  it("scopes to a region so one scene can carry several edges", () => {
    // Two edges, σ = 2 at x = 40 and σ = 8 at x = 120. Measuring the whole
    // image would fit one erf to both; the region is what makes each one a
    // measurement.
    const twoEdges = fromLinearLuminance(160, 16, (x) =>
      x < 80 ? 0.05 + 0.6 * gaussianStep(x, 40, 2) : 0.65 - 0.6 * gaussianStep(x, 120, 8),
    );
    expect(blurEdgeSpread(twoEdges, { axis: "x", region: { x: 0, y: 0, width: 80, height: 16 } }).sigmaPx).toBeCloseTo(
      2,
      1,
    );
    expect(
      blurEdgeSpread(twoEdges, { axis: "x", region: { x: 80, y: 0, width: 80, height: 16 } }).sigmaPx,
    ).toBeCloseTo(8, 0);
  });
});

describe("luminanceTransfer", () => {
  const ramp = fromLinearLuminance(120, 40, (x) => 0.02 + (0.88 * x) / 119);

  it("recovers a known slope and offset with r² at 1", () => {
    const rendered = fromLinearLuminance(120, 40, (x) => 0.6 * (0.02 + (0.88 * x) / 119) + 0.1);
    const fit = fitLuminanceTransfer(rendered, ramp);

    expect(fit.slope).toBeCloseTo(0.6, 2);
    expect(fit.offset).toBeCloseTo(0.1, 2);
    expect(fit.r2).toBeGreaterThan(0.9995);
    expect(fit.sampleCount).toBe(120 * 40);
  });

  it("reports both sides and the gap between them", () => {
    const native = fromLinearLuminance(120, 40, (x) => 0.6 * (0.02 + (0.88 * x) / 119) + 0.1);
    const web = fromLinearLuminance(120, 40, (x) => 0.55 * (0.02 + (0.88 * x) / 119) + 0.12);
    const report = luminanceTransfer(native, web, ramp);

    expect(report.native.slope).toBeCloseTo(0.6, 2);
    expect(report.web.slope).toBeCloseTo(0.55, 2);
    expect(report.slopeDelta).toBeCloseTo(-0.05, 2);
    expect(report.offsetDelta).toBeCloseTo(0.02, 2);
  });

  it("separates the glass from the bare backdrop when given a silhouette", () => {
    // Outside the surface the render *is* the backdrop, so an unmasked fit is
    // dragged towards slope 1. The masked fit must recover the real slope.
    const inside = rectPredicate(30, 5, 89, 34);
    const composite = fromLinearLuminance(120, 40, (x, y) => {
      const backdrop = 0.02 + (0.88 * x) / 119;
      return inside(x, y) ? 0.4 * backdrop + 0.2 : backdrop;
    });
    const interior = maskFromPredicate(120, 40, inside);

    expect(fitLuminanceTransfer(composite, ramp).slope).toBeGreaterThan(0.6);
    expect(fitLuminanceTransfer(composite, ramp, { interior }).slope).toBeCloseTo(0.4, 2);
  });

  it("refuses to fit a slope through a constant backdrop", () => {
    const solid = solidLuminance(32, 32, 0.4);
    let caught: unknown;
    try {
      fitLuminanceTransfer(solidLuminance(32, 32, 0.3), solid);
    } catch (error) {
      caught = error;
    }
    expect((caught as CalibrationError).code).toBe("degenerate-fit");
    expect((caught as CalibrationError).message).toMatch(/ramp, photo or checkerboard/);
  });
});

describe("tintResponse", () => {
  const backdrop = fromLinearRgb(60, 60, () => [0.25, 0.25, 0.25]);

  it("is exactly zero when the material adds nothing", () => {
    const report = tintResponse(backdrop, backdrop);
    expect(report.deltaL).toBe(0);
    expect(report.deltaA).toBe(0);
    expect(report.deltaB).toBe(0);
    expect(report.chromaDelta).toBe(0);
  });

  it("reads a blue tint as a negative OKLab b shift with added chroma", () => {
    const inside = rectPredicate(10, 10, 49, 49);
    const tinted = fromLinearRgb(60, 60, (x, y) =>
      inside(x, y) ? [0.25, 0.25, 0.38] : [0.25, 0.25, 0.25],
    );
    const report = tintResponse(tinted, backdrop, { interior: maskFromPredicate(60, 60, inside) });

    expect(report.deltaB).toBeLessThan(-0.02);
    expect(Math.abs(report.deltaA)).toBeLessThan(Math.abs(report.deltaB) / 2);
    expect(report.chromaDelta).toBeGreaterThan(0.02);
    expect(report.backdropChroma).toBeCloseTo(0, 5);
    expect(report.sampleCount).toBe(40 * 40);
  });

  it("averages light before compressing, not after", () => {
    // Half the interior at 0.9 linear and half at 0.01 has the same *mean
    // light* as a flat 0.455, so that is the L it must report — a per-pixel
    // OKLab average would report the much higher mean of the cube roots.
    const small = fromLinearRgb(40, 40, () => [0.25, 0.25, 0.25]);
    const split = fromLinearRgb(40, 40, (x) => (x < 20 ? [0.9, 0.9, 0.9] : [0.01, 0.01, 0.01]));
    const flat = fromLinearRgb(40, 40, () => [0.455, 0.455, 0.455]);

    expect(tintResponse(split, small).interior.L).toBeCloseTo(tintResponse(flat, small).interior.L, 2);
  });
});

describe("rimIntensity", () => {
  // A 60x60 surface whose interior luminance is a Gaussian ridge peaked 4px
  // below the contour, σ = 1.5px. The analytic FWHM is 2*sqrt(2 ln 2)*1.5.
  const x0 = 20;
  const y0 = 20;
  const x1 = 79;
  const y1 = 79;
  const inside = rectPredicate(x0, y0, x1, y1);
  const base = 0.2;
  const amplitude = 0.3;
  const image = fromLinearLuminance(100, 100, (x, y) => {
    if (!inside(x, y)) return 0.05;
    const depth = depthInsideRect(x, y, x0, y0, x1, y1);
    return base + amplitude * Math.exp(-((depth - 4) ** 2) / (2 * 1.5 * 1.5));
  });
  const silhouette = maskFromPredicate(100, 100, inside);

  it("finds the peak at the depth it was built at, with the right height", () => {
    const report = rimIntensity(image, silhouette);
    expect(report.peakDistancePx).toBe(4);
    expect(report.peakLuminance).toBeCloseTo(amplitude, 2);
    expect(report.peakAbsoluteLuminance).toBeCloseTo(base + amplitude, 2);
    expect(report.baselineLuminance).toBeCloseTo(base, 2);
  });

  it("recovers the analytic full width at half maximum", () => {
    const report = rimIntensity(image, silhouette);
    const expected = 2 * Math.sqrt(2 * Math.LN2) * 1.5;
    expect(report.fwhmResolved).toBe(true);
    expect(report.fwhmPx).toBeCloseTo(expected, 1);
  });

  it("flags an unresolved width instead of guessing one", () => {
    // A rim peaked 2px in with a 3px spread has its outward half cut off by the
    // surface's own edge: there is no ring shallower than 1px. The width is
    // then a lower bound, and the flag is how a caller knows that.
    const shallow = fromLinearLuminance(100, 100, (x, y) => {
      if (!inside(x, y)) return 0.05;
      const depth = depthInsideRect(x, y, x0, y0, x1, y1);
      return base + amplitude * Math.exp(-((depth - 2) ** 2) / (2 * 3 * 3));
    });
    const report = rimIntensity(shallow, silhouette);
    expect(report.peakDistancePx).toBe(2);
    expect(report.fwhmResolved).toBe(false);
  });
});

describe("shadowFalloff", () => {
  // An exponential exterior shadow, peak 0.2 at 1px out with a 6px decay
  // length, over a flat 0.5 backdrop.
  const x0 = 20;
  const y0 = 20;
  const x1 = 79;
  const y1 = 79;
  const inside = rectPredicate(x0, y0, x1, y1);
  const backdrop = solidLuminance(100, 100, 0.5);
  const image = fromLinearLuminance(100, 100, (x, y) => {
    if (inside(x, y)) return 0.7;
    return 0.5 - 0.2 * Math.exp(-distanceOutsideRect(x, y, x0, y0, x1, y1) / 6);
  });
  const silhouette = maskFromPredicate(100, 100, inside);

  it("recovers the decay length it was built with", () => {
    const report = shadowFalloff(image, silhouette, backdrop);
    expect(report.peakDistancePx).toBe(1);
    expect(report.peakDarkening).toBeCloseTo(0.2 * Math.exp(-1 / 6), 2);
    expect(report.decayResolved).toBe(true);
    expect(report.decayLengthPx).toBeGreaterThan(5.5);
    expect(report.decayLengthPx).toBeLessThan(6.5);
  });

  it("reports zero darkening for a surface that casts no shadow", () => {
    const flat = fromLinearLuminance(100, 100, (x, y) => (inside(x, y) ? 0.7 : 0.5));
    const report = shadowFalloff(flat, silhouette, backdrop);
    expect(Math.abs(report.peakDarkening)).toBeLessThan(0.005);
  });

  it("flags a shadow wider than the window rather than truncating it silently", () => {
    const report = shadowFalloff(image, silhouette, backdrop, { maxDistancePx: 4 });
    expect(report.decayResolved).toBe(false);
  });
});
