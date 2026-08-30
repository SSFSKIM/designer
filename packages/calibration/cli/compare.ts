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
 *   --allow-colourless-tints measure tinted scenes on a bed whose capture session
 *                            demonstrably dropped the author tint's colour. Every
 *                            number over one of those is the UNTINTED material
 *                            filed under a tinted scene id — see
 *                            `colourlessTintEvidence`.
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
 *
 * ## The capture is keyed by native profile, not by colour scheme (W1)
 *
 * The native side has six profiles across three axes — colour scheme, backing
 * scale, and accessibility state — and every one of them is a *browser context*
 * property on the web side: `colorScheme`, `deviceScaleFactor`, and the runtime's
 * per-root accessibility overrides. So a capture run is per profile, and the
 * directory a capture lands in is keyed by the profile key.
 *
 * It used to be keyed by colour scheme alone, which was right while `1x` and
 * `standard` were the only values the other two axes had. With the wider bed it
 * would have had the 2x run overwrite the 1x one and both accessibility profiles
 * overwrite light-standard — silently, and with plausible numbers, which is the
 * exact failure the scheme keying was introduced to prevent.
 */

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  createResultMatrix,
  deserializeResultMatrix,
  serializeResultMatrix,
  upsertCellResult,
  RESULT_MATRIX_SCHEMA_VERSION,
  type CellResult,
  type FixtureSet,
  type ResultMatrix,
} from "../src/index";
import { isCaptureFresh, matrixSchemaRefusal, shouldWriteMatrix } from "./gates";
import { DEFAULT_SILHOUETTE_THRESHOLD, measureCell } from "./measure";
import { declaredComponentOf, readSceneGeometry } from "./scene-geometry";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const REFERENCE = resolve(REPO_ROOT, "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const FIXTURE_SETS = ["calibration", "validation", "holdout", "recorded"] as const;
/**
 * Holdout is opt-in and `recorded` is opt-in twice over: the default is what a
 * tuning loop is allowed to look at, and a recorded cell is never that.
 */
const DEFAULT_SETS: readonly FixtureSet[] = ["calibration", "validation"];

interface SceneEntry {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
  /** A key into the matrix's `tints` registry (W3). Absent on an untinted scene. */
  readonly tint?: string;
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

interface ManifestProfile {
  readonly profileKey: string;
  readonly colorScheme: "light" | "dark";
  /** The System Settings state the fixtures were captured under. */
  readonly a11yMode: string;
  readonly display?: { readonly actualBackingScale?: number };
  readonly fixtures: readonly FixtureEntry[];
}

interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly ManifestProfile[];
  readonly caveats: readonly string[];
}

function readJson<T>(path: string): T {
  if (!existsSync(path)) {
    throw new Error(`compare: ${path} does not exist. Has the native harness been run?`);
  }
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

// ---------------------------------------------------------------------------
// The accessibility axis: what the web side renders for a native profile
// ---------------------------------------------------------------------------

/**
 * **The coupling.** macOS force-enables Reduce Transparency when Increase
 * Contrast is on, and the transparency checkbox cannot be uncleared while
 * contrast is on — the user measured it directly, and the harness stamps the
 * coupling on the profile's own manifest entry. So the native
 * `-increased-contrast` reference embodies BOTH flags by construction: there is
 * no single-flag increased-contrast state on that platform to capture.
 *
 * vitrea's two axes are independent. `prefers-contrast: more` and
 * `prefers-reduced-transparency: reduce` are separate media queries, and a web
 * user on a platform that decouples them can be in contrast-only. So "what
 * should the web side render against this fixture?" has two defensible answers,
 * and the flag exists because they measure different things rather than because
 * one is unsettled:
 *
 *   as-captured    (default) both flags on — the state a native user in this
 *                  mode is actually in, and therefore the like-for-like diff.
 *                  This is the fidelity number.
 *   contrast-only  contrast alone — vitrea's own `prefers-contrast` response,
 *                  measured against the only reference that exists for it. This
 *                  is a *bound* on the contrast-only path, not a fidelity claim:
 *                  its reference is a coupled capture.
 *
 * On every other profile the two modes are identical, and the capture directory
 * is only suffixed where they actually differ — so switching the mode never
 * re-captures a profile the choice does not reach.
 */
const WEB_ACCESSIBILITY_MODES = ["as-captured", "contrast-only"] as const;
type WebAccessibilityMode = (typeof WEB_ACCESSIBILITY_MODES)[number];

/** The `--accessibility` argument for a profile, or `undefined` for none. */
function webAccessibilityFlags(
  a11yMode: string,
  mode: WebAccessibilityMode,
): readonly string[] | undefined {
  switch (a11yMode) {
    case "standard":
      return undefined;
    case "reduced-transparency":
      return ["reduced-transparency"];
    case "increased-contrast":
      return mode === "contrast-only"
        ? ["increased-contrast"]
        : ["reduced-transparency", "increased-contrast"];
    default:
      throw new Error(
        `compare: the manifest declares a11yMode '${a11yMode}', which this run does not know how ` +
          `to render on the web side. Add it to webAccessibilityFlags with the coupling it implies.`,
      );
  }
}

/**
 * The capture-directory suffix for a non-default mode, empty where the mode
 * changes nothing. Keeping it empty matters: a suffix on an unaffected profile
 * would fork one profile's captures into two identical trees and make the
 * matrices from the two modes incomparable for no reason.
 */
function webAccessibilityVariant(a11yMode: string, mode: WebAccessibilityMode): string {
  const chosen = webAccessibilityFlags(a11yMode, mode);
  const asCaptured = webAccessibilityFlags(a11yMode, "as-captured");
  return String(chosen) === String(asCaptured) ? "" : `__web-${mode}`;
}

// ---------------------------------------------------------------------------
// The tint axis: admitted only by a bed that demonstrably carried colour
// ---------------------------------------------------------------------------

/**
 * Evidence that this bed's capture session did not carry the author tint's
 * COLOUR into the material — or `undefined` when it did.
 *
 * The test is byte-identity and nothing else, which is what makes it
 * unarguable: two scenes that share a background, a component and a state and
 * differ only in *which* tint they declare cannot render to the same bytes if
 * the seed reached the material. `systemOrange` and `systemBlue` are not the
 * same colour. When they produce the same file, the seed was dropped somewhere
 * between the registry and the composite, and every number measured over a
 * tinted fixture is a measurement of the UNTINTED material wearing a tinted
 * scene id — the exact failure the tint plan's "refuse rather than guess" rule
 * at the harness's own load step was written to prevent, one level deeper.
 *
 * **Why one duplicate condemns the whole tint axis rather than the pair.** A
 * manifest is written by one binary in one capture session. A tint path that
 * dropped the seed for `photo__capsule-button__rest-tint-blue` dropped it for
 * every other tinted scene in that same session too; the pairs are merely where
 * the drop is *visible*, because they are the only places the bed declares two
 * seeds over one scene. Admitting `light-solid__capsule-button__rest-tint-orange`
 * on the grounds that nothing contradicts it would be filing the untinted
 * material under a tinted key with no duplicate left to expose it.
 *
 * No threshold and no colour model on purpose. A chroma-response floor would be
 * a number that a bed could meet by accident, and this question does not need
 * one to be answered.
 */
interface ColourlessTintEvidence {
  readonly profileKey: string;
  readonly scenes: readonly [string, string];
}

function colourlessTintEvidence(
  spec: SceneSpec,
  manifest: Manifest,
): ColourlessTintEvidence | undefined {
  const sceneById = new Map(spec.scenes.map((scene) => [scene.id, scene]));
  const digest = (file: string): string =>
    createHash("sha256").update(readFileSync(resolve(FIXTURES, file))).digest("hex");

  for (const profile of manifest.profiles) {
    // Grouped by everything a tint is orthogonal to, so the only difference
    // left inside a group is the declared seed.
    const groups = new Map<string, FixtureEntry[]>();
    for (const fixture of profile.fixtures) {
      const scene = sceneById.get(fixture.sceneId);
      if (scene?.tint === undefined) continue;
      const base = `${scene.background}|${scene.component}|${scene.state}`;
      groups.set(base, [...(groups.get(base) ?? []), fixture]);
    }
    for (const group of groups.values()) {
      if (group.length < 2) continue;
      const byDigest = new Map<string, string>();
      for (const fixture of group) {
        const hash = digest(fixture.file);
        const twin = byDigest.get(hash);
        if (twin !== undefined) {
          return { profileKey: profile.profileKey, scenes: [twin, fixture.sceneId] };
        }
        byDigest.set(hash, fixture.sceneId);
      }
    }
  }
  return undefined;
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
  readonly allowColourlessTints: boolean;
  readonly materialProfile: string | undefined;
  readonly webAccessibility: WebAccessibilityMode;
  readonly matrixPath: string;
  readonly silhouetteThreshold: number;
  /**
   * Outward dilation of the declared search region, device px. Absent means the
   * package default, which is zero — see `DEFAULT_COMPONENT_REGION_MARGIN_PX`
   * for why a margin costs more than it buys against a shadow-casting reference.
   */
  readonly componentRegionMarginPx: number | undefined;
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

  const webAccessibility = (flag("web-accessibility") ?? "as-captured") as WebAccessibilityMode;
  if (!WEB_ACCESSIBILITY_MODES.includes(webAccessibility)) {
    throw new Error(
      `compare: --web-accessibility takes ${WEB_ACCESSIBILITY_MODES.join("|")}, ` +
        `not '${webAccessibility}'`,
    );
  }

  return {
    scenes,
    profileKeys,
    sets,
    renderer,
    skipCapture: argv.includes("--skip-capture"),
    writePartial: argv.includes("--write-partial"),
    allowMaterialFree: argv.includes("--allow-material-free"),
    allowColourlessTints: argv.includes("--allow-colourless-tints"),
    materialProfile: materialProfile === undefined ? undefined : resolve(process.cwd(), materialProfile),
    webAccessibility,
    matrixPath: resolve(PACKAGE_ROOT, flag("out-matrix") ?? "results/matrix.json"),
    silhouetteThreshold: Number(flag("silhouette-threshold") ?? `${DEFAULT_SILHOUETTE_THRESHOLD}`),
    componentRegionMarginPx:
      flag("region-margin") === undefined ? undefined : Number(flag("region-margin")),
  };
}

/** One cell to measure: a native fixture plus the scene metadata it needs. */
interface PlannedCell {
  readonly profileKey: string;
  readonly colorScheme: "light" | "dark";
  /** The backing scale the native fixture was captured at; the web `deviceScaleFactor`. */
  readonly scale: number;
  /** The native System Settings state; translated for the web side by `webAccessibilityFlags`. */
  readonly a11yMode: string;
  readonly sceneId: string;
  readonly fixtureSet: FixtureSet;
  readonly fixture: FixtureEntry;
  readonly backgroundFile: string;
  readonly order: number;
}

function plan(
  spec: SceneSpec,
  manifest: Manifest,
  options: Options,
  colourlessTints: ColourlessTintEvidence | undefined,
): PlannedCell[] {
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

      /*
       * Skipped, not failed. A bed that dropped the tint colour is a property of
       * the capture session, not of this run — so the untinted cells around these
       * still measure and still write a matrix, and the skip is reported in the
       * caveats block where a reader of the numbers will see it.
       */
      if (
        colourlessTints !== undefined &&
        !options.allowColourlessTints &&
        spec.scenes.find((s) => s.id === fixture.sceneId)?.tint !== undefined
      ) {
        continue;
      }

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
      // Schema-2 manifests key backgrounds per scale ("checkerboard@2x"),
      // because one merged manifest describes every scale's fixtures at once;
      // the bare-name fallback keeps schema-1 manifests readable.
      const scaleToken = /-(\d+)x-/.exec(profile.profileKey)?.[1] ?? "1";
      const backgroundFile =
        manifest.backgrounds[`${scene.background}@${scaleToken}x`] ??
        manifest.backgrounds[scene.background];
      if (backgroundFile === undefined) {
        throw new Error(
          `compare: the manifest has no background '${scene.background}' at ${scaleToken}x`,
        );
      }

      /*
       * The scale comes off the profile's recorded display, not off its key.
       * The key states the scale a profile CLAIMS and the harness refuses a
       * mismatched run, so the two agree — but the display record is the
       * observation, and a capture's deviceScaleFactor should be set from what
       * was measured rather than from what a string says.
       */
      const scale = profile.display?.actualBackingScale;
      if (scale === undefined) {
        throw new Error(
          `compare: ${profile.profileKey} records no display.actualBackingScale, so the web ` +
            `capture's deviceScaleFactor cannot be matched to it. Re-run the native harness.`,
        );
      }

      cells.push({
        profileKey: profile.profileKey,
        colorScheme: profile.colorScheme,
        scale,
        a11yMode: profile.a11yMode,
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
 * Where a profile's captures live: `web-captures/<profileKey><variant>/<scene>`.
 *
 * The profile key has to be in the path. Every profile shares the same scene
 * ids by design — the same geometry over the same backdrop under a different
 * scheme, scale or accessibility state is exactly the comparison those axes
 * exist to make — so a directory keyed on anything narrower has one profile's
 * run overwrite another's, and the second profile then gets measured against
 * the first's web capture. Silently, and with plausible numbers.
 */
function captureRootFor(profileKey: string, variant: string): string {
  return resolve(PACKAGE_ROOT, "web-captures", `${profileKey}${variant}`);
}

function captureDirFor(profileKey: string, variant: string, sceneId: string): string {
  return resolve(captureRootFor(profileKey, variant), sceneId);
}

function captureFor(planned: readonly PlannedCell[], options: Options): void {
  // One invocation per profile: colour scheme, device scale factor and the
  // accessibility overrides are all browser-context or per-root properties, so
  // none of them can vary within a capture run — but every scene under one
  // profile shares one browser and one dev server.
  const first = planned[0];
  if (first === undefined) return;
  const sceneIds = [...new Set(planned.map((cell) => cell.sceneId))];
  const accessibility = webAccessibilityFlags(first.a11yMode, options.webAccessibility);
  const variant = webAccessibilityVariant(first.a11yMode, options.webAccessibility);
  run(`web capture (${first.profileKey}${variant}, ${sceneIds.length} scene(s))`, "npx", [
    "tsx",
    "scripts/capture-web.ts",
    ...sceneIds,
    "--renderer",
    options.renderer,
    "--color-scheme",
    first.colorScheme,
    "--scale",
    `${first.scale}`,
    ...(accessibility === undefined ? [] : ["--accessibility", accessibility.join(",")]),
    "--out",
    captureRootFor(first.profileKey, variant),
    ...(options.materialProfile === undefined ? [] : ["--material-profile", options.materialProfile]),
  ]);
}

function say(line: string): void {
  process.stdout.write(`${line}\n`);
}

function metric(
  cell: CellResult,
  axis: "shape" | "material" | "perceptual" | "shadow",
  field: string,
): number | undefined {
  const report = cell[axis] as Record<string, { value: number } | undefined> | undefined;
  return report?.[field]?.value;
}

function fixed(value: number | undefined, digits: number): string {
  return value === undefined ? "  —   " : value.toFixed(digits);
}

/**
 * A tally of cells an axis was absent on, and the scenes they belong to.
 *
 * Both halves are needed and they are different sizes: the count is how much
 * evidence is missing, the scene list is where to look for it. Collapsing to
 * scene ids alone — which is what a bare `Set<sceneId>` does — reports one
 * twelfth of the former under its name on a six-profile, two-tier run.
 */
class Absences {
  private readonly cells = new Set<string>();
  private readonly scenes = new Set<string>();

  add(profileKey: string, sceneId: string, tier: string): void {
    this.cells.add(`${profileKey}|${sceneId}|${tier}`);
    this.scenes.add(sceneId);
  }

  get cellCount(): number {
    return this.cells.size;
  }

  get sceneNames(): readonly string[] {
    return [...this.scenes];
  }

  /** "N cell(s) across M scene(s): a, b, c" — never one standing in for the other. */
  describe(): string {
    return (
      `${this.cellCount} cell(s) across ${this.scenes.size} scene(s): ${this.sceneNames.join(", ")}`
    );
  }
}

function main(): void {
  const options = parseOptions(process.argv.slice(2));
  const spec = readJson<SceneSpec>(resolve(REFERENCE, "scenes.json"));
  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  // The same file, projected onto the geometry the instrument bounds its search
  // to (schema 5). Read through the shared resolver so `compare`, `diff` and
  // `tier-delta` cannot end up bounding three different regions.
  const geometry = readSceneGeometry(REFERENCE);

  const colourlessTints = options.allowColourlessTints
    ? undefined
    : colourlessTintEvidence(spec, manifest);

  const planned = plan(spec, manifest, options, colourlessTints);
  if (planned.length === 0) {
    throw new Error(
      "compare: the filters selected no cells. Check --scene / --profile / --set." +
        (colourlessTints === undefined
          ? ""
          : " Every tinted scene is being skipped — see --allow-colourless-tints."),
    );
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

  /*
   * Refuse an unwritable target BEFORE capturing anything.
   *
   * The matrix is only deserialised after the capture step, so a target this
   * build cannot merge into would otherwise cost a whole browser run before
   * failing — and during the schema-4/5 interregnum the *default* target is
   * exactly such a file. See `matrixSchemaRefusal`.
   */
  if (existsSync(options.matrixPath)) {
    const existing: unknown = JSON.parse(readFileSync(options.matrixPath, "utf8"));
    const version = (existing as { schemaVersion?: unknown }).schemaVersion;
    const refusal =
      typeof version === "number"
        ? matrixSchemaRefusal(version, RESULT_MATRIX_SCHEMA_VERSION, options.matrixPath)
        : `${options.matrixPath} has no numeric schemaVersion, so it is not a result matrix.`;
    // Unprefixed: `main`'s own catch prefixes every message with `compare:`.
    if (refusal !== undefined) throw new Error(refusal);
  }

  // Read before the capture step, so every artifact the measure loop selects can
  // be asked whether this run wrote it. See `isCaptureFresh`.
  const runStartedAt = Date.now();

  if (!options.skipCapture) {
    for (const profileKey of [...new Set(planned.map((cell) => cell.profileKey))]) {
      captureFor(
        planned.filter((cell) => cell.profileKey === profileKey),
        options,
      );
    }
  }

  let matrix: ResultMatrix = existsSync(options.matrixPath)
    ? deserializeResultMatrix(readFileSync(options.matrixPath, "utf8"))
    : createResultMatrix();

  const measured: { readonly planned: PlannedCell; readonly cell: CellResult; readonly notes: readonly string[] }[] =
    [];
  const failures: string[] = [];
  /** Dom-tier scenes whose texture twin was not on disk, so they carry no coherence. */
  const coherenceless = new Set<string>();

  process.stderr.write(`\n── measure (${planned.length} cell(s)) ─────────────────────────────\n`);
  for (const cell of planned) {
    const captureDir = captureDirFor(
      cell.profileKey,
      webAccessibilityVariant(cell.a11yMode, options.webAccessibility),
      cell.sceneId,
    );
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

    /*
     * The other half of the coherence pair (schema 4).
     *
     * A `compare` run renders one tier — `--renderer` is a single value, and the
     * two tiers are two invocations writing into one matrix. So the texture
     * capture is simply read off disk from the same scene directory: it is the
     * capture the `webgpu` run wrote there, and it is the same capture that run's
     * own cell in this matrix was measured from. Nothing is re-rendered and
     * nothing is inferred; a missing twin leaves the axis absent.
     *
     * This is why coherence is computed here rather than by a second CLI
     * enriching the written matrix: the matrix stays writable by exactly one
     * sanctioned path.
     */
    const twinPng = resolve(captureDir, `${cell.sceneId}__webgpu.png`);
    const textureTwinPath = options.renderer === "css" && existsSync(twinPng) ? twinPng : undefined;
    if (options.renderer === "css" && textureTwinPath === undefined) {
      coherenceless.add(cell.sceneId);
    }

    try {
      const outcome = measureCell({
        nativePath: resolve(FIXTURES, cell.fixture.file),
        webPath: webPng,
        ...(textureTwinPath === undefined ? {} : { textureTwinPath }),
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
        component: declaredComponentOf(geometry, cell.sceneId),
        canvas: geometry.canvas,
        // The measured backing scale, not the one the key claims — the same
        // observation the web capture's deviceScaleFactor was set from.
        scale: cell.scale,
        ...(options.componentRegionMarginPx === undefined
          ? {}
          : { componentRegionMarginPx: options.componentRegionMarginPx }),
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
  /*
   * Absences are counted per CELL and *named* per scene.
   *
   * The two are not the same number and the difference is not small: every scene
   * appears once per profile and once per tier, so a set of scene ids counts a
   * twelfth of what is missing on a six-profile two-tier run. Reporting the
   * shorter number under the longer number's label understates exactly the
   * evidence a reader is being warned about.
   */
  const noMaterial = new Absences();
  say("");
  say(
    "set         profile                        scene                                        IoU    cMean   SSIM    dE     " +
      "  lum slope N/W     interior mean N/W    interior sd N/W     rim peak N/W",
  );
  say("-".repeat(222));
  for (const { planned: cell, cell: result } of measured) {
    // The profile axes, minus the platform prefix every row shares.
    const profile = cell.profileKey.replace(/^apple-macos-[\d.]+-/, "");
    if (result.material === undefined) noMaterial.add(cell.profileKey, cell.sceneId, result.tier);
    say(
      [
        cell.fixtureSet.padEnd(11),
        profile.padEnd(29),
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
  // Per profile AND per set. A worst case pooled across profiles would let the
  // widest profile's cell stand in for every profile's, which is the opposite of
  // what a per-profile threshold table needs.
  for (const [profileKey, set] of [...new Set(measured.map((row) => row.planned.profileKey))]
    .flatMap((profileKey) => options.sets.map((set) => [profileKey, set] as const))) {
    const rows = measured.filter(
      (row) => row.planned.fixtureSet === set && row.planned.profileKey === profileKey,
    );
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
      `${profileKey.replace(/^apple-macos-[\d.]+-/, "").padEnd(29)} ${set.padEnd(11)} ` +
        `n=${String(rows.length).padStart(2)}  ` +
        [
          summarise("IoU", iou, "min", 4),
          summarise("contour p95", contour, "max", 2),
          summarise("SSIM", ssimValues, "min", 4),
          summarise("dE", deltaE, "max", 5),
        ].join("   "),
    );
  }

  // ---------------------------------------------------------------------------
  // The shadow axis (schema 5). Its own block rather than more columns above:
  // it is a description of a facet, not a residual, and the reference's numbers
  // are what a renderer gets fitted against.
  //
  // A dash is an ABSENT figure, never a zero — over a backdrop with no light to
  // remove there is no occlusion ratio to report, and a side that reached the
  // threshold in no direction has no offset.
  // ---------------------------------------------------------------------------
  const unnormalisedShadow = new Absences();
  say("");
  say("── the shadow axis: what each side does to the backdrop it does not cover ────────────");
  say(
    "profile                       scene                                        support  strength N/W     " +
      "extent above/below/left/right N       W                 offset y N/W     blur sigma N/W",
  );
  say("-".repeat(200));
  for (const { planned: cell, cell: result } of measured) {
    if (result.shadow === undefined) continue;
    if (metric(result, "shadow", "strengthPeakNative") === undefined) {
      unnormalisedShadow.add(cell.profileKey, cell.sceneId, result.tier);
    }
    const extents = (side: "Native" | "Web"): string =>
      (["extentAbove", "extentBelow", "extentLeft", "extentRight"] as const)
        .map((field) => fixed(metric(result, "shadow", `${field}${side}`), 0).padStart(3))
        .join("/");
    say(
      [
        cell.profileKey.replace(/^apple-macos-[\d.]+-/, "").padEnd(29),
        cell.sceneId.padEnd(44),
        fixed(metric(result, "shadow", "backdropSupport"), 2).padStart(7),
        `${fixed(metric(result, "shadow", "strengthPeakNative"), 4).padStart(7)}/${fixed(metric(result, "shadow", "strengthPeakWeb"), 4).padStart(7)}`,
        ` ${extents("Native")}  ${extents("Web")}`,
        `  ${fixed(metric(result, "shadow", "offsetYNative"), 1).padStart(6)}/${fixed(metric(result, "shadow", "offsetYWeb"), 1).padStart(6)}`,
        `  ${fixed(metric(result, "shadow", "falloffSigmaNative"), 1).padStart(6)}/${fixed(metric(result, "shadow", "falloffSigmaWeb"), 1).padStart(6)}`,
      ].join(" "),
    );
  }

  // ---------------------------------------------------------------------------
  // What this run does and does not show. Every caveat that would make a number
  // misleading is printed, never left to a reader who happens to open the JSON.
  // ---------------------------------------------------------------------------
  say("");
  say("── what this run does and does not show ────────────");
  if (colourlessTints !== undefined) {
    const tinted = spec.scenes.filter((scene) => scene.tint !== undefined).length;
    say(
      `THE TINT AXIS IS ABSENT from this run: all ${tinted} tinted scene(s) were skipped, on every ` +
        `profile. This bed's capture session did not carry the author tint's COLOUR into the ` +
        `material — ${colourlessTints.scenes[0]} and ${colourlessTints.scenes[1]} declare different ` +
        `seeds and their ${colourlessTints.profileKey} fixtures are byte-identical, which one ` +
        `binary in one session cannot have done for those two alone. Re-capture the bed to measure ` +
        `the tint; pass --allow-colourless-tints to measure the untinted material under the tinted ` +
        `ids anyway.`,
    );
  }
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
  if (noMaterial.cellCount > 0) {
    say(
      `material axis absent on ${noMaterial.describe()}. ` +
        `See the per-cell notes — absent means not identifiable on that scene, never zero.`,
    );
  }
  say(
    `the shape axis is BOUNDED to the declared component region (margin ` +
      `${String(options.componentRegionMarginPx ?? 0)} device px): within it, coverage, contour and ` +
      `corner profile are measured as before; outside it nothing is recovered, so a surface drawn ` +
      `LARGER than its declaration reads as a match. Area recovery is assumed, not measured — read ` +
      `silhouetteArea{Native,Web} against componentRegionArea.`,
  );
  if (unnormalisedShadow.cellCount > 0) {
    say(
      `shadow axis NOT NORMALISED on ${unnormalisedShadow.describe()}. Those backdrops carry too little ` +
        `light for an occlusion ratio to exist; the absolute departure is still reported and every ` +
        `ratio is absent, not zero.`,
    );
  }
  if (options.renderer === "css") {
    const withCoherence = measured.filter((row) => row.cell.coherence !== undefined).length;
    say(
      `coherence axis on ${withCoherence} of ${measured.length} dom cell(s) — this tier against its ` +
        `texture twin, web against web` +
        (coherenceless.size === 0
          ? "."
          : `; absent on ${coherenceless.size} scene(s) with no webgpu capture on disk: ` +
            `${[...coherenceless].join(", ")}. Run the webgpu tier first to pair them.`),
    );
  }
  for (const caveat of manifest.caveats) say(`caveat: ${caveat}`);
  if (options.materialProfile !== undefined) {
    say(`material profile applied to the web side: ${options.materialProfile}`);
  }

  // Every profile's web-side accessibility state, printed whether or not the
  // default was used: which flags a capture rendered under is not something a
  // reader of these numbers should have to infer from the profile key.
  for (const profileKey of [...new Set(measured.map((row) => row.planned.profileKey))]) {
    const a11yMode = measured.find((row) => row.planned.profileKey === profileKey)?.planned.a11yMode;
    if (a11yMode === undefined) continue;
    const flags = webAccessibilityFlags(a11yMode, options.webAccessibility);
    say(
      `web accessibility for ${profileKey} (native ${a11yMode}): ` +
        (flags === undefined ? "browser preferences, no overrides" : flags.join(" + ")) +
        (webAccessibilityVariant(a11yMode, options.webAccessibility) === ""
          ? ""
          : ` — MODE ${options.webAccessibility}, which is not the state the native fixture was captured in`),
    );
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
