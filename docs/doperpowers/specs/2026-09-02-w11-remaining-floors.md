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
  **Overturned in part at dispatch (Revision Note, 2026-09-02):** §5.38 §6
  measured a pure OKLab-ΔE rule on `photo` cells only; on the bed's other
  backdrops it is a regression, not a replacement — see the declaration.
- **Required:** required.
- **Status:** landed (2026-09-02; Decision Log 3, claims §5.40). The
  declaration below preceded the bed-wide run and every prediction in it
  held.

#### W11b declaration (written before the first bed-wide run, 2026-09-02)

**The rule.** A pixel inside the declared region is inside the silhouette
iff

    |Y_lin(capture) − Y_lin(plate)| ≥ 0.02   OR   ‖ab_OK(capture) − ab_OK(plate)‖ ≥ 0.03

— the existing luminance-delta arm, unchanged in threshold and space, plus
a second arm on OKLab chroma (the a/b plane, the neutral axis excluded)
that fires where a surface differs from what is behind it in colour at a
matched luminance. The two arms are orthogonal by construction and the
rule is a **strict superset** of the current one: no pixel the luminance
arm admits is dropped, so area recovery cannot fall and a hole cannot open
on any cell; the only outcomes the change can produce are holes closing,
fragments joining, and — the one to watch — a stray chroma fragment.

**Why not the advisory rule.** A pure OKLab-ΔE ≥ t rule replaces the
luminance arm with OKLab lightness, whose sensitivity to linear luminance
falls with level (dL/dY ≈ Y^(−2/3)/3: at Y 0.9 a ΔY of 0.02 is ΔL 0.007).
Measured on the captures on disk (`w11b-sensitivity`), at t = 0.03 it
drops the light-solid `rrect-md` reference to 0.031 of its region in seven
bodies, the light-solid capsule to 0.102, the `hc-text` `rrect-md`
reference to 0.948 with four holes, and punches 22 holes in the CSS
checkerboard `rrect-md`; at t = 0.02 the light-solid `rrect-md` reference
still reads 0.060. It also admits the near-black cells (impulse, dark
solid) where OKLab's cube root puts one code value of luminance noise at
ΔL ≈ 0.07 — a threshold-crossing that is capture noise, not a surface. The
union rule leaves every one of those cells byte-identical and fixes every
tinted one.

**The threshold.** 0.03 on Δab. The hole pixels §5.38 §6 measured sit at
Δab ≥ 0.12 (the orange over the photo's orange differs in chroma, not in
luminance); the masks' own 1st percentile is 0.11. Across 0.02 / 0.03 /
0.05 every cell measured gives an identical mask — the outcome is
insensitive to the threshold over a 2.5× range, which is the evidence that
the rule is not being fitted to the bed. Neutral captures over neutral
plates have a/b of exactly zero on both sides, so the arm is inert wherever
no colour is present.

