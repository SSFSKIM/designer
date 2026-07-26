# figma-design Persona Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use doperpowers:subagent-driven-development (recommended) or doperpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the optional persona layer for the figma-design skill and its first persona — the Essentialist, distilled from a primary-source Bauhaus → Rams → Ive corpus — per the approved spec at `docs/doperpowers/specs/2026-07-27-persona-layer-design.md`.

**Architecture:** One self-contained runtime file per persona (`personas/essentialist.md`, eight fixed parts) plus one "Persona routing" section in `SKILL.md`; the corpus and law-traceability notes live under `docs/research/personas/` and are never loaded at runtime. Persistence works through `DESIGN.md`'s `persona: <name>` record, which re-activates the persona on every later turn. Proven by a seven-build-plus-one-turn eval with mechanical ban-list assertions and a user-reviewed grid.

**Tech Stack:** Markdown skill files; WebSearch/WebFetch for corpus research; bash/grep verification; `playwright-cli` for eval screenshots; Sonnet subagent workers for eval builds.

## Global Constraints

Copied from the spec — every task's requirements implicitly include these:

- The persona activates **only** on: (a) explicit parameter ("use the essentialist persona", "persona: essentialist"); (b) name-match — *Dieter Rams*, *Braun*, *Jony Ive* / Ive-era Apple, or *"less but better" / "Weniger, aber besser"*; *Bauhaus* only when the brief's intent is functionalist product/UI design (poster-art phrasings stay with the normal flow); or (c) the project's `DESIGN.md` records `persona: <name>`. Generic adjectives ("clean", "minimal", "simple") never trigger it.
- When active: the sampler is **not** run; the persona file supplies the stance commitment; `DESIGN.md` records `persona: essentialist` plus the persona's laws.
- Persona laws override reference-file stylistic defaults; the accessibility floor and `references/qa-protocol.md` bind unconditionally. A one-family type system with weight/size differentiation satisfies the taste floor's type-role rule.
- Every per-step law block in the persona file ends with a `Sources:` tag naming corpus file(s). **A law that cannot be grounded does not ship.**
- Every corpus file opens with a provenance header: source URL, author, original date where known, date accessed, retrieval method. Excerpts and structured notes only — no wholesale reproductions of books.
- The home token system has the same shape as the complete systems in `references/stances.md` (color roles, radius scale, borders, shadow tiers, spacing, type ramp, motion).
- `SKILL.md`'s frontmatter `description` is unchanged.
- The 1919 Gropius manifesto grounds **lineage identity only** — functionalist laws cite the 1923 ("Art and Technology: A New Unity") and 1926 (Dessau "Principles of Bauhaus Production") texts.
- Eval workers: same model both arms of every A/B pair (use Sonnet for all eval builds).
- Commit messages: no `Co-Authored-By` or other attribution lines.

## File structure

```
Create:
  docs/research/personas/essentialist/rams-ten-principles.md      (Task 1)
  docs/research/personas/essentialist/rams-1976-speech.md         (Task 1)
  docs/research/personas/essentialist/rams-interviews.md          (Task 1)
  docs/research/personas/essentialist/rams-braun-cases.md         (Task 1)
  docs/research/personas/essentialist/vitsoe-essays.md            (Task 1)
  docs/research/personas/essentialist/bauhaus-1919-manifesto.md   (Task 2)
  docs/research/personas/essentialist/bauhaus-functionalist-texts.md (Task 2)
  docs/research/personas/essentialist/ive-interviews.md           (Task 2)
  docs/research/personas/essentialist/ive-rams-foreword.md        (Task 2)
  docs/research/personas/essentialist/ive-apple-cases.md          (Task 2)
  docs/research/personas/essentialist/hustwit-rams-2018.md        (Task 2)
  personas/TEMPLATE.md                                            (Task 3)
  personas/essentialist.md                                        (Task 3)
  docs/research/personas/essentialist-distillation.md             (Task 3)
Modify:
  SKILL.md                    (Task 4: single-mark bullet at line 16; new section after line 20)
  references/guidelines-authoring.md  (Task 4: append to Required-structure item 0, line 20)
  README.md                   (Task 4: repo-map bullet, line 42)
Eval (gitignored, never committed):
  figma-design-workspace/persona-eval/…                           (Task 5)
```

---

### Task 1: Corpus — Rams & Vitsœ

**Files:**
- Create: the five `docs/research/personas/essentialist/rams-*.md` / `vitsoe-*.md` files listed above.

**Interfaces:**
- Consumes: nothing (first task).
- Produces: corpus files whose exact filenames Task 3's `Sources:` tags cite verbatim.

