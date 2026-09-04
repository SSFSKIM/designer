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
 *   - **No profile is ungated any more.** Four were when this list was written;
 *     the last two adopted 2026-09-01. `UNGATED_PROFILES` is kept empty because
 *     its emptiness is the end of that story — see its docstring.
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
 * Everything below is the **frozen active-bed** suite (2026-09-01), schema 5,
 * 230 cells. The inactive bed this replaced is preserved as
 * `results/2026-08-30-inactive-bed-matrix.json`; Decision Log 15 ruling 3 had
 * held the enforced matrix there until the one honest post-W8 pass, because
 * re-adopting a bound over a reference facet vitrea rendered as zero would have
 * certified the defect. W8 rendered the shadow, the cascade fitted against the
 * new bed, and Decision Log 22 landed the flip.
 *
 * ## The third adoption: the flip, with floors (Decision Log 22, 2026-09-01)
 *
 * Two things arrived together and they pull in opposite directions, so both are
 * stated:
 *
 *   1. **The gate got stricter.** §5.17's conditioning predicate is implemented
 *      in full — two arms, both sides — where this file had been asking only the
 *      native side against a points area scaled by the backing scale squared. It
 *      had been gating contour rows on cells whose web mask was in seven pieces.
 *      Both accessibility profiles now pass everything they claim.
 *   2. **Thirty-three rows could not be met, and were not excused.** They keep
 *      their adopted bound as a claim marked UNMET in §5.27, and CI enforces a
 *      `REGRESSION_FLOORS` entry pinned at what the bed measures. A floor is not
 *      a bound: it says "no worse than this", it cannot be satisfied by moving
 *      it, and a cell that improves past its bound passes. W9 owns removing
 *      them. See claims §5.26 for the one mechanism behind all thirty-three.
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

/**
 * ## The fourth adoption: `ssimOutside`, on every table (W14 G2, claims §5.66)
 *
 * The `// W14` row in each of the twelve tables below is X6's band-windowed
 * SSIM outside the native silhouette (claims §5.60), adopted at the outer
 * shadow's landing as X6 planned and W14 Decision Log 1 recorded. It is set
 * by this file's own rule for a `≥` row — 0.02 below the worst measurement
 * over calibration, validation and holdout on the rebuilt bed, floored to the
 * hundredth — and read from the same rows the gate covers, so it is a
 * regression guard on what the bed measures and not a claim about Apple. The
 * worst rows are `photo__rrect-lg` under increased contrast (0.717 texture /
 * 0.633 dom), `photo__toolbar-group` or `checkerboard__rrect-lg` on the
 * standard light profiles (0.868 / 0.843 at 1x, 0.890 / 0.743 at 2x), and
 * `dark-solid__rrect-md` on the dark profiles (0.859 / 0.800 at 1x, 0.890 at
 * 2x texture): the `photo` and dom-tier exteriors carry differences the
 * shadow wave did not touch (a structured backdrop's blurred light, the CSS
 * tier's box against its radius), and the un-keyed thick law over a
 * near-black backdrop is W14's own recorded gap (claims §5.65 §5). Those set
 * the bound, not the checkerboard cells whose exterior the wave closed to
 * 0.99. The bar is low by design and ratchets from here.
 */
/** Texture tier, `apple-macos-26.5-1x-light-standard`, cell as claims §1. */
const TEXTURE_TIER_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.82],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 5.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.88],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.07],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.17],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.11],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.84], // W14
];

/** Dom tier, same profile, Chromium, `renderer: css`. */
const DOM_TIER_LIGHT: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.85],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.0],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 7.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.90],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.08],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.82], // W14
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
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.87], // W14
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
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.72], // W14
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
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.84], // W14
];

const DOM_TIER_REDUCED_TRANSPARENCY: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.89],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 1.5],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 5.0],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.91],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.04],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.07],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.11],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.83], // W14
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
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.69], // W14
];

const DOM_TIER_INCREASED_CONTRAST: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU", /*       */ "≥", 0.80],
  ["shape", /*      */ "contourDistanceMean", /* */ "≤", 2.6],
  ["shape", /*      */ "contourDistanceP95", /*  */ "≤", 5.5],
  ["perceptual", /* */ "ssimMean", /*            */ "≥", 0.83],
  ["perceptual", /* */ "oklabDeltaEMean", /*     */ "≤", 0.07],
  ["perceptual", /* */ "oklabDeltaEP95", /*      */ "≤", 0.09],
  ["perceptual", /* */ "edgeWeightedMean", /*    */ "≤", 0.18],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.61], // W14
];

/**
 * The dark pair, both tiers and both scales — **adopted 2026-09-01**, the wave's
 * last gate decision and the end of `UNGATED_PROFILES`.
 *
 * Proposed in claims §5.28 against the frozen bed and adopted as proposed. §5.3's
 * reason for holding these back — no validation or holdout column to bound
 * against — expired when W1's split extension gave each profile 18 calibration,
 * 2 validation and 6 holdout cells per tier. What was left was a gate decision,
 * not a measurement, and this is it.
 *
 * **All 28 rows pass on both columns, with no floor and no exceedance.** That is
 * unusual in this file and it has a measured reason rather than a lucky one: the
 * mechanism claims §5.26 charters to W9 needs a bright, high-spatial-frequency
 * backdrop to bite, and the dark bed's backdrops do not supply one. The dark pair
 * is the cleanest pair of profiles the frozen bed measures.
 *
 * Derived by §5.15's declared margin rule — for a `≤` row the smallest half-step
 * reaching 1.4× the worst measurement (1% step for the unitless ones), for a `≥`
 * row 0.02 below the worst, floored to the hundredth. The worst is taken over
 * BOTH columns rather than holdout alone: holdout still sets the bound's honesty,
 * but a table a calibration cell violates is not enforceable, and `2x-dark`'s dom
 * contour p95 needs exactly that (2.0 on calibration against 1.0 on holdout).
 */
