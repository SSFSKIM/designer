# W49b — separate transmission, bandwidth and the remaining dark texture regressions (draft, 2026-10-08)

## Purpose

The dark glass at Apple's 0.25 setting should transmit the structure Apple transmits without paying
for it with new mistakes elsewhere. W49a removed the opaque thick body; it did not identify a
material that repairs the remaining fifteen authorised regressions. **W49b's proposed success is
all fifteen repaired against their own historical references, with no new cell traded for them.**
A smaller list is not by itself success, and a better aggregate cannot overrule a cell's protection.

**Status: GROUNDING ONLY; DRAFT FOR THE PARENT.** Based on `98a4fdbbf`, current dark generation
`b2d074d2df24-940384c06f73`. No runtime source, shipped material, canonical matrix, native fixture,
or adopted bound changed. The Decision Log remains open. Neither this draft nor its diagnostic
renders authorises implementation, native capture, fitting, publication or a release.

The recommendation is **one identification wave with separate ladders and one joint landing rule**,
not a supposedly easy thin-cell sub-wave. The existing thin levers fail separation on the measured
controls. The strongest thick-body family is **D plus span-selective second-tap bandwidth W**, not
a share-only P. D separates the transmission knot from the scatter knot; W changes spatial
bandwidth rather than scaling every transmitted frequency together. The thin and low-contrast
mechanisms remain unresolved. G1 is conditional on G0 finding a separating route for them too;
there is no present claim that D+W alone can repair all fifteen.

## Progress

- [x] Grounding: frozen install and workspace build; current owner/cuts and W49a F2–F5 read.
- [x] All fifteen entries and all 24 photo / three 2x inactive fine cells attributed; pixels inspected.
- [x] Four prospectively recorded exploratory batches: ten candidates, fourteen scale-runs,
  342 gate-cell renders, classifying census passed before each launch. No referee/holdout render.
- [ ] Parent rules scope, families, native experiment and the proposed landing contract below.
- [ ] G0: prospective declaration, identity proof, separating ladders and identifying native bed.
- [ ] G1: fit, frozen gate, one prediction/blind exposure if admitted, seal and publication.
- [ ] G2: owner-test landing, evidence tree and release chain, or close at the finding.

## Grounding and evidence

Evidence root: `packages/calibration/results/2026-10-08-w49b-grounding/`.
`attribution.json` names every authorised cell's native/current/reference readings, B and source
hashes; `sheet-1.png` through `sheet-9.png` cover all fifteen plus every named photo and 2x inactive
fine cell. `probe-readings.json` reads the exploratory renders, using T1-low for the T regression
clause, never an `away` label in place of error growth. `probes*.json` records each batch's question
and predictions before its renders. These are adaptive **grounding**, not a predeclared fit.

T1 is the interior standard deviation of linear luminance over the native silhouette. B is the
existing cell's `max(one code, twice the repeat bar)`. A listed regression is repaired when
`|candidate-native| - |historical reference-native| <= B`; that does not mean native fidelity is
closed. All growth below is in B. The two impulse-ml entries use W48's `b2d074d2df24`; the other
thirteen use W46's `d0219cd684bf`. None uses W49a merely because W49a is current.

### F1 — the fifteen are five mechanisms, not one knob

