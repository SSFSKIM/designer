# W18 — The union-contour residual: the CSS tier's interior on the three-up capsules and the stacked scene, separated into the box, the neighbours and the stack (2026-09-05)

> **Parent:** the post-v1 wave (`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`),
> by way of W17's Deferred entry "The union-contour residual" and claims §5.75 §7,
> §5.76 §7, which name this closure's shape. **Ordering (user, 2026-09-05, after
> 0.7.0):** "union-contour residual on the toolbar and stacked-photo scenes would be
> our next work." **Consumes:**
> `results/2026-09-04-w17-css-interior-level/g1/toolbar-residual.md` (the annulus
> profile per surface; the two derived residuals reach −0.0043 of −0.0122; the same
> span alone reads −0.0005), `g1/region-sweep.md` (a `<filter>` region is inert on a
> `backdrop-filter`: k 0.5–3 byte-identical), claims §5.74 §4 (the closed form of the
> renderer's four terms on the surface's own box and radius, on the device grid),
> §5.55 §3 (the thin material's level — the renderer's own gap), `web/scenes.ts` (the
> group unions at the sampling padding, 24, over the declared spacing of 12; the
> stack's overlay group is DOM-sampled on the GPU tier, `refraction: "approximate"`,
> by the scene's own design), `packages/geometry/src/union.ts`
> (`DEFAULT_GROUP_UNION`: neck 8, bulge 2, separation 16 — the three-up merges on the
> GPU tier, by at most 2 px per facing contour), and Filter Effects Module Level 2's
> rule for `backdrop-filter` (a blur reads the element's own clipped border box with
> `edgeMode="mirror"`; Chromium implements the mirror). **Starts from** `main` at the
> W17 bed (`5868672`, recomposed `350e065`; 0.7.0 published from `1ca4a67`): the CSS
> tier's interior is within 0.005 of the renderer's on every light calibration cell
> but the two `toolbar-group` scenes (−0.0122 / −0.0150 at 1x, −0.0040 / −0.0101 at
> 2x) and `photo__glass-over-glass` (−0.0119 / −0.0126, holdout); the
> reduced-transparency `photo__toolbar-group` reads −0.0320, the bed's largest
> cross-tier miss; seven dom `ssimMean` floors held by decision.

## Purpose

Close the last interior residual the CSS tier carries against the renderer — the
one on surfaces whose box is small in both extents, and the one on the stacked
scene — as a **derivation**. The same span alone lands within 0.0005 of the
renderer (the 120 × 44 capsule; the span, the shorter extent, is the size law's
input on both tiers), so what the three 44 × 44 circles pay is not the span: it
is the box, whose perimeter over area is 1.5× the capsule's, or the neighbours,
or both. The wave finds which by separating measurements — a lone circle against
the capsule, the three-up against the lone circle with the renderer's union on
and off, each of the renderer's per-pixel terms declined on the circle and the
capsule, the stack taken apart into its base, its overlay and their stacking —
and derives each part from the profile and the surface's own geometry with its
residual recorded, the way W17 derived the band's light and W16 carried the
effective width. The closure lands on Chromium inside the tier's existing form.

Beside that, the wave captures natively, on a probe bed of its own that is never
fitted, what Apple's material does with a lone 44 px capsule, with three of them
at a merging spacing and at a non-merging one, and with the stack — so that the
renderer's union and overlay behaviour on these scenes has its reading against
Apple on the record, for the renderer's charter and for the gap ledger. The
scene's own comment in `scenes.json` asked whether the two implementations union
proximity the same way; no capture has answered it yet.

What this wave does **not** do. It does not move the renderer — its union, its
overlay's sampling, its thin-span level — and it does not fit the tier to Apple
past the renderer. On the three-up the CSS tier sits nearer native today than the
GPU tier does (+0.043 against +0.055 over native on the checkerboard at 1x), and
it does so by the mechanism this wave removes: two tiers that disagree by design
on a class of boxes is not coherence, and the renderer's +0.02…+0.06 over native
on thin spans is its own gap (§5.55 §3), which the probe bed's native readings
feed. Where the stack's residual turns out to be the renderer's overlay route
rather than the tier's, that part is named and left to the renderer's wave.

## Parent-Level Acceptance

- **The residual is separated and attributed.** On the two `toolbar-group` cells
  at 1x and 2x, the parts — the box alone (a lone 44 × 44 capsule against the
  120 × 44 one, on both tiers), the neighbours (the three-up against the lone
  circle, at the declared spacing and at one past the renderer's separation), and
  the per-term shares (the renderer's terms declined on the circle and on the
  capsule) — sum to the measured residual within 0.003 per cell; each part has a
  closed form from the profile and the surface's box and radius, its residual
  against the measurement recorded per cell; the instrument's recovery of a known
  offset (X4) beside every reading. On the stack, the base alone, the overlay
  alone over the raw backdrop, and the two stacked separate the overlay's own
  share from the stacking's, on both tiers, on the photo and the checkerboard, at
  both scales.
- **The tier lands on the renderer's level on these cells.** CSS − GPU within
  0.005 on the two `toolbar-group` cells at both scales under the standard light
  profile (today −0.0122 / −0.0150 / −0.0040 / −0.0101); within 0.01 under reduced
  transparency and increased contrast (today −0.0320 / +0.0096); within 0.005 on
  `photo__glass-over-glass` at both scales (today −0.0119 / −0.0126; holdout, read
  once at the dry run) — or, where G0 attributes the stack's term to the
  renderer's overlay route, the tier's own share closed and the renderer's named.
- **Nothing else moves.** Every other light cell's CSS − GPU within 0.002 of the
  W17 bed; no dom row below its adopted bound or its floor, the seven held rows at
  or above their W17 pins; the tinted and solid cells within 0.002 in every adopted
  metric; `PREDICATE_EXCLUDES` does not grow (a cell that leaves by the fix is
  recorded).
- **The GPU tier does not move:** every capture byte-identical to the W17 bed.
  The renderer's union parameters and the overlay's sampling route are untouched.
- **The probe bed exists and is attested.** `apps/reference-apple/scenes-w18-probe.json`
  through `VITREA_SCENES` into its own fixtures dir under
  `packages/calibration/results/2026-09-05-w18-union-contour/probe/`, captured at
  1x by W9's rule (claims §5.30: attested runs, the majority byte-state per cell,
  the shares recorded), committed as evidence; its native readings — the lone
  circle, the three-up at 12 and at 40, the stack — recorded in claims with the
  renderer's and the tier's beside them, and nothing fitted to them.
- **The cost:** if the closure adds a primitive or a layer, the knee stays where
  W16 left it (W16 G0's harness); the collapse rule is unchanged.
- **Chromium is measured;** the plain-`blur()` engines keep their form behind the
  conformance rows and their level stays a named gap.
- **By eye:** the X5 sheets at the dry run and the landing, with the three-up and
  the stack beside native and the GPU tier; the reading recorded; the landing the
  user's.
- All suites green, lint clean; the canonical matrix rebuilt once at
  recomposition; the holdout read once per frozen configuration; every gap in
  claims, this Deferred list or the tracker.

## Grounding Baseline (the W17 bed, 2026-09-05, `5868672`)

Interior mean, whole native silhouette, linear luminance; native, then the GPU
tier and the CSS tier as deltas against native; the last column is the gap this
wave closes (CSS minus GPU). Standard light profile unless marked.

| cell | dpr | set | native | GPU Δ | CSS Δ | CSS − GPU |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__toolbar-group` | 1x | cal | 0.6210 | +0.0553 | +0.0431 | **−0.0122** |
| `checkerboard__toolbar-group` | 2x | cal | 0.6246 | +0.0575 | +0.0535 | **−0.0040** |
| `photo__toolbar-group` | 1x | val | 0.6012 | +0.0351 | +0.0201 | **−0.0150** |
| `photo__toolbar-group` | 2x | val | 0.6204 | +0.0170 | +0.0069 | **−0.0101** |
| `photo__toolbar-group` (RT) | 1x | val | 0.8899 | +0.0090 | −0.0230 | **−0.0320** |
| `photo__toolbar-group` (IC) | 1x | val | 0.8792 | +0.0235 | +0.0331 | +0.0096 |
| `photo__glass-over-glass` | 1x | hold | 0.7064 | −0.0203 | −0.0322 | **−0.0119** |
| `photo__glass-over-glass` | 2x | hold | 0.7054 | −0.0188 | −0.0314 | **−0.0126** |
| `checkerboard__glass-over-glass` | 1x | hold | 0.7231 | −0.0111 | −0.0153 | −0.0042 |
| `checkerboard__glass-over-glass` | 2x | hold | 0.7223 | −0.0045 | −0.0057 | −0.0012 |
| `checkerboard__capsule-button` | 1x | cal | 0.6207 | +0.0576 | +0.0571 | −0.0005 |
| `checkerboard__capsule-button` | 2x | cal | 0.6226 | +0.0621 | +0.0716 | +0.0095 |
| `photo__capsule-button` | 1x | cal | 0.5832 | +0.0346 | +0.0351 | +0.0005 |
| `photo__capsule-button` | 2x | cal | 0.5837 | +0.0341 | +0.0357 | +0.0016 |

Four readings of the table. (i) The lone capsule at the same span — 44, the
shorter extent, which is the size law's input on both tiers — lands within
0.0005 at 1x where the three circles read −0.012…−0.015: what differs is the box
(44 × 44 against 120 × 44; perimeter over area 0.091 against 0.060) and the
neighbours, and nothing that is a function of the span. (ii) On the three-up the
CSS tier is nearer native than the GPU tier; the renderer's own +0.035…+0.058
over native on the 44 px span is the thin material's level (§5.55 §3), the larger
number and not this wave's. (iii) The stack's residual is on the photo (−0.012 at
both scales) and not on the checkerboard (−0.004 / −0.001): a backdrop-dependent
term of the overlay's sampling, not a level; and natively the stack sits above
both tiers (−0.011…−0.032), which is the renderer's overlay gap for the record.
(iv) The fold on the three-up is the bed's largest cross-tier miss (−0.032 under
reduced transparency) and has the opposite sign under increased contrast (+0.010).

W17 G1's annulus profile (`toolbar-residual.md` §1) is the second baseline. At 1x
each of the six circles reads a broad interior offset, −0.004…−0.012 across the
three inner bands, with a bright contour band (+0.017…+0.062 at 0.88–1.00 of the
half extent); at 2x the core is positive (+0.000…+0.009) and only the outer band
negative (−0.001…−0.017). That is the signature of a term whose share of the
interior scales with the perimeter over the area, read through a heavy width that
is 0.30 of the box at 1x (σ 13.8 CSS px on 46) and 0.097 at 2x (4.46). The two
residuals W17's form derives — the encoded-space mix of the two tinted layers
(−0.0040, the same value on every 1x cell) and the kernel's truncation at the box
with edge padding (−0.00035) — leave −0.008 unexplained; the truncation model
assumed edge duplication where the engine mirrors, which this wave measures rather
than models.

## Design (advisory unless marked)

- **[binding] Two tiers, one profile (K5).** Every part of the closure is
  derived from the profile's numbers and the surface's own box and radius through
  `optics.ts`; no constant is fitted for this tier; every derived quantity carries
  its residual against the measurement per cell. A lookup table of measured
  residuals is not a derivation and is not admissible; a bounded residual carried
  with its geometry, as W16's effective width was, is.
- **[binding] The target is the renderer's rendered interior** (W17 Decision Log
  1 q0's rule, carried; Decision Log 1 q0 re-asked it on the cells where the tier
  sits nearer Apple today and the user answered 2026-09-05: carried without
  qualification). "GPU minus CSS" per cell is the check on the outcome, never
  the input; the renderer's residual against native on these scenes is recorded
  from the probe bed and left to the renderer's waves.
- **[binding] The GPU tier does not move.** This wave changes
  `packages/platform-web` and the calibration harness's CSS-tier rows; the
  renderer's material, passes, union parameters, overlay sampling and goldens are
  untouched and byte-identical at the dry run and the landing. A part of the
  residual that G0 attributes to the renderer — the union's neck material, the
  overlay's DOM route — is a `[parent-impact]` on this rule, and the parent
  re-decides before G1 opens; it is not fixed here.
- **[binding] The probe bed's custody.** Its own scenes file
  (`scenes-w18-probe.json`, W9's template) through `VITREA_SCENES`, its own
  fixtures dir under this wave's results directory through `VITREA_FIXTURES`;
  attested by W9's rule; readable by the study and forbidden to fits; its
  `toolbar-group`, `glass-over-glass` and `capsule-button` cells are recorded
  twins of canonical geometry, never a substitute for the canonical cells' own
  readings. The canonical `scenes.json`, `fixtures/` and `web-captures/` are not
  written.
- **[binding] X8 — the holdout is read once** per frozen configuration, at the
  dry run; the landing reproduces it. The stack's light cells are holdout; the
  probe bed's recorded twins and the web-only decomposition are the study.
- **[binding] Chromium is the measured engine.** As W16 and W17.
- Advisory — **M1, the box.** A per-surface term the tier carries as a function of
  the span where the renderer integrates it per pixel over the box. Candidates,
  each already in `optics.ts`: the heavy share's area mean and the ramp
  (`scatterRampAreaMean` takes the extents and ignores the corners — on a circle
  the corners are the whole surface); the inner shadow's co-area mean
  (`P(u) = 2(W − 2r) + 2(H − 2r) + 2π(r − u)`, exact on the circle only if the
  shader's depth and profile are what the integral assumes, and the shader clamps
  the depth at half the span); the band's derived light X (the rim and the
  highlight, which W17 G0 evaluated on the device grid over the surface's own
  mask — check what the tier carries at the circle against that). Separating
  measurement: the lone circle against the capsule on both tiers over the
  checkerboard, the photo and the light solid; the renderer's terms declined one
  at a time (W17 G0's instrument: a scratch profile document per term, the
  isolation proof's precedent) on the circle and on the capsule, so each term's
  share on each box is read. Expected signature: a residual that survives the
  solid backdrop and scales with the perimeter over the area.
- Advisory — **M2, the box-limited input.** The tier's filters read the element's
  own border-box snapshot with `edgeMode="mirror"`. A linear blur's box mean is
  preserved by the mirror, so any residual from this is the chain's nonlinearity
  on a box the kernel covers: the linear-light encode, the table transfer's
  remainder amplified by 1/(1 − α₃) (2.99 at the group's alpha), the heavy layer
  under its raster ramp; the renderer samples the real backdrop with 24 px of
  padding. Separating measurement: the lone circle over the light solid (where the
  mirror is exact) against the checkerboard and the photo; the residual against
  σ/box across dpr. Expected signature: zero on the solid, present on structure,
  larger at 1x.
- Advisory — **M3, the neighbours.** The renderer unions the three at neck 8 /
  bulge 2 / separation 16 over a spacing of 12 (the facing contours bulge by at
  most 2 px; the bodies stay three, which the conditioning predicate confirms);
  the group's sampling on the GPU tier is one texture over the row; the tier draws
  three hosts 12 px apart whose L2 masks, inset shadows and filters are per host.
  Separating measurement: the three-up against the lone circle on both tiers; the
  three-up at spacing 40 (no union on the renderer, no overlap of anything on the
  tier) against 12. Expected signature: a three-up minus lone-circle difference on
  one tier only, and which tier names the owner.
- Advisory — **M4, the stack.** The overlay samples the base's rendered output on
  both tiers by different routes: the tier's overlay host filters the base host's
  composite in place; the renderer's overlay group is DOM-sampled through the plane
  sandwich by the scene's design (`web/scenes.ts`). The residual is on the photo
  only. Separating measurement: the base alone (220 × 130 r24), the overlay alone
  over the raw backdrop (120 × 56 r16 at its offset), and the two stacked, on both
  tiers, both backgrounds, both scales. The overlay's span (56) sits between the
  capsule's and `rrect-md`'s, so M1 predicts little of it. Expected signature: a
  stacking term that tracks the base's own residual under the overlay's footprint
  (the tier's to close), or the overlay reading a different image on each tier
  (the route's, named).
- Advisory — **M5, Apple.** The probe bed at 1x: `capsule-sm` (44 × 44),
  `toolbar-group` (spacing 12; recorded twin), `toolbar-group-wide` (spacing 40),
  `glass-over-glass` (recorded twin) and `capsule-button` (recorded twin) on
  `checkerboard` and `photo` — ten cells, one profile, existing background kinds
  (nothing rebuilds, no TCC re-grant); `dump-layers` beside the captures for the
  container's declared merge. What it answers: whether Apple's 44 px circle sits at
  its 120 × 44 capsule's level (the size law's input natively), whether a spacing
  of 12 merges and what the merge does to the interior between and inside the
  members, and the stack's native level for the renderer's overlay charter.
- Advisory — **the likely closure.** The tier's per-surface terms evaluated over
  the surface's own box and radius on the device grid — the co-area integral with
  the corners, as the inner shadow already does — carried at construction from
  `extentsCssPx` and the radius the tier already has; if M2 carries part of it, that
  part bounded per box and dpr and carried with its residual. The stack's term, if
  it is the tier's, closed the same way; if it is the route's, named.
- Advisory — **the fold.** Reduced transparency on the three-up (−0.032) is the
  same terms under the fold's occlusion; increased contrast's +0.010 is the drawn
  border's share on a small box. G1 carries both under the same derivation; q4
  sets the clause.

## Children

### G0: The residual separated — spike (deliverable: findings)

- **Purpose:** read the residual apart on scratch — the box against the span, the
  neighbours against the box, the stack against its parts, each of the renderer's
  terms on the circle against the capsule — on both tiers at both scales; capture
  the probe bed natively at 1x; derive a closed form for each attributed part from
  the profile and the geometry with its residual per cell; validate the instrument
  (X4); recommend answers to Decision Log 1's questions with numbers.
- **Observable acceptance:** a findings document under
  `packages/calibration/results/2026-09-05-w18-union-contour/g0/` with (a) the
  separation table — CSS − GPU interior mean for the lone circle, the capsule, the
  three-up at 12 and at 40, on `checkerboard`, `photo` and `light-solid` at 1x and
  2x, under the native silhouette where a fixture exists and the declared region
  otherwise, both stated; (b) the per-term attribution on the circle and the
  capsule — the renderer's rim, highlight, lens, lift and inner shadow declined one
  at a time and together, W17 G0's instrument, the sum within 0.003 of the whole;
  (c) the stack's decomposition on both tiers, both backgrounds, both scales; (d)
  the closed form per attributed part with its residual per cell and the largest
  residual named with its cell; (e) the probe bed: the scenes file, the attested
  fixtures, the native readings with the renderer's and the tier's beside them,
  `dump-layers` for the group at 12 and at 40; (f) the X4 recovery; (g) the
  cost, if the closure's shape adds anything to the element model; (h) the answers
  G0 recommends to Decision Log 1's questions, with numbers.
- **Stops (G0 has none — it reports).** A part attributed to the renderer (the
  union's neck, the overlay's route) is a `[parent-impact]` on Design's third
  binding rule; a residual the closed forms leave over 0.003 on either
  `toolbar-group` cell is a `[parent-impact]` on the acceptance; the parent
  re-decides before G1 opens. A TCC denial on the harness stops the native probe,
  not the web-side separation, and is reported for the user's hand.
- **Track:** spike; one worker; scratch captures only (GPU custody: one capture
  at a time, nothing else on the adapter; `--out-matrix` and `VITREA_WEB_CAPTURES`
  to scratch; the probe bed through `VITREA_SCENES` and `VITREA_FIXTURES`);
  commits with pathspecs under the findings directory, the probe results directory
  and the probe scenes file alone.

### G1: The declared derivation and its dry run — controlled

- **Purpose:** the attributed parts derived in `optics.ts` / `css-tier.ts` from
  the profile and the surface's geometry, G0's residuals in the doc comments; the
  tier-coherence pin extended to the box (the tier's per-surface terms on a
  44 × 44 circle, a 120 × 44 capsule and a 220 × 130 rounded rectangle against
  the renderer's per-pixel integral, at dpr 1 and 2); the fold carried under the
  same derivation; the dry run on the full bed to scratch under the stops, the
  holdout read once; the sheets; the declaration in claims.
- **Stops (refined by G0 with numbers):** (S1) every GPU capture byte-identical to
  the W17 bed and every GPU row within 0.0002; (S2) no dom row below its bound or
  floor, the seven held rows at or above their W17 pins, no 1x checkerboard row
  more than 0.002 below the W17 bed; (S3) the spread within W17's reach of native
  on the calibration spans; (S4) CSS − GPU within 0.005 on both `toolbar-group`
  cells at both scales under the standard light profile, within 0.01 under
  reduced transparency and increased contrast, within 0.005 on
  `photo__glass-over-glass` at both scales at the once-read holdout (or the tier's
  own share closed where G0 named the route); (S5) every other light cell's
  CSS − GPU within 0.002 of the W17 bed; the tinted and solid cells within 0.002 in
  every adopted metric; (S6) `tier-coherence` tighter or equal, the cross-tier ΔE
  not up on any profile; (S7) `PREDICATE_EXCLUDES` not up; (S8) the cost knee
  unmoved; (S9) the user's eye.
- **Edges:** blocked-by G0. **Track:** controlled; a branch; the landing is the
  user's call (Decision Log).

### G2: The landing and its referee — controlled

- **Purpose:** merge; the canonical rebuild once; the floors re-recorded at the
  landing's readings (none may go down without a decision); `PREDICATE_EXCLUDES`
  as the machine's output; the sheets; recomposition.
- **Stops:** G1's, re-read on the canonical bed, plus the referee running the
  landing's test file against the dry-run matrix before the merge (X6).
- **Edges:** blocked-by G1. **Track:** controlled.

## Cross-Child Contracts

- **X1 — the canonical rebuild.** As W16 X1: once, from the main checkout, at G2.
  Owner: parent.
- **X2 — floor bookkeeping.** Floors ratchet up where rows rise; a floor that
  would go down stops the landing for the user. Owner: parent.
- **X3 — the untouched tier.** Byte identity on the GPU tier, every profile; the
  union parameters and the overlay's sampling route untouched. Owner: parent.
- **X4 — the instrument's validation travels with every reading.** The
  interior-mean reader recovers a synthetic offset (+0.03 in linear light lerped
  into a capture) before it reads a separation. Owner: G0; G1 binds.
- **X5 — the by-eye sheets.** The W17 script's panels at 1x and 2x, dry run and
  landing, with the three-up and the stack beside native and the GPU tier. Owner:
  parent.
- **X6 — the dry-run referee runs the landing's gates.**
  `adopted-thresholds.test.ts` against the scratch matrix through
  `VITREA_MATRIX_PATH` (W17 X6). Owner: parent.
- **X7 — the coherence pin.** `tier-coherence.test.ts` asserts the tier's
  per-surface terms against the renderer's per-pixel integral on the three boxes
  and both dprs. Owner: G1.
- **X8 — the holdout, read once** per frozen configuration. Owner: G1; parent
  verifies.
- **X9 — the engines.** The closure is gated on the reference filter's
  conformance row where it lives in the filter; the plain-`blur()` engines' level
  stays a named gap. Owner: G1.
- **X10 — the probe bed's custody.** `scenes-w18-probe.json` and
  `results/2026-09-05-w18-union-contour/probe/` (fixtures, `last-run-manifest.json`,
  `provenance.json` by W9's rule); read by the study, fitted by nothing; the
  canonical layout untouched. Owner: G0; parent verifies.
- **X11 — the renderer's numbers travel unchanged.** `DEFAULT_GROUP_UNION`, the
  overlay group's `source`, `DEFAULT_GROUP_SAMPLING` are read, never edited, by
  every child. Owner: parent.

## Ordering & Dependency Map

G0 → G1 → G2 → recomposition. Nothing lands before G2's referee. Inside G0 the
web-side separation runs first (no native fixture needed for a cross-tier
reading) and the native probe second, behind its TCC gate; the two halves are
reported together.

## Risks & Mitigations

- **The harness's Screen Recording grant has lapsed.** The grant is keyed to the
  bundle's ad-hoc signature and survives only while `build.sh` is not re-run
  (README); the binary is the W12 probe's (2026-09-03). G0 runs `./capture.sh probe`
  first and stops the native half on a denial, reporting for the user's toggle;
  the web-side separation is unaffected.
- **The 2x native probe needs the display reconfigured.** The machine's displays
  present at 1x; the canonical 2x fixtures were captured on a reconfigured
  display. The probe is chartered at 1x (q1); a 2x session is the user's to open.
- **The residual is the renderer's.** The union's neck material or the overlay's
  DOM route may own part of it; X3 binds, G0 reports it as a `[parent-impact]`, and
  the fix belongs to the renderer's wave with its goldens' isolation proof — not
  this one.
- **The residual is the engine's and has no closed form.** If M2 carries it and
  the mirror's nonlinear remainder on a small box does not reduce to the profile's
  numbers, the admissible carry is a residual bounded per box and dpr with its
  geometry (K5's "derived with residual"), or a named gap; a lookup table is not.
- **The fold on the three-up is a separate mechanism.** −0.032 under reduced
  transparency is 2.6× the standard cell's; if the same derivation does not close
  it, G1 carries it under its own reason and q4's clause decides what is accepted.
- **The probe bed does not settle.** W9's rule (seven attested runs, the majority
  byte-state, the shares recorded) is the instrument; a cell under 4/7 is reported
  as unsettled, not read.

## Deferred / Out of Scope

- **The renderer's own level on thin spans** — +0.035…+0.058 over native on the
  44 px span (§5.55 §3); the probe bed's lone-circle reading joins that ledger.
  Its own charter.
- **The renderer's overlay gap** — the stack natively above both tiers
  (−0.011…−0.032); the probe's stack readings recorded for the renderer's charter.
- **The renderer's union against Apple's** — whether a spacing of 12 merges
  natively and what the merge does: the probe answers, and a difference is the
  renderer's item, not this tier's.
- **The shape axis's four cells and the fold's second cell** (W17 Deferred) — the
  extractor's second arm; an instrument item.
- **The darks on the encoded form; the plain-`blur()` engines' level; the CSS
  tier's frame timing** — W17 Deferred, unchanged.
- **A 2x native probe** — if the user opens a 2x session, the same scenes file at
  `VITREA_SCALE=2` into a second fixtures dir; otherwise the 2x separation is
  web-side only and says so.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | `packages/calibration/results/2026-09-05-w18-union-contour/g0/` (findings), `probe/` (the bed), `apps/reference-apple/scenes-w18-probe.json` | OPEN 2026-09-05 — dispatched on Decision Log 1's recommendations, which the user executed the same day (q0–q5 at the recommendations) |
| G1 | — | — |
| G2 | — | — |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-05)

**The cut.** Three children as W16's and W17's: a spike that separates the residual
into parts by measurement and derives each, a controlled gate that declares the
derivation and dry-runs it under stops, a controlled landing. The native probe
rides inside the spike rather than as a child of its own: it is one bed, one
profile, ten cells, and its readings are evidence for the record rather than an
input to the derivation — a fourth child would put a measurement nobody fits to on
the critical path.

**Bound here, with the joint-view reason.** The target stays the renderer's
rendered interior (W17's rule): the only alternative on these cells — leaving the
tier where it is because it happens to sit nearer Apple — would make the two tiers
disagree on purpose on every small box, and the renderer's thin-span level is
recorded as its own gap with a charter's shape. The GPU tier does not move, so a
part of the residual that is the renderer's stops this wave for a re-decision
rather than being fixed in passing. The probe bed is data-only under W9's rule.

**Put to the user, with the recommendation.**

- **q0 — the target on the three-up.** (a) The renderer's rendered interior, as
  W17 (recommended: the binding rule above; the tier is nearer Apple today by the
  defect this wave removes, and the renderer's +0.04…+0.06 on the 44 px span is
  §5.55 §3's item). (b) Leave the `toolbar-group` cells and close the stack alone —
  rejected: two tiers disagreeing by design on a class of boxes.
- **q1 — the native probe's scope.** (a) 1x only: ten cells (the lone circle, the
  three-up at 12 and at 40, the stack and the capsule as recorded twins, on the
  checkerboard and the photo), seven attested runs by W9's rule, from this machine
  (recommended: the separation is web-side and needs no native; the probe answers
  what Apple does with a small box, a merge and a stack for the record, and 2x
  needs the display reconfigured). (b) 1x and 2x, the user opening a 2x session.
  (c) No native probe — rejected: the wave's purpose is the gap to Apple, and the
  renderer's charter needs these readings.
- **q2 — the stack in scope.** (a) Yes, as a second mechanism family: its light
  cells are holdout and are read once at the dry run; the probe's recorded twins
  and the web-only decomposition are the study; where G0 attributes the term to
  the renderer's overlay route, that part is named and left (recommended). (b) The
  three-up only.
- **q3 — if G0 attributes a part to the renderer.** (a) Stop and re-decide with the
  numbers: the tier's own share closes here and the renderer's part is chartered
  where the goldens' isolation proof lives (recommended: X3). (b) Let this wave
  move the renderer — rejected: a renderer change needs its own referee, and two
  tiers moving in one wave is what K5's discipline exists to prevent.
- **q4 — the fold's clause on the three-up.** (a) Within 0.01 of the GPU tier
  under reduced transparency and increased contrast (recommended: from −0.032 and
  +0.010; W17's clause for those profiles was 0.015 and the fold on a small box is
  the same terms under the occlusion). (b) Within 0.015, W17's. (c) Out of scope —
  rejected: it is the bed's largest cross-tier miss.
- **q5 — the trade if the level costs structure.** (a) Stop and put both landings
  to the user with the sheets and the rows, as W15 and W17 did (recommended). (b)
  Accept structure losses inside the floors' epsilon without asking.

G0 opens on the recommendations; each answer that differs re-opens the affected
child before G1.

**Executed 2026-09-05 (the user: "Yes, all according to your Recommendation").** q0 (a) —
the target is the renderer's rendered interior on the three-up as everywhere; the Design
bullet that carried "q0 below re-asks it" is binding without qualification. q1 (a) — the
native probe at 1x from this machine, ten cells, seven attested runs by W9's rule; a 2x
session is the user's to open and is not chartered. q2 (a) — the stack is in scope as a
second mechanism family; its light cells are holdout, read once at the dry run; a part that
is the renderer's overlay route is named and left. q3 (a) — a part attributed to the renderer
stops the wave for a re-decision with the numbers; the renderer's part is chartered where the
goldens' isolation proof lives. q4 (a) — the fold's clause on the three-up is 0.01 of the GPU
tier under reduced transparency and increased contrast (S4 as written). q5 (a) — if the level
costs structure past S2, the wave stops and both landings go to the user with the sheets and
the rows. G0 was already running on these answers; nothing re-opens.

## Surprises & Discoveries

- (none yet)

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-05: v1 — chartered from W17's Deferred entry and claims §5.75 §7 on the
  user's pick after 0.7.0; grounded on the W17 bed, W17 G1's diagnosis, the scene
  builder's union and stack routes, the renderer's union parameters and Filter
  Effects 2's mirror rule; G0 dispatched on Decision Log 1's recommendations.
- 2026-09-05: Decision Log 1 executed by the user at the recommendations (q0–q5); the
  target rule's qualification removed; the Tracking Map's G0 row amended.
