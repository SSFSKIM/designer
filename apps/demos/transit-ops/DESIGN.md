# Ashport Transit Authority — Network Control

Design law for `apps/demos/transit-ops/index.html`. The product is the desktop operations map the
duty controller works out of in the control room at Dockside depot: the city, forty vehicles on
eight corridors, and the six things that need an instruction now.

---

## 0. Stance commitment

A near-white city under a monochrome control layer, interrupted by one thing only: forty running
blades whose colour is the service they are running. The system is **not** a dashboard of the
network — there is no headline number, no stat row, no chart. It is the network, with the
instruments floating over it. *If a decision is ever ambiguous, choose the more legible option.*

**Axis position**

- **Density: dense** (constraint) — one controller holds this for a whole shift and scans forty
  vehicles and six alerts; the verb is monitor, then operate on the exception.
- **Criticality: consequential** (constraint) — a hold, a short-turn or a relief instruction moves
  a bus carrying passengers, and each one is logged against a block.
- **Energy: quiet** — eight hours under a radio; nothing may ask for attention it has not earned.
- **Type: neutral sans plus a mono for data.** Tradition: legibility-engineered humanist sans.
  Criteria: unmistakable 0/O and 1/l/I at 12 px over a moving plane, high x-height, tabular lining
  figures; a mono with true tabular figures for clock times and adherence deltas.
- **Material model: glass over planes** — the city changes under the controls continuously and the
  controls must not cover the network they command. The surfaces *underneath* the glass — alert
  rows, the platter's inner content, the camera plate — are **tonal**: one lightness step and a
  hairline, no shadow at rest.
- **Color commitment: restrained** — chromatic surface stays under 10%. The only hue on the page is
  the five-state service ladder on the blades, and the harbour and two parks in the ground.
- **Accent job: none** — the floating layer is monochrome; interaction is carried by fill, weight,
  a hairline and a two-tone focus ring. The plane already spends the page's colour on service
  state, and Liquid Glass puts saturated colour in the content layer.
- **Ground lightness: light.** Scene: *07:10, the duty controller at Dockside depot, blinds half
  down on a grey harbour morning, this map on the left screen and the radio log on the right, a
  paper running board on the desk.*
- **Ground temperature: neutral** — every neutral at hue 250, C ≤ 0.008. The land must argue with
  nothing.

**Rejected coordinate vector.** quiet · **mono-as-display** · glass over planes · restrained ·
**status-only** accent · **dark** · **cool** — the sampler's `terminal` draw. Lost because a
control-room map is a picture before it is a readout: mono-as-display at 12 px over a moving plane
costs legibility a consequential surface cannot spend, and a dark basemap compresses amber against
red at the top of the state ladder. What survived from the sampler is `topographic` — the
graticule, the grid references, and annotation typography.

**Derivation.**

- *Accent.* Weighed and rejected: **signal yellow**, the network's own stop-flag and blind colour,
  a real product-world candidate. It lost because the plane already needs amber for "late" and a
  yellow control would be read as a warning by a controller trained on that amber. Also explicitly
  refused: a violet or an oxide orange picked as "the hue the status set has not spent" — that is
  the leftover-accent reflex `taste-calibration.md` names, and elimination is not a source.
- *Ground.* Weighed and rejected: a **dark basemap**, the reflex answer for a glass page and for a
  control room. It lost on the state ladder: five states must be separable by lightness as well as
  hue, and a dark ground pushes amber, red and blue into one narrow band at the light end. Neutral
  at near-zero chroma is what lets the ladder keep its spread.
- *Type.* Derived from the criteria, not from a pairing: this is a public agency's safety-relevant
  desk where fleet numbers, block numbers and route numbers are most of the text, so the UI face is
  the one cut that exists to disambiguate 0/O, 1/l/I and 5/S — **Atkinson Hyperlegible Next**. Data
  takes **Geist Mono** for true tabular figures. Two families, which is what dense allows.
  `Barlow / Barlow Condensed / IBM Plex Mono` is the transit-and-industrial pairing the reference
  library proposes; it was declined as the category's own reflex.

**Signature element.** The **running blade** — a vehicle marker built like a destination blind:
route number in ink on a plate tinted by service state, ruled by the state at full strength, with
an adherence notch above or below the number so state is never hue alone. Forty of them are the
page.