| scale | cell (all dark 0.25 WebGPU) | native | current | current growth / reference | attribution |
| --- | --- | ---: | ---: | --- | --- |
| 1x | checkerboard-32 lg rest | .058407 | .020268 | +2.979 / d0219 | shared scatter/transmission top, plus scale gain |
| 2x | checkerboard-32 lg rest | .055590 | .026031 | +2.714 / d0219 | same |
| 1x | checkerboard-64 lg rest | .085648 | .029153 | +1.552 / d0219 | same |
| 2x | checkerboard-64 lg rest | .084605 | .034312 | +1.713 / d0219 | same |
| 1x | hc-text-28 lg rest | .046004 | .026157 | +1.393 / d0219 | same |
| 2x | hc-text-28 lg rest | .041917 | .027650 | +1.343 / d0219 | same |
| 1x | checkerboard-lc16 md rest | .021654 | .034761 | +2.662 / d0219 | mid-span transmitted contrast AND a separate level error |
| 2x | checkerboard-lc16 md rest | .023019 | .036595 | +2.914 / d0219 | same; every far-span law has zero authority here |
| 1x | impulse capsule rest | .019766 | .025321 | +2.261 / d0219 | opened thin transmission and body/edge sampling |
| 2x | checkerboard capsule inactive | .050076 | .038284 | +2.786 / d0219 | receded thin ramp suppresses canonical-pitch structure |
| 2x | checkerboard capsule inactive-tint-orange | .065004 | .053912 | +1.927 / d0219 | same; crossing Apple is not automatically repair |
| 2x | checkerboard-32 lg inactive | .041221 | .030508 | +1.082 / d0219 | read-9 prediction miss: insufficient coarse transmission |
| 1x | impulse ml inactive | .000555 | .003953 | +2.372 / b2d074 | transmitted impulse energy, opposite direction to coarse deficit |
| 2x | impulse ml inactive | .000849 | .003965 | +2.628 / b2d074 | same |
| 2x | impulse lg inactive | .000587 | .002261 | +1.093 / d0219 | same; its mean is also too dark |

Here `lg`, `ml`, `md`, `sm`, `capsule` abbreviate `rrect-lg`, `rrect-ml`, `rrect-md`,
`rrect-sm`, `capsule-button`; full scene identities are in the machine table.

**The eye corroborates, and adds to, these attributions.** The six active thick cells have flatter,
wider structure than Apple; the text's dark bars lose contrast. The lc16 cells are darker AND more
contrasty than Apple: native/web means are .259394/.199091 at 1x and .259813/.200861 at 2x.
The same-pitch full-contrast md checker is already near Apple's T1 (.064827 vs .061594 at 1x,
.070453 vs .069371 at 2x). A global frequency filter cannot assume these two backdrops want the
same correction. The inactive impulses have narrow bright dots over a body Apple renders broader
and quieter; at lg the current mean is .003274/.003815 against .009130/.009115. Width alone is
not a claim to repair that level. The checker capsule's distortion/edge structure also differs;
repairing its T1 does not certify its optical shape.

### F2 — the easy thin levers do not separate the protected cells

- Active thin start .72 -> .60, 1x: impulse capsule .025321 -> .024013, still +1.289 B against
  d0219. Six new >B costs against current, including checker32 sm +1.866 and checker capsule
  +1.792. The 45-cell gate read protects the whole affected rest population.
- Receded 2x thin start .40 -> .70: plain checker capsule .053291, repaired at +.241 B; the orange
  twin crosses to .075745 and remains +1.845 B, **not repaired**. Impulse capsule grows +8.772 B,
  hc-text sm +4.988, lc16 capsule +1.863 against current.
- W47's existing body fine tap, re-read rather than presumed useless: active share .5 / sigma 3
  repairs the 1x impulse (.021301; -.726 B historical) but causes nine new >B costs. Receded
  thin-start .70 plus fine share 1 / sigma 4 at 2x protects the impulse but loses both checker
  targets (.032363 / .045211). These finite points do not prove global infeasibility; they do
  rule out presenting either tested lever as an isolated repair.

### F3 — bandwidth is a separator that share alone is not

The current secondary deep tap is 5 CSS px at both scales, share .25. On 2x, far-share delta
-.125 repairs the lg impulse (+.764 B historical) but the already-repaired coarse checker64
returns to +1.057 B historical. Delta +.125 helps coarse texture and worsens impulse. Width 8
at held share repairs all three W49a impulses, but creates thin/mid costs and returns checker64
lg at 2x to +1.386 B historical. A width/share companion does not restore coarse response at
both scales: the primary deep sample is a scale-dependent pyramid, not the same Gaussian at
both scales, so the sign of a share change need not transfer.

**The separating control is width 9 plus receded far alpha .09**, at held share .25. This was a
fourth, explicitly adaptive grounding batch, not a selected fit:

| cell | 1x T1 / historical growth | 2x T1 / historical growth |
| --- | --- | --- |
| impulse ml inactive | .003107 / +.849 B | .002984 / +.898 B |
| impulse lg inactive | .003236 / +.072 B (protected) | .001879 / +.429 B |
| checkerboard-64 lg inactive | .028800 / -.039 B | .036525 / +.487 B |

Every rendered ml/lg gate cell stays inside B of current, including text, fine checker and photo.
The three / five new >B costs at 1x / 2x are **all at spans <=96**. That is the empirical case for
restricting the bandwidth change by span: it separates the observed thick target/control cells,
but its global form cannot land. The checker32 lg referee was not rendered and is not declared
repaired by analogy. Neither were the photo-lg holdout or composite holdout.

### F4 — the named misses are not all deep texture

`attribution.json` contains all 24 photo rows and the three 2x F-inactive rows, not just exemplars.
Ordinary photo bodies remain too flat/desaturated: T1 ratios .22–.69 on untinted unpressed cells.
The eye sees missing hues and a too-neutral veil; a narrow tap is not a complete chromatic or
level law. The four pressed photo cells have the opposite sign (ratios 1.44–1.66), with a conspicuous
central highlight hotspot absent from these native frames. `wgsl/highlight.ts` draws a radial press
glow; its separate contribution is not isolated here. Orange active capsules are tint-dominated,
and the nested inactive panes have a conspicuous flat foreground, so neither is a simple uncoloured
single-surface blur diagnosis.

The remaining 2x F-inactive T1 ratios are 2.04 (checker4 md), 1.94 (checker8 md), 2.37 (checker8 lg).
But the existing **deep** readings, in encoded codes, are native/web .474/.480, .907/.686,
.478/.359. The eroded fine-band values are also much closer than full-silhouette T1. Much of the
remaining excess is outside the deep body, in the edge/rim region the sheets show. It is not
justification to blur the already-smoother deep checker further. G0 keeps the full-silhouette gate
and reports a disjoint edge/deep decomposition; it does not replace the adopted statistic.

## Proposed design: two independent axes, with the unresolved cells explicit

### D — the transmission's own top

Add `tintAlphaSpanMax` / `tintAlphaSpanMax2x`, **identity 0 = follow the scatter top**. Resolve a zero
anchor to that scale's scatter top BEFORE interpolating across dpr. For a nonzero top T, require
T > `sizeSpanMax`. Per pixel, with s the casting span:

`alphaBase = clamp(tintAlpha + farAlpha(dpr) * smoothstep(sizeSpanMax, T(dpr), s), 0, 1)`.

Everything after alphaBase, including W9's solve, remains unchanged. Both leaves are plain value
identity drops. The zero case executes the old expression exactly; digest and GPU byte proofs cover
all ten endpoints. CSS mirrors the same per-surface law and X75 reads the new resolved top on both
tiers. D is not a new free opacity budget: X75 remains <=.95 over spans 0..1024 at both scales.

The active ladder holds transmission T=160 and tries scatter tops 160, 192, 256, holding other
leaves first. W49a's P1 proved the shared-top attribution by render. As a first-order, **unrendered**
additive estimate, restoring scatter top 256 at held current scale gain predicts the three active
lg cells near .0267/.0332/.0303 (1x) and .0320/.0391/.0314 (2x), sufficient to remove their six
entries. The additivity is not established: the actual D ladder must meet the historical ceilings
and current-cell protections, including ml and photo. It must leave span <=96 unchanged.

### W — a span-selective second-tap bandwidth, not a renamed share

Proposed leaves `sizeHeavySecondSigmaFar1x` / `sizeHeavySecondSigmaFar2x`: CSS-px width deltas,
identity 0, plain value drops. Let sigma2 be the existing secondary width, delta its resolved new
width delta, H(s) the scatter's existing far smoothstep. Define the operator by its samples:

`secondary(s) = G(sigma2) + H(s) * (G(sigma2 + delta) - G(sigma2))`.

