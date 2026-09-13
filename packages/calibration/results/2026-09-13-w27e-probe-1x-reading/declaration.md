# W27e G2, the surface operator's pose reading: declared before the corpus was read (2026-09-13)

**Gate:** W27 coverage wave, child W27e gate G2 (§Children), Decision Log 15 (c) — the selector
decision held behind the 1x both-pose pass; claims §5.138, reserved. Consumes §5.133, §5.136 §4–§5
and §5.137 §1–§2 and §5–§6. **This gate fits nothing, captures nothing from Apple, adopts no bound
and declares no selector.** It reads one corpus that is already in git and says which of §5.137 §6's
four outcomes the fields show. No file under `packages/*/src` changes, and no material profile,
fixture, renderer golden, `scenes.json` entry or canonical `results/matrix.json` row moves.

This file is committed **before** the corpus is read, and is not edited afterwards. What the reading
finds goes in `reading.md` beside it and in claims §5.138.

## 0. The orientation pass that preceded this declaration, disclosed

Three things were looked at before this was written, and they are named here rather than left for a
reader to discover, in the discipline §5.137 §1 set for itself. **(i)** `index.md` of the corpus,
which is its author's own statement of the three arms and their poses. **(ii)** The **top-level**
fields of exactly three dumps — `active/light`, `recede/light` and `policy-only/dark`, all the
`checkerboard__rrect-md__rest-label` scene — to learn the names the harness writes for the two new
fields (`appIsActive`, `activationPolicy`) and to see that the pre-sitting dumps do not carry them
at all. No layer tree, no filter and no matrix was read. **(iii)** That every background the corpus
names has a committed `@1x.png` raster, which is a precondition of the reader running at all.

## 1. What will be read, field by field

From the 150 dumps of `results/2026-09-12-w27e-probe-1x/`, three arms × two schemes × 25 scenes:

*Per dump, top level.* `scene`, `background`, `component`, `state`, `tint`, `colorScheme`, `a11y`,
`backingScaleFactor`, `settleSeconds`, `os`, `canvas`, `label` (`text`, `fontSize`, `srgb`), and the
three pose fields: **`isKeyWindow`** on all 150, **`appIsActive`** and **`activationPolicy`** on the
50 `recede/` dumps, which are the only ones whose run had the fields. Their absence elsewhere is
recorded as absence and never as a value.

*Per layer, in the committed tree.* `class`, `name`, `frame`, `bounds`, `cornerRadius`,
**`opacity`**, `sublayers`; `properties.effect.class`, which is the tree's own statement of what a
layer draws; and on the surface's `CABackdropLayer`, `properties.tracksLuma`, `marginWidth` and
`scale`. From each `filters[]` entry: `description`, and where it is `vibrantColorMatrix`, the
inputs `inputColorMatrix.float32` (twenty floats), `inputBackdropAware`, `inputClamp`,
`inputClampPreserveHue` and the filter's own `properties.inputKeys`. From the `glassBackground`
filter on that backdrop layer: `inputFaceColorMatrixBlack`, `inputFaceColorMatrixWhite`,
`inputFaceColorMatrixFillColor`, `inputShadowColorMatrixFillColor`, `inputClamp` and
`inputClampPreserveHue`, because §5.133 §4 found the body's own adapted state co-varies with the
operator and the co-variation is the finding.

*Derived, from evidence that is not this corpus.* The backdrop tone under each cell, as
§5.133 §4 defines it — the mean linear luminance of the committed `@1x` background fixture over the
**declared** component region, through the harness's own `decodePng` / `componentRegion` /
`interiorLevel`; the declared span, cross-checked across every committed scene spec that declares
the component; and vitrea's own `backdropToneAdaptation(tone, sizeThickness(span))` at the shipped
material profile, recorded as a prediction beside the reading and never as a fit.

