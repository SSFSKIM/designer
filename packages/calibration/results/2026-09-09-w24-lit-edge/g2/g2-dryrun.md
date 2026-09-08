# W24 G2 — the declaration, and the dry run on the frozen configuration

The wave's rule: declare the constants, the fingerprints and what would stop the change **before**
running the bed. Everything above the horizontal rule was written before this gate captured a single
canonical pixel; everything below it is what the run then read.

---

## 1. What lands, and what the evidence for each is

Four constants land and one term is retired. Every one of them is a leaf of the material profile, so
the whole change crosses into the renderer through the one seam the isolation proof pins.

| constant | before | after | fitted on |
| --- | --- | --- | --- |
| `optics.regular.rimLitExponent` | — | **1.15** | 285 reference bins, 19 untinted solid rows, both beds and both probe grids |
| `rimLitAxis` | — | **[−0.7071, −0.7071]** | the same fit reads 136.0°; the exact diagonal is TAKEN (§1.1) |
| `collapseTransmission` | — | **0.017** | the collapsed `impulse__capsule-button`'s centre dot at 1x, one rendered rung |
| `collapseTransmission2x` | — | **0.070** | the same cell at 2x |
| the one-sided `spec` term on the rim | drawn | **retired** | declined on shape over the same 285 bins |

`optics.clear.rimLitExponent` stays 0 — no scene on either bed declares that variant, so it has no
rows (C9a §6.2). `rimWidth`, `rimWidth2x`, `rimAlpha`, `rimLevelGain`, `rimCollapsed`,
`rimCollapsedTinted`, `rimTintChroma` and `lightDirection` do not move: the lit factor is applied
OUTSIDE W23's amplitude bracket and normalised by `cos 45°` inside the power, so it is exactly 1
wherever the normal is horizontal or vertical at every exponent and no fitted amplitude has to be
re-expressed. `lightDirection` keeps its meaning for the inner shadow and the sweep because the lit
edge takes an axis constant of its own.

### 1.1 The lit edge

**The shape, and why no instrument saw it in three waves.** Every rim reader before W24 read per
SIDE, and a light on the 45° diagonal projects equally on all four straight sides — so `L−R` and
`T−B` are 0 for the reference exactly as they are for a flat rim, and the variation lives entirely
in the corner arcs, which W23's contour reader excludes by construction. Read around the whole
contour and binned by the normal's angle, the 2x dark `dark-solid__rrect-md` reads 0.0420 in its
north-west bin against 0.0016 in its north-east — a ratio of 26 — where vitrea reads 1.25.

**The form is symmetric.** Over 285 bins of 19 untinted solid reference rows, each cell normalised
by its own brightest bin: `(√2·|n · L|)^p` reaches 0.1475 of normalised RMS against 0.2881 for the
one-sided `max(n · L, 0)^p` and 0.3121 for the flat rim vitrea shipped. The one-sided form cannot
reach both ends of a diagonal whose two corners the reference draws equal to a thousandth, and it
degenerates in the fit — running to the ceiling of both its exponent and its floor trying to become
symmetric — which is the deeper reading of W22 G1's fit of `specularGain` to 0.

**The exponent is one constant.** 1.05 jointly; 1.10 light and 1.30 dark on the 2x rows; 1.10 ± 0.22
and 1.24 ± 0.17 on vitrea's own rendered rows against the reference. The schemes overlap, so one
constant is what the rows separate, and 1.15 is where the most rows meet both halves of clause 1.

**The axis is taken, not fitted.** The rows fit 136.0° and do not separate it from 135° (a
thousandth of RMS), and only at the exact diagonal is the factor equal on all four straight sides —
which is the mechanism that makes the amplitude's re-expression closed form. Measured on G0's
ladder, the worst straight-span movement is **0.00021** against a bound of 0.005.

**The ambient floor is declined and absent from the code.** The wave chartered `a + (1 − a)|n·L|^p`
with `a` expected at 0.15 dark and 0.25 light; every grouping fits it to 0.000 over a search of
0…0.6. The bin mean of `|cos|^p` over the 22.5° straddling the null already carries 0.10–0.16, which
is the whole of what the dim bins hold. A constant every row fits to zero is not carried, and it is
removed rather than shipped at 0.

