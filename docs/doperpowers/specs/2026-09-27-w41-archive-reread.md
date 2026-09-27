# W41 — the archive re-read: the body as luma and chroma, its locality, and the exterior stroke, identified on the W39 archive and landed if they close (2026-09-27)

**Status: G0 MERGED `cd55870d` (2026-09-27, §5.191): declaration 850747c1…, instrument proved on synthetic data, the single-exposure runner and the standing eye sheets landed; nothing fitted to native pixels. G1 (identification, the scratch leaves, the rendered check, the single exposure) is next.**

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
   group/local blend and a wide blur are not separated here and the charter says so. **And the
   W39 holdout contains no non-uniform backdrop**: on a uniform cell every blend collapses to the
   local law, so no held-out cell can referee a spatial law. The spatial question is answered on
   calibration as a bounded finding in this wave; its leaf does not land here (Decision Log 6).
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
   a source of coefficients. Of the held-out cells, the grey-255 BOTTOM pair is an off-centre
   placement the web runtime cannot pose, so it referees the numerical candidates only; the
   circular 160×96 pair, the witness pair and the six colours referee both the numerical and the
   RENDERED candidates (clause 11).
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
   **Three closure statuses are kept apart**: `measured` (an uncensored channel within the bound),
   `censored-bound-satisfied` (the prediction reaches the rail; it never certifies one-code accuracy
   and never counts toward a held-out coverage requirement) and `UNMEASURED`; an uncensored
   failure is binding whatever the censored channels say; a censored held-out cell is UNMEASURED
   (W39 X21 verbatim); a white exterior bin under a stroke candidate is scored on its uncensored
   channels and reported `censored-bound-satisfied` on the others, never as a zero-error pass
   (§5.186 §10's correction carries).
6. **Locality is a measurement before it is a leaf.** The gradient strip's body against
   F(local), against a group/local blend, and against a blend plus a signed vertical term is
   reported with the reflected-row differences per pose before any spatial law is nominated;
   the shipped tone solve's group argument is kept, blended or replaced on that reading, never
   two of those at once. **The strip is pinned in G0** (its mask, its reference-level domain, its
   row aggregation and both scales' definitions), and no deeper or wider strip is admitted after a
   reading. Because no held-out cell can referee it (clause 2), the spatial result is a
   calibration finding with its bounds, and its leaf is Deferred to a wave with a structured
   backdrop in its holdout (Decision Log 6).
7. **The stroke is identified in the receded pose first**, where the exterior carries nothing
   else (the receded documents' shadow anchors are 0), then in the active pose beneath the outer
   shadow PREDICTED from the shipped active document's constants (σ law, spread, offset, the six
   anchors, occlusion falloff) at each required pixel on the supplied path, held, never refitted
   to absorb the stroke. The stroke composites outside the path only; the interior shells are
   witnesses that it adds nothing inside; the bright inner line (W35) stays inside and is not
   relabelled. **The active identification is conditional on the held shadow model**: the shadow
   predictor is proved against the WGSL, not against Apple's shadow, so **shadow-only control
   bins** bound the predictor's own error: every exterior bin beyond the band at both scales (the
   shells that read exactly zero in the inactive pose, where nothing but the shadow can act when
   active), plus, as a stratum-specific observed zero, the dark-active top straight (memo B: 0 at
   grey-128 and grey-255 against a held shadow below 0.02). The light-active top straight is NOT a
   control: it carries −20 codes against a held shadow of −0.0001, i.e. stroke. A small signed
   active residual is never reported as an independently identified stroke coefficient.
8. **Nothing shipped moves until a law closes** (W39 clause 9): in G0–G1 no byte under
   `scenes.json`, `fixtures/`, the frozen matrix, `results/generations/`, the six material
   documents, the goldens or any adopted threshold; the freeze reads 1,818 at every merge.
9. **If a leaf lands, the acceptance is W38's shape and W39 clause 10's chain**, staged through
   W40's publisher: each leaf through the identity table as an identity gate-group, WebGPU tier;
   the CSS derivation measured in a browser, carried, approximated with its residual, or declined
   (Decision Log 4); W38's per-channel-bin veto FIRST against the shipped treatment on the W39
   calibration archive, where the shipped treatment is **the pre-W41 rendered complete exterior
   composite** captured in Chromium on the W39 web-plannable cells before any leaf exists (the
   active shadow included), never a zero baseline;
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
11. **The renderer that would ship is verified before the single exposure, and the exposure
    scores it too.** In G1, each surviving numerical candidate is implemented as an
    identity-gated operator in the worktree's renderer (a zero-strength gate-group appended to
    the identity table; no document resealed; nothing shipped moves), rendered in Chromium on the
    W39 web-plannable calibration and validation cells through `wave.py plan`, and read against
    Apple's pixels with the same instrument; the rendered candidate must meet the same survival
    bound there. The receipt then binds the renderer's source revision, its configuration and its
    frozen rendered predictions beside the numerical candidate's, and the ONE exposure's runner
    scores both on the held-out cells: the numerical candidate on all of them, the rendered one on
    the web-plannable ones. **The rendered held-out predictions are produced BEFORE the exposure**,
    blind, from the public declaration alone (the scene's declared backdrop and geometry through a
    committed generated-backdrop bundle, never a native fixture or archive payload), and frozen by
    hash; inside the receipt the runner recaptures them and requires byte/projection equality
    before any native held-out pixel is scored, so the web render is deterministic and the
    prediction preceded the evidence. "Inside the receipt" governs every read of Apple's held-out
    pixels, not the blind web render. A law CLOSES only if both meet the bound. Any later change that moves a rendered prediction stops the landing rather
    than inheriting the closure; a candidate whose operator fails is removed from the code before
    G1's merge, with its diff and renders kept as evidence.

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
- **Discriminators, honestly**: the review's re-computation on the memo's rows gives S1's
  minimax predictions only 1.15 (light inactive) and 2.03 (dark inactive) codes from S0's on the
  121–135 sweep — BELOW the three-code resolution rule — so S0 versus S1 may well read
  "insufficient resolution" on this bed, and the charter says so before any fit; S1 vs S2 rests
  on the active reflected-row difference (3 codes at 14.5 CSS px, both scales), which S1 cannot
  produce. **No held-out cell referees any spatial family** (clause 2): the spatial result is a
  bounded calibration finding, reported with the null's and each family's residuals, and no
  spatial leaf lands in W41 (Decision Log 6). The strip's mask (central 48 CSS px, rows ≥ 6 CSS px
  inward, arcs excluded), its reference-level domain and its row aggregation are pinned in G0.

