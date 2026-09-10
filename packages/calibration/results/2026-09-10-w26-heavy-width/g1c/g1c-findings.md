# W26 G1c — the fits, second reading, on the family reader: findings

**Controlled. The candidate is `sizeHeavyTapSigma` = 9 and `sizeHeavyTapSigma2x` = 9, and the
profile documents' VALUES are G2's to declare.** Evidence in this directory: `bytes.txt` (the
0.14.0 control rung, byte for byte), `ladder.txt` (the reference re-read, the control at every rung,
the mapping, the fits and the objective), `bed.txt` (X5 and the per-span OKLab ΔE at every rung),
`gate.txt` (the fourteen floors and every adopted bound, per rung), `clause.txt` (the gain's
silence and W25's clauses 3 and 4), and the scripts beside them. Read-only on `fixtures/`,
`scenes.json`, the canonical `results/matrix.json`, the canonical `web-captures/` and the two
committed profile documents; every rung rendered to scratch through `--out-matrix` and
`VITREA_WEB_CAPTURES`, with both documents patched (`both:`, W26 Decision Log 4 (c)).

---

## 0. What this child concludes, in one paragraph

The ladder is a clean lever and the control holds at every rung: with the heavy texture in place the
drawn kernel is a member of the fitted family at BOTH scales, and the reader returns the named width
to **+0.2 % on the 0.14.0 control's own 13.418** and to within −8.8 % everywhere else, on a mapping
whose slope is 0.995–1.111 with an rms of 0.03–0.06 device px. Inverting the reference's reading
through that mapping gives **9.48 / 8.63 / 9.19 at dpr 1** (span 96 light, span 160 light, span 96
dark) — a spread of 9.8 %, so **one number serves both spans at dpr 1** — and **8.13 / 9.79 / 8.37
at dpr 2**, a spread of 20.4 %, so **one number does not**. The candidate is **9 at both anchors**:
it takes the objective |log(read / reference)| from **0.275 to 0.069** over six cells, leaves the
share where it already was (mean |Δ| 0.064 → 0.060, unfitted), moves no thin cell by more than
**0.00021** against a bound of 0.001, **improves** the bed's own OKLab ΔE at every thick span in the
1x light scheme, and is the ONLY rung on the ladder other than the control at which the whole gate
passes **38 of 38 with no edit to `PREDICATE_EXCLUDES`**. Three things came out of the run that are
not the fit: `(13.418, 0.001)` is **not** an inert rung — the gate on the heavy texture is
`heavySigmaCss > 0`, so a thousandth of a texel builds one at chain level 0 and makes the deep
sample the RAW backdrop, moving every 2x row; `sizeScatterGainFar2x` is now **silent**, byte for
byte, wherever a source carries a heavy texture; and the dark scheme's ΔE **worsens** at every thick
span while the light improves, on a candidate the dark scheme's own reference reading asks for.

---

## 1. The control rung, and a correction to what it is

`bytes.txt`. The brief named `(13.418, 0.001)` as the 0.14.0 control. It is not one.

| rung | anchors | 1x light | 2x light | 1x dark | 2x dark |
| --- | --- | --- | --- | --- | --- |
| `c0` | (13.418, **0**) | 13/13 identical | 13/13 identical | 12/12 identical | 12/12 identical |
| `z001` | (13.418, **0.001**) | 13/13 identical | **0/13 — all moved** | 12/12 identical | **0/12 — all moved** |

`pyramid.ts` builds the heavy texture whenever `heavySigmaCss > 0`. At 0 there is none and the
optics pass takes the chain tap it has always taken, which is the 0.14.0 path to the bit; at 0.001
there IS one, `heavyTapPlan` selects chain level 0 with a residual of a thousandth of a texel, and
the deep sample becomes the unblurred backdrop. The reader confirms it from the other side: at
`z001` the 2x cells read σ at the scan's own floor with a share of 0.000 and a residual of
**8.8–10.5 display codes** against about 1.1 everywhere else (`ladder.txt` §2).

**So the control is `(13.418, 0)`, it is byte-identical to the canonical 0.14.0 captures on all
fifty rows at both scales in both schemes, and a profile must not name a near-zero heavy width at
either anchor.** The second half of that is a fact about the mechanism worth carrying past this
wave: `sizeHeavyTapSigma` has no small values, only zero and useful ones.

---

## 2. The reference, re-read holdout-free

`ladder.txt` §1. G1b was a spike and read eight backdrops per surface; three of them —
`checkerboard__rrect-lg`, `hc-text__rrect-md`, `photo__rrect-lg` — are HOLDOUT scenes. This child
fits two constants, so X3 applies and those three are dropped from every reading here, the
reference's included.

| surface | sc | scheme | rows | **σ** | share | resid | 2-Gaussian sharp / heavy @ share | G1b σ (8 rows) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1 | light | 7 | **9.300** | 0.400 | 1.936 | 1.30 / 9.00 @ 0.450 | 9.11 |
| `rrect-lg` | 1 | light | 6 | **8.050** | 0.645 | 1.556 | 1.55 / 8.75 @ 0.660 | 8.55 |
| `rrect-md` | 2 | light | 7 | **7.550** | 0.815 | 2.020 | 1.35 / 8.25 @ 0.835 | 7.92 |
| `rrect-lg` | 2 | light | 6 | **9.200** | 0.965 | 1.799 | 4.00 / 10.25 @ 0.925 | 8.97 |
| `rrect-md` | 1 | dark | 6 | **9.150** | 0.420 | 2.002 | 1.30 / 9.00 @ 0.470 | 9.18 |
| `rrect-md` | 2 | dark | 6 | **7.800** | 0.835 | 2.266 | 1.40 / 8.50 @ 0.850 | — |

**Dropping the three holdout rows costs 0.2–0.5 device px**, which is inside the fit's own grid step
and well inside the ladder's condition. Claims §5.121 §4 stands as recorded and these are beside it.

The sharp component (W26 Decision Log 5 (e)'s named gap, recorded not fitted): **1.30–1.55 device px
at 1x and 1.35–1.40 at 2x**, except `rrect-lg` at 2x, whose two-Gaussian fit returns 4.00 / 10.25 —
two halves of one kernel, the split W26 G1 §3a diagnosed, and not a reading.

**One reader change, and it is worth stating because it is where a bug lived.** G1b fitted the
family by Nelder-Mead over (σ, share); G1c scans σ and solves the rest in closed form, because the
model `g_b · [(1 − w)·body + w·tap(σ)]` is LINEAR in the gain. The first build of that scan solved
BOTH mixture coefficients per row, which quietly gives every backdrop its own share — and it does:
every row ran to a share near 1 and the fitted width followed it. One share across the backdrops
with one gain per backdrop is the model, and with it the scan and G1b's search agree to a fifth of a
device px on the same pixels.

---

## 3. The ladder, and the control at every rung

`ladder.txt` §2. Seven rungs, both anchors named in both documents, four profiles each.

| rung | anchors | 1x `-md` | 1x `-lg` | 2x `-md` | 2x `-lg` | dark 1x | dark 2x |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `c0` | 13.418 / 0 | **+0.2 %** | −0.1 % | (no tap) | (no tap) | +0.2 % | (no tap) |
| `d8` | 8 / 8 | −4.4 % | −8.8 % | −7.5 % | −7.5 % | −2.5 % | −7.5 % |
| `d9` | 9 / 9 | −2.2 % | −5.6 % | −5.6 % | −5.6 % | 0.0 % | −5.0 % |
| `d10` | 10 / 10 | −1.5 % | −4.5 % | −5.5 % | −6.0 % | 0.0 % | −5.5 % |
| `d11` | 11 / 11 | +0.5 % | −3.6 % | −5.0 % | −5.5 % | 0.0 % | −4.5 % |
| `x98` | 9 / 8 | −2.2 % | −5.6 % | −7.5 % | −7.5 % | 0.0 % | −7.5 % |
| `x910` | 9 / 10 | −2.2 % | −5.6 % | −5.5 % | −6.0 % | 0.0 % | −5.5 % |

**The two off-diagonal rungs separate the scales exactly.** `x98` and `x910` name 9 at dpr 1 and 8
or 10 at dpr 2; their 1x readings are identical to `d9`'s to the last digit (8.800 / 8.500 / 9.000)
and their 2x readings are identical to `d8`'s and `d10`'s. So the 1x reading depends on the 1x
anchor and on nothing else, and the same at dpr 2 — which is what `heavyTapSigmaAtScale`'s ramp
promises and what a ladder of diagonal rungs alone could not have shown.

**The control closes at 2x, as expected.** G1b read the drawn width 5–10 % narrow at dpr 2 because
`scatterLod` blended two chain levels and the drawn tap was outside the fitted family. With the
heavy texture in place `heavyTapPlan` builds exactly a member of it at both scales, and the 2x bias
is now the same −5 to −7.5 % as the 1x `-lg` bias rather than a different kind of error. The
remaining bias is a property of the reader, it is stable across the ladder, and the fits below
invert it rather than ignore it.

**The mapping** (`ladder.txt` §3), one line per cell over the rungs that name a width at that scale:

| surface | sc | scheme | rungs | slope | intercept | rms | σ ref | **FITTED** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1 | light | 7 | 1.070 | −0.840 | 0.059 | 9.300 | **9.476** |
| `rrect-lg` | 1 | light | 7 | 1.111 | −1.541 | 0.047 | 8.050 | **8.631** |
| `rrect-md` | 1 | dark | 7 | 1.025 | −0.274 | 0.059 | 9.150 | **9.192** |
| `rrect-md` | 2 | light | 6 | 1.016 | −0.707 | 0.030 | 7.550 | **8.128** |
| `rrect-lg` | 2 | light | 6 | 0.995 | −0.541 | 0.037 | 9.200 | **9.785** |
| `rrect-md` | 2 | dark | 6 | 1.025 | −0.775 | 0.046 | 7.800 | **8.366** |

**The condition**: the slope is 0.995–1.111 — about one device px of reading per device px of
constant — and the mapping's own rms is 0.03–0.06 device px over seven rungs spanning 8 to 13.4.
This is a lever the reader sees one for one, and it is the first time in this wave that a heavy
width has had one at BOTH scales.

**Does one number serve both spans?**

- **dpr 1: YES.** 9.48 (span 96 light), 8.63 (span 160 light), 9.19 (span 96 dark) — spread
  **9.8 %**, inside 15 %.
- **dpr 2: NO.** 8.13, 9.79, 8.37 — spread **20.4 %**, outside 15 %. The reference wants a WIDER
  heavy component on the 160-span surface at dpr 2 and a narrower one on the 96-span surface, which
  is the span grading `sizeScatterGainFar2x` used to carry and which one width per source cannot.
  W26 Decision Log 2 (f) chose that knowingly; this is its size, measured on the instrument of
  record: 1.66 device px between the two spans, 20 % of the smaller.

---

## 4. The candidate: 9 and 9

Chosen as the mean of the fitted values at each scale — 9.10 at dpr 1 over the three cells (9.05
over the two light cells), 8.76 at dpr 2 (8.96 over the two light cells) — rounded to the rung the
ladder already carries with its full bed. Nine is within 1.1 % of the 1x light mean and 0.4 % of the
2x light mean, and no other single pair is closer to both.

**The objective, before and after** (`ladder.txt` §4). |log(read / reference)| over the six cells,
a ratio because a width is a scale:

| rung | `-md` 1x L | `-lg` 1x L | `-md` 2x L | `-lg` 2x L | `-md` 1x D | `-md` 2x D | **MEAN** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `c0` (0.14.0) | 0.3690 | 0.5096 | 0.0641 | 0.2904 | 0.3852 | 0.0315 | **0.2750** |
| `d9` (candidate) | 0.0553 | 0.0544 | 0.1185 | 0.0791 | 0.0165 | 0.0918 | **0.0693** |

**0.275 → 0.069, a 75 % reduction**, and every cell improves except `rrect-md` at 2x (0.064 →
0.119) and `rrect-md` 2x dark (0.032 → 0.092) — the two cells the 0.14.0 material already had
nearly right at dpr 2, which is the same span-grading trade as §3's.

**The share is not fitted and does not move**: mean |Δ| **0.064 → 0.060** against the reference's
own. Both are inside W25 clause 2's 0.05-to-0.07 band on every individual cell but two, and neither
rung is better than the other by anything that matters. That is Decision Log 5 (b) confirmed on
rendered rungs: the share was already right, the width was what was wrong.

---

## 5. The bed, at every rung

### 5a. X5 — every probe cell of span ≤ 44 CSS px, against 0.001

`bed.txt`. Against the `c0` control, over 81 thin cells per rung:

| rung | `d8` | `d9` | `d10` | `d11` | `x98` | `x910` |
| --- | --- | --- | --- | --- | --- | --- |
| worst move | 0.00029 | **0.00021** | 0.00015 | 0.00022 | 0.00021 | 0.00021 |

**No rung comes within a factor of three of the bound.** The largest mover at every rung is
`checkerboard-32__capsule-button__rest`, whose span is 44 and which therefore sits at the very top
of X5's range.

### 5b. The fourteen thick floors and every adopted bound

`gate.txt`. `adopted-thresholds.test.ts` over each rung's own 170 calibration and validation cells
(both tiers, six profiles) beside the canonical holdout cells, through `VITREA_MATRIX_PATH`:

| rung | result |
| --- | --- |
| `c0` | **38 / 38 pass** |
| `d8` | 36 / 38 — 2 census assertions |
| **`d9`** | **38 / 38 pass** |
| `d10` | 35 / 38 — 3 census assertions |
| `d11` | 35 / 38 — 3 census assertions |
| `x98` | 36 / 38 — 2 census assertions |
| `x910` | 35 / 38 — 3 census assertions |

**Every failure at every rung is the conditioning predicate's CENSUS and never a bound or a floor.**
The assertions are "the gate must cover every applicable cell: expected … to have a length of 31 but
got 30 / 33" and "cells the shape rows skip, per claims §5's predicate: expected … to deeply equal
…". No floor value is exceeded anywhere on the ladder, which is the whole point of running the gate
at every rung rather than at the candidate.

**And at the candidate the census matches the frozen bed's exactly**: `d9` passes 38 of 38 with
`PREDICATE_EXCLUDES` untouched. That is worth stating precisely because W26 G1's candidate did NOT
— it admitted two cells and needed the file edited — so at this candidate G2 has one less committed
file to move.

### 5c. The per-span OKLab ΔE, both documents patched

`bed.txt`, mean over the span's cells, `c0` → `d9`:

| profile | span 96 | span 128 | span 160 |
| --- | --- | --- | --- |
| 1x light | 0.00475 → **0.00420** | 0.00672 → **0.00583** | 0.00905 → **0.00855** |
| 2x light | 0.00395 → 0.00395 | 0.00603 → **0.00590** | 0.00812 → 0.00934 |
| 1x dark | 0.00447 → 0.00520 | 0.01703 → 0.01892 | 0.02173 → 0.02404 |
| 2x dark | 0.00612 → 0.00628 | 0.02116 → 0.02242 | 0.02582 → 0.02923 |

**The light scheme improves at every thick span at dpr 1 and at two of three at dpr 2; the dark
scheme worsens at all six.** That is not a fit disagreeing with a metric — the dark scheme's OWN
reference reading is 9.15 at dpr 1 and 7.80 at dpr 2, which is what the candidate draws. So the dark
bed's ΔE prefers a heavy component half again wider than the kernel the dark reference actually has,
and the 0.14.0 material's 13.418 was masking something else in the dark scheme rather than being
right about the width. **What it masks is not identified here** and it is the largest thing this
child hands on: the dark bed's thick-span error at 128 and 160 is 0.017–0.026 against the light
bed's 0.007–0.009, three times as large before this candidate and after it.

---

## 6. Clause 5 — what the gain still grades, and W25's clauses 3 and 4

### 6a. `sizeScatterGainFar2x` is silent, byte for byte

`clause.txt`. `wgsl/optics.ts` takes the deep sample from the chain at `scatterLod` and then
overwrites it with the heavy texture wherever `heavyTap.x > 0.5`, and `scatterLod` is the only
consumer of `gainEff`, which is the only consumer of `sizeScatterGainMax`, `sizeScatterGainMax2x`
and `sizeScatterGainFar2x`. Two rungs at the candidate width differing only in that constant — 9.9
against 4.8, which flattens the span grading entirely:

| profile | result |
| --- | --- |
| 1x light | 13 identical — **SILENT** |
| 2x light | 13 identical — **SILENT** |
| 1x dark | 12 identical — **SILENT** |
| 2x dark | 12 identical — **SILENT** |

**Fifty rows, not one bit.** So at any candidate naming a heavy width at both anchors the three gain
constants grade nothing on any group whose source carries a pyramid, which on this bed is every
group. G2 decides whether they are retired; what they still grade is a source with no pyramid, which
is a group with no backdrop to sample.

### 6b. W25 clause 4 — the collapsed dot, read not fitted

`impulse__capsule-button__rest` (validation), reader A unedited, FWHM in CSS px of the composed
kernel by half maximum:

| scale | reference | `c0` (0.14.0) | `d9` (candidate) |
| --- | --- | --- | --- |
| 1x | 6.167 | 4.037 | 4.262 |
| 2x | 1.638 | 3.502 | 3.564 |

The clause asks for 1 CSS px. It is **not met at the control either** — 2.13 CSS px out at 1x and
1.86 in at 2x — so this candidate neither meets it nor regresses it: at dpr 1 it moves 0.22 CSS px
TOWARD the reference and at dpr 2 0.06 away. The reference's own 1x fit there returns a heavy
component at reader A's ceiling with an amplitude of zero, so its 6.167 is a single Gaussian's full
width and not a two-component reading; the clause's own instrument is unconditioned on that row.

### 6c. W25 clause 3 — the nested pane cannot be read by this child

`glass-over-glass` appears on this bed over exactly one backdrop,
`checkerboard__glass-over-glass__rest`, and the split puts it in the **holdout**. X3 reads the
holdout once, at the declaring child's dry run, so this child does not open it. **The clause has no
non-holdout instance at any rung**, which is a property of the bed and not of the candidate: a
clause that can only be read by spending the holdout cannot gate a ladder, and it is G2's at the
dry run or nobody's.

---

## 7. The candidate for G2, with its evidence

| constant | value | how it was arrived at |
| --- | --- | --- |
| `sizeHeavyTapSigma` | **9** | fitted on `rrect-md` and `rrect-lg` at dpr 1 in both schemes through the ladder's own mapping (slope 1.025–1.111, rms ≤ 0.06); the three cells give 9.48 / 8.63 / 9.19, spread 9.8 %, mean 9.10. |
| `sizeHeavyTapSigma2x` | **9** | the same at dpr 2: 8.13 / 9.79 / 8.37, spread 20.4 %, mean 8.76. One number does NOT serve both spans here; 9 is 0.4 % from the light pair's mean. |
| `sizeScatterHeavyShareThick1x` | 0, unchanged | the share is already within 0.06 of the reference's and the candidate does not move it (§4). W25's and W26's declines stand. |
| `sizeScatterFloor2x` | 1, unchanged | not re-opened; §4 shows the 2x share within 0.09 at the candidate. |
| `sizeScatterGainMax` / `Max2x` / `GainFar2x` | unchanged, and now INERT | silent byte for byte at the candidate (§6a). Retiring them is G2's ruling; nothing here depends on their values. |

**What the declaration must carry beside them**

1. The mechanism has no small values. A heavy σ of 0.001 is not "almost off" — it makes the deep
   sample the raw backdrop (§1). Whatever G2 declares, neither anchor may be a small non-zero.
2. `PREDICATE_EXCLUDES` needs no edit at this candidate (§5b), unlike at W26 G1's.
3. The dark bed's thick-span ΔE worsens on a candidate its own reference reading asks for (§5c).
   That is a gap for the tracker, not a reason to move the width.
4. The 2x span grading is worth 1.66 device px between spans 96 and 160 (§3) and one width per
   source cannot carry it; the gain constants that used to are now silent (§6a).
5. The holdout is untouched. `checkerboard__glass-over-glass__rest`, `hc-text__rrect-md__rest`,
   `photo__rrect-lg__rest` and `checkerboard__rrect-lg__rest` were read by nothing here.

---

## 8. What could not be read

- **The nested pane** (§6c) — holdout-only on this bed.
- **The holdout**, deliberately; and the reference's reading is 0.2–0.5 device px different from
  claims §5.121 §4's because those three rows are gone (§2).
- **Why the dark bed prefers a heavy component half again wider than its own reference's** (§5c).
- **The 2x span grading** — measured at 1.66 device px, not carried by any constant this wave has.
- **The sharp component**, recorded at 1.30–1.55 device px against vitrea's body of about 1.6 and
  not fitted: W26 Decision Log 5 (e) gives it to the wave after this one.
- **What no convolution explains**: the reference's residual is 1.556–2.266 display codes
  against vitrea's 0.757–1.188 at every rung of the ladder, unchanged by the width (claims §5.121 §6). The candidate does not
  touch it and no width fitted on this bed can.