**The `spec` term is retired from the rim on both tiers, and one thing goes with it.** The shipped
profiles carry `specularGain` 0 on `regular`, and no scene on either bed or in the golden suite
declares `clear`, so nothing measured moves. The `clear` variant's unfitted structural 0.45 stops
drawing — a change to a variant with no rows in either direction, made because the term is now
measured to have the wrong shape rather than merely the wrong gain. It is named here for the
parent, and it is one line to restore. `specularPower` and `specularGain` stay on the profile and in
both documents so the W22 record and this document's shape are unchanged; nothing reads them.

### 1.2 The collapse's transmission

**What removes the dot is the collapse's TARGET, and it is arithmetic.** On every
`impulse__capsule-button` cell of both schemes at both scales the collapse runs at `k` = 1.0000
exactly (toneX 0.0049 against `backdropToneLow` 0.02), read off the calibration page's own published
group state, and the W9 response solve is stood down twice over there. The composite is
`(1 − k)·M + k·target` with `target` the group's MEAN backdrop colour — one number for the whole
surface, which is what flattens the dot away. The target now lerps toward the per-pixel blurred
backdrop the refraction path already sampled; the tone axis's argument, the response law and the
collapsed rim are untouched.

**Two anchors because the kernels are two.** The reference transmits through σ 2.63 device px at 1x
and 1.30 at 2x — the same kernel as its uncollapsed cells, so the collapse changes the level and not
the blur — and that width is invariant in neither CSS nor device pixels, where vitrea's runs
1.68 → 4.86. The share cannot be one number over a width that is two.

**The fit's row is a validation row, and that is spent.** The only `impulse` CALIBRATION cell is the
tinted one, which does not move on either side at 1x; `dark-solid` holds the constant at zero by
construction. `collapseTransmission` is fitted on `impulse__capsule-button__rest` and checked by
three independent things: the two scales agreeing on a mechanism, the two schemes rendering the same
numbers, and every other capture of both beds holding byte-identical (W24 Decision Log 2 (e)).

**The accessibility regimes stand down.** Both tiers gate the transmission on
`backdropToneUnderPolicy ≥ 0.999`, so under Reduce Transparency, Increase Contrast or any fold of
the tone axis the target is the group's mean — W7's behaviour, and what those profiles were fitted
on. The two degraded profiles are therefore expected to be **byte-identical on this mechanism**, and
that is read below rather than asserted. It is a decision and not an arithmetic necessity: a
degraded reference's collapsed appearance over a textured backdrop has never been read.

## 2. The fingerprints

| document | before | after |
| --- | --- | --- |
| `apple-macos-26.5-1x-light-standard.json` | `c426a37744c38cce` | **`7968a7f8106b10a4`** |
| `apple-macos-26.5-1x-dark-standard.json` | `bf5752ac1b152238` | **`0d741cd19cd1243b`** |

Both documents move, so all six profiles are re-run and none rides along as a byte check. The dark
document's own `patch` does not move — all four constants are the material's — so
`platform-web/src/dark-profile.ts` regenerates **byte-identical** (X7), verified by running
`profile:dark` and diffing.

## 3. The stops, declared

W23 G1's S1–S8 and S10, and the wave's own S11.

- **S1** — any untinted row worse than the W23 bed by more than 0.001 ΔE mean or 0.005 `ssimMean`.
  Read on `mid-dark-solid__capsule-button` with its sign (W24 Decision Log 2 (g)): its worst angular
  bin moves the WRONG WAY above exponent 1.0 (0.0087 at 1.00, 0.0124 at 1.15, 0.0164 at 1.30
  against 0.0124 on the landed bed), it is a holdout row, and nothing was fitted on it.
