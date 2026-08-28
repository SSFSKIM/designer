/**
 * The adopted fidelity gate.
 *
 * `docs/doperpowers/specs/c9a-fidelity-claims.md` §5 ("Proposed thresholds — for
 * the human gate") set per-cell thresholds and left them explicitly as
 * proposals. The user **adopted them as proposed on 2026-08-26**, closing
 * `c9d-release-checklist.md` §2.2 and, with it, parent acceptance #7's "inside
 * declared thresholds". This file is what adoption means operationally: the
 * numbers stop being prose and become a test over the committed
 * `results/matrix.json`, so a matrix regeneration that pushes a cell past one of
 * them fails CI instead of waiting for whoever next reads the claims doc.
 *
 * The tables below are transcribed from §5 row for row and in §5's own order,
 * and they are the only copy of these numbers anywhere in the repo — the point
 * is that a reviewer can hold this file next to §5 and diff the two by eye.
 * Every bound is bounded by §5's *holdout* column rather than its calibration
 * one, deliberately: a gate that calibration passes and holdout fails would
 * certify overfitting rather than prevent it.
 *
 * ## The second adoption: W1 G3 (2026-08-29)
 *
 * The wave's W1 child re-measured a widened bed — six native profiles across
 * colour scheme, backing scale and accessibility state — and the user adopted
 * three decisions on it (`2026-08-28-post-v1-wave.md`, Decision Log 9):
 *
 *   1. **The 2× light-standard tables are gated**, on the same doctrine and from
 *      the same holdout column. They are `*_2X_LIGHT` below, and §5's rationale
 *      for why they are not simply the 1× numbers is in the claims doc's §5.1.
 *   2. **Cross-tier coherence is gated from the matrix**, not from prose. Schema
 *      4 puts a `coherence` axis on the dom-tier cell, so the row that used to be
 *      a tripwire in this file is now an assertion over real numbers.
 *   3. **The four provisional profiles stay ungated.** Named below, with the
 *      reason, rather than left out.
 *
 * `results/matrix.json` is now W1's six-profile measurement — the v1 60-cell
 * matrix it supersedes is in git history. The 1× tables are unchanged by that
 * promotion, in every digit: the widened bed re-measured the profile they were
 * set on rather than replacing it.
 *
 * ## What §5 does not gate, and why it is absent here
 *
 * Stated because an absent assertion is otherwise indistinguishable from a
 * forgotten one, and each of these is a decision §5 argues for:
 *
 *   - **Four profiles are provisional, not gated.** See `UNGATED_PROFILES`.
 *   - **The material axis is not gated.** The sub-metrics that would identify the
 *     material are either unidentifiable on this fixture set (blur sigma, §6.1)
 *     or below the capture's own quantisation (the light-scheme rim, §6.2). A
 *     threshold on a quantity the fixtures cannot resolve is a number that gets
 *     met by accident. Its `interiorMeanWeb` field is read here for one purpose
 *     only — cross-checking the coherence ratio, which is a cross-tier quantity,
 *     not a fidelity one.
 *   - **The motion axis is not gated.** No frame sequences were captured on the
 *     native side, and the still `pressed` fixtures cannot substitute: they are
 *     byte-identical to their rest counterparts (§6.3), so those cells measure
 *     vitrea's pressed pose against Apple's rest pose. They are still gated on
 *     the shape and perceptual axes — §5's own worst-case figures include them —
 *     but no press claim rests on that.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

// ---------------------------------------------------------------------------
// §5, transcribed
// ---------------------------------------------------------------------------

type GateRow = readonly [
  axis: "shape" | "perceptual",
  metric: string,
  bound: "≥" | "≤",
  threshold: number,
];

/** Texture tier, `apple-macos-26.5-1x-light-standard`, cell as claims §1. */
const TEXTURE_TIER_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.82],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 5.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.88],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.07],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.17],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.11],
];

/** Dom tier, same profile, Chromium, `renderer: css`. */
const DOM_TIER_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 4.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.90],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.08],
];