Every corpus file opens with this provenance header (YAML frontmatter), then holds excerpts and structured notes — quotes attributed, paraphrase marked as paraphrase:

```markdown
---
source: <URL, or full citation if print-only>
author: <name>
original-date: <year/date, or "unknown">
accessed: 2026-07-27
retrieval: <WebFetch | WebSearch excerpt | transcribed from published excerpt>
---
```

- [ ] **Step 1: Create the directory and research each source with WebSearch/WebFetch**

Collect, one file per source:

1. `rams-ten-principles.md` — the ten principles **with Rams' own commentary**, not the poster version. Primary candidate: Vitsœ's own page (vitsoe.com → "Dieter Rams: ten principles for good design"), which carries his elaborations. Record each principle plus its commentary, and note any concrete product example Rams himself attaches.
2. `rams-1976-speech.md` — the 1976 New York speech ("Design by Vitsœ"). Vitsœ has published this speech; search `Dieter Rams 1976 speech "Design by Vitsœ"`. Capture the passages on responsibility, longevity, and "the economy of Less".
3. `rams-interviews.md` — interviews, prioritizing the Rams–Ive conversations (Vitsœ filmed one; several print versions exist). Capture direct quotes on process and decision-making, not biography.
4. `rams-braun-cases.md` — concrete product decisions as case evidence: 606 Universal Shelving System, SK4 record player, ET66 calculator. For each: what was removed, what was standardized, which typeface/color decisions are documented (e.g., Braun's use of a single grotesk; the single green power switch as the only color accent on otherwise achromatic devices).
5. `vitsoe-essays.md` — Vitsœ's essays on the design ethos ("never sell aggressively", longevity, the 606 system's rules).

- [ ] **Step 2: Verify provenance headers and content shape**

Run:
```bash
ls docs/research/personas/essentialist/ | wc -l          # expect: 5
grep -L 'accessed:' docs/research/personas/essentialist/*.md   # expect: no output
grep -L 'source:' docs/research/personas/essentialist/*.md     # expect: no output
```

- [ ] **Step 3: Commit**

```bash
git add docs/research/personas/essentialist/
git commit -m "docs(research): persona corpus — Rams and Vitsœ primary sources"
```

---

### Task 2: Corpus — Bauhaus & Ive

**Files:**
- Create: the six `bauhaus-*.md` / `ive-*.md` / `hustwit-*.md` files listed in the file structure.

**Interfaces:**
- Consumes: the provenance header format from Task 1 (repeated below — use it verbatim).
- Produces: corpus filenames Task 3's `Sources:` tags cite verbatim.

Same provenance header as Task 1:

```markdown
---
source: <URL, or full citation if print-only>
author: <name>
original-date: <year/date, or "unknown">
accessed: 2026-07-27
retrieval: <WebFetch | WebSearch excerpt | transcribed from published excerpt>
---
```

- [ ] **Step 1: Research each source with WebSearch/WebFetch**

1. `bauhaus-1919-manifesto.md` — the Gropius founding manifesto. **Open the notes section with this exact warning line:** `> Lineage identity only — expressionist-craft phase ("the cathedral of the future"); do NOT cite under functionalist laws.`
2. `bauhaus-functionalist-texts.md` — the functionalist grounding: Gropius's "Art and Technology: A New Unity" (1923 exhibition address) and "Principles of Bauhaus Production" (Dessau, 1926). Capture the passages on standardization, function-derived form, and economy of means.
3. `ive-interviews.md` — interview and keynote transcripts: Objectified (2009) segments, major profiles (e.g., The New Yorker 2015), his own words on Rams' influence and on care for unseen detail.
4. `ive-rams-foreword.md` — Ive's written foreword on Rams. **Verify during collection which volume actually carries it** — attributed variously to *Less and More: The Design Ethos of Dieter Rams* and to Sophie Lovell's *Dieter Rams: As Little Design as Possible* — and record what is actually found in the provenance header.
5. `ive-apple-cases.md` — specific Apple-era decisions as digital case evidence: single type family per era (Myriad/SF), the iPod's reduction story, iOS 7's flattening rationale as stated by Ive, hardware color restraint.
6. `hustwit-rams-2018.md` — Gary Hustwit's *Rams* (2018) documentary: notes on statements Rams makes on camera, especially anything not in the print sources.

- [ ] **Step 2: Verify**

```bash
ls docs/research/personas/essentialist/ | wc -l          # expect: 11
grep -L 'accessed:' docs/research/personas/essentialist/*.md   # expect: no output
grep -q 'Lineage identity only' docs/research/personas/essentialist/bauhaus-1919-manifesto.md && echo OK   # expect: OK
```

