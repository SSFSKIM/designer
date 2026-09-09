# W25 G3 — the declaration, and the dry run on the frozen configuration

The wave's rule: declare the constants, the fingerprints and what would stop the change **before**
running the bed. Everything above the horizontal rule was written before this gate captured a
single canonical pixel; everything below it is what the run then read.

---

## 0. The goldens first, and they did not move

G2 left one command pending: the level term's re-form moved `+ levelFar` from `tone_response`'s
blend to its return, and the WGSL could not be pinned without a GPU while the parent's sitting held
every capture. Run first, in the foreground, at the inert defaults:

```
cd packages/renderer-webgpu && npx playwright test --grep @golden
```

**33 of 33 passed and no golden byte changed** (`git status` clean afterwards), which is exactly
G2 §8's stated expectation. The re-form is `+ 0.0` on the shipped material at every span and every
ratio on the GPU as it is on the CPU.

## 1. What lands, and what the evidence for each is

**One constant lands and three are declined, and every one of the four is a measurement on the
probe set.** That set is what this wave built: 52 scenes at both scales in both schemes, captured
by G1's sitting (claims §5.115) and rendered on the web at every rung of this child's ladder into
scratch, read by G0's own three readers.

| constant | before | after | fitted on |
| --- | --- | --- | --- |
| `optics.regular.rimAlongSideSlope` | 0 | **0.45** | 64 straight sides of six thick cells over the three flat solids, both scales, both schemes |
| `sizeScatterHeavyShareThick1x` | 0 | **0, declined** | identified at ≈0.5 by 3 rows; every check off them runs the other way |
| `sizeScatterHeavyShareThick2x` | 0 | **0, declined** | arithmetically inert: 206 of 206 2x probe captures byte-identical at a lift of 0.50 |
| `sizeToneLevelFar` | 0 | **0, declined** | the sign flips with the row set in both schemes |
| a `blurSigma2x` sibling | absent | **not added** | the 2x coarse checkerboards identify one combined width, not the sharp component |

`optics.clear.rimAlongSideSlope` stays 0 — no scene on either bed declares that variant, so it has
no rows (C9a §6.2), which is the rule the lit edge's exponent takes there too. Nothing else on
either document moves: `blurSigma`, the ramp's anchors, `sizeScatterFloor`, `sizeScatterSpanMax`,
`sizeSpanMin`, `sizeSpanMax`, W23's rim law and W24's lit edge and transmission are all where their
own rows put them.

### 1.1 The along-side field — the one that lands

**The form was chosen by the rows before it was fitted, and this child did not choose it.** G0 read
the reference's rim by POSITION along a straight side instead of by the normal's direction and
found the four sides' slopes exactly antisymmetric — top −0.000192 against bottom +0.000192 and
left −0.000379 against right +0.000379 luma per CSS px on the 1x dark `dark-solid__rrect-md`. A
field linear in position gives the top and the bottom the same slope in x and cannot have that; the
PRODUCT of the two normalised coordinates does, and it is +1 at exactly the two corners the
reference draws brightest — the same diagonal W24's `rimLitAxis` is symmetric about. So this is the
POSITION half of the light whose DIRECTION half W24 landed, not a second light.

**The fit, on the probe set.** 64 straight sides of `dark-solid__rrect-ml`, `dark-solid__rrect-lg`,
`light-solid__rrect-lg`, `mid-dark-solid__rrect-md` and `mid-dark-solid__rrect-lg` at both scales in
both schemes, every one of them a row G2 did not use:

```
implied slope   median 0.479   lever-weighted 0.425   quartiles 0.324 … 0.625
by group        1x light 0.35   1x dark 0.55   2x light 0.45   2x dark 0.63
condition       the rendered lever runs 3.7e-05 … 4.4e-03 luma per CSS px per unit slope
```

**The value is 0.45 and the reason is that two independent row sets bracket it.** G2 fitted 0.45 on
the 64 sides of the two 1x probe grids' solids; this child's two summary statistics on a disjoint
row set are 0.425 and 0.479. One constant is what the rows separate: the four groups overlap
throughout and none of them is outside the others' quartiles.

**The check off the fitted rows.** The rows ask for no further slope — G2's re-fit at the same value
read a median implied residual of −0.004 against +0.452 at the default — and the constant costs
nothing measurable anywhere else. Over the whole probe set the mean OKLab ΔE moves **−0.00001**; the
worst thick cell rises 0.000056 and the worst thin cell 0.000004 against X5's bound of 0.001.

**What it does not close, and it is recorded rather than chartered.** The corner-to-corner range
reaches about three quarters of the reference's (27 of 64 sides inside 20 %); the last quarter is in
W23's rim AMPLITUDE law, which was fitted on the straight spans this factor deliberately leaves
alone. And the 2x reference's rim is top-left/bottom-right asymmetric in its MEAN as well as its
gradient, which a factor that grades cannot draw.

### 1.2 The heavy share — identified, and declined on its own checks

The wave's charter named the heavy share as the thick-span mechanism (Decision Log 3 (a)), and the
probe set does identify it. Reader A's own share on the two 1x `impulse` rows above the knee:

| row | span | reference | vitrea | rendered lever | implied lift |
| --- | --- | --- | --- | --- | --- |
| `impulse__rrect-ml` 1x light | 128 | 0.674 | 0.354 | 1.00 / unit | **0.320** |
| `impulse__rrect-lg` 1x light | 160 | 0.727 | 0.492 | 0.35 / unit | **0.670** |
| `impulse__rrect-md` 1x (canonical, validation) | 96 | 0.473 | 0.233 | — | ≈0.51 (G2) |

The other four `impulse` rows are refused rather than averaged in, and each refusal is a reading:
`rrect-sm` at span 32 is thin on both sides (share 0.000), the 1x dark `rrect-lg` is the collapsed
160 px panel, and the 1x dark `rrect-ml` reads 0.743 native against a web fit that has degenerated
to one Gaussian.

**Every check off those rows runs the other way, and the direction is the same one G2 found on a
different fixture.**

- The coarse checkerboards' single-width objective, `mean |log(web/native)|` over 24 thick rows
  inside both readers' bounds, worsens **0.2373 → 0.3402** at a lift of 0.45.
- Nine probe rows are worse by more than S14's 0.002 ΔE at a lift of 0.45 and **five already at a
  lift of 0.18**, which closes barely a third of the share — the cost is concave and most of it is
  spent before the constant does any good.
- The probe set's mean rises **+0.00018** (+0.00065 on the 1x light rows) against parent clause 6's
  0.0001.

