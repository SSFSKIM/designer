**Replace the menu—but make the replacement a compiler of relationships, not a classifier with more labels.** The important transition is not:

> “Dashboard” → “exception-first layout”

but:

> “Operators must identify an actionable exception, inspect its evidence, and act without losing queue position” → priority, co-visibility, attachment, and context-preservation constraints → several permissible compositions.

The literature supports that architecture in pieces. It does **not** establish a validated, universal set of composition axes for autonomous web design. The closest precedents combine task models, relational or rhetorical structures, constraint solving, and human selection. Your proposed grammar is a defensible synthesis of those traditions, provided you distinguish **task fit**, **alternative-layout diversity for one task**, and **differentiation between different tasks**.

## 1. Prior art: what actually derives what

### Systems that compile or optimize presentations

|Prior art|Variables or structure read|Layout properties determined|Measured outcome|What it does not establish|
|---|---|---|---|---|
|**ConcurTaskTrees / TERESA — Paternò, Mori and colleagues**|Task hierarchy; temporal dependencies, alternatives and concurrency; interface objects; target-platform capabilities. Abstract composition includes grouping, ordering, hierarchy and relations between interactors.|Division into presentations; grouping; navigation; translation of abstract interactors into concrete controls and platform-specific arrangements.|Demonstrated model-to-interface transformations, including multi-device redesign.|Not evidence that automatically extracting these models from prose produces appropriate or diverse macro-layouts. Requires substantial explicit modeling and transformation rules. **Very close architectural precedent.** ([W3C](https://www.w3.org/2004/06/DI-MCA-WS/presentations/final/130940/presentation-cnr.html "https://www.w3.org/2004/06/DI-MCA-WS/presentations/final/130940/presentation-cnr.html"))|
|**Casner, 1991 — task-analytic graphic generation, BOZ**|Data plus a procedural description of the user’s task; logical operations that can be replaced by perceptual operations.|Representation and arrangement that reduce search and mental computation. The same flight data can warrant different presentations for different questions.|A seven-participant experiment found improvements between some successive task-informed presentations, but not every additional transformation improved performance.|Small, specialized graphic-presentation tasks, not complete web interfaces. Task descriptions were supplied, not inferred. Crucially, a table can remain the best answer for a lookup task. ([ResearchGate](https://www.researchgate.net/publication/220183723_Task-Analytic_Approach_to_the_Automated_Design_of_Graphic_Presentations "https://www.researchgate.net/publication/220183723_Task-Analytic_Approach_to_the_Automated_Design_of_Graphic_Presentations"))|
|**SUPPLE — Gajos and colleagues**|Functional UI specification, device constraints, usage patterns, preferences and individual motor abilities.|Widget selection and interface organization optimized for predicted interaction cost.|Controlled studies reported improved speed, accuracy and satisfaction for motor-impaired participants relative to manufacturer defaults.|Validates adaptation to specified users and tasks, not stylistic originality or general brief-to-page composition. Model accuracy and supplied specifications matter. ([하버드 전산학부](https://www.eecs.harvard.edu/~kgajos/research/supple/ "https://www.eecs.harvard.edu/~kgajos/research/supple/"))|
|**Weitzman & Wittenburg, 1994/1996 — relational grammars**|Structured descriptions of content and context, interpreted by relational grammars.|Media realization and spatial/temporal constraints, subsequently resolved into presentations.|Working grammar-based presentation architecture; I did not verify a comparative diversity or task-performance result.|A grammar can intentionally encode a fixed visual family. **“Uses a grammar” does not itself mean “avoids templates.”** ([ACM Digital Library](https://dl.acm.org/doi/pdf/10.1145/192593.192718 "https://dl.acm.org/doi/pdf/10.1145/192593.192718"))|
|**Rutledge et al., 2000 — rhetorical structure → presentation constraints**|Communicative intent: sequence, main/supporting content, and coequal content relationships.|Spatial, temporal and navigation constraints; compensation strategies when one presentation dimension cannot accommodate the content.|Demonstrated derivations and alternative presentations preserving rhetorical relationships.|No demonstrated landing-page conversion benefit or universal validation of the rhetorical vocabulary. Nevertheless, this is unusually direct prior art for your landing-page problem. ([CWI](https://ir.cwi.nl/pub/11350/11350B.pdf "https://ir.cwi.nl/pub/11350/11350B.pdf"))|
|**Scout — Swearngin et al., CHI 2020**|Supplied elements, semantic groups, repeated groups, emphasis, ordering, and keep/prevent constraints.|Position, size, arrangement, alignment, spacing and alternative representations.|Eighteen designers, two mobile-screen tasks: **12% greater within-designer spatial diversity**. Quality differences were nonsignificant; that is **not an equivalence or non-inferiority result**.|Human-supplied semantics, small screens and designer refinement—not autonomous interpretation of a product brief. Its diversity metric primarily measures geometry, not changes in task relationships. ([Amanda Swearngin](https://amaswea.github.io/assets/scout/AmandaSwearngin_Scout_CHI2020.pdf "Scout: Rapid Exploration of Interface Layout Alternatives through High-Level Design Constraints"))|
|**GRIDS — Dayama et al., CHI 2020**|Elements, size constraints, canvas, preferences and constraints on placement/alignment; a mixed-integer formulation.|Grid structure, packing, alignment and diverse near-optimal arrangements.|Optimized layouts received higher ratings in a 13-person study; a 16-designer study supported usefulness for exploration, particularly early in design.|Grid quality is not task fit. Grouping existed in the formulation but was absent from the evaluated interface, limiting complex hierarchical designs. ([컴퓨터 행동 연구소](https://userinterfaces.aalto.fi/grids/resources/chi2020-dayama-grids.pdf "https://userinterfaces.aalto.fi/grids/resources/chi2020-dayama-grids.pdf"))|
|**Sketchplore — Todi, Weir & Oulasvirta, DIS 2016**|Current sketch, elements, importance/usage assumptions; predictive models of search, pointing, clutter, grid quality and color harmony.|Local refinements and global alternatives in position, size and color.|Twenty-user selection study: faster performance **after excluding each app’s first selection**, not over all trials. Ten-designer study found substantial use of suggestions.|Explicitly lacks semantic and dynamic-interaction modeling; practical optimization was limited to about ten elements. It infers a design problem from a sketch, not a user workflow from a brief. ([Kashyap Todi](https://www.kashyaptodi.com/data/SketchploreDIS2016.pdf "https://www.kashyaptodi.com/data/SketchploreDIS2016.pdf"))|

**The central distinction:** Scout and GRIDS help explore arrangements once much of the problem is specified. Casner, SUPPLE, TERESA and rhetorical-structure work are stronger precedents for deciding **what the arrangement must accomplish**.

### Taxonomies, patterns and evaluation foundations

|Prior art|Variables or structure read|What it determines or describes|Evidence and limits|
|---|---|---|---|
|**Bach et al., Dashboard Design Patterns, 2022/2023**|Content abstraction, dashboard structure, layout, interaction and related characteristics.|A vocabulary of composable patterns—not simply mutually exclusive whole-page genres.|Derived from **144 dashboards**, yielding **42 patterns**, with a 23-participant workshop. Descriptive synthesis and demonstrated design usefulness, not a controlled proof that particular task variables require particular compositions. ([arXiv](https://arxiv.org/html/2205.00757v1 "Dashboard Design Patterns"))|
|**Sarikaya et al., 2019**|Purpose, audience, interaction, construction, alerts, benchmarks, updateability and related factors.|A dashboard design space and clusters of dashboard characteristics.|**83 examples, 15 factors, seven clusters.** Importantly, the authors could not operationalize analysis tasks and context of use reliably from their collected examples. This is a reason **not** to treat screenshot-derived categories as task-grounded grammar inputs. ([Alper Sarikaya](https://alper.datav.is/assets/publications/dashboards/dashboards-preprint.pdf "https://alper.datav.is/assets/publications/dashboards/dashboards-preprint.pdf"))|
|**Tidwell, Designing Interfaces**|What people do with objects, how they move between tasks, whether they need context, selection, creation or progression.|Conditional organizational and navigation patterns: selectors, drilldown, canvas/palette, wizard, hub/spoke, alternative views.|Pattern arguments and examples, not a universal comparative performance study. The native format already includes **when and why**; reducing it to a screenshot catalogue discards the useful part. ([O'Reilly Media](https://www.oreilly.com/library/view/designing-interfaces/0596008031/ "https://www.oreilly.com/library/view/designing-interfaces/0596008031/"))|
|**Site genres — van Duyne, Landay & Hong**|Site purpose and characteristic audience/activity expectations.|High-level expectations about content, navigation and transactions.|Useful priors; too coarse to determine within-genre composition. A site genre should constrain expectations, not emit a page skeleton. ([O'Reilly Media](https://www.oreilly.com/library/view/the-design-of/0131345559/ch06.html "https://www.oreilly.com/library/view/the-design-of/0131345559/ch06.html"))|
|**Rosenfeld, Morville & Arango: organization schemes and structures**|Content distinctions and ways users seek information; exact/ambiguous schemes and organizational relationships.|Taxonomy, grouping and navigation structure.|An IA foundation, not a screen-geometry compiler. **Content hierarchy and visual hierarchy are not interchangeable outputs.** ([O'Reilly Media](https://www.oreilly.com/library/view/information-architecture-4th/9781491913529/ch06.html "https://www.oreilly.com/library/view/information-architecture-4th/9781491913529/ch06.html"))|
|**Bertin → Mackinlay’s APT; Card & Mackinlay’s design space**|Attribute measurement levels, data relationships, transformations and available graphical encodings.|Expressive/effective mappings to marks, position, connection, enclosure and other graphical properties.|Strong formal vocabulary for representation; not a validated whole-page composition grammar. **Quantitative/ordinal/nominal describe attributes, not alternatives to network or spatial relationships.** ([ACM Digital Library](https://dl.acm.org/doi/10.1145/22949.22950 "https://dl.acm.org/doi/10.1145/22949.22950"))|
|**Shneiderman, 1996**|Seven data types crossed with seven tasks, including overview, filtering, relating and details.|An interaction-design space and the overview/zoom/filter/details heuristic.|Explicitly a starting point, not a rule that every interface needs an overview strip above its work area. No measured macro-layout diversity claim. ([드럼](https://drum.lib.umd.edu/bitstreams/419fe7fc-d7d8-4929-bdf0-f4a3041455c1/download "https://drum.lib.umd.edu/bitstreams/419fe7fc-d7d8-4929-bdf0-f4a3041455c1/download"))|
|**Ben Fry’s visualization process**|Data and the successive needs of acquiring, transforming, representing and interacting with it.|A process for developing a representation.|Useful workflow guidance, not independent composition variables or an automatic page-layout derivation. ([Ben Fry](https://www.benfry.com/phd/dissertation/5.html "https://www.benfry.com/phd/dissertation/5.html"))|
|**Shape grammars — Stiny & Gips**|Initial shapes and permitted transformation rules; semantics only when supplied by the grammar author.|Families of spatial configurations.|Establishes formal generativity, not task fitness. A highly generative grammar can still produce one recognizable family—or arbitrary variation. ([Academia](https://www.academia.edu/44344315/Shape_grammars_and_the_generative_specification_of_painting_and_sculpture "https://www.academia.edu/44344315/Shape_grammars_and_the_generative_specification_of_painting_and_sculpture"))|
|**Ngo, Teo & Byrne, 2003**|Geometric properties of displayed objects.|Aesthetic scores concerning balance, density, regularity, sequence and related qualities.|Compared model predictions with aesthetic judgments. These are **evaluation proxies**, not task-derived composition rules; maximizing regularity or symmetry can itself encourage convergence. ([Academia](https://www.academia.edu/11749849/Modelling_interface_aesthetics "https://www.academia.edu/11749849/Modelling_interface_aesthetics"))|
|**Rico / Enrico**|Existing mobile screens, UI hierarchies, visual features and topic labels.|Retrieval, representations and classification of observed interfaces.|Valuable corpora and comparison sets. Enrico’s 1,460 screens and 20 topics describe existing design organization; they do not establish causal mappings from user task to layout. ([Danafergan](https://danafergan.com/publications/deka2017rico.pdf "https://danafergan.com/publications/deka2017rico.pdf"))|

**Bibliographic caution:** I could not verify the title/author combination “Bailey & O’Brien, _Unraveling web design: the layout diversity_,” or an “ABC” method specifically associated with Sketchplore. I have not attributed findings to either. The verified site-genres source above is van Duyne, Landay and Hong.

## 2. Recommended composition variables

I recommend **seven structured fields**, ranked by their usefulness in preventing category-driven layout selection—not by an experimentally established importance ranking.

These should not be seven mutually independent sliders. Some are facts from the brief; others are explicit, auditable interpretations of those facts. The rules below are **proposed engineering rules**, informed by the research above, not experimentally validated universal laws.

### Ranked variable set

|Rank and variable|Values to record|Layout properties driven|One or two checkable rules|Collapses and dependencies|
|---|---|---|---|---|
|**1. Task and decision structure**|Primary activity: monitor, locate, compare, configure, create, transact, understand/evaluate. Record required steps and prerequisite/choice/parallel relationships—not just one verb.|Task-region grouping; progression; placement of controls and evidence; whether work is continuous or staged.|Every required action has an identified operating region and its necessary evidence. Independent, frequently revisited edits must not be forced through a sequential wizard unless the brief supplies a scaffolding reason.|Activity alone is insufficient: “monitor” can mean passive awareness or repeated exception resolution. Prerequisites are a relation, but deserve explicit task-level representation.|
|**2. Task-relevant information relations**|Peer set; ordered sequence; hierarchy; entity-by-attribute matrix; network; intrinsic spatial field; claim/evidence/qualification. Multiple relations may coexist.|What aligns, nests, connects, sits adjacent or follows something else.|Required comparison fields use consistent positions/order across peers. A spatial field dominates only when spatial relationships are needed for the decision—not merely because records contain addresses.|“Primary object” often duplicates this field or prematurely chooses a representation. Data hierarchy need not become navigational or visual hierarchy.|
|**3. Co-visibility and context retention**|Replace-one-focus; context-plus-focus; simultaneous peers; edit-plus-feedback/reference. Record the actual sets that must remain available together.|Panes, inline expansion, linked regions, disclosure, preserved selection and return state.|Required comparison/reference regions must be simultaneously available at the target desktop viewport. Selecting another record must preserve the stipulated queue/filter/scroll context.|“Overview-to-detail relationship” is largely the consequence of these requirements. Co-visibility is not fully implied by “compare” or “configure”; the particular evidence matters.|
|**4. Content inventory, geometry and scale**|Actual items and fields; uniform/heterogeneous schema; text-length range; media shape; typical and high-volume counts; bounded/growing collections.|Repeated unit, table/list/grid suitability, column capacity, local density, overflow and disclosure.|Test empty, singleton, typical and high-volume fixtures. Every repeated metric/card must correspond to a genuine content peer; no invented three-item group to complete a row.|Content volume and geometry interact with viewport. Local density is mostly an output, not another independent composition axis.|
|**5. Attention and consequence ordering**|Action-critical, routine-primary, supporting, optional; allow ties and partial orders. Record the consequence of overlooking a region.|First-viewport allocation; dominance; sequence; demotion/disclosure of supporting material.|In an exception-response task, the exception heading and first actionable item appear in the initial viewport; unrelated KPI cards cannot precede them. Regions declared unequal in decision importance cannot all receive indistinguishable treatment without an explicit reason.|Mostly **derived from task, criticality and current state**. Keep it as an intermediate field, not a second independent criticality setting competing with your stance layer.|
|**6. Temporal and update behavior**|Two fields: reference = historical/current/future interval; update = static/on-request/event-driven. Add whether order must remain stable during action.|Time alignment, freshness indicators, chronology, update policy and spatial stability.|Live monitoring must expose actionable exceptions and freshness—not automatically the newest event. Updates must not move the focused/selected item during an operation without an explicit reconciliation behavior.|“Static/historical/live/scheduled” mixes separate dimensions. A historical analysis can update live; a future schedule can be edited interactively. Chronology also overlaps information relations.|
|**7. Access and switching structure**|Known-item lookup, browsing or continuation; shallow/deep information space; frequent/occasional transitions within and between scopes.|Persistent versus local navigation, search, drilldown, return paths and navigation footprint.|A specified high-frequency sibling transition cannot require a compulsory hub round trip. A persistent navigation rail must serve documented recurring transitions, not merely the label “application.”|Navigation depth partly follows IA; transition frequency is independent evidence. Neither automatically implies a sidebar.|

### What to demote or remove

**Do not retain your candidate “primary object” enum unchanged.** It mixes ontological levels: a record is a content unit; a queue is a collection with an ordering policy; a timeline is often a representation; a map is a spatial representation; a canvas is an interaction surface. Making these peers invites rules such as “map → map-led page,” which decide the composition before deriving it.

Retain the actual domain entities and their schemas in the content inventory. Derive their presentation from task, relations and co-visibility.

**“Hero” is a consequence, not an input.** It is the region—or coordinated group of regions—that earns dominance from attention requirements and content geometry. Some pages should have no hero. Some should have coequal comparison regions. “What is the hero?” is therefore a late question.

**Viewport, input modality, accessibility needs, language and user expertise are boundary conditions.** They constrain all seven fields; they should not become optional novelty knobs. Likewise, your stance’s energy or material model must not manufacture asymmetry that contradicts task relationships.

### One grammar or two?

**One composition kernel, two semantic front ends.**

For product interfaces, derive an **operational model**: actions, prerequisites, state, evidence and context retention. For landing/editorial pages, derive a **communicative model**: audience question, claim, evidence, qualification, comparison and commitment. Rutledge et al. supply direct precedent for the latter: rhetorical relationships can compile into spatial, temporal or navigational constraints without requiring a unique presentation. ([CWI](https://ir.cwi.nl/pub/11350/11350B.pdf "https://ir.cwi.nl/pub/11350/11350B.pdf"))

Both can compile into the same small operator vocabulary:

`order`, `group`, `nest`, `align`, `juxtapose`, `attach`, `repeat`, `disclose`.

These are **composition operators**, not additional brief variables. A commerce page may use both front ends: explain an offer, compare alternatives, then complete a transaction. “Landing page” should not trigger a separate hero/features/pricing/FAQ production rule.

### What the agent should write before building

Require a constraint ledger:

> **Brief evidence → interpreted relationship → layout constraint → rendered assertion → forbidden move.**

Then request two or three **region-tree candidates**, each with first-viewport allocation and a stated tradeoff. Candidates should differ in grouping, context presentation or progression—not merely a 60:40 versus 50:50 split.

Keep content inventory constant. Do not permit the agent to invent sections to create diversity. And when only one composition satisfies the important constraints, let it say so rather than manufacturing inferior alternatives.

## 3. Mechanical layout diversity and clone detection

### What the cited studies actually measured

|Work|Actual method|Interpretation and limitation|
|---|---|---|
|**Design Theater, July 2026 revision**|TFS checks stated design commitments; PAS checks prompt-embedded principles. DHI has **three separate channels**: UIClip screenshot similarity; CIELCh color histograms with Earth Mover’s Distance; **OmniParser v2 screenshot detection followed by tree edit distance**. Screenshots are 1200 × 1200.|The layout method is **not DOM-tree comparison**. Its published description does not fully specify tree construction, labels, edit costs and normalization. Five tools are compared **within each same prompt**: this does not directly measure one agent cloning layouts across different task shapes. ([arXiv](https://arxiv.org/html/2607.22928v2 "https://arxiv.org/html/2607.22928v2"))|
|**Goree et al., CHI 2021**|Screenshot-derived **XY-tree representations** and tree edit distance for layout; additional color and CNN-based visual comparisons.|Reports an over-30% reduction in average layout distance after 2007. This is historical convergence, not a task-conditioned appropriateness test. Library adoption is part of the explanatory evidence, not experimentally isolated causation. **Not raw DOM edit distance.** ([ACM Digital Library](https://dl.acm.org/doi/fullHtml/10.1145/3411764.3445156 "https://dl.acm.org/doi/fullHtml/10.1145/3411764.3445156"))|
|**Webzeitgeist, CHI 2013**|Captures DOM, resources and rendered/computed properties at scale. Its example-based region retrieval uses a learned element-feature similarity metric, trained with **OASIS**.|Infrastructure and demonstrations for querying/retrieving designs—not a calibrated macro-layout clone detector. Possessing DOM data does **not** mean it evaluated DOM-tree edit distance, depth/breadth or repeated-card convergence. ([Stanford HCI Group](https://hci.stanford.edu/publications/2013/Webzeitgeist/webzeitgeist.pdf "https://hci.stanford.edu/publications/2013/Webzeitgeist/webzeitgeist.pdf"))|
|**Scout**|Combines matched-element positional changes, area changes and changes in pairwise element distances.|Useful for spatial variation with corresponding elements. It can register geometric differences without a different grouping, navigation or task relationship. ([Amanda Swearngin](https://amaswea.github.io/assets/scout/AmandaSwearngin_Scout_CHI2020.pdf "Scout: Rapid Exploration of Interface Layout Alternatives through High-Level Design Constraints"))|

A further caution on Design Theater: its channels have different scales, and the authors explicitly do not aggregate them. Its reported appearance/layout convergence is useful evidence, but the raw channel ranges should not be interpreted as a calibrated effect-size comparison saying layout convergence is _X times_ stronger than color convergence. ([arXiv](https://arxiv.org/html/2607.22928v2 "https://arxiv.org/html/2607.22928v2"))

### Recommended extraction: rendered regions, not framework markup

I would implement a **canonical rendered-region representation**. Combining accessibility structure with rendered geometry has precedent in datasets such as WebUI; the particular canonicalization below is my proposed implementation. ([arXiv](https://arxiv.org/html/2301.13280v1 "https://arxiv.org/html/2301.13280v1"))

Render each fixture at fixed viewports after fonts and layout settle. Combine landmarks/accessibility roles, DOM containment and bounding boxes. Remove hidden/decorative elements and collapse inert wrapper chains.

Maintain two parallel representations:

**Structural:** region containment, peer grouping, order, repetition, attachment and declared control/context relationships.

**Geometric:** normalized rectangles, first-viewport occupancy, resolved tracks, dominant-region shares and whitespace.

For macro comparison, collapse repeated rows into something like `repeat(record-schema, count-bucket)`. Otherwise a hundred table rows overwhelm the distance between “table workspace” and “table plus linked detail.” Preserve repetition statistics separately.

Use a small, fixed role vocabulary—navigation, collection, detail, workspace, controls, evidence, explanation—not product names or agent-invented labels. Compare the application shell and task workspace separately.

### Which measurements earn their place?

|Measure|Concrete implementation|Catches|Misses or confounds|
|---|---|---|---|
|**Canonical region-tree edit distance**|Ordered tree edit distance with documented insertion/deletion/substitution costs. A simple normalization is `TED / (nodesA + nodesB)` with unit costs.|Flattening versus nesting; attached detail versus independent sections; changes in grouping and sequence.|Raw DOM wrappers create false differences. A tree alone misses cross-region relationships, geometry and task fitness.|
|**Relationship-graph signature**|Add typed edges: contains, precedes, adjacent-to, aligned-with, co-visible-with, controls, supplies-evidence-to. Compare required edges and graph structure.|A linked workbench versus independent cards even when DOM nesting is similar.|Functional edges need code/state inspection or independently verified annotations; geometry alone cannot establish them.|
|**Region-count and area-share signature**|Count regions by role; calculate largest-region share, navigation share and concentration of non-overlapping region areas.|Dominant workspace versus grid of equals; excessive chrome; a large summary strip.|Area is not attention. Equal area vectors can have entirely different arrangements.|
|**First-viewport composition**|Record role occupancy, vertical ordering and visibility of specified targets within the initial viewport. A coarse occupancy raster can supplement exact boxes.|Big heading/three-stat-row pushing actual work below the fold; different initial priorities.|Ignores later content unless measured separately. Sensitive to fixture, viewport and font changes.|
|**Resolved tracks and spans**|Inspect computed layout and child rectangles, not merely the presence of `grid-cols-12`. Record effective column groups, ratios and spans.|Equal columns versus a dominant field and subordinate context; genuine use of width.|Ratio changes are **geometric**, not necessarily topological. Different CSS techniques can render identically.|
|**Repeated-unit detection**|Normalize sibling subtrees by roles/control types, remove text/token values, then compare fingerprints and repeated-area coverage.|Generic card cloning, repeated equal-sized sections and “three of everything.”|Catalogues, small multiples and comparison cards can be correct. Repetition is a diagnostic, not an automatic defect.|
|**DOM depth and breadth**|Record distributions as a low-cost smoke test.|Gross implementation changes and possible accidental nesting.|Primarily measures implementation conventions. **Do not use as a layout-diversity gate.**|

None of the three convergence/retrieval papers above establishes your proposed combination of grid-track ratios, first-viewport role allocation and repeated-card detection. Those are sensible **engineering extensions**, not methods to attribute to those papers.

### Making the clone check an assertion

Use two separate judgments:

NearClone(A,B)=similar structure∧similar dominance∧similar first viewport.\text{NearClone}(A,B) = \text{similar structure} \land \text{similar dominance} \land \text{similar first viewport}. CloneFailure(A,B)=NearClone(A,B)∧missing a required task-dependent difference.\text{CloneFailure}(A,B) = \text{NearClone}(A,B) \land \text{missing a required task-dependent difference}.

The thresholds require calibration on your own corpus. No cited paper provides defensible universal thresholds for your canonical regions.

Construct labeled calibration pairs: token-only changes; added wrappers; mirrored layouts; genuinely different grouping; linked selection/detail versus unrelated panels. Do not let trivial mirroring or spacing changes count as meaningful composition diversity.

Most importantly, add **counterfactual tests**:

|Brief mutation|Expected behavior|
|---|---|
|Change freight records to support tickets while preserving the same task relationships.|Topology may remain unchanged. Domain nouns alone should not demand novelty.|
|Change the task from resolving one exception to comparing several alternatives across shared attributes.|Assert the newly required comparison alignment/co-visibility—not merely a larger distance score.|
|Change passive monitoring to editing with a continuously visible reference.|Assert preserved reference context during editing.|
|Increase content from a handful of items to a large collection.|Assert capacity, navigation and overflow behavior; do not necessarily demand a completely new page topology.|

An assertion can establish that an expected relationship changed. A distance metric alone cannot establish that the change was warranted.

## 4. Risks, strong defaults and the role of priors

### Where the evidence counsels restraint

Scout’s results do not justify “diversity at guaranteed equal quality”: designers still encountered alignment, emphasis and balance problems and performed refinement. GRIDS exposed the cost of missing semantic grouping. Sketchplore’s selection benefit depended on excluding first encounters, and its optimized design was rated less symmetrical. These are demonstrations of useful tradeoffs, not evidence that free derivation always beats a strong conventional layout. ([Amanda Swearngin](https://amaswea.github.io/assets/scout/AmandaSwearngin_Scout_CHI2020.pdf "Scout: Rapid Exploration of Interface Layout Alternatives through High-Level Design Constraints"))

More broadly, the reviewed evidence is thin on **autonomously derived, multi-page production UIs evaluated against strong templates on real task outcomes**. Your rollout should test that comparison directly.

|Risk|Failure mechanism|Mitigation|
|---|---|---|
|**A larger catalogue disguised as a grammar**|`object=queue` and `activity=monitor` become another lookup key.|Ban direct field-combination → whole-page-template rules. Require relations between actual content regions and explicit constraint provenance.|
|**“Every dashboard must be unique”**|Distinct branding is mistaken for distinct work; familiar arrangements are rejected for looking ordinary.|Permit the same topology for the same task shape. Preserve shared application navigation. Judge unnecessary novelty as a cost.|
|**Optimizing proxies instead of work**|Symmetry, whitespace, low tree similarity or asymmetry becomes the objective.|Select lexicographically: feasibility → task fit → familiarity/effort → diversity as a tie-breaker. Never require asymmetry without a relational reason.|
|**Invented precision from an incomplete brief**|The agent fabricates volume, urgency, frequencies or peer groups to justify a layout.|Record unknowns and assumptions explicitly. Use a conservative prior when evidence is absent; do not manufacture content to satisfy geometry.|
|**Candidate generation becomes expensive decoration**|Three alternatives differ only superficially, or one clearly superior option is distorted to create others.|Hold content constant; compare region trees before implementation; allow fewer valid candidates.|
|**Responsive and live behavior invalidates a good screenshot**|Required context disappears on mobile; streaming updates move targets; empty or long-content states break hierarchy.|Compile breakpoint/state-specific constraints. Test reading order, keyboard progression, long content, empty states and live updates separately.|
|**The agent grades its own story**|It declares a region “primary” or “context-preserving” and its QA accepts the declaration.|Generate assertions from the brief-derived contract before coding. Check actual geometry and behavior; audit semantic annotations independently.|

### Keep Tidwell’s patterns as priors—not as prohibited defaults

Tidwell’s contextual pattern format is compatible with this approach. The problem is not having a two-panel selector or wizard available; it is selecting one without preserving the conditions that make it useful. ([O'Reilly Media](https://www.oreilly.com/library/view/designing-interfaces/0596008031/ "https://www.oreilly.com/library/view/designing-interfaces/0596008031/"))

The following are **proposed encodings**, not quotations from the book:

|Prior|Activation evidence and grammar|Named forbidden moves|Worked example|
|---|---|---|---|
|**Two-panel selector**|Repeated movement among records while retaining collection context. Compose a selector linked to a focus region; derive orientation and width from content and viewport.|**DetachedRail:** unrelated material occupies the “detail” region. **ContextReset:** selection destroys filter/scroll state.|A reviewer moves through disputed transactions while evidence remains linked to the selected item. No fixed sidebar width or obligatory KPI strip.|
|**Wizard**|Real prerequisites or a documented need for guided progression. Segment the dependency graph; preserve completed work and provide review.|**FalseSequence:** independent tasks are forcibly ordered. **ForcedReplay:** revising one answer requires traversing every prior step.|A quote cannot be computed until coverage inputs exist, but revising a contact field does not restart coverage selection.|
|**Hub-and-spoke**|Distinct, relatively infrequent activities with a meaningful return point. Provide task entry and preserved return state.|**HubTax:** frequent A→B switching always routes through the hub. **FakeOverview:** unrelated metrics are inserted merely to fill the hub.|An occasional-service portal routes users to independent applications; an operator’s repetitive workbench does not inherit that navigation.|
|**Canvas-plus-palette**|Creation or manipulation of a persistent artifact with tools and properties attached to it. Preserve workspace continuity and situate controls by scope.|**ChromeDominance:** navigation/tools displace the artifact. **CardifiedCanvas:** the artifact becomes a small card among unrelated summaries.|A floor-plan editor gives the plan the usable field; selection-specific properties need not become a permanent right rail.|

Each prior should therefore contain **activation evidence, relational invariants, forbidden moves, and an example with stated assumptions**. It should not contain immutable region counts, widths, section sequences or component inventories.

## What I would build

I would implement the replacement as four artifacts: a seven-field composition model; a sourced hard/soft constraint ledger; two or three candidate region trees; and independent rendered assertions plus clone diagnostics.

Evaluate **current menu versus grammar versus grammar-plus-QA**, keeping generation budget comparable. Include repeated runs and counterfactual brief pairs. Score task completion or independently assessed task fit separately from structural diversity; otherwise an ugly rearrangement can masquerade as progress.

The governing criterion should be:

> **Change composition when task-relevant relationships change; preserve it when only irrelevant surface facts change.**

That is a stronger objective than “avoid the same page shape.” It retains good defaults while making their use answerable to the brief.