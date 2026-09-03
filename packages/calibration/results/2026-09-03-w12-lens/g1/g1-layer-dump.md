# W12 G1 — Apple's Liquid Glass parameters read from the Core Animation layer tree

**What this is.** A new `dump-layers` subcommand on the native harness
(`apps/reference-apple/`) hosts each canonical scene in the capture window,
waits for SwiftUI to commit, and walks `window.contentView` and every layer
under it, reading each object's own declared state through the Objective-C
runtime. No pixels are captured; nothing under `fixtures/` is touched. The
numbers below are Apple's, as configured on this machine — not fitted.

- Machine: Mac14,12, macOS 26.5.2 (build 25F84), 1x display, light scheme,
  standard accessibility, capture window key and app active.
- JSON dumps: `layer-dumps/` (1.5 s settle, as briefed) and
  `layer-dumps-settle8/` (8 s settle — read §6 before using the 1.5 s set).
- Every input key below came from the filter's own `inputKeys` array
  (`inputKeysSource: "inputKeys"`, 55 keys on `glassBackground`). Nothing in
  this report was guessed from the ShatteredGlass key list.

---

## 1. The tree SwiftUI commits for one `.glassEffect` surface

```
NSHostingView                              320x200
└ NSViewBackingLayer
  ├ SwiftUI.ImageLayer                     320x200   (the raster background)
  └ CALayer                                320x200
    └ SwiftUI.SDFLayer                     <shape size>
      ├ CALayer                            0x0
      └ CALayer                            <shape size>
        ├ CABackdropLayer  name="@0"       <shape size>
        │   filters: [ CAFilter type=glassBackground  (55 inputs) ]
        │   └ CASDFLayer name="@0"  effect=CASDFOutputEffect
        │       └ CALayer 0x0
        │           └ CASDFElementLayer    <shape size>, cornerRadius, continuous
        ├ SwiftUI…SDFPortalLayer name="@1"
        └ CASDFLayer name="@2"  effect=CASDFKeyFillHighlightEffect
            filters: [ CAFilter type=vibrantColorMatrix ]
            └ SwiftUI…SDFPortalLayer 0x0
```

So the material is exactly three things: a **backdrop layer carrying one
`glassBackground` filter** (body, blur, refraction, bleed, shadow), an **SDF
element** that defines the shape the filter is evaluated against, and a
**separate SDF layer carrying the highlight effect** with its own vibrancy
colour matrix. A tint adds a fourth branch (§5).

`SwiftUI.SDFLayer` declares no readable state of its own; it is a plain
container.

## 2. The backdrop layer

Identical on every scene except `marginWidth`:

| property | value |
|---|---|
| `scale` | **0.25** (backdrop sampled at quarter resolution, every scene) |
| `lumaUpdateRate` | 0.25 |
| `allowsFilteredLuma` | 1 |
| `windowServerAware` | 1 |
| `allowsInPlaceFiltering` | 0 |
| `allowsSubstituteColor` | 0 |
| `groupNamespace` | `owningContext`; `groupName` `SwiftUI:<n>.00.0` |
| `enabled` | 1 |
| `zoom`, `bleedAmount`, `updateRate` | 0 |
| `tracksLuma` | **1 for spans ≤ 56, 0 for spans ≥ 96** — see §4 |
| `marginWidth` | 6.4 (32) · 8.8 (44) · 11.2 (56) · 68 (96) · 83 (128, 130, 160) |

`marginWidth` is `0.2 × span` up to span 56 and then jumps to 68 and 83; the
thick values are not a continuation of the thin law. `inputSourceSublayerName` on the glass filter is `"@0"`, the
backdrop layer's own name — that is the link from filter to source.

## 3. The `glassBackground` filter across span (checkerboard, settled)

Span = the surface's **minor** dimension: rrect-sm 64x32 → 32, capsule
120x44 → 44, rrect-md 160x96 → 96, rrect-ml 224x128 → 128, rrect-lg 280x160
→ 160.

