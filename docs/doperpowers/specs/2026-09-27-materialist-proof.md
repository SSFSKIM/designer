# The materialist, proven on pages: six demos on 0.24.0, the eval, and the 2.3 panel's close

Status: chartered 2026-09-27; G0 scaffold landing, G1 makers dispatched. Parents:
`2026-09-26-materialist-skill.md` (the skill; its Deferred list is this initiative's three items)
and `2026-09-10-liquid-glass-into-the-skill.md` (the 2.3 demos, their six briefs, the audit and the
pre-registered four-rater panel, all of which live only on the unmerged `capsule-refinement`
branch at `f13ab38c`).

## Purpose

The materialist skill has been judged on its prose: an independent review of what it says and a
verification of every measured claim against the source. Nothing yet says whether an agent that
reads it produces the pages it describes. This initiative judges the skill on pages.

After it: six glass demos exist on the vitrea demo site under `/gallery/<slug>/`, each built by a
fresh opus maker who read the materialist skill and nothing else about design, on the workspace
source at 0.24.0 through `@vitreajs/vitrea-react`, each carrying the skill's own record and each
audited mechanically, read by an independent panel against the twenty-five rules the 2.3 demos were
read against, and reviewed against the skill's own twenty checks. Beside them, an eval of the skill
against an unaided opus on the four registered briefs and two held-out ones says what the skill
adds over the model's own defaults. And the 2.3 spec's interrupted panel is either completed on its
frozen inputs or closed as unmeasurable, with the reason written down.

The user's ruling that opens this initiative (2026-09-27): all three deferred items, in the order
recommended, with opus as the maker.

## Design

### A. The six demos (G1)

The six briefs are the 2.3 spec's, verbatim, with one change to the shared tail: the deliverable is
a page of the vitrea demo site rather than one served HTML file. The tail now reads: "Desktop at 1440
wide. A page of the vitrea demo site at `apps/demo/gallery/<slug>/`, written in React through
`@vitreajs/vitrea-react` on the workspace source (0.24.0)."

1. `music-player`, 2. `transit-ops`, 3. `photo-review` (product surfaces); 4. `film-festival`,
5. `park-trails`, 6. `product-launch` (narrative pages). The briefs are in the 2.3 spec's "The six
briefs" and are copied into the makers' prompts from there.

**The maker.** One fresh opus agent per demo. It is told to follow `skills/materialist/SKILL.md`,
reading the references it routes to (`references/vitrea.md`, `optics.md`, `examples.md`), and it is
told nothing about the designer skill. That is the independence claim the materialist was written
under (the 2.4.0 spec, Decision Log: a second skill, standalone), and it is what is under test: the
materialist says it can carry a glass page from brief to record without the designer's spine.
`examples.md` derives these same six briefs, so a maker who reads it is realising a derivation the
skill already wrote; that is the intended use of a worked example and is recorded here, not hidden.
The eval (C) is where generalisation beyond the examples is measured.

**Where a demo lives, and how it is wired** (scaffolded before dispatch so six makers never touch
one file): `apps/demo/gallery/<slug>/index.html` is the page shell, `apps/demo/src/gallery/<slug>/`
holds everything the maker writes (`main.tsx`, components, styles, `images/` with a `CREDITS.md`,
`DESIGN.md`), and `apps/demo/vite.config.ts` names each page as a Rollup input. The demo app aliases
every `@vitreajs/*` import to the workspace source, so the demos run on 0.24.0 with no publish step,
and the Pages workflow deploys them with the site on the next push to `main`. A gallery index at
`/gallery/` lists the six.

**Imagery.** No Unsplash key is present on this machine, so the imagery ladder's second rung is
closed and `find-image.mjs search` falls to Openverse. The 2.3 demos' photographs, all Unsplash,
downloaded and registered at placement in 2.3 and credited by photographer, are exported from
`f13ab38c` into each demo's `images/` with their credits in `CREDITS.md`, as rung one: assets already
in the project. A maker may use them, credit carried, or source others; it never reads the 2.3 pages
or records, which would hand it a finished derivation of its own brief.

**The audit contract**, two window handles, as in 2.3: `window.__vitrea` is the runtime root
(`useGlassRootHandle().root` once mounted) and `window.__glassDemo` carries
`openMenu?()` for a page with a menu or platter and `setReducedTransparency(boolean)`, which is the
app-level switch the materialist asks a page to offer where the preference cannot be queried. The
page's own tokens follow `prefers-color-scheme` and the root is `colorScheme="auto"`, so one
Playwright emulation flips both halves.

**Concurrency.** Six makers in one working tree with disjoint ownership; each runs its own dev
server on an assigned port (5181 to 5186); none runs git; the session commits each demo after its
gate. `pnpm --filter demo lint` runs eslint and `tsc` over the whole app, so a maker reads the errors
under its own directory and ignores another maker's half-written file.

### B. The instrument (G2)

`docs/research/scripts/glass-audit.mjs`, `glass-rules.py` and `glass-rules-analyze.py` are ported
from `f13ab38c` and adapted: the audit takes page URLs rather than demo directories and reads the
0.24.0 root API (`capabilities`, `diagnostics.reported`, `scene.diagnostics.reported`,
`accessibility`, `renderInput`, `setAccessibilityOverrides`, each verified against
`packages/platform-web/src/root.ts` at port time); the rules script reads its twenty-five items from
`docs/research/2026-09-10-liquid-glass-design-language.md` ("Rules a page can be checked against"),
SHA-pinned, since the 2.3 reference it read them from was never merged; the quality items
(a1 to a4, d1, e1) are dropped (Decision Log 4). Data lands under
`docs/research/data/2026-09-27-materialist-proof/`.

The audit captures, per demo and per colour scheme: the first viewport at 1440 × 900, the full
page, the second and third screens, the menu or platter open, and reduced transparency through the
page's switch. It reads: page errors and failed requests; overflow from the capture's width; the
contrast sample on rendered pixels in both schemes; the root's resolved state (renderer, sampling
backend, analysis, health, demotion reason, `materialDocument`) per group; every diagnostic on both
channels; the surface inventory with each surface's shorter span; and the materialist's mechanical
ban subset (§7): authored `backdrop-filter`, `box-shadow`, `border` or `background` on a registered
host; list, row, table or article roles on glass; two tint hues in one group; an opacity transition
or animation on a host or any ancestor of the root; `filter`, `backdrop-filter`, `opacity < 1`,
`mask-image`, `clip-path` or `mix-blend-mode` on an ancestor of the root; a span under 32 outside
the family's deliberate exceptions. Then three further passes: increased contrast, reduced motion
and forced colours through Playwright's emulation, each reporting errors, the accessibility policy
the runtime resolved, and under forced colours the count of glass drawn (which must be zero).

