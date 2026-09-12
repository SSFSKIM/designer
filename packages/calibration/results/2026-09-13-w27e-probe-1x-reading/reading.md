# W27e G2: the 1x both-pose reading — what the pose moves, and what it does not (2026-09-13)

The prose working behind claims §5.138. What was declared before any of this was read is
`declaration.md`; the reader's own record is `table.json` / `table.md`
(`scripts/vibrancy.ts --corpus probe-1x`); the independent second pass over the same raw dumps is
`reading.py` / `reading.json`. Nothing was captured, nothing was fitted, no bound was adopted and no
selector is declared — Decision Log 15 (c) is the user's.

Operator ids below are `table.json`'s. **1** is §5.133's default surface operator (m 1.5, a 0.1,
b 0.9) and **3** its high-gain one (m 3.0, a 1.35, b 0.15); **0** is §5.136 §4's darkening label
matrix (offset −1) and **2** its lightening one (offset +1, alpha ×0.95); **4**–**7** are the author
tint's. `reading.py` numbers its own classes independently and the two agree cell for cell.

## 0. The stops, cleared before anything was concluded

`declaration.md` §5 declares eight. **S1**: 25 dumps in each of the six arm-and-scheme directories,
150 in all, each read once. **S2**: one configuration — `backingScaleFactor` 1 on all 150, `a11y`
`standard`, `settleSeconds` 8, `os` `Version 26.5.2 (Build 25F84)`, state `rest`. **S3**: the pose
tallies are `index.md`'s exactly — `active/light` **9 key and 16 not key**, `active/dark` 25 key,
`policy-only/*` 25 key each, `recede/*` 25 each with `isKeyWindow` false, `appIsActive` false and
`activationPolicy` `accessory`; the other four arms record neither of the two new fields, which is
reported as "not recorded" and never as false. **S4**, §5.137 §6's own inherited stop: the highlight
layer's `opacity` is **1 on all 84 key dumps**, so it does not fire. **S5**: no span disagreement
across the committed specs, every tree one glass surface, every `vibrantColorMatrix` decoded. **S6**:
no occurrence is unclassified and the worst residual against `out = m·c + g⊙Y(c) + b` is
**2.489e-4**, inside §5.133 §3's own 2.5e-4. **S7**: re-read through the extended reader, the G0
corpus is still 57 dumps / 60 occurrences / 4 matrices / 58 highlights at opacity 1, and the 2x probe
still 50 dumps / 24 labels in 2 matrices / 50 highlights at opacity 0. **S8**: nothing under any dump
tree was edited.

One thing the harness's own logs say that the dumps contradict, resolved rather than left: the
`policy-only` logs' header line reads `isKeyWindow: false, NSApp.isActive: false` while all 50 of
that arm's dumps record `isKeyWindow: true`. The header is printed once, before the run loop is up;
`isKeyWindow` is sampled per dump after the settle, immediately before the record is written
(`Sources/main.swift`). The per-dump field is the one that describes the dump, and `active/light`'s
own 9-then-16 split is internal proof that it is sampled per scene rather than once.

## 1. What the pose moves

Three things, and each moves with **key**, not with the application's activation:

| field | 84 key dumps | 66 non-key dumps |
| --- | --- | --- |
| the highlight layer's `opacity` (`CASDFKeyFillHighlightEffect`) | **1**, all 84 | **0**, all 66 |
| the backdrop layer's `marginWidth` | 8.8 / 9.6 / 12.8 / 58 / 68 by component | **0**, all 66 |
| the author tint's `vibrantColorMatrix` | a rank-one colorize, chroma present | **achromatic**, hue gone |

The 66 non-key dumps are the 50 of the `recede` arm — `.accessory`, never activated, `appIsActive`
false — **and the 16 of `active/light` that lost key while the application stayed active under the
regular policy**. On all three fields the two are indistinguishable. §5.128's receded bright rim is
the first row of that table read in Apple's configuration, and §5.130's "an author tint loses its hue
entirely while its darkening stays" is the third.

## 2. What the pose does NOT move: the surface operator's selection

Both operators appear in **both** schemes and in **every** window state. Per arm and pose, on 25
scenes each:

