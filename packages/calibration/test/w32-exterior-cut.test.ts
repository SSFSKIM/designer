/**
 * W32 G0 — the direction-resolved exterior cut's reader, pinned on the two
 * things a later gate leans on and on the one thing that moved (claims §5.166).
 *
 * The reader is
 * `results/2026-09-21-w32-g0-exterior-cut/exterior-cut.py`, W31 G1's
 * `exterior-instrument.py` copied into this gate's directory and extended with
 * the admitted-band rule, the direction resolution, the reach fields and the
 * window-restricted departure. It fits nothing and adopts nothing, so what
 * needs a test is not a bound:
 *
 *   1. **the direction-resolved per-band statistic is the same arithmetic W31
 *      G1 committed.** Its `exterior-instrument.txt` §4 prints `Δa` and `Δc`
 *      per band and per direction on two cells, and those printed numbers are
 *      committed evidence. Transcribed below and asserted against what this
 *      reader computes from the working matrix at the same rows — which is the
 *      only way a *direction*-resolved statistic can be pinned against a
 *      predecessor, since no other artefact in the repository carries one.
 *   2. **the admitted-band rule drops a band whose outer edge is past the
 *      cell's clearance**, and drops it from the statistic rather than from the
 *      record. Two scratch cells differing only in their clearance and their
 *      component make the rule the only thing that could separate them.
 *   3. **the two refusals the adopting gate's guards will rest on** (§5.162 §9,
 *      finding B-1): a holdout row yields no number unless the flag is typed,
 *      and the default `shipped` mode refuses a fabricated document hash.
 *
 * **And one thing case 1 records rather than asserts.** The four SHAPE bands
 * reproduce W31 G1's printed numbers exactly; the `0-3` band does NOT, and the
 * difference is 0.0002–0.0008 in `Δa`. *(Corrected beside, 2026-09-21, review
 * closure; claims §5.166 §10, finding N8: the ten moves run 0.00002 to 0.00092
 * — 0.00002 on `left` of the 2x light cell and 0.00092 on its `above`, which is
 * the largest on both cells. The `< 0.002` bound below is unchanged and is not
 * near either end.)* That is not a discrepancy to reconcile:
 * W31 G1 read the 0.20.0 generation (documents `d0c389d70456` / `880ab1e31450`)
 * and the working file now carries 0.21.0's (`49490eb9ff7a` / `b5714a866288`),
 * W31 G3 having sealed `bodyChromaRetention` into all four macOS 27 documents
 * in between (§5.164). `0-3` is the band that holds the body's own over-fill
 * (§5.62), so a leaf that acts inside the body composite reaches it and reaches
 * nothing further out. The case therefore asserts the shape bands EQUAL and the
 * `0-3` band MOVED — which is a sharper statement than either half alone, and
 * is the corroboration that §5.164's leaf touched no exterior pixel that a
 * shadow statistic reads.
 *
 * Nothing outside the temporary directory is written and no capture is taken.
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
  "2026-09-21-w32-g0-exterior-cut",
  "exterior-cut.py",
);
const WORKING_MATRIX = resolve(PACKAGE_ROOT, "results", "matrix.json");

function run(args: readonly string[], matrix = WORKING_MATRIX): {
  status: number | null;
  output: string;
} {
  const scratch = mkdtempSync(join(tmpdir(), "w32-g0-"));
  const result = spawnSync(
    "python3",
    [READER, "--matrix", matrix, "--out", scratch, ...args],
    { cwd: PACKAGE_ROOT, encoding: "utf8", timeout: 300_000, maxBuffer: 64 * 1024 * 1024 },
  );
  return { status: result.status, output: `${result.stdout ?? ""}${result.stderr ?? ""}` };
}

/**
 * W31 G1's committed `exterior-instrument.txt` §4, transcribed. The columns are
 * the reader's own `all`, `above`, `below`, `left`, `right`; the rows are the
 * axis's five bands in its order. Kept as strings, at the five decimals the
 * reader prints, so the comparison is against what was committed rather than
 * against a re-derivation of it.
 */
const W31_G1_SECTION_4 = {
  "photo__capsule-button__rest 2x light": {
    deltaA: {
      "0-3": [0.01512, 0.06433, -0.01952, 0.0378, -0.10526],
      "3-6": [-0.02873, 0.0, -0.04102, -0.08122, -0.03082],
      "6-12": [-0.01087, 0.0, -0.03325, -0.019, 0.00124],
      "12-24": [-0.00028, 0.0, -0.00263, 0.0, 0.0],
      "24-48": [0.0, 0.0, 0.0, 0.0, 0.0],
    },
    deltaC: {
      "0-3": [0.00312, -0.00275, 0.00372, 0.00521, 0.06607],
      "3-6": [0.00182, 0.0, 0.0009, 0.01065, 0.00623],
      "6-12": [-0.00108, 0.0, -0.00087, 0.00237, -0.00235],
      "12-24": [-0.00005, 0.0, 0.00027, 0.0, 0.0],
      "24-48": [0.0, 0.0, 0.0, 0.0, 0.0],
    },
  },
  "photo__capsule-button__rest 2x dark": {
    deltaA: {
      "0-3": [0.04539, 0.00828, -0.00319, 0.06902, -0.04106],
      "3-6": [-0.01648, 0.0, -0.0225, -0.04935, -0.01738],
      "6-12": [-0.00678, 0.0, -0.02006, -0.01289, 0.00094],
      "12-24": [-0.00019, 0.0, -0.00188, 0.0, 0.0],
      "24-48": [0.0, 0.0, 0.0, 0.0, 0.0],
    },
    deltaC: {
      "0-3": [-0.00646, -0.00076, -0.00263, 0.00021, 0.04136],
      "3-6": [0.00113, 0.0, 0.00057, 0.00655, 0.00334],
      "6-12": [-0.0007, 0.0, -0.00074, 0.00161, -0.00159],
      "12-24": [-0.00002, 0.0, 0.00024, 0.0, 0.0],
      "24-48": [0.0, 0.0, 0.0, 0.0, 0.0],
    },
  },
} as const;

