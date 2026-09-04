# W17 — The CSS tier's interior level: the two-equation conversion and the light the renderer draws that the tier does not (2026-09-04)

> **Parent:** the post-v1 wave (`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`),
> by way of W16's Deferred entry "The interior level" and claims §5.73 §7,
> which name this closure's shape; W16 Decision Log 3 landed the two-layer body
> with the level as its one named conversion gap. **Ordering (user,
> 2026-09-04, after 0.6.0):** "chartering the interior level's closure would be
> next." **Consumes:** claims §5.72 §3–§4 (eight single-cell configurations:
> one encoded alpha cannot match the renderer's linear lerp in mean and slope;
> a `contrast()` joint solve pivots at encoded 0.5 and breaks the dark cells; a
> `feComponentTransfer` joint solve with a free intercept lands the tier on the
> renderer's ANALYTIC composite, −0.03…+0.004 of native, and 0.023–0.058 BELOW
> the renderer's RENDERED interior, which carries the lens, the rim and the
> highlight in the same pixels), §5.73 §3 (the same level on the
> reduced-transparency fold drops two capsule cells from the conditioning
> predicate), `optics.ts`'s header and `cssTintAlpha` (the mapping agrees with
> the renderer at one declared backdrop level, `referenceBackdropLuminance`
> 0.02, and is off either side — the coherence floor the tier-coherence claim
> is worded around), §5.55 §3 (the thin material's scale-dependent level — the
> renderer's own gap, not this wave's), §5.35 (the tone response) and §5.37
> (the tint shade), which are the analytic composite's terms. **Starts from**
> `main` at the W16 bed (`64457d0`, recomposed `862b65e`; 0.6.0 published from
> `b86753f`): the CSS tier draws the two-component law through three children
> in linear light on Chromium, its tint an `rgba()` overlay at the one-alpha
> conversion (configuration E), its interior 0.04–0.09 over native and
> 0.016–0.068 over the GPU tier on every light-standard checkerboard, `hc-text`
> and `photo` cell at both scales; seven dom `ssimMean` floors held by
> decision, all the large spans' band.

## Purpose

Close the CSS tier's interior level as a **derivation**: the tier's tint
composite matches the renderer's in mean and slope — two equations, two
unknowns, an intercept and a slope on the filtered backdrop, carried by
`feComponentTransfer` inside the linear-light reference filter the tier
already runs on Chromium — and then adds, as a derived quantity, the light the
renderer draws into its interior that this tier does not: the rim's ambient
term, the highlight, and the lens's compression at the band. That excess is
the renderer's own property, measured on its own captures by declining each
term, and derived from the profile's numbers with the residual recorded, the
way the effective kernel width was carried in W16. The tier then reads at the
renderer's level on structured and flat backdrops alike, the cross-tier claim
stops being worded around a one-level floor, and the reduced-transparency
fold's two lost cells come back to the shape axis.

The wave also retires the one fitted constant the tier still carries: the
mapping's `referenceBackdropLuminance`, fitted against the cross-tier
difference, gives way to the group's own sampled level once the conversion is
exact there.

What this wave does **not** do: it does not fit the CSS tier to Apple past the
renderer. Where the renderer itself sits off native — the thin spans' +0.05,
the dark solid's dot — the tier inherits the renderer's composite and the gap
stays the renderer's, named in its own place (two tiers, one profile).

## Parent-Level Acceptance

