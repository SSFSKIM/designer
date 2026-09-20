/**
 * The bytes the canonical macOS 27 rows were read under are the bytes the runtime
 * now ships (W29 G4, claims §5.155; acceptance clause 5's honesty half).
 *
 * Two joins, and the second is the one that matters.
 *
 * **(1) The shipped patch equals the document's patch.** `@vitreajs/vitrea-web`
 * carries the four macOS 27 patches as generated source, so there are two copies
 * of every number and drift is possible. `macos27-profile-export.test.ts` deep-
 * equals them on every run; this prints the digest over each serialised pair so
 * the ledger can quote one line instead of "a test passes".
 *
 * **(2) The document the runtime ships is the document the rows were measured
 * at.** Every cell in `results/matrix.json` records its material profile document
 * and that document's content hash in its own `capturePath` — which is what makes
 * a refit append a generation rather than overwrite one. So the join is: take the
 * SHA-256 of each profile document on disk, and check that it is the hash the
 * newest macOS 27 row of every cell names. Where it is, the material this release
 * selects is the material W29 G3b read the bed with, and no re-read is needed to
 * say so.
 *
 * A cell whose newest row names an EARLIER generation is counted and named rather
 * than hidden: it means the later read produced no row for that cell, which is a
 * fact about the bed and not about the documents. §5.154 records the one such
 * cell this bed has.
 *
 *     node packages/calibration/results/2026-09-20-w29-g4-landing/document-identity.mjs
 *
 * It exits nonzero if a shipped patch differs from its document, or if any macOS
 * 27 row names a document the runtime does not ship at all. This is a proof, not
 * a report.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  macos27DarkMaterialProfile,
  macos27LightMaterialProfile,
  macos27MaterialProfileDocument,
  macos27RecededMaterialProfile,
} from "@vitreajs/vitrea-web";

const here = dirname(fileURLToPath(import.meta.url));
const profiles = resolve(here, "../../profiles");
const matrixPath = resolve(here, "../matrix.json");

const digest = (value) => createHash("sha256").update(JSON.stringify(value)).digest("hex");
const fileHash = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");

const CASES = [
  ["active light", macos27LightMaterialProfile, "apple-macos-27.0-1x-light-standard-glass0.5"],
  ["active dark", macos27DarkMaterialProfile, "apple-macos-27.0-1x-dark-standard-glass0.5"],
  [
    "receded light",
    macos27RecededMaterialProfile.light,
    "apple-macos-27.0-1x-light-standard-glass0.5-receded",
  ],
  [
    "receded dark",
    macos27RecededMaterialProfile.dark,
    "apple-macos-27.0-1x-dark-standard-glass0.5-receded",
  ],
];

let failures = 0;
const say = (line) => process.stdout.write(`${line}\n`);

say("(1) the shipped patch against the profile document's patch");
const hashes = new Map();
for (const [what, shipped, key] of CASES) {
  const path = resolve(profiles, `${key}.json`);
  const document = JSON.parse(readFileSync(path, "utf8"));
  const a = digest(shipped);
  const b = digest(document.patch);
  const file = fileHash(path);
  hashes.set(key, file);
  const ok = a === b;
  if (!ok) failures += 1;
  say(`  ${what.padEnd(14)} ${ok ? "equal" : "DIFFER"}  patch sha256 ${a.slice(0, 16)}`);
  say(`  ${"".padEnd(14)} document ${key}`);
  say(`  ${"".padEnd(14)} file sha256 ${file.slice(0, 12)}  resolvedMaterialSha256 ${document.resolvedMaterialSha256}`);
}

say("");
say("(2) the newest macOS 27 rows, against those file hashes");
const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));
const newest = new Map();
for (const cell of matrix.cells) {
  if (!cell.key.profileKey.startsWith("apple-macos-27.0-")) continue;
  const id = `${cell.key.profileKey}|${cell.key.sceneId}|${cell.tier}`;
  const held = newest.get(id);
  if (held === undefined || cell.capturedAt > held.capturedAt) newest.set(id, cell);
}
const shippedHashes = new Set([...hashes.values()].map((hash) => hash.slice(0, 12)));
const behind = [];
const unknown = [];
for (const [id, cell] of newest) {
  const cited = [
    ...cell.key.web.capturePath.matchAll(/profiles\/([\w.\-]+)\.json sha256:(\w+)/g),
  ].map(([, key, hash]) => ({ key, hash }));
  if (cited.length === 0) {
    unknown.push([id, "names no profile document"]);
    continue;
  }
  for (const { key, hash } of cited) {
    if (!hashes.has(key)) unknown.push([id, `${key} is not a shipped document`]);
    else if (!shippedHashes.has(hash)) behind.push([id, `${key} at ${hash}`, cell.capturedAt]);
  }
}
const profiles27 = new Set([...newest.values()].map((cell) => cell.key.profileKey));
say(`  ${newest.size} newest macOS 27 cells across ${profiles27.size} profiles`);
say(`  at a shipped document hash: ${newest.size - behind.length - unknown.length}`);
say(`  at an earlier generation:   ${behind.length}`);
for (const [id, what, at] of behind) say(`    ${id}  ${what}  ${at}`);
say(`  naming an unshipped document: ${unknown.length}`);
for (const [id, why] of unknown) say(`    ${id}  ${why}`);
failures += unknown.length;
for (const [key, hash] of [...hashes].sort()) {
  say(`  shipped ${key.padEnd(52)} ${hash.slice(0, 12)}`);
}

say("");
say(`document name: ${macos27MaterialProfileDocument.name} (${macos27MaterialProfileDocument.platform})`);
say(failures === 0 ? "all joins hold" : `${failures} join(s) failed`);
process.exit(failures === 0 ? 0 : 1);
