/**
 * W31 G1 — the exterior-width instrument's reader, exercised on a scratch
 * matrix with a known answer (claims §5.162).
 *
 * The reader is
 * `results/2026-09-21-w31-g1-exterior-instrument/exterior-instrument.py`. It is
 * a cut of committed evidence and adopts nothing, so what needs a test is not a
 * bound but the two properties a later wave will lean on when it reads a clause
 * off it:
 *
 *   1. **the statistics are the arithmetic they are declared to be.** `T` is a
 *      width-weighted mean of four per-band transmission differences, and the
 *      weights are the bands' widths in CSS px — 3, 6, 12 and 24 — so a matrix
 *      whose bands differ by 0.01, 0.02, 0.03 and 0.04 has one right answer and
 *      this case states it in full rather than re-deriving it from the script.
 *      Candidate (i) is the same for `|σ_web − σ_native| / σ_native` in CSS px;
 *   2. **a holdout row yields no number without the flag.** The reader drops the
 *      holdout in `cells()`, which is `fit.py`'s idiom and the contract claims
 *      §5.156 §4 records — the drop lives in the one function every table takes
 *      its rows from, so that a mistyped selection cannot undo it. A test that
 *      only checked the passing half would pass on a reader that printed
 *      nothing, so the scratch matrix carries one holdout row and one
 *      non-holdout row and the case asserts both directions on both.
 *
 * The scratch matrix is built here rather than sampled from the bed, for the
 * reason the known answer exists at all: a case read off `results/matrix.json`
 * would re-state whatever the script computed, and the arithmetic is what is
 * being pinned. Nothing outside the temporary directory is written and no
 * capture is taken.
 */
import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { RESULT_MATRIX_SCHEMA_VERSION } from "../src/report";

const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
const READER = resolve(
  PACKAGE_ROOT,
  "results",
  "2026-09-21-w31-g1-exterior-instrument",
  "exterior-instrument.py",
);

/** The bands `T` is taken over, with the width that is each one's weight. */
const SHAPE_BANDS = [
  { label: "3-6", inner: 3, outer: 6, width: 3 },
  { label: "6-12", inner: 6, outer: 12, width: 6 },
  { label: "12-24", inner: 12, outer: 24, width: 12 },
  { label: "24-48", inner: 24, outer: 48, width: 24 },
] as const;

/**
 * The transmission differences the scratch cell carries, one per band, in the
 * bands' own order. Chosen to rise outward so that a reader which weighted by
 * band COUNT rather than by band WIDTH would return a visibly different number
 * (0.02500 against 0.03267) instead of agreeing by accident.
 */
const DELTAS = [0.01, 0.02, 0.03, 0.04] as const;

const metric = (value: number, units: string) => ({ value, units });

const band = (index: number, side: "native" | "web") => {
  const { label, inner, outer } = SHAPE_BANDS[index]!;
  // `a` on the native side is 1 (a band that removes nothing); the web side is
  // displaced by the band's own delta, so the difference is exactly DELTAS[i].
  // The backdrop's standard deviation is well clear of the axis's 0.02 floor,
  // which is what makes the pair identifiable at all.
  return {
    direction: "all",
    ringLabel: label,
    innerDistanceCssPx: inner,
    outerDistanceCssPx: outer,
    sampleCount: 4096,
    backdropMeanLinear: 0.5,
    backdropStdDevLinear: 0.5,
    renderedLevelLinear: 0.5,
    slopeALinear: side === "native" ? 1 : 1 - DELTAS[index]!,
    interceptCLinear: 0,
    rSquared: 0.999,
  };
};

/**
 * One scratch cell. `sceneId`'s middle segment is the component, which is how
 * the reader resolves the casting span from `scenes.json` — `rrect-md` is 96.
 * The `capturePath` names a profile document and a hash; the tests below run
 * the reader with `--at-documents any`, which is the mode a superseded
 * generation is read in and the mode a scratch matrix needs, and one case
 * asserts that the default `shipped` mode refuses this fabricated hash.
 */
const cell = (fixtureSet: string, sceneId: string) => ({
  key: {
    profileKey: "apple-macos-27.0-1x-light-standard-glass0.5",
    sceneId,
    web: {
      engine: "chromium",
      renderer: "webgpu",
      samplingBackend: "gpu-texture",
      capturePath:
        "scratch, materialProfile=packages/calibration/profiles/scratch.json "
        + "sha256:000000000000",
      sceneId,
      pixelSize: [320, 200],
      deterministic: true,
      repeatNoise: 0,
    },
  },
  fixtureSet,
  state: "rest",
  tier: "texture",
  capturedAt: "2026-09-21T00:00:00.000Z",
  shadow: {
    axis: "shadow",
    exteriorArea: metric(40_000, "px^2"),
    backdropMeanLuminance: metric(0.5, "luminance"),
    // Clear of the axis's own `DEFAULT_MIN_BACKDROP_SUPPORT`, so the cell is a
    // backdrop a transmission can be measured over.
    backdropSupport: metric(1, "ratio"),
    clearanceAbove: metric(60, "px"),
    clearanceBelow: metric(60, "px"),
    clearanceLeft: metric(60, "px"),
    clearanceRight: metric(60, "px"),
    meanDepartureNative: metric(0.01, "luminance"),
    meanDepartureWeb: metric(0.01, "luminance"),
    falloffSigmaNative: metric(10, "px"),
    falloffSigmaWeb: metric(15, "px"),
    affineNative: SHAPE_BANDS.map((_, index) => band(index, "native")),
    affineWeb: SHAPE_BANDS.map((_, index) => band(index, "web")),
  },
});

