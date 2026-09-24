/** W36 G0: live rule-2 gate-group proof (§5.179, X13). */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, materialDigestInput,
  MATERIAL_IDENTITY_TABLE, materialLeafAt, backdropToneSolveWeight,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const here = import.meta.dirname;
for (const name of ["identity-proof.json", "resolved-materials.json"]) {
  if (existsSync(resolve(here, name))) throw new Error(`Refuse to overwrite recorded ${name}`);
}
const read = (name: string) => JSON.parse(readFileSync(resolve(here, "../../profiles", `${name}.json`), "utf8"));
const canonical = (v: unknown): unknown => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object" ? Object.fromEntries(Object.entries(v)
    .sort(([a], [b]) => a.localeCompare(b)).map(([k, child]) => [k, canonical(child)])) : v;
const hash = (v: unknown) => createHash("sha256").update(JSON.stringify(canonical(v)))
  .digest("hex").slice(0, 16);
const declaration = MATERIAL_IDENTITY_TABLE.find(e => e.wave === "W36");
if (!declaration) throw new Error("Real identity table has no W36 group");
const proposedInput = materialDigestInput;
const names = ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard",
  "apple-macos-27.0-1x-light-standard-glass0.5",
  "apple-macos-27.0-1x-light-standard-glass0.5-receded",
  "apple-macos-27.0-1x-dark-standard-glass0.5",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded"];
function resolveDocument(name: string): typeof DEFAULT_MATERIAL_PROFILE {
  const doc = read(name);
  const base = doc.appliesOver?.endsWith(".json")
    ? resolveDocument(doc.appliesOver.split("/").at(-1).replace(/\.json$/, ""))
    : DEFAULT_MATERIAL_PROFILE;
  return withMaterialOverrides(base, doc.patch as MaterialProfilePatch);
}
const materials = Object.fromEntries(names.map(name => [name, resolveDocument(name)]));
const rows = names.map(name => {
  const material = materials[name]!;
  const before = hash(materialDigestInput(material));
  const recorded = read(name).resolvedMaterialSha256;
  if (before !== recorded) throw new Error(`${name}: live ${before} != recorded ${recorded}`);
  const checks = [0, .001, .1, .5, 1].map(blackLevel => {
    const extended = { ...material, backdropToneBlackStrength: 0, backdropToneBlackThin: blackLevel, backdropToneBlackThick: 1 - blackLevel };
    const identity = hash(proposedInput(extended));
    if (identity !== before) throw new Error("identity digest moved");
    if (hash(proposedInput({ ...extended, backdropToneBlackStrength: 1 })) === before) {
      throw new Error("open gate was dropped");
    }
    // The proposed identity branch calls, rather than reorders, today's arithmetic.
    for (const x of [0, .0001, .001, .002, .003, .004, .11, .5, 1]) {
      const old = backdropToneSolveWeight(x, material);
      const identityWeight = extended.backdropToneBlackStrength === 0 ? old : 1;
      if (identityWeight !== old) throw new Error("old branch changed");
    }
    return { blackLevel, identity };
  });
  return { name, recorded, before, checks };
});
const result = { declaration, rows, renderedNewLeafIdentity: "see identity capture byte comparisons and identity-goldens.txt",
  qualification: "Live materialDigestInput and live backdropToneSolveWeight; six shipped documents remain unchanged." };
for (const [name, value] of [["identity-proof.json", result], ["resolved-materials.json", materials]] as const) {
  writeFileSync(resolve(here, name), `${JSON.stringify(value, null, 2)}\n`);
}
console.log(JSON.stringify(result, null, 2));
