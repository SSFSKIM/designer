# W22 — the resting sweep: the highlight band gated on the shimmer running, the rim re-read per side on both beds (2026-09-08)

**Status: IN PROGRESS — chartered 2026-09-08 from W21 Decision Log 3 (b) (claims §5.90 §4) at the
0.10.0 cut, on the user's "let's continue with that sweep"; the user's two eye observations on the
W21 landing sheets pinned as findings the same day (claims §5.93). G0 CLOSED 2026-09-08 (claims
§5.94; Decision Log 2): the gate merged with the goldens byte-identical, the light rim read per side,
`specularGain` to be fitted to 0 and three constants declined, the `impulse` capsule chartered to
the appearance switch, the nested pane a plumbing defect taken as G3 ahead of G1. G3 dispatched.**

Composite spec: design at the top; Decision Log, Surprises, Deferred and Revision Notes at the
tail. Parent: `2026-08-28-post-v1-wave.md` (the W22 row; wave Decision Log 23 (c)'s ordering, this
wave taken ahead of the thick-span composite on W21's recommendation). The defect it corrects was
found on W21's rim fit (`2026-09-06-w21-dark-scheme.md` Decision Log 3 (b), Surprises; the
tracker's entry "The highlight pass draws its specular sweep as a stationary band…"). The rim work
it re-reads is W11c's, W12's and W18's (the two-light rim: `optics.regular.rimAlpha`,
`specularGain`, `lightDirection`), all fitted with the band present. The user said this wave is
the last one chartered for now; what follows it is the user's call, not the parent's list.

## Purpose

