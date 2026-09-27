# The materialist's second register: glass as the surface, proven on two pages

Status: chartered 2026-09-27; in progress. Parents: `2026-09-26-materialist-skill.md` (the skill
and its one register) and `2026-09-27-materialist-proof.md` (the instrument, the panel, the pass
line and the six demos this initiative's two join). Source material:
`docs/research/2026-09-27-glass-as-surface-prior-art.md` (Apple's own use of glass as the surface,
collected for this initiative).

## Purpose

The materialist encodes one reading of Liquid Glass, the macOS and iOS one: a screen has two
planes, the content opaque and full-bleed, and a small floating set of controls on glass above it.
It is the right reading for a product whose screen is its content, and the six gallery pages hold
it. It is also why those pages read, to the user's eye, as thin chrome over a picture, and why the
material never becomes what the user asked for on 2026-09-27: "a core material of design, not like
a sidecar".

Apple has that second reading too. On visionOS the window itself is glass, content sits on it, the
controls that act on it hang at its edge as ornaments, and legibility comes from vibrancy and from
what the environment behind the window is allowed to be. iOS puts content on glass on the Lock
Screen, in notifications, in widgets and in Control Center; macOS draws its own material at window
scale in Spotlight, Control Center and Notification Center. None of that is in the skill, so a
maker who wants glass to be the surface has no conditions to meet and can only break the two-layer
law by accident, which is the glassmorphism failure the skill was written against.

After this initiative: the skill carries two registers, each with its conditions, and a decision
step that chooses between them; the runtime's reach at window scale is stated (what is measured,
what is extrapolated, what each tier draws); two gallery pages exist in the new register, built by
fresh opus makers who read the skill alone and put through the same instrument as the six (audit,
independent source reading, one fix wave, the four-rater panel on a pre-registered rulebook); and
one held-out eval brief says whether the skill, rather than the model's defaults, chooses and
carries the register.

The user's ruling that opens this initiative (2026-09-27): "Let's try making liquid glass a core
of design too", after the answer that the six demos' restraint was the skill's instruction and not
a library limit.

## Design

### A. The two registers (G1: the skill)

The skill names them. **The instrument register** is the existing one: glass is an instrument
held over the world; the world is content, opaque, edge to edge; every glass surface is a
control, navigation or a transient platter. **The spatial register** is the new one: glass is the
surface the interface is made of, set into an environment; content sits on a few large, thick
windows; the controls that act on a window hang at its edge as ornaments in their own glass;
everything inside a window that is not content is a fill or vibrancy. The names are Apple's
lineage for each (WWDC25 219 names visionOS as the immersive end of the material's ancestry), not
a web coinage. The default is the instrument register; the spatial register is chosen, named in the
record before the first host, and justified by the product, never by a brief that calls its cards
glass.

**The decision function gains a step 0**, which register: the instrument register when the screen's
content is the world (media, a map, a document, a canvas, a worksheet) and a person acts on it with
a few controls; the spatial register when the product's surfaces are the interface and the world is
their environment: a launcher or start surface, a glance surface, a guide or label beside the thing
it describes, a display, an ambient or spatial product. A page in the spatial register with many
glass tiles has not chosen a register; it has failed into glassmorphism, and the rule that catches
it is the window count.

**The spatial register's conditions**, each a law in the skill, each grounded in the research
memo's Apple quotes (its §8 lists the ten things Apple's own glass surfaces have in common) or in
a runtime measurement named here, and each with a QA check. Two forms of the register are named,
because Apple keeps two contracts (memo §8.10): the **window**, an app's content on one glass
canvas with ornaments at its edge (visionOS), and the **glance module**, a small information unit
on its own glass backing (Lock Screen notifications, widgets, Control Center), which carries
headlines, figures and graphs rather than prose and keeps its foreground bright.

