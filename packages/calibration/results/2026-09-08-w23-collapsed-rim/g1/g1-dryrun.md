# W23 G1 — the declaration, and the dry run on the frozen configuration

The wave's rule: declare the constants, the fingerprints and what would stop the change **before**
running the bed. Everything above the horizontal rule was written before this gate captured a single
canonical pixel; everything below it is what the run then read.

---

## 1. What lands, and what the evidence for each is

Six constants move and one is removed. Every one of them is a leaf of the material profile, so the
whole change crosses into the renderer through the one seam the isolation proof pins.

| constant | before | after | fitted on |
| --- | --- | --- | --- |
| `optics.regular.rimAlpha` (light) | 0.18 | **0.844** | 40 rendered solid rows, 10 cells, condition 9.7 |
| `optics.regular.rimLevelGain` (light) | — | **−0.628** | the same solve |
| `optics.regular.rimAlpha` (dark patch) | 0.082 | **0.0265** | 32 rendered solid rows, 8 cells, condition 29.7 |
| `optics.regular.rimLevelGain` (dark patch) | — | **+2.334** | the same solve |
| `optics.regular.rimWidth2x` | — | **1.35** | one rendered point at 1.2 on both beds at 2x |
| `rimCollapsed` | — | **0.038** | 28 reference sides, 11 collapsed cells |
| `rimCollapsedTinted` | — | **0.337** | one rendered point per scale on three tinted collapsed cells |
| `cssTierMapping.borderAlphaPerRimAlpha` | 1.95 | **0.64** | re-based, not refitted — see §5 |
| `optics.*.rimEnvGain` | 0 | **removed** | declined on every row of both beds |

`rimWidth` 1.5, `specularPower` 6, `specularGain` 0 and `lightDirection` do not move, and the
`clear` variant does not move at all: it declares no scene on this bed.

**The rim's law is (L4)**, `rimAlpha + rimLevelGain × luminance(material)`, affine in the surface's
own rendered level with the gain's sign opposite in the two schemes. G0 chose the form on the
reference's own solid sides — 44 in light and 36 in dark, from both canonical scales and both probe
grids — where it reads mean |residual| 0.0081 / 0.0013 against 0.0249 / 0.0253 for the additive
constant this replaces, 0.0168 / 0.0259 for a pure screen and 0.0105 / 0.0042 for screen plus an
environment term (claims §5.100 §4).

**One thing about the law's INPUT is G1's and not G0's,** and it is the only place this gate
departed from a rendered prediction. The shader takes the level as the tint shade does, and the tint
shade reads the composite *after* the author's colour. On the untinted rows that is the same
quantity; on the tinted ones it is not, and at G0's fitted point the dark bed's tinted structured
cells drew +0.3444 against the reference's +0.1286 — worse than the landed bed by 0.108, where
W23 Decision Log 2 (c) binds this gate to no tinted row worse than landed by more than 0.03. The rim
is the MATERIAL's mark and the author's colour is painted over it, which is Decision Log 2 (c)'s own
first candidate ("the rim beneath the author tint's coverage") read as an input rather than as a
composite order. The shader now keeps the material's own composite beside the tinted one and the
rim's law reads that; for an untinted pixel the two are bit-identical and no untinted row moves.
Rendered, every tinted row on both beds comes inside the binding (§6).

**`rimEnvGain` is removed rather than shipped at 0.** It is worse than the affine law on the
reference in both schemes and separated by no row on either bed — the rendered ladder point at +0.10
of gain moved every solid cell by 0 or 0.0005 — so C9a §6.2 applies and a declined constant is not
carried. The reference's own environment dependence is real and goes to the wave's Deferred list
with its numbers.

**`rimTintKeep` was tested and refused.** Decision Log 2 (c)'s second candidate was to gate the
collapse itself on the author tint's coverage, so that a painted surface keeps its APPEARANCE's own
rim. Rendered on both beds, the gate needs **0.534** on the light bed and **0.294** on the dark one
to reach the reference's +0.1149 on `dark-solid__capsule-button__rest-tint-orange` — a cell whose
reference fixture is byte-identical between the two schemes. A gate on `present` makes the kept rim
proportional to each scheme's amplitude law, and those differ by 1.8× there, so no single value can
draw one appearance out of two materials. What lands instead is `rimCollapsedTinted`, absolute in
its own units exactly as `rimCollapsed` is, which is X4's shape and reads the same in both schemes
by construction.

