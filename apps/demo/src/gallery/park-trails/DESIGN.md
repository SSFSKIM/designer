# Park trails — design record

The trails site for North Cascades National Park, a page of the vitrea demo site
(`apps/demo/gallery/park-trails/`), built under the materialist skill on vitrea 0.24.0 through
`@vitreajs/vitrea-react` on the workspace source. Desktop at 1440 wide.

Who it is for: a hiker at the Marblemount information counter, or at a laptop the night before,
choosing one of twelve trails and checking whether the road is open, what the weather is doing at
the pass and whether the trip needs a permit. What the page enables: one route chosen in the
floating planner, and everything beneath it (the list, the conditions, the forecast, the permit
steps) reading for that route.

## Record

Written before the first host was registered and brought up to date by the review fix wave of
27 September (below), so that every line describes the page as it is; what each changed line said
before is kept under "Revisions to the record".

```
plane: the licensed photograph of Diablo Lake (Pete Alexopoulos, Unsplash), painted cover-fit into
  one viewport-fixed <canvas> at the canvas's own box and device-pixel size, registered as the
  texture source "park" (an ImageBitmap snapshot of that canvas, placed on the canvas element, so
  paint and sample are the same pixels). The crop is chosen so the band under the planner is the
  forested ridge line and the valley's far wall, not the cloud: dark conifer texture and rock
  outcrops are the fine frequency, the ridge silhouettes and the valley's V the broad one. A
  relief map was the other rung the brief offered and was rejected: this park has no DEM on hand,
  and a relief painted from invented terrain would be a false map of a real park on a trails site.
inventory (base plane): the planner, one GlassToolbar at the top leading margin, three bodies:
  route (a morph trigger whose label carries the route's distance and gain), weather (a button
  whose label is today's weather at the route's high point, taking the reader to the forecast on
  the sheet), permits (a button that takes the reader to the permit steps for the planned route).
  (overlay plane, while open, the same host as its trigger): the route menu, whose rows are the
  twelve routes to choose from. Three glass hosts, all three drawn at every moment.
  Opaque, printed model: the sheet (header, the twelve-trail table, the conditions bulletin, the
  forecast by elevation with the planned route's trailhead and high point first, the permit
  steps, the footer), full-bleed paper that scrolls up over the photograph inside its own fixed
  scroller. The display switch (reduce transparency) is a control in the sheet, on paper.
groups: route — morph platter, own group; weather — button, own group; permits — button, own
  group. Three jobs (choose, check the weather, check the permits), three groups. Closed, all
  three sit inside the scroll-edge band, where the scroller is fully masked, so the only thing
  under them at every scroll position is the photograph: they read the texture. Open, the route
  menu extends over the sheet, which changes independently of the texture, so it samples the DOM
  from the frame it starts opening to the frame it has closed. Every group declares a hint
  measured from what is displayed under its measured bounds (encoded Rec. 709 luma, averaged and
  decoded once): the photograph from the pixels the canvas painted, the sheet from a model of its
  DOM (paper, fills, rules and each text run's ink coverage, `paper.ts`), blended by the mask's
  alpha. A declared hint overrides the runtime's own tone reading on both tiers, so this is what
  the body's tone and the ink follow everywhere, texture groups included.
  Gaps between groups are GlassToolbarSpacer, i.e. the runtime's own sampling padding.
family: thickness 8 across every surface. Rung M: span 48, capsule, radius 24 (route, weather,
  permits). Rung L: the route menu, 416 × 589 at 1440 × 900 (span 416), fixed radius 28. The
  family straddles the size law: 48 sits a quarter of the way up the 32–96 ramp (thin, clear
  glass), the menu is past saturation (the most opaque body, the deepest shadow). Anchor: the
  viewport edge at radius 0, a square frame; the planner sits at the page's leading margin and
  20 px from the top, and concentricity is held inside the menu: rows inset 8, radius
  28 − 8 = 20, which on a 40 px row is itself a capsule.
tint: none. The plane is the park and already carries the product's colour (evergreen, glacial
  turquoise, cloud); a hue on a control would add a colour a hiker cannot name a reason for. The
  one accent (lupine violet, the subalpine lupine of Cascade Pass and Sahale Arm) lives on paper:
  selection, links, focus.
scheme and pose: colorScheme auto, tokens follow prefers-color-scheme; the photograph is content
  and is the same in both schemes. windowActivation auto, never pinned.
motion: the route menu is a GlassMorph matchedGeometry from its trigger (radius 24 → 28,
  thickness 8 → 8, APPLE_LIKE_SMOOTHING at both ends); press is the runtime's glow and
  compression; the weather and permits buttons scroll the sheet to their destination (smooth,
  instant under reduced motion) and hand it focus. The plane never moves; there is no idle
  motion, no parallax, no reveal-on-scroll.
tier expectation: webgpu on localhost Chromium; css elsewhere and on ?renderer=css. The CSS tier
  is the same page without refraction.
accessibility: the runtime follows the system for motion, contrast and forced colours; reduce
  transparency is an app setting on the page (a switch in the sheet header, stored, seeded from
  the media query where the engine answers it) passed to GlassRoot as a boolean. Under forced
  colours the sheet redraws in system colours what it draws with backgrounds and shadows: the
  switch's track, thumb and state, the status marks, the bars that mark the planned route.
contrast: labels on glass take the primary ink on a child element; measured on rendered pixels at
  rest, with the route menu open at rest and over printed paper, both schemes and both tiers;
  results below.
```

