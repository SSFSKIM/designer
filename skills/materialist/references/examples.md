# Worked examples: six glass pages, derived

Six pages were built on the material in September 2026, three product surfaces and three narrative
pages, each from a brief that named a live plane. Their code sits on the `capsule-refinement` branch
against vitrea 0.14.0 and has not been rebuilt: the reasoning below is current, the code is not.
Where a page hand-built something the runtime now does, the sentence says so and moves on. Read these
as derivations to imitate, never as tables of values to copy; every number belongs to its photograph,
its window and its brief.

Each section walks the same eight decisions: the live plane, the floating inventory, the groups and
what they declared, the size family and its geometry, colour, motion, the mistake the page caught in
itself, and the recorded ruling on curvature. That ruling is the same on all six and was made
on 2026-09-10 after looking at them: single-row floating housings and controls prefer capsules, with
inner geometry related to the housing and comfortable end padding; multi-row platters keep generous
rounded rectangles. Music-player and park-trails were named the most convincing pages. It is a taste
decision recorded as one, not a rule attributed to Apple.

## music-player: a desktop player, the album's artwork filling the window

**Live plane.** One viewport-fixed canvas, registered as a texture source, painting the sounding
album's artwork cover-fit, a reading wash under the tracklist and a 1 px grain, all painted into the
texture so the lens bends them. The photograph is a pale, crystalline ice field: fine grain everywhere
for the lens to displace and long cracks for it to bend. A foggy coastline that was genuinely
beautiful was rejected because its right two thirds were flat, exactly where the queue sits, and
glass over a flat field is invisible. Changing release cross-dissolves the plane over 520 ms.

**Floating inventory.** Four surfaces: the transport bar and the volume capsule on the base plane,
the queue sidebar on the base plane, the playlist platter on the overlay plane. The album identity,
the tracklist, the liner note and the credits sit on the plane with no surface at all. Queue rows,
menu rows and the play button are fills inside a glass surface, never hosts of their own.

**Groups.** Three, all reading the texture: `transport` (bar and volume in one backdrop read, because
they sit on one band of the plane 24 px apart), `queue`, and `menu` on the overlay. Every group also
declares a backdrop, `light` at a measured luminance of 0.38 or 0.34 with complexity 0.85. The first
build declared none, on the reading that a texture group lets the runtime read pixels. That is true
on the WebGPU tier and false on the CSS tier, where the same groups resolved `analysis: "none"` and
never adapted. Declaring costs the texture tier nothing and lifts the CSS tier to `hint`.

**Size family and geometry.** Thickness 8 across three rungs. The queue plate (span 328) and the menu
platter (272) take a fixed radius of 22, derived rather than chosen: the viewport edge is treated as a
macOS window corner of radius 46, every floating surface sits at the 24 px page margin, so the
concentric radius is 46 minus 24. The transport bar (span 88) is a capsule at radius 44 and the volume
(44) a capsule at 22. Inside a plate, rows inset 8 take 22 minus 8, which is 14; inside the bar, 24 px
of horizontal padding makes the 44 outer radius minus the inset equal the 40 px end buttons' own
radius of 20. Nothing in the floating layer sits below span 32, where the size law is inert.

**Colour.** A light plane, chosen against the dark player shell every streaming client ships: the
scene is a lit room in the afternoon with the player one window among several. The chrome is
monochrome slate at the photograph's own hue (250, chroma at or under 0.02), so it belongs to the
plane rather than sitting on it as foreign grey. No group carries a tint: the content layer is a
photograph, and spending the one permitted tint would put a second hue on screen for no reason a
listener could name. The single accent is a status, a port-light red meaning "sounding now", on the
scrubber's fill and on a rule beside the sounding track, never on an action or a heading. On the
0.24.0 WebGPU tier the body over this photograph carries its blue instead of a neutral grey.

