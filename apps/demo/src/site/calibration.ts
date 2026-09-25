/**
 * The fidelity figures, read from the calibration matrix at build time.
 *
 * The page never states a number of its own. Every figure comes from the
 * current calibration matrix: the frozen macOS 26.5 rows in `matrix.json` and
 * the indexed current macOS 27 generations, keyed by the cell that produced
 * it. A scene without a cell renders a labelled empty slot rather than a
 * borrowed number. The §Calibration claims rule is structural: "all fidelity
 * claims cite the profile and cell, never 'pixel-identical to Apple'."
 *
 * **What it reads is a build-time REDUCTION of that current union, not its
 * files** (W30 G3b; charter Decision Log 5 (c), claims §5.159b; W40 G0,
 * claims §5.189). The old 69 MB whole-file import crossed a hard limit in the
 * test loader's JSON bridge (§5.159 §6b). `../../matrix-reduction.ts` reads
 * the union in Node, where large file reads are safe, then projects the scenes
 * the picker offers, the readings at shipped document bytes and the fields
 * `figuresOf` prints. `test/matrix-reduction.test.ts` checks every displayed
 * figure against an independent direct-file union and pins the complete
 * projected output to the pre-migration baseline.
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
   * `atAShippedDocument`: the index selects the current generation, while
   * this bit checks whether its recorded document bytes are still shipped.
   */
  readonly atShippedDocument: boolean;
  readonly figures: readonly Figure[];
}

interface Metric {
  readonly value: number;
  readonly units: string;
}

export interface Cell {
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
  readonly shadow?: Record<string, Metric | string>;
}

const cells: readonly Cell[] = CELLS;

const metric = (axis: Record<string, Metric | string> | undefined, name: string): Metric | null => {
  const found = axis?.[name];
  return typeof found === "object" && found !== null ? found : null;
};

const fixed = (value: number, places: number): string => value.toFixed(places);

/**
 * Exported for `test/matrix-reduction.test.ts`, which pins the build-time
 * reduction's `PROJECTED` to this function by running both over the same cell
 * (review closure; claims §5.159b §10, finding 10). The names here and the
 * names the plugin keeps were two lists that had to agree by hand, and a figure
 * added here without the other would simply stop appearing on the page.
 */
export function figuresOf(cell: Cell): readonly Figure[] {
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
  /*
   * The body's chroma-to-structure ratio, added at W31 G4 (claims §5.165 §4).
   *
   * 0.21.0's operator is the one this page had no figure for: the body's
   * CHROMATICITY restored toward the blurred backdrop's at a held linear luma.
   * None of the figures above can see it. The silhouette and contour rows are
   * geometry; SSIM is computed on luma; ΔE mean is a whole-capture distance in
   * which a body's hue is a fraction of a rim's and an exterior's; the
   * luminance slope is a level. A body that went from a flat warm grey to a
   * coloured one would move none of them enough to notice, which is the same
   * hole W30 G4 found on the shadow axis one wave earlier.
   *
   * The pair is printed rather than the ratio, on this page's own idiom — the
   * shadow σ and the luminance slope are both native/web pairs, and a reader who
   * wants the wave's statistic divides one by the other. The ratio of each side
   * is the interior's per-pixel OKLab chroma spread over its own luma spread, so
   * a body that blurs more but keeps its hues reads the same as one that blurs
   * less: it is scale-free in the deviations, which is what makes the two sides
   * comparable across a blur vitrea and the reference do not share.
   *
   * What the pair does NOT say, and the note says so: it is scale-free in both
   * directions, so a body that lost its chroma and its structure together reads
   * the same as one that kept both. The gate that closes that is
   * `adopted-thresholds.test.ts`'s M2, on the structure this page does not show.
   */
  add("Body chroma-to-structure, native", metric(cell.material, "chromaStructureRatioNative"), 3);
  add(
    "Body chroma-to-structure, web",
    metric(cell.material, "chromaStructureRatioWeb"),
    3,
    "The interior's per-pixel OKLab chroma spread over its own luma spread, so the blur the two sides do not share cancels. Web against native is the statistic 0.21.0's body-chroma retention was fitted on; it is scale-free in the deviations, so it is also blind to a body that loses chroma and structure together, and the gate pairs it with a bound on the structure. A macOS 26.5 row carries neither figure: the instrument entered the schema at W31.",
  );
  /*
   * The outer shadow's fitted falloff width, added at W30 G4 (claims §5.160).
   *
   * The wave that 0.20.0 carries graded this shadow's σ by the casting span —
   * one number became a line — and not one of the seven figures above could see
   * it: they read the silhouette, the interior and the transmission, and the
   * shadow is outside all three. On this bed the operator moves `falloffSigmaWeb`
   * from a flat 14 px to 20.3 px at a span of 160 and down to 11.0 px at 32,
   * against natives of 17.3 and (the thin regime) under 2. A page that prints a
   * cell's figures and omits the axis its own material just changed is printing
   * the figures that happened to exist.
   *
   * This fit is a reading of the composite, not the material's blur law.
   * The macOS 27 documents have no lift after W33; attributing the thin-span
   * fit to the lift's width would describe a term the default no longer draws.
   * The frozen macOS 26.5 material retains that term. The independently fitted
   * native and web edge widths are diagnostics, not C1's adopted shape metric;
   * the material's own law is `outerShadowSigmaPx`, evaluated on `/laws/`.
   */
  add("Shadow falloff sigma, native", metric(cell.shadow, "falloffSigmaNative"), 2);
  add(
    "Shadow falloff sigma, web",
    metric(cell.shadow, "falloffSigmaWeb"),
    2,
    "One blurred edge fitted to the whole exterior departure, not the material's own blur constant. The macOS 27 material has no lift; macOS 26.5 retains its blurred lift, which can dominate this composite reading at thin spans. These fitted widths remain diagnostics, not the adopted exterior-shape bound. The material's own law is evaluated on the /laws/ page.",
  );
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
 * A cell's `capturePath` names the active document and, for inactive scenes
 * posed separately, the receded one, each with twelve hex characters of its
 * bytes' SHA-256. A refit changes those bytes. The current union selects one
 * indexed generation per macOS 27 profile (plus the frozen 26.5 rows); a new
 * capture becomes a new immutable generation file, not rows appended to
 * `matrix.json`. Selection alone does not promise the documents on disk still
 * match: between a refit and its capture, this check keeps stale numbers off
 * the page. A row is at the shipped material only when EVERY named document
 * still has the bytes recorded in that row.
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
 * **The generation is a term in the order, not a timestamp** (W30 G1,
 * amended by its review closure). Before W40 the single matrix file could
 * briefly hold the newly appended generation beside the old one pending the
 * splitter; `capturedAt` was an unreliable way to choose which reading drew
 * the shipped material. The current union now reads only the index's current
 * generation per macOS 27 profile, but `primacy` still checks the named
 * document bytes: a refit can change them before the next capture publishes.
 * `capturedAt` is still printed as the measurement time, never used to decide
 * which material's reading counts.
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
 * Every displayable cell, keyed by scene, in the current union's key order.
 * Order is not a claim here — `reportsFor` decides the primary cell.
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
 * How many cells the current matrix union holds, not the reduction's count.
 *
 * The union is the frozen macOS 26.5 rows plus one indexed current generation
 * per macOS 27 profile. The reduction below it counts only what the page can
 * print; conflating the two would under-report the evidence it is built on.
 */
export const MEASURED_CELL_COUNT = MATRIX_CELL_COUNT;

/** How many of those rows this page was built with. Printed beside the count above. */
export const DISPLAYABLE_CELL_COUNT = cells.length;
