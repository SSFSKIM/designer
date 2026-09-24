# W35 — the body-boundary wave: Apple's inner edge line and ramp, fitted as excess over the body (2026-09-24)

**Status: CHARTERED 2026-09-24, v3 — two review rounds folded (two findings, then two on the folds); G0 is a two-phase gate (G0a the frozen declaration, G0b an authorised non-shipping runtime prototype at identity) and the fit-and-land contract (G1, G2, E1) is authorised only by Decision Log 1 on actual prototype renders. G0a open.** Chartered
by the parent on the user's "W35 body-boundary wave (Recommended)" after W34 closed at its finding
(main `d1162106`), under the standing "rest on your judgement" and the routing the user set on
2026-09-22 (X9, with the Codex-limit fallback recorded there). Grounded on a read-only memo taken off
W34's committed bed and archive and the runtime's sources
(`/Users/new/.claude/jobs/17c7ce02/tmp/w35-grounding.md`, a default-worker product; every number it
carries is reproduced by G0 into this wave's evidence before anything is fitted).

## Purpose

W34 (claims §5.174–§5.176) went looking for Apple's contour stroke and found that the **declared body
model fails first**: in the shell just inside the edge, [−2,−1) device px, Apple's active-pose body
misses a flat model by 2–27 codes on every endpoint, coefficient-independently, and no outside stroke
can reach that shell. The grounding memo read why, on W34's uniform greys, where the lens and the
scatter ramp are identities and the body's radial profile is bare:

1. **Apple's active body carries a narrow bright inner line about one CSS px wide** — two device px
   at 2x, one at 1x — sitting **18–53 codes above the deep body**: on 2x light grey-128 the top side
   reads 195 deep, **213** at shell −2, **226** at shell −1; on 2x dark grey-128, 134 → 156 → 173;
   on dark grey-0, 32 → 62 → 85. It is uniform along the side (226 / 226 / 226 across thirds) and
   top ≈ bottom within 2 codes. **Under it a shallow ramp** of +5 (light) to +8 (dark) codes rises over
   about −12…−3 device px, and deeper still the body is not flat: a trough of ~3 codes at 8–14 CSS px
   inside, 195 → 192 → 197 on 2x light grey-128.
2. **The inactive pose is flat to the edge** in both schemes (2x light grey-128: 188 at every inside
   shell; dark: 127) — its only boundary structure is the outside stroke W34 could not identify. The
   receded documents already draw rim 0 and inner shadow 0, which is why their floors were 2–3 codes.
3. **Vitrea draws something else.** On the light document a broad faint glow, 203 → 208 over eight
   device px, from `rimWidth` **6.5** / `rimWidth2x` **5.85** at `rimAlpha` 0.115 — W29 G3's refit,
   which set the width from "the reference's rim FWHM rose from about 1.3 to about 2.2 CSS px" on the
   canonical `rrect-md` cells (§5.153–§5.155 region; the 27 light document's `entries.rim`), a
   reading that most likely took the line and the ramp as one rim. On the dark document no ramp at
   all (flat 127 / 60) and a rim too dim at 2x (151 against Apple's 173). The frozen macOS 26.5
   documents keep W23's 1.5 / 1.35 widths at 0.844 / −0.628, fitted on the 26.5 solids (§5.100–§5.106).
4. **The line is on the canonical bed too**: `dark-solid__rrect-md__rest` at 2x light reads
   184 / 169 / 155 / 150 at shells −1 / −2 / −3 / −6 against the local web captures' 164 / 162 /
   160 / 154 (generation unverified in the memo; G0 verifies it with the checker), and on the
   continuous capsule and `rectangle-120` straights the profile is identical to the circular one.
5. **Most of W34's headline 91–165-code native–web gap is not the edge but the deep body's LEVEL**,
   worst on colour solids (2x dark red: native 239 / 51 / 51 against web 160 / 90 / 90) and up to
   +28 codes on dark grey-0. That is a different phenomenon — the body's tone and chroma over
   saturated and very dark backdrops — and this wave **does not fit it**: the edge law is expressed
   as excess over each image's own deep body so that it cannot absorb level, and the level miss is
   tabled for a wave of its own (Decision Log 2).

The purpose is Apple's inner edge — the line and the ramp, active pose, both schemes, both scales —
identified as a law of the body's own level on W34's bed, landed on the macOS 27 documents under every
stop the ledger carries, refereed on the canonical structured cells and read once on the canonical
holdout, with the CSS tier deriving what its one inset can carry, the frozen bed untouched, the deep
body's level recorded and not moved, and every gap written down.

## Parent-Level Acceptance

1. **The cut precedes the fit, on the full profile, with the bars derived.** G0 extends W34's reader
   (read-only, through `wave.py`'s roles) to shells [−H, 4) on the full-canvas archive with H at the
   capsule's centreline, derives the repeat bar for every new shell from `G1/repeat/` before any
   tolerance is declared, and tables — per pose, scheme, scale, level, part (arc / straight) — Apple's
   radial profile as **excess over the deep body** (the median over a declared interior domain whose
   inner edge is stated and whose trough is inside it), vitrea's WebGPU profile on the same masks, and
   the line / ramp decomposition (the line's width in device px per scale, its height per level; the
   ramp's reach and height). The memo's readings above are reproduced, not copied. **The diagnostic
   cut and the closure domain are distinct**: the cut covers every shell; the closure domain G0
   declares covers only the shells and pixels the model claims — the deep trough (~3 codes at
   8–14 CSS px inside), the coverage pixel and the arc pixels mixed with the outside stroke, and the
   stroke itself are given an explicit model or a justified DIAGNOSTIC-ONLY status before any fit,
   so that execution can neither fail on phenomena the model excludes nor narrow the domain after
   seeing residuals. Alignment and path uncertainty stay separate from the repeat tolerance and
   absolute values precede every averaging, as W34's `closure.json` holds.
2. **W29's width is reconciled before any width is fitted.** G0 re-reads the canonical solids
   (`light-solid`, `dark-solid`, `mid-dark-solid`, `mid-light-solid`, `mid-chroma-solid` over
   `rrect-md`, both schemes and scales, the committed fixtures) with the line + ramp decomposition
   beside W29 G3's FWHM reading, and says which of "2.2 CSS px" and "~1 CSS px" is Apple's line and
   what the other measured. The canonical web captures are verified by `check-capture-tree` for
   generation before they are read.
3. **The deep body's level is not this wave's, and subtracting it does not make absorption
   impossible.** The rim's amplitude law is conditioned on a level, and the runtime evaluates it on
   the LOCAL shadowed material luminance (`optics.ts` ~1554–1556), not on an encoded deep-body
   median; so comparing native excess at Apple's level with rendered excess at vitrea's level leaves
   `g · (L_web − L_native)`, which a fit on the native–web residual can absorb into the rim's
   coefficients without touching any tone leaf — and the +28-code dark-grey miss makes that real.
   And the runtime's conditioning input is an INTERMEDIATE the native pixels never show: the
   material composite after the inner shadow's occlusion and before the rim is added (`optics.ts`
   ~1504–1513, ~1554–1556), while the archive holds the final quantised RGB. Therefore: G0
   **declares the colour space and the conditioning variable** of the law and **declares and tests
   a forward model of the counterfactual pre-rim RGB/alpha field** from which native-side
   conditioning is computed — the runtime's own forward model supplied with native deep-body RGB,
   with the ownership and order of the ramp and the inner shadow stated, its uncertainty, its
   recoverability and its clipping and censoring treatment (saturated channels cannot uniquely
   recover added light) — never a claim to have observed Apple's internal state; the native excess
   law `E(L)` is **identified on native pixels alone** across the bed's levels on that declared
   conditioning, never on the native–web residual; the **transfer** at the runtime's actual
   conditioning level is reported separately with the tone error's contribution shown; **if only the
   excess against the deep-body level is identifiable, that is reported as an effective response and
   coefficient transfer is NOT authorised without a demonstrated mapping**; a **synthetic test on the
   same forward model** proves the instrument discriminates — a known nonzero level gain, a baseline
   change BEFORE shadow, rim and composition that preserves the coefficients but changes the
   predicted excess, a boundary-coefficient change at a fixed baseline, and recovery and
   discrimination within the declared numerical and quantisation error (adding a constant to the
   final encoded image and showing subtraction invariance is a control only, because it would pass
   the defective instrument); and if the transfer cannot close without compensating the tone error,
   the result is a qualified or stopped one, put to the user — never a fit that hides the level in
   the edge. G0 tables the level miss (greys and
   colour solids, both schemes) and puts it to the user as Decision Log 2, a wave of its own.
4. **Bounds before reads; a miss is recorded, not widened; holdout once by artifact.** G0 declares:
   the closure test on W34's validation greys and solids (absolute per-shell, per-channel residual
   within `max(1 code, bar)` over bins with the population floor, the derived deep-shell bars
   included); the canonical structured cells as the **referee, never the fit set** — the per-cell
   tables (edgeWeightedMean ≤ 0.11 and the rest), W20 conformance (contour ≤ 1 px, IoU ≥ 0.99), M1,
   M2 re-baselined per W32 Decision Log 4 with the eroded-mask attribution of the ring recorded, X1,
   C1, B1 — and the stops. Every stop carries its expected post-fit value. The canonical holdout is
   read once, at the sealed configuration, by `configuration.py record` (its fifth read); the W34
   bed's holdout is spent and its cells serve calibration and validation only; G0 delivers **one
   shared guarded reader for web pixels** beside W34's native reader, with negative tests that trip
   on a holdout id, because G2's web-capture directory holds 72 holdout cells among 408 and the
   native reader guards native pixels only — hand-written filters in each script are not the
   mechanism. The split is modest (one circular validation grey and one circular validation colour
   per endpoint, the other two validation circulars being gradients), which is why the canonical
   structured cells are the referee and the canonical holdout the blind read.
5. **The fit moves the rim's leaves and at most one appended leaf, on the macOS 27 ACTIVE documents.**
   `rimWidth`, `rimWidth2x`, `rimAlpha`, `rimLevelGain` (and `rimLitExponent` /
   `rimAlongSideSlope` only if G0's read of the along-side and lit fields demands it, with the read
   shown), plus **one** new leaf for the ramp added through the identity table at identity 0 — or the
   inner shadow re-signed and re-shaped if G0 shows that operator owns the ramp, with the read shown.
   Nothing else: not the lens, not the size law, not `bodyChromaRetention`, not the tone response, not
   the outer shadow, not the receded documents — which stay flat by a CHECKED composition: the
   receded patches compose OVER the active endpoint (`material-document.ts` ~82–85), so any new
   leaf needs an explicit zero override in both receded difference documents, or a proven existing
   zero gate, and G1 reads the receded pose to show it flat. The frozen 26.5 documents' rim leaves do not move and the
   new leaf sits at its identity there, so no 26.5 digest moves and no exemption is spent (X1, X13).
6. **The CSS tier derives or declines by measurement.** Its one inset (`optics.ts:133–180`, a single
   alpha with `rimAlpha` / `rimLevelGain` mirrored, no band, no `rimWidth2x`, no inner shadow) is
   re-derived from the same leaves — a one-CSS-px line is nearer to what it can draw than the 6.5
   band — rendered on the bed, read by G0's instrument, and carried or declined with the decline pinned
   against the shipped documents in `tier-coherence.test.ts`.
7. **The read follows the seal, once, and lands with its captures.** G1 seals the four macOS 27
   documents (rule 2, every digest site, `macos27-profile.ts` regenerated, the goldens attributed),
   runs the canonical read on the WebGPU tier, the ladder, the holdout once, the split
   (`--read-claims "c9a §5.178"`), pins `PREDICATE_EXCLUDES` as the machine says and the gated count,
   copies the read's capture tree to the canonical path with the replaced generation aside, and runs
   `check-capture-tree`; M2 is re-baselined at G1; the sheets and the eye with the LSB check beside
   every ×8 panel.
8. **Landing and every gap recorded — only if Decision Log 1 authorised the fit.** G0's feasibility
   verdict (a legitimate outcome is "cannot identify within this wave's operator budget") gates G1;
   G2 adopts, if the read supports it, one row — **E1, the inner edge's shape per pose** on the macOS 27 standard profiles, WebGPU tier, re-derived from the matrix
   and the captures at the adopting gate, with the amendment beside the header saying why it clears
   the MATERIAL-axis argument's grounds (as C1 and X1 do) — prepares 0.24.0, and writes Outcomes,
   Deferred-at-close and the Tracking Map. A CSS-only residual, an arc residual, the level miss and
   the inactive stroke are recorded, not chartered.

## Grounding Baseline (main at `d1162106`, W34 closed)

- **W34's bed and archive** (§5.175): 592 cells, every cell `probe`; the wave split
  `results/2026-09-23-w34-g0-contour-bed/split.json` 138 / 26 / 30 with the holdout SPENT (§5.176 §7);
  the repeat archive `results/2026-09-23-w34-g1-contour-sitting/repeat/` with full-canvas states, so
  the interior reaches the capsule centreline (22 CSS px for 120×44); bars exist for shells [−2, 4)
  only, at most 0.5 code; **no bar below shell −2 exists yet**. The reader and launcher are
  `results/2026-09-23-w34-g0-contour-bed/wave.py`, the shell reader `instrument.py` (exact stadium
  SDF with the archive's alignment; the cubic's 0.006·radius/22 CSS px qualification).
- **W34's split, as it bears on this fit** (`split.json`): calibration holds the greys 0, 32, 64,
  128, 160 and 255 and five chromatic solids; validation holds grey 96 and cyan (its other two
  circular cells are gradients); holdout holds grey 208 and is spent; every fixture role is `probe`,
  so `--set probe` alone selects nothing safely and the role-filtered `--scene` list is the entry.
- **W34's finding** (§5.176 §5): shell [−2,−1) floors, corrected: 1x dark active 10.00 / 10.00, 1x
  light active 10.25 / 10.00, 2x dark active 27.375 / 27.00, 2x light active 21.875 / 21.00; the
  inactive rows 2.0–3.0. The nominated body was flat to d = 0 with a bounded affine interior fit over
  d ≤ −6 (`closure.json`, `instrument.py`). The six-shell native–web gap 91–165 codes per stratum;
  the native-minus-no-glass response up to 222 codes.
- **The line's discriminants** (the review's read of the guarded archive): 2x light grey-128 reads
  213 / 226 on the two inner rows against a 195 deep median and a 128 background, and 219 at 1x;
  the black-on-white and white-on-black opaque controls show no intermediate straight-edge rows;
  an ordinary coverage mixture of body, darker outside stroke and background cannot produce 226;
  the surface sits inside the 320×200 canvas, not at the harness window's edge, the window is
  borderless and shadowless (`Capture.swift` ~120–127) and captured with explicit dimensions and
  `scalesToFit = false` (~393–402); W34's controls attest backing scales 1 and 2 and exact raster
  equality. These establish the line as material behaviour to investigate, not Apple's internal
  operator.
- **W29's width is a different estimand, not a contradiction**: `src/metrics/material.ts` ~658–673
  averages LINEAR-light luminance over integer distance-transform rings with the deepest ring as
  baseline, and ~704–708 doubles the inward half-width when the peak sits in the outermost ring;
  W29 G3's `baseline-matrix.json` records light `dark-solid__rrect-md__rest` at **2.4161 device px
  at 1x** (peak in ring 1) and **1.6628 device px = 0.8314 CSS px at 2x** (peak in ring 2). G0
  replays that estimator beside the new physical-distance profiles — units, mask, ring averaging,
  baseline and the doubling convention — and does not preselect "line plus ramp read as one rim".
- **The memo's first look** (§2 of the memo; reproduced by G0): the profile table above; arcs read
  on the circular SDF: 2x light grey-128 −8 / −3 / −2 / −1 / 0 / +1 = 193.5 / 194.6 / 200.0 / 186.6 /
  111.8 / 122.5 native against 203.4 / 205.6 / 206.3 / 196.7 / 136.1 / 127.2 web — arc pixels at −1
  mix the outside stroke subpixel-wise and need the exact-body integral, not centre classification;
  the deep-body level miss +8 / −5 / +28 / −7 / −4 (light 128 / light 255 / dark 0 / dark 128 / dark
  255) and ~80 codes on colour solids.
- **Vitrea's edge operators** (memo §3; `wgsl/optics.ts`): the rim
  `rw = (1 − |d| / rimWidth)²` × `lit = (√2 |n · rimLitAxis|)^rimLitExponent` ×
  `(1 + rimAlongSideSlope · sizeThick · field)` × `(rimAlpha + rimLevelGain · level)` (W23's
  amplitude law, W24/W25's lit and along-side factors); the inner shadow `(1 − t)²` darkening toward
  the edge at `shadowDepth` 0.35 / `shadowAlpha` 0.05 (W2; §5.49 already recorded "vitrea carries a
  1 % darkening from u ≈ 1.5 to 5.5 on solids that the reference does not have" and "the reference's
  line is 1.0 CSS px FWHM at 2x"); the lens (W12, from the 26.5 layer tree, never refit on 27) and the
  scatter ramp, identities on a uniform backdrop; the body mix `mix(backdrop, adapted, presentAlpha)`
  radially uniform; coverage `clamp(0.5 − d / ramp)` at one device px with the outer shadow composited
  into the same pixel; the highlight writes nothing at rest. Leaves on the four macOS 27 documents:
  light `rimAlpha` 0.115 / `rimLevelGain` −0.122 / `rimWidth` 6.5 / `rimWidth2x` 5.85, dark 0.055 /
  0.44 / 2.2 / 1.35, both receded 0 / 0 with the widths inherited; `rimLitExponent` 0.85,
  `rimAlongSideSlope` 0.1; `rimCollapsed` 0.038, `rimCollapsedTinted` 0.52, `rimTintChroma` 1;
  `strongBorderRim` {2, 0.95} on light, {1, −3.5} on light receded. The 26.5 pair: 0.844 / −0.628 and
  0.0265 / 2.334 at 1.5 / 1.35.
- **The CSS tier** (`platform-web/src/optics.ts:133–180`): one CSS px inset of one alpha with
  `rimAlpha` / `rimLevelGain` mirrored; no band, no `rimWidth2x`, no lit or along-side factor, no
  inner shadow, no lens; the band integral folded into `interiorBandLight`. `tier-coherence.test.ts`
  pins the rim per variant (:209–221), the collapsed rims (:227–245), the strong border (:604–627),
  the constants (:2243–2257) and the interior composite (X7, :2124+).
- **The gates** (memo §4; `adopted-thresholds.test.ts`): the per-cell tables (27 held at the 26.5
  twins, `:3048`; texture 1x light e.g. IoU ≥ 0.82, contour mean ≤ 2.5 / P95 ≤ 5.0, SSIM ≥ 0.88,
  ΔE ≤ 0.07 / P95 ≤ 0.17, **edgeWeightedMean ≤ 0.11**); `UNMET_ROWS` 11 (all 26.5), `MISSED_27_ROWS`
  8; the predicate at 0.95 with `PREDICATE_EXCLUDES` 67 (the silhouette extractor is a luminance
  delta — a brighter line can move it); W20 conformance contour ≤ 1 px, IoU ≥ 0.99 on the texture
  tier; M1 median R ∈ [0.80, 1.20], cell [0.60, 1.40] over the **un-eroded** native silhouette
  (`cli/measure.ts:482`); **M2** `interiorStdDevWeb` within 2 % of its reference generation, ring
  included — the likeliest stop, and the eroded-mask test the tracker names (:5340; W33 Deferred 10)
  has never run; B1 and C1 exterior (C1's `0-3` band excluded as the body's own edge, §5.62 §8); X1
  over black, at risk only if the line spills through the coverage pixel; the W14 X7 pair.
- **The identity table**: four entries (three W30, one W31), append-only, a new leaf at an inert
  identity so no shipped digest moves (W31 Decision Log 1 (a); `w31-identity-table.test.ts`,
  `w31-gate-groups.test.ts`). **The holdout**: four canonical reads on the configuration log
  (§5.164, §5.164 §13, §5.168, §5.172); one read per (document bytes, material sources); W34 did
  not touch it.
- **The canonical capture tree** on the machine at W33 G1b's generation (`check-capture-tree`
  1,893 match at the W33 G2 close); the sidecar `web-captures-superseded/`. The W34 web captures are
  under G2's evidence dir with 72 holdout cells among 408.
- **The machine**: the original harness bundle holds its Screen Recording grant again (W34 DL4
  executed); no native capture is planned here. The Codex accounts' usage limit refused the GPT
  rungs on 2026-09-24; X9 carries the fallback.

## Design (advisory unless marked)

**The model.** Per pose (active only — the inactive pose is a flat control that must stay flat),
per scheme and scale, the radial excess `E(d) = B_line(d) + B_ramp(d)` over the image's own deep body
`L` in the last N device px inside the edge, **in a declared colour space with a declared
conditioning variable** (the runtime's is the local shadowed material luminance; G0 says whether the
law is identified on that or on the deep-body level, and how the two relate on this bed): the line a narrow band of declared width `w_line` (about
one CSS px: G0 reads it per scale) whose height follows W23's amplitude form `a + g · L`; the ramp a
low band of reach `r_ramp` (about 12 device px) and height `h_ramp(L)`. Which operator owns the ramp
is G0's reading (Decision Log 1): the rim's `rw` band widened, a second rim component, or the inner
shadow re-signed — the memo notes Apple's ramp rises toward the edge where vitrea's inner shadow
darkens. The arcs are read on the exact-body integral, and the continuous-native / circular-web
mapping mismatch (§5.176 §4) is carried as a qualification on arc bins, not hidden.

**The fit set and the referee.** Fit on W34's non-holdout uniform greys and solids (calibration),
check on W34's validation cells, referee on the canonical bed's structured cells through the
existing gates and the per-cell tables — the canonical cells are never fitted on. The level miss is
a declared diagnostic in the fit (clause 3).

**Feasibility before leaves, in two phases.** A one-CSS-px observed line is not a one-CSS-px
`rimWidth`: the squared band weight, pixel-centre sampling, coverage, linear-light addition and the
encoding decide the output, and two bright 2x rows followed by an abrupt drop may not be drawable by
`rw` at all. A scratch material document can tune EXISTING operators only — `material-profile-file.ts`
~323–332 rejects unknown top-level keys, and no document creates a uniform or a shader term — so:
**G0a** (the frozen declaration) renders candidates built from the existing leaves through the tune
path — a calibration JSON document whose `profileKey` selects the shipped macOS 27 base and whose
`patch` is applied as tuning (`web/scene.ts` ~691–735), `--set probe` with the role-filtered
`--scene` list from `Wave.launch_scenes()`, the matching `--profile`, scratch `--material-profile`
(and `--receded-profile` when a receded override is tested), BOTH `--out-matrix` and
`VITREA_WEB_CAPTURES` at scratch, X6 checked and logged per launch through a W35 wrapper (W34 G2's
`browser.py` pattern; four launches per renderer per candidate, poses batched) — and reports what
the existing band can and cannot draw; then **G0b**, authorised by the parent after G0a's review, is
a **non-shipping runtime prototype**: the proposed identity-gated ramp operator and its plumbing
(one leaf, the uniform, the WGSL term, the identity-table entry and its tests) in G0's worktree,
every scratch capture recording the source hashes it was rendered from, shipped documents and
canonical evidence unchanged, the goldens byte-identical at identity — and Decision Log 1 rules on
ACTUAL prototype renders. G0's merge carries the prototype at identity only if Decision Log 1 adopts
the operator; otherwise its source is dropped from the branch and kept as a patch file in the
evidence. Nothing unimplemented is ever called runtime-tested.

**The leaves, if feasible.** Most likely: `rimWidth` / `rimWidth2x` narrowed to the line, `rimAlpha`
/ `rimLevelGain` refit at that width (W23's peak/0.336 calibration is width-dependent, so narrowing
re-opens the amplitude), and one appended identity-0 leaf for the ramp (gate-group if it gates
others). The two receded difference documents already zero `rimAlpha`, `rimLevelGain` and
`shadowAlpha` in `regular` and `clear` and the root `rimCollapsed` / `rimCollapsedTinted`; the new
ramp's amplitude or gate path is zeroed in both unless an existing zero gate is proved to disable
it, width and shape leaves need not be zero while the amplitude gate holds, and flatness is proved
by the operator tests plus a receded render and read with a NONZERO active candidate composed under
the receded patch (`macos27-profile-export.test.ts` pins the patches; it does not prove flatness). The dark document's rim (2.2 / 1.35 at 0.055 / 0.44) is refit on the same read. The
receded documents keep 0.

**The CSS tier.** Re-derive the one inset from the new leaves; render; read; carry or decline.

**The stops** (declared in G0 with expected values): the closure test on W34 validation; the
canonical per-cell tables and W20 conformance; M1; M2 with the eroded-mask attribution; X1; C1; B1;
the level-absorption diagnostic; the inactive pose flat.

## Children

### G0: The cut, the declarations and the feasibility — two phases, nothing shipped, no capture

Ledger **§5.177**; evidence `packages/calibration/results/2026-09-24-w35-g0-edge-cut/`. Owns its dir,
`test/w35-*.test.ts`, a read-only extension of W34's reader (a new module beside `wave.py`, not an
edit of the spent receipt's code path), the shared guarded web reader, the W35 render wrapper, and —
in G0b only, under the parent's authorisation — the prototype operator's source at identity.
**G0a** is the frozen declaration: everything below except the prototype, committed and independently
reviewed as a checkpoint. **G0b** is the prototype phase the parent authorises on G0a's review:
the proposed ramp operator behind an identity-0 leaf, its uniform, its WGSL term, its identity-table
entry and gate-group tests, the goldens byte-identical at identity (the isolation proof re-run),
scratch renders of the prototype on the bed with the source hashes recorded beside each capture,
read by the instrument against the frozen closure domain; the Decision Log 1 draft on those renders. Does: the deep-shell bars derived from the archive; the full
radial profile tables (native excess over the deep body, web, difference; per stratum, level, part)
reproducing the memo; the line / ramp decomposition per scale and level; W29 G3's FWHM reconciled on
the canonical solids with the capture tree's generation verified; the eroded-mask M2 test and the ring
attribution; the level-miss table (greys, colour solids) and a Decision Log 2 draft for the user; which
operator owns the ramp (a Decision Log 1 draft for the parent, with the inner-shadow reading beside);
the model's declared form, colour space and conditioning variable; the native-only identification
of `E(L)` across levels with the transfer at the runtime's conditioning level reported separately;
the synthetic level-offset test; the diagnostic cut partitioned from the closure domain with the
trough, the coverage pixel, the mixed arc pixels and the stroke each given a model or a
diagnostic-only status; W29's estimator replayed beside the new profiles; the **feasibility
verdict** — from tune-path renders of the existing leaves in G0a and from the prototype's renders in
G0b — with the domain frozen before either; the shared
guarded web reader with its negative tests; the CSS tier's derivation plan; the bounds and stops
with expected post-fit values (`bounds-declaration.md`); the E1 row's proposed form and precisely
what its evidence can establish; the identity route proven for the new
leaf (flat leaf, gate-group if needed; both 26.5 digests and the four 27 digests unmoved — the script
of W33 G0's `identity-proof.ts` shape). Acceptance: every number of the memo reproduced or corrected
beside; the bars for every shell the model reads; the declaration reviewed; nothing under `src/`,
`profiles/`, `fixtures/`, `results/matrix.json` or the canonical `scenes.json` touched; freeze 1,818.
Stop conditions: the level miss dominates the excess so the edge cannot be separated (re-scope as a
level wave, the user's); no deep-shell bar derivable from the archive; the canonical capture tree
at a generation the checker refuses; only the excess against the deep-body level identifiable with
no demonstrated mapping to the runtime's conditioning (an effective response, reported; coefficient
transfer not authorised). **A feasibility verdict of "cannot identify within this wave's operator
budget" is not a stop but a legitimate G0 outcome**, put to the parent in Decision Log 1 with what a
larger budget would need.

### G1: The fit, the seal, the read — one merge; opens only on Decision Log 1's feasibility verdict

Ledger **§5.178**; evidence `packages/calibration/results/2026-09-24-w35-g1-edge-fit/`. Owns
`material.ts`'s rim leaves' values on the four documents and the new leaf with its identity-table
entry and tests, the WGSL ramp term if one is added, `optics.ts` / `css-tier.ts`'s mirror or decline,
the four macOS 27 documents, the generated profile, `adopted-thresholds.test.ts`'s
`PREDICATE_EXCLUDES` and `MISSED_27_ROWS`, `window-activation.spec.ts`'s hashes if they move. Does:
the native-identified law transferred at the runtime's conditioning level with the tone error's
contribution shown (a transfer that closes only by compensating the tone error is a stop), the check
on W34 validation through the guarded readers, the canonical solids read before the seal, the
receded pose read flat; the leaves added
through the identity table; the CSS experiment; the seal (rule 2, every digest site, the goldens
attributed and the isolation proof re-recorded with reason); `configuration.py record` before the
passes; the canonical read on the WebGPU tier, the ladder, the holdout once; the split
(`--read-claims "c9a §5.178"`); `PREDICATE_EXCLUDES` as the machine says; the gated count; M2
re-baselined; the sheets and the eye with the LSB check; every stop read with its expected value
beside. Acceptance: clauses 3–7; a miss recorded and put to the user, never widened. Stop conditions:
a stop breaks (recorded with its decomposition, W32's `b3-window.py` precedent); the level-absorption
diagnostic fires; the inactive pose gains structure.

### G2: The landing — E1 adopted if the read supports it, 0.24.0 prepared

Ledger **§5.179**; evidence `packages/calibration/results/2026-09-24-w35-g2-landing/`. The E1 row
adopted as declared and re-derived at the gate; M2 per W32 Decision Log 4; `CLAUDE.md`, both READMEs,
CHANGELOG, the coverage matrix; the `/laws/` stage's readout re-checked (digest-keyed); the chain
(`chain.sh`, `dry-run.sh`, X6's four facts before every browser run); `pnpm changeset version` to
0.24.0; Outcomes & Retrospective; Deferred-at-close; the Tracking Map row.

## Cross-Child Contracts

- **X1 — the freeze, intact.** No macOS 26.5-keyed path, row, bound, floor or document changes;
  `freeze.py verify` 1,818 at every merge; the goldens byte-identical until G1's attributed change;
  the 26.5 digests stay the live pin with no exemption spent (the new leaf through the identity
  table, X13); `digest-supersessions.json` gains no record.
- **X2 — the cut precedes the fit.** G0's tables, bars, decomposition, reconciliation, bounds and
  stops are committed and reviewed before G1 opens; G1 fits against them and no other.
- **X3 — the fit's reach.** The rim leaves on the four macOS 27 documents, one appended leaf (or the
  inner shadow's sign and shape, on G0's reading and Decision Log 1), the receded documents flat by
  explicit zero overrides for any new leaf and a read of the receded pose.
  Not the lens, the size law, the tone response, the chroma retention, the outer shadow, the body's
  level, the scatter, or any 26.5 value. A fit that moves a row outside the edge axis is a warning,
  not a result.
- **X4 — bounds before reads; a miss is recorded, not widened; holdout once by artifact.** The
  canonical holdout at the sealed configuration only, `configuration.py record` first; the W34
  bed's holdout is spent and is never read; W35 reads web pixels only through G0's shared guarded
  web reader (negative tests), never a hand-written filter.
- **X5 — no native capture; the canvas does not change; no bundle is rebuilt or granted.** W34's bed
  and archive are read through W34's reader roles, read-only.
- **X6 — RT and IC 0, the slider 0.5, Show Borders 0, one capture process, ≥ 60 s idle and the
  foreign-process count** before every browser run, every run in `browser-runs.txt`.
- **X7 — the evidence layout by the one rule**: the split after the read that supersedes, no schema
  bump; the read's capture tree to the canonical path at G1's merge, the replaced generation to
  `web-captures-superseded/<active-document-sha>/`, `check-capture-tree` run.
- **X8 — padding untouched**; the reach's numbers recorded if the ramp widens the drawn extent.
- **X9 — routing.** Children, reviews and fix waves on `astra-medium` / `astra-high` or `sol-xhigh`
  (the user's ruling, 2026-09-22); **when the Codex accounts' usage limit refuses those rungs, the
  default Claude worker runs the bounded work and the charter's Revision Notes record each such
  dispatch** (W34's precedent); the charter's own review on `doperpowers:adversarial-reviewer` or,
  refused, a Claude reviewer with the same brief; reviews read-only; ledger sections as assigned;
  merges `--no-ff -F <file>` with the freeze verified; no attribution trailers; committed evidence
  never rewritten, corrections beside.
- **X10 — the 27 bed never empties between merges.** The four documents' bytes change only in G1's
  merge, which carries rows read at the new bytes; `MATRIX_CELLS` / `PREDICATE_EXCLUDES` move only in
  the commit that carries the read; the gated count pinned at every merge.
- **X11 — file ownership** as the children state; G0b's prototype source lives on G0's branch at
  identity 0 and merges only on Decision Log 1's adoption, else it is dropped from the branch and
  kept as a patch file in the evidence; nobody touches `receded-profile.ts`'s 26.5 block,
  `DEFAULT_MATERIAL_PROFILE`'s existing values, or W34's spent receipt and its code path.
- **X12 — arcs and straights read separately**, the arcs on the exact-body integral, the
  continuous-native / circular-web mapping mismatch carried as a qualification on arc bins.
- **X13 — the new leaf through the identity table**, flat, at identity 0, gate-group if it gates
  others, its rule-2 version recorded in every sealed document.
- **X14 — M2 re-baselined per W32 Decision Log 4 at G1**, its reference the superseded pre-W35
  generation and never the new result, with the eroded-mask attribution of the ring recorded beside
  the re-baseline so the cumulative drift the tracker tables stays visible; attribution does not
  waive the 2 % stop.

## Ordering & Dependency Map

G0a → independent review of the frozen declaration → the parent authorises G0b → G0b (the
prototype, scratch renders) → Decision Log 1 → merge (the prototype at identity only if adopted) →
G1 (fit, seal, read; the browser runs need the
machine quiet for X6 but not untouched) → review → merge with the capture tree → G2 → review → merge →
`pnpm release` (the user's hand) → tag.

## Risks & Mitigations

- **The line is an artefact, not Apple's material.** The discriminants in Grounding (opaque controls
  without intermediate rows, the surface inside the canvas, `scalesToFit = false`, attested backing
  scales, 219 at 1x and 213 / 226 at 2x against 195 / 128) argue it is material behaviour; G0's
  reconciliation on the canonical solids with the no-glass references and W29's estimator replayed
  settles what W29 measured. Neither identifies Apple's internal operator.
- **The band cannot draw the profile** (two bright rows and an abrupt drop are not a squared band):
  the feasibility verdict is G0's, with "cannot identify within this wave's operator budget" a
  legitimate outcome.
- **The fit absorbs the tone error through the level conditioning**: native-only identification,
  the transfer reported separately, the synthetic level-offset test, a stop if the transfer needs
  the compensation.
- **The ramp is the lens or the scatter, not light**: on uniform backdrops both are identities, so a
  ramp seen on greys is not them; G0 reads the gradient cells beside to say whether the ramp changes
  with backdrop structure.
- **M2 stops a correct change** because the ring is inside its mask. The eroded-mask test runs in
  G0; if the ring accounts for the move, Decision Log 3 puts M2's mask to the user before G1.
- **The level miss dominates**: the declared diagnostic; a stop and a re-scope, not a silent level
  fit.
- **The predicate moves** (a brighter line moves the luminance-delta silhouette): `PREDICATE_EXCLUDES`
  as the machine says, the count pinned, the cells named.
- **X1 trips** if the line spills through the coverage pixel onto black: read in G0's expected values.
- **The Codex limit** refuses the GPT rungs mid-wave: X9's fallback, recorded per dispatch.

## Deferred / Out of Scope

- The deep body's LEVEL over saturated and very dark backdrops (Decision Log 2): a wave of its own.
- The inactive pose's outside stroke (W34's negative): unchanged.
- The lens on macOS 27 (never refit since W12): unchanged here; noted if the gradient cells show it.
- The accessibility documents' edge: unmeasured here.
- W34's Deferred-at-close 2–7 carry.

## Tracking Map

| child | status |
| --- | --- |
| G0 | G0a DELIVERED FOR REVIEW as a qualified negative (§5.177); no transferable law or G0b operator identified |
| G1 | CHARTERED, opens after G0's merge and Decision Log 1 |
| G2 | CHARTERED, opens after G1's merge |

## Decision Log

### Decision Log 1 — the model's form and the ramp's owner (after G0; the parent's, under the standing "rest on your judgement")

Open. G0 drafts: the line's width per scale and its amplitude form in the declared colour space and
conditioning variable; which operator owns the ramp (rim band, second component, inner shadow
re-signed); the reconciliation of W29's estimator; the closure domain; **the feasibility verdict**
from G0a's tune-path renders of the existing leaves and G0b's renders of the actual prototype — the
existing band closes the declared domain, or the band plus the prototype ramp does, or "cannot
identify within this wave's operator budget" with what a larger budget would need; whether the
native law's conditioning has a demonstrated mapping to the runtime's (else an effective response
and no coefficient transfer); the leaves G1 would move. The parent rules whether G1 opens, and on
what.

**G0a draft, 2026-09-24 (§5.177; not ruled).** Do not open G1 or nominate a radial
ramp prototype on this evidence alone. The frozen-domain existing-leaf candidates fail
at25.50/33.75/36.00/46.57 codes (1x light/dark,2x light/dark), straight-only minima5–9.85;
normal tolerance1. Native-only scalar affine white-light fits fail chromatic solids,
while whole nominal-body arc bins show a markedly different angular response from the
shipped diagonal law. The counterfactual forward model checks the web branch to<.88
code but does not identify the native pre-rim field. A positive second ramp alone does
not explain all three misses. Recommend a bounded re-declaration addressing angular and
chromatic boundary structure, with the level wave kept separate, rather than spending
G0b on an unselected one-leaf ramp. No claim that every possible existing-leaf setting or
one-leaf function has been mathematically excluded. The parent decides the budget and
whether a useful G0b prototype can be stated; this worker starts none.

### Decision Log 2 — the deep body's level (after G0; the user's)

Open. G0 tables the level miss on greys and colour solids, both schemes; the user rules whether a
level wave follows W35 and whether anything about it constrains this wave's fit.

**G0a draft, 2026-09-24 (§5.177 §3; not ruled).** A separate level/chroma wave is
warranted: light black +49 codes and dark black +28 at both scales; active solid channel
misses reach111 and inactive144. These do not authorise compensating edge coefficients.
The user decides whether that wave precedes any renewed boundary transfer; G0a recommends
keeping native-only edge identification independent and forbidding tone compensation.

### Decision Log 3 — M2's mask if the ring is what it reads (after G0's eroded-mask test; the user's)

Open. If the eroded-mask attribution shows M2 would stop a correct edge change, the re-pin or the
mask change is put here with numbers before G1 opens.

**G0a draft, 2026-09-24 (§5.177 §7; not ruled).** The26-cell current-generation
1/2/3-device-pixel erosion reading is complete. One pixel changes dark photo/capsule
std-dev by−60.03% at1x and−48.43% at2x. This is ring sensitivity, not a prediction of the
change from a correct edge or proof about the W32 before/after pair. Retain the2% stop
and pre-W35 reference; defer mask/re-pin choice until a viable candidate supplies its
actual delta. The eroded statistic does not itself authorise a new bound or mask.

### Decision Log 4 — the E1 row's adopted form (after G1's read; the parent's)

Open.

## Surprises & Discoveries

(none yet)

## Revision Notes

- 2026-09-24 (G0a worker): the frozen pre-candidate domain committed in ae7492a8;
  §5.177 delivers336-cell deep profiles/bars, actual W29 replay, native-only forward
  diagnostics,26-cell M2 erosion attribution and eight candidate launches/64 deterministic
  captures. No tested candidate closes; native transfer and a particular G0b operator are
  not identified. Three Decision Log drafts are findings, not rulings. The parent directed
  a separate canonical reader allowing calibration/validation/probe and refusing holdout/
  recorded, and coexistence with the unrelated foreign Playwright session: the opening
  proof passes17/17 with nine foreign processes recorded; all feasibility preflights later
  read zero. No foreign session was closed. Missing canonical cells/captures and undefined
  post-fit canonical expectations remain explicit. Bounds declaration is plain text under
  the worker's no-Markdown-report constraint; its machine counterpart is domain.json.

- 2026-09-24 (the parent, v3): the second round found the v2 folds sound in direction and two of them
  not yet executable: (1) native-only identification against the deep-body level still had no
  demonstrated mapping to the runtime's conditioning input, which is the composite after the inner
  shadow and before the rim — clause 3 now requires a declared and tested forward model of that
  pre-rim field, an effective-response outcome with no coefficient transfer when only the deep-body
  excess is identifiable, and a synthetic test that exercises the same forward model (level gain,
  a pre-composition baseline change, a coefficient change at fixed baseline, recovery within the
  declared error) rather than an encoded-constant control; (2) a scratch document cannot render an
  operator that does not exist, so G0 is split into G0a (the frozen declaration, reviewed) and G0b
  (an authorised non-shipping runtime prototype at identity, source hashes beside every scratch
  capture, merged only on adoption), and Decision Log 1 rules on actual renders. The sound notes are
  folded: the render mechanism and its cost (four launches per renderer per candidate, X6 per
  launch), the split's actual composition, the receded documents' existing zeros and how flatness
  is proved. No third round: G0a's declaration is itself reviewed before G0b.
- 2026-09-24 (the parent, v2): the adversarial review of v1 returned two blocking findings, both
  folded, and five sound notes, all folded. (1) Subtracting the body's level does not isolate a
  level-conditioned law — the runtime conditions the rim on the local shadowed luminance and a fit
  on the native–web residual can absorb the tone error: clause 3 rewritten (declared colour space
  and conditioning variable, native-only identification of `E(L)`, the transfer reported separately,
  a synthetic level-offset test, a stop if the transfer needs compensation); the correlation
  diagnostic withdrawn. (2) The full-profile closure included phenomena the model excludes: clause 1
  partitions the diagnostic cut from the closure domain, gives the trough, the coverage pixel, the
  mixed arc pixels and the stroke a model or a diagnostic-only status, and G0 delivers a feasibility
  verdict — with "cannot identify within this wave's operator budget" a legitimate outcome — before
  G1 or E1 is authorised (clause 8, G0, G1, Decision Log 1). The notes: the line's discriminants
  replace "seen at both scales" in Grounding and Risks; W29's width is a different estimand (linear-
  light ring averages, deepest-ring baseline, the doubling convention; 2.4161 dp at 1x, 0.8314 CSS
  px at 2x) and G0 replays the estimator rather than presuming the explanation; a one-CSS-px line is
  not `rimWidth` 1 and G0 renders candidates through the tune path for feasibility; the receded
  documents compose over the active endpoint so a new leaf needs explicit zero overrides (clause 5,
  X3); one shared guarded web reader with negative tests replaces per-script filters (clause 4, X4);
  M2's reference is the superseded generation (X14). The wave stays one staged wave: G0 is a
  declaration-and-feasibility gate; G1 and G2 open only on Decision Log 1.
- 2026-09-24 (the parent): v1 chartered from the grounding memo; sent to adversarial review before
  G0 opens. The memo was written by the default Claude worker because the Codex accounts' usage limit
  refused the GPT rungs (X9).