## 2. The fingerprints

| document | before | after |
| --- | --- | --- |
| `apple-macos-26.5-1x-light-standard.json` | `f6c54a1ea236447a` | **`ee0010558553ee12`** |
| `apple-macos-26.5-1x-dark-standard.json` | `d86f480c0e136627` | **`afd0e999e2f5813e`** |

Both documents move, so all six profiles are re-run and none rides along as a byte check.
`platform-web/src/dark-profile.ts` is regenerated from the dark document (X7) and
`dark-profile-export.test.ts` and `tuned-profiles.test.ts` are green on both directions.

## 3. The stops, declared

- **S1** — any untinted row worse than the W22 bed by more than 0.001 ΔE mean or 0.005 `ssimMean`.
- **S2** — any tinted cell moved by more than 0.002 in body.
- **S3** — a calibration ΔE mean above the W22 bed's by more than 0.0001.
- **S4** — a golden moved for any reason but the rim.
- **S5** — a fitted constant whose rows do not separate it.
- **S6** — a CSS capture moved without an explanation.
- **S7** — a collapsed cell whose body moves by more than 0.002.
- **S8** — the user's eye.

## 4. How the bed is run

`g1-dryrun-run.sh`, all six profiles on both tiers, calibration and validation first and the holdout
last so a stop can fire before the holdout is opened. **This is the wave's one holdout read (X3)**
and it is taken on the constants above and on nothing else; G2 reproduces every capture byte for
byte from `g1-digests.txt`. Captures and matrix go to scratch through `VITREA_WEB_CAPTURES` and
`--out-matrix`; the canonical `results/matrix.json`, `web-captures/`, `apps/reference-apple/fixtures`
and `scenes.json` are untouched.

## 5. What the CSS tier takes, and what it cannot

The mirror takes the amplitude law (`optics.ts`'s `rimAmplitude`, evaluated once per group at the
level the tint shade is already read at) and the collapsed rims through the same `(1 − k)` seam
(`rimAmplitude × (1 − k) + collapsedRim(tintStrength) × k`), and `interiorBandLight` takes the law's
amplitude too, or the derived interior level drifts by the band's own light (claims §5.100 §8).

`borderAlphaPerRimAlpha` moves 1.95 → 0.64 and this is **not a refit**: the constant converts the
renderer's rim into this tier's border alpha, and the renderer's rim stopped being `rimAlpha` and
became an amplitude about three times larger, so 1.95 against it reads 1.07 and would clamp to an
opaque white outline on every surface. Divided by the same ratio, the border on an unsampled surface
is 0.3509 against the 0.351 it has drawn since W6 — a fortieth of an 8-bit code. What moves anyway
is the law arriving: the border now varies with the surface's own level, and a collapsed surface
draws a border where it drew none.

**The CSS-only residuals, recorded and not chartered:** the band's SHAPE (this tier draws one CSS px
of one alpha where the renderer spreads a squared falloff over 1.5, and `rimWidth2x` grades that
band at dpr 2 — neither reaches here); a PER-PIXEL level over a structured backdrop, which is the
approximation `materialLuminance` already makes and `tier-coherence` already gates; and the tier's
own rim amplitude, which the contour read now measures for the first time — light 1x
`dark-solid__rrect-md` +0.1576 against the reference's +0.2293 and `checkerboard__rrect-md` +0.0985
against +0.1763, 30–45 % short over a dark backdrop, while dark 1x `dark-solid__rrect-md` reads
+0.0415 against +0.0256, 1.6× too bright, which the re-based conversion roughly halves toward the
reference. `borderAlphaPerRimAlpha` is the constant a CSS wave would fit on this instrument; the
fixtures' own ΔE cannot see it (a 1.01× grid between 0 and 1.95).

---

## 6. What the run read