## Revisions to the record, made while building

Each is a line above that the render changed; the line is kept as written and corrected here.

- **plane, the crop.** The first crop (zoom 1.22) left the cloud bank under the planner: a near-flat
  white field, glass with nothing to bend, capsules that read as faint white pills. The crop is now
  zoom 1.4 over a plain cover fit, overflow split 0.40 / 0.94 (`PARK_CROP`), which puts the band
  at 1440 × 900 on the ridge line and the valley's hazy far wall: dark conifer texture, rock, the
  ridge silhouettes crossing behind the capsules. The cost is the sky: the cloud survives only as a
  wisp at the top-left corner, and the photograph is upscaled about 1.6× at 2x.
- **scheme, the photograph at night.** "The same in both schemes" did not survive measurement. At
  daylight exposure the band reads 0.40 to 0.52 encoded; the dark material's body over it lands
  mid-grey (about 0.45 to 0.52 encoded) and the runtime still picks white ink, which measured 3.0
  to 3.9 : 1 on every bar label. The dark scheme now paints the plane with one uniform cool
  multiply of about 0.5 (`NIGHT_EXPOSURE` in `ParkPlane.tsx`): the same place at dusk. It is
  painted into the canvas, so the texture, the luma field and the reader all see the same pixels,
  and it is uniform, not a gradient under the bar (the skill bans a scrim there).
- **family, the gap.** "Gaps are the runtime's sampling padding" became "gaps are one capsule
  height, never less than the runtime's padding": see the first runtime finding below.

### The review fix wave, 27 September

An independent source review against the skill
(`docs/research/data/2026-09-27-materialist-proof/review/park-trails.md`) returned five findings;
each is fixed, and the record above now says what the page does. What the record said before:

- **inventory, weather.** "weather (a morph trigger) … the weather platter. Five glass hosts in
  total." The platter was a three-day, two-elevation forecast table with the freezing level and
  sunset: a table of content floating on glass, which the skill's first question keeps on paper
  whatever the brief calls it (SKILL.md §3, 1; §7). The capsule is now a button that goes to the
  forecast on the sheet, and the sheet's forecast gained the two columns the platter had (see
  "The weather capsule goes to the forecast" below).
- **groups, the hint.** "the sheet's paper weighted in by its coverage and the mask's alpha,
  which is what the CSS tier and the DOM path adapt to." Two things were wrong. The sheet was one
  paper luma, so a menu open over headlines, body text, rules and the selected row's wash
  declared a paper that was lighter (light scheme) or darker (dark) than what it was over. And a
  declared hint is not only what the CSS tier and the DOM path adapt to: it overrides the
  runtime's own tone reading on both tiers, including a texture group's on the WebGPU tier
  (platform-web `root.ts`, the declared luminance; renderer-webgpu `renderer.ts`,
  `backdropToneHint`). The sheet is now measured as displayed (below).
