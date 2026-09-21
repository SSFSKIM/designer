# W31 — the chromatic wave: the body carries the backdrop's hue, with three instruments in front

**Status: OPEN 2026-09-21 — chartered by the parent on the user's "let's proceed with next wave"
after the 0.20.0 publish, under the standing "rest on your judgement".** Executes W29 Decision
Log 6 (c) (the chromatic-transmission child, the largest residual on W30's own sheets) and carries
three of W30's Deferred-at-close items whose evidence is on disk and which need no ruling: the
exterior-width instrument (item 1), the WGSL range class (item 12) and the refusal-wording sweep
(item 13). Grounded on main at `8d9b6ceb` (0.20.0 published). **Three rulings were drafted for the
user in Decision Log 1 and ruled the same day, all as recommended (the digest rule by value, the
holdout rule as practised, the tone stage kept); the three instrument children run first.**

## Purpose

Over a photograph, Apple's macOS 27 dark material carries the backdrop's hues through the body —
green and magenta are visible in the plate without amplification on W30's own sheets — and
vitrea's renders a flat warm grey. The level agrees (interior mean native 0.1814 against 0.1636 on
`photo__rrect-lg__rest`, 1x dark) and the chroma does not: the matrix's mean-OKLab instrument
reads the native body's chroma at the backdrop's (`tintChromaDeltaNative` +0.0022) and vitrea's
below it (−0.0135 on `dom`, −0.0146 on `texture`), and the interior's spread reads 0.0417 native
against 0.0091 / 0.0141. Four of the seven rows 0.19.0 and 0.20.0 record as missed are this one
cell, `photo__rrect-lg__rest :: oklabDeltaEP95`, on both dark profiles and both tiers; W30 declared
them expected-unmoved and they are unmoved to five decimals. The recede's missed bound is worst on
the same cell's inactive pose on every row (§5.154 §8).

**No constant in either document can close this** (W29 Decision Log 6 (c)). The body is a neutral
plate composited over the blurred backdrop, and the backdrop tone response solves the plate's
luma in closed form — "chroma is untouched, the shift is achromatic", in the shader's own words
(`optics.ts`, the W9 solve). On the dark document the plate's alpha is high, so what the body
transmits is mostly the neutral, and a photograph's hues arrive as a grey of the right level.
Apple's material at the same level keeps the hue, which is what a darkening that acts on the
backdrop's luma while leaving its chromaticity alone does, and a plate does not. That is a
**mechanism** the material lacks, not a value it has wrong, and it is the operator this wave adds:
a chroma-retaining term in the body's composite, fitted per scheme, with the level held.

Three instruments come first, in parallel, because their evidence is on disk and none needs a
ruling. **The exterior's width** (W30 Deferred 1): the three rows W30 claimed through the σ law
moved by 0.0002 where they needed 0.016, because whole-cell SSIM is dominated by the interior, while
`falloffSigmaWeb` — the axis the lever actually moves — moved by up to 30 CSS px under no gated
bound at all; the wave that next moves the shadow needs a clause that reads what the lever moves.
**The WGSL range class** (W30 Deferred 12): the `tanh` overflow is fixed as an identity and the
class is not; `src/wgsl/` evaluates `exp`, `pow`, `tanh` and polynomials on document-scaled
quantities with nothing asserting an argument stays inside f32. **The refusal's wording and the
sweep rule** (W30 Deferred 13): `matrixSchemaRefusal` still offers an operator a ruling that ended.

What this wave does **not** do: it does not move the shadow's σ law, the scatter, the tone
response's abscissa or any anchor (X3); it does not build the highlight's angular reader; it does
not fix `compare`'s decoupled-contrast flag; it does not re-open the analysis pass (W30 Deferred 2,
the user's to charter); it captures **no native pixel**; and it does not decide the tone stage's
fate (Decision Log 1 (c) puts it to the user beside the two rulings the leaf needs).

## Parent-Level Acceptance