**The measured reason is a width and not a share.** vitrea's heavy component is 13.3 device px at
the reference's own share where the reference's is 19.5, and `sizeScatterGainMax` is not a lever on
it: G2's rung `rG` raised it 8 → 10.3 and reader A's heavy reading did not move from 13.29, because
the heavy tap is a mip-chain level whose effective width saturates there. More of a too-narrow heavy
component is more of the wrong thing, and the ΔE that says so is not perceptual noise — it is the
interior of a coarse checkerboard being washed flatter than Apple washes it.

**The ruling this child takes, and whose it is.** Decision Log 4 (c) refused this landing when it
rested on one validation row whose off-row check ran the other way, at a cost above the clause, and
sent it to the probe set. The probe set has now answered on three rows and the answer is the same,
more strongly. The constant waits for the width, which is the next wave's, and the rows that would
fit it are named in §1.5.

### 1.3 The 2x share — inert, and the inertness is measured

At dpr 2 `sizeScatterFloor2x` is 1, so `kDeep` is saturated before the lift is added and
`clampUnit` absorbs it. This child measured that rather than restating it: at
`sizeScatterHeavyShareThick2x` = 0.50, **all 206 of the probe set's 2x captures are byte-identical
to the inert ones** and reader A's rendered lever is exactly 0.000 on every 2x row.

Decision Log 4 (e) asked for the 2x share to be fitted "through the floor (or the constant that has
headroom), and say which". **The answer is: neither, and here is why.** The constant with headroom
is `sizeScatterFloor2x` itself — W15's, fitted at 1 on the 2x body — and it enters
`floor + (1 − floor) · smoothstep(sizeSpanMin, sizeScatterSpanMax, span)`, which reaches EVERY 2x
span including the thin capsule at 44 and `rrect-sm` at 32. X5 forbids moving it in this wave, and
it would be a re-fit of a W15 constant rather than a fit of a W25 one.

### 1.4 The level term — the sign flips with the row set

`sizeToneLevelFar`, fitted per scheme by a rendered lever at ±0.05, in 8-bit display codes:

| rows | light | dark |
| --- | --- | --- |
| the wave's declared set (the three solids and the checkerboards at spans 80/96/128/160) | **−0.0035** over 28 rows, RMS 1.193 → **1.224 (worse)** | **−0.0074** over 16 rows, RMS 2.169 → 1.948 |
| every untinted probe backdrop above the knee | **+0.0046** over 34 rows, RMS 1.278 → 1.223 | **+0.0006** over 22 rows, RMS 2.978 → **3.015 (worse)** |

A constant whose sign depends on which backdrops are counted, and whose residual moves by less than
a twentieth of a code either way, is not identified (C9a §6.2). G2's +0.029 from the W9 grid's 14
rows does not reproduce against the sitting's own reference captures, and Decision Log 5 (d)'s
scheme separation is answered by neither scheme identifying it rather than by the two schemes
disagreeing.

**The controls hold either way, and they are what made the probe safe.** 32 rows at and below span
96 have a rendered lever of **exactly 0.0000** codes per unit, so no value of this constant could
have reached the bed the rest of the material was fitted on.

### 1.5 A `blurSigma2x` sibling — not added

Decision Log 4 (e) made it conditional on the 2x coarse checkerboards identifying it. They identify
a WIDTH; they do not identify the SHARP COMPONENT, and the difference is the whole question.
Reader A's two-component fit degenerates at 2x above the knee — sharp 11.80 and heavy 12.03 device
px with the share pinned at 1.000 on the 2x light `impulse__rrect-ml`, 10.01 / 12.58 on the dark one
— so what those rows carry is one combined number. Read as one number the 2x thick rows are already
close: reader B on `checkerboard-64` at 2x, inside its bound there (the pitch is 128 device px),
reads native 7.09 / 8.42 / 8.98 against vitrea's 8.15 / 8.58 / 11.70 at spans 96 / 128 / 160. And a
per-scale sharp anchor reaches every 2x span including the thin capsule, which X5 forbids.

**The rows that would close the wave's two declined constants**, so the next charter has them: a
2x `impulse` row over a surface whose span is above 96 and whose reference has NOT collapsed, which
would separate the 2x triple; and a heavy tap whose width follows a constant, which is a renderer
change (`packages/renderer-webgpu/src/wgsl/`) and not a fit — the mip-chain level is what saturates.

## 2. The fingerprints

| document | before | after |
| --- | --- | --- |
| `apple-macos-26.5-1x-light-standard.json` | `52a633135b9da151` | **`290f52cb025fce7b`** |
| `apple-macos-26.5-1x-dark-standard.json` | `2f47777637f8df50` | **`64ef5c3002d15009`** |

Both documents move, so all six profiles are re-run and none rides along as a byte check. The dark
document's own `patch` does not move — the field is the material's and lives on the shared default —
so `platform-web/src/dark-profile.ts` regenerates **byte-identical** (X7), verified by running
`profile:dark` and diffing before the run.

## 3. The stops, declared

W24 G2's S1–S8, S10 and S11, with W24's angular reads added to S11's family, plus this wave's three.

- **S1** — any untinted row worse than the 0.13.0 bed by more than 0.001 ΔE mean or 0.005
  `ssimMean`.
- **S2** — any tinted cell moved by more than 0.002 in body.
- **S3** — a calibration ΔE mean above the 0.13.0 bed's by more than 0.0001.
- **S4** — a golden moved for any reason but the field.
- **S5** — a fitted constant whose rows do not separate it.
- **S6** — a CSS capture moved without an explanation. This wave's prediction is sharper than the
  last wave's could be: **every CSS capture should be byte-identical**, because the field's integral
  around the contour is exactly zero and `interiorBandLight` integrates that band.
- **S7** — a collapsed cell whose body moves by more than 0.002.
- **S8** — the user's eye.
- **S10** — a cell the field cannot reach that moves at all.
- **S11** — W23's straight-span contour reads moved by more than 0.005 on any solid side, and
  W24's angular bins moved by more than 0.005 on any bin of any untinted solid row.
- **S12** — any thin cell (span at or below 44) moved by more than 0.001 ΔE.
- **S13** — a golden moved outside a thick surface's body or rim.
- **S14** — a probe row worse by more than 0.002 ΔE at the fitted constants than at the inert ones.

## 4. How the bed is run

`g3-dryrun-run.sh`, all six profiles on both tiers, **calibration and validation first**; then, only
once every clause and every stop above has been read on those rows, `g3-holdout-run.sh`. **This is
the wave's one holdout read (X3)**, taken on the constant above and on nothing else; G4 reproduces
every capture byte for byte from `g3-digests.txt`. Captures and matrix go to scratch through
`VITREA_WEB_CAPTURES` and `--out-matrix`; the canonical `results/matrix.json`, `web-captures/`,
`apps/reference-apple/fixtures/` and `scenes.json` are untouched. The flags are the canonical
rebuild's — `--alpha` and `--write-partial` — because G4 has to reproduce these bytes with them.

