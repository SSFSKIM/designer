/**
 * The build-time reduction is a PROJECTION of the current matrix union, not a
 * second source of truth (W30 G3b; charter Decision Log 5 (c), claims §5.159b;
 * W40 G0, claims §5.189).
 *
 * The frozen matrix and the index's current generation files are read here
 * directly, without the production store or its key serializer. Their rows are
 * independently key-sorted and checked against the reducer. The complete
 * reduction is also pinned to `demo-before.json`, captured from the old
 * 1,893-row monolith BEFORE migration, including the ordered projected cells
 * and every figure. A loader that skips a file or changes the output's order
 * cannot validate itself through the same mistaken read.
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  displayed,
  project,
  reduceMatrix,
  REFERENCE_SCENE_IDS,
  type SourceCell,
} from "../matrix-reduction.ts";
import { shippedDocumentHashes } from "../shipped-documents.ts";
import {
  type Cell,
  figuresOf,
  MEASURED_CELL_COUNT,
  REPORTS_BY_SCENE,
} from "../src/site/calibration";

const RESULTS = fileURLToPath(new URL("../../../packages/calibration/results/", import.meta.url));
const BEFORE = JSON.parse(readFileSync(
  join(RESULTS, "2026-09-26-w40-g0-generations/demo-before.json"), "utf8",
)) as {
  readonly cells: readonly ReturnType<typeof project>[];
  readonly matrixCellCount: number;
};
const INDEX = JSON.parse(readFileSync(join(RESULTS, "generations/index.json"), "utf8")) as {
  readonly currentByProfile: Readonly<Record<string, string>>;
};

// This oracle reads the authoritative files directly. It neither calls the store nor
// imports its key serializer, so a loader that loses or reorders a cell cannot bless itself.
const escape = (field: string): string => field.replace(/%/g, "%25").replace(/\|/g, "%7C");
const key = (cell: SourceCell): string => [
  cell.key.profileKey,
  cell.key.sceneId,
  cell.key.web["engine"],
  cell.key.web["engineVersion"],
  cell.key.web["renderer"],
  cell.key.web["samplingBackend"],
  cell.key.web["gpuAdapter"],
  cell.key.web["colorSpace"],
  cell.key.web["capturePath"],
].map((field) => escape(field ?? "")).join("|");
const rowsIn = (path: string): readonly SourceCell[] =>
  (JSON.parse(readFileSync(path, "utf8")) as { cells: readonly SourceCell[] }).cells;
const FILE = {
  cells: [
    ...rowsIn(join(RESULTS, "matrix.json")),
    ...[...new Set(Object.values(INDEX.currentByProfile))]
      .flatMap((name) => rowsIn(join(RESULTS, "generations", name))),
  ].sort((a, b) => key(a) < key(b) ? -1 : key(a) > key(b) ? 1 : 0),
};

/** A cell's identity in the current union: the page has no other way to name one. */
const identity = (cell: { readonly key: { readonly profileKey: string; readonly sceneId: string;
  readonly web: Record<string, string> }; readonly tier: string }): string =>
  [cell.key.profileKey, cell.key.sceneId, cell.tier, cell.key.web["capturePath"]].join("|");

describe("the reduction against the independently read current union", () => {
  const hashes = shippedDocumentHashes();
  const kept = FILE.cells.filter((cell) => displayed(cell, hashes));

  it("preserves the exact pre-migration projection, order, figures and row count", () => {
    expect(BEFORE.matrixCellCount).toBe(1893);
    expect(BEFORE.cells.length).toBe(411);
    expect(FILE.cells.length).toBe(1893);
    expect(reduceMatrix()).toEqual(BEFORE);
  });

  it("keeps exactly the rows the page's two rules select", () => {
    const { cells } = reduceMatrix();
    expect(cells.length).toBe(kept.length);
    expect(cells.map(identity)).toEqual(kept.map(identity));
  });

  it("drops nothing the page could have shown", () => {
    // A row drops because its scene is not in the picker, or because a
    // document it names is no longer on disk at those bytes. A third reason
    // would be a defect in the projection.
    for (const cell of FILE.cells) {
      if (displayed(cell, hashes)) continue;
      const path = cell.key.web["capturePath"] ?? "";
      const named = [...path.matchAll(/(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g)];
      const superseded = named.length === 0 || named.some((c) => hashes[c[1] ?? ""] !== c[2]);
      expect(
        !REFERENCE_SCENE_IDS.has(cell.key.sceneId) || superseded,
        `${cell.key.sceneId} / ${cell.key.profileKey} / ${cell.tier}`,
      ).toBe(true);
    }
  });

  it("carries every figure at the value the current rows record", () => {
    // The assertion the whole plugin exists to be held to. `project` is applied
    // to an independently loaded cell and compared to the page's reduction,
    // field for field, so a metric renamed, rounded or read off the wrong axis
    // fails here rather than being published as a fidelity claim.
    const { cells } = reduceMatrix();
    const byIdentity = new Map(cells.map((cell) => [identity(cell), cell]));
    expect(byIdentity.size).toBe(cells.length);
    for (const cell of kept) {
      expect(byIdentity.get(identity(cell)), identity(cell)).toEqual(project(cell));
    }
  });

  it("projects every metric `figuresOf` prints, over a cell carrying all of them", () => {
    // `PROJECTED` and `figuresOf` are two lists of metric names that have to
    // agree, and nothing made them (review closure; claims §5.159b §10, finding
    // 10). A figure added to the page and not to the plugin would not fail a
    // type check, would not fail a render, and would simply never appear.
    //
    // Pinned functionally rather than by name: a synthetic cell carrying every
    // metric any current row carries, on both sides of the projection. If
    // the projection drops one the page reads, the two figure lists differ.
    const maximal: Record<
      "shape" | "perceptual" | "material" | "shadow",
      Record<string, unknown>
    > = {
      shape: {},
      perceptual: {},
      material: {},
      shadow: {},
    };
    for (const cell of FILE.cells) {
      for (const axis of ["shape", "perceptual", "material", "shadow"] as const) {
        for (const [name, value] of Object.entries(cell[axis] ?? {})) {
          if (typeof value === "object" && value !== null) maximal[axis][name] ??= value;
        }
      }
    }
    const everyMetric = Object.values(maximal)
      .reduce((sum, axis) => sum + Object.keys(axis).length, 0);
    expect(everyMetric).toBeGreaterThan(40);

    const source = { ...(FILE.cells[0] as SourceCell), ...maximal } as SourceCell;
    const whole = figuresOf(source as unknown as Cell);
    const projected = figuresOf(project(source) as unknown as Cell);
    expect(whole.length).toBeGreaterThan(0);
    expect(projected).toEqual(whole);
  });

  it("reports the current union’s row count, not the reduction’s", () => {
    expect(MEASURED_CELL_COUNT).toBe(FILE.cells.length);
  });

  it("leaves a figure for every scene measured in the union and offered in the picker", () => {
    // The end-to-end statement: the reduction is upstream of `REPORTS_BY_SCENE`,
    // so this is what a reader would notice if a row went missing — a scene the
    // bed measured showing an empty slot.
    const measured = new Set(
      kept.filter((cell) => cell.shape !== undefined || cell.perceptual !== undefined)
        .map((cell) => cell.key.sceneId),
    );
    expect(measured.size).toBeGreaterThan(0);
    for (const sceneId of measured) {
      expect(REPORTS_BY_SCENE.get(sceneId)?.length ?? 0, sceneId).toBeGreaterThan(0);
    }
  });
});
