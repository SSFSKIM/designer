/**
 * W29 G3 — seal the macOS 27 profile documents, and record their hashes before
 * the canonical read.
 *
 *   npx tsx results/2026-09-19-w29-g3-refit/seal.ts
 *
 * The documents are built here rather than by hand for one reason: a profile
 * document's `resolvedMaterialSha256` is a digest over the FULLY RESOLVED
 * material, and a hand-written digest is a number nobody checked. This resolves
 * each patch through the renderer's own `withMaterialOverrides` and fingerprints
 * it with the same canonicalising digest `test/tuned-profiles.test.ts` pins, so
 * the document and the test cannot disagree about what the material is.
 *
 * It also re-asserts, every time it runs, that the two 26.5 documents still
 * resolve to the digests they recorded — contract X1's half of this child, proved
 * by the same function that writes the new ones rather than by inspection.
 *
 * The 27 light document is a PATCH over the unmoved runtime default (Decision
 * Log 1 (i)), exactly as the 26.5 light document is — but it is not the identity
 * with it, and it says so: `identityWithRuntimeDefault` is absent, because only
 * one document can be the identity and that one is frozen.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const PROFILES = resolve(import.meta.dirname, "..", "..", "profiles");

function fingerprint(resolved: unknown): string {
  const canonical = (value: unknown): unknown =>
    Array.isArray(value)
      ? value.map(canonical)
      : value !== null && typeof value === "object"
        ? Object.fromEntries(
            Object.keys(value as object)
              .sort()
              .map((key) => [key, canonical((value as Record<string, unknown>)[key])]),
          )
        : value;
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);
}

const read = (name: string): Record<string, unknown> =>
  JSON.parse(readFileSync(resolve(PROFILES, `${name}.json`), "utf8")) as Record<string, unknown>;

/** X1: the two frozen documents still resolve to the digests they recorded. */
for (const name of ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard"]) {
  const document = read(name);
  const got = fingerprint(
    withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, document["patch"] as MaterialProfilePatch),
  );
  if (got !== document["resolvedMaterialSha256"]) {
    throw new Error(`${name}: resolved ${got}, recorded ${document["resolvedMaterialSha256"]} — X1`);
  }
  console.log(`X1 ok  ${name} resolves to ${got}`);
}

for (const name of [
  "apple-macos-27.0-1x-light-standard-glass0.5",
  "apple-macos-27.0-1x-dark-standard-glass0.5",
]) {
  const path = resolve(PROFILES, `${name}.json`);
  const document = JSON.parse(readFileSync(path, "utf8")) as Record<string, unknown>;
  const resolvedMaterialSha256 = fingerprint(
    withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, document["patch"] as MaterialProfilePatch),
  );
  document["resolvedMaterialSha256"] = resolvedMaterialSha256;
  writeFileSync(path, `${JSON.stringify(document, null, 2)}\n`);
  const file = createHash("sha256").update(readFileSync(path)).digest("hex");
  console.log(`sealed ${name}`);
  console.log(`  resolvedMaterialSha256 ${resolvedMaterialSha256}`);
  console.log(`  document sha256        ${file}`);
}