- [ ] **Step 3: Commit**

```bash
git add docs/research/personas/essentialist/
git commit -m "docs(research): persona corpus — Bauhaus and Ive primary sources"
```

---

### Task 3: Distill — TEMPLATE.md, essentialist.md, distillation notes

**Files:**
- Create: `personas/TEMPLATE.md`, `personas/essentialist.md`, `docs/research/personas/essentialist-distillation.md`
- Read first: all 11 corpus files; `references/stances.md` lines 1–120 (the "Precision industrial" complete system — the token-shape reference); `references/qa-protocol.md` (the QA lens extends it).

**Interfaces:**
- Consumes: corpus filenames from Tasks 1–2 (cited verbatim in `Sources:` tags).
- Produces: `personas/essentialist.md` with exact headings `## 1. Identity & lineage` … `## 8. Provenance` (Task 4's routing section and Task 5's eval both name this file); a `§6 Ban list` whose grep-checkable subset Task 5's `assert-essentialist.sh` mirrors.

- [ ] **Step 1: Write `personas/TEMPLATE.md` with exactly this content**

```markdown
# Persona authoring template

A persona is a distilled human decision function: a governing layer that, when invoked, replaces the sampler run and the stance choice, and injects judgment into every workflow step. One persona = one self-contained file in `personas/`, written against the eight parts below, in this order, with these exact headings. This template is the authoring contract; it is never loaded at runtime.

Authoring rules:

- Distill from a collected primary-source corpus (`docs/research/personas/<name>/`), never from generic knowledge. Every per-step law block ends with `Sources: <corpus file(s)>`. A law that cannot be grounded in the corpus does not ship.
- Write laws agent-executable: exact values and checkable prescriptions ("one type family; weights 400 and 600 only"), never moods ("keep it elegant").
- The home token system copies the shape of the complete systems in `references/stances.md`: color roles, radius scale, border system, shadow tiers, spacing scale, type ramp, motion.
- Keep the whole file readable in one sitting — it is consulted mid-build as one voice.

## 1. Identity & lineage

Who the composite is; what each source in the lineage contributes. Written so the agent adopts a character, not a checklist.

## 2. The decision function

The persona's core loop, as questions asked at every choice.

## 3. Per-step laws

One block per spine step, each ending with a `Sources:` tag, under these subheadings:

### Composition & information architecture
### Color
### Typography
### Spacing & grid
### Surfaces & effects
### Motion
### Copy
### Single marks

## 4. Home token system

A complete stances.md-shaped token block (CSS custom properties) — the persona's default starting system, so a build begins without re-derivation.

## 5. Derivation rules

How to deviate in persona when the product genuinely requires it, without breaking character.

## 6. Ban list

Explicit negatives, mechanically checkable where possible. Keep the grep-checkable subset in sync with any eval assert script that enforces it.

## 7. QA lens

Added checks run after `references/qa-protocol.md`, phrased in the persona's voice — including the removal pass: name one element you tried to remove and why it had to stay.

## 8. Provenance

Corpus directory, distillation notes file, distillation date.
```

- [ ] **Step 2: Distill `personas/essentialist.md` from the corpus**

Use the template's exact eight headings and eight `### ` law subheadings. Requirements beyond the template:

- **Part 1** names the composite ("the Essentialist") and the three contributions: Bauhaus — form follows function, honest materials, geometric discipline (functionalist laws citing `bauhaus-functionalist-texts.md`, identity citing `bauhaus-1919-manifesto.md`); Rams — the ten principles as working rules, "as little design as possible", order and proportion; Ive — reduction as focus, care for unseen detail, material honesty on screens.
- **Part 2** is the core loop, grounded in Rams' own formulations: *Does this element serve the product's function? What can still be removed? If in doubt, leave it out.* Plus a single ambiguity tiebreaker sentence in the DESIGN.md-skeleton style ("if a decision is ever ambiguous, choose the more restrained option") — the persona's builds will copy it into their DESIGN.md stance section.
- **Part 3**: every law is a checkable prescription with exact values where the corpus supports them (e.g., the documented Braun pattern of an achromatic ground with a single functional color accent; the single-grotesk type practice; Ive-era single-family typography). Each block ends with `Sources:` naming corpus files from Tasks 1–2 verbatim.
- **Part 4**: full token block shaped exactly like stances.md's "Precision industrial" system — same token-category inventory (`--background` … `--ring`, status colors, `--radius-*`, border, shadow tiers, spacing scale, type ramp, motion durations/easings) with Essentialist values derived from Part 3's laws.
- **Part 6** ends with a fenced subsection titled `Mechanical subset` listing the grep-checkable bans, expected to include at least: at most one accent color role; at most two `font-family` stacks (the second only a monospace for tabular data); no `backdrop-filter`; no SVG filter primitives (`feTurbulence`, `feDisplacementMap`); no `text-shadow`. Adjust only if the corpus genuinely contradicts one — and if adjusted, Task 5's assert script must be adjusted to match.
- **Part 7** includes the removal pass verbatim: "Name one element you tried to remove and why it had to stay."
- **Part 8** points to `docs/research/personas/essentialist/` and `docs/research/personas/essentialist-distillation.md`, dated 2026-07-27.

