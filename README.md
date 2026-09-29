# designer

A Claude Code plugin that gives Claude a working design practice instead of a set of style preferences: read the project before touching it, derive one visual stance from the brief and commit to it in writing, build on semantic tokens, use real content, and check the result against an accessibility and taste floor before calling it done.

Most generated interfaces converge on the same few looks — warm-cream editorial, near-black with one hot accent, hairline broadsheet — not because a brief asked for them but because they are what models reach for absent a reason not to. This plugin is built to interrupt that: an ingredient sampler pushes each build off the trained default, the stance is derived from the product on nine axis lines — two the brief fixes (density, criticality) and seven the design chooses (energy, type, material model, color commitment, accent job, ground lightness, ground temperature) — rather than picked from a catalogue, that derivation is recorded as project law before any UI code is written, and a QA pass checks the finished page against the law it declared for itself — including whether its values would have come out the same for a different product in the same category. The layout is derived the same way: six lines read off the brief — posture, dominant activity, unit and relation, co-visibility, temporal structure, volume and homogeneity — compile into two or three candidate compositions, one is chosen and the rejected ones are recorded, and the named arrangements the reference teaches are kept as priors to start from rather than grids to copy.

The workflow is a from-scratch reconstruction of the method observed in Figma Make — its aesthetic sampling, stance commitment, tokenization, and QA discipline — rebuilt as a runtime-neutral skill from a corpus of interviews with that product (see `Figma Design/`), plus supporting design-engineering research.

> **Not affiliated with Figma.** This is not a Figma integration, a Figma plugin, or a way to talk to Figma files. "Figma" and "Figma Make" are trademarks of Figma, Inc., named here only to credit the source of the method. See `NOTICE`.

## Install

From the command line:

```bash
claude plugin marketplace add SSFSKIM/designer --sparse .claude-plugin skills
claude plugin install designer@designer
```

The repository also holds vitrea and its calibration evidence, about 600 MB packed, and the plugin needs only its manifest and `skills/`. `--sparse` checks out just those two directories, about 10 MB, where a full clone can run past the 120 seconds Claude Code allows a marketplace clone and fail; an update re-clones whenever there are new commits, so the limit applies every time. The in-session `/plugin marketplace add` has no `--sparse`, so add the marketplace from the shell.

