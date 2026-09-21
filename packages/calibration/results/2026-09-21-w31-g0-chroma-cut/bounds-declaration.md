# W31 G0 — the declarations, before any leaf exists

Acceptance clause 3; claims §5.161 §7. Every number here is declared **before**
the operator is written and is judged on evidence already in this directory:
`cut.md` and `cut.json` (the statistic over the whole chroma bed),
`reproduction-check.md` (the re-capture's fidelity to the committed rows),
`decompose-p95.txt` (the four claimed rows split into their luma and chroma
parts), `mask-adequacy.txt` (whether the dark bed's refused masks can carry the
statistic) and `css-ceiling.txt` (what the derived tier's two layers can reach).

## (a) The macOS 27 adopted tables do not move, and no floor is pinned

The tables `packages/calibration/test/adopted-thresholds.test.ts` holds for the
six macOS 27 profiles stay at the values W30 G4 left them at, digit for digit;
they are cited, never transcribed. `MISSED_27_ROWS`'s seven entries stay as
recorded. **No regression floor is pinned by this wave**, and none should be: a
floor is the instrument for a row a fix cannot reach, and §4 below shows the
four rows this wave claims are reachable by three times over.

## (b) The chroma tolerance

### The statistic

    R = chromaStructureRatioWeb / chromaStructureRatioNative

— ratio (i), the chroma-to-structure ratio of the masked interior, **web
against native on the same cell**. Never against 1, and never against the
backdrop: the reference is the only thing that says what this material should
do, and a ratio against the backdrop would be ratio (ii), in which the blur does
not cancel.

### The bed

The **untinted `photo` cells of the four macOS 27 standard profiles**, both
scales, `calibration` + `validation`, on the **WebGPU (`texture`) tier**, with
the two poses bounded separately because they draw two different documents:

| scheme | pose | cells | which |
| --- | --- | ---: | --- |
| light | active | 10 | `capsule-button`, `rrect-md`, `rrect-ml` (calibration); `rrect-sm`, `toolbar-group` (validation); × 1x, 2x |
| light | inactive | 8 | `capsule-button`, `rrect-md` (calibration); `rrect-sm`, `toolbar-group` (validation); × 1x, 2x |
| dark | active | 4 | `capsule-button`, `rrect-md` (calibration); × 1x, 2x |
| dark | inactive | 4 | `capsule-button`, `rrect-md` (calibration); × 1x, 2x |

The holdout cells (`rrect-lg`, `glass-over-glass`) are **excluded by
construction**, which is the point of naming the bed by set rather than by
scene.

**Every dark cell in this bed fails the conditioning predicate, and it is used
anyway, on evidence.** Not three cells as the charter's Grounding says —
*every* untinted `photo` cell of both dark macOS 27 profiles, in both poses, at
both scales, on both tiers. The refusal is an area-and-bodies refusal of the
SHAPE axis: over a dark body the luminance-delta rule loses the pixels where the
material's own level meets the backdrop's, so the reference silhouette comes
back a few per cent short and perforated. `mask-adequacy.txt` answers whether
that reaches this axis by computing the statistic twice per cell, once under the
silhouette and once under the **declared region**, which is complete by
construction and hole-free:

| cell | R under the silhouette | R under the declared region |
| --- | ---: | ---: |
| 1x dark `photo__capsule-button__rest` | 0.294 | 0.300 |
| 1x dark `photo__rrect-md__rest` | 0.315 | 0.314 |
| 1x dark `photo__rrect-lg__rest` | 0.393 | 0.394 |
| 1x dark `photo__rrect-md__inactive` | 0.512 | 0.507 |
| 2x dark `photo__rrect-md__rest` | 0.361 | 0.364 |
| 2x dark `photo__rrect-lg__rest` | 0.430 | 0.430 |

The two masks agree to **0.006 at worst** on R and to 0.001 on ratio (ii), on
cells whose masks differ by up to 4,400 px and 131 holes. The pixels the rule
drops are not a chromatically biased sample of the interior, so the shape axis's
refusal does not reach the chroma axis. **Declared: the tolerance is read under
the native silhouette, as every other material row is, and the refused cells are
in the bed.**

### The order statistic, and the bound

**Median of R over the bed, per scheme and per pose, with a per-cell floor.**

| | bound on the median | per-cell floor | today |
| --- | --- | --- | --- |
| light active | `0.80 ≤ median R ≤ 1.20` | every cell `R ≥ 0.60` | median **0.551**, range 0.509–0.653 |
| light inactive | `0.80 ≤ median R ≤ 1.20` | every cell `R ≥ 0.60` | median **0.514**, range 0.489–0.652 |
| dark active | `0.80 ≤ median R ≤ 1.20` | every cell `R ≥ 0.60` | median **0.333**, range 0.294–0.361 |
| dark inactive | `0.80 ≤ median R ≤ 1.20` | every cell `R ≥ 0.60` | median **0.584**, range 0.495–0.658 |

A median rather than a mean because the bed is 10 and 4 cells and `rrect-sm`'s
32 px span puts a rim band inside the interior mask, which pulls a mean; a
per-cell floor beside it so one cell cannot be traded away for the centre.
Two-sided, because an over-fitted retention adds chroma the reference does not
have, and 1.20 is as much a miss as 0.80.

### The noise bar the width is justified from

The instrument's own reproducibility, measured as the **1x-against-2x spread of
R on this bed's own cells** — the same material, the same scene and the same
document, read at two rasters, which is the only repeat this frozen bed offers:

| scheme | pairs | median | worst |
| --- | ---: | ---: | ---: |
| light | 9 | 4.49 % | 7.66 % (`rrect-sm__inactive`) |
| dark | 4 | 9.09 % | **19.41 %** (`capsule-button__rest`) |

±0.20 about 1.0 is a little over the dark bed's worst single-cell
reproducibility and about four times its median; the median over four or ten
cells is tighter than any single one. Against that, the residual the bound has
to detect is **0.45 (light) and 0.67 (dark) away from 1.0** — between 2.2 and
3.3 times the bound's own half-width. A bound a material misses by three times
its width is not a bound that gets met by accident.

The dark bed's 19.41 % is not capture noise. It is on `capsule-button__rest`,
the cell with the largest level miss in the bed (|Δ| 0.0493), and ratio (i)
scales as `(level)^(−2/3)` exactly (`metrics/chroma.ts`): that cell's level
alone biases R by 1.178. **The level stop in §(c) is what removes it**, and
after the fit the noise bar should read closer to the light bed's.

### Two stops without which the tolerance is gameable, declared with it

**The level stop is in §(c).** Without it R can be met by moving the level: the
exponent is `−2/3` and exact.

**The structure stop, and it is this child's addition.** Ratio (i) is
scale-free in the deviations, which is what makes the blur cancel — and it is
therefore equally blind to a body that loses chroma and structure *together*.
The CSS tier is the proof that this is not hypothetical rather than a worry:
on the dark photo cells it reads `R` 0.83–1.08, essentially the reference's
value, while ratio (ii) reads 0.18–0.24 against the reference's 0.90 and `eye.md`
records a body with no hues in it at all. So:

> **Declared: `interiorStdDevWeb` moves by no more than 2 % of its pre-fit value
> on any cell of the tolerance's bed.** Relative rather than absolute because
> the bed's values span 0.009 to 0.09. This is X3 restated as a number — the
> structure rows are expected unmoved and the analysis pass is deferred — and
> without it R is not a sufficient statistic.

### Its fate: the identifiability argument, and it CAN be made

A chroma row adopted at G4 would be the **first adopted row on the material
axis**, whose absence `adopted-thresholds.test.ts`'s own header argues for: the
material sub-metrics are "either unidentifiable on this fixture set (blur sigma)
or below the capture's own quantisation (the light-scheme rim)". The argument
for this row is that it is neither, and each half is a number:

1. **Not below quantisation.** The statistic's numerator is an OKLab chroma
   spread of 0.02–0.11 on this bed. An 8-bit capture's quantisation in OKLab is
   about 0.002 at these levels — one to two orders of magnitude down. The
   re-capture makes this concrete rather than analytic: **all 552 macOS 27 cells
   reproduce their committed `interiorMeanWeb` and `ssimMean` to |Δ| exactly 0**
   (`reproduction-check.md`), so there is no capture noise on this bed at all,
   and the only spread the statistic carries is the 4.5 % / 9.1 % across
   rasters that the bound is five times wider than.
2. **Not unidentifiable.** The native side separates by geometry over a range of
   1.47× (light) and 1.69× (dark) and the web side tracks it cell for cell; the
   web-against-native ratio is 0.55 and 0.33 against a reference 1.0. The
   quantity a fit would move is 3× the bound's half-width and 7× the
   instrument's own reproducibility. A threshold on a quantity the fixtures
   cannot resolve is a number that gets met by accident; this one is missed
   today by more than it could ever be met by chance.

**Two conditions the parent should attach if it adopts.** (i) The row is
adopted **with the structure stop as a second gated row**, because R alone is
insufficient by the CSS tier's own reading above. (ii) It is adopted on the
**WebGPU tier only**. The CSS tier's R is near 1.0 today with no chroma
operator anywhere in the renderer, so on that tier the statistic says nothing
and gating it would certify the gap — Decision Log 11's refusal, one axis over.

Absent those two, the honest disposition is **a one-wave reading**, and G0
recommends adoption with them rather than without.

### The CSS tier: recorded, not bounded

Its readings are in `cut.md` for every cell. Its analytic ceiling is §(g).

## (c) The level stop, as a number

There is no adopted interior-level row to cite — `interiorLevelRatioGpuOverCss`
is a cross-tier ratio and is blind to both tiers moving together — so this is
declared here and read before and after on scratch by G3.

> **Per cell of the tolerance's bed, on both tiers:**
>
> 1. `|interiorMeanWeb − interiorMeanNative| ≤ 0.055` in linear relative
>    luminance, and
> 2. that quantity **grows by no more than 0.005** from its pre-fit value.

Clause 2 is the operative one and clause 1 is the ceiling. The retention is
luma-preserving in linear luma **by construction** (§(e)), so the expected
movement is zero to floating-point rounding and 0.005 is a hundredfold margin
on that expectation. Today's worst on the bed is **0.0493** (1x dark
`photo__capsule-button__rest`, native 0.2254 against 0.1790) and the median is
0.0053 (light) and 0.0360 (dark); 0.055 is the worst cell rounded up, so clause
1 is met today by every cell and would be broken only by a fit that made the
level worse than the wave found it.

## (d) The four claimed rows: all four CLAIMED, and the lever is the chroma

`oklabDeltaEP95` is a Euclidean norm of two independent parts,
`ΔE² = ΔL² + Δc²`. A luma-preserving chroma operator moves `Δc` and cannot move
`ΔL`, so the best it can do is drive `Δc` to zero everywhere, leaving
`ΔE = |ΔL|`; the P95 of `|ΔL|` over the same population is therefore the row's
**reachable floor**. `decompose-p95.txt`:

| row | bound | committed | scratch | chroma share of ΔE² at the P95 pixels | reachable floor | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `texture / holdout / photo__rrect-lg__rest / 27.0-1x-dark` | ≤ 0.17 | 0.21531 | 0.21530 | 91.4 % | **0.06309** | **CLAIMED** |
| `texture / holdout / photo__rrect-lg__rest / 27.0-2x-dark` | ≤ 0.17 | 0.21341 | 0.21341 | 92.7 % | **0.06201** | **CLAIMED** |
| `dom / holdout / photo__rrect-lg__rest / 27.0-1x-dark` | ≤ 0.18 | 0.20095 | 0.20095 | 90.8 % | **0.06631** | **CLAIMED** |
| `dom / holdout / photo__rrect-lg__rest / 27.0-2x-dark` | ≤ 0.19 | 0.19474 | 0.19474 | 91.1 % | **0.06424** | **CLAIMED** |

Every one of the four is claimed, and the margin is not marginal: the floor sits
at a **third of the tightest bound**. The residual is 90–93 % chromatic by
energy at the pixels that set the P95, and the split by region says it is
interior-wide rather than a rim finding — `interior` 43,148 px reads ΔE P95
0.220 against `rim`'s 0.213 and `exterior`'s **0.0037**. The chroma share is
*highest* in the rim band (96.5 %), which is the one place a shape or shadow
defect would have shown up as luma, and it does not.

Stated as the claim rather than as the arithmetic: **none of these four rows
needs a perfect retention.** Closing the bound needs `Δc` at the P95 reduced
from 0.208 to about 0.158 on the tightest row — roughly a quarter of the
chromatic residual — which is well inside what R = 0.80 asks for.

**What the fit is judged on BEFORE the holdout is read.** All four are holdout
rows and the holdout is read once per configuration (Decision Log 1 (b)), so
the fit is judged on the **gated `photo` cells of `calibration` + `validation`**
— the tolerance's bed in §(b), the level stop in §(c) and the structure stop —
and the four rows are read once, at G3's canonical read, as a result and not as
an objective.

**The CSS tier's two rows carry one extra condition.** Their floors (0.0663,
0.0642) are as reachable as the WebGPU tier's, but only if the CSS tier carries
some of the operator; §(g)'s dark ceiling is 0.278 against a reference ratio (ii)
of 0.90, so the dom rows are claimed **conditionally on G3 deriving a term for
that tier**. If G3 declines the CSS projection, the two `dom` rows revert to
"reachable if the CSS tier carries a chroma term", and that is the wording the
ledger should carry until G3 decides.