- **the footer.** It described the planner from the permits group's state alone, and so said
  "reading the photograph's pixels" while the open menu sampled the page. It now reads all three
  groups and names each by its capsule's label.
- **forced colours.** The custom switch lost its track, thumb and state (its fills and inset
  shadow are what forced colours removes), and the status marks and the route's accent bars went
  with them. Each is redrawn in system colours under `(forced-colors: active)`.
- **focus.** "Conditions bulletin" inside the weather platter scrolled to the bulletin and focused
  it, then the platter's close handed focus back to the trigger. That button went with the
  platter; the rule behind the bug is fixed too: a platter's close returns focus to its trigger
  only when focus fell with the platter.
- **QA lens 14.** "Increase contrast was not opened: Playwright cannot emulate it." Playwright
  emulates `prefers-contrast: more`, and the session's audit had already opened it; it is now
  checked in both schemes (QA lens, 14).

## Decisions beyond the skill

- **The sheet has its own scroller, and the scroll edge is a mask on it.** The page's scroll is a
  viewport-fixed element (`.pt-scroller`), not the document, so its mask stays fixed to the window
  while the content moves under it, and it is a sibling of the glass root rather than an ancestor.
  The stops come from the planner's measured box: transparent to `bottom + height / 3` (the
  capsule's own shadow), opaque one capsule height later; 84 and 132 CSS px at 1440 × 900,
  recomputed by a ResizeObserver on the planner. The mask takes the paper with it, so what is under
  a closed capsule at every scroll position is the photograph, which is what makes the texture
  honest for the bar. The price is a strip of the park that is always visible above the sheet;
  it reads as the paper dissolving into the valley haze, and I kept it.
- **Keyboard scrolling is forwarded.** A fixed scroller does not receive Page Down or Space while
  nothing is focused; a window listener forwards them (and arrows, Home, End) when focus is on
  the body. Wheel over a capsule itself does not scroll the sheet; accepted.
- **The glass root attaches before `#root`** (`main.tsx`), so the planner is first in reading and
  tab order, inside a `section` landmark labelled "Trip planner", the way a header would be.
