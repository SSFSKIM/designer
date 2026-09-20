/**
 * The fidelity figures, read from the calibration matrix at build time.
 *
 * The page never states a number of its own. Every figure here comes out of
 * `packages/calibration/results/matrix.json` (X9's per-cell result matrix), keyed
 * by the cell that produced it, and a scene with no cell renders as a labelled
 * empty slot rather than as a borrowed number from a different cell. That is the
 * §Calibration claims rule made structural: "all fidelity claims cite the profile
 * and cell, never 'pixel-identical to Apple'."
 *
 * C9a's tuning run extends the same file. Nothing here needs to change when it
 * lands: more cells means more scenes with figures and fewer empty slots.
 *
 * **What it reads is a build-time REDUCTION of that file, not the file** (W30
 * G3b; charter Decision Log 5 (c), claims §5.159b). `matrix.json` is 66 MB and
 * grows by rule — a refit appends a generation of rows rather than rewriting
 * one, and W30's read appended the pitch ladder besides — and importing all of
 * it to reach the few hundred rows that carry a figure crossed a hard limit in
 * the test loader's JSON bridge (§5.159 §6b). `../../matrix-reduction.ts` does
 * the projection in Node, where reading 66 MB is a `readFileSync`, and the rules
 * it projects by are this module's own: the scenes the picker offers, the
 * generation at the documents on disk, and the fields `figuresOf` prints.
 * `test/matrix-reduction.test.ts` asserts every displayed figure against the
 * whole-file read, so the reduction is a projection and not a second source of
 * truth, and the page's figures no longer depend on the file's size.
 */

import { CELLS, MATRIX_CELL_COUNT } from "virtual:vitrea-matrix-reduction";
import { SHIPPED_DOCUMENT_HASHES } from "virtual:vitrea-shipped-documents";

export interface Figure {
  readonly label: string;
  readonly value: string;
  readonly unit: string;
  /** Set where a figure is a tuning target rather than a result. */
  readonly note?: string;
}

export interface CellReport {
  readonly sceneId: string;
  readonly profileKey: string;
  readonly engine: string;
  readonly engineVersion: string;
  readonly renderer: string;
  readonly samplingBackend: string;
  readonly gpuAdapter: string;
  readonly tier: string;
  readonly fixtureSet: string;
  readonly capturedAt: string;
  /**
   * Was this reading taken at the material profile documents that are on disk? See
   * `atAShippedDocument`: it is which GENERATION of the cell this row is, and
   * `reportsFor` ranks a shipped reading ahead of a superseded one.
   */
  readonly atShippedDocument: boolean;
  readonly figures: readonly Figure[];
}

interface Metric {
  readonly value: number;
  readonly units: string;
}

interface Cell {
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
  readonly shape?: Record<string, Metric | string>;
  readonly perceptual?: Record<string, Metric | string>;
  readonly material?: Record<string, Metric | string>;
}

const cells: readonly Cell[] = CELLS;

const metric = (axis: Record<string, Metric | string> | undefined, name: string): Metric | null => {
  const found = axis?.[name];
  return typeof found === "object" && found !== null ? found : null;
};

const fixed = (value: number, places: number): string => value.toFixed(places);

function figuresOf(cell: Cell): readonly Figure[] {
  const out: Figure[] = [];
  const add = (
    label: string,
    found: Metric | null,
    places: number,
    note?: string,
  ): void => {
    if (found === null) return;
    out.push({
      label,
      value: fixed(found.value, places),
      unit: found.units === "ratio" ? "" : found.units,
      ...(note === undefined ? {} : { note }),
    });
  };

  add("Silhouette IoU", metric(cell.shape, "silhouetteIoU"), 3);
  add("Contour distance, mean", metric(cell.shape, "contourDistanceMean"), 2);
  add("Contour distance, p95", metric(cell.shape, "contourDistanceP95"), 2);
  add("SSIM, mean", metric(cell.perceptual, "ssimMean"), 3);
  add("OKLab delta E, mean", metric(cell.perceptual, "oklabDeltaEMean"), 4);
  add(
    "Luminance slope, native",
    metric(cell.material, "luminanceSlopeNative"),
    3,
    "Not a transmission figure: this estimator is attenuated by the material's own blur, so it reads lower the busier the backdrop and the two sides are not comparable through it. C9a measured transmission by regressing interior level against backdrop level across scenes instead, and found the reference the MORE opaque of the two — the opposite of what a single slope reading implies.",
  );
  add("Luminance slope, web", metric(cell.material, "luminanceSlopeWeb"), 3);
  return out;
}