Then the existing signed secondary share mixes this result with the primary deep sample as before.
**This is a two-bandwidth crossfade, not an assertion that intermediate pixels equal a Gaussian at
an interpolated sigma.** It preserves DC; the kernel widths are CSS px resolved to device px by the
existing tap machinery. At delta 0, take the old path, allocate/sample no extra texture and preserve
bytes. Require sigma2+delta >0 when live. The first declared ladder uses nonnegative deltas {0,3,4,5}
from the current width 5. A nonzero width delta with zero secondary share need not allocate a tap.

Use D to hold the receded transmission top at 160 while testing the scatter top at 128 and 160.
At scatter top 128, H=1 at ml and lg, giving the global width diagnostic's bandwidth there while
holding spans <=96 at the old width. The scatter's other consumers still move: the ladder must
read their full output, not claim exact reproduction of the global probe. This minimal form uses
the existing scatter knot deliberately; **if its other consumers veto the separation, stop and
re-declare an independent width knot rather than smuggling one in during fitting.**

The dark ladder crosses delta {0,3,4,5}, receded far alpha {.09,.10}, scatter top {128,160}, with D
holding transmission top 160 and share .25. First compare identity and single-axis controls, then
the finite joint grid. Predictions at the fully widened ml/lg endpoint are the F3 table, with
measurement tolerance B; protected <=96 cells should reproduce within .1 bar when only W moves.
The success bar is stronger than a slope: all three impulse costs repaired, all five W49a removals
still repaired, the remaining checker32 lg prediction checked at the frozen exposure, and no
protected gate-cell error growth >B. The width controls must improve impulse without losing
coarse checker64; fine/text/photo are controls, not disposable compensation cells.

W45 already identified the light 0.25 need for a span-widening narrow term (§5.206–§5.207). W is a
single law with per-document anchors and can serve that question too. **No light fit or light
holdout read is part of W49b.** A later light declaration decides whether this two-bandwidth family
has the needed response; similarity of the missing axis is not proof of a shared fitted law.

CSS already declines the second tap. It declines W with it: no new CSS blur, no synthetic opacity
compensation. Its profile resolution and coherence tests must name that decline; D still mirrors
normally. An eventual dark document's existing leaf changes still require a CSS reading.

### N/L — thin bandwidth and backdrop-conditioned response, not yet identified

The finite thin-ramp/body-prefilter failures in F2 are controls for G0, not admitted repair points.
D and W have zero direct authority over the lc16-md cells. A fresh level/contrast crossed native
bed is needed before claiming a backdrop-conditioned transmission law: current lc16 changes both
mean and contrast, and tone-ordinate refitting alone does not change the group-level solve's
transmitted spatial contrast. Do not branch on a scene name, low-contrast label or sampled pitch.
A measured source statistic may condition a declared law only if the crossed bed identifies it.

G0 may close with **no full-list family identified**. To enter G1 it must produce, for every target,
a declared mechanism and separating ladder, including the five thin/mid entries. A parent wishing
to ship only a thick subset must rule a new success set explicitly before part 2; the present draft
neither disguises that subset as all-list repair nor presumes the decision.

## Proposed landing rule and references

**Part 2 admits NO post-gate amendment.** It is hashed before the fit's first gate read and contains
the complete candidate domain, selection arithmetic and every reference. If no point passes at both
scales, the verdict is **NEITHER**: no seal, no publication, no re-authorisation and no re-selection.
Close at the finding and hand the decision to the parent. A later user-directed exception is a new
explicit decision, not a rewritten pass; this draft proposes not to plan for that escape hatch.

1. **Repair all fifteen:** each against its F1 historical reference, growth <=B. References never
   advance merely because the current generation already carries a regression.
2. **No new trade:** every dark 0.25 WebGPU T1 cell against W49a current, growth <=B, including
   listed cells (so a historically allowable but presently worse result cannot slip through).
   For T cells, use T1-low for regression and T1-fine for fidelity. Count overshoots by growth.
3. **Keep the repairs already bought:** the five W49a removals remain <=B against d0219:
   checker64 lg inactive and photo lg inactive at both scales, checker32 lg inactive at 1x.
   Thus checker64 at 2x cannot silently return to the list while growing <B against W49a.
