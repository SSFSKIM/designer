# W17 G0 — the renderer's excess, measured and derived (spike findings)

The charter (`docs/doperpowers/specs/2026-09-04-w17-css-interior-level.md`) opens this wave on a
reading of W16: that the 0.023–0.058 between the CSS tier's exact conversion and the GPU tier's
rendered interior is "the light of terms the CSS tier does not draw" — the lens, the rim's ambient
term, the highlight and the outer shadow's lift — and that deriving those four from the profile and
adding them to the tier's composite closes the level.

**The four terms are 0.0026 to 0.0106 on the light-standard cells at both scales, not 0.023 to
0.058.** They are attributable, superposable and derivable, and this document reports all three to
the charter's tolerances. But they are an order of magnitude too small to be the gap the wave was
chartered to close, and the rest of that gap is not in the renderer at all: it is between the CSS
tier's composite and the renderer's, in two places this spike names with numbers. Section 7 carries
the four `[parent-impact]` items that follow.

Every reading below is a GPU-tier or CSS-tier capture taken on this machine's `apple / metal-3`
adapter through Playwright's full Chromium binary (151.0.7922.34) at the fixture's pixel size, into
scratch matrices and scratch capture roots under `/Users/new/.claude/jobs/5c70e47f/tmp/w17/g0/`.
Nothing canonical was written. The scratch profile documents are `make-profiles.mjs`'s output and
are reproduced under `profiles/` beside this file.

## 0. The instrument, and its two validations

**The declines.** Six profile documents per colour scheme: the committed one, four with a single
term declined, and one with all four. Each is the committed document with the declined fields
written into its `patch`, so a declined render differs from the default render in those fields and
in nothing else — the isolation proof's construction
(`packages/renderer-webgpu/e2e/golden/isolation.spec.ts`), applied through `--material-profile`,
which is the same `withMaterialOverrides` seam. `capture-web.ts` hashes the file, so each
configuration lands under its own cell key and no two rows can be confused. `make-profiles.mjs`
states which field stands each term down and why.

