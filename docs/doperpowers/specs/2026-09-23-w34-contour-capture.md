# W34 — the contour wave: the capture that identifies Apple's macOS 27 contour stroke (2026-09-23)

**Status: CHARTERED 2026-09-23, v1 — sent to adversarial review before any child opens.** Chartered
by the parent on the user's "W34 contour capture wave (Recommended)" after the 0.23.0 publish
(main `011de142`), under the standing "rest on your judgement" and the routing the user set on
2026-09-22 (X9). This is the wave W33 Decision Log 3 named when it ruled "stop": the identifying
capture, with X5 lifted by the user for this wave's probe bed and nothing else.

## Purpose

Apple's macOS 27 material draws **one device pixel of signed stroke at the contour, on both poses**,
and vitrea draws none. W33 G0 (claims §5.170) measured it model-free on an exact rounded-rect SDF:
the notch `native[d=0] − min(native[d=±1])` reads a median of **−19.78 bytes** on 1x light active
with 46 of 51 cells below −5, **−21.30** inactive, **−13.74** on 1x dark, against **+2.68** on the
frozen macOS 26.5 bed with 1 of 68; it is darker than both backdrop and body over a light square and
**lighter than the backdrop over a dark one, which a transmission cannot be** (§5.166 §7). W33 G1a
(§5.171) then found the law **unidentifiable on the bed as it stands**: of 152 angular strata none
closes at one byte and 8 at three; straight-only fits cannot identify an exponent because `|nx|` is
0 or 1 there; the arcs carry the term (dark active capsule straight −0.27 versus arcs −19.75) and
the harness's capsules are `.continuous` by default, so corner geometry, coverage and colour are
confounded in the only arcs the bed has; and one byte is an encoding comparator, not a noise bar,
because **no repeat native capture exists for this instrument**. The user ruled stop, no contour
leaf shipped, and the capture that would identify the term went to Deferred-at-close FIRST with
§5.171's amended plan as the shape of the work.

This wave is that capture, and what follows from it. Its purpose, in order:

1. **A native bed designed to identify the stroke's law**, where the confounds W33 could not
   separate are separated by construction: circular capsules, path-attested, beside the default
   continuous ones; matched continuous rectangles; an opaque no-glass control of the same path so
   the rasteriser's own edge coverage is read apart from the material; uniform grey and chromatic
   levels; gradient backdrops of declared direction and magnitude and a spatial-frequency ladder;
   independent x and y subpixel-phase sweeps at 1x and 2x; both schemes and both poses; no-glass
   references captured through the same path with the same colour management; and **enough repeats
   to publish a per-bin, per-channel run-to-run bar before any closure threshold is chosen**.
2. **Identification on that bed**, with the split declared before fitting: a law that closes
   against the measured bar on the validation subset and once on the holdout — or a second, sharper
   negative that says what the bed now excludes and at what resolution.
3. **Only if a law closes, the leaf**: added through the identity table as W33 G0/G1a proved a flat
   leaf can be, drawn on the WebGPU tier, carried or declined on the CSS tier by measurement, sealed
   and read once, with every W32/W33 stop re-read and the contour/IoU bound conflict W33 G0 tabled
   put to the user before any re-pin. Otherwise the wave closes at the finding.

The purpose is the term identified or its unidentifiability sharpened to a stated resolution, the
frozen bed and the shipped macOS 27 bed untouched until a law closes, and every gap written down.

## Parent-Level Acceptance

1. **The bed is declared before it is captured.** The wave-local scenes file, the split, the repeat
   count, the statistics, the closure rule and the stop conditions are committed and independently
   reviewed in G0 before any pixel is captured. The split is declared in the scenes file and never
   re-cut; the wave's holdout is read once, by artifact.