- [ ] **Step 3: Write `docs/research/personas/essentialist-distillation.md`**

A table mapping every Part-3 law (and every Part-6 ban) to its corpus file and the specific quote or passage it distills. Columns: `Law | Corpus file | Grounding quote/passage (short)`. This is the full traceability record; the runtime file carries only the compact `Sources:` tags.

- [ ] **Step 4: Verify template conformance mechanically**

```bash
for h in "## 1. Identity & lineage" "## 2. The decision function" "## 3. Per-step laws" \
         "## 4. Home token system" "## 5. Derivation rules" "## 6. Ban list" \
         "## 7. QA lens" "## 8. Provenance"; do
  grep -qF "$h" personas/essentialist.md || echo "MISSING $h"
done                                                        # expect: no output
grep -c '^Sources:' personas/essentialist.md                # expect: 8 (one per law subheading)
for t in '--background:' '--accent:' '--radius-' '--border:' 'shadow' 'font'; do
  grep -q -- "$t" personas/essentialist.md || echo "MISSING token group $t"
done                                                        # expect: no output
grep -qF 'Mechanical subset' personas/essentialist.md && echo OK   # expect: OK
grep -qF 'why it had to stay' personas/essentialist.md && echo OK  # expect: OK
```

Then read `personas/essentialist.md` end-to-end once against the corpus: any law without a real grounding in the cited file is removed or re-grounded (constraint: a law that cannot be grounded does not ship).

- [ ] **Step 5: Commit**

```bash
git add personas/ docs/research/personas/essentialist-distillation.md
git commit -m "feat(personas): the Essentialist — distilled Bauhaus/Rams/Ive persona + authoring template"
```

---

### Task 4: Routing — SKILL.md, guidelines-authoring.md, README.md

**Files:**
- Modify: `SKILL.md` (the single-mark bullet, currently line 16; new section inserted after the precedence-chain paragraph, currently line 20)
- Modify: `references/guidelines-authoring.md` (item 0 of "Required structure", currently line 20)
- Modify: `README.md` (repo-map first bullet, currently line 42)

**Interfaces:**
- Consumes: `personas/essentialist.md` from Task 3 (the section names it as the installed persona).
- Produces: the "Persona routing" section header text `## Persona routing` (Task 5's worker transcripts and Task 6's acceptance checks reference it).

- [ ] **Step 1: Amend the single-mark bullet in SKILL.md**

Replace (exact current text):

```markdown
- **Single mark.** A logo, icon, badge, monogram, crest, or standalone illustration. Read `references/icon-illustration.md` instead and skip everything else in this file — a single mark does not need a page-level stance, semantic tokens, or a `DESIGN.md`; it needs its own subject-specific treatment.
```

with:

```markdown
- **Single mark.** A logo, icon, badge, monogram, crest, or standalone illustration. Check the "Persona routing" section below first — an invoked persona governs a mark too — then read `references/icon-illustration.md` instead and skip everything else in this file; a single mark does not need a page-level stance, semantic tokens, or a `DESIGN.md`, it needs its own subject-specific treatment.
```

- [ ] **Step 2: Insert the Persona routing section into SKILL.md**

Insert after the precedence-chain paragraph (the one beginning "Hold the precedence chain verbatim…", line 20), before "## Required first steps (full-page briefs)":