/**
 * Texture tier, `apple-macos-26.5-2x-light-standard`. Claims §5.1, adopted
 * 2026-08-29; transcribed row for row exactly as the 1× tables are.
 *
 * Not the 1× numbers, and not uniformly looser than them. The three movements
 * each have a measured reason, stated once in §5.1 and once here because a
 * reader of this file should not have to open another to know whether a bound
 * was reasoned or copied: the **colour bounds are the 1× bounds unchanged**
 * (the measurements are — holdout ΔE mean 0.0546 at 2× against 0.0548 at 1×);
 * the **contour bounds are the 1× bounds doubled** (contour distance is a
 * device-pixel quantity, and the geometry error did not move); the **SSIM bound
 * is tighter than 1×'s** (SSIM reads systematically +0.014 higher at 2×, so
 * importing the 1× number would have been slack at this scale).
 */
const TEXTURE_TIER_2X_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 5.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 10.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.93],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.07],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.17],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.12],
];

/** Dom tier, `apple-macos-26.5-2x-light-standard`, Chromium, `renderer: css`. */
const DOM_TIER_2X_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 4.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 8.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.92],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.08],
];

/**
 * §5's coherence rows — a property of the *pair*, so they are gated off the
 * dom-tier cell's `coherence` axis, which is where schema 4 records them.
 *
 * The same two bounds carry both light profiles: the quantities are scale-free
 * (a whole-canvas ΔE and a ratio of two levels), and W1 measured them agreeing
 * across the two scales to the third decimal. So there is one table here rather
 * than a 1× and a 2× copy, and a divergence between the scales would show up as
 * a failure rather than as two tables drifting apart.
 *
 * **This replaces a tripwire.** Through schema 3 the cross-tier ΔE was not
 * derivable from anything committed — it is a web-against-web comparison of two
 * PNGs, and `web-captures/` is not in the repository — so this file carried the
 * number in prose plus a test asserting that no cell had a coherence axis, to
 * fire the day one did. W1 G3 made it derivable (Decision Log 9), and the
 * assertions below are what that tripwire was waiting for.
 */
const COHERENCE_ROWS = {
  crossTierOklabDeltaEMean: { bound: "≤", threshold: 0.05 },
  interiorLevelRatioGpuOverCss: { min: 0.8, max: 1.25 },
} as const;

/**
 * §5's well-conditioned-cell predicate, which qualifies the **shape rows only**
 * (every table carries it, unchanged).
 *
 * The luminance-delta extractor finds the component by differencing against its
 * backdrop, so it loses any part of the material whose level coincides with the
 * backdrop's. Where that happens the IoU and contour figures describe the
 * extractor rather than the geometry, and gating them would be gating the
 * instrument. `silhouetteAreaNative` is on the record in every cell (schema 3
 * onward) precisely so this can be machine-checked.
 */
const WELL_CONDITIONED_AREA_RATIO = 0.95;

// ---------------------------------------------------------------------------
// The cells the gate covers — stated, not discovered
// ---------------------------------------------------------------------------

/** The renderer each tier is captured through. §5's dom tables name their own. */
const RENDERER_OF_TIER = { texture: "webgpu", dom: "css" } as const;

interface GatedProfile {
  readonly profileKey: string;
  readonly texture: readonly GateRow[];
  readonly dom: readonly GateRow[];
  /** The table constants' own names, so a failure message points at the source. */
  readonly names: { readonly texture: string; readonly dom: string };
}

const GATED_PROFILES: readonly GatedProfile[] = [
  {
    profileKey: "apple-macos-26.5-1x-light-standard",
    texture: TEXTURE_TIER_LIGHT,
    dom: DOM_TIER_LIGHT,
    names: { texture: "TEXTURE_TIER_LIGHT", dom: "DOM_TIER_LIGHT" },
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    texture: TEXTURE_TIER_2X_LIGHT,
    dom: DOM_TIER_2X_LIGHT,
    names: { texture: "TEXTURE_TIER_2X_LIGHT", dom: "DOM_TIER_2X_LIGHT" },
  },
];

