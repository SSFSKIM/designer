# W17 G1 — the dry run of the interior level's conversion (branch `w17-g1-level`)

The charter's G1 child, run under W17 Decision Log 2's form and Decision Log 3's re-declaration of
S3 and S5. Nothing canonical was written: every capture and every matrix below lives under
`/Users/new/.claude/jobs/5c70e47f/tmp/w17/g1/`, and the canonical `results/matrix.json` and
`web-captures/` of the main checkout were read and never touched.

## 0. What was captured, and how the two configurations differ

Two **builds** of this branch, each captured over the whole bed — the six standard profiles'
calibration and validation sets, the GPU tier first so the cross-tier coherence rows compute:

| tag | what the tier draws | matrix |
| --- | --- | --- |
| `cfg1` | Decision Log 2 (b) alone: the size law's occlusion and the regime's lift before the W9 response solve, the inner shadow as the shader's layer pair, and the tint still on L3 as an `rgba()` overlay at the one-alpha conversion | `matrix-cfg1.json` |
| `cfg2` | the full form: (b) plus the tint's lerp inside the sharp layer's linear-light filter as a per-channel `feComponentTransfer type="linear"`, L3 without a tint | `matrix-cfg2.json` |

Configuration 1 is a one-line local edit that stands the transfer down (`css-tier.ts`'s `transfer`
forced `undefined`), built, captured and reverted; it is not on the branch. The scripts are
`run-dry.sh` (one profile, one tier, one set), `launch-dry.sh` (the order the evidence needs) and
`verify-dry.py` (the referee). `probe-tables.md` and `run-probe.sh` are the pre-check that opened
step 2; `residuals.ts` derives the two residuals Decision Log 2 (c) names.

**The division of labour with the landing's own gate.** Contract X6 says the landing's test file
runs against the dry run's matrix, and since this branch it can: `adopted-thresholds.test.ts` reads
`VITREA_MATRIX_PATH`. So S2's bounds and floors and S7's conditioning predicate are **that file's
verdict**, run here against each scratch matrix, and `verify-dry.py` owns what the test file cannot
see — the GPU tier's byte identity, and the four stops that compare two runs or the two tiers.

## 1. Configuration 1 — the ordering fix alone is a real correction and not a landing

`cfg1.verify.txt`. S1 met: **85 GPU captures byte-identical to the W16 bed, none differing**, worst
GPU row |Δ| **0.000000**. Every other stop fires, and the pattern is the point.

- **S4** fires on every light-standard checkerboard, `hc-text` and `photo` cell: the level closes
  from the bed's +0.027…+0.064 to **+0.0135…+0.0455** against the GPU tier, which is 0.010 to 0.018
  of gap closed and still four times the clause.
- **S3** fires on three spans against the GPU tier's own spread (`rrect-sm` −0.0113 at 1x and
  −0.0063 at 2x, `rrect-ml` −0.0162 at 2x), and the as-written reading against native gets *worse*
  at 2x than the bed's: `rrect-md` −0.0161 and `rrect-ml` −0.0187 against a ±0.015 band the bed sat
  inside at −0.0121 and −0.0156.
- **S5** fires on the solids in both directions — `light-solid__rrect-md` +0.0168 over the GPU tier,
  `impulse__rrect-md` −0.0434 under it, `dark-solid__rrect-md` −0.0162 under it at 1x-light and
  −0.0795 / −0.1155 in the dark scheme — and `dark-solid__rrect-md`'s cross-tier ΔE rises by
  +0.0016 at both light scales.
- **S6** fires on 24 rows: the level ratio is 0.939–0.980 on the light cells, outside 0.97–1.03.
- **S7** fires: `checkerboard__capsule-button__rest` under reduced transparency still reads
  `areaWeb / componentRegion` **0.8383** with **2 bodies**, so it does not condition.
- The landing's gate on this matrix reports one **new** predicate exclusion,
  `dom / calibration / checkerboard__rrect-md__rest / apple-macos-26.5-1x-light-reduced-transparency`
  — a cell that conditioned on the W16 bed and does not under the ordering fix alone.