### The stroke families (MARKED)

Outside the supplied path, on **every required exterior bin of the inherited reader** — shells 0
through +4·scale − 1 at both scales, population ≥ 4, arcs and straights separate — so that the
occupied 1x shell-1 arc bins (13.4 light / 26.8 dark codes at n = 9 on grey-255 inactive, §5.186
§8) are forward tests and the measured zero-stroke shells beyond the band constrain the support at
both scales; support failures are reported separately from material and angular fits; on the
44/64 calibration ladder, grey-128, grey-255, the gradients whose arcs sweep the local level
86–170, and the 51 calibration colours' centre cells:

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
- **Required tests**: one code on every required exterior bin (shells 0…+4·scale − 1) with
  population ≥ 4, per channel, with the three closure statuses of clause 5; the interior shells
  −1…−3 as witnesses that the stroke adds nothing inside; the straddling rows as a diagnostic of
  the raster edge, never a closure bin; the shadow-only control bins of clause 7 in the active
  pose; per scale, shape and pose, never pooled.

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

### G1: Identification, the scratch leaves, the rendered check, the single exposure (ledger §5.192)

Branch `w41-g1-identification`. In order: **the veto baseline** (the pre-W41 renderer captured in
Chromium on the W39 web-plannable calibration and validation cells, the complete exterior
composite included, frozen by artifact) → the uniform body (B1–B3 against B0) → the spatial
families on the surviving body (a finding; no leaf) → the stroke, receded then active beneath
the held shadow. Survival per W39 clause 8 on the numerical candidates → **each survivor
implemented as an identity-gated operator in the worktree's renderer** (clause 11), rendered on
the same web-plannable cells, read with the same instrument, W38's per-bin veto against the
frozen baseline, and held to the same survival bound → the freeze by artifact of both the
numerical and the rendered predictions for every held-out cell → **the ONE exposure**, whose
runner scores the numerical candidates on every held-out cell and the rendered candidates on the
web-plannable ones, capturing their web side inside the receipt → the resolution rule → the CSS
reach per survivor, measured in Chromium where a CSS derivation exists and by algebraic
projection where it does not (memo readings: E3 mirrors exactly on uniform backdrops where the
saturate does not clip, light green clips by 37.7 / 26.3 codes; a fixed-RGBA stroke has a
≥ 5.4–7.7-code minimax on the neutral straights). A failed operator is removed from the code
before merge; its diff and renders stay as evidence. Ends in Decision Log 2.

