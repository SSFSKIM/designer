/** W47 G0 (f), Decision Log 3 v1.1: scratch-only forms, built from the X62 snapshots.
 * Candidate declaration/digest handling follows W46's build-candidate.ts. No live profile is read.
 * Optional scratch leaves stay absent on the control, so its resolved digests match the snapshots.
 * Run from packages/calibration: pnpm exec tsx results/2026-10-06-w47-g0-operators/diagnostic/build-candidates.ts
 */
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "@vitrea/renderer-webgpu";
import { CANDIDATE_DECLARATION_KIND, resolvedDigest, cssTierMappingSha256,
  readCandidateDocument } from "../../../scripts/candidate-document";
const HERE = resolve(fileURLToPath(new URL(".", import.meta.url)));
const sha = (x: string | Buffer) => createHash("sha256").update(x).digest("hex");
const snapshots = {
  "active.light": "ebc3d9105a4a40565278845071113c6a5368b304910362786b8cbfb4cc66bb44",
  "active.dark": "d0219cd684bff75b2ba5c34d4f6cb2f6d49e32aab7cc27464220a05910f2638f",
  "receded.light": "12712d534b78017f68fee440cb9d9d451178aae1b80db36c0043fdfb1b591203",
  "receded.dark": "f0b36a71772a00a647c10a280ae73b92d21be1f0c65599334c4e3cdf36cb7f86",
};
for (const label of ["control", "body", "deep", "weights", "zero-share"]) {
  const out = join(HERE, "candidates", label);
  if (existsSync(out)) throw new Error(`${out} exists; evidence is not overwritten`);
  const active: Record<string, typeof DEFAULT_MATERIAL_PROFILE> = {};
  const endpoints: Record<string, {path: string; sha256: string}> = {};
  let mapping: any;
  mkdirSync(out, {recursive: true});
  for (const [slot, hash] of Object.entries(snapshots)) {
    const file = join(HERE, "../documents", `${hash.slice(0,12)}.json`);
    const text = readFileSync(file, "utf8");
    if (sha(text) !== hash) throw new Error(`snapshot ${slot} changed`);
    const source = JSON.parse(text);
    const [pose, scheme] = slot.split(".");
    const patch = structuredClone(source.patch);
    if (slot === "receded.dark" && label !== "control") {
      Object.assign(patch, {
        sizeFineTapShare: ["weights", "zero-share"].includes(label) ? 0 : 1,
        sizeFineTapSigma: 6, sizeFineTapSigma2x: 6,
        sizeFineTapFormScratch: label === "body" ? 0 : label === "weights" ? 2 : 1,
      });
    }
    const material = withMaterialOverrides(pose === "active" ? DEFAULT_MATERIAL_PROFILE : active[scheme!], patch);
    const digest = resolvedDigest(material);
    if ((slot !== "receded.dark" || label === "control") && digest !== source.resolvedMaterialSha256) {
      throw new Error(`${slot}: unmoved digest changed`);
    }
    if (pose === "active") active[scheme!] = material;
    if (slot === "active.light") mapping = source.cssTierMapping;
    const doc = {
      $comment: `W47 G0 (f) ${label}; scratch only; exact X62 patch except the declared receded dark leaves.`,
      profileKey: source.profileKey.replace("glass0.25", "glass0.250"),
      schemaVersion: source.schemaVersion, colorSpace: source.colorSpace,
      ...(pose === "receded" ? {kind: "receded-endpoint",
        resolvedOverActiveDocument: `active.${scheme}.json`} : {}),
      derivedFrom: {sha256: hash, path: `../documents/${hash.slice(0,12)}.json`},
      resolvedMaterialSha256: digest, resolvedMaterialSha256Rule: 2, patch,
      ...(pose === "active" ? {cssTierMapping: source.cssTierMapping} : {}),
    };
    const body = JSON.stringify(doc, null, 2) + "\n";
    writeFileSync(join(out, `${slot}.json`), body);
    endpoints[slot] = {path: `${slot}.json`, sha256: sha(body)};
  }
  const declaration = {kind: CANDIDATE_DECLARATION_KIND, schemaVersion: 1,
    name: `apple-macos-27.0-glass0.25-w47-diagnostic-${label}`, platform: "macOS 27.0",
    glassTintAmount: 0.25, endpoints, cssTierMappingSha256: cssTierMappingSha256(mapping)};
  const path = join(out, "candidate.json");
  writeFileSync(path, JSON.stringify(declaration, null, 2) + "\n");
  console.log(label, readCandidateDocument(path).declarationSha256,
    Object.fromEntries(Object.entries(readCandidateDocument(path).endpoints)
      .map(([slot, d]) => [slot, d.resolvedMaterialSha256])));
}
