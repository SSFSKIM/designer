# Worked examples: six glass pages, derived

Six pages were built on the material in September 2026, three product surfaces and three narrative
pages, each from a brief that named a live plane. Their code sits on the `capsule-refinement` branch
against vitrea 0.14.0 and has not been rebuilt: the reasoning below is current, the code is not.
Where a page hand-built something the runtime now does, the sentence says so and moves on. Where a
page broke a law, putting a collection read in place on glass or declaring a backdrop its plane did
not have at every phase, the derivation below is corrected and no longer describes the page; follow
the derivation. Read these as derivations to imitate, never as tables of values to copy; every number
belongs to its photograph, its window and its brief.

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
beautiful was rejected because its right two thirds were flat, exactly where the queue's control
sits, and glass over a flat field is invisible. Changing release cross-dissolves the plane over 520 ms.

**Floating inventory.** Four surfaces: the transport bar, the volume capsule and the queue's control
on the base plane, the playlist platter on the overlay plane. The queue itself, six tracks read in
order, is content whatever the brief calls it: an opaque tonal panel floating in the right margin
over the artwork, its rows ordinary DOM, scrolling inside itself rather than growing toward the
transport. Its control is a capsule over the artwork above it, and the playlist menu opens from
that. The album identity, the tracklist, the liner note and the credits sit on the plane with no
surface at all. Menu rows and the play button are fills inside a glass surface, never hosts of
their own.

**Groups.** Three, all reading the texture: `transport` (bar and volume in one backdrop read, because
they sit on one band of the plane 24 px apart), `queue` (its control alone), and `menu` on the
overlay. None declares a backdrop where the artwork's overall level stands for the band under it,
since the runtime reads the artwork on both tiers and a declaration would override that reading on
both. A group whose band departs from it declares the composite measured under its footprint,
re-measured through each release's dissolve, never a constant.

**Size family and geometry.** Thickness 8 across three rungs: the volume and the queue's control at
span 44, capsules at 22; the transport bar at 88, a capsule at 44; the menu platter at 272, a fixed
22, derived rather than chosen: the viewport edge is treated as a macOS window corner of radius 46,
every floating surface sits at the 24 px page margin, so the concentric radius is 46 minus 24. The
opaque queue panel takes the same 22 from the same anchor, so content and control share a geometry
without sharing a material. Menu rows inset 8 take 22 minus 8, which is 14; inside the bar, 24 px of
horizontal padding makes the 44 outer radius minus the inset equal the 40 px end buttons' own radius
of 20. Nothing in the floating layer sits below span 32, where the size law is inert.

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

**The mistake it caught, and the one it made.** Forcing the CSS tier with `renderer: "css"` and
looking at it, rather than assuming it, showed every group reporting `analysis: "none"` there. The
page answered with a constant declared beside the texture, and that was the mistake: `analysis`
names where the lens's pixels come from, the runtime reads the supplied artwork on both tiers, and a
declaration overrides that reading on both, so a constant goes false the moment the release changes.
The page also put the queue on glass on the brief's word, which the layer law refuses; the
derivation above takes it off.

**The ruling.** The transport took fully rounded 44 px ends and 24 px of breathing room; the volume's
capsule declaration was made explicit at 22 px. The queue panel and the platter kept their
larger-panel geometry. Named one of the two most convincing pages.

## transit-ops: a bus network's control-room map

**Live plane.** A painted city on one fixed canvas, repainted every frame and registered as a texture
source: harbour, river, two parks and a built-density wash for the lens to bend; a 32 px graticule,
the street web at 1 px and the corridor casings for it to displace. Both frequencies live inside the
texture, never as CSS over it. The toolbar was placed over a reservoir and a canal rather than over
the empty north-west quarter of the map, which is why the canal exists at all.