| group | default (1) | high-gain (3) |
| --- | ---: | ---: |
| `active/light` key (9 dumps) | 5 | 4 |
| `policy-only/light` key | 18 | 7 |
| `active/light` non-key (16 dumps) | 14 | 2 |
| `recede/light` | 17 | 8 |
| `active/dark` key | 2 | 23 |
| `policy-only/dark` key | 1 | 24 |
| `recede/dark` | 2 | 23 |

**Per scene and scheme, 47 of the 50 cells carry the same operator through every window state they
were dumped in.** Three do not, and no one of the three is aligned with the pose:

- `light dark-solid__capsule-button__rest` — default in **both** key arms, high-gain in the recede;
- `light dark-solid__rrect-48__rest-label` — default in `active`, high-gain in `policy-only` (**the
  same pose, two arms**) and in the recede;
- `dark light-solid__capsule-button__rest` — high-gain in `policy-only` only; `active` and `recede`
  both read the default.

Two of the three put two arms of the *same* pose on opposite sides, so the third is not evidence of a
pose effect either. They are run-to-run, and §7 below says what that costs.

## 3. The law the corpus does show, on 258 of 258 occurrences

**The surface's vibrancy operator is a function of the body's own adapted state, exactly.** On every
one of this corpus's 150 highlight occurrences, the high-gain operator sits on a surface whose
`inputFaceColorMatrixFillColor` is black and whose `inputShadowColorMatrixFillColor` is `nil`, and
the default operator on a surface whose fill is white and whose shadow fill is set — 150 of 150 on
both keys, with zero exceptions in three window states and two schemes. G0's corpus reads **58 of
58** through the reader, which resolves each occurrence's own surface by an ancestor walk; this
pass's single-surface walk covers 56 of those 58 and excludes `photo__glass-over-glass__rest` by
name, reading 56 of 56. The 2x probe reads **50 of 50**. §5.133 §4 saw this co-variation on two
cells and called it agreement; at **258** occurrences
over three corpora, three window states, two schemes and two scales it is the law. **The vibrancy
operator does not have a selector of its own: it is the glass's own adaptation, read out.**

What selects the body's state is the backdrop, with a **scheme-dependent** threshold — which is why
the 2x corpus looked scheme-selected. Scored against "each scheme sits at its base state (default in
light, high-gain in dark) and adapts to the other when the backdrop goes far enough the other way",
**146 of 150 rows agree** and the four exceptions are §2's three cells. In light the adapting
backgrounds are `dark-solid` (linear 0.011711) and `impulse` (0.003284) and only below a span; in
dark it is `light-solid` (0.890969), at every span the corpus holds.

Two brackets this corpus narrows, both stated as intervals and neither fitted:

- **the light-scheme span gate.** At `dark-solid`'s tone the surface adapts at declared span 44, 48
  and 64 and does not at 80 or 96, so the gate lies in **(64, 80]** — where §5.133 §4 could only say
  "somewhere in (44, 96)". vitrea's own `backdropToneAdaptation(tone, sizeThickness(span))` at the
  shipped profile reads **0.5338** at span 64 and **0.0029** at span 80: its fitted knee is already
  inside Apple's interval. Apple's own `tracksLuma` is 1 at 44/48/64 and 0 at 80/96 and brackets it
  identically — **at both scales**, which matters in §4.
- **the dark-scheme tone threshold.** The dark body adapts away from high-gain at tone 0.890969 and
  not at 0.5 (`checkerboard`), so it lies in **(0.5, 0.890969]** — a wide bracket with no cell inside
  it. vitrea has no term for this at all: `backdropToneAdaptation` reads 0 on every dark cell that
  switches, so the predicate that separates the light scheme 72 rows out of 75 separates nothing in
  dark.

## 4. So what the 2x corpus was: the scale, and nothing else left

§5.136 §5 could not tell a scale dependence from a pose collapse because the two corpora differed in
both. The pose is now controlled from both sides:

- the 2x corpus is non-key on all 50, `marginWidth` 0 on all 50, highlight opacity 0 on all 50 — the
  same receded configuration this corpus reaches at 1x;
- at 1x, **both** non-key states (accessory-and-inactive, and regular-and-active) give the same
  reading, so whichever of them the 2x run was in is covered.

