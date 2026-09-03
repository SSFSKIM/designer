# W13 — The body's depth ramp, carrying the device-pixel widths (2026-09-03)

> **Parent:** W12, the lens band's structure
> (`docs/doperpowers/specs/2026-09-03-w12-lens-band-structure.md`), by way of
> its Deferred entry "the body's depth ramp, carrying the device-pixel widths"
> and its Decision Log 7 (user-decided 2026-09-03: "Hold, and open the
> depth-ramp round as the next body wave carrying the widths with it"). W12
> sits under the post-v1 wave (`2026-08-28-post-v1-wave.md`). **Consumes:**
> claims §5.50 §1–§2 (the reference's body is one blur radius in a
> quarter-device-scale buffer with an opacity ramp in depth), §5.55 (the
> kernel is one kernel in device pixels; only the sharp term's weight changes
> with scale; the lens stands at 2x), §5.56 §1 (the device-pixel widths as
> declared), §5.57–§5.58 (candidate A's fall, the corrected dry run, the
> runtime sweep: the widths are right, the band is what is left, the
> transmission has no scale term), W12's G0 instrument
> (`results/2026-09-03-w12-lens/g1/w12lib.py`) and the runtime sweep
> (`packages/calibration/scripts/sweep.ts`). **Starts from** branch
> `w12-g3-candidate-a` (`56283a1`): the widths in device pixels on both
> tiers, `devicePixelRatio` plumbed to the material on both, tier-coherence
> rows over dpr {1, 1.5, 2, 3}. Three gates in the W12 shape — an
> instrument proven on vitrea's own capture, a measurement, a declared fit
> with its referee — and the user's eye at the landing.

## Purpose

The GPU tier's body is two components mixed by one number per span: a sharp
term (σ 1.25 CSS px) and a heavy one (σ 10 CSS px), the heavy share
`sizeScatterFloor` 0.4 rising with the span to 1 at `sizeScatterSpanMax`
256. The reference's body is the same two components — a quarter-scale
buffer leaking unblurred through one blur radius — but its mix is a **ramp
in depth**: the sharp share is ≈ 0.5 at the contour and falls toward zero at
the centre (§5.50 §2's opacity inputs; §5.55 §2's amplitude by depth at both
scales), and W11c's two span constants are that ramp's projection onto one
number per span. At 1x the projection is close enough that the checkerboard
rows meet; at 2x, where the widths halve in CSS px and the sharp share
collapses sooner, W12 G3 showed what the projection costs: with the widths
read in device pixels — which put the interior's structure on the reference
at every span, §5.58 §2 — the band is left sharper than the reference's,
because a uniform share keeps the sharp term at full weight where the
reference has already faded it, and `rrect-ml` at 2x falls below its floor.
The widths cannot land without the ramp; the ramp is the reference's own
mechanism; this wave measures it through the lens, declares its form, and
lands the two together on the GPU tier, with the CSS tier's single blur
re-derived as the same law's projection.

Beside the ramp, the same instrument reads what the pitch axis has not yet
been asked: the heavy width on the small spans (the reference's radius law
floors at 4/3 buffer px — 5.3 CSS px at 1x on the capsule against vitrea's
fixed 10 — and the user's by-eye gap "the dot disappears on
`impulse__capsule-button`" is, on the numbers, a heavy term twice too wide
on a small span, not a transmission), and the kernel read directly from the
impulse cells at both scales. Those are measurements first; a span term on
the heavy width enters the declaration only if the probe asks for it.

## Parent-Level Acceptance

- The sharp share **by depth** is measured on the reference, not assumed
  from the layer tree: k(u) per depth window from the contour to the
  centre, per span and scale, on the committed 1x and 2x probes, with the
  lens's displacement in the model — and the instrument's recovery of
  vitrea's own uniform share (and of the candidate's device-pixel widths)
  from vitrea's own captures recorded beside every reference reading.
- A form k(u, span, dpr) is declared **before** the landing capture with
  the widths in device pixels, fitted jointly on both probes with `rrect-lg`
  held out at both scales, the 1x and 2x canonical rows predicted by the
  runtime sweep (never by the paper model alone), and refereed on the full
  bed under the stops below. The 2x `checkerboard__rrect-ml` / `-lg` /
  `glass-over-glass` texture rows rise above their W12-close floors; the 2x
  interior structure stays where the widths put it; no 1x row falls; and
  the band — scored where the eye looks, by the windowed rows this wave
  adds — improves on every checkerboard cell at both scales. Any row that
  still misses is re-pinned with the mechanism named.
- **By eye:** the W12 X5 sheet (native | vitrea | signed difference, 2x and
  1x, the five checkerboard spans and `photo__rrect-md`, 10× corner crops)
  at the dry run and at the landing, sent to the user's Retina display; the
  user's reading recorded in the Decision Log beside the numbers, and the
  landing is theirs to call.
- Both tiers carry the law (K5): the CSS tier's single `blur()` σ is
  re-derived as the ramp's projection and its rows are predicted and
  refereed; `tier-coherence` pins the two tiers over dpr {1, 1.5, 2, 3}.
- All package suites green, lint clean, goldens re-recorded only where the
  Decision Log names the scene and the reason; the canonical matrix rebuilt
  once at recomposition; every gap left is in claims, this Deferred list,
  or the tech-debt tracker.

## Grounding Baseline (the W12 close bed, ω 0.8, 2026-09-03)

- Body as landed: sharp σ `blurSigma` 1.25 CSS px, heavy σ × `sizeScatterGainMax`
  8 = 10 CSS px at every span and scale; k = 0.4 + 0.6 · smoothstep(`sizeSpanMin`,
  256, span) · fold, one number per span, applied uniformly over the surface
  (`optics.ts` `kScatter`; the heavy tap is the mip chain at `size.w +
  log2(8)`, not a nominal Gaussian, §5.58 §1). Lens: W12 G2's power law
  with ω 0.8. The CSS tier: one `blur()` at the mixed σ, no lens, the 1x law
  at every dpr.
