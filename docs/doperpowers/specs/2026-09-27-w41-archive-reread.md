# W41 — the archive re-read: the body as luma and chroma, its locality, and the exterior stroke, identified on the W39 archive and landed if they close (2026-09-27)

**Status: v1 DRAFT (the parent, from grounding memos A and B); adversarial review requested; Decision Log 1 to the user before G0.**

## Purpose

W39 (§5.184–§5.186) captured the bed this wave needs and closed at the negative: no declared
body law survives one code, the declared edge family is rejected before any coefficient, and
Apple draws a dark contour outside its path that no family had a term for. Its release archive
`w39-archive` (6,360 captures; seven runs; both schemes, poses and scales; repeat bar at the
0.5-code floor) and its never-opened holdout are on disk. W41 declares the next families on
those findings, identifies them on the same archive with **no native capture**, and lands what
closes: on the WebGPU tier through the identity table, with the CSS tier's carry or decline
measured, the canonical holdout read once by artifact, the eye beside the metrics, a release.

Three questions, each with the grounding reading that shapes its families:

1. **The body as luma and chroma, and the dark scheme.** Memo A: H3's certified 20.1 / 17.5-code
   dark miss is mostly channelwise extrapolation at the saturated bridges (H3 without both
   bridges reads 2.9 / 3.1; with them 20.1 / 17.5), and what remains on the fresh colours is
   chroma EXPANSION that shrinks with level, not a hue rotation (native encoded chroma
   directions stay within 3.02° of radial; observed radial gain 1.17–1.23 dark at Y 0.05 down to
   1.08–1.15 at Y 0.18; light 0.92–0.96). An exploratory family that applies the neutral curve
   to encoded luma and a level-dependent radial gain to encoded chroma (three ordinates) reads
   0.62 / 0.83 / 1.01 / 1.43 codes on calibration (light active / light inactive / dark active /
   dark inactive). Its scalar axis sees the bridges INSIDE the neutral interval (66 and 146),
   which is why the bridges stop being an extrapolation.
2. **The body's locality.** Memo A, on the vertical-gradient cells (local reference 121–135
   codes across the strip): the body follows neither F(local) (max 1.9–4.2 codes) nor F(local)
   plus one constant (1.5–3.2). Its slope against the local reference is about 0.6 of the
   uniform neutral slope when inactive (0.25 against 0.41 light; 0.36 against 0.63 dark), and
   when active it depends on the gradient's DIRECTION (light 0.715 for one direction, 0.147 for
   the reflected one; dark 0.724 / 0.320): reflected rows with the same local input differ by 3
   codes at 14.5 CSS px inward, both scales, while inactive reflected differences stay ≤ 1. The
   shipped tone solve takes the GROUP's luminance as its argument and `collapseTransmission`
   mixes group and local colour; the archive varies neither the group mean nor the blur, so a
   group/local blend and a wide blur are not separated here and the charter says so.
3. **The exterior stroke.** Memo B: a dark band whose aligned straight footprint is exactly one
   DEVICE pixel at both scales (identical shell-0 departures at 1x and 2x; inactive shells 1–3
   zero on straights, shell 1 occupied on oblique arcs by area integration), outside the supplied
   path (the interior shell −1 reads exactly the deep body when inactive), with the opaque
   control at zero exterior coverage; strongest at horizontal normals (grey-255 inactive: −55.5
   light / −109.5 dark at the arc apex against −43 / −86 on the straights), even in the inactive
   pose, with a small top/bottom asymmetry plus the shadow when active, and dark active's top
   straight exactly 0 while its arcs exceed 100 codes. Its output against the local backdrop is
   its own tone curve, scheme-conditioned (inactive top deficit dark/light is 1 at grey-128 and
   2 at grey-255; a shared material with scheme-dependent coverage needs ≥ 7.13 codes of error
   on four points), nearly channel-separable on the 42 fresh colours (max 1.5 codes from the
   neutral knots) but not at the dark bridges (input 32 → 21 on red, 14 on green). The shipped
   active shadow, predicted from the document's own constants, explains dark active's bottom
   within a code and the top below resolution; the stroke's absence at the top when active is
   the effective model, and hidden cancellation is declared non-identifiable.

## Parent-Level Acceptance