/**
 * The profile and tier the page speaks for when a scene has more than one cell.
 *
 * A scene carries up to four (two colour schemes × two tiers), and the page shows
 * one. Which one is a claim rather than an implementation detail: the headline is
 * the **texture tier under the profile of the scheme the page is drawing**,
 * because that is the tier the demo defaults to, and because a figure measured in
 * one colour scheme is not evidence about a surface drawn in the other. The dom
 * tier's figures belong to the engine's `backdrop-filter` rather than to vitrea's
 * shader math, which is why the tier half of the rule does not move.
 *
 * Naming the primary was a fix for a real defect and not a preference. Cells
 * arrive in the matrix's key-sorted order, so "the first one" was the *dark dom*
 * cell purely because "apple-macos-26.5-1x-dark-standard" sorts before
 * "…-light-standard" — a figure from the wrong profile and the wrong tier,
 * presented as the page's answer. W21 G3 made the profile half follow the
 * resolved colour scheme, which is the same rule read one step further: the
 * default is unchanged, because the page's default scheme is light.
 */
/*
 * Moved to macOS 27 at W29 G4, with the runtime's default material and with the
 * pair's fixtures. The figure beside a live surface has to be a reading of the
 * material that surface is made of: the matrix holds macOS 26.5 rows beside the
 * macOS 27 ones and picking a macOS 26.5 one would print a number measured
 * against a material this page no longer draws, which is the same defect the
 * comment above records being fixed at W21 G3, one axis along.
 */
const PRIMARY_PROFILE_KEY_BY_SCHEME = {
  light: "apple-macos-27.0-1x-light-standard-glass0.5",
  dark: "apple-macos-27.0-1x-dark-standard-glass0.5",
} as const;
const PRIMARY_TIER = "texture";

/**
 * Which generation of a cell this row is: was it read at the material profile
 * documents that are on disk?
 *
 * A cell's `capturePath` names every document the run was driven from — the active
 * one and, where the run posed its inactive scenes, the receded one — with twelve hex
 * characters of SHA-256 over the document's bytes. A refit moves those bytes, so the
 * next canonical run appends a second generation of rows beside the first instead of
 * rewriting it. A row is at the shipped material only when EVERY document it names is
 * still on disk at the bytes it records: a reading posed with a receded document
 * nobody ships is not a reading of the shipped material, whatever its active document
 * says, which is the same rule `results/2026-09-20-w30-g1-split/split-generation.py`
 * splits the file by and `adopted-thresholds.test.ts` gates on.
 */
