# W26 G1b — the point spread without a shape assumption: findings

**SPIKE. No material change, no renderer code, no canonical write.** Evidence in this directory:
`align.txt` (the backdrop rasters verified against the fixtures), `synth.txt` (the smoothness
weight chosen, and the reader's bias by shape), `control.txt` (the binding control, both forms),
`reference.txt` (Apple's kernel, per surface per scale, with its sensitivity), `truth.txt` (what
vitrea itself draws, from the arithmetic), and the scripts that produced each. Everything was read
from `apps/reference-apple/fixtures/` and the canonical `web-captures/`, both read-only; nothing
was rendered and nothing was written outside this directory.

---

## 0. What this child concludes, in one paragraph

**The brief's method fails its control, and the failure names the instrument the wave actually
needs.** A free forty-node radial profile fitted jointly across eight backdrops recovers five very
different known kernels from synthetics built on those same backdrops to 0.5–8 %, and then, on
vitrea's own captures, fits the pixels better than the kernel vitrea demonstrably draws while
getting its half-maximum width wrong by up to a factor of two and its second moment by two-fold
under choices that should not matter. Forty parameters are not identified by this bed. **A width
is.** On the one band where the drawn kernel is a single chain tap with no share to average, a scan
over the LOD puts the minimum at 3.7 against the arithmetic's 3.780 and rises steeply on both
sides; and asked as the two-parameter family the material itself computes — the body vitrea already
draws, plus what `heavyTapPlan` would build for a heavy σ, at a share — the same eight backdrops
return the drawn width to **0.6 %** on both 1x bands and the drawn share to **0.043** everywhere.
Read with that instrument, **Apple's heavy width is 8.6–9.2 device px at 1x on both surfaces and in
both schemes, and 7.9–9.0 at 2x** — so vitrea's 13.418 at dpr 1 is about **50 % TOO WIDE**, not
30 % too narrow, and its share is already right to within 0.06. The `checkerboard-64` sign of W26
G1 §7.5 was the correct one and the impulse tile's 19.5 was the outlier. Two further corrections
follow: **two Gaussians describe Apple's kernel as well as forty free parameters do** (the residual
gap is 0.05–0.12 of a display code), so §7's "Apple's kernel is not two Gaussians" is not supported
by this reading; and **no radially symmetric kernel of any shape explains Apple's interior to better
than about 1.9 display codes** where vitrea's is explained to 0.83–1.17, which is the one thing here
that is genuinely unread.

---

## 1. Before any kernel: the model's unstated premise, measured

`align.txt`. Reader E's whole model is `observed ≈ a·(backdrop ⊛ K) + n(depth)`. If the committed
raster were displaced from the one the harness drew, the fit would absorb it by widening K, and
most on the finest pitches — the exact shape of the disagreement this spike exists to explain.

On the `rrect-sm` scenes, over every pixel more than 56 CSS px outside the contour, the fixture's
own free background matches the committed raster at shift (0, 0), gain **1.0000**, offset
**0.00000** and a residual of **0.00 display codes** — on every backdrop, at 1x and 2x, in both
schemes. The single exception is `hc-text` at 2x, at 1.57 codes, which is the harness's own text
antialiasing. So a recovered width cannot be a displaced raster, and this is not assumed anywhere
below.

---

## 2. The reader, and the two things building it taught

`w26blib.py`. K(r) on a 40-node radial grid, non-negative, unit mass, second-difference penalty,
fitted jointly across every thick untinted backdrop of one surface at one scale — `impulse`,
`checkerboard-64`, `-32`, `-16`, `-8`, `-4`, `hc-text` and `photo` — with a per-backdrop gain and a
low-order polynomial in DEPTH beside it, over a stated band of depth well inside the rim.

Two construction facts are worth recording because each one silently destroyed the reader before it
was found, and both were found by making the reader recover a kernel it had generated itself.

**The reduction must be a QR, not a Gram matrix.** Forty basis columns are one backdrop blurred at
forty neighbouring radii and are correspondingly collinear. Forming `A Aᵀ` squares that condition
number and a Cholesky of it loses exactly the digits the fit needs: built that way the reader
settled 25 % off in MTF and 35 % off in second moment on NOISELESS data of its own making. Reduced
by a thin QR of `[Aᵀ | nuisance]` per row it returns the generating kernel, and every sweep is then
arithmetic on 41 × 41 matrices, which is what makes eight restarts affordable.

