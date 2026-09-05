# Composition grammar: prior art, a ranked variable set, layout-difference measures, and risks

*Research memo, 2026-09-05. Source material for the `designer` plugin; never loaded at runtime.
Written for the decision to replace `references/composition.md`'s layout menu (five hero
archetypes, five dashboard arrangements, a "how to pick" keyed to hero unit and user's verb) with
a brief-derived composition grammar and a composition QA layer with a mechanical layout clone
check. Six parallel web-research tracks verified the sources below against primary pages; claims
a track could not open are marked "recalled, not verified". Section 0 is this repository's own
measurement. Section 5 lists claims in the 2026-09-05 stance memo that this round found wrong.*

## 0. What the current builds actually do

Before the prior art, a measurement. `docs/research/scripts/layout-topology.mjs` renders every
eval build under `figma-design-workspace/` (gitignored, local evidence) in Chromium at 1440 × 900,
decomposes each page into a block tree, classifies leaf regions by a coarse role, detects
repeated-sibling groups (card grids, stat rows, pricing trios, lists, tables), reads resolved grid
tracks, rasterises the first viewport, and computes pairwise distances between builds. Its output
is `docs/research/data/2026-09-05-layout-topology.json`. An earlier session's instrument
(`derivation-eval/layout-signature.mjs`, per-page signals without pairwise distances) was run
beside it as a cross-check. 51 builds: 17 consoles, 32 landing or marketing pages, 2 booking pages.

| Shape | Consoles (17) | Landing (32) | Cross-check (earlier tool) |
|---|---|---|---|
| Card grid of exactly three, three columns | 0 | **22** | feature trio 20 of 33 |
| Two or more card grids on the page | 0 | 15 | card grid 26 of 33 |
| Stat row (3–6 numeric siblings in one row) | 5 | 6 | relaxed stat row 5 of 18 |
| Two-track main-plus-rail grid, ratio 1.5–5 : 1 | **12** | — | right rail 5 of 18, table-like rows 13 of 18 |
| Table or list as the dominant first-viewport region | 11 | — | — |
| Full-width hero band in the first viewport | — | 14 | centered hero 18 of 33 |
| Split hero (two side-by-side regions in the top band) | — | 1 | — |

Three things follow.

**The reference's example CSS propagates verbatim, the way the accent hex did.** The asymmetric
split snippet in `composition.md` is `grid-template-columns: minmax(0,1.15fr) minmax(0,0.85fr)`,
a 1.35 : 1 ratio. That ratio is the single most common two-track ratio in the corpus (9 builds),
and the literal `1.15fr … 0.85fr` appears in 7 files: 6 skill-arm builds and 1 no-skill build.
The reference's own prose says the ratio "has to be *felt* (60/40 minimum)"; its snippet is
57/43. `repeat(3, …)` appears in 20 of 51 files, `repeat(auto-fit` in 13. The no-skill hit means
the ratio is also a model default that the snippet reinforces rather than overrides.

**The stance re-founding did not move layout.** Between each eval's with-skill and without-skill
build, first-viewport partition distance is 0.18–0.31 and signature distance 0.25–0.58; the mean
partition distance between *any* two builds in the corpus is 0.232. The skill arm is no farther
from the no-skill arm than unrelated builds are from each other, and it still carries the
canonical shapes: the kids-library skill build has seven card grids against an eval expectation of
"no template card-grid"; the hardware-store skill build has a pricing trio and two three-ups; the
rail-dispatch skill build has a stat row over a 2.44 : 1 main-plus-rail. Three different skills on
the same brief (the `comparison/` set) sit 0.18–0.35 apart on partition and as close as 0.17 on
signature — the Design Theater result reproduced locally.

**The records pick by name.** The pharmacy `DESIGN.md` reads "Exception-first over table-led. A
full-width exception queue is the page's one focal object; beneath it, an asymmetric two-column
body at `minmax(0,1fr) / clamp(324px,28%,430px)`"; the wind-farm one reads "a `1.5fr / 0.5fr`
split of plate and rail". Both cite the reference's pattern names as the choice, and both land the
same topology (dominant region plus right rail), which is what the reference's two questions
predict for any "fix problems" verb. The variables that should have separated them — the pharmacy's
unit is a lot in a table (a matrix), the wind farm's a turbine on a plate (a spatial field) — are
visible in the records' prose but had no rule to act through.

Instrument limits, so the numbers are read at the right weight: roles are coarse (a stack of
same-class sections reads as a "list"); the rail role wants a tall edge region, so rails built from
stacked panels are caught by the grid-track reading rather than the role (12 of 17 versus 1 of 17);
the twelve-slot signature is fine enough that 50 of 51 builds differ somewhere, so identity is the
wrong lens and prevalence is the right one. One unrelated pair has a byte-identical signature (the
hardware-store `impeccable` build and the meditation skill build), seven more differ in one slot.

*Addendum, same day, after the composition acceptance run.* The instrument gained four refinements
while measuring the acceptance builds (a visibility gate for closed `<details>` content, one
disclosed row allowed in a repeated group, hanging labels and footer groups marked; the spec's
Decision Log has each), and the corpus above was re-measured with it into
`data/2026-09-05-layout-topology-r2.json`, the original left as recorded. Six of the 51 signatures
move (two pages gain a first-viewport stat row that closed-details geometry had been hiding, one
loses a three-up, three change dominant role); the fractions the table reads from move by at most
two builds (stat row 7 → 9 of 51, three-up 23 → 22) and the mean pairwise partition distance goes
from 0.232 to 0.231. Nothing this section concludes depends on the difference.

## 1. Prior art: deriving layout from task and content