**What will move.** Shape and material rows on cells whose mask changes —
predicted: the twelve tinted `photo` cells across the six profiles and both
tiers, the `hc-text` tinted capsule, the increased-contrast `photo` tinted
capsule, and the `orange-half` capsule; the `photo` nested cells' residual
holes. Predicted to leave the exclusion list: the `bodiesWeb` tinted family
(`photo__capsule-button__rest-tint-{orange,blue}` on every profile that has
them, `photo__rrect-lg__rest-tint-orange` dom, `photo__rrect-md__rest-tint-
orange` dom, the three W10 joiners). Predicted MET: the two W10 contour
floors on `photo__rrect-md__rest-tint-orange` (the hole was the miss).
**What will not move:** every `perceptual` column (whole-crop, mask-free —
asserted byte-identical against the W11a-close matrix); every cell whose
capture is neutral; the `areaNative` exclusions (near-black references,
increased-contrast over the checkerboard's white); the `areaWeb` `hc-text`
family (white glass over white differs in nothing).

**Stop conditions.** Any cell whose `silhouetteBodies` count RISES (a stray
chroma fragment); any cell whose mask exceeds its declared region (impossible
by construction — the region bounds both arms — but asserted); any
`perceptual` value that moves by more than floating-point noise. Any of the
three stops the adoption and the finding is recorded before the rule is
changed.

**Protocol.** The rule lands behind `--silhouette-chroma-threshold` with
the package default at the declared 0.03; the dry run writes a scratch
matrix from the captures on disk (`--skip-capture`, all twelve
profile × renderer runs); the referee compares it column by column with the
W11a-close matrix, checks the stops, re-derives the exclusion list and the
per-profile gated counts, and then — only then — the same runs write
`results/matrix.json`. No capture is taken; the web PNGs stay byte-identical
by construction.

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
    approximation versus narrowing, with the measured gap. **Decided at
    G1's referee (Decision Log 5): narrowed** — the CSS body is the law's
    single-blur form; the two-layer form Chromium can render is deferred
    with its evidence.
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
- **Status:** in-flight — G1 LANDED 2026-09-03 (claims §5.42; Decision
  Log 5), G3 decided there; G2 (the GPU lens band) in flight.

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

**Chartered, deferred (Decision Log 5) — the two-layer CSS body.** Give
the CSS tier the two-component law as a second `backdrop-filter` layer:
a sibling drawn after the sharp layer at σ_b·√(gain² − 1) with `opacity`
= `kScatter` (the sharp layer at σ_b; the composition σ is the law's σ_b·
gain), the host's tint, rim and content painted above both. Evidence:
§5.42 §5 (the sibling form reproduces the mix to RMS 0.0011 in Chromium;
the child form is inert; `css-tier.ts`'s in-place doctrine and the rim's
painting order are the design questions). Acceptance sketch: the dom
checkerboard interiors read the GPU tier's structure (standard deviation
within 0.01 of native at every span), the dom checkerboard means recover
their pre-G1 level, `hc-text` dom rows recover their pre-G1 SSIM, and no
tier-coherence test loosens; the two constants stay shared (K5). Cost the
charter must weigh: two backdrop blurs per surface at the CSS tier;
WebKit's handling of `opacity` on a `backdrop-filter` element is
unmeasured.

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
| W11b | LANDED 2026-09-02 — claims §5.40; the extractor's luminance rule gains an OKLab chroma arm (Δab ≥ 0.03, `--silhouette-chroma-threshold`), a strict superset declared before the bed-wide run; 0 stops, all 230 perceptual rows byte-identical, 23 cells leave the exclusion list and none join, the two W10 contour floors met and removed; enforced count 15; matrix re-measured from the captures on disk (no capture) | landed |
| W11c | IN FLIGHT — **G1 LANDED 2026-09-03** (claims §5.41 declared, §5.42 refereed; Decision Logs 4–5): body σ 1.25, scatter gain 8, floor 0.40, scatter band top 256, fitted on the probe with `rrect-lg` held out; twelve-run referee, 0 stops outside the predicted 2x crossing; three 1x texture floors MET and removed, eight dom floors ratcheted up, four 2x texture floors re-pinned by decision; enforced count 12. **G3 decided:** the CSS claim narrowed, the two-layer CSS body deferred with evidence. **G2 in flight** | in-flight |

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

### Decision Log 3 — W11b's rule, its referee, and close (2026-09-02)

**The rule chosen, and the advisory overturned.** §5.38 §6 (advisory) named
a pure OKLab-ΔE rule; the child's sensitivity run on the captures on disk
falsified it as a replacement (light-solid `rrect-md` reference to 0.031 of
its region in seven bodies at ΔE ≥ 0.03; 22 holes in the CSS checkerboard
`rrect-md`; near-black noise admitted) and adopted the union instead: the
luminance arm unchanged, plus an OKLab a/b arm at 0.03. Rejected: pure ΔE
(above); replacing the threshold space wholesale (any single-space rule
trades one backdrop family for another); a holes arm on the predicate (it
would have EXCLUDED the twenty-three cells rather than measured them). The
overturn is recorded on the child section as a Revision Note and in §5.40.

