# W22 G0 — the resting sweep gated, the rim re-read per side on both beds, the two eye findings measured

Findings, not spec text. The parent writes the claims section and Decision Log 2 from this file.
Every number here is a reading taken in this gate; nothing canonical was written. The tables live
beside this file as `.txt`, the scripts that produced them beside those, and the scratch root is
`/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/`.

Worktree branch `worktree-agent-ac5e591b52341c4ce`; the gate's code at **550f16d**, this results
directory at the commit that carries it.

---

## 0. What was run, and what was deliberately not

| step | what | where |
| --- | --- | --- |
| the gate | `shimmer` added to both channel vocabularies; the highlight pass's gain becomes `sweepGain × shimmer(lead)` | commit 550f16d |
| the suites | `pnpm -r build`, `pnpm -r lint`, `pnpm -r test`, `test:golden` | all green; 29/29 goldens byte-identical |
| the bed | four standard profiles × GPU tier × `calibration,validation`, `--alpha` | `g0-capture.sh` → `after/` |
| the fit's points | light `specularGain` 0 at `rimAlpha` 0.18 and 0.04, both scales; dark `backdropToneMax` 0, both scales | `g0-fit-capture.sh` → `fit/` |
| W21's own rows | the W21 probe grid at `rimAlpha` 0.02 / 0.18 / 0.082 | `g0-probe-capture.sh` → `probe/` |
| the reads | per side on both beds, before and after; the isolation; the stack per pane; the glow | `read-canonical.sh`, `check-isolation.py`, `run-stack.sh`, `run-glow.sh` |
| the gate over the matrix | `adopted-thresholds` on a merged matrix | `moved-rows.py` |

**Not run, on purpose:** the holdout. W22 X5 spends the wave's one holdout read at G1's dry run on
the frozen configuration, so no capture below passes `--set holdout`. This has one consequence the
parent must carry: **both `glass-over-glass` cells are in the holdout split**, so §5's nested-pane
reading has a native column and a *canonical-capture* column and **no "after" column**. That is
stated again where it bites. The finding it measures is a body-level inversion the sweep cannot
touch — the gate moved no body on any cell by more than 0.000029 (§1) — so the
missing column changes no conclusion here, but G1 should re-read the two panes when it opens the
holdout.

---

## 1. The gate, and the attribution

`shimmer` ∈ [0, 1], idle 0, in `SurfaceChannelValues` (published as `--vitrea-shimmer`, read by
`readHostChannels`) and in the renderer's `SurfaceChannels`; the highlight pass's packed gain is
`sweepGain × shimmer` of the same lead surface that supplies the phase; Reduced Motion's CPU-side
zeroing unchanged. `test/resting-sweep.test.ts` reads the highlight uniform's own bytes off the
fake device and pins gain **0** at `IDLE_CHANNELS`, `sweepGain` at `shimmer` 1, and linearity
between; the press glow is asserted beside it as untouched.

**Golden verdict: 29 of 29 pass, byte-identical**, including `highlight-press-glow` (which now
declares `shimmer: 1`, as it always meant by driving a phase) and every hash table in
`e2e/golden/isolation.spec.ts`. **X4 held. No golden moved. Nothing was re-recorded.**

Suites: `pnpm -r build` ✓, `pnpm -r lint` ✓, `pnpm -r test` ✓ (1861 tests over 129 files; renderer
399, platform-web 426).

**The isolation, on the captures** (`isolation.txt`, `check-isolation.py`). Over 68 readable cells
across the four profiles — 272 sides — the gate moved the **left side on 54**, the **top on 2**, and
**bottom and right on none at all**. The two top-side movements are `photo__capsule-button__rest-tint-orange`
on the dark bed at −0.0000429 (1x) and −0.0000449 (2x), which is the peak statistic choosing a
different row of the top band now that the left corner under it is no longer lit: a consequence of
the band's removal, not a second change. Bodies moved on 46 cells by at most **−0.000029** (the
band's blur shoulder reaching six CSS px inside the box). The left side's own drop is −0.118 to
−0.235. This reproduces on the light bed the isolation W21 ran on the dark one (claims §5.90 §4) and
is the measurement that attributes the whole change to the resting band.

---

## 2. The light rim's verdict

**One sentence:** the light reference's rim has left exactly equal to right — |L−R| ≤ 0.0002 on
every solid cell at both scales, against vitrea's +0.1327 (1x) and +0.2312 (2x) before the gate and
≤ 0.0022 after — and it is *not* flat top against bottom, carrying +0.0002 over `dark-solid` and
+0.0086 to +0.0162 over `light-solid`, against vitrea's +0.1237 (1x) / +0.1817 (2x) over
`dark-solid`; so the horizontal light the shipped `lightDirection` implies is absent from the
reference and the vertical specular the shipped `specularGain` draws is five hundred times larger
than anything the reference shows over a dark backdrop.