/**
 * The four profiles the gate leaves, and the one reason all four share.
 *
 * Each declares **calibration scenes only** — no validation and no holdout — so
 * the column every bound in this file is bounded by does not exist for them.
 * Adopting a threshold from a calibration-only measurement would certify
 * overfitting in the doctrine's own words, which is v1's dark-provisional
 * reasoning transferred unchanged (wave spec Decision Log 9, approved by the
 * user 2026-08-29 together with the two adoptions above).
 *
 * They are not unmeasured. Every one of them is in the matrix on both tiers,
 * their figures are tabulated in `2026-08-29-w1-g3-measurement.md`, and their
 * coherence axis is asserted **present** below — measured, not gated. The
 * approved close is to give them a split: the split is declared per scene, so
 * extending their native scene sets to include a validation and a holdout scene
 * earns them one, and gating follows from that rather than from a decision to
 * relax the doctrine.
 */
const UNGATED_PROFILES = [
  "apple-macos-26.5-1x-dark-standard",
  "apple-macos-26.5-1x-light-increased-contrast",
  "apple-macos-26.5-1x-light-reduced-transparency",
  "apple-macos-26.5-2x-dark-standard",
] as const;

/**
 * The whole matrix, and how it partitions — asserted per profile rather than as
 * a bare total, so a profile going missing cannot be absorbed by another's cells
 * arriving. Six native profiles × two web tiers.
 */
const MATRIX_PARTITION: Readonly<Record<string, number>> = {
  "apple-macos-26.5-1x-dark-standard": 12,
  "apple-macos-26.5-1x-light-increased-contrast": 8,
  "apple-macos-26.5-1x-light-reduced-transparency": 8,
  "apple-macos-26.5-1x-light-standard": 48,
  "apple-macos-26.5-2x-dark-standard": 12,
  "apple-macos-26.5-2x-light-standard": 48,
};

const MATRIX_CELLS = 136;
const GATED_CELLS_PER_TIER = 24;

/**
 * The one gated scene that carries no shape and no material axis, on either
 * tier and at either scale — so two of each gated profile's 48 cells have
 * nothing for the shape rows to gate.
 *
 * Not a fault and not a gap in the gate: over a solid backdrop of the material's
 * own tone the reference sits within the extractor's 0.02 threshold of its
 * background, so the native silhouette is empty and `cli/measure.ts` records the
 * cell with its perceptual axis alone rather than inventing a shape. Named here
 * so the shape rows' cell count is derived from it instead of being a bare
 * number nobody can check.
 */
const NO_SHAPE_AXIS_SCENES = ["light-solid__rrect-md__rest"] as const;

/**
 * Every cell the well-conditioned predicate excludes, across the whole matrix —
 * gated or not, named rather than dropped. All six are in ungated profiles.
 *
 * Two families, one mechanism. In the **1× dark** profile a dark material over a
 * black-and-white checkerboard is genuinely indistinguishable from the black
 * squares it covers, so the native silhouette comes back at 4324 px where the
 * declared capsule is 4865, with holes punched through its own interior. In the
 * **increased-contrast** profile the failure runs the other way: the extractor
 * loses the brightened material over the checkerboard's white squares, and both
 * of that profile's checkerboard scenes recover only 53–57% of their declared
 * area.
 *
 * Two things this list is asserted for, beyond its own contents. **The light
 * gate excludes nothing** — every gated shape row, at both scales, is gated on a
 * well-conditioned cell. And **2× repaired the dark cell**: the same scene that
 * fails at 1× passes the predicate at 2× (recovery 100.2%, IoU 0.9538), which is
 * what makes the 1× exclusion an instrument-scoped one rather than a statement
 * about the material.
 */
const PREDICATE_EXCLUDES = [
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
] as const;

// ---------------------------------------------------------------------------
// Reading the committed artifacts
// ---------------------------------------------------------------------------

interface MetricValue {
  readonly value: number;
  readonly units: string;
}

type AxisReport = Readonly<Record<string, MetricValue | string | undefined>>;

interface Cell {
  readonly key: {
    readonly profileKey: string;
    readonly sceneId: string;
    readonly web: { readonly engine: string; readonly renderer: string };
  };
  readonly fixtureSet: string;
  readonly tier: "texture" | "dom";
  readonly shape?: AxisReport;
  readonly perceptual?: AxisReport;
  readonly material?: AxisReport;
  readonly coherence?: AxisReport;
}

interface ResultMatrix {
  readonly schemaVersion: number;
  readonly cells: readonly Cell[];
}