**The alternation needs hundreds of sweeps.** Twelve left the objective six orders of magnitude
above what the generating kernel itself achieves.

**Rows are weighted by their quantisation floor, not by their own standard deviation.** Normalising
each row by its own signal — what every earlier reader in this wave did — gives a row that is
entirely quantisation staircase the same vote as one carrying seventy display codes. On the 1x
`impulse` tile that is not hypothetical: W26 G1 §2 measured its whole surviving interior modulation
at about one code.

**The smoothness weight was chosen on synthetics and frozen at λ = 0.003** (`synth.txt`). Each
synthetic is the fixture's own backdrop raster convolved with a known kernel, gained and offset to
the level and amplitude the real capture of that row carries, and put through the 8-bit sRGB step.

| kernel | MTF err (1/512..1/8) | HWHMσ true → read | RMSσ true → read |
| --- | --- | --- | --- |
| Gaussian σ 8 | 0.5–4.9 % | 8.00 → 7.41–7.93 | 8.03 → 8.12–8.97 |
| two Gaussians 2.0/19.5 @ 0.47 | 0.6–6.9 % | 2.02 → 1.63–2.05 | 13.30 → 13.06–13.90 |
| the chain's own level-4 kernel | 0.5–4.8 % | 14.63 → 13.54–14.46 | 15.54 → 15.58–15.91 |
| vitrea's real composite | 0.8–2.8 % | 1.27–1.51 → 1.17–1.42 | 10.38–13.90 → 10.62–13.98 |
| exponential (cusped, heavy-tailed) | 8.0–23.9 % | 4.72 → 3.90–6.34 | 13.60 → 13.55–13.93 |

So the method and the eight backdrops' conditioning are, in principle, adequate: the reader is not
preferring a shape, and it recovers vitrea's own composite to under 3 %.

---

## 3. The control, and it does not pass

`control.txt`. The target is `g1b-truth.py`'s statement of what `wgsl/optics.ts` actually convolves
the backdrop with at the frozen 0.14.0 material, over the same band the fit is taken on.

### 3a. Two corrections to that statement, found by the control

**The body is not a Gaussian of `blurSigma`.** `bodyBlurPlan(1.25, plan)` picks the deepest chain
level whose advisory σ is at or below 1.25 — `CHAIN_SIGMA_AT_LEVEL_1` is 1.2, so level 1 — and
applies the residual √(1.25² − 1.2²) = 0.35 level-0 texels on top of it. The body sample is
therefore the chain's LEVEL-1 kernel, whose measured half-maximum σ is **1.542 and not 1.2** and
whose kurtosis is −0.43, blurred by a third of a texel. Reading it as a Gaussian of 1.25 understates
its width by about a quarter and misstates its shape. W25 G0's reader A reads vitrea's sharp
component at 1.65–1.84 device px at 1x, which is this and not 1.25.

**`kScatter` over a band must be averaged over the band's own pixels.** A ring at depth 16 holds far
more pixels than one at depth 45, so a uniform average over the band's edges states a share the
surface does not draw. On `rrect-md` at 2x the difference is 0.924 against 0.913.

### 3b. The free profile — FAILS

| surface | sc | band | MTF 1/64..1/8 | MTF 1/512..1/8 | HWHMσ drawn/read | RMSσ drawn/read |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1 | 16–48 | **2.5 %** | **2.3 %** | 1.793 / 1.335 (25 %) | 11.005 / 9.924 (9.8 %) |
| `rrect-md` | 2 | 16–48 | 35.4 % | 27.7 % | 2.230 / 1.389 (38 %) | 10.341 / 13.107 (27 %) |
| `rrect-lg` | 1 | 16–80 | **6.8 %** | **5.4 %** | 1.813 / 1.460 (19 %) | 12.902 / 16.087 (25 %) |
| `rrect-lg` | 2 | 16–80 | 32.4 % | 22.5 % | 2.246 / 2.188 (2.6 %) | 13.839 / 13.643 (1.4 %) |
| `rrect-lg` | 2 | 50–80 | 93.9 % | 73.1 % | 9.363 / 7.306 (22 %) | 14.193 / 14.980 (5.5 %) |
| `rrect-md` | 2 | 40–48 | 55.0 % | 38.1 % | 3.547 / 3.592 (1.3 %) | 10.669 / 11.737 (10 %) |

