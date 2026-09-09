# W26 G1 — the width built structurally, the instrument extended, and the fits: findings

**Controlled. Deliverable: the three parts landed on this branch with their measurements, and this
report. The parent merges; the profile documents' VALUES are G2's to declare — the only committed
evidence this child writes is `resolvedMaterialSha256` in both documents, re-recorded with a
`$comment-w26-g1` because two constants came out of the material's shape.**

Evidence in this directory: `mapping.txt` (part (a)'s acceptance and the ladder), `reader-d.txt`
(part (b)'s validation and its negative result), `fits.txt` (part (c)'s fits, each with its rows and
its condition), `inert-1x.txt` (what naming the chain's own 1x width costs), `probe-read.txt` (the
level, the spans and X5 over the whole probe set), and the scripts that produced each. Read-only on
`fixtures/`, `scenes.json`, the canonical `results/matrix.json` and the canonical `web-captures/`;
every render went to scratch through `--out-matrix` and `VITREA_WEB_CAPTURES`.

---

## 0. What this child concludes, in one paragraph

The mechanism works, costs almost nothing, and is exactly inert where it is declined. What it
cannot do is be FITTED at dpr 1, and the reason is not the reader W26 G0 blamed: the 1x `impulse`
fixture does not carry the heavy component at 8-bit depth, so no reader can recover a width from it.
At dpr 2, where the fixture does carry it, the fit succeeds on the one reference row whose own
two-component fit is conditioned — and lands the deep sample's width on the reference within 1.4 %
where the 0.14.0 material was 22.4 % narrow — at the cost of the `-lg` row, where the chain's
clamped tap was already right and one width per source cannot follow the span. The share is fitted
at 1x and improves its own objective by 72 % while costing the bed's ΔE on every thick span. Every
adopted bound and all fourteen thick floors pass at the candidate, and the conditioning predicate
admits two more cells than the frozen bed does. So there is a candidate, and there are two rulings
in it that belong to the parent rather than to this child.

---

## 1. Part (a) — the tap built structurally

`wgsl/optics.ts`'s 9 × 9 in-shader grid is gone. The width is now a **third pyramid texture**: the
chain level `heavyTapPlan` names, blurred up to the profile's σ by the two separable passes the
pyramid already runs for the body (`runSeparableBlur`, `PyramidResources.heavy`), read once at the
refracted uv. G0's candidates (i) `sizeHeavyLevelOffset` and (iii) `sizeHeavySecondShare` are
removed from the material, the uniform and the shader; G0's branch and `../g0/` are their record.
`sizeHeavyTapSigma` / `sizeHeavyTapSigma2x` and `CHAIN_LEVEL_SIGMA` stay.

**The acceptance, on captures rather than on arithmetic** (`mapping.txt` §1). At σ2x 11.3, reader A's
heavy σ on the three 2x impulse rows:

| row | G0's 9 × 9 grid | this texture | Δ | reference |
| --- | --- | --- | --- | --- |
| `impulse__rrect-md` | 12.22 | **12.22** | 0.0 % | 11.29 |
| `impulse__rrect-ml` | 11.95 | **11.95** | 0.0 % | 12.03 |
| `impulse__rrect-lg` | 12.04 | **12.04** | 0.0 % | 16.92 |

Zero, on all three, against an acceptance of 5 %. Separable and square integrate the same Gaussian
and the captures say so.

**The cost** (`e2e/bench/budget.spec.ts`, `apple / metal-3`, 60 interleaved rounds, the mobile
390 × 844 @ 3 scene): the frame **2.366 ms at the heavy tap against 2.186 ms at the control**, +0.180
ms inside the 0.2 ms acceptance and inside the run's own drift (the first row, the control's twin,
reads 2.272). The **optics pass does not move** — 0.989 against 0.999 — and the whole cost is on
`body-blur`, 0.083 against 0.045. G0's grid cost +1.1 ms on the optics pass and scaled with the
glass's area; this scales with nothing but the number of sources.

**Inert at 0.** The 33 renderer goldens pass in the foreground, and all 36 re-rendered bed rows are
byte-identical to the canonical 0.14.0 captures — 18 / 18 at each scale (`mapping.txt` §5).
`resolvedMaterialSha256` is re-recorded in both documents: `4475b4dfa6155ce7 → e6edd84292259f3a`
(light), `25a12c887e5b51cb → 874be66ea501621b` (dark), with a `$comment-w26-g1` saying that two
constants left the material's shape and that no value and no pixel moved.

**One width per source, on the mid-span rows** (`probe-read.txt` §2, and the decision the advisory
asked for). The advisory was to blend the chain's `scatterLod` sample back by the ramp where a
mid-span row crosses a floor. **Not taken, and here is why.** No floor is crossed at all (§5 below).
At 1x the mid-span rows (44 → 96) do not move by a single bit, because the recommended 1x width is
the width the chain already draws (§4a). At 2x they move by under 0.0004 of OKLab ΔE. And the one row
that genuinely regresses — `impulse__rrect-lg` at 2x — sits at the THICK end of the ramp, where a
blend that returns the chain's tap at THIN spans would not reach it. The mechanism the advisory names
does not address the regression it would be for; the regression is recorded instead (§4b), which is
what W26 Decision Log 2 (f) already ruled for it.