```markdown
## Persona routing

A persona is an optional distilled designer — a governing layer that, when invoked, replaces the sampler run and the stance choice with a committed decision function and its laws. Personas live in `personas/`, one self-contained file each; the persona currently installed is `personas/essentialist.md`, distilled from the Bauhaus → Dieter Rams → Jonathan Ive functionalist lineage.

A persona activates in exactly three cases, never otherwise:

1. **Explicit parameter.** The brief names it: "use the essentialist persona", "persona: essentialist".
2. **Name-match.** The brief literally names the lineage the persona distills: Dieter Rams, Braun, Jony Ive or Ive-era Apple, or the creed "less but better" / "Weniger, aber besser". "Bauhaus" counts only when the brief wants functionalist product or UI design — poster-art phrasings ("Bauhaus-style poster", "Bauhaus graphic") mean the primary-triad poster aesthetic, which is not this lineage, and stay with the normal flow's literal honoring of a named aesthetic.
3. **Recorded persona.** The project's `DESIGN.md` records `persona: <name>`. A recorded persona re-activates on every later turn touching the project — read the persona file again before extending anything, so the judgment layer persists across turns rather than surviving only as tokens.

Generic adjectives — "clean", "minimal", "simple" — never activate a persona; those briefs run the normal sampler flow.

When a persona is active: do not run the sampler — the persona file supplies the stance commitment and its laws in place of steps 2–3 of the required first steps. Read the persona file before any design decision and hold its per-step laws through composition, color, typography, spacing, surfaces, motion, copy, and QA. Record `persona: <name>` at the top of `DESIGN.md`'s stance section, with the persona's laws as project law. Persona laws override reference-file stylistic defaults where they conflict — a one-family type system differentiated by weight and size satisfies the taste floor's type-role rule — but the accessibility floor and `references/qa-protocol.md` bind unconditionally. Persona invocation is brief-level authority: a contradicting brief instruction wins per-surface (record the tension in one line of DESIGN.md), a supplied reference image keeps local authority over its own surface, and an existing design system loses to an explicit persona invocation — that invocation is a redesign instruction; record the conflict in DESIGN.md rather than silently replacing the system. For single marks, the persona governs too: follow `references/icon-illustration.md` for the workflow and the persona file's single-mark clause for its judgment.
```

- [ ] **Step 3: Append the persona field note to guidelines-authoring.md item 0**

Append to the end of item 0 ("**Stance commitment.** …", line 20):

```markdown
 If the project is built under a persona (see SKILL.md's "Persona routing"), open this section with a `persona: <name>` line — that record is load-bearing: any later turn that reads a DESIGN.md carrying a `persona:` line must reload `personas/<name>.md` and work under it, so the persona's judgment and QA lens persist across turns rather than surviving only as tokens.
```

- [ ] **Step 4: Add personas/ to README.md's repo map**

In the first repo-map bullet (line 42, "**Skill files — loaded at runtime by Claude.**"), after the `examples/` parenthetical and before the closing period of the bullet, insert:

```markdown
, and `personas/` (optional distilled designer personas — currently `essentialist.md` — loaded only when a brief invokes one; `personas/TEMPLATE.md` is the authoring contract and is never loaded at runtime)
```

- [ ] **Step 5: Verify**

```bash
grep -qF '## Persona routing' SKILL.md && echo OK                       # expect: OK
grep -qF 'Check the "Persona routing" section below first' SKILL.md && echo OK   # expect: OK
grep -qF 'persona: <name>' references/guidelines-authoring.md && echo OK  # expect: OK
grep -qF 'personas/' README.md && echo OK                               # expect: OK
git diff -U0 SKILL.md | grep '^[+-]description' | wc -l                 # expect: 0 (frontmatter untouched)
node --test scripts/*.test.mjs                                          # expect: all pass (nothing here touches scripts)
```

- [ ] **Step 6: Commit**

```bash
git add SKILL.md references/guidelines-authoring.md README.md
git commit -m "feat(skill): persona routing — activation, persistence, and precedence for distilled personas"
```

---

### Task 5: Eval — seven builds plus one persistence turn

**Controller-executed task** — the eval consists of dispatching worker subagents and running scripts; do not hand this task to a single implementer subagent. All workers: **Sonnet**. Workspace `figma-design-workspace/persona-eval/` is gitignored; nothing in this task is committed.

**Files (all under `figma-design-workspace/persona-eval/`, gitignored):**
- Create: `briefs.md`, `assert-essentialist.sh`, `shoot-persona-eval.sh`, `build-persona-eval-grid.mjs`, and the build directories below.

**Interfaces:**
- Consumes: the installed skill (`~/.claude/skills/figma-design` → this repo) including Task 4's routing section; `personas/essentialist.md` §6 "Mechanical subset" from Task 3 (the assert script mirrors it).
- Produces: `review-persona.html` (the user-review grid) and per-worker reports quoted in Task 6's acceptance walk.

Build matrix (directory → brief → arm):

