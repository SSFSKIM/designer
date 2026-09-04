# W16 G0 — what Chromium can draw for the two-layer CSS body, and with what instrument (2026-09-04)

The spike the W16 charter opens with (`docs/doperpowers/specs/2026-09-04-w16-css-two-layer-body.md`,
child G0). It changes no runtime, no profile and no golden: every form below is hand-built on a probe
page out of the material profile's own numbers, dumped from `packages/platform-web/src/optics.ts` by
`dump-law.ts` so that no constant is transcribed. Every capture is real Chromium
(`channel: "chromium"`, `--enable-unsafe-webgpu --enable-features=Vulkan,WebGPU`, the harness's own
recipe in `scripts/capture-web.ts`), never the headless shell, and `VITREA_ALLOW_FALLBACK_ADAPTER`
was never set. Engine: **chromium 151.0.7922.34**.

Scripts and pages beside this file: `dump-law.ts` (the law), `plates.py` (the probe backdrops),
`pages/probe.html` (every optical form), `capture.mjs` (the driver), `pages/cost.html`, `cost.mjs`
and `cost-probe.js` (the cost), `score-body.py` (the body's RMS), `ramp-read.py` (W13's
depth-window instrument on this tier). Machine-readable output in `parts/`.

## 0. The answer to the first question

**`mask-image` composes with `backdrop-filter` and `opacity` on one element in Chromium 151.** A
`mask-image` of uniform alpha *a* on a `backdrop-filter` layer renders **bit-identically** to
`opacity: a` on the same layer, and a mask of alpha 0.8 combined with `opacity: 0.5` renders
bit-identically to `opacity: 0.40`. Over `rrect-md`'s interior box, on the pitch-16 checkerboard:

| pair | RMS over the interior box | max over the interior box | max over the whole canvas |
| --- | --- | --- | --- |
| `opacity: 0.40` vs `mask-image` alpha 0.40 | **0.000000** | **0.000000** | 0.100889 |
| `opacity: 0.40` vs mask alpha 0.80 × `opacity: 0.5` | **0.000000** | **0.000000** | 0.105558 |
| `opacity: 0` vs mask alpha 0 | 0.000000 | 0.000000 | 0.000000 |
| `opacity: 1` vs mask alpha 1.0 | **0.000000** | **0.000000** | 0.208976 |

The whole-canvas maxima are the contour pixel and nothing else: the raster mask's own antialiasing
against the layer's `border-radius` clip differs from the clip alone by up to one strong code value
on the single boundary pixel. Inside the material there is no difference at all.

The carrier mechanism does not matter, which is the useful part — every one of these composes:

| how the heavy layer's weight is carried | result |
| --- | --- |
| `opacity` | composes |
| `mask-image: url(<png>)` with `mask-mode: alpha` | composes |
| `mask-image: url(<png>)` with no `mask-mode` | composes |
| `-webkit-mask-image: url(<png>)` | composes |
| `mask-image: linear-gradient(…)` | composes |
| `-webkit-mask-image: linear-gradient(…)` | composes |
| `clip-path: inset(0 round Rpx)` with `opacity` | composes |
| `will-change: backdrop-filter` with the mask | composes |
| the mask on a **wrapper**, the filter on its child | **the filter is inert** — the child renders nothing |

The last row is the one to carry forward: a masked *ancestor* is a backdrop root and kills a
descendant's `backdrop-filter` (`md-parent-mask` reproduces the sharp layer alone, RMS 0.000000
against it). So the mask has to sit on the filtered element itself, never on a wrapper.

**The charter's Risk "`mask-image` does not compose with `backdrop-filter` in Chromium" does not
fire.** The ramp does not have to fall back to one `opacity`.

## 1. The two-layer body against the reference — and the one thing that stops it (charter G0 (a))

### 1.1 Contract X4 — the pipeline reproduces claims §5.42 §5's own published columns

`score-body.py` regresses the native probe cell on one structure column with a level `a` and a
transmission `t` free per span and shared across pitches 8 / 16 / 32 / 64, over §5.41's inset
interior box, exactly as §5.42 §5 declared. Fed §5.42 §5's own model columns it returns §5.42 §5's
own numbers:

