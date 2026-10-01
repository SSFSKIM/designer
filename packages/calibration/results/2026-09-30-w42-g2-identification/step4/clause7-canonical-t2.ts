/**
 * Clause 7's candidate-2 reference on the canonical uniform cells: the runtime's own
 * `bodyToneTableCodesAt` at each solid's colour and each declared span, under the c2 documents
 * as the root resolves them (active, then receded over it). Printed as JSON for clause7_canonical.py.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { DEFAULT_MATERIAL_PROFILE, bodyToneTableCodesAt, withMaterialOverrides } from "@vitrea/renderer-webgpu";
const STEP4 = import.meta.dirname;
const REPO = resolve(STEP4, "../../../../..");
const sets = JSON.parse(readFileSync(resolve(STEP4, "documents/documents.json"), "utf8")).sets.c2;
const patch = (p: string) => JSON.parse(readFileSync(resolve(REPO, p), "utf8")).patch;
const light = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch(sets.light.path));
const out: Record<string, unknown> = {};
const endpoints = {
  "light-rest": light,
  "light-inactive": withMaterialOverrides(light, patch(sets.lightReceded.path)),
  "dark-inactive": withMaterialOverrides(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch(sets.dark.path)),
    patch(sets.darkReceded.path)),
};
const solids = { "light-solid": [242, 242, 247], "dark-solid": [28, 28, 30] } as const;
for (const [ep, m] of Object.entries(endpoints)) {
  for (const [bg, rgb] of Object.entries(solids)) {
    for (const span of [32, 44, 64, 80, 96, 128, 160]) {
      out[`${ep}|${bg}|${span}`] = bodyToneTableCodesAt(rgb as unknown as [number, number, number], span, m);
    }
  }
}
process.stdout.write(`${JSON.stringify(out)}\n`);