**Motion.** The platter emerges from the queue's own control: one host for the pair's whole life,
whose box the page sprang from the trigger's rect on five hand-written springs. The runtime now does
that as `GlassMorph` with the matched-geometry transition, or as `present` on a host for a materialise
in place. Press is the runtime's own glow at the pointer. The plane's dissolve on a release change is
a state change; there is no idle motion, no shimmer and no drifting artwork.

**The mistake it caught.** The missing CSS-tier declaration above, found by forcing the tier with
`renderer: "css"` and looking at it rather than assuming it.

**The ruling.** The transport took fully rounded 44 px ends and 24 px of breathing room; the volume's
capsule declaration was made explicit at 22 px. The queue and the platter kept their larger-panel
geometry. Named one of the two most convincing pages.

## transit-ops: a bus network's control-room map

**Live plane.** A painted city on one fixed canvas, repainted every frame and registered as a texture
source: harbour, river, two parks and a built-density wash for the lens to bend; a 32 px graticule,
the street web at 1 px and the corridor casings for it to displace. Both frequencies live inside the
texture, never as CSS over it. The toolbar was placed over a reservoir and a canal rather than over
the empty north-west quarter of the map, which is why the canal exists at all.

**Floating inventory.** Six surfaces, read aloud: a route rack, a state rack, a search field, a view
stack and an alerts sidebar on the base plane, and a vehicle platter on the overlay plane that has no
box at all until a vehicle is selected. Alert rows, the platter's inner content and the camera plate
are tonal fills beneath the glass, one lightness step and a hairline, never hosts.

**Groups.** Six, one per surface, because each reads a different part of the plane. All read the
texture and none declares a hint, so every group resolves `analysis: "exact"` on the WebGPU tier; a
rebuild would declare the measured backdrop beside the texture for the CSS tier's sake, which is the
finding music-player made the same day (the hint lifts that tier from `none` to `hint`). None
declares a sampling padding; the runtime derived 11.9 px for the bar-rung groups, 14 px for the
platter and 28.4 px for the sidebar, and the layout keeps base-plane groups at least 48 px apart. In
React the three top controls would be one `GlassToolbar` partitioned into three groups by spacers.

**Size family and geometry.** Thickness 8 on three rungs. Span 44: the two racks and the search field
as capsules at radius 22, the view stack (44 by 140, multi-row) at a fixed 14. Span 64: the platter at
18, mid-curve of the law's 32 to 96 ramp. Span 336: the sidebar at 26, past saturation. The anchor is
the 20 px window inset against a square viewport edge, so no outer radius is inherited from a frame;
four shapes are concentric with their own housing instead: rack segment 22 minus 5, view button 14
minus 4, alert row 26 minus 10, platter action 18 minus 12.

**Colour.** A near-white neutral basemap at hue 250 and chroma at or under 0.008. The dark basemap
was the reflex answer for both a glass page and a control room, and it lost on the state ladder: five
service states must separate by lightness as well as hue, and a dark ground compresses amber, red and
blue into one narrow band. No tint and no accent: the plane already spends the page's colour on the
forty vehicle blades, and the language puts saturated colour in the content layer.

**Motion.** The plane moves because the vehicles do. The platter materialises from the blade that
opened it, a hand-animated box over 220 ms that is now `present` or a morph. Press is the runtime's
glow. The map recentres in one step rather than a timed fly, so a selection never leaves the
controller watching an animation finish. Under reduced motion the vehicles step every four seconds
instead of interpolating: reduced, not frozen, because the positions are the information.

**The mistake it caught.** The first build hid the closed platter with `visibility: hidden`. A
hidden-but-laid-out host still has a box and the renderer still draws its glass, so a 420 by 64 white
plate sat over the top-left corner of the map. A closed platter is `display: none`, or better, released
and re-registered when it opens.

**The ruling.** The three one-row top controls became capsules, the search field gaining 16 px end
padding; the view stack, sidebar and platter kept their rounded rectangles. When the view stack turns
horizontal below 1024 px it re-registers as a 22 px capsule.

