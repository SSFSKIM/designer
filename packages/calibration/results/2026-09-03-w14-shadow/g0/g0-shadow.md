# W14 G0 — the reference's outer shadow, measured as a composite

The readings. `g0-instrument.md` is the instrument and its validation on vitrea's own shadow (X4),
and every table below carries that recovery beside it. Nothing here was captured and nothing under
`packages/**/src`, `profiles/` or `results/matrix.json` was touched.

**Two spaces, said once.** Every quantity is given in the space it was measured in. `enc` is encoded
Rec.709 luma — the domain both tiers composite in and the domain claims §5.60 §3's +0.039 was read
in; `lin` is linear luminance — the domain the charter binds and the shadow axis normalises in. The
same lift is +0.048 encoded and +0.0038 linear on `checkerboard__rrect-lg__rest`, because it sits on
a black square where the transfer function is steepest. See `g0-instrument.md` §2.

---

## 1. What the exterior is, in one sentence

Outside its contour the reference composites **two terms on one falloff**: a black term that removes
a fraction of the backdrop's light, and a lift that adds a blurred, darkened copy of the backdrop's
own light. The black term acts at every span and adapts to the backdrop; the lift appears only above
the thin/thick knee at span 64, is zero over a dark backdrop, and carries no fixed colour of its own.
vitrea renders the first term at one constant amplitude and does not render the second at all.

## 2. The lift by span, and the `VibrancyContribution` question

The checkerboard's two levels separate the composite with no regression at all: a multiply is inert
over black (claims §5.12), so the black squares outside the contour carry the lift and nothing else,
and the white squares carry both. `parts/span.json`, ring 0–6 CSS px **below** the surface, guarded.
The canonical bed and the W9 / W12 probe beds agree to the fourth decimal on every row.

| span | `Vc` = clamp((span−64)/96) | lift, enc | lift, lin | vitrea GPU | lift_enc / `Vc` | lift_lin / `Vc` |
| --- | --- | --- | --- | --- | --- | --- |
| 32 `rrect-sm` | 0.00 | 0.0000 | 0.0000 | 0.0000 | — | — |
| 44 `capsule-button` | 0.00 | 0.0000 | 0.0000 | 0.0000 | — | — |
| 96 `rrect-md` | 0.33 | 0.0290 | 0.0022 | 0.0000 | 0.0871 | 0.0067 |
| 128 `rrect-ml` | 0.67 | 0.0439 | 0.0034 | 0.0000 | 0.0659 | 0.0051 |
| 130 `glass-over-glass` | 0.69 | 0.0448 | 0.0035 | 0.0000 | 0.0652 | 0.0051 |
| 160 `rrect-lg` | 1.00 | 0.0479 | 0.0038 | 0.0000 | 0.0479 | 0.0038 |

At 2x, on the same rows: 0.0000 / 0.0000 / 0.0292 / 0.0445 / 0.0454 / 0.0487 encoded — **the lift is
a CSS-px quantity and is scale-free**, matching to 0.0008 at every span.

**Answers to the charter's question.** Spans at or below the knee do not lift at all: 0.0000 to four
decimals on both thin spans, on every checkerboard pitch, at both scales — the knee at 64 is exact,
and the lift is the thick regime's alone. Above the knee the lift is **not proportional** to
`VibrancyContribution`: the ratio falls from 0.087 at span 96 to 0.048 at span 160, a factor of 1.8
across the range where a proportional term would hold it constant. What the lift does instead is
rise and saturate — 0.029, 0.044, 0.048 at spans 96, 128, 160 — reaching 91% of its span-160 value
by span 128. `glass-over-glass` at an effective span of 130 lands on `rrect-ml`'s row (0.0448
against 0.0439), so the law reads off the shorter side of the base surface and not off the overlay.

By side, 1x, ring 0–6 encoded (2x within 0.0016 of every entry):

| cell | below | above | left | right | corner | above / below |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 0.0290 | 0.0125 | 0.0204 | 0.0200 | 0.0189 | 0.43 |
| `rrect-ml` | 0.0439 | 0.0180 | 0.0303 | 0.0306 | 0.0313 | 0.41 |
| `glass-over-glass` | 0.0448 | 0.0182 | 0.0285 | 0.0332 | 0.0331 | 0.41 |
| `rrect-lg` | 0.0479 | 0.0196 | 0.0327 | 0.0342 | 0.0349 | 0.41 |

One asymmetry, the same on every span: the lift below is 2.4× the lift above and the two flanks sit
between. That is exactly what a single silhouette displaced 8 CSS px downward produces — see §6 —
and it is why the lift needs no direction of its own.

Figure: `fig-lift-by-side.png` (c(d) per side, three spans, both scales, Apple against vitrea's flat
zero) and `fig-transmission-by-side.png` (a(d) on the white squares with the lift removed).

## 3. The lift's blur, from the probes' pitch axis

