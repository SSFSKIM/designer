# W34 — the contour wave: the capture that identifies Apple's macOS 27 contour stroke (2026-09-23)

**Status: G2 DELIVERED as a negative finding (2026-09-24); parent review and user DL2 ruling pending.**
The v3 charter folded two review rounds (nine findings, then three on the split's execution
contracts); G0 merged and Decision Log 1 is ruled. Chartered
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
   `actualBackingScale` checked after; the capturing bundle's cdhash and `LC_BUILD_VERSION`; the
   display's colour context beside the capture's sRGB setting (`Manifest.swift` records shifts up to
   4/255 from a display-profile change despite it); an opening and a closing read that must agree;
   per cell `deterministic` recorded and the pose attested as the harness attests it —
   `presentedActive` **true** on an active pass, **false with the presentation fields** on an
   inactive one (`Manifest.swift`, W27c). The sitting script is derived from `run-sitting-27.sh` with its `VITREA_APP` /
   `VITREA_HARNESS` seams pointed at the side bundle and its version gate kept.
4. **Repeats before thresholds, and the repeats reproducible from the repository.** Seven runs
   per pass, W29's bar — which is a **state-discovery** convention (the materialiser's own formula
   gives 72.1 % of seeing a one-in-six minority state in seven), not a precision guarantee, and is
   named as such. The per-bin, per-channel run-to-run spread of every declared statistic is
   published in G1 before G2 opens, **computed from all admitted runs before plurality, with the
   losing states preserved**, and from a committed **repeat-evidence artifact** — unrounded per-run,
   per-cell, per-bin channel statistics with populations, input hashes, state membership and the
   estimator, plus deduplicated contour-band and interior crops of every distinct state with their
   run mapping, **as lossless pixel values in their original coordinates and dimensions together
   with every sampled dependency** (the geometry and alignment inputs, the no-glass and opaque-control
   pixels, any neighbourhood an estimator reads) — so the bar AND the instrument re-run from the
   repository without the raw PNGs (which stay on the machine, X12); G0 demonstrates identical
   instrument outputs from raw inputs and from the archive alone, because a table that merely
   reproduces the spread is not replay. No closure threshold is chosen before the bar exists; "one
   byte" appears only as the encoding's resolution; a zero observed spread is not evidence of zero
   variability and buys no tolerance.
