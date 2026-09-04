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

**Corrected by G0 (Decision Log 2, 2026-09-04).** The light of the four terms is
0.0026–0.0106 on the light cells, not 0.023–0.058; the distance between the tier and
the renderer is the tier's own — its mirror applies the size law's occlusion after
the response solve where the shader applies it before (+0.015…+0.027), and any
conversion solved at one backdrop level is a point condition over a bimodal cell.
The purpose stands with its means restated: the tint's lerp itself moves into the
linear-light filter as an affine, exact per pixel, and the four terms plus the inner
shadow ride on its intercept as the derived light they are.

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
term-wise and not read as "GPU minus CSS" (Design, binding). *Correction beside
(G0, claims §5.74 §2–§3): the "excess" of 0.023–0.058 was not the four terms,
which measure 0.0026–0.0106 on these cells; it was the tier's mirror and the
point-condition of the conversion W16 G1 measured — see Decision Log 2.*

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
  **G0 (claims §5.74 §4): the form holds to +0.006 on every cell it covers, and the
  terms it derives are +0.0026…+0.0106 — kept in the derivation, not the mechanism.**
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
  **Superseded by Decision Log 2:** the two-equation solve is a point condition with
  a negative intercept a `type="linear"` primitive clips (G0 §4); the lerp itself is
  the affine, and it needs no solve.
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
- **The union-contour residual (from G1; claims §5.75 §7, §5.76 §7).** The two
  `toolbar-group` scenes and `photo__glass-over-glass` read −0.010…−0.015 against the
  GPU tier where every single-contour cell lands within 0.01: a broad interior offset at
  every depth with a bright contour band, a third of it the form's derived residuals, the
  same capsule alone at −0.0005. Next measurement: a native fixture of a lone 46 px
  capsule against the three-up arrangement, then the union contour's terms. Its own
  charter.
- **The shape axis's four cells and the fold's second cell.** `light-solid__rrect-md`
  (2x), `light-solid__rrect-ml` (both light scales) and `hc-text__capsule-button` (2x) in
  `PREDICATE_EXCLUDES` at the renderer's level over a near-tone backdrop;
  `hc-text__capsule-button` under reduced transparency at 0.9310 against 0.95. The
  extractor's reach, not the material's: a second arm (the rim's structure, or the GPU
  capture's silhouette as a prior) is an instrument item.
- **The darks on the encoded form** by the declared boundary — the dark scheme within
  0.011 of the GPU tier as it was; the eight-bit linear chain's quantum (thirteen encoded
  codes at the bottom) the reason; closes only with a higher-precision filter
  intermediate the platform does not offer.
