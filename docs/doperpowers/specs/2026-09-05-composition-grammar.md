# Composition grammar

**Status:** in progress. **Follows** `2026-09-05-stance-derivation.md` (its Deferred list opens
with this initiative) and applies the same move one layer over: the layout menu in
`references/composition.md` becomes a brief-derived grammar, the named patterns become priors,
and a composition QA layer gets a mechanical clone check. Research basis:
`docs/research/2026-09-05-composition-grammar-prior-art.md` (the memo, with the local
measurement in its §0 and the instrument at `docs/research/scripts/layout-topology.mjs`) and two
further rounds (`docs/research/gpt-research-1.md`, `docs/research/gpt-reseatch-2.md`).

## Purpose

After this change, a person can hand the skill two briefs for the same product whose tasks
differ — resolve exceptions in a queue, or compare three alternatives on shared criteria — and
receive two pages whose *topology* follows the task: the exception region first and dominant in
one, the compared units aligned on one axis in one region in the other. And they can hand it a
landing brief and not receive the scaffold every landing page gets today: a left-ranged headline
band with an empty right half, a three-up, a pricing trio, an FAQ. Where a familiar arrangement is
the right answer — a list beside its detail, a table for a matrix — they receive it, with the
line of the record that earned it.

How to see it working: the Acceptance section.

## The measured problem

Two instruments, run over the eval builds under `figma-design-workspace/` (gitignored, local
evidence) in Chromium at 1440 × 900 (memo §0; `derivation-eval/layout-signature.mjs`):

- **Landing pages converge hard.** 16 of 20 open with the same construction: a full-width band,
  a left-ranged headline in a 487–675px measure at a 140–192px gutter, no image, empty right
  half. 0 of 20 use a split hero. 22 of 32 carry a card grid of exactly three in three columns.
  8 of 20 carry an FAQ accordion. 12 of 20 have exactly four top-level sections.
- **Consoles converge on chrome, not on shape.** 15 builds produced 9 first-viewport
  topologies with no majority; but 12 of 17 are a two-track main-plus-rail grid, and the
  records pick the arrangement *by name* ("exception-first over table-led") — the pharmacy's
  unit is a lot in a table, the wind farm's a turbine on a plate, and nothing in the reference
  let that difference act.
- **The reference's snippet clones like the hex did.** `composition.md`'s asymmetric-split
  example, `minmax(0,1.15fr) minmax(0,0.85fr)`, is byte-identical in 7 builds (6 skill-arm); its
  1.35 : 1 ratio is the most common two-track ratio in the corpus while the reference's own
  prose says the ratio "has to be felt (60/40 minimum)". `repeat(3, …)` is in 20 of 51 files.
- **The stance re-founding did not move layout.** With-skill builds sit no farther from
  no-skill builds in first-viewport partition (0.18–0.31) than unrelated builds sit from each
  other (mean 0.232). The record stores a pattern name and grid numbers; there is no variable a
  different task could act through.
- **The literature agrees it is the harder half.** Design Theater 2026 found layout and
  appearance converging across five tools; Goree 2021 found web layout distance down 44% in a
  decade, tracking library defaults. Nothing published compiles a brief into a layout; the
  nearest four (Tidwell's organisation × screen role, Material's relation × window class,
  Cooper's postures, Card & Mackinlay's data relations) are the priors this design assembles.

## Terms

- **Composition.** The page's region topology: what regions exist, which dominates, how they are
  grouped, ordered, aligned, attached, repeated, and disclosed. Distinct from the stance (the
  visual system) and from chrome (the conventional shell).
- **Composition line.** One of six properties read off the brief, with a reason, recorded in
  `DESIGN.md` §4: posture, dominant activity, unit and relation, co-visibility, temporal
  structure, volume and homogeneity.
- **Compiled consequence.** A property the six lines produce rather than one the brief states:
  dominance, reading order, columns and their ratio, where density lives, what may repeat, the
  chrome that stays conventional. Recorded so it can be checked, never chosen directly.
- **Operator.** One of eight relationships a composition is written in: order, group, nest,
  align, juxtapose, attach, repeat, disclose. A candidate is a set of these over the content
  inventory, not a grid recipe.
