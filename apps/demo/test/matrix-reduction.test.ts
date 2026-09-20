/**
 * The build-time reduction is a PROJECTION of the matrix, not a second source of
 * truth (W30 G3b; charter Decision Log 5 (c), claims §5.159b).
 *
 * `calibration.ts` used to import `packages/calibration/results/matrix.json`
 * whole. It no longer can — the file is past the size the test loader's JSON
 * bridge converts, and it will only grow — so `matrix-reduction.ts` projects it
 * at build time onto the rows this page can show and the fields it prints. That
 * is a correctness risk of a specific shape: a projection can silently drop a
 * row, keep a stale one, or print a figure that is not the one in the file, and
 * none of those would fail a type check or a render.
 *
 * So the whole file is read here, in Node, where reading 66 MB is a
 * `readFileSync` — and every figure the page can display is asserted against it.
 * The suite that could not load the matrix and the check that the matrix is
 * faithfully reduced are therefore not in tension: the loader was the bundler's
 * JSON import, and this is a file read.
 */

import { readFileSync } from "node:fs";
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

const MATRIX = fileURLToPath(
  new URL("../../../packages/calibration/results/matrix.json", import.meta.url),
);

const FILE = JSON.parse(readFileSync(MATRIX, "utf8")) as { cells: readonly SourceCell[] };

/** A cell's identity in the file: the page has no other way to name one. */
const identity = (cell: { readonly key: { readonly profileKey: string; readonly sceneId: string;
  readonly web: Record<string, string> }; readonly tier: string }): string =>
  [cell.key.profileKey, cell.key.sceneId, cell.tier, cell.key.web["capturePath"]].join("|");

describe("the reduction against the whole file", () => {
  const hashes = shippedDocumentHashes();
  const kept = FILE.cells.filter((cell) => displayed(cell, hashes));

  it("keeps exactly the rows the page's two rules select", () => {
    const { cells } = reduceMatrix();
    expect(cells.length).toBe(kept.length);
    expect(cells.map(identity)).toEqual(kept.map(identity));
  });

  it("drops nothing the page could have shown", () => {
    // The complement, stated as a reason per dropped row rather than as a count:
    // a row is dropped because its scene is not in the picker, or because a
    // document it names is not on disk at the bytes it records. Any third reason
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

  it("carries every figure at the value the file records", () => {
    // The assertion the whole plugin exists to be held to. `project` is applied
    // to the file's own cell and compared to what the page was built with, field
    // for field, so a metric renamed, rounded or read off the wrong axis fails
    // here rather than being published as a fidelity claim.
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
    // metric any row in the file carries, on both sides of the projection. If
    // the projection drops one the page reads, the two figure lists differ.
    const maximal: Record<"shape" | "perceptual" | "material", Record<string, unknown>> = {
      shape: {},
      perceptual: {},
      material: {},
    };
    for (const cell of FILE.cells) {
      for (const axis of ["shape", "perceptual", "material"] as const) {
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

  it("reports the file's own row count, not the reduction's", () => {
    expect(MEASURED_CELL_COUNT).toBe(FILE.cells.length);
  });

  it("leaves the page with a figure for every scene the file measured and the picker offers", () => {
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
