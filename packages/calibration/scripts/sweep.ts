/**
 * The tuning sweep: turn one or more material tunables through a grid, measure
 * the calibration cells at every point, and report the objective.
 *
 *   npx tsx scripts/sweep.ts \
 *     --axis optics.regular.tintAlpha=0.28,0.45,0.6,0.7,0.8 \
 *     --axis optics.regular.blurSigma=4,6,8 \
 *     --base profiles/light.base.json \
 *     --profile apple-macos-26.5-1x-light-standard
 *
 * `--renderer css` sweeps the dom tier instead, where the axes are the CSS
 * tier's mapping constants (corrective K5):
 *
 *   npx tsx scripts/sweep.ts --renderer css \
 *     --axis cssTierMapping.referenceBackdropLuminance=0.08,0.18,0.32 \
 *     --profile apple-macos-26.5-1x-light-standard
 *
 * The two tiers share this script because they share the objective: the terms
 * below are properties of the rendered material, not of the pipeline that drew
 * it. What differs is only which constants an axis can name — a dotted path
 * rooted at `cssTierMapping` patches the mapping, anything else patches the
 * renderer's profile — and the profile document carries both sections, so a
 * point is one file and one hash whichever tier is measuring.
 *
 * `--base` is a patch merged under every point — for the parts of a profile a
 * numeric axis cannot express, a tint colour being the obvious one.
 *
 * ## Why this is a committed script and not a session's worth of hand-edits
 *
 * A tuned constant is only as trustworthy as the search that produced it. If the
 * search lives in a shell history, the number in the profile is an assertion; if
 * it lives here, the number is a result someone else can reproduce or overturn.
 * The grid, the objective and the winning point are all printed, so a reader can
 * see how flat the optimum was — which matters more than the optimum, because a
 * sharp minimum on twelve scenes is usually overfitting and a flat one is not.
 *
 * ## The objective, stated rather than assumed
 *
 * Mean over measured calibration cells of
 *
 *     |Δ interior mean| + |Δ interior stdDev| + |Δ rim peak|
 *
 * where each Δ is web minus native. All three terms are linear-light relative
 * luminance, so they are commensurate and the sum needs no invented weights —
 * which is the point. A weighted combination of quantities in different units
 * would be a taste judgement wearing a number's clothes.
 *
 * The three terms are also the three things the tunables being swept actually
 * move, and they are close to independent: the interior mean is the material's
 * level (tint), its spread is how much backdrop structure survives (blur), and
 * the rim peak is the edge treatment (rim + specular). SSIM and OKLab ΔE are
 * printed alongside as **checks, not terms** — they aggregate the same underlying
 * error, so including them would double-count it, but a point that improves the
 * objective while worsening ΔE is a point to distrust.
 *
 * ## The second objective, for the facet the first one cannot see (2026-08-31)
 *
 * The objective above is measured *inside* the component's region, so it is
 * exactly blind to the outer shadow (W8) — sweeping a shadow constant against it
 * returns a flat grid, which reads as "not identifiable" when the truth is "not
 * looked at". Schema 5's shadow axis supplies the matching quantity on the other
 * side of the contour:
 *
 *     mean over measured calibration cells of |Δ meanDeparture|
 *
 * where `meanDeparture` is the mean of `backdrop − rendered` over the whole
 * exterior in linear light, and the Δ is web minus native. One term in one unit,
 * for the same reason the first objective has three commensurate ones and no
 * weights: the shadow's entire content is how much of the surround's light it
 * removes, and a second term (a peak, an extent) would re-aggregate the same
 * error under an invented exchange rate. It is made absolute per cell rather than
 * pooled, so a cell that darkens too much cannot cancel one that darkens too
 * little. It is also defined on every cell — including the dark backdrops where
 * the normalised block is absent — because it is an absolute quantity.
 *
 * Both objectives are computed and printed on every run; `--objective shadow`
 * only changes which one sorts the table and names the best point. A shadow
 * constant that improves the exterior while moving the interior is a point to
 * distrust in the way the ΔE and SSIM checks already guard against, and the
 * cheapest way to see it is to have both columns in front of you.
 *
 * Holdout is never swept. This script cannot select it: it passes
 * `--set calibration` and no holdout id appears anywhere in this file.
 */

import { spawnSync } from "node:child_process";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { deserializeResultMatrix, listCellResults, type CellResult } from "../src/index";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const WORK = resolve(PACKAGE_ROOT, "sweep-work");

interface Axis {
  readonly path: string;
  readonly values: readonly number[];
}

