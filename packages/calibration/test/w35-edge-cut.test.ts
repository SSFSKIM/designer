/** W35 G0a pins immutable evidence and exercises access/forward/replay behavior (§5.177). */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";
const E = resolve(import.meta.dirname, "../results/2026-09-24-w35-g0-edge-cut");
const bytes = (name: string) => readFileSync(resolve(E, name));
const read = (name: string) => JSON.parse((name.endsWith(".gz") ? gunzipSync(bytes(name)) : bytes(name)).toString());
interface Bin { pixels: number; shell: number; admissible: boolean; barRGB: number[] }
interface Bar { cell: string; role: string; H: number; protocol: string; runs: number; bins: Bin[] }
interface Profile { cell: string; role: string; H: number; rows: { pixels: number; shell: number }[] }
const profiles = read("profiles.json.gz") as Profile[];
const bars = read("deep-bars.json.gz") as Bar[];

describe("W35's frozen cut and the boundary that makes it non-holdout", () => {
  it("refuses held, recorded and path-named payloads before opening them", () => {
    const r = spawnSync("python3.12", [resolve(E, "test-readers.py")], { encoding: "utf8" });
    expect(r.status, r.stderr).toBe(0);
  });

  it("recovers the pre-shadow intervention and does not cancel signed errors", () => {
    const r = spawnSync("python3.12", [resolve(E, "test-instrument.py")], { encoding: "utf8" });
    expect(r.status, r.stderr).toBe(0);
  });

  it("replays new deep-shell bars from all guarded states without raw sitting access", () => {
    const r = spawnSync("python3.12", [resolve(E, "test-replay.py")], { encoding: "utf8" });
    expect(r.status, r.stderr).toBe(0);
  }, 30_000);

  it("keeps the profile and repeat populations and never pools the two protocols", () => {
    expect(profiles).toHaveLength(336);
    expect(new Set(profiles.map(r => r.cell)).size).toBe(336);
    expect(profiles.every(r => ["calibration", "validation"].includes(r.role))).toBe(true);
    expect(profiles.reduce((n, r) => n + r.rows.length, 0)).toBe(42444);
    expect(bars).toHaveLength(672);
    expect(bars.reduce((n, r) => n + r.bins.length, 0)).toBe(238292);
    expect(bars.filter(r => r.protocol === "normal").every(r => r.runs === 7)).toBe(true);
    expect(bars.filter(r => r.protocol === "normal").reduce((n, r) => n + r.runs, 0)).toBe(2352);
    expect(bars.filter(r => r.protocol === "long").reduce((n, r) => n + r.runs, 0)).toBe(48);
    let maximum = 0;
    for (const r of bars) for (const b of r.bins) {
      expect(b.shell).toBeGreaterThanOrEqual(-r.H);
      expect(b.shell).toBeLessThan(4);
      expect(b.admissible).toBe(b.pixels >= 4);
      maximum = Math.max(maximum, ...b.barRGB);
    }
    expect(maximum).toBe(.5);
  }, 30_000); // The full 238,292-bin population is asserted even under concurrent workspace load.

  it("pins the domain before candidates and keeps diagnostic exclusions explicit", () => {
    expect(createHash("sha256").update(bytes("domain.json")).digest("hex"))
      .toBe("b03ea804892b390ed3a88533838cbad3e6b2f46178981551e92cb6d938773d00");
    expect(createHash("sha256").update(bytes("bounds-declaration.txt")).digest("hex"))
      .toBe("f712ea6b44e2ae1c516456f582e9e04d1bda333b1db4cac398ed53b2e262d1f5");
    const domain = read("domain.json");
    expect(domain.deepBody.innerEdgeCssPx).toBe(6);
    expect(domain.closure.minimumPixels).toBe(4);
    expect(Object.keys(domain.diagnosticOnly).sort()).toEqual(
      ["coverage", "mixedArcs", "outside", "structured", "trough"]);
    for (const [file, sha] of Object.entries(read("pins.json").sha256)) {
      expect(createHash("sha256").update(bytes(file)).digest("hex"), file).toBe(sha);
    }
  });

  it("preserves failure and the exact receded identity instead of manufacturing closure", () => {
    const verdicts = read("candidate-verdicts.json") as { closes: boolean; worstActive: number }[];
    expect(verdicts).toHaveLength(8);
    expect(verdicts.every(r => !r.closes && r.worstActive > 1)).toBe(true);
    const receded = read("receded-composition.json") as { changedPixels: number; maxDelta: number }[];
    expect(receded).toHaveLength(8);
    expect(receded.every(r => r.changedPixels === 0 && r.maxDelta === 0)).toBe(true);
    const m2 = read("m2-gated-attribution.json") as { cells: { matchesMatrix: number }[] };
    expect(m2.cells).toHaveLength(26);
    expect(m2.cells.every(r => r.matchesMatrix < 1e-12)).toBe(true);
  });

  it("keeps the six digests fixed under the proposed flat identity drop", () => {
    const proof = read("identity-proof.json") as { before: string; after: string; nonzero: string }[];
    expect(proof).toHaveLength(6);
    expect(proof[0]?.before).toBe("b2b570e4adcea8fb");
    expect(proof[1]?.before).toBe("874be66ea501621b");
    for (const r of proof) {
      expect(r.after).toBe(r.before);
      expect(r.nonzero).not.toBe(r.before);
    }
  });
});