**Clone test.** Another all-shift operations console lands at dense × consequential × quiet, and
that is the brief read correctly. What may not repeat: the zero-chroma land, the state ladder spread
by lightness as well as hue, an accent job of `none`, and the blade.

---

## 1. Palette, with usage rules

The token file is `:root` in `index.html`. Roles:

- `--n0 … --n9` — one neutral ramp at hue 250, C ≤ 0.008, carrying ground, map ink, controls and
  text. `--n9` is ink; `--n7` is muted ink; `--n0` is the street fill and the reversed label.
- `--water`, `--water-edge`, `--green` — the ground's only chroma, and only in the painted plane.
  Never on a control.
- `--st-*-fill` / `--st-*-line` — the five service states (early, on time, late, very late, no
  signal). **This is the only sanctioned literal-colour set on the page.** It appears on the blade,
  on the alert row's state square, on the state rack's dots and on the platter's leading blade. It
  never carries an action, a link, a selection or a focus ring.
- `--map-*` — the plane's own roles (land, density, casing, street, arterial, ink, halo, shield,
  corridor, graticule, rail), each aliasing a ramp step. They exist so the night map is a derived
  surface system and not an inversion: in daylight the streets are cut light out of a darker land, at
  night they are drawn light over a darker one, and both read as a basemap.
- There is **no accent token.** Selection is `--n9` fill with `--n0` label; focus is a 2 px `--n9`
  ring inside a 1 px `--n0` ring, so it survives both the glass and the map behind it.

Forbidden: a second hue family in the neutrals; a state colour on a control's background; any hex,
`rgb()` or `oklch()` literal outside the `:root` block, including inside canvas paint code, which
reads its colours back out of the same custom properties. **One documented exception**: each
photograph's own average colour, carried on its container so the layout holds while the image loads.
That value belongs to the photograph, not to this system.

---

## 2. Typography roles, with placement rules

- `--font-ui` (Atkinson Hyperlegible Next) — every control label, alert title and alert body, the
  route number on the blade and on a shield, and the map's district and street annotations.
- `--font-mono` (Geist Mono) — clock times, adherence deltas (`+6:20`), fleet and block numbers,
  headway readings, camera identifiers, and the map's grid references. Nowhere else: a mono
  paragraph is not this system.

Sizes come from `--t-*`; no component sets a raw `font-size`. Uppercase exists only as
`text-transform` on `--t-label` (11 px / 700 / 0.08em) and on the map's district annotation; the
underlying string is always sentence case. Alert bodies are 12.5 px at 1.45 and are written to two
lines at 336 px, so nothing on this page is ever truncated: the copy is a layout constraint here, not
an overflow to solve.

---

## 3. Canvas, texture & material

**The live plane.** `<canvas id="map">`, `position: fixed; inset: 0`, repainted every frame with the
harbour and river, two parks, a three-plateau built-density wash, the street web, the eight bus
corridors, a 32 px graticule with 128 px majors and their grid references, the district and street
annotations, the route shields and the forty blades. It is registered as backdrop source `city`
(`kind: "texture"`, probe clean and compatible) and supplied as `{ kind: "canvas" }`, so every group
reads real pixels — `analysis: "exact"` — and **no group declares a hint**.

Both spatial frequencies are painted *into* the texture, never laid over it in CSS: low frequency is
the water, the parks and the density wash; high frequency is the graticule, the street web at 1 px
and the corridor casings.

**Material model: glass over planes.** Variant **regular**, on every surface; `clear` is never used.
**Zero tinted controls** — the accent job is `none`, so the one tint the language permits is spent
nowhere. No `background` on a glass host. No glass on any row, list, table or prose. The plane split,
the floating-layer inventory, the group plan and the size family are composition decisions and are
recorded in **§4**, before the six composition lines, because they constrain layout rather than
style.

**Tier expectation**: `webgpu` on Chromium over `https` or `localhost`; `css` elsewhere. A module
page does not load over `file://` at all, so there is no tier there. Reduced transparency, increased
contrast and reduced motion are all passed as `"system"` at the root so the runtime reports honestly
where a query cannot be answered; forced colours removes the glass and the page stays a working
interface on its own borders.

---

## 4. Layout system

### The Liquid Glass composition, decided before the layout