If the lift is a blurred copy of the backdrop, its level over a black square must follow the
**blurred** plate there: a σ-40 CSS px copy of a pitch-4 checker is flat at the plate's mean, of a
pitch-64 checker it follows the squares. `parts/blur.json`, `parts/blur-black-square.json`; ring 0–6
below, guarded, encoded luma × 255.

| cell | pitch 4 | pitch 8 | pitch 16 | pitch 32 | pitch 64 | blur-40 at the black centres, 4…32 → 64 |
| --- | --- | --- | --- | --- | --- | --- |
| 1x `rrect-md` | 7.40 | 7.40 | 7.40 | 7.40 | 7.25 | 191.0 → 187.7 |
| 1x `rrect-ml` | 11.20 | 11.20 | 11.20 | 11.20 | 10.78 | 191.0 → 185.4 |
| 1x `rrect-lg` | 12.22 | 12.22 | 12.22 | 12.23 | 11.21 | 191.0 → 182.5 |
| 2x `rrect-md` | 7.45 | 7.45 | 7.45 | 7.49 | 7.27 | 191.0 → 187.7 |
| 2x `rrect-ml` | 11.36 | 11.36 | 11.35 | 11.36 | 10.94 | 191.0 → 185.4 |
| 2x `rrect-lg` | 12.45 | 12.43 | 12.43 | 12.43 | 11.30 | 191.0 → 182.5 |

The lift is flat across pitches 4 to 32 and drops at pitch 64 — by 8.3% on `rrect-lg` where the
blurred plate itself drops 4.4%, by 3.8% on `ml` where it drops 2.9%, by 2.1% on `md` where it drops
1.7%. It tracks the blurred plate, which is what "a blurred copy of the backdrop" means and is what
an unweighted blur term on pitch 16 alone could never see (claims §5.60 §3's "no blurred copy
detectable" was read on pitch 16, where a σ-40 copy is a constant to 0.001; that reading stands and
this one does not contradict it).

Pooling the five pitches and regressing the lift on a blurred copy at each σ on a grid of 8…64 CSS
px, the residual has a real minimum on the largest span and is flat on the other two:

| cell | σ* | residual at σ* | at σ 8 | at σ 32 | at σ 48 | at σ 64 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1x `rrect-lg`, ring 0–6 | **40** | 2.899 | 3.252 | 3.078 | 2.965 | 3.133 | identified, 40 ± 8 |
| 2x `rrect-lg`, ring 0–6 | **40** | 3.099 | 3.492 | 3.299 | 3.171 | 3.348 | identified, 40 ± 8 |
| 1x `rrect-lg`, ring 6–12 | **40** | 3.053 | 3.353 | 3.209 | 3.086 | 3.200 | identified |
| 1x `rrect-ml`, ring 0–6 | 40 | 2.843 | 2.863 | 2.847 | 2.848 | 2.917 | not identifiable — flat to 0.7% |
| 1x `rrect-md`, ring 0–6 | 20–32 | 1.865 | 1.874 | 1.865 | 1.866 | 1.883 | not identifiable — flat to 0.5% |

(residuals in encoded luma × 255; figure `fig-blur-sigma.png`.)

**One σ of 40 CSS px covers what can be identified.** On `rrect-lg` it is a genuine minimum, 12%
below the flat-copy residual, at both scales and in two rings, and it lands exactly on the layer
tree's `inputShadowBlurRadius` = 40 (claims §5.50 §2) read as a Gaussian standard deviation rather
than as a doubled radius. On `rrect-ml` and `rrect-md` the lift is weaker and the exterior window
smaller, and σ is not identifiable at all: their curves are flat within 0.7%, and this reports that
rather than quoting their argmin. Nothing in the data prefers a different σ at a different span.

## 4. The lift's colour: the backdrop's own light, not a fixed gray

The charter's binding rule asks for this to be settled before a colour constant is allowed into a
profile. The per-channel affine fit on `photo` cannot settle it — vitrea's own capture, whose shadow
is a pure gray multiply, reads back per-channel intercepts of (0.0020, 0.0005, 0.0013) in linear RGB
on `photo__rrect-lg__rest`, so a per-channel `c` carries a 4:1 channel imbalance of its own at this
amplitude (`parts/photo-colour.json`, and `g0-instrument.md` §6). The model comparison on `photo`
is likewise inconclusive: a blurred copy beats three per-channel constants by 3% of the residual at
ring 0–6 on `rrect-lg` and loses by 2% at 6–12.

The bed settles it somewhere else, where a fixed colour and a copy of the backdrop **must** disagree.
It carries near-black pixels under six different local blur levels at one span, and over a black
pixel the black term removes nothing, so the level there is the lift alone. `parts/vibrant.json`,
ring 0–6 below, guarded, encoded luma × 255:

| span | backdrop | blur-40 at those pixels | lift, Apple | lift, vitrea GPU |
| --- | --- | --- | --- | --- |
| 96 `rrect-md` | `impulse` | 24.4 | **0.00** | 0.00 |
| 96 `rrect-md` | checkerboard, pitch 64 | 187.7 | 7.25 | — |
| 96 `rrect-md` | checkerboard, pitch 16 | 191.0 | 7.40 | 0.00 |
| 44 `capsule-button` | `impulse` | 25.1 | 0.00 | 0.00 |
| 44 `capsule-button` | checkerboard | 191.0 | 0.00 | 0.00 |
| 44 `capsule-button` | `hc-text` | 210.9 | 0.00 | 0.00 |

A fixed gray at the alpha that produces 7.4/255 over the checkerboard would put 7.4/255 over
`impulse` as well. It puts **0.00**. Regressing the lift on the blurred backdrop over the pool, at
σ 40:

| cell | n | slope | intercept | R² | residual × 255 |
| --- | --- | --- | --- | --- | --- |
| 1x `rrect-md` | 2 420 | 0.0444 | −0.0042 | 0.983 | 0.415 |
| 2x `rrect-md` | 10 648 | 0.0447 | −0.0043 | 0.982 | 0.437 |
| 1x `rrect-ml` | 2 445 | 0.0802 | −0.0161 | 0.054 | 0.729 |
| 1x `rrect-lg` | 3 070 | 0.1211 | −0.0428 | 0.245 | 0.739 |
| 1x, 2x `capsule-button` | 1 520, 6 636 | 0.0000 | −0.00000 | — | 0.000 |

**The vibrant hypothesis is supported, and on `rrect-md` it is measured rather than inferred**: with
`impulse` and the checkerboard both in the pool the line explains 98% of the variance, its slope is
0.0444 of the blurred backdrop and its intercept is −0.004, i.e. the lift crosses zero at a blurred
backdrop of about 0.10 encoded and there is no fixed colour left over. `rrect-ml` and `rrect-lg` have
no dark-backdrop cell on this bed, so their pool is the checkerboard pitches alone and their slope
and intercept are not separated — only their value at the checkerboard's blur level is; their R² of
0.05–0.25 says exactly that and should not be read as a weaker hypothesis.

The darkening. On `rrect-md` a lift of 0.0290 encoded over a blurred backdrop of 0.749 encoded is
α_v · C = 0.0376 at the falloff's peak (§6), so if the vibrant layer's colour were the blurred
backdrop undarkened its alpha would be 0.050 and if the layer tree's `VibrancyContribution` 0.333
were the alpha the colour would be 0.113 — a factor of 6.6 apart. **This bed cannot choose between
them** (§6), and a wave that needs one number should carry the product.

## 5. The thin regime's black term, by backdrop

`parts/thin-alpha.json`. Below the knee there is no lift (§2), so the exterior is the black term
alone and one ratio identifies it with nothing to disentangle: y_enc/bg_enc = 1 − α_enc·F(d) at W8's
own geometry, over every exterior pixel whose backdrop clears the shadow axis's 0.05 linear floor.
`occ` is the linear-light occlusion 1 − (1 − α_enc)^2.4 — the quantity
`MaterialOuterShadow.occlusion` names.

Light standard, spans 32 and 44, 1x (2x within 0.001 of every entry):

| backdrop | mean L | §5.50 §2 fill α | Apple, α_enc (occ) | vitrea GPU (occ) | vitrea CSS (occ) | vitrea / Apple |
| --- | --- | --- | --- | --- | --- | --- |
| `impulse` | 0.004 | none | not identifiable — below the axis floor | | | |
| `dark-solid` | 0.012 | none | not identifiable — below the axis floor | | | |
| `mid-dark-solid` | 0.060 | 0.30 | 0.1630 (0.347) | 0.1375 (0.299) | 0.1255 (0.275) | 0.86 |
| `photo`, `rrect-sm` | 0.214 | 0.285 | 0.1586 (0.339) | 0.1301 (0.284) | 0.1051 (0.234) | 0.84 |
| `photo`, capsule | 0.214 | 0.285 | 0.1557 (0.334) | 0.1367 (0.297) | 0.1250 (0.274) | 0.89 |
| checkerboard, `rrect-sm` | 0.500 | 0.278 | 0.1523 (0.327) | 0.1303 (0.285) | 0.1067 (0.237) | 0.87 |
| checkerboard, capsule | 0.500 | 0.278 | 0.1526 (0.328) | 0.1372 (0.298) | 0.1262 (0.277) | 0.91 |
| `hc-text` | 0.740 | 0.278 | 0.1529 (0.329) | 0.1394 (0.303) | 0.1249 (0.274) | 0.92 |
| **`light-solid`** | 0.891 | **0.05** | **0.0550 (0.127)** | 0.1370 (0.298) | 0.1252 (0.275) | **2.35** |

