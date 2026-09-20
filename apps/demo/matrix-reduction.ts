/**
 * The calibration matrix, reduced at build time to the rows this page can show.
 *
 * `packages/calibration/results/matrix.json` is committed evidence and grows by
 * rule: a refit moves a material profile document's bytes, so the next canonical
 * run APPENDS a generation of rows beside the old ones rather than rewriting
 * them, and a wave that reads the pitch ladder as probe rows appends those too.
 * At 0.19.0 it was 55.8 MB; W30's read and split left it past 66. The page
 * imported the whole file through one JSON import to reach the few hundred rows
 * that carry a figure, and at that size the import crossed a hard conversion
 * limit in the test loader's Rust bridge — `test/calibration.test.ts` stopped
 * LOADING, before a case ran, while `pnpm --filter demo build` went on
 * succeeding because the bundler's loader is not the test runner's (claims
 * §5.159 §6b; charter W30 Decision Log 5 (c)).
 *
 * The fix is the one W30 G1's split already pointed at when it retired the
 * `capturedAt` tie-break and derived the shipped hashes at build time: the page
 * does not need the file, it needs the rows for the scenes it offers with the
 * fields it prints. This plugin performs that projection in Node, where reading
 * 66 MB is a `readFileSync`, and hands the page a module of a few hundred
 * kilobytes. **The page's figures do not depend on the file's size again** —
 * `test/matrix-reduction.test.ts` asserts every displayed figure against the
 * whole-file read, which is the assertion that makes this a projection rather
 * than a second source of truth.
 *
 * Three filters, each of them a rule the page already had:
 *
 *  - **The scenes the picker offers**, taken from `REFERENCE_SCENES` itself
 *    rather than from a second list. That module derives the picker's scenes
 *    from `apps/reference-apple/scenes.json` — dropping probe scenes, the
 *    recovered-inactive ones and the pressed pair — and it imports nothing but
 *    that file, so the build can evaluate it directly and the two cannot
 *    disagree.
 *  - **The current generation**, by the same `capturePath` clause
 *    `calibration.ts` reads and `adopted-thresholds.test.ts` gates on: every
 *    document a row names must be on disk at the bytes the row records. A cell
 *    whose documents have moved and has not been re-read yet drops out and the
 *    page renders a labelled empty slot, which is what it already does for a
 *    scene with no cell — a stale figure presented as current is the one outcome
 *    worth avoiding.
 *  - **The fields `figuresOf` prints**, and the key fields the page prints
 *    beside them. Everything else in a cell — forty-odd metrics per axis, the
 *    native readings, the shadow and tier-coherence axes — belongs to the gate
 *    and to the ledger, not to this page.
 *
 * `capturePath` is projected rather than resolved into a boolean, so
 * `calibration.ts` goes on deciding for itself which generation a row is. The
 * filter above means the answer is currently always yes; it is the page's rule
 * and it stays the page's to apply.
 *
 * `MATRIX_CELL_COUNT` is the WHOLE file's row count, not the reduction's,
 * because the sentence it appears in is about the matrix and not about this
 * module.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import type { Plugin } from "vite";

import { shippedDocumentHashes } from "./shipped-documents.ts";
import { REFERENCE_SCENES } from "./src/site/scenes.ts";

const MODULE_ID = "virtual:vitrea-matrix-reduction";

/** Vite's convention: a resolved virtual module id is prefixed with a NUL byte. */
const RESOLVED_ID = `\0${MODULE_ID}`;

const MATRIX = fileURLToPath(
  new URL("../../packages/calibration/results/matrix.json", import.meta.url),
);

/** The metrics `figuresOf` reads, per axis. Nothing else is projected. */
const PROJECTED = {
  shape: ["silhouetteIoU", "contourDistanceMean", "contourDistanceP95"],
  perceptual: ["ssimMean", "oklabDeltaEMean"],
  material: ["luminanceSlopeNative", "luminanceSlopeWeb"],
  shadow: ["falloffSigmaNative", "falloffSigmaWeb"],
} as const;

