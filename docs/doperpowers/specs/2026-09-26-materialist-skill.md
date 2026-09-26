# The materialist: an independent Liquid Glass aesthetic guideline, shipped as a second skill

Status: in progress, 2026-09-26. Parents: `2026-08-24-vitrea-liquid-glass-design.md` (the material
and its runtime) and `2026-09-10-liquid-glass-into-the-skill.md` (the 2.3 draft on the
`capsule-refinement` branch, never merged, whose research and rulings this initiative inherits).
Sibling: `2026-07-27-persona-layer-design.md`, whose authoring contract for a distilled decision
function this skill borrows in shape while standing outside the designer skill.

## Purpose

vitrea is mature enough that the question is no longer whether the material can be drawn but whether
an agent can design with it. The designer skill's `references/material.md` says when glass is earned
and how to ship it, and the 2.3 branch's `liquid-glass.md` says how Apple's system composes a
screen, but both are read only inside the designer workflow, both pin vitrea 0.14.0 and macOS 26, and
neither teaches the aesthetic: what the material is physically, what register it belongs to, and
how an agent should think when a brief has no rule for it. Models are also now strong enough that the
designer spine is not needed every time.

The user's own reading of the aesthetic, recorded here as the brief: a refined futurist aesthetic
with skeuomorphism at its finest, as if the user were interacting with a physical glass display
inside the web page or app, with active use of curvature and smooth, physical motion. The goal is
to let agents use the library to its full potential, with or without the designer skill.

After this initiative: an agent handed a brief that names Liquid Glass, vitrea, a glass or
translucent control layer, or an Apple-like material, whether or not the designer skill is present,
loads one skill that gives it the material's physical model, the aesthetic register, a decision
function, laws by area, a ban list, a QA lens, the vitrea cookbook at the current version, and six
worked derivations. The designer skill routes to it when its material axis resolves to glass over
planes, and the vitrea READMEs link to it so an agent that installs the library without the plugin
finds the same guideline.

## Design

### A. Packaging

A second skill in this plugin, `skills/materialist/`, auto-discovered beside `skills/designer/`
(the validator accepts it, checked 2026-09-26). It is independent: its `SKILL.md` never assumes the
designer spine, `DESIGN.md` or the sampler. The two compose when both are loaded: designer's
`material.md` routes the material and the floating layer to the materialist once the axis resolves
to glass over planes, and the materialist's record template is written so it works with or without
`DESIGN.md`.

Files:

- `skills/materialist/SKILL.md`: one voice, readable in one sitting. Identity and lineage, the
  register, the decision function, the laws by area (plane, floating layer, geometry, colour,
  type on glass, motion, accessibility), the ban list with its mechanical subset, the QA lens, and
  routing to the references.
- `references/optics.md`: the measured physical model, each law with its design consequence and
  its ledger section.
- `references/vitrea.md`: the cookbook, each aesthetic decision mapped to the 0.24.0 API on the
  React and vanilla paths, what the runtime does not catch, and the CSS-only path.
- `references/examples.md`: the six demos of the 2.3 branch as worked derivations, with the
  record template.
- `docs/research/materialist-distillation.md`: provenance, law by law, to the Apple memo, the
  practitioner critique, the fidelity ledger and the user's rulings.
- `docs/research/2026-09-26-liquid-glass-aesthetic-prior-art.md`: the research report on the
  aesthetic's prior art (Apple's articulation and stated lineage, the macOS 27 refinements, the
  critical reception through September 2026, the spring discipline), collected for this initiative.

Ported to main from the branch as source material, never loaded at runtime:
`docs/research/2026-09-10-liquid-glass-design-language.md` (34 sources, 25 checkable rules),
`docs/research/2026-09-10-vitrea-authoring-surface.md` (0.14.0; historical), and the 2.3 spec
`2026-09-10-liquid-glass-into-the-skill.md`. The six demos stay on the branch: they run on 0.14.0
and would need a rebuild, which is deferred.

### B. What the guideline teaches that the 2.3 draft did not

