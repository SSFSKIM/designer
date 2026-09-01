/**
 * The scene matrix's own consistency, checked where CI can see it.
 *
 * `apps/reference-apple/scenes.json` is validated at load by the Swift harness
 * (`SceneSpecFile.validate()`), and that check is the stricter of the two — but
 * it only runs on a Mac with Xcode, at the moment someone starts a capture. A
 * broken edit therefore surfaces at the worst possible time: after the rebuild
 * that invalidates the screen-recording grant, with a human waiting. These
 * assertions are the same invariants, evaluated in CI on every push, so the file
 * cannot reach a capture session inconsistent.
 *
 * Nothing here reads a fixture or a result. The matrix is a declaration, and a
 * declaration can be wrong long before anything has been measured against it.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  backdropToneAdaptation,
  sizeThickness,
} from "@vitrea/renderer-webgpu";

import { linearRgbLuminance, srgbByteToLinear } from "../src/color";

const REPO_ROOT = resolve(import.meta.dirname, "..", "..", "..");

interface SceneEntry {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
  readonly tint?: string;
}

interface Matrix {
  readonly version: number;
  readonly backgrounds: Record<string, { readonly kind: string; readonly srgb?: readonly number[] }>;
  readonly components: Record<string, { readonly kind: string; readonly size?: readonly number[] }>;
  readonly tints: Record<string, { readonly srgb: readonly number[]; readonly alpha?: number }>;
  readonly scenes: readonly SceneEntry[];
  readonly profiles: readonly { readonly key: string; readonly scenes: "all" | readonly string[] }[];
  readonly split: Record<"calibration" | "validation" | "holdout" | "recorded", readonly string[]>;
}

const MATRIX = JSON.parse(
  readFileSync(resolve(REPO_ROOT, "apps", "reference-apple", "scenes.json"), "utf8"),
) as Matrix;

const SETS = ["calibration", "validation", "holdout", "recorded"] as const;
const IDS = new Set(MATRIX.scenes.map((scene) => scene.id));
const setOf = (id: string): string | undefined =>
  SETS.find((set) => MATRIX.split[set].includes(id));

describe("the scene matrix resolves", () => {
  it("gives every scene exactly one split set", () => {
    // Unassigned is the dangerous direction and the reason the Swift side
    // refuses rather than defaulting: a scene silently treated as calibration is
    // how a holdout leaks into tuning.
    const unassigned = MATRIX.scenes.filter((scene) => setOf(scene.id) === undefined);
    expect(unassigned.map((scene) => scene.id)).toEqual([]);

    const assignments = SETS.flatMap((set) => MATRIX.split[set]);
    expect(assignments.length).toBe(new Set(assignments).size);
  });

  it("names only real scenes in the split", () => {
    const phantom = SETS.flatMap((set) => MATRIX.split[set]).filter((id) => !IDS.has(id));
    expect(phantom).toEqual([]);
  });

  it("resolves every scene's background, component and tint", () => {
    const unresolved: string[] = [];
    for (const scene of MATRIX.scenes) {
      if (MATRIX.backgrounds[scene.background] === undefined) {
        unresolved.push(`${scene.id}: background "${scene.background}"`);
      }
      if (MATRIX.components[scene.component] === undefined) {
        unresolved.push(`${scene.id}: component "${scene.component}"`);
      }
      // The one that would fail SILENTLY if it got through: an unknown tint id
      // renders an untinted surface under a tinted scene id, on both sides.
      if (scene.tint !== undefined && MATRIX.tints[scene.tint] === undefined) {
        unresolved.push(`${scene.id}: tint "${scene.tint}"`);
      }
    }
    expect(unresolved).toEqual([]);
  });

  it("gives every profile a list of real, distinct scenes", () => {
    for (const profile of MATRIX.profiles) {
      if (profile.scenes === "all") continue;
      expect(profile.scenes.filter((id) => !IDS.has(id)), profile.key).toEqual([]);
      expect(new Set(profile.scenes).size, profile.key).toBe(profile.scenes.length);
    }
  });

  it("declares a tint registry whose colours are well formed", () => {
    for (const [id, spec] of Object.entries(MATRIX.tints)) {
      expect(spec.srgb.length, id).toBe(3);
      for (const channel of spec.srgb) {
        expect(Number.isInteger(channel), id).toBe(true);
        expect(channel, id).toBeGreaterThanOrEqual(0);
        expect(channel, id).toBeLessThanOrEqual(255);
      }
      if (spec.alpha !== undefined) {
        expect(spec.alpha, id).toBeGreaterThan(0);
        expect(spec.alpha, id).toBeLessThanOrEqual(1);
      }
    }
  });
});

describe("the pressed cells are recorded, not fitted (Decision Log 19 ruling 1)", () => {
  const pressed = MATRIX.scenes.filter((scene) => scene.state === "pressed");

  it("keeps them in the matrix — they are captured evidence, not deleted", () => {
    // The bed still captures them: the appearance exists, it is just not one
    // this wave can fit to. Deleting them would throw away the only cells that
    // could ever answer the pressed question.
    expect(pressed.length).toBeGreaterThan(0);
  });

  it("gives every one of them the recorded role, and none a fitted or checked one", () => {
    // Why: on 2026-08-31 eleven of the twelve pressed fixtures were byte-copies
    // of their rest twin, and two of those copies sat in `validation` against
    // rest cells in `calibration` — so the held-out self-check on them was
    // reading the fit's own training data and could not have failed. Until the
    // pressed pose is captured for real, a pressed cell may carry no role that
    // any fit, check or bound reads. Claims §5.18.
    const misplaced = pressed.filter((scene) => setOf(scene.id) !== "recorded");
    expect(misplaced.map((scene) => scene.id)).toEqual([]);
  });

  it("leaves each of their rest twins in a fitted or checked set, unmoved", () => {
    // The dedupe removes the duplicate, not the measurement. Every pressed cell
    // was a copy of a rest cell that is still doing its job.
    for (const scene of pressed) {
      const twin = scene.id.replace(/__pressed$/, "__rest");
      expect(IDS.has(twin), twin).toBe(true);
      expect(["calibration", "validation", "holdout"]).toContain(setOf(twin));
    }
  });
});

describe("W3's tinted cells", () => {
  const tinted = MATRIX.scenes.filter((scene) => scene.tint !== undefined);

  it("are sized as the capture plan states: 7 calibration, 2 validation, 3 holdout", () => {
    const bySet = Object.fromEntries(
      SETS.map((set) => [set, tinted.filter((scene) => setOf(scene.id) === set).length]),
    );
    expect(bySet).toEqual({ calibration: 7, validation: 2, holdout: 3, recorded: 0 });
  });

  it("sweep five backdrop levels on the calibration set", () => {
    // Four free parameters in the tone curve, five constraints. The fifth is
    // what makes the fit falsifiable rather than exact, so losing a backdrop
    // level silently turns the measurement into an interpolation.
    const backdrops = new Set(
      tinted.filter((scene) => setOf(scene.id) === "calibration").map((scene) => scene.background),
    );
    expect(backdrops.size).toBe(5);
  });

  it("keep the three-segment scene id grammar, with the tint as a state suffix", () => {
    // X2: new axes extend the scene set, never the key grammar. Every consumer
    // that keys on an id assumes three `__` segments.
    for (const scene of MATRIX.scenes) {
      const segments = scene.id.split("__");
      expect(segments.length, scene.id).toBe(3);
      expect(segments[0], scene.id).toBe(scene.background);
      expect(segments[1], scene.id).toBe(scene.component);
      expect(segments[2], scene.id).toBe(
        scene.tint === undefined ? scene.state : `${scene.state}-tint-${scene.tint}`,
      );
    }
  });
});

describe("W7's backdrop-adaptation holdout", () => {
  const HOLDOUT = "mid-dark-solid__capsule-button__rest";

  /** The declared backdrop's linear luminance, by the same Rec. 709 weights the runtime samples with. */
  function luminanceOf(backgroundId: string): number {
    const background = MATRIX.backgrounds[backgroundId];
    if (background?.srgb === undefined) {
      throw new Error(`"${backgroundId}" is not a solid, so it has no single luminance`);
    }
    const [r, g, b] = background.srgb;
    return linearRgbLuminance(
      srgbByteToLinear(r ?? 0),
      srgbByteToLinear(g ?? 0),
      srgbByteToLinear(b ?? 0),
    );
  }

  /** What the shipped constants actually do over a backdrop, under a capsule-button. */
  function adaptationOver(backgroundId: string): number {
    const size = MATRIX.components["capsule-button"]?.size ?? [];
    const span = Math.min(size[0] ?? 0, size[1] ?? 0);
    return backdropToneAdaptation(
      luminanceOf(backgroundId),
      sizeThickness(span, DEFAULT_MATERIAL_PROFILE),
      DEFAULT_MATERIAL_PROFILE,
    );
  }

  it("exists, and is a holdout", () => {
    expect(IDS.has(HOLDOUT)).toBe(true);
    expect(setOf(HOLDOUT)).toBe("holdout");
    // Untinted on purpose: the axis is a function of luminance, and an author
    // tint would put a second unmeasured mechanism in the same cell.
    expect(MATRIX.scenes.find((scene) => scene.id === HOLDOUT)?.tint).toBeUndefined();
  });

  it("sits strictly ABOVE the collapse band, at every canonical size", () => {
    /*
     * REWRITTEN BY W9 (claims §5.33–§5.34). The original assertion held this
     * backdrop on the collapse curve's slope, and it fired exactly as designed
     * when the fit moved the curve — but the move was the round's finding, not
     * a regression: the reference's small surface over mid-dark keeps a
     * textured body at 0.4561, and the old band's partial collapse here WAS
     * the measured 0.1375-vs-0.4561 overshoot. The binding property inverts:
     * mid-dark-solid is now the band's upper-edge GUARD. If any size of
     * surface collapses over this backdrop, the overshoot is back.
     *
     * The collapse slope itself is no longer exercised by any canonical cell —
     * by design, the knee is a near-binary size snap bounded by the capsule
     * (full) and the 96 px rrect (none) over dark-solid below; its interior is
     * validated by the probe bed's frequency-settled cells instead.
     */
    for (const thickness of [0, 0.093, 0.5, 1]) {
      expect(
        backdropToneAdaptation(
          luminanceOf("mid-dark-solid"),
          thickness,
          DEFAULT_MATERIAL_PROFILE,
        ),
      ).toBe(0);
    }
  });

  it("brackets the collapse's size snap over dark-solid: capsule full, 96 px none", () => {
    /*
     * The two-rail pin the W9 band was placed by (claims §5.33): the reference
     * collapses its 44 px capsule onto dark-solid byte-identically — which
     * needs adaptation EXACTLY 1, since the rim and body fade on (1 − k) — and
     * leaves its 96 px rrect essentially unadapted. Both written against the
     * renderer's own constants, so a band edge cannot drift out from under
     * either without this failing.
     */
    expect(adaptationOver("dark-solid")).toBe(1);
    expect(
      backdropToneAdaptation(luminanceOf("dark-solid"), 1, DEFAULT_MATERIAL_PROFILE),
    ).toBe(0);
  });
});
