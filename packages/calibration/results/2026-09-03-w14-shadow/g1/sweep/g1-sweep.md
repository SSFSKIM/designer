# W14 G1 — the runtime sweep of the outer shadow's composite (2026-09-03)

The G1 purpose executed on the amplitude law: the ten constants `MaterialOuterShadow` gained
at branch commit `6dd3b68` turned through the real renderer on the calibration cells, at both
scales, in both colour schemes and on both tiers, and read on the X7 affine pair —
`slopeALinear` (1 − a, the transmission the black term removes) and `interceptCLinear` (c, the
lift, linear luminance) at direction `below`, bands `3-6` and `6-12`. Commands, base
construction, scratch layout and the discarded first pass: `README.md` beside this file.

**Headline.** The two MEASURED thin anchors read back on the runtime and are kept unchanged
(0.33 within 0.0000 on the checkerboard capsule, 0.127 within 0.0011 on the light-solid
capsule — the wave's 2.4× gap closed to 1.3%). The four PROVISIONAL thick constants all move,
and the lift moves most: **`liftAmplitude` 0.0073 → 0.0100, `liftSpanFull` 128 → 118,
`thickOcclusionAt96` 0.379 → 0.370, `thickOcclusionAt128` 0.497 → 0.448.** At those four the
runtime reproduces the reference's pair on the two thick calibration cells to within 0.0000 /
0.0013 in 1 − a and 0.0000 / 0.0001 in c, at 1x and 2x alike. **`thickOcclusionAt160` cannot
be identified on this bed at all** — every span above 128 in the fixture set is holdout — and
§4 says what was carried instead and why the two rules that could have extrapolated it are
both contradicted by the one span where they can be tested.

## 1. What was swept, on what, and what it was read on

Fifteen rounds, 104 points, 5–8 s a point because `--scene` restricts each point to the cells
that identify the constant it turns. The constants act on separate regimes and were swept one
or two at a time on those cells rather than as one grid; the one pair that is genuinely
coupled — a thick anchor and the lift's amplitude — was swept as a 5 × 4 grid at each thick
span (§3).

`sweep.ts`'s own shadow objective (mean |Δ `meanDeparture`| over the whole exterior) is
printed on every round and ranks none of the tables below. It is one number for a facet this
wave splits in two, and on a cell where the black term dominates the exterior mean it cannot
see the lift at all. Every table here is read out of the point matrices on the pair.

The reference row in every table is the native fixture's own reading in that same point
matrix, so "native" is never a stale number. The W12 close bed
(`$TMP/w14/x7/matrix-x7-baseline.json`, the X7 baseline) supplies the Δ column in §7 and the
before-state everywhere: at the W12 close the GPU tier read 1 − a = 0.2790–0.2940 flat across
every backdrop and span and c ≡ 0.

**The cells the brief named that this bed cannot sweep.** `checkerboard__rrect-lg` (span 160),
`checkerboard__glass-over-glass` (130), `hc-text__*` and `mid-dark-solid__capsule-button` are
all **holdout**, and `sweep.ts` passes `--set calibration` and can select none of them. So the
mid plateau is identified on the checkerboard and `photo` rather than on `hc-text` and
`mid-dark-solid`, the span-130 anchor is not identified at all, and §4's span-160 constant has
no cell. This is a property of the split, not of the sweep.

## 2. The thin regime — both MEASURED anchors read back, and are kept

`f1`, 1x light, GPU tier, band `3-6` below, occlusion 1 − a (web / native):

| cell | span | native | 0.30 | **0.33** | 0.36 |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button` | 44 | 0.2192 | 0.2003 | **0.2192** | 0.2417 |
| `checkerboard__rrect-sm` | 32 | 0.2179 | 0.1921 | **0.2125** | 0.2344 |
| `photo__capsule-button` | 44 | 0.2064 | 0.1992 | **0.2203** | 0.2403 |
| `dark-solid__capsule-button` | 44 | 0.0442 (level) | 0.0000 | **0.0000** | 0.0000 |

Solving each cell for the value that meets its native reading gives 0.330, 0.338 and 0.310 —
a spread of ±4% around the measured anchor, which is the cell-to-cell scatter G0 already
reported (0.327–0.347 across five backdrops). **0.33 is kept.** At `6-12` the same three cells
read 0.1838 / 0.1755 / 0.1910 against native 0.1776 / 0.1752 / 0.1700, so the tail is 3–12%
heavy where the peak is right — a falloff-shape residual, not an amplitude one, and W8's
lengths are not this wave's to refit (claims §5.62 §4).

`dark-solid` is the null and it holds exactly: the reference removes 0.0442 of the level in
`3-6` and 0.0004 by `6-12`, vitrea removes 0.0000 at every anchor. The facet is inert over
black on both terms, which is stop S5's own reading.

`f2`, the bright anchor on the one cell that carries it —
`light-solid__capsule-button`, occlusion off the level (no affine: the backdrop is flat):

| band | native | 0.10 | **0.127** | 0.15 |
| --- | --- | --- | --- | --- |
| `3-6` | 0.0815 | 0.0729 | **0.0826** | 0.0977 |
| `6-12` | 0.0668 | 0.0603 | **0.0755** | 0.0833 |

`3-6` solves to 0.125 and `6-12` to 0.108. **0.127 is kept**: the peak band is where G0
measured the anchor and the runtime meets it to 1.3%, and the `6-12` disagreement is the same
tail-shape residual as above. Against the W12 close this row is the wave's headline number —
the GPU tier read 0.1867 there against the reference's 0.0815, 2.29×; it now reads 0.0826,
**1.013×**, so charter stop S3's "within 20% of the reference's integrated darkening" is met
with a factor of fifteen in hand.

## 3. The thick regime — the anchor and the lift, swept together

Both terms ride one falloff and G0 could not split them (claims §5.62 §4), so each thick span
was swept as a 5 × 4 grid of its black anchor against `liftAmplitude`. The grids say something
G0 could not: **in the harness's own readout the two are almost perfectly separable after
all.** `c` at `3-6` depends on `liftAmplitude` and is identical to five decimals across the
whole anchor axis; 1 − a depends on both, because the lift is composited in the encoded domain
and a constant addition there is not a constant addition in linear light — it adds more where
the plate is bright — so a fixed share of the lift lands in the slope rather than the
intercept. That is why raising the lift *lowers* the measured occlusion at a fixed anchor.

`f3`, `checkerboard__rrect-md` (span 96), 1x light, band `3-6`; native 1 − a 0.1925, c 0.00211:

```
At96 \ liftAmplitude    0.005     0.0073     0.010      0.013
0.319            1-a   0.1847    0.1768    0.1668    0.1538
0.349                  0.2073    0.1996    0.1897    0.1770
0.379 (shipped)        0.2274    0.2198    0.2101    0.1976
0.409                  0.2464    0.2389    0.2294    0.2170
0.439                  0.2704    0.2631    0.2537    0.2415
any anchor         c   0.00090   0.00121   0.00161   0.00211
ssimOutside            0.972     0.986     0.993     0.996
```

`f4`, `checkerboard__rrect-ml` (span 128), native 1 − a 0.2195, c 0.00330:

```
At128 \ liftAmplitude   0.005     0.0073     0.010      0.013
0.437            1-a   0.2517    0.2325    0.2106    0.1902
0.467                  0.2738    0.2549    0.2335    0.2134
0.497 (shipped)        0.2977    0.2792    0.2581    0.2385
0.527                  0.3196    0.3014    0.2808    0.2615
0.557                  0.3429    0.3251    0.3049    0.2860
any anchor         c   0.00161   0.00241   0.00331   0.00424
ssimOutside            0.977     0.992     0.996     0.992
```

`rrect-ml` is the cell that pins the amplitude, because its span is `liftSpanFull` itself and
its lift is therefore saturated whatever the reach is: **c 0.00331 against the reference's
0.00330 at `liftAmplitude` 0.0100**, and 0.00327 against 0.00334 at 2x. `rrect-md` then pins
the reach, since its c is the same amplitude times the span rise.

`f5`, the reach at the fitted amplitude, `c` at `3-6` on `rrect-md` (native 0.00211):

| `liftSpanFull` | 104 | 112 | **118** | 128 | 144 |
| --- | --- | --- | --- | --- | --- |
| c, `rrect-md` | 0.00292 | 0.00241 | **0.00211** | 0.00161 | 0.00120 |
| c, `rrect-ml` | 0.00331 | 0.00331 | **0.00331** | 0.00331 | 0.00292 |
| `ssimOutside`, `rrect-md` | 0.9901 | 0.9945 | **0.9959** | 0.9934 | 0.9842 |

118 is both the pair's answer and the perceptual maximum, at 1x and at 2x (`f8`: 0.9898 /
**0.9934** / 0.9911 at 112 / 118 / 124). The declared form — a smoothstep from the exact knee
at 64 to a reach the sweep settles — survives; only the reach moves, from 128 to 118, and it
moves *toward* G0's measurement rather than away (§5.62 §2 read the rise at 0.52 / 0.96 / 1.00
of the span-160 value at spans 96 / 128 / 160, and a reach of 118 puts span 96 at 0.65).

`f6` / `f7`, the refinement grids at `liftAmplitude` 0.0100, band `3-6`:

| point | 1 − a web / native | c web / native |
| --- | --- | --- |
| `rrect-md`, spanFull 118, At96 **0.370**, 1x | **0.1925** / 0.1925 | **0.00211** / 0.00211 |
| `rrect-md`, spanFull 118, At96 0.370, 2x | 0.1897 / 0.1904 | 0.00211 / 0.00210 |
| `rrect-ml`, At128 **0.448**, 1x | 0.2190 / 0.2195 | 0.00331 / 0.00330 |
| `rrect-ml`, At128 0.448, 2x | 0.2200 / 0.2194 | 0.00327 / 0.00334 |

(The 0.448 rows are read off the `f7` / `f9` line through 0.437 / 0.447 / 0.457, which brackets
it; 0.447 measured directly gives 0.2182 at 1x and 0.2192 at 2x.) At `6-12` the same point
reads 0.1600 against 0.1564 on `rrect-md` and 0.1836 against 0.1808 on `rrect-ml` — the same
2–3% heavy tail the thin regime shows, and c there is 0.00170 against 0.00173 and 0.00270
against 0.00270.

**Both scales take one set of constants.** The native pair is scale-free to 0.0007 in 1 − a
and 0.00004 in c across every thick cell, and the fitted constants differ by less than the
grid's own step between scales (At96 1x 0.370 / 2x 0.371; At128 1x 0.4487 / 2x 0.4473). No
per-scale anchor is warranted, which is not what W13's ramp found on the same bed.

## 4. `thickOcclusionAt160` — not identifiable, and the two ways of guessing it disagree

`thickOcclusionAt160` has no calibration cell. Span 160 appears in the bed only as
`checkerboard__rrect-lg` and `photo__rrect-lg`, span 130 only as
`checkerboard__glass-over-glass` and `photo__glass-over-glass`, and all four are holdout.
Nothing in the tuning path may select them, and nothing here did.

Two rules could carry G0's measured ladder (0.379 / 0.497 / 0.544, claims §5.62 §4) onto the
fitted one, and the one span where both can be tested refutes both:

- **the measured increment.** G0's 96 → 128 rise is +0.118; the fitted rise is +0.078.
- **the measured ratio.** G0's 128 / 96 is 1.311; the fitted ratio is 1.211.

So a rule fitted at 96 predicts At128 as 0.488 (increment) or 0.485 (ratio) where the runtime
measures 0.448. Neither survives, and applying either to span 160 would be asserting a span law
the bed has already contradicted once.

**What is carried: 0.479, and it is a derivation, not a fit.** It keeps the fitted ladder's own
level and its own 96 → 128 slope (+0.078 over 32 px) and takes only the *relative flattening*
from G0 — whose 128 → 160 rise is 0.398 of its 96 → 128 rise — giving 0.448 + 0.398 × 0.078 =
0.479. That is the least the bed can be asked to support. The alternatives (0.490 by carrying
G0's ratio onto the fitted At128, 0.495 by carrying its increment) sit 0.011–0.016 above it,
which is about 0.012 in band occlusion on a span-160 cell — resolvable, so this is a real gap
and not a rounding. §7 reports what the holdout rows say about it; nothing was refitted after
reading them.

## 5. The CSS tier — the adaptive alpha lands, the lift does not, and one cell does not follow

Decision Log 1 question 2 (a) as implemented: the CSS tier carries the geometry and the
adaptive alpha and no lift. `f10` / `f11`, 1x light, band `3-6`, at the chosen constants:

| cell | native | CSS tier | GPU tier |
| --- | --- | --- | --- |
| `checkerboard__capsule-button` 1 − a | 0.2192 | 0.2210 (+0.8%) | 0.2192 (+0.0%) |
| `checkerboard__rrect-sm` 1 − a | 0.2179 | 0.1836 (−15.7%) | 0.2125 (−2.5%) |
| `photo__capsule-button` occlusion | 0.2125 | 0.2069 (−2.6%) | 0.2099 (−1.2%) |
| `dark-solid__capsule-button` occlusion | 0.0442 | 0.0000 | 0.0000 |
| `light-solid__capsule-button` occlusion | 0.0815 | 0.0841 (+3.2%) | 0.0826 (+1.3%) |
| `light-solid__capsule-button` `6-12` | 0.0668 | 0.0740 (+10.8%) | 0.0755 (+13.0%) |

The two tiers agree to 1–3% on every cell except `checkerboard__rrect-sm`, the smallest span
in the bed, where the CSS tier's `box-shadow` reads 16% light against the GPU tier's 2.5%. The
amplitude the two tiers resolve is the same number from the same profile, so the difference is
geometric — the CSS tier's box against its `border-radius` on a 32 px span, which is the same
family as the over-fill G0 measured on that tier (claims §5.62 §6) and is a shape gap rather
than an amplitude one. It is below the harness's coherence test's reach because that test pins
the two tiers' *constants*, not their rendered exteriors; this is the first time the pair has
been read across tiers in the harness rather than in the unit suite. Recorded for the
declaration; nothing in this sweep would fix it, since moving the shared anchor to suit
`rrect-sm` would move the capsule off its exact match.

`c` on the CSS tier is 0.00000 on every checkerboard cell, which is the intended reading of
"the lift is GPU-only". On `photo` it reads −0.0084 to −0.0094, against the GPU tier's +0.0019
to +0.0025 and the reference's −0.0015: `photo`'s intercept is not the lift on any tier
(X7's caveat, claims §5.62 §8) and none of the three numbers should be read as one.

## 6. The dark scheme — the lift is real there, and the thick anchor has to move with it

The dark document's `liftAmplitude` was 0 when this sweep started and the review's fix wave set
it to 0.0038, which is 0.52 × the light document's **old** 0.0073 carried from X7's ratio. The
dark bed measures it directly:

`f12` / `f13`, `checkerboard__rrect-md`, 1x dark, band `3-6`; native 1 − a 0.1525, c 0.00108:

| `liftAmplitude` (at `liftSpanFull` 118) | 0.0045 | **0.0051** | 0.0057 |
| --- | --- | --- | --- |
| c | 0.00091 | **0.00109** | 0.00121 |

| `thickOcclusionAt96` (at `liftAmplitude` 0.0051) | 0.258 | **0.278** | 0.298 |
| --- | --- | --- | --- |
| 1 − a, 1x | 0.1373 | **0.1525** | 0.1644 |
| 1 − a, 2x (`f15`, at 0.268 / 0.278 / 0.288) | 0.1451 | **0.1518** | 0.1586 |

**`liftAmplitude` 0.0051 lands the dark bed's c exactly (0.00109 against 0.00108), and it is
0.51 × the light document's fitted 0.0100** — X7's measured ratio, arrived at independently on
the dark bed rather than carried onto it. The fix wave's reasoning is confirmed; only the
number moves, because the light amplitude it multiplies moved.

**The dark thick anchor has to move with the lift, and by more than the lift itself:
`thickOcclusionAt96` 0.230 → 0.278, +21%.** At 0.230 with a lift present the dark cell reads
1 − a = 0.1231 against the reference's 0.1525, a 19% shortfall; the anchor closes it exactly at
1x and to −0.4% at 2x. This is the first number in the wave to say that the dark document's
thick anchors were carrying the *absence* of the lift, and it is the answer to the question the
coordinator's second instruction asked.

Two dark constants that follow it are **not identifiable**: `thickOcclusionAt128` and
`thickOcclusionAt160`, because the dark bed's only thick cells above span 96 are
`checkerboard__glass-over-glass` (130) and `photo__rrect-lg` (160) and both are holdout. Left
at 0.249 and 0.268 they would sit *below* the fitted At96 of 0.278 and the ladder would run
backwards. They are carried at **0.301 and 0.324** — G0's dark ladder scaled by the one ratio
the bed identifies, 0.278 / 0.230 = 1.209 — which preserves G0's measured span shape and
monotonicity and asserts nothing else. (The light document's At160 uses a different derivation
for a good reason: there, two anchors are fitted, so the fitted ladder has its own slope to
extrapolate from; here there is one, so only a level correction can be carried.)

**The dark thin plateau reads 6–10% high at the anchor G0 measured, on both of the bed's
dark thin cells, and is kept anyway.** `f14` / `f16`, band `3-6`:

| cell | quantity | native | 0.055 | 0.060 | **0.063** |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button` | 1 − a | 0.0421 | 0.0377 | 0.0435 | **0.0457** |
| `photo__capsule-button` | occlusion off the level | 0.0399 | 0.0362 | 0.0422 | **0.0441** |

Both solve to about 0.058–0.059, 6–8% below G0's measured 0.063 (`photo`'s *slope* solves
elsewhere and is disregarded: its intercept reads +0.0028 against a native −0.0002, which is
X7's low-frequency-projection caveat again, so its occlusion off the level is the reading that
means anything). **0.063 is kept**: it is MEASURED flat across three dark backdrops in the peak,
the light scheme's own mid anchor read back *exactly* on the same band, and 6–8% on two cells is
not enough to overturn a measurement with a band residual whose sign and size match the falloff
tail this sweep sees everywhere else (§2, §3). The overshoot is recorded, not fitted away.