- Texture-tier `ssimMean`, checkerboard (1x | 2x): `rrect-sm` 0.9988 |
  0.9978, `capsule-button` 0.9852 | 0.9836, `rrect-md` 0.9695 | 0.9517,
  `rrect-ml` 0.9482 | 0.9158, `rrect-lg` (holdout) 0.9428 | 0.9113,
  `glass-over-glass` (holdout) 0.9521 | 0.9211; `photo__rrect-md` 0.9975 |
  0.9981. The three 2x rows `-ml` / `-lg` / `glass-over-glass` are floors
  held by decision (W11 Decision Log 4, mechanism re-attributed by W12
  Decision Log 7 to the band's ramp), ratcheted to the W12 close at X2.
- Interior structure, `interiorStdDev` web / native: 2x `rrect-sm` 0.1372 /
  0.1636, `capsule` 0.1189 / 0.1552, `rrect-md` 0.0973 / 0.1272, `rrect-ml`
  0.0746 / 0.1018, `rrect-lg` 0.0525 / 0.0810 — vitrea at 65–84% of the
  reference; **1x** `rrect-sm` 0.1408 / 0.1549, `capsule` 0.1206 / 0.1424,
  `rrect-md` 0.0994 / 0.1131, `rrect-ml` 0.0769 / 0.0865, `rrect-lg` 0.0540 /
  0.0650 — 83–91%: the 1x interior is blurrier than the reference too, by
  the amount a ramp that fades the sharp term over the whole half-span
  differs from a uniform share fitted to its average.
- The candidate at `sizeScatterScaleTerm` 0 (the widths alone, §5.58 §2), 2x:
  `interiorStdDev` `rrect-md` 0.1260 (native 0.1272), `-ml` 0.1029 (0.1018),
  `-sm` 0.1647 (0.1636), `capsule` 0.1500 (0.1552); whole-crop `ssimMean`
  `rrect-md` 0.9455, `rrect-ml` **0.8998** (floor 0.9013), `rrect-sm` 0.9985,
  `capsule` 0.9855. The band carries the loss: 60% / 77% / 118% of it on md
  / ml / lg (g3 §9.5).
- Dom-tier `ssimMean` (1x | 2x): `rrect-md` 0.8963 | 0.9169, `rrect-ml`
  0.8481 | 0.8765, `rrect-lg` 0.8372 | 0.8696, `glass-over-glass` 0.8499 |
  0.8687 — eight floors held by decision (W11 Decision Log 5, the CSS
  tier's single blur).
- The reference, as measured: sharp core a 4 CSS px box at 1x (the
  quarter buffer's pixel), σ 0.5 CSS px at 2x; base σ 9 device px at 1x,
  8–10 at 2x on spans ≥ 96 (§5.55 §1); the sharp amplitude linear in depth
  over the half-span at 1x (`rrect-lg` 0.169 at u 20–28 → 0.040 at 76–80)
  and gone by mid-depth at 2x (`rrect-md` pitch 32: 0.094 → 0 over u 20 →
  48) (§5.55 §2); the layer tree's opacity ramp 0.5 at u = 1 → 1 at span/2
  on every shape, in points, the same inputs at both scales (§5.50 §2); the
  radius (span + 8)/42 buffer px floored at 4/3 — 5.3 / 9.9 / 16 CSS px at
  1x on the small spans / 96 / 160 (§5.50 §2); no transmission scale term
  (§5.58 §4); the lens within 0.9 / 1.3 px at 2x, a little long at
  mid-depth (§5.55 §4). Open: why the 1x material leaks so much more
  unblurred buffer than the 2x one — the reference's own quarter-buffer
  form needed a scale term of the same size as F1's (§5.55 §5).
- Probes: the 1x W9 probe (`results/2026-09-02-w9-probe/`, §5.31) and the 2x
  W12 probe (`results/2026-09-03-w12-lens/probe-2x/`, §5.53), 56 cells
  each, pitches 4 / 8 / 16 / 32 / 64 × spans 32 / 44 / 96 / 128 / 160, the
  three `rrect-sm` frequency-settled cells carrying a two-state spread
  that bounds any residual there before a law does.

## Design

Binding at this level, because only the whole picture settles them:

- **[binding — the ramp is measured through the lens, and the lens is not
  refit.]** k(u) is recovered per depth window with the lens's displacement
  fixed at W12 G2's landed law (ω 0.8), the instrument's model being W12
  G0's — the warp s(u) = u + D(u) along lines normal to each straight edge,
  the two-component body under it, the pixel integrated over its
  footprint — with one k per window instead of one per line set, and its
  recovery of vitrea's own uniform share from vitrea's own captures (both
  scales, `main` and the candidate's widths) recorded before any reference
  number. The lens's 0.6–1.3 px mid-depth residual at 2x (§5.55 §4) stays
  a recorded gap; a ramp fitted with the lens free would absorb it and
  neither would be measured.
- **[binding — the widths are device-pixel quantities and land with the
  ramp, not before it.]** σ_sharp = `blurSigma`/dpr and σ_heavy =
  `blurSigma`·`sizeScatterGainMax`/dpr on the GPU tier as §5.56 §1
  declared and §5.58 §2 verified; `sizeScatterScaleTerm` is retired (it was
  the projection's error, not the material's, §5.58 §2). The two land in
  one capture under one referee: the widths alone trip the `rrect-ml` 2x
  floor and the ramp alone has no 2x interior to act on.
- **[binding — a measured ramp, then a form; the runtime is the fitting
  instrument.]** The form of k(u, span, dpr) is chosen on the measured
  windows (the layer tree's linear ramp to zero at the centre is one
  candidate, a ramp with a floor is another, a scale term on the start or
  the reach a third), fitted on both probes with `rrect-lg` held out, and
  then swept **in the renderer** (`sweep.ts`, both scales, the calibration
  cells, the interior objective and the windowed band rows) before the
  landing capture: the paper model over-credited the mip chain's heavy tap
  by a factor that turned a right answer into a wrong constant (§5.58 §1),
  and no constant lands on a paper prediction again.
- **[binding — the span law is the ramp's projection, on both tiers.]**
  `sizeScatterFloor` and `sizeScatterSpanMax` are retired as fitted
  constants once the ramp lands: the heavy share a surface of a given span
  carries on average is the ramp integrated over the surface's area
  (closed form on the rounded rect: depth u has perimeter P − 8u of area,
  corners aside), and that integral is what the CSS tier's single `blur()`
  σ is derived from through the shared `sizeScatterSigmaAt` (K5). One law,
  two projections: per pixel on the GPU tier, per surface on the CSS tier.
  Whether the CSS tier's σ then follows dpr is Decision Log 1's question 2.

Advisory, carried into the children:

- The ramp's likely shape from the two readings in hand: sharp share s(u) =
  s₀(dpr) · max(0, 1 − u / (ρ(dpr) · span/2)), s₀ ≈ 0.5 at both scales, ρ 1
  at 1x and < 1 at 2x (§5.55 §2's "starts lower and reaches zero sooner");
  whether s₀ or ρ carries the scale, or the 1x ramp floors above zero
  (§5.55 §1's deep-interior core share 0.31–0.50 at 1x against 0.0–0.1 at
  2x is either the ramp seen through a window that stops short of the
  centre, or a floor), is what G0's windows decide. The open mechanism
  question of §5.55 §5 is the same question from the other side.
- The shader already has u per pixel: the field pass's SDF depth is what
  the lens's `lensT` is evaluated from, so k(u) is one expression beside
  `kScatter` in the optics pass — no new pass, no new texture. The
  `sizeScatterFloor`-fold semantics (the floor is the material's frost and
  is not folded; the rise is depth and is) carry over: the ramp's centre
  value is the frost, its edge excursion is folded.
- The heavy width on the small spans: §5.55 §1 fitted spans ≥ 96 only; the
  reference's radius law predicts 5.3 CSS px at 1x on `rrect-sm` /
  `capsule` against vitrea's 10. Read it on the probe's small spans and on
  the impulse cells (the kernel directly, both scales, light and dark
  grounds — the canonical `impulse__capsule-button` and the probe's impulse
  backdrops if any); if it holds, the declaration carries a span term on
  σ_heavy (one constant, the radius law's own form) and the user's dot gap
  closes with it. If the small spans read σ 9–10 device px as the large
  ones did, the dot gap stays a transmission question for its own wave.
- The band-windowed rows (`ssimBand`, `ssimInterior`, `ssimOutside`; X6):
  SSIM over the cell's silhouette split at a fixed depth from the contour
  (24 CSS px, past where D(u) reaches zero on every span, §5.49 §2), and
  over the exterior within the same depth, recorded on every cell from G0
  on (landed 2026-09-03, claims §5.60), adopted as bounds at G2's landing
  from the bed. This is W12's Deferred "by-eye-aligned band metric" in its
  first form; the corner crops stay by eye.
- The CSS tier cannot carry a depth ramp with one `backdrop-filter`; a
  two-layer body with an inset mask could (the two-layer CSS body, W11
  Decision Log 5, extended by a mask gradient on the sharp layer). Out of
  scope here; the CSS tier's rows in this wave move only through the
  projection.

## Children

### G0: The instrument and the measurement — spike (deliverable: findings)

- **Purpose:** extend W12 G0's instrument (`w12lib.py`) to one k per depth
  window (u bins of 4 CSS px from the contour to the centre, the lens fixed
  at the landed law), validate it on vitrea's own captures at both scales
  — `main` (uniform k per span, known: 0.4 + 0.6 · smoothstep(`sizeSpanMin`,
  256, span)) and the candidate at term 0 (the widths in device pixels) —
  then read the reference: k(u) per window, per span and scale, on both
  probes over pitches 8 / 16 / 32 / 64; the heavy σ on the small spans;
  the impulse kernels at both scales. Record the band-windowed SSIM rows
  on the W12 close bed as the baseline (X6).
- **Acceptance:** the instrument recovers vitrea's uniform k within ±0.05
  in every window over 4 ≤ u ≤ span/2 − 4 at 1x and 2x on `rrect-md` and
  `rrect-lg`, and the candidate's widths within the same; the reference
  tables carry that recovery beside them (X4); findings in
  `results/2026-09-03-w13-ramp/g0/`, claims section written.
- **Edges:** none. **Track:** spike; one worker, findings not the spec.

### G1: The declared form and its dry run — controlled

- **Purpose:** the form k(u, span, dpr) chosen on G0's windows, the widths
  in device pixels, the span law as the ramp's projection on both tiers,
  the heavy width's span term if G0 asked for it; fitted jointly on both
  probes with `rrect-lg` held out at both scales; then the runtime sweep on
  the calibration cells at both scales over the form's constants, and the
  1x and 2x canonical rows predicted from the sweep; the CSS tier's σ per
  span and scale predicted from the projection; the X5 sheet at the dry
  run.
- **Acceptance:** the declaration in claims — form, constants, the stops
  below, the twelve rows' predictions, both tiers — before any landing
  capture; the sheet sent; the user's reading recorded.
- **Edges:** blocked-by G0. **Track:** controlled.

### G2: The landing and its referee — controlled

- **Purpose:** implement on both tiers from the candidate branch (retire
  `sizeScatterScaleTerm`, `sizeScatterFloor`, `sizeScatterSpanMax`; add
  the ramp's constants; the CSS projection; `tier-coherence` over dpr;
  goldens behind the isolation proof), capture the twelve runs to a scratch
  matrix, referee under the stops, the X5 sheet at the landing, the user's
  eye.
- **Stops (declared here, refined by G1 with numbers):** (S1) no 1x row
  below its W12-close value by more than 0.002; (S2) the three held 2x
  texture rows rise above their W12-close floors; (S3) `interiorStdDev` at
  2x within 0.005 of the reference on the five checkerboard spans (the
  widths' gain kept); (S4) `ssimBand` rises on every checkerboard cell at
  both scales, read with `ssimInterior` beside it; (S5) the solids, `photo`
  and the tinted cells move by no more than 0.001 in any adopted metric,
  and `ssimOutside` by no more than 0.001 on every cell (the ramp does not
  touch the outside of the contour); (S6) the CSS tier moves only as G1
  predicted; (S7) a hard stop is a landing the user's eye rejects. S2 is
  the stop, not the 0.93 bound: 69–76% of the three 2x rows' deficit sits
  outside the silhouette (Surprises), and with the inside deficit removed
  entirely they would read ≈ 0.939 / 0.938 / 0.940 — meeting 0.93 belongs
  to the outer shadow's wave.
- **Edges:** blocked-by G1. **Track:** controlled; the landing is the
  user's call (Decision Log).

## Cross-Child Contracts

- **X1 — the canonical rebuild.** As W12 X1: children referee on partial
  runs to a scratch matrix; `rm results/matrix.json` and the twelve runs
  once at recomposition; the demo's reference-panel fixture re-copied.
  Owner: parent.
- **X2 — floor bookkeeping.** As W11/W12 X2. Owner: parent.
- **X3 — the untouched bed.** The whole-bed scan against the W12 close
  matrix; every cell moved by more than 0.005 is named. Owner: parent.
- **X4 — the instrument's validation travels with every reading.** A
  reference k(u) table is never quoted without the recovery of vitrea's
  own share from the same instrument on the same cell geometry beside it.
  Owner: G0; G1 binds.
- **X5 — the by-eye sheet.** W12's script and layout
  (`results/2026-09-03-w12-lens/sheets/`), at G1's dry run and G2's
  landing, under `results/2026-09-03-w13-ramp/sheets/`. Owner: parent.
- **X6 — the band-windowed rows.** `ssimBand`, `ssimInterior` and
  `ssimOutside` on the perceptual axis of every cell — the SSIM map's mean
  over windows centred inside the native silhouette within 24 CSS px of
  the contour, deeper than 24 CSS px, and outside the silhouette within
  24 CSS px (added 2026-09-03 from the baseline's first reading, Surprises;
  the three plus the far field partition the crop) — recorded by the
  compare from G0 on (schema addition, no bound until G2), their baseline
  the W12 close bed, adopted as bounds at G2's landing. Owner: G0 defines,
  parent adopts.

## Ordering & Dependency Map

G0 → G1 → G2 → recomposition. The candidate branch is rebased onto the W12
close before G2 implements; nothing on it lands before G2's referee.

## Risks & Mitigations

- **The 1x mechanism is not the layer tree's ramp** (§5.55 §5's open
  question; the 1x deep interior keeps a sharp core the 2x one has lost).
  Mitigation: the form is chosen on G0's measured windows, and a ramp with
  a floor is a declared candidate; if the two scales need different ramp
  shapes rather than one ramp with a scale term, that is the finding and
  the declaration says so.
- **The ramp couples with the lens in the band.** Mitigation: the lens is
  fixed (binding); the residual the lens leaves is recorded, not absorbed.
- **The 1x rows fall** because the uniform k was fitted to the 1x bed as a
  whole. Mitigation: S1 with the sweep at 1x before the landing capture;
  the 1x interior is blurrier than the reference today (baseline), so the
  ramp has room to improve 1x, not only 2x.
- **The mip chain's heavy tap** is not a Gaussian and its footprint at a
  given level is what the sweep sees. Mitigation: the renderer is the
  fitting instrument (binding).
- **The virtual 2x display.** §5.50 exonerated it for the blur; the ramp's
  2x reading rides on the same bed. Mitigation: recorded; a real Retina
  capture remains user-held and would be read once as a check.
- **The 2x rows' bound is outside this wave's reach.** The outer shadow's
  lift owns most of their deficit (Surprises); a landing that clears every
  inside stop still misses 0.93. Mitigation: S2 as written; the floors
  ratchet; the shadow's wave carries the bound.
- **Retiring two profile constants** touches every consumer of the span
  law (the proxy padding's 3σ rule, `tier-coherence`, the readouts).
  Mitigation: the projection keeps `scatterThickness(span)` as the
  function every consumer calls, with the ramp's integral as its body.

## Deferred / Out of Scope

- **The 2x deep value — its own charter** (Decision Log 4; claims §5.64 §4).
  At 2x the reference's sharp share at the contour is heavier than vitrea's
  deep interior on every cell, so the gap is in the span law and not in any
  ramp above it. Fitting G0's 2x contour readings as a deep curve returns
  floor 0.530, knee 112 and a **ceiling 0.840** (RMS 0.0148; four times worse
  with the ceiling pinned at 1), against the code's 0.400 / 256 / 1. Three
  scale terms, one of them a saturation constant the material has no name
  for, on the oldest span law in the profile — it needs its own declaration,
  its own referee and its own frozen bed. **Ordering (user, 2026-09-03):**
  chartered *after* the demo hero-ground decision and the coverage openers on
  the backlog, not immediately after W13 and W14 land. **Two terms added at
  the landing (Decision Log 8; claims §5.68 §7):** the body's widths at 2x —
  candidate A's device-pixel widths withdrawn as a landing candidate, the
  small spans' +0.024 forgone, to be re-asked with the deep value rather than
  alone — and the stacked scene's proxy padding, which at 2x derives from the
  1x ramp's projection (Decision Log 5's `CSS_TIER_RAMP_SCALE`) while the GPU
  tier draws the bed's span law there (Surprises).

- **The outer shadow's colour and span law — the next wave candidate,
  from X6's baseline (2026-09-03; Surprises).** The reference's shadow is
  a gray composited at low alpha that lifts the blacks (+0.04 at the
  contour on the checkerboard, decaying to 0 by 24 CSS px, strongest below
  the surface where the (0, 8) offset puts it) and darkens the whites less
  than vitrea's black multiply does; on `light-solid__capsule-button` it is
  2.4× lighter than vitrea's in integrated darkening at both scales (−0.040
  against −0.094 luma at the contour) — the user's by-eye "the shadow is
  darker" measured. It owns 52–67% of the GPU tier's whole-crop SSIM
  deficit on the four large checkerboard cells at 1x and 69–76% at 2x,
  through SSIM's luminance term on the black squares. Shape of the work:
  measure the shadow's composite colour and alpha by distance and side on
  the solids, the checkerboard and `photo` at both scales against §5.50's
  block (offset (0, 8), amount min(0.625·span, 75), height 0.4·span,
  opacity 0.5 − (span − 48)/448, blur 40 from span 72, saturation 1.8,
  vibrancy (span − 64)/96) and W8's fitted σ and reach; declare a composite
  colour with its alpha and span law in the shadow pass in place of the
  multiply, both tiers; `ssimOutside` and the solids' level rows as the
  instrument; the three 2x texture rows' 0.93 bound as the target it can
  reach and W13 cannot. **Chartered as W14 (Decision Log 2, 2026-09-03).**
- The CSS tier's depth ramp through a two-layer body with an inset mask —
  the two-layer CSS body charter (W11 Decision Log 5) extended; measured
  feasibility is a spike of its own.
- The lens's 2x mid-depth residual (0.6–1.3 px, §5.55 §4) — recorded, not
  refit here.
- The thin-material scale-dependent level on text and high-contrast
  backdrops (§5.55 §3) — a level question, its own wave.
- The user's other by-eye gaps from W12's Deferred: the whole-surface dome
  unchanged; the shadow's span law is W14; the dot gap measured by G0 and
  returned to W12's Deferred as the dark-ground transmission item (the
  thin material's dark-regime response closes the surface entirely over a
  near-black backdrop; the reference passes ≈ 0.025 — a W9 follow-up, one
  anchor of the response curve).
- The bleed term, the two-light rim, continuous corners, the tint's colour
  matrix, the pressed state — W12's Deferred, unchanged.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | two workers, 2026-09-03: the windowed instrument, its validation and the reference readings (`results/2026-09-03-w13-ramp/g0/g0-instrument.md`, `g0-ramp.md`; claims §5.61) — the ramp is real, H1 is not its law, the reach reads as a length, the 2x floor is bounded not measured, no span term on σ_heavy, the dot is not the body; X6's band rows landed and baselined (claims §5.60; `x6-baseline.md`; 243 tests) | COMPLETE 2026-09-03 (the transmission-by-depth addendum: flat on all six cells, §5.61 §7) |
| G1 | four forms of the ramp, each fitted in the renderer on branch `w13-g1-ramp` (worktree `.claude/worktrees/w13-g1`): the first (a start and a reach; `eb12219`) refuted at 81 points, span-flat where the bed is span-graded (claims §5.63, `results/2026-09-03-w13-ramp/g1/sweep/`); the second (the retired span law restored underneath; `2752301`, with the first review's two findings) refuted at 68 points, one start unable to sit above the deep value on thin and thick cells at once, and at 2x the inert configuration the best on every cell (§5.64, `sweep-2/`); the third (the start graded by `sizeThickness`; `f77b5f1` + `ef61b09`) reaching S4 on every 1x calibration cell with the 2x null bit-exact, and failing one holdout row because the start cannot fall past the thickness knee (§5.67, `sweep-3/`); **the fourth** (the start's own decline along the scatter facet's curve, one constant; `7de3d76` + `762c290` + `51c232d`, with the third review's five findings and main merged with W14 landed) **reaching S1 and S4 at 1x on every row holdout included** — `rrect-lg` +0.0056 / band +0.0136 on the W14 bed, its interior 12% over Apple's from 33% — the far start carried from G0's reading (Decision Log 7), the 2x null re-verified at zero over 20 cells × 774 measurements (`sweep-4/`, `12e2e2b`); the sheets sent with the parent's reading (`sheets/`, `9b1d5f2`); **the CSS tier's confirmation** found the candidate's device-pixel width division still in that tier and four dom floors broken at 2x — removed (`d0d778f`; Decision Log 5 executed in full), re-captured clean with every floor holding; the fourth form's review (Codex) — three code findings fixed (`8f00c0c`), the spec finding amended in Decision Log 5; **DECLARED** — claims §5.68 (form, constants, stops with numbers on the W14 bed, the twelve rows, both tiers; fingerprints light `2b8cfda6950bc697` / dark `aa6e466b1412ec04`) | COMPLETE 2026-09-03 |
| G2 | the landing plan in claims §5.68 §6; **the user's call between (a) the branch as declared (the 1x ramp plus the 2x device-pixel widths: four large 2x rows down 0.006–0.017, two small ones up) and (b) the 1x ramp with the GPU tier's 2x widths restored to the bed's** — the parent recommends (b) | IN PROGRESS 2026-09-04 — (b) decided (Decision Log 8); executed on the branch (`40f409c`, review fixes `beb823f`); the dry run verified against both predictions (claims §5.68 §7); landing |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-03)

**The cut.** Three children in W12's shape — instrument and measurement,
declaration and dry run, landing and referee — because the three have
different verification strategies (a recovery on a known field; a
prediction against a bed; a referee under stops) and the first two produce
findings the third must not pre-empt. Rejected: one controlled round from
the candidate branch (the ramp's form is not known well enough to declare
from §5.55 §2's windows, which start at u 20 and do not see the band); a
decision round on the CSS tier as a fourth child (it is one question, below).

**Binding rules.** The four in Design: the ramp measured through a fixed
lens; the widths land with the ramp; a measured ramp, then a form, fitted
in the renderer; the span law is the ramp's projection on both tiers.

**Beyond the user's words, for their eye:** the heavy width on the small
spans and the impulse kernels are added to G0's measurement (not to the
declaration) because the same instrument on the same probes reads them,
and because the user's dot gap looks, on §5.50 §2's radius law, like this
term. It costs G0 one more table.

**What the user decides at this gate** (each with the recommendation):

1. *Approve the cut and the binding rules; G0 starts.* Recommended; G0 is
   measurement only and lands nothing.
2. *The CSS tier at device scale.* (a) The CSS tier keeps the 1x law at
   every dpr: its `blur()` σ is the ramp's projection at dpr 1, the 2x dom
   rows stay held by decision with the claim narrowed to "the CSS tier
   renders the 1x material", and the CSS tier's own 2x form — whose best
   single σ is *larger* in CSS px at 2x, the opposite of the device-pixel
   widths (§5.55 §5) — goes to the two-layer CSS body wave. (b) Carry the
   device-pixel widths on the CSS tier through the candidate's
   `observeDevicePixelRatio` plumbing. **Recommended: (a)** — (b) moves the
   2x dom rows the way the measurement says is wrong, and (a) is honest
   about what the tier is.
3. *The band split at 24 CSS px* for the windowed rows (X6), fixed rather
   than per span. Recommended as written: one number the eye can check on
   the sheet; per-span splits would move with the lens depth and hide a
   lens change inside a metric change.

Held for the user beyond this gate: the by-eye reading at G1's dry run and
the landing call at G2.

### Decision Log 2 — the outer shadow's wave chartered beside this one (2026-09-03; user-decided)

**Evidence.** Surprises (X6's baseline): the exterior owns 52–67% of the
GPU tier's whole-crop deficit on the four large checkerboard cells at 1x
and 69–76% at 2x, through the reference's shadow lifting the blacks; the
light-solid capsule's shadow at 2.4× the reference's; claims §5.60.

**Decided (user, 2026-09-03):** "charter the outer shadow's wave next, and
run its measurement in parallel with W13." W14
(`2026-09-03-w14-outer-shadow-colour.md`) is chartered from this wave's
Deferred entry, its G0 dispatched at the charter; the two waves share the
X6 rows (`ssimOutside` is W14's primary row and W13's null) and coordinate
their landings under W14's X8 — each referees on `main` as it stands, the
second to land re-runs its dry run on the first's bed. Nothing in this
wave's cut or stops changes; S2 stays the stop and 0.93 is W14's.

### Decision Log 3 — the form re-declared: the retired span law underneath the ramp (2026-09-03; the parent, within G1's remit)

**The finding.** The first form's sweep (claims §5.63) cannot meet S2, S3 or S4
at any of 81 points at either scale, and the reason is the form: a start and a
reach project onto a span law of 0.43–0.56 where the retired law ran
0.41–1.00, so the small spans want a high start and the large ones a low one,
and no pair serves both. At 2x it also spends the interior §5.58 §2's widths
won. G0's measurement of the ramp stands; the family cannot carry it.

**Decided.** The form is one of the three the Design listed — *a ramp with a
floor* — with the floor being the retired size law itself: the deep value is
`kDeep(span) = sizeScatterFloor + (1 − sizeScatterFloor) · smoothstep(sizeSpanMin,
sizeScatterSpanMax, span)` (restored; `sizeScatterSpanMax` returns to the
profiles), and the ramp is the near-contour excursion `s(u) = sDeep + max(0, s₀ −
sDeep) · max(0, 1 − u/reach)` on both tiers, the CSS tier reading its area mean.
Four provisional constants stay (start per scale, reach per scale in device
px), set by a second sweep in the renderer with `rrect-lg` held out; the
declaration's twelve rows are predicted from that sweep.

**Rejected.** A fifth constant as a span-flat floor (fails for the first form's
reason: the bed's span dependence is the thing a flat number cannot carry).
Declaring the first form as-is at its best point (0.60 / 0.55 / 200 / 200): it
meets S1 at three points and nothing else, and the holdout rows fall below two
ratcheted floors. Re-pinning those floors is the user's decision and is not
asked; the fix is the form.

**What this does not settle.** Whether the excursion's start wants to grade
with span as well (G0 read the thin surfaces' start above the thick ones');
the second sweep's tables at each span will say. Whether the ramp's band gain
is visible to `ssimBand` at all when the span law is held — the first sweep
saw the small spans improve, which says yes for the thin regime.

### Decision Log 4 — the start grades with span; the 2x half of the wave becomes a null and its own charter (2026-09-03; the parent, within G1's remit)

**The finding** (claims §5.64). The second form fails at 1x because one start
per scale cannot sit above the deep value on both the thin cells (0.600) and
the thick ones (0.236): any start the smallest cell needs is above the start
the largest cell can tolerate, measured, by 0.017. At 2x it fails completely —
the configuration where the ramp does nothing scores the best band on all five
calibration cells and carries §5.58 §2's interior unchanged. G0 explains both:
the excursion the reference implies is positive on every cell at 1x and
**negative on every cell at 2x**.

**Decided.** The start becomes graded by the material's existing thin/thick
curve, `s₀(span) = startThin + (startThick − startThin) · sizeThickness(span)`
— the knee at 64 the tone response and the outer shadow already blend across,
so the form introduces no new span statistic. Six constants (thin and thick
start per scale, reach per scale in device px), all provisional until the third
sweep. The 1x thick start is 0.52, G0's own `rrect-md` reading, rather than the
0.47 the paper section pinned: 0.47 sits 0.011 below that cell's deep value and
would leave it inert.

**S4 is refined by scale, which G1 is chartered to do.** At 1x it stands: the
band rises on every checkerboard cell. At 2x it is replaced by a **null** —
every 2x row unchanged from the branch's pre-ramp state, which is what the form
predicts when every 2x start sits below its cell's deep value, and which the
sweep must *verify by capture* rather than assume. If any 2x row moves, the
form is wrong about the clamp. S2 and S3 at 2x are then met exactly as the
device-pixel widths already meet them.

**What this hands on.** The 2x gap is a deep-value gap and this wave does not
close it. Fitting G0's 2x contour readings as a deep curve wants floor 0.530,
knee 112 and a ceiling of 0.840 (RMS 0.0148, against 0.0612 with the ceiling
pinned at 1) — three changes to the span law, one of them a constant the
material has no name for. That is a charter of its own and is in Deferred.

**Rejected.** Landing the second form at its best point (S4 met nowhere).
Special-casing the ramp off at 2x (the law already evaluates to no excursion
there; a flag would hide the reading that says why). Refitting the deep value
inside this wave (it moves the material's oldest span law under a bed frozen
for the ramp, and it deserves its own declaration and referee).

### Decision Log 5 — the CSS tier keeps the 1x law for the ramp's mix (2026-09-03; user-decided)

**Decided (user, 2026-09-03),** answering Decision Log 1's question 2: *"keep
the one-times law. The measurement says this tier's own best single blur radius
is larger in CSS pixels at two-times, not smaller, so following the device-pixel
projection would move its rows in the direction the measurement calls wrong. Its
two-times rows then stay held by decision rather than fitted."*

The user also recorded the implementer's narrower reading of the same answer, as
what the branch then did: it kept the candidate's device-pixel width
division and fixed only the ramp's mix at scale one. **Overturned by
measurement (2026-09-03, claims §5.68 §3 S6):** the fourth form's dry run on
the W14 bed captured the CSS tier with that division still in it and read
`rrect-lg` 2x `ssimMean` −0.047, the interior's standard deviation from
0.026 to 0.143 against Apple's 0.081, and four of the dom tier's regression
floors broken — the direction §5.55 §5 predicted, on the rows this decision
holds. The decision is now executed in full: the CSS tier has no device-scale
input (branch `d0d778f`), its width and its mix are both read at
`CSS_TIER_RAMP_SCALE`, the group proxy's blur is taken at the same scale so
its padding matches what the tier writes, and the e2e helper derives its
expectation the same way (`8f00c0c`). Re-captured on a clean build, every dom
floor holds and the tier's rows rise or hold on every checkerboard cell at
both scales.

**What this binds.** The CSS tier's 2x rows are held by decision, not fitted, for
the ramp's mix — so a later reading that moves them is not a regression against
this wave. Any future work that makes the CSS tier follow the device scale has to
overturn the measurement (§5.55 §5) first, not just the constant.

### Decision Log 6 — the fourth form: the start keeps falling past the thickness knee (2026-09-03; the parent, within G1's remit)

**The finding** (claims §5.67 §4). The third form reaches the 1x band on every
calibration cell and lands `glass-over-glass` at the best interior agreement
on the bed, and fails one holdout row: `rrect-lg` at 1x, `ssimMean` −0.0026
against S1's 0.002, its interior from 17% under to 33% over. The cause is the
form's own arithmetic — `sizeThickness` saturates at 96, so every thick span
gets the same start while G0 read the reference's start falling 0.512 → 0.501
→ 0.410 across 96 → 160, and the deep value's own decline to 256 makes the
excursion grow with span where the reference's shrinks.

**Decided.** The start gets a slow decline along the scatter facet's own curve
above the thickness knee: `s₀(span) = startThin + (startThick − startThin) ·
sizeThickness(span) + (startFar − startThick) · smoothstep(sizeSpanMax,
sizeScatterSpanMax, span)`. One more constant per scale, `startFar` (the
start at span ≥ 256); no new span statistic; both curves already in the
material. The 1x thin / thick / reach hold at 0.72 / 0.52 / 80 and `startFar`
is swept alone on the thick calibration cells. At 2x the null holds for any
`startFar` at or below the thick anchor; carried at G0's `rrect-lg` reading.

**Where it runs.** On the W14 bed, after W14 lands — the re-run X8 requires of
the second lander anyway — so the fourth form's fit, its confirmation and the
X8 re-read (S2 at 2x against the new bed, where the three rows carry 0.04 of
margin) are one GPU block and one holdout read.

**Rejected.** Landing the third form with the overshoot and re-pinning
`rrect-lg`'s floor by decision: the cause is one term and the fix is one
constant. Refitting thin / thick / reach jointly with `startFar`: the 1x
optimum is interior on both refined axes and `startFar` acts only above 96.

**Not settled here.** The thin anchor sits 0.08 above G0's read-off, and the
runtime's reach at 80 device px against G0's 100–110; whether the runtime's
preference or the reference's contour reading better estimates the reference
is a question for the instrument, recorded in Surprises.

### Decision Log 7 — the far start is set by the reference's reading, inside the calibration noise (2026-09-03; the parent, within G1's remit)

**The limit.** `startFar` acts through `smoothstep(96, 256, span)`, which is
0 at `rrect-md` (96) and 0.10 at `rrect-ml` (128): on the calibration cells
the constant is nearly inert, and the two cells that feel it — `glass-over-
glass` (130) and `rrect-lg` (160) — are holdout. The 1x grid over 0.15…0.52
confirms it: only `rrect-ml` moves, monotonically better as `far` falls
(band +0.0042 → +0.0060), and it is flat within 0.0004 below 0.30. A runtime-
only pick would run to the grid's floor with nothing to stop it.

**Decided.** `sizeScatterRampStartFar1x` = **0.20** — inside the measured
range, within noise of the best point, and G0's own `rrect-lg` start (0.410
at span 160, §5.61 §1) re-expressed through the form (0.207). At 2x 0.15,
below the thick anchor, so the null holds by construction. Declared as
*carried from the measurement*, the way W14 carried its span-160 anchor,
and read once on holdout at the confirmation: `rrect-lg` 1x `ssimMean`
0.9743 (+0.0056 on the W14 bed), band +0.0136, interior 12% over Apple's
from the third form's 33%.

### Decision Log 8 — the landing: the ramp alone, the 2x widths restored to the bed's (2026-09-04; user-decided)

**Decided (user, 2026-09-04):** *"yes the second it is."* Of the two landings
claims §5.68 §5 put to the user, the second: the 1x ramp lands, and the GPU
tier's body widths return to CSS pixels at every device scale, as the W14 bed
has them — candidate A's device-pixel widths (W12 G3, held by W12 Decision
Log 7 and carried into this wave) are **withdrawn as a landing candidate**.
Every 2x row is then predicted byte-identical to the W14 bed (the ramp is a
verified null there and the widths were the only other change), the small
spans' 2x gain (band +0.024 on `rrect-sm` and the capsule) is forgone, and
the whole 2x question goes to the deep-value charter in Deferred with the
widths as one of its terms. The reach stays a length in device px as
declared; at 2x it has nothing to act on.

**What the landing does.** The widths' division removed on the branch with
its tests and the material's doc comment amended (the measurement that
retires it: §5.64 §4 — Apple's 2x interior is heavier than ours, and a
narrower width pushes the large spans the wrong way — and the sheets); a
dry run of the new configuration on the GPU tier at both scales, holdout
read once, predicting the 1x rows unchanged from sweep-4's confirmation and
the 2x rows identical to the bed; then G2's landing plan (claims §5.68 §6).

**Executed (2026-09-04).** `40f409c` on the branch; the branch as it lands
reviewed and its three findings fixed in `beb823f` (the CSS mirror's defaulted
ratio argument, the far anchors' barrel export, two retired records corrected
beside their text). The dry run read against both predictions by
`results/2026-09-03-w13-ramp/g2/g2-verify.py`: the 1x rows sweep-4's to four
decimals, 46 of 49 2x captures byte-identical to the bed and every 2x row the
bed's; the three stacked cells shift by a code across the overlay, attributed
to the proxy's padding following the ramp's projection (claims §5.68 §7;
Surprises; a term of the 2x charter in Deferred). Landing under G2.

## Surprises & Discoveries

- **The whole-crop SSIM deficit on the large checkerboard cells sits mostly
  outside the silhouette, and it is the outer shadow's colour (2026-09-03,
  X6's baseline).** Split by window class on the W12 close bed, GPU tier:
  the exterior carries 60% / 64% / 52% / 67% of `rrect-md` / `-ml` / `-lg`
  / `glass-over-glass` at 1x and 71% / 74% / 69% / 76% at 2x; the band
  35% / 28% / 31% / 26% and 22% / 16% / 20% / 17%; the interior 5% / 8% /
  17% / 7% and 7% / 11% / 11% / 7%. Profiled by distance on `rrect-lg` the
  loss sits 3–24 CSS px outside the contour (SSIM 0.73–0.87 there, 1.000
  beyond 48 px) and it is SSIM's **luminance term on the flat black
  squares** (l 0.69–0.72 with c and s ≥ 0.998; the windows on checker
  edges read 0.99): the reference's shadow lifts the blacks — 0.041 below
  the surface, 0.027 at the sides, 0.015 above, ring 2–12 px — where
  vitrea's leaves them at 0.000, and darkens the whites less (0.913
  against 0.922). Per ring the reference is a·plate + c with c +0.039 →
  +0.004 from the contour to 24 px out (a 0.887 → 0.988); vitrea is
  a·plate with c 0 (a 0.933 → 0.993): a gray composited at low alpha
  against a black multiply. Not a blurred backdrop copy (a blur term adds
  nothing to the affine fit) and not a displacement (the checker lines
  outside the contour sit within 0.02 px of the plate at 2x on both sides,
  0.3–0.5 on both at 1x — the plate's half-pixel convention). On
  `light-solid__capsule-button` the same shadow reads −0.040 luma at the
  contour on the reference against −0.094 on vitrea, 2.4× in integrated
  darkening, identical at 1x and 2x: the user's by-eye gap from W12's
  Deferred, measured. Consequences: X6 gains `ssimOutside`; S5 gains it as
  a null; S2 is the wave's stop and 0.93 is the shadow wave's (Risks,
  Deferred).
- **The layer tree's ramp is not the pixel law, and the reach is a length
  (2026-09-03, G0; claims §5.61 §2).** The sharp share does ramp — by
  0.10–0.26 at 1x and 0.12–0.39 at 2x across the readable depths, against
  an instrument flat-field noise of 0.012–0.046 — but §5.50 §2's "0.5 at
  the edge → 0 at the centre" (H1) fits one cell per scale and misses the
  rest by 0.17–0.37; a free ramp (H2) fits every span to 0.003–0.099. The
  per-span reaches in absolute depth (108 / 115 / 144 CSS px at 1x on lg /
  ml / md; 39 / 41 / 59 at 2x) spread by 1.3× where the relative ones
  spread by 2.2×: the reach is a length, and between the scales it halves
  in CSS px — one length in device pixels (≈ 100–110) fits the two beds
  where one in CSS px does not — while the start falls from ≈ 0.6 to ≈ 0.35
  (the peak windows) and the thin spans keep a higher start (0.64 / 0.44)
  with the same slope. The 2x floor is **bounded** to 0.00–0.03, not
  measured, because the 2x base width on the large spans is open (σ 9 / 11
  / 16 device px by three estimators) and sits under it. G1 declares the
  form as a device-pixel reach with a start by scale, fitted in the
  renderer, and treats the 2x floor as 0.
- **Only one pitch on vitrea's bed: the share's level is not identifiable
  there** (G0; §5.61 §1). At a single spatial frequency the transmission
  and a uniform shift of the share trade off (0.26–0.37 of error on a
  synthetic known law at one pitch, 0.003 at three); the instrument's
  recovery of vitrea's law is exact on the ramp's *shape* (the property
  the wave turns on) and off by 0.07–0.12 on its level on three spans.
  Every reference reading pools three pitches. The validation is met on
  the shape and reported as not met on the level, with the mechanism.
- **The dot gap is not the body** (G0; §5.61 §4). Under
  `impulse__capsule-button` vitrea's interior has standard deviation
  exactly 0.00000 at the plate's own global mean, at four profiles, where
  the reference keeps a dot of 0.0066 (1x) / 0.0266 (2x) above its
  surround; the cell's resolved state reads `gpu-texture`, `exact`, `ok`,
  so the group sampled and the material's dark-regime response (W9's dark
  anchor) closed the thin surface over a near-black backdrop entirely,
  where the reference passes ≈ 0.025 of the structure. Not the mix, not
  the widths (σ_heavy reads 7–12 device px on the small spans; no span
  term is asked for). It leaves this wave and returns to W12's Deferred as
  the dark-ground transmission item with this description.
- **One CSS capture on this machine is not frame-stable.**
  `light-solid__capsule-button__rest` at 1x on the CSS tier read
  `deterministic: false` with `repeatNoise` 1.17 × 10⁻⁵ in X6's scratch
  run and differed by one pixel, one code value, from the G2 bed in W12's
  X1 (claims §5.59 §1) — the same cell both times; the re-run for
  `ssimOutside` flagged it again and a second one,
  `photo__capsule-button__rest-tint-orange-half` (3.91 × 10⁻⁶), so the
  frame noise moves between cells from run to run (claims §5.60 §1).
  Below every bound by four orders; recorded, not chased.

- **The candidate's CSS width division cost four dom floors at 2x, and the
  tier-coherence suite could not see it (claims §5.68 §3 S6).** The first CSS
  capture of the fourth form read `rrect-lg` 2x `ssimMean` 0.8697 → 0.8230 and
  the interior's standard deviation 0.026 → 0.143 against Apple's 0.081: the
  tier's σ halved at 2x. The unit suites pin the two tiers' *laws* to each
  other over dpr, which is exactly the property that hides a tier rendering
  the wrong scale on purpose; only a capture against the bed sees it. The
  lesson for the harness: a cross-tier pin on the law is not a pin on the
  rows, and a decision that holds rows by decision needs a capture to check
  it was executed.
- **Three CSS cells read frame-unstable in the confirmation**, one of them
  larger than the recorded flicker: `dark-solid__rrect-md` 2x at 6.1e-3 of
  repeat noise beside the known `light-solid__capsule-button` (2.3e-5) and
  `photo__capsule-button__rest-tint-orange-half` (2.7e-3). Every GPU cell was
  deterministic. Recorded; below every bound; the CSS tier's frame timing on
  this machine is the tech-debt tracker's.
- **At 2x the device-pixel widths make the large surfaces visibly crisper
  than Apple's (G1 fourth sweep, the sheets).** The ramp is a null at 2x, so
  what the sheet shows against the W14 bed is candidate A's widths alone:
  `rrect-sm` and the capsule move toward Apple (band +0.024 each), and
  `rrect-md` through `rrect-lg` become crisper inside than Apple's — the
  three rows W14 raised fall 0.010–0.017 (rrect-ml 0.9746 → 0.9585, glass
  0.9762 → 0.9664, rrect-lg 0.9680 → 0.9509), staying above 0.93. It is
  §5.64 §4 seen by eye: Apple's 2x interior is heavier than ours, and a
  narrower body width pushes the large spans the wrong way while it helps
  the small ones. The widths came into this wave by W12 Decision Log 7; the
  evidence since says their 2x half is a trade, and the landing puts it to
  the user as one.
- **The far anchor is unfittable on the calibration cells** (Decision Log 7):
  the only spans it acts on are holdout. A form whose defining constant lives
  above the calibration set's largest span cannot be fitted by the runtime on
  this bed; it is carried from the instrument's reading and read once.
- **The 2x null is a property of the law, verified bit-exact (G1 third
  sweep; claims §5.67 §2).** Four constant pairs render identically over 20
  cells × 107 measurements, and identically to a capture from a different
  build of the shader. A sweep cannot fit a number that changes no pixel, so
  the 2x ramp constants stay provisional by necessity.
- **The start falls across the thick spans, and `sizeThickness` cannot carry
  that (claims §5.67 §4).** The reference's start reads 0.512 / 0.501 / 0.410
  at spans 96 / 128 / 160 while the thickness curve is flat at 1 above 96;
  with one thick start the excursion grows with span (0.039 / 0.156 / 0.284)
  where the reference's shrinks, and `rrect-lg` overshoots its interior by
  33%. The thin-against-thick defect and the thick-against-thick one are the
  same kind — one start where the reference has a curve.
- **The runtime wants more band on thin surfaces than the reference's contour
  reading implies (claims §5.67 §1).** The fitted thin start 0.72 is 0.08
  above G0's 0.637 / 0.642, and the fitted reach 80 device px is below G0's
  100–110. Both are interior optima with both neighbours measured. Which
  estimate is the better one is not settled: the instrument reads the
  contour share at three pitches, the runtime is scored on band SSIM.
- **Something at the coverage ramp touches the outside of the contour** by
  about a thousandth: `hc-text__capsule-button` (holdout) `ssimOutside`
  −0.00112 at 1x where S5 admits 0.001. A body law should be a null outside
  the contour. Recorded as a gap.
- **The reference's ramp runs the other way at 2x (G1 second sweep; claims
  §5.64 §4).** Against vitrea's own deep value the excursion G0 measured is
  positive on every cell at 1x (+0.031 to +0.174) and **negative on every
  cell at 2x** (−0.095 to −0.289): at 2x the reference's contour is heavier
  than vitrea's deep interior, so no upward excursion can help and the
  measured best is the ramp doing nothing. The wave's 1x and 2x halves are
  not one problem, and only the 1x half is a ramp.
- **A cell at `sizeSpanMin` is immovable by any excursion above the deep
  value.** `rrect-sm` is 64×32, so the law reads span 32 — exactly
  `sizeSpanMin`, where the restored curve sits at the floor and the deep
  sharp share is exactly `1 − sizeScatterFloor`. Any form whose excursion is
  `max(0, s₀ − sDeep)` needs a start above 0.600 to touch it at all. Worth
  carrying into any later span-law work: the bed's smallest cell sits on the
  curve's own boundary.
- **The first form is span-flat where the bed is span-graded (G1 first
  sweep; claims §5.63).** Its projection runs 0.43–0.56 at 1x against the
  retired law's 0.41–1.00; every cell can be raised alone and never
  together. `rrect-lg` at 1x overshoots the reference's `interiorStdDev`
  (0.0938 against 0.0650) by more than the W12 close undershot it (0.0540).
  The data asks for the deep value to be the span-graded heavy share and the
  excursion the sharp term the band wants — G0's H2, the Design's "ramp with
  a floor" — which the four constants could not express, so no sweep of them
  could find it.
- **The 2x interior the widths won is spent by a ramp without a floor.**
  §5.58 §2's widths-only reading is the best 2x `interiorStdDev` on record
  and all 38 2x points are worse; S3's best departure is 0.0151. A form that
  leaves the deep interior where the widths put it is the constraint the
  re-form carries.
- **The runtime's reach is about twice G0's.** Both scales' optima sit near
  200 device px against G0's 100–110, and the band is flat above ≈ 200; the
  first form's reach was pinned by the band while carrying the span law, so
  the number may move under the second form. Recorded, not explained.

- **The stacked scene's proxy moves with the ramp's projection at 2x, where
  the GPU tier's own law does not (2026-09-04, the landing's dry run).** The
  2x captures were predicted byte-identical to the W14 bed and 46 of 49 are;
  the three `glass-over-glass` cells differ by one code on 39% of the
  overlay's pixels, uniformly in depth, the level unchanged. The overlay
  samples the base plane through a proxy padded by 3σ of the *projected*
  scatter σ, and G1's binding rule made that projection the ramp's — so the
  proxy shrank from 299 × 171 to 292 × 164 device px (σ 4.918 → 4.352 CSS px
  for the 120 × 56 overlay) and the pyramid's texel phase moved with it. Not
  the material: a support floor that at 2x follows the 1x ramp's projection
  (Decision Log 5's `CSS_TIER_RAMP_SCALE`) while the GPU tier draws the bed's
  span law there. Deterministic on both sides; the rows move by at most
  0.0001 (claims §5.68 §7).

## Outcomes & Retrospective

(open)

## Revision Notes

- 2026-09-03: opened from W12 Decision Log 7.
- 2026-09-03: X6 gains `ssimOutside` after the baseline's first reading; S5 and the Risks
  carry the outer shadow; the shadow's wave chartered in Deferred (Surprises).
- 2026-09-03: Decision Log 2 — W14 chartered beside this wave (user-decided); X8 in W14
  orders the two landings.
- 2026-09-03: G0 complete (claims §5.61); three Surprises; the dot returned to W12.
- 2026-09-03: the first form's sweep complete (claims §5.63); Decision Log 3 re-declares the
  form with the retired span law underneath the ramp; three Surprises; G1 continues on the
  same branch with a second sweep.
- 2026-09-03: the first form's branch reviewed; two findings (the CSS projection's extents,
  pyramid invalidation over dpr) folded into the re-form (Tracking Map).
- 2026-09-04: Decision Log 8 — the landing, user-decided: the ramp alone, the 2x widths restored.
- 2026-09-03: **G1 declared** (claims §5.68). The CSS tier's device-pixel width division found
  by the first CSS capture and removed (Decision Log 5 executed in full, amended above); the
  fourth form's review — three code findings fixed on the branch, the spec finding amended; two
  Surprises; the Tracking Map's G1 row rewritten whole (an earlier edit had left a status
  segment embedded mid-row); G2 READY on the user's choice between the two landings.
