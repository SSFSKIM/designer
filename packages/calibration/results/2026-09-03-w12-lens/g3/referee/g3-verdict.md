# W12 G3 landing round — the verdict against §5.56 §4's six stops

Refereed 2026-09-03 from the landing worktree, twelve runs (both renderers over the six
profiles), all exit 0. Baselines: the material on `main` (the webgpu rows of the ω 0.8
round, the css rows of the G2 landing) and the 0.3.0 bed.

| stop | verdict |
| --- | --- |
| 1. W12's stops of §5.51 §3 | **PASS with one named exception.** 14 cells moved past 0.005 against the 0.3.0 bed and are named in `g3-scan.md`; every adopted bound and every regression floor holds (the adopted-thresholds run against this matrix fails only on bookkeeping — two cells the conditioning predicate now admits). Six 2x GPU *solid* captures differ by exactly **1 code value**; at 1x every solid capture is byte-identical. |
| 2. 1x is unchanged | **PASS.** 132 of 132 1x rows moved by +0.000000 SSIM. One 1x capture differs, by one code value: `photo__capsule-button__rest-tint-orange-half` on the CSS tier, whose SSIM is unmoved to six decimals. |
| 3. 2x moves as predicted | **FAIL.** All three 2x GPU texture rows moved DOWN, not up. |
| 4. the 2x CSS rows | **PASS.** No 2x CSS row is more than 0.002 below `main`; `rrect-ml` +0.0045 and `rrect-lg` +0.0024 against predictions of +0.0030 and +0.0004. |
| 5. renderer goldens | **NOT MET as stated, and the premise is wrong.** Every committed golden scene declares `devicePixelRatio: 2`, so there is no dpr-1 golden to be identical at; six of nine isolation hashes moved and two scene goldens exceed the suite's tolerance. |
| 6. by eye | the user's. Sheets and A/B composites are beside this file. |

## Stop 3 in numbers (webgpu, 2x light standard, checkerboard)

| row | on `main` | predicted (§5.56 §3) | measured | against the prediction |
| --- | --- | --- | --- | --- |
| `rrect-md` | 0.9517 | 0.9545 | **0.9451** | −0.0094 |
| `rrect-ml` | 0.9158 | 0.9219 | **0.9041** | −0.0178 |
| `rrect-lg` | 0.9113 | 0.9164 | **0.9078** | −0.0086 |
| `rrect-sm` | 0.9978 | 0.9974 | 0.9975 | +0.0001 |
| `capsule-button` | 0.9836 | 0.9832 | 0.9830 | −0.0002 |

All three still clear their pinned floors (`rrect-ml` 0.9041 ≥ 0.9013, `rrect-lg` 0.9078 ≥
0.9002) and `rrect-md` still clears 0.93 — so nothing regressed past a floor — but the
round's whole purpose was the rise, and it did not happen.

## Where the loss is, and why the dry run did not see it

`g3-where.txt` splits the same SSIM map the matrix scores into §5.41's interior box, the
band (0–24 CSS px inside the contour, outside that box) and the outside:

| row | whole | interior box | band < 24 | outside |
| --- | --- | --- | --- | --- |
| `rrect-md` | −0.0066 | −0.0249 | **−0.0293** | +0.0002 |
| `rrect-ml` | −0.0117 | −0.0097 | **−0.0399** | +0.0002 |
| `rrect-lg` | −0.0034 | **+0.0039** | **−0.0140** | +0.0003 |

Two facts, and the second is the one that matters:

1. **The band carries the loss on all three.** §5.41 §4's dry run — the method §5.56 §3's
   predictions come from — replaces vitrea's capture inside the interior box only and
   leaves the rim band and the outside untouched *by construction*. The landing capture
   changes all three, because the lens reads the body at the refracted position (W12 G2):
   a narrower body is a narrower band, and at 2x the band is where the reference and
   vitrea now disagree most.
2. **Even the interior box does not reproduce the prediction on `rrect-md` and `-ml`.**
   The dry run evaluates the candidate law at the **reference cell's own level and
   transmission**, and the probe fit that chose Δk = 0.35 carried level and transmission
   as free nuisance parameters. The runtime has neither: it renders at vitrea's own
   transmission, measured at 0.24 against the reference's 0.41 (§5.49 §7). Raising the
   heavy weight from k to k + 0.35 collapses the *sharp* component's share — on a 96 px
   span at 2x, from 0.48 to 0.13 — and at vitrea's own transmission that costs more
   retained structure than the narrower kernel returns.

`g3-interior-std.txt` is the same fact in the compare's own reading of retained structure,
`interiorStdDev`, at 2x light standard (native | main | G3):

| component | native | main | G3 (webgpu) | main | G3 (css) |
| --- | --- | --- | --- | --- | --- |
| `rrect-md` | 0.1272 | 0.0973 | **0.0611** | 0.0694 | **0.1103** |
| `rrect-ml` | 0.1018 | 0.0746 | **0.0411** | 0.0440 | **0.0915** |
| `rrect-lg` | 0.0810 | 0.0525 | **0.0379** | 0.0262 | **0.0888** |

The CSS tier moves toward the native reading and the GPU tier moves away from it, from the
same constants through the same shared functions — because a single `blur()` sees only the
interpolated σ (which narrows) while the GPU tier's two-component body also sees the weight
(which shifts onto the heavy tap). At 1x both tiers are unmoved to four decimals.

## What this does not say

The implementation is faithful to the declaration, on the evidence available: every 1x row
and 131 of 132 1x captures are byte-identical, the unit tests pin both tiers' formulas to
twelve decimals over dpr ∈ {1, 1.5, 2, 3}, and the tier without a lens moved in the
predicted direction by roughly the predicted amount. What failed is the prediction, and the
two normalisations it rests on — the reference's level and transmission, and the untouched
band — are named above.
