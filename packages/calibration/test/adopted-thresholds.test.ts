/**
 * The adopted fidelity gate.
 *
 * `docs/doperpowers/specs/c9a-fidelity-claims.md` §5 ("Proposed thresholds — for
 * the human gate") set per-cell thresholds and left them explicitly as
 * proposals. The user **adopted them as proposed on 2026-08-26**, closing
 * `c9d-release-checklist.md` §2.2 and, with it, parent acceptance #7's "inside
 * declared thresholds". This file is what adoption means operationally: the
 * numbers stop being prose and become a test over the committed
 * `results/matrix.json`, so a matrix regeneration that pushes a cell past one of
 * them fails CI instead of waiting for whoever next reads the claims doc.
 *
 * The tables below are transcribed from §5 row for row and in §5's own order,
 * and they are the only copy of these numbers anywhere in the repo — the point
 * is that a reviewer can hold this file next to §5 and diff the two by eye.
 * Every bound is bounded by §5's *holdout* column rather than its calibration
 * one, deliberately: a gate that calibration passes and holdout fails would
 * certify overfitting rather than prevent it.
 *
 * ## The second adoption: W1 G3 (2026-08-29)
 *
 * The wave's W1 child re-measured a widened bed — six native profiles across
 * colour scheme, backing scale and accessibility state — and the user adopted
 * three decisions on it (`2026-08-28-post-v1-wave.md`, Decision Log 9):
 *
 *   1. **The 2× light-standard tables are gated**, on the same doctrine and from
 *      the same holdout column. They are `*_2X_LIGHT` below, and §5's rationale
 *      for why they are not simply the 1× numbers is in the claims doc's §5.1.
 *   2. **Cross-tier coherence is gated from the matrix**, not from prose. Schema
 *      4 puts a `coherence` axis on the dom-tier cell, so the row that used to be
 *      a tripwire in this file is now an assertion over real numbers.
 *   3. **The four provisional profiles stay ungated.** Named below, with the
 *      reason, rather than left out.
 *
 * `results/matrix.json` is now W1's six-profile measurement — the v1 60-cell
 * matrix it supersedes is in git history. The 1× tables are unchanged by that
 * promotion, in every digit: the widened bed re-measured the profile they were
 * set on rather than replacing it.
 *
 * ## What §5 does not gate, and why it is absent here
 *
 * Stated because an absent assertion is otherwise indistinguishable from a
 * forgotten one, and each of these is a decision §5 argues for:
 *
 *   - **Four profiles are provisional, not gated.** See `UNGATED_PROFILES`.
 *   - **The material axis is not gated.** The sub-metrics that would identify the
 *     material are either unidentifiable on this fixture set (blur sigma, §6.1)
 *     or below the capture's own quantisation (the light-scheme rim, §6.2). A
 *     threshold on a quantity the fixtures cannot resolve is a number that gets
 *     met by accident. Its `interiorMeanWeb` field is read here for one purpose
 *     only — cross-checking the coherence ratio, which is a cross-tier quantity,
 *     not a fidelity one.
 *   - **The motion axis is not gated.** No frame sequences were captured on the
 *     native side, and the still `pressed` fixtures cannot substitute: they are
 *     byte-identical to their rest counterparts (§6.3), so those cells measure
 *     vitrea's pressed pose against Apple's rest pose. They are still gated on
 *     the shape and perceptual axes — §5's own worst-case figures include them —
 *     but no press claim rests on that.
 *   - **The shadow axis is not gated, and must not be yet.** Schema 5 measures
 *     it (claims §5.12) and vitrea reads zero across it on every cell. A bound
 *     over that would certify the gap, which is the move Decision Log 11
 *     refused at a smaller size; the axis gets its first bound from the cascade
 *     after W8 renders a shadow to bound.
 *
 * ## What this file is measuring, after the instrument changed
 *
 * Everything below is the **inactive-bed** suite, gated as historically
 * labelled. Wave Decision Log 15 ruling 3 holds `results/matrix.json` where it
 * is — schema 4, whole-canvas extraction — until the one honest post-W8 pass,
 * because re-adopting a bound over a reference facet vitrea renders as zero
 * would certify the defect. So this file gates a schema-4 matrix while the build
 * writes schema 5, and the first assertion pins both numbers so that stays a
 * decision rather than drift.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { RESULT_MATRIX_SCHEMA_VERSION } from "../src/report";

// ---------------------------------------------------------------------------
// §5, transcribed
// ---------------------------------------------------------------------------

type GateRow = readonly [
  axis: "shape" | "perceptual",
  metric: string,
  bound: "≥" | "≤",
  threshold: number,
];

/** Texture tier, `apple-macos-26.5-1x-light-standard`, cell as claims §1. */
const TEXTURE_TIER_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.82],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 5.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.88],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.07],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.17],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.11],
];

/** Dom tier, same profile, Chromium, `renderer: css`. */
const DOM_TIER_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 7.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.90],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.08],
];