## photo-review: a culling tool wrapped around one photograph

**Live plane.** One viewport canvas painting a neutral surround and then the selected frame, fit
whole, with exposure, white balance, compare state and crop already applied, so screen and texture are
the same pixels by construction. The surround is flat on purpose and no glass ever sits over it: every
floating surface is positioned inside the photograph's own rectangle and recomputed from that
rectangle at every width.

**Floating inventory.** Three surfaces on the base plane: the compare segmented control, the tool
column that grows into the adjustment platter, and the reject-rate-pick verdict bar. The overlay plane
is unused by decision: nothing overlaps anything, and the platter grows in place. The filmstrip band
and the readout column are opaque tonal planes.

**Groups.** Three, one per surface, all reading the texture and declaring no hint; a rebuild would
declare the measured backdrop beside the texture so the CSS tier adapts too. Measured gaps of 168
and 152 px at 1440 wide, far past any derived padding, recomputed from the frame's rectangle.

**Size family and geometry.** Thickness 9 on three rungs. S: the compare control at span 40, capsule
radius 20. M: the verdict bar at 56, capsule radius 28, and the tool column at rest, 56, fixed 28. L:
the open platter at 248, fixed 28, set equal to the M capsule radius so the two read as one material.
The anchor is the photograph's own rectangle at radius 0, so no surface is concentric with the plane,
and that is recorded rather than left unstated; concentricity is held one level down: platter inner 28
minus 10, verdict row 28 minus 8, compare segment 20 minus 4. Content-layer radius is 0 everywhere,
because a photograph has square corners. The morph carries one registered host from M to L, so the
size law's own behaviour, larger glass more opaque, is shown rather than described.

**Colour.** A dark achromatic surround at L* about 12, every neutral with r equal to g equal to b: any
hue in the surround biases the frame's apparent balance, which is the thing the white-balance control
exists to set. Near-black was rejected because it inflates apparent contrast and photographers flatten
their frames to compensate. No tint and no accent: a chromatic control 40 px from a skin tone shifts
how that tone is judged. The only chroma in the control layer is the white-balance ramps, where the
hue is the value being set.

**Motion.** The platter morphs and never cross-fades: one host driven from 56 to 328 px wide inside the
root's frame callback, now a morph the runtime interpolates on its own springs. The stage does not
transition between frames at all, deliberately: a photographer needs the next frame instantly.

**The mistake it caught.** Below 900 px the frame can no longer hold three separated groups, and
forcing it is exactly the proxy overlap the runtime reports, so the compare control and the platter
are released from the floating layer and re-mount as opaque controls in the band. The material's own
spacing rule decided the collapse, not a round breakpoint.

**The ruling.** The compare control took capsule ends at 20 with 16 px inner segment radii; the
verdict bar took the runtime's capsule shape to match its 28 geometry and 40 px inner buttons. The
tool column and its platter kept their 28 fixed geometry.

## film-festival: a programme page under one winter still

**Live plane.** A fixed canvas painted once per resize with the opening film's still cover-fit, a soft
light wash under the hero copy, and a 2 px monochrome grain at plus or minus 5 of 255, the film's own
medium, painted in so the lens has a high-frequency term everywhere, including the pale sky under the
bar. A scroll-edge mask on the scrolling sheet keeps the band above the bar clear at every scroll
position, so the toolbar sits on the still from first paint to the foot of the page.

**Floating inventory.** Four bar surfaces on the base plane: the masthead, the day control, the venue
button and the Book capsule. The venue menu on the overlay plane, registered when it opens and
released when it closes. The sheet beneath is printed: hairlines and whitespace, no shadow anywhere.