1. **Declared before fitted.** G0 commits, hashes and has independently reviewed: every family
   with its parameter count, working space, interpolation and out-of-range continuation; the
   discriminating cells per pair at ≥ 3 codes, with a discriminator that lives only on the
   bridges declared as such; the closure rules (W39 clause 8 verbatim: a law SURVIVES only at
   max(1 code, bar) on every required channel of every calibration AND validation cell/bin
   before the freeze; a survivor CLOSES only if it also meets that bound on the held-out cells;
   survivors within max(3, sum of bars) at every admitted discriminator are "insufficient
   resolution"); the stroke instrument's bins, populations and what each control proves; the
   stops. Nothing is fitted to native pixels in G0 beyond the grounding readings, which are
   recorded as readings.
2. **The split is W39's and is never re-cut.** Calibration, validation and holdout are
   `split.json` (w39-split-1). The holdout is the grey-255 bottom pair, the circular 160×96 pair,
   the W37 witness pair (circular 200×44) and the six held-out colours with their references.
   **W41's exposure is the W39 archive's only exposure**: ONE receipt binding every W41 candidate
   (body, spatial, stroke), logged at the W39 G0 evidence path `wave-identification-receipt.jsonl`
   and committed by W41; a failed exposure spends it; no candidate changes after it. W34's
   holdout stays spent. Validation is read-only transfer; the 96-span validation cells are never
   a source of coefficients.
3. **No pixel is new.** Every native number is read from the fetched release archive
   (`fetch-archive.py` verifies the digest before extraction) through the guarded reader; the
   raw runs and the producer's output are never read; nothing is captured. A question the
   archive cannot answer is recorded as unidentifiable, never answered by a sitting inside this
   wave.
4. **Identification precedes fitting; the bar is never fitted.** Fits on calibration only, equal
   mass per channel/bin, equal weight per cell; least-squares AND minimax; worst-channel and
   all-channel; every repeat state scored against the frozen prediction; rank and singular
   values; a certified global bracket wherever a family is linear in its parameters after the
   fixed neutral curve (W39 G2's LP with exact rational Farkas certificates), and a bounded
   deterministic multistart stated as LOCAL otherwise; the freeze by artifact precedes the
   exposure.
5. **Censoring is a one-sided bound, declared.** A native channel ≥ 250 or ≤ 5 is a one-sided
   constraint (the prediction must reach the rail), never a reconstructed value; the cell's
   uncensored channels remain constraints. W39 G2's H3 dropped the whole light-red cell; W41
   declares this difference and reports both populations beside each other. The bridges are
   retained in every fit and every survival test; a family's ablation without them is a reading.
6. **Locality is a measurement before it is a leaf.** The gradient strip's body against
   F(local), against a group/local blend, and against a blend plus a signed vertical term is
   reported with the reflected-row differences per pose before any spatial law is nominated;
   the shipped tone solve's group argument is kept, blended or replaced on that reading, never
   two of those at once.
7. **The stroke is identified in the receded pose first**, where the exterior carries nothing
   else (the receded documents' shadow anchors are 0), then in the active pose beneath the outer
   shadow PREDICTED from the shipped active document's constants (σ law, spread, offset, the six
   anchors, occlusion falloff) at each required pixel on the supplied path, held, never refitted
   to absorb the stroke. The stroke composites outside the path only; the interior shells are
   witnesses that it adds nothing inside; the bright inner line (W35) stays inside and is not
   relabelled.
8. **Nothing shipped moves until a law closes** (W39 clause 9): in G0–G1 no byte under
   `scenes.json`, `fixtures/`, the frozen matrix, `results/generations/`, the six material
   documents, the goldens or any adopted threshold; the freeze reads 1,818 at every merge.
9. **If a leaf lands, the acceptance is W38's shape and W39 clause 10's chain**, staged through
   W40's publisher: each leaf through the identity table as an identity gate-group, WebGPU tier;
   the CSS derivation measured in a browser, carried, approximated with its residual, or declined
   (Decision Log 4); W38's per-channel-bin veto FIRST against the shipped treatment on the W39
   calibration archive (for the stroke the shipped treatment draws nothing outside the path);
   E2's 212-row rendered-edge regression frozen against the pre-W41 capture; R1 for the
   fixture-less paths; the rendered body and stroke re-read against the W39 bed's web-plannable
   cells (`wave.py plan`, 138 scenes) on the WebGPU tier; M1/M2/C1/X1/L1 re-read (C1 and X1 read
   the exterior and the silhouette, which a stroke touches); the canonical holdout once by
   artifact (`holdout-configuration/configuration.py record`); the capture tree copied and the
   superseded one moved; `check-capture-tree` exit 0; **the eye beside the metrics on a standing
   sheet script** over the whole canonical bed and the W39 bed cells (native | shipped |
   candidate with ΔE×8), committed under the gate; the changeset (`@vitreajs/vitrea-web` minor);
   the release checklist with CI green at the release commit; `pnpm release` is the user's hand.
10. **Every gap is recorded**: a family that fails, a stroke the CSS tier cannot carry, a hue
    the bed cannot resolve, a gauge fixed by convention, each with its numbers, in §5.191–§5.194,
    the Deferred list or the tracker.

## Grounding Baseline (main at `edfddf79`, W39 closed)

Memos A and B (`/Users/new/.claude/jobs/17c7ce02/tmp/w41-grounding-{body,stroke}.txt`, scratch
`~/vitrea-w41/grounding/`; both read calibration only through the guarded reader, 408 uniform
colour cells + 16 gradient cells, and 504 cells' near-edge bins, every bar 0.5). Their readings
are quoted in Purpose; G0 copies the memos into its evidence directory as readings.

Neutral knots as measured (input 40, 56, 72, 88, 104, 128, 150; deep median; both scales agree):
F light active 152, 160, 168, 176, 183, 195, 205; light inactive 150, 157, 164, 171, 178, 188,
197; dark active 69, 83, 96, 108, 119, 134, 146; dark inactive 60, 74, 87, 100, 111, 127, 140.
Bridges (seven-run deep RGB): red 192/32/32 → 255/133/133 light active, 255/129/129 light
inactive, 242/50/50 dark active, 234/41/41 dark inactive; green 32/192/32 → 96/246/96,
89/239/89, 22/193/22, 16/187/16. Only light red's R is censored.

## Design (advisory unless marked)

### The body families (MARKED: declared with parameter counts in G0 before any fit)

Let x be the cell's input sRGB (the uniform backdrop), W = (.2126, .7152, .0722), L = W·x the
encoded luma, v = x − L·1 the encoded chroma vector, F the stratum's neutral curve (seven
measured ordinates per scheme × pose, piecewise-linear in encoded input, end-segment
continuation outside 40…150, unit-cube clip). Every family is per scheme × pose; scales share.

- **B0 — H3** (W39's, the certified negative): reported as the baseline at its recorded
  brackets; not refitted.
- **B1 — E3, luma tone with level-dependent radial chroma gain**: y = F(L)·1 + g(L)·v, then
  unit-cube clip; g piecewise-linear over three ordinates at L = 63, 93, 118 (the factorial's
  three levels' encoded lumas), held outside, each in [0, 3]. **3 chromatic parameters** per
  endpoint beside the seven measured ordinates. Linear in its gains after F: the survival
  question is a certified LP.
- **B2 — EH6, hue-dependent gain**: the same decomposition with g(h), six periodic ordinates at
  the factorial's OKLab input hues 0…300, zero chroma at neutral. **6 parameters**. The competing
  explanation (hue- rather than level-dependent gain). Linear after F: certified.
- **B3 — O12, level-conditioned OKLab matrix**: H3′'s L tone with its 2×2 (a, b) matrix
  interpolated across three input-L nodes. **12 parameters**. Non-linear: bounded deterministic
  multistart, stated as local.
- **Discriminators** (from the exploratory readings, declared as instances not universals):
  B1 vs B2 on dark-active `factor-y2-c24-h300` blue (3.2 codes) and dark-inactive
  `matched-channel-4` red (3.0); B1 vs B3 only on the dark red bridge (25 / 28 codes) — a
  bridge-only discriminator, declared as such; B1 vs a constant gain 6.8 / 7.0 on a bridge and
  ≤ 1.6 elsewhere, so the level dependence is TESTED on the bridges and the fresh colours
  together, never claimed beyond C 0.024.
- **Not declared**: a fourth "H2 per scheme" (the shipped H2 already is scheme- and
  pose-specific and reads 72.9 / 49.0 / 93.6 / 125.3; H2′ 10.7 / 10.7 / 8.4 / 27.7 as a local
  candidate); a free two-stage tone (a factorisation ambiguity on one input/output curve).

### The spatial families (MARKED)

On the gradient cells (`v90-c-c44`, `v270-c-c44`, both poses, both scales; the central 48-CSS-px
straight strip, rows ≥ 6 CSS px inward, each row a seven-run median with its local no-glass
reference x(p)), with the surviving uniform body law B applied per row:

- **S0 — local (the null)**: body(p) = B(x(p)). Memo reading: max 1.9–4.2 codes.
- **S1 — group/local blend**: body(p) = B(m·x(p) + (1 − m)·x̄), x̄ the cell's reference mean,
  **m per scheme × pose in [0, 1]** (4). Reads the inactive slope ratio (≈ 0.6). The shipped
  `collapseTransmission` mixes group and local colour; the tone solve's argument is group-level.
- **S2 — blend plus a signed vertical interior term**: S1 plus a·(y − y_c)/h in encoded codes
  per channel-shared amplitude, **a per ACTIVE endpoint only** (2), inactive held 0 (reflected
  differences ≤ 1 there). Reads the active direction dependence (0.715 vs 0.147).
- Declared limits: the two gradients share one mean and one amplitude, so S1's blend and a wide
  blur are not separated, and S2's term is not attributed to a lighting frame (W39 clause 7
  carries). The strip excludes the arcs and the first 6 CSS px; a long boundary tail is a
  declared alternative reading for S2, reported beside.
- **Discriminators**: S0 vs S1 on the inactive slope over the 121–135 sweep (≥ 3 codes at the
  strip's ends by the memo's reading); S1 vs S2 on the active reflected-row difference (3 codes
  at 14.5 CSS px, both scales).

### The stroke families (MARKED)

Outside the supplied path, on every required exterior bin (shell 0 at 1x; shells 0 and 1 at 2x;
arcs and straights separate; both scales; the 44/64 calibration ladder; grey-128, grey-255, the
gradients whose arcs sweep the local level 86–170, and the 51 calibration colours' centre cells):

O(p) = (1 − c(p))·B_shadow(p) + c(p)·S(b(p)), with B_shadow the shipped active shadow composite
over the local backdrop (B itself when inactive), b(p) the local unshadowed no-glass sample
evaluated per sub-pixel sample BEFORE bin aggregation, and c the pixel-area coverage of a band
0 < d_device < w on the actual supplied path times an angular factor.

- **Geometry G**: one shared band width w in DEVICE pixels; angular coverage
  A(n) = [1 + β(n_x² − 1) + γ·n_y] / max_n[·], β per endpoint (4), γ per ACTIVE endpoint (2),
  γ = 0 inactive, coverage in [0, 1]; **7 parameters**. A **CSS-width rival** (w in CSS px) is a
  separately declared geometry. A **curvature rival** adds ONE shared inverse-radius multiplier.
  Max-normal normalisation fixes the coverage/colour gauge by convention, not as opacity.
- **M0 — affine material**: S_j = t·b_j + k in encoded space, 2 per endpoint (8); G+M0 = 15.
  Memo reading: affine misses 4.2–7.7 codes on the neutral knots — declared as the null.
- **M1 — a monotone channel-shared curve** at eight declared encoded inputs 40, 56, 72, 88, 104,
  128, 150, 255, 8 ordinates per endpoint (32); G+M1 = 39 (40 with curvature). Interpolation and
  continuation declared before fitting; black and near-black stroke colour are unread.
- **M2 — M1 plus a dark-only contextual correction in linear RGB**: D(S_j) − κ·max(0, Y − Y0)·(Y −
  D(b_j)), Y the linear backdrop luminance, then gamut-safe encode; κ, Y0 per dark pose (4);
  total 43 (44 with curvature). Reads the dark bridges' weak-channel gap (input 32 → 21 on red,
  14 on green) without moving the neutral curve. A linear-space M1 rival has the same count and
  is declared separately if G0's twin audit wants it.
- **Order**: inactive geometry and material first (γ = 0, no shadow); then active with the
  shadow held at the document's constants and γ free. The effective model at the active top is
  a stroke that vanishes at vertical normals; hidden cancellation is non-identifiable and is
  declared, not tested.
- **Discriminators**: M0 vs M1 on the neutral knots (≥ 4 codes); M1 vs M2 on the dark bridges
  (7 codes); G vs the CSS-width rival on the 2x shell-1 occupancy of straights (zero) against
  arcs (occupied); the curvature rival on the circular-vs-rrect arc difference at 2x (−47.5 vs
  −38.75 light active on grey-128), with 1x rrect arcs at n = 2 declared UNMEASURED.
- **Required tests**: one code on every required exterior bin with population ≥ 4, per channel;
  the interior shells −1…−3 as witnesses that the stroke adds nothing inside; the straddling
  rows as a diagnostic of the raster edge, never a closure bin; per scale, shape and pose,
  never pooled.

### The closure chain — W39 clause 8 verbatim; the single exposure covers every survivor

### The instrument (G0)

W39's readers (`w39_readers.py`) extended with: the gradient-strip body reader (row medians
with the local reference); the exterior band integrator on the supplied path with sub-pixel
sampling of b(p) before aggregation; the active shadow predictor from the shipped document
(proved against the WGSL on synthetic cases, as W39 G2 proved its H2 port to 5.9e-5 code); the
E3/EH6 forward models with the certified LP; the O12 and stroke multistarts. Every tool has
synthetic recoveries committed before any native fit.

### The archive of record — W39's; W41 adds none. Every W41 instrument output is committed
with its replay from the fetched archive and the raw root denied.

## Children

### G0: Declaration and instrument (ledger §5.191)

Branch `w41-g0-declaration`; evidence `packages/calibration/results/2026-09-27-w41-g0-declaration/`.
The declaration (families, counts, spaces, interpolation, discriminators, censor rule, closure,
stops) hashed and pinned to the W39 split and inventory; the instrument with synthetic proofs;
the receipt binding; the memos copied as readings; the standing eye-sheet script's first
version (native | shipped over the canonical bed and the W39 web-plannable cells, the candidate
column empty until G2); independent review; nothing fitted to native pixels.

### G1: Identification (ledger §5.192)

Branch `w41-g1-identification`. In order: the uniform body (B1–B3 against B0) → the spatial
families on the surviving body → the stroke, receded then active. Survival per W39 clause 8;
the freeze by artifact; the ONE exposure for every survivor; the resolution rule; the transfer
table to vitrea's rendered body and exterior per survivor (W37's pattern, from the W39 cells'
existing web captures where they exist, nothing rendered anew); the CSS reach per survivor by
algebraic projection (memo readings: E3 mirrors exactly on uniform backdrops where the saturate
does not clip, light green clips by 37.7 / 26.3 codes; a fixed-RGBA stroke has a ≥ 5.4–7.7-code
minimax on the neutral straights). Ends in Decision Log 2.

### G2 (conditional on Decision Log 2 finding a law): the leaves, the seal, the reads, the landing (ledger §5.193; §5.194 if split)

G2a render-and-read: the leaf(s) as identity gate-groups in `material.ts` and the WGSL (the
body operator before author tint; the spatial term at the tone solve's argument; the stroke in
the optics pass before the outside early return, with the field/scissor reach checked); goldens
attributed; the WebGPU render of the W39 web-plannable cells read against Apple's (the transfer
measured, not tabled); W38's per-bin veto; E2; R1; the CSS derivation measured in Chromium
(Decision Log 4). G2b seal-and-land: the four documents resealed; M1/M2/C1/X1/L1; the canonical
holdout once; the staged publication once (W40 G1); the capture tree; the eye sheets; the demo
and README; the changeset; the release checklist; `pnpm release` is the user's hand; tag after.

