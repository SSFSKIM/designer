/** W33 G0's readers must not cancel channel errors or admit a held-out fitting row (§5.170). */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const EVIDENCE = resolve(import.meta.dirname, "../results/2026-09-22-w33-g0-rim-cut");

describe("W33 rim referee arithmetic", () => {
  it("keeps opposite channel errors and refuses a held-out fitting row", () => {
    const run = spawnSync("python3", ["-c", `
import sys, json
sys.path.insert(0, ${JSON.stringify(EVIDENCE)})
from rules import residual, fitting_role, round_up_2sf
r = residual([[0., 20., 10.]], [[20., 0., 10.]])
print(json.dumps(dict(mae=r['mae'], signed=r['signed'], zero=round_up_2sf(0),
                     rounded=round_up_2sf(.0000559626), holdout=fitting_role('holdout', False))))
`], { encoding: "utf8" });
    expect(run.status, run.stderr).toBe(0);
    const result = JSON.parse(run.stdout);
    expect(result.mae).toBeCloseTo(40 / 3);
    expect(result.signed).toEqual([-20, 20, 0]);
    expect(result.zero).toBe(0);
    expect(result.rounded).toBeCloseTo(.000056, 10);
    expect(result.holdout).toBe(false);
  });
});


interface BlackRow {
  profile: string; scene: string; role: string; pose: string;
  integer: { pixels: number; nativeNonzero: number; aboveZero: number; aboveOne: number };
  analytic: { aboveOne: number };
}
interface StrokeRow {
  profile: string; scene: string; role: string;
  offsets: { offset: number; all: { mae: number; maeRGB: number[] };
    strata: Record<string, { pixels: number; mae: number }> }[];
}
const read = (file: string) => JSON.parse(readFileSync(resolve(EVIDENCE, file), "utf8"));
const cut = read("referee.json") as {
  includeHoldout: boolean;
  censusSummary: { cells: number; withBlack: number; pixels: number; holdoutWithBlack: number };
  census: { pixels: number; role: string; scene: string }[];
  black: BlackRow[]; stroke: StrokeRow[];
  populations: { profile: string; pose: string; fitting: number; available: number;
    holdout: string[] }[];
  nativeLiftInventory: { profile: string; pixels: number; nonzero: number }[];
};

