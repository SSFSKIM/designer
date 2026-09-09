import { readFileSync } from "node:fs";

const R =
  "/Users/new/Developer/GitHub/designer/packages/";
const { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } = await import(
  R + "renderer-webgpu/src/material.ts"
);

const out = {};
for (const name of [
  "apple-macos-26.5-1x-light-standard",
  "apple-macos-26.5-1x-dark-standard",
]) {
  const doc = JSON.parse(readFileSync(R + "calibration/profiles/" + name + ".json", "utf8"));
  const r = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch);
  const keys = Object.keys(r).filter((k) => typeof r[k] === "number");
  out[name] = Object.fromEntries(keys.map((k) => [k, r[k]]));
}
console.log(JSON.stringify(out, null, 1));
