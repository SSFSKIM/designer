---
name: designer
description: Always invoke this skill for any UI/UX or design work — designing, building, redesigning, reworking, restyling, or improving a user interface or visual artifact.
version: 2.5.0
---

# Designer

Replicate a working design practice: read the project before touching it, derive one visual stance from the brief and commit to it in writing, build on semantic tokens, use real content, and check the result against an accessibility and taste floor before calling it done. This file is the route; each reference file is the specification of the step it is named at, and is read at that step.

## Classify the deliverable

Determine which of four routes applies before doing anything else. Misclassifying at this step wastes the rest of the workflow — a single mark forced through the full-page process picks up a stance and tokens it does not need, while a full page treated as a single mark skips composition and QA it does need.

- **Full page or multi-section UI.** Landing pages, dashboards, product surfaces, admin tools, portfolios, multi-section marketing sites. Follow the full workflow below.
- **Single mark.** A logo, icon, badge, monogram, crest, or standalone illustration. Check the "Persona routing" section below first — an invoked persona governs a mark too — then read `references/icon-illustration.md` instead and skip everything else in this file; a single mark does not need a page-level stance, semantic tokens, or a `DESIGN.md`, it needs its own subject-specific treatment.
- **Existing design system present in the project.** Use it. Do not run the sampler — an installed system is global authority and takes precedence over any generated ingredient. Read its component patterns, token names, icon rules, and accessibility conventions before adding or changing anything, and do not replace it with a new visual system unless the user specifically asks for a redesign. Continue with the workflow below, substituting the existing system's stance and tokens for a sampler run, and record usage rules in DESIGN.md only if the project has no design-law doc yet.
- **Supplied reference image or imported design.** Reproduce its visual language faithfully for that surface, improving implementation quality, responsiveness, and interaction where appropriate without inventing a competing aesthetic. A supplied reference has local authority only — it governs the surface it was supplied for, not the rest of the project. The full workflow below still applies to any surface the reference doesn't cover.

Hold the precedence chain verbatim when these routes conflict: "User brief wins per-surface > supplied reference (local) > existing design system (global) > sampled ingredients (only when no system exists) > your own defaults (the floor)." Each link in that chain only overrides the ones after it — a supplied reference never overrides an explicit brief instruction, and sampled ingredients never override either one.

## Persona routing

A persona is an optional distilled designer — a governing layer that, when invoked, replaces the sampler run and the stance derivation with a committed decision function and its laws. Personas live in `personas/`, one self-contained file each; the persona currently installed is `personas/essentialist.md`, distilled from the Bauhaus → Dieter Rams → Jonathan Ive functionalist lineage.

A persona activates in exactly three cases, never otherwise:

1. **Explicit parameter.** The brief names it: "use the essentialist persona", "persona: essentialist".
2. **Name-match.** The brief literally names the lineage the persona distills: Dieter Rams, Braun, Jony Ive or Ive-era Apple, or the creed "less but better" / "Weniger, aber besser". "Bauhaus" counts only when the brief wants functionalist product or UI design — poster-art phrasings ("Bauhaus-style poster", "Bauhaus graphic") mean the primary-triad poster aesthetic, which is not this lineage, and stay with the normal flow's literal honoring of a named aesthetic.
3. **Recorded persona.** The project's `DESIGN.md` records `persona: <name>`. A recorded persona re-activates on every later turn touching the project — read the persona file again before extending anything, so the judgment layer persists across turns rather than surviving only as tokens.

Generic adjectives — "clean", "minimal", "simple" — never activate a persona; those briefs run the normal sampler flow.

When a persona is active: do not run the sampler — the persona file supplies the stance commitment and its laws in place of the sampler and the stance derivation; the composition derivation still runs, under the persona's laws, because a persona governs values and judgment, not the page's topology. Read the persona file before any design decision and hold its per-step laws through composition, color, typography, spacing, surfaces, motion, copy, and QA. Record `persona: <name>` at the top of `DESIGN.md`'s stance section, with the persona's laws as project law. Persona laws override reference-file stylistic defaults where they conflict — a one-family type system differentiated by weight and size satisfies the taste floor's type-role rule — but the accessibility floor and `references/qa-protocol.md` bind unconditionally. Persona invocation is brief-level authority: a contradicting brief instruction wins per-surface (record the tension in one line of DESIGN.md), a supplied reference image keeps local authority over its own surface, and an existing design system loses to an explicit persona invocation — that invocation is a redesign instruction; record the conflict in DESIGN.md rather than silently replacing the system. For single marks, the persona governs too: follow `references/icon-illustration.md` for the workflow and the persona file's single-mark clause for its judgment.