describe("W33 cut's committed populations and baselines (§5.170)", () => {
  it("pins the census while keeping native-only holdout out of every referee", () => {
    expect(cut.censusSummary).toEqual({ cells: 448, withBlack: 264,
      pixels: 14329648, holdoutWithBlack: 30 });
    expect(cut.census.reduce((sum, r) => sum + r.pixels, 0)).toBe(14329648);
    const nonblackBackdrop = cut.census.filter(r => r.scene.startsWith("dark-solid") && r.pixels);
    expect(nonblackBackdrop).toHaveLength(4);
    expect(nonblackBackdrop.reduce((sum, r) => sum + r.pixels, 0)).toBe(680);
    expect(cut.includeHoldout).toBe(false);
    expect([...cut.black, ...cut.stroke].every(r => r.role !== "holdout")).toBe(true);
    expect(cut.black.filter(r => r.profile.includes("27.0"))).toHaveLength(232);
    expect(cut.stroke.filter(r => r.profile.includes("27.0"))).toHaveLength(304);
    for (const r of cut.populations.filter(r => r.profile.includes("27.0") &&
      r.profile.includes("standard"))) {
      const light = r.profile.includes("light"), active = r.pose === "rest";
      expect(r.available).toBe(light ? (active ? 51 : 37) : (active ? 40 : 30));
      expect(r.holdout).toHaveLength(light ? 5 : 2);
      expect(r.fitting).toBe(r.available-r.holdout.length);
    }
  });

  it("reproduces the zero native27 floor and the nonzero frozen control", () => {
    const old = cut.nativeLiftInventory.filter(r => r.profile.includes("26.5"));
    expect(old).toHaveLength(125);
    expect(old.filter(r => r.nonzero > 0)).toHaveLength(39);
    const native27 = cut.nativeLiftInventory.filter(r => r.profile.includes("27.0"));
    expect(native27.every(r => r.nonzero === 0)).toBe(true);
    const inactive = cut.black.filter(r => r.profile.includes("27.0") && r.pose === "inactive");
    expect(inactive.length).toBeGreaterThan(0);
    expect(inactive.every(r => r.integer.aboveZero === 0)).toBe(true);
    for (const [scale, text, count, analytic] of [[1, 28, 66, 44], [1, 7, 39, 39],
      [2, 28, 222, 180], [2, 7, 150, 150]]) {
      const row = cut.black.find(r => r.profile ===
        `apple-macos-27.0-${scale}x-light-standard-glass0.5` &&
        r.scene === `hc-text-${text}__rrect-lg__rest`);
      expect(row?.integer.aboveOne).toBe(count);
      expect(row?.analytic.aboveOne).toBe(analytic);
    }
  });

  it("keeps all six offset baselines and reads corners rather than dropping them", () => {
    for (const row of cut.stroke) {
      expect(row.offsets.map(r => r.offset)).toEqual([1, 2, 3, 4, 5, 6]);
      for (const offset of row.offsets) {
        expect(Object.keys(offset.strata).filter(k => k.startsWith("corner-"))).toHaveLength(4);
        expect(offset.all.mae).toBeCloseTo(offset.all.maeRGB.reduce((a,b)=>a+b,0)/3, 9);
      }
    }
    const tables = read("tables.json");
    expect(tables.bounds).toHaveLength(304);
    expect(tables.m2).toHaveLength(26);
    expect(tables.m2.every((r: { changedByOutside: number; changedByInside: number }) =>
      r.changedByOutside === 0 && r.changedByInside > 0)).toBe(true);
    expect(tables.stops.inactiveAdmitted).toBe(0);
    expect(tables.stops.inactiveWhole).toBeCloseTo(.0007967193578457206, 12);
  });

  it("pins the composed-alpha counterexample and distinguishes feasibility from gate passage", () => {
    const forms = read("forms.json");
    expect(forms.inventory).toEqual({ all: 442, atOne: 254, selected: 115, selectedAtOne: 48 });
    expect(forms.threshold).toBe(.5);
    expect(forms.rows).toHaveLength(380);
    expect(forms.summary.map((r: { contourFailures: number; iouFailures: number }) =>
      [r.contourFailures, r.iouFailures])).toEqual([[17,17], [2,1], [113,123], [0,0]]);
    expect(forms.summary[3].infeasibleCells).toBe(380);
    expect(forms.summary[3].infeasibleBeyondOneCells).toBe(378);
    const example = forms.rows.find((r: { profile: string; scene: string }) =>
      r.profile === "apple-macos-27.0-1x-light-standard-glass0.5" &&
      r.scene === "light-solid__rrect-md__rest");
    expect(example.forms[2].newlyThresholded).toBe(320);
    expect(example.forms[2].declaredContourMaxWeb).toBe(Math.SQRT2);
    expect(forms.oracleSummary.selectedContourFailures).toBe(23);
    expect(forms.oracleSummary.selectedIoUFailures).toBe(24);
  });

  it("pins the declaration and both frozen identities separately from the proposed table", () => {
    expect(createHash("sha256").update(readFileSync(resolve(EVIDENCE, "bounds-declaration.md")))
      .digest("hex")).toBe("2935421e7a97ab8a08872eaaa7f417da1d416626f936b50b2ac44348e941efed");
    const proof = read("identity-proof.json");
    expect(proof).toHaveLength(6);
    expect(proof[0].before).toBe("b2b570e4adcea8fb");
    expect(proof[1].before).toBe("874be66ea501621b");
    for (const r of proof) for (const w of r.widths) {
      expect(w.flat).toBe(r.recorded);
      expect(w.nested).not.toBe(r.recorded);
    }
    expect(proof[0].widths[0].nested).toBe("da59d059f9526c73");
  });
});
