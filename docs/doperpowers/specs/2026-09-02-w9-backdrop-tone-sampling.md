# W9 — Backdrop tone sampling under size × spatial frequency

**Opened 2026-09-02.** Child of the post-v1 wave
(`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`), chartered there as the
next wave's opener by Decision Log 22 and the Deferred section "W9 — backdrop
tone as a function of surface size (the next wave's opener)". Grounded in
claims §5.26 (the measurement), §5.27 (the thirty-three floors this spec
exists to remove), and §5.13's supersession note (the tint gamut clip and this
mechanism are one problem).

This spec opens the next wave, and it opens it alone. The rest of that wave's
cut — canvas enlargement, the pressed pose + motion-metrics harness, W7's
two-axis rework, the low-res GPU shadow pass, the per-corner radii, the
inactive-pose material — deliberately waits: W9's outcome moves the floors
landscape those children would be cut against, and a cut drawn before the
probe answers would be drawn against numbers about to change.

## Purpose

Thirty-three enforced rows on the two light-standard profiles are regression
floors instead of met claims, all through one measured mechanism: image
similarity degrades as surface size and backdrop spatial frequency combine,
because both tiers feed an *averaged* backdrop to a *non-linear* tone
response, and averaging before a non-linearity is not the averaging after it.
W9 answers the modelling question Decision Log 22 chartered — **how backdrop
tone should be sampled as a function of surface size over structured
content** — on both tiers, and discharges the floors by fix.

## What counts as done (binding, inherited from the charter)

- The thirty-three floors in §5.27 **removed rather than re-pinned**, each
  with its adopted bound restored as a met claim. A floor re-pinned at a
  better value is progress and is recorded as progress; it is not the charter
  discharged.
- Both tiers. The CSS tier is worse (one mean per source) but the GPU tier
  misses too, so locality alone is not the remedy and neither is restating
  the cover-fit mapping in platform-web.
- The tint coherence rows ride the same acceptance: the tone response picks
  the tint colour, and how saturated that pick is decides how hard
  `cssTintColor` clips it (§5.13 supersession). One problem, one fix, not two
  workstreams.
- **Standing caution (binding):** `sizeOcclusionGain` was fitted in the last
  cascade and the residual stayed size-monotonic after it — on holdout. A
  second scalar size gain is the obvious move and is presumptively the wrong
  one; the evidence says the mechanism is in how the backdrop is *sampled*.
- **Out of scope** (standing parent exclusions, unchanged): the WebGL2 tier;
  topology-changing morphs.

## Grounding (read from the code at open, 2026-09-02)

1. **CSS tier** — `packages/platform-web/src/backdrop-tone.ts`: one
   linear-light mean per *source*, fed to the non-linear tone map. The file's
   own header nominated the cross-tier bound as its referee and records that
   the referee has ruled against it.
2. **GPU tier** — `packages/renderer-webgpu/src/wgsl/optics.ts` carries TWO
   averaged inputs to non-linearities:
   - the W7 backdrop adaptation reads `toneColour` — the backdrop **source's
     own average**, host-measured — plus a size term (`toneAdapt.z · sizeK`).
     Same coarseness class as the CSS tier.
   - the tint tone map reads `backdropLuma` from the per-pixel **blurred**
     backdrop sample (optics.ts:271–290, 365). Per-pixel in position but
     pre-averaged at kernel/LOD scale — and the LODs are size-coupled, so a
     larger surface feeds a *coarser* average to the same non-linearity.
     This is a concrete candidate account of the GPU tier's size
     monotonicity; the probe treats it as a hypothesis about vitrea, not a
     fact about the reference.
3. **A dormant signal already exists.** The GPU analysis reduction
   (`renderer-webgpu/src/analysis.ts`) computes `variance` and `edgeDensity`
   (mean gradient magnitude per texel), low-passes each through its own
   driver, and exports them — and nothing downstream consumes either. If the
   answer needs a spatial-structure input, the GPU tier already delivers one
   to the CPU every readback.
4. **The scene machinery is parameterized data end to end.** Backgrounds in
   `apps/reference-apple/scenes.json` carry kind + parameters (`checkerboard`
   has `cell: 16`, `text-rows` has `rowHeight: 14` / `barHeight: 6`,
   `impulse` has `size`/`spacing`, `synthetic-photo` is seeded), the native
   harness decodes them at launch, and the web tier consumes native-exported
   backdrop bitmaps by manifest name rather than drawing its own. A pitch
   sweep over existing kinds is scenes.json entries only — **no rebuild, no
   TCC re-grant**. A new background *kind* would need Swift code and a
   rebuild, so the probe uses only existing kinds.