**Floating inventory.** Five surfaces, read aloud: a route rack, a state rack, a search field and a
view stack on the base plane, and a vehicle platter on the overlay plane that has no box at all until
a vehicle is selected. The platter carries the selected vehicle's name and its actions. What is read
in place is content, however it floats: the six alerts are an opaque tonal panel at the map's right
edge with each alert an ordinary row, and the vehicle's facts and camera plate are an opaque panel
beside its platter. Both are one lightness step off the map and a hairline, never hosts.

**Groups.** Five, one per surface, because each reads a different part of the plane. All read the
texture. The view stack and the platter sit over land, where the near-white basemap's overall level,
which the runtime reads on both tiers, is the level under them, so they declare nothing. The top
controls stand over the reservoir and the canal, darker than the map's average, so their groups
declare the composite measured from the painted canvas under their boxes, vehicles included, on a
steady cadence and on every camera move, never after a debounce the moving map keeps resetting. None
declares a sampling padding; the runtime derived 11.9 px for the bar-rung groups and 14 px for the
platter, and the layout keeps base-plane groups at least 48 px apart. In React the three top
controls would be one `GlassToolbar` partitioned into three groups by spacers.

**Size family and geometry.** Thickness 8 on two rungs. Span 44: the two racks and the search field
as capsules at radius 22, the view stack (44 by 140, multi-row) at a fixed 14. Span 64: the platter at
18, mid-curve of the law's 32 to 96 ramp. The alerts panel was the family's top rung while it was
glass; as content it keeps its radius of 26 and the glass family stops inside the band, which the
record states, because a family is never completed by putting glass where the layer law refuses it.
The anchor is the 20 px window inset against a square viewport edge, so no outer radius is
inherited from a frame; three shapes are concentric with their own housing instead: rack segment 22
minus 5, view button 14 minus 4, platter action 18 minus 12.

**Colour.** A near-white neutral basemap at hue 250 and chroma at or under 0.008. The dark basemap
was the reflex answer for both a glass page and a control room, and it lost on the state ladder: five
service states must separate by lightness as well as hue, and a dark ground compresses amber, red and
blue into one narrow band. No tint and no accent: the plane already spends the page's colour on the
forty vehicle blades, and the language puts saturated colour in the content layer.

**Motion.** The plane moves because the vehicles do. The platter materialises from the blade that
opened it, a hand-animated box over 220 ms that is now `present` or a morph. Press is the runtime's
glow. The map recentres in one step rather than a timed fly, so a selection never leaves the
controller watching an animation finish. Under reduced motion the vehicles step every four seconds
instead of interpolating, switching as the preference changes: reduced, not frozen, because the
positions are the information.

**The mistake it caught.** The first build hid the closed platter with `visibility: hidden`. A
hidden-but-laid-out host still has a box and the renderer still draws its glass, so a 420 by 64 white
plate sat over the top-left corner of the map. A closed platter is absent through `present`, keeping a
real box and its last content through the exit, or it is not registered at all; `visibility` is not a
material state.

**The ruling.** The three one-row top controls became capsules, the search field gaining 16 px end
padding; the view stack, the platter and the alerts panel kept their rounded rectangles. When the
view stack turns horizontal below 1024 px it re-registers as a 22 px capsule.

## photo-review: a culling tool wrapped around one photograph

**Live plane.** One viewport canvas painting a neutral surround and then the selected frame, fit
whole, with exposure, white balance, compare state and crop already applied, so screen and texture are
the same pixels by construction. The surround is flat on purpose and no glass ever sits over it: every
floating surface is positioned inside the photograph's own rectangle, at its margins where it covers
least of what is being judged, and recomputed from that rectangle at every width. The frame is the
live plane rather than reading content, so the controls sit over it at rest by design. It is also
content the page must show as it is, and some frames go flat under a control, a sky or a studio
sweep: the control stays where it is and its edge and shadow carry it, the frame is never altered
and nothing moves per frame, and the record lists those frames.