`liquid-glass.md` §1 runs before the composition lines, because every decision in it constrains
where things can go rather than how they look.

**The live plane** is the painted city (§3): the canvas fills the window and every floating surface
is over it, never beside it.

**The backdrop, designed.** The plane carries both spatial frequencies *inside the texture* — the
harbour, the canal, the reservoir, three parks and a four-plateau density wash for the lens to bend;
a 32 px graticule, the street web at 1 px and the corridor casings for it to displace. Nothing is
laid over the canvas in CSS, because anything laid over it would not be behind the glass. Every
surface was placed against that: the toolbar sits over Kelvin Reservoir and the Kelvin Cut rather
than over the empty north-west quarter, which is why the canal exists at all.

**The plane split.** Five surfaces on `base`; the vehicle platter alone on `overlay`, because it is
the one transient thing and because a platter anchored to a moving blade must be free to cross the
bar and the sidebar. Nothing is portalled, so no landmark is lost.

**The floating-layer inventory** — six surfaces, six groups, one per surface because each reads a
different part of the plane, and read aloud it is: two filter racks, a search field, a view stack, an
alerts sidebar, and a platter that is absent until a vehicle is selected. Everything else on the page
is opaque.

| # | Surface | Plane | Group | Box at 1440 × 900 | Job |
|---|---|---|---|---|---|
| 1 | Route rack | base | `routes` | 20, 20, 332 × 44 | multi-select filter over the eight corridors |
| 2 | State rack | base | `state` | 400, 20, 340 × 44 | all, plus four service-state toggles |
| 3 | Search field | base | `find` | 788, 20, 200 × 44 | fleet / block / stop lookup, at the bar's trailing edge |
| 4 | View stack | base | `view` | 20, 680, 44 × 140 | zoom in, zoom out, fit network |
| 5 | Alerts sidebar | base | `alerts` | 1084, 20, 336 × 860 | the six active alerts, co-visible with the map |
| 6 | Vehicle platter | **overlay** | `platter` | 460 × 64, anchored | the selected vehicle; **no box at all** at rest |

Everything else is opaque and tonal. No group declares `samplingPadding` or `mergeDistance`; the
runtime derives 3σ of the blur it actually drew, and it resolved **11.9 px** for the four bar-rung
groups, **14 px** for the platter and **28.4 px** for the sidebar. Base-plane groups sit at least
**48 px** apart and nothing sits within **96 px** of the sidebar. A closed platter is
`display: none`, not `visibility: hidden`: a hidden-but-laid-out host still has a box and the
renderer still draws its glass, which is how the first build shipped a 420 × 64 white plate over the
top-left corner of the map.

**Size family** — three rungs, one radius each, one thickness of **8** across all of them:

- **s — span 44, radius 14**: route rack, state rack, search field, view stack. Twelve px past the
  size law's inert floor of 32.
- **m — span 64, radius 18**: the vehicle platter. Mid-curve, at 64 of the law's 32 → 96 ramp.
- **l — span 336, radius 26**: the alerts sidebar. Past the saturation point of 96.

Every floating shape is a **fixed** rounded rectangle: `liquid-glass.md` §8's macOS reading keeps
compact desktop controls rectangular and reserves capsules for large standout actions, and this page
has none. The one capsule-shaped thing on it, the alert row's fleet chip, is content, not a control.

**Concentricity anchor**: the 20 px window inset against a square viewport edge, so every floating
radius is fixed rather than derived from a rounded frame. Four shapes *are* concentric, each
derived from its container's radius less its own inset: the rack segment (14 − 5 = 9), the view
stack's buttons (14 − 4 = 10), the sidebar's alert row (26 − 10 = 16) and the platter's actions
(18 − 12 = 6). The camera plate and the fleet chips take a fixed radius and are recorded as fixed:
they sit inside a container but not at its corners.

**Scroll edge**: exactly one, **hard** style — the desktop default — under the sidebar's header,
appearing only once the list has actually scrolled under it. A hairline rather than a gradient mask,
which also keeps every `mask-image` off the page: on an ancestor of the plane root one would re-root
the backdrop and demote the group. The map pans; it does not scroll, and it gets none.

**Safe area, by hand**: the painter is given the measured rectangle of every floating surface and
suppresses its own annotations and shields inside them, inflated by 12 px, recomputed whenever a box
changes. That is this page's answer to the safe-area inset the desktop web does not have, and to the
rule that content must not sit under a glass control at rest.