## 5. What the CSS tier takes, and what it cannot

**Nothing, and the reason is exact rather than a limitation discovered late.** The field is
`(x/hw)·(y/hh)`, odd under `x → −x` and under `y → −y`, so its integral around the whole contour —
straight runs and corner arcs alike — is zero, and `1 + 0.45 · field` is never clamped because
`|field| ≤ 1`. `interiorBandLight` integrates the renderer's band; a term whose integral is zero
adds nothing to integrate, so the two tiers' derived interior level is the same number with the
field and without it at every span and every slope. The mirror therefore does NOT gain a
`rimAlongSideSlope` (a constant nothing reads is not carried, C9a §6.2), and that is written into
`platform-web/src/optics.ts` beside `rimLitExponent`, which IS mirrored precisely because it does
not integrate to zero.

`blur()` is at the shared σ and does not move: `blurSigma` is untouched this wave, and the sharp
component's 1.67-against-2.79 gap at 1x is W25's recorded gap and not its constant.
`interiorBandLight` is unchanged by the field. The coherence pin
(`crossTierOklabDeltaEMean` ≤ 0.05) is re-read below rather than asserted.

**X8's residual is the FEATURE, and it is recorded and not chartered** (wave Decision Log 23 (a)):
this tier draws one inset shadow with one alpha the whole way round and cannot make a rim brighter
at two corners than at the other two, while remaining exactly coherent with the GPU tier's side
mean. That is a real difference to macOS on the CSS tier and it is in the ledger.

## 6. The goldens, re-recorded with the attribution measured