The CSS tier quantises it away entirely: at 0.055 and at 0.060 the dark `box-shadow` renders
the identical exterior (1 − a 0.0429 on the checkerboard capsule at both), because at this
amplitude the tier's alpha lands in the same 8-bit code. At 0.063 it reads 0.0493 against
native 0.0421, +17%. A dark-scheme thin anchor is not tunable on that tier at better than
about 0.005 of occlusion.

The dark document must also now *name* `liftSpanMin`, `liftSpanFull` and `liftBlurSigmaCss`.
It is a difference document over `DEFAULT_MATERIAL_PROFILE`, so silence there would leave the
dark scheme on the runtime default reach of 128 while the light document moved to 118 —
the same class of silent-inheritance problem the fix wave's own note on
`reducedTransparencyOcclusion` records.

## 7. The chosen constants

| constant | shipped on the branch | chosen | how |
| --- | --- | --- | --- |
| `thinOcclusionDark` | 0 | 0 | MEASURED; the null holds exactly (§2) |
| `thinOcclusionMid` | 0.33 | **0.33** | MEASURED; runtime reads it to 0.0000 on the checkerboard capsule, ±4% across cells (§2) |
| `thinOcclusionBright` | 0.127 | **0.127** | MEASURED; runtime reads it to +1.3% at `3-6` (§2) |
| `thickOcclusionAt96` | 0.379 | **0.370** | FITTED on `checkerboard__rrect-md`, exact at 1x, −0.4% at 2x (§3) |
| `thickOcclusionAt128` | 0.497 | **0.448** | FITTED on `checkerboard__rrect-ml`, −0.2% at 1x, +0.3% at 2x (§3) |
| `thickOcclusionAt160` | 0.544 | **0.479** | NOT IDENTIFIABLE; carried, derivation in §4 |
| `liftAmplitude` | 0.0073 | **0.0100** | FITTED on `rrect-ml`'s c, +0.3% at 1x, −2.1% at 2x (§3) |
| `liftSpanMin` | 64 | 64 | MEASURED, exact (claims §5.62 §2) |
| `liftSpanFull` | 128 | **118** | FITTED on `rrect-md`'s c; also the perceptual maximum at both scales (§3) |
| `liftBlurSigmaCss` | 40 | 40 | MEASURED; not swept — the bed identifies it only on a holdout cell |
| `reducedTransparencyOcclusion` | 0.197 | 0.197 | not swept; the review's fix wave re-formed it as an absolute measured amplitude (README) |
| `offsetPx` / `sigmaPx` / `spreadPx` | 7.95 / 15.55 / 3.1 | unchanged | W8's, re-read free and unmoved by G0 (claims §5.62 §4) |
| `sizeGain` | 0 | 0 | the identity; this wave does not touch the seam |
| dark `thinOcclusionMid` / `Bright` | 0.063 / 0.063 | 0.063 / 0.063 | kept, §6; `Bright` has no dark cell at all |
| dark `thickOcclusionAt96` | 0.230 | **0.278** | FITTED, exact at 1x (§6) |
| dark `thickOcclusionAt128` / `At160` | 0.249 / 0.268 | **0.301 / 0.324** | NOT IDENTIFIABLE; carried on the fitted ratio (§6) |
| dark `liftAmplitude` | 0.0038 | **0.0051** | FITTED on the dark bed's c, +0.9% (§6) |
| dark `liftSpanMin` / `SpanFull` / `BlurSigmaCss` | (inherited) | **64 / 118 / 40** | must be named, §6 |

