# W23 G0 — the contour instrument, the rim read on both beds, and the law fitted on the solids

Findings, not a merge. Everything here is under
`packages/calibration/results/2026-09-08-w23-collapsed-rim/g0/`; the mechanism code sits in this
worktree behind constants that are all 0, at which every golden and every capture reproduces byte
for byte. Nothing canonical was written: no `results/matrix.json`, no `web-captures/`, no fixture,
no `scenes.json`, no committed profile document. The holdout was captured by nothing — the ladder
ran `--set calibration,validation` on every point — and the holdout cells that appear in the
whole-bed table below are READS of captures already taken at the 0.11.0 configuration, whose
holdout W22 G1 spent.

**The short version.** The rim's law is (L4): the rim is affine in the surface's OWN rendered
level, `rimAlpha + rimLevelGain × luminance(surface)`, with the gain's SIGN opposite in the two
schemes — negative in light (a white line at a fraction of the body's headroom, the screen form)
and strongly positive in dark (a line that rides its own body up). Screen alone (L2) and
screen-plus-environment (L3) are both refuted on the reference's own solid rows, and the
environment term has no row on either bed that separates it. The collapsed rim is **not** the dark
material's rim: it is +0.0189 mean against the dark material's +0.0257 over the same backdrop, nine
codes apart, and `rimCollapsed` is its own absolute constant at **0.038**.

---

## (a) The instrument — `read-contour.py`, validated

`instrument.txt` carries the three validations; `read-contour.py`'s module doc carries the
definitions. The reader is W21's body (the declared box eroded 6 CSS px, linear Rec.709) with the
rim read at the contour: per side, the excess of each row or column over a base, summed over the
first two CSS px inside the declared box's edge and divided by the scale — one linear number per
side per CSS px, exactly `finding/contour-table.txt`'s units — plus the first row's own excess and
the reference's clip fraction.

Two things the spec did not name, both forced by the pixels and both recorded rather than assumed:

**The straight span needs 1.6 radii excluded, not 1.** Apple's rounded rectangle has a continuous
corner: on `dark-solid__rrect-md` at 1x the first contour row is still climbing from 0.60 to 0.74
linear between `x0 + r` (100) and `x0 + 1.5r` (110). Read at factor 1 that cell's rim is 0.2141; at
1.3, 0.2262; at 1.5, 0.2291; at **1.6, 0.2293**; at 2.0, 0.2297. The read converges by 1.5 on every
rrect and is flat on every capsule at every factor (a capsule's ends are true semicircles), so 1.6
is taken with a margin and still leaves 96 of 160 CSS px of span on `rrect-md`.

**A second excess is reported beside the first.** `rim` is the excess over the whole eroded body —
the wave's binding definition — and `rimLocal` is the excess over the side's OWN rows from 2 to
4 CSS px in. Over a solid backdrop they agree to a few ten-thousandths. Over a structured one they
do not, because the material passes the backdrop's structure and the level under one side's contour
is not the level averaged over the interior. On `photo__rrect-md` at 1x the reference's four sides
read +0.106 / +0.126 / +0.157 / +0.234 against the body and +0.150 / +0.151 / +0.147 / +0.060
against their own bases (0.639 / 0.649 / 0.666 / 0.748 against a body of 0.661): almost the whole
apparent per-side spread is the photograph, and it collapses when each side is read against what is
actually under it. **Every fit and every check in (d) is on `rimLocal`**, and both are printed
on every row of `contour-read.txt` so the difference is never hidden inside a verdict. This is the
spec's own instruction ("reading the structured cells' contour base from the reference's own
neighbouring rows before ruling L1 out") made into a column.

### The validations

**Injection.** A synthetic line of known linear amplitude, one CSS px deep (not one device pixel —
the reader's unit is per CSS px and a device-pixel line at 2x would test only the divisor), painted
along every straight span of a real capture. Unquantised the reader returns it **exactly**:
`|error| 0.000000000` on every side of all seven cases, against a bound of 1e-6. Re-quantised to
the bed's 8 bits it returns it to within **0.11…0.65 of one code** — 0.0025 linear on a mid-grey
body, 0.00027 on the dark bed's collapsed capsule.

> **A clause of the spec is wrong on the evidence, and here is the number.** The Design says the
> injection must read back "within 0.001". That is achievable on the dark bed (one code at a body of
> 0.011 is 0.00067) and is not achievable *at all* on a mid-grey body, where one 8-bit code is
> 0.0059 of linear luminance: the worst 8-bit injection error measured is 0.0025, which is 0.42 of a
> code and cannot be improved by any reader. The instrument's real bound is **exact in float and
> under one code at 8 bits**, and every verdict below is quoted against the code size at that
> cell's own level. The clause should be restated that way; the reader is not at fault.

**Clipping is a declared limit, not an error.** On `light-solid` the reference's contour row is 255
in all three channels across the whole span (`clip` 1.00), and an injected line there reads back 0
because the raster cannot carry it. Clipped sides are excluded from the injection bound and flagged
in every table.

**Cross-check against the parent's `contour-profile.py`.** On every SOLID row the two readers agree
to 0.0021 or better (0.4 of a code): `dark-solid__rrect-md` 0.2293 against 0.2310, `light-solid__rrect-md`
0.1002 against 0.1002, `dark-solid__capsule-button` 0.0200 against 0.0201, `mid-dark-solid__capsule-button`
0.2421 against 0.2425. On the STRUCTURED rows they diverge by up to 0.027 (`photo__rrect-md` 0.1056
against 0.1323), and that divergence is the point: the parent's reader averaged a fixed 20-CSS-px
window at the cell's centre, which on a photograph inherits whatever sits under it, while this one
averages the whole straight span. The span read is the one to believe there.

---

## (b) The read — `contour-read.txt`

Every cell of all six committed profiles at both tiers, native against the LANDED 0.11.0 captures
(matrix `3587400`), per side, with the `rimLocal` table beside; then W21's dark probe grid and W9's
light probe grid, both read the same way. W22's band read (`read.py`) runs beside it into
`reads/band-*.json` so W22 clause 2 can be re-checked on its own instrument without re-deriving it.
Tinted cells are in the tables as context and are fitted by nothing.

The rows that carry the wave (linear, per CSS px, top side unless stated):

| bed | cell | body ref | body web | rim ref | rim web |
| --- | --- | --- | --- | --- | --- |
| light 1x | `dark-solid__rrect-md` | 0.4798 | 0.4955 | +0.2293 | +0.0593 |
| light 1x | `impulse__rrect-md` (val) | 0.4311 | 0.4642 | +0.2400 | +0.0613 |
| light 1x | `mid-dark-solid__capsule-button` (holdout) | 0.4399 | 0.4563 | +0.2421 | +0.0715 |
| light 1x | `light-solid__rrect-md` (both clip) | 0.9345 | 0.9317 | +0.1002 | +0.0593 |
| light 2x | `dark-solid__rrect-md` | 0.4798 | 0.4955 | +0.2052 | +0.0692 |
| dark 1x | `dark-solid__rrect-md` | 0.0153 | 0.0130 | +0.0256 | +0.0367 |
| dark 1x | `mid-dark-solid__capsule-button` (holdout) | 0.0285 | 0.0285 | +0.0410 | +0.0362 |
| dark 1x/2x | `dark-solid__capsule-button` (collapsed) | 0.0110 | 0.0117 | +0.0201/+0.0204 | 0.0000 |
| probe W21 (dark) | `light-solid__rrect-md` | 0.0960 | — | +0.1032 | — |
| probe W9 (light) | `mid-dark-solid__rrect-lg` | 0.5841 | — | +0.2006 | — |

The probe grids are what make this wave fittable at all — see (d).

---

## (c) The collapsed rim — `collapsed.txt`

**Which cells are collapsed, from the pixels.** On the canonical beds, the cells whose landed GPU
capture has a contour rim of exactly 0 on every side: `dark-solid__capsule-button` and
`impulse__capsule-button`, in BOTH schemes, at BOTH scales. On the probe grids, where the reference's
body sits within a code of its own dark backdrop: `dark-solid__rrect-sm` (both grids) and
`dark-solid__rrect-lg` (W21's dark grid).

> **A surprise for the parent's Surprises list.** In W21's dark probe grid `dark-solid__rrect-sm`
> and `dark-solid__rrect-lg` both draw the collapsed appearance (body 0.0110, rim +0.0201 / +0.0196)
> while `dark-solid__rrect-md` between them does NOT (body 0.0153, rim +0.0256). A size law that
> collapses the small and the large surface and not the middle one is not a size law. It is on the
> record here and read by nothing in this wave.

**The reference's collapsed rim.** Over 11 cells and 28 sides: mean **+0.0189**, min +0.0149,
max +0.0204, spread 0.0056. The spread is not noise — it is the backdrop: over `dark-solid` the
reference reads +0.0196…+0.0204 and over `impulse` +0.0149…+0.0168, and one absolute constant draws
the same rim on both.

**Is the collapsed rim the dark material's rim? No.** The dark material's own rim over the same
backdrop, uncollapsed (`dark-solid__rrect-md` in the dark scheme, both scales, and W21's probe grid)
is +0.0256…+0.0258. The collapsed rim is **0.0068 lower** — nine 8-bit codes at that level, against
an instrument whose 8-bit resolution there is 0.00067 and whose float resolution is exact. **The two
do not agree within the read's precision, and the spec's "if the two agree, the collapsed rim IS the
dark rim" resolves to NO.** `rimCollapsed` is an absolute constant of the collapsed appearance,
expressed in its own units and not in the dark rim's.

**The value.** The ladder rendered `rimCollapsed` 0.05, which draws +0.0227 (1x) / +0.0245 (2x) on
the collapsed cells; the leverage is linear, so each row's own answer is:

| row | drawn at 0.05 | reference | that row's `rimCollapsed` |
| --- | --- | --- | --- |
| `dark-solid__capsule-button` 1x | 0.0227 | 0.0201 | 0.0441 |
| `impulse__capsule-button` 1x | 0.0226 | 0.0168 / 0.0149 | 0.0373 / 0.0330 |
| `dark-solid__capsule-button` 2x | 0.0245 | 0.0204 | 0.0418 |
| `impulse__capsule-button` 2x | 0.0245 | 0.0163 / 0.0155 | 0.0332 / 0.0317 |

The per-row answers span 0.0317…0.0441. Under S5 that spread would refuse a constant, and it does
not here for a stated reason: the rows disagree because the REFERENCE's own collapsed rim differs by
backdrop, not because the constant is unidentified. The worst residual over every collapsed side at
a chosen value:

| `rimCollapsed` | 0.035 | **0.038** | 0.040 | 0.041 | 0.043 | 0.045 |
| --- | --- | --- | --- | --- | --- | --- |
| worst \|d\| | 0.0042 | **0.0031** | 0.0041 | 0.0046 | 0.0055 | 0.0065 |

**0.038 is the recommendation** — the minimiser, and the only value quoted here that leaves every
collapsed side inside the parent's clause 1 (0.005) with margin. The rendered confirmation at 0.038
reads: collapsed sides, mean |rim − reference| **0.0180 → 0.0021**, worst **0.0201 → 0.0033** (1x)
and **0.0204 → 0.0029** (2x). Clause 1's rim half is met on every collapsed cell of both schemes at
both scales.

**The collapsed body.** Unchanged and not chased: the reference's is 0.01103 and vitrea's 0.01171
(+1.05 codes) on `dark-solid__capsule-button` at both scales in both schemes; on
`impulse__capsule-button` the reference's is 0.00664 and vitrea's 0.00367 (−6.2 codes). Clause 1's
body half (0.002) is met on the first and missed on the second by 0.0010 — inside 0.002, so met, but
the sign is worth the parent's eye: vitrea's collapsed body over `impulse` is a shade too dark
already, and `rimCollapsed` does not touch it.

**The schemes' fixtures, every scene both standard profiles declare.** The parent read two cells;
this reads all fourteen at both scales:

| scale | byte-identical across schemes |
| --- | --- |
| 1x | `dark-solid__capsule-button__rest`, `impulse__capsule-button__rest`, **`dark-solid__capsule-button__rest-tint-orange`** — 3 of 14 |
| 2x | `dark-solid__capsule-button__rest`, **`dark-solid__capsule-button__rest-tint-orange`** — 2 of 14 |

The parent's reading is confirmed and extended in one way that matters for X4: the identity survives
an AUTHOR TINT. `dark-solid__capsule-button__rest-tint-orange` is the same bytes in both schemes at
both scales, so the collapsed appearance is scheme-independent even when the author has painted it.
`impulse__capsule-button` is identical at 1x and not at 2x, exactly as the parent recorded. X4 holds:
`rimCollapsed` belongs on `DEFAULT_MATERIAL_PROFILE`, not in the dark patch.

---

## (d) The law — `fit-law.txt`, `ladder/`, `goldens-attribution.txt`

### The form, chosen on the reference before any vitrea constant

Least squares over the reference's own solid, unclipped, uncollapsed sides — 44 in light (bodies
0.4287…0.9326, from both canonical scales and W9's grid) and 36 in dark (bodies 0.0153…0.1029, from
both canonical scales and W21's grid). Mean and max |residual| in linear luminance per CSS px:

| candidate | light mae | light max | dark mae | dark max |
| --- | --- | --- | --- | --- |
| (L1) `rim = c` — additive, today's form | 0.0249 | 0.1162 | 0.0253 | 0.0601 |
| (L2) `rim = α(1 − base)` — screen | 0.0168 | 0.0666 | 0.0259 | 0.0644 |
| (L3) `rim = α(1 − base) + κ·out` — screen + environment | 0.0105 | 0.0228 | 0.0042 | 0.0090 |
| **(L4) `rim = c + m·base`** — affine in the surface's own level | **0.0081** | **0.0187** | **0.0013** | **0.0021** |
| (L4e) L4 + environment | 0.0071 | 0.0193 | 0.0010 | 0.0020 |

**L4 wins on both schemes, and the fitted constants are:**

- light: `rim = 0.3559 − 0.2752 × base`
- dark: `rim = 0.0130 + 0.9425 × base`

**L1 is refuted and the structured cells do not save it** (the spec asked for that check
explicitly). Read against each side's own local base rather than against the whole body — which is
what the spec meant by "reading the structured cells' contour base from the reference's own
neighbouring rows" — the light reference's structured rows land at 0.10…0.25 with a per-side spread
that tracks the local base, and L1's single constant misses them by 0.045 on average. The additive
form is not short by a scalar; it has no dependence on anything, and the reference's does.

**L2 is refuted by the probe grids' range.** Over the three light cells the parent read (bodies
0.43…0.48) pure screen at α 0.41…0.45 fits within 2 %, exactly as §5.99 says. Over the W9 grid's
range (0.43…0.93) it does not: the measured slope of rim against base is −0.275, and pure screen
requires it to be −α = −0.43. The two cells the canonical bed offers cannot tell the difference; the
probe grid can, and does.

**L3 is declined twice over.** It is worse than L4 on the reference in both schemes (light 0.0105
against 0.0081; dark 0.0042 against 0.0013). And on vitrea's side it has **no row that separates
it**: the ladder rendered `rimEnvGain` +0.10 on the light bed at 1x and every solid cell moved by
either exactly 0 or 0.0005. `light-solid`'s rows are already CLIPPED in the landed capture
(`clipWeb` 1.00), so a term that would brighten them cannot be measured there at all, and the dark
solids' `out` is 0.0117 or 0.0000, where +0.10 of gain buys 0.0005 of rim. Under S5 the constant is
not carried. The added constant in L4e is the same story from the other side: it earns 0.0010 of
light mae and 0.0003 of dark mae while flipping sign between the schemes (−0.032 against −0.022),
which is a constant fitting noise.

### The constants, solved on vitrea's own captures

The shader's rim is linear in each constant, so on a cell the reading is
`W × rimAlpha + (W × L) × rimLevelGain` where `W` is that cell's band weight — the band integral over
the first two CSS px, carrying the tone response, the inner shadow's shoulder and the quantisation,
which no desk calculation knows. Two captures fix it per cell: a base at the shipped `rimAlpha` gives
`W`, and one rendered point at a named `rimLevelGain` gives `W × L`. `present` and `toneAdapt` are
complementary, so one ladder document carries a level gain AND a collapsed rim and the two never mix
on one cell — the uncollapsed cells move by the first alone, the collapsed cells by the second alone.

> **The canonical bed cannot fit this law, and that is a finding.** Over a solid backdrop,
> unclipped, uncollapsed and outside the holdout, the light bed leaves exactly two cells
> (`dark-solid__rrect-md` and `impulse__rrect-md`, bodies 0.48 and 0.43) and the dark bed leaves
> exactly one (`dark-solid__rrect-md`). Two nearly collinear rows cannot separate a slope from an
> intercept: solving on light 1x alone gives (0.302, +0.569) and on light 2x alone (0.383, +0.183) —
> a factor of three apart, and both with a POSITIVE gain where the reference's slope is negative.
> The dark bed alone is worse: its one cell's `L` is 0.014, the design matrix is rank-deficient
> (condition 6e16) and the gain is unidentifiable. **The two probe grids are what make the wave
> fittable**, and this gate therefore rendered them: W9's light grid and W21's dark grid at the
> shipped document and at the level-gain point, through `VITREA_SCENES` / `VITREA_FIXTURES` into
> scratch. With them the pooled light solve is well conditioned (9.7) and the dark one usable (29.7).

Pooled over every rendered solid row of every bed:

| scheme | rows / cells | `rimAlpha` | `rimLevelGain` | mean \|d\| | max \|d\| | condition |
| --- | --- | --- | --- | --- | --- | --- |
| light | 40 / 10 | **0.8440** | **−0.6283** | 0.0250 | 0.0830 | 9.7 |
| dark | 32 / 8 | **0.0265** | **+2.3343** | 0.0020 | 0.0035 | 29.7 |
| light, 1x rows only | 32 / 8 | 0.9396 | −0.7563 | 0.0208 | 0.0428 | 9.3 |

`rimAlpha` near 1 is not a mistake: `W` is 0.38…0.46, so an amplitude of 0.84 draws a contour row
about 0.27 above the body on `dark-solid__rrect-md`, against the reference's 0.21 at the first row
and 0.23 summed. The sign of `rimLevelGain` is the whole finding — negative in light (the screen
form the CSS tier's inset shadow already is, with an additive part beside it) and strongly positive
in dark (a line that rides its own body up).

### The confirmation — the recommended constants RENDERED

Light `rimAlpha` 0.844 / `rimLevelGain` −0.628, dark 0.0265 / +2.334, `rimCollapsed` 0.038 on both,
captured on both canonical beds at both scales and on both probe grids. Mean |rim − reference| per
side, landed → fitted:

| point | solid | structured | collapsed |
| --- | --- | --- | --- |
| light 1x | 0.0872 → **0.0164** (worst 0.1680 → 0.0326) | 0.1135 → 0.0462 | 0.0180 → 0.0021 |
| light 2x | 0.0618 → **0.0282** (worst 0.1406 → 0.0505) | 0.0884 → 0.0772 | 0.0182 → 0.0021 |
| dark 1x | 0.0110 → **0.0005** (worst 0.0111 → 0.0006) | 0.0397 → 0.0251 | 0.0180 → 0.0021 |
| dark 2x | 0.0143 → **0.0023** (worst 0.0144 → 0.0024) | 0.0381 → 0.0252 | 0.0182 → 0.0021 |
| W9 light grid | 0.1008 → **0.0148** (worst 0.1662 → 0.0320) | 0.1021 → 0.0348 | 0.0201 → 0.0033 |
| W21 dark grid | 0.0268 → **0.0182** (worst 0.0760 → 0.1148) | 0.0469 → 0.0215 | 0.0185 → 0.0044 |

Per cell on the rows the parent's acceptance names, 1x:

| cell | reference | landed | fitted | d |
| --- | --- | --- | --- | --- |
| light `dark-solid__rrect-md` | 0.2294 | 0.0682 | 0.2266 | **−0.0028** |
| light `impulse__rrect-md` (val) | 0.2449 | 0.0769 | 0.2375 | −0.0074 |
| light `light-solid__rrect-md` (both clip) | 0.1002 | 0.0766 | 0.0766 | −0.0237 |
| dark `dark-solid__rrect-md` | 0.0256 | 0.0367 | 0.0252 | −0.0004 |
| dark grid `light-solid__rrect-md` | 0.1032 | — | 0.1103 | +0.0070 |
| dark grid `mid-dark-solid__rrect-sm` | 0.0412 | — | 0.0401 | −0.0011 |
| collapsed `dark-solid__capsule-button` | 0.0201 | 0.0000 | 0.0168 | −0.0033 |

**Two residuals are the width term and not the amplitude**, and they are the only places the fit
misses the parent's clause 2 (0.03 per side):

- `light-solid` at 1x sits at −0.0237 with vitrea's contour row already CLIPPED at 255, exactly as
  the reference's is. The two clip; the sums differ because the reference's SECOND row carries 53 %
  of its peak and vitrea's carries −6 %. No amplitude reaches that.
- every 2x light solid row sits at +0.037…+0.051 with the SAME constants that land 1x at −0.003.

The single worst row anywhere is W21's probe `light-solid__rrect-sm` at +0.1148, and it is not the
dark law's row at all: the reference draws its LIGHT appearance there (body 0.9666, contour clipped)
while vitrea draws the dark material. That is the appearance switch, already on the wave's Deferred
list, and it is not on the canonical dark bed — the dark profile declares no `light-solid` scene, so
no canonical row regresses.

### The width, read on both scales — `width.txt`

§5.99 read the shape on one cell and this reads it on ten. The finding is different from what §5.99
recorded, and is a correction beside it rather than a rewrite:

| cell | reference row0 / row1 (% of peak) | vitrea row0 / row1 |
| --- | --- | --- |
| light 1x `dark-solid__rrect-md` | 100 % / 8.3 % | 100 % / −7.4 % |
| light 1x `light-solid__rrect-md` | 100 % / 52.9 % | 100 % / −6.3 % |
| light 2x `dark-solid__rrect-md` | 100 % / 55.5 % | 100 % / 35.4 % |
| light 2x `light-solid__rrect-md` | 100 % / 65.3 % | 100 % / 53.1 % |
| dark 1x `dark-solid__rrect-md` | 100 % / 0.2 % | 100 % / 0.0 % |

**At 1x, over a dark backdrop, the two rims are the same one-pixel line** — the reference's second
row carries 8 % and vitrea's carries −7 %, and there is no width problem to fix. §5.99's "69 % / 25 %
against 100 % / 56 %" is the 2x reading, and at 2x it reads 100 % / 35 % against 100 % / 55 % here.
What DOES separate is the per-CSS-px integral across scales: vitrea's rises from 0.068 to 0.081
(+19 %) between 1x and 2x while the reference's falls from 0.229 to 0.205 (−10 %) — a 30 % mismatch
across the scale axis that no amplitude constant can absorb, because it is one constant for both
scales. **`rimWidth` should not move on the 1x rows.** What the rows ask for is a SCALE-GRADED width
— a `rimWidth2x` anchor beside `rimWidth`, on the precedent of `sizeScatterGainMax2x` and its
siblings — or a falloff exponent read per scale. Narrowing the 2x band by about 20 % is what closes
the +0.05.

### The goldens' attribution — `goldens-attribution.txt`

At the shipped defaults, with three new profile constants, a re-formed rim line in the optics
shader, a fourth vec4 in the optics uniform and the CSS mirror's rim seam: **all 29 golden tests
pass**, including the isolation proof's pinned pre-C9a hashes on every scene. Nothing moved.

At each ladder point, per golden scene, the largest 8-bit channel delta inside the contour band
(3 px of a coverage discontinuity) against outside it:

| point | worst inside a band | worst outside any band | scenes that moved |
| --- | --- | --- | --- |
| `rimLevelGain` −0.30 | 25 | **0** | 10 of 11 |
| `rimLevelGain` +0.50 | 28 | **0** | 10 of 11 |
| `rimEnvGain` +0.10 | 0 | **0** | 0 of 11 |
| `rimCollapsed` 0.05 | 0 | **0** | 0 of 11 |

X2 holds at every point: **not one pixel outside a contour band moved, on any scene, at any
constant.** Two of the four rows are worth reading twice. `rimCollapsed` moves no golden because no
golden scene has a collapsed surface — G1 must add one, or the constant lands with no golden
covering it. `rimEnvGain` moves no golden because the golden harness feeds no backdrop tone, which
is the same reason the environment term could not be measured on the bed.

---

## (e) The dark thick body over `dark-solid` — `dark-body.txt`

Read beside the rim, as the spec asked. `dark-solid__rrect-md__rest` in the dark scheme: reference
0.01527, vitrea 0.01299, **−0.00228 = −2.93 codes**, identical at both scales.

**No single constant separates it, and here is why.** The whole dark bed's body, native against
landed, in codes: `dark-solid__capsule-button` +1.05 (collapsed), `mid-dark-solid__capsule-button`
**+0.02**, `checkerboard__rrect-md` +0.45, `dark-solid__rrect-md` −2.93, `photo__rrect-md` −5.13,
`impulse__capsule-button` −6.20, `photo__rrect-lg` −3.41, `checkerboard__capsule-button` **−16.05**,
`photo__capsule-button` **−19.05**. A scalar on the dark tint's luminance or on the dark patch's
`tintAlpha` lifts the target by 2.9 codes and lifts `mid-dark-solid__capsule-button` — which is
currently exact to 0.02 of a code — by about the same, trading one three-code row for another. The
constant that could separate them is the dark end of the adaptive tint crossover
(`adaptiveTintDark`), which acts hardest where the backdrop is darkest; this gate did not render a
ladder point on it, because the body is on the wave's Deferred list and the rim ladder had first
call on the shared GPU. **Recommendation: carry it with its number** (−0.00228, −2.9 codes, W21
clause 1 met at 0.010), and name `adaptiveTintDark` as the constant a body wave would fit.

**The much larger number this read turned up, which nothing has charted:** the dark bed's THIN cells
over structured backdrops are −16.05 codes (`checkerboard__capsule-button`) and −19.05 codes
(`photo__capsule-button`), five to six times the thick cell's miss and at both scales. That is the
appearance switch (W21 / W22 Deferred) with a number on it for the first time in this gate's units.
It belongs in `tech-debt-tracker.md` or the switch's own charter, not in this wave.

---

## (f) What G1 should land, and what the parent should decide

### The exact diff

**`packages/renderer-webgpu/src/material.ts`** (already in this worktree, at 0):

- `MaterialOptics` gains `rimLevelGain` and `rimEnvGain`, per variant, with the doc comment naming
  the reading and the sign convention. `MaterialProfile` gains `rimCollapsed` at the root, beside the
  backdrop-tone block whose W7 paragraph it corrects. `MaterialProfilePatch` and
  `withMaterialOverrides` carry `rimCollapsed`; the two optics leaves ride the existing per-variant
  spread. The `clear` variant takes 0 for both gains — it has no rows.
- **G1's values:** light `optics.regular.rimAlpha` 0.18 → **0.844**, `rimLevelGain` 0 → **−0.628**;
  dark patch `optics.regular.rimAlpha` 0.082 → **0.0265**, `rimLevelGain` 0 → **+2.334**;
  `rimCollapsed` 0 → **0.038** on the material.

**`packages/renderer-webgpu/src/wgsl/optics.ts`** — the struct gains `rimLaw : vec4f` and the rim
term becomes

```wgsl
let rimLuma = bodyAlpha * dot(colour, vec3f(0.2126, 0.7152, 0.0722))
  + (1.0 - bodyAlpha) * ou.toneColour.w;
let rimAmplitude = ou.rim.y + ou.rimLaw.x * rimLuma + ou.rimLaw.y * ou.toneColour.w + spec;
let rim = rw * (rimAmplitude * present + ou.rimLaw.z * toneAdapt);
```

`rimLuma` is taken exactly as the tint shade already takes it twenty lines above — the composite
where the layer covers the pixel, the group's measured backdrop tone where it does not — so the two
level-dependent terms in this shader read one quantity.

**`passes.ts` / `renderer.ts`** — three fields on `OpticsPassArgs`, the optics uniform grows
96 → 100 floats with `d[96..98]` and `d[99]` free, and `renderer.ts` passes the two gains from the
variant and `rimCollapsed` from the material (X4: the collapsed rim is the profile's, not the
patch's).

**`packages/platform-web/src/optics.ts`** — `MaterialSourceOptics` gains the two mirrored gains,
`RIM_COLLAPSED` mirrors the profile constant, `rimAmplitude(source, backdropLuminance)` evaluates the
law once per group at the two levels this tier already knows (`materialLuminance` is right there),
and `adaptedSourceOptics`'s one seam becomes
`rimAmplitude(source, luminance(backdrop)) * (1 - k) + rimCollapsed * k`.

**`packages/calibration/scripts/capture-web.ts`** — `rimCollapsed` added to `MATERIAL_PATCH_KEYS`.
Without it the unknown-key guard refuses every ladder document that names the constant, which is how
this gate's first ladder run failed; the guard was right and the list was short.

**`packages/renderer-webgpu/test/backdrop-tone.test.ts`** — the assertion that pinned the old rim
expression now pins the new one, and a case beside it pins the collapsed rim's shape: inert at the
shipped constants for every `toneAdapt`, and exactly `rimCollapsed` at 1, exactly the appearance's own
at 0, one lerp between.

### What the CSS mirror can carry, and what it cannot

**Can:** the whole amplitude law and the collapsed floor. The tier's rim is an inset `box-shadow`
whose alpha is `rimAlpha × borderAlphaPerRimAlpha`, and both new terms are group constants —
`materialLuminance(source, backdropLuminance)` is already computed for the tint shade, and the
backdrop's own luminance is the same number the renderer's `toneColour.w` carries. It is also
already the right FORM: an inset white shadow composited source-over is a screen, which is what a
negative `rimLevelGain` is.

**Cannot:** the band's shape, and therefore the width residual. The renderer spreads
`rw(d) = clamp(1 − |d|/rimWidth, 0, 1)²` over 1.5 CSS px and this tier draws one CSS px of one alpha;
`interiorBandLight` already accounts for the difference in the derived interior LEVEL and must take
the new amplitude through `rimAmplitude` too, or the CSS interior will drift by the band's own light
(the term is `present × rimAlpha × ambient / area`, and `rimAlpha` there becomes the law's value).
It also cannot carry a per-pixel level: over a structured backdrop the renderer's `rimLuma` varies
along the contour and this tier has one number for the group. That is the same approximation the tint
shade already makes and `tier-coherence` already gates; it is a CSS-only residual to record, not to
charter.

### A Decision-Log-2-shaped recommendation

**(a) Take (L4), the affine law, and declare (L3) declined.** The rim is
`rimAlpha + rimLevelGain × luminance(surface)`; the environment term is refuted on the reference in
both schemes and has no row on either bed that separates it on vitrea's side. Record L3 in Deferred
with its two numbers (the reference's L3 mae 0.0105 light / 0.0042 dark against L4's 0.0081 / 0.0013;
the ladder's leverage of 0.0005 per 0.10 of gain) so a later wave with a backdrop-tone feed on the
bed can re-ask it.

**(b) Take `rimCollapsed` = 0.038 on the material, and record that it is NOT the dark rim.** The
spec's binding shape holds — `rw × (rimAmplitude × present + rimCollapsed × toneAdapt)` — and its
conditional does not: +0.0189 against the dark material's +0.0257 is nine codes, and the constant is
absolute. X4 holds and is strengthened: the byte identity extends to a tinted collapsed cell at both
scales.

**(c) Charter the rim's SCALE grading into G1, or narrow clause 2 for the 2x rows.** This is the
parent's call and it is the only clause the fit does not meet. With one width for both scales the
amplitude law lands 1x at −0.003…−0.007 on the dark-backdrop solids and 2x at +0.037…+0.051; the 2x
rows want a band about 20 % narrower. Either `rimWidth2x` joins the profile in this wave (one more
ladder pair, both scales, on the same instrument) or clause 2 is met at 1x and recorded at 0.05 on
2x with the width named as the term that closes it. **Recommendation: take it in G1.** It is one
constant, its rows are the same rows, and leaving it makes the wave's own acceptance unmeetable.

**(d) Add a collapsed-surface golden.** `rimCollapsed` moves nothing in the golden suite, so X2's
attribution is vacuous for that constant. A scene with a surface over a `dark-solid`-class backdrop
would give it one.

**(e) Decline, for this wave:** the dark thick body over `dark-solid` (carried at −2.9 codes; no
constant separates it), the appearance switch (now measured at −16 to −19 codes on the dark thin
structured cells), and W21's probe anomaly where `rrect-sm` and `rrect-lg` collapse over `dark-solid`
and `rrect-md` between them does not.

### Gaps the metrics do not catch, with numbers

1. **The reference's rim is one CSS px at 1x and vitrea's is 1.5.** The 1x sums agree after the fit
   because the amplitude absorbs it; the 2x sums do not, and the eye sees the difference as a softer
   edge, not a dimmer one. +0.05 at 2x, 20 % of band width. (c) above.
2. **`light-solid` clips in both and the sums still differ by 0.024.** A clipped row cannot report
   how much brighter it wanted to be, so no metric on that cell can ever close; the reference's
   SECOND row (53 % of peak against vitrea's −6 %) is where the difference lives and nothing on the
   bed reads it. Recorded here, unreadable by ΔE or SSIM.
3. **The environment term is real in the reference and unmeasurable on this bed.** The reference's
   dark rim grows 0.026 → 0.041 → 0.055 → 0.103 across `dark-solid`, `mid-dark-solid`, the
   structured backdrops and `light-solid` while its body moves a twelfth as much. L4 reproduces that
   through the body, which is a proxy; whether the mechanism is the body or the environment cannot be
   told apart on any bed that exists, because `light-solid` clips and the dark solids have no
   environment to speak of. A bed with a mid-bright solid backdrop under a light-scheme thick surface
   would separate them.
4. **The light bed has two fittable solid cells.** Any two-constant material law on the light scheme
   is unfittable on the canonical bed alone and needs a probe grid; this gate rendered W9's, which
   nothing in the pipeline captures routinely. If the rim law is to be maintained, the probe grids
   should be capturable by the harness rather than by a gate's own script.
5. **`toneColour.w` is 0 in the golden harness** and appears to be 0 for at least some calibration
   groups (the `light-solid` cells' env leverage was exactly 0 even before clipping is accounted
   for). Any future law that reads the group's backdrop tone has to establish that feed first.
6. **The dark scheme's `light-solid__rrect-sm`** is the appearance switch, and the fitted dark law
   makes it 0.115 worse on W21's probe grid. It is not on the canonical bed, so no clause sees it —
   which is exactly the shape of gap this project records rather than accepts.

---

## What was run, and where

| artefact | what it is |
| --- | --- |
| `read-contour.py` | the instrument (X1) |
| `instrument.sh` / `instrument.txt`, `corner-sweep.py`, `crosscheck.py` | (a) the validations |
| `run-reads.sh`, `reads/`, `tables.py`, `contour-read.txt` | (b) every bed, per side, contour and band |
| `collapsed.py`, `collapsed.txt` | (c) the collapsed cells, the byte identity, the body |
| `ladder.sh`, `probe-ladder.sh`, `read-ladder.sh`, `ladder/`, `fit-law.py`, `fit-law.txt` | (d) the law |
| `golden-ladder.spec.ts`, `golden-ladder.sh`, `goldens-attribution.txt` | (d) the goldens (X2) |
| `width.py`, `width.txt` | (f) the rim's profile across the contour |
| `dark-body.py`, `dark-body.txt` | (e) the dark bed's body |

Scratch (never committed): `/Users/new/.claude/jobs/5c70e47f/tmp/w23/g0/` — the candidate profile
documents, the capture logs and every ladder capture.

**One consequence G1 must handle.** Adding the three constants moves the profile documents'
`resolvedMaterialSha256` even though nothing renders differently, and
`packages/calibration/test/tuned-profiles.test.ts` is red in this worktree because of it. The
fingerprints at the seam with all three constants at 0 are `f067ef07c4512872` (light, was
`f6c54a1ea236447a`) and `30696365ef40287a` (dark, was `d86f480c0e136627`); with the fitted values
they will move again. G1 re-records them with the reason, and because the cell key includes the
document's hash the canonical rebuild at G2 has to start from `rm results/matrix.json` in any case.
