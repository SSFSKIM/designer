/** CPU-only validation through the driver's real candidate reader; no page or renderer launch. */
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import { mergeMaterialProfiles } from "@vitreajs/vitrea-web";
import type { MaterialProfilePatch } from "@vitrea/renderer-webgpu";
import { readCandidateDocument } from "../../../scripts/candidate-document";
import { opaqueGlassViolations } from "../../../scripts/no-opaque-glass";

const root = process.argv[2];
if (!root || process.argv.length !== 3) throw new Error("Usage: verify-candidates.ts <candidate-root>");
const built = JSON.parse(readFileSync(resolve(root, "build.json"), "utf8"));
const points = built.points.map((point: { label: string }) => {
  const path = resolve(root, point.label, "candidate.json");
  const candidate = readCandidateDocument(path);
  for (const scheme of ["light", "dark"] as const) {
    const active = JSON.parse(readFileSync(candidate.endpoints[`active.${scheme}`].path, "utf8"));
    const receded = JSON.parse(readFileSync(candidate.endpoints[`receded.${scheme}`].path, "utf8"));
    for (const patch of [active.patch, mergeMaterialProfiles(active.patch, receded.patch)]) {
      if (opaqueGlassViolations(patch as MaterialProfilePatch).length) {
        throw new Error(`${point.label}/${scheme}: X75 fails`);
      }
    }
  }
  return { label: point.label, candidateSha256: candidate.declarationSha256,
    resolvedDigests: "checked by readCandidateDocument", x75: "PASS" };
});
process.stdout.write(JSON.stringify({ points, scope: "CPU candidate digest and X75 only",
  environment: { node: process.version,
    playwright: createRequire(import.meta.url)("@playwright/test/package.json").version } }) + "\n");
