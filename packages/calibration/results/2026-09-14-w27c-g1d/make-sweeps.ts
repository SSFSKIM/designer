import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { recededMaterialProfile } from "../../../platform-web/src/receded-profile";

const here = dirname(fileURLToPath(import.meta.url));
const plan = JSON.parse(readFileSync(resolve(here, "sweep-plan.json"), "utf8"));
const out = resolve(here, "sweeps");
mkdirSync(out, { recursive: true });
const base = JSON.parse(JSON.stringify(recededMaterialProfile)) as any;
const clone = (): any => JSON.parse(JSON.stringify(base));
const write = (name: string, doc: unknown): void =>
  writeFileSync(resolve(out, `${name}.json`), `${JSON.stringify(doc, null, 2)}\n`);

write("baseline", clone());
for (const rung of plan.t1.rungs.slice(1)) {
  const doc = clone();
  doc.dark.backdropToneAnchorX = [0.1104, 0.2706, rung.x, 0.9505];
  doc.dark.backdropToneResponseThin = [
    base.dark.backdropToneResponseThin[0],
    base.dark.backdropToneResponseThin[1],
    rung.thin,
    plan.t1.fixedFar.thin,
  ];
  doc.dark.backdropToneResponseThick = [
    base.dark.backdropToneResponseThick[0],
    base.dark.backdropToneResponseThick[1],
    rung.thick,
    plan.t1.fixedFar.thick,
  ];
  write(`t1-${rung.id}`, doc);
}
for (const lift of plan.t2.reduceTransparencyRungs) {
  const doc = clone();
  doc.light.increasedOcclusionLiftByPolicy = {
    reduceTransparency: lift,
    increaseContrast: plan.t2.sharedDefault,
  };
  write(`t2-rt-${lift}`, doc);
}
for (const lift of plan.t2.increaseContrastRungs) {
  const doc = clone();
  doc.light.increasedOcclusionLiftByPolicy = {
    reduceTransparency: 0.92,
    increaseContrast: lift,
  };
  write(`t2-ic-${lift}`, doc);
}
console.log(`wrote ${1 + plan.t1.rungs.length - 1
  + plan.t2.reduceTransparencyRungs.length + plan.t2.increaseContrastRungs.length} rungs`);