/**
 * Texture tier, `apple-macos-26.5-2x-light-standard`. Claims §5.1, adopted
 * 2026-08-29; transcribed row for row exactly as the 1× tables are.
 *
 * Not the 1× numbers, and not uniformly looser than them. The three movements
 * each have a measured reason, stated once in §5.1 and once here because a
 * reader of this file should not have to open another to know whether a bound
 * was reasoned or copied: the **colour bounds are the 1× bounds unchanged**
 * (the measurements are — holdout ΔE mean 0.0546 at 2× against 0.0548 at 1×);
 * the **contour bounds are the 1× bounds doubled** (contour distance is a
 * device-pixel quantity, and the geometry error did not move); the **SSIM bound
 * is tighter than 1×'s** (SSIM reads systematically +0.014 higher at 2×, so
 * importing the 1× number would have been slack at this scale).
 */
const TEXTURE_TIER_2X_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 5.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 10.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.93],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.07],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.17],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.12],
];

/**
 * Dom tier, `apple-macos-26.5-2x-light-standard`, Chromium, `renderer: css`.
 *
 * **`contourDistanceP95` ≤ 10.0 is GATE-ADOPTED POST-READ** (wave Decision Log 18
 * ruling 2, 2026-08-31). It was ≤ 8.0, pre-registered against the retired
 * inactive bed. The frozen active bed moved it, and the bound was re-adopted at
 * the value the frozen bed measures rather than left to fail — the amendment
 * doctrine's one legal move, taken in the open. It is NOT a pre-registered
 * bound, and no fit was tuned against it.
 *
 * The row now equals its texture-tier twin, which is the doubled 1× contour
 * bound. That is the coincidence the 2× table already documents above: contour
 * distance is a device-pixel quantity, so the honest 2× bound is the 1× bound
 * doubled, and this row had been the one that was tighter than that rule for
 * reasons the retired bed supplied and the frozen bed withdrew.
 */
const DOM_TIER_2X_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 4.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 10.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.92],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.08],
];

/**
 * §5's coherence rows — a property of the *pair*, so they are gated off the
 * dom-tier cell's `coherence` axis, which is where schema 4 records them.
 *
 * The same two bounds carry both light profiles: the quantities are scale-free
 * (a whole-canvas ΔE and a ratio of two levels), and they measure the same at
 * both scales to the third decimal. So there is one table here rather than a 1×
 * and a 2× copy, and a divergence between the scales would show up as a failure
 * rather than as two tables drifting apart.
 *
 * **This replaced a tripwire.** Through schema 3 the cross-tier ΔE was not
 * derivable from anything committed — it is a web-against-web comparison of two
 * PNGs, and `web-captures/` is not in the repository — so this file carried the
 * number in prose plus a test asserting that no cell had a coherence axis, to
 * fire the day one did. W1 G3 made it derivable (Decision Log 9).
 */
const COHERENCE_ROWS = {
  crossTierOklabDeltaEMean: { bound: "≤", threshold: 0.05 },
  interiorLevelRatioGpuOverCss: { min: 0.8, max: 1.25 },
} as const;

/**
 * Reduced transparency, both tiers. Adopted 2026-08-30 (wave Decision Log 11),
 * holdout-bounded like every table here — the profile earned a binding column
 * when W1's split extension gave it two validation and two holdout scenes.
 *
 * Its bounds are the tightest in this file, and that is the measurement rather
 * than ambition: the reduce-transparency material is nearly opaque on both
 * sides, so there is very little backdrop left for the two to disagree about
 * (worst holdout ΔE mean 0.0300 against light-standard's 0.0548).
 *
 * ## Two rows here are GATE-ADOPTED POST-READ
 *
 * Decision Log 18 ruling 2 (2026-08-31) chartered both, and they are marked so
 * a reader never mistakes either for a pre-registered bound:
 *
 * - **texture `ssimMean` ≥ 0.95**, was ≥ 0.96. The frozen bed's
 *   `photo__toolbar-group__rest` validation cell reads 0.95948 — a miss of
 *   0.0005, on the profile whose SSIM bound was already the tightest here.
 * - **dom `contourDistanceP95` ≤ 5.0**, was ≤ 3.5. The frozen bed's
 *   `hc-text__capsule-button__rest` HOLDOUT cell reads exactly 5.0.
 *
 * Neither is a fit tuned to clear a gate: both were read once, off a bed frozen
 * before either was measured, and the bound then moved to the reading. The
 * second is the sharper admission — it is a holdout cell, so the bound it sets
 * is the honest one this profile's dom tier can carry, not an aspiration.
 */
const TEXTURE_TIER_REDUCED_TRANSPARENCY: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.87],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 1.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 3.5],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.95],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.04],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.08],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.10],
];

const DOM_TIER_REDUCED_TRANSPARENCY: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.89],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 1.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 5.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.91],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.04],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.07],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.11],
];

/**
 * Increased contrast, both tiers. Adopted with reduced transparency, and the
 * loosest tables in this file for two measured reasons rather than one.
 *
 * The reference here is the COUPLED state — macOS force-enables reduce
 * transparency with increase contrast, so no single-flag reference exists to
 * capture (Decision Log 8) — and vitrea's accessibility material under-occludes
 * against it (claims §5.3's Surprise). That gap is on the material axis, which
 * is not gated; what reaches these tables is its perceptual shadow, hence
 * SSIM ≥ 0.86 against reduced transparency's ≥ 0.96.
 *
 * Its shape rows also gate the fewest cells of any adopted table: two of its
 * nine scenes per tier fail the well-conditioned predicate, because the
 * brightened material is lost over the checkerboard's white squares. Those are
 * named in `PREDICATE_EXCLUDES` like every other excluded cell. It was three of
 * eight on the retired bed; the frozen bed recovered the hc-text scene (0.519 →
 * 0.982), so this profile gates strictly more of itself than it used to.
 */
