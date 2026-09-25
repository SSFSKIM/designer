/** W37 G0: proposed rule-2 append in memory, before any runtime leaf (§5.181, X13). */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, materialDigestInput,
  MATERIAL_IDENTITY_TABLE, materialLeafAt,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const here = import.meta.dirname;
const stdoutOnly = process.argv.includes("--stdout");
for (const name of stdoutOnly ? [] : ["identity-proof.json"]) {
  if (existsSync(resolve(here, name))) throw new Error(`Refuse to overwrite recorded ${name}`);
}
const read = (name: string) => JSON.parse(readFileSync(resolve(here, "../../profiles", `${name}.json`), "utf8"));
const canonical = (v: unknown): unknown => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object" ? Object.fromEntries(Object.entries(v)
    .sort(([a], [b]) => a.localeCompare(b)).map(([k, child]) => [k, canonical(child)])) : v;
const hash = (v: unknown) => createHash("sha256").update(JSON.stringify(canonical(v)))
  .digest("hex").slice(0, 16);
const gated = ["bodyEdgeLineWidth", "bodyEdgeShoulderWidth", "bodyEdgeShoulderShare",
  "bodyEdgeExponent", "bodyEdgeLumaIntercept", "bodyEdgeLumaSlope", "bodyEdgeChromaGain",
  "bodyEdgeChromaSlope", "bodyEdgeIsotropicKeep"];
const declaration = {
  wave: "W37", gate: { bodyEdgeStrength: 0 }, gated,
  law: "At gate 0 execute the complete old boundary treatment. At gate 1 replace, not stack; " +
    "only gpu-texture is identified. Neither tested family closes; no runtime nomination.",
  inertLawCase: "G1: renderer-webgpu/test/w37-body-edge.test.ts — zero gate preserves old " +
    "boundary at every gated leaf; GPU/CSS drawn identity and unsampled-backend invariance",
  literalIdentity: "expect(DEFAULT_MATERIAL_PROFILE.bodyEdgeStrength).toBe(0); append to " +
    "calibration/test/w31-identity-table.test.ts; explicit zero in both receded differences",
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
const archived = resolve(here, "identity-inputs.json");
const inputs: { materials: Record<string, typeof DEFAULT_MATERIAL_PROFILE>;
  recorded: Record<string, string> } = existsSync(archived)
  ? JSON.parse(readFileSync(archived, "utf8"))
  : { materials: Object.fromEntries(names.map(name => [name, resolveDocument(name)])),
      recorded: Object.fromEntries(names.map(name => [name, read(name).resolvedMaterialSha256])) };
const materials = inputs.materials;
if (process.argv.includes("--archive-inputs")) {
  if (existsSync(archived)) throw new Error("Refuse to rewrite identity inputs");
  writeFileSync(archived, `${JSON.stringify(inputs, null, 2)}\n`);
}
const rows = names.map(name => {
  const material = materials[name]!;
  const before = hash(materialDigestInput(material));
  const recorded = inputs.recorded[name];
  if (before !== recorded) throw new Error(`${name}: live ${before} != recorded ${recorded}`);
  const checks = [-10, 0, .001, .1, .5, 1, 10].map(value => {
    const extended = { ...material, bodyEdgeStrength: 0,
      ...Object.fromEntries(gated.map((leaf, i) => [leaf, value * (i + 1)])) };
    const identity = hash(proposedInput(extended));
    const nonzero = hash(proposedInput({ ...extended, bodyEdgeStrength: 1 }));
    if (identity !== before) throw new Error("identity digest moved");
    if (nonzero === before) throw new Error("open gate was dropped");
    return { gatedSweepValue: value, identity, nonzero };
  });
  return { name, recorded, before, checks };
});
const result = { declaration, rows, renderedNewLeafIdentity: false,
  qualification: "Digest route proved in memory; no optical branch or leaf exists. G1 must prove rendered identity." };
if (!stdoutOnly) writeFileSync(resolve(here, "identity-proof.json"), `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
