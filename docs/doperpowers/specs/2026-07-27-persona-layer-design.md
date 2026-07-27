# figma-design Persona Layer — Design Spec

## Purpose

Add an optional **designer-persona layer** to the figma-design skill, and ship its first persona: **the Essentialist** (`essentialist`) — a composite archetype distilled from the Bauhaus → Dieter Rams → Jonathan Ive lineage of extreme functionalist minimalism.

A persona is a distilled human decision function, not a style sheet. The method precedent is the STEM-pedagogy project, where distilling real practitioners (Feynman's lectures, 3Blue1Brown transcripts) into an agentic pedagogy core worked remarkably better than writing pedagogy rules from scratch. (External precedent: the user's STEM-education video-script project — not part of this repo; cited as a user-attested result, not as evidence inspectable from here.) This deliverable applies the same pipeline to design: research a real lineage from primary sources, distill it into an agent-executable persona (philosophy + per-step actionable laws), and route it as an optional governing layer over the existing figma-design workflow. It replaces the discarded SVG-filter direction as the next figma-design upgrade.

## Locked design decisions (from the 2026-07-27 grill)

1. **Architecture — governing layer.** When active, the persona *replaces* the sampler run and the stance choice (workflow steps 2–3): it supplies its own stance commitment with concrete distilled token laws, and injects per-step judgment into composition/IA, color, typography, spacing/grid, surfaces & effects, motion, copy, and QA — the same step list as template part 3, which is the operative contract. Everything else in the spine — DESIGN.md authoring, semantic tokens, realistic content, the standard QA protocol — runs unchanged beneath it.
2. **Invocation — explicit parameter + name-match.** The persona activates only when (a) the brief names it ("use the essentialist persona", "persona: essentialist"), or (b) the brief literally names what it distills: *Dieter Rams*, *Braun*, *Jony Ive* / Ive-era Apple, or the creed *"less but better" / "Weniger, aber besser"*. *Bauhaus* name-matches only when the brief's intent is functionalist product/UI design — in popular usage "Bauhaus" often means the poster aesthetic (primary-color triads, playful geometric composition), close to the opposite of extreme reduction, so poster-art phrasings ("Bauhaus-style poster", "Bauhaus graphic") stay with the normal flow, which already honors a named aesthetic literally. Generic adjectives ("clean", "minimal", "simple") never trigger it — those stay with the normal sampler flow. Never auto-applied otherwise; "optional" means optional.
3. **Research — primary-source corpus.** The persona is distilled *from* a collected corpus of real source material stored in the repo (never loaded at runtime), replicating the pipeline that worked: corpus → distillation → skill file. Writing the persona from model knowledge alone is explicitly rejected.
4. **Identity — composite archetype.** One persona with its own name, distilled from the whole lineage: Bauhaus functionalism as foundation, Rams as the definitive practitioner, Ive as the digital-era translation. Not an impersonation of a single named designer.
5. **Implementation shape — Approach A.** One self-contained runtime file per persona (`personas/essentialist.md`) written against a fixed eight-part template, plus one short "Persona routing" section in `SKILL.md`. Extensibility lives in the template contract, not in routing machinery.