Against `recede/*`, scene for scene, the 2x corpus differs on **10 of 50** surface cells and **5 of
24** labels, and every difference is in one direction: at 2x nothing adapts. In light the eight are
the `dark-solid` 44/48/64 and `impulse` families; in dark the two are `light-solid`. At 2x every
light cell reads a white face fill and every dark cell a black one — **each scheme sits at its base
state and no cell adapts**, which is exactly what "one operator per scheme" was.

**Scale is the axis.** The mechanism is not readable from the configuration, and one candidate is
refuted here rather than left standing: `tracksLuma` is 1 at declared span 44/48/64 and 0 at 80/96 at
**both** scales, so Apple's own size flag is computed in points and a "the size gate is in device
pixels" explanation does not survive. What is left is that something else in the adaptation reads the
backing scale. The experiment that would say what: a 2x `dark-solid` ladder at declared span 22 / 32
/ 44 — if the adaptation returns at the smaller declared spans the gate is in device pixels after all
and `tracksLuma` is not what gates it; if it never returns, the scale suppresses the adaptation by
some other route.

## 5. §5.137 §6's four outcomes, resolved

| # | what it required | what the corpus reads |
| ---: | --- | --- |
| **A** the recede collapses it | active opacity 1 **and** tone-and-span reproduces; recede opacity 0 **and** one operator per scheme | first column **holds**, second **fails**: the recede is opacity 0 but carries the same partition, 17/8 in light and 2/23 in dark |
| **B** scale is the axis | active pose: one operator per scheme | **fails as written** — the active pose at 1x carries both operators in both schemes |
| **C** the recede changes the selector on a layer that still draws | recede opacity **1** | **fails**: recede opacity is 0 on all 50 |
| **D** stop | opacity 0 in the key pose | **does not fire**: opacity 1 on all 84 key dumps |

**None of the four fits, and what fits is a fifth reading.** The pose does not select the operator at
all. It switches the layer the operator sits on off (opacity 1 → 0) and strips the tint's hue, and it
does that with the loss of key rather than with the application's deactivation. The operator's
selection is the glass's own adaptation (§3), it survives both poses at 1x, and the 2x corpus's
"one operator per scheme" is the scale suppressing the adaptation (§4).

Outcome **B's conclusion** — scale is the axis — is therefore the one the evidence delivers, reached
through outcome **A's first column** rather than through B's own. §5.137 §6's fourth row was written
as the stop; it is worth recording that the table's three live rows were built on the assumption that
the recede either collapses the selector or does not move it, and the corpus's answer is the second
with the collapse landing somewhere else entirely.

## 6. The label operator: the pair is unchanged, its selector is not

The two matrices are §5.136 §4's, float for float, and nothing about them moved: chroma gain exactly
1, no luma term, zero residual, `inputBackdropAware` 1 / `inputClamp` 1 / `inputClampPreserveHue`
unset on all 72 labelled occurrences, and the label's own layer at `opacity` **1 in every window
state** — so the label goes on drawing in the recede while the highlight beside it does not. The two
`-label-hot` scenes carry a label layer with an **empty filter list** in all six arm-and-scheme
combinations, 6 of 6: Apple still installs nothing over a colour the author named.

**What is refuted is that the colour scheme selects it.** At 1x the light scheme carries 8 darkening
and 4 lightening labels, and the dark scheme 1 darkening and 11 lightening. On **72 of 72** the label
carries the lightening matrix exactly when its own surface carries the high-gain operator and the
body's face fill is black — the same single bit as §3, per surface. The cell that proves it is the
one two arms of the same pose disagree about: on `dark-solid__rrect-48__rest-label` the `active`
light arm reads surface default **and** label darkening, and `policy-only` reads surface high-gain
**and** label lightening, on the same scene in the same scheme in the same pose. The label follows
the material, not the document.

Re-read under this reading, the 2x corpus agrees: there the label matches the body's fill on 24 of
24 as well, and it looked scheme-selected only because at 2x no surface adapts, so scheme and
material state coincide on every cell (§4). **§5.136 §4's "the selector is the colour scheme, and
nothing else the probe moved" was true of its corpus and is not the law**; it is left standing where
it was written, with this beside it.

