/** Native-only G0b evidence and the ruled stop, c9a §5.182. */
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";

const here = resolve(import.meta.dirname, "../results/2026-09-25-w37-g0b-edge-identification");
const read = (name: string) => {
  const bytes = readFileSync(resolve(here, name));
  return JSON.parse((name.endsWith(".gz") ? gunzipSync(bytes) : bytes).toString());
};
const python = (name: string, args: string[] = []) => spawnSync(
  "python3.12", [resolve(here, name), ...args], {
    encoding: "utf8", maxBuffer: 16 * 1024 * 1024,
    env: { ...process.env, OPENBLAS_NUM_THREADS: "1", VECLIB_MAXIMUM_THREADS: "1" },
  },
);
interface Residual {
  family: string; cell: string; role: string; scheme: string; part: string;
  active: boolean; admissible: boolean; closure: boolean; pixels: number;
  residualRGB: number[]; toleranceRGB: number[]; fails: boolean;
}

describe("W37 G0b's declared numerical experiment", () => {
  it("integrates kernels, permits signed tails and detects pre-composition interventions", () => {
    const result = python("test-instrument.py");
    expect(result.status, result.stderr).toBe(0);
  });

  it("retains absent E1 sides and shells as UNMEASURED", () => {
    const result = python("test-canonical.py");
    expect(result.status, result.stderr).toBe(0);
    const old = new Map(read("../2026-09-25-w37-g0-edge-identification/e1-baseline.json")
      .map((r: { cell: string; bins: unknown[] }) => [r.cell, r]));
    for (const row of read("e1-baseline-repaired.json")) {
      const scale = row.cell.includes("-2x-") ? 2 : 1;
      expect(row.bins).toHaveLength(24 * scale);
      const measured = row.bins.every((b: { status: string }) => b.status === "measured");
      expect(row.status).toBe(measured ? "measured" : "UNMEASURED");
      const prior = old.get(row.cell) as { bins: { side: string; shell: number }[] };
      for (const bin of prior.bins) {
        expect(row.bins.find((b: { side: string; shell: number }) =>
          b.side === bin.side && b.shell === bin.shell)).toMatchObject(bin);
      }
    }
  });

  it("reconstructs selected-shape coefficients independently and replays every output", () => {
    const result = python("verify-scores.py", ["--verify"]);
    expect(result.status, result.stderr).toBe(0);
    const proof = JSON.parse(result.stdout);
    expect(proof.exactReproduction).toBe(true);
    for (const check of proof.checks) expect(check.coefficientMaxDifference).toBeLessThan(1e-8);
  }, 180_000);

  it("proves the obstruction from guarded native pixels, not from fitted residuals", () => {
    const result = python("form-obstruction.py", ["--verify"]);
    expect(result.status, result.stderr).toBe(0);
    for (const witness of JSON.parse(result.stdout).witnesses) {
      expect(witness.role).toBe("calibration");
      for (const floor of witness.minimaxLowerBoundCodes) expect(floor).toBeGreaterThan(1);
      for (const check of witness.checks) expect(check.maximumFeatureDifference).toBeLessThan(1e-14);
    }
  }, 60_000);

  it("keeps validation out of fitting and rejects rank-deficient shapes", () => {
    const split = read("../2026-09-23-w34-g0-contour-bed/split.json");
    for (const fit of read("fits.json")) {
      expect(fit.thicknessFactor).toBe(1);
      expect(fit.rank).toBe(fit.columns);
      for (const cell of fit.fitCells) {
        const scene = cell.split("/")[1];
        expect(split.calibration).toContain(scene);
        expect(split.validation).not.toContain(scene);
        expect(scene).toMatch(/__circular-(120|200)__rest$/);
      }
    }
    for (const search of read("search.json.gz")) {
      expect(search.trials).toHaveLength(45);
      for (const trial of search.trials) {
        expect(trial.accepted).toBe(trial.rank === trial.columns &&
          trial.coefficients.every((c: number) => Math.abs(c) <= 4096));
      }
    }
  });

  it("derives the hard stop and every summary from the complete per-bin tables", () => {
    const rows = read("residuals.json.gz") as Residual[];
    const verdict = read("family-summary.json");
    for (const row of rows) {
      expect(row.admissible).toBe(row.pixels >= 4);
      expect(row.fails).toBe(row.admissible &&
        row.residualRGB.some((v, c) => v > row.toleranceRGB[c]! + 1e-12));
    }
    for (const summary of verdict.rows) {
      const selected = rows.filter(r => r.family === summary.family && r.scheme === summary.scheme &&
        r.role === summary.role && r.active && r.admissible &&
        (summary.stratum === "circular" ? r.closure : summary.stratum === "diagnostic" ? !r.closure :
          r.part === "straight" && r.cell.includes("/grey-")));
      expect(selected).toHaveLength(summary.bins);
      expect(selected.filter(r => r.fails)).toHaveLength(summary.failedBins);
      expect(Math.max(...selected.flatMap(r => r.residualRGB))).toBe(summary.maximum);
    }
    const families = [...new Set(rows.map(r => r.family))];
    const closes = families.map(f => !rows.some(r => r.family === f && r.active && r.admissible &&
      r.role === "calibration" && r.part === "straight" && r.cell.includes("/grey-") && r.fails));
    expect(verdict.hardStop).toBe(!closes.some(Boolean));
  });

  it("counts old-treatment improvements and worsenings using the same mean-error estimand", () => {
    const comparisons = read("old-rim-comparison.json.gz");
    for (const row of comparisons) for (let c = 0; c < 3; c++) {
      const delta = Math.abs(row.predictedExcess[c] - row.nativeExcess[c]) -
        Math.abs(row.oldExcess[c] - row.nativeExcess[c]);
      expect(row.errorChange[c]).toBeCloseTo(delta, 12);
      expect(row.classificationRGB[c]).toBe(delta > 0.5 ? "worse" : delta < -0.5 ? "better" : "same");
    }
    for (const summary of read("old-rim-summary.json").filter((r: { scope: string }) => r.scope === "all")) {
      const labels = comparisons.filter((r: { family: string }) => r.family === summary.family)
        .flatMap((r: { classificationRGB: string[] }) => r.classificationRGB);
      for (const label of ["better", "same", "worse"]) {
        expect(summary.counts[label]).toBe(labels.filter((v: string) => v === label).length);
      }
    }
  });
});
