import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";

const evidence = new URL("../results/2026-09-25-w38-g0-rim-axis-cut/", import.meta.url);
describe("W38 dominance before aggregate", () => {
  it("rejects a veto inside an improving stratum and separately checks horizontal normals", () => {
    expect(() => execFileSync("python3.12", [new URL("test-veto.py", evidence).pathname],
      { stdio: "pipe" })).not.toThrow();
  });
  it("does not nominate a failure witness when the declared search has no feasible point", () => {
    const search = JSON.parse(gunzipSync(readFileSync(new URL("search-results.json.gz", evidence))).toString()) as {
      scheme: string;
      trials: { index: number; feasible: boolean; minimax: number; maximumConstraintExcess: number }[];
    }[];
    const fits = JSON.parse(readFileSync(new URL("fits.json", evidence), "utf8")) as {
      scheme: string; selected: unknown; feasiblePoints: number;
      failureWitness: { index: number };
    }[];
    for (const fit of fits) {
      const trials = search.find(row => row.scheme === fit.scheme)!.trials;
      const feasible = trials.filter(row => row.maximumConstraintExcess <= 1e-10);
      expect(feasible.length).toBe(fit.feasiblePoints);
      expect(feasible).toHaveLength(0);
      expect(fit.selected).toBeNull();
      const closest = [...trials].sort((a, b) =>
        a.maximumConstraintExcess - b.maximumConstraintExcess || a.minimax - b.minimax)[0]!;
      expect(closest.index).toBe(fit.failureWitness.index);
      expect(closest.feasible).toBe(false);
    }
  });
});
