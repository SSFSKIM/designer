/**
 * W21 G0 — `apps/reference-apple/scenes-w21-probe.json`, generated from W9's grid.
 *
 * The wave's binding rule is that the dark probe is W9's 56-cell grid and nothing else: the same
 * backgrounds, the same components, the same tint, the same canvas, the same scene ids, so that a
 * dark reading and W9's light reading are the same measurement under two schemes. Only two things
 * change, and both are derived rather than typed: the profile block, which becomes the single dark
 * profile the wave measures, and the split, which is re-derived by W9's own rule against the
 * canonical DARK bed instead of the light one.
 *
 * W9's rule for `recorded` is that a probe cell duplicating the geometry of a canonical cell that
 * is holdout (or floored) in the bed the fit will be judged on cannot be fitted on: reading it is
 * allowed, fitting it would be peeking at a held-out row through its twin. Against the canonical
 * dark bed that set collapses to one cell. The dark profile's holdout is `photo__rrect-lg__rest`,
 * `checkerboard__glass-over-glass__rest` and `mid-dark-solid__capsule-button__rest`; the probe grid
 * has no `glass-over-glass` component and no `mid-dark-solid` capsule, so `photo__rrect-lg__rest`
 * is the only twin, and the dark pair carries no regression floors (W21 charter, Grounding
 * Baseline) so nothing is recorded on that account either. The holdout, the validation five and
 * therefore the calibration remainder keep W9's declared membership: the `checkerboard-8` column
 * whole (the pitch the fit never sees) plus the three large extremes, and W9's five validation
 * cells. The seven cells W9 recorded for its light twins move into calibration here, which is the
 * whole point of re-deriving rather than copying.
 *
 * Usage: `node make-probe-scenes.mjs <w9ScenesJson> <canonicalScenesJson> <outJson>`
 */

import { readFileSync, writeFileSync } from "node:fs";

const [, , w9Path, canonicalPath, outPath] = process.argv;
if (w9Path === undefined || canonicalPath === undefined || outPath === undefined) {
  throw new Error("usage: make-probe-scenes.mjs <w9ScenesJson> <canonicalScenesJson> <outJson>");
}

const w9 = JSON.parse(readFileSync(w9Path, "utf8"));
const canonical = JSON.parse(readFileSync(canonicalPath, "utf8"));

const DARK_PROFILE = "apple-macos-26.5-1x-dark-standard";
const darkProfile = canonical.profiles.find((p) => p.key === DARK_PROFILE);
if (darkProfile === undefined) throw new Error(`no ${DARK_PROFILE} in the canonical bed`);

/** The canonical dark bed's held-out cells: the bed's holdout intersected with what dark captures. */
const darkScenes = new Set(darkProfile.scenes);
const darkHoldout = canonical.split.holdout.filter((id) => darkScenes.has(id));

/** A probe cell is a twin of a canonical cell when the ids match: the grid reuses the bed's names. */
const probeIds = new Set(w9.scenes.map((s) => s.id));
const recorded = darkHoldout.filter((id) => probeIds.has(id)).sort();

const holdout = [...w9.split.holdout].sort();
const validation = [...w9.split.validation].sort();
const assigned = new Set([...recorded, ...holdout, ...validation]);
const calibration = w9.scenes.map((s) => s.id).filter((id) => !assigned.has(id));

const out = {
  $comment: [
    "W21 probe scene matrix — W9's declared grid (claims 5.30) captured under the DARK",
    "scheme, and NOTHING else reads this file. It runs through VITREA_SCENES into its own",
    "fixtures dir, so the canonical scenes.json and the frozen bed stay untouched. Every",
    "background, component, tint, state and scene id is W9's verbatim: the dark reading and",
    "the light one are then the same measurement under two schemes, cell for cell.",
    "",
    "Two things differ from scenes-w9-probe.json, and both are derived, not typed (see",
    "results/2026-09-06-w21-dark-scheme/g0/make-probe-scenes.mjs). The profile is the single",
    "dark one the wave measures. And the split is re-derived by W9's own rule against the",
    "canonical DARK bed: 'recorded' means a probe cell whose canonical twin is held out on the",
    "dark profiles, so that no fit can peek at a held-out row through its twin. On the dark",
    "bed that set is one cell — photo__rrect-lg__rest — because the other two dark holdouts",
    "(checkerboard__glass-over-glass__rest, mid-dark-solid__capsule-button__rest) have no twin",
    "in this grid, and the dark pair carries no regression floors. W9's holdout (the",
    "checkerboard-8 column whole plus the three large extremes) and W9's validation five are",
    "kept as declared; the seven cells W9 had to record for its LIGHT twins are calibration",
    "here.",
    "",
    "The split binds the FIT PHASE that follows the probe; the probe itself fits nothing, and",
    "G0 reads everything. G1 fits on 'calibration', checks itself on 'validation', and leaves",
    "this file's 'holdout' unread — the wave's one holdout read is the CANONICAL bed's, at",
    "G1's dry run (W21 X6).",
  ],
  version: w9.version,
  canvas: w9.canvas,
  backgrounds: w9.backgrounds,
  components: w9.components,
  tints: w9.tints,
  states: w9.states,
  scenes: w9.scenes,
  profiles: [
    {
      key: DARK_PROFILE,
      colorScheme: "dark",
      a11y: "standard",
      scenes: "all",
      $comment:
        "The probe's one profile — the mechanism is scale-free in every prior reading " +
        "(claims 5.30), and the canonical dark bed's 2x rows sit within 0.001 of their 1x " +
        "twins on every cell, so a 2x probe is deferred (W21 Deferred).",
    },
  ],
  split: {
    $comment: [
      "Declared 2026-09-06 in the W21 charter's G0, before the first capture.",
      "Binds the fit phase; the probe reads everything.",
      "Re-derived from W9's split by W9's rule against the canonical dark bed.",
    ],
    calibration,
    validation,
    holdout,
    recorded,
  },
};

writeFileSync(outPath, `${JSON.stringify(out, null, 2)}\n`);
process.stdout.write(
  `${outPath}: ${String(out.scenes.length)} cells — ` +
    `${String(calibration.length)} calibration, ${String(validation.length)} validation, ` +
    `${String(holdout.length)} holdout, ${String(recorded.length)} recorded\n`,
);