4. **Keep the achieved strata:** W48's C-rest halvings at both scales and F-inactive halving at 1x
   against d0219, on the same partition definitions; P both scales and F-inactive 2x remain named
   misses, reported against Apple and current, with no aggregate worsening. No row is dropped.
5. **Other adopted rows and images:** M2, L1, E2 and coherence use their current owner contracts;
   X75/X76 hold. Inspect native/current/candidate pixels, including deep, edge, pressed/tinted and
   composite cases. A new visible gap is recorded and returned to the parent, never hidden by T1.

The per-cell constraints are intersections, not a reference chosen after seeing a result.
Part 1 emits `references.json`: (profile, renderer, scene, statistic) -> current generation plus
any historical constraint, with document-pair hashes and capture-tree locations. Missing cells are
UNMEASURED, not passes. Unreachable cells are reproduced, not removed from final acceptance (X74).

Among points passing every gate clause at both scales, propose minimum median per-cell absolute
log error over all 154 dark T1 cells, using T1-fine on T and one-code epsilon; at the gate use only
its predeclared gate membership, never impute a movable withheld cell. Within the median bar-based
log tolerance, choose minimum normalised distance from current coefficients using ranges hashed
in part 2, then the lexicographic candidate id. The single frozen point's exposure must itself pass;
an exposure failure stops, never sends the fit back to choose another point.

## Referees and native capture

The canonical dark 0.25 holdout and W46's twelve dark referees are **spent and not blind** (reads
8 and 9; their current numbers and pixels were inspected here). They stay out of exploratory
renders and fitting, and the frozen point is read once as a prediction check with numbers declared
before that read. Calling that read a blind referee would be false.

No unspent, directly applicable dark 0.25 referee is identified in the existing bed. The light
referees/holdout remain outside this dark work; the earlier W42 archive's unspent H tests another
setting/model and is not a fresh 0.25 thick-span referee. **A blind identifying thick-span capture
is recommended and requires the user's lift of X5.** Nothing in this charter grants it.

Proposed native experiment: cross spans 44/64/96/112/128/144/160/192 with coarse/fine periodic inputs,
isolated impulses and a structured photograph; cross level and contrast independently at the same
pitch, including matched-mean full/low-contrast controls. Both dark poses and scales, colour-managed
no-glass controls, repeat bar, matched clearance on a canvas large enough for the thick surface.
Match a canonical bridge before transferring a new canvas's reading. Declare calibration versus
blind spans/pitches/structured scenes before capture; reserve interior spans 112/144 and new pitches
12/24/48 as candidate blind axes, not just another named size on the fit grid. The final manifest,
repeat count, capture mechanism and split are G0's pre-capture declaration, reviewed before X5.
A failed native bridge or unmeasured repeat bar stops identification. Native capture is not needed
to prove D's software decoupling, but is needed for the proposed new blind-generalisation claim.

## Children and interfaces (proposed, not dispatched)

### G0 — declaration and identification

Produce the immutable current/historical document snapshots, reference map, all-cell mechanism and
authority table; declare the native bed if authorised. Before any new operator's ladder, prove D/W
identity over ten digests, 34 goldens, fractional-dpr cases and the dark bed, with X75/X76 and the
CSS mirror/decline explicit. Declare the numeric ladder and its separation bar before each new
reading. Deliver actual D/W renders, the thin/level identification result, named counterexamples,
and a **PASS-to-fit or STOP-at-finding** outcome. No document is fitted or published in G0.

Code ownership: `packages/renderer-webgpu/src/material.ts` (profile, patch, scale helpers, identity
entries), `renderer.ts` / `passes.ts` (resolved uniform and binding data), `wgsl/optics.ts` (separate
alpha curve and the secondary sample), `pyramid.ts` and the heavy-tap planner (extra source blur,
identity allocation), `packages/platform-web/src/optics.ts` (D mirror/W decline), and
`packages/calibration/scripts/no-opaque-glass.ts`. Inspect every reader, not only the shader.
The identity table's old entries remain unchanged. Test auxiliary tap lifetime, multiple surfaces
of different spans sharing a source, live-backdrop invalidation and measured frame cost: W adds a
source blur, not just an arithmetic instruction.