### 2.1 The reference's own per-side structure (`per-side.txt`, tail)

`T−B` and `L−R` are the two contrasts the instrument can state without contamination (§2.2).

| profile | cell | T−B | L−R | flat (4 sides) |
| --- | --- | ---: | ---: | ---: |
| 1x light | `dark-solid__capsule-button` | +0.0002 | +0.0000 | 0.0088 |
| 1x light | `dark-solid__rrect-md` | +0.0002 | −0.0001 | 0.1077 |
| 1x light | `light-solid__capsule-button` | +0.0086 | −0.0002 | 0.0555 |
| 1x light | `light-solid__rrect-md` | +0.0138 | −0.0000 | 0.0311 |
| 1x light | `light-solid__rrect-ml` | +0.0139 | −0.0001 | 0.0356 |
| 2x light | `dark-solid__capsule-button` | +0.0002 | −0.0000 | 0.0114 |
| 2x light | `dark-solid__rrect-md` | +0.0002 | −0.0000 | 0.1101 |
| 2x light | `light-solid__capsule-button` | +0.0113 | −0.0001 | 0.0500 |
| 2x light | `light-solid__rrect-md` | +0.0162 | −0.0001 | 0.0315 |
| 2x light | `light-solid__rrect-ml` | +0.0162 | +0.0000 | 0.0360 |
| 1x dark | `dark-solid__capsule-button` | +0.0002 | +0.0000 | 0.0088 |
| 1x dark | `dark-solid__rrect-md` | +0.0001 | +0.0000 | 0.0044 |
| 2x dark | `dark-solid__capsule-button` | +0.0002 | −0.0000 | 0.0114 |
| 2x dark | `dark-solid__rrect-md` | +0.0002 | +0.0000 | 0.0070 |

So: **flat left-to-right everywhere, to the instrument's fourth decimal.** Top-to-bottom the
reference is flat over a dark backdrop and carries a small, consistent, scale-stable top-weighting
of +0.009 to +0.016 over a bright one.

### 2.2 The instrument's one geometric caveat, measured (declared in `fit-rim.py`'s header)

The declared box's rim band is a *rectangle's* band and a rounded shape does not fill it, so a
side's peak is a mixture of rim and background. The mixture's weight differs between the horizontal
and the vertical pair, because the box is wider than it is tall: the covered fraction is 0.758 /
0.341 on the capsule (top-bottom / left-right), 0.839 / 0.732 on `rrect-md`, 0.833 / 0.708 on
`rrect-ml`. **The `H−V` gap is therefore NOT a light direction.** Two readings prove it is the
mixture: its *sign follows sign(backdrop − rim)* — on the canonical light bed, where the backdrop
(0.891) is below the rim, the vertical sides read *lower* (H−V −0.024 to −0.11); on W21's probe,
where `light-solid` sits under the dark profile and the backdrop is far above the body, the same
cells read the vertical sides *higher* (native `light-solid__rrect-lg` left/right 0.3547 against
top 0.2557, bottom 0.2344). And the capsule model predicts it: at 0.36 coverage, `0.36 × 0.963 +
0.64 × 0.891 = 0.917` against the measured 0.907, and in dark `0.36 × 0.025 + 0.64 × 0.0117 =
0.0165` against the measured 0.0161.

`L−R` and `T−B` cancel the mixture exactly (identical geometry), which is why the verdict above is
stated on them and not on `H−V`. **This caveat did not exist in W21's records and belongs in the
ledger beside the instrument.**

### 2.3 Clause 2, cell by cell, after the gate

Left within 0.03 of right: **met on every cell of both beds at both scales** (worst 0.0022).

Each side within 0.03 of the reference's: met on every cell **except `dark-solid__rrect-md` under
the LIGHT profile**, which misses on all four sides at 2x and on three at 1x:

| scale | side | native | after | Δ |
| --- | --- | ---: | ---: | ---: |
| 1x | top | 0.5272 | 0.5577 | +0.0305 |
| 1x | bottom | 0.5269 | 0.4340 | −0.0930 |
| 1x | left | 0.4195 | 0.3884 | −0.0311 |
| 1x | right | 0.4196 | 0.3877 | −0.0319 |
| 2x | top | 0.5408 | 0.6348 | +0.0940 |
| 2x | bottom | 0.5406 | 0.4531 | −0.0875 |
| 2x | left | 0.4307 | 0.3945 | −0.0362 |
| 2x | right | 0.4307 | 0.3936 | −0.0371 |