If you added it earlier without `--sparse`, run `claude plugin marketplace remove designer` first: `add` refuses a source that differs from the one already declared, and the removal uninstalls the plugin, which the `install` line puts back. Where an SSH key for GitHub is configured but GitHub does not accept it, prefix the `add` with `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

## Usage

The skill triggers automatically — Claude reads its description and loads it whenever a task looks like UI design: building, redesigning, restyling, or critiquing a page, dashboard, product surface, or standalone mark (logo, icon, badge, illustration). No explicit invocation is needed.

What it does on a full-page brief: classifies the deliverable, reads existing project conventions, samples aesthetic ingredients, places the brief on the stance axes and derives one stance from the product's own world (with the road not taken recorded), writes that derivation into a `DESIGN.md` as project law, builds semantic tokens from it, derives the composition from six brief-read lines into two or three candidates and builds the one it chose (the rejected candidates recorded, the named layouts kept as priors), fills in realistic content, and runs a craft-and-QA pass that includes checking the build against its own declared rules and against the clone tell.

### The Essentialist persona

An optional persona layer replaces the sampler run and the stance choice with a committed decision function distilled from the Bauhaus → Dieter Rams → Jonathan Ive functionalist lineage, grounded in a primary-source corpus with law-by-law traceability. Invoke it by naming it in the brief:

```
Design a settings page for a home thermostat. persona: essentialist
```

It also activates when a brief names the lineage itself (Dieter Rams, Braun, Ive-era Apple, "less but better"), and it persists across turns once recorded in a project's `DESIGN.md`. Generic adjectives — "clean", "minimal", "simple" — deliberately do **not** activate it; those run the normal sampler flow.

`skills/designer/personas/TEMPLATE.md` is the authoring contract for writing additional personas.

### The Materialist skill

Since 2.4.0 the plugin ships a second, independent skill, `skills/materialist/`, for designing with
Liquid Glass and with vitrea, its web implementation (below). It loads whenever a brief names Liquid
Glass, glassmorphism, glass or translucent floating controls, an Apple- or visionOS-like material, or
the `@vitreajs/*` packages, with or without the designer skill. It is an aesthetic guideline written
as a decision function and its laws rather than a style sheet: what the material physically is
(a lens with thickness, a size law, a body that takes the backdrop's tone and hue, an exterior shadow
graded by the caster, two poses, two schemes), the register it belongs to (refined futurism with
optical rather than ornamental skeuomorphism; two registers, an instrument over a world and glass as
the surface set into an environment; active curvature; physical motion; daylight as the distinctive
case), the two-layer discipline and the spatial register's conditions, a ban list and 28 checks.
Its references carry the measured optics with their ledger sections, a cookbook mapping each
decision onto the current vitrea API, and eight worked derivations. When both skills are loaded, the
designer skill routes to it the moment a page's material model resolves to glass over planes.

The skill has been judged on pages, not only on its prose: eight demos built under it alone by fresh
agents, on the workspace source at 0.24.0, live on the demo site's gallery
(`https://ssfskim.github.io/designer/gallery/`, source under `apps/demo/src/gallery/<slug>/` with
each page's design record beside it), in two registers. Six are the instrument register, glass
controls over live content; two are the spatial register, where glass windows are the interface and
the world is their environment: a museum's viewing room with its label set into the painting, and a
browser start page around the day's photograph. Each was audited mechanically and read against the
skill's own checks, and each register was evaluated against an unaided agent: the first on six
briefs, the second on a held-out brief that does not name the register, beside a matched control
the skill must keep in the instrument register. The specs are
`docs/doperpowers/specs/2026-09-27-materialist-proof.md` and, for the second register,
`docs/doperpowers/specs/2026-09-27-materialist-spatial-register.md`; the evidence is under
`docs/research/data/2026-09-27-materialist-proof/` and
`docs/research/data/2026-09-27-materialist-spatial-register/`. Version 1.0.1 of the skill is what
the proof corrected; 1.1.0 added the spatial register.

A ninth page, the gallery's flagship, was built in the main session rather than by a fresh maker: a planetarium display, Tonight (`/gallery/planetarium/`), whose environment is the real sky over a place drawn live in WebGL, and whose window, module and two morphing ornaments are the clear variant tuned, leaf by named leaf, from the frost the shipped material draws at window span toward a lens — the runtime reporting it as tuned, the charter (`docs/doperpowers/specs/2026-09-28-planetarium-flagship.md`) saying why each leaf moved, and the same audit reading every text line on its glass in every state.

A tenth page, a second flagship, was also built in the main session: Chronograph (`/gallery/chronograph/`), a rattrapante on a watchmaker's bench whose dial, hands and loupe image are painted live into one canvas. Its crystal and a movable loupe are optical glass with nothing on them. The chronograph's controls are ordinary Liquid Glass beside the watch, and all of it is the regular material tuned from frost toward clear optics. The body's plate and haze are removed, the lens's height law is extended past its 20 px cap, and the lens itself stays calibrated. The Crystal menu offers the calibrated material as a comparison, and its record (`docs/doperpowers/specs/2026-09-29-chronograph-flagship.md`) says what each choice changed and what the runtime could not do.

An eleventh page, Terminal (`/gallery/terminal/`), asks whether a terminal can run on the glass itself, further than macOS's own Terminal goes: its Clear profiles, new in macOS 26, lay a ground 93 to 95 per cent opaque behind the text. Its window is the clear variant tuned toward a lens, with the terminal's text (xterm.js on its DOM renderer) written straight onto it and its sixteen colours designed against the body the runtime draws. It sits over a relief map of the Lake Tahoe basin built from USGS elevation data: the lake's flat water is the calm area behind the text, and the shores' contours bend at the window's rims. The window moves and resizes, sessions open as tabs, and one choice swaps in vitrea's calibrated material for comparison. The shell is simulated over a snapshot of this repository, because the page is static; it says so, and refuses anything that would need a real machine. Its record is `apps/demo/src/gallery/terminal/DESIGN.md`.

### The sampler, stand-alone

The one piece that is also useful on its own is the aesthetic-ingredient sampler. Run it directly when you want a draw without going through the full skill:

```bash
node skills/designer/scripts/sample-ingredients.mjs            # random draw
node skills/designer/scripts/sample-ingredients.mjs --seed 42  # deterministic draw
```

## Repo map

The plugin ships two skills. Everything Claude loads at runtime lives under `skills/designer/` and `skills/materialist/`; everything else in the repo is source material and project history that is **never loaded at runtime**.

**Runtime — `skills/designer/`**

- `SKILL.md` — entry point, deliverable classification, persona routing, workflow spine, taste floor
- `references/` — the thirteen files SKILL.md routes into: `stances.md` (the seven axes, the derivation procedure, five worked derivations, the named-stance library), `material.md` (the material-model axis and the vitrea path for glass), `component-character.md`, `color-engineering.md`, `typography.md`, `motion.md`, `composition.md`, `effects-policy.md`, `voice-copy.md`, `guidelines-authoring.md`, `icon-illustration.md`, `qa-protocol.md`, `taste-calibration.md`
- `personas/` — optional distilled designer personas, currently `essentialist.md`, loaded only when a brief invokes one. `TEMPLATE.md` is the authoring contract and is never loaded at runtime
- `scripts/` — the ingredient sampler, its data library, and its tests
- `examples/` — a one-brief-two-systems pair (`guidelines-frame.md`, `guidelines-meridian.md`) plus `reference-implementation/`, a runnable `DESIGN.md` + `index.html` demonstrating the law-to-code path end to end

**Runtime — `skills/materialist/`**

- `SKILL.md` — the Liquid Glass aesthetic as one voice: what the material is, the register, the decision function, the laws by area, the home system, derivation, the ban list, the 28 checks
- `references/` — `optics.md` (the measured physical model, law by law with its ledger section), `vitrea.md` (the cookbook at the current API, React and vanilla, what the runtime does not catch, the CSS-only path), `examples.md` (six worked derivations and the record template)

**Not runtime**

- `Figma Design/` — the raw Figma Make interview corpus (four interview rounds plus supporting notes) this workflow was reconstructed from
- `docs/research/` — design-engineering research, including the primary-source persona corpus and its law-by-law distillation record, the Liquid Glass design-language memo (34 sources), the prior-art report on the material's aesthetic and reception, and the materialist's own distillation record
- `docs/doperpowers/` — this project's own specs and implementation plans
- `evals/` — the eval suite used to measure the skill against unaided baselines
- `packages/`, `apps/` — **vitrea**, the second artifact this repo ships (see below). Nothing here is loaded by the plugin

Project history under `docs/` refers to this skill by its original working name, `figma-design`. It was renamed to `designer` at first release; the documents are left as written rather than retitled after the fact.

`docs/` also holds a second, discarded direction: a material-specialist skill built on SVG filters, planned in mid-2026 and cut. Those documents carry a banner marking them archived. The repository no longer builds anything on SVG filters — `effects-policy.md` treats material simulation as a rendering job with a CSS surface as its fallback, and `references/material.md` routes a glass-over-planes stance to vitrea (below) when the stack can host an ES module.

## vitrea — the material runtime

This repository is dual-artifact. Alongside the plugin it hosts **vitrea**, a
TypeScript library replicating Apple's Liquid Glass material on the web:
real-time size-parameterized lensing, per-element backdrop adaptation,
container-scoped sampling, and shape-to-shape morphing, on WebGPU with an honest
CSS fallback tier. It is the WebGL/GPU direction the archived SVG-filter plan
pointed at, built as its own open-source product.

Positioning, deliberately: not "the first WebGPU glass demo" — prior art exists.
vitrea is **a production-oriented, reference-calibrated material compositor for
semantic web controls**. Explicit backdrop contracts, shared sampling groups,
coherent cross-element morphing, adaptive accessibility, progressive fidelity
tiers that report what they actually resolved to, and fidelity numbers backed by
a versioned harness that diffs against native captures. Glass labels stay real
DOM: a `GlassButton` is a `<button>`, focusable and announced as one.

```bash
npm install @vitreajs/vitrea-react          # React
npm install @vitreajs/vitrea-web            # plain JS, or your own adapter
```

- **[`@vitreajs/vitrea`](./packages/core/README.md)** — the framework-agnostic runtime:
  scene model, capability and tier resolution, material and accessibility policy.
  No DOM code at all.
- **[`@vitreajs/vitrea-web`](./packages/platform-web/README.md)** — the browser host:
  `createGlassRoot`, element registration, planes, backdrop proxies, the CSS tier
  and the WebGPU lifecycle. Mounts a root from any framework, or none.
- **[`@vitreajs/vitrea-react`](./packages/react/README.md)** — the declarative surface:
  `GlassRoot`, `GlassGroup`, `GlassSurface`, and the v1 controls.
- **The public demo** — `apps/demo`, with side-by-side native reference pairs.
  Run it locally with `pnpm --filter demo dev`.
- **Design and roadmap** —
  [`docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`](./docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md).
- **Fidelity claims, in full** —
  [`docs/doperpowers/specs/c9a-fidelity-claims.md`](./docs/doperpowers/specs/c9a-fidelity-claims.md),
  including everything that could not be measured and why. Nothing anywhere in
  this project claims to be pixel-identical to Apple's material.
- **Designing with the material** —
  [`skills/materialist/SKILL.md`](./skills/materialist/SKILL.md), the aesthetic
  guideline: what the glass physically does, the two-layer discipline, geometry,
  colour, motion, and a cookbook mapping each decision onto this API.

The workspace is a pnpm monorepo. Seven packages under `packages/` — `core`,
`geometry`, `motion`, `platform-web`, `renderer-webgpu`, `react`, `calibration` —
of which exactly three are ever published, under the `@vitreajs` names above.
They layer the way React's own packages do: a pure runtime, a DOM host over it,
framework bindings over that, each externalising the one below so a page that
mounts roots through two of them still holds one copy of each. The remaining four
keep their `@vitrea/*` workspace names, never publish, and are bundled in at
publish time, so an app gets no transitive runtime dependency outside this
project beyond React. `apps/reference-apple` is the native SwiftUI capture
harness the fidelity claims are measured against.

```bash
pnpm install
pnpm -r build && pnpm -r lint && pnpm -r test
pnpm --filter demo dev            # the demo site and the acceptance playground
```

`core`, `geometry` and `motion` are pure: they never reference `window`,
`document`, `HTMLElement` or `navigator`. That is enforced twice — those packages
compile without the DOM type library, and ESLint fails on the globals by name —
and `packages/core/test/purity-law.test.ts` seeds a real violation on every run to
prove both layers still fire.

The plugin and the library share only this repository. The marketplace still
installs from `./` and reads `skills/`; no JavaScript build output is loaded at
plugin runtime.

> **Not affiliated with Apple.** "Liquid Glass" is the name of Apple Inc.'s
> design language, referenced descriptively to say what vitrea replicates and
> what its fidelity is measured against. See `NOTICE`.

## Development

Run the test suite with Node's built-in test runner:

```bash
node --test skills/designer/scripts/*.test.mjs
```

This covers the sampler's draw shape, its no-duplicates guarantee, seeded reproducibility, argument handling, and the integrity of the `ingredients.json` data library it draws from. The materialist skill ships no scripts; `evals/materialist.json` holds its eval briefs.

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
