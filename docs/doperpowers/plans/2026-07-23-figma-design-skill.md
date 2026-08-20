# figma-design Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use doperpowers:subagent-driven-development (recommended) or doperpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `figma-design` Agent Skill — a faithful, runtime-neutral replica of Figma Make's UI-design workflow (SKILL.md + ingredient sampler script + 11 references + examples), then eval it via the skill-creator loop.

**Architecture:** The repo root IS the skill. A zero-dependency Node script replicates Figma's `create_make_theme` entropy sampler over verbatim-extracted ingredient libraries; SKILL.md carries the workflow spine (classify → sample → commit stance → author project DESIGN.md → tokens → composition → build → QA); 11 progressive-disclosure references carry the craft layers, distilled from the interview corpus in `Figma Design/`; a quarantined `taste-calibration.md` carries 2026 anti-slop grafts from frontend-design and impeccable.

**Tech Stack:** Markdown (skill content), Node ≥18 zero-dependency ESM + `node:test` (sampler), playwright-cli (visual verification), skill-creator plugin (evals).

## Global Constraints

- Spec: `docs/doperpowers/specs/2026-07-23-figma-design-skill-design.md`. On conflict, fix the spec and log in its `## Revision Notes` — never silently diverge.
- SKILL.md body: 1,500–2,000 words (hard range 1,400–2,200 by `wc -w`).
- The 11 reference filenames are a locked contract: `stances.md`, `color-engineering.md`, `typography.md`, `motion.md`, `composition.md`, `effects-policy.md`, `voice-copy.md`, `guidelines-authoring.md`, `icon-illustration.md`, `qa-protocol.md`, `taste-calibration.md` — all under `references/`.
- Sampler: zero runtime dependencies, plain Node ≥18 ESM. No npm install anywhere in this plan.
- Figma-verbatim data (stance descriptions, tradition examples, canvas names, card frame text) must be copied character-exact from this plan / the corpus — no rewording.
- Runtime neutrality: no reference to Figma Make's file contract (`src/app/App.tsx`, `theme.css` paths, `motion/react`, Make Kits) anywhere in SKILL.md or references, except as attributed historical notes.
- SKILL.md and references must never point into `Figma Design/` or `docs/` (corpus and specs are not loaded at runtime).
- `taste-calibration.md` must attribute its two sources (Anthropic frontend-design, per its LICENSE.txt; impeccable, Apache 2.0).
- Commits: one per task minimum, message style `feat(skill): …` / `docs: …`, **no Co-Authored-By or attribution lines**.
- Corpus source files (read-only inputs):
  - `Figma Design/Interview Round 2 Result.md` (8,191 lines; "R2")
  - `Figma Design/Interview Round 3 - Prompts.md` (2,263 lines; "R3" — results are embedded under each `## R3-Px` heading)
  - `Figma Design/Interview Round 4 - Final Gap Prompts.md` ("R4")
  - `Figma Design/Interview Round 4b - Addendum.md` ("R4b")
  - `docs/research/figma-core-plus-grafts.md` (graft synthesis)
  - `/Users/new/.claude/plugins/cache/claude-plugins-official/frontend-design/unknown/skills/frontend-design/SKILL.md`
  - `/Users/new/.claude/skills/impeccable/SKILL.md`

---

### Task 1: Ingredient library — `scripts/ingredients.json`

**Files:**
- Create: `scripts/ingredients.json`

**Interfaces:**
- Produces: JSON object `{ stances: [{name, description, origin}], typographyTraditions: [{name, examples, origin}], canvasTreatments: [{name, origin}] }`. Consumed by Task 2's sampler and its tests. Exactly 10 stances, 13 traditions, 5 canvases carry `"origin": "figma"`; 8 stances carry `"origin": "extension"`.

- [ ] **Step 1: Write the file** with exactly this content (Figma entries are verbatim from R3 lines 421–472; extension entries are authored here, final):

```json
{
  "stances": [
    { "name": "archival", "description": "MoMA catalogs, Rijksmuseum. Numbered sections, serif/mono pairings, textured neutrals, reverent composition.", "origin": "figma" },
    { "name": "brutalist", "description": "Bloomberg Businessweek online, brutalistwebsites.com. Raw mono type, stark black/white, hot accent, deliberately unstyled-looking but composed.", "origin": "figma" },
    { "name": "data-dense", "description": "Bloomberg Terminal, FlightRadar. Small tabular fonts, maximum information density, functional color coding, little whitespace.", "origin": "figma" },
    { "name": "editorial", "description": "Monocle, The Gentlewoman, Kinfolk. Serif display + sans body, asymmetric column grids, generous margins, feature photography, warm neutral palettes.", "origin": "figma" },
    { "name": "kinetic", "description": "Pentagram motion reels, Apple product reveals. Motion is primary; often dark with light motion highlights.", "origin": "figma" },
    { "name": "maximalist", "description": "Zine aesthetic, scrap-and-tape. Mixed type, overlapping elements, deliberately layered hierarchy.", "origin": "figma" },
    { "name": "memphis", "description": "Ettore Sottsass. Geometric shapes on pastels, primary accents, asymmetric, playful without childish.", "origin": "figma" },
    { "name": "minimalist", "description": "Apple, Aesop, Teenage Engineering product pages. One hero element, tight type, lots of whitespace, single accent.", "origin": "figma" },
    { "name": "swiss", "description": "Vignelli, Jost Hochuli, Helvetica. Strict grid, mostly neutrals plus one accent, precise alignment, function declares the aesthetic.", "origin": "figma" },
    { "name": "warm", "description": "Aesop, Le Labo, boutique hospitality. Cream bases, muted earth tones, serif type, tactile-feeling imagery.", "origin": "figma" },
    { "name": "risograph", "description": "Riso zine printing, People of Print. Two-ink overprint, visible grain, slight misregistration, flat saturated spot colors on uncoated stock.", "origin": "extension" },
    { "name": "terminal", "description": "tmux dashboards, btop, Berkeley Graphics. Monospace everything, box-drawing rules, one phosphor accent on near-black, the information is the interface.", "origin": "extension" },
    { "name": "bauhaus", "description": "Bauhaus Dessau, Braun under Rams. Primary geometry, grid-locked composition, functional color blocking, zero ornament.", "origin": "extension" },
    { "name": "y2k-web", "description": "Frutiger Aero, early-2000s consumer web. Glossy depth, aqua gradients, rounded chrome, technological optimism.", "origin": "extension" },
    { "name": "luxury-fashion", "description": "Céline campaigns, The Row lookbooks. Extreme whitespace, Didone display, monochrome photography, hairline everything.", "origin": "extension" },
    { "name": "deco", "description": "Art Deco poster lithography, hotel signage. Stepped geometry, metallic accents, symmetry, vertical emphasis.", "origin": "extension" },
    { "name": "vernacular", "description": "Hand-painted shop signs, county-fair flyers. Loud type mixing, decorative borders, honest clutter, unpolished warmth.", "origin": "extension" },
    { "name": "topographic", "description": "USGS quadrangles, Swiss hiking maps, NASA mission graphics. Contour lines, coordinate grids, annotation typography, terrain palettes.", "origin": "extension" }
  ],
  "typographyTraditions": [
    { "name": "Blackletter / gothic", "examples": "Fraktur derivatives, Cloister, Wilhelm Klingspor Gotisch", "origin": "figma" },
    { "name": "Condensed / expressive display", "examples": "Druk, PP Right Grotesk, Founders Grotesk Condensed", "origin": "figma" },
    { "name": "Didone / high-contrast serif", "examples": "Bodoni, Didot, Noe Display, GT Sectra lineage", "origin": "figma" },
    { "name": "Geometric sans", "examples": "Futura, Avenir, Nunito", "origin": "figma" },
    { "name": "Glyphic serif", "examples": "Trajan, Albertus", "origin": "figma" },
    { "name": "Humanist sans", "examples": "Gill Sans, Gotham, Proxima Nova", "origin": "figma" },
    { "name": "Humanist serif", "examples": "Plantin, Sabon, Freight Text", "origin": "figma" },
    { "name": "Monospace-as-display", "examples": "JetBrains Mono, Berkeley Mono, Fira Code", "origin": "figma" },
    { "name": "Neo-grotesque sans", "examples": "Helvetica, Univers, Aktiv Grotesk", "origin": "figma" },
    { "name": "Old-style serif", "examples": "Garamond, Caslon, Minion, Janson", "origin": "figma" },
    { "name": "Script / calligraphic", "examples": "Didot Italic swashes, formal cursive — use sparingly", "origin": "figma" },
    { "name": "Slab serif", "examples": "Tiempos Text, Roboto Slab, Rockwell", "origin": "figma" },
    { "name": "Transitional serif", "examples": "Baskerville, Times, Charter", "origin": "figma" }
  ],
  "canvasTreatments": [
    { "name": "dark mode", "origin": "figma" },
    { "name": "gradient or mesh background", "origin": "figma" },
    { "name": "heavily-colored (full-page saturated canvas)", "origin": "figma" },
    { "name": "textured paper / cream", "origin": "figma" },
    { "name": "two-tone split (vertical or diagonal canvas divide)", "origin": "figma" }
  ]
}
```