This is the light material's rim over a *dark* backdrop, and the shipped `specularGain` 0.55 is what
splits top from bottom by 0.124 (1x) / 0.182 (2x) where the reference splits them by 0.0002. It is
a new open cell, visible only now that the band is gone.

The dark bed's two W21 clause-4 cells **close**: `dark-solid__rrect-md` left 0.1690 → 0.0363 with
right at 0.0363 (L−R 0.1327 → 0.0000 at 1x, 0.2312 → 0.0000 at 2x), each side within 0.0133 of the
reference; `dark-solid__capsule-button` collapsed and flat on all four.

---

## 3. The G1 recommendation — which constants to fit, and on which rows

### 3.1 `optics.regular.specularGain` (light profile): **FIT, to 0.** Its rows separate it.

| row | reference | shipped (0.55) | at 0 |
| --- | ---: | ---: | ---: |
| 1x `dark-solid__rrect-md` T−B | +0.0002 | **+0.1237** | +0.0002 |
| 2x `dark-solid__rrect-md` T−B | +0.0002 | **+0.1817** | +0.0001 |
| 1x `light-solid__rrect-md` T−B | +0.0138 | +0.0178 | +0.0123 |
| 2x `light-solid__rrect-md` T−B | +0.0162 | +0.0248 | +0.0148 |
| 1x `light-solid__capsule-button` T−B | +0.0086 | +0.0116 | +0.0066 |
| 2x `light-solid__capsule-button` T−B | +0.0113 | +0.0100 | +0.0060 |
| 1x `light-solid__rrect-ml` T−B | +0.0139 | +0.0203 | +0.0157 |
| 2x `light-solid__rrect-ml` T−B | +0.0162 | +0.0270 | +0.0194 |
| context: 1x `impulse__rrect-md` T−B | +0.0001 | +0.1091 | (unrendered) |

The separating row is `dark-solid__rrect-md` at both scales: the term the constant adds is 0.12–0.18
of luminance on the top side of a cell whose reference is flat to 0.0002. The `light-solid` rows do
not separate it (both settings sit within 0.01 of the reference, near saturation), so the fit rests
on the dark-backdrop rows and the two agree across scales. This is the same verdict W21 reached
independently on the dark patch (`specularGain` 0.55 → 0, declined-then-zeroed, claims §5.90 §1).

**The honest cost, declared:** the pooled objective (mean |Δ excess| over 16 live rows) is 0.0178 at
the shipped constants and 0.0236 at `specularGain` 0 (1x; 0.0221 → 0.0228 at 2x). The specular is
*better on the pooled mean* because it happens to lift `dark-solid__rrect-md`'s top row from −0.061
to +0.062 against a reference of +0.047 — while leaving the bottom row at −0.061 against the same
+0.047. It buys one side by breaking the pair. G1 should state the objective **per contrast** (`T−B`
and `L−R`), not pooled over sides, or the pooled mean will keep a term the reference does not have.

### 3.2 `optics.regular.rimAlpha` (light profile): **DECLINE.** Its own rows re-choose it.

Rendered at `specularGain` 0 and `rimAlpha` 0.04 / 0.18, the per-row answers on the twelve
`light-solid` rows are **0.1684 – 0.1936 (1x)** and **0.1573 – 0.2162 (2x)**; the pooled minimiser is
**0.1819 (1x) / 0.1793 (2x)** against the shipped **0.18**. C9a §6.2's rule applies: left where it
is.

The four `dark-solid__rrect-md` rows demand 2.40–2.85 (1x) and 0.82–2.85 (2x) — the light material's
rim over a dark backdrop is 0.05–0.11 too dim and no admissible alpha reaches it, because the line's
slope there is 0.049 against 0.35 on the `light-solid` rows. That is §2.3's open cell restated as a
constant, and it is **not** `rimAlpha`'s to fix. `dark-solid__capsule-button` is dead in the fit
(slope 0.0000): the collapse folds the rim out entirely, exactly as W21 recorded for
`dark-solid__rrect-sm`.

The light profile's `rimIntensity` entry is `status: unchanged-deliberately` with the reason "the
signal being fitted is seven to twenty-six times below the capture's own resolution" — that was the
*silhouette-band* instrument. Under the declared read the rim excess on `light-solid__rrect-md` is
+0.0288 native against a code step of 0.0079, so the constant is now measurable and the entry's
`wouldNeed` ("the 2x profile") is satisfied. **G1 should re-record the entry's status even though its
value does not move**, because the reason it carried is no longer the reason.

### 3.3 `lightDirection`: **DECLINE on the rim rows; read the shadow rows separately.**

