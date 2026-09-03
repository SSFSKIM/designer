# W14 — The outer shadow's colour and law (2026-09-03)

> **Parent:** W13, the body's depth ramp
> (`docs/doperpowers/specs/2026-09-03-w13-body-depth-ramp.md`), by way of
> its Deferred entry "the outer shadow's colour and span law" and its
> Surprises (the X6 baseline, claims §5.60); W13 Decision Log 2 (user-decided
> 2026-09-03: "charter the outer shadow's wave next, and run its measurement
> in parallel with W13"). W13 sits under W12, W12 under the post-v1 wave
> (`2026-08-28-post-v1-wave.md`), where W8 landed the outer shadow this wave
> corrects. **Consumes:** claims §5.11–§5.12 (the shadow as the largest
> unmodelled facet; the shadow axis and its multiplicative normalisation),
> W8's landing (`MaterialOuterShadow` in `packages/renderer-webgpu/src/material.ts`:
> σ 15.55 / offset 7.95 / spread 3.1 CSS px, occlusion 0.285, a black
> multiply on both tiers, lengths span-invariant), §5.50 §2 (the reference's
> shadow block read from its layer tree: `inputShadowRadius` 24 and offset
> (0, 8) constant; `inputShadowAmount` min(0.625·span, 75), `Height`
> 0.4·span, `BlurRadius` 40 from some span ≤ 96, `Opacity` min(0.5, 0.5 −
> (span − 48)/448), `VibrancyContribution` clamp((span − 64)/96, 0, 1),
> `SDRShadowOpacity` 0.08 + (span − 48)/700; the thin material's shadow
> fill α by backdrop — 0.278 on checkerboard / hc-text, 0.285 on photo, 0.30
> on mid-dark, **0.05 on light-solid**, none on dark and impulse; the thick
> material's a constant 0.12), §5.60 (the X6 baseline: the exterior owns
> 52–67% of the GPU tier's whole-crop deficit on the four large checkerboard
> cells at 1x and 69–76% at 2x; the reference's shadow is an affine map of
> the plate with a lift on the blacks, vitrea's a pure multiply; the
> light-solid capsule's shadow at 2.4× the reference's), and the X6 rows
> (`ssimOutside` and its window count on every cell). Three gates in the
> W12/W13 shape and the user's eye at the landing; runs beside W13.

## Purpose

W8 rendered the reference's outer shadow as a black multiply — the
component's own silhouette, offset down, blurred, removing a fraction of
the backdrop's light — and fitted its three lengths and one amplitude on
the active bed, where mirrored pixel pairs over `photo` said multiplicative
and not additive. That description holds where it was measured and misses
two things the bed has since shown. On the thick material the reference's
shadow **lifts the blacks**: on the checkerboard the black squares 2–12 CSS
px outside the contour read 0.041 below the surface, 0.027 at the sides,
0.015 above, where vitrea's stay at 0.000 — an affine map of the plate,
a·plate + c with c +0.039 at the contour decaying to 0 by 24 px, against
vitrea's c ≡ 0 (§5.60 §3). A black multiply cannot lift a black; a colour
composited at low alpha can, and SSIM's luminance term reads a 0.04 lift on
a 0.00 square as ≈ 0.06, which is why half of the large checkerboard
cells' whole-crop deficit at 1x and two thirds at 2x sit outside the
silhouette — more than the band and the interior together, and the reason
the three held 2x texture rows cannot reach 0.93 through W13. The layer
tree names the mechanism: the thick shadow carries a
`VibrancyContribution` that rises from 0 at span 64 to 1 at 160, with its
own blur (40) and extent (`Amount`, `Height` by span) — a blurred copy of
the backdrop, darkened, composited under the shadow, which is gray on the
checkerboard, the backdrop's own hue on `photo`, and nothing on black.

On the thin material the reference's shadow **adapts to the backdrop**:
its fill alpha is 0.278 over the checkerboard, 0.05 over `light-solid`,
none over `dark-solid` — vitrea's is 0.285 everywhere — and on
`light-solid__capsule-button` vitrea's shadow is 2.4× the reference's
integrated darkening at both scales (−0.094 against −0.040 luma at the
contour). That is the user's by-eye gap "the shadow is darker on the
light-solid capsule" (W12 Deferred), and it is W9's thin-regime response
seen from outside the surface: the same backdrop luminance that keys the
face keys the shadow.