### The six composition lines

1. **Posture: workspace** — held open for a whole shift and worked out of.
2. **Dominant activity: monitor** — the first read answers "which vehicles and which routes need an
   instruction now"; success is every exception actioned or acknowledged.
3. **Unit and relation** — the unit is the **vehicle**, the brief's own noun; the relation the first
   read acts on is a **spatial field**, because a vehicle's meaning is its position on its corridor
   relative to the one in front of it.
4. **Co-visibility: peer panes** for the alert list, which must stay readable while the map is
   worked, plus **on demand** for the vehicle platter.
5. **Temporal: live** — positions and adherence update continuously, "now" is marked in the bar, and
   regions hold position across updates.
6. **Volume and homogeneity** — **many homogeneous** for the forty vehicles on one schema;
   **few heterogeneous** for the six alerts, which have six different causes.

**Compiled consequences.** Dominance: one dominant — the map, by line 3, holding 100% of the first
viewport with the instruments floating over it. Reading order: the plane first in DOM order and
top-left, then the alerts, then the toolbar. Columns and ratio: **none** — the sidebar is an overlay
at 336 of 1440, not a track, so the page has no grid-track ratio to fingerprint. Density lives in
the plane and the alert list, never in the toolbar. What repeats: the blade × 40 and the alert row
× 6, and nothing else. Chrome conventional: search at the toolbar's trailing edge, filters leading,
the alert list in a floating inset sidebar on the right — the macOS 26 reading.

**Ledger.**

| Brief evidence | Interpreted relationship | Layout constraint | Rendered assertion | Forbidden move |
|---|---|---|---|---|
| "a city map fills the window" | the network is the artifact; the controls command it | the plane is `inset: 0`, painted before any chrome | the canvas is the first element in `<body>` and covers the viewport with no chrome band beside it | a map card inside a dashboard shell |
| "live vehicle positions on their routes" | forty units of one schema on a spatial field | one marker type, one schema, position stable across ticks | every blade carries route number, state fill and adherence notch; a tick never moves the selected blade out from under the pointer | a vehicle table beside the map |
| "a route-and-status filter toolbar" | two independent filters over one field | two controls, two groups, one bar | the route rack and the state rack are separate glass surfaces at least one sampling padding apart | eight coloured chips carrying a route palette into the control layer |
| "a sidebar lists the active alerts" | an exception set held co-visible with the field | a floating inset sidebar with its own scroll and its own scroll edge | the map is drawn beneath the sidebar to the window edge, and the list scrolls under a hard edge | a sidebar in its own opaque band beside the map |
| "a selected-vehicle platter" | detail on demand, emerging from the marker | an overlay-plane surface anchored to the selected blade | the platter is absent at rest and materialises at the blade it opened from | a permanent inspector pane, empty until something is selected |
| "forty vehicles… six alerts" | many homogeneous against few heterogeneous | one repeated blade; six titled rows with distinct causes | the alert list is six rows, no two sharing a cause, and is not a card grid | a stat row of network totals above the alerts |

**Chosen candidate: A — floating chrome over a full-window plane.** Map at inset 0; the bar floating
top-left; the alerts sidebar floating inset right; the platter on the overlay plane at the selected
blade.

**Rejected candidates.** *B — map plus a docked right rail and a bar above it*: it puts the bar
beside the content in its own band, which is the single most visible way a page fails to read as
this language, and it costs the map a quarter of the window it is the product of. *C —
exception-first, the alert queue leading top-left with the map subordinate below*: the
`exception-first` prior is genuinely earned by workspace × monitor × live, but line 3 is a spatial
field and an alert here is only actionable by seeing where the bus is; splitting them puts the
evidence one region away from the decision.

**Prior adopted: map-led / canvas-plus-palette**, earned by line 3. Its invariants hold — the field
holds the whole first viewport, the panels are subordinate, and they cross-highlight in both
directions: selecting an alert flies the map to it and selects its vehicle; selecting a blade opens
the platter and lifts the matching alert.

**Defaults overridden by name.** No stat row — nobody monitors this network by a headline number.
No persistent left sidebar — there are no peer destinations and no drill model, and "console" earns
nothing. No main-plus-rail grid — the rail is an overlay, not a track. No three-up. No near-equal
split, because there is no split.