## Required first steps (full-page briefs)

Before writing any UI code for a full-page or multi-section brief, complete these four steps in order:

1. Read the project's existing conventions — tokens, components, stack, styling approach, and its image assets (`node scripts/find-image.mjs inventory`) — so new work fits what already exists rather than fighting it. Skipping this step is how a second page ends up with a second, incompatible design system.
2. Run `node scripts/sample-ingredients.mjs` (path relative to this skill's directory; skip if Classify routed to an existing design system or a persona is active — see "Persona routing" above) and treat its output exactly per its own preamble.
3. Derive exactly one stance and one composition and commit to both in writing before any UI code: the stance by the procedure in `references/stances.md`, the composition by the procedure in `references/composition.md`. Both are derived from the product's own world, and both record the road not taken. An existing design system or an active persona reaches the same record another way; `references/stances.md` says how.
4. Author the project design law — `DESIGN.md`, per `references/guidelines-authoring.md` — before any UI code, so the stance and tokens are recorded somewhere durable rather than only implied by the first component written. Anyone touching the project later, human or agent, should be able to read `DESIGN.md` and match the existing direction without re-deriving it from the rendered output.

If the brief explicitly names an aesthetic — including a common one — honor it literally; ingredients are tiebreakers, never overrides.

## The workflow spine

Work through these eight steps in order. Each one points at the reference file that specifies it.

1. **Parse the brief.** Extract product type, audience, primary task, content shape, and explicit constraints before considering any visual direction, and read the brief onto the stance axes (`references/stances.md`) and the six composition lines (`references/composition.md`) from that reading. The material model is one of those axes and is decided here, not at the craft pass (`references/material.md`); when it resolves to glass over planes, `references/liquid-glass.md` governs the composition. This framing decides every downstream choice — an operational dashboard and a boutique landing page do not share a visual system even if their component inventories look similar. Category may speak at the level of an axis position or a posture; it never picks a value or a topology.
2. **Sample ingredients.** Run the sampler and read its output as tiebreaker material, not instruction. It exists to pull choices away from trained defaults, not to override anything the brief already said or anything an existing system or supplied reference already establishes.
3. **Derive one stance and one composition, and commit.** Run the derivation procedure in `references/stances.md` and the composition procedure in `references/composition.md`, consulting the build ledger (`node scripts/build-ledger.mjs nearest …`) before the values and the candidate are fixed, so that what recent builds chose is in view at the moment of choice. Half-committing to two directions, or quietly drifting between them section to section, produces a page that reads as generated rather than designed.
4. **Author DESIGN.md.** Record the derived stance, the composition, their rationale, and the rules that follow from them as project design law, so later work stays consistent with the first decision instead of drifting section by section. Every section is written here, before tokens. See `references/guidelines-authoring.md`.
5. **Build semantic tokens.** Translate the derived stance into a token set — color roles, type scale, surface and border treatment — rather than hard-coded values scattered through components. Naming a role once and reusing it everywhere is what lets a later revision change the whole system by editing one place instead of hunting through every component. See `references/color-engineering.md`, `references/typography.md`, `references/material.md`, and `references/component-character.md` for how a derived system expresses itself in components.
6. **Build the composition.** Implement the candidate fixed at step 3 and recorded in `DESIGN.md` §4, with imagery sourced off the imagery ladder where the subject is a world and drawn as content where it is an artifact. See `references/composition.md`.
7. **Build with realistic content.** Write and place real names, numbers, dates, and copy as the interface is built — never lorem ipsum or generic filler, since fake content hides real hierarchy, density, and spacing problems that only show up with content of realistic length and shape. See `references/voice-copy.md`.
8. **Run a craft pass, then QA.** Add motion and material effects only where they earn their place — communicating state change, spatial continuity, or feedback rather than decorating for its own sake — then verify the whole result before calling it done. The QA includes a check of the built page against the specific rules its own `DESIGN.md` committed to, mechanically where they are mechanical: a page that declared a rule and then broke it is a leading reason committed work still reads as generated. When the page passes, record what it chose in the build ledger (`node scripts/build-ledger.mjs record …`) so the next derivation can see it. See `references/motion.md` and `references/effects-policy.md` for what to add, then `references/qa-protocol.md` for what to check.

## Taste floor

These rules hold regardless of chosen stance, project, or surface. They are the floor beneath every other decision in this file, not a checklist to run once at the end.

- Commit to one stance — do not blend two aesthetic directions in a single interface unless the contrast is explicitly motivated by the brief. A page that hedges between two looks reads as indecisive, not eclectic.
- Values are derived, never ported — a token value lifted from a worked derivation, a named stance, or a previous project without a reason recorded for this product is a defect, however good it looked where it came from.
- Accent color does real work only: primary action, selection, focus, or status. It does not decorate headings, icons, dividers, cards, or backgrounds by default — spreading it everywhere flattens the very emphasis it exists to create.
- Content is realistic, always — real names, metrics, dates, and copy, never lorem ipsum or placeholder filler, in any pass of the build.
- An image-led brief ships imagery — a photograph the imagery ladder found or an artifact drawn as content — never a coloured block, an empty half, or a guessed URL where a picture belongs.
- Hierarchy comes before decoration — the primary task and most important information are visually dominant before any material effect is added on top.
- A glass surface is a control or it is not glass — navigation, an action, a transient platter over live content, never a card, a list, a panel or a hero; a page whose material model is glass over planes composes to `references/liquid-glass.md` before any token is set.
- Borders organize; they do not bully. Thin, low-opacity dividers structure content — heavy outlines and stacked shadow cards are not the default organization system, and shadows are reserved for elevation, temporary overlay, or floating context rather than applied to every panel.
- Type carries its role, not a single treatment for everything — a display face for expression, a readable face for body copy, and a mono face only where it structures something genuinely tabular such as metrics, timestamps, or code.
- Whitespace is functional, not incidental — it establishes hierarchy and lowers cognitive load rather than filling gaps with decorative components added merely to make a page look fuller.
- Unequal space follows unequal requirements — a dominant region gets a felt ratio, peers get equal tracks, and chrome stays where the platform's users expect it; asymmetry, a sidebar, a three-up, or a stat row is earned by a composition line or absent.
- Hold the accessibility floor: 4.5:1 contrast for body text, 3:1 for large text and interactive controls, never color alone to communicate status, validation, or selection, and a visible keyboard focus state on every interactive element in every surface state.
- Use semantic HTML controls where they exist — a real button for an action, a real link for navigation, a real label for an input — instead of a styled div standing in for a control.
- Include at least one responsive breakpoint with an intentional collapse — reordered hierarchy, adjusted density, and reconsidered navigation, not a naive compression of the desktop layout onto a narrow screen.

Before shipping anything, check `references/taste-calibration.md` — it names the currently saturated AI-default looks that read as generated.

## Runtime adaptation

Detect the project's existing stack before choosing how to structure output, and match it rather than imposing a fixed file layout. If no stack exists, default to a single self-contained HTML file. The semantic-token pattern itself is mandatory regardless of stack — colors, type, and surfaces are always driven by named tokens rather than hard-coded values — but where those tokens live adapts to the project's own conventions. Keep token values defined in exactly one place, and record the rules for how they are used in `DESIGN.md` rather than scattering that reasoning across components.

## Reference routing

| Reference | Read it for |
|---|---|
| `references/stances.md` | The stance axes, the compatibility rules, the derivation procedure and its two shortcut routes, five worked derivations, and the named-stance library. |
| `references/composition.md` | The six composition lines, the compiled consequences, the operators and ledger, the candidate procedure, the priors, imagery as content and the imagery ladder, and composition QA. |
| `references/material.md` | The material-model axis — printed, tonal, elevated, glass over planes — and how to ship glass: vitrea when the stack can host a module, CSS glass when it cannot. |
| `references/liquid-glass.md` | The Liquid Glass design language, read whenever the material model resolves to glass over planes: layers, the composition procedure for a glass page, variants, geometry, legibility, motion, anti-patterns, and the rules a glass page is checked against. |
| `references/component-character.md` | The same button set, card, and table built three ways — how a derived system expresses itself in components and interaction states. |
| `references/color-engineering.md` | Building a semantic color-token system from a derived stance. |
| `references/typography.md` | Choosing and pairing typefaces, setting scale and letter spacing by role. |
| `references/motion.md` | What motion is for, when it earns its place, and how to keep it accessible. |
| `references/effects-policy.md` | When decorative material effects (blur, glass, grain, glow, gradient) are and are not warranted. |
| `references/voice-copy.md` | Writing realistic, contextually appropriate copy and content instead of filler. |
| `references/guidelines-authoring.md` | Authoring `DESIGN.md` as durable project design law. |
| `references/icon-illustration.md` | The single-mark workflow — logos, icons, badges, standalone illustrations. |
| `references/qa-protocol.md` | The pre-ship check: hierarchy, accessibility, responsiveness, stance and composition consistency, and the build against its own law. |
| `references/taste-calibration.md` | Currently saturated AI-default looks to avoid, and how to calibrate against them. |