- 2026-09-03: the fourth form fitted on the W14 bed (sweep-4); Decision Log 7 (the far start
  carried from the reference's reading); two Surprises (the widths' 2x trade seen by eye; the
  far anchor unfittable on calibration); the sheets sent; the declaration pending the CSS rows.
- 2026-09-03: the third form fitted (claims §5.67): S4 met at 1x on every cell, the 2x null
  bit-exact, one holdout miss with its cause; Decision Log 6 decides the fourth form (the start's
  decline past the thickness knee, one constant) to be fitted on the W14 bed under X8; four
  Surprises.
- 2026-09-03: the 2x deep-value charter ordered behind the demo hero-ground decision and the
  coverage openers (user-decided; Deferred).
- 2026-09-03: Decision Log 5 — the CSS tier keeps the 1x law for the ramp's mix (user-decided);
  Decision Log 1's question 2 closed.
- 2026-09-03: the second form refuted in the renderer (claims §5.64); Decision Log 4 grades the
  start by `sizeThickness` and refines S4 by scale (a null at 2x, verified by capture); the 2x
  deep value goes to Deferred as its own charter; two Surprises.
- 2026-09-04: Decision Log 8 executed on the branch (`40f409c`; the landing review's three
  findings fixed in `beb823f`); the dry run read against both predictions (claims §5.68 §7);
  one Surprise (the stacked scene's proxy at 2x); the 2x charter gains two terms; G2 landing.
