# W30 — the operator wave: the span-graded shadow and the scale-selective scatter, under one exemption

**Status: CLOSED 2026-09-20 by G4's landing, against all seven Parent-Level Acceptance clauses
(Outcomes & Retrospective); 0.20.0 PREPARED, UNPUBLISHED — `pnpm release` is the user's hand and
the tag follows it.** Chartered 2026-09-20 (the parent, on the user's word "operator wave first,
and rest on your judgement" after the 0.19.0 publish); adversarially reviewed the same day and the
review folded (Revision Notes). Executes W29 Decision Log 7 (a) and W29 Deferred item 1. Grounded
on main at `4a4c941a` (0.19.0 published).

**0.20.0 PUBLISHED 2026-09-21, by the user's `pnpm release` on `484ec8a4` (the parent's final
chain record, the head at publish); tag `v0.20.0` annotated on that commit and pushed by the
parent the same day.** Registry: web 00:11:11.292Z, react 00:11:12.250Z, core 00:11:30.688Z — the
record beside the "PREPARED, UNPUBLISHED" status above, as the 0.19.0 record sits in W29; the
verification is in §Outcomes & Retrospective.

## Purpose

macOS 27 changed two things in Apple's material that the operators vitrea has cannot express, and
0.19.0 ships both as the best single compromise its constants admit.

The first is the outer shadow's blur. On macOS 26.5 it was span-invariant — a positive measurement,
σ within 15.4–15.9 CSS px across spans 32–160, recorded in `MaterialOuterShadow`'s own header — and
`sigmaPx` is one constant the shader reads from a uniform. On macOS 27 the blur is linear in the
casting span above span 96 (σ_css ≈ 0.133 · (span − 30), holding to 0.1–0.5 % at 1x and 1.7–6.6 %
at 2x; claims §5.154 §4 as corrected) and nearly constant in DEVICE px below it. 0.19.0 fits the
thick regime and ships the thin cells' shadow **5.97× too wide at 1x and 2.80× at 2x**, carrying the
right energy in the wrong shape — the amplitude anchors fitted beside the one σ absorb the energy
error (departure residual 0.0007), which is why the departure metric does not show it. The casting
surface's span is already in the shader one argument away from the σ uniform, and the CSS tier
already emits one `box-shadow` per surface with the span in scope.

The second is the diffusion. At the fitted point the light interior's spread reads **+0.044 over the
16 px checkerboard and −0.028 over both a finer (4 px) and a coarser (photograph) backdrop** (claims
§5.153 §6): Apple's material passes less structure than vitrea at one pitch and more at both sides of
it, which a positive mix of two Gaussians — monotone in frequency — cannot do at once. And the residual
changes sign with the colour scheme: on `checkerboard__rrect-md__rest` the WebGPU tier passes
**1.77×** the native structure in light and **0.55×** in dark, the CSS tier 1.04× and 0.32×
(§5.154 §9 (c); the tracker's "two tiers miss the backdrop's structure in opposite directions"). A
scatter fitted on the light bed alone lands on the wrong side of the dark one. Those four figures
are the **sheets'** instrument — 0–255 luminance over the component's box inset 12 CSS px — and the
matrix metric reads the same four cells 1.567 / 0.749 / 0.968 / 0.355, crossing 1.0 on the light CSS
reading where the sheet does not; claims §5.156 §3 tables the two beside each other and says which
one a test can pin, and B4 and `tier-coherence.test.ts` are written on the matrix's. Three of the seven
rows 0.19.0 records as missed sit on the shadow's reach at the largest spans and on this residual.

Both operators add leaves to the renderer's `DEFAULT_MATERIAL_PROFILE`, and every shipped document's
`resolvedMaterialSha256` is a digest over the FULLY RESOLVED material — so both move the frozen
macOS 26.5 pair's digests even though no macOS 26.5 pixel moves. That is why the user ruled them one
wave under a **single one-time X1 exemption** (W29 Decision Log 7 (a)), the class W29 Decision Log
1 (i) reserved, and why chartering them apart would spend two. The review of this charter found the
shape that spends the exemption without touching a frozen byte: the macOS 26.5 documents stay
byte-identical and the digest their pin now resolves to is recorded BESIDE them, once (Design).

This wave also does two things the re-read makes unavoidable. `results/matrix.json` is **72.1 MB**,
one recapture from GitHub's 100 MB refusal, and this wave's read appends about 455 rows; the
generation split G4 recommended is executed here, before the read, because this is the recapture
that would otherwise cross the limit. And the operators change the shadow's reach and the effective
blur width, which are what `outerShadowReachPx` and the CSS sampling pad are computed from, so the
padding is touched deliberately and the `GlassToolbar` seam the G4 review found is closed on the way.

What this wave does **not** do: it does not touch the chromatic transmission (W29 Decision Log
6 (c); the four dark `photo__rrect-lg` misses are not the operators' to claim, and a scatter fit that
appears to move them is a warning sign, not a result); it does not build the highlight's angular
reader; it does not fix `compare`'s decoupled-contrast flag mid-wave (that would confound the contrast
profiles' rows between the two reads); it does not re-open the level law's abscissa; and it captures
**no native pixel** — every fixture it fits on, the whole pitch ladder included, is on disk from W29.

## Parent-Level Acceptance

1. **The exemption is one commit, touches no frozen byte, and is proven pixel-inert on both tiers.**
   Before any leaf lands, the fully resolved macOS 26.5 light and dark materials are written to disk
   as JSON and committed as evidence. The wave's new leaves land in ONE commit (child G2) at inert
   defaults that are **algebraic identities** (a multiplied zero, an added zero, a σ law whose output
   is `sigmaPx` at every span) and nothing else. That commit does not edit either macOS 26.5 document
   or the seed: it writes `packages/calibration/profiles/digest-supersessions.json`, one record per
   macOS 26.5 document naming the document's recorded `resolvedMaterialSha256`, the digest the pin
   resolves to after the leaves, the leaves added, this Decision Log and the date; the pin tests read
   the current digest from that record and still assert the document's own field is the recorded
   one; `material-document.ts` and `window-activation.spec.ts` report the current digests because
   they name what actually draws. Proofs, all before any fit exists: `freeze.py verify` intact at
   **1,818 with nothing exempted**; the identity test (each macOS 26.5 document's resolved material
   minus the named leaves deep-equals the committed pre-wave JSON); the 34 renderer goldens
   byte-identical; a case that the CSS tier's declarations (`box-shadow` string, blur radius, every
   emitted property) are character-identical across a span sweep at the macOS 26.5 documents before
   and after; a unit case that each inert law returns exactly the pre-wave value over a sweep; and
   the gated macOS 26.5 row count in `adopted-thresholds.test.ts` pinned at **1,107** across the
   commit — `atAShippedDocument` hashes the documents' bytes, so an edited document would empty the
   frozen bed out of every bound, which is the failure this shape exists to avoid. The exemption is
   spent once; no later wave adds a record without a new grant.
2. **The structure is measured before the operator exists.** From committed evidence only — the
   native delta's `shadowFalloffSigmaPx` per cell and the matrix's `interiorStdDev{Native,Web}` per
   cell — G0 tables the shadow's σ per span per scale per scheme (the statistic named: which cells,
   which order statistic, which non-converged fits excluded, at which scale, with the spread) and
   the body's structure ratio per pitch per scheme per tier, on the gated sets and on the probe
   ladder separately, and names from those tables the smallest operator shape each law needs. The
   CSS tier's own attenuation goes into `tier-coherence.test.ts` as a measured residual before any
   fit.
3. **Bounds before reads; the targets named with their levers.** The 27 profiles' adopted tables stay
   at the values W29 Decision Log 4 ruled; no floor is adopted. G0 declares, per operator, the wave's
   own acceptance — a tolerance on the fitted σ against the native σ per span class at both scales
   with the statistic it is read by, and a tolerance on the structure ratio per pitch per scheme on
   the WebGPU tier with the CSS tier recorded — and says, per tolerance, whether it becomes an adopted
   row at G4 or stays a one-wave reading. It declares the **departure residual** the joint shadow fit
   must hold at or better than (0.0007 bed-wide) as a stop condition. It names which of the seven
   `MISSED_27_ROWS` the wave claims and through which operator on which tier: the two 1x-light dom
   `ssimMean` rows at spans 160 and 130 are the shadow's (the shadow mirrors fully onto the CSS tier;
   the scatter reaches `dom` only as a scalar), and the reduced-transparency `ssimOutside` row is
   "reachable if the law extrapolates", because its native σ is read on the holdout cell itself. The
   four dark `oklabDeltaEP95` rows are declared **expected unmoved**, and the reduced-transparency
   body-structure residual (native sd 0.43 against WebGPU 3.49) is declared **reported, not claimed**.
4. **Both operators land on the fidelity target with the CSS tier derived in the same commit, and the
   shadow is refitted jointly.** The shadow's σ graded by the casting span — the law is per caster:
   the GPU tier reads the caster's span per pixel from `shadowAux.z`, the CSS tier emits one blur
   radius per surface, and the group clip reach and the sampled shadow factor are the max over members
   and are bounds, pinned as such — with the six occlusion anchors and `liftAmplitude` of the macOS 27
   documents refitted **jointly** with it (they carry the compensation for the wrong σ today, and
   `thickOcclusionAt160` is derived rather than fitted exactly where σ moves most), the receded
   documents' inherited block moving with them. The scatter made selective in the backdrop's spatial
   scale on the WebGPU tier, with "conditioned by scheme" meaning two values of one leaf in the light
   and dark documents (the dark document is a patch; the renderer has no scheme input), the CSS
   tier's single `backdrop-filter` given the best scalar projection and its residual recorded;
   `sizeToneLevelFar` fitted in the 27 documents if the ladder gives it a stable sign (a leaf already,
   default 0, named by no document, a free lever — and NOT added to `tuned-profiles.test.ts`'s
   `FITTED_CONSTANTS`, which is asserted over the frozen macOS 26.5 light patch). The macOS 27
   documents re-sealed; `tier-coherence` green; the reach and both sampling pads recomputed.
5. **Read once per frozen configuration.** Scratch matrices during the fit with the holdout dropped
   in the reader by construction; then, with the documents sealed and their hashes in the ledger, the
   canonical run appended beside the 0.19.0 rows — six profiles, two tiers, calibration + validation,
   about 13 minutes — and the holdout read **once**. The verdict per profile per tier per clause with
   every missed cell named; a miss is recorded, not widened, not re-fitted; every passing tolerance
   G0 marked for adoption is carried into `adopted-thresholds.test.ts`.
6. **The evidence layout is ruled and holds at the wave's close.** `results/matrix.json` holds one
   generation per profile — the frozen macOS 26.5 rows unchanged and in their order, and per macOS 27
   profile the rows at the shipped documents — and superseded generations live in
   `results/superseded/<document-sha>.json` with a listing that names each by the document it was
   read at. G1 moves the generation superseded today; G4 moves the generation its own read supersedes,
   after the append-check, so the invariant is true at close and not only at G1. The freeze's 1,107
   row hashes verify against the working file throughout. Every reader of the matrix (`cli/compare.ts`,
   `cli/diff.ts`, `test/adopted-thresholds.test.ts`'s `atAShippedDocument`, the demo's
   `calibration.ts`, `scripts/vibrancy.ts`) reads the generation by name; the demo's `capturedAt`
   tie-break is retired; `vibrancy.ts`'s recorded `matrixSha256` provenance gets the new digest
   recorded beside the old with what moved it.
7. **The landing.** The demo on the new operators with its tone stage re-ranged (Decision Log 1 (e));
   `GlassRootHandle` carries the selected document so `GlassToolbar` opens at its own material's
   blur, with the case the tracker names; the coverage matrix re-scored; `CLAUDE.md`, READMEs and
   CHANGELOG say what moved; sheets native | WebGPU | CSS | difference per profile at both scales
   with the thin spans first, because that is where the shadow is now read; the fixed group
   versioned **0.20.0** and prepared, `pnpm release` the user's hand.

## Grounding Baseline (main at `4a4c941a`, 0.19.0 published)

