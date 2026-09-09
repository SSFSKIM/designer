# North Cascades — Trails · design law

The trails page of a national park, built on vitrea 0.14.0 through the workspace import map. One
`index.html`, inline CSS and JS, no framework, no build step, one photograph in `images/`.

## 0. Stance commitment

**A quadrangle sheet, read under the mountain it describes.** The page is a printed topographic
sheet — ink, hairlines, contour brown, four plates and no cards — that slides up over a fixed
photograph of the park, with exactly one floating layer of glass controls between the reader and
both. It is a survey document, not a brochure: it tells a hiker what the mountain is doing today and
whether they can legally sleep on it. It is **not** a destination-marketing page, not a card grid of
pretty trail thumbnails, and not a dashboard.

*If a decision is ever ambiguous, choose the more surveyed option* — the one that states a measured
figure, names its source and its date, and draws a rule instead of a box.

**Axis position.**

- **density — considered, dense where the comparison lives** (brief-fixed): twelve trails against
  six attributes is a real matrix; the sheet's margins stay wide so the matrix can be tight.
- **criticality — consequential** (brief-fixed): a hiker choosing against a snow line, a ford and a
  permit quota can be turned around at the trailhead or hurt above it.
- **energy — still**: the photograph carries every bit of movement this page needs.
- **type — annotation**: map lettering. One geometric sans for names and prose, one mono for every
  figure, italic reserved for water features as hydrography is set on a real sheet.
- **material model — glass over planes for the floating layer, printed for everything beneath.**
  Glass is earned: the controls sit over a photograph and over live conditions that change under
  them. The page's own surfaces are ink on paper and obey the printed model — no shadow anywhere,
  no card, radius 0–2. Rejected: *elevated*, which would put opaque slabs over the mountain the
  page exists to show.
- **colour commitment — full palette**, in the quadrangle's own sense: four printing plates —
  black, contour brown, water blue, a red overlay — each with exactly one job. Saturated colour
  otherwise lives in the photograph.
- **accent job — the red plate**: primary action, focus, selection, the snow line, and the closed
  status. Nothing else.
- **ground lightness — light**: paper. A survey sheet is printed, and the page is read in daylight
  at a trailhead kiosk or a kitchen table the night before.
- **ground temperature — cool**: alpine light, and the photograph's own temperature.

**Rejected coordinate vector.** *dense · consequential · still · annotation · glass over planes ·
four plates · red plate · **dark** · cool* — the dusk-ridge reading, with the sheet in slate and the
photograph at last light. Rejected because dark is where glass is easy (`references/material.md`),
because a printed sheet in a daylight product is paper, and because a dark ground would have made
the page's one hard problem — a legible control layer over a bright, high-frequency backdrop —
disappear instead of being solved.

**Derivation.**

- *Accent.* The red plate of a USGS quadrangle carries the human overlay — the survey grid,
  boundaries, the things people added to the mountain. This page's own additions are permits,
  quotas and closures, so the human overlay is exactly the accent's job. The value, `#a62941`
  (`oklch(0.485 0.16 15)`), is pulled toward the crimson the huckleberry meadows at Cascade Pass
  turn in the second week of September, which is the date this page is written for. **Weighed and
  rejected: glacier turquoise**, Diablo Lake's rock-flour blue — the most park-specific hue
  available and the wrong one, because the photograph already carries the park's cool colour and a
  cool accent would dissolve into it.
- *Ground.* The scene sentence: *a hiker at the Wilderness Information Center counter in Marblemount
  at nine in the morning, comparing twelve trails against a snow line.* That is a sheet of paper.
  `#edf2f0` is a cool near-white, faintly green — the tint a quadrangle's vegetation plate leaves in
  its white. **Weighed and rejected: a warm buff paper**, the older USGS sheet stock, which would
  have fought the alpine photograph's temperature and landed in the cream band.