## (e) The mechanism, and the one leaf

Stated in full in claims §5.161 §5 and summarised here because the bounds above
are bounds on it.

**Where the chroma is lost: the plate's alpha, and nothing else.** The composite
is `colour = mix(backdrop, adapted, presentAlpha)` in linear light with
`adapted` a neutral, so the backdrop's chromaticity survives scaled by
`1 − sizedAlpha`. On the macOS 27 dark document at span ≥ 96 that is **0.0950**
(`mechanism.txt`), and the measured ratio (ii) on the dark ACTIVE photo cells is
**0.106–0.119**. The two agree to within the lens and the scatter. The light
document's `1 − sizedAlpha` is **0.5130** and its measured ratio (ii) on the WebGPU tier is
0.25–0.32 — the light body loses chroma beyond the plate as well, which is what
ratio (iii) reads directly (0.34–0.47 against a blurred reference).

**The leaf.** `bodyChromaRetention ∈ [0, 1]`, inert identity **0**, applied
immediately after the composite and before `var materialColour = colour`:

    let Y  = dot(colour, W);                      // the luma the W9 solve produced
    let Yb = dot(backdrop, W);
    let target = backdrop * (Y / max(Yb, 1e-6));  // the backdrop's chromaticity AT Y
    var restored = mix(colour, target, bodyChromaRetention);
    restored = restored * (Y / max(dot(restored, W), 1e-6));   // a rounding guard
    colour = gamut_at_luma(restored, Y);