- **The fingerprint.** `fingerprint()` (`results/2026-09-19-w29-g3-refit/seal.ts`, duplicated in
  `test/tuned-profiles.test.ts` and `test/macos26-document-selection.test.ts`) is SHA-256 over
  `withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch)` with keys sorted, first 16 hex. Sites
  that name a resolved digest: the two macOS 26.5 documents' `resolvedMaterialSha256`
  (`b2b570e4adcea8fb`, `874be66ea501621b`) — frozen, entries 652 and 653 of the freeze, with the
  seed at 654, none of which this wave edits; the four macOS 27 documents (re-sealed by the fit);
  `material-document.ts`'s two hand-written 26.5 digests; `macos27-profile.ts`'s four;
  `window-activation.spec.ts`'s eight (four macOS 26.5, four macOS 27). Tests that go red at a new
  default leaf: `tuned-profiles`, `macos26-document-selection`, `macos27-profile-export`'s digest
  case, the `window-activation` spec, and `seal.ts`'s X1 loop. The goldens do NOT move —
  `isolation.spec.ts` renders an explicit patch and an inert leaf changes no pixel — and the 1,107
  frozen matrix rows do not move (G3b's append-check: 1107/1107, 0 changed).
- **Why the documents' bytes are load-bearing.** `adopted-thresholds.test.ts` builds
  `SHIPPED_DOCUMENT_HASHES` from the bytes of every file in `profiles/` and `atAShippedDocument`
  keeps only rows whose `capturePath` names a current hash; all 1,107 macOS 26.5 rows name
  `6a9600720477` / `950ce1c3e917`, the frozen bytes. An edit to either document — a re-recorded
  digest, a history comment — empties the macOS 26.5 half of every bound, floor and predicate, and
  the file says so in its own comment. This is what rules the exemption's shape.
- **The leaf plumbing a new leaf must pass.** `withMaterialOverrides` (`material.ts`) is an explicit
  per-leaf merge, so a leaf without its own line resolves silently to base;
  `scripts/material-profile-file.ts`'s `MATERIAL_PATCH_KEYS` and `OUTER_SHADOW_KEYS` are allowlists
  that REFUSE an unknown key, so a document naming an unregistered leaf is refused by `compare` at
  fit time; the CSS tier's mirror of the material slice lives in `platform-web/src/optics.ts` and is
  pinned by `tier-coherence.test.ts`. All three are in the exemption commit's scope.
- **The shadow operator.** `MaterialOuterShadow` (`material.ts:361–541`): `offsetPx`, `sigmaPx`,
  `spreadPx`, three thin and three thick occlusion anchors (`thickOcclusionAt160` derived, not
  fitted), four lift constants, the reduced-transparency flattening, `sizeGain`. In the shader
  `outer_shadow_thick(spanCss)` already interpolates the AMPLITUDE through 96/128/160 and the
  caster's span is `shadowAux.z`, read per pixel; the falloff is `outer_shadow_falloff(…, ou.shadow.y)`
  with `ou.shadow.y` the one σ uniform. `shadow`, `shadowSize` and `shadowThick` are all
  four-components-full, so a σ law needs a new uniform. `outerShadowReachPx(shadow, occlusion)`
  bisects on `shadow.sigmaPx` and must take a span; `renderer.ts` maxes occlusion over surfaces and
  must max the REACH. CSS: `outerShadowDeclaration` emits `box-shadow` with blur `2σ` through `px()`
  rounding, called per surface with `surface.spanPx` in scope; the group-shadow clip reach in
  `root.ts` and `sampledOuterShadowFactor` read one σ per group today. The instrument exists:
  `metrics/shadow.ts` fits one `falloffSigmaPx` per cell per direction as a blurred edge against an
  exponential alternative and reports both residuals; on a mixed-span composite (`glass-over-glass`
  at span 130, `toolbar-group`) it is no longer a single-parameter quantity, and G0 says what it
  means there.
- **The law as read** (§5.154 §4, bed-wide medians, CSS px; cell count in brackets):

  | bed | 32 | 44 | 96 | 128 | 130 | 160 |
  | --- | ---: | ---: | ---: | ---: | ---: | ---: |
  | 1x light | 4.06 (4) | 1.52 (22) | 8.80 (16) | 13.14 (8) | 13.36 (2) | 17.30 (13) |
  | 2x light | 2.38 (8) | 1.93 (25) | 9.36 (16) | 13.30 (8) | 13.58 (2) | 17.58 (13) |
  | 1x dark | 2.05 (3) | 1.54 (14) | 8.87 (10) | 13.19 (5) | 13.42 (1) | 17.45 (11) |
  | 2x dark | 1.89 (7) | 2.85 (14) | 9.38 (10) | 13.42 (5) | 13.74 (1) | 17.68 (11) |
  | 1x reduced transparency | — | 1.50 (5) | 8.59 (2) | — | — | 16.97 (1) |

  Above 96 every scale and scheme agrees to a few percent; below 96 the per-cell spread is 1.11–4.08
  at 1x light and 0.57–9.70 at 2x light, the span-32 column rests on three or four `rrect-sm` cells
  (one reads 157.7), two `checkerboard-64` cells read 74.3 where the fit finds no width, and the
  quoted span-44 cells read 1.84 at 1x against 3.92 at 2x — a ratio of 2.13, the device pixel ratio.
  Whether the thin regime is Apple's material or the instrument's limit (two or three rings above the
  body's own edge at σ ≈ 1.8) is not settled by this bed, and a ratio acceptance against a median
  whose cells disagree by 9× is unfalsifiable: the acceptance must name its statistic. The reduced-
  transparency span-160 figure (16.97) is `photo__rrect-lg__rest`, the holdout cell itself and the
  only span-160 cell that profile carries.
- **The scatter operator.** Flattened into `MaterialProfile`: `sizeScatterGainMax`, `sizeScatterFloor`,
  `sizeScatterSpanMax`, the 2x trio, `sizeScatterGainFar2x`, six ramp starts and two reaches, the
  two declined thick-share lifts, `sizeHeavyTapSigma{,2x}`; all gated by
  `sizeThickness = smoothstep(32, 96, span)`. GPU mechanism (`wgsl/optics.ts:855–897`): one body
  sample, one chain sample at `scatterLod = clamp(bodyChainLod + log2(gain), 0, maxLod)` — replaced
  by the dedicated `backdropHeavy` texture behind `ou.heavyTap.x > 0.5` where `sizeHeavyTapSigma` is
  set — then `mix(body, scatter, kScatter)`. The heavy texture is built per SOURCE before any group
  draws, so a second heavy tap at its own width is a second separable build and a second binding,
  not a uniform leaf (0.070 ms per build, W26 Decision Log 2 (b)); chain mips are 13-tap platykurtic
  low-passes rather than exact Gaussians. The analysis pass already computes mean, variance and edge
  density per source, which fits an operator conditioned on backdrop scale (a per-source quantity).
  CSS: `blurRadius = source.blurSigma · blurSigmaScale` (2.2 on macOS 27); the tier does not mirror
  `sizeHeavyTapSigma` and has no backdrop-frequency statistic, so a selective law can only be
  projected onto a refitted scalar there — and on the light bed the CSS tier already reads 1.04× the
  native structure where WebGPU reads 1.77×, so a scalar refitted to carry a WebGPU operator can move
  a `dom` row the wrong way.
- **The bed.** Each of the four macOS 27 STANDARD profiles carries 45 pitch-ladder fixtures
  (`checkerboard-4/8/32/64`, `checkerboard-lc16`, `hc-text-7/28`) — **every one of them `probe`**, 0
  in calibration, 0 in validation, 0 in holdout; the two accessibility profiles carry **5** ladder
  fixtures each, so scale-selectivity is not identifiable on them. The gated sets carry the 16 px
  checkerboard, `hc-text` (14 px rows), `photo`, `impulse` and the solids: 37 calibration /
  12 validation / 20 holdout distinct scenes, 8 recorded, 91 probe. The operator is fitted on probe
  rows and judged on three distinct pitches; no native capture is needed.
- **The seven missed rows** (`MISSED_27_ROWS`), all holdout, all `dom` but two. Unreachable by these
  operators: the four dark `photo__rrect-lg__rest :: oklabDeltaEP95` rows (chromatic; the tone solve
  is achromatic by construction). Reachable: `checkerboard__rrect-lg__rest :: ssimMean` 0.88402 and
  `checkerboard__glass-over-glass__rest :: ssimMean` 0.89538 on 1x-light dom (bound ≥ 0.9) — spans
  160 and 130, where the shadow's σ moves most and mirrors fully onto the CSS tier; and
  `photo__rrect-lg__rest :: ssimOutside` 0.82707 on reduced transparency dom (bound ≥ 0.83), scored
  OUTSIDE the silhouette at span 160, the single row the G3b refit worsened (0.82736 → 0.82707), and
  the cell whose own native σ is the profile's only span-160 reading.
- **The recede.** On macOS 27 the recede keeps the outer shadow (§5.154 §5), the receded documents
  carry their active document's `outerShadow` block leaf for leaf, and the receded pose's far-exterior
  difference at span 160 is 17.42 (WebGPU) / 15.89 (CSS) against ≤ 5.92 on any active strip — the old
  halo, still there, on the pose whose shadow the σ law re-shapes at exactly that span (tracker: "The
  macOS 27 recede's exterior is unfitted above span 96"). The law is expected to narrow it, since the
  block is inherited; it is reported on the inactive holdout rows, not fitted, because no non-holdout
  inactive cell above span 96 exists. No bound is gated on the inactive pose.
- **The cost of a read.** G3b's like-for-like precedent: calibration + validation 9:17 wall clock
  (332 rows), holdout 3:50 (123 rows) — **about 13 minutes and 455 rows**, 0 changed, 0 missing,
  the 26.5 half untouched. `canonical-read.sh` hard-codes the four sealed document hashes and refuses
  any other bytes, and nothing under `results/` is edited after commit — so G4 writes its own copy,
  inheriting the refusal, the `pgrep` exclusivity check and the RT/IC/slider reads verbatim. The
  12 h 49 m figure in W29 is the native sitting, which this wave does not repeat.
- **The matrix.** 72,102,187 bytes over 2,017 rows: 1,107 macOS 26.5 (≈39 MB) and two macOS 27
  generations of 455 (≈16.5 MB each). Removing the superseded generation leaves ≈55.7 MB; this
  wave's read appends 455 more and makes the G3b generation superseded in turn, so the layout must
  move again at G4 or the file is back at 72 MB at close. Readers: `cli/compare.ts`, `cli/diff.ts`,
  `test/adopted-thresholds.test.ts` (`atAShippedDocument` lives there, not in `gates.ts`), the demo's
  `calibration.ts` (`reportsFor` breaks the generation tie on `capturedAt` and says so), and
  `scripts/vibrancy.ts`, which also records a whole-file `matrixSha256` in its committed provenance.
  `gates.ts`, `report.ts` and two tests carry the path in strings and comments only. `freeze.py`
  hashes each 26.5 row by canonical content but labels entries with a positional counter in file
  order, so the rows' relative order must be preserved.
- **The padding.** `samplingPaddingFor` gained `profile` and `cssTierMapping` at W29 G4; `GlassToolbar`
  cannot pass either and opens at the default document's blur (2.2× over-padding on a page selecting
  macOS 26.5 — safe direction, wrong number). The tracker's first fix shape: carry the selected
  document on `GlassRootHandle` beside `root`, `ticker` and `profile`.
- **The tone stage.** Three plates at 40/68/112 px over a ground slider to near-black; on macOS 27
  the plates sit within 0.016 of each other and ~100× above the ground at the dark stop, where the
  separation the stage exists to show is plain over the bright half instead. G4 made the prose and
  the two e2e cases honest and left the geometry.
- **The holdout drop.** `shadow-table.py` drops holdout rows in the reader; `fit.py table` does not.
  The fix shape is the drop in `fit.py`'s `readings()` with the count printed and a `--with-holdout`
  flag for the canonical read.

## Design (advisory unless marked)

**The exemption's shape (ruled, Decision Log 1 (a)) — supersession beside the document.** The macOS
26.5 documents and the seed stay byte-identical. `packages/calibration/profiles/digest-supersessions.json`
records, per macOS 26.5 document: `profileKey`, `recordedSha256` (the document's own field, the
reading it was sealed at), `currentSha256` (what the pin resolves to over the default that now carries
the leaves), the leaves added, the Decision Log and the date. `tuned-profiles.test.ts` and
`macos26-document-selection.test.ts` assert three things: the document's field equals the record's
`recordedSha256`; the resolved fingerprint equals the record's `currentSha256`; and the resolved
material minus the named leaves deep-equals the pre-wave JSON. `material-document.ts` reports
`currentSha256` for the macOS 26.5 endpoints because `root.material` names what actually drew. Five
shapes were weighed. Re-recording the digest in place with history — this charter's first draft —
edits the frozen documents' bytes, which `atAShippedDocument` hashes, and so would empty the macOS
26.5 bed out of every bound (Grounding); it is withdrawn. A second digest field in the document edits
the same bytes. A fingerprint over only the leaves a schema version knows, and a fingerprint-excluded
section, avoid the exemption by making the pin blind to the new leaves in the frozen documents, where
they must stay inert forever — a default that can then change without any document being
re-recorded, which is the `sizeOcclusionGain` failure `tuned-profiles.test.ts`'s comment was written
after (the review notes the covered leaves would still be caught; the objection is to the uncovered
ones). Supersession beside the document costs zero freeze entries, keeps every frozen byte, keeps
the reading in the document as the reading, and puts the current digest where a person and a test
can both find it. It is still the exemption the user granted — the pin's meaning gains one
indirection, recorded once — and no later wave adds a record without a new grant.

**The exemption's timing (ruled, Decision Log 1 (b)).** Its own child, G2, merged and reviewed before
any fit opens: every new leaf of both operators at algebraically inert values, the supersession
record, the digest sites, the plumbing (merge line, allowlists, CSS mirror), and the proofs of clause
1 — all verifiable without a fit. G0's cut must settle the LEAF SHAPE before G2 opens — the number
and meaning of the leaves, not their values. Where G0's tables cannot choose between the scatter's
two candidates, G2 lands a leaf set that **spans both** at inert values (a second heavy width, its
signed weight, and a scale-conditioning gain keyed on the analysis pass's per-source statistics), the
idiom the project already uses for leaves inert by decision (`sizeGain`, `sizeToneLevelFar`, the two
declined thick-share lifts), so that no second exemption is needed mid-fit. A second heavy tap is a
second texture build and binding: it is gated on its weight leaf, so the off path costs nothing and is
what the goldens prove, and the on path is proven by a `test:gpu` case at a nonzero weight and by the
sealed read.

**The shadow's σ law (advisory).** σ_css(span, dpr) as a clamped line: `sigmaSlope · (span − sigmaSpan0)`
above a knee, held at a floor below it, with the floor expressed in device px if G0's cut confirms the
thin regime is nearly constant there (the 2.13 ratio) and in CSS px if it does not. Inert defaults:
slope 0, floor = `sigmaPx`, so σ(span) === `sigmaPx` identically. The law is **per caster**: the GPU
tier evaluates it per pixel from the caster's span in `shadowAux.z`, the CSS tier per surface from
`surface.spanPx`; the group clip reach and `sampledOuterShadowFactor` take the max over members and
are bounds on it, and `tier-coherence` pins all three to one law. The thin regime's reading has a
wide instrument error and the charter does not require the thin cells to be FITTED — it requires them
to be no longer 2.8–7.2× too wide by a statistic G0 names, on non-holdout cells, with the holdout
cells' native σ reported beside as a check. The six occlusion anchors and `liftAmplitude` are
refitted jointly with σ and the departure residual is the stop. The reach takes the span; the
renderer maxes the reach over surfaces; the CSS tier's blur radius is per surface.

**The scatter (advisory, the shape G0's cut names).** Two candidates and G0 chooses on the tables:
(i) a second heavy tap at its own width with a signed weight, which makes the kernel non-monotone in
frequency and is what a notch needs; (ii) a mix that is a function of the source's measured spatial
scale (the analysis pass's variance and edge density) rather than of the span alone. Scheme
conditioning is two values of one leaf in the light and dark documents. The accessibility profiles,
with five ladder rungs, inherit the 1x-light standard document's scatter values rather than a fit of
their own, and the reduced-transparency body-structure residual is reported. G0 also tables
`sizeToneLevelFar`'s conditioning on the probe ladder in both schemes; if the macOS 27 ladder gives it
a stable sign it is fitted in the 27 documents at no exemption cost. The CSS tier gets the best scalar
and its residual in the ledger, per the tier rule (Decision Log 23 of 2026-09-05, quoted in
`CLAUDE.md`: a material change lands on the target and the CSS tier carries what its two layers can);
a signed lobe that no metric on the bed reads is looked for by eye on the sheets (ringing at a
contour is what to look for) and named if seen.

**The matrix's generation split (ruled, Decision Log 1 (d)).** Split by generation. The working file
keeps one generation per profile — the frozen macOS 26.5 rows unchanged in place and in order, and
the macOS 27 rows read at the SHIPPED documents — and every superseded generation goes to
`results/superseded/<document-sha>.json`, pretty-printed as before, with `results/superseded/README.md`
listing each file by profile, document hash, the claims section that read it, and the date. "Which
generation is the shipped one" becomes a name; `atAShippedDocument` becomes a lookup; the demo's
`capturedAt` tie-break is retired; a superseded row is still one `git show` away. Executed by G1
before G2, and again by G4 for the generation its own read supersedes.

**The tone stage (ruled, Decision Log 1 (e)).** Re-range. The stage was built to make a size-gated
separation visible, and on macOS 27 that separation exists over the bright half of the slider and
closes at the dark end; so the slider's resolution moves to where the plates separate, with the
near-black stop kept as the last position so what macOS 27 does there — no convergence — remains one
drag away and the prose G4 wrote stays true. Not retired, because the behaviour it demonstrates is
still real; not re-subjected to the curve, because a demo of a curve is a chart and this is a
material site.

**Padding, deliberately.** G3 recomputes `outerShadowReachPx` from the σ law (max over surfaces) and
the CSS sampling pad from the effective blur; G4 carries the selected document on `GlassRootHandle`
and passes it through `GlassToolbar` (the additive, local fix shape), with the case: a React toolbar on
`macos26MaterialProfileDocument` whose gap equals the macOS 26.5 padding rather than 2.2× it. Whether
`samplingPaddingFor`'s core advisory constant should be retired is NOT decided here; the tracker entry
stays open with this wave's numbers added.

**The holdout drop, by construction.** G0 moves the drop into `fit.py`'s `readings()` with the count
printed and a `--with-holdout` flag, so every reader this wave and later waves build inherits it.

## Children

### G0: The cut and the declarations — no material change

*Opens on main. Read-only on the material; writes evidence, tables, tests and declarations.*

- (a) Write the fully resolved macOS 26.5 light and dark materials to
  `results/2026-09-20-w30-g0-cut/resolved-26.5-{light,dark}.json` (through the same
  `withMaterialOverrides` path the fingerprint uses, keys sorted; prove each file's fingerprint
  equals the pinned digest) and commit them before anything else. Add the identity test with an
  empty `W30_OPERATOR_LEAVES` list and the gated-26.5-row-count pin (1,107).
- (b) The shadow cut: from `results/2026-09-19-w29-g2-native-delta/native-delta.json` and the
  G3b rows, σ per span per scale per scheme per backdrop class with the per-cell spread and count,
  on the gated sets and on the probe ladder separately, at both scales, with the statistic named
  (which cells, which order statistic, which non-converged fits excluded); the instrument's meaning
  on mixed-span composites stated; the thin regime's device-px hypothesis tested on the cells that
  carry it; the reach the shipped constant implies against the reach the law implies at spans
  32/44/96/128/160. Name the σ law's leaf shape and each leaf's inert identity.
- (c) The structure cut: `interiorStdDev{Native,Web}` per pitch (4/8/16/32/64, lc16, hc-text 7/14/28,
  photo, solids) per scheme per tier per span, active and inactive, from the committed matrix — the
  tracker's precondition. Name the scatter's leaf shape from it, or say the tables cannot choose
  between (i) and (ii), in which case G2 lands the spanning set. Table `sizeToneLevelFar`'s sign on
  the macOS 27 ladder in both schemes.
- (d) Carry the CSS tier's measured attenuation into `tier-coherence.test.ts` as a recorded residual
  (the numbers from (c), recomputed), so the fit does not discover it.
- (e) Declarations, committed before G2 opens (clause 3): the tolerances with their statistics and
  their intended fate; the departure-residual stop; the claimed rows with lever and tier; the
  expected-unmoved rows; the reported-not-claimed residual; the 27 tables unchanged (cited from
  `adopted-thresholds.test.ts`, never transcribed); no floor.
- (f) The holdout drop in `fit.py`'s `readings()`, count printed, `--with-holdout` for the canonical
  read; `shadow-table.py` reads through it.
- Ledger: **§5.156**. Evidence: `results/2026-09-20-w30-g0-cut/`.

### G1: The matrix's generation split — parallel with G0, merged before G2

- Execute Decision Log 1 (d): move the superseded macOS 27 generation out of `results/matrix.json`
  to `results/superseded/<document-sha>.json` with the README listing; the working file holds the
  frozen macOS 26.5 rows unchanged and in their order (the freeze's 1,107 row hashes verify against
  it) and one macOS 27 generation per profile; every reader names the generation rather than the
  timestamp (`cli/compare.ts`, `cli/diff.ts`, `adopted-thresholds.test.ts`'s `atAShippedDocument`,
  the demo's `calibration.ts`, `scripts/vibrancy.ts`), with the path strings in `gates.ts`,
  `report.ts` and the two tests checked; the demo's tie-break retired and its comment rewritten;
  `vibrancy.ts`'s committed `matrixSha256` provenance given the new digest beside the old; an
  append-check that proves every moved row is byte-identical in its new file, no row was lost, and
  the retained rows' order is unchanged. The split script reusable by G4. File sizes before and after
  in the ledger.
- Ledger: **§5.157**. Evidence: `results/2026-09-20-w30-g1-split/`.

### G2: The leaves — the exemption spent, its own gate

*Opens after G0's declarations are committed and G1 is merged.*

- One commit of substance: every new leaf of both operators (or the spanning set) at algebraically
  inert values, in `MaterialProfile`, `withMaterialOverrides`, the allowlists, the CSS mirror, the
  uniform layout and the shader with the law evaluating to the pre-wave value; the supersession
  record; the digest sites (`material-document.ts`, `macos27-profile.ts` regenerated,
  `window-activation.spec.ts`, the four macOS 27 documents re-sealed with the prior digest in their
  history); the identity test's leaf list filled; the CSS declaration-identity case; the inert-law
  unit cases; a `test:gpu` case for the gated heavy path's on state. Proofs: `freeze.py verify` at
  1,818 with nothing exempted; goldens 34/34 byte-identical; the 1,107 pin; the full chain green.
  README paragraphs for the new leaves.
- Ledger: **§5.158**. Evidence: `results/2026-09-20-w30-g2-leaves/`.

### G3: The operators — the shadow first, then the scatter

*Opens after G2 is merged and reviewed.*

- (a) The shadow: the σ law's values, the six occlusion anchors and `liftAmplitude` fitted jointly
  on the calibration set per profile on scratch matrices through the reader with the holdout dropped,
  the departure residual held at or under the declared stop, checked on validation; the receded
  documents inheriting the block; `tier-coherence` green; the 27 documents re-sealed.
- (b) The scatter: the shape G0 named, two values per scheme-conditioned leaf across the light and
  dark documents; the accessibility profiles inheriting; the CSS tier's scalar projection with its
  residual measured; `sizeToneLevelFar` fitted or declined with the reason; fitted on calibration +
  probe rows, checked on validation; the increased-contrast-coupled profile as W29 Decision Log 5
  placed it.
- (c) Padding: `outerShadowReachPx(shadow, occlusion, span)`, `samplingPaddingFor` and the CSS pad
  recomputed; the diagnostics that read them green; the smallest pad the laws produce at each span
  recorded.
- (d) `PREDICATE_EXCLUDES` and every count test moved to what the machine says; a changeset for the
  fixed group (a `@vitreajs/vitrea-web` minor at least); the sheets at the fit's read by eye, with
  ringing at contours looked for and named.
- Ledger: **§5.159**. Evidence: `results/2026-09-20-w30-g3-operators/`.

### G4: The sealed read, the verdict, and the landing — 0.20.0 prepared

- (a) RT and IC read 0, `NSGlassTintAmount` 0.5, one capture process, idle ≥ 60 s; the sealed
  documents' hashes in the ledger before the read; G4's own copy of `canonical-read.sh` at those
  hashes over six profiles × two tiers, calibration + validation appended beside the 0.19.0 rows;
  then holdout **once**. The append-check; then G1's split script moves the generation this read
  supersedes to `results/superseded/`, and the append-check again.
- (b) The verdict per profile per tier per clause against the unchanged 27 tables and G0's
  declared tolerances; the claimed, expected-unmoved and reported rows each named with before and
  after; every passing tolerance G0 marked for adoption carried into `adopted-thresholds.test.ts`;
  every miss recorded and a Decision Log entry drafted for the user where a ruling is needed.
- (c) The landing: `GlassRootHandle` carries the selected document and `GlassToolbar` passes it, with
  the tracker's case; the tone stage re-ranged with its cases moved against the committed reading; the
  demo's figures on the new operators; `CLAUDE.md`, READMEs, CHANGELOG; the coverage matrix re-scored;
  sheets with the thin spans first; the fixed group versioned 0.20.0, dry runs green, unpublished.
- Ledger: **§5.160**. Evidence: `results/2026-09-20-w30-g4-landing/`.

## Cross-Child Contracts

- **X1 — the freeze, intact, with the one exemption spent as a supersession record.** No macOS
  26.5-keyed path, row, bound, floor or document changes; `freeze.py verify` at every merge reports
  1,818 intact with nothing exempted; the identity test, the 34 goldens, the CSS declaration case and
  the 1,107 gated-row pin are the pixel proof; the supersession record is written once, in G2.
- **X2 — the cut precedes the operator.** G0 names each leaf shape from committed evidence before G2
  writes a leaf; G2 adds no leaf G0 did not name except the spanning set where G0 could not choose.
- **X3 — the operators change nothing outside the two named structures and what they are fitted
  jointly with**: the shadow's σ together with the macOS 27 documents' occlusion anchors and
  `liftAmplitude`, whose values compensate for the σ they were fitted beside; the diffusion's scale
  conditioning with two values per scheme; the leaf that already exists (`sizeToneLevelFar`). A fit
  that moves the four chromatic rows is reported as a warning, not claimed.
- **X4 — bounds before reads; holdout once; a miss is recorded** (as every wave). The reader drops
  holdout by construction from G0 (f) on; the σ law is fitted on non-holdout cells and the holdout
  cells' native σ is a reported check.
- **X5 — no native capture; the granted bundle is never rebuilt and nothing is added under its
  identifier.** Every fixture the wave fits on is on disk from W29.
- **X6 — RT and IC 0, the slider 0.5, one capture process, ≥ 60 s idle** before every browser run;
  every read recorded.
- **X7 — the evidence layout changes by one rule, applied twice**: G1 moves the generation superseded
  today, G4 moves the one its read supersedes; every superseded row stays one `git show` away; the
  freeze's row hashes and the 26.5 rows' order verify against the working file at every merge.
- **X8 — padding is touched deliberately**: G3 recomputes it from the laws and records the numbers;
  G4 closes the toolbar seam; the core advisory constant's retirement is not decided in this wave.
- **X9 — no GPT-rung agents**; children and reviews are opus `general-purpose` (read-only for
  reviews); ledger sections assigned above; merges `--no-ff` with the freeze verified at each; no
  attribution trailers.

## Ordering & Dependency Map

Charter review → fold (done) → **G0 ∥ G1** → G1 merged; G0 merged; the parent rules any shape G0
could not name (or G2 lands the spanning set) → **G2** (merged, reviewed, proofs confirmed by the
parent) → **G3** → **G4** → the user's eye on the sheets → `pnpm release` (the user) → tag.
*Amended by Decision Log 4 (b): G3 fits, seals and reads (calibration + validation, the ladder,
holdout once); G4 lands.* After
this wave, in the order W29 Deferred kept: the chromatic-transmission child; the identifying sitting
on the 27 bed; the highlight directionality reader; the decoupled-contrast flag and its read; the
motion-metrics harness.

## Risks & Mitigations

- **A second leaf shape mid-fit** would be a second exemption. G0's cut is the first mitigation and
  the spanning set the second; a leaf inert by decision is a shape the project already documents.
- **The thin shadow regime is the instrument's limit, not Apple's law.** The acceptance names its
  statistic and excludes non-converged fits; the device-px hypothesis is tested on the cells that
  carry it before a leaf is shaped around it.
- **The joint refit loses the energy while fixing the shape.** The departure residual (0.0007 today)
  is a declared stop; `thickOcclusionAt160` becomes fitted rather than derived.
- **A light-only scatter fit lands on the wrong side of dark** (§5.154 §9 (c)). Two values per
  scheme in the leaf shape from G0, and the dark bed's structure tables in the declaration.
- **The probe ladder is fitted on and the gated sets carry three pitches**, so the verdict cannot
  see a fit that only matches the ladder. The claimed rows are on the gated pitches; the ladder's
  own residuals are reported per pitch so a fit that helps 16 px and hurts 4 px shows.
- **The scatter's scalar projection moves a `dom` row the wrong way.** The two `ssimMean` rows are
  declared the shadow's; the CSS tier's structure ratio is pinned before the fit (G0 (d)).
- **The read appends to a 72 MB file and makes another generation superseded.** X7, twice.
- **The recede's exterior moves with the σ law at spans it has no calibration cell for.** Reported on
  the inactive holdout rows as readings, not fitted; the tracker's scenes decision stays open.
- **The padding shrinks at thin spans**, the direction that can expose a sampling floor. G3 runs the
  diagnostics that read the pad and records the smallest pad the laws produce at each span.

## Deferred / Out of Scope

The chromatic transmission (W29 Decision Log 6 (c)); the highlight's angular reader; the decoupled
increased-contrast read and `compare`'s flag; the identifying sitting; the motion-metrics harness;
the CSS tier over pure black; inactive calibration cells above span 96 (a `scenes.json` decision;
evidence-visible); `samplingPaddingFor`'s advisory constant; the Reduced Transparency opacity policy
and the impulse specular point (tracker); the slider's ends as evidence classes.

**A third read of the holdout inside this wave would need a ruling** (added 2026-09-20, review
closure; claims §5.159b §10, finding 13). Decision Log 5 (a) reads "once per frozen configuration",
and the wave has spent two: G3 read the holdout at the sealed documents (124 rows) and G3b read it
again at the same documents after the renderer fix, which is a second frozen configuration by the
same rule that made G3's rows a generation of their own — the material did not move and the
renderer did. That is two reads of one scene set inside one wave, each legitimate under the rule as
written, and the rule does not by itself stop a third. G4's landing is not expected to want one:
it fits nothing and reads nothing. If a later child does — a second renderer fix, a re-seal, a
recapture — **the third read is the user's to rule on**, because "once per configuration" stops
being a guard against fitting on the holdout the moment a gate can mint configurations. What a
ruling would have to name is the smallest thing that makes a configuration new.

### At close, 2026-09-20 — what this wave measured and did not do

Each is a named piece of work whose evidence is already on disk, in the order the parent would
charter it. None is a loose end: the wave established the existence and the size of every one.

1. **A metric that reads the exterior's width.** The three rows this wave claimed are recorded
   **refuted rather than unmet** (Decision Log 5 (d)): the lever moved — the CSS group clip at span
   160 goes 33.05 → 45.79 CSS px and the per-surface blur radius with it — and the rows moved by
   0.0002 where they need 0.016, because SSIM over a whole cell is dominated by the interior and the
   backdrop. The biggest movers of the whole read are `falloffSigmaWeb`, by up to 30 CSS px, on an
   axis no gated bound is stated over. *The work*: an adopted clause on the exterior's fitted width
   or on the departure profile's shape, which would make the two `ssimMean` rows reachable by a lever
   that already exists. Evidence: `verdict.txt`, `moved-cells.v2.txt`.
2. **B4's miss on three of four standard beds, and a scale-invariant statistic that cannot fix it.**
   The structure ratio moves toward 1.0 on the dark document and is declined on the light one, and
   the reason is structural rather than a matter of values: the analysis pass's per-source statistic
   is read off a fixed 64 × 64 grid, which makes it the same number at both scales — measured 0.170
   against 0.176 on one scene — so it cannot act in opposite directions on two scales that need them.
   *The work*: a change to the analysis pass, which is a second operator and the user's to charter
   (§5.159 §4).
3. **The light bed's 16 px structure.** The light interior passes **1.5670** of the native's
   structure at the 16 px checkerboard, unmoved by this wave and visible on the sheet: the checker
   survives vitrea's body sharper than Apple's on `rrect-md`, `rrect-ml` and `rrect-lg`. It is the
   residual the scatter declined to move and the one the next diffusion child inherits.
4. **The thin regime's instrument.** B2 stays a one-wave reading rather than an adopted row because
   the thin-span (amplitude, σ) pair is not identified — it trades at a constant product at span 44 —
   and the thin σ **bifurcates on the author's tint**, untinted cells reading a 1x/2x ratio of
   1.86–2.57 and their tinted siblings 0.51–0.56 on the same geometry. *What would make it
   adoptable*: a thin-span cell whose amplitude lets the pair separate (§5.156 §5).
5. **The holdout's two reads, and what makes a configuration new.** This wave spent two reads of one
   scene set, each legitimate under Decision Log 5 (a) as written, because a renderer fix is a new
   frozen configuration by the same rule that makes a moved document one. **A third would need a
   ruling**, and what a ruling has to name is the smallest thing that makes a configuration new —
   because "once per configuration" stops guarding against fitting on the holdout the moment a gate
   can mint configurations (§5.159b §10, finding 13).
6. **`samplingPaddingFor`'s core advisory constant.** Not decided here by X8, and this wave added
   its numbers to the tracker entry rather than a ruling. The reading that matters is a negative one:
   the backdrop sampling pad **did not move at all**, because it is 3σ of the backdrop blur and the σ
   law reaches the shadow. What did move is the shadow's reach, 20.90 → 13.39 CSS px at span 32 and
   31.88 → 42.93 at 160 on the light document, 57.40 at 220, and 12.76 / 61.50 on the dark. So the
   constant a retirement would replace is no longer a constant on one of the two pads it stands
   beside, which is a second argument for the fix shape that entry names.
7. **The chromatic child.** W29 Decision Log 6 (c), untouched by contract (X3) and confirmed
   untouched by the read: the four dark `photo__rrect-lg__rest :: oklabDeltaEP95` rows were declared
   expected-unmoved and are unmoved to five decimals on two of four. It is the **largest residual on
   this wave's own sheets by a wide margin**, and in the dark scheme it is visible without
   amplification: Apple's dark body carries a photograph's green and magenta through it where
   vitrea's reads as a flat warm grey.
8. **The recede's exterior above span 96.** The inherited block narrows the old halo and does not
   close it: the inactive probe rows this wave committed read a native-over-web departure ratio of
   about 0.17 on both schemes. No non-holdout inactive cell above span 96 exists, which is a
   `scenes.json` decision and is evidence-visible rather than blocked.
9. **The exterior's SHAPE at the largest span.** New here, from the eye rather than from a metric:
   below a span-160 panel the ×8 difference carries visible level contours rather than a featureless
   haze. The width moved and the energy moved, and what is left is a difference in the falloff's
   profile that no bound on the bed reads (§5.160 §6).
10. **A shadow section for `/laws/`.** The page has five sections and no shadow readout at all; the
    σ law joined the body section's span control because that is the one axis the page already
    drives. A section of its own — a stage that shows a caster's shadow narrowing and widening as the
    span moves — is the shape that would make the operator legible rather than numeric.
11. **What the tracker gained this wave**, each with its own entry: the tone stage's disorder as a
    **band** under a ground of 0.003 rather than an anchor, localised to the 40 px plate's published
    alpha (0.695 against 0.648–0.656 everywhere above it — *beside, 2026-09-20, review closure;
    claims §5.160 §9, finding 9: **0.692–0.695 over the band and 0.647–0.667 above it**, 35 of those
    74 stops above 0.656, so it is a step at the band's edge against a rising trend*), with its
    composited body non-monotone
    across the bottom of the control; the standing one-code-between-landings class gaining a fourth
    recorded instance — a `dom` cell at 4.56·10⁻³ that the shader fix cannot have reached; and the
    React driver-timing class gaining the reading that **both of its cases have now failed on both
    engines**, which retires the last reading of it as an engine's property rather than the driver
    round trip's.

12. **Nothing checks that a WGSL transcendental's argument stays inside f32** (added 2026-09-20,
    review closure; claims §5.160 §9, finding 4; the tracker entry of that name). The wave's own
    open debt, and the only one it left in the shader. G3b's `tanh` overflow is fixed as an
    identity and the entry says why that is not the end of it: **the instance is fixed; the class is
    not.** `src/wgsl/` evaluates `exp`, `pow`, `tanh` and several polynomials on quantities a
    profile document scales, and nothing asserts that any of their arguments stays inside f32 over
    the inputs the bed carries, let alone over the ones a future fit could produce. *The work*, in
    the entry's own order: a unit case over the WGSL sources requiring every transcendental's
    argument to be clamped or to carry a named range proof; a `@gpu` sweep in the shape of
    `w30-thin-sigma-coverage.spec.ts`, over **both** halves of whatever ratio is being guarded —
    the material's axis and the scene's — since the defect is a ratio of a caster's depth to its σ;
    and a standing readback guard that refuses a raster with a hole inside a declared silhouette.
    It belongs in this list because this wave is what made the class reachable and what found it.
13. **A change's "checked, unchanged" sweep read the imports and not the prose** (added 2026-09-20,
    review closure; claims §5.160 §9, finding 4; the tracker entry of that name). G1's consumer
    table called three files "unchanged, checked" on what they DO while what they SAY had gone
    stale, and what is still open is the same error one layer out: `matrixSchemaRefusal`'s runtime
    message still offers the operator a ruling that ended. *The work*: re-read the refusal's wording
    against what a run that trips it today would be, and have a sweep that reports a file
    "unchanged, checked" say what the file CLAIMS about the thing being changed. It is listed here
    because a wave whose whole method is records beside records is the wave most exposed to it.

*As chartered and unchanged:* the highlight's angular reader; the decoupled increased-contrast read
and `compare`'s flag; the identifying sitting on the 27 bed; the motion-metrics harness; the CSS
tier over pure black; inactive calibration cells above span 96; the Reduced Transparency opacity
policy and the impulse specular point; the slider's ends as evidence classes.

## Tracking Map

| Child | Status | Claims section | Evidence |
| --- | --- | --- | --- |
| G0 | **CLOSED 2026-09-20.** The pre-wave resolved macOS 26.5 materials on disk before a leaf exists, at the pinned `b2b570e4adcea8fb` / `874be66ea501621b`, with the identity test (empty `W30_OPERATOR_LEAVES`, green) and the 1,107 gated-row pin. Nothing under the freeze touched; `freeze.py verify` intact at 1,818 at open and close. **The shadow cut**: the thick regime's line and its CSS-px scale invariance confirmed (ratio 1.021 light / 1.017 dark over 66 cell pairs), the thin regime's device-px reading **refuted** — neither 1.00 nor 0.50, the (amplitude, σ) pair trades at constant product, and the thin σ bifurcates on the author's TINT — so the floor is CSS px with its value **declared unfitted**. The σ law named: `σ = sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan · (span − sigmaSpanRefPx))`, three leaves, every inert default 0, the knee derived. **The structure cut**: the tables cannot choose between (i) and (ii) and G2 lands the spanning set; the scheme-conditioned leaf named under both; `sizeToneLevelFar` declined. The CSS tier's attenuation carried into `tier-coherence.test.ts` as twelve recorded readings plus the relation they encode. The holdout drop moved into `fit.py`'s `cells()`, exercised by a check that builds a matrix containing a holdout row. Declarations committed before G2 opens | §5.156 | `results/2026-09-20-w30-g0-cut/` |
| G1 | **CLOSED 2026-09-20** — the split executed: `results/matrix.json` 2,017 rows / 72,102,187 B → **1,562 rows / 55,768,930 B**, W29 G3's generation moved byte for byte to `results/superseded/fa872c683f3e.json` (343) and `96b36eedf1c4.json` (112), named by the ACTIVE document's hash with `index.json` the lookup; no macOS 26.5 row moved and their order holds; append-check 6/6 PASS including a full reconstruction to the pre-split digest; `freeze.py verify` intact at 1,818; the demo's `capturedAt` tie-break retired, `atAShippedDocument` kept as the edited-document guard, `vibrancy.ts` given a digest lineage beside the old; chain green and `pnpm --filter demo build` green (main chunk 39,062.53 → 30,272.52 kB) | §5.157 | `results/2026-09-20-w30-g1-split/`, `results/superseded/` |
| G2 | **CLOSED 2026-09-20.** The eight leaves landed at algebraic identities in one commit — `sigmaSlopePerSpan` / `sigmaSpanRefPx` / `sigmaThinOffsetPx` on `MaterialOuterShadow`, `sizeHeavySecondSigma` / `…2x` / `sizeHeavySecondShare` / `sizeScatterScaleGain` / `sizeScatterScaleRef` on `MaterialProfile`, every one 0 — with the merge lines, both allowlists, the CSS mirror of the σ law (and the five scatter leaves deliberately not mirrored), three new uniform vec4s, the shader evaluating both laws, and the second heavy texture as a third pyramid blur kind gated on its share. **No document was re-sealed**: the child measured that re-sealing the four macOS 27 documents drops 230 gated cells across six profiles and turns the chain red by 23 cases, which is this charter's own Surprise on the bed nobody checked, and the parent ruled Decision Log 4 — one record for all six documents, and a re-seal lands with its read from here on. Proofs: freeze intact at 1,818; goldens 34/34 byte-identical with no regen; the identity test green with the leaf list filled (`toStrictEqual`); the 1,107 gated-row pin; the CSS tier's 120 × 47 declarations character-identical to bytes recorded before a leaf existed; the inert laws swept over spans 1…1000 at both scales on both tiers; a `@gpu` case that opens the gate (widths-only Δ 0, share ∓1 Δ 41/32, sign Δ 73) — which **caught a real vec4 misalignment every inertness proof was green over**; `tier-coherence` green; chain green at 2,541 over 173; `window-activation` green at eight re-recorded hashes. **Reviewed and closed 2026-09-20 (§5.158 §8):** one blocking finding — the two RECEDED records' `currentSha256` were taken over the recede alone rather than over the composition a root draws, corrected beside to `035f537d9c27e3ed` / `4763b0d195fdb077` with `reseal.ts` now asserting its own construction and all six records recomputed independently — and six others: the σ and scatter vec4s each given an ON-path `@gpu` case (31 passed), the scale statistic's unobserved fallback moved from 0 to the material's reference, the reach's span made required with the bound's monotonicity condition asserted at the fitted shape, the declaration bed extended to both accessibility regimes against a pre-leaf fixture, a capture-path case for all eight leaves, the eight proof rows with no committed output rerun and committed, and the multiplied zero's finiteness clause. No document re-sealed, no frozen byte moved; chain 2,549 over 173 | §5.158 | `results/2026-09-20-w30-g2-leaves/`, `profiles/digest-supersessions.json` |
| G3 | **CLOSED 2026-09-20 with one BLOCKING finding for the user.** The σ law fitted and held: `sigmaSpanRefPx` at 96, light `8.96 / 0.1314 / −6.8328` and dark `9.04 / 0.1340 / −6.9680`, the knee derived at span 44. **B1 MET jointly on both documents** at 4.318 % and 3.604 % of its 5 %, from four objectives `shadow-law.py` computes and names — an absolute least squares lands the light document OUTSIDE the joint window because a squared absolute residual weights a span-160 observation four times a span-96 one, and the adopted point maximises the smaller of B1's and B2's slacks with the slope held inside the range the served beds measure for themselves. **B2 MET** on every bed it names (1.155–1.419 of its 1.5, against 0.19.0's 5.97–7.34). The seven amplitude leaves solved from the departure over three rounds, the solve's linearity holding to 1.4 % at the last; **`thickOcclusionAt160` fitted for the first time in the project's history**, on the ladder's span-160 rungs. **B3's stop HELD at 0.00034 against 0.00035.** The scatter decided on five probe rounds: candidate (ii) adopted on the DARK document at −2 about 0.03 (1x dark 0.7474 → 0.9732 inside the window, 2x dark 0.6367 → 0.7665 toward it) and declined on the light one, candidate (i) declined on both, **both declines measurements** — a second tap wider than the first moves the gated cell by −0.0000 (§5.158 §6's trap, reproduced), and candidate (ii)'s statistic is scale-invariant BY CONSTRUCTION at 0.170 against 0.176, so it cannot act in opposite directions on two scales that need them. **B4 MISSED on three of four standard beds**, recorded. The four documents re-sealed with the seal asserting its own construction first, the four macOS 27 supersession records retired, 726 rows read and appended (332 gated, **270 ladder probe — the first macOS 27 probe row the matrix has ever held**, 124 holdout once), the split applied at §5.157 §8's invocation and the append-check 6/6 PASS. **The blocking finding (§5.159 §6, Decision Log 5 drafted):** at a thin caster the fitted σ exposes a latent renderer defect that leaves a strip of a 44 px surface undrawn — visible on the dark bed's capsule, **170 texture cells outside W20's adopted declaration conformance**, and reproducible on 0.19.0's own shipped document with `sigmaPx: 8` and no W30 leaf involved. The gate will not widen the bound nor re-fit σ around it | §5.159 | `results/2026-09-20-w30-g3-operators/` |
| G3b | **CLOSED 2026-09-20.** §5.159 §6's blocking finding is **`tanh`**: the outer shadow's falloff is a tanh of a cubic in the distance to the shadow's silhouette in σ, and a backend that lowers `tanh` through `exp(2t)` — Metal's fast-math path — overflows f32 past `t = 44.3614`, which is **10.0610 σ inside the silhouette**, and the NaN reaches the composite's alpha through `shadowAlpha · (1 − coverage)` where a coverage of exactly 1 does not stop it. `nan-band.py` reproduces every row of §5.159 §6's bisect table to the row from that one expression with no free parameter, including the two that draw clean. **The fix is a ±20 clamp on the argument and is the identity** — tanh saturates to exactly 1.0 by |t| = 9.011 in f32 and 18.2 in f64 — so the **34 goldens are byte-identical** and `outerShadowReachPx`'s bisection does not move a digit; no material constant moves, no leaf, `DEFAULT_MATERIAL_PROFILE` untouched (X1). A **new `@gpu` case** at the fitted thin σ fails before at 652 of 4,780 capsule px undrawn (IoU 0.8636) and 132 of 4,308 toolbar px (0.9694) and passes after, with a σ sweep reading 0 / 0 / 784. **The fit does not move**: `shadow-law.py` re-runs byte-identical (B1, B2), **B3's whole block is byte-identical at 0.00034**, and B4's twelve gated readings are unchanged — predicted first on scratch, where `meanDepartureWeb` was bit-identical on all 49 light-standard texture cells because the NaN was only ever INSIDE the silhouette. The four documents carry a dated `$comment-w30-g3b` naming the fix, which moves the file hash and — asserted before and after — **not `resolvedMaterialSha256`**; `macos27-profile.ts` regenerates byte-identical. The bed re-read at those bytes: **726 rows** (332 gated, 270 ladder, 124 holdout once), `verdict.py` 0 native readings moved, the split applied and the append-check **6/6 PASS**, working file **1,833 rows / 66,075,976 B**. **Verdict: W20's declaration conformance 170 → 0 cells outside**, `PREDICATE_EXCLUDES` 83 → 68 with the fifteen span-44 cells all leaving, the **seven `MISSED_27_ROWS` unchanged and every one moving by +0.00000**, no floor adopted and no bound widened; 176 of 726 cells moved and 550 are bit-identical, 170 of the 176 being W20's own. **A second cost of the defect, found here**: the ladder's span-44 column read 5.3–10.2 where its neighbours read 0.5–1.5, so §5.159's `structure.txt` is a reading of the defect at that span and this gate's is the material's — the scatter's decisions stand, being stated on the span-96 gated cell. The **demo's build-time reduction** lands (Decision Log 5 (c)): main chunk **35,782.95 kB → 624.83 kB**, demo suite 34-and-a-dead-loader → **45 passed**, e2e **58 passed** with one case rewritten from a macOS 26.5 fact macOS 27 refutes. Chain green end to end: **2,555 unit tests, 0 failed** | §5.159b | `results/2026-09-20-w30-g3b-thin-strip/` |
| G3 + G3b, review closure | **CLOSED 2026-09-20.** An independent read of both children found **no blocking finding**, twelve findings and one Deferred line; all thirteen are closed here, with every correction recorded BESIDE the text it corrects and no material constant, leaf, document, bound, floor or matrix row moved (X1; `freeze.py verify` 1,818 at open and close; no capture). **Three recorded numbers corrected**: `tanh`'s f64 saturation is |t| = **19.0615**, not the 18.2 this table's G3b row and two code comments carry — the ±20 clamp is still the identity above both and nothing about the fix moves; the dark document's reach pad is **12.76** at span 32 and **61.50** at span 220 (`reach-pad.txt`) against §5.159 §5's 12.94 / 58.36; G3's read was at **build 26A428**, as all three of its read logs say, against commit `f479ead4`'s 25A354. Two commit messages cannot be amended (`f479ead4`, `35ce02b1`) and the Revision Notes say so. **One tooling bug**: `moved-cells.py` compared an axis named `tierCoherence` that no cell carries, so the cross-tier axis was compared against nothing — **331 of 726 cells moved**, not 176, the 155 extra being `dom` cells whose only movement is on an axis that reads their paired texture cell; the 176 that move on an axis of their own, 170 of them W20's, stand. **The unexplained residual is two**: the largest of the four `glass-over-glass` movers is a **dom** row at 4.56·10⁻³, a tier the shader fix cannot reach (candidate cause: the tracker's standing one-code-between-landings class, whose named instance is that scene on a dark bed), against ≤ 8.9·10⁻⁴ on the three texture rows. **The exposure gains its second axis**: a third `@gpu` case sweeps DEPTH at the macOS 26.5 σ of 15.55 and fails on the unfixed renderer at **1,156 of 114,356 declared px undrawn** on a 340 px caster — so a `macos26MaterialProfileDocument` surface past about **307 CSS px** was drawing a strip of itself undrawn, which the changeset now states as the positive note it is. **The fit re-read two ways** (`shadow-law.v2.txt`): with the holdout leak closed the light document does not move and the dark reads 9.0405 / 0.13409 against 9.0393 / 0.13401, the same 9.04 / 0.1340 after the seal's rounding; at those rounded constants B1 is 4.3225 % and 3.5966 % against the fit's 4.3177 % and 3.6043 %. **`results/superseded/`**: `readUnderClaims` split into reader and mover, the README's table generated from the index with every digest and byte count asserted, `apply` now requiring `--read-claims`. Chain green: **2,556 unit tests, 0 failed**, 34 goldens with no regen, **34 `@gpu`**, demo build green, freeze intact | §5.159b §10 | `results/2026-09-20-w30-g3-operators/shadow-law.v2.txt`, `results/2026-09-20-w30-g3b-thin-strip/moved-cells.v2.txt` |
| G4 | **CLOSED 2026-09-20.** The wave's one tolerance declared for adoption is **adopted**: B1, in the joint form Decision Log 3 (c) ruled it, four cases reading the natives back out of G0's cut and the law out of the shipped documents rather than transcribing either — mutation-checked at a 0.1 % tolerance, where three of the four fail and print `+1.872 %` and `+1.867 %` at span 96, which is `shadow-law.v2.txt`'s reading to the digit. **B2 and B4 are not adopted**, as §5.156 §5 declared before either operator existed; no floor, no widened bound, `MISSED_27_ROWS` unchanged at seven. **The layout holds at close** (X7's third application): `plan` reports **1,833 retained, 0 moved**, the working file is 1,833 rows / 66,075,976 B one generation per profile, `results/superseded/` holds **6 files, 1,636 rows, 59,878,163 B** with `readme` regenerating byte-identical, and `freeze.py verify` reads 1,818 intact at open and close. **The toolbar seam is closed** by the tracker's first shape — `GlassRootHandle` carries the selected document, a `clear` toolbar on `macos26MaterialProfileDocument` opens 36 CSS px where it opened 73, the default document is unchanged — and it turned up three things the entry did not have: `samplingPaddingFor` could not express an endpoint with no patch (the key's presence now does), the recorded 2.2× is 2.04 on the light endpoint, and the seam's second axis was an **under**-pad on a dark root. **The tone stage is re-ranged and the reading reverses the ruling's premise**: the plates separate widest over the DARK half (0.026, 11 % of their own level, at a ground of 0.006 against 0.0148 at 0.16), and what closes at the bottom is the ORDER. 81 stops of equal ratio between the same two ends, 40 of them in the separating band against 16 before; the finer control found the disorder is a **band** under 0.003 rather than an anchor, and localised it to one plate's alpha. **The demo shows the operator it ships**: the seven figures the page printed move by ≤ 0.0013 across this wave while `falloffSigmaWeb` moves by up to 6.2 CSS px, so the shadow's fitted falloff joins `figuresOf` and the reduction; the pair's three stale labels are derived; `/laws/` gains the σ law on its span control, having had no shadow readout at all. `CLAUDE.md` loses the `rm results/matrix.json` heuristic and gains the split; both READMEs and both changesets say what moved; the coverage matrix is re-scored with **no row moving** and one recorded limit closing. Chain: **2,564 unit tests 0 failed**, 34 goldens with no regen, 34 `@gpu`, 410 platform-web, 58 demo, and **2 React reds recorded not rerun** — the tracker's driver-timing class, which has now failed on both engines on both cases. **0.20.0** versioned, three minors, dry runs clean with `workspace:` rewritten to `^0.20.0`. **Amended beside 2026-09-20 (review closure; claims §5.160 §9), no number in this row rewritten:** the ≤ 0.0013 on the seven figures is the **light bed's** — the dark bed moves `luminanceSlopeWeb` by +0.0138 / +0.0113 and `ssimMean` by +0.0035 / +0.0031; the tone stage's 11 % and 16 stops are the spread over the MINIMUM and a count of the control's own settings, and under the one rule the page and the ledger now read by they are **10.4 %** and **15 stops** (against the ladder's 40, counted the same way); the 40 px plate's alpha is **0.692–0.695** over the band and **0.647–0.667** above it, with the body's minimum **0.2057 at position 7** and the discontinuity the 0.2340 → 0.2057 step; B1's population guard now asserts a per-span COUNT of contributing beds (light 4 / 2 / 4, dark 2 / 2 / 2) rather than a non-empty union, mutation-checked by dropping the 2x-light bed; and the two chain steps this row's count never covered — root `npx eslint .` and the demo Playwright — are run at the closure's head and committed | §5.160 | `results/2026-09-20-w30-g4-landing/` |
| G4, review closure | **CLOSED 2026-09-20.** An independent read of the landing found **no blocking finding** and fourteen items; all fourteen are closed here, every correction recorded BESIDE the text it corrects. Nothing is a runtime behaviour change — comments, tests, guards, records and prose — and **0.20.0 stays prepared and unpublished with no changeset added**; no material constant, leaf, document, bound value, floor or matrix row moved, no macOS 26.5-keyed byte changed, no capture (`freeze.py verify` **1,818 intact**). **Two guards where there were none**: B1's population case now asserts a per-span COUNT of contributing beds (light **4 / 2 / 4**, dark **2 / 2 / 2**) because the ±0.685 % window at span 96 comes entirely from the 2x-light bed and the old non-empty-union assertion let an emptied bed widen it to ±3.82 % — mutation-checked; and the `/laws/` σ readout, pinned by nothing at the landing, is now asserted at spans 32 and 288 against the `box-shadow` the tier writes, with the page's prose DERIVED from the same law rather than typed. **Two React contracts tested**: `GlassRootHandle` holds the document the ROOT selected when the prop moves under it, and the toolbar's gap follows the system scheme under `colorScheme="auto"` with the props standing still — both mutation-checked. **Numbers corrected beside, none rewritten**: the toolbar comment's 16 % is **7.6 %**; `index.json` maps **ten** document hashes, not eleven; the seven figures' ≤ 0.0013 is the **light bed's** (dark moves `luminanceSlopeWeb` +0.0138 / +0.0113); the tone table's column mixed spread/mean with spread/min and reads **7.1 / 10.4 / 6.1 / 2.8 / 2.3 %** under one rule, with the separating band **15 → 40** stops counted the same way; the 40 px plate's alpha is **0.692–0.695** over the band and **0.647–0.667** above it, its body's minimum **0.2057 at position 7**, and the discontinuity the **0.2340 → 0.2057** step, 2.5× the recorded dip. **Three verdicts re-read against their own evidence**: clause 4 is MET and contains B4's miss on three of four standard beds; clause 7's "two findings" is **three**; clause 7's four-column sheets were delivered at G3 (`sheets.py`). **Two chain steps that had no committed output are run and committed** — root `npx eslint .` and the demo Playwright — with `chain.sh` writing `chain-status.v2.txt` beside the hand-typed table. Deferred at close gains the wave's own two open tracker entries. Chain: build / lint / root eslint **exit 0**, **2,566 unit tests 0 failed** against §7's 2,564, demo Playwright **59 passed** against §7's 58, freeze 1,818, dry run clean at 0.20.0. The demo suite ran twice and both runs are disclosed: the first was red on this closure's OWN new case, which read the rim instead of the outer shadow because a browser reserialises `box-shadow` with the colour first and `inset` last | §5.160 §9 | `results/2026-09-20-w30-g4-landing/chain.sh`, `chain-status.v2.txt`, `chain-eslint-root.txt`, `chain-demo-e2e.txt` |

## Decision Log

### Decision Log 1 — the charter (2026-09-20; the parent, under the user's "operator wave first, and rest on your judgement"; amended the same day by the review fold)

Ruled by the user on 2026-09-19 (W29 Decision Log 7 (a)): both operators in one wave after 0.19.0
under a single one-time X1 exemption. Ruled by the parent here under the user's delegation — given
after the parent named the matrix split and the tone stage as the two decisions the user had been
holding and asked whether they were the parent's to make — each overridable by the user before G2
opens:

- (a) **The exemption's shape**: supersession beside the document. The macOS 26.5 documents and the
  seed stay byte-identical; `profiles/digest-supersessions.json` records the recorded and current
  digests once; the pin tests assert both and the identity over the pre-wave resolved materials.
  The first draft's re-record-in-place is withdrawn: it edits bytes `atAShippedDocument` hashes and
  would empty the macOS 26.5 bed out of every bound. Reasoning in Design.
- (b) **The exemption's timing**: its own child, G2, merged and reviewed before any fit, with every
  leaf at an algebraic identity and the proofs verifiable without a fit; the spanning set where G0
  cannot choose the scatter's shape.
- (c) **The order inside the fit**: the shadow first, jointly with its amplitudes; the scatter second,
  on G0's tables.
- (d) **The matrix's layout**: split by generation, applied by G1 and again by G4. The tracker filed
  this as the user's to rule; the user delegated it in so many words, and the parent seconds G4's
  recommendation for its reason (a name where a timestamp stands) and for this wave's (the read that
  would cross 100 MB). Overridable before G1 merges.