| Dir | Brief | Persona expected? |
|---|---|---|
| `brief-a/base/` | Brief A as-is | No |
| `brief-a/persona/` | Brief A + "Use the essentialist persona." | Yes |
| `brief-b/base/` | Brief B as-is | No |
| `brief-b/persona/` | Brief B + "Use the essentialist persona." | Yes |
| `name-match/` | Brief C (names Dieter Rams, no parameter) | Yes |
| `neg-minimal/` | Brief D (generic minimal) | **No** |
| `neg-bauhaus/` | Brief E (Bauhaus poster) | **No** |
| `brief-a/persona/` (turn 2) | Persistence turn | Yes (via DESIGN.md record) |

- [ ] **Step 1: Write `briefs.md` with exactly these five briefs**

```markdown
# Persona-eval briefs (verbatim; do not edit between arms)

**Brief A (product UI):** Design a settings and account page for "Meter", a home-energy
monitoring app: current usage, daily/monthly charts, tariff plan, notification
preferences, household members.

**Brief B (marketing):** Design a landing page for "Ledger", a bookkeeping tool for
freelance designers: hero, three feature sections, pricing, FAQ, footer.

**Brief C (name-match):** Design a product page for "Meridian One", a portable speaker,
the way Dieter Rams would — hero, spec sheet, gallery, buy module.

**Brief D (negative, generic minimal):** Design a clean, minimal dashboard for a
customer-support team: open tickets, response times, CSAT, agent load.

**Brief E (negative, Bauhaus poster):** Design a Bauhaus-style poster for a design
conference — "Form & Funktion 2026", October 9–11, Dessau — as a single-page HTML artifact.

**Persistence turn (on brief-a/persona only, after its first build):** Add a
notifications settings page as notifications.html, consistent with the project.
```

- [ ] **Step 2: Dispatch the seven first-turn builds (Sonnet workers, sequential or parallel)**

Worker prompt template — fill `<DIR>` and `<BRIEF>` from the matrix, nothing else:

```
You are building a standalone page. Load and follow the figma-design skill at
~/.claude/skills/figma-design/SKILL.md end to end, exactly as written.

Brief: <BRIEF>

Work directory: /Users/new/Documents/GitHub/SVGF-Design/figma-design-workspace/persona-eval/<DIR>
Produce a self-contained index.html there, plus the DESIGN.md the skill requires
(single-mark deliverables excepted per the skill's own classify step). Real content only.

In your final report, state explicitly: (1) which classify route and stance you
committed; (2) whether you ran scripts/sample-ingredients.mjs, and why; (3) whether
any persona activated, and what triggered or did not trigger it.
```

Record each worker's three-point report — Task 6 quotes them.

- [ ] **Step 3: Dispatch the persistence turn (Sonnet)**

```
Project directory /Users/new/Documents/GitHub/SVGF-Design/figma-design-workspace/persona-eval/brief-a/persona
contains an existing build (DESIGN.md + index.html). Task: add a notifications settings
page as notifications.html, consistent with the project. Load and follow the
figma-design skill at ~/.claude/skills/figma-design/SKILL.md.

In your final report, state explicitly: (1) what DESIGN.md's persona record made you do;
(2) which files you loaded because of it; (3) whether you ran scripts/sample-ingredients.mjs.
```

- [ ] **Step 4: Write and run `assert-essentialist.sh`**

Keep the assertions in sync with `personas/essentialist.md` §6 "Mechanical subset" — if the shipped subset differs from the defaults below, mirror the shipped subset.

```bash
#!/usr/bin/env bash
# Mechanical ban-list assertions for Essentialist persona arms (spec acceptance #1).
# Mirror of personas/essentialist.md §6 "Mechanical subset".
fail=0
for d in "$@"; do
  f="$d/index.html"; [ -f "$f" ] || { echo "MISS $f"; fail=1; continue; }
  ok=1
  n=$(grep -c -- '--accent:' "$f")
  [ "$n" -le 1 ] || { echo "FAIL accent-roles($n)  $f"; ok=0; }
  fams=$(grep -o 'font-family:[^;}]*' "$f" | sort -u | wc -l | tr -d ' ')
  [ "$fams" -le 2 ] || { echo "FAIL font-families($fams)  $f"; ok=0; }
  for p in 'backdrop-filter' 'feTurbulence' 'feDisplacementMap' 'text-shadow'; do
    grep -q "$p" "$f" && { echo "FAIL banned($p)  $f"; ok=0; }
  done
  grep -q 'persona: essentialist' "$d/DESIGN.md" 2>/dev/null || { echo "FAIL persona-record  $d/DESIGN.md"; ok=0; }
  [ $ok -eq 1 ] && echo "PASS $f" || fail=1
done
exit $fail
```