`chosen-light.json` and `chosen-dark.json` beside this file are those documents.

## 8. The two rankings

The pair and the perceptual rows rank the lift's two constants **the same way** and the black
anchors **not at all**, and on one cell they point in opposite directions.

- On `liftSpanFull` they agree exactly: `ssimOutside` on `rrect-md` peaks at 118 at 1x (0.9959
  against 0.9945 at 112 and 0.9949 at 124) and at 2x (0.9934 against 0.9898 and 0.9911), which
  is the value the pair's c solves to.
- On `liftAmplitude` they agree: `ssimOutside` on `rrect-ml` peaks at 0.010 (0.9962, against
  0.9922 at 0.0073 and 0.9916 at 0.013), which is where c meets the reference.
- On the black anchors the perceptual rows are **blind**. Across a 0.02 span of
  `thickOcclusionAt96` and of `thickOcclusionAt128`, `ssimMean`, `ssimBand` and `ssimInterior`
  are identical to four decimals and `ssimOutside` moves by 0.0001. Only the pair ranks them,
  which is the case for X7 having landed in the harness at all.
- They **disagree on `light-solid__capsule-button`.** The pair wants 0.127 (occlusion 0.0826
  against 0.0815); `ssimOutside` wants the shadow *weaker* — 0.9681 at 0.10, 0.9663 at 0.127,
  0.9653 at 0.15 on the GPU tier, and the same ordering on the CSS tier. The chosen value
  follows the pair, because the pair measures the facet this wave declares and the SSIM
  ordering on that cell is a second difference partly cancelling the shadow (the tier's
  over-fill, claims §5.62 §6, is on the same cell and the same sides). Recorded as a
  disagreement rather than resolved.

