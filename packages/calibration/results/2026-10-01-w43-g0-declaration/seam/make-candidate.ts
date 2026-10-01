/**
 * The byte-identity proof's candidate (W43 G0 (f)): the four shipped `-glass0.5` documents'
 * content, relabelled to scratch `-glass0.25` keys, and a candidate declaration naming the
 * four copies and their CSS mapping by hash.
 *
 *   cd packages/calibration && npx tsx results/2026-10-01-w43-g0-declaration/seam/make-candidate.ts
 *
 * Only `profileKey` changes in each copy, plus one comment key saying what the file is; the
 * patch, the CSS mapping and the recorded digest are the 0.5 document's, byte for byte as
 * values. Deterministic, so re-running it reproduces the committed files and hashes.
 */

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { CANDIDATE_DECLARATION_KIND, cssTierMappingSha256 } from "../../../scripts/candidate-document";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROFILES = resolve(HERE, "../../../profiles");
const OUT = join(HERE, "scratch-candidate");

const SOURCES = {
  "active.light": "apple-macos-27.0-1x-light-standard-glass0.5",
  "active.dark": "apple-macos-27.0-1x-dark-standard-glass0.5",
  "receded.light": "apple-macos-27.0-1x-light-standard-glass0.5-receded",
  "receded.dark": "apple-macos-27.0-1x-dark-standard-glass0.5-receded",
} as const;

mkdirSync(OUT, { recursive: true });
const endpoints: Record<string, { path: string; sha256: string }> = {};
let mapping: unknown;
for (const [slot, key] of Object.entries(SOURCES)) {
  const source = JSON.parse(readFileSync(join(PROFILES, `${key}.json`), "utf8")) as Record<string, unknown>;
  const copy: Record<string, unknown> = {
    "$comment-w43-g0-scratch": [
      `SCRATCH, W43 G0 (f): the content of profiles/${key}.json under a scratch -glass0.25 key,`,
      "for the candidate-mode byte-identity proof only. Not a measured 0.25 material.",
    ],
  };
  for (const [field, value] of Object.entries(source)) {
    copy[field] = field === "profileKey" ? (value as string).replace("-glass0.5", "-glass0.25") : value;
  }
  const text = `${JSON.stringify(copy, null, 2)}\n`;
  const file = `${slot}.json`;
  writeFileSync(join(OUT, file), text);
  endpoints[slot] = { path: file, sha256: createHash("sha256").update(text).digest("hex") };
  if (slot === "active.light") mapping = source["cssTierMapping"];
}

const declaration = {
  "$comment": "W43 G0 (f) byte-identity proof: the 0.5 documents' content under scratch 0.25 keys.",
  kind: CANDIDATE_DECLARATION_KIND,
  schemaVersion: 1,
  name: "apple-macos-27.0-glass0.25-w43-g0-scratch",
  platform: "macOS 27.0",
  glassTintAmount: 0.25,
  endpoints,
  cssTierMappingSha256: cssTierMappingSha256(mapping),
};
writeFileSync(join(OUT, "candidate.json"), `${JSON.stringify(declaration, null, 2)}\n`);
console.log(`wrote ${Object.keys(endpoints).length} endpoint copies and candidate.json to ${OUT}`);
