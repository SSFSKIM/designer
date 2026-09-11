# W27 — the coverage wave: the material's missing states, transitions and foreground, on the WebGPU tier against Apple (2026-09-10)

> **Parent:** the post-v1 wave (`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`), by its
> Decision Log 23 (c) — "then the coverage charters" — and its Outcomes' "Handed to the next cut";
> through it, the root spec `2026-08-24-vitrea-liquid-glass-design.md` (§What remains, item 4,
> "the post-v1 round … opens per #33(a) with the three coverage absences"). **Consumes:** the
> coverage matrix (`2026-08-25-coverage-matrix.md`) as re-scored in its §7 and the companion
> `2026-09-10-coverage-rescore.md`; the grounding of the four candidate children read against
> `main` at `cc89dd2` (0.15.0), summarised in §Design. Children dispatch per their track hint and
> open by citing this document (path + child id).

**Status: CHARTERED 2026-09-10.** W27a dispatched the same day (autonomous, worktree). The rest
dispatch in the order of §Ordering.

## Purpose

Eighteen consecutive waves (W9–W26, 2026-09-01 → 2026-09-10) fitted the optics of one material
variant on a static bed, and by W26 the instrument had reached the fixtures' own resolution: about
one display code of Apple's thick interior is not a convolution of the backdrop at all (claims
§5.121), and the reference every constant was fitted to is macOS 26.5, a version Apple has
announced it is superseding with a changed material. Over the same ten days the coverage of the
native *system* moved by six rows out of 174.

This wave turns to the system. Re-scored on 2026-09-10 (matrix §7), 40 native items remain
absent and never ruled on, and the grounding found that four of the highest-value ones are cheaper
and better instrumented than the record suggested: the inactive-window material has a complete
matched reference bed already in git history; Apple's vibrancy operator is a colour matrix already
sitting unread in 58 committed layer dumps; the toolbar's split is a partition the runtime already
performs by hand in the demo; and the materialization channel is declared, driven and pinned at 1
by a test, reaching nothing. The wave lands those, closes the defects the grounding tripped over on
the way, and gives the WebGPU tier a real material over ordinary page content, which is what an
adopter meets first and what the demo never shows.

The user's framing, recorded verbatim as the wave's boundary: *"WebGPU is what we compare with
Apple"* — not that the CSS tier is dropped. And the component question, answered: vitrea stays *a
material plus reference controls*; it does not grow a widget layer in this wave.

## Parent-Level Acceptance

The wave is closed by recomposition when all of the following hold on `main`, verified against the
shipped packages and the live demo, not the sum of child gates:

1. **The matrix moves by build, not by ruling.** A re-score of `2026-08-25-coverage-matrix.md`
   after the last child lands shows, at minimum: toolbar group management (§1.6) and `Glass.tint`
   on buttons `replicated`; `Glass.identity`, the `materialize` transition kind and the
   materialize/dematerialize row (§1.1, §1.3, §3.5) `replicated, unmeasured` with the motion axis
   named as the reason; window focus state (§3.6) `replicated+measured` against the recovered
   inactive bed; vibrancy and its named levels (§3.9) `replicated+measured` on vitrea's own
   controls against Apple's operator; and the WebGPU tier over a DOM-sourced group drawing the
   profile's material rather than an unsampled flat (a row the matrix never enumerated, added
   under §3.7 by the recomposition). The re-score is appended to the matrix's §7 beside the
   2026-09-10 one.
2. **Every feature is reachable and shown.** Each landed feature has a public prop or option on
   the React binding *and* on the framework-agnostic host entry, a README paragraph in the package
   that carries it, and a live instance in the demo or the playground that a reader can operate.
3. **The bed is no worse and the resting material is unchanged where the child promised it.**
   The enforced floors in `adopted-thresholds.test.ts` are unchanged or come off by fix; the
   holdout is read once per configuration that changes what draws; W27a, W27b and W27d leave every
   golden and every calibration digest byte-identical at rest, proven by the isolation spec and a
   from-empty rebuild at their landings.
4. **The CSS tier still derives.** `tier-coherence.test.ts` and the dom floors pass unchanged at
   every landing; a feature the CSS tier cannot carry is recorded in the claims ledger as a named
   residual, never silently absent.
5. **Released** as one `@vitreajs/vitrea-web` minor cut (0.16.0 or the next free minor) after the
   user's eye on the landing sheets, with the wave's changesets in the fixed group.

## Grounding Baseline

From the 2026-09-10 re-score (matrix §7), over 155 scoreable rows: replicated and measured 41
(26%), replicated unmeasured 25, partial 26, excluded by decision 23, absent and undecided 40
(26%). The rows this wave targets, with their status at the cut:

| row | matrix | status 2026-09-10 | owner |
| --- | --- | --- | --- |
| `Glass.tint` reachable on `GlassButton`; group tint per the 0.2.0 changelog | §1.1, §1.6 | published API that the React binding does not expose (defects) | W27a |
| The no-hint ink path decided by scheme (tracker, "The untinted material's ink…") | §3.3 | open defect, the 1.24-contrast class | W27a |
| Lens channel clamped at 1 in the renderer; no interaction reaches the shader | §3.6 | untracked defect found by the grounding | W27a |
| Vibrancy's named levels and floor | §3.9 | `absent, undecided` | W27a (tokens), W27e (semantics) |
| `ToolbarSpacer` / `sharedBackgroundVisibility` | §1.6, §2 | `absent, undecided` (a `groupId` lever exists) | W27b |
| Window / scene focus state | §3.6 | `excluded by decision`, bed preserved | W27c |
| `Glass.identity`, `GlassEffectTransition.materialize`, materialize-not-fade | §1.1, §1.3, §3.5 | `absent` / `partial` / `partial` | W27d |
| Vibrancy as the automatic foreground | §3.9 | `absent, undecided` | W27e |
| The WebGPU tier over a DOM-sourced group | not enumerated (claims §5.77 §4) | flat white unsampled material, `tint [1,1,1]` at α 0.665 | W27f |

Sizes from the grounding, in agent-hours: W27a ≈ 12; W27b 12–16; W27c 28–46 on the recovered bed;
W27d 20–30 as a behavioural wave; W27e 30–45; W27f not grounded at the cut (its own G0 sizes it).

## Design

Thin by construction: the six children share no design surface beyond the contracts below, so
this section records what the joint view settled and hands the rest down as advisory inheritance.

### The tier boundary **[binding — the user's ruling, extending the parent's Decision Log 23]**

Every measured acceptance, capture-bed claim and floor in this wave is stated against the WebGPU
tier. No CSS cell gates a child. Features that are API or composition rather than optics (the
transitions, the toolbar partition, the activation pose, the foreground tokens) land on whichever
tier the root resolved to, drawn with what that tier can carry; the CSS tier keeps deriving from
the shared profile as today, the coherence pin stays, and a CSS-only fidelity residual is written
into the ledger rather than chartered.

### Where each feature lives

- **Activation is a pose of the root, not a state of a surface** [binding — joint view: a window's
  activation is one fact per document; `resolveInteractionState` names one state at a time by
  precedence, so a seventh member would force an answer to "does inactive outrank hover?" that has
  no correct value, and it trips a published contract (`VITREA_CONTRACTS.interactionStates`) and
  two deliberate tripwire tests]. It takes the colour-scheme seam: an observer with a
  read-and-subscribe shape (`window` focus/blur plus `document.hasFocus()` through the supplied
  `view`; not `visibilitychange`, which stays `visible` for an unfocused window), a
  `recededMaterialProfile` difference document indexed by the resolved colour scheme beside
  `dark-profile.ts`, `applyMaterialProfile` as
  the one path, a `windowActivation: "auto" | "active" | "inactive"` option on the root and prop on
  `<GlassRoot>`. Two frozen endpoint documents, never a blended profile: the cell key embeds the
  profile SHA, so a blend is not a measurable configuration; the transit is the CSS tier's armed
  transitions and the GPU tier's per-frame uniforms. Apple's per-element recede ("element overlap
  and focus state"; the sheet) is not this wave's — it belongs with the excluded sheet.
- **Presence, not alpha** [binding — Apple's stated rule ("prefer setting the effect property over
  the alpha"; materialize "by gradually modulating the light bending and lensing") and the
  runtime's own constraint: any `opacity < 1` on a host or ancestor forms a Backdrop Root and kills
  the group's proxy sampling]. `materialization ∈ [0, 1]` is a per-surface presence that scales the
  material's optical terms — lens depth, body mix toward the unblurred backdrop, tint alpha, rim,
  inner and outer shadow, glow — and never the element's opacity; at 0 the surface reads as if no
  glass were applied, which is `Glass.identity`. A `getComputedStyle(host).opacity === "1"`
  assertion on every frame is the machine-checkable form. *Advisory:* the mechanism the grounding
  found cheapest is one per-instance scalar (the instance struct has one free slot) applied as a
  multiplier to the group's uniforms in the field and optics passes, rather than promoting the four
  per-group scalars to per-surface; lens-only was rejected because it delivers `.materialize` while
  splitting `.identity` off from it, and the matrix records the three Apple items as one capability
  seen from three angles.
- **The toolbar partition is a sampling-group partition** [binding — joint view: union and proxies
  are already per group, `GlassGroup` renders no DOM, and `membersOf` orders the roving tab stop
  document-wide, so a split changes grouping and nothing else]. A split yields one `role="toolbar"`
  with N sampling groups, never N toolbars. Both of Apple's shapes ship because they reduce to one
  rule: children are partitioned at each `GlassToolbarSpacer` and at each item that declares
  `sharedBackground="hidden"` (which becomes its own group). The gap between adjacent groups'
  padded proxies must clear the *live* sampling padding (24 CSS px at nominal σ 8, 42 under Reduce
  Transparency), read from the resolved policy, never a constant.
- **The foreground: an operator on vitrea's own controls, a token elsewhere** [binding — the
  user's ruling]. Apple transforms the app's own text colour; vitrea publishes a colour an app opts
  into, and Decision Log #34(c) of the root spec was won at cost so that an app's own rule beats the
  runtime. The wave keeps both true: `GlassButton`, `GlassIconButton`, `GlassSegmentedControl` and
  `GlassToolbar` labels receive the vibrant operator by default (vitrea owns those labels);
  arbitrary content under `GlassSurface asChild` keeps the token unless the author opts in
  (`foreground="vibrant"`). The operator is fitted to Apple's `vibrantColorMatrix` as read from the
  committed layer dumps, not to pixels of text; the no-text fixture rule stands. *Advisory:* the
  grounding's tier note — on the CSS tier the host is `isolation: isolate` so a blend composites
  against exactly the material; on the WebGPU tier the host is not a stacking context and would
  composite against the root's buffer — is the first thing W27e's G0 settles empirically through the
  probe machinery, and the GPU tier's answer is the one that counts (§The tier boundary).
- **Page content on the WebGPU tier gets the material, not a flat** [binding — the parent's
  Decision Log 23 (c)]. Over a DOM-sourced group the renderer resolves `samplingBackend:
  "css-backdrop"`, `refraction: "approximate"`, `analysis: "none" | "hint"` and paints an
  `unsampledMaterial` of `tint [1, 1, 1]` at α 0.665 (claims §5.77 §4). W27f replaces the flat with
  the profile's material at the hinted level: the same body, tint shade, rim and shadow the sampled
  path draws, evaluated at the group's backdrop tone (the author hint, else the tier's own sampled
  tone) with no lens. Refraction over DOM stays a seam (HTML-in-Canvas is not opened by this wave;
  Decision Log 3).
- **Prominent is held** [decision, W27 Decision Log 6]: Apple's `.glassProminent` differs from a
  tinted glass button by an accent-colour default and a vibrant label, and vitrea has neither until
  W27e. W27a makes the tinted button reachable; the *name* waits for the label.

### Delegated unknowns

- The inactive pose's four facets (less backdrop lift, less structure retained, tint dropped, no
  outer shadow) as one difference document: which profile fields, at what values, fitted on the
  recovered bed — W27c G1.