`g1-evidence.sh` reads it all: `read-canonical.sh` puts both instruments over both beds before and
after, `g1-clauses.py` evaluates clauses 1–4 per side, `stops.py` reads S1, S2 and S7, `delta-e.py`
is clause 5's headline, `byte-identity.py` names every mover and `g1-digests.py` is what G2
reproduces. 229 cells; the outputs are `g1-clauses.txt`, `stops.txt`, `delta-e.txt`,
`byte-identity.txt`, `g1-digests.txt` and `g1-gate.txt` beside this file.

**One run of the twenty-four exited 1**, `apple-macos-26.5-1x-light-increased-contrast / css /
holdout`: `hc-text__capsule-button__rest` could not be measured on `contourCurvature` ("a 0.00px
contour sampled 512 times at σ=3 carries no curvature"). It is not this gate's: that dom cell is
absent from the canonical W22 matrix for the same reason, so the bed carries the same hole. The
capture was written and `--write-partial` recorded the rest of the run.

### Clause 1 — glass on black is visible: the rim MET, the body missed on one cell and did not move

| cell | scheme | dpr | side | native | before | after | Δ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `dark-solid__capsule-button` | both | 1x | top/bottom | +0.0200 | **0.0000** | +0.0167 | −0.0033 |
| `dark-solid__capsule-button` | both | 2x | top/bottom | +0.0204 | **0.0000** | +0.0164 | −0.0040 |
| `impulse__capsule-button` | both | 1x | top | +0.0166 | **0.0000** | +0.0165 | −0.0000 |
| `impulse__capsule-button` | both | 2x | top | +0.0159 | **0.0000** | +0.0164 | +0.0005 |

**Every collapsed side of every collapsed cell, in both schemes at both scales, is inside 0.005**;
the worst is 0.0040. Before this gate every one of them was exactly 0.0000 — the collapse folded the
rim out — and that is the user's finding closed on the instrument.

The BODY half is met on `dark-solid__capsule-button` (+0.0007) and **missed on
`impulse__capsule-button` by 0.0029–0.0033** against a bound of 0.002. It did not move: stop S7
reads the largest collapsed-body movement over the whole bed at **0.00004**. The miss is the
pre-existing −6.2 codes G0 read (native 0.00664, web 0.00367; claims §5.100 §3) and no constant of
this wave touches it. It is the collapse's own level, and a body wave's.

### Clause 2 — the rim's law on the solids: MET

Worst |after − native| over every untinted solid side at both scales in both schemes: **0.0200**
against the clause's 0.03. `light-solid`'s rows clip in the reference and in vitrea and are reported
as clips rather than as amplitudes, which is the clause's own wording. `L−R` is inside 0.003 on
every solid cell.

### Clause 3 — the law off the solids: MISSED as a per-side bound, and better on 62 sides of 88

Over the 88 structured sides of both beds at both scales:

| rows | mean \|d\| before → after | worst before → after | sides over 0.05 before → after |
| --- | --- | --- | --- |
| all structured | 0.0886 → **0.0420** | 0.3124 → 0.1917 | 68 → **24** |
| top / bottom | 0.0750 → **0.0227** | 0.1680 → 0.0778 | 41 → **5** |
| left / right | 0.1082 → 0.0699 | 0.3124 → 0.1917 | 27 → 19 |
| `impulse` cells | 0.1513 → **0.0064** | 0.1680 → 0.0104 | 8 → **0** |

The clause's second half is met: the validation rows read mean |d| **0.0155** against the
calibration rows' **0.0479**, so the law is not a fit to the cells it was fitted on.

The clause's first half is not. **The residual is almost entirely the LEFT and RIGHT sides of the
structured cells,** and it is largely the instrument's rather than the law's: on
`checkerboard__rrect-md` at 1x the reference's own two sides read +0.2465 (left) and +0.1028
(right), a 2.4× split on a cell whose top and bottom agree to 0.002, because a checkerboard's phase
under one vertical contour is not its phase under the other. vitrea drew +0.3609 / −0.2096 before
this gate and +0.4293 / −0.0645 after: the right side improves by 0.145 and the left worsens by
0.069. **Eight sides met 0.05 before and do not now** — six of them `photo__rrect-md` and
`photo__rrect-ml` at 2x, which overshoot by +0.06…+0.12, and two the dark `checkerboard__rrect-md`
left side. Every one of the eight is a per-pixel level under a structured backdrop, which is the
term the CSS tier cannot carry either and the one the environment term was declined on.

### Clause 4 — the band read does NOT close, and the two instruments disagree in a legible way

W22's declared-geometry band read on the same captures. The eighteen sides of the three cells W22
deferred crossed the target rather than reaching it:

| cell (light) | dpr | side | native | before (Δ) | after (Δ) |
| --- | --- | --- | --- | --- | --- |
| `dark-solid__rrect-md` | 1x | top | 0.5272 | 0.4343 (−0.0928) | 0.5581 (**+0.0309**) |
| `impulse__rrect-md` | 1x | top | 0.4949 | 0.4052 (−0.0898) | 0.5300 (**+0.0351**) |
| `mid-dark-solid__capsule-button` | 1x | top | 0.4538 | 0.3896 (−0.0642) | 0.5092 (**+0.0555**) |
| `dark-solid__rrect-md` | 2x | top | 0.5408 | 0.4536 (−0.0872) | 0.6287 (**+0.0879**) |

Mean |d| over the eighteen sides 0.0329 → 0.0309, worst 0.0930 → 0.1246. And **47 sides that met
W22's 0.03 no longer do**, across sixteen cells — the rim they measure really is brighter.

The two readers disagree about the same rim and the disagreement locates itself. On
`dark-solid__rrect-md` at 1x the CONTOUR read gives +0.2176 against the reference's +0.2293 (−0.007,
inside clause 2), while the BAND read gives an excess over the body of +0.078 against the
reference's +0.047 (1.65× over). The contour read excludes 1.6 radii of corner by construction and
the band read averages the corner arcs in, so what the two disagree about is **the rim in the
CORNERS**: on the straight span vitrea now matches the reference, and over the whole side including
the arcs it overshoots. That is a candidate and not a proof — this gate has no corner reader — but
it is the only place the two instruments differ, and it is a gap the wave should record rather than
argue away. **Clause 4 is MISSED, and the parent decides** whether it stands as written, is restated
on the straight span, or the corner rim becomes named work.

