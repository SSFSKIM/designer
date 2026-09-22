/** W33 G1a's negative identification is evidence, not a new fidelity gate (§5.171). */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const here = resolve(import.meta.dirname, "../results/2026-09-22-w33-g1a-contour-model");
const read = <T>(name: string): T => JSON.parse(readFileSync(resolve(here, name), "utf8")) as T;
interface Cell { profile: string; scene: string; role: string }
interface Bin { residual: number; signed: number; predicted: number; signedRGB: number[]; pixels: number }
interface Fit { law: string; bins: Bin[]; maxBinResidual: number }
interface Angle {
  profile: string; pose: string; backdropClass: string; span: number; part: string;
  selected: string; closesOneByte: boolean; fits: Fit[];
}
interface Shape {
  silhouetteAreaWeb: number; silhouetteBodiesWeb: number; wellConditioned: boolean;
  declaredContourMaxWeb: number | null; declaredIoUWeb: number | null;
}
interface Form extends Shape {
  name: string; changedInteriorPixels: number; newlyThresholded: number; ringMAE: number;
  offsets: { offset: number; pixels: number; maeRGB: number[] }[];
}
interface PriceCell extends Cell { original: Shape; forms: Form[]; m2: boolean; hasCandidate: boolean }
interface PriceSummary {
  cells: number; conformanceCells: number; contourFailures: number; iouFailures: number;
  uniqueRedCells: number; infeasibleCells: number;
}
interface Forecast {
  name: string; cells: number; inactiveCells: number; before: number; inactiveBefore: number;
  changedDomain: number; rows: { changedDomain: boolean; before: number; after: number }[];
}
interface Proof {
  before: string; recorded: string; sweeps: { leaf: string; digest: string }[];
  widths: { flat: string; nested: string }[];
}
const hash = (name: string) => createHash("sha256")
  .update(readFileSync(resolve(here, name))).digest("hex");
const population = read<{ includeHoldout: boolean; rows: Cell[]; frozenControls: unknown[] }>("population.json");
const angular = read<{ bins: number; rows: Angle[] }>("angular.json");
const prices = read<{
  threshold: number; inventory: { all: number; atOne: number; selected: number; selectedAtOne: number };
  rows: PriceCell[]; skipped: unknown[]; summary: PriceSummary[]; forecasts: Forecast[];
}>("prices.json");
const tables = read<{
  angleSummary: { part: string; strata: number; closed: number }[];
  g0Ceilings: { red: boolean; mae: number; maeRGB: number[]; bound: number }[];
  ceilingMisses: number;
}>("tables.json");