5. **Geometry available.** Components span 64×32 → 280×160 (a 21.9× area
   range) on a 320×200 canvas; `rrect-lg` nearly fills it, so larger sizes
   wait on the separately-deferred canvas enlargement. The probe works within
   the 22× range and lets the pitch axis supply the additional decade of
   pitch-to-span ratio.

## Inherited constraints (binding)

- **X1, with a fresh split.** The thirty-three floored rows are spent
  holdout — the old holdout column was opened four times, stated plainly in
  the parent. They are never fit against. Fitting happens on the NEW scenes'
  calibration set under a declared protocol (grid + objective committed
  before running); the new split gets ONE holdout read; the floored rows on
  the frozen bed serve as the final referee, which is legitimate precisely
  because nothing was ever fitted to them.
- **The DL21 capture doctrine, all five items.** Unlocked + wake attested per
  cell and the per-cell audit is the completion criterion; the idle bar is a
  range; the 6-second neutral reset interstitial; unanimity under the
  structured-vs-incidental rule with the bimodality arm active; seventeen
  runs before any bed **freezes into the enforced suite** — a bed frozen on
  fewer records the confidence bought.
- **Provenance:** `resolvedMaterialSha256` on every capture (§5.29 reading
  for anything older).

## Phase 1 — The probe (declared before it runs)

The probe measures what the *reference* does. Not what fix makes vitrea's
numbers better — what Apple's material actually renders over structured
content as size and pitch vary. The last wave's lesson is explicit: three
times the honest answer was new evidence rather than a refit, and the
standing caution above says the failure is in sampling, which only a
measurement of the reference can characterize.

### Hypotheses, recorded before capture

- **H1 — map-then-average.** The reference's interior over structured content
  matches the spatial average of the per-region tone response
  (w·tone(dark) + (1−w)·tone(bright)), not tone(mean). Prediction: the
  checkerboard interior sits at the average-of-maps at every pitch, with no
  pitch dependence beyond edge effects.
- **H2 — band-limited input.** The tone input is the backdrop low-passed at a
  size-coupled scale. Prediction: the interior is a function of the
  pitch-to-span ratio — not of pitch or span alone — collapsing to
  tone(mean) where pitch ≪ the coupling scale and approaching the
  per-region response where pitch is comparable to it.
- **H3 — encoded-space averaging.** The averaging happens in an encoded or
  perceptual space rather than linear light. Prediction: the checkerboard
  interior matches tone(encoded mean), which for a bimodal backdrop is
  numerically far from both tone(linear mean) and the average-of-maps, so
  the three hypotheses separate cleanly on the same cells.
- **H4 — a contrast term.** Backdrop structure is a second input in its own
  right: the material responds differently to two backdrops with the *same
  mean* and different contrast. Prediction: the equal-mean pair below
  diverges even at pitches where H2 predicts collapse. (If H4 survives, the
  dormant `edgeDensity`/`variance` channel is the natural implementation
  input.)

These are not mutually exclusive — H2 and H4 in particular can both hold.
The probe's job is to score each against the reference, not to elect one by
forced choice.

### The discriminating grid (data-only scene additions)

- **Pitch axis:** `checkerboard` at cell ∈ {4, 8, 32, 64} joining the
  existing 16, black/white.