**Four readings, declared before any capture exists.**

1. **The mechanical read**, above, per demo.
2. **The panel.** The twenty-five rules as a blind yes/no rubric on the captures, four raters as in
   2.3 (`astra-high`, `astra-medium`, `claude-opus`, `claude-sonnet`), each reading all six demos in
   a seeded, recorded order before rating any, one file per rater per demo. Three rules cannot be
   seen on a static capture and the 2.3 panel scored them zero everywhere for that reason; they are
   assigned now, before a capture exists, rather than amended after: **r18** (contrast in both
   schemes) is read from the audit's contrast sample in both schemes; **r19** (works with reduced
   transparency, increased contrast and reduced motion) is read from the audit's three passes and its
   reduced-transparency capture; **r23** (materialise and morph, press as glow and flex) is read
   from the source by the reviewer in reading 3 against three named criteria: menus and platters
   arrive through `GlassMorph` or `present`, never an opacity transition; press is written through
   the channel properties, never a colour swap; nothing on a glass host transitions `opacity`,
   `background` or `filter`. The panel still answers r18, r19 and r23 and its answers are printed
   beside the assigned readings, so the substitution's effect is visible on every row.
3. **The source reading.** One independent `astra-high` reviewer per demo, read-only, reads the page
   against the materialist's §8 checks 1 to 19 and the three r23 criteria, on the source and the
   audit's captures, and returns findings with file and line. Findings are verified, then fixed by
   one opus fix wave per demo, then the demo is re-audited. The panel reads the post-fix state; there
   is one fix wave, and a demo still failing a `[layer]` or `[material]` check after it is recorded
   as such.
4. **The user's eye.** §8 check 20 and the 2.3 spec's question, "is this the same system?", per demo
   in both schemes and once with transparency reduced, beside a native capture of the nearest Apple
   surface; then a ranking of the six. Theirs to give, never inferred.