**The control fails the brief's acceptance on every band.** The two 2x bands at the bottom are the
best case the bed offers — at dpr 2 `sizeScatterFloor2x` is 1 and the depth ramp runs out at 50 CSS
px, so past that `rrect-lg` draws EXACTLY one chain tap, with no share to average and no depth
dependence — and they fail hardest.

Three things say what kind of failure it is.

**The residual at the drawn kernel is barely worse than at the fit.** Per row, in units of that
row's own quantisation step, on `rrect-md` at 1x: 1.11 / 1.17, 1.46 / 1.50, 1.24 / 1.28 (fit /
drawn) across the checkerboards. The pixels do not prefer the recovered profile by much; the fit
buys about a tenth of a display code with a shape twice as wrong.

**The half maximum is not a measured quantity here.** It is set by where the profile crosses half
its own peak, which for a two-component kernel depends on a peak-height ratio the 8-bit data cannot
pin, and on the profile at radii the backdrops' highest frequency cannot resolve. The regulariser
sets it, not the data. On the same fits the MTF at 1x agrees to 2.3–5.4 % while the half maximum
disagrees by 19–25 %; both cannot be right, and the MTF is the one the data carry.

**The 2x MTF failure is structural and identifiable.** A trilinear blend of two chain levels RINGS —
`rrect-lg` at 2x reads a modulation of −0.015 at 1/16 cycles per px — and a non-negative smooth
radial profile cannot reproduce a transform that crosses zero. Where the drawn kernel is a pure
chain tap, the comparison is being taken where its modulation is at the 1 % floor and its sign is
about to change.

### 3c. The same question in two parameters — and this one all but passes

The body vitrea already draws, plus what `heavyTapPlan` would build for a heavy σ, mixed at a
share: the composite `wgsl/optics.ts` computes, with the two numbers the material would name left
free, fitted to the PIXELS.

| surface | sc | band | σ drawn | σ read | Δ | k drawn | k read | Δ | resid | free |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1 | 16–48 | 13.500 | **13.418** | **−0.6 %** | 0.494 | 0.501 | +0.007 | 1.083 | 1.059 |
| `rrect-md` | 2 | 16–48 | 8.800 | 7.961 | −9.5 % | 0.913 | 0.872 | −0.041 | 1.205 | 1.167 |
| `rrect-lg` | 1 | 16–80 | 13.500 | **13.418** | **−0.6 %** | 0.684 | 0.678 | −0.006 | 0.859 | 0.825 |
| `rrect-lg` | 2 | 16–80 | 13.100 | 12.235 | −6.6 % | 0.950 | 0.916 | −0.034 | 1.024 | 0.989 |
| `rrect-lg` | 2 | 50–80 | 13.100 | 12.396 | −5.4 % | 1.000 | 0.957 | −0.043 | 0.430 | 0.342 |
| `rrect-md` | 2 | 40–48 | 8.800 | 7.887 | −10.4 % | 0.974 | 0.935 | −0.039 | 0.489 | 0.407 |

`σ drawn` is the drawn tap expressed in the same naming the family returns — the σ whose
`heavyTapPlan` kernel has the nearest modulation transfer, compared linearly and only where the
drawn tap still transfers 2 %, because the blend rings. Where the tap is a whole chain level, which
is every 1x row on this bed, that is `CHAIN_LEVEL_SIGMA[4]` exactly.

**Five of six bands inside 10 %, worst 10.4 %, and both 1x bands at 0.6 %.** The 1x bands are where
the drawn tap lies exactly in the fitted family; the 2x bands, where `scatterLod` is fractional and
the drawn tap is a trilinear blend no member of the family can be, read 5–10 % narrow. That is the
family's own bias against a kernel outside it, measured, and it is the correction to apply to a 2x
reading of the reference.

