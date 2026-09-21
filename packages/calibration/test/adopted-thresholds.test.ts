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
 *
 *     > **2026-09-21, W31 G4 (Decision Log 3 (a); claims §5.165 §1): the material
 *     > axis gets its first two adopted rows, and the paragraph above is the
 *     > standard they had to meet rather than a rule they break.** `M1` and `M2`
 *     > at the foot of this file gate the body's chroma-to-structure ratio and
 *     > the structure it is read over, on the macOS 27 standard profiles and the
 *     > WebGPU tier only. The two grounds the paragraph names are the two the
 *     > identifiability argument answers with numbers (claims §5.161 §7 (g), read
 *     > again at §5.164 §12). **Not below quantisation**: the statistic's
 *     > numerator is an OKLab chroma spread of 0.02–0.11 against an 8-bit
 *     > capture's OKLab quantisation near 0.002, and all 552 macOS 27 cells of
 *     > W31 G0's re-capture reproduced their committed rows to |Δ| exactly 0, so
 *     > the only spread in it is the 4.5 % / 9.1 % across rasters that the
 *     > adopted band is five times wider than. **Not unidentifiable**: the NATIVE
 *     > side separates by geometry over 1.47× light and 1.69× dark with the web
 *     > side tracking it cell for cell, and the quantity the operator moved was
 *     > three times the band's own half-width.
 *     >
 *     > It is still the narrower claim the paragraph asks for. Neither row is
 *     > stated on any other axis's sub-metric, on the CSS tier — whose `R` reads
 *     > near the reference with no chroma operator anywhere in the renderer,
 *     > which is Decision Log 11's refusal one axis over — or on the two
 *     > accessibility profiles, which stand the operator down entirely. And `M1`
 *     > does not travel alone: `M2` is adopted with it because `R` is scale-free
 *     > in the deviations and is therefore equally blind to a body that loses
 *     > chroma and structure together.
 *     >
 *     > **Two corrections beside the paragraph above, 2026-09-21 (W31 G4 review
 *     > closure; claims §5.165 §9, findings N7 and N9). No assertion moves.**
 *     >
 *     >   - **"Five times wider" is wrong under either reading of the spread.**
 *     >     The 4.5 % / 9.1 % quoted are the PRE-fit medians; the dark half got
 *     >     noisier with the fit and reads **10.60 %** after it, on §7 (b)'s own
 *     >     normalisation (claims §5.164 §12 as its closure corrects it). Against
 *     >     the post-fit dark median the adopted band is **1.9× on the half-band
 *     >     (±0.20) and 3.8× on the full one** — 2.2× and 4.4× against the pre-fit
 *     >     9.1 %, so five was never the number. The argument is unaffected: a
 *     >     band several times the instrument's own spread is what "not below
 *     >     quantisation" needs, and the residual it had to detect sits 0.45 and
 *     >     0.67 from 1.
 *     >   - **"The material axis gets its first two adopted rows" reads `M2` as a
 *     >     fidelity row and it is not one.** `M1` is stated against APPLE — web
 *     >     over native on the same cell — and is a fidelity bound. `M2` is stated
 *     >     against vitrea's OWN pre-fit generation and is a **regression stop**:
 *     >     it says the fit did not buy its ratio by flattening the body, and it
 *     >     would be green on a body that never resembled the reference. So the
 *     >     axis gains one fidelity row and one guard on it, which is the pair the
 *     >     paragraph's two grounds are answered by and is a smaller claim than
 *     >     "two adopted rows" on its own suggests.
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

import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
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
 *
 * Since W18 G2 (claims §5.79) the dom tier here carries eight cells to the
 * texture tier's nine: the holdout `hc-text__capsule-button__rest`, excluded
 * from the shape rows since W1 and the most degenerate cell on the bed, yields
 * no measurable contour once the outer shadow leaves the CSS tier's sampled
 * backdrop, and the harness writes no cell for it (`GatedProfile.cells`). Its
 * perceptual rows are the one thing the bed loses; named, not absorbed.
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
  // An area ratio on a deterministic capture, on the same order as SSIM's and
  // against misses of 0.003 and 0.025 (W21 Decision Log 4 (c)).
  silhouetteIoU: 0.001,
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
  // W18 G2 (claims §5.79; W18 Decision Log 4, user decision 2026-09-05)
  // RATCHETED three of the seven UP by 0.0001–0.0005 (the three 1x large
  // spans) and KEPT four (every 2x row, inside its epsilon): the outer shadow
  // left the CSS tier's own sampled backdrop — on L3 per surface, on the
  // group's last-painted host per group — and the rows moved by the shadow's
  // share of a large span's interior, which is small. Every reading below is
  // the canonical bed's at this landing; none meets its bound, the rim band
  // still the mechanism.
  // W19 G2 (claims §5.82; W19 Decision Log 4, landed on the parent's
  // recommendation under the user's standing instruction, 2026-09-05) KEPT
  // all seven: the author tint folded over the contrast floor touches only
  // tinted surfaces on the linear form, and every untinted CSS capture on
  // this bed is byte-identical to the W19 dry run's — the seven rows below
  // are untinted checkerboard spans, unmoved to five places. None meets
  // its bound; the rim band still the mechanism.
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.91521, floor: 0.9142 },
  // W9 (claims §5.35, user decision 2026-09-02) RE-PINNED seven ssimMean
  // floors on the checkerboard rrect-lg/ml cells, each DOWN by 0.0002–0.0072:
  // the response-curve law lands the interior MEAN on the reference and pays
  // a sliver of structural similarity for it — a measured, decided trade
  // that bought the six restored claims above, not a regression that slipped.
  // The SSIM axis on these cells is re-attributed to a structure round the
  // W9 spec's Deferred charters; the floors keep ratcheting from here.
  "dom / calibration / checkerboard__rrect-ml__rest / apple-macos-26.5-1x-light-standard :: ssimMean": { measured: 0.87585, floor: 0.8748 },
  "dom / calibration / checkerboard__rrect-ml__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.87893, floor: 0.8779 },
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-1x-light-standard :: ssimMean": { measured: 0.86141, floor: 0.8604 },
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.86811, floor: 0.8677 },
  "dom / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-1x-light-standard :: ssimMean": { measured: 0.87039, floor: 0.8693 },
  "dom / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-2x-light-standard :: ssimMean": { measured: 0.87220, floor: 0.8712 },
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
  //
  // W21 G2c (claims §5.90 §6; W21 Decision Log 4 (c), the parent's
  // recommendation under the user's standing instruction, 2026-09-07) PINNED the
  // two rows below, on one cell at one scale: the nested pane's `silhouetteIoU`
  // in the 2x dark profile, on both tiers. Neither is the material's level and
  // neither is its shape.
  //
  // What they are is the luminance-delta extractor, on the third cell in three
  // waves to show it (W17's and W18's paragraphs in `PREDICATE_EXCLUDES` have
  // the mechanism): a body that agrees with the reference sits nearer its own
  // backdrop, so the set the extractor recovers is smaller than the one it
  // recovered while the body was wrong. The texture row moved when the GPU tier
  // landed the dark material at G2 (0.95088 → 0.92673 while that tier's own ΔE
  // on the cell fell 0.0274 → 0.0177) and has not moved since; the dom row is
  // this landing's, and it is a row the bed could not read at all a moment ago —
  // the predicate excluded that cell until the CSS tier's level came right, so
  // 0.90482 is the FIRST reading of it, pinned where it was first read rather
  // than lowered from anything.
  //
  // The shape's own instrument disagrees with both, which is why the mechanism
  // is nameable. W20's conformance rows read the DRAWN coverage against the
  // surface's DECLARATION rather than against a luminance threshold, and on this
  // cell's texture tier they read `declaredIoUWeb` 0.99919 with a contour max and
  // p95 of one device pixel at 2x (0.99893 / 1 / 0 at 1x). The tier draws the
  // declared shape to a pixel; what the silhouette row measures is how much of
  // it a threshold can find against a checkerboard. The dom tier carries no
  // conformance row on this cell to quote beside it — the linear form composites
  // the material inside the filter rather than as an element paint, so its
  // interior alpha over the transparent conformance page is the floor overlay's
  // 0.2706 and the harness refuses the reading (the same refusal, for the same
  // reason, that 24 of the 36 light-standard dom cells have always carried).
  //
  // AND ITS TWO CONTOUR ROWS, which Decision Log 4 (c) did not reach because G2b
  // reported the cell one assertion deep and stopped at the `silhouetteIoU`. They
  // are the same instrument on the same cell, and the arithmetic says so rather
  // than the prose: the dom silhouette the extractor recovers at 2x carries **34
  // interior holes** against the texture tier's 40 and the light bed's none, and
  // `contourDistance` measures every hole's boundary as contour. The mean reads
  // 1.7602 device px against ≤ 0.5 and the p95 13 against ≤ 3.0, where the same
  // cell's TEXTURE contour — one silhouette without the holes' perforation at the
  // level the extractor can find — reads 0.0210 and 0. The predicate admits the
  // cell on area (0.9540) and bodies (one), which are the two arms it has; holes
  // are not among them, and this is the first cell on the bed where a silhouette
  // passes both arms and is perforated anyway. Recorded here rather than by
  // widening the predicate, which is a construct no wave may touch to make a gate
  // pass.
  //
  // W10's precedent is exact and in this same list: two contour floors pinned as
  // "an instrument floor, ONE interior hole the luminance-delta extractor cut",
  // removed at W11b when the extractor gained a chroma arm. These come off the
  // same way — by the instrument, or by the nested pane's own charter.
  //
  // The nested pane's own charter is where all four come off: the tone axis
  // stands down over a glass backdrop (W9 Deferred, W21 Deferred), and this cell
  // is the partial that predicts.
  //
  // RE-READ at the W22 landing (claims §5.96 §5; W22 Decision Log 4 (e)) — the
  // first gate that could, because the wave rebuilt the whole bed and W22 G3 gave
  // this cell's overlay the backdrop it had never been handed. The `measured`
  // values below stand as recorded and no floor moves; the landing's own readings
  // beside them are 0.92732 (texture silhouetteIoU, +0.00059), 0.90493 (dom
  // silhouetteIoU, +0.00011), 1.76018 (dom contourDistanceMean, bit-identical)
  // and 13.0 (dom contourDistanceP95, bit-identical). Two improve, two do not
  // move, all four still miss their adopted bound — none goes inert.
  //
  // RE-READ again at the W23 landing (claims §5.104; W23 Decision Log 4 (f)),
  // where the rim's law moved every cell on the bed. The `measured` values below
  // stand as recorded and NO FLOOR MOVES; the landing's own readings beside them
  // are 0.92708 (texture silhouetteIoU, −0.00024 against the W22 landing and
  // still over its floor by 0.0014), 0.92878 (dom silhouetteIoU, +0.0238),
  // 1.28921 (dom contourDistanceMean, −0.471) and 10.0 (dom contourDistanceP95,
  // −3). The three dom rows are the largest movement any of these four has seen,
  // and it is the instrument again from the other side: the rim gives the
  // extractor the overlay's boundary, so the perforated silhouette the W21
  // comment describes closes up. None of the four meets its adopted bound — the
  // dom `silhouetteIoU` is the nearest at 0.0012 under ≥ 0.93 — so all eleven
  // floors are held, none is inert, and none is re-pinned or widened.
  //
  // W23 G2 (claims §5.104; W23 Decision Log 4 (f)) PINNED THREE MORE, on the 1x
  // sibling of exactly that cell and on exactly those rows: the nested pane's
  // `silhouetteIoU`, `contourDistanceMean` and `contourDistanceP95` on the dom
  // tier of the 1x dark profile. **They are first readings, not regressions.**
  // The predicate excluded this cell through 0.11.0 on its `areaWeb` arm (25 069
  // of a 28 100 px region against a 26 695 floor), so no bed has ever gated these
  // three rows; the collapsed rim gives the overlay an edge the extractor can
  // hold, `areaWeb` rises to 26 912, the cell is admitted, and the first thing it
  // says is the same thing its 2x twin says.
  //
  // The mechanism is the paragraph above, unchanged in kind and now read at both
  // scales. This silhouette carries **13 interior holes** against the reference's
  // own 14, and `contourDistance` measures every hole's boundary as contour — so
  // the mean reads 0.9658 device px against ≤ 0.5 and the p95 8 against ≤ 3.0,
  // where the SAME TIER's conformance row on the texture side reads
  // `declaredIoUWeb` 0.99886 with a contour max of one device pixel and a p95 of
  // zero. The tier draws the declared shape to a pixel. What the silhouette rows
  // measure is how much of it a luminance threshold can find against a
  // checkerboard, and the reference is perforated there too.
  //
  // Every one of the three reads BETTER than the 2x twin's pinned value
  // (0.91007 against 0.90482, 0.9658 against 1.7602, 8 against 13) and better
  // than its own 0.11.0 reading behind the predicate (0.84448, 1.2903, 10).
  // Nothing was widened and nothing was lowered: three rows the bed could not
  // read are pinned where they were first read, and they come off the way W10's
  // did — by the instrument, or by the nested pane's own charter, which is where
  // all seven of these now wait.
  //
  // W24 G3 (claims §5.109 §6; W24 Decision Log 3 (d), the parent's
  // recommendation under the user's standing instruction, 2026-09-09) RE-PINNED
  // TWO of those three, on the same cell, DOWN: `silhouetteIoU` from a W23 pin
  // of 0.9090 under a measured 0.91007 to 0.9070 under a measured 0.90804, and
  // `contourDistanceP95` from 8.1 under 8.0 to 8.35 under 8.25. W23's numbers
  // stay written here beside them, as this list's discipline requires; nothing
  // was rewritten. The third row, `contourDistanceMean`, moved 0.96579 → 1.03304
  // and HOLDS under its 1.0658 floor, which is left where W23 pinned it.
  //
  // What moved is not the material and not this cell's fidelity. The wave's
  // transmitting collapse shifts this CSS interior's level by 0.00005 linear —
  // a fiftieth of an eight-bit code — and the cell's own ΔE moves +0.00005. What
  // that shift moves is where a luminance threshold crosses, which is the same
  // mechanism the paragraphs above describe from the other side, and the proof
  // that it is the extractor's and not the material's is the 2x sibling: the
  // identical change swings its three rows the OTHER way by ten times (IoU
  // 0.90482 → 0.92878, contour mean 1.760 → 1.289, p95 13 → 10), and those three
  // are the untouched floors below.
  //
  // A floor comes off by fix and is re-pinned only by the user (the fidelity
  // discipline). This is a decision, taken on the parent's recommendation under
  // the standing instruction, reversible in one edit and the user's to undo.
  // These two come off the way all seven do — by the instrument, or by the
  // nested pane's own charter.
  //
  // W26 G3a (claims §5.124; W26 Decision Log 8, 2026-09-10) TOOK THE INSTRUMENT
  // ROUTE, and the three `silhouetteIoU` floors of this cell — the 1x dom re-pin
  // just described, and the 2x texture and 2x dom pins above — CAME OFF BY FIX.
  // They are gone from this table; their readings are kept here as this list's
  // discipline requires, old → corrected on the same committed 0.14.0 bed:
  //
  //   dom / 1x dark     silhouetteIoU  floor 0.9070   0.90804 → 0.97319
  //   texture / 2x dark silhouetteIoU  floor 0.9257   0.92707 → 0.99979
  //   dom / 2x dark     silhouetteIoU  floor 0.9038   0.92878 → 0.98289
  //
  // All three clear ≥ 0.93, the dark profiles' own adopted bound, so they stop
  // being floors rather than being re-pinned. The fix is in the metric, not in
  // the material: `silhouetteIoU` is now taken over the DECIDABLE region — the
  // declared region minus every pixel enclosed by a hole of either mask — which
  // is claims §5.15's hole-fill correction for `contourDistance`, applied to the
  // silhouette. Every paragraph above diagnosed this cell as "the extractor's
  // contrast and not the material's"; W26's spike measured that the drop is a
  // fence and not a shape (the threshold scan is not even single-signed) and the
  // metric was corrected instead of the bed being re-pinned again.
  //
  // The four `contourDistance` floors on this same cell are UNTOUCHED and stay
  // below: `contourDistance` has hole-filled since §5.15, so this correction
  // cannot reach it, and the contour instrument's refusal on flat-cornered dark
  // squares is a separate open item.
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-1x-dark-standard :: contourDistanceMean": { measured: 0.96579, floor: 1.0658 },
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-1x-dark-standard :: contourDistanceP95": { measured: 8.25, floor: 8.35 },
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-dark-standard :: contourDistanceMean": { measured: 1.76018, floor: 1.8602 },
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-dark-standard :: contourDistanceP95": { measured: 13.0, floor: 13.1 },
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
 * large spans against the rim band it has no lens to draw; **11 after W21 G2c
 * pinned the nested pane's four 2x-dark shape rows** (claims §5.90 §6; W21
 * Decision Log 4 (c) and the two contour rows it did not reach), which are the
 * extractor's contrast and not the material's — the first two floors on this bed that are not a fidelity row at
 * all, and the reason the comment beside them says so at length; **14 after W23
 * G2 pinned the same three rows on the same cell's 1x sibling** (claims §5.104;
 * W23 Decision Log 4 (f)), which the conditioning predicate had excluded until
 * the collapsed rim gave the extractor an edge to hold — three first readings of
 * rows no bed had gated, every one of them better than the 2x twin's pin;
 * **11 after W26 G3a took `silhouetteIoU` over the decidable region** (claims
 * §5.124; W26 Decision Log 8), which met all three of that cell's IoU rows at
 * 0.97319 / 0.99979 / 0.98289 against ≥ 0.93 — the first three floors on this bed
 * to come off by correcting an INSTRUMENT rather than the material, and the
 * answer to what the comment beside them had been saying for three waves.
 */
const UNMET_ROWS = 11;

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
  /**
   * How many cells of this profile each tier carries. One number served both
   * tiers until W18 G2 (claims §5.79), when the increased-contrast profile's dom
   * tier lost `hc-text__capsule-button__rest`: with the outer shadow out of the
   * CSS tier's sampled backdrop that cell's silhouette — already the most
   * degenerate on the bed, 2 293 of 4 872 px in three bodies — no longer yields
   * a contour the curvature reader can sample, and `cli/compare.ts` writes no
   * cell for it. The texture tier keeps its nine. Stated per tier so the loss
   * is a number here and not a silently smaller gate.
   */
  readonly cells: { readonly texture: number; readonly dom: number };
  readonly texture: readonly GateRow[];
  readonly dom: readonly GateRow[];
  /** The table constants' own names, so a failure message points at the source. */
  readonly names: { readonly texture: string; readonly dom: string };
}

