# W19 — the author-tint fold on the CSS tier's linear path (2026-09-05)

**Status: OPEN — chartered 2026-09-05 on the user's decision after W18 ("charter the author-tint
fold as W19 now and cut 0.8.0 after it lands"); G0 opens on Decision Log 1's recommendations.**

Composite spec: design at the top; Decision Log, Surprises, Deferred and Revision Notes at the
tail. Parent: `2026-08-28-post-v1-wave.md` (the W19 row). Predecessors: W17
(`2026-09-04-w17-css-interior-level.md`, claims §5.74–§5.76 — the linear path this wave corrects)
and W18 (`2026-09-05-w18-union-contour-residual.md`, claims §5.77–§5.79 — whose post-landing
review found the defect; §5.79 §7 addendum). The tint pathway's own charter is W10
(`2026-09-02-w10-tint-pathway.md`, claims §5.36) and the strength axis's capture plan W3.

## Purpose

On Chromium's linear path (W17 G1, Decision Log 2 (c)) the CSS tier carries the material's lerp
inside the sharp layer's linear-light filter as a per-channel table and paints L3 at the
contrast floor; the table is solved so that the floor overlay composites back to the material
exactly. An author tint is the one thing still laid on L3 (W10), and it is laid as the author's
own layer at the author's own strength — while the table beneath it is still the one solved for
the floor overlay, and solved for the FOLDED tint colour at that (`root.ts` passes
`tintedCssOptics`' output as `optics`). The two compose to the intended expression
`(1 − s)·E(M) + s·E(L)` only at full strength, where the author layer covers the table's output
entirely. Below it the composite misses the material by `(1 − s)·α₃/(1 − α₃)` of the gap
between the material composite and the table's floor colour — read by review at −0.053…−0.014
of linear luminance for strength 0.2 and −0.002…+0.025 for 0.5 across backdrops 0.15–0.6 — and
below strength 0.2668 the element paint L3 carries is under the floor W17 Decision Log 4 (a)
requires. The bed's tint registry carries strengths 1.0 and 0.5 only, which is why no wave saw
it; W17 Decision Log 2 (c) named this re-derivation as owed if S5 fired on a tinted cell, and it
did (`hc-text__capsule-button__rest-tint-orange`, +0.0129 / +0.0118).

*Corrected by G0 (claims §5.80 §2; Decision Log 2), left as written above:* the mechanism has a
fourth term, and it is the largest. The transfer table clamps into [0, 1]; solved against the
FOLDED colour it saturates on the seed's darkest channel over most of the ladder (47 of 180
analytic channel cells, up to −0.083 encoded; 0.1–14.2 % of masked channel samples on captured
cells), a hue error that fires before L2's Gaussian and breaks the affine premise W17 G1's
derivation rests on. The fold removes it (clamp share 0.000 on every captured cell). Measured on
pixels the error is not one-signed: −0.068 at strength 0.1 and −0.041 at 0.2 over the photo at 1x,
+0.015…+0.016 on the blue seed at 0.5, zero near the bed's one sub-unit cell.

