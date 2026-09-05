# Composition

Composition is the page's region topology: what regions exist, which one dominates, how they are grouped, ordered, aligned, attached, repeated, and disclosed. It is derived from the brief's task and content, not selected from a menu of named layouts — the named layouts survive here as priors, each carrying the line positions that earn it, its invariants, and its forbidden moves. Composition is distinct from the stance, which is the visual system (`references/stances.md`), and from chrome — logo, navigation, search, account, footer — which stays conventional because familiarity is worth more there than difference. Use this file at three points in the workflow. The six composition lines are read off the brief at parse time, beside the stance lines. The candidates are written and chosen at step 6, "work information architecture and composition", before real content is written into the layout (`references/voice-copy.md`). Imagery is integrated into the chosen composition after that: the second half of this file covers photographic and drawn imagery, treatment, and what to do when a reference image is supplied.

## The six composition lines

Two front ends, one grammar. A product surface is read as an **operational model** — the actions available, their prerequisites, the state that must stay visible, the evidence behind a decision, the context that has to be retained while acting. A narrative page is read as a **communicative model** — the audience's question, the claim being made, the evidence for it, the qualifications, the alternatives, the commitment being asked for. Both are then written in the same six lines and the same operators, and posture selects which rules fire. Two grammars would rebuild the category tell: "landing" would predict the headline band and the three-up the way "console" predicts sidebar, stat row, and cards.

Each line is recorded in `DESIGN.md` §4 as a sentence with its reason. An unknown is recorded as unknown and resolved by writing candidates that differ on it; volume, urgency, and peers are never invented to fill a line.

| # | Line | Values | What in the brief decides it | What it drives | Checkable rules |
|---|---|---|---|---|---|
| 1 | **Posture** | workspace · transient · narrative | Attention duration crossed with frequency: is this the surface where long work happens, a bounded task passed through once, or an authored page read in the author's order | Which dialect of the rules below fires; chrome share; page length; whether reading is spatial or linear | Workspace: the dominant region reaches the first viewport and holds ≥ 40% of it; chrome ≤ 15% of viewport height above it; desktop page ≤ 2 viewports unless an unbounded list scrolls inside its own region. Narrative: exactly one dominant band in the first viewport, then a stratified sequence in the author's order; no region topology repeats more than twice down the page. Transient — a bounded task passed through once: a form, settings, checkout — one column, no secondary pane, no card grid, the primary action in a fixed position; steps only when the task is long, complicated, and novel. |
| 2 | **Dominant activity** | monitor · find · browse · compare · operate · read · decide | The verb the first read serves, with its success condition — which answer, which completed action | What dominates and what leads; whether search or filter precedes results; whether alignment across units is mandatory; where the action sits | Monitor: the highest-priority exception region is first in DOM order and top-left, in the first viewport, and no row of equal siblings sits above it. Find: the search or filter precedes results and shares the first viewport; results are a list or table, not cards. Browse: an overview of many units dominates, detail on demand or by drill. Compare: the compared units share one axis in one region — rows or columns of one table or grid — never separate cards. Operate: the editor or form is the stage, at least twice the width of anything beside it, and no marketing band sits above it. Read: one measure of 45–75ch dominates, media may bleed, nothing competes beside it. Decide: proposition, then evidence, then the action, with the action reachable in the first viewport. |
| 3 | **Unit and relation** | unit: the brief's own noun · relation: sequence · hierarchy · matrix · network · spatial field · set (several may hold; name the one the first read acts on) | What the units are and how they relate to each other. Not a "primary object" enum — "queue", "map", "canvas" bundle a unit, a collection, a representation, and a surface, and deciding on the bundle decides the composition before deriving it | The form of the dominant region; the axis density accumulates along; what may repeat | Sequence: one visible ordering axis, the ordering key first in the row. Hierarchy: containment by indentation or nesting, never by nested cards. Matrix: a real table or grid, both axes labelled and sticky, never reflowed into cards. Network: node-link or adjacency dominates and degree is visible. Spatial field: the map or canvas holds ≥ 50% of the first viewport, the panel is subordinate and cross-highlights. Set: a grid of equals is earned, cells uniform, no false hero. |
| 4 | **Co-visibility** | none (one level) · peer panes (overview and detail together) · drill (into a screen, with a way back) · on demand (expand in place, sheet, popover) | What must be visible at once for the task to be done — a comparison, a reference held while editing, a selection with its context | Column count; whether a side region is a detail pane, a supporting pane, or nothing; navigation depth; the collapse at narrower widths | Peer panes: two columns, the list narrower than the detail at a felt ratio of at least 1.5 : 1, selection state visible, one pane at a time below the expanded width, and selecting preserves queue, filter, and scroll. Drill: one pane, a breadcrumb or back, no rail. On demand: the overview keeps its position when detail opens. None: no rail masquerading as a detail pane — a rail is a named supporting pane with its own reason, or it is absent. |
| 5 | **Temporal structure** | static · historical · live · scheduled (the one that drives the layout; a live chart of history is *live*) | Whether the content moves while it is being viewed, records a past, or plans against a future | The freshness region; whether a time axis dominates; position stability; how "now" is marked | Live: a freshness mark per changing region; regions keep position across updates; the focused item does not move under the user. Historical: time runs left to right in the dominant region with range controls adjacent. Scheduled: a time-by-resource matrix or a day-grouped agenda with "now" marked. Static: no live badges and no "real-time" copy. A monitor activity on static content is a misread brief. |
| 6 | **Volume and homogeneity** | few (≤ 7) · many · unbounded × homogeneous · heterogeneous | How many units the surface holds and whether they share a schema; text length and media shape count here, because they change the unit's box | Whether repetition is legitimate; paging or overflow; sectioning; how much of the page a repeated group may take | Many homogeneous: one list, table, or grid of identical cells, ≥ 6 in view, paged or virtualised past the viewport. Few heterogeneous: titled sections with distinct topologies, never a card grid of unlike things. A repeated group of exactly three in three columns is three homogeneous peers *by the brief's own count*; three features, three benefits, or three plans are a sales device and need a stated reason. Fixtures at empty, one, typical, and high volume keep the required information reachable. |

