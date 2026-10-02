/**
 * The calibration matrix, reduced at build time to the rows this page can show.
 *
 * `packages/calibration/results/matrix.json` was one growing file through W39:
 * new document bytes appended rows, and the splitter retired the old generation.
 * The 69 MB import crossed the test loader's JSON conversion limit before a
 * test ran (claims §5.159 §6b; charter W30 Decision Log 5 (c)). W40 keeps the
 * frozen macOS 26.5 rows there and stores each current macOS 27 generation in
 * an indexed file. `loadCurrentRows` assembles their key-sorted union in Node;
 * this plugin projects only the rows and fields the page can show. The page
 * never imports the large JSON envelope into the test loader. Its independent
 * test reads the authoritative files directly and pins the projection against
 * the exact pre-migration output (W40 G0, claims §5.189).
 *
 * Three filters, each of them a rule the page already had:
 *
 *  - **The scenes the picker offers**, taken from `REFERENCE_SCENES` itself
 *    rather than from a second list. That module derives the picker's scenes
 *    from `apps/reference-apple/scenes.json` — dropping probe scenes, the
 *    recovered-inactive ones and the pressed pair — and it imports nothing but
 *    that file, so the build can evaluate it directly and the two cannot
 *    disagree.
 *  - **A reading at the shipped documents**, by the same `capturePath` clause
 *    `calibration.ts` reads and `adopted-thresholds.test.ts` gates on: every
 *    document a row names must be on disk at the bytes the row records. The
 *    store selects the current generation per profile; if its documents move
 *    before the next capture, the page still drops its stale cells and renders
 *    labelled empty slots rather than presenting stale figures as current.
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
 * `MATRIX_CELL_COUNT` is the current union's row count (frozen plus indexed
 * current generations) at the page's glass positions, not the reduction's: the
 * sentence it appears in is about the measured matrix, not just the rows this
 * page displays.
 *
 * **The page names its glass positions** (W43 X45, claims §5.201). Since W43
 * G3 (ii) the union holds macOS 27 rows at two slider positions, glass 0.5 and
 * glass 0.25, and every figure and sentence on this page describes the 0.5
 * material. A reduction that read the union without naming a position would
 * print 0.25 rows under the 0.5 material's description and count them in its
 * matrix. So both the count and the reduction read only `DISPLAYED_POSITIONS`;
 * the 0.25 material reaches the page when the page says which position it shows.
 */

import type { Plugin } from "vite";

import { keyPosition } from "../../packages/calibration/src/material-selection.ts";
import { loadCurrentRows } from "../../packages/calibration/src/matrix-store.ts";
import { shippedDocumentHashes } from "./shipped-documents.ts";
import { REFERENCE_SCENES } from "./src/site/scenes.ts";

const MODULE_ID = "virtual:vitrea-matrix-reduction";

/** Vite's convention: a resolved virtual module id is prefixed with a NUL byte. */
const RESOLVED_ID = `\0${MODULE_ID}`;

/**
 * The metrics `figuresOf` reads, per axis. Nothing else is projected.
 *
 * The two `chromaStructureRatio*` entries are W31 G4's (claims §5.165 §4), on
 * exactly the rule W30 G4 added the shadow pair under: a page that prints a
 * cell's figures and omits the axis its own material just changed is printing
 * the figures that happened to exist. They are optional schema-5 fields that
 * entered with W31 G0's instrument, so a macOS 26.5 row carries neither and
 * `axis()` drops what is not there — which is the right behaviour and not a
 * degradation, because those rows are frozen evidence read before the
 * instrument existed.
 */
const PROJECTED = {
  shape: ["silhouetteIoU", "contourDistanceMean", "contourDistanceP95"],
  perceptual: ["ssimMean", "oklabDeltaEMean"],
  material: [
    "luminanceSlopeNative",
    "luminanceSlopeWeb",
    "chromaStructureRatioNative",
    "chromaStructureRatioWeb",
  ],
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

/** macOS 26.5, which has no slider, and macOS 27 at the system default, glass 0.5. */
export const DISPLAYED_POSITIONS: readonly {
  readonly osVersion: string;
  readonly glass?: number;
}[] = [{ osVersion: "26.5" }, { osVersion: "27.0", glass: 0.5 }];

/** A key the profile grammar does not parse is kept, so the page's other rules decide it. */
export function atADisplayedPosition(profileKey: string): boolean {
  const position = keyPosition(profileKey);
  return position === undefined || DISPLAYED_POSITIONS.some(
    (shown) => shown.osVersion === position.osVersion && shown.glass === position.glass,
  );
}

export function reduceMatrix(): {
  readonly cells: readonly ReducedCell[];
  readonly matrixCellCount: number;
} {
  const hashes = shippedDocumentHashes();
  // CellResult's complete axis types lack an index signature; SourceCell is the
  // narrower projection view over those same parsed rows.
  const source = (loadCurrentRows() as unknown as readonly SourceCell[])
    .filter((cell) => atADisplayedPosition(cell.key.profileKey));
  return {
    cells: source.filter((cell) => displayed(cell, hashes)).map(project),
    matrixCellCount: source.length,
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