## Cross-Child Contracts

W39's **X21–X25** carry (the box and censor rule as amended by clause 5; prediction before
opening; the archive complete and cited; one canvas, attested positions). W34's **X1–X14**
carry where they concern the archive, the split and the ledger; **X5 is not invoked** (no native
capture). W37's **X15–X17** and W38's **X18** carry. X9's routing carries the 2026-09-26 note
(workers on `opus` or `astra` medium/high; reviews through the review-code agents,
`reviewer-high` at gate merges). New:

- **X26 — one exposure for the wave.** The W39 holdout opens at most once, for W41, on one
  receipt binding every W41 candidate; a failed exposure spends it; nothing changes after it.
- **X27 — the stroke is receded-first and composited outside only.** Identified with γ = 0 and
  no shadow; tested active beneath the predicted, held shadow; the interior shells witness that
  it adds nothing inside; no double paint at landing.
- **X28 — locality is measured.** The tone solve's group argument is kept, blended or replaced
  on the gradient reading; the blend/blur ambiguity and the boundary-tail alternative are
  recorded beside the choice.
- **X29 — censoring is one-sided and the bridges stay.** Clause 5; both populations reported.
- **X30 — the gauge is a convention.** Max-normal coverage normalisation; no coefficient is
  reported as physical opacity or width.

