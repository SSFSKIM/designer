---
name: figma-design
description: This skill should be used whenever the user asks to design, build, redesign, restyle, or improve any user interface or visual artifact — landing pages, marketing sites, dashboards, product UI, app shells, admin tools, portfolios, multi-section pages, or single graphic marks (logos, icons, badges, illustrations). Use it even when the user does not say "design" — building any new frontend surface counts, as does "make it look better", "make a page for X", or "create a logo". Not for backend-only or non-visual tasks.
version: 0.1.0
---

# Figma Design

Replicate a working design practice: read the project before touching it, commit to one visual stance in writing, build on semantic tokens, use real content, and check the result against an accessibility and taste floor before calling it done. The sections below route each part of that practice to the reference file that covers it in depth.

## Classify the deliverable

Determine which of four routes applies before doing anything else. Misclassifying at this step wastes the rest of the workflow — a single mark forced through the full-page process picks up a stance and tokens it does not need, while a full page treated as a single mark skips composition and QA it does need.

- **Full page or multi-section UI.** Landing pages, dashboards, product surfaces, admin tools, portfolios, multi-section marketing sites. Follow the full workflow below.
- **Single mark.** A logo, icon, badge, monogram, crest, or standalone illustration. Read `references/icon-illustration.md` instead and skip everything else in this file — a single mark does not need a page-level stance, semantic tokens, or a `DESIGN.md`; it needs its own subject-specific treatment.
- **Existing design system present in the project.** Use it. Do not run the sampler — an installed system is global authority and takes precedence over any generated ingredient. Read its component patterns, token names, icon rules, and accessibility conventions before adding or changing anything, and do not replace it with a new visual system unless the user specifically asks for a redesign. Continue with the workflow below, substituting the existing system's stance and tokens for a sampler run, and record usage rules in DESIGN.md only if the project has no design-law doc yet.
- **Supplied reference image or imported design.** Reproduce its visual language faithfully for that surface, improving implementation quality, responsiveness, and interaction where appropriate without inventing a competing aesthetic. A supplied reference has local authority only — it governs the surface it was supplied for, not the rest of the project. The full workflow below still applies to any surface the reference doesn't cover.

Hold the precedence chain verbatim when these routes conflict: "User brief wins per-surface > supplied reference (local) > existing design system (global) > sampled ingredients (only when no system exists) > your own defaults (the floor)." Each link in that chain only overrides the ones after it — a supplied reference never overrides an explicit brief instruction, and sampled ingredients never override either one.

## Required first steps (full-page briefs)

Before writing any UI code for a full-page or multi-section brief, complete these four steps in order:

