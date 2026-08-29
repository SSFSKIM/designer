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
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

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
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 4.0],
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

/** Dom tier, `apple-macos-26.5-2x-light-standard`, Chromium, `renderer: css`. */
const DOM_TIER_2X_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 4.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 8.0],
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
 */
const TEXTURE_TIER_REDUCED_TRANSPARENCY: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.87],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 1.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 3.5],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.96],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.04],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.08],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.10],
];

const DOM_TIER_REDUCED_TRANSPARENCY: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.89],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 1.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 3.5],
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
 * Its shape rows also gate the fewest cells of any adopted table: three of its
 * eight scenes per tier fail the well-conditioned predicate, because the
 * brightened material is lost over the checkerboard's white squares. Those are
 * named in `PREDICATE_EXCLUDES` like every other excluded cell.
 */
const TEXTURE_TIER_INCREASED_CONTRAST: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 1.8],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 3.2],
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

// ---------------------------------------------------------------------------
// The defect-class exclusion — a known renderer gap, enumerated
// ---------------------------------------------------------------------------

const KNOWN_GAP_REASON =
  "Apple's material continuously adapts its appearance to backdrop luminance — a " +
  "light-scheme capsule over a black or near-black backdrop settles to near-black — " +
  "and vitrea has no such axis: its material profiles are discrete per colour scheme. " +
  "Over these two extreme backdrops the reference all but disappears while vitrea " +
  "keeps drawing a light capsule, so the perceptual rows measure the missing axis " +
  "rather than a tuning error. Nothing here is loosened: the bound is unchanged and " +
  "the cell is named.";

const KNOWN_GAP_TRACKING = "wave child W7 (backdrop tone adaptation), post-v1 wave spec";

/**
 * One entry per gated row that a known renderer gap — not a tuning miss and not
 * an instrument artefact — currently fails.
 *
 * **This is a second, distinct exclusion class**, and the distinction is the
 * point. `PREDICATE_EXCLUDES` below drops shape rows whose *extractor* could not
 * find the component: the number there describes the instrument, so gating it
 * would gate the instrument. These entries drop rows the instrument measured
 * perfectly well; what they exclude is a defect vitrea is known to have and has
 * a chartered fix for. Conflating the two would let a real gap hide inside a
 * measurement caveat.
 *
 * Four properties are enforced below rather than promised:
 *
 *   - **Every entry must still fail.** An entry whose row now passes is a stale
 *     exclusion, and the test says so by name. That is what makes W7's landing
 *     force its own cleanup: when the gap closes, these rows pass, this file
 *     fails, and the fix is to DELETE the entries — at which point the adopted
 *     bounds re-arm unchanged, because nothing about them was ever edited.
 *   - **`measured` must match the matrix.** The figure quoted here is the one a
 *     reader will cite; if it drifts from the cell, the citation is fiction.
 *   - **Every entry carries a reason and a tracking pointer**, both non-empty.
 *     An exclusion nobody owns is a silently lowered bar.
 *   - **The class cannot quietly grow.** Its scope — which profiles, scenes and
 *     axes it may touch — is asserted, so a future failure elsewhere cannot be
 *     resolved by appending a row here.
 */
interface KnownGapExclusion {
  readonly profileKey: string;
  readonly sceneId: string;
  readonly tier: "texture" | "dom";
  readonly axis: "shape" | "perceptual";
  readonly metric: string;
  /** The figure as measured on the committed matrix, for citation. */
  readonly measured: number;
  /** The adopted bound this row fails, restated so the entry reads alone. */
  readonly bound: string;
  readonly reason: string;
  readonly tracking: string;
}