- [ ] **Step 2: Validate JSON parses and counts are right**

Run: `node -e "const l=JSON.parse(require('fs').readFileSync('scripts/ingredients.json','utf8')); console.log(l.stances.length, l.stances.filter(s=>s.origin==='figma').length, l.typographyTraditions.length, l.canvasTreatments.length)"`
Expected: `18 10 13 5`

- [ ] **Step 3: Commit**

```bash
git add scripts/ingredients.json
git commit -m "feat(skill): add ingredient library (figma-verbatim + 8 extension stances)"
```

---

### Task 2: Sampler script — `scripts/sample-ingredients.mjs` (TDD)

**Files:**
- Create: `scripts/sample-ingredients.mjs`
- Test: `scripts/sample-ingredients.test.mjs`

**Interfaces:**
- Consumes: `scripts/ingredients.json` (Task 1 shape).
- Produces: CLI `node scripts/sample-ingredients.mjs [--seed <int>]` printing the ingredients card to stdout: verbatim preamble, 3 stances, 2 typography traditions, 1 canvas treatment, verbatim "YOUR TASK" close. Seeded runs are deterministic. SKILL.md (Task 3) instructs agents to run exactly this command.

- [ ] **Step 1: Write the failing tests**

```js
// scripts/sample-ingredients.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

const run = (args = []) =>
  execFileSync("node", ["scripts/sample-ingredients.mjs", ...args], { encoding: "utf8" });

test("emits the verbatim card frame", () => {
  const out = run(["--seed", "7"]);
  assert.ok(out.startsWith("Here are some aesthetic ingredients to consider for this user's project."));
  assert.match(out, /Lean especially toward these directions to break out of trained defaults\. Treat them as tiebreakers when the brief is silent on aesthetic, not overrides — if the brief explicitly names an aesthetic, honor it literally\. If two directions feel equally plausible, pick the less-common one\./);
  assert.match(out, /YOUR TASK: Combine any preferences the user expressed with these directions to make a great theme for them\. Be opinionated and specific\. Commit to one stance — the most memorable outputs come from full commitment to one direction rather than hedging\.\s*$/);
});

test("draws exactly 3 stances, 2 traditions, 1 canvas, no duplicates", () => {
  const out = run(["--seed", "42"]);
  const stances = out.match(/^\d\. \*\*[^*]+\*\* — .+$/gm) ?? [];
  assert.equal(stances.length, 3);
  assert.equal(new Set(stances).size, 3);
  const traditionsSection = out.split("**Typography traditions:**")[1].split("**Canvas treatment:**")[0];
  const traditions = traditionsSection.match(/^\d\. .+ \(.+\)$/gm) ?? [];
  assert.equal(traditions.length, 2);
  assert.match(out, /\*\*Canvas treatment:\*\*\n1\. .+/);
});

test("same seed reproduces the draw; different seeds diverge", () => {
  assert.equal(run(["--seed", "7"]), run(["--seed", "7"]));
  const a = run(["--seed", "1"]);
  const b = run(["--seed", "2"]);
  const c = run(["--seed", "3"]);
  assert.ok(a !== b || b !== c, "three different seeds all produced identical draws");
});

test("library integrity: figma-verbatim entries intact", () => {
  const lib = JSON.parse(readFileSync("scripts/ingredients.json", "utf8"));
  assert.equal(lib.stances.filter((s) => s.origin === "figma").length, 10);
  assert.equal(lib.typographyTraditions.length, 13);
  assert.equal(lib.canvasTreatments.length, 5);
  assert.ok(lib.stances.length >= 16);
  const warm = lib.stances.find((s) => s.name === "warm");
  assert.equal(
    warm.description,
    "Aesop, Le Labo, boutique hospitality. Cream bases, muted earth tones, serif type, tactile-feeling imagery."
  );
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test scripts/*.test.mjs`
Expected: 4 failing tests (module not found / ENOENT for `sample-ingredients.mjs`).

- [ ] **Step 3: Write the implementation**

