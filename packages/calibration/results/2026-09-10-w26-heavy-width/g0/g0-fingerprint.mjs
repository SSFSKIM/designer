/**
 * W26 G0 — the resolved material's fingerprint, recomputed.
 *
 * `test/tuned-profiles.test.ts` digests the FULLY RESOLVED material, keys sorted, so the digest
 * moves when the shape of `MaterialProfile` moves and not only when a value does. This spike adds
 * four constants at zero, which moves the shape without moving one rendered pixel — the 33 goldens
 * and the bed's 36 reproduced captures are the proof of that — so the fingerprint is re-recorded
 * and the reason is written into the profile beside it, which is exactly what the test's own
 * message asks for.
 *
 * Prints the old and the new digest for both documents. It writes nothing; the profiles are edited
 * by hand so the `$comment` that explains the move is written in the same breath.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PACKAGE = resolve(HERE, "..", "..", "..");
// The renderer's SOURCE, through `tsx` — the built `dist` uses extensionless internal specifiers
// that plain node cannot resolve, and the material is one pure module either way.
const { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } = await import(
  resolve(PACKAGE, "..", "renderer-webgpu", "src", "material.ts")
);

const fingerprint = (value) => {
  const canonical = (v) =>
    Array.isArray(v)
      ? v.map(canonical)
      : v !== null && typeof v === "object"
        ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, canonical(v[k])]))
        : v;
  return createHash("sha256").update(JSON.stringify(canonical(value))).digest("hex").slice(0, 16);
};

for (const key of [
  "apple-macos-26.5-1x-light-standard",
  "apple-macos-26.5-1x-dark-standard",
]) {
  const path = resolve(PACKAGE, "profiles", `${key}.json`);
  const doc = JSON.parse(readFileSync(path, "utf8"));
  const now = fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch));
  console.log(`${key}  ${doc.resolvedMaterialSha256} -> ${now}`);
}