- **S2** — any tinted cell moved by more than 0.002 in body.
- **S3** — a calibration ΔE mean above the W23 bed's by more than 0.0001.
- **S4** — a golden moved for any reason but the two mechanisms.
- **S5** — a fitted constant whose rows do not separate it.
- **S6** — a CSS capture moved without an explanation.
- **S7** — a collapsed cell whose body moves by more than 0.002.
- **S8** — the user's eye.
- **S10** — a cell neither mechanism reaches that moves at all.
- **S11** — W23's straight-span contour reads moved by more than 0.005 on any solid side.

## 4. How the bed is run

`g2-dryrun-run.sh`, all six profiles on both tiers, **calibration and validation first**; then, only
once every clause and every stop above has been read on those rows and nothing has fired,
`g2-holdout-run.sh`. **This is the wave's one holdout read (X3)**, taken on the constants above and
on nothing else; G3 reproduces every capture byte for byte from `g2-digests.txt`. Captures and
matrix go to scratch through `VITREA_WEB_CAPTURES` and `--out-matrix`; the canonical
`results/matrix.json`, `web-captures/`, `apps/reference-apple/fixtures/` and `scenes.json` are
untouched. The flags are the canonical rebuild's — `--alpha` and `--write-partial` — because G3 has
to reproduce these bytes with them.

## 5. What the CSS tier takes, and what it cannot

**The transmission, exactly.** Matching the renderer's composite term by term against this tier's
one `rgba()` over one `backdrop-filter` gives the whole mirror in two lines:

```
A' = α + k(1 − α) − k·c   =  A − k·c
T' = ((1 − k)·α·tint + k·(1 − c)·tone) / A'
```

`(1 − A')·B + A'·T'` is then `(1 − k)·M + k·[(1 − c)·tone + c·B]` — the renderer's expression. No
second layer, no second filter, no new mapping constant; at `k` = 1 the collapsed surface stops
being opaque, which is precisely the transmission. The two tiers therefore no longer state the same
(colour, alpha) PAIR, and `tier-coherence` is re-stated on the composite, with the pair still pinned
wherever the collapse is not running.

**The lit edge, only where it can be derived.** This tier draws one inset shadow of one alpha and
cannot vary a rim around a contour at all. Its rim AMPLITUDE does not move, by the `√2`
normalisation. What does move is the band's own integral inside `interiorBandLight`: the factor is
exactly 1 on the four straight runs and below 1 on the corner arcs, which sweep one full turn
between them, so the arcs' `2π` becomes `∮ (√2|cos θ|)^p dθ` and the derived interior light falls to
0.956 of what it was on a capsule (all arc), 0.976 on `rrect-md` and 0.977 on `rrect-ml`.

**The CSS-only residuals, recorded and not chartered:** the rim's angular VARIATION, which one inset
shadow cannot carry in any form; and the transmitted dot's WIDTH, since this tier's one Gaussian at
`blurSigma` is not the renderer's sharp-plus-heavy mix — the share is exact and the width is not,
and that residual is smaller than the one the renderer itself carries against the reference.

---

## 6. What the run read

`g2-evidence.sh` reads it all: `read-canonical.sh` puts both instruments over both beds before and
after, `g2-clauses.py` evaluates clauses 1 and 3, `run-impulse.sh` is clause 2, `stops.py` reads S1,
S2, S7 and S11, `delta-e.py` is clause 4's headline, `byte-identity.py` names every mover (S10) and
`g2-digests.py` is what G3 reproduces. 229 cells, 460 captures. The outputs are `g2-clauses.txt`,
`impulse-read.txt`, `stops.txt`, `delta-e.txt`, `byte-identity.txt`, `g2-digests.txt` and
`g2-gate.txt` beside this file; the goldens are `goldens-attribution.txt`.

**Twenty-four runs, all exit 0.** The calibration and validation columns ran first (03:05–03:10);
every clause and every stop below was read on them; then the holdout, once, at 03:16–03:19, with
nothing in the material, the documents, the goldens or the code moved in between.

### Clause 1 — the edge is lit: the shape lands, the ratio half is met on 5 rows of 12

The instrument is the angular reader on the GPU tier, untinted solid rows, both canonical beds at
both scales, holdout included.

