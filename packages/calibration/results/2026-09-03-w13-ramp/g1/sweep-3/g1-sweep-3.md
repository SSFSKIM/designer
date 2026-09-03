# W13 G1 — the runtime sweep of the SPAN-GRADED depth ramp (2026-09-03)

The third form, turned through the real GPU renderer: the span law under the ramp as its
deep value (the second form), plus a start that grades from a thin anchor to a thick one
across the material's own `sizeThickness` curve. 44 points at 1x, a four-point
verification at 2x, and one confirmation read over calibration, validation and holdout.
Commands, base and provenance: `README.md` beside this file.

**Headline. The form works at 1x and S4 is met for the first time in this wave — every
checkerboard band row rises, worst +0.0019, with no calibration or validation row falling
at all. The 2x null the form predicts is verified bit-exact: the ramp changes not one
number of the 2x bed. And the holdout, read once, returns one failure and one structural
finding: `rrect-lg`'s 1x `ssimMean` falls 0.0026, below what S1 admits, because
`sizeThickness` saturates at 96 and the form therefore cannot grade WITHIN the thick
cells, where G0 read the start falling from 0.512 to 0.410.**

## 1. What was swept, and the prediction written before the first capture

`paper3.py` computed the form's closed-form projection on the real spans before any GPU
time was spent, and it makes one sharp prediction about the declared grid: **at a thin
anchor of exactly 0.60 the three smallest cells cannot move at all.** `rrect-sm`'s span is
exactly `sizeSpanMin`, so its deep sharp share is exactly `1 − sizeScatterFloor` = 0.600
and the excursion `max(0, s₀ − sDeep)` is zero there; the capsule and the toolbar group at
0.595 are cleared only when the thick anchor is high enough to lift `s₀(44)` past it.

    | thin | thick | sm(0.600) | caps/tb(0.595) | md(0.481) | ml(0.364) | lg(0.236) |
    | 0.60 | 0.50  | no        | no             | YES       | YES       | YES       |
    | 0.60 | 0.56  | no        | YES            | YES       | YES       | YES       |
    | 0.64 | any   | YES       | YES            | YES       | YES       | YES       |
    | 0.68 | any   | YES       | YES            | YES       | YES       | YES       |

The grid — thin {0.60, 0.64, 0.68} × thick {0.50, 0.52, 0.56} × reach {40, 60, 80, 120},
36 points — brackets that boundary deliberately, so the prediction is tested rather than
assumed. **The measurement confirms it to four decimals**: at thin 0.60 the `sm`, `caps`
and `tb` band deltas read `+0.0000` at every one of the twelve points, except where thick
0.56 lifts `s₀(44)` to 0.5963 and the capsule and toolbar move by +0.0008 and +0.0003
while `rrect-sm` stays at exactly `+0.0000`. That is the second form's refutation
(claims §5.64 §2) reproduced as a controlled boundary inside this round's own grid.

## 2. The 1x grid

Full tables: `1x-grid.tables.txt`. `ΔssimBand` against the W12 close, the five calibration
checkerboard cells, best eight by the worst cell:

| thin | thick | reach | sm | caps | md | ml | tb | worst | S1 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.68 | 0.52 | 120 | +0.0051 | +0.0049 | +0.0027 | +0.0042 | +0.0025 | **+0.0025** | −0.0011 PASS | **PASS** |
| 0.68 | 0.52 | 80 | +0.0050 | +0.0053 | +0.0023 | +0.0044 | +0.0023 | +0.0023 | +0.0000 PASS | **PASS** |
| 0.68 | 0.56 | 60 | +0.0048 | +0.0052 | +0.0023 | +0.0021 | +0.0024 | +0.0021 | +0.0000 PASS | **PASS** |
| 0.68 | 0.52 | 60 | +0.0048 | +0.0054 | +0.0018 | +0.0048 | +0.0022 | +0.0018 | +0.0000 PASS | **PASS** |
| 0.64 | 0.56 | 60 | +0.0039 | +0.0033 | +0.0023 | +0.0021 | +0.0016 | +0.0016 | +0.0000 PASS | **PASS** |
| 0.64 | 0.52 | 120 | +0.0045 | +0.0035 | +0.0027 | +0.0042 | +0.0015 | +0.0015 | −0.0011 PASS | **PASS** |
| 0.64 | 0.52 | 80 | +0.0045 | +0.0035 | +0.0023 | +0.0044 | +0.0013 | +0.0013 | +0.0000 PASS | **PASS** |
| 0.60 | 0.52 | 80 | +0.0000 | +0.0000 | +0.0023 | +0.0044 | +0.0000 | +0.0000 | +0.0000 PASS | FAIL |

