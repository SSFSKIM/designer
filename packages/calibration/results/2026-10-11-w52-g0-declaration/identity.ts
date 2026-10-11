/** W52-DL3: recompute all ten shipped digests without changing their source bytes. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch,
} from "../../../renderer-webgpu/src/material.ts";
import { resolvedDigest } from "../../scripts/candidate-document.ts";

type Prior = { name: string; recorded: string; actual: string; documentSha256: string };
type Document = { patch: MaterialProfilePatch; resolvedMaterialSha256: string };
const prior = JSON.parse(readFileSync(new URL(
  "../2026-10-08-w50-g0-declaration/evidence/digests.json", import.meta.url), "utf8")) as Prior[];
if (prior.length !== 10) throw new Error("The immutable identity witness must name ten documents");
const profileUrl = (name: string) => new URL(`../../profiles/${name}`, import.meta.url);
const read = (name: string): Document => JSON.parse(readFileSync(profileUrl(name), "utf8")) as Document;
const rows = prior.map((item) => {
  const raw = readFileSync(profileUrl(item.name));
  const documentSha256 = createHash("sha256").update(raw).digest("hex");
  if (documentSha256 !== item.documentSha256) throw new Error(`Shipped bytes moved: ${item.name}`);
  const document = read(item.name);
  const activeName = item.name.replace("-receded.json", ".json");
  const base = item.name.includes("-receded")
    ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read(activeName).patch)
    : DEFAULT_MATERIAL_PROFILE;
  const resolved = withMaterialOverrides(base, document.patch);
  if (resolved.lowEndStrength !== 0) throw new Error(`Shipped chart is not inert: ${item.name}`);
  const actual = resolvedDigest(resolved);
  if (actual !== item.actual || actual !== document.resolvedMaterialSha256) {
    throw new Error(`Identity digest moved: ${item.name}`);
  }
  return { name: item.name, documentSha256, recorded: item.recorded, actual, lowEndStrength: 0 };
});
const bytes = JSON.stringify({ schema: "w52-inert-digests-1", documents: rows }, null, 2) + "\n";
const out = fileURLToPath(new URL("evidence/digests.json", import.meta.url));
if (process.argv.includes("--check")) {
  if (readFileSync(out, "utf8") !== bytes) throw new Error("Recorded identity proof differs");
} else {
  writeFileSync(out, bytes);
}
console.log("W52 identity intact: ten document bytes and ten resolved digests; all chart gates zero");