1. **The environment is the product's, and it is designed.** Apple's spatial glass sits over an
   uncontrolled room and takes the legibility job itself: it "limits the range of background color
   information so a window can continue to provide contrast" (HIG Materials, visionOS). vitrea's
   material at window scale is Apple's macOS material extrapolated past the bed, not that
   range-limiting glass, so on the web the page takes the job: one full-bleed, viewport-fixed plane
   on the texture path (photograph, footage, artwork, a painted scene), chosen and graded so that
   every window's DRAWN body lands clearly light or clearly dark in the scheme the page runs,
   outside the runtime's published-ink dead band (a property of the drawn surface, encoded roughly
   0.39 to 0.49, where neither the primary nor the secondary ink carries body text;
   `references/vitrea.md` §5), and calmer where body text sits than where the rims are (NN/g's
   charge, memo §6.1: contrast varies across the surface and one average is not enough). Three
   quantities are kept apart: the source's statistics, the tone input the runtime adapts to (a
   texture group's active-pose tone is the whole source's average unless the group declares the
   level measured under its own footprint, which a window covering part of a graded plane does),
   and the rendered surface behind each line of text, which is the only one the acceptance reads. It carries the product's colour. It may be alive when it
   is the product's content (footage, a simulation, a sky); it is never animated to make the glass
   look alive.
2. **Windows are few, sized to their content, and thick.** "Windows … should remain smaller when
   possible to avoid blocking too much of people's view", one window where possible, empty areas
   minimised (WWDC23 10072, HIG Windows). One to three at rest, each a real unit of the task (a
   document, a list, a panel, a sheet) or a glance module (one information unit). Every window and
   module, a surface carrying reading content, is at or above span 96, where the size law saturates
   the body's occlusion and legibility is protected by size (`references/optics.md` §2); an
   ornament's labels are judged by their rendered contrast, not by the ornament's span, and 96 is
   stated as the shipped material's saturation point rather than a text-host minimum. One thickness across the family: 8,
   or up to 14 with the reason recorded, since the runtime's own morph opens to 14. Generous fixed
   radii; the concentric anchor is the window's corner. The environment stays visible around every
   window at rest, so the shadow has a plane and the glass has something to be over.
3. **Content on glass is composed for glass.** Apple's spatial text is vibrancy in three semantic
   levels (standard text; descriptive text, footnotes and subtitles; inactive elements only), set
   heavier than on iOS (medium for body, bold for titles), with tracking increased, predominantly
   white, and tested at scale (WWDC23 10076, HIG Typography). On the web: ink is the runtime's
   vibrancy ladder on a child element, primary for standard text and controls, secondary for
   descriptive text, tertiary and quaternary never for anything a person must read; medium through
   bold weights at reading sizes with a measure and leading a reader can hold; contrast measured on
   rendered pixels for body text as for labels, across the environment's phases and in both schemes,
   and an authored ink where a ratio must be guaranteed. Windows carry lists, collections, grouped
   data and sections, as Apple's do; long prose gets a window of its own. A glance module carries
   headlines, figures and graphs, text at 11 px or larger, and keeps its foreground bright (WWDC25
   255); full-colour imagery on it is media, smaller than the module (HIG Widgets). Images and
   video on a window are opaque content in a concentric frame.
4. **No glass on glass; hierarchy inside a window is fills with roles.** Apple separates sections
   and input fields with darker materials and lifts interactive and selected elements with lighter
   ones, and says "try to not stack lighter materials on top of each other" (WWDC23 10076). The
   runtime has one material and refuses nesting, so on the web the inner hierarchy is fills: a
   darker fill (black at a fixed low alpha) to separate a section or hold an input, a lighter fill
   (white at a fixed low alpha) for an interactive or selected element, never lighter on lighter,
   never a second material. A control that needs its own material is an **ornament**: "floats in a
   plane that's parallel to its associated window and slightly in front of it", presents controls
   "without crowding or obscuring the window's contents", no wider than the window, few, its
   buttons plain on the ornament's glass (HIG Ornaments). On the web: a separate surface in the
   overlay plane, in its own group, attached to a window's edge at the gap the runtime derives,
   holding plain buttons; on the texture path it sits outside the window's edge rather than across
   it, because the overlay group samples the environment and would draw it where the eye expects
   the window; the one permitted glass-over-glass across planes is on the DOM path, where the proxy
   sees the composite.
