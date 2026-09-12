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

## 0a. What was read outside the declaration's scope

`declaration.md` §1 scopes its field list to the 150 dumps of this corpus and names the two older
corpora only inside stop **S7**, as *aggregate reproduction* checks — dump counts, occurrence counts,
matrix counts, layer opacities. This pass reopens both of them and reads **fields**: the
`glassBackground` filter's face and shadow fills, every `vibrantColorMatrix`, the label layers and
`tracksLuma` by span. Four published figures come from that half — the body law's **58 of 58** on
G0's corpus and **50 of 50** at 2x (§3), and the **10 of 50** and **5 of 24** cross-scale differences
(§4).

It was read because **the 1x half is uninformative alone**: a co-variation found in one corpus is a
property of that corpus until it is checked against the others, exactly as §5.137 §1 found an
`opacity` of 0 to say nothing until the same layer was read somewhere else. **No bound, threshold or
partition is drawn on that half** — §3's bracket and §5's outcome resolution are stated on the 150
dumps alone — and it is nonetheless **load-bearing**, because §3's claim to be a law rather than a
description rests on the other two corpora agreeing, and §4's whole comparison is against the 2x one.
Disclosed in the discipline §5.137 §1 set for itself; `declaration.md` is not edited after the fact.

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
were dumped in.** Three do not:

- `light dark-solid__capsule-button__rest` — default in **both** key arms, high-gain in the recede,
  which **is** pose-aligned inside this corpus;
- `light dark-solid__rrect-48__rest-label` — default in `active`, high-gain in `policy-only` (**the
  same pose, two arms**) and in the recede;
- `dark light-solid__capsule-button__rest` — high-gain in `policy-only` only; `active` and `recede`
  both read the default (again **two arms of the same pose**).

Two of the three put two arms of the same pose on opposite sides, which measures this bed's own
run-to-run spread at one cell. The first is the one that would carry a pose claim, and it is
**inconclusive rather than null**: a "key → default" law over it is contradicted directly by the G0
corpus, which is light, 1x and **key** and reads that same scene id as **high-gain** — the opposite
of what such a law predicts. So one cell points at a pose effect, the corpus that should corroborate
it points the other way, and its two neighbours show a lone cell's disagreement needs no pose to
explain it. §7 below says what that costs; the settle study is what resolves it.

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

One bracket this corpus narrows, and one it does not:

- **the light-scheme span gate — narrowed.** At `dark-solid`'s tone the surface adapts at declared
  span 44, 48 and 64 and does not at 80 or 96, so the gate lies in **(64, 80]** — where §5.133 §4
  could only say "somewhere in (44, 96)". vitrea's own `backdropToneAdaptation(tone,
  sizeThickness(span))` at the shipped profile reads **0.5338** at span 64 and **0.0029** at span 80:
  its fitted knee is already inside Apple's interval. Apple's own `tracksLuma` is 1 at 44/48/64 and 0
  at 80/96 and brackets it identically — **at both scales**, which matters in §4. This is a bracket
  at **one tone across a span ladder**, which is what the probe bed was built to supply.
- **the dark-scheme tone threshold — NOT bracketed.** The figure first written here,
  **(0.5, 0.890969]**, is **withdrawn**, and named rather than deleted so the correction is legible.
  It mixed spans: the lower endpoint is `checkerboard` at **span 96** with `tracksLuma` **0**, the
  upper is `light-solid` at **span 44** with `tracksLuma` **1**, and this same section measures that
  span moves the adaptation — so the two endpoints are not comparable and the interval between them
  is not a tone threshold. At the one span the dark arm holds a tone ladder on, **span 44**, every
  *stable* cell up to tone **0.214096** (`mid-chroma-solid`) reads high-gain, and the only cell above
  it is `light-solid__capsule-button__rest`, which is one of §2's unstable three — 1 of its 6
  occurrences reads high-gain. So the corpus gives a **lower bound of 0.214096 at span 44 and no
  upper bound at all**, the deciding cell not holding still. What is unchanged: vitrea has no term
  for a dark-scheme adaptation at all — `backdropToneAdaptation` reads 0 on every dark cell that
  switches, so the predicate that separates the light scheme 72 rows out of 75 separates nothing in
  dark. A ladder that would bracket it must be **at fixed span with repeated endpoint dumps**.

## 4. So what the 2x corpus was: the scale, and nothing else left

§5.136 §5 could not tell a scale dependence from a pose collapse because the two corpora differed in
both. What this corpus supplies is the pose at 1x:

- the 2x corpus is non-key on all 50, `marginWidth` 0 on all 50, highlight opacity 0 on all 50 — the
  same receded configuration this corpus reaches at 1x;
- at 1x the two non-key states the corpus reaches — accessory-and-never-activated, and
  regular-and-still-active — give the same reading on every field this walk takes.

**The attribution is an inference, not a matched control, and is written as one.** Of the three
window states in play, exactly **one attests its own state per dump**: the `recede` arm, at
`isKeyWindow` false, `appIsActive` false, `activationPolicy` `accessory`. The `active/light` non-key
tail records **no** `appIsActive` either — those dumps predate the field — so
"regular policy, application still active" is read off its `open -W` launch and the corpus index
rather than off the dump. And the 2x run records **only** `isKeyWindow: false`. The chain is: those
two 1x states agree on every field (§9), from which the loss of **key** is what drives the receded
configuration, from which the 2x run's unrecorded activation cannot be what separates it — leaving
the scale. Each link is sound and the last is an inference. The pass that removes it is a **2x pass
through the accessory/never-activated mechanism with all three pose fields recorded per dump**, which
the harness can now do and which the same run that settles the mechanism below can take.

Against `recede/*`, scene for scene, the 2x corpus differs on **10 of 50** surface cells and **5 of
24** labels, and every difference is in one direction: at 2x nothing adapts. In light the eight are
the `dark-solid` 44/48/64 and `impulse` families; in dark the two are `light-solid`. At 2x every
light cell reads a white face fill and every dark cell a black one — **each scheme sits at its base
state and no cell adapts**, which is exactly what "one operator per scheme" was.

**Scale is the axis**, on that chain. The mechanism is not readable from the configuration, and one
candidate is **narrowed rather than killed**: `tracksLuma` is 1 at declared span 44/48/64 and 0 at
80/96 at **both** scales — computed at each scale and compared in `reading.json`, not asserted — so
Apple's own size flag is point-based and **`tracksLuma` is not the gate that closes at 2x**. That
does not exclude a *separate* adaptation size gate measured in device pixels; no field in the dumps
exposes one either way, so the refutation is scoped to the flag and the possibility stays open. The
experiment that would say which: a 2x `dark-solid` ladder at declared span 22 / 32 / 44 — if the
adaptation returns at the smaller declared spans there is a device-pixel gate after all and
`tracksLuma` is simply not it; if it never returns, the scale suppresses the adaptation by some other
route.

## 5. §5.137 §6's four outcomes, resolved

First, what "tone-and-span reproduces" was declared to mean. `declaration.md` §3 operationalised it
as a **literal cell partition** — high-gain on exactly `dark-solid__capsule-button__rest` and
`impulse__capsule-button__rest`, default on every other light cell. Measured against the active pose,
**12 of its 34 light rows contradict that partition, over 7 distinct scenes**: the ladder cells
`dark-solid__rrect-48__rest{,-label}`, `dark-solid__rrect-64__rest{,-label}`,
`impulse__capsule-button__rest-label` and `dark-solid__capsule-button__rest-label` read high-gain
where the partition says default, and `dark-solid__capsule-button__rest` itself reads default where
it says high-gain.

**That is the declaration's own defect and it is recorded, not repaired** (`declaration.md` is
committed evidence of what was declared and is not edited). §5.133 §4's partition was drawn on
**G0's** scene set; this bed carries a `dark-solid` span ladder G0 never had, and cells at the same
tone and a smaller span **must** switch under §5.133 §4's joint tone-and-span **law** while sitting
outside its two-cell **partition**. The declaration conflated the law with the partition, so its
operational test asks the bed for something the bed cannot give.

| # | what it required | what the corpus reads |
| ---: | --- | --- |
| **A** the recede collapses it | active opacity 1 **and** tone-and-span reproduces; recede opacity 0 **and** one operator per scheme | **both columns fail** — the literal partition does not reproduce in the active pose (12 of 34 rows against it), and the recede is opacity 0 but carries the same partition anyway, 17/8 in light and 2/23 in dark |
| **B** scale is the axis | active pose: one operator per scheme | **fails** — the active pose at 1x carries both operators in both schemes |
| **C** the recede changes the selector on a layer that still draws | recede opacity **1** | **fails**: recede opacity is 0 on all 50 |
| **D** stop | opacity 0 in the key pose | **does not fire**: opacity 1 on all 84 key dumps |

**All four fail, and what fits is a fifth reading.** What the active pose *does* reproduce is
§5.133 §4's **law** — a joint rule in tone and span, with every ladder cell on the side the law puts
it (§3, 146 of 150 rows). And the pose does not select the operator at all: it switches the layer the
operator sits on off (opacity 1 → 0) and strips the tint's hue, with the loss of key rather than with
the application's deactivation. The operator's selection is the glass's own adaptation (§3), it
survives both poses at 1x, and the 2x corpus's "one operator per scheme" is the scale suppressing the
adaptation (§4).

**Scale is the axis, and that rests on §4's own argument — not on any column of this table.** §4
controls the pose at 1x directly and names the single inference it still carries; outcome A's first
column is not the bridge and is not used as one. §5.137 §6's fourth row was written as the stop; it
is worth recording that the table's three live rows were built on the assumption that the recede
either collapses the selector or does not move it, and the corpus's answer is the second, with the
collapse landing on the layer instead.

## 6. The label operator: the pair is unchanged, its selector is not

The two matrices are §5.136 §4's, float for float, and nothing about them moved: chroma gain exactly
1, no luma term, zero residual, `inputBackdropAware` 1 / `inputClamp` 1 / `inputClampPreserveHue`
unset on all 72 labelled occurrences, and the label's own layer at `opacity` **1 in every window
state** — so the label goes on drawing in the recede while the highlight beside it does not. The two
`-label-hot` scenes carry a label layer with an **empty filter list** in all six arm-and-scheme
combinations, 6 of 6: Apple still installs nothing over a colour the author named.

**What is refuted is that the colour scheme selects it**, because at 1x **each scheme carries both
matrices**. Over all 72 labelled occurrences: **light 25 darkening / 11 lightening**, **dark 3 / 33**.
Per arm — light `active` 9/3, `policy-only` 8/4, `recede` 8/4; dark 1/11 in each of the three. (The
figures first written here, "8 and 4" and "1 darkening and 11 lightening", are the `policy-only` and
`recede` arms individually and were wrongly given as scheme-wide; the superseded pair is named rather
than deleted.) On **72 of 72** the label carries the lightening matrix exactly when its own surface
carries the high-gain operator and the body's face fill is black — the same single bit as §3, per
surface. The cell that proves it is the one two arms of the same pose disagree about: on
`dark-solid__rrect-48__rest-label` the `active` light arm reads surface default **and** label
darkening, and `policy-only` reads surface high-gain **and** label lightening, on the same scene in
the same scheme in the same pose. The label follows the material, not the document.

Re-read under this reading, the 2x corpus agrees: there the label matches the body's fill on 24 of
24 as well, and it looked scheme-selected only because at 2x no surface adapts, so scheme and
material state coincide on every cell (§4). **§5.136 §4's "the selector is the colour scheme, and
nothing else the probe moved" was true of its corpus and is not the law**; it is left standing where
it was written, with this beside it.

This is the finding Decision Log 15 (c) waits on — and it is narrower than it first looks, so the
limit goes here rather than in the recommendation alone. The 72 of 72 is a co-variation with the
body's face-fill **bit**. It does **not** show that Apple compares a composite **level** against a
threshold, which is what `foregroundCrossover` does: direct propagation of an internal adapted-state
bit from the body to the label fits these dumps exactly as well, and no field in a dump tells the two
apart. What the reading licenses is only that **Apple selects the label operator per surface, off
that surface's own adapted state, and not off the document's colour scheme** — the same *shape* as
`foregroundCrossover`'s role, not its arithmetic. §5.137 §3 chose the material's own composite level
for vitrea from vitrea's own constraint, that a surface's level need not follow the document's; that
choice is **converged on in form, not authorised in substance**, by this reading. Settling it needs
an intervention rather than a read: vary a surface's composite level while holding the body's adapted
state fixed and see whether the label's matrix follows the level or the bit, or recover structural
evidence naming the selector's input.

## 7. The gap, and what it costs

**Three cells in this corpus carry two different operators across runs** (§2), all at the two
backgrounds whose adaptation is marginal — `dark-solid` in light and `light-solid` in dark — and the
disagreement reaches the whole body, not just the filter: the face fill, the face black and white
points and the shadow fill all move together. Two of the three put two arms of the *same* pose on
opposite sides; the third is pose-aligned here and contradicted by G0's own key reading of the same
scene (§2), so the class as a whole is not a pose effect while one member of it is **unresolved
rather than dismissed**. It is either a settle that 8 s does not reach for the body's own adaptation,
or a genuinely bistable decision near the threshold.

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

They are **the recede, reached by losing key alone**. On every field this reading looks at they are
indistinguishable from the `.accessory` arm: highlight layer `opacity` 0 on all 16, backdrop
`marginWidth` 0 on all 16, the author tint's matrix the same achromatic light one the light recede
carries, the label layer still at `opacity` 1, and the surface operator agreeing with `recede/light`
on **16 of 16** shared scenes.

**Their own activation is inferred, not attested.** These dumps predate the harness's `appIsActive`
field, so "the application stayed active under the `.regular` policy and no deactivation was asked
for" is read off the `open -W` launch and the corpus index, not off the dump; only the `recede` arm
attests its state per dump. That matters because §4 leans on this pair.

One thing follows and one does not. It follows that the receded *configuration* is driven by key
resignation, not by application deactivation — a second, independent route to the same
configuration, a fact about what the capture's mechanism has to reproduce, and the link §4's
cross-scale comparison rests on, since the 2x corpus's own activation is unrecorded too. It does
**not** follow that the two states are the same pose in pixels: nothing here is a capture,
`presentedActive` and the attestation are about a capture and not a dump, and §5.136 §1 chose the
`.accessory` mechanism by measurement on the pixel side. The honest statement is that the two states
agree on every configuration field this reading reads, and that a pixel comparison of the two has
never been taken.
