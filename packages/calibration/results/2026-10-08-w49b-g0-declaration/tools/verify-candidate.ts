/** CPU-only prelaunch validation of the candidate the driver will draw, including X75. */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { mergeMaterialProfiles } from "@vitreajs/vitrea-web";
import type { MaterialProfilePatch } from "@vitrea/renderer-webgpu";
import { readCandidateDocument } from "../../../scripts/candidate-document";
import { opaqueGlassViolations, summariseOpaqueGlass } from "../../../scripts/no-opaque-glass";

const path = process.argv[2];
if (!path || process.argv.length !== 3) throw new Error("Usage: verify-candidate.ts <candidate.json>");
const candidate = readCandidateDocument(resolve(path));
for (const scheme of ["light", "dark"] as const) {
  const active = JSON.parse(readFileSync(candidate.endpoints[`active.${scheme}`].path, "utf8")).patch;
  const receded = JSON.parse(readFileSync(candidate.endpoints[`receded.${scheme}`].path, "utf8")).patch;
  for (const [pose, patch] of [["active", active], ["receded", mergeMaterialProfiles(active, receded)]] as const) {
    const violations = opaqueGlassViolations(patch as MaterialProfilePatch);
    if (violations.length) throw new Error(`${pose}.${scheme} violates X75: ` +
      summariseOpaqueGlass(violations).join("; "));
  }
}
process.stdout.write(JSON.stringify({ candidateSha256: candidate.declarationSha256, x75: "PASS", endpoints: 4 }) + "\n");
