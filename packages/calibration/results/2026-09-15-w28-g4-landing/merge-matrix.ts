/**
 * Fold the scratch inactive matrix into the canonical one, under X11's rule
 * (W28 G4, claims §5.148).
 *
 * The inactive run writes to scratch rather than straight into `results/matrix.json`
 * so that the canonical file changes exactly once, in a step that can say what it
 * did. What that step must be able to say is X11's promise: **the active material
 * does not move**. So every existing cell is compared with itself after the merge,
 * by its serialised bytes, and every added cell must be a new key of a declared
 * inactive scene. Anything else refuses, and the canonical file is not written.
 *
 *   tsx results/2026-09-15-w28-g4-landing/merge-matrix.ts --from /tmp/…/inactive-matrix.json
 *
 * `--check` reads and reports without writing.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  deserializeResultMatrix,
  serializeResultMatrix,
  upsertCellResult,
  RESULT_MATRIX_SCHEMA_VERSION,
  type CellResult,
  type ResultMatrix,
} from "../../src/index";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");

const arg = (name: string, fallback?: string): string => {
  const index = process.argv.indexOf(`--${name}`);
  const value = index < 0 ? fallback : process.argv[index + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};
const from = resolve(arg("from"));
const canonicalPath = resolve(pkg, "results/matrix.json");

const declaration = JSON.parse(
  readFileSync(resolve(repo, "apps/reference-apple/scenes.json"), "utf8"),
) as { readonly scenes: readonly { readonly id: string; readonly state: string }[] };
const inactiveScenes = new Set(
  declaration.scenes.filter((scene) => scene.state === "inactive").map((scene) => scene.id),
);

const canonical: ResultMatrix = deserializeResultMatrix(readFileSync(canonicalPath, "utf8"));
const incoming: ResultMatrix = deserializeResultMatrix(readFileSync(from, "utf8"));
if (canonical.schemaVersion !== RESULT_MATRIX_SCHEMA_VERSION) {
  throw new Error(`canonical matrix is schema ${canonical.schemaVersion}`);
}

const before = new Map(canonical.cells);
const refusals: string[] = [];
let merged = canonical;
const added: string[] = [];

for (const [key, cell] of incoming.cells) {
  if (before.has(key)) {
    // A key already in the canonical file is an ACTIVE row being overwritten, or the
    // same inactive row measured twice in one landing. Either way this step does not
    // decide it: it stops and names the key.
    refusals.push(`${key}: already in the canonical matrix`);
    continue;
  }
  if (cell.state !== "inactive" || !inactiveScenes.has(cell.key.sceneId)) {
    refusals.push(
      `${key}: state ${String(cell.state)} / declared ${inactiveScenes.has(cell.key.sceneId)}`,
    );
    continue;
  }
  merged = upsertCellResult(merged, cell as CellResult);
  added.push(key);
}

// The promise, read rather than argued: every key the canonical file already held
// still serialises to exactly the bytes it did.
const moved: string[] = [];
for (const [key, cell] of before) {
  const now = merged.cells.get(key);
  if (now === undefined) {
    moved.push(`${key}: dropped`);
    continue;
  }
  if (JSON.stringify(now) !== JSON.stringify(cell)) moved.push(`${key}: changed`);
}

const report = {
  gate: "W28 G4 — the inactive rows enter the canonical matrix",
  claims: "§5.148",
  from,
  canonical: canonicalPath.replace(`${repo}/`, ""),
  schemaVersion: merged.schemaVersion,
  cellsBefore: before.size,
  cellsIncoming: incoming.cells.size,
  cellsAdded: added.length,
  cellsAfter: merged.cells.size,
  existingCellsMoved: moved,
  refusals,
};
process.stdout.write(`${JSON.stringify(report, undefined, 2)}\n`);

if (refusals.length > 0 || moved.length > 0) {
  process.stderr.write("REFUSED — the canonical matrix is unchanged.\n");
  process.exit(1);
}
if (process.argv.includes("--check")) process.exit(0);

writeFileSync(canonicalPath, `${serializeResultMatrix(merged, { pretty: true })}\n`);
const reportPath = resolve(here, "merge-matrix.json");
if (existsSync(reportPath)) throw new Error(`${reportPath} exists; refusing to overwrite evidence`);
writeFileSync(reportPath, `${JSON.stringify(report, undefined, 2)}\n`);
process.stderr.write(`matrix → ${canonicalPath} (${merged.cells.size} cells)\n`);