**Floating inventory.** Three surfaces on the base plane: the compare segmented control, the tool
column that grows into the adjustment platter, and the reject-rate-pick verdict bar. The overlay plane
is unused by decision: nothing overlaps anything, and the platter grows in place. The filmstrip band
and the readout column are opaque tonal planes.

**Groups.** Three, one per surface, all reading the texture and declaring nothing: the runtime reads
the frame on both tiers, and a constant would describe one frame of thirty. A surface whose band
departs from the frame's overall level declares what is painted under the box the morph actually
drew, which after a resize with the platter open is not the box the page intended. Measured gaps of
168 and 152 px at 1440 wide, far past any derived padding, recomputed from the frame's rectangle.

**Size family and geometry.** Thickness 9 on three rungs. S: the compare control at span 40, capsule
radius 20. M: the verdict bar and the tool column at rest, both capsules at 28, half the 56 each box
measures; the column is the closed end of a morph, which takes only a fixed radius, so its 28 is
derived from the closed box's measured span rather than typed. L: the open platter at 248, fixed 28,
equal to the closed capsule's radius so the two read as one material. The anchor is the photograph's
own rectangle at radius 0, so no surface is concentric with the plane, and that is recorded rather
than left unstated; concentricity is held one level down: platter inner 28 minus 10, verdict row 28
minus 8, compare segment 20 minus 4. Content-layer radius is 0 everywhere, because a photograph has
square corners. The morph carries one registered host from M to L, so the size law's own behaviour,
larger glass more opaque, is shown rather than described.

**Colour.** A dark achromatic surround at L* about 12, every neutral with r equal to g equal to b: any
hue in the surround biases the frame's apparent balance, which is the thing the white-balance control
exists to set. Near-black was rejected because it inflates apparent contrast and photographers flatten
their frames to compensate. No tint and no accent: a chromatic control 40 px from a skin tone shifts
how that tone is judged. The only chroma in the control layer is the white-balance ramps, where the
hue is the value being set.

**Motion.** The platter morphs and never cross-fades: one host driven from 56 to 328 px wide inside the
root's frame callback, now a morph the runtime interpolates on its own springs. Open, its host is
not interactive, so a press on one of its plain controls presses the platter through the host's
channels, glowing from the contact point, rather than going without press or swapping a colour. The
stage does not transition between frames at all, deliberately: a photographer needs the next frame
instantly.

**The mistake it caught.** Below 900 px the frame can no longer hold three separated groups, and
forcing it is exactly the proxy overlap the runtime reports, so the compare control and the platter
are released from the floating layer and re-mount as opaque controls in the band. The material's own
spacing rule decided the collapse, not a round breakpoint.

**The ruling.** The compare control took capsule ends at 20 with 16 px inner segment radii; the
verdict bar took the runtime's capsule shape to match its 28 geometry and 40 px inner buttons. The
tool column's 28 is its capsule radius, and the platter kept its fixed 28.

## film-festival: a programme page under one winter still

**Live plane.** A fixed canvas painted once per resize with the opening film's still cover-fit, a soft
light wash under the hero copy, and a 2 px monochrome grain at plus or minus 5 of 255, the film's own
medium, painted in so the lens has a high-frequency term everywhere, including the pale sky under the
bar. A scroll-edge mask on the scrolling sheet keeps the band above the bar clear at every scroll
position, so the toolbar sits on the still from first paint to the foot of the page.

**Floating inventory.** Four bar surfaces on the base plane: the masthead, the day control, the venue
button and the Book capsule. The venue menu on the overlay plane, a platter of choices that emerges
from the venue button. The sheet beneath is printed: hairlines and whitespace, no shadow anywhere.

