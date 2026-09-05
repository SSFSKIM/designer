/**
 * W19 G0 (c) — the native ladder's scene bed, derived from the canonical one.
 *
 * `apps/reference-apple/scenes-w19-probe.json` is written by this script rather than typed, for the
 * same reason W19's web-side bed is: every value it shares with the frozen bed — the canvas, the two
 * backgrounds, the `capsule-button` component, the `orange` and `orange-half` registry entries — is
 * copied through, so a probe cell cannot differ from its canonical twin by a transcription.
 *
 * **What it is for.** The bed's tint registry carries strengths 1.0 and 0.5, so Apple's own
 * behaviour on the strength axis is one point and a full-strength anchor. Both of vitrea's tiers read
 * +0.020 over native at 0.5 on the photo capsule (§5.75 §4), and W19 fixes the CSS tier's fold
 * against the RENDERER's composite, not against Apple's — so the renderer's own gap on this axis
 * needs to be a curve rather than a point before anyone charters it. That is all this bed is: data
 * for the renderer's ledger, fitted to nothing (contract X10).
 *
 * **The controls.** `photo__capsule-button__rest-tint-orange`, `…-tint-orange-half` and
 * `checkerboard__capsule-button__rest-tint-orange` are the canonical bed's own ids at the canonical
 * bed's own geometry and tint, so their fixtures must come back byte-identical to the frozen ones.
 * A twin that is not byte-identical disqualifies the whole bed rather than being explained.
 *
 * Every scene is filed `recorded`: W9's rule files a probe cell as recorded when it duplicates
 * frozen-bed geometry whose twin is floored or holdout, and X10 forbids fitting anything here at
 * all, so a split naming any cell `calibration` would declare a fit phase this wave has ruled out.
 *
 * Usage:
 *   node make-probe-scenes.mjs <canonicalScenesJson> <outJson>
 */

import { readFileSync, writeFileSync } from "node:fs";

const [, , canonicalPath, outPath] = process.argv;
if (canonicalPath === undefined || outPath === undefined) {
  throw new Error("usage: make-probe-scenes.mjs <canonicalScenesJson> <outJson>");
}
const canonical = JSON.parse(readFileSync(canonicalPath, "utf8"));

/** The ladder, as `(tint id, strength)`. `orange-half` and `orange` are the bed's own entries. */
const RUNGS = [
  ["orange-010", 0.1],
  ["orange-020", 0.2],
  ["orange-035", 0.35],
  ["orange-half", 0.5],
  ["orange-075", 0.75],
  ["orange", 1.0],
];

const tints = { orange: canonical.tints.orange, "orange-half": canonical.tints["orange-half"] };
for (const [id, strength] of RUNGS) {
  if (tints[id] !== undefined) continue;
  tints[id] = {
    srgb: canonical.tints.orange.srgb,
    alpha: strength,
    $comment: `W19's native strength ladder: systemOrange at strength ${strength}. SwiftUI's Color carries opacity as the strength, exactly as vitrea reads a tint colour's alpha.`,
  };
}

const backgrounds = ["photo", "checkerboard"];
const scenes = [];
for (const background of backgrounds) {
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
    "W19 probe scene matrix — the author tint's strength axis, natively, and NOTHING else reads",
    "this file. It runs through VITREA_SCENES into its own fixtures dir under",
    "packages/calibration/results/2026-09-05-w19-author-tint-fold/probe/, so the canonical",
    "scenes.json and the frozen bed stay untouched (contract X10). Both backgrounds reuse an",
    "existing kind: nothing rebuilds and no TCC re-grant is needed for the rasters.",
    "",
    "What it is for. W19 corrects the CSS tier's author-tint composite against the RENDERER's",
    "expression at every strength; Apple's own curve on that axis is a separate question and this",
    "bed is its data. The bed carries strengths 1.0 and 0.5 only, and both vitrea tiers read +0.020",
    "over native at 0.5 on the photo capsule — one point. These twelve cells make it a curve.",
    "",
    "Three cells are the canonical bed's own ids at its own geometry and tint and must come back",
    "byte-identical to the frozen fixtures: photo tint-orange, photo tint-orange-half and",
    "checkerboard tint-orange. Nothing here is fitted to anything.",
  ],
  version: canonical.version,
  canvas: canonical.canvas,
  backgrounds: Object.fromEntries(backgrounds.map((key) => [key, canonical.backgrounds[key]])),
  components: { "capsule-button": canonical.components["capsule-button"] },
  tints,
  states: { rest: canonical.states.rest },
  scenes,
  profiles: [
    {
      key: "apple-macos-26.5-1x-light-standard",
      colorScheme: "light",
      a11y: "standard",
      scenes: "all",
      $comment:
        "The probe's one profile. 1x only, as W18's was: this machine presents at 1x and the " +
        "canonical 2x fixtures were captured on a reconfigured display, so a 2x native ladder is a " +
        "session the user opens (W19 Decision Log 1 q1(a); the charter's Deferred list).",
    },
  ],
  split: {
    $comment: [
      "Declared before the first capture. Nothing is fitted to this bed: every cell is 'recorded'",
      "and compare must be asked for that set twice over.",
    ],
    calibration: [],
    validation: [],
    holdout: [],
    recorded: scenes.map((s) => s.id),
  },
};

writeFileSync(outPath, `${JSON.stringify(out, null, 2)}\n`);
process.stdout.write(`${String(scenes.length)} scenes, ${String(Object.keys(tints).length)} tints -> ${outPath}\n`);