- What `vibrantColorMatrix`'s four variants are a function of (the grounding reads backdrop
  luminance × element size, flipping for the small element only) and whether one operator with
  the material's own level as input reproduces all four — W27e G0/G1.
- The hinted-level material's error against the sampled path on the same scene, and against the
  native stack cell — W27f G0.
- Whether the transitions' duration and easing have any reference at all; the wave assumes not and
  says so — W27d.

## Children

### W27a: The fix batch — autonomous — DISPATCHED 2026-09-10

- **Purpose:** Five items the grounding tripped over, each a defect or an omission the record
  already names, closed before the features that depend on them: `GlassButton`'s prop allow-list
  omits `tint` and `foreground`; the group tint the 0.2.0 changelog documents does not exist on
  `GlassGroupProps`; the no-hint ink path is still decided by the colour scheme (the tracker's
  1.24-contrast class); the renderer clamps `lensStrength` at 1 so hover, focus and press never
  reach the shader; and the named foreground levels can be published today from the level vitrea
  already computes.
- **Acceptance:** each item closed with a fail-before test and no assertion loosened; the resting
  material byte-identical (goldens unmoved — a golden that moves stops the item); the tracker entry
  marked closed in place; changesets in the fixed group; suites and the Chromium e2e green.
- **Edges:** blocked-by: —; blocks: W27b (the tinted button in the demo), W27d (shares
  `instances.ts`), W27e (the token names).
- **Contracts:** X2, X4.
- **Design inheritance:** §Where each feature lives (prominent held).
- **Required:** yes — acceptance 1 and 3.
- **Status:** in-flight (worktree agent, 2026-09-10).

### W27b: The toolbar partition — autonomous

- **Purpose:** Apple's whole vocabulary for a toolbar's shared glass background — `ToolbarSpacer`
  and `sharedBackgroundVisibility(.hidden)` — as one partition rule on `GlassToolbar`, so an author
  can put a primary action in its own body and keep the rest merged, the way every system bar does.
- **Acceptance:** `GlassToolbarSpacer` and a per-item `sharedBackground` prop partition the
  toolbar's children into N sampling groups under one `role="toolbar"`; the roving tab order is
  unchanged (test); adjacent groups' proxies never overlap at any accessibility setting (the gap
  derives from the live sampling padding; a test under `reducedTransparency` proves it and the
  `proxy-overlap-after-enforcement` diagnostic stays silent); the demo's hand-split toolbar
  (`apps/demo/src/App.tsx`) is rewritten on the API and the comment that explained the hand
  partition retired; the resting bed byte-identical; a README paragraph; a react changeset.
- **Edges:** blocked-by: W27a; blocks: —.
- **Contracts:** X2, X5.
- **Design inheritance:** §Where each feature lives (the partition; prominent held).
- **Required:** yes — acceptance 1, 2.
- **Status:** CLOSED 2026-09-10 (worktree agent, on `main` at `bc14af9`). The rule landed as
  written; the gap's *number* is derived from the material rather than from the two constants
  §Design names, which were σ = 8's and are no longer the material's — see Surprises and
  Revision Notes.

### W27c: Window activation — controlled

- **Purpose:** "When a window loses focus on the Mac or iPad, Liquid Glass shifts its appearance
  and visually recedes" (S219). The inactive material is the pose the project's capture history
  recorded by accident for its first week, and the tree before the re-baseline holds it for all
  121 fixtures over byte-identical backgrounds. Ship the recede as a pose of the root, measured
  against that bed.
