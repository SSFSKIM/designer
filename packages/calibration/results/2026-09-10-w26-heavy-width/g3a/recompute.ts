/**
 * W26 G3a — the corrected `silhouetteIoU`, recomputed by the SHIPPED harness over
 * the committed 0.14.0 bed and checked against the G2 spike's Python replica.
 *
 * The spike (`../g2/extractor/`) transcribed the extractor into Python so the
 * rule could be scanned over parameters a full capture run does not expose, and
 * proved the transcription against all 613 committed shape cells before drawing
 * any conclusion from it. This script closes the loop from the other side: it
 * runs `cli/measure.ts`'s own imports — `componentRegion`, `extractSilhouette`,
 * `decidableRegion`, `silhouetteIoU` — over the same canonical inputs and
 * asserts two things per cell:
 *
 *   1. the UNCORRECTED IoU still reproduces the committed matrix bit for bit,
 *      which is what says the inputs and the extractor are the ones the matrix
 *      was written from; and
 *   2. the CORRECTED IoU equals the spike's `drop` column in `blast-rows.json`
 *      to the last digit.
 *
 * Read-only against every canonical input. `results/matrix.json`, the fixtures,
 * `scenes.json` and `web-captures/` are read and never written; the only files
 * this produces are `recompute.txt` and `recompute-rows.json` beside it.
 *
 *   VITREA_WEB_CAPTURES=/path/to/canonical/web-captures \
 *     npx tsx results/2026-09-10-w26-heavy-width/g3a/recompute.ts
 *
 * The captures are gitignored and live on the capture machine, so the env var is
 * how a checkout without them (a worktree, say) points at the canonical set.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  componentRegion,
  decidableRegion,
  decodePng,
  extractSilhouette,
  silhouetteIoU,
  type CalibrationImage,
  type CanvasSize,
  type DeclaredComponent,
  type Silhouette,
} from "../../../src/index";

const HERE = dirname(fileURLToPath(import.meta.url));
const PACKAGE = resolve(HERE, "../../..");
const REPO = resolve(PACKAGE, "../..");
const FIXTURES = resolve(REPO, "apps/reference-apple/fixtures");
const CAPTURES = process.env["VITREA_WEB_CAPTURES"] ?? resolve(PACKAGE, "web-captures");
const MATRIX_PATH = resolve(PACKAGE, "results/matrix.json");
const BLAST_PATH = resolve(HERE, "../g2/extractor/blast-rows.json");

/** The bed's extraction constants, as `compare` defaults them. */
const SILHOUETTE_THRESHOLD = 0.02;
const SILHOUETTE_CHROMA_THRESHOLD = 0.03;

interface Reading {
  readonly value: number;
}
interface MatrixCell {
  readonly key: { readonly profileKey: string; readonly sceneId: string; readonly web: { readonly renderer: string } };
  readonly tier: string;
  readonly fixtureSet: string;
  readonly shape?: Readonly<Record<string, Reading>>;
}
interface SceneMatrix {
  readonly canvas: CanvasSize;
  readonly components: Readonly<Record<string, DeclaredComponent>>;
  readonly scenes: readonly { readonly id: string; readonly component: string; readonly background: string }[];
}
interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly { readonly fixtures: readonly { readonly file: string }[] }[];
}
interface BlastRow {
  readonly tier: string;
  readonly scene: string;
  readonly profile: string;
  readonly base: number;
  readonly drop: number;
}

const readJson = <T,>(path: string): T => JSON.parse(readFileSync(path, "utf8")) as T;
const readPng = (path: string): CalibrationImage => decodePng(readFileSync(path));

const MATRIX = readJson<{ readonly cells: readonly MatrixCell[] }>(MATRIX_PATH);
const SCENES = readJson<SceneMatrix>(resolve(REPO, "apps/reference-apple/scenes.json"));
const MANIFEST = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
const BLAST = readJson<readonly BlastRow[]>(BLAST_PATH);

