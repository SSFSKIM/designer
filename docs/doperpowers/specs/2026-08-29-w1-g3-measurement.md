# W1 G3 — the six-profile web-side measurement (2026-08-29)

Child of `2026-08-28-post-v1-wave.md` (W1, gate G3). This document records the
measurement half of G3 and carries the PROPOSED threshold tables to the human
gate. Nothing in it is enforced; adoption is a decision, and the enforced
tables live in `packages/calibration/test/adopted-thresholds.test.ts` only
after that decision. Evidence commits: `a3b4d00` (capture machinery),
`5205017` (the matrix + strengthen-only test). Matrices:
`packages/calibration/results/w1-matrix.json` (136 cells, schema 3) and
`results/w1-matrix-contrast-only.json` (8 cells), both written via
`compare --out-matrix`; the committed `results/matrix.json` is byte-unchanged.

## Headline results

- 136 cells (six native profiles × two web tiers), every one byte-identical
  over two independent page loads, every texture cell on the real apple/metal-3
  adapter, v1's frozen material profiles applied unchanged.
- The 1× light-standard profile reproduces claims §5 **figure for figure** on
  both tiers across an independent recapture (worst calibration IoU 0.8489,
  contour p95 4.0000, SSIM 0.9114, ΔE 0.0247; worst holdout 0.9612, 2.8284,
  0.9007, 0.0548).
- **No 2×-only defect on any gated axis.** Scale-free metrics agree with their
  1× twins to within noise (ΔE mean invariant to 0.0011 across 24 light
  cells); contour scales exactly with DPR (device-pixel quantity).
- The 2× bed **repaired v1's one excluded cell**: dark
  `checkerboard__capsule-button__rest`, extractor recovery 88.9% → 100.2%,
  IoU 0.8434 → 0.9538, contour p95 15.0 px → 5.81 device px. The v1 figures
  described the instrument at 1×, not the material.
- Cross-tier ΔE tripwire answered by real captures: every profile passes the
  adopted bound in the mean and on its worst cell (worst anywhere 0.031
  against ≤ 0.05).

## The accessibility-override ruling (Decision Log 8 in the wave spec)

`compare --web-accessibility as-captured` (both flags, matching the coupled
native reference) is the default and the fidelity number. Coupled beats
contrast-only on all 8 cells and every perceptual metric; ΔE p95 roughly
doubles under contrast-only. The contrast-only matrix is retained as a bound
on a state the reference cannot see — never a fidelity claim.

## PROPOSED thresholds — `apple-macos-26.5-2x-light-standard`

Doctrine as claims §5: bounded by the holdout column. Split: 12 calibration,
6 validation, 6 holdout per tier.

### Texture tier

| axis | metric | proposed | worst cal+val | worst holdout |
|---|---|---|---|---|
| shape | silhouette IoU | ≥ 0.85 | 0.8784 | 0.9592 |
| shape | contour distance mean | ≤ 5.0 device px | 3.7556 | 1.1963 |
| shape | contour distance p95 | ≤ 10.0 device px | 8.0000 | 5.6569 |
| perceptual | SSIM mean | ≥ 0.93 | 0.9582 | 0.9584 |
| perceptual | OKLab ΔE mean | ≤ 0.07 | 0.0247 | 0.0546 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 | 0.1070 | 0.1333 |
| perceptual | edge-weighted mean | ≤ 0.12 | 0.0494 | 0.1002 |

### Dom tier (Chromium, `renderer: css`)

| axis | metric | proposed | worst cal+val | worst holdout |
|---|---|---|---|---|
| shape | silhouette IoU | ≥ 0.85 | 0.8967 | 0.9360 |
| shape | contour distance mean | ≤ 4.0 device px | 2.3912 | 2.2484 |
| shape | contour distance p95 | ≤ 8.0 device px | 5.3852 | 5.0000 |
| perceptual | SSIM mean | ≥ 0.92 | 0.9684 | 0.9509 |
| perceptual | OKLab ΔE mean | ≤ 0.08 | 0.0274 | 0.0559 |
| coherence | cross-tier OKLab ΔE mean | ≤ 0.05 | 0.00960 | 0.03133 (worst cell) |
| coherence | interior level, GPU ÷ CSS | 0.80 … 1.25 | 0.845 … 1.068 | — |