**Groups.** `masthead`, `filters` (day control and venue button, 28 px apart inside the group so they
do not fuse) and `book` read the texture and declare no hint, because the mask guarantees only the
still is ever behind them; a rebuild would still declare the still's measured tone beside the
texture, since the CSS tier has no pixels to read and resolves `analysis: "none"` without it.
`venuemenu` cannot make that claim, since it opens over the sheet as often as over the still, so it
samples the DOM and declares `light` at 0.80. Groups sit 96 px apart.

**Size family and geometry.** Thickness 10. Span 40: day control, venue button and Book as capsules at
radius 20. Span 68: the masthead as a capsule at 34. Span 190 and up: the platter at a fixed 28. Below
560 px the day track and masthead step to 36 and 56 and their capsule radii follow. The anchor is the
square viewport edge with the page's 80 px margin standing in for the window inset; the two concentric
shapes are the selected-day pill at 20 minus 4 and its mobile form at 18 minus 3.

**Colour.** A light ground, a blue-violet white sampled from the shaded snow in the still, so the sheet
and the film are one material world with the glass between them. Warm paper cream, the honest metaphor
for a printed programme, lost because it would fight a snow-blue frame. One tint, on Book: a print-fade
magenta that is also the page's directional accent (primary action, link, focus ring) and never a
status. The selected day is a solid ink fill, because the floating layer is monochrome but for its one
tinted primary.

**Motion.** Two moves. The venue menu materialises from the control that opened it, its box springing
to the open box over 240 ms, now a morph or `present`; press is the runtime's glow. Everything else is
a 120 ms colour or border change.

**The mistake it caught.** The scroll edge has to be a `mask-image` on the scrolling stack, a sibling
of the glass root, because on any ancestor of the root it re-roots the backdrop and demotes every
group with `probe-failed`. Its stops are measured from the bar's own box each frame, because the
desktop web has no safe-area inset and a constant typed once stops being true when the bar's height
changes. The web has no hard or soft scroll-edge primitive; the tension is recorded, not passed.

**The ruling.** Capsules on the one-row controls with their existing end padding preserved, 22 px on
the masthead and 16 on the venue control; the multi-row venue platter kept radius 28.

## park-trails: a survey sheet sliding over a mountain

**Live plane.** A fixed, full-bleed photograph of the park with a printed sheet rising over it. At
rest the glass sits over the photograph's ridge band, rock, snow and trees chosen for texture rather
than sky; once scrolled it sits over the sheet, whose contour hairline field is painted into the
sheet's own background so the lens bends it. Between the two, a mask on the sheet fades its content
across the bar's footprint.

**Floating inventory.** The trip planner platter and the permit action capsule on the base plane; the
permit platter on the overlay plane, registered when it opens with `role="dialog"` and its own name,
because a plane's DOM sits outside every landmark the page wrote. The sheet, the matrix of twelve
trails, the bulletin and the permit steps are printed and opaque.

**Groups.** Three, one per surface, and all three sample the DOM deliberately. A texture group samples
the registered pixels over the whole viewport whatever is beneath the surface, and this page's whole
composition is content sliding under the bar; a texture-backed bar would have refracted mountain over
paper. The cost is stated: `refraction: "approximate"` and `analysis: "hint"` on the WebGPU tier
instead of `"true"` and `"exact"`. Declared backdrops are measured off the plane under each box at
both phases: `bar` light 0.86, `action` mixed 0.50, `permit` mixed 0.49. The capsule is its own group
because its backdrop is a different fact from the planner's, which is legal only because 290 px
separates them.

**Size family and geometry.** Thickness 8. The action capsule at span 48, radius 24. The planner at 80,
a capsule at 40 with capsule fields inside; on a phone it becomes a 106 two-row platter at a fixed 22.
The permit platter at 424 by 344, fixed 32, rows at 32 minus 12. The anchor is the window edge at
radius 0, so the leading surface aligns to the page's 40 px margin rather than taking extra inset, and
every radius is declared by its own surface.

