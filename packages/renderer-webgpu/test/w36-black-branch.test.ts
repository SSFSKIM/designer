/** W36 DL5: a black endpoint must not perturb the identified impulse/middle (§5.179). */
import { describe, expect, it } from "vitest";
import {
  DEFAULT_MATERIAL_PROFILE, backdropToneResponse, backdropToneSolveWeight,
  withMaterialOverrides, type MaterialProfilePatch,
} from "../src/material";

const old = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
  backdropToneResponseThin: [0.214, 0.2835, 0.5383, 0.937],
  backdropToneResponseThick: [0.242, 0.3074, 0.5554, 0.957],
});
const patch = (gate: number, thin = 0.2, thick = 0.3): MaterialProfilePatch => ({
  backdropToneBlackStrength: gate, backdropToneBlackThin: thin, backdropToneBlackThick: thick,
} as MaterialProfilePatch);

describe("W36 black branch", () => {
  it("solves a finite black endpoint with full authority, not the old fallback", () => {
    const on = withMaterialOverrides(old, patch(1));
    expect(backdropToneSolveWeight(0, on)).toBe(1);
    expect(backdropToneResponse(0, 0, on)).toBeCloseTo(0.2, 14);
    expect(backdropToneResponse(0, 1, on)).toBeCloseTo(0.3, 14);
  });
  it("keeps the old response and authority exact at gate zero whatever its ordinates", () => {
    for (const level of [0, 0.01, 0.2, 0.9, 1]) {
      const off = withMaterialOverrides(old, patch(0, level, 1 - level));
      for (const x of [0, 0.001, 0.002, 0.0029, 0.003, 0.003195, 0.004, 0.11, 0.5, 1]) {
        expect(backdropToneSolveWeight(x, off)).toBe(backdropToneSolveWeight(x, old));
        for (const t of [0, 0.09228515625, 0.5, 1]) {
          expect(backdropToneResponse(x, t, off)).toBe(backdropToneResponse(x, t, old));
        }
      }
    }
  });
  it("changes nothing at or above the join, including the below-anchor impulse cells", () => {
    const on = withMaterialOverrides(old, patch(1));
    for (const x of [0.003, 0.003195, 0.003284, 0.00375, 0.004, 0.11, 0.425, 0.95, 1]) {
      expect(backdropToneSolveWeight(x, on)).toBe(backdropToneSolveWeight(x, old));
      for (const t of [0, 0.09228515625, 0.5, 1]) {
        expect(backdropToneResponse(x, t, on)).toBe(backdropToneResponse(x, t, old));
      }
    }
  });
  it("rejoins continuously and stays finite throughout its support", () => {
    const on = withMaterialOverrides(old, patch(1));
    for (const t of [0, 0.09228515625, 0.5, 1]) {
      expect(backdropToneResponse(0.003 - 1e-10, t, on))
        .toBeCloseTo(backdropToneResponse(0.003, t, old), 12);
      for (let i = 0; i <= 300; i++) {
        const x = i / 100000;
        expect(Number.isFinite(backdropToneResponse(x, t, on))).toBe(true);
        expect(backdropToneSolveWeight(x, on)).toBeGreaterThanOrEqual(0);
        expect(backdropToneSolveWeight(x, on)).toBeLessThanOrEqual(1);
      }
    }
  });
});
