import { describe, expect, it } from "vitest";

import { CalibrationError } from "../src/errors";
import {
  createResultMatrix,
  deserializeResultMatrix,
  getCellResult,
  listCellResults,
  metricValue,
  motionAxisReport,
  perceptualAxisReport,
  RESULT_MATRIX_SCHEMA_VERSION,
  resultCellKey,
  serializeResultCellKey,
  serializeResultMatrix,
  shapeAxisReport,
  upsertCellResult,
  type CellResult,
  type ResultCellKey,
  type WebCell,
} from "../src/report";

const chromiumGpu: WebCell = {
  engine: "chromium",
  engineVersion: "141.0.7390.54",
  renderer: "webgpu",
  samplingBackend: "element-capture",
  gpuAdapter: "apple-m-series",
  colorSpace: "srgb",
  capturePath: "playwright-screenshot",
};

const chromiumCss: WebCell = { ...chromiumGpu, renderer: "css", samplingBackend: "backdrop-filter" };

const profile = "apple-macos-26.5-2x-light-standard";

function cell(key: ResultCellKey, overrides: Partial<CellResult> = {}): CellResult {
  return {
    key,
    fixtureSet: "calibration",
    tier: "texture",
    capturedAt: "2026-08-25T09:00:00.000Z",
    shape: shapeAxisReport({
      silhouetteAreaNative: 4865,
      silhouetteAreaWeb: 4871,
      componentRegionArea: 4872,
      componentRegionMarginPx: 0,
      silhouetteHolesNative: 0,
      silhouetteHolesWeb: 0,
      silhouetteBodiesNative: 1,
      silhouetteBodiesWeb: 1,
      componentRegionBodies: 1,
      silhouetteIoU: 0.9987,
      contourDistance: { maxPx: 1.41, p95Px: 1, meanPx: 0.32, rmsPx: 0.51, sampleCount: 812 },
      cornerCurvature: {
        cornerMaxDeltaPerPx: 0.011,
        cornerP95DeltaPerPx: 0.007,
        overallMaxDeltaPerPx: 0.014,
        overallP95DeltaPerPx: 0.009,
        cornerCurvaturePerPxA: 0.0625,
        cornerCurvaturePerPxB: 0.0611,
        peakCurvaturePerPxA: 0.088,
        peakCurvaturePerPxB: 0.086,
        cornerSampleCount: 210,
        sampleCount: 512,
        smoothingSigmaPx: 3,
        perimeterPxA: 421.2,
        perimeterPxB: 420.8,
      },
    }),
    ...overrides,
  };
}

describe("cell keys (X9)", () => {
  it("refuses a key whose profile does not match the X9 grammar", () => {
    let caught: unknown;
    try {
      resultCellKey("apple-macos-26.5-2x-light", chromiumGpu, "impulse-toolbar-rest");
    } catch (error) {
      caught = error;
    }
    expect((caught as CalibrationError).code).toBe("invalid-profile-key");
  });

  it("serialises deterministically", () => {
    const key = resultCellKey(profile, chromiumGpu, "impulse-toolbar-rest");
    expect(serializeResultCellKey(key)).toBe(serializeResultCellKey({ ...key }));
    expect(serializeResultCellKey(key)).toBe(
      "apple-macos-26.5-2x-light-standard|impulse-toolbar-rest|chromium|141.0.7390.54|webgpu|element-capture|apple-m-series|srgb|playwright-screenshot",
    );
  });

  it("distinguishes cells that differ in any single web-cell field", () => {
    const base = resultCellKey(profile, chromiumGpu, "scene");
    const variants: ResultCellKey[] = [
      resultCellKey(profile, { ...chromiumGpu, engine: "gecko" }, "scene"),
      resultCellKey(profile, { ...chromiumGpu, engineVersion: "142.0.0.0" }, "scene"),
      resultCellKey(profile, { ...chromiumGpu, renderer: "css" }, "scene"),
      resultCellKey(profile, { ...chromiumGpu, samplingBackend: "dom-hybrid" }, "scene"),
      resultCellKey(profile, { ...chromiumGpu, gpuAdapter: "software" }, "scene"),
      resultCellKey(profile, { ...chromiumGpu, capturePath: "screencapture" }, "scene"),
      resultCellKey("apple-macos-26.5-3x-light-standard", chromiumGpu, "scene"),
      resultCellKey(profile, chromiumGpu, "other-scene"),
    ];
    const keys = new Set([serializeResultCellKey(base), ...variants.map(serializeResultCellKey)]);
    expect(keys.size).toBe(variants.length + 1);
  });

  it("escapes its separator so no field can forge a collision", () => {
    const a = resultCellKey(profile, { ...chromiumGpu, gpuAdapter: "a|b" }, "c");
    const b = resultCellKey(profile, { ...chromiumGpu, gpuAdapter: "a" }, "b|c");
    expect(serializeResultCellKey(a)).not.toBe(serializeResultCellKey(b));
  });
});