## Compiled consequences

These are produced by the six lines rather than chosen. Record them so they can be checked; never pick one directly and reason backwards.

- **Dominance** — one dominant; one dominant with peers; all peers; two in tension — compiles from activity, relation, and volume. Monitor gives the exception region; read gives the document; browsing a set gives peers; deciding between a claim and an artifact gives two in tension. The brief may override with a stated reason ("the map is the product"). *Hero* is the narrative-posture name for the dominant region, and its form — image, claim, artifact, sequence — follows from what the one thing is. Some pages have no hero and some have coequal regions, so "what is the hero unit" is not a question this file asks first.
- **Reading order** — the activity's first need, then the unit's ordering key, then chrome. The region declared as the first read is first in DOM order and top-left in geometry.
- **Columns and ratio** — a felt ratio, at least 1.5 : 1, when one region dominates; equal tracks when units are peers or must be compared; **never the 1.1–1.35 : 1 band**, which reads as centered that forgot to center and is what an "asymmetric" instruction actually produces when nothing derives the number. Unequal space follows unequal requirements. Asymmetry is never a default, and a ratio is never carried over from an example. A supplied reference's or an adopted design system's geometry has authority over this rule: its ratio is reproduced and recorded as *adopted from <source>*, not derived, unless the brief asked for a redesign.
- **Where density lives** — relation crossed with activity. The matrix or the list carries the density; chrome and narrative bands do not.
- **What repeats** — volume crossed with homogeneity, and nothing else.
- **Chrome** — conventional. Logo, navigation, search, account, and footer sit where the platform puts them; that familiarity is measurable and it is not where the brief's difference lives. A sidebar needs at least 6 peer destinations or a drill model, stated. "Console" is not a reason.

Six pairs sound like separate decisions and are not. Keeping them apart is what stops the record from re-deciding the same thing twice under two names.

| Sounds distinct | What is actually going on | The rule that keeps them apart |
|---|---|---|
| Primary object and relation | "Queue", "timeline", "map", "schedule", "catalogue" are nominal bundles; the relation is the part the plane can act on | Record the unit as the brief's own noun and key every rule off the relation |
| Activity and temporal structure | Monitor implies live or scheduled; compare and read are usually static or historical | Temporal stays its own line, because a live status page can be *found* by a rider rather than monitored by an operator; the check is that monitor never sits on static |
| Posture and session length | Posture is attention crossed with frequency, and the stance layer already reads session length for density | Posture is recorded once and the stance's density constraint reads it; activity is still needed, because two workspace surfaces differ in what dominates |
| Co-visibility and navigation depth | Depth is a consequence of the detail model crossed with volume | Depth is not recorded; the collapse rule — one pane at a time below the expanded width — is |
| Volume and density | Volume decides where density accumulates and whether repetition is earned; the stance's density decides how tight it is | A dense stance on few heterogeneous units still forbids a card grid; a spacious stance on many homogeneous units still gets one list |
| Hero and dominance | The hero is dominance under narrative posture | One property, two names; the record says "dominant region" everywhere |
| Sidebar and category | The count of peer destinations and the detail model earn a sidebar | A sidebar needs ≥ 6 peer destinations or a drill model, stated; the word "console" earns nothing |

## The operators and the ledger

A candidate composition is written in eight operators over the content inventory, not as a grid recipe.

- **order** — A before B.
- **group** — A with B.
- **nest** — A inside B.
- **align** — A and B on one axis.
- **juxtapose** — A beside B, in tension or as peers.
- **attach** — B follows A's selection.
- **repeat** — A × n.
- **disclose** — B on demand from A.

Before any candidate, write the ledger: one row per constraint, in the shape *brief evidence → interpreted relationship → layout constraint → rendered assertion → forbidden move*. The rendered assertion is the sentence someone can check against the built page; the forbidden move is the default it displaces. The content inventory is held constant across candidates — a candidate that shortens copy, drops fields, or invents a metric in order to fit a shape is discarded, not admired.

## The procedure

1. **Read the six lines off the brief**, one reason each, through the front end that fits — operational for a product surface, communicative for a narrative page. Record unknowns as unknown.
2. **Compile the consequences**: dominance, reading order, columns, where density lives, what repeats, what chrome stays conventional. Name the defaults being overridden — the three-up, the stat row, the sidebar, the near-equal split, the headline band with an empty right half — the way the stance layer names the framework's radii and grays. A default that is not named stays in place and shows through.
3. **Write the ledger.**
4. **Write two or three candidates**, a sentence and an ASCII wireframe each, starting from different priors or different dominance readings. They must differ in grouping, co-visibility, or progression; a 60 : 40 against a 50 : 50 is one candidate wearing two hats. Write one when only one fits, and say so.
5. **Choose by fit to the six lines**, then by familiarity and effort, and only then by distinctness. Record the rejected candidates in one line each, beside the stance's rejected coordinate vector.
6. **Carry the chosen constraints into `DESIGN.md` §4** as checkable sentences, and build.

The output of this procedure is prose and ASCII wireframes, not a filled-in schema. The six lines are sentences with reasons, as the nine stance lines are; a structured form to complete narrows what gets produced, which is the opposite of the point.

### One worked pass

**Brief.** "A regional bus operator's fleet maintenance console — about 180 vehicles; drivers report defects through the shift and parts arrive during it — open defects by vehicle, overdue inspections, parts on order, the workshop's day. Used all shift, single HTML file."

**The six lines.**