- **Acceptance:** five gates. **G0 (measure):** the recede read on the recovered bed for every
  matched pair as a per-cell table of the four facets, with the recovered bed's provenance written
  into the claims ledger (schema 2, single run, pose inferred from the DL14 post-mortem, 37 of
  today's 92 scenes; admitted by Decision Log 5). **G1 (fit):** a `recededMaterialProfile`
  difference document fitted on the light and dark calibration pairs, holdout read once, declared
  and dry-run against the active bed byte-identical. **G1b (check; added 2026-09-11, Decision
  Log 12):** the spent holdout's mean is seven to eight times the calibration mean on the standard
  profiles (§5.130 §7), so before any runtime hook: the five residuals that section names — the
  dark mid-dark-solid level the three-anchor response misidentifies, the light checker's far-span
  scatter, the dark photo rrect-lg's colour/spatial miss, the light photo stacks, and neutral tint
  removing background chroma — each classified as model-form or bed on the evidence already
  committed, with the transfer/scatter experiment that would decide it declared before it runs;
  then one unspent checking bed captured natively (a fresh inactive session on the user's
  machine, or the OS 27 bed as new profile keys) and read once against the frozen G1 endpoint
  within a bound declared before the read. G2 stays blocked until that read holds: a pose proven
  only where it was fitted is not shipped. **G2 (runtime):** the activation observer,
  the root option and React prop, `setWindowActivation`, the pose applied through
  `applyMaterialProfile`, the transit through the existing transitions, tests on three engines
  that the pose follows `document.hasFocus()` and an explicit override wins. **G3 (land):** the
  inactive cells enter the matrix as a scene `state` (X3), floors adopted for the inactive rows at
  the light and dark calibration bounds, the active bed unmoved, the demo showing the recede when
  its window is backgrounded, the user's eye on the pair sheets.
- **Edges:** blocked-by: — for G0 and G1 (measurement and fit touch no source the others touch);
  W27a for G2 onward (shared `root.ts` edits); blocks: —.
- **Contracts:** X1, X2, X3, X7.
- **Design inheritance:** §Where each feature lives (activation as a root pose) [binding];
  the four-facet reading and the `dark-profile.ts` template (advisory).
- **Required:** yes — acceptance 1, 3.
- **Status:** G0 closed; G1 fitted and declared 2026-09-10 (claims §5.130), reviewed by the
  parent and merged (`f8c38a2`). The corrected 30-cell holdout is spent; photo chroma, mid-dark
  response and far-span scatter remain explicit gaps, so G1 does not establish G3's inactive
  floors. **G1b's analysis half CLOSED 2026-09-11 (claims §5.134):** the five residuals are
  classified — (a) the mid-dark anchor **bed**, (b) far-span scatter and (c)/(e) the photo's
  chroma transfer **model-form**, (d) the stacks **metrology** — the transfer/scatter experiment
  and the unspent checking bed are declared, and the bound is stated before the read. The gate
  also found that the "seven to eight times" its own charter rests on is a full-canvas statistic
  over sets whose footprints differ 3.08–3.68×; on the interior mask the light and accessibility
  holdout **means** are at or below their own validation level and all 30 spent cells clear the
  active bed's adopted *ceiling*, while the dark pair is genuinely 3.5× worse on two cells. That
  narrows what is unproven rather than how much: retro-applied jointly, G1b's own bound still
  fails four of six profiles, the two light standard ones on its per-cell clause through the
  tinted photo `rrect-lg`. G2 (the
  activation observer and `windowActivation`) and G3 (the landing, with the demo's inactive rows)
  stay HELD by the user (Decision Log 12); the evidence narrows what they are held on and no gate
  is unblocked by the analysis. G1b's **capture half is blocked on the user**: there is no native
  inactive capture path at all (the tracker's entry), the bed costs 8.3 h of the machine at the
  freeze bar and 11–21 h with attempt loss rather than Decision Log 5's one to two, and the OS 27
  bed cannot check the 26.5 endpoint because 27 changes the material. Reviewed independently at
  `4f90e05`, which confirmed the gate's four load-bearing claims and returned eight artifact
  defects, all fixed in place before the declaration landed (claims §5.134's verification record).

### W27d: Identity and materialize — controlled

- **Purpose:** `Glass.identity` is Apple's documented way to animate glass to nothing in place;
  `GlassEffectTransition.materialize` fades content while the material materializes without
  matching a neighbour's geometry; and Apple states that materializing is not a fade. vitrea has
  the channel and no way to reach it. Give a surface a presence and let the material follow it.
- **Acceptance:** a `present` prop on `GlassSurface` (and option on the host entry) drives
  `materialization` from 1 to 0 and back through the motion kernel's existing driver; the channel
  crosses the publication seam and reaches both tiers; on the WebGPU tier one `chromium-gpu` A/B
  proves a channel value reaches the shader (`maxChannelDelta > 8` at presence 0.35 against 1),
  the first such proof for any motion channel; on three engines the recorded per-frame trace is
  monotone, lands exactly on 0 within the driver's duration plus one frame, and
  `getComputedStyle(host).opacity` is `"1"` on every frame; `GlassMorph` gains a `transition`
  prop with `matchedGeometry` (today's behaviour) and `materialize` (content crossfade, material
  presence, no geometry match); the `states.test.ts` doctrine that no *interaction* state may touch
  materialization is kept and restated (presence is authored, not a state); reduced motion's
  treatment of the optical channel decided and tested; the resting bed byte-identical; the wave
  records in the claims ledger that the transition's timing has no reference and is unmeasured.
- **Edges:** blocked-by: W27a (`instances.ts`); blocks: —.
- **Contracts:** X2, X6.
- **Design inheritance:** §Where each feature lives (presence, not alpha) [binding]; the
  per-instance scalar mechanism (advisory).
- **Required:** yes — acceptance 1, 2.
- **Status:** CLOSED 2026-09-11, merged `108b40d` after two review rounds (the six-lane panel
  against `313fa2b`, then a single reviewer over the merge and the fixes alone, which returned
  no findings). See the Tracking Map row and claims §5.132's verification record.

### W27e: Vibrancy — controlled

- **Purpose:** "The label automatically becomes vibrant, based on its textColor" (S284). It is the
  mechanism by which anything on Apple's glass stays legible, it is automatic on the native side,
  and vitrea's foreground is a threshold between two hexes. Apple's operator is a 5×4 colour
  matrix on every glass layer, committed in 58 layer dumps. Fit it and apply it where vitrea owns
  the label.
- **Acceptance:** four gates. **G0 (mine):** every `vibrantColorMatrix` in the committed dumps
  tabulated against its cell's backdrop tone, span, scheme and tint; the number of distinct
  operators and what selects between them, stated; the tier composite question (which buffer a
  blended label composes against on each tier) settled by the probe machinery. **G1 (fit):** one
  operator with the material's own level (and, if G0 requires it, span) as input reproducing every
  dump's matrix within a declared tolerance, holdout dumps read once. **G2 (implement):** the
  operator applied to vitrea's own controls' labels by default and to `asChild` content under
  `foreground="vibrant"`, on the WebGPU tier as the reference and on the CSS tier as a derivation
  with its residual named; the existing token path kept for everything else; the crossfade the
  `foregroundTone` channel already declares consumed at last; the named levels of W27a re-derived
  through the operator; and, closing the parent's acceptance clause 2 for W27a (Surprises,
  2026-09-11), one playground plate a reader can operate that shows a tinted `GlassButton`, a
  `GlassGroup tint` and all four named ink levels live. **G3 (land):** the demo's contrast harness run on every glass label in the
  demo and its results recorded, the ~13 ink assertions re-baselined with each move attributed,
  the claims ledger §3.3 rewritten (it currently says the foreground is not a contrast calculation),
  the user's eye.
- **Edges:** blocked-by: W27a (token names); ordered after W27b and W27d land (shared React
  files); blocks: the "prominent" name (Deferred).
- **Contracts:** X1, X2, X4.
- **Design inheritance:** §Where each feature lives (operator on own controls, token elsewhere)
  [binding]; the layer-dump path over pixels (binding — the no-text fixture rule stands).
- **Required:** yes — acceptance 1, 2.
- **Status:** G0 CLOSED 2026-09-11 (claims §5.133). The corpus is 57 dumps and 60 occurrences in 4
  distinct matrices, and the reading changes the gate's premise: **58 occurrences are on the
  surface's own highlight layer and 2 on the author tint's gradient layer; none is on a label**,
  because the reference harness renders `Color.clear` inside every `glassEffect` by rule. The
  foreground operators number **2**, not the grounding's 4 (the other two matrices are the tint's
  backdrop-aware colorize). Both factor exactly as `out = m·c + g·Y(c) + b` on Rec.709 luma —
  an affine level map plus a saturation — at (m 1.5, a 0.1, b 0.9) and (m 3.0, a 1.35, b 0.15).
  The selector is backdrop tone and span **jointly** — neither alone: the same dark-solid backdrop
  switches at span 44 and does not at span 96, and no span switches over a lighter backdrop — and
  the switch is binary. `backdropToneAdaptation(tone, sizeThickness(span))` at the
  shipped profile reads exactly 1.0 on the two switching cells and ≤ 0.0077 on the other 56, and
  Apple's own face fill flips white→black on exactly those two. The tier composite question is
  settled in real Chromium: on **both** tiers a blended label composes against the material's
  composite and never the page, because vitrea's glass root is a stacking context — but a
  `mix-blend-mode` inside the host collapses `backdrop-filter` sampling for a group whose proxy is
  outside that element's subtree (one group per probe case, so the "every group under the root"
  universal is an extrapolation), so on a `css-backdrop` group the operator's darkening has to be
  folded into the ink on the CPU, while on a `gpu-texture` group Apple's literal pipeline works and
  is exact. The colour
  transform itself is exactly a CSS `filter: url(#m)` with `feColorMatrix` and
  `color-interpolation-filters: sRGB`, reproduced to the code value on both operators. G1's premise
  moves with all this: the operator's form needs no fit, the selector does, and whether a *label*
  carries this operator at all needs one `dump-layers` run on a labelled probe scene — which
  breaches no fixture rule, because a dump captures no pixels. G1 is not dispatched at this gate.

### W27f: The material over page content — controlled

- **Purpose:** On the WebGPU tier a group whose backdrop is ordinary page content draws a flat
  white at α 0.665 over a CSS blur, a different material from the one the CSS tier draws on the
  same page and from the one the sampled path draws on a texture. That is what a real adopter's
  first surface looks like, and the demo never shows it because every demo backdrop is a
  registered texture. Replace the flat with the profile's material at the hinted level.
- **Acceptance:** three gates. **G0 (measure):** the unsampled path's output against the sampled
  path's on the same scene at the same hinted tone, per term (body level, tint shade, rim, shadow),
  and against the native stack cell (`photo__glass-over-glass`'s overlay, claims §5.77 §4), with
  the CSS tier's reading beside for the record; the demo gains one DOM-backdrop stage so the path
  is visible. **G1 (derive and declare):** the unsampled material derived from the profile at the
  hinted level — the body's response, the tint shade at that level, the rim's amplitude law, the
  outer shadow's two terms — with no lens, declared as one function the CSS tier's mirror can also
  read, dry-run with the stack cells and holdout read once. **G2 (land):** the stack cells' overlay
  within a declared bound of the native overlay, the sampled path byte-identical, the CSS tier's
  coherence on DOM-sourced groups measured and recorded, the user's eye on the demo's DOM stage.
- **Edges:** blocked-by: —; blocks: —. Parallel-safe with W27c G0/G1 (different files).
- **Contracts:** X1, X2.
- **Design inheritance:** §Where each feature lives (page content gets the material) [binding];
  HTML-in-Canvas stays a seam (Decision Log 3).
- **Required:** yes — acceptance 1, 2, 3.
- **Status:** G0 completed (claims §5.129); G1 completed (claims §5.131, 2026-09-10) and merged
  (`6ae37c1`): shared profile-at-tone derivation, sampled-source identity, both schemes and the
  full once-read holdout recorded. **G2 completed 2026-09-11 (claims §5.135)**: the native stack
  envelope decided from S0 and S1 apart, the bound declared before the read and met in every
  clause, all eighteen overlay readings reproducing §5.131 §6 to six decimal places, the sampled
  path byte-identical (20/20 and 2/2 per scheme), the CSS tier's coherence on DOM-sourced groups
  recorded under X1, and the eye sheet prepared. **The bound is adopted**; the dark photo stack
  stays unbounded for want of a native fixture, and the two dark-checker overlay regressions
  §5.131 §6 names are pinned, not closed. **The user's acceptance of `/#page` is still not
  claimed** — the sheet is prepared and the eye is the parent's to take.

## Cross-Child Contracts

- **X1 — the tier boundary.** Owner: this document (§Design, binding). Binds W27c, W27e, W27f:
  every measured claim is on the WebGPU tier; the CSS tier derives and its residual is written.
- **X2 — public surface is a semver event.** Owner: the release checklist (`c9d-release-checklist.md`)
  and the fixed changeset group. Binds all. Adding a channel, a state, a token name or a prop is a
  minor on the package that carries it; `VITREA_CONTRACTS` (core) republishes the channel and state
  tables, so a change there is a core minor. Each child writes its changeset; the wave cuts once.
- **X3 — scene axes extend the set, never the key grammar.** Owner: `calibration/test/scene-matrix.test.ts`.
  Binds W27c: the inactive pose is a scene `state` (`checkerboard__rrect-md__inactive`), never a
  profile-key segment; N scenes → 2N fixtures → 4N cells, additive.
- **X4 — the foreground token vocabulary.** Owner: W27a for the names (`--vitrea-foreground`,
  `-secondary`, `-tertiary`, `-quaternary`), W27e for what computes them. W27e keeps every name
  W27a publishes and changes only their derivation.
- **X5 — a toolbar split is a sampling-group partition.** Owner: W27b. One `role="toolbar"`, N
  groups; the inter-group gap clears the live sampling padding. The demo consumes it.
- **X6 — presence never touches element opacity.** Owner: W27d. `materialization` scales optical
  terms; `opacity` stays 1 on the host and every ancestor the runtime writes (a sub-1 opacity forms
  a Backdrop Root). Outlives the wave: promote to the root's rendering contract at close.
- **X7 — activation is a root pose with two frozen endpoints.** Owner: W27c. Not an interaction
  state; two profile documents, the transit through existing transitions; the cell key's profile
  SHA is the active document's, the pose is the scene's `state`.
- **X9 — identity leaves content as the app wrote it.** Owner: W27d for the rule, W27e for the
  hook (added 2026-09-10 from W27d's flow-back). At presence 0 the host's semantics and the
  published ink token stay (identity is optical absence, not unmount), and the app owns its content
  over the uncovered backdrop. When the vibrant operator lands it scales with presence and reaches
  the app's own colour at 0, because Apple's identity leaves content "as if no glass effect was
  applied"; the token path W27d leaves untouched is where that hook goes. Never an opacity side
  effect (X6).
- **X8 — what was not measured is written down.** Owner: each child, in `c9a-fidelity-claims.md`.
  W27d's timing has no reference; W27e is fitted to coefficients, not pixels; W27c's bed is
  pre-attestation; W27f's stack bound is one cell's. Each is a named line in the ledger at landing.

## Ordering & Dependency Map

```
W27a ──┬── W27b ──┐
       ├── W27d ──┼── W27e ── recomposition ── the cut
       └── W27c G2+ ┘
W27c G0, G1 ── (parallel from the start)
W27f ─────────── (parallel from the start)
```

W27a first: three of its items are the levers the others pull. W27c G0/G1 and W27f run beside it
from the start; they touch the calibration results and the renderer's unsampled path, not the
React surface. W27b and W27d follow W27a in parallel (different files: controls versus the
channel seam). W27e is deliberately last among the features: it is the largest, it re-baselines
a dozen ink assertions, and it wants W27b's and W27d's React edits landed first. The cut follows
the recomposition and the user's eye.

## Risks & Mitigations

- *The lens-clamp fix (W27a item 4) changes the GPU tier's hover and press look.* Mitigated: the
  resting channel is exactly 1, so goldens must stay byte-identical, and the item stops if one
  moves. The pressed material has no reference (the native pressed fixtures are byte-identical to
  rest), so the interaction look is by design, not by measurement; recorded under X8.
- *A recovered, pre-attestation bed as a fidelity reference (W27c).* Mitigated by Decision Log 5's
  reasoning (the inactive material was found static across runs) and by X8: the provenance is in
  the ledger, and one attested session can be added later without re-fitting if the user wants
  the pose attested per cell.
- *Fitting to Apple's coefficients rather than pixels (W27e) is a first for the project.* Mitigated:
  the coefficients are Apple's own operator, read from Apple's own layer tree, and the demo's
  contrast harness measures the pixel outcome at G3.
- *W27f changes what draws on every DOM-backed WebGPU page.* Mitigated: the sampled path is
  byte-identical by acceptance, the stack cells bound the change, and the demo gains the stage that
  shows it.
- *The reference moves to OS 27 mid-wave.* No child fits against new captures except W27c's
  inactive bed, which is 26.5 by construction. The recapture is a separate item (Deferred).

## Deferred / Out of Scope

**Deferred (may return):** the name "prominent" (`GlassButton prominent` = accent tint + vibrant
label; opens when W27e lands); the motion-metrics harness (no native frame sequence has ever been
captured; the parent's Decision Log 23 (c) charters it after this wave); the OS 27 recapture
(macOS 27 ships publicly 2026-09-14; captured as new `apple-macos-27.0-…` profile keys beside the
frozen 26.5 ones, never replacing them; see Revision Notes); Apple's per-element recede
("element overlap") and the sheet's recede-opacify-grow; an HTML-in-Canvas or element-texture
spike for real refraction over page content; ambient colour spill from nearby content; transient
lift-into-glass; touch-versus-pointer intensity; Show Button Shapes and Differentiate Without
Color; the concentricity distance gradient and the window corner at the top of the chain; the
component families the root excluded (tab bar, sheet, popover, slider, toggle, search field), by
the user's answer at this cut ("material plus reference controls").

**W27d follow-up:** fractional-presence union geometry and nearest-field ownership (a weak
member still grows a neck and can own an overlap until exactly 0; multiplying the blend by
`min(pA, pB)` removes only the bulge, so that partial law was not added); fractional
stacked-backdrop tone prediction (carry the existing per-term presence fold into the predictor
and check GPU output, with no new fitted coefficient); the CSS transit's two-layer/tint-transfer
approximation; and unequal fractional proxy presence on engines whose mask-on-backdrop row is
unverified. Identity endpoints are exact, not deferred. Claims §5.132 records the evidence and
the W27e handoff: the vibrant operator must scale with presence and reach app-authored color at 0.

**Decided, not deferred (Decision Log 11, 2026-09-11):** host presence is always built on
`DEFAULT_MOTION_PROFILE`, so an author's `profile` retunes the bindings' content crossfade and
not the material's own arrival. That is the design as landed — presence is driven once by the
framework-agnostic root, which has no motion-profile input — and giving that root one is new
public surface on the package that carries it, which is why it was not taken there; the user has
since kept it as built (Decision Log 11). Both READMEs
state the limit at the point where the 220 ms ease is named; claims §5.132 §6 records it. The
group's proxy σ, likewise derived from every measured member regardless of presence, is
recorded in §5.132 §4 rather than deferred: deriving it from positive members only would make
the radius a function of presence and step a sibling's frost at the endpoint, which is the same
fractional union law already above.

**Explicitly out of scope (standing exclusions, unchanged):** WebGL2; a widget layer; scroll-edge
effects (the root's exclusion stands; overturning it is a product decision not taken here);
neighbour glow diffusion; topology-changing morphs.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| W27a | LANDED 2026-09-10 (merged `bc14af9`; seven commits plus three review fixes): `GlassButton`/`GlassIconButton` forward `tint` and `foreground` (the README's flagship tint example had not compiled); `GlassGroup` gains the `tint` the 0.2.0 changelog promised, parsed per document; the no-hint ink guards removed on both tiers with five assertions re-pinned stricter (tracker entry closed in place); the renderer's `lensStrength` clamp at 1 lifted to a finite guard of 4 with NaN resolving to the idle 1 (goldens 33/33 unmoved); four named ink levels published on both tiers, secondary solved per surface against the actual composite colour over the whole bracket (Decision Log 9). Review: two P1s on the ink floor (chromatic tint, unresolved level) fixed with fail-before tests measuring the real contrast; two P2s (adopted stylesheets, Infinity in the Float32Array) fixed. Two gaps logged, not closed: the dark scheme's primary ink at WCAG 4.945 with nothing watching it; `lensDepthPx` ignoring `lensStrength`. Main after merge: build, lint, all unit suites green (2004 tests), demo e2e 48. **Acceptance clause 2 unmet for three items (found on the 0.16.0 eye sheet, 2026-09-11; Surprises):** the tinted `GlassButton`, `GlassGroup tint` and the four named ink levels have their props and README paragraphs but no live instance in the demo or playground; W27e G2 closes it | landed; clause 2 open on three items |
| W27b | worktree agent, dispatched 2026-09-10 after W27a's merge; 14 commits `bc14af9..b59a585`; merged `38d782c` | CLOSED 2026-09-10 (one `role="toolbar"`, N groups; `GlassToolbarSpacer` and `sharedBackground="hidden"` as one partition rule; the gap derived through `samplingPaddingFor` over every group the toolbar registers, not the row's own props; the playground's hand split rewritten on the API; goldens and the resting bed unmoved. Review: two defects fixed before the head — the gap read only the toolbar's own material, then the first fix folded the toolbar's props in as a floor — final head reviewed correct. At the head: 2028 unit tests, platform-web 388, react e2e 114 on three engines, demo e2e 48) |
| W27c | G0 CLOSED 2026-09-10 (merged `7312fd0`; claims §5.128: all 121 pairs read; the outer shadow and the bright rim go to zero in every profile at both scales, structure retained falls, an author tint loses its hue entirely while its darkening stays — orange and blue capsules both settle at Y 0.451 against the untinted 0.606 — and no existing field expresses that; dark untinted glass and both accessibility bodies *brighten*; four cells background-identical; the 2x dark photo capsule's active side is the 1-of-17 minority state and is excluded from the fit) / G1 declared 2026-09-10, claims §5.130: scheme-indexed endpoint, two identity-default tint fields, 121 recovered fixtures, corrected 62-cell fit and 16-cell validation, one 30-cell holdout spent; all four review findings fixed | G1 LANDED (merged `f8c38a2` after the parent's review; holdout residuals explicit, no inactive floors adopted). G2 and G3 HELD by the user (Decision Log 12). **G1b analysis half CLOSED 2026-09-11** (worktree agent, claims §5.134, evidence `packages/calibration/results/2026-09-11-w27c-g1b/`): nothing fitted, captured or adopted; the five residuals classified with their deciding cells — mid-dark anchor **bed** (`backdropToneAnchorX[1]` is `mid-dark-solid`'s encoded mean exactly, and the active profiles read their middle ordinates off a probe grid the recovered bed has not got), far-span scatter **model-form** (the active bed's own fitted far anchors still leave span 160 at 1.21–1.33× native SD), dark photo colour and the tinted photo's lost background chroma **model-form on one cause** (the reference's inactive material transmits *more* chroma than its active one, rising with span, while the body lerp's alpha — the one field that governs chroma transmission — is left where the active pose put it in both schemes, light inheriting 0.46 and dark moving only 0.9 → 0.89, and the field that does move is a scalar level target), the stacks **metrology** (the overlay paints the unsampled DOM material — in light the *active* flat white at α 0.665 — so the endpoint never reached the second plane, and six of the 30 holdout rows are stale against `main`, which also leaves the stack-specific term unmeasured); the four-arm transfer/scatter experiment declared before it runs, two arms runnable today; the checking bed specified at 38 inactive scene ids plus 4 active, one new background (`mid-chroma-solid`), both paths costed; the bound declared in five clauses on the interior metric, scoped to the checking set, and failing four of six profiles when retro-applied jointly to the spent holdout. **G1b capture half BLOCKED on the user:** the native deactivation path does not exist, 8.3 h of machine time at the freeze bar (11–21 h with attempt loss), and the 2026-09-14 OS 27 ship date against a bed that only 26.5 can supply. Reviewed independently at `4f90e05`: four load-bearing claims confirmed, eight artifact defects fixed in place before the declaration landed (claims §5.134's verification record) |
| W27d | worktree agent, `bc14af9..31988e6` with main integrated at landing; merged `108b40d`; claims §5.132 with its verification record | CLOSED 2026-09-11 (`present` on `GlassSurface` and on the host entry drives `materialization` through the kernel's existing monotonic driver to both tiers; exactly 0 is `Glass.identity` and leaves the renderer's drawing set, the proxy's painted shape and the root's painted-tone forecast; `GlassMorph transition="materialize"` is two endpoints on their own boxes and planes with only the content crossfading; Reduced Motion steps presence on both tiers. Review: a six-lane panel plus a binding verifier against the frozen head — ten findings confirmed and fixed with fail-before tests (one P1: focus lost on a materialize close), two more of the same shape found while fixing them and fixed, three refuted as declared design and recorded instead (proxy σ in §5.132 §4; host presence on `DEFAULT_MOTION_PROFILE` in §5.132 §6, both READMEs and the Deferred list; the tint-table cache bound and the morph's arrival tolerance in the tracker). At the head: goldens 34/34 and GPU e2e 21/21 with nothing re-recorded, platform-web chromium e2e 158/158, react e2e 128 on three engines, demo e2e 48/48, 2 160 unit tests, build and lint clean) |
| W27e | G0 dispatched 2026-09-11, first after the 0.16.0 release (Decision Log 12); worktree agent, claims §5.133, evidence `packages/calibration/results/2026-09-11-w27e-g0-vibrancy/` | G0 CLOSED 2026-09-11: 57 dumps (not 58), 60 occurrences, 4 distinct matrices — **2** foreground operators on the surface's highlight layer plus 2 author-tint colorize matrices, and **no occurrence on a label**, the harness having rendered no text inside the glass by rule. Both foreground operators factor exactly through Rec.709 luma as an affine level map plus a saturation (m 1.5 / a 0.1 / b 0.9 and m 3.0 / a 1.35 / b 0.15, residual ≤ 2.5e-4). The selector is backdrop tone and span jointly, neither alone (the same dark backdrop switches at span 44 and not at span 96), so G1's threshold must be declared on a joint form; `backdropToneAdaptation(tone, sizeThickness(span))` at the shipped profile separates the two operators by 0.9923, a `tracksLuma`-gated rule fits the same 58 rows equally well, and Apple's own face fill flips white→black on exactly the two switching cells. Composite, settled in real Chromium (`composite-probe/`): on both tiers a blended label composes against the material, never the page, because the glass root isolates — but a `mix-blend-mode` inside the host collapses `backdrop-filter` sampling for a group whose proxy is outside that element's subtree (measured on one group per case; the "every group under the root" universal is an extrapolation), so only a `gpu-texture` group can run Apple's literal pipeline; the colour transform is exactly a CSS `feColorMatrix` at `color-interpolation-filters: sRGB`. G1 is not dispatched: its premise moved, and the one capture that would close the label question is named in §5.133 §7 |
| W27f | G0 CLOSED 2026-09-10 (merged `730a9d3`; claims §5.129: the unhinted dark capsule misses the collapse by ΔE 0.545 against the sampled path's 0.006, a correct scalar hint repairs it but the dark medium pane still misses by 0.079 (−0.089 L against the same-hint sampled path), the checkerboard rows lose spread and the photo rows keep too much; a scalar hint itself costs the sampled path its structured-backdrop correction, so the evidence keeps sampled-today, same-hint-sampled and hinted-page columns apart; the two stack overlays are the only native cells on this path; the demo gains `/#page`, "Over ordinary page content") / G1 CLOSED on isolated branch 2026-09-10 (claims §5.131: profile-at-known-tone derivation, scalar CPU/GPU law proof, unchanged sampled-source draws; 20 ordinary scenes plus both stacks in light/dark, full holdout spent at `1fff5e6`; thick-body repair with unknown-tone paint, structured spread/colour and dark-overlay regressions retained) | G1 LANDED (merged `6ae37c1`). **G2 CLOSED 2026-09-11** (worktree agent, claims §5.135, evidence `packages/calibration/results/2026-09-11-w27f-g2/`): a landing gate that fitted nothing and moved no material constant, profile, fixture, golden or canonical matrix row. The bound was declared and committed at `9edaa0b` **before** the first capture at `7b2e03c` — the native stack envelope taken from S0 (the old textured-base composite, unmeasurable at this head because its material is gone from the runtime) and S1 (the same base under G1's overlay), kept apart and never averaged, with Clause A bounding the DOM-base overlay at the envelope's upper endpoint on nine rows and Clause B pinning all twelve S1/Uh readings at §5.131 §6's magnitudes. Clause A is weak on exactly one row — dark checker, where the upper endpoint is S1's own regression — and that is named rather than smoothed, with Clause B carrying the cell. 308 captures at `8cf6a89`: all **eighteen** overlay readings reproduce §5.131 §6 **to six decimal places**, so every clause holds with nothing to weigh. Identity: sampled and same-hint-sampled **20/20** on the ordinary cells and **2/2** on the stacks in each scheme, both DOM arms byte-identical too, goldens green with nothing re-recorded. Three findings beyond the charter: §5.131 §4's CSS digest pair is **bistable, not changed** — six repeat invocations land on those two digests and no third, so a flip rather than a one-way change (`css-bistability.json`); the CSS coherence record on DOM-sourced groups puts **six dark ordinary cells and the dark checker stack outside the texture band 0.8–1.25**, the GPU interior as low as 0.6211 of the CSS one, recorded under X1 and never a CSS floor; and the two stack cells are **`split.holdout` members**, not the calibration cells the dispatch described, so this is their second read on one frozen configuration — taken deliberately, with the reasons written before the read (§5.135 §9) and the consequence recorded for whoever fits on the stack path next. The adoption's own limit is stated in the ledger and in the test: `matrix.json` carries no overlay-local metric, so the bound is six assertions over the committed verdict rather than a `GateRow`, which catches ledger-versus-evidence drift but not a material change; per-surface metrics in the matrix schema is the named work. Eye sheet prepared in both schemes on a measured hardware adapter — **the user's eye not yet taken** | G2 CLOSED; bound adopted; `/#page` acceptance still open |

## Decision Log

1. **The cut turns from fidelity to coverage (2026-09-10; user-decided on the parent's
   recommendation).** After W26, with the instrument at the fixtures' 8-bit floor and the
   reference version about to be superseded, the next wave is a coverage wave: re-score the matrix,
   then transitions, toolbar splitting, vibrancy and window focus. Rejected: scroll-edge effects
   first (a product decision to overturn a standing exclusion, not taken); the motion harness first
   (large; deferred to its own wave); staying on the eye-driven optics waves through the three
   logged dark-scheme gaps (the next code of 26.5 fidelity is worth less than any absent row and
   may not survive OS 27).
2. **"WebGPU is what we compare with Apple" (2026-09-10; the user's words).** First stated as "we
   only care about WebGPU from here", then corrected by the user the same hour: the CSS tier is not
   dropped; it is not the comparison target. Recorded as §The tier boundary (X1), extending the
   parent's Decision Log 23. Rejected: dropping the coherence pin (silent regression of the
   fallback); chartering CSS residuals as work.
3. **Six children; page content gets the derived material, not a spike (2026-09-10; user-decided).**
   W27b, W27c, W27d and W27e all in; W27f as the derived material at the hinted level per the
   parent's Decision Log 23 (c). Rejected: an HTML-in-Canvas spike in this wave (deferred);
   leaving the flat white and asking adopters to register textures (the demo's practice, not a
   library's promise).
4. **Vibrancy is an operator on vitrea's own controls and a token elsewhere (2026-09-10;
   user-decided on the parent's recommendation).** Rejected: the operator everywhere (Apple's
   semantics, but it rewrites app-authored colour and overturns the root's Decision Log #34(c));
   token only with levels (closes one row and leaves vibrancy absent).
5. **The recovered pre-DL14 inactive bed is admissible for the fit (2026-09-10; user-decided on
   the parent's recommendation).** 121 matched pairs over byte-identical backgrounds, single run,
   no per-cell attestation; admitted because the parent's own record found the inactive material
   static across runs where the active one carried per-instance state, which makes one run
   defensible for this pose specifically. Provenance goes into the ledger (X8). Rejected: one
   attested session before landing (available later without a re-fit); fresh captures only (one
   to two hours of the user's machine for a pose the record already holds).
6. **Prominent is held; the toolbar ships both of Apple's shapes (2026-09-10; the parent, from
   the grounding).** `.glassProminent` differs from a tinted button by an accent default and a
   vibrant label; vitrea has neither until W27e, so the name would arrive meaning nothing. The
   tinted button is made reachable in W27a. `ToolbarSpacer` (positional) and
   `sharedBackgroundVisibility` (per item) reduce to one partition rule, so both ship.
7. **Activation is a pose of the root (2026-09-10; user-decided by selecting the child so
   worded).** Not a seventh interaction state (§Design, binding). Rejected: a per-group continuous
   fold beside `backdropAdaptation` (serves Apple's per-element recede, which is the excluded
   sheet's case, at the price of a per-group scalar constant for nearly every surface).
8. **Presence, not alpha; whole-material, not lens-only (2026-09-10; the parent).** Binding for
   the semantics (Apple's rule plus the Backdrop Root constraint); the per-instance scalar mechanism
   is advisory. Rejected: lens-only (delivers `.materialize`, splits off `.identity`); element
   opacity (structurally broken: it kills sampling).
9. **The secondary ink's floor is a promise about the primary's reach (2026-09-10; W27a on the
   review's finding, accepted by the parent).** The review showed the first version's "secondary
   holds WCAG 4.5 on every surface" false twice: the solve contrasted a neutral level where a
   tinted material is chromatic (a full-strength magenta published light ink at 1.75), and the
   unresolved-level branch emitted Apple's flat 0.6. Fixed by solving against the composite colour
   the tier draws, over both ends of the material's own bracket, taking the harder answer. The
   rule that results: *secondary is never worse than the primary, and holds 4.5 wherever the
   primary can*; on the clear variant, whose bracket runs 0.27–1.0, neither ink holds 4.5 over any
   useful part, so secondary collapses onto the primary rather than claiming a floor the primary
   does not have. Tertiary and quaternary keep Apple's 0.3 and 0.18 and carry no floor. Rejected:
   narrowing the guarantee to "where the level resolves" (the bracket needs no backdrop, so the
   guarantee was available on every shipped path); a constant alpha (no constant holds 4.5 across
   the material's range without ceasing to be a secondary).
10. **The inactive endpoint needs shade through collapse and a difference per scheme (2026-09-10;
    W27c G1, approved by the parent after the one-field refutation).** Chroma suppression alone
    leaves the old shade at 1 on a collapsed body: no constant neutral seed can give both the
    1x light dark-solid tinted capsule's 0.03678 Y and the checkerboard tint's 0.45128 Y under a
    shade clamped below that seed. A second identity-default field retains the shade through
    collapse. The endpoint is indexed by resolved scheme so its light and dark response
    ordinates can be fitted independently; X7 still means two fixed endpoints per scheme, never
    a blended profile. The fit is claims §5.130. Rejected: discarding author tint strength;
    breaking the untinted dark-solid collapse to make tint fit; forcing a flat common patch to
    compromise opposite scheme responses. The historical-only native capture boundary is guarded
    in G1: refuse an inactive capture request before writing rather than file active pixels under
    an inactive id; fresh native deactivation requires a separate capture-path charter.
11. **A custom motion profile retunes only the content crossfade; the material's arrival keeps
    the system's timing (2026-09-11; user-decided).** W27d landed host presence on
    `DEFAULT_MOTION_PROFILE`, with an author's `profile` reaching only the bindings' content
    fade; the panel review raised it as a candidate defect and the verifier refuted it as
    declared design, leaving it in §5.132 §6 and the Deferred list as a wave-owner decision under
    X2. The user kept it as built: "That is Apple's own separation ('materialize is not a
    fade'), and letting authors retune the material's timing would make the pose depend on app
    motion settings." Rejected: a motion-profile input on the framework-agnostic root (new
    public surface, and a pose that varies per app). Consequence: the tracker's 1e-3
    arrival-tolerance window stays closed by design.
12. **After 0.16.0: vibrancy first, then W27f G2; the activation runtime is held behind a
    measurement gate (2026-09-11; user-decided).** The release met acceptance clause 5
    (`ad4266d`, tag `v0.16.0`) and lifted the stopping point. The user's ordering, in their
    words: "Vibrancy is the highest-value absent row (automatic legibility of anything on glass)
    and its operator is already in the repo unread." W27f G2 follows it. W27c G2/G3 wait:
    "today the inactive endpoint is seven to eight times worse [on holdout] than on calibration,
    so shipping the hook would ship a pose proven on 23 cells only. That needs a short
    measurement child first, not runtime work." Chartered as W27c G1b (§Children) from §5.130
    §7's five named residuals. Rejected: wiring the two declared endpoints now and improving the
    fit later (the runtime would publish a pose whose fidelity claim the ledger limits to where
    it was fitted); W27f G2 before vibrancy (a landing gate and a bound, worth less than the
    absent row).
13. **The 26.5 run before the capture machine updates: the labelled vibrancy probe and the
    inactive checking bed at the probe bar; `mid-chroma-solid` added; the hold stays on every
    profile (2026-09-11; user-decided on the parent's recommendation).** macOS 27 ships
    2026-09-14 and an updated capture machine can never produce 26.5 evidence again. Two gates
    converged on one run: W27e G0 found no label operator in the committed dumps (§5.133) and
    needs a `dump-layers` pass on a labelled probe scene — minutes, no pixels, no fixture; W27c
    G1b (§5.134) specified an unspent checking bed that needs an inactive-capture path the
    harness does not have, 4.4–8.5 h at the probe bar or 11–21 h at the freeze bar. The user
    takes both at the probe bar, which answers "does the fit hold" and can unblock G2, and not
    the freeze bar, so no inactive floor is adopted from this run (G3 stays a later gate). The
    one new background the bed proposed is added, as `mid-dark-solid` was in W7. The hold on
    W27c G2/G3 is kept as the declared bound reads it — on every profile, including light
    standard, where one cell family fails the single-cell cap — because a bound is not
    re-interpreted after it is declared. Rejected: the probe alone (leaves W27c held on evidence
    it cannot improve); neither (loses the 26.5 endpoint's check for good); dark-only or
    accessibility-only unblocking (relaxes a declared clause to ship a pose).

## Surprises & Discoveries

- **The eighteen fidelity waves moved six matrix rows; the eight coverage children before them
  moved twenty-seven** (matrix §7). The number that decided this cut.
- **0.16.0 shipped three W27a features no reader can operate** (found on the release's eye
  sheet, 2026-09-11, by the session that produced it; verified by the parent). `GlassButton
  tint`, `GlassGroup tint` and the four named ink levels have their props and README paragraphs,
  but every `tint=` under `apps/` is on a `GlassSurface` — a prop older than the wave — and
  nothing under `apps/` passes `foreground` or names the secondary, tertiary or quaternary
  tokens. Acceptance clause 2 was checked at each landing by prop and README and never by
  reading the demo; the sheet's panels for those rows came from a scratch harness committed as
  evidence under `results/2026-09-10-w27-coverage-wave/eye/harness/`. W27e G2 closes it with one
  playground plate; the missing check — that every landed prop has a live instance — is in the
  tracker.
- **The inactive material's bed survived the re-baseline intact** — 121 of 121 paths present in
  both trees, 0 of 121 unchanged, backgrounds byte-identical — because DL14 overwrote fixtures in
  place. The retired matrix survives too (`results/2026-08-30-inactive-bed-matrix.json`).
- **Apple's vibrancy operator has been in the repository since W12**, unread: a `vibrantColorMatrix`
  `CAFilter` on every glass `CASDFLayer` in 58 layer dumps, four distinct matrices, the high-gain
  variant on the small dark-solid capsule and not on the medium rrect over the same backdrop.
  *Corrected by W27e G0 (2026-09-11, claims §5.133), the reading left standing beside it per the
  repo's rule about recorded numbers:* the trees hold **57** dumps (the 58th file is W12's own
  report, which quotes a matrix); the four distinct matrices are **two operators of one kind and
  two of another** — 58 occurrences on the surface's highlight layer in 2 distinct operators, and
  2 on the author tint's gradient layer, which is a colorize rather than a variant of the
  foreground operator; the high-gain variant appears on the `impulse` capsule as well as the
  `dark-solid` one; and **no occurrence is on a label**, because the harness renders no text inside
  the glass by rule.
- **Three published behaviours did not exist:** the group tint (changelog 0.2.0), the tinted button
  (prop allow-list), and any interaction reaching the GPU tier's lens (clamped at 1 since the
  channel landed; only `disabled: 0.5` moved the renderer).
- **The demo has never shown the page-content path.** Every backdrop in the site, the laws page
  and the playground is a registered texture.
- **W27f G0: a correct scalar hint is not a texture analysis result.** It overrides both RGB
  and the independent linear mean, disabling the structured-backdrop correction; checker medium's
  sampled ΔE becomes 0.05196 from 0.01236 at the same measured scalar level. Claims §5.129 keeps
  both baselines. The unhinted dark capsule misses collapse (0.54523 ΔE); the correctly hinted dark
  medium pane misses the body's level instead (0.07851 against sampled 0.00877). The nominal white
  unsampled pair is subsequently adapted and tinted by the shader, not its final measured colour.
- **The "24 CSS px at nominal σ 8, 42 under Reduce Transparency" in §Design is a reading of a
  material the project no longer draws** (W27b). Both numbers are 3σ at σ = 8, which was this
  tier's blur when S1 wrote the padding rule; the recalibration cascade refitted σ, and W11c G1
  and W16 G1 moved the proxy's own σ to the scatter law over each group's members. The number a
  layout has to clear today is **not** a constant of the policy at all: at the shipped profile it
  reads 11.10 CSS px for a group with nothing measured, 11.84 at a 44 px control's span and 21.45
  at a 160 px one, and 22.46 / 23.04 / 30.61 for the same three under Reduce Transparency. So the
  binding sentence's *mechanism* — read it from the resolved policy, never a constant — landed
  exactly as written, and its parenthetical is history rather than a target. The derivation is
  `samplingPaddingFor` (`platform-web/src/optics.ts`), which is the frame loop's own composition;
  §Design's numbers are left standing beside this note rather than rewritten, per the repo's rule
  about recorded readings. *Added 2026-09-11, after the 0.16.0 eye sheet read `min-width: 24px`
  on the demo's spacer:* what a spacer actually clears is the larger of that derivation and
  core's advisory `DEFAULT_GROUP_SAMPLING.samplingPadding`, which is still σ = 8's 24 and which
  core's overlap check is written against. At the shipped profile the advisory is the larger on
  the regular variant — 24 against 11.1 (nothing measured), 11.3 (36 × 28 button), 11.9 (120 × 44
  capsule), 12.7 (420 × 52 bar) and 14.9 (420 × 72) — and the material is the larger on clear
  (35.5). So the 24 is the advisory winning, the spacer is wider than the material needs on
  regular and never narrower, and retiring the constant is a core change (core cannot import the
  derivation) that is in the tracker, not this wave.
- **`Glass.clear`'s dimming layer is painted by no renderer** (re-score §3): the variant resolves,
  warns and tints; `ResolvedMaterial.dimming` is produced and consumed by nobody. Logged to the
  tracker at this cut; not a child of this wave.

## Outcomes & Retrospective

Pending — written at recomposition against §Parent-Level Acceptance.

## W27f G1 dry-run declaration (2026-09-10)

The candidate fits no constants. `materialAtBackdrop` in `platform-web/src/optics.ts` owns the
profile-at-tone law; the host's CSS reading calls it and the GPU optics shader mirrors it per
pixel so a merged group keeps each member's span. The response and size laws read the linear
profile, never an already encoded alpha. Over a DOM proxy the shader evaluates that material at
the stated tone, shades paint there, applies the inner shadow and the rim's amplitude law there,
and only then solves the encoded canvas layer. Both outer-shadow terms follow the same tone;
the lift cannot reproduce the exterior's local colour without exterior pixels. No lens or proxy
blur change is included. The absent-tone branch does not enable response or collapse; the CSS
mapping's 0.02 is solely the no-reading conversion convention, not an inferred backdrop.

Before the dry run, the frozen `bdf0029` source reproduced every shared G0 light calibration
reading and texture digest. The same 20 calibration scenes are captured in light and dark 1x,
unhinted and hinted DOM GPU, sampled-today and same-hint sampled controls, and CSS readings.
All 20 dark scenes are captured, but only nine have native fixtures: missing native ΔE stays
null and route-to-route comparisons remain measurable. The two requested stack scenes are held
until the final frozen candidate and are read once then; the dark photo stack has no native
fixture either. Scratch only (`/tmp/w27f-g1`), never the canonical matrix or capture tree.

The end read covers **the entire declared holdout membership**, not only the stacks (parent
clarification before spending it). Light and dark native coverage is read on both DOM-GPU page
arms with CSS controls; the dark photo stack is also captured with its native result left null.
Ordinary texture controls need no new capture because their path is byte-identical. The stack
controls are different: their bases are textures but their overlays are DOM, so the two stacks'
standard and hinted textured-base arms are captured in the same once-only pass. No holdout
measurement may change this configuration. The marker records the frozen runtime fingerprint
before capture; a failed partial holdout capture is still spent, never silently retried as fresh.

Stops are sampled-path byte changes (renderer goldens plus isolation and the scratch texture
captures), an unexplained departure from the scalar response/collapse/paint/rim/shadow laws,
or suite regressions. G0's sampled-today errors remain the diagnostic budget; same-hint sampled
is a control, not a relaxed comparator. Structured-backdrop spread and colour need independent
linear/encoded means and local pixels, not a fabricated interpretation of `hint.complexity`.
G1 records every per-scene miss; G2 alone adopts a native stack bound and re-reads the demo.

## Revision Notes

- 2026-09-11, **W27f G2 closed; the wave's last landing gate.** Claims §5.135 and
  `packages/calibration/results/2026-09-11-w27f-g2/`. The bound was met in every clause and is
  adopted, and three things the charter did not ask for came out of the read. **One corrects the
  ledger:** §5.131 §4's CSS digest pair is two states of a bistable capture, not a change its
  material edit produced — six repeat invocations land on exactly those two digests and no third.
  **One is a gap nobody had measured:** on DOM-sourced groups the two tiers diverge much further in
  the dark scheme than the adopted texture-sourced band allows, the GPU interior reaching 0.6211 of
  the CSS one; X1 keeps it a record rather than a charter, and it is the largest single unclaimed
  thing this gate saw. **One is a premise defect worth generalising:** the two `glass-over-glass`
  cells the child treats as its native evidence are holdout members, which the dispatch had as
  calibration, so the gate spent a second read of a frozen configuration. It was taken with the
  reasons written before the read rather than justified after, and that is the pattern to keep —
  when a gate discovers its own premise is wrong, the correction belongs in the declaration it has
  not yet acted on, not in the claim it writes afterwards. Two mechanical repairs travelled with
  it: the calibration and golden servers' shared port 5189 is now overridable in both halves
  (defaulting to 5189, so no recorded capture changes meaning), and the W27f G1 runner's porcelain
  parser is fixed in the copy that ran. `/#page` acceptance remains open: the sheet is prepared in
  both schemes on a measured hardware adapter and the eye is the user's to take.

- 2026-09-11, **the 26.5 run decided (Decision Log 13); two gates merged.** W27e G0 landed at
  `335249d` and W27c G1b at `2b47bda`, each after an independent review (six and eight findings,
  all fixed before landing; the reviews are in §5.133 §10 and §5.134's verification record).
  Both reviews confirmed the claims the decision turned on and refuted none. Dispatched the same
  day: one worker on the Swift harness for the run's preparation — the inactive-capture path
  with its `presentedActive` attestation, `mid-chroma-solid`, the labelled probe scene, the
  reader for label layers and a runbook for the user's machine — and W27f G2 in parallel on
  the web side. W27e G1 waits for the probe's label data; W27c G2 stays held until a
  checking-bed read holds the declared bound.

- 2026-09-11, **W27c G1b's analysis half closed, and three recorded figures it could not
  confirm.** Claims §5.134 and `packages/calibration/results/2026-09-11-w27c-g1b/`. The gate
  fitted nothing, captured nothing and adopted nothing, and it found three places where this
  document's own numbers do not carry the weight they were given. Each is left standing where it
  was written, with the measurement beside it, per the repo's rule about recorded readings.
  **(i) Decision Log 12's premise.** "Seven to eight times worse on holdout" is computed on the
  full-canvas mean OKLab ΔE, a statistic claims §5.130 §1 itself calls "not an interior bound",
  across sets whose mean footprint differs 3.08–3.68× because the inactive split mirrors an active
  split that reserved the largest components. On the declared eroded body the ratio is 1.74× and
  1.61× on the light standard profiles — below those profiles' own validation ratio of 2.05× and
  1.99× — 1.01× and 1.22× on the accessibility pair, and 3.47× and 3.60× on the dark pair, where
  two cells carry it. All 30 spent holdout cells clear the `oklabDeltaEMean` *ceiling* the
  **active** material is already held to, the worst at 69% of it. What that narrows is **what** is
  unproven rather than how much: "a pose proven on 23 cells only" is not what the light standard
  *means* say, but those profiles are not cleared either — applied jointly, G1b's own declared
  bound fails them on its per-cell clause through the tinted photo `rrect-lg`, so four of six
  profiles fail it and only the two accessibility profiles hold all three clauses. The dark
  endpoint's level and colour and transmitted chroma at large span in every scheme remain
  unproven, no inactive floor is adoptable, and four named model-form gaps are open. **No gate is
  unblocked by this note**; the ruling is the user's and G2 and G3 stay held.
  **(ii) Decision Log 5's capture estimate.** "One to two hours of the user's machine" matches no
  recorded session at today's bed size: the specified checking bed costs 8.3 h at the seventeen-run
  freeze bar and **11–21 h** once attempt loss is budgeted at the record's own 1.3–2.5× (4.4–8.5 h
  at the seven-run probe bar), and W25 G1's comparable two seven-run passes ran 5 h 40 min.
  Decision Log 5 also called a later attested session "available later
  without a re-fit"; it is, but not cheaply — the native deactivation path it needs does not exist
  in any form, and no AppKit mechanism for it is recorded anywhere in the repository.
  **(iii) The stacking sentence** in claims §5.130 §7 is withdrawn: the stack's overlay resolves
  `css-backdrop` with `analysis: none` and paints the unsampled DOM material — in the light scheme
  the *active* flat white at α 0.665, in the dark one `tint [0.05, 0.05, 0.05]` at 0.9116 — so the
  inactive endpoint never reached the second plane, and W27f G1 replaced that flat in **both**
  schemes on `main` after those rows were captured. **Six** of the 30 holdout rows are stale
  against today's runtime — both light photo stacks and all four checkerboard stacks — and 24 are
  not. Because the achromatic control is itself one of the six, the stack-specific term is left
  unmeasured rather than bounded.

- 2026-09-11, **W27e G0 closed, and the child's premise moved.** The 58 committed dumps are 57,
  and the "four distinct matrices" the grounding found are two operators of one kind and two of
  another. More consequentially, none of them is on a label: the reference harness renders
  `Color.clear` inside every `glassEffect`, so the corpus holds the operator Apple installs on the
  *material's own highlight* and the one it installs on the *tint*, and says nothing about what it
  installs on an app's text. §Design's "the operator is fitted to Apple's `vibrantColorMatrix` as
  read from the committed layer dumps" therefore cannot be executed as written from this corpus
  alone; the sentence is left standing and claims §5.133 §7 names the one run that closes it — a
  `dump-layers` pass on a labelled probe scene, which breaches no fixture rule because a dump
  captures no pixels and writes nothing under `fixtures/`. Whether to take that run on 26.5 before
  macOS 27 ships on 2026-09-14, and whether G1 should proceed to fit the highlight operator's
  selector in the meantime, is the user's call; G1 was not dispatched at this gate.

- 2026-09-11 (**the 0.16.0 cut record**, the session that ran W24–W26, by agreement with the
  session that owns W27): the user's `pnpm release` on `ad4266d`, tag `v0.16.0`. Registry: web
  07:48:03Z, react 07:48:58Z, core 07:50:56Z — **the release-chain window recurred, an eleventh
  time, at 173 s** (against 53, 70, 73, 248, 267, 246, 124, 73, 125 and 52 s); for that window a
  fresh install of the dependents could not resolve core `^0.16.0`, and no install was attempted
  inside it. Verified by a cold install outside the workspace after all three were listed: all
  three at 0.16.0, ranges `^0.16.0`, all three entry points import (core 44 exports, web 229,
  react 36), `GlassToolbarSpacer` exported from the React binding and `recededMaterialProfile`
  from the web package, the renderer's material in core's split chunk carrying `sizeHeavyTapSigma`
  9, no private package installed, LICENSE / NOTICE / README in each (installed 1 772 / 1 672 /
  608 kB against 1 712 / 1 480 / 508 at 0.15.0). The chain the release must show green is
  `c9d-release-checklist.md`'s; on `12e90ad` the owning session ran build, lint, 2 160 unit
  tests, goldens 34 / 34 and the demo suite 47 / 48 (the one miss a timeout, tracked). **The eye
  record for this cut** is `packages/calibration/results/2026-09-10-w27-coverage-wave/eye/`
  (`eye-sheet-light.png`, `eye-sheet-dark.png`, `index.md`): the landed features captured at 2×
  in headed Chromium 151 on `apple / metal-3` (no fallback adapter, every group `webgpu`), five
  rows per scheme — the toolbar split beside the unsplit row, tints and the four ink levels, the
  page-content material beside the texture path and the native stack fixture, presence and both
  morphs as six-frame strips with `--vitrea-materialization` and the host's computed opacity
  (`1` on every frame) printed, and the lens at rest / hover / press with ×8 difference panels.
  Produced after the publish, so it is the record of what shipped rather than the veto before
  it. **One finding for the wave's acceptance:** three of W27a's features — the tinted
  `GlassButton`, `GlassGroup tint` and the four ink levels — have a prop and a README paragraph
  but no live instance in the demo or the playground (`grep -rn 'tint=' apps/` hits two
  `GlassSurface` sites and nothing names the secondary/tertiary/quaternary tokens), so
  Parent-Level Acceptance 2 is unmet for them; the sheet's panels for those rows come from the
  committed scratch harness. Also recorded by the sheet: `tint-mixing` does not fire on a group
  with no seed and one tinted member (checked, 0 of 12 diagnostics), and the spacer measured
  `min-width: 24px` on this run through `samplingPaddingFor`.
- 2026-09-11, **0.16.0 released; the stop lifted.** The user published the three packages at
  0.16.0 (`ad4266d`; tag `v0.16.0` pushed by the parent), so parent acceptance clause 5 is met.
  The cut record itself (registry, cold install, the c9d chain, the eye sheet) is written by the
  session that produced the eye material, above this note. The user then set the next cut:
  Decision Log 11 (the motion profile kept as built) and 12 (vibrancy first, W27f G2 next, the
  activation runtime held behind W27c G1b). W27e G0 and W27c G1b's analysis half are dispatched
  the same day, parallel-safe (the dumps and the calibration results against product code that
  neither touches); W27f G2 follows W27e G0.

- 2026-09-11, **stopping point, on the user's instruction:** "Keep the thing that's working to
  continue and finish, but don't dispatch the next wave; get to a good stopping point once works
  being done right now are done." The four children in flight when that was said were finished,
  reviewed, merged and verified, and nothing new was dispatched. On `main` at this note: W27a
  `bc14af9`, W27b `38d782c`, W27f G1 `6ae37c1`, W27c G1 `f8c38a2`, W27d `108b40d`. Main verified
  after the last merge, one suite after another: build and lint clean; 2 160 unit tests across
  the nine packages (motion 164, policy 23, geometry 170, renderer-webgpu 465, core 302,
  platform-web 552, calibration 340, react 141, demo 3); renderer goldens 34/34 with nothing
  re-recorded; demo e2e 47/48 in the full run. The one miss is `contrast.spec.ts` "the plates'
  labels hold the large-text floor", which timed out at Playwright's element-stable check with
  another session active on this repository and passed alone at 24.1 s against its 30 s budget
  (13 s of which are the helper's fixed phase waits): a test-budget flake, now in the tracker,
  not a material reading. Every demo test has passed on `108b40d`; not all in one run.
  Not dispatched, each with its design inheritance standing as written: W27e (vibrancy; X9 now
  names what its operator must do with presence); W27c G2 (the activation observer and
  `windowActivation`) and G3 (the landing, with the demo's inactive rows and any inactive
  floors); W27f G2 (a native stack bound and the user's acceptance of `/#page`). Parent
  acceptance clause 5, the release, is not met at this point by design: nine changesets sit in
  `.changeset/` for the fixed group, and the minor is cut only after the user's eye on the
  landing sheets. The reference moves on 2026-09-14; the 26.5 bed stays frozen per §Deferred and
  nothing here fits against 27. W27d's review ran as the six-lane panel against its frozen head
  with the binding verifier on Opus (GPT capacity was constrained), then one reviewer over the
  merge and the fixes alone, which returned nothing; the outcome is in W27d's note below and in
  claims §5.132.

- 2026-09-10, W27d implementation: presence is driven once by the framework-agnostic
  root, before either tier consumes `--vitrea-materialization`; React forwards `present`
  rather than owning a second driver. The interaction table keeps its invariant presence
  seed at 1, but `STATE_DRIVEN_CHANNELS` no longer includes authored presence. Reduced
  Motion gives the monotonic presence driver zero duration and the root steps to its
  target on both tiers, including a preference change mid-flight. This deliberately
  follows the HIG's caution about blur animation rather than extending interaction
  illumination's exemption to whole-material arrival. Timing/easing remain unmeasured.
  The DOM-backed GPU path needs one additional carrier: its sibling backdrop proxy must
  also consume presence, or shader identity would leave blur behind. This does not relax
  X6: neither host nor any ancestor fades. The instance's free scalar travels through
  a fourth `r16float` field attachment (+2 bytes per field texel, 24 → 26); all-1
  goldens remain unchanged. Exactly-zero members leave the renderer's drawing set after
  shape resolution, and leave the root's painted-tone forecast, so neither an absent
  union member nor its hue can affect a surviving surface. The proxy retains sampling
  bounds but removes zero members from its painted shape. Chromium needs a mask in
  place of its clip, not on top of it; claims §5.132 records the carrier experiment,
  the fractional residuals, the Reduced Motion rule and the W27e foreground handoff.

- 2026-09-11, **W27d CLOSED at its landing head.** Main was integrated first: the child was cut
  before W27b, W27c G1 and W27f G1, and the one place they meet is the optics shader, where
  W27f's derivation at a known backdrop tone and W27c's tint chroma collapse shape the same terms
  presence scales. They compose and each factor lands once; presence additionally reaches W27f's
  DOM branch on the secant's input rather than its result, so the recovered neutral stays where
  presence 1 solves it and only the coverage travels. Independent review (a six-lane panel and a
  binding verifier against the frozen head) returned ten confirmed findings, all fixed with tests
  that fail before them — one P1, focus lost on a materialize close, because the returning end was
  hidden by its instantaneous alpha rather than by the direction of travel. Two further defects of
  the same shape surfaced while fixing them and are fixed here: the group sort's back plane, which
  could defeat the stacked-tone fix by registration order, and two more paths holding a parked
  group's GPU allocations. Three findings were refuted as declared design and recorded instead —
  the proxy σ, host presence on `DEFAULT_MOTION_PROFILE`, and the tint-table cache bound with the
  morph's arrival tolerance. The bed did not move: goldens 34/34 and GPU e2e 21/21 with nothing
  re-recorded, platform-web chromium e2e 158/158, react e2e 128 on three engines, demo e2e 48/48,
  2 160 unit tests, build and lint clean. Claims §5.132 carries the verification record.

- 2026-09-10, **W27c G1 fitted and declared, pending parent review** (claims §5.130).
  The 121 inactive fixtures are recovered additively with source hashes, schema-2/single-run
  provenance and inferred pose. `recededMaterialProfile.light/.dark` supplies two fixed endpoints
  per resolved scheme; the new identity-default `tintChromaScale` and
  `tintShadeCollapseRetention` express author-hue extinction without deleting its strength or
  forcing a collapsed white layer. GPU and CSS derive the same seed/shade law.
  - **The first fit is invalidated, not erased.** Independent review caught an 800×600 viewport
    around the 320×200 scene and ignored page problems. The old numbers remain beside an explicit
    invalidation. A corrected instrument now refuses geometry/scale/problem mismatches, records
    them, restarts from an active-body seed and fits only 62 calibration rows. The selected
    endpoint is checked on 16 validation rows; all 78 repeat twice and remain byte-identical after
    integrating main through 38d782c. Three further review findings — inactive tint-guard poisoning,
    demo picker leakage and missing JSON profile keys — are fixed and independently rechecked.
  - **The holdout is spent, and limits matter.** Thirty cells read once on the new frozen document,
    with no subsequent fit. Full-canvas holdout mean OKLab ΔE: light 1x/2x 0.013353/0.013027,
    dark 1x/2x 0.022645/0.022298, light 1x IC/RT 0.005182/0.003171. Large photo surfaces expose
    desaturation, full-strength neutral tint loses native background colour, the dark mid-dark
    response is too bright, and far-span checker structure remains too strong. These are future
    transfer/scatter work with a newly declared experiment and unspent check bed, not silently
    accepted matches or G3 floors. Calibration/validation means improve in every profile.
  - **Unmoved and bounded.** Active resolved SHA pins and all 34 renderer golden/isolation tests
    pass without re-recording; workspace build/lint and 2,060 unit tests pass after integration.
    G1 takes the permitted isolation proof, leaving the active from-empty matrix rebuild to G3.
    The canonical matrix is untouched. Native fresh inactive capture is still absent and now
    refuses before GUI/output; G2 is web activation wiring, not a promise of native deactivation.
    G3 inherits runtime capture integration, floor decisions and the user's eye on the pairs.

- 2026-09-10, **W27b CLOSED**. `GlassToolbar` partitions its children into sampling groups at
  each `GlassToolbarSpacer` and at each item declaring `sharedBackground="hidden"`; one
  `role="toolbar"`, N groups (X5). Each partition takes the toolbar's `groupProps`, with the
  inherited `id` suffixed per partition (`toolbar`, `toolbar-1`, …) so an unsplit toolbar
  registers exactly the id it always did, and a hidden item may carry its own `groupProps`,
  whose `id` is taken as written. `GlassToolbarItemProps` is published so a control the library
  did not write can declare the pair; `GlassButton` drops them rather than handing them to the
  element. `GlassToolbarSpacer` (`kind="fixed" | "flexible"`) opens a *minimum*, written as
  `min-width` (or `min-height`) so a container `gap`, a margin or an authored width add to it.
  - **The gap.** `samplingPaddingFor({ members, material })` is new in `vitrea-web` and is the
    frame loop's own composition, extracted: `root.ts` now resolves each group's σ through
    `proxySamplingSigma` and the toolbar reads the padding through the same law, so there is one
    home for it instead of a second reading in the binding. The toolbar passes **its own measured
    box** in place of members it has not measured; the law is monotone in a member's span and in
    its extents (pinned in `proxy-geometry.test.ts`), so a box that contains the members bounds
    their padding rather than estimating it. Before the first measurement the box is empty, which
    is the projection at span 0 — the floor every group starts at.
  - **There are two paddings, and the gap clears both.** Found by probing rather than by reading:
    the platform's `proxy-overlap-after-enforcement` fires on what the group actually samples with
    (the derived 3σ), while **core's own `group-proxy-overlap` fires on the descriptor's padding**,
    which is `DEFAULT_GROUP_SAMPLING.samplingPadding` = 24 unless the author declared one — and
    that advisory deliberately did not follow σ down when the material was refitted (W6:
    "lowering a public default for tidiness rather than for a measurement would change behaviour
    for every consumer"). At today's material the advisory is the larger for a control-sized row,
    so a spacer opening only the derived 12.67 px raised `group-proxy-overlap` on every frame.
    The gap is therefore `max(declared ?? advisory, derived)`. It follows the policy where the
    material's own requirement is in front — a 420 × 72 bar under Reduce Transparency needs
    24.9 px — and rests on the advisory below that. **The first version of the e2e proof passed
    while the finding was really firing**, because the scene was built at the pre-flip state and
    the diagnostics channel dedupes by code and subjects: the finding landed before
    `clearDiagnostics()` and was never raised again. The test now declares the state under test
    before the first frame and reads every code, and it was shown failing at the derived-only gap
    before being fixed.
  - **Evidence.** `react/test/toolbar-partition.test.tsx` (18 tests: the partition, the ids, the
    merge, the protocol props never reaching the DOM, the roving order across a split, the
    derivation under both policies, along both axes and over each partition's own material, and
    — on the two functions the runtime resolves proxies with — that neither partition's padded box
    reaches the other's shapes at either policy).
    `platform-web/test/proxy-geometry.test.ts` (+6) pins the law and its monotonicity.
    `platform-web/e2e/shared/accessible-padding.spec.ts` puts the derived gap between the two
    groups of the demo-shaped scene on **real proxies** at both accessibility states and finds
    `proxy-overlap-after-enforcement` silent — in the same scene the spec above it shows the
    finding present at a tighter gap. `react/e2e/toolbar-partition.spec.ts` (three engines)
    asserts the split on the playground, and `semantics.spec.ts`'s arrow-order tests now measure
    that order *across* a live split without a line changing.
  - **The demo.** The playground's hand split — an explicit `GlassGroup` plus a 3.5rem margin —
    is now a flexible spacer and a hidden item with `groupProps={{ id: "toolbar-menu" }}`, so the
    capabilities panel keeps the group name it reads. No control was added or renamed: the
    acceptance suite's pinned arrow order is untouched. The one sentence kept from the retired
    comment is the morph's pre-measurement transient (DESIGN.md §9), which is a second reason the
    menu wants its own group.
  - **Unmoved.** The 33 renderer goldens are byte-identical; the resting bed is unchanged
    (calibration 313, `tier-coherence` and `adopted-thresholds` unaltered), because the frame
    loop's σ is the same composition in the same order. Suites: build and lint green across the
    workspace (`pnpm run ci` green end to end); unit 2028 across eight packages (policy 23,
    motion 162, geometry 170, renderer-webgpu 448, core 302, platform-web 484, react 126,
    calibration 313); `platform-web` Playwright 388; `vitrea-react` e2e 114 (3 skipped);
    demo e2e 48. The partition file is 18 of react's own.
  - **Reviewed.** An independent cross-model review of the whole change found one qualifying
    defect and then a follow-on in its own fix, both in the same place — the gap's fold over
    materials. (1) The derivation read the toolbar's `variant` alone, so a hidden item declaring
    `variant: "clear"` got a third of the room it needs, `clear` sampling at σ 4 against the
    regular material's 1.25. (2) The fix then folded the toolbar's own props in as a floor, so a
    clear row whose partitions all declared `regular` was spaced for a material nothing drew. The
    fold now maps the partitions themselves. Fragment semantics (boundaries are direct children),
    the dynamic-boundary remount and the profile patch were reviewed and left as contract scope or
    recorded deferrals. Verdict at the landing: correct, no material findings.
  - **Deferred (small).** A partition boundary that *moves* at runtime — a conditionally
    rendered spacer, an item flipping `sharedBackground` — moves the affected members between two
    context providers, and React remounts an element that changes parent. Measured: the groups
    re-derive correctly (`toolbar`, `toolbar-1`, `toolbar-2` → `toolbar`, `toolbar`, `toolbar-1`)
    and nothing leaks, but the moved member's DOM node is rebuilt and focus in it is lost. Avoiding
    it means one provider per child with the group's handle lifted out of `GlassGroup`, which is a
    change to that component's contract for a case the partition is not meant to serve; the
    behaviour is documented at the rule instead. `samplingPaddingFor` reads the *shipped*
    material, so a root whose profile has been patched through `applyMaterialProfile` — the
    calibration path — derives its gap from constants the renderer is no longer drawing with;
    the function says so and the frame loop's own `proxySamplingSigma` takes the patch, which is
    the seam a future caller with a profile in scope would use. The gap also bounds only the
    members the toolbar's own box contains. A member that
    escapes it — absolutely positioned out of the row, or a promoted platter measured in the same
    plane — is not bounded by the derivation, and is left to the `proxy-overlap-after-enforcement`
    diagnostic that already names it. A cross-toolbar gap (two `GlassToolbar`s side by side) is
    likewise the author's, unchanged by this child.

- 2026-09-10, W27f G1: `materialAtBackdrop` owns the linear profile-at-known-tone derivation,
  mirrored per pixel on DOM-backed WebGPU groups so mixed spans retain their own size law. The
  encoded source-over solve follows rim, coverage and shadow; proxy blur and the texture-source
  path stay unchanged. No constants fitted. §5.131 records all 22 G0 scenes in light/dark 1x,
  CSS coherence, the legacy capture-provenance limit, and the full ten-scene holdout per scheme
  spent at `1fff5e6`, plus separately frozen `bdf0029` dark-stack controls. Existing canonical
  texture controls were read, never rewritten or recaptured. Thick dark-body repair is measured;
  unknown-tone paint regressions, structured spread/colour, unhinted stack rim, dark-overlay
  regressions and missing dark fixtures remain named. 2,009 unit tests, 39 renderer browser tests
  (one attribution capture deliberately skipped), 35 measurement tests; goldens unchanged. A
  light/dark `/#page` sanity view is recorded, not the user's acceptance. G2 inherits the envelope
  and the S0/S1 distinction; it alone adopts a stack bound.

- 2026-09-10, W27f G0: measured 20 light-1x calibration scenes and the two requested stack
  holdout cells in six web configurations, with unhinted and identical-hint controls kept separate;
  claims §5.129 records body, paint, contour and exterior-shadow readings and their limits. The
  demo now shows ordinary page content at `#page`, beside the textured stage, with honest resolved
  readouts and GPU-specific state/contrast tests. Calibration 308 tests, demo 48 (none skipped),
  both lint/build checks passed. Review fixes enforce declared geometry, probe identity and scratch
  output; the CSS-only 2 × 2 px host excess is recorded, not changed. No material, profile, floor
  or canonical matrix moved; G1 is the next gate, not opened by this measurement.

- 2026-09-10: chartered. The re-score committed beside the matrix (`aa30022`); the grounding
  read (scratch, `/tmp/coverage-rescore/grounding.md`, its findings carried into §Design and
  §Surprises); the user's four decisions and the tier ruling recorded (Decision Log 1–5); W27a
  dispatched.
- 2026-09-10 (same day): **the reference moves on 2026-09-14.** The release-status research
  (web, primary sources: Apple's macOS page, the developer releases feed, the WWDC26 State of the
  Union) reports macOS 27 "Golden Gate" at RC build `26A428` on 2026-09-09 with public release
  scheduled for 2026-09-14; the latest public 26.x is 26.6.2 (`25G83`, 2026-08-17) with no
  documented Liquid Glass change since 26.5. On 27, existing apps inherit stronger diffusion of
  complex backdrops, a darkened edge, brighter speculars, more uniform refraction and revised
  window, sidebar and toolbar geometry with no recompile, and a user-facing ultraclear-to-tinted
  slider becomes a fixture axis; Apple documents no ScreenCaptureKit or Screen Recording consent
  change. Scheduling, recorded in §Deferred: the 26.5 profiles stay frozen and are never
  replaced; the OS 27 bed is captured as **new profile keys** (`apple-macos-27.0-…`) beside them
  on a clean capture machine on or after 2026-09-14, recording the exact GA build, the slider's
  position, the accessibility toggles including the newly independent Show Borders, and the
  display state; nothing in W27 fits against it. A one-time 26.5-versus-26.6.2 pixel comparison
  would turn release-note silence into evidence and is the user's call, since it needs the capture
  machine.