- **The weather capsule goes to the forecast; it does not float it.** The review offered two
  fixes: make the capsule a navigation to the opaque forecast, or keep a platter of choices (a day,
  an elevation) with the table on paper. A planner is served by the first. A menu of days or
  elevations would only change which number the capsule shows, a choice nobody planning a hike
  needs to make on glass, while what the hiker needs is the forecast itself, beside the rest of
  the conditions it belongs to. So the capsule is a `GlassButton` that scrolls the sheet to
  "Forecast by elevation" and focuses its table, as permits does for its section, and it lost its
  chevron, which promises a menu. The platter's content moved to paper rather than disappearing:
  the forecast's first two columns are the planned route's trailhead and high point, under the
  route's name and marked in lupine like every other mark of the route, so the capsule's figure
  (41°, showers, clearing, at Cascade Pass's high point) is the figure the reader lands on.
- **Sampling swaps with the route menu.** Its group reads the texture while it rests in the band
  and the DOM from the frame it starts opening until the frame it has finished closing
  (`useMorphSampling`; `onMorphEnd`). Read back: open, `css-backdrop / approximate / hint`; closed
  again, `gpu-texture / true / exact`. The swap is not visible at the start of the morph.
- **Declared backdrops are measured, continuously, as displayed.** `useMeasuredHint` reads each
  group's members' bounds from the runtime's scene every third frame and measures what is shown
  under them, cell by cell at 8 CSS px, quantised to 0.01. The photograph is its painted canvas.
  The sheet is `paper.ts`: a page cannot read back its own rendered DOM on every engine (a
  `foreignObject` snapshot taints the canvas in WebKit, where the CSS tier runs), so the sheet is
  modelled from its boxes and painted, at the field's resolution, into a small canvas in the
  sheet's own coordinates: its paper; every element's background, borders and inset zero-blur
  shadow strokes; the forecast's SVG symbols stroked from their paths; and each text run's line
  boxes filled with its colour at its ink coverage, the fraction of the line box its own glyphs
  cover, measured by drawing the run in its computed font into an offscreen canvas and summing
  the alpha. It is rebuilt a frame after the sheet's DOM, size, scheme or fonts change; the scroll
  position only moves where it is read. Left out, each a few per cent of the cells it touches:
  link underlines, the switch's thumb (a pseudo-element), focus rings and hover underlines.
  Checked against a capture of the same region with the menu closed (the menu's bounds, sheet
  scrolled over the trail table and over the bulletin), in encoded luma: light, model 0.909 /
  0.911 against capture 0.915 / 0.920, where paper alone said 0.942; dark, 0.132 / 0.130 against
  0.130 / 0.126, where paper alone said 0.100. The model now errs by under 0.01 where paper alone
  erred by 0.02 to 0.03, on the side of slightly too much ink in the light scheme. It is passed as
  `hint`, not as an `estimator`: platform-web's body tone adaptation reads only an author hint
  (`root.ts`, `declaredHint`), so an estimator would reach the readout and not the material. And
  a hint overrides the texture's own tone reading on the WebGPU tier too (`analysis: exact` says
  where the lens's pixels come from, not which value drives the tone), which is why it has to be
  the displayed pixels and never a typed constant.
- **Capsule faces stack every label they can show.** The route capsule's width is its widest
  route; the weather capsule's its widest forecast. `GlassMorph` measures its closed end once, so a
  label that changed width later would sit in a capsule of the old size; and a width that changed
  would push registered neighbours (below). The route capsule's slot holds a hidden in-flow sizer
  with the same face from the first layout, and the morph's footprint spacer grows into the same
  grid cell; the weather button's own stacked face does the same for it.
- **Focus returns to a trigger only when it fell with the platter.** Closing the route menu by a
  choice or a dismissal unmounts the focused row and focus falls to the body, so it goes back to
  the trigger the morph re-renders in place. A close during which something else took focus on
  purpose (a navigation, a press on a sheet control) keeps it there. The two navigations are
  plain buttons and move focus to their destination: the permit steps section and the forecast
  table.
- **Morph hosts are border-box.** On the first frames, before the GPU tier takes over, the CSS
  tier gives every host a 1 px rim border; on a content-box morph host that grew the capsule two
  pixels past its footprint and reported two `group-proxy-overlap`s at mount.
- **Tint withheld; the accent lives on paper.** Lupine violet marks the planned route's row, the
  bulletin entries that bear on it, its two forecast columns, the permit steps that apply, links
  and focus. Status marks
  differ by shape as well as hue (circle, triangle, square), and the word is always printed.
- **Content is realistic, not live.** Trail figures are the published ones as best known; the
  conditions, forecast (a lapse-rate model from the valley floor) and the Thornton Lakes closure
  are composed and dated 27 September 2026, and the footer says so.

## What the runtime resolved (read back, 1440 × 900, Chromium with WebGPU)

| state | route | weather | permits | diagnostics (root / scene) |
|---|---|---|---|---|
| webgpu, rest and scrolled | gpu-texture, true, exact, ok | same | same | 0 / 0 |
| webgpu, route menu open (at rest, over the trail table, over the bulletin) | css-backdrop, approximate, hint | gpu-texture, true, exact | same | 0 / 0 |
| webgpu, reduce transparency, each state above | as above | as above | as above | 0 / 0 |
| webgpu, increased contrast (emulated, both schemes) | as above; border strong, foreground near-monochrome | | | 0 / 0 |
| webgpu, forced colours (emulated) | as above; glass none | | | 0 / 0 |
| `?renderer=css`, every state | css-backdrop, none, hint, ok | same | same | 0 / 0 |

Both schemes identical in shape; material `apple-macos-27.0-glass0.5`; window activation
`active`. The footer reads the same states back in words. Declared backdrops (linear luminance, as
measured): light 0.23 / 0.18 / 0.12 under route / weather / permits, dark (night exposure) 0.06 /
0.04 / 0.03. The open route menu: light 0.35 at rest (photograph, then the masthead), 0.81 over
the trail table and over the bulletin (paper alone would have declared 0.87); dark 0.05 at rest,
0.02 over the sheet (paper alone, 0.01). Derived gaps, read by the maker and unchanged by the fix
wave (the spans did not move): 24 / 41 CSS px (light, normal / reduce transparency), 27 / 48
(dark).

## Contrast, on rendered pixels

Each label on glass is read from a capture of the viewport: the pixels inside its line boxes are
split into glyphs and ground, the ground's per-channel median is the reading, and the label's
computed ink (alpha included: black at 0.847, white at 0.804) is composited over it (the method
of the session's audit, `docs/research/scripts/glass-audit.mjs`). The figure is the minimum over
each surface's labels; "over the table" and "over the bulletin" are the sheet scrolled 700 and
1,850 px so the whole menu lies over printed text. The bar's band is the photograph at every
scroll position, so the capsules read the same at rest and scrolled.

| | light webgpu | light css | dark webgpu | dark css |
|---|---|---|---|---|
| route capsule | 10.2 | 10.3 | 5.4 | 5.4 |
| weather capsule | 9.7 | 9.7 | 6.2 | 6.2 |
| permits capsule | 9.0 | 8.9 | 6.9 | 6.9 |
| route menu, at rest (over the lake, then the masthead) | 8.7 | 9.7 | 4.6 | 4.7 |
| route menu, over the trail table | 11.8 | 11.9 | 6.2 | 6.1 |
| route menu, over the bulletin | 11.9 | 12.0 | 6.2 | 6.2 |

A sweep with the menu open, scrolling 0 to 1,400 px in steps of 50, finds every minimum at rest;
once the sheet lies under most of the menu (from 350 px on) the lowest is 10.0 light and 5.9
dark. The lowest figure on the page, 4.59 dark
WebGPU and 4.66 dark CSS, is the focused "Cascade Pass" row at rest: its 12 % ink fill over the
body where the menu lies over the lake. It passes by a small margin and is the page's worst
phase; the paper-only declaration gave the same figure there, so it does not come from the new
measurement.

Reduce transparency: capsules 13.6 and up light, 7.4 and up dark; the menu 11.7 and up light,
5.7 and up dark. It raises every figure except the dark menu over the sheet, which reads 5.8
against 6.2 without it. Increased contrast (emulated): light capsules 11.7 and up, menu 9.4;
dark capsules 10.3 and up, menu 7.0 at rest and 7.5 over the table. The session's audit on the
fixed page: 68 of 68 label pairs pass in each scheme, minimum 8.70 light and 4.59 dark. Before the
night exposure the dark column read 3.0 to 3.9 on the bar and 3.3 to 3.8 on the platter at rest.
On paper: ink 15.0 / 15.5, secondary ink 7.3 / 8.7, accent 6.3 / 8.6 (light / dark); in the
route's forecast columns, on their wash, ink 13.6 / 12.9 and secondary ink 6.6 / 7.2; status
marks at least 3.4 : 1.

## What the runtime did not tell me, and what the skill did not say

1. **A toolbar member that moves is not re-measured.** `GlassToolbarSpacer` re-derives its gap
   with the scheme and with Reduce Transparency, which moves every later member; nothing observes a
   host that moves without resizing, so the scene kept the old bounds and the glass stayed where
   it was while the label walked out of it (seen under Reduce Transparency: the weather chevron
   past the capsule's edge, "Permits" half outside). `GlassMorph`'s own closed-end realignment moves
   its host the same way. The page's fix is layout that never moves: gaps of 48, the largest
   derived value. Worth a runtime fix (invalidate a toolbar's members when its gap changes).
2. **The dark material's ink over a mid-tone photograph.** The skill says to measure; it does not
   say that the dark scheme can fail over the same band the light scheme passes at 10 : 1. The
   answer here was the plane's exposure, not the glass.
3. **Estimator versus hint** (above): only an author hint moves the body's tone, and a hint
   overrides the runtime's own tone reading on both tiers, a texture group's included.
   `vitrea.md` §2 says "on the WebGPU tier the pixels win", which is wrong on that point, and
   this page's own comment repeated it until the fix wave.
4. **Headless Chromium keeps every page focused**, so the receded pose was captured by pinning
   `setWindowActivation("inactive")` for the capture and releasing it to `auto`.

## QA lens (SKILL.md §8)

Looked at in both schemes, with reduce transparency on, with increased contrast, under forced
colours, on `?renderer=css`, and receded; answers as of the review fix wave.

1. `[layer]` Pass. The three capsules are a menu trigger and two navigations; the one platter is
   the route menu, whose rows are choices. The forecast, the one table that used to float, is on
   paper with the sheet, the trail table, the bulletin and the steps.
2. `[layer]` Pass. Rows inside the route menu are a 12 % ink fill; the trigger inside the morph
   host is a plain button.
3. `[layer]` Pass. Three capsules and at most one platter; each can be read aloud as a job.
4. `[material]` Pass. Regular everywhere.
5. `[material]` Pass. No tint; no fill or blur stands in for one.
6. `[material]` Pass for the bar: the band is the ridge line at every scroll position by
   construction. The route menu sits over the lake and forest and the masthead at rest and over
   printed paper with text when scrolled; paper is the flattest thing it meets, it carries text on
   it legibly, and its declaration now counts that text.
7. `[material]` Pass. No bevel, grain or painted light; the night exposure is a uniform grade.
8. `[geometry]` Pass. Capsules 48 / 24; the menu fixed 28; menu rows 28 − 8 = 20, capsules
   themselves. Anchor named: the viewport edge, radius 0.
9. `[geometry]` Pass. Single-row housings are capsules; the menu is a generous rectangle.
10. `[geometry]` Pass, with two rungs rather than three: 48 (a quarter up the size law) and the
    menu (span 416, saturated). Thickness 8 throughout, the morph's included.
11. `[grouping]` Pass. One group per body, three in the bar, no text and icon button sharing
    one, 48 px apart against a derived maximum of 48. Weather and permits are both navigations
    but different jobs over different stretches of the band, so they stay two groups.
12. `[legibility]` Pass; table above. Lowest: 4.59 : 1, the dark route menu's focused row over
    the lake at rest; with the sheet under most of the menu, 5.9 dark and 10.0 light.
13. `[legibility]` Pass. At rest the sheet starts at 58 % of the window, far below the band; the
    scroll edge exists only at the top, where the planner is.
14. `[legibility]` Reduce transparency: frosted near-white (light) and near-opaque grey (dark)
    capsules, every label 5.7 : 1 or better, layout unchanged. Increased contrast (emulated with
    Playwright's `contrast: "more"`, both schemes): the runtime resolves a strong border and
    near-monochrome ink, every label 7.0 : 1 or better, diagnostics 0 / 0. Forced colours
    (emulated): the runtime removes the glass, capsules and menu become system Canvas with
    CanvasText, the photograph stays, the platter still emerges non-elastically, diagnostics
    0 / 0; the sheet's switch keeps a bordered track and a thumb that moves and fills with
    Highlight when on, the status marks stay as CanvasText shapes, and the route's row, bulletin
    entries and forecast columns keep a Highlight bar. Receded (pinned for the capture): rim
    collapses and the shadow goes, labels legible.
15. `[layout]` Pass. The photograph and the sheet both reach every edge; the jump to a section or
    to the forecast lands its heading 24 px below the scroll edge, derived from the planner's box;
    the plane is viewport-fixed.
16. `[layout]` Pass. No authored background, border or scrim on any host; the only background
    declaration is the native button reset.
17. `[motion]` Pass. The route menu is a matched-geometry morph from its capsule; press is the
    runtime's glow and compression; nothing moves at idle.
18. `[colour]` Pass. Monochrome ink on glass; the photograph carries the colour, and on the GPU
    tier the capsules carry its blue-green haze.
19. `[honesty]` Pass. Every declared backdrop is measured from what is displayed, the sheet's
    ink included, and the model is checked against a capture (above); the footer reads each of
    the three groups' states rather than one; capabilities and both diagnostic channels were read
    in every state above.
20. `[eye]` No native capture was made. The nearest Apple surface is a macOS 27 unified toolbar of
    separate glass groups over a full-bleed photo (Photos or Maps). What the eye sees that the
    checks do not: at span 48 over the hazy far wall the light capsules read milky and lavender
    rather than clear, and the lens is hard to see at that size; over the dark forest (the permits
    capsule) the glass reads clearer and greener. The route capsule's fixed width leaves a gap
    before its chevron on short route names.