- (e) **The tone stage**: re-ranged, the near-black stop kept last. Reasoning in Design. The user may
  prefer retirement; the geometry is untouched until G4 so the choice is still open at G4's dispatch.
- (f) **Closed on the way**: the reader-side holdout drop (G0) and the `GlassToolbar` document seam
  (G4), both because this wave touches the code they live in.
- (g) **The version**: 0.20.0, three minors, prepared and unpublished.

### Decision Log 2 — the parent, on G0's cut (2026-09-20): the pitch ladder joins the macOS 27 canonical bed as probe rows; the σ floor is CSS px; the padding recomputation is two-sided

G0 found that the committed macOS 27 generation carries **no probe row** (§5.156 §3): the pitch
ladder — the only evidence that can identify a scale-selective scatter — was read onto scratch
matrices in W29 and never committed, so the wave would otherwise fit the operator on a ladder and
record its verdict on a bed with no rung of it. The macOS 26.5 bed carries 662 committed probe rows,
so probe rows in the canonical matrix are the precedent, not a departure. Ruled:

- (a) **G4's canonical read includes the pitch ladder as probe rows** for the macOS 27 generation:
  the 45 ladder scenes (`checkerboard-4/8/32/64`, `checkerboard-lc16`, `hc-text-7/28`) on the
  **WebGPU tier for the four standard profiles**, and on the **CSS tier for the two 1x standard
  profiles** so the CSS residual B4 records is committed evidence too — about 270 rows, written with
  `fixtureSet: "probe"` so the gate drops them as it drops every probe row. Not the whole probe set
  (about 180 rows per profile-tier, which would put the working file within reach of GitHub's
  refusal for no gated benefit) and not the accessibility profiles (five rungs identify nothing). The
  cost in bytes is recorded in §5.160 beside the split's second application. G3's fit reads the same
  ladder onto scratch first; G4's rows are the sealed reading of it.