Two independent reasons. (i) At `specularPower` 6 the x-component −0.3714 contributes
`0.3714⁶ × 0.55 = 0.0014` of rim — below the instrument. The measured `L−R` at the shipped constants
is +0.0000 to +0.0009 on every solid at both scales, against the reference's −0.0002 to +0.0000: the
horizontal component is invisible in the rows and cannot be fitted on them. (ii) Its y-component is
what `specularGain` scales, so §3.1's fit to 0 makes the direction inert **on the rim**. It still
feeds the inner shadow through `optics.ts`'s `light.xy`, so it is not inert in the material — G1
must read the shadow rows before it touches the number, and this gate did not.

### 3.4 The dark patch's `rimAlpha` 0.082: **DECLINE. It does not move.** (`probe-fit-rim.txt`)

W21's fit re-run on W21's own bed, W21's own two rendered points and W21's own script, with the band
gone:

| | W21 (band present, left excluded) | W22 (band gone, all four sides) |
| --- | --- | --- |
| pooled minimiser | 0.0808 | **0.0818** |
| per-row span | 0.0440 – 0.0884 | 0.0441 – 0.0903 |
| median | 0.0807 | 0.0818 |
| confirmation at 0.082, mean \|Δ excess\| | 0.0068 | 0.0068 |
| clause-4 verdict, 24 sides | 18 MET, **6 MISSED** (all left) | **24 MET** |
| worst web flatness over four sides | 0.1436 | **0.0066** |

Left now equals right to the fourth decimal on every one of the six cells, and vitrea's flatness
(0.0000 – 0.0066) sits beside the reference's (0.0008 – 0.0044). The constant W21 fitted over three
sides is the constant its four sides choose.

Recorded, not fitted: the probe's `light-solid` cells under the dark patch are now symmetric and
uniformly **0.048 – 0.061 too dim on all four sides** (was three sides too dim and the left +0.089
too bright). W21's recorded residual survives the gate with its sign made consistent.

---

## 4. The gate's rows that move, and the gate's verdict (`moved-rows.txt`)