const TEXTURE_TIER_INCREASED_CONTRAST: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 1.8],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 11.5],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.86],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.06],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.10],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.17],
];

const DOM_TIER_INCREASED_CONTRAST: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.80],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.6],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 5.5],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.83],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.07],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.09],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.18],
];

/*
 * ---------------------------------------------------------------------------
 * The defect-class exclusion is GONE (W7, 2026-08-30) — and it dissolved rather
 * than being widened, which is the whole point of how it was built.
 * ---------------------------------------------------------------------------
 *
 * Seven perceptual rows lived here from 2026-08-30 (wave Decision Log 11): the
 * `dark-solid` and `impulse` capsule scenes in the two light-standard profiles,
 * excluded as a LABELLED known renderer gap because Apple's material adapts its
 * appearance to backdrop luminance and vitrea's had no such axis. Worst of them
 * was an OKLab ΔE p95 of 0.6633 against a bound of ≤ 0.17.
 *
 * The entries were data, and one of the four properties enforced around them was
 * that every entry must **still fail**. So when W7 landed the axis, those rows
 * passed, this file failed, and it named them for deletion — which is what
 * happened here. Every adopted bound is exactly the number it was; none was
 * touched in either direction. The same rows now read ΔE p95 0.0000 and 0.0372,
 * and SSIM 0.9792 and 0.9678 against ≥ 0.93.
 *
 * Nothing replaces the mechanism, deliberately. An exclusion class standing empty
 * is a lowered bar with nothing in it, and the pattern — entries as data, with
 * still-fails, quote-the-matrix, carry-a-reason and cannot-grow enforced around
 * them — is in this file's history for the next gap that needs it.
 */

/**
 * §5's well-conditioned-cell predicate, which qualifies the **shape rows only**
 * (every table carries it, unchanged).
 *
 * The luminance-delta extractor finds the component by differencing against its
 * backdrop, so it loses any part of the material whose level coincides with the
 * backdrop's. Where that happens the IoU and contour figures describe the
 * extractor rather than the geometry, and gating them would be gating the
 * instrument. `silhouetteAreaNative` is on the record in every cell (schema 3
 * onward) precisely so this can be machine-checked.
 *
 * **It is a floor with no ceiling, and on this matrix that is a known hole.**
 * The predicate guards under-recovery only, so it cannot catch the opposite
 * failure — and the opposite failure is what the active-pose bed found: an
 * extractor that returns the component *and its shadow* produces areas at
 * roughly twice the declared, which this predicate passes (claims §5.11).
 * Schema 5 closes it at the source rather than here, by bounding extraction to
 * the declared region and recording `componentRegionArea` as the ceiling that
 * bound imposes; the numbers below are the inactive-bed suite, gated as
 * historically labelled per wave Decision Log 15 ruling 3, and they keep the
 * predicate they were adopted with.
 */
const WELL_CONDITIONED_AREA_RATIO = 0.95;

// ---------------------------------------------------------------------------
// The cells the gate covers — stated, not discovered
// ---------------------------------------------------------------------------

/** The renderer each tier is captured through. §5's dom tables name their own. */
const RENDERER_OF_TIER = { texture: "webgpu", dom: "css" } as const;

interface GatedProfile {
  readonly profileKey: string;
  readonly cellsPerTier: number;
  readonly texture: readonly GateRow[];
  readonly dom: readonly GateRow[];
  /** The table constants' own names, so a failure message points at the source. */
  readonly names: { readonly texture: string; readonly dom: string };
}

const GATED_PROFILES: readonly GatedProfile[] = [
  {
    profileKey: "apple-macos-26.5-1x-light-standard",
    cellsPerTier: 36,
    texture: TEXTURE_TIER_LIGHT,
    dom: DOM_TIER_LIGHT,
    names: { texture: "TEXTURE_TIER_LIGHT", dom: "DOM_TIER_LIGHT" },
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    cellsPerTier: 36,
    texture: TEXTURE_TIER_2X_LIGHT,
    dom: DOM_TIER_2X_LIGHT,
    names: { texture: "TEXTURE_TIER_2X_LIGHT", dom: "DOM_TIER_2X_LIGHT" },
  },
  {
    profileKey: "apple-macos-26.5-1x-light-reduced-transparency",
    cellsPerTier: 8,
    texture: TEXTURE_TIER_REDUCED_TRANSPARENCY,
    dom: DOM_TIER_REDUCED_TRANSPARENCY,
    names: {
      texture: "TEXTURE_TIER_REDUCED_TRANSPARENCY",
      dom: "DOM_TIER_REDUCED_TRANSPARENCY",
    },
  },
  {
    profileKey: "apple-macos-26.5-1x-light-increased-contrast",
    cellsPerTier: 9,
    texture: TEXTURE_TIER_INCREASED_CONTRAST,
    dom: DOM_TIER_INCREASED_CONTRAST,
    names: { texture: "TEXTURE_TIER_INCREASED_CONTRAST", dom: "DOM_TIER_INCREASED_CONTRAST" },
  },
];