| input key | rrect-sm (32) | capsule (44) | rrect-md (96) | rrect-ml (128) | rrect-lg (160) |
|---|---|---|---|---|---|
| `inputBleedAmount` | 11.2 | 15.4 | 33.6 | 44.8 | 56 |
| `inputBleedBlurRadius` | 0 | 0 | 67.2 | 89.6 | 112 |
| `inputBleedColorMatrixBlack` | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 |
| `inputBleedColorMatrixFillColor` | nil | nil | nil | nil | nil |
| `inputBleedColorMatrixSaturation` | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 |
| `inputBleedColorMatrixWhite` | 1 | 1 | 1 | 1 | 1 |
| `inputBleedDarkenBlend` | 1 | 1 | 1 | 1 | 1 |
| `inputBleedDistance0` | 1 | 1 | 1 | 1 | 1 |
| `inputBleedDistance1` | 0 | 0 | 0 | 0 | 0 |
| `inputBleedHeight` | 11.2 | 15.4 | 33.6 | 44.8 | 56 |
| `inputBleedOpacity` | 0 | 0 | 0.166667 | 0.333333 | 0.5 |
| `inputBlurDistance0` | -16 | -22 | -48 | -64 | -80 |
| `inputBlurDistance1` | -1 | -1 | -1 | -1 | -1 |
| `inputBlurDistance2` | 0 | 0 | 0 | 0 | 0 |
| `inputBlurDistance3` | 0 | 0 | 0 | 0 | 0 |
| `inputBlurDistance4` | 6.4 | 8.8 | 19.2 | 25.6 | 32 |
| `inputBlurOpacity0` | 1 | 1 | 1 | 1 | 1 |
| `inputBlurOpacity1` | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| `inputBlurOpacity2` | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| `inputBlurOpacity3` | 1 | 1 | 1 | 1 | 1 |
| `inputBlurOpacity4` | 1 | 1 | 1 | 1 | 1 |
| `inputBlurRadius` | 1.33333 | 1.33333 | 2.47619 | 3.2381 | 4 |
| `inputClamp` | 1 | 1 | 1.06961 | 1.06961 | 1.06961 |
| `inputClampPreserveHue` | 0 | 0 | 0 | 0 | 0 |
| `inputFaceColorMatrixBlack` | 0.35 | 0.35 | 0.5 | 0.5 | 0.5 |
| `inputFaceColorMatrixFillColor` | rgba(1,1,1,0.5) | rgba(1,1,1,0.5) | rgba(1,1,1,0.4) | rgba(1,1,1,0.4) | rgba(1,1,1,0.4) |
| `inputFaceColorMatrixSaturation` | 1 | 1 | 1 | 1 | 1 |
| `inputFaceColorMatrixWhite` | 0.95 | 0.95 | 1.03 | 1.03 | 1.03 |
| `inputFaceOpacity` | 1 | 1 | 1 | 1 | 1 |
| `inputInnerRefractionAmount` | -25.6 | -35.2 | -60 | -60 | -60 |
| `inputInnerRefractionHeight` | 8 | 11 | 20 | 20 | 20 |
| `inputMaxHeadroom` | 9999 | 9999 | 9999 | 9999 | 9999 |
| `inputOuterRefractionAmount` | 6.4 | 8.8 | 19.2 | 25.6 | 32 |
| `inputOuterRefractionHeight` | 4 | 5.5 | 12 | 16 | 20 |
| `inputRefractionDistance0` | -1 | -1 | -1 | -1 | -1 |
| `inputRefractionDistance1` | 0 | 0 | 0 | 0 | 0 |
| `inputRefractionOpacity` | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 |
| `inputSDRGradientDistance0` | -2 | -2 | -2 | -2 | -2 |
| `inputSDRGradientDistance1` | -1 | -1 | -1 | -1 | -1 |
| `inputSDRHoldingToneEnabled` | 1 | 1 | 1 | 1 | 1 |
| `inputSDRHoldingToneWhite` | 0.97 | 0.97 | 0.97 | 0.97 | 0.97 |
| `inputSDRShadowOpacity` | 0.08 | 0.08 | 0.148571 | 0.194286 | 0.24 |
| `inputShadowAmount` | 20 | 27.5 | 60 | 75 | 75 |
| `inputShadowBlurRadius` | 0 | 0 | 40 | 40 | 40 |
| `inputShadowColorMatrixBlack` | 0 | 0 | 0 | 0 | 0 |
| `inputShadowColorMatrixFillColor` | rgba(0,0,0,0.278182) | rgba(0,0,0,0.278182) | rgba(0,0,0,0.12) | rgba(0,0,0,0.12) | rgba(0,0,0,0.12) |
| `inputShadowColorMatrixSaturation` | 1.8 | 1.8 | 1.8 | 1.8 | 1.8 |
| `inputShadowColorMatrixWhite` | 1 | 1 | 1 | 1 | 1 |
| `inputShadowDistanceOffset` | 0 | 0 | 0 | 0 | 0 |
| `inputShadowHeight` | 12.8 | 17.6 | 38.4 | 51.2 | 64 |
| `inputShadowOffset` | NSSize: {0, 8} | NSSize: {0, 8} | NSSize: {0, 8} | NSSize: {0, 8} | NSSize: {0, 8} |
| `inputShadowOpacity` | 0.5 | 0.5 | 0.392857 | 0.321429 | 0.25 |
| `inputShadowRadius` | 24 | 24 | 24 | 24 | 24 |
| `inputShadowVibrancyContribution` | 0 | 0 | 0.333333 | 0.666667 | 1 |
| `inputSourceSublayerName` | @0 | @0 | @0 | @0 | @0 |