---

## 2. Part (b) — the instrument, and the finding that stops the 1x fit

Reader D (`w26lib.py`) is reader A's two-component kernel fitted as a **lattice over the whole
impulse tile** instead of over half a dot pitch: the backdrop raster itself convolved with a sharp
and a heavy Gaussian at their own amplitudes, the amplitudes solved exactly by non-negative least
squares at every candidate pair so only the two widths are searched, with a low-order polynomial
absorbing the interior's own smooth structure. It imports `w25lib` and does not edit it (X1).

**Validation 1 — on the model: exact.** Five of six synthetic pairs returned to 0.00 % —
2.00/10.00/0.25 and 3.00/19.50/0.47 among them. The sixth is σ 30 at 1x, where the lattice's own
modulation transfer is 1.3 % and the reader reports that it is at its bound.

**Validation 1b — on the chain's own kernel.** `chain-kernel.txt`'s level-4 point spread is
platykurtic (kurtosis −0.23), neither a Gaussian nor a box, and reader A reduces a kernel by half
maximum, which for that shape is σ 14.33. Reader D returns **13.58 and 13.60** at shares 0.23 and
0.50 — 5.2 % low, inside the 10 % acceptance.

**Validation 2 — against reader A on the 2x rows where reader A is monotone (σ 10 / 13 / 16):
median |Δ| 4.5 %, worst 8.0 %.** Inside the 10 % acceptance. Above σ 19 the two readers part company
in opposite directions and neither is reading a width.

**And then the finding, which is about the FIXTURE and not about any reader.**

| row | interior level | dot peak | peak in 8-bit codes | interior sd |
| --- | --- | --- | --- | --- |
| 1x `impulse__rrect-lg` | 0.4508 | 0.0581 | 10.3 | 0.0055 |
| 1x `impulse__rrect-md` | 0.4287 | 0.0742 | 13.6 | 0.0085 |
| 2x `impulse__rrect-lg` | 0.4508 | 0.0521 | 9.3 | 0.0057 |
| 2x `impulse__rrect-md` | 0.4287 | 0.1619 | 29.6 | 0.0112 |

One 8-bit sRGB code at a level of 0.4508 **is** 0.0059 of linear luma, and the whole interior's
standard deviation is 0.0055. The HEAVY component's own peak is **0.08 – 0.33 codes on every 1x
row**. Quantisation is then a deterministic staircase of the field rather than noise, concentrated
where the field is steepest — at the dot cores — and a spurious NARROW second component fits that
staircase better than the true wide one. On synthetics made at each fixture's own measured level and
dot peak, reader D's error is **79 – 90 % wherever the heavy peak is under half a code, and 1.6 % on
`2x rrect-md` where it is 2.56 codes**. A matched low-pass was built and scanned over 0 → 4 device
px; it quiets the staircase and collapses the sharp component into the heavy one, and no setting
reads the drawn width, so `SMOOTH_SIGMA` is 0 and the scan is kept in the record.

The decisive line: **a heavy component of 13.42 device px and one of 25.0 device px, each at its own
share, differ on 3.3 % of the tile's pixels after quantisation. 96.7 % are bit-identical.** No reader
recovers a width from a file that does not carry it.

**So part (c)'s 1x width fit is STOPPED, as the brief directs.** The fallback is reported and not
taken: a probe fixture whose transmitted dot peak is many codes rather than a fraction of one. Pitch
alone does not buy that — codes do. The arithmetic says a dot of **12 CSS px on a 128 CSS px pitch**
puts the heavy component's peak at roughly nine times its present amplitude, one to three codes at
1x, which is where reader D reads within a few per cent. That is a new probe scene and a native
sitting, which is the user's console.

**The reference read with reader D, recorded beside W25's numbers and rewriting none of them**
(`reader-d.txt` §3): 10.97 / 10.43 / 10.37 device px at 1x on `rrect-md` / `-ml` / `-lg`, and 10.11
at 2x on `rrect-md`, with fit residuals of 0.28 – 0.48 against reader A's usual under 0.1. The
residual is the reader saying, in its own units, that it is not reading them.

---

## 3. Part (c) — the fits, per scale, on the impulse rows

Every number here is in `fits.txt` with its rung.

### 3a. The reference, reader A, this run's own reading — and its conditioning

| profile | row | heavy | share | **sharp** |
| --- | --- | --- | --- | --- |
| 1x | `rrect-md` | 19.52 | 0.473 | 2.79 |
| 1x | `rrect-ml` | 23.27 | 0.674 | 2.74 |
| 1x | `rrect-lg` | 14.67 | 0.727 | 2.77 |
| 2x | `rrect-md` | 11.29 | 0.689 | **1.40** |
| 2x | `rrect-ml` | 12.03 | 1.000 | **11.80** |
| 2x | `rrect-lg` | 16.92 | 0.784 | **9.67** |