**Luma preservation is by construction, not by correction.** Both endpoints of
the mix have linear luma exactly `Y` — `colour` by definition and `target`
because it is the backdrop scaled to `Y` — and linear luma is a linear
functional, so the mix has luma `Y` in exact arithmetic. The renormalisation is
an f32 rounding guard and the identity otherwise. This is why the formulation
works in linear RGB rather than in OKLab: the charter's Design warns that
holding OKLab `L` while moving toward a saturated chromaticity changes `Y` by
−22 % at sRGB blue, −14 % at red and +10 % at green, and none of that arises
here because `L` is never held.

**Gamut, with the luma held and never clipped per channel.**
`gamut_at_luma(c, Y)` is `mix(vec3f(Y), c, t)` with `t` the largest value in
[0, 1] keeping every channel in [0, 1] — `t ≤ (1 − Y)/(cᵢ − Y)` where a channel
overshoots and `t ≤ Y/(Y − cᵢ)` where one undershoots. Both endpoints again have
luma `Y`, so the clamp scales chroma down and holds the level exactly.

**The `toneAdapt` gate: none, and the reason is a measurement.** Both macOS 27
documents set `backdropToneLow` 0 and `backdropToneHigh` 0.0001 against a
`backdropToneSizeBias` of 0.05, so the smoothstep saturates at every backdrop
and every span and `toneAdapt` is **identically 0 on the macOS 27 material**
(`mechanism.txt` evaluates it at ten backdrop levels from 0 to 0.9 and reads
0.00000000 at every one). `1 − toneAdapt` is the constant 1 over the entire
macOS 27 bed, so a gate on it is a multiplier by one that no cell can move — an
unmeasurable leaf. On the frozen macOS 26.5 documents the collapse does fire,
and there the retention sits at its identity 0 and the gate would never be
exercised either. **Recorded as a condition rather than dismissed:** a future
document that re-opens `backdropToneHigh` must re-examine whether the retention
needs standing down where the collapse owns the pixel. Tracker at G4.