### 3.1 The size law, closed form

Every span-dependent input is one of three shapes. Let `d` be the span,

```
u = clamp((d - 48) / 112, 0, 1)      # 0 at d≤48, 1 at d≥160
v = clamp((d - 64) /  96, 0, 1)      # 0 at d≤64, 1 at d≥160
```

**Proportional to `d`** (exact on all five cells, and on the two
`glass-over-glass` surfaces at d=56 and d=130, which were not used to derive
them):

| input | law |
|---|---|
| `inputBleedAmount`, `inputBleedHeight` | `0.35 d` |
| `inputBlurDistance0` | `-0.5 d` |
| `inputBlurDistance4`, `inputOuterRefractionAmount` | `0.2 d` |
| `inputOuterRefractionHeight` | `0.125 d` |
| `inputShadowHeight` | `0.4 d` |
| `inputInnerRefractionHeight` | `min(0.25 d, 20)` |
| `inputInnerRefractionAmount` | `max(-0.8 d, -60)` |
| `inputShadowAmount` | `min(0.625 d, 75)` |
| `inputBleedBlurRadius` | `0.7 d` when `v > 0`, else `0` |
| `CABackdropLayer.marginWidth` | `0.2 d` for d ≤ 56; 68 at d=96; 83 at d ≥ 128 (no single law) |

**On the `u` ramp:**

| input | law | check at d=56 / d=130 |
|---|---|---|
| `inputBlurRadius` | `1.3333 + 2.6667 u` | 1.52381 / 3.28571 — both exact |
| `inputShadowOpacity` | `0.5 − 0.25 u` | 0.482143 / 0.316964 — exact |
| `inputSDRShadowOpacity` | `0.08 + 0.16 u` | 0.091429 / 0.197143 — exact |

**On the `v` ramp:**

| input | law |
|---|---|
| `inputShadowVibrancyContribution` | `v` |
| `inputBleedOpacity` | `0.5 v` |
| `inputShadowBlurRadius` | `40` when `v > 0`, else `0` |

The two ramps were fitted on the five checkerboard cells and then **predicted**
the `glass-over-glass` surfaces at d=56 and d=130 to every digit the dump
prints. That is a strong independent confirmation, and it says the size law is
piecewise-linear in the minor span with two distinct knees (48 and 64) and a
common saturation at 160 — not a single smooth saturating curve.