```js
#!/usr/bin/env node
// scripts/sample-ingredients.mjs — replicates Figma Make's create_make_theme sampler.
import { readFileSync } from "node:fs";
import { randomInt } from "node:crypto";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const lib = JSON.parse(readFileSync(join(here, "ingredients.json"), "utf8"));

const seedIdx = process.argv.indexOf("--seed");
const seed = seedIdx !== -1 ? Number(process.argv[seedIdx + 1]) : null;

function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const rand =
  seed === null
    ? (max) => randomInt(max)
    : (() => {
        const r = mulberry32(seed);
        return (max) => Math.floor(r() * max);
      })();

function draw(pool, n) {
  const copy = [...pool];
  const out = [];
  while (out.length < n) out.push(copy.splice(rand(copy.length), 1)[0]);
  return out;
}

const stances = draw(lib.stances, 3);
const traditions = draw(lib.typographyTraditions, 2);
const [canvas] = draw(lib.canvasTreatments, 1);

const lines = [
  "Here are some aesthetic ingredients to consider for this user's project.",
  "",
  "Lean especially toward these directions to break out of trained defaults. Treat them as tiebreakers when the brief is silent on aesthetic, not overrides — if the brief explicitly names an aesthetic, honor it literally. If two directions feel equally plausible, pick the less-common one.",
  "",
  "**Stances to consider:**",
  ...stances.map((s, i) => `${i + 1}. **${s.name}** — ${s.description}`),
  "",
  "**Typography traditions:**",
  ...traditions.map((t, i) => `${i + 1}. ${t.name} (${t.examples})`),
  "",
  "**Canvas treatment:**",
  `1. ${canvas.name}`,
  "",
  "YOUR TASK: Combine any preferences the user expressed with these directions to make a great theme for them. Be opinionated and specific. Commit to one stance — the most memorable outputs come from full commitment to one direction rather than hedging.",
];

console.log(lines.join("\n"));
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test scripts/*.test.mjs`
Expected: `# pass 4`, `# fail 0`

- [ ] **Step 5: Commit**

```bash
git add scripts/sample-ingredients.mjs scripts/sample-ingredients.test.mjs
git commit -m "feat(skill): add create_make_theme-replica sampler with seeded determinism"
```

---

### Task 3: SKILL.md

**Files:**
- Create: `SKILL.md`

**Interfaces:**
- Consumes: sampler CLI from Task 2 (`node scripts/sample-ingredients.mjs`).
- Produces: the always-loaded skill body. Its routing table names the 11 locked reference filenames (Global Constraints) — Tasks 4–14 must create exactly those files. Its workflow step names ("classify", "sample", "commit", "DESIGN.md", "tokens", "composition", "build", "QA") are referenced by `qa-protocol.md` and the eval assertions (Tasks 18–19).

- [ ] **Step 1: Author SKILL.md** with this exact frontmatter and section structure (prose written fresh, 1,500–2,000 words; modeled on the captured aesthetic-stance skeleton at R3 lines 536–633 and rulebook R2 lines 4551–4848, generalized per spec):

Frontmatter (verbatim):

```yaml
---
name: figma-design
description: This skill should be used whenever the user asks to design, build, redesign, restyle, or improve any user interface or visual artifact — landing pages, marketing sites, dashboards, product UI, app shells, admin tools, portfolios, multi-section pages, or single graphic marks (logos, icons, badges, illustrations). Use it even when the user does not say "design" — building any new frontend surface counts, as does "make it look better", "make a page for X", or "create a logo". Not for backend-only or non-visual tasks.
version: 0.1.0
---
```

Required H2 sections, each with its must-contain content:

1. `## Classify the deliverable` — four routes: full page / multi-section UI (this workflow); single mark (read `references/icon-illustration.md` instead, skip everything else); existing design system present in project (use it — do NOT run the sampler; the system is global authority); supplied reference image or imported design (reproduce its visual language faithfully for that surface; it has local authority only). State the precedence chain verbatim: *"User brief wins per-surface > supplied reference (local) > existing design system (global) > sampled ingredients (only when no system exists) > your own defaults (the floor)."*
2. `## Required first steps (full-page briefs)` — numbered: (1) read the project's existing conventions — tokens, components, stack, styling approach — before designing; (2) run `node scripts/sample-ingredients.mjs` (path relative to this skill's directory) and treat its output per its own preamble; (3) commit to exactly one stance in writing before any UI code; (4) author the project design law (`DESIGN.md`, per `references/guidelines-authoring.md`) before any UI code. Include the line: *"If the brief explicitly names an aesthetic — including a common one — honor it literally; ingredients are tiebreakers, never overrides."*
3. `## The workflow spine` — the eight steps in order, one short paragraph each, each pointing at its reference file: parse brief (product, audience, task, content, constraints) → sample ingredients → commit one stance → author DESIGN.md → build semantic tokens (`references/color-engineering.md`, `references/typography.md`, `references/stances.md`) → information architecture and composition (`references/composition.md`) → build with realistic content (`references/voice-copy.md`; never lorem ipsum) → craft pass (`references/motion.md`, `references/effects-policy.md`) → QA (`references/qa-protocol.md`).
4. `## Taste floor` — always-on rules distilled from R2 rulebook: commit-don't-blend; accent color does real work only (action, selection, focus, status); realistic content always; hierarchy before decoration; borders organize rather than bully; whitespace is functional; accessibility floor (4.5:1 body, 3:1 large text and controls, never color alone, visible focus); at least one responsive breakpoint with intentional collapse. Close with pointer: *"Before shipping anything, check `references/taste-calibration.md` — it names the currently saturated AI-default looks that read as generated."*
5. `## Runtime adaptation` — detect and match the project's stack; if none exists default to a single self-contained HTML file; semantic-token pattern is mandatory but file locations adapt to the project; keep token values in one place and usage rules in DESIGN.md.
6. `## Reference routing` — table of all 11 references with one-line when-to-read guidance.

- [ ] **Step 2: Verify structure and length**