1. **The chroma is measured before the operator exists, by an instrument that reads hue per
   pixel.** The matrix's `tintChromaDelta` is over the interior's MEAN OKLab against the backdrop's
   mean, so a balanced photograph whose hues pass through reads near zero on both sides; it is the
   wrong instrument for this residual and G0 says so with the numbers. G0 adds a per-pixel chroma
   instrument to `packages/calibration` — the mean per-pixel OKLab chroma over the interior and the
   standard deviations of `a` and `b`, native, web and backdrop, so a **chroma transmission ratio**
   (interior over backdrop) can be read per cell — runs it over every chroma-carrying cell of the
   current generation (the `photo` scenes, `mid-chroma-solid`, the tinted cells; both schemes,
   both tiers, both scales, active and inactive; the macOS 26.5 rows beside for comparison) from
   committed fixtures and the captures the ledger names, and tables it per backdrop class per
   scheme per tier per span. The native delta between 26.5 and 27 on the same statistic is read from
   W29 G2's evidence or recomputed, so the wave knows whether Apple moved the chroma or vitrea never
   had it.
2. **The mechanism is named from the shader, and the leaf shape from the tables.** G0 states, from
   `optics.ts` and `material.ts`, exactly where the backdrop's chroma is lost (the plate's alpha in
   the composite; the achromatic solve; the tint's own chroma path; the recede's chroma collapse),
   which of those the light and dark documents exercise, and names **one** leaf shape with its
   inert identity under which every shipped document is bit-identical — a chroma retention that
   acts on the body's transmitted colour with the luma held, so the interior-level bounds do not
   move — with "conditioned by scheme" meaning two values of one leaf in the light and dark
   documents. It says what the CSS tier's two layers can carry of it (a `saturate()` term in the one
   `backdrop-filter` is available; whether it is the right projection is measured, not assumed)
   and what stays a recorded residual.
3. **Bounds before reads; the digest rule and the holdout rule are ruled before the leaf lands.**
   G0 declares the wave's acceptance — a tolerance on the chroma transmission ratio per backdrop
   class per scheme on the WebGPU tier with the CSS tier recorded; the four missed `oklabDeltaEP95`
   rows claimed, with the lever and the tier; the recede's worst cell reported; the interior-level
   and departure stops the fit must hold; every other adopted row expected unmoved, the shadow's
   and the scatter's named — and whether each tolerance becomes an adopted row at G4 or stays a
   one-wave reading. The 27 tables stay at their ruled values; no floor. **G0 also proves what
   Decision Log 1 (a) asks the user to rule on**: the fingerprint of each macOS 26.5 document with
   every leaf at its declared inert identity dropped equals the document's own recorded
   `resolvedMaterialSha256` (`b2b570e4adcea8fb`, `874be66ea501621b`), with the inert-identity
   table committed beside the proof.
4. **Three instruments land without a material change.** G1: a statistic over the exterior's
   fitted width and the departure profile's shape, a reader, and a clause shape declared as the
   candidate adopted row for the wave that next moves the shadow, read on the current generation
   as a one-wave reading with the seven missed rows' figures beside — not adopted, not fitted. G2:
   a unit case over `src/wgsl/` requiring every transcendental's argument to be clamped or to carry
   a named range proof; `@gpu` sweeps in the shape of `w30-thin-sigma-coverage.spec.ts` over **both
   halves** of each guarded ratio (the material's axis and the scene's) for the lens depth, the
   scatter widths and the tone knots; a readback guard that refuses a raster with an alpha hole
   inside a declared silhouette; `matrixSchemaRefusal`'s wording re-read against what trips it
   today; and the sweep rule recorded where consumer tables are written. Goldens 34/34
   byte-identical across G1 and G2; `freeze.py verify` 1,818 intact.
5. **The operator lands on the fidelity target with the CSS tier derived in the same commit, and
   the level is held.** The leaf at its inert identity in one commit under the digest rule the user
   chose (Decision Log 1 (a)); the identity proofs W30 established (the resolved-material identity
   test extended with the new leaf; the CSS declaration-identity case; the goldens; the 1,107
   gated-row pin). Then the fit per scheme on the calibration set (the probe `mid-chroma-solid`
   rows granted, as W30 Decision Log 2 (a) granted the ladder) through the reader with the holdout
   dropped by construction, checked on validation, the interior-level stop held, the receded
   documents inheriting; the macOS 27 documents re-sealed; `tier-coherence` green; the tinted cells'
   own chroma path proven unmoved (their rows expected unmoved, or the reason recorded).
