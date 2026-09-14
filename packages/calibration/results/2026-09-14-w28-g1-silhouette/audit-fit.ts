/** Audit completed sweep membership, repeat counts and unchanged runtime provenance. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { admitFitRows } from "./admission";

const here = dirname(fileURLToPath(import.meta.url));
const json = (file: string): any => JSON.parse(readFileSync(resolve(here, file), "utf8"));
const partition = json("partition.json");
const partitionSha = createHash("sha256").update(readFileSync(resolve(here, "partition.json"))).digest("hex");
const jobs = json("sweep-jobs.json");
const holdout = new Set<string>(partition.holdout);
let source: string | undefined;
let instrument: string | undefined;
let total = 0;
const records = [];
for (const job of jobs) {
  const matrix = json(`sweep-matrices/${job.label}.json`);
  const expected = partition.rows.filter((r: any) => r.scheme === job.scheme && r.a11yMode === "standard")
    .map((r: any) => r.cell).sort();
  const actual = matrix.rows.map((r: any) => `${r.profile}/${r.scene}`).sort();
  if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(`${job.label}: incomplete/duplicate rows`);
  admitFitRows(matrix.rows, holdout);
  if (matrix.renderer !== "webgpu" || matrix.rows.some((r: any) => r.scored || r.repeats !== 2)) {
    throw new Error(`${job.label}: wrong tier, scoring membership or repeat count`);
  }
  if (matrix.partitionSha256 !== partitionSha) throw new Error(`${job.label}: partition drift`);
  const currentSource = JSON.stringify(matrix.sourceSha256);
  source ??= currentSource;
  instrument ??= matrix.instrumentSha256;
  if (source !== currentSource || instrument !== matrix.instrumentSha256) {
    throw new Error(`${job.label}: runtime or instrument changed during the fit`);
  }
  if (matrix.machineAccessibility.reduceTransparency !== 0 || matrix.machineAccessibility.increaseContrast !== 0) {
    throw new Error(`${job.label}: machine preferences were not both off`);
  }
  total += actual.length;
  records.push({ label: job.label, rows: actual.length, head: matrix.repositoryHead,
    patchSha256: matrix.patchSha256, inactiveSha256: matrix.inactiveSha256 });
}
writeFileSync(resolve(here, "fit-audit.json"), `${JSON.stringify({
  rungs: records.length, rows: total, capturesIncludingRepeat: total * 2,
  checkingRows: 0, holdoutRows: 0, allAccessibilityOff: true,
  unchangedRuntimeAndInstrument: true, partitionSha256: partitionSha, records,
}, null, 2)}\n`);
console.log(`${records.length} rungs, ${total} rows, no D/holdout rows, one unchanged runtime/instrument`);