const GATED_PROFILES_26_5: readonly GatedProfile[] = [
  {
    profileKey: "apple-macos-26.5-1x-light-standard",
    cells: { texture: 36, dom: 36 },
    texture: TEXTURE_TIER_LIGHT,
    dom: DOM_TIER_LIGHT,
    names: { texture: "TEXTURE_TIER_LIGHT", dom: "DOM_TIER_LIGHT" },
  },
  {
    profileKey: "apple-macos-26.5-2x-light-standard",
    cells: { texture: 36, dom: 36 },
    texture: TEXTURE_TIER_2X_LIGHT,
    dom: DOM_TIER_2X_LIGHT,
    names: { texture: "TEXTURE_TIER_2X_LIGHT", dom: "DOM_TIER_2X_LIGHT" },
  },
  {
    profileKey: "apple-macos-26.5-1x-light-reduced-transparency",
    cells: { texture: 8, dom: 8 },
    texture: TEXTURE_TIER_REDUCED_TRANSPARENCY,
    dom: DOM_TIER_REDUCED_TRANSPARENCY,
    names: {
      texture: "TEXTURE_TIER_REDUCED_TRANSPARENCY",
      dom: "DOM_TIER_REDUCED_TRANSPARENCY",
    },
  },
  {
    profileKey: "apple-macos-26.5-1x-light-increased-contrast",
    cells: { texture: 9, dom: 8 }, // dom 9 → 8 at W18 G2; see `cells` above
    texture: TEXTURE_TIER_INCREASED_CONTRAST,
    dom: DOM_TIER_INCREASED_CONTRAST,
    names: { texture: "TEXTURE_TIER_INCREASED_CONTRAST", dom: "DOM_TIER_INCREASED_CONTRAST" },
  },
  {
    profileKey: "apple-macos-26.5-1x-dark-standard",
    cells: { texture: 13, dom: 13 },
    texture: TEXTURE_TIER_DARK,
    dom: DOM_TIER_DARK,
    names: { texture: "TEXTURE_TIER_DARK", dom: "DOM_TIER_DARK" },
  },
  {
    profileKey: "apple-macos-26.5-2x-dark-standard",
    cells: { texture: 13, dom: 13 },
    texture: TEXTURE_TIER_2X_DARK,
    dom: DOM_TIER_2X_DARK,
    names: { texture: "TEXTURE_TIER_2X_DARK", dom: "DOM_TIER_2X_DARK" },
  },
];

/*
 * ---------------------------------------------------------------------------
 * The fifth adoption: macOS 27, at the 26.5 values (W29 Decision Log 4 (a))
 * ---------------------------------------------------------------------------
 *
 * The reference moved. macOS 27 draws a different material under every app
 * (claims §5.151: it moved on all 619 cells and its geometry did not), the 27
 * bed is captured under its own keys beside the frozen 26.5 one, and W29 G3
 * refits vitrea to it. **The bounds that judge that refit are declared here
 * before the fit is read** — contract X5, and the reason this block lands in a
 * commit of its own that precedes every fit commit.
 *
 * **The user ruled the numbers, and ruled them to be the 26.5 numbers**
 * (Decision Log 4 (a), 2026-09-19): the five unconfounded 27 profiles carry the
 * 26.5 tables' values per tier, and increased contrast carries no table at all.
 * So these are not new tables — they are the same tables, and they are ALIASES
 * rather than transcriptions on purpose. A copy could drift from its twin by a
 * digit and nothing would notice; an alias is the ruling itself, in code.
 *
 * *What un-aliasing one would mean.* If a later wave re-pins a 27 bound, it must
 * break that table out into its own literal rather than edit the constant on the
 * left of the `=`, because the 26.5 tables gate the frozen 26.5 rows and X1
 * forbids moving them. The alias is a statement that the two are equal today,
 * not a statement that they are the same object forever.
 *
 * *Why the 26.5 values are a defensible target rather than an optimistic one.*
 * G2 measured the two operating systems against each other at a whole-cell ΔE of
 * 0.014 at the median — an order under the 0.07 the light texture table already
 * allows (claims §5.151 §10). On the two light standard profiles and on reduced
 * transparency the whole native-to-native distribution sits inside the allowance
 * (ΔE mean p90 0.047, 0.048 and 0.009). On the two DARK profiles it does not:
 * p90 0.111 and max 0.155 against an allowance of 0.09, edge-weighted p90 0.072
 * against 0.04. The user ruled these tables knowing that (Decision Log 4 (a)),
 * and ruled what a dark miss means: **a floor decision for the user, recorded**
 * — not a bound loosened after the read, and not a fit failure.
 *
 * *No regression floor for any 27 profile, in this wave.* Acceptance clause 4
 * rules it out and the reason is the bed's own bar: the 27 fixtures are
 * published at the seven-run probe bar, not the seventeen-run freeze bar the
 * 26.5 floors stand on (claims §5.150 Part B §4). A floor pinned at a
 * seven-run bed's reading would claim a precision the bed does not carry. The
 * assertion below is what keeps that a rule rather than an intention.
 *
 * *One increased-contrast key gets a table and one does not.* The **decoupled**
 * 27 bed is a different accessibility state from the 26.5 bed of the same name —
 * macOS 27 no longer force-enables Reduce Transparency with Increase Contrast —
 * so a bound declared across that pair would be a bound on the decoupling and
 * not on the material (claims §5.151 §9), and it gets none. The **coupled** bed
 * was captured in the state macOS 26.5 forced, so its native-to-native read
 * differs in the operating system and nothing else, and **Decision Log 5 rules
 * it a table at the 26.5 increased-contrast values** on the same form and the
 * same argument as Decision Log 4 (a) (claims §5.152 §B).
 *
 * That entry also names the one row it expects to be hard, so that a miss there
 * reads as the prediction it is rather than as a surprise: the coupled profile's
 * native-to-native **SSIM-outside complement reaches 0.237 at its worst cell
 * against an allowance of 0.20**, the only material-adjacent row of that profile
 * outside its allowance. It is recorded and **not loosened** — a miss on it is a
 * floor decision for the user, exactly as a dark ΔE miss is.
 */

/**
 * A 27 profile's cell counts before the sealed read has been taken.
 *
 * The thresholds above are a DECLARATION — they are chosen, and X5 makes
 * choosing them before the read the whole point. The cell counts are not: they
 * are the machine's output, transcribed from the canonical run the way
 * `PREDICATE_EXCLUDES` is. The two therefore land in two different commits, and
 * this sentinel is what holds the gap open honestly: while it stands, the
 * profile is declared and not yet gated, and the case below asserts the matrix
 * carries no row for it. The moment a row lands, the counts must be transcribed
 * or the suite goes red.
 */
const PENDING_UNTIL_THE_27_READ = "pending-until-the-27-read" as const;

type Declared27Profile = Omit<GatedProfile, "cells"> & {
  readonly cells: GatedProfile["cells"] | typeof PENDING_UNTIL_THE_27_READ;
};

/** The 27 tables, aliased to the 26.5 tables the user ruled them equal to. */
const TEXTURE_TIER_27_LIGHT = TEXTURE_TIER_LIGHT;
const DOM_TIER_27_LIGHT = DOM_TIER_LIGHT;
const TEXTURE_TIER_27_2X_LIGHT = TEXTURE_TIER_2X_LIGHT;
const DOM_TIER_27_2X_LIGHT = DOM_TIER_2X_LIGHT;
const TEXTURE_TIER_27_DARK = TEXTURE_TIER_DARK;
const DOM_TIER_27_DARK = DOM_TIER_DARK;
const TEXTURE_TIER_27_2X_DARK = TEXTURE_TIER_2X_DARK;
const DOM_TIER_27_2X_DARK = DOM_TIER_2X_DARK;
const TEXTURE_TIER_27_REDUCED_TRANSPARENCY = TEXTURE_TIER_REDUCED_TRANSPARENCY;
const DOM_TIER_27_REDUCED_TRANSPARENCY = DOM_TIER_REDUCED_TRANSPARENCY;
const TEXTURE_TIER_27_INCREASED_CONTRAST_COUPLED = TEXTURE_TIER_INCREASED_CONTRAST;
const DOM_TIER_27_INCREASED_CONTRAST_COUPLED = DOM_TIER_INCREASED_CONTRAST;

/**
 * The five profiles Decision Log 4 (a) names and the sixth Decision Log 5 adds,
 * and no others.
 *
 * The list is stated rather than derived from the matrix or from `scenes.json`,
 * for the reason every enumerated list in this file is stated: a gate whose
 * membership follows its artifact cannot notice a profile that arrived or left.
 * A 27 row under any key not here fails the case below — which is what keeps the
 * two increased-contrast beds out by rule rather than by nobody having captured
 * them.
 */
const DECLARED_27_PROFILES: readonly Declared27Profile[] = [
  {
    profileKey: "apple-macos-27.0-1x-light-standard-glass0.5",
    cells: { texture: 36, dom: 36 },
    texture: TEXTURE_TIER_27_LIGHT,
    dom: DOM_TIER_27_LIGHT,
    names: { texture: "TEXTURE_TIER_27_LIGHT", dom: "DOM_TIER_27_LIGHT" },
  },
  {
    profileKey: "apple-macos-27.0-2x-light-standard-glass0.5",
    cells: { texture: 36, dom: 36 },
    texture: TEXTURE_TIER_27_2X_LIGHT,
    dom: DOM_TIER_27_2X_LIGHT,
    names: { texture: "TEXTURE_TIER_27_2X_LIGHT", dom: "DOM_TIER_27_2X_LIGHT" },
  },
  {
    profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5",
    cells: { texture: 13, dom: 13 },
    texture: TEXTURE_TIER_27_DARK,
    dom: DOM_TIER_27_DARK,
    names: { texture: "TEXTURE_TIER_27_DARK", dom: "DOM_TIER_27_DARK" },
  },
  {
    profileKey: "apple-macos-27.0-2x-dark-standard-glass0.5",
    cells: { texture: 13, dom: 13 },
    texture: TEXTURE_TIER_27_2X_DARK,
    dom: DOM_TIER_27_2X_DARK,
    names: { texture: "TEXTURE_TIER_27_2X_DARK", dom: "DOM_TIER_27_2X_DARK" },
  },
  {
    profileKey: "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
    cells: { texture: 8, dom: 8 },
    texture: TEXTURE_TIER_27_REDUCED_TRANSPARENCY,
    dom: DOM_TIER_27_REDUCED_TRANSPARENCY,
    names: {
      texture: "TEXTURE_TIER_27_REDUCED_TRANSPARENCY",
      dom: "DOM_TIER_27_REDUCED_TRANSPARENCY",
    },
  },
  {
    // Decision Log 5, ruled 2026-09-19 after the five above were declared: the
    // coupled bed is the 26.5 state captured on 27, so a bound across the pair is
    // a bound on the material. Declared in its own commit, and that commit still
    // precedes every fit commit that touches this profile (contract X5).
    profileKey: "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
    cells: { texture: 9, dom: 9 },
    texture: TEXTURE_TIER_27_INCREASED_CONTRAST_COUPLED,
    dom: DOM_TIER_27_INCREASED_CONTRAST_COUPLED,
    names: {
      texture: "TEXTURE_TIER_27_INCREASED_CONTRAST_COUPLED",
      dom: "DOM_TIER_27_INCREASED_CONTRAST_COUPLED",
    },
  },
];

/** The 26.5 tables each 27 table is ruled equal to — the pin on the alias. */
const RULED_EQUAL_TO_26_5: Readonly<Record<string, readonly GateRow[]>> = {
  TEXTURE_TIER_27_LIGHT: TEXTURE_TIER_LIGHT,
  DOM_TIER_27_LIGHT: DOM_TIER_LIGHT,
  TEXTURE_TIER_27_2X_LIGHT: TEXTURE_TIER_2X_LIGHT,
  DOM_TIER_27_2X_LIGHT: DOM_TIER_2X_LIGHT,
  TEXTURE_TIER_27_DARK: TEXTURE_TIER_DARK,
  DOM_TIER_27_DARK: DOM_TIER_DARK,
  TEXTURE_TIER_27_2X_DARK: TEXTURE_TIER_2X_DARK,
  DOM_TIER_27_2X_DARK: DOM_TIER_2X_DARK,
  TEXTURE_TIER_27_REDUCED_TRANSPARENCY: TEXTURE_TIER_REDUCED_TRANSPARENCY,
  DOM_TIER_27_REDUCED_TRANSPARENCY: DOM_TIER_REDUCED_TRANSPARENCY,
  TEXTURE_TIER_27_INCREASED_CONTRAST_COUPLED: TEXTURE_TIER_INCREASED_CONTRAST,
  DOM_TIER_27_INCREASED_CONTRAST_COUPLED: DOM_TIER_INCREASED_CONTRAST,
};

const transcribed27 = (profile: Declared27Profile): profile is GatedProfile =>
  profile.cells !== PENDING_UNTIL_THE_27_READ;

/**
 * Every profile the gate runs its tables over: the six 26.5 ones, plus each 27
 * profile whose counts have been transcribed from the sealed read.
 *
 * Composed rather than written out, so a declared-but-unread 27 profile is
 * carried by exactly one construct — and so that transcribing its counts is the
 * only edit needed to put it under every bound, floor, partition and
 * conditioning case below.
 */
const GATED_PROFILES: readonly GatedProfile[] = [
  ...GATED_PROFILES_26_5,
  ...DECLARED_27_PROFILES.filter(transcribed27),
];

/**
 * How many profiles the gate covers, pinned so the composition above cannot
 * quietly cover fewer. It was 6 while the 27 read was pending and is 12 now
 * that the six 27 profiles carry the counts the canonical run measured.
 */
const GATED_PROFILE_COUNT = 12;

/**
 * The one 27 key that gets no table in this wave, named so its absence from
 * `DECLARED_27_PROFILES` reads as the ruling it is rather than as an omission.
 *
 * The DECOUPLED increased-contrast bed: contrast alone on 27 against contrast
 * **with** transparency reduction on 26.5, so a bound across the pair would be a
 * bound on the toggle (Decision Log 4 (a); claims §5.151 §9). It is also not read
 * against vitrea at all in this wave — `compare`'s web accessibility flags key on
 * the manifest's `a11yMode`, which reads `increased-contrast` for both 27 contrast
 * profiles, so the web side cannot yet be put in contrast-without-reduction. That
 * is the tracker entry G1c Part B left, and the reason the absence here is two
 * decisions rather than one.
 */
const UNBOUNDED_27_PROFILES: readonly string[] = [
  "apple-macos-27.0-1x-light-increased-contrast-glass0.5",
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
  "apple-macos-26.5-1x-light-increased-contrast": 17,
  "apple-macos-26.5-1x-light-reduced-transparency": 16,
  "apple-macos-26.5-1x-light-standard": 72,
  "apple-macos-26.5-2x-dark-standard": 26,
  "apple-macos-26.5-2x-light-standard": 72,
  "apple-macos-27.0-1x-dark-standard-glass0.5": 26,
  "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5": 18,
  "apple-macos-27.0-1x-light-reduced-transparency-glass0.5": 16,
  "apple-macos-27.0-1x-light-standard-glass0.5": 72,
  "apple-macos-27.0-2x-dark-standard-glass0.5": 26,
  "apple-macos-27.0-2x-light-standard-glass0.5": 72,
};

const MATRIX_CELLS = 459; // 458 until W29 G3b re-read the 27 bed (§5.154); 229 until W29 G3 appended it (§5.153); 230 until W18 G2 (§5.79)

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
 *
 * **Per TIER since W23 G2** (claims §5.104; W23 Decision Log 4 (f)). It was one
 * list per profile while the two tiers agreed on which scenes vanish, and the
 * collapsed rim separated them: a rim on a surface that drew nothing gives the
 * extractor an outline to find where it had none, and a CSS body that lands
 * closer to its own backdrop takes one away. Both movements are the same
 * mechanism read from the two sides, and neither is a fidelity row — the shape
 * axis is what the extractor could resolve, never what vitrea drew.
 */
const NO_SHAPE_AXIS_SCENES: Readonly<
  Record<string, { readonly texture: readonly string[]; readonly dom: readonly string[] }>