- **Equal-mean pair (H4):** two checkerboards at cell 16 whose linear means
  match (the existing black/white pair's 0.5) at two contrasts — full
  contrast vs. a low-contrast grey pair chosen to the same linear mean.
- **Second structured family (transfer check):** `text-rows` at rowHeight
  {7, 28} joining the existing 14 — anisotropic structure; whatever law fits
  the checkerboard must transfer or the law is a checkerboard fit.
- **Controls:** `light-solid` and `photo` — the null cases §5.26 measured
  flat.
- **Size axis:** `rrect-sm`, `capsule-button`, `rrect-md`, `rrect-ml`,
  `rrect-lg` — the 22× area range.
- **States/tints:** `rest` only; untinted, plus orange tint on
  `capsule-button` (the tint pick rides the same input; §5.13 unification).
- The exact cell list and the new calibration/validation/holdout split are
  declared in the probe manifest **before the first run**, alongside the
  scoring statistic for each hypothesis.

### Protocol

The DL21 winning protocol: 6-second neutral reset before each cell, unlocked
+ wake attested per cell, the per-cell audit as the completion criterion,
bimodality arm active. Any state-ambiguous cell that a hypothesis score
depends on gets a targeted top-up before scoring. Run count per Decision
Log 1 (below); the seventeen-run bar applies when a bed freezes into the
enforced suite, which the probe does not do — the probe's product is
findings, and its runs record the confidence they bought.

The campaign needs the same machine-cooperation set as the last wave —
unlocked throughout, screen lock and display sleep disabled, wake assertion
held — but **no TCC re-grant**, because nothing rebuilds.

### What would stop it

- A reference measurement no declared hypothesis fits → back to the design
  table with the measurement recorded; the model round runs on what was
  measured, not on a forced fit.
- A two-state epidemic on the new backdrops (the sweep's convergence was
  measured on the old bed's backdrops) → the doctrine question reopens
  before any hypothesis is scored.

**Status: COMPLETE 2026-09-02.** Seven runs (five declared + two top-ups
the bimodality arm demanded for four load-bearing two-state cells), every
run 56/56 attested by the per-cell audit; neither stop condition fired.
Findings in claims §5.31; the materialized majority-state bed with per-cell
state shares at `packages/calibration/results/2026-09-02-w9-probe/`. The
verdict: **encoded-space averaging (H3) wins at RMS 0.0400** — 2.68× better
than the current model, predicting the equal-mean pair's direction and
80–90% of its magnitude at every size; pitch is a null axis (H2 dissolved);
H4 survives only as a ~0.01 second-order remainder, recorded and not
modelled. One capture incident: a focus steal by Chrome aborted the top-up
preflight once ("window not key"); a synthetic Finder activation cleared
it — no HID input, idle guard unaffected.

## Beyond the probe (advisory sketch — each step opens with its own decision round)

2. **The model round.** A Decision Log entry with the probe's numbers; pick
   the sampling model both tiers implement. Candidates as of open (to be
   revised by the probe, not preserved against it): the GPU tier moves the
   non-linearity inside the per-pixel path (map-then-average, which its
   shader is one expression away from); the CSS tier approximates the same
   integral with richer statistics from its existing single read — a small
   histogram in place of one mean — so the two tiers implement one law at
   two fidelities; a variance/edge term only if H4 survives the probe.
3. **Implement** behind the material-profile seam, both tiers.
4. **Fit** on the new calibration cells under a declared protocol;
   validation; ONE read of the new holdout.
5. **The referee.** Re-measure the thirty-three floored rows on the frozen
   bed. Floors come off row by row where the adopted bound is met; a row
   still unmet keeps its floor with the improvement recorded. Claims §5.27
   and the `backdrop-tone.ts` header update to the outcome either way.
6. **Gate updates** if new scenes join the enforced suite — the
   seventeen-run freeze applies there, not to the probe.

## Decision Log

1. **The opening round (2026-09-02, user-approved, all three as
   recommended).** (a) **Probe-first**: the reference is measured before any
   model is designed — declared hypotheses, new pitch-swept scenes, no
   fitting. Model-first was rejected because the failing cells are spent
   holdout, so a candidate checked against them proves nothing, and the
   parent's lesson stands: three times the honest answer was new evidence
   rather than a refit. (b) **Five runs plus targeted top-ups** under the
   DL21 winning protocol, bimodality arm active; the seventeen-run bar
   applies only when a bed freezes into the enforced suite, which the probe
   does not do — its runs record the confidence they bought, and any
   state-ambiguous cell a hypothesis score depends on is topped up before
   scoring. (c) **The campaign runs today**: the kit (scene entries, probe
   manifest with declared split and scoring statistics, chain prep) is built
   and verified first, then the user is pinged for the machine window —
   unlocked throughout, screen lock and display sleep off, wake held, no TCC
   re-grant needed since nothing rebuilds.

2. **The model round (2026-09-02, user-approved as recommended).** The
   tone axes' input becomes the ENCODED-SPACE mean of the backdrop behind
   the surface, on both tiers — the probe's winning model, adopted as an
   averaging-space swap with no new constants. H4's ~0.01 remainder stays
   unmodelled (the standing caution); the confirm-on-a-second-profile
   option was declined on the mechanism's scale-free record. Implementation
   shape, from the probe's own evidence: the reference reads
   **per-footprint**, not per-source — the pitch-64 `rrect-sm` cell whose
   footprint sits inside one uniform white cell rendered white-adapted
   (0.9632, footprint-predicted 0.9713) where any source-mean input would
   have predicted ~0.61. So: the CSS tier's read swaps to an exact
   encoded-space mean at its existing per-source granularity (its
   granularity limit stands as documented); the GPU tier's analysis
   reduction gains an encoded-mean statistic for the source-level tone
   input, and the per-pixel path carries the source-level correction ratio
   so locality is preserved while the mean matches the model exactly.
   A dedicated encoded-space pyramid for true per-footprint GPU means is
   named as the escalation if the referee demands it, not built
   speculatively. Then: web captures of the probe scenes, the declared
   verification (nothing tuned unless verification misses, and then only
   under a declared grid), ONE read of the probe holdout, and the
   thirty-three floors as the untouched referee.

3. **The form round (2026-09-02, user-approved as recommended).** The
   refit sweep falsified the single-smoothstep mix form under §5.32's
   pre-stated condition, and the endpoint diagnostic (claims §5.33)
   showed the failure is the TARGET, not the curve: six cells need
   strengths outside [0, 1] because the reference adapts toward the
   material's own light/dark appearance, which coincides with the
   backdrop tone only on dark-solid. Adopted: **the response-curve
   law** — the interior tone becomes `R_size(encodedMean)`, the
   monotone (Fritsch–Carlson) curve through the three solid anchors'
   settled levels, with the anchor levels as functions of size. RMS
   0.0337 on the probe calibration bed with zero fitting beyond the
   probe's anchors, against the falsified form's best 0.1063. The
   two-sided-mix alternative was declined (reconstructs the same curve
   indirectly with more constants); keep-and-re-pin was declined as a
   charter breach.

   Implementation shape (binding where stated):
   - **The mechanism splits in two.** (a) THE TONE SOLVE (new): per
     pixel, evaluate `R(toneX, sizeK)` and shift the scheme NEUTRAL's
     luma so the nominal composited interior mean lands on R — nominal
     mean `M₀ = (1−α)·bgLinear + α·neutralLuma`, solved before the
     collapse mix and compensating the collapse's own mean pull so the
     two never double-count. Chroma is untouched; the author tint
     applies after, per the composition contract's existing order.
     (b) THE COLLAPSE MIX (unchanged): the existing smoothstep-gated
     convergence onto the backdrop tone keeps its mechanism and its
     constants — its validated domain is exactly the near-black knee
     (byte-identical dark-solid collapse, the near-binary size snap),
     and on structured backdrops it is already zero. Binding: the
     response law owns the interior MEAN; the collapse mix owns
     TEXTURE loss; neither reaches into the other's axis.
   - **Constants added: the response surface's anchors.** Three anchor
     inputs (the solid anchors' encoded means, 0.1104/0.2706/0.9505)
     and per-anchor level rows as functions of sizeK, fitted to the
     probe's settled levels (sm/md/lg per anchor) plus the canonical
     capsule collapse evidence on the dark row — the dark row's size
     dependence is a steep knee and the row fit must carry it (claims
     §5.33). Named profile constants, both tiers, one document.
   - **Both tiers, one law.** GPU: in-shader solve (toneX, backdrop
     linear mean, neutral, α, sizeK are all present or one uniform slot
     away). CSS: the same formulas on the layer model at its documented
     per-source granularity.
   - The known remainder (~0.05–0.08 on the smallest footprints over
     structured backdrops) stays unmodelled THIS round; the referee
     (33 floors) is the arbiter, and a second-order term is a later
     declared round only if floors demand it. Verification order
     unchanged: probe-bed re-verify, validation read after the
     constants land, ONE probe-holdout read at round end, then the
     frozen-bed referee.

## Revision Notes

- 2026-09-02 (the refit falsified the mix form): the declared 64-point
  W7 sweep completed and its falsification condition FIRED — no grid
  point brings solids and structure inside 0.05 together (claims §5.33).
  The endpoint diagnostic behind it is stronger than the clause
  anticipated: six cells need strengths outside [0, 1] entirely, so the
  mix's TARGET (collapse onto the backdrop tone) is wrong, not just the
  smoothstep in front of it — the reference adapts toward the material's
  own light/dark appearance, which coincides with the backdrop only on
  dark-solid, the background W7 was fitted on. The candidate the clause
  named — interior tone as the anchored response curve of the encoded
  mean — evaluates at RMS 0.0337 on the same bed with no fitting beyond
  the probe's anchors. Decision Log 3 (the form round) is OPEN; the
  decision is the user's per this spec's phase-gating rule.

- 2026-09-02 (the probe reported): Phase 1 COMPLETE the same day it was
  chartered — seven attested runs, verdicts under the declared rules,
  claims §5.31. The winning model is one nobody proposed at open in this
  form: the reference's tone input behaves as the backdrop's ENCODED-space
  mean, the exact averaging convention both tiers were deliberately built
  to avoid. The advisory model-candidate sketch in "Beyond the probe" is
  OVERTURNED in part by this evidence: per-pixel map-then-average on the
  GPU tier (P1) is dominated by the encoded-mean input and is no longer
  the leading candidate; the CSS histogram idea survives only as the
  mechanism for computing an encoded mean it already had. Decision Log 2
  carries the model round.

- 2026-09-02 (opening): spec authored at W9 open, grounded in a fresh read of
  both tiers' code paths, the dormant analysis stats, and the scene
  machinery's parameterization. The parent's Tracking Map row updates from
  "not cut" to this spec's path.
