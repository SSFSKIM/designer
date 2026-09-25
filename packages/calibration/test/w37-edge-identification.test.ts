/** W37 G0's access, native-only identification and immutable declaration (§5.181). */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";

const cal = resolve(import.meta.dirname, "..");
const here = resolve(cal, "results/2026-09-25-w37-g0-edge-identification");
const bytes = (name: string) => readFileSync(resolve(here, name));
const read = (name: string) => JSON.parse(
  (name.endsWith(".gz") ? gunzipSync(bytes(name)) : bytes(name)).toString(),
);
const python = (name: string, args: string[] = []) => spawnSync(
  "python3.12", [resolve(here, name), ...args], { encoding: "utf8", maxBuffer: 8 * 1024 * 1024 },
);
interface Residual {
  cell: string; shell: number; bin: number; toleranceRGB: number[];
  space: string; scheme: string; role: string; active: boolean; closure: boolean;
  admissible: boolean; part: string; pixels: number; residualRGB: number[]; fails: boolean;
}

describe("W37's guarded, native-conditioned boundary identification", () => {
  it("refuses spent native, web, canonical holdout and recorded payloads before open", () => {
    const result = python("test-readers.py");
    expect(result.status, result.stderr).toBe(0);
  });

  it("checks opaque composition, compact support and pre-composition interventions", () => {
    const result = python("test-instrument.py");
    expect(result.status, result.stderr).toBe(0);
  });

  it("reconstructs every score and selected-shape coefficient from guarded native pixels", () => {
    const result = python("verify-scores.py");
    expect(result.status, result.stderr).toBe(0);
    const proof = JSON.parse(result.stdout);
    expect(proof.exactReproduction).toBe(true);
    expect(proof.checks).toHaveLength(4);
    for (const check of proof.checks) {
      expect(check.rank).toBe(5);
      expect(check.nativeOnlyCoefficientDifference).toBeLessThan(1e-10);
    }
  }, 60_000);

  it("replays the complete memo cut instead of trusting a stored zero-difference flag", () => {
    // G0 records absolute worktree provenance; compare every numeric field while keeping
    // those original paths as evidence rather than requiring this checkout to have its name.
    const result = python("../2026-09-25-w37-g0b-edge-identification/reproduce-g0.py",
      ["--verify-native"]);
    expect(result.status, result.stderr).toBe(0);
  }, 60_000);

  it("pins the pre-score declaration, E1 population and unchanged-stop snapshot", () => {
    const pins: Record<string, string> = {
      "bounds-declaration.txt": "270ba479c6599bea082696e111b1ba81d9f941d93cfb6343c29a387e3ca8328b",
      "e1-declaration.json": "de89c420cfa0a50e241162e8830f80e50a7599a3d2193c417dc7c2d7020937ea",
      "canonical-stop-baseline.json.gz": "65771fd6578aa4eca309ec92bf75d777a0923ee3e33a0932a9a87dc27ff5df16",
    };
    for (const [name, sha] of Object.entries(pins)) {
      expect(createHash("sha256").update(bytes(name)).digest("hex"), name).toBe(sha);
    }
    expect(read("declaration-pins.json")).toEqual(pins);
    const old = readFileSync(resolve(here, "../2026-09-24-w35-g0-edge-cut/domain.json"));
    expect(createHash("sha256").update(old).digest("hex"))
      .toBe("b03ea804892b390ed3a88533838cbad3e6b2f46178981551e92cb6d938773d00");
  });

  it("keeps validation and thickness transfer out of all coefficient fits", () => {
    const split = JSON.parse(readFileSync(resolve(here,
      "../2026-09-23-w34-g0-contour-bed/split.json"), "utf8"));
    for (const fit of read("fits.json")) {
      expect(fit.thickness.freeParameters).toBe(0);
      expect(fit.thickness.calibrationSpans).toEqual([44]);
      for (const cell of fit.fitCells as string[]) {
        const scene = cell.split("/")[1];
        expect(split.calibration).toContain(scene);
        expect(split.validation).not.toContain(scene);
        expect(scene).toMatch(/__circular-(120|200)__rest$/);
      }
    }
  });

  it("rederives the negative verdict from every channel rather than hiding failing bins", () => {
    const rows = read("residuals.json.gz") as Residual[];
    for (const r of rows) {
      expect(r.admissible).toBe(r.pixels >= 4);
      expect(r.fails).toBe(r.admissible && r.residualRGB.some(v => v > 1));
    }
    for (const summary of read("family-summary.json").rows) {
      const selected = rows.filter(r => r.active && r.admissible && r.closure &&
        r.space === summary.space && r.scheme === summary.scheme && r.role === summary.role);
      expect(selected).toHaveLength(summary.bins);
      expect(selected.filter(r => r.fails)).toHaveLength(summary.failedBins);
      expect(Math.max(...selected.flatMap(r => r.residualRGB))).toBe(summary.maxCodes);
      expect(Math.max(...selected.filter(r => r.part === "straight").flatMap(r => r.residualRGB)))
        .toBe(summary.straightMaxCodes);
    }
    expect(read("family-summary.json").nomination).toBe("none");
  });

  it("uses the matching whole-pixel repeat tolerance rather than a pooled bar", () => {
    const bars = new Map<string, { pixels: number; barRGB: number[]; tauRGB: number[] }>();
    for (const cell of read("closure-bars.json.gz")) {
      expect(cell.runStates).toHaveLength(7);
      for (const bin of cell.bins) bars.set(
        `${cell.cell}/${bin.part}/${bin.shell}/${bin.bin}`, bin,
      );
    }
    for (const row of read("residuals.json.gz") as Residual[]) {
      const bar = bars.get(`${row.cell}/${row.part}/${row.shell}/${row.bin}`)!;
      expect(bar).toBeDefined();
      expect(bar.pixels).toBe(row.pixels);
      if (row.admissible) {
        expect(row.toleranceRGB).toEqual(bar.barRGB.map(v => Math.max(1, v)));
        expect(row.toleranceRGB).toEqual(bar.tauRGB);
      }
    }
  });

  it("derives E1's rows from the declared scenes without dropping rim-only native masks", () => {
    const declaration = read("e1-declaration.json");
    const rows = read("canonical-stop-baseline.json.gz").rows;
    const selected = rows.filter((r: { key: { sceneId: string; web: { renderer: string } } }) =>
      r.key.web.renderer === "webgpu" && declaration.scenes.includes(r.key.sceneId));
    const cells = selected.map((r: { key: { profileKey: string; sceneId: string } }) =>
      `${r.key.profileKey}/${r.key.sceneId}`).sort();
    expect(cells).toEqual(declaration.cells);
    expect(cells).toHaveLength(14);
    expect(read("e1-baseline.json").map((r: { cell: string }) => r.cell)).toEqual(cells);
    expect(declaration.boundCodes).toBe(1);
    expect(declaration.minimumPixels).toBe(4);
  });

  it("executes the six-document identity route across unread gated-leaf values", () => {
    const result = spawnSync("pnpm", ["exec", "tsx", resolve(here, "identity-proof.ts"), "--stdout"],
      { cwd: cal, encoding: "utf8", maxBuffer: 8 * 1024 * 1024 });
    expect(result.status, result.stderr).toBe(0);
    const proof = JSON.parse(result.stdout);
    expect(proof.rows).toHaveLength(6);
    expect(proof.rows.map((r: { before: string }) => r.before)).toEqual([
      "b2b570e4adcea8fb", "874be66ea501621b", "be13dae45098fc89",
      "b0d0d8dacc6a03af", "2a4323f33df8d799", "7c454858a3cbad5b",
    ]);
    for (const r of proof.rows) for (const check of r.checks) {
      expect(check.identity).toBe(r.before);
      expect(check.nonzero).not.toBe(r.before);
    }
    expect(proof.renderedNewLeafIdentity).toBe(false);
  }, 30_000);
});