### G2 (conditional on Decision Log 2 finding a law): the seal and the landing (ledger §5.193; §5.194 if split)

The leaves are already in the code at their closed values behind their gates (clause 11): the
body operator before author tint; the stroke in the optics pass before the outside early return,
with the field/scissor reach checked; no spatial leaf (Decision Log 6). G2 sets the gates in the
four documents and reseals them; goldens attributed; E2's 212-row regression against the
pre-W41 capture; R1; M1/M2/C1/X1/L1 re-read; the CSS derivation carried, approximated or
declined on its Chromium measurement (Decision Log 4); the canonical holdout once by artifact;
the staged publication once (W40 G1); the capture tree copied and the superseded one moved;
the eye sheets over the canonical bed and the W39 cells; the demo and README; the changeset; the
release checklist with CI green; `pnpm release` is the user's hand; tag after. **No rendered
prediction moves between G1's freeze and G2's seal**; if one must, the landing stops and the
law returns to a new identification with a new archive.

## Cross-Child Contracts

W39's **X21–X25** carry (the box and censor rule as amended by clause 5; prediction before
opening; the archive complete and cited; one canvas, attested positions). W34's **X1–X14**
carry where they concern the archive, the split and the ledger; **X5 is not invoked** (no native
capture). W37's **X15–X17** and W38's **X18** carry. X9's routing carries the 2026-09-26 note
(workers on `opus` or `astra` medium/high; reviews through the review-code agents,
`reviewer-high` at gate merges). New:

