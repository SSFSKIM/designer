# figma-design

A Claude Agent Skill that replicates Figma Make's UI-design workflow — the aesthetic-sampling, stance-commitment, tokenization, and QA discipline Figma Make applies when it builds a page — as a runtime-neutral skill any Claude Code session can load, independent of Figma's own product. It is not a Figma integration or plugin; it is a from-scratch reconstruction of that workflow's method, assembled from a corpus of interviews with Figma Make (see `Figma Design/`) plus supporting design-engineering research, so the same discipline is available wherever Claude is designing UI.

This repository is itself the skill: `SKILL.md` at the repo root is the entry point, and everything a running Claude session reads lives alongside it (`scripts/`, `references/`, `examples/`).

## Install

From a local clone, symlink the repo into Claude's user-level skills directory:

```bash
ln -s "$(pwd)" ~/.claude/skills/figma-design
```

(Once this project is published to a marketplace, installing from there will be the preferred path instead of the manual symlink.)

## Usage

The skill triggers automatically — Claude reads its `description` in `SKILL.md` and loads it whenever a task looks like UI design: building, redesigning, restyling, or critiquing a page, dashboard, product surface, or standalone mark (logo, icon, badge, illustration). No explicit invocation is needed.

The one piece of it that's also useful stand-alone is the aesthetic-ingredient sampler, which replicates Figma Make's `create_make_theme` behavior. Run it directly when you want a draw without going through the full skill:

```bash
node scripts/sample-ingredients.mjs            # random draw
node scripts/sample-ingredients.mjs --seed 42   # deterministic draw, for reproducing a result
```

## Development

Run the test suite with Node's built-in test runner:

```bash
node --test scripts/*.test.mjs
```

This currently covers `scripts/sample-ingredients.mjs` via `scripts/sample-ingredients.test.mjs`, checking the sampler's draw shape, its no-duplicates guarantee, seeded reproducibility, and the integrity of the `scripts/ingredients.json` data library it draws from.

## Repo map

Three tiers, with different runtime treatment:

- **Skill files — loaded at runtime by Claude.** `SKILL.md` (entry point and routing logic), `scripts/` (the ingredient sampler and its data/tests), `references/` (the eleven files SKILL.md routes into: `stances.md`, `color-engineering.md`, `typography.md`, `motion.md`, `composition.md`, `effects-policy.md`, `voice-copy.md`, `guidelines-authoring.md`, `icon-illustration.md`, `qa-protocol.md`, `taste-calibration.md`), and `examples/` (a one-brief-two-systems pair, `guidelines-frame.md` and `guidelines-meridian.md`, plus `reference-implementation/` — a runnable `DESIGN.md` + `index.html` demonstrating the law-to-code path end to end).
- **`Figma Design/`** — the raw Figma Make interview corpus (four interview rounds plus supporting notes) that this skill's workflow was reverse-engineered from. Source material only: it is **never loaded at runtime**.
- **`docs/`** — project research notes (`docs/research/`) and this skill's own design spec and implementation plan (`docs/doperpowers/`). Also **never loaded at runtime**; useful for understanding how the skill was built, not for using it.

## Credits

- The **Figma Make interviews** (`Figma Design/`) are this workflow's primary source — the sampler, the stance taxonomy, and the QA protocol are all reconstructed from that corpus.
- **`frontend-design`**, Anthropic's official frontend-design plugin skill, informed parts of this workflow; its own terms are in its bundled `LICENSE.txt`.
- **`impeccable`** (Apache 2.0) likewise informed parts of this workflow.
