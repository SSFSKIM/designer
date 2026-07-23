# figma-design Skill — Design Spec

**Date:** 2026-07-23 · **Status:** Approved design, pre-implementation

## Purpose

Ship `figma-design`: a self-contained Claude Code Agent Skill that replicates Figma Make's UI-design workflow, extracted through four rounds of interviews with Figma Make's AI (corpus in `Figma Design/`). This is deliverable #1 of the SVGF-Design repo. Deliverable #2 — the SVG Filter design skill — will be built *using* figma-design together with `frontend-design` (Anthropic) and `impeccable` (Apache 2.0), so figma-design's fidelity to the extraction is part of its value: it is the Figma leg of that three-source foundation.

The skill exists because agent-generated UI collapses into recognizable defaults. Figma Make's counter-architecture — entropy-sampled aesthetic ingredients, single-stance commitment, a per-project design-law document, semantic tokens, and blind QA — reliably produces distinct, coherent interfaces. We replicate that architecture natively for Claude Code.

## What "done" looks like (acceptance, phrased as behavior)

1. **Triggering:** In a session with the skill installed, a prompt like "build a landing page for X" or "design a dashboard for Y" loads the skill; a backend-only prompt does not. A single-mark prompt ("make a logo for Z") routes to the icon-illustration reference, not the full-page workflow.
2. **Workflow execution:** On a full-page brief, the agent (a) reads project conventions first, (b) runs `scripts/sample-ingredients.mjs` and receives an ingredients card, (c) commits to exactly one stance in writing, (d) authors a project `DESIGN.md` before writing UI code, (e) builds with realistic content, (f) runs the QA checklist. Skipping any of (a)–(d) on a full-page brief means the SKILL.md instructions failed and must be revised.
3. **Divergence (generalizability test):** The same brief run twice with different sampler seeds produces two visibly different, each-internally-coherent design systems — the FRAME/MERIDIAN property.
4. **Slop-escape:** Briefs that don't name an aesthetic do not produce the three named AI-default looks (cream+serif+terracotta; near-black+acid accent; broadsheet hairline) or banned patterns (eyebrow-on-every-section, hero-metric template, identical card grids).
5. **Brief authority:** A brief that explicitly names an aesthetic — including a "default" look — is honored literally; ingredients act only as tiebreakers.
6. **Standalone:** All of the above hold with only figma-design installed (no impeccable/frontend-design co-loaded).
7. **Eval:** The skill-creator loop has run at least one iteration: 4–6 briefs, with/without-skill pairs, screenshots rendered, user review completed, revisions applied.

## Architecture (approved: option B — skill + sampler script + reference library)

### Repo layout

```
SVGF-Design/                     ← repo IS the skill (symlink/marketplace install)
├── SKILL.md
├── scripts/
│   ├── sample-ingredients.mjs   # zero-dep Node; replicates create_make_theme
│   └── ingredients.json         # stance/typography/canvas libraries
├── references/                  # progressive disclosure, 2–5k words each
├── examples/
├── Figma Design/                # interview corpus (source material, never loaded)
├── docs/                        # research + specs (never loaded)
└── README.md
```

### SKILL.md (~1,500–2,000 words, always loaded on trigger)

Skeleton mirrors the captured aesthetic-stance skill, generalized off Figma's runtime:

1. **Frontmatter** — `name: figma-design`; pushy third-person description covering design/build/redesign of multi-section UI *and* single marks; excludes backend-only work.
2. **Classify the deliverable** — full page / single mark / existing design system / supplied reference image — with the corrected precedence chain: user brief wins per-surface > reference image (local authority) > existing system (global authority) > sampled ingredients (only when no system exists) > personal defaults. Existing system present ⇒ do **not** run the sampler (kit XOR sampler).
3. **Required first steps (full-page)** — read project conventions (tokens/components/stack) before designing; run the sampler; commit one stance; author the project design law before UI code.
4. **Workflow spine** — parse brief → sample → commit → `DESIGN.md` → semantic tokens → IA/composition → build with realistic content → craft pass → QA. Each step points at its reference file.
5. **Inline taste floor** — commit-don't-hedge; accent discipline; realistic content always; brief-wins rule; pointer to `taste-calibration.md`.
6. **Runtime neutrality** — no fixed file contract; detect and match the project's stack (plain HTML, React+Tailwind, etc.); semantic-token *pattern* mandatory, file locations adaptive. Single-file HTML is the default when no project exists.
7. **Routing table** — references with when-to-read guidance.