**Independent of everything measured here** (identical in all 14 dumps):
`inputBlurOpacity0..4` = 1, 0.5, 0.5, 1, 1 · `inputBlurDistance1` = −1 ·
`inputBlurDistance2` = `inputBlurDistance3` = 0 · `inputRefractionDistance0` =
−1, `…1` = 0 · `inputRefractionOpacity` = 0.3 · `inputFaceOpacity` = 1 ·
`inputFaceColorMatrixSaturation` = 1 · `inputBleedColorMatrix{Black,White,
Saturation}` = 0.9, 1, 1.2 · `inputBleedColorMatrixFillColor` = nil ·
`inputBleedDarkenBlend` = 1 · `inputBleedDistance0/1` = 1, 0 ·
`inputShadowColorMatrix{Black,White,Saturation}` = 0, 1, 1.8 ·
`inputShadowOffset` = (0, 8) · `inputShadowRadius` = 24 ·
`inputShadowDistanceOffset` = 0 · `inputSDRGradientDistance0/1` = −2, −1 ·
`inputSDRHoldingToneEnabled` = 1 · `inputSDRHoldingToneWhite` = 0.97 ·
`inputMaxHeadroom` = 9999 · `inputClampPreserveHue` = 0.

## 4. What depends on the backdrop, and what does not

Five inputs are **not** size laws — they are set from the sampled backdrop, and
only on the surfaces whose backdrop layer has `tracksLuma = 1` (span ≤ 56):

| scene (span) | `tracksLuma` | FaceCM Black | FaceCM White | Face fill α | Shadow fill α | `inputClamp` |
|---|---|---|---|---|---|---|
| checkerboard rrect-sm (32) | 1 | 0.35 | 0.95 | 0.500 | 0.2782 | 1 |
| checkerboard capsule (44) | 1 | 0.35 | 0.95 | 0.500 | 0.2782 | 1 |
| checkerboard toolbar item (44) | 1 | 0.35 | 0.95 | 0.500 | 0.2782 | 1 |
| light-solid capsule (44) | 1 | 0.81875 | 1.03 | 0.2656 | 0.050 | 1.06961 |
| photo capsule (44) | 1 | 0.31875 | 0.91875 | 0.5156 | 0.285 | 1 |
| photo glass-over-glass upper (56) | 1 | 0.69375 | 1.03 | 0.3281 | 0.2032 | 1.06961 |
| **any span ≥ 96, any background** | 0 | **0.5** | **1.03** | **0.400** | **0.120** | **1.06961** |

Read plainly: **thin glass adapts its body to the backdrop; thick glass does
not.** Above the knee the face matrix is a constant (0.5 / 1.03 / white at 40% /
black at 12%) on a light solid, a black-and-white checkerboard and a photo
alike. Below it, a bright backdrop (light-solid, sRGB 242/242/247) leaves the
body near its unadapted values, while a mid/high-contrast backdrop
(checkerboard, photo) pushes the white fill from 26.6% to ~50%, drops the black
lift from 0.82 to ~0.33 and more than quintuples the shadow fill alpha.

`inputClamp` is binary in practice: 1.06961 unadapted, 1 fully adapted.

**Nesting** (`photo__glass-over-glass__rest`): two completely independent
surfaces, each with its own backdrop layer, glass filter and highlight, each
parameterised by its own span (130 and 56). The upper surface's filter shows no
sign of knowing it sits on glass — its numbers are exactly what the size law
predicts for d=56 with a backdrop-adapted face.

**Grouping** (`checkerboard__toolbar-group__rest`): one backdrop layer, one
glass filter, one highlight layer for the whole row; the three 44x44 capsules
are three `CASDFElementLayer`s (`operation: union`, at x = 0, 56, 112) under a
single `CASDFLayer` whose `smoothness` is **12** rather than 8. Every filter
input matches a single 44-span surface. So a merged group is a single material
evaluated over a unioned SDF, and the only trace of merging is the smoothness.

**Pressed** (`checkerboard__rrect-md__pressed`, `Glass.interactive(true)`):
**no difference at all.** A full structural diff against the rest cell differs
only in object addresses and the SwiftUI group serial. The pressed appearance is
therefore not a different material configuration at rest — it is either applied
only while a gesture is actually active, or it lives somewhere this walk does
not reach. This is a gap worth chasing before any pressed-pose claim leans on
layer parameters.

## 5. The highlight, the output clamp, and the tint

**`CASDFKeyFillHighlightEffect`** — identical in all 14 dumps, every scene:

```
keyAmount   0.5     keyAngle    -0.7853981633974483  (= -π/4)
fillAmount  0.5     fillAngle    2.356194490192345   (= 3π/4)
keySpread   1.5707963267948966 (= π/2)   fillSpread  π/2
keyHeight   1       fillHeight   1
keyHeightOffset/Scale 0 / 1      fillHeightOffset/Scale 0 / 1
keySpreadOffset/Scale 0 / 1      fillSpreadOffset/Scale 0 / 1
curvature   0.7     global       0
```

Two lights exactly opposite (−45° and +135°), equal amplitude 0.5, each with a
π/2 spread, and one curvature constant 0.7. The highlight layer carries a
`vibrantColorMatrix` filter whose 5x4 matrix is the same everywhere:

```
R' =  1.2024 R − 1.0014 G − 0.1010 B + 0.9
G' = −0.2976 R + 0.4987 G − 0.1011 B + 0.9
B' = −0.2977 R − 1.0012 G + 1.3989 B + 0.9
A' =  A
```

**`CASDFOutputEffect`** on the body: `minimum` = −10000 always, `maximum` falls
with span — 39.52764 (32 and 44), 39.26310 (56), 37.77141 (96), 36.30592 (128),
36.20362 (130), 34.46388 (160). Monotone but not obviously a clean law; recorded
rather than fitted. `CASDFLayer.smoothness` = 8 (12 for the merged group),
`gaussianRadius` = 0, `mergeElements` = 0, `effectOffset` = 0.
`CASDFElementLayer.gradientOvalization` = 0 for capsules and rrect-sm, **0.5**
for md/ml/lg and the glass-over-glass base — another thin/thick split.

**Tint.** `Glass.tint(_:)` does **not** change the `glassBackground` filter.
Verified directly: `photo__capsule-button__rest`, `…-tint-orange` and
`…-tint-blue` have byte-identical glass filters (Black 0.31875, White 0.91875,
fill α 0.515625, shadow α 0.285, clamp 1). The tint is an extra branch inserted
between the backdrop layer and the highlight layer:

```
CALayer "@1"
└ CALayer "@0"
  ├ CASDFLayer "@0"  effect=CASDFGradientEffect
  │   filters: [ CAFilter vibrantColorMatrix, inputBackdropAware = 1 ]
  │   └ CASDFElementLayer  <shape>
  └ CASDFLayer "@1"  effect=CASDFFillEffect
      compositingFilter: "destIn"      ← a filter NAME string, not an object
```

The gradient effect is the same for both hues: colours white(α1), white(α1),
white(α0) at SDF distances −1, 0, 10, interpolations linear then a cubic Bézier
`(0.60938 0.00663; 0.47124 0.99115)`, `premultiplied` = 1.

The tint's own colour matrix is backdrop-aware and is **pure luminance in, one
line out**. Both hues' matrices factor exactly through the Rec.709 luma weights
(0.2126, 0.7152, 0.0722):

| tint | R' | G' | B' |
|---|---|---|---|
| orange, sRGB 255/149/0 | `0.40000 L + 0.60000` | `0.26300 L + 0.32125` | `0` |
| blue, sRGB 10/132/255 | `0.04613 L − 0.00692` | `0.24401 L + 0.27364` | `0.36954 L + 0.63045` |

At `L = 1` each line lands **exactly on the seed** — (1.0, 0.58425, 0) is
systemOrange and (0.03921, 0.51765, 1.0) is systemBlue to five decimals. At
`L = 0` it lands on a darker, desaturated shade of the same hue. That is the
reference's tint tone curve, stated in its own numbers: an affine map of
backdrop luminance onto a line whose bright endpoint is the seed colour itself
— which is what claims §5.36's "an opaque shade of the seed" asserted from
pixels, now confirmed from the configuration.

## 6. What I could not read, and why