1. **The physical model.** The material as a lens with thickness, a size law inert below span 32
   and saturated at 96, a two-component body, a body that takes the backdrop's tone and hue, a rim,
   an exterior shadow graded by the caster, two poses, two schemes, two variants, a tint that is a
   shade, four ink levels, accessibility settings as material states, and the motion's character.
   Each with the design consequence stated, so a smart model can reason about a novel case.
2. **The register.** Refined futurism with optical skeuomorphism: the glass behaves like glass and
   depicts nothing; the content plane is the world and the controls are an instrument held over it;
   precision geometry; calm; motion is physical rather than choreographed; daylight is the
   distinctive register and dark the easy one.
3. **A decision function** short enough to hold at every choice.
4. **The current API**, including what did not exist at 0.14.0: colour scheme, window activation,
   presence, the materialize morph, toolbar spacers, the macOS 27 material, hue retention.
5. **Authority.** Apple's material physics and two-layer discipline are law; Apple's platform chrome
   conventions are offered as a macOS reading (user decision, pending at the time of writing; the
   recommended default is written in).

### C. Integration

- `skills/designer/references/material.md`: routes to the materialist for the material and the
  floating layer once the axis resolves to glass over planes; its own don'ts and QA additions stay
  as the designer-side summary.
- `skills/designer/SKILL.md`: one routing row and the taste-floor line the 2.3 draft added ("a glass
  surface is a control or it is not glass", active curvature).
- `README.md`: the plugin section names two skills; the vitrea section links the guideline.
- `packages/{core,platform-web,react}/README.md`: a "Designing with the material" pointer.
- `.claude-plugin/plugin.json` and `marketplace.json`: version 2.4.0, description updated. The
  branch's 2.3.0 and 2.3.1 were never released from main; 2.4.0 avoids a collision with those
  commit titles in history.
- `evals/materialist.json`: briefs for the new skill, including one where glass is not earned.

## Decision Log

- Decision: a second skill in the plugin rather than a persona or a standalone document.
  Rationale: the user asked for independence from the designer skill and for something an agent
  using the library can reach; a skill is what Claude Code loads by description, and the designer
  skill can route to it. A standalone document alone would not be loaded; a persona would be
  coupled. Recommended to the user 2026-09-26; proceeding on the recommendation pending their
  answer.
  Date/Author: 2026-09-26, Claude (recommendation), user (pending).

- Decision: material physics and the two-layer discipline are law; Apple's platform chrome
  conventions are a macOS reading offered as reference.
  Rationale: a web product is not a Mac app, and the goal is the material's aesthetic at full
  potential rather than HIG compliance. Recommended to the user; proceeding on the recommendation
  pending their answer.
  Date/Author: 2026-09-26, Claude (recommendation), user (pending).

- Decision: skeuomorphism is optical only. The glass behaves like glass and depicts nothing; no
  surface fakes another material as decoration; the content plane is real content.
  Rationale: what makes the glass read as glass is that nothing else on the page is pretending;
  the demo's own law and the Essentialist's material-honesty line agree. Recommended to the user;
  proceeding pending their answer.
  Date/Author: 2026-09-26, Claude (recommendation), user (pending).

- Decision: the user's 2026-09-10 curvature ruling carries forward as law: single-row floating
  housings and controls prefer capsules with related inner geometry and comfortable padding;
  multi-row platters, sidebars and sheets keep generous rounded rectangles.
  Rationale: recorded user taste on the branch ("much better with more curvature"), consistent
  with Apple's capsule default for bordered buttons.
  Date/Author: 2026-09-10, the user; carried 2026-09-26.

- Decision: plugin version 2.4.0.
  Rationale: 2.3.0 and 2.3.1 exist as commit titles on the unmerged branch; reusing the numbers
  would make two different plugins answer to one version in history.
  Date/Author: 2026-09-26, Claude.

- Decision: the independent review's twenty-six findings were verified against the source and all
  but two were applied in one fix wave. Dismissed: that the laws, the ban list and the QA lens
  restate each rule three times, which is the persona template's structure by design (a law to hold,
  a ban to grep for, a check to answer on the rendered page); and the "one voice" phrasing, which the
  essentialist persona uses for the same reading contract. Four findings had turned a claim into its
  opposite and were treated as blocking: a `file://` page importing from a CDN boots and reaches the
  GPU tier in Chrome; the dark-backdrop vanishing is macOS 26.5's behaviour, removed on 27; setting
  the accessibility overrides to `"system"` is the default and changes nothing; and an in-document
  texture source is mapped onto its own box, not viewport cover-fit, since §5.47.
  Date/Author: 2026-09-26, Claude.

