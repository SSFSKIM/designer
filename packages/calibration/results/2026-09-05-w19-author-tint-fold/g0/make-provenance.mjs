/**
 * W19 G0 (c) — the probe bed's `provenance.json`, written from the runs rather than by hand.
 *
 * W9's rule (claims §5.30) is that a bed's custody travels with its bytes: which runs were taken,
 * which were kept, which were disqualified and why, the HID idle at each run's start and end, and the
 * machine the pixels came off. Every one of those is in the runs' own manifests, so this reads them
 * rather than restating them — a provenance block typed by hand is a second record that can disagree
 * with the first.
 *
 * A run is DISQUALIFIED when any of its cells fails its own attestation: `presentedActive` (Liquid
 * Glass draws a flat inactive appearance when the window is not key, which is where the 2026-08-30
 * bed's author tints went), `deterministic`, or `materialRendered`. The failing cells are named.
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
        ? "attested, not needed: seven runs were taken before it"
        : `${String(failing.length)} of ${String(fixtures.length)} cells failed attestation ` +
          `(${failing.map((f) => f.sceneId).join(", ")}); HID activity during the run`;
  }
}
const keptLabels = kept.map((n) => `w19-probe-${n}`);
const seed = JSON.parse(readFileSync(resolve(runRoot, `run-${kept[0]}`, "manifest.json"), "utf8"));

writeFileSync(
  outJson,
  `${JSON.stringify(
    {
      $comment: [
        "W19's probe bed (the charter's X10): twelve cells at 1x — the author tint's strength ladder",
        "on the canonical capsule over `photo` and `checkerboard` at 0.1, 0.2, 0.35, 0.5, 0.75 and 1.0",
        "— captured on this machine by W9's protocol (claims §5.30: a 6 s bare neutral reset before",
        "each cell, the one stable order, the run refused unless the machine had been idle 45 s) and",
        "materialised by the majority byte-state per cell over seven attested runs.",
        "",
        "Nothing is fitted to this bed. It exists so that the renderer's own gap to Apple on the",
        "strength axis is a curve rather than the single point the frozen bed carries at 0.5.",
      ],
      materializedFrom: keptLabels,
      excludedRuns: excluded,
      rule:
        "majority byte-state per cell across seven attested runs (frequency-settled, claims §5.30); " +
        "shares recorded per cell",
      auditResult: audits,
      idleSecondsAtStartAndEnd: idle,
      recordedTwins: {
        $comment:
          "The three cells this bed shares with the frozen one, at the frozen bed's own ids and " +
          "geometry. They must be byte-identical to the canonical fixtures or the bed is refused.",
        cells: [
          "photo__capsule-button__rest-tint-orange",
          "photo__capsule-button__rest-tint-orange-half",
          "checkerboard__capsule-button__rest-tint-orange",
        ],
      },
      toolchain: { hardware: seed.hardware, captureProtocol: seed.captureProtocol },
    },
    null,
    2,
  )}\n`,
);
process.stdout.write(`provenance -> ${outJson}\n`);
