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
 * ## What §5 does not gate, and why it is absent here
 *
 * Stated because an absent assertion is otherwise indistinguishable from a
 * forgotten one, and each of these is a decision §5 argues for:
 *
 *   - **The dark profile is provisional, not gated.** It declares no validation
 *     and no holdout scenes, so nothing in it is held out, and two of its six
 *     cells cannot measure the material at all. A dark-scheme claim needs its own
 *     split before it can be gated at the light profile's level. The twelve dark
 *     cells are named below as the cells the gate leaves, not skipped silently.
 *   - **The material axis is not gated.** The sub-metrics that would identify the
 *     material are either unidentifiable on this fixture set (blur sigma, §6.1)
 *     or below the capture's own quantisation (the light-scheme rim, §6.2). A
 *     threshold on a quantity the fixtures cannot resolve is a number that gets
 *     met by accident. Its `interiorMeanWeb` field is read here for one purpose
 *     only — the coherence ratio, which is a cross-tier quantity, not a
 *     fidelity one.
 *   - **The motion axis is not gated.** No frame sequences were captured on the
 *     native side, and the still `pressed` fixtures cannot substitute: they are
 *     byte-identical to their rest counterparts (§6.3), so those cells measure
 *     vitrea's pressed pose against Apple's rest pose. They are still gated on
 *     the shape and perceptual axes — §5's own worst-case figures include them —
 *     but no press claim rests on that.
 *   - **One coherence row cannot be enforced from here at all.** See
 *     `COHERENCE_ROWS` and the last test in the file.
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
 * §5's coherence rows — a property of the *pair*, so neither tier's cell carries
 * them and both are derived across the two.
 *
 * The interior-level ratio is derivable and enforced. `material.interiorMeanWeb`
 * is each tier's own interior level measured under the **native** silhouette
 * (`cli/measure.ts` masks both sides with it, so the two tiers report over one
 * pixel set), which is exactly the quantity `cli/tier-delta.ts` divides. The
 * ratio computed here reproduces §5's tabulated range to three decimals.
 *
 * The cross-tier ΔE is not derivable from the committed matrix: it is a
 * web-against-web pixel comparison of the two tiers' PNG captures, and
 * `web-captures/` is not committed — `results/matrix.json` is the only committed
 * artifact, and schema 3 carries no coherence axis. The number is recorded here
 * so the adopted table is complete in one place, and the last test in this file
 * is the tripwire that fires when a future schema makes it enforceable.
 */
const COHERENCE_ROWS = {
  crossTierOklabDeltaEMean: { bound: "≤", threshold: 0.05 },
  interiorLevelRatioGpuOverCss: { min: 0.8, max: 1.25 },
} as const;

/**
 * §5's well-conditioned-cell predicate, which qualifies the **shape rows only**
 * (both tables carry it, unchanged).
 *
 * The luminance-delta extractor finds the component by differencing against its
 * backdrop, so it loses any part of the material whose level coincides with the
 * backdrop's. Where that happens the IoU and contour figures describe the
 * extractor rather than the geometry, and gating them would be gating the
 * instrument. `silhouetteAreaNative` is on the record in every cell (schema 3)
 * precisely so this can be machine-checked.
 */
const WELL_CONDITIONED_AREA_RATIO = 0.95;

// ---------------------------------------------------------------------------
// The cells the gate covers — stated, not discovered
// ---------------------------------------------------------------------------

const GATED_PROFILE = "apple-macos-26.5-1x-light-standard";
const PROVISIONAL_PROFILE = "apple-macos-26.5-1x-dark-standard";

/** The renderer each tier is captured through. §5's dom table names its own. */
const RENDERER_OF_TIER = { texture: "webgpu", dom: "css" } as const;

/** The whole matrix, and how it partitions. Asserted, so a shrink cannot pass. */
const MATRIX_CELLS = 60;
const GATED_CELLS_PER_TIER = 24;
const PROVISIONAL_CELLS_PER_TIER = 6;

