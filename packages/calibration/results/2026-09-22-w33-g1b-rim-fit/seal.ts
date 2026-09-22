/**
 * W33 G1b — rule-2 seal of the lift's stand-down and anchor compensation (§5.172).
 *
 * The sorted-key fingerprint is W32 G1's corrected seal. Only the two active
 * documents are written. The receded differences already override every moving
 * amplitude to zero; their fully composed fingerprints must stay identical,
 * not merely the hashes of their files. Both frozen digests are checked before
 * any write. Prior readings are appended to history, never replaced there.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "profiles");
const chosen = process.argv[2];
if (chosen === undefined) throw new Error("seal.ts <round label>");
const constants = JSON.parse(readFileSync(resolve(HERE, "rounds", chosen, "constants.json"), "utf8")) as
  Record<string, Record<string, number>>;
const canonical = (value: unknown): unknown => Array.isArray(value) ? value.map(canonical)
  : value !== null && typeof value === "object" ? Object.fromEntries(
    Object.keys(value).sort().map((key) => [key, canonical((value as Record<string, unknown>)[key])]),
  ) : value;
const hash = (bytes: string | Buffer): string => createHash("sha256").update(bytes).digest("hex");
const fingerprint = (material: unknown): string =>
  hash(JSON.stringify(canonical(materialDigestInput(material))));
type Document = Record<string, unknown> & { patch: MaterialProfilePatch };
const read = (name: string): Document =>
  JSON.parse(readFileSync(resolve(PROFILES, name), "utf8")) as Document;
if (MATERIAL_DIGEST_RULE_VERSION !== 2) throw new Error("This seal names rule 2 only");

for (const scheme of ["light", "dark"]) {
  const name = `apple-macos-26.5-1x-${scheme}-standard.json`;
  const doc = read(name);
  const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch);
  const digest = fingerprint(resolved);
  if (digest.slice(0, 16) !== doc["resolvedMaterialSha256"]) throw new Error(`X1: ${name}`);
  console.log(`frozen unchanged ${name}: ${digest}`);
}
const allowed = new Set([
  "liftAmplitude", "thickOcclusionAt96", "thickOcclusionAt128", "thickOcclusionAt160",
]);
const plans: { name: string; bytes: string; record: Record<string, unknown> }[] = [];
const manifest: Record<string, unknown> = {};
for (const scheme of ["light", "dark"]) {
  const name = `apple-macos-27.0-1x-${scheme}-standard-glass0.5.json`;
  const doc = read(name);
  const oldBytes = readFileSync(resolve(PROFILES, name));
  const shadow = doc.patch.outerShadow as unknown as Record<string, number>;
  const next = constants[scheme];
  if (next === undefined || next["liftAmplitude"] !== 0) throw new Error("Lift must stand down");
  if (JSON.stringify(Object.keys(shadow).sort()) !== JSON.stringify(Object.keys(next).sort())) {
    throw new Error("A candidate changed the shadow's leaf set");
  }
  for (const key of Object.keys(shadow)) {
    if (shadow[key] !== next[key] && !allowed.has(key)) throw new Error(`X3: ${scheme}/${key}`);
  }
  const oldDigest = doc["resolvedMaterialSha256"];
  doc.patch = { ...doc.patch, outerShadow: next } as MaterialProfilePatch;
  const active = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch);
  const full = fingerprint(active);
  const after = full.slice(0, 16);
  const comments = doc["$comment"] as string[];
  comments.push("", "W33 G1b, claims §5.172; Decision Log 1 (a), ruled: liftAmplitude is DECLARED 0,",
    "not fitted. Apple's macOS 27 backdrop-black exterior is zero on 67 light / 50 dark",
    "cells and 1,546,726 / 1,099,348 backdrop-black pixels (§5.170). The frozen macOS 26.5",
    "material is nonzero on 39 of 125 cells and keeps its 0.01 / 0.0051 lifts and digests.",
    `The three thick anchors take the rendered window-departure compensation (round ${chosen}).`,
    "liftSpanMin and the lift's shape leaves stay, UNREAD at zero amplitude. The receded",
    "difference already holds zero and is unchanged. No contour leaf or rim term moved",
    "(W33 Decision Log 3, ruled); this is not a contour-stroke fit.");
  const history = doc["$comment-sha-history"] as string[];
  history.push(`${String(oldDigest)} — rule 2, SHA-256 of materialDigestInput(resolved). ` +
    `Re-sealed at ${after} under the same rule, W33 G1b (claims §5.172; Decision Log 1 (a)): ` +
    "the lift stands down and only the three thick anchors take its compensation.");
  doc["resolvedMaterialSha256"] = after;
  doc["resolvedMaterialSha256Rule"] = 2;
  const bytes = `${JSON.stringify(doc, null, 2)}\n`;
  const record = { beforeDigest: oldDigest, resolvedMaterialSha256: after, fullDigest: full,
    beforeFileSha256: hash(oldBytes), fileSha256: hash(bytes) };
  plans.push({ name, bytes, record });
  manifest[name] = record;
  const recededName = name.replace(".json", "-receded.json");
  const receded = read(recededName);
  const recededFull = fingerprint(withMaterialOverrides(active, receded.patch));
  if (recededFull.slice(0, 16) !== receded["resolvedMaterialSha256"]) {
    throw new Error(`Receded composition moved: ${recededName}`);
  }
  const file = hash(readFileSync(resolve(PROFILES, recededName)));
  manifest[recededName] = { beforeDigest: receded["resolvedMaterialSha256"],
    resolvedMaterialSha256: receded["resolvedMaterialSha256"], fullDigest: recededFull,
    beforeFileSha256: file, fileSha256: file, unchanged: true };
}
for (const { name, bytes, record } of plans) {
  writeFileSync(resolve(PROFILES, name), bytes);
  console.log(name, record);
}
writeFileSync(resolve(HERE, "sealed-manifest.json"),
  `${JSON.stringify({ claims: "c9a §5.172", rule: 2, round: chosen, documents: manifest }, null, 2)}\n`);
console.log("SEAL OK: two active documents written; both receded and both frozen unchanged");
