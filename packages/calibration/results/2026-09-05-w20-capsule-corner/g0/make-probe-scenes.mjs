// W20 G0 — write `apps/reference-apple/scenes-w20-probe.json`, the native probe's own bed.
//
// The bed is generated rather than hand-written for one reason: the ladder is a function of the
// saturation ratio (`1 / (2 * APPLE_REACH)` = 0.327083) and every component's comment quotes the
// ratio, the reach and the overflow that ratio implies. Deriving them here means the file cannot
// disagree with itself, and the ratio appears once.
//
// It writes a NEW file. `apps/reference-apple/scenes.json` is never touched, and the probe runs
// through `VITREA_SCENES` into its own fixtures directory.
//
// Usage: `node make-probe-scenes.mjs`, from this directory.

import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(HERE, "../../../../../apps/reference-apple/scenes-w20-probe.json");

/** Apple's published corner-curve expansion factor for `.continuous`. */
const APPLE_REACH = 1.52866495;
const SATURATION = 1 / (2 * APPLE_REACH);

const f = (x, n = 4) => x.toFixed(n);

/** One rung's arithmetic, so the comment states what the rung is rather than repeating a number. */
function rung(w, h, r, extra) {
  const budget = Math.min(w, h) / 2;
  const ratio = r / Math.min(w, h);
  const reach = APPLE_REACH * r;
  const overflow = (reach / budget - 1) * 100;
  const clamped = budget / APPLE_REACH;
  const head =
    ratio <= SATURATION
      ? `Ratio ${f(ratio)}, BELOW Apple's saturation ratio ${f(SATURATION, 6)} ` +
        `(= 1 / (2 * ${APPLE_REACH})): the reach ${f(reach, 2)} px still fits the corner's budget ` +
        `${f(budget, 2)} px, so every candidate policy draws the same corner here.`
      : `Ratio ${f(ratio)}, above saturation: the reach would be ${f(reach, 2)} px against a ` +
        `budget of ${f(budget, 2)} px, an overflow of ${f(overflow, 1)} %. vitrea's policy today ` +
        `clamps the radius to ${f(clamped, 2)} px; a shoulder compression would keep ${r}.`;
  return { kind: "rrect", size: [w, h], radius: r, $comment: extra ? `${head} ${extra}` : head };
}

const components = {
  "rrect-120x44-r14": rung(120, 44, 14,
    "It is the ladder's control: the rung that tests the instrument rather than Apple."),
  "rrect-120x44-r16": rung(120, 44, 16, "The first rung above saturation."),
  "rrect-120x44-r18": rung(120, 44, 18,
    "Mid-ladder, where the two candidate policies are furthest apart per unit of overflow."),
  "rrect-120x44-r20": rung(120, 44, 20, ""),
  "rrect-120x44-r22": rung(120, 44, 22,
    "The capsule limit reached by RoundedRectangle rather than by Capsule(). If Apple compresses " +
    "the shoulder this must draw exactly the stadium the capsule control draws; if Apple clamps " +
    "the radius it draws a rounded rectangle whose corner is a third smaller. The two are 7.6 px " +
    "apart on the contour, fifteen times the grid's 0.5 px floor."),
  "capsule-120x44": {
    kind: "capsule",
    size: [120, 44],
    $comment:
      "The control. `Capsule()` is a circular stadium by definition (`Sources/SceneViews.swift`), " +
      "so this cell is what the contour reader is verified against before any rung is read, and " +
      "it is what `rrect-120x44-r22` is compared to.",
  },
  "rrect-44x44-r14": rung(44, 44, 14,
    "The circle regime — the toolbar's 44 x 44 case — below saturation."),
  "rrect-44x44-r18": rung(44, 44, 18, "The square box's mid rung."),
  "rrect-44x44-r22": rung(44, 44, 22,
    "The square box at the limit: a circle of diameter 44 under a shoulder compression, a rounded " +
    "square under vitrea's radius clamp. This is the shape the bed's `toolbar-group` draws."),
  "capsule-44x44": {
    kind: "capsule",
    size: [44, 44],
    $comment:
      "`Capsule()` on a square box, which is a circle. The second control, and the shape the " +
      "bed's `toolbar-group` items are declared as.",
  },
};