> = {
  // One scene, not two. `light-solid__rrect-md__rest` was here against the
  // retired inactive bed, whose untinted material over a light solid left the
  // extractor no interior to sample at all. The frozen active bed carries a
  // shadow and a rim it did not, so the scene has an interior again and is
  // gated like any other. Removed because the matrix says so — the assertion
  // below re-derives this list from the artifact on every run.
  //
  // W23 G2: at 2x the GPU tier's `dark-solid__capsule-button__rest` LEAVES this
  // list in both schemes. The collapsed rim lands +0.020 of linear light on a
  // body one code under a near-black backdrop, which is over the extractor's
  // 0.02 threshold, so the cell now carries a shape axis — of the rim alone
  // (457 px of a 19 468 px region, 60 bodies), which the conditioning predicate
  // then refuses. It moves from "no axis to gate" to "an axis the predicate
  // excludes", and is named in `PREDICATE_EXCLUDES` instead of here. At 1x the
  // same rim falls under the threshold and the cell stays here.
  //
  // W24 G3 (claims §5.109; W24 Decision Log 3 (i)): at 1x it LEAVES too, in
  // both schemes, and the mechanism is one wave further on. The lit edge
  // modulates the rim's amplitude around the contour by a symmetric cosine
  // about the top-left ↔ bottom-right diagonal, so the two lit arcs are drawn
  // brighter than the flat rim W23 shipped while the straight sides are
  // unchanged, and at 1x those arcs are what now crosses the extractor's 0.02
  // threshold on this near-black cell. What it finds is the arcs alone — 25 px
  // native and 34 px web of a 4 872 px region, in 16 and 18 pieces — and every
  // one of the predicate's four arms refuses it. Same movement as the 2x cells
  // above, same destination: `PREDICATE_EXCLUDES`, not a fidelity row.
  "apple-macos-26.5-1x-light-standard": {
    texture: [],
    dom: ["dark-solid__capsule-button__rest"],
  },
  "apple-macos-26.5-2x-light-standard": {
    texture: [],
    dom: ["dark-solid__capsule-button__rest"],
  },
  // The same scene, the same reason, in the two profiles adopted 2026-09-01: a
  // dark solid under a dark scheme leaves no interior to sample either.
  //
  // W23 G2: `dark-solid__rrect-md__rest` JOINS this list on the CSS tier in both
  // dark profiles. The dark bed's dom cell was the degenerate one the 2026-09-01
  // predicate extension was adopted for — the extractor recovered 205 px of a
  // 15 024 px region at 1x and 849 of 60 064 at 2x, in six to nine pieces — and
  // on the landed bed it recovers nothing at all. That is the CSS tier's body
  // arriving closer to the backdrop it sits on (the dark dom calibration ΔE mean
  // falls 0.00682 → 0.00633 at 1x and 0.00699 → 0.00658 at 2x), read through a
  // luminance-delta extractor: the better the body agrees, the less there is to
  // find. Nothing is lost from the gate — the cell was excluded by the predicate
  // before and carries no axis now — and the reason moves with it.
  //
  // W24 G3: the texture list here empties for the reason the light bed's does —
  // the lit edge's arcs give the 1x collapsed capsule a shape axis of the rim
  // alone, which the predicate then refuses. The two schemes read identically
  // on this cell because the fixture and the capture are the same bytes.
  "apple-macos-26.5-1x-dark-standard": {
    texture: [],
    dom: ["dark-solid__capsule-button__rest", "dark-solid__rrect-md__rest"],
  },
  "apple-macos-26.5-2x-dark-standard": {
    texture: [],
    dom: ["dark-solid__capsule-button__rest", "dark-solid__rrect-md__rest"],
  },
  "apple-macos-26.5-1x-light-reduced-transparency": { texture: [], dom: [] },
  "apple-macos-26.5-1x-light-increased-contrast": { texture: [], dom: [] },
  /*
   * **Every 27 profile's lists are empty, on both tiers, and that emptiness is a
   * measurement** (W29 G3, claims §5.153).
   *
   * On 26.5 the entries above exist because Apple's material over a near-black
   * solid sat inside the extractor's 0.02 linear threshold of its own backdrop:
   * there was no silhouette to find, so the cell carried no shape axis. On macOS
   * 27 it does not sit there — claims §5.151 §4 measured the same thing from the
   * other side (`dark-solid__rrect-64__rest` is 52 px of silhouette on 26.5 and
   * 6,996 px on 27) — and vitrea's refitted material follows it, so every cell of
   * every 27 profile yields a contour on both tiers.
   *
   * They are written out rather than left to the `?? []` default, because an
   * absent key and an empty list would then be the same thing, and these six are
   * the statement that the near-tone cells came back.
   */
  "apple-macos-27.0-1x-light-standard-glass0.5": { texture: [], dom: [] },
  "apple-macos-27.0-2x-light-standard-glass0.5": { texture: [], dom: [] },
  "apple-macos-27.0-1x-dark-standard-glass0.5": { texture: [], dom: [] },
  "apple-macos-27.0-2x-dark-standard-glass0.5": { texture: [], dom: [] },
  "apple-macos-27.0-1x-light-reduced-transparency-glass0.5": { texture: [], dom: [] },
  "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5": { texture: [], dom: [] },
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
 *
 * **What moved with W18 (2026-09-05, claims §5.79).** Four dom rows LEAVE and
 * none joins. Three of them are the light solids W17 admitted — `light-solid__
 * rrect-md__rest` at 2x and `light-solid__rrect-ml__rest` at both light scales.
 * The arm that held them was the BODIES arm, not the area arm the W17
 * paragraph above names (corrected here, that text left as written): on the
 * W17 bed their web silhouettes recovered 0.994–0.998 of the region but in two
 * or three bodies against the region's one. The tier had been sampling its own
 * outer shadow through its own backdrop, and the shadow — offset downward —
 * darkened the body's lower rows toward the background (the bottom two rows of
 * `rrect-ml` at 1x read 0.923 in linear light against the centre's 0.933), where
 * the luminance-delta extractor cut the silhouette. With the shadow carried
 * outside the sampled region (on L3, or on the group's last-painted host) those
 * rows lift by 0.0013–0.0023, the centre does not move, the interior mean moves
 * +0.0003…+0.0008, and the silhouette is one body again at 0.9997–0.9999 of the
 * region. Coherence with the renderer no longer costs these cells. The fourth,
 * `hc-text__capsule-button__rest` under increased contrast, does not condition —
 * it leaves because the bed lost it (`GatedProfile.cells`).
 *
 * **What JOINS with W21 (2026-09-07, claims §5.90 and the W21 landing).** Five
 * rows over a checkerboard in the two dark profiles, and none leaves. All five
 * are `areaWeb` or `bodiesWeb` exclusions and all five are the same mechanism —
 * the dark scheme's response law landing on the material, seen by a
 * luminance-delta extractor:
 *
 * - The four dom rows are the CSS tier's structured-backdrop residual (W21
 *   Decision Log 3 (a)). Its two layers resolve the response from a single
 *   backdrop level, so over a checkerboard the body lands at 0.0122 where the
 *   reference and the WebGPU tier put it at 0.047 — dark enough that the
 *   extractor cuts the silhouette in half: `checkerboard__rrect-md__rest`
 *   recovers 7 618 of a 15 024 px region in two bodies where it recovered the
 *   whole region in one, 30 450 of 60 064 at 2x, and
 *   `checkerboard__glass-over-glass__rest` 17 649 of 28 100 in two bodies (70 609
 *   of 112 416 in six at 2x).
 * - The one texture row, `checkerboard__rrect-md__rest` at 2x, is the opposite
 *   sign of the same coin and the W17 and W18 paragraphs above have its shape
 *   already: coherence with the reference costs the instrument what the renderer
 *   gains. The GPU body moved from 0.0628 to 0.0475 against a reference of
 *   0.0475, and at that level 4 503 px of the region's 60 064 (0.925 recovery,
 *   still one body) fall inside the extractor's threshold of their own backdrop.
 *   Its 1x twin recovers 0.9977 and still conditions.
 *
 * Every one of the five is still gated on all of its perceptual rows, and this
 * list is not a fidelity exceedance — see the landing document for the rows on
 * the coherence axis, which are.
 *
 * **What W21 G2c gave back (2026-09-07; W21 Decision Log 4 (a), (d)).** ONE of
 * those five leaves and none joins: 34 lines become 33. The CSS tier's level over
 * a structured dark backdrop is now the renderer's — the form boundary is a
 * comparison of the two forms' errors and the structured cells take the exact
 * one — and the extractor sees the surface again. The BODIES arm recovers on all
 * four dom rows: `checkerboard__rrect-md__rest` returns to one body from two at
 * both scales, and `checkerboard__glass-over-glass__rest` from two at 1x and six
 * at 2x. Only the 2x nested pane clears the AREA arm with it, recovering 107 239
 * of a 112 416 px region (0.954 against the 0.95 the predicate asks).
 *
 * The other three recover most of what they lost and still miss that arm —
 * `checkerboard__rrect-md__rest` 12 153 of 15 024 (0.809) at 1x and 50 974 of
 * 60 064 (0.849) at 2x, the 1x nested pane 25 047 of 28 100 (0.891) — and they
 * miss it for the reason the texture row in the paragraph above misses it, which
 * is now visibly one mechanism rather than two: a body that agrees with the
 * reference sits inside the extractor's 0.02 threshold of its own backdrop over
 * the checkerboard's white squares, so coherence costs the instrument what the
 * material gains. The CSS rows read that way now because they finally draw what
 * the GPU rows draw. Their perceptual and coherence rows gate as before.
 *
 * **What LEAVES with W22 (2026-09-08, claims §5.96 §6; W22 Decision Log 4 (e)).**
 * FOUR texture rows leave and none joins: 33 lines become 29, and the predicate
 * had been excluding cells for a defect in the RENDERER rather than one in the
 * extractor. All four are 2x light-standard checkerboard cells and all four are
 * the same mechanism — the resting specular sweep, a stationary band the
 * highlight pass drew on the left edge of every surface because nothing in v1
 * ever drove its phase, was fragmenting the web silhouette, and this predicate
 * refuses a mask in pieces. With the band gated on a shimmer amplitude the
 * driver owns (0 at rest), each mask comes back as ONE body:
 *
 * - `checkerboard__rrect-md__rest` 2 bodies → 1, IoU 0.99792 → 0.99953,
 *   contour mean 0.1335 → 0.0302, p95 1 → 0;
 * - `checkerboard__rrect-ml__rest` 3 → 1, 0.99861 → 0.99981, 0.1202 → 0.0164,
 *   p95 1 → 0;
 * - `checkerboard__glass-over-glass__rest` 3 → 1 with its 4 interior holes gone,
 *   0.99750 → 0.99803, 0.1068 → 0.0031, p95 1 → 0;
 * - `checkerboard__rrect-lg__rest` 4 → 1, 0.99885 → 0.99993, 0.1199 → 0.0075,
 *   p95 1 → 0.
 *
 * The gate got stricter, not looser: four cells the bed could not read it now
 * reads, each meeting every bound it newly carries with room, and no bound was
 * widened to take them.
 *
 * **What moved with W23 G2 (2026-09-08; claims §5.104, W23 Decision Log 4 (f)):
 * 29 → 27, four lines leaving and two joining, one mechanism in both
 * directions.** The rim is now a law of the surface's own level with an absolute
 * floor the collapse keeps, so a surface that drew nothing over a near-black
 * backdrop draws an outline — and what the extractor can find moves with it.
 *
 * - **`dom / calibration / dark-solid__rrect-md__rest`, both dark profiles —
 *   LEAVES by losing the axis, not by conditioning.** It recovered 205 px of a
 *   15 024 px region (1x) and 849 of 60 064 (2x), in six to nine pieces; the
 *   landed CSS body sits closer to its own backdrop and the extractor recovers
 *   nothing at all, so the cell carries no shape axis and is named in
 *   `NO_SHAPE_AXIS_SCENES` instead. Same coverage, a different reason.
 * - **`dom / holdout / checkerboard__glass-over-glass__rest / 1x dark` — LEAVES,
 *   admitted.** `areaWeb` 25 069 → 26 912 against a floor of 26 695: the rim
 *   gives the nested pane's overlay an edge the threshold can hold, and the cell
 *   is gated on all four shape rows again (IoU 0.84448 → 0.91007).
 * - **`dom / holdout / hc-text__capsule-button__rest / 2x light` — LEAVES,
 *   admitted.** `bodiesWeb` 2 → 1: the rim closes the gap that split the mask.
 * - **`texture / calibration / dark-solid__capsule-button__rest / 2x dark and
 *   2x light` — JOIN.** These two are the collapsed cell the whole wave is for.
 *   At 2x the kept rim is +0.020 of linear light over the extractor's 0.02
 *   threshold, so the cell gains a shape axis where it had none — an axis of the
 *   RIM alone, 457 px of a 19 468 px region in 60 bodies, on both the native and
 *   the web side (the reference's fixture carries the same outline and no body).
 *   Every arm fires. The predicate is doing exactly what it exists to do: a
 *   silhouette that is one hairline is not a shape to gate a contour on, and the
 *   cell's fidelity is read on its perceptual rows as it always was.
 *
 * No cell lost a gated row to this and no bound moved. Two cells joined the
 * shape gate, two changed which construct names them, and two are excluded for a
 * silhouette that consists of the rim this wave added.
 *
 * W24 G3 (claims §5.109; W24 Decision Log 3 (i)) — **27 → 31, four join and
 * none leaves.** The wave lights the rim around the contour by a symmetric
 * cosine about the top-left ↔ bottom-right diagonal, which brightens the two lit
 * arcs and leaves every straight side exactly where W23 fitted it. Both kinds of
 * movement below are that factor read through a luminance-delta extractor, and
 * neither is a fidelity row.
 *
 * - **`texture / calibration / dark-solid__capsule-button__rest`, 1x dark and 1x
 *   light — JOIN by GAINING an axis.** These are the 1x siblings of the two 2x
 *   cells above and the story is the same one wave on: the lit arcs cross the
 *   extractor's 0.02 threshold where W23's flat rim at 1x did not, so the cell
 *   carries a shape axis for the first time — of the ARCS alone, 25 px native
 *   and 34 px web of a 4 872 px region, in 16 and 18 pieces, IoU 0.639. All four
 *   arms fire. The cell moves out of `NO_SHAPE_AXIS_SCENES` and into this list,
 *   and its fidelity is read on its perceptual rows as it always was (ΔE mean
 *   0.00052 → 0.00047, `ssimMean` 0.99849 → 0.99951).
 * - **`texture / calibration / checkerboard__rrect-md__rest / 2x light` and
 *   `checkerboard__toolbar-group__rest / 2x light` — JOIN on the topology arm,
 *   with every row they take out of the gate met.** `bodiesWeb` goes 1 → 2 and
 *   3 → 4: the lit factor dims the two unlit arcs of a large 2x span by enough
 *   for the threshold to pinch the silhouette into one more piece. This is the
 *   arm doing what it exists to do — a silhouette in more pieces than the
 *   reference's is not one to gate a contour on — but it is worth naming that
 *   nothing was hiding behind it. On the landed bed `rrect-md` reads IoU 0.99634
 *   (≥ 0.93), contour mean 0.236 (≤ 0.5) and p95 1 (≤ 3.0), and `toolbar-group`
 *   reads 0.99026, 0.205 and 1.414 — every one inside its adopted bound, and the
 *   toolbar's IoU and contour mean IMPROVED against the 0.12.0 bed (0.98714 and
 *   0.288). Both cells' ΔE means improve too (0.00367 → 0.00364, 0.00243 →
 *   0.00235). Two calibration cells leave the shape gate meeting every row it
 *   would have asked of them; that is coverage lost to the extractor's
 *   topology, recorded here rather than recovered by touching the predicate.
 *
 * W26 G2 (claims §5.123; W26 Decision Log 7) — **31 → 32 at the candidate, one
 * joins and none leaves**, and unlike the four above this one is a fidelity
 * signal rather than an artefact of an extractor. **The entry is described here
 * and NOT yet in the list**, because this list is read against the COMMITTED
 * `results/matrix.json`, which is still the 0.14.0 bed: adding it now would make
 * the file disagree with the only matrix CI has. Re-deriving it belongs to the
 * canonical rebuild, as it did at W25 G3 → G4, and the cell and its mechanism are
 * written down here so that the rebuild has to reproduce a stated reading rather
 * than discover one.
 *
 * - **`dom / calibration / checkerboard__capsule-button__rest /
 *   apple-macos-26.5-1x-light-reduced-transparency` — JOINS on the HOLES arm.**
 *   `silhouetteHolesWeb` goes **0 → 6** with the native's still 0, the web
 *   silhouette's area 4 856 → 4 541 px² of a native 4 872, IoU 0.99672 → 0.93206
 *   and the contour's max distance 1 → 6 px. The mechanism is one number: this
 *   wave gives the CSS tier the profile's own heavy width, 9 device px, in place
 *   of `blurSigma × gain` through the mip chain's effective ratio — and under
 *   `frost: "increased"` the old form was multiplied by the frost as well, so on
 *   THIS profile the heavy layer goes 24.15 → 9.000 CSS px. Less blur leaves more
 *   of the checkerboard's own structure inside the surface, and the extractor's
 *   luminance threshold reads six of its dark squares as holes.
 *   **The two tiers agree for the first time here, which is why the reading
 *   moved.** At dpr 1 `scatterLod` was clamped at `chainMaxLod` before this wave
 *   (claims §5.116 §2), so the frost could not widen the GPU tier's heavy tap at
 *   all — it drew 13.418 device px frosted or not — while the mirror drew 24.15.
 *   W26 makes both draw 9, and the accessibility fold now reaches the SHARP
 *   component alone on both tiers. Whether the fold should reach the heavy width
 *   is a material question this wave did not declare and did not fit; it is
 *   recorded in the wave's Decision Log and in the tracker with this cell as its
 *   evidence, and the exclusion is what the machine reads meanwhile.
 *
 * W26 G3 (claims §5.126; W26 Decision Log 7 (f) and 10) — **31 → 32 at the
 * LANDED bed, one joins and none leaves, and it is a DIFFERENT cell from the one
 * the paragraph above describes.** That paragraph is the reading at the
 * configuration the parent then REJECTED, in which the CSS tier also took the
 * profile's heavy width; it is kept as read. Under the ruled configuration the
 * CSS tier is byte-identical to 0.14.0 on all 644 captures, so the
 * reduced-transparency dom capsule does not move at all and never enters. What
 * enters instead is a GPU cell, and it is re-derived here from the machine's own
 * output over the rebuilt matrix rather than carried over from the dry run.
 *
 * - **`texture / holdout / checkerboard__rrect-lg__rest /
 *   apple-macos-26.5-2x-light-standard` — JOINS on the BODIES arm.**
 *   `silhouetteBodiesWeb` goes **1 → 3** against a native 1 and a region of 1,
 *   which is the arm firing exactly as designed: a silhouette in more pieces than
 *   the reference's is not one to gate a contour on. `silhouetteHolesWeb` goes
 *   4 → 7 beside it (the native's is 0), and the AREA arm never comes near — the
 *   web silhouette is 174 847 px² of a 175 240 px² region, 0.9978 against a bound
 *   of 0.95.
 *   The mechanism is the wave's one constant and nothing else. This is the
 *   largest span on the bed (160 CSS px) over the coarsest committed
 *   checkerboard, at the scale where the heavy component narrows most in device
 *   px; less blur leaves more of the backdrop's own structure inside the surface,
 *   and the extractor's 0.02 linear-luminance rule pinches that structure into
 *   two more pieces. It is the same reading, on the same instrument, that
 *   Decision Log 8 diagnosed on the nested pane: over a coarse dark pattern the
 *   rule degenerates toward an absolute brightness test and reports the
 *   BACKDROP's structure as the silhouette's.
 *   **Every row it takes out of the shape gate is met at the landed bed**:
 *   `silhouetteIoU` 0.99807 (≥ 0.93), contour mean 0.204 (≤ 0.5), p95 1 (≤ 3.0),
 *   max 2. Its fidelity is read on its perceptual rows as always, and those are
 *   where this cell's real cost is recorded rather than hidden: ΔE mean 0.00795 →
 *   0.01145, the worst single holdout cell of the wave (+0.00350) and the price
 *   of one heavy width per source at the 2x span grading the reference has and
 *   vitrea does not (W26 Decision Log 2 (f), 7 (g); the tracker).
 */
/*
 * ---------------------------------------------------------------------------
 * The fifteen rows the macOS 27 refit missed — recorded, claimed UNMET, and
 * enforced by nothing (W29 G3, claims §5.153)
 * ---------------------------------------------------------------------------
 *
 * **This is NOT a regression floor, and the difference is the whole point.**
 * A floor pins a number and says "no worse than this"; acceptance clause 4
 * forbids one on any 27 profile, because the 27 bed is published at the
 * seven-run probe bar and a floor needs the seventeen-run freeze bar. So these
 * rows enforce no value at all. Each one keeps its adopted bound as a claim that
 * is **missed**, exactly as §5.27's rows keep theirs, and what CI holds is only
 * the membership of this list: a new miss fails the case below, and a row that
 * comes good fails it too. Nothing here can be satisfied by moving a number.
 *
 * The bound was declared before the fit was read (contracts X5; Decision Logs
 * 4 (a) and 5), the fit was read once at a sealed configuration, and the holdout
 * was read once. **Nothing was re-fitted after that read** — which is why five of
 * the fifteen are holdout cells that this child could not and did not tune
 * against. Re-pinning any of these bounds is the user's ruling and nobody
 * else's; the wave's Decision Log 6 draft is where it is put.
 *
 * ## What is left, after W29 G3b read the one law nobody had measured
 *
 * The list was FIFTEEN rows at G3's read and is **seven** now. Decision Log 6 (a)
 * ruled the outer shadow read native-against-native and refit, G3b did it, and
 * every row that cause carried came good — the whole of cause (1) below, plus two
 * rows of cause (2) that turned out to be carrying the same exterior. The eight
 * that cleared are recorded in the ledger's §5.154 with their before and after;
 * the sharpest is `2x-light-standard` texture `checkerboard__rrect-lg__rest ::
 * ssimOutside`, **0.77243 → 0.95599**.
 *
 * The seven that remained were **all holdout cells** and they were two causes,
 * both of which Decision Log 6 accepted as residual rather than chartered to
 * G3b. **Two of the seven cleared at W31 G3** (claims §5.164 §7) and five
 * remain; the paragraph below is kept as the record of the seven and corrected
 * beside rather than rewritten.
 *
 * > **2026-09-21, W31 G3.** Cause (a) below said "no constant in either
 * > document can close it", and that was right: what closed it was a MECHANISM.
 * > `bodyChromaRetention` restores the body's chromaticity toward the blurred
 * > backdrop's at a held linear luma, and the two **`texture`** rows went
 * > 0.21531 → **0.14655** and 0.21341 → **0.14505** against ≤ 0.17. The two
 * > `dom` rows are unmoved to the fifth decimal, because the CSS tier carries
 * > nothing of the operator — a derivation was written, rendered and declined
 * > on the measurement (§5.164 §5) — so they stay here with cause (a) intact
 * > and the lever named. Cause (b)'s three rows are untouched by this wave (X3).
 *
 * **(a) The dark bed's diffusion at a large span over a photograph** — the four
 * `photo__rrect-lg__rest :: oklabDeltaEP95` rows, unchanged to the fourth decimal
 * by the shadow refit, which is the right outcome: the residual is inside the
 * body and the shadow is outside it. The level agrees (native 0.1814 against
 * 0.1636) and the spread does not (0.0417 against 0.0142), so vitrea passes a
 * third of the structure the 27 dark reference passes there. Decision Log 6 (c)
 * made this a child of its own after the wave; §5.153 §9 has the same finding by
 * eye — over a photograph vitrea's body is grey and Apple's is coloured — and the
 * tone response's solve is achromatic by construction, so no constant in either
 * document can close it.
 *
 * **(b) The largest spans keep the most residual** — `checkerboard__rrect-lg__rest`
 * and `checkerboard__glass-over-glass__rest :: ssimMean` on the 1x light dom tier,
 * and `photo__rrect-lg__rest :: ssimOutside` on reduced transparency's. All three
 * improved and none crossed: 0.88380 → 0.88402, 0.89349 → 0.89538, and reduced
 * transparency's moved the wrong way by 0.0003 (0.82736 → 0.82707), which is the
 * one place the shadow refit cost anything measurable. `sizeToneLevelFar` is still
 * the constant W25 declined and §5.153 §6's scale-selective scatter is still the
 * mechanism; Decision Log 6 (b) accepted these as residual.
 *
 * What is NOT here any more is cause (1), and the reason it is worth saying: it
 * was the only one of the three that was a genuinely unmeasured law rather than a
 * known residual, and reading it cost no new capture at all.
 *
 * Decision Log 4 (a) ruled what a dark miss means — a floor decision for the user,
 * recorded — and the review of §5.152 §B extended the same shape to a 2x-light
 * SSIM miss. All seven are in one of those two classes.
 */
interface MissedRow {
  readonly measured: number;
  readonly bound: string;
}

/*
 * **2026-09-21, W31 G4: three of the entries below are recorded AT ADOPTION, by
 * the row that records them** (Decision Log 3 (a); claims §5.165 §1).
 *
 * Every other entry in this list is a row that was gated first and missed later.
 * `M1`'s three are the other order: the parent chose the per-cell ceiling knowing
 * which cells it declares missed, because the alternative — a ceiling at 1.55,
 * above the bed's own worst cell — is a clause that passes and says nothing. The
 * worst cell on the declared bed reads 1.5155 and the ruling took 1.40, so the
 * thinnest surface in the bed and two of its siblings enter this list on the day
 * the row enters the file. That is the shape W29 used at the 27 tables' own
 * adoption and it is the only honest one: a bound is worth having when it is
 * stated against the spread a fit leaves rather than the median it hits.
 *
 * The lever is named with each: a retention conditioned on the SURFACE rather
 * than one constant per document (charter Decision Log 3 (b), claims §5.164 §8
 * (a)). `1 − sizedAlpha` falls as the span rises, so one multiplicative constant
 * buys a larger relative chroma gain on a thinner plate; span 32 is the thinnest
 * the bed carries and it is where the overshoot is.
 */
const MISSED_27_ROWS: Readonly<Record<string, MissedRow>> = {
  "dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-27.0-1x-light-standard-glass0.5 :: ssimMean": { measured: 0.89539, bound: "≥ 0.9" },
  "dom / holdout / checkerboard__rrect-lg__rest / apple-macos-27.0-1x-light-standard-glass0.5 :: ssimMean": { measured: 0.88421, bound: "≥ 0.9" },
  // The two DARK `dom` rows below are unmoved to the fifth decimal by W31's
  // chroma operator, and that is the CSS tier's decline rather than the operator
  // failing: this tier carries nothing of it (claims §5.164 §5). Their siblings
  // on the WebGPU tier cleared — 0.21531 → 0.14655 and 0.21341 → 0.14505 at the
  // same material — which is what left these two here.
  //
  // 2026-09-21, W31 G3c (review closure; claims §5.164 §13, finding N18): this
  // comment sat one entry LOWER, above the reduced-transparency `ssimOutside`
  // row, which it says nothing about. It is moved to the rows it describes and
  // names both of them.
  "dom / holdout / photo__rrect-lg__rest / apple-macos-27.0-1x-dark-standard-glass0.5 :: oklabDeltaEP95": { measured: 0.20095, bound: "≤ 0.18" },
  "dom / holdout / photo__rrect-lg__rest / apple-macos-27.0-1x-light-reduced-transparency-glass0.5 :: ssimOutside": { measured: 0.82698, bound: "≥ 0.83" },
  "dom / holdout / photo__rrect-lg__rest / apple-macos-27.0-2x-dark-standard-glass0.5 :: oklabDeltaEP95": { measured: 0.19474, bound: "≤ 0.19" },
  // W31 M1's three, recorded at adoption. All three are `photo__rrect-sm` — span
  // 32, the thinnest surface the bed carries — and the lever that closes them is
  // a retention conditioned on the surface rather than one constant per document.
  "texture / validation / photo__rrect-sm__inactive / apple-macos-27.0-1x-light-standard-glass0.5 :: chromaStructureRatioR": { measured: 1.53911, bound: "≤ 1.40" },
  "texture / validation / photo__rrect-sm__inactive / apple-macos-27.0-2x-light-standard-glass0.5 :: chromaStructureRatioR": { measured: 1.46115, bound: "≤ 1.40" },
  "texture / validation / photo__rrect-sm__rest / apple-macos-27.0-2x-light-standard-glass0.5 :: chromaStructureRatioR": { measured: 1.44950, bound: "≤ 1.40" },
  // W32 G1's one (claims §5.168), and M2's first since adoption. The outer
  // shadow's exterior is fitted and the receded documents stop drawing one at
  // all, and this cell's `interiorStdDevWeb` moves 0.0184262 → 0.018154, which
  // carries the CUMULATIVE delta from W31's pre-fit generation (0.0186722) past
  // 2 %: −1.317 % → −2.775 %. The cell is span 32 INACTIVE, the thinnest caster
  // the bed carries and the pose whose whole exterior this wave removed.
  //
  // 2026-09-21, W32 G1 review closure (claims §5.168 §10, finding B-2): this
  // comment said the mechanism was "the silhouette extractor — which thresholds
  // the render against its background — takes a different set of edge pixels",
  // and the first value was transcribed as 0.018432. **The mask did not move
  // and it is not web-derived**: `cli/measure.ts` takes `const interior =
  // nativeSil`, and over the 726 rows this gate superseded and re-read,
  // `silhouetteAreaNative` moved on 0 (`results/2026-09-21-w32-g1-shadow-fit/
  // b2-mask.py`); on this cell the native area, the web area and the declared
  // region are all 2000 with an IoU of 1 before and after. What moved is the
  // render's values under a fixed mask. The candidate mechanism — untested — is
  // the optics pass compositing `shadowAlpha · (1 − coverage)` into the
  // antialiased contour ring INSIDE the declared region, which would put the
  // effect where that ring is the largest fraction of the region, the thinnest
  // span. Both percentages above were computed from the right values and do not
  // move. The tracker carries the measurement that would test the hypothesis,
  // and beside it the half that is a ruling the user owns: M2's reference
  // generation is frozen at W31's pre-fit while its subject keeps moving.
  "texture / validation / photo__rrect-sm__inactive / apple-macos-27.0-1x-light-standard-glass0.5 :: interiorStdDevStructureDelta": { measured: 0.02775, bound: "≤ 0.02" },
};

/*
 * **The fifteen span-44 texture cells W30 G3 added are gone again, and that
 * round trip is the point** (W30 G3b, claims §5.159b). They entered because the
 * fitted σ law reached a width at which the optics pass's shadow falloff
 * returned NaN inside a thin caster, leaving a strip of the surface undrawn:
 * the predicate's own arms then refused those cells — a drawn silhouette in
 * several pieces, with holes — and the gate lost 170 declaration-conformance
 * rows to it. W30 G3b fixed the shader and re-read the bed at the same material,
 * and the list is back to the 68 entries it held at 0.19.0, with every one of
 * the fifteen returning to a gated shape row rather than being written off. The
 * list is derived from the artifact by the case below on every run, so neither
 * the going nor the coming was typed.
 *
 * 2026-09-21, W31 G3c (review closure; claims §5.164 §13, addendum H): the
 * version this names and the one claims §5.164 §7 names are BOTH right and read
 * as a disagreement. 68 is the count at 0.19.0, the count 0.20.0 shipped — W30
 * G3's 83 lived and died inside W30, so it never reached a release — and the
 * count here. The excursion was 68 → 83 → 68 within one wave; the releases on
 * either side of it are both 68. Whichever version a later reader reaches for,
 * the number is the same, and it is the same 68 CELLS and not merely 68 of them.
 */
/*
 * 2026-09-21, W32 G1 (claims §5.168): **sixty-SEVEN since the exterior fit**, and
 * the one that left did so by being FIXED rather than by being excused. The list
 * is the machine's output at the read and is transcribed from it, as this file's
 * convention requires.
 *
 * `dom / calibration / checkerboard__capsule-button__rest /
 * apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5` was here because
 * the CSS tier's silhouette on that cell drew in TWO pieces: `silhouetteBodiesWeb`
 * read 2 against the predicate's ≤ 1. The outer shadow's outset fell 3.10 → 0.50
 * CSS px and the tier's `box-shadow` fell with it, the silhouette closed into one
 * body, and the cell JOINS the gated bed — so the increased-contrast profile's
 * `dom` shape rows gate 7 cells where they gated 6, and the count above is
 * derived from this list rather than typed, which is why one deletion moves both.
 *
 * 2026-09-21, W32 G1 review closure (claims §5.168 §10, finding B-3): this
 * comment said the cell "did not clear 95 % of its declared region", and that
 * arm was never the one failing. Off the two generations the area arm reads
 * 4756 → 4755 of a 4872 px region against a threshold of 4628.4 — clear before
 * and after, and it moved the wrong way — while `silhouetteBodiesWeb` reads
 * 2 → 1. The count, the cell and the consequence are unchanged; the arm named
 * beside them was wrong, and commit `0e03f189`'s body carries the same slip
 * where it cannot be amended.
 *
 * Its macOS 26.5 sibling one line up is unmoved and cannot move: that document is
 * frozen. The two beds reading the same scene at different conditioning is the
 * generation difference, visible.
 */
const PREDICATE_EXCLUDES = [
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / checkerboard__capsule-button__rest / apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-dark-standard",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-2x-dark-standard",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
  "dom / calibration / checkerboard__rrect-md__rest / apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "dom / calibration / light-solid__capsule-button__rest / apple-macos-27.0-1x-light-standard-glass0.5",
  "dom / calibration / light-solid__capsule-button__rest / apple-macos-27.0-2x-light-standard-glass0.5",
  "dom / calibration / light-solid__rrect-md__rest / apple-macos-27.0-1x-light-standard-glass0.5",
  "dom / calibration / light-solid__rrect-md__rest / apple-macos-27.0-2x-light-standard-glass0.5",
  "dom / calibration / photo__capsule-button__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "dom / calibration / photo__capsule-button__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
  "dom / calibration / photo__rrect-md__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "dom / calibration / photo__rrect-md__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-reduced-transparency",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
  "dom / holdout / hc-text__capsule-button__rest / apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "dom / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "dom / holdout / photo__rrect-lg__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "dom / holdout / photo__rrect-lg__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "dom / validation / impulse__capsule-button__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "dom / validation / impulse__capsule-button__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
  "texture / calibration / checkerboard__capsule-button__rest / apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-2x-dark-standard",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
  "texture / calibration / checkerboard__rrect-md__rest / apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "texture / calibration / checkerboard__toolbar-group__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / dark-solid__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / calibration / dark-solid__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "texture / calibration / dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "texture / calibration / dark-solid__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "texture / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-1x-dark-standard",
  "texture / calibration / dark-solid__rrect-md__rest / apple-macos-26.5-2x-dark-standard",
  "texture / calibration / light-solid__capsule-button__rest / apple-macos-27.0-1x-light-standard-glass0.5",
  "texture / calibration / light-solid__capsule-button__rest / apple-macos-27.0-2x-light-standard-glass0.5",
  "texture / calibration / light-solid__rrect-md__rest / apple-macos-27.0-1x-light-standard-glass0.5",
  "texture / calibration / light-solid__rrect-md__rest / apple-macos-27.0-2x-light-standard-glass0.5",
  "texture / calibration / photo__capsule-button__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "texture / calibration / photo__capsule-button__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
  "texture / calibration / photo__rrect-md__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "texture / calibration / photo__rrect-md__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
  "texture / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-increased-contrast",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-26.5-1x-light-reduced-transparency",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
  "texture / holdout / hc-text__capsule-button__rest / apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "texture / holdout / hc-text__rrect-md__rest / apple-macos-26.5-2x-light-standard",
  "texture / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / holdout / mid-dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "texture / holdout / photo__rrect-lg__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "texture / holdout / photo__rrect-lg__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-dark-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-1x-light-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-dark-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-26.5-2x-light-standard",
  "texture / validation / impulse__capsule-button__rest / apple-macos-27.0-1x-dark-standard-glass0.5",
  "texture / validation / impulse__capsule-button__rest / apple-macos-27.0-2x-dark-standard-glass0.5",
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
    readonly web: {
      readonly engine: string;
      readonly renderer: string;
      /**
       * How the capture was taken, including the profile document and its hash
       * (W29 G3b reads it — `atAShippedDocument`). Part of the key, so a refit
       * appends a generation beside the rows read at the old document; W30 G1
       * moves the superseded generation to `results/superseded/` once the refit
       * has landed, so the working file carries one generation per profile.
       */
      readonly capturePath: string;
    };
  };
  readonly fixtureSet: string;
  /** The scene's declared pose (W28 G4). Absent on a row written before the label existed. */
  readonly state?: string;
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
const MATRIX_FILE = readJson<ResultMatrix>(MATRIX_PATH);
/**
 * The scene declaration, read here rather than inside one `describe`, because two
 * of the drops below are stated over it.
 */
const SCENE_DECLARATION = readJson<{
  readonly scenes: readonly { readonly id: string; readonly state: string }[];
  readonly split: Record<string, readonly string[]>;
}>(resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple", "scenes.json"));
/** Every scene the declaration poses inactive — the window-activation axis's far end. */
const INACTIVE_SCENES = new Set(
  SCENE_DECLARATION.scenes.filter((scene) => scene.state === "inactive").map((scene) => scene.id),
);

/**
 * The gated bed: the matrix file minus its `probe` rows, and minus the inactive
 * pose on every set.
 *
 * Since W25 the canonical matrix carries the probe set beside the frozen bed:
 * the harness captures it routinely and the fits and the claims read it, but it
 * is gated by nothing (W25 Decision Log 3 (e), claims §5.113). Every count,
 * partition, bound, floor and conditioning exclusion in this file is stated over
 * a cell of the frozen bed, so the set the file reads has to be the frozen bed
 * and the drop has to happen once, here, rather than in each of the two dozen
 * places that select from it. The guard at the foot of the file is what keeps
 * this from becoming a hole: it asserts that nothing gated ever sees a probe
 * row, in both directions.
 *
 * W28 G4 adds the second drop, and it is an axis rather than a set. The canonical
 * matrix now carries the window-inactive pose beside the active one (claims
 * §5.148), across `calibration`, `validation` and `probe` alike, so the frozen bed
 * this file gates is no longer "the matrix minus one set" unless the pose is named
 * too. **No inactive floor may be adopted** — W27 Decision Log 13 rules that a
 * regression floor needs a regime frozen at the seventeen-run bar and the inactive
 * bed is at the probe bar of seven, which is also why `fitted-endpoint.json`
 * records `adoptsNoFloor` — and every adopted bound, floor, partition count and
 * conditioning exclusion in this file was measured on the active pose. Letting the
 * inactive rows into any of them would silently restate an active-pose promise over
 * a different material. The drop is by the declared pose, never by naming cells:
 * a list of inactive scene ids here would need a line per cell per profile per
 * tier, and every new inactive scene would join the gate by default, which is the
 * failure this axis-shaped exclusion cannot have.
 */
/**
 * The short content hash `capture-web` puts in a cell's `capturePath` for each
 * committed profile document, as the documents stand right now.
 *
 * Twelve hex characters of SHA-256 over the file, which is
 * `scripts/material-profile-file.ts`'s own construction. Derived here rather
 * than transcribed for the reason every hash in this file is: a number a person
 * retypes after a refit is a number that goes stale silently, and this one
 * decides which rows the gate reads.
 */
const SHIPPED_DOCUMENT_HASHES = new Map(
  readdirSync(resolve(PACKAGE_ROOT, "profiles"))
    .filter((file) => file.endsWith(".json"))
    .map((file) => {
      const path = `packages/calibration/profiles/${file}`;
      const hash = createHash("sha256")
        .update(readFileSync(resolve(PACKAGE_ROOT, "profiles", file)))
        .digest("hex")
        .slice(0, 12);
      return [path, hash] as const;
    }),
);

/**
 * Was this row captured at a profile document that is committed and unchanged?
 *
 * **A guard, no longer a generation filter** (W29 G3b; narrowed by W30 G1). A
 * cell's key contains its `capturePath`, and the `capturePath` names the material
 * profile document and its content hash — so a refit that moves a document does
 * not overwrite the rows read at the old one, it APPENDS a second generation
 * beside them, because a recorded number is never rewritten.
 *
 * Until W30 G1 both generations lived in the working file and this predicate was
 * what decided which of them shipped. They no longer do: the superseded
 * generation is moved, byte for byte, to `results/superseded/<document-sha>.json`
 * as soon as the refit that superseded it has landed (Decision Log 1 (d),
 * contract X7, claims §5.157), so `results/matrix.json` holds one generation per
 * profile and "which generation ships" is a name rather than a computation. Over
 * the split file this predicate drops nothing, and that is the point: the rows it
 * sifted are not here to sift.
 *
 * It stays, at full strength, because sifting was never its only job. It is the
 * guard that a profile document edited WITHOUT a re-read empties its own profile
 * out of every bound, floor and count — loudly, rather than gating a promise
 * against a bed nobody captured. W30 leans on exactly that: the macOS 26.5
 * documents' bytes are an input to all 1,107 frozen rows, so a re-recorded digest
 * or a history comment in one of them would retire half the gated bed, and this
 * is what makes that failure visible instead of silent.
 *
 * A row whose `capturePath` names no document at all — `materialProfile=renderer
 * defaults` — is not a bed row and never was; it would be a capture taken at the
 * renderer's untuned defaults, which is not the material any bound is stated on.
 */
function atAShippedDocument(cell: Cell): boolean {
  const clause = /materialProfile=(\S+) sha256:([0-9a-f]{12})/.exec(cell.key.web.capturePath);
  if (clause === null) return false;
  return SHIPPED_DOCUMENT_HASHES.get(clause[1] ?? "") === clause[2];
}

const MATRIX: ResultMatrix = {
  ...MATRIX_FILE,
  cells: MATRIX_FILE.cells.filter(
    (cell) =>
      cell.fixtureSet !== "probe" &&
      cell.state !== "inactive" &&
      !INACTIVE_SCENES.has(cell.key.sceneId) &&
      atAShippedDocument(cell),
  ),
};

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

/*
 * W26 G3a's `W26_CORRECTED_SILHOUETTE_IOU` stood here and is DELETED (W26 G3, the
 * landing; claims §5.126). It named the three cells where the committed matrix
 * and the shipped instrument disagreed, because G3a corrected `silhouetteIoU` to
 * the decidable region in `cli/measure.ts` while the matrix was still the 0.14.0
 * bed's capture (claims §5.124; W26 Decision Log 8). Its own test asserted the
 * entries were STILL NEEDED and went red the moment the canonical rebuild carried
 * the corrected reading, which is the only ending the construct was allowed to
 * have; that rebuild is this landing's and the three cells now read 0.97319,
 * 0.99980 and 0.98289 from the matrix itself. The referee checked the whole
 * column rather than the three: 423 of 423 cells whose captures did not move
 * agree with `g3a/recompute-rows.json` to five decimals, and none reads a
 * pre-correction value.
 */

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
// W31 M1 / M2 — the body's chroma, read from a cut regenerated at the adopting
// gate (W31 Decision Log 3 (a), claims §5.165 §1). The rows themselves are at
// the foot of this file; what lives here is the reading they and the
// `MISSED_27_ROWS` derivation both need.
// ---------------------------------------------------------------------------

interface ChromaCutCell {
  readonly profile: string;
  readonly scene: string;
  readonly set: string;
  readonly tier: "texture" | "dom";
  readonly scheme: "light" | "dark";
  readonly scale: number;
  readonly pose: "active" | "inactive";
  readonly chromaStructureRatioNative: number;
  readonly chromaStructureRatioWeb: number;
  readonly interiorStdDevWeb: number;
  readonly R: number;
  readonly interiorStdDevWebPreFit: number;
  readonly structureDeltaFraction: number;
}

interface ChromaCut {
  readonly mode: string;
  readonly atDocuments: string;
  readonly withHoldout: boolean;
  readonly tier: string;
  readonly renderer: string;
  readonly sets: readonly string[];
  readonly preFitGeneration: Readonly<
    Record<string, { readonly activeDocumentSha256: string; readonly file: string }>
  >;
  readonly beds: Readonly<
    Record<
      string,
      {
        readonly cells: number;
        readonly median: number;
        readonly min: number;
        readonly max: number;
        readonly worstStructureDeltaFraction: number;
      }
    >
  >;
  readonly cells: readonly ChromaCutCell[];
}

/**
 * The cut, written by `chroma-cut.py` in the same evidence directory, at the
 * gate that adopts the rows reading it.
 *
 * **Why a path and not a literal, and why a path is not enough.** B1 above reads
 * W30 G0's `shadow-cut.json`, and W31 G1's review closure found what that shape
 * costs when the reading gate is not the declaring one: a cut committed at an
 * earlier gate is a SNAPSHOT of the matrix, so a bound stated over it asserts
 * frozen numbers and can never fail (claims §5.162 §9). Decision Log 3 (a) rules
 * the cut regenerated here; the case below closes the other half by re-deriving
 * every figure in it from `results/matrix.json` and from the superseded files it
 * names, so a read that moves a row moves these rows whether or not anyone
 * re-runs the script.
 */
const CHROMA_CUT = readJson<ChromaCut>(
  // 2026-09-21, W32 G1 (claims §5.168): re-pointed at this wave's directory,
  // which is the rule above being obeyed rather than an exception to it. W32 G1
  // re-read the whole macOS 27 bed at fitted shadow documents, so W31 G4's cut
  // became a snapshot of a generation the working file no longer holds — the
  // exact failure the paragraph above describes — and the case that re-derives
  // every figure from `results/matrix.json` is what caught it. The script is
  // W31 G4's `chroma-cut.py`, copied byte for byte and re-run.
  resolve(PACKAGE_ROOT, "results", "2026-09-21-w32-g1-shadow-fit", "chroma-cut.json"),
);

/**
 * The four beds M1 and M2 are stated over, with the scheme each reads at.
 *
 * The two macOS 27 accessibility profiles are deliberately absent. They inherit
 * the light document and then stand the retention DOWN entirely under their
 * occlusion lift (W31 Decision Log 3 (d), claims §5.164 §13), so their body is
 * byte for byte what 0.20.0 drew and a chroma row over them would be a promise
 * about a material this wave did not change. What they need instead is a
 * retention of their own, measured — deferred, with the evidence, to a later
 * chromatic wave (Decision Log 3 (c)).
 */
const CHROMA_BED_PROFILES: Readonly<Record<string, "light" | "dark">> = {
  "apple-macos-27.0-1x-light-standard-glass0.5": "light",
  "apple-macos-27.0-2x-light-standard-glass0.5": "light",
  "apple-macos-27.0-1x-dark-standard-glass0.5": "dark",
  "apple-macos-27.0-2x-dark-standard-glass0.5": "dark",
};

/** The metric name the misses are keyed under, in `MISSED_27_ROWS`'s own shape. */
const CHROMA_METRIC = "chromaStructureRatioR";

/**
 * M2's, added 2026-09-21 by W32 G1 (claims §5.168).
 *
 * **M2 gains the recorded-miss path M1 has had since adoption, and the BOUND
 * does not move.** M2 was adopted with no miss, so it had no path; W32 G1 is the
 * first wave to move its subject without touching its operator and it produced
 * one. Every cell that moved by more than half a percent is inactive, thin, or
 * both.
 *
 * *(2026-09-21, W32 G1 review closure; claims §5.168 §10, finding B-2. This
 * paragraph said `interiorStdDevWeb` "is read over the EXTRACTED silhouette,
 * and the silhouette extractor thresholds the render against its background".
 * It is read over the NATIVE silhouette — `cli/measure.ts` is `const interior =
 * nativeSil`, deliberately, because a web-derived mask moves as the web side is
 * tuned — and `silhouetteAreaNative` moved on 0 of the 726 rows this gate
 * re-read. The mask is not the mechanism; the values under it are what moved.
 * The untested candidate is the optics pass compositing the shadow into the
 * antialiased contour ring inside the declared region, and the tracker carries
 * the measurement that would test it.)*
 *
 * The 2 % is untouched and the miss is named, which is the difference between
 * recording and widening: `chromaStructureMisses()` derives the failures from the
 * same cut M2 reads, the owner case asserts that the derived set IS the recorded
 * set, and a cell that starts missing or stops missing fails it either way.
 */
const CHROMA_STRUCTURE_METRIC = "interiorStdDevStructureDelta";

/** M1's two clauses (W31 Decision Log 3 (a), ruled). */
const CHROMA_MEDIAN_MIN = 0.8;
const CHROMA_MEDIAN_MAX = 1.2;
const CHROMA_CELL_MIN = 0.6;
const CHROMA_CELL_MAX = 1.4;

/** M2's clause: `interiorStdDevWeb` within 2 % of the pre-fit generation's. */
const CHROMA_STRUCTURE_TOLERANCE = 0.02;

const chromaKey = (cell: ChromaCutCell): string =>
  `${cell.tier} / ${cell.set} / ${cell.scene} / ${cell.profile}`;

/**
 * Which cells of the cut fail M1's per-cell clause — the same derivation the
 * `MISSED_27_ROWS` owner runs and the same one M1 excuses, so a miss can only be
 * recorded and never widened away.
 */
const chromaPerCellMisses = (): readonly ChromaCutCell[] =>
  CHROMA_CUT.cells.filter((cell) => cell.R < CHROMA_CELL_MIN || cell.R > CHROMA_CELL_MAX);

/**
 * Which cells of the cut fail M2's per-cell clause — the same shape as
 * `chromaPerCellMisses` above and for the same reason (W32 G1, claims §5.168).
 */
const chromaStructureMisses = (): readonly ChromaCutCell[] =>
  CHROMA_CUT.cells.filter(
    (cell) => Math.abs(cell.structureDeltaFraction) > CHROMA_STRUCTURE_TOLERANCE,
  );

// ---------------------------------------------------------------------------

describe("the adopted fidelity gate (claims §5, adopted 2026-08-26 / -29 / -30)", () => {
  it("reads the matrix at the schema the build writes, and pins both numbers", () => {
    // Corrected 2026-09-20 (W30 G1 review closure, c9a §5.157 §10): this case's
    // title and comment still described the interregnum wave Decision Log 15
    // ruling 3 opened — the committed matrix held at schema 4, the build moved on
    // to schema 5, whose shape and material figures are measured under a
    // *bounded* silhouette and are therefore not the same quantities. The post-W8
    // pass re-read the bed and closed it; the two assertions below have both read
    // 5 since, under a title that said they differed.
    //
    // Both numbers stay pinned, which is what the case is for: equal today, and a
    // future bump that opens the gap again has to move this file and re-verify the
    // tables above against the new instrument rather than assume they survived it.
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
    expect(GATED_PROFILES).toHaveLength(GATED_PROFILE_COUNT);

    for (const { profileKey, cells: counted } of GATED_PROFILES) {
      for (const tier of ["texture", "dom"] as const) {
        const cells = cellsOf(profileKey, tier);
        expect(cells, `${profileKey} / ${tier}`).toHaveLength(counted[tier]);
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
        const noShape = NO_SHAPE_AXIS_SCENES[profile.profileKey]?.[tier] ?? [];

        // The shape rows gate fewer cells than the perceptual rows, for named
        // reasons only. Derived from the names so a new such scene cannot arrive
        // unnoticed and shrink the gate.
        expect(shapeCells).toHaveLength(profile.cells[tier] - noShape.length);
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
              ? profile.cells[tier] - noShape.length - predicateExcludedCount(profile.profileKey, tier)
              : profile.cells[tier];
          expect(
            applicable,
            `${tier} / ${metric}: the gate must cover every applicable cell`,
          ).toHaveLength(expected);
          expect(applicable.length, `${tier} / ${metric}: nothing left to gate`).toBeGreaterThan(0);

          for (const cell of applicable) {
            const measured = reading(cell, axis, metric);
            // A 27 row the refit missed: named in `MISSED_27_ROWS`, claimed
            // UNMET, and enforced by nothing until the user rules. The case that
            // owns that list is what keeps it from growing unnoticed.
            if (MISSED_27_ROWS[`${name(cell)} :: ${metric}`] !== undefined) continue;
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
      const noShape = NO_SHAPE_AXIS_SCENES[profileKey]?.dom ?? [];

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
     * the degenerate cell is asserted to be excluded by what the bed says about
     * it — if a future bed resolves `dark-solid__rrect-md__rest` properly, this
     * fails and the cell goes back to being gated, which is the correct outcome
     * and not a maintenance burden to route around.
     *
     * **W23 G2 (claims §5.104): the measurement moved and the exclusion changed
     * construct.** Through 0.11.0 the cell had a shape axis of two degenerate
     * samples — 205 px of a 15 024 px region at 1x, 849 of 60 064 at 2x, in six
     * to nine pieces — and the predicate refused it. On the landed bed the CSS
     * tier's body sits closer to the dark solid it is over and the luminance-
     * delta extractor recovers NOTHING, so `cli/measure.ts` writes the cell with
     * no shape axis and no interior ratio at all. It is now excluded by absence
     * and named in `NO_SHAPE_AXIS_SCENES`, which is a stronger statement of the
     * same fact, and this test asserts that fact rather than the old one.
     *
     * And the extension must not have quietly emptied the row: it is asserted to
     * still refuse dom cells on this profile by a web-side arm, and a
     * well-conditioned dark cell is asserted to still be gated on its ratio.
     */
    const degenerate = MATRIX.cells.filter(
      (cell) =>
        cell.tier === "dom" &&
        cell.key.sceneId === "dark-solid__rrect-md__rest" &&
        (DARK_PROFILES as readonly string[]).includes(cell.key.profileKey),
    );
    expect(degenerate, "the cell the extension exists for").toHaveLength(DARK_PROFILES.length);

    for (const cell of degenerate) {
      // Excluded, and excluded because the extractor recovered nothing at all —
      // not a borderline miss of the floor, and not a decision about the scene.
      expect(cell.shape, `${name(cell)}: no silhouette the extractor could find`).toBeUndefined();
      expect(
        cell.coherence?.interiorLevelRatioGpuOverCss,
        `${name(cell)}: and so no interior to sample either`,
      ).toBeUndefined();
      expect(
        [...(NO_SHAPE_AXIS_SCENES[cell.key.profileKey]?.dom ?? [])],
        `${name(cell)}: named where the reason lives`,
      ).toContain(cell.key.sceneId);
      // The GPU tier still resolves the same scene, which is what makes this a
      // property of the CSS tier's own agreement rather than of the scene.
      const twin = MATRIX.cells.find(
        (candidate) =>
          candidate.tier === "texture" &&
          candidate.key.sceneId === cell.key.sceneId &&
          candidate.key.profileKey === cell.key.profileKey,
      );
      expect(twin?.shape, `${name(cell)}: the texture twin still carries a shape axis`).toBeDefined();
    }

    // The extension itself must still bite on these profiles: a dom cell the
    // native-only predicate would have passed and the web-side arms refuse.
    for (const profileKey of DARK_PROFILES) {
      const refusedOnTheWeb = cellsOf(profileKey, "dom").filter((cell) => {
        if (cell.shape === undefined || isWellConditioned(cell)) return false;
        const at = (metric: string): number => reading(cell, "shape", metric);
        return (
          at("silhouetteAreaNative") >= WELL_CONDITIONED_AREA_RATIO * at("componentRegionArea") &&
          at("silhouetteBodiesNative") <= at("componentRegionBodies")
        );
      });
      expect(
        refusedOnTheWeb.length,
        `${profileKey}: the web-side arms must still refuse a cell the native arms pass`,
      ).toBeGreaterThan(0);
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

/**
 * W20 — the declaration-conformance bound on the texture tier (claims §5.84–§5.86; W20
 * Decision Log 2 ruling 2, adopted at the landing).
 *
 * Every other shape row bounds both silhouettes to the declared geometry, and a surface drawn
 * LARGER than its declaration fills that region and reads perfect — which is how the GPU tier
 * drew every capsule with its corner clamped to 0.327 of its height for nineteen waves while the
 * axis read IoU 1.000 (§5.83). These two rows read the tier's own coverage over a transparent
 * page with no region at all, against the declaration. The bound is the raster's antialiased
 * band: one device pixel of contour, and an IoU that band cannot take under 0.99 on the smallest
 * shape the bed carries (the toolbar's three circles read 0.9969 at 2x). The defect read
 * 0.9545 / 3.16 px on a capsule and 0.8682 / 3.16 px on the toolbar; a uniform one-pixel
 * oversize reads about 0.936 (§5.84 §7).
 *
 * Every texture-tier cell that carries a shape axis must carry the rows: a canonical rebuild that
 * forgot `--alpha` would otherwise pass with nothing to gate. The dom tier refuses the reading by
 * its interior alpha (§5.84 §7) and is not gated here.
 */
describe("the macOS 27 tables, declared before the refit's read (W29 Decision Log 4 (a))", () => {
  it("declares exactly the six profiles the user ruled, and not the confounded one", () => {
    expect(DECLARED_27_PROFILES.map((profile) => profile.profileKey).sort()).toEqual(
      [
        "apple-macos-27.0-1x-dark-standard-glass0.5",
        "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
        "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
        "apple-macos-27.0-1x-light-standard-glass0.5",
        "apple-macos-27.0-2x-dark-standard-glass0.5",
        "apple-macos-27.0-2x-light-standard-glass0.5",
      ],
    );
    for (const key of UNBOUNDED_27_PROFILES) {
      expect(
        DECLARED_27_PROFILES.map((profile) => profile.profileKey),
        `${key}: ruled to carry no table this wave`,
      ).not.toContain(key);
    }
    // Every declared key parses as a 27 key at the system default slider
    // position, which is the bed Decision Log 3 (a) captured.
    for (const { profileKey } of DECLARED_27_PROFILES) {
      expect(profileKey.startsWith("apple-macos-27.0-"), profileKey).toBe(true);
      expect(profileKey.endsWith("-glass0.5"), profileKey).toBe(true);
    }
  });

  it("holds every 27 table at its 26.5 twin's values, row for row", () => {
    // The content of Decision Log 4 (a). The tables are aliases, so this reads
    // as a tautology today — and that is the guarantee: the case fails the day
    // somebody breaks one out into a literal without saying so, which is the
    // only way a 27 bound may ever move.
    for (const profile of DECLARED_27_PROFILES) {
      for (const tier of ["texture", "dom"] as const) {
        const ruled = RULED_EQUAL_TO_26_5[profile.names[tier]];
        expect(ruled, `${profile.names[tier]}: no 26.5 table named as its twin`).toBeDefined();
        expect(profile[tier], `${profile.profileKey} / ${tier}`).toEqual(ruled);
      }
    }
    expect(Object.keys(RULED_EQUAL_TO_26_5)).toHaveLength(2 * DECLARED_27_PROFILES.length);
  });

  it("adopts no regression floor on any 27 profile (acceptance clause 4)", () => {
    // The 27 bed is published at the seven-run probe bar and a floor needs the
    // seventeen-run freeze bar. A floor here would pin a precision the bed does
    // not carry, so the rule is enforced rather than remembered.
    expect(
      Object.keys(REGRESSION_FLOORS).filter((key) => key.includes("apple-macos-27.0-")),
      "no 27 profile may carry a regression floor in W29",
    ).toEqual([]);
  });

  it("names every 27 row the refit missed, and nothing it did not", () => {
    /*
     * The list's owner. It is derived here from the artifact and compared to the
     * constant in BOTH directions, which is the only thing that makes recording
     * a miss different from excusing one: a row that starts missing joins this
     * failure, and a row that stops missing joins it too, so the set can only be
     * changed in a commit that says why.
     *
     * Nothing about the VALUE is asserted. That is deliberate and it is what
     * separates this from `REGRESSION_FLOORS` — acceptance clause 4 adopts no 27
     * floor, so there is no number here for a later run to be held to.
     */
    const missed: string[] = [];
    for (const profile of DECLARED_27_PROFILES.filter(transcribed27)) {
      for (const tier of ["texture", "dom"] as const) {
        for (const [axis, metric, comparison, threshold] of profile[tier]) {
          for (const cell of cellsOf(profile.profileKey, tier)) {
            if (axis === "shape" && (cell.shape === undefined || !isWellConditioned(cell))) continue;
            const measured = reading(cell, axis, metric);
            const fails = comparison === "≥" ? measured < threshold : measured > threshold;
            if (fails) missed.push(`${name(cell)} :: ${metric}`);
          }
        }
      }
    }
    /*
     * **W31 M1's misses join the same derivation** (2026-09-21, Decision Log
     * 3 (a); claims §5.165 §1).
     *
     * The loop above walks the transcribed per-cell tables, and M1 is not one of
     * them — it is stated over a cut and over a bed that includes the INACTIVE
     * pose, which `MATRIX` drops. Left out, its three recorded misses would make
     * this case red in one direction (entries nothing derives) and, worse, a
     * fourth cell crossing 1.40 later would be silent. So the derivation is
     * extended rather than the list exempted: the chroma row's failures are
     * computed from the same cut M1 reads and appended here, which keeps the one
     * property this case exists for — a row that starts missing and a row that
     * stops missing both fail it.
     */
    for (const cell of chromaPerCellMisses()) {
      missed.push(`${chromaKey(cell)} :: ${CHROMA_METRIC}`);
    }
    // M2's, on the same argument (W32 G1, claims §5.168): its clause is per cell
    // over the same cut, so its failures are derived here rather than excused.
    for (const cell of chromaStructureMisses()) {
      missed.push(`${chromaKey(cell)} :: ${CHROMA_STRUCTURE_METRIC}`);
    }
    expect(missed.sort(), "the 27 rows that miss their declared bound").toEqual(
      Object.keys(MISSED_27_ROWS).sort(),
    );

    // And each chroma miss's recorded reading is the cut's own, to five decimals,
    // on the same rule as the tabled rows below: the prose beside the list cannot
    // drift from the artifact it describes.
    for (const cell of chromaPerCellMisses()) {
      const row = MISSED_27_ROWS[`${chromaKey(cell)} :: ${CHROMA_METRIC}`];
      expect(row, `${chromaKey(cell)}: a chroma miss with no recorded reading`).toBeDefined();
      expect(cell.R, `${chromaKey(cell)} :: ${CHROMA_METRIC}`).toBeCloseTo(
        row?.measured ?? Number.NaN,
        5,
      );
    }

    for (const cell of chromaStructureMisses()) {
      const row = MISSED_27_ROWS[`${chromaKey(cell)} :: ${CHROMA_STRUCTURE_METRIC}`];
      expect(row, `${chromaKey(cell)}: a structure miss with no recorded reading`).toBeDefined();
      expect(
        Math.abs(cell.structureDeltaFraction),
        `${chromaKey(cell)} :: ${CHROMA_STRUCTURE_METRIC}`,
      ).toBeCloseTo(row?.measured ?? Number.NaN, 5);
    }

    // Every recorded reading is the one the sealed read took, to five decimals —
    // so the prose beside the list cannot drift from the artifact it describes.
    for (const profile of DECLARED_27_PROFILES.filter(transcribed27)) {
      for (const tier of ["texture", "dom"] as const) {
        for (const [axis, metric] of profile[tier]) {
          for (const cell of cellsOf(profile.profileKey, tier)) {
            const row = MISSED_27_ROWS[`${name(cell)} :: ${metric}`];
            if (row === undefined) continue;
            expect(reading(cell, axis, metric), `${name(cell)} :: ${metric}`).toBeCloseTo(
              row.measured,
              5,
            );
          }
        }
      }
    }
  });

  it("gates every 27 row it finds, and refuses one it never declared", () => {
    const rows = MATRIX.cells.filter((cell) => cell.key.profileKey.startsWith("apple-macos-27.0-"));
    const declared = new Set(DECLARED_27_PROFILES.map((profile) => profile.profileKey));
    for (const cell of rows) {
      expect(
        declared,
        `${name(cell)}: a 27 row under a key no table was declared for`,
      ).toContain(cell.key.profileKey);
    }

    // The sentinel's whole job. While a profile's counts are pending it is
    // declared and not yet gated, so the matrix must carry nothing for it; the
    // first row that lands makes this red until the counts are transcribed from
    // the canonical run, exactly as `PREDICATE_EXCLUDES` is.
    for (const profile of DECLARED_27_PROFILES) {
      if (transcribed27(profile)) continue;
      expect(
        rows.filter((cell) => cell.key.profileKey === profile.profileKey),
        `${profile.profileKey}: rows are in the matrix but its cell counts are still ` +
          `${PENDING_UNTIL_THE_27_READ} — transcribe them into DECLARED_27_PROFILES`,
      ).toHaveLength(0);
    }
  });
});

describe("W20 — declaration conformance on the texture tier", () => {
  const DECLARED_CONTOUR_MAX_PX = 1;
  const DECLARED_IOU_MIN = 0.99;
  const cells = MATRIX.cells.filter((cell) => cell.tier === "texture" && cell.shape !== undefined);

  it("carries the rows on every texture-tier cell with a shape axis", () => {
    const missing = cells
      .filter((cell) => cell.shape?.["declaredContourMaxWeb"] === undefined)
      .map(name);
    expect(missing, "cells without a conformance reading — was the rebuild run with --alpha?").toEqual([]);
    expect(cells.length).toBeGreaterThan(0);
  });

  it("holds every texture-tier cell to its declared geometry within the antialiased band", () => {
    for (const cell of cells) {
      const contour = reading(cell, "shape", "declaredContourMaxWeb");
      const iou = reading(cell, "shape", "declaredIoUWeb");
      expect(contour, `${name(cell)}: declaredContourMaxWeb = ${contour} device px`).toBeLessThanOrEqual(
        DECLARED_CONTOUR_MAX_PX,
      );
      expect(iou, `${name(cell)}: declaredIoUWeb = ${iou}`).toBeGreaterThanOrEqual(DECLARED_IOU_MIN);
    }
  });
});

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


/**
 * W25's `probe` set, and the one thing this file has to say about it.
 *
 * The set is captured by the ordinary harness run, read by fits and cited by
 * claims — and gated by nothing (W25 Decision Log 3 (e), claims §5.113). That
 * is a promise about *this file*, because this file is where the gate lives:
 * the adopted bounds, the regression floors, the conditioning exclusions and
 * the cross-tier coherence rows are all here, and every one of them is stated
 * over a cell of the frozen bed. The assertions below are that promise,
 * written so it fails the moment a probe row starts carrying a number the bed
 * is judged by — whether because a matrix was rebuilt with `--set probe` in the run, or
 * because a floor was transcribed against a probe cell's scene id.
 *
 * The direction that matters is the one that is silent. A probe row entering a
 * gated count does not look like a failure; it looks like a bed that grew.
 *
 * The cross-tier coherence rows get no assertion of their own: they are gated
 * from the matrix rather than from prose, so the matrix guard covers them.
 */
describe("the probe set is captured, and gated by nothing (W25 Decision Log 3 (e))", () => {
  const PROBE = new Set(SCENE_DECLARATION.split["probe"] ?? []);

  it("declares a probe set, so these assertions are about something", () => {
    // An empty list would make every assertion below vacuously true, which is
    // the failure mode a guard test has that the thing it guards does not.
    expect(PROBE.size).toBeGreaterThan(0);
  });

  it("puts no probe row in the gated bed, at any profile or tier", () => {
    // `cellsOf` filters by profile and tier alone — every count, partition and
    // bound in this file runs over whatever `MATRIX` holds. So the guard is that
    // `MATRIX` holds no probe row, by either name: neither the set label the
    // capture wrote nor a scene the declaration lists as probe.
    const intruders = MATRIX.cells.filter(
      (cell) => cell.fixtureSet === "probe" || PROBE.has(cell.key.sceneId),
    );
    expect(intruders.map(name)).toEqual([]);
  });

  it("drops the file's probe rows, the inactive pose and superseded generations, and nothing else", () => {
    // The other direction, and it is the one that could rot silently: the file
    // on disk now carries the probe set (W25 G4's rebuild), so the guard above
    // passes both when the drop works and when the rows were never captured.
    // Every row the drop removes must be a probe row of a declared probe scene, a
    // row of a declared inactive scene, or a row captured at a profile document
    // this repository no longer contains — and the two views must differ by
    // exactly those rows. The inactive arm is W28 G4's and the generation arm is
    // W29 G3b's; each has its own guards below. Since W30 G1 the generation arm
    // is expected to drop nothing — the superseded generation lives in
    // `results/superseded/` rather than here — and it is asserted anyway, because
    // what it guards is an edited document, not a second generation.
    const dropped = MATRIX_FILE.cells.filter((cell) => !MATRIX.cells.includes(cell));
    expect(
      dropped.every(
        (cell) =>
          (cell.fixtureSet === "probe" && PROBE.has(cell.key.sceneId)) ||
          INACTIVE_SCENES.has(cell.key.sceneId) ||
          !atAShippedDocument(cell),
      ),
    ).toBe(true);
    expect(MATRIX.cells).toHaveLength(MATRIX_FILE.cells.length - dropped.length);
  });

  it("gates only rows captured at a profile document this repository still contains", () => {
    // The generation drop, from the inside. Two things would make it a hole: a
    // hash set that resolved nothing (every row dropped, which the partition
    // above would catch loudly) and a regex that matched everything (no row
    // dropped, which nothing else would catch at all). So the mapping is
    // asserted to be non-empty and to be the thing the rows actually name.
    expect(SHIPPED_DOCUMENT_HASHES.size).toBeGreaterThan(0);
    for (const cell of MATRIX.cells) {
      expect(atAShippedDocument(cell), name(cell)).toBe(true);
    }
    // And every document the gated rows name is one of the committed profile
    // documents, at its current bytes — not merely SOME string that parsed.
    const named = new Set(
      MATRIX.cells.map(
        (cell) => /materialProfile=(\S+) /.exec(cell.key.web.capturePath)?.[1] ?? "(none)",
      ),
    );
    for (const path of named) expect([...SHIPPED_DOCUMENT_HASHES.keys()]).toContain(path);
  });

  it("names no probe scene in the conditioning predicate's exclusion list", () => {
    // `PREDICATE_EXCLUDES` must equal the machine's own output over the gated
    // bed. A probe scene named here would be an exclusion for a cell no gated
    // count ever reaches — a line that can never be re-derived, and therefore
    // one nothing could ever remove.
    const named = PREDICATE_EXCLUDES.filter((line) =>
      [...PROBE].some((sceneId) => line.includes(` / ${sceneId} / `)),
    );
    expect(named).toEqual([]);
  });

  it("floors no probe row", () => {
    // A regression floor is a promise that a measured number will not get
    // worse. Over a probe cell it would be a promise about a bed that is
    // deliberately allowed to grow and be re-captured — and floors come off by
    // fix, never by re-pinning without the user.
    const floored = Object.keys(REGRESSION_FLOORS).filter((key) =>
      [...PROBE].some((sceneId) => key.includes(` / ${sceneId} / `)),
    );
    expect(floored).toEqual([]);
  });
});

/**
 * The window-activation axis: published in the matrix, and gated by nothing
 * (W28 G4, claims §5.148; W27 Decision Log 13).
 *
 * The same promise the probe set has, for a different reason. The probe set is
 * ungated because its membership is allowed to grow and be re-captured; the
 * inactive pose is ungated because **no floor may be adopted from it at all** —
 * a regression floor needs a regime frozen at the seventeen-run bar, the inactive
 * bed stands at the probe bar of seven, and the endpoint's own
 * `fitted-endpoint.json` records `adoptsNoFloor`. Beside that, every adopted bound
 * and conditioning exclusion in this file was measured on the active pose against
 * active native fixtures; an inactive row entering one of them would restate an
 * active-pose promise over a material with no rim, no outer shadow and a different
 * response.
 *
 * As with the probe guard, the direction that matters is silent: an inactive row
 * inside a gated count does not look like a failure, it looks like a bed that
 * grew. And the exclusion is stated on the axis rather than on cells, so that a
 * scene added to the inactive bed tomorrow is outside the gate the moment it is
 * declared, rather than the moment somebody remembers to list it.
 */
describe("the inactive pose is published, and gated by nothing (W27 Decision Log 13)", () => {
  it("declares an inactive pose, so these assertions are about something", () => {
    expect(INACTIVE_SCENES.size).toBeGreaterThan(0);
  });

  it("puts no inactive row in the gated bed, at any profile or tier", () => {
    // By either name, exactly as the probe guard reads its own set: the label the
    // capture wrote onto the row, and the pose the scene declaration gives it.
    const intruders = MATRIX.cells.filter(
      (cell) => cell.state === "inactive" || INACTIVE_SCENES.has(cell.key.sceneId),
    );
    expect(intruders.map(name)).toEqual([]);
  });

  it("catches a labelled row left stale by a later edit to the declaration", () => {
    // Not two independent readings. `cell.state` was copied off this same
    // declaration at capture time, so what the comparison can find is drift in
    // time rather than disagreement between two sources: a scene re-posed in
    // `scenes.json` after its rows were measured leaves rows whose label the
    // declaration no longer supports, and the drop above would then depend on
    // which of the two names happened to be read. That is worth holding; a
    // second reading of the pose would have to come from the capture, and the
    // capture's own resolved `windowActivation` is checked on the publishing
    // path instead (`capturePoseRefusal`, claims §5.148 §1).
    const disagreeing = MATRIX_FILE.cells.filter(
      (cell) =>
        cell.state !== undefined &&
        (cell.state === "inactive") !== INACTIVE_SCENES.has(cell.key.sceneId),
    );
    expect(disagreeing.map(name)).toEqual([]);
  });

  it("names no inactive scene in the conditioning predicate's exclusion list", () => {
    // `PREDICATE_EXCLUDES` must equal the machine's own output over the gated bed.
    // An inactive scene named here would be an exclusion for a cell no gated count
    // ever reaches — a line nothing could ever re-derive or remove.
    const named = PREDICATE_EXCLUDES.filter((line) =>
      [...INACTIVE_SCENES].some((sceneId) => line.includes(` / ${sceneId} / `)),
    );
    expect(named).toEqual([]);
  });

  it("floors no inactive row", () => {
    const floored = Object.keys(REGRESSION_FLOORS).filter((key) =>
      [...INACTIVE_SCENES].some((sceneId) => key.includes(` / ${sceneId} / `)),
    );
    expect(floored).toEqual([]);
  });

});

/**
 * ## The stack overlay bound: W27f G2 (2026-09-11)
 *
 * W27f replaced the flat white a WebGPU group drew over ordinary page content
 * with the profile's material at the group's backdrop level. Its landing gate
 * had to bound the one thing on this bed that has a native reading of a
 * `css-backdrop` group: a stack's overlay, which resolves `css-backdrop` on
 * every route and is therefore the composed-glass analogue of the page path
 * (claims §5.129 X8). The bound was declared before the read, in
 * `results/2026-09-11-w27f-g2/declaration.md` §4, and the read met it in every
 * clause; claims §5.135 is the adoption.
 *
 * **Why this is not a `GateRow` over `matrix.json` like every bound above it.**
 * The matrix carries no overlay-local metric, and cannot: a stack cell's
 * footprint is the union of both placed shapes, and every perceptual, shape and
 * material row is stated over that union. Claims §5.131 §6 is explicit that the
 * overlay's residual must not be allowed to disappear behind the base's larger
 * footprint, so a whole-footprint floor on these cells would gate the wrong
 * number. The metric exists only in the gate's own reader, and its reading is
 * committed beside it.
 *
 * **What this therefore is, stated plainly.** It is weaker than a matrix floor.
 * A matrix floor fails when a re-capture moves a number; this fails when the
 * committed reading's own arithmetic no longer satisfies the bound the ledger
 * says it satisfies. Each clause below is asserted twice over: once on the
 * measured error against the declared bound, which is what makes a perturbed
 * reading fail, and once on the boolean the runner wrote, which is what catches
 * the runner disagreeing with its own inputs. It catches the ledger and the
 * evidence drifting apart — which W27c G1b found three instances of (claims
 * §5.134) — and it does not catch a material change on its own, because nothing
 * regenerates this reading in CI. What would make it a real floor is per-surface
 * metrics in the matrix schema, so a stack cell's overlay carries adopted rows
 * like any other cell; that is named as the work in claims §5.135 and is not
 * done here.
 *
 * The dark `photo__glass-over-glass__rest` cell is absent from the table on
 * purpose: `apple-macos-26.5-1x-dark-standard` has no such fixture, so the cell
 * has no envelope and nothing about it is adopted.
 */
describe("the stack overlay bound (W27f G2, claims §5.135)", () => {
  interface OverlayArm {
    readonly read: Record<string, number | null>;
    readonly recorded?: Record<string, number | null>;
    readonly reproducesRecord?: boolean;
    readonly errorToNative?: Record<string, number | null>;
    readonly clauseA?: Record<string, { bound: number; from: string; holds: boolean }>;
    readonly clauseB?: Record<string, { pin: number; holds: boolean }>;
  }
  interface OverlayCell {
    readonly scheme: string;
    readonly stack: string;
    readonly scene: string;
    readonly nativeFixture: boolean;
    readonly envelope: Record<string, { min: number; max: number; upperFrom: string } | null>;
    readonly arms: Record<string, OverlayArm>;
  }
  interface Verdict {
    readonly cells: readonly OverlayCell[];
    readonly stopsScope: string;
    readonly boundStops: readonly string[];
    readonly landing: string;
  }
  interface Identity {
    readonly sampledPathStops: readonly string[];
    readonly coverageStops: readonly string[];
    readonly instrumentStops: readonly string[];
    readonly declaredStopRulings: readonly {
      stop: string;
      ruling: string;
      resolved: boolean;
      decidedBy: string;
    }[];
  }

  const EVIDENCE = resolve(PACKAGE_ROOT, "results", "2026-09-11-w27f-g2");
  const VERDICT = readJson<Verdict>(resolve(EVIDENCE, "verdict.json"));
  const IDENTITY = readJson<Identity>(resolve(EVIDENCE, "identity.json"));
  const METRICS = ["de", "lum", "rim"] as const;
  /** The three cells with a native fixture; the dark photo stack has none. */
  const REFEREED = VERDICT.cells.filter((cell) => cell.nativeFixture);

  it("reads the three cells that have a native overlay, and only those", () => {
    expect(VERDICT.cells).toHaveLength(4);
    expect(REFEREED.map((cell) => `${cell.scheme} / ${cell.stack}`)).toEqual([
      "light / checkerboard",
      "light / photo",
      "dark / checkerboard",
    ]);
    const unrefereed = VERDICT.cells.filter((cell) => !cell.nativeFixture);
    expect(unrefereed.map((cell) => `${cell.scheme} / ${cell.stack}`)).toEqual(["dark / photo"]);
    // Nothing is adopted over the cell with no native fixture. If a dark
    // `photo__glass-over-glass` is ever captured, this is where it stops being
    // true and the cell gains an envelope of its own.
    for (const cell of unrefereed) {
      for (const arm of Object.values(cell.arms)) {
        expect(arm.clauseA).toBeUndefined();
        expect(arm.clauseB).toBeUndefined();
      }
    }
  });

  it("holds clause A: the DOM-base overlay is inside the native stack envelope", () => {
    // The envelope's endpoints are S0 (the old textured-base composite, which
    // the runtime can no longer produce) and S1 (the same base under the landed
    // material), kept apart and never averaged. The bound is the upper endpoint.
    // The comparison is made here rather than read off `holds`, so that a
    // reading which drifts out of the envelope fails this test even if the
    // runner's own verdict still says it passed.
    for (const cell of REFEREED) {
      const uh = cell.arms["uh"];
      expect(uh, `${cell.scheme} / ${cell.stack} has no hinted DOM arm`).toBeDefined();
      for (const metric of METRICS) {
        const clause = uh?.clauseA?.[metric];
        expect(clause, `${cell.scheme} / ${cell.stack} :: ${metric}`).toBeDefined();
        const error = uh?.errorToNative?.[metric];
        expect(
          error,
          `${cell.scheme} / ${cell.stack} :: ${metric} has no measured error to native`,
        ).toBeTypeOf("number");
        expect(
          error as number,
          `${cell.scheme} / ${cell.stack} :: ${metric} left the envelope at ${clause?.bound}`,
        ).toBeLessThanOrEqual(clause?.bound as number);
        expect(clause?.holds, `${cell.scheme} / ${cell.stack} :: ${metric}`).toBe(true);
      }
    }
  });

  it("holds clause B: no overlay reading is worse than claims §5.131 §6 recorded", () => {
    // Eighteen pins: two arms × three metrics × the three cells with a native
    // fixture. Each is the measured error against the magnitude claims §5.131 §6
    // recorded for the same configuration and metric, compared here rather than
    // taken on trust from the runner's boolean.
    let pinned = 0;
    for (const cell of REFEREED) {
      for (const which of ["s1", "uh"]) {
        for (const metric of METRICS) {
          const pin = cell.arms[which]?.clauseB?.[metric];
          expect(pin, `${cell.scheme} / ${cell.stack} / ${which} :: ${metric}`).toBeDefined();
          const error = cell.arms[which]?.errorToNative?.[metric];
          expect(
            error,
            `${cell.scheme} / ${cell.stack} / ${which} :: ${metric} has no measured error`,
          ).toBeTypeOf("number");
          expect(
            error as number,
            `${cell.scheme} / ${cell.stack} / ${which} :: ${metric} widened past ${pin?.pin}`,
          ).toBeLessThanOrEqual(pin?.pin as number);
          expect(pin?.holds, `${cell.scheme} / ${cell.stack} / ${which} :: ${metric}`).toBe(true);
          pinned += 1;
        }
      }
    }
    expect(pinned).toBe(18);
  });

  it("records that the read reproduced the ledger exactly, rather than merely passing", () => {
    // The distinction matters. A reading that is inside the bound but somewhere
    // new would mean the material moved and happened to stay in range; every one
    // of these reproduced claims §5.131 §6 to the printed precision, which is
    // why the landing head could be certified as the configuration G1 measured.
    // The equality is asserted on the readings themselves, so that a reading
    // which moves fails here whatever `reproducesRecord` was written as.
    for (const cell of REFEREED) {
      for (const which of ["s1", "uh"]) {
        const arm = cell.arms[which];
        for (const metric of METRICS) {
          const recorded = arm?.recorded?.[metric];
          if (recorded === undefined || recorded === null) continue;
          expect(
            arm?.read?.[metric],
            `${cell.scheme} / ${cell.stack} / ${which} :: ${metric} left §5.131 §6's value`,
          ).toBe(recorded);
        }
        expect(
          arm?.reproducesRecord,
          `${cell.scheme} / ${cell.stack} / ${which} did not reproduce §5.131 §6`,
        ).toBe(true);
      }
    }
  });

  it("carries the two dark-checker regressions the ledger names, pinned and unclosed", () => {
    // Claims §5.131 §6 records both: the hinted DOM overlay's ΔE went
    // 0.011332 → 0.013059 and the textured-base overlay's 0.013765 → 0.016702
    // when G1's material replaced the flat. Neither is repaired by W27f G2, and
    // the point of pinning them is that they cannot widen unobserved. A gate
    // that quietly improved these numbers would also fail here, which is
    // correct: it would mean the material moved.
    const dark = REFEREED.find((cell) => cell.scheme === "dark" && cell.stack === "checkerboard");
    expect(dark?.arms["uh"]?.clauseB?.["de"]?.pin).toBe(0.013059);
    expect(dark?.arms["s1"]?.clauseB?.["de"]?.pin).toBe(0.016702);
    // And the one row where clause A's upper endpoint is S1's own regression,
    // which is why clause B is what carries this cell.
    expect(dark?.envelope["de"]?.upperFrom).toBe("s1");
  });

  it("landed with none of the bound's own stops outstanding", () => {
    // Scoped deliberately. `verdict.json` decides S1 and S2, the two clauses,
    // and those are empty: this is what the adoption rests on. It does not
    // decide S3 or S4, and an unqualified "no stop outstanding" over this file
    // would assert something about the instrument that this file never
    // measured — which is how the gate's two evidence files came to disagree
    // with nothing reconciling them.
    expect(VERDICT.boundStops).toEqual([]);
    expect(VERDICT.landing).toBe("the bound's clauses hold");
    expect(VERDICT.stopsScope).toContain("S1");
  });

  it("carries the instrument's stops apart, with S4 tripped and ruled on by the user", () => {
    // S3 held: no sampled digest moved, and no capture the record has went
    // missing from the read. S4, as `declaration.md` §6 worded it, did not: one
    // record-only CSS capture is not byte-repeatable.
    //
    // The user scoped S4 to the WebGPU arms on 2026-09-12 (W27 Decision Log 14),
    // on the ground that the stop as declared contradicted contract X1, which
    // predates it — so the ruling corrects the declaration and not the reading.
    //
    // What this asserts is the *record*, not the outcome. The stop must still be
    // recorded as tripped, the ruling must still name the decision that scoped
    // it, and the decision must still be attributed. A later edit that quietly
    // drops the trip, restates the ruling as the gate's own, or re-attributes it
    // fails here — which is the whole point of keeping the history in the
    // evidence rather than only in prose that nothing checks.
    expect(IDENTITY.sampledPathStops).toEqual([]);
    expect(IDENTITY.coverageStops).toEqual([]);
    expect(IDENTITY.instrumentStops.length).toBeGreaterThan(0);

    const [s4, ...rest] = IDENTITY.declaredStopRulings;
    expect(rest).toEqual([]);
    expect(s4?.stop).toBe("S4");
    expect(s4?.resolved).toBe(true);
    expect(s4?.decidedBy).toBe("W27 Decision Log 14");
    expect(s4?.ruling).toContain("scoped to the WebGPU arms");
    expect(s4?.ruling).toContain("corrects the declaration, not the reading");
    // The residual the ruling explicitly did not close.
    expect(s4?.ruling).toContain("CSS bistability stays a named residual");
  });
});

/**
 * W30 G0 (a), acceptance clause 1 — the frozen bed's own count, pinned across
 * the exemption.
 *
 * `atAShippedDocument` above keeps only the rows whose `capturePath` names a
 * profile document whose BYTES are the bytes on disk. That is a strength
 * everywhere else in this file and it is a hazard for exactly one commit: W30 G2
 * spends the wave's single X1 exemption by adding leaves to the renderer's
 * default, which moves every document's resolved digest, and the obvious way to
 * record that move — re-recording the digest inside the two frozen macOS 26.5
 * documents — would change those documents' bytes. `SHIPPED_DOCUMENT_HASHES`
 * would then no longer hold the hashes the 1,107 macOS 26.5 rows name, the
 * partition would drop all of them, and **every bound, floor, partition count and
 * conditioning exclusion stated over the macOS 26.5 bed would pass vacuously.**
 * No assertion in this file says "over a non-empty set" often enough to catch
 * that; a bed that silently empties does not look like a failure.
 *
 * So the count is pinned. It is stated over the matrix FILE rather than over
 * `MATRIX`, because the probe and inactive drops are a different question and
 * this one is only about the document partition. The number is the freeze's own:
 * `results/2026-09-16-w29-freeze/sha256.txt` carries one row hash per macOS
 * 26.5-keyed row of the canonical matrix and there are 1,107 of them, so a
 * disagreement here is either a document whose bytes moved or a row that left
 * the matrix, and both are X1 events.
 *
 * It is a pin rather than a floor: if a later wave legitimately re-reads the
 * macOS 26.5 bed the number moves WITH the freeze and both are re-recorded
 * together, which is the event this exists to make visible rather than
 * impossible.
 */
describe("the frozen macOS 26.5 bed survives the document partition (W30 G0, X1)", () => {
  const FROZEN = MATRIX_FILE.cells.filter((cell) =>
    cell.key.profileKey.startsWith("apple-macos-26.5-"),
  );

  it("keeps all 1,107 macOS 26.5 rows at documents whose bytes are on disk", () => {
    expect(FROZEN.length).toBe(1107);
    expect(FROZEN.filter(atAShippedDocument).length).toBe(1107);
  });

  it("names the two frozen documents and nothing else", () => {
    // The partition passes on a hash match, so the thing worth asserting beside
    // the count is WHICH documents the frozen rows were captured at: two, both
    // macOS 26.5, the pair the freeze holds. A macOS 26.5 row captured at some
    // other document would pass the count above and still not be the frozen bed.
    const named = new Set(
      FROZEN.map(
        (cell) => /materialProfile=(\S+) sha256:/.exec(cell.key.web.capturePath)?.[1] ?? "none",
      ),
    );
    expect([...named].sort()).toEqual([
      "packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json",
      "packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json",
    ]);
  });
});

/**
 * **B1, adopted — the outer shadow's σ law against the bed's own native σ**
 * (W30 G4, claims §5.160; declared at §5.156 §5 (b) as the wave's one tolerance
 * "adopted at G4 if it passes", restated by charter Decision Log 3 (c), fitted
 * and met at §5.159 §1, re-read at the constants the seal wrote by §5.159b §10
 * finding 7).
 *
 * **What it asserts.** On macOS 27 the outer shadow's blur is linear in the
 * casting span above a knee, where on macOS 26.5 it was one constant at every
 * size. 0.19.0 shipped that one constant and this wave replaced it with the law.
 * B1 is the promise that the law's output stays inside ±5 % of the native
 * material's own σ at the three thick spans the bed measures — 96, 128 and 160 —
 * on every bed the document serves.
 *
 * **Joint, which is what makes it bite.** A material profile document is selected
 * per colour scheme and not per scale or per accessibility state, so ONE document
 * draws four beds on the light side (1x, 2x, reduced transparency, coupled
 * contrast) and two on the dark. The admissible σ at a span is therefore the
 * INTERSECTION of those beds' ±5 % windows, and on the light document that
 * intersects to ±0.685 % at span 96 rather than ±5 %. A law fitted to the
 * 1x-light median alone lands −6.08 % against the 2x-light bed and fails here;
 * that is measured, not hypothetical (§5.156 §5, Decision Log 3 (c)).
 *
 * **Read from committed evidence, never transcribed.** The natives come from W30
 * G0's cut — one σ per bed per span per cell, off W29 G2's native delta, with the
 * statistic G0 named — and the law's output comes from the shipped documents'
 * own leaves. Neither side is a literal in this file, for the reason no bound in
 * this file is: a number retyped after a refit is a number that goes stale
 * silently. What IS stated here is the tolerance and the spans, because those are
 * the promise.
 *
 * **Why B1 and not B2 or B4.** §5.156 §5 declared the fate of each of the wave's
 * five acceptances before the first leaf existed, and only B1's was adoption.
 * B2 (the thin-span factor) stays a one-wave reading because the thin regime's
 * (amplitude, σ) pair is not identified and bifurcates on the author's tint; B4
 * (the structure ratio) stays one because it would be a standing promise about a
 * curve read at one pitch. Both name what would make them adoptable and neither
 * is asserted here.
 */
describe("W30 B1 — the shadow's σ law, adopted (claims §5.160)", () => {
  /** G0's statistic, named at §5.156 §5 (b): the upper middle order statistic. */
  const upperMiddle = (values: readonly number[]): number =>
    [...values].sort((a, b) => a - b)[Math.floor(values.length / 2)] ?? Number.NaN;

  const B1_TOLERANCE = 0.05;
  const B1_SPANS = [96, 128, 160] as const;

  interface CutCell {
    readonly bed: string;
    readonly profile: string;
    readonly span: number;
    readonly sigmaCss: number;
  }

  /**
   * W30 G0's native cut: one σ per active cell, `sigma_css > span` already
   * excluded by the rule the file records in its own `exclusionRule`.
   */
  const CUT = readJson<{
    readonly statistic: string;
    readonly cells: readonly CutCell[];
  }>(resolve(PACKAGE_ROOT, "results", "2026-09-20-w30-g0-cut", "shadow-cut.json"));

  /** A shipped document, read for its σ leaves. */
  const documentOf = (
    file: string,
  ): {
    readonly sigmaPx: number;
    readonly sigmaSlopePerSpan: number;
    readonly sigmaSpanRefPx: number;
    readonly sigmaThinOffsetPx: number;
  } => {
    const patch = readJson<{
      readonly patch: { readonly outerShadow: Record<string, number> };
    }>(resolve(PACKAGE_ROOT, "profiles", file)).patch.outerShadow;
    for (const leaf of [
      "sigmaPx",
      "sigmaSlopePerSpan",
      "sigmaSpanRefPx",
      "sigmaThinOffsetPx",
    ] as const) {
      expect(typeof patch[leaf], `${file} names ${leaf}`).toBe("number");
    }
    return patch as never;
  };

  /**
   * The law itself, mirrored from `platform-web`'s `outerShadowSigmaPx` and the
   * renderer's `outer_shadow_sigma`.
   *
   * Written out here rather than imported, for this file's standing reason: a
   * gate that evaluated the runtime's own function would be asserting that the
   * runtime agrees with itself. What binds the three copies to each other is
   * `tier-coherence.test.ts` and `w30-inert-laws.test.ts`; what this file asserts
   * is that the copy the DOCUMENTS carry lands inside the NATIVE bed's window.
   */
  const sigmaAt = (
    leaves: ReturnType<typeof documentOf>,
    span: number,
  ): number =>
    leaves.sigmaPx
    + Math.max(
      leaves.sigmaThinOffsetPx,
      leaves.sigmaSlopePerSpan * (span - leaves.sigmaSpanRefPx),
    );

  /**
   * Which beds a document serves: every declared 27 profile of its own scheme.
   *
   * Derived from `DECLARED_27_PROFILES` rather than listed again, which is what
   * keeps the confounded `…-1x-light-increased-contrast-glass0.5` bed out of the
   * bound — it is not a declared profile (W29 Decision Log 5), it is in the cut,
   * and a hand-written list of beds would have let it in by looking plausible.
   */
  const served = (scheme: "light" | "dark"): readonly string[] =>
    DECLARED_27_PROFILES.map((profile) => profile.profileKey).filter((key) =>
      scheme === "dark" ? key.includes("-dark-") : key.includes("-light-"),
    );

  const DOCUMENTS = [
    { scheme: "light", file: "apple-macos-27.0-1x-light-standard-glass0.5.json" },
    { scheme: "dark", file: "apple-macos-27.0-1x-dark-standard-glass0.5.json" },
  ] as const;

  /**
   * How many of the beds a document serves carry a cell at each asserted span.
   *
   * Counted rather than merely required to be non-zero (corrected 2026-09-20,
   * W30 G4 review closure; claims §5.160 §9). The per-bed case above `continue`s
   * on an empty bed by design — the two accessibility beds carry no span-128
   * cell — and the joint case intersects over whatever windows it finds, so a bed
   * that stopped contributing would silently leave the clause to the beds that
   * remain rather than fail. That is not hypothetical: the light document's
   * ±0.685 % window at span 96 comes entirely from the 2x-light bed, and with
   * that bed removed all four cases stay green over [8.3556, 9.0193], ±3.82 %.
   * These counts are what turns an emptied bed into a red.
   *
   * The values are the cut's own population: on the light side the two standard
   * beds carry all three spans and the reduced-transparency and coupled-contrast
   * beds carry 96 and 160 only; on the dark side the two standard beds carry all
   * three and there is no accessibility bed.
   */
  const CONTRIBUTING_BEDS: Readonly<
    Record<"light" | "dark", Readonly<Record<number, number>>>
  > = {
    light: { 96: 4, 128: 2, 160: 4 },
    dark: { 96: 2, 128: 2, 160: 2 },
  };

  it("reads the cut at the statistic §5.156 §5 (b) declared, over every bed that carries each span", () => {
    // The guard the rest of this block leans on. A cut that had moved, emptied or
    // been re-stated at another statistic would let every window below pass over
    // nothing, and no assertion about a maximum says "over something".
    expect(CUT.statistic).toContain("upper middle order statistic");
    expect(CUT.cells.length).toBeGreaterThan(200);
    for (const { scheme } of DOCUMENTS) {
      for (const span of B1_SPANS) {
        const contributing = served(scheme).filter((profile) =>
          CUT.cells.some((cell) => cell.profile === profile && cell.span === span),
        );
        expect(
          contributing.length,
          `${scheme} at span ${span}: ${contributing.join(", ") || "no bed"}`,
        ).toBe(CONTRIBUTING_BEDS[scheme][span]);
      }
    }
  });

  for (const { scheme, file } of DOCUMENTS) {
    it(`${scheme}: the law's σ is within 5% of every served bed's native σ at spans 96, 128 and 160`, () => {
      const leaves = documentOf(file);
      // A negative slope would invert the group reach's bound, which is asserted
      // as a bound in `w30-inert-laws.test.ts`; assert the precondition here too,
      // because B1 passing at a negative slope would be B1 passing about nothing.
      expect(leaves.sigmaSlopePerSpan).toBeGreaterThanOrEqual(0);

      for (const span of B1_SPANS) {
        const law = sigmaAt(leaves, span);
        for (const profile of served(scheme)) {
          const cells = CUT.cells.filter(
            (cell) => cell.profile === profile && cell.span === span,
          );
          // A bed that carries no cell at this span is not evidence about it: the
          // accessibility beds have no span-128 cell at all, and the law's value
          // there is an extrapolation §5.156 §5 declares as one.
          if (cells.length === 0) continue;
          const native = upperMiddle(cells.map((cell) => cell.sigmaCss));
          const error = (law - native) / native;
          expect(
            Math.abs(error),
            `${profile} at span ${span}: law ${law.toFixed(4)} against native ${native.toFixed(4)} `
              + `over ${cells.length} cells, ${(error * 100).toFixed(3)}%`,
          ).toBeLessThanOrEqual(B1_TOLERANCE);
        }
      }
    });
  }

  it("holds the joint window, which is tighter than the clause's own 5% on the light document", () => {
    /*
     * The clause restated as one intersection per span, which is what Decision
     * Log 3 (c) ruled it is. Asserting it this way rather than bed by bed catches
     * the case a per-bed loop cannot: a law that clears every bed by 4.9 % in
     * OPPOSITE directions would satisfy the case above and still be outside the
     * set of σ any single document can draw for all of them.
     *
     * The intersection is also the reading that made B1 worth adopting. On the
     * light document it is ±0.685 % at span 96 — the four served beds' windows
     * overlap that narrowly — so the adopted promise is seven times tighter than
     * the number it is written with, and it is tighter by measurement rather than
     * by choice.
     */
    for (const { scheme, file } of DOCUMENTS) {
      const law = documentOf(file);
      for (const span of B1_SPANS) {
        const windows = served(scheme)
          .map((profile) =>
            CUT.cells.filter((cell) => cell.profile === profile && cell.span === span),
          )
          .filter((cells) => cells.length > 0)
          .map((cells) => upperMiddle(cells.map((cell) => cell.sigmaCss)))
          .map((native) => [native * (1 - B1_TOLERANCE), native * (1 + B1_TOLERANCE)] as const);
        expect(windows.length, `${scheme} at span ${span}`).toBeGreaterThan(0);
        const low = Math.max(...windows.map((window) => window[0]));
        const high = Math.min(...windows.map((window) => window[1]));
        expect(low, `${scheme} at span ${span}: the served beds' windows do not intersect`)
          .toBeLessThanOrEqual(high);
        const value = sigmaAt(law, span);
        expect(
          value,
          `${scheme} at span ${span}: σ ${value.toFixed(4)} against [${low.toFixed(4)}, ${high.toFixed(4)}]`,
        ).toBeGreaterThanOrEqual(low);
        expect(value).toBeLessThanOrEqual(high);
      }
    }
  });
});

/**
 * **M1 and M2, adopted — the body carries the backdrop's hue, and the structure
 * it is read over does not move** (W31 G4, Decision Log 3 (a) as ruled; declared
 * at claims §5.161 §7 (b) before any leaf existed, fitted and met at §5.164 §4,
 * adopted at §5.165 §1).
 *
 * **The first two adopted rows on the material axis.** The header at the top of
 * this file argues the axis is not gateable on this fixture set, on two grounds,
 * and carries the amendment that says why these two clear both. What follows is
 * what they assert.
 *
 * **M1, the chroma tolerance.** `R = chromaStructureRatioWeb /
 * chromaStructureRatioNative` — web against native on the same cell and never
 * against 1, which is what makes it a fidelity statement rather than a promise
 * about a constant. The numerator of each side is the interior's per-pixel OKLab
 * chroma spread and the denominator is its own luma spread, so a body that blurs
 * more but keeps its hues reads the same as one that blurs less: the structure
 * deficit this wave did not touch cancels instead of being absorbed as
 * saturation. Two clauses, over four document beds — the four macOS 27 standard
 * profiles at both scales, untinted `photo`, `calibration` + `validation`, the
 * two poses separated because they draw two different documents:
 *
 *   1. **the median per bed is inside [0.80, 1.20]**, two-sided because an
 *      over-fitted retention adds chroma the reference does not have;
 *   2. **every cell is inside [0.60, 1.40]**, also two-sided, and the ceiling is
 *      the parent's number rather than the bed's. The worst cell reads 1.5155,
 *      so 1.55 would be green today and say almost nothing; 1.40 declares three
 *      cells MISSED and they are in `MISSED_27_ROWS` with the lever. A miss is
 *      recorded, never widened.
 *
 * The band's half-width is justified from the instrument's own reproducibility,
 * the 1x-against-2x spread of `R` on the bed's own cells: 4.5 % median light and
 * 9.1 % dark pre-fit, 4.5 % and 10.6 % after (claims §5.164 §12 as its closure
 * corrects it). Plus or minus 0.20 is **1.9 times** the dark bed's post-fit median
 * spread of **10.60 %** — 3.8 times on the full band — and what it had to detect
 * was a residual 0.45 and 0.67 away from 1. *(Corrected 2026-09-21, W31 G4 review
 * closure, claims §5.165 §9 finding N7: "about four times" was taken against the
 * PRE-fit 9.1 %, where it is 2.2× on the half-band and 4.4× on the full one. The
 * post-fit median is the right denominator, because it is the spread the band has
 * to sit above on the material this file now gates.)*
 *
 * **M2, the structure stop, and why M1 does not travel alone.** `R` is scale-free
 * in the deviations. That is what makes the blur cancel and it is exactly what
 * makes `R` insufficient on its own: a body that lost its chroma AND its
 * structure together reads the same ratio as one that kept both. The CSS tier is
 * the demonstration and not a hypothesis — its `R` reads near the reference on
 * the dark cells while its ratio (ii) reads 0.19 to 0.24 against 0.90 and the
 * sheets show a body with no hues in it at all (claims §5.161 §7 (b)). So M2
 * bounds `interiorStdDevWeb` to within 2 % of what the same cell drew at the
 * **pre-fit generation** — the rows read at the macOS 27 documents before any
 * retention was fitted into them, which the split moved to
 * `results/superseded/`. A retention that bought its ratio by flattening the body
 * fails M2 before M1 notices.
 *
 * **The WebGPU tier only** (`tier === "texture"`), which is G0's second condition
 * and is stronger after the read than before it. The CSS tier's `R` at the
 * canonical read sits at 0.95 to 1.12 by bed median on a tier that carries none
 * of this operator — a derivation was written, rendered and declined on the
 * measurement (claims §5.164 §5) — so gating it would certify the gap, which is
 * Decision Log 11's refusal one axis over. The two accessibility profiles are out
 * for a different reason: they stand the retention down entirely under their
 * occlusion lift (W31 Decision Log 3 (d)), so their body is 0.20.0's and this row
 * would be asserting nothing about this wave.
 *
 * **Read from a cut regenerated at this gate, never from a literal.** See
 * `CHROMA_CUT` above for why the path alone is not enough and what closes the
 * rest.
 */
describe("W31 M1 / M2 — the body's chroma and the structure it is read over (claims §5.165)", () => {
  /** Which beds the cut must carry, and with how many cells — B1's own guard. */
  const CONTRIBUTING_CELLS: Readonly<Record<string, number>> = {
    "light|active": 10,
    "light|inactive": 8,
    "dark|active": 4,
    "dark|inactive": 4,
  };

  /**
   * The bed, re-derived here from the matrix rather than taken from the cut.
   *
   * `MATRIX` is not usable: it drops the inactive pose, and half this bed is the
   * inactive pose, because the receded documents carry their own retention and
   * are bounded separately. So the selection is restated over `MATRIX_FILE` with
   * the shipped-document guard applied to EVERY document a row names — the
   * receded one included, which `atAShippedDocument` does not reach and which is
   * what decides what an inactive row drew.
   */
  const bedFromMatrix = (): Map<string, Cell> => {
    const out = new Map<string, Cell>();
    for (const cell of MATRIX_FILE.cells) {
      if (CHROMA_BED_PROFILES[cell.key.profileKey] === undefined) continue;
      if (cell.key.web.renderer !== "webgpu") continue;
      if (cell.fixtureSet !== "calibration" && cell.fixtureSet !== "validation") continue;
      const scene = cell.key.sceneId;
      if (!scene.startsWith("photo__") || scene.includes("-tint-")) continue;
      const named = [
        ...cell.key.web.capturePath.matchAll(
          /(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g,
        ),
      ];
      if (named.length === 0) continue;
      if (!named.every((match) => SHIPPED_DOCUMENT_HASHES.get(match[1] ?? "") === match[2])) {
        continue;
      }
      out.set(`${cell.key.profileKey} ${scene}`, cell);
    }
    return out;
  };

  it("reads a cut taken at this gate, in the declared mode, over the bed the matrix itself carries", () => {
    // The guard everything below leans on, and the one W31 G1's closure named: a
    // cut in another mode, at other documents, or with the holdout in it would
    // let every window below pass over the wrong numbers.
    expect(CHROMA_CUT.mode).toContain("chromaStructureRatioWeb / chromaStructureRatioNative");
    expect(CHROMA_CUT.mode).toContain("median per scheme and pose");
    expect(CHROMA_CUT.atDocuments).toBe("shipped");
    expect(CHROMA_CUT.withHoldout).toBe(false);
    expect(CHROMA_CUT.tier).toBe("texture");
    expect(CHROMA_CUT.renderer).toBe("webgpu");
    expect([...CHROMA_CUT.sets].sort()).toEqual(["calibration", "validation"]);

    // No declared holdout scene reached it, asserted against the declaration
    // rather than against the set label, because the two could disagree.
    const holdout = new Set(SCENE_DECLARATION.split["holdout"] ?? []);
    expect(
      CHROMA_CUT.cells.filter((cell) => holdout.has(cell.scene)).map(chromaKey),
      "a declared holdout scene in the cut (contract X4)",
    ).toEqual([]);

    /*
     * **The cut is a record and never the only copy.** Every figure in it is
     * re-derived here from the committed matrix and from the pre-fit generations
     * it names, in both directions, so the snapshot problem W31 G1's review
     * closure found in B1's shape cannot live here: a canonical read that moves a
     * row makes M1 and M2 read the new number, and a cut nobody regenerated fails
     * this case instead of quietly gating yesterday's bed.
     */
    const bed = bedFromMatrix();
    expect(
      CHROMA_CUT.cells.map((cell) => `${cell.profile} ${cell.scene}`).sort(),
      "the cut's cells against the bed the matrix carries",
    ).toEqual([...bed.keys()].sort());

    const preFit = new Map<string, Cell>();
    for (const [scheme, generation] of Object.entries(CHROMA_CUT.preFitGeneration)) {
      const file = readJson<ResultMatrix>(
        resolve(PACKAGE_ROOT, "results", "superseded", generation.file),
      );
      for (const cell of file.cells) {
        // Named, not inferred: a row in the file read at some other document
        // would be a different baseline wearing the same key.
        if (!cell.key.web.capturePath.includes(`sha256:${generation.activeDocumentSha256}`)) {
          continue;
        }
        const scheme_ = CHROMA_BED_PROFILES[cell.key.profileKey];
        if (scheme_ === undefined) continue;
        expect(
          scheme_,
          `${generation.file}: ${cell.key.profileKey} is not a ${scheme} bed`,
        ).toBe(scheme);
        preFit.set(`${cell.key.profileKey} ${cell.key.sceneId}`, cell);
      }
    }

    for (const cut of CHROMA_CUT.cells) {
      const key = `${cut.profile} ${cut.scene}`;
      const cell = bed.get(key);
      expect(cell, `${chromaKey(cut)}: in the cut and not in the matrix`).toBeDefined();
      if (cell === undefined) continue;
      expect(cell.tier, chromaKey(cut)).toBe(cut.tier);
      expect(cell.fixtureSet, chromaKey(cut)).toBe(cut.set);
      const native = reading(cell, "material", "chromaStructureRatioNative");
      const web = reading(cell, "material", "chromaStructureRatioWeb");
      expect(cut.chromaStructureRatioNative, chromaKey(cut)).toBeCloseTo(native, 12);
      expect(cut.chromaStructureRatioWeb, chromaKey(cut)).toBeCloseTo(web, 12);
      expect(cut.R, `${chromaKey(cut)}: R against the matrix`).toBeCloseTo(web / native, 12);
      expect(cut.interiorStdDevWeb, chromaKey(cut)).toBeCloseTo(
        reading(cell, "material", "interiorStdDevWeb"),
        12,
      );

      const before = preFit.get(key);
      expect(before, `${chromaKey(cut)}: no pre-fit row in the named generation`).toBeDefined();
      if (before === undefined) continue;
      // The pre-fit generation predates the instrument, which is the check that
      // it really is pre-fit: `chromaStructureRatio*` entered the schema with this
      // wave, so a baseline row carrying one was read after the leaf.
      expect(
        before.material?.["chromaStructureRatioWeb"],
        `${chromaKey(cut)}: the baseline row carries a chroma field, so it is not pre-fit`,
      ).toBeUndefined();
      const baseline = reading(before, "material", "interiorStdDevWeb");
      expect(cut.interiorStdDevWebPreFit, chromaKey(cut)).toBeCloseTo(baseline, 12);
      expect(cut.structureDeltaFraction, chromaKey(cut)).toBeCloseTo(
        (cut.interiorStdDevWeb - baseline) / baseline,
        12,
      );
    }
  });

  it("carries every bed the two documents draw, at the cell counts the read left", () => {
    // B1's `CONTRIBUTING_BEDS` one row along, and for its reason: a bed that
    // stopped contributing would leave the median to the cells that remain rather
    // than fail. Counted, so an emptied bed is a red.
    const counted: Record<string, number> = {};
    for (const cell of CHROMA_CUT.cells) {
      const bed = `${cell.scheme}|${cell.pose}`;
      counted[bed] = (counted[bed] ?? 0) + 1;
    }
    expect(counted).toEqual(CONTRIBUTING_CELLS);
    // And both scales are in every bed, which is what the reproducibility the
    // band is justified from is measured across.
    for (const bed of Object.keys(CONTRIBUTING_CELLS)) {
      const scales = new Set(
        CHROMA_CUT.cells
          .filter((cell) => `${cell.scheme}|${cell.pose}` === bed)
          .map((cell) => cell.scale),
      );
      expect([...scales].sort(), `${bed}: the scales the bed carries`).toEqual([1, 2]);
    }
  });

  it("M1: the median R of every bed is inside [0.80, 1.20]", () => {
    for (const bed of Object.keys(CONTRIBUTING_CELLS)) {
      const values = CHROMA_CUT.cells
        .filter((cell) => `${cell.scheme}|${cell.pose}` === bed)
        .map((cell) => cell.R)
        .sort((a, b) => a - b);
      expect(values.length, bed).toBe(CONTRIBUTING_CELLS[bed]);
      const middle = values.length / 2;
      const median =
        values.length % 2 === 0
          ? ((values[middle - 1] ?? Number.NaN) + (values[middle] ?? Number.NaN)) / 2
          : (values[Math.floor(middle)] ?? Number.NaN);
      expect(median, `${bed}: median R over ${values.length} cells`).toBeGreaterThanOrEqual(
        CHROMA_MEDIAN_MIN,
      );
      expect(median, `${bed}: median R over ${values.length} cells`).toBeLessThanOrEqual(
        CHROMA_MEDIAN_MAX,
      );
      // The cut's own summary has to agree with the statistic computed here, or
      // its printed table describes a different bed from the gated one.
      expect(CHROMA_CUT.beds[bed]?.median, `${bed}: the cut's median`).toBeCloseTo(median, 12);
    }
  });

  it("M1: every cell is inside [0.60, 1.40], or is named in MISSED_27_ROWS", () => {
    for (const cell of CHROMA_CUT.cells) {
      const key = `${chromaKey(cell)} :: ${CHROMA_METRIC}`;
      // Recorded, not widened: the three cells the ruling declared missed are
      // excused here and only here, and `MISSED_27_ROWS`'s owner asserts that the
      // set of excused cells is exactly the set that fails.
      if (MISSED_27_ROWS[key] !== undefined) continue;
      expect(cell.R, `${key}: R ${cell.R.toFixed(4)}`).toBeGreaterThanOrEqual(CHROMA_CELL_MIN);
      expect(cell.R, `${key}: R ${cell.R.toFixed(4)}`).toBeLessThanOrEqual(CHROMA_CELL_MAX);
    }
  });

  it("M2: interiorStdDevWeb is within 2% of the pre-fit generation, or is named in MISSED_27_ROWS", () => {
    for (const cell of CHROMA_CUT.cells) {
      // Recorded, not widened — the same path M1 has one case up, added at W32 G1
      // (claims §5.168) when the first miss appeared. The tolerance above is
      // unmoved and `MISSED_27_ROWS`'s owner asserts that the set of excused
      // cells is exactly the set that fails.
      if (MISSED_27_ROWS[`${chromaKey(cell)} :: ${CHROMA_STRUCTURE_METRIC}`] !== undefined) continue;
      expect(
        Math.abs(cell.structureDeltaFraction),
        `${chromaKey(cell)}: interiorStdDevWeb ${cell.interiorStdDevWebPreFit.toFixed(6)} -> `
          + `${cell.interiorStdDevWeb.toFixed(6)}, `
          + `${(cell.structureDeltaFraction * 100).toFixed(3)}%`,
      ).toBeLessThanOrEqual(CHROMA_STRUCTURE_TOLERANCE);
    }
  });
});