- (b) **The σ law's floor is in CSS px and its value is a declared unfitted reading** (§5.156 §2):
  the thin regime is the instrument's — the 1x/2x ratio is neither 1.00 nor 0.50, the (amplitude, σ)
  pair trades at a constant product at span 44, and the thin σ bifurcates on the author's tint — so
  the law takes no dpr argument, and `sigmaThinOffsetPx` is set by G3 to where the fitted line meets
  the thin statistic B2 names, with B2 a one-wave reading rather than an adopted row. The Design's
  "device px if the cut confirms it" is resolved the other way, for the measured reason.
- (c) **X8's padding recomputation is two-sided**: the shipped σ is a third too narrow above span
  128 (reach 31.88 → 43.80 CSS px at span 160, +37 %), not only too wide below 96, so G3 records
  the largest pad the laws produce as well as the smallest, and the group clip takes the max over
  members.
- (d) **The spanning set is what G2 lands**: `sigmaSlopePerSpan`, `sigmaSpanRefPx`,
  `sigmaThinOffsetPx` on `MaterialOuterShadow`; `sizeHeavySecondSigma`, `sizeHeavySecondSigma2x`,
  `sizeHeavySecondShare`, `sizeScatterScaleGain`, `sizeScatterScaleRef` on `MaterialProfile` — with
  the two signed amounts (`sizeHeavySecondShare`, `sizeScatterScaleGain`) the scheme-conditioned
  leaves at inert 0, the widths and the reference not scheme-conditioned, and the second heavy
  texture gated on `sizeHeavySecondShare` so the off path allocates nothing. `sizeToneLevelFar` stays
  declined (sign stable per scheme, magnitude 5.5× apart within the light scheme).