1. Posture: **workspace** — one controller has this open for a whole shift and works out of it; it is where the work happens, not a report about the work.
2. Activity: **monitor** — the first read answers "what needs a decision before this shift ends", and the success condition is every overdue inspection and vehicle-off-road defect assigned to a bay or deferred with a reason.
3. Unit and relation: the unit is the **vehicle**; the relation the first read acts on is a **matrix** — vehicle against defect state and inspection due date. The workshop's day is a second matrix, bays against hours, and it is subordinate.
4. Co-visibility: **unknown**. The brief does not say whether a defect's history has to stay visible while the next one is read. The two candidates differ on exactly this.
5. Temporal: **live** — the brief says defect reports come in from drivers and parts arrive during the shift.
6. Volume and homogeneity: **many homogeneous** — the brief's roughly 180 vehicles share one defect schema; the workshop's day is few heterogeneous inside its own region.

**Three ledger rows.**

| Brief evidence | Interpreted relationship | Layout constraint | Rendered assertion | Forbidden move |
|---|---|---|---|---|
| "overdue inspections" | An exception set ordered by how far past due, against a legal deadline | The exception region leads | It is the first content region in DOM order, top-left, and holds ≥ 40% of the first viewport | A stat row of fleet totals above it |
| "open defects by vehicle" | A matrix: vehicle against defect state | A real table, both axes labelled | Sticky header and sticky vehicle column; overflow scrolls horizontally inside the table's own container | One card per vehicle |
| "the workshop's day" | Bays against hours, with a present moment | A scheduled region with "now" marked, subordinate to the exception region | The day grid marks now and keeps its position across live updates | A utilisation donut standing in for the day |

**Candidate A — peer panes.** The exception queue leads, with a permanent detail pane attached to the selected defect.

```text
+- chrome: fleet · search · shift ---------------------------+
+---------------------------------------+-------------------+
| NEEDS A DECISION THIS SHIFT   14:20    | VEHICLE 4471      |
|  6 overdue inspections · 4 VOR         |  defect history   |
|  4471 · 3 days over · brake test    >  |  parts on order   |
|  2210 · 1 day over  · tacho         >  |  next inspection  |
|  1806 · VOR         · door seal     >  |  assign to bay    |
+---------------------------------------+                   |
| OPEN DEFECTS BY VEHICLE  180 rows      |                   |
|  sticky header + vehicle column        |                   |
+---------------------------------------+-------------------+
| THE WORKSHOP'S DAY   bays x hours, now line at 14:20       |
+------------------------------------------------------------+
```

**Candidate B — disclosure in place.** The same queue leads, and a row expands where it sits; the width the detail pane would have taken goes to the defect table and to parts.

```text
+- chrome: fleet · search · shift ---------------------------+
| NEEDS A DECISION THIS SHIFT                    14:20       |
|  6 overdue inspections · 4 VOR                             |
|  4471 · 3 days over · brake test · bay 2        [ open ]   |
|   > history · parts on order · assign · defer with reason  |
|  2210 · 1 day over  · tacho calibration         [ open ]   |
+------------------------------------------------------------+
| OPEN DEFECTS BY VEHICLE   filter: depot · status · age     |
|  full-width table, sticky header + vehicle column          |
+-----------------------------------------+------------------+
| THE WORKSHOP'S DAY  bays x hours, now    | PARTS DUE TODAY  |
+-----------------------------------------+------------------+
```

**Chosen: B**, because nothing in the brief asks for two defects to be readable at once. The controller disposes of the queue one item at a time, so a permanent detail pane spends a third of the width on a region that is empty until something is selected, and it shrinks the defect table that the second read actually works in. Peer panes is the right prior when the task is comparison or reference held while editing; this task is disposition. A recorded in the rejected line: "peer panes, rejected — no line asked for co-visibility, and the empty pane costs the table its width."

## Priors

Every named arrangement survives as a prior: the activation evidence — which line positions earn it — its invariants, its forbidden moves, and a worked example. Never a CSS block with a ratio in it. A prior is the strong default a working designer would reach for at that position, so departing from one needs a line that earns the departure, and rejecting one is recorded with the line that rejects it.