The sharp column is the conditioning statistic and it has not been read this way before. At 1x all
three reference rows fit a sharp component of 2.74 – 2.79 device px, which is a sharp component. At
2x only `rrect-md` does (1.40); `-ml` and `-lg` fit sharp components of 11.80 and 9.67, which means
reader A has split a single wide kernel into two wide halves and its "heavy" on those rows is not
the heavy component. **The only conditioned 2x reference row is `impulse__rrect-md`**, and that is
what the 2x width is fitted on.

### 3b. `sizeHeavyTapSigma2x` — FITTED at 10.3

Rows: the three 2x impulse rows, reader A's heavy σ. Condition: the read moves 11.0 → 52.2 device px
over σ 10 → 25 and is monotone over the whole range — about 1.2 device px of reading per device px
of constant near the fit.

| rung | σ2x | `rrect-md` | `rrect-ml` | `rrect-lg` | all 3 | md+ml |
| --- | --- | --- | --- | --- | --- | --- |
| `r0` | inert | 8.76 | 11.23 | 16.59 | 0.1141 | 0.1614 |
| `t10` | 10.0 | 11.04 | 10.44 | 10.51 | 0.2136 | 0.0823 |
| **`t103`** | **10.3** | **11.13** | 10.84 | 11.07 | 0.1808 | 0.0592 |
| `t11` | 11.0 | 11.84 | 11.74 | 11.88 | 0.1419 | **0.0361** |
| `t113` | 11.3 | 12.22 | 11.95 | 12.04 | 0.1419 | 0.0428 |
| `t12` | 12.0 | 12.66 | 12.86 | 12.86 | 0.1518 | 0.0904 |
| `t13` | 13.0 | 14.19 | 14.10 | 14.28 | 0.1855 | 0.1936 |

(the objectives are mean |log(web/native)|; the ladder runs on to σ 25 in `fits.txt`.)

**Residual on the fitted row, `impulse__rrect-md` at 2x: |log| 0.2536 → 0.0143.** The 0.14.0
material draws the deep sample 22.4 % narrower than the reference there; at σ2x 10.3 it is 1.4 %
narrow. On the two unconditioned rows the same constant reads 10.84 against 12.03 and 11.07 against
16.92.

If instead the objective takes `md+ml` at face value the minimum is σ2x 11.0 at 0.0361, and if it
takes all three the minimum is the INERT material at 0.1141 — because the chain's clamped tap grades
with the span at 2x (8.76 → 16.59) where one width per source cannot. Both readings are in the table;
the recommendation follows the conditioning.

### 3c. `sizeHeavyTapSigma` at 1x — NOT FITTED

| rung | σ1x | `rrect-md` | `rrect-ml` | `rrect-lg` | median |
| --- | --- | --- | --- | --- | --- |
| `r0` | inert | 9.08 | 14.36 | 19.78 | 14.36 |
| `t10` | 10.0 | 12.27 | 14.78 | 14.66 | 14.66 |
| `t113` | 11.3 | 11.85 | 14.78 | 19.16 | 14.78 |
| `t13` | 13.0 | 10.05 | 14.84 | 19.38 | 14.84 |
| `t16` | 16.0 | 34.76 | 11.22 | 19.11 | 19.11 |
| `t19` | 19.0 | 61.76 | 3.62 | 12.91 | 12.91 |
| `t25` | 25.0 | 61.76 | 61.75 | 61.69 | 61.75 |

Reader A's 1x median — the statistic G0 measured as exact on a known width — is **flat at 14.4 – 14.8
across σ 10 → 13** while the drawn kernel moves by three device px, and garbage above it. Reader D
cannot read these rows at all (§2). There is no 1x lever any instrument on this bed can see.

### 3d. The share, per scale — the two scales want it in opposite directions

At 1x reader A puts vitrea's heavy share at 0.233 / 0.354 / 0.492 against the reference's 0.473 /
0.674 / 0.727: too LOW. At 2x it puts it at 0.803 / 0.955 / 0.977 against 0.689 / 1.000 / 0.784: too
HIGH on two of three. So the 1x lever is W25's lift on `kDeep` and the 2x lever, if there is one, is
`sizeScatterFloor2x` coming DOWN off 1 — the lift at 2x is not merely inert under the floor, it is
pointed the wrong way, which settles the "lift applied before the floor" half of the brief's question
without a code change.

**1x — `sizeScatterHeavyShareThick1x`, FITTED at 0.25.**

| lift | `rrect-md` | `rrect-ml` | `rrect-lg` | mean \|Δshare\| |
| --- | --- | --- | --- | --- |
| 0 (inert) | 0.233 | 0.354 | 0.492 | 0.2652 |
| 0.15 | 0.291 | 0.519 | 0.629 | 0.1450 |
| **0.25** | **0.337** | **0.664** | **0.649** | **0.0745** |
| 0.35 | 0.391 | 0.790 | 0.649 | 0.0919 |
| 0.45 | 0.429 | 0.804 | 0.649 | 0.0838 |