This is the finding Decision Log 15 (c) waits on. §5.137 §3 chose, for vitrea, "the material's own
composite level against `foregroundCrossover`" as the label operator's selector, and argued it from
vitrea's own constraint — that a surface's level need not follow the document's. Apple turns out to
do the same thing, per surface, off the same quantity.

## 7. The gap, and what it costs

**Three cells in this corpus carry two different operators across runs** (§2), all at the two
backgrounds whose adaptation is marginal — `dark-solid` in light and `light-solid` in dark — and the
disagreement reaches the whole body, not just the filter: the face fill, the face black and white
points and the shadow fill all move together. Two of the three put two arms of the *same* pose on
opposite sides, so this is not a pose effect; it is either a settle that 8 s does not reach for the
body's own adaptation, or a genuinely bistable decision near the threshold.

It also touches a committed reading. `dark-solid__capsule-button__rest` is one of the two cells
§5.133 §4 named as switching at 1x in the key pose; in this corpus the two key arms read it as
**not** switching while the light recede reads it as switching. Of the eight scene ids shared with
G0, seven reproduce G0's matrix in every light group here and that one does not. **No committed
number is rewritten** — §5.133 §4's reading stands as recorded, and this is the second reading beside
it.

What it costs: any selector law for the surface operator is bounded from above by this. A law fitted
on the key pose alone would be fitted on a cell that two arms disagree about, and a bound declared
tighter than one cell in 25 could not be met by a second run of the same bed. The work that would
close it is a settle study on the body's adaptation — the same scene re-dumped n times at
`--settle` 8 and at a longer settle, reading `inputFaceColorMatrixFillColor` rather than a pixel —
which `dump-layers` can do in minutes and which no capture has ever needed before, because until now
the body's adapted state was read off pixels that had already settled.

## 8. The author tint, for completeness

12 occurrences, two scenes per arm and scheme, all on a `CASDFGradientEffect` layer with
`inputBackdropAware` 1 and no clamp, and the layer at `opacity` 1 in **every** window state:

| pose | scheme | what the matrix is |
| --- | --- | --- |
| key | light | rank-one colorize, `m` ≈ 0, output `g·Y + b` at b = 0.6000 / 0.3212 / 0.0000 |
| key | dark | rank-one colorize, `m` ≈ 0, b = 1.0056 / 0.5749 / −0.0306 |
| non-key | light | **achromatic**, `m` 0.7 with `g` 0.3 and b = −0.1 on every channel |
| non-key | dark | **achromatic**, `m` 0.7 with `g` 0.3 and b = +0.1 on every channel |

In the key pose the tint is W12 §5's and §5.133 §3's colorize: no identity part, the whole output on
one line through the seed. In the recede it is not a colorize at all — a level map with unit level
gain and a ±0.1 offset, and **no hue anywhere in it**. That is §5.130's measured "an author tint
loses its hue entirely while its darkening stays" appearing in Apple's own configuration rather than
in a pixel difference, and it is the first configuration-level evidence for the endpoint W27c G1
fitted. The two key-pose dark matrices, from `active` and `policy-only`, differ by at most
**2.38e-7** — one operator written twice by float32, which is what the reader's 1e-6 tolerance
exists for and why this pass reports nine byte-classes where the reader reports eight operators.

## 9. `active/light`'s 16 non-key dumps, read on their own

They are **the recede, reached by losing key alone**. The application stayed active under the
`.regular` policy and no deactivation was asked for, and on every field this reading looks at they
are indistinguishable from the `.accessory` arm: highlight layer `opacity` 0 on all 16, backdrop
`marginWidth` 0 on all 16, the author tint's matrix the same achromatic light one the light recede
carries, the label layer still at `opacity` 1, and the surface operator agreeing with `recede/light`
on **16 of 16** shared scenes.

Two things follow and one does not. It follows that the receded *configuration* is driven by key
resignation, not by application deactivation — which is a fact about what the capture's mechanism has
to reproduce, and a second, independent route to the same configuration. It also follows that
whichever non-key state the 2x corpus was in, §4's comparison holds. It does **not** follow that the
two states are the same pose in pixels: nothing here is a capture, `presentedActive` and the
attestation are about a capture and not a dump, and §5.136 §1 chose the `.accessory` mechanism by
measurement on the pixel side. The honest statement is that the two states agree on every
configuration field this reading reads, and that a pixel comparison of the two has never been taken.