## 9. The confirmation run

Nine runs at the chosen constants over `calibration,validation,holdout` into
`matrix-confirm.json` (commands in `README.md`), 21:24–21:29 on 2026-09-03, on the branch at
`99ea455` rebuilt. **Holdout was read once, here.** Every Δ below is against the W12 close bed
(the X7 baseline).

### 9.1 The perceptual rows, GPU tier, the checkerboard spans

| cell | set | 1x `ssimMean` | 1x `ssimOutside` | 2x `ssimMean` | 2x `ssimOutside` |
| --- | --- | --- | --- | --- | --- |
| `rrect-sm` | calibration | 0.9988 (+0.0000) | 0.9991 (+0.0002) | 0.9978 (+0.0001) | 0.9975 (+0.0004) |
| `capsule-button` | calibration | 0.9852 (−0.0000) | 0.9663 (−0.0000) | 0.9836 (−0.0000) | 0.9611 (−0.0003) |
| `rrect-md` | calibration | 0.9859 (**+0.0163**) | 0.9959 (**+0.0639**) | 0.9840 (**+0.0324**) | 0.9934 (**+0.1350**) |
| `rrect-ml` | calibration | 0.9788 (**+0.0306**) | 0.9962 (**+0.0878**) | 0.9746 (**+0.0588**) | 0.9932 (**+0.1800**) |
| `glass-over-glass` | holdout | 0.9807 (**+0.0287**) | 0.9950 (**+0.0817**) | 0.9762 (**+0.0550**) | 0.9900 (**+0.1670**) |
| `rrect-lg` | holdout | 0.9687 (**+0.0259**) | 0.9935 (**+0.1030**) | 0.9680 (**+0.0567**) | 0.9885 (**+0.2053**) |
| `toolbar-group` | calibration | 0.9642 (−0.0001) | 0.9278 (−0.0003) | 0.9662 (−0.0001) | 0.9232 (−0.0005) |