- *Type.* Trail names are place names and must read as map lettering: Avenir Next, a geometric sans
  with the even colour a map label needs at 13–15px. Every figure a hiker compares — miles, feet,
  freezing level, quota — is set in Menlo so the columns align without a tabular-figure feature.
  Water features are italic, which is the one type rule this page borrows from cartography rather
  than from software.

**Signature element — the snow line.** One dashed red-plate rule at 6,000 ft, drawn across all
twelve elevation profiles at one shared vertical scale, so how much of each trail is above today's
new snow is a glance rather than a calculation.

**Clone test.** Any park's trails page lands at dense-and-consequential, and most would land at
still and light. The plate palette, the crimson from a specific week's meadows, the italic
hydrography and the shared-scale snow line are this page's and not portable. The near neighbour to
watch is the *broadsheet* default — hairlines, no radius, tight columns — which this page shares
two surface habits with and nothing else: the rules here are a quadrangle's plate structure, the
measure is wide rather than columnar, the density is a table's, and the sheet carries a contour
field and a hydrography convention a newspaper has no use for.

## 1. Palette, with usage rules

Values live in the `:root` token block of `index.html`. Four plates, named for the printing plates
of the sheet they come from:

- `--ink` `--ink-2` `--ink-3` — **the black plate.** All type, all rules. `--ink-3` is the smallest
  it goes and clears 4.77:1 on paper.
- `--contour` — **the brown plate.** Contour hairlines in the sheet's ground texture and the
  elevation profile's own line and fill. Never type.
- `--water` — **the blue plate.** Water-feature names, set italic, and the ford readouts. Never a
  button, never a border.
- `--sheet` `--sheet-2` `--sheet-edge` — **the ground.** Named for the survey sheet it is, and it
  is not in the cream band: `oklch(0.958 0.006 170)` is a cool near-white with a green cast, well
  outside L 0.84–0.97 × C < 0.06 × hue 40–100.
- `--accent` — **the red plate**, and the only accent. It appears on: the primary action (its tint
  seed and its filled forms), every focus ring, the hover state of a link or a trail name, the
  selected trail row, the snow line, and the `closed` status. Nowhere else — not on a date, not on
  a figure, not on a heading. There is no second accent and no gradient anywhere on the page.

Status is never colour alone: every status carries a glyph and a word (`● open`, `▲ caution`,
`■ closed`), and the selected trail row is a background tint plus a leading `▶` plus the name in the
red plate plus `aria-current` — never a coloured side stripe, which is banned outright. Every colour on the page resolves from `:root`, including the ones inside SVG, which
take their stroke and fill from `.p-line` / `.p-snow` / `.p-fill` / `.p-base` rather than from an
attribute. Two literals remain and are declared: the contour texture's data URI, which cannot carry
a `var()`, and the `#000` stops in the scroll edge's mask, which are opacity and not ink.

## 2. Typography roles, with placement rules

| Role | Face | Where it is allowed |
|---|---|---|
| Display | Avenir Next Demi Bold, 44/1.05, −0.02em | The page's one `h1`. Nowhere else. |
| Heading | Avenir Next Demi Bold, 24/1.2 | Section headings, sitting on a hairline with the section's key figure at the rule's trailing end. |
| Label | Avenir Next Medium, 11/1.2, 0.14em, uppercase | Table column heads, field labels inside the planner. Never above a heading — this page has no kicker. |
| Body | Avenir Next Regular, 15.5/1.65, measure ≤ 68ch | Bulletin copy and permit steps. |
| Data | Menlo, 13–15px | Every figure: miles, feet, times, dates, quotas, freezing level. Never prose. |
| Hydrography | Avenir Next Italic, in `--water` | Water-feature names in the conditions bulletin only. |

The eyebrow appears exactly once on the page — `North Cascades National Park · Washington`, above
the `h1`. A second one anywhere is a defect.

## 3. Canvas, texture and material

The ground is `--paper`, carrying one texture at the root of the sheet and nowhere else: a contour
hairline field at 6% brown-plate ink, painted as a repeating SVG background on the sheet itself so
it is genuinely *behind* the glass and gets refracted. No grain per section, no texture on any
component.