### 3d. And the same scan, with no family at all

On `rrect-lg` at 2x past 50 CSS px, asking only which chain LOD best explains the band:

| lod | 2.0 | 2.5 | 3.0 | 3.5 | **3.8** | 4.0 | 4.5 | 5.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| resid (quantisation steps) | 3.954 | 3.079 | 2.027 | 0.823 | **0.563** | 1.254 | 2.049 | 3.461 |

The minimum is at lod **3.7** against the arithmetic's **3.780**, and the residual rises by a factor
of two within half a level either side. The free profile reaches 0.342 against the best pure tap's
0.447 — it fits better, and it is that extra tenth of a step that it pays for with an unidentified
shape.

**So the control's verdict, stated exactly.** The brief's acceptance — 10 % on the MTF over
1/64..1/8 AND 10 % on the half maximum — is **not met, on any band**. Read as a diagnosis rather
than a gate: the free profile's SHAPE is not identified by this bed; a one- or two-parameter WIDTH
is, to 0.6 % where the drawn kernel is in the family and 5–10 % where it is not. Everything in §4
is read with the instrument that passed and is quoted with that instrument's measured bias.

---

## 4. Apple's kernel

`reference.txt`. Same rows, same bands, same grid, same frozen λ; the only difference between the
two sources is the material.

### 4a. The width and the share

| surface | sc | scheme | **reference σ** | **share** | resid | vitrea σ | share | resid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1 | light | **9.11** | **0.436** | 2.149 | 13.418 | 0.499 | 1.083 |
| `rrect-lg` | 1 | light | **8.55** | **0.648** | 1.926 | 13.418 | 0.678 | 0.859 |
| `rrect-md` | 2 | light | **7.92** | **0.831** | 2.099 | 7.961 | 0.872 | 1.205 |
| `rrect-lg` | 2 | light | **8.97** | **0.987** | 2.045 | 12.235 | 0.916 | 1.024 |
| `rrect-md` | 1 | dark | **9.18** | **0.422** | 2.002 | 13.418 | 0.519 | 0.988 |

σ is `sizeHeavyTapSigma` in device px — the constant the material would name, since the family
fitted IS `heavyTapPlan`'s output. Debiased by §3c's measured family bias (−0.6 % at 1x, −5 to
−10 % at 2x), Apple's heavy width is **8.6–9.2 device px at 1x** and **8.7–9.6 at 2x**.

**Three readings of the wave's own question follow directly.**

- **Vitrea's heavy component at dpr 1 is about 50 % TOO WIDE**, not 30 % too narrow. It draws
  13.418 against 8.6–9.2. W26 Decision Log 3 (c) named 13.418 for continuity and byte-identity and
  called it free; on this reading it is not the right width, it is the wrong one by half.
- **At dpr 2 `rrect-md` is right and `rrect-lg` is not.** Read through the same instrument,
  vitrea 7.96 against the reference's 7.92 on the 96-span surface; 12.24 against 8.97 on the
  160-span one. That is precisely the gap W26 Decision
  Log 2 (f) accepted when it chose one width per source: the reference's width barely grades with
  span (8.6 → 9.0 across a 96 → 160 span) while `sizeScatterGainFar2x` makes vitrea's grade from
  8.0 to 12.2. **The reference does not want that grading at all.**
- **The share is already close.** Reference 0.436 / 0.648 at 1x against vitrea's 0.499 / 0.678;
  0.831 / 0.987 at 2x against 0.872 / 0.916. Every difference is under 0.07 and three of five are
  under 0.045, which is inside the control's own share bias. W25 clause 2's "share within 0.05"
  is met at the 0.14.0 material — read this way — and the constant W25 and W26 both declined
  (`sizeScatterHeavyShareThick1x`) would have moved it the wrong way.

### 4b. The dark scheme agrees with the light one

`rrect-md` at 1x reads 9.18 in the dark standard against 9.11 in the light — 0.8 % apart, on six
rows instead of eight (`impulse` and `hc-text` are not captured there). Whatever this width is, it
is not a property of the scheme.