This wave measures the shadow as a composite — a black term and a
backdrop-derived term, each with its extent, by span, side, scale and
backdrop — with an instrument validated on vitrea's own captures first,
declares the model, lands it on both tiers under stops, and puts the
result in front of the user's eye. It runs beside W13 on the same bed;
the two touch different passes and different windows.

## Parent-Level Acceptance

- The reference's shadow is **measured as a composite**, not assumed:
  per side, ring, span, scale and backdrop, the black term's alpha and
  the lift (the per-ring affine map of the backdrop, a and c), with the
  backdrop-derived term's colour, blur and extent read where it is
  identifiable (the solids identify the black term alone; the checkerboard
  and `photo` identify the lift; the probes' pitch axis identifies its
  blur) — and the instrument's recovery of vitrea's own W8 shadow (c ≡ 0,
  a = 1 − 0.285·falloff within ±0.005) recorded beside every reference
  table (X4).
- A model is declared **before** the landing capture — the black term's
  alpha keyed on the backdrop luminance the face's response already uses
  (thin regime) and constant above the knee (thick), its geometry
  reconciled between W8's lengths and the layer tree's inputs; the
  vibrant term's contribution, blur and extent by span; both tiers — fitted
  on the calibration cells with the holdouts held out, the twelve rows'
  `ssimOutside`, `ssimMean`, the shadow axis and the solids' level rows
  predicted, and refereed on the full bed under the stops. `ssimOutside`
  rises on every checkerboard cell at both scales; the light-solid
  capsule's shadow lands within 20% of the reference's integrated
  darkening; the three 2x texture-tier `ssimMean` rows meet 0.93 or are
  re-pinned with the mechanism named; no inside row moves.
- **By eye:** the W12 sheet extended with shadow crops — the region below
  and beside `rrect-lg`, `rrect-md` and the capsule on checkerboard,
  light-solid and photo, native | vitrea | signed difference at 3× — at
  the dry run and the landing, sent to the user's Retina display; the
  reading recorded, the landing theirs to call.
- The compare's shadow axis is widened to read the composite (X7): its
  multiplicative normalisation stays as one reading and a two-term ring
  read lands beside it, absent where not identifiable, so the harness
  measures what this wave changes.
- Both tiers carry the geometry and the adaptive alpha (K5-style: one
  profile, two renderers); the CSS tier's vibrant term is Decision Log 1's
  question. Suites green, goldens re-recorded only where the Decision Log
  names the scene, the canonical matrix rebuilt once at recomposition,
  every gap in claims, this Deferred list or the tech-debt tracker.

## Grounding Baseline (the W12 close bed, 2026-09-03)

- vitrea's outer shadow as landed (W8): the group's own field translated
  down 7.95 CSS px, outset 3.1, blurred σ 15.55, applied as an alpha on
  black — the backdrop keeps 1 − 0.285·falloff of its light; the size law's
  `sizeGain` at 0 (the amplitude's span dependence pointed opposite ways
  in the two schemes); reduced transparency at 0.7 of the amplitude
  (measured 0.566); the CSS tier a `box-shadow` of pure black with the same
  three lengths (blur 2σ). Inert over black on both tiers, exactly.
- The reference, as read: W8's fit (σ 15.4–15.9 and offset 6.9–8.1 across
  spans 32–160, both scales in device px ×2; RMS 0.0021 in occlusion on
  the finest cell); the layer tree's block above (§5.50 §2) with the
  thin/thick knee at span 64 and the thin shadow's fill alpha by backdrop;
  and §5.60 §3: the affine lift on the checkerboard (c +0.039 / +0.024 /
  +0.014 / +0.004 at 0–6 / 6–12 / 12–24 / 24–48 px out, a 0.887 → 0.988;
  vitrea a 0.933 → 0.993, c 0), strongest below; the light-solid capsule
  at −0.040 vs −0.094 luma at the contour (0.688 vs 1.630 luma·px per
  column at 1x, identical at 2x); no outward displacement, no blurred copy
  detectable by an *unweighted* blur term in the affine fit (the vibrant
  term's blur is 40 on the layer tree and a σ-40 copy of a pitch-16 checker
  is nearly a constant — which is why the affine fit saw a lift and not a
  copy; the pitch axis is where the blur becomes identifiable).
