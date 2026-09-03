# W12 — The lens band's structure (2026-09-03)

> **Parent:** the post-v1 wave
> (`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`), by way of its
> Deferred entry "the 2x lens study" (added 2026-09-03 from claims §5.48).
> Picked by the user 2026-09-03: "Let's start it ahead of the two-layer CSS
> body." **Consumes:** claims §5.43–§5.44 (W11c G2: the band measured per
> depth shell as a radial mean, the 1.6× gain that landed), §5.41 §5 and W11
> Decision Log 4 (the 2x interior is a different object; 2x rows held by
> decision until a Retina capture exists), §5.48 (the gap read by eye).
> Three gates in the W9/W10/W11 shape: an instrument, a measurement, a
> declared fit with its referee — and a conditional decision round on the
> 2x body.

## Purpose

The GPU tier's lens has the reference's magnitude (W11c G2) and not its
shape. Read by eye against the fixtures at both scales (§5.48, and the
crops this wave opens on), the reference's band is a set of crisp lobes: the
checker rows are reversed and compressed into the band, the inner boundary
of the band — where the reversal folds — is sharp and high-contrast, every
rounded corner carries a large round lobe, and a thin dark line sits just
inside the bright rim. Ours displaces the sample by the same profile but
reads a heavily pre-blurred body at the displaced position, so the fold
that makes the reference's lobes sharp is blurred away before it can
happen; our band is a faint compression. This is visible at 1x as much as
at 2x — the metric that scored the band's mean could not see it — and 2x is
where it is most legible and where the user reads it on a Retina display.

Beside the band, the 2x interior itself is more transparent and less hazy
than ours (transmission 0.41 against 0.24, level 0.47 against 0.58 on
`rrect-md`), which W11 held by decision. This unit measures the band as a
displacement **field** with an instrument proven on vitrea's own capture
first, fits an edge profile with real thickness only if the field asks for
one, lands it on the GPU tier under the W11c stops, and puts the 2x body's
gap in front of the user with the two capture routes that could close it.
Every gap it does not close is written down with its evidence, per the
project's rule.

## Parent-Level Acceptance

- The band's displacement field on the reference is **measured**, not
  modelled: D(u) along the normal per edge and per span at 1x and 2x, the
  blur order (before or after the displacement) that explains the band, the
  band's own σ and transmission by depth, the corner field, and the
  near-contour profile (rim line, dark line) — with the instrument's
  recovery of vitrea's known law recorded beside every reference reading.
- A form is declared **before** the landing capture, fitted at 1x with
  `rrect-lg` held out, predicted at 2x by dry run, and refereed on the full
  bed under the stops below. The band's absolute loss on the three
  calibration checkerboard cells falls again at 1x, and the 2x
  `checkerboard__rrect-ml` / `-lg` / `glass-over-glass` texture rows rise;
  any that still miss are re-pinned with the mechanism named.
- **By eye:** a side-by-side sheet (native | vitrea | signed difference,
  2x, 3× nearest-neighbour, the five checkerboard spans and `photo__rrect-md`)
  is produced at every gate, committed under the wave's results directory,
  and sent to the user's Retina display; the user's reading is recorded in
  the Decision Log beside the numbers.
- The 2x body (transmission, level, σ) is measured on every checkerboard
  cell for both sides and the decision round G3 is presented: a 2x probe
  capture on this machine's virtual HiDPI display, a real Retina capture
  (user-held), or hold — with what each would and would not settle.
- All package suites green, lint clean, goldens re-recorded only where the
  Decision Log names the scene and the reason; the canonical matrix rebuilt
  once at recomposition (X1); every gap left is in claims, this Deferred
  list, or the tech-debt tracker.

## Grounding Baseline (measured on the 0.3.0 bed, 2026-09-03)

- Lens as landed (W11c G2): `D(u) = lensDepth × 1.6 × (1 − u/lensDepth)²`
  along the SDF normal, `lensDepth = thickness × lensSizeGain ≤ span/2`
  (20.8 CSS px on spans ≥ 96); both body components sampled at the
  displaced position; the CSS tier has no lens by contract.
- Interior, single-Gaussian fit over the inset interior (σ CSS px / level a
  / transmission t), `checkerboard__rrect-md`:
  1x native σ 1.25 / 0.556 / 0.246, vitrea σ 1.5 / 0.573 / 0.239 — agree;
  2x native σ 3.0 / 0.473 / 0.413, vitrea σ 1.5 / 0.582 / 0.239 — the
  reference transmits 1.7× more and carries 0.11 less haze.
- Texture-tier `ssimMean`, checkerboard: 1x `rrect-md` 0.9538, `-ml` 0.9307,
  `-lg` 0.9286 (bounds ≥ 0.88, met); 2x `rrect-md` 0.9389 (met, ≥ 0.93),
  `-ml` 0.9023, `-lg` 0.9013, `glass-over-glass` 0.9076 (floors, held by
  W11 Decision Log 4). Band loss share after G2 (1x): 43–56%; outside band
  39–47% (§5.44 §3).
- The 2x bed is the BetterDisplay virtual HiDPI display's ("가상 16:9",
  hiDPI on), attested settled A/B; no real Retina panel has been captured.
  The machine still has that display online (1x mode today), so a 2x probe
  capture is one `--hiDPI=on` and one scene-set edit away.
- Evidence from the read by eye (`w12/md-{1x,2x}-{full,corner,left}.png`,
  `lg-2x-full.png`, `photo-md-2x-full.png` in the job scratch; the sheet
  tooling below commits them): the lobes, the sharp fold, the corner lobes
  and the dark line are on the reference at both scales and on ours at
  neither.

## Design

Three decisions are binding at this level because only the whole picture
settles them:

- **[binding — the instrument precedes the reading]** No reference number
  is recorded until the same instrument has recovered vitrea's own law from
  vitrea's own capture (33.3·(1 − u/20.8)² at 1x on `rrect-md`, within
  1 CSS px over 2 ≤ u ≤ 20; the 2x capture in CSS px). W11c's shell fit
  read a radial mean through a fold and could not tell shape from blur;
  this wave's instrument is judged on a known field first.
- **[binding — a field, then a form]** D(u) is recovered non-parametrically
  (a smooth warp s(u) = u + D(u) along lines normal to each straight edge,
  the fold allowed, fitted under both blur orders), and only then are forms
  ranked on it: the landed quadratic, a physical bevel (Snell through a
  circular or superellipse edge of width L, thickness T, index n), or a
  free profile. A physical constant (n, T) enters the profile only if the
  physical form beats the empirical one at equal parameter count on the
  held-out span; otherwise the empirical form lands and the physical
  reading is recorded as a finding.
- **[binding — the blur order is a measurement, not a preference]** Whether
  the reference blurs the backdrop before or after displacing it is decided
  by the band's residual under each order on the probe's pitch-32/64 cells,
  and the GPU tier takes the order that wins even though it changes the
  pass structure (blur-after means the lens samples the sharp source and
  the body blur runs on the refracted image, or an equivalent). The CSS
  tier is untouched either way.