const TEXTURE_TIER_DARK: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU",       "≥", 0.93],
  ["shape", /*      */ "contourDistanceMean", "≤", 0.5],
  ["shape", /*      */ "contourDistanceP95",  "≤", 1.5],
  ["perceptual", /* */ "ssimMean",            "≥", 0.87],
  ["perceptual", /* */ "oklabDeltaEMean",     "≤", 0.09],
  ["perceptual", /* */ "oklabDeltaEP95",      "≤", 0.17],
  ["perceptual", /* */ "edgeWeightedMean",    "≤", 0.04],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.83], // W14
];

const DOM_TIER_DARK: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU",       "≥", 0.93],
  ["shape", /*      */ "contourDistanceMean", "≤", 0.5],
  ["shape", /*      */ "contourDistanceP95",  "≤", 1.5],
  ["perceptual", /* */ "ssimMean",            "≥", 0.83],
  ["perceptual", /* */ "oklabDeltaEMean",     "≤", 0.09],
  ["perceptual", /* */ "oklabDeltaEP95",      "≤", 0.18],
  ["perceptual", /* */ "edgeWeightedMean",    "≤", 0.05],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.78], // W14
];

/** The same pair at 2×. Contour rows are device-pixel quantities; the rest are scale-free. */
const TEXTURE_TIER_2X_DARK: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU",       "≥", 0.93],
  ["shape", /*      */ "contourDistanceMean", "≤", 1.0],
  ["shape", /*      */ "contourDistanceP95",  "≤", 1.5],
  ["perceptual", /* */ "ssimMean",            "≥", 0.88],
  ["perceptual", /* */ "oklabDeltaEMean",     "≤", 0.09],
  ["perceptual", /* */ "oklabDeltaEP95",      "≤", 0.17],
  ["perceptual", /* */ "edgeWeightedMean",    "≤", 0.04],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.86], // W14
];

const DOM_TIER_2X_DARK: readonly GateRow[] = [
  ["shape", /*      */ "silhouetteIoU",       "≥", 0.93],
  ["shape", /*      */ "contourDistanceMean", "≤", 0.5],
  ["shape", /*      */ "contourDistanceP95",  "≤", 3.0],
  ["perceptual", /* */ "ssimMean",            "≥", 0.85],
  ["perceptual", /* */ "oklabDeltaEMean",     "≤", 0.09],
  ["perceptual", /* */ "oklabDeltaEP95",      "≤", 0.19],
  ["perceptual", /* */ "edgeWeightedMean",    "≤", 0.05],
  ["perceptual", /* */ "ssimOutside", /*         */ "≥", 0.82], // W14
];

/*
 * ---------------------------------------------------------------------------
 * Regression floors — the rows the frozen bed cannot meet (Decision Log 22)
 * ---------------------------------------------------------------------------
 *
 * Thirty-three rows fail their adopted bound on the frozen active bed. Decision
 * Log 22 lands the flip anyway, and the rule it lands under is the founding one:
 * **nothing is widened and nothing is excepted — the claim narrows, in writing.**
 *
 * So each of these rows keeps its adopted bound as an *aspiration*, marked UNMET
 * in the claims tables with claims §5.26 as the mechanism and W9 as the owner,
 * and CI enforces a **floor pinned at what the bed actually measures**. A cell
 * that gets worse fails. A cell that gets better passes, and keeps passing until
 * someone re-pins the floor upward. What this must never become is a bound that
 * was quietly moved to wherever the code happened to land: the difference is that
 * a floor is not a claim, and §5.27 states the unmet claim beside every one.
 *
 * ## The epsilon, declared
 *
 * A floor sits one `FLOOR_EPSILON` below the measurement (above it, for a `≤`
 * row), so re-measurement noise cannot fail CI on an unchanged renderer. The
 * captures are deterministic — the matrix records `deterministic: true` and
 * `repeatNoise: 0` on every cell — so this is headroom against constants moving
 * in their last digit, not against a noisy instrument. It is deliberately far
 * smaller than any of the misses it guards: the largest epsilon here is 0.005
 * against a coherence miss of 0.39.
 *
 * Floor literals are rounded away from the measurement (down for a floor, up for
 * a ceiling) so the number in this file is never tighter than the epsilon says.
 */
/**
 * Floor literals are written to four decimals, so a check on "within epsilon"
 * must allow the rounding step at both ends — and one more, because the tenth
 * digit of a float is not where correctness should be decided. Two steps is
 * still an order of magnitude under the smallest epsilon below.
 */
const FLOOR_ROUNDING = 0.0001;

const FLOOR_EPSILON: Readonly<Record<string, number>> = {
  ssimMean: 0.001,
  ssimOutside: 0.001,
  oklabDeltaEMean: 0.001,
  oklabDeltaEP95: 0.001,
  interiorLevelRatioGpuOverCss: 0.005,
  // Contour distances are pixel-grid quantities on a deterministic capture; the
  // headroom is a tenth of a pixel, against misses of several pixels (W10).
  contourDistanceMean: 0.1,
  contourDistanceP95: 0.1,
};

/** What the frozen bed measured, and the value CI holds it to. */
interface Floor {
  readonly measured: number;
  readonly floor: number;
}

/**
 * `tier / set / scene / profile :: metric` → the reading that could not meet its
 * adopted bound, and the floor pinned under it.
 *
 * `measured` is recorded rather than re-derived, and that is load-bearing. The
 * checks below ask whether the bound was missed *at the moment of pinning*,
 * which is a fact about the frozen bed and stays true; asking the live matrix
 * instead would fail CI the day a cell IMPROVED past its bound, which is the one
 * outcome this construct exists to invite. Decision Log 22 is explicit that
 * worsening fails and improvement passes.
 *
 * Direction is never stored: it comes from the adopted row, since a floor only
 * ever exists where that row is missed.
 *
 * A floor whose cell has since recovered its adopted bound goes inert — still
 * satisfied, no longer binding. Removing it, and restoring the claim it narrowed
 * in §5.27, is W9's work and wants a commit of its own.
 */
