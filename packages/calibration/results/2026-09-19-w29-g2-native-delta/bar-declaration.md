# The noise bar, declared — W29 G2, before any 26.5 pair is read

W29 acceptance clause 3 and Decision Log 1 (ii); claims §5.151. This file and `noise-bar.json`
are committed **before** the commit that reads a single 26.5 fixture against a 27 one. Nothing in
this gate has yet compared the two beds.

## The instrument

`packages/calibration/cli/native-delta.ts`, with `cli/native-delta-metrics.ts` (the pair reader)
and `cli/native-delta-readers.ts` (the two declared-geometry rim readers W23 and W24 built).

**It lives in `cli/`, not in this results directory, and that is a judgement.** A one-wave script
belongs beside its numbers; this is not one. A bed-against-bed read is what every OS recapture
needs — 26.5 against 27 now, 27 against 28 later — and the charter's own Design sites it at
`cli/native-delta.ts` shaped like `tier-delta.ts`. More decisively, acceptance clause 3 asks for
"the same metric primitives the fidelity read uses", and those primitives are the TypeScript ones
in `packages/calibration/src/metrics/`: putting the driver anywhere else would mean either
re-implementing them or reading them from another language. It typechecks under
`tsconfig.cli.json`, lints under the package's config and is covered by
`test/native-delta.test.ts`, which a script under `results/` is not.

The two rim readers were Python (`results/2026-09-08-w23-collapsed-rim/g0/read-contour.py`,
`results/2026-09-09-w24-lit-edge/g0/read-angular.py`) and are ported rather than shelled out to,
for the one reason that decides it: **the bar and the delta must be the same function of a pair of
captures**, or the bar does not bound the delta. The ports are checked against those instruments'
own committed 26.5 output by `native-delta.ts verify-readers`; the agreement is in
`verify-readers.txt` beside this file.

## The construction

For each of the 624 cells of the macOS 27 bed, and for each metric:

> the distribution of that metric over **all 21 unordered pairs of the cell's seven raw macOS 27
> runs**, the lower-numbered run of each pair taken as the reference side.

Pairwise, and not each run against the published fixture, because the delta is a comparison of two
independently captured, equally valid renderings of one declared cell — and that is exactly what a
pair of runs is, while the published bytes are privileged by the plurality and are one of the runs'
anyway. The run-against-published distribution is computed and recorded beside it, because it is
the form the charter names first and because it is a subset of the same behaviour; it is
corroboration and it is not the bar.

The raw runs are `~/vitrea-w29-27-run/<mode>-<pose>-<scale>x/run-N/<profileKey>/<sceneId>.png` and
they stay on the capture machine, as a sitting's snapshots do. What is committed is the derived
per-cell distribution.

## The rule

> **MOVED** on a metric means the 26.5-against-27 value **exceeds the MAX** of that cell's own
> 27-against-27 pairwise distribution.

The max and not a quantile. At 21 samples a tail quantile is not better estimated than the extreme,
and the statement the ledger needs is the strict one: *beyond anything this bed did against itself*.
The whole distribution — min, median, p95, max — is recorded per cell and per metric, so a reading
at a softer bar can be taken later without re-running the sitting.

**Cells whose own spread is exactly zero on a metric** — seven byte-identical runs, which the
sitting has 505 unanimous cells' worth of — take as their bar the **smallest non-zero pairwise max
anywhere in the 27 bed for that metric** (`bedMinimumNonZeroBar` in `noise-bar.json`, and the row
records `barSource: "bed-minimum"`). A cell that happened to be perfectly stable must not be handed
an infinitely sharp instrument; the bed's own finest resolved difference on that metric is the
sharpest honest bar available.

**Amended once, on the bar's own output and before the first pair was read** (2026-09-19). Three
metrics have **no** non-zero pairwise max anywhere in the bed — `contourDistanceP95Px` (610 of 610
cells at zero), `oklabDeltaEP95` (624 of 624) and `rimPeakDepthDeltaPx` (610 of 610) — because a
95th percentile over pixels and a rounded ring index are both blind to the handful of pixels a
re-run moves. The rule above is silent there, so it is extended: **the bar is exactly zero, and
moved means a non-zero reading.** That is the strongest of the three levels rather than the
weakest — a non-zero cross-bed value on such a metric is beyond every one of the bed's 13,104
within-bed pairs — and the rows record it as `barSource: "bed-zero"` so that no verdict resting on
it can be mistaken for one resting on a cell's own spread. The amendment changes no figure already
committed: `noise-bar.json` was written before it and is unchanged by it.

