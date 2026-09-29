/**
 * W41 G2 seal (c9a §5.193; charter Decision Log 2 as ruled 2026-09-29): the light-receded
 * macOS 27 document enables E3 at EXACTLY the tuple the one exposure scored, and nothing else.
 *
 * The E3 fields are read from the scratch candidate document that manifest-1 froze and the
 * receipt recaptured, never retyped, and the new patch must equal that candidate's patch
 * key-for-key, so the resolved material (and therefore every WebGPU pixel) is the one the
 * exposure closed on. The other three macOS 27 documents and the frozen 26.5 pair must keep
 * their file bytes and digests. Run once with tsx from packages/calibration.
 */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { isDeepStrictEqual } from "node:util";
import {
  DEFAULT_MATERIAL_PROFILE, MATERIAL_DIGEST_RULE_VERSION, materialDigestInput,
  withMaterialOverrides, type MaterialProfile, type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const here = import.meta.dirname;
const calibration = resolve(here, "../..");
const profiles = resolve(calibration, "profiles");
const g1 = resolve(here, "../2026-09-27-w41-g1-identification");
const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5.json";
const RECEDED = LIGHT.replace(".json", "-receded.json");
const read = (path: string) => JSON.parse(readFileSync(path, "utf8"));
const sha = (bytes: string | Buffer) => createHash("sha256").update(bytes).digest("hex");
const canonical = (v: unknown): unknown => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object" ? Object.fromEntries(Object.keys(v).sort()
    .map((k) => [k, canonical((v as Record<string, unknown>)[k])])) : v;
const fingerprint = (m: MaterialProfile) => sha(JSON.stringify(canonical(materialDigestInput(m))));

if (existsSync(resolve(here, "sealed-manifest.json"))) throw new Error("Already sealed");
if (MATERIAL_DIGEST_RULE_VERSION !== 2) throw new Error("This seal uses digest rule 2");

// The exposure's frozen configuration, and the candidate document it pins.
const MANIFEST = resolve(g1, "exposure/final-configuration/manifest-1.json");
const MANIFEST_SHA = "77f93ba2166e83a8e31bb5f26a1c5ffb9e6d2be35fa5ec5509a0a19e72ba95a7";
if (sha(readFileSync(MANIFEST)) !== MANIFEST_SHA) throw new Error("manifest-1 moved");
const candidatePath = resolve(g1, "body-leaf/candidate", RECEDED);
const candidateBytes = readFileSync(candidatePath);
const CANDIDATE_SHA = "d34ebe3a73f281e542734737db6bbb92dbe4b432368307de067200eb31d571bd";
if (sha(candidateBytes) !== CANDIDATE_SHA) throw new Error("scratch candidate moved");
const manifestFiles = read(MANIFEST).files as Record<string, string>;
const candidateRel = "packages/calibration/results/2026-09-27-w41-g1-identification/" +
  `body-leaf/candidate/${RECEDED}`;
if (manifestFiles[candidateRel] !== CANDIDATE_SHA) throw new Error("manifest does not pin it");
const candidate = JSON.parse(candidateBytes.toString());

// Every source document still at the bytes and digest G1 pinned before its scratch.
const pins = read(resolve(g1, "body-leaf/source-document-pins.json")) as
  Record<string, { sha256: string; resolvedMaterialSha256: string }>;
const material = (name: string): MaterialProfile => {
  const doc = read(resolve(profiles, name));
  return withMaterialOverrides(doc.resolvedOverActiveDocument === undefined
    ? DEFAULT_MATERIAL_PROFILE : material(doc.resolvedOverActiveDocument), doc.patch);
};
for (const [name, pin] of Object.entries(pins)) {
  const bytes = readFileSync(resolve(profiles, name));
  if (sha(bytes) !== pin.sha256) throw new Error(`source bytes moved: ${name}`);
  if (fingerprint(material(name)).slice(0, 16) !== pin.resolvedMaterialSha256) {
    throw new Error(`source digest moved: ${name}`);
  }
}

const path = resolve(profiles, RECEDED);
const beforeBytes = readFileSync(path);
const doc = JSON.parse(beforeBytes.toString());
const beforeDigest: string = doc.resolvedMaterialSha256;
const beforeFull = fingerprint(material(RECEDED));
const e3 = {
  bodyE3Strength: candidate.patch.bodyE3Strength,
  bodyE3Gains: candidate.patch.bodyE3Gains,
  bodyE3Neutral: candidate.patch.bodyE3Neutral,
};
if (e3.bodyE3Strength !== 1) throw new Error("candidate is not enabled");
doc.patch = { ...doc.patch, ...e3 } as MaterialProfilePatch;
// Key-for-key the scratch patch the exposure scored: the seal adds no other leaf.
if (!isDeepStrictEqual(doc.patch, candidate.patch)) throw new Error("patch differs from candidate");
const sealed = withMaterialOverrides(material(LIGHT), doc.patch);
const full = fingerprint(sealed);
const digest = full.slice(0, 16);
if (digest !== candidate.resolvedMaterialSha256) throw new Error("resolved material differs");