`ssimOutside` rises on every checkerboard cell at both scales, and on `photo__rrect-md`,
`hc-text__rrect-md` (+0.0050 at 1x, **+0.0808** at 2x) and `light-solid__capsule-button`
(+0.0150 / +0.0091). The only cells whose `ssimOutside` falls are the `photo` thick cells
(−0.0003 to −0.0016) and `dark-solid__capsule-button` (−0.0023), both below 0.002 except the
last; see §9.4.

### 9.2 The stops, with numbers

- **S1 — no inside row moves by more than 0.001. FAILS on one cell, in one direction, and the
  mechanism is named.** `ssimBand` and `ssimInterior` move by ≤ 0.0008 on every cell of every
  profile and both tiers **except `dark-solid__capsule-button__rest`**: `ssimBand` −0.0188 at
  1x light and −0.0474 at 2x light on the GPU tier, −0.0086 / −0.0148 on the CSS tier,
  −0.0081 / −0.0132 in the dark scheme, and `dark-solid__rrect-md` −0.0057 / −0.0041 in the
  dark scheme. Consistent across four profiles and both tiers, so it is real and not frame
  noise. The cause is the declared change itself: the thin law returns exactly 0 over a
  backdrop below `OUTER_SHADOW_THIN_L.inert` where W8 applied 0.285 everywhere, and the band
  window (inside the native silhouette, within 24 CSS px of the contour) contains the
  contour's own partly-covered pixels, which the exterior term reaches. **The reference is not
  perfectly inert there**: X7 reads it removing 0.0442 of the level in `3-6` below over
  `dark-solid` — 0.00017 of linear luminance, one code of 255, which is exactly the size
  §5.62 §5 said it was, and exactly the size SSIM's luminance term magnifies on a near-black
  level. It is §5.60 §3's own finding with the sign reversed: a hair of darkness on black is
  most of that row. The absolute rows are 0.3855 (1x) and 0.2764 (2x) against 0.4043 and
  0.3238, on the cell whose band SSIM was already the lowest in the bed.