Run:
```bash
cd /Users/new/Documents/GitHub/SVGF-Design
bash figma-design-workspace/persona-eval/assert-essentialist.sh \
  figma-design-workspace/persona-eval/brief-a/persona \
  figma-design-workspace/persona-eval/brief-b/persona \
  figma-design-workspace/persona-eval/name-match
# expect: PASS ×3, exit 0. Also run against notifications.html manually:
grep -o 'font-family:[^;}]*' figma-design-workspace/persona-eval/brief-a/persona/notifications.html | sort -u | wc -l   # expect ≤ 2
```

And the negative direction:
```bash
grep -L 'persona' figma-design-workspace/persona-eval/neg-minimal/DESIGN.md
# expect: filename printed (DESIGN.md exists, records no persona)

# neg-bauhaus may legitimately classify as a single mark and produce no DESIGN.md;
# its no-activation evidence is the worker report (point 3). If a DESIGN.md exists, also:
[ -f figma-design-workspace/persona-eval/neg-bauhaus/DESIGN.md ] \
  && grep -L 'persona' figma-design-workspace/persona-eval/neg-bauhaus/DESIGN.md
```

- [ ] **Step 5: Screenshot all builds — `shoot-persona-eval.sh`**

```bash
#!/usr/bin/env bash
# Render all persona-eval pages to full-page screenshots.
set -u
ROOT="/Users/new/Documents/GitHub/SVGF-Design/figma-design-workspace/persona-eval"
PORT=8747
( cd "$ROOT" && python3 -m http.server "$PORT" >/dev/null 2>&1 ) &
SRV=$!
sleep 1
trap 'kill $SRV 2>/dev/null' EXIT
playwright-cli open >/dev/null 2>&1

shot() {  # $1 = url path relative to ROOT, $2 = output png
  playwright-cli run-code "async page => {
    await page.setViewportSize({width:1440,height:1000});
    await page.goto('http://localhost:${PORT}/$1',{waitUntil:'load'});
    await page.waitForTimeout(800);
    await page.evaluate(async () => {   // scroll through once so reveal-on-scroll content is visible
      await new Promise((res) => {
        let y = 0;
        const step = () => {
          window.scrollTo(0, y);
          y += Math.round(window.innerHeight * 0.75);
          if (y < document.body.scrollHeight) { setTimeout(step, 110); }
          else { window.scrollTo(0, 0); setTimeout(res, 350); }
        };
        step();
      });
    });
    await page.waitForTimeout(600);
    await page.screenshot({path:'$2', fullPage:true});
  }" >/dev/null 2>&1
}

for p in brief-a/base brief-a/persona brief-b/base brief-b/persona name-match neg-minimal neg-bauhaus; do
  [ -f "$ROOT/$p/index.html" ] && shot "$p/index.html" "$ROOT/$p/screenshot-1440.png" \
    && echo "OK $p" || echo "MISS $p"
done
[ -f "$ROOT/brief-a/persona/notifications.html" ] \
  && shot "brief-a/persona/notifications.html" "$ROOT/brief-a/persona/screenshot-notifications-1440.png" \
  && echo "OK persistence-turn"
echo done
```

Run: `bash figma-design-workspace/persona-eval/shoot-persona-eval.sh` — expect `OK` ×8.

- [ ] **Step 6: Build the review grid — `build-persona-eval-grid.mjs`**

```js
#!/usr/bin/env node
// Persona-eval review grid: A/B pairs + singles + persistence turn.
import { writeFileSync, existsSync } from 'node:fs';

const ROOT = '/Users/new/Documents/GitHub/SVGF-Design/figma-design-workspace/persona-eval';
const cell = (dir, label, png = `${dir}/screenshot-1440.png`) => `
  <div class="cell"><div class="cellhead"><span>${label}</span>
    <a href="${dir}/index.html" target="_blank">live page</a></div>
    ${existsSync(`${ROOT}/${png}`) ? `<div class="shot"><img src="${png}" alt=""></div>`
                                   : `<div class="missing">no screenshot</div>`}</div>`;

const html = `<!doctype html><meta charset="utf-8">
<title>Essentialist persona eval</title>
<style>
  body { margin:0; font:15px/1.5 system-ui; padding:24px; background:Canvas; color:CanvasText; }
  h1{font-size:20px;margin:0 0 4px} .note{opacity:.7;margin-bottom:24px}
  section{margin-bottom:40px} h2{font-size:16px;margin:0 0 10px}
  .pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .cell{border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:8px;overflow:hidden}
  .cellhead{display:flex;justify-content:space-between;padding:8px 12px;font-weight:600;
    border-bottom:1px solid color-mix(in srgb,CanvasText 12%,transparent)}
  .cellhead a{font-weight:400} .shot{max-height:640px;overflow-y:auto}
  .shot img{width:100%;display:block} .missing{padding:40px;text-align:center;opacity:.6}