- Where the deficit sits (§5.60 §2, GPU tier, whole-crop share outside the
  silhouette): 1x `rrect-md` 50%, `-ml` 53%, `-lg` 47%, `glass-over-glass`
  54%; 2x 63 / 63 / 66 / 64%; `ssimOutside` 0.89–0.93 at 1x, 0.78–0.86 at
  2x on those four; the CSS tier's outside 0.74–0.90 (the same shadow). The
  three held 2x texture rows 0.9158 / 0.9113 / 0.9211 against 0.93, floors
  0.9147 / 0.9102 / 0.9201.
- The compare's shadow axis (§5.12): occlusion = (backdrop − rendered) /
  backdrop in linear light per ring and direction, absent below a backdrop
  floor of 0.05 (dark-solid, impulse); a blurred-edge falloff fitted
  against an exponential; no adopted bound. A composite's lift on a black
  square is, by construction, outside what this normalisation can report.
- Instruments in hand: the X6 rows on every cell; the W12 G0 / W13 G0
  warp-and-body instrument (not needed here; the shadow is outside the
  lens); the probe beds at 1x and 2x with their pitch axis; the layer-dump
  tool; the runtime sweep (`sweep.ts`).

## Design

Binding at this level, because only the whole picture settles them:

- **[binding — a composite, decomposed where each term is identifiable,
  with the instrument proven on vitrea first.]** The exterior of every cell
  is read per side and ring as an affine map of the backdrop the capture
  was taken over, y = a·bg + c, in linear light: a solid backdrop
  identifies only a·bg + c together (the black term's alpha and the lift
  trade off on a constant), so the black term's alpha by backdrop comes
  from the solids *and* the lift's absence on them, the lift's amplitude
  from the checkerboard and `photo`, and the lift's blur from the probes'
  pitch axis (a σ-40 copy of a pitch-4 checker is flat; of a pitch-64
  checker it follows the squares). Before any reference number, the same
  code recovers vitrea's own W8 shadow from vitrea's captures: c within
  ±0.005 of 0 and a within ±0.005 of 1 − 0.285·Φ-falloff on every ring and
  side at both scales.
- **[binding — the vibrant term is the backdrop's own light.]** The lift
  is modelled as a blurred, darkened copy of the backdrop composited under
  the shadow (colour = k·blur_σ(backdrop) at alpha α_v, both by span), and
  the hypothesis is tested on `photo` (where the copy is coloured) against
  the checkerboard (where it is gray) and the solids (where it is the
  backdrop's own colour, invisible beside the black term) before any fixed
  colour constant is allowed into the profile. A fixed gray that fits the
  checkerboard and fails `photo` is not the material.
- **[binding — one key for the thin regime.]** The thin material's shadow
  alpha keys on the same backdrop luminance the face's response uses (W9's
  curve, §5.50's table: 0.278 at L 0.21–0.74, 0.30 at 0.06, 0.05 at 0.89,
  none at ≤ 0.012), through the same thickness curve that gates the
  regime; no second luminance statistic is introduced for the shadow.
- **[binding — the geometry is reconciled by measurement.]** W8's
  span-invariant σ 15.55 / offset 7.95 / spread 3.1 and the layer tree's
  `Radius` 24 / offset (0, 8) / `Amount` / `Height` / `BlurRadius` 40 are
  two descriptions of one shadow; the working reading (advisory below) is
  that W8's lengths are the black term's and the `Amount` / `Height` /
  `BlurRadius` 40 are the vibrant term's extent and blur. G0 measures
  which; the declaration carries what was measured, and W8's lengths are
  not refit unless G0 shows them wrong on the cells W8 did not have.
- **[binding — both tiers, and the coordination with W13 (X8).]** The
  geometry and the adaptive alpha land on both tiers from one profile; the
  vibrant term lands on the GPU tier (a coarse-LOD sample of the backdrop
  chain outside the coverage, in the optics pass that already writes the
  shadow alpha) and on the CSS tier only as Decision Log 1 decides. W13
  and W14 referee and land on `main` as it stands the day of the capture:
  whichever lands second re-runs its dry run on the first's bed before its
  landing capture, and its stops are read against that bed.

Advisory, carried into the children:

- The working model of the reference's thick shadow, from the layer tree
  and §5.60: rendered = backdrop·(1 − α_b·F_b(d)) composited with a
  vibrant layer of colour k·blur₄₀(backdrop) at alpha α_v·F_v(d), where
  F_b is W8's blurred-edge falloff (σ 15.55, offset 7.95, spread 3.1),
  F_v the vibrant term's own extent (`Amount` outward, `Height` downward,
  a blurred edge of `BlurRadius` 40), α_b the fill alpha (0.12 thick;
  the adaptive table thin) times `SDRShadowOpacity`-like factors the fit
  resolves, α_v the `VibrancyContribution` clamp((span − 64)/96, 0, 1)
  times an amplitude, and k the darkening (≈ 0.7 from the checkerboard's
  lift of 0.04 at α_v·k·0.5). On the capsule α_v = 0 and only the adaptive
  α_b acts. The first numbers to check: c(d) on the checkerboard should be
  ≈ α_v(span)·F_v(d)·k·0.5, so `rrect-md` (α_v 0.33) should lift a third of
  what `rrect-lg` (α_v 1) does — §5.60's ring fits were on `rrect-lg`;
  `rrect-md`'s c at 0–6 px was +0.024 against `rrect-lg`'s +0.039.