| Source | Variables read | Layout properties determined | Measured diversity or fit | Not covered |
|---|---|---|---|---|
| Swearngin et al. CHI 2020 (Scout) | Designer-declared grouping, repeat and alternate groups, order (fixed or varying, first or last), emphasis (high, normal, low), keep or prevent feedback | Arrangement, alignment axis, padding, element size, margin, columns, gutter, baseline grid, position; diversity by randomised assignment order plus a constraint forbidding each found layout | **Both.** N = 18 designers. Spatial diversity +12% within designer (F₁,₈₆ = 5.05, p < .027, d = .435), +26% across all designer pairs; non-professionals +35%, professionals −2% (interaction p < .038). Quality 5.37 vs 5.73 baseline, not significant | Mobile single screens; no semantic content or typography; "Scout required time for specifying elements … which may have left less time for refinement" |
| Dayama et al. CHI 2020 (GRIDS) | Element list with sizes and types, preferential placement, locked elements, designer-specified groups | Grid lines, positions, sizes, alignment, rectangularity, group contiguity | Ratings N = 13: optimal 72.12 vs sub-optimal 42.66 vs far 20.63; design study N = 16, 44.17% of suggestions incorporated. No diversity metric | "A designer would need to put effort to express groups via the tool"; "the optimisation system presently does not learn" |
| Todi et al. DIS 2016 (Sketchplore) | The sketch itself; importance values if given; task inferred | Position, size, alignment, colour, via clutter, visual search, Fitts, grid quality, colour harmony | Optimised menu faster (t(19) = 2.67); symmetry rated lower. No diversity metric | "These models do not allow us to deal with semantic aspects of layouts, such as naming or grouping of elements" |
| Todi et al. **IUI** 2018 (Familiarisation) | The user's browsing history: frequency, recency, per-feature spatial distributions | Repositioning toward the user's learned layout | Search time 2.8 → 2.5 s (t(663) = 5.3), fixations 3.4 → 2.6; ">10%" time, ">23%" fixations | Positions only; the authors name "unfamiliarisation or diversification of interfaces" as the inverse application |
| Oulasvirta et al. Proc. IEEE 2020 (survey) | Designer-supplied semantic association matrix δᵢⱼ (0–100), usage frequencies, element types and sizes | Positions, grid lines, grouping, menus | Survey. Names "multiple near-optimal solutions" as an open problem; rejects solver diversity ("only one decision variable … negligible for the end user") | "The lack of objective functions that capture essential aspects of human behavior" |
| Marks et al. SIGGRAPH 1997 (Design Galleries) | Input-parameter vector | n/a (graphics) | Dispersion measured on the **output** vector; "the output-vector parameters should be scaled so that they each have approximately the same dynamic range" or "the dispersion algorithm found a malicious way to get … spread in one of the vector coordinates" | Devising the output vector was "the most difficult task" |
| Lee et al. ECCV 2020 (Neural Design Network); Feng et al. NeurIPS 2023 (LayoutGPT); Lin et al. NeurIPS 2023 (LayoutPrompter) | Element categories and counts; pairwise relations (left, above, larger); saliency map; text | Bounding boxes | FID, mIoU, alignment, overlap, DocSim, constraint violation. Diversity not measured; LayoutGPT checks exemplar copying (278 of 423 scenes "true generation") | Boxes without hierarchy; the templates become in-context exemplars |
| Kumar et al. CHI 2011 (Bricolage) | Two page trees, ~30 node features | Content-to-region mapping with an edge cost c(e) = visual + ancestry + sibling terms, weights learned from 117 human mappings | Visual only 53% match to humans; + sibling 67%; + ancestry 75%; all 78%. Humans preserved sibling groups 83.9% of the time, ancestry 53.3% | Transfer, not generation |
| Cao, Jiang & Xia CHI 2025 (task-driven data model) | "The essential information entities, relationships, and data within information tasks" | UI specification from the data model | Abstract only; **recalled, not verified** beyond it | The closest direct precedent; mechanics unread |
| Tidwell, *Designing Interfaces* 3e (2019), ch. 2–4 | Content organisation (alphabetical, number, time, location, hierarchy, category or facet) × screen role (**Overview, Focus, Make, Do**); one thing vs many; task novelty and length; screen size | Application shell (Feature-Search-Browse, Streams and Feeds, Media Browser, Dashboard, Canvas Plus Palette, Wizard, Settings Editor, Alternative Views, Many Workspaces); navigational model (hub and spoke, fully connected, multilevel, step by step, pyramid, flat); region layout (Visual Framework, Center Stage, Grid of Equals, Titled Sections, Module Tabs, Accordion, Collapsible and Movable Panels) | Argued with examples; no measurement. Center Stage fixes a ratio: centre "at least twice as wide as whatever is in its side margins" | No rule computes a structure from a brief; 3e pattern bodies paywalled, "use when" quotes are 1e text |
| Van Duyne, Landay & Hong, *The Design of Sites* 2e | Site **genre** (12: e-commerce, news, community, government, nonprofit, grassroots, company, education, arts, web apps, intranets, blogs); organisation basis (hierarchical, task, alphabetical, chronological, popularity) | Genre routes to pattern sets; group I fixes page layout (grid, above the fold, clear first reads, fixed or expanding width, consistent sidebars) | Argued | Genre routes rather than dictates; no empirical test |
| Rosenfeld, Morville & Arango, *IA* 4e, ch. 6; Garrett, *Elements*; Apple HIG navigation | Whether content divides unambiguously (exact vs ambiguous schemes); structure (hierarchy, hypertext, relational database; Garrett adds matrix, organic, sequential); relation among destinations (nested, peer, continuous) | Navigation model; Apple: hierarchical ("one choice per screen"), flat ("switch between multiple content categories"), content-driven | Argued | Scheme sub-lists and Garrett's text recalled, not verified; NN/g publishes no such taxonomy |
| Cooper et al., *About Face* (postures) | Attention duration × frequency of use | Sovereign: "best used full-screen, monopolizing the user's attention for long periods", conservative, dense, small controls; transient: "a single, high-relief function", takes no more space than necessary, larger and brighter controls; daemonic; auxiliary | Argued (2.0 text verified; 4e wording not) | The strongest prior for deriving density from a task variable |
| Material 3 canonical layouts (Compose docs) | Content relation: list ↔ detail; primary ↔ supporting; equivalent items; × window size class | List-detail: two side-by-side panes at expanded, one at a time below; supporting pane: primary "about two thirds", support drops below or into a sheet at compact; feed: equivalent same-size elements in an adaptive grid | Platform-normative; no measurement | Which layout a brief implies; "the cleanest existing example" of relation × window class → layout |
| Wroblewski 2012 (multi-device patterns) | Column count and reflow tolerance | Mostly fluid, column drop, layout shifter, tiny tweaks, off canvas | Observational survey | No task variable |
| Bach et al. TVCG 2023 (Dashboard Design Patterns) | Descriptive coding of 144 dashboards | **Page layout: stratified 49%, grouped 33%, open 22%, table 19%, schematic 1%**; screenspace: parameterisation 52%, detail-on-demand 47%, screenfit 44%, multiple pages 42%, overflow 22%; structure: single 61%, hierarchical 19%, parallel 16%, open 8%; six genres (analytic 73%, static 21%, repository 17%, infographic 6%, embedded 4%, magazine 2%) | Frequencies; "none of these page layout patterns are exclusive and combinations are common"; a four-way trade-off (screenspace, abstraction, pages, interaction) | Patterns are "purely descriptive"; the only layout rules are three sentences ("stratification to put the most important information at the beginning"; table layouts "when multiple facets and similar/repeated information need to be shown"; analytic dashboards avoid overflow "since scrolling complicates comparing") |
| Sarikaya et al. TVCG 2019 | Purpose (strategic, tactical, operational; communication), audience, visual features, data semantics (alerting, benchmarks, updatable) | Almost none by design: "overview+detail" when strategic and operational combine | 83 dashboards, 15 factors, 7 clusters | Layout "left out for tractability" |
| Shneiderman 1996; Munzner 2014; Brehmer & Munzner 2013; Amar, Eagan & Stasko 2005 | Data type (1-D, 2-D, 3-D, temporal, multi-D, tree, network); dataset type (tables, networks and trees, fields, geometry); static vs dynamic; **search 2 × 2** (target known × location known → lookup, locate, browse, explore); query (identify, compare, summarize); ten low-level tasks incl. find anomalies, find extremum, sort, filter | "Overview first, zoom and filter, then details-on-demand"; overview "plus an adjoining detail view" | Typologies; none measures layout | All stop at the single view |
| Card & Mackinlay 1997; Bertin 1967/83 | Data type N, O, Q, QX, QXlon, **N×N**; Bertin's three levels and impositions (diagrams, networks, maps) | Plane usage within one view: N×N → X, Y, connection (node-link) or enclosure (treemap) | Formal, no study | Within one chart; Bertin recalled, not verified |
| Few, *Information Dashboard Design* | Importance, viewing sequence, exception status | "The top-left and center sections of the dashboard are the areas of greatest emphasis"; single screen; exceptions "reduce the data … to what is essential" | Assertion | No derivation; his fragmentation critique is about splitting across screens, not equal panels |
| Bendeck et al. 2023 (Tableau Public census, 25,620 dashboards) | None; measures artefacts | Adjacency graphs; 16 HDBSCAN clusters cover 59%, 41% unassignable; "like is often juxtaposed with like" | Counts; "the number you were hoping for does not exist": nobody has counted hero-plus-rail vs grid-of-tiles | — |
| Leiva et al. 2020 (Enrico); Deka et al. 2017 (Rico) | 20 design topics over 1,460 screens | — | Screenshot 75.8% top-1, **wireframe alone 39.4%**: structure carries about half the signal that topic predicts | Category predicts layout is the normal state; within-category variety is unmeasured |
| Goree et al. CHI 2021; Imteyaz et al. 2026 (Design Theater) | Screenshots over time (227,802 images, 10,482 sites); five tools × 24 tasks | Layout distance via tree edit distance (below) | Layout distance −44% 2010→2019 (abstract says "over 30%"); library Jaccard correlates 0.77 with visual similarity; Bootstrap "correlates strongly with decreased layout distance". Design Theater: layout index range 0.181–0.211 across tools | Between-tool or over-time only; **no one has measured layout diversity across briefs from one generator** |