6. **Read once per frozen configuration, under the ruled definition.** With the documents sealed and
   their hashes in the ledger, the canonical run appended beside the 0.20.0 rows — six profiles, two
   tiers, calibration + validation, the ladder — then the holdout **once**; the append-check; the
   split moves the generation this read supersedes; `freeze.py verify` 1,818 intact throughout. The
   verdict per profile per tier per clause with every missed cell named; a miss is recorded, not
   widened, not re-fitted; every passing tolerance G0 marked for adoption carried into
   `adopted-thresholds.test.ts`.
7. **The landing.** Sheets native | WebGPU | CSS | difference for the photo cells and
   `mid-chroma-solid` in both schemes at both scales, looked at, with what the eye sees recorded;
   the demo's figures on the operator; the coverage matrix re-scored where a row moved;
   `CLAUDE.md`, READMEs and CHANGELOG say what moved; the fixed group versioned **0.21.0** and
   prepared, `pnpm release` the user's hand, the tag after.

## Grounding Baseline (main at `8d9b6ceb`, 0.20.0 published)

- **The composite, and where the chroma goes.** The optics pass composites a neutral plate of alpha
  `sizedAlpha` over the blurred backdrop and solves the plate's luma so the post-collapse mean lands
  on the measured response — `mean = (1 − k)·M₀ + k·toneLuma`, `M₀ = (1 − α)·bgLinear + α·L(neutral)`
  (`optics.ts`, the W9 solve; "chroma is untouched — the shift is achromatic"). On the dark documents
  α is large, so the body is mostly neutral. The tint path carries its own chroma law
  (`tintChromaScale`, `rimTintChroma`, the adapted tint) and the recede carries a chroma collapse
  (W27c); neither is the untinted body's transmission. The CSS tier composes one `backdrop-filter`
  and one `rgba()` layer from the same profile (`platform-web/src/optics.ts`, `css-tier.ts`), pinned
  to the WebGPU tier by `tier-coherence.test.ts`.
- **The instrument today.** `metrics/material.ts`'s `tintResponse` reads the interior's MEAN linear
  RGB and the backdrop's, converts each to OKLab once, and reports `chromaDelta` as the difference
  of the two means' chromas, with `interiorChroma` and `backdropChroma` computed but not exported
  to the row (the row carries `tintDelta{L,A,B}`, `tintChromaDelta`, `tintHueShift`). On the dark
  1x `photo__rrect-lg__rest` row: native ΔA +0.0287 / ΔB −0.0217 / chroma +0.0022; web (dom)
  +0.0116 / −0.0069 / −0.0135. A mean-colour instrument cannot distinguish "the hues pass through"
  from "the mean is tinted"; the per-pixel one G0 adds can. The interior's luma spread
  (`interiorStdDev`) is the structure instrument and is not chroma.
- **The chroma-carrying cells.** `photo` is a deterministic multi-frequency colour field with
  saturated hue transitions (`scenes.json`); `mid-chroma-solid` is sRGB (213, 2, 255), the W27c
  chroma anchor, probe-only; the tinted cells carry the author's chroma on top of the backdrop's.
  Active untinted `photo` cells per profile: calibration `capsule-button`, `rrect-md`, `rrect-ml`;
  validation `rrect-sm`, `toolbar-group`; holdout `rrect-lg`, `glass-over-glass`. The inactive
  poses mirror that split. The bed for this operator is thin, which is why the probe anchor is
  granted to the fit and why the tolerance is read on the gated `photo` cells.
- **The four missed rows.** `MISSED_27_ROWS` holds seven: this cell's `oklabDeltaEP95` on
  `apple-macos-27.0-{1x,2x}-dark-standard-glass0.5` × `{texture,dom}` (0.21531 / 0.21341 against
  ≤ 0.17 on `texture`; 0.20095 / 0.19474 against ≤ 0.18 / ≤ 0.19 on `dom`), and three the σ law was
  declared to reach and did not (`checkerboard__rrect-lg__rest` and
  `checkerboard__glass-over-glass__rest :: ssimMean` on 1x-light dom, 0.88423 / 0.89531 against
  ≥ 0.9; `photo__rrect-lg__rest :: ssimOutside` on reduced-transparency dom, 0.82695 against ≥ 0.83).
  All seven are holdout rows.
