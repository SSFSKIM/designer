# W31 — the chromatic wave: the body carries the backdrop's hue, with three instruments in front

**Status: CLOSED 2026-09-21 by G4's landing**, against all seven Parent-Level Acceptance clauses
(Outcomes & Retrospective) — **clause 7 on the `photo` half only: the chartered `mid-chroma-solid`
sheets were not made, and that is a scoping choice rather than a contract, recorded beside the
verdict and at Deferred item 9** (2026-09-21, review closure; claims §5.165 §9, finding R2).
**0.21.0 is prepared and UNPUBLISHED**: `pnpm release` is the user's hand and the tag `v0.21.0`
follows it. The user's eye on the sheets is the one remaining acceptance
input; `packages/calibration/results/2026-09-21-w31-g4-landing/eye.md` is the implementer's, and it
records no regression on the accessibility band and no reason to stop the cut.

**0.21.0 PUBLISHED 2026-09-21, by the user's `pnpm release` on `c87b5493` (the parent's final
chain record, the head at publish); tag `v0.21.0` annotated on that commit and pushed by the
parent the same day.** Registry: core 08:10:02.146Z, react 08:10:04.854Z, web 08:12:09.283Z — the
record beside the "prepared and UNPUBLISHED" status above, as the 0.20.0 record sits in W30; the
verification is in §Outcomes & Retrospective.

*Opened as:* **OPEN 2026-09-21 — chartered by the parent on the user's "let's proceed with next wave"
after the 0.20.0 publish, under the standing "rest on your judgement"; adversarially reviewed the
same day and the review folded (v2, Revision Notes).** Executes W29 Decision Log 6 (c) (the
chromatic-transmission child, the largest residual on W30's own sheets) and carries three of W30's
Deferred-at-close items whose evidence is on disk and which need no ruling: the exterior-width
instrument (item 1), the WGSL range class (item 12) and the refusal-wording sweep (item 13).
Grounded on main at `8d9b6ceb` (0.20.0 published). **Three rulings were drafted for the user in
Decision Log 1 and ruled the same day, all as recommended (the digest rule by value, the holdout
rule as practised, the tone stage kept); the three instrument children run first.**

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
a chroma-retaining term in the body's composite, fitted per scheme, with the level held in the
renderer's own linear luma.

The review of this charter named the trap in that sentence and the wave is written around it:
W29 Decision Log 6 (c) framed the finding on the interior's SPREAD (0.0417 against 0.0142) and
said the chromatic residual and §5.151 §5's "conditioned on something beyond the backdrop's
mean" are "plausibly the same finding read two ways". vitrea passes about a quarter of the native
structure on that cell (`interiorStdDev` 0.0091 / 0.0141 against 0.0417, over a backdrop at
0.1256), and this wave declines to touch the structure (X3; the analysis pass is deferred). A
per-pixel chroma ratio read against the raw backdrop measures the blur and the chroma loss
together, so a retention fitted to close it would absorb the structure deficit as saturation and
call it a result. The instrument is therefore defined so that the blur cancels (Design), the
acceptance is web against NATIVE on the same cell and never against 1, and the four claimed rows
are decomposed into their luma and chroma parts before any claim is declared.

Three instruments come first, in parallel, because their evidence is on disk and none needs a
ruling. **The exterior's width** (W30 Deferred 1): the three rows W30 claimed through the σ law
moved by 0.0002 where they needed 0.016, because whole-cell SSIM is dominated by the interior, while
`falloffSigmaWeb` — the axis the lever actually moves — moved by up to 30 CSS px under no gated
bound on the rendered side (B1 bounds the DOCUMENT's law against the native σ, and is green at
±0.685 % on the light document while the rendered σ disagrees — that disagreement is itself a
finding G1 surfaces). **The WGSL range class** (W30 Deferred 12): the `tanh` overflow is fixed as
an identity and the class is not; `src/wgsl/` has sixteen transcendental call sites on
document-scaled quantities with nothing asserting an argument stays where the result is finite in
f32. **The refusal's wording and the sweep rule** (W30 Deferred 13): `matrixSchemaRefusal` still
offers an operator a ruling that ended.

What this wave does **not** do: it does not move the shadow's σ law, the scatter, the tone
response's abscissa, any anchor, or the CSS tier's existing `saturate()` constants (X3); it does
not build the highlight's angular reader; it does not fix `compare`'s decoupled-contrast flag; it
does not re-open the analysis pass (W30 Deferred 2, the user's to charter); it captures **no native
pixel**; and it does not bump the matrix schema.

## Parent-Level Acceptance

1. **The chroma is measured before the operator exists, by an instrument in which the blur
   cancels.** The matrix's `tintChromaDelta` is over the interior's MEAN OKLab against the
   backdrop's mean, so a balanced photograph whose hues pass through reads near zero on both
   sides; it is the wrong instrument for this residual and G0 says so with the numbers. G0 adds a
   per-pixel chroma instrument to `packages/calibration` — per pixel over the interior silhouette,
   the mean OKLab chroma and the standard deviations of `a` and `b`, for native, web and backdrop
   — and reads it as a **chroma-to-structure ratio**: the interior's per-pixel chroma spread over
   its own luma spread, so a body that blurs more but keeps its hues reads the same as one that
   blurs less. The raw-backdrop ratio is tabled beside it so the confound is visible, and the
   backdrop blurred at the material's own radius is a third column where G0 can compute it. Every
   statistic is stated as **web against native on the same cell**, never against 1. The new fields
   are **optional additions at schema 5, no version bump**, on `drawnAreaWeb`'s precedent
   (`report.ts`); they cannot reach the 1,818 frozen rows, so the macOS 26.5 readings live in the
   evidence directory only and any adopted row on the statistic is macOS 27-only. The web side of
   the chroma bed is **re-captured as scratch** (no current-generation capture tree exists on this
   machine — Surprises), and for every re-captured cell G0 re-derives at least one committed metric
   and shows it reproduces the committed row within the repeat noise before reading a new
   statistic off it. The native delta between 26.5 and 27 on the same statistic is recomputed from
   the fixture pairs, so the wave knows whether Apple moved the chroma or vitrea never had it.
2. **The mechanism is named from the shader, and the leaf shape from the tables.** G0 states, from
   `optics.ts` and `material.ts`, exactly where the backdrop's chroma is lost (the plate's alpha in
   the composite; the achromatic solve), that the two collapses are different things (the backdrop
   tone collapse `toneAdapt` pulls `adapted` toward `toneTarget` for every body; W27c's chroma
   collapse acts on the tint SEED inside `if (tintK > 0.0)` and does nothing to an untinted body),
   which of those the light and dark documents exercise at the photo cells' levels, and names
   **one** leaf shape with its inert identity under which every shipped document is bit-identical:
   a chroma retention on the composited colour that is **luma-preserving in the renderer's own
   linear luma** (restore chromaticity, then renormalise so `dot(rgb, (0.2126, 0.7152, 0.0722))`
   is unchanged), with its gamut behaviour stated (chroma scaled down until in gamut with luma
   held, never clipped per channel), its behaviour as a function of `toneAdapt` stated (a gate, or
   the reason none is needed), its place in the shader's order named (after
   `colour = mix(backdrop, adapted, presentAlpha)` and before the tint composition, so the author's
   tint still displaces the result per the composition contract), and the receded documents
   carrying their **own** value read on the inactive cells rather than inheriting one nobody
   measured. "Conditioned by scheme" means two values of one leaf in the light and dark documents.
   It says what the CSS tier's two layers can carry of it: the tier's `backdrop-filter` already
   carries a CSS-only `saturate()` at 1.8 (regular) / 1.4 (clear) that the renderer has no
   counterpart to, whose value does not move (X3); a projection of the retention onto that layer
   acts BEFORE the `rgba()` plate covers it, so the reachable interior chroma is bounded by
   `(1 − α)·s` and the ceiling is lowest in the dark scheme — G0 states that analytic ceiling per
   scheme as a **declared residual** before the fit, and whether a derived term is worth adding or
   the CSS tier records the residual and carries nothing.
3. **Bounds before reads; the stop is a number; the rulings are already made.** G0 declares the
   wave's acceptance — a tolerance on the chroma-to-structure ratio, web against native, per
   backdrop class per scheme on the WebGPU tier with the CSS tier recorded, with the statistic
   (which cells, which order statistic, which conditioning, the noise bar it is justified from)
   — and its fate: **a one-wave reading unless G0 makes the identifiability argument**, because a
   chroma row adopted at G4 would be the first material-axis adopted row in
   `adopted-thresholds.test.ts`, whose header says the material axis is not gated on this fixture
   set; the parent decides at G4 on G0's argument. **The level stop is an explicit numeric
   tolerance on `interiorMeanWeb` against `interiorMeanNative` per cell, declared by G0 from the
   committed rows and read before and after on scratch** — there is no adopted interior-level row
   to cite (the only one, `interiorLevelRatioGpuOverCss`, is blind to both tiers moving together).
   The four missed `oklabDeltaEP95` rows are **decomposed** on the committed captures into their
   ΔL and Δ(a,b) parts (the P95 is over the whole capture, interior, rim and exterior together) and
   the headroom the chroma lever alone can reach is stated; each row is then declared CLAIMED or
   "reachable if" on that number, with the lever and the tier, and what the fit is judged on
   BEFORE the holdout read (the gated photo cells on calibration + validation) is named, since all
   four are holdout rows. The recede's worst cell is reported. The shadow's, the scatter's and the
   tinted cells' rows are declared expected unmoved. The 27 tables stay at their ruled values; no
   floor. **G0 also proves what Decision Log 1 (a) ruled**: the fingerprint of each macOS 26.5
   document with every identity-valued leaf (and gate-group) dropped equals the document's own
   recorded `resolvedMaterialSha256` (`b2b570e4adcea8fb`, `874be66ea501621b`), with the identity
   table committed beside the proof and the holes the rule does not cover named.
4. **Three instruments land without a material change.** G1: the two exterior statistics, a
   reader, candidate (i) tabled beside B1's per-bed windows on the same cells with what a
   divergence means, and a clause shape declared as the candidate adopted row for the wave that
   next moves the shadow, read on the current generation as a one-wave reading with the seven
   missed rows' figures beside — not adopted, not fitted. G2: a unit case over `src/wgsl/`
   requiring every transcendental's argument to be **clamped to a range on which the result is
   finite in f32, per argument** (a `pow` base non-negative), or to carry a named range proof;
   `@gpu` sweeps in the shape of `w30-thin-sigma-coverage.spec.ts` over **both halves** of each
   guarded ratio (the material's axis and the scene's) for the lens depth, the scatter widths and
   the tone knots; a readback guard whose predicate is an ENCLOSED region of zero alpha inside a
   declared silhouette (not any low alpha — the unsampled layer path writes a translucent interior
   and `dom_material_alpha` is 0 at presence 0, both stood down by rule); `matrixSchemaRefusal`'s
   wording re-read against what trips it today; and the sweep rule recorded where consumer tables
   are written. Goldens 34/34 byte-identical across G1 and G2; `freeze.py verify` 1,818 intact.