Run: `wc -w SKILL.md` — Expected: between 1400 and 2200.
Run: `grep -c 'references/' SKILL.md` — Expected: ≥ 12 (all 11 files named at least once).
Run: `grep -n 'sample-ingredients.mjs' SKILL.md` — Expected: at least one hit.
Run: `grep -n 'honor it literally' SKILL.md` — Expected: at least one hit.

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat(skill): add SKILL.md workflow spine"
```

---

### Task 4: `references/stances.md`

**Files:**
- Create: `references/stances.md`

**Interfaces:**
- Produces: stance library consumed at design time. Section names must use the stance `name` values from `scripts/ingredients.json` so agents can look up a sampled stance directly.

- [ ] **Step 1: Author the file.** Structure:
  - Intro (¶): a stance is a committed visual system, not a mood; how to use this file (look up the committed stance; if it's an extension stance with no full system here, derive one using the per-area procedure files).
  - `## Five complete systems` — port the five R2-P2 systems **with all values intact** (R2 lines 25–793): Precision industrial, Quiet editorial, Contemporary craft commerce, Institutional calm, Playful consumer. For each: the full CSS token block (colors, radius, borders, shadows, spacing, typography, motion) and its implementation-rules paragraph, converted from Figma's `--token` conventions only where needed to stay runtime-neutral (keep custom-property syntax; drop nothing).
  - `## Component character per stance` — distill R2-P6 (R2 lines 3338–3910): the button/card/table implementations compared across three stances; keep the code, trim narration.
  - `## Mapping sampled stances to systems` — table mapping all 18 `ingredients.json` stances to either one of the five complete systems (e.g. `swiss` → Precision industrial variant, `warm` → Contemporary craft commerce variant) or "derive fresh" with 2–3 sentence derivation hints for each extension stance (which ground temperature, which typography tradition fits, what the accent should do).
  - Closing rule: never blend two systems; derive, commit, and record the result in the project DESIGN.md.

- [ ] **Step 2: Verify**

Run: `grep -c '^## ' references/stances.md` — Expected: ≥ 4.
Run: `grep -n 'Precision industrial\|Playful consumer' references/stances.md | head -4` — Expected: hits for both.
Run: `grep -n -- '--background' references/stances.md | head -2` — Expected: token blocks present.

- [ ] **Step 3: Commit**

```bash
git add references/stances.md
git commit -m "feat(skill): add stance library reference"
```

---

### Task 5: `references/color-engineering.md`

**Files:**
- Create: `references/color-engineering.md`

- [ ] **Step 1: Author the file** from R2-P5's real content (R2 lines 2566–3337 — NOTE: lines 2095–2565 are an accidental duplicate of the typography answer; skip them). Required sections:
  - `## Think in OKLCH` — the L/C/H model and why (verbatim-adapt R2 lines 2568–2588).
  - `## The construction sequence` — the 9-step order (R2 lines 2591–2607), kept as a numbered list.
  - `## Neutral ramps` — warm-paper ramp and cool-technical ramp with **all OKLCH values** (R2 lines 2635–2698) and the non-uniform-lightness-steps rationale.
  - `## Choosing the accent` — product-to-accent heuristics table + per-stance chroma limits table (R2 lines 2712–2737), values intact.
  - `## Validation` — text contrast, role contrast, color-blind resilience, in-context saturation checks (R2 lines 2741–2804).
  - `## Dark mode: derive, do not invert` — all 7 rules with their numeric ranges (R2 lines 2808–2890).
  - `## Chart series` — sequential/diverging/categorical rules (R2 lines 2893–2951).
  - `## Worked example` — condense the film-studio end-to-end (R2 lines 2954–3337) to ~40 lines keeping the ramp values and final token assignments.

- [ ] **Step 2: Verify**

Run: `grep -c 'oklch(' references/color-engineering.md` — Expected: ≥ 15.
Run: `grep -n 'derive, do not invert\|Derive, do not invert' references/color-engineering.md` — Expected: 1 hit.

- [ ] **Step 3: Commit**

```bash
git add references/color-engineering.md
git commit -m "feat(skill): add OKLCH color-engineering reference"
```

---

### Task 6: `references/typography.md`

**Files:**
- Create: `references/typography.md`

- [ ] **Step 1: Author the file** from R2-P4 (R2 lines 1619–2092). Required sections:
  - `## Selection order` — existing system → project fonts → Google Fonts → system fallbacks.
  - `## The curated library` — all eight register tables (display serif, humanist sans, grotesk, geometric sans, expressive display, slab, mono) with their use/register columns intact.
  - `## Ten strong pairings` — all ten pairings with stance/why/use rows.
  - `## Overused defaults` — both blacklist tables (faces and pairings) plus the rule "reject when used as a substitute for art direction, not because popular".
  - `## Operational scales` — the dense-operational-tool table and the editorial-landing scale (R2 lines 1864–1985) with px values, weights, line-heights, tracking.
  - `## Case behavior` — uppercase-label rules with exact size/tracking values (R2 lines 1986–2560 relevant subsections; the mobile floor rule "never below 10px").
  - `## Family-count rule` — 1 family for dense tools (+mono), 2 for landing pages, 3 only with a real data role.

- [ ] **Step 2: Verify**

Run: `grep -n 'Newsreader\|Bricolage' references/typography.md | head -3` — Expected: hits.
Run: `grep -n 'Space Grotesk' references/typography.md` — Expected: appears in the overused-defaults section.

- [ ] **Step 3: Commit**

```bash
git add references/typography.md
git commit -m "feat(skill): add typography reference"
```

---

### Task 7: `references/motion.md`

**Files:**
- Create: `references/motion.md`

- [ ] **Step 1: Author the file** from R2-P7 (R2 lines 3911–4550). Required sections:
  - `## Duration tiers` — the six-tier table (80/120/180/240/320/420ms) with use rows and the application-rules block.
  - `## Easing curves` — all named cubic-beziers with the when-to-use table; spring-overshoot allowed/forbidden lists.
  - `## Properties` — animate-regularly table and do-not-animate table with reasons.
  - `## Per-stance motion` — 3–4 rows distilled from R2-P7's stance guidance (editorial vs operational vs playful).
  - `## Reduced motion` — mandatory alternative for every nonessential animation.
  - Implementation note: prefer CSS transitions/keyframes; use a JS motion library only for mount/unmount coordination or gestures (name none — runtime-neutral).

- [ ] **Step 2: Verify**

Run: `grep -c 'cubic-bezier' references/motion.md` — Expected: ≥ 6.
Run: `grep -n 'prefers-reduced-motion' references/motion.md` — Expected: ≥ 1 hit.

- [ ] **Step 3: Commit**

```bash
git add references/motion.md
git commit -m "feat(skill): add motion reference"
```

---

### Task 8: `references/composition.md`

**Files:**
- Create: `references/composition.md`