This wave measures the composite at every strength on both tiers, derives the exact fold from
the profile with no fitted constant — the author layer folded over the floor overlay in encoded
space so that L3's alpha never drops below α₃ and the identity holds at every strength — lands it
on the renderer's composite, and records Apple's own strength law at 1x for the renderer's ledger.
The 0.8.0 cut follows the landing (the user's).

## Parent-Level Acceptance

- **The composite is measured and attributed.** On the tinted capsule over the photo and the
  checkerboard at both light-standard scales, at strengths 0.1, 0.2, 0.35, 0.5, 0.75 and 1.0
  (the bed's two strengths among them, as controls): the tier's composite against the intended
  expression `(1 − s)·E(M) + s·E(L)` and against the renderer's rendered interior, per cell; the
  error's closed form from the code (`cssTierTintTable`, `authorTintLayer`, `tintedCssOptics`)
  reproducing the measured error within 0.002 per cell; the floor drop (L3's alpha under α₃ for
  s < 0.2668) named with its cells; the instrument's recovery of a known offset (X4) beside
  every reading.
- **The tier lands on the renderer's composite at every strength.** CSS − GPU interior mean
  within 0.005 on every ladder cell at both scales under the standard light profile; within
  W17's 0.01 on the tinted cells of the fold profiles at the strengths the ladder reads there;
  the level ratio inside 0.97–1.03; the bed's own tinted cells (twelve scenes) within 0.005 or
  unmoved where they already are.
- **The floor holds at every strength.** L3's painted alpha ≥ α₃ on every tinted surface on the
  linear form — a unit pin over the ladder, and the contrast-floor e2e (`css-tier-pixels.spec.ts`,
  "stays legible with the blur removed") extended to a tinted panel at strength 0.1.
- **Nothing else moves.** Every untinted CSS-tier capture byte-identical to the W18 bed (the
  change touches only surfaces with an author layer); the full-strength tinted cells
  byte-identical or within 0.0005 (at s = 1 the fold is the opaque layer the tier draws today);
  no dom row below its adopted bound or its floor, the seven held rows at or above their W18
  pins; `PREDICATE_EXCLUDES` does not grow.
- **The GPU tier does not move:** every capture byte-identical to the W18 bed. The renderer's
  strength law (`tintedMaterialColour`) is read, never edited; if the native ladder disagrees
  with it, that is the renderer's item, named.
- **The native ladder exists and is attested** (q1): `apps/reference-apple/scenes-w19-probe.json`
  through `VITREA_SCENES` into its own fixtures dir under
  `packages/calibration/results/2026-09-05-w19-author-tint-fold/probe/`, 1x, by W9's rule (claims
  §5.30: attested runs, the majority byte-state per cell, the shares recorded), the recorded
  twins (`orange`, `orange-half`) byte-identical to the canonical fixtures as the control; Apple's
  interior mean per strength recorded in claims beside the renderer's law and the tier's, and
  fitted to nothing.
- **The encoded form is unchanged.** The dark scheme's tinted cells and any cell the boundary
  puts on the encoded form draw `tintedCssOptics`' fold as today, byte-identical; the form each
  tinted ladder cell drew recorded (`cssShadow`'s neighbour, `cssTint`, on the group state).
- **The cost:** no primitive or layer added; the knee where W16 left it.
- **Chromium is measured;** the plain-`blur()` engines keep `tintedCssOptics`' fold behind the
  conformance rows, unchanged.
- **By eye:** X5 sheets at the dry run and the landing — the ladder rows with native where
  captured, the W18 bed, the candidate, the GPU tier and the signed difference; the reading
  recorded; the landing the user's.
- All suites green, lint clean; the canonical matrix rebuilt once at recomposition; the holdout
  read once per frozen configuration (the tinted holdout cells: `hc-text__capsule-button__rest-
  tint-orange` at both scales, `dark-solid__capsule-button__rest-tint-blue` at both scales,
  `photo__rrect-lg__rest-tint-orange` at both scales); every gap in claims, this Deferred list or
  the tracker.

## Grounding Baseline (the W18 bed, 2026-09-05, `3d8e769`)

**The code.** `packages/platform-web/src/css-tier.ts` (`cssTierDeclarations`, the block "Which
form draws, and what each half of it carries"): `transfer = cssTierTintTransfer(interior,
floorAlpha, optics.tint / 255)` with `floorAlpha = cssTierFloorAlpha(optics)` = 0.2668, and
`overlayTint = authorLayer === undefined ? rgba(optics.tint, floorAlpha) : rgba(authorLayer.color,
authorLayer.strength)`. `packages/platform-web/src/optics.ts`: `cssTierTintTable` (the table
`F(b) = D((E(M) − E(T)·α₃)/(1 − α₃))`), `authorTintLayer` (the seed at its shade, the author's
strength), `tintedCssOptics` (the encoded-space fold `α″ = 1 − (1 − s)(1 − α′)`,
`C″ = ((1 − s)·α′·C′ + s·E(L))/α″`, W10). `packages/platform-web/src/root.ts` (~1907–1932):
`authorLayer = authorTintLayer(policySource, seed, …)` and `nodeBaseOptics =
tintedCssOptics(cssOpticsFromSource(...), policySource, seed, …)` — the FOLDED optics are what
`cssTierDeclarations` receives as `optics`, so on a tinted surface the table's floor colour is the
folded colour, not the material's own. The renderer: `packages/renderer-webgpu/src/material.ts`
`tintedMaterialColour` — `decode(mix(encode(material), encode(layer), s))` per pixel, the author
layer opaque at the author's opacity in encoded space (claims §5.36 finding 3), mirrored per pixel
in `wgsl/optics.ts`.

**The bed's tinted cells** (twelve scenes; CSS − GPU interior mean, canonical `matrix.json`):

| cell | 1x | 2x | note |
| --- | --- | --- | --- |
| `photo__capsule-button__rest-tint-orange-half` | −0.0008 | −0.0003 | the ONE sub-unit strength on the bed; both tiers +0.020 over native (0.4587 against 0.4385 / 0.4391) |
| `hc-text__capsule-button__rest-tint-orange` (holdout) | +0.0128 | +0.0117 | standing since W17 (§5.75 §4) |
| `photo__rrect-lg__rest-tint-orange` (holdout) | −0.0028 | −0.0032 | |
| `photo__rrect-md__rest-tint-orange` (validation) | −0.0023 | −0.0031 | |
| `checkerboard__capsule-button__rest-tint-orange` | −0.0016 | −0.0031 | |
| the other seven light cells | −0.0017…+0.0000 | −0.0025…+0.0000 | |
| the three dark-scheme cells, both scales | −0.0012…−0.0007 | −0.0011…−0.0003 | the encoded form |
| the fold profiles (`tint-orange` capsule) | +0.0056 / +0.0055 (IC, two backdrops), +0.0002 (RT) | — | |

Every full-strength cell is insensitive to the defect by construction (the opaque layer covers
the table's output), so the bed's agreement on eleven of twelve scenes says nothing about
strengths below one. The `orange-half` cells' small reading is the review's formula at the
photo capsule's backdrop, where `E(M)` happens to sit near the folded colour; G0 measures whether
that is so.

*Corrected by G0 (claims §5.80 §6), left as written above:* the "+0.020 over native at 0.5 on both
tiers" is not a reading of the strength law. Apple's curve is the encoded-space mix of Apple's own
endpoints to 0.003 on ten rungs, the renderer's law exactly; the sub-unit `GPU − native` gap is the
thin-span material level (+0.035 photo, +0.055 checkerboard; §5.55 §3) faded in by `(1 − s)`, plus
+0.007…+0.012 that survives at full strength — the tint shade's own gap, the renderer's. The
`orange-half` cell's small reading is the error's zero crossing at that backdrop, measured.

**The review's readings** (claims §5.79 §7 addendum; the scratch test at
`~/.claude/jobs/5c70e47f/tmp/w18/findings/zz-w18-verify.test.ts`, not committed): the composite
error in linear luminance, orange seed, `interior.tintAlpha` 0.62 — strength 0.2: −0.053 / −0.041
/ −0.014 at backdrops 0.15 / 0.3 / 0.6; strength 0.5: −0.002 / +0.007 / +0.025; strength 0.8:
+0.005 / +0.009 / +0.015; the untinted control 0.00004. These are the review's, to be measured by
G0 with X4 beside them.

## Design (advisory unless marked)

- **The mechanism (binding, from the code).** Three things compound on a tinted surface on the
  linear form: (i) the table is solved for the floor overlay `(T_folded, α₃)` where `T_folded` is
  `tintedCssOptics`' fold rather than the untinted conversion's `T`; (ii) L3 paints `(L, s)` in
  place of the overlay the table was solved for, so the composite is `(1 − s)·F(b) + s·E(L)`
  where the target is `(1 − s)·E(M) + s·E(L)`; (iii) for `s < α₃` the element paint is under the
  doctrine's floor. At `s = 1` all three vanish.
- **The exact fold (advisory).** Keep the table as W17 solved it, on the UNTINTED conversion's
  `(T, α₃)` — so `(1 − α₃)·F(b) + α₃·E(T) = E(M)` — and paint on L3 the encoded-space fold of the
  author layer `(L, s)` over that floor overlay: `α″ = 1 − (1 − s)(1 − α₃)`,
  `C″ = ((1 − s)·α₃·E(T) + s·E(L))/α″`. Then `(1 − α″)·F + α″·C″ = (1 − s)(1 − α₃)·F +
  (1 − s)·α₃·E(T) + s·E(L) = (1 − s)·E(M) + s·E(L)`, the renderer's expression, at every `s`;
  `α″ ≥ α₃` always, so the floor holds; at `s = 1` it is the opaque layer drawn today, at `s = 0`
  the floor overlay. `tintedCssOptics` already computes this fold — with `css = {tint: T,
  tintAlpha: α₃}` as its input it IS this fold — so the derivation adds no algebra, only the
  right inputs: `root.ts` passes the untinted conversion's optics to the declarations on the
  linear form and the tier folds the author layer over the floor itself, or the tier receives
  both and does the same. The closed form is verified to 1e-6 at every `s` and `b` before a
  pixel is captured (G0 (d)).
- **What stays where it is (binding).** The encoded form and the plain-`blur()` engines keep
  `tintedCssOptics`' fold over the material's whole `rgba()` — that path was never wrong. The
  renderer's `tintedMaterialColour` is read, never edited (X3). The floor constant stays the named
  0.2668 (W17 Decision Log 4 (a); the review's finding 3 is a tracker line).
- **The boundary at low strength (advisory).** `cssTintFormAt` reads the composite level of the
  MATERIAL; an author layer at low strength barely moves it, so no ladder cell should flip form
  — G0 records the form each cell drew and G1's stops name any flip.
- **The strength law against Apple (data-only).** Both tiers read the bed's half-strength cell
  +0.020 over native. The native ladder records Apple's interior mean per strength; if the
  encoded-space mix does not fit it, the renderer's law is the item and it goes to Deferred with
  the readings — this wave does not move the renderer.
- **The rim band on square boxes** (claims §5.79 §7 addendum; q4) is out of this wave's scope on
  the recommendation and keeps its Deferred shape in W18.

## Children

### G0: The strength ladder measured, and the exact form verified — spike

- **Purpose:** (a) the closed form of today's composite error from the code, per strength,
  backdrop and seed, on the shipped light profile — the review's scratch test made an
  instrument; (b) the web-side ladder captured on both tiers to scratch (a scratch scenes file
  adding `orange-010`, `orange-020`, `orange-035`, `orange-075` and `blue-020`, `blue-050` on the
  capsule over the photo and the checkerboard, both light-standard scales; the fold profiles at
  0.2 and 0.5 on the photo), the interior mean CSS − GPU per cell under the declared region with
  X4, the form each cell drew from `report__css.json`; (c) the native ladder at 1x by W9's rule
  behind the TCC gate, the recorded twins as controls; (d) the exact fold's identity verified
  in the closed form at every `s` and `b` to 1e-6, the floor condition shown, the boundary
  checked; (e) `[parent-impact]` items.
- **Stops:** none — a spike reports. Its reader validated by X4 before any reading is used.
- **Edges:** none. **Track:** spike. One worker; the native probe rides inside it (as W18).

### G1: The fold declared and dry-run — controlled

- **Purpose:** the exact fold implemented where G0 places it (`root.ts`'s inputs, or the tier
  folding over the floor itself), the unit pins (the identity over the ladder; L3's alpha ≥ α₃;
  the full-strength layer byte-identical to today's declaration), the e2e floor test at strength
  0.1, contract X7's coherence pin, a pre-check on G0's ladder bed (scratch), then the whole bed
  dry-run on the frozen configuration with the holdout read once (X8), the sheets.
- **Stops:** S1 the GPU tier byte-identical; S2 no dom row below its bound or floor, the seven
  held rows at or above their W18 pins; S3 every untinted CSS capture byte-identical and every
  full-strength tinted cell within 0.0005; S4 CSS − GPU within 0.005 on every ladder cell at both
  scales (standard light) and within 0.01 on the fold profiles' ladder cells; S5 every ladder cell
  moves by its own derived share within 0.002 (the closed form of (a)); S6 the cross-tier ΔE down
  or flat on every profile, the level ratio inside 0.97–1.03; S7 `PREDICATE_EXCLUDES` does not
  grow; S8 the knee unmoved; S9 by eye, the sheets. A stop that fires stops the child for the
  parent.
- **Edges:** blocked-by G0. **Track:** controlled. One worker.

### G2: The landing and its referee — controlled

- **Purpose:** merge; the canonical rebuild once; the floors re-recorded (none may go down
  without a decision); `PREDICATE_EXCLUDES` as the machine's output; the sheets; recomposition;
  then the 0.8.0 cut (the changesets pending: `css-shadow-carriers.md` and this wave's; the user
  publishes, the parent tags).
- **Stops:** G1's, re-read on the canonical bed, plus the referee running the landing's test file
  against the dry-run matrix before the merge (X6).
- **Edges:** blocked-by G1. **Track:** controlled. The parent.

## Cross-Child Contracts

- **X1 — the canonical rebuild.** Once, from the main checkout, at G2. Owner: parent.
- **X2 — floor bookkeeping.** Floors ratchet up where rows rise; a floor that would go down stops
  the landing for the user. Owner: parent.
- **X3 — the untouched tier.** Byte identity on the GPU tier, every profile; `tintedMaterialColour`
  and the shader's mirror read, never edited. Owner: parent.
- **X4 — the instrument's validation travels with every reading.** The interior-mean reader
  recovers a synthetic offset (+0.03 in linear light lerped into a capture) under every mask it
  uses before it reads a ladder cell (W18 G0's `x4-recovery.ts`, re-run on this wave's reader).
  Owner: G0; G1 binds.
- **X5 — the by-eye sheets.** W18's script with its rows re-aimed: the ladder at 1x and 2x, dry
  run and landing, native where captured. Owner: parent.
- **X6 — the dry-run referee runs the landing's gates.** `adopted-thresholds.test.ts` against the
  scratch matrix through `VITREA_MATRIX_PATH`. Owner: parent.
- **X7 — the coherence pin.** `tier-coherence.test.ts` asserts the tier's tinted composite equals
  `tintedMaterialColour`'s expression at every strength of the ladder and every backdrop level
  the bed samples, to the chain's quantum. Owner: G1.
- **X8 — the holdout, read once** per frozen configuration. Owner: G1; parent verifies.
- **X9 — the engines.** The fold's exactness is gated on the reference filter's conformance row;
  the plain-`blur()` engines keep `tintedCssOptics`' fold. Owner: G1.
- **X10 — the probe bed's custody.** `scenes-w19-probe.json` and
  `results/2026-09-05-w19-author-tint-fold/probe/` (fixtures, `last-run-manifest.json`,
  `provenance.json` by W9's rule); read by the study, fitted by nothing; the canonical layout
  untouched. Owner: G0; parent verifies.
- **X11 — the renderer's numbers travel unchanged.** The profile's tint shade constants and the
  strength law are read, never edited, by every child. Owner: parent.

## Ordering & Dependency Map

G0 → G1 → G2 → recomposition → the 0.8.0 cut. Inside G0 the closed form and the web-side ladder
run first (no native fixture needed for a cross-tier reading) and the native ladder second, behind
its TCC gate; the two halves are independent and the web side does not wait on the grant.

## Risks & Mitigations

- **The grant has lapsed again** — the native ladder waits on the user's hand, as W18's did; the
  web side proceeds; the acceptance clause for the probe is met when the pixels are taken.
- **A tinted cell's structure pays** — the fold changes L3's colour and alpha on every tinted
  surface below full strength; the bed's `orange-half` cells carry no floor, so a drop below a
  bound is a stop (S2) and the user's decision (q5).
- **A form flip at low strength** — named by G0 (d) before G1; a flipped cell draws the encoded
  fold, which is exact too, and the stop is whether the level clause holds.
- **The renderer's law is not Apple's at sub-unit strength** — the bed already reads +0.020 at
  0.5 on both tiers; the ladder makes it a curve; it is the renderer's item (X3) and goes to
  Deferred with the readings.
- **The GPU is shared** — one capture process at a time; every run detached and awaited.

## Deferred / Out of Scope

- **The renderer's strength law against Apple's** — both tiers +0.020 over native at strength
  0.5 on the photo capsule (the bed); the native ladder makes it a curve. The renderer's item.
  *Rewritten by G0 (claims §5.80 §6), the line above left as written:* the strength law IS Apple's
  shape (the encoded-space mix within 0.003 on ten rungs; linear light refuted by +0.009…+0.033),
  and the sub-unit gap is the thin-span level faded by `(1 − s)`, already the renderer's ledger.
  What is new is **the tint shade's own gap at full strength**: +0.007 (photo) / +0.012
  (checkerboard) of luminance where the material is the tint and the level gap should have
  vanished, its hue half not taken. The renderer's item, for its charter, with the ladder's
  twelve native cells as its bed.
- **The clamp's cost as a colour (G0).** §5.80 §2 reports the saturation per channel and its
  share per cell; no ΔE was taken on the ladder. The hue error is what a reader would see and what
  an interior mean under-reports; G1's dry run reads ΔE on the ladder cells against the GPU tier.
- **The blue seed on the ladder (G0)** — captured at 0.2, 0.5 and 1.0 only, and natively not at
  all; the second hue is the cheap next probe if the shape is doubted.
- **The fold profiles' tinted composite under a policy fold (G0)** — measured (§5.80 §4), not
  attributed: `predict.ts` resolves under the nominal policy.
- **The bed's strength axis (Decision Log 3 (6)).** Two rungs at 1x (orange 0.2 and 0.75 over
  the photo and the checkerboard) from the probe's attested fixtures joining `scenes.json` as
  calibration cells, with the partition counts and the gate's tables moved beside them — a W3
  amendment, its own small child after the 0.8.0 cut, so a defect of this class cannot sit at
  the bed's one zero crossing again.
- **S5's control on a tinted surface (Decision Log 3 (2)).** The decoration constant depends on
  L3's alpha; a per-rung control (the untinted capture's decoration scaled by the L3 alpha it
  composites at) would close the three dpr-2 misses; an instrument item for the next tint wave.
- **The rim band on square boxes** (W18 Deferred; q4) — its own charter after 0.8.0 on the
  recommendation.
- **The floor literal under a runtime-patched profile** (the tracker; review finding 3).
- **The plain-`blur()` engines' tinted composite** — the encoded fold at the one-alpha anchor
  (E's gap, W17 X9), unchanged.
- **A 2x native ladder** — the user's session to open; otherwise the 2x ladder is web-side only
  and says so.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | `packages/calibration/results/2026-09-05-w19-author-tint-fold/g0/g0-findings.md` (`ebade16`, merged `1e0b2a0`), `probe/` (the 1x native ladder, twelve cells, seven attested runs), `apps/reference-apple/scenes-w19-probe.json`; claims §5.80 | CLOSED 2026-09-05 — the charter's term confirmed and a larger one found beside it (the table saturates; the fold removes it), the error not one-signed (−0.068 at strength 0.1 on the photo), the fold exact to 8.9e−8 with `α″ − α₃ ≥ +0.0733` and no form flip, Apple's curve the renderer's encoded mix to 0.003, the tier crossing Apple's curve near strength 0.3; nine `[parent-impact]` items reconciled in Decision Log 2 |
| G1 | branch `worktree-agent-a560cc39a6bdaa3ec` at `485b824` (the fold; `g1/g1-precheck.md`, `parts/`, `run-read.sh`; `test/author-tint-fold.test.ts`, `w19-pre-fold-declarations.json`; X7 in `tier-coherence.test.ts`; the tinted contrast-floor e2e; `.changeset/css-author-tint-fold.md`) | PRE-CHECK PASSED 2026-09-05 (Decision Log 3): S4 met on 36 / 36 tinted ladder cells (worst 0.0039, from −0.0684); the hue down on every sub-unit cell; the untinted captures byte-identical, the full-strength ones within 0.00013 with every differing pixel on the contour; the floor restored (least margin +0.07318); no form flip; two clauses re-declared with the reason; the dry run opens |
| G2 | — | — |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-05)

**The cut.** Three children as W17's and W18's: a spike that measures the ladder on both tiers
and verifies the exact form in the closed form, a controlled gate that declares and dry-runs it,
a controlled landing followed by the 0.8.0 cut. The native ladder rides inside the spike behind
its TCC gate, as W18's probe did: data for the renderer's ledger, on nobody's critical path.

**Bound here.** The target is the renderer's composite at every strength (W17's rule and W10's:
the two tiers agree on the strength axis by construction, and the renderer's own gap to Apple at
sub-unit strength is the renderer's item). The GPU tier does not move. The encoded form and the
other engines keep the fold they have. No constant is fitted: the fold is algebra the tier
already carries in `tintedCssOptics`, applied to the right pair.

**Put to the user, with the recommendation.**

- **q0 — the target.** (a) The renderer's composite `(1 − s)·E(M) + s·E(L)` at every strength
  (recommended: the binding rule above). (b) Apple's interior at the strengths the ladder
  captures — rejected: two tiers disagreeing by design, and the renderer untouched.
- **q1 — the native ladder.** (a) 1x, the photo and checkerboard capsule at strengths 0.1, 0.2,
  0.35, 0.5, 0.75, with the recorded `orange` and `orange-half` twins as byte-identity controls,
  seven attested runs by W9's rule, from this machine (recommended: the bed reads both tiers
  +0.020 over Apple at the one sub-unit strength it has, and the wave that fixes the tier's
  fold should leave the renderer's charter a curve rather than a point; the grant is the user's
  hand if it has lapsed). (b) No native ladder — the web side alone. (c) 1x and 2x, the user
  opening a 2x session.
- **q2 — the floor under the author layer.** (a) The doctrine's floor holds at every strength —
  the author layer folded over the floor overlay, `α″ ≥ α₃` (recommended: W17 Decision Log 4
  (a)'s condition is a doctrine, not a fit, and the fold costs nothing). (b) Let the author layer
  sit under the floor at low strength — rejected.
- **q3 — where the fold is applied.** (a) Where G0 places it after reading `root.ts`'s inputs —
  the untinted conversion's optics passed on the linear form and the tier folding the author
  layer over its own floor, or the same fold done in `root.ts` (recommended: G0's reading
  decides; the algebra is the same). (b) A new declaration path — rejected: nothing new is
  needed.
- **q4 — the rim band on square boxes, in scope?** (a) Yes, as its own controlled child with its
  own stops (bed byte-identical on the CSS tier; a radius ladder against the renderer's law).
  (b) No — its own charter after the 0.8.0 cut (recommended: one material mechanism per wave
  keeps the attribution clean and the cut sooner; the square-box gap is the bed's blind spot,
  not a shipped tint user's defect).
- **q5 — the trade if the fold costs structure on a tinted cell.** (a) Stop and put both landings
  to the user with the sheets and the rows, as W15, W17 and W18 did (recommended). (b) Accept
  structure losses inside the floors' epsilon without asking.

G0 opens on the recommendations; each answer that differs re-opens the affected child before G1.

**Executed 2026-09-05 (the user: "for decisions, all according to your recommendation").** q0
(a), q1 (a), q2 (a), q3 (a), q4 (b), q5 (a). G0 continues as dispatched; the rim band on square
boxes stays in W18's Deferred for its own charter after the 0.8.0 cut.

### Decision Log 2 — G0 read: the saturation joins the mechanism, the stops re-declared on the fold's own prediction, the Deferred entry rewritten (2026-09-05; the parent)

**What G0 found that the charter did not say** (claims §5.80): the transfer table saturates on
the seed's darkest channel when solved against the folded colour — the largest of the four terms,
a hue error, non-affine, removed entirely by the fold; the error on pixels is not one-signed and
crosses zero near the bed's one sub-unit cell; the floor is breached today at strengths 0.1 and
0.2; Apple's strength curve is the renderer's own encoded mix and the sub-unit gap to Apple is the
thin-span level faded in; the tier crosses Apple's curve near strength 0.3. The nine
`[parent-impact]` items, ruled:

1. **The Purpose and the Grounding Baseline are corrected beside** (above): the saturation is the
   fourth term; the "+0.020 over native" reading is the level curve at one point.
2. **The acceptance's closed-form clause is re-declared in two halves.** *Analytic:* today's chain
   reproduces the intended expression's difference to 1e−6 wherever the table does not saturate —
   met (8.3e−8 on 133 of 180). *On captured cells:* the prediction is the FOLD's (`predFold`, which
   does not clamp), corrected by the cell's own decoration constant read at `s = 1` on the same
   backdrop and scale, within **0.005**; the clamp share recorded beside every row and required
   0.000 under the fold. A form evaluated on a composite cannot model a clamp that fires inside a
   filter before a blur, and a clause that asks it to is asking the wrong instrument. **S5 for G1
   is this statement on the pre-check's ladder.**
3. **The eight-bit quantum is named:** `C″` rounds to `Rgb255` (2.85e−3), the same quantum today's
   `rgba(L, s)` carries; no clause on a tinted cell sits under 0.003, and the 0.005 clauses stand.
4. **S3 is re-declared by capture:** every full-strength tinted cell of the bed byte-identical to
   the W18 bed's capture, or — because the transfer's floor colour moves under an opaque layer of
   the same shape — within 0.0005 in the interior mean with the differing pixels confined to the
   contour ring, named per cell. Every UNTINTED CSS capture byte-identical, as written.
5. **The fold profiles' clause is re-declared as movement against the untinted control:** on each
   fold profile, `(CSS − GPU)_tinted − (CSS − GPU)_untinted` within **0.01** at the ladder's
   strengths; the untinted offsets (+0.0364 under increased contrast, −0.0070 under reduced
   transparency) are the fold's own gap (W18 §5.79 §7) and stay there.
6. **q2 (a) stands and is now measured:** the floor breached today on six of eighteen captured
   tinted cells; G1's pin is `α″ ≥ α₃` on every tinted surface, least margin +0.0733.
7. **X7 is stated against the tier's own `L`:** the coherence pin holds the tier's composite to
   `(1 − s)·E(M) + s·E(L_css)` at the tier's granularity; the renderer's per-pixel shade sits
   0…+0.0084 above that on the analytic sweep (W10's known granularity, not this wave's). **S4
   stays at 0.005** on every ladder cell against the GPU tier; where a checkerboard cell misses
   by no more than the granularity term measured on that cell, the parent re-declares at the
   pre-check with the number rather than before it.
8. **The Deferred entry for the renderer's strength law is rewritten beside** (above): the law is
   Apple's shape; the new item is the tint shade's own gap at full strength, the renderer's.
9. **The activation attestation's second failure mode goes to the tracker**: a run losing cells to
   `presentedActive: false` with the machine idle throughout; a probe now banks seven runs in
   about ten.

**G1 opens** on G0's placement (q3 (a), claims §5.80 §7): `root.ts` passes the untinted conversion
as `untintedOptics` beside the folded `optics`; `cssTierDeclarations`' `linear` branch takes the
transfer's floor colour from it and builds L3 from `tintedCssOptics({ ...untintedOptics,
tintAlpha: floorAlpha }, …)`; the encoded form and the plain-`blur()` engines untouched by
construction. Stops S1–S9 as the Children section wrote them, with S3, S4's checkerboard reading,
S5 and the fold profiles' clause as re-declared here.

### Decision Log 3 — the pre-check at the gate: the fold accepted, two clauses re-declared on what they were measuring, the dry run opens (2026-09-05; the parent)

**What the pre-check measured** (`g1/g1-precheck.md`; branch at `485b824`). The fold at G0's
placement — `untintedOptics` beside `optics`, the table's floor colour from it, L3 the encoded
fold of the author layer over `(T, α₃)` through one function `foldedOverlay` that
`tintedCssOptics` now calls too; a caller without `untintedOptics` gets the previous declarations.
On G0's ladder bed, re-captured on both tiers: **S4 met on every one of the thirty-six tinted
cells at both scales, worst |CSS − GPU| 0.0039** (sixteen were outside 0.005 before, the worst
−0.0684); **the hue**: cross-tier OKLab ΔE down on every sub-unit tinted cell by 0.0030–0.0323,
up on none (G0's Deferred item closed); **X3**: 48 / 48 GPU captures byte-identical; **S3 by
capture**: every untinted CSS capture byte-identical, every full-strength tinted capture within
0.00013 with not one differing pixel more than two device pixels inside the contour (21–42 region
pixels, worst code 38, on the antialiased edge where the transfer's moved floor colour reaches
the screen); **the floor**: L3 paints 0.340 where it painted 0.100, least margin +0.07318,
twelve of thirty-six cells were under it before; **the form**: 48 / 48 `linear`, no flip;
**the pins**: the identity to 8.885e−8 real, 1.490e−3 as written; X7's tinted clause worst
0.00158; **S8**: no layer, no primitive, three multiply-adds per tinted surface; suites green,
the Chromium pixel spec 11 / 11.

**Ruled:**

1. **The fold profiles' clause is re-declared on what the fold itself predicts.** Decision Log 2
   (5) bounded `(CSS − GPU)_tinted − (CSS − GPU)_untinted` at 0.01, and under increased contrast
   it reads −0.0333 at `s = 1` on a declaration the pins prove byte-identical: the clause was
   measuring the UNTINTED increased-contrast capsule's own +0.0364 disappearing under an opaque
   tint. The fold composites `(1 − s)·M + s·L`, so a tinted cell carries `(1 − s)` of its
   untinted material's gap by construction — the clause is therefore
   `(CSS − GPU)_tinted − (1 − s)·(CSS − GPU)_untinted` within 0.01, derived and not fitted. On
   the pre-check that reads −0.0017 / −0.0036 / +0.0031 under increased contrast and +0.0023 /
   +0.0005 / +0.0002 under reduced transparency at 0.2 / 0.5 / 1.0: **met on all six**. The
   untinted increased-contrast gap is W18 §5.79 §7's fold item and stays there; what the fold did
   on that profile is make the strength curve monotone (−0.049 / −0.018 / −0.033 → −0.009 /
   −0.022 / −0.033).
2. **S5 stays at 0.005 and the three misses are carried by name.** Its control — the decoration
   constant read at `s = 1` — is a function of L3's alpha (the rim and the press glow on L3
   composite at `α″`, not at 1), so the sub-unit rungs carry a residual that follows `1 − α″`.
   Eighteen of eighteen at dpr 1 (worst −0.00499); fifteen of eighteen at dpr 2, the three over by
   0.00011 / 0.00268 / 0.00049 (`photo` orange 0.2, `checkerboard` orange 0.1 and 0.2). The
   number is not loosened after the reading; the misses are the control's, attributed, and the
   fidelity claim is S4's, which those three cells meet at +0.0029 / +0.0036 / −0.0015.
3. **The clamp share is stated to four places.** Under the fold it is 0.0000 % on every cell but
   the 2x checkerboard's 0.0582 % (the pixels within 0.4 % of white G0 §2.1 names); G0's text
   said 0.000 at three places and is corrected beside in claims §5.80. The stop reads "under
   0.1 % of masked channel samples", which it is.
4. **The 2x checkerboard untinted control** (+0.0101, byte-identical to G0's) is W18's carried
   remainder on that box and scale, not a ladder cell; S4's "every ladder cell" is the tinted
   cells, as read.
5. **The filter collapse is a claim to read at the dry run:** a tinted surface's transfer is now
   the untinted surface's at the same backdrop, so a tinted group needs no `<filter>` of its own;
   G1 counts the definitions per group before and after on a tinted page.
6. **The bed's own strength axis, recommended for after the cut.** The canonical bed carries one
   sub-unit strength and it sits at this defect's zero crossing; the probe took attested 1x
   fixtures at five more rungs. Adding two rungs (0.2 and 0.75, orange, photo and checkerboard)
   to `scenes.json` at 1x would guard against this class of defect returning, and it is a W3
   amendment — the split, the partition counts and the gate move with it. Recommended as its own
   small child after the 0.8.0 cut, not inside W19; recorded in Deferred with its shape.

**The dry run opens** on the frozen configuration `485b824`: the whole bed, both tiers, GPU
first, the holdout read once (X8; the tinted holdout cells named in the acceptance), the
referee's S1–S9 with rulings 1–3 above, the sheets (X5) with the ladder at 1x beside native, and
`adopted-thresholds.test.ts` against the scratch matrix (X6).

## Surprises & Discoveries

- **2026-09-05 (G1 pre-check) — the fold profiles' movement clause was reading the untinted
  cell.** Under increased contrast the −0.033 "movement" at full strength is the untinted
  capsule's +0.036 vanishing under an opaque tint; the fold's own algebra gives the right clause,
  `(1 − s)` of the untinted gap, and it is met on all six rungs.
- **2026-09-05 (G1 pre-check) — a control read at `s = 1` is read at `α″ = 1`**, and L3's
  decoration composites at `α″` elsewhere; the constant is not one. Three dpr-2 cells carried by
  name.
- **2026-09-05 (G1 pre-check) — the transfer's moved floor colour reaches the screen at the
  contour** under an opaque full-strength layer: 21–42 pixels per cell, none more than two device
  pixels inside, worst code 38, interior mean within 0.00013. Byte-identity at `s = 1` was an
  argument about compositing and the capture settled it.
- **2026-09-05 (G0) — the table saturates, and that is the largest term.** The charter named a
  level error; the clamp on the seed's darkest channel is a hue error, non-affine, up to −0.083
  encoded, and the fold removes it entirely.
- **2026-09-05 (G0) — the error crosses zero where the bed happened to look.** The one sub-unit
  cell sits near the crossing; −0.068 at strength 0.1 on the same backdrop.
- **2026-09-05 (G0) — Apple's strength curve is the renderer's encoded mix to 0.003**, and the
  sub-unit gap to Apple is the thin-span level faded in by `(1 − s)`, not the law. The tint shade's
  own +0.007…+0.012 at full strength is the item nobody had.
- **2026-09-05 (G0) — the tier crosses Apple's curve** near strength 0.3 (−0.039 under native at
  0.1 on the photo, where the renderer is +0.030 over).
- **2026-09-05 (G0) — a closed form on a composite cannot model a clamp inside a filter**; the
  acceptance asked for it and was re-declared on the fold's own prediction.
- **2026-09-05 (G0) — the harness's window activation fails with the machine idle** (run 7, six
  of twelve cells, 700–818 s idle): a second failure mode beside W18's HID one; the tracker's.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-05: chartered from claims §5.79 §7's addendum (the W18 post-landing review's finding 1)
  on the user's decision; Decision Log 1 written; G0 dispatched on its recommendations.
- 2026-09-05: Decision Log 1 executed on the recommendations (the user); G0 resumed after a
  usage-limit stop mid-capture.
- 2026-09-05: G0 CLOSED (claims §5.80); Decision Log 2 — the Purpose and Grounding corrected
  beside, the closed-form clause and S5 re-declared on the fold's prediction, S3 by capture, the
  fold profiles' clause against the untinted control, X7 against the tier's `L`, the Deferred entry
  rewritten; six Surprises; G1 opens.
- 2026-09-05: Decision Log 3 — the pre-check at the gate: the fold accepted, the fold profiles'
  clause re-declared on `(1 − s)` of the untinted gap, S5's three misses carried by name, the
  clamp share to four places; three Surprises, two Deferred shapes; the dry run opens.