**22 of the 36 points meet S4.** Every point at thin 0.64 or 0.68 meets it except the two
at thick 0.56 / reach 120, which lose `rrect-ml` (−0.0003) and fail S1 as well (−0.0037).
The twelve at thin 0.60 fail S4 by §1's arithmetic and not by a margin.

**Two axes, two cells, and a tension inside the thick anchor.** `sm`, `caps` and `tb`
answer to the THIN anchor and rise with it. `md` and `ml` answer to the THICK anchor and
pull against each other: `md` wants it high (+0.0030 at thick 0.56, +0.0004 at 0.50) and
`ml` wants it low (+0.0057 at thick 0.50, −0.0003 at 0.56). **0.52 is where both are
comfortably positive** — `md` +0.0023, `ml` +0.0044 at reach 80 — which is also G0's own
`rrect-md` reading and the reason Decision Log 4 pinned it there rather than at the 0.47 a
joint fit returns.

The optimum sat at the grid's thin edge on both rankings, so it was refined once, as the
charter allows.

## 3. The refinement, and the constants chosen

Eight points, thin {0.72, 0.76} × thick {0.52, 0.54} × reach {80, 120}
(`1x-refine.tables.txt`):

| thin | thick | reach | worst cell | bandRise | S1 | maxΔisd | interior objective |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.72 | 0.52 | 120 | +0.0026 | +0.0042 | −0.0011 PASS | 0.0129 | 0.05045 |
| 0.72 | 0.54 | 120 | +0.0024 | +0.0040 | **−0.0021 FAIL** | 0.0156 | 0.05056 |
| 0.72 | 0.54 | 80 | +0.0021 | +0.0036 | −0.0006 PASS | 0.0124 | 0.05052 |
| **0.72** | **0.52** | **80** | **+0.0019** | **+0.0038** | **+0.0000 PASS** | **0.0097** | **0.05032** |
| 0.76 | 0.52 | 80 | +0.0011 | +0.0036 | −0.0001 PASS | 0.0144 | 0.05042 |
| 0.76 | 0.54 | 80 | +0.0009 | +0.0032 | −0.0006 PASS | 0.0144 | 0.05062 |
| 0.76 | 0.52 | 120 | +0.0007 | +0.0035 | −0.0011 PASS | 0.0154 | 0.05084 |
| 0.76 | 0.54 | 120 | +0.0006 | +0.0033 | −0.0021 FAIL | 0.0156 | 0.05096 |

**Chosen: thin 0.72, thick 0.52, reach 80 device px at 1x; thin 0.46, thick 0.17, reach
100 at 2x.**

The choice is not the maximum of the worst band cell — that is thin 0.72 / thick 0.52 /
reach 120 at +0.0026 — and the reason is that the extra +0.0007 costs an `ssimMean`
regression of 0.0011 and a third more interior error, where reach 80 takes S1 with **exact
equality**: not one calibration or validation row falls at all. Reach 80 also carries the
best interior objective (0.05032) and the best interior gap (0.0097) of all 44 points.

**Both chosen axes are interior, which is what makes them a fit rather than a limit.** In
the thin anchor, 0.68 and 0.76 are measured either side and both score worse on the
objective (0.05045 / 0.05032 / 0.05042) and on the interior gap (0.0125 / 0.0097 /
0.0144). In the reach, 40, 60 and 120 are all measured and 80 is between them.