const SHAPE_BANDS = ["3-6", "6-12", "12-24", "24-48"] as const;

/**
 * Pull §4's table for one cell out of the reader's printed output. The block is
 * introduced by the cell's own heading line and holds ten data lines, five
 * labelled `Δa (web−nat)` and five `Δc (web−nat)`.
 */
function sectionFour(output: string, heading: string): {
  deltaA: Record<string, number[]>;
  deltaC: Record<string, number[]>;
} {
  const start = output.indexOf(heading);
  expect(start, `§4 block for ${heading}`).toBeGreaterThan(-1);
  const block = output.slice(start, start + 4000);
  const deltaA: Record<string, number[]> = {};
  const deltaC: Record<string, number[]> = {};
  for (const line of block.split("\n")) {
    const matched = /^\s{4}(\d+-\d+)\s+(.*?)\s+Δ([ac]) \(web−nat\)\s*$/u.exec(line);
    if (matched === null) continue;
    const [, band, figures, which] = matched;
    const values = figures!.trim().split(/\s+/u).map(Number);
    (which === "a" ? deltaA : deltaC)[band!] = values;
    if (Object.keys(deltaA).length === 5 && Object.keys(deltaC).length === 5) break;
  }
  return { deltaA, deltaC };
}

const metric = (value: number, units: string) => ({ value, units });

/**
 * One scratch band pair. The native side transmits everything (`a` = 1) and the
 * web side is displaced by the band's own delta, so the per-band difference is
 * exactly `DELTAS[index]`. The deltas rise outward, which is what makes a
 * reader that admitted the wrong band return a visibly different `T`.
 */
const BANDS = [
  { label: "3-6", inner: 3, outer: 6, width: 3 },
  { label: "6-12", inner: 6, outer: 12, width: 6 },
  { label: "12-24", inner: 12, outer: 24, width: 12 },
  { label: "24-48", inner: 24, outer: 48, width: 24 },
] as const;
const DELTAS = [0.01, 0.02, 0.03, 0.04] as const;

const band = (index: number, side: "native" | "web") => {
  const { label, inner, outer } = BANDS[index]!;
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
 * A scratch cell at a fabricated clearance. `sceneId`'s middle segment is the
 * component, which is how the reader resolves the casting span from
 * `scenes.json`; `rrect-md` is 96 and `rrect-lg` is 160. The clearance is the
 * ONLY thing the two cells below differ in that the admitted-band rule reads.
 */
const cell = (fixtureSet: string, sceneId: string, clearanceCssPx: number) => ({
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
    backdropSupport: metric(1, "ratio"),
    clearanceAbove: metric(clearanceCssPx, "px"),
    clearanceBelow: metric(clearanceCssPx, "px"),
    clearanceLeft: metric(clearanceCssPx, "px"),
    clearanceRight: metric(clearanceCssPx, "px"),
    meanDepartureNative: metric(0.01, "luminance"),
    meanDepartureWeb: metric(0.01, "luminance"),
    falloffSigmaNative: metric(10, "px"),
    falloffSigmaWeb: metric(15, "px"),
    affineNative: BANDS.map((_, index) => band(index, "native")),
    affineWeb: BANDS.map((_, index) => band(index, "web")),
  },
});

function scratchMatrix(cells: readonly unknown[]): string {
  const scratch = mkdtempSync(join(tmpdir(), "w32-g0-matrix-"));
  const matrix = join(scratch, "matrix.json");
  writeFileSync(
    matrix,
    JSON.stringify({ schemaVersion: RESULT_MATRIX_SCHEMA_VERSION, cells }),
  );
  return matrix;
}

const weighted = (widths: readonly number[], deltas: readonly number[]): number =>
  widths.reduce((sum, w, index) => sum + w * deltas[index]!, 0)
  / widths.reduce((sum, w) => sum + w, 0);

