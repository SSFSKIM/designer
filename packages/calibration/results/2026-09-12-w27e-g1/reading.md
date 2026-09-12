# W27e G1 — the label operator's semantics, its two tiers, and what it saturates (2026-09-12)

The prose working behind claims §5.137. The declaration is `declaration.md`, committed before any
of this was read. The numbers are in `structure.json`, `order.json`, `highlight-opacity.json`,
`operator-probe/results.json` and `verdict.json`.

## 1. The corpus read: §5.136 §4 reproduces, and four facts around it that it did not read

`structure.py` walks all 50 dumps. **§5.136 §4 reproduces exactly** — two distinct label matrices,
24 of 26 labelled dumps carrying one, the two `-label-hot` scenes carrying an empty filter list,
`inputBackdropAware` 1 and `inputClamp` 1 throughout. Declaration stop S3 is not tripped and no
committed number is rewritten.

Four facts around it, declared in §1.2 and read after the declaration was committed:

1. **No label layer carries a `compositingFilter`, and none carries a `backgroundFilters` entry.**
   `apps/reference-apple/Sources/LayerDump.swift` reads both (lines 399–407) and emits them when
   non-nil, so this is a measured negative and not a gap in the instrument. 0 of 26.
2. **Every label layer carries exactly one filter.** The set of filter counts over the 26 is
   `{0, 1}`: one on the 24 automatic labels, zero on the two that name their own colour.
3. **The label is composited above the material's own output and below the key-fill highlight.**
   The label's `CGDrawingLayer` lives in branch 0 of the `glassEffect`'s `SwiftUI.SDFLayer`, which
   is *below* the material branch in paint order — and it is not drawn there. The
   `SDFPortalLayer` inside the material branch names branch 0's root as its `sourceLayer` and
   carries `hidesSourceLayer: 1`, on **26 of 26**. The projected order is
   `CABackdropLayer @0` (the `glassBackground` material) → the label's portal → `CASDFLayer @2`
   (the `CASDFKeyFillHighlightEffect`), on 24; on the two tinted cells the author tint's gradient
   layer inserts at index 1 and the order becomes backdrop → tint → label portal → highlight. So
   the buffer immediately beneath a label is **the glass material's composite including the author
   tint and excluding the highlight**.
4. **The layer the *surface* operator sits on draws nothing in this corpus.** Its `opacity` is
   **0** on all 50 probe occurrences and **1** on all 58 of G0's. Every probe dump records
   `isKeyWindow: false` and every G0 dump `true`, and §5.128 records that the bright rim goes to
   zero in the receded pose in every profile at both scales. This was read as a control on the
   label's own layer — which is `opacity` 1 in both schemes, so nothing about the label rides on
   it — and it is kept because of what it does to §5.136 §5. See §6.

## 2. The semantics, settled — and two corrections to the reasoning it would have been settled by

The declaration's hypothesis was the classic vibrancy blend: plus-darker in light,
`out = max(0, backdrop + ink − 1)`, and plus-lighter in dark, `out = min(1, backdrop + 0.95·ink)`.
**It is refuted, and the reading that fits is that the operator is a saturating source-over
transform with no destination blend at all.**

### 2.1 What the configuration says

The arithmetic refutes the hypothesis on its own terms before any external source is consulted.
A single mechanism "combine the filtered source with the buffer beneath, then clamp" cannot produce
both blends from these two matrices: `clamp(ink + backdrop − 1)` is plus-darker and needs offset
−1, `clamp(ink + backdrop)` is plus-lighter and needs offset **0**, and the dark matrix's offset is
**+1**. Under any uniform additive rule one of the two schemes degenerates to a constant. The two
matrices are not a plus-darker/plus-lighter pair.

### 2.2 What Apple says, and what Apple ships

Apple has never documented the operator. The one place it names a compositing mode is the Yosemite
AppKit release notes, and it names four as examples without binding any of them to an appearance:

> "Vibrancy" describes a compositing mode that does special blending such as "Plus Darker", "Plus
> Lighter", "Color Dodge", and "Color Burn."
> — [AppKit Release Notes, OS X 10.10](https://developer.apple.com/library/archive/releasenotes/AppKit/RN-AppKitOlderNotes/)

The same document says the mechanism is `layer.compositingFilter`. WWDC 2018 session 218 is the
most specific Apple has ever been and still declines the formula — "it's very similar to a color
dodge or burn"; the vibrant appearances "include the exact formula" and Apple does not publish it.
So **the plus pairing is not Apple's documentation**; it is folklore that the release note's
example list is usually read as.

Apple's own shipped renderer contradicts the folklore for classic vibrancy. QuartzCore's GLSL
generator, recovered from a shipped binary by a third party, emits `vibrantLight` as a colour-burn
composed with a luminance-weighted source-over, and `vibrantDark` as its colour-dodge mirror —
not the plus modes at all. Apple's "similar to a color dodge or burn" was literal.

**The decisive item is the shader signature.** The macOS 26.5 QuartzCore metallib carries three
entry points for this filter family:

```
vibrant_color_matrix(half4, half4, constant half4*, half, half)
vibrant_color_matrix_sover(half4, half4, constant half4*, half, half)
backdrop_aware_vibrant_color_matrix_sover(half4, half4, half4, constant half4*, half, half)
```

The backdrop-aware entry point takes **one extra colour input and nothing else**, and there is no
backdrop-aware variant that is not `_sover`. Beside it, the renderer's own fault string names the
mechanism — "Unable to render backdrop-aware vibrant color matrix filter while existing memoryless
offscreen surface in use" — around a `capture_in_place_backdrop` call into a surface labelled
`implicit-backdrop-vibrant-color-matrix`. So `inputBackdropAware` **binds a snapshot of what is
already rendered beneath the layer as an additional input image to the filter, and the filter's
result is then composited source-over.** It does not change the destination blend, because the only
destination blend this filter has is source-over.

Two further keys are settled the same way. UIKit's `_UIVibrancyEffectVibrantColorMatrixImpl` builds
the filter from a configuration created by
`_vibrantColorMatrixConfigurationWithColorMatrix:maxColorComponent:preservesHue:` and writes
`inputClamp` from `maxColorComponent` and `inputClampPreserveHue` from `preservesHue`. SwiftUI
exposes the same three knobs on the glass foreground path as
`Material.ForegroundStyle.colorMatrix(_:backdropAware:maxColorComponent:preservesHue:)`, whose
two-argument form defaults `maxColorComponent` to +∞. So **`inputClamp: 1` means "clamp the maximum
colour component to 1.0"**, and `inputClampPreserveHue` unset means clamp per channel rather than
scaling the triple to keep its hue.

*Attestation, stated plainly.* Items 1 and 2 of this subsection are Apple's own words at Apple's own
URLs. The shader signatures, the fault string, the UIKit and SwiftUI symbol names and the
`flattened_compositing_filter` behaviour below are **recovered from shipped Apple binaries by third
parties**. They are not Apple's words and were not disassembled on this machine. They are used here
because they are the only attestation that exists — Apple documents none of this — and because each
one is a name or a signature rather than an interpretation.

### 2.3 The correction: the absent `compositingFilter` is expected, not evidence of no blend

§1 fact 1 would naturally be read as "there is no blend, therefore the result composites
source-over". **That inference is wrong, and it is recorded here because it is the one this gate
would otherwise have been built on.** QuartzCore's `flattened_compositing_filter(CALayer*)` returns
the lone filter's type as the layer's compositing filter when `compositingFilter` is nil and
`layer.filters.count == 1`, for exactly `vibrantColorMatrix`, `vibrantDark` and `vibrantLight`.
The corpus satisfies that precondition on all 24 — §1 fact 2 is the precondition, read
independently — so **the `vibrantColorMatrix` *is* the label layer's compositing filter**, and its
absence from the `compositingFilter` key says nothing about whether a blend exists. The conclusion
survives, by the shader signature rather than by the absence.

### 2.4 The operator, and what its input is

> **Light (Apple's light scheme, vitrea's `darkening`):** the ink is black at the glyph's own
> coverage.
> **Dark (Apple's dark scheme, vitrea's `lightening`):** the ink is white at 0.95 × the glyph's own
> coverage.
> Composited source-over onto the material beneath. No destination blend.

Both matrices offset every colour channel by a whole unit against a `[0, 1]` clamp, so **the
operator saturates**: nothing of the input colour survives, and the only thing the input
contributes is its alpha, which `lightening` scales by 0.95.

**What the input is, exactly.** The shader receives both the source (the layer's own rendered
glyphs) and the captured in-place backdrop. Which of the two the colour matrix consumes is *not*
resolvable from the evidence, and **it does not matter**: a unit offset against `inputClamp` = 1
saturates either one. It matters for the alpha row, and there both readings agree too — if the
matrix consumes the source, `lightening`'s 0.95 scales the glyph coverage directly; if it consumes
the backdrop and the source supplies coverage, 0.95 scales the backdrop's alpha, which is 1 inside
the glass, and the coverage multiplies in afterwards. Same answer.

What *is* identified is the buffer: `capture_in_place_backdrop` snapshots what is already rendered
beneath the layer, and §1 fact 3 says what that is in the tree — **the glass material's composite
including the author tint and excluding the key-fill highlight.** That is the point in Apple's
stack the operator's backdrop input is taken at.

### 2.5 The one thing that is not resolvable, and what it is worth

**Where the clamp sits relative to the backdrop combination is unverified.** The research found the
clamp and preserve-hue scalars passed as parameters to the same shader function that receives the
source, the destination and the backdrop, so the ordering is inside a function body nobody has
disassembled. The legacy software rasteriser (`CA::OGL::SW::tex_vibrant_color_matrix`) does the
matrix first and the combination second, which is the ordering assumed here, but it is the legacy
path.

**And no native pixel can arbitrate it.** There is no native fixture for a label, the no-text
fixture rule stands with §5.136 §4's three locks, and a fixture is not going to be made. So this is
a reading, taken on the best attestation available, with its alternative and the alternative's
magnitude both recorded — §4 measures them apart.

**Where it has no consequence at all:** at the ink Apple actually feeds the operator. §4's
`atAppleOwnInk` row reads the two readings **11 code values apart at worst**, on one cell, and that
cell is the one where the 0.95 decides it: under the declared reading the alpha is a visible 5 %
pull-back (white over a 0.133 material reads 244); under the plus-lighter reading it is inert,
because that composite saturates to 255 whatever the alpha. In light, at black ink, the two readings
agree to **0** on every ground.

**Where it does have consequence:** at any ink that is neither black nor white — which is every
extended ink vitrea publishes and none that Apple ships. There the two readings are up to **61**
code values apart (§4).

## 3. The operator on vitrea's two tiers

Stated, not implemented. `packages/calibration/scripts/vibrancy.ts` carries it as a pure evaluator
and `test/vibrancy.test.ts` pins its coefficients to the committed dumps.

**The selector.** Apple selects by colour scheme and by nothing else the probe moved (§5.136 §4).
vitrea cannot use the document's scheme: a vitrea surface's own level does not have to follow it,
and §5.133 §4's finding was that "the vibrancy operator switches with the glass, not beside it".
The selector is therefore the material's own composite level against the CSS tier's
`foregroundCrossover` — the same quantity the published primary ink already switches on
(`css-tier.ts:912`, `optics.ts:3416`, 0.475). Granularity matches Apple's: one matrix per layer
there, one operator per surface here.

**Both tiers, same function.**

| | input | output |
| --- | --- | --- |
| selector | the material's composite level, and `foregroundCrossover` | `darkening` \| `lightening` |
| `darkening` | the ink's automatic level (alpha only) | `rgb(0 0 0 / α)` |
| `lightening` | the ink's automatic level (alpha only) | `rgb(255 255 255 / 0.95·α)` |

**`gpu-texture`.** Apple's literal per-pixel pipeline is available: `feColorMatrix` at
`color-interpolation-filters: sRGB` on the ink, composited source-over. §5.133 §5 established that
the colour transform is exact there and that the tier is immune to the blend collapse.

**`css-backdrop`.** §5.133 §5 measured that a `mix-blend-mode` inside the host collapses
`backdrop-filter` sampling for a group whose proxy lives outside that element's subtree, so a
destination blend is unavailable and the operator has to be folded into the ink on the CPU from the
material's own composite level.

**What the CSS-tier fold loses relative to the per-pixel path: nothing.** That is the payoff of
§2.4 and it is worth stating as a result rather than as an absence. The operator carries **no
backdrop term** — the material's composite level enters only as the *selector*, and the selector is
per-surface on both tiers because it is per-layer in Apple's own configuration. So the fold is the
per-pixel path, and §4 measures them equal. The constraint §5.133 §5 found is real and simply never
binds on this operator.

Two things do *not* follow from that, and are named so G2 does not inherit them as licence:

- The material *beneath* the label still varies per pixel, and the ink's alpha lets it through.
  Whatever the CSS tier already loses in the material it still loses under the label; that is X1's
  standing record, not something the operator adds.
- Had the alternative reading been right, the fold would lose up to 61 code values (§4) — and
  there would be no way to recover them, because **Chromium 151 does not support
  `mix-blend-mode: plus-darker` at all** (§4). The per-pixel path for that reading does not exist
  on the web on either tier.

## 4. The browser proof, and the tolerance

`operator-probe/run.mjs` on real Chromium (`channel: "chromium"`, chromium/151.0.7922.34), Apple
metal-3, `isFallbackAdapter: false`, 1120 × 1000 at dpr 1, port 5232 verified free with
`strictPort`, every reading a compositor screenshot. Declaration stop S5 is not tripped.

The bench is 7 material grounds × 8 inks × 4 arms × 2 schemes = 448 flat cells, each in its own
isolated group so a blended swatch blends against its own ground and nothing else. The glass arm
puts the same patches inside a real host on each of the three tier configurations, over the
checkerboard page, so the material under a patch varies.

**A. The declared path against the closed form — the tolerance.** 112 cells per arm.

| arm | max |mean − closed form|, code values of 255 |
| --- | ---: |
| `over` (`feColorMatrix` at sRGB, source-over) | **0.54** |
| `fold` (the CPU fold, painted flat) | **0.47** |

**The measured tolerance is 0.54 code values**, against the 1 declared in §3 of the declaration
before the run. **What it bounds is the analytic operator against the browser's composite of it.**
It is not a bound between vitrea and macOS: there is no native label fixture and, under the no-text
fixture rule, there cannot be one. The fidelity claim available on this path is a configuration
claim — Apple's coefficients, read exactly, zero residual, 26 dumps — and this number is not it.

**B. The fold against the per-pixel path.** Max **1** code value over 112 pairs, on one cell
(`dark--over--black-085--g4`, 223 against 222), which is the 8-bit quantisation of the pre-computed
flat colour. On the glass arm, over a material that actually varies: `over` and `fold` differ by
**0.00** on `gpu-texture` and `gpu-dom`, **0.04** worst on `css`, in both schemes. In light both
read a flat `[0, 0, 0]` at sd 0 over a material at sd 3.58 (css) and 12.59 (gpu-dom) — the ink does
not track the material, which is §3's claim measured directly.

**C. The alternative reading.** Half of it is not expressible in this engine, which the run asked
rather than inferred: `CSS.supports("mix-blend-mode", "plus-darker")` is **false** and
`plus-lighter` **true** (and `background-blend-mode` carries neither). A rejected value computes to
`normal`, so a light-scheme reading taken through a dropped blend would look like two readings
agreeing when they were never compared. The dark half is measured in the browser; the light half is
stated from the closed form and marked as such in `verdict.json`.

| | against the declared operator, max code values | source |
| --- | ---: | --- |
| light | 61 | closed form — the engine cannot express it |
| dark | 49 | browser |
| **at Apple's own ink** (black in light, white in dark) | **11** | browser; light agrees to 0 |

**A finding beyond the charter, and a free corroboration.** The plus-blend cases reproduce
§5.133 §5's collapse with a *different* blend: `mix-blend-mode: plus-lighter` inside the host takes
the bare material from sd 3.58 to sd **35** on `css` and from 12.59 to **35** on `gpu-dom` — the
same flat-white-over-raw-page signature §5.133 §5 measured with `multiply` — and leaves
`gpu-texture` byte-identical. The light cases, where the blend was dropped, leave the material
untouched, which is the control.

## 5. The automatic label colour

**The dumps cannot attest it.** A `CGDrawingLayer` carries rendered content and no colour property,
and `label.srgb` is null on every automatic scene by construction. Declared in advance (declaration
§4): what comes from documentation is published as documentation-sourced.

**What macOS's automatic label colour is.** Apple publishes no component values for the label ladder
and says so — "Avoid hard-coding system color values in your app… The actual color values may
fluctuate from release to release" (HIG, Color). The values below are **third-party measurements**,
four of them independent and on different API surfaces and OS generations, agreeing exactly, and
unchanged from macOS 11 to 26.5:

| | Aqua (light) | DarkAqua (dark) |
| --- | --- | --- |
| `labelColor` | black at **0.847059** | white at **0.847059** |
| `secondaryLabelColor` | black at 0.498039 | white at 0.549020 |
| `tertiaryLabelColor` | black at 0.258824 | white at 0.247059 |
| `quaternaryLabelColor` | black at 0.098039 | white at 0.098039 |

SwiftUI's `Color.primary` resolves to `labelColor`, alpha included, and a default `Text` uses it.
The macOS ladder is **not** the iOS one (100 / 60 / 30 / 18 on a cool `#3C3C43`), and the dark
column is not a mirror of the light one.

**What it carries inside the glass.** The operator saturates it, so the level does not survive — but
the alpha does. **Apple's automatic label inside a Liquid Glass surface renders as black at
α 0.847 in light and white at α 0.804706 (0.847059 × 0.95) in dark**, at the glyph's antialiased
coverage. The 0.95 is measured from the dumps; the 0.847 is documentation-sourced in the sense
above.

**Against W27a's four published levels.** vitrea publishes `FOREGROUND_INK` `#1c1c1e` / `#f5f5f7`
(`css-tier.ts:200`) with level alphas secondary 0.6, tertiary 0.3, quaternary 0.18
(`css-tier.ts:273`) — the **iOS** ladder on a non-neutral ink — and solves secondary per surface
against a WCAG 4.5 floor over the material's own composite bounds (Decision Log 9,
`inkAlphaHoldingContrast`, `optics.ts:3972`).

