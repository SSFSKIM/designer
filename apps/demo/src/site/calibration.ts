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
 * A scene now carries up to four (two colour schemes x two tiers), and the page
 * shows one. Which one is a claim rather than an implementation detail: the
 * headline is the **texture tier under the light-standard profile**, because that
 * is the tier the demo itself defaults to and the profile the runtime's own
 * constants target — the dark profile is a patch a host has to pass (C9a §4.3),
 * and the dom tier's figures belong to the engine's `backdrop-filter` rather than
 * to vitrea's shader math.
 *
 * This was a real defect and not a preference. Cells arrive in the matrix's
 * key-sorted order, so "the first one" was the *dark dom* cell purely because
 * "apple-macos-26.5-1x-dark-standard" sorts before "…-light-standard" — a figure
 * from the wrong profile and the wrong tier, presented as the page's answer.
 * Naming the primary makes the choice visible and stops a new cell reordering it.
 */
const PRIMARY_PROFILE_KEY = "apple-macos-26.5-1x-light-standard";
const PRIMARY_TIER = "texture";

/** Lower sorts first. Ties fall through to the matrix's own order, which is stable. */
function primacy(report: CellReport): number {
  return (
    (report.profileKey === PRIMARY_PROFILE_KEY ? 0 : 2) + (report.tier === PRIMARY_TIER ? 0 : 1)
  );
}

/**
 * Every measured cell, keyed by scene, **primary cell first**. A scene may hold
 * more than one cell; see `PRIMARY_PROFILE_KEY` for which one speaks.
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
  for (const reports of bySceneId.values()) {
    reports.sort((a, b) => primacy(a) - primacy(b));
  }
  return bySceneId;
})();

export const MEASURED_CELL_COUNT = cells.length;