### Clause 5 — the bed no worse anywhere: MET on the GPU tier

OKLab ΔE mean per profile, set and tier, before → after (`delta-e.txt`). Every GPU calibration mean
improves or holds:

| profile | tier | calibration | validation | holdout |
| --- | --- | --- | --- | --- |
| 1x light standard | webgpu | 0.00330 → **0.00328** | 0.00261 → 0.00252 | 0.00914 → **0.00909** |
| 2x light standard | webgpu | 0.00333 → **0.00332** | 0.00332 → 0.00323 | 0.00906 → **0.00904** |
| 1x dark standard | webgpu | 0.00404 → **0.00398** | 0.00291 → 0.00251 | 0.01326 → **0.01331** |
| 2x dark standard | webgpu | 0.00403 → **0.00400** | 0.00329 → 0.00294 | 0.01301 → **0.01317** |
| 1x light increased contrast | webgpu | 0.00793 → 0.00770 | 0.00862 → 0.00834 | 0.02042 → 0.02033 |
| 1x light reduced transparency | webgpu | 0.00172 → 0.00174 | 0.00113 → 0.00112 | 0.00341 → 0.00345 |
| 1x light standard | css | 0.00699 → 0.00708 | 0.00544 → 0.00551 | 0.01581 → 0.01575 |
| 2x light standard | css | 0.00727 → 0.00738 | 0.00563 → 0.00569 | 0.01618 → 0.01616 |
| 1x dark standard | css | 0.00682 → **0.00633** | 0.00362 → 0.00364 | 0.01732 → 0.01731 |
| 2x dark standard | css | 0.00699 → **0.00658** | 0.00401 → 0.00403 | 0.01724 → 0.01741 |

No untinted row fires S1 (worst ΔE rise **+0.00078** against +0.001; worst `ssimMean` fall
**−0.00475** against −0.005 — both inside, both close). No adopted bound is widened by this gate: it
widens none. The eleven floors and the predicate are read in §8 and re-derived at G2.

### Clause 6 — the holdout, read once