- **The fingerprint and the exemption.** `fingerprint()` is SHA-256 over
  `withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch)` with keys sorted, first 16 hex. W30
  spent the one exemption W29 Decision Log 7 (a) granted: eight leaves at inert identities moved
  every document's digest; the two macOS 26.5 documents stayed byte-identical and
  `profiles/digest-supersessions.json` records `recordedSha256` → `currentSha256` per document
  (`b2b570e4adcea8fb` → `b340a4dee871633c`, `874be66ea501621b` → `93ab090705c43f1f`); the pin
  tests read `currentSha256` from the record. W30's charter weighed and withdrew a fingerprint
  blind to new leaves ("a default that can then change without any document being re-recorded",
  the `sizeOcclusionGain` failure) — the objection was to a pin blind by SCHEMA, so that an
  uncovered leaf's default could move unseen. Decision Log 1 (a) proposes a pin blind by VALUE:
  a leaf is dropped from the digest only while its resolved value equals its declared inert
  identity, so a moved default reappears in the digest the moment it moves. Adding a leaf at its
  identity then moves no digest at all, and the exemption class ends.
- **The holdout rule as practised.** W30 read the holdout twice at one document set — G3 at the
  sealed documents and G3b again after a renderer fix with no constant moved — and its review said
  a third read would need a ruling naming "the smallest thing that makes a configuration new"
  (§5.159b §10, finding 13). Decision Log 1 (b) drafts that ruling.
- **The exterior instrument.** Every row carries, on its `shadow` axis, `falloffSigma{Native,Web}`,
  `falloffAmplitude{Native,Web}`, `falloffSigmaResidual`, `meanDeparture{Native,Web}`, the
  `extent*`/`offset*` per direction, and the affine rings (`affineNative`/`affineWeb`: rendered
  against backdrop luminance per ring 0–3, 3–6, 6–12, 12–24, 24–48 CSS px, per direction). No
  adopted clause reads any of them; B3 (the departure residual) is a stop, not a bound.