### Decision Log 3 — the parent, on G0's review (2026-09-20): B3 restated on the tier it is read on; B4 scoped to the fitted beds; the σ law's held parameter; the ladder read is the shadow's too

G0's independent review reproduced every figure of the cut and found the defects in the
declarations — the part the wave is judged against. Ruled, for the review closure to execute:

- (a) **B3, the stop condition, is restated on the tier and partition it is read on.** As declared
  ("0.0007 bed-wide, mean absolute, both tiers, non-holdout cells of every profile") it is already
  exceeded today: the committed matrix reads **0.00079** on that statistic, and the 0.0007 was
  §5.154 §3's light-standard-bed fit figure restated unqualified. The stop is now **the WebGPU
  tier's mean absolute exterior departure over the non-holdout cells of all six profiles, 0.00035
  today, held at or better by G3's sealed fit**, with the both-tier figure (0.00079) recorded beside
  as the CSS tier's reading. The correction is recorded beside §5.154 §3 and §4, not over them.

  > **Re-stated again 2026-09-22, beside this, by W32 Decision Log 3 (a) as RULED by the user;
  > executed at W32 G2 (claims §5.169 §2).** The statistic above reads the WHOLE exterior, which
  > includes the `0-3` band, where vitrea's body over-fills its declared contour on the active
  > pose and Apple's receded exterior is a one-device-pixel rim stroke on the inactive one. Those
  > two errors had been CANCELLING the exterior's own, so W32's fit of the exterior broke the stop
  > by removing one side of a cancellation — 0.00034 → **0.00072** — while the same functional
  > over the admitted bands went **0.00122 → 0.00006** (claims §5.168 §7). B3 is now the same
  > arithmetic mean over the same 166 cells restricted to the **admitted bands** (3–48 CSS px,
  > W32 G0's per-cell per-direction clearance rule), both poses, WebGPU tier, bounded at
  > **0.000056** by W32 clause 2's rule from the bed at W32 G1's read. The 0.00035 above is the
  > superseded statement's bound and 0.00072 its last reading; both are kept, neither is
  > rewritten, and W32 G2's `b3-stop.py` is the reader.
- (b) **B4 binds the four standard beds only.** "Toward 1.0 on every one of the six profiles" cannot
  pass: the reduced-transparency and coupled-contrast beds are captured at the light standard
  document and inherit its scatter values, and the light bed needs structure removed (1.567) where
  those two need it added (0.818, 0.969). B4's "toward 1.0 and past it on none" is scoped to the
  four standard beds whose documents are fitted; the accessibility beds are **reported**, as B4's
  own last sentence already said. The ladder clause is read on the ladder probe rows Decision Log
  2 (a) grants, on the macOS 27 generation, and is conditioned on nothing else.
- (c) **The σ law holds `sigmaSpanRefPx` at 96 in the macOS 27 documents.** The law has one flat
  direction (shifting `sigmaPx`, `sigmaThinOffsetPx` and `sigmaSpanRefPx` together leaves σ
  unchanged), so G3 fits the slope and the offset and refits `sigmaPx` as **the σ at span 96** —
  the span every bed carries sixteen cells at and the span the amplitude's own anchor is keyed to —
  with the reference held. The inert default of `sigmaSpanRefPx` stays 0 (the identity does not
  depend on it); 96 is the fit's value, not the default's. B1 is joint across the beds one document
  serves: the light document must meet ±5 % on 1x, 2x, reduced transparency and coupled contrast at
  once (window at span 96 **[8.897, 9.020]**, ±0.68 % effective) — recomputed by the review closure at four decimals as **[8.8966, 9.0193]**, ±0.685 %; the figure here is the review's rounding, kept as written, the dark on 1x and 2x
  (**[8.908, 9.318]**); a law fitted to the 1x-light median alone fails the 2x-light bed at −6 %.
- (d) **Decision Log 2 (a)'s ladder read is the shadow's evidence as much as the scatter's**: all ten
  fittable span-160 cells per standard bed are ladder probe rows, so without it the wave would seal
  a span-160 σ and a fitted `thickOcclusionAt160` with no macOS 27 web reading at that span outside
  three holdout cells. The ruling stands as granted and is now cited by both operators.
- (e) The rest of the review's findings are executed as amendments beside the record:
  `sizeToneLevelFar`'s table relabelled as linear luminance ×255 with the 8-bit column beside (the
  verdict survives); the spanning set given the same leaf table the σ law has (Decision Log 2 (d) is
  its list); §5.154 §9 (c)'s sheet-instrument ratios and the matrix-instrument ratios named as two
  instruments on the same cells, with the charter's Purpose pointed at both; the row counts
  qualified as metric-carrying; `fit.py render` refusing a holdout set or scene without
  `--with-holdout` so the drop is end to end; `toStrictEqual` in the identity test; the same-scale
  split between `hc-text-7` and `checkerboard-8` recorded as evidence for candidate (ii).

### Decision Log 4 — the parent, on G2's stop (2026-09-20): no document is re-sealed in G2, the supersession record covers all six shipped documents; a re-seal and its canonical read land in one merge, so G3 owns the read and G4 is the landing

G2 landed the eight leaves as algebraic identities and then measured that re-sealing the four
macOS 27 documents — the step the brief asked for because they are not frozen — empties the macOS
27 half of the gated bed: `SHIPPED_DOCUMENT_HASHES` hashes every document's bytes and
`atAShippedDocument` keeps only rows read at a current hash, so the 455 committed macOS 27 rows
(230 gated cells across six profiles) leave every bound and count the moment the bytes move, and
`adopted-thresholds.test.ts` goes red by 15 cases with `tier-coherence` by 8. This is the charter's
own Surprise on the bed nobody checked. Ruled:

- (a) **G2 re-seals nothing.** `packages/calibration/profiles/digest-supersessions.json` carries one
  record per shipped document — six, not two: the two macOS 26.5 and the four macOS 27 — each with
  the document's own `recordedSha256` and the `currentSha256` the pin resolves to over the default
  that now carries the leaves. No document byte moves; every one of the 1,562 rows stays at a
  current hash; the exemption is spent once, as one record beside the documents.
  `scripts/generate-macos27-profile.mjs` reads the current digests from the record so that
  `MACOS_27_RESOLVED_MATERIAL_SHA256` and `root.material` name what actually draws, and
  `macos27-profile-export.test.ts` and `tuned-profiles.test.ts` (its "exactly two records" case
  becomes "exactly the six shipped documents") move with it. Decision Log 1 (a)'s argument, taken
  one step further, as the supersession shape itself was.
- (b) **A re-seal and its canonical read land in the same merge**, so the gated bed is never empty
  on main and no count is ever written down to zero to make a merge green. G3 therefore seals the
  macOS 27 documents when it genuinely moves their material AND runs the canonical read at those
  bytes in the same child — calibration + validation, the ladder probe rows of Decision Log 2 (a),
  and the holdout **once** — with the sealed hashes recorded in §5.159 before the read, exactly as
  W29 G3 and G3b did. G4 is the landing: the split's second application, the verdict carried into
  `adopted-thresholds` where G0's tolerances passed, the toolbar seam, the tone stage, the demo,
  0.20.0 prepared. Clause 5's "read once per frozen configuration" is unchanged in substance; its
  owner moves from G4 to G3, and the Ordering map reads G2 → G3 (fit, seal, read) → G4 (landing).
