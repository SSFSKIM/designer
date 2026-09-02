# W11 — The remaining floors (2026-09-02)

> **Parent:** the post-v1 wave
> (`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`), by way of W9's and
> W10's Deferred lists (`2026-09-02-w9-backdrop-tone-sampling.md`,
> `2026-09-02-w10-tint-pathway.md`). Picked by the user 2026-09-02: "open
> the remaining twenty-three floors." **Consumes:** claims §5.27 (the floor
> tables), §5.35 and §5.37 (the two re-attributions that left these
> twenty-three), and §5.38 (the per-pixel measurement of all three classes,
> taken before this document was written). This is a composite: three
> children, each a controlled round in the W9/W10 shape, dispatched in the
> order the Decision Log fixes.

## Purpose

Twenty-three enforced rows on the two light-standard profiles are regression
floors instead of met claims. W9 and W10 discharged twelve of the original
thirty-three by fix and re-attributed what they did not own; what remains is
three mechanisms with nothing in common except the ratchet that holds them:
the interior's spatial structure on structured backdrops (fifteen `ssimMean`
rows), the nested-glass surface (six ΔE/ratio rows, and the pane's share of
four of the SSIM rows), and the silhouette extractor (two contour rows). §5.38
measured each per pixel. One is a rendering defect with a predicted cure, one
is an instrument rule with a measured replacement, and one is a fidelity
question with a measured decomposition and a contract inside it. This unit
exists to take every floor to one of two ends — **removed as a met claim**,
or **held by decision with its mechanism named and its owner or its narrowed
claim written down** — so that no row in §5.27 is attributed to "unknown"
when it closes.

## Parent-Level Acceptance

- Every row of §5.27's tables reads either **MET (W11x)** with its adopted
  bound restored, or **UNMET by decision** with the mechanism, the evidence
  and either an owner charter or a narrowed claim beside it. No row is
  floored on an unexplained miss.
- `UNMET_ROWS` in the enforcement test equals the number of by-decision rows,
  the floors match the rebuilt canonical matrix, and the predicate's
  exclusion list is the machine's.
- The canonical matrix is rebuilt **once, at recomposition**, across all
  twelve per-profile runs (X1), and the whole-bed regression scan against
  the W10-close matrix shows every cell outside the three classes inside its
  bounds, with the untinted, un-nested, non-checkerboard bed byte-identical
  except where a child names the change.
- All package suites green, lint clean, golden e2e green — re-recorded only
  where a child's Decision Log says which scene and why.

## Grounding Baseline (measured, §5.38)

- Floors: 23 (10 nested-glass rows, 11 checkerboard rrect SSIM rows, 2
  extractor rows). Enforced count 23.
- SSIM is whole-crop; in-glass SSIM is not size-monotonic (texture 1x:
  0.806 / 0.639 / 0.734 / 0.784 / 0.803 from `rrect-sm` to `rrect-lg`).
- Loss by region, 1x `rrect-lg`: deep body 39–45%, rim band (0–24 px
  inside) 42–45%, outside 12–16%; at 2x the outside band is 34–52%.
- Reference body law (1x, spans ≥ 96): heavy blur σ₁ ≈ 8.5–9 CSS px, sharp
  leak t₂ 0.235 → 0.112 with span, level 0.416 → 0.464; vitrea flat from
  span 96 (GPU σ 3.8 / t 0.41; CSS σ 3.0 / t 0.563).
- Nested glass: the GPU tier's upper pane is a flat 0.468 (bytes 182) where
  the reference reads 0.893 and the CSS tier 0.899.
- Extractor: an OKLab ΔE rule at 0.02–0.05 recovers 1.000 of the region with
  zero holes on all twelve measured sides; the native side has 2–6 holes
  under the current rule.

## Design

This is an uncoupled bundle: the three children share no rendering surface
beyond the enforcement bookkeeping and the matrix rebuild, so the design
here is thin and lives in the children. Three decisions are binding at this
level because only the whole picture settles them:

- **[binding — the referee is shared]** One canonical matrix rebuild at the
  end, not one per child. Each child referees its own rows on partial runs
  (`--write-partial`) and records them; the parent's recomposition run is
  the read that lands in `results/matrix.json` and in §5.27. Reason: the
  extractor child changes every cell's mask, so a child that rebuilt the
  matrix before it would be re-read anyway.
- **[binding — the instrument precedes the fit]** The extractor child lands
  before the structure child's referee runs. Reason: the structure child's
  material statistics (`interiorStdDev`, the frosting ratio) read through
  the mask; fitting on one mask and gating on another is a moving target.
- **[binding — a defect is not a fit]** The nested-glass child changes no
  constant and fits nothing; it corrects a compositing path and is refereed
  on the holdout cells it owns plus a new golden scene. Reason: the two
  nested cells are the only nested cells and both are holdout; a fit there
  is forbidden by the discipline, a repair is not.

Advisory, carried from §5.38 into the children's Design inheritance: the
two-component body model and its constants; the rim-band decomposition; the
2x disagreement; the CSS-lens arithmetic.

## Children

### W11a: Nested glass — the upper pane composites over what is under it — controlled

- **Purpose:** the optics pass writes a surface with no backdrop source as
  an opaque pixel with black baked in (`colour = mix(vec3f(0), adapted,
  adaptedAlpha)`, encoded at `coverage`), so the DOM proxy's blurred base
  glass beneath the canvas never shows. The upper pane of both nested cells
  is a flat 0.468 against the reference's 0.89–0.91. This child makes the
  no-backdrop path write the material premultiplied — the adapted colour at
  the material's alpha, the outer shadow still under it — so the pane
  composites over the proxy exactly as the CSS tier's in-place filter does.
- **Acceptance:** the four `oklabDeltaEP95` floors and the two
  `interiorLevelRatioGpuOverCss` floors on the nested cells removed as met
  claims (predicted: GPU interior ≈ 0.70 against native 0.706, ratio ≈
  0.93); the four nested SSIM floors no worse; every non-nested cell on the
  GPU tier byte-identical (the path is gated on `flags.x`); a golden e2e
  scene that exercises a DOM-sampled surface with no backdrop source, added
  and recorded with the fix (the current goldens never take this path —
  `concentric-nesting` samples a texture); the isolation spec's attribution
  re-run if the change is not expressible as a profile patch (it is not).
- **Edges:** blocked-by: —; blocks: — (independent of W11b/W11c; ordered
  first because its rows are the largest single errors on the bed and the
  fix is a repair).
- **Contracts:** X1, X2, X3.
- **Design inheritance:** §5.38 §5 (the mechanism, the region table, the
  prediction) — advisory; the first read is the shader's output for
  `flags.x = 0` and the highlight pass's behaviour on the same surface.
- **Required:** required.
- **Status:** landed (2026-09-02; Decision Log 2, claims §5.39).

### W11b: The silhouette extractor — a colour-aware rule, bed-wide — controlled (instrument)

- **Purpose:** the luminance-delta rule cuts holes wherever an opaque
  tint's luminance meets the backdrop's, on the native side as much as the
  web side, and the conditioning predicate has no holes arm. §5.38 §6
  measured an OKLab ΔE rule recovering the whole region with no holes at
  every threshold tried. This child declares the rule and its threshold
  before it runs, re-measures the whole bed from the captures on disk, and
  restates everything that reads through the mask.
- **Acceptance:** the two `contourDistance` floors on
  `photo__rrect-md__rest-tint-orange` removed as met claims; every cell's
  shape and material numbers re-read and any adopted bound that moves
  recorded with its before/after (SSIM and ΔE, whole-crop, must not move —
  a byte-identity check on those columns); `PREDICATE_EXCLUDES` re-derived
  and the change in coverage counted; §5.15's published predicate counts
  restated against the new masks; the rule's threshold and space declared
  in the child's spec **before** the first bed-wide run, with the stop
  condition "a mask that grows past the declared geometry or admits the
  outer shadow" written down.