- **Evidence layout.** `results/matrix.json` one generation per profile (1,833 rows / 66,075,976 B
  at W30's close); `results/superseded/` by active-document hash with `index.json`;
  `split-generation.py plan|apply` runs after the read that supersedes; `freeze.py verify` reads
  1,818 intact. The demo reads a build-time projection.
- **Tests that go red at a new default leaf** (W30 Grounding, unchanged): `tuned-profiles`,
  `macos26-document-selection`, `macos27-profile-export`'s digest case, `window-activation.spec.ts`'s
  eight hashes, `seal.ts`'s X1 loop, and now `w30-operator-identity.test.ts`. Under Decision Log
  1 (a)'s rule none of them moves for a leaf at its identity; under a second supersession all of
  them are re-recorded beside, as W30 G2 did.

## Design (advisory unless marked)

**The instrument (G0, clause 1).** A per-pixel OKLab read over the interior silhouette — for native,
web and backdrop — producing: mean per-pixel chroma; standard deviation of `a` and of `b`; the
chroma transmission ratio `mean chroma(interior) / mean chroma(backdrop)`; and the same ratio on
the spread (`sd(a,b)` interior over backdrop), which is the "hues pass through" reading. Exported
on the row's `material` axis beside the mean-based fields, never replacing them. Runs from the
fixture and the capture the row names; where the current generation's captures are not on this
machine's canonical tree, G0 says so and takes scratch captures for the cells it sheets under X6
(that is a browser run, not a read: nothing is appended).

**The mechanism (G0, clause 2).** Apple's dark body at the same luma keeps the backdrop's
chromaticity; a plate composite cannot, because `(1 − α)·bg + α·neutral` scales chroma by
`(1 − α)`. The shape the parent expects — advisory — is a **chroma retention** on the transmitted
backdrop: after the solve fixes the body's luma, the body's OKLab `a`/`b` are restored toward the
blurred backdrop's by a fraction `bodyChromaRetention ∈ [0, 1]` (inert 0: the plate as today; 1:
the backdrop's chromaticity at the solved luma), applied before the tint composition so the author's
tint still displaces the result per the composition contract, and before the recede's collapse so
the inactive pose's chroma law is unchanged in shape. Two values across the light and dark documents
(the renderer has no scheme input); the accessibility documents inherit the light value. The CSS
tier: `saturate()` in the one `backdrop-filter` scales the backdrop's chroma before the `rgba()`
layer covers it, which is the same algebra one layer earlier; whether one scalar projects the
retention well enough is a measured residual, recorded, and the CSS tier is never bounded on it.
G0 may name a different shape if the tables demand it; it may not name two.

**The digest rule (Decision Log 1 (a), for the user).** The fingerprint drops a leaf whose resolved
value equals its declared inert identity. The identity table is a committed, tested constant beside
`DEFAULT_MATERIAL_PROFILE` (leaf path → identity value → the law's proof); the unit case that a
leaf is inert at its identity is the law's, as W30 wrote them. Consequences, all proven by G0
before the ruling: the two macOS 26.5 documents' recorded digests become the live fingerprint
again (`b2b570e4adcea8fb`, `874be66ea501621b`); `digest-supersessions.json` becomes history with
its records kept; `material-document.ts` and `window-activation.spec.ts` return to the recorded
digests; the four macOS 27 documents' digests move once (they carry non-identity values on the σ
law and the scatter, which stay in the digest) and are re-sealed with history. The alternative is
W30's shape again — a second supersession row per document, a second exemption spent — which the
parent does not recommend: the class recurs every time an operator is added, and the rule closes it.

**The holdout rule (Decision Log 1 (b), for the user).** A frozen configuration is the pair
(the shipped document bytes, the renderer's material-affecting sources); the holdout is read once
per configuration; **no fitted constant may change between two holdout reads of the same document
bytes**, so a renderer fix may be re-read once and a fit may not — which is what W30 did and what
this rule writes down. The stricter alternative, once per wave, would have left 0.20.0's holdout
evidence at the unfixed renderer.

**The exterior clause (G1, advisory).** Two candidates, both from fields every row already
carries: (i) the fitted σ's error, `|falloffSigmaWeb − falloffSigmaNative| / falloffSigmaNative`
per cell, on cells whose fit converged (`falloffSigmaResidual` under the threshold G0 of W30
named), by span class; (ii) the departure profile's shape — the affine rings' `interceptC` and
`slopeA` against native per ring, which reads the exterior's level per distance band and is not
dominated by the interior. G1 tables both on the current generation, says which one the seven
missed rows move under, and declares the clause the next shadow wave adopts.

## Children

### G0: The chromatic cut, the instrument and the declarations — no material change

*Opens on main, parallel with G1 and G2. Read-only on the material; writes an instrument, evidence,
tables, tests and declarations.*

- (a) The per-pixel chroma instrument in `packages/calibration/src/metrics/` with unit cases on
  synthetic interiors (a grey plate over a colour field reads ratio 0; a pass-through reads 1);
  exported on the row beside the mean-based fields; the report/schema readers updated; the
  matrix's schema version and its refusal handled as the project does (no rewrite of any row: the
  new fields are absent on old rows and the readers say so).
- (b) The cut: the statistic over every chroma-carrying cell of the current generation from
  committed fixtures and the captures the ledger names (or scratch captures under X6, disclosed),
  tabled per backdrop class per scheme per tier per span, active and inactive, both scales; the
  26.5 rows beside; the 26.5→27 native delta on the same statistic. State plainly whether the
  light scheme has the residual too (the eye said the light photo cells beside it read grey).
- (c) The mechanism, from the shader: where chroma is lost, which documents exercise which path,
  the one leaf shape with its inert identity, the CSS projection and its expected residual, what
  the tinted cells' own chroma law does under it.
- (d) The digest-rule proof: the inert-identity table for every leaf added since the 26.5 seal
  (W30's eight) and for the leaf this wave names; a script that fingerprints each 26.5 document
  with identity-valued leaves dropped and shows `b2b570e4adcea8fb` / `874be66ea501621b`; the
  four 27 documents' digests under the rule, beside their current ones. No test or document
  changes: the proof is evidence for the ruling.
- (e) The declarations, committed last: tolerances with statistic and fate; the four rows claimed
  with lever and tier; the recede's worst cell reported; the stops (interior level per the adopted
  tables; the departure residual at B3's 0.00035; the shadow's and scatter's rows expected
  unmoved); the 27 tables cited from `adopted-thresholds.test.ts`, never transcribed; no floor.
- (f) Sheets: native | WebGPU | CSS | ×8 difference for `photo__rrect-md__rest`,
  `photo__rrect-lg__rest` and `mid-chroma-solid__capsule-button__rest` in both schemes at 1x, from
  the current generation, with what the eye sees written down before any fit exists.
- Ledger: **§5.161**. Evidence: `results/2026-09-21-w31-g0-chroma-cut/`.

### G1: The exterior-width instrument — parallel with G0

- The two candidate statistics computed over the current generation for every row with a shadow
  axis, from committed fields only; per cell, per span class, per scheme, per tier, per scale; the
  seven missed rows' readings under each; the non-converged fits excluded by the rule W30 G0 named
  (the 74.3 and 157.7 class) and counted. A reader script under the evidence dir, a unit case on a
  scratch matrix, and the clause declared — the statistic, the bound it would carry and the bed it
  is read on — as the **candidate adopted row for the wave that next moves the shadow**, recorded as
  a one-wave reading here. Nothing adopted, nothing fitted, no capture.
- Ledger: **§5.162**. Evidence: `results/2026-09-21-w31-g1-exterior-instrument/`.

### G2: The WGSL range class and the refusal's wording — parallel with G0 and G1

- (a) A unit case over `packages/renderer-webgpu/src/wgsl/*.ts` that finds every `exp`, `exp2`,
  `pow`, `tanh`, `log`, `sinh`/`cosh` call and requires its argument to be clamped in the same
  expression or to be listed in a committed range-proof table (call site → bound → why), which the
  case reads; every current call site classified, with the proofs written for the ones that need
  none.
- (b) `@gpu` sweeps in the shape of `w30-thin-sigma-coverage.spec.ts`, each over BOTH halves of its
  ratio — the material's axis and the scene's — for the lens depth, the scatter widths and the tone
  response's knots, asserting an invariant that does not depend on the swept value (coverage
  inside the silhouette; no NaN in the readback).