### Sampler — `scripts/sample-ingredients.mjs` + `ingredients.json`

- Zero-dependency Node; `node scripts/sample-ingredients.mjs [--seed N]`.
- Emits Figma's exact card format: preamble ("…tiebreakers when the brief is silent… pick the less-common one"), **3 stances + 2 typography traditions + 1 canvas treatment**, closing "YOUR TASK: Combine…" directive.
- Library: Figma's verbatim 10 stances / 13 typography traditions / 5 canvas treatments (`origin: figma`), widened with ~6–8 authored stances (`origin: extension`) chosen to sit outside the saturated lanes (candidates at build time: e.g. risograph/print, terminal-native, Bauhaus-modernist, Y2K-web, luxury-fashion editorial, vernacular/DIY, art-deco geometric). Each entry uses Figma's exact one-line format: name — reference exemplars, characterization.
- `--seed` gives reproducible draws for evals; unseeded uses crypto randomness.
- Rationale for a script over prose instruction: LLMs sample badly from prose lists (mode collapse onto famous entries); deterministic sampling makes the entropy injection real. This is the load-bearing difference between options B and A.

### References (11 files)

| File | Content | Primary sources |
|---|---|---|
| `stances.md` | Stance library with full implementation values: token sets, radius/border/shadow, spacing, type scale, motion per stance. Five complete systems from R2 + authored systems for extension stances | R2-P2; R3-P1 |
| `color-engineering.md` | OKLCH-first procedure: ground temperature, neutral-ramp construction (non-uniform L steps), accent heuristics by product meaning, per-stance chroma limits, validation checks, 7 dark-mode derivation rules, chart-series construction | R2-P5 |
| `typography.md` | Curated type library by register, 10 named pairings, operational type scales (dense tool vs editorial), case behavior, overused-defaults blacklist | R2-P4 |
| `motion.md` | Duration tiers, named cubic-beziers with use table, spring-overshoot restrictions, animate/never-animate property tables, reduced-motion policy | R2-P7 |
| `composition.md` | Hero archetypes, dashboard arrangements (exception-first etc.), content/detail and commerce patterns, grid definitions, collapse behavior, selection logic | R3-P7 |
| `effects-policy.md` | Earned-effects framework (semantic role, stance fit, localized, legible, fallback, budget), per-effect conditions + shippable recipes: glass, gradients, grain, glow, organic forms, displacement; per-primitive SVG-filter positions. Conservative by design — the seam the SVGF skill extends | R2-P3 |
| `voice-copy.md` | Believable-data rules, voice-per-stance worked examples, microcopy rules (verb+object buttons, standalone links, error anatomy), length heuristics; frontend-design's writing-in-design section (attributed) | R3-P8; frontend-design |
| `guidelines-authoring.md` | How to author the project `DESIGN.md`: values-vs-usage split (tokens file owns values, DESIGN.md owns usage), section structure (stance commitment → palette rules → type roles → layout system → component canon → voice → motion → hard don'ts), ambiguity tiebreaker line | R4 FRAME; R4b MERIDIAN; R3-P2 |
| `icon-illustration.md` | The verbatim-captured single-mark skill, lightly generalized (output mechanics de-Figma'd) | R4-P3 verbatim |
| `qa-protocol.md` | Ordered blind checklist (compile → completeness → computed composition → OKLCH-gap contrast proxy → responsive → states → content → interactivity → token discipline → scope), top-10 defect list, screenshot verification via playwright-cli when available, multi-turn drift defense ("system is constraint, not suggestion") | R3-P9 |
| `taste-calibration.md` | **Quarantined graft layer, attributed:** frontend-design's three named default looks + two-pass plan/self-review + signature-element discipline; impeccable's absolute bans, cream-band OKLCH spec + token-name tells, second-order category-reflex check, physical-scene sentence, color-strategy commitment axis | frontend-design; impeccable (Apache 2.0) |

Quarantine rationale: the replica core (SKILL.md + 10 other references) stays faithful to the extraction; the calibration file makes the skill safe standalone. Attribution preserved per license.

### Examples

- `examples/guidelines-frame.md` — FRAME Studio (quiet-editorial, warm paper) — from R4.
- `examples/guidelines-meridian.md` — MERIDIAN PICTURES (brutalist, near-black) — from R4b.
- Both prefaced: *same brief, different sampled ingredients → two committed, mutually-exclusive, internally-coherent systems.* This pair is the skill's proof-of-method and the model for `DESIGN.md` authorship.
- `examples/reference-implementation/` — one complete built page adapted from R3-P6 (film-studio dashboard): DESIGN.md + tokens + single-file implementation, showing the law→code chain end to end.

### Eval plan (skill-creator loop)

- **Briefs (4–6):** one near the corpus (ops dashboard), several far (e.g. municipal transit status board, children's library site, hardware-store commerce, musician EPK, clinical-trial portal). At least one names an explicit aesthetic (brief-authority check) and one is deliberately vague.
- **Runs:** with-skill and without-skill pairs per skill-creator; screenshots via playwright-cli; results in eval viewer for user review.
- **Skill-specific assertions:** divergence (same brief, seeds A/B → different committed stances/systems); slop-escape (no unprompted landing in the three default looks / banned patterns); process-compliance (sampler run, stance committed in writing, DESIGN.md authored before UI code).
- **Last:** description-triggering optimization (skill-creator's trigger-eval loop).

## Out of scope (this deliverable)

- SVG-filter material recipes beyond the conservative effects-policy (that's deliverable #2, which consumes this skill).
- An impeccable-style command surface (`critique`, `polish`, …) — impeccable already exists; wrong scope.
- Backend/persistence guidance of any kind.
- Replicating Figma Make's environment contract (App.tsx/theme.css paths, motion/react, Make Kits) — replaced by runtime-neutral convention detection.

## Decision Log

- **Architecture B (skill + sampler script + references) over A (prose monolith) and C (full plugin).** A lost because prose-instructed sampling mode-collapses back to defaults — the sampler script is load-bearing. C lost because it duplicates impeccable's command surface and multiplies maintenance beyond the repo's second act. (2026-07-22, user-confirmed 2026-07-23)
- **Name `figma-design`** over `design-director`/`stance-design`: honest about lineage; composes by name with `frontend-design` + `impeccable` as the three-source foundation for the SVGF skill. (User decision, 2026-07-23)
- **Taste grafts quarantined in `taste-calibration.md`** rather than woven through the core (would dilute replica fidelity) or omitted (unsafe standalone: Figma's own example outputs land inside the 2026 banned lanes — cream #F5F0E8/#F4F1EA systems, eyebrow scaffolds). (2026-07-23)
- **Runtime-neutral over Figma's file contract**: consumers are arbitrary Claude Code projects, not Figma Make's fixed scaffold. Semantic-token pattern kept mandatory; file locations adaptive. (2026-07-23)
- **Sampler library = Figma's verbatim sets + tagged extensions** rather than Figma-only (pool sits inside saturated lanes) or fully re-authored (loses replica identity). (2026-07-23)
- **Repo root as skill root** (vs nested `figma-design/` dir): matches "the repo is the skill" packaging decision from the first grill; corpus dirs coexist harmlessly. (2026-07-22)
- **No further Figma interviews**: corpus declared complete after Round 4b; the one open offer (verbatim Guidelines-authoring section of aesthetic-stance) is optional enrichment, not a blocker. (2026-07-22)

## Surprises & Discoveries

- `create_make_theme` is an entropy sampler, not a theme generator; the design intelligence lives in the skill body + model. Confirmed live in R4b: tool output ends at "YOUR TASK: Combine…" with no Guidelines-authoring instructions (those live in the aesthetic-stance SKILL.md — its own frontmatter description was misleading).
- Figma Make internally runs a Claude-style skill architecture (Skill tool, SKILL.md frontmatter, conditional modules) — the port is 1:1, not a translation.
- Triple convergent evolution: Figma Make, impeccable, and frontend-design independently evolved project-law file + entropy source + stance commitment + conditional references + verification loop.
- Figma's example outputs land inside the AI-default looks the other two skills ban (MERIDIAN's `--paper: #F4F1EA` is the literal hex frontend-design names as the cream tell) — hence the quarantined calibration layer.
- The FRAME/MERIDIAN pair (same brief → two systems) fell out of the interviews unplanned and became the skill's canonical proof-of-method.

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-07-23: Initial spec from approved design presentation.