Read against §5.50 §2's table, the rendered occlusion is a constant **1.16–1.19×** the layer tree's
fill alpha on `mid-dark-solid`, `photo`, the checkerboard and `hc-text` — four backdrops spanning a
mean luminance from 0.06 to 0.74 — and **2.5×** it on `light-solid`. So the table's shape is right
where it is flat and its 0.05 at the bright end over-states the drop: the reference's shadow over
`light-solid` is not one sixth of its shadow over the checkerboard, it is **0.39 of it** (0.127
against 0.328 in linear occlusion). A declaration that keys the alpha on the same luminance the
face's response uses (the charter's third binding rule) should be anchored on 0.127 at L 0.891 and
0.33 across L 0.06…0.74, not on the layer-tree numbers directly.

Over `dark-solid` and `impulse` the multiplicative ratio is not identifiable at all — the backdrop's
mean linear luminance (0.0117, 0.0037) is below the shadow axis's own floor. The absolute reading
there is that the reference removes at most 1 of 255 codes below the capsule and 2 below `rrect-md`,
i.e. §5.50 §2's "none" is confirmed to within the capture's resolution but is a bound rather than a
fit.

**The light-solid capsule's 2.4×, decomposed** (`parts/thin-alpha.json`, ring occlusion below the
surface, linear light):

| ring, CSS px | 0–3 | 3–6 | 6–12 | 12–24 | 24–48 |
| --- | --- | --- | --- | --- | --- |
| Apple | 0.0911 | 0.0824 | 0.0686 | 0.0406 | 0.0080 |
| vitrea GPU | 0.2019 | 0.1854 | 0.1560 | 0.0950 | 0.0201 |
| vitrea CSS | 0.2066 | 0.1956 | 0.1674 | 0.1072 | 0.0285 |
| GPU / Apple | 2.22 | 2.25 | 2.27 | 2.34 | 2.49 |

At 2x: 2.17 / 2.23 / 2.28 / 2.36 / 2.58. **It is one amplitude and not a shape difference**: the
ratio is 2.2–2.3 across the near field and drifts to 2.5 only in the outermost ring, where the
reference's own signal is 2 codes. As an amplitude the whole of it is the adaptive alpha —
0.127 against vitrea's 0.285, a ratio of 2.24 — and the free geometry fit on that cell returns
σ 14.81, offset 7.97, spread 3.17 against W8's 15.55 / 7.95 / 3.1, so nothing about the shadow's
shape is involved. §5.60's 2.4× is this, read as an integral rather than as an amplitude.

**Both other schemes.** The dark scheme's thin material is flat at 0.063 linear occlusion over
`mid-dark-solid`, `photo` and the checkerboard alike (α_enc 0.0267–0.0271 on every one), against
vitrea's 0.098–0.131 — vitrea 1.6–2.4× too dark. Under increased contrast and reduced transparency,
which macOS force-couples (claims §5.27, W8), the reference is flat at 0.192–0.202 on every cell,
thin and thick alike, and vitrea reads 0.198–0.208: **W8's reduced-transparency fold of 0.7 is
correct and no adaptation survives the preference**.

**The thick regime is not a constant either, once rendered.** The layer tree says the thick
material's shadow fill α is 0.12 on every backdrop (claims §5.50 §2). The rendered composite is not:
the same `rrect-md` reads α_enc 0.1303 over the checkerboard, 0.1110 over `hc-text`, 0.0893 over
`light-solid` and 0.0848 over `photo`. Part of that is the lift arriving on the same pixels (over a
bright backdrop the lift is brighter and cancels more of the black term), and this bed cannot say
whether any of it is the black term itself — the two are separable only on the checkerboard (§6).
What it does say is that a model with a constant thick alpha and no lift, which is what vitrea has,
cannot match the exterior on four backdrops at once.

## 6. The geometry: whose lengths are whose

`parts/geometry.json`. On the checkerboard the two terms are read separately with no model in the
way: the black squares give the lift Λ(d), the white squares give Λ(d) plus the transmission, and
their difference gives the transmission alone.

**The black term's falloff, from the thin cells and the solids, where no lift exists** (free fit,
four parameters, 1x; 2x within 0.4 of every σ and 0.05 of every offset):

| cell | α_enc | occ | σ | offset | spread | rms × 255 |
| --- | --- | --- | --- | --- | --- | --- |
| checkerboard `rrect-sm` | 0.1717 | 0.364 | 16.19 | 7.99 | 0.88 | 0.24 |
| checkerboard `capsule-button` | 0.1709 | 0.362 | 16.11 | 7.96 | 0.99 | 0.26 |
| `mid-dark-solid` capsule | 0.1648 | 0.351 | 15.30 | 7.93 | 2.99 | 0.82 |
| `light-solid` capsule | 0.0554 | 0.128 | 14.81 | 7.97 | 3.17 | 0.23 |
| **W8 as landed** | 0.1304 | 0.285 | **15.55** | **7.95** | **3.1** | — |
| vitrea GPU, same fit | 0.125–0.127 | 0.274–0.279 | 15.0–15.1 | 7.97–8.00 | 3.66–3.95 | 0.24 |