## Surprises & Discoveries

- Observation: the "v2.3" the user remembered is real and unmerged: `origin/capsule-refinement`
  carries designer 2.3.0 and 2.3.1, 41 commits ahead of a base that main has since passed by 757
  commits. Its reference pins vitrea 0.14.0 and macOS 26.
  Evidence: `git branch -a --contains 87cd51b2`; `git log --oneline main..f13ab38c | wc -l`.

- Observation: Apple's macOS 27 refinements (WWDC26 Platforms State of the Union) make part of the
  2.3 draft's "macOS reading" stale on its own terms: menu icons are hidden by default rather than
  carried on every item, sidebars run edge to edge on the Mac rather than floating inset, a uniform
  toolbar appears where content scrolls under floating bars, and every window took a tighter corner
  radius. Apple also describes the material's new edge as "a darkened edge along with brighter
  specular highlights", which is the edge W35 read on the bed and W37 could not fit. The materialist
  states the 27 reading and records the concession as a licence for a quieter desktop control layer.
  Evidence: `docs/research/2026-09-26-liquid-glass-aesthetic-prior-art.md` §1.9.

- Observation: the critics' two strongest charges, legibility (NN/g, Fast Company, Heer) and
  "see-through blandness" (Gruber, 2026-09), are answerable by composition rather than by softening
  the material's rules, and the guideline now answers both: legibility before translucency with the
  opaque page designed first, and identity living in the plane, the type, the motion and one accent.
  Evidence: the same report, §3.1 and §3.6.

## Deferred

- Rebuilding the six demos on 0.24.0 through `@vitreajs/vitrea-react` and publishing them to the
  Pages site (the 2.3 spec's own deferred item).
- Completing the 2.3 spec's interrupted four-rater panel; its pre-registered criterion stands.
- An eval run of the materialist skill against an unaided baseline, on the pattern of
  `evals/evals.json`.
- Input-method scaling of the press response. Apple's material answers direct touch with more
  emphasis and a pointer with less (HIG Motion); vitrea's shipped motion profile has one press
  response for every input. The guideline states the gap and asks a page to add no motion of its own
  rather than to simulate the scaling.

## Revision Notes

- 2026-09-26: created from the user's direction after reading the branch, the runtime and the
  demo law; three recommendations put to the user; research on the aesthetic's prior art dispatched.
- 2026-09-26 (later): the four skill files, the distillation record and the eval briefs written;
  designer's `material.md` corrected on the four stale points the 2.3 authoring-surface memo named
  (esm.sh pin, `file://`, Gecko's conformance cell, the state's field list) and a fifth attempted on
  the way (the host `background` mechanism); the review round below re-corrected two of those five,
  `file://` and the background mechanism, and the entries here record what was first written rather
  than rewriting it. The READMEs and manifests updated; independent review dispatched on the working
  tree.
- 2026-09-26 (research landed): the prior-art report saved as source material; SKILL.md gains
  Apple's own definition and lineage, the practitioner vocabulary for the register, the "where the
  identity lives" answer to the blandness critique, the spring and frequency discipline for motion,
  legibility before translucency with the opaque page designed first, and the macOS 27 reading; the
  distillation record extended with the new rows.
- 2026-09-26 (review round): the independent review's findings applied in a two-worker fix wave;
  the four blocking corrections, the size law's reach (thickness facets saturate at 96, the scatter
  and the shadow keep growing), the group gap attributed to the body's blur rather than the shadow,
  the hue-retention figures per pose with the after and the gap named, the heavy tap's width per
  document, the tint count in the examples, the case-study phrasing ("the user") removed from the
  runtime files, the record defined at first use, the mechanical subset's allowance for the native
  button reset, and check 20's no-capture case; the distillation rows that changed re-grounded.
