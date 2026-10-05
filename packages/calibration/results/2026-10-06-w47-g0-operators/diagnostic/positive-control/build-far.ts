/** Requested positive control: deep form at sigma40 CSS px, otherwise the diagnostic's snapshot pair. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "@vitrea/renderer-webgpu";
import { readCandidateDocument, resolvedDigest } from "../../../../scripts/candidate-document";
const HERE=resolve(fileURLToPath(new URL(".",import.meta.url)));
const source=join(HERE,"../candidates/deep");
const out=join(HERE,"candidates/deep40");
if(existsSync(out)) throw new Error(`${out} exists`);
const valid=readCandidateDocument(join(source,"candidate.json"));
const declaration=JSON.parse(readFileSync(join(source,"candidate.json"),"utf8"));
const active=JSON.parse(readFileSync(join(source,"active.dark.json"),"utf8"));
const base=withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,active.patch);
mkdirSync(out,{recursive:true});
for(const slot of Object.keys(valid.endpoints)) {
 const doc=JSON.parse(readFileSync(join(source,`${slot}.json`),"utf8"));
 if(slot==="receded.dark") {
  doc.patch.sizeFineTapSigma=40;doc.patch.sizeFineTapSigma2x=40;
  doc.resolvedMaterialSha256=resolvedDigest(withMaterialOverrides(base,doc.patch));
  doc.$comment="W47 G0(f) positive control: deep form, share1, extra width40 CSS px, not a fitted candidate.";
 }
 const text=JSON.stringify(doc,null,2)+"\n";
 writeFileSync(join(out,`${slot}.json`),text);
 declaration.endpoints[slot].sha256=createHash("sha256").update(text).digest("hex");
}
declaration.name="apple-macos-27.0-glass0.25-w47-positive-control-deep40";
writeFileSync(join(out,"candidate.json"),JSON.stringify(declaration,null,2)+"\n");
console.log(readCandidateDocument(join(out,"candidate.json")).declarationSha256);