5. **Colour is sparing, and it goes where it can be seen.** "Use color sparingly, especially on
   glass"; "prefer using color in bold text and large areas", "in a background layer or an entire
   button"; white text and symbols most of the time (HIG Color, WWDC23 10076). Windows and modules
   are untinted; the environment carries the colour and the window takes it (the hue retention on
   the GPU tier). An accent is spent on an entire button or fill, or in bold text, never in light
   type or a thin mark; at most one tinted glass surface per view, and it is an ornament's control.
   Imagery keeps its colour; identity comes through imagery rather than an opaque brand-coloured
   window (WWDC24 10086's Red Bull TV example).
6. **Depth.** The window's shadow onto the environment is the material's and the only elevation on
   the page; sheets and popovers emerge from their control in the overlay plane by morph; windows
   never overlap one another within a plane.
7. **Scroll.** Content scrolls inside the window's own clip, a child scroller with scroll edges at
   the window's inner edges; ornaments stay put while it scrolls (HIG Ornaments); the window host
   does not scroll; the plane is viewport-fixed.
8. **Variants.** Regular wherever a surface carries "a significant amount of text, such as alerts,
   sidebars, or popovers" (HIG Materials), which is every window and module. `clear` only over
   media the person is watching, under Apple's three conditions, and then with the dimming layer
   **painted into the plane by the page**: the HIG's conditional figure is a dark layer at 35 %,
   the API example's is black at 30 %, and the runtime requires the policy, resolves it and draws
   no scrim on either tier (Surprises). Both are uncalibrated and the record says so.
9. **The material yields when attention or accessibility require it.** Apple dims passthrough for
   a film, dims and thickens a sheet as focus deepens, and lets Reduce Transparency make its
   transparent backgrounds solid (memo §2.8, §4). On the web: Reduce Transparency frosts the
   windows harder; Increase Contrast strengthens the edges; forced colours turns every window into
   a Canvas panel with a CanvasText border and every authored fill must survive substitution; a
   modal task over a window darkens the plane beneath it; on the CSS tier the root sums the areas
   of its present hosts times the device pixel ratio squared against a 0.4 M device px budget
   (`css-tier-layers.ts` `filteredAreaDevicePx`, `root.ts`), so one 600 × 500 window is two-layer
   at a ratio of 1 and collapsed at 2; the record reports the `cssBody` the page actually resolved
   and both forms are looked at as that tier's design.
10. **Motion.** The register adds none: windows materialise and morph, ornaments press as light and
    compression, nothing moves at idle; a live environment is content changing, not the glass.

Two boundaries the memo draws are kept as bans: the Dynamic Island is opaque, so a compact live
status is not a glass-surface precedent; and Apple's glass clock numerals are display type, not a
paragraph precedent, so no page reads a glass glyph as licence for prose on a thin sheet.

**Where it lands in the skill.** `SKILL.md`: §1 gains the second Apple reading beside the first;
§2 gains the spatial register's articulation (the world seen through glass rather than an
instrument over a world; the identity lives in the environment, the type and the window geometry;
daylight still the distinctive case); §3 gains step 0; §4 gains a section "The spatial register"
carrying the ten conditions as laws and a line in each affected section saying which register it
governs; §5 gains the register row; §6 gains "which register" and "the environment"; §7 gains the
register's bans; §8 gains checks 21 to 28 tagged for the register; §9 routes. `references/optics.md`
gains the thick regime at window scale (the laws' fitted reach, span 160 on the bed, the scatter
ramp to 256 fitted with the largest scene held out, extrapolation beyond; the shadow's amplitude
and σ at window spans; the dead band; the CSS area budget; what `clear` draws and does not).
`references/vitrea.md` gains the recipe: a window as a `GlassSurface` on a sectioning element with
a label, not interactive, its scroller inside; the ornament in the overlay plane; fills; the ink
tokens on children; `clear` with the painted dimming layer; reading the collapsed CSS body back.
`references/examples.md` gains the two demos as worked derivations and a "which register" note in
"What the six have in common". `docs/research/materialist-distillation.md` gains one row per new law
with its provenance. The register's rules for the panel (B) are written into the research memo.
Skill 1.1.0; plugin 2.5.0.

