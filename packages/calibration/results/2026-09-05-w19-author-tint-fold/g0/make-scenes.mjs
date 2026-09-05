/**
 * W19 G0 (b) — the strength ladder's scratch scene bed, derived from the canonical one.
 *
 * The bed's tint registry carries three entries and two strengths (1.0, and `orange-half`'s 0.5),
 * which is why no wave saw the composite defect below full strength. This writes a SCRATCH bed that
 * adds the missing rungs — orange at 0.1, 0.2, 0.35 and 0.75 and blue at 0.2 and 0.5 — on the
 * canonical capsule over the two backgrounds the bed already captures it on, and keeps the bed's own
 * `orange`, `orange-half` and `blue` cells and the two untinted controls verbatim. Keeping the
 * canonical ids means those cells still have native fixtures, so the ladder's reader can put the
 * native silhouette beside the declared region on them and show that the scratch bed reproduces the
 * Grounding Baseline before any new rung is read.
 *
 * Nothing is typed here that the canonical file already declares: the canvas, the backgrounds, the
 * `capsule-button` component, the three existing tints and the profile list are copied through, and
 * only the six new registry entries and the scene list are this wave's. It writes to the path it is
 * given and never to `apps/reference-apple/scenes.json`.
 *
 * Usage:
 *   node make-scenes.mjs <canonicalScenesJson> <outJson>
 */

import { readFileSync, writeFileSync } from "node:fs";

const [, , canonicalPath, outPath] = process.argv;
if (canonicalPath === undefined || outPath === undefined) {
  throw new Error("usage: make-scenes.mjs <canonicalScenesJson> <outJson>");
}

const canonical = JSON.parse(readFileSync(canonicalPath, "utf8"));

/** The rungs, as `(tint id, strength)`; the three with no alpha are the bed's own. */
const RUNGS = [
  ["orange-010", 0.1],
  ["orange-020", 0.2],
  ["orange-035", 0.35],
  ["orange-half", 0.5],
  ["orange-075", 0.75],
  ["orange", 1.0],
  ["blue-020", 0.2],
  ["blue-050", 0.5],
  ["blue", 1.0],
];

const tints = {
  orange: canonical.tints.orange,
  "orange-half": canonical.tints["orange-half"],
  blue: canonical.tints.blue,
};
for (const [id, strength] of RUNGS) {
  if (tints[id] !== undefined) continue;
  const seed = id.startsWith("orange") ? canonical.tints.orange : canonical.tints.blue;
  tints[id] = {
    srgb: seed.srgb,
    alpha: strength,
    $comment:
      `W19's strength ladder: the same seed as '${id.startsWith("orange") ? "orange" : "blue"}' at ` +
      `strength ${strength}. The registry's alpha IS the strength on both harnesses.`,
  };
}

const backgrounds = ["photo", "checkerboard"];
const scenes = [];
for (const background of backgrounds) {
  scenes.push({ id: `${background}__capsule-button__rest`, background, component: "capsule-button", state: "rest" });
  for (const [id] of RUNGS) {
    scenes.push({
      id: `${background}__capsule-button__rest-tint-${id}`,
      background,
      component: "capsule-button",
      state: "rest",
      tint: id,
    });
  }
}

const out = {
  $comment: [
    "W19 G0's scratch ladder bed — the author tint's strength axis on the canonical capsule over",
    "the two backgrounds the bed captures it on, at 1x and 2x and under the two fold profiles.",
    "Written by make-scenes.mjs from apps/reference-apple/scenes.json; it is read by capture-web",
    "through VITREA_SCENES and by ladder.ts, and NOTHING canonical is written.",
    "",
    "Every scene id that exists on the canonical bed is that bed's id verbatim, so the ladder's",
    "reader can take the native silhouette on those cells and show that this scratch run reproduces",
    "the Grounding Baseline before a new rung is read. The six new registry entries are the same two",
    "seeds at the strengths the charter names; the registry's alpha is the strength.",
    "",
    "Every scene is filed 'recorded': W19 fits nothing to this bed, and 'recorded' is compare's",
    "opt-in set, so a cell here cannot reach a calibration or validation number by accident.",
  ],
  version: canonical.version,
  canvas: canonical.canvas,
  backgrounds: Object.fromEntries(backgrounds.map((key) => [key, canonical.backgrounds[key]])),
  components: { "capsule-button": canonical.components["capsule-button"] },
  tints,
  states: canonical.states,
  scenes,
  profiles: canonical.profiles
    .filter((profile) => ["1x", "2x"].some((s) => profile.key.includes(`-${s}-light-standard`)))
    .map((profile) => ({ ...profile, scenes: scenes.map((s) => s.id) })),
  split: { calibration: [], validation: [], holdout: [], recorded: scenes.map((s) => s.id) },
};

writeFileSync(outPath, `${JSON.stringify(out, null, 2)}\n`);
process.stdout.write(`${String(scenes.length)} scenes, ${String(Object.keys(tints).length)} tints -> ${outPath}\n`);
