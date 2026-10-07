/** W49b G0's ten shipped byte witnesses; no document is resealed here. */
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch } from "@vitrea/renderer-webgpu";
import { resolvedDigest } from "../../../scripts/candidate-document";

const cal = resolve(import.meta.dirname, "../../..");
const profiles = resolve(cal, "profiles");
const files = readdirSync(profiles).filter(p => /^apple-macos-.*-1x-(light|dark)-standard(?:-glass0\.(25|5)(?:-receded)?)?\.json$/.test(p));
const doc = (name: string) => JSON.parse(readFileSync(resolve(profiles, name), "utf8")) as {
  patch: MaterialProfilePatch; resolvedMaterialSha256: string;
};
if (files.length !== 10) throw new Error(`Expected ten shipped documents, got ${files.length}`);
const records = files.map(name => {
  const document = doc(name);
  const base = name.includes("-receded") ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
    doc(name.replace("-receded", "")).patch) : DEFAULT_MATERIAL_PROFILE;
  const actual = resolvedDigest(withMaterialOverrides(base, document.patch));
  if (actual !== document.resolvedMaterialSha256) throw new Error(`Changed digest: ${name}`);
  return { name, recorded: document.resolvedMaterialSha256, actual,
    documentSha256: createHash("sha256").update(readFileSync(resolve(profiles, name))).digest("hex") };
});
const out = process.argv[2];
if (!out) throw new Error("Provide an evidence output path");
writeFileSync(out, JSON.stringify(records, null, 2) + "\n");
console.log(`${records.length} shipped digests unchanged`);