/** A rounded rect; a capsule is one whose radius is half its short side. */
interface ShapeSpec {
  readonly kind: "capsule" | "rrect";
  readonly size: readonly [number, number];
  readonly radius?: number;
  readonly offset?: readonly [number, number];
}
interface GroupSpec {
  readonly kind: "group";
  readonly items: readonly ShapeSpec[];
  readonly spacing: number;
}
interface StackSpec {
  readonly kind: "stack";
  readonly base: ShapeSpec;
  readonly over: ShapeSpec;
}
type ComponentSpec = ShapeSpec | GroupSpec | StackSpec;

interface SceneMatrix {
  readonly components: Readonly<Record<string, ComponentSpec>>;
  readonly scenes: readonly { readonly id: string; readonly component: string }[];
}

const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

const MATRIX = readJson<ResultMatrix>(resolve(PACKAGE_ROOT, "results", "matrix.json"));
const SCENES = readJson<SceneMatrix>(resolve(REPO_ROOT, "apps", "reference-apple", "scenes.json"));

/** `tier / set / scene / profile` — every failure message starts with this. */
function name(cell: Cell): string {
  return `${cell.tier} / ${cell.fixtureSet} / ${cell.key.sceneId} / ${cell.key.profileKey}`;
}

function reading(
  cell: Cell,
  axis: "shape" | "perceptual" | "material" | "coherence",
  field: string,
): number {
  const entry = cell[axis]?.[field];
  if (typeof entry !== "object") {
    // A metric that vanished from the schema must not read as a cell that
    // passed. Absent axes are handled by the caller, which knows which cells
    // legitimately have none; an absent *field* inside a present axis is a
    // gate that silently stopped checking something.
    throw new Error(`${name(cell)}: no ${axis}.${field} on the record`);
  }
  return entry.value;
}

// ---------------------------------------------------------------------------
// The declared component area — the predicate's right-hand side
// ---------------------------------------------------------------------------

/** A rectangle less its four corner offcuts, each of which removes r² − πr²/4. */
function shapeArea(spec: ShapeSpec): number {
  const [width, height] = spec.size;
  const radius = spec.kind === "capsule" ? Math.min(width, height) / 2 : (spec.radius ?? 0);
  return width * height - (4 - Math.PI) * radius * radius;
}

function declaredComponentArea(componentId: string): number {
  const spec = SCENES.components[componentId];
  if (spec === undefined) throw new Error(`scenes.json declares no component "${componentId}"`);

  if (spec.kind === "group") {
    /*
     * The sum of the members, unmerged. Claims §4.5 measured this: at the
     * declared spacing of 12 the reference's own silhouette is three separate
     * bodies, so a union would overstate the declared area and loosen the
     * predicate on exactly the cell it was measured on.
     */
    return spec.items.reduce((sum, item) => sum + shapeArea(item), 0);
  }

  if (spec.kind === "stack") {
    // The overlay sits wholly inside the base, so the union IS the base. Checked
    // rather than assumed: an overlay that escaped would make this an undercount,
    // and an undercount loosens the predicate instead of failing it.
    const [baseWidth, baseHeight] = spec.base.size;
    const [overWidth, overHeight] = spec.over.size;
    const [offsetX, offsetY] = spec.over.offset ?? [0, 0];
    const inset =
      spec.base.kind === "capsule"
        ? Math.min(baseWidth, baseHeight) / 2
        : (spec.base.radius ?? 0);
    const contained =
      Math.abs(offsetX) + overWidth / 2 <= baseWidth / 2 - inset &&
      Math.abs(offsetY) + overHeight / 2 <= baseHeight / 2 - inset;
    if (!contained) {
      throw new Error(
        `"${componentId}"'s overlay is no longer inside its base, so the declared ` +
          `area is a union this test does not compute. Compute it, or split the scene.`,
      );
    }
    return shapeArea(spec.base);
  }

  return shapeArea(spec);
}

const COMPONENT_OF_SCENE = new Map(SCENES.scenes.map((scene) => [scene.id, scene.component]));

function declaredAreaOf(cell: Cell): number {
  const componentId = COMPONENT_OF_SCENE.get(cell.key.sceneId);
  if (componentId === undefined) {
    throw new Error(`${name(cell)}: scenes.json declares no such scene`);
  }
  return declaredComponentArea(componentId);
}