Condition: the regressor's spread is 0.233 → 0.429 on `-md`, 0.354 → 0.804 on `-ml` and 0.492 →
0.649 on `-lg`, which **saturates at 0.25** (`kDeep` clamps to 1 there and the row stops responding).
Residual 0.2652 → 0.0745, a 72 % reduction. Leave-one-out: `-ml` alone chooses 0.25 and the other
two rows are then short of the reference in the same direction; `-md` alone wants more than 0.45 and
`-ml` overshoots at that value. The rows agree on the sign and disagree on the distance.

**2x — `sizeScatterFloor2x`, DECLINED at 1.**

| floor | `rrect-md` | `rrect-ml` | `rrect-lg` | mean \|Δshare\| |
| --- | --- | --- | --- | --- |
| 1.00 | 0.803 | 0.955 | 0.977 | 0.1174 |
| 0.85 | 0.643 | 0.716 | 0.796 | 0.1140 |
| 0.75 | 0.561 | 0.598 | 0.716 | 0.1997 |
| 0.65 | 0.461 | 0.500 | 0.633 | 0.2932 |
| 0.55 | 0.361 | 0.420 | 0.558 | 0.3782 |

Two reasons, either of which is sufficient. The objective is **flat** — 0.1174 at 1 against 0.1140 at
0.85, a 2.9 % move inside the instrument's own spread — because the reference's `-ml` share is 1.000
and lowering the floor takes that row away as fast as it brings the other two in. And every value
off 1 **moves the thin cells**: `impulse__rrect-sm` at 2x goes 0.337 → 0.301 → 0.281 → 0.257 → 0.244
down the ladder, which X5 forbids. The floor has no `sizeThick` factor to make it inert at the thin
end the way the lift does; that is the structural difference between the two constants, and it is
what decides this.

### 3e. The share's off-row check

`impulse__rrect-sm`, the fourth impulse span and the only one no fit above reads (Decision Log 2 (d)
retired the coarse checkerboards for this job). At 1x the lift leaves it at 0.001 at **every** value
— `sizeThick` is exactly 0 at `sizeSpanMin`, so the law is inert there by construction. That makes
the check vacuous as a check and conclusive as an X5 proof, and both halves are worth stating: the
1x share law cannot be checked off-row on this bed, and it cannot move a thin cell either.

### 3f. `sizeToneLevelFar` re-read on the probe solids — the sign flip PERSISTS, unchanged

`probe-read.txt` §1. Above the knee (span ≥ 96), the interior-level error the solids ask for at the
candidate:

| profile | `light-solid` | `dark-solid` | `mid-dark-solid` |
| --- | --- | --- | --- |
| 1x light | −0.00067 (raise) | +0.00276 (lower) | +0.00432 (lower) |
| 2x light | −0.00067 (raise) | +0.00284 (lower) | +0.00438 (lower) |
| 1x dark | −0.00270 (raise) | +0.00010 (lower) | +0.00045 (lower) |
| 2x dark | −0.00270 (raise) | +0.00010 (lower) | +0.00046 (lower) |

W25's sign flip across backdrops is exactly as it was, and **the candidate moves not one solid by
more than 0.00001**. That is the answer to the question the wave asked: a solid backdrop has no
structure for a heavy width to act on, so the level term's flip was never a symptom of a too-narrow
heavy component and the width does not touch it. `sizeToneLevelFar` stays 0 and stays declined, now
on a measurement rather than on a conjecture.

### 3g. The sharp σ, read at every rung and not fitted

At 1x vitrea's sharp component reads **1.65 – 1.84 device px at every rung of both ladders** against
the reference's 2.74 – 2.79: about 40 % too narrow, and unmoved by everything this child fitted. That
is the named quantity Decision Log 2 (d) asked for, and it is a gap with no constant behind it in
this wave. At 2x vitrea reads 1.78 – 2.07 on `rrect-md` against the reference's 1.40, and the
reference's own `-ml` / `-lg` sharp readings are the unconditioned 11.80 / 9.67 of §3a.

---

## 4. The recommended candidate

| constant | value | how it was arrived at |
| --- | --- | --- |
| `sizeHeavyTapSigma` | **13.418** | not fitted — NAMED. See §4a. |
| `sizeHeavyTapSigma2x` | **10.3** | fitted on `impulse__rrect-md` at 2x, the one conditioned reference row; residual \|log\| 0.2536 → 0.0143. |
| `sizeScatterHeavyShareThick1x` | **0.25** | fitted on the three 1x impulse rows' share; mean \|Δ\| 0.2652 → 0.0745. See §4b. |
| `sizeScatterFloor2x` | 1, unchanged | DECLINED — flat objective, and every value off 1 moves a thin cell (§3d). |
| `sizeScatterHeavyShareThick2x` | 0, unchanged | DECLINED — the 2x share must come down, so a lift is the wrong sign (§3d). |
| `sizeToneLevelFar` | 0, unchanged | DECLINED — the sign flip is invariant to the width (§3f). |

### 4a. Why the 1x anchor is 13.418 and not 0