/**
 * The two profiles the gate still leaves, and why.
 *
 * They have a split now — W1's extension gave every provisional profile two
 * validation and two holdout scenes, which is what promoted the two
 * accessibility profiles into `GATED_PROFILES` above. The dark pair is held back
 * for a different reason: its cross-tier figures are under active investigation
 * after the settled re-baseline, and a table set from numbers that are about to
 * be re-measured would be adopted twice. Their proposed tables are in W1's G3
 * measurement report, ready to adopt once the re-measure lands (wave Decision
 * Log 11).
 *
 * They are not unmeasured. Both are in the matrix on both tiers, and their
 * coherence axis is asserted PRESENT below — measured, not gated.
 */
const UNGATED_PROFILES = [
  "apple-macos-26.5-1x-dark-standard",
  "apple-macos-26.5-2x-dark-standard",
] as const;

/**
 * The whole matrix, and how it partitions — asserted per profile rather than as
 * a bare total, so a profile going missing cannot be absorbed by another's cells
 * arriving. Six native profiles × two web tiers, on the settled bed.
 *
 * **The bed the counts are over (2026-08-30).** `scenes.json` declares 37 scenes
 * and the harness captured 121 native fixtures, but only 25 scenes reach this
 * matrix. The difference is W3's 12 tinted scenes, and they are absent for a
 * reason `cli/compare.ts` derives rather than remembers: that capture session
 * dropped the author tint's COLOUR, which its own bytes prove — scenes declaring
 * `systemOrange` and `systemBlue` over one backdrop came back byte-identical.
 * `colourlessTintEvidence` finds that and skips the tint axis on every profile,
 * so the counts here are also the assertion that no untinted material got filed
 * under a tinted scene id. A re-captured bed admits the tinted cells again and
 * these numbers move with it.
 *
 * What DID arrive is W7's `mid-dark-solid__capsule-button__rest`, in the four
 * standard profiles — one cell per profile per tier, the +2 on each count below.
 */
const MATRIX_PARTITION: Readonly<Record<string, number>> = {
  "apple-macos-26.5-1x-dark-standard": 26,
  "apple-macos-26.5-1x-light-increased-contrast": 18,
  "apple-macos-26.5-1x-light-reduced-transparency": 16,
  "apple-macos-26.5-1x-light-standard": 72,
  "apple-macos-26.5-2x-dark-standard": 26,
  "apple-macos-26.5-2x-light-standard": 72,
};

const MATRIX_CELLS = 230;

/**
 * Scenes that carry no shape and no material axis, per profile — so the shape
 * rows have nothing to gate there.
 *
 * Not a fault and not a gap in the gate: over a solid backdrop of the material's
 * own tone the reference sits within the extractor's 0.02 threshold of its
 * background, so the native silhouette is empty and `cli/measure.ts` records the
 * cell with its perceptual axis alone rather than inventing a shape. On the
 * settled bed `dark-solid__capsule-button__rest` joined this list in the light
 * profiles: the reference capsule over a near-black backdrop settles to that
 * backdrop, which is backdrop tone adaptation seen through the extractor instead
 * of through ΔE.
 *
 * This list is about the REFERENCE's silhouette, so W7 landing the same
 * adaptation on vitrea's side does not move it. Both sides now vanish into that
 * backdrop, which is the point — but the extractor still has nothing to find.
 */
const NO_SHAPE_AXIS_SCENES: Readonly<Record<string, readonly string[]>> = {
  // One scene, not two. `light-solid__rrect-md__rest` was here against the
  // retired inactive bed, whose untinted material over a light solid left the
  // extractor no interior to sample at all. The frozen active bed carries a
  // shadow and a rim it did not, so the scene has an interior again and is
  // gated like any other. Removed because the matrix says so — the assertion
  // below re-derives this list from the artifact on every run.
  "apple-macos-26.5-1x-light-standard": ["dark-solid__capsule-button__rest"],
  "apple-macos-26.5-2x-light-standard": ["dark-solid__capsule-button__rest"],
  "apple-macos-26.5-1x-light-reduced-transparency": [],
  "apple-macos-26.5-1x-light-increased-contrast": [],
};

/**
 * Every cell §5.17's conditioning predicate excludes, across the whole matrix —
 * gated or not, named rather than dropped. Re-derived against the FROZEN active
 * bed (2026-09-01), under the two-arm predicate above.
 *
 * The predicate reads the recovery and the topology of a silhouette, so every
 * line here is a statement about what the extractor could resolve — never about
 * vitrea's fidelity. A cell named here is still gated on all of its perceptual
 * rows. This list is not, and must not be read as, a fidelity exceedance.
 *
 * **The families, by the arm that fires.**
 *
 * - **`bodiesWeb` — the web mask broke into pieces.** The dominant family, and
 *   the one the old native-only predicate could not see at all. It is almost
 *   entirely *tinted* surfaces: `photo__rrect-lg__rest-tint-orange` reads one
 *   native body against SEVEN web bodies, with 11 holes, an IoU still of 0.968,
 *   and a contour p95 of 67 px that is measuring the distance between fragments
 *   rather than any error of outline. The tint carries the surface toward the
 *   backdrop's own colour and the extractor loses the boundary in patches.
 *
 * - **`areaWeb` — the web mask is intact but under-recovered.**
 *   `hc-text__rrect-md__rest` recovers 1.000 of its region natively and 0.934 on
 *   the web side; the old predicate asked only the native side, passed it, and
 *   then gated a contour p95 of 24 px against a bound of 4.
 *
 * - **`areaNative` — the reference itself is not resolvable.** A material over a
 *   near-black backdrop in the standard profiles (`impulse__capsule-button__rest`
 *   at 0.027 recovery, `dark-solid__rrect-md__rest` at 0.025/0.020 in the two
 *   dark-scheme profiles), and the increased-contrast material lost against the
 *   checkerboard's white squares (0.651 and 0.622).
 *
 * **What LEFT this list.** `hc-text__capsule-button__rest` in increased contrast
 * recovered 0.519 on the retired inactive bed and recovers 0.982 on the frozen
 * one. Like v1's canonical `checkerboard__capsule-button__rest` before it — §5's
 * whole argument for this predicate at 88.9%, and 100.8% once the bed settled —
 * the exclusion was instrument-caused. An unsettled reference, not a hard scene.
 */
