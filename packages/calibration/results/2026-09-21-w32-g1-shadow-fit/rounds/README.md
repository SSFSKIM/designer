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
| A | `spreadPx` 3.10 → **0.50** (light) and → **1.80** (dark) | **0.00176** | **0.00225** | 0.00063 | — |

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

### A — the outset, and it is the whole story

`spreadPx` 3.10 → 0.50 on the light document and 3.10 → 1.80 on the dark one; the σ law, the
offset and all thirteen amplitude leaves unmoved; the recede still at zero. Two values in one
round, for the reason stated above — the documents are independent and the axis is sampled twice.

**The objective falls by a factor of two and a half on the light bed and a third on the dark one**,
from one leaf that no measurement had ever fitted on the macOS 27 bed (§5.162 §2): light 0.00480 →
**0.00176**, dark 0.00381 → **0.00225**. Per span, `T`:

| bed | 32 | 44 | 96 | 128 | 160 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1x light | 0.00294 → 0.00145 | 0.00339 → 0.00172 | 0.00408 → **0.00144** | 0.00843 → **0.00243** | 0.00796 → **0.00397** |
| 2x light | 0.00288 → 0.00146 | 0.00337 → 0.00176 | 0.00413 → **0.00151** | 0.00889 → **0.00230** | 0.00797 → 0.00463 |
| 1x dark | 0.00171 → 0.00121 | 0.00201 → 0.00146 | 0.00399 → **0.00204** | 0.00782 → **0.00389** | 0.00659 → **0.00265** |
| 2x dark | 0.00168 → 0.00115 | 0.00199 → 0.00148 | 0.00385 → **0.00219** | 0.00738 → 0.00421 | 0.00627 → **0.00222** |

Against C1's ruled bound of 0.0042 that is **ten of twelve bed × span rows PASSING** where four
passed before, with the two misses `2x light` at span 160 (0.00463, by 10 %) and `2x dark` at span
128 (0.00421, by 0.2 %). Candidate (i), the wave's headline, closes by a third at every bed and
span: the rendered σ minus the native σ runs **+2.39 to +2.69 CSS px** where it ran +3.11 to +3.77,
and `(i)` itself 0.414 → 0.272 on 1x light at span 96. Still outside B1's ±5 % window on all
twelve, which is the reading and not a gate (§5.162 §5).

**And the per-band table says why one leaf did this.** The `3-6` / `6-12` / `12-24` `Δa` at span
128 on 1x light moves −0.0075 / −0.0093 / −0.0090 → **+0.0042 / +0.0002 / −0.0030**: the profile
crosses Apple's instead of sitting under it everywhere. The whole exterior does not improve — at
the same cells the `0-3` band goes **0.1058 → 0.1154**, further from Apple, because a smaller
outset moves the profile inward and the `0-3` band loses what the shadow bands shed. That is the
body's own over-fill (§5.62) and is the other half of B3's story below.

**B3 reads 0.00063 against ≤ 0.00035**, and now both poses contribute:

| pose | n | pre-fit | R | A |
| --- | ---: | ---: | ---: | ---: |
| active | 85 | 0.00029 | 0.00029 | **0.00047** |
| inactive | 81 | 0.00039 | 0.00080 | 0.00080 |
| pooled — the stop | 166 | 0.00034 | 0.00054 | **0.00063** |

The **window-restricted** departure, the quantity the anchors are solved on, moves the other way at
every thick span: 1x light 96 0.00176 → **0.00062**, 128 0.00433 → **0.00059**, 160 0.00463 →
**0.00172**. So the two statistics disagree in SIGN about this round, which is §5.166 §6's finding
arriving as a consequence rather than as a caution.