### G1 — fit and referee only after G0 closes the mechanisms

Hash the complete fit/selection in part 2, fit in candidate mode with the reference map and X70's
requested/planned/measured membership equality, freeze one point, then read spent referees as the
one prediction exposure and any newly captured blind set once. NEITHER stops as above. A full pass
permits the parent's seal/publication act with strict-mode reproduction, X75 and X76 applied to
**every** receded named/inherited leaf. Declare the complete dark stage, including recorded/probe,
then publish its immutable pair-qualified generation in one act. Copy its capture tree at landing
and archive the superseded pair without losing the W49a capture provenance.

### G2 — owner landing or evidence-only closure

On a passing landing, execute X59's five-part order: old/new band fixtures; historical witnesses;
remove repaired authorisations (no replacement costs); re-derive missed cells; move the reference
last. Keep M2/L1/E2's stated references. Update generated material, ledger, sheets, demo projection
and release chain. On a finding, record it without a material changeset or canonical publication.
The fidelity release size is the parent's decision, not inherited from W49a's opacity-fix patch.

Verification proposed: one independent adversarial spec/buildability review before execution;
independent high review for G0's operators and G1's gating/seal, medium for G2's owner/reference
landing. Runtime checks follow `pnpm -r build && pnpm -r lint && pnpm -r test`, GPU/goldens and the
c9d chain; each merge verifies the frozen 1,818 and X41 911. Grounding scripts verify request/row
membership and browser version, and preserve the exact scratch matrices, census and candidates.

## Risks and alternatives

- **P, share alone:** fewer resources, but its measured direction couples impulse and coarse
  texture; it cannot reproduce the width/alpha separator. Retain as a control, not the lead family.
- **R, more transparent everywhere:** W49a's six-rung obstruction remains; no pitch distinction.
- **Existing thin ramp:** cheap but measured tradeoffs above. Splitting it off does not make it pass.
- **Body fine tap:** already available and worth reading; the measured controls fail. No assertion
  that W48's original objective proved it universally useless.
- **Direct per-pixel Gaussian width:** more literal than W's crossfade but needs a blur pyramid or
  source atlas and extra sampling; W is the minimum test of the missing bandwidth axis. If its
  crossfade family fails, report that rather than presenting it as the exact variable-width law.
- **Full native LT/nonlinear compositing:** can address more of the photo/level problem, but W42
  already found no declared landing and it carries a larger frame cost. A crossed native bed should
  decide whether that complexity is required; no revived LT fit is implicit here.
- A 342-cell exploratory programme identifies local separations, not a globally feasible material.
  The all-list rule is deliberately capable of stopping the wave before a refit.

## Decision Log

Open for the parent. No ruling is recorded by this grounding worker.

Decisions requested: (1) retain all fifteen as success or explicitly charter a thick subset;
(2) authorise D/W identification with thin/level work as a G1 prerequisite; (3) request the user's
X5 lift for the crossed native bed, or accept an evidence-only/non-blind scope; (4) adopt the
reference intersections, no-new-trade rule and no post-gate amendment/NEITHER stop above.

## Surprises and discoveries

The fine named miss is not excess deep checker contrast. The thin-start orange cell is a crossing
that still fails its historical budget. Width and share are not interchangeable, nor does a share
change have the same sign at the two scales. A recorded authorisation cannot be retired using
only the current-generation budget; the old historical constraint remains live even after repair.

## Deferred

Light fitting, dark 0.5, accessibility at 0.25, contour/pressed-response fitting, and the photo's full
colour law remain separate declarations. Their measured gaps are recorded above, not excused.
The five unresolved thin/mid repairs are G0 prerequisites, not silently deferred out of success.

## Outcomes and revision notes

- 2026-10-08 draft: grounded on W49a's landed pair, prospective scratch controls and inspected pixels.
  The wave is not approved or executed. No complete all-list solution is claimed.