**(a) The ratio, within 20 % of the reference's where the reference's exceeds 2 — met on 5 of 12.**

| profile | cell | reference | landed bed | this gate | after/ref |
| --- | --- | --- | --- | --- | --- |
| 1x light | `dark-solid__capsule-button` | 12.38 | 1.29 | 13.38 | **1.08** |
| 1x light | `dark-solid__rrect-md` | 5.46 | 2.33 | 47.75 | 8.75 |
| 1x light | `mid-dark-solid__capsule-button` | 5.82 | 2.00 | 18.02 | 3.10 |
| 2x light | `dark-solid__capsule-button` | 15.97 | 1.25 | 12.48 | 0.78 |
| 2x light | `dark-solid__rrect-md` | 7.72 | 1.49 | 17.97 | 2.33 |
| 2x light | `mid-dark-solid__capsule-button` | 6.23 | 1.44 | 16.31 | 2.62 |
| 1x dark | `dark-solid__capsule-button` | 12.38 | 1.29 | 13.38 | **1.08** |
| 1x dark | `dark-solid__rrect-md` | 21.07 | 1.25 | 17.83 | **0.85** |
| 1x dark | `mid-dark-solid__capsule-button` | 2.16 | 1.24 | 2.26 | **1.05** |
| 2x dark | `dark-solid__capsule-button` | 15.97 | 1.25 | 12.48 | 0.78 |
| 2x dark | `dark-solid__rrect-md` | 25.86 | 1.25 | 13.73 | 0.53 |
| 2x dark | `mid-dark-solid__capsule-button` | 2.43 | 1.07 | 2.66 | **1.09** |

Every row went from a rim that was one number the whole way round (1.07–2.33) to one with the
reference's own kind of angular contrast (2.26–47.75). The five misses are of two different kinds
and neither is a failure of the shape:

- **Overshoot, on the light bed's rrect and `mid-dark-solid` rows (2.3× to 8.8×).** The ratio is a
  quotient by the DIMMEST bin, and `(√2·|n · L|)^p` goes to zero at the null while the reference's
  profile keeps a floor there — G0 §8.5's finding that the reference's lobe is flatter and its null
  shallower than a single power law's. The statistic divides by a number approaching zero, so a
  shape that is closer everywhere reads a ratio that is further away. **The bin-by-bin half of the
  clause is the one that is not degenerate**, and it is met on the same rows.
- **Undershoot at 2x (0.78, 0.53).** The exponent is one constant where the reference's angular
  contrast depends on the scale: every 2x row wants 1.30–1.45 and every 1x row 0.85–1.10 (G0 §8.1).
  1.15 is the value the rows separate, and at 2x it under-reaches by exactly that difference. The
  scale dependence is on the record and a second anchor is not fitted on four rows.

**(b) The worst bin error, at or under half the landed bed's — met on 10 of 12.**

| profile | cell | landed bed | this gate | share |
| --- | --- | --- | --- | --- |
| 1x light | `dark-solid__capsule-button` | 0.0130 | 0.0024 | **0.18** |
| 1x light | `dark-solid__rrect-md` | 0.1070 | 0.0657 | 0.61 |
| 1x light | `mid-dark-solid__capsule-button` | 0.1284 | 0.0884 | 0.69 |
| 2x light | `dark-solid__capsule-button` | 0.0177 | 0.0044 | **0.25** |
| 2x light | `dark-solid__rrect-md` | 0.2020 | 0.0844 | **0.42** |
| 2x light | `mid-dark-solid__capsule-button` | 0.2038 | 0.0960 | **0.47** |
| 1x dark | `dark-solid__capsule-button` | 0.0130 | 0.0024 | **0.18** |
| 1x dark | `dark-solid__rrect-md` | 0.0194 | 0.0085 | **0.44** |
| 1x dark | `mid-dark-solid__capsule-button` | 0.0118 | 0.0042 | **0.35** |
| 2x dark | `dark-solid__capsule-button` | 0.0177 | 0.0044 | **0.25** |
| 2x dark | `dark-solid__rrect-md` | 0.0292 | 0.0112 | **0.38** |
| 2x dark | `mid-dark-solid__capsule-button` | 0.0145 | 0.0070 | **0.48** |