1. **The 1.5 s dumps are not settled.** The five backdrop-adaptive inputs (§4)
   are animated toward their adapted values over seconds on `tracksLuma = 1`
   surfaces. `checkerboard__capsule-button__rest` reads FaceCM Black 0.628 in
   the committed 1.5 s dump and 0.35 at 8 s; an earlier 1.5 s run of the same
   scene read 0.85 (its file has since been overwritten), so the 1.5 s reading is
   not even repeatable. **Use `layer-dumps-settle8/`.** The
   1.5 s set is kept only as evidence of the transient. Every number quoted in
   this report is from the 8 s set. This also raises a question for the capture
   protocol: a fixture taken before this adaptation settles photographs the
   transient, not the material.
2. **No `CALayer`-level private state.** The class walk stops at `CALayer`
   deliberately. `CALayer`'s selector list in a loaded application is not
   `CALayer`'s: MapKit's `vk_autoFadeOutShapeRectLayer` category getter *builds
   and inserts a sublayer* when read, so the first version of this walk grew the
   tree it was walking — 12 254 layers and 2.7 million reads before it was
   killed. The stock geometry (frame, bounds, position, cornerRadius,
   cornerCurve, contentsScale, opacity, masksToBounds) is recorded explicitly
   instead.
3. **`SwiftUI.SDFLayer` and `CASDFFillEffect` expose nothing.** Neither class
   declares readable properties or zero-argument getters below its superclass.
4. **The SDF sign convention is unresolved.** The tint gradient's distances
   (−1, 0, 10) and `CASDFOutputEffect.maximum` cannot both be read the same way
   without knowing whether positive distance is inside or outside the shape.
   That decides whether the tint fades over 10 pt *inward from the rim* or is
   uniform inside — a visible difference. Worth settling before the tint pathway
   is refit.
5. **One display, one appearance.** 1x only (this machine is not Retina), light
   scheme only, standard accessibility only. Whether any of these constants
   change at 2x, in dark, or under Reduce Transparency is unmeasured. The
   `--scenes` flag makes the dark and accessibility scenes a one-line run once
   somebody decides the question is worth the minutes.
6. **`inputSourceSublayerName` is `"@0"`** everywhere, i.e. a name-based link to
   the backdrop layer, and carries no numeric information.
7. **`CAColorMatrix` values arrive as `NSValue`, not `NSData`.** They are
   unboxed here by reading the objCType (`{CAColorMatrix=ffffffffffffffffffff}`)
   and pulling twenty floats. Any other boxed struct is recorded with its
   encoding and description but not decoded.

## 7. The ten numbers that matter most

1. `CABackdropLayer.scale` = **0.25** — Apple samples the backdrop at quarter
   resolution, on every scene and every span.
2. `inputBlurRadius` = **1.3333 → 4.0** across span, and it is a *ramp*
   `1.3333 + 2.6667·clamp((d−48)/112, 0, 1)`, not a saturating curve.
3. `inputBlurDistance0` = **−0.5 d** — the deepest of five blur taps scales
   exactly with the surface's minor span.
4. `inputInnerRefractionAmount` = **max(−0.8 d, −60)** and
   `inputInnerRefractionHeight` = **min(0.25 d, 20)** — the lens saturates at a
   96 pt span, exactly where `tracksLuma` also switches off.
5. `inputOuterRefractionHeight` = **0.125 d**, `inputOuterRefractionAmount` =
   **0.2 d** — the outer lens never saturates.
6. Thick-glass face matrix = **black 0.5 / white 1.03 / white fill at α 0.40 /
   shadow fill black at α 0.12**, identical on light solid, checkerboard and
   photo.
7. Thin-glass face fill α = **0.2656 on a bright backdrop vs 0.500 on
   checkerboard** — the body's white fill nearly doubles with backdrop, and only
   below the span knee.
8. `CASDFKeyFillHighlightEffect`: **two lights at −π/4 and 3π/4, amount 0.5
   each, spread π/2 each, curvature 0.7** — constant everywhere.
9. Tint tone curve, orange: **R = 0.4 L + 0.6, G = 0.263 L + 0.32125, B = 0**,
   hitting systemOrange exactly at L = 1.
10. `inputShadowOffset` = **(0, 8)**, `inputShadowRadius` = **24**,
    `inputShadowOpacity` = **0.5 − 0.25 u** — the drop shadow's geometry is
    fixed and only its opacity moves with span.