The ordering fix moves the tier toward the renderer everywhere and lands it nowhere. That is the
reading Decision Log 2 (b) asked for: it is a defect worth fixing in its own right, and it is not
this wave's mechanism.

## 2. Configuration 2 — the level lands, and two carriers of the form do not

`cfg2-calval.verify.txt`, `dry-tables.md`. S1 met again: **85 GPU captures byte-identical, worst
GPU row |Δ| 0.000000** under both builds, so contract X3 held across four whole-bed runs.

**S4 is met on every light-standard checkerboard, `hc-text` and `photo` cell except the two
`toolbar-group` cells.** The level against the GPU tier, 1x then 2x:

| cell | bed CSS−GPU | cfg1 | cfg2 |
| --- | --- | --- | --- |
| `checkerboard__rrect-sm` | +0.0237 / +0.0158 | +0.0165 / +0.0157 | **+0.0002 / −0.0003** |
| `checkerboard__capsule-button` | +0.0269 / +0.0310 | +0.0218 / +0.0258 | **−0.0055 / +0.0001** |
| `checkerboard__rrect-md` | +0.0473 / +0.0578 | +0.0371 / +0.0397 | **−0.0061 / −0.0005** |
| `checkerboard__rrect-ml` | +0.0500 / +0.0638 | +0.0378 / +0.0455 | **−0.0064 / −0.0011** |
| `checkerboard__toolbar-group` | +0.0186 / +0.0241 | +0.0135 / +0.0190 | **−0.0209 / −0.0107** |
| `photo__rrect-md` | +0.0562 / +0.0517 | +0.0373 / +0.0413 | **−0.0066 / −0.0037** |
| `photo__rrect-ml` | +0.0572 / +0.0550 | +0.0384 / +0.0442 | **−0.0067 / −0.0032** |
| `photo__toolbar-group` | +0.0467 / +0.0475 | +0.0322 / +0.0369 | **−0.0237 / −0.0156** |

`ssimMean` rises on every checkerboard cell (+0.0019 to +0.0165 at 1x) and `ssimBand` rises on
most; the cross-tier ΔE falls on both light-standard profiles. The level ratio lands inside
0.97–1.03 on every light cell **except** the two `toolbar-group` cells at 1x (1.0319, 1.0386).

### 2.1 The `toolbar-group` deficit is the body's filter region, not the conversion

The `toolbar-group` scenes are **three separate 46 × 46 capsules**, and the deficit is a uniform
interior offset — measured per annulus on the 1x checkerboard cell, the core reads −0.0087 to
−0.0180 and the mid-ring −0.0136 to −0.0229 below the GPU tier while the contour band reads
+0.0339 to +0.0649 above it. A uniform body offset with a bright band is not a tint error.