- **Candidate.** A one-sentence description plus an ASCII wireframe of one composition that
  satisfies the constraints. Two or three are written; they must differ in the rendered
  partition (grouping, co-visibility, progression), not in column fractions.
- **Prior.** A named arrangement (Tidwell's, and the fifteen the reference already teaches)
  kept as activation evidence, invariants, forbidden moves, and a worked example — never a CSS
  block, never a ratio.
- **Chrome.** Logo, navigation, search, account, footer. Conventional by rule; familiarity is
  worth a measured 10% in search time and 23% in fixations (Todi 2018), and it is not where the
  brief's difference lives.
- **Instrument.** `docs/research/scripts/layout-topology.mjs`: renders a build, builds a block
  tree, detects repeated-sibling groups, reads resolved grid tracks, rasterises the first
  viewport, and emits a twelve-slot signature plus pairwise partition, raster, pq-gram and
  signature distances.

## Design

### Six composition lines, read off the brief

Two front ends, one grammar. A product surface is read as an *operational model* (actions,
prerequisites, state, evidence, context to retain); a narrative page as a *communicative model*
(the audience's question, the claim, its evidence, qualifications, alternatives, the commitment).
Both are then written in the same six lines and the same operators, and posture selects which
rules fire. Two grammars would re-create the category tell: "landing" would predict the scaffold
the way "console" predicts sidebar-stats-cards today.

| # | Line | Values | What in the brief decides it | What it drives | Checkable rules |
|---|---|---|---|---|---|
| 1 | **Posture** | workspace · transient · narrative | Cooper's attention × frequency: is the surface where long work happens, a bounded task, or an authored page read in the author's order | Which dialect fires; chrome share; page length; spatial vs linear reading | Workspace: the dominant region reaches the first viewport and holds ≥ 40% of it; chrome ≤ 15% of viewport height above it; desktop page ≤ 2 viewports unless an unbounded list scrolls inside its own region. Narrative: exactly one dominant band in the first viewport, then a stratified sequence in the author's order; no region topology repeats more than twice down the page. Transient: one column, no secondary pane, no card grid, the primary action in a fixed position; steps only when the task is long, complicated, and novel. |
| 2 | **Dominant activity** | monitor · find · browse · compare · operate · read · decide | The verb the first read serves, with its success condition (what answer, what completed action) | What dominates and leads; whether search or filter precedes results; whether alignment across units is mandatory; where the action sits | Monitor: the highest-decision-priority exception region is first in DOM order and top-left, in the first viewport, and no row of equal siblings sits above it. Find: the search or filter precedes results and shares the first viewport; results are a list or table, not cards. Browse: an overview of many units dominates; detail on demand or by drill. Compare: the compared units share one axis in one region (rows or columns of one table or grid), never separate cards. Operate: the editor or form is the stage, at least twice the width of anything beside it; no marketing band. Read: one measure of 45–75ch dominates; media may bleed; nothing competes beside it. Decide: proposition, then evidence, then the action, with the action reachable in the first viewport. |
| 3 | **Unit and relation** | unit: the brief's own noun · relation: sequence · hierarchy · matrix · network · spatial field · set (several may hold; name the one the first read acts on) | What the units are and how they relate — not a "primary object" enum, which mixes a record (a unit), a queue (a collection with an ordering), a map (a representation), and a canvas (a surface) | The form of the dominant region; the axis density accumulates along; what may repeat | Sequence: one visible ordering axis, the key first in the row. Hierarchy: containment by indentation or nesting, never nested cards. Matrix: a real table or grid, both axes labelled and sticky, never reflowed into cards. Network: node-link or adjacency dominates. Spatial field: the map or canvas holds ≥ 50% of the first viewport, the panel is subordinate and cross-highlights. Set: a grid of equals is earned, cells uniform, no false hero. |
| 4 | **Co-visibility** | none (one level) · peer panes (overview and detail together) · drill (into a screen, with a way back) · on demand (expand in place, sheet, popover) | What must be visible at once for the task to be done: a comparison, a reference while editing, a selection with its context | Column count; whether a side region is a detail pane, a supporting pane, or nothing; navigation depth; the collapse at narrower widths | Peer panes: two columns, list narrower than detail (ratio ≥ 1.5 : 1 either way), selection state visible, one pane at a time below the expanded width; selecting preserves queue, filter, and scroll. Drill: one pane, breadcrumb or back, no rail. On demand: the overview keeps its position when detail opens. None: no rail masquerading as detail — a rail is a named supporting pane with its own reason, or absent. |
| 5 | **Temporal structure** | static · historical · live · scheduled (the one that drives the layout; a live chart of history is *live*) | Whether the content moves while viewed, records a past, or plans against time | The freshness region; whether a time axis dominates; position stability; "now" marking | Live: a freshness mark per changing region; regions keep position across updates; the focused item does not move under the user. Historical: time runs left to right in the dominant region, range controls adjacent. Scheduled: a time × resource matrix or a day-grouped agenda with "now" marked. Static: no live badges, no "real-time" copy. Monitor on static content is a misread brief. |
| 6 | **Volume and homogeneity** | few (≤ 7) · many · unbounded × homogeneous · heterogeneous | How many units the surface holds and whether they share a schema; text-length and media shape where they change the unit's box | Whether repetition is legitimate; paging or overflow; sectioning; how much of the page a repeated group may take | Many homogeneous: one list, table, or grid of identical cells, ≥ 6 in view, paged or virtualised past the viewport. Few heterogeneous: titled sections with distinct topologies, never a card grid of unlike things. A repeated group of exactly three in three columns is three homogeneous peers *by the brief's own count*; three features, three benefits, or three plans are a sales device and need a stated reason. Fixtures at empty, one, typical, and high volume keep the required information reachable. |

**Compiled consequences, not lines.**

- **Dominance** — one dominant; one dominant with peers; all peers; two in tension — compiled
  from activity, relation, and volume. Monitor → the exception region; read → the document;
  browse a set → peers; decide with a claim and an artifact → two in tension. The brief may
  override with a stated reason ("the map is the product"). *Hero* is the narrative-posture name
  for the dominant region; its form (image, claim, artifact, sequence) follows from what the one
  thing is. Some pages have no hero; some have coequal regions. "What is the hero unit" is no
  longer a question the skill asks first.
- **Reading order** — the activity's first need, then the unit's ordering key, then chrome. The
  declared first-read region is first in DOM order and top-left in geometry.
- **Columns and ratio** — a felt ratio (≥ 1.5 : 1) when one region dominates; equal tracks when
  units are peers or must be compared; **never the 1.1–1.35 : 1 band**, which reads as centered
  that forgot to center and is what the old "asymmetric" prior actually produced. Unequal space
  follows unequal requirements; asymmetry is never a default.
- **Where density lives** — relation × activity: the matrix or list carries it; chrome and
  narrative bands do not.
- **What repeats** — volume × homogeneity, and nothing else.
- **Chrome** — stays conventional (logo, navigation, search, account, footer where the platform
  expects them). A sidebar needs ≥ 6 peer destinations or a drill model, stated; "console" is not
  a reason.

**Collapses to guard** (memo §2): primary object ≠ relation (record the noun, key on the
relation); monitor implies live or scheduled, and a monitor line on static content is a misread;
posture is recorded once and the stance's density constraint reads it; navigation depth is
co-visibility × volume, not a line; hero is dominance under narrative posture; sidebar is earned
by destination count and detail model, never by category.

### The operators and the constraint ledger

A candidate is written in eight operators over the content inventory: **order** (A before B),
**group** (A with B), **nest** (A inside B), **align** (A and B on one axis), **juxtapose** (A
beside B, in tension or as peers), **attach** (B follows A's selection), **repeat** (A × n),
**disclose** (B on demand from A). Before any candidate, the record carries a ledger, one row per
constraint: *brief evidence → interpreted relationship → layout constraint → rendered assertion
→ forbidden move*. The content inventory is held constant across candidates; a candidate that
shortens copy, drops fields, or invents a metric to fit a shape is discarded.

### The procedure

Replaces "how to pick":

1. **Read the six lines off the brief**, one reason each, with the front end that fits
   (operational or communicative). Record unknowns as unknown; do not invent volume, urgency,
   or peers.
2. **Compile the consequences**: dominance, reading order, columns, density placement,
   repetition, chrome. Name the defaults being overridden (three-up, stat row, sidebar,
   near-equal split, the headline band with an empty right half), the way the stance layer names
   the framework's radii and grays.
3. **Write the ledger.**
4. **Write two or three candidates** — a sentence and an ASCII wireframe each — starting from
   different priors or different dominance readings. They must differ in grouping, co-visibility,
   or progression; a 60 : 40 against a 50 : 50 is one candidate. Write one when only one fits,
   and say so.
5. **Choose by fit to the six lines**, then by familiarity and effort, and only then by
   distinctness; record the rejected candidates in one line each, beside the stance's rejected
   vector.
6. **Carry the chosen constraints into `DESIGN.md` §4** as checkable sentences, and build.

Output is prose and wireframes, not a schema: structured scaffolding measurably narrows what a
model produces (Yun 2025), and the six lines are sentences with reasons, as the nine stance lines
are.

### Priors

Every named arrangement the reference teaches survives as a prior: the activation evidence (which
line positions earn it), its invariants, its forbidden moves, and a worked example — never a CSS
block with a ratio in it. Exception-first is the prior for (workspace, monitor, live) and forbids
a row of equals above the exception region and an alert zone with no severity behind it. List
beside detail is the prior for peer panes and forbids three sticky columns and a detail that does
not follow selection. Grid of equals is the prior for (browse, set, many homogeneous) and forbids
itself when one tile matters more. Wizard is the prior for (transient, operate, a long, complicated,
novel task) and forbids itself for short forms and expert users. Center stage is the prior for
(operate or read, one unit) with its 2 : 1 rule. Hub and spoke is the prior for compact viewports
with many peer destinations. The asymmetric split is the prior for (narrative, decide, two in
tension) with its ratio stated as a rule and no snippet. Tidwell's canvas-plus-palette, two-panel
selector, and titled sections join them. Implementation techniques that carry no ratio — named
grid lines for an editorial bleed, a sticky buy-box, a table that scrolls horizontally instead of
reflowing into cards — stay as techniques, with placeholders where a track ratio would be.

### Imagery as first-class content

The survey found no hero images because single-file deliverables have no assets, and the empty
right half of the headline band is the shape that absence took. When the dominant region is an
artifact and no asset exists, the artifact is *drawn* — an SVG, a canvas-painted field, a real
diagram — as content, the way the wind farm drew its survey plate and the music player its
sleeve. A text-only band is not the default answer to "no image"; it is one candidate, earned when
the argument is verbal.

### Composition QA

Distinct from token QA. Six checks, mechanical where they can be:

1. **The canonical shape is absent unless earned, part by part.** For the surface's category, the
   parts of its default scaffold (workspace: stat row, main-plus-rail, sidebar; narrative: headline
   band with an empty right half, three-up, pricing trio, FAQ) are each present only with the line
   that earned them named in `DESIGN.md` §4. Checked with repeated-sibling detection, grid tracks,
   and the signature.
2. **Reading order agrees.** The declared first-read region is first in DOM order, top-left in
   geometry, and dominates the first viewport (share ≥ 0.4 for workspace; one band for narrative).
3. **Candidates differ on the page.** The written candidates, rendered as wireframe HTML,
   differ by first-viewport partition ≥ 0.20 — the local same-brief cross-tool range.
4. **No fingerprint.** No grid-track ratio, snippet, or section sequence byte-identical to a
   reference example without a recorded re-derivation; the 1.1–1.35 : 1 band is absent.
5. **The ledger neighbour.** The nearest build in the workspace ledger with a *different* relation
   model or activity sits at partition ≥ 0.15 and signature ≥ 0.25; a nearer one is the tell. A
   build with the *same* task shape may match — the same task shape is expected to look alike.
6. **Counterfactual assertions over distance.** For paired briefs, the required difference is
   declared before generation and asserted after — a comparison task's units are aligned on one
   axis; a monitor task's exception region leads. A distance alone never decides.

Each measure's blind spot is named (tree distance is blind to ratios, rasters to roles below the
fold, segmentation reaches F 0.70 against human 0.74); a fail on one is a reason to look, and the
human grid remains the referee.

### Files

| File | Change |
|---|---|
| `skills/designer/references/composition.md` | Rewrite the first half: the six lines, compiled consequences, collapses, operators and ledger, procedure, candidates, priors (fifteen existing plus Tidwell's), imagery as content. Keep "Imagery integration" and "Working from a supplied reference". Remove every literal track ratio. |
| `skills/designer/SKILL.md` | Step 1 reads the six composition lines beside the stance lines; step 6 replaces "favor intentional asymmetry … by default" with the dominance rule and the candidate step; step 8 adds composition QA; taste floor gains "unequal space follows unequal requirements". |
| `skills/designer/references/guidelines-authoring.md` | §4 records the six lines with reasons, the compiled consequences, the ledger, the chosen candidate and the rejected ones, the chrome kept conventional, the defaults overridden. |
| `skills/designer/references/qa-protocol.md` | Check 3 becomes composition QA with the six checks; "verify against own law" gains the layout clone check. |
| `skills/designer/references/taste-calibration.md` | Three flagged bands: the landing scaffold (headline band with an empty right half, three-up, pricing trio, FAQ), the almost-equal split (1.1–1.35 : 1), the sidebar by category. |
| `skills/designer/references/stances.md` | The library's "composition grammar" column stays; one sentence points at the composition lines. |
| `evals/evals.json` | Evals 10–12: the counterfactual pair and the landing-scaffold break. |
| `figma-design-workspace/derivation-eval/assert-composition.sh` | Runs the instrument on a build and checks 1, 2, 4 mechanically and 6 against a declared expectation. |
| `README.md`, `.claude-plugin/*.json` | Wording; version 2.1.0. |
| `docs/doperpowers/specs/2026-09-05-stance-derivation.md` | Revision note: the deferred item taken up here. |

## Acceptance

Builds under `figma-design-workspace/derivation-eval/` (briefs in `briefs.md` there), each a fresh
agent with only the brief and the skill. `node docs/research/scripts/layout-topology.mjs --out
<scratch> <builds…>` is the instrument; `assert-composition.sh` wraps it.

**C1 — Counterfactual pair, same domain, different task.** Brief E: "Design the maintenance
console for a regional bus operator's fleet: open defects by vehicle, overdue inspections, parts
on order, the workshop's day. High-trust, used all shift. Single HTML file." Brief F: "Design the
page where that same operator's fleet manager compares three tyre suppliers' quotes on the same
criteria — price per axle, lead time, warranty, on-site fitting — and picks one. Single HTML
file." Declared before building: E's dominant region is the exception region (defects, overdue),
first in DOM and top-left; F's compared units share one axis in one region (a table or grid with
supplier columns or rows), no supplier cards. `assert-composition.sh` passes both, and the pair's
first-viewport partition distance is ≥ 0.20.

**C2 — The landing scaffold, broken where it is not earned.** Brief L: "Design the public page
for a city's home-battery rebate program: who qualifies, what the rebate is worth, the one form to
apply, and the installers already approved. Single HTML file." Declared before building: the
communicative model is *eligibility → value → apply*, the dominant region is the eligibility
check or the value (not a slogan band), and any three-up is three homogeneous peers the brief
counts (it counts none). `assert-composition.sh` passes; no three-up, no pricing trio; an FAQ only
if `DESIGN.md` §4 names the line that earned it; the signature's hero slot is not the empty
headline band.

**C3 — Familiarity is preserved.** In C1, E's chrome (top bar, navigation, search) is
conventional, and `DESIGN.md` §4 states which prior E adopted and which line earned it. A console
whose task shape matches a prior looks like that prior; it is not marked down for it.

**C4 — No fingerprint.** `grep -rn "1.15fr\|0.85fr" skills/designer` returns nothing; no literal
`grid-template-columns` ratio remains in `composition.md`'s prior entries; the instrument reports
no track ratio in the 1.1–1.35 band in C1 or C2.

**C5 — Nothing else regressed.** Sampler tests and `claude plugin validate . --strict` pass; the
stance-derivation assert still passes on the pharmacy and wind-farm builds (the composition
change must not break the stance record).

**C6 — Human grid.** Screenshots of C1 and C2 beside the earlier pharmacy and wind-farm
builds in one review page.

## Decision Log

- Decision: Compile the brief into six composition lines, eight operators, and a ledger, then
  two or three candidates; keep the named arrangements as priors without CSS ratios.
  Rationale: three research rounds converged on "a compiler of relationships, not a classifier
  with more labels": Scout is the one measured result (declared structure bought +12–26%
  spatial diversity at non-significant quality change, professionals gained nothing), and the
  local measurement shows the reference's own snippet cloning across seven builds. Rejected:
  (a) a bigger menu keyed to more variables — "map + monitor → map-led" is a template with a
  longer key; (b) a JSON composition schema the agent fills — structured scaffolding narrows
  output (Yun 2025), so the grammar's output is prose and wireframes; (c) two grammars, one per
  page class — "landing" would predict the scaffold exactly as "console" predicts the rail today.
  Date/Author: 2026-09-05, Claude.

- Decision: Hero is a compiled consequence (dominance under narrative posture), and the
  "primary object" enum is replaced by the brief's own noun plus a relation model.
  Rationale: Both GPT rounds and the memo independently: making hero an input invites a
  dominant decorative region; "queue, timeline, map, canvas" mix a unit, a collection, a
  representation, and a surface, and a rule keyed on them decides the composition before
  deriving it. The relation is what the plane can act on (Bertin, Card & Mackinlay, Munzner).
  Date/Author: 2026-09-05, Claude.

- Decision: Chrome stays conventional; the grammar governs content topology only; asymmetry is
  never a default and the 1.1–1.35 : 1 band is forbidden.
  Rationale: familiarity is worth a measured 10% search time and 23% fixations (Todi 2018);
  Jakob's law; NN/g's zigzag study on decorative asymmetry; the local corpus shows the
  "asymmetric" prior produced near-equal splits in nine builds. `SKILL.md`'s "favor intentional
  asymmetry … by default" is replaced by "unequal space follows unequal requirements".
  Date/Author: 2026-09-05, Claude.

- Decision: Composition QA is a battery with named blind spots and counterfactual assertions,
  not a distance threshold; the same task shape is allowed to look alike.
  Rationale: every published layout-diversity measure reads a screenshot and scores two grids of
  different ratios as identical; no universal cutoff separates a clone from legitimate reuse; a
  distance cannot say whether a difference was warranted, an assertion declared before building
  can. Diversity is a tie-breaker after fit, familiarity, and effort. Rejected: a single diversity
  score; requiring every dashboard to be unique.
  Date/Author: 2026-09-05, Claude.

- Decision: Imagery is first-class content — an artifact with no asset is drawn.
  Rationale: the survey's most striking number (16 of 20 landing pages with an empty right half)
  is the shape of the missing image; two builds in the acceptance run drew their artifact and
  were the two that broke the pattern.
  Date/Author: 2026-09-05, Claude.

- Decision: Version 2.1.0.
  Rationale: additive to the 2.0.0 record (a §4 shape) without changing the stance contract.
  Date/Author: 2026-09-05, Claude.

## Surprises & Discoveries

- Observation: The reference's snippet is the layout-level `#D46B2C`.
  Evidence: `minmax(0,1.15fr) minmax(0,0.85fr)` in seven builds; its ratio the corpus mode; a
  no-skill build carries it too, so it is also a model default the snippet reinforced.

- Observation: Consoles did not converge on shape, only on chrome; landing pages converged on
  shape.
  Evidence: memo §0 and the signature survey. The two classes needed different diagnoses and the
  same fix.

- Observation: The pharmacy and wind-farm records both said "exception-first" while their units
  should have produced different dominant regions.
  Evidence: their `DESIGN.md` §4 text. The variable that separates them (a lot in a matrix, a
  turbine on a spatial field) was visible in the prose and had no rule to act through.

## Deferred

- **The settling experiment gains a layout arm**: the same briefs under the menu, under the
  grammar with one candidate, and under the grammar with candidates plus composition QA; human
  pairwise quality; partition and pq-gram distance as diversity; the six-line fit as the
  headline.
- **A layout ledger** beside the families-and-hues ledger: nearest-neighbour partition and
  signature distances against prior builds at derivation time.
- **Responsive and live-state composition**: the grammar compiles a desktop first viewport;
  breakpoint-specific constraints and update-stability behaviour are asserted by the existing
  QA checks but not compiled.
- **Rendered-candidate comparison** once a render path can be assumed.

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-09-05: created from the layout survey and three research rounds; direction approved by
  the user ("next would be the composition grammar").
