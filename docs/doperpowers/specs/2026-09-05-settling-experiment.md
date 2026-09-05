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
  `analyze.py` — Bradley–Terry, diversity, effective diversity, the report.
- `figma-design-workspace/settling/` (gitignored): frozen skills, builds, screenshots,
  `judgments.jsonl`.
- Committed evidence: `docs/research/data/2026-09-05-settling/` — `manifest.json`,
  `measurements.json`, `topology.json`, `judgments.jsonl`, `fit.json`, `results.md`.

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

## Surprises & Discoveries

Pending — recorded as the waves land.

## Deferred

- A second judge, for an agreement statistic.
- The stance memo's hypothetical arms (archetypes with derivable tokens; axes plus one
  ingredient), if this run leaves the stance layer's contribution ambiguous.
- Design Theater's UIClip channel; no local model.

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-09-05: pre-registered before wave one; direction from the user ("Let's go to settling
  experiment").