- (c) The readback guard: `renderScene`'s readback refuses a raster whose alpha has a hole inside
  a declared silhouette, with a case that a seeded NaN trips it.
- (d) `matrixSchemaRefusal`'s message re-read against what trips it today and rewritten; the
  consumer-table rule ("unchanged, checked" says what the file CLAIMS) recorded where such tables
  are written; the W30 G3b `glass-over-glass` residual (four dark cells, ≤ 8·10⁻⁴ px) re-read under
  (a)'s range proof and closed or left open with the reason.
- Goldens 34/34 byte-identical; `test:gpu` green; no material change; both tracker entries
  amended beside.
- Ledger: **§5.163**. Evidence: `results/2026-09-21-w31-g2-range-class/`.

### G3: The leaf and the fit — opens after G0's declarations, G1 and G2 merged, and Decision Log 1 (a) and (b) ruled

- (a) The leaf in one commit at its inert identity: `MaterialProfile`, `MaterialProfilePatch`,
  `withMaterialOverrides`, the allowlists, the CSS mirror, the uniform and the shader with the
  composite bit-identical at the identity; under the digest rule if ruled (the identity table, the
  fingerprint's rule, the pins returning to the recorded digests, the four 27 documents re-sealed
  with history) or under a second supersession row if that is the ruling; the identity test's leaf
  list extended; the CSS declaration-identity case; the inert-law unit case; a `test:gpu` case that
  the on state draws differently from off. Proofs as W30 G2's, each output committed.
- (b) The fit per scheme on calibration + the granted probe anchor through the reader with the
  holdout dropped, checked on validation; the interior-level stop and the departure stop held; the
  receded documents inheriting; the tinted cells read before and after; the 27 documents re-sealed;
  `tier-coherence` green; the CSS projection's residual measured and recorded; `PREDICATE_EXCLUDES`
  and every count test moved to what the machine says; a changeset (a `@vitreajs/vitrea-web`
  minor at least); sheets at the fit by eye.
- Ledger: **§5.164**. Evidence: `results/2026-09-21-w31-g3-chroma-fit/`.

### G4: The sealed read, the verdict, and the landing — 0.21.0 prepared

- (a) RT and IC read 0, `NSGlassTintAmount` 0.5, one capture process, idle ≥ 60 s; the sealed
  hashes in the ledger before the read; the canonical run over six profiles × two tiers,
  calibration + validation + ladder appended beside the 0.20.0 rows; holdout **once** under the
  ruled definition; the append-check; the split; the append-check again; freeze 1,818.
- (b) The verdict per profile per tier per clause; the claimed, expected-unmoved and reported rows
  each named with before and after; adoptions carried in; misses recorded; Decision Log entries
  drafted where a ruling is needed.
- (c) The landing: sheets, the demo's figures, the coverage matrix, `CLAUDE.md`, READMEs,
  CHANGELOG; the fixed group versioned 0.21.0, dry runs green, unpublished.