describe("W32 G0 — the direction-resolved exterior cut (claims §5.166)", () => {
  it("reproduces W31 G1's §4 shape bands on every direction, and shows `0-3` moved", () => {
    const { status, output } = run([]);
    expect(status, output).toBe(0);

    for (const [label, expected] of Object.entries(W31_G1_SECTION_4)) {
      const [scene, ...bedParts] = label.split(" ");
      const heading = `${scene} — ${bedParts.join(" ")}, span 44`;
      const got = sectionFour(output, heading);

      // The four bands `T` is taken over reproduce W31 G1's committed printout
      // exactly, in all five directions, on both Δa and Δc — 40 numbers per
      // cell. `above` is 0.00000 on every one of them, which is the reading the
      // charter's clause 1 calls "identified one-sidedly".
      for (const bandLabel of SHAPE_BANDS) {
        expect(got.deltaA[bandLabel], `${label} Δa ${bandLabel}`)
          .toEqual(expected.deltaA[bandLabel]);
        expect(got.deltaC[bandLabel], `${label} Δc ${bandLabel}`)
          .toEqual(expected.deltaC[bandLabel]);
      }
      expect(got.deltaA["3-6"]![1], `${label} Δa 3-6 above`).toBe(0);
      expect(got.deltaA["6-12"]![1], `${label} Δa 6-12 above`).toBe(0);

      // And `0-3` did not, because the generation moved: W31 G3 sealed
      // `bodyChromaRetention` into all four macOS 27 documents between the two
      // reads and `0-3` is the band that holds the body's own over-fill. The
      // move is small and is confined to that band, which is the assertion.
      expect(got.deltaA["0-3"], `${label} Δa 0-3`).not.toEqual(expected.deltaA["0-3"]);
      for (const [index, value] of got.deltaA["0-3"]!.entries()) {
        expect(Math.abs(value - expected.deltaA["0-3"]![index]!)).toBeLessThan(0.002);
      }
    }
  });

  it("drops a band whose outer edge is past the cell's own clearance", () => {
    // Two cells, identical in every band they carry. The first has 60 CSS px of
    // clearance, which admits all four bands; the second has 20, which admits
    // `3-6` and `6-12` and leaves `12-24`'s outer edge 4 px outside the frame.
    const matrix = scratchMatrix([
      cell("calibration", "checkerboard__rrect-md__rest", 60),
      cell("calibration", "checkerboard__rrect-lg__rest", 20),
    ]);
    const { status, output } = run(["--at-documents", "any"], matrix);
    expect(status, output).toBe(0);

    // The rule states itself per span before any figure is printed.
    expect(output).toContain("span  96: admitted (all) 3-6/6-12/12-24/24-48");
    expect(output).toContain("span 160: admitted (all) 3-6/6-12    ");

    // Span 96 reads the four-band weighted mean; span 160 reads the two-band
    // one, which is a different number and is the rule's whole effect.
    const four = weighted(BANDS.map((b) => b.width), DELTAS);
    const two = weighted([3, 6], [0.01, 0.02]);
    expect(four).toBeCloseTo(0.0326666, 6);
    expect(two).toBeCloseTo(0.0166666, 6);
    expect(output).toContain(four.toFixed(5));
    expect(output).toContain(two.toFixed(5));

    // §3c holds the two rules side by side on the same cell: W31 G1's
    // renormalisation would have read the four-band number at span 160 too, so
    // the difference between the columns is the admitted-band rule and nothing
    // else.
    const line = output.split("\n").find((l) => /^\s{2}1x light\s+160/u.test(l));
    expect(line, output).toBeDefined();
    expect(line).toContain(four.toFixed(5));
    expect(line).toContain(two.toFixed(5));
  });

  it("yields no number from a holdout row unless the flag is typed", () => {
    const matrix = scratchMatrix([
      cell("calibration", "checkerboard__rrect-md__rest", 60),
      cell("holdout", "photo__rrect-md__rest", 60),
    ]);
    const dropped = run(["--at-documents", "any"], matrix);
    expect(dropped.status, dropped.output).toBe(0);
    expect(dropped.output).toContain("1 holdout row(s)");
    expect(dropped.output).toContain("photo__rrect-md__rest");
    expect(dropped.output).toContain("NOT READ");
    // Not vacuous: the non-holdout row is on a table.
    expect(dropped.output).toContain("0.500 [0.500–0.500] (1)");

    const admitted = run(["--at-documents", "any", "--with-holdout"], matrix);
    expect(admitted.status, admitted.output).toBe(0);
    expect(admitted.output).toContain("--with-holdout: every row of matrix.json is read");
    expect(admitted.output).not.toContain("holdout row(s) in matrix.json and NOT read");
  });

  it("refuses a fabricated document hash in the default `shipped` mode", () => {
    // The guard the adopting gate's `CUT.atDocuments === "shipped"` rests on
    // (§5.162 §9, finding B-1): a row read at a document nobody ships is not
    // the bed a clause is stated over.
    const matrix = scratchMatrix([cell("calibration", "checkerboard__rrect-md__rest", 60)]);
    const { status, output } = run([], matrix);
    expect(status, output).toBe(0);
    expect(output).toContain("0 macOS 27 rows carry a shadow axis");
    expect(output).not.toContain("0.500 [0.500–0.500]");
  });
});