**Pass line, per demo, the 2.3 line.** At least 22 of the 25 rules hold (panel majority on the 22
capture-visible rules, the assigned readings on r18, r19 and r23), no rule tagged `[layer]` or
`[material]` fails, the mechanical read shows zero diagnostics on either channel and zero ban-subset
findings, and the page works with transparency reduced. The initiative **meets its purpose** when
all six pass. **Stop:** if three or more demos fail a `[layer]` or `[material]` rule after the one
fix wave, the skill is not teaching the language on the briefs its own examples derive; the result
is recorded here and in the skill's spec, and the next step is a rewrite of the skill's §4 from the
failures, not a seventh demo.

**Comparability.** The rules, the rater identities, the capture set and the pass line are the 2.3
panel's, so the 2.3 available-panel figures (three raters, 16 to 21 rules held, r18, r19 and r23 at
zero) stand beside the new ones. The differences are named: 0.24.0 against 0.14.0, React against
vanilla, the materialist against the designer's 2.3 reference, and three rules read mechanically
against read from captures. No difference is attributed to one cause.

### C. The eval (G4)

`evals/materialist.json` carries the four registered briefs (a music player in React, a camera
launch page over a CDN import, a pharmacy console as the negative control, and a component-tree
review). Two are near-copies of demo briefs and all four are within reach of `examples.md`, so two
held-out briefs are added as ids 5 and 6, written after the skill and absent from every reference:
a desktop weather app whose animated radar composite is the plane, and an architecture studio's
portfolio over its own photography on the vanilla path. The eval measures what an agent gets from the
skill in practice; ids 5 and 6 measure it beyond the worked examples.

**Arms.** `none`: the brief alone, the builder forbidden to read `skills/`, `docs/` or `evals/`
(the package READMEs and source are the library and stay readable, pointers to the skill included:
that is the unaided condition an agent without the plugin is actually in). `materialist`: the brief
and an instruction to follow `skills/materialist/SKILL.md`. Opus is the maker in both arms, one
seed each, twelve builds. Outputs go to `figma-design-workspace/materialist-proof/eval/<id>/<arm>/`
(gitignored); the committed evidence is the audit JSON and the grader's JSON per cell and a
`results.md`.

**Criteria, written before any build.** Each brief's `expected_output` is split into numbered
criteria in `docs/research/data/2026-09-27-materialist-proof/eval/criteria.json`, so a grader
answers a fixed list rather than a paragraph. The mechanical audit runs on every built page in
both arms (ids 1, 2, 3, 5, 6); id 4 is a text review and is graded only.

**The grader.** One `astra-high` per brief, receiving both arms labelled A and B in a recorded random
order, the criteria list, the pages, records and audit JSON, and answering holds or fails per
criterion per arm with one line of evidence. It is blind to the arm label and not to the content: a
page carrying the materialist's record is recognisable as the skill's, and the limitation is
recorded rather than papered over with screenshots-only judging, because most of the criteria are
structural and need the source.

**Expectation and what would stop it.** The `materialist` arm holds at least 80% of the criteria on
every brief and strictly more than `none` on each of ids 1, 2, 3, 5 and 6; on id 4 it names at least
four of the five faults. A brief where `none` holds as many criteria as `materialist` is recorded
with the skill section that should have carried the difference named, and that section is the next
edit to the skill.

### D. The 2.3 panel (G3)

The pre-registered panel rated frozen captures of the 0.14.0 demos at source revision `23ea4415`,
whose SHA-256s are in `baseline-captures.json`; three raters completed, the `claude-opus` rater never
ran, and the `claude-sonnet` thread ended on a rate-limit error after writing six files. The
captures themselves were preserved only under `figma-design-workspace/glass-panel-baseline/`, which
no longer exists on this machine (checked 2026-09-27).

Recovery, bounded: a worktree at `23ea4415`, the workspace built there, the six demos served and
audited with that revision's own `glass-audit.mjs`, and every regenerated capture hashed against
`baseline-captures.json`. If all thirty-six match, the frozen inputs are recovered: the `claude-opus`
rater runs with its preserved prompt over those captures, the `claude-sonnet` files are validated
for completeness, `glass-rules-analyze.py` writes `results.md`, and the 2.3 spec's Outcomes record
the complete panel. If any capture differs, the frozen inputs are unrecoverable (the spec itself
warned that fresh captures of animated pages are not byte-identical) and the panel closes as
**unmeasurable**, with the available-panel figures standing as provisional and the reason recorded
in the 2.3 spec. Either way the panel's data directory is ported to `main` beside the spec that
governs it, since the spec is on `main` and its evidence is not.

