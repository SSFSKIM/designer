/** Adopt only the response rows selected by the completed, control-gated GPU tables. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const sourceFile = resolve(here, "../../../platform-web/src/receded-profile.ts");
const json = (file: string): any => JSON.parse(readFileSync(file, "utf8"));
const sha = (text: string): string => createHash("sha256").update(text).digest("hex");
const selected = Object.fromEntries(["light", "dark"].map((scheme) => {
  const fit = json(resolve(here, `fit-${scheme}.json`));
  if (fit.selected === null || fit.rungs[fit.selected].refused) {
    throw new Error(`${scheme}: no control-admitted selected endpoint`);
  }
  const patch = json(resolve(here, "sweeps", `${fit.selected}.json`));
  if (sha(JSON.stringify(patch)) !== fit.rungs[fit.selected].patchSha256) {
    throw new Error(`${scheme}: selected patch bytes changed`);
  }
  return [scheme, { name: fit.selected, patch: patch[scheme], row: fit.rungs[fit.selected] }];
})) as Record<string, any>;
let text = readFileSync(sourceFile, "utf8");
const beforeSha256 = sha(text);
const lightAt = text.indexOf("  light: {");
const darkAt = text.indexOf("  dark: {");
if (lightAt < 0 || darkAt <= lightAt) throw new Error("Unexpected receded document layout");
const prefix = text.slice(0, lightAt);
const parts = { light: text.slice(lightAt, darkAt), dark: text.slice(darkAt) };
for (const scheme of ["light", "dark"] as const) {
  let block = parts[scheme];
  for (const key of ["backdropToneAnchorX", "backdropToneResponseThin", "backdropToneResponseThick"]) {
    const values = selected[scheme].patch[key] as number[];
    if (!Array.isArray(values) || ![3, 4].includes(values.length) || !values.every(Number.isFinite)) {
      throw new Error(`${scheme}/${key}: invalid selected row`);
    }
    const line = `    ${key}: [${values.join(", ")}],`;
    const pattern = new RegExp(`^    ${key}: \\[[^\\n]*\\],$`, "m");
    if (pattern.test(block)) block = block.replace(pattern, line);
    else if (key === "backdropToneAnchorX") {
      block = block.replace("    backdropToneResponseThin:", `${line}\n    backdropToneResponseThin:`);
    } else throw new Error(`Missing ${scheme}/${key}`);
  }
  block = block.replace("    backdropToneAnchorX:",
    "    // W28's non-D fit under the silhouette abscissa; the sealed rows are in claims §5.145.\n" +
    "    backdropToneAnchorX:");
  parts[scheme] = block;
}
text = prefix + parts.light + parts.dark;
writeFileSync(sourceFile, text);
writeFileSync(resolve(here, "adopted-response.json"), `${JSON.stringify({
  sourceFile, beforeSha256, afterSha256: sha(text),
  selected: Object.fromEntries(Object.entries(selected).map(([scheme, value]) => [scheme, {
    name: value.name, inactiveSha256: value.row.inactiveSha256,
    anchors: value.patch.backdropToneAnchorX, thin: value.patch.backdropToneResponseThin,
    thick: value.patch.backdropToneResponseThick,
  }])),
}, null, 2)}\n`);
console.log("Adopted selected response rows; declaration and resolved-identity checks remain mandatory.");