Advisory, carried into the children: the fold arithmetic of §5.43 §2 (the
source coordinate stationary near u ≈ 17 under the landed law); the
Fresnel reading of the rim (a bright line where incidence grazes, a dark
line where transmission collapses) as a candidate explanation of the
near-contour profile, to be tested, not assumed; the W9 probe's scene set
(`apps/reference-apple/scenes-w9-probe.json`) as the 2x probe's template.

**Outside evidence, advisory (2026-09-03, research pass at open).** Apple
documents lensing only in words (WWDC25 session 219: the material "bends,
shapes, and concentrates light", larger surfaces show "more pronounced
lensing and refraction effects, and a softer scattering of light"); no
public source has measured a profile, an index or a thickness from the
real material. One reconstruction built from Apple's private Core
Animation layers (AlexStrNik/ShatteredGlass, `CustomGlassView.swift`)
exposes the `glassBackground` `CAFilter`'s parameter surface, and that
surface — not the author's working values — is the strongest hint on the
form: **two refraction terms of opposite sign and different widths**
(`inputInnerRefractionAmount` / `-Height`, `inputOuterRefractionAmount` /
`-Height`, working values −40 over 12.5 and +10 over 6.25), a **blur mix
ramped by distance from the edge** (`inputBlurDistance0..4` /
`inputBlurOpacity0..4`, working values −25, −1, 0, 0, 10 with 1, 0.5, 0.5,
1, 1), a small `inputBlurRadius` (1.5) on a backdrop layer rasterised at
**`setScale(0.25)`**, a "bleed" term (`inputBleedAmount` / `-Height` /
`-BlurRadius`), and the rim drawn by two separate `CASDFGlassHighlightEffect`
layers at 45° and −135° (`curvature`, `spread`, `height`), not by the
backdrop filter. No chromatic-aberration parameter exists. Three
predictions follow and G1 tests each: D(u) is reduced or counter-signed
within a few px of the contour and peaks inside (the fold and the dark
line); the sharp share of the body is a depth ramp, not a span law
(vitrea's `sizeScatterFloor`/`SpanMax` would be its 1x projection); and a
quarter-scale backdrop with one blur radius in buffer pixels makes the
material scale-dependent in points — which would explain the 2x interior
as physics rather than as a virtual-display artefact. Reproductions on the
web (kube.io's SVG height-profile Snell map at n 1.5, the Flutter port's
`refract()` through a circular bevel, ybouane's sharp/blurred mix biased
sharp at the rim) are recorded as prior art, none of them measured.

## Children

### G0: The instrument — spike (deliverable: findings)

- **Purpose:** a warp-recovery instrument that reads D(u) from a checkerboard
  cell without assuming its shape. Along each line normal to a straight edge
  through a cell-column centre, the observed luminance is `Y(u) = a + t ·
  B(s(u))` (blur-before) or `Y = a + t · (G_σ ∗ P∘s)(u)` (blur-after), with
  `s(u) = u + D(u)` a smooth spline (knots every 2 CSS px, second-difference
  penalty, sign of s′ free so the fold is representable). A 2-D corner
  check renders the recovered straight-edge D radially about the corner
  centre and compares to the capture.
- **Acceptance:** on vitrea's own `checkerboard__rrect-md__rest` webgpu
  captures (1x and 2x) the recovered D(u) is within 1 CSS px of the
  analytic law over 2 ≤ u ≤ 20 on all four edges, and the blur-before order
  is preferred (it is what the shader does); on the 1x probe pitch-32 cell
  the same holds. The corner check reproduces vitrea's own corner to the
  same RMS as its straight edges.
- **Edges:** blocks G1. **Track:** spike, this session.

### G1: The measurement — spike (deliverable: findings; claims §5.49)

- **Purpose:** the reference's field. Per edge (top, bottom, left, right —
  the light direction may break the symmetry) and per span: D(u) with a
  confidence band across the lines, at 1x on the probe's pitch-32 and -64
  cells (`rrect-md`, `-ml`, `-lg`) and the canonical pitch 16, and at 2x on
  the canonical cells; the blur order and the band's σ, t, a by depth; the
  corner field on `rrect-md` and `-lg` against the radial prediction; the
  near-contour profile in linear luminance at 2x (0 ≤ u ≤ 6, 0.5 px steps)
  on solid, checkerboard and photo backdrops; the small spans
  (`rrect-sm`, `capsule-button`) where the lens depth is clamped; and the
  2x body (σ, t, a) on every checkerboard cell, both sides, both tiers.
- **Acceptance:** every number above recorded with the instrument's
  validation beside it; the forms ranked (landed quadratic / physical bevel
  / free) by RMS on the fit spans and the held-out `rrect-lg`; the by-eye
  sheet at 2x produced and sent. **No constant changes in G1.**
- **Edges:** blocked-by G0; blocks G2, G3. **Track:** spike, this session.

### G2: The declared fit and its referee — controlled

- **Purpose:** the form G1 ranks first, declared with its constants and its
  pass-structure change before the landing capture; a dry run (band
  replaced by the declared form at the reference's own a, t) by whole-crop
  SSIM at 1x and 2x on the calibration cells and the holdout; then the GPU
  tier implemented, goldens attributed, and the twelve-run referee.
- **Acceptance:** the band's absolute loss on `rrect-md` / `-ml` / `-lg`
  (1x) falls from the §5.44 §3 values; the 2x checkerboard texture rows
  rise; the by-eye sheet shows the lobes, the fold and the corner lobes on
  ours; and the **stops** (declared here, carried from §5.43 §4): any
  solid-backdrop cell moving by more than one code value; any `photo`,
  dark-profile or accessibility cell leaving its bounds; any CSS-tier
  capture differing at all; any 2x floor crossed; any small-span texture
  cell (`rrect-sm`, `capsule-button`, `toolbar-group`) below its 0.3.0 SSIM
  by more than 0.005; the rim/specular constants untouched unless G1
  measures them as the term.
- **Edges:** blocked-by G1; blocks recomposition. **Track:** controlled.

### G3: The 2x body — decision round (conditional on G1)

- **Purpose:** G1's 2x body numbers against the 1x law (fit at 1x, predict
  2x, W11 Decision Log 4). If the 2x transmission/level gap survives G2's
  lens (it should: the interior is not the band), present the routes: (a) a
  2x probe capture on this machine's virtual HiDPI display (the W9 scene
  set with `-2x-` profile entries, pitches 4…64 × five spans) to fit a
  scale-aware body with its virtual-display caveat stated; (b) a real Retina
  capture on the user's MacBook (harness build + ScreenCaptureKit TCC,
  user-held); (c) hold, claim narrowed to 1x as today.