`heavyTapSigmaAtScale` interpolates LINEARLY between the two anchors (`rampAtScale`). A 2x anchor of
10.3 with a 1x anchor of 0 would make the heavy blur vanish at dpr 1 and be a fraction of a pixel
wide at dpr 1.05 — a discontinuity in the material at fractional ratios that nothing measured and
nobody chose. `CHAIN_LEVEL_SIGMA[4]` = 13.418 device px is the width the pyramid's clamped tap
already draws at dpr 1, so naming it asks the mechanism to draw at dpr 1 what is drawn there today.

**And it costs nothing, measured** (`inert-1x.txt`): all 17 ladder rows of the 1x light profile are
**byte-identical** between `r0` and the candidate width — worst per-channel difference 0 codes,
worst OKLab ΔE move 0.00000 — because `heavyTapPlan` at that σ selects level 4 with a residual of
exactly zero and the separable pair then reproduces the chain tap it replaces. Over the whole probe
set every 1x cell and every dark cell moves by 0.00000 (`probe-read.txt` §2 and §3).

It is also worth more than continuity. W26 G0's tracker entry records that the 1x heavy width is
currently a property of the BACKDROP RASTER's size — the chain stops where `MIN_LEVEL_EXTENT` says
it does, so the same profile over a larger backdrop draws a different heavy width. Naming 13.418
makes it a material constant that every raster reproduces, which is a correctness improvement
independent of any fit.

### 4b. The two rulings that belong to the parent, not to this child