function parseAxes(argv: readonly string[]): Axis[] {
  const axes: Axis[] = [];
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] !== "--axis") continue;
    const raw = argv[i + 1];
    if (raw === undefined) throw new Error("--axis needs path=v1,v2,...");
    const [path, list] = raw.split("=");
    if (path === undefined || list === undefined) throw new Error(`bad --axis '${raw}'`);
    const values = list.split(",").map((v) => Number.parseFloat(v.trim()));
    if (values.some((v) => !Number.isFinite(v))) throw new Error(`bad values in --axis '${raw}'`);
    axes.push({ path, values });
  }
  if (axes.length === 0) throw new Error("give at least one --axis path=v1,v2,...");
  return axes;
}

/**
 * Deep-merge the base patch under a point's leaves, so `--base` can carry the
 * things a numeric axis cannot — a tint colour is an RGB triple, not a scalar,
 * and the sweep must be able to hold one fixed while turning the scalars.
 */
function mergeInto(target: Record<string, unknown>, source: Record<string, unknown>): void {
  for (const [key, value] of Object.entries(source)) {
    if (Array.isArray(value) || typeof value !== "object" || value === null) {
      target[key] = value;
      continue;
    }
    target[key] ??= {};
    mergeInto(target[key] as Record<string, unknown>, value as Record<string, unknown>);
  }
}

/** The section of the profile document an axis path patches. */
const CSS_TIER_SECTION = "cssTierMapping";

/**
 * Build a profile *document* from dotted leaf paths, over an optional base.
 *
 * Always a document — `{ patch, cssTierMapping }` — rather than a bare patch,
 * because a point may now name constants in either tier and the two must not be
 * flattened together: `referenceBackdropLuminance` is not a renderer optic and
 * `optics.regular.tintAlpha` is not a mapping constant. A path rooted at
 * `cssTierMapping` lands in that section; anything else lands under `patch`,
 * which is where every pre-K5 axis already pointed.
 *
 * A `--base` that is itself a document merges section-wise; one that is a bare
 * patch merges into `patch`, so the committed profiles keep working unchanged.
 */
function documentFrom(
  point: readonly { readonly path: string; readonly value: number }[],
  base: Record<string, unknown> = {},
): unknown {
  const root: Record<string, unknown> = { patch: {}, [CSS_TIER_SECTION]: {} };
  const baseIsDocument = "patch" in base || CSS_TIER_SECTION in base;
  mergeInto(root, baseIsDocument ? base : { patch: base });

  for (const { path, value } of point) {
    const parts = path.split(".");
    const section = parts[0] === CSS_TIER_SECTION ? CSS_TIER_SECTION : "patch";
    const leaves = parts[0] === CSS_TIER_SECTION ? parts.slice(1) : parts;
    let node = root[section] as Record<string, unknown>;
    for (const part of leaves.slice(0, -1)) {
      node[part] ??= {};
      node = node[part] as Record<string, unknown>;
    }
    node[leaves[leaves.length - 1] as string] = value;
  }

  // An empty section is dropped rather than written: `cssTierMapping: {}` reads
  // as "the mapping was configured to nothing", and the driver would accept it.
  for (const section of ["patch", CSS_TIER_SECTION]) {
    if (Object.keys(root[section] as Record<string, unknown>).length === 0) delete root[section];
  }
  return root;
}

/** Every combination, in a stable order. */
function grid(axes: readonly Axis[]): { readonly path: string; readonly value: number }[][] {
  let points: { readonly path: string; readonly value: number }[][] = [[]];
  for (const axis of axes) {
    points = points.flatMap((prefix) => axis.values.map((value) => [...prefix, { path: axis.path, value }]));
  }
  return points;
}

function value(cell: CellResult, axis: "material" | "perceptual" | "shadow", field: string): number | undefined {
  const report = cell[axis] as Record<string, { value: number } | undefined> | undefined;
  return report?.[field]?.value;
}

/** Which objective ranks the grid. Both are always computed and printed. */
export type Objective = "interior" | "shadow";

export interface Score {
  readonly objective: number;
  readonly meanTerm: number;
  readonly sdTerm: number;
  readonly rimTerm: number;
  /** The shadow objective: mean |Δ meanDeparture| over the exterior, linear light. */
  readonly shadow: number;
  readonly shadowCells: number;
  readonly deltaE: number;
  readonly ssim: number;
  readonly cells: number;
}