| Prior | Earned by | Invariants | Forbidden moves | Worked example |
|---|---|---|---|---|
| **Exception-first** | workspace, monitor, live | The exception region is first in DOM and top-left, with a real severity signal behind it | A row of equals above the exception region; an alert zone with nothing urgent behind it | The pharmacy console's "four items need a decision this shift" queue above its stock table |
| **List beside detail** (the two-panel selector; list-detail) | peer panes | List narrower than detail; detail follows selection; selection state visible; one pane at a time below the expanded width | Three sticky columns; a detail that does not follow selection; selection resetting the list's filter or scroll | A reviewer stepping through disputed transactions with the evidence pane following |
| **Table-led** | operate or find, matrix or sequence, many homogeneous | A real table, both axes labelled, sticky header and first column, horizontal scroll inside its own container | Reflowing columns into cards; making every column responsive | An orders workbench |
| **Grid of equals** | browse, set, many homogeneous | Uniform cells, no false hero, ≥ 6 in view | Using it when one tile matters more; a grid of unlike things | A status wall of services |
| **Map-led / canvas-plus-palette** | spatial field | The field holds ≥ 50% of the first viewport; the panel is subordinate and cross-highlights; tools attach by scope | Chrome displacing the artifact; the field as one card among summaries; panel and field not linked | The wind-farm survey plate with its rail |
| **Primary region with supporting pane** | one dominant with peers; co-visibility on demand, or a named supporting pane | The supporting pane is named with its reason and capped; the primary takes about two thirds | A rail that becomes a junk drawer of equal cards; a rail with no reason — a rail that overflows means the relation was a matrix and the prior is table-led | An analytics overview with one chart and three context readouts |
| **Center stage** | operate or read, one unit | The stage is at least twice the width of anything beside it | A marketing band above an editor; side rails competing with the stage | A document editor |
| **Wizard** | transient, operate, a task that is long, complicated, and novel | Real prerequisites between steps; completed work preserved; a review step before commit | Artificial serialization of independent settings; forcing a replay of every step to change one answer | A first-time insurance quote |
| **Hub and spoke** | compact viewport with many peer destinations; occasional, independent activities | Reliable return and orientation from every spoke | Frequent A-to-B switching routed through the hub; a hub padded with unrelated metrics | A service portal on a phone |
| **Titled sections** (the editorial stack) | narrative, few heterogeneous | Each section carries its own topology; one band dominates by scale, colour, or bleed; the sequence is the author's | Equal bands with no anchor; a topology repeating more than twice down the page | A launch story |
| **Asymmetric split** | narrative, decide, two in tension — a claim and an artifact | A felt ratio of at least 1.5 : 1, with the artifact bleeding or overflowing; copy first on collapse | The almost-equal split; equal-weight columns; a split with nothing real on the second side | A proposition beside a real screenshot |
| **Full-bleed image** | narrative, browse a feeling, or a product that *is* the image | The image is the product; a scrim or copy panel tested against the image's lightest region, not its average | Text over untreated midtones | A travel or food page |
| **Typographic poster** | narrative, decide, the argument is verbal and the display face has real personality | One headline is the composition; at most 3 lines | A system font at 8rem; reaching for it with no distinctive face | A manifesto |
| **Product object, centered** | narrative, one hero artifact, and the message is "look at this" | The object is rendered convincingly; the symmetry is earned by the object | Centered symmetry with no strong object underneath | A device launch |
| **Reading column** | read | One measure of 45–75ch; media may bleed via named grid lines; nothing competes beside it; rails stick only on the outside | Line length past 75ch; three sticky columns fighting the same scroll | A long-form article; docs with a table-of-contents rail |
| **Product detail and listing** (PDP / PLP) | decide (buy) on one unit with its evidence, or browse a set of them; the checkout itself is transient | Gallery beside a sticky buy-box; filter rail beside a product grid; on collapse a sticky add-to-cart bar and an off-canvas filter drawer showing its active count | A buy-box that scrolls away; 1-up product grids on phones; `auto-fit` leaving a lonely stretched card in the last row | An independent retailer |
| **Lookbook** | narrative plus buy; browse a feeling | Editorial bands interleaved with shoppable grids; the shopping surfaces | Beautiful and unbuyable | A fashion or home brand |

### Techniques that carry no ratio

Three implementations are worth keeping verbatim, because they solve a mechanical problem and encode no proportion. Everywhere a track ratio would go, the value comes from the record — the dominance line and the felt ratio derived from it — not from this file.

**The editorial bleed, by named grid lines.** Content sits in the measure; a figure crosses the gutters to full width without leaving the flow.

```css
.stack { display: grid; grid-template-columns:
         [full-start] minmax(1rem,1fr) [content-start] minmax(0,64rem)
         [content-end] minmax(1rem,1fr) [full-end]; row-gap: clamp(2rem,6vw,6rem); }
.stack > *      { grid-column: content; }
.stack > .bleed { grid-column: full; }
```

**The sticky commitment.** A buy-box or a summary panel that must stay reachable while a tall gallery scrolls, and its narrow-width form.

```css
.buybox { position: sticky; top: 1.5rem; }
@media (max-width: 900px) {
  .buybox { position: static; }
  .commit-bar { position: fixed; inset: auto 0 0 0; }  /* price + one action */
}
```

**The table that scrolls instead of reflowing.** A matrix stays a matrix at every width.

```css
.table-wrap { overflow-x: auto; }
.table-wrap thead th          { position: sticky; top: 0; }
.table-wrap tbody th          { position: sticky; left: 0; }  /* the row's key */
```

Two-track grids get their tracks from the record, not from a snippet:

```css
/* Values come from DESIGN.md §4: the dominance line and the ratio derived from it. */
.split { display: grid;
         grid-template-columns: minmax(0, var(--dominant)) minmax(0, var(--subordinate));
         gap: clamp(2rem,5vw,5rem); }
```

## Imagery as content

When the dominant region is an artifact and no asset exists, the artifact is drawn — an SVG, a canvas-painted field, a real diagram — as content, the way a survey plate or a record sleeve is content. Pages converge on a left-ranged headline band with an empty right half because that is the shape a missing image takes. A text-only band is one candidate, earned when the argument is genuinely verbal; it is not the default answer to "there is no photograph". For photography, treatment, and when SVG beats a photo outright, see "Imagery integration" below.

## Composition QA

Six checks, run against the built page and mechanical wherever they can be.

1. **The canonical shape is absent unless earned, part by part.** For this surface's category — workspace: stat row, main-plus-rail, sidebar; narrative: headline band with an empty right half, three-up, pricing trio, FAQ — each part present is named in `DESIGN.md` §4 with the line that earned it.
2. **Reading order agrees.** The region declared as the first read is first in DOM order, top-left in geometry, and dominates the first viewport: at least 40% of it under workspace posture, one band under narrative.
3. **Candidates differ on the page.** Once the candidates are rendered as wireframe HTML, or two builds of a paired brief are put side by side, they differ by a first-viewport partition of at least 0.20 rather than in column fractions. While they are still ASCII, their partitions are compared by eye, for a difference in grouping, co-visibility, or progression.
4. **No fingerprint.** No grid-track ratio, snippet, or section sequence is byte-identical to an example in this file without a recorded re-derivation, and the 1.1–1.35 : 1 band is absent.
5. **The nearest neighbour is a relative.** The closest prior build with a *different* relation model or activity is not the one this page most resembles; a page with the *same* task shape may look alike, and that is expected rather than a fault.
6. **The declared difference is asserted, not measured.** For paired briefs, the required difference is written down before building and checked after — a comparison task's units aligned on one axis, a monitor task's exception region leading. A distance never decides on its own.

Each of these is blind somewhere: a tree comparison cannot see ratios, a screenshot cannot see roles below the fold, and automatic region segmentation is only about as reliable as two people agreeing on where the regions are. A failure on one check is a reason to look at the page, not a verdict on it. Run these beside the rest of the pre-ship pass in `references/qa-protocol.md`.