**(i) `impulse__rrect-lg` at 2x.** At σ2x 10.3 reader A's heavy σ on that row goes 16.59 → 11.07
against a reference reading of 16.92. G2's declared stop S15 — "reader A's heavy σ on any fitted row
further from the reference's than at 0.14.0" — fires on it as stated. Three things bear on the
ruling: the reference's own reading on that row is UNCONDITIONED (its fitted sharp component is 9.67
device px, §3a); the regression is the direct, expected consequence of one width per source, which
W26 Decision Log 2 (f) chose knowingly and recorded as a named gap; and the brief's advisory remedy
(blending the chain's tap back by the ramp) does not reach it, because the row is at the thick end
(§1). The choices are to re-state S15 onto the conditioned rows, to accept the regression as the
recorded gap, or to decline the 2x width — in which case the 1x anchor of §4a is the whole of what
W26 lands, and it lands byte-identical.

**(ii) The 1x share lift's off-row cost.** At the candidate, on the 1x light probe set, the OKLab ΔE
mean against the reference **worsens** on the thick spans:

| span | cells | 1x light, inert → candidate | worsened |
| --- | --- | --- | --- |
| 96 | 9 | 0.00475 → 0.00516 | 6 / 9 |
| 128 | 7 | 0.00672 → 0.00767 | 5 / 7 |
| 160 | 12 | 0.00905 → 0.01038 | 7 / 12 |

The 1x width is byte-identical and `sizeScatterHeavyShareThick2x` is 0, so those columns isolate the
share lift exactly. The lift improves the share the impulse rows measure by 72 % and costs 9 – 15 %
on the bed's own perceptual metric at every thick span — which is the shape W25 recorded and
declined the lift on, reproduced here with the width in place and the checkerboards' objective out
of the argument. The wave's premise was that the share could be raised once the width was right; at
1x the width could not be made right, so the premise was never tested. Declining the lift is the
consistent reading of W25; taking it is a choice to weight the kernel's identified share over the
bed's ΔE, and it is the parent's.

For completeness, the same table at 2x, where the columns isolate the WIDTH: span 32 6 / 11 cells
worse, 44 6 / 9, 96 5 / 9, 128 3 / 7 (the mean improves), 160 7 / 12.

---

## 5. The bed at the candidate

**X5 — every probe cell of span ≤ 44, 81 of them: worst OKLab ΔE move 0.00017**, against a bound of
0.001 (`probe-read.txt` §3). Every 1x cell and every dark cell moves by exactly 0. The largest movers
are all 2x light and all under a fifth of the bound.

**The fourteen thick regression floors and every adopted bound: PASS.** The frozen bed
(calibration + validation, both tiers, all six profiles) was re-captured at the candidate and
`adopted-thresholds.test.ts` was run over it through `VITREA_MATRIX_PATH` — the file that is the only
copy of those numbers, rather than a second copy of them. X3 keeps the holdout for G2, so the gate's
input was assembled by `g1-gate.py` as the candidate's 170 calibration/validation cells beside the
canonical matrix's 59 holdout cells; the holdout rows in that run are the frozen bed's own and are
evidence about nothing in this candidate.

The result is **36 of 38 assertions passing untouched, and 38 of 38 once two lines are removed from
`PREDICATE_EXCLUDES`**. The two failures are one event and it is an improvement: at the candidate the
conditioning predicate ADMITS `texture / calibration / checkerboard__rrect-md__rest` and
`checkerboard__toolbar-group__rest` on `apple-macos-26.5-2x-light-standard`, which the 0.14.0 bed
excludes as ill-conditioned. Both then meet `TEXTURE_TIER_2X_LIGHT`'s bounds. The edit is the one
CLAUDE.md describes — `PREDICATE_EXCLUDES` must equal the machine's output — and it is G2's to make;
this child made it in a scratch copy, ran the gate, and reverted it.

`proves every regression floor stands on a genuinely unmet bound` also passes, so no floor became
removable either: the candidate moves no floored row past its bound in either direction.

---

## 6. What could not be read

- **The 1x heavy width, by any instrument on this bed** (§2). The fixture, not the reader.
- **The reference's 2x heavy component on `impulse__rrect-ml` and `-lg`** (§3a). Reader A's fitted
  sharp components there are 11.80 and 9.67 device px; those two rows' "heavy" is the second half of
  a split, not a component. The ledger's 12.03 and 16.92 stand as recorded and this reading is
  recorded beside them.
- **The 1x share off-row** (§3e), because the law that carries it is inert at the only span left.
- **The holdout**, deliberately: X3 gives it to G2, once, at the dry run.
- **The user's eye** (X6): the wave's clause 8 is not this child's.

---

## 7. Follow-on (2026-09-10): the coarse checkerboards read the 1x width, and the reference's 1x heavy component turns out not to be identified

**Two rulings recorded first, both the parent's, both taken as given here.**

**(i) S15 is re-stated.** It reads "any fitted row, or any row whose reference two-component fit is
conditioned (sharp under 4 device px)". It therefore does **not** fire on `impulse__rrect-lg` at 2x:
that row is not fitted and its reference fit returns a sharp component of 9.67 device px, which §3a
measured as one wide kernel split in half. The row's 16.59 → 11.07 move is the gap W26 Decision Log
2 (f) recorded when it chose one width per source, and it stays recorded rather than blocking.
§4b (i) is superseded by this and its numbers stand where they are.

**(ii) `sizeScatterHeavyShareThick1x` = 0.25 is DECLINED** at the current 1x width, on the evidence
shape W25 declined it on: the bed's OKLab ΔE worsens 9–15 % on every 1x thick span (§4b (ii)). It is
re-tested only if the 1x width becomes fittable. §7.6 is that test, and it does not become fittable.

### 7.1 The dark scheme moved by exactly 0 because the candidate was never in the dark document

`probe-read.txt`'s dark columns are the inert material re-rendered, not the candidate. The cause is
mechanical and it is mine: `g0-candidate.py`'s `light:` scope writes a constant into the LIGHT
document only, and the dark profile is a **difference document resolved over
`DEFAULT_MATERIAL_PROFILE`, not over the light patch** — `tuned-profiles.test.ts` resolves both as
`withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch)`, and the dark patch names only
`adaptiveTint*`, `backdropTone*`, `tintShadeStrength`, `outerShadow` and five `optics.regular` keys.
So a dark capture at a scratch rung takes this wave's constants from the CODE default, which is 0,
and the mechanism is off.

Nothing in the dark difference document makes the heavy width inert. **A landed constant does reach
the dark scheme**, because landing edits `DEFAULT_MATERIAL_PROFILE` — which is exactly what W15's and
W25's own entries mean by "the defaults this difference document inherits" and "the dark document's
resolved material moves with it". Verified by resolving both committed documents:
`optics.regular.rimAlongSideSlope` is 0.1 in the light patch, 0.1 in the resolved dark material and
0.1 in the code default. **So G2's declaration WILL move the dark bed**, and the dark bed had to be
measured before it does.

`g1-dark.sh` re-captures the whole probe set in both dark profiles with the candidate written into
**both** documents (`both:` scope), which reproduces at capture time what a landing reproduces at
declaration time. Against the inert `p0`:

| span | 1x dark, inert → candidate | worsened | 2x dark, inert → candidate | worsened |
| --- | --- | --- | --- | --- |
| 32 | 0.00225 → 0.00225 | 0 / 12 | 0.00217 → 0.00218 | 5 / 12 |
| 44 | 0.00284 → 0.00284 | 1 / 9 | 0.00278 → 0.00275 | 0 / 8 |
| 96 | 0.00447 → 0.00465 | 5 / 9 | 0.00612 → 0.00600 | 2 / 9 |
| 128 | 0.01703 → 0.01695 | 3 / 7 | 0.02116 → 0.02113 | 2 / 7 |
| 160 | 0.02173 → 0.02167 | 3 / 12 | 0.02582 → 0.02767 | 7 / 12 |

X5 in the dark scheme over 41 thin cells: worst move **0.00013**, against a bound of 0.001. The 1x
share lift is roughly NEUTRAL in the dark scheme (128 and 160 improve slightly, 96 worsens) where it
was clearly negative in light, and the 2x width costs the largest dark span the way it costs the
largest light one. Neither reading changes ruling (ii), and the light bed remains the one that
declines the lift.

### 7.2 Reader D on the coarse checkerboards — the codes are there, and `checkerboard-64` reads

§2's finding was about the impulse tile's CONTRAST, and reader D was never specific to it. The
coarse checkerboards carry, in the native interior eroded 16 CSS px (`checker.txt` §A):

| row | interior level | amplitude p2..p98 | **codes** |
| --- | --- | --- | --- |
| 1x `checkerboard-64__rrect-md` | 0.4342 | 0.5132 | **73.0** |
| 1x `checkerboard-64__rrect-ml` | 0.4452 | 0.4764 | **68.0** |
| 1x `checkerboard-64__rrect-lg` | 0.4621 | 0.4426 | **63.0** |
| 1x `checkerboard-32__rrect-md` | 0.4564 | 0.4567 | 65.0 |
| 1x `checkerboard-32__rrect-lg` | 0.4969 | 0.3827 | 54.0 |

against the 1x impulse tile's heavy component of 0.08–0.33 codes. On synthetics made at each row's
own level and at a FIXED transmission — calibrated so a 3.0 / 19.5 / 0.47 kernel reproduces that
row's observed contrast, so a wider kernel flattens the checkerboard the way it really would rather
than being handed back the codes it destroyed — through the sRGB 8-bit step (`checker.txt` §B):

| row | σh 10.0 | 13.418 | 19.5 | 25.0 | 30.0 |
| --- | --- | --- | --- | --- | --- |
| `checkerboard-64__rrect-lg` | **1.8 %** | **0.3 %** | **0.5 %** | **0.0 %** | **0.1 %** |
| `checkerboard-64__rrect-ml` | 0.8 % | 0.3 % | 1.0 % | 1.2 % | 1.8 % |
| `checkerboard-64__rrect-md` | 6.7 % | 0.5 % | 3.5 % | 0.2 % | 1.3 % |
| `checkerboard-32__rrect-lg` | 15.6 % | 4.7 % | 78.0 % | 90.1 % | 91.6 % |
| `checkerboard-32__rrect-ml` | 37.0 % | 48.7 % | 72.4 % | 90.1 % | 91.8 % |

**`checkerboard-64` is an instrument and `checkerboard-32` is not**, and the split is exactly the
modulation transfer: a 32 CSS px pitch passes exp(−2π²σ²/32²) of the fundamental, which is 6 × 10⁻⁴
at σ 19.5 and 6 × 10⁻⁶ at σ 25 — those rows fail in the FLOAT column too, before any quantisation.
The 64 px pitch passes 16 % at 19.5 and 5 % at 25, and on 63–73 codes that is ten codes and three.
The chain's own platykurtic level-4 kernel reads **13.58 / 13.47** at shares 0.23 / 0.50 against the
14.33 its half maximum asks for — 5.2 % low, the same as reader D on the impulse tile.

This does not contradict W26 G0 §7. What G0 retired was a SINGLE-Gaussian objective, which is
dominated by the kernel's core and answers about the sharp component at any width (Decision Log
2 (d)). A two-component lattice reader is a different instrument on the same pixels.