What recurs. Nothing published compiles a brief into a layout; the nearest four are Tidwell's
organisation × screen-role cross, Material's relation × window-class rules, Cooper's
attention × frequency postures, and Card & Mackinlay's data-relation grammar within one view.
The optimisation family stops exactly where semantics begin (Sketchplore says so; GRIDS wants
groups declared; the Proc. IEEE survey encodes semantics as a hand-filled matrix). Scout is the one
study that measured what this decision hopes for, and its result is precise: declared structure
bought diversity without buying quality, and bought professionals nothing. Bricolage supplies an
empirical ranking of which constraints humans hold: sibling grouping (83.9%) over containment
(53.3%). Bach supplies the one corpus fact that argues against a menu: page layouts are
non-exclusive combinations of independent properties, and a menu of five would assign one name to
each dashboard, which the corpus says is wrong about half the time.

## 2. Recommended composition variables, ranked

Ranking weighs evidence, how much fit-relevant topology the variable buys, and how many layout
properties it drives. Six variables; two brief constraints the stance layer already reads
(viewport class, session length) are shared, not duplicated. Values are discrete and named, no
variable has an unlabelled default, and each record line carries a reason.

| # | Variable | Values | Layout properties driven | Checkable rules |
|---|---|---|---|---|
| 1 | **Posture** — what kind of surface this is | workspace (sovereign, long sessions, the surface is where the work happens) · transient (a bounded task: settings, a form, checkout, a dialog) · narrative (an authored page read in the author's order: landing, article, press kit, docs) | Which dialect of the rules below fires; screen occupancy; chrome share; page length; whether the reading model is spatial or linear; density placement (with the stance density constraint) | Workspace: the dominant region reaches the first viewport and holds ≥ 40% of it; nothing full-width sits above it except chrome ≤ 15% of viewport height; desktop page height ≤ 2 viewports unless an unbounded unit list scrolls inside its own region (Few's single screen; Bach's analytic dashboards avoid overflow). Narrative: exactly one dominant band in the first viewport carrying the proposition (Center Stage; Few's top-left and centre; NN/g 57% of viewing time above the fold), then a stratified sequence in authored order; no region topology repeats more than twice down the page. Transient: one column, no secondary pane, no card grid, the primary action in a fixed position; Iftikhar 2021's single-page form beat the wizard for expert users (SUS 76 vs 67), so steps need the Wizard's own condition (long, complicated, novel) |
| 2 | **Dominant activity** — the verb the first read serves | monitor (find anomalies over changing state) · find (a known target: lookup or locate) · browse (an unknown target among known kinds) · compare (several targets on one axis) · operate (edit, configure, create, transact the unit) · read (linear consumption) · decide (evaluate a proposition and act) | What dominates and what leads; reading order; whether a search or filter precedes results; whether alignment across units is mandatory; the action's position | Monitor: the freshest exception-bearing region is the first content region in DOM order and in top-left geometry, in the first viewport, and no group of equal-weight siblings (a stat row, a card row) sits above it; every region carries a freshness mark. Find: the search or filter control precedes the results region in reading order and shares its first viewport; results are a list or table, not cards (NN/g: cards hurt scanning of search results; Baymard: sidebar filters beat horizontal ones because the options stay visible). Browse: an overview of many homogeneous units dominates and detail is on demand or by drill. Compare: the compared units share one axis in one region (rows or columns of one table or grid), never separate cards of differing width (Bach's table layout; NN/g eyetracking on card comparison). Operate: the editor or form is Center Stage, at least twice the width of anything beside it; no marketing band. Read: one measure column of 45–75ch dominates, media may bleed, nothing competes at its side. Decide: proposition, proof, action, in that order, with the action reachable in the first viewport (Van Duyne's Up-Front Value Proposition). Zheng et al. 2018 is the empirical anchor: task changes what is salient (an input field 1.68× under form filling) |
| 3 | **Unit and relation model** — the unit named, and how units relate | unit: the brief's noun (lot, turbine, train, stop, book, tool, event, section) · relation: sequence (ordered by one key or by time) · hierarchy (containment) · matrix (two keys, e.g. time × resource) · network (links) · spatial field (position on a map or canvas) · set (unordered peers) | The form of the dominant region (list or timeline; tree or outline; table or schedule grid; graph; map or canvas; grid of equals); the axis along which density accumulates; what may repeat | Sequence: one ordering axis visible and stated, the ordering key first in the row. Hierarchy: containment shown by indentation or nesting, not by nested cards. Matrix: a real table or grid with both axes labelled and sticky, never reflowed into cards (existing rule). Network: node-link or adjacency dominates, degree visible. Spatial field: the map or canvas holds ≥ 50% of the first viewport and the panel is subordinate with cross-highlighting (Tidwell's Canvas Plus Palette; the existing map-led rule). Set: a grid of equals is earned, cells uniform, no false hero (Tidwell's Grid of Equals applies to "similar style and importance"; Material's feed to "equivalent content elements"). Prior art: Bertin's impositions, Card & Mackinlay's N×N and QX, Munzner's tables, networks, fields, geometry |
| 4 | **Overview-to-detail** — how a unit's detail is reached | none (one level) · peer panes (overview and detail side by side) · drill (into a screen, with a way back) · on demand (expand in place, sheet, popover) | Column count; whether a side region is a detail pane, a supporting pane, or nothing; navigation depth; the collapse at medium and compact widths | Peer panes: two columns, the list narrower than the detail (Material list-detail; Tidwell's Two-Panel Selector), ratio ≥ 1.5 : 1 or ≤ 1 : 1.5, selection state visible, one pane at a time below the expanded class. Drill: one pane, a breadcrumb or back, no rail. On demand: the overview keeps its position when detail opens. None: no rail masquerading as detail; a rail must be named as a supporting pane with its own reason (Material: primary "about two thirds") |
| 5 | **Temporal structure** — how the content moves | static · historical (a record over time) · live (changing while viewed) · scheduled (planned against time) | The freshness region; whether a time axis dominates; position stability; "now" marking; update information in chrome | Live: a "last updated" or per-region freshness mark (Bach: 64% of dashboards show update information); regions keep position across updates; exceptions surface (Few). Historical: time runs left-to-right in the dominant region with range controls adjacent. Scheduled: a time × resource matrix or a day-grouped agenda with "now" marked. Static: no live badges, no "real-time" copy. Monitor requires live or scheduled; a monitor verb on static content is a misread brief (Munzner's static vs dynamic) |
| 6 | **Volume and homogeneity** — how many units, and whether they are alike | few (≤ 7) · many (dozens) · unbounded (paged or virtualised) × homogeneous · heterogeneous | Whether repetition is legitimate; pagination or overflow (Bach's screenfit vs overflow); sectioning; how much of the page a repeated group may take | Many homogeneous: one list, table or grid of identical cells, ≥ 6 cells in view, paged or virtualised past the viewport. Few heterogeneous: Titled Sections with distinct topologies, never a card grid of unlike things (the SaaS card kit). A repeated-sibling group of exactly three in three columns must be three homogeneous peers by the brief's own count; three features, three benefits, or three plans are a sales device, not a set, and need a stated reason (§0: 22 of 32 landing builds carry one) |

Consequences, not variables:

- **Dominance structure** (one dominant; one dominant with peers; all peers; two in tension) is
  compiled from activity, relation, and volume. Monitor → the exception region dominates; read →
  the document; browse a set → peers; decide with a claim and an artifact → two in tension. The
  brief may override with a stated reason ("the map is the product"). This is the property the
  current "what is the hero unit" question was reaching for.
- **Hero** is the narrative-posture name for the dominant region; its *form* (full-bleed,
  split, typographic, object, stack) follows from what the one thing is (image, claim, artifact,
  sequence) and whether a second thing stands in tension. Not a variable. The five hero archetypes
  become priors keyed to those positions.
- **Sidebar versus top navigation** follows from posture (workspace), the count of peer
  destinations (≥ 6), and overview-to-detail (drill needs a way back; peer panes already spend a
  column). A sidebar is never a default of the console category.
- **Navigation depth** is overview-to-detail × volume. **Where density lives** is relation × activity
  (the matrix or list carries it; chrome and narrative bands do not). **What repeats** is volume ×
  homogeneity. **Grid and asymmetry** follow from dominance: a felt ratio (≥ 1.5 : 1) when one
  region dominates, equal tracks when units are peers, and never the 1.1–1.35 band that reads as
  "centered that forgot to center".
- **Reading order** is the activity's first need, then the unit's ordering key, then chrome: the
  declared first-read region must be first in DOM order and top-left in geometry.

Collapses to watch:

| Sounds distinct | What the evidence says | Rule that keeps them apart |
|---|---|---|
| Primary object and relation model | "Queue", "timeline", "map", "schedule", "catalogue" are nominal bundles of a unit, a relation and a volume; the relation is what the plane can act on (Bertin, Card & Mackinlay, Munzner) | Record the unit as the brief's noun; key the rules off the relation, as type tradition is the nominal value and criteria drive the stance layer |
| Dominant activity and temporal structure | Monitor implies live or scheduled; compare and read are usually static or historical | Temporal stays a line because a live status page can be *found* (a rider) rather than monitored (an operator); the check is that monitor never sits on static |
| Posture, activity, and session length | Cooper's posture is duration × frequency; the stance layer already reads session length for density | Posture is recorded once and the density constraint reads it; activity is still needed because two workspace surfaces (monitor vs compare) differ in what dominates |
| Overview-to-detail and navigation depth | Depth is a consequence of detail model × volume | Depth is not recorded; the collapse rule (one pane at a time below expanded) is |
| Volume and density | Volume decides where density accumulates and whether repetition is earned; density (the stance constraint) decides how tight it is | A dense stance on few heterogeneous units still forbids a card grid; a spacious stance on many homogeneous units still gets one list |
| Hero and dominance | The hero is dominance under narrative posture | One property, two names; the record uses "dominant region" everywhere |
| Sidebar and category | 12 of 17 local consoles carry main-plus-rail; the count of peer destinations and the detail model earn it, the word "console" does not | A sidebar needs ≥ 6 peer destinations or a drill model, stated |

**One grammar or two.** One grammar, with posture selecting the dialect. Landing pages and product
surfaces answer the same six questions; they differ in the answers (narrative × decide × sequence
of sections × none × static × few heterogeneous, against workspace × monitor × matrix × peer panes
× live × many homogeneous), and the rules that fire differ accordingly. Two grammars would
re-create the category tell: "landing" would predict the hero-split-three-cards stack the way
"console" predicts sidebar-stats-cards today. Cooper's postures and Tidwell's screen roles are the
precedent for one vocabulary spanning both; Bach's genres show the same descriptive axes covering
analytic dashboards and magazine pages alike.

**Named layouts stay, as priors.** Each of Tidwell's patterns and each of the current ten
arrangements becomes an entry with the variable position that earns it, its applicability sentence
in the author's words, its forbidden moves, and a worked example; never a CSS block. Exception-first
is the prior for (workspace, monitor, live) and forbids a row of equals above the exception region
and an alert zone with no severity behind it. Grid of Equals is the prior for (browse, set, many
homogeneous) and forbids itself "when one tile *is* more important". List-detail is the prior for
peer panes and forbids three sticky columns. Wizard is the prior for (transient, operate, a task
that is "long or complicated, and … novel for the user") and forbids itself for short forms and
expert users. Center Stage is the prior for (operate or read, one unit) with its 2 : 1 rule. Hub and
spoke is the prior for compact viewports with many peer destinations. The asymmetric split is the
prior for (narrative, decide, two in tension) with its ratio stated as a rule (felt, ≥ 1.5 : 1) and
no snippet, because §0 shows the snippet is what shipped.

**The procedure.** Read the six lines off the brief with a reason each. Compile the consequences
(dominance, reading order, columns, density placement, repetition, chrome). Write two or three
layout candidates as one-sentence descriptions with ASCII wireframes (Anthropic's public
frontend-design skill already asks for "ASCII wireframes to ideate and compare"; unevaluated, but
in-house precedent), each starting from a different prior or a different dominance reading.
Candidates must differ in the rendered partition, not in rule assignment (Marks 1997; the Proc.
IEEE survey's remark that one changed decision variable is "negligible for the end user"). Choose
by fit to the six lines, record the rejected candidates beside the rejected coordinate vector, and
carry the chosen constraints into `DESIGN.md` as checkable sentences.

## 3. Measuring that two layouts differ

Every published layout-diversity measure reads a screenshot, not the DOM: Goree's XY-tree (cut
along gutters and solid colours, then Zhang–Shasha tree edit distance with insertion cost = region
size and relabel cost = symmetric difference), Design Theater's element tree from OmniParser v2
with tree edit distance, Rico's 64-dimension autoencoder over a two-channel text/non-text raster of
leaf boxes, Miniukovich's and Reinecke's quadtree and X-Y cut features. The DOM and render-tree
measures are structural (Bricolage's learned tree matching, Webzeitgeist's 1,679-dimension node
descriptors, RTDM, MDR, DEPTA), and every one of them scores two grids with different track ratios
as identical, because geometry enters at most ordinally. No published work reads CSS tracks, and no
published work measures within-generator layout diversity across briefs. The clone check is new
territory, which is why it needs several measures with named blind spots.

| Measure | Input | Catches | Misses | Used by |
|---|---|---|---|---|
| Block tree (VIPS-style segmentation: split when ≥ 2 children are visibly large; pass through a single covering child; a repeated-sibling parent is one region) | DOM + computed geometry | The page's region topology at the level a designer means | Depends on thresholds; VIPS merges structurally similar neighbours (card rows collapse into one region, which is what detection wants); best algorithms reach F 0.70 against human agreement 0.74 (Kiesel 2020/21) | Cai et al. 2003; this repository's instrument |
| Tree edit distance / pq-grams over a role-labelled block tree | Block tree | Added, removed, re-nested regions; hero vs no hero as a node difference | Two grids of different ratios; a stat row vs a card row if labels are coarse; O(n²·depth²) for Zhang–Shasha, pq-grams approximate it linearly | Goree 2021, Design Theater 2026 (TED); Augsten et al. 2005 (pq-grams) |
| First-viewport partition distance (24 × 16 raster of region identity; fraction of cell adjacencies whose same-region relation differs) | Block tree | Geometric partition independent of labels: split vs stack, rail vs no rail, band heights | Below the fold; roles; two pages with the same partition and different content kinds | Rico's raster (as an embedding); this instrument |
| Role raster distance (same grid, role per cell) | Block tree + roles | Table where a chart was; media where a heading was | Geometry when roles agree | This instrument |
| Coarse signature (top nav; sidebar or rail; hero form; dominant role; dominance ratio; stat row; card grids; three-up; first-viewport region count; column count; page length) | Block tree, groups, grids | The named tells directly; prevalence counts across a corpus | Fine structure; 50 of 51 local builds differ somewhere, so use it for prevalence and nearest-neighbour, not identity | Earlier `layout-signature.mjs`; this instrument |
| Repeated-sibling detection (≥ 3 children of one parent sharing tag, classes and child count with near-uniform boxes; normalised edit distance < 0.3 in the original) | DOM + geometry | Card grids, stat rows, pricing trios, lists, tables, with count, columns and first-viewport membership | Repetition across non-siblings; whether the repetition is *earned* | MDR (Liu, Grossman & Zhai 2003: 99.8% recall on 46 pages); DEPTA 2005 |
| Grid-track ratios (resolved `grid-template-columns` of large grids) | Computed style | The 1.35 : 1 fingerprint; near-equal splits; main-plus-rail; equal tracks | Flex and float layouts; ratios that come from content width | No prior art; this instrument |
| Reading-order agreement (declared first-read region vs DOM order vs top-left geometry) | Block tree + the record | A first read that is not first; an exception region under a stat row | Whether the *declared* order is right; LayoutReader shows naive left-right-top-bottom order scores BLEU 0.70 against human order on documents, so geometry alone is not the referee | LayoutReader 2021 (documents); Faraday 2000's salience order is unvalidated and Still & Masciocchi 2018 found it "does a poor job predicting entry points" |
| Aesthetic and structure measures (Ngo's balance, sequence, density, regularity, economy, rhythm; AIM's 17; Miniukovich's grid quality) | Boxes or screenshot | Balance and quadrant weight | Topology: an equal-ink three-column grid and a hero column score alike; grid quality was the weakest term (r = −.22) in Miniukovich 2015; AIM reports no validation of its own | Ngo, Teo & Byrne 2003; Oulasvirta et al. 2018; Miniukovich & De Angeli 2015 |
| Screenshot embeddings (UIClip; CNN classifiers) | Screenshot | Holistic look; design-quality similarity | Uninterpretable as layout; Design Theater's visual index lives in a quality-tuned space | Goree 2021 (CNN), Design Theater (UIClip) |

The clone check that follows. (a) Prevalence, not identity: assert that the build's canonical
shape for its category (main-plus-rail with a stat row; hero, three-up, pricing, FAQ) is absent
unless the six lines earn each part, checking the parts with repeated-sibling detection, grid
tracks and the signature. (b) Reading order: the declared first-read region is first in DOM and
top-left, and dominates the first viewport (share ≥ 0.4 for workspace, one band for narrative).
(c) Candidates: the two or three written candidates, rendered as wireframe HTML or as the built
page's alternatives, differ by partition distance ≥ 0.20, which is the local same-brief cross-tool
range (0.18–0.35). (d) Ledger: the nearest build of a *different task shape* in the workspace
ledger sits at partition ≥ 0.15 and signature ≥ 0.25; a nearer neighbour with a different relation
model or activity is the tell, the way a shared accent hex is. (e) Fingerprints: no grid track
ratio or snippet byte-identical to a reference example unless re-derived with a reason. The
thresholds come from §0's corpus and should be re-read once the grammar has produced a dozen
builds; the same-constraint case (two live monitoring consoles both landing on a dominant region
plus rail) is expected and passes when their relation models differ in the dominant region's form.

## 4. Risks, and the mitigation for each

1. **Diversity without quality.** Scout is the direct analogue and its quality trended down (5.37
   vs 5.73, n.s.) while diversity rose, and professionals gained nothing. GRIDS found its optimiser
   "less useful as the layout became more well-defined". Rule: the grammar is a fit instrument;
   the composition QA scores fit to the six lines and reading order, never spread; the priors stay
   as the strong defaults a professional would reach for, and a candidate that departs from the
   prior needs a variable that earns the departure.
2. **Every dashboard unique.** Familiarity is worth a measured amount: Todi 2018 cut search time
   10% and fixations 23% by matching a user's learned layout; Roth 2010 (N = 652) found stable,
   genre-specific expectations for where objects sit; Tuch 2012 found prototypicality moves
   first-impression appeal strongly on clean pages (d ≈ 1.8–2.0) and barely on busy ones
   (d = .24); Jakob's Law. Rule: chrome placement (logo, navigation, search, sign-in) is not a
   composition variable and stays conventional; the grammar governs *content topology*; deviation
   from a prior is argued from a variable, not from a wish to differ. Silvennoinen 2025 is the
   counterweight: novelty predicted appeal more strongly than typicality on 12 sites, with genre
   moderating, so the cost of departure is findability, not appeal, and workspace posture weighs
   findability first.
3. **Asymmetry for its own sake.** NN/g's zigzag study found alternating image-text rows made users
   "stumble over" decorative images; Tuch 2010 found symmetry's aesthetic effect gender-moderated
   (recalled, not verified); Ngo's balance measures and Sketchplore's raters both reward symmetry.
   Rule: asymmetry only from dominance; equal tracks are correct for peers; the forbidden band is
   the almost-equal split (1.1–1.35 : 1), which §0 shows is what the "asymmetric" prior produced in
   nine builds. The existing skill line "favor intentional asymmetry over equal-width columns … by
   default" is replaced by the dominance rule.
4. **Good defaults are good.** Wizard, hub and spoke, list-detail and Center Stage exist because
   they work for their conditions, and Tidwell states the conditions; Iftikhar 2021 shows what
   happens when the condition is ignored (single page beat wizard for expert clinical staff).
   Rule: every prior carries its applicability sentence and its forbidden moves, and the grammar
   never deletes a prior by fiat; a prior is rejected in the record with the variable that rejects
   it.
5. **A structured intermediate suppresses variety.** Yun et al. 2025 found format scaffolding
   cut semantic diversity 10–40% and topic entropy 2.6× on text tasks; "output diversity is
   primarily governed by the presence or absence of structural tokens". Rule: the grammar's output
   is prose constraints and ASCII wireframes, not a JSON schema the agent fills; the six lines are
   sentences with reasons, as the nine stance lines are.
6. **Spread in rule space, sameness on the page.** Marks 1997's malicious dispersion; the Proc.
   IEEE survey's one-variable "solutions". Rule: candidates are compared on the rendered partition
   (§3 c), and the ledger disperses builds in output space (the stance spec's deferred ledger,
   extended to layout).
7. **Relocated fixation.** The grammar's own vocabulary becomes the attractor: every "monitor"
   lands on exception band over main-plus-rail at 2.5 : 1. Rule: the exception region's *form*
   comes from the relation model (a queue, a plate, a timeline, a schedule), so two monitor
   consoles differ where their units differ; the ledger check (§3 d) fires on a nearer neighbour
   with a different relation or activity; rejected candidates are recorded.
8. **Snippets clone.** The `1.15fr / 0.85fr` fingerprint in seven builds is the layout-level `#D46B2C`.
   Rule: the reference states ratios as rules and shows a snippet only as one worked
   instantiation labelled as such, with the ratio derived in the text beside it.
9. **The model's own defaults sit beneath the grammar.** The fingerprint also appeared in a
   no-skill build, and Goree attributes the web's layout convergence to library defaults
   (Bootstrap most of all). Rule: the grammar names the default it is overriding (three-up, stat
   row, sidebar, near-equal split) the way the stance layer names the framework's radii and grays.
10. **The instrument lies in known ways.** Tree edit distance is blind to ratios; screenshot
    measures are blind to the DOM; segmentation reaches F 0.70 against human 0.74; the signature
    is coarse; roles misfire on stacked same-class sections. Rule: the clone check is a battery
    (§3) with each measure's blind spot named, and a fail on any one is a reason to look, not a
    verdict; the human grid (the stance spec's A6) remains the referee.
11. **Evidence is thin where it matters most.** No study measures layout diversity across briefs
    from one generator; no study compares a layout-planning stage against direct generation on
    open-ended topology (every planning result — LaTCoder +66.67% TreeBLEU, DCGen +15% visual
    similarity — is fidelity to a given screenshot); GameUIAgent's schema ablation (quality 8.0 vs
    4.8 of 10) is game UI judged by a VLM. The settling experiment from the stance memo gains a
    layout arm: the same briefs under the menu and under the grammar, human pairwise quality,
    partition and tree distance as the diversity measures, and the six-line fit as the headline,
    because raw spread flatters the arm that ignores the brief.

## 5. Corrections to the 2026-09-05 stance memo

Found while verifying this round's sources; the spec's Revision Notes should carry them.

- Feng, Hélie & Panchal 2025 is multi-persona prompting (parallel, collective, sequential; about
  five concepts per persona) on product-design text, not "one design per conditioning vector".
- Fu et al. 2026 (rules vs examples) covers games, arithmetic and linguistic inference; it has no
  design artifact and no diversity metric.
- Verbalized Sampling (Zhang et al. 2025) tested no structured or visual output; its 1.6–2.1× is
  text-only.
- "Low complexity + high prototypicality most appealing" is Tuch et al. 2012, not Reinecke et al.
  2013; Reinecke measures colourfulness (R² = .78) and complexity (R² = .65) and mentions
  prototypicality once, in a citation.
- Goree et al. 2021: layout distance fell 44% from 2010 to 2019 in the results section (the abstract
  says "over 30%", the contributions list 43%), computed by tree edit distance on XY-trees from
  screenshots; the attribution is library convergence (Jaccard 0.77 with visual similarity), with
  Bootstrap the strongest single correlate.
- Design Theater's three indices are between-tool distances on the same prompt over unnormalised
  scales; "colour varied almost twofold while layout was nearly invariant" over-reads them. The
  paper contains no qualitative description of the recurring page shapes, and it forbade component
  libraries, which "may reduce variation across outputs".
- Venues: Familiarisation is IUI 2018; UMSI is UIST 2020; Misty is CHI 2025; LayoutGMN is Patil,
  Li, Fisher, Savva & Zhang, CVPR 2021 (Manandhar et al. ECCV 2020 is the baseline it beats).
- Tidwell 3e: chapter 4 is "Layout of Screen Elements" with eight patterns; Right/Left Aligned,
  Diagonal Balance, Responsive Disclosure and Liquid Layout are earlier-edition patterns; chapter 2
  renamed News Stream and Picture Manager to Streams and Feeds and Media Browser.
- NN/g publishes no hierarchical / sequential / matrix / network taxonomy; that is Garrett's and
  Lynch & Horton's. Few's fragmentation critique concerns splitting across screens, not equal
  panels. MDR's threshold is 0.3 normalised edit distance. "Bailey & O'Brien, Unraveling web
  design" does not exist; the layout-decline finding is Goree's.

## Sources

Constraint and optimisation: Swearngin et al. 2020 (Scout) https://arxiv.org/abs/2001.05424 · Dayama et al. 2020 (GRIDS) https://arxiv.org/abs/2001.02921 · Todi et al. 2016 (Sketchplore) https://www.kashyaptodi.com/data/SketchploreDIS2016.pdf · Todi et al. 2018 (Familiarisation) https://www.kashyaptodi.com/data/FamiliarisationIUI2018.pdf · Oulasvirta et al. 2020 (Proc. IEEE) https://doi.org/10.1109/JPROC.2020.2969687 · Marks et al. 1997 https://www.merl.com/publications/docs/TR97-14.pdf · Lee et al. 2020 (NDN) https://arxiv.org/abs/1912.09421 · Feng et al. 2023 (LayoutGPT) https://arxiv.org/abs/2305.15393 · Lin et al. 2023 (LayoutPrompter) https://arxiv.org/abs/2311.06495 · Kumar et al. 2011 (Bricolage) https://hci.stanford.edu/publications/2011/Bricolage/Bricolage-CHI2011.pdf · Cao, Jiang & Xia 2025 https://arxiv.org/abs/2503.04084 · UI grammar position paper https://arxiv.org/abs/2310.15455

Pattern languages and platforms: Tidwell, Brewer & Valencia 2019, *Designing Interfaces* 3e (O'Reilly; 1e pattern text via designinginterfaces.com Wayback captures) · Van Duyne, Landay & Hong 2006, *The Design of Sites* 2e, ch. A–I · Rosenfeld, Morville & Arango 2015, *IA* 4e, ch. 6 · Garrett 2010, *Elements* (recalled) · Cooper et al., *About Face* 2.0 text https://flylib.com/books/en/2.153.1.43/1/ · Apple HIG navigation (2022 capture) https://developer.apple.com/design/human-interface-guidelines/ · Material canonical layouts https://developer.android.com/develop/ui/compose/layouts/adaptive/canonical-layouts · Wroblewski 2012 https://www.lukew.com/ff/entry.asp?1514 · Jakob's Law https://www.nngroup.com/videos/jakobs-law-internet-ux/ · Anthropic frontend-design skill https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md

Dashboards and visualization tasks: Bach et al. 2022 https://arxiv.org/abs/2205.00757 and https://dashboarddesignpatterns.github.io/patterns.html · Sarikaya et al. 2019 https://alper.datav.is/assets/publications/dashboards/dashboards-preprint.pdf · Shneiderman 1996 https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf · Munzner 2014 (author slides) https://www.cs.ubc.ca/~tmm/talks/vad/VAD-2021.pdf · Brehmer & Munzner 2013 https://www.cs.ubc.ca/labs/imager/tr/2013/MultiLevelTaskTypology/brehmer_infovis13.pdf · Amar, Eagan & Stasko 2005 https://faculty.cc.gatech.edu/~stasko/papers/infovis05.pdf · Card & Mackinlay 1997 https://hci.ucsd.edu/hollan/infovis_design_space.pdf · Few 2006/2013, *Information Dashboard Design*; https://www.perceptualedge.com/articles/Whitepapers/Common_Pitfalls.pdf · Bendeck et al. 2023 (Tableau Public census) https://arxiv.org/abs/2306.16513 · Lin et al. 2022 (DMiner) https://arxiv.org/abs/2209.01599 · Wexler, Shaffer & Cotgreave 2017 (recalled)

Measurement: Goree et al. 2021 https://aux.engineering.ucsc.edu/publications/Goree_Doosti_Crandall_Su-HomogenizationWebDesign-CHI21.pdf · Imteyaz et al. 2026 (Design Theater) https://arxiv.org/abs/2607.22928 · Kumar et al. 2013 (Webzeitgeist) http://vis.stanford.edu/files/2013-Webzeitgeist-CHI.pdf · Ivory, Sinha & Hearst 2001 https://webtango.berkeley.edu/papers/chi2001/chi2001.pdf · Ivory & Hearst 2002 https://bailando.berkeley.edu/papers/chi2002.pdf · Ivory & Megraw 2005 https://doi.org/10.1145/1114571.1114572 · Gibson, Punera & Tomkins 2005 https://doi.org/10.1145/1060745.1060792 · Deka et al. 2017 (Rico) https://doi.org/10.1145/3126594.3126651 · Leiva, Hota & Oulasvirta 2020 (Enrico) https://userinterfaces.aalto.fi/enrico/ · Li et al. 2021 (Screen2Vec) https://arxiv.org/abs/2101.11103 · Patil et al. 2021 (LayoutGMN) https://arxiv.org/abs/2012.06547 · Kikuchi et al. 2021 https://arxiv.org/abs/2108.00871 · Patil et al. 2020 (READ, DocSim) https://arxiv.org/abs/1909.00302 · Cai et al. 2003 (VIPS) MSR-TR-2003-79 · Kiesel et al. 2020 https://doi.org/10.1145/3340531.3412782 · Kiesel et al. 2021 https://doi.org/10.1007/978-3-030-72113-8_5 · Liu, Grossman & Zhai 2003 (MDR) https://doi.org/10.1145/956750.956826 · Zhai & Liu 2005 (DEPTA) https://doi.org/10.1145/1060745.1060761 · Zhang & Shasha 1989 https://doi.org/10.1137/0218082 · Reis et al. 2004 (RTDM) https://doi.org/10.1145/988672.988740 · Augsten, Böhlen & Gamper 2005 (pq-grams) VLDB · Ngo, Teo & Byrne 2003 https://doi.org/10.1016/S0020-0255(02)00404-8 · Oulasvirta et al. 2018 (AIM) https://doi.org/10.1145/3170427.3186470 · Miniukovich & De Angeli 2015 https://doi.org/10.1145/2702123.2702575 · Reinecke et al. 2013 https://www.eecs.harvard.edu/~kgajos/papers/2013/reinecke13aesthetics.pdf · Wang et al. 2021 (LayoutReader) https://arxiv.org/abs/2108.11591 · Wu et al. 2024 (UIClip) https://arxiv.org/abs/2404.12500 · Duan et al. 2024 (UICrit) https://arxiv.org/abs/2407.08850

Attention, familiarity, and templates: Faraday 2000 (Wayback) http://web.archive.org/web/20110126212352/http://facweb.cs.depaul.edu:80/cmiller/faraday/Faraday.htm · Still & Masciocchi 2018 https://doi.org/10.1016/j.chb.2018.03.014 · Shen & Zhao 2014 https://doi.org/10.1007/978-3-319-10584-0_3 · Zheng et al. 2018 (task-driven webpage saliency) ECCV https://openaccess.thecvf.com/ · Fosco et al. 2020 (UMSI) https://arxiv.org/abs/2008.02912 · Nielsen 2006 and Pernice 2017 (F-pattern) https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/ · Fessenden 2018 https://www.nngroup.com/articles/scrolling-and-attention/ · NN/g zigzag layouts https://www.nngroup.com/articles/zigzag-page-layout/ · NN/g cards https://www.nngroup.com/articles/cards-component/ · Baymard product list UX https://baymard.com/research/ecommerce-product-lists · Djamasbi, Siegel & Tullis 2010 https://doi.org/10.1016/j.ijhcs.2009.12.006 · Bauerly & Liu 2006 (recalled) https://doi.org/10.1016/j.ijhcs.2006.03.002 · Tuch, Bargas-Avila & Opwis 2010 (recalled) https://doi.org/10.1016/j.chb.2010.06.016 · Tuch et al. 2012 https://research.google.com/pubs/archive/38315.pdf · Roth et al. 2010 https://doi.org/10.1016/j.intcom.2009.10.004 · Roth et al. 2013 (numbers unverified) https://doi.org/10.1016/j.ijhcs.2012.09.001 · Bernard 2001/2002 (recalled) · Iftikhar et al. 2021 https://pmc.ncbi.nlm.nih.gov/articles/PMC8190652/ · Silvennoinen, Kotkajuuri & Kujala 2025 IJHCI (open access via JYX)

LLM-era generation and diversity: Chen, Shi & Chen 2025 (SpecifyUI) https://arxiv.org/abs/2509.07334 · Suh et al. 2024 (Luminate) https://arxiv.org/abs/2310.12953 · Lu et al. 2025 (Misty) https://arxiv.org/abs/2409.13900 · LaTCoder 2025 https://arxiv.org/abs/2508.03560 · DCGen 2024 https://arxiv.org/abs/2406.16386 · Si et al. 2024 (Design2Code) https://arxiv.org/abs/2403.03163 · Sketch2Code https://arxiv.org/abs/2410.16232 · Prototype2Code https://arxiv.org/abs/2405.04975 · WebGen-V https://arxiv.org/abs/2510.15306 · UICoder https://arxiv.org/abs/2406.07739 · UI-Bench https://arxiv.org/abs/2508.20410 · ArtifactsBench https://arxiv.org/abs/2507.04952 · FullFront https://arxiv.org/abs/2505.17399 · GameUIAgent 2026 https://arxiv.org/abs/2603.14724 · Semantic-guidance UI generation 2026 https://arxiv.org/abs/2601.19171 · Shin et al. 2026 (vibe-coding homogenization taxonomy) https://arxiv.org/abs/2603.13036 · Yun et al. 2025 https://arxiv.org/abs/2505.18949 · Zhang et al. 2025 (Verbalized Sampling) https://arxiv.org/abs/2510.01171 · Zhang, Xin & Zhong 2026 https://arxiv.org/abs/2606.10302 · Feng, Hélie & Panchal 2025 https://doi.org/10.1017/dsj.2025.10037 · Fu et al. 2026 https://arxiv.org/abs/2609.03213