## Ordering & Dependency Map

Decision Log 1 → G0 (declaration, instrument; review) → G1 (body → spatial → stroke; freeze;
one exposure; Decision Log 2) → G2a → G2b → release → close. No W40-style housekeeping is
needed: the publisher, the generation store and the release-asset readers exist.

## Risks & Mitigations

- **E3 stays above one code on the dark scheme** (1.01 / 1.43 in the exploratory reading): the
  negative is recorded at its resolution; B2/B3 are the declared alternatives; no tolerance widens.
- **The blend and a wide blur are confounded**: declared; the leaf, if any, is the blend as an
  effective operator; a textured/frequency control is Deferred.
- **The stroke's gauge**: coverage and colour trade; fixed by the max-normal convention and
  reported as such; the CSS projection reads the effective product only.
- **1x arc populations of 2**: UNMEASURED, never regularised; the curvature rival is tested
  where populations admit it.
- **The predicted shadow is not the measured shadow** in the first two exterior pixels: the
  active stroke's small signed residuals are not reported as independent coefficients.
- **The CSS stroke cannot read the backdrop**: a fixed colour per document with a DPR-aware
  width is the best projection; Decision Log 4 carries, approximates with its residual, or
  declines on the browser measurement.
- **The W39 holdout is one exposure for everything**: the freeze is complete for every survivor
  before the receipt; a survivor found later waits for a new archive.