## Cost, declared

Six demo builds at about 0.5 M tokens each; twelve eval builds at about 0.3 M; twenty-four rater
runs at about 0.1 M; six source reviews and six fix workers at about 0.2 M each; six graders at
about 0.15 M; the port and the panel recovery at about 0.5 M each. About 12 M tokens, most of it in
parallel; the user's time is the eye reading, about thirty minutes.

## Files

- This spec.
- `apps/demo/gallery/index.html`, `apps/demo/gallery/<slug>/index.html` × 6,
  `apps/demo/src/gallery/index/`, `apps/demo/src/gallery/<slug>/` × 6 (each with `main.tsx`,
  `DESIGN.md`, `images/CREDITS.md`), `apps/demo/vite.config.ts` (seven inputs), `apps/demo/README.md`
  (the route table), `apps/demo/e2e/gallery.spec.ts` (zero authoring diagnostics on every gallery
  page, the site's own assertion extended).
- `docs/research/scripts/glass-audit.mjs`, `glass-rules.py`, `glass-rules-analyze.py`,
  `settling/reliability.py` (ported).
- `docs/research/data/2026-09-27-materialist-proof/`: `audit/<slug>.json` and the capture hashes,
  `rules/<rater>/<slug>.json`, `review/<slug>.{md,json}`, `results.md`; `eval/criteria.json`,
  `eval/<id>/<arm>/audit.json`, `eval/<id>/grade.json`, `eval/results.md`.
- `docs/research/data/2026-09-10-liquid-glass-demos/` (ported from `f13ab38c`, completed or closed).
- `evals/materialist.json` (ids 5 and 6).
- `skills/materialist/SKILL.md` and its spec, only where a finding here moves a law.

## Decision Log

- Decision: The makers read the materialist alone, not the designer skill.
  Rationale: the materialist was packaged as a standalone skill on the user's ruling (2.4.0 spec,
  2026-09-27), and standalone is the claim a demo can test. A build under both skills would say
  nothing about which one carried it.
  Date/Author: 2026-09-27, Claude.

- Decision: The demos are pages of `apps/demo` on the workspace source, published with the site,
  rather than single files over a CDN import of the published 0.24.0.
  Rationale: the 2.3 spec's deferred item is React demos published to the Pages site, and the site
  already aliases the packages to source, lints and typechecks them, and deploys on push. The CDN
  single-file recipe is exercised by the eval's ids 2 and 6 instead.
  Date/Author: 2026-09-27, Claude.

- Decision: Opus is the maker in every build, demo and eval, both arms.
  Rationale: the user's direction ("let opus be the maker"), and an eval whose arms differ only in
  the skill needs one maker.
  Date/Author: 2026-09-27, the user.

- Decision: The quality reading (a1 to a4, d1, e1) is dropped from the panel.
  Rationale: the 2.3 spec's own Deferred list carries the instrument's d1 calibration round, unrun;
  a scale whose reliability was never established adds a number without a meaning. The rule reading
  and the user's eye are the readings the pass line uses.
  Date/Author: 2026-09-27, Claude.

- Decision: r18, r19 and r23 are assigned to the audit and the source reviewer before any capture
  exists; the panel's answers on them are printed beside.
  Rationale: the 2.3 panel scored all three at zero on every page because a static capture cannot
  show them, and its post-hoc amendment was rightly withdrawn for changing the denominator after
  inspecting outcomes. Declaring the substitution before the run is what the withdrawal asked for.
  Date/Author: 2026-09-27, Claude.

- Decision: One fix wave per demo, after the source reading and before the panel.
  Rationale: the panel measures the skill's output at its finish condition, and the skill's own
  finish condition includes its QA lens; a page the skill would have caught is not the skill's
  failure. A second wave would measure the reviewer.
  Date/Author: 2026-09-27, Claude.