- [ ] **Step 1: Author the file** from R3-P7 (R3 lines 1733–1970) + R2-P11 (R2 lines 6498–7394) + the useful generalizable core of R3-P3's image-attachment module (R3 lines 821–922). Required sections:
  - `## Hero archetypes` — every archetype from R3-P7 with its grid-template code, when-earned, collapse behavior, and failure mode.
  - `## Dashboard arrangements` — the named arrangements (exception-first, primary-metric + rail, table-led, map-led) with grid definitions.
  - `## Content, detail, and commerce patterns` — from R3-P7.
  - `## How to pick` — the brief-signal → pattern selection logic from R3-P7's closing section.
  - `## Imagery integration` — from R2-P11: search/selection criteria, crop/aspect rules per slot, overlay/scrim/duotone recipes with values, when to use generated SVG instead of photos, the distinguished-vs-generic hero comparison.
  - `## Working from a supplied reference` — generalized from R3-P3 image-attachments: determine the image's role first (reproduce vs inspiration vs asset), inspect before coding, reproduction priority order (geometry → palette → type → texture), reference wins over personal defaults for its surface.

- [ ] **Step 2: Verify**

Run: `grep -c 'grid-template' references/composition.md` — Expected: ≥ 4.
Run: `grep -n 'exception-first\|Exception-first' references/composition.md` — Expected: ≥ 1 hit.

- [ ] **Step 3: Commit**

```bash
git add references/composition.md
git commit -m "feat(skill): add composition + imagery reference"
```

---

### Task 9: `references/effects-policy.md`

> **Superseded 2026-08-21.** Task 9 shipped as written, but the file has since dropped every
> SVG-filter section: the primitive catalog is gone, grain is a generated tile, and refraction
> defers to WebGL. The `feTurbulence` acceptance check in Step 2 is expected to fail against the
> current file and must not be "fixed" by restoring the filters.

**Files:**
- Create: `references/effects-policy.md`

- [ ] **Step 1: Author the file** from R2-P3 (R2 lines 794–1618). Required sections:
  - `## When an effect is earned` — the 7-condition framework verbatim-adapted (semantic role, stance fit, product fit, localized, legible, fallback, performance budget) + the removal test quote.
  - Per-effect sections, each with when-earned / when-not lists and the complete shippable code from R2-P3: `## Glass` (frosted-surface CSS incl. fallback + prefers-contrast), `## Gradients` (atmospheric + data-intensity recipes), `## Grain` (SVG-noise data-URI recipe + practical values: opacity 0.025–0.08, tile 128–256px, never animate), `## Glow` (live-control recipe), `## Organic shapes` (deliberate backdrop + explicit SVG path), `## Displacement and refraction` (liquid-glass filter + the "non-essential artwork only" boundary).
  - `## SVG filter primitives: positions` — the per-primitive verdicts and code (feTurbulence static-only; feDisplacementMap rarely; goo very-rarely with the full goo filter code; feSpecularLighting almost-never; feDropShadow commonly-but-gently).
  - `## Worked contrasts` — both before/afters (video-editor glass earned; dashboard animated gradient removed) condensed, keeping the code.
  - `## The three questions` — closing rule of thumb verbatim.
  - Footer note: *"This policy is deliberately conservative. A companion skill for SVG-filter material design extends it where the product genuinely earns richer materials."*

- [ ] **Step 2: Verify**

Run: `grep -c 'feTurbulence\|feDisplacementMap\|feColorMatrix' references/effects-policy.md` — Expected: ≥ 6.
Run: `grep -n 'backdrop-filter' references/effects-policy.md | head -2` — Expected: hits.

- [ ] **Step 3: Commit**

```bash
git add references/effects-policy.md
git commit -m "feat(skill): add earned-effects policy reference"
```

---

### Task 10: `references/voice-copy.md`

**Files:**
- Create: `references/voice-copy.md`

- [ ] **Step 1: Author the file** from R3-P8 (R3 lines 1971–2060) + frontend-design's writing section (its SKILL.md "More on writing in design", attributed). Required sections:
  - `## Believable data` — per-domain plausibility rules (non-round arithmetic-consistent budgets, causally-ordered dates, domain-correct names/labels).
  - `## Voice per stance` — the four-stance worked set (same hero headline + CTA + empty state + error, four ways) from R3-P8.
  - `## Microcopy rules` — verb+object buttons; action keeps its name through the flow; standalone-meaning links; sentence case default; label/tooltip phrasing; error anatomy (what happened, data lost?, next step); empty states invite action.
  - `## Length heuristics` — hero subhead / card description / section intro limits from R3-P8.
  - `## Writing as design material` — adapted from frontend-design (attributed in a footer line): user-side naming, active voice, one job per element.

- [ ] **Step 2: Verify**

Run: `grep -n 'verb' references/voice-copy.md | head -2` — Expected: button-verb rule present.
Run: `grep -in 'frontend-design' references/voice-copy.md` — Expected: attribution line present.

- [ ] **Step 3: Commit**

```bash
git add references/voice-copy.md
git commit -m "feat(skill): add voice and copy reference"
```

---

### Task 11: `references/guidelines-authoring.md`

**Files:**
- Create: `references/guidelines-authoring.md`

**Interfaces:**
- Produces: the DESIGN.md authoring procedure that SKILL.md's "Required first steps" mandates. Section structure it prescribes must match the two examples (Task 15).

- [ ] **Step 1: Author the file** from R4 FRAME (R4 lines 15–126), R4b MERIDIAN, and R3-P2's guidance. Required sections:
  - `## Why a design law` — the values-vs-usage split: the tokens file owns *values*; DESIGN.md owns *usage*; when they disagree, tokens win for values, DESIGN.md wins for usage. Drift on turn 5 happens when neither is reloaded.
  - `## Required structure` — the section skeleton both examples share: (0) Stance commitment — one committed idea + the ambiguity tiebreaker line ("if a decision is ever ambiguous, choose the more X option"); (1) Palette with usage rules; (2) Typography roles with placement rules; (3) Canvas & texture; (4) Layout system; (5) Component canon (named canonical components; build order); (6) Voice; (7) Motion; (8) Hard don'ts.
  - `## Authoring rules` — write it before any UI code; every rule must be checkable against code; include what is *forbidden*, not just preferred; keep it under ~120 lines; record the sampled ingredients you rejected and why (one line).
  - `## Worked examples` — pointer to `examples/guidelines-frame.md` and `examples/guidelines-meridian.md` with the one-brief-two-systems framing.

- [ ] **Step 2: Verify**

Run: `grep -n 'Stance commitment' references/guidelines-authoring.md` — Expected: ≥ 1 hit.
Run: `grep -n 'Hard don' references/guidelines-authoring.md` — Expected: ≥ 1 hit.

- [ ] **Step 3: Commit**

```bash
git add references/guidelines-authoring.md
git commit -m "feat(skill): add DESIGN.md authoring reference"
```