1. Read the project's existing conventions — tokens, components, stack, styling approach — so new work fits what already exists rather than fighting it. Skipping this step is how a second page ends up with a second, incompatible design system.
2. Run `node scripts/sample-ingredients.mjs` (path relative to this skill's directory; skip if Classify routed to an existing design system) and treat its output exactly per its own preamble.
3. Commit to exactly one stance in writing before any UI code. Name it, and hold it across layout, typography, surfaces, components, imagery, motion, and interaction states. Do not mix unrelated stances in one interface unless the contrast is explicitly motivated by the product or brief.
4. Author the project design law — `DESIGN.md`, per `references/guidelines-authoring.md` — before any UI code, so the stance and tokens are recorded somewhere durable rather than only implied by the first component written. Anyone touching the project later, human or agent, should be able to read `DESIGN.md` and match the existing direction without re-deriving it from the rendered output.

If the brief explicitly names an aesthetic — including a common one — honor it literally; ingredients are tiebreakers, never overrides.

## The workflow spine

Work through these eight steps in order. Each one points at the reference file that covers it.

1. **Parse the brief.** Extract product type, audience, primary task, content shape, and explicit constraints before considering any visual direction. This framing decides every downstream choice — an operational dashboard and a boutique landing page do not share a visual system even if their component inventories look similar, and trust level and content density should shape the system as much as stated aesthetic preference does.
2. **Sample ingredients.** Run the sampler and read its output as tiebreaker material, not instruction. It exists to pull choices away from trained defaults, not to override anything the brief already said or anything an existing system or supplied reference already establishes.
3. **Commit to one stance.** Pick a single coherent direction and write it down before building. Half-committing to two directions, or quietly drifting between them section to section, produces a page that reads as generated rather than designed; see `references/stances.md` for the vocabulary of stances and how to choose and hold one from a brief.
4. **Author DESIGN.md.** Record the chosen stance, its rationale, and the rules that follow from it as project design law, so later work stays consistent with the first decision instead of drifting section by section. See `references/guidelines-authoring.md`.
5. **Build semantic tokens.** Translate the stance into a token set — color roles, type scale, surface and border treatment — rather than hard-coded values scattered through components. Naming a role once and reusing it everywhere is what lets a later revision change the whole system by editing one place instead of hunting through every component. See `references/color-engineering.md`, `references/typography.md`, and `references/stances.md`.
6. **Work information architecture and composition.** Decide what is dominant, what is secondary, and how sections and grids carry that hierarchy before filling anything in. Favor intentional asymmetry over equal-width columns and repeated card grids by default, and let the primary task stay visually dominant throughout. See `references/composition.md`.
7. **Build with realistic content.** Write and place real names, numbers, dates, and copy as the interface is built — never lorem ipsum or generic filler, since fake content hides real hierarchy, density, and spacing problems that only show up with content of realistic length and shape. See `references/voice-copy.md`.
8. **Run a craft pass, then QA.** Add motion and material effects only where they earn their place — communicating state change, spatial continuity, or feedback rather than decorating for its own sake — then verify the whole result before calling it done. See `references/motion.md` and `references/effects-policy.md` for what to add, then `references/qa-protocol.md` for what to check.

## Taste floor

These rules hold regardless of chosen stance, project, or surface. They are the floor beneath every other decision in this file, not a checklist to run once at the end.

- Commit to one stance — do not blend two aesthetic directions in a single interface unless the contrast is explicitly motivated by the brief. A page that hedges between two looks reads as indecisive, not eclectic.
- Accent color does real work only: primary action, selection, focus, or status. It does not decorate headings, icons, dividers, cards, or backgrounds by default — spreading it everywhere flattens the very emphasis it exists to create.
- Content is realistic, always — real names, metrics, dates, and copy, never lorem ipsum or placeholder filler, in any pass of the build.
- Hierarchy comes before decoration — the primary task and most important information are visually dominant before any material effect is added on top.
- Borders organize; they do not bully. Thin, low-opacity dividers structure content — heavy outlines and stacked shadow cards are not the default organization system, and shadows are reserved for elevation, temporary overlay, or floating context rather than applied to every panel.
- Type carries its role, not a single treatment for everything — a display face for expression, a readable face for body copy, and a mono face only where it structures something genuinely tabular such as metrics, timestamps, or code.
- Whitespace is functional, not incidental — it establishes hierarchy and lowers cognitive load rather than filling gaps with decorative components added merely to make a page look fuller.
- Hold the accessibility floor: 4.5:1 contrast for body text, 3:1 for large text and interactive controls, never color alone to communicate status, validation, or selection, and a visible keyboard focus state on every interactive element in every surface state.
- Use semantic HTML controls where they exist — a real button for an action, a real link for navigation, a real label for an input — instead of a styled div standing in for a control.
- Include at least one responsive breakpoint with an intentional collapse — reordered hierarchy, adjusted density, and reconsidered navigation, not a naive compression of the desktop layout onto a narrow screen.

Before shipping anything, check `references/taste-calibration.md` — it names the currently saturated AI-default looks that read as generated.

## Runtime adaptation

Detect the project's existing stack before choosing how to structure output, and match it rather than imposing a fixed file layout. If no stack exists, default to a single self-contained HTML file. The semantic-token pattern itself is mandatory regardless of stack — colors, type, and surfaces are always driven by named tokens rather than hard-coded values — but where those tokens live adapts to the project's own conventions. Keep token values defined in exactly one place, and record the rules for how they are used in `DESIGN.md` rather than scattering that reasoning across components.

## Reference routing

| Reference | Read it for |
|---|---|
| `references/stances.md` | The vocabulary of aesthetic stances and how to pick and commit to one from a brief. |
| `references/color-engineering.md` | Building a semantic color-token system from a chosen stance. |
| `references/typography.md` | Choosing and pairing typefaces, setting scale and letter spacing by role. |
| `references/motion.md` | What motion is for, when it earns its place, and how to keep it accessible. |
| `references/composition.md` | Information architecture, grid choice, and layout hierarchy. |
| `references/effects-policy.md` | When decorative material effects (blur, glass, grain, glow, gradient) are and are not warranted. |
| `references/voice-copy.md` | Writing realistic, contextually appropriate copy and content instead of filler. |
| `references/guidelines-authoring.md` | Authoring `DESIGN.md` as durable project design law. |
| `references/icon-illustration.md` | The single-mark workflow — logos, icons, badges, standalone illustrations. |
| `references/qa-protocol.md` | The pre-ship check: hierarchy, accessibility, responsiveness, and stance consistency. |
| `references/taste-calibration.md` | Currently saturated AI-default looks to avoid, and how to calibrate against them. |
