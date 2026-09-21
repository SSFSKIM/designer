# W31 — the chromatic wave: the body carries the backdrop's hue, with three instruments in front

**Status: OPEN 2026-09-21 — chartered by the parent on the user's "let's proceed with next wave"
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
if" through the chroma on G0's decomposition); the highlight's angular reader; the decoupled
increased-contrast read and `compare`'s flag; the identifying sitting; the motion-metrics harness;
the CSS tier over pure black; inactive calibration cells above span 96; `samplingPaddingFor`'s
advisory constant; the Reduced Transparency opacity policy and the impulse specular point; the
slider's ends as evidence classes; a shadow section for `/laws/` (W30 Deferred 10); the thin
regime's instrument (W30 Deferred 4); the light bed's 16 px structure (W30 Deferred 3); the CSS
tier's `saturate()` constants as fitted rather than authored values.

## Tracking Map

| Child | Status | Claims section | Evidence |
| --- | --- | --- | --- |
| G0 | **CLOSED 2026-09-21.** The per-pixel instrument landed as 23 optional schema-5 fields with the unit cases, and one of them records that **the charter's own Design paragraph is wrong**: a luma-only darkening scales ratio (i) by exactly `c^(−2/3)`, not by 1, because OKLab's `L`, `a` and `b` all scale by `c^(1/3)` while the declared denominator is LINEAR luma. `interiorOklabLSdDev*` is exported beside it as the exactly-invariant twin. The chroma bed re-captured as scratch at the shipped documents (616 cells, nothing appended, RT/IC/slider recorded) and **all 552 macOS 27 cells reproduce their committed rows to \|Δ\| exactly 0**; two macOS 26.5 cells do not, and the diagnosis is that the canonical `web-captures/` tree is already a different generation from the rows beside it (Surprises). **The residual**, ratio (i) web/native on the WebGPU tier: **0.333 dark active, 0.551 light active** — the light scheme carries it. Ratio (ii) web 0.106–0.119 on the dark cells against `1 − sizedAlpha` = 0.0950, so the chroma is lost in the plate's alpha and nowhere else. **Apple moved it**: ratio (ii) rises +0.22…+0.38 on every untinted photo and `mid-chroma-solid` cell of both schemes between macOS 26.5 and 27 while the tinted cells move −0.03…+0.00, and the mean-OKLab instrument reads the same change as a fifteenth of that. Ratio (iii) says the DARK reference is not a blur (1.20–1.80× what a matching Gaussian leaves) and the LIGHT one nearly is (0.75–1.00). **All four claimed rows CLAIMED** — 90–93 % of ΔE² at the P95 pixels is chromatic and the chroma lever's reachable floor is 0.062–0.066 against bounds of 0.17–0.19. **The mechanism**: `bodyChromaRetention ∈ [0,1]`, identity 0, after the composite, luma-preserving in linear RGB BY CONSTRUCTION (both mix endpoints carry the same luma, so the renormalisation is an f32 guard), gamut by scaling chroma toward the neutral at fixed luma, **no `toneAdapt` gate because `toneAdapt` is identically 0 on the macOS 27 material** at every backdrop and span. **The digest rule proved**: `b2b570e4adcea8fb` / `874be66ea501621b` reproduce, the four macOS 27 digests printed under the rule, a moved default shown to move them — and the gate-group refined, because `sigmaThinOffsetPx` is NOT gated by the slope. Tolerance, level stop, structure stop and the identifiability argument declared; the CSS ceiling 0.784 light / 0.278 dark as a declared residual | §5.161 | `results/2026-09-21-w31-g0-chroma-cut/` |
| G0 review closure | **CLOSED 2026-09-21**, beside the row above and moving nothing in a number. An independent read reproduced every figure of §§1–10 and found sixteen things in the reasoning and the record — four blocking. **B1**: `css-ceiling.ts` evaluated an alpha the runtime does not draw (the anchor forced where `root.ts` gates it on `linearChainReaches`, the source unsized where the runtime sizes through `sizeOcclusionAlphaAt`); corrected, the CSS ceiling is **0.5995 / 0.5654 light** and **0.2767 / 0.2651 dark** by span against the recorded 0.784 / 0.278 — and since today's light CSS tier already reads ratio (ii) to 0.633 the light figure was never a bound. **The recommendation to G3 is reversed**: the room for a derived term is on the DARK scheme, not the light one. **B2**: §4's floor is measured in OKLab `L` while the leaf preserves LINEAR luma; measured, the restoration moves `L` by ≤ **0.040** and the four floors recomputed under it are 0.0677–0.0730 against bounds of 0.17–0.19, so all four rows stay CLAIMED. **B3**: the digest rule had no record in the ledger — now §5.161 **§7b**, with the rule, its version, the table, both frozen digests and the four macOS 27 ones. **B4**: two of the three gate-groups' cited cases did not prove the statement the table makes; closed by **code** (`w31-gate-groups.test.ts`, twelve cases, the shipped `sizeScatterScaleRef` = 0.03 among them), and the Revision Note's "wrong in two places" **reads one** — under the grouping it attributes to the charter, a material with `sigmaThinOffsetPx` 5 fingerprints to the frozen `b2b570e4adcea8fb`. Twelve non-blocking, all beside: `toneAdapt` is not identically 0 (it is zero because every backdrop is ≫ 1e-4); ratio (iii)'s level confound reverses the LIGHT reading — Apple's light body REMOVES 23–48 % of a matched blur's chroma; the invariant twin is not blind and G3 reads it beside `R`; §3's ratio (ii) columns are all-sets where its medians are the declared bed; the level stop's baseline is **0.0060 / 0.0210** on both tiers with the worst cell 2x dark `texture`; the anchor's dark bias is **2.41×**; **24** optional fields, not 23. Carried forward for G3: the level-corrected plate predictor `(1 − sizedAlpha)·(Y_web/Y_backdrop)^(−2/3)` holds at **0.897–0.996 on all 34** single-body photo cells, and `dom_material_alpha` clamps per channel inside a luma computation, so the `dom` tier is not luma-transparent | §5.161 §11, §7b | `results/2026-09-21-w31-g0-chroma-cut/` (seven evidence files added beside, none replaced) |
| G1 | **MERGED** — the clause C1 declared on the departure profile's SHAPE; candidate (i) recorded as the diagnostic that points at `spreadPx`/`offsetPx`; nothing adopted, nothing fitted, no capture. **Amended beside 2026-09-21 (review closure; claims §5.162 §9), no number in this row or in §5.162 rewritten:** an independent read reproduced every figure of both statistics and found no measurement wrong; its fourteen findings, two blocking, were **all in the record**, and **no statistic, bound, count, exclusion or verdict moved**. The two blocking: the drafted C1 row read a **frozen snapshot** of the matrix, so a dated condition now requires the adopting gate to re-run `exterior-instrument.py` into its own evidence directory and point `CUT` there, and the draft gains the two provenance assertions it lacked (`atDocuments` shipped, `withHoldout` false); and the backdrop-support rule's reach is **32 `impulse` rows, fourteen carrying a non-zero `T` up to 0.004287**, not eighty rows of zeros — the 48 `dark-solid` rows identify no affine band at all — with the rule **kept** because it is the axis's own constant and admitting all 32 moves no WebGPU-tier order statistic (it moves twelve counts and two unprinted CSS-tier span-44 medians). One reason **withdrawn**: "its own lever reverses" applies to candidate (ii) too, and the choice stands on the other two and on the per-band structure. Corrections beside: the span-96 per-cell maxima are 0.00508–0.00561 and all above 0.0045; the CSS tier is NOT worse everywhere (1x dark span 160, 0.00789 against 0.00921); §6's improvement ranges are 20–54 % and 8.5–32 %; **all 726** macOS 27 rows carry a shadow axis and 602 is the non-holdout count; span 128 on the light beds is **two** gated cells; the +2.66…+3.77 gap is the **WebGPU tier's** (CSS runs −4.74…+5.36); the `spreadPx` reading assumes Apple's outset ≈ 0 and is softened, with the unfitted half verified across three documents; the bilateral σ rule is inert on today's bed; and `T` is declared **span-confounded**, with a per-span bound or a σ-normalised window named as what adoption must consider. New evidence `support-rule-check.py` / `.txt`; `test/adopted-thresholds.test.ts` untouched; freeze 1,818 at open and close | §5.162, §5.162 §9 | `results/2026-09-21-w31-g1-exterior-instrument/`, `support-rule-check.txt` |
| G2 | **MERGED** — 11 call sites: 8 clamped, 3 proven, 0 stopped; 5 sweeps + 3 guard cases green; goldens 34/34 byte-identical; one NEW reachable NaN found and floored as an identity (`angle_delta`); both tracker entries closed; the W30 G3b residual's candidate REFUTED and the residual re-opened. **Amended beside 2026-09-21 (review closure; claims §5.163 §8), no number in this row or in §5.163 rewritten:** an independent read reproduced every figure and found **no blocking finding** and nine non-blocking ones; no material constant, leaf, document, bound, floor, row or golden moves. Two are code. **The guard's wall was the raster's peak**, so a hole inside a dim surface escaped whenever a brighter one was in frame — the review's pair read 0 against 1, and `glass-over-glass` is a two-surface scene; the wall is now read **per declared region** with candidates bounded to the declared silhouettes, which is the charter's own (c) taken literally, and the presence-0 stand-down becomes exact rather than incidental. **The cross term was never rendered**: twenty-eight readings now pair each material ladder's endpoints with spans 32 and 340, every one 0 undrawn at containment 1.0000 (`sweeps-cross.txt`). Beside them: `iou` was **containment** and is renamed in the shared module and both specs, recorded values unchanged; the refusal's **newer**-schema branch enumerated older-schema artefacts and now has its own sentence and a case that reads more than two words; `prelude.ts`'s `pow` base is **floored as an identity** (goldens byte-identical) and the site stays PROVEN because the base's ceiling is what the scanner still objects to — the split is unchanged at 8/3/0; the division count was **99**, not "over a thousand", with **three** uniform divisors and none of them a material leaf (`division-count.py`); §7's totals were a pre-merge branch reading, **2,613** at this closure's head and **2,617** after it, `test:gpu` **43**; the guard is **test-time**, in the e2e harness; and the sweep-phase residual is now its own tracker entry instead of a paragraph inside a closed one. One defect the closure found itself: merging two declared masks with a spread `push` overflowed the stack on a 340 px caster and took `w30-heavy-second-tap` down — fixed and pinned by a case. Goldens 34/34, `e2e/goldens` clean, freeze **1,818** | §5.163, §5.163 §8 | `results/2026-09-21-w31-g2-range-class/`, `sweeps-cross.txt`, `division-count.py`, `call-sites-closure.txt` |
| G3 | **OPEN 2026-09-21** — dispatched on main after G0, G1, G2 and their three closures merged; Decision Log 2 | §5.164 | `results/2026-09-21-w31-g3-chroma-fit/` |
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
- **The CSS tier already saturates.** `optics.ts`'s `backdrop-filter` carries `saturate()` at
  1.8 / 1.4, CSS-only, with no renderer counterpart and no pin; a chroma operator on the fidelity
  target now has an authored constant beside it on the derived tier that the charter's v1 called
  "available". Recorded in Grounding and X3.

## Outcomes & Retrospective

*(at close)*

## Revision Notes

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
