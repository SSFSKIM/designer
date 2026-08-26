/**
 * `compare` — the whole scene matrix, end to end: capture the web side, diff
 * every cell against its native fixture, write one result matrix.
 *
 *   # every calibration and validation cell of every captured profile
 *   pnpm --filter @vitrea/calibration run compare
 *
 *   # one scene
 *   pnpm --filter @vitrea/calibration run compare -- --scene photo__rrect-md__rest
 *
 *   # the holdout cells, once, after tuning has frozen
 *   pnpm --filter @vitrea/calibration run compare -- --set holdout
 *
 * Two escapes exist and both name what they switch off, because both switch off
 * a check on whether the output is evidence:
 *
 *   --write-partial          write `results/matrix.json` even though cells
 *                            failed. The file then mixes this run's cells with
 *                            an earlier run's; the default is to leave it alone.
 *   --allow-material-free    measure fixtures marked `materialRendered: false`.
 *                            Every number over one of those is web-glass against
 *                            a bare background (Decision Log #26a).
 *
 * Everything the run needs is read from committed data rather than passed in:
 * each scene's background and split membership come from `scenes.json`, and each
 * native fixture's path, capture method and emptiness come from the harness's own
 * `manifest.json`. Nothing here restates a fact either file already owns, which
 * is what keeps the two sides from drifting.
 *
 * ## Three properties this orchestrator exists to hold
 *
 * **The holdout set is opt-in and never named here.** `--set` defaults to
 * `calibration,validation`. No holdout scene id appears in this file or anywhere
 * else in the tuning path; membership is read from `scenes.json`'s declared split,
 * so the anti-overfitting rule is enforced by data rather than by discipline. A
 * run that includes holdout says so in a banner, because a holdout number is
 * reportable exactly once per frozen configuration.
 *
 * **The capture order is interleaved and reproducible.** C6 measured GPU clock
 * state moving the same benchmark config by 90% between the first and last slot,
 * and the methodology mandates interleaving. Ordering matters far less for image
 * comparison than for timing, but a run whose order depends on file enumeration
 * is not reproducible, so the order is a stable permutation: cells sorted by
 * FNV-1a of `profileKey|sceneId`. That is deliberately the native harness's own
 * scheme (Decision Log #26e) — a language-independent hash, because Swift's
 * per-process string hash seed would have made the two orders incomparable.
 *
 * **One browser, one measurement pass, one write.** All of a profile's scenes are
 * captured in a single `capture-web` invocation — one browser launch, one dev
 * server — and every cell is then measured in this process against one in-memory
 * matrix that is serialised once. The alternative (a subprocess per scene) made a
 * full re-measure slow enough to discourage running one, which is the wrong
 * incentive for the only thing that tells you whether a tuning change helped.
 */

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  createResultMatrix,
  deserializeResultMatrix,
  serializeResultMatrix,
  upsertCellResult,
  type CellResult,
  type FixtureSet,
  type ResultMatrix,
} from "../src/index";
import { isCaptureFresh, shouldWriteMatrix } from "./gates";
import { DEFAULT_SILHOUETTE_THRESHOLD, measureCell } from "./measure";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const REFERENCE = resolve(REPO_ROOT, "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const FIXTURE_SETS = ["calibration", "validation", "holdout"] as const;
/** Holdout is opt-in. The default is what a tuning loop is allowed to look at. */
const DEFAULT_SETS: readonly FixtureSet[] = ["calibration", "validation"];

interface SceneEntry {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
}

interface SceneSpec {
  readonly scenes: readonly SceneEntry[];
  readonly split: Readonly<Record<FixtureSet, readonly string[]>>;
}

interface FixtureEntry {
  readonly sceneId: string;
  readonly file: string;
  readonly fixtureSet: FixtureSet;
  readonly captureMethod: string;
  readonly materialRendered: boolean;
  readonly identicalToBackground?: boolean;
}

interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly {
    readonly profileKey: string;
    readonly colorScheme: "light" | "dark";
    readonly fixtures: readonly FixtureEntry[];
  }[];
  readonly caveats: readonly string[];
}