**W8's three lengths are the black term's, and G0 does not refit them.** Across four cells that span
two backdrops, two spans and both scales the measured σ is 14.8–16.2 against 15.55, the offset is
7.93–8.00 against 7.95 — the layer tree's `inputShadowOffset` (0, 8) exactly — and the spread is
0.9–3.2 against 3.1. The residual spread of σ is 9% and of the spread parameter is 2.3 CSS px, which
is the same order W8 itself reported (σ 15.4–15.9, offset 6.9–8.1). Nothing on this bed asks for a
different geometry, and the charter's rule that W8's lengths are not refit unless G0 shows them
wrong is satisfied by leaving them alone.

**The lift's falloff, from the black squares alone** (free fit; the layer tree's own span laws
beside it):

| cell | amplitude A_v | σ | offset | spread | `Height` 0.4·span | `Amount` min(0.625·span, 75) | rms × 255 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1x `rrect-md` | 0.0376 | 14.36 | 8.09 | 4.70 | 38.4 | 60.0 | 0.23 |
| 1x `rrect-ml` | 0.0695 | 15.82 | 7.88 | 1.46 | 51.2 | 75.0 | 0.32 |
| 1x `glass-over-glass` | 0.0762 | 16.45 | 7.64 | −0.05 | 52.0 | 75.0 | 0.68 |
| 1x `rrect-lg` | 0.0727 | 16.81 | 8.33 | 0.96 | 64.0 | 75.0 | 0.73 |
| 2x `rrect-md` | 0.0364 | 14.14 | 8.08 | 5.16 | 38.4 | 60.0 | 0.22 |
| 2x `rrect-ml` | 0.0682 | 15.61 | 7.91 | 1.80 | 51.2 | 75.0 | 0.32 |
| 2x `rrect-lg` | 0.0750 | 17.11 | 8.36 | 0.29 | 64.0 | 75.0 | 0.73 |

**The lift has no geometry of its own.** Its σ is 14.1–17.1 and its downward offset is 7.6–8.4 —
the black term's, and W8's. It is not `Height` = 0.4·span (38 to 64 CSS px, which would put the
lift's core well below the contour and make the above/below asymmetry far stronger than the
measured 0.41), and it is not `Amount` = min(0.625·span, 75) outward. The layer tree's `Amount`,
`Height` and the working reading in the charter's advisory ("W8's lengths are the black term's and
the `Amount` / `Height` / `BlurRadius` 40 are the vibrant term's extent and blur") is therefore
**half right**: `BlurRadius` 40 is the vibrant term's blur, of the backdrop it copies (§3), and
`Amount` / `Height` are **not** its spatial extent on this bed. One falloff carries both terms.

**And that is why the two terms' amplitudes do not separate.** With the two shapes measured, the
correlation between them over the exterior is 0.9997–0.9999 on every thick cell at both scales, and
the joint fit for the vibrant colour C, the vibrant alpha α_v and the black alpha α_b runs along a
flat ridge — C lands on its bound of 1.0 with α_b 0.141–0.180 (occ 0.306–0.378), and a start that
walks off the ridge lands at α_b ≈ 0.002 with a nonsense σ. **On this bed the decomposition into
(α_v, C, α_b) is not identifiable**; what is identifiable, exactly and at the capture's own noise
floor, is the pair of profiles:

- the **lift** Λ(d) = A_v · F(d), A_v = 0.0376 / 0.0695 / 0.0727 encoded at spans 96 / 128 / 160,
  scaled by the local σ-40 blurred backdrop relative to the checkerboard's 0.749 (§4);
- the **composite transmission** T(d) = 1 − α_T · F(d) on the whites with the lift removed,
  α_T = 0.1798 / 0.2490 / 0.2790 encoded at the same spans (occ 0.379 / 0.497 / 0.544), against
  vitrea's 0.127–0.135 (occ 0.279–0.294) read the same way.

Those two are what a renderer needs, and neither requires knowing which of the two layers owns which
part of the alpha. Reported here rather than resolved, because resolving it needs a backdrop that
separates the shapes — a thick surface over `impulse` or `dark-solid` at spans 128 and 160, which
this bed does not carry (only `rrect-md` has them).

## 7. Where vitrea stands, cell by cell

Collected from the tables above, GPU tier, light standard.