/**
 * §5's predicate, evaluated — in **declared units**.
 *
 * `scenes.json` declares component sizes in points, and a 2× cell's silhouette
 * is measured in device pixels, so the declared area is scaled by the square of
 * the profile's backing scale before the comparison. Without that a 2× cell
 * would clear a 1× area threshold roughly four times over and the predicate
 * would stop biting at exactly the scale where the extractor is most likely to
 * be doing something interesting.
 */
function backingScaleOf(profileKey: string): number {
  const scale = /-(\d+)x-/.exec(profileKey)?.[1];
  if (scale === undefined) throw new Error(`${profileKey}: no backing scale in the profile key`);
  return Number(scale);
}

function isWellConditioned(cell: Cell): boolean {
  if (cell.shape === undefined) return true;
  const scale = backingScaleOf(cell.key.profileKey);
  return (
    reading(cell, "shape", "silhouetteAreaNative") >=
    WELL_CONDITIONED_AREA_RATIO * declaredAreaOf(cell) * scale * scale
  );
}

// ---------------------------------------------------------------------------
// Selection
// ---------------------------------------------------------------------------

const cellsOf = (profileKey: string, tier?: "texture" | "dom"): readonly Cell[] =>
  MATRIX.cells.filter(
    (cell) => cell.key.profileKey === profileKey && (tier === undefined || cell.tier === tier),
  );

// ---------------------------------------------------------------------------

