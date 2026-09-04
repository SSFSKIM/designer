**I recommend replacing the menu with a constraint-producing composition grammar, while retaining patterns as conditional priors.** The evidence supports generating alternatives from explicit structure, emphasis, order, and relationships. It does **not** yet establish that an LLM can reliably infer those constraints from a brief, or that greater layout diversity improves task performance.

The strongest architecture is therefore: derive requirements; generate feasible compositions; evaluate task fit; use diversity to distinguish otherwise suitable alternatives.

Two findings materially affect your proposal:

- **“Hero” should ordinarily be an output of priority and content analysis.** Making it an input invites the agent to invent a dominant decorative region.
- **Design Theater’s released implementation does not recover hierarchical layout topology.** It constructs a flat tree of detected elements and compares bounding-box geometry. Its method is useful, but your clone check needs a stronger structural representation.

I inspected your current references without modifying them. The replacement also needs to address the default preference for asymmetry in [SKILL.md (line 56)](/Users/new/Developer/GitHub/designer/skills/designer/SKILL.md:56); otherwise that instruction will continue steering the new grammar.

The following distinguishes published findings from my proposed rules.

**The prior art supports different parts of the system—not one already-validated compiler.**

|Prior art|Variables read from task/content or designer input|Layout properties determined|Measured outcome|What it does not establish|
|---|---|---|---|---|
|[Scout, Swearngin et al., CHI 2020](https://faculty.washington.edu/ajko/papers/Swearngin2020Scout.pdf)|Supplied elements; hierarchy; ordinary, repeating, and alternating groups; order; emphasis; Keep/Prevent feedback.|Positions, sizes, arrangements, alignment, padding, ordering, and repetition under constraints.|With 18 designers, alternatives were **12% more spatially diverse**. Quality means were 5.37 versus 5.73 for the baseline; the difference was not significant.|Brief interpretation remained human work. “Similar quality” was **not an equivalence test**. Small mobile wireframes and expert visual ratings do not establish product-level task fit.|
|[GRIDS, Dayama et al., CHI 2020](https://userinterfaces.aalto.fi/grids/resources/chi2020-dayama-grids.pdf)|Rectangles, size bounds, canvas, partial placements, locks, grouping, placement preferences, and transition relations.|Mixed-integer optimization determines geometry, alignment, contiguity, traversal distance, and permitted placement. Generates alternatives and completes partial layouts.|A 13-person study found perceived quality tracked objective optimality. A separate 16-designer study showed adoption and usable authoring support.|No demonstrated improvement in downstream task performance; the designer study lacked a comparison condition. Complex hierarchies reduced suggestion relevance.|
|[Sketchplore/Sketchplorer, Todi et al., DIS 2016](https://www.kashyaptodi.com/data/SketchploreDIS2016.pdf)|Sketch geometry, element types, nesting, importance, and usage probabilities; simplified task inference from these inputs.|Local/global alternatives optimizing visual search, pointing, clutter, grid quality, and color harmony.|In a 20-person app-selection study, the optimized layout was faster **only after first encounters with each app were excluded**; the all-trials difference was not significant. Designer uptake was high in a separate small study.|Proxy optimization is not general task understanding. Familiarization mattered; semantic relationships and interaction dynamics were incomplete.|
|[Dashboard Design Patterns, Bach et al., 2022](https://arxiv.org/abs/2205.00757)|Requirements, users, tasks, and datasets are assumed upstream. Patterns were derived from 144 dashboards.|Forty-two combinable patterns across eight groups, including information, page layout, screenspace, multipage structure, and interaction.|A two-week workshop with 23 participants supported usefulness for discussing and developing designs.|Descriptive vocabulary, not a tested task-to-layout mapping. No controlled quality or task-performance comparison. Formal automation rules remain future work.|
|[Dashboard taxonomy, Sarikaya et al., 2019](https://alper.datav.is/assets/publications/dashboards/dashboards-preprint.pdf)|Purpose, decision horizon, audience, expertise, interaction, customization, alerts, benchmarks, and updates.|Describes seven dashboard types and conditional design considerations.|Eighty-three examples coded; initial agreement was 86.5%, κ=.64.|The authors could not operationalize several factors, including analysis tasks and layout arrangement. The taxonomy is useful upstream of composition, not an executable layout grammar.|
|[Lam & Munzner, 2010](https://www.cs.ubc.ca/sites/default/files/tr/2010/TR-2010-11_0.pdf)|Data levels, information needed to answer a task, cross-level clues, and interaction costs.|Single versus multiple levels; overview content; simultaneous versus successive views; embedded versus separate views.|Synthesizes **22 empirical studies** into conditional guidance. Simultaneous levels help when answers or clues span levels.|Guidelines remain qualitative; no universal space-allocation thresholds. Scope is multilevel visualization, not all application or marketing composition.|
|[Tidwell, _Designing Interfaces_](https://www.oreilly.com/library/view/designing-interfaces/0596008031/ch02s03.html)|Collection/detail relationships, manipulation, task progression, alternative access paths.|Conditional arrangements such as selector/detail, canvas/palette, drilldown, and wizard.|Accumulated design practice and examples; the inspected material provides no controlled diversity result.|Patterns mix abstraction levels. Tidwell explicitly distinguishes a wizard’s task sequence from its many possible physical presentations. A pattern need not prescribe one page shape.|
|[Brehmer & Munzner, 2013](https://www.cs.ubc.ca/labs/imager/tr/2013/MultiLevelTaskTypology/)|Why a task is performed, how, inputs/outputs, and interdependent task sequences.|Supplies an intermediate task description from which composition requirements can be reasoned about.|Demonstrates descriptive utility through a detailed case study.|No geometric compiler or measured generated-layout advantage. Particularly useful for avoiding confusion between user goals and interface mechanisms.|
|[Shneiderman, 1996](https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf)|Seven data types crossed with seven tasks, including overview, filtering, detail, relating, history, and extraction.|Organizes requirements for information exploration.|Taxonomy and system examples.|“Overview first” is a starting point, not evidence that every page should begin with a summary dashboard. It does not determine rails, grid ratios, or section counts.|
|[Mackinlay’s APT, 1986](https://www.cs.rpi.edu/~cutler/classes/visualization/F10/papers/p110-mackinlay.pdf)|Relations, functional dependencies, domain types, requested information, and priorities.|Composes graphical languages, rejects inexpressive encodings, and ranks effective ones.|Working generation system and worked examples.|This is chart/presentation synthesis. Transferring its **semantic validity before preference** architecture to whole interfaces is a useful analogy, not a demonstrated result.|
|[Stiny & Gips, shape grammars](https://ocw.mit.edu/courses/4-540-introduction-to-shape-grammars-i-fall-2018/pages/lecture-slides-and-supplemental-readings/)|Initial shapes, vocabulary, and transformation rules.|Generates families of spatial compositions.|Formal generative capability.|A grammar can generate an extensive family without knowing anything about task suitability. Diversity depends on its production rules.|
|[Van Duyne, Landay & Hong, _The Design of Sites_](https://www.oreilly.com/library/view/the-design-of/0131345559/ch06.html)|Site purposes and genre-specific needs.|High-level genres route toward finer navigation, content, task, and layout patterns.|Practice-based pattern language.|Category routing can reproduce your current failure if the intermediate reasoning is omitted. Genre is useful background evidence, not a sufficient layout selector.|
|[Rosenfeld & Morville, organization structures](https://www.oreilly.com/library/view/information-architecture-for/0596000359/ch05s04.html)|Content organization and relationships: hierarchy, database-oriented structures, hypertext.|Constrains navigation and access paths.|Conceptual framework with practice examples.|Information architecture does not uniquely determine visible page geometry. A hierarchical collection need not produce a permanent sidebar.|
|[Ngo, Teo & Byrne, 2003](https://shdl.mmu.edu.my/2562/)|Geometric screen features used in 14 aesthetic measures.|Scores properties such as balance, regularity, density, and rhythm.|Reports preliminary empirical support for aesthetic appraisal.|Does not establish task fit or diversity. Maximizing these scores can itself favor repetitive regularity. I could verify the institutional abstract, not the complete validation protocol.|
|[Rico](https://www.interactionmining.org/archive/rico) and [Enrico](https://userinterfaces.aalto.fi/enrico/)|Rendered mobile screens, view hierarchies, element properties, interaction traces; Enrico adds topic labels.|Enables retrieval, representation learning, and classification.|Rico demonstrates layout-similarity retrieval; Enrico curates 1,460 screens into 20 topics and evaluates classifiers.|Topic classification and corpus prevalence are not evidence that a composition suits a task. Using topic labels as grammar inputs risks reintroducing category templates.|

A bibliographic clarification: the verified **site-genres** source is van Duyne, Landay, and Hong. Wroblewski separately distinguishes visual personality from organization through meaningful grouping, sequence, and hierarchy—useful support for separating stance and composition. [Wroblewski’s account](https://www.lukew.com/ff/entry.asp?184=)

Bertin’s measurement/encoding distinctions, and the Fry/Card–Mackinlay–Shneiderman visualization tradition, help characterize information and representation. I would not count them as independent evidence for page-level layout rules. Also, I could not resolve the exact Bailey–O’Brien “Unraveling web design” citation; I would leave it out of the evidence base until its bibliographic identity is established.

**I recommend seven composition inputs, ranked below.**

These are a proposed engineering synthesis. They are **not seven independent statistical axes**, and their exact rules have not been validated as an LLM instruction system. Record evidence from the brief or content beside each value; preserve “unknown” when necessary.

|Rank and variable|Values to record|Properties it drives|Checkable rules|Collapses and dependencies|
|---|---|---|---|---|
|**1. Task and success condition**|Monitor/detect; investigate; compare/choose; configure; create/manipulate; transact; read/understand; browse/discover. Specify the answer or completed action, plus necessary task dependencies.|Primary workspace, action placement, required evidence, progression and reading order.|**Comparison:** required criteria remain aligned or directly comparable across the selected alternatives. **Dependent task:** prerequisites precede dependent actions in the interaction sequence; merely placing sections vertically does not satisfy this.|“Buy,” “read,” or “monitor” alone is too broad. Activity does not determine importance, volume, or presentation.|
|**2. Task-relevant information relationships**|Entities and attributes connected by sequence, hierarchy, cross-classification, network, spatial relationship, or claim/evidence dependency. Allow combinations.|Grouping, shared axes, containment, correspondence, ordering, linked regions.|**Sequence:** preserve the declared order. **Relationship-dependent answer:** expose the relevant relationship, rather than presenting its endpoints as unrelated cards.|Combine “primary object” and “relation model” here. A record can belong to a queue, timeline, map, and catalogue simultaneously.|
|**3. Required context co-presence**|Independent views; successive detail with recoverable context; overview/detail needed together; multiple peers needed together; editing with continuous feedback.|Separate versus integrated views, inspector placement, comparison regions, progressive disclosure.|**Cross-level answer:** required levels remain simultaneously available at the supported viewport. **Successive inspection:** returning from detail preserves selection, filters, and position.|Partly derived from the task, but worth making explicit: overlooking it changes topology substantially.|
|**4. Attention priority**|One focal object; ranked set; genuinely equal peers; stage-dependent focus. Identify what makes priority change.|Dominance, first-viewport allocation, ordering, subordinate regions, local density.|**Actionable exception state:** the highest-priority exception and its next action appear before unrelated summaries. **Peer set:** use consistent representational weight unless an explicit selection or status justifies a difference.|“Hero,” asymmetry, and focal-region size are consequences. Existing criticality stance informs this input but does not replace it.|
|**5. Working-set size and content shape**|Actual or bounded item counts; fields per item; text-length distribution; image dependence; aspect ratios; simultaneous comparison set; expected growth.|Repetition unit, table/list/grid suitability, scrolling, pagination, measures, region size.|**Attribute scanning:** repeated comparison fields align across instances. **Volume:** minimum, typical, and maximum fixtures retain access to required information without clipping or replacing real content with equal-length filler.|Page density is largely a consequence of this input, task frequency, display constraints, and stance. “Large dataset” does not necessarily mean a dense first viewport.|
|**6. Temporal behavior**|Refresh cadence, relevant time horizon, scheduling constraints, history needs, and whether updates change priority. These are separate fields, not mutually exclusive labels.|Freshness indicators, time axes, update stability, schedule regions, historical context.|**Live monitoring:** expose freshness/staleness for the monitored information. **Active interaction:** incoming updates must not move the selected target underneath the user without an explicit transition policy.|Live ≠ urgent. Historical ≠ chart-led. Scheduled data may need either a calendar or a sortable list, depending on the task.|
|**7. Traversal and return behavior**|Expected depth; frequent destination switches; repeated return to a collection; occasional drilldown; linear completion; exploratory movement.|Navigation persistence, local versus global controls, breadcrumbs, return paths, distribution across pages.|**Frequent route:** meet a declared interaction budget in a representative task trace. **Deep traversal:** retain location and a usable return path.|Often follows from information structure and task sequence. Keep it last; depth alone does not justify a sidebar.|

The strongest empirical support here is for **context co-presence**. Lam and Munzner connect simultaneous presentation to answers and clues spanning levels; they also document costs from unnecessary levels, excessive overview information, distortion, and coordinating separate views. They explicitly avoid numerical universal thresholds. [Full synthesis](https://www.cs.ubc.ca/sites/default/files/tr/2010/TR-2010-11_0.pdf)

Several proposed values need cleaning up before becoming skill vocabulary:

- **Queue, timeline, map, canvas, and catalogue mix domain structures with presentations.** Start with entities, relationships, and tasks. Respect an explicitly requested presentation as a constraint.
- **Reading order has multiple sources:** content dependency, task dependency, and attention priority. Resolve conflicts explicitly.
- **Grid/asymmetry, hero presence, card count, rail placement, and density distribution belong in the output.**
- **Viewport, accessibility, existing navigation conventions, and supplied references are boundary conditions.** They should not consume more composition-variable slots.

For your example rule, I would change “freshest exception-bearing region” to **“highest decision-priority exception.”** Recency alone can elevate a harmless new event above an older unresolved emergency.

**Use one shared composition language, with different task interpretation for marketing and operational interfaces.**

The shared language should express grouping, precedence, correspondence, repetition, visibility, co-presence, and space allocation.

For a landing page, derive those relationships from what the visitor needs to understand or evaluate: claim, evidence, eligibility, alternatives, objections, and commitment. For a product interface, derive them from task execution, state, selection, feedback, and recovery. These require different reasoning, but do not require two unrelated layout catalogues.

A hero then becomes an optional consequence: one artifact or claim may deserve the initial focus. An incident queue, comparison workspace, or reference document may need no hero region at all. This is my recommendation by synthesis, not a published comparison of one-grammar versus two-grammar systems.

Have each candidate describe:

1. Its task-bearing regions and information relationships.
2. What must remain together, what may be deferred, and the reading or interaction order.
3. The space allocation and repetition rule.
4. Its tradeoff against the other candidate.

Require a consequential structural difference—such as integrated versus separate detail, different valid grouping, or different disclosure—not merely different column fractions. Do not require three alternatives when the brief leaves only one credible structure.

**Mechanical diversity measurement needs to distinguish topology, geometry, and appearance.**

Here is what the named studies actually measured:

|Work|Actual representation and comparison|What the result establishes—and misses|
|---|---|---|
|[Goree et al., CHI 2021](https://aux.engineering.ucsc.edu/publications/Goree_Doosti_Crandall_Su-HomogenizationWebDesign-CHI21.pdf)|Screenshots recursively segmented along gutters/solid-color regions into **XY-trees**. Zhang–Shasha tree edit distance: insertion/deletion cost is region area; relabeling cost is the pixel-area symmetric difference between regions. Separate color and CNN appearance measures.|Hierarchical **visual segmentation plus geometry**, not DOM or task semantics. The corpus contained 227,802 homepage images from 10,482 sites. Reported convergence is observational; shared-library associations and interviews do not establish that libraries caused it.|
|[Design Theater, paper](https://arxiv.org/html/2607.22928v1)|Five tools × 24 tasks; standardized 1200×1200 screenshots. DHI has separate visual, color, and layout submeasures. TFS measures rationale implementation; PAS measures prompt-embedded principles.|Its principal comparison is **different tools on the same prompt**. That does not directly test whether one tool changes composition across different task structures. Raw visual, color, and layout distances have different scales and cannot be compared as interchangeable quantities.|
|[Design Theater, released layout code](https://github.com/kashifimteyaza/design-theater.io/blob/ef42be741998176b18117883470cd4e1001d6abf/pipeline/pipeline/stage4_layout.py) and [distance code](https://github.com/kashifimteyaza/design-theater.io/blob/ef42be741998176b18117883470cd4e1001d6abf/pipeline/pipeline/stage5_distances.py)|OmniParser detections become **one root with flat leaf children**. Area-weighted tree edit distance compares bounding boxes; element type and content are unused. Distance is normalized by summed node areas, including roots.|Useful geometric sensitivity, but no recovered nesting of semantic regions. Identical leaf counts have the same unlabelled tree topology despite potentially different compositions. This is a source-code finding at the linked revision; I did not reproduce the paper’s scores.|
|[Webzeitgeist, Kumar et al., CHI 2013](https://hci.stanford.edu/publications/2013/Webzeitgeist/webzeitgeist.pdf)|Render-time DOM is filtered and reparented into a **visual-containment hierarchy**. Elements carry geometry, relative sizes, sibling/order/depth, content, CSS, and vision features. Example retrieval uses learned similarity over descriptors.|Strong precedent for your representation. It is a mining/retrieval platform, not a canonical whole-page topology-distance metric or longitudinal diversity result. Its corpus has 103,744 pages; viewport and temporal variants were outside the original collection design.|

For your implementation, I would retain a **small vector of measures**, rather than collapse everything into one “diversity score”:

|Measure|Mechanical implementation|Catches|Misses or confounds|
|---|---|---|---|
|**Normalized region-tree edit distance**|Build a tree of meaningful rendered regions; discard implementation-only wrappers. Use stable role classes and declared edit costs.|Grouping, nesting, region insertion/removal, meaningful ordering.|Depends heavily on segmentation. A containment tree cannot express all coordination relationships.|
|**Typed relationship differences**|Compare edges such as contains, precedes, adjacent-to, controls, and reveals-detail-for, after matching region roles.|Structural relationships that trees miss; whether a rail is actually coupled to the main region.|Control relationships need markup or interaction evidence; geometry alone cannot establish them.|
|**Region count and area signature**|Record counts, normalized areas, and coarse positions at one consistent segmentation level.|Dominant workspace versus many equal regions; persistent shell versus main-content allocation.|Equal signatures can hide different topology. Area is only a proxy for perceptual weight.|
|**First-viewport composition**|Measure visible shares for navigation, title, task workspace, evidence, action, and repetition; account for clipping/overlays.|Oversized introductions and summaries displacing the actual task.|Misses content and relationships below the fold.|
|**Track and placement signatures**|Read computed tracks and actual child boxes; normalize widths, heights, and gaps.|Repeated 1:1 splits or identical multi-column geometry.|CSS Grid, Flexbox, and absolute positioning can render identically; declaration comparison alone is unreliable.|
|**Repeated-sibling signature**|Group siblings by normalized subtree shape and rendered dimensions; record run length, area share, and placement.|Repeated card scaffolds, three-stat rows, identical section sequences.|Tables, catalogues, and status walls may correctly repeat. Repetition is evidence, not an automatic defect.|
|**DOM depth/breadth**|Compute both raw-DOM and normalized-region distributions.|Cheap screening for structural sameness or unusual complexity.|Raw DOM largely reflects frameworks and wrappers. Use as a diagnostic, not a clone gate.|
|**Appearance embedding**|Screenshot embedding distance, optionally alongside a simplified region rendering.|Perceptual resemblance outside your structural features.|Fonts, imagery, and color can dominate. It cannot certify a topology change.|

Normalize viewport, content fixture, font loading, application state, and scroll position. Compare both the initial viewport and the whole surface at desktop and narrow widths. Treat an established application shell separately from the content workspace so legitimate shared navigation does not overwhelm the comparison.

Markup-only checks can inspect declared structure and repetition. They cannot establish final geometry, occlusion, responsive order, or visibility without rendering.

**Make the clone check a conditional assertion, not a universal distance threshold.**

Use paired briefs with a declared expected structural consequence:

- **Same task structure, different business domain:** substantial similarity may be correct.
- **Same domain, changed task structure:** test whether the required relationship changes.
- **Same task, alternative feasible solutions:** measure exploration diversity while requiring both to satisfy the task.

For example, change a brief from “read each record independently” to “compare three records against the same criteria.” The assertion is that the latter supports the required simultaneous comparison. A changed palette, extra wrappers, or a shifted sidebar cannot satisfy it.

Define the expected consequence **before generation**. Otherwise the agent can rationalize an unchanged layout after seeing it.

For near-clone detection, calibrate thresholds against labelled examples of:

- Structural duplicates with cosmetic changes.
- Different implementations of the same rendered composition.
- Genuine grouping or relationship changes.
- Legitimate reuse for equivalent tasks.

There is no source-backed universal tree-distance cutoff that separates “template clone” from “appropriate reuse.” An exact structural match can be detected mechanically; whether that match is a defect still requires the task comparison.

**The main risks concern the objective you give the grammar.**

|Risk|Evidence or mechanism|Mitigation|
|---|---|---|
|**A grammar simply becomes a larger template selector.**|“Map + monitor” can become as deterministic as “dashboard.”|Compile to relationships and constraints first. Preserve multiple feasible geometries. Avoid one input tuple mapping to one named layout.|
|**Diversity displaces usability.**|Scout’s diversity improvement did not establish quality equivalence. Sketchplore’s performance benefit depended on excluding first encounters.|Make task requirements and usability gates precede diversity. Include initial-use and repeated-use evaluation.|
|**Asymmetry becomes the new default.**|Your current workflow explicitly favors it.|Require unequal space to follow unequal requirements. Preserve equality for genuine peers and aligned comparison.|
|**“Every dashboard is unique” destroys useful consistency.**|Dashboard taxonomies describe different purposes; they do not imply that every instance needs novel interaction.|Preserve familiar navigation and interaction contracts. Vary composition only where task or content relationships warrant it.|
|**Priority inference creates decorative urgency.**|“Live” and “critical” can be incorrectly treated as synonyms.|Derive urgency from actual states and decisions. Test both exception and steady-state fixtures.|
|**Geometric proxies reward the wrong result.**|Regularity, density, and area cannot establish semantic importance.|Keep separate checks for relationships, visibility, interaction, and appearance. Never maximize a combined aesthetic score as a substitute for task fit.|
|**Candidate generation changes content to justify a layout.**|Shortening copy, removing fields, or adding decorative metrics makes almost any template appear appropriate.|Hold the information inventory and success conditions constant across candidates; document intentional disclosure.|
|**New prose produces more confident rationalization.**|Declared constraints can remain unimplemented.|Attach each mechanical rule to actual regions and test states. Verify the result, not the explanation.|

Keep Tidwell-style patterns in the form you proposed: **prior, conditions, grammar consequences, forbidden moves, worked example**. The forbidden moves below are my proposed guardrails, not quotations from Tidwell.

|Prior|Applicable condition|Invariants to preserve|Named forbidden move|
|---|---|---|---|
|**Two-panel selector**|Repeatedly inspect members while retaining collection context.|Selection correspondence, useful detail space, preserved collection state.|**Disconnected detail:** the detail region does not identify or follow selection.|
|**Wizard**|Meaningful dependencies or guided progression warrant sequencing.|Valid progression, recoverable prior work, appropriate review.|**Artificial serialization:** independent settings are forced through a long sequence solely to create a wizard.|
|**Hub-and-spoke**|Users repeatedly return to a common launch point between independent destinations.|Reliable return and orientation.|**Forced hub detour:** frequent lateral work requires unnecessary trips through the hub.|
|**Grid of peers**|Entities genuinely share comparison status and representation.|Consistent encoding and sufficient information for the intended comparison.|**False equality:** unrelated summaries, urgent exceptions, and ordinary entities receive identical treatment.|

A worked example should demonstrate how requirements produced these invariants and which alternatives remained plausible. Fixed ratios, section counts, and CSS recipes would make it too easy to copy the example’s answer.

The next investment I recommend is a controlled comparison of **the current menu**, **grammar with one candidate**, and **grammar with alternatives plus composition QA**. Hold stance, content, model configuration, and generation budget comparable; use repeated runs and previously unseen briefs. Measure requirement compliance, structural responsiveness to changed tasks, and task performance separately. That experiment would determine whether the improvement comes from better derivation, broader exploration, or verification—and whether it preserves the advantages of strong defaults.