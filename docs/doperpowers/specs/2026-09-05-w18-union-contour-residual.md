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

**Corrected by G0 (Decision Log 2, 2026-09-05).** The residual is not a term the tier
computes by the span; it is a thing the tier paints and then re-reads. The outer shadow,
a `box-shadow` on the host, sits inside the sampled region of the host's own filter
layers and of its neighbours' — declining it moves the GPU tier by 0.00000 and the CSS
tier by +0.0032…+0.0096, and it is the whole of the neighbours' term. The renderer's
union is not implicated: its interior is flat to ±0.0002 across gaps of 12 to 56. The
stack's residual is the renderer's: on a DOM-sourced group it draws an unsampled white at
α 0.665 where the tier draws the profile's material, and under q3 that part is named and
left. The purpose stands with its means restated: the shadow leaves the sampled backdrop,
and the remainder on structure (about −0.005 on the small box, zero on the solid) is
derived or bounded at G1's pre-check.

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
*Correction beside (G0 §4, claims §5.77 §4): the stack's residual is the overlay's,
0.042–0.057 on the checkerboard as on the photo; the whole-cell number is the dilution of a
23 % region by the base's own positive difference; the owner is the renderer's unsampled
route, not a backdrop-dependent term of the tier's.*

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
- **Corrected by G0 (Decision Log 2) — the mechanism and the closure.** The tier writes the
  outer shadow as `box-shadow` on the host, whose three filter layers are negative-`z`
  children painted after it, and Chromium samples a `backdrop-filter`'s backdrop over the
  region its kernel needs; so every surface blurs its own shadow into its own body, and a
  later host blurs its earlier neighbours' shadows into its body too. The host is a
  stacking context (`isolation: isolate`), so a child of a host can be painted after that
  host's own filters but never after a sibling host's. Two carriers follow, and G1
  measures both on G0's probe scenes before the whole-bed run: **A**, per surface — the
  outer shadow joins L3's `box-shadow` list (painted after L1 and L2; a surface's own
  filters never sample it), on every host whose overflow does not clip its children; **B**,
  per group — the members' shadows painted after every member's filter layers, hosted by
  the group's last-painted member as one child per member at that member's box and radius,
  clipped out of every member's body by an even-odd path (the renderer's `(1 − coverage)`),
  none focusable, hit-testable or announced. The fallback per host is recorded in the
  group's state (`cssShadow`), and G0 §6's closed form stays in `optics.ts` as the bound for
  what remains sampled (a neighbour outside the group within the shadow's reach, a clipping
  host). What is left with the shadow out — about −0.0045 on the lone circle over the
  checkerboard and the photo, +0.0017 over the solid, near zero on the capsule — is M2's
  family and is G1's pre-check to derive or bound: the interior spread per tier beside the
  mean on the small box, the blur's effective width on a box the kernel covers, the chain's
  nonlinearity turning a spread difference into a level difference.