const FIXTURE_FILES = new Set(MANIFEST.profiles.flatMap((profile) => profile.fixtures.map((f) => f.file)));

function sceneOf(sceneId: string): SceneMatrix["scenes"][number] {
  const scene = SCENES.scenes.find((entry) => entry.id === sceneId);
  if (scene === undefined) throw new Error(`scenes.json declares no scene '${sceneId}'`);
  return scene;
}

/** The backing scale the profile key names — the same token the harness keys on. */
const scaleOf = (profileKey: string): number => (profileKey.includes("-2x-") ? 2 : 1);

function regionOf(sceneId: string, scale: number, image: CalibrationImage): Silhouette {
  const scene = sceneOf(sceneId);
  const component = SCENES.components[scene.component];
  if (component === undefined) throw new Error(`scenes.json lacks component '${scene.component}'`);
  return componentRegion(component, {
    canvas: SCENES.canvas,
    scale,
    width: image.width,
    height: image.height,
  }).silhouette;
}

function backgroundPath(sceneId: string, scale: number): string {
  const background = sceneOf(sceneId).background;
  const file = MANIFEST.backgrounds[`${background}@${scale}x`] ?? MANIFEST.backgrounds[background];
  if (file === undefined) throw new Error(`the manifest has no background '${background}' at ${scale}x`);
  return resolve(FIXTURES, file);
}

function nativePath(profileKey: string, sceneId: string): string {
  const file = `${profileKey}/${sceneId}.png`;
  if (!FIXTURE_FILES.has(file)) throw new Error(`the manifest declares no fixture '${file}'`);
  return resolve(FIXTURES, file);
}

interface Row {
  readonly tier: string;
  readonly set: string;
  readonly scene: string;
  readonly profile: string;
  readonly matrix: number;
  readonly base: number;
  readonly corrected: number;
  readonly spikeDrop: number;
}

function measure(): readonly Row[] {
  const rows: Row[] = [];
  for (const cell of MATRIX.cells) {
    if (cell.shape === undefined) continue;
    const { profileKey, sceneId } = cell.key;
    const scale = scaleOf(profileKey);
    const native = readPng(nativePath(profileKey, sceneId));
    const web = readPng(resolve(CAPTURES, profileKey, sceneId, `${sceneId}__${cell.key.web.renderer}.png`));
    const background = readPng(backgroundPath(sceneId, scale));
    const region = regionOf(sceneId, scale, native);
    const extractor = {
      kind: "luminance-delta",
      background,
      threshold: SILHOUETTE_THRESHOLD,
      chromaThreshold: SILHOUETTE_CHROMA_THRESHOLD,
      region,
    } as const;
    const nativeSil = extractSilhouette(native, extractor);
    const webSil = extractSilhouette(web, extractor);
    const spike = BLAST.find(
      (row) => row.tier === cell.tier && row.scene === sceneId && row.profile === profileKey,
    );
    if (spike === undefined) throw new Error(`blast-rows.json has no row for ${cell.tier} / ${sceneId} / ${profileKey}`);
    rows.push({
      tier: cell.tier,
      set: cell.fixtureSet,
      scene: sceneId,
      profile: profileKey,
      matrix: cell.shape["silhouetteIoU"]?.value ?? Number.NaN,
      base: silhouetteIoU(nativeSil, webSil),
      corrected: silhouetteIoU(nativeSil, webSil, decidableRegion(region, nativeSil, webSil)),
      spikeDrop: spike.drop,
    });
  }
  return rows;
}

/** The three `silhouetteIoU` regression floors of the committed bed. */
const FLOORS: readonly (readonly [string, string, string, number])[] = [
  ["dom", "checkerboard__glass-over-glass__rest", "apple-macos-26.5-1x-dark-standard", 0.907],
  ["texture", "checkerboard__glass-over-glass__rest", "apple-macos-26.5-2x-dark-standard", 0.9257],
  ["dom", "checkerboard__glass-over-glass__rest", "apple-macos-26.5-2x-dark-standard", 0.9038],
];

