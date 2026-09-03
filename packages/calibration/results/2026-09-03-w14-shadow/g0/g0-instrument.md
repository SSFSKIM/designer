# W14 G0 — the instrument, and its validation on vitrea's own shadow (X4)

The charter's first binding rule: before any reference number, the same code recovers vitrea's
landed W8 shadow from vitrea's own captures. This document is that validation, plus the three
things the validation itself measured — the space the composite lives in, the window the surface's
own edge occupies, and what a solid backdrop can and cannot identify.

Everything here is analysis of committed rasters. No constant under `packages/**/src`, no profile
document, no matrix and no spec was touched, and nothing was captured.

## 1. What the instrument does

For a cell — a native fixture, a vitrea capture or an analytic composite, all read the same way:

- the **declared component region** is the union of the rounded rects `scenes.json` declares, placed
  by `placeComponent`'s rule (centre on the canvas, then the shape's own offset). It is derived from
  the declaration and never from the image, which is claims §5.12's bounding rule and the reason a
  shadow-swallowing extractor cannot get into this measurement;
- `d` is the exact signed distance to that union in CSS px, positive outside;
- each exterior pixel is classified by the **normal of the nearest declared rect** — `below`,
  `above`, `left`, `right`, or `corner` when the nearest point lies on a corner arc. The corner
  class is kept and reported separately rather than folded into a side. A capsule has no flat left
  or right edge at all, so its `left` and `right` classes are legitimately empty and everything past
  its caps is `corner`;
- rings are 0–3, 3–6, 6–12, 12–24 and 24–48 CSS px, plus the 0–6 ring claims §5.60 §3 reported its
  lift on, so this instrument's readings and the ledger's can sit side by side without re-binning
  either;
- per side × ring the capture is fitted as **y = a·bg + c** by least squares against the backdrop
  raster the capture was taken over, and the plain occlusion ratio mean((bg − y)/bg) is recorded
  beside it over the pixels whose backdrop clears the shadow axis's own 0.05 floor;
- the fit is run in **both spaces** — see §2 — and every reference row carries three companions:
  vitrea's GPU capture, vitrea's CSS capture, and W8's own analytic composite over the same
  backdrop, all read by this same code.

Absence is said rather than smoothed over. On a solid backdrop the design matrix's two columns are
collinear: `a` and `c` are not separable, and the instrument reports `identifiable: false` with the
reason `flat-backdrop`, the ring's level and the ring's ratio instead of a fabricated pair. A ring
with fewer than 32 pixels is not fitted.

Code: `w14lib.py`; the validation is `g0_validate.py` and `parts/validation.json`.

## 2. The space the composite lives in, found while validating

The first pass of this instrument ran in linear luminance alone, as the charter's binding rule
specifies, and it read vitrea's own black multiply back as an amplitude of **0.271** where the
profile says 0.285 — a 5% shortfall, consistent across every ring, side, span and scale. That
shortfall was the instrument's, not the renderer's, and finding it is the reason X4 exists.

Both tiers paint a pure black layer at `outerShadowAlpha(0.285)` = 0.13045 and the composite lands
in the canvas's **encoded** space. Reading vitrea's white checkerboard squares as an encoded ratio
recovers that alpha exactly:

| cell | encoded-space alpha recovered | `outerShadowAlpha(0.285)` |
| --- | --- | --- |
| 1x `checkerboard__rrect-lg__rest` | 0.13018 | 0.13045 |
| 2x `checkerboard__rrect-lg__rest` | 0.13036 | 0.13045 |

What the linear-space reading got wrong is the decode, not the composite. The linear factor is
**not** (1 − α·F)^2.4: sRGB's decode carries the 0.055 offset, so the factor is
srgb_to_lin(e·(1 − α·F)) / srgb_to_lin(e) and depends on the backdrop's own encoded level `e`. The
fix is to predict the composite in the encoded domain and decode it, which needs no factor at all
(`w14lib.w8_predicted_capture`). With that correction the linear-light validation passes; the tables
below carry both spaces.

**Consequence for every table in `g0-shadow.md`.** Claims §5.60 §3's lift of +0.039 / +0.024 /
+0.014 / +0.004 was read in encoded Rec.709 luma. This instrument reproduces it there
(+0.0346 / +0.0250 / +0.0151 on `checkerboard__rrect-lg__rest` at 1x over the four sides, corners
excluded, and +0.0479 / +0.0382 / +0.0255 below the surface alone, which is the window §5.60 §3
describes). The **same lift in linear luminance is +0.0038 / +0.0030 / +0.0020** — ten times
smaller, because the lift sits on a black square where the transfer function is at its steepest.
Neither number is wrong; they are the same measurement in two spaces, and every reading in this
wave says which. The charter binds the linear reading; the encoded reading is the one that connects
to §5.60 and to what either tier would have to composite.

## 3. The validation (X4)

Five cells at both scales, GPU tier, `parts/validation.json`. Each ring's fitted (a, c) is compared
with two predictions of the same landed shadow, each **projected onto that ring's own affine fit**
so the comparison carries no ring-width caveat:

- `exact` — the composite the GPU tier actually produces: black at `outerShadowAlpha(0.285)·F` in
  the encoded domain, rounded to 8 bits, decoded;
- `charter` — the charter's stated form, the linear-light multiply 1 − 0.285·F.

F is computed from the geometry: the component's own silhouette translated down 7.95, outset 3.1,
through `outerShadowFalloff` at σ 15.55 — the shader's own construction, evaluated analytically.

Worst departure over every ring and side of a cell, linear space, with the first 1.5 device px of
exterior dropped (see §4):

| cell | max abs Δa vs `exact` | max abs Δc vs `exact` | max abs Δa vs `charter` |
| --- | --- | --- | --- |
| 1x `checkerboard__rrect-lg__rest` | 0.0015 | 0.0000 | 0.0043 |
| 1x `checkerboard__rrect-md__rest` | 0.0015 | 0.0000 | 0.0042 |
| 1x `photo__rrect-md__rest` | 0.0056 | 0.0017 | 0.0170 |
| 2x `checkerboard__rrect-lg__rest` | 0.0013 | 0.0000 | 0.0043 |
| 2x `checkerboard__rrect-md__rest` | 0.0014 | 0.0000 | 0.0043 |
| 2x `photo__rrect-md__rest` | 0.0043 | 0.0013 | 0.0152 |
| 1x, 2x `checkerboard__capsule-button__rest` | 0.0016 on the four sides; **0.30 on the corner class** | 0.0000 / **0.27** | — |
| 1x, 2x `light-solid__capsule-button__rest` | not identifiable — flat backdrop, §5 | | |

**The verdict: X4 passes on every flat side of every cell, at ±0.0016 in `a` and ±0.0000 in `c`,
and fails on one class — the capsule's corner sector — for a reason that is a measurement of vitrea
rather than of the instrument (§4).** The charter's stated model, the linear multiply 1 − 0.285·F,
sits within 0.0043 of the fit on the checkerboard and 0.017 on `photo`; the exact encoded composite
sits within 0.0016 and 0.0056. Both are recorded; the exact form is the one the reference tables
are read against, and the charter's ±0.005 tolerance holds for it everywhere except the corner
class.

The per-ring detail on `checkerboard__rrect-lg__rest` at 1x, linear space, Δ against `exact`:

| side | 0–3 | 3–6 | 6–12 | 12–24 |
| --- | --- | --- | --- | --- |
| below | a 0.7992 (+0.0001), c +0.0000 | 0.8149 (+0.0000), +0.0000 | 0.8431 (−0.0011), +0.0000 | 0.8912 (+0.0001), +0.0000 |
| above | 0.9049 (+0.0003), −0.0000 | 0.9216 (+0.0000), −0.0000 | 0.9459 (+0.0015), −0.0000 | 0.9713 (−0.0011), +0.0000 |
| left | 0.8514 (+0.0004), +0.0000 | 0.8687 (+0.0001), −0.0000 | 0.8981 (+0.0001), +0.0000 | 0.9411 (+0.0002), +0.0000 |
| right | 0.8513 (+0.0003), −0.0000 | 0.8696 (+0.0006), +0.0000 | 0.8986 (+0.0008), +0.0000 | 0.9412 (+0.0003), +0.0000 |
| corner | 0.8566 (+0.0011), −0.0000 | 0.8715 (+0.0010), +0.0000 | 0.9004 (+0.0010), −0.0000 | 0.9459 (+0.0006), +0.0000 |

`c` recovers as 0.0000 to four decimals on **every** ring and side of every checkerboard cell, at
both scales. That is the null the reference's lift is read against, and it is exact rather than
approximately zero because a black multiply cannot lift a black square by construction.

## 4. What the instrument measured about vitrea while validating: the own-edge window

The innermost ring contains the surface's own antialiased boundary, which is the component and not
its shadow. On a checkerboard the black squares make that separable with no model at all: the lift
never exceeds 0.055 encoded anywhere on this bed, so a black pixel outside the contour reading above
0.02 is the **body**. Walking outward until no black pixel exceeds 0.02 gives, per source, how far
each renderer's own body reaches past the geometry the scene declares:

| cell | Apple | vitrea GPU | vitrea CSS | where the CSS/GPU spill sits |
| --- | --- | --- | --- | --- |
| 1x `capsule-button` | 1.0 | **4.0** | 3.5 | corner (the caps); CSS also below |
| 1x `rrect-sm` | 1.0 | 0.5 | 3.0 | below, right, corner |
| 1x `rrect-md` | 0.0 | 1.0 | 3.5 | below, right, corner |
| 1x `rrect-lg` | 0.0 | 0.5 | 3.5 | below, right, corner |
| 2x `capsule-button` | 0.5 | **3.5** | 3.0 | corner (the caps); CSS also below |
| 2x `rrect-sm` | 0.5 | 0.5 | 3.0 | below, right, corner |
| 2x `rrect-md` | 0.0 | 0.5 | 3.0 | below, right, corner |
| 2x `rrect-lg` | 0.0 | 0.5 | 3.5 | below, right, corner |