Material model, both halves, per `references/material.md`:

- **glass over planes** — the floating layer only. Three surfaces, listed in §4.
- **printed** — every surface beneath. Checkable: `box-shadow` appears exactly zero times in the
  stylesheet;
  no element beneath the floating layer has a radius above 2px; sections are separated by hairlines
  and whitespace; there is no card.

## 4. Layout system

### The six composition lines

1. **Posture — narrative.** The park's public trails page, read once in the order the park wrote it:
   the place, the trip, the trails, the conditions, the permit. Nobody works out of it for a shift,
   and it is not one bounded form.
2. **Dominant activity — compare.** The first read after the place is *which of these twelve can I
   walk this weekend*, and the success condition is one trail chosen with its distance, its gain,
   its high point against today's snow line, and its permit known. Compare's rule fires: the twelve
   share one axis in one region.
3. **Unit and relation — the trail; matrix.** The unit is the brief's own noun. The relation the
   first read acts on is a matrix: trail against distance, gain, high point, profile, condition,
   permit. A spatial field is present as the page's ground, but nothing is acted on there.
4. **Co-visibility — none.** Nothing in the brief asks for two trails to be readable at once, and
   the profile column gives every trail its evidence in the row. Recorded as decided, not unknown.
5. **Temporal — live.** Conditions change under the reader: snow line, fords, a fire closure, the
   quota for a chosen date. Every changing region carries a freshness mark with its source.
6. **Volume and homogeneity — many homogeneous** (twelve trails, one schema) **plus few
   heterogeneous** (bulletin, permit sequence), each with its own topology.

### Compiled consequences

- **Dominance** — one dominant band in the first viewport: the photograph, with the page's name and
  the day's reading over its lower third. The matrix is the dominant content region below it.
- **Reading order** — planner (chrome) · the place · the twelve trails · the conditions · the
  permit · credits. The declared first-read content region, `#trails`, is the first section of the
  sheet and reaches the sheet's leading margin.
- **Columns and ratio** — no split. The matrix is one full-measure region; the bulletin runs as a
  two-column definition list (term 232px, description 1fr — 1 : 4.1, clear of the forbidden band); the permit steps are one ordered column at the reading measure.
- **Where density lives** — the table. The hero band, the bulletin and the permit sequence are
  spacious.
- **What repeats** — twelve trail rows, four forecast days, four permit steps. Nothing else.
- **Chrome** — conventional: identity and the trip controls at the top of the window, credits and
  park information in the footer.

### The ledger

| Brief evidence | Interpreted relationship | Layout constraint | Rendered assertion | Forbidden move |
|---|---|---|---|---|
| "twelve trails with distance, elevation and current conditions" | Twelve peers compared on one schema | One real `<table>`, both axes labelled, sticky head clear of the bar | Twelve `<tr>` in one `<tbody>`, seven `<th scope=col>`, head sticky at 132px | A card per trail |
| "a full-bleed relief map or panoramic photograph fills the window" | The park is the ground, not an illustration | A fixed, full-bleed photograph behind everything | `.plane` is `position:fixed;inset:0` and the sheet scrolls over it | A photo cropped into a hero box |
| "a floating trip planner over it" | Trip parameters held while the comparison is made | The planner is glass, viewport-fixed, and the only chrome | Two glass surfaces in the base plane, at the window's top | The planner as a section of the page |
| "the trail list … extend beneath the floating bar" | Content slides under the chrome | The sheet reaches the window's edges and passes under the bar, with a scroll edge | The sheet's mask fades content across the bar's own footprint | A bar sitting beside content in its own band |
| "current conditions" | A dated reading with a source | A freshness mark per changing region | Three regions carry `Read 09:40, Thu 10 Sept 2026 — WIC Marblemount` or their own dated line | A live badge with nothing behind it |
| "permits" | An ordered process with real dates | A numbered sequence, ordering key first | Four `<li>` with the date first in each row | A pricing-style trio of permit cards |

