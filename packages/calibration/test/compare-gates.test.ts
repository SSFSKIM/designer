/**
 * The `compare` orchestrator's self-checks.
 *
 * They exist because the CLI's failure mode is not a crash — it is a
 * `results/matrix.json` that reads as evidence and is not one, or an hour of
 * capture spent on a target that was never writable. None of the conditions is
 * reachable from a unit test through the CLI itself (one needs a GPU that
 * refuses WebGPU, another a browser capture), so the decisions are pure
 * functions and this is where they are pinned.
 */

import { describe, expect, it } from "vitest";

import { isCaptureFresh, matrixSchemaRefusal, shouldWriteMatrix } from "../cli/gates";
import { RESULT_MATRIX_SCHEMA_VERSION } from "../src/report";

describe("isCaptureFresh", () => {
  it("rejects an artifact left by an earlier run", () => {
    const runStartedAt = Date.parse("2026-08-26T12:00:00Z");
    const anHourEarlier = runStartedAt - 3_600_000;
    expect(isCaptureFresh(anHourEarlier, runStartedAt)).toBe(false);
  });

  it("accepts an artifact written during the run", () => {
    const runStartedAt = Date.parse("2026-08-26T12:00:00Z");
    expect(isCaptureFresh(runStartedAt + 12_000, runStartedAt)).toBe(true);
  });

  it("tolerates a whole-second mtime truncated below the run's start", () => {
    // A filesystem storing mtime to the second reports 12:00:00.000 for a file
    // written at 12:00:00.600 — after a run that started at 12:00:00.400.
    const runStartedAt = Date.parse("2026-08-26T12:00:00Z") + 400;
    const truncated = Date.parse("2026-08-26T12:00:00Z");
    expect(isCaptureFresh(truncated, runStartedAt)).toBe(true);
  });
});

describe("shouldWriteMatrix", () => {
  it("writes a run with no failures", () => {
    expect(shouldWriteMatrix(0, false)).toBe(true);
  });

  it("refuses to write a run with holes in it", () => {
    expect(shouldWriteMatrix(1, false)).toBe(false);
  });

  it("writes a run with holes only when asked explicitly", () => {
    expect(shouldWriteMatrix(1, true)).toBe(true);
  });
});

describe("matrixSchemaRefusal", () => {
  it("permits a target this build wrote", () => {
    expect(
      matrixSchemaRefusal(RESULT_MATRIX_SCHEMA_VERSION, RESULT_MATRIX_SCHEMA_VERSION, "results/x.json"),
    ).toBeUndefined();
  });

  it("refuses the frozen inactive-bed matrix by name, and says where to write instead", () => {
    // The interregnum case, and the one a default invocation lands on: the
    // committed matrix is schema 4 by ruling, this build writes 5. Checked
    // before capture, so the refusal costs nothing but a message.
    const refusal = matrixSchemaRefusal(4, 5, "results/matrix.json");
    expect(refusal).toContain("results/matrix.json");
    expect(refusal).toContain("schema-4");
    expect(refusal).toContain("--out-matrix");
  });

  it("refuses a target from a newer build too, not only an older one", () => {
    expect(matrixSchemaRefusal(6, 5, "results/next.json")).toBeDefined();
  });
});