const REGRESSION_FLOORS: Readonly<Record<string, Floor>> = {
  // W11a (claims §5.39) REMOVED six floors here — the two dom-tier
  // interiorLevelRatioGpuOverCss rows on photo__glass-over-glass__rest
  // (0.796 → 0.918 against ≥ 0.8) and the four texture-tier oklabDeltaEP95
  // rows on both nested cells (0.19 → 0.07–0.12 against ≤ 0.17), because the
  // GPU tier's upper pane now composites over the glass beneath it instead
  // of over black. Their claims are restored in §5.27 and gate as ordinary
  // rows again.
  // W9 (claims §5.35) REMOVED six floors here — photo__rrect-lg tinted
  // oklabDeltaEMean, light-solid tinted capsule oklabDeltaEP95, and
  // mid-dark-solid capsule oklabDeltaEP95, each at both scales — because the
  // response-curve law brought every one of them inside its adopted bound
  // (the mid-dark capsule 0.1775 → 0.0095). Their claims are restored in
  // §5.27's tables and gate as ordinary rows again.
  // W10 (claims §5.37) PINNED two contour floors here on
  // photo__rrect-md__rest-tint-orange (1x texture, 5.8893 / 33 px) — an
  // instrument floor, ONE interior hole the luminance-delta extractor cut where
  // the orange tint sat over the photo's own orange. W11b (claims §5.40) gave
  // the extractor a chroma arm and REMOVED them: the cell reads IoU 1.000 and
  // contour 0 / 0 under the declared rule, the claims restored in §5.27.
  // W11c G1 (claims §5.42; W11 Decision Log 5, user decision 2026-09-03)
  // REMOVED three floors here — the 1x texture-tier ssimMean rows on
  // checkerboard rrect-ml, glass-over-glass and rrect-lg (0.862 / 0.880 /
  // 0.823 → 0.896 / 0.899 / 0.893 against ≥ 0.88) — because the body is now
  // the reference's two-component law (a sharp σ 1.25 body mixed toward a
  // σ 10 scatter). Their claims are restored in §5.27. The eight dom-tier
  // rows below RATCHET UP by 0.011–0.152 (the CSS tier's one blur() runs at
  // the law's mixed σ and cannot carry its sharp component; the claim is
  // narrowed to that form, §5.42 §5). The four 2x texture-tier rows RE-PIN
  // DOWN by 0.0015–0.0083: the law is fitted at 1x and the 2x reference is
  // a different object (§5.41 §5); the crossing was the dry run's own
  // prediction and is accepted by decision, the claim narrowed to the 1x bed
  // until a Retina capture exists.
  // W11c G2 (claims §5.44) REMOVED the 2x texture-tier ssimMean floor on
  // checkerboard rrect-md (0.9234 → 0.9389 against ≥ 0.93) and RATCHETED the
  // other three 2x texture rows UP by 0.018–0.023: the lens is the body read
  // from 1.6 lens depths inside, at full weight, and the rim band was 61–91%
  // of what the GPU tier had left. The dom rows below are byte-unchanged
  // (the CSS tier has no lens).
  // W16 G2 (claims §5.73; W16 Decision Log 3, user decision 2026-09-04)
  // REMOVED the 1x dom-tier ssimMean floor on checkerboard rrect-md here
  // (0.89628 → 0.90284 against ≥ 0.90) because the CSS tier's body is now
  // the reference's two-component law too: two filtered children at the
  // renderer's effective widths, the depth ramp as a raster mask on the
  // heavy one, in linear light on Chromium (§5.72 §1). Its claim is
  // restored in §5.27. Every other dom row that the tier moved is re-recorded
  // at the landing's reading with its floor one epsilon under, as every
  // floor here sits: the three other 1x rows RATCHET UP by 0.0064–0.0141;
  // at 2x the four large spans FELL against the W15 bed by 0.0025–0.0051
  // with the band as the mechanism — without a lens the sharp component's
  // crisp checker runs to the contour where the reference's is curved, and
  // the smeared single blur had hidden that absence (§5.72 §5) — yet
  // rrect-ml and rrect-lg still read above their W11c pins and RATCHET UP,
  // glass-over-glass stays inside its epsilon and its floor is KEPT, and
  // rrect-md RE-PINS DOWN by 0.0021 (0.91695 → 0.91489, 0.0010 under the
  // W15 bed's live reading) by the user's decision, the claim narrowed to
  // the band the tier cannot draw.
  // W17 G2 (claims §5.76; W17 Decision Log 7, user decision 2026-09-05)
  // RATCHETED six of the seven dom floors UP by 0.0004–0.0190 and KEPT one
  // (2x glass-over-glass, 0.86832 → 0.86809 inside its epsilon): the CSS
  // tier now draws the renderer's interior composite — the tint's lerp as a
  // table in the sharp layer's linear-light filter over the doctrine's floor,
  // the mirror in the shader's order with the inner shadow — and every 1x
  // large span rose 0.008–0.019 with its interior on the renderer's level.
  // None meets its adopted bound: the rim band the tier has no lens to draw
  // is still the mechanism (§5.72 §5), unchanged in kind.
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.91529, floor: 0.9142 },
  // W9 (claims §5.35, user decision 2026-09-02) RE-PINNED seven ssimMean
  // floors on the checkerboard rrect-lg/ml cells, each DOWN by 0.0002–0.0072:
  // the response-curve law lands the interior MEAN on the reference and pays
  // a sliver of structural similarity for it — a measured, decided trade
  // that bought the six restored claims above, not a regression that slipped.
  // The SSIM axis on these cells is re-attributed to a structure round the
  // W9 spec's Deferred charters; the floors keep ratcheting from here.
  "dom / calibration / checkerboard__rrect-ml__rest / apple-macos-26.5-1x-light-standard :: ssimMean": { measured: 0.87574, floor: 0.8747 },
  "dom / calibration / checkerboard__rrect-ml__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.87892, floor: 0.8779 },
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-1x-light-standard :: ssimMean": { measured: 0.86095, floor: 0.8599 },
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.86809, floor: 0.8677 },
  "dom / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-1x-light-standard :: ssimMean": { measured: 0.87021, floor: 0.8692 },
  "dom / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.87222, floor: 0.8712 },
  // W12 (claims §5.59; W12 Decision Logs 4, 6 and 7) RATCHETED the three 2x
  // texture-tier rows UP again by 0.010–0.014: the lens is now the reference's
  // own field (one steep power on Apple's span law along a normal ovalized by
  // 0.8, §5.51–§5.54) and every checkerboard row rose with it. The rows still
  // miss 0.93 and stay held by decision, their mechanism re-attributed: not "a
  // different object at 2x" but the body's depth ramp — the reference fades
  // its sharp term from the contour inward and vitrea mixes one share per
  // span (§5.55, §5.58) — which is the next body wave's charter (W13). The dom
  // rows are byte-unchanged (the CSS tier has no lens).
  // W11a (claims §5.39) RATCHETED the nested cell's two texture rows UP once
  // its upper pane composited over the base glass (0.84092 → 0.87961,
  // 0.87624 → 0.89482); W11c G1 (claims §5.42) MET the 1x row and re-pinned
  // the 2x one with the rest of the 2x family above.
  // W14 G2 (claims §5.66; W14 Decision Log 6, user decision 2026-09-03)
  // REMOVED the three 2x texture-tier ssimMean floors here — checkerboard
  // rrect-ml, glass-over-glass and rrect-lg (0.91579 / 0.92114 / 0.91128 →
  // 0.9746 / 0.9762 / 0.9680 against ≥ 0.93) — because the outer shadow is
  // now the reference's two-term composite: a backdrop-adaptive black
  // multiply and a blurred copy of the backdrop's own light, on W8's one
  // falloff. §5.60 had read 63–66% of those rows' deficit OUTSIDE the
  // silhouette, and removing it met the bound with 0.04 of margin; the body's
  // depth ramp (W13) was never what those rows needed. Their claims are
  // restored in §5.27. The dom rows above are unchanged in kind: the CSS tier
  // carries the adaptive alpha and no lift (W14 Decision Log 4).
};

