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

/** Build a patch object from dotted leaf paths, over an optional base patch. */
function patchFrom(
  point: readonly { readonly path: string; readonly value: number }[],
  base: Record<string, unknown> = {},
): unknown {
  const root: Record<string, unknown> = {};
  mergeInto(root, base);
  for (const { path, value } of point) {
    const parts = path.split(".");
    let node = root;
    for (const part of parts.slice(0, -1)) {
      node[part] ??= {};
      node = node[part] as Record<string, unknown>;
    }
    node[parts[parts.length - 1] as string] = value;
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

function value(cell: CellResult, axis: "material" | "perceptual", field: string): number | undefined {
  const report = cell[axis] as Record<string, { value: number } | undefined> | undefined;
  return report?.[field]?.value;
}

interface Score {
  readonly objective: number;
  readonly meanTerm: number;
  readonly sdTerm: number;
  readonly rimTerm: number;
  readonly deltaE: number;
  readonly ssim: number;
  readonly cells: number;
}

function score(matrixJson: string): Score {
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

  for (const cell of cells) {
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

  if (measured === 0) throw new Error("sweep: no calibration cell carried a material axis");
  return {
    objective: (meanTerm + sdTerm + rimTerm) / measured,
    meanTerm: meanTerm / measured,
    sdTerm: sdTerm / measured,
    rimTerm: rimTerm / measured,
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
    `sweep: ${points.length} point(s) over ${axes.map((a) => `${a.path}[${a.values.length}]`).join(" × ")}\n`,
  );

  const results: { readonly label: string; readonly score: Score }[] = [];

  for (const [index, point] of points.entries()) {
    const label = point.map((p) => `${p.path.split(".").pop() ?? p.path}=${p.value}`).join(" ");
    const profilePath = resolve(WORK, `profile-${index}.json`);
    const matrixPath = resolve(WORK, `matrix-${index}.json`);
    writeFileSync(profilePath, `${JSON.stringify(patchFrom(point, base), null, 2)}\n`);
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
        ...(profileKey === undefined ? [] : ["--profile", profileKey]),
        ...(scenes === undefined ? [] : ["--scene", scenes]),
      ],
      { cwd: PACKAGE_ROOT, stdio: ["ignore", "ignore", "inherit"] },
    );
    if (run.status !== 0) {
      process.stderr.write(`sweep: point '${label}' failed; skipping it rather than scoring a partial run\n`);
      continue;
    }
    results.push({ label, score: score(readFileSync(matrixPath, "utf8")) });
  }

  const say = (line: string): void => void process.stdout.write(`${line}\n`);
  say("");
  say("objective = mean over calibration cells of |Δmean| + |Δsd| + |Δrim|, linear light");
  say("SSIM and dE are CHECKS, not terms of the objective.");
  say("");
  say(`${"point".padEnd(46)}${"objective".padStart(11)}${"|Δmean|".padStart(10)}${"|Δsd|".padStart(9)}${"|Δrim|".padStart(9)}${"dE".padStart(9)}${"SSIM".padStart(8)}${"n".padStart(4)}`);
  say("-".repeat(106));
  const sorted = [...results].sort((a, b) => a.score.objective - b.score.objective);
  for (const { label, score: s } of sorted) {
    say(
      label.padEnd(46) +
        s.objective.toFixed(5).padStart(11) +
        s.meanTerm.toFixed(5).padStart(10) +
        s.sdTerm.toFixed(5).padStart(9) +
        s.rimTerm.toFixed(5).padStart(9) +
        s.deltaE.toFixed(5).padStart(9) +
        s.ssim.toFixed(4).padStart(8) +
        String(s.cells).padStart(4),
    );
  }
  const best = sorted[0];
  if (best !== undefined) {
    say("");
    say(`best: ${best.label}  objective ${best.score.objective.toFixed(5)}`);
    const worst = sorted[sorted.length - 1];
    if (worst !== undefined && worst !== best) {
      say(
        `spread across the grid: ${best.score.objective.toFixed(5)} … ${worst.score.objective.toFixed(5)} ` +
          `(${(worst.score.objective / best.score.objective).toFixed(2)}×). A flat grid means the optimum ` +
          `is weakly identified, which is information about the fixtures, not a reason to pick harder.`,
      );
    }
  }
}

try {
  main();
} catch (error) {
  process.stderr.write(`sweep: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}