### Candidates

**Chosen — A, the sheet under the bar.** The photograph is fixed and full-bleed; the sheet rises
over it, carrying the matrix, the bulletin and the permit sequence; the glass bar is fixed at the
top and everything passes beneath it.

Rejected in one line each:

- **B, the plane as a left pane** — photograph fixed at 55%, content scrolling at 45%. Rejected:
  the bar would then sit *beside* content in its own band, which is the desktop failure
  `references/liquid-glass.md` §8 names, and the split lands near the forbidden band.
- **C, list beside detail** — the matrix on the left, the selected trail's profile and notes in a
  permanent pane on the right. Rejected: co-visibility is *none*; the pane is empty until something
  is selected and it costs the comparison a third of its width, while the profile column already
  gives every row its evidence.

**Priors adopted.** *Full-bleed image*, earned by the narrative posture and by the park being the
subject rather than an illustration of it — its invariant honoured by testing the hero copy against
the photograph's lightest region. *Table-led*, earned by compare × matrix × many homogeneous — a
real table with a sticky head, scrolling horizontally inside its own container below 900px rather
than reflowing.

**Defaults overridden, by name.** The trail **card grid** (the park-website reflex; displaced by the
compare line). The **three-up** of features under the hero (absent). The **stat row** (absent — the
day's figures are in the planner, where they are the trip's parameters). The **headline band with an
empty right half** (the first viewport is a photograph). The **sidebar** (no six peer destinations,
no drill model). The **hero-photo-with-search-box** (the planner is not a search).

### The plane split, and the floating-layer inventory

Two planes, as the runtime has, and three surfaces on them — a list short enough to read aloud, each
load-bearing:

1. **base · the trip planner platter** — route, date, party, and the three readouts the choice is
   made against: the route's distance and gain, the day's temperature, the freezing level.
2. **base · the permit action capsule** — the page's one primary action and its one tinted surface.
3. **overlay · the permit platter** — the transient answer to that action: zone, night, sites open,
   walk-up desk. It is registered when it opens and released when it closes, so a closed platter
   draws nothing, and it carries `role="dialog"` with its own name because a plane's DOM sits
   outside every landmark the page wrote.

Everything else stays opaque and printed: the sheet, the matrix, the bulletin, the permit sequence,
the footer. Nothing else is ever promoted between planes.

### The group plan

Three groups, one per surface, each declaring the backdrop it actually has — measured off the
plane's own pixels under that surface's box in the crop the page renders, at both phases, not
guessed. The field is `backdrop:`, not `hint:`; `hint:` is silently ignored on the vanilla path and
would leave every group at `analysis: "none"`.

| Group | Surface | At rest | Scrolled | Declared |
|---|---|---|---|---|
| `bar` | planner platter | 0.84, the cloud band | 0.878, paper | `{ tone: "light", luminance: 0.86, complexity: 0.55 }` |
| `action` | permit capsule | 0.138, the dark ridge | 0.878, paper | `{ tone: "mixed", luminance: 0.50, complexity: 0.60 }` |
| `permit` | permit platter | 0.106, the ridge | 0.878, paper | `{ tone: "mixed", luminance: 0.49, complexity: 0.55 }` |

The capsule is its own group rather than the platter's because its backdrop is a different fact and
a shared `light` declaration would be a lie at first paint; that split is only legal because the
290px between them is far past either group's effective sampling padding. Two adjacent bar items
would have had to share one group instead. No group declares `samplingPadding` or `mergeDistance`:
the runtime derives 3σ of the blur it resolved, and that follows reduced transparency by itself.

### The size family

Three sizes, one radius per size, one thickness of 8 across all three — the reference's method, not
its numbers.