- **Edges:** blocked-by: —; blocks: W11c's referee (binding, Design).
- **Contracts:** X1, X2, X4 (owner).
- **Design inheritance:** §5.38 §6 — advisory (the threshold is the child's;
  0.03 is the measured midpoint with a 4× margin to the hole pixels' 0.12).
- **Required:** required.
- **Status:** not-dispatched (dispatchable now; lands before W11c's referee).

### W11c: Interior structure — the body law, the lens band, and the CSS contract — controlled

- **Purpose:** fifteen `ssimMean` rows on checkerboard cells. §5.38
  decomposed the deficit into a deep body that vitrea renders with a
  size-invariant σ 3 blur where the reference renders a heavy σ ≈ 9 blur
  plus a sharp leak that fades with span; a rim band where the GPU tier's
  lens differs from the reference's and the CSS tier has none by contract;
  and an outside band of contour-straddling windows. This child fits the
  body law on both tiers through the scatter facet that already exists,
  fits the GPU lens band against the probe's resolved-lens cells, and takes
  the CSS-tier rim question to its referee with the measured arithmetic.
- **Acceptance (three named gates):**
  - **G1 (required) — the body law.** `sizeScatterGainMax` (or the
    replacement law the child declares) and the level past the band top
    fitted on the calibration spans 32 / 44 / 96 / 128 at pitch 16 plus the
    probe's pitch axis at 1x; 2x validated by prediction, not fitted;
    `rrect-lg` and the nested cells untouched holdout. Photo and solid cells
    must not move outside their bounds (the law rides only structured
    content by construction, or the child measures why not).
  - **G2 (required) — the GPU lens band.** The rim band's share of the
    deficit on the GPU tier halved on the calibration cells, fitted against
    the probe's pitch-32/64 cells where the reference's lens is resolved;
    the rim/specular constants (§6.2) untouched unless the child measures
    them as the term.
  - **G3 (conditional on G1+G2's referee) — the CSS tier's rim band.**
    Evaluable once G1 and G2 have landed and the CSS rows are re-read. If
    the dom rows on calibration cells meet (the §5.38 arithmetic predicts
    ≈ 0.91–0.92 against 0.90), the holdout dom rows are held by decision
    under the refraction contract with the claim narrowed in writing. If
    they do not, the child opens a decision round on a CSS-tier lens
    approximation versus narrowing, with the measured gap.
- **Edges:** blocked-by: W11b (referee only; the fit may start on the
  current masks); blocks: recomposition.
- **Contracts:** X1, X2, X3, X4 (consumer).
- **Design inheritance:** §5.38 §1–§4 — advisory throughout; the
  two-component model is a description of the reference, not the
  implementation's shape, and the 2x disagreement is a delegated unknown
  this child must state a position on before fitting (one law in CSS px,
  or a device-pixel term — the latter overturns "lengths in points" and
  needs its own decision).
- **Required:** G1 and G2 required; G3 conditional as stated.
- **Status:** not-dispatched (dispatchable now for the fit; referee waits on
  W11b).

## Cross-Child Contracts

- **X1 — the canonical rebuild.** `rm results/matrix.json`, then twelve
  per-profile runs (`--material-profile`, `--renderer webgpu|css`, `--set
  calibration,validation,holdout --write-partial`), the same driver W9 and
  W10 used. Children write partial rows for their own referee; the parent
  runs X1 once at recomposition. Owner: parent.
- **X2 — floor bookkeeping.** A floor comes off only with its bound
  restored as a met claim in §5.27 (struck row, before → after values);
  `UNMET_ROWS`, `FLOOR_EPSILON` and `PREDICATE_EXCLUDES` in
  `packages/calibration/test/adopted-thresholds.test.ts` edited with the
  count sitting next to the section number that justifies it. Owner:
  parent; every child binds.
- **X3 — the untouched bed.** Each child runs the whole-bed regression scan
  against the W10-close matrix (`matrix-w9-close.json` pattern) and names
  every cell that moved by more than 0.005; cells outside the child's class
  that move are a finding, not a footnote. Owner: parent; every child binds.
- **X4 — the mask.** The silhouette rule and threshold W11b declares define
  "interior" for every material statistic the bed reports. W11c's referee
  reads through it; W11a's ratio rows are predicted on the current mask and
  refereed on X4's. Owner: W11b.

## Ordering & Dependency Map

W11a → W11b → W11c (referee) → recomposition. W11a and W11b are independent
of each other and could run in parallel; sequential is chosen because each
lands in the same enforcement file and each rewrites §5.27's count. W11c's
fit may begin at any time (it reads native references and the probe bed,
not the mask); its referee waits for W11b.

## Risks & Mitigations

- **The nested fix moves cells that share the path.** Every surface in a
  group with no backdrop source takes it — the golden `highlight-press-glow`
  is `noBackdrop`. Mitigation: W11a's byte-identity scan on the GPU tier and
  the golden suite before the referee.
- **The extractor rule grows a mask into the rim or the shadow.** The rule
  is region-bounded by geometry, so the shadow is excluded; the rim is
  inside the declared region on both sides today. Mitigation: the stop
  condition in W11b's declaration and the per-cell area ratio (≤ 1.000).
- **The body law fitted at 1x lands 2x wrong.** §5.38 §3 measured the two
  scales disagreeing in the reference. Mitigation: 2x is predicted, not
  fitted, and a miss there is a recorded finding with the device-pixel
  question routed to a decision, not a silent second constant.
- **G3 becomes a feature.** A CSS-tier lens is a new tier capability with
  its own calibration and browser support question (`backdrop-filter:
  url()` is Chromium and Gecko, not WebKit). Mitigation: G3 is conditional
  and opens a decision round rather than starting the work.

## Deferred / Out of Scope

**Deferred (may return):** the outside band's contour-straddling loss
(measured, not attributed; the shadow amplitude is right); the 2x
reference's non-Gaussian interior structure (the 2x bed has no probe
pitches — a 2x probe capture is the charter); the dom tier's standing photo
level (+0.056 on large surfaces, inside bounds); the W9 and W10 Deferred
lists as they stand (dark response surface, per-footprint tone, accessibility
response surfaces, half-strength layer, dark tint surface, mid-collapse
regime, blue hue residual).

**Explicitly out of scope:** the WebGL2 tier; topology-changing morphs;
recapturing the canonical bed (every child measures from captures on disk;
only W11c's referee captures the web side).

## Tracking Map

| child | spec / evidence | status |
| --- | --- | --- |
| W11a | LANDED 2026-09-02 — claims §5.39; the optics pass's unsampled path writes a premultiplied layer at the host's compositing-space pair (`unsampledMaterial`, the CSS tier's alpha on the renderer's tint); 6 floors MET and removed, 2 texture SSIM floors ratcheted up, 2 dom SSIM floors unchanged; enforced count 17; 248/254 captures byte-identical, the 6 that differ are the nested GPU cells | landed |
| W11b | — | not-dispatched |
| W11c | — | not-dispatched |

## Decision Log

### Decision Log 1 — the cut, the order, and what the user decides (2026-09-02; DECIDED the same day)

**Decided (user, 2026-09-02):** the cut and the order approved as
recommended (W11a → W11b → W11c); W11a dispatched immediately; W11c's G3
question (CSS-tier lens versus narrowing the claim) decided at W11c's
referee with the measured residual in hand, not now.

**The cut.** Three children by mechanism, as measured in §5.38, rather than
one round over all twenty-three or a round per metric. Rejected: one round
(three verification strategies — a repair, an instrument change, a fit — in
one referee would hide which moved what); a round per cell class by metric
(the four nested SSIM rows straddle two mechanisms and would be owned twice).

**The order.** W11a, W11b, W11c. Rejected: structure first (the largest class,
but its referee would run on a mask the extractor child then changes);
extractor first (mechanically sound, but the nested repair is the smallest,
surest win and its rows are the bed's largest single errors).

**What the user decides now.** (1) Approve the cut and the order. (2)
Dispatch W11a immediately. (3) Whether G3's CSS-tier question is decided
now or at W11c's referee — the recommendation is the referee, because the
§5.38 arithmetic says the calibration dom rows may meet without a lens and
the decision is cheaper with that read in hand.

### Decision Log 2 — W11a's referee and close (2026-09-02)

**Verdict.** All six chartered floors MET on the re-captured bed (ΔE p95
0.19 → 0.07–0.12 against ≤ 0.17; the `photo` cross-tier ratio 0.796 → 0.918
against ≥ 0.8), removed with their claims restored; the two texture-tier
nested SSIM floors improved (0.8409 → 0.8796, 0.8762 → 0.8948) and stay
unmet, **ratcheted up** to the new measurement rather than left at the
old one — a floor is what the bed measures; the two dom-tier nested SSIM
floors byte-unchanged. Enforced count 23 → 17. The child's acceptance is met
in every clause (the byte-identity scan: 248 of 254 captures unchanged, the
six that differ being exactly the nested GPU captures; the `field-mask`
golden re-recorded as the one golden on the path; the isolation hash
re-recorded with its attribution; unit tests on the pair's path end to end).

**What the child changed beyond the charter, and why.** Two forms in the
layer had to be chosen where the composite had been a single expression:
the outer shadow fills `1 − coverage` (a `box-shadow` clipped out of its
border box; the first form filled the layer's own transparency and read the
pane at 0.811), and the rim carries its light in the layer's opacity (the
first form, white over the layer at the rim's weight, is short of the
additive term by the rim times the whole composite; the carried form is
exact for an opaque layer). Both are recorded in §5.39. One instrument
finding beside them: the platform-web GPU suite's rim read on a tinted
dom-mode panel had been sampling outside the rim band and sitting on its
own threshold since W10; it now reads inside the band at DPR 2.

**The pair is the host's, not the profile's.** The browser composites the
layer in encoded sRGB, so the alpha the layer is written at is the CSS
tier's (`cssTintAlpha` at the mapping's reference level, 0.665) on the
renderer's own tint — resolved once by the host and forwarded only to groups
that sample nothing. Rejected: writing the profile's linear alpha (0.46)
and letting the tiers differ; solving a per-pixel alpha in the shader
against a backdrop it cannot see.

**The residual is recorded, not fitted.** The GPU pane sits 0.014–0.020
under the reference; the reference's effective encoded alpha back-solves
near 0.72 against 0.669. Both nested cells are holdout. Whether the
reference's pane carries the size law, the base's rim, or a nested tone
response is W9's Deferred "nested-glass tone" charter and needs a
calibration cell that does not exist.

**Close.** W11a landed on its acceptance; W11b dispatches next per Decision
Log 1.

## Surprises & Discoveries

- **The nested fix touched the whole GPU-over-DOM path.** Every `dom`-source
  group on the GPU tier — the ordinary React usage, not only the nested
  scene — had been an opaque grey slab over its proxy (the material mixed
  over black, written opaque). The calibration bed saw it only on the nested
  cells because every other canonical scene samples a texture (§5.39).
- **A layer is not a composite with alpha.** Two of the shader's terms
  (the outer shadow's fill, the rim's added light) had one form when the
  body was opaque and needed a different one as a layer; each surfaced as
  a measured miss rather than in review (§5.39, the two corrective
  findings).
- **The SSIM size trend was coverage.** In-glass SSIM is flat-to-better with
  size; the capsule is the worst cell on the texture tier (§5.38 §1).
- **The nested pane was never rendered.** The GPU tier's upper pane has been
  a constant since the scene existed; §6.4's "mixed-backend claim" was
  describing an opaque grey rectangle (§5.38 §5).
- **The reference's mask has holes too.** The extractor's rule is the
  instrument on both sides of the comparison (§5.38 §6).
- **The reference disagrees with itself across scales** in the interior's
  structure, not only its contrast (§5.38 §3).

## Outcomes & Retrospective

Pending — written at recomposition, after the single X1 rebuild.

## Revision Notes

- 2026-09-02 (W11a landed; Decision Log 2): six floors removed, two
  ratcheted up, count 17; the Tracking Map row and claims §5.39 carry the
  evidence. Two Surprises added. W11b is next.
- 2026-09-02 (Decision Log 1 decided by the user): the cut and order
  approved, W11a dispatched, G3 deferred to W11c's referee.
- 2026-09-02 — opened. §5.38 measured; three children cut; Decision Log 1
  awaiting the user's round.