Two readings, both outside this wave's own subject and both recorded because nothing else in the
harness can see them:

- **The GPU tier's capsule over-fills its declared contour by 3.5–4 CSS px at the caps**, where the
  reference over-fills by 1 or less and where vitrea's own rounded rectangles over-fill by 0.5–1.
  This is the same defect the X4 corner-class residual reports from the other side: on the capsule's
  corner sector the fitted `a` sits 0.008–0.011 below the model at rings 3–6, 6–12 and 12–24, i.e.
  slightly more darkening than W8's falloff predicts, and 0.30 below it at ring 0–3, where the body
  itself is in the window.
- **The CSS tier over-fills by 3–3.5 CSS px on `below`, `right` and `corner` on every component at
  both scales** — a displacement toward the bottom right rather than a symmetric halo.

Claims §5.12 states that the shape axis is bounded to the declared region and therefore **cannot**
measure over-fill: "a surface drawn larger than its declaration is clipped to the declaration and
reads as a match". These two rows are that blind spot, measured from outside for the first time.
They belong to the shape axis and the CSS tier, not to the shadow, and they go to the tech-debt
tracker and to this wave's Deferred list rather than into W14's model.

Operationally the instrument takes the guard from this measurement rather than assuming one:
`g0_geometry.py` walks the guard per cell and per source (floor 2.0 CSS px, the antialiased boundary
every source has; ceiling 6.0), and `g0_validate.py` reports both the plain ring and a 1.5-device-px
guard so the reader can see what the guard costs.

A second window rule comes from the same place. A shadow cannot brighten its surround, so an
exterior pixel reading more than 2% above its own backdrop is not shadow. Native and GPU captures
have none past the guard — their ratio maxes at 1.009 — while the CSS captures have a handful whose
ratio runs to 3.4, and one such pixel has enough leverage to pull a least-squares amplitude to
zero, which is exactly what the first pass of `g0_thin.py` reported for the CSS tier over `photo`
(0.000 against the GPU tier's 0.130). They are dropped and counted, never winsorised.

## 5. What a solid backdrop cannot identify, said plainly

On `light-solid` the backdrop is one constant, so `a·bg + c` has one degree of freedom and the fit
reports `identifiable: false`. What is identifiable is the ring's level, and the instrument recovers
vitrea's own composite there to ±0.0034 in linear luminance:

`light-solid__capsule-button__rest`, vitrea GPU, 1x, linear luminance, backdrop 0.8910:

| side | ring | measured level | `exact` model | `charter` model |
| --- | --- | --- | --- | --- |
| below | 0–3 | 0.7110 | 0.7142 | 0.7083 |
| below | 3–6 | 0.7258 | 0.7256 | 0.7226 |
| below | 6–12 | 0.7520 | 0.7530 | 0.7508 |
| below | 12–24 | 0.8063 | 0.8060 | 0.8068 |
| below | 24–48 | 0.8731 | 0.8724 | 0.8728 |
| above | 0–3 | 0.8093 | 0.8059 | 0.8072 |
| above | 24–48 | 0.8892 | 0.8892 | 0.8890 |
| corner | 0–3 | 0.8493 | 0.7639 | 0.7628 | 

2x reads the same to ±0.002 on every row. The corner row at 0–3 is §4's capsule over-fill again —
the body's own light raising the ring, not the shadow failing to arrive.

This is why the charter's decomposition rule is what it is: the solids fix the black term's
amplitude through the level and say nothing about a lift, the structured backdrops identify the
lift, and the probes' pitch axis identifies its blur. `g0-shadow.md` reads them in that order.

## 6. What is left as an instrument caveat

- **The corner class on a capsule.** Ring 0–3 is unusable on the GPU tier (§4). Rings 3–6 and
  outward carry a −0.008 to −0.011 bias in `a` that the model does not explain; it is bounded, it is
  reported on every capsule row, and it is not the reference's.
- **`photo` and the per-channel fit.** vitrea's own capture, whose shadow is a pure gray multiply,
  reads back per-channel intercepts of (0.0020, 0.0005, 0.0013) in linear RGB on
  `photo__rrect-lg__rest` — non-zero and unequal, because on a textured backdrop the three channels'
  regressions are ill-conditioned at this amplitude. A per-channel `c` on `photo` therefore cannot
  by itself say whether a lift is coloured or gray at the 0.004 level the reference's lift lives at,
  and `g0-shadow.md` §6 answers that question a different way.
- **The 24–48 ring on the large spans.** The canvas leaves 20 CSS px of margin around `rrect-lg`, so
  that ring is absent there and truncated on `rrect-ml`. Reported absent, never zero.
- **Eight-bit quantisation.** The residual of every good fit on this bed sits at 0.0025–0.0030 in
  linear luminance near white, which is exactly one 8-bit code spread over root-twelve. Every fit
  quoted here is at the capture's own floor.
