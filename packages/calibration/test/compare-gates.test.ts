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

import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import {
  colourlessTintEvidence,
  isCaptureFresh,
  matrixSchemaRefusal,
  shouldWriteMatrix,
  type Manifest,
  type SceneSpec,
} from "../cli/gates";
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

describe("colourlessTintEvidence", () => {
  const dirs: string[] = [];
  afterEach(() => {
    for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
  });

  /** A scratch fixtures directory, with `files` written into it as given. */
  function fixturesDir(files: Readonly<Record<string, string>>): string {
    const dir = mkdtempSync(join(tmpdir(), "colourless-tint-"));
    dirs.push(dir);
    for (const [name, contents] of Object.entries(files)) {
      writeFileSync(join(dir, name), contents);
    }
    return dir;
  }

  const EMPTY_SPLIT: SceneSpec["split"] = {
    calibration: [],
    validation: [],
    holdout: [],
    recorded: [],
    probe: [],
  };

  /**
   * `bg__comp__<state>-tint-<tint>`, the same three-segment grammar the real
   * scene matrix uses (`docs/doperpowers/specs`' scenes.json), reduced to the
   * fields the function reads.
   */
  function tintedScene(state: string, tint: "orange" | "blue"): {
    readonly id: string;
    readonly background: string;
    readonly component: string;
    readonly state: string;
    readonly tint: string;
  } {
    return { id: `bg__comp__${state}-tint-${tint}`, background: "bg", component: "comp", state, tint };
  }

  function manifestOf(
    profileKey: string,
    fixtures: readonly { readonly sceneId: string; readonly file: string }[],
  ): Manifest {
    return {
      backgrounds: {},
      caveats: [],
      profiles: [
        {
          profileKey,
          colorScheme: "light",
          a11yMode: "standard",
          fixtures: fixtures.map((f) => ({
            sceneId: f.sceneId,
            file: f.file,
            fixtureSet: "calibration",
            captureMethod: "screen-capture",
            materialRendered: true,
          })),
        },
      ],
    };
  }

  /**
   * FAIL-BEFORE: the recovered inactive bed's own genuine pair — same
   * background/component, `state: "inactive"`, orange and blue fixtures that
   * are byte-identical because the window-recede pose drops hue by design
   * (claims §5.128, "orange and blue give the same inactive level on the
   * checkerboard"). Before this fix, `colourlessTintEvidence` grouped by
   * background/component/state same as it does now but never excluded
   * `inactive`, so this exact pair read as capture corruption and condemned
   * EVERY tinted scene on the profile — active ones included, even though
   * their fixtures actually differ. This test fails against that code: it
   * returns the inactive pair as evidence instead of `undefined`.
   */
  it("does not condemn the tint axis over an inactive pair that is supposed to be colourless", () => {
    const inactiveOrange = tintedScene("inactive", "orange");
    const inactiveBlue = tintedScene("inactive", "blue");
    const restOrange = tintedScene("rest", "orange");
    const restBlue = tintedScene("rest", "blue");

    const spec: SceneSpec = {
      split: EMPTY_SPLIT,
      scenes: [inactiveOrange, inactiveBlue, restOrange, restBlue],
    };
    const dir = fixturesDir({
      "inactive.png": "same-bytes-by-design",
      "rest-orange.png": "orange-really-rendered",
      "rest-blue.png": "blue-really-rendered",
    });
    const manifest = manifestOf("profileA", [
      { sceneId: inactiveOrange.id, file: "inactive.png" },
      { sceneId: inactiveBlue.id, file: "inactive.png" },
      { sceneId: restOrange.id, file: "rest-orange.png" },
      { sceneId: restBlue.id, file: "rest-blue.png" },
    ]);

    expect(colourlessTintEvidence(spec, manifest, dir)).toBeUndefined();
  });

  it("still condemns the axis when an ACTIVE pose's tint pair is byte-identical", () => {
    // The guard this function exists for, unchanged: a `rest` pair that comes
    // back byte-identical is real evidence the capture session dropped the
    // seed, and is still caught with the inactive exemption in place.
    const restOrange = tintedScene("rest", "orange");
    const restBlue = tintedScene("rest", "blue");

    const spec: SceneSpec = { split: EMPTY_SPLIT, scenes: [restOrange, restBlue] };
    const dir = fixturesDir({ "rest.png": "dropped-seed-both-render-untinted" });
    const manifest = manifestOf("profileA", [
      { sceneId: restOrange.id, file: "rest.png" },
      { sceneId: restBlue.id, file: "rest.png" },
    ]);

    const evidence = colourlessTintEvidence(spec, manifest, dir);
    expect(evidence?.profileKey).toBe("profileA");
    expect(evidence?.scenes.slice().sort()).toEqual([restBlue.id, restOrange.id].sort());
  });

  it("clears when every tinted pair, active and inactive alike, actually differs", () => {
    const inactiveOrange = tintedScene("inactive", "orange");
    const inactiveBlue = tintedScene("inactive", "blue");
    const restOrange = tintedScene("rest", "orange");
    const restBlue = tintedScene("rest", "blue");

    const spec: SceneSpec = {
      split: EMPTY_SPLIT,
      scenes: [inactiveOrange, inactiveBlue, restOrange, restBlue],
    };
    const dir = fixturesDir({
      "inactive-orange.png": "inactive-orange-bytes",
      "inactive-blue.png": "inactive-blue-bytes",
      "rest-orange.png": "rest-orange-bytes",
      "rest-blue.png": "rest-blue-bytes",
    });
    const manifest = manifestOf("profileA", [
      { sceneId: inactiveOrange.id, file: "inactive-orange.png" },
      { sceneId: inactiveBlue.id, file: "inactive-blue.png" },
      { sceneId: restOrange.id, file: "rest-orange.png" },
      { sceneId: restBlue.id, file: "rest-blue.png" },
    ]);

    expect(colourlessTintEvidence(spec, manifest, dir)).toBeUndefined();
  });
});