**The receded documents carry their own value**, read on the inactive photo
cells — `photo__capsule-button__inactive` and `photo__rrect-md__inactive` on
calibration, at both scales, in both schemes. They need one: the dark inactive
bed reads R 0.495–0.658 against the dark active bed's 0.294–0.361, so the two
poses are not one number.

**The tint path is unmoved by construction on a fully tinted pixel, and by
arithmetic elsewhere.** The tint's shade law reads `u`, the untinted material's
LUMINANCE, which the retention preserves exactly — so `shade`, `layer` and
`rimTintColour` are bit-identical. The composition
`mix(encodedMaterial, encodedLayer, s)` moves by `(1 − s)·Δ(encodedMaterial)`:
**exactly zero at full strength** and half the body's change at
`tint-orange-half`. The rim's amplitude law reads `materialColour`'s luminance
and is likewise unmoved. So the tinted rows are expected unmoved **by
construction at `s = 1` and by measurement at `s = 0.5`**, which is a stronger
statement than "by fit" and is checkable before the fit.

**One place the retention cannot act, named now.** On the unsampled layer path
(`flags.x <= 0.5` and not `domMaterial`) the shader overwrites `colour` with
`adapted` and writes a layer for the browser to composite over a DOM proxy;
there is no backdrop in hand and no chromaticity to restore toward. The
retention is silently the identity there, which is correct and is also a
declared residual: an unsampled group on the WebGPU tier carries none of this
operator.