/** The clause `calibration.ts` and `adopted-thresholds.test.ts` both read. */
const DOCUMENT_CLAUSE = /(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g;

interface Metric {
  readonly value: number;
  readonly units: string;
}

export interface SourceCell {
  readonly key: {
    readonly profileKey: string;
    readonly sceneId: string;
    readonly web: Record<string, string>;
  };
  readonly tier: string;
  readonly fixtureSet: string;
  readonly capturedAt: string;
  readonly shape?: Record<string, Metric | string>;
  readonly perceptual?: Record<string, Metric | string>;
  readonly material?: Record<string, Metric | string>;
  readonly shadow?: Record<string, Metric | string>;
}

export interface ReducedCell {
  readonly key: {
    readonly profileKey: string;
    readonly sceneId: string;
    readonly web: {
      readonly engine: string;
      readonly engineVersion: string;
      readonly renderer: string;
      readonly samplingBackend: string;
      readonly gpuAdapter: string;
      readonly capturePath: string;
    };
  };
  readonly tier: string;
  readonly fixtureSet: string;
  readonly capturedAt: string;
  readonly shape?: Record<string, Metric>;
  readonly perceptual?: Record<string, Metric>;
  readonly material?: Record<string, Metric>;
  readonly shadow?: Record<string, Metric>;
}

export function atAShippedDocument(
  capturePath: string,
  hashes: Record<string, string>,
): boolean {
  const named = [...capturePath.matchAll(DOCUMENT_CLAUSE)];
  return named.length > 0 && named.every((clause) => hashes[clause[1] ?? ""] === clause[2]);
}

const axis = (
  source: Record<string, Metric | string> | undefined,
  names: readonly string[],
): Record<string, Metric> | undefined => {
  const out: Record<string, Metric> = {};
  for (const name of names) {
    const found = source?.[name];
    if (typeof found === "object" && found !== null) out[name] = found;
  }
  return Object.keys(out).length === 0 ? undefined : out;
};

/** One cell, projected onto what the page prints. */
export function project(cell: SourceCell): ReducedCell {
  const web = cell.key.web;
  const shape = axis(cell.shape, PROJECTED.shape);
  const perceptual = axis(cell.perceptual, PROJECTED.perceptual);
  const material = axis(cell.material, PROJECTED.material);
  const shadow = axis(cell.shadow, PROJECTED.shadow);
  return {
    key: {
      profileKey: cell.key.profileKey,
      sceneId: cell.key.sceneId,
      web: {
        engine: web["engine"] ?? "",
        engineVersion: web["engineVersion"] ?? "",
        renderer: web["renderer"] ?? "",
        samplingBackend: web["samplingBackend"] ?? "",
        gpuAdapter: web["gpuAdapter"] ?? "",
        capturePath: web["capturePath"] ?? "",
      },
    },
    tier: cell.tier,
    fixtureSet: cell.fixtureSet,
    capturedAt: cell.capturedAt,
    ...(shape === undefined ? {} : { shape }),
    ...(perceptual === undefined ? {} : { perceptual }),
    ...(material === undefined ? {} : { material }),
    ...(shadow === undefined ? {} : { shadow }),
  };
}

/** Whether the page can show this row at all: the two filters, stated once. */
export function displayed(cell: SourceCell, hashes: Record<string, string>): boolean {
  return (
    REFERENCE_SCENE_IDS.has(cell.key.sceneId) &&
    atAShippedDocument(cell.key.web["capturePath"] ?? "", hashes)
  );
}

export const REFERENCE_SCENE_IDS = new Set(REFERENCE_SCENES.map((scene) => scene.id));

export function reduceMatrix(): {
  readonly cells: readonly ReducedCell[];
  readonly matrixCellCount: number;
} {
  const hashes = shippedDocumentHashes();
  const source = JSON.parse(readFileSync(MATRIX, "utf8")) as { cells: readonly SourceCell[] };
  return {
    cells: source.cells.filter((cell) => displayed(cell, hashes)).map(project),
    matrixCellCount: source.cells.length,
  };
}

export function matrixReduction(): Plugin {
  return {
    name: "vitrea-matrix-reduction",
    resolveId(id) {
      return id === MODULE_ID ? RESOLVED_ID : null;
    },
    load(id) {
      if (id !== RESOLVED_ID) return null;
      const { cells, matrixCellCount } = reduceMatrix();
      return (
        `export const CELLS = ${JSON.stringify(cells)};\n` +
        `export const MATRIX_CELL_COUNT = ${matrixCellCount};\n`
      );
    },
  };
}