**Colour.** Light paper, a cool near-white with a green cast: the scene is a hiker at an information
counter at nine in the morning. The dusk-ridge dark reading was rejected because dark is where glass
is easy and would have made the page's one hard problem, a legible control layer over a bright
high-frequency backdrop, disappear instead of being solved. One tint, on the permit action: the red
plate of a quadrangle sheet, which is also the accent for focus, selection, the snow line and the
closed status.

**Motion.** The permit platter emerges from the capsule and materialises by resolving into rest, lens
channel 1 to 0 with an owned scale 0.94 to 1 over about 280 ms, now `present`; it is registered on
open and released on close so a closed platter draws nothing. No reveal-on-scroll, no parallax.

**The mistake it caught.** Measured on rendered pixels over the dark ridge, secondary ink on the permit
platter read 3.1 to 4.2 to 1. It was replaced with full ink and the key-value hierarchy moved into the
type roles. The audit's DOM pass could not see what the canvas drew, which is why a table of measured
ratios exists at all.

**The ruling.** The one-row 80 px planner took a 40 px radius with 16 px end padding and capsule
fields; the phone platter, the permit platter and the action capsule were unchanged. Named one of the
two most convincing pages. The wider ends exposed an 11.58 px planner-to-action overlap at 721 px, so
the collapse moved to 748 px, before the collision.

## product-launch: a camera's launch page on its own photography

**Live plane.** A viewport canvas painting seven same-origin photographs cover-fit, cross-dissolving
over 420 ms when the section or the configuration changes, with a warm multiply that normalises every
state's exposure so the bands under the bars land in one range and one ink passes over all seven. The
crop per state is designed so the bars stand on wood grain, knurling and coating bloom rather than an
empty corner. Choosing a finish or a lens changes the photograph the whole page stands on, and both
bars re-read their material in the same frame.

**Floating inventory.** Five surfaces: the wordmark and the section links (navigation, top) and the
configure cluster and the reserve action (bottom) on the base plane; the lens platter on the overlay
plane only while open. The sheets, tables and rules in the scrolling column are tonal and opaque.

**Groups.** `nav`, `commit` and `platter`, all reading the texture and each also declaring a measured
hint, `dark` at 0.05 with complexity 0.8, for the CSS tier's sake; the WebGPU tier reads pixels and
reports `exact` either way. Members within a bar sit 16 px apart, above the merge threshold, so the
wordmark and the section list read as two controls and the configuration and its commitment as two
acts. The platter has its own group so an unplaced platter cannot drag the bar's sampling union.

**Size family and geometry.** Thickness 8. Span 44: wordmark and section links as capsules at 22. Span
64: configure and reserve as capsules at 32. Span 268: the platter at a fixed 26. The anchor is the
viewport edge at radius 0, recorded as the web deviation it is; concentricity is held inside each
surface: section links 22 minus 6, the segmented track 32 minus 10, a segment 22 minus 3, a platter
row 26 minus 10. No control in the floating layer sits below span 32.

**Colour.** A dark ground, olive-bronze from the bloom on a coated lens element, because every
photograph the ladder returned is a low-key macro; a white page would turn them into bright rectangles
and leave the bars over a uniform field. Neutral near-black was rejected as half of the saturated
near-black-plus-hot-accent default. One tint, on reserve: an index red from the alignment dot on a
lens mount, the accent whose one job is marking the thing to press. On the 0.24.0 WebGPU tier the
body over these photographs carries their olive rather than a neutral grey of the right level.

**Motion.** The stage dissolve is a state change. The platter springs from the lens trigger over
260 ms while the lens and sweep channels rise, now a morph. Press is the runtime's glow. The system has
no idle motion and this page has none.

**The mistakes it caught.** Two, and one recorded. The reserve control drew as a flat grey slab until
the user agent's own button face was removed with `background: transparent; appearance: none`, the
single permitted background declaration on a host. A host registered before layout had settled was
reported as `same-plane-overlap` on roughly one load in eight, because it was measured while its type
metrics were still moving. And the scroll-edge fade cannot exist on this page: a viewport-following
mask must sit either on an ancestor of the root, which demotes every group, or on the column with
scroll-driven stops, where a full-page capture masks everything away. At rest no content sits under a
bar; the fade mid-scroll is lost and written down rather than passed.

