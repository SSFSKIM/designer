/**
 * `diff` — measure ONE native/web pair and write its per-axis report.
 *
 * Usage — note that `pnpm --filter` runs in the package directory, so relative
 * paths resolve from `packages/calibration/`, not the repo root:
 *
 *   pnpm --filter @vitrea/calibration run diff -- \
 *     --native  ../../apps/reference-apple/fixtures/<profile>/<scene>.png \
 *     --web     web-captures/<scene>/<scene>__webgpu.png \
 *     --background ../../apps/reference-apple/fixtures/backgrounds/<bg>@1x.png \
 *     --profile apple-macos-26.5-1x-light-standard \
 *     --scene   checkerboard__capsule-button__rest \
 *     --web-cell web-captures/<scene>/cell__webgpu.json \
 *     --matrix  results/matrix.json
 *
 * The measurement itself lives in `measure.ts`, shared with `compare`, so the
 * single-pair and whole-matrix routes cannot drift into measuring two different
 * things. This file is argument parsing and file writing, and nothing else.
 *
 * **No thresholds and no verdict.** The exit code says whether the measurement
 * ran, never whether the numbers are good.
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  createResultMatrix,
  deserializeResultMatrix,
  parseProfileKey,
  serializeResultMatrix,
  upsertCellResult,
  RESULT_MATRIX_SCHEMA_VERSION,
  type FidelityTier,
  FIXTURE_SETS,
  type FixtureSet,
} from "../src/index";
import { matrixSchemaRefusal } from "./gates";
import { DEFAULT_SILHOUETTE_THRESHOLD, measureCell, type MeasureInput } from "./measure";
import { declaredComponentOf, readSceneGeometry } from "./scene-geometry";

const REFERENCE = resolve(
  fileURLToPath(new URL(".", import.meta.url)),
  "..",
  "..",
  "..",
  "apps",
  "reference-apple",
);

interface Args extends MeasureInput {
  readonly matrix?: string;
  readonly out?: string;
}

function parseArgs(argv: readonly string[]): Args {
  const map = new Map<string, string>();
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === undefined || !token.startsWith("--")) continue;
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) {
      map.set(token.slice(2), "true");
    } else {
      map.set(token.slice(2), next);
      i += 1;
    }
  }

  const need = (name: string): string => {
    const v = map.get(name);
    if (v === undefined) throw new Error(`diff: --${name} is required`);
    return v;
  };

  const profileKey = need("profile");
  const profile = parseProfileKey(profileKey);
  if (profile === null) {
    throw new Error(
      `diff: --profile '${profileKey}' does not match X9's profile-key grammar ` +
        `(apple-<platform>-<os>-<scale>x-<scheme>-<a11y>)`,
    );
  }

  /*
   * The declared geometry the instrument bounds its search to (schema 5), read
   * from the scene matrix rather than taken as a flag. The scene id and the
   * profile key between them already determine it, and a hand-passed rect could
   * disagree with the one the harnesses laid the scene out from — which would be
   * indistinguishable from a fidelity finding.
   */
  const sceneId = need("scene");
  const geometry = readSceneGeometry(REFERENCE);

  const tier = map.get("tier") ?? "texture";
  if (tier !== "texture" && tier !== "dom") {
    throw new Error(`diff: --tier must be 'texture' or 'dom', got '${tier}'`);
  }

  const fixtureSet = map.get("fixture-set") ?? "calibration";
  if (!(FIXTURE_SETS as readonly string[]).includes(fixtureSet)) {
    throw new Error(`diff: --fixture-set must be ${FIXTURE_SETS.join("|")}, got '${fixtureSet}'`);
  }

  const blurAxis = map.get("blur-axis") ?? "x";
  if (blurAxis !== "x" && blurAxis !== "y") {
    throw new Error(`diff: --blur-axis must be 'x' or 'y', got '${blurAxis}'`);
  }

  let blurRegion: readonly [number, number, number, number] | undefined;
  const rawRegion = map.get("blur-region");
  if (rawRegion !== undefined && rawRegion !== "true") {
    const parts = rawRegion.split(",").map((p) => Number.parseInt(p.trim(), 10));
    if (parts.length !== 4 || parts.some((p) => !Number.isFinite(p))) {
      throw new Error(`diff: --blur-region must be 'x,y,width,height', got '${rawRegion}'`);
    }
    blurRegion = [parts[0] as number, parts[1] as number, parts[2] as number, parts[3] as number];
  }

  // Optional fields are spread in only when present: `exactOptionalPropertyTypes`
  // distinguishes "absent" from "present and undefined", and that distinction is
  // one this package leans on everywhere else (an absent axis means not measured,
  // never measured as zero), so the CLI honours it too.
  const backgroundPath = map.get("background");
  const matrix = map.get("matrix");
  const out = map.get("out");

  return {
    nativePath: need("native"),
    webPath: need("web"),
    profileKey,
    sceneId,
    webCellPath: need("web-cell"),
    tier: tier as FidelityTier,
    fixtureSet: fixtureSet as FixtureSet,
    blurAxis,
    silhouetteThreshold: Number(map.get("silhouette-threshold") ?? `${DEFAULT_SILHOUETTE_THRESHOLD}`),
    component: declaredComponentOf(geometry, sceneId),
    canvas: geometry.canvas,
    scale: profile.scale,
    ...(backgroundPath === undefined ? {} : { backgroundPath }),
    ...(matrix === undefined ? {} : { matrix }),
    ...(out === undefined ? {} : { out }),
    ...(blurRegion === undefined ? {} : { blurRegion }),
  };
}

function main(): void {
  const args = parseArgs(process.argv.slice(2));

  // Checked before measuring, and for the reason `compare` checks before
  // capturing: a matrix written under another schema can be neither read nor
  // merged into, and `results/matrix.json` is frozen under one for the duration
  // of the interregnum. See `matrixSchemaRefusal`.
  if (args.matrix !== undefined && existsSync(args.matrix)) {
    const onDisk: unknown = JSON.parse(readFileSync(args.matrix, "utf8"));
    const version = (onDisk as { schemaVersion?: unknown }).schemaVersion;
    const refusal =
      typeof version === "number"
        ? matrixSchemaRefusal(version, RESULT_MATRIX_SCHEMA_VERSION, args.matrix)
        : `${args.matrix} has no numeric schemaVersion, so it is not a result matrix.`;
    if (refusal !== undefined) throw new Error(`diff: ${refusal}`);
  }

  const { cell, notes } = measureCell(args);

  const reportJson = JSON.stringify(cell, null, 2);
  if (args.out !== undefined) {
    mkdirSync(dirname(args.out), { recursive: true });
    writeFileSync(args.out, `${reportJson}\n`);
    process.stderr.write(`report → ${args.out}\n`);
  } else {
    process.stdout.write(`${reportJson}\n`);
  }

  if (args.matrix !== undefined) {
    const existing = existsSync(args.matrix)
      ? deserializeResultMatrix(readFileSync(args.matrix, "utf8"))
      : createResultMatrix();
    const updated = upsertCellResult(existing, cell);
    mkdirSync(dirname(args.matrix), { recursive: true });
    writeFileSync(args.matrix, `${serializeResultMatrix(updated, { pretty: true })}\n`);
    process.stderr.write(`matrix → ${args.matrix}\n`);
  }

  for (const note of notes) process.stderr.write(`note: ${note}\n`);
}

main();