Read at this configuration and at no other, on all six profiles and both tiers, after the
calibration and validation columns. The GPU numbers are in the table above: light **0.00914 →
0.00909** (1x) and **0.00906 → 0.00904** (2x), dark **0.01326 → 0.01331** (1x) and **0.01301 →
0.01317** (2x). `g1-digests.txt` carries a sha256 for every one of the 229 captures and both profile
documents' file digests (`1858a8fb65b8…` light, `2c27b98a79cd…` dark); G2 reproduces them.

### Clause 7 — the goldens, attributable

`goldens-attribution.txt`. Every scene rendered twice through the isolation proof's own profile
seam, once with the rim's five constants set back to what they were before this gate and once as
shipped. **Not one pixel outside a contour band moved, on any scene** — the largest delta outside a
band is 0 on all eleven. Inside the band: `field-mask` 80 (2 392 px), `tint-adaptation-dark` 48,
`rim-two-references` 37, `union-pair` 37, `concentric-nesting` 35, `placed-checkerboard` 32,
`lens-size-scaling` 32, `refraction-checkerboard` 31, `body-ramp-1x` 21, `tint-adaptation-light` 8,
and the new `collapsed-tone` 130. `highlight-press-glow` is the control and moved **0 pixels**: it
captures the highlight canvas and the ambient rim is the optics pass's.

Ten goldens are re-recorded under `W23_HASHES` and one is new; `PLACED_CHECKERBOARD_COVER_HASH`
moves with them for the same reason it did at W22. The suite is **31 / 31** at the re-recorded
values. **S4 does not fire.**

### Clause 8 — the CSS tier derives, and every mover is explained

`byte-identity.txt`, every capture on both tiers against the canonical W22 bed:

| tier | moved | identical |
| --- | --- | --- |
| webgpu, render | 115 | 0 |
| webgpu, alpha | 115 | 0 |
| css, render | 107 | **8** |
| css, alpha | 106 | **9** |

Every GPU capture moves, which is the law. Every CSS capture moves **except the increased-contrast
profile's**, and that exception is the explanation: under `border: "strong"` this tier substitutes
`STRONG_BORDER`'s own width and alpha for the rim, so the law does not reach it and the captures are
byte-identical. The CSS movers are the amplitude law arriving through `adaptedSourceOptics`, the
re-based `borderAlphaPerRimAlpha`, the collapsed rims through the same seam, and
`interiorBandLight`'s derived interior level taking the law's amplitude. **S6 does not fire**: no CSS
capture moved without one of those four reasons.

## 7. The `rimLuma` feed, verified (Decision Log 2 (f))

`rim-feed.ts` reads the tone `scene.ts` publishes for every group of every scene, on both beds at
both scales; `rim-feed.txt` is the table. **42 groups per bed, none absent, none exactly 0**, with
linear means spanning 0.00375 (`impulse`) to 0.89097 (`light-solid`). G0's gap 5 — "`toneColour.w`
is 0 in the golden harness and appears to be 0 for at least some calibration groups" — resolves in
two halves: it was 0 in the GOLDEN harness, which no scene fed and which `collapsed-tone` now feeds,
and it is a real measured level on every calibration group. The law's input is the tint shade's own
quantity by construction, and since this gate it is the MATERIAL's composite rather than the painted
one, so the rim and the shade read the same level on an untinted surface and the rim reads the level
under the paint on a painted one.

## 8. The gate over the scratch matrix, and what G2 re-derives

`adopted-thresholds.test.ts` with `VITREA_MATRIX_PATH` on this gate's matrix: **24 of 33 pass, 9
fail, and all nine are the machine's own bookkeeping moving** (`g1-gate.txt`). No adopted bound is
breached; what moved is which cells the conditioning predicate admits.

`PREDICATE_EXCLUDES` re-derives **29 → 27**. Four cells the predicate used to refuse are now
well-conditioned:

```
dom / calibration / dark-solid__rrect-md__rest        / apple-macos-26.5-1x-dark-standard
dom / calibration / dark-solid__rrect-md__rest        / apple-macos-26.5-2x-dark-standard
dom / holdout     / checkerboard__glass-over-glass__rest / apple-macos-26.5-1x-dark-standard
dom / holdout     / hc-text__capsule-button__rest     / apple-macos-26.5-2x-light-standard
```