*What will NOT be read.* No cell of `results/matrix.json`: no single profile key describes a corpus
spanning both schemes and three poses, and a cell from another configuration would be a wrong number
rather than a missing one, so `material.interiorMeanBackdrop` and `shadow.backdropMeanLuminance` stay
unavailable here exactly as they do on the 2x probe. No pixel is decoded from anything but the
background rasters above. Nothing under the dump tree is edited, and the reader writes only into
`results/2026-09-13-w27e-probe-1x-reading/`, create-only.

## 2. How the corpus partitions, before anything is read

Per `index.md`, and to be verified rather than assumed (stop S3 below):

- **the ACTIVE pose at 1x** = `active/dark` (25) + the `active/light` dumps that record
  `isKeyWindow: true` (9 by the index) + `policy-only/light` and `policy-only/dark` (50) = **84**;
- **the RECEDE at 1x** = `recede/light` + `recede/dark` (50), each with `isKeyWindow: false`,
  `appIsActive: false`, `activationPolicy: "accessory"`;
- **a third state** = the `active/light` dumps that record `isKeyWindow: false` (16 by the index),
  regular policy with the application still active, which is not the mechanism the capture uses and
  is read on its own and never pooled into either pose.

`policy-only/` is an ACTIVE-pose arm under an accessory policy and is named for what it is: an
`.accessory` application that calls `activate` becomes active and its key-capable window becomes
key. If its dumps do not read `isKeyWindow: true`, stop S3 fires.

## 3. The four outcomes of §5.137 §6, in these fields

The quantity that decides them is the pair (`layerOpacity` on the `CASDFKeyFillHighlightEffect`
layer, the partition of `operatorId` over the cells) read in each pose. "§5.133's tone-and-span
selector reproduces" means exactly this, on the LIGHT scheme where G0 read it: the high-gain
operator (m 3.0 / a 1.35 / b 0.15) on `dark-solid__capsule-button__rest` and
`impulse__capsule-button__rest` and the default operator (m 1.5 / a 0.1 / b 0.9) on every other light
cell, with `backdropToneAdaptation` 1.0 on the switching cells and ≤ 0.0077 on the rest. "One
operator per scheme" means every cell of a scheme carries one matrix, whatever its tone and span.

| # | active pose (84) | recede (50) | what the reading chooses |
| ---: | --- | --- | --- |
| **A** | opacity **1**, tone-and-span reproduces | opacity **0**, one operator per scheme | **the recede collapses it, and the collapse is on an invisible layer** — the selector was never refuted, the 2x corpus's "one per scheme" is a switched-off layer's leftover configuration, and scale is not the axis |
| **B** | opacity **1**, one operator per scheme | either | **scale is the axis** — the 2x reading reproduces at 1x in the active pose |
| **C** | opacity **1**, tone-and-span reproduces | opacity **1**, one operator per scheme | **the recede changes the selector on a layer that still draws** — the only outcome in which the collapse is a claim about pixels |
| **D** | opacity **0** anywhere in the active pose | — | **stop**: the pose or the instrument is not what either corpus recorded, and nothing is fitted or declared |

Outcome A is the one the §5.137 §1 finding predicts; it is written here with the others and carries
no privilege. If the fields fit none of the four — the active pose reproducing neither §5.133's
partition nor one-per-scheme, the three arms of one pose disagreeing with each other, or the recede
carrying a partition of its own — the reading says what the fields do show and resolves the four
outcomes as "none", rather than forcing the nearest one.

The reading is per scheme and per arm throughout, because `active/` and `policy-only/` reach the
active pose by different mechanisms and agreeing is a finding rather than an assumption.

## 4. The other three questions, and what would count as an answer

**The LABEL operator.** Whether the scheme-only pair of §5.136 §4 still stands at 1x in both poses:
the light matrix `[1,0,0,0,−1, …]` and the dark `[…, 0.949999988079071, 0]`, chroma gain 1, no luma
term, zero residual, `inputBackdropAware` 1 and `inputClamp` 1 on every labelled dump that took the
automatic colour; the two `-label-hot` scenes' label layers present with an empty filter list in both
schemes; and the label layer's own `opacity`. **Any change with pose or scale is the finding** and is
reported whether or not it changes the operator — a third matrix, a matrix moving between schemes, a
labelled dump losing its operator, a `-label-hot` dump gaining one, or a label layer at opacity 0.