describe("W33 contour identification, holdout-free and explicitly unclosed", () => {
  it("pins the population, the full angular profile and the candidate declaration", () => {
    expect(hash("population.json"))
      .toBe("614eacd5000604508110ea62a93697f1fe4b92dd247d52529b04c8c4f960d70b");
    expect(hash("angular.json"))
      .toBe("1942870b11e3d8a8850bbf3e00984c38d131f2124890aaf6813a2bca91bac149");
    expect(hash("candidate.json"))
      .toBe("3fe3c6f7cf71e52f08596a82aa45867cdfb57a2d55d9bd76be83fe404cae1417");
    expect(population.includeHoldout).toBe(false);
    expect(population.rows).toHaveLength(304);
    expect(angular.rows).toHaveLength(456);
    const spec = JSON.parse(readFileSync(resolve(here,
      "../../../../apps/reference-apple/scenes.json"), "utf8"));
    const heldOut = new Set(spec.split.holdout);
    for (const row of [...population.rows, ...prices.rows]) {
      expect(heldOut.has(row.scene)).toBe(false);
      expect(row.role).not.toBe("holdout");
      expect(row.profile).toContain("27.0");
    }
    expect(new Set(population.rows.map((r) => `${r.profile}/${r.scene}`)).size).toBe(304);
    expect(population.frozenControls).toHaveLength(4);
  });

  it("keeps arcs and every populated normal bin, rather than fitting only axes", () => {
    expect(angular.bins).toBe(16);
    expect(tables.angleSummary.map((r) => [r.part, r.strata, r.closed]))
      .toEqual([["all",152,0], ["straight",152,78], ["arcs",152,3]]);
    for (const row of angular.rows) {
      const fit = row.fits.find((f) => f.law === row.selected)!;
      expect(fit.bins.length).toBeGreaterThan(0);
      for (const bin of fit.bins) {
        expect(bin.residual).toBeCloseTo(bin.signed-bin.predicted, 10);
        expect(bin.signedRGB).toHaveLength(3);
        expect(bin.pixels).toBeGreaterThan(0);
      }
    }
    const example = angular.rows.find((r) => r.profile ===
      "apple-macos-27.0-1x-dark-standard-glass0.5" && r.pose === "rest" &&
      r.backdropClass === "photo" && r.span === 96 && r.part === "all")!;
    expect(example.selected).toBe("isotropic-even-4");
    const fit = example.fits.find((f) => f.law === example.selected)!;
    expect(fit.bins).toHaveLength(16);
    expect(fit.maxBinResidual).toBeCloseTo(14.76281306160735, 9);
    expect(example.closesOneByte).toBe(false);
  });

  it("recombines refined backdrop classes before applying G0's 304 ceilings", () => {
    expect(tables.g0Ceilings).toHaveLength(304);
    expect(tables.g0Ceilings.filter((r) => r.red)).toHaveLength(52);
    expect(tables.ceilingMisses).toBe(52);
    for (const row of tables.g0Ceilings) {
      expect(row.mae).toBeCloseTo(row.maeRGB.reduce((a: number,b: number)=>a+b,0)/3, 10);
      expect(row.red).toBe(row.mae > row.bound);
    }
  });

  it("prices valid RGBA8 replacement separately from the unattainable capped target", () => {
    expect(prices.threshold).toBe(.5);
    expect(prices.rows).toHaveLength(386);
    expect(prices.inventory).toEqual({ all: 380, atOne: 216, selected: 85, selectedAtOne: 30 });
    expect(prices.rows.filter(r => r.m2)).toHaveLength(26);
    expect(prices.rows.filter(r => r.m2 && r.hasCandidate)).toHaveLength(22);
    expect(prices.skipped).toEqual([]);
    expect(prices.summary.map((r) =>
      [r.cells,r.conformanceCells,r.contourFailures,r.iouFailures,r.uniqueRedCells]))
      .toEqual([[304,298,36,14,42], [304,298,0,0,0], [386,380,40,45,58], [386,380,0,0,0]]);
    for (const row of prices.rows) for (const form of row.forms) {
      expect(form.changedInteriorPixels).toBe(0);
      expect(form.silhouetteAreaWeb).toBe(row.original.silhouetteAreaWeb);
      expect(form.silhouetteBodiesWeb).toBe(row.original.silhouetteBodiesWeb);
      expect(form.wellConditioned).toBe(row.original.wellConditioned);
      if (form.name.endsWith("capped")) {
        expect(form.newlyThresholded).toBe(0);
        expect(form.declaredContourMaxWeb).toBe(row.original.declaredContourMaxWeb);
        expect(form.declaredIoUWeb).toBe(row.original.declaredIoUWeb);
      }
      if (form.name === "oracle-exact") expect(form.ringMAE).toBe(0);
      const peer = row.forms.find((f) => f.name.endsWith("exact"))!;
      expect(form.offsets.slice(1)).toEqual(peer.offsets.slice(1));
    }
    expect(prices.summary[1]!.infeasibleCells).toBe(120);
    expect(prices.summary[3]!.infeasibleCells).toBe(296);
  });

  it("preserves the complete stop population and declares the unmodelled cells unchanged", () => {
    for (const forecast of prices.forecasts) {
      expect(forecast.cells).toBe(166);
      expect(forecast.inactiveCells).toBe(81);
      expect(forecast.before).toBeCloseTo(.0007158135811605964, 12);
      expect(forecast.inactiveBefore).toBeCloseTo(.0007967193578457206, 12);
      expect(forecast.changedDomain).toBe(forecast.name.startsWith("candidate") ? 100 : 166);
      for (const row of forecast.rows.filter((r) => !r.changedDomain)) {
        expect(row.after).toBe(row.before);
      }
    }
  });

  it("extends the flat identity proof to all sixteen gated leaves on all six documents", () => {
    const declaration = read<{ gate: Record<string, number>; gated: Record<string, number> }>("candidate.json");
    expect(declaration.gate).toEqual({ contourStrokeAlpha: 0 });
    expect(Object.keys(declaration.gated)).toHaveLength(16);
    expect(Object.keys(declaration.gated).every(k => !k.includes("."))).toBe(true);
    const proof = read<Proof[]>("identity-proof.json");
    expect(proof).toHaveLength(6);
    for (const row of proof) {
      expect(row.before).toBe(row.recorded);
      expect(row.sweeps).toHaveLength(80);
      expect(new Set(row.sweeps.map((r) => r.leaf)))
        .toEqual(new Set(Object.keys(declaration.gated)));
      expect(row.sweeps.every((s) => s.digest === row.recorded)).toBe(true);
      expect(row.widths.every((w) => w.flat === row.recorded && w.nested !== row.recorded))
        .toBe(true);
    }
  });
});
