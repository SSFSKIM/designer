# W27e G1 — the label operator, declared before the reading (2026-09-12)

Executes W27's child **W27e gate G1** (`docs/doperpowers/specs/2026-09-10-w27-coverage-wave.md`,
§Children), the §Design clause *Where each feature lives* (binding: the operator on vitrea's own
controls, the token elsewhere), Decision Logs 12 and 13, and contracts **X1** (the tier boundary),
**X2** (public surface is a semver event) and **X4** (the foreground token vocabulary). It consumes
claims **§5.133** (G0's read of the surface operators and the composite probe) and **§5.136 §4–§5**
(the labelled probe). It will be recorded as claims **§5.137**.

**This file is committed before this gate reads the probe corpus and before it runs anything in a
browser.** Head at writing: `0e8cf995` (`main`), branch `worktree-agent-a9221cd601ef2087b`.

## 0. What this gate is, and what it is not

The gate as chartered asks for "one operator with the material's own level as input reproducing
every dump's matrix within a declared tolerance, holdout dumps read once". **The probe moved that
premise and the fit is gone.** §5.136 §4 found the label operator already solved in Apple's own
coefficients: two matrices selected by colour scheme alone, identity with offset −1 in light and
+1 with alpha ×0.95 in dark, chroma gain 1, no luma term, zero residual on 24 of 26 labelled dumps,
`inputBackdropAware` 1 and `inputClamp` 1, and the two labels that name their own colour carrying
no filter at all. There is no coefficient left to fit and no residual left to bound.

So this gate produces the operator **as a function vitrea can evaluate**: its semantics settled
against the dumps' complete layer and filter configuration and against Apple's own documentation of
vibrancy compositing, its form on each of vitrea's two tiers stated, and a tolerance declared from a
browser measurement. **Nothing is implemented at this gate.** No file under `packages/*/src`
changes. No material profile, fixture, renderer golden, `scenes.json` entry or canonical
`results/matrix.json` row moves. Nothing is captured from Apple; the one measurement here is taken
in Chromium against arithmetic, not against a native pixel.

Evidence directory: **`packages/calibration/results/2026-09-12-w27e-g1/`**. Everything this gate
reads, computes or measures lands there.

## 1. The honesty position on the corpus, stated before it is re-read

**All 26 labelled dumps were read in §5.136 §4**, when the operator was identified. No unread label
dump remains, so this gate **declares no holdout partition on the label corpus**. Naming a partition
now would be drawing it after the read, which is the move the wave's own discipline exists to
refuse. The label operator therefore stands on 26 of 26 read dumps with nothing held back, and that
is a limit of the evidence, recorded here rather than dressed as a spend.

The one unspent check that could exist on this path is named in §5 below and is not this gate's.

### 1.1 What §5.136 §4 read

Per labelled dump: the presence of a `vibrantColorMatrix` on the `CGDrawingLayer` inside the
`glassEffect`; that filter's `inputColorMatrix` float32 values; `inputBackdropAware`, `inputClamp`
and `inputClampPreserveHue` on it; the dump's `colorScheme`, `background`, `component`,
`backingScaleFactor`, `tint` and `isKeyWindow`; and the probe scene's declared label
(`label.srgb` set on the two `-label-hot` scenes, unset elsewhere). §5.136 §5 additionally read the
surface highlight layer's matrix on all 50 dumps.

### 1.2 What this gate will read that §5.136 §4 did not — declared before reading

1. **Every field the dumper emits on the label's `CGDrawingLayer`**, and in particular the
   *absence* of `compositingFilter` and `backgroundFilters`. `Sources/LayerDump.swift` reads both
   (lines 399–407) and emits them when non-nil, so their absence in a dump is a measured negative
   and not a gap in the instrument.
2. **The length and contents of the label layer's whole `filters` array**, not only the
   `vibrantColorMatrix` entry, so that "one filter and nothing else" is read rather than assumed.
3. **Sublayer order** inside the `glassEffect`'s `SwiftUI.SDFLayer` — where the label's content sits
   relative to the material's `CABackdropLayer @0`, the `SDFPortalLayer @1` and the highlight
   `CASDFLayer @2` — together with each portal layer's `sourceLayer`, `hidesSourceLayer`,
   `matchesOpacity` and `sourceLayerOpacityScale`. `layer.sublayers` is CoreAnimation paint order,
   and `describeLayer` snapshots it unmodified, so the array index is the compositing order.
4. **`opacity`, `masksToBounds`, `isHidden`, `frame` and `bounds`** on each of those layers.
5. **The `CABackdropLayer @0`'s `glassBackground` filter inputs and its own `properties`** —
   specifically `allowsFilteredLuma`, `groupName`, `groupNamespace`, `lumaSubrect` and
   `lumaUpdateRate` — because a backdrop *group* is the only object in the tree a backdrop-aware
   filter could resolve against, and whether one exists is a fact about the stack.
6. **The `label` block of the dump envelope** on all 50 dumps, to confirm which scenes declare a
   colour and which do not.

**A correction to the order, recorded rather than hidden.** A structural orientation pass over
**one** light dump (`light/dark-solid__capsule-button__rest-label.json`) was taken before this file
was committed, to find out what the tree even looks like. It saw items 1–5 above on that one dump:
no `compositingFilter`, a single-entry `filters` array, the label's content layer at sublayer index
0 of the `SDFLayer` with the material container at index 1, `SDFPortalLayer @1` naming that content
layer as its `sourceLayer` with `hidesSourceLayer: 1`, the highlight `@2` above it at `opacity: 0`
on that cell, and a `CABackdropLayer` carrying `groupName: "SwiftUI:32.00.0"` with
`allowsFilteredLuma: 1`. That is stated here so nothing below is presented as pre-declared when it
was not. Nothing numeric is fitted to it, no bound is drawn on it, and the corpus-wide read of items
1–6 across all 50 dumps happens after this commit.

## 2. The hypothesis, and what would refute it

A unit offset over a backdrop-aware, clamped input is on its face the classic vibrancy blend:
plus-darker in light, `out = max(0, backdrop + ink − 1)`, and plus-lighter in dark,
`out = min(1, backdrop + 0.95·ink)`. **That is this gate's hypothesis, not its answer.** It will be
held against:

- the complete layer and filter configuration named in §1.2, across all 26 labelled dumps;
- Apple's public documentation of vibrancy compositing (the AppKit vibrant appearances and the
  `plusDarker`/`plusLighter` pairing, `CGBlendMode`'s printed formulas, and whatever the Liquid
  Glass material documentation says about a label's colour);
- what is attested about the private `CAFilter` `vibrantColorMatrix` and its `inputBackdropAware`
  input, with third-party reverse engineering marked as such.

**What would refute it, and what that costs.** Any of the following is recorded as a contradiction
and the reading that fits recorded instead:

- a `compositingFilter` or a `backgroundFilters` entry on any label layer, or a second filter in its
  `filters` array — the operator would then not be the matrix alone;
- the label's content not composited above the material's `@0` output in some dump, which would
  leave "which buffer" without a single answer;
- documentation or attested behaviour that puts the clamp **after** a backdrop combination rather
  than on the matrix output, or that makes `inputBackdropAware` mean something other than a
  combination with the buffer beneath.

**A limit this gate expects to have to state, and states in advance so it cannot be quietly
skipped.** A ±1 offset saturates the unit interval under a `[0, 1]` clamp. If the clamp lands on the
matrix output, the operator is constant; if it lands after an addition of the buffer beneath, it is
not. Those two readings may agree on the *automatic* ink (the only ink Apple ever puts through this
filter) and disagree on any other. Where they agree the choice is free; where they disagree, **no
native pixel can arbitrate it, because the no-text fixture rule stands with three locks and there
is no native label fixture nor can there be one.** If that is where the evidence lands, this gate
names the decidable part, names the undecidable part, chooses on the documentation, and records the
alternative with the size of the disagreement rather than claiming a measurement it does not have.

## 3. What will be measured in a browser, and the tolerance declared before it

The measurement proves the **analytic form** of the operator on each tier against what Chromium
actually composites, using the machinery §5.133 §5 built: real Chromium (`channel: "chromium"`), a
compositor screenshot and never a canvas readback, `feColorMatrix` at
`color-interpolation-filters: sRGB` (the SVG default `linearRGB` is a different operator and is
load-bearing), plus whatever blend the settled semantics requires.

Two arms:

- **per-pixel arm** — the operator expressed the way a `gpu-texture` group can run it: the ink under
  the colour transform, composited against a known material by the blend the semantics names;
- **folded arm** — the same operator evaluated on the CPU into a single sRGB ink and painted
  source-over, which is what a `css-backdrop` group must do, because §5.133 §5 measured that a
  `mix-blend-mode` inside the host collapses `backdrop-filter` sampling for a group whose proxy is
  outside that element's subtree.

**The tolerance is declared here, before the first capture: every channel of every case must agree
with the closed-form arithmetic to within 1 code value of 255, and the maximum observed difference
is what gets published as the operator's tolerance.** Zero is expected wherever no blend is
involved; §5.133 §5 read 0.0 against hand computation on every opaque case of the surface operator.

**What that tolerance bounds, said plainly.** It bounds *the analytic operator against the browser's
own composite of it* — that vitrea's closed form is the same arithmetic the compositor performs. It
is **not** a bound between vitrea and macOS. There is no native pixel fixture for a label and there
cannot be one, so no number this gate publishes is a fidelity claim against Apple. The fidelity
claim available here is a configuration claim: Apple's coefficients, read exactly, with zero
residual, on 26 dumps.

## 4. The automatic label colour

S284 says the label becomes vibrant based on its `textColor`, so the operator's input level is part
of the answer. A `CGDrawingLayer` carries rendered content and no colour property, so **the dumps
can attest which scenes declare a colour and cannot attest what level an undeclared one resolves
to.** Declared in advance: where the level comes from documentation rather than from the corpus it
is published as documentation-sourced and named as such, never as a measured level, and the
relation to the four ink levels W27a published (primary, secondary, tertiary, quaternary; Decision
Log 9 solved secondary per surface) is stated as what G2 must re-derive and what it may keep.

## 5. The open half this gate does not close: the surface operator's selector

**The surface operator's selector is not this gate's to fit, and this gate does not fit it.**
§5.136 §5 showed that the 1x corpus is key-window and the 2x corpus is non-key, so scale and window
pose are confounded across two axes, not one: "the selector depends on scale" and "§5.133's
tone-and-span selector holds in the active pose and the recede collapses it to one operator per
scheme" fit those rows equally well. The separating pass — `dump-layers` at 1x **in both poses** —
is scheduled inside the user's 26.5 sitting. This gate records it as W27e G1's open half and writes
down the exact reading that pass must produce to choose between the two, so the choice is made by
the data and not by whoever reads it next.

## 6. What would stop this gate

Per item; nothing is published past a stop.

- **S1 — the configuration contradicts the semantics.** Any label layer carrying a
  `compositingFilter`, a `backgroundFilters` entry, or more than one filter. The operator would not
  be the matrix alone and the semantics below it would be wrong.
- **S2 — the order is not uniform.** The label's content not composited above the material's `@0`
  output in every labelled dump.
- **S3 — §5.136 §4's reading does not reproduce.** Any of the 24 matrices differing from the two
  §5.136 §4 published, or any label layer's `inputBackdropAware`, `inputClamp` or
  `inputClampPreserveHue` differing from what it recorded. The gate stops rather than building on a
  reading it cannot reproduce; the committed numbers are not rewritten, the disagreement is recorded
  beside them.
- **S4 — the analytic form misses the browser.** Any channel of any case differing from the closed
  form by more than 1 code value. No tolerance is declared from a form that failed; the form is
  wrong and the gate stops.
- **S5 — the browser is not the declared instrument.** A run that is not real Chromium, or a
  `gpu-texture` case resolving onto a fallback adapter.
- **S6 — the no-text fixture rule.** Any scene declaring a label reaching `scenes.json`, any pixel
  written under a fixture root, or any native capture taken by this gate. The rule stands with the
  three locks §5.136 §4 records and this gate adds nothing to `scenes.json`.
- **S7 — scope.** Any change under `packages/*/src`, or to a material profile, fixture, renderer
  golden or canonical matrix row. This gate states the operator; G2 implements it.

## 7. What lands

1. This declaration, committed first.
2. The corpus read of §1.2 across all 50 dumps, as JSON plus its reader.
3. The settled semantics, with the contradictions found (if any) and the alternatives that survive.
4. The two tiers' functions, stated with their inputs, their output, and the CSS fold's information
   loss named.
5. The browser proof and the tolerance measured against the declaration in §3.
6. The automatic label colour, and what G2 must re-derive against W27a's four levels.
7. The open half of §5, with the reading the 1x both-pose pass must produce.
8. A pure evaluator in `packages/calibration/scripts/vibrancy.ts` with a vitest pinning its
   coefficients to the committed dumps.
9. Claims §5.137, the wave's W27e Status line and Tracking row, a Revision Notes entry, and any gap
   to macOS in the wave's Deferred list or `specs/tech-debt-tracker.md`.
