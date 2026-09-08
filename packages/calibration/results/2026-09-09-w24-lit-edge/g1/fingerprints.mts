/**
 * W24 G1 — the resolved-material fingerprint of every committed profile document under this
 * worktree's renderer, beside the one each document records.
 *
 * `collapseTransmission` is a new field on the resolved material, so `tuned-profiles.test.ts`'s
 * completeness digest moves even though the constant is inert and no pixel does. G1 does not write
 * the profile documents; this prints what G2 must re-record and nothing else.
 *
 * Run: `npx tsx results/2026-09-09-w24-lit-edge/g1/fingerprints.mts` from `packages/calibration`.
 */
import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "@vitrea/renderer-webgpu";

const fingerprint = (resolved: unknown): string => {
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
};

for (const file of readdirSync("profiles").filter((n) => n.endsWith(".json")).sort()) {
  const doc = JSON.parse(readFileSync(`profiles/${file}`, "utf8")) as {
    readonly patch?: object;
    readonly resolvedMaterialSha256?: string;
  };
  if (doc.patch === undefined) continue;
  const now = fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch));
  console.log(
    `${file.padEnd(50)} recorded ${(doc.resolvedMaterialSha256 ?? "-").padEnd(18)} now ${now}`,
  );
}