5. **The operator lands on the fidelity target with the CSS tier derived in the same commit, the
   level held, and the re-seal and the read in ONE merge.** The leaf at its inert identity, the
   digest rule executed (the identity table with gate-groups; `fingerprint()` under the rule in
   `seal.ts` and both test copies; the pins returning to the recorded 26.5 digests; the four
   macOS 27 documents re-sealed with history and the rule's version recorded in them), the
   identity proofs W30 established (the resolved-material identity test extended; the CSS
   declaration-identity case; the goldens; the 1,107 gated-row pin); then the fit per scheme on the
   calibration set (the probe `mid-chroma-solid` rows granted, as W30 Decision Log 2 (a) granted
   the ladder) through the reader with the holdout dropped by construction, checked on validation,
   the level stop held, the receded documents read on the inactive cells; the macOS 27 documents
   re-sealed; `tier-coherence`'s mirror list extended with a case that the list is exhaustive over
   `MaterialProfile`'s keys (green is otherwise vacuous for a new leaf); the tinted cells read
   before and after. **Every re-seal of a macOS 27 document empties the 27 bed out of every bound
   until rows at its bytes exist** (`atAShippedDocument` hashes the documents' bytes; 230 gated
   cells / 726 rows today), so — as W30 Decision Log 4 (b) ruled — the re-seal and the canonical
   read at those bytes land in one merge: **G3 fits, seals and reads; G4 lands** (Ordering, X10).
6. **Read once per frozen configuration, under the ruled definition as enforced by artifact.** The
   configuration is recorded in the read's own evidence as the four document file hashes plus a
   hash over an enumerated source list (`packages/renderer-webgpu/src/wgsl/`, `src/material.ts`,
   `src/renderer.ts`, `src/passes.ts`, `packages/platform-web/src/{optics,css-tier}.ts`); a second
   read of the same document hashes requires the source hash to have moved for a named non-fit
   reason. With the documents sealed and their hashes in the ledger, the canonical run appended
   beside the 0.20.0 rows — six profiles, two tiers, calibration + validation, the ladder — then
   the holdout **once**; the append-check; the split moves the generation this read supersedes;
   the read's capture tree copied to the canonical `web-captures/` on the main checkout at merge
   (Surprises); `freeze.py verify` 1,818 intact and the 27 gated-cell count pinned throughout. The
   verdict per profile per tier per clause with every missed cell named; a miss is recorded, not
   widened, not re-fitted; every passing tolerance G0 marked for adoption carried into
   `adopted-thresholds.test.ts` on the parent's decision.
7. **The landing.** Sheets native | WebGPU | CSS | difference for the photo cells and
   `mid-chroma-solid` in both schemes at both scales, looked at, with what the eye sees recorded;
   the demo's figures on the operator; the coverage matrix re-scored where a row moved;
   `CLAUDE.md`, READMEs and CHANGELOG say what moved; the tone stage's two open records closed on
   Decision Log 1 (c); the fixed group versioned **0.21.0** and prepared, `pnpm release` the
   user's hand, the tag after.

## Grounding Baseline (main at `8d9b6ceb`, 0.20.0 published)

- **The composite, and where the chroma goes.** The optics pass composites a neutral plate of alpha
  `sizedAlpha` over the blurred backdrop and solves the plate's luma so the post-collapse mean lands
  on the measured response — `mean = (1 − k)·M₀ + k·toneLuma`, `M₀ = (1 − α)·bgLinear + α·L(neutral)`
  (`optics.ts`, the W9 solve; "chroma is untouched — the shift is achromatic"), luma being LINEAR
  luma, `dot(rgb, (0.2126, 0.7152, 0.0722))`, which is also what `interiorLevel` measures in
  `metrics/material.ts`. On the dark documents α is large, so the body is mostly neutral. The
  backdrop tone collapse (`toneAdapt`, `adapted` toward `toneTarget`) acts on every body; the
  composite is `colour = mix(backdrop, adapted, presentAlpha)`; the tint path carries its own
  chroma law (`tintChromaScale`, `rimTintChroma`, the adapted tint) and W27c's chroma collapse acts
  on the tint seed inside `if (tintK > 0.0)` — so an untinted receded body, the recede's worst
  cell's population, has no chroma law at all today. The CSS tier composes one `backdrop-filter`
  and one `rgba()` layer from the same profile (`platform-web/src/optics.ts`, `css-tier.ts`), pinned
  to the WebGPU tier by `tier-coherence.test.ts` over an ENUMERATED list of constants; the filter
  already carries `saturate()` at 1.8 / 1.4, documented as CSS-only with no renderer counterpart,
  and the dom tier's chroma reads −0.01345 against texture's −0.01457 on the dark photo cell — the
  existing 1.8× buys about 0.001.
- **The instrument today.** `metrics/material.ts`'s `tintResponse` reads the interior's MEAN linear
  RGB and the RAW backdrop's under the same mask, converts each to OKLab once, and reports
  `chromaDelta` as the difference of the two means' chromas, with `interiorChroma` and
  `backdropChroma` computed but not exported to the row. On the dark 1x `photo__rrect-lg__rest`
  row: native ΔA +0.0287 / ΔB −0.0217 / chroma +0.0022; web (dom) +0.0116 / −0.0069 / −0.0135. The
  mean gap between native and web is about 0.023 in OKLab, a sixth of the P95 the four rows carry.
  `oklabDeltaE` (`metrics/perceptual.ts`) is a per-pixel distance over the WHOLE capture. The
  interior's luma spread (`interiorStdDev`) is the structure instrument: backdrop 0.1256, native
  0.0417 (0.33 of it), web 0.0091 / 0.0141 (0.073 / 0.11).
- **The chroma-carrying cells, and their conditioning.** `photo` is a deterministic multi-frequency
  colour field with saturated hue transitions (`scenes.json`); `mid-chroma-solid` is sRGB
  (213, 2, 255), the W27c chroma anchor, probe-only; the tinted cells carry the author's chroma on
  top of the backdrop's. Active untinted `photo` cells per profile: calibration `capsule-button`,
  `rrect-md`, `rrect-ml`; validation `rrect-sm`, `toolbar-group`; holdout `rrect-lg`,
  `glass-over-glass`; the inactive poses mirror that split. **On the dark profiles,
  `photo__capsule-button__rest`, `photo__rrect-md__rest` and `photo__rrect-lg__rest` are in
  `PREDICATE_EXCLUDES` at both scales and both tiers** — the silhouette-quality predicate refuses
  them (`photo__rrect-lg__rest` 1x dark: `silhouetteAreaNative` 39,392 against a region of 43,816,
  3 bodies, 68 holes) — which leaves the dark calibration bed at one well-conditioned untinted
  photo cell (`rrect-ml`) plus the probe anchor. The material metrics read the declared interior
  mask, not the contour; G0 reports the conditioning state of every cell the fit and the tolerance
  read and says, with evidence, whether a mask the shape rows refuse is adequate for a per-pixel
  chroma statistic.
- **The four missed rows.** `MISSED_27_ROWS` holds seven: this cell's `oklabDeltaEP95` on
  `apple-macos-27.0-{1x,2x}-dark-standard-glass0.5` × `{texture,dom}` (0.21531 / 0.21341 against
  ≤ 0.17 on `texture`; 0.20095 / 0.19474 against ≤ 0.18 / ≤ 0.19 on `dom`), and three the σ law was
  declared to reach and did not (`checkerboard__rrect-lg__rest` and
  `checkerboard__glass-over-glass__rest :: ssimMean` on 1x-light dom, 0.88423 / 0.89531 against
  ≥ 0.9; `photo__rrect-lg__rest :: ssimOutside` on reduced-transparency dom, 0.82695 against ≥ 0.83).
  All seven are holdout rows.
- **The bed's byte dependence.** `SHIPPED_DOCUMENT_HASHES` is built from the bytes of every file
  in `profiles/`; `atAShippedDocument` keeps rows whose `capturePath` names a current hash;
  `MATRIX_CELLS = 459` and the 27 half of it — 230 gated cells, 726 rows across six profile keys —
  drops the moment a 27 document's bytes change, restored only by rows read at the new bytes.
  `resolvedMaterialSha256` and `$comment-sha-history` live inside the documents, so a re-seal is a
  byte change. W30 Decision Log 4 (b): a re-seal and its canonical read land in ONE merge.
- **The fingerprint and the rule.** `fingerprint()` is SHA-256 over
  `withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch)` with keys sorted, first 16 hex,
  duplicated in `seal.ts`, `tuned-profiles.test.ts` and `macos26-document-selection.test.ts`. W30
  spent the one exemption W29 Decision Log 7 (a) granted: eight leaves at inert identities moved
  every document's digest; the two macOS 26.5 documents stayed byte-identical and
  `profiles/digest-supersessions.json` records `recordedSha256` → `currentSha256` per document
  (`b2b570e4adcea8fb` → `b340a4dee871633c`, `874be66ea501621b` → `93ab090705c43f1f`). **Three of the
  eight leaves have no standalone identity by the material's own words**: `sigmaSpanRefPx` is inert
  because the slope is 0 whatever the pivot holds; `sizeHeavySecondSigma{,2x}` are unread while
  `sizeHeavySecondShare` is 0; `sizeScatterScaleRef` cannot reach the mix while
  `sizeScatterScaleGain` is 0 — and the light 27 document ships it at 0.03 with the gain at 0,
  provably inert and off any would-be identity. Decision Log 1 (a) as executed therefore drops
  **gate-groups**: a gated leaf is dropped only jointly with its gate at the gate's identity
  (Design). Under the rule the 26.5 digests reproduce because every post-seal leaf is at its
  identity there, which makes the identity table a permanent constraint on
  `DEFAULT_MATERIAL_PROFILE`: a post-seal leaf's default IS its identity, forever, and the table is
  append-only.
- **The holdout rule as practised.** W30 read the holdout twice at one document set — G3 at the
  sealed documents and G3b again after a renderer fix with no constant moved — and its review said
  a third read would need a ruling naming "the smallest thing that makes a configuration new"
  (§5.159b §10, finding 13). Decision Log 1 (b) ruled it; clause 6 enforces it by artifact.
- **The exterior instrument.** Every row carries, on its `shadow` axis, `falloffSigma{Native,Web}`,
  `falloffAmplitude{Native,Web}`, `falloffSigmaResidual`, `meanDeparture{Native,Web}`, the
  `extent*`/`offset*` per direction, and the affine rings (`affineNative`/`affineWeb`: rendered
  against backdrop luminance per ring 0–3, 3–6, 6–12, 12–24, 24–48 CSS px, per direction). No
  adopted clause reads any of them from the rendered side; B1 (adopted at W30 G4) bounds the
  DOCUMENT's σ law against the native σ per bed at ±5 % (±0.685 % effective on the light document);
  B3 (the departure residual) is a stop, not a bound.
- **Evidence layout.** `results/matrix.json` one generation per profile (1,833 rows / 66,075,976 B
  at W30's close); `results/superseded/` by active-document hash with `index.json`;
  `split-generation.py plan|apply` runs after the read that supersedes; `freeze.py verify` reads
  1,818 intact; `deserializeResultMatrix` hard-refuses any envelope whose `schemaVersion` differs
  from the build's, so a schema bump would make the append impossible and additions are optional
  fields at schema 5. The demo reads a build-time projection.
- **Where the captures are.** `packages/calibration/web-captures/` on the main checkout holds the
  six macOS 26.5 trees only (last written 2026-09-15). Two agent worktrees hold macOS 27 trees at
  document hashes `96b36eedf1c4` and `272d1b0c3e10` — earlier generations, not the current
  `880ab1e31450` family; G3b's worktree, which read the current generation, is gone. Captures are
  gitignored and a worktree inherits none. So the chroma bed's web side does not exist on disk at
  the current generation and G0 re-captures it as scratch (clause 1).
- **Tests that go red at a new default leaf** (W30 Grounding, unchanged): `tuned-profiles`,
  `macos26-document-selection`, `macos27-profile-export`'s digest case, `window-activation.spec.ts`'s
  eight hashes, `seal.ts`'s X1 loop, and `w30-operator-identity.test.ts`. Under the rule none of
  them moves for a leaf at its identity; the four 27 digests move once when the rule itself lands,
  in G3's one merge.

## Design (advisory unless marked)

**The instrument (G0, clause 1).** Per pixel over the interior silhouette, OKLab for native, web
and backdrop; per cell: mean per-pixel chroma, sd(a), sd(b), and the luma sd the row already
carries. The reading the bound is declared on is the **chroma-to-structure ratio**
`sqrt(sd(a)² + sd(b)²) / sd(L_linear)` of the interior, web against native on the same cell: a
body that blurs more but keeps its hues reads the same as one that blurs less, so the structure
deficit this wave does not touch cancels rather than being absorbed. Tabled beside it: the raw
ratio (interior per-pixel chroma over the raw backdrop's, the confounded one, so the reader sees
the confound), and the blurred-reference ratio (the backdrop blurred at the material's own radius)
where G0 can compute the radius from the document. Unit cases: a grey plate over a colour field
reads 0 on every ratio; a luma-only darkening leaves the chroma-to-structure ratio unchanged; a
blur alone leaves it unchanged while it moves the raw ratio. Exported on the row's `material` axis
as optional fields at schema 5 beside the mean-based ones, never replacing them.

**The mechanism (G0, clause 2).** Apple's dark body at the same luma keeps the backdrop's
chromaticity; a plate composite scales chroma by `(1 − α)`. The shape the parent expects —
advisory — is a **chroma retention** on the composited colour: after
`colour = mix(backdrop, adapted, presentAlpha)`, restore the colour's chromaticity toward the
blurred backdrop's by `bodyChromaRetention ∈ [0, 1]` (inert 0) **and renormalise so the linear
luma is exactly what the solve produced** (OKLab L is not linear luma: holding L while moving
toward a saturated chromaticity changes Y by −22 % at sRGB blue, −14 % at red, +10 % at green;
`mid-chroma-solid` sits at ratio ≈ 0.82). Gamut: scale the chroma down until every channel is in
[0, 1] with the luma held, never clip per channel. Gate: state the term as a function of
`toneAdapt` — at high adaptation the reference renders a flat dark body and a retention with no
gate would add chroma the reference does not have; G0 reads the photo cells' `toneAdapt` and says
whether `(1 − toneAdapt)` or nothing is the gate. Before the tint composition, so the author's
tint still displaces the result. The receded documents carry their own value, read on the
inactive photo cells (the recede's worst cell is untinted and inactive; today it has no chroma law
at all). Two values across the light and dark documents; the accessibility documents inherit the
light value. G0 may name a different single mechanism if the tables demand it (a lower plate alpha
with a darker neutral; a multiplicative darkening of the backdrop); it may not name two.

**The CSS projection (G0 states, G3 executes or declines).** `saturate()` in the one
`backdrop-filter` acts on the backdrop before the `rgba()` plate covers it, so the interior chroma
it can reach is bounded by `(1 − α)·s`; the existing constants 1.8 / 1.4 are CSS-only and do not
move (X3). G0 states the ceiling per scheme as a declared residual. G3 either derives one further
term from the leaf with `tier-coherence` extended to cover it, or records that the CSS tier carries
nothing of this operator, with the residual measured. `tier-coherence.test.ts` mirrors an
enumerated list; G3 adds a case that the list is exhaustive over `MaterialProfile`'s keys, so that
"tier-coherence green" says something about a new leaf.

**The digest rule as executed (Decision Log 1 (a), ruled; the execution shape is the parent's).**
The fingerprint drops a leaf whose resolved value equals its declared inert identity, and drops a
**gate-group** — a gate leaf at its identity together with the leaves it makes unread — as one
unit; a gated leaf's own value is never dropped on its own. The identity table is a committed,
tested, **append-only** constant beside `DEFAULT_MATERIAL_PROFILE`: leaf path → identity value (or
gate → gated leaves), the inert-law unit case that proves it (`w30-inert-laws.test.ts` per leaf;
this wave's leaf gets its own), and the wave that added it. A leaf a document sets EXPLICITLY to
its identity reads as absent (the digest is over what draws, and an explicit identity draws
nothing) — G0 states this and its consequence for the light 27 document's declined scatter. The
rule has a version, recorded in every document re-sealed under it (a `resolvedMaterialSha256Rule`
field, or the history idiom), so a recorded digest names the function that produced it; the two
26.5 documents are not edited — their recorded digests equal both definitions' output, which is the
proof G0 commits. Consequences: the 26.5 documents' recorded digests are the live fingerprint again;
`digest-supersessions.json` becomes history with its records kept and the pins reading the
documents' own fields; `material-document.ts` and `window-activation.spec.ts` return to the
recorded digests; the four 27 documents' digests move once, re-sealed with history, in G3's merge.
What the rule does not catch, named for the record: a mis-declared identity (mitigated by the
unit case the table requires); a default that moves TO a value some document explicitly carried
(the document's digest then drops the leaf — G0 says whether that is a hole).

**The holdout rule as enforced (Decision Log 1 (b), ruled).** The configuration is recorded in the
read's evidence as the four 27 document file hashes plus a SHA-256 over the enumerated source list
in clause 6, by a script G3 commits; a second holdout read at identical document hashes is refused
by that script unless the source hash moved and a non-fit reason is named on the command line and
recorded. A fit that moves a value from a document into a shader default is a document change AND
a source change and is caught as the former.

**The exterior clause (G1, advisory).** Two candidates from fields every row carries: (i) the
fitted σ's error, `|falloffSigmaWeb − falloffSigmaNative| / falloffSigmaNative` per cell on
converged fits, by span class — tabled BESIDE B1's per-bed windows on the same cells, because B1
bounds the same quantity from the document's side and is green where (i) is not; what a
divergence means (the document's law right and the rendered σ wrong, or the instrument reading
something the law does not model) is stated before the clause is declared; (ii) the departure
profile's shape — the affine rings' `interceptC` and `slopeA` against native per ring, not
dominated by the interior. G1 says which one the seven missed rows move under and which the eye
agrees with (§5.160 §6), and declares the clause the next shadow wave adopts.

## Children

### G0: The chromatic cut, the instrument and the declarations — no material change

*Opens on main, parallel with G1 and G2. Read-only on the material; writes an instrument, evidence,
tables, tests and declarations. Does not touch `cli/gates.ts` or `test/compare-gates.test.ts` (G2's).*

- (a) The per-pixel chroma instrument in `packages/calibration/src/metrics/` with the unit cases
  Design names; the three ratios; exported on the row beside the mean-based fields as optional
  schema-5 additions (no bump; `report.ts`'s `drawnAreaWeb` precedent); `interiorChroma` /
  `backdropChroma` exported too.
- (b) The scratch re-capture of the chroma bed's web side at the shipped documents under X6
  (`--out-matrix`, `VITREA_WEB_CAPTURES`; nothing appended; disclosed), with a reproduction check
  per re-captured cell (at least `interiorMeanWeb` and `ssimMean` against the committed row, within
  the row's `repeatNoise` or the bar G0 states); then the cut: the statistic over every
  chroma-carrying cell — `photo`, `mid-chroma-solid`, the tinted cells; both schemes, tiers, scales;
  active and inactive — tabled per backdrop class per scheme per tier per span with the conditioning
  state of each cell, the 26.5 rows beside (from the canonical 26.5 trees), and the 26.5→27 native
  delta on the same statistic from the fixture pairs, with the mean-OKLab instrument's reading
  beside so the ledger says why the per-pixel one was needed. Whether the light scheme carries the
  residual; whether Apple moved it or vitrea never had it.
- (c) The four claimed rows decomposed: `oklabDeltaEP95` on the four dark `photo__rrect-lg__rest`
  rows split into its ΔL and Δ(a,b) contributions over the whole capture (interior, rim,
  exterior), and the headroom the chroma lever alone can reach stated per row.
- (d) The mechanism, from the shader, as clause 2 requires: where chroma is lost; the two collapses
  told apart; the leaf shape with its identity, its luma-preservation rule in linear luma, its
  gamut behaviour, its `toneAdapt` gate or the reason none, its place in the order; the receded
  documents' own value; the tint path under it; the CSS ceiling per scheme as a declared residual.
- (e) The digest-rule proof: the identity table with gate-groups for the eight W30 leaves and this
  wave's leaf; a script that fingerprints each 26.5 document under the rule and prints
  `b2b570e4adcea8fb` / `874be66ea501621b`; the four 27 documents' digests under the rule beside
  their current ones; a run with a default moved off its identity in memory showing the 26.5
  digests move; the holes named (Design). No test or document changes.
- (f) The declarations, committed last: the tolerances with statistic, conditioning and fate
  (one-wave unless the identifiability argument is made); the level stop as a number per cell;
  the four rows each CLAIMED or "reachable if" on (c)'s headroom, with the pre-holdout judgement
  named; the recede's worst cell reported; the expected-unmoved rows (shadow, scatter, tint); B3's
  departure stop 0.00035 on the WebGPU tier; the 27 tables cited, never transcribed; no floor.
- (g) Sheets: native | WebGPU | CSS | ×8 difference for `photo__rrect-md__rest`,
  `photo__rrect-lg__rest` and `mid-chroma-solid__capsule-button__rest` in both schemes at 1x, from
  the scratch captures (disclosed), with `eye.md` written before any fit exists — hue, not level.
- Ledger: **§5.161**. Evidence: `results/2026-09-21-w31-g0-chroma-cut/`.

### G1: The exterior-width instrument — parallel with G0

- The two candidate statistics computed over the current generation for every row with a shadow
  axis, from committed fields only; per cell, span class, scheme, tier, scale; candidate (i) beside
  B1's per-bed windows on the same cells with what a divergence means; the seven missed rows'
  readings under each; the non-converged fits excluded by W30 G0's rule and counted; the G3
  generation against its superseded predecessor on both statistics (which one the lever moved). A
  reader script under the evidence dir, a unit case on a scratch matrix, and the clause declared —
  statistic, bound, bed, row shape — as the **candidate adopted row for the wave that next moves
  the shadow**, recorded as a one-wave reading here. Nothing adopted, nothing fitted, no capture.
- Ledger: **§5.162**. Evidence: `results/2026-09-21-w31-g1-exterior-instrument/`.

### G2: The WGSL range class and the refusal's wording — parallel with G0 and G1

*Sole owner of `packages/calibration/cli/gates.ts` and `test/compare-gates.test.ts` in this wave.*

- (a) A unit case over `packages/renderer-webgpu/src/wgsl/*.ts` that finds every `exp`, `exp2`,
  `pow`, `tanh`, `sinh`, `cosh`, `log`, `log2` call (sixteen sites today: optics 11, highlight 2,
  prelude 2, backdrop 1) and requires each argument to be **clamped to a range on which the result
  is finite in f32** — a clamp to the function's saturation point, as G3b's ±20 was, not merely a
  clamp — with a `pow` base required non-negative, or to appear in a committed range-proof table
  (call site → bound → the leaf and scene quantities it depends on → why the bound holds over the
  bed and over any value a fit could produce). Every site classified; a site that can be neither
  proven nor clamped as an identity STOPS the child on that site.
- (b) `@gpu` sweeps in the shape of `w30-thin-sigma-coverage.spec.ts`, each over BOTH halves of its
  ratio — the material's axis over the range a fit could reach and the scene's axis at the shipped
  values — for the lens depth, the scatter widths, the tone response's knots and the rim's exponent,
  asserting an invariant that does not depend on the swept value: silhouette coverage (IoU ≥ 0.99)
  and no NaN in the readback.
- (c) The readback guard: refuse a raster with an **enclosed** region of zero alpha inside a
  declared silhouette, stood down on the layer path (translucent interior by design) and at
  presence 0 (`dom_material_alpha` is legitimately 0); a case that a seeded NaN trips it and a case
  that a legitimately translucent interior does not; proof it never fires on the 34 goldens or the
  coverage cases; and a sentence on what (c) adds over (b) — (b) is the shape that caught the W30
  strip; (c) is the cheap standing guard for a scene no sweep named.
- (d) `matrixSchemaRefusal`'s message rewritten to what trips it today, its pinned cases updated;
  the consumer-table rule ("unchanged, checked" says what the file CLAIMS) recorded where such
  tables are written; the W30 G3b `glass-over-glass` residual (four dark cells, ≤ 8·10⁻⁴ px)
  re-read under (a)'s range proof for the outer-shadow falloff and closed or left open with the
  reason.
- Goldens 34/34 byte-identical; `test:gpu` green; no material change; both tracker entries
  amended beside.
- Ledger: **§5.163**. Evidence: `results/2026-09-21-w31-g2-range-class/`.

### G3: The leaf, the rule, the fit, the seal and the read — one merge; opens after G0, G1 and G2 are merged and reviewed

- (a) The leaf at its inert identity and the digest rule in one commit: `MaterialProfile`,
  `MaterialProfilePatch`, `withMaterialOverrides`, the allowlists, the CSS mirror (or its declined
  record), the uniform and the shader with the composite bit-identical at the identity; the
  identity table with gate-groups; `fingerprint()` under the rule in `seal.ts` and both test
  copies, the rule's version recorded; the pins returning to the recorded 26.5 digests
  (`digest-supersessions.json` kept as history, its reader retired or made historical);
  `material-document.ts`, `window-activation.spec.ts` and `macos27-profile.ts` moved to what the
  rule computes; the identity test's leaf list extended; the CSS declaration-identity case; the
  inert-law unit case for the new leaf; a `test:gpu` case that the on state draws differently from
  off; `tier-coherence`'s mirror list extended with the exhaustiveness case. Proofs as W30 G2's,
  each output committed: freeze 1,818; goldens 34/34; the 1,107 pin; the 26.5 digests reproduced.
- (b) The fit per scheme on calibration + the granted probe anchor through the reader with the
  holdout dropped, checked on validation; the level stop and the departure stop held on scratch;
  the receded documents' own value read on the inactive cells; the tinted cells read before and
  after; the four 27 documents re-sealed with history under the rule; `PREDICATE_EXCLUDES` and
  every count test moved to what the machine says **only in the commit that carries the read**; a
  changeset (a `@vitreajs/vitrea-web` minor at least); sheets at the fit by eye.
- (c) The read, in the same gate: RT and IC read 0, `NSGlassTintAmount` 0.5, one capture process,
  idle ≥ 60 s; the configuration script (document hashes + source hash) run and its output in the
  ledger before the read; the canonical run over six profiles × two tiers, calibration + validation
  + the ladder appended beside the 0.20.0 rows; holdout **once**; the append-check; the split; the
  append-check again; freeze 1,818; the 27 gated-cell count back at 230 (or at what the machine
  says, with the difference explained cell by cell); the capture tree kept for the parent to copy
  to the canonical `web-captures/` at merge.
- (d) The verdict per profile per tier per clause; the claimed, expected-unmoved and reported rows
  each named with before and after; misses recorded; Decision Log entries drafted where a ruling
  is needed; the adoption question put to the parent with G0's identifiability argument.
- Ledger: **§5.164**. Evidence: `results/2026-09-21-w31-g3-chroma-fit/`.

### G4: The landing — 0.21.0 prepared

- Adoptions carried in on the parent's decision; sheets native | WebGPU | CSS | difference for the
  photo cells and `mid-chroma-solid` in both schemes at both scales, looked at; the demo's figures;
  the coverage matrix; `CLAUDE.md`, READMEs, CHANGELOG; the tone stage's two records closed on
  Decision Log 1 (c); the fixed group versioned 0.21.0, dry runs green, unpublished; the chain.
- Ledger: **§5.165**. Evidence: `results/2026-09-21-w31-g4-landing/`.

## Cross-Child Contracts

- **X1 — the freeze, intact.** No macOS 26.5-keyed path, row, bound, floor or document changes;
  `freeze.py verify` reports 1,818 intact at every merge; the 34 goldens byte-identical through G1,
  G2 and G3's leaf commit; the 1,107 gated-row pin holds. No exemption is spent: the digest rule
  makes the leaf's addition digest-neutral, and the 26.5 documents' recorded digests are reproduced
  by proof before the rule lands.
- **X2 — the cut precedes the operator.** G0 names the leaf shape and its identity from the
  instrument's tables before G3 writes a leaf; G3 adds no leaf G0 did not name.
- **X3 — the operator changes nothing outside the body's chroma path.** The σ law, the scatter, the
  tone solve's luma, the anchors, the tint's chroma law, the recede's seed collapse and the CSS
  tier's existing `saturate()` constants do not move; a fit that moves a shadow, structure or tint
  row is a warning, not a result.
- **X4 — bounds before reads; the level stop is a number; holdout once under Decision Log 1 (b)
  as enforced by artifact; a miss is recorded.**
- **X5 — no native capture; the granted bundle is never rebuilt and nothing is added under its
  identifier.** Every fixture is on disk from W29.
- **X6 — RT and IC 0, the slider 0.5, one capture process, ≥ 60 s idle** before every browser run,
  scratch captures included; every run recorded.
- **X7 — the evidence layout changes by the one rule**: the split after the read that supersedes;
  every superseded row one `git show` away; the freeze's row hashes verify at every merge; no
  schema bump, additions optional at schema 5.
- **X8 — padding untouched.** The chroma term reaches no pad; the advisory constant's retirement
  stays undecided.
- **X9 — no GPT-rung agents**; children and reviews are opus `general-purpose` (read-only for
  reviews); ledger sections assigned above; merges `--no-ff -F <file>` with the freeze verified at
  each; no attribution trailers, no session URLs; committed evidence never rewritten.
- **X10 — the 27 bed never empties between merges.** A macOS 27 document's bytes change only in a
  merge that also carries rows read at the new bytes (W30 Decision Log 4 (b)); the parent pins the
  27 gated-cell count (230 cells / 726 rows, or what the machine says after G3 with the difference
  explained) at every merge, and `MATRIX_CELLS` / `PREDICATE_EXCLUDES` move only in the commit that
  carries the read.
- **X11 — file ownership among the parallel children.** G2 owns `cli/gates.ts` and
  `test/compare-gates.test.ts`; G0 owns `src/metrics/`, `cli/measure.ts` and `src/report.ts`'s
  material axis; G1 owns nothing G0 touches except `report.ts`'s shadow axis if it adds a field
  (say so). Every child appends its ledger section at the tail and its Tracking Map row; the parent
  merges **G1 → G2 → G0** and resolves the tail by keeping every section in numeric order.

## Ordering & Dependency Map

Charter → adversarial review → fold (done) → **G0 ∥ G1 ∥ G2** → merged in the order G1, G2, G0,
each reviewed → **G3** (leaf + rule + fit + seal + read, one merge, reviewed) → the parent's
adoption decision → **G4** → the user's eye on the sheets → `pnpm release` (the user) → tag. After
this wave, in the order W30's Deferred kept: the analysis pass (W30 Deferred 2, the user's to
charter); the shadow's next wave carrying G1's clause; the identifying sitting on the 27 bed; the
highlight's angular reader; the decoupled-contrast flag and its read; the motion-metrics harness.

## Risks & Mitigations

- **The chroma term moves the level.** The retention is luma-preserving in linear luma by
  construction and the level stop is a declared number per cell, read before and after on scratch.
- **The instrument rewards absorbing the structure deficit.** The bound is on the
  chroma-to-structure ratio, in which blur cancels; the raw ratio is tabled beside so a fit that
  moves only the raw one is visible; the structure rows are expected unmoved (X3).
- **The bed is thin: one well-conditioned untinted dark photo cell per profile.** The probe anchor
  is granted; G0 reports conditioning and argues the mask; the tolerance's fate is a one-wave
  reading unless identifiability is argued; the tinted cells are read as a check, not fitted on.
- **The tinted cells' chroma law absorbs it.** Their rows are declared expected unmoved; the
  retention is applied before the tint composition.
- **The CSS projection is wrong in one scheme, or worthless.** The ceiling is declared before the
  fit; the tier may carry nothing, recorded; `tier-coherence` is made exhaustive so green means
  something.
- **The light scheme has no residual and the leaf is fitted to zero there.** A declined value is a
  measurement, recorded as W30 recorded the light scatter; an explicit identity reads as absent in
  the digest.
- **The digest rule hides a leaf whose identity is mis-declared, or a gated leaf on its own.** The
  identity table requires the inert-law unit case per entry and drops gate-groups only as a unit;
  the table is append-only.
- **The re-seal empties the 27 bed.** X10: seal and read in one merge, the count pinned.
- **The re-capture reads a different renderer day.** The reproduction check per re-captured cell
  against the committed row, within the repeat noise, before any new statistic is read.
- **A read appends to a 66 MB file.** X7, once.

## Deferred / Out of Scope

The analysis pass's scale statistic (W30 Deferred 2); the shadow's next fit under G1's clause C1, and beside it **a joint fit of the shadow's three lengths — `sigmaPx`, `spreadPx` and `offsetPx` — against the exterior it draws rather than the blur alone**, which G1's candidate (i) names with a number (§5.162 §2, §5) (the
seven rows are not claimed through the shadow here; the four dark ones are claimed or "reachable
if" through the chroma on G0's decomposition);

**Added at G3's close (claims §5.164 §8), each measured rather than anticipated:**
**a retention conditioned on the SURFACE** rather than one constant per document
— a single value closes the median and widens the per-cell spread (light active
**1.2824 → 1.6216** between the extremes, corrected 2026-09-21 by G3c's review
closure from 1.28 → 1.44, which dropped the bed's own lowest two cells; claims
§5.164 §13, finding F4) and overshoots the largest span, R 1.24 / 1.36
on the holdout cell, because `1 − sizedAlpha` falls as the span rises; **the two
accessibility documents' own retentions**, which inherit the light value under
Decision Log 2 (a) and read 3.04 / 2.95 active and 1.99 / 0.14 inactive against a
reference of 1 — on beds that DO carry bounds, sixteen gated cells and eighteen,
none of which the chroma statistic is one of, and behind W31 G3c's stand-down,
which returns all four to 0.20.0's readings and makes the deferral a question
about a value rather than about a regression (Decision Log 3 (c) and (d); claims
§5.164 §13, finding F2); **a chroma operator the CSS tier can
actually carry**, on the `rgba()` layer rather than on the backdrop beneath it,
since a gain on `saturate()` is inert where the converted alpha covers the
backdrop and clips the level where it does not; and **`mid-chroma-solid`'s hue
ROTATION** (§5.161 §8), which is a probe scene and was not re-read at the
canonical read, so G0's finding stands open; the highlight's angular reader; the decoupled
increased-contrast read and `compare`'s flag; the identifying sitting; the motion-metrics harness;
the CSS tier over pure black; inactive calibration cells above span 96; `samplingPaddingFor`'s
advisory constant; the Reduced Transparency opacity policy and the impulse specular point; the
slider's ends as evidence classes; a shadow section for `/laws/` (W30 Deferred 10); the thin
regime's instrument (W30 Deferred 4); the light bed's 16 px structure (W30 Deferred 3); the CSS
tier's `saturate()` constants as fitted rather than authored values.

### At close, 2026-09-21 — what this wave measured and did not do

Each is a named piece of work whose evidence is already on disk, in the order the parent would
charter it. None is a loose end: the wave established the existence and the size of every one.

1. **A retention conditioned on the SURFACE rather than one constant per document.** One constant
   closes the median and scales the spread: the light active bed's per-cell range goes from
   0.5095–0.6533 to 0.8891–1.4417, a factor of **1.2824 → 1.6216** like for like, with the same
   components the outliers on both sides. The holdout cell overshoots at `R` **1.2391** / **1.3596**
   and three span-32 cells overshoot the other way at 1.5155 / 1.4469 / 1.4417, now recorded MISSED
   under M1. The cause is one thing: `1 − sizedAlpha` falls as the span rises, so a constant fraction
   of the FULL backdrop chromaticity is a larger relative gain the less the plate transmits
   (correlation −0.39 between transmitted chroma and gain over 56 cells). *The work*: make the
   retention a function of the plate's own alpha, as W30 made σ a function of the casting span — and
   **widen the dark bed's spans first**, a `scenes.json` decision, because the dark half is four
   cells at one span each. Evidence: §5.164 §8 (a), §13; `round-B.txt`; tracker.
2. **The two accessibility documents' own retentions.** They inherit the light value under Decision
   Log 2 (a) and stand it down entirely under Decision Log 3 (d), so 0.21.0 draws exactly what 0.20.0
   drew there — proven at the raster (48 of 48 PNGs) and at 6,855 numeric readings — and the value
   they SHOULD carry is now an open question on a material that carries none. Two readings say the
   answer is not obviously zero: the increased-contrast inactive bed has read `R` **0.1552** against
   a reference of 1 with and without this wave, and under the declined lift rule the perceptual rows
   were better on three of four beds. *The work*: fit on their own beds (16 and 18 gated cells), or
   evaluate item 1's law at the lifted alpha, which is the likelier answer. Evidence: §5.164 §8 (b),
   §13; tracker.
3. **A chroma operator the CSS tier can actually carry.** The derived term was written, rendered and
   declined: 0.000 of the gap on the dark scheme at **every** retention up to 1, because that tier's
   converted alpha leaves no backdrop for `saturate()` to act on, and both stops broken on the light
   one because `saturate()` stops preserving luminance the moment an sRGB channel clips. The cost is
   two `dom` rows in `MISSED_27_ROWS`, unmoved to the fifth decimal while their `texture` siblings
   cleared. *The work*: a chroma term on the `rgba()` layer rather than on the backdrop beneath it,
   or a plate this tier does not solve to full coverage. Evidence: §5.164 §5, §8 (c); tracker.
4. **The next shadow wave, carrying C1 and the `spreadPx` joint fit.** C1 is declared on the
   departure profile's shape at ≤ 0.0045 per standard bed per thick span — a bound today's material
   misses at spans 128 and 160 on all four beds and meets at 96 — as a one-wave reading, and the
   adopting wave must **re-run `exterior-instrument.py` into its own evidence directory** rather than
   read this gate's cut, and must consider a per-span bound or a σ-normalised window because `T` is
   span-confounded. Beside it: B1's two sides are not the same quantity, and the gap is additive and
   nearly constant at **+2.66 to +3.77 CSS px** — the size of the shipped `spreadPx`, which the macOS
   27 material inherited and no wave has fitted, and which neither dark document carries at all. *The
   work*: a joint fit of the shadow's three lengths — `sigmaPx`, `spreadPx`, `offsetPx` — against the
   exterior it draws rather than the blur alone. Evidence: §5.162 §2, §5, §9.
5. **The analysis pass.** W30's B4 missed on three of four standard beds because the per-source
   statistic is read off a fixed 64 × 64 grid and is therefore the same number at both scales, so it
   cannot act in opposite directions on two scales that need them. W31 declined to touch the
   structure (X3) and the structure deficit is what the dark sheets' remaining ΔE is: vitrea's body
   is smoother than the reference's. *The work*: a second operator, and the user's to charter.
   Evidence: W30 §5.159 §4.
6. **The sweep phase reaches the uniform unwrapped.** G2 floored `highlight.ts`'s `angle_delta` as an
   identity, which closes the NaN; the phase itself still arrives from a CSS custom property nothing
   wraps, so the argument grows without bound over a long-lived page. *The work*: wrap at the source.
   Evidence: §5.163; tracker.
7. **`prelude.ts`'s `pow` base has a floor and no ceiling.** The base is floored in the shader and the
   site stays PROVEN, because at an exponent above 1 it is the base's CEILING that decides finiteness
   and a floor cannot reach it. The proof carries a written range argument with a witness rather than
   a clamp. *The work*: a source-side ceiling, or the proof recorded as permanent. Evidence: §5.163
   §1, §8.
8. **The receded TINTED cells' body has no chroma at all.** Ratio (ii) reads **0.001–0.006** against
   the reference's 0.54–0.65 while the ACTIVE tinted cells match almost exactly (1.433 against
   1.435). That is W27c's seed collapse driving the paint to neutral where Apple's receded material
   keeps it — a tint-path defect this wave neither caused nor could close (X3), and one its own
   instrument can now judge. *The work*: re-read the seed collapse against the macOS 27 receded
   fixtures, which are a different bed from the one it was fitted on. Evidence: §5.161 §3 (b);
   tracker.
9. **`mid-chroma-solid`'s hue ROTATION — and its LEVEL break beside it.** G0 recorded the
   reference's body as a clean lighter pink
   and vitrea's as a lavender — desaturated AND rotated toward blue — with `tintHueShift*` never read
   on those cells. It is a probe scene, so neither canonical read carried it and neither G3 nor G4
   could capture one (X1). On the `photo` cells the restored hues sit where the reference's do, which
   is consistent with a rotation that was the plate's; nobody claims it. *The work*: a `--set probe`
   run at the shipped documents and a sheet beside G0's. Evidence: §5.161 §8, §5.164 §9, §5.165 §2;
   tracker.
   > **Two corrections beside this item, 2026-09-21 (review closure; claims §5.165 §9, findings R2
   > and R4).** **(i) The reason is not X1.** X1 is the freeze; X5 bars NATIVE capture only; X6
   > contemplates scratch captures by name; G0 made this scene's sheets from a scratch web
   > re-capture inside this wave. So the route was open at G3 and at G4 and both declined it — a
   > scoping choice, not a contract. **(ii) The scene is also LEVEL-broken, which is the harder half
   > and is tracked nowhere else.** Its 1x dark inactive cell reads `interiorMeanWeb` **0.0761
   > against a native 0.2856** over a backdrop of 0.2141 — the reference's receded body is BRIGHTER
   > than what is behind it and vitrea's is a quarter of it — and its 1x light rest cell reads
   > **0.6134 against 0.3957**. Since the chroma ratio scales as `(level)^(−2/3)` exactly, those bias
   > it by 2.415× and 0.75× (§5.161 §3 (b) as its own closure corrects the dark figure, N6), and the
   > charter's own Surprises rule that the anchor **"must not carry the tolerance until its level
   > agrees"**. A `--set probe` run answers the rotation; it does NOT answer the level, and a wave
   > that reads the probe set should expect to find the level miss still there.
10. **The retention under Increase Contrast ALONE.** The stand-down is on the OCCLUSION axis and only
    Reduce Transparency raises one, so a 0.21.0 page under Increase Contrast by itself draws the
    retention at full value. Not a regression against 0.20.0, which had no operator — and not
    measured either, because macOS 27 decoupled the two switches and this wave's increased-contrast
    bed is the COUPLED profile whose occlusion IS lifted. Under it is a design question: Increase
    Contrast's own consequence is `ambientTint: "reduced"`, documented as the material's colour cast
    picked up from its backdrop, which is literally this leaf. *The work*: read the decoupled bed
    (which needs `compare`'s flag fixed first), then decide whether the retention should read
    `ambientTint` as well as `occlusion`. Evidence: §5.165 §5; tracker.
11. **The level stop, declared as a number and gated by nothing.** `R` scales as `(level)^(−2/3)`
    exactly, so a level miss biases both adopted rows; M1's band was widened to absorb it and M2
    bounds the structure instead. The bed's worst is 0.04933 against the declared 0.055, on the same
    cell whose reproducibility pair is the dark bed's worst at 19.41 % — **the PRE-fit figure;
    post-fit the same pair reads 25.10 % over the pair's mean and 28.70 % over `R₁ₓ` (§5.164 §12 as
    its closure corrects it; corrected beside 2026-09-21, §5.165 §9, finding N6)** — and the eye
    sees the chroma miss and the level miss there as one defect. *The work*: adopt the level clause
    as a third material-axis row — the cut already carries `interiorMean{Native,Web}` per cell, so
    it is a clause and not a capture — choosing a bound that declares its outliers rather than one
    that passes.
    Evidence: §5.161 §7 (c), §5.165 §2 (c); tracker.
12. **Nothing checks the canonical capture tree against the matrix.** The tree held no macOS 27
    generation at all until this wave's clause 6, and the macOS 26.5 tree that did survive is a
    DIFFERENT generation from the rows beside it — two cells of `photo__glass-over-glass__rest`
    disagree by 2.8e-03 and 2.5e-03 on `interiorMeanWeb`. The copy is now a step in a charter and not
    a rule anything enforces. *The work*: a checker that walks the tree's `cell__*.json`, reads each
    capture's document hashes and asserts the generation matches the matrix's rows for that profile —
    a file walk and a string compare, skipping cleanly where the tree is absent. Evidence: charter
    Surprises, §5.161 §2; tracker.
13. **0.21.0's headline operator has no stage on the demo that shows it.** The site's dark stage is
    achromatic by construction (`DARK_GROUND.field` is 0, because the lobes multiply and multiplying
    a light lobe onto near-black is nothing), and the dark scheme is the endpoint the wave moved most
    — ratio (i) 0.3332 → 0.9994. On the light stage the plates sit over the palest corner of the
    bloom. *The work*: a chromatic ground the dark scheme can carry at a chroma the contrast case
    still passes, or surfaces over the bloom's centre, or a stage of the operator's own. A design
    decision before an implementation. Evidence: §5.165 §4; `eye.md` §8; tracker.
14. **The evidence-hygiene items three gates named and none could fix in place**: the two dark macOS
    27 documents' wrong `$comment-sha-history` parenthetical, which cannot be corrected without a
    canonical read of two profiles (X10); `split-generation.py` documenting a rule it does not
    enforce, with two committed entries carrying the slip; the holdout configuration log living
    inside one gate's evidence directory where a copying convention can fork it;
    `interiorStdDevWeb` moving 5.69 % on a standard light cell off M2's declared bed; and
    `standard-row-identity-matrix.txt` having no generator committed beside it. Each is a tracker
    entry with its fix shape. Evidence: §5.164 §13, §5.165 §6.
15. **Carried unchanged from W30's list, untouched by this wave**: the identifying sitting on the 27
    bed; the highlight's angular reader; the decoupled increased-contrast read and `compare`'s flag
    (item 10 now needs it); the motion-metrics harness; the CSS tier over pure black; inactive
    calibration cells above span 96; `samplingPaddingFor`'s advisory constant; the Reduced
    Transparency opacity policy and the impulse specular point; the slider's ends as evidence
    classes; a shadow section for `/laws/`; the thin regime's instrument (B2); the light bed's 16 px
    structure; and the CSS tier's `saturate()` constants as fitted rather than authored values.
16. **The unsampled-DOM path restores toward the DECLARED tone** (added 2026-09-21 by the G4 review
    closure; claims §5.165 §9, finding R3 — the finding existed at §5.164 §13 N7 and was on no list).
    On the unsampled-material path nothing samples a backdrop, so `dom_material_backdrop()` supplies
    one. **Mode 1**, a group with no declared `backdropTone`, fabricates a neutral and the operator
    is the identity in effect — zero bytes move at any retention up to 1. **Mode 2** returns the tone
    the page DECLARED, and there the operator is live and restores toward a colour the page asserted
    rather than toward what is behind the surface: interior chroma **0.066 → 0.334**, with the
    **gamut clamp already binding at the shipped retention**, so the fitted fraction is not what that
    path draws. *The work*: rule on the policy — stand the retention down on the unsampled path, or
    keep it and state that a declared tone is a colour claim and not only a level claim — and record
    the clamp's reading either way. Evidence: §5.164 §13 N7;
    `packages/renderer-webgpu/e2e/gpu/w31-unsampled-dom-chroma.spec.ts`; tracker.

## Tracking Map

| Child | Status | Claims section | Evidence |
| --- | --- | --- | --- |
| G0 | **CLOSED 2026-09-21.** The per-pixel instrument landed as 23 optional schema-5 fields with the unit cases, and one of them records that **the charter's own Design paragraph is wrong**: a luma-only darkening scales ratio (i) by exactly `c^(−2/3)`, not by 1, because OKLab's `L`, `a` and `b` all scale by `c^(1/3)` while the declared denominator is LINEAR luma. `interiorOklabLSdDev*` is exported beside it as the exactly-invariant twin. The chroma bed re-captured as scratch at the shipped documents (616 cells, nothing appended, RT/IC/slider recorded) and **all 552 macOS 27 cells reproduce their committed rows to \|Δ\| exactly 0**; two macOS 26.5 cells do not, and the diagnosis is that the canonical `web-captures/` tree is already a different generation from the rows beside it (Surprises). **The residual**, ratio (i) web/native on the WebGPU tier: **0.333 dark active, 0.551 light active** — the light scheme carries it. Ratio (ii) web 0.106–0.119 on the dark cells against `1 − sizedAlpha` = 0.0950, so the chroma is lost in the plate's alpha and nowhere else. **Apple moved it**: ratio (ii) rises +0.22…+0.38 on every untinted photo and `mid-chroma-solid` cell of both schemes between macOS 26.5 and 27 while the tinted cells move −0.03…+0.00, and the mean-OKLab instrument reads the same change as a fifteenth of that. Ratio (iii) says the DARK reference is not a blur (1.20–1.80× what a matching Gaussian leaves) and the LIGHT one nearly is (0.75–1.00). **All four claimed rows CLAIMED** — 90–93 % of ΔE² at the P95 pixels is chromatic and the chroma lever's reachable floor is 0.062–0.066 against bounds of 0.17–0.19. **The mechanism**: `bodyChromaRetention ∈ [0,1]`, identity 0, after the composite, luma-preserving in linear RGB BY CONSTRUCTION (both mix endpoints carry the same luma, so the renormalisation is an f32 guard), gamut by scaling chroma toward the neutral at fixed luma, **no `toneAdapt` gate because `toneAdapt` is identically 0 on the macOS 27 material** at every backdrop and span. **The digest rule proved**: `b2b570e4adcea8fb` / `874be66ea501621b` reproduce, the four macOS 27 digests printed under the rule, a moved default shown to move them — and the gate-group refined, because `sigmaThinOffsetPx` is NOT gated by the slope. Tolerance, level stop, structure stop and the identifiability argument declared; the CSS ceiling 0.784 light / 0.278 dark as a declared residual | §5.161 | `results/2026-09-21-w31-g0-chroma-cut/` |
| G0 review closure | **CLOSED 2026-09-21**, beside the row above and moving nothing in a number. An independent read reproduced every figure of §§1–10 and found sixteen things in the reasoning and the record — four blocking. **B1**: `css-ceiling.ts` evaluated an alpha the runtime does not draw (the anchor forced where `root.ts` gates it on `linearChainReaches`, the source unsized where the runtime sizes through `sizeOcclusionAlphaAt`); corrected, the CSS ceiling is **0.5995 / 0.5654 light** and **0.2767 / 0.2651 dark** by span against the recorded 0.784 / 0.278 — and since today's light CSS tier already reads ratio (ii) to 0.633 the light figure was never a bound. **The recommendation to G3 is reversed**: the room for a derived term is on the DARK scheme, not the light one. **B2**: §4's floor is measured in OKLab `L` while the leaf preserves LINEAR luma; measured, the restoration moves `L` by ≤ **0.040** and the four floors recomputed under it are 0.0677–0.0730 against bounds of 0.17–0.19, so all four rows stay CLAIMED. **B3**: the digest rule had no record in the ledger — now §5.161 **§7b**, with the rule, its version, the table, both frozen digests and the four macOS 27 ones. **B4**: two of the three gate-groups' cited cases did not prove the statement the table makes; closed by **code** (`w31-gate-groups.test.ts`, twelve cases, the shipped `sizeScatterScaleRef` = 0.03 among them), and the Revision Note's "wrong in two places" **reads one** — under the grouping it attributes to the charter, a material with `sigmaThinOffsetPx` 5 fingerprints to the frozen `b2b570e4adcea8fb`. Twelve non-blocking, all beside: `toneAdapt` is not identically 0 (it is zero because every backdrop is ≫ 1e-4); ratio (iii)'s level confound reverses the LIGHT reading — Apple's light body REMOVES 23–48 % of a matched blur's chroma; the invariant twin is not blind and G3 reads it beside `R`; §3's ratio (ii) columns are all-sets where its medians are the declared bed; the level stop's baseline is **0.0060 / 0.0210** on both tiers with the worst cell 2x dark `texture`; the anchor's dark bias is **2.41×**; **24** optional fields, not 23. Carried forward for G3: the level-corrected plate predictor `(1 − sizedAlpha)·(Y_web/Y_backdrop)^(−2/3)` holds at **0.897–0.996 on all 34** single-body photo cells, and `dom_material_alpha` clamps per channel inside a luma computation, so the `dom` tier is not luma-transparent | §5.161 §11, §7b | `results/2026-09-21-w31-g0-chroma-cut/` (seven evidence files added beside, none replaced) |
| G1 | **MERGED** — the clause C1 declared on the departure profile's SHAPE; candidate (i) recorded as the diagnostic that points at `spreadPx`/`offsetPx`; nothing adopted, nothing fitted, no capture. **Amended beside 2026-09-21 (review closure; claims §5.162 §9), no number in this row or in §5.162 rewritten:** an independent read reproduced every figure of both statistics and found no measurement wrong; its fourteen findings, two blocking, were **all in the record**, and **no statistic, bound, count, exclusion or verdict moved**. The two blocking: the drafted C1 row read a **frozen snapshot** of the matrix, so a dated condition now requires the adopting gate to re-run `exterior-instrument.py` into its own evidence directory and point `CUT` there, and the draft gains the two provenance assertions it lacked (`atDocuments` shipped, `withHoldout` false); and the backdrop-support rule's reach is **32 `impulse` rows, fourteen carrying a non-zero `T` up to 0.004287**, not eighty rows of zeros — the 48 `dark-solid` rows identify no affine band at all — with the rule **kept** because it is the axis's own constant and admitting all 32 moves no WebGPU-tier order statistic (it moves twelve counts and two unprinted CSS-tier span-44 medians). One reason **withdrawn**: "its own lever reverses" applies to candidate (ii) too, and the choice stands on the other two and on the per-band structure. Corrections beside: the span-96 per-cell maxima are 0.00508–0.00561 and all above 0.0045; the CSS tier is NOT worse everywhere (1x dark span 160, 0.00789 against 0.00921); §6's improvement ranges are 20–54 % and 8.5–32 %; **all 726** macOS 27 rows carry a shadow axis and 602 is the non-holdout count; span 128 on the light beds is **two** gated cells; the +2.66…+3.77 gap is the **WebGPU tier's** (CSS runs −4.74…+5.36); the `spreadPx` reading assumes Apple's outset ≈ 0 and is softened, with the unfitted half verified across three documents; the bilateral σ rule is inert on today's bed; and `T` is declared **span-confounded**, with a per-span bound or a σ-normalised window named as what adoption must consider. New evidence `support-rule-check.py` / `.txt`; `test/adopted-thresholds.test.ts` untouched; freeze 1,818 at open and close | §5.162, §5.162 §9 | `results/2026-09-21-w31-g1-exterior-instrument/`, `support-rule-check.txt` |
| G2 | **MERGED** — 11 call sites: 8 clamped, 3 proven, 0 stopped; 5 sweeps + 3 guard cases green; goldens 34/34 byte-identical; one NEW reachable NaN found and floored as an identity (`angle_delta`); both tracker entries closed; the W30 G3b residual's candidate REFUTED and the residual re-opened. **Amended beside 2026-09-21 (review closure; claims §5.163 §8), no number in this row or in §5.163 rewritten:** an independent read reproduced every figure and found **no blocking finding** and nine non-blocking ones; no material constant, leaf, document, bound, floor, row or golden moves. Two are code. **The guard's wall was the raster's peak**, so a hole inside a dim surface escaped whenever a brighter one was in frame — the review's pair read 0 against 1, and `glass-over-glass` is a two-surface scene; the wall is now read **per declared region** with candidates bounded to the declared silhouettes, which is the charter's own (c) taken literally, and the presence-0 stand-down becomes exact rather than incidental. **The cross term was never rendered**: twenty-eight readings now pair each material ladder's endpoints with spans 32 and 340, every one 0 undrawn at containment 1.0000 (`sweeps-cross.txt`). Beside them: `iou` was **containment** and is renamed in the shared module and both specs, recorded values unchanged; the refusal's **newer**-schema branch enumerated older-schema artefacts and now has its own sentence and a case that reads more than two words; `prelude.ts`'s `pow` base is **floored as an identity** (goldens byte-identical) and the site stays PROVEN because the base's ceiling is what the scanner still objects to — the split is unchanged at 8/3/0; the division count was **99**, not "over a thousand", with **three** uniform divisors and none of them a material leaf (`division-count.py`); §7's totals were a pre-merge branch reading, **2,613** at this closure's head and **2,617** after it, `test:gpu` **43**; the guard is **test-time**, in the e2e harness; and the sweep-phase residual is now its own tracker entry instead of a paragraph inside a closed one. One defect the closure found itself: merging two declared masks with a spread `push` overflowed the stack on a 340 px caster and took `w30-heavy-second-tap` down — fixed and pinned by a case. Goldens 34/34, `e2e/goldens` clean, freeze **1,818** | §5.163, §5.163 §8 | `results/2026-09-21-w31-g2-range-class/`, `sweeps-cross.txt`, `division-count.py`, `call-sites-closure.txt` |
| G3 | **CLOSED 2026-09-21.** The leaf, the rule, the fit, the seal and the read in one branch (X10). **`bodyChromaRetention`** landed at inert identity 0 with luma held by construction — the composite bit-identical at 0, linear luma held to under two ULP of a double at every retention, and a `@gpu` case on a hardware adapter over a chromatic backdrop where ON moves 37 codes while the interior's mean luminance moves 2.5e-05. **The digest rule executed**: `MATERIAL_IDENTITY_TABLE` beside `DEFAULT_MATERIAL_PROFILE`, append-only and pinned to G0's declaration; the two frozen macOS 26.5 documents' own fields are the live pin again WITHOUT being edited; `digest-supersessions.json` became history with a test that reproduces both halves of every record; and the four macOS 27 documents re-sealed under rule 2 **reproduced the four digests G0 PREDICTED** (`62e68474…`, `c61194f8…`, `183c8949…`, `1a64247d…`) with the leaf added — the drop count moving 5/3/5/3 → 6/4/6/4 and nothing else. Two of the eight browser-read hashes came home to pre-W30 readings this file already carried. **The fit**: 0.282 light active, 0.349 light receded, 0.336 dark active, 0.142 dark receded, in two rounds, with R 0.5506→1.0486 / 0.5137→1.0205 / 0.3332→0.9994 / 0.5841→1.0170 — all four inside 0.80–1.20, every cell above the 0.60 floor, and no round C because the residuals are inside the instrument's own reproducibility. **Both stops held**: level worst |Δ| 0.04932 against 0.055 and worst GROWTH +0.00006 against 0.005; structure worst 1.317 % against 2 %, and that residual is the capture's 8-bit quantisation (it scales inversely with the cell's spread). **The CSS tier's term was derived, rendered and DECLINED on the measurement**: on the dark bed it bought 0.000 of the gap — and still 0.000 at a retention of **1** — because the tier's converted alpha leaves no backdrop for `saturate()` to act on, so §5.161 §6's dark ceiling is unreachable rather than an upper bound; on the light bed it bought 0.76–1.04 and broke the level-growth stop on 10 of 26 cells and the structure stop on 11, because `saturate()` stops preserving luminance when an sRGB channel clips. **The read**: 726 rows appended at the sealed bytes, holdout once after `configuration.py record` (which refuses a second read and was verified doing so), both append-checks green, the split moved 726 rows to two new superseded files, freeze **1,818** intact, the 27 bed back at **230 gated cells / 726 rows** with `PREDICATE_EXCLUDES` unmoved. **The verdict: the two `texture` claimed rows CLEARED** — 0.21531 → **0.14655** and 0.21341 → **0.14505** against ≤ 0.17, so `MISSED_27_ROWS` is five — and the two `dom` rows are unmoved to the fifth decimal, which is the CSS decline and is recorded as a miss. The recede's worst cell went R 0.537 → **0.9811** (1x) and 0.514 → **0.9431** (2x) with the level unmoved. Every expected-unmoved row held, the tinted rows exactly at s = 1, B3 at **0.00034**, and no native reading moved. Three residuals measured and named: a single retention SCALES the per-cell spread rather than closing it (the holdout cell overshoots at R 1.24 / 1.36 and the next form is a retention conditioned on the surface); the two accessibility documents inherit the light value and read 2.95–3.04 and 0.138; and the CSS tier carries none of the operator | §5.164 | `results/2026-09-21-w31-g3-chroma-fit/` |
| G3c | **CLOSED 2026-09-21.** The fix, its read and every record finding, on one branch (X10). **The regression is fixed by the HARD GATE and the choice is a measurement**: Decision Log 3 (d)'s ruled lift rule `r · (1 − lift)` was implemented, scratch-captured on both tiers and both poses, and left the accessibility beds at **R 1.7897 / 1.1507 / 1.8324** against the 0.9096 / 0.8294 / 0.8147 they held at 0.20.0 — `1 − α` is so small under a lift of 0.75–0.98 that even a scaled retention is a large relative gain on what the plate leaves, which is Decision Log 3 (b)'s structural reading one policy level down. Under the gate all four beds return to **0.20.0's readings exactly**, and the proof is at the byte: **48 of 48 PNG rasters identical** to G3's pre-fit tree. On the standard rows the fold is an identity — 34 goldens byte-identical with no regen, **8 of 8 PNGs identical** across two calibration captures differing only in the renderer, and every standard light row and every CSS row **+0.0000** at the canonical read. `bodyChromaRetentionUnderPolicy` is an exhaustive switch on the occlusion axis folded at the uniform's pack site, because the optics uniform carries no policy and W30's rule forbids a lane for a factor the CPU holds. **The generation and the read**: a dated `$comment-w31-g3c` on the two LIGHT documents (digests unmoved and asserted unmoved; file hashes `e2fa07589d99 → 49490eb9ff7a` and `25863dccef9d → 14c6bacf2eda`), the dark pair untouched and asserted untouched, **479 rows appended** row for row, the split to `superseded/e2fa07589d99.json`, freeze **1,818**, the 27 bed back at **230 gated cells / 726 rows** with `PREDICATE_EXCLUDES` and `MISSED_27_ROWS` unmoved, B3 at **0.00033889**. **Every record finding closed beside**: the changeset and README rewritten to the CSS DECLINE and given the four SHIPPED digests (`3dc24a74…` / `8a43f541…` / `ab3ed65a…` / `e1f42c56…`, which appeared nowhere); §8 (b)'s before-readings and its false "beds that carry no bound"; §7's "every one of them DOWN" (rank 39 is +0.02004 UP, and it is the regression); §8 (a)'s spread (1.2824 → **1.6216**, not 1.28 → 1.44); §12's reproducibility, where **the two sides were normalised differently** and the dark half is worse after the fit under either; the CSS structure-stop count (**13**, not 11); the tinted rows (**147 of 148** exactly zero); and eight further corrections. Four checkers and two scripts fixed by CODE: the split's "counts add up" clause read the manifest and could not fail (now off the files, with a probe that shows it failing); `verdict.py` printed the three declared SHADOW rows as em-dashes, named a cell the bed does not carry, and could not run after the split; `tier-coherence`'s exhaustiveness case was blind to the four OPTIONAL profile keys (now a compile error) and pinned the CSS mirror against a default that is 0 forever (now against the shipped documents); and the identity table's append-only proof rested on an unpinned JSON. **Found by the closure itself**: N7 is the identity in EFFECT on mode 1 and the residual is about the TARGET on mode 2 (measured, 0 bytes and 0.066 → 0.334); §8 (b)'s before and after were over different beds | §5.164 §13 | `results/2026-09-21-w31-g3c-accessibility-gate/` |
| G4 | **CLOSED 2026-09-21.** The adoption, the sheets, the records, the demo and 0.21.0 prepared and unpublished. **The material axis has two adopted rows for the first time** (Decision Log 3 (a)): `M1` bounds `R` — the body's chroma-to-structure ratio, web against native — with the median per bed in [0.80, 1.20] (**1.0486 / 1.0205 / 0.9994 / 1.0170**) and every cell in [0.60, 1.40]; `M2` bounds `interiorStdDevWeb` to within 2 % of the PRE-FIT generation (worst **1.317 %**), because `R` is scale-free in the deviations and is therefore blind to a body that loses chroma and structure together. **Three cells are recorded MISSED on the day the row lands** — `photo__rrect-sm__inactive` 1x light **1.5155** and 2x **1.4469**, `photo__rrect-sm__rest` 2x **1.4417**, all span 32 — with the surface-conditioned retention named as the lever, and the fourth sibling passing at 1.3567 is what a ceiling at 1.40 buys over one at 1.55. The cut is regenerated here AND **re-derived inside the test** from `results/matrix.json` and the two superseded files it names, which closes the snapshot hole §5.162 §9 found in B1's shape; `cut-discrimination.txt` shows each of four clauses going red on a perturbation and the cut coming back byte for byte. `MISSED_27_ROWS`'s owner walks the chroma cut too, so the list stays machine-derived in both directions. **The eye did not stop the cut**: twenty sheets from the CANONICAL capture tree (the first landing since W29 whose sheets are the pixels the rows were measured off), and on the four accessibility sheets vitrea's body is the flat occluded plate 0.20.0 drew, with `accessibility-identity.txt` reading **6,855 numeric readings across every axis, 0 moved** against the 0.20.0 generation. Three findings of the gate's own: **§5.164 §9's rim inversion is a reading up to about span 96**, not of the light scheme flat — at span 160 the ΔE panel is interior-dominated, and 160 is where the claimed cells live; **the overshoot the ceiling names is invisible** — the three missed cells and the passing sibling are indistinguishable from each other and from their references, because span 32 transmits so little that a 52 % relative excess is almost nothing, which argues FOR the clause since it is the same defect that reads 1.24 / 1.36 at span 160; and **the level stop biases both adopted rows and is gated by nothing**. **Records**: fourteen tracker entries; Decision Log 1 (c) executed — the "designed around a convergence" entry closed and removed, W29 Deferred item 8 closed with it, the 40 px plate's band kept open as the ruling's own words require; the coverage matrix re-scored with **one row moving where W30's two operators moved none** (§3.4's "takes colour from behind", `partial` with both halves of its reason now wrong), tally unchanged at 46 of 156; `CLAUDE.md` given the digest rule, the two adopted rows, the chroma operator and the corrected capture-tree rule; both READMEs given 0.21.0 and the stale `root.material` digest corrected to the shipped `e1f42c5656ef392f`. **The demo** gains the chroma pair on the calibration readout (main chunk 663.11 → **691.84 kB**, gzip 69.40 → 72.96), and `demo-figures.txt` reads the `checkerboard` control **bit-exact** — every projected figure +0.000000 and the web chroma pair exactly 0.000000 — while ΔE mean falls 0.0235 / 0.0259 on the two `rrect-lg` cells. `/laws/` is unchanged and the reason is recorded. **A gap the demo shots found**: `DARK_GROUND.field` is 0, so the site's dark stage is achromatic and cannot show the endpoint this wave moved most. **Folded from G3c's review before the cut**: the changeset and the renderer README said the retention stands down "under Reduce Transparency or Increase Contrast" — false, since only Reduce Transparency raises an occlusion and macOS 27 decoupled the switches, so IC alone draws the operator at full value; both corrected and the gap recorded with its design question. **The chain** is green end to end at the 0.21.0 head: build / lint / root eslint **exit 0**, **2,662 unit tests over 183 files, 0 failed**, goldens **34** byte-identical, `test:gpu` **48**, platform-web Playwright **410** over four projects, React e2e **174 passed / 3 skipped / 0 failed** on three engines — **green, where the last four cuts each disclosed the standing driver-timing class** — and demo e2e **59**. `dry-run.txt` is clean at 0.21.0 with `workspace:` rewritten to `^0.21.0` in both dependents. `freeze.py verify` **1,818** at open and close; the 27 bed **230 gated cells / 726 rows**; `PREDICATE_EXCLUDES` unmoved | §5.165 | `results/2026-09-21-w31-g4-landing/` |
| G4 review closure | **CLOSED 2026-09-21**, beside the row above and moving nothing in a number. An independent read found **the gate sound** — every figure of the adoption reproduced, no bound mis-stated, no verdict unsupported — and returned **one blocking word, four record fixes and seven non-blocking items**, not one of them in a statistic. **B1**: `platform-web/README.md` called the Increase-Contrast-alone gap "a combination the reference bed does not measure"; the reference bed DOES measure it (`scenes.json`'s decoupled profile, 32 fixtures on disk) and what is missing is this wave's web-side read — corrected to "the wave's bed", which every sibling copy already said. **R2**: clause 7 read a bare MET while the chartered `mid-chroma-solid` sheets were never made, and the reason recorded in four places was wrong — **X1 is the freeze, X5 bars NATIVE capture only, X6 contemplates scratch captures by name, and G0 made those very sheets from a scratch web re-capture in this wave** — so the verdict is qualified beside (**MET on the `photo` half**), the Status line with it, and the miss is recorded as a **scoping choice**. **R3**: §5.164 §13's N7 — the unsampled-DOM path restoring toward the DECLARED tone, chroma **0.066 → 0.334** with the **gamut clamp binding at the shipped retention** — was carried by no tracker entry and no Deferred item and its §10 pointer dangled; a tracker entry and **Deferred item 16** now carry it and the pointer is repointed. **R4**: `mid-chroma-solid`'s LEVEL break (`interiorMeanWeb` **0.0761 vs 0.2856** dark inactive, **0.6134 vs 0.3957** light rest) was tracked nowhere — added beside the hue rotation in both records, with the consequence that a `--set probe` run answers the rotation and not the level. **R5**: every published "before" was a chroma-MEAN and no "after" was given in it — reproduced from `results/matrix.json` as **0.5118–0.5716 / 0.5757–0.6616 light** and **0.3499–0.3672 / 0.2188–0.2291 dark** against a pre-fit 0.2385–0.3304 / 0.1059–0.1227, with the native column reproducing §5.161 §3's to < 5e-5, and added to both READMEs and the CHANGELOG with the note that the fit was judged on the SPREAD ratio. Seven non-blocking, all beside: the worst dark reproducibility pair quoted PRE-fit in three records (**25.10 % / 28.70 %** post-fit); the band justified against the wrong spread in two comments (**1.9× / 3.8×** against the post-fit 10.60 %, not "five times"); a **fifth perturbation** added because the per-bed count guard had never been red (`cut-discrimination-closure.txt`, guard RED, cut restored byte for byte); **`M1` is against Apple and `M2` is a regression stop**, not two fidelity rows; four chain-record items (**eight** readings not seven, the build string **typed and not machined**, `--fail-if-no-match` added to `chain.sh` for the next chain, and `pnpm release`'s **last live exercise is 0.1.0** on an unmoved `@changesets/cli` 3.0.1); `eye.md`'s "nearly black on all four" is the interior and the field while **the rim is bright on all four**; and the tracker's header rule reconciled to the two practices the file actually uses. **0.21.0 does not move and `.changeset/` is untouched**; no material, document, row, golden or test assertion changes; `freeze.py verify` **1,818** at open and close | §5.165 §9 | `results/2026-09-21-w31-g4-landing/` (two evidence files added beside, none replaced) |

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

*Execution notes beside the ruling, 2026-09-21 (the parent, from the adversarial review; the
ruling is unchanged, its enforcement is made mechanical):* (a) is executed over **gate-groups**,
because three of W30's eight leaves are inert only through a gate (Grounding); the identity table
is append-only and each entry carries its inert-law unit case; the rule is versioned and the
version recorded in every document re-sealed under it; the 26.5 documents are not edited. (b) is
enforced by artifact: the four document file hashes plus a hash over the enumerated source list in
clause 6, recorded by a committed script in every read's evidence, which refuses a second read at
identical document hashes unless the source hash moved and a non-fit reason is named.

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

### Decision Log 2 — RULED 2026-09-21 by the parent at G3's dispatch, under the standing "rest on your judgement": what the fit gate carries

Ruled on §5.161 as corrected by its closure (§11), with G1 and G2 merged and closed. (a) **The
leaf is `bodyChromaRetention`** exactly as §5.161 §5 names it: inert identity 0; after
`colour = mix(backdrop, adapted, presentAlpha)` and before `var materialColour = colour`;
chromaticity restored toward the blurred backdrop's carried to the colour's own linear luma,
luma held by construction, chroma scaled toward the neutral at fixed luma for gamut; **no
`toneAdapt` gate**, on the closure's reason (a retention toward the backdrop's chromaticity is
inert wherever the backdrop is achromatic, the only region the band can fire in) with the
condition recorded on any document that re-opens the band; two values across the light and dark
documents; the receded documents carry their **own** value read on the inactive cells; the
accessibility documents inherit the light value. (b) **The CSS projection on the corrected
ceilings** (light 0.5654–0.5995, already met by the authored `saturate()`; dark 0.2651–0.2767
against 0.906): a term is derived from the leaf on both documents only if it adds reach without
moving the authored constants, measured on scratch, else the tier records the residual and
carries nothing; the two `dom` rows are claimed conditionally on the dark tier's term and revert
to "reachable if" without one. (c) **The digest rule executes in G3** with the identity table as
`identity-table.json` declares it after the closure (the two-leaf σ gate; the heavy-second gate;
the scatter gate; this wave's leaf), append-only, versioned, each entry naming its gate-group
case (`w31-gate-groups.test.ts`); the 26.5 documents unedited and their own fields the live pin;
`digest-supersessions.json` history with a test that it still reproduces under rule 1. (d)
**`mid-chroma-solid` is granted for direction only**; the objective is R on the gated untinted
photo cells per pose; the level stop at the closure's corrected baseline, the structure stop,
B3, and the expected-unmoved rows are hard stops; the invariant twin is read beside R. (e) **The
holdout rule by artifact**: a committed configuration script (document hashes + a hash over the
enumerated source list) run before the read, refusing a second read at identical document hashes
without a named non-fit reason. (f) **One merge** (X10): the leaf, the rule, the fit, the seal and
the read land on one branch and are merged whole; `PREDICATE_EXCLUDES` and the counts move only in
the commit that carries the read. (g) **Adoption is decided at G4** on G0's identifiability
argument and the fit's own reproducibility, with the structure stop as a second gated row and the
WebGPU tier only if adopted.

### Decision Log 3 — RULED 2026-09-21 by the parent on G3's draft below as reviewed (§5.164's independent review and its two addenda): the accessibility regression is fixed before the cut; the tolerance is adopted at 1.40; the surface-conditioned form and the accessibility documents' own values are deferred with their evidence

**Ruled.** (d) **The retention regressed the two accessibility paths and that is fixed before
0.21.0, not deferred.** Reduce Transparency and Increase Contrast are the light document plus an
occlusion lift (`occlusionLiftForPolicy`; `α_eff = nominal + lift·(1 − nominal)`), and the leaf is
applied unconditionally: the review reproduced R on their untinted photo beds going 0.9096 →
3.0374 (RT active), 0.8294 → 1.9923 (RT inactive), 0.8147 → 2.9489 (IC active), with every
perceptual reading on those cells moving the wrong way (`oklabDeltaEP95` +89 % on IC
`photo__rrect-lg__rest`) inside bounds too loose to trip. Three of those four beds sat inside the
wave's own band at 0.20.0. The fix is the smallest rule that restores 0.20.0's rendering there
exactly and is an identity everywhere else: **the retention acts on the plate's un-lifted share**,
`r_eff = r · (1 − lift)` where `lift` is the resolved policy lift (0 under no accessibility
policy — bit-identical on every standard row, proven by the goldens, the unit case and a scratch
spot-check — and the document's lift under a policy). If the measured accessibility R under that
rule does not return to within the band 0.20.0 was in, the hard gate (`r_eff = 0` under any
lift) is used instead, and the choice is a measurement recorded in §5.164's closure. The light
documents get a dated `$comment-w31-g3c` so the file hash names the renderer that drew (W30 G3b's
idiom; the digests do not move), the four light profiles are re-read at those bytes under the
holdout rule's non-fit clause (`--source-moved-because`), the dark profiles are untouched, X10
holds in the same merge. (a) **Adopt** the chroma tolerance on the WebGPU tier with G0's two
conditions and G3's third, the per-cell clause two-sided at **[0.60, 1.40]** — the review's
corrected cost: THREE cells of the declared bed exceed 1.40 (`photo__rrect-sm__inactive` 1x and
2x light, `photo__rrect-sm__rest` 2x light) and are recorded MISSED under the row, against a
post-fit light-active spread of 0.8891–1.4417 (1.62×, not 1.44×) and a dark reproducibility that
WORSENED against the gate's own pre-fit bed (8.60 % → 9.93 % median, 17.70 % → 25.10 % worst) —
both recorded beside the ruling because the floor and the ceiling are what absorb them. (b) **The
surface-conditioned retention is deferred** with the review's structural reading added to G3's:
the retention restores a constant fraction of the FULL backdrop chromaticity regardless of what
the plate transmits (correlation −0.39 between transmitted chroma and gain over 56 cells), so the
accessibility case and the span overshoot are one defect; (d)'s lift rule is its first, policy-
level instance. (c) **The accessibility documents' own values are deferred** behind (d): under
the lift rule they need none for 0.21.0; a later chromatic wave measures whether they want one.

*G3's draft as put to the parent:*


Three questions, each with the measurement behind it in claims §5.164 and none
of them answerable from inside this gate.

**(a) The chroma tolerance: adopt, and with what per-cell clause?** Decision Log
2 (g) leaves this to G4 on G0's identifiability argument and the fit's own
reproducibility. Both are now measured (§5.164 §12): the instrument is no
noisier after the fit than before (4.36 % / 9.93 % against 4.49 % / 9.09 %), and
G0's two conditions — the structure stop as a second gated row, the WebGPU tier
only — both survive. What the fit adds is a reason to change the per-cell
clause: the bound is on the MEDIAN, the median is what the fit moved, and the
per-cell spread widened. **G3 recommends adoption with G0's two conditions and a
third — the per-cell clause two-sided rather than a floor alone.** The ceiling
itself is the parent's number: the worst cell on the declared bed is **1.5155**,
so 1.55 is green today and says almost nothing while 1.40 declares that cell and
its 2x sibling missed.
<!-- 2026-09-21, G3c review closure (claims §5.164 §13, finding F5): THREE cells
     of the declared bed exceed 1.40, not two — `photo__rrect-sm__inactive` at 1x
     light (1.5155) and 2x light (1.4469), and `photo__rrect-sm__rest` at 2x light
     (1.4417). The ruling above already carries the corrected count; this draft's
     "that cell and its 2x sibling" is corrected beside rather than over. --> The choice is between a clause that passes and a clause
that is worth having, and it has to be made against the spread the fit leaves
rather than against the median it hits.

**(b) Is the retention's next form a function of the SURFACE?** §5.164 §8 (a)
measures that one constant per document closes the median and widens the spread,
that the same components are the outliers before and after, and that the holdout
cell overshoots at R 1.24 / 1.36 because `1 − sizedAlpha` falls as the span
rises. That is the same shape W30 found for the outer shadow's σ. The parent's
call is whether the next chromatic wave fits a law rather than a constant, and
on what bed — the dark half has four cells at one span each, which is not enough
to fit a slope on.

**(c) Do the two accessibility documents get their own retentions?** They
inherit the light value under Decision Log 2 (a) and read R 3.04 / 2.95 active
and 1.99 / 0.14 inactive at the canonical bytes, on beds that carry no bound.
An inherited constant that reads three times the reference on one bed and a
seventh of it on another is a value nobody measured, and it will stay unmeasured
until somebody charters it.

> **"On beds that carry no bound" is false, and the ruling above turns on it**
> (2026-09-21, G3c review closure; claims §5.164 §13, finding F2). Both profiles
> are gated in `test/adopted-thresholds.test.ts` —
> `TEXTURE_TIER_27_REDUCED_TRANSPARENCY` and its `dom` twin over 16 cells, the
> increased-contrast-coupled pair over 18 — and every one of those tables held
> while the body's chroma went to three times the reference's. What carries no
> bound is the chroma statistic `R` itself. A bound that exists and does not
> reach the thing that moved is what let a regression through; "no bound at all"
> would have been the milder fact.

## Surprises & Discoveries

- **The current generation's web captures exist nowhere on disk** (2026-09-21, the parent, on the
  review's finding). The canonical `web-captures/` holds the six macOS 26.5 trees; the two agent
  worktrees that still hold macOS 27 trees are at earlier document hashes (`96b36eedf1c4`,
  `272d1b0c3e10`), and G3b's worktree — which read the `880ab1e31450` generation the matrix now
  carries — was removed after merge. Every W30 read ran in a worktree and copied nothing to the
  canonical tree. `CLAUDE.md`'s "the canonical `web-captures/` beside it is gitignored — it lives on
  the capture machine and is what the sheets and the demo fixture are copied from" has been false
  since W29. Consequence here: the chroma cut re-captures its bed as scratch with a reproduction
  check (clause 1); from G3 on, the parent copies the read's tree to the canonical path at merge
  (clause 6). Tracker entry at G4.
- **The canonical `web-captures/` tree is not merely stale, it is a DIFFERENT GENERATION from the
  rows beside it** (2026-09-21, G0). The charter's Surprise above says the current generation's
  captures exist nowhere; the sharper fact is that the tree which does exist disagrees with the
  matrix. Re-measuring the six frozen macOS 26.5 trees with `--skip-capture` — no browser, today's
  metric on both sides — reproduces 282 of 284 cells exactly and misses two:
  `photo__glass-over-glass__rest` on the two light profiles, `texture` tier, `interiorMeanWeb`
  2.840e-03 and 2.527e-03 out. The `dom` tier of the same cells reproduces to the last bit, which
  leaves only the raster: the tree's files are dated 2026-09-10 and the rows were measured
  2026-09-11. Consequence: the macOS 26.5 columns for that one scene are read off pixels the
  committed row was not read off, and they carry the sentence. Tracker at G4, beside the entry the
  first Surprise already asks for.
- **`mid-chroma-solid` is level-broken on both schemes and cannot carry the wave's statistic**
  (2026-09-21, G0). The charter grants it as the probe anchor. Its 1x dark inactive cell reads
  `interiorMeanWeb` **0.0761 against a native 0.2856** over a backdrop of 0.2141 — the reference's
  receded body is BRIGHTER than what is behind it and vitrea's is a quarter of it — and its 1x
  light rest cell reads 0.6134 against 0.3957. Ratio (i) scales as `(level)^(−2/3)` exactly, so
  those bias the statistic by 2.29× and 0.75×. The anchor is granted to G3 for the chromaticity
  DIRECTION and must not carry the tolerance until its level agrees. Its `__rest` poses also exist
  on the LIGHT macOS 27 profile only; the dark bed's four `mid-chroma-solid` fixtures are all
  `__inactive`, which is why G0's dark sheet is the inactive pose.
- **The dark bed's conditioning is worse than Grounding states, and it does not matter**
  (2026-09-21, G0). Grounding names three dark `photo` cells in `PREDICATE_EXCLUDES` and says the
  dark calibration bed keeps "one well-conditioned untinted photo cell (`rrect-ml`)". In fact
  **every** untinted `photo` cell of both dark macOS 27 profiles is refused, in both poses at both
  scales on both tiers — and the dark bed has no ACTIVE `rrect-ml` fixture at all. G0 answers the
  mask question directly instead: the statistic computed under the hole-free declared region agrees
  with the silhouette's to 0.006 on ratio (i) and 0.001 on ratio (ii), across masks differing by up
  to 18,000 px and 131 holes. The refusal is the shape axis's and does not reach this one.
- **On the RECEDED TINTED cells vitrea's body has no chroma at all** (2026-09-21, G0). Ratio (ii)
  reads 0.001–0.006 against the reference's 0.54–0.65, while the ACTIVE tinted cells match almost
  exactly (1.433 against 1.435). That is W27c's seed collapse driving the paint to neutral where
  Apple's receded material keeps it — a tint-path defect, not a body-chroma one, frozen by X3 and
  sent to the tracker.
- **The CSS tier's room was reversed twice, and the second reversal is to
  nothing** (2026-09-21, G3). The charter's Design put the projection's headroom
  on the light scheme; G0's review closure corrected `css-ceiling.ts` and put it
  on the DARK one (§5.161 §11, B1), and Decision Log 2 (b) dispatched G3 on that
  correction. Rendered on the drawn tier the derived term buys **0.000** of the
  gap on the dark active cells — and still 0.000 at a retention of **1** — while
  on the light one it buys 0.76 to 1.04 and breaks both stops (§5.164 §5). So
  the dark ceiling §5.161 §6 declares is not an upper bound there at all: it is
  unreachable, because the alpha the expression is evaluated at is not the alpha
  the runtime solves. That is the same class of finding as B1 itself, one solve
  further along, and it is the second time an analytic ceiling on this tier has
  been corrected by looking at what it actually draws. Consequence: the two
  `dom` rows §5.161 §4 claimed conditionally are recorded as missed.

- **A fix made by a review closure had a failure mode the closure's own machine
  could not show** (2026-09-21, G3). §5.161 §11 finding N8 replaced
  `scratch-capture.sh`'s unsupported `pgrep -fc` with
  `pgrep -f 'playwright' | wc -l`. On a machine with NO foreign browser, BSD
  `pgrep` exits 1, `pipefail` hands the pipeline that status, an assignment takes
  its command substitution's status and `set -e` kills the script before a single
  cell is captured — silently, with exit 1 and no output. G0's own run could
  never have hit it, because the foreign `playwright-cli` daemon its §2 discloses
  was up throughout. G3's copy swallows pgrep's empty match and nothing else;
  G0's file is committed evidence and is not edited. The general shape is worth
  the entry: **a guard fixed on the machine where it fired is a guard tested
  only in the state it was fixed for.**

- **The smallest rule that fixes a regression is not always the ruled one, and
  naming the fallback in advance is what makes that cheap** (2026-09-21, G3c).
  Decision Log 3 (d) ruled the retention acting on the plate's un-lifted share,
  `r · (1 − lift)`, with the hard gate as its fallback and the choice declared a
  measurement. The lift rule left the accessibility beds at R 1.79 and 1.83
  where 0.20.0 had them at 0.91 and 0.81, so the fallback shipped. What makes
  the entry worth keeping is WHY the smaller rule failed: `1 − α` under a lift
  of 0.75 to 0.98 is a tenth to a fiftieth of what it is nominally, and a
  multiplicative operator restoring a constant fraction of the FULL backdrop
  chromaticity is a larger relative gain the less the plate transmits. The
  accessibility path and the span overshoot are the same defect measured at two
  different axes, which is what Decision Log 3 (b) defers — and a rule derived
  from the same wrong shape inherits it.

- **A comparison can be arithmetic nobody got wrong and still not be a
  movement** (2026-09-21, G3c). Two of the review's findings turned out to have
  the same cause once reproduced: §12's post-fit reproducibility is normalised
  over the pair's mean and the pre-fit figures it is compared to are normalised
  over `R₁ₓ`; §8 (b)'s "after" is a four-cell median with the holdout in it and
  the "before" it is read against is a three-cell median without. Every number
  was right. The sentences built on them — "the operator did not make the
  instrument noisier", "R went 0.9096 → 3.0374" — were not, and in the first
  case the true reading is the opposite on half the bed. A before and an after
  have to name the bed and the normalisation or they are two readings that
  happen to be adjacent.

- **The CSS tier already saturates.** `optics.ts`'s `backdrop-filter` carries `saturate()` at
  1.8 / 1.4, CSS-only, with no renderer counterpart and no pin; a chroma operator on the fidelity
  target now has an authored constant beside it on the derived tier that the charter's v1 called
  "available". Recorded in Grounding and X3.

## Outcomes & Retrospective

**CLOSED 2026-09-21 by G4's landing**, against the seven Parent-Level Acceptance clauses, on this
wave's branch at the 0.21.0 version head. The cut is prepared and unpublished: `pnpm release` is the
user's hand and the tag follows it. *The parent's final chain at the merged head `05d2d5a7` (Revision
Notes, 2026-09-21): every suite green except the React driver-timing class, red on its two standing
cases this run and green on G4's run of the same head minus the closure — disclosed, as at
0.17.0–0.20.0; accepting it is the user's.*

**0.21.0 PUBLISHED 2026-09-21, by the user's `pnpm release` on `c87b5493` (the head after the
parent's final chain record; the version bump itself landed on G4's branch); tag `v0.21.0`
(annotated, on that commit) pushed by the parent on 2026-09-21.** Registry: core 08:10:02.146Z,
react 08:10:04.854Z, web 08:12:09.283Z — **web last, and in two steps**: the React binding, which
requires `@vitreajs/vitrea-web@^0.21.0`, was listed 124 s before the web package's packument
carried 0.21.0 (span core→web 127.1 s), and the web TARBALL was not served for a further five
minutes after that — `GET …/vitrea-web-0.21.0.tgz` returned 404 at 08:12:39Z with the version
already in the packument, and 200 at 08:17:15Z — so the release-chain window recurred, the
eleventh time, and for the first time in two layers (metadata, then content); an install attempted
at 08:12:39Z inside it failed on the tarball and is recorded as such (it is the parent's own
first cold-install attempt, not an installation anybody depended on). Verified by a cold install
outside the workspace after the tarball was served (`npm install --prefer-online` of the three at
`0.21.0` plus React 19): all three at 0.21.0, ranges `^0.21.0`, all three entry points import
(core 44 exports, web **258**, react 37 — web's one new export is `BODY_CHROMA_RETENTION`, the CSS
tier's declined mirror at 0, §5.164 §11), `GlassRootHandle.materialProfileDocument` in the React
declarations, both material documents exported, no private package installed; installed
1 996 / 1 940 / 659 kB against 1 942 / 1 930 / 658 at 0.20.0 (the web package carries the four
re-sealed macOS 27 documents and the retention leaf's CSS-side constant; core's growth is the
changelog). **One reading moved by design and is recorded so nobody reads it as drift**: the
shipped `macos26MaterialProfileDocument` now reports the light active digest `b2b570e4adcea8fb` —
the document's OWN sealed field, which 0.20.0 reported as `currentSha256` `b340a4dee871633c` under
W30's supersession record — because rule 2 (Decision Log 1 (a); §5.161 §7b) drops the inert leaves
before hashing and the recorded digests are the live pin again. The publish accepts the two React
driver-timing reds as disclosed, as at 0.17.0–0.20.0.

The one-line result of the wave: **the body stopped being a neutral plate — it carries the
backdrop's chromaticity now, at a held linear luma, fitted per colour scheme and per window pose —
two of the seven rows `MISSED_27_ROWS` had carried since W29 cleared on a MECHANISM where the list's
own comment said no constant could reach them, the digest rule ended the class of exemption every
inert-leaf addition had needed, and the wave's tolerance is adopted as the first two rows the
material axis has ever had, with three cells recorded missed on the day they land.**

And the wave's sharpest single finding is one it did not set out to make: a review found the leaf
applied unconditionally under an accessibility occlusion lift, taking the body's chroma to three
times the reference's on beds that were INSIDE the wave's own band before it. The fix was ruled with
a fallback, the ruled rule was measured and declined, the fallback shipped in ten minutes of
capture, and 0.20.0's rendering came back 48 of 48 rasters identical. Naming the fallback in advance
cost one sentence.

### The acceptance, as verified

1. **The chroma is measured before the operator exists, by an instrument in which the blur cancels —
   MET, and the instrument's own declared form was wrong in a way that had to be kept.** G0 added 24
   optional schema-5 fields with unit cases, and one of them records that **the charter's Design
   paragraph is wrong**: a luma-only darkening scales ratio (i) by exactly `c^(−2/3)`, not by 1,
   because OKLab's `L`, `a` and `b` all scale by `c^(1/3)` while the declared denominator is LINEAR
   luma. The declared form was KEPT anyway — the exactly-invariant twin also very nearly cancels the
   plate composite and would make the instrument blind to what it measures — with the twin exported
   beside it and read at every step of the fit, and the consequence carried as the level stop. The
   web side was re-captured as scratch (616 cells, nothing appended, X6 recorded) and **all 552 macOS
   27 cells reproduced their committed rows to |Δ| exactly 0**. The residual: **0.333 dark active,
   0.551 light active**, web against native, so the light scheme carries it too. **Apple moved it**:
   ratio (ii) rises +0.22…+0.38 on every untinted `photo` and `mid-chroma-solid` cell of both schemes
   between macOS 26.5 and 27, while the mean-OKLab instrument the matrix already had reads the same
   change as a fifteenth of that — which is the clause's own question answered with a number.
2. **The mechanism is named from the shader, and the leaf shape from the tables — MET.** Chroma is
   lost in the plate's alpha and nowhere else: ratio (ii) reads 0.106–0.119 on the dark cells against
   `1 − sizedAlpha` = 0.0950, and the level-corrected plate predictor
   `(1 − sizedAlpha)·(Y_web/Y_backdrop)^(−2/3)` accounts for 0.897–0.996 of the measured ratio on all
   34 single-body photo cells with no fitted parameter. The two collapses were told apart, the leaf
   named with its identity, its luma-preservation in linear luma, its gamut behaviour, its place in
   the order and the receded documents' own value — and **no `toneAdapt` gate**, on a reason the
   review closure substituted for G0's: a retention toward the backdrop's CHROMATICITY is the
   identity wherever the backdrop is achromatic, which is the only region the band can fire in. The
   CSS ceiling was declared as a residual before the fit, corrected once by the closure and then
   found unreachable by the pixels (clause 5).
3. **Bounds before reads; the stop is a number; the rulings are already made — MET, and the
   identifiability argument was made and accepted.** The tolerance, the level stop as a number per
   cell, the structure stop, B3 and the expected-unmoved rows were declared in
   `bounds-declaration.md` before a leaf existed, and the four claimed rows were decomposed on the
   committed captures first: **90–93 % of ΔE² at the P95 pixels is chromatic** and the chroma lever's
   reachable floor is 0.062–0.066 against bounds of 0.17–0.19, so all four were CLAIMED rather than
   hoped for. G0's two conditions — the structure stop as a second gated row, the WebGPU tier only —
   both survived the read and the parent adopted on them (Decision Log 3 (a)).
4. **Three instruments land without a material change — MET.** G1 declared C1 on the departure
   profile's SHAPE and found that candidate (i), the fitted σ's width, **anti-correlates with the eye
   by a factor of forty**; it also found that the gap between B1's two sides is additive and nearly
   constant at +2.66 to +3.77 CSS px — the size of the shipped `spreadPx`, a leaf no wave has fitted
   — which is new named work. G2 classified all eleven transcendental call sites (8 clamped, 3
   proven, 0 stopped), found **one more reachable NaN than anyone had** (`highlight.ts`'s
   `angle_delta` past one revolution, reachable from a CSS custom property nothing clamps), and its
   own review closure found the readback guard reading its wall off the whole frame rather than per
   declared region. Goldens 34/34 byte-identical through both; freeze 1,818.
5. **The operator lands on the fidelity target with the CSS tier derived in the same commit, the
   level held, and the re-seal and the read in ONE merge — MET, and the CSS half is a decline.**
   `bodyChromaRetention` landed at inert identity 0 with linear luma held **by construction rather
   than by correction** — worst movement 4.35e-16 over 224 composites, and 2.5e-05 on a hardware
   adapter while the chroma rises 3.6× — and the digest rule executed with the four macOS 27 digests
   reproducing **the numbers G0 PREDICTED before the leaf existed**, the drop count moving 5/3/5/3 →
   6/4/6/4 and nothing else. The fit: 0.282 / 0.349 / 0.336 / 0.142, two rounds, with both hard stops
   held (level worst |Δ| 0.04932 against 0.055, growth +0.00006 against 0.005, structure 1.317 %
   against 2 %). **The CSS tier's term was derived, rendered and DECLINED on the measurement**: 0.000
   of the gap on the dark bed at every retention up to 1, and both stops broken on the light one.
   `tier-coherence`'s list is exhaustive over `MaterialProfile`'s keys now, so "green" says something
   about a leaf nobody thought about.
6. **Read once per frozen configuration, under the ruled definition as enforced by artifact — MET,
   and spent twice under the rule's own non-fit clause.** `configuration.py` recorded the four
   document hashes plus a hash over the enumerated source list before each read and **was verified
   refusing a second read at identical bytes**. G3 read 726 rows at the sealed documents with the
   holdout once; G3c re-read 479 under the non-fit clause with its reason on the command line, after
   a renderer fix that moved no constant. Both append-checks green, both splits applied, `freeze.py
   verify` **1,818** at every gate's open and close, and the macOS 27 bed back at **230 gated cells /
   726 rows** with `PREDICATE_EXCLUDES` unmoved — so this material changed no cell's shape.
7. **The landing — MET on the `photo` half; the `mid-chroma-solid` sheets are a miss, Deferred item
   9** (qualified beside 2026-09-21, review closure; claims §5.165 §9, finding R2 — the verdict below
   is what the gate read and is not restated). Clause 7 chartered sheets for the photo cells **and
   `mid-chroma-solid` in both schemes at both scales**, and only the photo half was made. The reason
   recorded at the time — that X1 allowed the gate no capture — is wrong: X1 is the FREEZE and says
   nothing about capture, X5 bars NATIVE capture only, X6 contemplates scratch captures by name
   ("scratch captures included"), and G0 made exactly those sheets from a scratch web re-capture in
   this same wave. The route was open and this gate declined it, which is a scoping choice and is
   recorded as one. What the clause did return: the tolerance adopted as `M1` and `M2`, from a cut
   regenerated at the adopting gate and re-derived inside the test, with three cells recorded MISSED
   at adoption and the lever named; twenty sheets from the canonical capture tree, looked at, with
   the accessibility band reading no regression by eye as well as at 6,855 numeric readings; the
   demo given the axis its own
   material just changed and a gap the demo shots found recorded rather than papered over; the
   coverage matrix re-scored with one row's reason rewritten; `CLAUDE.md`, both READMEs and the
   changeset saying what moved, with the changeset's accessibility claim CORRECTED before it was
   consumed; the tone stage's ruling executed and W29's Deferred item 8 closed with it; the fixed
   group versioned **0.21.0**, dry run clean with `workspace:` rewritten, unpublished.

### What the wave cost, and what it found

It cost six children — G0, G1, G2, G3, G3c and G4 — **five independent reviews** (one per instrument
child, one of G3 that found the shipped regression and produced Decision Log 3, and one of G3c that
ran beside G4 and folded into this landing), and **not one native pixel** (X5): every fixture it
fitted on was on disk from W29. Two canonical reads and one scratch re-capture were the whole of the
machine time.

What it found, beyond the operator:

- **A defect can be structural and show up first as a policy bug.** The retention restores a constant
  fraction of the FULL backdrop chromaticity regardless of what the plate transmits. At a span that
  is an overshoot on the largest surface; under an accessibility occlusion lift, where `1 − α` is a
  tenth to a fiftieth of nominal, it is a body at three times the reference's chroma. The ruled
  smaller fix — scaling the retention by the plate's remaining share — **inherits the same wrong
  shape** and failed for exactly that reason. They are one defect at two axes, and the deferred
  surface-conditioned form is what closes both.
- **A fix ruled with a fallback is a fix that was measured.** Decision Log 3 (d) named the lift rule
  and named the hard gate as what to use if the measurement did not come back. It did not, and the
  gate shipped in ten minutes of capture rather than in a second round trip.
- **A digest rule is only as good as the prediction it survives.** G0 printed the four rule-2 digests
  on a material that did not yet have the wave's leaf; the seal computed them on one that does, and
  they reproduced to the digit. What moved was the drop COUNT. That is the whole claim of a
  digest-neutral operator, checked rather than asserted — and it is worth doing in the gate BEFORE
  the one that adds the leaf.
- **An analytic ceiling computed from a solve is a statement about the solve.** The CSS projection's
  headroom was put on the light scheme by the charter, corrected onto the dark one by a review that
  found `css-ceiling.ts` evaluating an alpha the runtime does not draw, and then found by the pixels
  to be **nowhere**: on the dark bed the derived term buys 0.000 at every retention up to 1. Two
  reversals, the second to nothing, and only the tier could say.
- **A comparison can be arithmetic nobody got wrong and still not be a movement.** §12's
  reproducibility normalised the two sides differently and §8 (b)'s before and after ran over beds of
  different sizes. Every number was right; the sentences built on them were not, and in one case the
  true reading is the opposite on half the bed. **A before and an after have to name the bed and the
  normalisation.**
- **A clause that cannot fail reads PASS forever.** The split's "counts add up" was `n == n` on every
  input and had read PASS in every gate since W30 G1. It was found by reading the code. G4 adopted
  its two rows only after showing each of four clauses going red on a perturbation and the cut coming
  back byte for byte.
- **A bound that exists and does not reach the thing that moved is what lets a regression through.**
  The two accessibility profiles carry 16 and 18 gated cells and every table held while the body's
  chroma tripled. "No bound at all" would have been the milder fact.
- **A predicate that reads a threshold off the whole frame is a predicate about the frame.** G2's
  readback guard read its wall off the raster's peak, so a hole inside a dim surface escaped whenever
  a brighter one was in shot. Both of that guard's defects — this one and the false positive the gate
  found itself — were fixed by making the predicate name which DECLARED thing it is talking about.
- **A guard fixed on the machine where it fired is a guard tested only in the state it was fixed
  for.** A review closure's `pgrep` fix killed the capture script silently on any machine with no
  foreign browser running; the gate that found it could not have been the gate that wrote it.
- **A sheet can hold the residual the metrics frame as two numbers.** On `photo__capsule-button__rest`
  the body is greyer AND darker than the reference and the eye sees one defect; the chroma statistic
  and the level stop see two, and only one of them is adopted.

### What is written down that was not before

The wave's instruments are committed and re-runnable: the per-pixel chroma instrument in
`packages/calibration/src/metrics/` with its unit cases and its exactly-invariant twin;
`chroma-fit.py`, whose `cells()` drops every holdout row in the one function every reader is built
on; `configuration.py`, which refuses a second holdout read at identical document bytes and was
verified doing so; `exterior-instrument.py` and `support-rule-check.py`; `digest-rule-proof.ts`,
`identity-table.json` and the two tests that pin the live table to it by SHA-256 and by literal;
`accessibility-read.py`, `comment-generation.ts`, `append-check.py` with a discrimination probe that
shows its corrected clause failing; and G4's `chroma-cut.py`, `cut-discrimination.py`,
`accessibility-identity.py`, `sheets.ts`, `demo-figures.py` and `sheet.py`.

`MATERIAL_IDENTITY_TABLE` is new and is the thing that ends a class rather than an instance: an
append-only constant beside `DEFAULT_MATERIAL_PROFILE` under which a leaf at its declared inert
identity moves no document's digest, so **no wave spends an exemption for an inert leaf again** and
`digest-supersessions.json` becomes history with a test that keeps it true.

And the ledger gained five sections — §5.161 through §5.165, with §5.161 §11, §5.162 §9, §5.163 §8
and §5.164 §13 as the four review closures — in which every corrected number is recorded BESIDE the
text it corrects and not one recorded number is rewritten.

## Revision Notes

- 2026-09-21 (the parent): **0.21.0 PUBLISHED**, by the user's `pnpm release` on `c87b5493`
  (registry core 08:10:02Z, react 08:10:04Z, web 08:12:09Z — web listed last, 127 s after core,
  and its tarball served only at 08:17:15Z, five minutes after its packument: the release-chain
  window recurred, the eleventh, in two layers for the first time; the parent's own cold install at
  08:12:39Z failed on the tarball's 404 and was rerun after it was served); tag `v0.21.0` annotated
  on `c87b5493` and pushed; cold install verified (core 44 / web 258 / react 37 exports, the one
  addition `BODY_CHROMA_RETENTION` at 0; both material documents exported;
  `GlassRootHandle.materialProfileDocument` declared; the shipped 26.5 light digest reads the
  document's own `b2b570e4adcea8fb` by rule 2's design where 0.20.0 read `b340a4dee871633c`;
  1 996 / 1 940 / 659 kB). The publish accepts the React driver-timing reds as disclosed. Status
  and §Outcomes carry the record beside the "prepared and UNPUBLISHED" text.
- 2026-09-21 (the parent): **G4 merged (`3e3c906c`), its review closure merged (`05d2d5a7`), and the
  parent's final chain run on the merged tree at the 0.21.0 head** — machine 27.0/26A428 (typed),
  RT 0, IC 0, slider 0.5 recorded before each browser suite: freeze 1,818 at open and close; build,
  lint and root eslint exit 0; unit **2,662** (policy 23, motion 164, geometry 170, renderer-webgpu
  561, core 302, platform-web 631, react 169, calibration 596, demo 46); goldens 34 byte-identical;
  gpu 48; platform-web 410 across four projects; demo 59; the 27 bed 230 gated cells / 726 rows;
  React **172 passed, 3 skipped, 2 failed** in the driver-timing class — `presence.spec.ts`
  "authored presence is monotone in place" on chromium (elapsed 533.1 ms against 420.1) and
  `morph-materialize.spec.ts` "the end that is absent is inert, and is released when it has gone"
  on firefox — the same two cases as W30's G4 run, recorded in the tracker beside and not rerun;
  G4's own run of the same suite at this cut was green (174 / 3 / 0). Logs
  `results/2026-09-21-w31-g4-landing/chain-parent-final-*.txt` beside G4's, written by
  `chain-parent-final.sh` (G4's `chain.sh` with the parent's file names). The status stands:
  **CLOSED, 0.21.0 PREPARED, UNPUBLISHED**; `pnpm release` is the user's hand and the tag follows it.

- 2026-09-21 (G4 review closure): **the gate was sound and the record was not, and the two ways it
  was wrong are both worth carrying** (claims §5.165 §9). Nothing in a number moved; 0.21.0 did not
  move; the only code touched was two comments and a shell flag.
  - **A contract quoted from memory is an excuse with a citation on it.** Four records said
    `mid-chroma-solid` could not be captured because of X1. X1 is the freeze and says nothing about
    capture; X5 bars native capture only; X6 contemplates scratch captures by name; and **G0 made
    exactly those sheets from a scratch web re-capture inside this wave**. The sheets were a scoping
    choice and they read as an impossibility, which is the more comfortable of the two and the one
    nobody re-checks. A gate that declines chartered work should say it declined, because "the
    contract forbade it" is a sentence a later wave will not test.
  - **State the after in the statistic the before was stated in, or the record has a hole a reader
    cannot see.** Every published description of this wave's gap was a chroma MEAN and every
    published result was a SPREAD ratio, so the change had no closed sentence anywhere — and on the
    light scheme the "before" was `1 − alpha` rather than the mean, so the naive comparison said
    nothing had moved when it had roughly doubled. Two statistics is fine and often necessary; two
    statistics with only one of them carried to the end is not.
  - **The clause-that-cannot-fail class has a twin outside the bounds.** This wave found it twice in
    its own adopted rows and closed both. It was also in `chain.sh`, where a `pnpm --filter` without
    `--fail-if-no-match` exits 0 and runs nothing — an empty log, a green exit code and a ledger row
    saying a suite passed that never ran. A verification step that cannot report absence is the same
    defect as a bound that cannot go red, and it lives wherever a runner selects its work by name.
- 2026-09-21 (G4): **the wave's tolerance is adopted, the eye did not stop the cut, and the clause
  the parent chose is a statistic rather than a picture** (claims §5.165). Five things worth
  carrying past this gate.
  - **A cut regenerated at the adopting gate is half of what W31 G1's closure found.** Decision Log
    3 (a) ruled the cut regenerated here rather than read from an earlier gate's evidence, which is
    the fix §5.162 §9 named for B1's shape. The other half is that a cut committed at THIS gate is a
    snapshot for the next one, so the gate re-derives every figure in it from `results/matrix.json`
    and from the superseded files it names, in both directions. A read that moves a row moves the
    rows whether or not anybody re-runs the script. The discipline generalises past cuts: **an
    artefact a bound reads should be checkable against the thing it was derived from, in the same
    case that reads it.**
  - **A newly adopted row has never been red, and that is the one thing to check before adopting
    it.** `cut-discrimination.txt` perturbs the committed cut four ways and records which clause
    each turns red, restoring between perturbations so nothing accumulates. It cost one script. The
    class it guards is the one the split's `n == n` belonged to, and the only way that class is ever
    found is by making a green thing fail on purpose.
  - **A ceiling can be worth having and invisible at the same time.** The three cells M1 records
    MISSED at 1.52, 1.45 and 1.44 are indistinguishable by eye from the sibling that passes at 1.36
    and from their own references, because span 32 transmits so little that a 52 % relative excess
    is almost nothing. That is not an argument against the clause: it is the SAME defect that reads
    1.24 and 1.36 at span 160, carried there by the axis one constant per document does not condition
    on, and a clause that fired only where the eye already complains would add nothing. But it has to
    be recorded as what it is, because "three cells look wrong" is a different claim and is false.
  - **A wave can measure an operator into existence and leave the product with no way to show it.**
    The demo's dark stage is achromatic by construction — `field: 0`, for a reason its own contrast
    case guards — and the dark scheme is the endpoint this wave moved most. The sheets found it;
    nothing in the test suite could have, because nothing asserts that the site demonstrates what the
    runtime does.
  - **A sentence about a policy is a sentence about an AXIS, and the two are not the same.** The
    changeset and the renderer README said the retention stands down "under Reduce Transparency or
    Increase Contrast". The stand-down is on the occlusion axis; Increase Contrast raises no
    occlusion, and macOS 27 decoupled the two switches. The claim was true of the calibration bed —
    whose increased-contrast profile is the COUPLED one — and false of the runtime, which is exactly
    the shape a bed-shaped sentence takes when it escapes into a release note.

- 2026-09-21 (the parent): **G3c merged** (`c72f90b7`): the hard gate adopted on measurement (the lift
  rule left two accessibility beds at R 1.79 / 1.83), 0.20.0's accessibility rasters restored 48 of 48,
  every standard row bit-identical, the four light profiles re-read under the non-fit clause, thirty
  review findings closed beside. The read's capture tree copied to the canonical `web-captures/`
  (light hash `49490eb9ff7a`). **G4 dispatched** with Decision Log 3 (a)–(d) as ruled; G3c's own
  independent review runs beside it and folds into G4's closure.

- 2026-09-21 (G3c): **the regression is fixed by the fallback and not by the
  rule, and that is the gate's one finding of its own** (claims §5.164 §13).
  Four things worth carrying past this gate.
  - **A fix ruled with a fallback is a fix that was measured.** Decision Log
    3 (d) named the lift rule and named the hard gate as what to use if the
    measurement did not come back. It did not — two of three beds stayed near
    twice the reference — and the gate shipped in ten minutes of capture rather
    than in a second ruling. The cost of naming the fallback in advance was one
    sentence; the cost of not naming it would have been a round trip.
  - **A defect can be structural and show up first as a policy bug.** The lift
    rule failed for exactly the reason Decision Log 3 (b) defers: the retention
    restores a constant fraction of the FULL backdrop chromaticity regardless of
    what the plate transmits, so scaling it by the plate's remaining share still
    over-restores where that share is small. The accessibility beds are the
    same defect as the span overshoot, at a lift instead of a span.
  - **Two numbers compared as one statistic is how "no regression" gets
    written.** §12's "within a tenth of a point" survived because the pre-fit
    figures divide by `R₁ₓ` and the post-fit ones divide by the pair's mean, and
    §8 (b)'s before/after ran over a three-cell bed and a four-cell one. Neither
    was a wrong measurement; both were comparisons of things that were not the
    same quantity. A before and an after should name the bed and the
    normalisation, or they are two readings sitting next to each other.
  - **A clause that cannot fail reads PASS forever.** The split's "counts add
    up" was `n == n` on every input and had read PASS in every gate since W30
    G1. It was found by reading the code rather than by anything going red,
    which is the only way that class is ever found.

- 2026-09-21 (the parent): **Decision Log 3 ruled** on G3's independent review (six blocking,
  thirteen further, two addenda): the accessibility regression the review found — the retention
  applied unconditionally under an occlusion lift — is fixed before the cut by a lift rule that is an
  identity on every standard row, in a closure gate G3c that also closes every record finding and
  re-reads the four light profiles under the holdout rule's non-fit clause. The tolerance is
  adopted at [0.60, 1.40] with three cells recorded missed. G4 waits on G3c.

- 2026-09-21 (G3): **the operator landed, the rule landed with it, and the CSS
  tier's half was measured and declined** (claims §5.164). Four things worth
  carrying past this gate, none of them a correction of the charter.
  - **A digest rule is only as good as the prediction it survives.** G0 printed
    the four macOS 27 documents' rule-2 digests on a material that did not yet
    have this wave's leaf. The seal computed them on a material that does, and
    they reproduced to the digit; what moved was the drop COUNT. A rule that
    claims to be leaf-neutral should be made to say so in advance, on the
    numbers, by the gate before the one that adds the leaf.
  - **The charter and G0 both put the CSS tier's room on the dark scheme, and
    the pixels put it nowhere.** §5.161 §6 declared a dark ceiling of
    0.2651–0.2767 on ratio (ii), and its own review closure had already
    corrected that expression once for being evaluated at an alpha the runtime
    does not draw. Measured on the drawn tier the derived term buys 0.000 at
    **every** retention up to 1, because the converted alpha there leaves no
    backdrop for `saturate()` to act on. An analytic ceiling computed from a
    solve is a statement about the solve; the tier is the only thing that can
    say what it draws. The decline is therefore a measurement and the two `dom`
    rows are recorded as missed rather than widened.
  - **A stop that is met by a factor of eighty is telling you something about
    the operator's FORM.** The level stop's clause two — growth ≤ 0.005 — read
    +0.00006, because the retention holds linear luma by construction rather
    than by correction. What the bed did move by more than the arithmetic allows
    is `interiorStdDev`, by up to 1.3 %, and the cause is the capture's 8-bit
    quantisation: the movement scales inversely with the cell's own spread. A
    stop stated as a fraction of a small quantity will read the raster before it
    reads the material.
  - **One constant per document closes the median and widens the spread.** The
    four medians land inside the bound and the per-cell range goes from a factor
    of **1.2824 to 1.6216** on the light bed (1.28 → 1.44 as first written, which
    dropped the bed's two lowest cells; corrected 2026-09-21 by G3c's review
    closure, claims §5.164 §13, finding F4), with the same components the outliers on
    both sides and the holdout cell overshooting at R 1.24 / 1.36. That is what
    a multiplicative operator with one constant must do, and it names the next
    form — a retention conditioned on the surface, as W30 made σ a function of
    the casting span.

- 2026-09-21 (the parent): **G3 dispatched** on main after G0, G1, G2 and their three review
  closures merged (`89aba451`; freeze 1,818; 2,629 unit tests green), under Decision Log 2 — the
  parent's rulings for the fit gate on §5.161 as corrected. One merge for the leaf, the rule, the
  fit, the seal and the read (X10).

- 2026-09-21 (G2 review closure): **nine findings closed, no blocking one, and the guard's
  predicate was the only thing that was wrong rather than mis-stated** (claims §5.163 §8). An
  independent read reproduced every figure of the gate. Two findings are code and both are inside
  the charter's own (c) and (b) rather than beyond them. **The readback guard read its wall off the
  whole raster**, so a surface's sensitivity depended on what else was in the frame: a hole punched
  through a dim surface read 0 holes with a bright surface elsewhere and 1 without it, measured
  both ways. The wall is now read **per declared region** and candidates are bounded to the declared
  silhouettes — which is what "inside a declared silhouette" in (c) says, taken literally instead of
  approximated by the raster — and the presence-0 stand-down stops depending on the transparent page
  reaching the border. **The sweeps had no cross term**: (b) asks for both halves of every ratio and
  the gate swept each half with the other held at the shipped values, which cannot see a defect that
  is a COMBINATION, and §5.159b's was; twenty-eight cross readings now pair each ladder's endpoints
  with spans 32 and 340. The other seven are in the record and none moves a number: a statistic
  named `iou` that is containment, a refusal branch that enumerated the wrong artefacts, a division
  count wrong by an order of magnitude, a pre-merge test total, a standing watch that is test-time,
  a proof that can be half a clamp, and a residual that was a paragraph inside a closed tracker
  entry instead of an entry. **What is worth carrying forward**, beyond the corrections themselves:
  - **A predicate that reads a threshold off the whole frame is a predicate about the frame.** The
    guard's two defects — this one and the false positive the gate itself found before merging —
    are the same mistake in opposite directions, and both were fixed by making the predicate say
    which DECLARED thing it is talking about. A scene-level statistic is not a surface-level one,
    however close they are on a one-surface scene, and every bed scene that matters has more than
    one surface.
  - **A clamp does not always retire a proof.** `prelude.ts`'s base is now floored in the shader and
    the site is still PROVEN, because the scanner's objection was never only the sign: at an
    exponent above 1 the base's CEILING decides finiteness, and a floor cannot reach it. The gate's
    preference for a clamp over a proof holds; what it buys is the half of the proof that the
    source can carry. The split is unchanged at eight clamped, three proven, none stopped.
  - **A guard runs on the largest surface the suite has**, and the one that fails there fails
    everywhere it would have mattered. The per-region wall's first form merged two declared masks
    with a spread `push` and overflowed the stack on a 340 px caster — the same surface class
    §5.159b's third case exists for — inside the guard itself. It is the second form of that
    failure mode this module has had to avoid.

- 2026-09-21 (G0): **the charter is wrong in two places and the corrections are in the evidence,
  not in the prose above.** (1) Design's instrument paragraph asserts that "a luma-only darkening
  leaves the chroma-to-structure ratio unchanged". It does not: OKLab's `L`, `a` and `b` are all
  linear in the cube roots of the LMS responses, so multiplying linear RGB by `c` multiplies all
  three by exactly `c^(1/3)` while ratio (i)'s declared denominator is LINEAR luma and scales by
  `c` — the ratio scales by exactly `c^(−2/3)`, pinned to 0.35 % on an 8-bit field by
  `test/chroma.test.ts`. The declared form is kept, because the exactly-invariant form (over
  `sd(L_oklab)`) also very nearly cancels the plate composite and would make the instrument blind
  to what it measures; the invariant twin is exported beside it and the consequence is carried as
  the level stop. (2) Grounding's gate-group shape puts `sigmaThinOffsetPx` under the slope's gate.
  The law is `σ = sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan·(span − sigmaSpanRefPx))`, so
  at slope 0 a non-zero offset moves σ at every span and the slope does not gate it; at a non-zero
  slope it is a real floor and is not inert on its own either. The identity table declares a
  TWO-LEAF gate `{slope 0, offset 0}` gating `sigmaSpanRefPx`, which is what
  `w30-inert-laws.test.ts` actually proves and which reproduces the same digests. Both are recorded
  in claims §5.161 §§1 and 6 rather than edited into the text above, on the rule that a charter is
  a record of what was declared.
  - **2026-09-21 (the G0 review closure), beside this note and correcting two things in it.**
    (i) **This note is wrong in ONE place, not two.** Grounding names exactly three leaves as having
    no standalone identity — `sigmaSpanRefPx`, `sizeHeavySecondSigma{,2x}` and `sizeScatterScaleRef`
    — and `sigmaThinOffsetPx` is **not** among them, so the charter leaves it an ordinary value drop,
    which is sound: a plain value drop is injective for free. The two-leaf gate is therefore a
    **TIGHTENING** of a correct shape — it drops a strict subset of what Grounding drops — and not a
    correction of a broken one. The tightening still earns its place, and by value:
    `gate-group-proof-closure.txt` fingerprints a macOS 26.5 light material with `sigmaThinOffsetPx`
    5 — five CSS px of extra blur on every outer shadow, at every span, on both tiers — and under
    the grouping this note ATTRIBUTES to the charter it reads `b2b570e4adcea8fb`, the frozen digest
    itself. Under the charter's own shape and under the shipped one it does not. (ii) **The pointer
    is repointed.** (1) is in claims §5.161 §1 as this note says; (2) is in §5.161 **§7b**, the
    subsection the closure added because the digest rule had no record in the ledger at all — §6 is
    the CSS projection and always was. And the case the note credits with proving the two-leaf gate
    did not: `w31-gate-groups.test.ts` is the one that does (claims §5.161 §11, finding B4).
- 2026-09-21 (G0 review closure): **sixteen findings closed, four of them blocking, and not one of
  them in a number** (claims §5.161 §11, the new section listing each finding, how it was verified
  and what closed it, plus §7b, the digest rule's missing ledger record). The review reproduced
  every figure of §5.161 §§1–10 and found no measurement wrong; what it found was in the reasoning
  and the record — the part a reproduction of the numbers cannot check. Every correction is
  **beside** the text it corrects and dated, every committed output of the gate is byte-unchanged,
  seven evidence files are added beside them and none replaced, and no material constant, document,
  fixture, golden, bound, floor, leaf or matrix row moved (X1, X5; `freeze.py verify` **1,818
  intact** at open and close; no capture; `adopted-thresholds.test.ts`, `cli/gates.ts` and
  `test/compare-gates.test.ts` untouched, as X11 requires). What G3 has to carry from it:
  - **The CSS projection's room is on the DARK scheme, not the light one.** `css-ceiling.ts`
    evaluated an alpha the runtime does not draw — the conversion anchor forced where `root.ts`
    gates it on the linear chain's reach, and the source unsized where the runtime sizes it.
    Corrected, the ceiling is a function of the span: light **0.5995 / 0.5654**, dark **0.2767 /
    0.2651**. The light tier already reads ratio (ii) to 0.633, so the expression is not a bound
    there at all; the dark one binds at ~30 % of the reference's body chroma. **G3 derives the term
    from the leaf on both documents only if the derivation adds REACH without moving the authored
    constants, and records the residual otherwise.** §4's two `dom` rows are unaffected.
  - **The reachable floor is a floor to within 0.04 of OKLab `L`, not exactly.** The leaf preserves
    LINEAR luma and the statistic is OKLab's. Measured at the retention these cells need, the four
    floors recomputed under the restoration are 0.0677–0.0730 against bounds of 0.17–0.19: **all
    four rows stay CLAIMED**, and a later wave with a thinner margin may not read §4's premise as
    exact.
  - **The digest rule's gate-groups are proved by code now**, per group, with the gate held at its
    identity and the gated leaf swept off it — including the `sizeScatterScaleRef` = 0.03 the macOS
    27 light document actually ships, which nothing had ever evaluated the law at.
    `identity-table.json` cites those cases and keeps its first citations verbatim beside.
  - **Two readings that change what a fit is judged against**: the level stop's pre-fit baseline is
    **0.0060 light / 0.0210 dark** per cell on BOTH tiers (§7 (c) read it off the texture tier's
    active half), and ratio (iii) level-corrected says **Apple's light body removes 23–48 %** of the
    chroma a matched blur would leave — the light scheme has a chroma law rather than lacking one.
  - **One reading carried forward and one trap named**: the plate predictor
    `(1 − sizedAlpha)·(Y_web/Y_backdrop)^(−2/3)` accounts for 0.897–0.996 of the measured ratio (ii)
    on all 34 single-body photo cells with no fitted parameter, so the retention's target is
    readable rather than searched for; and `dom_material_alpha` clamps per channel inside a luma
    computation, so the `dom` tier is NOT luma-transparent and a movement there at G3 is to be
    explained rather than assumed away.
  - One premise **withdrawn** rather than restated: "the charter is wrong in two places" reads
    **one**. Grounding never put `sigmaThinOffsetPx` under the slope's gate; the two-leaf gate is a
    tightening of a correct shape, and the shape the note attributes to the charter is the one that
    would merge a material five CSS px of blur away into the frozen digest.

- 2026-09-21 (G1 review closure): **fourteen findings closed, none of them in a number** (claims
  §5.162 §9, the new section listing each finding, how it was verified and what closed it). The
  review reproduced every figure of both statistics and found no measurement wrong; everything it
  found was in the record — the part a reproduction of the numbers cannot check. Every correction is
  **beside** the text it corrects and dated, the reader's committed `.txt` and `.json` re-run
  byte-identical, one evidence file is added beside them and none replaced, and no material
  constant, document, fixture, golden, bound, floor, leaf or matrix row moved (X1, X5;
  `freeze.py verify` **1,818 intact** at open and close; no capture; `adopted-thresholds.test.ts`
  untouched, as X11 requires). What a later child has to carry from it:
  - **C1 is not adoptable as drafted.** The row shape read its cut from *this gate's* evidence
    directory, which is a snapshot of the matrix at W31 G1: adopted verbatim it would assert
    ≤ 0.0045 against frozen numbers and could never fail. **The wave that adopts C1 re-runs
    `exterior-instrument.py` into its own evidence directory and points `CUT` there**, and the
    block now also asserts the cut's provenance (`atDocuments` = shipped, `withHoldout` = false),
    which the draft did not. This is B1's own discipline one level up — in a path instead of a
    literal.
  - **`T` is span-confounded as one bound across 96, 128 and 160.** The window is fixed at 3–48 CSS
    px whatever the caster is and the `24-48` band carries 53 % of the weight, so part of the rise
    with span is the window filling up. Adoption considers a **per-span bound** or a **σ-normalised
    window**; the statistic and the exclusions stay exactly as declared either way.
  - **The population table the adopting wave writes its guard from is right in its counts and wrong
    in its composition**: span 128 on the light beds is **two** gated cells, not one.
  - **The `spreadPx` finding is softened but its Deferred item is not.** The size agreement assumes
    Apple's own outset is ≈ 0, which this bed does not measure; what is verified is that `spreadPx`
    3.1 and `offsetPx` 7.95 are byte-identical across the macOS 26.5 default, the 26.5 light and the
    27 light documents and that **neither dark document carries either** — so the joint fit of the
    shadow's three lengths stays the named work, and it is not this wave's (X3).
  - The backdrop-support rule is **kept** and its record corrected: reach 32 `impulse` rows, 14
    non-zero, no WebGPU-tier statistic moved (`support-rule-check.py` / `.txt`, new evidence).
  - One reason **withdrawn** rather than restated: "its own lever reverses" told the two candidates
    apart in the record and does not on the bed — candidate (ii) reverses at the same spans. The
    verdict is unmoved and rests on the other two reasons and on the per-band structure.

- 2026-09-21 (G2): **the WGSL range class and the refusal's wording landed** (claims §5.163). Every
  transcendental in `src/wgsl/` is now classified by a committed case — eleven sites, eight clamped
  by the source, three carrying a written range proof with a WITNESS, none stopped — and the two
  leaf bounds those proofs rest on are pinned on the runtime default and on every committed profile
  document, so a fit that broke one fails a case rather than a capture. Three things the charter
  did not anticipate. **A second reachable NaN**: `highlight.ts`'s `angle_delta` goes negative past
  one revolution into an undefined `pow` base, reachable from an application because the sweep
  phase comes off a CSS custom property nothing clamps; floored as an identity, goldens
  byte-identical. **The guard's predicate needed its silhouette clause to be a clause**: written as
  enclosure alone it fired on a single pixel of the outer shadow's quantisation tail, on two of
  forty-two `@gpu` cases, and the wall is now alpha at or above half the raster's peak — the same
  extractor W20 reads. **The W30 G3b residual is re-opened, not closed**: the overflow is one-sided
  so no exterior pixel can reach it, and `glass-over-glass`'s deepest interior pixel sits at
  x = 8.45 against 10.061, so the three texture cells moved across a change provably the identity
  on their scene. Beside it, from the same table, `rrect-48` also cleared the boundary and nothing
  had ever read that — a probe component, so never gated. The sweep rule went to root `CLAUDE.md`'s
  Conventions rather than to a calibration README that does not exist or to a ledger section nobody
  would find. Two config edits beside the work: `renderer-webgpu`'s unit tsconfig gains Node types
  for the scan's file reads and `tsconfig.build.json` takes them straight back out, so the shipped
  compile still sees none.
- 2026-09-21 (G1): **the exterior clause declared, and it is the SHAPE and not the width.** Both
  candidates were computed over the current generation from committed fields alone — no schema
  addition was needed, so `report.ts`'s shadow axis is untouched and X11 has nothing to report.
  Candidate (ii), the departure profile's shape read off the affine bands as a width-weighted
  transmission error `T`, **agrees with §5.160 §6's eye**; candidate (i), the fitted σ's relative
  error, **anti-correlates with it by a factor of forty** and reads 0.000 on the largest of W30's
  three refuted rows. C1 is declared on candidate (ii) at ≤ 0.0045 per standard bed per thick span
  — a bound today's material misses at spans 128 and 160 on all four beds and meets at 96 — as a
  **one-wave reading**, with the row shape written out in `bounds-declaration.md` rather than as a
  skipped case, because `adopted-thresholds.test.ts`'s convention is that every case in it is live.
  The charter's Design paragraph asked what a divergence between candidate (i) and B1 would mean
  and the bed answered it: **the two sides of B1 are not the same quantity** — B1 bounds the
  document's blur leaf, candidate (i) reads the rendered exterior — and the gap is additive and
  nearly constant at +2.66 to +3.77 CSS px, the size of the shipped `spreadPx`, a leaf the macOS 27
  material inherited and no wave has fitted. That is a new piece of named work for the Deferred
  list (§5.162 §5) and it is NOT this wave's (X3).

- 2026-09-21 (the parent): **v2, the adversarial review folded** (opus, read-only; one P0, seven
  P1, seven P2, all folded; nothing dismissed). What moved: the re-seal and the read are one gate
  (G3) under a new contract X10 pinning the 27 gated-cell count — the P0: a re-seal empties 230
  gated cells out of every bound until rows at the new bytes exist, which W30 Decision Log 4 (b)
  had already ruled and v1 had not carried. The mechanism is luma-preserving in LINEAR luma with
  gamut and `toneAdapt` behaviour stated and the two collapses told apart; the receded documents
  carry their own value. The instrument is the chroma-to-structure ratio, in which blur cancels,
  stated web-against-native and never against 1, with the raw ratio beside; the level stop is a
  declared number per cell, since no adopted row gates the material axis; the four claimed rows
  are decomposed into ΔL and Δ(a,b) before any claim; the chroma tolerance's fate is a one-wave
  reading unless identifiability is argued. The web side is re-captured as scratch with a
  reproduction check (Surprises). The CSS tier's existing `saturate()` is named, frozen under X3,
  and the projection's ceiling is a declared residual; `tier-coherence` gains an exhaustiveness
  case. The digest rule is executed over gate-groups with an append-only, versioned table; the
  holdout rule is enforced by artifact. G1 tables its candidate (i) beside B1. G2's clamp is to the
  finite range, its hole is an enclosed region with two stand-downs. File ownership and the merge
  order are X11. The dark bed's conditioning is in Grounding.
- 2026-09-21 (the parent): **Decision Log 1 ruled by the user** — "all according to you
  recommendation" — before the adversarial review returned: the digest rule by value, the holdout
  rule as W30 practised it, the tone stage kept. G3's precondition is now the review's fold and
  the three instrument children's merge.
- 2026-09-21: v1 of this charter, drafted by the parent from a read-only grounding of the composite,
  the chroma instrument, the four missed rows, W30's Deferred-at-close list and the two rulings its
  review asked for. Sent for adversarial review before any child opens.