- **Acceptance:** the user decides; the decision and its reason land in
  the Decision Log; a chosen capture route becomes its own child.
- **Edges:** blocked-by G1. **Track:** decision round.

## Cross-Child Contracts

- **X1 — the canonical rebuild.** `rm results/matrix.json`, then the twelve
  per-profile runs, once at recomposition; children referee on partial runs
  to a scratch matrix. Owner: parent. Also at X1: the demo's reference-panel
  fixture (`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png`
  and its `.cell.json`) is a byte copy of the harness's GPU capture and must
  be re-copied from the rebuilt `web-captures/` — on the G2 + ω 0.8 material
  it already differs from the live panel by 0.0219 encoded luma against its
  0.02 bound (`reference-panel.gpu.spec.ts`, seen 2026-09-03 on 6ff1319),
  which is the test failing for the right reason.
- **X2 — floor bookkeeping.** As W11 X2: a floor comes off only with its
  bound restored as a met claim in §5.27; `UNMET_ROWS`, `PREDICATE_EXCLUDES`
  edited beside the section that justifies them. Owner: parent.
- **X3 — the untouched bed.** The whole-bed scan against the 0.3.0 matrix
  (`matrix-w11c-g2-close.json` is that bed); every cell moved by more than
  0.005 is named. Owner: parent; G2 binds.
- **X4 — the instrument's validation travels with every reading.** A
  reference D(u) table is never quoted without the vitrea-capture recovery
  from the same instrument and the same cell geometry beside it. Owner: G0;
  G1 and G2 bind.
- **X5 — the by-eye sheet.** `packages/calibration/results/2026-09-03-w12-lens/sheets/<gate>-2x.png`:
  native | vitrea webgpu | signed luma difference, 3× nearest-neighbour, one
  row per cell (`rrect-sm`, `capsule-button`, `rrect-md`, `rrect-ml`,
  `rrect-lg` on checkerboard; `photo__rrect-md`), plus 10× corner crops of
  `rrect-md`. Produced by one script kept in that directory, at G1 (the
  0.3.0 bed), at G2's dry run, and at G2's landing; sent to the user each
  time. Owner: parent.

## Ordering & Dependency Map

G0 → G1 → G2 → recomposition; G3 opens on G1's numbers and runs beside G2.
G0 and G1 are one session's work and share a scratch library; G1 is split
across two workers (straight edges and blur order; corners, near-contour
profile and the 2x body) that write findings, not the spec.

## Risks & Mitigations

- **The fold defeats the warp fit** (a stationary s(u) is a degenerate
  design matrix). Mitigation: the spline's second-difference penalty and
  the multi-line average; the instrument's acceptance on vitrea's own fold
  is the proof it copes.
- **Blur-after changes the renderer's pass order** and may cost a pass.
  Mitigation: G1 measures the order; G2 declares the pass structure with
  its cost before implementing; an equivalent single-pass approximation is
  acceptable if its residual on the probe is within the instrument's noise.
- **The 2x bed is a virtual display.** Mitigation: G3 is a decision round,
  not a fit; nothing 2x-specific lands in a constant in this wave without
  the user choosing a capture route.
- **Corner lobes may need the true lens depth to exceed the corner radius**
  (D(0) 33 > r 20 on `rrect-md`). Mitigation: the corner check is measured
  against the radial prediction before any corner-specific term is
  considered; a corner term is a finding first.

## Deferred / Out of Scope

- **The body's depth ramp, carrying the device-pixel widths — the next body
  wave (Decision Log 7).** What is settled: the reference's body is one
  kernel in device pixels, vitrea's GPU tier renders its interior exactly
  when the two widths are read in device pixels, the transmission has no
  scale term (claims §5.55, §5.58). What is left: the band — the
  reference's sharp share is ≈ 0.5 at the contour and 0 deep inside at 2x
  where vitrea's is one number per span, and with the widths right the
  lens refracts a crisp checker through a band the reference blurs
  (`rrect-ml` 2x 0.8998 against its 0.9013 floor). Shape of the work: (1)
  an instrument that measures the band through the lens — the sharp share
  and the two widths by depth u, per span and scale, on the committed 1x
  and 2x probes, with vitrea's recovery beside every reading (X4); (2) a
  declared form k(u, span, dpr) for the sharp share's ramp, fitted on
  both probes with `rrect-lg` held out, the widths in device pixels, the
  1x bed's rows predicted (the 1x fit's uniform k per span is the ramp's
  1x average, so 1x moves and must be budgeted, unlike G3's candidate);
  (3) the band budgeted as a stop of its own beside the whole-crop rows;
  (4) the runtime-in-the-loop sweep of `g3/referee/sweep/` as the
  instrument for the fit, since the paper model of the mip-chain heavy
  tap over-credited it (§5.58 §1); (5) both tiers — the CSS tier's single
  `blur()` cannot carry a ramp, so its rows either stay predicted from the
  widths alone or the two-layer CSS body (below) opens with it. Starts
  from branch `w12-g3-candidate-a` (`56283a1`).

- **Three by-eye gaps from the user's fidelity-gap list (2026-09-03), not
  yet measured:**
  - **The dot disappears on `impulse__capsule-button__rest`.** Apple's
    shows the dot through the glass; ours does not. Points at transmission
    on dark grounds, not the band. The G1 / G3 body measurement covers
    checkerboards only; the shape of the work is adding the dark grounds
    (`impulse`, `dark-solid`) to whatever measures transmission — the
    probe scene set or a dark-ground pitch axis — and reading the
    response there against the light one. *Measured by W13 G0 (2026-09-03,
    claims §5.61 §4):* vitrea's capsule interior on `impulse` has standard
    deviation exactly 0 at the plate's own mean at four profiles — the
    group sampled (`gpu-texture`, `exact`) and the dark-regime response
    closed the surface entirely — where the reference keeps the dot at
    0.0066 / 0.0266 (1x / 2x) and passes ≈ 0.025 of the structure. Not the
    body's mix or widths. Shape of the work now: W9's dark anchor of the
    response curve (the occlusion it drives at L ≈ 0.004), fitted so the
    thin material over a near-black backdrop transmits the reference's
    sliver; one constant, its own small round.
  - **A possible whole-surface dome.** The 3D curvature the eye sees may
    be a shallow magnification across the interior, not only at the
    edges. The G1 instrument pins displacement to zero past u ≈ 28 px and
    cannot see it. Shape of the work: an interior pitch check — the
    checker pitch measured inside the surface against outside, per span
    and scale, on the probe beds already committed.
  - **The shadow is darker on `light-solid__capsule-button__rest`.** The
    outer shadow (W8) was measured on large cells only and its size gain
    is inert at 1; Apple's small surfaces cast lighter shadows. Shape of
    the work: a by-eye check on the small spans and a measurement of the
    shadow's span law, which the layer dump already reads (claims §5.50:
    amount min(0.625·span, 75), height 0.4·span, opacity 0.5 − (span −
    48)/448, blur 40 from span 96). *Measured by W13 X6 (2026-09-03):*
    vitrea's shadow below the capsule is 2.4× the reference's integrated
    darkening at both scales (−0.094 against −0.040 luma at the contour),
    and the reference's shadow is a gray composite that lifts blacks
    where vitrea's is a black multiply — chartered as the outer shadow's
    wave in W13's Deferred.

