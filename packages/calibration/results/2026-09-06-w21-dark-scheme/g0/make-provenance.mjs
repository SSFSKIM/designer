/**
 * W21 G0 — the dark probe bed's `provenance.json`, written from the runs rather than by hand.
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
const keptLabels = kept.map((n) => `w21-probe-${n}`);
const seed = JSON.parse(readFileSync(resolve(runRoot, `run-${kept[0]}`, "manifest.json"), "utf8"));

writeFileSync(
  outJson,
  `${JSON.stringify(
    {
      $comment: [
        "W21's probe bed: W9's declared 56-cell grid (claims §5.30) — the five-component size",
        "sweep over the checkerboard pitch axis and the low-contrast equal-mean twin, the",
        "three-component sweep over the text-row family and the three solid response anchors,",
        "`photo` as the broadband control, and the orange tint capsule across the pitch sweep —",
        "captured under the DARK scheme at 1x on this machine, by W9's protocol (a 6 s bare",
        "neutral reset before each cell, the one stable order, the run refused unless the machine",
        "had been idle 45 s), and materialised by the majority byte-state per cell over the",
        "attested runs.",
        "",
        "Nothing is fitted to this bed at G0. It exists because the dark profile's response",
        "surface has never been measured: `backdropToneResponseStrength` is 0 on the dark",
        "profiles precisely because their anchors were read on the LIGHT reference, and the",
        "canonical dark bed cannot supply them — it has no `light-solid` scene, and over its dark",
        "solids the silhouette extractor returns the rim ring rather than the body (claims §5.87).",
        "The six anchors G1 records come from here, read under the declared geometry (W21 X2).",
        "",
        "The scene bed is `apps/reference-apple/scenes-w21-probe.json`, which is W9's grid",
        "verbatim with one dark profile and the split re-derived against the canonical DARK bed.",
        "The probe's own holdout column is unread at G0.",
      ],
      materializedFrom: keptLabels,
      excludedRuns: excluded,
      rule:
        "majority byte-state per cell across the attested runs (frequency-settled, claims §5.30); " +
        "shares recorded per cell",
      auditResult: audits,
      idleSecondsAtStartAndEnd: idle,
      toolchain: { hardware: seed.hardware, captureProtocol: seed.captureProtocol },
    },
    null,
    2,
  )}\n`,
);
process.stdout.write(`provenance -> ${outJson}\n`);
