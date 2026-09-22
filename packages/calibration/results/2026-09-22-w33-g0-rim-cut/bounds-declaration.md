# W33 G0 — bounds and stops, before any material fit

2026-09-22; claims §5.170; W33 clauses 1–3. No bound is adopted by this gate.
The complete numeric declaration is `tables.json` → `bounds` (304 strata), derived by
`tables.py`; `referee.json` holds the unrounded per-cell baselines. No constant is fitted.

## Population and geometry

Every fitting/referee, colour-family and conditionality row excludes `scenes.json`'s holdout
and recorded sets before opening the web PNG. `--include-holdout` belongs to G1's post-seal
read only and has NOT been run. Probe strength is stated at span 160. The native-only archival
inventory includes holdout and is not a fitting population. The separately requested predecessor
`halo.py` is an archival corroboration at its existing held-out scene, not a candidate read or
an input to the stroke family, bound or constant. No holdout configuration was recorded or spent.

A uses the declared bounding box, integer offset >= 2 CSS px: at 1x the first admitted centre
is 1.5 CSS px outside. The far edge is exclusive (`x >= x1` is outside); distance counts its
last inside index as `x1-1`. This is NOT analytic >= 2 CSS px. The Euclidean analytic box
exterior is printed per cell beside it. Both require BACKDROP RGB (0,0,0); web eligibility also
requires native RGB (0,0,0). Apple's own nonzero count uses the backdrop-black set BEFORE that
second restriction. The archival full-exterior census instead has NO inset and selects NATIVE
black, including pixels that Apple's body crushed to black over a nonblack backdrop.

The toolbar bbox is 156×44 (three 44px items, two 12px gaps); the stack inventory names the
120×56 overlay at [0,-8]. These boxes are not a union-of-shapes stroke sampler. B admits exact
single rounded rectangles/capsules only; all composite exclusions are enumerated in
`referee.json.declined`, not silently treated as another rectangle. Its available untinted
population is 51/37 light and 40/30 dark per scale before holdout removal; 46/32 and 38/28 after.
Each accessibility bed has 4/4 fitting cells (6/6 available, 2/2 held out).

B reads pixel centres in exact rounded-rect SDF shells: offset 1 is d in [0,1) DEVICE px;
offsets 2–6 are [1,2) through [5,6). Corner pixels project radially onto the appropriate arc,
so these are normal-distance samples, not a square bbox corner and not an angular oversample.
Every corner pixel is read once; the four corners and each available straight side are separate
strata. The native model-free notch is ring-luma[0] − min(ring-luma[-1],ring-luma[1]); it is a
detector and does not replace the RGB absolute residual. Tint scenes are present in A and the
forms experiment, not in B's literal `__rest` / `__inactive` population.

## A — zero by an explicit rule, not an arbitrary positive allowance

The receded non-holdout nine-backdrop reading is exactly **0.0%** on all six profiles. Apply
`ceil2sf(x)`, defined as 0 for x=0 and ceil(x/10^(floor(log10(x))-1)) times that step otherwise:
the bound is **0**, not epsilon. The stand-down target is fraction web>0 **0** and count web>1
**0**, at every cell and bed×span. `web>1` is a separate stronger target, not today's baseline.

Non-regression during the round additionally requires each cell's count web>1 <= its unrounded
G0 count. On 1x light `hc-text-28` / `hc-text-7` at span160 those counts are **66 / 39**;
on 2x light **222 / 150**. Analytic >=2 counts are **44 / 39** and **180 / 150**. All four are
probe. Neither zero target has been achieved here; no material changed. Halo max **137.10**
is corroboration only, not another fitted objective or adopted bound.

## B — per-stratum, absolute before either reduction

For each profile × pose × backdrop class × straight side / individual corner, pool the pixels
of its non-holdout cells and compute `mean(abs(native[c]-web[c]))` over pixels AND RGB channels.
The ceiling is that G0 value rounded UP to two significant figures. All **304** numeric ceilings
are in `tables.json.bounds`, spanning **0.5–200 bytes**; signed RGB means, channelwise MAE and
counts accompany every one. Separate classes are black-bearing, light-solid, photo, and
`dark-or-other-solid` (dark, mid-level and low-contrast rasters, explicitly not called pure black).
No stratum may buy another's regression. A single pooled ceiling would conceal the measured
orientation and accessibility differences. At G1's canonical read the same rounding rule can
propose a tighter adopted bound, but not loosen these pre-fit ceilings without a ruling.

This is a **non-regression declaration, not a claim that today's residual closes the gap**.
A round must table improvement and the remaining residual, not label passage of a 200-byte
baseline fidelity. The colour family is not identified: eight tested one-/two-/four-parameter
families leave substantial errors, even when direction is separated. A scalar amplitude plus
width is not yet a demonstrated sufficient model. The family/model decision precedes G1.

Offsets 2–6 use each cell's unrounded absolute RGB residual as a non-regression baseline, with
signed channel means beside it. Do not substitute the old +0.00…+0.21 shorthand. An operator
confined to d in [0,1) should leave those pixels exactly unchanged in this offline experiment;
the rendered round must verify that expectation rather than assume shader support is exact.