function run(args: readonly string[]): { status: number | null; output: string } {
  const scratch = mkdtempSync(join(tmpdir(), "w31-g1-"));
  const matrix = join(scratch, "matrix.json");
  writeFileSync(
    matrix,
    JSON.stringify({
      schemaVersion: RESULT_MATRIX_SCHEMA_VERSION,
      cells: [
        cell("calibration", "checkerboard__rrect-md__rest"),
        cell("holdout", "photo__rrect-md__rest"),
      ],
    }),
  );
  const result = spawnSync(
    "python3",
    [READER, "--matrix", matrix, "--out", scratch, ...args],
    { cwd: PACKAGE_ROOT, encoding: "utf8", timeout: 120_000 },
  );
  return { status: result.status, output: `${result.stdout ?? ""}${result.stderr ?? ""}` };
}

describe("W31 G1 — the exterior instrument's reader (claims §5.162)", () => {
  it("computes both statistics to their declared arithmetic", () => {
    const { status, output } = run(["--at-documents", "any"]);
    expect(status, output).toBe(0);

    // Candidate (i): |15 − 10| / 10 at scale 1, so 0.500 in CSS px as well as in
    // device px — the relative error is what the scale divides out of.
    expect(output).toContain("0.500 [0.500–0.500] (1)");

    // Candidate (ii): Σ w·|Δa| / Σ w over the four bands, weights 3, 6, 12, 24.
    const weights = SHAPE_BANDS.map((b) => b.width);
    const expected =
      weights.reduce((sum, w, index) => sum + w * DELTAS[index]!, 0)
      / weights.reduce((sum, w) => sum + w, 0);
    expect(expected).toBeCloseTo(0.0326666, 6);
    expect(output).toContain(`${expected.toFixed(5)} [${expected.toFixed(5)}`);

    // And the weighting is the load-bearing part: an unweighted mean of the same
    // four differences is 0.025, which must NOT be what the reader printed.
    const unweighted = DELTAS.reduce((sum, d) => sum + d, 0) / DELTAS.length;
    expect(unweighted).toBeCloseTo(0.025, 6);
    expect(output).not.toContain(unweighted.toFixed(5));
  });

  it("yields no number from a holdout row without the flag, and names what it refused", () => {
    const { status, output } = run(["--at-documents", "any"]);
    expect(status, output).toBe(0);

    // The drop notice is present, carries the count, and names the scene it
    // refused — naming a refusal is the opposite of reading it.
    expect(output).toContain("1 holdout row(s)");
    expect(output).toContain("photo__rrect-md__rest");

    // No table line carries the holdout row's own class, and the block that
    // would print the seven missed rows says it did not.
    expect(output).not.toContain("holdout   ");
    expect(output).toContain("NOT READ");

    // The check cannot pass by the reader having printed nothing: the
    // non-holdout row is on a table.
    expect(output).toContain("0.500 [0.500–0.500] (1)");
  });

  it("admits the holdout row when the flag is typed, which is what makes the drop a choice", () => {
    const { status, output } = run(["--at-documents", "any", "--with-holdout"]);
    expect(status, output).toBe(0);
    expect(output).toContain("--with-holdout: every row of matrix.json is read");
    expect(output).not.toContain("holdout row(s) in matrix.json and NOT read");
    // Two rows now, on one table line each — the holdout row's class appears,
    // on a line that also carries the reading (the spans between are empty).
    expect(output).toMatch(/holdout[^\n]*0\.500 \[0\.500–0\.500] \(1\)/);
  });

  it("refuses a fabricated document hash in the default `shipped` mode", () => {
    // `atAShippedDocument` is what keeps a row read at a document nobody ships
    // out of every table (claims §5.156; `departure-stat.py`). The scratch
    // matrix names `sha256:000000000000`, so the default mode must read nothing
    // from it rather than read it anyway.
    const { status, output } = run([]);
    expect(status, output).toBe(0);
    expect(output).toContain("0 macOS 27 rows carry a shadow axis");
    expect(output).not.toContain("0.500 [0.500–0.500]");
  });
});
