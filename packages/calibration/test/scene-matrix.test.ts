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
  readonly canvas: { readonly width: number; readonly height: number };
  readonly backgrounds: Record<string, { readonly kind: string; readonly srgb?: readonly number[] }>;
  readonly components: Record<string, { readonly kind: string; readonly size?: readonly number[] }>;
  readonly tints: Record<string, { readonly srgb: readonly number[]; readonly alpha?: number }>;
  readonly scenes: readonly SceneEntry[];
  readonly profiles: readonly { readonly key: string; readonly scenes: "all" | readonly string[] }[];
  readonly split: Record<
    "calibration" | "validation" | "holdout" | "recorded" | "probe",
    readonly string[]
  >;
}

const MATRIX = JSON.parse(
  readFileSync(resolve(REPO_ROOT, "apps", "reference-apple", "scenes.json"), "utf8"),
) as Matrix;

const SETS = ["calibration", "validation", "holdout", "recorded", "probe"] as const;
/**
 * The sets a fidelity number is stated over. `recorded` and `probe` are outside
 * it for opposite reasons — one is read by nothing, the other is read by fits
 * and claims but bound by no gate — and every assertion below that is about the
 * frozen bed's shape is written against these three rather than against all
 * five (W25 Decision Log 3 (e)).
 */
const GATED_SETS: readonly string[] = ["calibration", "validation", "holdout"];
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
    // The four probe tinted cells are W25's, and they are counted separately
    // on purpose: this assertion is what would catch a probe cell drifting into
    // a fitted or checked role, which is the whole risk a non-gated set carries.
    expect(bySet).toEqual({ calibration: 7, validation: 2, holdout: 3, recorded: 0, probe: 4 });
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

describe("W25's probe set is captured evidence that no gate is stated over", () => {
  const PROBE = MATRIX.split.probe;

  it("is declared, non-empty, and disjoint from every gated set", () => {
    // The one property the role exists for. A probe id that also sat in a gated
    // list would be a cell the gate reads and the fits treat as free ground.
    expect(PROBE.length).toBeGreaterThan(0);
    const gated = new Set(GATED_SETS.flatMap((set) => MATRIX.split[set as "calibration"]));
    expect(PROBE.filter((id) => gated.has(id))).toEqual([]);
  });

  it("keeps the grids' own scene ids, so a probe row continues a grid row", () => {
    // W9's and W21's grids ran through VITREA_SCENES into their own fixture
    // directories and the ledger cites them by id. Folding them into the
    // canonical matrix under a different name would break every citation, and
    // re-deriving an id is how two records of the same measurement drift apart.
    const grid = JSON.parse(
      readFileSync(resolve(REPO_ROOT, "apps", "reference-apple", "scenes-w9-probe.json"), "utf8"),
    ) as { scenes: readonly SceneEntry[] };
    const missing = grid.scenes.map((scene) => scene.id).filter((id) => !IDS.has(id));
    expect(missing).toEqual([]);
  });

  it("re-declares the two withdrawn dark-grid cells (claims §5.113)", () => {
    // Both W21 fixtures' majority byte-state is the W9 LIGHT grid's file, so
    // both were withdrawn as dark readings. They are back in the matrix to be
    // re-captured under the dark scheme, and they are probe cells because
    // nothing on the frozen bed was ever fitted on them.
    for (const id of ["dark-solid__rrect-sm__rest", "light-solid__rrect-sm__rest"]) {
      expect(IDS.has(id), id).toBe(true);
      expect(setOf(id), id).toBe("probe");
    }
  });

  it("separates span from canvas clearance at one span", () => {
    // On this canvas the short-axis clearance falls with span (84 / 52 / 20 CSS
    // px at 32 / 96 / 160), so "the collapse keys on span" and "the collapse
    // keys on edge proximity" fit every committed fixture equally well. This
    // cell holds rrect-md's geometry and moves its clearance to rrect-lg's.
    const canvas = MATRIX.canvas;
    const clear = MATRIX.components["rrect-md-clear20"] as {
      size: readonly number[];
      offset?: readonly number[];
    };
    const plain = MATRIX.components["rrect-md"] as { size: readonly number[] };
    expect(clear.size).toEqual(plain.size);
    const height = clear.size[1] ?? 0;
    const top = Math.round((canvas.height - height) / 2) + (clear.offset?.[1] ?? 0);
    expect(canvas.height - top - height).toBe(20);
  });

  it("rides the four standard profiles and none of the accessibility ones", () => {
    // Both scales in both schemes is the amendment: the grids as they stood on
    // disk were 1x only, and no fixture identified the reference's kernel width
    // above span 96 at 2x. The accessibility profiles are excluded because the
    // question the set asks is about the material, not about a11y policy, and
    // each such profile costs its own capture session with a System Settings
    // toggle flipped.
    const carrying = MATRIX.profiles
      .filter((profile) => profile.scenes === "all" || PROBE.every((id) => profile.scenes.includes(id)))
      .map((profile) => profile.key)
      .sort();
    expect(carrying).toEqual([
      "apple-macos-26.5-1x-dark-standard",
      "apple-macos-26.5-1x-light-standard",
      "apple-macos-26.5-2x-dark-standard",
      "apple-macos-26.5-2x-light-standard",
    ]);
    for (const key of [
      "apple-macos-26.5-1x-light-reduced-transparency",
      "apple-macos-26.5-1x-light-increased-contrast",
    ]) {
      const profile = MATRIX.profiles.find((p) => p.key === key);
      expect(profile?.scenes === "all" ? [] : (profile?.scenes ?? []).filter((id) => PROBE.includes(id)), key)
        .toEqual([]);
    }
  });

  it("keeps the two dark profiles scene-comparable across scale", () => {
    // The invariant the file states for itself, re-asserted because W25 is the
    // first change to touch both dark lists at once.
    const at = (key: string): readonly string[] => {
      const scenes = MATRIX.profiles.find((profile) => profile.key === key)?.scenes;
      return scenes === undefined || scenes === "all" ? [] : scenes;
    };
    expect(at("apple-macos-26.5-2x-dark-standard")).toEqual(at("apple-macos-26.5-1x-dark-standard"));
  });
});