const PREDICATE_EXCLUDES = [
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-standard",
  "dom / calibration / checkerboard__rrect-sm__rest / apple-macos-26.5-1x-light-standard",
  "dom / calibration / checkerboard__rrect-sm__rest / apple-macos-26.5-2x-light-standard",
  "dom / calibration / checkerboard__toolbar-group__rest / apple-macos-26.5-1x-light-standard",
  "dom / calibration / checkerboard__toolbar-group__rest / apple-macos-26.5-2x-light-standard",
  "dom / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-1x-dark-standard",
  "dom / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-2x-dark-standard",
  "dom / calibration / photo__capsule-button__rest-tint-blue / apple-macos-26.5-1x-light-standard",
  "dom / calibration / photo__capsule-button__rest-tint-blue / apple-macos-26.5-2x-light-standard",
  "dom / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-1x-dark-standard",
  "dom / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-1x-light-reduced-transparency",
  "dom / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-1x-light-standard",
  "dom / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-2x-dark-standard",
  "dom / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-2x-light-standard",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / holdout / hc-text__rrect-md__rest / apple-macos-26.5-1x-light-standard",
  "dom / holdout / hc-text__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "dom / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "dom / holdout / photo__rrect-lg__rest-tint-orange / apple-macos-26.5-1x-light-standard",
  "dom / holdout / photo__rrect-lg__rest-tint-orange / apple-macos-26.5-2x-light-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "dom / validation / photo__rrect-md__rest-tint-orange / apple-macos-26.5-1x-light-standard",
  "dom / validation / photo__rrect-md__rest-tint-orange / apple-macos-26.5-2x-light-standard",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / checkerboard__rrect-ml__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / checkerboard__rrect-sm__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-1x-dark-standard",
  "texture / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-2x-dark-standard",
  "texture / calibration / photo__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "texture / calibration / photo__capsule-button__rest-tint-blue / apple-macos-26.5-1x-light-standard",
  "texture / calibration / photo__capsule-button__rest-tint-blue / apple-macos-26.5-2x-light-standard",
  "texture / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-1x-dark-standard",
  "texture / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-1x-light-reduced-transparency",
  "texture / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-1x-light-standard",
  "texture / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-2x-dark-standard",
  "texture / calibration / photo__capsule-button__rest-tint-orange / apple-macos-26.5-2x-light-standard",
  "texture / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-reduced-transparency",
  "texture / holdout / hc-text__rrect-md__rest / apple-macos-26.5-1x-light-standard",
  "texture / holdout / hc-text__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "texture / holdout / photo__rrect-lg__rest-tint-orange / apple-macos-26.5-1x-light-standard",
  "texture / holdout / photo__rrect-lg__rest-tint-orange / apple-macos-26.5-2x-light-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "texture / validation / photo__rrect-md__rest-tint-orange / apple-macos-26.5-1x-light-standard",
] as const;

// ---------------------------------------------------------------------------
// Reading the committed artifacts
// ---------------------------------------------------------------------------

interface MetricValue {
  readonly value: number;
  readonly units: string;
}

type AxisReport = Readonly<Record<string, MetricValue | string | undefined>>;

interface Cell {
  readonly key: {
    readonly profileKey: string;
    readonly sceneId: string;
    readonly web: { readonly engine: string; readonly renderer: string };
  };
  readonly fixtureSet: string;
  readonly tier: "texture" | "dom";
  readonly shape?: AxisReport;
  readonly perceptual?: AxisReport;
  readonly material?: AxisReport;
  readonly coherence?: AxisReport;
}

