# Liquid Glass into the skill: the design language distilled, and six demos on vitrea 0.14.0

Status: pre-registered 2026-09-10; the user's decisions recorded (shape, briefs, home, taste anchors),
the reference and the audit in progress, no demo built. Parents: `2026-08-24-vitrea-liquid-glass-design.md` (the material) and the skill's
`references/material.md` (how the skill ships glass today). Research: `docs/research/2026-09-10-
liquid-glass-design-language.md` (34 sources, 25 checkable rules) and `docs/research/2026-09-10-
vitrea-authoring-surface.md` (the 0.14.0 authoring surface read from the code).

## Purpose

The skill can already say when glass is earned and how to ship it through vitrea. It cannot yet
compose a page the way Apple's system composes one: content edge to edge with navigation and
controls floating over it as the only glass; the material on the control, never on a card; capsule
and concentric geometry; bar items grouped so they read as one material; text on glass that meets
contrast in both schemes; menus that morph out of the control that opened them; monochrome controls
with one tinted primary. That is the Liquid Glass aesthetic, and the user's direction is to dissolve
it into the skill so the skill masters it rather than decorates with it.

After this initiative: a designer hands the skill a brief whose product has a live plane — artwork,
a map, a photograph, footage — and receives a page that a reader of Apple's guidelines would
recognise as the system: the plane fills the window, the floating layer is small and load-bearing,
every glass surface is a control, and the page still works with transparency reduced. Six such pages
exist under `apps/demos/`, built by the skill on the local vitrea 0.14.0 build, each with the audit
that says which of the language's rules it holds.

How to see it working: serve the repo root and open `apps/demos/<slug>/index.html` over
`http://localhost`; run the audit (`node docs/research/scripts/glass-audit.mjs apps/demos/<slug>`)
and read the rule table it prints; read `apps/demos/<slug>/DESIGN.md` for the plane split, the
floating-layer inventory and the group plan the page committed to.

## The measured problem

- The skill's material reference (`references/material.md`, 228 lines) covers the material axis,
  when glass is earned, the plane and group constraints, and two shipping paths. It has no account
  of the system's composition: which controls float, how bars group, concentric geometry, the scroll
  edge, the tint rule, the monochrome rule, the anti-patterns. A builder following it can put one
  correct glass toolbar on a page that otherwise reads as any web page.
