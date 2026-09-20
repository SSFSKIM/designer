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
 */

import matrix from "../../../../packages/calibration/results/matrix.json";

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
    };
  };
  readonly tier: string;
  readonly fixtureSet: string;
  readonly capturedAt: string;
  readonly shape?: Record<string, Metric | string>;
  readonly perceptual?: Record<string, Metric | string>;
  readonly material?: Record<string, Metric | string>;
}

const cells = (matrix as { readonly cells: readonly Cell[] }).cells;

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
 * material that surface is made of: the matrix now holds both generations of
 * rows and picking the macOS 26.5 one would print a number measured against a
 * material this page no longer draws, which is the same defect the comment
 * above records being fixed at W21 G3, one axis along.
 */
const PRIMARY_PROFILE_KEY_BY_SCHEME = {
  light: "apple-macos-27.0-1x-light-standard-glass0.5",
  dark: "apple-macos-27.0-1x-dark-standard-glass0.5",
} as const;
const PRIMARY_TIER = "texture";

/** Lower sorts first. Ties fall to the newest reading — see `reportsFor`. */
function primacy(report: CellReport, scheme: "light" | "dark"): number {
  return (
    (report.profileKey === PRIMARY_PROFILE_KEY_BY_SCHEME[scheme] ? 0 : 2) +
    (report.tier === PRIMARY_TIER ? 0 : 1)
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
 * **The tie-break is the capture time, newest first, and it became load-bearing
 * at W29 G4.** A cell's key carries the material profile document's hash, so a
 * refit appends a generation of rows beside the old one and never rewrites it
 * (which is the project's rule about recorded numbers, and why the matrix grows
 * at all). One profile and one tier therefore no longer name one cell: macOS
 * 27's light texture rows exist twice over, once at W29 G3's documents and once
 * at W29 G3b's re-sealed ones. The page draws the material the runtime ships,
 * which is the latest, so the latest reading is the one that speaks for it —
 * and "which generation is the shipped one" is a question the matrix answers
 * only by timestamp today (`specs/tech-debt-tracker.md`, the matrix-size entry,
 * whose generation-split option would make it answerable by name).
 */
export function reportsFor(
  sceneId: string,
  scheme: "light" | "dark" = "light",
): readonly CellReport[] {
  const found = REPORTS_BY_SCENE.get(sceneId);
  if (found === undefined) return [];
  return [...found].sort(
    (a, b) =>
      primacy(a, scheme) - primacy(b, scheme) || b.capturedAt.localeCompare(a.capturedAt),
  );
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
      figures: figuresOf(cell),
    };
    const existing = bySceneId.get(report.sceneId);
    if (existing === undefined) bySceneId.set(report.sceneId, [report]);
    else existing.push(report);
  }
  return bySceneId;
})();

export const MEASURED_CELL_COUNT = cells.length;
