# W32 G1 — the rounds

Claims **§5.168**. Each subdirectory is one rendered round of the fit bed: six macOS 27 profiles on
the WebGPU tier over calibration + validation + the widened ladder, active and inactive, at four
CANDIDATE documents built by `build-shadow.py` into a scratch tree. The canonical
`results/matrix.json` and the canonical `web-captures/` are never written by a round.

Each directory holds `constants.json` (the candidate, and the whole of it — a leaf not named there
is the shipped value), `documents.txt` (what was built, with B1's position at that σ law),
`exterior-cut.{txt,json}` (G0's reader), `c1-forms.{txt,json}`, `stops.{txt,json}`,
`departure-stat.{txt,json}` and `anchor-solve.txt` (the objective, both anchor solves, the
linearity check, the inactive pose and the per-backdrop residual).

**The objective**, per scheme, stated once: the mean over spans 32, 44, 96 and 128 of the upper
middle `T` at that span, over that scheme's two STANDARD beds, WebGPU tier, active, non-holdout,
cells whose identified band set equals their span's admitted set — equal weight per span. Span 160
is rendered and read at every round and is never in the objective. The two accessibility beds are
read every round and are not in the objective: their six anchors are overwritten by the
reduced-transparency fold, which X3 forbids this wave to move.

**Two points per round, deliberately.** The light and dark documents are independent patches over
`DEFAULT_MATERIAL_PROFILE` and a round renders one candidate per scheme, so a round that gives the
two schemes DIFFERENT values of a length samples that axis twice. The cross-scheme reading is used
as a prior on the SHAPE of the response and never as a fitted value for the other scheme; each
document's own value is read on its own beds.

## The trajectory

| round | what moved | light objective | dark objective | B3 (cal+val, WebGPU) | shipped? |
| --- | --- | ---: | ---: | ---: | --- |
| pre-fit | — (the shipped documents) | 0.00480 | 0.00381 | 0.00034 | the before |
| R | the receded documents' amplitude → 0 (Decision Log 2); the active material unmoved | 0.00480 | 0.00381 | **0.00054** | — |

### pre-fit — the before

The shipped documents. Reproduces the committed rows at |Δ| exactly 0 on all 346 cells that have
one (`../pre-fit/repro.txt`) and reproduces G0's committed statistics to the digit.

### R — Decision Log 2's stand-down, confirmed, and the stop it breaks

The four receded amplitude leaves and `reducedTransparencyOcclusion` set to 0 on both receded
documents; **every leaf of both ACTIVE documents unmoved**. The round is therefore two readings at
once: a confirmation of the stand-down on the inactive pose, and a repeat of the pre-fit bed on the
active one.

**The active bed is identical to the pre-fit's**, statistic for statistic — objective 0.00480 /
0.00381, `T` per bed per span the same to five decimals, candidate (i) the same to three, the thin
table unchanged. Nothing a receded document carries reaches an active cell, and the two renders say
so rather than the reasoning.

**The stand-down does exactly what Decision Log 2 predicted.** On every inactive row of every bed
at every span the window-restricted web departure goes to **0.000000** and the inactive `T` over
the admitted bands goes to **0.00000** — against a native side that was already exactly 0.000000
and 1.000000. What is left of vitrea's inactive exterior is `whole web` at **−0.000122 to
+0.000230**, which is the body's own edge in the `0-3` band and nothing else; the native side's
`whole nat` is **0.00024 to 0.01101**, which is Apple's one-device-pixel contour stroke. Nothing
draws in 3–48 px on either side on any inactive cell of this bed.

**And it breaks B3.** The stop reads **0.00054** against ≤ 0.00035, worst cell
`checkerboard__rrect-md__inactive` at 0.00372. Decomposed by pose over the stop's own 166 cells:

| pose | n | pre-fit | round R |
| --- | ---: | ---: | ---: |
| active | 85 | 0.00029 | **0.00029** |
| inactive | 81 | 0.00039 | **0.00080** |
| pooled — the stop | 166 | 0.00034 | **0.00054** |

The whole of the break is the inactive pose and none of it is the active fit, which keeps its own
17 % of headroom against the bound. The cause is structural and is measured rather than argued:
**B3 is stated over the WHOLE exterior, and on the inactive pose Apple's whole exterior is the
`0-3` band** — one device pixel of dark stroke at the contour (§5.166 §7 and its review closure).
Before the stand-down vitrea drew the ACTIVE shadow in the inactive pose, whose integral over the
whole exterior happened to sit near Apple's hairline's, so the two wrongs cancelled in B3's mean;
after it, the hairline is the entire residual and B3 reads it in full. The hairline is a RIM term
and is on this wave's Deferred list by name.

This is a miss and is recorded as one (X4). It is not widened and it is not re-fitted: Decision
Log 2 is the parent's ruling and the stand-down ships. A Decision Log draft on B3's re-statement
goes to the parent with §5.168 — the stop cannot separate a shadow from a rim on a pose whose
exterior is only a rim.
