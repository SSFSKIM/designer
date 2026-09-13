/**
 * W27c G1c: the sweep's candidate documents, generated from `sweep-plan.json`.
 *
 * A rung is the exported frozen document with ONE field replaced, so a rung file
 * can never quietly carry a second change: this script starts from
 * `recededMaterialProfile` itself and writes the difference it names into the
 * one scheme entry the plan names.
 *
 * Usage:
 *   pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx \
 *     results/2026-09-13-w27c-g1c-fit/make-sweeps.ts
 */
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
const written: string[] = [];
const write = (name: string, doc: unknown): void => {
  writeFileSync(resolve(out, `${name}.json`), `${JSON.stringify(doc, null, 2)}\n`);
  written.push(name);
};

/* T1: one ordinate of the dark thin response, and nothing else in either entry. */
for (const x of plan.terms[0].rungs as number[]) {
  const doc = clone();
  doc.dark.backdropToneResponseThin = [
    base.dark.backdropToneResponseThin[0],
    base.dark.backdropToneResponseThin[1],
    x,
  ];
  write(`t1-far-${x}`, doc);
}

/*
 * T2: the accessibility fold of the LIGHT entry. `refractionScale` is a partial
 * record on both tiers' merge rules, so naming one rung leaves `true` and `none`
 * at the ladder's own values — which is what keeps every standard-profile cell
 * byte-identical, since a standard policy caps at `true`.
 */
const t2 = plan.terms[1];
for (const cap of t2.staged[0].rungs as number[]) {
  const doc = clone();
  if (cap !== 0.45) doc.light.refractionScale = { approximate: cap };
  write(`t2-s1-cap-${cap}`, doc);
}
for (const lift of t2.staged[1].rungs as number[]) {
  const doc = clone();
  /*
   * s2 runs at the cap s1 selects. The generator cannot know that yet, so it
   * writes the s2 rungs against EVERY s1 cap and the run uses the one the s1
   * table selected — the alternative is a second generator run after a
   * selection, which would let the selection edit the rungs.
   */
  for (const cap of t2.staged[0].rungs as number[]) {
    const rung = JSON.parse(JSON.stringify(doc));
    if (cap !== 0.45) rung.light.refractionScale = { approximate: cap };
    rung.light.increasedOcclusionLift = lift;
    write(`t2-s2-cap-${cap}-lift-${lift}`, rung);
  }
}

console.log(`${written.length} rungs: ${written.join(", ")}`);