Rationale, stated once: the **colour bounds are the 1× bounds unchanged**
because the measurements are (holdout ΔE mean 0.0546 at 2× vs 0.0548 at 1×);
the **contour bounds are the 1× bounds doubled** because contour distance is
a device-pixel quantity and the geometry error did not move; the **SSIM
bounds are tighter than 1×'s deliberately** — SSIM reads systematically
higher at 2× (+0.014 mean; fixed pixel window over finer sampling), so the
proposal keeps §5's ~2–3% margin over the measured worst instead of
importing the 1× number, which would be slack at this scale.

## NOT proposed — the three provisional profiles

`2x-dark-standard`, `1x-light-reduced-transparency`,
`1x-light-increased-contrast`: calibration cells only, no validation, no
holdout — a bound's binding column does not exist, and adopting one would
certify overfitting in the doctrine's own words (v1's dark-provisional
reasoning, unchanged). Measured figures for the record:

| metric | 2x dark tex / dom | red-transp tex / dom | inc-contrast tex / dom |
|---|---|---|---|
| silhouette IoU | 0.9470 / 0.9329 | 0.9503 / 0.9303 | 0.9326 / 0.8814 |
| contour mean (dev px) | 1.4419 / 2.3119 | 0.7497 / 1.1977 | 1.1541 / 2.2225 |
| contour p95 (dev px) | 5.8135 / 5.3852 | 2.8284 / 2.8284 | 2.8284 / 5.0000 |
| SSIM mean | 0.9528 / 0.9446 | 0.9851 / 0.9643 | 0.9359 / 0.9204 |
| OKLab ΔE mean | 0.0216 / 0.0241 | 0.0105 / 0.0119 | 0.0177 / 0.0220 |
| OKLab ΔE p95 | 0.1409 / 0.1448 | 0.0469 / 0.0427 | 0.0605 / 0.0559 |
| edge-weighted mean | 0.0092 / 0.0128 | 0.0298 / 0.0383 | 0.0646 / 0.0735 |

(Increased-contrast shape rows rest on the two well-conditioned photo cells;
both checkerboard cells fail the §5 conditioning predicate — the extractor
loses the bright material over white squares, recovery 53–57%. Those raw
figures describe the instrument, not the geometry.)

**The cheap close:** the calibration split is declared per scene, so
extending these profiles' native scene sets to include one validation and one
holdout scene gives them a split for free — one accessibility-toggle session
and one dark session on the existing harness. Gate only after that.

## Cross-tier coherence, per profile

Bounds: cross-tier ΔE mean ≤ 0.05; interior ratio GPU ÷ CSS in 0.80…1.25.

| profile | n | ΔE mean / worst cell | SSIM mean / worst | interior ratio |
|---|---|---|---|---|
| 1× light standard | 23 | 0.00954 / 0.03124 | 0.9643 / 0.9158 | 0.844 … 1.067 |
| 2× light standard | 23 | 0.00960 / 0.03133 | 0.9746 / 0.9490 | 0.845 … 1.068 |
| 1× dark standard | 4 | 0.00530 / 0.00996 | 0.9760 / 0.9714 | 1.044 … **1.241** |
| 2× dark standard | 4 | 0.00542 / 0.01011 | 0.9803 / 0.9758 | 1.053 … **1.238** |
| 1× reduced-transparency | 4 | 0.00520 / 0.00763 | 0.9737 / 0.9630 | 0.958 … 1.013 |
| 1× increased-contrast | 4 | 0.00743 / 0.01037 | 0.9631 / 0.9473 | 0.955 … 1.017 |

Watch item (binding on W2/W3's awareness, advisory on their means): both dark
profiles sit within 0.9% of the interior-ratio ceiling. Any retune that
lightens the CSS tier in dark crosses 1.25.

Enforcing the cross-tier row from the matrix (instead of prose) needs a
schema-4 `coherence` axis on the cell — a design decision at the human gate.
The measurements say it would pass everywhere today.

## Findings routed elsewhere

- **Accessibility occlusion gap** (`increasedOcclusionLift`,
  `reducedTransparencyFrost` under-reach the native material) — recorded as a
  Surprise in the wave spec; tuning it needs the provisional profiles to gain
  a split first (tuning against calibration-only cells is fitting without a
  holdout).
- **Rim estimator candidate at 2×** — named, not adjudicated; claims §6.2's
  no-rim-thresholds ruling stands; needs a rim-specific investigation.
- `apps/reference-apple/fixtures/backgrounds/index.json` is unread; delete or
  scale-qualify at the next batched harness rebuild.
- The 2× holdout is SPENT for this configuration; W2/W3 must not fit to it.