## (f) Two collapses, told apart

The **backdrop tone collapse** (`toneAdapt`, `adapted` toward `toneTarget`) acts
on every body and is identically 0 on macOS 27, as above.

**W27c's chroma collapse** (`tintChromaScale` through `ou.rim.z`) lives inside
`if (tintK > 0.0)` and acts on the tint SEED. An untinted body — including every
untinted receded body, the recede's worst cell's population — passes it with
`tintK = 0` and has **no chroma law at all today**. The two are different
mechanisms on different populations and this wave touches neither.

**A finding beside it, outside this wave's scope and recorded rather than
carried.** On the RECEDED TINTED photo cells vitrea's body has essentially no
chroma left: ratio (ii) reads **0.001–0.006** against the reference's 0.54–0.65
(`cut.md`, `photo__capsule-button__inactive-tint-orange` and siblings), while
the ACTIVE tinted cells match the reference almost exactly (1.433 against 1.435
on `capsule-button__rest-tint-orange`). That is W27c's seed collapse driving the
paint to neutral where Apple's receded material keeps it. It is a tint-path
defect, not a body-chroma one; X3 freezes the tint's chroma law here, so it
goes to the tracker.

## (g) The CSS projection: the ceiling per scheme, as a declared residual

`saturate()` acts on the backdrop inside the one `backdrop-filter` and the
`rgba()` plate covers the result, so the interior chroma the tier can reach is
bounded by `(1 − α′)·s` with `s` = 1.8 (regular, frozen by X3) and `α′` the
CONVERTED alpha `cssTintAlpha` solves at the surface's own measured backdrop
(`css-ceiling.txt`):