---

### Task 12: `references/icon-illustration.md`

**Files:**
- Create: `references/icon-illustration.md`

- [ ] **Step 1: Author the file**: copy the verbatim-captured skill body (R4 lines 184–294, everything after the frontmatter block) with exactly two edits: (a) replace the `## Output mechanics` bullet "Write to `src/app/App.tsx`…" with runtime-neutral wording: "Render one self-contained `<svg>` in whatever file the project calls for (a standalone `.svg`, an inline component, or an HTML page); do not fragment a single mark across files."; (b) append a `## Execution mechanics` section distilled from R2-P12 (R2 lines 7395–8191): grid construction (64×64 canvas default), primitives-vs-paths choice, stroke-vs-fill defaults with scale-floor stroke math (`strokeWidth / canvas × displaySize`), optical-balance verification, and the coastal-roastery worked example condensed to the default-breaking pass + final SVG code with coordinate commentary.

- [ ] **Step 2: Verify**

Run: `grep -n 'inversion test' references/icon-illustration.md` — Expected: ≥ 1 hit.
Run: `grep -n 'src/app/App.tsx' references/icon-illustration.md` — Expected: **no hits** (runtime-neutral).

- [ ] **Step 3: Commit**

```bash
git add references/icon-illustration.md
git commit -m "feat(skill): add single-mark (icon/illustration) reference"
```

---

### Task 13: `references/qa-protocol.md`

**Files:**
- Create: `references/qa-protocol.md`

- [ ] **Step 1: Author the file** from R3-P9 (R3 lines 2061–2124), R2-P9 (R2 lines 4849–5431), R2-P10 (R2 lines 5432–6497). Required sections:
  - `## Pre-delivery checks, in order` — the 10-step blind checklist (compile → completeness → computed composition → blind contrast via OKLCH lightness gap ≥ 0.4 → responsive collapse → state coverage → content pass → interactivity → token discipline → scope).
  - `## Top defects by frequency` — the ranked top-10 list.
  - `## Seeing your work` — when a browser tool (e.g. playwright-cli) is available, screenshot at ≥ 2 viewport widths and re-review composition/contrast with eyes before delivering; blind checks are the fallback, not the preference.
  - `## Unglamorous states` — from R2-P10: empty, loading/skeleton, error, zero-data chart, long-content overflow, permission-denied — one concrete recipe each.
  - `## Multi-turn coherence` — extend-don't-redesign default; refactor triggers; token-drift defense ("the established system is constraint, not suggestion"); what to re-read each turn (tokens file, DESIGN.md, the component being touched).
  - `## Translating vague feedback` — from R2-P9: the five translations ("make it pop", "feels bland", "more premium", "too corporate", "I don't like it") — diagnose-first protocol, levers in order, what to refuse to change to protect coherence.

- [ ] **Step 2: Verify**

Run: `grep -n 'make it pop' references/qa-protocol.md` — Expected: ≥ 1 hit.
Run: `grep -n '0.4' references/qa-protocol.md` — Expected: OKLCH-gap heuristic present.

- [ ] **Step 3: Commit**

```bash
git add references/qa-protocol.md
git commit -m "feat(skill): add QA and iteration protocol reference"
```

---

### Task 14: `references/taste-calibration.md`

**Files:**
- Create: `references/taste-calibration.md`

- [ ] **Step 1: Author the file** — the quarantined graft layer. Open with a framing note: *"This file is calibration, not workflow. It exists because entropy sampling alone does not prevent convergence: the looks below are legitimate when a brief asks for them and tells when they appear unprompted. Sources: Anthropic's frontend-design skill (see its LICENSE.txt) and impeccable v3.5 (Apache 2.0), adapted with attribution."* Required sections:
  - `## The three saturated default looks` — from frontend-design: (1) warm cream near `#F4F1EA` + high-contrast serif display + terracotta accent; (2) near-black + single acid-green/vermilion accent; (3) broadsheet hairline-rules zero-radius dense columns. Rule: brief's words always win, including when it asks for one of these; where the brief is silent, don't spend the freedom here.
  - `## The cream band, specified` — impeccable's OKLCH spec (L 0.84–0.97, C < 0.06, hue 40–100) + token-name tells (`--paper`, `--cream`, `--sand`, `--bone`, `--linen`, `--parchment`…) + the three escape routes (saturated brand body; chroma-0 off-white; darker brand-tinted mid-tone).
  - `## Absolute bans` — impeccable's match-and-refuse list: side-stripe borders; gradient text; glassmorphism-as-default; hero-metric template; identical card grids; eyebrow-on-every-section; numbered markers as reflex scaffold; heading overflow at breakpoints. One line each with the rewrite direction.
  - `## The category-reflex check` — both altitudes: first-order (theme guessable from category alone → rework) and second-order (aesthetic family guessable from category + anti-reference → rework again).
  - `## Commitment devices` — frontend-design's two-pass plan (compact token plan → self-review "would I arrive here for any similar brief?" → build to plan); the signature element (one memorable thing, everything else quiet); physical-scene sentence for dark-vs-light; color-strategy axis (restrained / committed / full palette / drenched).
  - `## Copy tells` — no em dashes; no aphoristic-cadence recurring voice; no buzzword family (streamline/empower/seamless/…).

- [ ] **Step 2: Verify**

Run: `grep -n 'F4F1EA' references/taste-calibration.md` — Expected: 1 hit.
Run: `grep -in 'Apache' references/taste-calibration.md` — Expected: attribution present.
Run: `grep -n '0.84' references/taste-calibration.md` — Expected: cream-band spec present.

- [ ] **Step 3: Commit**

```bash
git add references/taste-calibration.md
git commit -m "feat(skill): add quarantined taste-calibration reference (attributed grafts)"
```

---

### Task 15: Examples — FRAME and MERIDIAN guidelines pair

**Files:**
- Create: `examples/guidelines-frame.md`
- Create: `examples/guidelines-meridian.md`

- [ ] **Step 1: Create both files.** Each gets the same 6-line preface (adapted per file), then the corpus document verbatim:

Preface template:

```markdown
> **One brief, two systems.** This and its sibling were produced from the *same*
> film-studio brief with different sampled ingredients. FRAME committed to quiet
> editorial on warm paper; MERIDIAN committed to brutalist-cinematic on near-black.
> Both are internally coherent and mutually exclusive — that divergence is the
> point of the workflow: ingredients + full commitment produce distinct systems,
> not variations on one template. Use the structure, not the palette.
```