doc.$comment.push("",
  "W41 G2, claims §5.193; charter Decision Log 2 (ruled 2026-09-29): E3 enabled here only.",
  "bodyE3Strength 1 with the seven neutral ordinates and three chroma gains that the one W39",
  "holdout exposure scored (manifest-1 77f93ba2…, receipt fc157275): light-inactive E3 met",
  "the one-code bound on 18/18 numerical and 16/16 rendered claimed held-out cells. On the",
  "regular variant, under nominal policy and over an actually sampled texture, E3 REPLACES",
  "the tone solve, chroma retention and black branch below with y = F(L)·1 + g(L)·v on",
  "encoded luma; those leaves stay recorded because every other pose and policy still draws",
  "them. Its claim is uniform backdrops; structured backdrops are a diagnostic domain",
  "(§5.192 §6, §20). The other three macOS 27 documents keep E3 at its identity.");
doc.entries.bodyE3 = {
  status: "identified on the W39 archive and closed on its holdout (light receded only)",
  value: e3,
  previous: { bodyE3Strength: 0 },
  method: [
    "W41 B1 (E3): luma tone F at seven measured neutral ordinates (encoded inputs 40, 56, 72,",
    "88, 104, 128, 150; end segments continued, unit-cube clip) and a radial chroma gain g at",
    "encoded luma 63, 93 and 118, held outside. The gains are the certified-LP minimax upper",
    "witness on the W39 calibration cells (§5.192 §2), frozen before validation and the one",
    "exposure; no coefficient was refitted after it. The neutral ordinates are the measured",
    "light-inactive deep medians, not fitted.",
    "",
    "Survival: numerical uniform calibration/validation 138 cells, worst 0.832 code; rendered",
    "130 uniform cells, worst 1.000 code, with the W38 per-bin veto passing every admitted",
    "bin (§5.192 §15). Closure: 18/18 numerical (worst 0.666) and 16/16 rendered (worst",
    "1.0, at the bound) claimed held-out cells (§5.192 §25). Not claimed: structured",
    "backdrops, the active pose, the dark scheme, and the CSS tier (Decision Log 4).",
  ],
};
(doc["$comment-sha-history"] ??= []).push(`${beforeDigest} — rule 2, superseded by ${digest}, ` +
  "W41 G2 (§5.193): the E3 gate-group enabled at the exposure's frozen tuple; " +
  "every other leaf unchanged.");
doc.resolvedMaterialSha256 = digest;
doc.resolvedMaterialSha256Rule = 2;
const bytes = JSON.stringify(doc, null, 2) + "\n";

// The seal must leave every other document byte-identical.
const others = Object.fromEntries(Object.entries(pins).filter(([name]) => name !== RECEDED)
  .map(([name, pin]) => [name, pin]));
writeFileSync(path, bytes);
for (const [name, pin] of Object.entries(others)) {
  if (sha(readFileSync(resolve(profiles, name))) !== pin.sha256) throw new Error(`moved: ${name}`);
  if (fingerprint(material(name)).slice(0, 16) !== pin.resolvedMaterialSha256) {
    throw new Error(`digest moved: ${name}`);
  }
}
if (fingerprint(material(RECEDED)) !== full) throw new Error("written document does not resolve");
const manifest = {
  claims: "c9a §5.193", rule: 2,
  ruling: "W41 Decision Log 2, ruled by the user 2026-09-29",
  exposure: { manifest: "results/2026-09-27-w41-g1-identification/exposure/final-configuration/" +
    "manifest-1.json", manifestSha256: MANIFEST_SHA, receiptCommit: "fc157275" },
  candidate: { path: `results/2026-09-27-w41-g1-identification/body-leaf/candidate/${RECEDED}`,
    sha256: CANDIDATE_SHA, resolvedMaterialSha256: candidate.resolvedMaterialSha256 },
  documents: { [RECEDED]: {
    beforeDigest, beforeFullDigest: beforeFull, resolvedMaterialSha256: digest, fullDigest: full,
    beforeFileSha256: sha(beforeBytes), fileSha256: sha(bytes), e3,
    patchEqualsCandidate: true,
  } },
  unchanged: others,
};
writeFileSync(resolve(here, "sealed-manifest.json"), JSON.stringify(manifest, null, 2) + "\n",
  { flag: "wx" });
console.log(JSON.stringify(manifest, null, 2));
