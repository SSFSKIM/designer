/** Freeze the corrected endpoint only after its declared calibration/validation checks. */
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../renderer-webgpu/src/material";
import { recededMaterialProfile } from "../../platform-web/src/receded-profile";

const canonical = (v: any): any => Array.isArray(v) ? v.map(canonical) :
  v !== null && typeof v === "object" ? Object.fromEntries(
    Object.keys(v).sort().map((k) => [k, canonical(v[k])]),
  ) : v;
const sha = (v: unknown): string => createHash("sha256")
  .update(JSON.stringify(canonical(v))).digest("hex");
const bytesSha = (v: Buffer): string => createHash("sha256").update(v).digest("hex");
const checkedBytes = readFileSync(process.argv[3]!);
const checked = JSON.parse(checkedBytes.toString());
if (sha(checked.patch) !== sha(recededMaterialProfile)) throw new Error("Checked patch is not the export");
if (checked.rows.filter((r: any) => r.set === "calibration").length !== 62 ||
    checked.rows.filter((r: any) => r.set === "validation").length !== 16 ||
    checked.rows.length !== 78) throw new Error("Wrong frozen check population");
if (checked.rows.some((r: any) => r.problems.length !== 0 || r.repeats !== 2 ||
    r.geometry.viewport.width !== 320 || r.geometry.viewport.height !== 200 ||
    r.geometry.requestedScale !== r.scale || r.geometry.devicePixelRatio !== r.scale)) {
  throw new Error("Frozen checks lack clean framing or independent repeats");
}
const profiles = Object.fromEntries((["light", "dark"] as const).map((scheme) => {
  const active = JSON.parse(readFileSync(resolve(import.meta.dirname,
    `../profiles/apple-macos-26.5-1x-${scheme}-standard.json`), "utf8"));
  const activeResolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active.patch);
  const inactiveResolved = withMaterialOverrides(activeResolved, recededMaterialProfile[scheme]);
  const activeSha256 = sha(activeResolved);
  if (activeSha256.slice(0, 16) !== active.resolvedMaterialSha256) throw new Error("Active fingerprint moved");
  return [scheme, { activeSha256, activeRecordedFingerprint: active.resolvedMaterialSha256,
    inactiveSha256: sha(inactiveResolved) }];
}));
writeFileSync(process.argv[2]!, JSON.stringify({
  declaredIn: "W27c G1 corrected experiment; claims §5.130; W27 X1/X3/X7/X8",
  supersedesInvalidDeclaration: "2026-09-10-w27c-g1-declaration.json (preserved unchanged)",
  frozenAt: new Date().toISOString(),
  repositoryHead: execFileSync("git", ["rev-parse", "HEAD"], {
    cwd: resolve(import.meta.dirname, "../../.."), encoding: "utf8",
  }).trim(),
  instrumentSha256: bytesSha(readFileSync(resolve(import.meta.dirname,
    "2026-09-10-w27c-g1-run.ts"))),
  integrityHelperSha256: bytesSha(readFileSync(resolve(import.meta.dirname,
    "../src/capture-integrity.ts"))),
  patch: recededMaterialProfile,
  profiles,
  fit: { calibrationCells: 62, validationCells: 16, independentCaptureRepeats: 2,
    checkedRun: process.argv[3], checkedRunSha256: bytesSha(checkedBytes),
    selection: process.argv[4],
    knownExcludedPair: "apple-macos-26.5-2x-dark-standard/photo__capsule-button__rest",
    recordedInteractionCopies: "12 rows preserved in the bed and not fitted or checked" },
  holdout: { statusAtDeclaration: "unread", declaredCells: 30,
    rule: "Read once on this fixed document, record as spent, never fit to the reading" },
  identityProof: { activePinsUnchanged: true, rendererGoldensUnchanged: true,
    method: "tuned-profiles.test.ts plus the full 34-test renderer golden/isolation suite on a private server; no from-empty canonical matrix rebuild in G1" },
}, null, 2) + "\n", { flag: "wx" });
console.log(JSON.stringify(profiles, null, 2));