- **X26 — one exposure for the wave, scoring the renderer too.** The W39 holdout opens at most
  once, for W41, on one receipt binding every W41 candidate — numerical AND rendered (the
  renderer's source revision, configuration and frozen predictions) — whose runner captures the
  web-plannable held-out cells' web side inside the receipt; a failed exposure spends it; nothing
  changes after it; a rendered prediction that moves afterwards stops the landing.
- **X27 — the stroke is receded-first and composited outside only.** Identified with γ = 0 and
  no shadow; tested active beneath the predicted, held shadow; the interior shells witness that
  it adds nothing inside; no double paint at landing.
- **X28 — locality is measured.** The tone solve's group argument is kept, blended or replaced
  on the gradient reading; the blend/blur ambiguity and the boundary-tail alternative are
  recorded beside the choice.
- **X29 — censoring is one-sided and the bridges stay.** Clause 5; both populations reported.
- **X30 — the gauge is a convention.** Max-normal coverage normalisation; no coefficient is
  reported as physical opacity or width.
- **X31 — three closure statuses.** `measured`, `censored-bound-satisfied`, `UNMEASURED`, kept
  apart in every table. Aggregation: a candidate SURVIVES when every required channel/bin is
  `measured` within max(1 code, bar) or `censored-bound-satisfied` (its prediction reaches the
  rail); a `measured` miss or a rail violation is binding; a population-deficient bin is
  `UNMEASURED`, excluded from the test and counted in the report. A bound-satisfied channel is a
  constraint met, never accuracy evidence: it is reported beside the measured maxima, not folded
  into them. At closure, a censored held-out cell is `UNMEASURED` (X21) and counts toward neither
  pass nor coverage; closure requires every `measured` held-out cell to pass and reports the
  measured coverage as a fraction of the held-out set.
- **X32 — the veto baseline is the rendered composite.** W38's per-bin veto runs against the
  pre-W41 renderer's complete exterior and interior as captured in Chromium, frozen before any
  leaf; shadow-only control bins stay in every active-pose table.

## Ordering & Dependency Map

Decision Log 1 → G0 (declaration, instrument; review) → G1 (baseline capture → body → spatial
finding → stroke → scratch leaves rendered and vetoed → freeze of both → one exposure → Decision
Log 2) → G2 (seal, reads, landing) → release → close. No W40-style housekeeping is
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
- **The W39 holdout is one exposure for everything**: the freeze is complete for every survivor,
  numerical and rendered, before the receipt; a survivor found later waits for a new archive.
- **The spatial families have no held-out referee and a sub-resolution null**: reported as a
  finding with the resolution rule applied; no leaf; the structured-backdrop bed is Deferred.
- **The held shadow model is not Apple's shadow**: the shadow-only control bins bound its error
  and the active stroke's identification is stated as conditional on it.

## Deferred / Out of Scope

- A dense hue sweep and C above 0.024; inputs below 40 and above 150; the black branch below
  encoded 0.003 (W36's, untouched).
- A textured, frequency or chromatic-gradient control that separates the group/local blend
  from the blur; a window-relative versus path-local lighting frame (needs an oriented path).
- A phase mechanism on a different actuator (W39 Decision Log 3).
- Span 160, the accessibility beds, author tint over coloured backdrops, dynamics and stacking.
- Black and near-black intrinsic stroke colour; the stroke under Increase Contrast.
- **The spatial body leaf** (a group/local blend and an active directional term at the tone
  solve's argument): needs a bed whose holdout carries structured backdrops and whose
  calibration varies the group mean and the backdrop frequency, with the strip pinned before
  capture.

## Tracking Map

| child | status |
| --- | --- |
| G0 | MERGED 2026-09-27 as `cd55870d` (§5.191): declaration 850747c1… (superseded 99e460d5… kept); execution parameters body a3947184… / stroke df9f807e…; twin audit (B1/B3 bridge-only; S0/S1 below resolution); synthetic proofs (E3/EH6 4.3e-14 / 4.0e-13; certified LP 100/100 noisy; O12 local; band integrator; width-aware stroke search; strip reader; shadow vs WGSL on Metal 2.8e-5 code over 3,240 cases); exposure runner 41 tests; sheets 1,003 canonical MATCH, 330 rendered; two instrument P2s fixed in bounded waves with clean re-reviews. Review: reviewer-high, no material findings; 114 synthetic tests, the 100 noisy LP cases, the width recoveries, 3,600 shadow cases, the guarded replay and all 41 exposure tests rerun; every pin matches; no protected file changed |
| G1 | — |
| G2 | conditional |

## Decision Log

### Decision Log 1 — identification only, or landing in this wave (before G0; the user's)

The parent recommends landing in this wave: a survivor at one code on calibration, validation
and the held-out cells is exactly the shipping criterion, and G2's chain is W38/W39's as
written. Identification-only would end at Decision Log 2 with the leaves chartered separately.

**Ruled 2026-09-27 (the user): land in this wave.** If a law survives calibration, validation and
the held-out cells at one code, G2 ships it through the identity table, the CSS carry-or-decline,
the canonical holdout once, the eye sheets and a release.

### Decision Log 2 — a law or the negative, per question (after G1; the user's)

### Decision Log 3 — bounds and floors if a leaf lands (in G2; the user's)

### Decision Log 4 — the CSS tier's carry, approximation or decline, per leaf (in G2; the parent's, on the browser measurement)

### Decision Log 5 — the censor rule and the bridges (in G0, by rule; the parent's)

Ruled at charter: clause 5 / X29 / X31. Recorded here so that W39 G2's population and W41's
are never confused in the ledger.

### Decision Log 6 — the spatial families are a finding, not a leaf, in W41 (at v2, by rule; the parent's)

Ruled at v2 on the review's P1: the W39 holdout has no non-uniform backdrop, so no held-out
cell can referee a group/local blend or a directional interior term, and the null-versus-blend
separation on the calibration strip is below the three-code resolution rule. S0–S2 are
identified and reported on calibration with their residuals and the resolution verdict; the
edge conditioner in this wave stays the measured deep median (W39 Decision Log 8); the leaf is
Deferred.

## Surprises & Discoveries

- **H3's dark miss was the bridges' extrapolation, not hue dependence** (memo A): 20.1 / 17.5
  codes with them, 2.9 / 3.1 without, and the native chroma direction stays radial within 3°.
- **The stroke is one device pixel, not one CSS pixel** (memo B): identical shell-0 departures
  at 1x and 2x on aligned straights.
- **The body's slope on a gradient depends on the gradient's direction when active** (memo A):
  0.715 against 0.147 (light), 3 codes at 14.5 CSS px inward between reflected rows.

## Revision Notes

- 2026-09-27 (v2.4, the parent, on G1's stop): the declaration fixes G1's order with the pre-W41
  rendered baseline first, and X6 refused the capture (the user's Chrome and another session's
  Playwright browsers on the machine). Ruled: the numerical steps (uniform body, spatial finding,
  stroke receded then active) may run before the baseline capture, because they read Apple's pixels
  and the baseline reads vitrea's, so its timing cannot influence them; the baseline MUST be captured
  and frozen before any candidate operator is rendered (steps 5–6), which is what the order protects.
  The worker records this as an ordering amendment in the declaration with the superseded hash
  850747c1… kept beside the new one and no other byte changed, and the README and §5.192 say why.
- 2026-09-27 (G0's merge, the parent): merged `cd55870d` after an independent gate review (reviewer-high, no material findings; 114 synthetic tests, the 100 noisy LP cases, the width recoveries, 3,600 shadow cases, the guarded replay and all 41 exposure tests rerun; every pin matches; no protected file changed);
  freeze 1,818; no capture tree moved; nothing fitted to native pixels. G0's stops produced v2.1–v2.3;
  its instrument reviews produced two P2 fix waves (exact-support recovery; width-aware stroke search),
  each re-reviewed clean. X9: G0 ran on an `astra` high worker with its own sub-workers for the body
  instrument, the exposure runner and the sheets, and `reviewer-high` on each. Worktree removed.

- 2026-09-27 (v2.3, the parent, on the exposure runner's question): clause 11's "capturing their
  web side inside the receipt" could be read as forbidding a blind pre-exposure web render of the
  held-out cells, which the same clause's freeze requires. Ruled: rendered held-out predictions are
  produced blind from the public declaration before the exposure and frozen; the receipt recaptures
  and requires equality before scoring; "inside the receipt" governs reads of Apple's pixels only.
- 2026-09-27 (v2.2, the parent, on G0's question): X31's "only `measured` counts toward
  survival" could be read as forbidding any survivor with a censored required channel, which
  would kill every light body candidate on the red bridge's R and every stroke on a white exterior
  bin. Amended to the intended aggregation: bound-satisfied channels are constraints met that
  permit survival and never accuracy evidence; censored held-out cells are UNMEASURED at closure.
- 2026-09-27 (v2.1, the parent, on G0's stop): clause 7 had named "the top straight when active"
  a shadow-only control; that is true of the dark scheme only (memo B: dark active top 0, light
  active top −20 against a held shadow of −0.0001). Amended: the controls are the exterior bins
  beyond the band at both scales, plus the dark-active top straight as a stratum-specific observed
  zero; light active's top is a stroke bin. Recorded before any declaration was hashed.
- 2026-09-27 (G0 dispatch, the parent): the second adversarial round on the re-cut returned no
  material findings and approved the charter for G0, noting that the exposure runner G0 builds
  needs its own independent review. G0 dispatched on an `astra` high worker (X9).
- 2026-09-27 (v2, the parent): one adversarial round folded — P1 the spatial families had no
  held-out referee and an overstated discriminator (fixed: a finding, no leaf, the strip pinned,
  Decision Log 6); P1 the stroke's required set dropped the occupied 1x shell-1 arcs and the
  zero-stroke outer shells (fixed: the inherited reader's full exterior range at both scales);
  P1 the single exposure preceded the renderer that would ship (fixed: clause 11 — scratch
  identity-gated operators rendered and vetoed on calibration/validation before the exposure,
  the receipt binding their predictions, the runner scoring both; G1/G2 re-cut); P2 one-sided
  rail satisfaction could read as closure (fixed: three statuses, X31); P2 the stroke veto named
  a zero exterior baseline (fixed: the pre-W41 rendered composite, X32, shadow-only control
  bins). Second adversarial round requested on the re-cut.
- 2026-09-27 (v1, the parent): chartered from grounding memos A (body) and B (stroke) on the
  W39 calibration cells; Decision Log 1 put to the user; adversarial review requested.
