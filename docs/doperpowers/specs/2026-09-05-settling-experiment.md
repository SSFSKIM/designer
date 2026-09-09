# The settling experiment: menu against derivation, measured

**Status:** pre-registered 2026-09-05, before any build ran. Runs in waves; results recorded at
the tail as they arrive.

## Purpose

Two initiatives replaced the skill's named-look menu with derivation: the stance layer
(`2026-09-05-stance-derivation.md`, plugin 2.0.0) and the composition grammar
(`2026-09-05-composition-grammar.md`, plugin 2.1.0). Each shipped with an acceptance run of a
few builds and a review loop, and each deferred the same question: does derivation actually buy
diversity that reaches the page, at a quality a designer would still ship? The research behind
both said there is no published study comparing named-look sampling with axis derivation for UI,
and named the experiment that would settle it (stance memo §3; composition memo risk 11). This
spec runs it.

The question, stated so that either answer is useful: **across the same briefs, with the same
model and the same budget, does each step of the doctrine (menu → axis derivation → derivation
plus grammar) raise effective diversity — spread among the outputs that a designer would still
deliver — without lowering what that designer would deliver?** If it does not, the doctrine is
costing more than it earns and the next initiative is diagnosis, not more doctrine.

## Design

**Arms.** Four, differing only in which skill the builder reads. The skill versions are frozen
copies extracted from git into the workspace so that edits to the live skill during the run
cannot leak into a later wave.

| Arm | Skill | What it isolates |
|---|---|---|
| `none` | no skill; the brief alone | the model's own defaults: the floor for diversity and the baseline for quality |
| `v1.1` | `skills/designer` at `282a9dd` (plugin 1.1.0) | the named-stance menu and the layout menu |
| `v2.0` | at `7536ad5` (plugin 2.0.0) | axis derivation with the layout menu still in place |
| `v2.1` | at `HEAD` of this spec's first commit (plugin 2.1.0) | derivation plus the composition grammar |

**Briefs.** Seven, verbatim from `evals/evals.json`, chosen so that each category has three
members (category sameness is where cloning shows) and one counterfactual pair is present.

| Brief | Eval | Category | Posture · activity the grammar should read |
|---|---|---|---|
| rail | 1 | console | workspace · monitor |
| pharmacy | 7 | console | workspace · monitor |
| fleet | 10 | console | workspace · monitor |
| library | 3 | narrative | narrative · decide |
| hardware | 4 | narrative | narrative · browse/decide |
| rebate | 12 | narrative | narrative · decide |
| compare | 11 | pair with fleet | transient · compare |

Brief 11's "that same bus operator" is reworded to "a regional bus operator's fleet manager" as
in the composition acceptance run, because a fresh agent has no antecedent.

**Cells and seeds.** Six briefs × four arms × two seeds, plus the compare brief × four arms × one
seed: 52 builds. Seeds are sampler seeds, `1000 + eval` and `2000 + eval`, identical across
arms so that where the ingredient lists coincide the draws coincide; the `none` arm has no
sampler and its two seeds are plain repeats. Within-brief repeats are what let the experiment
see mode collapse (the same brief, the same skill, the same page twice).

**Builder.** A fresh `general-purpose` subagent on Opus at the session's effort, the same as the
two acceptance runs. The prompt is one template with the arm's skill path substituted
(`docs/research/scripts/settling/cells.mjs prompt <id>` prints it); it names the brief, the
output directory, the seed, and the rule not to read anything else under the workspace. The
`none` arm's prompt additionally forbids reading `skills/`. Every arm may render with
`playwright-cli` if available. Nothing in the prompt describes what a good page is.

**Blinding.** Each cell gets a random six-character id; builds live under
`figma-design-workspace/settling/builds/<id>/`; the rating page sees ids, screenshots and copied
HTML only; the id → cell map is `manifest.json`, which the rating page never loads.

**Waves.** Eight builds at a time, one console brief and one narrative brief per wave, seed A
before seed B, the compare brief in wave four; a wave's measurement runs as soon as its builds
land. The run is resumable: a cell with `index.html` present is not rebuilt.

## Measures, declared before the run

