/**
 * The build-time reduction is a PROJECTION of the current matrix union, not a
 * second source of truth (W30 G3b; charter Decision Log 5 (c), claims §5.159b;
 * W40 G0, claims §5.189).
 *
 * The frozen matrix and the index's current generation files are read here
 * directly, without the production store or its key serializer. Their rows are
 * independently key-sorted and checked against the reducer. The macOS 26.5 and
 * glass 0.5 part of the reduction is also pinned to `demo-before.json`, captured
 * from the old 1,893-row monolith BEFORE migration, including the ordered
 * projected cells and every figure. A loader that skips a file or changes the
 * output's order cannot validate itself through the same mistaken read.
 *
 * The glass 0.25 part entered at W43 G3 (iii) (charter clause 13, X45; claims
 * §5.201) and has no pre-migration baseline, so it is pinned by this file's own
 * oracle: the generation files the index names, the profile documents hashed
 * here, the picker's scenes, and the figures `figuresOf` prints off the raw row.
 * None of those goes through the reducer's `displayed` or `project`.
 */

import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  atADisplayedPosition,
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
const PROFILES = fileURLToPath(new URL("../../../packages/calibration/profiles/", import.meta.url));
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
const UNION = [
  ...rowsIn(join(RESULTS, "matrix.json")),
  ...[...new Set(Object.values(INDEX.currentByProfile))]
    .flatMap((name) => rowsIn(join(RESULTS, "generations", name))),
].sort((a, b) => key(a) < key(b) ? -1 : key(a) > key(b) ? 1 : 0);
// The page's positions (W43 X45, claims §5.201), by the key's own trailing token rather than
// the reducer's parser: no slider token (macOS 26.5), glass 0.5 or glass 0.25.
const glassOf = (profileKey: string): number | undefined => {
  const token = /-glass(\d+(?:\.\d+)?)$/.exec(profileKey)?.[1];
  return token === undefined ? undefined : Number(token);
};
const BEFORE_POSITIONS: readonly (number | undefined)[] = [undefined, 0.5];
const atBefore = (cell: { readonly key: { readonly profileKey: string } }): boolean =>
  BEFORE_POSITIONS.includes(glassOf(cell.key.profileKey));
const atClearer = (cell: { readonly key: { readonly profileKey: string } }): boolean =>
  glassOf(cell.key.profileKey) === 0.25;
const FILE = {
  cells: UNION.filter((cell) => atBefore(cell) || atClearer(cell)),
};

/** A cell's identity in the current union: the page has no other way to name one. */
const identity = (cell: { readonly key: { readonly profileKey: string; readonly sceneId: string;
  readonly web: Record<string, string> }; readonly tier: string }): string =>
  [cell.key.profileKey, cell.key.sceneId, cell.tier, cell.key.web["capturePath"]].join("|");