**Groups.** `masthead`, `filters` (day control and venue button, 28 px apart inside the group so
they do not fuse) and `book` read the texture. The mask guarantees only the still is ever behind
them, which settles where the pixels come from and not whether the pale sky band under the bar
matches the still's overall level, the one tone the runtime reads for a group in the active pose; so
each group declares nothing only where the level measured under its footprint matches that average,
and otherwise declares the measured band, recomputed whenever the crop or the layout moves, never a
number taken at one window size. `venuemenu` opens over the still, the gradient and the sheet, so it
samples the DOM and declares the composite measured under its footprint, re-measured on a cadence
and on every layout change while it is open, never the paper's colour alone. Groups sit 96 px apart.

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

**Floating inventory.** The trip planner platter and the permit action capsule on the base plane;
the permit platter on the overlay plane, registered when it opens with `role="dialog"` and its own
name, because a plane's DOM sits outside every landmark the page wrote. The planner's route,
distance and weather fields are choices; the forecast the weather field answers with is content,
printed on the sheet with the conditions, and choosing a day takes the reader there and leaves focus
on it. The permit platter holds the permit's choices and its action; a short status or a choice's
secondary text does not change its role, while a read-only collection or panel would be content. The
sheet, the matrix of twelve trails, the bulletin and the permit steps are printed and opaque.

**Groups.** Three, one per surface, and all three sample the DOM deliberately. A texture group samples
the registered pixels over the whole viewport whatever is beneath the surface, and this page's whole
composition is content sliding under the bar; a texture-backed bar would have refracted mountain over
paper. The cost is stated: `refraction: "approximate"` and `analysis: "hint"` on the WebGPU tier
instead of `"true"` and `"exact"`. Each declared backdrop is the composite under its own box, the
photograph at rest and the sheet with its ink and fills once scrolled, not the paper's colour alone,
re-measured as the sheet passes under. The capsule is its own group because its backdrop is a
different fact from the planner's, which is legal only because 290 px separates them.

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
channel 1 to 0 with an owned scale 0.94 to 1 over about 280 ms, now `present` or a morph from the
capsule; closed, it draws nothing and is never an empty box. No reveal-on-scroll, no parallax.

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

**Groups.** `nav`, `commit` and `platter`, all reading the texture. The runtime reads the painted
plane on both tiers through every dissolve, so a declaration, which would override it, is made only
where a bar's band departs from the photograph's overall level, and then measured from the painted
mix, never from the destination photograph. Members within a bar sit 16 px apart, above the merge
threshold, so the wordmark and the section list read as two controls and the configuration and its
commitment as two acts. The platter has its own group so an unplaced platter cannot drag the bar's
sampling union.

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
  action or a transient platter. Everything else declares its own opaque model, tonal or printed,
  including a collection the brief asked to float, which floats as an opaque panel.
- One group per backdrop fact. Texture groups let the runtime read pixels on both tiers; a group over
  content that changes independently samples the DOM and declares what it measured, phase by phase.
  A declaration overrides the pixels on either tier, so it is made only where it is truer than the
  runtime's own reading, and kept true as the plane moves.
- One thickness per page, spans across the size law's 32 to 96 band as far as the controls reach it,
  one radius per span, and a named concentric anchor even when the honest answer is "the viewport,
  radius 0".
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
  a broad and a fine spatial frequency where the glass sits; any phases where content shown as it
  is goes flat under a control>
inventory: <every floating surface, its plane (base | overlay) and its job; then what stays
  opaque and which model it obeys (tonal | printed), including any content panel that floats>
groups: <one line per group: id, members, texture source or DOM, gap to its neighbours; declared
  backdrop { tone, luminance, complexity } and how it is measured from the displayed composite
  and re-measured (cadence, layout change, transition), or none and why the runtime's reading holds>
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
  page offers the setting and passes a boolean; forced colours removes the glass and every
  authored mark (track, switch, selection) still shows; page-owned motion follows Reduce Motion
contrast: labels styled on a child element, measured on rendered pixels at the plane's lightest
  and darkest phases, 4.5:1 for labels and 3:1 for large text and plates; every reading recorded
  here per label and icon, per scheme, at rest, scrolled and receded, and one under the floor
  stated as a failure
```
