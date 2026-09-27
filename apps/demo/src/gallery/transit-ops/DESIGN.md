# Transit operations — design record

The desktop operations map of Port Alder Transit's control room: eight bus routes, forty vehicles in
service, six active alerts, seen by a dispatcher at a 1440-wide desk monitor. Built under the
materialist skill (`skills/materialist/SKILL.md`) on `@vitreajs/vitrea-react` at the workspace
source (0.24.0), then revised on 2026-09-27 against the independent source review recorded in
`docs/research/data/2026-09-27-materialist-proof/review/transit-ops.md` (§2, "Revised after the
source review").

## 0. The product, before the material

Who: a bus dispatcher (a "controller") watching the whole network for exceptions and acting on one
vehicle at a time. What the screen enables: scan for what is wrong, go to it, act on it — an alert
becomes a vehicle, the vehicle becomes a call to its operator. The whole page exists for that loop,
so the design decisions below are weighed against how fast an exception is found and how calmly the
normal state reads.

The opaque page first, as if no material existed: a full-window map is the page; its hierarchy is
carried by cartography (a quiet basemap, eight route lines, forty vehicles) and by one rule taken
from control-room practice (ISA-101 "high-performance" HMI): the normal state is quiet and colour is
reserved for the abnormal. On-time vehicles carry only their route's colour; only an exception
carries a tag, and its tag says in words what is wrong (`+7 min`, `Disabled`, `Detour`), with
severity doubled by colour (amber warning, red critical). Beside the map sit two things a dispatcher
reads: the list of alerts, and the selected vehicle's dossier. Over it sit the controls a dispatcher
uses: which routes and which states to look at, a way to jump to a vehicle, stop or route, the map's
own zoom, and the selected vehicle's actions. The reading is content; the controls are what the
glass is for.

## 1. The record

```
plane: one full-viewport <canvas> (position: fixed, inset 0), painted at its own CSS box x DPR and
  registered as texture source "city", so paint and sample are the same pixels. It is live: the
  forty vehicles move every frame on real time along the eight routes. Broad frequencies painted
  in: the Alder river and the harbour bay, parks and a reserve, a built-density wash (the old town
  darker than the suburbs), district tones. Fine frequencies painted in: a 1 px street web on
  district grids at several angles, arterial casings, the rail line's ticks, harbour piers, the
  harbour's chart (isobaths, the dredged channel and its buoys), route lines with casings, stop
  dots, street and district labels, and on the city's two flat fills their own marks: depth
  soundings on the water and tree marks in the parks, on a world-fixed lattice whose pitch stays
  24 to 48 px on screen at every zoom. Nothing is laid over the canvas in CSS. The camera is
  bounded to the mapped city (the districts and the harbour, -7000..12000 by -4000..11000 m) at
  zooms from the one where the window just fits inside it (0.076 px/m at 1440 x 900) to 0.5, so no
  control ever floats over the bare land fill past the city's edge.
inventory: glass, base plane — (1) route filter rack, (2) status filter (runtime segmented
  control), (3) search field: the top bar, three groups; (4) zoom stack (zoom out, zoom in, fit
  network); (5) the selected vehicle's action capsule (call operator, hold, follow, close),
  transient, materialised in place when a vehicle is selected. Glass, overlay plane — (6) search
  suggestions, transient, materialised under the field while a query has matches. Opaque, tonal
  (one lightness step off the map's land and a hairline, no shadow, no blur): the alerts sidebar
  (the operations summary, six alert rows, the Reduce transparency switch, the map attribution)
  and the selected vehicle's detail card (identity and status, the alert's note, the nearest
  camera still, six facts). Everything else is the map itself. Inside glass, chips, segments,
  actions and suggestion rows are fills or vibrant ink, never hosts.
groups: routes (rack), status (segmented), search (field), suggest (suggestions, overlay), zoom
  (stack), vehicle (action capsule). All six read texture "city". Each ALSO declares a hint, read
  from the final displayed canvas (city, buses, tags, selection) under that host's current box:
  mean relative luminance, and a complexity from the spread. Every repaint of the canvas (the
  buses included) marks the hints dirty and a dirty set is re-read at most every 6th frame, so a
  continuous pan cannot starve it; a host whose footprint moved is re-read on the frame that sees
  it, past the throttle; 500 ms is the backstop (§2.3). Gaps are derived from the
  runtime's resolved sampling padding (renderInput), never pinned: between two glass groups the
  larger padding, between glass and an opaque panel the glass group's own padding.
family: thickness 8 across all surfaces. Rung M, span 44: rack, segmented control, search field,
  zoom stack and action capsule, capsules at radius 22. Rung L, span 62 (the absent platter's one
  held row) to 295 (six rows): the suggestions platter at a fixed radius 26. The family straddles
  the size law: 44 sits in the 32..96 band (thin, clear glass), the open suggestions past
  saturation. The opaque panels share the 26 radius so the page has one large corner, and are not
  in the family. Anchor: the viewport edge, radius 0, at a 12 px window inset; no outer radius is
  inherited. Inner radii are housing minus inset and land on one number: rack chips 22 - 4 = 18,
  segment indicator 22 - 4 (resolved concentric by the runtime), zoom buttons, actions and the
  close button 22 - 4, suggestion rows 26 - 8.
tint: none. The plane already spends eight route hues and two alarm hues; a tinted control would
  be an eleventh hue competing with the alarms, and the only candidate (Call operator) is found by
  position and weight. The primary action is an ink fill inside the capsule.
scheme and pose: colorScheme auto. Light is the day shift in a daylit room and the distinctive
  register; dark is the night shift with the room dimmed. The basemap and the panels have their
  own palette per scheme (a dark map, not the light one inverted). windowActivation auto: an
  unfocused window recedes, which is the normal state of a map on the second of a dispatcher's
  three monitors.
motion: the action capsule and the suggestions use `present` (materialise in place; the capsule's
  source is a vehicle on the map or an alert row, both content, with no glass to morph from), and
  their content arrives with --vitrea-materialization; switching vehicles changes content in place
  without re-materialising. The detail card is content and fades over 200 ms beside the capsule's
  materialise (none under reduced motion); stepping aside for the suggestions is immediate. The
  segmented control's indicator is the runtime's. The zoom stack and the action capsule are
  `interactive`: the runtime's light and flex at the pointer, no page colour on press.
  The map recentres in one step only when a selection would be hidden under the chrome or off
  screen. The glass has no idle motion; the plane moves because the buses do (real time, not
  accelerated). Reduced motion: vehicles step at the AVL ping cadence (every 5 s) instead of
  gliding, following the runtime's resolved policy live.
tier expectation: webgpu where the engine grants a secure context and an adapter (localhost in
  Chromium); css elsewhere and on request via ?renderer=css; the CSS tier is the same design
  without refraction or hue retention.
accessibility: the runtime follows the system for motion and contrast; Reduce transparency is an
  app setting (a switch in the sidebar footer, seeded from prefers-reduced-transparency where the
  engine answers it, then stored) passed to the root as a boolean on every engine; forced colours
  removes the glass and the page still works (the panels become Canvas/CanvasText, the map
  unchanged).
contrast: glass labels take the runtime's primary ink on child elements, made opaque on the thin
  controls, and a secondary mixed from it; panel labels take the page's own ink, measured on the
  panel ground; measured on rendered pixels at the plane's lightest and darkest phases in both
  schemes, 4.5:1 for labels and 3:1 for large text and glyphs; results in section 4.
```

## 2. Decisions

### Revised after the source review (2026-09-27)

The review found eight defects in the page as first built. Each fix, and what it changed:

1. **The alerts sidebar is content, so it is opaque.** It had been glass, argued as navigation
   because each row is a button. But six incident records with their title, place, age, severity
   and routes, and the operations summary above them, are read in place; the skill's decision
   function (SKILL.md §3, step 1) keeps a list or panel of content opaque whatever it is called.
   The sidebar is now an ordinary `<aside>` in the page's flow, never registered, on the tonal
   model, in the same place and with the same select-on-click rows. The map attribution moved into
   its footer, off the map's corner, where the action capsule now sits.
2. **The vehicle platter is split along the layer line.** Its note, camera still and six facts are
   a dossier, so they are an opaque detail card; only its actions are controls, so they are one
   capsule on the family's 44 rung (Call operator, Hold, Follow, Close) that materialises with
   `present`. The capsule sits at a fixed place in the window's bottom-right corner and the card
   stands on it, clearing it by the capsule's own padding and growing upward with its content, so
   a card of any height never moves a registered host. The card steps aside (hidden, inert) while
   the search suggestions are open: they open over its corner, and glass there reads the painted
   map, not the card, so glass over the card would show a map the reader cannot see. Stepping
   aside is immediate, with no fade, so the suggestions never materialise over a card that is
   still visible; coming back fades in over 200 ms. The capsule is `interactive`: a press on any
   action lights and flexes the housing, and the buttons inside stay plain fills.
3. **Hints come from the displayed canvas, on a cadence that cannot starve.** They had been read
   from the cached basemap (no buses, no tags) after a 300 ms debounce that every camera move
   reset, and never when a host moved. A declared hint is what drives the material's tone on both
   tiers (the WebGPU tier stands its own measured tone down when one is present), so it has to be
   the backdrop the reader sees. Now every repaint of the canvas, the buses' every frame included,
   marks the hints dirty, and in the root's own frame after the buses are painted a dirty set is
   re-read at most every 6th frame. The same frame compares every host's box with the last one's,
   and a moved footprint (a gap change, the suggestions opening, the capsule appearing) is read on
   that frame, bypassing the throttle, because its old reading describes a place it no longer is.
   500 ms is the backstop should the frame loop stop repainting. The reading draws the displayed
   canvas into a half-resolution GPU copy, reads that copy
   back once into a `willReadFrequently` canvas, and takes each host's mean relative luminance and
   spread; a group's declaration changes only when its luminance moves by 0.004 or its complexity
   by 0.05. Measured during a 2 s continuous drag: the zoom group's tone level as the runtime
   resolved it (`renderInput`) moved 0.580 → 0.603 → 0.642 as the water left it, in step with the
   drag rather than after it. No Chromium readback warning.
4. **The camera is bounded to the mapped city.** Unbounded panning could leave every control over
   the flat land fill outside the districts. The camera's position now keeps the whole window
   inside the districts and harbour, and its zoom runs from the window-fits-the-city scale up to
   0.5 px/m. At that ceiling the coarsest street web (150 m blocks) is 75 px apart, finer than the
   shortest control's long side (the zoom stack, 120 px). Water and parks are the city's only flat
   fills, and a whole control fits inside one at a close zoom, so they carry depth soundings and
   tree marks on a lattice whose pitch doubles with zoom (24 to 48 px on screen). The one-step
   recentre on selection steps the zoom in, within the bounds, where the bounds stop a recentre
   short near the city's edge.
5. **The absent suggestions host is a real box.** It registered at span 16 (its padding) while
   empty and collapsed mid-dematerialise when a pick cleared the query. It now holds the rows it
   last showed through its exit and, before it has ever opened, one hidden row of the real height,
   so the absent host is span 62 and `present` always materialises a real surface.
6. **The selected bus is tested after the card opens.** The visibility test ran before the open
   state committed, against the closed platter, so a bus visible before opening could end up
   underneath. It now runs in a layout effect after the selection commits, against the card's and
   the capsule's open boxes. Checked: selecting the Kingsway detour alert, whose bus sat where the
   card opens, recentres it into the free rectangle.
7. **No colour on press; the runtime's press instead.** The icon buttons' `:active` fill is gone,
   and the zoom stack's hover fill with it: that housing is `interactive`, so hover and press are
   the runtime's light and flex. The action capsule is `interactive` too, so Call operator, Hold,
   Follow and Close press the housing rather than changing colour; the close button takes the same
   hover fill as the actions beside it and no pressed colour.
8. **Reduced motion is followed live.** It was read once at mount; the simulation's stepped flag now
   comes from the runtime's resolved accessibility policy (`useGlassAccessibility`), which follows
   the system preference, with the media query answering only before the root's first frame.

### Decisions from the build that stand

1. **Search results emerge as a platter on the overlay plane**, under the field, materialised with
   `present`. It is a hand-written ARIA 1.2 combobox (`role="combobox"` input, `listbox` child,
   `aria-activedescendant`) that searches buses, routes, stops and operators.
2. **The zoom stack sits at the bottom-left of the map area**, on the top bar's vertical. The right
   column belongs to the selected vehicle, its card and the action capsule in the corner. The
   skill's macOS reading puts map controls bottom-right, so this departs from convention, and the
   record says why.
3. **The status filter carries no counts.** Under Reduce Transparency the runtime asks for up to
   50 px between bar groups, and with counts the top bar overran a 1280 window. The counts live in
   the sidebar summary (`40 in service · 8 late · 3 early`), and each segment's accessible name
   still carries its count.
4. **Gaps are derived every frame, then the hosts are re-dirtied.** `Gaps` in `App.tsx` reads
   `root.renderInput().groups[].samplingPadding` and writes the gaps as CSS variables. The floor is
   24, core's advisory padding, which its own overlap check reads. Gaps grow at once and shrink only
   past 6 px. The runtime re-measures a host only when its own box resizes, on a scroll, on a
   viewport resize or through a handle's `invalidateGeometry()`, so a host moved by a gap change
   would keep its old rect (measured on the first build: glass drawn 36 px above its box, and an
   overlap check reading stale rects with no diagnostic). `GlassSegmentedControl` keeps its host
   handle to itself, so the page dispatches a document `scroll` after a gap change, which dirties
   every host. Measured: 0.0 px between every host's DOM box and `scene.glassNode().bounds`, at
   rest and with the vehicle open under Reduce Transparency.
5. **The vehicle is mounted with content from the first frame** (bus 4431, closed). The capsule
   already has its open span, so the padding the runtime derives from it does not jump on first
   open, and the card has a box to lay out.
6. **The harbour has a chart.** Five isobaths, the dredged channel with its buoys, a breakwater, a
   marina's pontoons and a shipyard's piers; since the revision, soundings between them (§2.4).
7. **Ink.** Primary labels on the thick glass take the runtime's token. Two places use the page's
   own ink (skill: "a page that needs a guaranteed ratio sets its own ink on a child element"):
   - Secondary text on glass is `color-mix(var(--vitrea-foreground) 70 % light / 90 % dark,
     transparent)`. The runtime's secondary holds 4.5 against the mean surface and read 3.8:1 where
     the body carries a lighter patch of the map; the dark mix was raised from 85 % to 90 % in the
     revision because the suggestions' detail line read 4.51 at 85 % against the honest hints.
   - On the thin 44 px controls, labels use `rgb(from var(--vitrea-foreground) r g b / 1)`: the
     pole the runtime picked, made opaque. The explicit `/ 1` matters; relative colour syntax
     otherwise keeps the origin's alpha.

   The panels' ink is the page's outright, since no runtime token exists off the glass: light
   `#1b2129` / `#525a64` on `#f5f6f8`, dark `#eef1f4` / `#a7b0ba` on `#1c2026`; their selected row
   is ink at 12 %, and under `prefers-contrast: more` their secondary joins the primary.
8. **Selection fills** on glass are the ink at 15 %, hover at 8 %, and the primary action is a solid
   ink fill with inverse text. Nothing on the page is tinted. The only saturated colours in the
   control layer are the route dots (a legend key to the plane's lines).
9. **Tags avoid each other.** Four late buses sit inside ten pixels in the Victoria Bridge queue.
   Exception tags are placed most severe first: right, left, then stacked with a leader. A tag is
   dropped only when nothing fits, and a selected or hovered bus's tag is always drawn.
10. **Forced colours** needs `forced-color-adjust: none` on selected chips, segments, alert rows and
    the primary action, because Chromium's text backplate otherwise paints Canvas behind
    HighlightText and erases the label. The settings switch gets a CanvasText outline.
11. **Every `window` handle goes through a local cast, not a global `Window` augmentation**,
    because the gallery pages compile in one program and two declarations of `__vitrea` with
    different types collide.
12. **Below 1380 px** the sidebar narrows to 268 and the chips tighten, so the three bar groups and
    their derived gaps fit at 1280 × 800 under Reduce Transparency (checked in dark with the vehicle
    open: zero diagnostics).

## 3. What the runtime resolved

Read back from the page (`__vitrea.capabilities(id)`, `renderInput()`, both diagnostics channels)
at 1440 × 900, DPR 2, Chromium 151 with `--enable-unsafe-webgpu`, material
`apple-macos-27.0-glass0.5`, on 2026-09-27 after the revision.

| state | renderer | sampling | refraction | analysis | health |
|---|---|---|---|---|---|
| default, all 6 groups, light and dark | webgpu | gpu-texture | true | exact | ok |
| `?renderer=css`, all 6 groups, light and dark | css | css-backdrop | none | hint | ok |

`analysis: exact` names where the pixels come from; the tone on both tiers is the declared hint
(§2.3).

Resolved sampling padding (CSS px), with the vehicle open:
- Light: the five 44-span groups 23.0, suggestions 24.9. Under Reduce Transparency 40.0 and 41.4.
- Dark: 25.8 and 29.8. Under Reduce Transparency 47.2 and 50.3.

The derived gaps followed: 26 px light and 28 dark nominal, 42 and 50 under Reduce Transparency.

Diagnostics, `__vitrea.diagnostics.reported` and `__vitrea.scene.diagnostics.reported`: **0 and 0**
in every captured state, light and dark, on both tiers:
- at rest; the vehicle open; the suggestions open (card stepped aside);
- the old town's bundle and tags dragged under the top bar with the vehicle open;
- panned to the north-west and south-east corners of the bounded camera, at the fitted zoom and at
  the zoom floor;
- zoomed to the ceiling over the open harbour;
- Reduce Transparency on with the vehicle open; forced colours; the receded pose;
- 1280 × 800, dark, Reduce Transparency, vehicle open, then suggestions open.

The console carried no errors or warnings. The receded pose was captured once with
`setWindowActivation("inactive")` (a headless page stays focused); the page itself never pins it.
Seen: the rim collapses, the shadows stop, the glass flattens a step toward grey, and the layout
and the opaque panels are unchanged.

## 4. Contrast, measured

Method: for every label, two DPR 2 frames, one as rendered and one with the labels' glyphs made
transparent (`-webkit-text-fill-color`, which leaves fills mixed from `currentColor` in place) and
the icons hidden, with reduced motion emulated so the buses hold still between the two. Glyph
pixels are where the frames differ inside the label's own text rectangles; the ink is the median of
the strongest fifth of them. The ground is the text-free frame under the same rectangles, at the 5th
or 95th percentile nearest the ink ("worst"). The script was run from the session and is not
committed. States: rest; the vehicle open; the suggestions open; the old town's route bundle and
exception tags dragged under the top bar with the vehicle open; the north-west and south-east
corners of the bounded camera. Floor: 4.5:1 for labels, 3:1 for large text and glyphs.

Worst reading over all six states (436 readings per scheme and column, none below its floor):

| label | light GPU | dark GPU | light GPU+RT | dark GPU+RT | light CSS | dark CSS |
|---|---|---|---|---|---|---|
| panel primary (h1, summary, title, facts, note) | 14.98 | 14.43 | 14.98 | 14.43 | 14.98 | 14.43 |
| panel primary on the selected alert row | 11.82 | 10.24 | 11.82 | 10.24 | 11.82 | 10.24 |
| panel secondary (eyebrow, clock, facts, caption) | 6.46 | 7.45 | 6.46 | 7.45 | 6.46 | 7.45 |
| panel secondary on the selected alert row | 5.10 | 5.29 | 5.10 | 5.29 | 5.10 | 5.29 |
| route chip | 13.31 | 5.17 | 14.45 | 6.69 | 13.32 | 5.09 |
| status segment | 12.86 | 4.53 | 15.02 | 7.12 | 13.13 | 4.71 |
| search input (placeholder) | 4.99 | 5.19 | 5.48 | 6.34 | 5.06 | 5.41 |
| search key | 5.12 | 5.82 | 5.43 | 6.36 | 5.19 | 5.79 |
| search glyph (3:1) | 4.89 | 5.16 | 5.41 | 6.38 | 5.08 | 5.41 |
| suggestion title and route | 11.07 | 5.55 | 11.60 | 5.46 | 11.04 | 5.61 |
| suggestion detail (sec) | 4.90 | 4.84 | 5.03 | 4.76 | 4.96 | 4.89 |
| action labels | 15.17 | 8.75 | 14.94 | 8.32 | 15.31 | 8.69 |
| close glyph (3:1) | 13.77 | 7.85 | 14.53 | 7.46 | 13.78 | 7.84 |
| zoom glyphs (3:1) | 17.00 | 11.41 | 19.86 | 10.53 | 16.94 | 11.20 |

The lowest label is the dark status segment's selected "All" over the old town bundle, 4.53 on the
GPU tier: white ink over the 15 % indicator fill, on glass whose declared hint now includes the
bright tags under it. It passes and is the thinnest margin on the page; the next ink or fill change
there should re-read it.

## 5. QA lens (SKILL.md §8)

1. `[layer]` Pass. The glass surfaces are the route rack, the status filter, the search field and
   the zoom stack (actions and navigation), and the vehicle's action capsule and the search
   suggestions (transient). The map, the alerts sidebar and the vehicle's detail card are content:
   the map on the plane, the two panels opaque (§2.1, §2.2).
2. `[layer]` Pass. Nothing registered sits inside a registered host: chips, segment labels,
   actions and suggestion rows are fills or ink, and the segmented indicator is the runtime's DOM
   fill. The suggestions overlap the capsule only across planes, and never overlap an opaque
   panel: the card steps aside while they are open.
3. `[layer]` Pass. Four persistent surfaces and two transient ones, each read aloud in §1.
4. `[material]` Pass. Regular everywhere; no clear variant.
5. `[material]` Pass. No tint at all. No solid fill or hand-rolled blur on any host; the panels'
   fills are on elements that are not registered.
6. `[material]` Pass. The camera never shows past the mapped city (§2.4), the street web is finer
   than every control at the zoom ceiling, and water and parks carry their own marks. Checked by
   eye at the zoom floor's northern and southern extremes (at the floor the city's full width is
   in the window) and at the ceiling over open harbour.
7. `[material]` Pass. No depicted material. The camera still is a photograph of content, on the
   opaque card.
8. `[geometry]` Pass. The anchor is the viewport edge (r0) at a 12 px inset. Every inner radius on
   glass is housing minus inset: 22 − 4 = 18 for chips, the segment indicator (the runtime's
   concentric resolver), zoom buttons, actions and the close button; 26 − 8 = 18 for suggestion
   rows.
9. `[geometry]` Pass. The rack, status filter, search, zoom stack and action capsule are capsules
   at 44; the suggestions platter is a fixed 26 rounded rectangle.
10. `[geometry]` Pass. Two rungs, 44 and 62–295, one radius each, thickness 8 throughout; no
    registered host is below span 44, the absent suggestions platter included (§2.5). There is no
    mid rung (60–90) beyond the platter's one-row size; adding a surface to fill one would break
    law 3.
11. `[grouping]` Pass. One group per surface, three in the top bar. The zoom stack is icons only;
    the rack and the status filter are text only; the action capsule is one row of one job, whose
    close glyph ends it. Gaps are derived from the resolved padding, glass to glass and glass to
    panel, and hold under Reduce Transparency.
12. `[legibility]` Pass. Every label is at or above 4.5:1, and every glyph and large label at or
    above 3:1, at its worst measured phase in both schemes, on both tiers and under Reduce
    Transparency (§4). The lowest are the dark selected segment (4.53) and the dark suggestion
    detail (4.76 under Reduce Transparency).
13. `[legibility]` Pass, with a map-specific reading. At rest the network is fitted into the
    rectangle the chrome leaves free, measured from the hosts' and panels' boxes, so no bus sits
    under glass or a panel at first paint. A selection is tested against the open card and capsule
    after they commit (§2.6). The map pans under the glass by intent, and that is the plane moving.
    The panels scroll only their own content, with no glass over them, so there is no scroll edge.
14. `[legibility]` Pass. Reduce Transparency: the app's switch, frostier glass, gaps widen, the
    panels unchanged. Increased contrast: the page's fills strengthen and the panels' secondary ink
    joins the primary under `prefers-contrast: more`; the runtime's material for it was not
    captured, because Playwright cannot emulate it. Reduced motion: buses step at the 5 s AVL
    cadence, following the runtime's policy live (checked: the resolved `reducedMotion` flips with
    the emulated preference), and the card does not fade. Forced colours: captured, the glass is
    gone and the page still works. Receded pose: captured.