| cell | GPU law, published | reproduced here | CSS σ today, published | reproduced here (at §5.42 §5's σ) |
| --- | --- | --- | --- | --- |
| `rrect-sm` | 0.0280 | **0.0280** | 0.0708 | **0.0708** |
| `capsule-button` | 0.0281 | **0.0281** | 0.0784 | **0.0784** |
| `rrect-md` | 0.0138 | **0.0138** | 0.0615 | **0.0615** |
| `rrect-ml` | 0.0148 | **0.0148** | 0.0491 | **0.0491** |
| `rrect-lg` | 0.0174 | **0.0174** | 0.0376 | **0.0376** |

(The second pair needs §5.42 §5's own σ — 4.75 / 4.79 / 5.79 / 6.82 / 7.93 — because the tier's σ
moved at W13 G1 when the ramp's area mean replaced the uniform share. At today's σ the same model
column reads 0.0631 / 0.0681 / 0.0599 / 0.0464 / 0.0354.)

### 1.2 What Chromium draws, measured

Every column below is a Chromium capture of a page scored by the pipeline just validated. The
"model GPU law" column is the analytic two-component law at this scale's own widths, and is the
target the acceptance is written against.

### RMS against the native probe bed, dpr 1

| cell | span | model GPU law | model CSS σ today | capture: one blur | capture: two flat (kDeep) | capture: two flat (area) | capture: two + raster ramp | capture: reference filter, sRGB | capture: reference filter, linearRGB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.0280 | 0.0631 | 0.0704 | 0.0273 | 0.0255 | 0.0252 | 0.0273 | 0.0327 |
| `capsule-button` | 44 | 0.0281 | 0.0681 | 0.0880 | 0.0566 | 0.0492 | 0.0498 | 0.0566 | 0.0310 |
| `rrect-md` | 96 | 0.0138 | 0.0599 | 0.0789 | 0.0410 | 0.0399 | 0.0400 | 0.0410 | 0.0207 |
| `rrect-ml` | 128 | 0.0148 | 0.0464 | 0.0678 | 0.0434 | 0.0422 | 0.0420 | 0.0434 | 0.0209 |
| `rrect-lg` | 160 | 0.0174 | 0.0354 | 0.0569 | 0.0432 | 0.0416 | 0.0414 | 0.0432 | 0.0209 |

### RMS against the native probe bed, dpr 2

| cell | span | model GPU law | model CSS σ today | capture: one blur | capture: two flat (kDeep) | capture: two flat (area) | capture: two + raster ramp | capture: reference filter, sRGB | capture: reference filter, linearRGB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.0456 | 0.0485 | 0.0591 | 0.0510 | 0.0384 | 0.0375 | 0.0510 | 0.0453 |
| `capsule-button` | 44 | 0.0330 | 0.0489 | 0.0723 | 0.0587 | 0.0390 | 0.0417 | 0.0587 | 0.0334 |
| `rrect-md` | 96 | 0.0271 | 0.0347 | 0.0664 | 0.0539 | 0.0543 | 0.0534 | 0.0539 | 0.0262 |
| `rrect-ml` | 128 | 0.0309 | 0.0267 | 0.0603 | 0.0581 | 0.0600 | 0.0585 | 0.0581 | 0.0305 |
| `rrect-lg` | 160 | 0.0234 | 0.0229 | 0.0521 | 0.0504 | 0.0514 | 0.0504 | 0.0504 | 0.0242 |

Read the 1x table against the acceptance ("the tier's RMS within 1.5× the GPU law's at every span",
i.e. ≤ 0.0420 / 0.0422 / 0.0207 / 0.0222 / 0.0261):

| cell | one blur today | two `blur()` layers (area-mean share) | ratio to the GPU law | two `url(#f)` layers, linearRGB (`kDeep` share) | ratio |
| --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 0.0704 | 0.0255 | **0.91×** | 0.0327 | 1.17× |
| `capsule-button` | 0.0880 | 0.0492 | 1.75× | 0.0310 | **1.10×** |
| `rrect-md` | 0.0789 | 0.0399 | 2.89× | 0.0207 | **1.50×** |
| `rrect-ml` | 0.0678 | 0.0422 | 2.85× | 0.0209 | **1.41×** |
| `rrect-lg` | 0.0569 | 0.0416 | 2.39× | 0.0209 | **1.20×** |

**The two-layer body halves the residual on every span and still misses the acceptance on four of
five — and the mechanism is the colour space, not Chromium.** `backdrop-filter: blur()` is an
operator on the page's *encoded* values; the reference's body is linear in luminance, which is what
`structure_gpu` models and what the GPU tier draws. Three readings pin it:

| cell | the law, blurred in LINEAR light | the same law, blurred in the ENCODED space | the capture | the capture against its own encoded-chain model, (a, t) free |
| --- | --- | --- | --- | --- |
| `rrect-sm` | 0.0280 | 0.0298 | 0.0273 | 0.01503 |
| `capsule-button` | 0.0281 | 0.0525 | 0.0566 | 0.00487 |
| `rrect-md` | 0.0138 | 0.0389 | 0.0410 | 0.00243 |
| `rrect-ml` | 0.0148 | 0.0410 | 0.0434 | 0.00242 |
| `rrect-lg` | 0.0174 | 0.0408 | 0.0432 | 0.00268 |

The fourth column is the honest statement: **Chromium draws the law**. The capture agrees with the
forward model of what the page asked for — the sharp layer's encoded blur, the heavy layer's encoded
blur of *that* output at σ_b·√(gain² − 1), mixed at the heavy share in the encoded space — to RMS
0.0024–0.0049 on the four larger spans. The third column is the cost of the space, and it is
2.4–2.8× on the three thick spans. On the probe bed's black-and-white plate the encoding is the
whole of the deficit, and no σ, no share and no mask can move it.

### 1.3 The way out that the charter did not name: a reference filter in linear light

`backdrop-filter: url(#f)` with an SVG `feGaussianBlur` and `color-interpolation-filters="linearRGB"`
— SVG's own default — blurs in linear light. Chromium is the only engine that renders a reference
filter inside `backdrop-filter` at all, and the conformance table already records exactly that
(`referenceFilterInBackdrop: true` on the two Chromium rows, `false` on Gecko and both WebKit rows,
citing WebKit 245510 and Gecko 1887451). The same two-layer form with the same widths and the same
share, drawn that way:

| cell | GPU law model (linear) | two `blur()` layers | two `url(#f)` layers, `sRGB` | two `url(#f)` layers, `linearRGB` |
| --- | --- | --- | --- | --- |
| `rrect-sm` @1x | 0.0280 | 0.0273 | 0.0273 | 0.0327 |
| `capsule-button` @1x | 0.0281 | 0.0566 | 0.0566 | **0.0310** |
| `rrect-md` @1x | 0.0138 | 0.0410 | 0.0410 | **0.0207** |
| `rrect-ml` @1x | 0.0148 | 0.0434 | 0.0434 | **0.0209** |
| `rrect-lg` @1x | 0.0174 | 0.0432 | 0.0432 | **0.0209** |
| `rrect-sm` @2x | 0.0456 | 0.0510 | 0.0510 | **0.0453** |
| `capsule-button` @2x | 0.0330 | 0.0587 | 0.0587 | **0.0334** |
| `rrect-md` @2x | 0.0271 | 0.0539 | 0.0539 | **0.0262** |
| `rrect-ml` @2x | 0.0309 | 0.0581 | 0.0581 | **0.0305** |
| `rrect-lg` @2x | 0.0234 | 0.0504 | 0.0504 | **0.0242** |

The `sRGB` column is bit-for-bit the `blur()` column on every cell and both scales, which is the
control: the reference filter changes nothing except the space it works in. At **2x the linearRGB
form lands on the analytic GPU law within 0.0008 on every span** (ratios 0.99 / 1.01 / 0.97 / 0.99 /
1.03), and at 1x within 1.10–1.50× of it. This is the only measured form that meets the charter's
parent-level acceptance for the body, and it is Chromium-only by construction.

### 1.4 The contour ring — where the tint has to go

The same two layers with the host's tint (`rgba(255,255,255,0.46)`) *beneath* them against the same
tint on a third layer *above* them, pitch 16, encoded means by depth band:

| cell | depth band, CSS px | tint under the layers | tint over them | difference |
| --- | --- | --- | --- | --- |
| `rrect-md` | 0–1 | 0.7104 | 0.7210 | −0.0106 |
| `rrect-md` | 1–2 | 0.7196 | 0.7294 | −0.0098 |
| `rrect-md` | 2–4 | 0.7221 | 0.7295 | −0.0074 |
| `rrect-md` | 4–8 | 0.7240 | 0.7294 | −0.0054 |
| `rrect-md` | 8–16 | 0.7269 | 0.7294 | −0.0026 |
| `rrect-md` | 16–32 | 0.7289 | 0.7294 | −0.0005 |
| `rrect-md` | whole silhouette | 0.7267 | 0.7291 | −0.0025 |
| `rrect-lg` | 0–1 | 0.7106 | 0.7212 | −0.0106 |
| `rrect-lg` | 1–2 | 0.7149 | 0.7294 | −0.0145 |
| `rrect-lg` | 2–4 | 0.7185 | 0.7294 | −0.0109 |
| `rrect-lg` | 4–8 | 0.7214 | 0.7294 | −0.0081 |
| `rrect-lg` | 8–16 | 0.7255 | 0.7294 | −0.0039 |
| `rrect-lg` | 16–32 | 0.7281 | 0.7295 | −0.0013 |
| `rrect-lg` | whole silhouette | 0.7268 | 0.7293 | −0.0025 |

The charter's linearity argument holds away from the contour and fails inside a kernel's width of it,
exactly as it predicted, and the size of the failure is now a number: **the tint beneath the layers
darkens a ring 0.010–0.015 encoded deep over the first 4 CSS px and 0.004–0.008 out to 8**, decaying
to a thousandth by 16–32. Over the whole silhouette it is 0.0025, which is inside the bed's noise
but is a *band* and not a level, and the band is the statistic this wave exists to fix. The
capture also confirms the paint order empirically: the layers blur the host's own background, so
negative-`z-index` children do paint above it.

**Recommendation: the tint goes on a third created layer above both filters.** It is the same
`rgba()` over the same blurred backdrop away from the ring, and it removes the ring.

## 2. The ramp's three mask carriers (charter G0 (b))

### 2.1 The carriers' own alpha, read directly

An opaque white layer under the carrier's mask over a black page composites to exactly the mask's
alpha, so one capture is the whole 2-D mask field with no filter in the loop. Against the shader's
k(u) evaluated on the same rounded-rect SDF (contour pixel excluded, u > 1 CSS px):

| carrier | cell | region | mean \|Δ\| | p99 \|Δ\| | max \|Δ\| |
| --- | --- | --- | --- | --- | --- |
| raster | `rrect-md` | inside | **0.0010** | 0.0018 | **0.0019** |
| raster | `rrect-md` | straight runs | 0.0010 | 0.0018 | 0.0018 |
| raster | `rrect-md` | corners | 0.0010 | 0.0019 | 0.0019 |
| SVG inset, blurred | `rrect-md` | inside | 0.0104 | 0.0203 | 0.0208 |
| SVG inset, blurred | `rrect-md` | corners | 0.0052 | 0.0105 | 0.0110 |
| gradient stack | `rrect-md` | inside | 0.0324 | 0.0665 | 0.0693 |
| gradient stack | `rrect-md` | corners | **0.0608** | 0.0690 | 0.0693 |
| raster | `rrect-lg` | inside | **0.0010** | 0.0020 | **0.0020** |
| SVG inset, blurred | `rrect-lg` | inside | 0.0476 | 0.1154 | 0.1214 |
| SVG inset, blurred | `rrect-lg` | corners | 0.0207 | 0.0539 | 0.0600 |
| gradient stack | `rrect-lg` | inside | 0.0619 | 0.2018 | 0.2111 |
| gradient stack | `rrect-lg` | corners | **0.1895** | 0.2079 | 0.2111 |

The raster carrier's 0.0010 mean and 0.0020 maximum are **the 8-bit mask channel's own
quantisation** (half of 1/255 = 0.0020) and nothing else: it is exact to the alpha channel's
resolution everywhere, corners included. The SVG carrier's error is its profile — an erf where the
law is a straight ramp — and it grows with the span because the ramp's reach covers more of a large
surface. The gradient stack's error is what the charter predicted and then some: `mask-composite:
intersect` **multiplies** alphas where the distance field takes a minimum, so its corner error
(0.061 / 0.190 mean) is 2–4× its straight-run error, and it is the worst carrier on both cells even
along a straight edge because twelve colour stops cannot follow the profile the way a raster can.

### 2.2 W13's depth-window instrument on the tier's own captures, with X4 beside every reading

`ramp-read.py` runs W13 G0's windowed estimator (`w13lib.WindowFit.solve_shared_t`) on these
captures with two changes, both forced by what the CSS tier is: the fixed lens is pinned at
**zero** displacement (`thickness=0`), because this tier draws no displacement field; and the
instrument is fed the capture's **encoded** grey rather than its linear luminance, because
`backdrop-filter: blur()` is linear in the encoded space. The second change is exact rather than
approximate — the probe's plates are 0 and 1 in both spaces, so the analytic blurred plate the
estimator builds is the same array either way — and it makes `Y = a + t·[(1−k)·A + k·B]` hold
bit-for-bit on this tier. Pitches 16 / 32 / 64, the pool W13 validated the estimator in.

| reading | cell | windows | u range | max |k − truth| | mean (k − truth) | fit RMS |
| --- | --- | --- | --- | --- | --- | --- |
| X4 known ramp (0.30 -> 0.90 over 40 CSS px) | `rrect-md` | 10 | 6–42 | 0.0083 | +0.0010 | 0.00799 |
| X4 known flat share 0.40 | `rrect-md` | 10 | 6–42 | 0.0103 | -0.0026 | 0.00722 |
| carrier raster | `rrect-md` | 10 | 6–42 | 0.0112 | -0.0012 | 0.00722 |
| carrier svg | `rrect-md` | 10 | 6–42 | 0.0183 | -0.0139 | 0.00735 |
| carrier gradient | `rrect-md` | 10 | 6–42 | 0.0387 | -0.0287 | 0.00911 |
| X4 known ramp (0.30 -> 0.90 over 40 CSS px) | `rrect-lg` | 18 | 6–74 | 0.0195 | -0.0006 | 0.00633 |
| X4 known flat share 0.40 | `rrect-lg` | 18 | 6–74 | 0.0115 | -0.0034 | 0.00647 |
| carrier raster | `rrect-lg` | 18 | 6–74 | 0.0066 | +0.0009 | 0.00621 |
| carrier svg | `rrect-lg` | 18 | 6–74 | 0.1058 | -0.0568 | 0.00641 |
| carrier gradient | `rrect-lg` | 18 | 6–74 | 0.0596 | -0.0335 | 0.02184 |

The first two rows of each cell are contract X4: the instrument reads a page whose k(u) the analysis
knows and the profile does not — a straight ramp from 0.30 at the contour to 0.90 at 40 CSS px, and
a flat share of 0.40 — and returns it to **0.0083 / 0.0195 (the ramp)** and **0.0103 / 0.0115 (the
flat share)** in every validated window. That is the same order as W13's own synthetic recovery
(0.003 flat, 0.007 ramped) and well inside the ±0.05 X4 asks for, so the carrier rows below it are
readings and not artefacts.

**The raster carrier is the only one that meets ±0.05 on both cells** (max 0.0112 and 0.0066), and
it is the only one whose bias is not systematic (mean −0.0012 and +0.0009 against the SVG's −0.0139
and −0.0568 and the gradient's −0.0287 and −0.0335). Both approximate carriers read **low**, which
is the direction the alpha reading in §2.1 predicts: an erf that has not reached its plateau and a
product of alphas both undershoot the ramp.

**Recommendation: carrier (c), the raster mask.** It is exact to the mask channel's own 8 bits, its
corners are exact, it costs one small canvas per size change (§5's cost table finds no measurable
frame cost for it), and it is the only carrier whose error is a quantisation rather than a shape.

## 3. The second scale (charter G0 (c))

The two layers at device-pixel widths through dpr 2 — sharp σ `blurSigma / dpr` = 0.625 CSS px,
heavy σ `blurSigma · scatterGainAt(span, dpr) / dpr` = 3.000 / 3.000 / 3.000 / 3.332 / 4.122 CSS px,
the share the tier's own area-mean projection of the renderer's ramp at dpr 2 (0.601 / 0.647 / 0.871
/ 0.896 / 0.913) — projected onto one Gaussian by matching the mixture's second moment,
σ_eq = √((1−k)·σ_s² + k·σ_h²), beside §5.69 §4's four columns and beside the **measured** best single
σ of the 2x capture itself:

| cell | the tier draws today (§5.70 §5) | the reference's ceiling (§5.69 §4) | the reference's own mix and widths (§5.69 §4) | **this form, moment-matched** | **this form, the capture's own best single σ** |
| --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 3.79 | 3.00 | 2.91 | **2.36** | **2.50** |
| `capsule-button` | 3.97 | 2.50 | 2.82 | **2.44** | **2.35** |
| `rrect-md` | 5.53 | 4.00 | 3.64 | **2.81** | **2.80** |
| `rrect-ml` | 6.09 | 5.00 | 4.19 | **3.16** | **3.00** |
| `rrect-lg` | 7.04 | 5.00 | 5.01 | **3.94** | **3.65** |

The arithmetic and the capture agree to 0.14–0.29 CSS px, so the projection is not a modelling
choice. Against the acceptance ("within 0.8 CSS px of §5.69 §4's fourth column: 2.91 / 2.82 / 3.64 /
4.19 / 5.01") the form lands **−0.55 / −0.38 / −0.84 / −1.03 / −1.07**: inside 0.8 on the two thin
spans and outside it on the three thick ones, and outside on the same side on all five.

**This contradicts the charter's Purpose, item 2**, which predicts that "a tier that draws two layers
at device-pixel widths through the live ratio, with the heavy share as the GPU tier computes it, is
predicted to land there with no term of its own". It lands much closer than today's form — the error
falls from +0.88 / +1.15 / +1.89 / +1.90 / +2.03 to −0.55 / −0.38 / −0.84 / −1.03 / −1.07 — but it
lands **narrow**, not on. The mechanism is visible in the numbers: the reference's own 2x heavy
widths are 4.00 / 3.75 / 4.00 / 4.50 / 5.50 CSS px (§5.69 §1's bounded fits in device px, halved)
where this form's are 3.00 / 3.00 / 3.00 / 3.33 / 4.12, so the tier's heavy component is 0.4–1.4 CSS
px narrower than the reference's at every span, and the moment match carries that straight through.
That is a statement about the **GPU tier's own 2x gain**, not about this tier: the CSS tier draws
`scatterGainAt` and nothing of its own, and closing the last CSS pixel would mean moving a fitted
renderer constant, which this wave's binding rules forbid.

None of this bears on the RMS: §1.3's 2x reference-filter row lands on the analytic GPU law within
0.0008 on every span, so the form reproduces *the law it was given* at the second scale essentially
perfectly. The 0.4–1.4 CSS px is the law's own distance from the reference at 2x, restated in this
tier's units.

## 4. The lift (charter G0 (d))

**The charter's advisory form cannot be built, and the reason is not a defect.** Over a flat
`#3a5a80`-class ground (encoded 0.50196) with a ring whose `backdrop-filter` is
`brightness(1.5)` — so the filtered backdrop is exactly 0.75294 and every prediction is arithmetic:

| `mix-blend-mode` on the ring | ring `opacity` | measured | `normal` predicts | `plus-lighter` predicts | `screen` predicts |
| --- | --- | --- | --- | --- | --- |
| `plus-lighter` | 0.4 | 0.60392 | **0.60235** | 0.80314 | 0.65196 |
| `plus-lighter` | 1.0 | 0.75294 | **0.75294** | 1.00000 | 0.87696 |
| `normal` | 0.4 | 0.60392 | **0.60235** | 0.80314 | 0.65196 |
| `normal` | 1.0 | 0.75294 | **0.75294** | 1.00000 | 0.87696 |
| `screen` | 0.4 | 0.60392 | **0.60235** | 0.80314 | 0.65196 |
| `screen` | 1.0 | 0.75294 | **0.75294** | 1.00000 | 0.87696 |

All three blend modes render the `normal` result, identically, to within one code value (0.60392
against 0.60235 is 0.4/255, the ring's own antialiasing inside the sampled band). **A blend mode does
not reach a `backdrop-filter`'s output**: it blends the element's own *content* with the backdrop,
and an empty ring has no content, so `plus-lighter` on a filtered ring is `normal` on a filtered
ring. This is the spec's composition order rather than a Chromium quirk, which is why it is reported
as a form that does not exist rather than as a defect.

The obvious repair — put the filter on a child and the blend on its parent, so the filter's output
becomes the parent's content — fails on the other side:

| form | ring `opacity` | measured | the bare ground | `plus-lighter` of the filtered ring |
| --- | --- | --- | --- | --- |
| filtered child inside a `plus-lighter` parent | 0.4 | **0.50196** | 0.50196 | 0.80314 |
| filtered child inside a `plus-lighter` parent | 1.0 | **0.50196** | 0.50196 | 1.00000 |
| filtered child inside a `normal` parent | 1.0 | 0.75294 | 0.50196 | — |

A `mix-blend-mode` ancestor **is** a backdrop root, so the child's `backdrop-filter` is inert and the
ring renders the bare ground exactly. The control on the third row is the proof that nothing else
broke: the same construction with `mix-blend-mode: normal` at opacity 1 renders the filtered value.

So on this tier the lift is only expressible if the blurred backdrop can be made the element's own
**content** — which means copying the backdrop into a layer, which is a proxy, which is the one
thing this tier does not build and the reason `probe-failed` may demote to it.

Two supporting readings:

- **The ring does not re-root the backdrop for a body beneath it.** With the ring painted after the
  host, the two-layer body's interior is byte-identical to the body drawn alone (RMS 0.000000, max
  0.000000 over the interior box). With the ring inserted *before* the host — so that the body's
  filters sample the ring's own output — the interior moves by RMS 0.000185 and at most 0.003922
  encoded, one code value on the pixels where the ring's mask still has weight, and with the ring
  wrapped in a blended parent it is byte-identical again (RMS 0.000000), which it must be because
  the wrapped ring paints nothing. So the charter's Risk "the lift re-roots the backdrop" does not
  fire for a sibling; it fires for an ancestor, and then absolutely.
- **What the lift is worth on the canonical bed.** Encoded means over the shadow ring
  (0 to 25 CSS px outside the silhouette) on the committed captures:

| cell | GPU − CSS | native − CSS | native − GPU |
| --- | --- | --- | --- |
| `photo__rrect-md__rest` | −0.0171 | −0.0112 | +0.0059 |
| `light-solid__rrect-md__rest` | −0.0025 | −0.0000 | +0.0025 |
| `light-solid__rrect-ml__rest` | +0.0024 | +0.0069 | +0.0045 |

The CSS tier is *lighter* than the GPU tier in the ring on `photo__rrect-md` by 0.0171 encoded and
*lighter* than the native by 0.0112 — so on this cell W14's derived alpha `α′ = α − L/B` is not
under-darkening for want of the lift; it over-corrects by about 0.011 encoded, and adding light
would move it the wrong way. On the thick solids the three tiers agree to 0.007 encoded. **The lift
is not the CSS tier's largest ring error on the bed as it stands**, which is worth saying before a
wave spends an element on it.

**Recommendation for Decision Log 1 q3: the lift is not in this wave.** Not because it is expensive
— because CSS has no construction for it that keeps the backdrop, and the number it would buy is
smaller than the number W14's own conversion is already off by on the one cell that has a lift.

## 5. The cost (charter G0 (e))

**What the first attempt measured, and why it is recorded.** Launched with
`--disable-gpu-vsync --disable-frame-rate-limit`, every configuration — no filter, one blur, two
blurs, two blurs and a mask, 0 to 320 surfaces, both scales — returned a median
`requestAnimationFrame` interval of 0.1–0.3 ms. That reading is empty, and the reason is worth
carrying: rasterisation is the compositor's work and the main thread is idle, so an uncapped rAF
interval measures the main thread's spin rate and nothing about the frame. The measurement below
therefore keeps **vsync on** and reads the surface count at which the display's own cadence breaks,
which is a number a budget can be set from. The machine's cadence with no filter at all is a median
of 11.1–13.4 ms over the same counts and both scales, so a configuration above about 14 ms is
dropping frames.

Synthetic page, 1280 × 800 viewport, `n` surfaces of 160 × 96 CSS px in a grid, a checkerboard
backdrop translated every frame so that every frame really re-rasterises (median frame interval in
ms; every surface is inside the viewport up to n = 40, and above that the grid overflows and the
count over-states the work):

| surfaces (160 x 96 CSS px) | filtered device px per frame @1x / @2x | one blur @1x | two @1x | two + mask @1x | one blur @2x | two @2x | two + mask @2x |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | 0.31 M / 1.23 M | 11.3 | 11.8 | 10.5 | 10.9 | 19.5 | 10.8 |
| 24 | 0.37 M / 1.47 M | 10.7 | 12.4 | 10.5 | 14.8 | 10.3 | 10.4 |
| 28 | 0.43 M / 1.72 M | 10.4 | 10.6 | 11.0 | 11.7 | 15.1 | 10.6 |
| 32 | 0.49 M / 1.97 M | 10.8 | 11.9 | 11.5 | 10.9 | 11.0 | 12.4 |
| 36 | 0.55 M / 2.21 M | 10.7 | 14.1 | 14.7 | 10.5 | 12.0 | 14.3 |
| 40 | 0.61 M / 2.46 M | 10.9 | 16.7 | 18.5 | 10.6 | 15.2 | 19.0 |
| 48 | 0.74 M / 2.95 M | 16.7 | 21.9 | 21.9 | 10.2 | 20.2 | 20.9 |
| 80 | 1.23 M / 4.92 M | 11.0 | 26.9 | 27.0 | 10.6 | 22.7 | 26.8 |
| 160 | 2.46 M / 9.83 M | 10.9 | 27.2 | 27.2 | 10.5 | 23.7 | 27.2 |
| 320 | 4.92 M / 19.66 M | 10.6 | 26.9 | 27.2 | 10.9 | 26.7 | 26.8 |

Every cell is a single run and the cadence jitters: two readings below 32 surfaces sit well off the
trend (`two` at dpr 2, n = 20, 19.5 ms; `one` at dpr 1, n = 48, 16.7 ms) and neither reproduces at
its neighbours. Read as a trend rather than cell by cell, the signal is unambiguous: **one
`backdrop-filter` per surface never leaves the cadence at any count measured, and two leave it
monotonically from 32 surfaces upward at both scales** — 0.49–0.61 M filtered device px per frame at
dpr 1 and 1.97–2.46 M at dpr 2 — saturating at about 27 ms (≈ 37 fps) from 80 surfaces up. **The
mask is free**: `two` and `two + mask` are within the noise of each other at every count and both
scales, so the raster carrier costs nothing per frame once its canvas exists.

A single large surface costs nothing measurable at either shape, including well past the
software-raster area limit the conformance table carries:

| --- | --- | --- | --- | --- |
| 320 x 144 (the demo's largest) | 11.0 ms | 11.5 ms | 11.6 ms | 10.9 ms |
| 1600 x 900 (2.88 M device px x4) | 11.8 ms | 12.5 ms | 11.6 ms | 12.6 ms |

| demo page (CSS tier forced) | filtered elements | largest | as shipped | two layers | two + mask |
The 1600 × 900 case at dpr 2 is 5.76 M device px on a single element and 11.5 M across the two
layers, three to six times `CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT`, and the filter neither dropped nor
cost a frame — which is the expected answer on a real GPU and says nothing about the software
rasteriser. **The charter's Risk "two filtered elements each under the software-raster area limit
cost something jointly" is not answered here**: answering it needs the headless shell's software
path, which this spike is forbidden to capture on, and it stays open.

The demo, with `?renderer=css` forcing the tier, each page as shipped and then with every filtered
host converted in place to the two-layer shape (the site and the laws pages invalidate by scrolling;
the playground does not scroll, so an injected moving strip supplies the invalidation and the run
records which was used):

| `demo site` @1x | 3 | 288 x 112 | 11.9 ms | 11.0 ms | 11.6 ms |
| `demo site` @2x | 3 | 288 x 112 | 19.0 ms | 11.9 ms | 12.4 ms |
| `demo laws` @1x | 2 | 288 x 112 | 10.9 ms | 11.8 ms | 11.9 ms |
| `demo laws` @2x | 2 | 288 x 112 | 11.6 ms | 12.2 ms | 13.4 ms |
| `demo playground` @1x | 8 | 320 x 144 | 11.8 ms | 11.4 ms | 12.8 ms |
| `demo playground` @2x | 8 | 320 x 144 | 11.4 ms | 11.3 ms | 12.0 ms |

invalidation: {'demo site as shipped (one blur)': 'scroll', 'demo site two layers': 'scroll', 'demo site two layers + mask': 'scroll', 'demo laws as shipped (one blur)': 'scroll', 'demo laws two layers': 'scroll', 'demo laws two layers + mask': 'scroll', 'demo playground as shipped (one blur)': 'injected moving strip', 'demo playground two layers': 'injected moving strip', 'demo playground two layers + mask': 'injected moving strip'}
**The demo's densest CSS-tier page is `/playground/` with eight filtered elements**, the largest
320 × 144 CSS px; the site has three and the laws page two. At that density the shape is free: every
reading is at the cadence and the spread between "as shipped" and "two layers + mask" is 0.6–1.0 ms
at 1x and 0.6–1.8 ms at 2x, inside the run-to-run noise. The one reading above the cadence — the
site at dpr 2 as shipped, 19.0 ms — is *today's* one-blur form and did not reproduce in the
two-layer runs, so it is noise rather than a baseline.

**The parent's recommendation for Decision Log 1 q1 (the cost budget).** The number to hold is not a
surface count but a filtered area: two layers stay inside a 120 Hz cadence up to about **0.5 M
filtered device pixels per frame** on this machine and break by 0.6 M, where one layer holds past
4.9 M. A budget of *"the two-layer form may be drawn while a root's total measured surface area is
under 0.4 M device px per frame, and a root above it collapses the heavy layer into the single mixed
σ"* is met by every page vitrea ships (the demo's densest is 0.16 M at dpr 2) with a 2.5× margin,
and it makes the fallback a declared, measured degradation. The collapse is cheap to implement
because it is exactly today's form. Whether that threshold, a surface count, or no cap at all is
wanted is the user's call.

### 5.1 Addendum — the linear-light form's cost (2026-09-04, after G0's first close)

§1.3's `url(#f)` / `color-interpolation-filters="linearRGB"` form is the only one that reaches the
reference's body, so the budget has to be set on *its* cost and not on `blur()`'s. The same
saturation sweep, the same page, the same counts and scales and the same medians, with the two
layers drawn as reference filters carrying the same two widths and the same `saturate(1.5)` (as an
`feColorMatrix`, so the two columns differ in the operator's colour space and in nothing else) —
one filter pair for the whole document, so the reading is the cost of the FORM and not of a filter
per element. The `blur()` columns are §5's, repeated beside rather than replaced; nothing above is
rewritten. The form was confirmed to paint before the sweep ran: at four surfaces it differs from
the unfiltered page by a mean 0.257 of full scale and from the `blur()` form by 0.132, which is the
colour-space difference §1.3 measures.

| surfaces | filtered device px per frame @1x / @2x | one @1x | one-ref @1x | two @1x | two-ref @1x | two-mask @1x | two-ref-mask @1x | one @2x | one-ref @2x | two @2x | two-ref @2x | two-mask @2x | two-ref-mask @2x |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | 0.31 M / 1.23 M | 11.3 | 11.8 | 11.8 | 10.5 | 10.5 | 10.9 | 10.9 | 11.3 | 19.5 | 10.6 | 10.8 | 10.8 |
| 24 | 0.37 M / 1.47 M | 10.7 | 11.0 | 12.4 | 10.4 | 10.5 | 10.7 | 14.8 | 11.7 | 10.3 | 10.5 | 10.4 | 10.3 |
| 28 | 0.43 M / 1.72 M | 10.4 | 11.2 | 10.6 | 10.9 | 11.0 | 10.6 | 11.7 | 10.9 | 15.1 | 10.8 | 10.6 | 11.0 |
| 32 | 0.49 M / 1.97 M | 10.8 | 12.4 | 11.9 | 12.5 | 11.5 | 12.8 | 10.9 | 10.7 | 11.0 | 13.2 | 12.4 | 13.5 |
| 36 | 0.55 M / 2.21 M | 10.7 | 11.3 | 14.1 | 15.5 | 14.7 | 16.6 | 10.5 | 10.4 | 12.0 | 15.7 | 14.3 | 20.7 |
| 40 | 0.61 M / 2.46 M | 10.9 | 10.4 | 16.7 | 19.4 | 18.5 | 19.5 | 10.6 | 10.5 | 15.2 | 19.7 | 19.0 | 19.4 |
| 48 | 0.74 M / 2.95 M | 16.7 | 10.7 | 21.9 | 24.9 | 21.9 | 23.8 | 10.2 | 10.4 | 20.2 | 23.7 | 20.9 | 24.7 |
| 80 | 1.23 M / 4.92 M | 11.0 | 11.1 | 26.9 | 22.8 | 27.0 | 27.2 | 10.6 | 10.4 | 22.7 | 27.5 | 26.8 | 28.5 |
| 160 | 2.46 M / 9.83 M | 10.9 | 10.8 | 27.2 | 22.7 | 27.2 | 27.8 | 10.5 | 10.9 | 23.7 | 27.5 | 27.2 | 27.7 |
| 320 | 4.92 M / 19.66 M | 10.6 | 10.5 | 26.9 | 27.1 | 27.2 | 23.0 | 10.9 | 10.7 | 26.7 | 27.7 | 26.8 | 27.7 |

**The knee does not move.** `one-ref` never leaves the cadence at any count measured (10.4–12.4 ms
over 20 to 320 surfaces at both scales), exactly as `one` does not. `two-ref` and `two-ref-mask`
leave it between 32 and 36 surfaces at both scales — the same 0.49–0.55 M filtered device px per
frame at dpr 1 and 1.97–2.21 M at dpr 2 that `blur()` breaks at — and saturate at the same
23–28 ms from 80 surfaces up. Where the two forms differ at all it is on the far side of the knee
and at the second scale: at n = 36 and 48 at dpr 2 the reference filter reads 15.7 / 23.7 ms against
`blur()`'s 12.0 / 20.2, and with the mask 20.7 / 24.7. So the linear-light form costs the same up to
the knee and a little more past it, which is the region a budget exists to keep a page out of.

The demo, converted the same way (one reference-filter pair injected per document):

| page | filtered elements | largest | as shipped (one blur) | two layers | two layers + mask | two ref layers | two ref layers + mask |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `demo site` @1x | 3 | 288 × 112 | 11.9 ms | 11.0 ms | 11.6 ms | 11.5 ms | 11.4 ms |
| `demo site` @2x | 3 | 288 × 112 | 19.0 ms | 11.9 ms | 12.4 ms | 11.5 ms | 16.5 ms |
| `demo laws` @1x | 2 | 288 × 112 | 10.9 ms | 11.8 ms | 11.9 ms | 11.5 ms | 11.3 ms |
| `demo laws` @2x | 2 | 288 × 112 | 11.6 ms | 12.2 ms | 13.4 ms | 11.5 ms | 17.2 ms |
| `demo playground` @1x | 8 | 320 × 144 | 11.8 ms | 11.4 ms | 12.8 ms | 11.1 ms | 11.0 ms |
| `demo playground` @2x | 8 | 320 × 144 | 11.4 ms | 11.3 ms | 12.0 ms | 11.0 ms | 11.2 ms |

The playground — the densest CSS-tier page, eight filtered elements, 0.16 M filtered device px at
dpr 2 — is at the cadence in every shape including the reference filter with the mask (11.0–12.8 ms).
Two readings sit above it, the site and the laws page at dpr 2 with the reference filter and the mask
(16.5 and 17.2 ms) on **three and two** filtered elements, which is fewer elements and less area than
the playground that reads 11.2 ms in the same shape. They are single runs and internally
inconsistent with the denser page, so they are recorded as measured and read as jitter rather than
as a cost of the form.

**The area rule stands.** The recommendation in §5 — allow the two-layer form while a root's total
measured surface area is under about 0.4 M device px per frame, and collapse to today's single mixed
σ above it — was derived from the `blur()` knee and is unchanged by this form, because the knee is
unchanged. The demo's densest page clears it by a factor of 2.5 in either form. The one refinement
the addendum earns is that the budget should be stated on *filtered area*, not on a surface count or
a form: `one`, `one-ref`, `two`, `two-ref`, `two-mask` and `two-ref-mask` all break at the same
filtered area for a given number of layers, and the layer count is the only multiplier.

## 6. The redistribution list (charter G0 (f))

What `cssTierDeclarations` writes on the author's host today (`packages/platform-web/src/css-tier.ts`,
applied by `root.ts` around line 1602), and where each goes under a model with three created
children. Two CSS facts decide most of the list and both are confirmed by the captures above: a
negative-`z-index` child of a stacking context paints **above** that element's own background and
border and **below** its in-flow content (§1.4's ring is the host's own tint being blurred by the
layers, which is that order observed); and an absolutely positioned child's containing block is the
host's **padding** box, so a child at `inset: 0` does not cover the host's border area.

The model this list assumes: the host keeps `position: relative` and `isolation: isolate` and gains
three children, each `position: absolute`, `inset: calc(-1 * <borderWidth>)` so its border box is the
host's border box, `border-radius: inherit`, `pointer-events: none`, `aria-hidden="true"`, no tab
stop — **L1** the sharp `backdrop-filter`, **L2** the heavy one drawn after it (its weight an
`opacity` or a raster `mask-image`), **L3** the tint, the press glow and the rim.

| property today, on the host | where it goes | why |
| --- | --- | --- |
| `border-radius` | **stays on the host** | the layers take `border-radius: inherit`, and it is the author's own geometry |
| `backdrop-filter` / `-webkit-backdrop-filter` | **L1 and L2** | a filtered parent makes a filtered child inert (§5.42 §5), so both layers must be children of a filter-free host |
| `background-color` (the tint) | **L3, above both filters** | beneath them the filters sample it and the contour reads 0.010–0.015 encoded dark over the first 4 CSS px (§1.4) |
| `background-image` (the press glow) | **L3**, on its own longhand as today | it is light added on top of the material; a filter below it must not blur it, and it must not be able to take the tint down |
| `border-style` / `border-width` | **stays on the host** | it is layout: the author's content box depends on it and no created layer may move it |
| `border-color` | **`transparent` on the host; the rim colour becomes an `inset box-shadow` on L3** | the host's border paints *below* the negative-`z` children and would be covered; an inset shadow follows `border-radius` exactly and needs no box-sizing arithmetic |
| `box-shadow` (the outer shadow) | **stays on the host** | it paints outside the border box, below the background, and the children — clipped to their own boxes — never cover it |
| `transition` | **splits**: `backdrop-filter` onto L1 and L2, `background-color` and the rim's `box-shadow` onto L3, the outer `box-shadow` stays on the host | a transition has to be declared on the element that carries the property |
| `--vitrea-tint`, `--vitrea-occlusion`, `--vitrea-border-color`, `--vitrea-foreground` | **stay on the host** | they are the public vocabulary an app styles against and the GPU tier writes the same names; the created layers are private |
| `--vitrea-blur` | **stays on the host, still the single-σ projection** | an app matching it with its own `blur()` must keep getting one number; the two per-layer σ belong in the readout and the capture cell, not in a token |
| the `glass: "none"` branch (forced colors) | **unchanged, and the layers are torn down** | it is a different surface, not a dimmer material; a tier that left the layers up would leave glass under system colours |

Three consequences to carry into G1, none of them decided here:

1. `css-tier.ts`'s doctrine narrows from "in place, nothing layered" to "**no proxy**", exactly as
   the charter says. The filter still reads what is behind the host, so `probe-failed` may still
   demote here — and §4's finding is the sharp edge of that: the moment the tier needs a *copy* of
   the backdrop (the lift) it stops being demotable-to, which is why the lift is not in this wave.
2. The rim's move from `border-color` to an inset `box-shadow` on L3 is the only change an author can
   observe in the computed style of their own element, and the platform-web e2e pins that read the
   host's `backdropFilter` (`proxies`, `probe`, `webgpu-tier`, `css-tier-pixels`) all have to be
   re-pointed at L1 with the reason.
3. Nothing in the list makes a created layer focusable, hit-testable or announced, and none of them
   is a proxy, so `registration.spec`, `hit-testing.spec`, `focus.spec` and `proxies.spec` should
   hold unchanged.

## 7. The other engines (charter G0 (g), contract X9)

**Section H has landed on `spikes/s1-proxy-topology/pages/manual-check.html`**, in the page's own
style: four amber questions over the page's existing flat `#3a5a80` ground with
`brightness(1.25)` filters, so every answer is a swatch match and not a judgement, and every swatch
is computed in the page from `FLAT` rather than written down. H1 sibling `opacity` on a filtered
layer; H2 `mask-image` on a filtered layer; H3 `plus-lighter` on a filtered layer; H4 a filtered
child inside a `plus-lighter` parent. Each question names Chromium's own measured answer, so a
divergence is visible rather than inferred. The page's "Reporting back" list now asks for H1–H4.

Section H's four tiles were rendered in the same Chromium the rest of this spike used and read at
their band centres, and each matches the swatch the page names for it to the exact code value:
H1 `rgb(80, 124, 176)` = BOTH, H2 `rgb(80, 124, 176)` = BOTH, H3 `rgb(64, 99, 141)` = NOT ADDED,
H4 `rgb(58, 90, 128)` = INERT. So the swatches are arithmetic a human can trust, and Chromium's
own column of answers on the page is measured rather than asserted.

**The conformance-table fields section H would move** (named here, not changed —
`packages/platform-web/src/probe/conformance-table.ts` is untouched by G0):

- three new fields on `EngineConformanceRow`, all `"yes" | "no" | "unverified"` and all
  `"unverified"` on every non-Chromium row so the runtime fails closed:
  `siblingOpacityOnFilteredLayer` (H1), `maskOnFilteredLayer` (H2) and
  `blendReachesFilteredBackdrop` (H3 — Chromium's answer is **`"no"`**, and it is a fact about the
  composition order rather than a defect, so it belongs on this axis and not in `engine-defects.ts`);
- `backdropRootTriggers`, which H4 reads directly: a `mix-blend-mode` ancestor re-roots in Chromium
  (measured, §4), which is the normative membership the Chromium and WebKit 18.6 rows already claim,
  and H4 is the observation that would let a Gecko row claim it too;
- `referenceFilterInBackdrop`, which §1.3 turns from a seam into a **fidelity dependency**: if G1
  takes the linear-light form, an engine whose row says `false` cannot draw the tier's body in the
  right colour space and gets the `blur()` form with its measured 2.4–2.8× residual. That is a
  policy the table can already express and the runtime already reads.

**Recommendation for Decision Log 1 q2 (the unverified-engine policy).** The charter's recommendation
— the two layers with one `opacity` — is measured correct as far as it goes, and G0 strengthens it:
sibling `opacity` on `backdrop-filter` is ordinary CSS, `mask-image` on a filtered layer is now
measured to compose in Chromium, and the failure mode of a mask an engine ignores is a *flat mix*
(the layer at alpha 1), which is a wrong-looking surface, not a broken one. So: **on an engine whose
`maskOnFilteredLayer` row is `"unverified"`, draw the two layers with the heavy share as one
`opacity` at the ramp's area mean** — the body's two components without the band — and gate the
raster mask on the labeled pass. The `blur()`-versus-reference-filter choice rides on
`referenceFilterInBackdrop`, which the table already carries per engine.

## 8. What contradicts the charter, and what the parent has to decide

1. **The acceptance's body term is not reachable with `blur()`, at any σ or share.** The charter's
   parent-level acceptance asks for the tier's RMS within 1.5× the GPU law's on the probe bed. Two
   `blur()` layers reach 0.91× / 1.75× / 2.89× / 2.85× / 2.39×, and the residual is the encoded
   space — the capture matches its own encoded-space forward model to 0.0024–0.0049 (§1.2). Two
   `url(#f)` layers with `color-interpolation-filters="linearRGB"` reach 1.17× / 1.10× / 1.50× /
   1.41× / 1.20× at 1x and 0.97–1.03× at 2x (§1.3). **The acceptance is met only by a form the
   charter does not name, and that form is Chromium-only.**
2. **The second scale lands narrow, not on.** The two layers at device-pixel widths project to
   2.36 / 2.44 / 2.81 / 3.16 / 3.94 CSS px against §5.69 §4's 2.91 / 2.82 / 3.64 / 4.19 / 5.01 —
   inside 0.8 on two spans, outside on three, and the cause is that the renderer's own 2x heavy
   width is 0.4–1.4 CSS px under the reference's (§3). The charter's Purpose item 2 predicted it
   would "land there with no term of its own"; it lands much closer than today and not there.
3. **The lift's advisory form does not exist.** `mix-blend-mode` does not reach a
   `backdrop-filter`'s output, and a blended ancestor re-roots the backdrop, so the additive ring is
   unbuildable without a backdrop copy (§4). The charter's Risk anticipated re-rooting; the measured
   failure is one step earlier than that.
4. **The mask question, which everything about the ramp depended on, answers yes** (§0), and the
   exact raster carrier is free per frame (§5) and exact to the mask channel's own 8 bits (§2).

Open, and named rather than closed: the software rasteriser's joint area limit for two filtered
elements (§5); whether a linear-light reference filter changes the tier's cost (not measured — §5's
cost runs all use `blur()`); and the `accessibility` folds on the two-layer form, which are G1's.