</style>
<h1>Essentialist persona eval</h1>
<p class="note">A/B rows: left = normal flow, right = persona. Singles below. Success test: the persona arms read as one committed functionalist voice — reduced, exact, quiet — without losing the base skill's craft floor.</p>
<section><h2>Brief A — Meter, energy-app settings (product UI)</h2>
  <div class="pair">${cell('brief-a/base','figma-design alone')}${cell('brief-a/persona','+ essentialist persona')}</div></section>
<section><h2>Brief B — Ledger, bookkeeping landing (marketing)</h2>
  <div class="pair">${cell('brief-b/base','figma-design alone')}${cell('brief-b/persona','+ essentialist persona')}</div></section>
<section><h2>Name-match — "the way Dieter Rams would" (must activate)</h2>
  <div class="pair">${cell('name-match','persona via name-match')}
  ${cell('brief-a/persona','persistence turn — notifications page','brief-a/persona/screenshot-notifications-1440.png')}</div></section>
<section><h2>Negative controls (must NOT activate)</h2>
  <div class="pair">${cell('neg-minimal','generic "clean, minimal" — sampler flow')}${cell('neg-bauhaus','Bauhaus poster — literal aesthetic, not Essentialist')}</div></section>`;
writeFileSync(`${ROOT}/review-persona.html`, html);
console.log('wrote', `${ROOT}/review-persona.html`);
```

Run: `node figma-design-workspace/persona-eval/build-persona-eval-grid.mjs` — expect `wrote …/review-persona.html`.

---

### Task 6: Final verification — acceptance walk, user gate, spec tail

**Controller-executed.** Quote of the spec's acceptance section is authoritative; each criterion below names its evidence.

**Files:**
- Modify: `docs/doperpowers/specs/2026-07-27-persona-layer-design.md` (eval verdict, Outcomes & Retrospective, Revision Notes)

- [ ] **Step 1: Walk acceptance criteria 1–6 against evidence**

1. *"A full-page brief containing 'use the essentialist persona' produces a build whose DESIGN.md records `persona: essentialist` plus the persona's laws as project law, whose transcript shows the sampler was **not** run, and whose page passes the persona's mechanical law checks"* — evidence: `brief-a/persona` and `brief-b/persona` worker reports (point 2 = sampler not run; point 3 = persona activated) + `assert-essentialist.sh` PASS lines.
2. *"A follow-up turn … re-activates the persona without the brief re-naming it"* — evidence: persistence-turn report (points 1–2 name DESIGN.md's record and `personas/essentialist.md` loaded) + the notifications.html font-family check.
3. *"…'design this the way Dieter Rams would' (no persona parameter) routes to the persona"* — evidence: `name-match` worker report + assert PASS.
4. *"'clean, minimal dashboard' does **not** activate … 'Bauhaus-style poster' also does **not** activate"* — evidence: `neg-minimal` and `neg-bauhaus` reports (sampler ran; no persona) + the `grep -L 'persona'` check on both DESIGN.md files.
5. *Template conformance* — re-run Task 3 Step 4's grep block verbatim; expect the same clean output.
6. *Corpus provenance* — run:
   ```bash
   grep -L 'accessed:' docs/research/personas/essentialist/*.md   # expect: no output
   ls docs/research/personas/essentialist/ | wc -l                # expect: 11
   ```

Also run the full suite: `node --test scripts/*.test.mjs` — expect all pass.

- [ ] **Step 2: USER GATE — acceptance criterion 7**

Present `figma-design-workspace/persona-eval/review-persona.html` to the user (serve it locally; give the URL). Ask for the verdict on: (a) do the persona arms read as one committed functionalist voice; (b) do the A/B pairs show the persona adding a real, distinct direction rather than a grayer version of the base arm; (c) any arm to rerun. **Do not proceed until the user answers.**

- [ ] **Step 3: Record the verdict and close the spec tail**

In `docs/doperpowers/specs/2026-07-27-persona-layer-design.md`: record the user's eval verdict under `## Surprises & Discoveries` (or a dedicated eval-verdict line under acceptance if clean); replace `## Outcomes & Retrospective`'s "Pending — written at finish." with the actual outcome (what shipped, what the eval showed, what surprised); add a `## Revision Notes` line dated with the eval completion.

- [ ] **Step 4: Commit**

```bash
git add docs/doperpowers/specs/2026-07-27-persona-layer-design.md
git commit -m "docs(spec): persona layer — eval verdict and outcomes"
```
