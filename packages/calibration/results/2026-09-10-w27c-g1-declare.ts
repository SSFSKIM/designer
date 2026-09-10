/** Create-only declaration of the endpoint before its holdout is read. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../renderer-webgpu/src/material";
import { recededMaterialProfile } from "../../platform-web/src/receded-profile";

// The same canonicalization as tuned-profiles.test.ts; record both full SHA-256
// and its established 16-hex display prefix rather than changing that pin's shape.
const canonical = (v: any): any => Array.isArray(v) ? v.map(canonical) :
  v !== null && typeof v === "object" ? Object.fromEntries(
    Object.keys(v).sort().map((k) => [k, canonical(v[k])]),
  ) : v;
const sha = (v: unknown): string => createHash("sha256")
  .update(JSON.stringify(canonical(v))).digest("hex");
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
  declaredIn: "W27c G1; claims §5.130; W27 X1/X3/X7/X8",
  frozenAt: new Date().toISOString(),
  patch: recededMaterialProfile,
  profiles,
  fit: { calibrationCells: 62, validationCells: 16, independentCaptureRepeats: 2,
    selection: "t3 light standard/reduced transparency, t5 dark standard/increased contrast; final module repeated on all 78 cells after main integration, all 62 fitted PNGs byte-identical",
    knownExcludedPair: "apple-macos-26.5-2x-dark-standard/photo__capsule-button__rest",
    recordedInteractionCopies: "12 rows preserved in the bed and not fitted or checked" },
  holdout: { statusAtDeclaration: "unread", declaredCells: 30,
    rule: "Read once on this fixed document, record as spent, never fit to the reading" },
  identityProof: { activePinsUnchanged: true, rendererGoldensUnchanged: true,
    method: "tuned-profiles.test.ts plus the full 34-test renderer golden/isolation suite on a private server; no from-empty canonical matrix rebuild in G1" },
}, null, 2) + "\n", { flag: "wx" });
console.log(JSON.stringify(profiles, null, 2));