72 GPU-tier cells recaptured; **286 of 432 rows moved**, 130 unmoved (`rimPeakDistanceWeb` moved on
no cell at all — the band never moved the peak's position, only its height).

| row | cells moved | direction |
| --- | ---: | --- |
| `rimPeakLuminanceWeb` | 56 | down on every one; worst −0.0535 (2x dark `photo__rrect-md`, 0.1142 → 0.0607) |
| `rimFwhmWeb` | 56 | up (the band's removal narrows nothing; the remaining rim is the ambient one) |
| `interiorMeanWeb` | 58 | down; worst −0.0417 (2x dark `dark-solid__rrect-md`, 0.0976 → 0.0559) |
| `ssimMean` | 58 | up on all but a handful; best +0.0057 (1x dark `dark-solid__rrect-md`) |
| `oklabDeltaEMean` | 58 | down on all but a handful; best −0.00032 (1x dark `dark-solid__rrect-md`) |
| `rimPeakDistanceWeb` | 0 | — |

### Calibration ΔE mean, before → after

| profile | set | cells | before | after | Δ |
| --- | --- | ---: | ---: | ---: | ---: |
| 1x light | calibration | 20 | 0.00329 | 0.00329 | +0.00000 |
| 1x light | validation | 6 | 0.00259 | 0.00259 | −0.00000 |
| 2x light | calibration | 20 | 0.00334 | 0.00333 | −0.00000 |
| 2x light | validation | 6 | 0.00263 | 0.00262 | −0.00001 |
| 1x dark | calibration | 9 | 0.00410 | 0.00404 | **−0.00007** |
| 1x dark | validation | 1 | 0.00291 | 0.00291 | +0.00000 |
| 2x dark | calibration | 9 | 0.00410 | 0.00403 | **−0.00007** |
| 2x dark | validation | 1 | 0.00329 | 0.00329 | +0.00000 |

**No scheme, scale or set is worse.** Clause 4's "no worse anywhere" holds with room.

### S1, evaluated

Worst movement in the wrong direction: `oklabDeltaEMean` **+0.000025** (1x light
`dark-solid__rrect-md`, bound 0.001) and `ssimMean` **−0.000145** (1x light
`photo__capsule-button__rest-tint-blue`, bound −0.005). **S1 would fire on zero rows.**

### The gate over the merged matrix

`adopted-thresholds.test.ts` run with `VITREA_MATRIX_PATH` pointed at the canonical matrix with this
gate's 72 GPU rows substituted in place: **29 of 33 pass; 4 fail, all of one kind** — the coherence
axis's identity check (`interiorLevelRatioGpuOverCss` must equal the two tiers' own levels divided),
one profile each, mismatching by **0.0016 – 0.0039**. This is the merge's artefact, not a
regression: the CSS cells' recorded ratio was computed against the *old* GPU capture, and the axis
is re-derived when both tiers are recaptured together. **It is also W21's lesson arriving on
schedule: G1's dry run must run the gate over its own matrix, and G1/G2 should expect every dom-tier
`interiorLevelRatioGpuOverCss` row to move by up to 0.004.** The adopted bound on that row is
[0.8, 1.25] and the moved values (0.998 – 1.026) sit far inside it, so no bound is at risk.

**No floor goes inert and none can be re-read at this gate.** Every live `REGRESSION_FLOORS` entry
is either a dom-tier `ssimMean` row (the CSS tier draws no sweep) or one of the four W21 instrument
floors on the 2x dark nested pane, which is a holdout cell this gate did not open. Re-reading the
floors is G2's.

**No adopted bound was widened, and none needs to be.**

---

## 5. Eye finding 1 — the dark `impulse` capsule (`glow-reads/`, `read-glow.py`)

### 5.1 The size, measured under both instruments

`glow` is the mean over the box's central 16 × 16 CSS px minus the mean over the rest of the eroded
box: the structure the material passes, isolated from the level it sits at.

| 1x dark | body | sd | centre | surround | **glow** | rim T / B / L / R |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| native | 0.0066 | 0.0008 | 0.0080 | 0.0065 | **+0.0014** | 0.0145 / 0.0137 / 0.0041 / 0.0042 |
| vitrea at the gate | 0.0037 | 0.0001 | 0.0037 | 0.0037 | **+0.0000** | 0.0030 / 0.0030 / 0.0017 / 0.0017 |
| vitrea, `backdropToneMax` 0 | 0.0455 | 0.0027 | 0.0493 | 0.0452 | **+0.0041** | 0.0572 / 0.0562 / 0.0232 / 0.0232 |

| 2x dark | body | sd | centre | surround | **glow** | rim T / B / L / R |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| native | 0.0067 | 0.0015 | 0.0085 | 0.0065 | **+0.0019** | 0.0162 / 0.0153 / 0.0059 / 0.0061 |
| vitrea at the gate | 0.0033 | 0.0001 | 0.0033 | 0.0033 | **+0.0000** | 0.0027 / 0.0027 / 0.0016 / 0.0016 |
| vitrea, `backdropToneMax` 0 | 0.0457 | 0.0029 | 0.0500 | 0.0453 | **+0.0047** | 0.0709 / 0.0692 / 0.0249 / 0.0249 |

The two instruments reconciled: the declared body averages the whole capsule and reads 0.0066; the
silhouette interior (matrix `interiorMeanNative` 0.0210 at 1x, 0.0263 at 2x) is taken over the
fragments the extractor recovers, which over this backdrop are the rim ring and the glow — the two
bright things. **Both instruments are right about their own region.** The eye read a third thing,
and it is now a number: the reference passes a **+0.0014 / +0.0019** glow through the body and draws
a **0.0145 / 0.0162** top rim; vitrea passes **+0.0000** to four decimals and draws **0.0030**.

### 5.2 The mechanism, as far as the read shows it

Not the collapse constant, and not one constant at all.

- **The reference collapses over `dark-solid` and does NOT over `impulse`.** Over `dark-solid`
  (backdrop 0.0117 linear, sd 0.0000) the native body is 0.0110 — within 0.0007 of its own
  backdrop, collapsed, and vitrea matches it to 0.0007. Over `impulse` (backdrop 0.0030 linear, sd
  0.0550) the native body is 0.0066 — **2.2× its backdrop** — with a visible rim and a passed glow.
  The design's own rule then applies: *"if it collapses over `dark-solid` and not over `impulse`, the
  term is the appearance switch's (a scene-level input), and it is chartered, not tuned."*
- **A term keyed on the backdrop's mean level cannot separate the two cells**, because the collapse's
  argument is exactly that: `toneAdapt = strength × (1 − smoothstep(low, high, backdropLuminance +
  sizeBias·sizeK))` with `low` 0.02 and `high` 0.055. Both backdrops are far below `low`, so both
  collapse fully. What differs between them is the backdrop's **structure** (sd 0.0550 against
  0.0000), which the axis does not see.
- **The W9 response law has no anchor below `dark-solid`.** The dark anchors are encoded
  [0.1104, 0.2706, 0.9505]; `dark-solid`'s encoded mean *is* 0.1104 and `impulse`'s is **0.0030**,
  below the lowest anchor, so the law clamps and hands the two cells the same answer. The reference
  gives them 0.0110 and 0.0066. The probe that measured those anchors had no backdrop darker than
  `dark-solid`, so the anchor does not exist to be read.
