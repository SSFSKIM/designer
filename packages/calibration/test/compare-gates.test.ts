/**
 * The `compare` orchestrator's two self-checks.
 *
 * Both exist because the CLI's failure mode is not a crash — it is a
 * `results/matrix.json` that reads as evidence and is not one. Neither condition
 * is reachable from a unit test through the CLI itself (one needs a GPU that
 * refuses WebGPU, the other a browser capture), so the decisions are pure
 * functions and this is where they are pinned.
 */

import { describe, expect, it } from "vitest";

import { isCaptureFresh, shouldWriteMatrix } from "../cli/gates";

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
