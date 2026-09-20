# W30 — the operator wave: the span-graded shadow and the scale-selective scatter, under one exemption

**Status: CHARTERED 2026-09-20 (the parent, on the user's word "operator wave first, and rest on
your judgement" after the 0.19.0 publish); not yet reviewed; no child dispatched.** Executes W29
Decision Log 7 (a) and W29 Deferred item 1. Grounded on main at `4a4c941a` (0.19.0 published).

## Purpose

macOS 27 changed two things in Apple's material that the operators vitrea has cannot express, and
0.19.0 ships both as the best single compromise its constants admit.

The first is the outer shadow's blur. On macOS 26.5 it was span-invariant — a positive measurement,
σ within 15.4–15.9 CSS px across spans 32–160, recorded in `MaterialOuterShadow`'s own header — and
`sigmaPx` is one constant the shader reads from a uniform. On macOS 27 the blur is linear in the
casting span above span 96 (σ_css ≈ 0.133 · (span − 30), holding to 0.1–0.5 % at 1x and 1.7–6.6 %
at 2x; claims §5.154 §4 as corrected) and nearly constant in DEVICE px below it. 0.19.0 fits the
thick regime and ships the thin cells' shadow **5.97× too wide at 1x and 2.80× at 2x**, carrying the
right energy in the wrong shape, which is why the departure residual does not show it. The casting
surface's span is already in the shader one argument away from the σ uniform, and the CSS tier
already emits one `box-shadow` per surface with the span in scope.

The second is the diffusion. At the fitted point the light interior's spread reads **+0.044 over the
16 px checkerboard and −0.028 over both a finer (4 px) and a coarser (photograph) backdrop** (claims
§5.153 §6): Apple's material passes less structure than vitrea at one pitch and more at both sides of
it, which a positive mix of two Gaussians — monotone in frequency — cannot do at once. And the residual
changes sign with the colour scheme: on `checkerboard__rrect-md__rest` the WebGPU tier passes
**1.77×** the native structure in light and **0.55×** in dark, the CSS tier 1.04× and 0.32×
(§5.154 §9 (c); the tracker's "two tiers miss the backdrop's structure in opposite directions"). A
scatter fitted on the light bed alone lands on the wrong side of the dark one. Three of the seven
rows 0.19.0 records as missed sit on this residual and on the shadow's reach at the largest spans.

Both operators add leaves to the renderer's `DEFAULT_MATERIAL_PROFILE`, and every shipped document's
`resolvedMaterialSha256` is a digest over the FULLY RESOLVED material — so both move the frozen
macOS 26.5 pair's digests even though no macOS 26.5 pixel moves. That is why the user ruled them one
wave under a **single one-time X1 exemption** (W29 Decision Log 7 (a)), the class W29 Decision Log
1 (i) reserved, and why chartering them apart would spend two.

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

1. **The exemption is one commit, digest-only, and proven so.** Before any leaf lands, the fully
   resolved macOS 26.5 light and dark materials are written to disk as JSON and committed as
   evidence. The wave's new leaves land in ONE commit at inert defaults; that commit re-records the
   two macOS 26.5 documents' `resolvedMaterialSha256` with the prior digest kept in each document's
   `$comment-sha-history` (the project's own idiom, twelve entries deep), re-records the four
   `window-activation.spec.ts` hashes and the two hand-written digests in `material-document.ts`,
   and writes an **exemption record** beside the W29 freeze — `sha256.txt` itself is not edited —
   that names the two entries, both hashes, and this Decision Log. `freeze.py verify` reports the
   freeze intact with those two entries exempted by name, and a new test asserts that each macOS 26.5
   document's resolved material **minus the new leaves** deep-equals the committed pre-wave JSON. The
   34 renderer goldens are byte-identical and the 1,107 frozen macOS 26.5 matrix rows are unchanged.
   Nothing else under a macOS 26.5-keyed path changes, in this wave or after it: the exemption is
   spent once.
2. **The structure is measured before the operator exists.** From committed evidence only — the
   native delta's `shadowFalloffSigmaPx` per cell and the matrix's `interiorStdDev{Native,Web}` per
   cell — G0 tables the shadow's σ per span per scale per scheme (with the reading's own spread) and
   the body's structure ratio per pitch per scheme per tier, on the gated sets and on the probe
   ladder separately, and names from those tables the smallest operator shape each law needs. The
   CSS tier's own attenuation goes into `tier-coherence.test.ts` as a measured residual before any
   fit, as the tracker's fix shape asks.
3. **Bounds before reads; the targets named.** The 27 profiles' adopted tables stay at the values
   W29 Decision Log 4 ruled; no floor is adopted (the bed is at the seven-run bar). G0 declares, per
   operator, the wave's own acceptance — a tolerance on the fitted σ against the native σ per span
   class at both scales, and a tolerance on the structure ratio per pitch per scheme on the WebGPU
   tier with the CSS tier recorded — and names which of the seven `MISSED_27_ROWS` the wave claims:
   the two 1x-light dom `ssimMean` rows at the largest spans and the reduced-transparency
   `ssimOutside` row. The four dark `oklabDeltaEP95` rows are declared **expected unmoved**.
4. **Both operators land on the fidelity target with the CSS tier derived in the same commit.** The
   shadow's σ graded by the casting span on the WebGPU tier (`ou.shadow.y` becomes a law of
   `shadowAux.z`) and one `box-shadow` blur radius per surface on the CSS tier; the scatter made
   selective in the backdrop's spatial scale and conditioned by scheme on the WebGPU tier, with the
   CSS tier's single `backdrop-filter` given the best scalar projection and its residual recorded;
   `sizeToneLevelFar` fitted in the 27 documents if the read supports it (it is a leaf already, at
   default 0, named by no document — a free lever that costs no exemption). The macOS 27 documents
   re-sealed; `tier-coherence` green; the reach and both sampling pads recomputed from the new laws.
5. **Read once per frozen configuration.** Scratch matrices during the fit with the holdout dropped
   in the reader by construction; then, with the documents sealed and their hashes in the ledger, the
   canonical run appended beside the 0.19.0 rows — six profiles, two tiers, calibration + validation,
   about 13 minutes — and the holdout read **once**. The verdict per profile per tier per clause with
   every missed cell named; a miss is recorded, not widened, not re-fitted.
6. **The evidence layout is ruled and executed before the read.** `results/matrix.json` holds one
   generation per profile — the frozen macOS 26.5 rows and, per macOS 27 profile, the rows at the
   shipped documents — and superseded generations move to `results/superseded/<document-sha>.json`
   with a listing that names each by the document it was read at. The freeze's 1,107 row hashes stay
   in the working file and verify. Every consumer that names the matrix (nine files: `compare`,
   `diff`, `gates`, `report`, three tests, the demo's `calibration.ts`, `scripts/vibrancy.ts`) reads
   the generation by name, and the demo's `capturedAt` tie-break is retired.
7. **The landing.** The demo on the new operators with its tone stage re-ranged (Decision Log 1 (e));
   `GlassRootHandle` carries the selected document so `GlassToolbar` opens at its own material's
   blur, with the case the tracker names; the coverage matrix re-scored; `CLAUDE.md`, READMEs and
   CHANGELOG say what moved; sheets native | WebGPU | CSS | difference per profile at both scales
   with the thin spans first, because that is where the shadow is now read; the fixed group
   versioned **0.20.0** and prepared, `pnpm release` the user's hand.

## Grounding Baseline (main at `4a4c941a`, 0.19.0 published)

- **The fingerprint.** `fingerprint()` (`results/2026-09-19-w29-g3-refit/seal.ts`, duplicated in
  `test/tuned-profiles.test.ts` and `test/macos26-document-selection.test.ts`) is SHA-256 over
  `withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch)` with keys sorted, first 16 hex. Six sites
  move at any new default leaf: the two macOS 26.5 documents' `resolvedMaterialSha256`
  (`b2b570e4adcea8fb`, `874be66ea501621b`); the four macOS 27 documents (re-sealed by the fit
  anyway); `material-document.ts`'s two hand-written 26.5 digests; `macos27-profile.ts`'s four;
  `window-activation.spec.ts`'s eight; and the W29 freeze's entries 652 and 653 (the two macOS 26.5
  profile files' byte hashes). Tests that go red: `tuned-profiles`, `macos26-document-selection`,
  `macos27-profile-export`'s digest case, the `window-activation` spec, and `seal.ts`'s X1 loop. The
  goldens do NOT move — `isolation.spec.ts` renders an explicit patch and an inert leaf changes no
  pixel — and the 1,107 frozen matrix rows do not move (G3b's append-check: 1107/1107, 0 changed).
- **The shadow operator.** `MaterialOuterShadow` (`material.ts:361–541`): `offsetPx`, `sigmaPx`,
  `spreadPx`, three thin and three thick occlusion anchors, four lift constants, the reduced-
  transparency flattening, `sizeGain`. In the shader `outer_shadow_thick(spanCss)` already
  interpolates the AMPLITUDE through 96/128/160 and the caster's span is `shadowAux.z`; the falloff
  is `outer_shadow_falloff(…, ou.shadow.y)` with `ou.shadow.y` the one σ uniform. `shadow`,
  `shadowSize` and `shadowThick` are all four-components-full, so a σ law needs a new uniform.
  `outerShadowReachPx(shadow, occlusion)` bisects on `shadow.sigmaPx` and must take a span;
  `renderer.ts` maxes occlusion over surfaces and must max the REACH. CSS: `outerShadowDeclaration`
  emits `box-shadow` with blur `2σ`, called per surface with `surface.spanPx` in scope; two further σ
  readers want the max over members (the group-shadow clip reach in `root.ts`, and
  `sampledOuterShadowFactor`). The instrument exists: `metrics/shadow.ts` fits `falloffSigmaPx` per
  cell as a blurred edge against an exponential alternative and reports both residuals.
- **The law as read** (§5.154 §4, bed-wide medians, CSS px; cell count in brackets):

  | bed | 32 | 44 | 96 | 128 | 130 | 160 |
  | --- | ---: | ---: | ---: | ---: | ---: | ---: |
  | 1x light | 4.06 (4) | 1.52 (22) | 8.80 (16) | 13.14 (8) | 13.36 (2) | 17.30 (13) |
  | 2x light | 2.38 (8) | 1.93 (25) | 9.36 (16) | 13.30 (8) | 13.58 (2) | 17.58 (13) |
  | 1x dark | 2.05 (3) | 1.54 (14) | 8.87 (10) | 13.19 (5) | 13.42 (1) | 17.45 (11) |
  | 2x dark | 1.89 (7) | 2.85 (14) | 9.38 (10) | 13.42 (5) | 13.74 (1) | 17.68 (11) |
  | 1x reduced transparency | — | 1.50 (5) | 8.59 (2) | — | — | 16.97 (1) |

  Above 96 every scale and scheme agrees to a few percent; below 96 the per-cell spread is 1.11–4.08
  at 1x light and 0.57–9.70 at 2x light, the span-32 column rests on three or four `rrect-sm` cells,
  and the quoted span-44 cells read 1.84 at 1x against 3.92 at 2x — a ratio of 2.13, the device
  pixel ratio. Whether the thin regime is Apple's material or the instrument's limit (two or three
  rings above the body's own edge at σ ≈ 1.8) is not settled by this bed.
- **The scatter operator.** Flattened into `MaterialProfile`: `sizeScatterGainMax`, `sizeScatterFloor`,
  `sizeScatterSpanMax`, the 2x trio, `sizeScatterGainFar2x`, six ramp starts and two reaches, the
  two declined thick-share lifts, `sizeHeavyTapSigma{,2x}`; all gated by
  `sizeThickness = smoothstep(32, 96, span)`. GPU mechanism (`wgsl/optics.ts:855–897`): one body
  sample, one chain sample at `scatterLod = clamp(bodyChainLod + log2(gain), 0, maxLod)` — replaced
  by the dedicated `backdropHeavy` texture where `sizeHeavyTapSigma` is set — then
  `mix(body, scatter, kScatter)`. The full chain, the body texture and the heavy texture are all bound
  per pixel, so extra taps and uniform leaves land without a new pass; chain mips are 13-tap
  platykurtic low-passes rather than exact Gaussians, and a second EXACT Gaussian at an out-of-chain
  width is another separable build (0.070 ms, W26 Decision Log 2 (b)). The analysis pass already
  computes mean, variance and edge density per SOURCE; the heavy width is per source, not per pixel,
  which fits an operator conditioned on backdrop scale (a per-source quantity) rather than on span.
  CSS: `blurRadius = source.blurSigma · blurSigmaScale` (2.2 on macOS 27); the tier does not mirror
  `sizeHeavyTapSigma` and has no backdrop-frequency statistic, so a selective law can only be
  projected onto a refitted scalar there.
- **The bed.** Each macOS 27 standard profile carries 45 pitch-ladder fixtures (`checkerboard-4/8/
  32/64`, `checkerboard-lc16`, `hc-text-7/28`) — **every one of them `probe`**, 0 in calibration, 0
  in validation, 0 in holdout. The gated sets carry the 16 px checkerboard, `hc-text` (14 px rows),
  `photo`, `impulse` and the solids: 37 calibration / 12 validation / 20 holdout distinct scenes,
  8 recorded, 91 probe. So the operator is fitted on probe rows and judged on three distinct pitches,
  and no native capture is needed.
- **The seven missed rows** (`MISSED_27_ROWS`), all holdout. Unreachable by these operators: the four
  dark `photo__rrect-lg__rest :: oklabDeltaEP95` rows (chromatic; the tone solve is achromatic by
  construction). Reachable: `checkerboard__rrect-lg__rest :: ssimMean` 0.88402 and
  `checkerboard__glass-over-glass__rest :: ssimMean` 0.89538 on 1x-light dom (bound ≥ 0.9), and
  `photo__rrect-lg__rest :: ssimOutside` 0.82707 on reduced transparency dom (bound ≥ 0.83) — the
  last scored OUTSIDE the silhouette, at span 160, on the one profile whose σ reads 16.97 against the
  shipped 11.0, and the single row the G3b refit worsened (0.82736 → 0.82707). The shadow, not the
  scatter, is its lever.
- **The recede.** On macOS 27 the recede keeps the outer shadow (§5.154 §5), so a span-graded σ
  moves receded exterior readings at the largest spans; the receded documents carry their active
  document's `outerShadow` block leaf for leaf. No bound is gated on the inactive pose; the recede's
  own declared bound holds on 1 of 12 profile-tiers and its worst cell is chromatic on every row.
  The receded exterior above span 96 has no non-holdout inactive cell to fit on (tracker).
- **The cost of a read.** G3b's like-for-like precedent: calibration + validation 9:17 wall clock
  (332 rows), holdout 3:50 (123 rows) — **about 13 minutes and 455 rows**, 0 changed, 0 missing,
  the 26.5 half untouched. `canonical-read.sh` refuses at any bytes but the sealed documents and is
  reusable as-is. The 12 h 49 m figure in W29 is the native sitting, which this wave does not repeat.
- **The matrix.** 72,102,187 bytes; two macOS 27 generations; the demo's `reportsFor` breaks the
  generation tie on `capturedAt` descending and says so in its own comment. Nine files name the
  canonical path.
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

**The exemption's shape (ruled, Decision Log 1 (a)).** Re-record in place with history, and record the
exemption beside the freeze rather than in it. Of the four shapes weighed — re-record in place; a
second digest field keyed by schema version; a fingerprint over only the leaves a schema version
knows; a fingerprint-excluded section for the new leaves — only the first keeps the instrument whole.
The second does not avoid the exemption (the file gains bytes, so entries 652 and 653 move anyway)
and puts one number in two places. The third and fourth avoid the exemption by making the pin blind to
exactly the class of change it exists to catch: `tuned-profiles.test.ts` is there so that a renderer
default cannot change without the profile being re-recorded, which is the `sizeOcclusionGain` failure
its comment was written after, and a version-scoped or excluded leaf is a default that can change
silently forever. What "evidence never rewritten" protects is the READING: the old digest is kept in
`$comment-sha-history` with what moved it, the freeze manifest is not edited, and the pre-wave resolved
materials are committed so the identity claim is checkable by anyone, not only by whoever ran the
commit.

**The exemption's timing.** ONE commit, early in G2, containing the new leaves at inert defaults and
nothing else: the inert values are the ones under which the macOS 26.5 material renders bit-identically
(a σ law whose output equals `sigmaPx` at every span; a scatter term with zero weight), the goldens
prove the default, and the identity test proves the documents. G2's fits then move only the macOS 27
documents' values, which are not frozen. G0's cut must therefore settle the LEAF SHAPE before G2
opens — the number and meaning of the leaves, not their values — because a second shape is a second
exemption. Where G0 cannot settle a shape from the evidence, it says so and the parent rules.

**The shadow's σ law (advisory).** σ_css(span, dpr) as a clamped line: `sigmaSlope · (span − sigmaSpan0)`
above a knee, held at a floor below it, with the floor expressed in device px if G0's cut confirms the
thin regime is nearly constant there (the 2.13 ratio) and in CSS px if it does not. Inert defaults:
slope 0, floor = `sigmaPx`, so the macOS 26.5 material is unchanged. The thin regime's reading has a
wide instrument error and the charter does not require the thin cells to be FITTED — it requires them
to be no longer 2.8–7.2× too wide, and the acceptance tolerance G0 declares says how much. The reach
takes the span; the renderer maxes the reach over surfaces; the CSS tier's blur radius is per surface
and the two max-over-members readers follow.

**The scatter (advisory, the shape G0's cut names).** Two candidates and G0 chooses on the tables:
(i) a second heavy tap at its own width with a signed weight, which makes the kernel non-monotone in
frequency and is what a notch needs; (ii) a mix that is a function of the source's measured spatial
scale (the analysis pass's variance and edge density) rather than of the span alone. Either is
conditioned by scheme, because the dark bed inverts the light bed's sign. G0 also tables
`sizeToneLevelFar`'s conditioning on the probe ladder in both schemes, since W25 declined it for a
sign that flipped with the row set; if the macOS 27 ladder gives it a stable sign it is fitted in the
27 documents with no exemption cost. The CSS tier gets the best scalar and its residual in the ledger,
per the tier rule (Decision Log 23 of 2026-09-05, quoted in `CLAUDE.md`: a material change lands on
the target and the CSS tier carries what its two layers can).

**The matrix's generation split (ruled, Decision Log 1 (d)).** Split by generation. The working file
keeps one generation per profile — the frozen macOS 26.5 rows unchanged in place, and the macOS 27
rows read at the SHIPPED documents — and every superseded generation goes to
`results/superseded/<document-sha>.json`, pretty-printed as before, with `results/superseded/README.md`
listing each file by profile, document hash, the claims section that read it, and the date. "Which
generation is the shipped one" becomes a name; `atAShippedDocument` becomes a lookup; the demo's
`capturedAt` tie-break is retired; a superseded row is still one `git show` away. Executed by G1
before G3's read, so the file the read appends to is small and stays so.

**The tone stage (ruled, Decision Log 1 (e)).** Re-range. The stage was built to make a size-gated
separation visible, and on macOS 27 that separation exists over the bright half of the slider and
closes at the dark end; so the slider's resolution moves to where the plates separate, with the
near-black stop kept as the last position so what macOS 27 does there — no convergence — remains one
drag away and the prose G4 wrote stays true. Not retired, because the behaviour it demonstrates is
still real; not re-subjected to the curve, because a demo of a curve is a chart and this is a
material site.

**Padding, deliberately.** G2 recomputes `outerShadowReachPx` from the σ law (max over surfaces) and
the CSS sampling pad from the effective blur; G3 carries the selected document on `GlassRootHandle`
and passes it through `GlassToolbar` (the additive, local fix shape), with the case: a React toolbar on
`macos26MaterialProfileDocument` whose gap equals the macOS 26.5 padding rather than 2.2× it. Whether
`samplingPaddingFor`'s core advisory constant should be retired is NOT decided here; the tracker entry
stays open with this wave's numbers added.

**The holdout drop, by construction.** G0 moves the drop into `fit.py`'s `readings()` with the count
printed and a `--with-holdout` flag, so every reader this wave and later waves build inherits it.

## Children

### G0: The cut and the declarations — no material change

*Opens on main after the charter's review is folded. Read-only on the material; writes evidence,
tables, tests and declarations.*

- (a) Write the fully resolved macOS 26.5 light and dark materials to
  `results/2026-09-20-w30-g0-cut/resolved-26.5-{light,dark}.json` (through the same
  `withMaterialOverrides` path the fingerprint uses, keys sorted) and commit them before anything
  else. Add the freeze's exemption reader: `freeze.py verify` accepts an `exemptions.json` beside
  `sha256.txt` (path, recorded hash, exempted hash, Decision Log, date) and reports intact entries
  and exempted entries separately; with no exemption file present its output is unchanged.
- (b) The shadow cut: from `results/2026-09-19-w29-g2-native-delta/native-delta.json` and the
  G3b rows, σ per span per scale per scheme per backdrop class with the per-cell spread, on the gated
  sets and on the probe ladder separately, at both scales; the thin regime's device-px hypothesis
  tested on the cells that carry it; the reach the shipped constant implies against the reach the law
  implies at spans 32/44/96/128/160. Name the σ law's leaf shape.
- (c) The structure cut: `interiorStdDev{Native,Web}` per pitch (4/8/16/32/64, lc16, hc-text 7/14/28,
  photo, solids) per scheme per tier per span, active and inactive, from the committed matrix — the
  tracker's precondition. Name the scatter's leaf shape from it, or say the tables cannot choose
  between (i) and (ii) and put the choice to the parent. Table `sizeToneLevelFar`'s sign on the
  macOS 27 ladder in both schemes.
- (d) Carry the CSS tier's measured attenuation into `tier-coherence.test.ts` as a recorded residual
  (the numbers from (c)), so the fit does not discover it.
- (e) Declarations, committed before G2 opens: the wave's per-operator acceptance tolerances; the
  three claimed rows and the four expected-unmoved rows; the 27 tables unchanged; no floor.
- (f) The holdout drop in `fit.py`'s `readings()`, count printed, `--with-holdout` for the canonical
  read; `shadow-table.py` reads through it.
- Ledger: **§5.156**. Evidence: `results/2026-09-20-w30-g0-cut/`.

### G1: The matrix's generation split — parallel with G0, merged before G3

- Execute Decision Log 1 (d): move the superseded macOS 27 generation(s) out of `results/matrix.json`
  to `results/superseded/<document-sha>.json` with the README listing; the working file holds the
  frozen macOS 26.5 rows unchanged (the freeze's 1,107 row hashes verify against it) and one macOS 27
  generation per profile; every consumer names the generation rather than the timestamp (`compare`,
  `diff`, `gates`' `atAShippedDocument`, `report`, `backdrop-mode`/`adopted-thresholds`/
  `compare-gates` tests, the demo's `calibration.ts`, `scripts/vibrancy.ts`); the demo's tie-break
  retired and its comment rewritten; an append-check that proves every moved row is byte-identical in
  its new file and no row was lost. File sizes before and after in the ledger.
- Ledger: **§5.157**. Evidence: `results/2026-09-20-w30-g1-split/`.

### G2: The operators — the shadow first, then the scatter; the exemption spent once

*Opens after G0's declarations are committed and the parent has ruled any shape G0 could not.*

- (a) **The exemption commit**: every new leaf of both operators at inert defaults, in one commit,
  with the six digest sites re-recorded, `$comment-sha-history` extended in both macOS 26.5 documents,
  `exemptions.json` written, the identity test green against G0's resolved JSON, goldens 34/34
  byte-identical, `freeze.py verify` intact with two exempted by name. Nothing else in the commit.
- (b) The shadow: the σ law on the WebGPU tier (uniform, falloff, reach with span, renderer maxing
  the reach) and the CSS tier per surface in the same commit; fitted on the calibration set per
  profile on scratch matrices through the reader with the holdout dropped; checked on validation;
  `tier-coherence` green; the 27 documents (active and receded, per scheme) re-sealed. The receded
  documents inherit the law leaf for leaf as they inherit the block today.
- (c) The scatter: the shape G0 named, conditioned by scheme, on the WebGPU tier; the CSS tier's
  scalar projection with its residual measured; `sizeToneLevelFar` fitted or declined with the reason;
  fitted on calibration + probe rows, checked on validation; the increased-contrast-coupled profile
  fitted as W29 Decision Log 5 placed it.
- (d) Padding: `outerShadowReachPx(shadow, occlusion, span)`, `samplingPaddingFor` and the CSS pad
  recomputed; the diagnostics that read them green; the numbers recorded.
- (e) `PREDICATE_EXCLUDES` and every count test moved to what the machine says; README paragraphs
  for the new leaves; a changeset for the fixed group (a `@vitreajs/vitrea-web` minor at least).
- Ledger: **§5.158**. Evidence: `results/2026-09-20-w30-g2-operators/`.

### G3: The sealed read, the verdict, and the landing — 0.20.0 prepared

- (a) RT and IC read 0, `NSGlassTintAmount` 0.5, one capture process, idle ≥ 60 s; the sealed
  documents' hashes in the ledger before the read; `canonical-read.sh` over six profiles × two tiers,
  calibration + validation appended beside the 0.19.0 rows; then holdout **once**. The append-check.
- (b) The verdict per profile per tier per clause against the unchanged 27 tables and G0's
  declared tolerances; the three claimed rows and the four expected-unmoved rows each named with
  before and after; every miss recorded and a Decision Log entry drafted for the user where a
  ruling is needed (a bound to adopt into `adopted-thresholds` from G0's tolerances; a miss to accept).
- (c) The landing: `GlassRootHandle` carries the selected document and `GlassToolbar` passes it, with
  the tracker's case; the tone stage re-ranged with its cases moved against the committed reading; the
  demo's figures on the new operators; `CLAUDE.md`, READMEs, CHANGELOG; the coverage matrix re-scored;
  sheets with the thin spans first; the fixed group versioned 0.20.0, dry runs green, unpublished.
- Ledger: **§5.159**. Evidence: `results/2026-09-20-w30-g3-landing/`.

## Cross-Child Contracts

- **X1 — the freeze, with exactly one exemption.** Two entries of 1,818, digest-only, spent in G2 (a)
  and never again; `freeze.py verify` at every merge reports intact plus two exempted by name; the
  identity test and the 34 goldens are the pixel proof. No other macOS 26.5-keyed path, row, bound,
  floor or document changes.
- **X2 — the cut precedes the operator.** G0 names each leaf shape from committed evidence before G2
  writes a leaf; G2 adds no leaf G0 did not name without the parent's ruling.
- **X3 — the operators change nothing outside the two named structures** (the shadow's σ and the
  diffusion's scale and scheme conditioning), plus the leaf that already exists (`sizeToneLevelFar`).
  A fit that moves the four chromatic rows is reported as a warning, not claimed.
- **X4 — bounds before reads; holdout once; a miss is recorded** (as every wave). The reader drops
  holdout by construction from G0 (f) on.
- **X5 — no native capture; the granted bundle is never rebuilt and nothing is added under its
  identifier.** Every fixture the wave fits on is on disk from W29.
- **X6 — RT and IC 0, the slider 0.5, one capture process, ≥ 60 s idle** before every browser run;
  every read recorded.
- **X7 — the evidence layout changes once, in G1, before G3's read**; every superseded row stays
  one `git show` away; the freeze's row hashes verify against the working file.
- **X8 — padding is touched deliberately**: G2 recomputes it from the laws and records the numbers;
  G3 closes the toolbar seam; the core advisory constant's retirement is not decided in this wave.
- **X9 — no GPT-rung agents**; children and reviews are opus `general-purpose` (read-only for
  reviews); ledger sections assigned above; merges `--no-ff` with the freeze verified at each; no
  attribution trailers.

## Ordering & Dependency Map

Charter review → fold → **G0 ∥ G1** → (the parent rules any shape G0 could not name) → **G2** →
merge G1 if not already → **G3** → the user's eye on the sheets → `pnpm release` (the user) → tag.
After this wave, in the order W29 Deferred kept: the chromatic-transmission child; the identifying
sitting on the 27 bed; the highlight directionality reader; the decoupled-contrast flag and its read;
the motion-metrics harness.

## Risks & Mitigations

- **A second leaf shape mid-fit** would be a second exemption. G0's cut is the mitigation; where the
  evidence cannot choose, the parent rules before G2 rather than G2 guessing.
- **The thin shadow regime is the instrument's limit, not Apple's law.** The acceptance is stated as
  "no longer 2.8–7.2× too wide within G0's tolerance", not as a fit to the thin medians; the
  device-px hypothesis is tested on the cells that carry it before a leaf is shaped around it.
- **A light-only scatter fit lands on the wrong side of dark** (§5.154 §9 (c)). The scheme
  conditioning is in the leaf shape from G0, and the dark bed's structure tables are part of the
  declaration.
- **The probe ladder is fitted on and the gated sets carry three pitches**, so the verdict cannot
  see a fit that only matches the ladder. The three claimed rows are on the gated pitches; the ladder's
  own residuals are reported per pitch in the ledger so a fit that helps 16 px and hurts 4 px shows.
- **The read appends to a 72 MB file.** G1 lands first (X7).
- **The recede's exterior moves with the σ law at spans it has no calibration cell for.** Reported on
  the inactive holdout rows as readings, not fitted; the tracker's scenes decision stays open.
- **The padding shrinks at thin spans**, which is the direction that can expose a sampling floor. G2
  runs the diagnostics that read the pad and records the smallest pad the laws produce at each span.

## Deferred / Out of Scope

The chromatic transmission (W29 Decision Log 6 (c)); the highlight's angular reader; the decoupled
increased-contrast read and `compare`'s flag; the identifying sitting; the motion-metrics harness;
the CSS tier over pure black; inactive calibration cells above span 96 (a `scenes.json` decision;
evidence-visible); `samplingPaddingFor`'s advisory constant; the Reduced Transparency opacity policy
and the impulse specular point (tracker); the slider's ends as evidence classes.

## Tracking Map

| Child | Status | Claims section | Evidence |
| --- | --- | --- | --- |
| G0 | not dispatched | §5.156 | `results/2026-09-20-w30-g0-cut/` |
| G1 | not dispatched | §5.157 | `results/2026-09-20-w30-g1-split/` |
| G2 | not dispatched | §5.158 | `results/2026-09-20-w30-g2-operators/` |
| G3 | not dispatched | §5.159 | `results/2026-09-20-w30-g3-landing/` |

## Decision Log

### Decision Log 1 — the charter (2026-09-20; the parent, under the user's "operator wave first, and rest on your judgement")

Ruled by the user on 2026-09-19 (W29 Decision Log 7 (a)): both operators in one wave after 0.19.0
under a single one-time X1 exemption. Ruled by the parent here, under the user's delegation, each
overridable by the user before G2 opens:

- (a) **The exemption's shape**: re-record in place with the prior digest kept in
  `$comment-sha-history`; the freeze manifest not edited; an `exemptions.json` beside it naming the
  two entries; the pre-wave resolved materials committed as evidence and an identity test over them.
  Reasoning in Design.
- (b) **The exemption's timing**: one commit at the start of G2 with every leaf at its inert value,
  after G0 has named every leaf's shape. A second shape is a second exemption and needs the user.
- (c) **The order inside G2**: the shadow first, because its law is read and its shape is nearly
  certain; the scatter second, on G0's tables.
- (d) **The matrix's layout**: split by generation, executed by G1 before the read. G4's
  recommendation, seconded for its reason (a name where a timestamp stands) and for this wave's
  reason (the read that would cross 100 MB).
- (e) **The tone stage**: re-ranged, the near-black stop kept last. Reasoning in Design. The user may
  prefer retirement; the geometry is untouched until G3 so the choice is still open at G3's dispatch.
- (f) **Closed on the way**: the reader-side holdout drop (G0) and the `GlassToolbar` document seam
  (G3), both because this wave touches the code they live in.
- (g) **The version**: 0.20.0, three minors, prepared and unpublished.

## Surprises & Discoveries

*(none yet)*

## Revision Notes

- 2026-09-20: v1 of this charter, drafted by the parent from a read-only grounding of the fingerprint
  mechanics, both operators as they stand in the shader and the CSS tier, the bed's set membership
  per pitch, the seven missed rows' causes, the cost of a read, and the W29 Deferred list and tracker.
  Not yet reviewed; no child dispatched.