**Authoring discipline.** The register is stated as conditions and consequences, not as a
case study of two pages; nothing is written that a maker would already do; each new line has to
change what a maker would otherwise build. The skill worker reads the research memo and the
runtime facts named here and writes the register; an independent review verifies every claim
against the source before any maker reads it.

### B. The rulebook and the instrument (G2)

The 2.3 panel's twenty-five rules are the instrument register's; five of them contradict the
spatial register by construction (r1, no content surface uses glass; r3, the count is small and
each is a control; r17, content does not sit under a glass control at rest; r20, bars float over
content; r21, safe-area insets). A panel that read the two pages against them would fail them for
choosing the register, which says nothing.

So the register gets its own rulebook, written before any capture exists: "Rules a spatial-register
page can be checked against", a numbered section of the research memo, SHA-pinned by
`glass-rules.py` under a `--rules spatial` option exactly as the twenty-five are. It carries the
instrument rules that apply to any glass page verbatim, with their `r` number beside each so the
per-rule comparison to the six is direct (material r4 to r7 and r16; geometry r8 to r10; grouping
r11 to r14; legibility r18, r19; motion r23; colour r24, r25), two rules **adapted** and marked
`(~ rN)` rather than carried, because their verbatim form forbids what the register requires (r15,
a scroll edge "nowhere else" than under a floating control, where a window's inner scroller needs
one at its clipping edge; r22, no darkening layer under a sheet, where Apple's own modal sheet
takes one), a table naming the five rules the register replaces (r1, r3, r17, r20, r21) and what
replaces each, frozen before any capture, and spatial rules in their place: the environment is the product's and its level under every window is outside the dead
band; windows are few (one to three at rest) and each is a unit of the task; every text-bearing
surface is at or above span 96; the environment is visible around every window at rest; ink on
windows is the vibrancy ladder with body text measured at 4.5; inside a window everything that is
not content is a fill, never glass; ornaments are separate surfaces at a window's edge, outside it
on the texture path; content scrolls inside the window with its own scroll edges; images on a
window sit in a concentric frame; colour is sparing and sits in bold text, an entire button or a
fill, never in light type; windows and modules are untinted; the CSS tier's collapsed body and the
forced-colours panel are designed states. Tags: `[environment]`, `[layer]`, `[material]`,
`[geometry]`, `[grouping]`, `[legibility]`, `[layout]`, `[motion]`, `[colour]`.

The audit (`glass-audit.mjs`) is extended before any page exists, because the proof's own record
says the inherited protocol misses what this register is made of (its Deferred list: the audit
scrolls the document, so a page whose content scrolls inside a fixed element yields no second
screen). Seven additions: (1) **inner scrollers**: every scrollable descendant of a registered
host is enumerated and captured at its top, middle and bottom, with the contrast sample taken at
each; (2) **per-line contrast with the text suppressed**: a second capture of each state with an
injected rule making glyphs transparent, so the ground behind each line box is read from the
material alone; the ratio is computed per line against the line's computed ink, the worst line
gates, and every failing line is kept; (3) **the CSS tier**, a pass over the same states with the
page's `?tier=css` switch (C), reading `cssBody` per group; (4) **the receded pose**, a pass with
`root.setWindowActivation("inactive")` through `window.__vitrea`, captured and sampled; (5) **the
environment's phases**: where the page exposes `window.__glassDemo.phases()` and `setPhase(id)`,
each phase is captured and sampled in both schemes, so an exhibition with eight works is read on
eight backdrops rather than one; (6) **roles**: each registered host carries `data-glass-role`
(`window`, `module`, `ornament`, `platter`, `control`), and `text-bearing-span-under-96` applies to
`window` and `module` hosts only, while a text-bearing host with no role on a spatial page is the
finding `unroled-host`; (7) the **drawn surface level** per host, from the text-suppressed capture,
flagged when inside the dead band, beside a 24 px ring of the environment outside the box, and the
fraction of the first viewport covered by glass. A state the page cannot reach (no phases, no
`?tier=css`) reads UNREAD on the clauses that need it and blocks the verdict rather than shrinking
the tested population. The assigned readings carry over: r18 from the per-line contrast, r19 from
the three preference passes and the reduced capture, r23 from the source reviewer's
`review/<slug>.json`. `glass-rules-analyze.py` gains the spatial rulebook, its tags, the UNREAD
rule and its pass line.

