/**
 * W43 G2 (f), review closure: the unmoved endpoint read through the masks G3 will read it through.
 *
 * S1's anti-null is a 0.25 endpoint that renders exactly the pixels vitrea renders at 0.5. G3 reads
 * `interiorMean` off the matrix rows, and `cli/measure.ts` measures a row's web image through that
 * row's NATIVE silhouette (`interior = nativeSil`). So the unmoved endpoint's 0.25 row would read the
 * 0.5 web capture through Apple's 0.25 silhouette, not its 0.5 one, and its change is
 *
 *   V = I(web@0.5 under the 0.25 native silhouette) − interiorMeanWeb(0.5 row),
 *
 * which is zero only where the two silhouettes coincide. This reads both terms, per non-holdout cell
 * and tier: the 0.5 web capture from the canonical tree under the 0.25 fixture's silhouette, and the
 * same capture under the 0.5 fixture's silhouette, which must reproduce the row's interiorMeanWeb.
 * The silhouettes come from the native delta's `readCapture`, whose extraction reproduces the rows'
 * interiorMeanNative exactly (`s1-null.txt`, reader checks).
 *
 *   cd packages/calibration
 *   npx tsx results/2026-10-02-w43-g2-reading/s1/anti-null-reader.ts [--tree <web-captures dir>]
 *
 * Writes `anti-null-readings.json` beside itself. Read-only on the tree.
 */

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { contextFor, load, readJson, FIXTURES, REFERENCE, type Manifest } from "../../../cli/native-delta";
import { readCapture } from "../../../cli/native-delta-metrics";
import { readSceneGeometry } from "../../../cli/scene-geometry";
import { interiorLevel, type CalibrationImage } from "../../../src/index";

const HERE = resolve(fileURLToPath(new URL(".", import.meta.url)));
const NON_HOLDOUT = new Set(["calibration", "validation", "recorded", "probe"]);
const TIERS = ["webgpu", "css"] as const;

const argv = process.argv.slice(2);
const at = argv.indexOf("--tree");
const tree =
  at >= 0 && argv[at + 1] !== undefined
    ? resolve(argv[at + 1] as string)
    : "/Users/new/Developer/GitHub/designer/packages/calibration/web-captures";

interface DeltaRow {
  readonly profileKey: string;
  readonly counterpartProfileKey: string;
  readonly sceneId: string;
  readonly fixtureSet: string;
}

const delta = JSON.parse(readFileSync(resolve(HERE, "..", "delta", "slider-delta.json"), "utf8")) as {
  readonly rows: readonly DeltaRow[];
};
const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
const spec = readJson<{ readonly scenes: readonly { readonly id: string; readonly background: string }[] }>(
  resolve(REFERENCE, "scenes.json"),
);
const geometry = readSceneGeometry(REFERENCE);
const backgrounds = new Map<string, CalibrationImage>();
const fileOf = new Map<string, string>();
for (const profile of manifest.profiles) {
  for (const fixture of profile.fixtures) fileOf.set(`${profile.profileKey} ${fixture.sceneId}`, fixture.file);
}

const out: Record<string, unknown>[] = [];
let read = 0;
for (const row of delta.rows) {
  if (!NON_HOLDOUT.has(row.fixtureSet)) continue;
  const file25 = fileOf.get(`${row.profileKey} ${row.sceneId}`);
  const file05 = fileOf.get(`${row.counterpartProfileKey} ${row.sceneId}`);
  if (file25 === undefined || file05 === undefined) throw new Error(`no fixture for ${row.sceneId}`);
  const fixture25 = load(resolve(FIXTURES, file25));
  const fixture05 = load(resolve(FIXTURES, file05));
  const context = contextFor(
    row.sceneId,
    row.counterpartProfileKey,
    manifest,
    spec,
    geometry,
    fixture05.width,
    fixture05.height,
    backgrounds,
  );
  if (context === null) throw new Error(`no context for ${row.sceneId}`);
  const sil25 = readCapture(fixture25, context.background, context.geometry);
  const sil05 = readCapture(fixture05, context.background, context.geometry);
  for (const tier of TIERS) {
    const capture = resolve(tree, row.counterpartProfileKey, row.sceneId, `${row.sceneId}__${tier}.png`);
    const entry: Record<string, unknown> = {
      profileKey: row.profileKey,
      sceneId: row.sceneId,
      tier,
      area25: sil25.area,
      area05: sil05.area,
    };
    if (!existsSync(capture)) {
      entry.status = "no capture in the tree";
    } else if (sil25.area === 0 || sil05.area === 0) {
      entry.status = "an empty native silhouette";
    } else {
      const web = load(capture);
      entry.status = "measured";
      entry.webUnder025 = interiorLevel(web, { interior: sil25.silhouette }).mean;
      entry.webUnder05 = interiorLevel(web, { interior: sil05.silhouette }).mean;
      read += 1;
    }
    out.push(entry);
  }
}
writeFileSync(
  resolve(HERE, "anti-null-readings.json"),
  `${JSON.stringify({ tree, readings: out }, null, 1)}\n`,
);
process.stdout.write(`anti-null reader: ${String(read)} tier-cells read from ${tree}\n`);