## Carried stops and expected post-fit readings

| stop | unchanged declaration | expected after the proposed fit |
| --- | --- | --- |
| C1 | <=0.0042, twelve standard bed×span rows, admitted bands only | Remain <=0.0042, approximately today's 0.00088–0.00391 after anchor compensation. Stroke-only change outside these bands is exactly 0; compensation's actual residual must be rendered. |
| Thin | Per-cell change of absolute deltaA in 3–6 and 6–12, spans32/44, against 0.002044 | Stroke-only move 0 and lift is already below its span64 knee. Accessibility's inherited absolute mismatch (worst0.02168) is not cured or re-pinned by this wave. |
| B1 light | span96 [8.8966,9.0193], 128 [12.6397,13.7947], 160 [16.7033,17.8198] | Exactly 8.9600 / 13.1648 / 17.3696: the law and lengths do not move. |
| B1 dark | span96 [8.9084,9.3180], 128 [12.7458,13.8499], 160 [16.7931,18.3237] | Exactly 9.0400 / 12.9280 / 16.8160, for the same reason. |
| B3 admitted | <=0.000056; current0.00005596255774381109,166 rows | Stroke-only pooled reading unchanged; inactive half exactly0 before and after. Active lift/anchor compensation must still keep pooled<=0.000056; no exact forecast is justified for that refit. |
| Whole exterior warning | current0.0007158135811605964, NOT bounded | Expected DOWN toward0 if the missing exterior stroke is reproduced. Inactive half0.0007967193578457206 should tend toward0, while its admitted half remains0. A colour/coverage form that fails to reproduce the stroke need not deliver this reduction. |
| M2 | Per-wave2%, reference re-pointed at the adopting gate under W32 DL4; cumulative drift tabled separately | Pure OUTSIDE forms touch0 pixels of the native-derived mask in all26 M2 cells. INSIDE form touches every one:257–1311 pixels/cell, listed in tables.json.m2. No justified numeric forecast of their standard deviations from those counts. Rebaseline at adoption, record every move and its mechanism. |

The anchor trade is an ESTIMATE, replaced by G1's rendered round: shadow occlusion maps to
encoded alpha by `1-(1-occlusion)^(1/2.4)`, not alpha=occlusion. The earlier **2.4%** estimate
used the wrong space. The charter's corrected **5–7% at span160** is a first-order scale for the
compensation, not a fixed multiplication applied to the anchors. `3–6` is watched separately.

## Form decision and accessibility

`forms.ts` constructs the finished RGBA8, thresholds at the live `DRAWN_ALPHA_THRESHOLD=0.5`,
and reuses the real contour, IoU, area and connected-body functions. Its baseline agrees with
all four matrix shape numbers on every one of380 non-holdout capture pairs. The inventory of442
rows (254 at contour1; selected115,48 at1) reads metadata, not held-out images.

(i) Measured per-cell best encoded black source-over depth outside:17 contour and17 IoU failures;
(ii) same depth inside:2/1 broad failures,0/0 selected, five broad conditioning changes and one
selected change (one known exclusion clears; 67 would become66 only if unread holdout rows stayed unchanged); (iii) source-over0.49 outside:113/123 broad
and37/41 selected failures; (iv) colour changed at held coverage:0/0 and no shape changes, but
native target RGB is outside the feasible premultiplied interval on all380 cells (378 even with
one-byte tolerance). A source-over oracle permitting an independent colour at each pixel still
forces73/59 broad and23/24 selected contour/IoU failures. This is a lower-bound feasibility test,
not a proposed material. None of these four constructions both reproduces the bytes and keeps
all existing promises. DL2 is drafted, UNRULED; re-adopting contour alone does not settle IoU.

**Accessibility declaration:** leave the new contour term independent of the `strongBorderRim`
substitution; do NOT silently replace or zero it when that fold replaces the lit rim. Both
measured accessibility beds retain a native notch on all4 active and all4 inactive fitting cells.
RT medians -16.678/-18.359 bytes, IC-coupled -17.014/-18.694, against positive web notches.
The new term's eventual coefficients on these beds are recorded outputs of the declared fold,
not an accessibility shadow refit. Forced-colours draws no optical body and therefore no new
stroke; isolated IC without RT and dark/2x accessibility are unmeasured and not inferred.

## Identity declaration

Flat `contourStrokeAlpha` gate **0**, gated `contourStrokeWidthDevicePx` (default1 device px),
appended as one gate-group. `identity-proof.ts` executes the live rule and reproduces both
frozen and all four27 digests, then extends its path-drop in memory. Widths0,.5,1,2,3,1000 all
preserve them when alpha0. Nested leaves leave an empty container and move every digest;
frozen light becomes`da59d059f9526c73`, not`b2b570e4adcea8fb`.
G1 must add the literal `contourStrokeAlpha: 0` in calibration's
`w31-identity-table.test.ts` and an inertLawCase in renderer's `w33-contour-stroke.test.ts`:
“alpha zero leaves the composited pixel unchanged at every width and device scale”. Extend
renderer `w31-gate-groups.test.ts` with the gated-width sweep. This proof is of digest routing,
not of shader inertness: no shader exists yet and no material source was edited here.