| Surface | Span (short side) | Shape | Radius | Concentric children |
|---|---|---|---|---|
| Action capsule | 48 | capsule | height / 2 = 24 | none |
| Planner capsule (desktop) | 80 | capsule | height / 2 = 40 | fields are capsules inside the rounded ends |
| Planner platter (phone) | 106 | fixed rounded rect | 22 | fields retain radius 12 |
| Permit platter | 344 (424 × 344) | fixed rounded rect | 32 | rows at 32 − 12 = 20 |

48 sits just past the size law's floor of 32, 80 mid-curve, 344 well past its ceiling of 96, so the
family straddles the band the law actually acts on. The platter's box is its content's: 424 wide is
where the longest zone line sets on one line for every route (the widest measures 380 in a 380 box),
344 tall is the content's own 341 rounded to the spacing step. The concentricity anchor is named: the **window
edge**, radius 0, which is why the leading surface aligns to the page's own 40px margin rather than
taking extra inset, and why every radius on the page is declared by its own surface rather than
inherited from a frame that does not exist.

### The backdrop design

The glass sits over two things in turn, and both were designed to have two spatial frequencies.

- **At rest** — the photograph's ridge band: rock, snow and trees across the window's top, chosen
  for texture rather than for sky, because glass over a uniform field renders as an invisible
  outline.
- **Scrolled** — the sheet, whose contour hairline field and the matrix's own rules supply the fine
  frequency, and whose paper supplies the broad one. The contour field is painted *into* the sheet's
  background, not laid over it, so the lens actually bends it.
- **Between them** — the scroll edge: a mask on the sheet fading its content across the bar's own
  footprint, so the photograph reappears through the dissolving paper instead of a hard line
  arriving under the glass. The hard desktop style, built by hand because the web has no primitive,
  and on the sheet — never on an ancestor of the glass root, which would re-root the backdrop and
  demote every group with `probe-failed`. The matrix's column heads pin at 132px, clear of the fade
  band's end at 128, so they never arrive at the glass half-erased.

### Imagery ladder

| Slot | Rung | Why not the rung above |
|---|---|---|
| The live plane — the park panorama | **Unsplash** (rung 2). Diablo Lake from the North Cascades Highway overlook, by Pete Alexopoulos; downloaded same-origin into `images/`, credited by name in the footer. | The project's own assets (rung 1) are calibration fixtures only — `find-image.mjs inventory` finds no brand photography. |
| Twelve elevation profiles | drawn as content | An artifact, not a world: the profile is this page's own measurement, so it is SVG at one shared scale, per `references/composition.md`. |
| Status and wayfinding glyphs | drawn as content | Three shapes at 8px; an icon set would be a second drawing language. |

### Mechanics

The desktop web has no safe area, so the page owes that guarantee by hand: `--bar-bottom` is the
bar's *measured* bottom edge, written at boot, after the fonts settle and on every resize, and both
the scroll edge's stops and the matrix's sticky-head offset are `calc()` off it. No inset on this
page is a constant typed once. The frame loop writes exactly one property, `--scroll-y`.

Sheet measure 1180px, page margin 40px, spacing scale 4 · 8 · 12 · 20 · 32 · 56 · 96. Sections are
separated by a hairline and 56px, never by a card or a shadow. The collapse is staged, and it is a
reordering rather than a compression: the planner sheds its readouts one at a time from 1240px down
as the window takes them (they reappear as one line in the hero), at 900px the matrix becomes its
own horizontal scroller rather than reflowing and its heads go static, and at 748px and below the planner
wraps to two rows and the action capsule is released as a glass surface, returning as a filled
button inside it — one glass surface on a phone, which is the honest inventory at that width.

## 5. Component canon

`.pick` — the one selection mark, a `▶` that reserves its space and fades in.
`.status` — the one status chip: glyph, word, and a note. `.figure` — the one numeric treatment,
Menlo with a unit in `--ink-3`. `.profile` — the one elevation glyph, 132 × 40, shared 0–8,000 ft
scale, brown-plate line, red-plate dashed snow line. `.rule-head` — the one section heading, a
hairline with the heading at the leading end and a figure at the trailing end. `.field` — the one
control inside the planner. No card component exists and none is to be added.