*What G2 must re-derive:*

1. **The primary ink's colour.** `#1c1c1e` and `#f5f5f7` are vitrea's own choice; under the operator
   the ink is pure black and pure white. This is an X4 event of the kind X4 anticipates — the four
   names keep their names and change only their derivation.
2. **The primary ink's alpha.** vitrea publishes it opaque; Apple's automatic label is not. The two
   are not interchangeable: pure black at 0.847 and `#1c1c1e` at 1.0 are different composites over
   every material, and one of them is what Apple ships.
3. **The ladder.** vitrea carries the iOS numbers. The macOS ones are in the table above. Which
   ladder a web runtime replicating macOS should publish is G2's decision, and it is a decision
   rather than a lookup, because vitrea's ink was neutral-but-not-black and Apple's is black.
4. **Whether the per-surface secondary solve still binds.** It was solved against `#1c1c1e`; pure
   black at the same alpha has more contrast, so the solve's output moves and the ~13 ink assertions
   move with it. The *mechanism* is not in question — see below.
5. **Whether the operator's selector replaces `foregroundCrossover`'s current role or sits beside
   it.** Today the crossover picks which of two inks to publish; under the operator it picks which
   of two operators to apply. Those are the same decision, and G2 should make them one thing rather
   than two that can disagree.