| what | Apple | vitrea | gap |
| --- | --- | --- | --- |
| black term's geometry | σ 14.8–16.2, offset 7.93–8.00, spread 0.9–3.2 | σ 15.55, offset 7.95, spread 3.1 | none measurable |
| thin alpha, checkerboard / `photo` / `hc-text` / `mid-dark` | occ 0.33–0.35 | 0.285 | vitrea 0.84–0.91× — too light |
| thin alpha, `light-solid` | occ 0.127 | 0.285 | vitrea **2.24×** — too dark |
| thin alpha, dark scheme | occ 0.063 | 0.089–0.131 | vitrea 1.6–2.4× — too dark |
| reduced transparency / increased contrast | occ 0.192–0.202 | 0.198–0.208 | none measurable |
| thick composite, checkerboard | occ 0.379–0.544 by span | 0.279–0.294 | vitrea too light, and the deficit grows with span |
| the lift | 0.029–0.048 encoded, spans 96–160 | **0.0000** | the whole facet is missing |
| over `dark-solid`, `impulse` | ≤ 2 codes | 0 codes | none measurable — both inert |

## 8. What the declaration should carry

For G1, from what is measured rather than what is assumed.

**The form.** In the compositing (encoded) domain, outside the coverage:

    out = bg · (1 − α_b(backdrop, span, scheme, a11y) · F(d))  +  A_v(span) · F(d) · V

with **one** falloff `F` — W8's own: the surface's silhouette outset by `spreadPx`, translated down
by `offsetPx`, through `outerShadowFalloff` at `sigmaPx`, all three unchanged at 3.1 / 7.95 / 15.55
— and `V` the local σ-40 CSS px blurred backdrop, relative to the level the amplitudes were fitted
at (0.749 encoded). The second term is zero below span 64 and zero over a black backdrop by
construction, so the material stays exactly inert over `dark-solid` and `impulse` on both tiers, and
W8's "invisible over black" property survives intact.

**The constants, as measured.**

- `sigmaPx` 15.55, `offsetPx` 7.95, `spreadPx` 3.1 — kept, not refit (§6).
- The black term's amplitude, thin regime (span ≤ 64), light scheme, as linear occlusion:
  **0.33** across backdrop luminance 0.06…0.74, **0.127** at 0.891, and inert below 0.05. Three
  anchors on the same luminance statistic W9's face response uses, which is the charter's third
  binding rule; the interpolation between 0.74 and 0.891 is unconstrained by this bed and needs to
  be declared as a choice.
- The black term's amplitude, dark scheme, thin: **0.063**, flat on all three measurable backdrops.
- Under `frost: increased`: **0.192–0.202** flat, thin and thick alike — W8's 0.7 fold, unchanged.
- The lift's peak amplitude A_v by span, encoded, at V = 0.749: **0.0376 / 0.0695 / 0.0727** at
  spans 96 / 128 / 160, zero at 64 and below. Not clamp((span−64)/96): as a fraction of its
  span-160 value it reads 0.52 at span 96 and 0.96 at span 128, against 0.33 and 0.67.
- The thick regime's composite amplitude on the checkerboard, for the referee to predict against:
  occ 0.379 / 0.497 / 0.544 at spans 96 / 128 / 160.

**What the CSS tier can carry without a second element.** The geometry and the adaptive alpha, in
full: a `box-shadow` of pure black takes one colour and one alpha, and everything in the black term
is exactly that. The measured CSS captures already track the GPU tier's black term to within 0.05 in
occlusion on every cell (0.234–0.303 against 0.284–0.303), so the whole of the thin regime's gap —
the `light-solid` capsule's 2.2× included — closes on the CSS tier with a profile change and no
new element. **The lift cannot be carried by a `box-shadow`**: it needs the backdrop's own light outside the element, which means a
pseudo-element with `backdrop-filter: blur(40px)` masked to the falloff, which is Decision Log 1's
question (b). The share at stake is the lift alone: 0.029–0.048 encoded on the thick spans, nothing
on the thin ones, and nothing over a dark backdrop.

**What remains unidentifiable on this bed, and what would identify it.**

1. **The split of the composite into (α_v, C, α_b).** The two terms ride one falloff, correlation
   0.9998 (§6). A thick surface (span 128 or 160) over `impulse` or `dark-solid` would kill the lift
   and leave the black term alone; the bed has that cell only at span 96.
2. **The vibrant term's darkening.** Same cause: α_v · C = 0.0376 at span 96 is measured, the two
   factors are not.
3. **σ on the mid spans.** Identified only on `rrect-lg` (40 ± 8 CSS px). `rrect-ml` and `rrect-md`
   are flat to 0.7%; a pitch-128 probe, or a probe canvas with more exterior, would separate them.
4. **The adaptive alpha between L 0.74 and 0.891.** The bed jumps from `hc-text` to `light-solid`
   with nothing between, and the whole factor-of-2.6 drop happens in that gap.
5. **The dark scheme's thick regime.** `checkerboard__rrect-md` reads occ 0.230 and
   `photo__rrect-lg` 0.268 there, against the thin material's 0.063 — the amplitude rises with span
   in the dark scheme and falls in the light one, which is exactly W8's `sizeGain` seam
   (`MaterialOuterShadow.sizeGain`, shipped at the identity). This wave's decomposition **explains
   the sign** — the light scheme's thick composite includes a lift that a dark backdrop does not
   produce — but the dark scheme's own numbers are the composite, and its layer tree has not been
   dumped (W12 Deferred: `dump-layers` needs a scheme flag). The seam should stay at the identity
   until that is read.