## Imagery integration

### Image-search workflow

Don't search for "beautiful images." Search for visual evidence that belongs to the product, its audience, and the specific layout slot.

```text
Brief
  → identify the visual role
  → formulate several narrow queries
  → search broadly enough to compare
  → reject weak candidates quickly
  → select for crop, palette, composition, and narrative fit
  → treat image into the UI system
  → test at the actual slot size
```

Search a stock-photo service when the product needs photography or reference imagery. If the project already contains brand photography, user-uploaded assets, or an imported design with images, those take priority over a fresh search.

### Define the image's job before searching

Before writing a query, classify the slot.

|Image role|What it must do|Search emphasis|
|---|---|---|
|Hero narrative image|Establish world, mood, product subject|Composition, negative space, atmosphere|
|Product evidence|Prove the product or service is real|Specificity, detail, authenticity|
|Contextual support|Make an abstract story concrete|Relevant people/place/process|
|Editorial section image|Create pacing between text blocks|Crop flexibility, tonal fit|
|Card thumbnail|Identify content quickly|Legible subject at small size|
|Background texture|Establish material without competing with content|Low-detail, tonal stability|
|Team/avatar image|Humanize ownership and collaboration|Consistent framing, genuine expression|
|Data/diagram substitute|Explain process or system|Usually SVG/diagram, not photo|

A photo is only useful when it has a clear job.

### Query formulation

Begin with **three to six focused search queries**, not one vague noun phrase.

Weak query:

```text
film production
```

Likely result: generic clapperboards, cinema cameras, red-carpet imagery, staged actors, irrelevant movie-theater shots.

Better query set for a film-production studio dashboard:

|Query|Likely role|
|---|---|
|`film editor dark studio workstation`|Hero or workspace context|
|`film production crew candid location`|Team/process storytelling|
|`cinematographer camera rig daylight`|Product/process evidence|
|`post production color grading monitor`|Editorial visual for post-production|
|`film set equipment natural light`|Atmospheric background or section image|
|`production notebook call sheet desk`|Detail image for operational/craft tone|

Query structure:

```text
[subject] + [activity or environment] + [lighting / visual quality]
```

Examples:

```text
ceramicist hands studio warm daylight
architectural model workshop overhead
field technician industrial equipment overcast
student reading library window light
coastal restaurant kitchen candid
researcher microscope laboratory side light
```

The third clause matters. It prevents results that are technically relevant but tonally wrong.

### Selection criteria

Once results arrive, select for these criteria in order.

**A. Subject authenticity.** Does the image show the actual world of the product? A logistics product needs real loading bays, routes, packages, equipment, people at work. A food product needs ingredients, process, place, product detail. A healthcare product needs care — generic smiling clinicians may be less credible than a calm, specific environment or process.

**B. Compositional usability.** Can the image survive the required crop? Look for clear subject placement, usable negative space, no critical face/object at likely crop edges, a readable silhouette at small size, foreground/background depth, and tolerance for `object-fit: cover`.

**C. Tonal compatibility.** Does it fit the UI's material world? For a warm editorial product: natural light, warm but not orange-heavy images, visible material texture, controlled contrast, muted or earth-adjacent color. For a cool technical product: structured environment, cooler or neutral light, clean shapes, deliberate geometry — not necessarily "blue technology" imagery.

**D. Narrative specificity.** Does it tell something copy cannot — a real production moment, craft in progress, a distinct environment, a process, a physical artifact, a person's role? A weak image is often merely "nice-looking."

**E. Crop resilience.** Test at the actual intended ratio:

```text
wide hero: 16:9, 3:2, 21:9
editorial image: 4:3, 3:4
product thumbnail: 1:1, 4:5
avatar: 1:1
background strip: 3:1 or wider
```

If the image only works at its original ratio, it is not a flexible UI asset.

### What disqualifies an image

Reject an image when it has any of these problems.

1. **Generic stock symbolism** — handshake, generic laptop, smiling office meeting, staged call-center headset, random city skyline.
2. **The wrong cultural or product context** — a generic cinema image for a production workflow product, a Silicon Valley office for a local cultural institution, a laboratory photo for a logistics product.
3. **No crop safety** — the only important subject sits at an edge or will be cut by the intended slot.
4. **Competing visual noise** — busy background, too many faces, cluttered props, high-frequency detail behind text.
5. **Wrong color temperature** — a heavily cyan-and-magenta club image inside a calm paper-based editorial system, unless that contrast is intentional.
6. **Overly literal cliché** — a leaf for sustainability, a lightbulb for ideas, a lock for security, a coffee cup for coffee, unless it is genuinely a product image rather than symbolic filler.
7. **Overprocessed style** — aggressive HDR, artificial blur, heavy color grading, or a trend look that will fight the UI.
8. **Weak subject readability at thumbnail scale** — a beautiful wide landscape may be useless as a 72px content thumbnail.
9. **Text embedded in the image** — unless the image is a documented poster, cover, or artifact where the text itself is required.
10. **Mismatched production quality** — if one image looks like high-end editorial photography and another looks like casual phone photography, the difference must be intentional.

### Crop and aspect rules by layout slot

**Hero: split-layout image.** Typical ratio `3:2`, `4:3`, or `16:10`. Use for product context, craft, place, feature storytelling.

```tsx
<div className="relative aspect-[3/2] overflow-hidden bg-[#D9D2C7]">
  <img
    src="/images/color-grading-suite.jpg"
    alt="Film editor reviewing footage in a color-grading suite"
    className="size-full object-cover object-[62%_center]"
  />
</div>
```

Crop rule: put the key subject on the visual side opposite the primary text. Use `object-position` intentionally; do not accept a browser-default center crop if it cuts the visual story. Maintain one calm region for text or surrounding whitespace. Do not overlay copy on the image unless the image was selected for text legibility.

