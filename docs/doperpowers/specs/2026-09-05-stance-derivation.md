# Stance layer re-founded on derivation

**Status:** in progress. **Supersedes** the stance-layer doctrine in
`docs/doperpowers/specs/2026-07-23-figma-design-skill-design.md` ("five complete systems", "port
intact", the as-is / variant / derive-fresh mapping tiers). Extends the project-wide principle
adopted in `docs/doperpowers/specs/2026-07-27-persona-layer-design.md` (open possibility space
with derivation rules, not mandates) from the persona layer to the stance layer. Research basis:
`docs/research/2026-09-05-stance-axes-prior-art.md` (prior art, ranked axis set, generative-diversity
evidence, risks) and two further research rounds summarized in the Decision Log.

## Purpose

After this change, a person can hand the skill two briefs from the same product category — a
hospital pharmacy inventory console and a wind-farm operations console, say — and receive two
designs that each fit their own product: different accent hues argued from each product's world,
different type choices argued from each product's reading conditions, and a `DESIGN.md` that
records the derivation and the road not taken. Today they receive the same orange, the same three
fonts, and the same 48px display size, because the stance step is a catalogue whose values are
forbidden to move.

A person can also commit the skill to a stance that no library names, and — when a translucent
material genuinely is the right answer for a product — ship Apple-style liquid glass through this
repository's own vitrea runtime with honest fallbacks, instead of being told the material layer is
"outside this skill's scope".

How to see it working: the Acceptance section, run end to end.

## The measured problem

Audit of `skills/designer/` on 2026-09-04, against the eval builds under
`figma-design-workspace/` (gitignored, local evidence):

- **The same accent hex ships across unrelated products.** `#D46B2C`, the Precision industrial
  accent, is in the freight-rail dispatch console, the home-energy settings app, the
  customer-support triage console, and the gym class-booking page. The Archivo + Inter + Geist Mono
  triple is in seven builds. `references/stances.md` step 2 said: "port that system's token block
  into the project with all values intact — do not reweight a hex".
- **Precision industrial is the single most common outcome** (4 of ~25 non-persona builds). Every
  other stance appears once or twice. Any operational or high-trust brief lands there, and once it
  lands, fit is prohibited.
- **The mapping table split 18 sampler names into three tiers**: 3 "use as-is", 3 "variant",
  12 "derive fresh". A draw of three names contains at least one as-is or variant pull 73% of the
  time. The derive-fresh half produced genuinely product-specific work (terminal, risograph,
  luxury-fashion, topographic, deco, vernacular, Frutiger Aero). The as-is half produced clones.
- **Every downstream table was keyed to the five names.** Accent chroma limits
  (`color-engineering.md`), voice postures (`voice-copy.md`), motion bands (`motion.md`), component
  character (`stances.md`), the two operational type scales (`typography.md`). A stance derived
  fresh found no row anywhere, so the cheapest path was always a canned one.
- **The catalogue was constant on the axes that matter most for fit.** Converted to OKLCH
  (research memo §0): every one of the five grounds is light (L 0.93–0.975), every spacing scale
  is the identical 4/8/12/16, and three of five accents sit in the terracotta hue band (35–48°)
  that `taste-calibration.md` names as the first AI default. The catalogue varied on hue family,
  type family, radius and easing — the choices that least affect fit — and was constant on density
  and lightness, the two on which a dispatch console and a gym page should differ most.
- **Material was an afterthought by construction.** Material effects lived in workflow step 8, the
  craft pass, after layout and tokens. `effects-policy.md` said building a real material layer is
  outside the skill's scope. The skill had zero mentions of vitrea, the material runtime in this
  same repository. A liquid-glass system changes the component canon, the plane model, and how
  controls sit over content; it cannot be added after the fact.

**Precedent.** The persona layer hit exactly this defect on 2026-07-27: all three persona arms
shipped byte-identical cream and leaf-green because `personas/essentialist.md` said "copy it in
whole". The fix — "structure carries the law; the home values are one worked instantiation;
derive the accent hue and ground temperature per product, and record one rejected candidate" —
was verified by a hue-discrimination probe the same day. The stance layer was never brought under
that principle. This spec does that.

**Mechanism.** The research memo names why a verbatim token block clones: concrete exemplars
transmit their surface (Min et al. 2022; Wadinambiarachchi et al. CHI 2024: a reference
propagated about a third of its features into designers' work), and the same example stated
abstractly reduces fixation (Ezzat et al. 2020). A hex block is the most concrete exemplar
possible. A derivation stated in criteria is the abstract form of the same knowledge.

## Terms

- **Stance.** A committed visual system: the brief's position on two constraints and seven
  coordinates (below), the values derived for this product from that position, one signature
  element, and the road not taken. Not a mood, and not a name.
- **Constraint.** A property the brief fixes and the design does not choose: density and
  criticality. Category is allowed to speak here.
- **Coordinate.** A property the design chooses for the product, nudged by sampled ingredients:
  energy, type, material model, color commitment, accent job, ground lightness, ground temperature. Category may bias a coordinate; it
  never picks a value.
- **Value.** A concrete token: a hex, a family name, a size, a duration. Always derived for this
  product, never inherited from a name or a worked derivation.
- **Worked derivation.** A complete token system shown together with the product it was derived
  for, its axis position, and the reasons behind its values. The five "complete systems" become
  five worked derivations. An exemplar of the method, never a template.
- **Named stance.** A library entry — a name, reference exemplars, a prior over the coordinates, a
  composition grammar, forbidden moves, a signature — offered by the sampler as a starting
  position. It contains no hex and no mandatory family. Adopting one still derives every value.
- **Compatibility rule.** A stated interaction between two axis positions (dense × glass,
  consequential × exuberant) that resolves what a naive per-axis lookup would get wrong.
- **Material model.** The coordinate that says what a surface is made of and how layers are shown:
  printed, tonal, elevated, or glass over planes.
- **vitrea.** The TypeScript runtime in `packages/` that replicates Apple's Liquid Glass on the web
  (WebGPU tier with a CSS tier, resolved per group and reported honestly). Published as
  `@vitreajs/vitrea`, `@vitreajs/vitrea-web`, `@vitreajs/vitrea-react`.

## Design

### Two constraints the brief fixes, seven coordinates the design chooses

The prior art (Kansei engineering, Scout, morphological analysis, IBM Carbon, SAP Fiori, Material,
Apple HIG; memo §1) supports a *typed, constrained design space*, not seven independent sliders.
Two properties are read off the brief and never sampled. Seven are chosen for the product (energy,
type, material model, color commitment, accent job, ground lightness, ground temperature — nine
lines in `DESIGN.md` §0 with the two constraints). Each has discrete, named rungs; none has an unlabelled default; two deliberately have no middle rung
(midpoint attraction is a measured LLM behavior, memo §4).

| Axis | Kind | Rungs | What decides it | Token families it owns | Checkable starter rules |
|---|---|---|---|---|---|
| **Density** | constraint | spacious / standard / dense | The user's verb (read or browse → spacious; operate on rows, monitor, fix → dense), session length, viewport. Standard is a real product default, chosen by task and recorded. | Control and row height, spacing base and steps, gaps, label placement, containment method, type-scale ratio. **Not** body size by itself. | Dense: control height 28–32, rows ≤ 36, steps favour 4/8/12/16, labels inline, containment by hairline or tone, accent coverage ≤ 5%. Spacious: controls 40–48, steps favour 8/16/24/32/48, labels above fields, scale ratio ≥ 1.25. Body size is a type decision made *within* the density (dense permits 13–14px with a reason; density never silently shrinks type — SAP Fiori compact keeps font size and shrinks geometry). Touch targets never below the platform floor. One density per view hierarchy. |
| **Criticality** | constraint | exploratory / transactional / consequential | Whether actions are reversible, audited, safety- or money-relevant, regulated. Trust is an outcome of this plus craft, not an axis. | State redundancy, contrast floors, destructive-action treatment, transparency permission on task surfaces, motion caps, copy directness, confirmation and recovery. | Consequential: no state communicated by hue alone; the accent never doubles as warning, danger, or success; primary task surfaces opaque; no overshoot on error or confirmation motion; irreversible actions confirmed or recoverable; error copy literal and actionable. |
| **Energy** | coordinate | quiet / composed / lively / exuberant (no middle) | Stakes and the user's frame of mind, and what the brand can carry. Not "the brand is fun". | Accent chroma ceiling, heading-to-body contrast, size jumps, radius and shape language, illustration licence, motion amplitude and overshoot permission, copy enthusiasm ceiling. | Quiet: accent C ≤ 0.15, control radius ≤ 6px, no overshoot, at most one high-salience treatment per viewport. Lively and above: C up to 0.22, radius ≥ 10px or a declared shape language, at most **two** simultaneous expressive channels (chroma + shape, not chroma + huge type + spring + decorative shadow). Overshoot is a separate recorded yes/no. Energy sets a chroma *ceiling*; it never raises chroma by itself. |
| **Type** | coordinate | a tradition (the 13 in `ingredients.json`) as the nominal value, plus **criteria** | Energy, the product's world, and what must be legible at what size. | Display, UI, and mono selection; family count; weight range; numerals; tracking; case. | The stance records *criteria* — x-height, terminals, width, weight range, tabular numerals, whether a display face is licensed — never a family name; families are chosen at derivation under `typography.md`'s derive-first / swap-one-slot rule. Family count by density (one plus mono at dense; two at standard; three only with a real data role). Display class sits inside energy (quiet: grotesque, humanist, geometric, slab, transitional; lively: any). Script and display faces never for body or UI. |
| **Material model** | coordinate (categorical, with compatibility rules) | printed / tonal / elevated / glass over planes | Whether anything genuinely sits above changing content, whether the product's world has physical layers, whether the surface is a printed thing. | Border system, shadow tiers, surface stepping, radius tendency, texture, `backdrop-filter`/vitrea. | Printed: no shadow except a modal. Tonal: ≤ 3 surface steps, shadow only on floating UI. Elevated: ≤ 3–4 named tiers, floating UI only. Glass: floating control layer only, never nested, never in the content layer, opaque fallback. Not a slider: glass is not "more elevation". `references/material.md`. |
| **Color commitment** | coordinate | restrained / committed / full palette / drenched | Whether color is the brand's carrier and what the surface is for. Already in `taste-calibration.md`. | Accent coverage, number of color roles, whether the ground may be chromatic. | Restrained ≤ 10% chromatic surface; committed 30–60%; full palette 3–4 roles each with a job; drenched only for hero and campaign moments. Chroma ceiling comes from energy, coverage from commitment. The **accent's job** (none / status-only / directional / atmospheric) is a recorded decision on its
own line, not a sampled axis: exactly one primary job, and a directional accent never doubles as danger, warning, or success. |
| **Ground** | coordinate, recorded as two lines (ground temperature, ground lightness) | temperature: warm / neutral / cool / brand-tinted × lightness: light / dark | Temperature from the product's material world. Lightness from the physical-scene sentence — never from energy or criticality (dark reads heavy and dominant, not sober). Both modes are derivable from one role set. | Neutral ramp hue, background lightness, border and shadow tint, dark-mode derivation. | All neutrals in one hue family within ±20°, C ≤ 0.02 (≤ 0.04 brand-tinted). A cream-band ground (L 0.84–0.97, C < 0.06, h 40–100) needs a named justification; warm at dark or mid-tone is first-class. Dark: elevation by lighter surfaces, shadows demoted to overlays, accent L ≥ 0.62. |

**Derived by resolvers, not axes.** Motion (energy supplies amplitude and character; density
supplies speed pressure; criticality caps overshoot and ambiguity; material supplies the spatial
model), radius (energy × density), border weight (material × density), voice (energy × criticality;
formality rises with criticality), the light/dark pairing (both modes from one role set). Each gets a
table keyed by the axes, so any derived stance finds its row.

**Not axes.** Trust and seriousness (outcomes of criticality, craft, and quiet energy; QA floor).
"Premium" and "professional" (underspecified brief words; decompose them). Playful ↔ sober
(energy under another name, conflated with criticality and formality). Motion register (a
resolver). Accent job (a recorded decision). Layout (a separate composition grammar; see Deferred).

**Compatibility rules.** Per-axis lookups are not additive; the joint result is what ships.
Stated rules resolve the known collisions:

| Combination | Resolution |
|---|---|
| dense × glass over planes | Glass only on small persistent navigation or controls; primary data surfaces opaque. |
| consequential × lively or exuberant | Emphasis stays in type and color; no humorous copy, no bounce, no ambiguous state transitions. |
| dense × characterful display face | The display face appears in one overview region; operational components keep instrumental text. |
| dense × full palette or drenched | On task surfaces, refused; on chrome and overview, confined there; no continuous tint behind tabular data. Density is information density, not visual layering. |
| dark × elevated | Resolves to tonal plus shadow demoted to overlays; elevation is drawn by lighter surfaces. |
| consequential × any | No glass on primary task surfaces; no overshoot on error or confirmation; no hue-only state. |
| restrained × exploratory | Neutral primary actions are allowed, but focus and selection stay unmistakable. |
| warm × light | Lands in or near the cream band; needs a justification or the warmth moves to accent and imagery. |

### The derivation procedure

Replaces "look up the name, port the block":

1. **Read the constraints off the brief**: density and criticality, one line each with the
   reason. Category is allowed to speak here.
2. **Write two candidate coordinate vectors**: the modal one (what the category expects) and one
   non-modal alternative that still fits the product. The sampler's ingredients and, optionally, a
   named stance are the material for the second. Reject anything the compatibility rules forbid.
3. **Choose, with reasons, and record the rejected vector.** A vector on the category's modal
   position at every coordinate must then carry its distinctness in the values and the signature.
4. **Derive the values from the product's own world.** Accent job first, then accent hue from
   product meaning with one candidate hue weighed and rejected; ground from the scene sentence with
   one rejected alternative; type from the criteria under the derive-first rule; radius, border,
   shadow from the material model; spacing and geometry from density; motion, voice, and the
   light/dark pairing from the resolvers. Override the framework's defaults explicitly (Tailwind and
   shadcn radii, grays, and shadows are the layer beneath the tokens and will show through
   otherwise).
5. **Write the commitment as base plus tension**: "quiet operational typography on a planar cool
   ground, interrupted by one directional amber signal." The tension is the signature element.
   "Modern, clean, trustworthy" has neither.
6. **Run the clone check** before code: would this `DESIGN.md` come out the same for a different
   product in the same category? Same constraints are expected. Same coordinates are plausible.
   Same values are the tell; re-derive.
7. **Record it** in `DESIGN.md` §0: the nine axis lines (density, criticality, energy, type,
   material model, color commitment, accent job, ground lightness, ground temperature) with
   reasons, the rejected vector, the two rejected values, the signature.

**Ingredients are bounded mutations.** Each sampled ingredient must map to a coordinate, a
composition rule, or a component treatment; it may change one or two decisions, never import a
whole visual system; it survives the same compatibility and fit tests; and the record says why the
mutation helps this product. The sampler stays, at its current draw shape, for the job the evidence
gives it — escaping the modal answer.

### What happens to the five systems

They stay, as worked derivations. Each keeps its token block, now prefixed with the product it was
derived for, its axis position, and a paragraph on why these values for that product. The rule
"port with all values intact — do not reweight a hex" is deleted. Its replacement: values from a
worked derivation may be reused only after re-derivation for the product at hand, with the reasons
recorded; byte-identical reuse across unrelated products is the clone tell the QA pass looks for.
This is the same move `typography.md` made for its ten pairings ("method illustrations, not a
menu") and `personas/essentialist.md` made for its home token system.

### The library

All 18 named stances in one table, in derivation vocabulary: prior over the coordinates (the
constraints a stance usually implies are noted, not fixed), signature, composition grammar,
forbidden moves, reference exemplars, and type *criteria* rather than family names. The as-is /
variant / derive-fresh tiers are gone. A named stance is a prior and a grammar with character; the
derivation governs the values. Archetype = prior and grammar. Brief = evidence. Resolved stance =
product-specific derivation.

### Unnamed stances

`SKILL.md` and the closing rule of `stances.md` state it: the committed stance may be one the
library has never named, provided `DESIGN.md` carries the full derivation. The sampler card is
Figma's verbatim tool output and stays byte-identical (Decision Log); the licence lives in the
skill body.

### Downstream tables re-keyed by axis

- `color-engineering.md`: ground sections by temperature × lightness (done); the accent's job
  (done); accent chroma limits by energy, with the dark-ground adjustment as a row.
- `motion.md`: the resolver — bands by density × energy, criticality caps, overshoot as a flag;
  the intro no longer says "port that system's motion block".
- `voice-copy.md`: voice by energy × criticality; the four examples relabelled by axis position.
- `typography.md`: the two operational scales become the dense and spacious positions with
  families marked as instantiations; family count by density; criteria vocabulary for the type
  coordinate.
- `effects-policy.md`: material model decided at stance time; glass routes to `material.md`
  (done).
- `guidelines-authoring.md`, `qa-protocol.md`, `taste-calibration.md`: axis lines, clone check,
  category-predicts-positions-not-values (done; axis names updated).

### Material model and vitrea — `references/material.md` (done)

One file for the coordinate: the four models with their token consequences and checkable
consequences, when glass is earned, the design-time constraints (planes, content-layer
prohibition, labels stay real DOM, honest hints, group spacing), and the vitrea contract written
from the library's own documentation (`docs/research/vitrea-designer-contract.md`): the two tiers
and the reported `GlassGroupState`, the accessibility split, the browser truth, the verified
single-file path over esm.sh, and the CSS path when the stack cannot host a module. The skill stays
runtime-neutral: vitrea is the named path when the stack can host it, CSS glass when it cannot, and
`DESIGN.md` records which and why.

### Component character moves to its own file (done)

The three component-character implementations (~570 lines of `stances.md`) moved to
`references/component-character.md`, routed from `SKILL.md` at the build step where they are
used.

### Persona layer

Unchanged. `personas/essentialist.md` is already derivation-based, and its Part 5 is the template
for the wording here.

### Files

| File | Change |
|---|---|
| `skills/designer/references/stances.md` | Rewrite: the axes, compatibility rules, derivation procedure, five worked derivations, the library in derivation vocabulary, closing rule. |
| `skills/designer/references/component-character.md` | New (done): the three implementations, moved, with a preface. |
| `skills/designer/references/material.md` | New (done). |
| `skills/designer/SKILL.md` | Done: parse step reads constraints and places coordinates; "derive and commit"; unnamed stances licensed; clone check in step 8; taste-floor rule "values are derived, never ported"; routing for the two new files. |
| `skills/designer/references/color-engineering.md` | Ground and accent-job sections done; chroma table by energy pending. |
| `skills/designer/references/motion.md`, `voice-copy.md`, `typography.md` | Re-key by axis (pending). |
| `skills/designer/references/effects-policy.md`, `guidelines-authoring.md`, `qa-protocol.md`, `taste-calibration.md` | Done. |
| `skills/designer/personas/TEMPLATE.md` | One reference to "complete systems" reworded. |
| `README.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Done: wording, reference count, version 2.0.0. |
| `evals/evals.json` | Evals 7–9 added. |
| `docs/doperpowers/specs/2026-07-23-figma-design-skill-design.md`, `2026-07-27-persona-layer-design.md` | Revision note pointing here. |

## Acceptance

All commands run from the repository root. Builds go under `figma-design-workspace/derivation-eval/`
(gitignored, like every other eval workspace; briefs in `briefs.md` there). Each build is a fresh
agent given only the brief and the skill.

**A1 — Category-clone divergence.** Two briefs, one category, built independently:

- Brief P: "Design a desktop inventory console for a hospital pharmacy: stock levels by drug,
  expiring lots, controlled-substance counts, pending orders. High-trust, used all shift. Single
  HTML file with realistic data."
- Brief W: "Design a desktop operations console for a wind-farm operator: turbine status, power
  output, curtailment orders, maintenance crews. High-trust, used all shift. Single HTML file with
  realistic data."

`bash figma-design-workspace/derivation-eval/assert-derivation.sh pharmacy windfarm` prints `PASS`
for both and exits 0 when: (a) neither build's `--accent` resolves to any of the five worked
derivations' accent values (`#D46B2C`, `#A9462D`, `#B65A3C`, `#2B7B78`, `#FFB94D`) — the clone
tell; (b) the two builds' accent hues differ by at least 30° in OKLCH, or `DESIGN.md` names the
shared hue with a product-specific reason; (c) each `DESIGN.md` §0 carries the nine axis lines
(density, criticality, energy, type, material model, color commitment, accent job, ground lightness,
ground temperature), a rejected coordinate vector line, a "rejected" line
for the accent hue and one for the ground, and a named signature; (d) no `backdrop-filter` in
either build; (e) the sampler was run and its draw recorded. Expected: both land at dense /
consequential (quiet is the likely energy, not a requirement); the coordinates may match or differ;
the values differ.

**A2 — Brief authority holds.** Eval 6 ("meditation app in a warm editorial style with a cream
background, serif display type, and terracotta accents") rebuilt: the build's background is in the
cream band, the display face is a serif, and the accent is a terracotta. Derivation does not
override an explicit brief.

**A3 — Material routing.** Brief G: "Design a desktop music player: album artwork fills the window
and the transport controls, queue, and volume float over it. Single HTML file." `DESIGN.md`
records `material model: glass over planes` with the reason (controls over changing artwork), names
the implementation path (vitrea via an ES module, or CSS glass with the reason vitrea was not
used), and the build passes the ten pre-delivery checks. If vitrea is used, the page still renders
readable controls with WebGPU unavailable.

**A4 — Nothing else regressed.** `node --test skills/designer/scripts/*.test.mjs` passes
unchanged (the sampler is untouched). `claude plugin validate . --strict` passes.

**A5 — The doctrine is gone from the runtime files.**
`grep -rn -i "all values intact\|use as-is\|port that system\|five complete systems" skills/designer`
returns nothing.

**A6 — Human grid.** Full-page screenshots of A1, A2 and A3 assembled into one review page and sent
to the user. The persona-layer retrospective is explicit that cross-build monoculture is visible
only to a human viewing the grid; this is a first-class step, not a nicety.

## Decision Log

- Decision: Re-found the stance layer on derivation — two brief-fixed constraints and five
  coordinates with compatibility rules — keeping the five systems as worked derivations and the 18
  names as priors and grammars.
  Rationale: The audit shows fit is prohibited exactly where values are forbidden to move; the
  persona layer proved on 2026-07-27 that "structure carries the law, values are a worked
  instantiation, derive per product with a rejected candidate" removes monoculture without losing
  character. Rejected: (a) keep the catalogue and add more systems — more templates, more clones;
  (b) delete the five systems — a complete worked instantiation is the strongest teaching device
  the skill has; (c) only delete "port intact" — with every downstream table keyed by the five
  names, the gravitational pull would remain.
  Date/Author: 2026-09-05, Claude (user-approved direction 2026-09-04).

- Decision: The axis set is two constraints (density, criticality) and five coordinates (energy,
  type, material model, color commitment, ground), amended from the first draft's six axes
  (ground, density, register, color commitment, typographic tradition, material model) after three
  independent research rounds converged.
  Rationale: The three rounds (GPT-5.6 Pro; the memo at
  `docs/research/2026-09-05-stance-axes-prior-art.md`; a third synthesis) agreed on: (1) density
  and criticality are read off the brief, not sampled; (2) "trust" is an outcome, not an axis —
  replace with criticality, which has checkable consequences; (3) "register / playful ↔ sober"
  conflates activation, formality, and criticality — replace with energy, four rungs, no middle,
  because midpoint attraction is measured LLM behavior; (4) type stores criteria, never family
  names, or the three-family fingerprint returns one level down; (5) material is categorical with
  compatibility rules, not a flat → glass slider; (6) ground lightness is chosen by scene, never by
  energy, and is a separate decision from temperature; (7) motion and voice are resolvers; (8)
  named archetypes survive as prior + grammar + forbidden moves + worked examples with zero
  protected hex. Rejected: a separate motion axis (duplicates energy × density × criticality unless
  motion is the brand asset); a separate copy-exuberance control (derived from energy ×
  criticality); accent job as a sampled axis (a role decision, recorded on the color-commitment
  line); a social-posture axis (not yet needed by the corpus; would replace ground temperature if
  it ever is).
  Date/Author: 2026-09-05, Claude.

- Decision: Material model is a coordinate decided in the parse step, not a craft-pass effect.
  Rationale: A glass system changes the component canon, the plane model, and how controls sit
  over content. It cannot be layered onto a finished flat page; `effects-policy.md`'s "one material
  moment" rule still governs how much of the page carries it.
  Date/Author: 2026-09-05, Claude.

- Decision: vitrea is routed, not embedded. `material.md` gives the contract and the two
  implementation paths; the skill stays runtime-neutral.
  Rationale: The plugin loads nothing from `packages/` (repo law, `CLAUDE.md`). The vitrea design
  spec's Decision Log #2 chose fidelity-first and deferred skill integration; this is that
  integration, done at the doctrine level. Rejected: shipping vitrea snippets as the skill's glass
  recipe (couples the plugin to a library version) and leaving glass CSS-only (the runtime exists
  and reports its tier honestly, which is a better answer to "the fallback is the design" than a
  hand-written CSS fallback).
  Date/Author: 2026-09-05, Claude.

- Decision: The sampler card stays byte-identical; ingredients are bounded mutations; the licence
  for unnamed stances lives in `SKILL.md` and `stances.md`.
  Rationale: The card is Figma's verbatim tool output and the 2026-07-23 spec's replica identity
  rests on it; its test pins the frame. The evidence (memo §3: random surface injection transmits
  almost nothing to output, 0.003 versus 0.46–0.55 for specification-level variation; guided
  stimuli beat random for generating, random is good at removing blocks) gives the sampler exactly
  one job — escaping the modal answer — and says its draws must map to decisions rather than
  import systems. Axis-position sampling is deferred: no evidence yet says it breaks defaults
  better, and the named pool carries reference exemplars the axis space lacks.
  Date/Author: 2026-09-05, Claude.

- Decision: Two candidate vectors, modal and non-modal, before commitment; the rejected vector is
  recorded.
  Rationale: The evidence favours surfacing a non-modal candidate (verbalized sampling, 1.6–2.1×
  diversity) and against letting a single exemplar dominate (fixation). Three rendered candidates
  compared as thumbnails, as one research round proposed, is the stronger form but assumes a
  rendering path the skill cannot rely on; two written vectors is the form that runs blind.
  Date/Author: 2026-09-05, Claude.

- Decision: Component character moves to `references/component-character.md`.
  Rationale: 570 lines of implementation code were loaded at the stance step where they are not
  used; they are used at the build step.
  Date/Author: 2026-09-05, Claude.

- Decision: Named stances are kept as priors with a signature and a grammar, not dissolved into
  pure parameters.
  Rationale: The known risk of parametric derivation is averaged, bland output, and a handful of
  scalar positions cannot reconstruct the joint gestalt a name like Swiss or Memphis carries. A
  name with reference exemplars anchors character; the derivation governs values. Shape grammars
  are the precedent: a style is a rule system that generates a class of designs, not a frozen
  output.
  Date/Author: 2026-09-05, Claude.

- Decision: Version 2.0.0.
  Rationale: The doctrine every `DESIGN.md` is written against changes shape (nine axis lines,
  rejected vector and values, signature); values in older `DESIGN.md`s ported from a system are now
  a QA finding. That is a contract change for the plugin's users.
  Date/Author: 2026-09-05, Claude.

- Decision: First external review round (2026-09-05, Codex `gpt-5.6-sol` at xhigh over
  ac06488) — eight findings, all confirmed, all fixed in one wave. (1) The derivation step
  overrode the existing-design-system and persona routes; both branches now say what the nine
  lines record. (2) "Same axis position is expected" froze the seven chosen coordinates and
  contradicted `stances.md` and eval 8; the clone check everywhere now reads *same constraints
  expected, same coordinates plausible, same values the tell*, and eval 8 no longer demands a
  coordinate to differ (forcing divergence over fit is the research's risk 7). (3) The
  `DESIGN.md` skeleton omitted the rejected coordinate vector and the routed examples were v1
  records; the skeleton now requires it, `reference-implementation/DESIGN.md` is rewritten in
  the v2 shape, and the two Figma transcripts carry a banner saying they predate the record.
  (4) Three library rows (bauhaus, luxury-fashion, deco) could not be expressed in the
  accent-job enum; the axis gains a `none` rung (a monochrome interaction language with a
  visible non-color focus) and every row maps to one job. (5)–(7) Three vitrea facts were
  wrong against 0.6.0: group spacing is at least the larger group's *effective* sampling
  padding (derived from the resolved blur), not the sum of two 24px defaults; `GlassGroupState`
  carries an optional `cssBody: "two-layer" | "collapsed"`; and `createGlassRoot()` defaults to
  the CSS renderer, so the vanilla path must pass `{ renderer: "webgpu" }` to reach the GPU
  tier. (8) `SKILL.md` frontmatter still said 1.1.0.
  Rationale: none of the eight was minor enough to log as debt — each would have produced a
  wrong `DESIGN.md` record or a wrong statement about the runtime in shipped builds.
  Date/Author: 2026-09-05, Claude.

- Decision: Second external review round (2026-09-05, Codex `gpt-5.6-sol` over 33fc55e) — five
  findings, all confirmed and fixed: the adoption and persona routes carried into the authoring
  skeleton, the workflow step, and the QA clone check; the canonical example's accent made to obey
  one job (status-only, with focus moved to the primary) and its type line made criteria-only; the
  DPR claim removed from the proxy-spacing rule (the runtime projects the group blur at a fixed
  scale); A1 and the assert script synchronized with the revised contract (rejected vector
  required, coordinates may match).
  Rationale: each was a contract inconsistency a builder could follow into a wrong record; none was
  minor enough to log as debt. Review is converging — the second round found only follow-through on
  the first.
  Date/Author: 2026-09-05, Claude.

## Surprises & Discoveries

- Observation: The persona layer had already found and fixed this exact defect class in July.
  Evidence: `2026-07-27-persona-layer-design.md` Decision Log — "all three persona arms shipped
  byte-identical hex values … Part 4 said 'copy it in whole'"; the fix and the hue probe that
  verified it. The project-wide principle adopted then was never applied to `stances.md`.

- Observation: The clone is mechanical, not stylistic — the identical hex, not a similar look.
  Evidence: `grep -rl D46B2C figma-design-workspace` → rail dispatch, energy settings, support
  console, gym booking.

- Observation: The catalogue was constant on the two axes that matter most for fit.
  Evidence: memo §0's OKLCH conversion — five light grounds (L 0.93–0.975), one spacing scale,
  three of five accents in the terracotta band. Design Theater 2026 (five generative-UI tools, 24
  tasks) found convergence in layout and visual appearance while color varied most — so a hue
  axis buys the least spread, density and layout the most.

- Observation: The vitrea design spec deferred skill integration by name.
  Evidence: its Decision Log #2 — "Rejected: adoption-first, skill-integration-first"; and C9b,
  which restyled the demo through the skill without anything flowing back.

- Observation: A parallel session was working the same problem from the research side.
  Evidence: commit 5ace85c (the memo) and uncommitted, aligned edits to `color-engineering.md`
  (ground temperature × lightness headings, neutral and brand-tinted grounds, the accent's job)
  appeared in the working tree mid-implementation. Kept and built on; the session was messaged to
  avoid further collisions.

- Observation: vitrea works from a single HTML file with no bundler and no import map.
  Evidence: `docs/research/vitrea-designer-contract.md` §5 — esm.sh rewrites the one bare
  specifier and the dynamic renderer chunk; a headless-Chrome smoke test over localhost resolved
  `activeRenderer: "webgpu"`. And one trap: the plain-JS API takes the backdrop hint as
  `backdrop:`, not `hint:`, which is silently ignored.

- Observation: The acceptance pair converged on the violet band by elimination, each with a
  defensible reason.
  Evidence: pharmacy accent `oklch(0.365 0.125 308)` (a controlled-substance custody mark);
  wind farm `oklch(0.425 0.145 328)` (the USGS overprint purple). Hue difference 20°, under
  A1's 30°. Both derivations reasoned "the one hue the status set has not taken" — a valid
  constraint used as a source. Recorded in `taste-calibration.md` as "The leftover accent,
  flagged", the sage accent's second cousin; the fix is to name what the product's own world
  offered and why it lost, or to take a `none` accent job.

- Observation: Family choices recur across builds even with criteria-only type records.
  Evidence: Literata in two of four builds, Atkinson Hyperlegible Next in three, JetBrains Mono
  in two. Each choice is argued from criteria ("legibility under poor conditions", "dotted
  zero"), which is the relocated-fixation risk the research named: the criteria funnel to the
  same "best answer" face. The swap-one-slot rule exists for this; a ledger of recent builds'
  families and hues is the structural answer (Deferred).

- Observation: The nine-line record costs more than estimated.
  Evidence: §0 ran 45–70 lines in the four builds; two `DESIGN.md`s exceeded the old 120-line
  budget (184 and 152). The budget was raised to 160 with a one-clause-per-line instruction;
  a compact table form for the nine lines may be the better fix.

- Observation: A semantically named accent token defeats the mechanical clone check.
  Evidence: the builds named their accents `--custody-ink`, `--overprint`, `--clay`; the
  assert script's `--accent` lookup found nothing and the pharmacy record never names its
  token on an accent line, so its hue could not be resolved mechanically.
  `guidelines-authoring.md` §1 now requires the record to say which token carries the accent
  role; `resolve-accent.mjs` reads that.

- Observation: vitrea's GPU tier could not be observed on the test machine.
  Evidence: headless Chrome exposed no GPU adapter; both groups resolved
  `activeRenderer: css, cssBody: two-layer, health: ok` with zero diagnostics. The music
  build's `DESIGN.md` says so rather than claiming refraction; confirming the WebGPU tier needs
  a headed browser with an adapter.

## Deferred

- **A ledger of recent builds' families and hues**, consulted at derivation so that
  dispersion happens in output space (the research's Marks 1997 point) rather than by axis
  distance; the acceptance builds show criteria alone re-converging on Literata, Atkinson
  Hyperlegible Next, and JetBrains Mono.
- **Composition grammar.** All three research rounds say token derivation alone will not stop
  "sidebar + cards + big heading + three-stat row"; Design Theater measured layout convergence
  above color. A brief-derived composition model (primary object, dominant activity, temporal
  structure, relation model, overview-to-detail) generating two or three layout candidates, with a
  composition QA layer distinct from stance QA (Scout, CHI 2020, is the precedent). Touches
  `composition.md`'s "How to pick" and the QA protocol. Its own initiative.
- **The settling experiment.** No published study compares named-look sampling, random-ingredient
  injection, and axis-position sampling for UI. Four arms over the same briefs (immutable named
  systems; named archetypes with derivable tokens; axis derivation without names; axis derivation
  plus one scoped ingredient), quality by blinded human pairwise judgment, effective semantic
  diversity as the headline. A1 is the smallest slice of it.
- **Axis-vocabulary validation.** A lightweight Kansei pass over the skill's own output corpus —
  designers rate screenshots on candidate adjective pairs, inspect correlations, merge synonymous
  coordinates, split ones whose poles produce different token consequences — so "trust",
  "professional", "serious", "minimal", and "enterprise" cannot silently become five names for one
  bundle.
- **Axis-position sampling** as a sampler mode, if the settling experiment favours it.
- **A second evaluation against the brief with the stance hidden.** QA against the build's own law
  tests execution, not whether the law was appropriate; a reader who sees only the brief and the
  rendered page should find the law fitting. The human grid (A6) is the manual form.

## Outcomes & Retrospective

**Achieved against the purpose.** The category-clone pair now diverges. A hospital pharmacy
console and a wind-farm console, built blind to each other under the rewritten skill, share
their constraints (dense, consequential) and their energy (quiet), and differ in everything the
old catalogue would have cloned: material model (tonal against printed), ground (neutral
graphite against neutral white stock), every family (Commissioner / Atkinson Hyperlegible Next
/ JetBrains Mono against Literata / Barlow / JetBrains Mono), and the accent's job and hue
(a status-only custody violet against a directional overprint plum). Neither carries any of the
five worked derivations' values. The brief-authority build honoured a cream-serif-terracotta
brief literally, with the cream band justified in writing. The material-routing build took the
vitrea path from a single HTML file, measured its backdrop hints from the artwork instead of
asserting them, and shipped with the CSS tier reported honestly as the design.

**A1 verdict, stated plainly.** Clauses (a), (c), (d), (e) pass on both builds. Clause (b) fails
on the number — the two accent hues sit 20° apart, both in violet — and passes on the reasoning:
each hue has a product-specific derivation. The convergence itself was the round's most useful
finding and is now a calibration rule. A2 and A3 pass. A4 and A5 pass. A6: the review grid is
at `figma-design-workspace/derivation-eval/review.html`.

**Two external review rounds** (Codex, xhigh) found thirteen real issues and no false ones; the
second round found only follow-through on the first, which is the convergence signal the
project's review policy looks for.

**Lessons.** (1) The persona layer's July lesson was the whole design; this initiative was
applying it one layer up, and the research confirmed it rather than changing it — the value of
the research was the amendments (criticality, energy over register, criteria over names, the
no-middle rungs). (2) Convergence relocates: remove the hex block and it reappears as the
"best answer" family and the "leftover" hue. A calibration file that names bands is the right
tool, and it needs feeding from every eval round. (3) Mechanical checks need the record to name
its own tokens; a semantic token name is good practice and defeats a naive grep. (4) The
research's warning against treating orthogonality as mandatory saved the design from a seven-
slider lookup; the compatibility rules are where the joint judgment lives.

**Remaining.** The composition grammar (layout convergence is untouched by any of this), the
settling experiment, the axis-vocabulary validation pass, a rendered-thumbnail form of the
two-vector step once a render path can be assumed, and a headed-browser confirmation of the
GPU tier for the music build.

## Revision Notes

- 2026-09-05: created from the 2026-09-04 audit; direction approved by the user.
- 2026-09-05 (second revision): the axis set amended after three research rounds converged — two
  brief-fixed constraints (density, criticality) and five coordinates (energy, type, material
  model, color commitment, ground) replace the six-axis draft; compatibility rules, the two-vector
  candidate step, ingredients-as-bounded-mutations, and the Deferred section added; the OKLCH
  catalogue finding and the parallel-session discovery recorded.
- 2026-09-05 (third revision): accent job gains a `none` rung; first external review round recorded with its eight fixes.
- 2026-09-05 (fourth revision): A1 synchronized with the constraints-vs-coordinates rule and the rejected vector; second review round recorded.
- 2026-09-05 (fifth revision): acceptance run recorded — A1 (b) fails on the 30° threshold with both accents in violet, all other clauses pass; five Surprises added; the ledger deferred; Outcomes & Retrospective written.
