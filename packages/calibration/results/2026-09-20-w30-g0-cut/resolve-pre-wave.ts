/**
 * W30 G0 (a) — the PRE-WAVE resolved macOS 26.5 materials, written to disk before
 * any leaf of either operator exists.
 *
 *   npx tsx results/2026-09-20-w30-g0-cut/resolve-pre-wave.ts
 *
 * Acceptance clause 1 asks for a proof that the exemption is inert at the
 * material level, and a digest cannot be that proof on its own: after G2 lands
 * the leaves the digest MOVES by construction, which is the whole reason the
 * exemption exists. What does not move is every OTHER leaf of the resolved
 * material, and the only way to assert that is to have the pre-wave material
 * itself on disk, byte for byte, before the first leaf is added.
 *
 * So this writes it. The path is the fingerprint's own —
 * `withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch)` resolved through the
 * renderer, then canonicalised with keys sorted — so the file is the same value
 * `results/2026-09-19-w29-g3-refit/seal.ts` and `test/tuned-profiles.test.ts`
 * hash, and the digest it prints is the pinned `resolvedMaterialSha256` or this
 * script throws.
 *
 * Two digests are printed per document and they are different things:
 *   - `resolved fingerprint` is SHA-256 over the canonical JSON of the resolved
 *     material, first 16 hex — the document's own `resolvedMaterialSha256`.
 *   - `file sha256` is SHA-256 over the bytes this script writes, full length —
 *     what `test/w30-operator-identity.test.ts` reads the file back through.
 *
 * X1: this script writes nothing under a macOS 26.5-keyed path. The two JSON
 * files land in this wave's evidence directory, which is new.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "profiles");

/** Keys sorted at every depth — `seal.ts`'s `canonical`, and the same value. */
function canonical(value: unknown): unknown {
  return Array.isArray(value)
    ? value.map(canonical)
    : value !== null && typeof value === "object"
      ? Object.fromEntries(
          Object.keys(value as object)
            .sort()
            .map((key) => [key, canonical((value as Record<string, unknown>)[key])]),
        )
      : value;
}

function fingerprint(resolved: unknown): string {
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);
}

const DOCUMENTS = [
  ["apple-macos-26.5-1x-light-standard", "resolved-26.5-light.json", "b2b570e4adcea8fb"],
  ["apple-macos-26.5-1x-dark-standard", "resolved-26.5-dark.json", "874be66ea501621b"],
] as const;

for (const [key, out, pinned] of DOCUMENTS) {
  const document = JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as {
    patch: MaterialProfilePatch;
    resolvedMaterialSha256: string;
  };
  const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, document.patch);
  const digest = fingerprint(resolved);
  if (digest !== document.resolvedMaterialSha256) {
    throw new Error(
      `${key}: resolved ${digest}, document records ${document.resolvedMaterialSha256}`,
    );
  }
  if (digest !== pinned) {
    throw new Error(`${key}: resolved ${digest}, the charter's Grounding records ${pinned}`);
  }
  const path = resolve(HERE, out);
  writeFileSync(path, `${JSON.stringify(canonical(resolved), null, 2)}\n`);
  const file = createHash("sha256").update(readFileSync(path)).digest("hex");
  console.log(`${key}`);
  console.log(`  -> ${out}`);
  console.log(`  resolved fingerprint  ${digest}  (document and charter agree)`);
  console.log(`  file sha256           ${file}`);
}