**Hero: full-bleed background image.** Typical ratio `16:9`, `21:9`, or full viewport. Use for immersive consumer, travel, culture, media, hospitality, visual product launch.

```tsx
<section className="relative min-h-[680px] overflow-hidden bg-[#1A2423]">
  <img
    src="/images/studio-wide.jpg"
    alt=""
    className="absolute inset-0 size-full object-cover object-center"
  />
  <div className="hero-scrim absolute inset-0" />

  <div className="relative mx-auto flex min-h-[680px] max-w-7xl items-end px-6 py-12 lg:px-10 lg:py-16">
    {/* Content */}
  </div>
</section>
```

Crop rule: use only when the image has enough visual depth and negative space. Place the heading in an intentionally quieter area, not on the busiest part of the image. Keep the live text's contrast valid over the **worst part** of the responsive crop, not only the desktop mockup. Avoid full-bleed images for a dense operational dashboard.

**Editorial image beside copy.** Typical ratio `4:5`, `3:4`, or `4:3`. Use for story pacing, case study, cultural content, hospitality, portfolio.

```tsx
<figure className="max-w-[580px]">
  <div className="aspect-[4/5] overflow-hidden bg-[#E5DDD1]">
    <img
      src="/images/call-sheet-location.jpg"
      alt="A producer marking a call sheet beside a camera cart"
      className="size-full object-cover object-center"
    />
  </div>
  <figcaption className="mt-3 font-['DM_Mono'] text-[11px] leading-[1.4] text-[#756D64]">
    Location scout, North Yorkshire · June 2026
  </figcaption>
</figure>
```

Crop rule: the image should have one clear vertical gesture or subject. Avoid an image that only works wide. Give the caption the same metadata system used elsewhere in the interface. Do not make every image the same ratio; variation is useful in editorial pacing when deliberate.

**Product or project card image.** Typical ratio `4:3`, `3:2`, or `1:1`. Use for project identification, product gallery, destination card, story preview.

```tsx
<a
  href="#project"
  className="group block overflow-hidden border border-[#D4CABE] bg-[#FCF9F3]"
>
  <div className="aspect-[4/3] overflow-hidden bg-[#EAE2D7]">
    <img
      src="/images/coastal-lighting-setup.jpg"
      alt="Lighting setup on a coastal film location"
      className="size-full object-cover transition-transform duration-[260ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.025]"
    />
  </div>
  <div className="p-5">
    {/* Card copy */}
  </div>
</a>
```

Crop rule: the subject must remain legible at 200px wide. Do not crop a person's head at an awkward line. Use a fixed aspect ratio across a repeated card set unless there is a strong editorial reason not to. Keep image hover zoom at `1.015–1.03`, never dramatic.

**Avatar or contributor portrait.** Typical ratio `1:1`. Use for ownership, collaboration, identity, comments, crew/team context.

```tsx
<img
  src="/images/avatar-mina-okafor.jpg"
  alt="Mina Okafor, director of photography"
  className="size-9 rounded-full object-cover object-[50%_35%] ring-1 ring-[#FFFFFF]"
/>
```

Crop rule: eyes should be near the upper third, not centered vertically by default. Use a consistent portrait style across a team list. Do not mix tiny high-fashion portrait crops with casual distant group shots.

**Dashboard contextual banner.** Typical ratio `3:1`, `4:1`, or `16:5`. Use for a single context-setting visual on a project detail page, not decorative wallpaper.

```tsx
<div className="relative aspect-[16/5] overflow-hidden bg-[#243130]">
  <img
    src="/images/night-shoot-banner.jpg"
    alt="Film crew preparing a night shoot on location"
    className="size-full object-cover object-[50%_45%]"
  />
  <div className="absolute inset-0 bg-[linear-gradient(90deg,rgb(20_30_31_/_60%)_0%,rgb(20_30_31_/_18%)_58%,rgb(20_30_31_/_0%)_100%)]" />
</div>
```

Crop rule: use a banner only when it adds project identity or context. A project dashboard should not need a new banner on every route. Keep enough low-detail space for a possible overlaid project title. Do not hide critical project data inside image treatment.

### Overlay and treatment recipes

The treatment should integrate the image into the palette and solve a specific issue: legibility, tonal fit, material consistency, or subject emphasis.

**Dark text-protection scrim.** Use when white or pale text sits over an image.

```css
.hero-scrim {
  background:
    linear-gradient(
      90deg,
      rgb(17 26 26 / 76%) 0%,
      rgb(17 26 26 / 54%) 34%,
      rgb(17 26 26 / 16%) 66%,
      rgb(17 26 26 / 0%) 100%
    ),
    linear-gradient(
      0deg,
      rgb(17 26 26 / 22%) 0%,
      rgb(17 26 26 / 0%) 46%
    );
}
```

Use when the text is placed on the left of a full-bleed image, the image has uneven brightness, or the stance supports a cinematic, immersive, or media-led hero. Do not use when the product is operational and the image is not necessary, when the overlay becomes so dark that the image no longer has a role, or when the image was selected purely because a heavy overlay can hide its flaws.

**Light editorial wash.** Use to keep a photograph visible while bringing it into a warm paper system.

```css
.editorial-image {
  position: relative;
  overflow: hidden;
  background: #E9E0D4;
}

.editorial-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      rgb(245 240 232 / 22%) 0%,
      rgb(245 240 232 / 5%) 52%,
      rgb(169 70 45 / 10%) 100%
    );
  mix-blend-mode: multiply;
}

.editorial-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.88) contrast(0.96) sepia(0.04);
}
```

Exact effect: saturation reduced to `88%`, contrast reduced to `96%`, a very light sepia shift of `0.04`, and a warm multiply wash at `22% → 5% → 10%` opacity. This is enough to make mismatched photography sit beside warm neutral UI without turning every image brown.

**Cool technical tone matching.** Use for technical products where photography needs to sit in a cool, controlled environment.