and two are newly refused:

```
texture / calibration / dark-solid__capsule-button__rest / apple-macos-26.5-2x-dark-standard
texture / calibration / dark-solid__capsule-button__rest / apple-macos-26.5-2x-light-standard
```

Both directions are the same mechanism and it is the one the wave's Risks named: **a rim on a
surface that drew nothing changes the web silhouette.** The dark CSS cells gained a border where
they had none and became conditionable; the collapsed 2x capsule gained a rim around a body that is
its own backdrop, and a silhouette that is a thin ring is what the predicate refuses. The cell
counts move with them (`TEXTURE_TIER_2X_LIGHT` 35 → 36 shape cells, `DOM_TIER_2X_LIGHT` 33 → 34) and
so do the coherence rows' `noShape` lists. Re-derived at G2 as the wave assigns, not edited here.

## 9. The stops, dispositioned

| stop | verdict | number |
| --- | --- | --- |
| S1 — untinted row worse by 0.001 ΔE / 0.005 ssim | **does not fire** | worst +0.00078 and −0.00475, 0 rows |
| S2 — a tinted cell's body moved by more than 0.002 | **FIRES, on two CSS rows** | +0.00350 / +0.00354 |
| S3 — calibration ΔE mean above the bed's by 0.0001 | **fires on the CSS tier at the fifth decimal** | 2x light CSS +0.00011 |
| S4 — a golden moved for a reason but the rim | does not fire | 0 pixels outside any band |
| S5 — a fitted constant whose rows do not separate it | does not fire, and it refused one mechanism | see §1 |
| S6 — a CSS capture moved without an explanation | does not fire | 4 named reasons, 8 identical |
| S7 — a collapsed cell's body moved by more than 0.002 | does not fire | worst 0.00004 |
| S8 — the user's eye | **the user's** | `sheets/g1-1x.png`, `sheets/g1-2x.png` |

**S2, in full.** `photo__capsule-button__rest-tint-orange-half` on the CSS tier at both scales:
body 0.45293 → 0.45643 (1x) and 0.45342 → 0.45697 (2x), +0.0035 against a bound of 0.002. One cell
of the bed, on one tier, and it is the only tinted cell whose body could move: at an author strength
of 0.5 the material shows through the paint, and this tier's derived interior level carries
`interiorBandLight`'s band term, which took the law's amplitude in this gate. Every tinted cell at
strength 1 is byte-stable in body, and no GPU tinted body moves at all. It is the mechanism S2 was
written to catch working exactly as intended — the band's light is part of the derived level and the
band got brighter — rather than the rim reaching into an interior it should not. **Recorded as
fired, and the parent's to accept or refuse.**

**S3, in full.** On the GPU tier — the tier clause 5 is stated on — every calibration mean improves.
On the CSS tier the light-standard means rise by +0.00010 (1x) and +0.00011 (2x), the second of
which is 0.00001 over the stop. The same shape as W22 G1's own "one stop fires at the sixth
decimal". The CSS tier's rim is the term that moved and §5 records what it is short of.

## 10. What the parent must decide

1. **Clause 4 does not close** and cannot be closed by this law: on the straight span the rim
   matches (contour −0.007 on `dark-solid__rrect-md`), and over the whole side including the corner
   arcs the band peak overshoots by +0.031 at 1x and +0.088 at 2x, with 47 sides leaving W22's
   bound. Either the clause is restated on the straight span, or the rim in the corners is named
   work. The numbers for both readings are on the record and neither is rewritten.
2. **Clause 3 misses on 24 of 88 structured sides**, almost all left/right, where the reference's
   own two sides split by 2.4× on a cell whose top and bottom agree to 0.002. The bed improves from
   68 sides over the bound to 24 and from 0.0886 to 0.0420 mean.
3. **S2 fires on one CSS cell** at +0.0035 for a named and intended reason (§9).
4. **S3 fires on the CSS tier at +0.00011** against 0.0001 (§9).
5. **`borderAlphaPerRimAlpha` was re-based and not refitted** (§5). The contour read can fit this
   tier's border and the fixtures' ΔE cannot; the numbers are in the tracker.
6. **The eye, S8** — the sheets.
