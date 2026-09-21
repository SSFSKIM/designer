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
  capturePoseRefusal,
  colourlessTintEvidence,
  isCaptureFresh,
  matrixSchemaRefusal,
  shouldWriteMatrix,
  type CaptureReport,
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

  it("refuses a target at an older schema, and says where to write instead", () => {
    // Checked before capture, so the refusal costs nothing but a message.
    const refusal = matrixSchemaRefusal(4, 5, "results/scratch.json");
    expect(refusal).toContain("results/scratch.json");
    expect(refusal).toContain("schema-4");
    expect(refusal).toContain("--out-matrix");
  });

  it("refuses a target from a newer build too, not only an older one", () => {
    expect(matrixSchemaRefusal(6, 5, "results/next.json")).toBeDefined();
  });

  /**
   * What the message SAYS, re-read against what trips it (W31 G2; c9a §5.163
   * §5; the tracker's "A change's 'checked, unchanged' sweep read the imports
   * and not the prose").
   *
   * The refusal used to offer "If that is the frozen inactive-bed matrix, it is
   * meant to stay frozen (wave Decision Log 15 ruling 3)", which described the
   * schema-4/5 interregnum. That ended when the post-W8 pass re-read the bed:
   * the committed matrix is at the schema this build writes, so the default
   * invocation no longer lands here at all and the ruling no longer applies to
   * any file an operator could be holding. The sentence survived the W30 G1
   * closure because that closure's subject was the split and this is user-facing
   * copy — which is exactly the shape of rot the tracker entry names.
   *
   * These two cases are what stops it happening again: the ruling must not be
   * cited, and the three files that DO reach this predicate must be.
   */
  it("does not cite a ruling that stopped applying when the interregnum ended", () => {
    const refusal = matrixSchemaRefusal(4, 5, "results/scratch.json") ?? "";
    expect(refusal).not.toContain("Decision Log 15");
    expect(refusal).not.toContain("frozen inactive-bed");
    expect(refusal).not.toContain("meant to stay frozen");
  });

  it("names what a run that trips it today is actually holding", () => {
    const older = matrixSchemaRefusal(4, 5, "results/scratch.json") ?? "";
    expect(older).toContain("--out-matrix");
    expect(older).toContain("results/superseded/");
    expect(older).toContain("never");
    expect(older).toContain("an older");

    const newer = matrixSchemaRefusal(6, 5, "results/next.json") ?? "";
    expect(newer).toContain("a newer");
  });
});

describe("capturePoseRefusal", () => {
  /** A `report__<renderer>.json` carrying the resolved readouts, or none of them. */
  const report = (page?: {
    windowActivation?: string;
    colorScheme?: string;
    candidateRecededMaterialProfile?: unknown;
  }): CaptureReport => (page === undefined ? {} : { page });

  it("admits an inactive scene whose capture resolved the inactive pose", () => {
    expect(
      capturePoseRefusal(report({ windowActivation: "inactive", colorScheme: "dark" }), "inactive", "dark"),
    ).toBeUndefined();
  });

  it("admits a rest scene whose capture resolved the active pose", () => {
    expect(
      capturePoseRefusal(report({ windowActivation: "active", colorScheme: "light" }), "rest", "light"),
    ).toBeUndefined();
  });

  it("refuses the active material published under the recede's name", () => {
    // The failure the check exists for: the key would carry no trace of it, so
    // this row would read as an inactive fidelity number forever.
    const refusal = capturePoseRefusal(
      report({ windowActivation: "active", colorScheme: "dark" }),
      "inactive",
      "dark",
    );
    expect(refusal).toContain("declared inactive");
    expect(refusal).toContain("resolved 'active'");
  });

  it("refuses a receded capture filed under a scene that is not declared inactive", () => {
    const refusal = capturePoseRefusal(
      report({ windowActivation: "inactive", colorScheme: "light" }),
      "pressed",
      "light",
    );
    expect(refusal).toContain("declared pressed");
    expect(refusal).toContain("resolved 'inactive'");
  });

  it("admits an unlabelled capture for an active-pose scene, because that is all it can be", () => {
    expect(capturePoseRefusal(report(), "rest", "light")).toBeUndefined();
    expect(capturePoseRefusal(report(), "pressed", "dark")).toBeUndefined();
  });

  it("refuses an unlabelled capture for an inactive scene", () => {
    const refusal = capturePoseRefusal(report(), "inactive", "dark");
    expect(refusal).toContain("predates W28 G4");
  });

  it("refuses a capture that drew the other scheme's material", () => {
    const refusal = capturePoseRefusal(
      report({ windowActivation: "active", colorScheme: "light" }),
      "rest",
      "dark",
    );
    expect(refusal).toContain("dark profile");
    expect(refusal).toContain("'light'");
  });

  it("admits an active root under an inactive id when a candidate receded document drew", () => {
    // W29 G3b: the candidate seam pins the root active by construction, because
    // a root that receded itself would apply the SHIPPED difference and the
    // candidate would never draw. The recede is admitted on the evidence that it
    // happened and on nothing else.
    expect(
      capturePoseRefusal(
        report({
          windowActivation: "active",
          colorScheme: "dark",
          candidateRecededMaterialProfile: { tintShadeLight: 1.46 },
        }),
        "inactive",
        "dark",
      ),
    ).toBeUndefined();
  });

  it("still checks the scheme on the candidate path", () => {
    const refusal = capturePoseRefusal(
      report({
        windowActivation: "active",
        colorScheme: "light",
        candidateRecededMaterialProfile: { tintShadeLight: 1.46 },
      }),
      "inactive",
      "dark",
    );
    expect(refusal).toContain("dark profile");
    expect(refusal).toContain("'light'");
  });

  it("does not take a null or non-object candidate as evidence of a recede", () => {
    // `candidateRecededMaterialProfile: null` is what EVERY runtime-posed and
    // active capture writes, so reading it as truthy evidence would open the
    // exception on the whole bed. A scalar or an array is a malformed report and
    // is no better.
    for (const candidate of [null, undefined, 0, "", "yes", [] as unknown]) {
      expect(
        capturePoseRefusal(
          report({
            windowActivation: "active",
            colorScheme: "dark",
            candidateRecededMaterialProfile: candidate,
          }),
          "inactive",
          "dark",
        ),
      ).toContain("resolved 'active'");
    }
  });

  it("does not let a candidate document excuse a capture that resolved neither pose", () => {
    // An unlabelled capture predates the pose readback entirely; a candidate
    // document named beside it cannot say what the root did.
    expect(
      capturePoseRefusal(
        report({ colorScheme: "dark", candidateRecededMaterialProfile: { tintShadeLight: 1.46 } }),
        "inactive",
        "dark",
      ),
    ).toContain("predates W28 G4");
  });

  it("refuses a labelled capture that carries no scheme readback", () => {
    // `windowActivation` present means a post-W28-G4 capture, where the scheme
    // readback is written by the same code path; its absence is a malformed
    // report rather than a legacy one.
    expect(capturePoseRefusal(report({ windowActivation: "active" }), "rest", "light")).toContain(
      "(absent)",
    );
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