*What G2 may keep:*

- **The four token names** — X4 binds this and the operator does not touch it.
- **The publishing mechanism**: four declarations and never an inline `color` (root Decision Log
  #34(c)), which §5.136 §4 now lets vitrea cite Apple for — Apple installs nothing over an
  app-authored colour.
- **The per-surface secondary solve as a mechanism** (Decision Log 9). Its inputs move; its shape —
  bisect the alpha that holds the floor over every candidate composite, collapse onto the primary
  when none does — does not.
- **The accessibility collapses**: `CanvasText` under forced colours, `light-dark(#000, #fff)` under
  increased contrast. Both are policy outcomes that the operator does not reach.
- **X9's presence scaling as vitrea's own design decision.** §5.133 §9 stands: all 57 G0 dumps are
  at full presence, nothing in Apple's configuration bears on presence, and the labelled probe adds
  nothing to that.

**One published claim that does not survive contact, flagged for G3.** WWDC 2018 session 210 says
that under the *legacy* vibrant appearances an opaque black glyph becomes fully transparent in dark
mode and an opaque white one does in light. Under this matrix the opposite happens — black in light
stays black, white in dark stays white. The legacy vibrancy (colour-burn/dodge) and the Liquid Glass
`vibrantColorMatrix` path are different operators, and G2 must not import the 2018 mental model.

## 6. The open half: the surface operator's selector

**Not this gate's, and this gate does not fit it.** §5.136 §5 refuted both of §5.133 §8's candidate
selectors and left two explanations fitting equally well, because the corpora differ in two axes:
G0 is 1x through a key window, the probe is 2x through a non-key one.

**§1 fact 4 adds a third explanation, and it is the one this evidence most supports.** The layer the
surface operator sits on has `opacity` **0** on all 50 probe occurrences and **1** on all 58 of
G0's. A matrix on a layer that draws nothing has no pixel consequence, and there is no reason for
SwiftUI to keep a dormant layer's configuration correct. So "one operator per scheme at 2x" may not
be a selector reading at all — it may be the configuration of a switched-off layer. That is a
different claim from "the recede collapses the selector", and both are different from "the selector
depends on scale".

**The reading the 1x both-pose pass must produce.** It is the same `dump-layers` pass the runbook
schedules against the bed's 1x pass — the active pose is `dump-layers`' existing path, the recede is
the same `.accessory` launch the capture uses, each dump recording its own `isKeyWindow`. Every
dump must additionally record the **`opacity` of the layer the matrix sits on**, which the reader
now emits as `layerOpacity`. Four outcomes, and each chooses:

| at 1x, **key** | at 1x, **non-key** | what it says |
| --- | --- | --- |
| highlight opacity 1, §5.133's tone-and-span selector reproduces | highlight opacity 0, one operator per scheme | **the recede collapses it** — and, if the collapse is only on an invisible layer, the selector was never refuted at all. Scale is not the axis. |
| highlight opacity 1, one operator per scheme | either | **scale is the axis**: the 1x key corpus at 2x-like behaviour would mean G0's own reading was the scale-specific one |
| highlight opacity 1, tone-and-span reproduces | highlight opacity **1**, one operator per scheme | **the recede genuinely changes the selector on a layer that still draws** — the only outcome in which "the recede collapses the selector" is a claim about pixels |
| highlight opacity 0 in the key pose | — | the instrument or the pose is not what either corpus recorded; stop and re-read before fitting anything |

Until that pass is read, **no selector for the surface operator is declared**, and W27e G2 must not
ship one. The label operator does not depend on it: the label's own layer is `opacity` 1 in both
schemes and both corpora, and its selector is the colour scheme with 24 of 24 agreeing.

## 7. Limits

- **The label corpus is fully read.** All 26 labelled dumps were read in §5.136 §4 and no partition
  is drawn after the fact. The operator stands on 26 of 26 with nothing held back, and that is a
  limit of the evidence rather than a spend.
- **One engine, one machine, flat slabs rather than glyphs.** Gecko and WebKit render
  `backdrop-filter` as a no-op in every automatable capture path, so §4's readings are Chromium's.
  Antialiased glyph edges are covered only by the alpha rows of the bench, not by real type.
- **`plus-darker` is untestable in this engine**, so half of §4's C column is arithmetic.
- **The clamp's position relative to the backdrop combination is unverified** (§2.5), and no native
  pixel can settle it.
- **Everything in §2.2 below Apple's two quotes is third-party recovery from shipped binaries**, not
  Apple's words, and was not disassembled here.
- **Nothing here measures Apple's material.** No pixel was captured, no fixture, profile, golden,
  `scenes.json` entry or canonical matrix row moved, and no file under `packages/*/src` changed.