Every resting surface vitrea draws carries a specular shimmer parked on its left edge, in both
colour schemes, since the highlight pass landed. `packages/renderer-webgpu/src/wgsl/highlight.ts`
draws the sweep as a Gaussian band in the rim's angular coordinate centred at `hu.sweep.x · 2π`;
the motion channel `sweep` is 0 when nothing drives it (`render-model.ts`, `channels.ts`'s
`IDLE_CHANNELS`), and 0 radians in that coordinate is the left edge. Nothing in v1 drives the
channel at all — `reduced-motion.ts` says so ("shimmer travel has no channel in v1; the specular
sweep is the renderer's"), no binding writes `--vitrea-sweep`, and the CSS tier has no sweep — so
the band sits at `sweepGain` 0.85 on the left of every surface at rest, and the pass's own contract
("the band is not drawn stationary, it is not drawn") is false at nominal motion.

W21 isolated it exactly (claims §5.90 §4): with the rim's specular term at zero, vitrea's left edge
reads 0.12–0.15 above its other three sides on every dark solid; the same documents at `sweepGain`
0 move the left side by −0.119 to −0.145 and every other side by +0.0000, and left then equals
right to the fourth decimal. On the canonical dark bed it is the whole of W21 clause 4's miss
(`dark-solid__rrect-md` +0.1394 at 1x, +0.2445 at 2x on the left; `mid-dark-solid__capsule-button`
+0.0518 / +0.0579). On the light bed it has never been read per side, and three waves of rim work
fitted a two-light rim over it — the light reference's rim has left equal to right; vitrea's does
not. It could not be fixed inside W21 because W21 bound the light captures byte-identical, and the
correct fix moves every light capture with a rim.

Beside the sweep, two things the user's eye found on the W21 landing sheets, pinned with the bed's
numbers at claims §5.93 (`results/2026-09-08-w22-resting-sweep/finding/`):

- **The dark capsule over `impulse` is flat where Apple's is glass.** Apple draws a visible rim
  ring (0.0145 / 0.0137 top and bottom against vitrea's 0.0030) and passes the centre square
  through the body as a soft glow (the silhouette interior reads 0.021–0.026 against the declared
  body's 0.0066; vitrea reads 0.0037 / 0.0033 under both, with no structure —
  `luminanceSlopeWeb` 0.000005 against the reference's −0.009). vitrea's tone collapse
  (`backdropToneLow` 0.02 / `High` 0.055 — W7's light-scheme measurement, inherited by the dark
  patch unmeasured) folds the dark material onto the black between the squares; the dark reference
  does not collapse there. W21 clause 3 scored the cell "met (collapsed)" against the declared
  body alone.
- **The nested pane in dark inverts.** Apple's overlay pane is darker than its base; vitrea's is
  lighter than its base, a flat mid grey on the GPU tier and lighter still on the CSS tier. And
  Apple's base pane blurs the checker to a haze vitrea's does not (`blurSigmaNative` 4.84 px at 2x
  against 0.69; the thick-span composite of wave Decision Log 23 (c)). No per-pane number exists:
  the declared reader refuses composites, and the matrix reads the stack as one region.

This wave gates the band on the shimmer actually running, so a resting surface draws its ambient
rim alone; re-reads the rim per side on both beds with the band gone and re-fits the light rim's
constants on the rows that separate them; lands on the GPU tier, rebuilds the canonical bed and
re-reads every rim row and floor the band had been holding; and measures the two eye findings
under the declared geometry — extending the reader to a stack's two boxes — so that each is either
closed here by one constant or chartered with its numbers.

## Parent-Level Acceptance

Binding. The numbers are the charter's; G1 re-declares them with G0's readings beside.

1. **Nothing at rest.** A surface with the sweep undriven writes no sweep term to the highlight
   canvas: the pass's gain is 0 at `IDLE_CHANNELS` (a renderer unit test on the pass arguments);
   the press glow is unchanged. A surface whose shimmer is driven still draws the band at the
   driven phase (the golden `highlight-press-glow`, which captures the highlight canvas with a
   driven sweep, reproduces byte-identical once its scene declares the shimmer running; the eight
   optics goldens reproduce byte-identical — the isolation proof's attribution).
2. **The rim per side, both beds.** On every untinted texture-tier cell over a solid backdrop at
   both scales, in both schemes: the left side within 0.03 of the right, and each side's rim-band
   peak within 0.03 of the reference's under the declared geometry. On the dark bed W21 clause 4's
   two open cells close (`dark-solid__rrect-md`, `mid-dark-solid__capsule-button`, left side).
3. **The light rim re-fitted on its rows.** `optics.regular.rimAlpha`, `specularGain` and
   `lightDirection` on the light profile re-read per side with the band gone; a constant whose
   rows separate it is re-fitted on them and carries them; one whose rows do not is declined and
   left where it is (C9a §6.2's rule). The dark patch's `rimAlpha` 0.082 was fitted with the band
   present on the left of six cells × three sides; it is re-read and moved only if its rows move it.
4. **The bed no worse anywhere, better on the rim.** At both scales on the GPU tier: calibration ΔE
   mean not above the W21 bed's on either scheme; no untinted row worse than the W21 bed by more
   than 0.001 in ΔE mean or 0.005 in `ssimMean`; every `rimPeakLuminance` row moved is recorded
   with its direction; no adopted bound widened; every floor re-read — a floor whose cell recovers
   its bound goes inert and is removed with its reason, none is re-pinned without the user.
5. **The holdout once**, at G1's dry run on the frozen configuration, both schemes, both scales;
   G2 reproduces byte for byte.
6. **The CSS tier derives.** The CSS tier has no sweep, so its captures are expected byte-identical
   on both schemes; verified, not assumed. A CSS row that moves is explained.
7. **The two eye findings measured.** The dark `impulse` capsule read under both instruments with
   the discrepancy reconciled (the centre glow; the ring); vitrea's collapse read against the dark
   reference's non-collapse with a scratch prediction (`backdropToneMax` 0 in the dark patch) so
   the term's size is known. The nested pane read per pane on both beds, both tiers, both scales
   — the reader extended to stacks — with the overlay's excess over its base stated for the
   reference and for vitrea. Each finding then either closes here (one constant on its own rows,
   inside this wave's stops) or is chartered with the numbers in the Deferred list and the ledger.
8. **By eye, and the ledger.** The landing sheet (native | GPU before | GPU landed | CSS) at both
   scales on the solids and the two eye cells, in both schemes, before publish; the user's veto
   kept. **0.11.0** after the landing (a `vitrea-web` minor: the material moves).

## Grounding Baseline (the W21 bed, 2026-09-08, `800a04f`; matrix at the 0.10.0 landing)

- Light GPU calibration ΔE 0.0033 / holdout 0.0091 (both scales within 0.0002); dark GPU
  calibration 0.00410 at both scales, holdout 0.01612 / 0.01596 (claims §5.91).
- The sweep's isolation (claims §5.90 §4; `w21/g1/fit-rim.txt`): `sweepGain` 0 moves the left side
  −0.119 to −0.145 on the dark solids, other sides +0.0000. On the dark `light-solid` cells the
  left side reads +0.0891 above the reference where top and bottom read −0.05 to −0.06
  (`fit-rim.txt` lines 152–158) — the band on one side of a rim otherwise too faint.
- The light per-side rim has never been read. W9's light probe snapshots and the canonical light
  fixtures exist; `probe-score.ts --interior declared --profile <light>` reads them per side.
- The highlight pass and its uniform: `highlight.ts` (`hu.sweep` = phase, band width, gain, rim
  width); `renderer.ts` sets `sweepGain: policy.glass === "none" ? 0 : material.sweepGain` and
  `sweep: lead.channels.sweep`; `passes.ts` packs them. `material.ts`: `sweepBandRadians` 0.55,
  `sweepGain` 0.85, `lightDirection` [−0.3714, −0.9285], light `rimAlpha` 0.18 (regular) / 0.14
  (clear), `specularGain` 0.55; the dark patch `rimAlpha` 0.082, `specularGain` 0.
- The goldens: `highlight-press-glow` is the only golden capturing the highlight canvas and drives
  `sweep: 0.15`; the isolation spec's `POST_WAVE_HASHES` pins it byte-identical since 2026-08-25.
  The e2e harness drives `sweep` 0.3 / 0.6 in two scenes.
- The two eye cells: `results/2026-09-08-w22-resting-sweep/finding/eye-finding.txt` and the two
  crops; the numbers in the Purpose.
- The gate: `adopted-thresholds.test.ts` at `PREDICATE_EXCLUDES` 33 lines, `UNMET_ROWS` 11, the
  four W21 instrument floors on the 2x dark nested pane; the rim rows are `rimPeakLuminance` /
  `rimPeakDistance` / `rimFwhm` on the material axis.

## Design (advisory unless marked)

**The gate is an amplitude the driver owns (binding).** The sweep's position is a phase; what the
pass lacks is an amplitude. `SurfaceChannelValues` gains `shimmer` ∈ [0, 1] (`IDLE_CHANNELS`
0; published as `--vitrea-shimmer` beside `--vitrea-sweep`; `RenderSurface.channels` likewise, 0
at rest) and the highlight pass's gain becomes `sweepGain × shimmer(lead)`, with Reduced Motion's
CPU-side zeroing unchanged. At rest the term is exactly 0 and the pass's early return writes
nothing — the contract the pass's own comment already states. Why an amplitude rather than a
sentinel on the phase or a parked phase: the angular coordinate covers the whole contour, so no
phase is off the surface; and an amplitude is what a shimmer driver will output when one exists
(the design's §Motion names shimmer travel; v1 has no channel for it), so the seam is the future
driver's, not a flag. The lead surface (the largest `glow`) supplies the phase today; the
amplitude is read from the same lead. The golden and e2e scenes that drive `sweep` declare
`shimmer: 1`, so their bytes are the proof that only resting surfaces moved.

**The light rim re-read before it is re-fitted (advisory; G0 decides the form).** With the band
gone the light bed's left side drops by an amount G0 measures on vitrea's own captures at
`shimmer` 0 (the same isolation W21 ran on the dark bed, in scratch); the reference's per-side rim
on the light solids (`light-solid`, `mid-dark-solid`, `dark-solid` under the light profile, and
W9's probe grid) says whether the light rim is flat (then `specularGain` is fitting the band and
goes to its rows' answer, likely down) or top-weighted (then the specular is real and `rimAlpha` /
`specularGain` are re-fitted per side by W21 G1's `fit-rim.py` method on the light solids). Two
constants at most on the light profile; the dark patch's `rimAlpha` re-read on its six cells with
the band gone — it was fitted against three sides where the left carried the band, so it may not
move at all. `lightDirection` is the shadow's direction too (`optics.ts`'s `light.xy` feeds the
inner shadow): it moves only if the rim's per-side read separates it, and the shadow rows are read
beside it.

**The instrument (binding).** W21's declared-geometry read (`probe-score.ts --interior declared`)
is the rim and body definition on every gate in both schemes; extended for this wave to (i) the
light profiles' canonical captures and W9's light probe snapshots, and (ii) a stack: the base's
declared box with the overlay's box cut out, and the overlay's box, each eroded 6 CSS px, each
with its own rim band — so the nested pane has two bodies and eight sides. The reader's recovery
is re-validated on a stack by injection (X3).

**The two eye findings (advisory; G0 reads, Decision Log 2 rules).** (a) The `impulse` capsule:
read the declared body and the silhouette interior on native and web, with the centre square's
glow isolated (the box's central 16 × 16 CSS px against the rest); read vitrea's capsule at
`backdropToneMax` 0 in a scratch dark patch to state what un-collapsing the dark material costs
and buys across every dark cell (the `dark-solid` capsule, which collapses in the reference too,
is the stop). If the dark reference never collapses, the collapse is a light-scheme term the dark
patch stands down with one constant; if it collapses over `dark-solid` and not over `impulse`,
the term is the appearance switch's (a scene-level input), and it is chartered, not tuned. (b) The
nested pane: the overlay's body against its base on native and web, both schemes; on the web the
overlay samples the base's rendered output through the `dom` backend, so the read says whether the
overlay's backdrop is the base's output at all (the flat mid grey suggests an unsampled or
mis-levelled proxy rather than a response-law miss), and the base's haze is read as W15's blur
against span and handed to the thick-span composite by name.

**What ships.** `@vitreajs/vitrea-web` publishes `--vitrea-shimmer` in `GLASS_CHANNEL_PROPERTIES`
and reads it in `readChannels`; react passes nothing new (no binding drives the shimmer in v1); the
light profile's rim constants move in `material.ts` with their rationale; the dark profile
document moves only if its rows move it (and `dark-profile.ts` regenerates from it, X7 of W21).

## Children

### G0: The isolation on both beds, the light rim per side, the two eye reads — spike (deliverable: findings)

- **Purpose:** (a) the gate implemented in a worktree as the design binds (channel, uniform,
  tests, the golden and e2e scenes declaring `shimmer: 1`; the renderer suite and the goldens run
  — the eight optics goldens and `highlight-press-glow` byte-identical is the attribution); (b)
  vitrea's captures on both canonical beds at both scales, GPU tier, at the gate (scratch; the
  canonical bed untouched), read per side under the declared geometry against the native
  fixtures: the per-side table before and after on every untinted cell over a solid, both schemes;
  (c) the light reference per side: the canonical light solids and W9's light probe snapshots
  through `probe-score.ts --interior declared --profile <light>`, the flatness per cell, the
  top/bottom against left/right split with its σ; the same on the dark reference from W21's probe
  (already read; tabulated beside); (d) the gate's rows that move: every `rimPeakLuminance`,
  `rimPeakDistance`, `rimFwhm`, `ssimMean`, ΔE row on both beds before and after, against its
  adopted bound and floor; (e) the two eye reads as the design states — the reader extended to
  stacks and re-validated by injection, the `impulse` capsule under both instruments with the glow
  isolated, the collapse prediction at `backdropToneMax` 0 across the dark bed, the nested pane per
  pane on both beds and both tiers; (f) `g0-findings.md` — the tables, the light rim's verdict
  (flat or lit), the constants G1 should fit and their rows, the eye findings' sizes and a
  Decision-Log-2-shaped recommendation for each (close here, or charter).
- **Acceptance:** the gate green on the renderer suite with the goldens byte-identical; the
  per-side tables on both beds; the light rim's verdict by the declared read with σ; the moved-rows
  table; the two eye reads with numbers; nothing canonical written; the findings file; the claims
  section written by the parent from it.
- **Edges:** none. **Track:** spike; one worker in a worktree; findings, not the spec. The GPU is
  shared — one capture process at a time; the calibration server's port and the capture pgrep
  clear before every run.

### G1: The form declared and dry-run — controlled

- **Purpose:** the light profile's rim constants re-fitted on their rows (or declined), the dark
  patch re-read, any eye-finding constant Decision Log 2 admits; `resolvedMaterialSha256` moved on
  any profile document that moves, with the reason; the dry run on both canonical beds at both
  scales on the GPU tier with the holdout read once (the frozen configuration), the CSS tier
  captured beside it and its captures verified byte-identical (or explained); the gate run over
  the scratch matrix (`adopted-thresholds` with `--out-matrix` — W21's lesson: a dry run that never
  runs the gate finds the coherence axis at the landing); the sheet; the declaration in claims
  before any landing capture.
- **Stops:** (S1) any untinted row worse than the W21 bed by more than 0.001 ΔE mean or 0.005
  `ssimMean`; (S2) any tinted cell moved by more than 0.002 in body; (S3) a light or dark
  calibration ΔE mean above the W21 bed's; (S4) a golden moved — the attribution failed; (S5) a
  fitted constant whose rows do not separate it; (S6) a CSS capture moved without an explanation;
  (S7) the user's eye.
- **Acceptance:** the claims section; the sheet sent; the stops dispositioned in a Decision Log.
- **Edges:** blocked-by G0. **Track:** controlled.

### G2: The landing and its referee — controlled

- **Purpose:** merge; the canonical rebuild from the main checkout (`rm results/matrix.json`
  first — the light profile's hash moves; both tiers, six profiles, `--alpha`, calibration and
  validation before the holdout); the referee — every GPU capture against the dry run byte for
  byte, every CSS capture against the W21 bed byte for byte; the gate — the rim rows and every
  floor re-read, inert floors removed with their reason, `PREDICATE_EXCLUDES` re-derived
  (expected unchanged: the native silhouettes do not move; the web silhouettes may, on the
  collapsed cells); the demo's calibration figures; the landing sheet; the user's eye; the
  changeset (a `vitrea-web` minor, 0.11.0).
- **Acceptance:** clauses 1–6 and 8 of the parent's; the chain green; the claims section.
- **Edges:** blocked-by G1. **Track:** controlled; the landing is the user's call.

### G3: The overlay's backdrop input — controlled (added by Decision Log 2)

- **Purpose:** the overlay group of a stacked scene is handed a backdrop 2.9× its base pane's
  rendered output (claims §5.94 §5: the shipped dark law at the true input gives 0.0245 against
  the reference's 0.0207; the capture is 0.0493, the law's answer at linear 0.1344). Find the
  mechanism in the sampling path — the candidate is the overlay's `css-backdrop` proxy sampling
  past the base pane through the padding W8 inflated for the outer shadow (`proxy-geometry.ts`,
  `backdrop-proxy.ts`, the proxy requests in `root.ts`, `backdrop-tone.ts`'s measurement of what
  the group is handed), read directly off the proxy's readback and the group's resolved
  `backdropTone` on the calibration page — and fix it where it lives, with a unit test on the
  mechanism. Verified WITHOUT opening a native fixture: vitrea's overlay body on its own capture
  read with `read-stack.py` against the law's answer at the base's measured output (target 0.0245
  ± 0.004 in dark at both scales; the light nested pane read the same way), and every non-stacked
  capture byte-identical on both beds (the fix must reach only groups whose proxy overlaps another
  surface's output).
- **Stops:** any non-stacked capture moved; a fix that is a constant rather than a mechanism.
- **Acceptance:** the mechanism named with its arithmetic; the fix; the test; the overlay read; the
  byte-identity of the rest; the findings file; the claims section by the parent.
- **Edges:** blocked-by G0; blocks G1 (the frozen configuration includes this fix, so the wave's
  one holdout read is spent on an overlay handed the right input). **Track:** controlled; one
  worker in a worktree; captures to scratch under the GPU rule.

## Cross-Child Contracts

- **X1 — the gate before the read.** No rim is read on vitrea's side until the band is gone; a
  reading with the band present is W21's and is not repeated.
- **X2 — the instrument.** The declared-geometry read per side is the rim definition on every
  gate; the silhouette rows are reported beside it. A stack is two bodies and eight sides.
- **X3 — the reader's recovery**, re-validated on a stack by injection, recorded beside the first
  reading.
- **X4 — the goldens byte-identical** at G0, G1 and G2: the sweep gate is attributable to the
  resting state alone.
- **X5 — the holdout once**, at G1's dry run on the frozen constants; G2 reproduces byte for byte.
- **X6 — by eye.** The sheet at W21's zoom: native | GPU before | GPU landed | CSS, both scales,
  the solids and the two eye cells, both schemes.
- **X7 — one source.** A dark patch that moves regenerates `dark-profile.ts`; the two W21 tests
  pin it.

## Ordering & Dependency Map

G0 → G3 → G1 → G2 → the 0.11.0 cut (G3 inserted by Decision Log 2). After this wave the next is the user's call (the thick-span
composite of wave Decision Log 23 (c), the eye findings' charters if Decision Log 2 sends them out,
or something else). The GPU is shared; one capture at a time.

## Risks & Mitigations

- **The light rim was fitted over the band, and the constants may not separate cleanly.** Three
  waves' rim constants absorbed a left-side band; with it gone the fit is re-run on the same
  method (W21's `fit-rim.py`) with the sides read separately, and a constant that does not
  separate is declined — the bed can be no worse on the rim than it was, because the left side's
  excess was pure error.
- **The goldens.** Only one golden captures the highlight canvas and it drives the sweep; with
  its scene declaring the shimmer running its bytes hold. If any golden moves, the gate touched
  something it should not have, and G0 stops there.
- **The eye findings pull the wave wide.** They are reads in G0 and one-constant fixes at most in
  G1; anything larger is chartered with its numbers, not built here.
- **The console lock and the shared GPU** — no native probe this wave (every reference read is
  from committed fixtures and W9's / W21's probe snapshots), so the TCC gate is not in the path.

## Deferred / Out of Scope

- **A shimmer driver.** v1 has none; this wave gives the renderer the amplitude a driver would
  output and nothing more. Post-v1 (the design's §Motion).
- **The thick-span composite** (wave Decision Log 23 (c)) — the base pane's haze in the nested
  pane belongs to it; G0 hands it the per-pane blur reading.
- **The appearance switch** (W21 Deferred) — the `impulse` capsule joins it with claims §5.94 §4's
  numbers: the glow +0.0014 / +0.0019 against +0.0000, the top rim 0.0145 / 0.0162 against 0.0030,
  no anchor below encoded 0.1104, and the `backdropToneMax` 0 table as the bound on what the
  existing axis can buy. The collapse and the appearance term are one axis (Decision Log 2 (d)).
- **The collapsed rim in light** — `dark-solid__rrect-md` under the light profile misses clause 2 on
  its bottom by 0.093 / 0.088 (the light material's rim over a dark backdrop too dim by 0.05–0.11;
  `rimAlpha`'s rows there demand 2.4–2.9). W21 deferred the same term at +0.017 in dark. In the
  tracker.
- **The CSS tier's sweep.** The CSS tier draws no shimmer and gains none here.

## Tracking Map

| child | status |
| --- | --- |
| G0 — the isolation, the light rim per side, the two eye reads | CLOSED 2026-09-08 (claims §5.94; the gate at `550f16d`, merged `eda878b`; Decision Log 2) |
| G3 — the overlay's backdrop input | DISPATCHED 2026-09-08 |
| G1 — the form declared and dry-run | — (after G3) |
| G2 — the landing and its referee | — |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-08)

(a) **Three children, one spike first.** The gate is a small renderer change but every rim
constant on the light profile was fitted over the defect, so the wave's substance is a measurement
(G0) before a fit (G1); the same shape as W21. The eye findings are reads in G0 by the user's
observation on the sheets, not a fourth child: the user asked for the sweep, and the findings are
measured on the captures the sweep's isolation produces anyway.

(b) **Binding:** the amplitude channel as the gate (the phase is a position, the pass lacked an
amplitude, and the seam is a future driver's); the declared-geometry read per side on both beds;
the goldens byte-identical as the attribution; the holdout once; the light bed no worse anywhere.

(c) **The user decides:** the landing; any re-pinned floor; the rim bounds if the margin rule
re-proposes them; whether an eye finding closes here or is chartered, on G0's numbers; the cut.
The sheets before publish, the eye's veto kept.

(d) **This is the last wave chartered on the parent's list for now**, on the user's word; after
the cut the parent recommends and the user directs.

### Decision Log 2 — G0 read: the gate lands as built, `specularGain` goes to its rows' answer, three constants declined, the `impulse` capsule chartered, the nested pane's input defect taken as G3 ahead of G1 (2026-09-08; the parent, on the user's standing instruction, the eye's veto kept before publish)

(a) **The gate is the design's and it lands as G0 built it** (`550f16d`; merged): the amplitude
channel, the goldens 29 / 29 byte-identical, the isolation exact to the left side. The
implementation is not re-litigated at G1.

(b) **`specularGain` on the light profile is fitted at G1 per contrast** — `T−B` and `L−R` over the
solid rows at both scales, never a mean pooled over sides (G0 showed the pooled mean keeps the term
because it buys one side of a pair by breaking the other). G0's reading is 0; G1 declares the fit's
answer with its rows. `rimAlpha` (light), `lightDirection` and the dark patch's `rimAlpha` are
**declined** on G0's rows (claims §5.94 §3) and do not move this wave; `lightDirection`'s shadow
rows are read beside the declaration.

(c) **The instrument's flatness is `L−R` and `T−B`.** The declared reader's horizontal-against-
vertical gap is a geometric artefact of the bands' corner coverage (binding on clause 2's reading;
per-side peaks against the reference's same side remain the clause's per-side term).

(d) **Eye finding 1 is chartered, not tuned.** The dark reference collapses over `dark-solid` and
not over `impulse`; the collapse and the appearance term are one axis pulling two ways; the dark law
has no anchor below encoded 0.1104; `backdropToneMax` 0 breaks four cells to improve two. It joins
the appearance-switch spike with §5.94 §4's table. The demo and the gate are not touched for it.

(e) **Eye finding 2 is a plumbing defect and is taken as G3, ahead of G1.** The law at the true
input lands within 0.004 of the reference; the overlay is handed 2.9× its base's output. A fix in
the sampling path is a mechanism, not a constant, and the wave's one holdout read must not be spent
on a configuration known to hand the overlay the wrong input — so G3 is inserted between G0 and G1
and G1's frozen configuration includes it. Verification without the native fixture: the overlay on
vitrea's own capture against the law's answer at the base's output. The base pane's haze goes to
the thick-span composite with G0's number.

(f) **Recorded, not this wave's:** `dark-solid__rrect-md` under the light profile (the collapsed
rim in light, bottom −0.093; `rimAlpha`'s rows there inadmissible); the `rimIntensity` entry's
superseded reason, re-recorded at G1 with the value unchanged; `--alpha` on every scratch bed; G1
captures both tiers together and runs the gate over its own matrix.

## Surprises & Discoveries

- **The light reference's rim is left-equals-right to 0.0002.** Three waves fitted a two-light rim
  whose horizontal signature was the band; with the band gone vitrea's left equals right to 0.0022
  with no constant moved, and the only lit term the reference keeps is a top-against-bottom
  +0.0002 to +0.0162 that `specularGain` 0.55 overdraws by an order of magnitude.
- **The overlay pane never saw its base.** The nested pane has been in the bed since S1 and read
  "partial" through W9, W11a and W21; the response law was right at every step and the input was
  2.9× the base's output. A flat grey lighter than its backdrop was the symptom no metric named.
- **The collapse and the appearance term are one axis.** The setting that fixes W21's two thin
  structured-backdrop capsules is the setting that breaks the four cells the collapse gets right.

- **The channel nothing drives.** `--vitrea-sweep` is read by `readChannels` and written by
  nothing in the workspace; the e2e harness and one golden set it directly. The shimmer has been a
  renderer feature with no producer since v1, and its idle value drew.
- **Two instruments, one cell, a factor of three.** The declared body and the silhouette interior
  disagree on the native `impulse` capsule (0.0066 against 0.0210) because the centre square's
  glow through the body is inside one read and dominated out of the other. W21 scored the cell
  "met (collapsed)" on the declared read alone; the eye read the glow.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-08: chartered; G0 dispatched.
- 2026-09-08: G0 CLOSED (claims §5.94); Decision Log 2 — G3 (the overlay's backdrop input) added and
  ordered ahead of G1; the Ordering map, the Tracking Map, Deferred and Surprises updated.