`goldens-attribution.txt`, from `g3-golden-attribution.spec.ts` run before any golden byte was
rewritten: every scene rendered at the landed slope and again with the field declined, compared per
pixel inside a contour band (3 px of a coverage discontinuity, from the landed render's own alpha)
and outside it.

**The field moved not one pixel outside a contour band, on any scene** — its outside delta is 0 on
all thirteen. Inside, it is 2–23 code values on the twelve that carry a rim (371–2 972 pixels), and
the order of the twelve is the order of their spans, which is the size law showing up in a hash
table: `collapsed-tone` at span 44 moves 2 codes and `union-pair` at 52 moves 4, where `field-mask`
at 68 moves 23 and `rim-two-references` at 88 moves 14 on 2 972 pixels. `highlight-press-glow` is
the control and holds at **0 pixels**, byte-identical to its 2026-08-25 original for the twelfth
wave running.

Twelve hashes are re-recorded under `W25_HASHES`, and two other pins move with them:
`PLACED_CHECKERBOARD_COVER_HASH` in `scenes.spec.ts` (the cover-fit render draws the graded rim like
the placed one does) and, not a hash at all, one assertion inside the isolation proof —

**One bound was NARROWED and it is named here rather than buried.** `the outer shadow is the whole
of W8's delta` asserted that toggling the shadow moves not one colour channel and takes no pixel's
alpha down. Both canvas passes blend premultiplied source-over into an eight-bit target, so the
optics pass composites onto an already-quantised shadow; where the rim is brighter the two roundings
can differ. Measured: 45 colour channels move by exactly 1 on 15 pixels lying on the contour at the
checkerboard's own 16 px pitch (six up, two down, alpha unchanged), and 5 pixels in the canvas's
last column take alpha down by exactly 1 with their RGB unchanged — and at slope 0 both counts are
0, which is why the strict form held for eleven waves. The assertions are now "no channel by more
than one code, on fewer than a thousandth of the canvas" with the measurement in the doc comment.
The guard's content is unchanged: a shadow that put colour on this canvas would move many pixels by
many codes in one direction.

**What the golden suite cannot show, and where the thin claim lives instead.** No golden scene has a
span at or below 32 — the smallest is 44 — so the attribution's thin assertion is vacuous by
construction and is not evidence. The claim is carried by `test/thick-span.test.ts`, where the
factor is `toBe` exactly 1 at spans 0, 8, 16, 31 and 32 at every slope, and by the probe set, where
the worst thin cell moved 0.000004 ΔE.

## G3b. The re-declaration, on the parent's ruling (W25 Decision Log 6)

**Everything in §§1–6 above stands as the record of what W25 G3 declared and ran. It is not
rewritten.** The parent ruled on S11b's firing (§7.11 below): the confound is resolved by a JOINT
re-fit of W24's `rimLitExponent` with `rimAlongSideSlope`, on existing fixtures, and the W24
constant is re-opened by that decision. The four declines of §1.2–§1.5 stand as ruled — the 1x
share, the 2x share, the level term and the `blurSigma2x` sibling stay at their inert values and
the heavy width is the next wave's. This section is written above the rule for the same reason §§1–6
were: it was written before the second dry run captured a canonical pixel.

### G3b.1 What lands now

| constant | 0.13.0 | W25 G3 declared | **W25 G3b lands** |
| --- | --- | --- | --- |
| `optics.regular.rimLitExponent` | 1.15 | 1.15 | **0.85** |
| `optics.regular.rimAlongSideSlope` | 0 | 0.45 | **0.10** |

### G3b.2 The joint fit

**Why a grid and not a lever.** Every other fit in this wave used a rendered lever, because one
constant moved one quantity monotonically. These two do not: they multiply the same rim amplitude,
both peak on the same top-left/bottom-right diagonal, and the exponent's factor is a POWER, so the
surface is not separable and a derivative at one point does not locate the minimum of the other.
**Forty-six points, each one a real render** of the solid rows of all four standard profiles
(`g3b-ladder.sh`, about a minute a point), read by W24's angular reader and W25's along-side reader
in the same pass (`g3b-read.py`) and scored with no model of the rim between the objective and the
pixels (`g3b-fit.py`, `g3b-fit.txt`).

**The rows.** The five untinted flat-solid CALIBRATION cells of the canonical bed and the twelve
solid rows of the probe set, on all four standard profiles — 54 rows carrying 864 angular bins and
58 rows carrying 220 straight sides. The bed's one holdout solid,
`mid-dark-solid__capsule-button__rest`, is never opened (X3). Two exclusions beyond that, both
stated rather than silent: `dark-solid__rrect-md-clear20` is out of the ANGULAR half because W24's
reader centres a component and that cell is displaced 32 points down; and **four rows are refused by
a guard** — a row whose normalised angular error at the 0.13.0 material already exceeds 1 is not a
rim-shape row, because vitrea's bins differ from the reference's by more than the reference's own
brightest bin and the two are not drawing the same material there. Measured, they are
`light-solid__rrect-sm` in the dark profiles (19.9, claims §5.115 §3's size-keyed scheme adaptation)
and `dark-solid__rrect-64` in the light profiles (3.6–3.9, where the reference has collapsed at span
64 and vitrea has not). Both are body gaps wearing a rim reader's numbers.

**The objective and its weighting.**

```
A = mean over rows of the mean |web − native| over the sixteen angular bins
R = mean over straight sides of |range(web) − range(native)|
    — each row divided by its OWN brightest native bin, so the two are commensurate
J = A + w·R,  w chosen so the two contribute EQUALLY at the 0.13.0 material:  w = 0.3951
A(0.13.0) = 0.16206      R(0.13.0) = 0.41021
```

**The sensitivity, stated rather than claimed away.** Over the whole grid the objective's minimum is
(0.55, 0.45) at every weight in ±50 %. Over the ALLOWED set — see G3b.3 — the pick is (0.70, 0.15)
at w×{0.75, 1.0, 1.25, 1.5} and (0.85, 0.10) at w×0.5, one grid step in each coordinate. **The
landing is (0.85, 0.10), which is inside that band rather than at one end of it**, and the two
candidates' thick readings are close (bin 0.17208 against 0.17000, range 0.37472 against 0.34919).

### G3b.3 Why the objective's minimum is not what lands

**The ruling's acceptance condition is not the objective, and on this plane they disagree.** The
objective's own minimum, (0.55, 0.45), improves only 5 of 28 thick solid rows; **no point of the
plane with a slope at or above 0.20 keeps the thick solids' angular error at or under the 0.13.0
bed's.** Among the pairs that do, the objective's minimum is (0.70, 0.15).

**And (0.70, 0.15) is refused, for a reason no metric in the objective carries.** At that pair the
collapsed `dark-solid__capsule-button` loses its contour on the GPU tier at 1x in BOTH schemes: the
capsule's band is entirely corner arc, which is exactly where both of these factors dim it, the
extractor reads a 0.00 px contour, and **two calibration cells drop out of the bed.** Measured one
scene at a time rather than inferred: (0.70, 0.15) unmeasurable, (0.85, 0.10) measurable on all four
standard profiles, (0.70, 0.00) measurable — so it is the pair and not either constant alone. A
change that narrows the instrument is not a fidelity gain, and this is the second time in one wave
that the declared objective and the bed's own health have had to be read against each other.

**So the landing is the objective's minimum among the pairs that both keep the thick solids at or
under the bed AND leave every cell measurable: (0.85, 0.10).** Its readings against the 0.13.0
material, on the 28 thick solid rows: **mean bin error 0.17527 → 0.17208 and range error 0.43269 →
0.37472, with 16 rows improving against 12.**

### G3b.4 The per-bin table the ruling asked for

1x light `dark-solid__rrect-md`, the cell S11b fired on, normalised by the reference's own brightest
bin (0.18919 linear luma). `g3b-bins.txt` carries the same table at every candidate and the 1x dark
row beside it.

| bin | reference | 0.13.0 (1.15, 0) | error | G3 (1.15, 0.45) | error | **G3b (0.85, 0.10)** | **error** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N (a straight side) | 0.18882 | 0.20906 | 0.02023 | 0.21205 | 0.02322 | 0.21128 | 0.02246 |
| NNE | 0.03598 | 0.06435 | 0.02837 | 0.03902 | 0.00304 | 0.07105 | 0.03507 |
| NE (the null) | 0.03661 | 0.00439 | 0.03221 | −0.00078 | 0.03739 | 0.00952 | 0.02708 |
| ENE | 0.03815 | 0.06440 | 0.02625 | 0.04129 | 0.00314 | 0.07185 | 0.03370 |
| SE (a bright corner) | 0.12739 | 0.14384 | 0.01645 | 0.20347 | 0.07608 | 0.13867 | 0.01128 |
| NW (the other) | 0.12223 | 0.14220 | 0.01997 | 0.20344 | 0.08121 | 0.13740 | 0.01517 |
| **mean, normalised** | | | **0.18398** | | **0.30073** | | **0.18738** |

The shape of it: **the two bright corners come back inside the reference** (NW 0.020 → 0.015, SE
0.016 → 0.011, where G3's landing took them to 0.081 and 0.076), the null lifts toward the
reference's own shallow floor (0.032 → 0.027), and what pays for it is the shoulder pair NNE/ENE,
which the lower exponent brightens past the reference (0.028 → 0.035). On this one cell the mean is
a wash (0.18398 → 0.18738, +1.8 %); over the 28 thick rows it improves, and against G3's landing on
this cell it is 0.18738 against 0.30073.

### G3b.5 The check off the fitted rows

`g3b-check.py` on the checkerboard cells — the canonical checkerboard rows and the probe set's
coarse checkerboards over the three thick spans, none of them a row the pair was fitted on, at the
0.13.0 material and at the pair. **19 rows improve and 17 worsen, and every movement is small**: the
largest worsening is 0.27410 → 0.28657 (2x light `checkerboard-32__rrect-lg`, +4.5 %) and most are
under a percent. The check neither buys nor contradicts the fit, which is what a fit made on solids
should do over a backdrop where G0 measured the same reader correlating 0.85–0.96 with the lens.

### G3b.6 The fingerprints, and the two documents

| document | before G3b | after |
| --- | --- | --- |
| `apple-macos-26.5-1x-light-standard.json` | `290f52cb025fce7b` | **`9b7806cdefd1d1d6`** |
| `apple-macos-26.5-1x-dark-standard.json` | `64ef5c3002d15009` | **`eec7c2ea8dc89cae`** |

**The dark patch does not move** — both constants are the material's, named in the light patch and
inherited by the difference document — and `platform-web/src/dark-profile.ts` regenerates
byte-identical, verified by running `profile:dark` and diffing before the run.

### G3b.7 What the CSS tier takes now, and it is not nothing

Unlike G3's landing, the mirror moves. The field still integrates to zero around the contour and is
still not mirrored; but **`interiorBandLight` reads the EXPONENT**, and its arc integral runs
0.90741 of `2π` at 1.15 against **0.89686 at 0.85**, so the derived interior light falls by about a
percent of the band's own contribution. `test/interior-level.test.ts` records the third reading
beside the first two rather than rewriting either: `bandLightW22` is the unlit band, `bandLightW24`
the lit one at 1.15, `bandLightW25` the lit one at 0.85 — 0.995–0.997 of the second and 0.951–0.975
of the first on the three W16 probe cells. Tier coherence is re-read below.

### G3b.8 The stops

As before, with S11b re-read as an **ERROR** bound rather than a movement bound, per the ruling: the
thick solids' mean bin error at or under the 0.13.0 bed's on every row.

### G3b.9 How the bed is run, and what the earlier holdout read is worth

`g3-dryrun-run.sh` then `g3-holdout-run.sh`, at the constants above. **The holdout read recorded in
§7 belongs to a configuration that will not land** — the pair (1.15, 0.45) that S11b fired on — and
it is kept as the record of that run and not as a claim about this material. This section's is the
read for the landing.

---

## 7. What the run read

`g3-dryrun-run.sh` ran the calibration and validation columns of all six profiles on both tiers at
22:59–23:04, **twelve runs, all exit 0**. Every clause and every stop below was read on those rows;
one stop fired and is dispositioned to the parent rather than treated as a halt (S11's angular
half, §7.11). Then `g3-holdout-run.sh`, **once**, at 23:10–23:13, with nothing in the material, the
documents, the goldens or the code moved in between. 229 cells, 229 captures digested.

The evidence beside this file: `delta-e.txt` (clause 6's headline and clause 7's holdout),
`byte-identity.txt` (S6 and S10), `canonical-reads/` (W23's contour reader and W24's angular reader,
both beds, both tiers, before and after), `stops.txt` (S1, S2, S7, S11's straight spans),
`g3-stops.txt` (S11's angular family, S12, S13, S14), `g3-floors.txt` (the fourteen thick floors),
`g3-gate.txt` (the gate over the scratch matrix), `g3-digests.txt` (what G4 reproduces),
`goldens-attribution.txt`, and `sheets/g3-1x.png` and `sheets/g3-2x.png`.

### Clause 1 — the haze is measured before it is fitted: met at 1x, and at 2x the answer is that the two components are not separable

Re-declared by Decision Log 3 (a) as the TRIPLE — sharp σ, heavy σ, share — read by reader A on the
impulse rows and by readers B and C on the coarse checkerboards, with the residual beside.

**At 1x it is a reading on every thick cell the probe set carries.** Reader A on the reference:
`impulse__rrect-ml` 2.74 / 23.27 / 0.674 at residual 0.053 and `impulse__rrect-lg` 2.77 / 14.67 /
0.727 at 0.064, beside the canonical `impulse__rrect-md`'s 2.79 / 19.52 / 0.473 at 0.049. **The
sharp component is span-flat**: 2.53 at span 32, 2.62 on the collapsed capsule, 2.74–2.86 at spans
128 and 160 — 6 % across the whole sweep — and the unit it is flat in is DEVICE px.

**At 2x the triple is not identifiable above the knee, and that is the reading.** Reader A's
two-component fit degenerates: 11.80 / 12.03 with the share pinned at 1.000 on the 2x light
`impulse__rrect-ml` and 10.01 / 12.58 on the dark one, which is one Gaussian wearing two names. What
the 2x coarse checkerboards DO give — for the first time, and this is what G1's sitting bought — is
a single width inside both readers' validated bounds, because `checkerboard-64`'s pitch is 128
device px there: reader B reads native 7.09 / 8.42 / 8.98 against vitrea's 8.15 / 8.58 / 11.70 at
spans 96 / 128 / 160 in the dark scheme, and reader C 11.75 / 11.50 / 10.50 against 13.00 / 12.25 /
12.00. The σ-match's 16.00 ceiling and the edge-spread's unidentifiable residual are retired as
readings on these rows, which is clause 1's own ask.

### Clause 2 — the thick surface's body matches: NOT MET on all three halves, and each miss is a declined constant

| half | bound | reading | which constant |
| --- | --- | --- | --- |
| sharp σ within 15 % | 2.53–2.86 device px at 1x | vitrea 1.66–1.81 — **35–40 % low** | `blurSigma`, the thin capsule's own width; X5-entangled, not this wave's |
| share within 0.05 | 0.674 / 0.727 at spans 128 / 160 | vitrea 0.354 / 0.492 — **0.32 / 0.24 out** | `sizeScatterHeavyShareThick1x`, declined (§1.2) |
| level within 0.002 linear | — | worst thick untinted miss **0.011 linear** (1x light `checkerboard-32__rrect-md`, 0.68223 native against 0.69324) | `sizeToneLevelFar`, declined (§1.4) — and the term's own shape explains none of it |

The transmitted dot's FWHM is W24's reading and did not move: 4.99 CSS px against the reference's
7.57 at 1x. **The clause is missed and the wave's answer is that the rows say the misses are not the
constants the charter named.**

### Clause 3 — the nested base is Apple's: NOT MET, and untouched

`checkerboard__glass-over-glass__rest`'s base pane reads native 1.28 (reader B) / 1.50 (reader C) at
1x against vitrea's 1.73 / 2.10 — 35–40 % over, the same direction and size as every other thick
1x cell — and at 2x both readers are past their bound on that backdrop. Nothing in this wave moves
it: the base's haze is the heavy share's, and the heavy share is declined. The cell's own numbers
did move, and only in the direction the field can reach: its cross-tier coherence rose 0.03104 →
0.03108 and its GPU ΔE improved. **The eye's cell is still open, and the rows that would close it are
§1.5's.**

### Clause 4 — the size law's argument, and the four laws that ride it

Answered at G0 in the landed law's favour and not re-opened: nothing in this wave touches
`sizeSpanMin`, `sizeSpanMax`, `sizeScatterSpanMax` or the knee. The four riders are re-read rather
than re-fitted, through the renderer's own functions at the landed material and at all three W25
constants set to 1 (`g2/predict.mjs rides`): `lensDepthPx` 8.0 / 11.0 / 20.0, `sizeOcclusionAlpha`
0.4600 / 0.4625 / 0.4870, `sizeShadowDepth` 0.3500 and `backdropToneSizeBias` 0.0000 / 0.0046 /
0.0500 at spans 32 / 44 / 96 and above — **identical to the last digit printed in both columns at
every span of the bed.** The bed confirms it: the four `checkerboard__rrect-sm` and
`photo__rrect-sm` GPU captures at span 32 are BYTE-IDENTICAL to the 0.13.0 bed.

### Clause 5 — the collapse's key

Answered at G1 (Decision Log 5 (d)): the collapse keys on SPAN and not on canvas clearance, and the
large dark panel's "collapse" is the level law's floor arriving. Nothing in this gate re-opens it.
The sweep it was answered on is on both sheets, in span order, so the eye can see the reference's
level declining with span while vitrea's stays flat — the declined level term, in a picture.

### Clause 6 — the bed no worse anywhere: MET on every aggregate, with one instrument dissenting

`delta-e.txt`. **Every GPU calibration group improves or holds**, and not one group anywhere is
worse by as much as 0.00001:

| profile | GPU calibration | GPU validation | CSS calibration |
| --- | --- | --- | --- |
| 1x light | 0.00321 → **0.00321** | 0.00241 → 0.00240 | 0.00709 → 0.00709 |
| 2x light | 0.00326 → **0.00326** | 0.00248 → 0.00247 | 0.00738 → 0.00738 |
| 1x dark | 0.00393 → **0.00392** | 0.00244 → 0.00244 | 0.00633 → 0.00633 |
| 2x dark | 0.00395 → **0.00394** | 0.00297 → 0.00297 | 0.00657 → 0.00657 |
| 1x light reduced-transparency | 0.00171 → **0.00171** | 0.00110 → 0.00110 | 0.00447 → 0.00447 |
| 1x light increased-contrast | 0.00793 → 0.00793 | 0.00862 → 0.00862 | 0.01301 → 0.01301 |

Row by row (S1) the worst ΔE rise anywhere is **+0.00001** against a bound of 0.001 and the worst
`ssimMean` fall is **−0.00012** against 0.005; no row fires. The thin half (S12) reads **+0.000002**
worst over 114 thin cells against 0.001. W23's straight-span contour reads move by at most
**0.00273** against 0.005 and none fires. **W24's angular reads are the dissent and they are §7.11.**

**The fourteen thick floors, re-read** (`g3-floors.txt`): **0 breached**, and none of them moved.
Thirteen of the fourteen are `dom`-tier rows, which this wave's one constant cannot reach at all, so
they read to five decimals exactly what the 0.13.0 bed read; the fourteenth, `texture / holdout /
checkerboard__glass-over-glass__rest / 2x dark :: silhouetteIoU`, moves 0.92707 → 0.92708, toward
its bound. **No floor is re-pinned by this gate.** The wave expected them to move because it expected
the share and the level to land; with those declined, they stand.

### Clause 7 — the holdout, read once

| profile | tier | before | after |
| --- | --- | --- | --- |
| 1x light | webgpu | 0.00898 | **0.00897** |
| 2x light | webgpu | 0.00895 | **0.00894** |
| 1x dark | webgpu | 0.01325 | **0.01324** |
| 2x dark | webgpu | 0.01311 | **0.01310** |
| 1x light reduced-transparency | webgpu | 0.00343 | **0.00342** |
| 1x light increased-contrast | webgpu | 0.02042 | 0.02042 |
| 1x light | css | 0.01576 | 0.01576 |
| 2x light | css | 0.01617 | 0.01617 |
| 1x dark | css | 0.01735 | 0.01735 |
| 2x dark | css | 0.01739 | 0.01739 |
| 1x light reduced-transparency | css | 0.00751 | 0.00751 |
| 1x light increased-contrast | css | 0.04561 | 0.04561 |

**Every GPU holdout group improves or holds and every CSS holdout group is unchanged.** Nothing
anywhere is worse. This is the wave's one holdout read (X3), taken on the constant of §1 and on
nothing else; **a ruling that moves that constant voids it and needs another.**

### Clause 8 — what the CSS tier took: exactly nothing, exactly as declared

The prediction in §5 was a byte-identity claim and the bed tests it: **84 of the 85 CSS captures are
byte-identical to the 0.13.0 bed**, and so are their alpha channels. The one mover is
`apple-macos-26.5-1x-light-increased-contrast / photo__toolbar-group__rest`, measured rather than
assumed: **17 pixels of 64 000, every one by exactly 1 code, alpha untouched**, confined to a
16 × 50 px box on the third member's edge, with the cell's ΔE unchanged to five decimals and its
GPU sibling byte-identical. No constant the mirror reads moved, so it is the browser's own raster of
a `backdrop-filter` over a photo and not this wave — recorded, not explained further.

`blur()` runs at the unchanged shared σ. `interiorBandLight` returns the same number, which is why
the tier holds. The coherence pin is re-read on all 114 cells that carry one: **worst 0.03268**
against ≤ 0.05 (2x light `checkerboard__glass-over-glass`), the 31 checkerboard cells running
0.00273 … 0.03268, and the worst movement anywhere **+0.000043**. The large-span interior spread is
untouched and stays Decision Log 23 (a)'s recorded residual.

### Clause 9 — by eye, and the ledger

`sheets/g3-1x.png` and `sheets/g3-2x.png`, 37 rows each: native | GPU before (0.13.0) | GPU landed |
CSS landed, over the thick rrects on `dark-solid`, `light-solid`, `checkerboard` and `photo`, the
nested pane with its base cropped, the impulse rrect with its centre dot at 4×, the `dark-solid`
span sweep 32 → 160 in both schemes from the probe set, and the RIM'S CORNERS at 4× per CSS px on
three thick panels — TL | BR | TR | BL in one strip, because the field is +1 at the first pair and
−1 at the second and a sheet showing one corner shows nothing. **The user's veto stands over all of
it (X6, S8), and §7.11 is what the eye is being asked to rule on.**

### 7.11 The stops

| stop | reading | verdict |
| --- | --- | --- |
| **S1** untinted row ΔE +0.001 / ssim −0.005 | worst +0.00001 / −0.00012 | **clear** |
| **S2** tinted body 0.002 | worst 0.00001 | **clear** |
| **S3** calibration ΔE mean +0.0001 | every group improves or holds | **clear** |
| **S4** a golden moved for another reason | 0 pixels outside any contour band on any of the thirteen scenes | **clear** |
| **S5** a constant whose rows do not separate it | one constant landed on 64 sides at two scales in two schemes; three declined on measurement | **clear** |
| **S6** a CSS capture moved without an explanation | 84 of 85 byte-identical; the one mover measured at 17 px × 1 code, alpha untouched, ΔE unchanged | **clear** |
| **S7** collapsed body 0.002 | worst 0.00000 | **clear** |
| **S8** the user's eye | `sheets/g3-1x.png`, `g3-2x.png` | the user's |
| **S10** a cell the field cannot reach that moves | 74 of 85 GPU captures moved; the 11 that did not are the 7 increased-contrast cells where `border: "strong"` folds the slope to 0 and the 4 `rrect-sm` cells at span 32 where `sizeThickness` is 0 | **clear** |
| **S11a** straight spans, 0.005 | GPU and CSS worst **0.00273** | **clear** |
| **S11b** W24's angular bins, 0.005 | worst **0.10895**, 56 bins over the bound on 28 rows | **FIRES** |
| **S12** a thin cell moved by 0.001 ΔE | worst **+0.000002** over 114 thin cells | **clear** |
| **S13** a golden moved outside a thick surface's body or rim | **0** on every scene | **clear** |
| **S14** a probe row worse by 0.002 ΔE | worst **+0.000056** over 205 probe cells | **clear** |

**S11b's firing, and it is the wave's open question rather than a technicality.**

Read as declared — a movement bound — S11b fires by construction: the field grades the rim's
amplitude by POSITION, and on a rounded rectangle a bin of the normal's DIRECTION is a position, so
the bins move because the mechanism draws. That reading alone would be a mis-specified stop. What
matters is whether the bins moved TOWARD the reference, so the ERROR is read beside the movement,
per row, in `g3-stops.txt`:

```
rows whose mean bin error IMPROVED: 5    worsened: 9
```

and the five that improved are the thin capsules the field barely reaches, while the nine that
worsened are the thick solids it is for. On the wave's own named cell, 1x light
`dark-solid__rrect-md`, the mean bin error goes 0.03481 → 0.05689 and the worst bin 0.06571 →
0.14870.

**The diagnosis is in the per-bin table and it is a confound, not a defect in either constant.**

| bin | reference | before | after | error before | error after |
| --- | --- | --- | --- | --- | --- |
| NW (the top-left corner) | 0.12223 | 0.14220 | 0.20344 | 0.01997 | **0.08121** |
| SE (the bottom-right) | 0.12739 | 0.14384 | 0.20347 | 0.01645 | **0.07608** |
| NNE (between the axis and the null) | 0.03598 | 0.06435 | 0.03902 | 0.02837 | **0.00304** |
| ENE | 0.03815 | 0.06440 | 0.04129 | 0.02625 | **0.00314** |
| NE (the null) | 0.03661 | 0.00439 | −0.00078 | 0.03221 | 0.03739 |
| N (a straight side) | 0.18882 | 0.20906 | 0.21205 | 0.02023 | 0.02322 |

**W24's lit edge and W25's field peak on the SAME diagonal.** The exponent is `(√2·|n · L|)^p` with
`L` the exact top-left/bottom-right diagonal, maximal at NW and SE; the field is `+1` at exactly
those two corners. W24 fitted the exponent with the position term ABSENT, so on the corner arcs —
where the two are confounded and where G0's along-side reader does not look, because it walks only
the straight part of a side — the exponent absorbed part of the position grading. Adding the
position term now double-counts there. The signature is unmistakable and it is also the proof that
the field is aimed correctly: the bins that RISE are NW and SE, the bins that FALL are the ones
straddling NE and SW, and the straight sides move by 0.003.

The arithmetic says no smaller slope rescues it on this cell: the peak bins' error grows at about
0.136 per unit slope where the near-null bins' shrinks at 0.056, so the mean bin error is worst at
every positive slope and the break-even is below zero. **What the rows ask for is a JOINT re-fit of
`rimLitExponent` with `rimAlongSideSlope` on W24's 285-bin row set together with this wave's 64
sides** — one bounded piece of work, on fixtures that already exist, which is named in the tracker
and in the wave's Deferred list.

**This gate does not rule it.** The dry run's job is to declare, run and read; the landing is G4's
and the user's (X6). What the parent has to weigh is on both sides of one line: every aggregate the
bed measures improves or holds (ΔE on all eighteen groups, SSIM, the straight spans, the goldens'
attribution, the probe set, the floors, the holdout), the corner-to-corner range on the solids goes
from 0.227 to 0.743 of the reference's, and one instrument — the finest one the rim has — says the
diagonal is now over-graded on the thick solids because two mechanisms grade it.

### The gate over the scratch matrix

`g3-gate.txt`, `VITREA_MATRIX_PATH` pointed at the dry run: **2 of 37 cases fail, and both are the
conditioning predicate moving**, which is what CLAUDE.md says a fidelity change does.
`PREDICATE_EXCLUDES` reads **33** where the file names 31: three cells enter —
`texture / calibration / checkerboard__rrect-ml__rest / 2x light`,
`texture / holdout / checkerboard__glass-over-glass__rest / 2x light` and
`texture / holdout / checkerboard__rrect-lg__rest / 2x light` — and one leaves,
`texture / calibration / checkerboard__toolbar-group__rest / 2x light`. The coverage count that
follows from it moves 31 → 29 on `texture / silhouetteIoU`. **Re-deriving that file is G4's**, by the
wave's own charter. **No regression floor is breached and none is re-pinned by this gate.**

### The ladder the fits were made on

Five probe-set renders, each to its own scratch directory through `g3-probe-run.sh` (both tiers) or
`g3-ladder.sh` (the GPU tier alone, since none of the three constants reaches the other), read by
`g3-read.py` with G0's instruments and fitted by `g3-fit.py`. The canonical `results/matrix.json`,
`web-captures/`, `apps/reference-apple/fixtures/` and `scenes.json` were never written (X2), and the
GPU ran one capture process at a time throughout (X4).

| rung | material | what it measured | table |
| --- | --- | --- | --- |
| `r0` | the inert defaults | the baseline: 470 width rows, 382 level rows, 384 side rows, native and web, four profiles | `read-r0.json` |
| `rS` | lift1x 0.45, lift2x 0.50 | the share's lever and the 2x floor's saturation | `g3-fit-share.txt`, `g3-moved-rS.txt` |
| `rS2` | lift1x 0.18 | the share's cost curve, which is concave — five probe rows already past 0.002 ΔE | `g3-moved-rS2.txt` |
| `rV` | `sizeToneLevelFar` +0.05 light, −0.05 dark | the level term's lever and its 32 zero-lever controls | `g3-fit-level.txt`, `g3-fit-level-all-backdrops.txt` |
| `rW` | `rimAlongSideSlope` 0.45 | the field's lever, and the landed material's own probe reading | `g3-fit-field.txt`, `g3-moved-rW.txt`, `read-rW.json` |

`rW` is the material this document declares, so its probe matrix is what S14 is read against and its
captures are what the sheets' sweep rows show.

### The digests

`g3-digests.txt`: both profile documents' file digests
(`9ccecbd4025de666…` light, `157748e05df352d2…` dark) and resolved fingerprints, the full resolved
patch of each, and the sha256 of every one of the **229 captures** at the frozen configuration, none
missing. G4 reproduces them from the main checkout.


---

## 8. What the G3b run read

`g3-dryrun-run.sh` ran the calibration and validation columns of all six profiles on both tiers at
00:44–00:48, twelve runs, all exit 0, **and not one cell went unmeasured**. Every clause and every
stop below was read on those rows; then `g3-holdout-run.sh`, once, at 00:53–00:56, with nothing in
the material, the documents, the goldens or the code moved in between. 229 cells, 229 captures
digested.

**One bookkeeping note, because it is the kind of thing that silently corrupts a gate.** This child
ran the canonical bed twice — once at (0.70, 0.15) and once, after that pair was found to drop two
calibration cells, at (0.85, 0.10) — into the same `--out-matrix`. A cell's key carries the material
document's sha256, so `compare` APPENDED rather than replaced and the matrix held every cell twice;
the gate read 397 cells and failed 25 of 37 cases for that reason alone. `g3b-reduce.py` reduces it
to the rows whose capture path names the documents **on disk now** — a claim about the material
rather than about ordering — leaving 229 distinct cells and none duplicated. Every table below is
read from `g3-dryrun-landed.json`, the reduced matrix. The captures themselves were never ambiguous:
they are written per profile and scene and the second run overwrote the first.

The evidence beside this file: `g3b-delta-e.txt`, `g3b-byte-identity.txt`, `g3b-stops.txt`,
`g3b-stops2.txt`, `g3b-floors.txt`, `g3b-gate.txt`, `g3b-digests.txt`, `g3b-goldens-attribution.txt`,
`g3b-fit.txt`, `g3b-bins.txt`, `g3b-check.txt`, `canonical-reads/` and the two sheets.

### Clause 6 — the bed no worse anywhere: MET, and every group holds to five decimals

Not one of the twenty-four calibration and validation groups moves by as much as 0.00001 except one
CSS validation group at +0.00001 (`increased-contrast`). Row by row (S1) the worst ΔE rise anywhere
is **+0.00003** against 0.001 and the worst `ssimMean` fall **−0.00006** against 0.005; no row fires.
W23's straight spans move at most **0.00276** against 0.005. **The fourteen thick floors: 0
breached, none re-pinned**, and none moved — thirteen are `dom`-tier rows whose readings are set by
the band's level rather than the rim's shape, and the fourteenth holds at 0.92707.

### Clause 7 — the holdout, read once on THIS configuration

| profile | tier | before | after |
| --- | --- | --- | --- |
| 1x light | webgpu | 0.00898 | 0.00898 |
| 2x light | webgpu | 0.00895 | 0.00895 |
| 1x dark | webgpu | 0.01325 | 0.01325 |
| 2x dark | webgpu | 0.01311 | 0.01311 |
| 1x light reduced-transparency | webgpu | 0.00343 | 0.00343 |
| 1x light increased-contrast | webgpu | 0.02042 | 0.02042 |
| 1x light | css | 0.01576 | 0.01576 |
| 2x light | css | 0.01617 | 0.01616 |
| 1x dark | css | 0.01735 | 0.01735 |
| 2x dark | css | 0.01739 | 0.01739 |
| 1x light reduced-transparency | css | 0.00751 | 0.00751 |
| 1x light increased-contrast | css | 0.04561 | 0.04561 |

**Every group holds and one improves.** Nothing anywhere is worse. **The §7 holdout read belongs to
the (1.15, 0.45) configuration, which does not land; this one is the landing's.**

### Clause 8 — the CSS tier, which this time does move

`g3b-byte-identity.txt`: **33 of 85 CSS renders moved and 52 held**, and the movers are the cells
whose band the arc integral reaches; the ALPHA channel moved on one capture only, the same
increased-contrast `photo__toolbar-group` noise cell §7 measured at 17 pixels by one code. On the
GPU tier 78 of 85 moved and the 7 that held are exactly the increased-contrast cells where
`border: "strong"` folds both constants to 0 — a smaller set than G3's 11, because the exponent
rides no size law and so reaches the `rrect-sm` cells at span 32 that the field could not. The
coherence pin is re-read and nothing approaches its ≤ 0.05.

### The stops

| stop | reading | verdict |
| --- | --- | --- |
| **S1** untinted row ΔE / ssim | worst +0.00003 / −0.00006 | **clear** |
| **S2** tinted body 0.002 | worst 0.00006 | **clear** |
| **S3** calibration ΔE mean +0.0001 | every group holds | **clear** |
| **S4** a golden moved for another reason | 0 pixels outside any contour band on any of the thirteen scenes | **clear** |
| **S5** a constant whose rows do not separate it | the pair is a joint minimum over 46 rendered points on 54 + 58 rows | **clear** |
| **S6** a CSS capture moved without an explanation | 33 renders moved and the explanation is derived: `interiorBandLight`'s arc integral 0.90741 → 0.89686 of `2π`. One alpha moved, and it is the same raster-noise cell as before | **clear** |
| **S7** collapsed body 0.002 | worst 0.00000 | **clear** |
| **S8** the user's eye | `sheets/g3-1x.png`, `g3-2x.png` — now native \| before \| G3's pair \| G3b's pair \| CSS | the user's |
| **S10** a cell the pair cannot reach that moves | 7 GPU captures held, all of them cells where `border: "strong"` folds both constants to 0 | **clear** |
| **S11a** straight spans, 0.005 | worst **0.00276** | **clear** |
| **S11b** the thick solids' mean bin error at or under the 0.13.0 bed's, ON EVERY ROW | 5 of the canonical bed's 8 thick solid GPU rows improve; 3 worsen, worst **+0.00064** on 1x light `dark-solid__rrect-md` (0.03481 → 0.03545, +1.8 %) | **fires on 3 rows, dispositioned** |
| **S12** a thin cell moved by 0.001 ΔE | worst **+0.000009** | **clear** |
| **S13** a golden moved outside a thick surface's body or rim | **0** on every scene | **clear** |
| **S14** a probe row worse by 0.002 ΔE | worst **+0.000009** over 203 probe cells | **clear** |

**S11b's residual firing, and why it is not the same object as G3's.** Under G3's pair the same stop
fired on 26 of 28 thick rows and took the named cell's mean bin error up by 63 %; under the joint
pair it fires on 3 rows of 8 on the canonical bed and 12 of 28 over the whole fitted set, with the
worst single row worsening by 1.8 % and the aggregate improving 0.17527 → 0.17208. The three that
worsen are all `dark-solid__rrect-md` — the cell whose reference rim is BRIGHTEST on its straight
sides and dimmest on its diagonals, which is the one shape a factor that grades toward the diagonal
cannot improve. What remains is not a confound any more; it is the rim's own AMPLITUDE at the arcs,
which is W23's law and is on the tracker as the wave's largest remaining rim gap.

### The gate over the scratch matrix

`g3b-gate.txt`, `VITREA_MATRIX_PATH` pointed at the reduced dry run: **37 of 37 pass.** The
conditioning predicate does NOT move — `PREDICATE_EXCLUDES` reads exactly the 31 the file names,
where G3's pair moved it to 33 — so unlike the earlier landing this one leaves
`adopted-thresholds.test.ts` untouched and G4 has no re-derivation to do. No floor is breached and
none is re-pinned.

### The digests

`g3b-digests.txt`: both documents' file digests (`602b9fc63cec…` light, `d9be6210c9b5…` dark) and
resolved fingerprints, the full resolved patch of each, and the sha256 of every one of the **229
captures** at the frozen configuration, none missing. G4 reproduces them from the main checkout.

### By eye

`sheets/g3-1x.png` and `g3-2x.png`, 37 rows each, now **five panels**: native | GPU at the 0.13.0
bed | GPU at the pair W25 G3 declared | GPU at the pair W25 G3b declares | CSS. The corner strips on
the three thick panels are the row to read — TL | BR | TR | BL at 4× per CSS px — because that is
where the two constants meet. **The user's veto stands over all of it (X6, S8).**
