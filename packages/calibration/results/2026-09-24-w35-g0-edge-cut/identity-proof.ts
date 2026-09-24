/** W35 G0a, before any shader code: extend rule 2 in memory, never the material (§5.177). */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, materialDigestInput,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const here = import.meta.dirname;
if (existsSync(resolve(here, "identity-proof.json"))) {
  throw new Error("Refuse to overwrite the recorded identity proof; replay in a fresh evidence copy");
}
const profiles = resolve(here, "../../profiles");
const read = (name: string) => JSON.parse(readFileSync(resolve(profiles, `${name}.json`), "utf8"));
const canonical = (v: unknown): unknown => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object" ? Object.fromEntries(Object.entries(v)
    .sort(([a], [b]) => a.localeCompare(b)).map(([k, child]) => [k, canonical(child)])) : v;
const hash = (v: unknown) => createHash("sha256").update(JSON.stringify(canonical(v)))
  .digest("hex").slice(0, 16);

/** A proposed flat value drop; the runtime identity table is not edited. */
function proposedInput(value: Record<string, unknown>): unknown {
  const input = materialDigestInput(value) as Record<string, unknown>;
  if (input["bodyBoundaryRamp"] !== 0) return input;
  return Object.fromEntries(Object.entries(input).filter(([key]) => key !== "bodyBoundaryRamp"));
}
const names = ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard",
  "apple-macos-27.0-1x-light-standard-glass0.5", "apple-macos-27.0-1x-dark-standard-glass0.5",
  "apple-macos-27.0-1x-light-standard-glass0.5-receded",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded"];
function resolveDocument(name: string): typeof DEFAULT_MATERIAL_PROFILE {
  const doc = read(name);
  const base = doc.appliesOver?.endsWith(".json") ? resolveDocument(doc.appliesOver.split("/").at(-1).replace(/\.json$/, ""))
    : DEFAULT_MATERIAL_PROFILE;
  return withMaterialOverrides(base, doc.patch as MaterialProfilePatch);
}
const rows = names.map((name) => {
  const material = resolveDocument(name);
  const recorded = read(name).resolvedMaterialSha256;
  const before = hash(materialDigestInput(material));
  if (before !== recorded) throw new Error(`${name}: live ${before} != recorded ${recorded}`);
  const flat = { ...material, bodyBoundaryRamp: 0 };
  const after = hash(proposedInput(flat));
  const nonzero = hash(proposedInput({ ...flat, bodyBoundaryRamp: .01 }));
  if (after !== before || nonzero === before) throw new Error("identity route failed");
  return { name, recorded, before, after, nonzero,
    proposedEntry: { wave: "W35", gate: { bodyBoundaryRamp: 0 }, gated: [],
      law: "C_preShadow += bodyBoundaryRamp * compactBoundaryRamp(d, nativeIdentifiedLevelLaw)",
      inertLawCase: "TO BE IMPLEMENTED: packages/renderer-webgpu/test/w35-boundary-ramp.test.ts — zero ramp preserves the pre-shadow composite bit-identically",
      literalAssertion: "expect(DEFAULT_MATERIAL_PROFILE.bodyBoundaryRamp).toBe(0)",
      claims: "c9a §5.177, X13", runtimeTested: false } };
});
console.log(JSON.stringify(rows, null, 2));
writeFileSync(resolve(here, "identity-proof.json"), `${JSON.stringify(rows, null, 2)}\n`);