The four terms and their fields: the lens (`lensRefractionGain` and `lensAmountMax` at 0, the factor
on the displacement's magnitude and the cap on the amount law it is built from); the rim's ambient
term (`optics.*.rimAlpha`, the shader's `ou.rim.y`); the highlight (`optics.*.specularGain`, the lit
half of the same added band — the highlight *pass*, the travelling sweep and the press glow, is a
separate plane and draws nothing on a bed cell at rest); and the outer shadow's lift
(`outerShadow.liftAmplitude`, which the shader adds as `liftEncoded * (1 - coverage)`).

**Validation one — the instrument reproduces the bed.** Twenty-four runs, all exit 0
(`parts/attribution-runs.txt` is the log's transcript). The default configuration's 72 GPU captures
across the four standard profiles are **byte-identical to the canonical `web-captures/`**, and every
numeric metric of all 72 cells matches `results/matrix.json` **to 0.000000** — not one leaf differs.
Four cells carry no material axis (`dark-solid__capsule-button__rest` on each profile: the reference
is very nearly invisible over its own tone, which `measure.ts` names as a real outcome), so the
attribution is over 68 cells.

**Validation two — the reader recovers a known offset (contract X4).** `x4-recovery.ts` calls
`measureCell` — the same function `cli/compare.ts` calls, with the same declared component region,
the same native-silhouette mask and the same `interiorLevel` — on the capture as written, and then
reads a copy with a +0.03 linear-light offset lerped into it through the same masked reader:

| profile | cell | interior mean as captured | recovery | against nominal +0.030 | against the offset actually on disk | mask pixels clamped at white |
| --- | --- | --- | --- | --- | --- | --- |
| 1x light | `checkerboard__rrect-md__rest` | 0.69462400 | +0.030713 | +0.000713 | 1.6e−14 | 61 / 15 024 |
| 1x light | `checkerboard__capsule-button__rest` | 0.67829533 | +0.030430 | +0.000430 | 1.9e−14 | 38 / 4 872 |
| 1x light | `checkerboard__rrect-ml__rest` | 0.69471552 | +0.030485 | +0.000485 | 3.7e−14 | 83 / 28 048 |
| 2x light | `checkerboard__rrect-md__rest` | 0.70147419 | +0.030630 | +0.000630 | 1.2e−15 | 305 / 60 058 |
| 2x light | `checkerboard__capsule-button__rest` | 0.68467402 | +0.030608 | +0.000608 | 3.6e−14 | 209 / 19 462 |
| 2x light | `checkerboard__rrect-ml__rest` | 0.70129712 | +0.030384 | +0.000384 | 1.8e−13 | 340 / 112 175 |

The recovery is inside 0.001 of the nominal offset on every reading, and inside 2e−13 of the offset
the doctored file actually carries — the whole of the +0.0004…+0.0007 is the eight-bit round trip's
own upward bias, not the reader's. `measureCell`'s reading of the undoctored capture equals the
direct `interiorLevel` reading to 0.0e+00 and equals the number already in the run's matrix
exactly. One thing the script found on the way and records rather than works around: the SHAPE axis
refuses a doctored capture — raising the whole image moves every web pixel away from the background,
the luminance-delta extractor returns the whole declared region, and `cornerCurvature` throws on a
contour with no curvature. That is the shape axis being right about a file that is not a capture.

**The declines change pixels.** Against the default capture of `checkerboard__rrect-md__rest` at 1x
light: `no-lens` differs on 7 313 pixels with a maximum of 37 code values, `no-rim` on 565 with 14,
`no-highlight` on 195 with 32, `no-lift` on 16 509 with 8 (all of them outside the silhouette), and
`all-declined` on 23 756 with 59. On `photo__rrect-md__rest` the same four are 7 665 / 599 / 208 /
15 182. The lens moves a large band by a large amount and moves the interior MEAN by nothing; that
is a finding of §1, not a failure of the decline.

## 1. The attribution (charter G0 (a))

`attribution.py` over the six scratch matrices; the full 68-cell table is `parts/attribution.txt`
and `parts/attribution.json`. Interior mean, whole silhouette, linear luminance. "whole" is
default minus the all-declined render; each term is default minus that term's decline.

The three W16 probe cells at both scales:

| dpr | cell | default | all declined | whole | lens | rim | highlight | lift | sum | sum − whole |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1x | `checkerboard__rrect-md__rest` | 0.6946 | 0.6911 | +0.0036 | −0.0002 | +0.0022 | +0.0013 | +0.0001 | +0.0034 | −0.00017 |
| 1x | `checkerboard__capsule-button__rest` | 0.6783 | 0.6731 | +0.0052 | −0.0002 | +0.0028 | +0.0024 | +0.0000 | +0.0050 | −0.00018 |
| 1x | `checkerboard__rrect-ml__rest` | 0.6947 | 0.6921 | +0.0026 | −0.0002 | +0.0016 | +0.0010 | +0.0001 | +0.0025 | −0.00008 |
| 2x | `checkerboard__rrect-md__rest` | 0.7015 | 0.6979 | +0.0036 | −0.0002 | +0.0022 | +0.0012 | +0.0000 | +0.0032 | −0.00033 |
| 2x | `checkerboard__capsule-button__rest` | 0.6847 | 0.6793 | +0.0054 | +0.0001 | +0.0027 | +0.0023 | +0.0000 | +0.0052 | −0.00018 |
| 2x | `checkerboard__rrect-ml__rest` | 0.7013 | 0.6985 | +0.0028 | −0.0001 | +0.0017 | +0.0010 | +0.0001 | +0.0026 | −0.00022 |

**The four terms superpose.** The largest disagreement between the sum of the four single-term
differences and the all-declined difference is **0.000817**, on
`dark-solid__rrect-md__rest` in the 1x dark profile — the cell where the whole excess is largest
(+0.1344). **No cell exceeds 0.005**, and 64 of the 68 are inside 0.0005. The charter's clause is met
with six times the margin it asks for.

**The four terms are small.** On every light-standard checkerboard, `photo` and `hc-text` cell at
both scales the whole excess is **+0.0026 to +0.0106**, largest on the thin spans
(`checkerboard__rrect-sm__rest` +0.0100 at 1x and +0.0106 at 2x) and smallest on the large ones
(`rrect-ml` +0.0026 / +0.0028). The band-fraction signature the charter predicted is there — the
32 px span's excess is 3.8× the 128 px span's — and it is a signature of a term that is four times
too small to be the 0.023–0.058 the charter attributes to it.

**The lift reads zero inside the silhouette**, as the shader's `(1 - coverage)` factor says it must:
+0.0000 to +0.0001 on every one of the 68 cells, the tenth of a thousandth being the anti-aliased
contour ring where the coverage is not 1.

**The lens carries no mean on a checkerboard and a small one on a photo.** −0.0002 on every light
checkerboard span, and +0.0021 to +0.0036 on `photo__rrect-md` and `photo__rrect-ml`, negative
(−0.0021 / −0.0024) on `photo__rrect-sm`. This is the charter's advisory reading confirmed exactly:
a displacement moves the mean of a homogeneous backdrop by nothing and moves a photo's by the
backdrop's own gradient at the contour, sign included.

**Where the excess IS large, it is the rim and the highlight over an invisible body.**
`dark-solid__rrect-md__rest` in the dark profile reads +0.1344 at 1x and +0.1607 at 2x, of which the
rim is +0.0801 / +0.0957 and the highlight +0.0534 / +0.0655. The material there is a near-black
body at 0.0761 and the band is the only light in it. Nothing about that cell is anomalous; it is the
same two terms over a hundredth of the denominator.

## 2. The analytic check (charter G0 (b))

`analytic.ts` computes the composite from the profile through `optics.ts`'s own functions —
`sourceOptics`, `sizeThickness`, `backdropToneAdaptation`, `toneRespondedSourceOptics`,
`adaptedSourceOptics`, `sizeOcclusionAlphaAt` — in the order `root.ts` runs them, and lerps in
linear light: `mean = (1 − α)·b + α·L(tint)`. The full table is `parts/analytic.txt`.

**How the backdrop level is sampled, and which one is which.** There are two quantities and they are
not interchangeable.

- **The group's sampled tone** drives the W9 response solve and the collapse. It is one number per
  backdrop SOURCE over the whole texture, in the two spaces `BackdropToneSample` carries:
  `luminance`, the encoded-space mean decoded once, which is the response curve's input; and
  `linearLuminance`, the linear mean, which the collapse converges onto. This script recomputes both
  from the fixture background the scene declares, exactly as `sampleBackdropTone` accumulates them.
  One difference is stated rather than hidden: the browser draws the texture down to
  `SAMPLE_EXTENT` = 512 on its longest edge first and this reads every pixel; a box average of box
  averages is the same average up to rounding, and the 1x backgrounds are 320 × 200 and are not
  downsampled at all.
- **The level the lerp runs against** is what is behind the SURFACE, which is neither of those. The
  harness measures it per cell already, as `material.interiorMeanBackdrop` — `interiorLevel` of the
  background image over the same native silhouette the web reading uses — and **that is what this
  script lerps against.** The group-sampled linear mean is reported beside it, and the two part
  company where the surface does not sit over an average patch of its own backdrop
  (`photo__rrect-sm__rest`: 0.1682 under the surface against 0.2141 for the source;
  `photo__toolbar-group__rest`: 0.2536 against 0.2141).

**The model as `optics.ts` states it is not the shader's, and the error has a name.** The residual
(model minus all-declined render) runs to **+0.0268** on `dark-solid__rrect-md__rest` in the light
profile, **+0.0209** on `photo__rrect-md__rest` and **+0.0147** on `checkerboard__rrect-md__rest` at
1x — 15 of the 44 untinted cells over 0.005, all in the same direction. The cause is an **ordering
difference between the tier's mirror and the shader**:

> `root.ts` applies the size law's occlusion LAST, on the alpha `adaptedSourceOptics` returned;
> the shader applies it FIRST — `sizedAlpha = tint.w + size.y * sizeK * (1 - tint.w)` is computed
> before the W9 response solve, and the solve then shifts the neutral so that the composite AT THAT
> ALPHA lands on the response `R`. The solve's whole purpose is to put the mean on `R`; a solve run
> at α = 0.46 followed by a raise to α = 0.487 lands the mean above `R` by the raise times the
> tint's excess over the backdrop.

Recomputing the same chain in the shader's order drops the residual to +0.0058 or less on 39 of the
44 untinted cells, and adding the **inner shadow** — which is in the all-declined render and in
neither model, since it is not one of the four terms — closes it further. The inner shadow's area
mean comes out of the same co-area integral the rim's does: `shadowKeep = 1 − P̄·shadowDepth·
shadowAlpha` with `P̄ = (1/A)∫₀^D (1 − u/D)²·P(u) du`, `D = min(thickness·(1 + (lensSizeGainMax −
1)·sizeK), span/2)` and the authored thickness `DEFAULT_HOST_SHAPE.thickness` = 8 CSS px, which the
calibration pages never override.

| model | cells within 0.005 (of 44 untinted) | worst residual |
| --- | --- | --- |
| `root.ts`'s order, no inner shadow | 29 | +0.0268 `dark-solid__rrect-md__rest` 1x light |
| the shader's order, no inner shadow | 39 | −0.0399 `dark-solid__rrect-md__rest` 2x dark |
| the shader's order plus the inner shadow | **37** | **−0.0400** `dark-solid__rrect-md__rest` 2x dark |

On the three probe cells the shader-order-plus-inner-shadow model reads +0.0008 / −0.0007 / +0.0004
at 1x and −0.0060 / −0.0069 / −0.0059 at 2x. Two residual families remain and both are named rather
than absorbed:

1. **The dark scheme's `dark-solid__rrect-md__rest`**, −0.0274 at 1x and −0.0400 at 2x: the render
   is brighter than the model. This is the same cell the renderer's own dark-ground dot lives on
   (W15 Deferred; the GPU tier is +0.17 over native there), so the model failing on it is the model
   declining to reproduce a gap that is the renderer's and is already recorded.
2. **A scale-signed term on the 2x light cells**, −0.0039 to −0.0080 on every 2x checkerboard and
   the 2x toolbar, against ±0.0021 on their 1x twins: at the second scale the shader's body is
   brighter than the composite the profile states. That belongs with §5.55 §3's scale-dependent
   level, is the renderer's, and is not this tier's to import.

The author-tinted cells are excluded (32 of 68 skipped in §3's table for the same reason): this
model does not carry the seed's opaque layer (W10), and a 0.4 residual against a model that was
never asked to include it is noise in a table rather than information.

## 3. The closed form (charter G0 (c))

`closed-form.ts` derives each term from `withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch)` —
the resolved material the shader itself was handed — and the surface's own box and radius, and
compares it with §1's measured differences on the reader's own mask, rebuilt through the harness's
extractor. Full table: `parts/closed-form.txt`. Forty cells; 32 skipped, 28 of them author-tinted
and four for the surfaces the band is a union over (`toolbar-group`, `glass-over-glass`), where the
contour is not one rounded rectangle.

- **The rim's ambient term** is `rw(d)·rimAlpha·present` added in linear light, with
  `rw(d) = clamp(1 − |d|/rimWidth, 0, 1)²`. Its area mean is the co-area integral over the inward
  offsets, which for a rounded rectangle is exact: the offset by `u` keeps its straight runs and
  shrinks only its corner arcs, so `P(u) = 2(W − 2r) + 2(H − 2r) + 2π(r − u)`.
- **The highlight** is the same band lit: `rw(d)·clamp(n̂ · lightDirection, 0, 1)^specularPower ·
  specularGain·present`, whose band weight is the same and whose contour weight is the integral of
  the specular factor around the contour.
- **The lift** is drawn outside the coverage and is predicted **exactly zero** inside.
- **The lens** is a displacement, not light: it re-samples the blurred backdrop and adds nothing of
  its own, so on a backdrop that is statistically homogeneous over the band its mean shift is zero
  to first order. It is predicted **zero**, and §1's measured −0.0024…+0.0036 is carried as the
  derivation's own residual rather than fitted to. A closed form for the second-order term needs the
  renderer's two-component body, which is W16's measurement and not this profile's number.

Both bands are evaluated on the **device pixel grid** rather than as continuous integrals, because a
1.5 CSS px band is one and a half samples wide at dpr 1 and the sum and the integral differ by about
a tenth of the term; and each is reported twice, once as the area mean in linear light and once as
the same light added to the all-declined capture, encoded, rounded to eight bits and re-read, which
is what §1 can be compared with. On the probe cells the two forms differ by at most 0.0005, so the
quantisation is not what the residual is made of.

The three probe cells at both scales (the quantisation-modelled form):

| dpr | cell | rim predicted | rim measured | highlight predicted | highlight measured | whole predicted | whole measured | residual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1x | `checkerboard__rrect-md__rest` | +0.00270 | +0.00223 | +0.00160 | +0.00133 | +0.00430 | +0.00356 | +0.00075 |
| 1x | `checkerboard__capsule-button__rest` | +0.00522 | +0.00282 | +0.00360 | +0.00239 | +0.00882 | +0.00521 | +0.00361 |
| 1x | `checkerboard__rrect-ml__rest` | +0.00194 | +0.00160 | +0.00121 | +0.00102 | +0.00315 | +0.00262 | +0.00053 |
| 2x | `checkerboard__rrect-md__rest` | +0.00280 | +0.00223 | +0.00157 | +0.00123 | +0.00436 | +0.00358 | +0.00078 |
| 2x | `checkerboard__capsule-button__rest` | +0.00525 | +0.00274 | +0.00332 | +0.00230 | +0.00857 | +0.00538 | +0.00318 |
| 2x | `checkerboard__rrect-ml__rest` | +0.00208 | +0.00171 | +0.00121 | +0.00101 | +0.00329 | +0.00281 | +0.00047 |

**The largest residual is +0.00605, on `dark-solid__rrect-md__rest` in the 1x dark profile** —
predicted +0.1404 against a measured +0.1344, a 4.5 % relative error on the largest excess in the
bed. **No cell exceeds 0.01**, so the charter's clause for (c) is met on every one of the 40 cells
the form covers, with the largest miss at three fifths of the allowance.

The residual is systematically positive and largest on the capsules (+0.0027 to +0.0036 on every
`capsule-button` cell, against +0.0005 to +0.0008 on the `rrect-md` and `rrect-ml` cells and −0.0032
on `photo__rrect-md__rest` at 2x, where the unmodelled lens is +0.0036). A capsule's radius is its
own half-height, so its band is entirely corner arc and its predicted term is the most sensitive to
a pixel of disagreement between the geometric contour and the native mask the measurement uses; that
is the shape of the miss and it is recorded rather than tuned away.

## 4. The carrier (charter G0 (d))

The two-equation solve, carried by an `feComponentTransfer` inside the tier's existing linear-light
reference filter. The patch is `carrier-patch/w17-carrier.ts` and `carrier-patch/call-sites.md` —
built, captured, and reverted before anything was committed.

**Where the stage goes.** On the SHARP filter alone. The tier's body is two layers: L1 filters the
page at the sharp width and L2 filters L1's own output at the heavy step under the ramp mask. A
Gaussian is linear and normalised, so `blur(m·b + c) = m·blur(b) + c` — an affine applied at L1
passes through L2 unchanged and reaches the composite exactly once. Applying it at both would apply
it twice; applying it at L2 alone would leave the sharp share untransformed where the mask is open.

**The solve.** With `E` the sRGB encode, the renderer's composite `M(b) = (1 − α)b + αT`, the target
`G(b) = E(M(b) + X)` and the tier's output `F(b) = E(mb + c)(1 − α′) + Ec·α′`, requiring
`F(b₀) = G(b₀)` and `F′(b₀) = G′(b₀)` gives `m` and `c` in closed form with no third unknown — the
overlay stays exactly what `cssTintAlpha` and `cssTintColor` write. `α` and `T` are §2's shader-order
values, `X` is §3's derived excess, and `b₀` is the group's own sampled linear mean.

The coefficients (`solve-record.ts`, `parts/solve.json`):

| cell | b₀ | α | T | X | overlay α′ | slope | intercept |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__rrect-md__rest` | 0.5000 | 0.4870 | 0.8991 | 0.00462 | 0.6833 | 1.1123 | **−0.1892** |
| `checkerboard__capsule-button__rest` | 0.5000 | 0.4625 | 0.8771 | 0.00930 | 0.6635 | 1.1316 | **−0.1872** |
| `checkerboard__rrect-ml__rest` | 0.5000 | 0.4870 | 0.8991 | 0.00339 | 0.6833 | 1.1087 | **−0.1901** |

The six probe readings, GPU tier from the same run's own captures (which are byte-identical to the
canonical bed on all 52, so the patch moved no GPU pixel — contract X3 holds under it):