### 7.3 The cross-check at 2x, where three instruments are conditioned

`checker.txt` §C, on `rrect-md` at 2x:

| rung | reader A, impulse | reader D, impulse | reader D, `checkerboard-64` |
| --- | --- | --- | --- |
| `r0` inert | 8.76 | 9.91 | 8.69 |
| `t10` | 11.04 | 11.06 | 9.57 |
| `t13` | 14.19 | 14.10 | 12.57 |
| `t16` | 17.83 | 17.94 | 16.05 |

Monotone, same ordering, the checkerboard 10–13 % below the impulse readers. That is inside the
10 % acceptance at the low end and just outside it at the top, and it is what earns the checkerboard
the right to read the 1x rows the impulse tile cannot.

### 7.4 The 1x ladder — a readable lever, at last

`checker.txt` §E, `checkerboard-64` at 1x:

| rung | σ1x | `rrect-lg` | `rrect-ml` | `rrect-md` |
| --- | --- | --- | --- | --- |
| `r0` | inert | 18.71 | 16.44 | 16.53 |
| `t10` | 10.0 | 10.28 | 10.34 | 9.90 |
| `c1` | 13.418 | 18.71 | 16.44 | 16.53 |
| `t16` | 16.0 | 21.34 | 18.99 | 19.18 |
| `t19` | 19.0 | 24.20 | 22.18 | 27.14 |
| `t22` | 22.0 | 27.21 | 24.11 | 29.42 |
| `t25` | 25.0 | 30.03 | 26.93 | 31.76 |

Monotone from 13.418 up, at a slope of about 0.95 device px of reading per device px of constant on
`-lg` and `-ml`. `c1` reads identically to `r0` on every row, which is §4a's byte-identity seen from
the instrument side. **This is the 1x lever the wave was chartered to find**, and §2's verdict is
narrowed accordingly: the impulse FIXTURE cannot carry the 1x heavy component, and the coarse
checkerboard can.

### 7.5 And then the two instruments disagree about the reference by a factor of 2.3

`checker.txt` §D, the reference at 1x on `checkerboard-64`: heavy **8.42 / 8.68 / 8.71** on `-lg` /
`-ml` / `-md`, sharp 1.35 / 1.21 / 1.41, share 0.648 / 0.536 / 0.429, residual 0.056–0.065. Reader A
on the 1x impulse tile reads the same three surfaces at **14.67 / 23.27 / 19.52**.