/**
 * How many rows the frozen bed cannot meet. Pinned so the set cannot grow
 * quietly. 33 at the §5.27 landing; 27 after W9 restored six (claims §5.35);
 * 23 after W10 restored the six tinted coherence rows and pinned two contour
 * rows on a cell the predicate newly admits (claims §5.37); 17 after W11a
 * restored the six nested-glass rows the unrendered upper pane had floored
 * (claims §5.39); 15 after W11b's chroma arm closed the hole those two contour
 * rows were pinned on (claims §5.40); 12 after W11c's body law met the three
 * 1x texture-tier structure rows (claims §5.42); 11 after W11c's lens met the
 * 2x texture-tier rrect-md row (claims §5.44); still 11 after W12 (claims
 * §5.59), whose lens raised the three 2x texture rows without meeting them;
 * 8 after W14's outer shadow met those three (claims §5.66) — the deficit was
 * outside the silhouette all along; 7 after W16's two-layer CSS body met the
 * 1x dom-tier rrect-md row (claims §5.73), the seven left being the CSS tier's
 * large spans against the rim band it has no lens to draw.
 */
const UNMET_ROWS = 7;

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
  {
    profileKey: "apple-macos-26.5-1x-dark-standard",
    cellsPerTier: 13,
    texture: TEXTURE_TIER_DARK,
    dom: DOM_TIER_DARK,
    names: { texture: "TEXTURE_TIER_DARK", dom: "DOM_TIER_DARK" },
  },
  {
    profileKey: "apple-macos-26.5-2x-dark-standard",
    cellsPerTier: 13,
    texture: TEXTURE_TIER_2X_DARK,
    dom: DOM_TIER_2X_DARK,
    names: { texture: "TEXTURE_TIER_2X_DARK", dom: "DOM_TIER_2X_DARK" },
  },
];

/**
 * The profiles the gate leaves ungated: **none, since 2026-09-01.**
 *
 * This list is kept, empty, because its emptiness is the end of a story the rest
 * of the file tells and a deleted constant would tell nothing. It held four
 * profiles for most of the wave, then two, and now zero.
 *
 * How it emptied, in order. W1's split extension gave every provisional profile
 * validation and holdout scenes, which is what a bound in this document must be
 * set against; that promoted the two **accessibility** profiles on 2026-08-30
 * (§5.6). The **dark pair** stayed behind one more round — not for want of
 * measurement but because its figures were mid-investigation, and a table set
 * from numbers about to be re-measured would be adopted twice. The frozen active
 * bed settled them, claims §5.28 proposed their tables row by row against it, and
 * the gate adopted all 28 fidelity rows on 2026-09-01. Every one passes on both
 * columns.
 *
 * So `MATRIX_PARTITION` below is now entirely gated profiles, and the assertion
 * that the gated and ungated sets together account for the whole matrix has
 * become the stronger statement that the gated set alone does.
 */
const UNGATED_PROFILES: readonly string[] = [];

/**
 * The dark pair, named where the file needs to talk about them as a pair rather
 * than as two entries in `GATED_PROFILES`.
 */
const DARK_PROFILES = [
  "apple-macos-26.5-1x-dark-standard",
  "apple-macos-26.5-2x-dark-standard",
] as const;