- **`backdropToneMax` 0 is inadmissible, measured** (§5.3), and it overshoots the glow by 3×
  (+0.0041 against +0.0014) while overshooting the rim by 4× (0.0572 against 0.0145). No single
  collapse strength lands both: the reference's body sits 7% of the way from the collapsed to the
  un-collapsed reading and its rim sits 21% of the way.

### 5.3 The prediction the design asked for, across the whole dark bed

`backdropToneMax` 0 in a scratch dark patch, GPU tier, both scales, calibration+validation. The last
two columns are |body − native| before and after; the numbers are 1x, with 2x within 0.0003 of every
one of them.

| cell | Δ body | Δ glow | Δ rim T | \|Δ\| now | \|Δ\| at max 0 | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `dark-solid__capsule-button` | +0.0350 | −0.0000 | +0.0500 | 0.0007 | **0.0357** | far worse — **the stop fires** |
| `impulse__capsule-button` | +0.0419 | +0.0041 | +0.0542 | 0.0030 | **0.0389** | far worse |
| `dark-solid__rrect-md` | +0.0337 | +0.0000 | +0.0249 | 0.0023 | 0.0314 | far worse |
| `checkerboard__rrect-md` | +0.0452 | +0.0001 | +0.0348 | 0.0007 | 0.0458 | far worse |
| `photo__rrect-md` | +0.0269 | +0.0000 | +0.0205 | 0.0077 | 0.0193 | worse |
| `checkerboard__capsule-button` | +0.0277 | −0.0000 | +0.0195 | 0.0387 | **0.0109** | better |
| `photo__capsule-button` | +0.0132 | +0.0000 | +0.0091 | 0.0433 | **0.0302** | better |
| the three tinted cells | ≤ 0.0001 | ≤ 0.0001 | ≤ 0.0029 | — | — | inert |

**The `dark-solid` capsule is the stop the design named and it fires:** the dark reference collapses
there (native 0.0110 against a 0.0117 backdrop) and un-collapsing takes vitrea from 0.0007 to 0.0357
of error on that one cell. The two cells that improve are exactly W21's two "appearance term" misses
(the thin capsules over structured backdrops, claims §5.90 §5), which is worth recording: **the
appearance term and the collapse are the same axis pulling in two directions**, and one constant
cannot serve both.

### 5.4 Recommendation

**Charter, with these numbers.** It is not one constant on its own rows: the discriminating input
(backdrop structure, or a scene-level appearance state) is not in the axis's argument, the response
law lacks an anchor below encoded 0.1104, and the one constant the design proposed as a test is
measurably inadmissible. It joins the appearance-switch spike (W21 Deferred) — which the design
already anticipated — carrying: the glow (+0.0014 / +0.0019 against +0.0000), the top rim (0.0145 /
0.0162 against 0.0030), the missing anchor (encoded 0.0030 against a lowest anchor of 0.1104), and
the `backdropToneMax` 0 table above as the bound on what the existing axis can buy.

---

## 6. Eye finding 2 — the nested pane (`stack.txt`, `overlay-prediction.txt`, `read-stack.py`)

### 6.1 The reader, extended and validated (X3)

`read-stack.py` gives a stack two bodies and eight sides: the base's declared box eroded 6 CSS px
with the overlay's box **dilated** 6 px cut out, the overlay's box eroded 6 px, and each pane's
outer 3 px as its own rim band. The placement is `component-region.ts`'s rule restated in one
function and printed — base 220 × 130 at (50, 35), overlay 120 × 56 at (100, 64) — and the reader
asserts that the overlay clears the base's band on every side rather than assuming it (smallest gap
29 CSS px, at the top).

**X3, by injection on a stack:** known levels painted into a copy of a capture and recovered through
the same masks and the same peak statistic — base body 0.0450 → 0.0450 (err 0.000000), overlay body
0.0320 → 0.0320 (err 0.000000), eight rim peaks recovered with errors 0.000000 – 0.000625. **Worst
recovery error over the ten quantities: 0.000625**, which is the instrument's floor on this
geometry. Every number in §6.2 is far above it.

### 6.2 The panes, per scheme, per tier, per scale

`excess` = overlay body − base body. **The web column is the canonical `web-captures/` at the 0.10.0
landing — both cells are HOLDOUT and this gate took no capture of them (X5).**