**Pass line, per page.** Every rule tagged `[environment]`, `[layer]` or `[material]` holds by
panel majority; at least 88 % of the rulebook holds (the 2.3 line's 22 of 25, carried as a
proportion; assigned readings on the three rules read elsewhere); zero diagnostics on both
channels; zero ban-subset findings; every rendered-pixel text pair on glass, body text included,
passes its floor in both schemes at every captured state, the worst line gating, with any miss
recorded as a failure and never as a pass with a residual; and no clause reads UNREAD. The pre-fix
readings are kept beside the post-fix ones, as the proof kept them. **Stop and diagnose:** a page
still failing an `[environment]`, `[layer]` or `[material]` rule after the one fix wave is
classified by cause before anything is rewritten: the rule's text, a runtime seam, the instrument,
or the maker. Only the first is the register's failure, and then the next step is a rewrite of the
conditions, not a third page; the other three go to the tracker or the instrument. Two pages are a
bounded demonstration that the conditions can be met; whether the skill TEACHES and CHOOSES the
register is the eval's claim (D), not the pages'.

**Comparability.** Same rater identities, same capture set per page, same seeded order, same
blind yes/no instruction, same analyzer. The rulebook differs by design and the difference is
named per rule by the `r` numbers.

### C. The two pages (G3)

Two, because the register has two Apple precedents and a page per precedent shows both: the
visionOS one (a window with content and ornaments) and the iOS glance one (a few glanceable
modules over a wallpaper). Both light-first with `colorScheme="auto"`, because daylight is the
distinctive register and both are measured in both schemes anyway.

**7. `exhibition`** (the visionOS reading). "The online viewing room of a museum exhibition,
*Weather in Painting*: one work fills the screen at a time, and the visitor reads about it while
seeing it. The label essay and the work's data sit on glass set into the painting; the audio guide's
transport and the way between works hang at that window's edge. Realistic data: eight works in the
public domain, with their real titles, makers, dates and collections, sourced with credits."

**8. `start-page`** (the iOS glance reading). "A browser start page, Daybreak: the day's photograph
fills the window, and the time, the weather, the day's agenda, the tasks and the places the person
goes sit on glass over it, glanceable from across the room and workable up close; a search field
leads. Realistic data: a full day's agenda, seven tasks, twelve places, a five-day forecast."

**Shared tail** (replacing the six's): "Desktop at 1440 wide. A page of the vitrea demo site at
`apps/demo/gallery/<slug>/`, written in React through `@vitreajs/vitrea-react` on the workspace
source (0.24.0). Follow `skills/materialist/SKILL.md` and the references it routes to. The
interface is glass set into its environment, the skill's spatial register: say so in the record
and derive the page from the register's conditions." The brief names the register because the
pages exist to show it; whether the skill CHOOSES the register from a brief that does not name it is
the eval's question (D).

**The maker, the wiring, the audit contract, the imagery, the concurrency**: as the proof's A, with
two makers on ports 5187 and 5188, and four additions to the audit contract that B needs: the page
mounts its root with `renderer="css"` when the URL carries `?tier=css`; every registered host
carries `data-glass-role`; a page whose environment has states exposes `window.__glassDemo.phases()`
returning their ids and `setPhase(id)` to show one (the exhibition's works; the start page's
photograph if it changes); and the receded pose needs nothing from the page, since the audit pins
it through the runtime's own `setWindowActivation`. The page shells, the Rollup inputs, the gallery index entries
(the index says which register each page is in) and the Playwright slugs are scaffolded before
dispatch. Imagery: the exhibition's works are public-domain paintings (a museum's open-access
programme or Wikimedia Commons), credited by maker, title, date and collection; the start page's
photograph comes from the imagery ladder as before. The makers never read the six pages' records.