/**
 * The whole matrix, and how it partitions — asserted per profile rather than as
 * a bare total, so a profile going missing cannot be absorbed by another's cells
 * arriving. Six native profiles × two web tiers, on the frozen active bed.
 *
 * **The bed the counts are over (2026-09-01): the FROZEN ACTIVE bed.**
 *
 * The tinted scenes are HERE. The retired inactive bed carried none of them —
 * that capture session had dropped the author tint's COLOUR, which its own bytes
 * proved when scenes declaring `systemOrange` and `systemBlue` over one backdrop
 * came back byte-identical, and `cli/compare.ts` skipped the axis on every
 * profile rather than filing untinted material under a tinted scene id. The
 * re-captured bed carries the colour, `colourlessTintEvidence` no longer fires,
 * and W3's twelve tinted scenes are admitted and gated. That is most of the
 * growth from 176 cells to 230.
 *
 * The tinted cells gate under the general light-standard tables rather than under
 * tint tables of their own — a stricter outcome than §5.13 proposed, recorded
 * there — and ten of the floored rows in §5.27 are tinted cells.
 *
 * Also here is W7's `mid-dark-solid__capsule-button__rest`, in the four standard
 * profiles, one cell per profile per tier.
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
  // The same scene, the same reason, in the two profiles adopted 2026-09-01: a
  // dark solid under a dark scheme leaves no interior to sample either.
  "apple-macos-26.5-1x-dark-standard": ["dark-solid__capsule-button__rest"],
  "apple-macos-26.5-2x-dark-standard": ["dark-solid__capsule-button__rest"],
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
 *
 * **What left it with W9 (2026-09-02, claims §5.35).** Eight rows, none
 * joining: the dom-tier checkerboard rrect-sm/md and toolbar-group cells at
 * both scales, and `hc-text__rrect-md__rest` on three of its four rows. Every
 * one was an `areaWeb` exclusion — the web silhouette under-recovered because
 * the surface's interior sat too close to the backdrop for the extractor.
 * Landing the interior mean on the reference moved them clear (all eight now
 * read IoU ≥ 0.99, contour p95 ≤ 1 px), so they gate as ordinary cells.
 *
 * **What moved with W10 (2026-09-02, claims §5.37).** The `bodiesWeb` family's
 * account above — "the tint carries the surface toward the backdrop's own
 * colour and the extractor loses the boundary in patches" — was the wash's
 * doing, and the opaque tint dissolves most of it: the texture-tier
 * `photo__rrect-lg` tinted rows at both scales and `photo__rrect-md` tinted at
 * 1x now condition (IoU 0.992–0.994) and gate. Three texture rows JOIN, each a
 * single stray fragment (`bodiesWeb` 2 against 1, area ≥ 0.968): the
 * increased-contrast `photo` tinted capsule and the `orange-half` capsule at
 * both scales. The extractor is still a luminance-delta rule, and an opaque
 * orange over the photo's own orange region is invisible to it — see the
 * contour floors pinned on the `rrect-md` cell it newly admits.
 *
 * **What left it with W11b (2026-09-02, claims §5.40).** Twenty-three rows,
 * none joining: the whole `bodiesWeb` tinted family and the `areaWeb` tinted
 * remainder — `photo__capsule-button__rest-tint-{orange,blue,orange-half}` on
 * every profile that carries them, `photo__rrect-md` and `photo__rrect-lg`
 * tinted on the dom tier, and the 2x-dark untinted `photo` capsule. The
 * extractor gained a chroma arm (OKLab a/b distance ≥ 0.03 beside the
 * luminance delta), so an opaque tint at its backdrop's own luminance is no
 * longer a hole: every one of the twenty-three reads IoU ≥ 0.995 and contour
 * p95 ≤ 1 px, and gates as an ordinary cell. What remains below is the
 * `areaNative` family (references invisible over near-black, and the
 * increased-contrast material over the checkerboard's white), the `areaWeb`
 * `hc-text` family (white glass over white differs in nothing), the 2x
 * texture-tier checkerboard family and `hc-text__rrect-md` at 2x — unchanged,
 * and none of them a colour question.
 *
 * **What left it with W11c G2 (2026-09-03, claims §5.44).** One row, none
 * joining: the 2x texture-tier `checkerboard__rrect-sm__rest`, an `areaWeb`
 * and `bodiesWeb` exclusion (0.985 of its region in four bodies) that the
 * lens closed — the band now carries the interior's structure at the
 * displaced position instead of a sharper sample, and the extractor recovers
 * one body at 0.998 (IoU 0.998, contour p95 0 px). It gates as an ordinary
 * cell.
 *
 * **What JOINS with W16 (2026-09-04, claims §5.73).** Two dom rows, both the
 * capsule under reduced transparency, both `areaWeb`: the two-layer CSS body's
 * reduced-transparency fold reads 0.056–0.070 lighter than the reference's
 * interior where the single blur's read 0.018–0.038 lighter (the level
 * conversion gap of §5.72 §4, seen on the fold), and on the thin span over the
 * checkerboard's white squares and the hc-text bars the luminance-delta
 * extractor loses 8.5% and 14.7% of the region (recovery 1.000 → 0.915 with
 * seven holes, 0.982 → 0.853). Both cells still gate on every perceptual row
 * and hold them (ssimMean 0.983 / 0.992 against ≥ 0.91, ΔE 0.004 / 0.003
 * against ≤ 0.04). The dry run's referee did not run this predicate, so the
 * landing is where it was read — W16 Surprises.
 *
 * **What moved with W17 (2026-09-05, claims §5.76).** One dom row LEAVES —
 * `checkerboard__capsule-button__rest` under reduced transparency, whose
 * fold now recovers 0.9961 of its region with one body once the tier's level
 * is the renderer's — and four JOIN, all `areaWeb`, all one mechanism:
 * `light-solid__rrect-md__rest` at 2x, `light-solid__rrect-ml__rest` at both
 * light scales and `hc-text__capsule-button__rest` at 2x now sit within 0.004
 * of their own background at the renderer's level (0.9315–0.9322 over
 * 0.9337–0.9347 on the light solids), and the luminance-delta extractor
 * separates the GPU tier there only by the rim and lens the CSS tier does
 * not draw. Coherence with the renderer costs the instrument what the
 * renderer keeps; every one of the four still gates on its perceptual rows.
 * The reduced-transparency `hc-text` capsule stays: its recovery rose to
 * 0.9310 against the 0.95 arm (W17 Deferred).
 */