2. **The side bundle carries its own identity and the granted bundle is untouched.** The harness
   change is built by `build.sh` under `VITREA_BUILD_OUT` outside the repository, with the same
   toolchain, SDK and flags as the granted bundle, so the sources' additions and the bundle
   identifier are the only differences; the identifier is **not** `dev.vitrea.reference-apple`,
   because TCC keeps one Screen Recording row per identifier and the last code hash added owns it
   (W29 Surprises, measured 2026-09-18). `apps/reference-apple/build/` is never rebuilt and
   `build-probe/` — a 2026-09-13 side bundle that carries the granted bundle's identifier — is never
   added to Screen Recording. The granted bundle's own grant is **positively re-checked** after the
   side bundle is granted, by a scratch capture with `materialRendered: true`; a loss is a Surprise
   and the README's remove-and-re-add recipe is the recovery.
3. **Every run is attested as W29's were, and a run that fails to attest is quarantined.** macOS
   27.0 build 26A428; `NSGlassTintAmount` 0.5; Reduce Transparency and Increase Contrast 0; Show
   Borders (`ButtonShapesEnabled`) 0; the display mode read before the pass and the manifest's
   `actualBackingScale` checked after; the capturing bundle's cdhash and `LC_BUILD_VERSION`; an
   opening and a closing read that must agree; per cell `presentedActive` true and `deterministic`
   recorded. The sitting script is derived from `run-sitting-27.sh` with its `VITREA_APP` /
   `VITREA_HARNESS` seams pointed at the side bundle and its version gate kept.
4. **Repeats before thresholds.** Seven runs per pass, W29's bar. The per-bin, per-channel
   run-to-run spread of every statistic the identification reads is published in G1, before G2
   opens, and **no closure threshold is chosen before it exists**. "One byte" appears in this wave
   only as the encoding's resolution, never as a bar.
5. **The instrument separates what W33 could not.** Circular capsules whose rendered path is
   attested by the harness itself (the elements of `shape.path(in:)` written beside the capture,
   the construction of G1a's `capsule-geometry.swift` applied in-process) beside default continuous
   ones of the same rect; continuous rounded rectangles of the same rect at a smaller radius; an
   opaque control of each path with no glass; uniform levels and chromatic solids; gradient
   backdrops with declared direction and magnitude; a frequency ladder; x and y subpixel phases
   swept independently at 1x and 2x; both schemes; both poses; and no-glass references of every
   backdrop captured through ScreenCaptureKit like the glass cells. Arcs and straights are separate
   strata everywhere (W33 X12 carried). The existing `capsule-button` over the existing backdrops
   is in the bed as a **bridge**, so the new bar can be laid beside W33's readings.
6. **Identification precedes fitting and the split precedes identification.** G2 fits on the
   calibration subset, checks on validation, reads holdout once; least-squares and minimax are both
   reported; a family "closes" only when every populated bin's signed channel residual lies within
   the declared multiple of that bin's measured bar. The candidate families G1a tested are re-run
   on the new bed first, so the finding is comparable, before any new family is tried.
7. **Nothing shipped moves until a law closes.** In G0–G2 no byte changes under `scenes.json`,
   `fixtures/`, `results/matrix.json`, the six material documents, the goldens or any adopted
   threshold; the wave's bed is a probe bed under its own scenes file and fixture root (claims
   §5.30's pattern; W9, W12, W20, W21 and W27e's precedent), committed under the capturing gate's
   evidence directory and read with `fixtureSet: "probe"` into the wave's own matrix.
   `freeze.py verify` **1,818** at every merge.
