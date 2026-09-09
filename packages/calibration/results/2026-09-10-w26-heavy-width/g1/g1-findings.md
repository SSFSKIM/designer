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