function main(): void {
  const rows = measure();
  const out: string[] = [];
  const say = (line = ""): void => {
    out.push(line);
    process.stdout.write(`${line}\n`);
  };

  const matrixExact = rows.filter((row) => row.base === row.matrix).length;
  const spikeExact = rows.filter((row) => row.corrected === row.spikeDrop).length;
  const worstMatrix = Math.max(...rows.map((row) => Math.abs(row.base - row.matrix)));
  const worstSpike = Math.max(...rows.map((row) => Math.abs(row.corrected - row.spikeDrop)));
  const movers = rows.filter((row) => row.corrected !== row.base);
  const deltas = movers.map((row) => row.corrected - row.base).sort((a, b) => a - b);
  const median = deltas.length === 0 ? 0 : (deltas[(deltas.length - 1) >> 1] ?? 0);

  say("W26 G3a — the shipped harness's corrected `silhouetteIoU` against the G2 spike");
  say("");
  say(`shape-bearing cells of the committed matrix   ${rows.length}`);
  say(`uncorrected IoU exactly equal to the matrix    ${matrixExact}   (worst |delta| ${worstMatrix.toExponential(3)})`);
  say(`corrected IoU exactly equal to the spike's     ${spikeExact}   (worst |delta| ${worstSpike.toExponential(3)})`);
  say("");
  say(`cells the correction moves                     ${movers.length}`);
  say(`of which DOWN                                  ${movers.filter((row) => row.corrected < row.base).length}`);
  say(`median move of the movers                      ${median >= 0 ? "+" : ""}${median.toFixed(5)}`);
  say(`largest move                                   +${Math.max(...deltas).toFixed(5)}`);
  say("");
  say("The three committed `silhouetteIoU` regression floors:");
  say(`${"floor row".padEnd(92)}${"floor".padStart(8)}${"base".padStart(10)}${"corrected".padStart(11)}`);
  for (const [tier, scene, profile, floor] of FLOORS) {
    const row = rows.find((r) => r.tier === tier && r.scene === scene && r.profile === profile);
    if (row === undefined) throw new Error(`no recomputed row for ${tier} / ${scene} / ${profile}`);
    const label = `${tier} / ${row.set} / ${scene} / ${profile}`;
    say(`${label.padEnd(92)}${floor.toFixed(4).padStart(8)}${row.base.toFixed(5).padStart(10)}${row.corrected.toFixed(5).padStart(11)}`);
  }
  say("");
  say("Every cell the correction moves, largest first:");
  say(
    `${"tier".padEnd(9)}${"set".padEnd(12)}${"profile".padEnd(46)}${"scene".padEnd(44)}` +
      `${"base".padStart(9)}${"corrected".padStart(11)}${"delta".padStart(10)}`,
  );
  for (const row of [...movers].sort((a, b) => b.corrected - b.base - (a.corrected - a.base))) {
    say(
      `${row.tier.padEnd(9)}${row.set.padEnd(12)}${row.profile.padEnd(46)}${row.scene.padEnd(44)}` +
        `${row.base.toFixed(5).padStart(9)}${row.corrected.toFixed(5).padStart(11)}` +
        `${(row.corrected - row.base >= 0 ? "+" : "") + (row.corrected - row.base).toFixed(5)}`.padStart(10),
    );
  }

  writeFileSync(resolve(HERE, "recompute.txt"), `${out.join("\n")}\n`);
  writeFileSync(resolve(HERE, "recompute-rows.json"), `${JSON.stringify(rows, null, 1)}\n`);

  if (matrixExact !== rows.length || spikeExact !== rows.length) {
    throw new Error("a cell disagrees — see recompute.txt; nothing downstream may use this run");
  }
}

main();