- **A by-eye-aligned band metric.** ω 0.8 lost 0.001–0.002 SSIM on every
  texture row that can see it and the user read it as much closer to
  macOS (Decision Log 6): whole-crop SSIM weights the blurred interior and
  not the corner or the along-edge stretch. Shape of the work: a windowed
  metric on the band's crops (the G1 instrument's D(u) residual per edge
  and corner, or SSIM restricted to the band), adopted beside the whole-
  crop bound, so a lens change is scored where the eye looks.

- The two-layer CSS body (W11 Decision Log 5) — unchanged, still deferred.
- The outside band (contour-straddling windows; W11 Deferred) — unchanged.
- Chromatic aberration in the band: recorded if G1 sees it (the
  checkerboard is achromatic; `photo` is where it would show); not fitted.
- The Gecko manual pass and the Chromium bug report — user-held, unchanged.

**Gaps opened by the layer dump (claims §5.50), each future work by the
project's rule**, in the order they would be worth a wave:

- **The bleed term.** Thick surfaces (span > 64) composite a pulled-in,
  heavily blurred, darken-blended copy of the outside backdrop over the
  edge (`inputBleedAmount` = `Height` 0.35·span, blur 0.7·span, opacity
  (span − 64)/192, colour matrix black 0.9 / saturation 1.2). Vitrea has
  no such term; its visible effect is the soft darkening of the band's
  outer half on structured backdrops. Measure it on the `photo` cells
  (where colour bleeds) before modelling.
- **The shadow block versus W8.** Offset (0, 8), blur radius 40 from
  span 72, amount min(0.625·span, 75), height 0.4·span, opacity
  0.5 − (span − 48)/448, colour saturation 1.8, vibrancy (span − 64)/96,
  a fill alpha that adapts on thin surfaces (0.278 checkerboard / 0.05
  light-solid / 0.285 photo). W8 fitted one σ and one reach; this is the
  reference's own law and it has a knee W8 could not see.
- **The face on thin surfaces adapts; on thick it is constant.** Black
  0.5 / white 1.03 / fill α 0.4 above the knee on every backdrop; below it
  black 0.35–0.82, white 0.92–1.03, fill α 0.27–0.52 by backdrop. W9's
  response curve is this mapping seen from outside; a dump on the dark,
  mid-dark, impulse and hc-text backdrops and the dark scheme reads it
  directly (one `--scenes` run, no TCC).
- **The body is one blur in a quarter-device-scale buffer with a depth
  ramp** (radius (span + 8)/42 floored at 4/3; opacity 0.5 at the edge →
  1 at span/2). The dry run's body test (§5.51 §2) reproduces the 2x
  interior in kind and not the 1x sharp share as parametrised: the ramp's
  effective form at 1x, or the buffer's scale at 1x, is still to be read —
  G3's 2x probe and a 1x re-read of the ramp on the probe's pitch axis.
- **The rim is two opposed lights** (key at −45°, fill at +135°, amount
  0.5 each, spread π/2, curvature 0.7) drawn by a separate SDF effect, not
  by the backdrop filter. Vitrea's single light gives a 3.2:1 anisotropy
  the reference does not have (§5.49 §5). For the rim's owner (§6.2).
- **The author tint is a colour matrix on luminance** (orange R = 0.4·L +
  0.6, G = 0.263·L + 0.321, B = 0, landing on systemOrange at L = 1) in a
  separate backdrop-aware pass, and does not touch the glass filter. W10's
  "opaque shade of the seed" is its outside view; the matrix form would
  make the shade exact.