- **S2 — `ssimOutside` rises on every checkerboard and `photo` cell at both scales. MET on the
  checkerboard (§9.1), MISSED on three `photo` cells by less than 0.002**
  (`photo__glass-over-glass` −0.0006, `photo__rrect-lg` −0.0016 at 1x and −0.0014 at 2x,
  `photo__rrect-lg__rest-tint-orange` −0.0016 / −0.0013). Those cells sat at 0.9952–0.9978
  before and sit at 0.9931–0.9972 now.
- **S3 — the light-solid capsule within 20% of the reference's integrated darkening. MET by a
  factor of fifteen.** Occlusion off `3-6` below: reference 0.0815, GPU tier **0.0826**
  (1.013×), CSS tier **0.0841** (1.032×), against the W12 close's 0.1867 and 0.1838 (2.29× /
  2.25×). At 2x, reference 0.0824, GPU 0.0830, CSS 0.0848. On `mid-dark-solid` (holdout, the
  other solid the stop names) the GPU tier reads 0.1856 against the reference's 0.2042, 9%
  light — the mid plateau's dark end wants more than 0.33 and the flat plateau does not give
  it (§9.3).
- **S4 — the three 2x texture rows meet 0.93. MET, with 0.04 of margin each.**
  `rrect-ml` **0.9746** (floor 0.9147, was 0.9158), `glass-over-glass` **0.9762** (floor
  0.9201, was 0.9211), `rrect-lg` **0.9680** (floor 0.9102, was 0.9113). And no 1x row falls
  more than 0.002 below its W12-close `ssimMean`: the largest 1x fall anywhere in the
  confirmation is −0.0019 (`photo__rrect-lg`, dark scheme).
- **S5 — `dark-solid` and `impulse` unchanged.** `impulse` is unchanged to ±0.0005 on every
  row, tier and scale. `dark-solid` is **not**: see S1.
- **S6 — the CSS tier moves only as predicted. It does not.** See §9.5.
- **S7** is the user's eye and is not this document's to call.

### 9.3 The holdout rows, read once and fitted to nothing