describe("W25's probe backgrounds and shapes cost no new generator", () => {
  it("declares every probe background in a kind the harness already draws", () => {
    // A new background KIND is a Swift change, and a Swift change is a rebuild,
    // and a rebuild re-signs the bundle ad hoc and invalidates the screen
    // recording grant until a human re-toggles it. Every backdrop this set adds
    // is an existing generator at another parameter, which costs none of that.
    const kinds = new Set(["solid", "checkerboard", "impulse", "synthetic-photo", "text-rows"]);
    for (const [id, background] of Object.entries(MATRIX.backgrounds)) {
      // No `startsWith("$comment")` escape here on purpose: `backgrounds`
      // decodes as a map of specs on the native side, so a comment key in it is
      // a phantom background rather than a comment, and this is where that says
      // so. The probe set's rationale lives at the root beside `$comment-tints`.
      expect(kinds.has(background.kind), `${id}: ${background.kind}`).toBe(true);
    }
  });

  it("holds the size sweep's aspect ratio and radius fraction across the new spans", () => {
    // The sweep varies the short side and nothing else. A shape family that
    // also changed aspect or corner fraction with span would confound the size
    // law's argument with the two shape axes S2 pins separately.
    for (const id of ["rrect-48", "rrect-64", "rrect-80", "rrect-ml"]) {
      const shape = MATRIX.components[id] as { size: readonly number[]; radius?: number };
      const [long, short] = [shape.size[0] ?? 0, shape.size[1] ?? 0];
      expect(long / short, `${id}: aspect`).toBeCloseTo(1.75, 2);
      expect((shape.radius ?? 0) / short, `${id}: radius fraction`).toBeCloseTo(0.211, 2);
    }
  });
});