- **Continuous corners.** The reference's shape is `cornerCurve:
  continuous` (superellipse-style); vitrea's field family is circular. The
  silhouette metrics tolerate it; the corner crops show it, and the
  corner's dark ring under the bright arc (§5.51 §2) may be its shadow.
- **The ovalization's oval.** Apple's 0.5 on an ellipse inscribed in the
  box gives half the measured tilt; the oval it blends toward is more
  curved at the edge midpoint, or the blend is not of unit directions.
  ω 0.6 is the pixels' value; the true field is one more dump question
  (`CASDFElementLayer` has no further readable property naming it) or a
  corner-resolved fit.
- **Apple's two-term profile.** Threads the crossings at zero fitted
  amplitudes and loses on the pixels (§5.51 §2): what the amounts do
  spatially is not two cubics. A finding for whoever wants the exact
  operator; the landed power law is its measured result.
- **The pressed state** is not in the filter's inputs (rest and pressed
  read identical); the press lives in the highlight or the transform.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | this session; validation in `results/2026-09-03-w12-lens/g1/g0-instrument.md`; claims §5.49 §1 | COMPLETE 2026-09-03 (0.35 / 0.33 px at 1x / 2x) |
| G1 | two workers, findings and tables committed under `results/2026-09-03-w12-lens/g1/`; claims §5.49 | COMPLETE 2026-09-03 |
| G1c (added) | the harness `dump-layers` command (d3fb396) and the settled dumps under `results/2026-09-03-w12-lens/layer-dumps/`; claims §5.50 — the reference's own parameters | COMPLETE 2026-09-03 |
| G2 | dry run and referee in `results/2026-09-03-w12-lens/g2/` (claims §5.51–§5.52); Decision Logs 3–4; commits `cab52ad`, `27704a7`; sheets `sheets/g2-{2x,1x}.png`; the ω 0.8 A/B measured (claims §5.54, `g2b/`) and landed by eye (Decision Log 6) | LANDED 2026-09-03; ω 0.8 2026-09-03 |
| G3 | decision round → controlled round (Decision Log 5, user-decided); the 2x probe materialised under `results/2026-09-03-w12-lens/probe-2x/` (five runs, attested per cell, four cells majority-settled; claims §5.53); pitch-axis measurement complete (`g3/g3-measurement.md`, claims §5.55: one kernel in device px, only the sharp term's weight changes with scale; G2 stands at 2x); the 1x-preserving variant, exclusion refit and SSIM dry run (`g3/` §8); **declared** in claims §5.56; candidate A implemented and refereed (`g3/referee/`, branch `w12-g3-candidate-a`) — **stop 3 tripped**, the 2x texture rows fell, not landed (claims §5.57); the corrected dry run (g3 §9) and the runtime sweep (`g3/referee/sweep/`, claims §5.58): the device-pixel widths put the 2x interior on the reference exactly, any weight shift moves it away, the band is what is left (the depth ramp); **held at `main` by Decision Log 7** — the depth-ramp round is the next body wave and carries the widths, branch `w12-g3-candidate-a` kept as its start | HELD 2026-09-03 (Decision Log 7; refereed, not landed) |
| X1 | `results/2026-09-03-w12-lens/x1/x1-rebuild.sh`; claims §5.59 §1 — twelve runs at `8b456d6`, GPU rows and captures identical to the ω 0.8 referee bed, CSS captures identical on 114 / 115 (one pixel, one code value, named); the demo fixture re-copied, its spec green | DONE 2026-09-03 |
| X2 | `adopted-thresholds.test.ts`, §5.27 amended; claims §5.59 §3 — three 2x texture floors ratcheted up 0.010–0.014, none met, the mechanism re-attributed (the ramp); 11 → 11 | DONE 2026-09-03 |
| X3 | claims §5.59 §2 — eighty GPU cells moved, all the lens, fifteen above 0.005 named; the `hc-text` silhouettes named; solids, impulse and photo unchanged | DONE 2026-09-03 |
| X5 | `sheets/g1-*`, `g2-dryrun-*`, `g2-*`, `g2b-*`, `g3-*` and the A/B composites; sent at every gate | DONE 2026-09-03 |
| recomposition | Outcomes & Retrospective; claims §5.59 | RECOMPOSED 2026-09-03 |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-03)

**Evidence.** The 0.3.0 crops read by eye (Grounding Baseline) and the
interior fits at both scales. The lobes, the sharp fold, the corner lobes
and the dark line are on the reference at 1x and 2x and on ours at neither;
the 2x interior gap is in transmission and level, not in the band.

**Decided (this session, within the user's pick):** three gates and a
decision round as written; the instrument-first rule, the field-then-form
rule and the blur-order-as-measurement rule bound at this level. Rejected:
fitting a corner term or a rim term from the eye (both are findings until
G1 measures them); a 2x constant set (W11 Decision Log 4 stands until G3).

**For the user:** G3's route, and the by-eye verdict at G2 — the numbers
will say whether the band's loss fell; the user's display says whether the
material reads as glass.

### Decision Log 2 — the G1 sheet read by the user; G2 kept; the 2x probe started (2026-09-03; user-decided)

**Evidence.** The G1 by-eye sheets (`results/2026-09-03-w12-lens/sheets/g1-{2x,1x}.png`)
and the G1 findings on corners, the near-contour profile, the small spans,
the 2x body and the depth ramp (claims §5.49 when written). The user's
reading, in their words: "Apple's definitely look more subtle and refined.
Apple's sort of look like cloudy glass, while ours look way too glassy …
our vitrea GPU tier is quite close to Apple's with just a final optic
physics for 3D edges not being there" — the "too glassy" panel being the
sheet's third column, the signed difference, which the caption had not made
unmistakable; the middle column (ours) is the restrained one at the edge
and the milkier one in the 2x interior. On the two real panels the user's
core statement holds: close except the edge optics, and "too gooey?" for
what the edge shows.

**Decided (user, 2026-09-03): keep G2** — the edge form proceeds as
chartered, fitted to the reference's own band with the stops and the sheet
as the guard against over-glass. The 2x probe capture (G3 route (a)) is
started in the background on the session's recommendation, under the W9
probe's guards, fixtures to scratch; it commits nothing and decides
nothing — it gives G3 numbers.

**Sheet caption rule (from this reading):** every sheet names its columns
on the image and says in the caption that the third is a difference map,
not a render.

### Decision Log 3 — G2 declared: one steep power on Apple's span law along an ovalized normal (2026-09-03)

**Evidence.** Claims §5.49 (the field), §5.50 (the reference's own
parameters, the knee at 64), §5.51 (the dry run: fourteen forms ranked on
the fit cells, the holdout at both scales, the 2x rows and the small
spans).

**Decided (this session, inside the user's "keep G2"):** the form of
§5.51 §3 — lens depth `(thickness/8)·min(0.25·span, 20)`, magnitude
`0.745·(thickness/8)·min(0.8·span, 60)`, extent `1.337·lensDepth`,
exponent 3.69, direction the gradient of the 0.6-blended rounded-rect /
inscribed-oval field on thick surfaces (smoothstep 64 → 72), magnitude
fixed; blur-before; the body, the CSS tier, `sizeThickness` and the inner
shadow untouched. Rejected: Apple's two-term shape at its literal amounts
(loses on the pixels and the holdout — §5.51 §2); ω 0.8 (the tilt's value,
+0.003 on the pixels, kept as the alternative); a fixed tangential stretch
(breaks the small spans); a step at the knee (a smoothstep is the same at
both ends and keeps a morph continuous). The thickness-law doctrine "one
curve for every facet" is amended to "one input, the span, and each
facet's own curve" — the reference's facets have different laws (§5.50),
and the lens now takes its own.

**Held for the user:** ω 0.6 versus 0.8 if the landed sheet reads
under-stretched by eye; the 2x interior route (G3), which the quarter-scale
reading has sharpened (§5.51 §2) but not settled.

### Decision Log 4 — G2 refereed and landed (2026-09-03)

**Verdict.** Claims §5.52: the declared form implemented (`cab52ad`),
twelve runs to a scratch matrix, the whole bed scanned against the 0.3.0
matrix — no stop fired; solids and the CSS tier byte-stable; every
checkerboard texture row up at both scales (1x `rrect-md` / `-ml` / `-lg`
0.9538 / 0.9307 / 0.9286 → 0.9709 / 0.9498 / 0.9442; 2x 0.9389 / 0.9023 /
0.9013 → 0.9521 / 0.9164 / 0.9116; the capsule 0.9770 → 0.9852) within
0.004 of the prediction at 1x; `hc-text` rows up 0.010–0.020 unpredicted.
The landing sheet sent to the user (and to their Retina MacBook by
Taildrop). **Their reading (2026-09-03):** "The current vitrea GPU tier
is much closer. The only gap left seems to be the subtle transparency
difference, and a very subtle difference in optic physics left. Apple's
has a bit more refraction on the edge than ours currently, but a bit."
Read against the numbers: the transparency is the 2x interior (G3); the
"bit more refraction" is the two declared residuals — the direction bends
toward the oval at ω 0.6 where the measured tilt sits at 0.8–1.0, and at 2x
the reference's band keeps more contrast because its body blur is 5 CSS px
there against vitrea's 10 (the quarter-scale law, §5.50), so its lobes
stay crisper. **Follow-up decided:** a one-constant round at ω 0.8
(`lensOvalization`), refereed the same way, with both sheets put side by
side for the user's A/B; the 2x band contrast is G3's.

**Measured (2026-09-03, claims §5.54):** ω 0.8 costs 0.0013–0.0019 SSIM
on every 1x texture row that can see it and 0.0003–0.0009 at 2x, moves
nothing else, and holds every W12 stop against the 0.3.0 bed. By eye it
pulls the long-edge lobes a little further toward the corners and
nothing more; the refraction the eye wants more of is the magnitude
`S`, not ω. Constant and goldens on branch `w12-omega-08-ab`, not
landed; the A/B composites `sheets/g2-vs-g2b-{2x,1x}.png` sent to the
user. **Recommendation: keep 0.6; the user's eye may override.** Overridden: Decision Log 6.

**Decided (this session):** G2 LANDED. The three 2x texture floors stay
by W11 Decision Log 4 (their deficit is the interior's now); the
`hc-text` capsule level move is recorded for the level's owner; the
canonical rebuild and the predicate's one-line edit wait for
recomposition (X1, X2). Held for the user: ω 0.6 versus 0.8 by eye; G3.

### Decision Log 6 — ω 0.8 lands by eye (2026-09-03; user-decided)

**Evidence.** Claims §5.54: ω 0.8 costs 0.0013–0.0019 SSIM on every 1x
texture row that can see it and 0.0003–0.0009 at 2x, moves nothing else,
holds every W12 stop; the field's measured tilt is 0.8–1.0 (§5.49 §3);
the A/B composites `sheets/g2-vs-g2b-{2x,1x}.png`.

**Decided (user):** "omega 0.8 — I can say that's much more similar to
original macOS." The eye overrides the metric's hair: the branch
`w12-omega-08-ab` is cherry-picked onto `main` as it stands
(`lensOvalization` 0.8, fingerprints light `c6e388fc8349282d` / dark
`f9722f244e7f2af2`, five goldens behind `W12_G2B_HASHES`), and §5.54 §1's
rows are the recorded cost at the next canonical rebuild. My
recommendation (keep 0.6) is recorded as overridden. Rejected: holding at
0.6 with the eye's reading in Deferred.

**Follows.** A Deferred entry for the instrument: SSIM over a blurred
interior does not weight the corner or the along-edge stretch the eye
reads; a by-eye-aligned metric on the band's crops is the shape of the
work that would let the metric and the eye agree.

### Decision Log 7 — G3 held at `main`; the depth ramp is the next body wave (2026-09-03; user-decided)

**Evidence.** Claims §5.55 (the reference's body is one kernel in device
pixels; only the sharp term's weight changes with scale), §5.57 (candidate
A: 1x byte-identical, the 2x texture rows fall, stop 3 tripped), §5.58 §2
(the runtime sweep: with `sizeScatterScaleTerm` at 0 the device-pixel
widths put the interior's structure on the reference at every span, every
weight shift moves it away, and `rrect-ml` at 2x reads 0.8998 against its
0.9013 floor — the band is what is left), §5.58 §4 (the transmission has
no scale term).

**Decided (user, 2026-09-03):** "Hold, and open the depth-ramp round as
the next body wave carrying the widths with it." G3 closes HELD: `main`
keeps the ω 0.8 material and the 1x-fitted body; nothing from the
candidate lands in W12. The next body wave is the depth ramp on the sharp
share — k(u, span, dpr) rising from the contour inward, the reference's
own mechanism (§5.50 §2's opacity ramp 0.5 → 1 over span/2; §5.55 §2's
sharp share ≈ 0.5 at the contour and 0 deep inside at 2x) — and it carries
the device-pixel widths (σ_sharp = `blurSigma`/dpr, σ_heavy =
`blurSigma`·`sizeScatterGainMax`/dpr) with it, since the widths are right
and only the band keeps them from landing. Branch `w12-g3-candidate-a`
(commit `56283a1`, worktree kept) is that wave's starting point: the
widths, the dpr plumbing on both tiers and the tier-coherence rows over
dpr {1, 1.5, 2, 3}. Rejected: opening the ramp round inside W12 (a new
declaration, a new instrument — the band measured through the lens — and a
new bed read: a wave of its own, and W12's acceptance is already
answerable); landing the widths alone (the `rrect-ml` 2x floor, a hard
stop).

**Follows.** W12 proceeds to recomposition on `main` as the frozen
configuration: X1 (the twelve runs, the demo fixture re-copied), X2
(floors: the 2x texture rows stay held by decision with the mechanism now
named — the band's depth ramp, not the interior — and the ω 0.8 cost of
§5.54 §1 is the recorded reading), X3, holdout once. The ramp wave's
charter is written from this log and §5.58 §3 when W12 closes.

### Decision Log 5 — G3 opened: the scale-aware body, fitted on both probes (2026-09-03; user-decided)

**Evidence.** Claims §5.49 §7 (the 2x interior: mean scale-invariant,
structure not — σ 3 → 5 with depth on `rrect-md`, transmission 0.41
against ours 0.24), §5.50 §1 (the reference's blur radius is one number
in a quarter-device-scale buffer: 9.9 CSS px at 1x and 4.95 at 2x on span
96, with an opacity ramp in depth), §5.51 §2 (the quarter-scale body as
parametrised explains the 2x interior in kind and not the 1x sharp share),
§5.52 §2 (after G2 the three 2x texture floors' deficit is the interior's),
and the user's own reading of the landing ("the only gap left seems to be
the subtle transparency difference"). The "fit at 1x, predict 2x" rule of
W11 Decision Log 4 was written when the 2x bed's difference had no
mechanism; it now has one, and it is the reference's.

**Decided (user, 2026-09-03): take route (a).** The 2x probe (the W9 scene
set at 2x on the virtual HiDPI display, five runs, settled by majority
vote per cell as the 1x probe was) is the measurement; a **scale-aware
body** is declared from it and fitted jointly on the 1x and 2x probes with
`rrect-lg` held out; W11 Decision Log 4's doctrine is overturned for the
body — the reference's blur is a device-pixel quantity and vitrea's law
may carry the device scale. Rejected: hold (the gap is the largest one
left at 2x and the user reads it); a real Retina capture first (the
virtual display is exonerated by §5.50, and the user's Retina reading
agrees with the virtual bed).

**G3 as a controlled round.** *Measurement:* the 2x probe materialised
(`results/2026-09-03-w12-lens/probe-2x/`, provenance as the W9 probe's);
on its pitch axis (4 / 8 / 16 / 32 / 64) per span and depth: the heavy σ,
the sharp component's σ and share, the level and transmission, against
the 1x probe's; the lens crossings at 2x on pitch 32 / 64 as a check of
G2's law at 2x. *Declaration before the landing capture:* the form (a
device-scale term on the heavy σ, and whatever the pitch axis says about
the sharp share and its depth ramp), fitted on both probes, `rrect-lg`
held out, 2x and 1x canonical rows predicted by dry run. *Both tiers:*
the body law is shared (K5, `tier-coherence`), so the CSS tier's `blur()`
carries the same device-scale term through `devicePixelRatio`; the CSS
tier's rows are predicted and refereed too. *Referee:* the twelve runs on
both beds against the G2 landing; the W12 stops, plus **no 1x row below
its G2-landing value by more than 0.002** and the CSS tier moving only as
predicted. *By eye:* the X5 sheet at 2x and 1x.

**Held for the user:** the by-eye verdict at G3's landing; ω 0.8 (Decision
Log 4) runs first, as the smaller round.

## Surprises & Discoveries

- (2026-09-03, G3) **The dry run's two normalisations hid a fall.** §5.41
  §4's method replaces the interior box at the reference's own level and
  transmission and leaves the band alone; the runtime renders at vitrea's
  transmission and the lens reads the body under the band. The declared
  scale term (heavy weight +0.35 at 2x) collapsed the sharp share and the
  2x texture rows fell 0.004–0.012 where a rise of 0.003–0.006 was
  predicted, while the CSS tier moved toward native from the same
  constants. Any future body dry run evaluates at vitrea's own (a, t) and
  budgets the band. Claims §5.57.
- (2026-09-03, G3) **The reference's body kernel is one kernel in device
  pixels.** On the pitch axis the 1x sharp core is a flat-topped box
  exactly 4 CSS px wide — the quarter-device-scale buffer's own pixel —
  on a base of σ 9 device px; at 2x the base is 8–10 device px and the
  core carries almost no weight. §5.49 §7's "σ widens with depth at 2x"
  was a single-Gaussian fit watching the sharp term die. A two-component
  law with the heavy σ in device px and one scale term on the share fits
  both probes at the residual W11c reached at 1x alone. Two gaps named:
  the interior mean is not scale-invariant on the thin material over
  text and high-contrast backdrops (up to 0.086, a level question), and
  the reference's own quarter-buffer mechanism needs a scale term as
  large as the phenomenological form's, so the mechanism is not yet
  understood. Claims §5.55.
- (2026-09-03, the user, by eye, on the ω A/B composites) **"The degree of
  blurring through the glass is less in Apple's — the sharpness behind the
  glass is reduced less — and instead the transparency is higher."** This
  is the interior, not the band, and it is what claims §5.49 §7 measured
  on the 2x bed in numbers: the reference retains 19–35% more backdrop
  contrast on `rrect-md` / `-ml` / `-lg` (a narrower kernel, σ 5 CSS px at
  2x against our 10) with a higher transmission (0.41 against our 0.24 on
  `rrect-md`) and a lower level (0.473 against 0.556 — less white in the
  plate). The reference's own mechanism is §5.50 §1's quarter-device-scale
  blur. G3 is the round that carries it, on both tiers; the user's reading
  is recorded here as the by-eye acceptance G3's landing sheet must meet:
  sharper behind the glass, more transparent, at 2x.
- (2026-09-03, G3) **The 2x probe needed a per-cell attestation filter, and
  the bistable cells moved.** Two of the five runs were denied window
  activation part-way through (4 and 28 unattested cells); every
  unattested capture returned bytes matching no attested state, so the
  inactive pose is excluded per cell and never voted. Among attested
  observations three cells hold a second settled state (16–43 codes,
  whole-surface) and all three are `rrect-sm` — at 1x the two-state cells
  were the `checkerboard-8` family. Claims §5.53.
- (2026-09-03, G1) **The reference's own parameters are readable.** A
  `dump-layers` command added to the native harness walks SwiftUI's layer
  tree and reads the private `glassBackground` `CAFilter`'s inputs per
  scene (`results/2026-09-03-w12-lens/layer-dumps/`). The material's size
  law is written there as functions of the shape's shorter side: inner
  refraction −min(0.8·span, 60) over min(0.25·span, 20); outer refraction
  +0.2·span over 0.125·span; blur radius max(4/3, (span + 8)/42) with an
  opacity ramp from 0.5 at the edge to 1 at span/2; bleed 0.35·span at an
  opacity (span − 64)/192; shadow amount min(0.625·span, 75), height
  0.4·span, opacity 0.5 − (span − 48)/448, blur 40 from span 96; face black
  and fill alpha and shadow fill alpha adapting to the backdrop. Four things
  follow at once: the two-term lens the research pass predicted is real and
  its cubic reading reproduces the crossings (32.6 / 25 / 12.3 against
  34 / 24 / 12 at u 2 / 4 / 8 on `rrect-md`); the blur opacity ramp is the
  sharp leak that fades with depth (W11c's `sizeScatterFloor` / `SpanMax`
  are its projection); a blur radius in a quarter-device-scale buffer is
  9.9 CSS px at 1x and 4.95 at 2x — the two impulse kernels the bed
  measured — so the 2x reference's "different object" is the material's
  own scale-dependence and the virtual display is exonerated; and the
  shadow's numbers (offset 8, blur 40, height 0.4·span) are W8's to check.
- (2026-09-03, G1) **Five of the filter's inputs animate for seconds.**
  The face's black, white and fill alpha, the shadow's fill alpha and
  `inputClamp` settle toward backdrop-adapted values over several seconds
  after a surface appears; a 1.5 s dump read transients (0.628 and 0.85 on
  two runs of one scene). The dump gained `--settle` and reads at 8 s; the
  first §5.50 readings are amended beside the settled ones. The capture
  protocol's 45 s idle dwell is past it; a future harness feature that
  presents and shoots fast would not be.
- (2026-09-03, G2) **The `hc-text` rows rose more than the checkerboard's**
  (+0.020 on `rrect-md` at 1x) though nothing was fitted on them: the
  bars' reversed images in the band were the term. The capsule's inset
  interior now lies inside its lens extent (11 px inset, 14.7 px extent),
  so its interior level statistic reads band pixels — a measurement
  artefact of the inset, recorded, not a material move.
- (2026-09-03, G1) **The material has a knee at 64 points.** Read at
  spans 48–112: the ovalization, the face constants, the shadow fill, the
  clamp, the bleed and the shadow blur all switch between 64 and 72 while
  the refraction amounts and heights and the blur radius stay continuous
  (claims §5.50 §1). W9's thin/thick rows and W11c's scatter floor were
  this knee seen from outside.
- (2026-09-03, G1) **The band magnifies along the edge**, uniformly about
  the edge's midpoint, by 1.31× / 1.15× / 1.11× at u = 2.5 on spans 96 /
  128 / 160 (2x, confirmed from the checker maxima: 128 / 169.5 / 212 CSS
  px on `rrect-md`, the plate's 135.5 / 167.5 / 199.5 stretched about
  x = 160), ∝ 1/width² within 10%, decaying to 1 by u ≈ 18. No
  normal-only displacement carries it and nothing in the filter's inputs
  names it; G2 tests an empirical tangential term.
- (2026-09-03, G1) **There is no dark line and no counter-signed term.**
  On solid backdrops the reference reads exactly its deep level from
  u = 2.5 inward on every edge at both scales; the line the eye saw is the
  lens crossing a checker boundary at u ≈ 2. The Fresnel advisory does not
  hold. The physical bevel fails structurally (it peaks inside the contour;
  the reference peaks at it).

- (2026-09-03, research pass) The private filter's API has two refraction
  terms, a distance-ramped blur mix and a quarter-scale backdrop (Design,
  "Outside evidence"). If G1 confirms the ramp, W11c G1's span law is a
  projection of a depth law, and if it confirms the quarter scale, the 2x
  bed's "different object" is the material's own scale-dependence.
- (2026-09-03, at open) The gap §5.48 recorded as "the 2x gap" is at 1x
  too: the 1x fixture shows the same lobes and fold, at half the size, and
  ours shows the same faint compression. W11c's SSIM rise at 1x came from
  the band's mean, and the band's shape was never in the metric.

## Outcomes & Retrospective

**RECOMPOSED 2026-09-03 (claims §5.59).** Verified against the
Parent-Level Acceptance, clause by clause, on the bed as it ships:

1. *The band's displacement field measured, not modelled.* G0's instrument
   recovered vitrea's own law to 0.35 / 0.33 px at 1x / 2x before any
   reference number (§5.49 §1); G1 read D(u) per edge, span and scale, the
   blur order (before, by 3–5× in RMS), the band's σ and transmission by
   depth, the corner field and the near-contour profile (§5.49 §2–§6), the
   2x body (§5.49 §7) — and, added as G1c, the reference's own parameters
   from its layer tree (§5.50). Every reference table carries the
   instrument's recovery beside it (X4).
2. *A form declared before the landing capture, fitted at 1x with
   `rrect-lg` held out, predicted at 2x, refereed under the stops.* §5.51
   declared one steep power on Apple's span law along an ovalized normal;
   §5.52 refereed it on the twelve runs: every checkerboard row rose at
   both scales, no stop fired, the 1x holdout landed within 0.001 of its
   prediction. The three 2x texture rows rose 0.010–0.014 and still miss
   0.93: re-pinned with the mechanism named — the body's depth ramp
   (Decision Log 7), not the lens.
3. *By eye, at every gate.* Sheets at G1 (the 0.3.0 bed), the G2 dry run,
   the G2 landing, the ω A/B and G3, each sent to the user's Retina
   display; the user's readings in Decision Logs 2, 6 and 5 (the lobes and
   the fold; "ω 0.8 is much more similar to original macOS"; "Apple blurs
   less through the glass and is more transparent"). ω 0.8 landed by eye
   against a hair of SSIM — the instrument gap is Deferred, W13 X6 its
   first form.
4. *The 2x body measured on every checkerboard cell for both sides and the
   decision round presented.* §5.49 §7 and §5.55 on the 1x and 2x probes
   (the 2x probe materialised, §5.53); route (a) chosen (Decision Log 5),
   the scale-aware body declared (§5.56), refereed and stopped (§5.57),
   corrected and swept in the renderer (§5.58), and held by the user with
   the ramp as the next body wave (Decision Log 7).
5. *Suites green, goldens re-recorded only where a Decision Log names the
   scene, the canonical matrix rebuilt once, every gap written down.* CI
   green on `7428134` (build · lint · test 24 packages; the three-engine
   integration); on the rebuilt bed with the ratcheted floors, `pnpm -r
   lint` clean and every unit suite green (renderer 357 / 357, platform-web
   341 / 341, calibration 233 / 233, core 302 / 302, react 97 / 97, motion
   162 / 162, geometry 149 / 149, policy 23 / 23), the enforcement test
   27 / 27 and the demo's reference-panel spec 1 / 1 on a real adapter; five goldens re-recorded
   at the G2 landing (Decision Log 4) and again at ω 0.8 (Decision Log 6),
   each behind its isolation hash; X1 once (§5.59 §1, deterministic against
   the referee bed); the gaps in claims §5.55 §3 and §5.58, this Deferred
   list and W13's charter.

**Outcomes.** Enforced floors 11 → 11 (three ratcheted up). The GPU tier's
lens is the reference's field: the instrument's D(u) at both scales, the
corner lobes, the fold, the along-edge stretch (ω 0.8), within 0.9 / 1.3 px
at 2x. The 1x checkerboard texture rows read 0.943–0.999 where the unit
opened on 0.929–0.998; the 2x rows 0.911–0.998 where it opened on
0.901–0.997; `hc-text` up 0.010–0.015. The reference's own parameters are on
file (the layer dump, §5.50): the lens's two profiles, the quarter-scale
buffer, the depth ramp, the two-light rim, the bleed, the shadow's law. The
2x body is understood — one kernel in device pixels, no transmission
term, the ramp — and deliberately not landed. New instruments: the
warp-recovery instrument (`w12lib.py`), the harness's `dump-layers`, the
2x probe bed, the runtime sweep as a fitting instrument.

**Lineage check.** Each child's section is its spec and cites the parent
by construction. Binding content changed once during the wave, by the
user: Decision Log 5 overturned W11 Decision Log 4's "fit at 1x, predict
2x" for the body (recorded there and in the Risks' "nothing 2x-specific
lands without the user choosing a route" — honoured: nothing landed).
G1c was added as a child when the layer tree turned out to be readable
(Tracking Map). X1 executed once at the close with its determinism
checked; X2 at the close (§5.27 amended, the count beside its section);
X3 at G2's referee, the ω A/B and the close, the movers named each time;
X4 on every reference table; X5 at every gate. One piece of advisory
inheritance was overturned with evidence and recorded on the parent (the
Fresnel reading of the rim — the dark line is the outer refraction term
of opposite sign, §5.50 §2, not a transmission collapse).

**Retrospective.** The instrument-first rule paid at every gate: a field
recovered on a known law before the reference was read is why the fold,
the corner lobes and the 2x "different object" could be told apart from
the instrument's own blur, and why the layer dump's numbers could be
checked against captures instead of believed. The declared stop fired on
G3 exactly where it was written (the 2x texture rows) and became a
decision instead of a re-pin — and the wave's largest correction came
from taking the stop seriously: the paper model of the mip chain's heavy
tap over-credited it by the amount that turned a right width into a wrong
weight, and only the renderer-in-the-loop sweep could show it. Carry
forward: fit in the renderer, never on the paper model alone (W13
binding); a metric that scores the band where the eye reads it (W13 X6);
and the reference's own parameters as the first hypothesis, measured, not
assumed.

## Revision Notes

- 2026-09-03: opened.
- 2026-09-03: Decision Log 7 — G3 held at `main`; the depth-ramp round chartered as the
  next body wave in Deferred; the wave moves to recomposition.
- 2026-09-03: RECOMPOSED (claims §5.59). W13 opened from Decision Log 7
  (`2026-09-03-w13-body-depth-ramp.md`).
- 2026-09-03: the Deferred shadow gap measured by W13 X6 (2.4× on the capsule; a gray
  composite against a black multiply); evidence added beside the entry.
- 2026-09-03: the Deferred dot gap measured by W13 G0 (the dark-regime response closes the
  thin surface; not the body); evidence and the sharper shape of work added beside the entry.