- **The excess is measured, attributed and derived.** On the calibration and
  validation cells of the four standard profiles at 1x and 2x, the renderer's
  rendered interior mean minus its all-terms-declined render is read per cell,
  and the per-term declines (lens, rim, highlight, the outer shadow's lift)
  sum to the whole within 0.005 on every cell; the all-declined render agrees
  with the analytic composite computed from the profile (the tone response,
  the shade, the lerp) within 0.005; and a closed form from the profile's own
  numbers reproduces the excess within 0.01 on every calibration cell, its
  residual recorded per cell. The instrument's recovery of a known offset is
  beside every reading (X4).
- **The tier lands on the renderer's level.** The CSS tier's interior mean is
  within 0.01 of the GPU tier's rendered interior on every light-standard
  checkerboard, `hc-text` and `photo` cell at both scales (today +0.016 to
  +0.068), and within 0.015 on the reduced-transparency and increased-contrast
  cells; the dark-scheme and solid cells, already within 0.015 of the GPU
  tier, move by no more than 0.005; the cross-tier level ratio reads within
  0.97–1.03 on every light cell (today 0.92–0.98) and the cross-tier ΔE on
  the fitted sets falls on every profile.
- **The slope survives.** The interior spread stays within W16's reach of
  native — ±0.01 at 1x and ±0.015 at 2x on the calibration spans (the
  `rrect-ml` 2x 0.0006 miss carried, not widened).
- **The structure does not pay for the level.** No dom row falls below its
  adopted bound or its floor; the seven held floors' rows read at or above
  their W16 pins; no 1x checkerboard row falls more than 0.002 below the W16
  bed. If the exact level costs structure beyond that, the wave stops and the
  trade goes to the user with both numbers (Decision Log 1 q3).
- **The fold recovers.** `checkerboard__capsule-button__rest` and
  `hc-text__capsule-button__rest` under reduced transparency condition again
  (`areaWeb` ≥ 0.95, one body) and leave `PREDICATE_EXCLUDES`; every fold row
  stays inside its bound.
- **The GPU tier does not move**: every capture byte-identical to the W16 bed
  and every row within 0.0002; the tinted (author-tint) cells and the solids
  within 0.002 in every adopted metric.
- **The cost is measured** on W16 G0's harness: the added primitive keeps the
  knee where the reference filter left it (two surfaces' filters leave the
  cadence between 32 and 36 surfaces); the collapse rule is unchanged.
- **Chromium is measured; the other engines keep the one-alpha conversion**
  behind the conformance rows unless the user says otherwise (Decision Log 1
  q1).
- **By eye:** the X5 sheets at the dry run and the landing, sent; the
  candidate no longer reads whiter than native and the GPU tier on the
  checkerboards; the reading recorded; the landing the user's.
- All suites green, lint clean; the canonical matrix rebuilt once at
  recomposition; the holdout read once per frozen configuration; every gap in
  claims, this Deferred list or the tracker.

## Grounding Baseline (the W16 bed, 2026-09-04, `64457d0`)

Interior mean, whole silhouette, linear luminance; native, then the GPU tier
and the CSS tier as deltas against native; the last column is the gap this
wave closes (CSS minus GPU).

| cell | dpr | native | GPU Δ | CSS Δ | CSS − GPU |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__rrect-sm` | 1x | 0.6285 | +0.0511 | +0.0748 | +0.024 |
| `checkerboard__capsule-button` | 1x | 0.6207 | +0.0576 | +0.0844 | +0.027 |
| `checkerboard__rrect-md` | 1x | 0.6829 | +0.0117 | +0.0590 | +0.047 |
| `checkerboard__rrect-ml` | 1x | 0.6936 | +0.0011 | +0.0511 | +0.050 |
| `checkerboard__glass-over-glass` | 1x | 0.7231 | −0.0111 | +0.0369 | +0.048 |
| `checkerboard__rrect-lg` | 1x | 0.7066 | −0.0119 | +0.0441 | +0.056 |
| `hc-text__rrect-md` | 1x | 0.7368 | +0.0127 | +0.0650 | +0.052 |
| `hc-text__capsule-button` | 1x | 0.6657 | +0.0902 | +0.1356 | +0.045 |
| `photo__rrect-md` | 1x | 0.6649 | −0.0064 | +0.0498 | +0.056 |
| `photo__rrect-lg` | 1x | 0.6855 | −0.0238 | +0.0350 | +0.059 |
| `light-solid__rrect-md` | 1x | 0.9373 | −0.0048 | +0.0206 | +0.025 |
| `dark-solid__rrect-md` | 1x | 0.4844 | +0.0131 | +0.0144 | +0.001 |
| `mid-dark-solid__capsule-button` | 1x | 0.4484 | +0.0138 | +0.0574 | +0.044 |
| `checkerboard__rrect-md` | 2x | 0.6832 | +0.0182 | +0.0761 | +0.058 |
| `checkerboard__rrect-ml` | 2x | 0.6929 | +0.0084 | +0.0722 | +0.064 |
| `checkerboard__glass-over-glass` | 2x | 0.7223 | −0.0045 | +0.0528 | +0.057 |
| `checkerboard__rrect-lg` | 2x | 0.7052 | −0.0041 | +0.0636 | +0.068 |
| `checkerboard__capsule-button` | 2x | 0.6226 | +0.0621 | +0.0932 | +0.031 |
| `hc-text__rrect-md` | 2x | 0.7404 | +0.0165 | +0.0731 | +0.057 |
| `photo__rrect-md` | 2x | 0.6654 | −0.0052 | +0.0463 | +0.052 |
| `checkerboard__rrect-md` (dark) | 1x | 0.0493 | +0.0191 | +0.0079 | −0.011 |
| `dark-solid__rrect-md` (dark) | 1x | 0.0414 | +0.1691 | +0.0896 | −0.080 |
| `checkerboard__capsule-button` (RT) | 1x | 0.8903 | +0.0430 | +0.0555 | +0.012 |
| `hc-text__capsule-button` (RT) | 1x | 0.8932 | +0.0480 | +0.0695 | +0.022 |

Three readings of the table. (i) On the mid and large light spans the GPU
tier sits within ±0.012 of native and the CSS tier 0.04–0.07 over: the gap is
the tier's, and closing it to the renderer closes it to Apple. (ii) On the thin
spans the renderer itself is +0.05–0.09 over native (§5.55 §3, the thin
material's scale-dependent level) and the CSS tier a further +0.02–0.05 over
that; this wave closes the second number and leaves the first where it is
recorded. (iii) On the dark scheme and the dark solid the CSS tier is nearer
native than the GPU tier (the renderer's dot, +0.17 on `dark-solid`); the
conversion must not import that, which is why the excess is derived
term-wise and not read as "GPU minus CSS" (Design, binding).

The eight single-cell configurations of W16 G1 (`results/2026-09-04-w16-css-two-layer/g1/g1-dry-run.md`
§5) are the wave's second baseline: H (the `feComponentTransfer` joint solve
against the analytic composite) at −0.0226 / +0.0044 / −0.0306 of native on
`rrect-md` / the capsule / `rrect-ml` at 1x and −0.0343 / −0.0532 / −0.0317
against the GPU tier; E (landed) +0.0590 / +0.0844 / +0.0511 of native. The
renderer's excess over its analytic composite, read as the difference, is
0.034 / 0.053 / 0.032 at 1x and 0.028 / 0.058 / 0.023 at 2x — larger on the
thin span, where the band is a larger fraction of the interior, which is the
first thing the term-wise attribution has to reproduce.

## Design (advisory unless marked)

- **[binding] Two tiers, one profile (K5).** The conversion's intercept and
  slope are solved from the profile's tint, alpha, tone response and shade
  through `optics.ts`; the excess is derived from the profile's rim, highlight
  and lens numbers and the surface's geometry; no constant is fitted for this
  tier, and every derived quantity carries its residual against the
  renderer's measured excess per cell. A lookup table of measured excesses is
  not a derivation and is not admissible; the measurement validates the closed
  form.
- **[binding] The target is the renderer's rendered interior, term by term
  (Decision Log 1 q0, answered 2026-09-04).** The tier adds the light of the terms
  it does not draw and nothing else; the renderer's residual against native
  that is not a term (the thin-span level, the dark-ground dot) is not
  imported. "GPU minus CSS" per cell is a check on the outcome, never the
  input.
- **[binding] The GPU tier does not move.** This wave changes
  `packages/platform-web` (the mapping, the reference filter's primitives, the
  fold) and the calibration harness's CSS-tier rows; the renderer's material,
  passes and goldens are untouched and byte-identical at the dry run and the
  landing. G0's declined renders are scratch captures under a scratch profile
  document, never the canonical bed.
- **[binding] The carrier lives inside the existing form.** No new element:
  the intercept and slope are primitives in the reference filter the heavy and
  sharp layers already run (`feComponentTransfer` on the filtered backdrop,
  before the tint composites), Chromium-only by the same conformance row as
  the filter; the plain-`blur()` engines keep the one-alpha conversion and its
  level (Decision Log 1 q1).
- **[binding] Chromium is the measured engine.** As W16.
- **[binding] X8 — the holdout is read once** per frozen configuration, at the
  dry run; the landing reproduces it.
- Advisory — **the instrument.** The renderer's `materialProfile` seam
  (`withMaterialOverrides`; the isolation proof's declined profiles are the
  precedent) takes a scratch profile document with one term declined at a
  time — the lens (`lensAmountMax` and `lensRefractionGain` 0), the rim
  (`rimAlpha` 0), the highlight (`specularGain` 0), the outer shadow's lift —
  and all four together; the calibration CLI renders the GPU tier under it to
  a scratch matrix (`--out-matrix`, `VITREA_WEB_CAPTURES`), and the interior
  mean per cell is read from the cells as the bed's is. The all-declined
  render is the analytic composite drawn by the shader; its agreement with the
  composite computed in TypeScript from the same profile is the check that the
  analytic model is the shader's (the tone response is read at the group's
  sampled luminance, the shade at the same, the lerp in linear light).
- Advisory — **the likely closed form.** Each term's excess is its light
  times the fraction of the interior it covers: the rim's ambient term at
  `rimAlpha` times the highlight's linear luminance over the band's width
  along the contour (the band a known function of span and the rim's
  falloff), the highlight over its arc, the lens's compression bringing the
  exterior's mean inward over the band (a displacement, so its sign follows
  the backdrop's gradient at the contour and its mean over a checkerboard is
  near zero but not over a photo); the outer shadow's lift is outside the
  silhouette by construction and should read zero inside. The thin-span
  excess being 1.5–2× the mid-span's is the band-fraction signature.
- Advisory — **the conversion.** W16 G1's H, described in claims §5.72 §3
  and `g1-dry-run.md` §5, its mechanism written on the tier in the mapping's
  `referenceBackdropLuminance` doc comment (`optics.ts`, W16 G1's re-form);
  the sweep that measured it was not committed, so G0 re-derives the solve
  from the two equations: the intercept and slope such that the tier's
  encoded output matches `E(b(1−α) + t·α)` in mean and in derivative with
  respect to `b` at the group's backdrop level, then the intercept raised by
  the derived excess in linear light before encoding. The mapping's
  `referenceBackdropLuminance` (0.02, **fitted against the cross-tier
  difference** — the one constant on this tier that is a fit, by that
  comment's own account) is retired for the group's sampled level, which the
  tier already measures for the tone response; the coherence floor "at one
  declared level" becomes "the derivative's second order", which G0 should
  bound.
- Advisory — **the fold.** Reduced transparency raises the occlusion on both
  tiers to the same composed mix (W16 X7); the conversion applies to the
  fold's composite as to the nominal one, and the two predicate cells are the
  fold's acceptance. Increased contrast likewise.
- Advisory — **the dark cells.** With a free intercept the dark solids sit
  where H put them (0.5162 / 0.4580 on `dark-solid` / `impulse` `rrect-md` in
  the light profile, within 0.0003 of the bed); the stop is that they do not
  move by more than 0.005 anywhere.

## Children

### G0: The renderer's excess, measured and derived — spike (deliverable: findings)

- **Purpose:** read the renderer's rendered-interior excess over its analytic
  composite per cell, attribute it term by term with declined renders, check
  the analytic model against the all-declined render, derive the closed form
  from the profile and record its residual per cell; confirm the
  `feComponentTransfer` carrier lands the tier within 0.01 of the target on
  the three W16 probe cells at both scales; measure the primitive's cost on
  W16 G0's harness; validate the instrument (X4).
- **Observable acceptance:** a findings document under
  `packages/calibration/results/2026-09-04-w17-css-interior-level/g0/` with
  (a) the attribution table — every calibration and validation cell of the
  four standard profiles at 1x and 2x, default minus each declined render and
  minus the all-declined, the per-term sum within 0.005 of the whole; (b) the
  analytic check — the all-declined render against the TypeScript composite
  within 0.005 per cell, or the model's error named; (c) the closed form with
  its residual per cell and the largest residual named with its cell; (d) the
  carrier check on the six probe readings; (e) the cost; (f) the X4 recovery;
  (g) the answers G0 recommends to Decision Log 1's questions, with numbers.
- **Stops (G0 has none — it reports).** A finding that the excess is not
  attributable to the four terms within 0.01 (the sum short, or the
  all-declined render off the analytic composite by more) is a
  `[parent-impact]` on Design's binding target, and the parent re-decides
  before G1 opens.
- **Track:** spike; one worker; scratch captures only (GPU custody: one
  capture at a time, nothing else on the adapter); commits with pathspecs
  under the findings directory alone.

### G1: The declared conversion and its dry run — controlled

- **Purpose:** the conversion's intercept and slope in `optics.ts` from the
  profile, the excess's closed form beside them with G0's residual recorded
  in the doc comment, the primitives in the reference filter, the fold; the
  tier-coherence pin extended to the level (the tier's composite against the
  renderer's per backdrop level over {0.05, 0.2, 0.5, 0.8} and dpr {1, 2});
  the dry run on the full bed to scratch under the stops, the holdout read
  once; the sheets; the declaration in claims.
- **Stops (refined by G0 with numbers):** (S1) every GPU capture byte-identical
  to the W16 bed and every GPU row within 0.0002; (S2) no dom row below its
  bound or floor, the seven held rows at or above their W16 pins, no 1x
  checkerboard row more than 0.002 below the W16 bed; (S3) the spread within
  ±0.01 / ±0.015 of native at 1x / 2x on the calibration spans; (S4) the
  interior mean within 0.01 of the GPU tier's on every light-standard
  checkerboard, `hc-text` and `photo` cell at both scales, the dark and solid
  cells moving ≤ 0.005; (S5) the tinted and solid cells within 0.002 in every
  adopted metric; (S6) `tier-coherence` tighter, the cross-tier ΔE down on
  every profile, the level ratio within 0.97–1.03 on every light cell; (S7)
  the two reduced-transparency capsule cells condition; (S8) the cost knee
  unmoved; (S9) the user's eye.
- **Edges:** blocked-by G0. **Track:** controlled; a branch; the landing is
  the user's call (Decision Log).

### G2: The landing and its referee — controlled

- **Purpose:** merge; the canonical rebuild once; `PREDICATE_EXCLUDES` down by
  two (the machine's output); the floors re-recorded at the landing's
  readings (none may go down without a decision); the sheets; recomposition.
- **Stops:** G1's, re-read on the canonical bed, plus the referee running the
  landing's test file against the dry-run matrix before the merge (W16's
  lesson).
- **Edges:** blocked-by G1. **Track:** controlled.

## Cross-Child Contracts

- **X1 — the canonical rebuild.** As W16 X1. Owner: parent.
- **X2 — floor bookkeeping.** Floors ratchet up where rows rise; a floor that
  would go down stops the landing for the user. Owner: parent.
- **X3 — the untouched tier.** Byte identity on the GPU tier, every profile.
  Owner: parent.
- **X4 — the instrument's validation travels with every reading.** The
  interior-mean reader recovers a synthetic offset (+0.03 in linear light
  lerped into a capture) before it reads a declined render. Owner: G0; G1
  binds.
- **X5 — the by-eye sheets.** W16's script (five panels) at 1x and 2x, dry run
  and landing. Owner: parent.
- **X6 — the dry-run referee runs the landing's gates.** `verify-dry.py`'s
  successor either replicates every gate of `adopted-thresholds.test.ts`
  (bounds, floors, the conditioning predicate) or the test file runs against
  the scratch matrix. Owner: parent.
- **X7 — the coherence pin.** `tier-coherence.test.ts` asserts the tier's
  composite against the renderer's per backdrop level and dpr, and the fold
  on both tiers. Owner: G1.
- **X8 — the holdout, read once** per frozen configuration. Owner: G1; parent
  verifies.
- **X9 — the engines.** The primitive is gated on the reference filter's
  conformance row; the plain-`blur()` engines' level is recorded as a named
  gap, not measured. Owner: G1.

## Ordering & Dependency Map

G0 → G1 → G2 → recomposition. Nothing lands before G2's referee.

## Risks & Mitigations

- **The excess is not the four terms.** The tone response is read per group
  at the sampled luminance and the shader may apply it per pixel, or the lens
  may carry a mean on structured backdrops that no closed form reaches within
  0.01. G0's (b) and (c) are built to find this; a residual over 0.01 is a
  parent-impact and the target is re-decided (a bounded per-span residual
  carried as the effective width's was, or the wave narrowed to the mean
  alone).
- **The exact level costs structure.** W16 G1 saw H score under E on five of
  six cells while sitting nearer native in level. S2's 0.002 clause is the
  guard; if the level and the structure pull apart past it, the trade is the
  user's (Decision Log 1 q3), and the wave records both landings as W15's
  §5.70 §7 did.
- **The fold's composite differs from the nominal one in a way the two
  equations do not cover** (the occlusion lift is applied after the tone
  response). G1 carries the fold under its own two equations if so; the two
  predicate cells are the acceptance either way.
- **`feComponentTransfer`'s cost on the reference filter.** G0 measures it on
  W16's harness; if the knee moves, the primitive is a `linear` transfer on
  one channel of a luminance-only stage, or the collapse budget takes it into
  account (a user decision).
- **The other engines.** Their level stays E's; the gap is named, not hidden.

## Deferred / Out of Scope

- **The renderer's own level gaps** — the thin spans' +0.05–0.09 over native
  (§5.55 §3) and the dark-ground dot (`dark-solid` +0.17 in the dark scheme;
  W15 Deferred). Not imported by this tier and not fixed here; their own
  charters.
- **The rim band on the CSS tier** — W16 Deferred, unchanged; the seven floors'
  mechanism.
- **The plain-`blur()` engines' level** — E's, behind the conformance rows;
  measured only by the user's labeled manual pass (S1's section H).
- **The author-tint fold (W10)** — the two encoded layers fold into one exactly
  today; with an intercept beneath them the fold's algebra changes. This wave
  keeps the tinted cells within 0.002 (S5) and does not re-derive the fold; if
  S5 fires, the fold is G1's to re-derive with its reason.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | `packages/calibration/results/2026-09-04-w17-css-interior-level/g0/` | opened 2026-09-04 |
| G1 | — | blocked-by G0 |
| G2 | — | blocked-by G1 |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-04)

**The cut.** Three children as W16's: a spike that measures the renderer's
property this conversion needs and validates the closed form, a controlled
gate that declares the derivation and dry-runs it under stops, a controlled
landing. One child fewer would put the measurement and the fit in one hand,
which is what K5 forbids; one more would split the conversion from the fold it
has to cover.

**Bound here, with the joint-view reason.** The target is the renderer's
rendered interior term by term (not "GPU minus CSS", not native): the tier
draws the renderer's material and only the renderer's residual against native
is Apple's gap, which belongs to the renderer's waves — reading the outcome as
the input would import the dot and the thin-span level into this tier and
make the two tiers disagree on purpose. The carrier lives inside the existing
reference filter: a fourth element or a second filter would re-open W16's
element model and its cost knee for a quantity that is a transfer function.

**Put to the user, with the recommendation.**

- **q0 — the target.** (a) The renderer's rendered interior, term by term
  (recommended: the binding rule above; the mid and large light spans, where
  the renderer is within ±0.012 of native, close to Apple as a consequence).
  (b) Apple's level directly, per cell — a fit against native on this tier,
  which K5 forbids and which W16 G1's H already measured: nearer native in
  mean, lower in structure on five of six cells.
- **q1 — the carrier and the engines.** (a) `feComponentTransfer` inside the
  linear-light reference filter, Chromium-only by the filter's conformance
  row; the plain-`blur()` engines keep the one-alpha conversion and E's level,
  named as their gap (recommended: the only exact carrier measured, and no new
  element). (b) A `contrast()`-based approximation on every engine — rejected
  at W16 G1 on the dark cells (its pivot at encoded 0.5) and not re-measured
  here unless asked.
- **q2 — the reduced-transparency fold in scope.** (a) Yes: the same
  conversion on the fold's composite, the two predicate cells its acceptance
  (recommended: the fold's level is the same mechanism, and the cells are a
  live shape-axis loss). (b) No: the fold keeps E and the two cells stay
  excluded with their reason.
- **q3 — the trade if the level costs structure.** (a) Stop and put both
  landings to the user with the sheets and the rows, as W15 did (recommended:
  the metric cannot arbitrate a level it barely weighs and an eye can). (b)
  Accept structure losses inside the floors' epsilon without asking.
- **q4 — the coherence claim's wording.** With the conversion exact at the
  group's sampled level, the tier-coherence claim can drop "at one declared
  backdrop level" for "within the derivative's second order" with G0's bound;
  (a) re-word at G2 with the number (recommended), (b) keep the wording.

G0 opens on the recommendations; each answer that differs re-opens the
affected child before G1.

**Executed 2026-09-04 (the user: "all according to your recommendations").** q0 (a) — the
target is the renderer's rendered interior term by term; the Design bullet that carried "once
answered" is binding without qualification. q1 (a) — `feComponentTransfer` inside the
linear-light reference filter, Chromium-only by the filter's conformance row; the
plain-`blur()` engines keep the one-alpha conversion and E's level as a named gap. q2 (a) —
the reduced-transparency fold is in scope, the two predicate cells its acceptance. q3 (a) — if
the level costs structure past S2's 0.002 clause, the wave stops and both landings go to the
user with the sheets and the rows. q4 (a) — the tier-coherence claim is re-worded at G2 with
G0's second-order bound. G0 was already running on these answers; nothing re-opens.

## Surprises & Discoveries

(none yet)

## Outcomes & Retrospective

(open)

## Revision Notes

- 2026-09-04: chartered from W16's Deferred entry and claims §5.73 §7 on the
  user's pick after the 0.6.0 cut ("chartering the interior level's closure
  would be next"); G0 opened.
- 2026-09-04: **Decision Log 1 executed** — the user took every recommendation (q0–q4); the target
  rule is binding outright; G0 continues unchanged.