**Mechanics.** Window inset 20 px. Bar row at y 20, height 44. Sidebar x 1084 → 1420, y 20 → 880.
View stack bottom-left, above the scale bar and the credit line. Spacing scale
4 / 8 / 12 / 16 / 20 / 24 / 32 / 48. Sections inside the sidebar are separated by a hairline at
`--n9 / 12%`, never by a card. Tab order follows the declared reading order — the floating controls,
then the page's own content — which the build gets by moving its trailing elements after the plane
root vitrea appends to the body.

**Responsive collapse.** Both breakpoints sit where the *group gaps* stop fitting, not at a round
number, because a bar that merely squeezes makes one group's padded proxy sample the pixels its
neighbour paints and the runtime reports it. The single-row bar needs
20 + 332 + 48 + 340 + 48 + 200 + 56 + 336 + 20 = **1400 px**; the two-row bar beside a sidebar needs
**1024**.

- **≤ 1399**: search leaves the bar's trailing edge — that is where the sidebar now is — for a second
  row at the leading edge, 32 px below the first, which is past both the sampling padding and the
  merge distance. The sidebar narrows to 300 and anchors to the right edge.
- **≤ 1023**: an intentional collapse, three things at once. The alert list leaves the right edge for
  a bottom sheet of horizontally scrolling cards, so the map keeps its full width and the controller
  still sees the whole network. The state filter drops from five service states to the one decision a
  small screen actually makes — all against **Exceptions**, which is late, 10+ late and no signal
  together. The view stack turns horizontal above the sheet, and the page's credit line, which the
  map's own attribution carries at desktop widths, rides with the sheet instead.

**Imagery.** Two photo slots, both **rung 2, Unsplash** (`find-image.mjs search` → `pick`, credits
on the page). Rung 1 did not answer: the project has no image assets (`inventory` returns 0). The
slot is an on-street camera still shown on the expanded alert, 304 × 171 at `object-fit: cover`,
intrinsic size declared, container pre-filled with the photo's own average colour, treated with the
cool technical tone match (`saturate(0.76) contrast(1.05)`, and one stop darker at night) so two
photographers read as one camera estate. Only the two location incidents carry one; a headway gap, a
ramp fault and an overdue relief have no camera by nature, which is why the other four rows carry a
sentence saying so rather than an empty picture frame. A third slot was searched and abandoned: the
Unsplash candidate was monochrome with embedded signage against two colour frames, and the Openverse
fall-through returned snapshots that would have read as a different production standard. The live
plane itself is **rung 4, drawn** — a map is an artifact, so it is painted as content on the canvas.

---

## 5. Component canon

- **Running blade** — the vehicle marker. 28 × 20, radius 5, state fill, 1.5 px state rule, route
  number in `--n9`, adherence notch above (early), below (late), doubled below (very late), absent
  (on time), hollow centre (no signal). Selected: inverted to `--n9` with an `--n0` number and a
  2 px `--n0` ring.
- **Route shield** — 22 × 16, radius 3, `--n8` fill, `--n0` number. Pinned once per corridor
  terminus and once mid-corridor. Suppressed inside a floating surface's safe rectangle.
- **Rack segment** — the one filter control. A plain `<button role="switch">` inside a glass rack;
  unselected is transparent with an `--n8` label, selected is `--n9` fill with an `--n0` label, at
  radius 9 — concentric with the rack's 14 less its 5 px inset.
- **Roster item** — the keyboard and screen-reader path to a vehicle the map draws in a canvas.
  Visually hidden until it takes focus, when it becomes a readable chip clear of the view stack: a
  control that can take focus and cannot be seen is worse than no control.
- **Alert row** — the one list item. `--n0` at 72% over the glass, radius 16 (26 less the sidebar's
  10 px inset), a 10 × 10 state square, a title, a mono timestamp, two lines of body, the affected
  route and fleet numbers as chips, and the state as a word. Expanded adds a 1.5 px `--n9` rule on
  all four sides — never a coloured left stripe.
- **Camera plate** — the photo slot, 304 × 171 radius 12, with a mono caption naming the camera and
  the frame time.
- **Platter action** — a plain 32 px button inside the platter. Never a second glass surface: the
  platter is already the material.