const KNOWN_RENDERER_GAP_EXCLUSIONS: readonly KnownGapExclusion[] = [
  {
    profileKey: "apple-macos-26.5-1x-light-standard",
    sceneId: "dark-solid__capsule-button__rest",
    tier: "texture",
    axis: "perceptual",
    metric: "oklabDeltaEP95",
    measured: 0.6272,
    bound: "≤ 0.17",
    reason: KNOWN_GAP_REASON,
    tracking: KNOWN_GAP_TRACKING,
  },
  {
    profileKey: "apple-macos-26.5-1x-light-standard",
    sceneId: "impulse__capsule-button__rest",
    tier: "texture",
    axis: "perceptual",
    metric: "oklabDeltaEP95",
    measured: 0.6633,
    bound: "≤ 0.17",
    reason: KNOWN_GAP_REASON,
    tracking: KNOWN_GAP_TRACKING,
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    sceneId: "dark-solid__capsule-button__rest",
    tier: "texture",
    axis: "perceptual",
    metric: "ssimMean",
    measured: 0.9259,
    bound: "≥ 0.93",
    reason: KNOWN_GAP_REASON,
    tracking: KNOWN_GAP_TRACKING,
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    sceneId: "impulse__capsule-button__rest",
    tier: "texture",
    axis: "perceptual",
    metric: "ssimMean",
    measured: 0.92,
    bound: "≥ 0.93",
    reason: KNOWN_GAP_REASON,
    tracking: KNOWN_GAP_TRACKING,
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    sceneId: "dark-solid__capsule-button__rest",
    tier: "texture",
    axis: "perceptual",
    metric: "oklabDeltaEP95",
    measured: 0.6272,
    bound: "≤ 0.17",
    reason: KNOWN_GAP_REASON,
    tracking: KNOWN_GAP_TRACKING,
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    sceneId: "impulse__capsule-button__rest",
    tier: "texture",
    axis: "perceptual",
    metric: "oklabDeltaEP95",
    measured: 0.6647,
    bound: "≤ 0.17",
    reason: KNOWN_GAP_REASON,
    tracking: KNOWN_GAP_TRACKING,
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    sceneId: "impulse__capsule-button__rest",
    tier: "dom",
    axis: "perceptual",
    metric: "ssimMean",
    measured: 0.9191,
    bound: "≥ 0.92",
    reason: KNOWN_GAP_REASON,
    tracking: KNOWN_GAP_TRACKING,
  },
];

/** The only scenes and profiles the defect class is allowed to touch. */
const KNOWN_GAP_SCOPE = {
  scenes: ["dark-solid__capsule-button__rest", "impulse__capsule-button__rest"],
  profileKeys: ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard"],
  axes: ["perceptual"],
} as const;

function isKnownGap(cell: Cell, axis: string, metric: string): boolean {
  return KNOWN_RENDERER_GAP_EXCLUSIONS.some(
    (entry) =>
      entry.profileKey === cell.key.profileKey &&
      entry.sceneId === cell.key.sceneId &&
      entry.tier === cell.tier &&
      entry.axis === axis &&
      entry.metric === metric,
  );
}

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
    cellsPerTier: 24,
    texture: TEXTURE_TIER_LIGHT,
    dom: DOM_TIER_LIGHT,
    names: { texture: "TEXTURE_TIER_LIGHT", dom: "DOM_TIER_LIGHT" },
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    cellsPerTier: 24,
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
    cellsPerTier: 8,
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
 */
const MATRIX_PARTITION: Readonly<Record<string, number>> = {
  "apple-macos-26.5-1x-dark-standard": 20,
  "apple-macos-26.5-1x-light-increased-contrast": 16,
  "apple-macos-26.5-1x-light-reduced-transparency": 16,
  "apple-macos-26.5-1x-light-standard": 48,
  "apple-macos-26.5-2x-dark-standard": 20,
  "apple-macos-26.5-2x-light-standard": 48,
};

const MATRIX_CELLS = 168;

/**
 * Scenes that carry no shape and no material axis, per profile — so the shape
 * rows have nothing to gate there.
 *
 * Not a fault and not a gap in the gate: over a solid backdrop of the material's
 * own tone the reference sits within the extractor's 0.02 threshold of its
 * background, so the native silhouette is empty and `cli/measure.ts` records the
 * cell with its perceptual axis alone rather than inventing a shape. On the
 * settled bed `dark-solid__capsule-button__rest` joined this list in the light
 * profiles: the reference capsule over a near-black backdrop now settles to
 * that backdrop, which is the same tone adaptation the defect class above is
 * about, seen through the extractor instead of through ΔE.
 */