## 6. Voice

The park speaking to somebody who has to make a decision: plain, dated, sourced. Sentence case
everywhere except the label role. Figures always carry their unit and, where they are a reading,
their time and who read it. No exclamation, no adjectives about scenery, no "discover", no
"adventure". Empty and error states name what is unavailable and what to do instead.

## 7. Motion

Glass materialises and morphs; it never cross-fades. The permit platter emerges from the capsule
that opened it, and it materialises by resolving *into* rest: the lens channel runs 1 → 0 with a
0.94 → 1 owned scale over roughly 280ms, because a channel parked at 1 leaves a standing band on
the surface. It is registered on open and released on close, so a closed platter draws nothing. Press feedback is the runtime's own glow at the pointer (`--vitrea-press`, `--vitrea-press-x/y`),
never a colour swap. The sheet has no reveal-on-scroll animation of any kind. Under
`prefers-reduced-motion` the platter appears at its final geometry and every transition is 0ms.

## 8. Hard don'ts

1. No card. No `box-shadow` anywhere in the stylesheet, including on the glass, which carries its
   own occlusion.
2. No glass outside the three declared surfaces, and no `backdrop-filter` written by hand anywhere.
3. No glass on a row, a table, a list or prose; no glass inside glass; no background colour on a
   glass host.
4. No second accent, no gradient, no colour literal outside `:root` (except the declared glyph
   exception), no hue on a control label.
5. No `filter`, `opacity < 1`, `mask-image`, `clip-path` or `mix-blend-mode` on any ancestor of the
   glass root's container.
6. No reveal-on-scroll, no parallax, no idle motion, no shimmer.
7. No lorem ipsum, no invented figure without a source line, no "photographs via Unsplash" without
   the photographer's name.
8. No text over the photograph outside the hero band, and none anywhere the scrim was not tested.
9. No coloured side stripe on a row, card or callout; no gradient text; no em dash used as
   punctuation in page copy (a range keeps its en dash).

## 9. The glass record

```
path: vitrea 0.14.0, @vitreajs/vitrea-web through the workspace import map. One HTML file plus a
  served repository; needs http://localhost, since a module page does not load over file:// at all.
renderer: createGlassRoot({ renderer: "webgpu", devMode: true, colorScheme: "light" }).
  `?tier=css` opens the same page at the CSS tier, because that tier is a state of this design and
  has to be openable to be checked; it resolves cssBody "two-layer", health "ok".
sampling: DOM proxy (css-backdrop), deliberately — see the note below.
scheme: one, light. The sheet is printed once; `color-scheme: light` is set on :root and on every
  host, because the plane root carries `light dark` and app content inside a plane otherwise takes
  the reader's system ink.
accessibility: reducedTransparency, increasedContrast and reducedMotion all declared "system" at the
  root, because prefers-reduced-transparency is not Baseline and a silent false is the failure mode.
  Under forced colours there is no glass; what remains is the sheet, which is the whole interface.
contrast: labels get their own foreground on a child element, never on the host, whose background
  the CSS tier rewrites every frame. Measured on rendered pixels, both phases. Recorded below.
```

**The sampling decision, and its cost.** The photograph is *not* registered as a texture source. A
texture group samples the registered pixels over the whole viewport regardless of what is actually
beneath the surface, and this page's whole composition is content sliding under the bar: once the
sheet covers the window, a texture-backed bar would refract mountain pixels over paper and claim to
show what is behind it when it does not. So all three groups sample the DOM. The cost is stated
rather than hidden: `refraction: "approximate"` — the shader's rim lensing over a CSS proxy —
instead of `"true"`, and `analysis: "hint"` instead of `"exact"`. The page keeps the WebGPU tier and
loses true refraction; it keeps honesty, which is the material's own doctrine.

**Measured, on rendered pixels.** Captured in Chromium at 1440 × 900 on the WebGPU tier and read
off the capture, in both phases. Backdrop before the material: photograph's cloud band 0.85, dark
ridge 0.14 / 0.11, paper 0.878. Glass as drawn, and the ratio of the ink actually set on it:

| Surface | Phase | Glass luminance | Smallest label on it |
|---|---|---|---|
| Planner platter | over the photograph | 0.854 – 0.947 | `--ink-2` at 10px, **6.3 : 1** |
| Planner platter | over the sheet | 0.870 – 0.937 | `--ink-2` at 10px, **6.4 : 1** |
| Action capsule | over the photograph | 0.373 – 0.421 | `--ink` at 15px, **6.4 : 1** |
| Action capsule | over the sheet | 0.456 – 0.494 | `--ink` at 15px, **7.6 : 1** |
| Permit platter | over the photograph | 0.396 – 0.592 | `--ink` at 13px, **6.7 : 1** |

The permit platter's labels are the reason nothing on it is set in `--ink-2`: measured over the
photograph's dark ridge, `--ink-2` came back at 3.1 – 4.2 : 1 and was replaced with full ink, with
the key/value hierarchy carried by the type roles instead. The audit's own DOM-composite pass reads
28 / 28 and 12 / 12 on glass; it cannot see what a canvas drew, which is why the table above exists.

**One renderer defect, found here and fixed upstream.** Building this page surfaced a real bug: on
either sampling backend the outer shadow's falloff fed `tanh` an argument that overflows to NaN on
Metal past roughly 153 px of depth, which drew a hard bright band across a large surface's own
centre. It showed up as a threshold near 306 px of platter height — swept at 288 / 296 / 300 / 304 /
308 / 312 / 320 / 330 / 340 and scanned in the capture, absent at and below 304, growing with the
box, absent on the CSS tier and independent of the lens channel and of any owned transform. The
clamp landed in the workspace build (`c62c19c`), so the constraint is gone: the platter's size is
derived from its content again, and its interior was re-scanned and re-read at 424 × 344 with the
band at zero. Kept here because the sweep is how a page-level symptom became a one-line renderer
fix, and the next page that sees a band on a large surface should recognise it.

**Channels return to rest.** `--vitrea-lens` and `--vitrea-press` are 0 at rest by construction; a
channel parked at 1 leaves the surface permanently lensed, which is the standing bright band 0.11.0
removed. The platter materialises by resolving *into* rest — lens 1 → 0 with a 0.94 → 1 owned scale
— and the capsule's press channel eases back to 0 on release.

## User-directed capsule follow-up — 2026-09-10

The user preferred actively rounded capsules to rectangular floating controls. The one-row
80px planner now takes a 40px radius with 16px end padding and capsule-shaped fields. The
106px two-row phone planner retains its 22px platter radius and compact field geometry; the
permit platter, action capsule, layout, imagery and material are unchanged. This is the user’s
visual refinement, not a new Apple requirement. Frozen baseline PNGs and audit.json remain
untouched; new verification belongs in `figma-design-workspace/capsule-followup/park-trails/`.

Verification also exposed a separate lifecycle bug: after returning from phone to desktop,
the permit action discarded its replacement host handle. The follow-up retains that handle
so subsequent responsive transitions release the current surface rather than an already
released node. This changes no interaction or visual intent.

## Responsive capsule regression fix — 2026-09-10

The 16px capsule ends exposed an 11.58px planner/action overlap at 721px. The shared CSS
and host-lifecycle breakpoint now collapses at 748px, before the collision: the first
single-row width, 749px, retains just over 16px between the planner and the action.
The two-row phone platter and inline action are unchanged; repeated crossings release
and replace the current planner/action handles rather than accumulating surfaces.

Verified in real Chromium with `node docs/research/scripts/capsule-responsive-regression.mjs`:
123 layout states across all three demos, including 721/732px, 350px, 1023/1024px and
three repeated round trips per demo. The assertions read actual runtime shape/radius
registrations as well as DOM bounds. Before/after captures live only under
`figma-design-workspace/capsule-responsive-fix/`; frozen captures and audits are untouched.