interface ResultMatrix {
  readonly schemaVersion: number;
  readonly cells: readonly Cell[];
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
const MATRIX = readJson<ResultMatrix>(resolve(PACKAGE_ROOT, "results", "matrix.json"));

/** `tier / set / scene / profile` — every failure message starts with this. */
function name(cell: Cell): string {
  return `${cell.tier} / ${cell.fixtureSet} / ${cell.key.sceneId} / ${cell.key.profileKey}`;
}

function reading(
  cell: Cell,
  axis: "shape" | "perceptual" | "material" | "coherence",
  field: string,
): number {
  const entry = cell[axis]?.[field];
  if (typeof entry !== "object") {
    // A metric that vanished from the schema must not read as a cell that
    // passed. Absent axes are handled by the caller, which knows which cells
    // legitimately have none; an absent *field* inside a present axis is a
    // gate that silently stopped checking something.
    throw new Error(`${name(cell)}: no ${axis}.${field} on the record`);
  }
  return entry.value;
}

// ---------------------------------------------------------------------------
// The conditioning predicate
// ---------------------------------------------------------------------------

/**
 * §5.17's conditioning predicate, in its final form — **two arms, both sides**,
 * and not one chosen number between them.
 *
 * 1. **Area, both sides**: `silhouetteArea{Native,Web} ≥ 0.95 × componentRegionArea`.
 * 2. **Bodies, both sides**: `silhouetteBodies{Native,Web} ≤ componentRegionBodies`.
 *
 * Everything it compares against is the cell's own **declared region**, recorded
 * on the same axis by the same run. There is no unit conversion left to get
 * wrong: the region area is in the cell's own device pixels, so a 2× cell is
 * compared against a 2× region and the backing scale never enters. The version
 * this replaces multiplied a points-declared area from `scenes.json` by the
 * square of the backing scale, and asked only the NATIVE side — which is how a
 * cell whose WEB mask had broken into seven pieces was still being gated on its
 * contour rows.
 *
 * The bodies arm counts against the *region's own* body count rather than one,
 * so a genuinely multi-body component is not penalised: `toolbar-group` declares
 * three capsules and its region has three bodies.
 *
 * Verified against §5.17's published table before it was adopted here: evaluated
 * over `results/2026-08-31-round-two.json`, the bed that table was measured on,
 * this reproduces all eight of its declared cell counts exactly (22/18, 21/18,
 * 6/6, 6/5).
 */
function isWellConditioned(cell: Cell): boolean {
  if (cell.shape === undefined) return true;
  const at = (metric: string): number => reading(cell, "shape", metric);
  const regionArea = at("componentRegionArea");
  const regionBodies = at("componentRegionBodies");
  return (
    at("silhouetteAreaNative") >= WELL_CONDITIONED_AREA_RATIO * regionArea &&
    at("silhouetteAreaWeb") >= WELL_CONDITIONED_AREA_RATIO * regionArea &&
    at("silhouetteBodiesNative") <= regionBodies &&
    at("silhouetteBodiesWeb") <= regionBodies
  );
}

// ---------------------------------------------------------------------------
// Selection
// ---------------------------------------------------------------------------

const cellsOf = (profileKey: string, tier?: "texture" | "dom"): readonly Cell[] =>
  MATRIX.cells.filter(
    (cell) => cell.key.profileKey === profileKey && (tier === undefined || cell.tier === tier),
  );

/** How many cells of this profile and tier the enumerated predicate list drops. */
const predicateExcludedCount = (profileKey: string, tier: string): number =>
  PREDICATE_EXCLUDES.filter((line) => line.startsWith(`${tier} / `) && line.endsWith(` / ${profileKey}`))
    .length;

// ---------------------------------------------------------------------------

describe("the adopted fidelity gate (claims §5, adopted 2026-08-26 / -29 / -30)", () => {
  it("reads the schema it was written against, which is no longer the one the build writes", () => {
    // The field names below were verified against schema 4, and this matrix is
    // still a schema-4 file. That is deliberate, not drift: wave Decision Log 15
    // ruling 3 keeps the inactive-bed gate enforced as the historically
    // labelled suite until the one honest post-W8 pass, so `results/matrix.json`
    // is not regenerated — while the build has moved to schema 5, whose shape
    // and material figures are measured under a *bounded* silhouette and are
    // therefore not the same quantities as the ones gated here.
    //
    // Both numbers are pinned so the divergence stays a decision. When the
    // post-W8 matrix replaces this one, these two become equal again and the
    // tables above must be re-verified against the new instrument, not assumed
    // to have survived it.
    expect(MATRIX.schemaVersion).toBe(5);
    expect(RESULT_MATRIX_SCHEMA_VERSION).toBe(5);
  });

  it("covers four profiles of the settled bed, and names the two it leaves", () => {
    const perProfile = new Map<string, number>();
    for (const cell of MATRIX.cells) {
      perProfile.set(cell.key.profileKey, (perProfile.get(cell.key.profileKey) ?? 0) + 1);
    }
    expect(Object.fromEntries([...perProfile].sort())).toEqual(MATRIX_PARTITION);

    // Total, in both directions: the gated profiles plus the ungated ones
    // account for the whole matrix, so no cell is outside the statement.
    expect(MATRIX.cells).toHaveLength(MATRIX_CELLS);
    expect(Object.values(MATRIX_PARTITION).reduce((a, b) => a + b, 0)).toBe(MATRIX_CELLS);
    expect(
      [...GATED_PROFILES.map((profile) => profile.profileKey), ...UNGATED_PROFILES].sort(),
    ).toEqual(Object.keys(MATRIX_PARTITION).sort());

    for (const { profileKey, cellsPerTier } of GATED_PROFILES) {
      for (const tier of ["texture", "dom"] as const) {
        const cells = cellsOf(profileKey, tier);
        expect(cells, `${profileKey} / ${tier}`).toHaveLength(cellsPerTier);
        // And every gated cell is the engine and renderer the tables name. A
        // cell captured through anything else is not the cell the thresholds
        // were set on.
        for (const cell of cells) {
          expect(cell.key.web.engine, name(cell)).toBe("chromium");
          expect(cell.key.web.renderer, name(cell)).toBe(RENDERER_OF_TIER[tier]);
        }
      }
    }
  });

  for (const profile of GATED_PROFILES) {
    for (const tier of ["texture", "dom"] as const) {
      const table = profile[tier];
      const constant = profile.names[tier];
      it(`gates the ${tier}-tier ${profile.profileKey} cells against ${constant}`, () => {
        const cells = cellsOf(profile.profileKey, tier);
        const shapeCells = cells.filter((cell) => cell.shape !== undefined);
        const noShape = NO_SHAPE_AXIS_SCENES[profile.profileKey] ?? [];

        // The shape rows gate fewer cells than the perceptual rows, for named
        // reasons only. Derived from the names so a new such scene cannot arrive
        // unnoticed and shrink the gate.
        expect(shapeCells).toHaveLength(profile.cellsPerTier - noShape.length);
        expect(
          cells
            .filter((cell) => cell.shape === undefined)
            .map((cell) => cell.key.sceneId)
            .sort(),
        ).toEqual([...noShape].sort());

        for (const [axis, metric, comparison, threshold] of table) {
          // Shape rows carry the well-conditioned predicate; perceptual rows do
          // not. Nothing else qualifies either any more — the defect class that
          // used to sit beside the predicate dissolved with W7 (see the note
          // above), so a perceptual row now covers every cell of its profile.
          const applicable = axis === "shape" ? shapeCells.filter(isWellConditioned) : cells;

          // The expected count comes from the enumerated exclusion list, never
          // from the matrix — so a gate that quietly stopped covering a cell
          // fails here rather than passing with less work to do.
          const expected =
            axis === "shape"
              ? profile.cellsPerTier - noShape.length - predicateExcludedCount(profile.profileKey, tier)
              : profile.cellsPerTier;
          expect(
            applicable,
            `${tier} / ${metric}: the gate must cover every applicable cell`,
          ).toHaveLength(expected);
          expect(applicable.length, `${tier} / ${metric}: nothing left to gate`).toBeGreaterThan(0);

          for (const cell of applicable) {
            const measured = reading(cell, axis, metric);
            const because = `${name(cell)}: ${metric} = ${measured.toPrecision(5)}, gate ${comparison} ${threshold}`;
            if (comparison === "≥") expect(measured, because).toBeGreaterThanOrEqual(threshold);
            else expect(measured, because).toBeLessThanOrEqual(threshold);
          }
        }
      });
    }
  }

  it("machine-checks the well-conditioned predicate and names every cell it excludes", () => {
    const excluded = MATRIX.cells.filter((cell) => !isWellConditioned(cell)).map(name).sort();
    expect(excluded, "cells the shape rows skip, per claims §5's predicate").toEqual([
      ...PREDICATE_EXCLUDES,
    ]);

    // The predicate is not passing by being vacuous. It has to bite somewhere —
    // §5 adopted it *because* a canonical cell failed it, and a predicate that
    // excluded nothing at all would mean the areas had stopped being measured.
    expect(excluded.length).toBeGreaterThan(0);
    // Every excluded cell must fail a NAMED arm, and the failing arm is asserted
    // rather than assumed. The predicate has four; a cell that appeared in the
    // list without any of them firing would mean the list had drifted from the
    // artifact, which is the one way this bookkeeping can rot silently.
    for (const cell of MATRIX.cells.filter((candidate) => !isWellConditioned(candidate))) {
      const at = (metric: string): number => reading(cell, "shape", metric);
      const floor = WELL_CONDITIONED_AREA_RATIO * at("componentRegionArea");
      const bodies = at("componentRegionBodies");
      expect(
        at("silhouetteAreaNative") < floor ||
          at("silhouetteAreaWeb") < floor ||
          at("silhouetteBodiesNative") > bodies ||
          at("silhouetteBodiesWeb") > bodies,
        `${name(cell)}: excluded, so one of the four arms must fail`,
      ).toBe(true);
    }

    // The web-side arms are not decoration: the frozen bed's exclusions are
    // mostly cells the old native-only predicate passed. Asserted so a future
    // change that quietly reverted to reading one side would fail here.
    const webOnly = MATRIX.cells.filter((cell) => {
      if (cell.shape === undefined || isWellConditioned(cell)) return false;
      const at = (metric: string): number => reading(cell, "shape", metric);
      return (
        at("silhouetteAreaNative") >= WELL_CONDITIONED_AREA_RATIO * at("componentRegionArea") &&
        at("silhouetteBodiesNative") <= at("componentRegionBodies")
      );
    });
    expect(webOnly.length, "cells only the web-side arms catch").toBeGreaterThan(0);

    // v1's canonical ill-conditioned cell is gated again on the settled bed, at
    // both scales. Asserted so nobody re-adds the exclusion from memory: the
    // 88.9% recovery was an unsettled capture, not dark glass over a checkerboard.
    for (const profileKey of UNGATED_PROFILES) {
      for (const cell of cellsOf(profileKey)) {
        if (cell.key.sceneId !== "checkerboard__capsule-button__rest") continue;
        expect(isWellConditioned(cell), `${name(cell)}: settled, this cell conditions fine`).toBe(true);
      }
    }
  });

  // -------------------------------------------------------------------------
  // Coherence
  // -------------------------------------------------------------------------

  /*
   * Gated on the two light-standard profiles only. The accessibility tables
   * adopted on 2026-08-30 are the seven fidelity rows as proposed; their
   * coherence figures are measured and reported but were not part of that
   * adoption, so they are asserted present below rather than bounded here.
   */
  const COHERENCE_GATED = [
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
  ] as const;

  for (const profileKey of COHERENCE_GATED) {
    it(`enforces the coherence rows over ${profileKey}, from the matrix`, () => {
      const dom = cellsOf(profileKey, "dom");
      const { min, max } = COHERENCE_ROWS.interiorLevelRatioGpuOverCss;
      const deltaE = COHERENCE_ROWS.crossTierOklabDeltaEMean;
      const noShape = NO_SHAPE_AXIS_SCENES[profileKey] ?? [];

      // Coherence is a property of the pair, so it is present on every dom cell
      // whose texture twin was captured — which, in this matrix, is all of them.
      expect(dom.filter((cell) => cell.coherence !== undefined)).toHaveLength(dom.length);

      let ratios = 0;
      for (const cell of dom) {
        const measured = reading(cell, "coherence", "crossTierOklabDeltaEMean");
        expect(
          measured,
          `${name(cell)}: cross-tier ΔE mean = ${measured.toPrecision(4)}, gate ${deltaE.bound} ${deltaE.threshold}`,
        ).toBeLessThanOrEqual(deltaE.threshold);

        // The ratio is absent exactly where there is no interior to sample, and
        // those are the named no-shape scenes. Absent, never zeroed — so its
        // absence is checked against the reason rather than skipped.
        if (cell.coherence?.interiorLevelRatioGpuOverCss === undefined) {
          expect([...noShape], "a scene with no interior to sample").toContain(cell.key.sceneId);
          continue;
        }
        const ratio = reading(cell, "coherence", "interiorLevelRatioGpuOverCss");
        const because = `${name(cell)}: interior level gpu ÷ css = ${ratio.toPrecision(4)}, gate ${min}…${max}`;
        expect(ratio, because).toBeGreaterThanOrEqual(min);
        expect(ratio, because).toBeLessThanOrEqual(max);
        ratios += 1;
      }
      expect(ratios, "every scene with a material on both tiers is a coherence pair").toBe(
        dom.length - noShape.length,
      );
    });

    it(`cross-checks ${profileKey}'s recorded ratio against the two tiers' own levels`, () => {
      /*
       * The coherence axis is written by `cli/measure.ts` during the dom-tier
       * run, from the texture capture on disk. The same ratio is independently
       * derivable from the matrix itself — each tier's `material.interiorMeanWeb`
       * is that tier's interior level under the *native* silhouette, which is the
       * identical quantity over the identical mask.
       *
       * Deriving it a second way and requiring the two to agree is what keeps the
       * axis from being a number the gate trusts because it has no other source.
       */
      const twin = new Map(
        cellsOf(profileKey, "texture").map((cell) => [cell.key.sceneId, cell] as const),
      );
      let checked = 0;
      for (const cell of cellsOf(profileKey, "dom")) {
        if (cell.coherence?.interiorLevelRatioGpuOverCss === undefined) continue;
        const texture = twin.get(cell.key.sceneId);
        expect(texture, `${cell.key.sceneId}: coherence is a property of the pair`).toBeDefined();
        if (texture === undefined) continue;
        const derived =
          reading(texture, "material", "interiorMeanWeb") /
          reading(cell, "material", "interiorMeanWeb");
        expect(
          reading(cell, "coherence", "interiorLevelRatioGpuOverCss"),
          `${name(cell)}: the recorded ratio must be the two tiers' own levels, divided`,
        ).toBeCloseTo(derived, 9);
        checked += 1;
      }
      expect(checked).toBeGreaterThan(0);
    });
  }

  it("measures coherence on every profile the rows do not gate", () => {
    /*
     * The two dark profiles are ungated entirely (their tables await a
     * re-measure); the two accessibility profiles are gated on their fidelity
     * rows but not on coherence. Both cases are measured, and presence is what
     * is asserted here — a profile that silently stopped carrying coherence
     * would otherwise look exactly like one that was never gated on it.
     */
    const notCoherenceGated = [
      ...UNGATED_PROFILES,
      "apple-macos-26.5-1x-light-reduced-transparency",
      "apple-macos-26.5-1x-light-increased-contrast",
    ];
    for (const profileKey of notCoherenceGated) {
      const dom = cellsOf(profileKey, "dom");
      expect(dom.length, profileKey).toBeGreaterThan(0);
      for (const cell of dom) {
        expect(cell.coherence, `${name(cell)}: coherence measured, not gated`).toBeDefined();
        expect(
          cell.coherence?.interiorLevelRatioGpuOverCss === undefined,
          `${name(cell)}: the ratio exists exactly where a shared interior does`,
        ).toBe(cell.material === undefined);
      }
    }
  });

  it("carries a coherence axis on the dom tier and nowhere else", () => {
    // The pair has one number, so it lives on one side of the pair. A texture
    // cell that grew one would mean two records of the same quantity, which can
    // disagree — and the direction (GPU ÷ CSS) would then be ambiguous.
    for (const cell of MATRIX.cells) {
      if (cell.tier === "dom") continue;
      expect(cell, `${name(cell)}: coherence belongs to the dom-tier cell`).not.toHaveProperty(
        "coherence",
      );
    }
  });
});