describe("result matrix", () => {
  it("upserts by key, replacing rather than merging", () => {
    const key = resultCellKey(profile, chromiumGpu, "scene");
    const first = cell(key);
    const second: CellResult = { ...cell(key), capturedAt: "2026-08-26T09:00:00.000Z", fixtureSet: "holdout" };

    const matrix = upsertCellResult(upsertCellResult(createResultMatrix(), first), second);
    expect(matrix.cells.size).toBe(1);
    expect(getCellResult(matrix, key)?.capturedAt).toBe("2026-08-26T09:00:00.000Z");
    expect(getCellResult(matrix, key)?.fixtureSet).toBe("holdout");
  });

  it("keeps the same scene under two web cells apart", () => {
    // X9's whole point: the same build measured through two renderers is two
    // results, not one overwriting the other.
    const gpu = resultCellKey(profile, chromiumGpu, "scene");
    const css = resultCellKey(profile, chromiumCss, "scene");
    const matrix = upsertCellResult(upsertCellResult(createResultMatrix(), cell(gpu)), {
      ...cell(css),
      tier: "dom",
    });

    expect(matrix.cells.size).toBe(2);
    expect(getCellResult(matrix, gpu)?.tier).toBe("texture");
    expect(getCellResult(matrix, css)?.tier).toBe("dom");
  });

  it("does not mutate the matrix it was given", () => {
    const original = createResultMatrix();
    upsertCellResult(original, cell(resultCellKey(profile, chromiumGpu, "scene")));
    expect(original.cells.size).toBe(0);
  });

  it("round-trips through JSON losslessly, including absent axes", () => {
    const withMotion: CellResult = {
      ...cell(resultCellKey(profile, chromiumGpu, "morph-button-to-menu")),
      motion: motionAxisReport({
        morph: {
          frameCount: 12,
          frameTimeDeltaMaxMs: 0.5,
          centroidDistancePx: { count: 12, min: 0.1, max: 1.9, mean: 0.7, p95: 1.7, rms: 0.9 },
          areaRatio: { count: 12, min: 0.97, max: 1.03, mean: 1.0, p95: 1.02, rms: 1.0 },
          boundsDeltaPx: { count: 12, min: 0, max: 2, mean: 0.8, p95: 1.8, rms: 1.1 },
          silhouetteIoU: { count: 12, min: 0.94, max: 1, mean: 0.98, p95: 1, rms: 0.98 },
        },
      }),
      perceptual: perceptualAxisReport({
        edgeWeighted: { weightedMean: 0.004, weightedP95: 0.02, unweightedMean: 0.002, edgeGain: 4, sampleCount: 1 },
        ssim: { mean: 0.982, min: 0.71, windowCount: 4000 },
        oklabDeltaE: { mean: 0.012, p95: 0.04, max: 0.09, sampleCount: 1 },
      }),
    };
    const plain = cell(resultCellKey(profile, chromiumCss, "impulse-toolbar-rest"));

    const matrix = upsertCellResult(upsertCellResult(createResultMatrix(), withMotion), plain);
    const restored = deserializeResultMatrix(serializeResultMatrix(matrix));

    expect(listCellResults(restored)).toEqual(listCellResults(matrix));
    // Absent stays absent: a cell with no motion axis must not gain one.
    expect(getCellResult(restored, plain.key)).not.toHaveProperty("motion");
    expect(getCellResult(restored, withMotion.key)?.motion?.morphSilhouetteIoUMin).toEqual(
      metricValue(0.94, "ratio"),
    );
    // And C9's timing metrics stay absent rather than arriving as zeros.
    expect(getCellResult(restored, withMotion.key)?.motion).not.toHaveProperty("responseLatency");
  });

  it("serialises in a stable key order so a committed matrix diffs cleanly", () => {
    const keys = ["c-scene", "a-scene", "b-scene"].map((scene) => resultCellKey(profile, chromiumGpu, scene));
    const forward = keys.reduce((matrix, key) => upsertCellResult(matrix, cell(key)), createResultMatrix());
    const backward = [...keys]
      .reverse()
      .reduce((matrix, key) => upsertCellResult(matrix, cell(key)), createResultMatrix());

    expect(serializeResultMatrix(forward)).toBe(serializeResultMatrix(backward));
    expect(listCellResults(forward).map((result) => result.key.sceneId)).toEqual(["a-scene", "b-scene", "c-scene"]);
  });

  it("refuses a file that is not a result matrix", () => {
    expect(() => deserializeResultMatrix("not json")).toThrowError(CalibrationError);
    expect(() => deserializeResultMatrix('{"cells":[]}')).toThrowError(/schemaVersion/);
    // Derived from the constant rather than restated: the bump on a schema change
    // is the point, and a test that hardcodes the old number turns an intended
    // bump into a failure that says nothing about the shape it guards.
    expect(() => deserializeResultMatrix('{"schemaVersion":99,"cells":[]}')).toThrowError(
      new RegExp(`this build writes ${RESULT_MATRIX_SCHEMA_VERSION}`),
    );
    const current = `"schemaVersion":${RESULT_MATRIX_SCHEMA_VERSION}`;
    expect(() => deserializeResultMatrix(`{${current},"cells":{}}`)).toThrowError(/not an array/);
    expect(() => deserializeResultMatrix(`{${current},"cells":[{}]}`)).toThrowError(/well-formed key/);
    // And a matrix written by the previous schema is refused rather than coerced.
    expect(() => deserializeResultMatrix('{"schemaVersion":1,"cells":[]}')).toThrowError(/schemaVersion 1/);
  });
});