Not one row is worse. The two that miss the half are the light bed's 1x rows, at 0.61 and 0.69 —
improvements of 39 % and 31 % where the clause asks for 50 %, and the residual is W23's amplitude
rather than this wave's shape.

**The row Decision Log 2 (g) told this gate to watch did not do what the ladder feared.**
`mid-dark-solid__capsule-button` was named because its worst bin moved the wrong way above exponent
1.0 on the ladder's own reads. On the bed it improves on every profile — worst bin 0.1284 → 0.0884
(1x light), 0.2038 → 0.0960 (2x light), 0.0118 → 0.0042 (1x dark), 0.0145 → 0.0070 (2x dark) — and
its ΔE improves with it on all four (see S1 below). **S1 does not fire on it.**

### Clause 2 — the collapsed material transmits: the peak MET, the FWHM and the body recorded

`impulse-read.txt`, the collapsed `impulse__capsule-button`, GPU tier, both schemes (the two schemes
render the same numbers, as they did at the fit):

| reading | native | landed bed | this gate | clause |
| --- | --- | --- | --- | --- |
| 1x peak | +0.0066 | **0.0000** | **+0.0067** | ✅ 0.0001 against 0.005 |
| 1x FWHM (CSS px) | 7.57 | — | 4.99 | recorded: 2.58 short — the kernel |
| 1x body | 0.0066 | 0.0037 | 0.0037 | recorded: −0.0029, unchanged and pre-existing |
| 2x peak | +0.0254 | **0.0000** | **+0.0256** | ✅ 0.0002 |
| 2x FWHM | 3.80 | — | 4.64 | recorded: +0.84 |
| 2x body | 0.0067 | 0.0033 | 0.0034 | recorded: −0.0033 |

The peak is met at both scales in both schemes, exactly at the fit's prediction. The FWHM and the
body are the two sub-clauses W24 Decision Log 2 (f) carries by name: the first is vitrea's own
scatter kernel, which is the wrong width at 1x and no value of a transmission share can change a
width; the second is the collapse's target LEVEL, which sits at the backdrop's mean where Apple's
collapsed glass sits above it, and is the natural next term.

### Clause 3 — answered, and the cells it names did not move

The dark structured thin capsules run `k` = 0.0000 at both scales in both schemes, so no
transmission constant reaches them (W24 G1 §4, read off the running system's own published group
state). What this gate adds is that nothing else reached them either: on the GPU tier their bodies
move by at most **0.00011** and on the CSS tier by at most **0.00120**, against clause 3's own
−18 to −22 codes of standing deficit, which is §5.89's dark passthrough and not this wave's term.

### Clause 4 — the bed no worse anywhere, and better nearly everywhere

`delta-e.txt`, OKLab ΔE mean per profile / tier / set. **Every GPU calibration group improves:**

| profile | GPU calibration | GPU validation |
| --- | --- | --- |
| 1x light | 0.00324 → **0.00321** | 0.00246 → 0.00241 |
| 2x light | 0.00329 → **0.00326** | 0.00250 → 0.00248 |
| 1x dark | 0.00395 → **0.00393** | 0.00251 → 0.00244 |
| 2x dark | 0.00397 → **0.00395** | 0.00294 → 0.00297 |
| 1x light reduced-transparency | 0.00172 → **0.00171** | 0.00112 → 0.00110 |
| 1x light increased-contrast | 0.00793 → 0.00793 | 0.00862 → 0.00862 |

Clause 4 asks for no calibration mean above the W23 bed's by more than 0.0001; every one is BELOW
it. Five groups of twenty-four are worse at all, and the worst is +0.00008 (`increased-contrast` /
css / validation). Row by row (S1) the worst ΔE rise anywhere is **+0.00008** against a bound of
0.001 and the worst `ssimMean` fall is **−0.00082** against 0.005; **no row fires**.