Build order: tokens → the painted plane → the glass surfaces and their groups → the data → the
interactions → the reduced and forced-colour states.

---

## 6. Voice

Quiet × consequential: terse, technical, states facts, never humorous, never manufactured urgency.
Sentence case everywhere; uppercase only as a styled label. Times are 24-hour. An adherence reading
is always signed and always paired with a word (`+6:20 late`), never a colour alone. Button verbs
name the outcome the controller is accountable for — "Hold 3 min", "Call driver", "Short-turn" —
never "Submit" or "OK". Empty results say what is absent and what clears it: "No vehicle matches
route 44 and *late*. Clear the state filter."

---

## 7. Motion

Three motions, each answering a state change:

- **The plane moves** because the vehicles do — position interpolated per frame along the corridor.
  Content motion, not decoration.
- **The platter materialises** from the blade that opened it: one registered host whose box the page
  animates from the blade's rect to the platter's over 220 ms on `--ease-out`. Never a cross-fade,
  never a second surface faded in over the first.
- **Press** is the runtime's own glow at the pointer — `--vitrea-press`, `--vitrea-press-x/y`,
  `--vitrea-glow` written on the host — never a colour swap.

Durations: 90 ms press, 140 ms hover and focus, 220 ms platter. The map's recentre is a single step
of 55% of the offset rather than a timed fly, so a selection never leaves the controller watching an
animation finish. Under `prefers-reduced-motion` the platter is placed instead of animated and the
vehicles step every 4 s instead of interpolating — reduced, not frozen, because the positions are
the information.

---

## 8. Hard don'ts

- No glass on a row, a list, a table, the alert content or the camera plate. Glass is the six
  surfaces in §3 and nothing else.
- No glass inside glass. Every control inside the sidebar or the platter is a plain element.
- No `background`, `filter`, `opacity < 1`, `mask-image`, `clip-path` or `mix-blend-mode` on a glass
  host or on any ancestor of the plane root — the last five re-root the backdrop and demote the
  group.
- No tint. No `clear` variant. No non-uniform radii.
- No coloured left border on an alert row, no gradient text, no shadow on a resting surface, no
  eyebrow above every section, no `01 / 02 / 03` markers.
- No route hue in the control layer, and no service-state colour on a control's background.
- No colour literal outside `:root`, including in canvas paint code.
- No stat row, no headline metric, no chart. This surface has none and does not want one.
- No CSS grid, grain or gradient laid *over* the backdrop: anything the lens must bend is painted
  into the texture.
- No second `requestAnimationFrame` loop — per-frame work joins `root.subscribe`.

---

## 9. Data rules

The world is fictional and internally consistent: one city, eight corridors, forty vehicles, six
alerts. Fleet numbers are 4100–4499 and every vehicle's block number is `<route><two digits>`.
Adherence readings sum: a headway gap named in an alert is the difference between the two vehicles
the alert names, and both appear on the map with the states the alert claims. A vehicle named in an
alert is on the corridor the alert names. Clock times run backwards from the network clock in
plausible order — an alert raised at 08:41 is above nothing raised later. Nothing on the page is a
round number.

---

## 10. What this page does not demonstrate

Recorded rather than left implicit, so a later pass knows where to look.

- **The size law's mid-curve is thin.** Only the platter sits at span 64, and only while a vehicle
  is selected; at rest the family is two rungs, 44 and 336, which are the law's two ends. The page
  has two classes of floating surface and a third rung would be an invented control.
- **No tint and no `clear` variant appear at all.** An accent job of `none` spends both, so nothing
  here exercises the adaptive tint or the dimming layer `clear` requires.
- **The CSS tier is the same design without refraction, by contract.** It was forced once (by
  withholding `navigator.gpu`) and looked at: layout, hierarchy, type and the state ladder are
  unchanged, and the residual is the lens.
- **Only Chromium was rendered.** Gecko's `backdrop-filter` conformance is unverified in this
  repository and WebKit's is manual-only, so no cross-engine claim is made here either.
- **One scroll edge, because there is one scrolling view.** The map pans; it never scrolls. A second
  scrolling region would owe its own edge at the same height.
- **Reduced transparency was exercised through the runtime's override API,** not through the media
  query, because no browser driver can emulate `prefers-reduced-transparency`.