```css
.technical-image {
  position: relative;
  overflow: hidden;
  background: #D8E0E1;
}

.technical-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      rgb(18 59 69 / 18%) 0%,
      rgb(39 107 138 / 10%) 55%,
      rgb(244 246 247 / 8%) 100%
    );
  mix-blend-mode: color;
}

.technical-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.78) contrast(1.04);
}
```

Exact effect: saturation reduced to `78%`, contrast increased to `104%`, a cool color blend overlay using the product's deep teal and information blue, and no extreme blue tint. This works for equipment, locations, industrial environments, maps, and workspace photography — it is not a generic "tech photo" filter.

**Duotone treatment.** Use a true duotone only when the product's visual system has a strong graphic or campaign-quality image language. Good fits: cultural event, music platform, activist/civic campaign, youth-oriented consumer experience, editorial storytelling section, brand campaign. Poor fits: account settings, financial tables, generic product dashboards, small card thumbnails where color fidelity matters.

```css
.duotone-image {
  position: relative;
  overflow: hidden;
  background: #1F244A;
}

.duotone-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1) contrast(1.12);
  mix-blend-mode: luminosity;
}

.duotone-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      #24203D 0%,
      #5A47D5 48%,
      #FFB94D 100%
    );
  mix-blend-mode: color;
}
```

The result preserves tonal information from the image while applying the app's own accent palette.

**Subtle image depth without an overlay.** Sometimes the correct treatment is only crop plus restrained tonal adjustment.

```css
.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.94) contrast(1.02);
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

@media (hover: hover) and (pointer: fine) {
  .product-card:hover .product-image img {
    transform: scale(1.025);
  }
}
```

Use this when image fidelity matters — food, products, art, place, photography portfolios, or anything where the source image itself is part of the value.

### When to use SVG instead of photos

Use SVG when the visual needs to be explanatory rather than atmospheric, consistent across many sizes, tied directly to data or interaction, brand-specific, visually simple at small scale, or impossible/misleading to represent through stock photography.

|Need|Better choice|
|---|---|
|Workflow explanation|Diagram or process graphic|
|Data relationship|Chart, map, timeline, node graph|
|Product architecture|SVG diagram|
|Empty state|Small purposeful illustration or icon|
|Status / category|Icon system|
|Branded pattern or motif|SVG shape/pattern|
|A physical or abstract concept that must remain controllable|Custom illustration|
|A small visual identity moment|Monogram, badge, mark|

Use a photo instead when the user needs proof of a real place, person, product, or process; the subject benefits from authenticity and material detail; the product is selling an experience, place, or physical object; or the image needs emotional specificity a generic illustration cannot provide. A photo of a real production location is better than an SVG clapperboard if the story is "this is the work we make."

The SVG is subordinate to the UI — it should not introduce a new unrelated illustration language on every route. Drawing conventions vary by stance:

- **Precision / operations products:** geometric fills or simple monoweight strokes, `stroke-width="1.5"` or `2` at a `24 × 24` icon scale, square or modest corner joins, low color count, one semantic accent maximum, structured grid alignment, minimal texture, no decorative sparkles or random circles.

```tsx
export function DeliveryFlowGraphic() {
  return (
    <svg
      viewBox="0 0 320 144"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Delivery path from edit to client approval"
      role="img"
      className="h-auto w-full"
    >
      <path d="M44 72H138M182 72H276" stroke="#8FA0A4" strokeWidth="1.5" />
      <path d="M133 67L138 72L133 77" stroke="#8FA0A4" strokeWidth="1.5" />
      <path d="M271 67L276 72L271 77" stroke="#8FA0A4" strokeWidth="1.5" />

      <rect x="16" y="44" width="56" height="56" rx="6" fill="#FFFFFF" stroke="#C7D0D2" />
      <rect x="132" y="44" width="56" height="56" rx="6" fill="#FFFFFF" stroke="#C7D0D2" />
      <rect x="248" y="44" width="56" height="56" rx="6" fill="#FFF9F5" stroke="#D9A888" />

      <path d="M31 61H57V83H31V61Z" stroke="#123B45" strokeWidth="1.8" />
      <path d="M147 61H173V83H147V61Z" stroke="#123B45" strokeWidth="1.8" />
      <path d="M263 62L276 84L289 62H263Z" fill="#D46B2C" />

      <text x="44" y="122" textAnchor="middle" fill="#607076" fontSize="11" fontFamily="Geist Mono">
        EDIT
      </text>
      <text x="160" y="122" textAnchor="middle" fill="#607076" fontSize="11" fontFamily="Geist Mono">
        REVIEW
      </text>
      <text x="276" y="122" textAnchor="middle" fill="#8C3C17" fontSize="11" fontFamily="Geist Mono">
        RELEASE
      </text>
    </svg>
  );
}
```

- **Editorial or craft products:** fewer, larger forms; material references through line rhythm or shape, not fake photorealistic effects; low contrast unless the illustration is the main feature; one drawing vocabulary across every illustration; carefully controlled asymmetry; hand-drawn quality only if it belongs to the product, not as generic charm.
- **Playful consumer products:** larger, friendlier silhouettes; strong shape rhythm; limited bright palette; smooth corners or intentional irregular geometry; minimal interior detail; motion only for feedback, not constant ambient decoration.

General SVG rules: start with the silhouette and major shapes; use negative space deliberately; keep the element count tied to the brief; use one drawing vocabulary per illustration; do not mix outline, glossy 3D, stipple, and gradient fill without a reason; design for the smallest intended rendering size; do not use illustrations as filler for an otherwise weak empty state or hero.

### Distinguished vs. generic hero

A distinguished hero is not defined by visual complexity. It is defined by a clear relationship between proposition, composition, visual evidence, and action.