const NO_SHAPE_AXIS_SCENES: Readonly<Record<string, readonly string[]>> = {
  "apple-macos-26.5-1x-light-standard": [
    "dark-solid__capsule-button__rest",
    "light-solid__rrect-md__rest",
  ],
  "apple-macos-26.5-2x-light-standard": [
    "dark-solid__capsule-button__rest",
    "light-solid__rrect-md__rest",
  ],
  "apple-macos-26.5-1x-light-reduced-transparency": [],
  "apple-macos-26.5-1x-light-increased-contrast": [],
};

/**
 * Every cell the well-conditioned predicate excludes, across the whole matrix —
 * gated or not, named rather than dropped.
 *
 * Three families, one mechanism: the extractor cannot separate the material from
 * its backdrop, so the figure describes the instrument. In the
 * **increased-contrast** profile the brightened material is lost over the
 * checkerboard's white squares (and over its hc-text holdout scene). In all four
 * **standard** profiles the `impulse` capsule is lost over a black backdrop — new
 * on the settled bed, and the extractor's view of the same tone adaptation W7
 * exists to fix.
 *
 * What is NOT here any more is v1's canonical example. The 1× dark
 * `checkerboard__capsule-button__rest` cell was §5's whole argument for this
 * predicate at 88.9% recovery; on the settled bed it recovers 100.8% and is
 * gated like any other cell. The v1 exclusion was instrument-caused — an
 * unsettled capture, not a property of dark glass over a checkerboard.
 */