- Advisory — **M1, the box.** *(G0: carries no share — two of the three terms already
  integrate over the box, and the ramp's rectangle form errs +0.0000 on the circle.)* A per-surface term the tier carries as a function of
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
- Advisory — **M2, the box-limited input.** *(G0: masked in the default captures by the
  shadow's share on the solid; with the shadow out its signature holds for the remainder —
  zero on the solid, present on structure — and it is G1's pre-check.)* The tier's filters read the element's
  own border-box snapshot with `edgeMode="mirror"`. A linear blur's box mean is
  preserved by the mirror, so any residual from this is the chain's nonlinearity
  on a box the kernel covers: the linear-light encode, the table transfer's
  remainder amplified by 1/(1 − α₃) (2.99 at the group's alpha), the heavy layer
  under its raster ramp; the renderer samples the real backdrop with 24 px of
  padding. Separating measurement: the lone circle over the light solid (where the
  mirror is exact) against the checkerboard and the photo; the residual against
  σ/box across dpr. Expected signature: zero on the solid, present on structure,
  larger at 1x.
- Advisory — **M3, the neighbours.** *(G0: confirmed exactly, the tier the owner, by the
  mechanism above and not the union — the renderer's interior is flat across the sweep.)* The renderer unions the three at neck 8 /
  bulge 2 / separation 16 over a spacing of 12 (the facing contours bulge by at
  most 2 px; the bodies stay three, which the conditioning predicate confirms);
  the group's sampling on the GPU tier is one texture over the row; the tier draws
  three hosts 12 px apart whose L2 masks, inset shadows and filters are per host.
  Separating measurement: the three-up against the lone circle on both tiers; the
  three-up at spacing 40 (no union on the renderer, no overlap of anything on the
  tier) against 12. Expected signature: a three-up minus lone-circle difference on
  one tier only, and which tier names the owner.
- Advisory — **M4, the stack.** *(G0: the renderer's — an unsampled white at α 0.665 on the
  DOM-sourced overlay group; the tier's share is inside 0.005; re-decided under q3.)* The overlay samples the base's rendered output on
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
- Advisory — **M5, Apple.** *(G0: the layer tree answered without the grant — one backdrop
  over the row, `smoothness` equal to the spacing, no threshold; the pixels wait on it.)* The probe bed at 1x: `capsule-sm` (44 × 44),
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

### G1: The shadow out of the sampled backdrop, the remainder measured, and the dry run — controlled

- **Purpose:** the outer shadow leaves every sampled backdrop the tier can take it out
  of — carrier A on every host whose overflow does not clip, carrier B where a group has
  more than one member (Design, the corrected bullet), the fallback per host recorded in
  `GlassGroupState.cssShadow`; G0 §6's closed form kept in `optics.ts` as the bound for
  what stays sampled, its residual in the doc comment; the pre-check on G0's probe scenes
  at both scales on both tiers, reported before the whole-bed run (Decision Log 3): the
  two carriers' readings, the remainder on the lone circle over structure with the interior
  spread per tier beside the mean, and its derivation or its bound; then the dry run on the
  full bed to scratch under the stops, the holdout read once; the sheets; the declaration in
  claims.
- **Stops (refined by G0; re-declared at Decision Log 3 with the pre-check's numbers):**
  (S1) every GPU capture byte-identical to the W17 bed and every GPU row within 0.0002;
  (S2) no dom row below its bound or floor, the seven held rows at or above their W17 pins,
  no 1x checkerboard row more than 0.002 below the W17 bed; (S3) the spread within W17's
  reach of native on the calibration spans; (S4) CSS − GPU within 0.005 on both
  `toolbar-group` cells at both scales under the standard light profile (from −0.0122 /
  −0.0150 / −0.0040 / −0.0101), within 0.01 under reduced transparency and increased
  contrast (from −0.0320 / +0.0096); on `glass-over-glass` the tier's share — the base
  excluding the overlay within 0.005 of the GPU tier (from +0.0083 / +0.0018) and the
  overlay alone over the raw backdrop within 0.005 (from +0.0043 / +0.0054) — read on the
  scratch twins, the canonical holdout cell read once and recorded with the renderer's route
  named as its remainder; (S5) every other light cell's CSS − GPU moves by its own derived
  shadow share and no more — the move within 0.0015 of G0's closed form per cell — and stays
  within W17's 0.01 clause, or its leaving is named for the user with the number (a
  darkening that was never fidelity is not a reason to keep it); the tinted and solid cells'
  other adopted metrics within 0.002; (S6) `tier-coherence` tighter or equal, the cross-tier
  ΔE not up on any profile; (S7) `PREDICATE_EXCLUDES` not up; (S8) the cost knee unmoved if
  carrier B adds children (W16 G0's harness); (S9) by eye, the shadow outside every surface
  unchanged and no shadow on a member's body inside a group; (S10) the user's eye.
  *S4 and S5 re-declared at Decision Log 3 with the pre-check's numbers.*
- **Edges:** blocked-by G0 (CLOSED). **Track:** controlled; a branch in a worktree; the
  pre-check gate is Decision Log 3; the landing is the user's call.

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
- **X7 — the coherence pin.** `tier-coherence.test.ts` asserts that no filter layer
  of a group samples a shadow the tier paints for that group (the paint order, by
  construction of the carriers) and G0 §6's closed form as the bound where a shadow
  stays sampled. *(Restated by Decision Log 2 from the per-surface-terms pin the charter
  wrote; G0 found those terms carry no share.)* Owner: G1.
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
- **The renderer's unsampled material on DOM-sourced groups (G0 §4).** The overlay group
  of the stack draws `tint [1, 1, 1]` at α 0.66496 with `analysis: "none"`, 0.042–0.057
  above the tier's converted material on the same base; by the whole-cell native readings
  the native overlay sits above both — measured on the probe bed at 0.9088 / 0.8970
  (checkerboard / photo), +0.019 / +0.023 above the renderer's white and +0.065 / +0.080
  above the tier's material. Its charter: a static material derived from the
  profile at the group's hinted or sampled level, or a sampling route for DOM sources,
  where the goldens' isolation proof lives; the probe bed's stack twin (pending the grant)
  gives the native overlay level.
- **The renderer's union against Apple's (G0 §5).** Apple's container blends by a
  `smoothness` equal to the declared spacing at every spacing, one backdrop layer over the
  row, no separation threshold; the renderer stops at 16. The renderer's item.
- **The native pixels of the probe bed at 2x** — the 1x bed is captured and read
  (`probe/readings.md`); a 2x session is the user's to open.
- **The 2x `capsule-button` at +0.0094** (W17's own miss inside 0.01) — the shadow's
  removal moves it; S5 names what leaves 0.01. *Decision Log 3: its mechanism is M2's sign flip
  at 2x (+0.0076 of structure remainder on that box), the shadow's share +0.0007; predicted
  +0.0102; the landing question's.*
- **The box-limited filter input's remainder (M2), bounded, not derived (Decision Log 3).**
  The tier keeps the same fraction of the backdrop's structure on a 44 × 44 box as on a 120 × 44
  one where the renderer and Apple keep more on the small box; the level cost is −0.0044…−0.0069
  per small box over structure at 1x and up to +0.0076 on the 2x checkerboard capsule. Its
  charter's shape: a sweep of square boxes (24…120 CSS px) over the checkerboard and the photo
  at both scales, the spread per tier beside the mean, the effective blur width per box against
  W16's ratio (derived on spans whose long extent exceeds the kernel), and a derivation of the
  chain's nonlinearity on the mirrored distribution or a per-box effective width carried with its
  residual.
- **The shadow's composite over a glassed body (the stack's base).** G0's decline puts 0.0054 of
  the checkerboard base's +0.0081 on the shadow's composite where a surface's shadow falls on
  another surface's rendered interior: the tier multiplies in encoded space by
  `cssTierShadowAlpha`'s conversion, the renderer occludes in linear light, and on a lightened
  body the two differ. Its shape: the conversion re-derived at the glassed body's level, or the
  composite bounded per level with its residual; measured on the stack's base region.
- **A 2x native probe** — if the user opens a 2x session, the same scenes file at
  `VITREA_SCALE=2` into a second fixtures dir; otherwise the 2x separation is
  web-side only and says so.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | `packages/calibration/results/2026-09-05-w18-union-contour/g0/g0-findings.md` (`ebb57fa`), `probe/` (the bed, `scenes-w18-probe.json`, two layer dumps), claims §5.77 | CLOSED 2026-09-05 — the owner is the tier's own shadow in its own sampled backdrop (the whole neighbours' term, half the box's); the renderer's union not implicated; the stack the renderer's route; Apple's container blends by the spacing; four `[parent-impact]` items reconciled in Decision Log 2; the native pixels taken the same day after the user restored the grant (`probe/readings.md`: seven attested runs, the twins byte-identical to the canonical fixtures, Apple's material box-invariant at the span, the native overlay 0.909 / 0.897) |
| G1 | branch `w18-g1-shadow` (`6207287` the carriers, `7a8a09b` the pre-check, `2d11305` the dry run; `g1/g1-precheck.md`, `g1/g1-dry-run.md`, `dry-verify.txt`, `dry-gate.txt`, `sheets/g1-{1,2}x.png`, `.changeset/css-shadow-carriers.md`); claims §5.78 | COMPLETE 2026-09-05 — DECLARED in claims §5.78: seven stops met, S4's fold clause missed both ways, S5 on one cell by 0.0005, two cells over 0.01 by a thousandth, three cells back on the shape axis, the GPU tier byte-identical; the landing is Decision Log 4, the user's |
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

### Decision Log 2 — G0 read: the mechanism is the tier's own shadow in its own backdrop; the stack is the renderer's route, re-decided under q3; the Design rewritten on the attribution (2026-09-05)

**What G0 found (claims §5.77; `g0/g0-findings.md`, `ebb57fa`).** The parts sum exactly on
the checkerboard at 1x: the same span alone −0.0005, the box −0.0072, the neighbours far
+0.0014, the neighbours near −0.0059. The renderer's interior is flat to ±0.0002 across gaps
12–56; the tier's rises and saturates by 28, the outer shadow's own reach (σ 15.55). Declining
the outer shadow moves the GPU tier by 0.00000 on every cell and the CSS tier by +0.0032 to
+0.0096; the neighbours' term goes from −0.0058 to +0.0005. Declining the charter's five terms
makes the residual worse. With the shadow out the cells read −0.0026 / −0.0086 / +0.0044 /
−0.0043 (checkerboard and photo, 1x then 2x); the photo's remainder is per surface over
structure (−0.0084 at gap 40), M2's family. The stack's residual is the overlay's (−0.046 /
−0.057 at 1x, on both backdrops), not its material (+0.004 / +0.005 alone), not the shadow
(0.0002): the renderer draws an unsampled white at α 0.66496 on the DOM-sourced group
(0.335 × 0.6951 + 0.665 = 0.898 against 0.8899 measured). The closed form is exact to 0.0014
with no close neighbour and to 0.0004 on the three at gap 40, and under-predicts the merging
gap by +0.0024…+0.0062 (the paint order's asymmetry). Superposition holds on 22 of 24 rows
within 0.0018; `light-solid__capsule-button` misses by +0.0059 / +0.0065 where the rim and
the highlight clip at white. The grant is denied; the bed is committed; the layer tree read
without it: one `CABackdropLayer` over the row, three union elements, `smoothness` equal to
the spacing at 12 and at 40, no threshold.

**Decided here (the parent, inside the user's q0–q5).**

1. **The closure is a removal, not a compensation.** The shadow leaves the sampled backdrop
   by the two carriers in Design's corrected bullet; a compensation inside the affine would
   correct a mean against a structured perturbation and leave a signature the level does not
   show. The closed form is kept as the bound for what stays sampled, and the last third of
   the neighbours' term (the paint order at the merging gap) is not modelled because the
   carriers remove the thing it models. (`[parent-impact]` 2 reconciled.)
2. **The stack, under q3 (a).** The tier's own share is the clause: the base excluding the
   overlay and the overlay alone, each within 0.005 of the GPU tier (S4 restated); the
   canonical holdout cell's whole-cell reading is recorded once, not gated, with the
   renderer's route named as its remainder. The renderer's unsampled material on DOM-sourced
   groups is a named gap with its charter's shape (Deferred). (`[parent-impact]` 1.)
3. **The Design is rewritten on the attribution.** M1 closed (no share); M2 narrowed to the
   remainder with the shadow out; M3 confirmed with the tier as the owner by a mechanism
   outside the list; M4 the renderer's; M5's layer-tree half answered, its pixel half
   waiting on the grant. (`[parent-impact]` 3.)
4. **The remainder on structure is a gate, not a discovery at the dry run.** G1 reports the
   pre-check on G0's probe scenes (Decision Log 3) — the carriers' readings and the
   remainder with the interior spread per tier — before the whole-bed run; S4 on
   `photo__toolbar-group` at 1x is re-declared there with the number, by the user if it
   cannot be derived. (`[parent-impact]` 4.)
5. **X7 restated** from a per-surface-terms pin to a paint-order assertion with the closed
   form as the bound elsewhere.
6. **The acceptance's superposition clause** is met on 22 of 24 rows; the one cell's miss is
   the reference's clipping at white, recorded as a Surprise and not a stop.
7. **S5 is written for what the removal does everywhere:** every light cell's CSS − GPU
   moves by its own shadow share (the closed form within 0.0015), and a cell that leaves
   W17's 0.01 clause because a darkening that was never fidelity is gone is named for the
   user with the number, not kept dark.
8. **The native probe** waits on the user's grant and is run by the parent, sequenced with
   G1's captures (one capture process at a time); its readings go to claims as the ledger's
   half and fit nothing.

G1 opens on this log.

### Decision Log 3 — the pre-check at the gate: both carriers accepted, the remainder bounded per box and scale, S4 and S5 re-declared with the numbers, the whole-bed run opens (2026-09-05)

**What the pre-check measured** (`g1/g1-precheck.md`, branch `w18-g1-shadow` at `7a8a09b`). The two
carriers reproduce G0's `no-outer-shadow` decline within 0.0002 on all twenty-four rows of the
separation bed while the shadow stays on the page outside every surface (a ring one device pixel
outside the contour reads 0.4751 against 0.4747 with the shadow on the host and 0.5029 with it
declined). `checkerboard__toolbar-group` −0.0122 → **−0.0028** at 1x and −0.0040 → **+0.0044** at
2x; `photo__toolbar-group` −0.0150 → **−0.0087** and −0.0101 → **−0.0044**. Carrier A alone leaves
−0.0099 / −0.0140 on the two 1x cells, so carrier B is two thirds of the closure on a group. Every
GPU capture byte-identical to G0's (36 / 36). The cost knee unmoved (40 surfaces at both scales,
every surface in a group of three). The DOM as the e2e spec reads it: a lone host `layer`, a
three-member group `group` with one caster per member inside the last-painted host under an
even-odd clip, a clipping host `host`. **The remainder with the shadow out** is M2's: on the light
solid (the one backdrop whose mirror is exact) every component reads +0.0016…+0.0026, and the
structure-dependent part is −0.0015…−0.0020 on the 120 × 44 box and −0.0044…−0.0069 on the 44 × 44
at 1x (−0.0103 on the confounded bright photo patch), sign-flipped at 2x (+0.0076 on the
checkerboard capsule). The spread names it: the tier keeps 0.278 of the backdrop's structure on
both boxes where the renderer keeps 0.306 on the small one and 0.277 on the capsule, and Apple
sits on the renderer's side (`probe/readings.md`). The step from the spread to the level is not
one coefficient (−0.0142 of spread with −0.0062 of level on one cell, −0.0082 with +0.0011 on
another), and the worker did not fit one. The stack: the overlay's term unchanged and the
renderer's (−0.0459 / −0.0565); the overlay alone within 0.005 (+0.0047 / +0.0057); the base
excluding the overlay unchanged by the carriers (+0.0081 / +0.0016 at 1x against G0's +0.0083 /
+0.0018; +0.0108 / +0.0006 at 2x). The Design's carrier-A note that the shadow's spread grows by
the border width was wrong and was not applied: `layerFrame` insets L3 by the border width from
the host's padding box, which is the border box already, and `border-radius: inherit` puts the
host's radius on it (a Revision Note).

**Decided here (the parent), before the whole-bed run.**

1. **Both carriers land**; carrier B is load-bearing and stays. The default carrier is `layer`,
   `host` only where the page's own `overflow` forces it, `group` where a group has more than one
   member; `GlassGroupState.cssShadow` reports which.
2. **The remainder is carried as a bound per box and per scale**, K5's admissible form (W16's
   effective width the precedent), with its mechanism named and evidenced by the spread and
   its charter's shape in Deferred: at 1x, −0.0015…−0.0020 on a 120 × 44 box and
   −0.0044…−0.0069 on a 44 × 44 over structure, +0.0016…+0.0026 on a solid; at 2x within
   ±0.002 on the photo and up to +0.0076 on the checkerboard capsule. No coefficient is fitted
   for it. The 2x `checkerboard__capsule-button` at +0.0095 on the W17 bed is this family's sign
   flip at 2x, not the shadow's (the shadow's share there is +0.0007).
3. **S4 re-declared on `photo__toolbar-group` at 1x: within 0.01 of the GPU tier** (from
   −0.0150; the pre-check reads −0.0087, the bound's −0.0103 on the bright-patch member the
   reason), with the miss of the charter's 0.005 named. The other three cells keep 0.005
   (−0.0028 / +0.0044 / −0.0044 at the pre-check). The fold's clause (q4, 0.01) is measured at
   the dry run.
4. **S4's stack clause restated to what this wave touches**: the overlay alone over the raw
   backdrop within 0.005 (met); the base excluding the overlay within 0.001 of G0's reading (the
   carriers move it 0.0002). The checkerboard base's +0.0081 / +0.0108 is not closed here and is
   named: G0's decline put 0.0054 of it on the shadow's composite over a glassed body (the two
   tiers darken the base's rendered interior unequally under the overlay's shadow) and the rest
   on the largest box's remainder; Deferred carries both shapes. The canonical holdout cells'
   whole-cell readings are recorded once with the renderer's route as their remainder (the
   photo predicted −0.0100 / −0.0108).
5. **S5 re-declared with what the form predicts and what it was never asked to carry**: every
   single-member light cell's CSS − GPU moves by the closed form's share within 0.002 (the
   pre-check's isolated boxes within 0.0015), the light-solid cells within 0.0035 (the form's
   recorded under-prediction on the solid, +0.0029…+0.0030); the two `toolbar-group` cells move
   above the form by the paint-order residual Decision Log 2 (1) declined to model, bounded at
   0.005 per cell (+0.0038…+0.0047 at the pre-check), and are gated by S4 directly. A cell that
   leaves W17's 0.01 clause is named for the user with the number: the pre-check predicts one,
   `checkerboard__capsule-button` at 2x at about +0.0102 (from +0.0095; the shadow's share
   +0.0007; the mechanism item 2's), and the landing question carries it.
6. **The dark and tinted cells** move by their own derived share and no more (S5's rule applies
   to every cell; the shadow is multiplicative and inert over black).
7. **X7 as built stands**: the coherence pin asserts the paint order from the tier's own output
   and `sampledOuterShadowFactor` bounds the `host` fallback.

**The whole-bed run opens on this log:** every profile at both scales on both tiers to scratch,
the holdout read once in the same frozen configuration (`6207287`), the referee
(`adopted-thresholds.test.ts` through `VITREA_MATRIX_PATH`; the verify script against the W17
bed), the sheets, the changeset, the declaration in claims.

### Decision Log 4 — the landing: as declared, held for the fold, or carrier A alone (2026-09-05; the user's)

**What the dry run measured** (claims §5.78; `g1/g1-dry-run.md`, branch `w18-g1-shadow` at
`2d11305`). S1, S2, S3, S6, S7, S8, S9 met. The four cells the wave is for: −0.0028 / +0.0044 /
−0.0087 / −0.0044 (from −0.0122 / −0.0040 / −0.0150 / −0.0101), three inside 0.005 and the
fourth inside the re-declared 0.01. The fold measured for the first time and missed both ways:
reduced transparency −0.0320 → −0.0281, increased contrast +0.0096 → +0.0139 (the carriers'
own +0.004 each; no second mechanism in this wave). S5 on one cell by 0.0005 (`rrect-sm` 1x; the
form's one-signed over-prediction). Two cells cross W17's 0.01 line by a thousandth —
`checkerboard__capsule-button` 2x +0.0102 (predicted), `hc-text__capsule-button` 1x +0.0105 (not
predicted; the same family) — three leave it in the good direction, seventeen stand unmoved.
Three cells return to the shape axis. One bed cell (`hc-text__capsule-button` under increased
contrast, already excluded) becomes unmeasurable; the bed loses a row. The GPU tier
byte-identical 115 / 115; the knee unmoved; every suite green.

1. **Land as declared** (recommended). Both carriers; G2 rebuilds the bed once, re-records the
   floors (none may go down), takes four lines off `PREDICATE_EXCLUDES` and drops the profile's
   count, names in claims the fold's two misses, the two capsule cells over 0.01 by a thousandth
   with their mechanism, S5's one cell, the unmeasurable cell, and the stack's base. Why: the
   wave's purpose is met on the cells it was chartered for; every miss is either a mechanism this
   wave never had (the fold's 2.8× clause; the bounded remainder) or the model's, and none is a
   loss of structure; holding gains nothing on those misses.
2. **Hold for the fold.** Keep the branch until a second mechanism closes the reduced-transparency
   cell (−0.028, of which the shadow was 0.004) and the increased-contrast cell (+0.014). Why not:
   the fold's remainder is not the shadow's and needs its own measurement (the occlusion's single
   absolute value under the fold against the two-regime law; the drawn border's share under
   increased contrast); the three-up would stay 0.012–0.015 dark on the standard profiles
   meanwhile.
3. **Carrier A alone.** Rejected by the pre-check: it leaves −0.0099 / −0.0140 on the two 1x
   `toolbar-group` cells; carrier B is two thirds of the closure on a group.

Whichever lands, the fold's two cells, the capsule cells over the line, the remainder's bound,
the stack's base and the unmeasurable cell are recorded by name.

## Surprises & Discoveries

- **2026-09-05 (G0) — the owner is a thing the tier paints and re-reads, not a term it
  computes.** The host's `box-shadow` sits inside its own filter layers' sampled region;
  declining it moves the GPU tier by 0.00000 and the CSS tier by +0.0032…+0.0096.
- **2026-09-05 (G0) — the renderer's union is not implicated.** Its interior is flat to
  ±0.0002 across gaps 12–56; the tier saturates at 28, the shadow's reach, not at 16 or 24.
- **2026-09-05 (G0) — the stack's residual is on the checkerboard as much as on the photo**
  (−0.046 / −0.057 on the overlay); the Grounding's reading (iii) was a 23 % region's
  dilution; the owner is the renderer's unsampled white at α 0.665 on DOM-sourced groups.
- **2026-09-05 (G0) — `GlassEffectContainer(spacing:)` is the SDF smooth-union's
  `smoothness` verbatim**, one backdrop layer over the row, no separation threshold; the
  renderer's 16 is a difference in kind, recorded for its charter.
- **2026-09-05 (G0) — declining the charter's five terms makes the residual worse**
  (−0.0077 → −0.0189 on the lone circle); M1's candidates carry no share.
- **2026-09-05 (G0) — superposition misses on `light-solid__capsule-button`** by +0.0059 /
  +0.0065: the rim and the highlight clip at white on the reference there.
- **2026-09-05 (G0) — the 2x checkerboard `toolbar-group` was small by cancellation** (box
  −0.0068, neighbours −0.0062, the capsule itself +0.0094); the shadow's removal alone takes
  it to +0.0044.
- **2026-09-05 (G0) — the Screen Recording grant has lapsed**; the bed is committed and the
  capture waits on the user's hand. *Taken the same day after the user restored it.*
- **2026-09-05 (the probe) — the native capture reproduces to the byte across five days:**
  all five recorded twins are byte-identical to the canonical fixtures of 2026-08-31, through a
  re-granted permission; and the protocol's own attestation caught the one compromised run
  (HID activity, the window losing key on two cells), which was excluded and replaced.
- **2026-09-05 (the probe) — Apple's material is box-invariant at the 44 px span:** the lone
  circle within 0.001 of the capsule, the three-up the same at spacing 12 and 40; the merge
  changes nothing inside the members; only the CSS tier moves with the box.
- **2026-09-05 (G1 pre-check) — carrier B is two thirds of the closure on a group:** carrier A
  alone leaves −0.0099 / −0.0140 on the two 1x `toolbar-group` cells; a host's stacking context
  means only the group's last-painted member can paint after every member's filters.
- **2026-09-05 (G1 pre-check) — the remainder's sign flips with the scale:** M2's structure term
  is one-signed negative at 1x (three times larger on the small box) and turns positive on the
  2x checkerboard (+0.0076 on the capsule), which is where W17's 2x capsule miss (+0.0095) comes
  from; the spread is the signature (the tier keeps 0.278 of the structure on both boxes, the
  renderer 0.306 / 0.277, Apple on the renderer's side).
- **2026-09-05 (G1 pre-check) — the Design's spread arithmetic was wrong:** L3's box is the
  host's border box already; growing the spread by the border width would have grown every
  shadow. Caught by the worker before a pixel was measured with it.
- **2026-09-05 (G1 pre-check) — the stack's checkerboard base carries a shadow-over-glass
  composite term** (+0.0081 with the shadow on both tiers, +0.0029 with it declined on both) that
  the carriers do not touch: the two tiers darken a glassed body unequally under a shadow.
- **2026-09-05 (G1 dry run) — the fold's clause, measured for the first time, misses both
  ways:** reduced transparency improves by a tenth of itself (−0.0320 → −0.0281) and increased
  contrast worsens (+0.0096 → +0.0139); the carriers move each by +0.004 and the rest is not the
  shadow's.
- **2026-09-05 (G1 dry run) — three cells return to the shape axis:** the shadow's removal
  lifts the light-solid cells +0.002…+0.004 off the background the extractor could not separate
  them from at W17; `PREDICATE_EXCLUDES` goes down by three (and by one more for an unmeasurable
  cell). Coherence with the renderer gave the instrument back part of what it took.
- **2026-09-05 (G1 dry run) — the closed form over-predicts one-signed on every single-member
  cell** (forty-two misses, −0.0001…−0.0033): the canvas clamp and the device-grid coverage both
  err toward more shadow than the engine paints. The form's property, recorded.
- **2026-09-05 (G1 dry run) — a bed cell became unmeasurable:** `hc-text__capsule-button` under
  increased contrast, already the most degenerate cell (IoU 0.470, three bodies) and already
  excluded; the bed loses a row at the landing.
- **2026-09-05 (G1 dry run) — a second cell crosses the 0.01 line the pre-check did not
  predict:** `hc-text__capsule-button` at 1x, +0.0091 → +0.0105, the remainder's family on a
  third backdrop.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-05: v1 — chartered from W17's Deferred entry and claims §5.75 §7 on the
  user's pick after 0.7.0; grounded on the W17 bed, W17 G1's diagnosis, the scene
  builder's union and stack routes, the renderer's union parameters and Filter
  Effects 2's mirror rule; G0 dispatched on Decision Log 1's recommendations.
- 2026-09-05: Decision Log 1 executed by the user at the recommendations (q0–q5); the
  target rule's qualification removed; the Tracking Map's G0 row amended.
- 2026-09-05: G0 closed (claims §5.77); Decision Log 2 — the Purpose corrected beside, the
  Grounding's reading (iii) corrected beside, the Design's mechanism bullet added and M1–M5
  carrying G0's verdicts, G1 rewritten on the attribution with a pre-check gate, X7
  restated, Deferred extended (the renderer's unsampled route, the union's kind, the native
  pixels, the 2x capsule), eight Surprises; G1 dispatched.
- 2026-09-05: the probe bed captured and read after the grant (claims §5.77 §6, `probe/readings.md`);
  two Surprises, the Tracking Map's G0 row and Deferred amended; the spread signature passed to G1.
- 2026-09-05 (by G1's pre-check, an advisory overturn): the Design's corrected bullet said carrier
  A grows the shadow's `spread` by the border width; it does not — L3's box is the host's border
  box (`layerFrame` insets by the border width from the padding box) and inherits its radius;
  no growth applied. Evidence: the unit tests pin L3's value against the resolved material's.
- 2026-09-05: Decision Log 3 — the pre-check read, both carriers accepted, the remainder bounded
  per box and scale, S4 and S5 re-declared, the stack's clause restated; four Surprises, two
  Deferred shapes; the whole-bed dry run opens.
- 2026-09-05: G1 DECLARED (claims §5.78); Decision Log 4 — the landing question put to the user
  with the recommendation; five Surprises from the dry run; the Tracking Map's G1 row COMPLETE.
