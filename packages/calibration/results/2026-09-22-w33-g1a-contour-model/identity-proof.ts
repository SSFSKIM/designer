/** W33 G1a, before any shader code: extend rule 2 in memory, never the material (§5.171). */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, materialDigestInput,
  MATERIAL_IDENTITY_TABLE, materialLeafAt, type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const here = import.meta.dirname;
const declaration = JSON.parse(readFileSync(resolve(here, "candidate.json"), "utf8"));
const profiles = resolve(here, "../../profiles");
const read = (name: string) => JSON.parse(readFileSync(resolve(profiles, `${name}.json`), "utf8"));
const canonical = (v: unknown): unknown => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object" ? Object.fromEntries(Object.entries(v)
    .sort(([a], [b]) => a.localeCompare(b)).map(([k, child]) => [k, canonical(child)])) : v;
const hash = (v: unknown) => createHash("sha256").update(JSON.stringify(canonical(v)))
  .digest("hex").slice(0, 16);

/** Exactly materialDigestInput's path drop, with a proposed append supplied in memory. */
function proposedInput(value: unknown, nested: boolean): unknown {
  const prefix = nested ? "contourStroke." : "";
  const gate = nested ? "alpha" : "contourStrokeAlpha";
  const width = nested ? "widthDevicePx" : "contourStrokeWidthDevicePx";
  const entries = [...MATERIAL_IDENTITY_TABLE,
    { gate: { [prefix + gate]: 0 }, gated: nested ? [prefix + width] : Object.keys(declaration.gated) }];
  const paths = entries.flatMap((e) => Object.entries(e.gate)
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
  const widths = [0, .5, 1, 2, 3, 1000].map((width) => {
    const flat = { ...material, ...declaration.gated, contourStrokeAlpha: 0, contourStrokeWidthDevicePx: width };
    const nested = { ...material, contourStroke: { alpha: 0, widthDevicePx: width } };
    const flatDigest = hash(proposedInput(flat, false));
    const nestedDigest = hash(proposedInput(nested, true));
    if (flatDigest !== before || nestedDigest === before) throw new Error("identity route failed");
    if (hash(proposedInput({ ...flat, contourStrokeAlpha: .1 }, false)) === before) {
      throw new Error("a non-identity gate was dropped");
    }
    return { width, flat: flatDigest, nested: nestedDigest };
  });
  const sweeps = Object.keys(declaration.gated).flatMap(leaf => [-1000, 0, .5, 1, 1000].map(value => {
    const materialWithLeaves = { ...material, ...declaration.gated, contourStrokeAlpha: 0, [leaf]: value };
    const digest = hash(proposedInput(materialWithLeaves, false));
    if (digest !== before) throw new Error(`${name}/${leaf}: gated leaf moved identity`);
    return { leaf, value, digest };
  }));
  return { name, recorded, before, widths, sweeps };
});
console.log(JSON.stringify(rows, null, 2));
writeFileSync(resolve(here, "identity-proof.json"), `${JSON.stringify(rows, null, 2)}\n`);