/**
 * The one gated scene that carries no shape and no material axis, on either
 * tier — so four of the 48 gated cells' shape rows have nothing to gate.
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
 * gated or not, named rather than dropped.
 *
 * Both are the same scene on the two tiers, both in the provisional dark
 * profile, and they are the case §5 describes: a dark material over a
 * black-and-white checkerboard is genuinely indistinguishable from the black
 * squares it covers, so the native silhouette comes back at 4324 px where the
 * declared capsule is 4865, with holes punched through its own interior. **The
 * light gate excludes nothing** — every gated shape row is gated on a
 * well-conditioned cell. That is a property of today's matrix, not a
 * simplification: it is asserted below in both directions.
 */
const PREDICATE_EXCLUDES = [
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
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

function reading(cell: Cell, axis: "shape" | "perceptual" | "material", field: string): number {
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

/** §5's predicate, evaluated. Cells with no shape axis are not candidates. */
function isWellConditioned(cell: Cell): boolean {
  if (cell.shape === undefined) return true;
  return (
    reading(cell, "shape", "silhouetteAreaNative") >=
    WELL_CONDITIONED_AREA_RATIO * declaredAreaOf(cell)
  );
}

// ---------------------------------------------------------------------------
// Selection
// ---------------------------------------------------------------------------

const gated = (tier: "texture" | "dom"): readonly Cell[] =>
  MATRIX.cells.filter((cell) => cell.tier === tier && cell.key.profileKey === GATED_PROFILE);

const provisional = MATRIX.cells.filter((cell) => cell.key.profileKey === PROVISIONAL_PROFILE);

// ---------------------------------------------------------------------------

describe("the adopted fidelity gate (claims §5, adopted 2026-08-26)", () => {
  it("reads the schema it was written against", () => {
    // The field names below were verified against schema 3. A schema bump is a
    // reason to re-verify them, not to trust that they survived.
    expect(MATRIX.schemaVersion).toBe(3);
  });

  it("covers exactly the light-profile cells, and names the twelve it leaves", () => {
    // Total, in both directions: the gated cells plus the provisional ones
    // account for the whole matrix, so no cell is outside the statement.
    expect(MATRIX.cells).toHaveLength(MATRIX_CELLS);
    expect(gated("texture")).toHaveLength(GATED_CELLS_PER_TIER);
    expect(gated("dom")).toHaveLength(GATED_CELLS_PER_TIER);
    expect(provisional).toHaveLength(2 * PROVISIONAL_CELLS_PER_TIER);
    expect(gated("texture").length + gated("dom").length + provisional.length).toBe(MATRIX_CELLS);

    // And every gated cell is the engine and renderer §5's tables name. A cell
    // captured through anything else is not the cell the thresholds were set on.
    for (const tier of ["texture", "dom"] as const) {
      for (const cell of gated(tier)) {
        expect(cell.key.web.engine, name(cell)).toBe("chromium");
        expect(cell.key.web.renderer, name(cell)).toBe(RENDERER_OF_TIER[tier]);
      }
    }
  });

  for (const [tier, table, bound] of [
    ["texture", TEXTURE_TIER_LIGHT, "TEXTURE_TIER_LIGHT"],
    ["dom", DOM_TIER_LIGHT, "DOM_TIER_LIGHT"],
  ] as const) {
    it(`gates all ${GATED_CELLS_PER_TIER} ${tier}-tier light cells against ${bound}`, () => {
      const cells = gated(tier);
      const shapeCells = cells.filter((cell) => cell.shape !== undefined);

      // The shape rows gate one cell fewer than the perceptual rows, for the one
      // named reason. Derived from the name so a second such scene cannot arrive
      // unnoticed and shrink the gate by one.
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
        ).toHaveLength(axis === "shape" ? GATED_CELLS_PER_TIER - NO_SHAPE_AXIS_SCENES.length : GATED_CELLS_PER_TIER);

        for (const cell of applicable) {
          const measured = reading(cell, axis, metric);
          const because = `${name(cell)}: ${metric} = ${measured.toPrecision(5)}, gate ${comparison} ${threshold}`;
          if (comparison === "≥") expect(measured, because).toBeGreaterThanOrEqual(threshold);
          else expect(measured, because).toBeLessThanOrEqual(threshold);
        }
      }
    });
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
      expect(cell.key.profileKey, `${name(cell)} is excluded, so it must be outside the gate`).toBe(
        PROVISIONAL_PROFILE,
      );
      // The numbers §5 quotes for it, so the exclusion is legible and not merely
      // a boolean: the extractor loses 12% of the declared capsule here.
      expect(reading(cell, "shape", "silhouetteAreaNative")).toBeLessThan(
        WELL_CONDITIONED_AREA_RATIO * declaredAreaOf(cell),
      );
    }
  });

  it("holds the two tiers' interior levels inside §5's coherence ratio", () => {
    const { min, max } = COHERENCE_ROWS.interiorLevelRatioGpuOverCss;
    const byScene = new Map<string, { texture?: Cell; dom?: Cell }>();
    for (const cell of MATRIX.cells) {
      if (cell.key.profileKey !== GATED_PROFILE) continue;
      const pair = byScene.get(cell.key.sceneId) ?? {};
      if (cell.tier === "texture") pair.texture = cell;
      else pair.dom = cell;
      byScene.set(cell.key.sceneId, pair);
    }

    let pairs = 0;
    for (const [sceneId, pair] of byScene) {
      const { texture, dom } = pair;
      expect(texture, `${sceneId}: coherence is a property of the pair`).toBeDefined();
      expect(dom, `${sceneId}: coherence is a property of the pair`).toBeDefined();
      if (texture === undefined || dom === undefined) continue;
      // The material axis is absent on both tiers together, for the one named
      // scene, so a one-sided absence would be a real fault rather than a skip.
      expect(texture.material === undefined, sceneId).toBe(dom.material === undefined);
      if (texture.material === undefined) {
        expect([...NO_SHAPE_AXIS_SCENES], "a scene with no interior to sample").toContain(sceneId);
        continue;
      }

      const ratio =
        reading(texture, "material", "interiorMeanWeb") /
        reading(dom, "material", "interiorMeanWeb");
      const because = `${sceneId}: interior level gpu ÷ css = ${ratio.toPrecision(4)}, gate ${min}…${max}`;
      expect(ratio, because).toBeGreaterThanOrEqual(min);
      expect(ratio, because).toBeLessThanOrEqual(max);
      pairs += 1;
    }

    expect(pairs, "every gated scene with a material on both tiers is a coherence pair").toBe(
      GATED_CELLS_PER_TIER - NO_SHAPE_AXIS_SCENES.length,
    );
  });

  it("cannot enforce the cross-tier ΔE row from the committed matrix, and trips when it can", () => {
    /*
     * The adopted bound is ΔE mean ≤ 0.05 between the two tiers' own captures.
     * That is a web-against-web measurement with no fixture in it, which
     * `cli/tier-delta.ts` computes from two PNGs — and the PNGs live in the
     * uncommitted `web-captures/`, so nothing in the repository holds the
     * quantity. Recorded as a tripwire rather than an omission: the day a cell
     * carries a coherence axis, this fails and the row above gets wired up
     * alongside the ratio.
     */
    for (const cell of MATRIX.cells) {
      expect(
        cell,
        `${name(cell)}: a coherence axis is now on the record — enforce ` +
          `crossTierOklabDeltaEMean ${COHERENCE_ROWS.crossTierOklabDeltaEMean.bound} ` +
          `${COHERENCE_ROWS.crossTierOklabDeltaEMean.threshold} here`,
      ).not.toHaveProperty("coherence");
    }
  });
});