15. `[layout]` Pass. The canvas is viewport-fixed and full-bleed, and the page does not scroll.
    Every inset is measured: the network fit, and the one-step recentre when a selection would
    fall under the chrome.
16. `[layout]` Pass. No host carries a background, border or shadow. The only authored rules on
    hosts are placement and the search capsule's `border-radius`, which shapes its focus outline.
    The panels' fill and hairline are the content layer's own ground.
17. `[motion]` Pass, with one departure. The capsule and the suggestions materialise with
    `present`, and their content follows `--vitrea-materialization`. The segmented indicator slides
    on the runtime's springs. The zoom stack and the action capsule are `interactive`: glow and
    flex at the pointer, and no page colour on press. The map recentres in one step. Nothing on the
    glass moves at idle. The route rack is not `interactive`, because pressing one chip would
    compress a whole 480 px housing of eight independent filters; it behaves as the runtime's own
    segmented track does, fills inside and no flex. The capsule materialises in place rather than
    emerging from a control, because its source is a bus on the map or an alert row, which are
    content.
18. `[colour]` Pass. The control layer is monochrome ink. The route dots are a key to the plane, not
    a label colour. The severity glyphs, the only alarm colour beside the map, live on the opaque
    panels, each doubled by shape and word. Route hues avoid red and amber, which are reserved for
    alarms on the map.
19. `[honesty]` Pass. The hints are read from the displayed canvas under each host's current box
    on a bounded cadence and on every footprint change (§2.3), and the resolved state and both
    diagnostics channels are read back in every state (§3).
20. `[eye]` Not compared. The nearest Apple surface is Apple Maps on macOS 27: a full-bleed map, an
    edge-to-edge sidebar, floating capsule controls and a place card. No native capture was
    available in this session, so no side-by-side was made. Differences seen by eye against memory
    of that surface, and not caught by any check:
    - Maps puts the selected place's card in its sidebar; this page gives the vehicle a card of its
      own in the right column, so the alert list stays visible while a vehicle is open. That costs
      the suggestions platter a collision it resolves by making the card step aside.
    - Maps' sidebar reaches the window's edges; this one keeps the 12 px inset and the 26 radius the
      page's first build gave it, so it reads as a panel on the map rather than a column beside it.
    - The 44 px controls show little lensing at the fitted zoom, because the map's fine structure
      is 1 px streets at about 8 to 14 px spacing. A closer zoom shows the rim displacing route
      lines and soundings clearly.
