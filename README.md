# figma-design

A Claude Code plugin that replicates Figma Make's UI-design workflow — the aesthetic-sampling, stance-commitment, tokenization, and QA discipline Figma Make applies when it builds a page — as a runtime-neutral skill any Claude session can load, independent of Figma's own product. It is a from-scratch reconstruction of that workflow's method, assembled from a corpus of interviews with Figma Make (see `Figma Design/`) plus supporting design-engineering research, so the same discipline is available wherever Claude is designing UI.

> **Not affiliated with Figma.** This is not a Figma integration, a Figma plugin, or a way to talk to Figma files. "Figma" and "Figma Make" are trademarks of Figma, Inc.; the name describes the workflow this skill reconstructs. See `NOTICE`.

## Install

Add the marketplace, then install the plugin:

```
/plugin marketplace add SSFSKIM/SVGF-Design
/plugin install figma-design@figma-design
```

Or from the command line:

```bash
claude plugin marketplace add SSFSKIM/SVGF-Design
claude plugin install figma-design@figma-design
```

## Usage

The skill triggers automatically — Claude reads its `description` and loads it whenever a task looks like UI design: building, redesigning, restyling, or critiquing a page, dashboard, product surface, or standalone mark (logo, icon, badge, illustration). No explicit invocation is needed.

### The Essentialist persona

An optional persona layer replaces the sampler run and the stance choice with a committed decision function distilled from the Bauhaus → Dieter Rams → Jonathan Ive functionalist lineage. Invoke it by naming it in the brief:

```
Design a settings page for a home thermostat. persona: essentialist
```

It also activates when a brief names the lineage itself (Dieter Rams, Braun, Ive-era Apple, "less but better"), and it persists across turns once recorded in a project's `DESIGN.md`. Generic adjectives — "clean", "minimal", "simple" — deliberately do **not** activate it; those run the normal sampler flow.

### The sampler, stand-alone

The one piece that's also useful on its own is the aesthetic-ingredient sampler, which replicates Figma Make's `create_make_theme` behavior. Run it directly when you want a draw without going through the full skill:

```bash
node skills/figma-design/scripts/sample-ingredients.mjs            # random draw
node skills/figma-design/scripts/sample-ingredients.mjs --seed 42  # deterministic draw
```

## Repo map

The plugin ships one skill. Everything Claude loads at runtime lives under `skills/figma-design/`; everything else in the repo is source material and project history that is **never loaded at runtime**.

**Runtime — `skills/figma-design/`**

- `SKILL.md` — entry point, deliverable classification, persona routing, workflow spine, taste floor
- `references/` — the eleven files SKILL.md routes into: `stances.md`, `color-engineering.md`, `typography.md`, `motion.md`, `composition.md`, `effects-policy.md`, `voice-copy.md`, `guidelines-authoring.md`, `icon-illustration.md`, `qa-protocol.md`, `taste-calibration.md`
- `personas/` — optional distilled designer personas, currently `essentialist.md`, loaded only when a brief invokes one. `personas/TEMPLATE.md` is the authoring contract and is never loaded at runtime
- `scripts/` — the ingredient sampler, its data library, and its tests
- `examples/` — a one-brief-two-systems pair (`guidelines-frame.md`, `guidelines-meridian.md`) plus `reference-implementation/`, a runnable `DESIGN.md` + `index.html` demonstrating the law-to-code path end to end

**Not runtime**

- `Figma Design/` — the raw Figma Make interview corpus (four interview rounds plus supporting notes) that this workflow was reverse-engineered from
- `docs/research/` — design-engineering research, including the primary-source persona corpus and its law-by-law distillation record
- `docs/doperpowers/` — this project's own specs and implementation plans
- `evals/` — the eval suite used to measure the skill against unaided baselines
- `svgf-design/` — a discarded second skill (SVG filter craft). Kept for the record; it is outside `skills/` and does not ship

## Development

Run the test suite with Node's built-in test runner:

```bash
node --test skills/figma-design/scripts/*.test.mjs
```

This covers the sampler's draw shape, its no-duplicates guarantee, seeded reproducibility, argument handling, and the integrity of the `ingredients.json` data library it draws from.

Validate the plugin and marketplace manifests:

```bash
claude plugin validate . --strict
```

## Credits

- The **Figma Make interviews** (`Figma Design/`) are this workflow's primary source — the sampler, the stance taxonomy, and the QA protocol are all reconstructed from that corpus.
- **`frontend-design`**, Anthropic's official plugin skill (Apache-2.0), informed the calibration and copy guidance.
- **`impeccable`** v3.5 (Apache-2.0) informed the cream-band specification, the absolute-bans list, the category-reflex check, and the color-strategy axis.

Per-section attribution is inline at each point of use; see `NOTICE` for the full provenance record.

## License

Apache License 2.0 — see `LICENSE`. Third-party quotations in the research corpus remain the property of their copyright holders and are quoted, not relicensed; see `NOTICE`.
