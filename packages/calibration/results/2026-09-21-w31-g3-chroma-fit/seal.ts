/**
 * W31 G3 — seal the four macOS 27 profile documents UNDER THE DIGEST RULE, and
 * record their file hashes before the canonical read.
 *
 *   npx tsx results/2026-09-21-w31-g3-chroma-fit/seal.ts [--reason "<why>"]
 *
 * W29 G3's `results/2026-09-19-w29-g3-refit/seal.ts` one rule along, copied
 * rather than reused on that file's own convention: nothing under `results/` is
 * edited after commit, and a sealing script that hard-codes the rule it sealed
 * under is the only kind whose output a later reader can reproduce.
 *
 * **What changed is the FUNCTION, not the fingerprint.** The digest is still
 * SHA-256 over the fully resolved material with keys sorted, first 16 hex. It is
 * now taken over `materialDigestInput(resolved)` — the material with every
 * `MATERIAL_IDENTITY_TABLE` entry dropped whose gates hold their declared
 * identities (W31 Decision Log 1 (a), ruled; claims §5.161 §7b). That is **rule
 * 2**; rule 1 is the plain resolved digest every document sealed before this one
 * carries, and `profiles/digest-supersessions.json` is rule 1's history.
 *
 * So each document re-sealed here records `resolvedMaterialSha256Rule: 2` beside
 * its digest — a recorded digest names the function that produced it — and
 * appends a line to its own `$comment-sha-history`. The two frozen macOS 26.5
 * documents are NOT edited and NOT re-sealed: under rule 2 their own recorded
 * fields are the live fingerprint again, which this script asserts before it
 * writes a byte (X1), and a document with no field naming a rule is rule 1 by
 * default — which for those two is the same number under either.
 *
 * It refuses to write if the assertions fail, so the X1 proof runs before the
 * seal rather than after it.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  materialDigestDroppedLeaves,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const PROFILES = resolve(import.meta.dirname, "..", "..", "profiles");

/**
 * `tuned-profiles.test.ts`'s fingerprint, verbatim: keys sorted, SHA-256, first
 * 16 hex. Deliberately duplicated — an algorithm restated is an algorithm two
 * places can check. What is NOT duplicated is the rule, which is a table walk
 * whose drift would be silent and which lives in the renderer.
 */
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

const ruleDigest = (resolved: unknown): string => fingerprint(materialDigestInput(resolved));

const read = (name: string): Record<string, unknown> =>
  JSON.parse(readFileSync(resolve(PROFILES, `${name}.json`), "utf8")) as Record<string, unknown>;

const reasonFlag = process.argv.indexOf("--reason");
const REASON =
  reasonFlag >= 0 ? (process.argv[reasonFlag + 1] ?? "") : "W31 G3 — the digest rule lands (claims §5.164)";

let failures = 0;
const fail = (message: string): void => {
  failures += 1;
  console.log(`  FAIL ${message}`);
};

/**
 * X1, and the half of it this rule exists for: the two frozen documents resolve
 * to the digests they RECORDED — their own fields, not a record beside them.
 */
console.log(`== X1: the frozen macOS 26.5 documents, under rule ${String(MATERIAL_DIGEST_RULE_VERSION)} ==`);
for (const name of ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard"]) {
  const document = read(name);
  const resolved = withMaterialOverrides(
    DEFAULT_MATERIAL_PROFILE,
    document["patch"] as MaterialProfilePatch,
  );
  const plain = fingerprint(resolved);
  const under = ruleDigest(resolved);
  const dropped = materialDigestDroppedLeaves(resolved);
  console.log(`  ${name}`);
  console.log(`    recorded in the document  ${String(document["resolvedMaterialSha256"])}`);
  console.log(`    rule 1 (plain)            ${plain}`);
  console.log(`    rule 2 (under the table)  ${under}   dropped ${String(dropped.length)}: ${dropped.join(", ")}`);
  if (under !== document["resolvedMaterialSha256"]) {
    fail(`${name}: under the rule ${under}, recorded ${String(document["resolvedMaterialSha256"])} — X1`);
  }
}

const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5";
const DARK = "apple-macos-27.0-1x-dark-standard-glass0.5";

const activeBase = (name: string): unknown =>
  withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read(name)["patch"] as MaterialProfilePatch);

/**
 * The four macOS 27 documents, each resolved through the construction it names.
 * A receded document is a DIFFERENCE over the active document of its own scheme
 * — the composition a root performs when the window loses focus — and a digest
 * over the recede alone is a digest of a material nothing draws (claims §5.158
 * §8, finding 1).
 */
const TARGETS: readonly (readonly [string, () => unknown])[] = [
  [LIGHT, () => activeBase(LIGHT)],
  [DARK, () => activeBase(DARK)],
  [
    `${LIGHT}-receded`,
    () =>
      withMaterialOverrides(
        activeBase(LIGHT) as never,
        read(`${LIGHT}-receded`)["patch"] as MaterialProfilePatch,
      ),
  ],
  [
    `${DARK}-receded`,
    () =>
      withMaterialOverrides(
        activeBase(DARK) as never,
        read(`${DARK}-receded`)["patch"] as MaterialProfilePatch,
      ),
  ],
];

if (failures > 0) {
  console.log(`\nSEAL REFUSED — ${String(failures)} failure(s); nothing written.`);
  process.exit(1);
}

console.log(`\n== the four macOS 27 documents, re-sealed under rule ${String(MATERIAL_DIGEST_RULE_VERSION)} ==`);
for (const [name, resolveIt] of TARGETS) {
  const path = resolve(PROFILES, `${name}.json`);
  const document = JSON.parse(readFileSync(path, "utf8")) as Record<string, unknown>;
  const before = String(document["resolvedMaterialSha256"]);
  const beforeRule = document["resolvedMaterialSha256Rule"] ?? 1;
  const resolved = resolveIt();
  const after = ruleDigest(resolved);
  const dropped = materialDigestDroppedLeaves(resolved);
  const history = Array.isArray(document["$comment-sha-history"])
    ? [...(document["$comment-sha-history"] as string[])]
    : [];
  if (after !== before || beforeRule !== MATERIAL_DIGEST_RULE_VERSION) {
    history.push(
      `${before} — the reading under rule ${String(beforeRule)} (the plain resolved ` +
        `fingerprint). Re-sealed at ${after} under rule ${String(MATERIAL_DIGEST_RULE_VERSION)}, ` +
        `the inert-identity rule of W31 Decision Log 1 (a): the same SHA-256 over the same ` +
        `resolved material with MATERIAL_IDENTITY_TABLE's entries dropped where their gates ` +
        `hold. ${REASON}`,
    );
  }
  const rebuilt: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(document)) {
    rebuilt[key] = value;
    if (key === "resolvedMaterialSha256") {
      rebuilt[key] = after;
      rebuilt["resolvedMaterialSha256Rule"] = MATERIAL_DIGEST_RULE_VERSION;
    }
  }
  rebuilt["$comment-sha-history"] = history;
  writeFileSync(path, `${JSON.stringify(rebuilt, null, 2)}\n`);
  const file = createHash("sha256").update(readFileSync(path)).digest("hex");
  console.log(`sealed ${name}`);
  console.log(`  was                    ${before} (rule ${String(beforeRule)})`);
  console.log(`  resolvedMaterialSha256 ${after} (rule ${String(MATERIAL_DIGEST_RULE_VERSION)})`);
  console.log(`  dropped (${String(dropped.length)})          ${dropped.join(", ")}`);
  console.log(`  document sha256        ${file}`);
}
console.log("\nSEAL OK");
