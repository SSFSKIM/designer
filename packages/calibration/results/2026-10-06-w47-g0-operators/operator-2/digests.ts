/**
 * W47 G0 (b): every shipped document's `resolvedMaterialSha256`, recomputed on the operator's code
 * (charter clause 1, X66, X57 carried; claims §5.211).
 *
 * Resolves each profile document as its own fields say — over the runtime default, or a receded
 * difference over its active document (`resolvedOverActiveDocument`) — and takes the digest under
 * the rule the runtime applies today (`MATERIAL_DIGEST_RULE_VERSION`, the sorted-key SHA-256 of
 * `materialDigestInput`), restated here as `tuned-profiles.test.ts` restates it. An optional
 * `W47_FINE_DIGEST_OUT` writes a new witness exclusively; exits 1 if a live digest differs from what it
 * records, or if the fine share is not at its identity or its entire gate-group is not dropped.
 *
 *     npx tsx results/2026-10-06-w47-g0-operators/operator-2/digests.ts   (from packages/calibration)
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
const keys = ["sizeFineTapShare", "sizeFineTapSigma", "sizeFineTapSigma2x"] as const;
const lines = [`rule ${String(MATERIAL_DIGEST_RULE_VERSION)}; fine-body gate at the default: ` +
  `${String(DEFAULT_MATERIAL_PROFILE.sizeFineTapShare)}`];
let failures = 0;
for (const file of files) {
  const document = load(file);
  const base = document.resolvedOverActiveDocument === undefined
    ? DEFAULT_MATERIAL_PROFILE
    : withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, load(document.resolvedOverActiveDocument).patch);
  const resolved = withMaterialOverrides(base, document.patch);
  const live = fingerprint(materialDigestInput(resolved));
  const dropped = keys.every(key => materialDigestDroppedLeaves(resolved).includes(key));
  const ok = live === document.resolvedMaterialSha256 && resolved.sizeFineTapShare === 0 && dropped;
  if (!ok) failures += 1;
  lines.push(`${ok ? "unchanged" : "MOVED    "}  ${file.padEnd(62)} recorded ${document.resolvedMaterialSha256}` +
    `  live ${live}  leaf ${String(resolved.sizeFineTapShare)}${dropped ? " (dropped)" : " (CARRIED)"}`);
}
lines.push(`${String(files.length - failures)} of ${String(files.length)} documents reproduce their recorded digest`);
// Evidence is append-only: a second run writes to stdout, never over the committed witness.
const out = process.env["W47_FINE_DIGEST_OUT"];
if (out !== undefined) writeFileSync(resolve(out), `${lines.join("\n")}\n`, { flag: "wx" });
process.stdout.write(`${lines.join("\n")}\n`);
process.exit(failures === 0 ? 0 : 1);