**Readings**, as the proof's B: the mechanical read; the panel on the spatial rulebook; the source
reading by one independent `astra-high` per page against the skill's checks 1 to 28 and the three
r23 criteria, one opus fix wave, re-audit; the user's eye, theirs to give, beside the nearest Apple
surface, which for the exhibition is a visionOS window (no native capture is available on this
machine, and the record says so) and for the start page is the iOS Lock Screen or macOS
Notification Center.

### D. The eval (G4)

One held-out brief, id 7, in `evals/materialist.json`, written after the skill change and absent
from every reference, that does NOT name the register: "Design the guest page for a mountain
lodge's in-room display. The view from the room, live, fills the screen; the guest's stay, the
day's weather and trails, room service and the concierge sit over it. React through
`@vitreajs/vitrea-react`. Realistic data: a three-night stay, six trails, a room-service menu." Its
criteria, written before any build, include: the register is chosen and named with the reason; the
environment is on the texture path and its level under every surface is measured and outside the
dead band; every text-bearing surface is at or above span 96 and there are at most three at rest;
ink is the vibrancy ladder with body text measured at 4.5 in both schemes; inner controls are fills
and any control with its own material is an ornament outside the surface's edge; no glass tiles;
the CSS tier's collapsed body is named in the record; forced colours looked at. Arms, maker, grader,
blinding and mechanics as the proof's C. Expectation, in two parts scored separately: the register
CHOICE, criterion c1 (the register named with a product-based reason), must hold in the
`materialist` arm for the line to be met at all; then execution, the remaining criteria, at least
80 % held and strictly more than `none`. A `none` arm that chooses windows over the view is
recorded as such; the skill's value on this brief is the conditions, not the idea. And because one
positive brief cannot tell a decision function from a new default, id 8 is a matched control the
skill must keep in the instrument register: the same lodge's public website, its valley photograph
filling the first screen with the navigation and a Book control floating over it and the rooms,
trails and story running beneath. It runs in the `materialist` arm only (the `none` arm says
nothing about the skill's choice) and is graded on the choice and its execution; both outcomes are
printed side by side.

### E. What is Apple-measured and what is Apple-shaped

Stated in `references/optics.md` and in every record: the material's laws are fitted on spans up
to 160 CSS px (the bed's `rrect-lg`) and the scatter ramp to 256 with that scene held out, so a
window at span 400 to 800 draws every law extrapolated; visionOS's glass is a different material
(Colin Cornaby's reading in the prior-art memo) and no visionOS capture exists in the harness, so
the register on the web is Apple's macOS material composed in Apple's visionOS way; `clear` is
uncalibrated and its dimming layer is the page's; the CSS tier at window scale is the collapsed
body. These are recorded as the register's fidelity position, not hidden in a footnote.

## Cost, declared

Research memo about 0.5 M tokens; the skill worker about 1 M and its review 0.3 M; the instrument
worker 0.4 M; two makers at 0.6 M; two source reviews at 0.2 M and two fix workers at 0.2 M; eight
rater runs at 0.1 M; two eval builds at 0.3 M and one grader at 0.15 M; the spec's review 0.2 M.
About 6 M tokens, most of it in parallel; the user's time is the eye reading, about ten minutes,
and one line on Harvestar if they want a page shaped toward it.

## Files

- This spec.
- `docs/research/2026-09-27-glass-as-surface-prior-art.md` (the memo, with the spatial rulebook).
- `skills/materialist/SKILL.md` (1.1.0), `references/{optics,vitrea,examples}.md`,
  `docs/research/materialist-distillation.md`; `.claude-plugin/plugin.json` and `marketplace.json`
  (2.5.0); the 2.4.0 spec's Revision Notes.
- `apps/demo/gallery/{exhibition,start-page}/index.html`, `apps/demo/src/gallery/{exhibition,start-page}/`,
  `apps/demo/src/gallery/index/main.tsx` (two entries and the register per entry),
  `apps/demo/vite.config.ts`, `apps/demo/e2e/gallery.spec.ts`, `apps/demo/README.md`, `README.md`.
- `docs/research/scripts/glass-audit.mjs`, `glass-rules.py`, `glass-rules-analyze.py`.
- `docs/research/data/2026-09-27-materialist-spatial-register/`: `audit/<slug>.json`,
  `review/<slug>.{md,json}`, `rules/<rater>/<slug>.json`, `results.md`, `panel-captures.{json,sha256}`;
  `eval/criteria.json`, `eval/grade-assignment.json`, `eval/audit/`, `eval/7/grade.json`,
  `eval/results.md`.
- `evals/materialist.json` (id 7).
- `docs/doperpowers/specs/tech-debt-tracker.md` (the runtime seams found).

## Decision Log

- Decision: A second register beside the first, rather than loosening the two-layer law.
  Rationale: the two-layer law is Apple's stated rule for the platforms it governs and the six
  pages show it produces the material correctly there; the user's request is for a different
  composition Apple also makes, not for the first one done more loosely. Two registers with a
  choosing step let a maker take either deliberately; one law with exceptions would let both
  happen by accident.
  Date/Author: 2026-09-27, Claude (recommendation); the user's direction "let's try making liquid
  glass a core of design too", 2026-09-27.

- Decision: The registers are named the instrument register and the spatial register.
  Rationale: each name says what the glass is in it, and "spatial" is Apple's own word for the
  platform whose windows are glass; "window register" would collide with the browser window and the
  skill's window pose, and "surface register" with the runtime's `GlassSurface`.
  Date/Author: 2026-09-27, Claude.

- Decision: No condition enters the skill without an Apple statement or a runtime measurement behind
  it, and the memo is written first.
  Rationale: the register's whole value is that it is Apple-shaped; a condition invented for the
  web is glassmorphism with a citation style. The web-only conditions (the CSS area budget, the
  texture-path ornament placement, the painted dimming layer) are runtime facts named in this spec.
  Date/Author: 2026-09-27, Claude.

- Decision: The clear variant's dimming layer is the page's to paint, and the skill says so.
  Rationale: a runtime fact (Surprises): core requires and resolves the policy and neither tier
  reads it. Drawing it in the runtime is a feature for a runtime wave, not a skill claim.
  Date/Author: 2026-09-27, Claude.

- Decision: Two pages, one per Apple precedent, briefs naming the register; one eval brief that does
  not name it.
  Rationale: the pages exist to show the register and its two precedents, so they are told which
  register they are in; whether the skill chooses the register from a product description is a
  separate question and the eval asks it on a brief the skill has never seen.
  Date/Author: 2026-09-27, Claude.

- Decision: The rulebook carries the applicable instrument rules verbatim with their `r` numbers and
  replaces the five register-contradicting ones; the pass line is 88 % with the fatal tags
  `[environment]`, `[layer]`, `[material]`.
  Rationale: per-rule comparability to the six where the rule is the same; a line that is the 2.3
  line's proportion rather than a new number; and the register's fatal failures are the three things
  that make a page not this register.
  Date/Author: 2026-09-27, Claude.

- Decision: Opus makers, `astra-high` readers, one fix wave, the four 2.3 rater identities, captures
  archived as a release asset at landing.
  Rationale: carried from the proof's Decision Log, for the same reasons and for comparability.
  Date/Author: 2026-09-27, Claude.

- Decision: No runtime change in this initiative.
  Rationale: the register is reachable on 0.24.0 as it is (large `GlassSurface`, texture planes,
  overlay-plane ornaments, the ink tokens, `clear` with a painted layer); every seam a maker hits is
  recorded in the tracker with the shape of the runtime work, as the proof did.
  Date/Author: 2026-09-27, Claude.

- Decision: The spec's adversarial review (nine findings, two blocking) is accepted in full and
  the charter amended before any maker reads it: the dead band is the drawn surface's, not the
  environment's, and three quantities are kept apart (condition 1); the span floor governs windows
  and modules, not ornament labels (condition 2); the CSS collapse is a root total, not a viewport
  fact (condition 9, Surprises); the audit scrolls inner scrollers, reads contrast per line with
  glyphs suppressed, captures the CSS tier, the receded pose and the environment's phases, and
  reads roles (B); r15 and r22 are adapted rather than carried and the five replacements are
  tabled before capture (B); a missing state reads UNREAD and blocks the verdict (B); the stop rule
  diagnoses before it rewrites (B); the eval's choice criterion is mandatory and a matched
  instrument-register control is added (D). Nothing was dismissed: each finding named a way the
  proof could pass an unreadable window or fail a page that followed the conditions.
  Date/Author: 2026-09-27, Claude, on the reviewer's report.

- Decision: Skill 1.1.0, plugin 2.5.0.
  Rationale: a second register is a feature of the skill, not a correction.
  Date/Author: 2026-09-27, Claude.

## Surprises & Discoveries

- Observation: The clear variant's dimming policy is required and resolved by core
  (`packages/core/src/material.ts`, `resolveMaterial`) and never read by either tier: no file under
  `platform-web/src` or `renderer-webgpu/src` reads `dimming`, and `adaptation: "constrained"` is
  likewise unread. `clear` differs from `regular` only by its optics constants (blur σ 4, tint alpha
  0.1, rim 1.25 at 0.14). The skill's §10 of `optics.md` and the cookbook say the runtime "refuses
  a clear surface without" a dimming policy, which is true, and imply the layer is drawn, which is
  not. Recorded in the tracker; the register's condition 8 states the page's duty.
  Evidence: `grep -rn dimming packages/platform-web/src packages/renderer-webgpu/src`, 2026-09-27.

- Observation: The CSS tier's two-layer body collapses when the sum over the root's PRESENT CSS
  hosts of width × height × dpr² exceeds 0.4 M device px (`CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX`,
  a compositor budget measured in W16). This charter first said a window-sized surface always
  collapses; the spec's adversarial review corrected it: a 600 × 500 window is 0.3 M at a ratio of
  1 (two-layer) and 1.2 M at 2 (collapsed), so the same page draws either form by machine, and the
  record has to report the `cssBody` it resolved rather than declare one.
  Evidence: `packages/platform-web/src/css-tier.ts:493–510`, `css-tier-layers.ts:589–594`,
  `root.ts:1948–1983`.

- Observation: The calibration bed's largest span is 160 CSS px (`rrect-lg`; span 128 declared
  without fixtures); the scatter ramp's top of 256 was fitted with `rrect-lg` held out. Every law a
  window at span 400 to 800 draws is an extrapolation beyond the bed.
  Evidence: `apps/reference-apple/scenes.json`, the `rrect-lg` and span-128 comments;
  `renderer-webgpu/src/material.ts`, `sizeScatterSpanMax`.

## Deferred

- A page shaped toward Harvestar, once the user says what it is (asked 2026-09-27, non-blocking).
- A native visionOS capture for check 20 on the exhibition page; no device is available.
- A dark, media-rich page in the register that spends `clear`, with a measurement of the variant
  against a native capture (the variant has no calibration scene).
- The runtime drawing the clear variant's dimming layer from the policy it already resolves.
- The instrument register's second wave (the proof's Deferred) is unchanged by this initiative.

## Outcomes & Retrospective

To be written at landing.

## Revision Notes

- 2026-09-27: chartered from the user's direction, after the answer that the six pages' restraint
  was instruction rather than library; the research memo dispatched first; the two runtime facts
  (dimming not drawn, the CSS area budget) and the bed's span reach found while reading the runtime
  for the register; nine decisions recorded.
- 2026-09-27 (review): the adversarial review's nine findings applied (Decision Log); the memo
  landed and the ten conditions re-grounded in its quotes, with the two forms (window, glance
  module) and the two boundaries (the Dynamic Island, the glass clock) added; eval id 8 added as
  the matched control.