### 4c. Two Gaussians ARE enough, and that reverses a recorded conclusion

Every family fitted to the same pixels, in units of each row's own display step (`reference.txt`
§3b). `free` is the forty-node profile and is a lower bound no shape can beat.

| surface | sc | one Gaussian | two Gaussians | body + Gaussian | body + chain tap | free |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` 1x reference | | 2.691 | **2.047** | 2.150 | 2.149 | 1.959 |
| `rrect-lg` 1x reference | | 2.534 | **1.905** | 1.927 | 1.926 | 1.787 |
| `rrect-md` 2x reference | | 2.363 | **2.092** | 2.105 | 2.099 | 2.011 |
| `rrect-lg` 2x reference | | 2.101 | **2.038** | 2.043 | 2.045 | 1.985 |
| `rrect-md` 1x vitrea | | 1.832 | 1.075 | 1.079 | 1.083 | 1.059 |
| `rrect-lg` 1x vitrea | | 2.232 | 0.855 | 0.854 | 0.859 | 0.825 |

**Two Gaussians come within 0.05–0.12 of a display code of forty free parameters, on the reference
as on vitrea.** One Gaussian does not — it is 0.5–0.9 codes worse, which is why a single-width
objective was retired. So the shape of Apple's kernel is, as far as this bed can tell, a
two-component kernel, and W26 Decision Log 4 (e)'s "Apple's kernel is not two Gaussians" and the
Surprises entry that repeats it **are not supported by this reading**. The factor-of-three
disagreement §7.5 recorded came from fitting two Gaussians to ONE backdrop at a time — the impulse
tile alone at 1x carries about one display code — not from a shape the basis cannot hold. Fitted
across eight backdrops at once, on the pixels, the two-Gaussian answer is stable and agrees with the
mechanism family: **sharp 1.29–1.40, heavy 8.65–9.07** on four of the five rows.

The exception is `rrect-lg` at 2x, where the two-Gaussian fit returns 7.77 / 15.72 at a share of
0.409 — two wide halves of one kernel, the same split W26 G1 §3a diagnosed on the reference's own
2x rows, and its residual advantage over the mechanism family there is 0.007 of a code, which is
nothing. That row's two-Gaussian numbers are not a reading.

The same table also reverses the recorded reading of the SHARP component. The reference's sharp
Gaussian is **1.29–1.40** device px against vitrea's **1.64–1.75** on every row where the fit is
conditioned — vitrea's is 20–30 % TOO WIDE, where claims §5.120 §3g recorded it as about 40 % too
narrow against a reference reading of 2.74–2.79.

### 4d. Can vitrea's mechanism draw it, and at what σ

Yes, and that is the `body + chain tap` column above: it is within 0.02 of a display code of the
free two-Gaussian answer on every reference row, so the mechanism W26 G1 built carries Apple's
kernel as well as anything else this bed can distinguish. The σ it needs, per scale, is §4a's
column: **about 9.1 at 1x on span 96 and 8.6 on span 160; about 8.7 at 2x on span 96 and 9.6 on
span 160** after the family bias. The two scales want nearly the same number, and neither wants a
strong span grading.

### 4e. The reading does not move

`reference.txt` §5, the same fit under every choice that could have made it. `σ` in device px:

| surface | sc | as read | deeper band | deepest band | tiled outside | no `photo` | no `impulse` | no fine checkers | checkers only |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1 | 9.11 | 8.79 | 9.10 | 9.11 | 9.07 | 9.14 | 9.11 | 9.27 |
| `rrect-md` | 2 | 7.92 | 7.63 | 7.58 | 7.92 | 7.91 | 7.92 | 7.84 | 7.52 |
| `rrect-lg` | 1 | 8.55 | 8.45 | 8.38 | 8.55 | 8.35 | 8.56 | 8.55 | 8.16 |
| `rrect-lg` | 2 | 8.97 | 9.41 | 9.52 | 8.97 | 8.87 | 8.96 | 8.94 | 8.71 |

**Every reading moves by under 6 % under every choice**, including dropping any single backdrop,
dropping the fine checkerboards entirely, reading only the checkerboards, moving the band twice, and
tiling the backdrop outside the canvas instead of clamping it. On the same variants the free
profile's second moment moves from 11.8 to 28.4 on one surface. That contrast is the whole finding
of §3 seen from the reference's side.

---

## 5. What no kernel explains, and it is the largest thing here

Every family, INCLUDING the free forty-node profile, fits Apple's interior about twice as badly as
vitrea's:

| | reference | vitrea |
| --- | --- | --- |
| free profile, RMS over rows, in display codes | 1.79 – 2.01 | 0.83 – 1.17 |

Per row it is worse on the structured backdrops than that average suggests: on `rrect-md` at 1x the
reference leaves 2.08 codes on `checkerboard-32`, 2.27 on `checkerboard-16`, 1.82 on
`checkerboard-4` and **3.22 on `hc-text`**, where vitrea leaves 1.48, 1.25, 0.65 and 1.35 on the
same rows through the same reader. The alignment check of §1 rules out a displaced raster, the
nuisance polynomial absorbs anything that varies with depth alone, and forty free radial parameters
have already been given every chance to describe it.

**So Apple's interior carries structure that no radially symmetric convolution of the backdrop
produces, at roughly one display code RMS.** Candidates this spike cannot separate: a kernel that is
not radially symmetric; a transmission that is not affine in the backdrop's luma (a per-channel or
per-level tone response); a spatially varying kernel that varies with something other than depth;
or a component of the material that is not a convolution at all. It is the single largest unexplained
quantity this reader found and it bounds how much any width fitted on this bed can be trusted.

---

## 6. What could not be read

- **The shape of either kernel.** §3b: forty radial parameters are not identified by these eight
  backdrops at 8-bit depth. Only a one- or two-parameter width is.
- **The half-maximum width of anything.** §3b: it is set by the regulariser, not by the data, and
  the control shows it wrong by 19–38 % while the MTF over the same fits agrees to 2–5 %. Any
  acceptance stated on a half maximum — including this brief's — is not testable on this bed.
- **The 2x width to better than 5–10 %**, because the drawn tap there is a trilinear blend outside
  the family the reader passed its control in. A material that named `sizeHeavyTapSigma` at 2x
  rather than letting `scatterLod` blend two levels would be readable to 0.6 % like the 1x rows.
- **The ~1 display code of Apple's interior that is not a convolution** (§5).
- **`rrect-ml`**, which has no `hc-text` row, and every tinted or pressed variant: out of scope.
- **The holdout**, untouched. **The user's eye**, not this child's.

---

## 7. What this leaves the wave

Stated as measurements, not as recommendations; the rulings are the parent's.

1. **`sizeHeavyTapSigma` = 13.418 is about 50 % wider than the reference at dpr 1** (8.6–9.2). W26
   Decision Log 3 (c) named it on continuity and byte-identity, explicitly not on a fit, and this is
   the first reading of that constant against a target with a control behind it.
2. **The 1x lever now has a target**, and it is *narrower* than what the material draws — the
   direction `checkerboard-64` gave in G1 §7.4 and §7.5, not the impulse tile's.
3. **The share needs no lift.** Reference 0.42–0.99 against vitrea's 0.50–0.92, every difference
   under 0.07. W25's and W26's declines of `sizeScatterHeavyShareThick1x` are confirmed by
   measurement rather than by cost.
4. **The 2x span grading is the reference's largest single disagreement** with vitrea at 2x
   (8.97 read against 12.24 drawn on `rrect-lg`), and it comes from `sizeScatterGainFar2x` rather
   than from the heavy tap.
5. **The claims that rest on the impulse tile's 1x two-Gaussian fit should be read beside this.**
   §5.113 §2's 19.52 and §5.120 §3a's sharp component of 2.74–2.79 are single-backdrop projections;
   the eight-backdrop reading of the same surfaces is 9.11 and 1.35–1.50. Neither is rewritten here
   and both are recorded.
6. **The next instrument is not a wider probe fixture.** It is the residual of §5: until something
   explains the display code of Apple's interior that no convolution produces, every width fitted on
   this bed carries it as an unmodelled bias, and a better fixture would not remove it.