**One reading the bar gives for free, as a check on itself.** The number of cells whose whole-cell
metrics (`ssimComplement`, `oklabDeltaEMean`, `edgeWeightedMean`) have exactly zero spread across
all 21 pairs is **505 of 624** — precisely the sitting's count of cells published unanimously across
all seven runs (§5.150 Part B §4). Two independent constructions, one on bytes and one on metrics,
agreeing cell for cell.

A metric a cell cannot measure — a composite component with no declared box, a solid backdrop that
identifies no luminance transfer, a silhouette empty inside the declared region — is **absent**,
with its reason, and never zero.

## What the bar cannot say, stated once and carried on every reading

It is a **27-against-27** bar. The 26.5 bed's own run-to-run variation is not in it and is not
derivable: that bed's plurality record is byte-level and transient, carries no SSIM, ΔE or contour
distribution, and 38 % of its cells can be attributed no capture bar at all (§5.149 §6; Decision
Log 1 (iii)). So every verdict of "moved" understates the combined spread of a cross-bed pair by
whatever the 26.5 side's own spread was — the bar is a **floor** on the evidence a claim needs, not
a ceiling. A cell that fails to move is therefore a weaker statement than a cell that moves.

## The metrics

Every metric is a **non-negative distance** between two captures of one declared cell, so that one
comparison — "beyond the bar" — works on all of them. A similarity enters as its complement; a
level enters as the absolute difference of the two readings. The signed readings of both sides are
carried beside the distances, because "Apple darkened the edge" needs a direction and a distance
has none.

| law | metrics |
| --- | --- |
| silhouette / geometry | `silhouetteIoUComplement`, `contourDistanceMeanPx`, `contourDistanceP95Px`, `silhouetteAreaDeltaPx` |
| corner geometry | `cornerCurvatureDeltaPerPx` (the characteristic corner curvature of each contour, 1/px) |
| perceptual, whole cell | `ssimComplement`, `ssimBandComplement`, `ssimInteriorComplement`, `ssimOutsideComplement`, `oklabDeltaEMean`, `oklabDeltaEP95`, `edgeWeightedMean` |
| body | `oklabDeltaEBodyMean` (ΔE under the reference silhouette) |
| interior level | `interiorMeanDelta`, `bodyLevelDelta` (the declared box eroded 6 CSS px — mask-free) |
| scatter / diffusion | `interiorStdDevDelta` (the material's frosting strength against the backdrop's own structure) |
| tone response by backdrop | `transferSlopeDelta`, `transferOffsetDelta` (the affine fit of rendered against backdrop luminance, in linear light) |
| rim band / edge darkening | `rimContourDeltaMax`, `rimLocalDeltaMax`, `rimRow0DeltaMax` (W23, per side on the straight span), `rimPeakDelta`, `rimPeakDepthDeltaPx`, `rimFwhmDeltaPx` (the radial profile) |
| highlight amplitude and position | `highlightBinDeltaMax`, `highlightBinDeltaMean`, `highlightIntegralDeltaMax`, `highlightRatioDelta`, `highlightPeakAngleDeltaDeg` (W24, sixteen 22.5° bins around the whole boundary) |
| tint shade | `tintDeltaLDelta`, `tintChromaDelta`, `tintHueShiftDeltaDeg` |

The recede is not in this table. It is a **difference of differences** —
`(27 inactive − 27 active) − (26.5 inactive − 26.5 active)` — so it is built from the signed
per-capture readings rather than from pair distances, and its bar is the sum of the two 27 cells'
own run-to-run reading spreads (`readingSpread` in `noise-bar.json`). The 26.5 pair contributes an
unmeasured amount on top of that, exactly as above.

## What this gate has not done

It has not read one 26.5 fixture against one 27 fixture. It has changed no material, no profile
document, no bound, no floor, no golden and no row of `results/matrix.json` (X3). It has taken no
capture.
