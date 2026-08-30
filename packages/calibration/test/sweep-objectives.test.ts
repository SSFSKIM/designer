/**
 * The sweep's two objectives, and the guard that used to conflate them.
 *
 * `score()` refuses an empty set rather than scoring it as zero — a cell that
 * cannot measure the material must not look like one that measures it perfectly.
 * That refusal was unconditional, which made a legitimate run impossible: over a
 * solid backdrop of the material's own tone the native silhouette is empty, so
 * `cli/measure.ts` records the cell with NO material axis while its exterior
 * metrics are present and correct. A shadow-objective sweep scoped to such cells
 * computed its objective and then threw it away on the interior objective's
 * guard. Found by review of the recalibration cascade's refit, 2026-08-31.
 */

import { describe, expect, it } from "vitest";

import { score } from "../scripts/sweep";
import {
  createResultMatrix,
  serializeResultMatrix,
  upsertCellResult,
  type CellResult,
} from "../src/index";

const metric = (value: number, units: string) => ({ value, units });

/** A dark-solid-shaped cell: a shadow axis, and no material axis at all. */
const shadowOnlyCell = (sceneId: string, native: number, web: number): CellResult =>
  ({
    key: {
      profileKey: "apple-macos-26.5-1x-light-standard",
      sceneId,
      web: {
        engine: "chromium",
        engineVersion: "0",
        renderer: "webgpu",
        samplingBackend: "gpu-texture",
        gpuAdapter: "apple/metal-3",
        colorSpace: "srgb",
        capturePath: "synthetic",
        sceneId,
        pixelSize: [320, 200],
        deterministic: true,
        repeatNoise: 0,
      },
    },
    fixtureSet: "calibration",
    tier: "texture",
    capturedAt: "2026-08-31T00:00:00.000Z",
    shadow: {
      axis: "shadow",
      meanDepartureNative: metric(native, "luminance"),
      meanDepartureWeb: metric(web, "luminance"),
    },
  }) as unknown as CellResult;

const matrixOf = (...cells: readonly CellResult[]): string => {
  let matrix = createResultMatrix();
  for (const cell of cells) matrix = upsertCellResult(matrix, cell);
  return serializeResultMatrix(matrix);
};

describe("the sweep's objective guards", () => {
  it("ranks a shadow-only sweep, where every cell lacks a material axis", () => {
    const json = matrixOf(
      shadowOnlyCell("dark-solid__capsule-button__rest", 0.02, 0.05),
      shadowOnlyCell("dark-solid__rrect-md__rest", 0.04, 0.03),
    );

    const scored = score(json, "shadow");

    // |0.05 − 0.02| and |0.03 − 0.04|, averaged: the objective is defined and finite.
    expect(scored.shadowCells).toBe(2);
    expect(scored.shadow).toBeCloseTo((0.03 + 0.01) / 2, 12);
    // And the interior objective is absent rather than zero, so it cannot be
    // mistaken for a perfect score by anything reading the same record.
    expect(scored.cells).toBe(0);
    expect(Number.isNaN(scored.objective)).toBe(true);
  });

  it("still refuses an INTERIOR sweep over the same cells, and says which flag to pass", () => {
    const json = matrixOf(shadowOnlyCell("dark-solid__capsule-button__rest", 0.02, 0.05));

    expect(() => score(json, "interior")).toThrow(/--objective shadow/);
  });

  it("refuses a shadow sweep with no shadow axis, on the same rule", () => {
    // The mirror of the case above: neither objective may be scored over nothing.
    const bare = { ...shadowOnlyCell("photo__capsule-button__rest", 0, 0) } as Record<string, unknown>;
    delete bare["shadow"];
    expect(() => score(matrixOf(bare as unknown as CellResult), "shadow")).toThrow(/shadow axis/);
  });
});