describe("the reduction against the independently read current union", () => {
  const hashes = shippedDocumentHashes();
  const kept = FILE.cells.filter((cell) => displayed(cell, hashes));

  it("preserves the exact pre-migration projection, order and figures at 26.5 and 0.5", () => {
    // The glass 0.25 rows joined the page at W43 G3 (iii); everything the page printed before
    // them is still printed, cell for cell and in the same order, with the same figures.
    expect(BEFORE.matrixCellCount).toBe(1893);
    expect(BEFORE.cells.length).toBe(411);
    expect(UNION.filter(atBefore).length).toBe(BEFORE.matrixCellCount);
    expect(reduceMatrix().cells.filter(atBefore)).toEqual(BEFORE.cells);
  });

  it("names its glass positions: 26.5, 0.5 and 0.25 reach the page, nothing else does", () => {
    // The union holds exactly those three today, so the allowlist is read directly as well:
    // a later slider position, or a macOS 27 key with no glass token, must not pass it.
    expect(new Set(UNION.map((cell) => glassOf(cell.key.profileKey))))
      .toEqual(new Set([undefined, 0.5, 0.25]));
    const { cells } = reduceMatrix();
    expect(new Set(cells.map((cell) => glassOf(cell.key.profileKey))))
      .toEqual(new Set([undefined, 0.5, 0.25]));
    expect(atADisplayedPosition("apple-macos-27.0-1x-light-standard-glass0.25")).toBe(true);
    expect(atADisplayedPosition("apple-macos-27.0-1x-light-standard-glass0.75")).toBe(false);
    expect(atADisplayedPosition("apple-macos-27.0-1x-light-standard")).toBe(false);
  });

  it("counts the whole current union, every position", () => {
    expect(UNION.length).toBe(1893 + 656 + 468);
    expect(reduceMatrix().matrixCellCount).toBe(UNION.length);
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
    expect(MEASURED_CELL_COUNT).toBe(UNION.length);
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

/**
 * The glass 0.25 cells, which entered the page at W43 G3 (iii) (charter clause 13, X45; claims
 * §5.201) and have no pre-migration baseline to be pinned to.
 *
 * So they are pinned by this file's own oracle, none of which goes through the reducer: the
 * generation files `index.json` names for the four 0.25 profiles, the profile documents hashed
 * here rather than by `shippedDocumentHashes`, the scenes the picker offers, and the figures
 * `figuresOf` prints off the raw row rather than off `project`'s output.
 */
describe("the glass 0.25 cells against this file's own oracle", () => {
  const CLEARER_ROWS_BY_PROFILE = {
    "apple-macos-27.0-1x-dark-standard-glass0.25": 24,
    "apple-macos-27.0-1x-light-standard-glass0.25": 64,
    "apple-macos-27.0-2x-dark-standard-glass0.25": 24,
    "apple-macos-27.0-2x-light-standard-glass0.25": 64,
  };
  const onDisk: Readonly<Record<string, string>> = Object.fromEntries(
    readdirSync(PROFILES)
      .filter((file) => file.endsWith(".json"))
      .map((file) => [
        `packages/calibration/profiles/${file}`,
        createHash("sha256").update(readFileSync(join(PROFILES, file))).digest("hex").slice(0, 12),
      ]),
  );
  const documentOf = (scheme: "light" | "dark", receded = false): string =>
    `packages/calibration/profiles/apple-macos-27.0-1x-${scheme}-standard-glass0.25`
    + `${receded ? "-receded" : ""}.json`;
  const CLAUSE = /(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g;
  const KEY_FIELDS = [
    "engine", "engineVersion", "renderer", "samplingBackend", "gpuAdapter",
  ] as const;
  const expected = UNION.filter(atClearer).filter((cell) => {
    if (!REFERENCE_SCENE_IDS.has(cell.key.sceneId)) return false;
    const named = [...(cell.key.web["capturePath"] ?? "").matchAll(CLAUSE)];
    return named.length > 0 && named.every((clause) => onDisk[clause[1] ?? ""] === clause[2]);
  });
  const reduced = reduceMatrix().cells.filter(atClearer);

  it("is read from the two generations the index names for the 0.25 profiles", () => {
    // A receded-only reseal shares its active hash with retired rows and names the pair
    // (W49a, claims §5.215). Both filename forms must still name the shipped document bytes;
    // the row oracle below independently checks the complete pair, not just the active alias.
    const files = Object.keys(CLEARER_ROWS_BY_PROFILE).map((key) => INDEX.currentByProfile[key]);
    expect(new Set(files).size).toBe(2);
    for (const scheme of ["light", "dark"] as const) {
      const active = onDisk[documentOf(scheme)];
      const receded = onDisk[documentOf(scheme, true)];
      for (const scale of [1, 2]) {
        const file = INDEX.currentByProfile[`apple-macos-27.0-${scale}x-${scheme}-standard-glass0.25`];
        expect([`${active}.json`, `${active}-${receded}.json`]).toContain(file);
      }
    }
    expect(UNION.filter(atClearer).length).toBe(656 + 468);
  });

  it("keeps the picker's scenes at the shipped 0.25 documents, in the union's order", () => {
    expect(reduced.map(identity)).toEqual(expected.map(identity));
    const byProfile: Record<string, number> = {};
    for (const cell of reduced) {
      byProfile[cell.key.profileKey] = (byProfile[cell.key.profileKey] ?? 0) + 1;
    }
    expect(byProfile).toEqual(CLEARER_ROWS_BY_PROFILE);
    expect(reduced.length).toBe(176);
  });

  it("names a 0.25 document, and only 0.25 documents, on every cell", () => {
    for (const cell of reduced) {
      const named = [...cell.key.web.capturePath.matchAll(CLAUSE)].map((clause) => clause[1]);
      const scheme = cell.key.profileKey.includes("-dark-") ? "dark" : "light";
      expect(named[0], identity(cell)).toBe(documentOf(scheme));
      for (const document of named.slice(1)) {
        expect(document, identity(cell)).toBe(documentOf(scheme, true));
      }
    }
  });

  it("prints every figure the raw row carries, and the key it was measured under", () => {
    const rows = new Map(expected.map((cell) => [identity(cell), cell]));
    for (const cell of reduced) {
      const row = rows.get(identity(cell));
      if (row === undefined) throw new Error(`no raw row for ${identity(cell)}`);
      expect(figuresOf(cell as unknown as Cell), identity(cell))
        .toEqual(figuresOf(row as unknown as Cell));
      expect([cell.tier, cell.fixtureSet, cell.capturedAt], identity(cell))
        .toEqual([row.tier, row.fixtureSet, row.capturedAt]);
      for (const field of KEY_FIELDS) {
        expect(cell.key.web[field], `${identity(cell)} ${field}`).toBe(row.key.web[field]);
      }
    }
  });
});