| dpr | cell | native | GPU rendered | CSS bed (E) | CSS carrier | carrier − GPU | bed − GPU | spread native | spread carrier | spread bed | ssimMean carrier | ssimMean bed | level ratio carrier | level ratio bed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1x | `checkerboard__rrect-md__rest` | 0.6829 | 0.6946 | 0.7419 | 0.6797 | **−0.0149** | +0.0473 | 0.1131 | 0.1137 | 0.1064 | 0.9086 | 0.9028 | 1.0220 | 0.9363 |
| 1x | `checkerboard__capsule-button__rest` | 0.6207 | 0.6783 | 0.7051 | 0.6555 | **−0.0228** | +0.0269 | 0.1424 | 0.1564 | 0.1416 | 0.9716 | 0.9672 | 1.0348 | 0.9619 |
| 1x | `checkerboard__rrect-ml__rest` | 0.6936 | 0.6947 | 0.7447 | 0.6826 | **−0.0121** | +0.0500 | 0.0865 | 0.0985 | 0.0927 | 0.8676 | 0.8593 | 1.0177 | 0.9328 |
| 2x | `checkerboard__rrect-md__rest` | 0.6832 | 0.7015 | 0.7593 | 0.7108 | **+0.0093** | +0.0578 | 0.1272 | 0.1086 | 0.1151 | 0.9165 | 0.9149 | 0.9869 | 0.9238 |
| 2x | `checkerboard__capsule-button__rest` | 0.6226 | 0.6847 | 0.7157 | 0.6810 | **−0.0036** | +0.0310 | 0.1552 | 0.1452 | 0.1455 | 0.9758 | 0.9738 | 1.0053 | 0.9566 |
| 2x | `checkerboard__rrect-ml__rest` | 0.6929 | 0.7013 | 0.7651 | 0.7162 | **+0.0149** | +0.0638 | 0.1018 | 0.0815 | 0.0862 | 0.8788 | 0.8783 | 0.9793 | 0.9166 |