const PREDICATE_EXCLUDES = [
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-1x-dark-standard",
  "dom / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-2x-dark-standard",
  "dom / calibration / light-solid__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "dom / calibration / light-solid__rrect-ml__rest / apple-macos-26.5-1x-light-standard",
  "dom / calibration / light-solid__rrect-ml__rest / apple-macos-26.5-2x-light-standard",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-reduced-transparency",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "dom / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / checkerboard__rrect-ml__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-1x-dark-standard",
  "texture / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-2x-dark-standard",
  "texture / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-reduced-transparency",
  "texture / holdout / hc-text__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
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

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
/**
 * Which matrix this gate reads — the canonical one, or a scratch one named by
 * `VITREA_MATRIX_PATH` (contract X6, W17 G1).
 *
 * The gate exists to run over the committed evidence and that is what it does
 * with no environment set. What the variable buys is the referee a dry run
 * needs: W16's lesson was that a landing's own test file has to run against the
 * dry run's matrix BEFORE the merge, or the wave discovers at the landing that a
 * bound it never re-read had moved. Pointing the file at a scratch matrix is the
 * only way to run every bound, every floor and the conditioning predicate over a
 * candidate — a second script replicating them would be a second copy of the
 * numbers this file exists to be the only copy of.
 *
 * A relative path resolves against the package root, which is where the
 * canonical matrix lives, so `VITREA_MATRIX_PATH=results/matrix.json` is the
 * default written out.
 */
const MATRIX_PATH = resolve(
  PACKAGE_ROOT,
  process.env["VITREA_MATRIX_PATH"] ?? resolve(PACKAGE_ROOT, "results", "matrix.json"),
);
const MATRIX = readJson<ResultMatrix>(MATRIX_PATH);

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
    // Since 2026-09-01 this is the stronger statement it used to approximate:
    // the GATED set alone accounts for the whole matrix. `UNGATED_PROFILES` is
    // still summed in so that re-adding a provisional profile keeps this honest
    // rather than silently failing here for the wrong reason.
    expect(
      [...GATED_PROFILES.map((profile) => profile.profileKey), ...UNGATED_PROFILES].sort(),
    ).toEqual(Object.keys(MATRIX_PARTITION).sort());
    expect(UNGATED_PROFILES, "every profile in the matrix is gated").toHaveLength(0);
    expect(GATED_PROFILES).toHaveLength(6);

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
            const pinned = REGRESSION_FLOORS[`${name(cell)} :: ${metric}`];

            // An UNMET row: the adopted bound stands as a claim in §5.27 and CI
            // holds the line where the bed actually is. Worsening fails here.
            if (pinned !== undefined) {
              const because = `${name(cell)}: ${metric} = ${measured.toPrecision(5)}, UNMET against ${comparison} ${threshold}, regression floor ${comparison} ${pinned.floor}`;
              if (comparison === "≥") expect(measured, because).toBeGreaterThanOrEqual(pinned.floor);
              else expect(measured, because).toBeLessThanOrEqual(pinned.floor);
              continue;
            }

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
    for (const profileKey of DARK_PROFILES) {
      for (const cell of cellsOf(profileKey)) {
        if (cell.key.sceneId !== "checkerboard__capsule-button__rest") continue;
        expect(isWellConditioned(cell), `${name(cell)}: settled, this cell conditions fine`).toBe(true);
      }
    }
  });

  // -------------------------------------------------------------------------
  // The regression floors, machine-checked against the claims they narrow
  // -------------------------------------------------------------------------

  it("proves every regression floor stands on a genuinely unmet bound", () => {
    /*
     * A floor is the one construct in this file that can make a red row green,
     * so it is the one that most needs a check it cannot pass by accident. The
     * important assertion is the first: the adopted bound must actually have
     * been MISSED. A floor over a row the bed already met would be a bound
     * quietly moved to wherever the code landed — exactly what Decision Log 22
     * forbade when it said nothing is widened.
     *
     * Every arithmetic check runs against the RECORDED `measured`, not the live
     * matrix, so that a cell which improves past its bound passes here instead
     * of failing. The live reading is enforced against the floor by the gate
     * cases themselves; this case is about whether the floors are honest.
     */
    const seen = new Set<string>();
    const check = (key: string, pinned: Floor, metric: string, missed: boolean, low: boolean): void => {
      seen.add(key);
      const epsilon = FLOOR_EPSILON[metric];
      // A metric with a floor but no declared epsilon is a floor whose width
      // nobody stated, which is the one thing §5.27 promises never happens.
      if (epsilon === undefined) throw new Error(`${key}: no declared epsilon for ${metric}`);
      expect(missed, `${key}: floored, so its adopted bound must have been missed`).toBe(true);
      if (low) {
        expect(pinned.floor, `${key}: a floor must sit at or below its measurement`).toBeLessThanOrEqual(pinned.measured);
        expect(pinned.floor, `${key}: and within the declared epsilon of it`).toBeGreaterThanOrEqual(pinned.measured - epsilon - 2 * FLOOR_ROUNDING);
      } else {
        expect(pinned.floor, `${key}: a ceiling must sit at or above its measurement`).toBeGreaterThanOrEqual(pinned.measured);
        expect(pinned.floor, `${key}: and within the declared epsilon of it`).toBeLessThanOrEqual(pinned.measured + epsilon + 2 * FLOOR_ROUNDING);
      }
    };

    for (const profile of GATED_PROFILES) {
      for (const tier of ["texture", "dom"] as const) {
        for (const [axis, metric, comparison, threshold] of profile[tier]) {
          for (const cell of cellsOf(profile.profileKey, tier)) {
            if (axis === "shape" && (cell.shape === undefined || !isWellConditioned(cell))) continue;
            const key = `${name(cell)} :: ${metric}`;
            const pinned = REGRESSION_FLOORS[key];
            if (pinned === undefined) continue;
            const missed =
              comparison === "≥" ? pinned.measured < threshold : pinned.measured > threshold;
            check(key, pinned, metric, missed, comparison === "≥");
          }
        }
      }
    }

    // The coherence rows, whose direction comes from which end of the band was
    // missed rather than from a single comparison.
    const { min, max } = COHERENCE_ROWS.interiorLevelRatioGpuOverCss;
    for (const profileKey of COHERENCE_GATED) {
      for (const cell of cellsOf(profileKey, "dom")) {
        if (!isWellConditioned(cell)) continue;
        const key = `${name(cell)} :: interiorLevelRatioGpuOverCss`;
        const pinned = REGRESSION_FLOORS[key];
        if (pinned === undefined) continue;
        const missed = pinned.measured < min || pinned.measured > max;
        check(key, pinned, "interiorLevelRatioGpuOverCss", missed, pinned.measured < min);
      }
    }

    // No orphans: a floor naming a cell or metric the gate does not reach would
    // be a claim narrowed against nothing, and would hide a typo in the key.
    expect(
      Object.keys(REGRESSION_FLOORS).filter((key) => !seen.has(key)),
      "floors that no gated row reaches",
    ).toEqual([]);

    // And the set is pinned. Growth is allowed — by editing this number, in a
    // commit, beside a §5.27 row saying what stopped being claimed.
    expect(Object.keys(REGRESSION_FLOORS)).toHaveLength(UNMET_ROWS);
    expect(seen.size).toBe(UNMET_ROWS);
  });

  // -------------------------------------------------------------------------
  // Coherence
  // -------------------------------------------------------------------------

  /*
   * Gated on the two light-standard profiles and, since 2026-09-01, the dark pair.
   * The accessibility tables adopted on 2026-08-30 are the seven fidelity rows as
   * proposed; their coherence figures are measured and reported but were not part
   * of that adoption, so they are asserted present below rather than bounded here.
   *
   * ## The conditioning predicate now carries these rows too (adopted 2026-09-01)
   *
   * One rule on both axes. The shape rows have always skipped a cell whose
   * silhouette the extractor could not resolve; the coherence rows did not, and
   * that inconsistency had a cost the dark pair made visible.
   * `interiorLevelRatioGpuOverCss` samples each tier's interior level **under the
   * native silhouette**, so a cell whose native mask is 2% of its declared region
   * is a ratio of two tiny samples — `dark-solid__rrect-md__rest` reads 1.589 at
   * 1× and 1.855 at 2× for exactly that reason, and it is already excluded from
   * the shape rows by the same measurement.
   *
   * A gate that trusts a two-percent sample on one axis while refusing it on
   * another is not one rule, so the predicate now applies to both. It excludes by
   * MEASUREMENT and never by name — the pin below asserts the degenerate cell
   * fails an arm rather than appearing on a list, and that a well-conditioned cell
   * is still gated.
   */
  const COHERENCE_GATED = [
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
    ...DARK_PROFILES,
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
      let skipped = 0;
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
        // The conditioning predicate, on this axis too (adopted 2026-09-01). The
        // ratio is sampled under the native silhouette, so a cell the extractor
        // could not resolve gives a ratio of two degenerate samples. Skipped by
        // measurement, and counted as skipped rather than as a gated pair.
        if (!isWellConditioned(cell)) {
          skipped += 1;
          continue;
        }

        const ratio = reading(cell, "coherence", "interiorLevelRatioGpuOverCss");
        const pinned = REGRESSION_FLOORS[`${name(cell)} :: interiorLevelRatioGpuOverCss`];

        // The referee `backdrop-tone.ts` nominated has ruled against the CSS
        // tier's one-mean-per-source read (claims §5.26). Until W9 re-poses the
        // question, the divergence is pinned where it is rather than allowed.
        if (pinned !== undefined) {
          const because = `${name(cell)}: interior level gpu ÷ css = ${ratio.toPrecision(4)}, UNMET against ${min}…${max}, regression floor ${pinned.floor}`;
          if (pinned.measured > max) expect(ratio, because).toBeLessThanOrEqual(pinned.floor);
          else expect(ratio, because).toBeGreaterThanOrEqual(pinned.floor);
          ratios += 1;
          continue;
        }

        const because = `${name(cell)}: interior level gpu ÷ css = ${ratio.toPrecision(4)}, gate ${min}…${max}`;
        expect(ratio, because).toBeGreaterThanOrEqual(min);
        expect(ratio, because).toBeLessThanOrEqual(max);
        ratios += 1;
      }
      expect(
        ratios + skipped,
        "every scene with a material on both tiers is a coherence pair",
      ).toBe(dom.length - noShape.length);
      expect(ratios, "the predicate must not empty this row").toBeGreaterThan(0);
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
     * One case left, since the dark pair's adoption on 2026-09-01: the two
     * accessibility profiles are gated on their fidelity rows but not on
     * coherence, because the 2026-08-30 adoption was the seven fidelity rows as
     * proposed and their coherence figures were not part of it.
     *
     * Presence is what is asserted — a profile that silently stopped carrying
     * coherence would otherwise look exactly like one that was never gated on it.
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

  it("excludes the degenerate coherence cell by measurement, and gates its neighbours", () => {
    /*
     * The pin for the predicate extension adopted 2026-09-01, and it is written
     * to fail in both directions.
     *
     * The exclusion must be earned by the measurement, not by the scene id. So
     * the degenerate cell is asserted to FAIL a named arm — if a future bed
     * resolves `dark-solid__rrect-md__rest` properly, this fails and the cell
     * goes back to being gated, which is the correct outcome and not a
     * maintenance burden to route around.
     *
     * And the extension must not have quietly emptied the row: a well-conditioned
     * dark cell is asserted to still be gated on its ratio.
     */
    const degenerate = MATRIX.cells.filter(
      (cell) =>
        cell.tier === "dom" &&
        cell.key.sceneId === "dark-solid__rrect-md__rest" &&
        (DARK_PROFILES as readonly string[]).includes(cell.key.profileKey),
    );
    expect(degenerate, "the cell the extension exists for").toHaveLength(DARK_PROFILES.length);

    for (const cell of degenerate) {
      const at = (metric: string): number => reading(cell, "shape", metric);
      // Excluded, and excluded because the extractor recovered almost nothing —
      // roughly 2% of the declared region, not a borderline miss of the floor.
      expect(isWellConditioned(cell), `${name(cell)}: must fail the predicate`).toBe(false);
      expect(at("silhouetteAreaNative") / at("componentRegionArea")).toBeLessThan(0.05);
      // And its ratio is the out-of-band number the extension exists to keep out.
      const ratio = reading(cell, "coherence", "interiorLevelRatioGpuOverCss");
      expect(ratio).toBeGreaterThan(COHERENCE_ROWS.interiorLevelRatioGpuOverCss.max);
    }

    // The other side of the pin: the row still bites on this profile.
    for (const profileKey of DARK_PROFILES) {
      const gated = cellsOf(profileKey, "dom").filter(
        (cell) =>
          isWellConditioned(cell) &&
          cell.coherence?.interiorLevelRatioGpuOverCss !== undefined,
      );
      expect(gated.length, `${profileKey}: the ratio row must still gate cells`).toBeGreaterThan(5);
      for (const cell of gated) {
        const ratio = reading(cell, "coherence", "interiorLevelRatioGpuOverCss");
        const { min, max } = COHERENCE_ROWS.interiorLevelRatioGpuOverCss;
        expect(ratio, `${name(cell)}: well-conditioned, so gated`).toBeGreaterThanOrEqual(min);
        expect(ratio, `${name(cell)}: well-conditioned, so gated`).toBeLessThanOrEqual(max);
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

// ---------------------------------------------------------------------------
// W14 X7: the shadow axis's affine pair, adopted at G2 (claims §5.66 §5)
// ---------------------------------------------------------------------------

/**
 * The pair `y = a·bg + c` per band (claims §5.62 §8) is the instrument that
 * sees the two things the occlusion ratio cannot: what the shadow removes over
 * a solid backdrop, and the light the thick shadow ADDS (the lift, `c`). Two
 * readings of it are adopted here, GPU tier only, on the light-standard
 * profiles at both scales, from band `3-6` below the surface — the first band
 * clear of the body's own edge (§5.62 §8's `0-3` caveat):
 *
 *   - `light-solid__capsule-button`: the occlusion off the band, web against
 *     native, within 20% — the charter's own S3 tolerance. The W12 close read
 *     2.29× here (the user's by-eye "the shadow is darker on the light-solid
 *     capsule"); the landing reads 1.013× at 1x and 1.008× at 2x.
 *   - the four thick checkerboard cells: `c` web against native within 20%.
 *     The lift is what §5.60 §3 found half the large cells' whole-crop
 *     deficit to be, and a renderer that stopped painting it would pass every
 *     other row in this file. Landing ratios 1.001 / 1.003 / 0.949 / 0.916 at
 *     1x and 1.002 / 0.980 / 0.935 / 0.899 at 2x on rrect-md / rrect-ml /
 *     glass-over-glass / rrect-lg; the two holdout cells' one-signed residual
 *     is `liftSpanFull` saturating early (§5.66 §3) and stays a recorded gap.
 *
 * The CSS tier carries the adaptive alpha and no lift by decision (W14
 * Decision Log 4), so its `c` is 0 on every checkerboard cell by construction
 * and is not gated; its light-solid capsule reads 1.032× and is covered by the
 * tier-coherence suite rather than here.
 */
const PAIR_RATIO_TOLERANCE = 0.2;
const PAIR_BAND = "3-6";
const PAIR_PROFILES = ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard"];
const LIFT_CELLS = [
  "checkerboard__rrect-md__rest",
  "checkerboard__rrect-ml__rest",
  "checkerboard__glass-over-glass__rest",
  "checkerboard__rrect-lg__rest",
];

interface PairSide {
  readonly direction: string;
  readonly ringLabel: string;
  readonly backdropMeanLinear: number;
  readonly renderedLevelLinear: number;
  readonly slopeALinear?: number;
  readonly interceptCLinear?: number;
}
interface PairAxis {
  readonly affineNative?: readonly PairSide[];
  readonly affineWeb?: readonly PairSide[];
}

function bandBelow(side: readonly PairSide[] | undefined, label: string): PairSide {
  const found = side?.find((row) => row.ringLabel === label && row.direction === "below");
  if (found === undefined) throw new Error(`no band ${label} below on this cell`);
  return found;
}

describe("W14 X7 — the shadow axis's pair, adopted at the outer shadow's landing", () => {
  for (const profileKey of PAIR_PROFILES) {
    it(`${profileKey}: the light-solid capsule's shadow is within 20% of the reference's`, () => {
      const cell = cellsOf(profileKey, "texture").find(
        (candidate) => candidate.key.sceneId === "light-solid__capsule-button__rest",
      );
      expect(cell).toBeDefined();
      const axis = (cell as unknown as { shadow?: PairAxis }).shadow;
      const native = bandBelow(axis?.affineNative, PAIR_BAND);
      const web = bandBelow(axis?.affineWeb, PAIR_BAND);
      const occlusion = (side: PairSide): number =>
        (side.backdropMeanLinear - side.renderedLevelLinear) / side.backdropMeanLinear;
      const ratio = occlusion(web) / occlusion(native);
      expect(
        Math.abs(ratio - 1),
        `${profileKey} light-solid capsule: occlusion ratio web/native ${ratio.toFixed(4)}`,
      ).toBeLessThanOrEqual(PAIR_RATIO_TOLERANCE);
    });

    it(`${profileKey}: the lift is painted on every thick checkerboard cell, within 20%`, () => {
      const cells = cellsOf(profileKey, "texture").filter((candidate) =>
        LIFT_CELLS.includes(candidate.key.sceneId),
      );
      expect(cells.map((cell) => cell.key.sceneId).sort()).toEqual([...LIFT_CELLS].sort());
      for (const cell of cells) {
        const axis = (cell as unknown as { shadow?: PairAxis }).shadow;
        const native = bandBelow(axis?.affineNative, PAIR_BAND);
        const web = bandBelow(axis?.affineWeb, PAIR_BAND);
        const nativeLift = native.interceptCLinear;
        const webLift = web.interceptCLinear;
        expect(nativeLift, `${name(cell)}: the reference's lift is identified here`).toBeDefined();
        expect(webLift, `${name(cell)}: vitrea's lift is identified here`).toBeDefined();
        const ratio = (webLift ?? 0) / (nativeLift ?? 1);
        expect(
          Math.abs(ratio - 1),
          `${name(cell)}: lift ratio web/native ${ratio.toFixed(4)}`,
        ).toBeLessThanOrEqual(PAIR_RATIO_TOLERANCE);
      }
    });
  }
});