5. **The instrument separates what W33 could not, and says what each control proves.** Circular
   capsules beside default continuous ones of the same rect, with the harness writing the
   **supplied** path (the elements of `shape.path(in:)`, G1a's witness applied in-process) beside
   each capture — which attests the path SwiftUI supplied, **not** the transform, pixel origin or
   geometry the window server rasterised, so the rendered alignment is MEASURED from the capture
   (the opaque control's edge and the SDF fit) and the circular cubic's deviation from a true circle
   (+0.006 CSS px, §5.171) is carried as a qualified error, never "exact by attestation";
   continuous rounded rectangles of the same rect at a smaller radius, and a fixed-radius,
   varying-length contrast so curvature separates from surface size; **opaque controls** in
   high-contrast pairs, which measure the rasteriser's alignment and coverage on the ordinary fill
   path and are NOT assumed to transfer to the `glassEffect` path — a partially covered glass edge
   pixel carries the material's body, so the identification declares a **forward model** whose body
   baseline is constrained from stroke-free interior samples with its uncertainty propagated into
   the edge fit; uniform levels and chromatic solids; **matched local-colour contrasts** (the
   backdrop's colour varying ACROSS the contour, as §5.171 asks) beside gradients of declared
   direction and magnitude; a short frequency ladder; subpixel phases defined in **device pixels
   divided by the scale** (so 2x sweeps device phases, not ½-device-px aliases of CSS quarters),
   swept in x and in y with a small **joint x/y** subset; both schemes; both poses; and no-glass
   references of every backdrop captured through ScreenCaptureKit like the glass cells. Arcs and
   straights are separate strata everywhere (W33 X12 carried). A **bridge** of existing cells over
   existing backdrops lays the new bar beside W33's readings — after a **semantic twin audit**
   (clause 7).
6. **Identification precedes fitting and the split precedes identification; a bin mean is not a
   closure.** G2 fits on the calibration subset, checks on validation, reads holdout once;
   least-squares and minimax are both reported. The closure test is the **absolute** per-channel,
   per-radial-shell residual (W33 G0's referee form, absolute values taken before any spatial or
   channel reduction — §5.171 says of the signed bin-mean diagnostic that passing it would not
   establish fidelity, and it is kept as a diagnostic only), over bins with a declared **minimum
   population**, against BOTH the measured bar and an absolute resolution floor declared in G0, with
   the estimator, the multiplier-selection rule, the quantisation treatment and the required
   discriminating power **declared before any model residual is inspected**. Competing families must
   be distinguishable at that resolution; a bed that cannot distinguish them yields the outcome
   **"insufficient resolution"**, and a decomposition that stays non-unique (coverage against body)
   is reported as an **effective rendered contour response**, not as Apple's compositing law
   identified. G1a's families are re-run first so the finding is comparable.
7. **Nothing shipped moves until a law closes.** In G0–G2 no byte changes under `scenes.json`,
   `fixtures/`, `results/matrix.json`, the six material documents, the goldens or any adopted
   threshold; the wave's bed is a probe bed under its own scenes file and fixture root (claims
   §5.30's pattern; W9, W12, W20, W21 and W27e's precedent), committed under the capturing gate's
   evidence directory and read with `fixtureSet: "probe"` into the wave's own matrix. **Every W34
   cell carries the single role `probe` in its scenes file** (`SceneSpec.swift` refuses double
   membership and `compare.ts` selects by one role), and the wave's identification split is a
   separate, wave-local, hashed `split.json` — calibration, validation and holdout over probe-role
   cells, whole phase, geometry and gradient combinations held out and not only interleaved levels —
   **enforced by a wave reader and launcher G0 owns**, not by a hash alone and not by copying W33's
   `rules.py` (which admits every `probe`): the launcher takes an explicit identification-role
   selector defaulting to calibration and validation, validates complete and disjoint membership
   against the declared cells, pins the scenes-file and `split.json` hashes, and drives
   `compare.ts` through its `--scene` allowlist with the native-only controls excluded — the bare
   `--set probe` command is never the documented entry point, because it selects the wave holdout
   too; the reader refuses to open a holdout PNG, crop or numeric-statistics payload the caller has
   not been authorised for, and **negative tests trip on each of those** including when the
   underlying fixture role is `probe`. The bar is published from calibration and validation cells.
   **Sealing is a procedural access boundary, not a claim that committed plaintext is unreadable**:
   the holdout cells' numeric payload, crops and state diagnostics live in their own directory apart
   from the calibration and validation artifacts; a deterministic producer (the capture, the
   materialiser, the archiver) may process holdout inputs without publishing analytical values and
   exposes only the declared inventory, integrity hashes and the admission result; G1's reporting
   and every pre-holdout reader are tested never to deserialise or print that payload; and the
   payload is read once, on the wave-identification receipt (G2). A **semantic twin audit** precedes the split: any W34 cell
   whose geometry and backdrop duplicate a canonical holdout scene (`mid-dark-solid__capsule-button`
   in both poses is one) is excluded from calibration and validation and from the bar, or dropped —
   the same audit applies to the uniform levels. `freeze.py verify` **1,818** at every merge.
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
  restored by re-adding its path. Both existing bundles' designated requirements are **cdhash
  requirements** (`codesign -d -r-`: `designated => cdhash H"88cbbb5b…"` on the granted one), so a
  grant is to one binary's hash: a rebuilt side bundle is a new grant, whatever its identifier.
  `build.sh` has **no guard** over `build/` — it defaults there, overwrites and re-signs — and
  `capture.sh` invokes that default build when `build/harness` is missing; the charter's v1 sentence
  that it "keeps refusing" was wrong and is corrected in Design. The README's recipe: remove the row and re-add, because a recorded
  denial suppresses the prompt. The user's standing instruction for GUI toggles is the codex
  companion's `amigo` first and their own hand if it fails; `amigo` needs `--write`, a per-turn
  bootstrap, and can hang on a first approval (its reference), which is why the fallback is named.
- **The harness.** `capture.sh` execs `build/harness` and nothing else; the W29 sitting script's
  `VITREA_APP` / `VITREA_HARNESS` seams are how another bundle runs a pass. `VITREA_SCENES` and
  `VITREA_FIXTURES` are honoured by both the harness and `cli/compare.ts`, which is what makes a
  probe bed measurable end to end without touching the canonical layout — but not by every
  invocation: `run-sitting-27.sh` calls `rehearse-tints` on a non-dry inactive pass without a
  fixture root, and `main.swift` then opens the compiled `ROOT`'s manifest, which a side bundle
  compiled in a removed worktree no longer has; `DRY=1` skips that branch. The calibration side's
  adapters accept only `capsule` and `rrect` (`src/component-region.ts` throws on any other kind;
  `web/scenes.ts` maps the family by the old capsule name). The capture filter is
  `SCContentFilter(desktopIndependentWindow:)` with `colorSpaceName` sRGB: it captures the window's
  own pixels, so moving the window does not move the contour against the captured grid. The
  canonical holdout recorder `results/holdout-configuration/configuration.py` keys on the four
  shipped documents and the renderer sources and nothing else; the current configuration already
  carries W33's read (2026-09-22T09:42:53Z, §5.172), so its `record` would refuse a W34 read and
  would in any case freeze none of the wave's fitting inputs — it stays the canonical material
  receipt for G3, and the wave's identification read needs a receipt of its own. Shape kinds are `capsule`
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
  existing) at the bed's 120×44 — the **circular anchor** carries the full colour sweep; the same
  pair at a second rect (160×96) so the arcs come at two radii, and a fixed-radius, varying-length
  pair (120×44 and 200×44) so curvature separates from surface size; `rrect` continuous at 120×44
  with radius 12 as the matched rectangle; and **opaque controls** of each path in high-contrast
  pairs (black on white, white on black), which measure the ordinary fill path's alignment and
  coverage and nothing about the glass path — the continuous shapes and the opaque controls take a
  **matched subset** of the backdrops, not the full sweep.
- *Backdrops.* Uniform greys at eight levels (0 … 255) and six chromatic solids on the circular
  anchor; gradients as a new `linear-gradient` kind with `from`, `to` and `angle` at 0°, 45°, 90°,
  135° and two magnitudes, AND matched local-colour contrasts whose colour changes across the
  contour itself (a two-colour backdrop split under the edge), because a global gradient does not
  hold local colour fixed; three separated checkerboard pitches (4, 16, 64) as the frequency
  ladder; a no-glass reference of every backdrop as a scene with an empty component (new kind
  `none`), captured through ScreenCaptureKit exactly as the glass cells are, which is what makes the
  reference's colour management identical.
- *Phase.* The circular capsule over one mid grey with `offset` swept at 0, ¼, ½, ¾ **device**
  pixels divided by the scale (at 2x: 0, ⅛, ¼, ⅜ CSS px — a CSS-quarter sweep at 2x would alias to
  device phases 0, ½, 0, ½), in x and separately in y, plus a small joint x/y subset (¼,¼ and
  ½,½), at 1x and 2x. G0's scratch measurement decides whether the composited shape honours a
  fractional offset at all; if it snaps, **the phase axis is declared unreachable and recorded** —
  the v1 window-origin fallback is withdrawn, because the capture filter takes the window's own
  pixels.
- *Poses, schemes, scales.* Both schemes in one pass (the harness captures light and dark profiles
  from one process); active and inactive passes; 1x and 2x. Four passes.
- *Bridge.* `capsule-button` over `light-solid`, `dark-solid`, `photo` and `checkerboard` exactly
  as the canonical bed has them, so the new run-to-run bar is laid beside W33's readings of the
  same cells; `mid-dark-solid` is NOT in the bridge — both its capsule poses are canonical holdout
  — and the twin audit decides the rest.
- *Sentinels.* A small set of cells captured with a longer settle and a different order seed, so a
  transient the settle procedure repeatably captures is separable from a settled appearance
  (`main.swift` records that distinction).
- *Budget.* The full product of five glass geometries by 27 backdrops by two schemes is about 270
  cells a pass and about 20 h for four seven-run passes at W29's rate — **that is not the plan**.
  The plan is the sparse crossed design above, priced by G0 per pass at the bar, with the cells a
  trim to 120 per pass would drop named, and the parent trims in Decision Log 1.
- *Split.* Every cell `probe` in the scenes file; the wave's own hashed `split.json` beside it
  (clause 7): calibration, validation and holdout with whole phase, geometry and gradient
  combinations held out, the holdout read once by artifact.

**The harness change** (G0): the new shape kind, the gradient kind, the empty component, the opaque
control, a per-scene **path attestation** (the `CGPath` elements of the resolved shape in the
capture's rect, written beside the fixture in the manifest entry), and `build.sh` gaining a
`VITREA_BUNDLE_ID` override that defaults to today's identifier **and a refusal to write over
`build/`** (or any protected output path) unless an explicit override is set, failing closed when
signing fails — every addition decoded from JSON and covered by the harness's own `self-check`, with
the canonical `scenes.json` still decoding on the granted bundle (proved by `dump-layers` on one
scene, which captures no pixels). **The calibration adapters are part of the change**:
`src/component-region.ts`, `web/scenes.ts` and the scene matrix's shape typing learn
`capsule-circular` (with a stated vitrea counterpart — the geometry package's corner curve is
continuous; whether a circular capsule can be drawn on the web is a G0 answer, and if it cannot, the
web comparison for circular cells is declared against the continuous render), and declare `none`
and the opaque controls as **native-only** with no material or shape metric rather than forcing
them through a glass referee; each with a non-capturing test.

**The grant** (G0): the side bundle at `~/vitrea-w34/side/VitreaReference.app` with identifier
`dev.vitrea.reference-apple.w34`, **finalised and cdhash-pinned before it is granted** — built from
G0's final commit, its cdhash recorded, and reused by G1 as that binary; any rebuild is a new grant
and a fresh positive check. The grant obtained through `amigo` driving System Settings, or the
user's hand if that fails; positively checked by one scratch capture that renders the material; the
granted bundle re-checked afterwards. The runbook drives the side bundle by explicit commands with
explicit `VITREA_SCENES` / `VITREA_FIXTURES` on **every** invocation (`rehearse-tints` included),
never through `capture.sh`, and its rehearsal exercises the non-dry inactive branch.

**The instrument** (G0): W33 G0's referee re-derived for the new bed — the circular capsule's arcs
read on the circular SDF with the cubic's qualified error, the rendered alignment measured from the
capture, the opaque control's coverage read from its own capture as an alignment measurement, the
no-glass reference read as the backdrop, the forward model's body baseline **in declared algebra**
(the constrained form, the stroke-free sampling domain, and the propagation to the edge fit — not
the phrase "interior baseline"; where interior samples cannot identify a structured backdrop's
boundary value, the outcome is the effective-response or insufficient-resolution one) — and the
run-to-run bar's estimator declared: per bin and per channel across ALL admitted runs before
plurality, from the repeat-evidence artifact, with the minimum population per bin chosen from the
declared geometry and phase sampling and the absolute resolution floor and discrimination rule from
the quantisation and predeclared synthetic alternatives — non-circular routes that consult no fitted
native residual (G1 publishes; G0 declares how).

**Identification** (G2): G1a's families first, then the ones the new axes make testable — a
coverage-weighted stroke (a one-device-pixel band's geometric coverage times a stroke alpha, in
linear and encoded sRGB), colour blends against the local backdrop (multiply, screen, affine) with
the gradient cells separating local colour from angle, the two-term even law with the exponent now
identifiable on exact arcs, and per-pose and per-scheme coefficients. Closure by clause 6's absolute
test on validation; the holdout once; "insufficient resolution" and "effective rendered contour
response" as admissible outcomes. The vitrea side of the glass scenes is rendered through
`wave.py plan --roles calibration,validation --execute`, with the explicit fixture, matrix
and capture roots documented in G0’s evidence README and its glass-only scene allowlist so the
residual is read against what vitrea draws today as well as against zero; the native-only controls
are not rendered.

**2026-09-23 G0 review correction:** the guarded launcher replaces the former bare probe-set
invocation here. Identification roles, not the native fixture role, control selection;
holdout selection belongs to the once-only receipt and its authorised launcher call.

## Children

### G0: The bed, the bundle, the grant and the instrument — declared and rehearsed, nothing captured into evidence

Ledger **§5.174**; evidence `packages/calibration/results/2026-09-23-w34-g0-contour-bed/`. Owns the
harness additions, `build.sh`'s identifier override and protected-path refusal, the calibration
adapters (`src/component-region.ts`, `web/scenes.ts`, the shape typing) with their non-capturing
tests, `apps/reference-apple/scenes-w34-contour.json`, the wave-local `split.json` with its reader
and launcher (the identification-role selector, the membership validation, the hash pins, the
`--scene` allowlist, the native-only exclusion, the negative tests), the wave-identification receipt
tool (G2's), the derived sitting script, `test/w34-*.test.ts` and its evidence dir. Does: the machine record (W33 G2's `record-machine.py`
widened with Show Borders, the display mode, the two bundles' cdhashes and linked SDKs); proves the
granted bundle still captures BEFORE any TCC change; the Swift additions with the self-check; the
side build outside the repository; the grant (amigo, else the user) and its positive check; the
granted bundle re-checked; **the scratch measurements** — fractional offset honoured or snapped, the
path attestation written, the empty component and the opaque control rendering as intended, a
gradient cell's bytes matching its declaration — each a handful of cells into `~/vitrea-w34/scratch/`,
never under the evidence dir; the bed declared (scenes file with every cell `probe`, the twin audit, the hashed
`split.json`, per-pass cell lists via a `pass-spec.py` of its own, the priced sparse plan at the
bar); the instrument, the forward model's algebra, the estimator, the minimum populations, the
resolution floor and the discriminating-power requirement declared by their non-circular routes;
the repeat-evidence artifact's format declared, produced from the scratch runs, and shown to replay
the instrument identically from the archive alone; the split reader and launcher with their
negative tests; the wave-identification receipt tool with its refusals tested; the side bundle finalised, cdhash-pinned and granted; a rehearsal
that exercises the non-dry inactive branch as well as `DRY=1`; a Decision Log 1 draft for the
parent.
Acceptance: the record; both grant checks green; every scratch measurement answered; the
declaration reviewed; nothing under `fixtures/`, `profiles/`, `results/matrix.json` or `build/`
touched; freeze 1,818. Stop conditions: the granted bundle no longer captures before G0 touches TCC;
the side bundle's grant evicts the granted bundle's and the recipe does not recover it; the canonical `scenes.json` no longer decoding on
the granted bundle after the Swift change. A fractional offset that snaps is NOT a stop: the phase
axis is declared unreachable and the bed proceeds without it.

### G1: The sitting — the bed captured at the bar, materialised, committed; the bar published; no read against vitrea

Ledger **§5.175**; evidence `packages/calibration/results/2026-09-23-w34-g1-contour-sitting/`, the
probe fixtures under its `probe/<profile-key>/`. Does: the four passes with the derived sitting
script (opening and closing attestation, HID idle, the version gate), seven runs each, raw runs on
the machine under `~/vitrea-w34/run/`; `materialize` with `--set probe` into the evidence dir with
each cell's own manifest entry and path attestation; **the repeat-evidence artifact** committed from
all seven runs before plurality (per-run, per-cell, per-bin unrounded channel statistics, hashes,
state membership, the deduplicated contour-band and interior crops of every distinct state with
their run mapping); the per-bin, per-channel bar of every declared statistic over calibration and
validation cells, published as a table before G2 opens, the holdout cells' payload, crops and state
diagnostics written by the producer into their own directory with only their inventory, hashes and
admission result exposed (the materialiser prints voted and refused-state diagnostics today — the
holdout's are captured to that directory, not to the report);
`sitting.md` with wall clock per pass; per-run attestations and distilled logs committed as W29
G1's were. Acceptance: every run attested; the cell count per pass as declared or each shortfall
named; the artifact and the bar committed and re-derivable from the repository; the frozen manifest
and `fixtures/` re-verified untouched; no vitrea render; the holdout payload processed by the
producer only, with the test that G1's reporting never deserialises or prints it green.
Stop conditions: a pass that cannot attest; a cell that will not settle across seven runs
(recorded, not forced); the display mode drifting mid-pass; the grant lost mid-sitting.

### G2: Identification — a law against the bar, or the negative at its resolution

Ledger **§5.176**; evidence `packages/calibration/results/2026-09-23-w34-g2-contour-identification/`.
Does: the instrument run on the committed bed; G1a's families first, then the new ones; fits on the
calibration subset, checks on validation, the wave's holdout once **on the wave-identification
receipt** — its own persistent log and a configuration digest over the scenes-file and `split.json`
hashes, the evidence generation, the instrument and closure declaration, and the committed
candidate families with their coefficients, recorded before the payload is opened, authorised
once, with a failed attempt recorded and a changed candidate after exposure or a second read
refused (tests pin both) — the canonical `configuration.py` untouched and reserved for G3;
vitrea's render of the same scenes through the guarded `wave.py` launcher into the wave's
own matrix (`--out-matrix`), X6's four facts before every browser run; the residual
tables against zero and against vitrea; a Decision Log 2 draft for the user with the closure or the
negative, the families excluded and the resolution reached. Acceptance: every family's residual per
bin beside the bar; the split honoured (holdout read once); no material, document, threshold or
canonical row changed. Stop conditions: a holdout read before the calibration fit is committed; a
closure claimed against anything but the published bar.

**2026-09-23 G0 review correction:** this G2 contract also replaces the former bare probe-set
invocation with G0’s role-aware launcher. The receipt freezes all permitted inventory hashes
before exposure; repeat and materialized archives must each be named if both will be read.

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
  same toolchain, SDK and flags as the granted bundle, identifier `dev.vitrea.reference-apple.w34`,
  **finalised from the last accepted build-input revision and cdhash-pinned before it is granted;
  any change to a build input is a rebuild, a new grant and a fresh positive check, while
  evidence-only commits are not**; `build/` never rebuilt and `build.sh` made to refuse it; `build-probe/` never
  granted; the granted bundle's grant checked before and after; the side bundle's cdhash in every
  attestation; every invocation with explicit roots, none through `capture.sh`.
  **Execution ruling, 2026-09-23 (DL4):** grant-before passed, side SCK passed, original
  grant-after was denied despite distinct identifiers. The wave keeps the side grant;
  the original grant's recovery and positive check are deferred to wave close, not a G0 stop.
  Both identities and the denial are recorded in §5.174; coexistence and the TCC mechanism
  are not established.
- **X4 — attestation before pixels.** The four facts, Show Borders, the display mode and colour
  context, the bundle cdhash and linked SDK, opening and closing; per cell `deterministic` and the
  pose as the harness attests it (`presentedActive` true on active passes, false with the
  presentation fields on inactive ones); a run that fails to attest is quarantined and named.
- **X5 — the lift, bounded.** Native capture is authorised for the W34 probe bed only: the
  wave-local scenes file, the wave's fixture root, the side bundle. The canonical `scenes.json` and
  `fixtures/` do not change; no 26.5 key is captured; no accessibility pass is run.
- **X6 — the browser side as before.** RT and IC 0, the slider 0.5, one capture process, ≥ 60 s
  idle and the foreign-process count before every browser run, every run in `browser-runs.txt`;
  never a browser capture while a native pass runs.
- **X7 — repeats before thresholds.** The run-to-run bar is published in G1 before G2 opens; no
  closure threshold exists before it; "one byte" is the encoding's resolution and nothing else.
- **X8 — the split precedes the fit.** Every W34 cell `probe` in its scenes file; the wave's
  identification split in a hashed wave-local `split.json` declared at G0 after the twin audit,
  enforced by the wave reader and launcher before any image, crop or statistic is opened, never
  re-cut; the holdout's payload behind the procedural boundary of clause 7 and read once on the
  wave-identification receipt; the canonical holdout untouched until G3 and never a fitting or bar
  input here.
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
- **X12 — raw runs stay on the machine**; logs, attestations, the materialised bed AND the
  repeat-evidence artifact (statistics and contour/interior crops of every distinct state) are what
  is committed, so the bar re-derives from the repository.
- **X13 — arcs and straights are separate strata everywhere**; the circular capsule's arcs are read
  on the circular SDF with the cubic's qualified error and the rendered alignment measured, not
  "exact by attestation".
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
  G0 measures it first; if it snaps the axis is declared unreachable and recorded (a finding about
  how Apple rasterises the material), and no window-origin fallback is attempted — the capture
  filter takes the window's own pixels, so moving the window moves nothing against the grid.
- **Seven runs discover states; they do not measure precision.** The bar is a spread estimate with
  a stated population; the closure test carries an absolute floor and an "insufficient resolution"
  outcome so a quiet bin cannot manufacture a closure.
- **The opaque control does not transfer to the glass path**, and coverage against body may stay
  non-unique. The forward model and its body baseline are declared; a non-unique decomposition is
  reported as an effective response, not a law.
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

- G0's quarter-phase axis is unreachable on the measured path; a genuinely independent
  phase mechanism needs a new identifying experiment if G2 cannot close without it (§5.174).
- The original bundle's grant is restored and positively checked at wave close under DL4.
- The one-code settle/order dependence, sixteen under-populated 1x rectangle bins and the
  existing continuous-native/circular-web capsule mismatch remain qualified gaps (§5.174,
  tracker), not silently accepted fidelity or permission to pool bins after fitting.

- The accessibility beds' contour (Reduce Transparency, Increase Contrast, coupled): not captured
  here; the standard bed identifies the law first.
- The empirical partial correction W33 declined (20.60 from 34.98 bytes): stays declined.
- The composite referee's geometry-qualified domain (W33 Deferred 3): unchanged.
- Span 160's canvas and split (W33 Deferred 4): unchanged; the bed keeps the 320×200 canvas.
- Any change to the canonical bed's scenes or the gate's counts: a later wave's, on a ruling.

## Tracking Map

| child | status |
| --- | --- |
| G0 | DELIVERED for independent review — phase grid unreachable, 148 cells/pass declared, side active and canonical pixel check positive; DL1 ruling and review/merge pending (§5.174). Original grant recovery deferred by DL4 **MERGED 2026-09-23 as `d2201845`; Decision Log 1 ruled at the merge.** |
| G1 | DELIVERED 2026-09-24 for parent review/merge — all 40 runs admitted, 592/592 cells published, separate bars and archive-only replay complete (§5.175); G2 not opened **MERGED 2026-09-24 as `7c5c71c3`** (§5.175; independent review with no material finding). |
| G2 | DELIVERED, §5.176 — no point-closed law; boundary-body counterexample and qualification recorded; once-only receipt complete; web bed captured. Parent review and DL2 ruling pending. Evidence directory is dated 2026-09-24. **MERGED 2026-09-24 as `5e807599`** (§5.176; review closure `053bb29e`–`81ad53c7`; Decision Log 2 put to the user). |
| G3 | CONDITIONAL on Decision Log 2 |

## Decision Log

### Decision Log 1 — the bed's final shape and its price (after G0's draft; the parent's, under the standing "rest on your judgement")

**RULED by the parent 2026-09-23 at G0's merge (`d2201845`), under the standing "rest on your
judgement": the full sparse bed at 148 cells per pass, as G0 declared and its independent review
recommended.** The 120-cell alternative is declined because its 28 drops per pass are the
second-radius pair with its opaque controls, both 135° gradients and their references, and both
y-edge local-colour contrasts — the curvature-against-size and directional contrasts this wave
exists to identify. The phase axis is absent by measurement (quarter-device steps collapse to two
states at both scales; no window-origin workaround), which is a recorded finding and not a trim.
The three longer-settle, reordered sentinels per pass stay, kept apart from the seven runs, and G1
publishes the normal and long protocols as separate bars because the grey sentinel moved one code
at eighteen edge pixels. Price accepted at 10.9356 h plus 12.6 min before waits and the display
switches; G1 opens only in a window the user names for leaving the machine untouched, with the
other session's browser closed, because G1's driver requires zero foreign capture processes and
the user's G0 exception does not extend to it. The identification split (138 / 26 / 30) and the
closure declaration are frozen as pinned; G2 chooses nothing that G0 did not declare.

**G0 draft, 2026-09-23; parent ruling still open.** Recommend the full sparse bed at **148
cells/pass**, seven runs in each of four passes: **10.9356 h** at W29's 9.5 s/cell, plus
**12.6 min** for three longer-settle/order-seed sentinels per pass. The phase grid is omitted
under the measured-unreachable clause: quarter-device steps collapse to two states at both
scales; no window-origin workaround. Every original/corrected reading is retained (§5.174).

194 scene ids, all fixture-role probe; identification split **138 calibration / 26 validation /
30 holdout**, pinned separately. Both poses and schemes remain on glass; the 46 native-only
controls/references per pass are captured in the light profile and shared across schemes.
No-glass grey in the inactive scratch is byte-stable in both schemes; the raster path itself
has no scheme-dependent colour input. Geometry/backdrop twins of canonical holdout are
excluded from fitting even across tint or pose, so the dark-solid capsule bridge is
identification-holdout-only, beside the explicitly omitted mid-dark bridge.

`pass-plan.json` names all cells and an exact **120-cell alternative**: drop 28/pass by
removing the second-radius pair and its opaque controls, both 135° gradients/references,
and both y-edge local-colour contrasts/references. That loses identifying axes and is not
G0's recommendation. The bed with the phase axis absent is the alternative this gate puts
before DL1, not permission to silently substitute a different mechanism.

`closure.json` fixes the absolute per-channel/shell statistic, population floor4, observed
pair envelope with multiplier1, one-code quantisation floor, nuisance propagation and
competing-family discrimination. Sixteen 1x rectangle bins remain under-populated; actual
physical decomposition can still return insufficient resolution. The grey sentinel's two
internally unanimous protocols differ by one code at 18 edge pixels; neither is relabelled
zero or universal settledness. Seven-run bars remain G1's, not these scratch readings.

### Decision Log 2 — a law or the negative (after G2; the user's)

**DRAFT FOR THE USER, not ruled (G2 complete, 2026-09-24; §5.176).** Recommend closing W34
at the negative and **not opening G3**. No tested fitted configuration point-closes validation
at the declared one-code floor. More importantly, every endpoint and both contour parts have
an inner-shell counterexample where the nominated outside stroke has zero support: changing
its alpha, colour or exponent cannot repair that nominated body/path decomposition. The
separate nuisance/discrimination checks establish no unique physical decomposition. The once-only
receipt is complete; its unaltered held reading is confined to §5.176 §7 and its own artifacts.

No G3 leaf or identity values are nominated, and **no material document moves**. The next useful
study is an explicitly declared body-boundary/radial-model extension on the existing non-holdout
pixels, not another full sitting merely to add repeats. If the user chooses to continue, a later
blind confirmation needs a newly authorised, genuinely unexposed bed/receipt; it must improve
independent glass-path coverage/registration or the boundary body constraint, prove any new
phase mechanism reachable first, and retain local-colour/gradient contrasts and populated arcs.
The physically constrained alpha family and the affine/angular families' coefficients, residuals,
populations and bars are in the gate's complete index. Failed nominated fits are not a claim
that every possible colour law is excluded, and interval compatibility is not Apple's internal
compositing law identified. The alternatives remain the user's: close at this finding, or charter
that narrower continuation. No threshold widening, partial correction, native capture or G3 work
has been chosen on their behalf. Original-grant restoration remains DL4's wave-close obligation.

### Decision Log 3 — the contour and IoU bounds if a law lands (in G3; the user's)

Open. W33 G0's forms table stands: no compositing form both reproduces Apple's bytes and keeps
`declaredContourMaxWeb ≤ 1`. If a law closes, the re-pin question is put here with numbers.

### Decision Log 4 — keep the side grant for the wave; restore the original at close (2026-09-23, parent ruling)

Under the standing “rest on your judgement”, the parent rules that the wave runs on the
side bundle and does not restore the original grant now. Restoring it might displace the
side grant, and no remaining G0/G1 step needs an original-bundle capture: canonical decoding
was already proved with `dump-layers`. Original grant recovery by the README recipe and a
positive capture check are required at wave close. The supplied distinct identifiers did
not yield simultaneous grants in the observed checks; no internal TCC mechanism is inferred.
Original cdhash `88cbbb5b2db0af50167c0d7004f3bd7d3ebe6427`; side cdhash
`830a00c6ff7b9ff74898c745e30e9335e31488a5`; §5.174 preserves the original's denial.

The side's first launch after granting was repeat-stable but inactive. Up to three fresh
one-cell scratch checks are authorised to establish the active pose, keeping every attempt;
if none attests active, diagnose before measuring. This is a pose check, not permission to
repeat noisy measurements until they pass. The user's earlier “Proceed; record it as foreign”
ruling remains: every capture carries opening/closing foreign-process counts and PIDs;
G1 exclusivity remains the parent's decision. Subsequent reads currently report zero.

## Surprises & Discoveries

- **G2's nominated boundary body fails where the outside stroke has no support**
  (2026-09-24, §5.176 §5). At nominal geometry, every subpixel in shell [−2,−1) is
  inside the body and the outside [0,1) band has zero coverage. Yet populated validation
  bins miss by 2–27.375 encoded codes, with both parts and every endpoint represented;
  the linear family also fails. All stroke coefficients are algebraically inert there.
  This sharpens the negative beyond an optimizer failure while narrowing its physical
  meaning: it rejects the nominated body/path/stroke decomposition, not Apple's colour
  law in isolation. A body-boundary/radial study on existing non-holdout data is a more
  useful next step than another full sitting that merely adds repeats. No new model,
  capture permission or G3 leaf is authorised by that recommendation.

- **G0 grant-after refused despite distinct bundle identifiers** (2026-09-23, §5.174).
  The original captured before; the side captured after the user's grant; the original then
  returned TCC denial without a manifest. Both binary identities are unchanged. The side's
  capture was repeat-stable but not actively presented, so it is not an admitted active
  baseline. The UI/TCC mechanism is not identified. Recovery through the user's hand and
  positive checks of both bundles remain pending; no rebuild or further grant change occurred.
  DL4 subsequently defers original-grant recovery to wave close while the side runs the wave;
  the original denial stays recorded rather than being relabelled a positive coexistence check.

- **The parent found 53 leftover agent worktrees under `.claude/worktrees/` (31 GB)** from merged
  waves W12–W28 while grounding this charter, two of them carrying only a stray
  `tsconfig.stripped-dts.json`; all were removed and pruned on 2026-09-23. Their branches remain.

## Revision Notes

- 2026-09-24 (the parent, G2's merge): G2 merged to main as `5e807599` with `--no-ff` after an
  independent review (astra, high) that reproduced fits and minimax optima, found the negative
  sound in its scope and three evidence defects, all closed on the branch with red-then-green
  tests and the corrections beside the recorded values; `freeze.py verify` 1,818. **Routing
  deviation, recorded:** the review fix wave began on `astra-high` and was cut off by the Codex
  accounts' usage limit after committing the code corrections; a `sol-xhigh` continuation was
  refused by the same limit before it started; the closing (recording the re-derived readings and
  committing them) ran on the default Claude worker, against the user's routing note of
  2026-09-22, because nothing else was available and the work was bounded and fully specified.
  Decision Log 2 is put to the user with G2's draft; Decision Log 4's restoration of the original
  bundle's grant is the wave-close action that follows the ruling.
- 2026-09-24 (the parent, G1's merge): G1 merged to main as `7c5c71c3` with `--no-ff` after an
  independent review (astra, high) that re-derived every published hash, plurality, attestation
  and bar and found no material finding; `freeze.py verify` 1,818; the bed of 592 cells and the
  114 MiB repeat archive are committed as the charter's clause 4 asks, the archive being 103 MiB
  of per-run statistics and 11 MiB of compressed lossless crops (a tracker entry weighs the
  repository cost). The evidence index is renamed from `README.txt` to `README.md` in this record
  and the sitting record stays `sitting.json`, because the worker's own model instructions forbid
  Markdown reports; §5.175 carries the narrative tables. One correction to the parent's own
  dispatch summary, not to the evidence: the normal bars also reach 0.5 byte on 1x light active
  arcs (one witness, population 8), as §5.175 records. G2 opens on this revision.
- 2026-09-23 (G0 delivered, §5.174): the side active pose and one canonical byte identity
  proved; quarter-device phases collapse at both scales. Declared the phase-free sparse bed,
  conservative canonical-twin audit, separately pinned split, wave reader/launcher and receipt,
  forward/closure algebra, role-separated repeat archive and actual archive-only replay.
  Controls and both inactive schemes attested; a one-code sentinel protocol difference is
  preserved. Four real no-pixel rehearsals presented 148 each; the non-dry inactive root seam
  was separately exercised without capture. No wave capture or fit, browser render, material
  change or canonical holdout read. DL1 and independent review/merge remain the next gate.

- 2026-09-23 (G0 checkpoint, §5.174): native controls, supplied-path export, protected build
  guard and calibration adapters built and tested. The user allowed the foreign browser to
  remain during G0 with opening/closing process counts and repeat failures preserved; this is
  not a G0 exclusivity stop. Companion credits exhausted before GUI action, so the user granted
  the side and owns subsequent toggles through the parent. Original grant-after denied; G0
  stops for recovery. No bed/split, instrument/bar or G1 permission is implied by this checkpoint.

- 2026-09-23 (the parent, v3): the second round attacked the folds and found six of nine sound as
  written, one sound operationally (the cdhash pin, with "final commit" read as the last accepted
  build-input revision — X3 now says so), one sound but incomplete at the holdout boundary (the
  repeat archive, which now has to hold lossless pixels with every sampled dependency and be shown
  to replay the instrument — clause 4), and one incomplete (the probe role with an independent
  split), which its three blocking findings complete: (1) `compare.ts --set probe` selects the wave
  holdout and the native-only controls, and W33's `rules.py` admits every `probe`, so G0 owns a
  wave reader and launcher with an identification-role selector, membership validation, hash pins,
  the `--scene` allowlist and negative tests on PNG, crop and statistics access (clause 7, G0, X8);
  (2) the canonical holdout recorder keys on the shipped documents and sources, already carries
  W33's read and would freeze none of the wave's fitting inputs, so G2 reads on a
  wave-identification receipt of its own (Grounding, G2); (3) sealing is defined as a procedural
  access boundary with a producer exception, a separate holdout directory and tests that reporting
  never prints the payload (clause 7, G1). The body baseline's algebra and the non-circular routes
  for populations, floor and discrimination are G0 obligations stated in Design. No third round:
  the remaining questions are G0 design work, and G0's declaration is itself reviewed before G1.
- 2026-09-23 (the parent, v2): the adversarial review of v1 returned nine findings, all blocking
  and all verified against the files it cited; every one is folded. (1) The closure test is the
  absolute per-shell residual with minimum populations, a resolution floor, the estimator and
  multiplier rule declared before residuals are seen, distinguishability required and
  "insufficient resolution" / "effective rendered contour response" as outcomes — the signed
  bin-mean is a diagnostic only (clause 6). (2) The opaque control measures the fill path's
  alignment and coverage and is not assumed to transfer to the glass path; a forward model with a
  body baseline from stroke-free interior samples; matched local-colour contrasts across the
  contour (clause 5, Design). (3) The bar re-derives from a committed repeat-evidence artifact
  computed before plurality with losing states kept; X12 amended (clause 4, G1). (4) Phase offsets
  in device pixels over the scale with a joint x/y subset; the path export attests the supplied path
  only, alignment is measured, the cubic's error qualified; the window-origin fallback withdrawn
  because the capture filter is window-independent (clause 5, Design, Risks). (5) Every cell is
  `probe` in the scenes file and the identification split is a hashed wave-local `split.json`
  enforced before image access, whole combinations held out, holdout repeat statistics sealed
  (clause 7, X8). (6) A semantic twin audit before the split; `mid-dark-solid` dropped from the
  bridge because both its capsule poses are canonical holdout (clause 7, Design). (7) G0 owns the
  calibration adapters and their tests; native-only controls declined from glass metrics; the
  circular capsule's web counterpart is a G0 answer (Design, G0). (8) Every invocation with explicit
  roots including `rehearse-tints`, a rehearsal of the non-dry inactive branch, and clause 3's pose
  attestation corrected — inactive captures attest `presentedActive` false (clause 3, X3, X4).
  (9) `build.sh` has no guard today and designated requirements are cdhash-based: the side bundle is
  finalised and cdhash-pinned before granting, any rebuild is a new grant, `build.sh` gains the
  refusal, `capture.sh` is never used for it (Grounding, Design, X3). The review's verdict notes are
  folded too: the sparse crossed design replaces the unpriced full product (about 270 cells a pass,
  about 20 h), sentinels with a longer settle and another order seed, a fixed-radius varying-length
  contrast, three pitches, the display colour context attested. Sent to a second round on the folds.
- 2026-09-23 (the parent): v1 chartered from the grounding above; sent to adversarial review before
  G0 opens.

- 2026-09-23 (G0 independent-review fix wave, §5.174 §14): reject symlinked build descendants
  before writes and prove binary neutrality by the fresh verification build's matching cdhash;
  bind every holdout reader to the receipt's frozen inventory-hash manifest; implement the
  declared gradient prediction range rather than deviation from the full fit. Regression
  tests reproduced all three defects before the fixes. The two operational bare-probe
  instructions above now name the guarded launcher. No closure declaration number changed;
  the full 148-cell recommendation and pending DL1 are unchanged.

- 2026-09-24 (G1 delivered, §5.175): all 28 normal and 12 long sentinel runs admitted,
  no refusal or quarantine; 592/592 cells materialized only after the full repeat archive
  was committed. Normal/long bars published separately on 336/16 non-holdout cells, with
  maximum admitted envelopes 0.5/0.223684211 byte and 192 under-populated normal 1x arc bins
  unmeasured. Archive-only instrument and alignment replay reproduce 2,400 observations;
  holdout producer payloads stay sealed and the receipt remains unspent. Mode68 restored;
  freeze1,818 and all required checks pass. Parent review/merge precedes G2; no fit or render.

- 2026-09-24 (G2 checkpoint, §5.176): the guarded native instrument and calibration-only family
  fits are committed before exposure. All 336 non-holdout web cells render under four fresh X6
  preflights; three standard curvature measurements refuse, leaving 333 wave-matrix rows while
  the contour reader retains all 336 captures. G1's missing manifest caveats field is handled by
  a wave-local metadata projection, with the failed original report preserved. The exact-body
  uncertainty propagation is offline; no native capture, build, TCC action or material change.
  G2's actual evidence directory is dated September 24, beside the prospective September 23
  path in its original child brief. No holdout reading or user ruling is asserted here.

- 2026-09-24 (G2 delivered, §5.176): 672 calibration-fitted configurations and their validation
  bins recorded; the nominated outside-only decomposition has a coefficient-independent inner-body
  floor, and no point-closed law is identified. Full body/reference/geometry/numerical propagation
  and G0 discrimination precede the committed once-only receipt. The held read and its web captures
  are complete, with no refit or second exposure; its figures stay in its own ledger table.
  All 408 glass cells have real-GPU web captures. The standard matrix remains 333 non-holdout rows,
  with three curvature refusals preserved; held cells are read by the guarded contour instrument.
  Closing calibration 658 passed/1 skipped, boundary 6/6, numeric 6/6, freeze1,818. No material,
  canonical evidence, adopted bound, native capture, rebuild or TCC change. Parent review and the
  user's DL2 ruling are next; this child neither merges nor opens G3.

- 2026-09-24 (G2 review fix wave, §5.176 §9): the independent review's three corrections are
  applied beside the original readings. Under the corrected half-pixel affine-body convention,
  three inner-shell floors move (1x dark active 9.000 / 9.237 → 10.000 on arc / straight, 2x
  dark inactive arc 2.778 → 3.000); every floor still exceeds one code, and the 2–27.375 code
  range this charter's Surprises entry cites is unchanged. G0's verdicts stay 128 insufficient
  resolution with 19/128 interval-compatible. The faithful W33 bases close 0/128 against both
  no-glass and the web. The spent receipt's complete event carries forty bookkeeping fields;
  stripping them restores the begin digest exactly. The held figures were not re-read. Decision
  Log 2's draft and the tracker entry cite no number that moved, and the conclusion stands.