Derived (design-time, user-approved in the design sections): persona invocation is brief-level authority in the existing precedence chain (it enters at "user brief wins per-surface"); specific contradicting brief instructions still beat persona laws per-surface, with the tension recorded in one line of DESIGN.md; a supplied reference image keeps local authority for its own surface; an existing design system loses to explicit persona invocation (invoking a persona over a system *is* a redesign instruction), with the conflict recorded, not silently bulldozed. The persona applies to both deliverable routes — full pages and single marks (a short clause covers the `icon-illustration.md` route). Persona laws override reference-file stylistic defaults where they conflict (e.g., the taste floor's display-face/body-face pairing yields to a one-family law — weight and size differentiation satisfies the type-role floor); the accessibility floor and the QA protocol still bind unconditionally. A `DESIGN.md` that records `persona: <name>` **re-activates that persona on every later turn** touching the project — the per-step judgment and QA lens persist across turns, not just the recorded token laws. `SKILL.md`'s frontmatter `description` is unchanged: personas activate *within* the skill, which already triggers on all design work.

## What "done" looks like (acceptance, phrased as behavior)

1. **Explicit invocation.** A full-page brief containing "use the essentialist persona" produces a build whose `DESIGN.md` records `persona: essentialist` plus the persona's laws as project law, whose transcript shows the sampler was **not** run, and whose page passes the persona's mechanical law checks (accent-role count, font-family count, banned-effects grep — the exact assertions come from the distilled ban list).
2. **Persistence.** A follow-up turn on the criterion-1 project (e.g., "add a settings page") re-activates the persona without the brief re-naming it: the transcript shows `personas/essentialist.md` loaded again — triggered by `DESIGN.md`'s `persona: essentialist` record — and the new surface passes the same law checks.
3. **Name-match routing.** The criterion-1 brief phrased as "design this the way Dieter Rams would" (no persona parameter) routes to the persona and meets criterion 1's checks.
4. **Negative controls.** A brief saying only "clean, minimal dashboard" does **not** activate the persona: the transcript shows a normal sampler run and stance commitment, and DESIGN.md records no persona. A brief for a "Bauhaus-style poster for a design conference" also does **not** activate it — poster-art phrasing routes to the normal flow's literal-aesthetic honoring, not to the Essentialist.
5. **Template conformance.** `personas/essentialist.md` contains all eight template parts (identity & lineage, decision function, per-step laws, home token system, derivation rules, ban list, QA lens, provenance); its home token system has the same shape as the complete systems in `references/stances.md` (color roles, radius scale, borders, shadow tiers, spacing, type ramp, motion); and every per-step law block carries a compact source tag naming the corpus file(s) it distills from.
6. **Corpus provenance.** Every file in `docs/research/personas/essentialist/` opens with a provenance header: source URL, author, original date where known, date accessed, and retrieval method. Corpus files hold excerpts and structured notes, not wholesale reproductions of books.
7. **Eval complete.** The persona eval ran end-to-end — 2 A/B briefs (same brief, normal flow vs. persona-invoked), 1 name-match brief, 2 negative controls (generic-minimal and Bauhaus-poster), and 1 follow-up persistence turn on a persona arm — the side-by-side grid was reviewed by the user, and the verdict is recorded in this spec.

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

`SKILL.md` gains one section, **"Persona routing,"** placed between "Classify the deliverable" and "Required first steps (full-page briefs)". It states the activation contract (decision 2), what activation changes (skip sampler; persona file supplies the stance commitment and per-step laws; record `persona: <name>` in DESIGN.md), the precedence rules, the persistence rule, and the override rule (all from the derived block above), and the single-mark clause.

Two small amendments make the section reachable and durable:

- **Single-mark reachability.** Classify's single-mark bullet currently says "skip everything else in this file," which would make a post-Classify routing section unreachable on "design a logo the way Dieter Rams would." That bullet gains a pointer — check Persona routing below first; an invoked persona governs the mark too — while the routing section itself stays after Classify, preserving the classify-first invariant.
- **`references/guidelines-authoring.md`** gains a brief note defining the `persona:` field in DESIGN.md: what it records, and that its presence re-activates the named persona for every later turn on the project, so DESIGN.md authors and readers share the field's meaning.

`README.md`'s repo map gains a `personas/` line.

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
- **Bauhaus:** the 1919 Gropius manifesto **for lineage identity only** — it belongs to the Bauhaus's expressionist-craft phase ("the cathedral of the future") and cannot ground functionalist laws. The functionalist laws ground in "Art and Technology: A New Unity" (1923) and Gropius's "Principles of Bauhaus Production" (Dessau, 1926).
- **Ive:** interview and keynote transcripts (Objectified segments, major profiles, his own words on Rams' influence); his written foreword on Rams — the single most direct primary source; verify during collection which volume carries it (attributed variously to *Less and More: The Design Ethos of Dieter Rams* and to Sophie Lovell's *Dieter Rams: As Little Design as Possible*) and record what is actually found in the provenance header; Gary Hustwit's *Rams* (2018) documentary; specific Apple-era decisions as digital case evidence.

**Distillation discipline:** every law in the persona file must trace to the corpus — law blocks carry compact source tags in the runtime file; the full law-by-law mapping lives in `essentialist-distillation.md`. A law that cannot be grounded does not ship. This is the rule that keeps the persona a distillation rather than generic minimalism wearing a Rams badge.

### Eval

Workspace: `figma-design-workspace/persona-eval/` (gitignored, like previous evals). Seven builds plus one follow-up turn: 2 briefs × 2 arms (normal vs. persona-invoked, same worker model both arms), 1 name-match brief, 2 negative controls (generic-minimal; Bauhaus-poster), and 1 follow-up persistence turn extending one persona arm's project. Mechanical assertions from the ban list run as a grep script over the persona arms; a side-by-side review grid carries the taste verdict to the user.

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

- **Spec review round 1 (2026-07-27) caught two integration bugs the design sections missed.** (1) The routing section as placed was unreachable on single-mark briefs: Classify's single-mark bullet says "skip everything else in this file," so "design a logo the way Dieter Rams would" would never have read the persona clause the spec put inside the skipped section. (2) Persona persistence was unspecified: the QA protocol's multi-turn pass re-reads DESIGN.md and "extends, don't redesign," so a later turn would have seen `persona: essentialist`, had no idea it meant "reload the persona file," and silently extended under normal flow — the per-step judgment and QA lens (the parts that make a persona more than a stance) would have evaporated after turn one. Lesson: a governing layer must specify not just how it activates but how it *re*-activates, and any routing addition must be checked against every classify route's reading path, including the ones told to skip ahead.
- **Same round: "Bauhaus" is not a safe bare trigger.** In popular usage it frequently means the primary-triad poster aesthetic — close to the opposite of extreme reduction — so a bare name-match would invert exactly the briefs ("Bauhaus-style poster") it pattern-matched. The trigger list now carries intent, not just names, and the eval gained a false-positive probe.

- **Eval round 1 (2026-07-27) surfaced palette monoculture — an instantiation mistaken for a law.** All three persona arms (energy app, bookkeeping landing, hardware product page) shipped byte-identical hex values: cream `#F6F5F2` ground, leaf-green `#3F6B4A` accent. Root cause was two-fold in `personas/essentialist.md`: Part 4 said "copy it in whole" (making home hex values mandatory rather than exemplary) and Part 5 contained no rule licensing per-product accent-hue or ground-temperature derivation — while the decision function's "choose the more restrained option" tiebreaker actively punished unlicensed deviation. The corpus supports derivation, not a fixed palette (Braun's chart: blood orange / honey yellow / leaf green by function; ET66's lone yellow accent; "colours have to suit the product"). Fixed in commit e6b6366. Two structural lessons: (1) a persona file must separate the law from its worked instantiation, and license every per-product judgment explicitly — a rule-following agent treats unlicensed freedom as forbidden; (2) mechanical gates count roles, not appropriateness, and isolated build agents can't see cross-build convergence — only a human viewing all arms side-by-side catches a monoculture. Project-wide principle adopted from this (user directive): avoid hard TODO/NOT-TODO mandates beyond what the corpus warrants; open possibility space with derivation rules instead. A follow-up hunt-and-challenge audit of the whole persona implementation against the corpus was commissioned on this principle.

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-07-27: Initial spec from approved brainstorm (4-question grill + track confirmation + Approach A + three design sections, all user-approved).
- 2026-07-27 (eval round 1): user verdict on the review grid — essentialist voice confirmed clear, but thematic narrowness flagged (every persona arm cream+green). Persona Part 4 reframed from "copy it in whole" to structure-carries-the-law with home values as fallbacks; Part 5 gained accent-hue and ground-temperature derivation rules (corpus-grounded, traceability added to distillation notes Part 5). name-match and brief-b/persona arms rebuilt against the revised persona; corpus-challenge audit dispatched.
- 2026-07-27 (review round 1): applied all findings from external review — (1) single-mark reachability: Classify's single-mark bullet gains a Persona-routing pointer; (2) persistence: DESIGN.md's `persona:` record re-activates the persona on later turns, `guidelines-authoring.md` documents the field, new acceptance criterion 2 and a persistence eval turn added; (3) "Bauhaus" trigger narrowed to functionalist intent, Bauhaus-poster false-positive probe added as a second negative control; (4) corpus corrected — the 1919 manifesto demoted to lineage-identity-only, functionalist grounding moved to the 1923/1926 Gropius texts, Ive's Rams foreword (volume to be verified at collection) and Hustwit's *Rams* (2018) added. Smaller: persona-laws-override-reference-defaults rule stated (accessibility floor and QA protocol still bind; one family + weights satisfies the type-role floor), decision-1 step list aligned to template part 3, STEM precedent marked as external and user-attested.