- It is also stale in four places the code contradicts (research memo §7): the esm.sh pin at 0.6.0
  (npm's newest is 0.13.0, 0.12.0 never published, 0.14.0 unpublished); Gecko's CSS tier reported as
  verified where the conformance table says unverified; `GlassGroupState` listed with nine fields of
  eleven; and `file://` offered as a way to force the CSS tier, where a module page will not load
  over `file://` at all. It omits the backdrop-root trigger list and the size law's span-32 floor.
- Across the 52 settling builds, zero pages used glass, which is correct for those briefs and says
  nothing about whether the skill can compose for it.

## Design

### A. The distillation

A new reference, `skills/designer/references/liquid-glass.md`, read when the material axis resolves
to `glass over planes`, carrying:

1. **The two layers**, and the composition procedure for a glass page: name the live plane (what
   content fills the window and changes under the controls); inventory the floating layer
   (navigation, the primary action, transient platters — and nothing else); decide what stays in
   the content layer opaque; plan the groups (one material read per group, at most three per bar,
   text and icon buttons never sharing one); design the backdrop (varied, never a flat field —
   the "ghost glass" failure); choose the size family (vitrea's span floor of 32; a three-step
   sweep such as the demo's 112 / 68 / 40 with radii 26 / 18 / 12 and one thickness); place the
   scroll edge where content passes under a bar; write the fallback (the CSS tier, reduced
   transparency, increased contrast) as part of the design, not after it.
2. **The material's variants and the tint rule** — regular by default, clear only over media with a
   dim layer, one tinted control per view and it is the primary action, monochrome otherwise.
3. **Geometry** — three shape kinds only (fixed, capsule, concentric); nested radii derived from the
   container; capsules for bordered floating buttons, rounded rectangles for dense desktop controls.
4. **Legibility and accessibility** — contrast 4.5:1 to 17 pt and 3:1 above, in both schemes; the
   honest backdrop hint; the three accessibility modes as first-class states.
5. **Layout** — content to the window's edges with bars floating over it; safe-area insets; the
   plane fixed to the viewport; no custom background under a bar.
6. **Motion** — materialise and morph, never cross-fade; press glow and flex at the pointer.
7. **The anti-patterns**, named: glass on content, glass over glass, translucent everything, heavy
   tint, a hand-rolled blur, decorative glass cards, glass over a uniform field.
8. **The macOS reading** for desktop pages: window chrome, the sidebar, the toolbar, menus.
9. **The 25 checkable rules** from the research memo, each tagged, as the page's QA list.

Alongside: `references/material.md` corrected on the four points and extended with the trigger
list and the span floor; its shipping section rewritten for the workspace build (an import map to
`/packages/core/dist` and `/packages/platform-web/dist` served from the repo root; esm.sh at the
newest published version, marked unverified until re-checked); `references/qa-protocol.md` gains a
"glass page" pass that runs the 25 rules; `SKILL.md`'s workflow points to the reference at the
material step and its taste floor gains one line (a glass surface is a control or it is not glass).
Plugin version 2.3.0.

### B. The six demos

Six briefs written for glass, three product surfaces and three narrative pages (the user's choice;
the list is in the Decision Log once approved). Each is built by a fresh builder under the updated
skill, as one `index.html` plus `DESIGN.md` and an `images/` directory under `apps/demos/<slug>/`,
importing vitrea through the import map above, served from the repo root, WebGPU tier over
`http://localhost` and the CSS tier otherwise. Backdrops are real: photographs off the imagery
ladder, or a drawn plane (a map canvas) where the brief's world is drawn. `DESIGN.md` §4 carries
the plane split, the floating-layer inventory, the group plan, the size family and the backdrop
design, so the audit can read the page against its own law.

### C. The audit

`docs/research/scripts/glass-audit.mjs` renders a demo in Chromium over `http://localhost` with
WebGPU, captures the first viewport, the full page, two native tiles, and one capture with the
page's menu or platter open, and reads: page errors, overflow from the capture width, the contrast
pass, and the glass root's resolved state through `devMode` — the renderer that drew, every group's
diagnostics (a nested glass host, a same-plane overlap, a content-layer host, a demoted backdrop
root), and the count of glass surfaces. Then:

1. **The rule reading.** The 25 rules as a blind yes/no rubric on the captures, rated by the
   quality instrument's four-rater panel (the rubric machinery of `2026-09-09-quality-instrument.md`,
   a new item set), α per rule reported, the panel majority per rule per demo.
2. **The quality reading.** The instrument's a1–a4, d1 and e1 on the same captures by the same
   panel, for the level beside the settling arms.
3. **The user's eye, as comparison.** The user opens each demo live, in both schemes and with
   transparency reduced once, beside a reference capture of the Apple surface it is nearest to, and
   answers one question per demo — "is this the same system?" yes or no — then ranks the six. No
   scale: the quality instrument found that a person cannot place near-equal pages on one, and
   that only direct comparison worked.

A demo **passes** when at least 22 of the 25 rules hold by panel majority and no rule tagged
`[layer]` or `[material]` fails; the mechanical read shows no group diagnostic; and the page still
works with transparency reduced. The initiative **meets its purpose** when all six pass, the panel's
d1 mean over the six is at least 5.0, and the user answers "the same system" on at least five of
six.

**Stop.** If three or more demos fail a `[layer]` or `[material]` rule after one rebuild each, the
reference is not teaching the language; the result is recorded here and in the skill's spec chain,
and the next step is a rewrite of the reference from the failures, not a seventh demo.

### Cost, declared

The reference and the corrections: a working day. Six builds at about 0.5 M tokens each; the audit
script a half day; the panel's rule reading and quality reading 6 × 4 × 2 runs at about 0.1 M each,
5 M tokens; the user about thirty minutes at the demos and ten at the ratings.

## The six briefs

Every brief names a live plane, asks for realistic data, and ends the same way: desktop at 1440
wide, one HTML file on vitrea 0.14.0 (the workspace build through the import map), served from the
repository root. The builder receives the brief verbatim plus the serving mechanics.

**Product surfaces**

1. `music-player` — Design a desktop music player for a streaming service's Mac web client. The
   current album's artwork fills the window; the transport (play, pause, previous, next, a scrubber),
   the queue and the volume float over it, and a menu opens from the queue control for playlist
   actions. Realistic data: one album with its tracks, a queue of six, three playlists.
2. `transit-ops` — Design the desktop operations map for a city bus network's control room. A city
   map fills the window with live vehicle positions on their routes; a search field, a route-and-
   status filter toolbar and a selected-vehicle platter float over the map, and a sidebar lists the
   active alerts. Realistic data: forty vehicles on eight routes, six alerts.
3. `photo-review` — Design a desktop photo review and adjustment tool for a working photographer
   culling a shoot. The selected photograph fills the stage; a tool palette, the adjustment controls
   (exposure, white balance, crop) and a before-and-after compare toggle float over it, and a
   filmstrip of the shoot runs beneath. Realistic data: a shoot of thirty frames with ratings and
   flags.

**Narrative pages**

4. `film-festival` — Design the programme page for a city film festival. A full-bleed still from the
   opening film fills the first screen with the navigation and the date-and-tickets controls floating
   over it; the schedule by day and venue, the strands and the passes extend beneath. Realistic data:
   four days, three venues, twenty-four films.
5. `park-trails` — Design the trails site for a national park. A full-bleed relief map or panoramic
   photograph of the park fills the window with a floating trip planner (route, distance, weather,
   permits) over it; the trail list, the conditions and the permit steps extend beneath the floating
   bar. Realistic data: twelve trails with distance, elevation and current conditions.
6. `product-launch` — Design the launch page for a mirrorless camera from a small maker. Hero
   photography of the camera fills the first screen with the navigation floating over it; the sensor,
   the lenses, the body and the price scroll beneath the floating bar, and a configure-and-buy bar
   floats at the bottom. Realistic data: three lens options, two body colours, a price.

## Files

- This spec.
- `skills/designer/references/liquid-glass.md` (new), `references/material.md`, `references/
  qa-protocol.md`, `SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`.
- `apps/demos/<slug>/{index.html,DESIGN.md,images/}` × 6; `apps/demos/README.md` with the serve
  command and the import map.
- `docs/research/scripts/glass-audit.mjs` (new); the rule item set in `docs/research/scripts/
  settling/rubric.py` or beside it.
- Committed evidence: `docs/research/data/2026-09-10-liquid-glass-demos/` — each demo's audit
  JSON, the panel's rule and quality files, the user's comparison answers, `results.md`. The PNG
  captures are not committed (the settling run's were not either): `glass-audit.mjs` regenerates
  them from the committed page in one command, and `.gitignore` keeps the copies it writes inside
  `apps/demos/<slug>/` out of the tree.

## Decision Log

- Decision: Six briefs, three product surfaces and three narrative pages, one build each after the
  reference is distilled — not three briefs before-and-after, not a twelve-build baseline-then-
  rebuild.
  Rationale: the user's choice. Coverage of where glass belongs over a paired comparison; the
  before state is already known from the settling run (no page used glass) and from the
  reference's gaps.
  Date/Author: 2026-09-10, the user.

- Decision: New briefs written for glass, each with a live plane, over the existing eval briefs.
  Rationale: the user's choice. The skill's own rule earns glass only over a changing plane; the
  settling briefs are tables and documents.
  Date/Author: 2026-09-10, the user.

- Decision: The demos live at `apps/demos/<slug>` and load the workspace's 0.14.0 build through an
  import map over a local server; not the `demos` branch on a published version, not scratch.
  Rationale: the user's choice, and 0.14.0 is unpublished (npm's newest is 0.13.0). A page that
  imports from `/packages/*/dist` is one HTML file plus a served repo; `DESIGN.md` says so plainly.
  Publishing the demos is a later decision.
  Date/Author: 2026-09-10, the user.

- Decision: The taste anchors are the macOS Tahoe apps — Finder, Safari, Music, Maps, System
  Settings on macOS 26: window chrome, sidebars, floating toolbars, menus — and the reference's
  macOS reading and the demos' reference captures are drawn from them.
  Rationale: the user's choice; the demos are desktop web pages and macOS is the nearest analogue.
  iOS 26 remains the source for the strongest expressions (floating tab bars, bottom search) where
  the guidelines state them.
  Date/Author: 2026-09-10, the user.

- Decision: The six briefs above stand as drafted.
  Rationale: the user's approval of the list.
  Date/Author: 2026-09-10, the user.

- Decision: The audit's rule reading uses the 25 rules from the research memo, as written, with the
  quality instrument's panel; the pass line is 22 of 25 with no layer or material failure.
  Rationale: the rules are sourced one by one to Apple's guidelines and sessions (two to
  practitioners, marked); a page that fails a layer or material rule is not the language whatever
  else it does, while three of the finer rules can be lost to a desktop web context (safe-area
  insets, the scroll edge's exact style, the icon layering) without the page ceasing to read as the
  system. Rejected: the panel's d1 alone (it measures deliverability, not the language); the user's
  eye alone (one rater, the settling lesson).
  Date/Author: 2026-09-10, Claude.

- Decision: Curvature is written into the reference as the language's signature, used actively: a
  one-row glass surface is a capsule; rounded rectangles are for the compact controls inside a
  capsule and for the multi-row surfaces a capsule has no meaning on (platter, sidebar, sheet, a
  two-row transport). The demos get a capsule pass to match, after the panel has read the as-built
  captures.
  Rationale: the user's read of the six beside the Mac's apps — "use more rounded capsules than
  rectangular ones", and "it uses curvature very actively, preferring round capsules to the
  rectangular". The reference had said desktop density keeps controls rectangular, and every
  one-row bar container the builders drew came out at a fixed radius; the density belongs inside
  the capsule, not in place of it.
  Date/Author: 2026-09-10, the user; written by Claude.

- Decision: Post hoc, flagged as such — in the verdict, r18 (contrast on glass) and r19 (the
  accessibility modes) are read from the mechanical audit where one exists, r23 (motion) is unread,
  and the line is applied as "at most three of the rules read failed"; the panel-only count as
  pre-registered is printed beside it on every demo.
  Rationale: the prompt tells the panel that a rule it cannot see holding does not hold, and a static
  capture cannot show contrast in both schemes, the three accessibility modes or a morph — so every
  rater scored r18, r19 and r23 as 0 on every page, and the first two said so in their reports. Left
  in, "22 of 25" would have meant "every rule the captures can show", a line the spec never drew.
  The audit measures two of the three (rendered contrast in the page's scheme; the reduced pass with
  the override honoured and the material moved) and nothing measures the third. The amendment was
  made after two of four readings had arrived and before any verdict was written; the panel-only
  reading stays in the report so the effect of the amendment is visible on every row.
  Date/Author: 2026-09-10, Claude.

## Surprises & Discoveries

- Observation: The workspace build fails on this machine because a stray Yarn Plug'n'Play
  manifest, `~/.pnp.cjs` (2025-09-30, 451 KB), sits in the home directory; esbuild finds it walking
  up from every package and then refuses the workspace's own imports. With the file set aside for
  the build's duration, core built in 0.3 s and the full workspace built clean under the Homebrew
  Node 26 (the shell's default is Node 22; the repo asks for 24). On the user's decision the file
  now lives at `~/.pnp.cjs.disabled`.
  Evidence: the tsup error naming `../../../../../.pnp.cjs`; `BUILD-EXIT 0` with it moved aside.

- Observation: `references/material.md` is stale on four points the code contradicts (research
  memo §7), and 0.14.0 is unpublished while the reference pins esm.sh at 0.6.0.
  Evidence: the authoring-surface memo, file and line per point.

- Observation: vitrea 0.14.0's WebGPU tier drew an opaque white rectangle across the interior of
  any surface over ~307 px in both dimensions, inset ~153 px from every edge — on Apple GPUs, on
  either sampling backend. Two builders found it independently the same hour (music-player's queue
  sidebar, park-trails' permit platter) and designed under it; a one-surface repro confirmed it.
  The outer shadow's falloff feeds `tanh` a cubic in depth over σ, Metal's `tanh` overflows to NaN
  past ~44, and NaN × (1 − coverage) put NaN in the pass's alpha. Fixed by clamping the argument to
  ±8 σ (identity to f32 there); a GPU spec now reads the deep interior of the fixture's 420 × 400
  surface and fails on the old shader with alpha 0. The 44 golden and GPU specs pass unchanged.
  Evidence: `.changeset/large-surfaces-draw-their-whole-interior.md`;
  `packages/renderer-webgpu/e2e/gpu/deep-interior.spec.ts`.
  A demo campaign is a renderer test the calibration bed is not: the bed's largest span is
  under the line, and no scene in it has a surface deep enough to reach 153 px.

## Deferred

- Publishing 0.14.0 (the user's `pnpm release`) and re-verifying the esm.sh single-file recipe at
  the published version, so a demo can be one file with no served repo.
- React demos on `@vitreajs/vitrea-react`; publishing the demos to the Pages site.
- The quality instrument's calibration round for d1 (its own Deferred list).

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-09-10: created from the user's direction ("six demos on vitrea, so the skill masters the
  Liquid Glass aesthetic") after the research round; the three shape decisions recorded; taste
  anchors and the brief list open.
- 2026-09-10 (later): the taste anchors (macOS Tahoe) and the six briefs recorded; the user's eye
  made a comparison task on the quality instrument's finding; the manifest moved aside.
- 2026-09-10 (builds landing): Files — the audit JSON is the committed evidence and the PNG
  captures are regenerable, not committed; the copies the audit writes inside a demo directory are
  gitignored.
- 2026-09-10 (user's read): the user's comparison answered in part (music-player and park-trails
  most convincing; "a good use"); the curvature decision recorded and the reference revised.
