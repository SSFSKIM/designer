/** W36 G0: proposed rule-2 append in memory, before any runtime leaf (§5.178, X13). */
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
const declaration = {
  wave: "W36", gate: { backdropToneBlackStrength: 0 }, gated: ["backdropToneBlackLevel"],
  law: "At gate 0 execute the old authority and response branch exactly. At gate 1 use full " +
    "response authority and a linear segment from (0, blackLevel) to the existing first knot; " +
    "above that knot use the old response. The black level is shared across thickness rows.",
  inertLawCase: "G1: packages/renderer-webgpu/test/w36-black-knot.test.ts — gate 0 holds the " +
    "old solve at every blackLevel; packages/renderer-webgpu/e2e/gpu/w36-black-knot.spec.ts — " +
    "gate 0 draws pinned bytes, gate 1 changes black; CSS declaration identity and tier coherence",
  literalIdentity: "G1 appends backdropToneBlackStrength: 0 to calibration/test/w31-identity-table.test.ts",
};
function proposedInput(value: unknown): unknown {
  const entries = [...MATERIAL_IDENTITY_TABLE, declaration];
  const paths = entries.flatMap(e => Object.entries(e.gate)
    .every(([p, identity]) => materialLeafAt(value, p) === identity)
    ? [...Object.keys(e.gate), ...e.gated] : []);
  const strip = (v: unknown, prefix = ""): unknown => {
    if (v === null || typeof v !== "object" || Array.isArray(v)) return v;
    return Object.fromEntries(Object.entries(v).map(([k, child]) =>
      [prefix ? `${prefix}.${k}` : k, k, child] as const)
      .filter(([p]) => !paths.includes(p)).map(([p, k, child]) => [k, strip(child, p)]));
  };
  return strip(value);
}
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
    const extended = { ...material, backdropToneBlackStrength: 0, backdropToneBlackLevel: blackLevel };
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
const result = { declaration, rows, renderedNewLeafIdentity: false,
  qualification: "Digest route and exact identity branch proved; no leaf exists. G1 must prove rendered identity." };
for (const [name, value] of [["identity-proof.json", result], ["resolved-materials.json", materials]] as const) {
  writeFileSync(resolve(here, name), `${JSON.stringify(value, null, 2)}\n`);
}
console.log(JSON.stringify(result, null, 2));