- The three holdout cells 0.001–0.003 past the level clause, S3's `rrect-ml` 2x by
  0.0005, increased contrast's ΔE +0.00012; the plain-`blur()` engines' level (E's with
  the ordering fix, its anchor kept on W16 G1's measurement); the CSS tier's frame timing
  (one cell by 1 code at this rebuild; the tracker).

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | `packages/calibration/results/2026-09-04-w17-css-interior-level/g0/g0-interior-level.md` (`654ad0e`), claims §5.74 | CLOSED 2026-09-04 — the four terms 0.0026–0.0106, superposing within 0.0008 and derived within 0.006; the mirror's ordering defect (+0.015…+0.027) and the inner shadow found; the chartered carrier clips and is a point condition; four `[parent-impact]` items reconciled in Decision Log 2 |
| G1 | branch `w17-g1-level` at `033ea6b` (seven commits: the ordering fix and the inner shadow, the transfer, X6 and X7, the probe pre-check, configurations 1–2, the re-form, configuration 3, the holdout; `g1/g1-dry-run.md`, the verify and gate outputs, `toolbar-residual.md`, `region-sweep.md`, `cost/`, the sheets); claims §5.75 | COMPLETE 2026-09-05 — DECLARED in claims §5.75; Decision Log 7 executed by the user: land as declared |
| G2 | `packages/calibration/results/2026-09-04-w17-css-interior-level/g2/` (`g2-landing.md`, `g2-rebuild.sh`, `g2-runs.txt`, `g2-verify.py`, `g2-verify.txt`), `sheets/g2-1x.png`, `g2-2x.png`; claims §5.76; `.changeset/css-interior-level.md` | COMPLETE 2026-09-05 — merge `6c97c3a`, the canonical bed rebuilt once (230 cells; the GPU tier byte-identical 115 / 115, the CSS tier the frozen configuration's within 0.00005); six floors ratcheted and one kept (`UNMET_ROWS` 7); the predicate list 30 → 33 by one mechanism; the coherence statement narrowed in `optics.ts` (q4); every suite green; the sheets the dry run's panels; **RECOMPOSED** in claims §5.76 §5 |

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

### Decision Log 2 — G0 read: the target stands, the account of the distance is replaced, and the conversion becomes the lerp itself in linear light (2026-09-04)

**Evidence** (claims §5.74; G0's findings §1–§7). The four terms measure +0.0026…+0.0106 on the
light cells, superpose within 0.0008 and derive within 0.006 — the charter's stop ("not
attributable within 0.01") is not tripped, and the charter's premise that they are the 0.023–0.058
is false. The tier's mirror computes the composite in the wrong order (+0.015…+0.027, one-signed
on 15 of 44 untinted cells) and omits the inner shadow; in the shader's order with the inner shadow
the model reads within 0.001 of the render on the probe cells at 1x. The chartered carrier — a
value-and-slope solve at the group's level carried by `type="linear"` — clips 29–38 % of the
backdrop at a −0.19 intercept and is a point condition over a cell whose backdrop's σ is 0.39–0.42;
it still closed the gap 2.5–4× and raised `ssimMean` on all six probe readings.

**Rulings (the parent; binding unless marked).**

- **(a) The target stands** — the renderer's rendered interior, term by term (the user's q0). The
  Grounding Baseline's reading (iii), Purpose's account and Design's "likely closed form" bullet
  carry corrections beside them rather than rewrites. The four terms stay in the derivation at
  their measured size (they are 0.010 of the level on a thin span, the clause's own tolerance).
- **(b) The mirror takes the shader's order and gains the inner shadow.** `sizeOcclusionAlphaAt`
  enters the alpha before the response solve, as `sizedAlpha` does in the shader; the inner shadow
  (`shadowDepth`, `shadowAlpha`; area mean by G0 §2's co-area integral over the host's declared
  thickness) enters the mirror in the shader's own placement. This is a tier defect in its own
  right and moves the level on every engine, so G1 measures it ALONE as the dry run's first
  configuration before the full form, and X7 pins the composite — not only the constants —
  against the renderer's per backdrop level.
- **(c) The conversion is the lerp.** On Chromium the tint's lerp moves into the SHARP layer's
  linear-light reference filter as a per-channel `feComponentTransfer type="linear"` — slope
  `1 − α`, intercept `α·T_c + X_c` — with α and T the shader-order values per group and X the
  derived light of the four terms and the inner shadow's area mean. The intercept is non-negative
  by construction; the form is exact per pixel, so the acceptance's mean is met by construction up
  to two residuals G1 derives and records: the page's encoded-space mix of the two TINTED layers
  under the mask (second order in the sharp–heavy difference, and smaller than W16's untinted mix
  by `1 − α`), and W16's effective-width residual. L3 carries no tint overlay on Chromium. The
  `rgba()` overlay stays on the plain-`blur()` engines (E's form, with (b)'s ordering fix, behind
  the conformance row) and for the author-tint fold (W10), whose algebra over a tinted filter
  output G1 re-derives if S5 fires. The filter definitions become per group (keyed by σ, α, T and
  X) and re-solve when the sampled tone changes. *Reason (joint view):* the point solve's failure is
  structural — a clipped intercept and a curvature term that is first order on a bimodal cell —
  and the lerp is affine while the Gaussian is linear, so the exact composite is one primitive
  with no degree of freedom to solve; this removes the conversion rather than improving it.
- **(d) `referenceBackdropLuminance` retires on Chromium**; on the plain-`blur()` engines the
  one-alpha conversion keeps a declared anchor, and G1 decides (advisory: the group's sampled
  level, since (b) re-derives the alpha there anyway).
- **(e) What is not imported.** The renderer's 2x term (its body 0.004–0.008 brighter than its own
  composite, §5.55 §3) and the dark-ground dot. A tier that lands 0.004–0.008 under the GPU tier
  at 2x is inside the acceptance's 0.01; if the mask-mix residual stacks it past 0.01 the clause
  is re-declared at G1 with both numbers named, not widened silently.
- **(f) The other answers.** q1's correction accepted in (c); q2 the fold in G1 (unmeasured at
  G0; the same transfer with the folded α); q3 stands and was not called; q4's wording is the
  measured level ratio, re-read at G1 without the clip.