export function score(matrixJson: string, objective: Objective): Score {
  const cells = listCellResults(deserializeResultMatrix(matrixJson)).filter(
    (cell) => cell.fixtureSet === "calibration",
  );
  let meanTerm = 0;
  let sdTerm = 0;
  let rimTerm = 0;
  let deltaE = 0;
  let ssim = 0;
  let measured = 0;
  let perceptualCount = 0;
  let shadowTerm = 0;
  let shadowCells = 0;

  for (const cell of cells) {
    // The exterior objective, independent of everything above: a cell with no
    // shadow axis contributes nothing rather than a zero, on the same rule.
    const dn = value(cell, "shadow", "meanDepartureNative");
    const dw = value(cell, "shadow", "meanDepartureWeb");
    if (dn !== undefined && dw !== undefined) {
      shadowTerm += Math.abs(dw - dn);
      shadowCells += 1;
    }

    const e = value(cell, "perceptual", "oklabDeltaEMean");
    const s = value(cell, "perceptual", "ssimMean");
    if (e !== undefined && s !== undefined) {
      deltaE += e;
      ssim += s;
      perceptualCount += 1;
    }

    const nm = value(cell, "material", "interiorMeanNative");
    const wm = value(cell, "material", "interiorMeanWeb");
    const nsd = value(cell, "material", "interiorStdDevNative");
    const wsd = value(cell, "material", "interiorStdDevWeb");
    const nr = value(cell, "material", "rimPeakLuminanceNative");
    const wr = value(cell, "material", "rimPeakLuminanceWeb");
    // A cell whose material axis is absent contributes nothing rather than a
    // zero: a scene that cannot measure the material must not look like a scene
    // that measures it perfectly.
    if (nm === undefined || wm === undefined || nsd === undefined || wsd === undefined) continue;
    if (nr === undefined || wr === undefined) continue;
    meanTerm += Math.abs(wm - nm);
    sdTerm += Math.abs(wsd - nsd);
    rimTerm += Math.abs(wr - nr);
    measured += 1;
  }

  /*
   * The interior objective is undefined without a material axis, and a cell that
   * cannot measure the material must not look like one that measures it
   * perfectly — so an empty set is a refusal rather than a zero.
   *
   * Conditioned on the interior objective actually being RANKED on, though. A
   * shadow-objective sweep scoped to shadow-only cells is a legitimate run: over
   * a solid backdrop of the material's own tone the native silhouette is empty,
   * so `cli/measure.ts` records the cell with no material axis at all, while its
   * exterior metrics are present and are exactly what such a sweep is ranking.
   * Throwing there discarded an objective that had just been computed correctly.
   */
  if (measured === 0 && objective === "interior") {
    throw new Error(
      "sweep: no calibration cell carried a material axis, so the interior objective " +
        "is undefined here. If you meant to sweep the outer shadow, pass --objective shadow.",
    );
  }
  if (shadowCells === 0 && objective === "shadow") {
    throw new Error("sweep: no calibration cell carried a shadow axis, so the shadow objective is undefined here.");
  }
  return {
    objective: measured === 0 ? Number.NaN : (meanTerm + sdTerm + rimTerm) / measured,
    meanTerm: measured === 0 ? Number.NaN : meanTerm / measured,
    sdTerm: measured === 0 ? Number.NaN : sdTerm / measured,
    rimTerm: measured === 0 ? Number.NaN : rimTerm / measured,
    shadow: shadowCells === 0 ? Number.NaN : shadowTerm / shadowCells,
    shadowCells,
    deltaE: deltaE / Math.max(1, perceptualCount),
    ssim: ssim / Math.max(1, perceptualCount),
    cells: measured,
  };
}