A generic gradient-blob hero has a recognizable shape: a vague headline ("The future of productivity starts here"), a generic subheading ("Manage your work in one powerful platform"), two default CTA buttons, a large purple-blue gradient with blurred blob shapes, a dashboard mockup with no specific data or task, equal-weight typography and image, and no reason the hero belongs to this product instead of any other SaaS product. The problem isn't that gradients, blur, or glass are inherently bad — it's that none of these elements are tied to a specific product, user, or task.

A distinguished hero swaps decoration for evidence. For a film-production operations platform, the design choices might be:

```text
Stance: quiet editorial operations

Primary visual: real production workspace / practical editing image

Composition: text and dashboard proof have different jobs. The copy block
is not centered because this is not a generic campaign. The visual
provides actual evidence: shoot, crew, budget, and delivery status.

Palette: warm paper ground, deep studio green, oxide urgency accent.

Action: one primary action, one low-emphasis proof link.

Material: no gradient blob, no decorative glass — a restrained image
treatment and border-led composition instead.
```

The photo itself carries a localized, earned overlay — a directional scrim (`linear-gradient(90deg, rgb(37 33 30 / 58%) 0%, rgb(37 33 30 / 18%) 55%, rgb(37 33 30 / 0%) 100%)`) plus `saturate-[0.86] contrast-[0.97]` — and a small glass-like data panel (`bg-[rgb(37_33_30_/_74%)]` with `backdrop-blur-[10px]`) floats over the image's calm region, showing three real numbers (shoot days, budget used, next delivery) instead of a content-free mockup. It is not distinguished because it has a serif, an image, or a glass panel — it is distinct because the copy names a real production problem, the image belongs to the product's actual world, the content proof is specific, the composition is asymmetric for a reason (proposition on one side, operational evidence on the other), the palette maps to the stance, the overlay is localized and earned, the CTA is direct and singular, and there are no decorative blobs trying to substitute for a product point of view.

## Working from a supplied reference

When a brief supplies an image, screenshot, photo, logo, or mockup, treat it as load-bearing design input — it frequently communicates more than the written prompt, so treat it as a first-class source of truth for the surface it covers. This authority is local: it governs the surface it was supplied for, not the rest of the project, and it does not override an explicit brief instruction elsewhere.

### Determine the image's role first

Classify a supplied image before deciding how to use it. Three broad categories cover most cases — reproduce it, draw inspiration from it, or use it as a content asset — but it's worth distinguishing five practical roles:

|Role|Required interpretation|
|---|---|
|**Reference to match**|Reproduce visible layout, hierarchy, component types, and styling fidelity. Deviate only where the reference is incomplete or ambiguous.|
|**Inspiration / vibes**|Match the visual feeling — palette, density, type mood, materiality — but do not copy the exact layout or copy.|
|**Content to use**|Display the photo, illustration, logo, or icon in the app; do not recreate it in code.|
|**Bug report / current state**|Treat the image as evidence of a problem to fix, not a target to reproduce. Ask if the failure is unclear.|
|**Data source**|Read visible table/menu/schedule information and seed the interface with that real data, rather than placeholder text.|

If ambiguous: default UI screenshots to **reference to match**, and default photos/logos/illustrations to **content to use**.

### Scope the actual reference

If the image is low-resolution or blurred, capture broad intent rather than fake pixel-level precision. If cropped or partial, do not invent unseen areas — infer only conservatively when the request clearly requires a fuller build. Separate the actual design subject from browser chrome, OS elements, cursor, surrounding apps, or incidental framing. If a screenshot includes a whole desktop but the request is clearly about one modal, card, or section, recreate the intended subject, not the accidental surrounding frame.

### Inspect before coding

Do not guess from a filename or a one-line description. Inspect the image and extract:

- Main layout and hierarchy
- Primary, secondary, and chrome regions
- Navigation, sidebar, list, card, footer, tab bar, toolbar, and modal roles
- Light/dark palette, surfaces, accents, and text tones
- Serif/sans/display cues and relative type scale
- Visual density
- Readable text content and labels
- Visible controls and affordances

Use real readable text from the image where it carries meaning; paraphrase only obvious filler.

### Reproduction priority order

Build a reference reproduction in this order: **geometry → palette → type → texture.**

1. **Geometry first** — page skeleton and major regions, then hierarchy and grouping, then the correct component type for each region (this is the layout and structure the reference actually shows, not an invented substitute).
2. **Palette second** — once the region structure holds, extract the light/dark palette, surfaces, accents, and text tones, and encode them in shared tokens rather than scattering raw color literals through components.
3. **Type third** — match serif/sans/display cues and the relative type scale, and carry over real readable text and data from the reference rather than placeholder copy.
4. **Texture last** — match spacing, density, and material rhythm, then wire interaction for controls that are clearly interactive so the reproduction behaves like a real surface rather than a static image.

Reference wins over personal defaults for its surface: reproduce its geometry, palette, type, and density even when the hero-archetype or dashboard-arrangement logic above would otherwise point toward a different pattern.

### Rendering a supplied image inside the interface

When an attached image must appear inside the built interface rather than be redrawn: preserve its aspect ratio; use `object-cover` for hero/background imagery and `object-contain` for logos and icons; always provide meaningful alt text; and never recreate an attached photo, logo, illustration, or existing SVG with gradients, `<div>` elements, or new hand-written SVG. Reference the asset the way the project's own toolchain already imports static assets, rather than assuming one scheme — do not hardcode a literal file path if the project's bundler fingerprints assets. If the interface needs additional images beyond what was supplied, search for or generate assets that match the uploaded material's subject, style, and mood — supplementary assets should look like they belong to the same curated set, not like generic stock dropped in beside it.

### Multiple-image interpretation

Multiple screenshots of one app usually indicate different screens or states — build all of them and connect them with routing or tabs. A screenshot plus a logo or photo normally means the screenshot is the layout reference while the logo/photo is content to embed. Two near-identical screenshots may represent before/after or light/dark versions — support both. If image roles remain unclear, state the interpretation briefly and proceed.