- Decision: Two held-out briefs, ids 5 and 6, added to the eval.
  Rationale: the four registered briefs are all within reach of `examples.md`, two nearly verbatim;
  the eval would otherwise measure retrieval of a worked example.
  Date/Author: 2026-09-27, Claude.

- Decision: The 2.3 photographs are exported from `f13ab38c` as rung one of the imagery ladder, with
  credits, and the makers never read the 2.3 pages or records.
  Rationale: no Unsplash key on this machine; the photographs are licensed, registered and credited
  already; the records would hand a maker a finished derivation of its own brief.
  Date/Author: 2026-09-27, Claude.

- Decision: The eval's React cells are Vite projects installing the PUBLISHED `@vitreajs/vitrea-react@0.24.0`
  from npm, and its vanilla cells import `@vitreajs/vitrea-web@0.24.0` from esm.sh; the demos run on
  the workspace source.
  Rationale: the two together cover both things a reader can pick up, the npm artefact and the
  repository; a Vite cell keeps JSX and the same tooling in both arms, and a single-file cell is
  what those briefs ask for. Both arms get identical mechanics text and identical tool access (the
  imagery search script is a tool, not a skill; the package READMEs are the library's own
  documentation), so the arms differ in the skill alone.
  Date/Author: 2026-09-27, Claude.

- Decision: Three calls made at the port (G2), accepted. (a) r18 is read from a sample of every
  glass text run against the CAPTURED pixels behind it, in both schemes, across the first viewport,
  the tiles and the open menu; the 2.3 DOM sample, which measures a label on WebGPU-tier glass
  against the page ground behind the canvas rather than the glass, is printed beside it. (b) The
  source reviewer writes `review/<slug>.json` (`r23`, `evidence`, optional `spanExceptions`) for the
  analyzer beside its `review/<slug>.md` for people. (c) A page that breaks the audit contract (no
  `__vitrea`, no reduced-transparency switch) reads as UNREAD on the clauses that need the runtime,
  not as failed, and gets no verdict until it exposes the handle.
  Rationale: (a) is what "measured on rendered pixels" means; (b) keeps one machine-readable shape;
  (c) is the honesty core's own rule, a missing read is not a zero.
  Date/Author: 2026-09-27, Claude, on the porter's report.

- Decision: The same four rater identities as the 2.3 panel, the maker's model among them.
  Rationale: comparability with the available-panel figures. The same-model bias (an opus rater on
  opus-built pages) is the same bias the 2.3 panel carried and is recorded, not corrected.
  Date/Author: 2026-09-27, Claude.

## Surprises & Discoveries

- Observation: The 2.3 panel's frozen captures survived only in a gitignored workspace directory
  that is gone, while their hashes and the pages that produced them are committed on a branch. The
  recovery path in D exists because hashes without pixels are a lock without a key.
  Evidence: `ls figma-design-workspace/glass-panel-baseline` → no such directory, 2026-09-27;
  `f13ab38c:docs/research/data/2026-09-10-liquid-glass-demos/baseline-captures.json`.

- Observation: The 2.3 panel closed as unmeasurable (D, step 4): 0 of 30 regenerated captures match
  their frozen SHA-256 although every mechanical read equals the baseline audit, and sixteen of them
  are byte-stable across three runs and two Chromium builds and still miss. The rendering moved with
  the machine (macOS 26.5 at baseline, 27.0 since 2026-09-18), on top of the animated pages' own
  variation. An arithmetic bound stands whatever the missing rater would have said: a tie fails, so
  a fourth answer can only lower a held count, and the highest three-rater count is 21 of 25.
  Evidence: `docs/research/data/2026-09-10-liquid-glass-demos/recovery-2026-09-27.md`; the 2.3
  spec's Outcomes, 2026-09-27.

- Decision (from the observation): This initiative's panel captures are committed evidence, not a
  gitignored copy. They are too large for the repository, so the capture set the raters read is
  archived as a GitHub release asset at landing, the way W39 archived its sitting, and the hashes
  beside the rules files name it.
  Date/Author: 2026-09-27, Claude.

## Deferred

- The user's eye reading (B, reading 4), when the six are up.
- Publishing the demos as single files over the CDN import as well, so a reader can lift one.

## Revision Notes

- 2026-09-27: chartered from the user's ruling on the 2.4.0 spec's three deferred items; nine
  decisions recorded; the recovery path for the 2.3 panel written after the captures were found
  missing.