const DOCUMENT_CLAUSE = /(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g;

function atAShippedDocument(capturePath: string): boolean {
  const named = [...capturePath.matchAll(DOCUMENT_CLAUSE)];
  return (
    named.length > 0 &&
    named.every((clause) => SHIPPED_DOCUMENT_HASHES[clause[1] ?? ""] === clause[2])
  );
}

/**
 * Lower sorts first; see `reportsFor` for what the order means.
 *
 * Three terms, most significant first: the profile of the scheme the page is drawing,
 * then the tier the page speaks for, then the generation. The weights encode that
 * precedence — a reading of the right profile on the right tier that a refit has since
 * superseded still outranks a current reading of another tier, because the tier half of
 * the rule is about *what was measured* and the generation is about *which reading of
 * it*.
 */
export function primacy(report: CellReport, scheme: "light" | "dark"): number {
  return (
    (report.profileKey === PRIMARY_PROFILE_KEY_BY_SCHEME[scheme] ? 0 : 4) +
    (report.tier === PRIMARY_TIER ? 0 : 2) +
    (report.atShippedDocument ? 0 : 1)
  );
}

/**
 * A scene's cells with the one that speaks for the given scheme first.
 *
 * A cell from the other scheme's profile still sorts in, behind: the caller shows
 * the head of the list and the head is the claim. What the caller must NOT do is
 * present a cell from the wrong scheme as this scheme's evidence — which is why
 * every report carries its own `profileKey` and the page prints it.
 *
 * **The generation is a term in the order, not a timestamp** (W30 G1, amended by
 * its review closure). A cell's key carries the material profile documents' own
 * hashes, so a refit appends a generation of rows beside the old one and never
 * rewrites it — which is the project's rule about recorded numbers, and why the
 * matrix grows at all. W29 G4 met that as two macOS 27 generations in one file and
 * broke the tie on `capturedAt`, newest first: a heuristic standing where a name
 * belonged, and the tracker's matrix-size entry said so.
 *
 * Two things replaced it and both are needed. Since W30 G1 the superseded
 * generation is moved out to
 * `packages/calibration/results/superseded/<document-sha>.json` as soon as the
 * refit that superseded it lands, so the rows this module imports are normally the
 * shipped bed already. And `primacy` ranks a row at the documents on disk ahead of
 * one that is not, so the page is right about which reading it is showing in the
 * interval a wave actually lives in — between the capture that appends a
 * generation and the split that retires the one it superseded — rather than
 * silently showing whichever of the two the file happened to list first. Which
 * documents ship is read from their bytes at build time, never transcribed.
 *
 * `capturedAt` is still carried on every report, and the page still prints it —
 * it is when the reading was taken. It is simply no longer asked to decide which
 * reading counts.
 */
export function reportsFor(
  sceneId: string,
  scheme: "light" | "dark" = "light",
): readonly CellReport[] {
  const found = REPORTS_BY_SCENE.get(sceneId);
  if (found === undefined) return [];
  return [...found].sort((a, b) => primacy(a, scheme) - primacy(b, scheme));
}

/**
 * Every measured cell, keyed by scene, in the matrix's own order. Order is not a
 * claim here — `reportsFor` is where the primary cell is decided.
 */
export const REPORTS_BY_SCENE: ReadonlyMap<string, readonly CellReport[]> = (() => {
  const bySceneId = new Map<string, CellReport[]>();
  for (const cell of cells) {
    const report: CellReport = {
      sceneId: cell.key.sceneId,
      profileKey: cell.key.profileKey,
      engine: cell.key.web.engine,
      engineVersion: cell.key.web.engineVersion,
      renderer: cell.key.web.renderer,
      samplingBackend: cell.key.web.samplingBackend,
      gpuAdapter: cell.key.web.gpuAdapter,
      tier: cell.tier,
      fixtureSet: cell.fixtureSet,
      capturedAt: cell.capturedAt,
      atShippedDocument: atAShippedDocument(cell.key.web.capturePath),
      figures: figuresOf(cell),
    };
    const existing = bySceneId.get(report.sceneId);
    if (existing === undefined) bySceneId.set(report.sceneId, [report]);
    else existing.push(report);
  }
  return bySceneId;
})();

/**
 * How many cells the result matrix holds — the FILE's count, not the
 * reduction's.
 *
 * The sentence this appears in is about the matrix: what has been measured and
 * kept, one generation per profile. The reduction below it is about what this
 * page could ever print, which is a different and smaller thing, and conflating
 * the two would make the page under-report the evidence it is built on.
 */
export const MEASURED_CELL_COUNT = MATRIX_CELL_COUNT;

/** How many of those rows this page was built with. Printed beside the count above. */
export const DISPLAYABLE_CELL_COUNT = cells.length;