- `guidelines-frame.md`: preface + the FRAME Studio document from R4 lines 16–122 verbatim.
- `guidelines-meridian.md`: preface + the MERIDIAN PICTURES document from R4b (the fenced markdown block) verbatim.

- [ ] **Step 2: Verify**

Run: `grep -n 'MERIDIAN' examples/guidelines-meridian.md | head -2` && `grep -n 'FRAME' examples/guidelines-frame.md | head -2` — Expected: hits in each.
Run: `grep -n 'One brief, two systems' examples/guidelines-frame.md examples/guidelines-meridian.md` — Expected: 1 hit per file.

- [ ] **Step 3: Commit**

```bash
git add examples/guidelines-frame.md examples/guidelines-meridian.md
git commit -m "feat(skill): add FRAME/MERIDIAN one-brief-two-systems example pair"
```

---

### Task 16: Example — reference implementation

**Files:**
- Create: `examples/reference-implementation/DESIGN.md`
- Create: `examples/reference-implementation/index.html`

**Interfaces:**
- Produces: the law→code demonstration. `DESIGN.md` follows the Task 11 required structure; `index.html` is a single self-contained file (no external requests except Google Fonts) implementing the film-studio dashboard Overview page.

- [ ] **Step 1: Author `DESIGN.md`** — FRAME Studio system, restructured to the Task 11 skeleton (sections 0–8), tokens quoted from the R2-P5 §7 film-studio OKLCH ramp (R2 lines 2989–3337) and the R3-P6 theme decision summary (R3 lines 1404–1415). ≤ 120 lines.

- [ ] **Step 2: Author `index.html`** — adapt the R3-P6 OverviewRoute (R3 lines 1580–1702) to a single-file page: embedded `<style>` with the DESIGN.md tokens as CSS custom properties; Google Fonts import for Newsreader/Archivo/Manrope/DM Mono; the header, view tabs (Today/This week working via ~15 lines of vanilla JS), four Metric tiles, budget-pace panel (static SVG area chart hand-drawn with the chart tokens — no chart library), selected-project list with working selection state; realistic data from R3-P6 (Autumn House, Low Tide, North Terminal, project codes, budgets, dates); visible focus states; one responsive breakpoint at 1000px collapsing the two-column band.

- [ ] **Step 3: Verify visually**

Run: open `examples/reference-implementation/index.html` via the playwright-cli skill, screenshot at 1440px and 390px widths.
Expected: warm-paper canvas, bordered flat panels, Newsreader page title, working tab/selection interactions, no horizontal overflow at 390px. Fix anything that fails before committing.

- [ ] **Step 4: Verify tokens and content**

Run: `grep -c 'var(--' examples/reference-implementation/index.html` — Expected: ≥ 25 (token-driven styling).
Run: `grep -in 'lorem' examples/reference-implementation/index.html` — Expected: no hits.

- [ ] **Step 5: Commit**

```bash
git add examples/reference-implementation
git commit -m "feat(skill): add law-to-code reference implementation"
```

---

### Task 17: README and install

**Files:**
- Modify: `README.md` (replace bootstrap placeholder entirely)

- [ ] **Step 1: Rewrite README.md** with: what the skill is (2 ¶: Figma Make workflow replica; part of the SVGF-Design project whose second deliverable is an SVG-filter design skill built on this one + frontend-design + impeccable); install (`ln -s "$(pwd)" ~/.claude/skills/figma-design` from a clone, or marketplace when published); usage (triggers automatically on UI-design tasks; sampler can be run manually: `node scripts/sample-ingredients.mjs [--seed N]`); development (`node --test scripts/*.test.mjs`); repo map (skill files vs `Figma Design/` corpus vs `docs/` research+specs, noting corpus is never loaded at runtime); credits (Figma Make interviews; frontend-design; impeccable Apache 2.0).

- [ ] **Step 2: Verify**

Run: `node --test scripts/*.test.mjs` — Expected: `# pass 4` (still green).
Run: `grep -n 'ln -s' README.md` — Expected: install line present.

- [ ] **Step 3: Install and commit**

```bash
ln -sfn "$(pwd)" ~/.claude/skills/figma-design
git add README.md
git commit -m "docs: rewrite README for the figma-design skill"
```

---

### Task 18: Eval briefs — `evals/evals.json`

**Files:**
- Create: `evals/evals.json`

**Interfaces:**
- Produces: the skill-creator eval set consumed by Task 19. `expected_output` fields double as grader guidance.

