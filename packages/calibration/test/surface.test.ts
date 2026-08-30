import { describe, expect, it } from "vitest";

import * as calibration from "../src/index";

/**
 * The barrel is what the CLI and C9 import, so what it exposes is a contract.
 * C1's four declarations in particular must survive every reorganisation of the
 * files underneath — they are what fixtures and fidelity claims cite.
 */
describe("package surface", () => {
  it("still exports C1's X9 vocabulary", () => {
    expect(calibration.METRIC_AXES).toEqual(["shape", "material", "motion", "perceptual"]);
    expect(calibration.FIXTURE_SETS).toEqual(["calibration", "validation", "holdout"]);
    expect(calibration.PROFILE_KEY_PATTERN.test("apple-macos-26.5-2x-light-standard")).toBe(true);
    expect(calibration.parseProfileKey("apple-ios-26.5-3x-dark-increased-contrast")?.scale).toBe(3);
  });

  it("exports one entry point per axis, plus the substrate and the report schema", () => {
    for (const name of [
      // Substrate.
      "decodePng",
      "assertComparable",
      "srgbByteToLinear",
      "linearRgbToOklab",
      "extractSilhouette",
      "squaredEuclideanDistanceTransform",
      "aggregate",
      "CalibrationError",
      // The declared geometry the instrument bounds its search to (schema 5).
      "placeComponent",
      "componentRegion",
      "DEFAULT_COMPONENT_REGION_MARGIN_PX",
      // Axes.
      "silhouetteIoU",
      "contourDistance",
      "cornerCurvature",
      "blurEdgeSpread",
      "luminanceTransfer",
      "tintResponse",
      "rimIntensity",
      "shadowFalloff",
      "shadowField",
      "edgeWeightedDifference",
      "ssim",
      "oklabDeltaE",
      "morphSilhouetteTrajectory",
      // Report schema.
      "resultCellKey",
      "serializeResultCellKey",
      "createResultMatrix",
      "upsertCellResult",
      "serializeResultMatrix",
      "deserializeResultMatrix",
      "shapeAxisReport",
      "materialAxisReport",
      "perceptualAxisReport",
      "motionAxisReport",
      "shadowAxisReport",
      "coherenceAxisReport",
    ]) {
      expect(calibration, name).toHaveProperty(name);
    }
  });

  it("exposes no callable stub for a metric C9 owns", () => {
    // The five timing metrics exist as types only. A function that exists and
    // always throws reads as a capability in an editor's completions, and C9
    // finding out at runtime is worse than not finding it at all.
    for (const name of ["responseLatency", "peakCompression", "overshoot", "settlingTime", "redirectContinuity"]) {
      expect(calibration).not.toHaveProperty(name);
    }
  });
});