function main(): void {
  const argv = process.argv.slice(2);
  const axes = parseAxes(argv);
  const flag = (name: string): string | undefined => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const profileKey = flag("profile");
  const renderer = flag("renderer") ?? "webgpu";
  if (renderer !== "webgpu" && renderer !== "css") {
    throw new Error(`sweep: --renderer takes webgpu or css, not '${renderer}'`);
  }
  const objective = (flag("objective") ?? "interior") as Objective;
  if (objective !== "interior" && objective !== "shadow") {
    throw new Error(`sweep: --objective takes interior or shadow, not '${objective}'`);
  }
  const rank = (s: Score): number => (objective === "shadow" ? s.shadow : s.objective);
  // Scene restriction, forwarded to compare. Its use here is to check that an
  // optimum does not depend on a subset of cells — the pressed scenes in
  // particular, whose native side carries no press pose.
  const scenes = flag("scene");
  const basePath = flag("base");
  const base =
    basePath === undefined
      ? {}
      : (JSON.parse(readFileSync(resolve(process.cwd(), basePath), "utf8")) as Record<string, unknown>);

  mkdirSync(WORK, { recursive: true });
  const points = grid(axes);
  process.stderr.write(
    `sweep: ${renderer} tier, ${points.length} point(s) over ` +
      `${axes.map((a) => `${a.path}[${a.values.length}]`).join(" × ")}\n`,
  );

  const results: { readonly label: string; readonly score: Score }[] = [];

  for (const [index, point] of points.entries()) {
    const label = point.map((p) => `${p.path.split(".").pop() ?? p.path}=${p.value}`).join(" ");
    const profilePath = resolve(WORK, `profile-${index}.json`);
    const matrixPath = resolve(WORK, `matrix-${index}.json`);
    writeFileSync(profilePath, `${JSON.stringify(documentFrom(point, base), null, 2)}\n`);
    /*
     * Delete any matrix already at this path before measuring into it.
     *
     * `compare` upserts into an existing matrix, and a cell's key includes the
     * capture path — which names the profile hash — so cells from a *previous*
     * sweep do not collide with this point's, they accumulate beside them. The
     * score then averages this point together with whatever was measured here
     * last time. Caught by the reported cell count differing between points,
     * which is why that count is printed.
     */
    rmSync(matrixPath, { force: true });

    process.stderr.write(`\n═══ [${index + 1}/${points.length}] ${label} ═══\n`);
    const run = spawnSync(
      "npx",
      [
        "tsx",
        "cli/compare.ts",
        "--set",
        "calibration",
        "--material-profile",
        profilePath,
        "--out-matrix",
        matrixPath,
        "--renderer",
        renderer,
        ...(profileKey === undefined ? [] : ["--profile", profileKey]),
        ...(scenes === undefined ? [] : ["--scene", scenes]),
      ],
      { cwd: PACKAGE_ROOT, stdio: ["ignore", "ignore", "inherit"] },
    );
    if (run.status !== 0) {
      process.stderr.write(`sweep: point '${label}' failed; skipping it rather than scoring a partial run\n`);
      continue;
    }
    results.push({ label, score: score(readFileSync(matrixPath, "utf8"), objective) });
  }

  const say = (line: string): void => void process.stdout.write(`${line}\n`);
  const num = (value: number, digits: number): string =>
    Number.isNaN(value) ? "—" : value.toFixed(digits);
  say("");
  say("interior = mean over calibration cells of |Δmean| + |Δsd| + |Δrim|, linear light");
  say("shadow   = mean over calibration cells of |Δ meanDeparture| over the exterior, linear light");
  say(`ranked on the ${objective.toUpperCase()} objective. SSIM and dE are CHECKS, not terms of either.`);
  say("");
  say(
    `${"point".padEnd(46)}${"interior".padStart(11)}${"|Δmean|".padStart(10)}${"|Δsd|".padStart(9)}` +
      `${"|Δrim|".padStart(9)}${"shadow".padStart(10)}${"dE".padStart(9)}${"SSIM".padStart(8)}${"n".padStart(4)}${"ns".padStart(4)}`,
  );
  say("-".repeat(120));
  const sorted = [...results].sort((a, b) => rank(a.score) - rank(b.score));
  for (const { label, score: s } of sorted) {
    say(
      label.padEnd(46) +
        num(s.objective, 5).padStart(11) +
        num(s.meanTerm, 5).padStart(10) +
        num(s.sdTerm, 5).padStart(9) +
        num(s.rimTerm, 5).padStart(9) +
        num(s.shadow, 5).padStart(10) +
        s.deltaE.toFixed(5).padStart(9) +
        s.ssim.toFixed(4).padStart(8) +
        String(s.cells).padStart(4) +
        String(s.shadowCells).padStart(4),
    );
  }
  const best = sorted[0];
  if (best !== undefined) {
    say("");
    say(`best: ${best.label}  ${objective} ${rank(best.score).toFixed(5)}`);
    const worst = sorted[sorted.length - 1];
    if (worst !== undefined && worst !== best) {
      say(
        `spread across the grid: ${rank(best.score).toFixed(5)} … ${rank(worst.score).toFixed(5)} ` +
          `(${(rank(worst.score) / rank(best.score)).toFixed(2)}×). A flat grid means the optimum ` +
          `is weakly identified, which is information about the fixtures, not a reason to pick harder.`,
      );
    }
  }
}

/*
 * Only run when this file is the entry point. `score` is exported so the guard
 * conditioning it on the chosen objective can be pinned in the unit suite, and an
 * import must not launch a grid of browser captures to get at it.
 */
const invokedDirectly =
  process.argv[1] !== undefined && resolve(process.argv[1]) === fileURLToPath(import.meta.url);

try {
  if (invokedDirectly) main();
} catch (error) {
  process.stderr.write(`sweep: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}