- The GPU tier's implementation sketch: outside the coverage the optics
  pass returns `vec4f(0, 0, 0, shadowAlpha)`; the vibrant term makes that
  `vec4f(colour·α_v', α_b' + α_v' − …)` in premultiplied form with the
  colour a `textureSampleLevel` of the backdrop chain at the LOD whose σ
  is 40 CSS px, at the pixel's own position (the copy is of the backdrop
  beneath the shadow, not under the surface). The chain covers the group's
  padded rect, which is the shadow's reach by W8's padding rule. No new
  pass.
- The CSS tier cannot sample the backdrop outside the element with one
  `box-shadow`; a pseudo-element behind the surface, outset by the vibrant
  extent, with `backdrop-filter: blur(40px) brightness(k)` and a mask
  gradient would carry it. Feasible, and a second element per surface —
  Decision Log 1's question.
- The shadow axis (X7): per ring and direction, beside the occlusion
  ratio, the affine pair (a, c) against the backdrop raster, absent where
  the ring's backdrop has no contrast to identify them (a solid). Its
  baseline on the W12 close bed lands with it.
- The bleed term (§5.50 §2: a pulled-in, blurred, darken-blended copy of
  the outside backdrop over the edge, opacity (span − 64)/192) is the same
  family — a blurred backdrop copy composited near the contour, inside
  rather than outside. Out of scope; the instrument built here reads it,
  and the Deferred entry says so.

## Children

### G0: The instrument and the measurement — spike (deliverable: findings)

- **Purpose:** the per-ring affine instrument, validated on vitrea's
  captures, then the reference read: (1) a and c per side (below, above,
  left, right) and ring (0–3, 3–6, 6–12, 12–24, 24–48 CSS px) on every
  checkerboard, `photo` and solid cell of the canonical bed at both scales,
  light and dark schemes; (2) the thin regime's alpha by backdrop on
  `capsule-button` and `rrect-sm` (seven backdrops, both schemes) against
  §5.50's table; (3) the lift's blur from the probes' pitch axis on the
  three large spans (the modulation of c with the checker pattern by
  pitch); (4) the lift's colour on `photo` (a and c per channel, or in
  OKLab) against a blurred copy of the photo; (5) the geometry — the black
  term's falloff σ, offset and spread re-read from the solids and the
  whites, and the lift's extent from c(d) by side — against W8's lengths
  and the layer tree's `Amount` / `Height` / `BlurRadius`; (6) the
  compare's shadow axis on the same cells as a cross-check; (7) the
  light-solid capsule's 2.4× decomposed. Findings in
  `results/2026-09-03-w14-shadow/g0/`.