function readJson<T>(path: string): T {
  if (!existsSync(path)) {
    throw new Error(`compare: ${path} does not exist. Has the native harness been run?`);
  }
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

/**
 * FNV-1a, 32-bit. Deliberately this and not a language hash: the native harness
 * orders its own captures by the same function over the same key, and a
 * per-process-seeded hash would make the two orders incomparable between runs.
 */
function fnv1a(input: string): number {
  let hash = 0x811c9dc5;
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash >>> 0;
}

function run(label: string, command: string, args: readonly string[]): void {
  process.stderr.write(`\n── ${label} ─────────────────────────────\n`);
  const result = spawnSync(command, args, { cwd: PACKAGE_ROOT, stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`compare: ${label} failed (exit ${String(result.status)})`);
  }
}

interface Options {
  readonly scenes: readonly string[] | undefined;
  readonly profileKeys: readonly string[] | undefined;
  readonly sets: readonly FixtureSet[];
  readonly renderer: "webgpu" | "css";
  readonly skipCapture: boolean;
  readonly writePartial: boolean;
  readonly allowMaterialFree: boolean;
  readonly materialProfile: string | undefined;
  readonly matrixPath: string;
  readonly silhouetteThreshold: number;
}

function parseOptions(argv: readonly string[]): Options {
  const flag = (name: string): string | undefined => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const list = (name: string): readonly string[] | undefined => {
    const raw = flag(name);
    return raw === undefined ? undefined : raw.split(",").map((s) => s.trim()).filter(Boolean);
  };

  const renderer = flag("renderer") ?? "webgpu";
  if (renderer !== "webgpu" && renderer !== "css") {
    throw new Error(`compare: --renderer takes webgpu or css, not '${renderer}'`);
  }

  const rawSets = list("set");
  const sets = (rawSets ?? DEFAULT_SETS) as readonly FixtureSet[];
  for (const set of sets) {
    if (!FIXTURE_SETS.includes(set as (typeof FIXTURE_SETS)[number])) {
      throw new Error(`compare: --set takes ${FIXTURE_SETS.join("|")}, not '${set}'`);
    }
  }

  const materialProfile = flag("material-profile");
  const scenes = list("scene");
  const profileKeys = list("profile");

  return {
    scenes,
    profileKeys,
    sets,
    renderer,
    skipCapture: argv.includes("--skip-capture"),
    writePartial: argv.includes("--write-partial"),
    allowMaterialFree: argv.includes("--allow-material-free"),
    materialProfile: materialProfile === undefined ? undefined : resolve(process.cwd(), materialProfile),
    matrixPath: resolve(PACKAGE_ROOT, flag("out-matrix") ?? "results/matrix.json"),
    silhouetteThreshold: Number(flag("silhouette-threshold") ?? `${DEFAULT_SILHOUETTE_THRESHOLD}`),
  };
}

/** One cell to measure: a native fixture plus the scene metadata it needs. */
interface PlannedCell {
  readonly profileKey: string;
  readonly colorScheme: "light" | "dark";
  readonly sceneId: string;
  readonly fixtureSet: FixtureSet;
  readonly fixture: FixtureEntry;
  readonly backgroundFile: string;
  readonly order: number;
}

function plan(spec: SceneSpec, manifest: Manifest, options: Options): PlannedCell[] {
  const setOf = (sceneId: string): FixtureSet => {
    for (const set of FIXTURE_SETS) {
      if (spec.split[set]?.includes(sceneId) === true) return set;
    }
    throw new Error(`compare: '${sceneId}' is in no declared split in scenes.json`);
  };

  const cells: PlannedCell[] = [];
  for (const profile of manifest.profiles) {
    if (options.profileKeys !== undefined && !options.profileKeys.includes(profile.profileKey)) continue;
    for (const fixture of profile.fixtures) {
      if (options.scenes !== undefined && !options.scenes.includes(fixture.sceneId)) continue;

      const declared = setOf(fixture.sceneId);
      if (fixture.fixtureSet !== declared) {
        // The two files disagree about which split this scene is in. Refuse rather
        // than pick one: a scene that is holdout in one place and calibration in
        // another is exactly the failure the split exists to prevent.
        throw new Error(
          `compare: split mismatch for '${fixture.sceneId}' — scenes.json says ${declared}, ` +
            `manifest says ${fixture.fixtureSet}`,
        );
      }
      if (!options.sets.includes(declared)) continue;

      if (!fixture.materialRendered && !options.allowMaterialFree) {
        // Decision Log #26a refused material-free captures as fixtures: they are
        // pixel-identical to their backgrounds, so a fidelity number over one
        // measures the backdrop, not the material. Refusing here rather than
        // printing a caveat afterwards — by then the matrix is already written.
        throw new Error(
          `compare: '${fixture.sceneId}' (${profile.profileKey}) is marked materialRendered: false, ` +
            `so a fidelity number over it measures the backdrop rather than the material ` +
            `(Decision Log #26a). Pass --allow-material-free to measure it anyway.`,
        );
      }

      const scene = spec.scenes.find((s) => s.id === fixture.sceneId);
      if (scene === undefined) {
        throw new Error(`compare: the manifest has a fixture for '${fixture.sceneId}', which scenes.json lacks`);
      }
      const backgroundFile = manifest.backgrounds[scene.background];
      if (backgroundFile === undefined) {
        throw new Error(`compare: the manifest has no background '${scene.background}'`);
      }

      cells.push({
        profileKey: profile.profileKey,
        colorScheme: profile.colorScheme,
        sceneId: fixture.sceneId,
        fixtureSet: declared,
        fixture,
        backgroundFile,
        order: fnv1a(`${profile.profileKey}|${fixture.sceneId}`),
      });
    }
  }

  // The interleaving permutation. Sorted by hash, tie-broken by key so the order
  // is total and reproducible rather than dependent on enumeration.
  return cells.sort(
    (a, b) =>
      a.order - b.order ||
      `${a.profileKey}|${a.sceneId}`.localeCompare(`${b.profileKey}|${b.sceneId}`),
  );
}

/**
 * Where a capture lives, keyed by colour scheme.
 *
 * The scheme has to be in the path. The light and dark profiles share scene ids
 * by design — the same geometry over the same backdrop is exactly the comparison
 * the scheme axis exists to make — so a directory keyed on the scene id alone
 * has the dark run overwrite the light one, and the light profile then gets
 * measured against a dark web capture. Silently, and with plausible numbers.
 */
function captureDirFor(colorScheme: "light" | "dark", sceneId: string): string {
  return resolve(PACKAGE_ROOT, "web-captures", colorScheme, sceneId);
}

function captureFor(
  planned: readonly PlannedCell[],
  colorScheme: "light" | "dark",
  options: Options,
): void {
  // One invocation per colour scheme: the scheme is a browser-context property,
  // so it cannot vary within a capture run, but every scene under it can share
  // one browser and one dev server.
  const sceneIds = [...new Set(planned.map((cell) => cell.sceneId))];
  run(`web capture (${colorScheme}, ${sceneIds.length} scene(s))`, "npx", [
    "tsx",
    "scripts/capture-web.ts",
    ...sceneIds,
    "--renderer",
    options.renderer,
    "--color-scheme",
    colorScheme,
    "--out",
    resolve(PACKAGE_ROOT, "web-captures", colorScheme),
    ...(options.materialProfile === undefined ? [] : ["--material-profile", options.materialProfile]),
  ]);
}

function say(line: string): void {
  process.stdout.write(`${line}\n`);
}

function metric(cell: CellResult, axis: "shape" | "material" | "perceptual", field: string): number | undefined {
  const report = cell[axis] as Record<string, { value: number } | undefined> | undefined;
  return report?.[field]?.value;
}

function fixed(value: number | undefined, digits: number): string {
  return value === undefined ? "  —   " : value.toFixed(digits);
}

function main(): void {
  const options = parseOptions(process.argv.slice(2));
  const spec = readJson<SceneSpec>(resolve(REFERENCE, "scenes.json"));
  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));

  const planned = plan(spec, manifest, options);
  if (planned.length === 0) {
    throw new Error("compare: the filters selected no cells. Check --scene / --profile / --set.");
  }

  if (options.sets.includes("holdout")) {
    process.stderr.write(
      `\n${"!".repeat(72)}\n` +
        `THIS RUN INCLUDES HOLDOUT CELLS.\n` +
        `Holdout exists to be measured once against a frozen configuration and\n` +
        `reported as-is. If any constant changes after this run, these numbers are\n` +
        `spent and the scenes are no longer a holdout for the new configuration.\n` +
        `${"!".repeat(72)}\n\n`,
    );
  }

  // Read before the capture step, so every artifact the measure loop selects can
  // be asked whether this run wrote it. See `isCaptureFresh`.
  const runStartedAt = Date.now();

  if (!options.skipCapture) {
    for (const colorScheme of ["light", "dark"] as const) {
      const subset = planned.filter((cell) => cell.colorScheme === colorScheme);
      if (subset.length > 0) captureFor(subset, colorScheme, options);
    }
  }

  let matrix: ResultMatrix = existsSync(options.matrixPath)
    ? deserializeResultMatrix(readFileSync(options.matrixPath, "utf8"))
    : createResultMatrix();

  const measured: { readonly planned: PlannedCell; readonly cell: CellResult; readonly notes: readonly string[] }[] =
    [];
  const failures: string[] = [];

  process.stderr.write(`\n── measure (${planned.length} cell(s)) ─────────────────────────────\n`);
  for (const cell of planned) {
    const captureDir = captureDirFor(cell.colorScheme, cell.sceneId);
    const webPng = resolve(captureDir, `${cell.sceneId}__${options.renderer}.png`);
    const webCell = resolve(captureDir, `cell__${options.renderer}.json`);
    const missing = [webPng, webCell].filter((path) => !existsSync(path));
    if (missing.length > 0) {
      failures.push(
        `${cell.profileKey} / ${cell.sceneId}: no ${options.renderer}-tier capture on disk ` +
          `(${missing.map((p) => p.replace(`${PACKAGE_ROOT}/`, "")).join(", ")})` +
          (options.skipCapture ? " — running with --skip-capture; drop it to capture now" : ""),
      );
      continue;
    }

    if (!options.skipCapture && !isCaptureFresh(statSync(webCell).mtimeMs, runStartedAt)) {
      failures.push(
        `${cell.profileKey} / ${cell.sceneId}: the ${options.renderer}-tier capture on disk predates ` +
          `this run — capture-web resolved another tier; check its FELL BACK line`,
      );
      continue;
    }

    try {
      const outcome = measureCell({
        nativePath: resolve(FIXTURES, cell.fixture.file),
        webPath: webPng,
        backgroundPath: resolve(FIXTURES, cell.backgroundFile),
        profileKey: cell.profileKey,
        sceneId: cell.sceneId,
        webCellPath: webCell,
        /*
         * Read off what drew, never off what was asked for.
         *
         * X9 states claims per tier and the two tiers mean different things: the
         * texture tier is a claim about vitrea's own shader math, the dom tier a
         * claim about an engine's backdrop-filter. A CSS-tier capture labelled
         * `texture` would file a measurement of Chromium's blur as evidence about
         * vitrea's optics. The capture script already resolves the renderer off
         * the page's own GlassGroupState, so the honest label is downstream of
         * that rather than of this orchestrator's flag.
         *
         * The glass-over-glass scenes are the exception the claims document
         * names: their overlay group is necessarily `dom` even on the GPU tier,
         * so those cells are a mixed-backend claim that neither label captures.
         */
        tier: options.renderer === "webgpu" ? "texture" : "dom",
        fixtureSet: cell.fixtureSet,
        blurAxis: "x",
        silhouetteThreshold: options.silhouetteThreshold,
      });
      matrix = upsertCellResult(matrix, outcome.cell);
      measured.push({ planned: cell, cell: outcome.cell, notes: outcome.notes });
      writeFileSync(
        resolve(captureDir, `report.cell__${options.renderer}.json`),
        `${JSON.stringify(outcome.cell, null, 2)}\n`,
      );
    } catch (error) {
      failures.push(
        `${cell.profileKey} / ${cell.sceneId}: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  // The per-cell `report.cell__*.json` written above are scratch and always
  // land, so a partial run stays inspectable. The matrix is the official artifact
  // and only a whole run may replace it.
  const writeMatrix = shouldWriteMatrix(failures.length, options.writePartial);
  if (writeMatrix) {
    mkdirSync(dirname(options.matrixPath), { recursive: true });
    writeFileSync(options.matrixPath, `${serializeResultMatrix(matrix, { pretty: true })}\n`);
    process.stderr.write(`matrix → ${options.matrixPath} (${matrix.cells.size} cell(s) total)\n`);
  }

  // ---------------------------------------------------------------------------
  // The table. Per cell, the numbers a tuning pass steers by — each as the pair
  // it is, native beside web, because a gap is not a quantity until both halves
  // are shown.
  // ---------------------------------------------------------------------------
  const noMaterial = new Set<string>();
  say("");
  say(
    "set         profile  scene                                        IoU    cMean   SSIM    dE     " +
      "  lum slope N/W     interior mean N/W    interior sd N/W     rim peak N/W",
  );
  say("-".repeat(196));
  for (const { planned: cell, cell: result } of measured) {
    const scheme = cell.colorScheme === "light" ? "light" : "dark ";
    if (result.material === undefined) noMaterial.add(cell.sceneId);
    say(
      [
        cell.fixtureSet.padEnd(11),
        scheme.padEnd(8),
        cell.sceneId.padEnd(44),
        fixed(metric(result, "shape", "silhouetteIoU"), 3).padStart(6),
        fixed(metric(result, "shape", "contourDistanceMean"), 2).padStart(7),
        fixed(metric(result, "perceptual", "ssimMean"), 3).padStart(7),
        fixed(metric(result, "perceptual", "oklabDeltaEMean"), 4).padStart(8),
        `  ${fixed(metric(result, "material", "luminanceSlopeNative"), 3).padStart(6)}/${fixed(metric(result, "material", "luminanceSlopeWeb"), 3).padStart(6)}`,
        `  ${fixed(metric(result, "material", "interiorMeanNative"), 4).padStart(7)}/${fixed(metric(result, "material", "interiorMeanWeb"), 4).padStart(7)}`,
        `  ${fixed(metric(result, "material", "interiorStdDevNative"), 4).padStart(7)}/${fixed(metric(result, "material", "interiorStdDevWeb"), 4).padStart(7)}`,
        `  ${fixed(metric(result, "material", "rimPeakLuminanceNative"), 4).padStart(7)}/${fixed(metric(result, "material", "rimPeakLuminanceWeb"), 4).padStart(7)}`,
      ].join(" "),
    );
  }

  // Per-set aggregates on the axes a threshold would be set on. Worst case as
  // well as mean, because a per-cell threshold is what the methodology asks for
  // and a mean can hide the one cell that fails it.
  say("");
  for (const set of options.sets) {
    const rows = measured.filter((row) => row.planned.fixtureSet === set);
    if (rows.length === 0) continue;
    const collect = (axis: "shape" | "perceptual", field: string): number[] =>
      rows.flatMap((row) => {
        const value = metric(row.cell, axis, field);
        return value === undefined ? [] : [value];
      });
    const iou = collect("shape", "silhouetteIoU");
    const contour = collect("shape", "contourDistanceP95");
    const ssimValues = collect("perceptual", "ssimMean");
    const deltaE = collect("perceptual", "oklabDeltaEMean");
    const summarise = (name: string, values: number[], worst: "min" | "max", digits: number): string => {
      if (values.length === 0) return `${name} n/a`;
      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      const extreme = worst === "min" ? Math.min(...values) : Math.max(...values);
      return `${name} mean ${mean.toFixed(digits)} worst ${extreme.toFixed(digits)}`;
    };
    say(
      `${set.padEnd(11)} n=${String(rows.length).padStart(2)}  ` +
        [
          summarise("IoU", iou, "min", 4),
          summarise("contour p95", contour, "max", 2),
          summarise("SSIM", ssimValues, "min", 4),
          summarise("dE", deltaE, "max", 5),
        ].join("   "),
    );
  }

  // ---------------------------------------------------------------------------
  // What this run does and does not show. Every caveat that would make a number
  // misleading is printed, never left to a reader who happens to open the JSON.
  // ---------------------------------------------------------------------------
  say("");
  say("── what this run does and does not show ────────────");
  const withoutMaterial = manifest.profiles
    .flatMap((p) => p.fixtures)
    .filter((f) => !f.materialRendered);
  if (withoutMaterial.length > 0) {
    say(
      `${withoutMaterial.length} fixture(s) carry NO MATERIAL (materialRendered: false). Every number ` +
        `for those is web-glass-vs-bare-background, not a fidelity measurement.`,
    );
  } else {
    say(`All native fixtures used here carry the composited material (materialRendered: true).`);
  }
  if (noMaterial.size > 0) {
    say(
      `material axis absent on ${noMaterial.size} cell(s): ${[...noMaterial].join(", ")}. ` +
        `See the per-cell notes — absent means not identifiable on that scene, never zero.`,
    );
  }
  for (const caveat of manifest.caveats) say(`caveat: ${caveat}`);
  if (options.materialProfile !== undefined) {
    say(`material profile applied to the web side: ${options.materialProfile}`);
  }

  const notes = measured.flatMap((row) => row.notes.map((note) => `${row.planned.sceneId}: ${note}`));
  if (notes.length > 0) {
    say("");
    say(`── notes (${notes.length}) ────────────`);
    for (const note of notes) say(`  ${note}`);
  }

  if (failures.length > 0) {
    say("");
    say(`── ${failures.length} cell(s) COULD NOT BE MEASURED ────────────`);
    for (const failure of failures) say(`  ${failure}`);
    say(
      writeMatrix
        ? `  --write-partial: ${options.matrixPath} WAS WRITTEN and now mixes this run's cells with ` +
            `whatever an earlier run left under the keys above.`
        : `  ${options.matrixPath} was left UNCHANGED. Fix the cells above and re-run, or pass ` +
            `--write-partial to write the matrix with these cells missing.`,
    );
    // A cell that could not be measured is a hole in the matrix, and a run that
    // exits 0 with holes in it invites a claim built on partial coverage.
    process.exitCode = 1;
  }
}

try {
  main();
} catch (error) {
  process.stderr.write(`compare: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}
