/**
 * W27c G1c: freeze the fitted endpoint (claims §5.141).
 *
 * Run AFTER the selected rungs are written into
 * `packages/platform-web/src/receded-profile.ts` and BEFORE the re-read, in the
 * same shape as `2026-09-10-w27c-g1-corrected-declare.ts` froze the endpoint
 * this one supersedes: the exported document, its resolved SHA-256 per scheme,
 * and the two ACTIVE fingerprints that must not have moved.
 *
 * The active checks are refusals here, not records. This child fits a difference
 * over the active material and may not touch the material itself, so a
 * declaration written while either active document had drifted would freeze an
 * endpoint over a base nobody measured.
 *
 * Usage:
 *   pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx \
 *     results/2026-09-13-w27c-g1c-fit/declare.ts
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { recededMaterialProfile } from "../../../platform-web/src/receded-profile";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides,
} from "../../../renderer-webgpu/src/material";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");
const json = (file: string): any => JSON.parse(readFileSync(file, "utf8"));
const sha = (data: string | Buffer): string =>
  createHash("sha256").update(data).digest("hex");
const canonical = (v: any): any =>
  Array.isArray(v)
    ? v.map(canonical)
    : v !== null && typeof v === "object"
      ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, canonical(v[k])]))
      : v;
const shaValue = (v: unknown): string => sha(JSON.stringify(canonical(v)));

const frozen = json(resolve(pkg, "results/2026-09-10-w27c-g1-corrected-declaration.json"));
const profiles: Record<string, unknown> = {};
for (const scheme of ["light", "dark"] as const) {
  const doc = json(resolve(pkg, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`));
  const declared = frozen.profiles[scheme];
  const activeResolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch);
  const activeSha256 = shaValue(activeResolved);
  if (activeSha256 !== declared.activeSha256) {
    throw new Error(
      `The ${scheme} ACTIVE material resolves to ${activeSha256} where the frozen G1 declaration ` +
        `froze ${declared.activeSha256}. This child may not move the active material.`,
    );
  }
  if (doc.resolvedMaterialSha256 !== declared.activeRecordedFingerprint) {
    throw new Error(
      `The ${scheme} active profile document records ${doc.resolvedMaterialSha256} where the ` +
        `frozen G1 declaration froze ${declared.activeRecordedFingerprint}`,
    );
  }
  profiles[scheme] = {
    activeSha256,
    activeRecordedFingerprint: doc.resolvedMaterialSha256,
    inactiveSha256: shaValue(withMaterialOverrides(activeResolved, recededMaterialProfile[scheme])),
    frozenG1InactiveSha256: declared.inactiveSha256,
  };
}

const head = execFileSync("git", ["-C", repo, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
writeFileSync(
  resolve(here, "fitted-endpoint.json"),
  `${JSON.stringify({
    declaredIn: "W27c G1c model-form fit; claims §5.141; W27 Decision Log 17; X1/X3/X7/X8",
    supersedes: "2026-09-10-w27c-g1-corrected-declaration.json (preserved unchanged)",
    frozenAt: new Date().toISOString(),
    repositoryHead: head,
    partition: "packages/calibration/results/2026-09-13-w27c-g1c-fit/partition.json",
    sweepPlan: "packages/calibration/results/2026-09-13-w27c-g1c-fit/sweep-plan.json",
    instrumentSha256: sha(readFileSync(resolve(here, "g1c-run.ts"))),
    patch: recededMaterialProfile,
    patchSha256: sha(JSON.stringify(recededMaterialProfile)),
    frozenG1PatchSha256: sha(JSON.stringify(frozen.patch)),
    profiles,
    holdout: {
      statusAtDeclaration: "unread",
      cells: [
        "apple-macos-26.5-1x-dark-standard/light-solid__capsule-button__inactive",
        "apple-macos-26.5-2x-dark-standard/light-solid__capsule-button__inactive",
        "apple-macos-26.5-1x-light-increased-contrast/dark-solid__rrect-80__inactive",
        "apple-macos-26.5-1x-light-reduced-transparency/dark-solid__rrect-80__inactive",
      ],
      rule: "read once on this fixed document, in the frozen re-read, and no constant moves after it",
    },
    adoptsNoFloor:
      "W27 Decision Log 13's probe bar stands: the checking bed is seven runs and no inactive " +
      "regression floor comes out of it, whatever this endpoint measures.",
  }, null, 2)}\n`,
);
console.log(`declared at ${head}`);
console.log(JSON.stringify(profiles, null, 2));
