/**
 * W20 G0 — the probe bed's `provenance.json`, written from the runs rather than by hand.
 *
 * W9's rule (claims §5.30) is that a bed's custody travels with its bytes: which runs were taken,
 * which were kept, which were disqualified and why, the HID idle at each run's start and end, and
 * the machine the pixels came off. Every one of those is in the runs' own manifests, so this reads
 * them rather than restating them — a provenance block typed by hand is a second record that can
 * disagree with the first.
 *
 * A run is DISQUALIFIED when any of its cells fails its own attestation: `presentedActive` (Liquid
 * Glass draws a flat inactive appearance when the window is not key), `deterministic`, or
 * `materialRendered`. The failing cells are named.
 *
 * Usage:
 *   node make-provenance.mjs <runRoot> <outJson> <keptRunNumber>...
 */

import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const [, , runRoot, outJson, ...kept] = process.argv;
if (runRoot === undefined || outJson === undefined || kept.length === 0) {
  throw new Error("usage: make-provenance.mjs <runRoot> <outJson> <keptRunNumber>...");
}

const runs = readdirSync(runRoot)
  .filter((name) => /^run-\d+$/.test(name))
  .sort((a, b) => Number(a.split("-")[1]) - Number(b.split("-")[1]));

const idle = {};
const excluded = {};
const audits = {};
for (const run of runs) {
  const manifestPath = resolve(runRoot, run, "manifest.json");
  let manifest;
  try {
    manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
  } catch {
    continue;
  }
  const label = manifest.captureProtocol.runLabel;
  const fixtures = manifest.profiles[0].fixtures;
  const failing = fixtures.filter(
    (f) => !(f.presentedActive && f.deterministic && f.materialRendered),
  );
  idle[label] = [
    Math.round(manifest.captureProtocol.hidIdleSecondsAtStart),
    Math.round(manifest.captureProtocol.hidIdleSecondsAtEnd),
  ];
  audits[label] = `${String(fixtures.length - failing.length)}/${String(fixtures.length)}`;
  if (!kept.includes(run.split("-")[1])) {
    excluded[label] =
      failing.length === 0
        ? "attested, not needed: the materialised set was already complete"
        : `${String(failing.length)} of ${String(fixtures.length)} cells failed attestation ` +
          `(${failing.map((f) => f.sceneId).join(", ")})`;
  }
}
const keptLabels = kept.map((n) => `w20-probe-${n}`);
const seed = JSON.parse(readFileSync(resolve(runRoot, `run-${kept[0]}`, "manifest.json"), "utf8"));

writeFileSync(
  outJson,
  `${JSON.stringify(
    {
      $comment: [
        "W20's probe bed: twenty cells at 1x — `RoundedRectangle(cornerRadius: r, style:",
        ".continuous)` at r = 14, 16, 18, 20, 22 on a 120 x 44 box and at r = 14, 18, 22 on a",
        "44 x 44 box, with `Capsule()` on each box as the control, over `light-solid` and",
        "`checkerboard` — captured on this machine by W9's protocol (claims §5.30: a 6 s bare",
        "neutral reset before each cell, the one stable order, the run refused unless the machine",
        "had been idle 45 s) and materialised by the majority byte-state per cell over the attested",
        "runs.",
        "",
        "Nothing is fitted to this bed. It exists because vitrea's Apple reference clamps the RADIUS",
        "above the saturation ratio 0.327083 on an assumption nobody measured (claims 5.83), and the",
        "canonical bed's capsules are `Capsule()`, which cannot answer the question.",
      ],
      materializedFrom: keptLabels,
      excludedRuns: excluded,
      rule:
        "majority byte-state per cell across the attested runs (frequency-settled, claims §5.30); " +
        "shares recorded per cell",
      auditResult: audits,
      idleSecondsAtStartAndEnd: idle,
      internalControl: {
        $comment:
          "The layer dump shows `Capsule()` and `RoundedRectangle(cornerRadius: 22, style: " +
          ".continuous)` reaching Core Animation as the SAME declaration — a CASDFElementLayer of " +
          "the same bounds with cornerRadius 22 and cornerCurve continuous. The two cells must " +
          "therefore be byte-identical on each background, and that is checked rather than assumed.",
        pairs: [
          ["light-solid__capsule-120x44__rest", "light-solid__rrect-120x44-r22__rest"],
          ["checkerboard__capsule-120x44__rest", "checkerboard__rrect-120x44-r22__rest"],
          ["light-solid__capsule-44x44__rest", "light-solid__rrect-44x44-r22__rest"],
          ["checkerboard__capsule-44x44__rest", "checkerboard__rrect-44x44-r22__rest"],
        ],
      },
      toolchain: { hardware: seed.hardware, captureProtocol: seed.captureProtocol },
    },
    null,
    2,
  )}\n`,
);
process.stdout.write(`provenance -> ${outJson}\n`);