## Deferred / Out of Scope

- A dense hue sweep and C above 0.024; inputs below 40 and above 150; the black branch below
  encoded 0.003 (W36's, untouched).
- A textured, frequency or chromatic-gradient control that separates the group/local blend
  from the blur; a window-relative versus path-local lighting frame (needs an oriented path).
- A phase mechanism on a different actuator (W39 Decision Log 3).
- Span 160, the accessibility beds, author tint over coloured backdrops, dynamics and stacking.
- Black and near-black intrinsic stroke colour; the stroke under Increase Contrast.

## Tracking Map

| child | status |
| --- | --- |
| G0 | — |
| G1 | — |
| G2 | conditional |

## Decision Log

### Decision Log 1 — identification only, or landing in this wave (before G0; the user's)

The parent recommends landing in this wave: a survivor at one code on calibration, validation
and the held-out cells is exactly the shipping criterion, and G2's chain is W38/W39's as
written. Identification-only would end at Decision Log 2 with the leaves chartered separately.

### Decision Log 2 — a law or the negative, per question (after G1; the user's)

### Decision Log 3 — bounds and floors if a leaf lands (in G2; the user's)

### Decision Log 4 — the CSS tier's carry, approximation or decline, per leaf (in G2; the parent's, on the browser measurement)

### Decision Log 5 — the censor rule and the bridges (in G0, by rule; the parent's)

Ruled at charter: clause 5 / X29. Recorded here so that W39 G2's population and W41's are
never confused in the ledger.

## Surprises & Discoveries

- **H3's dark miss was the bridges' extrapolation, not hue dependence** (memo A): 20.1 / 17.5
  codes with them, 2.9 / 3.1 without, and the native chroma direction stays radial within 3°.
- **The stroke is one device pixel, not one CSS pixel** (memo B): identical shell-0 departures
  at 1x and 2x on aligned straights.
- **The body's slope on a gradient depends on the gradient's direction when active** (memo A):
  0.715 against 0.147 (light), 3 codes at 14.5 CSS px inward between reflected rows.

## Revision Notes

- 2026-09-27 (v1, the parent): chartered from grounding memos A (body) and B (stroke) on the
  W39 calibration cells; Decision Log 1 put to the user; adversarial review requested.