**The ruling.** The wordmark, section navigation and configure bar joined the existing reserve capsule
with related inner radii; the lens platter kept its 26 geometry.

## What the six have in common

- The plane is never a wash behind a shell. It is the product: artwork, a city, a frame, a still, a
  mountain, the object being configured. Every page put structure under the glass on purpose and
  checked the empty corners before placing a surface.
- The floating inventory can be read aloud in one breath, and every item on it is navigation, an
  action or a transient platter. Everything else declares its own opaque model, tonal or printed.
- One group per backdrop fact. Texture groups let the runtime read pixels; a group over content that
  changes independently samples the DOM and declares what it measured. A declaration beside a texture
  costs the WebGPU tier nothing and is what the CSS tier adapts to.
- One thickness per page, three spans straddling the size law's 32 to 96 band, one radius per span,
  and a named concentric anchor even when the honest answer is "the viewport, radius 0".
- Three of six spent no tint at all; the three that did spent it on the primary action and nowhere
  else.
  Four of six are light. Dark was chosen twice, both times for the photographs, never for the glass.
- Nothing cross-fades between two glass surfaces. Platters emerge from the control that opened them,
  and every hand-written spring the pages carried is now `GlassMorph` or `present`.
- None of the six handled the window losing focus; since 0.18.0 the root does under
  `windowActivation: "auto"`, and since 0.22.0 the receded material it draws casts no outer shadow.
  Since 0.20.0 the shadow's blur is graded by the casting span, so a 336 px sidebar paints its shadow
  far wider than a 44 px rack does; the gap a layout owes between groups is a different quantity,
  three σ of the body's blur, and it too grows with the larger member. A rebuild would feel all three.
- Every page found a defect by looking: at the CSS tier, at rendered contrast, at a hidden host, at a
  slab where the material should be. The runtime catches nesting, overlap, tint mixing and padding; it
  does not catch a flat backdrop, a CSS overlay, an unsettled measurement or an assumed ratio.

## Record template

Write these lines down before the first host is registered: in `DESIGN.md` if the project keeps one,
in the page's own header comment or README if it does not. A reviewer should be able to check the
built page against every line, and a later agent should be able to extend the page without
re-deriving them from the render.

```
plane: <what fills the window and changes under the controls; texture or DOM; why it has both
  a broad and a fine spatial frequency where the glass sits>
inventory: <every floating surface, its plane (base | overlay) and its job; then what stays
  opaque and which model it obeys (tonal | printed)>
groups: <one line per group: id, members, texture source or DOM, declared backdrop
  { tone, luminance, complexity } measured at rest and scrolled, gap to its neighbours>
family: thickness <n> across all surfaces; <span> <radius> <capsule | fixed | concentric> per
  rung, straddling 32 to 96; anchor: <viewport edge r0 | frame radius r at margin m>; inner
  radii derived as housing radius minus inset
tint: <none, or the one surface, its seed and the job it marks>
scheme and pose: colorScheme <light | dark | auto>; windowActivation auto unless pinned, and why
motion: <what morphs (matchedGeometry | materialize), what uses present, what never moves;
  reduced-motion behaviour>
tier expectation: webgpu where the engine grants a secure context and an adapter (Chromium over
  https, localhost, or a file:// page importing from a CDN); css elsewhere and on request via
  renderer: "css"; the CSS tier is the same design without refraction
accessibility: the runtime follows the system; where Reduce Transparency cannot be queried the
  page offers the setting and passes a boolean; forced colours removes the glass and the page
  still works
contrast: labels styled on a child element, measured on rendered pixels at the plane's lightest
  and darkest phases, 4.5:1 for labels and 3:1 for large text and plates; results recorded here
```