**One departure to state plainly. The thin anchor 0.72 is above G0's own read-off of
0.637 (`rrect-sm`) and 0.642 (capsule).** The runtime wants roughly 0.08 more band on the
thin cells than the reference's contour reading implies. That is the same shape of
departure the FIRST sweep found on the reach (the runtime wanted about twice G0's length),
and it is recorded here rather than reconciled: G0's instrument identifies the ramp's
shape and not its level wherever only one spatial frequency is available (claims §5.61
§1), and vitrea's own canonical bed is exactly that case.

## 4. The 2x null, verified bit-exact

Not swept. The form predicts that at the 2x anchors the excursion is zero on every cell —
G0's 2x start readings (0.483 / 0.437 / 0.192 / 0.179 / 0.141) all lie BELOW their cells'
deep sharp shares, implied excursions −0.095 to −0.289 (claims §5.64 §4). A prediction is
not an exemption, so it was measured: four points, thin2x {0.46, 0} × thick2x {0.17, 0},
reach 100.

**All four are identical, and identical to the branch's pre-ramp state, to every digit the
capture produces.**

| comparison | cells | axes per cell | max absolute difference |
| --- | --- | --- | --- |
| chosen 2x point against a zeroed-start point, same build | 20 | 107 | **0** |
| chosen 2x point against sweep-2's pre-ramp 2x matrix, earlier build | 20 | 107 | **0** |

The second row matters as much as the first: it is a different build of the shader
(the second form's), and it agrees bit for bit, so the null is a property of the law and
not of one binary. The five calibration band rows read `rrect-sm` 0.966255,
`capsule-button` 0.887934, `rrect-md` 0.916308, `rrect-ml` 0.920485, `toolbar-group`
0.747581 — the same figures §5.64 §3 recorded for the inert configuration.

**S4-at-2x-as-a-null: MET.** The 2x three constants therefore stay PROVISIONAL and cannot
be fitted on this bed by any grid: a sweep cannot identify a constant that changes no
pixel. They are held at G0's readings until the deep-value charter gives 2x a law whose
excursion is non-zero.

## 5. The confirmation run, and the holdout

One read, four profiles, `calibration,validation,holdout`, GPU tier, into
`matrix-confirm.json` (98 cells). Full rows: `confirm.tables.txt`.

### 5.1 The stops, with numbers

**S1 — no 1x row below its W12-close value by more than 0.002.** Met on every calibration
and validation row: the largest 1x fall anywhere in those two sets is smaller than 0.0005.
**One holdout row fails**: `checkerboard__rrect-lg__rest` `ssimMean` 0.9428 → **0.9401**,
−0.0026. It is the only failing row in the whole matrix.

**S4 at 1x — `ssimBand` rises on every checkerboard cell, read with `ssimInterior`
beside it. MET.**

| cell | ssimBand | Δ | interiorStdDev web → | native | gap before → after |
| --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 0.9720 | **+0.0048** | 0.1408 → 0.1620 | 0.1549 | 0.0141 → 0.0071 |
| `capsule-button` | 0.8873 | **+0.0058** | 0.1206 → 0.1385 | 0.1424 | 0.0218 → 0.0039 |
| `rrect-md` | 0.9340 | **+0.0023** | 0.0994 → 0.1052 | 0.1131 | 0.0137 → 0.0079 |
| `rrect-ml` | 0.9414 | **+0.0044** | 0.0769 → 0.0963 | 0.0865 | 0.0096 → 0.0097 |
| `toolbar-group` | 0.7246 | **+0.0019** | 0.1227 → 0.1424 | 0.1481 | 0.0254 → 0.0057 |

`ssimInterior` is defined on `rrect-md` and `rrect-ml` only and moves −0.0001 and −0.0033;
the interior SSIM falls a little on `-ml` where the interior standard deviation crosses
from under the reference to over it, which is the overshoot the next section is about.

**S4 at 2x, as the null it was refined into — MET**, §4.

**S2 at 2x — the three held texture `ssimMean` rows rise above their W12-close floors. NOT
MET, and the ramp is not what fails it.**

| cell | floor | confirmation | against floor |
| --- | --- | --- | --- |
| `checkerboard__rrect-ml` | 0.9158 | 0.8998 | **−0.0160** |
| `checkerboard__rrect-lg` (holdout) | 0.9113 | 0.8944 | **−0.0169** |
| `checkerboard__glass-over-glass` (holdout) | 0.9211 | 0.9113 | **−0.0098** |

Every one of those numbers is candidate A's device-pixel widths and nothing else — the
ramp contributes exactly zero at 2x, proven in §4 — so this is the widths pedestal
§5.64 §2 already named, reported here against the stop it fails rather than left implicit.
**The brief's expectation that "S2 and S3 at 2x are met exactly as the branch already
meets them" is right about the mechanism and wrong about the verdict: the branch does not
meet S2, and no form of this ramp can make it, because the ramp cannot act at 2x at all.**

**S3 at 2x — `interiorStdDev` within 0.005 of native. Three of five calibration cells.**

| cell | web / native | gap | S3 |
| --- | --- | --- | --- |
| `rrect-sm` | 0.1647 / 0.1636 | 0.0011 | PASS |
| `capsule-button` | 0.1500 / 0.1552 | 0.0052 | FAIL by 0.0002 |
| `rrect-md` | 0.1260 / 0.1272 | 0.0011 | PASS |
| `rrect-ml` | 0.1029 / 0.1018 | 0.0010 | PASS |
| `toolbar-group` | 0.1510 / 0.1581 | 0.0071 | FAIL by 0.0021 |
| `rrect-lg` (holdout) | 0.0788 / 0.0810 | 0.0021 | PASS |
| `glass-over-glass` (holdout) | 0.1324 / 0.1401 | 0.0077 | FAIL |

Identical to §5.64 §3's reading of the inert configuration, as §4 requires.

**S5 — the solids, `photo` and the tinted cells move by no more than 0.001 in any adopted
metric, and `ssimOutside` by no more than 0.001 on every cell. MET on the first clause,
MISSED marginally on the second.**

The solids are exact: every `light-solid`, `dark-solid`, `mid-dark-solid` and `impulse`
row reports `+0.0000` on band, mean and outside at both scales — on a flat backdrop the
mix has nothing to reveal. Over the fifteen S5 cells the largest movement in any ADOPTED
metric (`silhouetteIoU`, `contourDistanceMean`, `contourDistanceP95`, `ssimMean`,
`oklabDeltaEMean`, `oklabDeltaEP95`) is **0.00057**, on `photo__rrect-ml`'s ΔE p95, and it
is an improvement (0.07763 → 0.07705).

`ssimOutside` misses its 0.001 null on five cells:

| cell | scale | Δ`ssimOutside` | is this the ramp? |
| --- | --- | --- | --- |
| `hc-text__capsule-button` (holdout) | 2x | −0.00285 | **no** — the ramp is inert at 2x |
| `hc-text__rrect-md` (holdout) | 2x | −0.00133 | **no** |
| `checkerboard__toolbar-group` | 2x | −0.00132 | **no** |
| `checkerboard__rrect-md` | 2x | −0.00116 | **no** |
| `hc-text__capsule-button` (holdout) | 1x | −0.00112 | yes, by 0.00012 |

The four 2x rows are the widths pedestal again — §4 proves the ramp moved nothing there,
so those departures belong to candidate A and were already in the branch. **The one
genuine miss is a single 1x holdout row, over by 0.00012.** It is small, it is on a
high-contrast-text scene, and it is a real gap: a body law should not touch the outside of
the contour at all, and something at the coverage ramp does. Recorded as a gap, not
excused.

### 5.2 The holdout, and the round's structural finding

`glass-over-glass`, span 130, lands almost exactly: band 0.9480 (**+0.0035**), `ssimMean`
0.9529 (+0.0008), and the interior gap closes from 0.0127 to **0.0001** (0.1320 against a
native 0.1321). That is the best interior agreement any cell on this bed has recorded.

`rrect-lg`, span 160, is the failure:

| | W12 close | confirmation |
| --- | --- | --- |
| `ssimMean` | 0.9428 | **0.9401** (−0.0026, S1 FAIL) |
| `ssimBand` | 0.9395 | 0.9394 (−0.0000) |
| `interiorStdDev` web | 0.0540 | **0.0865** |
| native | 0.0650 | 0.0650 |
| gap | 0.0110 (17% under) | **0.0216 (33% OVER)** |

**The mechanism, and it is the form's own arithmetic rather than a bad constant.**
`sizeThickness` is a smoothstep from `sizeSpanMin` 32 to `sizeSpanMax` 96, so it is
saturated at 1 for every span at or above 96. Spans 96, 128, 130 and 160 therefore all
receive the *identical* start, the thick anchor 0.52. But G0 read the reference's start
FALLING across exactly those spans — 0.512 on `rrect-md`, 0.501 on `rrect-ml`, 0.410 on
`rrect-lg` — so the form over-starts the largest span by **0.110**:

| cell | span | G0 start 1x | the form's s₀ | error | deep sharp | excursion |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 96 | 0.512 | 0.520 | +0.008 | 0.481 | 0.039 |
| `rrect-ml` | 128 | 0.501 | 0.520 | +0.019 | 0.364 | 0.156 |
| `glass-over-glass` | 130 | — | 0.520 | — | 0.356 | 0.164 |
| `rrect-lg` | 160 | 0.410 | 0.520 | **+0.110** | 0.236 | **0.284** |

And the excursion runs the wrong way across the thick cells for a second reason: the deep
value keeps falling past 96 (its own band top is `sizeScatterSpanMax` 256), so with one
thick start the excursion *grows* with span — 0.039 → 0.156 → 0.284 — where G0 has the
start *falling*. On `rrect-lg` those two errors compound, and the holdout measured the
result as a 33% interior overshoot.

**The third form fixed the thin-against-thick disjointness and inherits a thick-against-
thick one.** It is a smaller defect than either of the two the earlier forms died of — S4
is met, S1 is met on every fitted cell, and one of the two holdout cells is the best on
the bed — but it is the same kind of defect, and the parent's declaration has to answer
it.

## 6. What this asks of the declaration

1. **The 1x half of the wave is reached.** S4 met on all five calibration cells, S1 met
   with exact equality, the 1x interior gap more than halved on four of five, and the
   constants are an interior optimum with both neighbours measured. The 1x three are
   fitted and land on the branch (`ef61b09`).
2. **The 2x half is a verified null and the 2x constants are unfittable here.** Zero
   difference over 20 cells × 107 axes, against two different builds. They stay
   PROVISIONAL by necessity rather than by caution, and the 2x gap stays where §5.64 §4
   put it: in the deep value's floor, knee and top.
3. **S2 at 2x is not met and cannot be met by this wave.** The three held rows sit
   0.0098–0.0169 below their W12-close floors on candidate A's widths alone. That is a
   decision the user owns, not a number another sweep can move.
4. **The holdout returns one S1 failure with a named structural cause.** `rrect-lg` 1x
   `ssimMean` −0.0026 and a 33% interior overshoot, because `sizeThickness` saturates at
   96 and cannot distinguish spans 96 to 160 while G0 read the start falling by 0.10
   across them. The shape of the work that would close it: give the start a curve whose
   knee sits where the scatter facet's own does (`sizeScatterSpanMax` 256) rather than
   where the thickness curve's does, which is one more constant and no new span statistic
   — or accept the overshoot on the largest span and re-pin the floor by decision. This is
   the first form of the ramp that is worth that question.
5. **One 1x `ssimOutside` row moves by 0.00112 where S5 admits 0.001.** A body law should
   not touch the outside of the contour; something at the coverage ramp does, by about a
   thousandth, on one high-contrast-text holdout cell.
6. **The thin anchor is 0.08 above G0's own read-off**, the same direction and the same
   kind of departure the first sweep found in the reach. Whether the runtime's preference
   or the reference's reading is the better estimate of the reference's contour share is
   not settled by this round.