- Ledger: **§5.165**. Evidence: `results/2026-09-21-w31-g4-landing/`.

## Cross-Child Contracts

- **X1 — the freeze, intact.** No macOS 26.5-keyed path, row, bound, floor or document changes;
  `freeze.py verify` reports 1,818 intact at every merge; the 34 goldens byte-identical through G1,
  G2 and G3's leaf commit; the 1,107 gated-row pin holds. No exemption is spent without the ruling
  in Decision Log 1 (a), and if the rule is chosen no exemption is spent at all.
- **X2 — the cut precedes the operator.** G0 names the leaf shape and its identity from the
  instrument's tables before G3 writes a leaf; G3 adds no leaf G0 did not name.
- **X3 — the operator changes nothing outside the body's chroma path.** The σ law, the scatter, the
  tone solve's luma, the anchors, the tint's chroma law and the recede's collapse do not move; a fit
  that moves a shadow, structure or tint row is a warning, not a result.
- **X4 — bounds before reads; holdout once under Decision Log 1 (b); a miss is recorded.**
- **X5 — no native capture; the granted bundle is never rebuilt and nothing is added under its
  identifier.** Every fixture is on disk from W29.
- **X6 — RT and IC 0, the slider 0.5, one capture process, ≥ 60 s idle** before every browser run,
  scratch captures included; every run recorded.
- **X7 — the evidence layout changes by the one rule**: the split after the read that supersedes;
  every superseded row one `git show` away; the freeze's row hashes verify at every merge.
- **X8 — padding untouched.** The chroma term reaches no pad; the advisory constant's retirement
  stays undecided.
- **X9 — no GPT-rung agents**; children and reviews are opus `general-purpose` (read-only for
  reviews); ledger sections assigned above; merges `--no-ff -F <file>` with the freeze verified at
  each; no attribution trailers, no session URLs; committed evidence never rewritten.

## Ordering & Dependency Map

Charter → adversarial review → fold → **G0 ∥ G1 ∥ G2** → each merged and reviewed → the user rules
Decision Log 1 (a), (b) (and (c) whenever) → **G3** → **G4** → the user's eye on the sheets →
`pnpm release` (the user) → tag. After this wave, in the order W30's Deferred kept: the analysis
pass (W30 Deferred 2, the user's to charter); the shadow's next wave carrying G1's clause; the
identifying sitting on the 27 bed; the highlight's angular reader; the decoupled-contrast flag and
its read; the motion-metrics harness.

## Risks & Mitigations

- **The chroma term moves the level.** The retention acts on OKLab `a`/`b` at the solved luma, and
  the interior-level rows are declared stops; G3 reads them before and after on scratch.
- **The bed is thin: five gated untinted photo cells per profile.** The probe anchor is granted to
  the fit; the tolerance is read on the gated `photo` cells; the tinted cells are read as a check,
  not fitted on; a fit that only matches `mid-chroma-solid` shows on the photo rows.
- **The tinted cells' chroma law absorbs it.** Their rows are declared expected unmoved; the
  retention is applied before the tint composition, and G0 says what the tint path does under it.
- **The CSS projection is wrong in one scheme.** Recorded, never bounded; `tier-coherence` pins the
  projection's derivation, not its residual.
- **The light scheme has no residual and the leaf is fitted to zero there.** A declined value is a
  measurement, recorded as W30 recorded the light scatter.
- **The digest rule hides a leaf whose identity is mis-declared.** The identity table is tested by
  the law's own inert-identity unit case; a leaf enters the table only with that case.
- **The rulings arrive late.** G0, G1 and G2 need none; G3 waits; the wave loses no time before it.
- **A read appends to a 66 MB file.** X7, once.

## Deferred / Out of Scope

The analysis pass's scale statistic (W30 Deferred 2); the shadow's next fit under G1's clause (the
seven rows are not claimed through the shadow here; the four dark ones are claimed through the
chroma); the highlight's angular reader; the decoupled increased-contrast read and `compare`'s
flag; the identifying sitting; the motion-metrics harness; the CSS tier over pure black; inactive
calibration cells above span 96; `samplingPaddingFor`'s advisory constant; the Reduced Transparency
opacity policy and the impulse specular point; the slider's ends as evidence classes; a shadow
section for `/laws/` (W30 Deferred 10); the thin regime's instrument (W30 Deferred 4); the light
bed's 16 px structure (W30 Deferred 3).