6. **The `photo` colour reading.** The lift's colour is settled by the dark backdrops (§4), not by
   `photo`; the per-channel instrument's own null is 0.002 with a 4:1 imbalance, so a coloured lift
   at this amplitude is below what a per-channel affine fit can resolve on this bed.

**Two findings outside this wave's subject**, from `g0-instrument.md` §4, both to the tech-debt
tracker and this wave's Deferred list:

- the GPU tier's capsule over-fills its declared contour by 3.5–4 CSS px at the caps (Apple: ≤ 1);
- the CSS tier over-fills by 3–3.5 CSS px toward the bottom right on every component and both
  scales.

Claims §5.12 states that the shape axis is bounded to the declared region and therefore cannot see
over-fill. These are the first measurements of it, and they belong to the shape axis, not here.

---

## For claims §5.61

### 5.61 W14 G0: the reference's outer shadow is two terms on one falloff — a backdrop-adaptive black multiply and a blurred copy of the backdrop's own light (2026-09-03)

**Claim.** The per-ring affine instrument the charter's first binding rule asks for, validated on
vitrea's own captures before any reference number, and the reference read on 82 cells across six
profiles at both scales. Findings, scripts and figures under
`packages/calibration/results/2026-09-03-w14-shadow/g0/` (`g0-instrument.md`, `g0-shadow.md`,
`w14lib.py`, `g0_*.py`, `parts/*.json`, four figures). Nothing captured, no constant moved.

**1. The instrument, and its validation (X4).** Signed distance to the region `scenes.json` declares
(never to the image, §5.12's rule), four sides by the nearest rect's normal with the corner arcs as
their own class, five rings plus §5.60's 0–6, and `y = a·bg + c` per side × ring in both linear
luminance and encoded Rec.709 luma. On vitrea's canonical GPU captures the instrument recovers W8's
black multiply to **±0.0016 in `a` and ±0.0000 in `c`** on every ring and flat side of
`checkerboard__{rrect-lg, rrect-md, capsule-button}` and `photo__rrect-md` at both scales, and the
level on `light-solid__capsule-button` to ±0.0034; the one class it fails is the capsule's corner
sector, for a reason that is a measurement of vitrea (§4 below). The charter's stated form of the
model, the linear multiply 1 − 0.285·F, sits within 0.0043 of the fit; the composite the shader
actually produces — black at `outerShadowAlpha(0.285)·F` in the ENCODED domain — sits within 0.0016,
and is what the reference tables are read against. **The linear-space reading of vitrea's own shadow
was 5% low (0.271 against 0.285) until the sRGB decode was done exactly**: the linear factor is not
(1 − α·F)^2.4, because sRGB's decode carries the 0.055 offset. §5.60 §3's +0.039 / +0.024 / +0.014
was read in encoded luma; the same lift is +0.0038 / +0.0030 / +0.0020 in linear light, and this
wave says which space every number is in.

**2. The lift: only above the knee, scale-free, not proportional to `VibrancyContribution`.** On the
checkerboard the black squares carry the lift alone (a multiply is inert over black). Ring 0–6 below
the surface, encoded: **0.0000 at spans 32 and 44, 0.0290 at 96, 0.0439 at 128, 0.0448 at 130
(`glass-over-glass`), 0.0479 at 160**; at 2x 0.0000 / 0.0000 / 0.0292 / 0.0445 / 0.0454 / 0.0487,
and the W9 and W12 probe beds reproduce every row to the fourth decimal. vitrea reads 0.0000
everywhere. The knee at 64 is exact. Against `inputShadowVibrancyContribution` =
clamp((span − 64)/96, 0, 1) the ratio is **0.087 / 0.066 / 0.065 / 0.048** at spans 96 / 128 / 130 /
160 — a factor of 1.8, so the lift is *not* proportional to it: it rises and saturates, reaching 91%
of its span-160 value by span 128. By side it is below 0.0479, left 0.0327, right 0.0342, above
0.0196 on `rrect-lg` — an above/below ratio of 0.41 on every thick span, which one silhouette
displaced 8 CSS px down produces exactly.

**3. The lift is the backdrop's own light, blurred at σ 40 CSS px.** Over `impulse` (blurred
backdrop 24/255) `rrect-md` lifts **0.00**; over the checkerboard (191/255) it lifts 7.40/255.
Pooled over six backdrops the regression at σ 40 gives slope 0.0444, intercept −0.0042, R² 0.983
(2x: 0.0447, −0.0043, 0.982) — proportional to the blurred backdrop with no fixed colour left over.
A fixed gray is excluded. The σ comes from the probes' pitch axis, where the lift is flat across
pitches 4–32 and drops at pitch 64 by 8.3% on `rrect-lg` as the blurred plate drops 4.4%: the
pooled residual has a real minimum at **σ = 40 CSS px** on `rrect-lg` at both scales and in two
rings, 12% below the flat-copy residual, which is `inputShadowBlurRadius` 40 (§5.50 §2) read as a
Gaussian standard deviation. On `rrect-ml` and `rrect-md` σ is **not identifiable** (flat to 0.7%)
and is reported as such. §5.60 §3's "no blurred copy detectable" stands: it was read on pitch 16,
where a σ-40 copy is constant to 0.001.

