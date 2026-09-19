/**
 * W29 G3b — seal all four macOS 27 documents and record their hashes before the
 * canonical read.
 *
 *   npx tsx results/2026-09-19-w29-g3b-shadow-recede/seal.ts
 *
 * G3's `seal.ts` with the receded pair added, and the addition is the whole
 * reason this file exists rather than a re-run of that one: a document change
 * re-keys every row it drew, so the read has to be at a configuration whose
 * bytes are on the record, and the configuration is now four documents rather
 * than two.
 *
 * What it does, in the order it matters:
 *
 *   1. **X1, every run.** Both 26.5 documents still resolve, through the
 *      renderer's own `withMaterialOverrides`, to the digests they recorded.
 *      Proved by the same function that writes the new ones rather than by
 *      inspection.
 *   2. The two 27 ACTIVE documents are re-resolved and their
 *      `resolvedMaterialSha256` rewritten. G3 wrote these; this child moves the
 *      `outerShadow` block in them (Decision Log 6 (a)), so the digest moves
 *      with it and the old one is superseded rather than corrected — the number
 *      G3 recorded stays in §5.153 and in the rows it keyed.
 *   3. The two 27 RECEDED documents are resolved **over their own active
 *      document**, not over `DEFAULT_MATERIAL_PROFILE`, because that is what
 *      they are: a difference the page merges over the active patch before the
 *      root is built. A digest taken over the recede alone would be a digest of
 *      something that never draws.
 *
 * Nothing here computes a number a test does not also compute: the
 * fingerprinting is the canonicalising digest `test/tuned-profiles.test.ts`
 * pins, so the documents and the suite cannot disagree about what the material
 * is.
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

const path = (name: string): string => resolve(PROFILES, `${name}.json`);
const read = (name: string): Record<string, unknown> =>
  JSON.parse(readFileSync(path(name), "utf8")) as Record<string, unknown>;
const patchOf = (document: Record<string, unknown>): MaterialProfilePatch =>
  document["patch"] as MaterialProfilePatch;

/** X1: the two frozen documents still resolve to the digests they recorded. */
for (const name of ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard"]) {
  const document = read(name);
  const got = fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(document)));
  if (got !== document["resolvedMaterialSha256"]) {
    throw new Error(`${name}: resolved ${got}, recorded ${document["resolvedMaterialSha256"]} — X1`);
  }
  process.stdout.write(`X1 ok  ${name} resolves to ${got}\n`);
}

const ACTIVE = {
  light: "apple-macos-27.0-1x-light-standard-glass0.5",
  dark: "apple-macos-27.0-1x-dark-standard-glass0.5",
} as const;

const resolvedActive: Record<"light" | "dark", MaterialProfilePatch> = {} as never;

for (const scheme of ["light", "dark"] as const) {
  const name = ACTIVE[scheme];
  const document = read(name);
  const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(document));
  resolvedActive[scheme] = patchOf(document);
  document["resolvedMaterialSha256"] = fingerprint(material);
  writeFileSync(path(name), `${JSON.stringify(document, null, 2)}\n`);
  const file = createHash("sha256").update(readFileSync(path(name))).digest("hex");
  process.stdout.write(
    `sealed ${name}\n  resolvedMaterialSha256 ${String(document["resolvedMaterialSha256"])}\n` +
      `  document sha256        ${file}\n  capturePath sha256     ${file.slice(0, 12)}\n`,
  );
}

for (const scheme of ["light", "dark"] as const) {
  const name = `${ACTIVE[scheme]}-receded`;
  const document = read(name);
  /*
   * Over the active patch, then over the defaults — the composition the page
   * performs, in the page's order. `withMaterialOverrides` merges leaf by leaf
   * one level down, so applying the two patches in sequence is the same material
   * the single merged patch resolves to, and doing it in two steps is what makes
   * the dependency on the active document explicit in this file.
   */
  const material = withMaterialOverrides(
    withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, resolvedActive[scheme]),
    patchOf(document),
  );
  document["resolvedMaterialSha256"] = fingerprint(material);
  document["resolvedOverActiveDocument"] = `${ACTIVE[scheme]}.json`;
  writeFileSync(path(name), `${JSON.stringify(document, null, 2)}\n`);
  const file = createHash("sha256").update(readFileSync(path(name))).digest("hex");
  process.stdout.write(
    `sealed ${name}\n  resolvedMaterialSha256 ${String(document["resolvedMaterialSha256"])}\n` +
      `  document sha256        ${file}\n  capturePath sha256     ${file.slice(0, 12)}\n`,
  );
}