- [ ] **Step 1: Write the file** (assertions stay empty per skill-creator; they're drafted during the runs):

```json
{
  "skill_name": "figma-design",
  "evals": [
    {
      "id": 1,
      "prompt": "Design a desktop dashboard for a regional freight rail operator's dispatch team: live train positions, crew hours, delay exceptions, and maintenance windows. High-trust, data-dense, used 8 hours a day. Build it as a single HTML file with realistic data.",
      "expected_output": "Committed non-generic operational system; exception-first or comparable arrangement; semantic tokens; realistic rail data; working interactions",
      "files": []
    },
    {
      "id": 2,
      "prompt": "Build a public status web page for a mid-size city's bus network: line health, current disruptions, next departures for saved stops. Municipal, accessible, needs to work for riders in a hurry. Single HTML file.",
      "expected_output": "Civic, accessible system distinct from eval 1; status legible without color alone; committed stance recorded in a DESIGN.md",
      "files": []
    },
    {
      "id": 3,
      "prompt": "Design a website for a children's public library summer reading program — kids 6 to 12 and their parents. Sign-up call-to-action, weekly book lists, event calendar. Fun without being garish. Single HTML file.",
      "expected_output": "Playful-but-disciplined system; no template card-grid; age-appropriate voice; realistic book/event data",
      "files": []
    },
    {
      "id": 4,
      "prompt": "Build an e-commerce landing page for a third-generation family hardware store going online for the first time: featured tools, seasonal project guides, in-store pickup. Practical and trustworthy, not startup-slick. Single HTML file.",
      "expected_output": "Commerce composition with product imagery treatment rules; trustworthy non-SaaS system; believable products and prices",
      "files": []
    },
    {
      "id": 5,
      "prompt": "Design a one-page electronic press kit for an experimental jazz trio: bio, listen links, upcoming dates, press photos, booking contact. Single HTML file.",
      "expected_output": "DELIBERATELY VAGUE BRIEF — the divergence testbed. A committed, unusual, coherent system; run twice with different sampler seeds must yield two different stances",
      "files": []
    },
    {
      "id": 6,
      "prompt": "Design a landing page for a meditation app in a warm editorial style with a cream background, serif display type, and terracotta accents. Single HTML file.",
      "expected_output": "BRIEF-AUTHORITY CHECK — explicitly requests a 'default' look; the skill must honor it literally (cream + serif + terracotta) with high craft, not swerve away",
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

Run: `node -e "JSON.parse(require('fs').readFileSync('evals/evals.json','utf8')); console.log('ok')"` — Expected: `ok`
```bash
git add evals/evals.json
git commit -m "test(skill): add eval brief set"
```

---

### Task 19: Eval iteration 1 (skill-creator loop)

**Files:**
- Create: `figma-design-workspace/iteration-1/` (sibling eval workspace per skill-creator; add `figma-design-workspace/` to `.gitignore`)

This task follows the skill-creator skill's run procedure. It is interactive (user review gate).

- [ ] **Step 1:** Add `figma-design-workspace/` to `.gitignore`; commit (`chore: ignore eval workspace`).
- [ ] **Step 2:** Spawn all runs in one turn per skill-creator: for each of the 6 evals, one with-skill subagent (skill path = repo root) and one without-skill baseline, each saving a complete HTML deliverable (and DESIGN.md when produced) to `figma-design-workspace/iteration-1/eval-<id>-<name>/{with_skill,without_skill}/outputs/`. For eval 5 add a third run: with-skill, prompt appended with "Use `--seed 11`" vs the first with-skill run's "Use `--seed 22`" (divergence pair). Write `eval_metadata.json` per eval dir.
- [ ] **Step 3:** While runs execute, draft assertions into each `eval_metadata.json`: process-compliance (output includes a DESIGN.md with a "Stance commitment" section; transcript shows `sample-ingredients.mjs` was run — evals 1–5 only); slop-escape (for evals 1–5: page background not in cream band unless stance-justified, no eyebrow-kicker repeated over ≥ 3 sections, no identical-card-grid hero — checkable by grep/screenshot); brief-authority (eval 6 only: cream + serif + terracotta present); divergence (eval 5: the two seeded runs committed different stances).
- [ ] **Step 4:** Capture each run's `timing.json` from task notifications as they arrive.
- [ ] **Step 5:** Screenshot every output HTML at 1440px via playwright-cli into each run's outputs dir.
- [ ] **Step 6:** Grade (grader subagent per skill-creator `agents/grader.md`), aggregate (`python -m scripts.aggregate_benchmark <workspace>/iteration-1 --skill-name figma-design` from the skill-creator directory), and launch the viewer (`eval-viewer/generate_review.py`).
- [ ] **Step 7:** **USER GATE** — tell the user the viewer is open (Outputs + Benchmark tabs), wait for their review, read `feedback.json`.
- [ ] **Step 8:** Apply revisions to SKILL.md/references per feedback; commit each revision (`fix(skill): …`). If feedback demands structural change, update the spec's `## Revision Notes` too.

---

### Task 20: Description-triggering optimization

Follows skill-creator's Description Optimization procedure. Requires the `claude` CLI.

- [ ] **Step 1:** Generate 20 trigger eval queries (8–10 should-trigger incl. indirect phrasings like "make my settings page less ugly"; 8–10 tricky should-not-trigger near-misses: backend API design, database schema design, designing a CLI's flag interface, "design a logging architecture", SVG *parsing* code, choosing a chart library without UI work). Save to `figma-design-workspace/trigger-eval.json`.
- [ ] **Step 2:** **USER GATE** — render skill-creator's `assets/eval_review.html` with the queries; user edits/approves; retrieve exported `eval_set.json`.
- [ ] **Step 3:** Run the loop in background: `python -m scripts.run_loop --eval-set <path> --skill-path <repo root> --model <current session model id> --max-iterations 5 --verbose`; report scores as iterations complete.
- [ ] **Step 4:** Apply `best_description` to SKILL.md frontmatter; show before/after; commit (`fix(skill): optimize trigger description`).

---

### Task 21: Final verification — spec acceptance walk

Execute the spec's acceptance section as written (`docs/doperpowers/specs/2026-07-23-figma-design-skill-design.md`, "What done looks like"). For each criterion, record pass/fail with evidence:

- [ ] **1. Triggering:** with the Task 17 symlink installed, in a fresh session: "build a landing page for a pottery studio" → skill loads; "write a cron job that rotates logs" → skill does not load; "make a logo for a kayak rental company" → skill loads AND routes to `references/icon-illustration.md`. (Evidence: session transcripts.)
- [ ] **2. Workflow execution:** from the Task 19 transcripts, verify a with-skill run shows all of (a) conventions read, (b) sampler run, (c) written stance commitment, (d) DESIGN.md authored before UI code, (e) realistic content, (f) QA checklist executed. Any miss → revise SKILL.md instructions and note it.
- [ ] **3. Divergence:** eval 5's seed-11 vs seed-22 outputs committed different stances and look visibly different in screenshots.
- [ ] **4. Slop-escape:** evals 1–5 outputs contain none of: cream-band body background (grep hex + OKLCH check), eyebrow-kicker over ≥ 3 sections, hero-metric template, identical card grids (screenshot review).
- [ ] **5. Brief authority:** eval 6 output IS cream + serif + terracotta, executed with craft.
- [ ] **6. Standalone:** confirm eval runs used only this skill (no impeccable/frontend-design in the subagent context).
- [ ] **7. Eval complete:** iteration-1 ran end-to-end with user review and applied revisions (Task 19 evidence).
- [ ] **Full test suite still green:** `node --test scripts/*.test.mjs` → `# pass 4`.
- [ ] **Close the spec:** write `## Outcomes & Retrospective` in the spec (replacing "Pending — written at finish."), noting acceptance results and anything deferred; final commit (`docs: close out figma-design spec v1`).

---

## Self-Review (performed at plan-writing time)

- **Spec coverage:** every spec architecture element maps to a task (SKILL.md→3, sampler→1–2, 11 references→4–14, examples→15–16, eval plan→18–20, acceptance→21; README/packaging→17). Corpus sections the spec left unmapped are now assigned (R2-P6→stances, R2-P9/P10→qa-protocol, R2-P11 + R3-P3 image module→composition, R2-P12→icon-illustration, R2-P8→SKILL.md) — recorded in the spec's Revision Notes.
- **Placeholder scan:** clean — extension stances, eval briefs, and all data are final in-plan; content tasks carry full outlines + verification.
- **Type consistency:** reference filenames locked in Global Constraints and identical across Tasks 3–14; sampler CLI identical in Tasks 2/3/17/19; workspace paths identical in Tasks 19–21.
- **Spec drift:** two fixes applied to the spec (source-map extensions; sampler test file added to layout) — see spec Revision Notes 2026-07-23.
