/*
 * W25 G3 — the resolved material's fingerprint for the two profile documents.
 *
 * `tuned-profiles.test.ts` pins `resolvedMaterialSha256` over the FULLY RESOLVED material, so a
 * declaration that adds a constant to the renderer's default moves both documents' fingerprints
 * even where only one of them names the constant. This prints the digest each document's patch
 * resolves to at the working tree's defaults, so the declaration can re-record the number it
 * measured rather than the number it expected.
 *
 * The digest is the test's own: keys sorted at every depth, JSON, sha256, first sixteen hex digits
 * — restated here rather than imported because the test is a test and this is a tool, and a tool
 * that imported it would make the pin circular.
 *
 *   pnpm exec tsx results/2026-09-09-w25-thick-span-composite/g3/g3-fingerprint.mjs
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
} from "../../../../renderer-webgpu/src/material.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROFILES = resolve(HERE, "..", "..", "..", "profiles");

const canonical = (value) =>
  Array.isArray(value)
    ? value.map(canonical)
    : value !== null && typeof value === "object"
      ? Object.fromEntries(
          Object.keys(value)
            .sort()
            .map((key) => [key, canonical(value[key])]),
        )
      : value;

const fingerprint = (resolved) =>
  createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);

for (const name of [
  "apple-macos-26.5-1x-light-standard.json",
  "apple-macos-26.5-1x-dark-standard.json",
]) {
  const document = JSON.parse(readFileSync(resolve(PROFILES, name), "utf8"));
  const resolvedNow = fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, document.patch));
  const recorded = document.resolvedMaterialSha256;
  console.log(
    `${name.padEnd(44)} recorded ${recorded}  resolves to ${resolvedNow}` +
      (recorded === resolvedNow ? "  (unchanged)" : "  (RE-RECORD)"),
  );
}