const backgrounds = {
  "light-solid": {
    kind: "solid",
    srgb: [242, 242, 247],
    $comment:
      "System light grey, the canonical bed's entry verbatim so the committed raster is reused " +
      "and nothing rebuilds. The flat case: no backdrop detail, so the rim band reads alone and " +
      "its peak locus is the contour.",
  },
  checkerboard: {
    kind: "checkerboard",
    cell: 16,
    a: [0, 0, 0],
    b: [255, 255, 255],
    $comment:
      "The canonical bed's entry verbatim. Every cell edge is a step edge, so the material's blur " +
      "shows as a collapse of LOCAL CONTRAST everywhere inside the surface — which is the " +
      "silhouette rule this probe reads it with, and which the outer shadow does not trip because " +
      "a darkened checker keeps its contrast.",
  },
};

const scenes = [];
for (const background of ["light-solid", "checkerboard"]) {
  for (const component of Object.keys(components)) {
    scenes.push({ id: `${background}__${component}__rest`, background, component, state: "rest" });
  }
}

const doc = {
  $comment: [
    "W20 probe scene matrix — what Apple draws for RoundedRectangle(cornerRadius:style:.continuous)",
    "when the radius exceeds 0.327083 of the short side. NOTHING else reads this file. It runs",
    "through VITREA_SCENES into its own fixtures directory under",
    "packages/calibration/results/2026-09-05-w20-capsule-corner/probe/, so the canonical",
    "scenes.json and the frozen bed stay untouched. Both backgrounds reuse an existing kind",
    "verbatim: nothing rebuilds and no TCC re-grant is needed for the rasters.",
    "",
    "What it is for. vitrea's Apple reference clamps the RADIUS above the saturation ratio",
    "1 / (2 * APPLE_REACH) = 0.327083, so that Apple's measured corner reach 1.52866495 * r still",
    "fits half the short side (packages/geometry/src/apple.ts, buildAppleContour; pinned by",
    "test/apple.test.ts under the name 'Apple's budget policy is its own'). That was never",
    "measured — S2 fitted the corner below the ratio only, and the bed's capsules are Capsule(), a",
    "circular stadium by definition, which cannot answer it (claims 5.83). These rungs put the",
    "question to Apple: five radii on a 120 x 44 box from just below the ratio to the capsule",
    "limit, three on the 44 x 44 box that is the toolbar's case, and Capsule() beside each as the",
    "control whose true shape is known.",
    "",
    "Untinted, state rest, 1x light-standard only. This measures a CONTOUR: the tint and the",
    "colour scheme are noise on that axis, and a corner law is scale-free, so 1x is the whole",
    "measurement rather than half of one. Two backgrounds because the contour is read two ways —",
    "the checkerboard by a local-contrast silhouette and light-solid by the rim band's peak locus.",
    "Nothing here is fitted to anything: every scene is 'recorded'.",
  ],
  version: 2,
  canvas: { width: 320, height: 200 },
  backgrounds,
  components,
  states: { rest: { $comment: "No interaction." } },
  scenes,
  profiles: [
    {
      key: "apple-macos-26.5-1x-light-standard",
      colorScheme: "light",
      a11y: "standard",
      scenes: "all",
      $comment:
        "The probe's one profile, as W18's and W19's probes had one: this machine presents at 1x " +
        "and the canonical 2x fixtures were captured on a reconfigured display.",
    },
  ],
  split: {
    $comment: [
      "Declared before the first capture. Nothing is fitted to this bed: every cell is 'recorded'",
      "and no number taken from it tunes a constant.",
    ],
    calibration: [],
    validation: [],
    holdout: [],
    recorded: scenes.map((s) => s.id),
  },
};

writeFileSync(OUT, `${JSON.stringify(doc, null, 2)}\n`);
console.log(`${scenes.length} scenes, ${Object.keys(components).length} components → ${OUT}`);