const PREDICATE_EXCLUDES = [
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-light-standard",
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

/** A rounded rect; a capsule is one whose radius is half its short side. */
interface ShapeSpec {
  readonly kind: "capsule" | "rrect";
  readonly size: readonly [number, number];
  readonly radius?: number;
  readonly offset?: readonly [number, number];
}
interface GroupSpec {
  readonly kind: "group";
  readonly items: readonly ShapeSpec[];
  readonly spacing: number;
}
interface StackSpec {
  readonly kind: "stack";
  readonly base: ShapeSpec;
  readonly over: ShapeSpec;
}
type ComponentSpec = ShapeSpec | GroupSpec | StackSpec;

interface SceneMatrix {
  readonly components: Readonly<Record<string, ComponentSpec>>;
  readonly scenes: readonly { readonly id: string; readonly component: string }[];
}

const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

const MATRIX = readJson<ResultMatrix>(resolve(PACKAGE_ROOT, "results", "matrix.json"));
const SCENES = readJson<SceneMatrix>(resolve(REPO_ROOT, "apps", "reference-apple", "scenes.json"));

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
// The declared component area — the predicate's right-hand side
// ---------------------------------------------------------------------------

/** A rectangle less its four corner offcuts, each of which removes r² − πr²/4. */
function shapeArea(spec: ShapeSpec): number {
  const [width, height] = spec.size;
  const radius = spec.kind === "capsule" ? Math.min(width, height) / 2 : (spec.radius ?? 0);
  return width * height - (4 - Math.PI) * radius * radius;
}

function declaredComponentArea(componentId: string): number {
  const spec = SCENES.components[componentId];
  if (spec === undefined) throw new Error(`scenes.json declares no component "${componentId}"`);

  if (spec.kind === "group") {
    /*
     * The sum of the members, unmerged. Claims §4.5 measured this: at the
     * declared spacing of 12 the reference's own silhouette is three separate
     * bodies, so a union would overstate the declared area and loosen the
     * predicate on exactly the cell it was measured on.
     */
    return spec.items.reduce((sum, item) => sum + shapeArea(item), 0);
  }

  if (spec.kind === "stack") {
    // The overlay sits wholly inside the base, so the union IS the base. Checked
    // rather than assumed: an overlay that escaped would make this an undercount,
    // and an undercount loosens the predicate instead of failing it.
    const [baseWidth, baseHeight] = spec.base.size;
    const [overWidth, overHeight] = spec.over.size;
    const [offsetX, offsetY] = spec.over.offset ?? [0, 0];
    const inset =
      spec.base.kind === "capsule"
        ? Math.min(baseWidth, baseHeight) / 2
        : (spec.base.radius ?? 0);
    const contained =
      Math.abs(offsetX) + overWidth / 2 <= baseWidth / 2 - inset &&
      Math.abs(offsetY) + overHeight / 2 <= baseHeight / 2 - inset;
    if (!contained) {
      throw new Error(
        `"${componentId}"'s overlay is no longer inside its base, so the declared ` +
          `area is a union this test does not compute. Compute it, or split the scene.`,
      );
    }
    return shapeArea(spec.base);
  }

  return shapeArea(spec);
}

const COMPONENT_OF_SCENE = new Map(SCENES.scenes.map((scene) => [scene.id, scene.component]));

function declaredAreaOf(cell: Cell): number {
  const componentId = COMPONENT_OF_SCENE.get(cell.key.sceneId);
  if (componentId === undefined) {
    throw new Error(`${name(cell)}: scenes.json declares no such scene`);
  }
  return declaredComponentArea(componentId);
}

/**
 * §5's predicate, evaluated — in **declared units**.
 *
 * `scenes.json` declares component sizes in points, and a 2× cell's silhouette
 * is measured in device pixels, so the declared area is scaled by the square of
 * the profile's backing scale before the comparison. Without that a 2× cell
 * would clear a 1× area threshold roughly four times over and the predicate
 * would stop biting at exactly the scale where the extractor is most likely to
 * be doing something interesting.
 */
function backingScaleOf(profileKey: string): number {
  const scale = /-(\d+)x-/.exec(profileKey)?.[1];
  if (scale === undefined) throw new Error(`${profileKey}: no backing scale in the profile key`);
  return Number(scale);
}

function isWellConditioned(cell: Cell): boolean {
  if (cell.shape === undefined) return true;
  const scale = backingScaleOf(cell.key.profileKey);
  return (
    reading(cell, "shape", "silhouetteAreaNative") >=
    WELL_CONDITIONED_AREA_RATIO * declaredAreaOf(cell) * scale * scale
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

/** How many cells of this profile, tier and metric the defect class drops. */
const knownGapCount = (profileKey: string, tier: string, metric: string): number =>
  KNOWN_RENDERER_GAP_EXCLUSIONS.filter(
    (entry) => entry.profileKey === profileKey && entry.tier === tier && entry.metric === metric,
  ).length;

// ---------------------------------------------------------------------------

describe("the adopted fidelity gate (claims §5, adopted 2026-08-26 / -29 / -30)", () => {
  it("reads the schema it was written against", () => {
    // The field names below were verified against schema 4. A schema bump is a
    // reason to re-verify them, not to trust that they survived.
    expect(MATRIX.schemaVersion).toBe(4);
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
          // not. Both carry the defect class, which is enumerated per metric.
          const applicable = (axis === "shape" ? shapeCells.filter(isWellConditioned) : cells).filter(
            (cell) => !isKnownGap(cell, axis, metric),
          );

          // The expected count comes from the enumerated exclusion lists, never
          // from the matrix — so a gate that quietly stopped covering a cell
          // fails here rather than passing with less work to do.
          const expected =
            axis === "shape"
              ? profile.cellsPerTier - noShape.length - predicateExcludedCount(profile.profileKey, tier)
              : profile.cellsPerTier - knownGapCount(profile.profileKey, tier, metric);
          expect(
            applicable,
            `${tier} / ${metric}: the gate must cover every applicable cell`,
          ).toHaveLength(expected - (axis === "shape" ? knownGapCount(profile.profileKey, tier, metric) : 0));
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

  // -------------------------------------------------------------------------
  // The defect class, held to its own contract
  // -------------------------------------------------------------------------

  describe("the known-renderer-gap exclusions", () => {
    it("still fail their adopted bound, every one of them", () => {
      /*
       * The mechanism that makes W7 clean up after itself. When the adaptation
       * axis lands, these rows pass; this test then fails and names the entries,
       * and the fix is to DELETE them. The adopted bounds re-arm unchanged at
       * that moment because nothing about them was ever edited to accommodate
       * the gap — the rows were skipped, not loosened.
       */
      const stale: string[] = [];
      for (const entry of KNOWN_RENDERER_GAP_EXCLUSIONS) {
        const cell = MATRIX.cells.find(
          (candidate) =>
            candidate.key.profileKey === entry.profileKey &&
            candidate.key.sceneId === entry.sceneId &&
            candidate.tier === entry.tier,
        );
        expect(cell, `${entry.sceneId} / ${entry.profileKey} / ${entry.tier}: no such cell`).toBeDefined();
        if (cell === undefined) continue;

        const measured = reading(cell, entry.axis, entry.metric);
        const [comparison, threshold] = entry.bound.split(" ") as [string, string];
        const passes =
          comparison === "≥" ? measured >= Number(threshold) : measured <= Number(threshold);
        if (passes) {
          stale.push(
            `${name(cell)} / ${entry.metric} now reads ${measured.toPrecision(5)} and PASSES ` +
              `${entry.bound} — delete this entry from KNOWN_RENDERER_GAP_EXCLUSIONS`,
          );
        }
      }
      expect(stale, "exclusions whose gap has closed — delete them and the gate re-arms").toEqual([]);
    });

    it("quote the figure the matrix actually holds", () => {
      // The `measured` field is what a reader cites. If it drifts from the cell,
      // the citation is fiction and the claims doc inherits the fiction.
      for (const entry of KNOWN_RENDERER_GAP_EXCLUSIONS) {
        const cell = MATRIX.cells.find(
          (candidate) =>
            candidate.key.profileKey === entry.profileKey &&
            candidate.key.sceneId === entry.sceneId &&
            candidate.tier === entry.tier,
        );
        if (cell === undefined) continue;
        expect(
          reading(cell, entry.axis, entry.metric),
          `${name(cell)} / ${entry.metric}: the entry quotes ${entry.measured}`,
        ).toBeCloseTo(entry.measured, 3);
      }
    });

    it("each carry a reason and a tracking pointer", () => {
      // An exclusion nobody owns is a silently lowered bar.
      for (const entry of KNOWN_RENDERER_GAP_EXCLUSIONS) {
        const where = `${entry.sceneId} / ${entry.profileKey} / ${entry.tier} / ${entry.metric}`;
        expect(entry.reason.length, `${where}: needs a reason`).toBeGreaterThan(40);
        expect(entry.tracking, `${where}: needs a tracking pointer`).toContain("W7");
      }
    });

    it("cannot grow beyond the scope the ruling gave them", () => {
      /*
       * Decision Log 11 excluded two named scenes' perceptual rows in the two
       * light-standard profiles, and nothing else. Without this, a future
       * failure anywhere could be resolved by appending a row here, which is
       * exactly the silent loosening the labelled class exists to prevent.
       */
      for (const entry of KNOWN_RENDERER_GAP_EXCLUSIONS) {
        expect(KNOWN_GAP_SCOPE.scenes as readonly string[]).toContain(entry.sceneId);
        expect(KNOWN_GAP_SCOPE.profileKeys as readonly string[]).toContain(entry.profileKey);
        expect(KNOWN_GAP_SCOPE.axes as readonly string[]).toContain(entry.axis);
      }
      // And it is not vacuous: the class must be doing work, or it should be gone.
      expect(KNOWN_RENDERER_GAP_EXCLUSIONS.length).toBeGreaterThan(0);
    });
  });

  it("machine-checks the well-conditioned predicate and names every cell it excludes", () => {
    const excluded = MATRIX.cells.filter((cell) => !isWellConditioned(cell)).map(name).sort();
    expect(excluded, "cells the shape rows skip, per claims §5's predicate").toEqual([
      ...PREDICATE_EXCLUDES,
    ]);

    // The predicate is not passing by being vacuous. It has to bite somewhere —
    // §5 adopted it *because* a canonical cell failed it, and a predicate that
    // excluded nothing at all would mean the areas had stopped being measured.
    expect(excluded.length).toBeGreaterThan(0);
    for (const cell of MATRIX.cells.filter((candidate) => !isWellConditioned(candidate))) {
      const scale = backingScaleOf(cell.key.profileKey);
      expect(reading(cell, "shape", "silhouetteAreaNative")).toBeLessThan(
        WELL_CONDITIONED_AREA_RATIO * declaredAreaOf(cell) * scale * scale,
      );
    }

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
