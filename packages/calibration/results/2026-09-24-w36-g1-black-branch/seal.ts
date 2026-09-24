/** Seal only a priced configuration, under rule 2, before its once-only read (§5.179). */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  DEFAULT_MATERIAL_PROFILE, MATERIAL_DIGEST_RULE_VERSION, materialDigestInput,
  withMaterialOverrides, type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
const here = import.meta.dirname;
const profiles = resolve(here, "../../profiles");
const read = (path: string) => JSON.parse(readFileSync(path, "utf8"));
if (existsSync(resolve(here, "sealed-manifest.json"))) throw new Error("Already sealed");
if (read(resolve(here, "price-final.json")).frozenStopsBroken.length) throw new Error("Price failed");
const formula = read(resolve(here, "formula-outcome.json"));
if (formula.shipped !== false || formula.sourcesRestored !== true) {
  throw new Error("This seal supports the black-only outcome; a formula adoption needs its own seal");
}
const canonical = (v: unknown): unknown => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object" ? Object.fromEntries(Object.entries(v)
    .sort(([a], [b]) => a.localeCompare(b)).map(([k, child]) => [k, canonical(child)])) : v;
const hash = (v: string | Buffer) => createHash("sha256").update(v).digest("hex");
const fingerprint = (v: unknown) => hash(JSON.stringify(canonical(materialDigestInput(v))));
if (MATERIAL_DIGEST_RULE_VERSION !== 2) throw new Error("This seal uses rule 2");
for (const scheme of ["light", "dark"]) {
  const name = `apple-macos-26.5-1x-${scheme}-standard.json`;
  const doc = read(resolve(profiles, name));
  if (fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch)).slice(0, 16)
    !== doc.resolvedMaterialSha256) throw new Error(`Frozen digest moved: ${name}`);
}
const fits = read(resolve(here, "candidate-ordinates.json"));
const pricePlans = read(resolve(here, "candidate-plans.json"));
const writes: { name: string; bytes: string }[] = [];
const documents: Record<string, Record<string, unknown>> = {};
for (const scheme of ["light", "dark"]) {
  let active = DEFAULT_MATERIAL_PROFILE;
  for (const pose of ["rest", "inactive"]) {
    const name = `apple-macos-27.0-1x-${scheme}-standard-glass0.5` +
      (pose === "inactive" ? "-receded" : "") + ".json";
    const path = resolve(profiles, name);
    const beforeBytes = readFileSync(path);
    const doc = JSON.parse(beforeBytes.toString());
    const beforeDigest = doc.resolvedMaterialSha256;
    const beforeMaterial = withMaterialOverrides(pose === "rest" ? DEFAULT_MATERIAL_PROFILE
      : withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
        read(resolve(profiles, name.replace("-receded", ""))).patch), doc.patch);
    const beforeFull = fingerprint(beforeMaterial);
    if (beforeFull.slice(0, 16) !== beforeDigest) throw new Error(`Stale pin: ${name}`);
    const fit = fits.find((f: { scheme: string; pose: string }) => f.scheme === scheme && f.pose === pose);
    doc.patch = { ...doc.patch, ...fit.patch } as MaterialProfilePatch;
    for (const plan of pricePlans.filter((p: { profile: string }) => p.profile.includes(`-${scheme}-`))) {
      const priced = pose === "rest" ? plan.active.patch : plan.receded.patch;
      for (const [key, value] of Object.entries(fit.patch)) {
        if (priced[key] !== value) throw new Error(`Unpriced black ordinate: ${name}/${key}`);
      }
    }
    const material = withMaterialOverrides(pose === "rest" ? DEFAULT_MATERIAL_PROFILE : active, doc.patch);
    if (pose === "rest") active = material;
    const full = fingerprint(material), digest = full.slice(0, 16);
    doc.$comment.push("", "W36 G1, claims §5.179; Decision Log 5: the black branch alone.",
      "Strength 1 carries the native span44 black ordinate, with thick explicitly equal to thin",
      "as an unmeasured extrapolation. Support ends at encoded input 0.003, below the minimum",
      "admitted packed impulse input 0.0031948897521942854. The middle and all old knots stay.",
      "Both receded documents state their own black values over their active endpoint.",
      "The separate receded colour-formula trial was declined at its frozen regression stops.");
    (doc["$comment-sha-history"] ??= []).push(`${beforeDigest} — rule 2, superseded by ${digest}, ` +
      "W36 G1 (§5.179): black-only compact branch; all old leaves unchanged.");
    doc.resolvedMaterialSha256 = digest;
    doc.resolvedMaterialSha256Rule = 2;
    const bytes = JSON.stringify(doc, null, 2) + "\n";
    documents[name] = { beforeDigest, beforeFullDigest: beforeFull,
      resolvedMaterialSha256: digest, fullDigest: full,
      beforeFileSha256: hash(beforeBytes), fileSha256: hash(bytes), black: fit.patch };
    writes.push({ name, bytes });
  }
}
for (const { name, bytes } of writes) writeFileSync(resolve(profiles, name), bytes);
writeFileSync(resolve(here, "sealed-manifest.json"), JSON.stringify({
  claims: "c9a §5.179", rule: 2, formulaIncluded: false, documents,
}, null, 2) + "\n", { flag: "wx" });
console.log(JSON.stringify(documents, null, 2));
