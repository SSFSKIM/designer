/**
 * W47 G0 (a): every shipped document's `resolvedMaterialSha256`, recomputed on operator 1's code
 * (charter clause 1, Decision Log 2, X57; claims §5.211). W45's `digests.ts`
 * (`results/2026-10-03-w45-g0-operator/operator/`), ported to the two new leaves.
 *
 * Resolves each profile document as its own fields say — over the runtime default, or a receded
 * difference over its active document (`resolvedOverActiveDocument`) — and takes the digest under
 * the rule the runtime applies today (`MATERIAL_DIGEST_RULE_VERSION`, the sorted-key SHA-256 of
 * `materialDigestInput`), restated here as `tuned-profiles.test.ts` restates it. Writes
 * `digests.txt` beside itself and exits 1 if any document's live digest differs from the one it
 * records, or if either new leaf is not at its identity (and dropped) in every resolved material.
 *
 *     npx tsx results/2026-10-06-w47-g0-operators/operator-1/digests.ts   (from packages/calibration)
 */
import { createHash } from "node:crypto";
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  materialDigestDroppedLeaves,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "..", "profiles");
const LEAVES = ["tintAlphaFar1x", "tintAlphaFar2x"] as const;

const fingerprint = (resolved: unknown): string => {
  const canonical = (value: unknown): unknown =>
    Array.isArray(value)
      ? value.map(canonical)
      : value !== null && typeof value === "object"
        ? Object.fromEntries(Object.keys(value as object).sort()
          .map((key) => [key, canonical((value as Record<string, unknown>)[key])]))
        : value;
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);
};

interface ProfileDocument {
  readonly patch: MaterialProfilePatch;
  readonly resolvedMaterialSha256: string;
  readonly resolvedMaterialSha256Rule?: number;
  readonly resolvedOverActiveDocument?: string;
}
const load = (file: string): ProfileDocument =>
  JSON.parse(readFileSync(resolve(PROFILES, file), "utf8")) as ProfileDocument;

const files = readdirSync(PROFILES)
  .filter((file) => file.startsWith("apple-macos-") && file.endsWith(".json") && !file.includes(".seed."))
  .sort();
const lines = [`rule ${String(MATERIAL_DIGEST_RULE_VERSION)}; leaves at the default: ` +
  LEAVES.map((leaf) => `${leaf} ${String(DEFAULT_MATERIAL_PROFILE[leaf])}`).join(", ")];
let failures = 0;
for (const file of files) {
  const document = load(file);
  const base = document.resolvedOverActiveDocument === undefined
    ? DEFAULT_MATERIAL_PROFILE
    : withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, load(document.resolvedOverActiveDocument).patch);
  const resolved = withMaterialOverrides(base, document.patch);
  const live = fingerprint(materialDigestInput(resolved));
  const droppedLeaves = materialDigestDroppedLeaves(resolved);
  const leavesOk = LEAVES.every((leaf) => resolved[leaf] === 0 && droppedLeaves.includes(leaf));
  const ok = live === document.resolvedMaterialSha256 && leavesOk;
  if (!ok) failures += 1;
  lines.push(`${ok ? "unchanged" : "MOVED    "}  ${file.padEnd(62)} recorded ${document.resolvedMaterialSha256}` +
    `  live ${live}  leaves ${LEAVES.map((leaf) => String(resolved[leaf])).join("/")}` +
    `${leavesOk ? " (dropped)" : " (CARRIED)"}`);
}
lines.push(`${String(files.length - failures)} of ${String(files.length)} documents reproduce their recorded digest`);
writeFileSync(resolve(HERE, "digests.txt"), `${lines.join("\n")}\n`);
process.stdout.write(`${lines.join("\n")}\n`);
process.exit(failures === 0 ? 0 : 1);