It is the reference filter's **region**. `createCssTierFilterDefs` writes `x=-50% y=-50%
width=200% height=200%`, which on a 46 CSS px box is ±23 px, and the heavy step at dpr 1 is
σ = 13.69 CSS px, whose 3σ reach is **41.1 px**. The kernel is clipped and the layer reads dark.
The arithmetic says exactly which cells are affected and the bed agrees:

| surface | dpr | heavy step σ | 3σ | region half-extent | clipped |
| --- | --- | --- | --- | --- | --- |
| 46 × 46 (`toolbar-group`) | 1 | 13.69 | 41.1 | ±23 / ±23 | **yes, both axes** |
| 122 × 46 (`capsule-button`) | 1 | 13.69 | 41.1 | ±61 / ±23 | yes, one axis |
| 162 × 98 (`rrect-md`) | 1 | 13.69 | 41.1 | ±81 / ±49 | no |
| any of the three | 2 | 4.36 | 13.1 | ≥ ±23 | no |

which is why the `toolbar-group` cells are the worst at 1x and roughly half as bad at 2x, why the
lone capsule is only −0.0055, why `rrect-md` and `rrect-ml` land inside 0.007 — and why
`photo__toolbar-group__rest` under reduced transparency, where the frost is 1.75× wider still,
reads **−0.0495** from the GPU tier. This is a **W16 defect the `rgba()` overlay was masking**: the
overlay's own conversion was fitted against the cross-tier difference and absorbed part of the
clipping, and an exact conversion cannot.

### 2.2 The near-black composite truncates in the filter's 8-bit linear intermediate

`impulse__capsule-button__rest` is the one cell where the tier now draws **black**. Its material
has collapsed onto the impulse background's own tone, so the renderer draws a flat 0.0037 in linear
light — 12/255 encoded — and the transfer's intercept is that same 0.0037. The tier's capture reads
**0**, at both scales, and the cost is `ssimMean` 0.9756 → 0.9060 at 1x and 0.9759 → **0.9155** at
2x, below that profile's 0.92 bound, with `ssimBand` −0.375 / −0.216. The recorded level ratio
becomes undefined, which the landing's gate reports as its own failure.

The mechanism is the carrier's, and it is arithmetic rather than a guess: the composite is carried
through `color-interpolation-filters="linearRGB"`, whose intermediate is eight bits **in linear
light**, so its quantum is 1/255 = 0.0039 — larger than the whole composite on a near-black cell,
and 0.0037 truncates to zero. The `rgba()` overlay never met this because it composites in the
ENCODED space, where 0.0037 linear is a comfortable 12/255. Every other cell of the bed is far
enough from black for the quantum to be irrelevant; `impulse__rrect-md__rest`, over the same
background, lands at 0.4623 against the GPU tier's 0.4660.

### 2.3 The solids, the tinted cells and the dark scheme (S5 as re-declared)

The **light solids land on the renderer**: `light-solid__rrect-md` +0.0001 / +0.0000,
`light-solid__rrect-ml` −0.0008 / +0.0000, `light-solid__capsule-button` +0.0012 / +0.0016, from a
bed that sat +0.017 over. `dark-solid__rrect-md` in the light profiles lands −0.0019 / −0.0018.

The **author-tinted cells behave exactly as the fold's algebra predicts.** Every tinted scene in
the bed except one carries a seed at full strength, and at `s` = 1 the author's layer is opaque and
`(1 − s)` of the untinted change is zero: the measurements are −0.0017 to +0.0000 on those cells.
The single half-strength cell, `photo__capsule-button__rest-tint-orange-half`, is the one that
moves, and it lands within 0.01 of the GPU tier under configuration 2 where configuration 1 left it
+0.0188 / +0.0157 away.

The **dark-scheme cells move by more than the 0.005 clause**: `checkerboard__capsule-button`
+0.0217 / +0.0204, `checkerboard__rrect-md` +0.0125 / +0.0118, `photo__capsule-button` +0.0127 /
+0.0118, `photo__rrect-md` +0.0057 / +0.0054 — all upward, all toward the GPU tier they were below.
`dark-solid__rrect-md` in the dark scheme stays **−0.0758 / −0.1138 under the GPU tier**, which is
the renderer's own dark-ground dot that Decision Log 2 (e) rules out of this tier's account: the
tier is nearer native there, and the re-declared S5 reads it as a miss because it reads the
renderer.

### 2.4 The conditioning predicate, and the two stops it moves

The landing's gate against the configuration 2 matrix (contract X6, `cfg2.gate.txt`) reports the
predicate's exclusion list moving by three cells, in both directions:

- **`dom / calibration / checkerboard__capsule-button__rest / 1x-light-reduced-transparency`
  leaves it** — S7's first cell conditions again (`areaWeb / componentRegion` and one body), which
  is the shape-axis loss W16 recorded and this wave set out to recover.
- **`dom / calibration / light-solid__rrect-ml__rest` at both light-standard scales joins it.**
  Landing that surface on the renderer's level puts it at 0.9315 / 0.9322 over a background at
  0.9347 / 0.9337, and the silhouette extractor's luminance-delta can no longer separate the two.
  The GPU tier conditions on the same cell at 0.9323 / 0.9322, so this is a threshold the CSS tier
  crosses and the renderer does not.

S7's second cell, `hc-text__capsule-button__rest` under reduced transparency, is a **holdout** cell
and is not read here — see §3.

### 2.5 The tier's contrast floor no longer survives a filter that does not render

The doctrine at the top of `css-tier.ts` is S1's undetectable failure class made into a rule: **the
surface always paints a real tint and a real border, and never relies on the blur for contrast**,
because no probe can catch "the engine reports support and renders nothing", so a missed demotion
has to be a fidelity loss rather than a broken UI. `e2e/pixel/css-tier-pixels.spec.ts`'s "stays
legible with the blur removed" simulates exactly that by taking `backdrop-filter` off both created
layers and measuring the surface against the bare page beneath it.

With the tint inside the filter, taking the filter away takes the tint with it: the three sampled
interior points read a channel delta of **0, 0, 0** against a floor of 8. The rim survives — it is
an inset `box-shadow` on L3 — and the body does not. Four more Chromium pixel specs fail beside it,
three of which recompute the tier's own law and need re-pointing for the ordering fix
(`backdrop-tone-pixels` at 202 and 236, `tint-pixels` at 132, where the tint colour is now 254
rather than 255 because the inner shadow scales the pair), and one of which is a level assertion on
a near-black backdrop that moved by 6.3 codes — §2.2's truncation, seen from the other side.

The three law-recomputing pins are ordinary re-pointing work and were deliberately **not** done
here, because they would be work on a form the two findings above may change. The contrast-floor
failure is not re-pointing work: it is the doctrine, and the form has to answer it.

## 3. The holdout was NOT read, and why

Contract X8 reads the holdout **once per frozen configuration**. Configuration 2 is not frozen:
§2.1, §2.2 and §2.5 are three mechanisms that fire stops, and each has a named, plausible fix that
would change what the tier draws (the filter region's extent; the carrier's behaviour near black;
whether L3 keeps a floor of tint under the filter's own). A
holdout read taken now would either be spent on a configuration the wave then revises, or would
have to be repeated — which is the exact expenditure X8 exists to prevent. The read is therefore
left for the parent to authorise once the configuration is settled, and every holdout row above is
marked "not read" rather than estimated.

## 3b. Configuration 3 — the re-form, whole bed

`cfg3-calval.verify.txt`, `cfg3.gate.txt`, `dry-tables.md`, `cost/cost-table.md`,
`toolbar-residual.md`. Decision Log 4's (a) and (c) with Decision Log 5's floor; (b) withdrawn
and its sweep kept as `region-sweep.md`.

**S1 met.** 85 GPU captures byte-identical to the W16 bed, worst GPU row |Δ| **0.000000** — the
sixth whole-bed run in a row where contract X3 holds exactly.

**S4 met on every light cell except the two `toolbar-group` scenes**, which are the named carry:

| cell | dpr | form | bed CSS−GPU | cfg3 CSS−GPU |
| --- | --- | --- | --- | --- |
| `checkerboard__rrect-sm` | 1x / 2x | linear | +0.0237 / +0.0158 | **+0.0032 / +0.0078** |
| `checkerboard__capsule-button` | 1x / 2x | linear | +0.0269 / +0.0310 | **−0.0005 / +0.0095** |
| `checkerboard__rrect-md` | 1x / 2x | linear | +0.0473 / +0.0578 | **+0.0010 / +0.0034** |
| `checkerboard__rrect-ml` | 1x / 2x | linear | +0.0500 / +0.0638 | **−0.0003 / +0.0039** |
| `checkerboard__toolbar-group` | 1x / 2x | linear | +0.0186 / +0.0241 | −0.0122 / −0.0040 |
| `photo__rrect-md` | 1x | linear | +0.0562 | **−0.0048** |
| `photo__rrect-ml` | 1x | linear | +0.0572 | **−0.0051** |
| `photo__toolbar-group` | 1x / 2x | linear | +0.0467 / +0.0475 | −0.0150 / −0.0101 |
| `light-solid__rrect-md` | 1x | linear | +0.0254 | **+0.0007** |
| `dark-solid__rrect-md` | 1x / 2x | linear | +0.0014 / +0.0003 | **+0.0045 / +0.0046** |
| `impulse__capsule-button` | 1x / 2x | **encoded** | +0.0000 | **−0.0000** |
| `dark-solid__rrect-md` (dark) | 1x / 2x | **encoded** | −0.0795 / −0.1155 | −0.0795 / −0.1155 |

`ssimMean` rises on every light checkerboard row (+0.0019 to +0.0165 at 1x) and no held floor's
row falls below its pin. `ssimBand` rises on the 1x checkerboards by +0.0191 to +0.0590.

**S3, one-sided (Decision Log 4 (d)): one cell.** `checkerboard__rrect-ml` at 2x is 0.0081 from
native where the renderer is 0.0025 — farther by **+0.0055**, over the 0.005 clause by 0.0005.
Every other calibration span is inside. The as-written reading against native fires on one cell
too, `checkerboard__rrect-md` at 1x, −0.0117 against a ±0.01 band with the renderer at −0.0080;
both readings are printed on every row.

**S5, against the renderer.** Every solid and tinted cell lands within 0.01 of the GPU tier. The
half-strength tinted cell, `photo__capsule-button__rest-tint-orange-half`, moves −0.0237 against a
prediction of `(1 − s)` of its untinted base's change and lands **−0.0011** from the GPU tier; the
full-strength tinted cells move by ≤ 0.0023, as `(1 − s) = 0` requires. Three small rises fire it:
`dark-solid__rrect-md`'s cross-tier ΔE by +0.0006 / +0.0007 at the two light scales, the
half-strength tinted cell's by +0.0010, and `dark-solid__rrect-md` in the DARK scheme reading
−0.0795 / −0.1155 from the GPU tier — that last cell **did not move at all** (0.1310 → 0.1310), it
takes the encoded form, and the distance is the renderer's own dark-ground dot that Decision Log 2
(e) rules out of this tier's account.

**S6.** Cross-tier ΔE falls on both light-standard profiles (0.00721 → 0.00607, 0.00749 →
0.00633) and on reduced transparency (0.00419 → 0.00389), is unchanged on both dark profiles
(0.00406, 0.00414 — the encoded form), and **rises by +0.00012 on increased contrast** (0.00657 →
0.00669), which fires the clause. The worst light-cell level ratio is **1.0241** on
`photo__toolbar-group`, inside 0.97–1.03.

**S7 met on its first cell.** `checkerboard__capsule-button__rest` under reduced transparency reads
`areaWeb / componentRegion` **0.9961** with **one body** and conditions; its level is 0.9279
against the GPU tier's 0.9333. Its second cell is a holdout and was not read.

**S8 met.** `cost/cost-table.md`: the body alone and the body with the shipped 33-value table both
hold the display's cadence to 32 surfaces and leave it by 40 at both scales, with single-count
jitter of the kind W16 G0 and W17 G0 both recorded. The demo-page measurement Decision Log 4 (b)
asked for belonged to its budget change; (b) is withdrawn, the budget and the area it is taken over
are untouched, and there is nothing on the demo for it to catch.

**The conditioning predicate (X6, `cfg3.gate.txt`).** One cell leaves —
`checkerboard__capsule-button__rest` under reduced transparency, S7's recovery. **Three join**:
`light-solid__rrect-ml__rest` at both light-standard scales (the named carry) and
`light-solid__rrect-md__rest` at 2x. The mechanism is the same for all three: landing a light solid
on the renderer's level puts it within 0.004 of its own background, which the luminance-delta
extractor separates on the GPU tier only by the rim and lens this tier does not draw. The gate's
remaining failures are the whole-bed count assertions, which cannot pass on a matrix without the
holdout.

## 4. The suites (configuration 3)

| suite | result |
| --- | --- |
| `pnpm -r lint` | clean |
| `pnpm -r test` (eight packages) | **1785 passed**, none failed |
| platform-web Playwright, `chromium` | **129 passed** — the contrast-floor test among them |
| platform-web Playwright, `firefox` | **102 passed** |
| platform-web Playwright, `webkit` | **102 passed** |
| platform-web Playwright, `chromium-gpu` | **9 passed** |
| `@vitreajs/vitrea-react` e2e (three engines) | **105 passed, 3 skipped** |

Every project green. The doctrine's own pixel test — "stays legible with the blur removed — the
tint carries the contrast" — passes without being loosened, which is Decision Log 4 (a)'s
acceptance. The three pins that recompute the tier's law are re-pointed for the ordering fix with
the reason in each.

## 5. The holdout, read once on the frozen configuration

Contract X8's single reading, taken on configuration 3 frozen (Decision Log 6): no source file
changed between the calibration and validation run and this one — the build at 00:28:15 is the
build both were captured from, and the working tree was clean throughout. Twelve runs, six profiles
on each tier, every exit 0. `cfg3-full.verify.txt` and `cfg3-full.gate.txt` are the referee over
the whole matrix.

**S1 met on the whole bed: 115 of 115 GPU captures byte-identical, worst row |Δ| 0.000000.**

**S2 met.** The landing's own gate over the full matrix reads **27 of 31 passing, and no bound and
no floor among the four failures** — all four are the machine's bookkeeping of which cells
condition (three shape-row coverage counts and the predicate list itself), which is G2's to
re-record. The eight held rows all read at or above their pins, six of them up:
`checkerboard__rrect-md` 2x 0.9149 → 0.9153, `rrect-ml` 1x 0.8593 → **0.8757** and 2x 0.8783 →
0.8789, `glass-over-glass` 1x 0.8529 → **0.8610** and 2x 0.8683 → 0.8681, `rrect-lg` 1x 0.8513 →
**0.8702** and 2x 0.8709 → 0.8722.

**What the holdout adds, and it is the reason for reading one.** Four cells the calibration and
validation sets do not contain sit outside the level clause:

| cell | dpr | form | bed CSS−GPU | cfg3 CSS−GPU |
| --- | --- | --- | --- | --- |
| `hc-text__capsule-button` | 1x / 2x | linear | +0.0454 / +0.0441 | +0.0091 / **+0.0119** |
| `hc-text__capsule-button__rest-tint-orange` | 1x / 2x | linear | +0.0177 / +0.0165 | **+0.0129 / +0.0118** |
| `photo__glass-over-glass` | 1x / 2x | linear | +0.0510 / +0.0472 | **−0.0119 / −0.0127** |
| `mid-dark-solid__capsule-button` | 1x / 2x | linear | +0.0437 / +0.0437 | +0.0086 / **+0.0109** |

Every one of them closes by 0.03 to 0.06 against the bed and three of the four land inside 0.01 at
one scale and just outside at the other. `photo__glass-over-glass` is the second of the two surface
families G0 named as outside the closed form's contour — the same family as the `toolbar-group`
gap of §2.1's successor, and it misses in the same direction and by the same order.

**S7 recovers one of its two cells, not both.** `checkerboard__capsule-button__rest` under reduced
transparency conditions (`areaWeb / componentRegion` 0.9961, one body) and leaves the predicate's
exclusion list. `hc-text__capsule-button__rest` under the same profile reads **0.9310** against the
0.95 clause with one body — its level improves markedly, 0.9628 → 0.9478 against the GPU tier's
0.9412, and its area recovery does not clear the bar. The Parent-Level Acceptance names both cells,
so this is the clause's own miss and is reported as such.

**The predicate list, whole bed.** One cell leaves and **four join**: `light-solid__rrect-md` at
2x, `light-solid__rrect-ml` at both light scales, and `hc-text__capsule-button` at 2x. The
mechanism is one: a surface landed on the renderer's level over a background within 0.004 of it,
which the luminance-delta extractor separates on the GPU tier only by the rim and lens this tier
does not draw.