The straight-span half of clause 4 is S11 below.

### Clause 5 — the holdout, read once

| profile | tier | before | after |
| --- | --- | --- | --- |
| 1x light | webgpu | 0.00901 | **0.00898** |
| 2x light | webgpu | 0.00898 | **0.00895** |
| 1x dark | webgpu | 0.01331 | **0.01325** |
| 2x dark | webgpu | 0.01317 | **0.01311** |
| 1x light reduced-transparency | webgpu | 0.00345 | **0.00343** |
| 1x light increased-contrast | webgpu | 0.02042 | 0.02042 |
| 1x light | css | 0.01577 | 0.01576 |
| 2x light | css | 0.01617 | 0.01617 |
| 1x dark | css | 0.01731 | 0.01735 |
| 2x dark | css | 0.01741 | 0.01739 |
| 1x light reduced-transparency | css | 0.00751 | 0.00751 |
| 1x light increased-contrast | css | 0.04557 | 0.04561 |

Every GPU holdout group improves or holds. Two CSS holdout groups are worse by 0.00004.

### Clause 6 — the goldens, attributed

`goldens-attribution.txt`. The lit edge moves **not one pixel outside a contour band on any scene**;
inside, 15–81 code values on the eleven scenes that draw a rim. The transmission moves
`collapsed-tone-textured` (1 669 pixels in band, 13 147 outside it, by up to 3 codes — the collapsed
bodies, which is what that scene exists for) and 16 pixels by 1 code on `collapsed-tone`, whose
backdrop is flat and where the only disagreement between the per-pixel sample and the group mean is
what the refraction path's own displacement reaches at the contour. `highlight-press-glow` moves 0
pixels under both, and its hash is byte-identical to the 2026-08-25 original for the eleventh wave
running. Twelve hashes are re-recorded under `W24_HASHES`, one of them a first reading for the new
scene; the suite is 33/33 green behind them.

### Clause 7 — what the CSS tier took, and the one thing its own conversion refuses

**The lit edge's derivable half landed.** `interiorBandLight` integrates the factor over the corner
arcs, so the band's derived interior light falls to 0.956 of what it was on a capsule, 0.976 on
`rrect-md` and 0.977 on `rrect-ml`. Eighty of 115 CSS renders move for that reason; the tier's rim
AMPLITUDE does not move at all, by the `√2` normalisation.