| profile | tier | cell | which | base | over | excess | baseSd | overSd | blurσ‑match |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x dark | webgpu | `checkerboard__gog` | native | 0.0467 | 0.0207 | **−0.0260** | 0.0165 | 0.0011 | 1.50 |
| 1x dark | webgpu | `checkerboard__gog` | web | 0.0470 | 0.0493 | **+0.0023** | 0.0205 | 0.0007 | 2.20 |
| 1x dark | css | `checkerboard__gog` | web | 0.0454 | 0.0502 | **+0.0048** | 0.0192 | 0.0015 | 2.00 |
| 2x dark | webgpu | `checkerboard__gog` | native | 0.0475 | 0.0208 | **−0.0267** | 0.0196 | 0.0017 | 16.00 |
| 2x dark | webgpu | `checkerboard__gog` | web | 0.0475 | 0.0494 | **+0.0018** | 0.0224 | 0.0008 | 8.00 |
| 2x dark | css | `checkerboard__gog` | web | 0.0481 | 0.0506 | **+0.0025** | 0.0191 | 0.0014 | 5.50 |
| 1x light | webgpu | `checkerboard__gog` | native | 0.6676 | 0.9047 | +0.2371 | 0.0940 | 0.0078 | 1.50 |
| 1x light | webgpu | `checkerboard__gog` | web | 0.6611 | 0.8902 | +0.2291 | 0.0959 | 0.0128 | 2.20 |
| 1x light | webgpu | `photo__gog` | native | 0.6497 | 0.8936 | +0.2439 | 0.0690 | 0.0118 | 16.00 |
| 1x light | webgpu | `photo__gog` | web | 0.6313 | 0.8736 | +0.2423 | 0.0578 | 0.0099 | 16.00 |
| 1x light | css | `checkerboard__gog` | web | 0.6647 | 0.8432 | +0.1784 | 0.0909 | 0.0231 | 1.70 |
| 2x light | webgpu | `checkerboard__gog` | web | 0.6673 | 0.8925 | +0.2252 | 0.1035 | 0.0163 | 7.50 |

**The size: 0.0283 (1x) / 0.0285 (2x) on the GPU tier, 0.0308 / 0.0292 on the CSS tier — the
overlay's body alone.** The base pane is right to 0.0003 – 0.0012 in dark. In the light scheme both
sides agree in sign and to 0.008 – 0.012 on the GPU tier (the CSS tier is 0.06 short, a separate
CSS-only residual). **The inversion is dark-only and overlay-only, at both scales and on both
tiers.**

### 6.3 What the overlay's backdrop actually is, on the web (`overlay-prediction.txt`)

`web/scenes.ts` declares the base group `texture` and the overlay group `dom`; on the GPU tier that
resolves to `samplingBackend: "css-backdrop"`, and the plane sandwich composites the overlay's proxy
after the base plane's optics canvas — so the overlay's backdrop **should be** the base pane's
rendered output, which this gate measured directly at **0.0470 linear (encoded 0.2402)**.

Evaluating the *shipped dark response law* (`backdropToneResponse`, reimplemented term for term)
at that input:

| | 1x dark | 2x dark |
| --- | ---: | ---: |
| the base pane's own body (the overlay's backdrop) | 0.0470 | 0.0475 |
| its encoded mean — the law's input | 0.2402 | 0.2415 |
| **the law's answer, thin row** | **0.0245** | **0.0246** |
| the law's answer, thick row | 0.0214 | 0.0215 |
| **the reference's overlay** | **0.0207** | **0.0208** |
| **what vitrea's overlay drew** | **0.0493** | **0.0494** |
| the encoded input the law would need to draw that | **0.4022** | 0.4025 |
| that input, in linear luminance | **0.1344** | 0.1346 |

**The law is right and the input is wrong.** At the overlay's true backdrop the shipped dark law
lands within 0.0038 of the reference (0.0007 on the thick row); the capture is 2.0× the law's answer
and corresponds to a backdrop of 0.1344 linear — **2.9× the base pane's actual output**. So the
answer to the design's question is: *the overlay is not being handed the base's rendered output*.
The flat mid grey is an input error, not a response-law miss.

A candidate mechanism, with its arithmetic, **flagged as untested here**: 0.1344 is what you get by
mixing 19.3% of the raw checkerboard (0.500) into 80.7% of the base's output (0.0470). The overlay's
proxy rect is the group's rect expanded by the field rect, which W8 made much larger for the outer
shadow; the overlay sits 29 CSS px below the base's top edge, so an expansion of roughly 50 px puts
about that share of the sampled rect over raw checkerboard outside the base pane. Naming it exactly
needs a probe on the proxy's readback and its `backdropTone` measurement, which this gate could not
run because the cell is holdout.

### 6.4 The base pane's haze, handed to the thick-span composite by name