- **(g) Acceptance clause one is met at G0** (the excess measured, attributed within 0.0008,
  the analytic model within 0.005 in the shader's order, the closed form within 0.006). Clause
  two's 0.01 is unchanged.

**G1's shape.** A branch (`w17-g1-level`). First the probe pre-check — the three W16 cells at
both scales under (b) + (c), the level against the GPU tier, the spread and `ssimMean` beside —
reported to the parent before the full dry run, since (c) is a form G0 did not capture. Then two
whole-bed dry runs to scratch under the stops: configuration 1, the ordering fix and the inner
shadow alone (E's overlay); configuration 2, the full form. The landing's test file runs against
each scratch matrix (X6). The holdout once, at configuration 2 frozen. The sheets. The declaration
in claims (§5.75).

### Decision Log 3 — the probe pre-check lands; S3 and S5 re-declared against the renderer before the whole-bed run (2026-09-04)

**Evidence** (branch `w17-g1-level` at `72bd15a`, `results/2026-09-04-w17-css-interior-level/g1/probe-tables.md`).
The full form — the shader's ordering, the inner shadow as the shader's own layer identity, the
tint's lerp inside the sharp layer's linear-light filter — puts the CSS tier's interior within
0.01 of the GPU tier's on all six probe readings: −0.0061 / −0.0055 / −0.0064 at 1x and −0.0005 /
+0.0001 / −0.0011 at 2x, against the W16 bed's +0.027…+0.064; the level ratio 0.9998–1.0094; the
cross-tier ΔE down and `ssimMean` up on all six (+0.0097 / +0.0051 / +0.0165 at 1x); the GPU tier
byte-identical. The ordering fix alone closes 0.010–0.018 of the gap and is not a landing. The two
derived residuals: the encoded-space mix of the two tinted layers −0.0040 at dpr 1 and −0.0009…
−0.0022 at dpr 2 (7–14× smaller than the untinted mix, as (c) predicted, and the size and sign of
the tier's −0.006 at 1x); the effective width moves the level by ≤ 3e−6. Decision Log 2 (d)'s
question is answered by the worker with W16 G1's own measurement: the plain-`blur()` anchor stays
at 0.02 and is no longer read on the Chromium path.

**Two stops were declared against the wrong reference, and are re-declared here, in the open,
with both numbers to be named on every cell.**

- **S3, the spread.** As written it reads the interior spread against NATIVE at ±0.01 / ±0.015,
  which was W16's reach for a body change. `checkerboard__rrect-md` at 1x now reads −0.0122
  against native and within 0.0042 of the GPU tier's own −0.0080: the tier became coherent with
  the renderer on a cell where the renderer is itself off native, which is this wave's binding
  target (Decision Log 2 (a), (e)). **Re-declared:** the tier's spread within 0.005 of the GPU
  tier's own spread on every calibration span at both scales; the distance to native reported
  beside it as a second column and carried as the renderer's residual where it exceeds W16's
  reach. Read as written, S3 fires by 0.0022 on one 1x cell; that reading is recorded, not
  suppressed.
- **S5, the untouched cells.** As written it holds the solids and the author-tinted cells within
  0.002 in every adopted metric — a clause inherited from W16, whose body change was not meant to
  move the level. This wave moves the level on every cell by design: the light solid sits +0.025
  over the GPU tier on the bed and must move to land; an author-tinted surface draws
  `(1 − s)·material + s·layer` and carries `(1 − s)` of the untinted level change, 0.04–0.06, by
  the fold's own algebra. **Re-declared:** every solid and author-tinted cell's interior mean
  lands within 0.01 of the GPU tier's (the tinted cells' move predicted per cell as `(1 − s)` of
  the untinted change and the prediction reported beside the measurement); its cross-tier ΔE does
  not rise; its `ssimMean` stays inside its bound or floor; the dark-scheme cells that were within
  0.015 of the GPU tier move by no more than 0.005. The Parent-Level Acceptance's corresponding
  clauses read the same way from here.
- **`ssimBand` down 0.0044 on `rrect-md` and `rrect-ml` at 2x** while `ssimMean` rises there:
  not a stop of its own; S2's floors on the whole bed decide, and the reading is named in the
  declaration either way.

Everything else in G1's stops stands as written. Step 2 opens on these terms.

### Decision Log 4 — the whole-bed run: the level lands on the renderer; three properties of the carrier stop it, and each is re-formed with its mechanism (2026-09-04)

**Evidence** (branch `w17-g1-level` at `29f4afa`, `results/2026-09-04-w17-css-interior-level/g1/g1-dry-run.md`,
`cfg1.verify.txt`, `cfg2-calval.verify.txt`, the gate outputs, `dry-tables.md`, the sheets). Two
whole-bed runs (configuration 1, the ordering fix and the inner shadow alone; configuration 2, the
full form) over the six profiles' calibration and validation cells, the GPU tier byte-identical on
85 / 85 captures under both (S1). Configuration 2 puts the CSS tier's interior within 0.01 of the
GPU tier's on every light checkerboard, `photo` and solid cell except the two `toolbar-group`
scenes (`rrect-md` −0.0061 / −0.0005, `rrect-ml` −0.0064 / −0.0011, `light-solid__rrect-md`
+0.0001 / +0.0000 from a bed +0.017 over), `ssimMean` up on every checkerboard cell, the tinted
cells moving by exactly `(1 − s)` of the untinted change (the one half-strength cell lands within
0.01; the full-strength ones move ≤ 0.0017), and `checkerboard__capsule-button` under reduced
transparency conditioning again (S7's first cell). Configuration 1 alone closes 0.010–0.018 of
the gap and is not a landing (recorded, as (b) asked). The holdout was not read — configuration 2
is not frozen, and the worker's refusal to spend X8's one reading on a form these findings change
is upheld.

**Three mechanisms, each measured to its cause.**

1. **The reference filter's region clips the heavy kernel on small surfaces** — a W16 defect the
   fitted `rgba()` anchor had absorbed. `createCssTierFilterDefs` writes `−50% / 200%`; on a
   46 CSS px capsule that is ±23 px against a heavy step of σ 13.69 CSS px at dpr 1 (3σ = 41 px).
   The arithmetic predicts exactly the cells that miss: the `toolbar-group` scenes read −0.021 /
   −0.024 at 1x against the GPU tier, −0.050 under reduced transparency where the frost is 1.75×
   wider, and half as bad at 2x where the step is 4.36 px; per annulus a uniform dark body with a
   bright contour band, not a tint error.
2. **The linear-light chain's intermediate is eight bits in linear light**, and its quantum at
   the bottom is 13 encoded codes (`E(1/255)` = 0.0498). `impulse__capsule-button`, whose
   composite the renderer draws flat at 0.0037 linear (12 / 255 encoded), draws 0 on the tier
   at both scales: `ssimMean` 0.9756 → 0.9060 / 0.9155, the latter under its 0.92 bound. The
   dark profiles' cross-tier ΔE rises with it (0.00406 → 0.00565, 0.00414 → 0.00562): the dark
   scheme's composites sit at 13–18 quanta, where each step is 2–3 codes. The `rgba()` overlay
   never met this because it composites in the encoded space.
3. **The tier's contrast floor does not survive a filter that does not render.** The doctrine at
   the head of `css-tier.ts` — the surface always paints a real tint and never relies on the blur
   for contrast, because S1's failure class ("the engine reports support and renders nothing")
   is undetectable — is binding, and with the whole tint inside the filter the contrast-floor
   pixel test reads a channel delta of 0 against a floor of 8.

**Rulings (the parent; binding).**

- **(a) The floor is an element paint, and the filter carries the remainder exactly.** L3 keeps
  an encoded tint overlay at the doctrine's floor alpha α₃ (the tier's existing floor constant;
  G1 names it and derives nothing new), and the sharp layer's filter carries the remainder as a
  per-channel `feComponentTransfer type="table"` sampling
  `F(b) = D((E(M(b) + X) − E(T)·α₃) / (1 − α₃))` over N points, N from the piecewise-linear
  interpolation error bound (< 1e−4), monotone, and non-negative whenever α₃ ≤ α (which the
  floor guarantees). Exact to the table's resolution, no point condition. Reason: the doctrine
  is binding, and an affine under an encoded overlay would reintroduce the curvature term
  Decision Log 2 removed; a table does not.
- **(b) The filter region derives from the heavy step's reach.** The input extent the kernel
  needs beyond the box is `k·σ_heavy` at the live device ratio, written in the box's own
  percentage units per group; `k` is chosen by measurement — the level residual on the
  `toolbar-group` cells at k = 2, 2.5 and 3 — as the smallest k whose residual is within 0.005,
  its residual recorded beside the constant. The region's area counts in W16's filtered-area
  budget (the collapse rule, unchanged at 0.4 M device px per layer per frame), and S8 is
  re-measured on the cost harness with the derived region at both scales and on the demo's
  densest CSS-tier page; if the knee moves there, it is a `[parent-impact]` on W16 Decision
  Log 2 q1 (the user's budget) and comes to the parent before any landing.
- **(c) A declared boundary for the darks.** A group whose composite's sampled level lies where
  the eight-bit linear chain's quantum in encoded codes exceeds a declared tolerance draws the
  encoded form (E's overlay with the ordering fix and the inner shadow) instead of the table; the
  boundary is derived from the quantum, `E(L + 1/255) − E(L)` against the tolerance, and
  confirmed against the dark profiles' readings (their ΔE must not rise under it). The group
  state reports it (`cssTint: "linear" | "encoded"`, beside W16's `cssBody`), so the readouts
  and the harness say which form drew. The dark scheme's level then remains E's, named as such;
  on the bed it was within 0.011 of the GPU tier and nearer native than the renderer on its dot.
- **(d) S3 is one-sided.** It fires only where the tier's spread is farther from native than the
  renderer's by more than 0.005. The 2x cells where the tier's spread is above the renderer's
  because it is nearer native (+0.009…+0.011 against the GPU tier, −0.002…−0.007 against native)
  are a recorded finding — the tier drawing the renderer's kernel at its measured effective
  width lands nearer native than the renderer's own pass — and not a stop. Both numbers stay in
  every table.
- **(e) `light-solid__rrect-ml` joins `PREDICATE_EXCLUDES` at the landing**, at both light
  scales, with its reason: the tier at the renderer's level (0.9315 / 0.9322) over a background
  0.003 away, which the luminance-delta extractor separates on the GPU tier only by the rim and
  lens the CSS tier does not draw. The machine's output; the perceptual rows still gate.
- **(f) The holdout stays unspent** until the re-form is frozen; then once.
- **(g) The three Chromium e2e pins** that recompute the tier's law are re-pointed for the
  ordering fix with the reason; the contrast-floor test passes with (a) by construction and is
  not loosened; the near-black level assertion follows (c).

**G1 continues on the re-form.** Implement (a), (b) and (c); re-run the probe pre-check on the
three W16 cells plus the two `toolbar-group` scenes, `impulse__capsule-button` and one
dark-scheme checkerboard cell at both scales, with the k sweep for (b); report. Then the
whole-bed run as configuration 3 under the stops as they now read, the landing's test file against
its matrix (X6), the holdout once when frozen, the cost (S8), the suites, the sheets, and the
declaration (claims §5.75, written by the parent from the report).

### Decision Log 5 — the re-form's pre-check: (a) and (c) land, (b) is refuted by its own sweep and withdrawn, the floor's identity settled by arithmetic (2026-09-05)

**Evidence** (branch `w17-g1-level`, four commits past `29f4afa`; `g1/region-sweep.md` and the
probe tables). Under the floor overlay with the table transfer (a) and the declared boundary (c),
the three W16 probe cells read +0.0010 / −0.0005 / −0.0003 against the GPU tier at 1x and
+0.0034 / +0.0095 / +0.0039 at 2x; `ssimMean` up on every light cell against the W16 bed and
`ssimBand` up 0.022–0.059 at 1x; the cross-tier ΔE down on every light cell; the GPU tier
byte-identical. `impulse__capsule-button` and the dark-scheme checkerboard draw the encoded form
and are unchanged from the bed to every printed digit, which is what the boundary is for.

**The floor's identity.** Ruling (a) named "the tier's existing floor constant" and the tier has
no constant of that name. The worker measured both readings: the group's own converted alpha
(0.665, the regular variant) lands the probe cells +0.018 / +0.008 / +0.018 at 1x and
+0.032 / +0.023 / +0.038 at 2x, worse than the previous form; the least tint the tier draws on
the shipped profile, `MATERIAL_OPTICS.clear.tintAlpha` = 0.2668, lands them as above. The reason
is arithmetic: the filter carries the remainder after the overlay, so everything it draws —
the encoded-space mix of the two layers under the mask with it — reaches the composite through
`1 / (1 − α₃)`, 2.99 at the first reading and 1.36 at the second. **Ruled: the floor is the least
real tint the tier draws, the clear variant's alpha**, an existing constant; the amplification
argument goes in its doc comment. A smaller floor derived from the pixel test's eight codes was
considered and declined: the doctrine's floor is a material, not a threshold.

**Ruling (b) is withdrawn, not adjusted.** The sweep it asked for gives byte-identical captures at
k = 0.5, 1, 1.5, 2, 2.5 and 3: a `backdrop-filter`'s input is the snapshot behind the element's
own border box, so the `<filter>` element's region reaches nothing outside it and loses nothing
inside it — the attribute is inert on this construction, and Decision Log 4's attribution of the
`toolbar-group` deficit to it was wrong. The worker reverted the derivation and the budget change
rather than land a constant with no effect, and that is upheld. The `toolbar-group` cells
improved under (a) and (c) alone (−0.0209 → −0.0122 and −0.0150 at 1x, −0.0040 and −0.0101 at 2x)
and remain outside 0.005 with their cause unexplained.

**The `toolbar-group` residual gets a bounded diagnosis and no remedy from inference:** per
annulus against the GPU tier on both scenes at both scales; the form's two derived residuals
evaluated on the toolbar geometry (a 46 px capsule where the ramp's heavy share is high
everywhere, so the encoded-space mix of the two tinted layers may be several times
`rrect-md`'s); one single-surface capsule of the same span in a scratch scene. Explained: the
term is recorded beside its constant. Unexplained: carried as a named gap with the annulus
profile as evidence. G1 proceeds either way.

**Then the whole-bed run as configuration 3** under the stops as they read after Decision Logs
3 and 4, the landing's test file against its matrix (X6); if nothing fires beyond the carries
already named (the `toolbar-group` cells; `light-solid__rrect-ml`'s predicate entry),
configuration 3 is frozen and the holdout read once (X8); then S8 on the cost harness and the
demo's densest page with the table transfer, the suites, the sheets, and the report for the
declaration (claims §5.75).

### Decision Log 6 — configuration 3 frozen on the whole-bed run; four sub-thousandth readings and the `toolbar-group` residual carried by name; the holdout spent (2026-09-05)

**Evidence** (branch `w17-g1-level`, six commits; `g1/g1-dry-run.md`, the configuration 3 verify
and gate outputs, `toolbar-residual.md`). Configuration 3 — the ordering fix and the inner shadow,
the floor overlay at the clear variant's alpha with the table transfer on the sharp layer's
linear-light filter, the declared boundary sending dark composites to the encoded form — over the
six profiles' calibration and validation cells: the CSS tier's interior within 0.01 of the GPU
tier's on every light cell but the two `toolbar-group` scenes (`rrect-md` +0.0010 / +0.0034,
`rrect-ml` −0.0003 / +0.0039, the capsule −0.0005 / +0.0095, `light-solid__rrect-md` +0.0007 from
+0.0254), `ssimMean` up on every light checkerboard row and `ssimBand` up 0.019–0.059 at 1x, no
held floor's row below its pin, the GPU tier byte-identical on 85 / 85 (S1, the sixth whole-bed
run in a row); the tinted cells moving by exactly `(1 − s)` of their base's change; the
reduced-transparency capsule conditioning again (S7, recovery 0.9961); the cost knee unmoved
with the 33-value table (S8); every suite green (1 785 unit; chromium 129, firefox 102, webkit
102, chromium-gpu 9, react 105 + 3).

**Four readings past the stops, accepted as named carries.** S3 (one-sided) on
`checkerboard__rrect-ml` at 2x, farther from native than the renderer by +0.0055 against 0.005;
S5's cross-tier ΔE up +0.0006 / +0.0007 on `dark-solid__rrect-md` at the light scales and
+0.0010 on the half-strength tinted cell; S6's +0.00012 on increased contrast; and
`light-solid__rrect-md` at 2x joining `PREDICATE_EXCLUDES` beside `rrect-ml` at both scales, one
mechanism for all three — a light solid landed on the renderer's level sits within 0.004 of its
own background, which the luminance-delta extractor separates on the GPU tier only by the rim
and lens this tier does not draw. Each is at or under 0.001 except the 0.0005, none is a
mechanism the run has not explained, and none moves a floor.

**The `toolbar-group` residual is a named gap, not an attribution.** The bounded diagnosis: a
broad interior offset at every depth (−0.005…−0.017 at dpr 1 across the first three annuli, a
bright contour band +0.017…+0.062, nearly absent in the core at dpr 2); the encoded-space mix of
the two tinted layers −0.0040 on the toolbar capsule, the same as on every other 1x cell (the
affine scales the sharp–heavy difference by `1 − α` before the encode sees it, so a high heavy
share does not multiply it); the kernel's truncation at the element's own boundary −0.00035;
together a third of the −0.0122. The single-surface capsule of the same span
(`checkerboard__capsule-button`) reads −0.0005, so the residual tracks the three-up box and not
the span, and separating the box from its neighbours needs a native fixture this bed does not
have. Carried with the annulus profile as its evidence (`toolbar-residual.md`); no remedy
proposed.

**Ruled:** configuration 3 is frozen as it ran; the holdout is read once on those bytes (X8) —
the CSS renderer over the six profiles, the GPU rows byte-identical by S1 — and the declaration
follows in claims §5.75 with the landing question for the user.

### Decision Log 7 — the landing: as declared, held for the union-contour residual, or the ordering fix alone (2026-09-05; the user's)

**Evidence** (claims §5.75; `results/2026-09-04-w17-css-interior-level/g1/g1-dry-run.md` §3b and
§5; the sheets sent 2026-09-05, whose banner is W16's script's and reads one wave behind —
columns 2 and 4 are the W16 bed, column 3 this candidate). By the parent's eye at 1x: the
candidate's grey sits on native's and the GPU tier's on every checkerboard span and on the photo
where the bed read whiter; the checker's contrast is the GPU tier's; the diff column is flat
inside and carries only the band; neither CSS column has the lens curvature or the rim band, the
seven floors' mechanism, unchanged.

**Options.**

1. **Land as declared** (`033ea6b`). G2 merges, rebuilds the canonical bed once, ratchets six of
   the seven floors (`rrect-ml` 1x → 0.8747, `glass-over-glass` 1x → 0.8600, `rrect-lg` 1x →
   0.8692, `rrect-md` 2x → 0.9143, `rrect-ml` 2x → 0.8779, `rrect-lg` 2x → 0.8712; `glass-over-
   glass` 2x kept at 0.8677), keeps `UNMET_ROWS` at 7, records the predicate list's move (30 → 33
   lines, one mechanism), re-words the tier-coherence claim with the measured ratio (q4), and
   carries by name: the union-contour residual on the two `toolbar-group` scenes and
   `photo__glass-over-glass` (−0.010…−0.015), the three holdout cells 0.001–0.003 past the level
   clause, the fold's second capsule cell at 0.931 against 0.95, S3's one cell by 0.0005, and the
   dark scheme on the encoded form (within 0.011 of the GPU tier, as it was). **Recommended:** the
   wave's purpose is met on every light calibration cell but the union-contour pair, the floors
   only rise, the coherence falls on the fitted profiles, and what is left is either an
   instrument's reach (the shape axis on a light solid at the renderer's level) or a residual
   whose next measurement needs a fixture this bed does not have.
2. **Hold for the union-contour residual.** Capture a lone 46 px capsule against the three-up
   arrangement natively, derive the union contour's terms, re-run. The eleven cells that landed
   do not move with it; the two that miss might. A charter of its own either way.
3. **Land configuration 1 alone** — the ordering fix and the inner shadow with the encoded
   overlay: closes 0.010–0.018 of the gap, moves no predicate cell, keeps the level 0.02–0.05
   over the renderer. Not recommended.

**The user decides.**

**Executed 2026-09-05 (the user: "land as declared").** Option 1. G2 opens: the merge of
`w17-g1-level` at `033ea6b`, the canonical rebuild once from the main checkout, six floors
ratcheted and one kept, `UNMET_ROWS` 7, the predicate list's move recorded with its mechanism,
the tier-coherence claim re-worded with the measured ratio (q4), the carries named in Deferred,
the sheets, the changeset, recomposition.

## Surprises & Discoveries

- **2026-09-05 (G1) — a light solid landed on the renderer's level is invisible to the
  extractor.** `light-solid__rrect-ml` and `rrect-md` sit within 0.004 of their background once
  the tier draws the renderer's composite; the GPU tier conditions there only by the rim and
  lens. Coherence with the renderer costs the shape axis cells the renderer keeps (Decision Log 6).
- **2026-09-05 (G1) — the `toolbar-group` residual tracks the box, not the span.** The same
  capsule alone reads −0.0005 and three-up reads −0.0122; neither derived residual reaches it.
- **2026-09-05 (G1) — a `<filter>` element's region is inert on a `backdrop-filter`.** Six
  regions from k = 0.5 to 3 capture byte-identical: the input is the snapshot behind the element's
  border box and nothing outside it exists to reach. The Surprise below it, written from Decision
  Log 4's inference, is withdrawn by this measurement (Decision Log 5); the `toolbar-group`
  residual it explained is unexplained again.
- **2026-09-05 (G1) — the contrast floor's size is a mechanism, not a detail.** The filter's
  remainder reaches the composite through `1 / (1 − α₃)`; at the group's own alpha that is 2.99
  and the probe cells land worse than the un-floored form, at the least tint the tier draws it is
  1.36 and they land within 0.001 at 1x (Decision Log 5).
- **2026-09-04 (G1) — [withdrawn 2026-09-05, see above] the reference filter's region was
  clipping the heavy kernel on small surfaces since W16, and the fitted overlay hid it.** `−50% / 200%` is ±23 px on a 46 px capsule
  against a 41 px reach; the `toolbar-group` cells read −0.021…−0.050 against the GPU tier only
  once the tint became exact (Decision Log 4 (b)). A conversion fitted against the cross-tier
  difference absorbs the defects on both sides of it.
- **2026-09-04 (G1) — the linear-light chain is eight bits in linear light, and its bottom quantum
  is thirteen encoded codes.** A composite the renderer draws at 12 / 255 the tier draws at 0, and
  the dark scheme's composites step by 2–3 codes (Decision Log 4 (c)). The body's blur had lived
  with it since W16; the tint cannot.
- **2026-09-04 (G1) — the tint inside the filter removed the tier's contrast floor**, the
  doctrine written for exactly the failure that cannot be probed (Decision Log 4 (a)).
- **2026-09-04 (G1) — at 2x the tier's spread lands nearer native than the renderer's own** on
  three cells, drawing the renderer's kernel at its measured effective width; a coherence stop
  read symmetrically would have called that a miss (Decision Log 4 (d)).
- **2026-09-04 (G0) — the renderer's light is a hundredth of the level.** Declining the
  lens, the rim, the highlight and the lift together moves the GPU tier's interior by
  +0.0026…+0.0106 on the light cells (claims §5.74 §2); W16 G1's 0.023–0.058 was the
  tier's own composite against a wrong model and a point condition, not the renderer's
  terms. The charter's premise was a reading of a difference, not a measurement of a
  cause — the spike existed to find exactly this, and did.
- **2026-09-04 (G0) — the tier's mirror and the shader disagree on when the size law's
  occlusion enters the alpha**, and it is worth +0.015…+0.027 of the level on the tier
  today (`root.ts` after the response solve, the shader's `sizedAlpha` before it; claims
  §5.74 §3). A two-tiers-one-profile defect that tier-coherence did not pin because it
  pins the constants and not the composite; fixed in G1 and pinned there (X7).
- **2026-09-04 (G0) — `feComponentTransfer type="linear"` cannot carry a negative
  intercept.** Filter Effects clamps a primitive's result to [0, 1]; the chartered solve's
  intercept is −0.19 and 29–38 % of the checkerboard's filtered backdrop is clipped. The
  lerp itself has a non-negative intercept and needs no clamp (Decision Log 2).
- **2026-09-04 (G0) — matching value and slope at one backdrop level does not match a
  mean over a bimodal cell**; the encode's curvature times the backdrop's variance
  (σ 0.39–0.42) is first order. Any single-point conversion of this composite inherits
  it, and W16's one-alpha conversion is one; the exact form is per pixel or nothing.
- **2026-09-04 (G0) — the lens is exactly a displacement.** Its mean on a checkerboard
  is −0.0002 and on a photo the backdrop's own gradient at the contour, sign included; a
  term that moves 7 313 pixels by up to 37 codes and the mean by nothing.

## Outcomes & Retrospective

**RECOMPOSED 2026-09-05** (claims §5.76 §5, clause by clause). The CSS tier draws the
renderer's interior composite: its mirror computes the alpha in the shader's order and carries
the inner shadow; on Chromium the tint's lerp runs inside the sharp layer's linear-light filter
as a per-channel table over the least tint the tier draws, exact per pixel with no solve and no
fitted constant, the mapping's declared anchor no longer read on that path; groups whose
composite sits below the eight-bit linear chain's quantum draw the encoded overlay and say so on
their state. On the canonical bed the interior level is within 0.01 of the GPU tier's on every
light calibration cell but the two union-contour scenes (from +0.02…+0.06 over), similarity
rises on every light checkerboard row, six held floors ratchet up and none moves down, the
cross-tier ΔE falls on the fitted profiles, the reduced-transparency capsule conditions again,
and the GPU tier is byte-identical on every capture.

**What did not close, by name.** The union-contour residual (−0.010…−0.015 on three cells,
tracking the box and not the span); four cells the shape axis can no longer condition and the
fold's second capsule cell at 0.931 against 0.95, the extractor's reach on a surface at the
renderer's level; three holdout cells 0.001–0.003 past the level clause, one spread cell by
0.0005, one profile's ΔE by 0.00012; the dark scheme on the encoded form by the declared
boundary; the plain-`blur()` engines' level; the renderer's own gaps, not imported.

**Retrospective.** The charter was written on an inference from W16's numbers — that the
renderer's light was the gap — and the spike it chartered measured that inference to a
hundredth of the level and found the gap in the tier's own composite instead: an ordering
defect no coherence pin had reached, and a conversion that could not be exact at one level. The
design was re-decided twice on measurement (Decision Logs 2 and 4) and once withdrawn on it
(Decision Log 5, the filter region), and each ruling that survived is one whose rival was
measured beside it: the floor's size, the table over the affine, the boundary for the darks.
The stops were re-declared twice in the open (Decision Logs 3 and 4) when the wave's binding
target and the inherited stops disagreed, with both readings kept in every table. The worker's
two refusals — not to spend the holdout on an unfrozen form, not to ship a constant its sweep
showed inert — were the discipline working from below. Process: one worker for G0 and one for G1
through three configurations; the parent's rulings were wrong once on a mechanism and right on
the form; the referee ran the landing's test file against every scratch matrix (X6, W16's
lesson), and the landing found nothing the dry run had not.

## Revision Notes

- 2026-09-04: chartered from W16's Deferred entry and claims §5.73 §7 on the
  user's pick after the 0.6.0 cut ("chartering the interior level's closure
  would be next"); G0 opened.
- 2026-09-04: **Decision Log 1 executed** — the user took every recommendation (q0–q4); the target
  rule is binding outright; G0 continues unchanged.
- 2026-09-04: **G0 CLOSED** (claims §5.74). The four terms are 0.0026–0.0106, not the charter's
  0.023–0.058; the tier's mirror has an ordering defect worth +0.015…+0.027 and omits the inner
  shadow; the chartered carrier clips and is a point condition. Four `[parent-impact]` items
  reconciled in Decision Log 2: the target stands, the mirror takes the shader's order, the
  conversion becomes the lerp itself as an affine in the sharp layer's linear-light filter. Five
  Surprises. G1 opened on that form with a probe pre-check first.
- 2026-09-04: **G1 pre-check landed** (Decision Log 3): all six probe readings within 0.01 of the
  GPU tier, `ssimMean` up on every one. S3 re-declared against the renderer's own spread and S5
  against the renderer's level with the tinted cells' predicted move beside, both with the reason;
  the whole-bed dry run opens.
- 2026-09-04: **G1 whole-bed run read** (Decision Log 4). The level lands on the renderer's across
  the bed and three properties of the carrier stop it — the filter region clipping the heavy
  kernel (a W16 defect), the eight-bit linear intermediate's truncation in the darks, and the
  contrast floor the doctrine requires; each re-formed with its mechanism: the floor stays an
  element paint and a table transfer carries the exact remainder, the region derives from the
  heavy step's reach with its residual, a declared boundary sends dark composites to the encoded
  form. S3 one-sided; one cell to the predicate list; the holdout unspent. Four Surprises.
- 2026-09-05: **G1 re-form pre-check read** (Decision Log 5). (a) and (c) land the probe cells
  within 0.001 at 1x and 0.01 at 2x with `ssimMean` up everywhere; the floor is the clear
  variant's alpha by the amplification arithmetic; (b) refuted by its own sweep — the filter region
  is inert on a `backdrop-filter` — and withdrawn, Decision Log 4's Surprise struck through; the
  `toolbar-group` residual to a bounded diagnosis, then the whole-bed run, the freeze and the
  holdout.
- 2026-09-05: **configuration 3 frozen** (Decision Log 6): the whole-bed run meets every stop but
  four sub-thousandth readings, accepted as named carries; the `toolbar-group` residual carried
  with its annulus profile after a bounded diagnosis; the holdout spent once on the frozen bytes.
- 2026-09-05: **G1 DECLARED** (claims §5.75): configuration 3 refereed on the whole bed with the
  holdout read once — S1, S2, S8 met; S3 by 0.0005 on one cell; S4 on the two union-contour scenes
  and two holdout cells; S5 on two holdout cells and three ΔE rises; S6 by 0.00012 on one
  profile; S7 one of two. Decision Log 7 puts the landing to the user (recommended: as declared).
- 2026-09-05: **Decision Log 7 executed** — the user landed the declaration as it stood (option 1). G1 COMPLETE, G2 opened.
- 2026-09-05: **G2 COMPLETE, the wave RECOMPOSED** (claims §5.76). Merge `6c97c3a`; the canonical
  bed rebuilt once; the GPU tier byte-identical 115 / 115; the CSS tier the frozen configuration's
  within 0.00005; six floors up, one kept; the predicate list 30 → 33 by one mechanism; the
  coherence statement narrowed to the engines it still describes; every suite green; the sheets
  the dry run's panels with the banner corrected. Outcomes & Retrospective written; the
  union-contour residual, the shape axis's cells, the darks' boundary and the margin misses
  carried.