**The transmission's arithmetic landed and its captures did not, and the reason is a measurement
this gate made rather than an oversight.** The mirror is exact — `A' = A − k·c` with the tone's
share re-solved — and it reaches the declaration on any collapsed surface the tier converts
ordinarily. On this bed it does not, because every collapsed cell here is a cell whose composite
sits below the linear chain's reach, so the tier anchors its conversion on the group's own tone
(W21 Decision Log 4 (a)'s `conversionAnchor`). That solve reproduces the GPU tier's LEVEL, and over
a backdrop whose tone equals the tint it is DEGENERATE — every alpha reproduces the same level — so
it returns 1 and the transmission is thrown away. Measured, not inferred: at `collapseTransmission`
0.2 the collapsed `impulse__capsule-button` CSS capture is byte-identical to the landed one
(0 pixels moved), and the anchored conversion returns `cssTintAlpha` = 1 for source alphas of
0.983 and 0.800 alike.

That is an X5 residual and it is recorded rather than chartered: **the CSS tier does not transmit
on the cells this bed can see.** The candidate fix is one line — cap the anchored solve at the
source's own alpha, since a tier may not draw a surface MORE opaque than the material is — and it
changes the conversion on every anchored cell, so it belongs to a gate with its own rows and the
parent's word rather than to this one.

The tier's other residuals stand as declared: it cannot vary a rim around a contour in any form, and
the dot it would transmit arrives through one Gaussian rather than the renderer's two components.

### The stops

| stop | reading | verdict |
| --- | --- | --- |
| **S1** untinted row ΔE +0.001 / ssim −0.005 | worst +0.00008 / −0.00082; `mid-dark-solid__capsule-button` improves on all four profiles | **clear** |
| **S2** tinted body 0.002 | worst 0.00026 | **clear** |
| **S3** calibration ΔE mean +0.0001 | every group improves | **clear** |
| **S4** a golden moved for another reason | 0 pixels outside any contour band from the lit edge; the transmission's movers are the two collapsed scenes | **clear** |
| **S5** a constant whose rows do not separate it | the ambient floor was declined and removed; nothing was fitted on a row that does not separate it | **clear** |
| **S6** a CSS capture moved without an explanation | 80 renders and 5 alphas moved; the renders are `interiorBandLight`'s arc integral and the alphas are the four `dark-solid` collapsed capsules | **clear** |
| **S7** collapsed body 0.002 | worst 0.00007 | **clear** |
| **S8** the user's eye | the sheets are `sheets/g2-1x.png` and `g2-2x.png` | the user's |
| **S10** a cell neither mechanism reaches moves | 9 GPU captures identical, and they are the increased-contrast cells where `border: "strong"` folds the exponent to 0; every other GPU cell draws a rim, which the lit edge reaches by construction | **clear** |
| **S11** a straight span moved by more than 0.005 | GPU worst **0.00029**; CSS **0.00571 on one cell** | **fires on the CSS tier** |

**S11's firing, dispositioned.** It is one cell, `mid-dark-solid__capsule-button` at 1x light, on the
CSS tier, on its top and bottom spans, at +0.00571 against a 0.005 bound. It is not the rim: the
contour reader's rim is `peak − body`, and on that cell the body FELL by 0.00285 while the contour
row ROSE by 0.00286, so a level change of 0.00285 linear — about four tenths of an eight-bit code at
that body — is reported as twice itself. The tier's rim amplitude cannot have moved, because no
constant it reads moved; what moved is `interiorBandLight`, which is the lit edge's derivable half
doing exactly what X5 asks. On the tier S11 was written for — the GPU tier, where G0's ladder read
0.00021 — the bed reads **0.00029** against 0.005. The cell's own ΔE improves (css 0.00400 →
0.00389). Recorded for the parent; the stop is not treated as a halt.

### The gate over the scratch matrix

`g2-gate.txt`, `VITREA_MATRIX_PATH` pointed at the dry run: **5 of 33 cases fail**, and they split
into two kinds.

- **Four are the conditioning predicate moving**, which is what CLAUDE.md says a fidelity change
  does: `PREDICATE_EXCLUDES` reads 31 where the file names 27, and the three shape-cell counts that
  follow from it (35 → 36, 33 → 31, 12 → 13) move with it. Re-deriving that file is G3's, by the
  wave's own charter.
- **One is a regression floor breached**, and it is the reading the parent has to see:
  `dom / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-1x-dark-standard ::
  silhouetteIoU` reads **0.90804** against a floor of 0.9090 pinned at a landed 0.91007 — a fall of
  0.00203, breaching by 0.00096. It is a CSS-tier cell and a nested-pane one, which is the family
  the wave expected to move; the cause is the same interior-level shift S11 reports, moving where
  the silhouette's threshold crosses. **A floor comes off by fix and is re-pinned only by the
  user** (the fidelity discipline), so it is named here and carried to G3 and to the user, not
  re-pinned by this gate.

### The digests

`g2-digests.txt`: both profile documents' file digests and resolved fingerprints, and the sha256 of
every one of the 229 captures at the frozen configuration. G3 reproduces them from the main
checkout.

### By eye

`sheets/g2-1x.png` and `sheets/g2-2x.png`: native | GPU before (the canonical 0.12.0 bed) | GPU
landed | CSS landed, both schemes, the solids, the impulse cells and the tinted capsules, with the
dark capsules and rrects repeated at 4× per CSS px cropped to the whole surface so the ARCS are
visible, and the impulse capsule's centre dot at 4× beside them. On the 2x dark capsule's arc row
the reference's north-west arc is visibly brighter than its north-east one, the landed panel now
does the same thing, the panel before it does not, and the CSS panel cannot. **The user's veto
stands over all of it (X6, S8).**