**The author-tint colorize matrices**, for completeness: how many occurrences sit on a
`CASDFGradientEffect` layer, their decomposition (`m` ≈ 0, output `g_i·Y + b_i`), their
`inputBackdropAware`, and their layer opacity in each pose.

**`active/light`'s non-key dumps with the application active**, read on their own: their count, the
scene ids they cover, what the surface operator and its layer opacity read on them, what the label
reads, and whether they look like the active pose, like the recede, or like neither. They are the one
state in the corpus that no prior reading has seen, and they are reported as a state rather than
folded into a pose.

## 5. What would stop the reading

Each of these refuses the reading rather than qualifying it. Nothing is published under §5.138 on any
of them except the stop itself.

- **S1 — the corpus is not what it says.** Any arm that does not hold 25 dumps per scheme, a dump
  read twice, or a dump that is not valid JSON with a `view.layer`.
- **S2 — the configuration is not one.** Any dump whose `backingScaleFactor` is not 1, whose `os` is
  not the sitting's `Version 26.5.2 (Build 25F84)`, whose `settleSeconds` is not 8 or whose `a11y` is
  not `standard`. The whole point of this corpus is that scale and accessibility are held fixed so
  the pose is the only axis; a dump that breaks that re-confounds it.
- **S3 — the pose tallies disagree with `index.md`.** `active/light` 9 key and 16 not key,
  `active/dark` 25 key, `policy-only/*` 50 key, `recede/*` 50 with `isKeyWindow` false, `appIsActive`
  false and `activationPolicy` `accessory`. A disagreement means the index and the dumps are
  describing different runs, and the pose axis is unreadable until it is resolved.
- **S4 — §5.137 §6's own fourth row, inherited.** A `CASDFKeyFillHighlightEffect` layer at
  `opacity` 0 in the ACTIVE pose. Stop and re-read before fitting; declare nothing.
- **S5 — the tree is not the tree the reader knows.** A scene declared in no committed spec, two
  specs disagreeing on a component's span, a `vibrantColorMatrix` with no decoded matrix, an
  occurrence whose carrying layer resolves to no glass surface, or a labelled dump whose tree holds
  other than exactly one glass surface.
- **S6 — a family that is not one of the three.** Any occurrence classified `unclassified`, or any
  highlight or tint matrix whose residual against `out = m·c + g⊙Y(c) + b` exceeds **2.5e-4**, which
  is the worst §5.133 §3 recorded. That is a fourth operator family and it is reported as one rather
  than folded into a four-outcome table that has no room for it.
- **S7 — a committed reading moves.** Re-running the reader over the G0 corpus must still give 57
  dumps, 60 occurrences, 4 distinct matrices, 58 on the highlight at opacity 1; over the 2x probe, 50
  dumps, 24 labels in 2 matrices, 50 highlights at opacity 0. If extending the reader moves any of
  them, the extension changed the reading and the reading is void.
- **S8 — the evidence is edited.** Anything under
  `results/2026-09-11-w27e-g0-vibrancy/`, `results/2026-09-11-w27e-probe/` or
  `results/2026-09-12-w27e-probe-1x/` showing as modified in `git status`. The dumps and both
  committed tables are read-only to this gate; new readings are written beside them.

## 6. What this gate may and may not conclude

It may say which outcome the fields show, and it may recommend. It **may not declare the surface
operator's selector**: §5.137 §6 holds that behind this reading and Decision Log 15 (c) reserves the
decision — whether the operator's scheme-only selection replaces `foregroundCrossover`'s role, sits
beside it, or something else — for the user. The recommendation at the end of §5.138 is a
recommendation, with the evidence for each option, and the decision stays the user's.
