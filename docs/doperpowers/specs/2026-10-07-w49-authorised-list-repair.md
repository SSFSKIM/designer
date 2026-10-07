# W49 — the repair of W48's authorised regressions: the receded dark 0.25 body drawn opaque at thick spans, the span top the transmission and the scatter share, and a landing that cannot trade new cells for old (2026-10-07)

**Status: DRAFT v0 (2026-10-07), the grounding worker's draft for the parent. Decision Log OPEN.**
Branch `w49-g0-grounding` from main `a58573d2f`. Nothing is captured, no holdout is read, no
document moves and no runtime byte changes in this draft. The grounding's evidence is
`packages/calibration/results/2026-10-07-w49-grounding/` (`attribution.py` → `attribution.txt` /
`.json`, read from committed cuts and the release `w48-fit-summaries-archive`; `sheet.py` →
`authorised-sheet.png`). No scratch probe rendered: the classifying census refused every attempt
on a capture process (Zoom's helper processes) and no other session's browser was touched; the
probes are G0's first act (G0 (a)).

## Decisions

Every entry is a PROPOSAL for the parent; the full text is under Decision Log.

| DL | question | proposed |
| --- | --- | --- |
| 1 | the scope, the bed, the rule | the dark `-glass0.25` pair only, from `b2d074d2df24` / `29da6a888a23`; X41, X60 carried; no native capture unless DL 7 asks the user; W45's growth rule at bar 0.5; the landing rule as Design "The landing rule", with the repair clause binding |
| 2 | the reference per cell | `b2d074d2df24` for every cell (X52) EXCEPT the opacity-artifact set (Grounding F1), read against `d0219cd684bf`, declared before any render |
| 3 | the families | R (the receded far delta, an existing leaf, signed) first; A (the active's thick end: the far delta, the scatter top, the scale gain, the 1x thin start); D and W as new leaves landed inert only on their ladder bars |
| 4 | the post-gate tie-break | none: the selection rule is lexicographic and hashed in part 2; no part-2 amendment after the gate |
| 5 | if no point repairs the list | the wave closes at the finding, or the user rules on R alone; no ruling re-authorises a listed cell |
| 6 | the no-opaque invariant | `alphaBase < 1` for every shipped endpoint at every span, both tiers, both scales, as a test |
| 7 | the referee | the spent holdout and referees read once at the exposure as a PREDICTION check (read 9); a blind thick-span referee needs a native capture (X5, the user's) |
| 8 | 0.28.0's opaque unfocused glass | a product defect on both tiers; R may land on its own as an early patch if the parent wants it before the whole repair |

## Purpose

**What the wave is for.** W48 shipped the dark `-glass0.25` refit `b2d074d2df24` (0.28.0) as an
improvement landing with seventeen (cell, profile) entries authorised to regress against
`d0219cd684bf` (`T1_DARK_AUTHORISED_REGRESSIONS`; claims §5.213–§5.214; ten distinct scenes). W49
repairs them while keeping W48's gains (C rest halved at both scales, F inactive halved at 1x), and
moves the named misses (P at both scales, F inactive at 2x) where it can. The parent has ruled the
success condition DECLARES the repair of the list rather than an aggregate improvement, so the next
landing cannot trade new cells for old.

**What the grounding found changes the question.** W48 deferred "a span-graded receded scatter" for
the thick inactive cells (Decision Log 9 §7). That diagnosis is wrong: the receded body is not
under-scattered at span 160, it is OPAQUE there (F1). No scatter law, span-graded or not, can draw
through it. The repair of the three worst entries is an existing leaf at a value W48's fit never
read, and W49's real modelling question is the one that sits behind it: Apple's thick body passes
coarse structure strongly while passing text and impulses weakly at the same span (F2, F5), which is
a pitch-selective transmission vitrea's span law alone cannot draw.

**The best version of this is four things.**
1. **The defect repaired first, and on both tiers.** 0.28.0's dark 0.25 material draws an unfocused
   window's glass as an opaque slab wherever a surface's shorter side is 160 CSS px or more; Apple's
   is transmissive there (native T1 0.073 on `checkerboard-64__rrect-lg__inactive`). That is a
   product defect, not a texture residual (DL 8).
2. **A declaration that can see its own blind spots.** W48's stage 2 had no authority over four
   inactive cells per scale and its stage 1 drew an opaque thick body at eight of its nine
   operator-1 grid pairs; nothing in the protocol noticed (X74, X75).
3. **The repair as the landing condition, the tie-break hashed before the first render** (DL 4, 5).
4. **The pitch-selective thick body, as far as the bed identifies it**, through the existing second
   heavy tap's span grading, extended to 1x only if its ladder bar demands it (Design "W").

**What the wave does not do.** No light change, no 0.5 change (X60, X41). No change to T1's
statistic, bar or arithmetic. No native capture without the user's lift of X5 (DL 7). The dark photo
body and S1 dark stay named gaps unless a family moves them.

## Grounding (main at `a58573d2f`, W48 closed)

All numbers are T1 (`interiorStdDev`, linear light, over the native silhouette), WebGPU tier, read
from W48's exposure cut `cut-025-w48-dl9-exposure`, W46's gate cut of point A and the archived W48
fit summaries. `attribution.txt` §1–§5 carries every row this section quotes.

### F1 — the receded body is opaque at span 160 (the three worst entries)

**The mechanism.** Operator 1 reads `alphaBase = clamp(tintAlpha + rampAtScale(far1x, far2x, dpr)
· farS(span), 0, 1)`, with `span` the surface's shorter extent and `farS = smoothstep(sizeSpanMax,
sizeScatterSpanMax(dpr), span)`. The receded document `29da6a888a23` names `tintAlpha` 0.8 and
carries the active's far deltas 0.2 / 0.2 and span tops 160 / 160, materialised by inheritance
(X67). At `rrect-lg` (span 160) `farS` = 1, so the receded `alphaBase` is exactly **1.0** at both
scales (0.9 on `rrect-ml`, 0.8 at and below `rrect-md`). With `sizedAlpha` = `solvedAlpha` = 1 the
composite is `adapted` alone: the backdrop's transmission is zero and the body is a flat colour
except where the collapse target's per-pixel lerp leaks a trace (`attribution.txt` §5).

**The evidence.**
- *Authority.* Over all 191 stage-2 fit summaries W48 archived (receded transmission 0.8 and 0.89,
  the receded scatter sweep, the second tap, operator 2, the body width), every `rrect-lg` inactive
  cell reads ONE value at each scale: `checkerboard-64` 0.0020 / 0.0006, `checkerboard-8` 0.0146 /
  0.0161, `hc-text` 0.0189 / 0.0212, `impulse` 0.0000 / 0.0000. Every other inactive cell reads 15–48
  distinct values. No stage-2 leaf reached a span-160 inactive cell (`attribution.txt` §2).
- *The same scatter without the opacity.* W46's point A, the receded scatter W48 shipped at
  `tintAlpha` 0.8 with no far delta over the `d0219cd684bf` active, read
  `checkerboard-64__rrect-lg__inactive` **0.0480 / 0.0686** against native 0.0733 / 0.0742 —
  toward Apple by 6.45 / 10.27 B (§3). The scatter W48 deferred as the cause was moving the cell the
  right way.
- *By eye* (`authorised-sheet.png`, rows 1, 2, 5, 9, 10, 12): `b2d074d2df24` draws all three
  thick inactive cells perfectly flat, at a gain of 4 as well, where Apple and `d0219cd684bf` keep
  the blurred checker and the photo's hues.
- *The CSS tier mirrors it* (`spanGradedTintAlpha`): its `checkerboard-64__rrect-lg__inactive`
  reads 0.0000 / 0.0001, `photo__rrect-lg__inactive` 0.0010 / 0.0007.

**What it also explains.** The opaque body made three other cells read better than they are: at
the opaque floor `hc-text__rrect-lg__inactive` (0.0189 / 0.0212 against native 0.0164) and
`impulse__rrect-lg__inactive` (0 against 0.0006) moved toward Apple, and
`checkerboard-8__rrect-lg__inactive` (0.0146 / 0.0161) is one of the F inactive cells whose 1x
halving W48 claims. Point A, transmitting, read them 0.0334 / 0.0364, 0.0049 / 0.0037 and 0.0157 /
0.0162. So un-opaquing keeps `checkerboard-8__rrect-lg` (F inactive's halving survives), but
moves the text and impulse cells away from Apple unless something else separates them (F5). And
W48's operator-2 verdict at stage 2 ("the fine term improves the objective at neither scale",
Decision Log 9 §4) was read with one of its two fine cells held constant by the opacity: it is
confounded, not refuted.

**The opacity reached the active stage too.** Of stage 1's nine (`tintAlpha`, far) pairs, eight
put `tintAlpha + far` ≥ 1 and drew the active `rrect-lg` rest body opaque (`checkerboard-64__rrect-lg
__rest` 0.0096 / 0.0077 at every one of them, §4). Only the landed pair (0.7, 0.2) did not. The
factorial was a one-point search at the thick end.

### F2 — the thick rest cells pay for the shared span top

`checkerboard-32`, `-64` and `hc-text-28` at `rrect-lg` rest. The transmission at span 160 is 0.9
in both generations (`d0219cd684bf`: 0.9 flat; `b2d074d2df24`: 0.7 + 0.2 · 1), so the body is not
the cause. `sizeScatterSpanMax` is: one leaf sets operator 1's far knot AND the scatter's span top,
and W48 moved it 256 → 160 for the transmission's sake. At 1x that takes `kDeep(160)` 0.74 → 1.00
(the deep sharp share 0.26 → 0) and the ramp's edge start 0.41 → 0.20; at 2x, where the deep value is
already 1, it takes the heavy gain `sizeScatterGainFar2x` from 6.6 to its full 9.9 (§5). Stage 1
isolates it: at the same alpha 0.9, `d0219cd684bf` reads 0.0292 / 0.0338 / 0.0311 at 1x and the
top-160 point with the old scale gain −2 reads 0.0228 / 0.0297 / 0.0270 (2x 0.0343 / 0.0395 / 0.0325
against 0.0283 / 0.0347 / 0.0287). The selected scale gain −0.5 takes a further 0.0025 / 0.0005 /
0.0008 at 1x (0.0023 / 0.0004 / 0.0010 at 2x).

By eye the gap is larger than the growth says: Apple's coarse thick body carries about three times
vitrea's contrast in both generations (native 0.0856 against 0.0338 / 0.0292 on
`checkerboard-64__rrect-lg__rest`), and Apple's `hc-text-28` bars stay crisp at `rrect-lg` where
vitrea's are smoothed, while the fine and text cells at the same span (`checkerboard-8`, `hc-text`,
`hc-text-7` lg rest) already read within 20 % of Apple. That is F5's signature in the active pose.

### F3 — the gain knot's cost at the thin and middle spans

- `checkerboard-lc16__rrect-md__rest` (2.66 / 2.91 B, the only `rrect-md` rest cell over Apple;
  every other reads a ratio of 0.59–1.25 against its 1.61 / 1.59). The cause is operator 1's opening at
  span 96, where `farS` = 0: `alphaBase` 0.9 → 0.715. At `tintAlpha` 0.9 stage 1 read it 0.0235
  (native 0.0217); at 0.7 it reads 0.0402 with the scale gain −2 and 0.0348 at −0.5 (the selected
  gain helped it), 0.0331 at 0, 0.0251 at `sizeOcclusionGain` 0.6 (which gives back the md C rest
  gains). By eye (`authorised-sheet.png` rows 4 and 11, gain 4) Apple's body is lighter than both
  vitrea generations and smooth, where `b2d074d2df24` draws the 16 px checker: a level difference
  as well as a texture one, and Apple separates this low-contrast checker from the full-contrast
  `checkerboard__rrect-md__rest` (ratio 1.05) at the same span and pitch. No span or pitch leaf can;
  only the contrast-weighted scale statistic distinguishes them, and it moves the coarse thick rest
  cells (F2) the same way.
- `impulse__capsule-button__rest` at 1x (2.26 B; at 2x it is −2.00 B, an overshoot inside the
  rule). The opening at span 44 (0.0173 at 0.9, 0.0242 at 0.7 with gain −2) and the scale gain −0.5
  (+0.0011). The 1x thin start reaches it (0.0231 at 0.6, within B of `d0219cd684bf`'s error) at a
  cost to the other thin rest cells that halved C rest.

### F4 — the 2x capsule inactive cells are W46 point A's receded thin start

`checkerboard__capsule-button__inactive` 2.79 B and its orange tint 1.93 B, 2x only (1x 0.69 /
0.85 B). The receded `sizeScatterRampStartThin2x` 1 → 0.4 (point A) takes the cell 0.0676 → 0.0356
(native 0.0501); 0.7 reads 0.0514. The receded scale gain 0 against the inherited value adds to it
(0.0356 at 0, 0.0463 at −1, 0.0573 inherited), and the second tap's 2x width recovers a little
(σ 5: 0.0383). Existing receded leaves reach both cells; the question is what the trade costs the
F inactive and thin inactive cells that preferred 0.4.

### F5 — Apple's thick body is pitch-selective

At span 160, in both poses, Apple passes 64 px structure at about the level it passes at span 96
(inactive 0.0733 against 0.0783; rest 0.0856 against 0.1010) and text and impulses weakly
(`hc-text__rrect-lg__inactive` 0.0164, `impulse__rrect-lg__inactive` 0.0006). vitrea's thick body
transmits everything at one alpha through a heavy component of one width per source (13.4 device px
at 1x, the chain's last level; `sizeHeavyTapSigma` 0 on the dark pair). Point A at alpha 0.8 brought
`checkerboard-64__rrect-lg__inactive` toward Apple and took `hc-text__rrect-lg__inactive` and
`impulse__rrect-lg__inactive` away from it by 1.70 / 2.27 B and 2.90 / 3.55 B against
`d0219cd684bf`. So a transmission alone repairs the listed cells at a value near `d0219cd684bf`'s
(about 0.89 at span 160) and cannot go further toward Apple without moving those two cells away. A
body that is more transmissive AND more widely blurred at thick spans can, which is what a
span-graded second heavy tap draws: W45's share law, live at 2x, absent at 1x (W48 Deferred, "the
1x per-span width").

### Per-cell attribution

Growth in B against `d0219cd684bf` (1x / 2x; a dash is not listed at that scale). Partition is the
cell's W46 role.

| cell | growth | partition | cause | evidence | existing leaves reach it? |
| --- | --- | --- | --- | --- | --- |
| `checkerboard-64__rrect-lg__inactive` | 8.94 / 12.53 | gate | receded `alphaBase` 1.0 at span 160: receded `tintAlpha` 0.8 + inherited far 0.2 | F1: 191 renders one value; point A 0.048 / 0.069; flat by eye; CSS 0.0000 | yes: the receded far delta (R) |
| `checkerboard-32__rrect-lg__inactive` | 3.20 / 6.04 | referee | the same | flat by eye; same span | yes (R); read only at the exposure |
| `photo__rrect-lg__inactive` | 2.64 / 2.90 | holdout | the same | flat by eye; web 0.0022 / 0.0023 | yes (R); read only at the exposure |
| `checkerboard-32__rrect-lg__rest` | 2.98 / 2.71 | gate | the span top 256 → 160 in the scatter (1x `kDeep` and ramp, 2x heavy gain); the scale gain −0.5 | F2, stage 1 at equal alpha | only by lowering the active far knot, which the span top couples (D) |
| `checkerboard-64__rrect-lg__rest` | 1.55 / 1.71 | gate | the same | F2 | as above |
| `hc-text-28__rrect-lg__rest` | 1.39 / 1.34 | gate | the same | F2 | as above |
| `checkerboard-lc16__rrect-md__rest` | 2.66 / 2.91 | gate | operator 1's opening at span 96 (0.9 → 0.715) | F3, stage 1 | trade: occlusion gain, scale gain; contrast-dependent, perhaps a level gap |
| `impulse__capsule-button__rest` | 2.26 / – | gate | the opening at span 44; the scale gain | F3 | yes: the 1x thin start, at a C rest cost |
| `checkerboard__capsule-button__inactive` | – / 2.79 | gate | receded 2x thin start 0.4 and receded scale gain 0 (point A) | F4, stage-2 sweeps | yes: the receded 2x thin start, the gain, the second tap's 2x width |
| `checkerboard__capsule-button__inactive-tint-orange` | – / 1.93 | gate | the same | F4 | yes |

## Design (advisory unless marked)

### The families

- **R — the receded transmission at thick spans (an existing leaf, never fitted).** The receded
  document's `tintAlphaFar1x` / `tintAlphaFar2x` as its own fit members, not the active's values
  materialised. Proposed domain **[−0.3, 0.2]**, signed: the shader and `spanGradedTintAlpha` clamp
  `alphaBase` into [0, 1] and neither tier validates the sign (`material.ts`, `optics.ts`), so a
  negative delta needs no runtime change, only the builder's declared domain (W47 X68 says [0, 0.6]).
  Crossed with the receded `tintAlpha` {0.8, 0.89}. Read on the non-withheld receded cells; the
  `rrect-lg` and `rrect-ml` inactive cells carry the decision. Prediction (F1, F5): every far ≤ 0.1
  repairs `checkerboard-64__rrect-lg__inactive`; near 0.09 at `tintAlpha` 0.8 the lg text and
  impulse cells read within B of `d0219cd684bf`; at 0 or below they move away.
- **A — the active's thick end.** The active far deltas {0.1, 0.15, 0.2} (W48's grid had nothing
  below 0.2, and eight of its nine pairs were opaque at span 160), the scatter top
  `sizeScatterSpanMax` / `…2x` {160, 192, 256}, `sizeScatterScaleGain` {−2, −1, −0.5, 0}, the 1x
  thin start {0.6, 0.66, 0.72}, `sizeOcclusionGain` {0.05, 0.2}. With the top coupled, a top above
  160 moves operator 1's knot too and a thick end at 0.9 then needs a far delta that takes
  `alphaBase` past 1 above span 160, which X75 forbids; that is D's reason.
- **D — operator 1's own span top (a new leaf pair, conditional).** `tintAlphaSpanMax` /
  `tintAlphaSpanMax2x`: `farA(span) = smoothstep(sizeSpanMax, tintAlphaSpanMax(dpr), span)` in place
  of `farS` in the `alphaBase` line only. Identity **0, meaning "the scatter's top"**
  (`sizeScatterSpanMax(dpr)`), a plain value drop in `MATERIAL_IDENTITY_TABLE`, so every shipped
  document, `b2d074d2df24` included, resolves and hashes as today. Where it lives: the field and
  default in `packages/renderer-webgpu/src/material.ts` with a `tintAlphaSpanMaxAtScale` resolver,
  the CPU pack in `renderer.ts` (one float, the optics uniform's next free slot), the `alphaBase` line
  of `src/wgsl/optics.ts`, the mirror in `platform-web/src/optics.ts`'s `spanGradedTintAlpha` and the
  patch reader, pinned by `tier-coherence.test.ts`; proven inert as W47's operator 1 was (ten
  digests, 34 goldens, the dark 0.25 bed byte-identical). It decouples the transmission's knot from
  the scatter's top so A can return the scatter top to where the thick rest cells want it. Ladder
  bar: lands only if, with the scatter top at 192 or 256 and the transmission's knot held at 160, the
  three thick rest cells come within B of `d0219cd684bf` with C rest still halved.
- **W — the 1x anchor of W45's span-graded second-tap share (conditional).**
  `sizeHeavySecondShareFar1x`: `tapShare = share + rampAtScale(far1x, far2x, dpr) · farS`. Identity
  0, a plain value drop. **No shader change**: `heavySecondShareFarAtScale` in `material.ts`
  resolves `rampAtScale(0, far2x, dpr)` today and becomes `rampAtScale(far1x, far2x, dpr)`; the
  share keeps its gate (a share of 0 allocates nothing, so the delta is read only where a document's
  share opens the tap, as now). The CSS tier declines it with the tap (W45). Its job is F5: at span
  160 more transmission (R below 0.09) with more of a wider heavy component, so 64 px structure
  passes and text and impulses do not. Ladder bar: lands only if R's ladder shows the trade (the lg
  text or impulse inactive cell away beyond B at every R value that moves
  `checkerboard-64__rrect-lg__inactive` toward Apple beyond `d0219cd684bf`) AND a W rung clears it
  at both scales. The receded 2x tap's span grading already exists (`sizeHeavySecondShareFar2x`)
  and is a fit member at 2x without a ladder.
- **O — operator 2 re-read.** `sizeFineTapShare` / `…Sigma` / `…Sigma2x` re-enter the receded stage:
  their W48 verdict was read with `checkerboard-8__rrect-lg__inactive` held constant by the opacity
  (F1). F inactive at 2x is a named miss this family can move.

### The order

R first, alone, on the receded document over `b2d074d2df24`'s active: it is the defect, it needs
no runtime change, and its gate is cheap. Then A (with D if its bar met) on the active. Then the
receded scatter's capsule leaves (F4), W and O on the receded over the stage-A active. The union
re-read once, as W46–W48.

### The landing rule (MARKED when ruled; DL 1, 2, 4, 5)

W45's growth-only rule at bar 0.5 per cell, with these clauses, all hashed in part 1:
1. **The repair (binding).** Every one of the seventeen entries reads not away beyond B against
   `d0219cd684bf`. A rendered point that fails any entry is not a landing candidate.
2. **No new trade (binding).** Against the reference of DL 2 (`b2d074d2df24`, except the
   opacity-artifact set read against `d0219cd684bf`: `checkerboard-8__rrect-lg__inactive`,
   `hc-text__rrect-lg__inactive` and `impulse__rrect-lg__inactive` at both scales, whose
   `b2d074d2df24` readings were drawn by an opaque body), **no cell away beyond B and none past 3 B**.
   A budget of zero, because the parent's condition is that no listed cell is bought with a new one.
3. **Keep W48's gains (binding).** C rest halved at both scales and F inactive halved at 1x, each
   against `d0219cd684bf`'s aggregate as W48 read them; the gated groups as W48.
4. **The targets (read).** P at both scales and F inactive at 2x read and named; not landing
   conditions.
5. **X75** at every rendered point.

**The selection, hashed in part 2 before any fit render (DL 4).** Among rendered points that meet
1–3 and X75: the declared objective's minimum, then the hashed tie rule. Among points that do not,
for the report only: fewest unrepaired entries, then fewest new cells away beyond B, then fewest
past 3 B, then the objective. No part-2 amendment after the gate; W48's Decision Log 9 amended its
selection after reading the gate, and the record had to say so. If no point meets 1–3 the gate
reads NEITHER and DL 5 applies.

### The CSS tier

R and D are mirrored (operator 1 is, per surface). W and O are declined with the taps. The CSS
tier's lg inactive cells are opaque today (F1); X75 holds on both tiers.

## Children

### G0: the probes, the operators inert if their bars meet, the declaration (ledger §5.215)

Branch `w49-g0-declaration`, evidence `results/2026-10-07-w49-g0-declaration/`.
- (a) **The probes the grounding could not render** (the census refused), scratch only, under the
  classifying census, non-withheld cells only:
  - P1: `d0219cd684bf` with only `sizeScatterSpanMax` / `…2x` 160. Prediction: the three thick rest
    cells read 0.0228 / 0.0297 / 0.0270 at 1x and 0.0283 / 0.0347 / 0.0287 at 2x (F2 by render
    rather than by arithmetic).
  - P2: `b2d074d2df24` with the receded far deltas at {−0.1, 0, 0.05, 0.09, 0.15}. Prediction:
    `checkerboard-64__rrect-lg__inactive` leaves 0.0020 / 0.0006 at every value below 0.2; the
    other `rrect-lg` inactive cells as F5.
- (b) **The ladders** for D and W on their bars (Design); each lands inert in this child only if its
  bar meets (W47's form: digests, goldens, the dark bed byte-identical).
- (c) **X74 and X75 in the tools**: the authority check in the fit driver, the opacity check in the
  builder and as a runtime test over every shipped document.
- (d) W48's declaration tools re-bound to W49 (`b2d074d2df24` / `29da6a888a23` snapshots,
  W49's root), part 1 hashed on the assembled tree (the rule, the reference per cell, the families,
  the predictions, including the withheld cells' numeric predictions of DL 7), the verdicts read,
  part 2 with the selection rule hashed.

### G1: the fit, the gate, the exposure, the publication (ledger §5.216)

R, then A (+D), then the receded leaves (F4, W, O), then the union; the gate report and STOP; the
freeze and strict-mode stage; the exposure once (read 9) and STOP; publication superseding
`b2d074d2df24` on the parent's go. If DL 8 rules an early landing, R's own gate and exposure can
publish first and the later stages supersede it.

### G2: the landing (ledger §5.217)

T1's dark row re-baselined in the five-part order (X59) with `T1_DARK_AUTHORISED_REGRESSIONS`
EMPTIED (the repair clause makes every entry not away against `d0219cd684bf`), its standing witness
kept for the record, `MISSED_27_ROWS` re-derived, `T1_DARK_REFERENCE` moved last; the generated 0.25
module, the docs, CLAUDE.md's W48 paragraph corrected (the deferral's diagnosis), the changeset
(`@vitreajs/vitrea-web` minor; a patch if R lands alone), the c9d chain, the sheets.

## Referees and the holdout

- **Spent for W49's question.** The canonical dark 0.25 holdout (seven scenes per scale) and W46's
  referees (six per scale, `w46-referees-1`) were read once at `b2d074d2df24`'s bytes (read 8). Two of
  the seventeen entries are withheld cells, and this grounding read their exposure values and
  images. They are not blind for W49.
- **What W49 can do with them.** Keep them withheld from every fit, stage, gate read and sheet; state
  in part 1 a numeric prediction for each (from the gate cells' ladder: `checkerboard-32__rrect-lg__
  inactive` and `photo__rrect-lg__inactive` move as `checkerboard-64__rrect-lg__inactive` does) and
  read them once at the new bytes as read 9, recorded as a prediction check, not as a held-out
  generalisation test.
- **A blind thick-span referee needs a capture.** Every non-solid `rrect-lg` inactive cell of the
  dark bed is either a gate cell or spent, and the bed stops at span 160, which is exactly where the
  defect starts. A native capture under X5 (the user's lift) of new thick inactive and rest cells
  (other pitches and text sizes at `rrect-lg`, and a surface above span 160) would give a blind
  referee and test X75's extrapolation (DL 7).

## Cross-Child Contracts

**Carried from W44–W48:** X1, X3, X24, X33, X41, X44 (as narrowed), X45, X49–X55, X57–X73 as W48
bound them, with X52's reference moved to `b2d074d2df24` and DL 2's exception; X62's snapshots taken
at this charter's merge; the census, no attribution, path-scoped adds, freeze 1,818 and X41 911 at
every merge.

**New (proposed):**
- **X74 — the authority check.** Before any selection, every declared cell of a stage reads at
  least two distinct values over the stage's rendered points, or the stage report names it as
  outside the stage's reach with the reason. W48's stage 2 had four such cells per scale and
  selected over them silently.
- **X75 — no opaque glass.** For every shipped and every candidate endpoint, `alphaBase < 1` (a
  declared margin, e.g. ≤ 0.95, is the parent's) at every span from 0 to 1024 CSS px, at dpr 1 and
  2, on both tiers; a runtime test over `SHIPPED_MATERIAL_PROFILE_DOCUMENTS` and a builder refusal.
- **X76 — an inherited receded leaf is a choice.** A leaf the receded document materialises at the
  active's value (X67) is either a fit member of the receded stage or held by a declared `hold` with
  its reading; it is never fixed silently.

## Risks & Mitigations

- **The repair clause may be unattainable for `checkerboard-lc16__rrect-md__rest`** (F3: a
  contrast-dependent and partly level gap that W48's opening exposed). Its repair by existing leaves
  gives back md C rest gains. *Mitigation:* G0's ladder reads it first; if no rung repairs it with C
  rest halved, the parent rules before the fit (DL 5's options), not after the gate.
- **R alone moves text and impulse cells away** (F5). *Mitigation:* the rule reads them against
  `d0219cd684bf` (DL 2), R's prediction is near 0.09, and W exists for the rest.
- **D adds a uniform float.** *Mitigation:* W47's inert proof; the optics uniform has spare slots
  (check at G0 (b)).
- **The census.** Capture processes (Zoom here) refuse renders; the driver retries with backoff.

## Deferred / Out of Scope

- The dark photo body (P), S1 dark, the dark 0.5 pair (X41), the light scheme (X60), the CSS tier's
  fine pitch, accessibility at 0.25.
- A blind thick-span native bed (DL 7) unless the user lifts X5.

## Tracking Map

| child | status | ledger |
| --- | --- | --- |
| grounding | DONE on `w49-g0-grounding`: attribution, the sheet, this draft | (to §5.215 at G0) |
| G0 | not started | §5.215 |
| G1 | not started | §5.216 |
| G2 | not started | §5.217 |

## Decision Log

OPEN. The proposals the Decisions table summarises, each for the parent (or the user where marked):

- **DL 1 — the scope, the bed, the rule.** As the table. Proposed because the defect and the list
  are dark 0.25 only; X60 and X41 stand.
- **DL 2 — the reference per cell.** Proposed: `b2d074d2df24` for every cell except the
  opacity-artifact set, read against `d0219cd684bf`, declared before any render. *Why:* those
  readings were drawn by an opaque body, a state the landing must remove; defending them against
  the repair would make the repair impossible by construction. *Alternative:* everything against
  `b2d074d2df24`, which then needs R to keep `hc-text__rrect-lg__inactive` at or under about
  0.022, which F5 says only W can do.
- **DL 3 — the families and their order.** R, A (+D on its bar), then F4's receded leaves, W on
  its bar, O. *Alternative:* R alone (DL 8), if the parent wants the defect closed before the
  modelling question.
- **DL 4 — no post-gate tie-break.** The selection is part 2's, hashed before any render, as
  Design states. *Why:* W48's Decision Log 9 amended part 2 after the gate.
- **DL 5 — when nothing repairs the list.** Proposed: close at the finding, or the user rules on
  landing R alone if R meets the rule on the cells it reaches; no ruling re-authorises a listed
  cell, and any cell left unrepaired stays in the list with its original W48 ruling.
- **DL 6 — X75's margin.** The parent's number; 0.95 proposed (Apple's thick receded body reads
  T1 near its `rrect-md` value, nowhere near opaque).
- **DL 7 — the referee (the user's for X5).** Read the spent cells once as a prediction check;
  ask the user whether to capture a blind thick-span bed.
- **DL 8 — the shipped defect.** 0.28.0's `macos27Glass025MaterialProfileDocument` draws unfocused
  dark glass opaque at a shorter side ≥ 160 CSS px on both tiers. Proposed: R first and landable on
  its own gate as a patch, if the parent wants the defect closed early.

## Surprises & Discoveries

- **W48's deferral named the wrong cause** (F1): the thick inactive cells are opaque, not
  under-scattered, and W48's stage 2 could not have seen it, because no stage-2 leaf reached them.
- **Most of W48's stage-1 operator-1 grid was opaque at span 160** (eight of nine pairs); the landed
  pair was the only one that was not.
- **The opacity flattered three cells**, one of them in a target W48 reports as halved (F1).
- **The census refused the grounding's probes** on a capture process (Zoom); nothing rendered.

## Revision Notes

- 2026-10-07 (v0): drafted by the grounding worker from main `a58573d2f`; Decision Log open.