| scheme | α′ at the photo backdrop | ceiling on ratio (ii) | the reference's ratio (ii) | today's tier |
| --- | ---: | ---: | ---: | ---: |
| light | 0.5642 | **0.784** | 0.72–0.86 | 0.40–0.63 |
| dark | 0.8456 | **0.278** | 0.90–0.92 | 0.18–0.24 |

**Declared residual.** The light tier's ceiling sits essentially AT the
reference's own reading with no headroom to spare — a derived term is worth
adding there and can in principle close the gap. The dark tier's ceiling is
**0.278 against a reference 0.906**, so the dark CSS tier can carry at most
**31 %** of the reference's body chroma however it is derived, and a residual of
about 0.63 in ratio (ii) is unclosable on that tier without moving `saturate()`
— which X3 forbids and which would be a CSS-only constant fitted to a renderer
operator in any case.

**G0's recommendation to G3, which G3 may decline with a measurement.** Derive
the term on the light scheme and record the dark scheme's ceiling as the
residual; do not spend `saturate()`. Whichever it does, `tier-coherence.test.ts`
gains the exhaustiveness case so that green says something about a new leaf.

**One reading that complicates it and is recorded rather than smoothed.** On
`mid-chroma-solid` the CSS tier is already CLOSER to the reference than the
WebGPU tier is, by eye and by ratio (ii) (0.484 against 0.352 at 1x light
`capsule-button__rest`, reference 0.802). The fidelity target is behind its own
derived tier on that cell, which is what a CSS-only `saturate()` with no
renderer counterpart produces.

## (h) The expected-unmoved rows, and the stops

- **The shadow.** No `shadow` axis row moves. B3's stop is restated as declared
  in W30 Decision Log 3 (a): the **WebGPU tier's mean absolute exterior
  departure over the non-holdout cells of all six profiles, 0.00035, held at or
  better**, with the both-tier figure recorded beside. The retention acts inside
  the body composite and reaches no exterior pixel, so any movement here is a
  warning and not a result (X3).
- **The scatter and the structure rows.** `interiorStdDev*` and every
  `blurSigma*` row: unmoved, to the structure stop in §(b).
- **The tinted cells.** Unmoved at `s = 1` by construction; read before and
  after at `s = 0.5`.
- **The rim.** `rimPeakLuminance*`, `rimPeakDistance*`, `rimFwhm*`: unmoved.
  The rim's amplitude law reads `materialColour`'s LUMINANCE, which the
  retention preserves exactly.
- **The light document's value may be declined, and a decline is a
  measurement.** The light bed reads R 0.551 against the dark bed's 0.333 — the
  light scheme carries the residual and a decline there is unlikely — but if the
  fit lands at zero it is recorded as W30 recorded the light scatter, and an
  explicit identity reads as absent in the digest under Decision Log 1 (a).

## (i) The recede's worst cell (W29 §5.154 §8), reported

`photo__rrect-lg__rest`'s inactive pose is the recede's worst cell on every row.
Today, WebGPU tier, macOS 27 dark:

| | 1x | 2x |
| --- | ---: | ---: |
| R (ratio (i), web / native) | 0.537 | 0.514 |
| ratio (ii), native / web | 0.923 / 0.127 | 0.920 / 0.132 |
| `interiorMean` native / web | 0.1708 / 0.1606 | 0.1705 / 0.1608 |

It is not in the tolerance's bed — it is a holdout scene — and it is reported,
not claimed. Its population is the one W27c's chroma collapse does not reach
(§(f)), so the receded documents' own `bodyChromaRetention` is the first chroma
law this cell will ever have had.

## (j) One thing this child did NOT do

It did not read `--set holdout` as a verdict. The holdout cells were
re-captured, disclosed, and used for exactly two things: the reproduction check
(where they reproduce to |Δ| 0) and the decomposition in §(d), which reads the
committed rows' own pixels rather than declaring a new number. The committed
0.20.0 holdout rows remain the reading for this configuration.