So the checkerboard says vitrea's inert 1x heavy component (18.71) is more than TWICE as wide as the
reference's (8.42); the impulse tile says it is 30 % too narrow. **The two instruments do not agree
on the sign of the error the whole wave exists to close.** The checkerboard's sign is the one
claims §5.113 §2 already recorded with readers B and C — vitrea 32–46 % too wide on these very rows.

### 7.6 One kernel, two tiles — the joint fit, and its control

If the disagreement were fit noise, one (σ_sharp, σ_heavy, share) fitted across both tiles at once —
per-tile gain, per-tile polynomial, each tile's residual normalised by its own signal — would
reconcile them. **The control is vitrea, whose kernel is known**: at `r0` the deep sample is the
chain's own level 4, half-maximum σ 13.42 device px, mixed with a body of 1.25 (`joint.txt`).

| 1x, `checkerboard-64` + `impulse` | `rrect-lg` | `rrect-ml` | `rrect-md` |
| --- | --- | --- | --- |
| joint heavy — **reference** | 9.37 | 9.48 | 9.02 |
| joint heavy — **vitrea r0** (truth 13.42) | 11.28 | 10.28 | 11.55 |
| per-tile residual, reference (impulse / checker) | 0.472 / 0.128 | 0.282 / 0.150 | 0.287 / 0.146 |
| per-tile residual, vitrea r0 | 0.568 / 0.082 | 0.190 / 0.074 | 0.411 / 0.085 |

**The control fails.** The joint fit under-reads vitrea's known 13.42 by 14–23 %, and it lands near
the checkerboard's answer rather than between the two — because the checkerboard has sixty times the
codes and wins even after the per-tile normalisation. Its residual on the impulse tile is 2–7 times
its residual on the checkerboard, for the reference and for vitrea alike: **one two-Gaussian kernel
does not describe both tiles of the same surface**, and that is true of vitrea, whose kernel really
is two components.

Every instrument's bias on vitrea's known 13.42, and the reference debiased by it:

| instrument | reads vitrea's 13.42 as | bias | reads the reference as | debiased |
| --- | --- | --- | --- | --- |
| reader A, 1x impulse (median) | 14.36 | ×1.07 | 19.52 | **18.2** |
| reader D, `checkerboard-64` `-lg` | 18.71 | ×1.39 | 8.42 | **6.0** |
| reader D, `checkerboard-64` `-ml` | 16.44 | ×1.23 | 8.68 | **7.1** |
| joint, `-lg` | 11.28 | ×0.84 | 9.37 | **11.1** |
| joint, `-ml` | 10.28 | ×0.77 | 9.48 | **12.4** |

A factor of **3.0** between the extremes, and 1.6 between the joint fit and the impulse tile after
each is corrected by its own measured bias. The reference's residuals are 5–7 times reader D's
residual on its own synthetics (0.009–0.013) on every row of every tile, which is the readers saying
in their own units that **Apple's kernel is not two Gaussians** and that which two Gaussians you
recover depends on which backdrop you read it through.

### 7.7 Verdict

**The 1x width is not fitted, and the reason is now a better one than §2's.** There is a readable 1x
lever (§7.4) and there is no identified target for it: fitting `sizeHeavyTapSigma` on
`checkerboard-64` would take it to about 8 device px, NARROWER than the 13.418 the material already
draws; fitting it on the impulse tile would take it to about 19.5, wider; the joint fit says 9–12 and
fails its own control. Fitting any of them is fitting an instrument, which is the failure mode this
wave was chartered to avoid.

**Ruling (ii) therefore stands unchanged and the share lift is not re-tested at a new width**, there
being no defensible new width to test it at.

**What this puts in question is larger than the fit.** W25 clause 2 asks for "the heavy σ within
15 % of the reference's at both scales", and §7.5 and §7.6 say the reference's heavy σ is not a
single number: it is a projection of a kernel that is not two Gaussians onto a two-Gaussian basis,
and the projection depends on the backdrop. Claims §5.113 §2's 19.52 / 11.29 are that projection
through the impulse tile, and the readings here are the same surfaces' projection through
`checkerboard-64`; both are recorded and neither is rewritten.

**The next instrument, and it needs no sitting.** A kernel model with more than two components — or
two components with a shape parameter — fitted jointly across three or more backdrops of the same
surface, and **validated first on vitrea's own known kernel**, which is the control every reader in
this wave should have had and only §7.6 built. The wider-pitch impulse probe scene of §2 remains the
fallback for the impulse-side reading and is still a sitting; it is now the second priority, because
a better fixture does not help an unidentified target.

**What §7 leaves the candidate.** Nothing moves. `sizeHeavyTapSigma` stays at 13.418 on §4a's
grounds, which are byte-identity and the continuity of `rampAtScale` rather than a fit;
`sizeHeavyTapSigma2x` stays at 10.3 on §3b's, which is the one conditioned reference row; the share
lift and the other three constants stay declined.