- **Acceptance:** the validation within ±0.005 on a and c on every ring and
  side of `rrect-lg`, `rrect-md` and `capsule-button` at both scales; the
  reference tables with the recovery beside them (X4); a "what the
  declaration should carry" section and a draft ledger section.
- **Edges:** none. **Track:** spike; one worker, dispatched at the charter.

### G1: The declared model and its dry run — controlled

- **Purpose:** the composite as G0 measured it, on both tiers; the profile
  constants (the adaptive alpha's anchors, the vibrant term's amplitude,
  darkening, blur and extent by span; W8's lengths kept or corrected);
  fitted on the calibration cells with the holdouts held out; the twelve
  rows' `ssimOutside`, `ssimMean`, the shadow axis and the solids' level
  rows predicted by the runtime sweep; the X7 rows landed in the harness
  with their baseline; the sheet at the dry run.
- **Acceptance:** the declaration in claims — model, constants, stops,
  predictions, both tiers — before any landing capture; the sheet sent; the
  user's reading recorded.
- **Edges:** blocked-by G0. **Track:** controlled.

### G2: The landing and its referee — controlled

- **Purpose:** implement (the GPU tier's vibrant sample and adaptive alpha;
  the CSS tier's adaptive alpha and whatever Decision Log 1 decides for
  its vibrant term; `tier-coherence`; goldens behind the isolation proof),
  the twelve runs to a scratch matrix, the referee under the stops, the
  sheet at the landing, the user's eye.
- **Stops (declared here, refined by G1 with numbers):** (S1) no inside
  row (`ssimBand`, `ssimInterior`) moves by more than 0.001 on any cell
  unless the declaration says the shadow reaches under the surface, in
  which case as predicted; (S2) `ssimOutside` rises on every checkerboard
  and `photo` cell at both scales; (S3) the solids' shadow profile (the
  shadow axis, and X7's pair) within the declared tolerance of the
  reference on `light-solid` and `mid-dark-solid` at every span, and the
  light-solid capsule within 20% of the reference's integrated darkening;
  (S4) the three 2x texture rows meet 0.93 or are re-pinned with the
  mechanism named; no 1x row falls more than 0.002 below its W12-close
  value; (S5) `dark-solid` and `impulse` cells unchanged (the shadow stays
  invisible over black on both terms); (S6) the CSS tier moves only as G1
  predicted; (S7) a hard stop is a landing the user's eye rejects.
- **Edges:** blocked-by G1; X8 with W13. **Track:** controlled; the
  landing is the user's call.

## Cross-Child Contracts

- **X1 — the canonical rebuild.** As W12 X1, once at recomposition; the
  demo's reference-panel fixture re-copied. Owner: parent.
- **X2 — floor bookkeeping.** As W11/W12 X2. Owner: parent.
- **X3 — the untouched bed.** The whole-bed scan against the bed the
  landing capture was taken on; every cell moved by more than 0.005 named.
  Owner: parent.
- **X4 — the instrument's validation travels with every reading.** Owner:
  G0; G1 binds.
- **X5 — the by-eye sheet.** W12's script and layout extended with the
  shadow crops (below and beside the surface, 3×), under
  `results/2026-09-03-w14-shadow/sheets/`, at G1's dry run and G2's
  landing. Owner: parent.
- **X6 — the band-windowed rows** (W13's): `ssimOutside` is this wave's
  primary row; `ssimBand` / `ssimInterior` its nulls. Shared with W13;
  neither wave changes the split.
- **X7 — the shadow axis widened.** The per-ring affine pair (a, c)
  against the backdrop raster, per direction, beside the occlusion ratio;
  absent where the ring's backdrop is a constant; recorded from G1 on,
  baseline on the bed of the day; adopted at G2. Owner: G0 defines, G1
  lands, parent adopts.
- **X8 — coordination with W13.** Each wave's dry run and referee are
  taken on `main` as it stands that day; the second to land re-runs its
  dry run on the first's bed before its landing capture and reads its
  stops against that bed; neither wave's referee is read while the other's
  landing is between its capture and its merge. Owner: both parents
  (this session).

## Ordering & Dependency Map

G0 → G1 → G2 → recomposition, beside W13's G0 → G1 → G2. G0 starts at the
charter (user-decided). X8 orders the two landings.

## Risks & Mitigations

- **The lift and the black alpha trade off on a solid backdrop.**
  Mitigation: decomposition by backdrop (binding); the solids fix the black
  term, the structured backdrops the lift.
- **The vibrant term's blur is invisible to an affine fit on pitch 16.**
  Mitigation: the probes' pitch axis (binding); a σ that cannot be
  identified is reported as a range, not a number.
- **W8's "multiplicative, not additive" reading conflicts on its face.**
  It does not: on `photo` a copy of the backdrop's own light tracks the
  backdrop's ratio, which is what W8's mirrored pairs saw. Mitigation:
  G0's `photo` read (a per channel) says so or not with numbers.
- **The CSS tier's vibrant term is a second element per surface.**
  Mitigation: Decision Log 1; the tier's rows are predicted for whichever
  answer stands.
- **Two waves on one bed.** Mitigation: X8; the GPU is shared and no two
  captures run at once.
- **The frame-unstable CSS cells** (§5.59 §1, §5.60 §1): below every bound;
  the referee's scan names them if they move.

## Deferred / Out of Scope

- The bleed term (§5.50 §2), the shadow's inside-the-contour sibling —
  read by X7's instrument if pointed inward; its own round.
- The inner shadow (`shadowDepth` / `shadowAlpha`) — untouched.
- The shadow under the dark scheme beyond what G0 reads (the layer tree's
  dark-scheme dump needs a scheme flag, W12 Deferred).
- The `sizeGain` seam (W8: opposite span dependence in the two schemes) —
  if G0's adaptive alpha explains the opposite signs (the thin regime's
  fill alpha on the dark scheme's backdrops), it is retired with the
  declaration; otherwise it stays at the identity.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | one worker, dispatched 2026-09-03 at the charter; `results/2026-09-03-w14-shadow/g0/` | IN PROGRESS |
| G1 | — | blocked-by G0 |
| G2 | — | blocked-by G1; X8 |

## Decision Log

### Decision Log 1 — the charter, the cut, and what the user decides (2026-09-03; the charter and the parallel run user-decided)

**Decided (user, 2026-09-03):** "charter the outer shadow's wave next, and
run its measurement in parallel with W13." Chartered from W13's Surprises
and Deferred (claims §5.60); G0 dispatched at the charter.

**The cut.** Three children in W13's shape, for the same reason (three
verification strategies); the measurement runs now because it lands
nothing and every later decision needs its numbers. Rejected: folding the
shadow into W13 (a different pass, a different window, a different
instrument — and W13's stops are written so the shadow is a null there);
a decision round on the CSS tier as a child (one question, below).

**Binding rules.** The five in Design: decomposed where identifiable, the
instrument proven on vitrea first; the vibrant term is the backdrop's own
light; one key for the thin regime; the geometry reconciled by
measurement; both tiers and X8.

**What the user decides at this gate** (each with the recommendation):

1. *Approve the cut and the binding rules.* Recommended; G0 is measurement
   only.
2. *The CSS tier's vibrant term.* (a) The CSS tier carries the geometry and
   the adaptive alpha (its `box-shadow` stays black; the thin regime's
   alpha and any corrected lengths land) and the vibrant term is deferred
   to a follow-up with the two-layer CSS body, since both need a second
   element per surface. (b) A pseudo-element with `backdrop-filter`
   carrying the vibrant term lands in this wave. **Recommended: (a)** —
   the adaptive alpha is most of the CSS tier's shadow gap on the thin
   spans, the vibrant term's share on the CSS tier is measured by G0 before
   (b) is costed, and one new element per surface is a layering decision
   the CSS body wave should make once for both.
3. *Adopted bounds.* `ssimOutside` and X7's pair get bounds at G2's landing
   from the bed, as X6 planned. Recommended as written.

Held for the user beyond this gate: the by-eye reading at G1's dry run and
the landing call at G2; the landing order under X8 if both waves declare
in the same week.

## Surprises & Discoveries

(open)

## Outcomes & Retrospective

(open)

## Revision Notes

- 2026-09-03: opened from W13 Decision Log 2 / claims §5.60.