8. **A law lands as W33 planned it, or the negative is recorded with its resolution.** If Decision
   Log 2 finds a law: G3 adds the leaf through the identity table (flat leaves; the frozen 26.5
   documents at its identity), the WGSL term, the CSS carry-or-decline, the seal, the canonical read,
   the holdout by artifact, the W32/W33 stops (C1, B1, B3, X1, the thin stop, M2 re-baselined per
   W32 Decision Log 4) re-read, and the contour/IoU conflict (W33 G0's forms table: no compositing
   form both reproduces Apple's bytes and keeps `declaredContourMaxWeb ≤ 1`) put to the user as
   Decision Log 3 before any bound is re-pinned. If it does not: the wave closes at G2 with the
   negative, the families excluded, the resolution the bed reached, and what a third bed would need.

## Grounding Baseline (main at `011de142`, 0.23.0 published)

Read by the parent on 2026-09-23 before this charter; G0 re-verifies every machine fact into its own
record before anything is built.

- **The machine.** macOS 27.0 build 26A428; Reduce Transparency 0, Increase Contrast 0,
  `NSGlassTintAmount` 0.5, `ButtonShapesEnabled` 0 (the four facts plus Show Borders, read
  2026-09-23). The BetterDisplay virtual screen `가상 16:9` (persistent id `7709FD0F-…`) is present
  with **mode 68 (2x) current and mode 69 (1x)** beside it, the same two modes W29's sitting ran at;
  `displayplacer` at `/opt/homebrew/bin`. `python3.12` has PIL and numpy. Toolchains: Xcode 26.6's
  `swiftc` 6.3.3 with `MacOSX.sdk` at 26.5 (what `build.sh` uses), and the Command Line Tools'
  `swiftc` 6.4 with SDKs 26.5, 27.0 (what W29's SDK-gating side build used).
- **The granted bundle.** `apps/reference-apple/build/VitreaReference.app`, identifier
  `dev.vitrea.reference-apple`, binary dated 2026-09-12, `LC_BUILD_VERSION` minos 26.0 sdk 26.0
  (`sdk == minos` whatever SDK compiled it — a measured linker quirk, W29 G0). Whether its Screen
  Recording grant is intact today is **not verified here**; G0 proves it before touching TCC.
  `build-probe/VitreaReference.app` (2026-09-13) carries the **same identifier**, and is the hazard
  clause 2 names. W29 settled SDK gating on the declared material: bundles recording sdk 26.5 and
  27.0 declared a byte-identical filter tree on 9 of 9 cells, so a 26.5-SDK side bundle draws the
  27 material the granted one draws.
- **The grant.** W29 Surprises: TCC keeps one row per bundle identifier and the last code hash added
  owns it; adding the 27-SDK side bundle by path evicted the granted bundle's grant, which the user
  restored by re-adding its path. The README's recipe: remove the row and re-add, because a recorded
  denial suppresses the prompt. The user's standing instruction for GUI toggles is the codex
  companion's `amigo` first and their own hand if it fails; `amigo` needs `--write`, a per-turn
  bootstrap, and can hang on a first approval (its reference), which is why the fallback is named.
- **The harness.** `capture.sh` execs `build/harness` and nothing else; the W29 sitting script's
  `VITREA_APP` / `VITREA_HARNESS` seams are how another bundle runs a pass. `VITREA_SCENES` and
  `VITREA_FIXTURES` are honoured by both the harness and `cli/compare.ts`, which is what makes a
  probe bed measurable end to end without touching the canonical layout. Shape kinds are `capsule`
  (→ `Capsule()`, `.continuous` by default — G1a's witness: default equals explicit continuous and
  differs from explicit circular, the straight-segment starts −0.30…+0.04 CSS px from the circle)
  and `rrect` (`RoundedRectangle(…, style: .continuous)`); a shape spec's `offset: [x, y]` goes to
  `.offset(x:y:)` as `Double`, so a fractional phase is expressible in JSON today — **whether the
  composited glass shape honours a fractional offset or snaps to the device grid is unmeasured**
  and is G0's first scratch measurement. Backgrounds: `solid`, `checkerboard`, `impulse`,
  `synthetic-photo`, `text-rows`; **no gradient kind, no no-glass reference, no opaque control, no
  path attestation** — each is a Swift change, which is why a side bundle is unavoidable. Canvas
  320×200. The manifest records per fixture `deterministic`, `repeatNoise`, `presentedActive`,
  `materialRendered`, `chromaShift`, and per profile the display; `cli/materialize.ts` publishes a
  bed from several runs by plurality with a seven-run bar and refuses a cell that will not settle.
- **The cost.** W29's sitting: 162 cells × 7 runs in 3 h 01 m per standard active pass, about
  9.5 s per cell-capture; 12 h 49 m for eight passes. A W34 pass of N cells at seven runs costs about
  N × 66 s.
- **The probe-bed precedent.** W9, W12 (2x), W20, W21 and W27e each ran a wave-local
  `scenes-w*-probe.json` through `VITREA_SCENES` into fixture directories committed under the
  gate's evidence dir (`results/2026-09-06-w21-dark-scheme/probe/<profile-key>/`), read by fits and
  claims and never gated; W25 Decision Log 3 (e) made `probe` a declared role beside `recorded`.
- **W33's instrument and findings**, to be re-derived rather than copied: `referee.py` (the SDF
  shells, corners projected radially, arcs and straights as separate strata), `coverage.py` (an
  ideal annulus over 64 subpixel samples), the 456 angular strata at 22.5° bins, the 5,472 radial
  rows, the 400 colour strata, and the families tested (constants, `|nx|^k` at k = ½…8,
  `a + b|nx|^k`, a one-sided diagonal vector, the shipped-diagonal factor, an affine signed-normal
  field, the two-term even law, rotated axis, isotropic plus even-axis terms, gradient, colour plus
  gradient; least squares and minimax).

## Design (advisory unless marked)

**The bed** — G0 designs it to clause 5 and prices it; the parent rules its final shape in
Decision Log 1 from G0's draft. The shape the parent expects:

- *Shapes.* `capsule-circular` (new kind → `Capsule(style: .circular)`) and `capsule` (continuous,
  existing) at the bed's 120×44; the same pair at a second rect (160×96) so the arcs come at two
  radii; `rrect` continuous at 120×44 with radius 12 as the matched rectangle (straight sides of
  known length beside arcs of known continuous geometry); and an **opaque control** of each — the
  same path filled with an opaque colour and no `glassEffect` — which reads the rasteriser's own edge
  coverage and antialiasing so the material's stroke is a difference from geometry, not from an
  assumed ideal circle.
- *Backdrops.* Uniform greys at eight levels (0 … 255) and six chromatic solids; gradients as a new
  `linear-gradient` kind with `from`, `to` and `angle` at 0°, 45°, 90°, 135° and two magnitudes;
  the existing checkerboard pitches 4, 8, 16, 32, 64 as the frequency ladder; a no-glass reference of
  every backdrop as a scene with an empty component (new kind `none`), captured through
  ScreenCaptureKit exactly as the glass cells are, which is what makes the reference's colour
  management identical.
- *Phase.* The circular capsule over one mid grey with `offset` swept at 0, ¼, ½, ¾ CSS px in x
  and, separately, in y — seven cells per scale — at 1x and 2x; G0's scratch measurement decides
  whether the sweep is real at all (a snapped shape collapses it) and, if it is, whether it needs to
  be in both schemes.
- *Poses, schemes, scales.* Both schemes in one pass (the harness captures light and dark profiles
  from one process); active and inactive passes; 1x and 2x. Four passes.
- *Bridge.* `capsule-button` over `light-solid`, `dark-solid`, `mid-dark-solid`, `photo` and
  `checkerboard` exactly as the canonical bed has them, so the new run-to-run bar is laid beside
  W33's readings of the same cells.
- *Budget.* Keep each pass near 120–160 cells so seven runs cost 2–3 h and the four passes about
  10–12 h of machine time, the accessibility beds excluded (Deferred). G0 prices the plan at the
  bar and the parent trims in Decision Log 1 rather than the child.
- *Split.* Declared in the scenes file: calibration, validation and holdout by construction —
  levels, angles and phases interleaved so no family can close on calibration by memorising a
  bin — with the holdout list read once by artifact.

**The harness change** (G0): the new shape kind, the gradient kind, the empty component, the opaque
control, a per-scene **path attestation** (the `CGPath` elements of the resolved shape in the
capture's rect, written beside the fixture in the manifest entry), and `build.sh` gaining a
`VITREA_BUNDLE_ID` override that defaults to today's identifier — every addition decoded from JSON
and covered by the harness's own `self-check`, with the canonical `scenes.json` still decoding to
byte-identical fixtures on the granted bundle (proved by `dump-layers` on one scene, which captures
no pixels). `build.sh` keeps refusing to build over `build/` unless asked, as it does today.

**The grant** (G0): the side bundle at `~/vitrea-w34/side/VitreaReference.app` with identifier
`dev.vitrea.reference-apple.w34`; the grant obtained through `amigo` driving System Settings, or the
user's hand if that fails; positively checked by one scratch capture that renders the material; the
granted bundle re-checked afterwards.

**The instrument** (G0): W33 G0's referee re-derived for the new bed, with the circular capsule's
arcs read as exact circles from the attested path, the opaque control's edge coverage read from
its own capture, the no-glass reference read as the backdrop, and the run-to-run bar computed per
bin and per channel across the seven runs (G1 publishes it; G0 declares how).

**Identification** (G2): G1a's families first, then the ones the new axes make testable — a
coverage-weighted stroke (a one-device-pixel band's geometric coverage times a stroke alpha, in
linear and encoded sRGB), colour blends against the local backdrop (multiply, screen, affine) with
the gradient cells separating local colour from angle, the two-term even law with the exponent now
identifiable on exact arcs, and per-pose and per-scheme coefficients. Closure against the bar on
validation; the holdout once. The vitrea side of the same scenes is rendered through
`compare.ts --set probe` under `VITREA_SCENES` / `VITREA_FIXTURES` so the residual is read against
what vitrea draws today as well as against zero.

## Children

### G0: The bed, the bundle, the grant and the instrument — declared and rehearsed, nothing captured into evidence

Ledger **§5.174**; evidence `packages/calibration/results/2026-09-23-w34-g0-contour-bed/`. Owns the
harness additions, `build.sh`'s identifier override, `apps/reference-apple/scenes-w34-contour.json`,
`test/w34-*.test.ts` and its evidence dir. Does: the machine record (W33 G2's `record-machine.py`
widened with Show Borders, the display mode, the two bundles' cdhashes and linked SDKs); proves the
granted bundle still captures BEFORE any TCC change; the Swift additions with the self-check; the
side build outside the repository; the grant (amigo, else the user) and its positive check; the
granted bundle re-checked; **the scratch measurements** — fractional offset honoured or snapped, the
path attestation written, the empty component and the opaque control rendering as intended, a
gradient cell's bytes matching its declaration — each a handful of cells into `~/vitrea-w34/scratch/`,
never under the evidence dir; the bed declared (scenes file, split, per-pass cell lists via a
`pass-spec.py` of its own, the priced pass plan at the bar); the instrument and the statistics
declared; a `DRY=1` rehearsal of every pass's refusals; a Decision Log 1 draft for the parent.
Acceptance: the record; both grant checks green; every scratch measurement answered; the
declaration reviewed; nothing under `fixtures/`, `profiles/`, `results/matrix.json` or `build/`
touched; freeze 1,818. Stop conditions: the granted bundle no longer captures before G0 touches TCC;
the side bundle's grant evicts the granted bundle's and the recipe does not recover it; a fractional
offset that snaps AND no other phase mechanism; the canonical `scenes.json` no longer decoding on
the granted bundle after the Swift change.

### G1: The sitting — the bed captured at the bar, materialised, committed; the bar published; no read against vitrea

Ledger **§5.175**; evidence `packages/calibration/results/2026-09-23-w34-g1-contour-sitting/`, the
probe fixtures under its `probe/<profile-key>/`. Does: the four passes with the derived sitting
script (opening and closing attestation, HID idle, the version gate), seven runs each, raw runs on
the machine under `~/vitrea-w34/run/`; `materialize` with `--set probe` into the evidence dir with
each cell's own manifest entry and path attestation; the per-bin, per-channel run-to-run bar of every
declared statistic, published as a table before G2 opens; `sitting.md` with wall clock per pass;
per-run attestations and distilled logs committed as W29 G1's were. Acceptance: every run attested;
the cell count per pass as declared or each shortfall named; the bar published; the frozen manifest
and `fixtures/` re-verified untouched; no vitrea render and no read of a wave holdout cell.
Stop conditions: a pass that cannot attest; a cell that will not settle across seven runs
(recorded, not forced); the display mode drifting mid-pass; the grant lost mid-sitting.

### G2: Identification — a law against the bar, or the negative at its resolution

Ledger **§5.176**; evidence `packages/calibration/results/2026-09-23-w34-g2-contour-identification/`.
Does: the instrument run on the committed bed; G1a's families first, then the new ones; fits on the
calibration subset, checks on validation, the wave's holdout once by artifact (`configuration.py
record` before the read); vitrea's render of the same scenes through `compare.ts --set probe` into
the wave's own matrix (`--out-matrix`), X6's four facts before every browser run; the residual
tables against zero and against vitrea; a Decision Log 2 draft for the user with the closure or the
negative, the families excluded and the resolution reached. Acceptance: every family's residual per
bin beside the bar; the split honoured (holdout read once); no material, document, threshold or
canonical row changed. Stop conditions: a holdout read before the calibration fit is committed; a
closure claimed against anything but the published bar.

### G3 (conditional on Decision Log 2 finding a law): The leaf, the seal, the read, the landing

Ledger **§5.177** and following, assigned at dispatch. Opens only on the user's ruling. Does what W33
G1b was chartered to do for the stroke: the leaf through the identity table with its gate-group
tests, the WGSL term, the CSS experiment carried or declined by measurement, the seal of the four
macOS 27 documents (the 26.5 documents at the leaf's identity, digests unmoved), the canonical read,
the holdout by artifact, the split, the stops re-read (C1, B1, B3, X1, thin, M2 re-baselined), the
contour/IoU conflict put to the user as Decision Log 3 before any re-pin, the sheets and the eye,
the changeset. Merged with its capture tree by the X10/X7 rule of W32/W33.

## Cross-Child Contracts

- **X1 — the freeze, intact.** No macOS 26.5-keyed path, row, bound, floor or document changes;
  `freeze.py verify` 1,818 at every merge; the goldens byte-identical through G2; the 27 documents'
  bytes change only in a G3 merge that carries rows read at the new bytes.
- **X2 — the bed before the pixels.** G0's declaration is reviewed and merged before G1 captures;
  G1 captures that declaration and no other; G2 reads what G1 committed and no other.
- **X3 — the side bundle.** Built by `build.sh` under `VITREA_BUILD_OUT` outside the repository,
  same toolchain, SDK and flags as the granted bundle, identifier `dev.vitrea.reference-apple.w34`;
  `build/` never rebuilt; `build-probe/` never granted; the granted bundle's grant checked before
  and after; the side bundle's cdhash in every attestation.
- **X4 — attestation before pixels.** The four facts, Show Borders, the display mode, the bundle
  cdhash and linked SDK, opening and closing; per cell `presentedActive` and `deterministic`; a run
  that fails to attest is quarantined and named.
- **X5 — the lift, bounded.** Native capture is authorised for the W34 probe bed only: the
  wave-local scenes file, the wave's fixture root, the side bundle. The canonical `scenes.json` and
  `fixtures/` do not change; no 26.5 key is captured; no accessibility pass is run.
- **X6 — the browser side as before.** RT and IC 0, the slider 0.5, one capture process, ≥ 60 s
  idle and the foreign-process count before every browser run, every run in `browser-runs.txt`;
  never a browser capture while a native pass runs.
- **X7 — repeats before thresholds.** The run-to-run bar is published in G1 before G2 opens; no
  closure threshold exists before it; "one byte" is the encoding's resolution and nothing else.
- **X8 — the split precedes the fit.** Declared in the scenes file at G0, never re-cut; the wave's
  holdout read once by artifact; the canonical holdout untouched until G3.
- **X9 — routing** (the user's, 2026-09-22): children, reviews and fix waves on `astra-medium` /
  `astra-high` or the default `sol` worker at xhigh; the charter's review on
  `doperpowers:adversarial-reviewer`; reviews read-only; ledger sections as assigned; merges
  `--no-ff -F <file>` with the freeze verified; no attribution trailers, no session URLs; committed
  evidence never rewritten, corrections beside.
- **X10 — the probe bed is not a gated set.** No gate count, predicate, floor or coherence row moves
  on it; its rows carry `fixtureSet: "probe"` in the wave's own matrix, never in `results/matrix.json`
  before a G3 landing.
- **X11 — file ownership.** G0 the Swift additions, `build.sh`, the scenes file, its tests and dir;
  G1 its dir and the committed probe fixtures; G2 its dir; G3 as W33 X11. Nobody touches
  `receded-profile.ts`'s 26.5 block, `DEFAULT_MATERIAL_PROFILE`'s existing values, or
  `SceneViews.swift`'s existing `capsule` and `rrect` resolutions.
- **X12 — raw runs stay on the machine**; logs, attestations and the materialised bed are what is
  committed, as W29 G1 did.
- **X13 — arcs and straights are separate strata everywhere**, and the circular capsule's arcs are
  exact circles by attestation, not by assumption.
- **X14 — the machine's GUI is touched by `amigo` first and the user second**, and every toggle's
  effect is read back from the machine (the TCC check, `defaults`, `displayplacer`), never assumed
  from the action.

## Ordering & Dependency Map

G0 → adversarial review of its declaration → merge → G1 (the sitting; the machine's hours; the
display switched between the 2x and 1x passes as W29 did) → merge → G2 → Decision Log 2 (the user) →
G3 if a law closed, else close. G0 and G1 both need the machine idle and the user reachable for the
grant; G2 needs neither.

## Risks & Mitigations

- **The glass shape snaps to the device grid at a fractional offset**, collapsing the phase sweep.
  G0 measures it first; the fallbacks are a window-origin phase (moving the capture window by a
  fraction, if ScreenCaptureKit's crop honours it) or a 2x-only sweep, and a null result is itself
  a finding about how Apple rasterises the material.
- **TCC evicts the granted bundle's grant despite the distinct identifier** (if it keys on
  something other than the identifier). Positively checked; the recipe recovers; recorded.
- **`amigo` cannot drive System Settings** (first-approval hang, no permission callback). The user's
  hand, per their standing instruction; the wave does not wait on the tool.
- **Machine time.** Four passes near 12 h; the pass plan is priced in G0 and trimmed by the parent
  in Decision Log 1, not silently by the child.
- **The empty component and the opaque control are new render paths.** Each is proved by a scratch
  cell before the declaration is reviewed.
- **A second negative.** An acceptable outcome; the wave's value is then the resolution it states
  and the families it excludes, and Deferred names the third bed.
- **The recede pose.** Inactive passes use the harness's `--inactive` path as W29 did; the accessory
  recede's non-key, non-active state is re-checked in G0.

## Deferred / Out of Scope

- The accessibility beds' contour (Reduce Transparency, Increase Contrast, coupled): not captured
  here; the standard bed identifies the law first.
- The empirical partial correction W33 declined (20.60 from 34.98 bytes): stays declined.
- The composite referee's geometry-qualified domain (W33 Deferred 3): unchanged.
- Span 160's canvas and split (W33 Deferred 4): unchanged; the bed keeps the 320×200 canvas.
- Any change to the canonical bed's scenes or the gate's counts: a later wave's, on a ruling.

## Tracking Map

| child | status |
| --- | --- |
| G0 | CHARTERED |
| G1 | CHARTERED, opens after G0's merge |
| G2 | CHARTERED, opens after G1's merge |
| G3 | CONDITIONAL on Decision Log 2 |

## Decision Log

### Decision Log 1 — the bed's final shape and its price (after G0's draft; the parent's, under the standing "rest on your judgement")

Open. G0 drafts the cell lists per pass, the priced plan, the split and the statistics; the parent
rules the shape and any trimming here.

### Decision Log 2 — a law or the negative (after G2; the user's)

Open. G2 puts the closures against the bar, the families excluded and the resolution reached; the
user rules whether a law is identified and whether G3 opens.

### Decision Log 3 — the contour and IoU bounds if a law lands (in G3; the user's)

Open. W33 G0's forms table stands: no compositing form both reproduces Apple's bytes and keeps
`declaredContourMaxWeb ≤ 1`. If a law closes, the re-pin question is put here with numbers.

## Surprises & Discoveries

- **The parent found 53 leftover agent worktrees under `.claude/worktrees/` (31 GB)** from merged
  waves W12–W28 while grounding this charter, two of them carrying only a stray
  `tsconfig.stripped-dts.json`; all were removed and pruned on 2026-09-23. Their branches remain.

## Revision Notes

- 2026-09-23 (the parent): v1 chartered from the grounding above; sent to adversarial review before
  G0 opens.
