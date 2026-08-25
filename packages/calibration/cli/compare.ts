/**
 * `compare` — one scene, end to end: capture the web side, diff it against the
 * native fixture, write the cell into X9's result matrix.
 *
 *   pnpm --filter @vitrea/calibration run compare -- --scene checkerboard__capsule-button__rest
 *
 * This is C7's integration proof. The acceptance asks that the result-matrix
 * schema be "consumed by at least one automated comparison run", and the thing
 * that has to work is the *pipeline* — capture → diff → matrix entry — not the
 * numbers it produces. On this machine the numbers are meaningless on purpose:
 * the native fixture carries no material (see apps/reference-apple/README.md
 * §"The capture wall"), so the diff is measuring web glass against a bare
 * background. That is reported loudly rather than quietly averaged.
 *
 * Everything the run needs is read from committed data rather than passed in:
 * the scene's background and split membership come from `scenes.json`, and the
 * native fixture's path, capture method and emptiness come from the harness's
 * own `manifest.json`. Nothing here restates a fact either file already owns,
 * which is what keeps the two sides from drifting.
 */

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const REFERENCE = resolve(REPO_ROOT, "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

interface SceneEntry {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
}

interface SceneSpec {
  readonly scenes: readonly SceneEntry[];
  readonly split: {
    readonly calibration: readonly string[];
    readonly validation: readonly string[];
    readonly holdout: readonly string[];
  };
}

interface FixtureEntry {
  readonly sceneId: string;
  readonly file: string;
  readonly fixtureSet: string;
  readonly captureMethod: string;
  readonly materialRendered: boolean;
  readonly identicalToBackground?: boolean;
}

interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly {
    readonly profileKey: string;
    readonly colorScheme: string;
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

function run(label: string, command: string, args: readonly string[]): void {
  process.stderr.write(`\n── ${label} ─────────────────────────────\n`);
  const result = spawnSync(command, args, { cwd: PACKAGE_ROOT, stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`compare: ${label} failed (exit ${String(result.status)})`);
  }
}

function main(): void {
  const argv = process.argv.slice(2);
  const flag = (name: string): string | undefined => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 ? argv[i + 1] : undefined;
  };

  const sceneId = flag("scene") ?? "checkerboard__capsule-button__rest";
  const renderer = flag("renderer") ?? "webgpu";
  const skipCapture = argv.includes("--skip-capture");

  const spec = readJson<SceneSpec>(resolve(REFERENCE, "scenes.json"));
  const scene = spec.scenes.find((s) => s.id === sceneId);
  if (scene === undefined) {
    throw new Error(`compare: '${sceneId}' is not in scenes.json`);
  }

  const fixtureSet = spec.split.holdout.includes(sceneId)
    ? "holdout"
    : spec.split.validation.includes(sceneId)
      ? "validation"
      : "calibration";

  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  const profileKey = flag("profile") ?? manifest.profiles[0]?.profileKey;
  if (profileKey === undefined) throw new Error("compare: the manifest declares no profiles");

  const profile = manifest.profiles.find((p) => p.profileKey === profileKey);
  if (profile === undefined) throw new Error(`compare: no profile '${profileKey}' in the manifest`);

  const fixture = profile.fixtures.find((f) => f.sceneId === sceneId);
  if (fixture === undefined) {
    throw new Error(`compare: profile '${profileKey}' has no fixture for scene '${sceneId}'`);
  }
  if (fixture.fixtureSet !== fixtureSet) {
    // The two files disagree about which split this scene is in. Refuse rather
    // than pick one: a scene that is holdout in one place and calibration in
    // another is exactly the failure the split exists to prevent.
    throw new Error(
      `compare: split mismatch for '${sceneId}' — scenes.json says ${fixtureSet}, ` +
        `manifest says ${fixture.fixtureSet}`,
    );
  }

  const backgroundFile = manifest.backgrounds[scene.background];
  if (backgroundFile === undefined) {
    throw new Error(`compare: the manifest has no background '${scene.background}'`);
  }

  const captureDir = resolve(PACKAGE_ROOT, "web-captures", sceneId);

  if (!skipCapture) {
    run("web capture", "npx", [
      "tsx",
      "scripts/capture-web.ts",
      sceneId,
      "--renderer",
      renderer,
      "--color-scheme",
      profile.colorScheme,
    ]);
  }

  // The capture step suffixes its output with the tier that drew, which is the
  // right call: the same scene captured on the GPU and CSS tiers are two
  // different measurements and must not overwrite one another.
  const webPng = resolve(captureDir, `${sceneId}__${renderer}.png`);
  const webCell = resolve(captureDir, `cell__${renderer}.json`);
  for (const path of [webPng, webCell]) {
    if (!existsSync(path)) {
      throw new Error(
        `compare: expected ${path} from the capture step` +
          (skipCapture ? " (running with --skip-capture; drop it to capture now)" : ""),
      );
    }
  }

  run("diff", "npx", [
    "tsx",
    "cli/diff.ts",
    "--native",
    resolve(FIXTURES, fixture.file),
    "--web",
    webPng,
    "--background",
    resolve(FIXTURES, backgroundFile),
    "--profile",
    profileKey,
    "--scene",
    sceneId,
    "--web-cell",
    webCell,
    "--fixture-set",
    fixtureSet,
    // The texture tier: the web capture's own cell reports samplingBackend
    // "gpu-texture", so this cell is a claim about vitrea's shader math rather
    // than about an engine's backdrop-filter.
    "--tier",
    "texture",
    "--out",
    resolve(captureDir, `report.cell__${renderer}.json`),
    "--matrix",
    resolve(PACKAGE_ROOT, "results", "matrix.json"),
  ]);

  process.stderr.write(`\n── what this run does and does not show ────────────\n`);
  process.stderr.write(`scene       ${sceneId}  (${fixtureSet})\n`);
  process.stderr.write(`native      ${fixture.file}\n`);
  process.stderr.write(`            captureMethod=${fixture.captureMethod} materialRendered=${String(fixture.materialRendered)}\n`);
  if (!fixture.materialRendered) {
    process.stderr.write(
      `\nThe native side of this comparison contains NO MATERIAL` +
        (fixture.identicalToBackground === true ? ` (it is pixel-identical to its background)` : ``) +
        `.\nEvery number above is therefore web-glass-vs-bare-background, not a fidelity\n` +
        `measurement. The pipeline is what this run demonstrates. Grant Screen\n` +
        `Recording and re-run the native harness to make these numbers mean something:\n` +
        `apps/reference-apple/README.md §"The capture wall".\n`,
    );
  }
}

try {
  main();
} catch (error) {
  process.stderr.write(`compare: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}
