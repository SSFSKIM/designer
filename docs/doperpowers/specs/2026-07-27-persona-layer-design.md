# figma-design Persona Layer — Design Spec

## Purpose

Add an optional **designer-persona layer** to the figma-design skill, and ship its first persona: **the Essentialist** (`essentialist`) — a composite archetype distilled from the Bauhaus → Dieter Rams → Jonathan Ive lineage of extreme functionalist minimalism.

A persona is a distilled human decision function, not a style sheet. The method precedent is the STEM-pedagogy project, where distilling real practitioners (Feynman's lectures, 3Blue1Brown transcripts) into an agentic pedagogy core worked remarkably better than writing pedagogy rules from scratch. This deliverable applies the same pipeline to design: research a real lineage from primary sources, distill it into an agent-executable persona (philosophy + per-step actionable laws), and route it as an optional governing layer over the existing figma-design workflow. It replaces the discarded SVG-filter direction as the next figma-design upgrade.

## Locked design decisions (from the 2026-07-27 grill)

1. **Architecture — governing layer.** When active, the persona *replaces* the sampler run and the stance choice (workflow steps 2–3): it supplies its own stance commitment with concrete distilled token laws, and injects per-step judgment into composition, color, typography, motion, effects, copy, and QA. Everything else in the spine — DESIGN.md authoring, semantic tokens, realistic content, the standard QA protocol — runs unchanged beneath it.
2. **Invocation — explicit parameter + name-match.** The persona activates only when (a) the brief names it ("use the essentialist persona", "persona: essentialist"), or (b) the brief literally names what it distills: *Dieter Rams*, *Braun*, *Bauhaus*, *Jony Ive* / Ive-era Apple, or the creed *"less but better" / "Weniger, aber besser"*. Generic adjectives ("clean", "minimal", "simple") never trigger it — those stay with the normal sampler flow. Never auto-applied otherwise; "optional" means optional.
3. **Research — primary-source corpus.** The persona is distilled *from* a collected corpus of real source material stored in the repo (never loaded at runtime), replicating the pipeline that worked: corpus → distillation → skill file. Writing the persona from model knowledge alone is explicitly rejected.
4. **Identity — composite archetype.** One persona with its own name, distilled from the whole lineage: Bauhaus functionalism as foundation, Rams as the definitive practitioner, Ive as the digital-era translation. Not an impersonation of a single named designer.
5. **Implementation shape — Approach A.** One self-contained runtime file per persona (`personas/essentialist.md`) written against a fixed eight-part template, plus one short "Persona routing" section in `SKILL.md`. Extensibility lives in the template contract, not in routing machinery.

Derived (design-time, user-approved in the design sections): persona invocation is brief-level authority in the existing precedence chain (it enters at "user brief wins per-surface"); specific contradicting brief instructions still beat persona laws per-surface, with the tension recorded in one line of DESIGN.md; a supplied reference image keeps local authority for its own surface; an existing design system loses to explicit persona invocation (invoking a persona over a system *is* a redesign instruction), with the conflict recorded, not silently bulldozed. The persona applies to both deliverable routes — full pages and single marks (a short clause covers the `icon-illustration.md` route). `SKILL.md`'s frontmatter `description` is unchanged: personas activate *within* the skill, which already triggers on all design work.

## What "done" looks like (acceptance, phrased as behavior)

1. **Explicit invocation.** A full-page brief containing "use the essentialist persona" produces a build whose `DESIGN.md` records `persona: essentialist` plus the persona's laws as project law, whose transcript shows the sampler was **not** run, and whose page passes the persona's mechanical law checks (accent-role count, font-family count, banned-effects grep — the exact assertions come from the distilled ban list).
2. **Name-match routing.** The same brief phrased as "design this the way Dieter Rams would" (no persona parameter) routes to the persona and meets criterion 1's checks.
3. **Negative control.** A brief saying only "clean, minimal dashboard" does **not** activate the persona: the transcript shows a normal sampler run and stance commitment, and DESIGN.md records no persona.
4. **Template conformance.** `personas/essentialist.md` contains all eight template parts (identity & lineage, decision function, per-step laws, home token system, derivation rules, ban list, QA lens, provenance); its home token system has the same shape as the complete systems in `references/stances.md` (color roles, radius scale, borders, shadow tiers, spacing, type ramp, motion); and every per-step law block carries a compact source tag naming the corpus file(s) it distills from.
5. **Corpus provenance.** Every file in `docs/research/personas/essentialist/` opens with a provenance header: source URL, author, original date where known, date accessed, and retrieval method. Corpus files hold excerpts and structured notes, not wholesale reproductions of books.
6. **Eval complete.** The persona eval ran end-to-end — 2 A/B briefs (same brief, normal flow vs. persona-invoked), 1 name-match brief, 1 negative control — the side-by-side grid was reviewed by the user, and the verdict is recorded in this spec.

## Architecture (approved: Approach A — one file + one routing section)

### Repo layout

```
personas/
  essentialist.md          # runtime: the only file loaded when the persona is invoked
  TEMPLATE.md              # non-runtime: the eight-part authoring contract for future personas
docs/research/personas/
  essentialist/            # non-runtime corpus: one file per source, provenance headers
  essentialist-distillation.md   # non-runtime: full law → source traceability notes
```

`SKILL.md` gains one section, **"Persona routing,"** placed between "Classify the deliverable" and "Required first steps (full-page briefs)". It states the activation contract (decision 2), what activation changes (skip sampler; persona file supplies the stance commitment and per-step laws; record `persona: <name>` in DESIGN.md), the precedence rules (derived block above), and the single-mark clause. `README.md`'s repo map gains a `personas/` line.

### The persona file template (the extensibility contract)

Every persona file has exactly these eight parts, in order:

1. **Identity & lineage.** Who the composite is; what each source contributes. Written so the agent adopts a character, not a checklist. (Essentialist: Bauhaus — form follows function, honest materials, geometric discipline; Rams — the ten principles as working rules, "as little design as possible," order and proportion; Ive — reduction as focus, care for unseen detail, material honesty on screens.)
2. **The decision function.** The persona's core loop as questions asked at every choice (Essentialist: *Does this element serve the product's function? What can still be removed? If in doubt, leave it out.*).
3. **Per-step laws.** For each spine step — composition/IA, color, typography, spacing/grid, surfaces & effects, motion, copy, single marks — a block of hard, agent-executable prescriptions. Exact values come from the corpus during distillation, not invented at spec time. Each block ends with a compact source tag (`Sources: <corpus files>`).
4. **Home token system.** A complete stances.md-shaped token block — the persona's default starting system, so a build begins immediately without re-derivation.
5. **Derivation rules.** How to deviate *in persona* when the product genuinely requires it (e.g., a monitoring dashboard's status colors), without breaking character.
6. **Ban list.** Explicit negatives, mechanically checkable where possible.
7. **QA lens.** Added checks run after the standard `references/qa-protocol.md` pass, phrased in the persona's voice — including the removal pass: name one element you tried to remove and why it had to stay.
8. **Provenance.** Pointer to the corpus directory, the distillation notes file, and the distillation date.

Parts 3–4 are deliberately redundant: laws constrain any token derivation; the home system makes the common case zero-cost. This mirrors stances.md's own law-plus-default pattern (five complete systems + "derive fresh" rules).

### Corpus & distillation

Corpus collection is web research (WebSearch/WebFetch), one file per source:

- **Rams:** the ten principles *with Rams' own commentary* (not the poster version); the 1976 New York speech; Vitsœ essays; interviews including the Rams–Ive conversations; concrete Braun product decisions (606 shelving, SK4, ET66) as case evidence.
- **Bauhaus:** the Gropius manifesto; core texts on functionalism and form.
- **Ive:** interview and keynote transcripts (Objectified segments, major profiles, his own words on Rams' influence); specific Apple-era decisions as digital case evidence.

**Distillation discipline:** every law in the persona file must trace to the corpus — law blocks carry compact source tags in the runtime file; the full law-by-law mapping lives in `essentialist-distillation.md`. A law that cannot be grounded does not ship. This is the rule that keeps the persona a distillation rather than generic minimalism wearing a Rams badge.

### Eval

Workspace: `figma-design-workspace/persona-eval/` (gitignored, like previous evals). Six builds: 2 briefs × 2 arms (normal vs. persona-invoked, same worker model both arms), plus 1 name-match brief and 1 negative control. Mechanical assertions from the ban list run as a grep script over the persona arms; a side-by-side review grid carries the taste verdict to the user.

## Out of scope (this deliverable)

- Additional personas — only the template contract and the Essentialist ship. (The template's generality is proven by conformance, not by shipping a second persona.)
- Persona composition — at most one persona per project; combining personas is undefined behavior and stays that way.
- Soft semantic triggering ("ultra-minimal" phrasing activating the persona) — rejected in the grill; the sampler flow owns generic minimalism.
- Any changes to the sampler, the stance taxonomy, or the discarded svgf-design skill (its files remain on disk, uninstalled).
- Persona packaging/marketplace concerns.

## Decision Log

- **Governing layer over new-stance-entry and philosophy-lens.** A sixth stance in stances.md is just a token block — no judgment layer, no QA lens, and personas never become a first-class concept. A pure philosophy lens leaves the sampler running, so random ingredient draws constantly fight an extreme-minimalist filter — sampling ornament to veto it. The governing layer is the only shape that matches the "distilled human as decision function" precedent.
- **Parameter + name-match over strict-explicit-only and soft-semantic triggering.** Strict-only wastes the persona on the requests it fits best (the skill already promises to honor a named aesthetic literally — having a Rams persona installed but unused on "design like Dieter Rams" is absurd). Soft triggering hijacks briefs whose authors just wanted a quieter normal flow, and makes "optional" stop meaning optional.
- **Primary-source corpus over knowledge-based and hybrid-without-corpus distillation.** Knowledge-based is the highest-risk path to poster platitudes — the 3B1B result came from transcripts, not summaries of transcripts. The no-corpus hybrid loses the auditable, re-distillable base, which is also what makes future personas cheap to add well.
- **Composite archetype over named-individual and philosophy-named.** The Feynman+3B1B precedent was itself a composite. A literal `dieter-rams` persona is narrower than the lineage and demands more extrapolation for surfaces Rams never touched. A creed name ("less-but-better") names a rule, not a decision-maker — the WHO framing is the part that made the pedagogy core work.
- **Approach A (one file + routing section) over B (mini-skill package) and C (fold into stances.md).** B fragments what must read as one coherent voice — an agent mid-build consults a persona as a single character, and splitting philosophy from laws invites reading one and skipping the other. C erases the persona-vs-stance distinction the architecture decision just established, and bloats an already-large file. A keeps extensibility in the file contract, where it is cheap.

## Surprises & Discoveries

(None yet — populated during implementation.)

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-07-27: Initial spec from approved brainstorm (4-question grill + track confirmation + Approach A + three design sections, all user-approved).