**4. The geometry: one falloff, W8's, for both terms.** Free four-parameter fits on the cells where
each term is alone give σ 14.8–16.2, offset 7.93–8.00, spread 0.9–3.2 for the black term (four
cells, two backdrops, two spans, both scales) and σ 14.1–17.1, offset 7.6–8.4 for the lift (four
thick cells, both scales) — both W8's 15.55 / 7.95 / 3.1, and the offset is the layer tree's
`inputShadowOffset` (0, 8) exactly. **W8's lengths are the shadow's and are not refit.** The layer
tree's `inputShadowAmount` and `inputShadowHeight` are **not** the lift's spatial extent; only
`inputShadowBlurRadius` 40 belongs to it, as the blur of the backdrop it copies. Because both terms
ride one falloff their shapes correlate at 0.9997–0.9999 and the split into (vibrant alpha, vibrant
colour, black alpha) is **not identifiable on this bed**; what is identifiable at the capture's noise
floor is the pair — the lift A_v = 0.0376 / 0.0695 / 0.0727 encoded at spans 96 / 128 / 160, and the
composite transmission α_T = 0.1798 / 0.2490 / 0.2790 (linear occlusion 0.379 / 0.497 / 0.544)
against vitrea's 0.279–0.294. A thick surface over `impulse` or `dark-solid` at span 128 or 160
would separate them; the bed has that cell only at span 96.

**5. The thin regime's alpha, and the light-solid capsule's 2.4× as one amplitude.** Below the knee
the exterior is the black term alone. Linear occlusion, light standard: **0.347** over
`mid-dark-solid`, **0.334–0.339** over `photo`, **0.327–0.328** over the checkerboard, **0.329**
over `hc-text`, **0.127** over `light-solid`; not identifiable over `dark-solid` and `impulse`
(below the shadow axis's 0.05 floor), where the reference removes at most 1–2 of 255 codes. Against
§5.50 §2's fill-alpha table the rendered occlusion is a constant **1.16–1.19×** the tabulated alpha
on the four mid backdrops and **2.5×** on `light-solid`: the table's 0.05 over-states the drop, and
the reference's shadow over `light-solid` is 0.39 of its shadow over the checkerboard, not one
sixth. vitrea's 0.285 is 0.84–0.91× the reference on the four mid backdrops and **2.24×** it on
`light-solid`; by ring the ratio is 2.22 / 2.25 / 2.27 / 2.34 / 2.49 at 0–3 / 3–6 / 6–12 / 12–24 /
24–48 CSS px, and the free geometry fit on that cell returns σ 14.81 / offset 7.97 / spread 3.17, so
**§5.60's 2.4× is one amplitude and no part of it is shape**. The dark scheme's thin material is
flat at 0.063 on all three measurable backdrops against vitrea's 0.098–0.131. Under increased
contrast and reduced transparency alike the reference is flat at 0.192–0.202, thin and thick
together, against vitrea's 0.198–0.208: **W8's 0.7 fold is correct and no adaptation survives the
preference.**

**6. Two gaps outside this wave's subject, measured because nothing else can see them.** §5.12
states that the shape axis is bounded to the declared region and therefore cannot measure over-fill.
Walking outward from the contour until no black checkerboard square carries the body gives, in CSS
px: Apple ≤ 1 on every component; vitrea's GPU tier 0.5–1 on the rounded rectangles but **3.5–4 on
the capsule's caps**; vitrea's CSS tier **3–3.5 on every component**, on `below`, `right` and
`corner` — a displacement toward the bottom right rather than a halo. Both are recorded in the
tech-debt tracker and in W14's Deferred list; neither is the shadow's.

**7. What it changes.** G1 declares a composite of two terms on W8's own falloff, with the black
term's amplitude keyed on the backdrop luminance the face's response already uses (three anchors:
0.33 across L 0.06…0.74, 0.127 at 0.891, inert below 0.05) and the lift as a σ-40 blurred sample of
the backdrop at an amplitude that is zero below span 64 and saturating above it. Both tiers carry
the geometry and the adaptive alpha — which is the whole of the thin regime's gap and needs no new
element — and Decision Log 1's question narrows to the lift alone, worth 0.029–0.048 encoded on the
thick spans and nothing on the thin ones or over a dark backdrop.