**The carrier does most of the work and misses the clause.** The gap to the GPU tier goes from
+0.027…+0.064 to −0.023…+0.015 — closed by a factor of 2.5 to 4 on every reading — and the
cross-tier level ratio goes from 0.917–0.962 to 0.979–1.035, inside the charter's 0.97–1.03 on four
of six. **Two of the six are within 0.01 and four are not**, so the charter's clause for (d) is
**not met**.

**The structure does not pay for it.** `ssimMean` is UP on all six against the landed bed
(+0.0058 / +0.0044 / +0.0083 at 1x, +0.0016 / +0.0020 / +0.0005 at 2x). The interior spread lands
within 0.0006 of native on `rrect-md` at 1x (0.1137 against 0.1131) and moves AWAY from native
elsewhere: +0.0140 over on the 1x capsule, +0.0120 over on `rrect-ml` at 1x, and 0.0186 / 0.0203
UNDER at 2x on `rrect-md` and `rrect-ml`, which is outside the ±0.015 the parent-level acceptance
holds at 2x.

**Why it misses, measured.** The solve's intercept is **negative** on every probe cell, and Filter
Effects 1 clamps a primitive's result to the allowed range: a `type="linear"` transfer cannot emit a
negative value however negative its intercept is. The zero crossing sits at a backdrop level of
about 0.17 in linear light, and on the checkerboard the sharp layer's filtered backdrop is below
that on **29.0 % of its pixels at dpr 1 and 37.5–37.9 % at dpr 2**
(`clamp-fraction.py`, `parts/clamp-fraction.txt`; the backdrop blurred at W16's measured effective
sharp width, 1.7 device px at dpr 1). Over that third of the interior the tier's body is brighter
than the conversion asked for, and the fraction rising with the scale is the same direction the
residual moves in (−0.012…−0.023 at 1x, −0.004…+0.015 at 2x). Beside it and in the other direction,
the encode is concave, so matching the target at `b₀` in value and slope leaves the tier's MEAN
below the target by the curvature term times the variance of `b`, which on a checkerboard is large
(the filtered backdrop's standard deviation is 0.387 at 1x and 0.416 at 2x). **The two equations are
a point condition and the cell is not a point**; that is the shape of what is left.

One run of the same configuration is recorded beside the reported one
(`parts/carrier-overlay-from-nodeoptics.json`): it conditioned the solve on `nodeOptics` rather than
on the overlay the tier had actually declared, and read −0.0077 / −0.0220 / −0.0046 at 1x and
+0.0145 / −0.0035 / +0.0206 at 2x. The difference between the two is a reading and not a correction,
and it changes no verdict.

## 5. The cost (charter G0 (e))

W16 G0's harness, its pages copied here with one form added: `two-ref-mask-ct` is `two-ref-mask` —
the landed shape, two linear-light reference filters and the raster mask — with an
`feComponentTransfer` of `type="linear"` appended to each filter's chain. Both forms were measured
in one session on the same browser (`parts/g0-cost-fecomponenttransfer.json`,
`parts/cost-run.txt`), vsync ON, so the number that carries information is the surface count at
which the display's cadence breaks. Median `requestAnimationFrame` interval, ms:

| surfaces (160 × 96 CSS px) | two + mask @1x | two + mask + transfer @1x | two + mask @2x | two + mask + transfer @2x |
| --- | --- | --- | --- | --- |
| 20 | 10.4 | 10.6 | 10.6 | 14.0 |
| 24 | 10.6 | 11.2 | 10.2 | 10.2 |
| 28 | 11.5 | 11.0 | 15.6 | 11.4 |
| 32 | 12.6 | 13.6 | 13.6 | 13.5 |
| 36 | 20.2 | 16.6 | 16.6 | 16.6 |
| 40 | 18.9 | 20.1 | 19.9 | 19.8 |
| 48 | 21.3 | 26.0 | 22.7 | 23.8 |
| 80 | 29.2 | 28.1 | 29.3 | 27.2 |
| 160 | 26.8 | 27.7 | 28.2 | 28.4 |
| 320 | 28.3 | 27.4 | 26.1 | 28.1 |

**The knee does not move.** Both forms hold the cadence to 32 surfaces and both leave it by 36, at
both scales — the charter's clause exactly. The disagreements between the two columns are in both
directions and are the same jitter W16 G0 recorded (28 surfaces at dpr 2 reads 15.6 for the form
WITHOUT the transfer and 11.4 with it; 48 at dpr 1 reads 21.3 without and 26.0 with). A
`type="linear"` transfer is one multiply-add per channel per pixel and it costs what that implies,
which is nothing this harness can resolve. The coefficients on the cost page are illustrative and
are not §4's solve; the page says so, and a linear transfer's cost does not depend on them.

## 6. Recommended answers to Decision Log 1 (charter G0 (g))

**q0 — the target. Neither (a) as chartered nor (b); the option the measurement opens is (a) with
the target restated.** The charter's (a) is "the renderer's rendered interior, term by term", and
its arithmetic is that the tier's exact composite plus the four terms reaches the renderer's render.
§1 measures those four terms at **0.0026–0.0106** where that arithmetic needs 0.023–0.058, so adding
them to an exact composite leaves 0.02–0.05 of the gap standing. What §2 and §4 show is that the
remaining distance is not the renderer's light at all: **+0.0147 to +0.0268 of it is the tier's own
mirror disagreeing with the shader about when the size law's occlusion enters the alpha** (§2), and
the rest is the tier's composite against a distribution of backdrop levels rather than a point (§4).
So the recommendation is to keep the target — the renderer's rendered interior, which is what K5
requires and what §4 confirms is reachable to −0.023…+0.015 with one primitive — and to replace the
charter's account of what stands between the tier and it. The four terms stay in the derivation
because §3 derives them within 0.006 and they are 0.010 of the level on a thin span, which is the
clause's own tolerance; they are simply not the mechanism. **q0(b), a fit against native, stays
rejected** and §4 strengthens the reason: the carrier's `ssimMean` is up on all six probe readings
while its level moves onto the GPU tier's, so coherence and structure are not in tension here and
there is nothing to buy by fitting elsewhere.

**q1 — the carrier and the engines. (a), with one correction that is not optional.**
`feComponentTransfer` inside the linear-light reference filter is the right carrier — it is exact
arithmetic, it needs no new element, it costs nothing measurable (§5), and it moves the level by
0.05–0.08 in the right direction (§4). But **`type="linear"` with a negative intercept is not
representable**: the primitive clamps at zero and 29–38 % of the checkerboard's filtered backdrop
falls in the clamped region. G1 must either reformulate so the intercept is non-negative, or use a
transfer type whose curve is not clipped there (`type="table"` over the same two constraints, or
`type="gamma"` with `amplitude`/`exponent`/`offset`). The plain-`blur()` engines keep the one-alpha
conversion and E's level behind the same conformance row, as the charter says.

**q2 — the reduced-transparency fold in scope. (a), yes, and G0 did not measure it.** The fold was
not captured here (§4 is the two light-standard profiles). Nothing found argues against including
it, and §5.73 §3's two lost predicate cells are the fold's own level gap, so the mechanism is the
same one. G1 owns the measurement.

**q3 — the trade if the level costs structure. (a) stands, and on this evidence it may not be
called.** `ssimMean` rose on all six probe readings with the carrier in (+0.0005 to +0.0083), so the
level did not cost structure on the cells the trade was anticipated for. What DID move is the
interior spread at 2x, 0.019–0.020 under native on `rrect-md` and `rrect-ml` against the ±0.015 the
acceptance holds — that is a spread question rather than a structure one, and it is S3's, not q3's.

**q4 — the coherence claim's wording. (a), re-word at G2, and the bound G0 can offer is not "the
derivative's second order".** The two equations match value and slope at `b₀` exactly; what they do
not carry is the curvature over the cell's distribution of `b`, and on this bed that distribution's
standard deviation is 0.387–0.416, which is not a small parameter. The honest wording is a measured
one: with the conversion solved at the group's sampled level the cross-tier level ratio reads
**0.979–1.035** on the probe cells against the bed's 0.917–0.962, and the residual is bounded by the
backdrop's own variance rather than by a derivative order. G1 should re-measure the bound after the
clamp is dealt with, because §4's number carries the clipping in it.

## 7. What contradicts the charter — `[parent-impact]`

1. **`[parent-impact]` The excess is not the four terms, and the charter's binding target rests on
   the claim that it is.** Design's second binding rule and the Grounding Baseline's reading (iii)
   both hold that the renderer's 0.023–0.058 over its analytic composite is the light of the lens,
   the rim and the highlight. Declining all four moves the GPU tier's interior by **0.0026 to 0.0106**
   on the light-standard cells (§1), superposing within 0.0008 and deriving within 0.006 (§3), so
   the attribution is sound and the quantity is four to ten times too small. The parent's stop —
   "a finding that the excess is not attributable to the four terms within 0.01" — is not literally
   triggered, because the terms ARE attributable to well inside 0.01; what fails is the premise that
   they are the gap. **This is the finding that re-opens Design before G1.**
2. **`[parent-impact]` A cross-tier ordering difference the wave did not know about, worth +0.015 to
   +0.027 of the level.** `root.ts` applies `sizeOcclusionAlphaAt` after the W9 response solve and
   the shader applies its `sizedAlpha` before it (§2). The solve exists to land the composite's mean
   on the response, and raising the alpha afterwards lands it above. This is a two-tiers-one-profile
   defect in its own right — it is present on the tier today, independent of any conversion — and it
   is a larger single contribution to the CSS tier's level than everything §1 measured put together.
   It may deserve its own G-child, and it may move rows the wave promised not to move.
3. **`[parent-impact]` `feComponentTransfer type="linear"` cannot carry the solve as stated.** The
   intercept comes out at −0.187 to −0.190 and the primitive's output is clamped to [0, 1], so 29 %
   of the filtered backdrop at dpr 1 and 38 % at dpr 2 is clipped (§4). Design's binding "the
   carrier lives inside the existing form" survives — the stage is still one primitive in the filter
   the tier already runs — but the charter's advisory "the conversion" needs a formulation whose
   intercept is representable, and the choice between reformulating and changing the transfer type
   is G1's with the parent's blessing.
4. **`[parent-impact]` The two equations are a point condition and the acceptance is a mean.**
   Matching value and slope at `b₀` does not match the mean over a cell whose filtered backdrop has
   a standard deviation of 0.39–0.42 in linear light. Even with the clipping removed, the charter's
   advisory solve is second-order-accurate where the acceptance is stated to 0.01 on a strongly
   bimodal backdrop. G1 will need either a third condition (the curvature, or the solve taken
   against the cell's own distribution rather than at a point) or a restated tolerance.

Two more, smaller, recorded here rather than as impacts. The 2x light cells' body is 0.004–0.008
brighter than the profile's composite even in the shader's own order (§2), which belongs with §5.55
§3's scale-dependent level and is the renderer's. And the interior spread at 2x under the carrier
lands 0.019–0.020 under native on `rrect-md` and `rrect-ml` (§4), outside the parent-level
acceptance's ±0.015 — measured on a configuration that is not G1's and reported so that G1 measures
it deliberately rather than discovering it.

## 8. What is in this directory

| file | what it is |
| --- | --- |
| `make-profiles.mjs` | the six scratch profile documents per colour scheme, and why each field stands its term down |
| `profiles/` | the ten documents it wrote, exactly as the runs consumed them |
| `run-attribution.sh` | the 24 GPU runs of §1, one at a time, all to scratch |
| `attribution.py`, `parts/attribution.{json,txt}` | §1's table over 68 cells |
| `x4-recovery.ts`, `parts/x4-recovery.json` | contract X4's recovery, through `measureCell` |
| `analytic.ts`, `analytic-table.py`, `parts/analytic.{json,txt}` | §2's three models against the all-declined render |
| `closed-form.ts`, `closed-form-table.py`, `parts/closed-form.{json,txt}` | §3's derivation and its residual |
| `carrier-patch/` | the reverted `platform-web` patch §4 was captured under, and its two call sites |
| `run-carrier.sh`, `carrier-table.py`, `parts/carrier*.json`, `parts/carrier.txt` | §4's captures and table |
| `solve-record.ts`, `parts/solve.json` | §4's coefficients |
| `clamp-fraction.py`, `parts/clamp-fraction.txt` | how much of the filtered backdrop the transfer clips |
| `cost.mjs`, `pages/cost.html`, `cost-cases.json`, `parts/g0-cost-fecomponenttransfer.json`, `parts/cost-run.txt` | §5's cost measurement |