Under the whole-region match statistic (`blurSigmaMatchPx`; not the matrix's edge-spread
`blurSigmaNative`), the dark base pane at 2x matches at σ **16.00 native against 8.00 web** — the
native value is at the search grid's ceiling, so the reference's haze is ≥ 16 px and the residual is
≥ 8 px. In light at 2x it is 16.00 against 7.50 on `checkerboard` and 16.00 against 12.50 on
`photo`. The base pane's interior sd tracks it: native 0.0196 against web 0.0224 in dark 2x, native
0.1095 against web 0.1035 in light 2x. This belongs to the thick-span composite (wave Decision Log
23 (c)) and is handed over as such.

### 6.5 Recommendation

**Charter.** Two separate things, neither a constant:

1. **The overlay's backdrop input** (§6.3) — a plumbing defect worth 0.028 of luminance on the
   overlay's body in dark, invisible in light because the same error moves a bright backdrop very
   little. It is diagnosable in one bounded probe (read the overlay group's resolved
   `backdropTone` and its proxy rect against the base pane's output) and fixable in the sampling
   path, not in `material.ts`. Recommend a spike of its own; it is bigger than a wave clause but
   much smaller than the thick-span composite.
2. **The base pane's haze** (§6.4) — already chartered as the thick-span composite; this gate adds
   the per-pane number it lacked.

---

## 7. Gaps, blocks and instrument notes for the ledger

1. **The holdout could not be read, so the nested pane has no "after" column.** Both
   `glass-over-glass` cells are holdout; X5 reserves the wave's one read for G1. G1 should re-read
   both panes with `read-stack.py` when it opens the holdout, and G2 should re-read the four W21
   instrument floors that sit on the 2x dark nested pane — none of them could be touched here.
2. **The declared reader's `H−V` is a geometric artefact, not a light direction** (§2.2). Measured,
   with the covered fractions and a two-sided sign check. `L−R` and `T−B` are clean. This belongs
   beside the instrument in the ledger.
3. **A new open cell: `dark-solid__rrect-md` under the LIGHT profile** misses clause 2 on three
   sides at 1x and four at 2x, worst −0.093 / −0.088 on the bottom (§2.3). The light material's rim
   over a dark backdrop is too dim by 0.05–0.11 and `rimAlpha`'s rows there demand 2.4–2.9, so no
   admissible value reaches it. It was hidden under the band; it is not created by the gate.
4. **The dom-tier coherence rows will move by up to 0.004** at the landing (§4). Far inside the
   adopted [0.8, 1.25] bound, but the identity check fails on any partial rebuild, so G1's dry run
   must capture both tiers together and run the gate over its own matrix.
5. **The light profile's `rimIntensity` entry carries a superseded reason** (§3.2): "below the
   capture's own resolution" was the silhouette-band instrument's finding, and the declared read
   measures the same rim at 0.0288 against a 0.0079 code step. The value does not move; the reason
   should be re-recorded.
6. **`--alpha` is not optional on a scratch bed** that will be run through `adopted-thresholds`. The
   first capture pass omitted it and the W20 conformance rows failed for absence; the second pass
   reproduced every capture **byte for byte** (72/72) with the alpha rows added, which is recorded
   in `digests.sh`'s two runs.
7. **The appearance term and the collapse are one axis pulling two ways** (§5.3): the setting that
   fixes W21's two thin structured-backdrop capsules is the setting that breaks the four cells the
   collapse currently gets right. Whoever takes the appearance switch needs both halves of that
   table.

---

## 8. Files

| file | what |
| --- | --- |
| `g0-capture.sh` | the bed at the gate, four profiles, GPU, scratch |
| `g0-fit-capture.sh`, `make-candidates.mjs` | the fit's rendered points and the collapse prediction |
| `g0-probe-capture.sh` | W21's probe grid at the gate, for §3.4 |
| `read-canonical.sh`, `tables.py`, `per-side.txt` | §1, §2 |
| `check-isolation.py`, `isolation.txt` | §1's isolation — which sides moved, and by how much |
| `fit-rim.py`, `run-fit-reads.sh`, `fit-rim-1x.txt`, `fit-rim-2x.txt` | §3.1 – §3.3 |
| `run-probe-fit.sh`, `probe-fit-rim.txt`, `probe-reads/` | §3.4 |
| `moved-rows.py`, `moved-rows.txt` | §4 |
| `read-glow.py`, `run-glow.sh`, `glow-reads/` | §5 |
| `read-stack.py`, `run-stack.sh`, `stack-tables.py`, `stack.txt`, `stack-reads/` | §6.1, §6.2 |
| `predict-overlay.py`, `overlay-prediction.txt` | §6.3 |
| `digests.sh` | the sha256 of every capture this gate produced |
| `canonical-reads/`, `fit-reads/` | the per-cell JSON every table is computed from |