describe("the adopted fidelity gate (claims §5, adopted 2026-08-26 and 2026-08-29)", () => {
  it("reads the schema it was written against", () => {
    // The field names below were verified against schema 4. A schema bump is a
    // reason to re-verify them, not to trust that they survived.
    expect(MATRIX.schemaVersion).toBe(4);
  });

  it("covers exactly the two light profiles, and names the four it leaves", () => {
    const perProfile = new Map<string, number>();
    for (const cell of MATRIX.cells) {
      perProfile.set(cell.key.profileKey, (perProfile.get(cell.key.profileKey) ?? 0) + 1);
    }
    expect(Object.fromEntries([...perProfile].sort())).toEqual(MATRIX_PARTITION);

    // Total, in both directions: the gated profiles plus the ungated ones
    // account for the whole matrix, so no cell is outside the statement.
    expect(MATRIX.cells).toHaveLength(MATRIX_CELLS);
    expect(Object.values(MATRIX_PARTITION).reduce((a, b) => a + b, 0)).toBe(MATRIX_CELLS);
    expect(
      [...GATED_PROFILES.map((profile) => profile.profileKey), ...UNGATED_PROFILES].sort(),
    ).toEqual(Object.keys(MATRIX_PARTITION).sort());

    for (const { profileKey } of GATED_PROFILES) {
      for (const tier of ["texture", "dom"] as const) {
        const cells = cellsOf(profileKey, tier);
        expect(cells, `${profileKey} / ${tier}`).toHaveLength(GATED_CELLS_PER_TIER);
        // And every gated cell is the engine and renderer §5's tables name. A
        // cell captured through anything else is not the cell the thresholds
        // were set on.
        for (const cell of cells) {
          expect(cell.key.web.engine, name(cell)).toBe("chromium");
          expect(cell.key.web.renderer, name(cell)).toBe(RENDERER_OF_TIER[tier]);
        }
      }
    }
  });

  for (const profile of GATED_PROFILES) {
    for (const tier of ["texture", "dom"] as const) {
      const table = profile[tier];
      const constant = profile.names[tier];
      it(`gates all ${GATED_CELLS_PER_TIER} ${tier}-tier ${profile.profileKey} cells against ${constant}`, () => {
        const cells = cellsOf(profile.profileKey, tier);
        const shapeCells = cells.filter((cell) => cell.shape !== undefined);

        // The shape rows gate one cell fewer than the perceptual rows, for the
        // one named reason. Derived from the name so a second such scene cannot
        // arrive unnoticed and shrink the gate by one.
        expect(shapeCells).toHaveLength(GATED_CELLS_PER_TIER - NO_SHAPE_AXIS_SCENES.length);
        expect(
          cells
            .filter((cell) => cell.shape === undefined)
            .map((cell) => cell.key.sceneId)
            .sort(),
        ).toEqual([...NO_SHAPE_AXIS_SCENES].sort());

        for (const [axis, metric, comparison, threshold] of table) {
          // Shape rows carry the well-conditioned predicate; perceptual rows do not.
          const applicable =
            axis === "shape" ? shapeCells.filter((cell) => isWellConditioned(cell)) : cells;
          expect(
            applicable,
            `${tier} / ${metric}: the gate must cover every applicable cell`,
          ).toHaveLength(
            axis === "shape"
              ? GATED_CELLS_PER_TIER - NO_SHAPE_AXIS_SCENES.length
              : GATED_CELLS_PER_TIER,
          );

          for (const cell of applicable) {
            const measured = reading(cell, axis, metric);
            const because = `${name(cell)}: ${metric} = ${measured.toPrecision(5)}, gate ${comparison} ${threshold}`;
            if (comparison === "≥") expect(measured, because).toBeGreaterThanOrEqual(threshold);
            else expect(measured, because).toBeLessThanOrEqual(threshold);
          }
        }
      });
    }
  }

  it("machine-checks the well-conditioned predicate and names every cell it excludes", () => {
    const excluded = MATRIX.cells.filter((cell) => !isWellConditioned(cell)).map(name).sort();
    expect(excluded, "cells the shape rows skip, per claims §5's predicate").toEqual([
      ...PREDICATE_EXCLUDES,
    ]);

    // The predicate is not passing by being vacuous. It has to bite somewhere —
    // §5 adopted it *because* one canonical cell fails it, and a predicate that
    // excluded nothing at all would mean the areas had stopped being measured.
    expect(excluded.length).toBeGreaterThan(0);
    for (const cell of MATRIX.cells.filter((candidate) => !isWellConditioned(candidate))) {
      expect(
        UNGATED_PROFILES as readonly string[],
        `${name(cell)} is excluded, so it must be outside the gate`,
      ).toContain(cell.key.profileKey);
      // The exclusion is legible and not merely a boolean: the area it turns on
      // is on the record and below the predicate's right-hand side.
      const scale = backingScaleOf(cell.key.profileKey);
      expect(reading(cell, "shape", "silhouetteAreaNative")).toBeLessThan(
        WELL_CONDITIONED_AREA_RATIO * declaredAreaOf(cell) * scale * scale,
      );
    }

    // The 1× dark exclusion is scoped to the instrument at 1×, not to the
    // material: the same scene at 2× recovers the whole declared capsule and is
    // gated like any other cell. Asserted so a future reader cannot mistake the
    // exclusion for a property of dark glass over a checkerboard.
    for (const cell of cellsOf("apple-macos-26.5-2x-dark-standard")) {
      if (cell.key.sceneId !== "checkerboard__capsule-button__rest") continue;
      expect(isWellConditioned(cell), `${name(cell)}: 2× repairs the 1× exclusion`).toBe(true);
    }
  });

  for (const { profileKey } of GATED_PROFILES) {
    it(`enforces the coherence rows over ${profileKey}, from the matrix`, () => {
      const dom = cellsOf(profileKey, "dom");
      const { min, max } = COHERENCE_ROWS.interiorLevelRatioGpuOverCss;
      const deltaE = COHERENCE_ROWS.crossTierOklabDeltaEMean;

      // Coherence is a property of the pair, so it is present on every dom cell
      // whose texture twin was captured — which, in this matrix, is all of them.
      expect(dom.filter((cell) => cell.coherence !== undefined)).toHaveLength(
        GATED_CELLS_PER_TIER,
      );

      let ratios = 0;
      for (const cell of dom) {
        const measured = reading(cell, "coherence", "crossTierOklabDeltaEMean");
        expect(
          measured,
          `${name(cell)}: cross-tier ΔE mean = ${measured.toPrecision(4)}, gate ${deltaE.bound} ${deltaE.threshold}`,
        ).toBeLessThanOrEqual(deltaE.threshold);

        // The ratio is absent exactly where there is no interior to sample, and
        // that is the same one scene the shape axis is absent on. Absent, never
        // zeroed — so its absence is checked against the reason, not skipped.
        if (cell.coherence?.interiorLevelRatioGpuOverCss === undefined) {
          expect([...NO_SHAPE_AXIS_SCENES], "a scene with no interior to sample").toContain(
            cell.key.sceneId,
          );
          continue;
        }
        const ratio = reading(cell, "coherence", "interiorLevelRatioGpuOverCss");
        const because = `${name(cell)}: interior level gpu ÷ css = ${ratio.toPrecision(4)}, gate ${min}…${max}`;
        expect(ratio, because).toBeGreaterThanOrEqual(min);
        expect(ratio, because).toBeLessThanOrEqual(max);
        ratios += 1;
      }
      expect(ratios, "every scene with a material on both tiers is a coherence pair").toBe(
        GATED_CELLS_PER_TIER - NO_SHAPE_AXIS_SCENES.length,
      );
    });

    it(`cross-checks ${profileKey}'s recorded ratio against the two tiers' own levels`, () => {
      /*
       * The coherence axis is written by `cli/measure.ts` during the dom-tier
       * run, from the texture capture on disk. The same ratio is independently
       * derivable from the matrix itself — each tier's `material.interiorMeanWeb`
       * is that tier's interior level under the *native* silhouette, which is the
       * identical quantity over the identical mask.
       *
       * Deriving it a second way and requiring the two to agree is what keeps the
       * axis from being a number the gate trusts because the gate has no other
       * source for it.
       */
      const twin = new Map(
        cellsOf(profileKey, "texture").map((cell) => [cell.key.sceneId, cell] as const),
      );
      let checked = 0;
      for (const cell of cellsOf(profileKey, "dom")) {
        if (cell.coherence?.interiorLevelRatioGpuOverCss === undefined) continue;
        const texture = twin.get(cell.key.sceneId);
        expect(texture, `${cell.key.sceneId}: coherence is a property of the pair`).toBeDefined();
        if (texture === undefined) continue;
        const derived =
          reading(texture, "material", "interiorMeanWeb") /
          reading(cell, "material", "interiorMeanWeb");
        expect(
          reading(cell, "coherence", "interiorLevelRatioGpuOverCss"),
          `${name(cell)}: the recorded ratio must be the two tiers' own levels, divided`,
        ).toBeCloseTo(derived, 9);
        checked += 1;
      }
      expect(checked).toBe(GATED_CELLS_PER_TIER - NO_SHAPE_AXIS_SCENES.length);
    });
  }

  it("measures coherence on the four ungated profiles without gating it", () => {
    /*
     * Decision Log 9 (wave spec, user-approved 2026-08-29): these profiles are
     * calibration-only, so no bound over them can be bounded by a holdout column,
     * and a gate set from calibration alone would certify overfitting. They are
     * measured all the same — the figures are in W1's G3 report, and a reader who
     * wants to know how far apart the tiers draw a dark or a high-contrast scene
     * has the number on the record rather than a gap.
     *
     * What IS asserted is presence, in both directions: the axis is on every one
     * of their dom cells, and the ratio is absent on exactly the cells whose
     * native silhouette is empty. A profile that silently stopped carrying
     * coherence would otherwise look the same as one that was never gated.
     */
    for (const profileKey of UNGATED_PROFILES) {
      const dom = cellsOf(profileKey, "dom");
      expect(dom.length, profileKey).toBeGreaterThan(0);
      for (const cell of dom) {
        expect(cell.coherence, `${name(cell)}: coherence measured, not gated`).toBeDefined();
        expect(
          cell.coherence?.interiorLevelRatioGpuOverCss === undefined,
          `${name(cell)}: the ratio exists exactly where a shared interior does`,
        ).toBe(cell.material === undefined);
      }
    }
  });

  it("carries a coherence axis on the dom tier and nowhere else", () => {
    // The pair has one number, so it lives on one side of the pair. A texture
    // cell that grew one would mean two records of the same quantity, which can
    // disagree — and the direction (GPU ÷ CSS) would then be ambiguous.
    for (const cell of MATRIX.cells) {
      if (cell.tier === "dom") continue;
      expect(cell, `${name(cell)}: coherence belongs to the dom-tier cell`).not.toHaveProperty(
        "coherence",
      );
    }
  });
});