## Tracking Map

| Child | Status | Claims section | Evidence |
| --- | --- | --- | --- |
| G0 | OPEN | §5.161 | `results/2026-09-21-w31-g0-chroma-cut/` |
| G1 | OPEN | §5.162 | `results/2026-09-21-w31-g1-exterior-instrument/` |
| G2 | OPEN | §5.163 | `results/2026-09-21-w31-g2-range-class/` |
| G3 | not dispatched — Decision Log 1 ruled; waits on G0–G2 merged | §5.164 | `results/2026-09-21-w31-g3-chroma-fit/` |
| G4 | not dispatched | §5.165 | `results/2026-09-21-w31-g4-landing/` |

## Decision Log

### Decision Log 1 — RULED 2026-09-21 (the user: "all according to you recommendation", on the parent's draft below): the digest rule by value, the holdout rule as practised, the tone stage kept

**Ruled.** (a) **The fingerprint drops a leaf whose resolved value equals its declared inert
identity** — option (i); no exemption is spent by this wave or by any later inert-leaf addition,
the two frozen macOS 26.5 documents' recorded digests become the live fingerprint again, and
`digest-supersessions.json` becomes history with its records kept. G0 proves the rule reproduces
the recorded digests before G3 executes it. (b) **A frozen configuration is (the shipped document
bytes, the renderer's material-affecting sources); the holdout is read once per configuration; no
fitted constant may change between two holdout reads of the same document bytes.** A renderer fix
after a read may be re-read once and disclosed as such; a fit may not. (c) **The tone stage stays
as re-ranged**, with the 40 px plate's band recorded in the tracker; W29 Deferred item 8 and the
tracker's "designed around a convergence macOS 27 does not have" entry close on this ruling, which
G4 records beside them.

*The draft as put to the user:*


**(a) The digest rule — the parent recommends the rule.** Either (i) **the fingerprint drops a leaf
whose resolved value equals its declared inert identity**, with the identity table a tested
constant beside the default, so that adding an operator at its identity moves no document's
digest, the two frozen macOS 26.5 documents' recorded digests are the live fingerprint again, the
supersession record becomes history, and no wave spends an exemption for an inert leaf again; or
(ii) **a second one-time exemption** in W30's shape — a second row per frozen document in
`digest-supersessions.json`, every digest site re-recorded beside — spent by this wave for one leaf,
with the class recurring at the next operator. G0 proves (i) computes the recorded digests before
the user rules. W30's objection to a schema-blind pin does not reach (i): a leaf whose default
moves off its identity reappears in the digest the moment it moves.

**(b) The holdout rule — the parent recommends codifying W30's practice.** A frozen configuration
is (the shipped document bytes, the renderer's material-affecting sources); the holdout is read
once per configuration; **no fitted constant may change between two holdout reads of the same
document bytes.** A renderer fix after a read may be re-read once and disclosed as such; a fit may
not. The alternative — once per wave, full stop — is stricter and would have left 0.20.0's holdout
evidence at the unfixed renderer.

**(c) The tone stage — the parent recommends keeping it as re-ranged.** §5.160 §4 read the range
the ruling asked for and found the premise reversed: the three plates separate most over the dark
half (10.4 % spread over the mean) and least at the bright end (2.3 %), and what closes at the
bottom is their ORDER, not their separation. The re-ranged stage is true to that reading and its
prose says so; retirement removes the one live figure on the site that shows the tone law across a
ground, and what it would spare is the 40 px plate's published-alpha band (tracker). Keep, with the
band recorded, unless the user's taste says the reversal makes the section say the wrong thing.

## Surprises & Discoveries

*(none yet)*

## Outcomes & Retrospective

*(at close)*

## Revision Notes

- 2026-09-21 (the parent): **Decision Log 1 ruled by the user** — "all according to you
  recommendation" — before the adversarial review returned: the digest rule by value, the holdout
  rule as W30 practised it, the tone stage kept. G3's precondition is now the review's fold and
  the three instrument children's merge.
- 2026-09-21: v1 of this charter, drafted by the parent from a read-only grounding of the composite,
  the chroma instrument, the four missed rows, W30's Deferred-at-close list and the two rulings its
  review asked for. Sent for adversarial review before any child opens.