**Q — quality, the primary endpoint.** Blinded pairwise human judgment by the user, on
UI-Bench's protocol (Jung et al. 2025): two builds side by side in iframes, full page,
randomised left/right, forced choice, the question *"Which would you be more likely to deliver to
a client?"* One departure: the brief is shown above the pair, because the memos' warning is that
raw spread flatters the arm that ignores the brief, and a judge who cannot see the brief cannot
penalise that. Pairs are within brief and across arms only, never seed against seed of one arm;
each build appears in three pairs (12 per six-arm-pair brief, 6 for the compare brief), 78
judgments, about forty minutes. Aggregation: Bradley–Terry strengths per brief (all pairs are
observed, so TrueSkill's sequential update is not needed), pooled per arm as the mean log-strength
across briefs, plus raw arm-versus-arm win rates with Wilson intervals. Single rater; no
agreement statistic is possible and none is claimed.

**V — the validity gate**, per build, for the effective-diversity metric: (a) the page renders in
Chromium with no uncaught script error; (b) no horizontal document overflow at 1440 px; (c) no
"lorem ipsum" or placeholder text; (d) at least nine in ten sampled text nodes reach 4.5 : 1
against their effective background; (e) the build won at least one of its three pairwise
judgments. (a)–(d) are mechanical; (e) is the human's.

**D — diversity.** Following Shypula et al. 2025's pairwise form, every measure is a mean over
pairs of `V_i · V_j · d(i, j)`, reported beside the raw mean with V dropped.

| | Measure | Pairs |
|---|---|---|
| D1 (headline) | first-viewport partition distance and pq-gram distance from `layout-topology.mjs` | within category across briefs; within brief across seeds, reported separately |
| D2 | accent-hue circular dispersion (1 − R̄); ground lightness and hue spread; screenshot hue-histogram earth-mover distance (Design Theater's colour channel) | same |
| D3 | display and body family sets: mean pairwise Jaccard distance; distinct display families over builds | same |
| D4 | prevalence of the canonical shapes from the survey: consoles — side region or main-plus-rail grid, first-viewport stat row; narrative — three-up, first-viewport card grid, headline band with an empty half | per arm, per category |

Tokens are read from the rendered page, not the record: the ground is the body's computed
background; the accent is the most chromatic colour among interactive elements; families are the
computed font stacks of the `h1`, the body, and any monospace element. This keeps `none` and
`v1.1`, which write no axis record, on the same footing as `v2.x`.

**F — fit, secondary.** For each brief, one blinded Opus rater sees the brief and every build's
screenshots (ids only) and answers five structural yes/no questions fixed per category (console:
the work region is the first read; nothing full-width sits above it but chrome; no numeric
summary strip precedes the work; no side region carries non-task content; the dominant region's
form matches the brief's unit — a table for lots, a queue for defects, positions on a field for
trains. Narrative: one region carries the proposition; the primary action is reachable in the
first viewport; no three equal peers the brief did not count; no empty half beside the headline;
the brief's named sections are all present). A vision-model rater is a weak aesthetic judge
(Visual Aesthetic Benchmark 2026: 26.5 % against experts' 68.9 %) and is used here only for
structure; its agreement with Q is reported, and it never overrides Q.

**P — the pair.** For fleet and compare under each arm: the compare build puts the three
suppliers on one axis in one region and the fleet build's first read is the exception region,
checked by the F rater's questions and by `layout-topology.mjs` (all four distances reported;
none pre-set as a bar — the composition spec's C1 showed partition alone cannot see this pair).

## Hypotheses and what would stop the doctrine

- **H1 (diversity).** Effective D1 across briefs within category rises monotonically
  `v1.1 < v2.0 ≤ v2.1` for the layout measures, and effective D2 accent dispersion rises
  `v1.1 < v2.0` (the stance layer's claim). A rise smaller than 0.03 partition or 0.05 dispersion
  is reported as no effect.
- **H2 (quality).** `v2.1` against `v1.1`, pooled over all briefs, wins at least 45 % of direct
  pairs; `v2.1` against `none` wins at least 60 %.
- **H3 (baseline).** `none` carries the canonical shapes at or above the survey's rates (stat row
  in 5 of 17 consoles, three-up in 22 of 32 landing pages); each skill arm below it, `v2.1` lowest.
- **H4 (mode collapse).** Within-brief seed distance (D1, D2) in `v2.x` exceeds `none`'s.
- **H5 (the pair).** P holds in both `v2.1` builds; the number of arms in which it holds is
  reported.

**Stop.** If `v2.1` wins fewer than 35 % of its direct pairs against `v1.1`, or effective D1 for
`v2.1` is not above `v1.1`, the doctrine is not earning its cost: the result is recorded here and
in both parent specs' Outcomes, and the next initiative is a diagnosis of *where* derivation
loses (the record, the sampler, the QA, or the grammar), not a further doctrine change. No
threshold above is moved after the run; a threshold that proves wrong is recorded as wrong with
the reason, beside the reading.

## Cost, declared

About 52 builder runs at 0.3–0.4 M tokens each for the skill arms and roughly a third of that
for `none`, so 15–20 M subagent tokens; seven waves of roughly forty-five minutes; forty minutes
of the user's judging time; seven blinded rater runs. The two acceptance runs cost about 0.4 M
per build, so this is roughly twelve acceptance runs' worth.

## Files

- This spec.
- `docs/research/scripts/settling/cells.mjs` — manifest and prompts;
  `measure.mjs` — screenshots, tokens, the mechanical gate, the topology run;
  `rate.py` — the blinded pairwise page and its judgment log;
  `judge.py` — a model judge's prompt per brief, on the same pairs (judge name and output
  directory as arguments);
  `analyze.py` — Bradley–Terry, diversity, effective diversity, the report.
- `figma-design-workspace/settling/` (gitignored): frozen skills, builds, screenshots,
  `judgments.jsonl`.
- Committed evidence: `docs/research/data/2026-09-05-settling/` — `manifest.json`,
  `measurements.json`, `topology.json`, `judgments.jsonl`, `judgments-model/<brief>.jsonl`,
  `judgments-model-run1/<brief>.jsonl`, `judgments-model-b/<brief>.jsonl`, `fit/<brief>.json`,
  `results.md`.

## Decision Log

- Decision: Four arms by skill version, not the stance memo's four (immutable systems; named
  archetypes with derivable tokens; axes; axes plus one ingredient) nor the composition memo's
  three (menu; grammar; grammar plus QA).
  Rationale: the versions are the doctrine as it actually shipped, each step isolating one
  layer; the memos' arms would need skills that never existed and would measure hypotheticals.
  `none` is added because every survey finding had a no-skill build carrying the same shape.
  Date/Author: 2026-09-05, Claude.

- Decision: The user is the single judge, on UI-Bench's question, with the brief shown.
  Rationale: the memos rule out a vision-model judge for quality; the user is the taste the
  skill exists to serve; showing the brief is the one departure and is argued above.
  Date/Author: 2026-09-05, Claude.

- Decision: Effective diversity uses Shypula's pairwise form with a gate that includes one human
  clause (won at least one pair).
  Rationale: a mechanical gate alone passes a page that is valid and dreadful; the human clause
  is the cheapest reading of Q that does not require a threshold on a noisy strength.
  Date/Author: 2026-09-05, Claude.

- Decision: Tokens are read from the rendered page for every arm.
  Rationale: two arms have no axis record; reading the record would measure the record, not the
  page.
  Date/Author: 2026-09-05, Claude.

- Decision: Implementation details fixed at the smoke test, before wave one was measured. The
  accent is the most chromatic colour (OKLCH C ≥ 0.06, 0.2 ≤ L ≤ 0.9) on interactive elements,
  and where those carry no chroma — a status-only accent job leaves them monochrome — the most
  chromatic colour anywhere on the page. The contrast clause of V uses WCAG's own large-text
  allowance (3 : 1 at 24 px, or 18.66 px bold). D4's "side region" is reported as two columns,
  an edge region by role and a two-track band at 1.5 : 1 or wider, because the fleet acceptance
  build showed a derived band that the raw rule reads as a rail. The smoke test ran the whole
  chain on two derivation-eval builds in a scratch workspace.
  Date/Author: 2026-09-05, Claude.

- Decision: A supplementary D2 row reads the accent's *job* — declared in the 2.x record, inferred
  for the other arms from where the extractor found the colour — and reports dispersion over
  directional accents only. The pre-registered D2 row is unchanged and stays first.
  Rationale: the extractor's fallback on an achromatic interactive layer returns the loudest
  status colour, so the pre-registered hue list charges a 2.x build that chose no accent with a
  critical red. Half the 2.x builds made that choice; without the supplement the arm that
  declines an accent looks like the arm that always picks red.
  Date/Author: 2026-09-06, Claude.

- Decision: From wave five the waves overlapped, and a running builder's directory carries the
  `.incomplete` marker until its report arrives; the measurer and the manifest skip marked
  builds, and the marker is removed by hand on the builder's notification.
  Rationale: builders write `index.html` early and iterate, so without the marker the measurer
  captured half-built pages and the rating page would have served them to the judge. The marker
  was already the convention for interrupted builders; it now means "not finished" in either
  sense.
  Date/Author: 2026-09-06, Claude.

- Decision: Two instrument fixes after wave seven, both re-run over all 52 builds with the diff
  recorded under Surprises: the colour parser no longer divides canvas bytes by alpha (they are
  already un-premultiplied), and the measurer re-measures a build whose screenshots are missing.
  A count-based accent (the hue cluster on the most interactive elements) is recorded beside the
  max-chroma accent but not used in any table.
  Rationale: the alpha bug inflated every semi-transparent colour; the diff shows it moved no gate
  verdict and one accent hex, so the pre-registered readings stand. The count-based read was tried
  as a better accent locator and is no better (it finds body ink on one build, a status colour on
  another); it is kept as data, not as a measure.
  Date/Author: 2026-09-06, Claude.

- Decision: A second judge, a blinded `astra-medium` rater, on the same 78 pairs (same schedule,
  same left/right, screenshots and ids only), grouped by brief so a rater reads a brief's eight
  pages once and decides its twelve pairs; its judgments live in `judgments-model/<brief>.jsonl`
  and the report carries a Q table per judge and raw agreement with Cohen's κ over the pairs
  both judged. One rater takes several briefs in one prompt (`judge.py prompt a,b,c`); the first
  run had fanned out six raters, one per brief, before the user's direction to batch arrived, and
  those six were left to finish.
  Rationale: the user's direction ("make it be a visual judge too — we'll collect both"; "prefer
  batch if possible than fan-out per one"). The human's Q stays the primary endpoint and the
  gate's human clause reads only the human file; the model's table is secondary, and the
  agreement statistic is the reading the pre-registration said a single rater could not give.
  The memos' warning that a vision model is a weak aesthetic judge stands, which is why it is a
  second column and not a replacement.
  Date/Author: 2026-09-08, Claude.

- Decision: The tiebreak for Q. The user finished the 78 pairs and reported that the sitting
  was long and tiring, that the verdicts may be inaccurate, and that if so the model judge's
  result is the tiebreaker. Applied as a majority of three blinded judges rather than as the
  second judge overruling the first: a third judge (`claude-opus`, the same prompt, the same 78
  pairs, four batches of one or two briefs) was added, and `analyze.py` reports Q per judge, a
  Q★ majority table, the H2 thresholds and the stop clause per judge, and every pair of judges'
  agreement. The human file remains the pre-registered primary endpoint and the only one the
  gate's human clause reads; every claim below is stated under both readings.
  Rationale: the disagreement is not fatigue-shaped. The human and the astra-medium rater agree
  on 41 of 78 pairs (κ 0.03), and the rate is the same in the first sitting (3 pairs at 50 s
  each), the second (14 pairs, 29 s median) and the last (61 pairs, 14 s median): 0.33, 0.50,
  0.54; verdicts under 8 s agree with the model at 0.58 and slower ones at 0.50. The
  disagreement sits on the cross-generation pairs (`none` and `v1.1` against 2.x) and on four
  briefs (pharmacy 3 of 12 agree, compare 2 of 6, library 4 of 12, rebate 5 of 12), and it is a
  consistent preference, not noise: the human takes the no-skill page over `v2.0` on 10 of 13.
  Letting one judge overrule the other on that pattern would replace the endpoint with the
  other judge's taste; a majority of three is the nearest thing to the tiebreak the user asked
  for in which no judge decides alone.
  Date/Author: 2026-09-09, Claude, on the user's direction.

## Surprises & Discoveries

- Observation: Chromium serialises a computed colour in the syntax it was written in, so a
  build whose tokens are `oklch()` reports `oklch(…)` from `getComputedStyle`, and a parser
  that expects `rgb()` reads its ground as white, its accent as absent and its contrast sample
  as empty (an empty sample passed the gate vacuously). Four of wave one's eight builds were
  affected, exactly the four whose skills teach OKLCH tokens.
  Evidence: wave one's first measurement against the builders' own reports (two "dark" grounds
  read as `#FFFFFF`). Fixed before any judgment was collected: every colour is normalised
  through a canvas; the wave was re-measured.

- Observation: The 1.1 menu's rail build carries the reference implementation's accent hex
  `#D46B2C` verbatim, and its rebate build a second orange at 46°; the two arms' accents are
  0.0 apart in dispersion. The stance spec's founding finding reproduces under the frozen old
  skill on the first wave.
  Evidence: wave one D2 row for `v1.1`.

- Observation: The no-skill arm produced the two shapes the memos named as defaults — a dark
  command-centre board with a seven-tile stat row for the console, and a cream, serif, terracotta
  landing page with a stat row and a three-up for the rebate — and both fail the contrast clause
  of the gate (0.85 and 0.76 of sampled text).
  Evidence: wave one V and D4 rows for `none`.

- Observation: The 1.1 pharmacy builder reported that the old stance reference "routes healthcare
  products to Institutional calm directly regardless of what the sampler returns", and ported it
  intact. The category-to-values lookup the stance spec was founded on is visible in the builder's
  own words under the frozen skill.
  Evidence: the wave-two 1.1 pharmacy report; its four sampler draws all declined.

- Observation: Convergence relocated to the signature element. Both derivation arms' library
  builds (2.0 and 2.1, different agents, no shared context) drew the same hero object — a
  reader's card with eight stamp boxes, four filled — from the brief's "weekly" and the sampler's
  shared draw; the 1.1 build drew an eight-shape card. The stance layer's "signature" step is a
  new attractor for the same reason the accent was: one prompt, one most-probable answer.
  Evidence: wave-two first-viewport captures for 99499b, 672565, dd3f5c.

- Observation: A 2.1 build carries a three-step "how it works" row under a hero — the narrative
  three-up the grammar names as a default — on a brief that counts no three.
  Evidence: 672565's D4 row; the row is a repeated group of three, three columns, outside the
  footer.

- Observation: The instrument's pairwise matrices are arrays in build order, not keyed by file;
  the first analysis read every layout distance as missing. Fixed before any diversity number was
  reported.
  Evidence: wave-two results before and after the index fix.

- Observation: The hardware brief converged on one object across all three skill arms — a
  will-call or shelf ticket drawn as a card at the right of the hero, with "on the shelf, not in a
  warehouse" as the proposition — while the no-skill build drew a storefront. Three different
  skills, three agents, one signature; the stamp-card finding from the library brief repeats on
  the second narrative brief.
  Evidence: wave-three first-viewport captures for 5c24f6, 0663a2, c7de7e against 4d761e.

- Observation: A 2.1 build fails the mechanical gate on a 31 px horizontal overflow from a
  sortable table header, after its builder reported "no page-level horizontal scroll" at four
  widths. The builder measured at 1512 px; the gate measures at 1440. Recorded as a gate failure,
  not repaired.
  Evidence: 49e6cb, `scrollWidth` 1471 against 1440.

- Observation: Wave three's builders were interrupted by a plan-usage limit and resumed in
  place with their context; seven of eight finished after resumption with no visible break in
  their records. An `.incomplete` marker now keeps an interrupted build out of measurement and
  rating until its builder reports done.
  Evidence: the seven resumed reports; the marker respected by `measure.mjs` and `cells.mjs`.

- Observation: On the compare brief every arm put the three suppliers on one axis, and all
  four led with a document head — title, prose, a metadata strip — above the comparison; the
  no-skill build added a recommendation card before the matrix. The grammar's own transient
  rule (no band above the action) was not followed by its own arm, whose first viewport is a
  title, a paragraph, and a metadata strip over a scale.
  Evidence: wave-four first-viewport captures for ede597, 32cc11, 033fcb, d178d1.

- Observation: The rail brief's second seed reproduced the first seed's forms arm by arm — the
  1.1 arm a light steel console with a stat row over a train graph beside an exceptions rail,
  the 2.0 and 2.1 arms dark or zero-chroma string-line boards with an exception queue first —
  and the no-skill arm its dark command-centre board with a seven-tile stat row both times.
  Within-brief partition distance across seeds is 0.22–0.25 for every arm, the same as the
  across-brief figure; the instrument does not separate "same brief, same skill, second run"
  from "different brief".
  Evidence: the within-brief D table after wave four; the rail captures for both seeds.

- Observation: Every wave-four builder was killed by a revoked login before writing a file;
  all eight were resumed in place and finished. One resumed builder stopped after a single
  tool call and needed a second nudge; one timed out once more and was resumed again.
  Evidence: the wave-four task notifications.

- Observation: The validity gate is the no-skill arm's story. Six of thirteen no-skill builds fail
  the contrast clause (rail A and B, rebate A, pharmacy A and B, library B), every one on small
  muted metadata text between 3.3 and 4.1 : 1; the three skill arms fail once in thirty-nine, on
  a 31 px overflow. Effective across-brief diversity for `none` consoles is therefore 0.0 — the
  only two valid no-skill consoles are the two fleet builds, which are the same brief — and the
  raw column is the one to read for that arm.
  Evidence: the V table in `results.md`; the `fails` lists in `measurements.json`.

- Observation: Half the 2.x builds chose no directional accent (2.0: seven of thirteen; 2.1: six of
  thirteen, as status-only or none), and on those the max-chroma extractor returns the critical
  red. Read by declared job, dispersion over directional accents is 0.36 (`none`), 0.33 (`v1.1`),
  0.55 (`v2.0`), 0.81 (`v2.1`); the pre-registered row reads 0.28 / 0.34 / 0.41 / 0.48. The
  no-skill and menu arms cluster between 23° and 55° (orange-red) with an occasional violet; the
  2.x directional accents sit at 220–282° as often as in the red band. One 2.1 build (fleet B)
  is mis-read even by job: its declared blue accent (255°) has less chroma than the red border
  on its caution buttons, so the extractor reports 27°; with that one hue corrected the 2.1
  figure is 0.82. An accent is a role, and no colour statistic recovers the role on every page.
  Evidence: the D2 supplement in `results.md`; `DESIGN.md` of `f8973a`; the count-based accent
  field, which also returns the red.

- Observation: The pharmacy brief's three skill arms open on the controlled-substance count
  discrepancy on both seeds (a fentanyl or hydromorphone variance as the first item, in 1.1 as a
  banner, in 2.0 as a boxed-warning block, in 2.1 as the head of a time-bucketed queue), and the
  no-skill arm opens on a six-tile KPI strip on both. Six of the eight pharmacy builds score 5 of
  5 on fit; the two that do not are no-skill B (2) and 1.1 B (4, for the banner).
  Evidence: `fit/pharmacy.json`; the pharmacy first-viewport captures.

- Observation: Derivation alone does not remove the stat row; the grammar does. The 2.0 arm
  carries a first-viewport stat strip on fleet B (four tiles above the workshop board, fit 2 of
  5, the same score as no-skill fleet A) and on rebate B (four tiles under the nav); 2.1 carries
  none on any console (0 of 6) and one on a narrative. D4 over all 52: consoles with a stat row
  in the first viewport — `none` 3, `v1.1` 1, `v2.0` 1, `v2.1` 0; consoles with a side region —
  `none` 2, `v2.0` 1, the others 0; every 2.1 console is a main-plus-rail band at 1.5 : 1 or
  wider (6 of 6).
  Evidence: D4 in `results.md`; `fit/fleet.json`; the `645bc6` and `ea1cfd` captures.

- Observation: The library brief converges on a stamp motif under derivation across seeds: 2.0 A's
  stamp card, 2.0 B's fill-a-square log grid, 2.1 B's sheet of ten perforated week-stamps. Both
  2.x seed-B builds also take a saturated green or teal ground (L 0.885 and 0.679) with a
  stamp-red accent. The 1.1 seed-B build took the sampler's "topographic" stance literally — a
  contour map on dark spruce with the eight weeks as trail stations — and is the most distinct
  library page in the set.
  Evidence: the library captures; `DESIGN.md` of `f3d810`, `8f113d`, `b0bad8`.

- Observation: On the hardware brief the four arms are least distinguishable by eye. All four
  seed-B first viewports are a headline at left, a panel at right (storefront illustration, hours
  card, store plate, three product cards) and a row of three facts beneath; 2.0 and 2.1 wrote
  nearly the same headline ("Check the shelf before you drive over", "See the shelf before you
  drive over"), and no-skill and 1.1 the same opener ("Seventy-five years on Water Street",
  "Seventy-seven years on James Street"). Fit is saturated: six of eight at 5, two at 4, both
  for an unrequested three-up.
  Evidence: the hardware captures; `fit/hardware.json`.

- Observation: The compare brief's blinded fit rater put every arm within one point: no skill
  2 of 5, and 1.1, 2.0 and 2.1 each 3 of 5. All four fail q4 and q5 — every build places a title
  band and a summary or metadata strip above the comparison, and every build carries a stat row
  or three-column block somewhere on the page. The 2.1 build's first viewport is a full-width
  "tender evaluation" card with a six-cell metadata strip before the quotes; only its pinned
  award bar passes q3, where the no-skill build's award control is the last row of its table.
  So on the one pair-category brief the grammar removed the side column and nothing else; the
  headline band it forbids on consoles reappears as an evaluation header.
  Evidence: `fit/compare.json`; the compare first-viewport captures.

- Observation: The fit rater is consistent within a brief and reports its own borderline calls
  (an "Apply" link in a page's section navigation counted as reachable; numeric readout rows and
  strips of four or more steps not counted as three-up), but the same arm can score 5 on one seed
  and 2 on the other (2.0 rail: A 5, B 2, the B build leading with a status strip). Per-brief
  means by arm over all seven briefs: `none` 3.38, `v1.1` 4.23, `v2.0` 4.23, `v2.1` 4.62.
  Evidence: `fit/*.json`; the F table.

- Observation: Three procedure faults, all caught before a judgment touched them. The measurer
  ran while waves overlapped and captured seven half-built pages (builders write `index.html`
  early); the rating page would have served them, so running builds now carry the `.incomplete`
  marker. A builder that finished as the measurer ran deleted the measurer's two screenshots in
  its own cleanup (library 2.1 B), so the measurer now re-measures a build with missing shots.
  And the rating server had been restarted on a schedule that no longer matched the judgment
  file's pair ids; it was restarted again from the current code before judging resumed.
  Evidence: the wave five and six task notifications; this session's shell log.

- Observation: The pairwise schedule was not deterministic. Briefs were ordered by first wave with
  ties left to a set's iteration order, which differs per process, so every process drew its own
  left/right and seed pairing from the fixed seed. This is why the restarted rating server once
  showed all 78 pairs pending with three judged, and why the model judge's first run — six
  raters, one per brief, each prompt printed by its own process — judged pairs of which only 70
  of 78 exist in the fixed schedule. Fixed by breaking the tie on the brief's name and matching
  judged pairs by unordered id; the three human judgments all lie in the fixed schedule. The
  first run is kept as `judgments-model-run1/` and read against the batch run as a self-agreement
  sample.
  Evidence: three `PYTHONHASHSEED` values now give one schedule digest; the overlap counts.

- Observation: The colour parser divided un-premultiplied canvas bytes by alpha, inflating every
  semi-transparent colour. Re-measuring all 52 builds after the fix changed no gate verdict, two
  contrast rates by under 0.01, and one accent hex (fleet 2.1 B, from a malformed seven-digit
  value to the same red border read correctly).
  Evidence: the diff printed at the fix; `measurements.json`.

- Observation: Three blinded judges agree with one another at chance on "which would you
  deliver": human–astra 41 of 78 (κ 0.03), human–opus 47 (κ 0.17), astra–opus 46 (κ 0.14);
  unanimous on 28 of 78. Each orders the arms differently: the human puts `v1.1` and `none` a
  full Bradley–Terry unit above `v2.0` and `v2.1`, astra-medium the reverse, claude-opus `none`
  first and `v2.1` last. Each stated a criterion the others did not weigh — astra the
  decision-ordered queue, opus the light high-contrast console and whether the goods are
  pictured, the human (read from the pairs) the conventional console shell over the editorial
  one. The astra rater is self-consistent across two runs (κ 0.85), so this is not rater noise:
  at this level of craft the forced choice is decided by taste, and the arms differ mostly in
  taste.
  Evidence: `results.md`, the three Q tables and the agreement section; the raters' reason
  fields in `judgments-model*/`.

- Observation: Two capture artifacts the judges saw. The first-viewport capture of two no-skill
  library builds (30f897, which scroll-snaps, and 5c042a) is not the top of the page — the page
  scrolled itself before the capture — so the model judges, who read both captures, saw a
  hero-less, half-blank first viewport that the human, who read the full-page capture only,
  never saw; the astra rater cites it in a reason. The bias runs against `none`, so it cannot
  rescue H2. And the `v2.1` library build 672565 overflowed to 2760 px wide at capture time while
  the gate's overflow read at load was false; every judge saw its content in the left half of an
  over-wide sheet, and the opus rater cites it. The gate reads `scrollWidth` once at load; the
  full-page capture's width is the better overflow instrument.
  Evidence: a pixel comparison of every build's first-viewport capture against the top of its
  full-page capture (8 of 52 differ on more than 7 % of pixels, six of them narrative pages with
  reveal-on-scroll); the capture's size.

## Deferred

- The stance memo's hypothetical arms (archetypes with derivable tokens; axes plus one
  ingredient), if this run leaves the stance layer's contribution ambiguous.
- Design Theater's UIClip channel; no local model.
- The diagnosis initiative the stop rule names: where within-category layout distance is lost
  under 2.1 (the record's composition lines, the grammar's console forms, or the instrument),
  read against Q — and, now that Q is in, against the quality reading too: why two of three
  judges prefer the no-skill page to either 2.x arm and `v2.0` to `v2.1`.
- The overflow gate read from the full-page capture's width, and one capture set for every
  judge (the first viewport taken at scroll 0 after the page has settled), for the next run.
- An accent locator that reads the role rather than the colour statistic — the colour of the
  primary action control, falling back to the declared job — for the next rendered-token run.

## Outcomes & Retrospective

All 52 builds exist, are measured, rated for fit, and judged on all 78 pairs by three blinded
judges: the user (the primary endpoint), an astra-medium rater and a claude-opus rater. Everything
below is final (`python3 docs/research/scripts/settling/analyze.py` rebuilds `results.md`).

**H1 (diversity) — the token clause holds, the layout clause does not.** Effective D2 accent
dispersion rises `v1.1` 0.34 → `v2.0` 0.41 → `v2.1` 0.52, a rise of 0.07 over the 0.05 bar; read by
declared accent job it is 0.33 → 0.55 → 0.81, and the no-skill arm sits at 0.36 with ten of its
thirteen accents between 21° and 74°. Effective D1 is not monotonic. Partition distance across
briefs within category: consoles `v1.1` 0.257, `v2.0` 0.308, `v2.1` 0.115 (raw 0.212, the
effective figure carrying one overflow failure); narrative 0.254, 0.270, 0.273. pq-gram: consoles
0.483, 0.616, 0.432 (raw 0.601); narrative 0.590, 0.601, 0.500. So `v2.0` is above `v1.1` on both
layout measures in both categories (the console partition rise of 0.05 clears the bar; the
narrative rise of 0.016 does not), and `v2.1` is above `v1.1` only on raw console pq-gram. Family
Jaccard is flat and high for every arm (0.75–0.94): family choice was never where convergence
lived. Distinct display families over thirteen builds: 7 (`none`), 8, 8, 9.

**H2 (quality) — not met.** On the primary judge `v2.1` wins 4 of 13 direct pairs against
`v1.1` (0.31, Wilson 0.13–0.58) and 6 of 13 against `none` (0.46, 0.23–0.71), under both
thresholds (0.45 and 0.60). On the majority of the three judges (the tiebreak, Decision Log
2026-09-09) it wins 6 of 13 against `v1.1` (0.46, over the bar) and 5 of 13 against `none` (0.38,
under it). Only the astra-medium rater clears both (8 and 9 of 13). Pooled Bradley–Terry on the
human's file: `v1.1` −0.49, `none` −0.64, `v2.0` −1.40, `v2.1` −1.59; on the majority: `none`
−0.55, `v2.0` −0.79, `v1.1` −1.55, `v2.1` −1.82. Two readings are shared by two of the three
judges and by the majority: `v2.0` beats `v1.1` (majority 9 of 13; the human alone has the
reverse, 5 of 13), and `v2.1` does not beat `v2.0` (majority 4 of 13; the human alone 7 of 13).
So derivation is preferred to the menu, the grammar on top of derivation is not preferred to
derivation, and no skill arm is preferred to no skill by two of three judges (`none` over `v2.0`
8 of 13, over `v2.1` 8 of 13 on the majority).

**Q2 — the model judge (added 2026-09-08, secondary).** A blinded `astra-medium` rater on the
same 78 pairs. Pooled Bradley–Terry log-strength: `none` −1.84, `v1.1` −1.81, `v2.0` −0.58,
`v2.1` −0.53 — the two derivation arms a full unit above the menu and no-skill arms, which it
cannot tell apart (`none` wins 6 of 13 against `v1.1`), and `v2.0` against `v2.1` a coin flip (7 of
13). Its per-brief pattern is not uniform: on the hardware brief it prefers both no-skill pages
to everything (3 of 3 each) and both `v2.1` pages to nothing (0 of 3 each); on rail and compare
`v2.1` wins every pair it is in; on fleet `v2.0` does. The rater is stable — its first run, six
raters on a schedule that differed per process, agrees with the batch run on 65 of the 70 pairs
they share (κ 0.85) — and its agreement with the human is chance (41 of 78, κ 0.03). The memos'
warning stands: this is a structural and legibility reading by a vision model, the column beside
the human's, not the endpoint.

**Q3 — the third judge (added 2026-09-09, secondary).** A blinded `claude-opus` rater on the
same 78 pairs, four batches. Pooled Bradley–Terry: `none` −0.43, `v2.0` −0.74, `v1.1` −1.66,
`v2.1` −1.88. It prefers the no-skill page to every skill arm (9, 8 and 10 of 13), `v2.0` to
`v1.1` (9 of 13) and `v2.0` to `v2.1` (9 of 13); its stated criteria were completeness without
clipping, light high-contrast consoles for all-shift use, and whether a shop page shows the
goods. It agrees with the human on 47 of 78 (κ 0.17) and with the astra rater on 46 (κ 0.14).

**Q★ — the majority.** One verdict per pair by majority of the three; unanimous on 28 of 78,
the human outvoted on 18. Pooled Bradley–Terry: `none` −0.55, `v2.0` −0.79, `v1.1` −1.55, `v2.1`
−1.82. Arm pairs: `none` over `v1.1` 7 of 13, over `v2.0` 8, over `v2.1` 8; `v2.0` over `v1.1` 9;
`v2.1` over `v1.1` 6; `v2.0` over `v2.1` 9.

**H3 (baseline) — holds for the stat row, half-holds for the three-up.** `none` carries a
first-viewport stat row on 3 of 6 consoles (the survey's rate was 5 of 17) and a three-up on 5
of 6 narrative pages (the survey's 22 of 32); the skill arms carry the stat row on 1, 1 and 0
consoles, `v2.1` lowest as predicted. The three-up is `v1.1` 5, `v2.0` 3, `v2.1` 3 of 6: the menu
arm matches the baseline, and `v2.1` ties `v2.0` rather than sitting lowest. The side region
(the survey's other console shape) is `none` 2, `v2.0` 1, the others 0; every `v2.1` console is a
main-plus-rail band at 1.5 : 1 or wider.

**H4 (mode collapse) — holds on narrative layout, not on consoles.** Within-brief seed distance,
raw partition: consoles `none` 0.247 against `v2.0` 0.215 and `v2.1` 0.193; narrative `none`
0.200 against 0.271 and 0.264. Screenshot hue distance across seeds is *lower* under 2.x on
consoles (0.127 against 0.071 and 0.045). The effective column has 2.x above `none` everywhere,
but only because five of six no-skill consoles fail the gate. By eye the same signatures recur
across seeds under derivation (the stamp motif on the library brief, the count discrepancy on
the pharmacy brief) and across arms on the hardware brief, where the four seed-B first viewports
share one composition and two headline sentences.

**H5 (the pair) — holds.** Both `v2.1` fleet builds open on the exception queue (fit q1 = 1) and
the `v2.1` compare page puts the three suppliers on one axis in one region. It holds for every
build of two arms (`v1.1`, `v2.1`), for `v2.0`'s seed A only (seed B leads with a stat strip),
and for `none`'s seed B only. The compare page under every arm carries a band above the
comparison and a stat row or three-column block somewhere, so P is satisfied by the pair's first
reads and not by the compare page's whole structure.

**F (fit, secondary) — monotone in the doctrine.** Mean yes-of-five over all thirteen builds per
arm: `none` 3.38, `v1.1` 4.23, `v2.0` 4.23, `v2.1` 4.62. Consoles separate the arms most (rail:
2.0, 2.5, 3.5, 5.0; fleet: 3.0, 5.0, 3.5, 5.0; pharmacy: 3.5, 4.5, 5.0, 5.0); the hardware brief is
saturated at 4–5 for every arm; the compare brief is 2, 3, 3, 3.

**V (the gate) — the no-skill arm's finding.** Six of thirteen `none` builds fail on contrast,
all on small muted text at 3.3–4.1 : 1; the skill arms fail once in thirty-nine (a 31 px
overflow). This is the doctrine's least glamorous and most reliable effect: every skill version
teaches a contrast check and the fresh agent skips one, so the no-skill arm's effective
diversity is mostly gate.

**The stop rule.** Both clauses read. The layout clause fires: effective D1 for `v2.1` is not
above `v1.1` (consoles 0.115 against 0.257; narrative 0.273 against 0.254, a rise under the 0.03
bar). The quality clause fires on the primary judge (`v2.1` wins 31 % of its direct pairs against
`v1.1`; the clause fires under 35 %) and does not fire on the majority of three (46 %) or on
either model judge alone (62 %, 54 %). Under the pre-registration one fired clause is enough,
and the layout clause fired under every reading, so the consequence is the same: recorded here
and in both parent specs, and the next initiative is a diagnosis, not a doctrine change. What
the tiebreak changes is the diagnosis's brief. Read by the human alone the doctrine loses at
`v1.1` → 2.x; read by the majority, derivation (2.0) is preferred to the menu, the grammar (2.1)
is not preferred to derivation, and neither is preferred to no skill. The reading to carry into that diagnosis:
what the grammar did on consoles is converge them onto the brief's form (queue or table first,
one rail band, no stat row, no side column — 6 of 6), and within-category partition distance is
exactly the quantity that convergence lowers. The composition spec's C1 had already shown
partition alone cannot see this kind of form change (within-brief distance equals across-brief
distance for every arm). The clause was pre-registered on a measure that penalises the layer's
intended effect, and it is reported as fired because no threshold moves after the run. Whether
that convergence is a loss is Q's question, and Q is the user's.

**What the experiment settles now.** (1) Derivation moved the tokens: accent hue and ground
spread with the doctrine, and half the 2.x builds chose no directional accent at all, which no
menu build did. (2) The grammar, not derivation, removed the console shapes; 2.0 still carries
a stat strip on two seed-B builds. (3) No arm holds the compare brief to its form. (4) Layout
diversity within a category is not a property any version raised; the honest instrument for
the grammar is fit, and fit rose with every version. (5) The biggest single difference between
no skill and any skill is that the skilled page passes contrast. (6) On "which would you
deliver", three blinded judges agree at chance and no skill arm is preferred to no skill by two
of them; the one reading two of three share is that derivation beats the menu and the grammar
does not beat derivation. Quality, as this experiment could measure it, did not rise with the
doctrine.

**Retrospective.** Rendered tokens kept four arms on one footing and were worth the two
instrument faults they cost (the OKLCH serialisation, the alpha division). The accent extractor
is the weak reading: an accent is a role, and a page whose interactive layer is achromatic or
whose caution buttons out-saturate its action colour defeats any colour statistic; the declared
job is the better read where a record exists. Overlapping waves need the `.incomplete` marker
from the first build, not from the first accident. The blinded fit rater was consistent and
cheap and its per-brief means track the D4 counts; it should be the acceptance instrument for
the next grammar change rather than partition distance. Quality was the endpoint the design
under-provided for: one human judge on a forced choice over 78 pairs, one sitting of 61, and
the two model judges added afterward agree with the human and with each other at chance. The
next quality question needs several judges from the start, a criterion-anchored form per brief
(the fit rating's yes-of-five shape) beside the forced choice, and one capture set for every
judge. Seven waves cost about 15 M subagent tokens over roughly nine hours of wall clock, within
the declared budget; the two model judges cost about 0.7 M more.

## Revision Notes

- 2026-09-05: pre-registered before wave one; direction from the user ("Let's go to settling
  experiment").
- 2026-09-06: all seven waves built, measured and fit-rated; Decision Log, Surprises, Deferred and
  Outcomes written; Q, H2 and the stop rule's quality clause left pending on the user's judging.
- 2026-09-08: second judge added on the user's direction (Decision Log); schedule determinism fault
  found and fixed (Surprises); Q2 and the model's read of H2 and the stop rule written.
- 2026-09-09: the user's 78 judgments in; a third judge and the majority tiebreak added on the
  user's direction (Decision Log); Q, Q3, Q★, H2 and the stop rule's quality clause written; the
  judges' chance-level agreement and two capture artifacts recorded (Surprises).