| cell | scheme | span | native 1 − a | web 1 − a | native c | web c |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__glass-over-glass` | light 1x | 130 | 0.2214 | 0.2208 | 0.00349 | 0.00331 |
| `checkerboard__rrect-lg` | light 1x | 160 | 0.2117 | **0.2436** | 0.00362 | 0.00331 |
| `checkerboard__glass-over-glass` | light 2x | 130 | 0.2214 | 0.2219 | 0.00350 | 0.00327 |
| `checkerboard__rrect-lg` | light 2x | 160 | 0.2123 | **0.2436** | 0.00364 | 0.00328 |
| `hc-text__capsule-button` | light 1x | 44 | 0.2196 | 0.2227 | 0.00000 | 0.00000 |
| `hc-text__rrect-md` | light 1x | 96 | 0.1691 | 0.1779 | 0.00303 | 0.00213 |
| `mid-dark-solid__capsule-button` | light 1x | 44 | 0.2042 (level) | 0.1856 | — | — |
| `checkerboard__glass-over-glass` | dark 1x | 130 | 0.2195 | **0.1537** | 0.00187 | 0.00170 |

Three things the holdout says, reported and acted on nowhere:

1. **The reference's band occlusion is not monotone in span, and §5.62 §4's peak ladder is.**
   Native 1 − a at `3-6` below on the checkerboard runs 0.1925 (96) → 0.2195 (128) → 0.2214
   (130) → **0.2117 (160)**, at both scales. G0's peak ladder runs 0.379 → 0.497 → 0.544,
   rising throughout. Something between the peak occlusion and the `3-6` band reading turns
   over between span 130 and span 160, and this sweep cannot say what — every cell that could
   is holdout. **This is the one reading in the sweep that contradicts claims §5.62.**
2. **`thickOcclusionAt160` at the carried 0.479 is 15% heavy** (0.2436 against 0.2117); the
   local slope says the band would be met at about **0.437**. Nothing was refitted to that
   number and the chosen document keeps 0.479. §4's warning that no rule survives is what the
   holdout confirms — the value the holdout implies is *below* the fitted At128 of 0.448, which
   no extrapolation from the calibration cells would ever have produced.
3. **The dark scheme's thick ladder above span 96 is badly wrong, and was never identifiable.**
   The dark bed's only thick cells above 96 are holdout, so §6's carried 0.301 / 0.324 are a
   level correction on G0's shape; at span 130 the runtime reads 0.1537 against the reference's
   0.2195, 30% light. The local slope says span 130 wants about 0.40, so the dark ladder rises
   with span far more steeply than G0's dark peak ladder (0.230 / 0.249 / 0.268, nearly flat)
   suggests — and the dark reference's band occlusion at span 130 (0.2195) is within 1% of the
   *light* reference's at the same span (0.2214), where at span 96 the two differ by 21%.
   Nothing on the calibration side of the dark bed can see this.

The lift's own holdout residual is small and one-signed: web c is 5% low at span 130 and 9%
low at 160, which is the smoothstep saturating fully by 118 where §5.62 §2 measured the rise
still climbing from 0.96 to 1.00 between 128 and 160.

### 9.4 The accessibility beds and the dark scheme

The preference's re-formed absolute amplitude (the fix wave's 0.197, not swept here) reads back
flat across the thin and the thick regime together, which is what §5.62 §5 measured. Band
`3-6`, 1 − a, reduced transparency (increased contrast is identical to three decimals on every
row, which is Decision Log 8's coupling again):

| cell | span | native | web |
| --- | --- | --- | --- |
| `checkerboard__capsule-button` | 44 | 0.1245 | 0.1274 (+2.3%) |
| `checkerboard__rrect-md` | 96 | 0.1326 | 0.1250 (−5.7%) |
| `hc-text__capsule-button` (holdout) | 44 | 0.1247 | 0.1289 (+3.4%) |
| `photo__capsule-button` | 44 | 0.1202 (occl) | 0.1200 (−0.2%) |
| `photo__rrect-md` | 96 | 0.1276 (occl) | 0.1200 (−6.0%) |
| `photo__rrect-lg` (holdout) | 160 | 0.1094 (occl) | 0.1204 (+10.1%) |

`c` is 0.00000 on every checkerboard row on both sides: the lift is stood down under the
preference and the reference has none there either.

The dark scheme's GPU rows rise where the lift landed — `checkerboard__rrect-md` `ssimMean`
0.9564 (+0.0071) and `ssimOutside` 0.9922 (+0.0292) at 1x, 0.9694 (+0.0151) and 0.9904
(+0.0659) at 2x; `checkerboard__glass-over-glass` (holdout) +0.0169 / +0.0508 and +0.0337 /
+0.1072 — and fall slightly on the dark `photo` cells (`photo__rrect-md` −0.0013 / −0.0040,
`photo__rrect-lg` −0.0019 / −0.0050), which is the `photo` intercept caveat showing up as a
real over-darkening: native occlusion 0.1159 against web 0.1426 on `photo__rrect-md` dark.

### 9.5 The CSS tier — S6 misses, and the reason is structural

The CSS tier's **thin** cells land where the profile says: `light-solid__capsule-button`
occlusion 0.0841 against 0.0815 and `ssimOutside` +0.0172 at 1x (+0.0112 at 2x),
`checkerboard__capsule-button` 0.2210 against 0.2192. Its **thick** cells do not:

| cell (1x light, CSS tier) | span | native 1 − a | W12 close | now |
| --- | --- | --- | --- | --- |
| `checkerboard__rrect-md` | 96 | 0.1925 | 0.1840 | **0.2439** |
| `checkerboard__rrect-ml` | 128 | 0.2195 | 0.1881 | **0.3058** |
| `checkerboard__glass-over-glass` (holdout) | 130 | 0.2214 | 0.1877 | **0.3100** |
| `checkerboard__rrect-lg` (holdout) | 160 | 0.2117 | 0.1925 | **0.3364** |

**The thick anchors cannot serve both tiers, because they were fitted on a tier that has a
lift.** §3 showed that a fixed share of the GPU tier's lift lands in the slope and *lowers* the
measured occlusion at a fixed anchor; the CSS tier carries the anchor and no lift (Decision Log
1 question 2 (a)), so the same number over-darkens it by exactly that share — 27% at span 96
rising to 59% at span 160. Its exterior was closer to the reference before this wave. The
perceptual rows barely notice (`ssimOutside` −0.0002 to −0.0034 on those four cells, because
the CSS tier's exterior loss is dominated by other differences), which is why only the pair
sees it; it is the same lesson as §8's blindness, one tier over.

Two further CSS-tier readings: `checkerboard__rrect-sm` reads 0.1836 against native 0.2179
(−16%) where the GPU tier reads 0.2125 (§5), and the dark scheme's thin anchor quantises (§6).

## 10. What this asks of the declaration

Stated as the instrument found them, not as recommendations.

1. **Four PROVISIONAL constants have fits; a fifth cannot be identified and the holdout says
   the natural guesses were wrong.** `thickOcclusionAt96` 0.370, `thickOcclusionAt128` 0.448,
   `liftAmplitude` 0.0100 and `liftSpanFull` 118 can be written as FITTED with the cell, band,
   scale and residual in §3 and §7. `thickOcclusionAt160` has no calibration cell at all, is
   carried at 0.479 by the derivation in §4, and the holdout read (§9.3) puts it near 0.437 —
   *below* the fitted At128, which no extrapolation from the calibration side would have
   produced. It stays carried; a span-160 or span-130 calibration cell is what would close it,
   and that is a Deferred entry.
2. **One reading contradicts claims §5.62.** §5.62 §4's peak ladder rises monotonically with
   span (0.379 / 0.497 / 0.544). The reference's occlusion in the `3-6` band below does not: it
   runs 0.1925 / 0.2195 / 0.2214 / 0.2117 at spans 96 / 128 / 130 / 160, turning over between
   130 and 160, at both scales, on the checkerboard. The two are different quantities — a peak
   and a band — and G0 never claimed the band tracked the peak, but a renderer fitted on one
   and refereed on the other has to know which. Reported; both cells that show it are holdout,
   so this sweep could not have found it before the confirmation and cannot act on it now.
3. **The lift is 37% larger and reaches 8% sooner than declared, and both were declared
   PROVISIONAL for exactly this.** Nothing in G0's own measurement is contradicted: §5.62 §2's
   rise (0.52 / 0.96 / 1.00 at spans 96 / 128 / 160) is better served by a reach of 118 (0.65
   at span 96) than by 128 (0.50), and the amplitude's provisional derivation divided G0's
   linear lift by an assumed backdrop level the sweep never had to assume. The residual is that
   a smoothstep saturating at 118 is 5–9% low at spans 130 and 160, where G0 measured the rise
   still climbing.
4. **The thin regime needs nothing, and its one gap is the plateau's dark end.** Both MEASURED
   anchors read back (0.33 exactly on the checkerboard capsule, 0.127 to +1.3% on the
   light-solid capsule) and the wave's largest by-eye gap — the light-solid capsule at 2.29× —
   is now 1.013×, stop S3 met by a factor of fifteen. The holdout `mid-dark-solid` capsule, the
   only cell inside the tone curve's transition band, reads 9% light: G0 measured 0.347 there
   against 0.327–0.339 elsewhere and the flat plateau at 0.33 cannot carry both. W14's Deferred
   already names the missing backdrop between L 0.74 and 0.891; this is the same shape of gap at
   the other end.
5. **The dark document's thick anchors were carrying the absence of the lift, and only one of
   the three can be measured.** `liftAmplitude` 0.0051 lands the dark bed's c exactly and is
   0.51 × the light's fitted amplitude — X7's ratio, arrived at on the dark bed rather than
   carried onto it. `thickOcclusionAt96` must go 0.230 → 0.278 with it or the dark bed reads 19%
   light. The other two are unidentifiable and the holdout says the carried values are 30% light
   at span 130. The dark document must also *name* `liftSpanMin`, `liftSpanFull` and
   `liftBlurSigmaCss` rather than inherit them, since the light reach moved.
6. **S6 misses: the thick anchors cannot serve both tiers while the lift is GPU-only.** The
   CSS tier over-darkens its thick spans by 27% at 96 rising to 59% at 160 (§9.5), and its
   exterior was closer to the reference before this wave. This is a consequence of Decision
   Log 1 question 2 (a) that the decision did not foresee: (a) assumed the lift's absence costs
   the CSS tier only the lift, and the sweep shows it also costs the shared black anchor, whose
   fitted value absorbs part of the lift. Either the CSS tier needs its own thick anchors (a
   `cssTierMapping` question, and the mapping section already exists for exactly this kind of
   corrective) or the lift has to land there too. **The declaration cannot honestly say "both
   tiers carry the geometry and the adaptive alpha from one profile" for the thick regime as
   things stand.** The thin regime is fine on both tiers and is most of what (a) was argued on.
7. **S1 misses on `dark-solid`, and the mechanism is the mirror of the one this wave was
   chartered for.** Making the facet exactly inert below the luminance floor costs `ssimBand`
   0.019–0.047 on `dark-solid__capsule-button` across four profiles and both tiers, because the
   reference is not perfectly inert there — X7 reads it removing one code of 255 — and SSIM's
   luminance term magnifies one code on a near-black level, exactly as it magnified the lift on
   the checkerboard's black squares (§5.60 §3). Either the declaration says the shadow reaches
   under the surface at the contour and predicts this, or `thinOcclusionDark` is not 0 but the
   small number X7 measures. It is a decision, not a fit; the bed can supply the number
   (0.0442 of the level in `3-6` below, over a backdrop at 0.0039 linear).
8. **Two residuals that no amplitude constant can absorb.** The falloff's tail reads 2–13%
   heavy at `6-12` on every cell, tier, scale and scheme while the `3-6` peak band is right —
   W8's lengths were re-read free by G0 and not refit, so this is a shape residual the
   declaration should name rather than let the `3-6` agreement hide. And
   `checkerboard__rrect-sm` reads 16% light on the CSS tier against 2.5% on the GPU tier at the
   same profile constant, which `tier-coherence` cannot see because it pins the constants and
   not the rendered exteriors — tech-debt tracker, with the CSS tier's over-fill (§5.62 §6) it
   most likely shares a cause with.

## 11. The GPU

Held as one block for the sweep (20:47:40–20:52:50, fifteen rounds) and released; the W13
ramp's re-sweep took it at 20:52:55 and held it until 21:21. The confirmation block ran
21:24:03–21:28:44 and the GPU was **released at 21:28:44**; nothing of this wave's has held it
since. A stale vite server on the harness's fixed port 5189 outlived one of the two workers'
runs twice during that window and cost two rounds, which is worth a `pgrep`-plus-`lsof` check
rather than `pgrep` alone before a block.