**The referee.** Every declared stop clear; every declared prediction held
(the tinted `bodiesWeb` family left the exclusion list, the W10 floors met,
the perceptual columns byte-identical, the `areaNative` and `hc-text`
families unmoved). Two floors removed; count 17 → 15; 23 cells newly gate
and every one meets its bounds. Adopted from the scratch matrix (the same
deterministic runs; §5.40's adoption note).

**Consequence for W11c (X4).** The mask is now the union rule's; W11c's
referee reads through it. The material targets on the checkerboard cells
W11c owns did not move (neutral over neutral), so W11c's fit is unaffected.

**Close.** W11b landed on its acceptance; W11c is the last child.

### Decision Log 4 — W11c opened: the body law's form, the 2x position, the order (2026-09-03; user-decided)

**Evidence the round was decided on** (probe bed, native 1x, five spans ×
four pitches; §5.41 carries the tables). In vitrea's own scatter form —
`body = mix(G_σb, G_σb·gain, k)` — the reference is reproduced at RMS
0.0169 (current model 0.0416) only when the mix has a **floor** (k ≈ 0.4 at
spans ≤ 44) and its own band (k still rising at 160; best span max 256):
body σ 1.25, heavy σ 10. The existing `sizeThickness` band (0 at 32,
saturated at 96) reaches RMS 0.024 at best. The photo family improves under
the same law (0.0153 → 0.0135). The 2x reference's interior is a different
object — a moderate single Gaussian (σ 3 CSS px, t 0.41 on `rrect-md`) with
no sharp leak — which vitrea's current model already nearly matches; the
1x law moves two 2x texture rows slightly the wrong way in the dry run.

**Decided (user, 2026-09-03):**

1. **G1's form: the scatter facet gets its own curve.** Two new profile
   constants, `sizeScatterFloor` and `sizeScatterSpanMax`, so
   `kScatter = floor + (1 − floor)·smoothstep(sizeSpanMin, scatterSpanMax,
   span)` (folded by the accessibility cap like every facet); `blurSigma`
   is refit (K5: one number on both tiers); `sizeScatterGainMax` comes off
   the identity. `sizeThickness` itself — and with it the lens, the
   occlusion, the inner shadow and W9's thin/thick response rows — is
   untouched and must read byte-identical on every solid and photo cell's
   level. Rejected: reusing the existing band (cannot reach the floor;
   `rrect-ml` texture stays 0.001 short); keeping σ 3 and widening only
   (the reference's sharp component is near σ 1.25; RMS 0.026 at best).
2. **The 2x position: fit at 1x, predict 2x, hold by decision.** The law
   is fitted on the 1x probe alone. 2x rows that do not meet are held as
   floors with the claim narrowed to the 1x bed until a Retina capture
   exists; a 2x regression past a floor is a stop. Rejected: a device-pixel
   law (overturns "lengths in points" and the 2x reference carries no leak
   to fit); a separate 2x constant set (no 2x probe; three spans to fit on).
3. **G1 then G2, separate capture-and-referee cycles**, for clean
   attribution.

**G1 declaration (written before the fit that lands).** Fit set: the probe
bed's `checkerboard-{8,16,32,64}` × `{rrect-sm, capsule-button, rrect-md,
rrect-ml}` (twenty native 1x cells); `rrect-lg` is holdout and excluded
from the objective. Free: `blurSigma`, `sizeScatterGainMax`,
`sizeScatterFloor`, `sizeScatterSpanMax`; per-cell level and transmission
are nuisance parameters (other rounds' laws own them). Held: every other
constant. Objective: RMS of linear luminance over the deep interior, joint
across pitches within a span. Validation: the photo family's structure RMS
must not rise; 2x by prediction. Referee: the twelve-run capture, whole-bed
scan against the W11b-close matrix. **Stops:** any solid-backdrop cell
moving by more than one code value; any photo cell leaving its bounds; any
2x floor crossed; any dark-profile cell leaving its bounds.

### Decision Log 5 — G1's referee: the 2x stop, the CSS tier, and the close (2026-09-03; user-decided)

**Verdict.** Twelve runs, whole bed against the W11b close (claims §5.42).
No declared stop fired outside the one the declaration predicted: solid
and impulse cells unchanged, `photo` cells inside bounds (max ΔSSIM
0.0033), dark cells inside bounds, no cell newly missing a bound, the
exclusion list unchanged. Three 1x texture-tier floors MET (0.8963 /
0.8987 / 0.8934 against 0.88; `rrect-lg` was the holdout) and removed;
eight dom-tier floors rose by 0.011–0.152 and ratchet up; four 2x
texture-tier floors crossed by 0.0015–0.0083. Enforced count 15 → 12.

**Decided (user, 2026-09-03):**

1. **The 2x stop: adopt G1 and re-pin the four 2x floors** at the new
   measurements, the claim on those rows narrowed to the 1x bed until a
   Retina capture exists. Rejected: holding G1 back (three met floors and
   every dom improvement against four regressions under 0.01).
2. **G3: narrow the claim, charter the two-layer CSS body as deferred
   work.** Measured first (§5.42 §5): a single blur cannot be both sharp
   and faint; the mixed σ the tier runs today is the worst single form on
   the probe (RMS 0.049–0.078 against a best single σ at 0.019–0.052 and
   the GPU law at 0.014–0.028); Chromium renders the two-component law
   exactly as two sibling `backdrop-filter` layers with the heavy one's
   `opacity` as the mix weight (RMS 0.0011), and not at all as a nested
   child. Rejected for now: building the two-layer form inside W11c (it
   changes the tier's in-place, no-proxy doctrine and the rim's painting
   order, for an expected yield of about one dom floor, the rest of the
   dom deficit being the rim band no CSS form carries); narrowing without
   a charter (the evidence is fresh and the route is real).

**Driver note (X1).** A cell's key carries its capture path, which names
the material profile document; when the document's content changes the
twelve runs append beside the previous rows instead of replacing them.
`rm results/matrix.json` before the rebuild, or reduce to the newest cell
per (profile, scene, tier) — the referee did the latter, the canonical
rebuild at recomposition does the former.

**Findings recorded, not acted on.** The CSS tier's checkerboard interior
mean fell 0.008–0.012 (an encoded-space blur's mean moves with σ), and
`hc-text__rrect-md` dom at 1x now reads 0.9029 against ≥ 0.90 — the
nearest any gated row sits to its bound. Both belong to the deferred
two-layer child.

## Surprises & Discoveries

- **Chromium mixes a `backdrop-filter` layer by its opacity — and ignores
  a nested one.** A second sibling layer with the heavy blur at `opacity:
  0.4` over a sharp-blur sibling renders the exact 0.6 / 0.4 mix of the two
  blurs (RMS 0.0011, encoded space); the same layer as a child of the
  sharp one renders nothing of its own. The CSS tier can carry a
  two-component body, but only as a sibling drawn after the host's own
  filter — the fact the deferred charter is built on (§5.42 §5).
- **The CSS tier's level on a structured backdrop moves with its σ.** A
  `blur()` runs in encoded sRGB; on a black-and-white plate its linear
  mean is a function of how much of the checker survives, so G1's softer
  σ lowered the dom checkerboard interiors by 0.008–0.012 with no change
  to any tint constant. The GPU tier, blurring in linear light, held its
  means to 0.0008 (§5.42 §3, §5).

- **The rim band is where the reference is smooth and vitrea is sharp.**
  G2's first readings (2026-09-03, `w11c-lens*` in the job scratch): at
  the 16 px pitch the reference's band inside the contour is a bright rim
  of ≤ 3 px and then ≈ 20 px of structureless glass about 6% darker than
  the deep interior, with checker edges displaced by 7–11 px at depths 8–12
  on the resolved pitches; vitrea's band is a dark ring at depth 1–4 and
  then a sharply refracted, compressed checker (the rim LOD is biased
  sharper by design, `lensRimLodBias` 2.5) whose displacement is attenuated
  by the lens profile twice (magnitude × mix weight) and confined to ≈ 6 px.
  A synthesis model of "displaced plate" fits vitrea's own band at RMS
  0.015 and the reference's at 0.05–0.07 with every parameter at its grid
  edge — the reference's band is not that model. G2's declaration will
  start from a 2-D measurement of the band on the pitch-32/64 probe cells
  rather than from the current shader's form.
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
- **The advisory extractor rule was a regression everywhere it had not been
  measured.** A pure OKLab-ΔE rule looked complete on the `photo` cells and
  would have lost the light-solid reference almost entirely (§5.40). The
  lesson generalises: a replacement instrument rule needs the whole bed's
  backdrop families in its dry run, not the cells that motivated it.
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

- 2026-09-03 (W11c G1 landed; Decision Log 5): the twelve-run referee
  read against the W11b close; three floors removed, eight ratcheted up,
  four re-pinned down by decision, count 12; G3 decided (narrowed; the
  two-layer CSS body chartered as deferred with its evidence); the X1
  driver note added. Two Surprises added. G2 is next.
- 2026-09-02 (W11b landed; Decision Log 3): the extractor's chroma arm
  declared, dry-run, refereed and adopted the same day; two floors removed,
  count 15; W11b's advisory inheritance (§5.38 §6's pure-ΔE rule) overturned
  with the sensitivity evidence, recorded on the child section. One Surprise
  added. W11c is next.
- 2026-09-02 (W11a landed; Decision Log 2): six floors removed, two
  ratcheted up, count 17; the Tracking Map row and claims §5.39 carry the
  evidence. Two Surprises added. W11b is next.
- 2026-09-02 (Decision Log 1 decided by the user): the cut and order
  approved, W11a dispatched, G3 deferred to W11c's referee.
- 2026-09-02 — opened. §5.38 measured; three children cut; Decision Log 1
  awaiting the user's round.