- (c) **"Binds nothing" is recorded as "costs nothing"**: a WGSL bind-group layout is one layout, so
  the second heavy texture's binding exists at every draw and takes the placeholder view the first
  heavy texture already takes when absent (W26's precedent); at share 0 there is no pool
  allocation, no scratch, no separable pass and no sample. §5.158 says so plainly.

### Decision Log 5 — the parent, on G3's stop (2026-09-20): a renderer child before the wave lands (option (a)); the demo's build-time reduction pulled forward; the re-read a new generation by a recorded comment

G3 (claims §5.159, on its branch, unmerged) fitted the σ law jointly with its anchors and met B1
on every bed a document serves and B2 on every bed it names, held B3 (0.00035 → 0.00034), sealed
the four documents, read the bed once with the ladder and the holdout, and found two things that
stop it from merging. Ruled, on G3's draft (§5.159 §6):

- (a) **Option (a): a renderer child, G3b, on top of G3's branch, before anything merges.** At a
  casting span of 44 CSS px the fitted σ (2.13) reaches a width no shipped material ever had, and
  the optics pass leaves a horizontal strip of the surface undrawn — reproducible on the macOS 27
  light document as 0.19.0 ships it with `sigmaPx` 8 and no W30 leaf above its inert value, a
  function of the shadow's geometry through the group field rect (its bottom edge 24 CSS px above
  the rect's), and it costs W20's declaration conformance 0 → 170 texture cells. The wave will not
  widen W20's bound (option (c)) and will not choose a fit to avoid a renderer bug (option (b)):
  the thin regime is the half of the wave the user chartered. G3b diagnoses and fixes the field
  rect, proves the fix with the goldens byte-identical (they render at σ 15.5) and a new `@gpu`
  case at a thin σ that asserts the surface's drawn coverage equals its declared region, re-verifies
  the sealed fit on scratch (B1–B3; a re-fit is allowed only if the fix moves a reading, and then
  before the holdout), and re-reads the bed at the fixed renderer: calibration + validation, the
  ladder, the holdout **once** for this configuration (a renderer fix is a new frozen configuration
  under X4, as W29's children each were).
- (b) **The re-read is a new generation by the existing rule.** A document's file hash is what keys
  a generation and a renderer fix does not move it, so G3b records the fix in each of the four
  macOS 27 documents as a dated `$comment` naming §5.159 §6 and the commit that fixed it — a true
  statement about the conditions the rows beside it were read under, which moves the file hash and
  not `resolvedMaterialSha256` (the material did not change; the seal script asserts it). G3's
  first read then moves to `results/superseded/` by G1's script as the generation it is — evidence
  of the fit at the defective renderer, findable by name — and the working file holds one
  generation per profile at close. The naming rule gains the case in its README.
- (c) **The demo's build-time reduction is pulled forward from G4 into G3b**, because the chain
  cannot go green without it: the demo imports the whole matrix and the test loader's bridge
  refuses the file between 55.8 and 66.1 MB. The demo reads, at build time, only the current
  generation's rows for the scenes it offers with the fields it prints — a Vite plugin beside the
  shipped-hashes one G1's closure added — so the page's figures do not depend on the file's size
  again. The 270 ladder rows stay (Decision Log 2 (a)); their cost is recorded.
- (d) The three claimed rows are recorded **refuted rather than unmet**: the lever moved (the CSS
  clip at span 160 33.05 → 45.79 CSS px) and the SSIM rows did not, so a whole-cell SSIM does not
  read a shadow's width; the seven rows stay seven, and the wave's Deferred carries "a metric that
  reads the exterior's width" as the shape of work that would close them.

## Surprises & Discoveries

- **The macOS 27 generation of `results/matrix.json` carries no probe row at all** (G0, claims
  §5.156 §3). The canonical read is calibration + validation, then holdout; the pitch ladder is
  entirely probe; so the ladder — the row set this wave's scatter is fitted on — has **no committed
  macOS 27 web reading**. 260 calibration + 62 validation + 123 holdout, and zero probe, against the
  macOS 26.5 generation's 662. §5.153 §6's per-pitch figures came off G3's scratch matrices, which
  were never committed. The Grounding's "each of the four macOS 27 standard profiles carries 45
  pitch-ladder fixtures — every one of them probe" is true of the fixture bundle and is what made
  the operator look fittable from committed evidence; it is not true of the matrix. **Consequence
  for G4**: the canonical read should include `--set probe` for the macOS 27 generation, or the wave
  closes with the operator fitted on a ladder and its verdict recorded on a bed carrying no rung of
  it. That is about 180 rows per profile-tier beyond the 455 and is the parent's to rule. It is also
  what makes `sizeToneLevelFar` and the scatter's shape unfittable from committed evidence today,
  which is three consequences of one cause.
- **The σ law does not only shrink the padding; at span 160 it grows it by 37 %** (G0, claims
  §5.156 §2). The Risks list carries "the padding shrinks at thin spans, the direction that can
  expose a sampling floor", which is right at spans 32 and 44 (−36 % and −41 %) and backwards at the
  top: `outerShadowReachPx` goes 31.88 → 43.80 CSS px at span 160 and 29.86 → 33.52 at 128, because
  the shipped σ is **too NARROW by a third** at spans 128 and above. §5.154 §4's "too wide" is only
  the thin half of a two-sided miss and the wide half had never been stated. X8's "padding is
  touched deliberately" therefore has a cost on a facet already at 3.2× the frame's GPU time, and a
  question for the group clip, which takes the max over members.
- **§5.154 §4's "nearly constant in DEVICE px" is the wrong way round, and the thin regime is the
  instrument** (G0, claims §5.156 §2). The reading it quotes is real and reproduces; the
  interpretation is not: σ_css(2x)/σ_css(1x) = 2.13 means σ in device px goes 1.84 → 7.84, which is
  four times. Neither hypothesis holds in the thin regime (ratio 1.44 light, 1.88 dark). What does
  hold is that the reader's (amplitude, σ) pair trades at a nearly constant product there while both
  factors are separately scale-invariant at 96–160, and that the thin σ **bifurcates on the author's
  tint** — untinted cells read a ratio of 1.86–2.57 and their tinted siblings 0.51–0.56 on the same
  geometry. So the Design's "the floor expressed in device px if G0's cut confirms the thin regime
  is nearly constant there" resolves to **CSS px with an unfitted value**, and the law needs no dpr
  argument at all, which is one mirror fewer for the CSS tier to keep.
- **The instrument returns no σ on `toolbar-group`, and `glass-over-glass` is not a mixed-span
  reading** (G0, claims §5.156 §2). The charter asks what one σ per cell means on a mixed-span
  composite. On `toolbar-group` it means nothing: seven active rows, `shadowFalloffSigmaPx` null on
  every one, in both families — the silhouette is fenestrated and the monotone profile the model
  needs does not exist. On `glass-over-glass` the 120×56 overlay lies wholly inside the 220×130 base
  and never reaches the measured exterior, so the reading is the base's alone and is a clean span-130
  one. **All six of those cells are holdout**, so span 130 has no cell any fit may see and the law's
  value there is an extrapolation — which matters, because one of the two `ssimMean` rows this wave
  claims is at span 130.
- **The frozen documents' bytes are an input to every bound** (found by the charter's review):
  `adopted-thresholds.test.ts` hashes the profile files on disk and keeps only rows captured at those
  bytes, so the first draft's "re-record the digest in place" would have silently retired the macOS
  26.5 half of the gated bed — and the instruction "move every count test to what the machine says"
  is exactly how a child would have baked it in. The shape that costs nothing (supersession beside)
  was found by taking the draft's own argument against a second field one step further.

## Outcomes & Retrospective

**CLOSED 2026-09-20 by G4's landing**, against the seven Parent-Level Acceptance clauses, on this
wave's branch at the 0.20.0 version head. The cut is prepared and unpublished: `pnpm release` is
the user's hand and the tag follows it. The React driver-timing class is red at this cut and
disclosed (clause 7 below); accepting it is the user's, as it was at 0.17.0, 0.18.0 and 0.19.0.

**0.20.0 PUBLISHED 2026-09-21, by the user's `pnpm release` on `484ec8a4` (the head after the
parent's final chain record; the version bump itself landed on G4's branch); tag `v0.20.0`
(annotated, on that commit) pushed by the parent on 2026-09-21.** Registry: web 00:11:11.292Z,
react 00:11:12.250Z, core 00:11:30.688Z — **core last**: the web package and the React binding,
both of which require `@vitreajs/vitrea@^0.20.0`, were listed 19 s and 18 s before core was, so
the release-chain window recurred for 19 s (span 19.4 s); no install attempted inside it. Verified
by a cold install outside the workspace after all three were listed (`npm install --prefer-online`
of the three at `0.20.0` plus React): all three at 0.20.0, ranges `^0.20.0`, all three entry points
import (core 44 exports, web 257, react 37 — web's one new export is `outerShadowSigmaPx`, the
σ law's CSS-side evaluation, §5.158), `GlassRootHandle.materialProfileDocument` in the React declarations, both
material documents exported, no private package installed; installed 1 942 / 1 930 / 658 kB
against 1 848 / 1 880 / 644 at 0.19.0 (the web package carries the four re-sealed macOS 27
documents and the span law's readout; core carries nothing new of size, its growth is the
changelog). One reading moved by design and is recorded here so nobody reads it as drift: the
shipped `macos26MaterialProfileDocument` now reports the light active digest `b340a4dee871633c`
where 0.19.0 reported `b2b570e4adcea8fb` — `currentSha256` from `digest-supersessions.json`, the
resolved material with the eight inert leaves present (§5.158; `recordedSha256` kept beside it in
the record, the document's own field unchanged), which is what `root.material` has to say since
that is what actually draws. The publish accepts the two React driver-timing reds disclosed at
the head, as at 0.17.0–0.19.0.

The one-line result of the wave: **two constants of Apple's material became operators — the outer
shadow's blur is a line in the casting span and the dark material's diffusion is conditioned on the
backdrop's spatial scale — the one-time X1 exemption was spent on a single record beside six
unedited documents with no frozen byte and no pixel moving, a latent `tanh` overflow that had been
in the renderer since the facet was built was found by reaching a σ no shipped material had reached
and fixed as an identity, and the wave's one tolerance declared for adoption is adopted.**

### The acceptance, as verified

1. **The exemption is one commit, touches no frozen byte, and is proven pixel-inert on both tiers —
   MET, and in a shape the charter did not predict.** The pre-wave resolved macOS 26.5 materials
   were written to disk and committed before a leaf existed, at the pinned `b2b570e4adcea8fb` /
   `874be66ea501621b`; the eight leaves landed in one commit at algebraic identities; the proofs all
   held — `freeze.py verify` 1,818 with nothing exempted, 34 goldens byte-identical with no regen,
   the identity test `toStrictEqual` over the pre-wave JSON, the CSS tier's 120 × 47 declarations
   character-identical to bytes recorded before a leaf existed, both inert laws swept over spans
   1…1000 at both scales on both tiers, and the 1,107 gated macOS 26.5 row pin. What the charter did
   not predict is **Decision Log 4**: G2 measured that re-sealing the four macOS 27 documents empties
   the macOS 27 half of the gated bed, because `atAShippedDocument` keeps only rows read at a current
   hash, so the supersession record covers **six** shipped documents rather than two and a re-seal
   lands with its own read from here on. The exemption is spent once.
2. **The structure is measured before the operator exists — MET.** G0's two cuts came off committed
   evidence only and both changed what the wave could do. The shadow cut confirmed the thick
   regime's line and its CSS-px scale invariance (ratio 1.021 light / 1.017 dark over 66 cell pairs)
   and **refuted** the thin regime's device-px reading, so the floor is CSS px with its value
   declared unfitted (Decision Log 2 (b)). The structure cut could not choose between the scatter's
   two candidate shapes, so G2 landed the spanning set (Decision Log 2 (d)). The CSS tier's measured
   attenuation went into `tier-coherence.test.ts` as twelve recorded readings before any fit.
3. **Bounds before reads; the targets named with their levers — MET, with three of the five
   declarations corrected by G0's own review before G2 opened.** B3's stop was restated on the tier
   it is read on (0.00035, twice as tight as declared), B4 scoped to the four standard beds it can
   bind, and B1 restated as two joint clauses with `sigmaSpanRefPx` held at 96 (Decision Log 3). The
   27 tables stayed at W29 Decision Log 4's values throughout and no floor was adopted. The three
   claimed rows were named with their lever and their tier before the read.
4. **Both operators land on the fidelity target with the CSS tier derived in the same commit, and
   the shadow is refitted jointly — MET.** The σ law fitted jointly with the six occlusion anchors
   and `liftAmplitude` over three rounds, with `thickOcclusionAt160` **fitted for the first time in
   the project's history**; B3 held at 0.00034 against its 0.00035 stop; the CSS tier's mirror is one
   function of CSS span with no dpr argument, and `tier-coherence` pins all three readers to it. The
   scatter was adopted on the dark document and **declined on the light one**, with both declines
   measurements rather than omissions — a second tap wider than the first moves the gated cell by
   −0.0000, and candidate (ii)'s statistic is scale-invariant by construction at 0.170 against
   0.176, so it cannot act in opposite directions on two scales that need them. *Beside,
   2026-09-20 (review closure; claims §5.160 §9, finding 6): this clause is MET and it contains a
   MISS. **B4, the structure ratio toward 1.0, missed on three of the four standard beds**, and is
   recorded rather than adopted exactly as §5.156 §5 declared before either operator existed. The
   clause reads MET because what it requires is that both operators land on the fidelity target
   with the CSS tier derived and the shadow refitted jointly, not that every reading improve — but
   a met clause should not read as a clean one. The miss is recorded at §5.159 §4, in the G3 row of
   the Tracking Map below, and as item 2 of Deferred at close, whose named work is a change to the
   analysis pass and is the user's to charter.*
5. **Read once per frozen configuration — MET, and spent twice for a reason the rule allows.** G3
   read the bed at the sealed documents (726 rows: 332 gated, 270 ladder probe — the first macOS 27
   probe rows the matrix has ever held — and the holdout once). G3b's renderer fix made a new frozen
   configuration by the same rule that makes a moved document one, and re-read the same 726. Both
   are legitimate under Decision Log 5 (a) as written; a **third would need a ruling**, which is the
   Deferred line the review closure added. The verdict is recorded per profile per tier per clause
   with every missed cell named, and the three rows this wave claimed are recorded **refuted rather
   than unmet**: the lever moved (the CSS group clip at span 160, 33.05 → 45.79 CSS px) and the rows
   did not, because a whole-cell SSIM does not read a shadow's width.
6. **The evidence layout is ruled and holds at the wave's close — MET, applied three times.** G1
   moved the generation superseded on the day (2,017 rows / 72.1 MB → 1,562 / 55.8 MB), G3b moved
   the one G3's read superseded, and G4 ran `plan` again to find **1,833 retained and 0 moved**. The
   working file is 1,833 rows / 66,075,976 B, one generation per profile, 9.2 % below where the wave
   opened while carrying 271 more rows than the charter priced. `results/superseded/` holds six
   files, 1,636 rows, 59,878,163 B, each named by its active document, each listed in `index.json`
   with the gate that read it and the gate that moved it. Every reader names the generation; the
   demo's `capturedAt` tie-break is retired and the page now reads a build-time projection.
7. **The landing — MET.** B1 adopted; the toolbar seam closed at the document the page draws, with
   the case the tracker named and two findings it did not have *(**three**, beside 2026-09-20,
   review closure; claims §5.160 §9, finding 7: `samplingPaddingFor`'s two readings of an absent
   key, the 2.04 ratio against the entry's 2.2, and the scheme axis on which the error was an
   under-pad — which is what §5.160 §3 and the Tracking Map's G4 row both say)*; the tone stage
   re-ranged against a
   reading that reverses the ruling's own premise, with both ends kept and the two cases moved
   against the committed reading; the demo's figures given the axis the wave fitted, its three stale
   labels derived, and `/laws/` given the σ law; `CLAUDE.md`, both READMEs and both changesets
   saying what moved; the coverage matrix re-scored with no row moving and one recorded limit
   closing; sheets at 2x in both schemes with the eye's residuals named *(three-column, native |
   WebGPU | difference. The clause asks for **native | WebGPU | CSS | difference … with the thin
   spans first**, and that is delivered — at G3, by
   `results/2026-09-20-w30-g3-operators/sheets.py` and the `sheets/` beside it, whose docstring
   names both changes as that child's subject. G4's sheets are the eye's second look at the landed
   material, not the clause's artefact; pointer added beside 2026-09-20, review closure, claims
   §5.160 §9)*; the fixed group versioned
   **0.20.0**, dry runs clean with `workspace:` rewritten to `^0.20.0`, unpublished. **The React
   browser suite is red at this cut** — `presence.spec.ts`'s elapsed window on chromium at 485.0 ms
   against 406.7 allowed and `morph-materialize.spec.ts`'s release timing on firefox — both of the
   tracker's standing driver-timing class, neither in code this wave touched, recorded and not
   rerun.

### What the wave cost, and what it found

It cost four children, one of them unplanned, and no machine time at all: **not one native pixel was
captured** (X5). Every fixture the wave fitted on was on disk from W29, and the two canonical reads
cost about twenty-six minutes of browser time between them.

What it found, beyond the two operators:

- **A clause can be met by a crutch.** W20's declaration conformance read 1.0 on every span-44
  capsule while the shadow was six times too wide, because the shadow's own coverage filled what the
  material's did not. Narrowing the shadow is what made the reading fall — to 170 cells outside an
  adopted bound. The general form is worth the doctrine: *a bound that passes while a neighbouring
  constant is wrong may be passing BECAUSE it is wrong.*
- **A defect that had been shipping since the facet was built, found by reaching a number.** The
  outer shadow's falloff is a `tanh` of a cubic in the distance to the silhouette in σ, and a
  backend lowering `tanh` through `exp(2t)` overflows f32 at 10.061 σ inside it. At every σ the
  project had ever shipped that was deeper than any surface in the bed; at the fitted thin σ of 2.13
  a 44 px control's own centre line is past it. The fix is a ±20 clamp and is the identity — the 34
  goldens are byte-identical — and the case that catches it found a second axis the first never
  swept: at the macOS 26.5 σ of 15.55 a surface past about **307 CSS px** on its shorter side was
  drawing a strip of itself undrawn under 0.18.0 and 0.19.0 too.
- **An operator landed at an identity makes a lane assignment, a fallback, a default and an
  unexercised path all indistinguishable from correct.** The three new uniform vec4s were packed at
  float offsets 117 / 121 / 125, none a multiple of four, and every inertness proof was green over
  it because every word involved was zero. Only opening the gate could see it.
- **An axis list typed by hand against a schema is a silent filter**, and the failure mode is a
  clean-looking negative: `moved-cells.py` compared an axis no cell carries, so the cross-tier axis
  was compared against nothing and a count read 176 where it is 331.
- **The ruling's premise about the tone stage was backwards**, and the reading the ruling asked for
  is what found it. The plates separate widest over the dark half, not the bright one; what closes at
  the bottom is the ordering, and the finer control the re-range installed shows it is a band rather
  than an anchor and localises it to one plate's alpha.
- **A demo can print seven figures and see none of the wave.** `figuresOf`'s metrics moved by at most
  0.0013 while the axis the wave fitted moved by 6.2 CSS px on the same cells. *Beside, 2026-09-20
  (review closure; claims §5.160 §9, finding 3): **on the light bed.** On the dark bed
  `demo-figures.txt` has `material.luminanceSlopeWeb` at +0.0138 and +0.0113 and `ssimMean` at
  +0.0035 and +0.0031, an order of magnitude more, so the "seven figures saw none of the wave"
  reading is the light bed's. It does not move the lesson — none of those seven is the shadow's
  width either — but the ≤ 0.0013 is a light-bed number and is quoted unqualified here and in the
  Tracking Map's G4 row.*

### What is written down that was not before

The wave's instruments are committed and re-runnable: `shadow-cut.py` and `structure-cut.py` with
the statistics named in them, `shadow-law.py` with the four objectives one clause admits and two
flags that read the fit's population and the seal's rounding back, `departure-stat.py` so the stop
is re-run rather than transcribed, `anchor-solve.py`, `scatter-solve.py`, `reach-pad.ts`,
`nan-band.py` — which reproduces every row of the strip's bisect table from one expression with no
free parameter — `moved-cells.py`, `verdict.py`, `split-generation.py` with its self-test and its
generated README, `demo-figures.py`, `tone-range.mjs` and `sheet.py`.

`packages/calibration/profiles/digest-supersessions.json` is new and is the exemption itself: six
records, each naming a document's own sealed digest and the digest its pin resolves to over a
default that now carries eight more leaves, with the leaves listed and the ruling dated. It costs
the freeze zero entries because not a frozen byte moved.

And the ledger gained six sections — §5.156 through §5.160, with §5.159b §10 as the review closure —
in which the three corrected numbers are tabled in one place so a later child does not have to
reconstruct which reading is current.

## Revision Notes

- 2026-09-21 (the parent): **0.20.0 PUBLISHED**, by the user's `pnpm release` on `484ec8a4`
  (registry web 00:11:11Z, react 00:11:12Z, core 00:11:30Z — core listed last, 19 s after web, so
  a 19 s release-chain window recurred, the tenth; span 19.4 s); tag `v0.20.0` annotated on
  `484ec8a4` and pushed; cold install verified (core 44 / web 257 / react 37 exports; both material
  documents exported; `GlassRootHandle.materialProfileDocument` declared; the shipped 26.5 light
  digest reads `currentSha256` `b340a4dee871633c` by §5.158's design, `recordedSha256` beside it in
  the supersession record; 1 942 / 1 930 / 658 kB). The publish accepts the React driver-timing
  reds as disclosed. Status and §Outcomes carry the record beside the "PREPARED, UNPUBLISHED"
  text. The tone stage's fate (Decision Log 1 (e); §5.160 §4) is still the user's call and stays
  as shipped, re-ranged, until ruled.
- 2026-09-20 (the parent): **G4 merged (`fadd9792`), its review closure merged (`ec9e136f`), and
  the parent's final chain run on the merged tree at the 0.20.0 head** — machine 27.0/26A428, RT 0,
  IC 0, slider 0.5, recorded: build, lint and root eslint exit 0; unit **2,566** (policy 23, motion
  164, geometry 170, renderer-webgpu 511, core 302, platform-web 631, react 169, calibration 550,
  demo 46); goldens 34 byte-identical; gpu 34; platform-web 410 across four projects; demo 59; React
  **172 passed, 3 skipped, 2 failed** in the driver-timing class (`presence.spec.ts` on chromium,
  528.2 ms against 425.1; `morph.spec.ts` "a reversal mid-flight" on firefox, a 31.4 ms frame against
  29.3) — recorded in the tracker beside G4's two and not rerun; freeze intact at 1,818. Logs
  `results/2026-09-20-w30-g4-landing/chain-parent-final-*.txt`. The status stands: **CLOSED, 0.20.0
  PREPARED, UNPUBLISHED**; `pnpm release` is the user's hand and the tag follows it. Two things for
  the user's eye before the cut: the tone stage's re-range executed under a Decision Log 1 (e) whose
  stated reason the reading refuted (§5.160 §4 says what retirement would remove), and the two React
  reds disclosed as at 0.17.0–0.19.0.
- 2026-09-20 (G4 review closure): **an independent read of the landing found no
  blocking finding and fourteen items; all fourteen are closed on this branch**
  (claims §5.160 §9, which carries the per-finding table, the three further
  readings and the chain). Nothing here is a runtime behaviour change — comments,
  tests, guards, records and prose only. No material constant, leaf, document,
  bound value, floor or matrix row moved, no byte under a macOS 26.5-keyed path
  changed, no capture was taken; `freeze.py verify` reads 1,818 intact, and
  **0.20.0 stays prepared and unpublished with no changeset added**. What the
  parent and the next wave have to carry from it:
  - **An adopted bound can be tight for a reason nothing asserts.** B1's joint
    window at span 96 is ±0.685 % on the light document, and that tightness comes
    entirely from ONE of the four served beds: remove the 2x-light bed and all
    four cases stay green over ±3.82 %. The population guard asserted a non-empty
    UNION and the per-bed case skips an empty bed by design, so an emptied bed
    would have widened the promise silently. It now asserts a per-span COUNT of
    contributing beds. *The general form: where a clause is an intersection, the
    population it intersects over is part of the clause and has to be asserted
    with it.*
  - **Three of the gate's own scripts launched browsers with no machine reading.**
    `tone-range.mjs`, `demo-shot.mjs` and `harness-captures.sh` do not call
    `record-machine.sh`, and `tone-range.json` is stamped seven minutes before
    the first reading in `browser-runs.txt`. The bracketing readings are
    RT 0 / IC 0 / slider 0.5 on both sides and no fixture or matrix row came off
    any of the three, so nothing recorded depends on it — but the discipline
    exists to make that statement checkable rather than argued, and the fix shape
    is the one `chain.sh` already has.
  - **A "% of their own level" column is a divisor, and it has to be the same
    one twice.** §5.160 §4's table mixed spread/mean with spread/min, and the
    mixed row is the one the shipped prose, the e2e and this charter all quote.
    One rule adopted — the mean — which reads the separating band at **10.4 %**
    rather than 11 %. The same applies to the band's stop counts: 16 counted the
    control's settings where 40 counted painted grounds, and under one rule it is
    **15 → 40**. Neither moves the finding; both move what a later reader can
    compare against.
  - **The tone stage's defect is a STEP, and bigger than recorded.** The 40 px
    plate's alpha is 0.692–0.695 over the band and 0.647–0.667 above it, so what
    the band contrasts with is a rising trend; the composited body's minimum over
    the whole control is 0.2057 at position 7 — on the ordered side of the break
    — and the discontinuity is the 0.2340 → 0.2057 step, 2.5× the dip the ledger
    carried and about 13 % of the bodies it sits among. The tracker's fix shape
    is restated at that number.
  - **A met clause can contain a recorded miss, and should say so.** Clause 4 is
    MET and B4 missed on three of four standard beds. Clause 7 counted two of the
    toolbar seam's three findings. The chain's own table had two steps with no
    committed output. *The general form: an acceptance written as a verdict wants
    a second pass that reads it against the evidence it points at, not only
    against the work.*

- 2026-09-20 (G4): **the landing — one tolerance adopted, two seams closed,
  the tone stage re-ranged against a reading that reverses this charter's own
  premise, and 0.20.0 prepared and unpublished** (claims §5.160; evidence
  `results/2026-09-20-w30-g4-landing/`). Contract X1 holds with nothing to report
  and `freeze.py verify` reads 1,818 intact at the gate's open and close; no
  capture was taken, no row of the matrix moved, no leaf was added and no material
  constant moved. What the parent and the next wave have to carry from it:
  - **Decision Log 1 (e)'s premise is refuted by the reading it asked for, and
    the ruling is executed anyway because its instruction survives.** The charter
    says the tone stage's separation "exists over the bright half of the slider
    and closes at the dark end". `tone-range.json` walks all eighty stops on the
    shipped material: the three plates separate by **0.026, 11 % of their own
    level, over a ground of 0.006** and by **0.0148, 2.4 %, at 0.16**. Widest over
    the dark half, narrowest at the bright end. *Beside, 2026-09-20 (review
    closure; claims §5.160 §9, finding 14): those two percentages divide the
    spread by the MINIMUM of the three bodies where three of the five rows of
    §5.160 §4's table divide it by the MEAN. Under one rule — the mean, which the
    page, the e2e and the ledger now read this stage by — they are **10.4 %** and
    **2.3 %**, and the reversal is the same size either way.* What closes at the
    bottom is the
    **order**, not the separation. The instruction — resolution where the plates
    separate — is followed against the measurement, and the premise is corrected
    beside the tracker entry that carried it rather than over it. *The general
    form, for a later charter: a ruling that states a reason AND an instruction
    can survive its reason being wrong, and the reading that executes it is where
    that is found out.*
  - **The finer control found more of the defect, which is a cost of the change
    and is stated as one.** The old grid had one stop under a ground of 0.004 and
    it was the disordered one; the re-ranged ladder has seven and every one is
    disordered, with the order returning at 0.0030 and holding for 74 stops. So
    the tracker's "not ordered by span at the curve's first anchor" is a **band**,
    and it is **one plate's alpha** rather than three plates' composite — the
    40 px plate publishes 0.695 over the band against 0.648–0.656 at every stop
    above it, and its composited body is therefore not monotone across the bottom
    of the control. A sweep that starts at the bottom stop fails on this rather
    than on continuity. *Beside, 2026-09-20 (review closure; claims §5.160 §9,
    finding 9): the alpha is **0.692–0.695** over the band and **0.647–0.667**
    above it — 35 of those 74 stops above 0.656 — so what the band contrasts with
    is a rising trend and not a second plateau; and the body's real minimum over
    the whole control is **0.2057 at position 7**, the first ORDERED stop, with
    the discontinuity being the **0.2340 → 0.2057** step at the alpha break,
    2.5× the dip the ledger records. The conclusion is unchanged and the shape of
    it is a step rather than a dip.*
  - **A demo can print seven figures and see none of the wave.** `figuresOf`'s
    metrics move by at most 0.0013 across this wave on the light bed, while
    `falloffSigmaWeb` on the same cells moves by up to 6.2 CSS px. The page's
    readout now carries the shadow's fitted falloff, with a note saying what the
    web reading is below the size law's knee (the lift's width, not the
    shadow's). *A page that prints a cell's figures and omits the axis its own
    material just changed is printing the figures that happened to exist.*
  - **A padding function could not name one of its own shipped endpoints.**
    `samplingPaddingFor`'s `input.profile ?? defaultSamplingProfile()` collapsed
    "this endpoint has no patch" — which the macOS 26.5 light active material IS —
    into "use the default document's", so the one case the tracker asked for would
    have measured the wrong material. The key's PRESENCE now carries it. And the
    seam had a second axis on which the error ran the UNSAFE way: the macOS 27
    dark endpoint wants about 7.6 % more room than the light one and the toolbar
    took the light one's number under both.
  - **The coverage matrix does not move, and that is the finding.** Both operators
    land inside behaviours already scored `replicated+measured`. What changes is a
    LIMIT recorded inside §1.7's row — "the shadow's blur is span-invariant in
    vitrea and is not on macOS 27" — which this wave closes and the re-score
    records beside rather than over.
  - **The React browser suite is red at the cut and is disclosed rather than
    rerun**, as at 0.17.0, 0.18.0 and 0.19.0. Two cases of the tracker's standing
    driver-timing class, neither in code this wave touched. The entry gains the
    reading that **both cases have now failed on both engines**.

- 2026-09-20 (G3/G3b review closure): **an independent read of the two children
  found no blocking finding, twelve findings and one Deferred line; all thirteen
  are closed on this
  branch** (claims §5.159b §10, which carries the per-finding table and the
  chain). No material constant, leaf, document, bound, floor or matrix row moved
  and no capture was taken; `freeze.py verify` reads 1,818 intact. What the
  parent and G4 have to carry from it:
  - **Three recorded numbers were wrong and are corrected BESIDE the text that
    carries them**, never over it. `tanh` saturates in f64 at |t| = **19.0615**
    and not 18.2 (the clamp is still the identity — 20 is above both — so
    nothing about the fix or the goldens changes); the dark document's reach pad
    is **12.76** at span 32 and **61.50** at span 220, which is what this wave's
    own `reach-pad.txt` prints, against the 12.94 / 58.36 §5.159 §5 quotes; and
    G3's read was taken on **build 26A428**, as all three of its read logs say
    and as §5.159b §5 already recorded, where commit `f479ead4`'s message says
    25A354. **Two commit messages cannot be amended and are noted instead**:
    `f479ead4` for the build, `35ce02b1` for the 18.2.
  - **A tooling bug that flattered a count.** `moved-cells.py` compared an axis
    named `tierCoherence`, which no cell carries — the key is `coherence` — so
    the cross-tier axis was compared against nothing. Corrected: **331 of 726
    cells moved**, not 176; the 155 extra are `dom` cells whose only movement is
    on an axis that reads their paired texture cell, so the 176 that move on an
    axis of their own (170 of them W20's) still stands. The lesson generalises
    past this script: **an axis list typed by hand against a schema is a silent
    filter**, and the failure mode is a clean-looking negative.
  - **The unexplained residual is two residuals, and one of them is not the
    shader's.** Per cell the largest of the four `glass-over-glass` movers is a
    **`dom`** row at 4.56·10⁻³, a tier the fix cannot reach; the three texture
    rows are ≤ 8.9·10⁻⁴. The dom row's likelier home is the tracker's standing
    "two CSS-tier cells differ by one code between landings" class, whose named
    instance is that very scene on a dark bed. Recorded as a candidate, not
    settled.
  - **The exposure had one axis and the defect has two.** The `@gpu` case swept
    σ at a fixed depth; a third case sweeps depth at a fixed σ and fails on the
    unfixed renderer at the **macOS 26.5** σ of 15.55 — 1,156 of 114,356
    declared pixels undrawn on a 340 px caster. So the fix is not about macOS
    27's thin regime: a `macos26MaterialProfileDocument` surface past about 307
    CSS px on its shorter side was drawing a strip of itself undrawn, and the
    changeset now says so as the positive note it is.
  - **The fit's population and the seal's rounding are both readings about the
    fit.** `shadow-law.py` now takes `--fit-on non-holdout` (the fit sees what
    its own table's label promises) and `--at-shipped` (B1 and B2 at the
    constants the documents carry). Neither moves a shipped constant: the light
    document does not move at all and the dark rounds to the same 9.04 / 0.1340.
    Both defaults are unchanged, so `shadow-law.txt` is still what the bare
    invocation produces and §5.159b §3's zero-line `diff` is still checkable.
  - **`results/superseded/` had one field carrying two meanings**, and the README
    that claimed to be generated from it was typed. `readUnderClaims` is now the
    gate that READ the rows and `movedUnderClaims` the gate that moved them;
    `split-generation.py apply` requires both and `readme` generates the table
    from the index, refusing first if any recorded byte count or digest
    disagrees with the file on disk. **G4's invocation gains `--read-claims`**;
    the docstring carries it in full.

- 2026-09-20 (G3b): **the strip was `tanh` overflowing f32, the fix is an
  identity, and the bed is re-read at the same material** (claims §5.159b;
  evidence `results/2026-09-20-w30-g3b-thin-strip/`). Decision Log 5 (a)–(d)
  executed in full; X1 holds with nothing to report and `freeze.py verify` reads
  1,818 intact at the child's open and close. What the parent and G4 have to
  carry from it:
  - **The defect was one line and one precision.** The falloff's tanh argument is
    a cubic in the distance to the shadow's silhouette in σ, and a backend that
    lowers `tanh` through `exp(2t)` — Metal's fast-math path — overflows f32 at
    10.0610 σ inside that silhouette. Clamping the argument to ±20 is the
    identity in both precisions, which is why the 34 goldens are byte-identical
    and why the fit did not have to move: B1, B2, B3 and B4's gated readings all
    re-read byte-identical, W20 goes 170 → 0 cells outside, and the seven
    `MISSED_27_ROWS` move by +0.00000.
  - **Two readings of §5.159 §6 are corrected in §5.159b rather than over
    there**, and G4 should quote the corrected ones: the "24 CSS px above the
    group field rect" is `11.05·σ − 0.5` and not a constant, and the one-line
    reproduction DOES involve W30 leaves — `--material-profile` patches the
    runtime material its `profileKey` selects, so `sigmaPx: 8` over 0.19.0's
    document draws σ(44) = 1.1672. A genuinely flat σ 8 draws clean. The defect
    is a function of σ alone.
  - **A second cost of the defect, not named at G3.** An undrawn strip inside the
    body inflates `interiorStdDevWeb`, so the ladder's **span-44 column** read
    5.3–10.2 where its neighbours read 0.5–1.5, and every per-pitch median
    containing it moved with it (1x dark `photo` 4.230 → 0.441, `impulse` 6.877 →
    0.896). §5.159's `structure.txt` is a reading of the defect at that span and
    §5.159b's is the material's. **The scatter's decisions are unaffected** —
    every one is stated on the span-96 gated cell, whose twelve readings are
    byte-identical — but a later child reading the ladder must take the newer
    table.
  - **The demo's e2e had one assertion that was the macOS 26.5 material written
    down as a law**, and G3 never ran that suite. `site.spec.ts` asserted
    `blur > 2 · offset` on every plate, which a 40 px caster now fails by
    measurement at 2σ = 4.25. Replaced by the span grading itself — the 112 px
    plate's blur exceeds the 40 px plate's — which is the operator read off the
    DOM and which macOS 26.5 could not have satisfied. **G4 should expect other
    assertions of the same shape** anywhere a σ was written as a number.
  - **The demo's reduction is done and G4 inherits it, not the problem.** Main
    chunk 35,782.95 kB → 624.83 kB; `test/matrix-reduction.test.ts` asserts every
    displayed figure against the whole-file read, so the page's figures no longer
    depend on the file's size. The 270 ladder rows stayed (Decision Log 2 (a)).
  - **The split ran a second time here**, so contract X7's second application is
    spent: G4's own read will be the third. The working file is 1,833 rows /
    66,075,976 B, one generation per profile, and `results/superseded/`'s naming
    rule now carries the "same material, renderer changed" case.

- 2026-09-20 (G3): **the operators fitted, sealed and read — and one finding that
  stops the wave at the user's desk** (claims §5.159; evidence
  `results/2026-09-20-w30-g3-operators/`). Contract X1 holds with nothing to
  report and `freeze.py verify` reads 1,818 intact at the child's open and close.
  What a later child, and the parent, have to carry from it:
  - **The blocking one. The fitted σ at a thin caster exposes a latent renderer
    defect that leaves a strip of the surface undrawn**, and the strip is visible
    — a row of page showing through the dark bed's 44 px capsule
    (`thin-sigma-band.png`). It is **not this wave's**: it reproduces on the
    macOS 27 light document as 0.19.0 ships it with `sigmaPx` set to 8, a leaf
    that has existed since W14, and no W30 leaf set above its inert value. It is
    the shadow's GEOMETRY and not its amplitude — zeroing the occlusion leaves the
    strip byte for byte, zeroing `offsetPx` moves it eight rows, zeroing
    `spreadPx` shortens it from eight rows to two, and its bottom edge sits 24 CSS
    px above the group field rect's own. It costs **170 texture cells outside
    W20's declaration conformance** where there were none. **Decision Log 5 is
    drafted in §5.159 §6 with three options and a recommendation** (a renderer
    child first, the shadow above the knee only, or re-pinning W20); the gate
    refuses all three of widening the bound, re-fitting σ around the defect, and
    merging with 170 gated cells outside an adopted bound.
  - **The second thing that stops it is a loader, not a material.** The demo reads
    `results/matrix.json` through one whole-file JSON import, and at the
    66,076,556 bytes this child's read leaves after its own split that import
    crosses a hard conversion limit in the test runner's Rust bridge where
    55,768,930 bytes passed. The page still builds; the suite that reads it does
    not load. About 10 MB of the growth is the 270 ladder probe rows Decision Log
    2 (a) granted, which are the evidence the scatter's shape was decided on, so
    the ruling is not the thing to reconsider; the fix is the build-time reduction
    clause 6's "every reader of the matrix reads the generation by name" already
    points at, and it is G4's (claims §5.159 §6b).
  - **The two `ssimMean` rows this wave claimed are refuted rather than unmet.**
    The lever was right — the σ law mirrors fully onto the CSS tier and the group
    clip at span 160 goes 33.05 → 45.79 CSS px — and the rows move by 0.0002 where
    they need 0.016, because SSIM over a whole cell does not see a shadow's width.
    A row claimed through a lever needs the lever AND an instrument that reads it;
    §5.156 §7 (c) had the first and not the second.
  - **The scale axis §5.156 §3 found is not expressible by the spanning set, and
    the reason is structural rather than a matter of values.** The analysis pass's
    per-source statistic is read off a fixed 64 × 64 grid, which is what makes it
    independent of the resolution policy and therefore the same number at both
    scales — measured 0.170 against 0.176 on one scene. Closing it is a change to
    the analysis pass, which is a second operator and the user's to charter.
  - **A clause can be met by a crutch.** W20's declaration conformance read 1.0 on
    every span-44 capsule while the shadow was six times too wide, because the
    shadow's own coverage filled what the material's did not. Narrowing the shadow
    to the reference's width is what made the reading fall. The general form:
    *a bound that passes while a neighbouring constant is wrong may be passing
    BECAUSE it is wrong.*
- 2026-09-20 (G1 review closure): **the split's review folded — no blocking finding, twelve items
  closed** (claims §5.157 §10, a new Review closure section; evidence
  `results/2026-09-20-w30-g1-split/classifier-selftest.txt` and `append-check.v2.txt`). Nothing
  recorded was rewritten: every correction is a dated paragraph beside the text it corrects, and the
  re-run append-check is committed as a second reading beside the first rather than over it. The
  three that change what a later child does. (i) **The tool now holds X1 and its own reruns**: a row
  of a frozen macOS 26.5 profile selected to move is refused before a byte is written, `apply`
  requires `--evidence` and `--claims` explicitly — with no defaults, G4's rerun cannot overwrite
  G1's before-manifest or label a new generation with G1's section — and every destination, index
  entry and manifest is checked over the whole plan first. G4's invocation is written out in §5.157
  §8, in the script's docstring and in `results/superseded/README.md`. (ii) **The naming rule now
  covers the generation it could not name**: where only the receded document moved and the active one
  still ships, the file is the compound `<active>-<receded>.json` with both hashes in the index,
  produced rather than refused; `classifier-selftest.py` exercises that and four other shapes the bed
  does not contain, including a `capturePath` carrying a third document clause, which is now refused
  rather than judged on the clauses that happen to parse. (iii) **The demo's generation is a term in
  the order, not a timestamp**: retiring the `capturedAt` tie-break moved `reportsFor`'s head for 210
  of 312 (scene, scheme) pairs and for 20 of the 32 scenes the picker offers in the dark scheme, inert
  only because `Stage.tsx` renders a report where a native capture exists and the 12 displayed dark
  scenes each carry the dark primary row. `primacy` now ranks a row at the documents on disk ahead of
  one that is not — profile, then tier, then generation — with the shipped hashes derived from the
  documents' bytes at build time, so the page stays right in the interval between a capture that
  appends a generation and the split that retires the one it superseded. Two items are **G4's** and
  logged rather than fixed: the pair's three "macOS 26.5" labels beside a macOS 27 caption, and
  `CLAUDE.md`'s retired "`rm results/matrix.json` … or reduce to the newest row per key" — both
  clause 7's. And one the review did not find, because the closure's chain ran a suite G1's did
  not: `pnpm --filter demo test:e2e` was **red**. G1's own copy names
  `packages/calibration/results/superseded/` in an inline `<code>` inside a list item, one
  unbreakable 346 px token in a 232 px line, and the page scrolled 94 CSS px sideways at 320 px —
  `DESIGN.md` §9's reflow floor, failing. Attributed to G1 by re-running with the closure's only
  page-affecting file reverted, and fixed in `site.css` (inline `code` in prose takes
  `overflow-wrap: anywhere`; a code BLOCK still scrolls inside itself). **A child that changes the
  page's copy runs the page's suite** — G1's chain stopped at `pnpm -r test` and the demo build.
- 2026-09-20 (G0 review closure): **Decision Log 3 executed** under claims §5.156 §9, which is the
  new section listing each finding, the ruling it executes and what closed it. The review reproduced
  every figure of both cuts and found nothing wrong with the measurements; all ten findings were in
  the declarations. Every correction is recorded **beside** the text it corrects and dated, and the
  three cut outputs gained sections without losing one. What a later child has to carry from it:
  - **B3's stop is the WebGPU tier's 0.00035**, not 0.0007 bed-wide — twice as tight on the tier
    that is fitted, with the both-tier 0.00079 recorded beside as the CSS tier's, and a committed
    script (`departure-stat.py`) so G3 and G4 re-run the statistic instead of transcribing it.
    §5.154 §3's 0.00074 is qualified beside as a fit-loop residual that this file does not
    reproduce under any partition.
  - **B1's effective tolerance on the light document is ±0.685 %, not ±5 %**, because one document
    serves four beds and the windows intersect; `sigmaSpanRefPx` is held at 96 to remove the law's
    flat direction, its inert default still 0. A 1x-only fit fails 2x light by −6.08 %.
  - **B4 binds the four standard beds**; the two accessibility beds are reported, and the ladder
    clause is read on the macOS 27 probe rows Decision Log 2 (a) grants.
  - **The holdout drop is now end to end**: `fit.py render` refuses a holdout `--set` or `--scene`
    without `--with-holdout`, because it writes `compare`'s stdout to a log a `cat` can read.
  - Two readings of the record were qualified rather than corrected: §5.156 §1's file counts are
    stale after G1's split and the 1,107 pin is unmoved, and §3's row counts are of the
    metric-carrying subset where the generation's are 455 and 1,107.
  Nothing under `results/2026-09-16-w29-freeze/` was touched and `freeze.py verify` reads 1,818
  intact at this closure's open and close. No material constant, document, fixture, golden, bound,
  floor or matrix row moved; no leaf was added; no capture was taken.
- 2026-09-20 (G0): **G0 closed** under claims §5.156; six commits, each its own clause. Nothing
  under `results/2026-09-16-w29-freeze/` was touched — v1's exemption reader stays withdrawn and
  `freeze.py verify` reads 1,818 intact at this child's open and close. Four Surprises recorded
  above, and three of them change what later children can do:
  - **The scatter's shape is not decidable from committed evidence**, because the macOS 27 bed
    carries no probe row. G2 lands the **spanning set** per Decision Log 1 (b), and the parent has a
    decision on whether G4's canonical read includes the probe set. G0's tables do fix everything
    the spanning set needs to be written: the scheme-conditioned leaf under either shape, its inert
    default, and the per-source statistic candidate (ii) would key on (`stats` is `[encoded mean,
    linear variance, edge density, sample count]` per source, already computed in the analysis pass).
  - **The σ law's floor is CSS px and its value is declared unfitted**, which resolves the Design's
    open "device px or CSS px" in the second direction and for a measured reason.
  - **The padding grows at the large spans**, so X8's recomputation at G3 is not only a shrink.
  Two readings recorded beside existing ones rather than over them: §5.154 §4's span-32 column is
  carried by a runaway fit (4.06 over four cells, 2.63 over the three that converge), and its
  thin-span "bed-wide median disagrees with the quoted cell" is explained — the quoted 1.84 is the
  untinted median and the 1.52 was pulled down by cells whose fit had collapsed.
- 2026-09-20 (G1): **the generation split executed** (claims §5.157; evidence
  `results/2026-09-20-w30-g1-split/`, layout `results/superseded/`). The working file holds one
  generation per profile — 1,107 macOS 26.5 rows unchanged and in their order, 455 macOS 27 rows at
  the four shipped documents — and W29 G3's 455 superseded rows moved byte for byte into two files.
  Three things the charter left to G1 to settle, settled: **the file name is the ACTIVE document's
  twelve-hex hash and a receded document never names a file** (it is a difference over its scheme's
  active document and cannot be read apart from it), so a light and a dark generation land in two
  files; a row is current only when *every* document it names is current; and finding a superseded
  row is a lookup in `results/superseded/index.json`, which maps every document hash — active and
  receded — to the file holding it. Three findings worth the parent's eye. (i) The freeze needed no
  exemption and no edit: it skips non-26.5 rows entirely and its positional counter runs over 26.5
  rows only, so deleting macOS 27 elements leaves all 1,107 entries identical — verified intact at
  1,818. (ii) **One cell leaves the working file**: the IC-coupled `hc-text__capsule-button__inactive`
  dom holdout row, §5.155 §3's "one of 456", whose newest reading is G3's because G3b's read produced
  none for it. It is holdout and inactive, so no gated number moves, and §5.157 §4 names it rather
  than rounding it away. (iii) A JSON round trip of this file is **not** byte-exact (Python's printer
  against V8's differs by ~6.5 kB), so rows move as raw text slices and the append-check proves it by
  reconstructing the pre-split file and matching its digest. The demo's bundle is 8.8 MB smaller as a
  side effect. G4 runs the same script with no arguments after its own read (X7).
- 2026-09-20 (G2): **the exemption spent**, under claims §5.158; one preparatory commit (the CSS
  tier's declarations recorded before a leaf existed) and one commit of substance. Contract X1
  holds with nothing to report: the two frozen macOS 26.5 documents, the seed, every fixture, every
  golden and every row of `results/matrix.json` are byte-identical to main, and `freeze.py verify`
  reads 1,818 intact at this child's open and close. Three things worth the parent's eye, beyond
  Decision Log 4, which this child's own measurement produced:
  - **The `@gpu` on-path case caught a defect every inertness proof was green over.** The three new
    uniform vec4s were packed at float offsets 117 / 121 / 125, none of them a multiple of four, so
    the shader read `localTone`'s padding as the σ law and each operator's words as its
    neighbour's. Every word involved is 0 on the landed material, so the 34 goldens, the identity
    test, the CSS declaration case and the whole unit chain passed over it. Only opening the gate
    could see it — which is the general lesson: *a proof that the OFF path is unchanged says
    nothing about whether the ON path is wired to anything.*
  - **A scatter operator measured on a pitch the body already erases measures as dead.** The first
    draft of that case ran on `refraction-checkerboard`, where a share of ±1 at a second width of
    40 CSS px moved exactly one 8-bit code, because a 10 px pitch is gone at the FIRST heavy width
    and both taps read the same flat mean. It runs on `lens-size-depth` instead. G3's fit inherits
    the trap.
  - **`sampledOuterShadowFactor` and the two group-level readers are now bounds in the code as well
    as in the prose**: the optics pass's pad takes the max over members of the occlusion and,
    separately, of the span; the CSS group-shadow clip takes the law at the widest carried cast.
    Neither is any member's value.

- 2026-09-20 (G2 review closure): **one blocking finding and six others closed**, under claims
  §5.158 §8, which is the section this note is the charter's half of. Nothing here changes what a
  later child does to the material; two things change what G3 inherits.
  - **The blocking one was a digest taken over a material nothing draws.** `reseal.ts` computed all
    six supersession records as `fingerprint(withMaterialOverrides(DEFAULT, patch))`, which is the
    construction for the four patch documents and the wrong one for the two receded ones: a receded
    document is a difference over the ACTIVE document of its own scheme, and W29 G3b's `seal.ts`
    sealed the pair over that composition. Recomputed, the two are `035f537d9c27e3ed` and
    `4763b0d195fdb077`, which is what the browser prints. **No document was re-sealed and no frozen
    byte moved** — Decision Log 4 (a) is untouched — and the corrections stand beside the recorded
    numbers rather than over them. The structural half is a closed loop where the digest is
    produced: the script asserts that the resolved material minus the eight leaves reproduces the
    document's own field, which only the right construction can do. **G3 inherits that shape**: the
    seal it runs should assert its own inverse, and `tuned-profiles.test.ts` now recomputes all six
    from the documents so no pin ends at the record it came from.
  - **Three of the wave's zeros were standing in for measurements and were read at zero only.** The
    `@gpu` case opened one of the three new vec4s; the scale statistic's unobserved fallback was 0
    rather than the material's reference, which is the identity only while the reference is 0; and
    the reach's span argument defaulted to 0, which is an under-bound the moment a slope exists.
    Each is closed by reading it at a value the fit will produce, and that is the closure's general
    lesson beside the wave's own: *an operator landed at an identity makes a lane assignment, a
    fallback, a default and an unexercised path all indistinguishable from correct.* **G3 inherits
    a constraint as a test**: `outerShadowReachPx`'s doc comment states that a group's
    `reach(max occlusion, max span)` is a bound while `sigmaSlopePerSpan ≥ 0`, and
    `w30-inert-laws.test.ts` asserts the monotonicity at the fitted shape, so a fit that produced a
    negative slope fails there rather than at a scissor.
  - The rest are coverage and record-keeping: the CSS declaration bed extended to both accessibility
    regimes against a second fixture recorded on the pre-leaf tree, a capture-path case admitting a
    document that names all eight leaves, the eight §5 proof rows that had no committed output
    rerun and committed, and one clause naming the finite operands the multiplied-zero argument
    assumes. Chain 2,549 over 173 against the merge's 2,541 over 173; freeze intact at 1,818;
    goldens 34/34 with no regen; `test:gpu` 31 passed.

- 2026-09-20 (the parent): **adversarial review folded** (opus, read-only; two blocking, fourteen
  should-fix, six minor). Folded: the exemption's shape withdrawn and replaced by supersession beside
  the document (finding 1, 2); the exemption its own child with proofs on both tiers, algebraic inert
  identities and the plumbing sites named (3, 4, 26); the spanning leaf set where G0 cannot choose
  (5); "eight hashes, four macOS 26.5" and the seed's entry (6, 7); the joint refit of the amplitude
  anchors and `liftAmplitude` with the departure-residual stop (8, 30); the law per caster with the
  group readers as bounds (9); the acceptance statistic (10); the reduced-transparency row read on its
  own holdout cell, restated (11); the instrument on composites (12); the accessibility profiles' five
  rungs and the reduced-transparency structure residual declared (13); the second heavy tap's
  resource gated on its leaf (14); the lever per claimed row, the `ssimMean` rows the shadow's (15);
  scheme conditioning as two values in two documents (16); `sizeToneLevelFar` kept out of
  `FITTED_CONSTANTS` (17); tolerances' fate declared and carried in at G4 (18); the layout rule
  applied twice (21); the consumer list corrected and `vibrancy.ts`'s provenance digest (22); the
  26.5 rows' order (23); G1 before G2 (24); `canonical-read.sh` copied, not reused (28); the recede's
  exterior cited with an expectation (29). Dismissed with reason: (25) the matrix split put back to
  the user — the user delegated it in so many words after the parent named it; recorded in Decision
  Log 1 (d) and left overridable. Holds as reviewed: 19, 20, 27.
- 2026-09-20: v1 of this charter, drafted by the parent from a read-only grounding of the fingerprint
  mechanics, both operators as they stand in the shader and the CSS tier, the bed's set membership
  per pitch, the seven missed rows' causes, the cost of a read, and the W29 Deferred list and tracker.
