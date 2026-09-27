# Exhibition: *Weather in Painting*, the online viewing room

The record the materialist skill asks for (`skills/materialist/SKILL.md`, the template in
`references/examples.md`). Part one was written before the first glass host was registered; part
two records what building and measuring changed. A reviewer should be able to check the built
page against every line of part one, and part two says where the page departed from it and why.

## Part one: the derivation, before any host

**register:** spatial. The person is not acting on the painting with a few controls; they are
reading a gallery label beside the thing it describes, which is the case the skill's decision
function names for the spatial register ("a guide or label beside the thing it describes"). The
world is the painting and the interface is one window set into it. The instrument reading was
considered and refused: it would put the label essay on the plane, and a label printed over a
Van Gogh is either illegible or a panel that hides the work. The page is derived from the ten
spatial conditions, not from the instrument register's step 1.

**The product and who it is for.** The online viewing room of a museum exhibition, *Weather in
Painting*: eight public-domain works, one at a time, each filling the screen. The visitor looks
at the work and reads (or hears) its label without leaving it. The exhibition's argument is
chronological: from a Dutch winter in the Little Ice Age (Avercamp, c. 1608) to a London fog
that was largely coal smoke (Monet, 1900), the sky moving from backdrop to subject.

**environment:** one product-owned, full-bleed, viewport-fixed `<canvas>`, painted at its own
box size in device pixels and registered as the texture source `environment`, so the lens bends
the painting's real pixels and paint and sample agree exactly (the cookbook's §2 exact case).
It paints the current work cover-fit with a per-work vertical focus; every work is landscape,
so the crop is always top/bottom and never horizontal. Both spatial frequencies come from the
painting itself: composition (sky, horizon, a bridge, a wave) is the broad term and brushwork,
craquelure and figures are the fine term, painted into the texture, never laid over it in CSS.
Phases are the eight works (`frost`, `cloud`, `clearing`, `thunder`, `rain`, `wind`, `gale`,
`fog`). A change of work is a state change of the environment: a canvas cross-dissolve of about
0.7 s (instant under Reduce Motion and for `setPhase`), never the glass moving.
Grading, per condition 1 and the dead band: a painting is content shown as it is, so the page
does not regrade the work where it is seen. It grades only UNDER the glass footprints, a wash
painted into the canvas inside each host's rounded box: toward a warm label-card white in the
light scheme and toward a deep neutral in the dark, strongest behind the text and falling off
toward the rim so the edge still has the painting's structure to bend ("keep the area behind
text calmer than the rim"). Its strength is solved per work and per scheme from the painted
pixels, so a painting already in range is barely touched, and it is capped so the field under
the glass never goes flat. Outside the footprints the painting is untouched.
Measurement, kept as three separate quantities: (1) the source statistics (the whole canvas's
encoded Rec709 mean), (2) the tone input each group declares, the encoded-luma mean measured
under that group's own rounded footprint on the painted (washed) canvas and decoded once, the
same statistic the runtime's silhouette reading uses, re-measured every frame of a dissolve and
on every resize, scheme change and layout change, and (3) the drawn surface level behind each
text line, read from rendered pixels. Only (3) gates contrast. The whole-source average is not
used as the window's tone because the window covers a graded part of the plane.
Phases where the plane is locally soft: `fog` (Monet's London haze is low-contrast by
subject) and parts of `thunder` (Heade's black sky and water). Neither is altered for the glass;
the rim and the shadow carry the surfaces there, and the record lists the readings.

**windows:** at rest, one window and two ornaments; nothing else is glass.
- `label` (**window**), base plane, `<section aria-label>` registered with `GlassSurface asChild`,
  at the viewport's left edge (every work's subject that the eye goes to first, Caillebotte's
  couple, Ruisdael's mill, Van Gogh's cypresses, Heade's watcher, Cole's valley, sits right of
  centre; a left window covers the least of them). About 32vw wide (clamped 400 to 468 CSS px),
  full height between the 32 px margin and the ornament row: span well above 96. It holds two
  views of one task, reading the exhibition: the **Label** (room and weather, title, maker, date,
  the whole work in an opaque frame with the detail on screen outlined, the essay, the work's
  data) and the **Rooms** (the exhibition's introduction, the eight rooms as a list, and the
  viewing-room setting for Reduce Transparency). The host is still; a child scroller scrolls
  with scroll edges at its inner top and bottom only where content passes under them.
- `rooms` (**ornament**), overlay plane, attached below the window's bottom edge at its leading
  side: previous room, the room index (`4 / 8`, which opens the Rooms view in the window), next
  room. Plain buttons on its glass.
- `guide` (**ornament**), overlay plane, attached below the window's bottom edge at its trailing
  side: the audio guide's transport, play or pause and the stop's name and length. The guide
  reads the label aloud with the browser's own speech synthesis (no audio files), and underlines
  the sentence being read; where the browser has no voice the control says so and is disabled.
- No platter: the list of rooms is a collection read in place, so it is window content ("lists,
  collections and sections belong in windows"), not a transient platter. `openMenu` is therefore
  absent from `__glassDemo`, by decision.
- Both ornaments sit OUTSIDE the window by the runtime-derived gap (texture path; they sample the
  environment, not the window's glass), are together no wider than the window, and are spaced
  from each other by the same derivation. The painting is visible around every surface.

**groups:** one per surface, all on the texture `environment`, all with a declared hint:
- `label-window`: the window. Hint `{ tone, luminance }` measured under the window's rounded
  footprint on the painted canvas (encoded-luma mean decoded once), every dissolve frame and on
  every layout or scheme change. No `complexity`: the runtime reads none, and a number on a
  scale nothing defines would be invented; the luma deviation is kept for the record instead.
- `rooms-ornament`, `guide-ornament`: the same measurement under each ornament's own box.
- Gaps: window to ornament row, and ornament to ornament, are `ceil(max(24, samplingPaddingFor
  (each group's measured box, resolved policy, the selected document's active endpoint for the
  resolved scheme)))`, the advisory 24 being core's descriptor floor; recomputed with geometry,
  scheme and Reduce Transparency. No `samplingPadding` is pinned.

**family:** thickness 8 across all three surfaces (no reason to leave the reference). Window:
fixed radius 32, the generous window corner. Ornaments: 52 tall capsules, radius 26; their
inner buttons 44 tall, radius 22 = 26 minus the 4 px inset. Anchor: the window corner, r 32;
inner fills derive from it: the data section's darker fill inset 14 from the window edge takes
32 minus 14 = 18; the whole-work frame and list rows at the 28 px content inset take 32 minus 28
= 4. The page's outer frame is the square viewport edge at a 32 px margin.

**tint:** none. The environment is eight paintings; every colour on screen is theirs, and any
control colour would compete with a Caillebotte grey or a Van Gogh blue for no reason a visitor
could name. The tint budget is spent by not spending it.

**scheme and pose:** `colorScheme="auto"`; the page's tokens follow `prefers-color-scheme`. The
light scheme is a daylit gallery (label-card white under the glass), the dark an evening viewing
room (deep neutral under the glass); the environment's wash is graded per scheme, which is how
the dark material over bright paintings (Homer's spray, Monet's fog) is kept out of the ink's
dead band. `windowActivation` is left on `auto`: the receded pose is a state of the design.

**motion:** nothing morphs and nothing materialises after mount. The window and ornaments are
still. The environment dissolves between works over about 0.7 s, stepped from `root.subscribe`
(no second rAF loop); the label content changes at once and its scroller returns to the top.
The runtime's press is the only glass motion. Under Reduce Motion, read live from the resolved
policy, the dissolve is a cut and the guide's follow-along scrolling is instant.

**tier expectation:** webgpu where the engine grants a secure context and an adapter (the dev
server on localhost in Chromium); css elsewhere and on request via `?tier=css`, the same design
without refraction and without hue retention. The CSS root's body form depends on the summed
present-host area: at DPR 1 the window plus ornaments is about 0.33 M device px (two-layer), at
DPR 2 about 1.3 M (collapsed); part two records the `cssBody` actually read.

**accessibility:** the runtime follows the system for motion and contrast. Reduce Transparency
is the page's own setting in the Rooms view, initialised from `prefers-reduced-transparency`
where the engine answers it and from a stored preference otherwise, and always passed to the
root as a boolean. Forced colours removes the glass; the page's authored marks (the data
section's fill, the selected room, the whole-work outline, the switch, the spoken-sentence
underline, focus rings) are drawn so each survives substitution as a system-colour border or
decoration. Labels are real DOM: `<button>`s, a `<nav>`, a named region for the window, the
painting's canvas as `role="img"` named for the work. Left and right arrow keys also move
between rooms.

**contrast:** every text line on glass is styled on a child with the runtime's ink (primary for
reading text and controls, secondary for descriptions; tertiary and quaternary only for rules),
medium to bold weights with slightly opened tracking. It is measured per rendered line on
rendered pixels (the computed ink composited over the text-hidden capture of the same frame,
per pixel, median and adverse tail), in both schemes, at all eight phases, active and receded,
at rest and scrolled, at 4.5:1 for body and labels and 3:1 for large text; the worst line gates
and every failing line is written down in part two. If a line cannot pass on the published ink
after grading, the page authors ink on that child rather than falsifying a hint.

**fidelity:** Apple's macOS 27 material composed in Apple's visionOS way: a window with
ornaments at its edge, Apple-shaped at window scale, not visionOS glass. The window's span
(about 400 to 470 by 700 to 800 CSS px) is beyond the bed's largest scene (span 160), so its
scatter, shadow amplitude and shadow blur are the fitted laws extrapolated, not calibration.
Regular variant only; no clear, no dimming layer. Nearest Apple surface: a visionOS window with
a bottom toolbar ornament (for example the Photos or TV app's window over an environment);
no native capture of it is available to this page, so no side-by-side comparison was made.

## Part two: what building and measuring changed

Everything below was read from the running page (`http://localhost:5187/gallery/exhibition/`,
Chromium with `channel: "chromium"` on a real adapter unless the line says CSS tier), 2026-09-27.

**What drew.** All three groups resolve `activeRenderer: webgpu`, `samplingBackend: gpu-texture`,
`refraction: true`, `analysis: exact`, `health: ok` on the GPU tier; on `?tier=css` all three
resolve `css`, `css-backdrop`, `refraction: none`, `analysis: hint`, `health: ok`. The texture is
the in-document canvas, placed on its own box; no `backdrop-texture-unplaced`.

**The wash became a solve, not a table.** Part one planned a per-work, per-scheme grade. The first
build painted a fixed 0.55 under every footprint, and the measurement showed both ways it was wrong:
in the light scheme the window bodies read 0.79 to 0.97 (the painting nearly gone under a white
card, far more grade than legibility needed), while in the dark scheme the two ornaments over
Avercamp's bright ice read 0.43 to 0.45, inside the dead band, at 3.7 to 3.9:1. The painter now
reads the painting's own mean under each footprint and paints just enough wash to bring it to a
target (light: painted mean at least 0.50 for every surface; dark: at most 0.20 under the window and
0.16 under the ornaments, which sit over brighter paint and draw lighter at their span), floored at
0.12 so the text area is always calmer than the rim and capped at 0.82 so the field never goes flat,
falling to 35 % of its strength at the footprint's edge. The targets are the fitted part: the
painted levels at which every drawn body measured clear of the dead band with margin in both poses.
Because the solve runs on whatever is painted, it holds through a dissolve and at any viewport, not
only at eight works at one size. Drawn bodies behind text, all phases, both poses, both views: light
scheme 0.66 to 0.95 (encoded), dark scheme 0.13 to 0.37, all outside the 0.39 to 0.49 dead band. The
light glass now carries the painting's colour (Van Gogh's blue, Cole's gold) instead of reading as a
label card.

**Environment statistics, three quantities kept apart** (1440 × 900, active pose). Whole canvas:
the painted source's encoded-luma mean. Per group: the painting's mean under the footprint before
the wash → after it (the solved strength s, the luma deviation left under the glass) · the
declared tone and linear luminance. The drawn body behind each text line is the `surface` column
of `CONTRAST.md`.

| scheme | phase | whole canvas | label-window | rooms-ornament | guide-ornament |
|---|---|---|---|---|---|
| light | frost | 0.610 | 0.593 → 0.617 (s 0.12, sd 0.174) · light 0.339 | 0.679 → 0.693 (s 0.12, sd 0.148) · light 0.438 | 0.725 → 0.734 (s 0.12, sd 0.153) · light 0.498 |
| light | cloud | 0.420 | 0.489 → 0.523 (s 0.12, sd 0.102) · light 0.236 | 0.409 → 0.473 (s 0.17, sd 0.034) · dark 0.19 | 0.369 → 0.463 (s 0.22, sd 0.066) · dark 0.181 |
| light | clearing | 0.454 | 0.246 → 0.473 (s 0.36, sd 0.067) · dark 0.19 | 0.150 → 0.411 (s 0.44, sd 0.094) · dark 0.141 | 0.218 → 0.429 (s 0.38, sd 0.109) · dark 0.154 |
| light | thunder | 0.318 | 0.221 → 0.464 (s 0.38, sd 0.090) · dark 0.183 | 0.508 → 0.537 (s 0.12, sd 0.122) · light 0.25 | 0.564 → 0.586 (s 0.12, sd 0.109) · light 0.303 |
| light | rain | 0.469 | 0.583 → 0.608 (s 0.12, sd 0.133) · light 0.328 | 0.510 → 0.538 (s 0.12, sd 0.082) · light 0.251 | 0.614 → 0.634 (s 0.12, sd 0.060) · light 0.36 |
| light | wind | 0.497 | 0.547 → 0.576 (s 0.12, sd 0.102) · light 0.291 | 0.535 → 0.560 (s 0.12, sd 0.053) · light 0.274 | 0.510 → 0.538 (s 0.12, sd 0.058) · light 0.251 |
| light | gale | 0.482 | 0.585 → 0.609 (s 0.12, sd 0.220) · light 0.329 | 0.191 → 0.421 (s 0.41, sd 0.085) · dark 0.148 | 0.133 → 0.418 (s 0.45, sd 0.088) · dark 0.146 |
| light | fog | 0.479 | 0.479 → 0.516 (s 0.12, sd 0.069) · light 0.229 | 0.469 → 0.501 (s 0.12, sd 0.028) · light 0.215 | 0.428 → 0.472 (s 0.14, sd 0.025) · dark 0.189 |
| dark | frost | 0.499 | 0.593 → 0.212 (s 0.74, sd 0.093) · dark 0.037 | 0.679 → 0.264 (s 0.82, sd 0.138) · dark 0.057 | 0.727 → 0.268 (s 0.82, sd 0.130) · dark 0.058 |
| dark | cloud | 0.334 | 0.489 → 0.204 (s 0.68, sd 0.061) · dark 0.034 | 0.409 → 0.198 (s 0.72, sd 0.069) · dark 0.032 | 0.368 → 0.184 (s 0.69, sd 0.060) · dark 0.028 |
| dark | clearing | 0.373 | 0.246 → 0.174 (s 0.25, sd 0.069) · dark 0.026 | 0.150 → 0.119 (s 0.12, sd 0.053) · dark 0.013 | 0.220 → 0.152 (s 0.39, sd 0.081) · dark 0.02 |
| dark | thunder | 0.238 | 0.221 → 0.172 (s 0.14, sd 0.111) · dark 0.025 | 0.508 → 0.227 (s 0.79, sd 0.122) · dark 0.042 | 0.564 → 0.218 (s 0.81, sd 0.100) · dark 0.039 |
| dark | rain | 0.361 | 0.583 → 0.210 (s 0.74, sd 0.079) · dark 0.036 | 0.510 → 0.218 (s 0.79, sd 0.094) · dark 0.039 | 0.614 → 0.239 (s 0.82, sd 0.111) · dark 0.046 |
| dark | wind | 0.398 | 0.547 → 0.212 (s 0.72, sd 0.072) · dark 0.037 | 0.535 → 0.222 (s 0.80, sd 0.097) · dark 0.04 | 0.510 → 0.215 (s 0.79, sd 0.091) · dark 0.038 |
| dark | gale | 0.374 | 0.585 → 0.206 (s 0.74, sd 0.091) · dark 0.035 | 0.191 → 0.140 (s 0.24, sd 0.046) · dark 0.017 | 0.131 → 0.100 (s 0.12, sd 0.065) · dark 0.01 |
| dark | fog | 0.396 | 0.479 → 0.207 (s 0.67, sd 0.059) · dark 0.035 | 0.469 → 0.211 (s 0.77, sd 0.081) · dark 0.037 | 0.428 → 0.195 (s 0.74, sd 0.067) · dark 0.032 |

**The secondary ink was dropped for reading text.** The runtime solves the secondary to exactly
4.5 against its own model of the surface; on this plane's rendered pixels, in the first full pass,
115 of the 237 lines that carried it read below 4.5 (4.19 at worst), most of them the data list's
labels on its darker fill and the dark window's secondary lines where the rendered body sat a few
codes lighter than the model. Every readable line now takes the primary token, and hierarchy
moved into size, weight and case, as on a printed museum label. Tertiary remains only on rules and
the guide's ring track; quaternary is never named (it would report against the span-52 ornaments).

**Contrast, on rendered pixels: no line under its floor.** Every text line and ornament icon on
the glass, read per rendered line with the method in `CONTRAST.md` (computed ink composited per
pixel over the text-hidden capture of the same frame; the adverse 10th percentile gates):

| pass | readings | under floor | worst p10 (where) |
|---|---|---|---|
| GPU, 8 phases × 2 schemes × active and receded × label (every scroll step) and rooms views | 3,756 | 0 | 4.93 (dark, rooms view, the current room's row on its lifted fill) |
| GPU, label view, window lines (titles, essay, data) | 1,332 | 0 | 6.34 dark active, 6.72 dark receded, 8.78 light active, 7.36 light receded |
| GPU, ornament labels and icons | 216 | 0 | 5.44 (dark, `frost`, over Avercamp's ice, wash at its ceiling) |
| CSS tier, DPR 1 (`two-layer`), active, both views | 1,916 | 0 | 4.95 (dark, rooms view, current row) |
| CSS tier, DPR 2 (`collapsed`), active, label view | 812 | 0 | 5.32 (dark, `frost`, guide ornament) |
| GPU with Reduce Transparency on, active, label view | 861 | 0 | 7.28 (dark, `frost`) |

The narrowest margin on the page is the dark scheme's lifted fill behind the current room's row
(white 12 % over a body of 0.36): 4.93 to 5.0 in every phase, kept because the selection must read
as lifted on a dark body, and recorded here as the line to watch. The full per-line table, every
phase, scheme, pose and view, is `CONTRAST.md` beside this file.

**The fills follow the drawn body, not the hint's tone.** The declared tone is a statement about
the backdrop, cut at an encoded 0.5; in the light scheme several backdrops read 0.41 to 0.49 under
a body that draws at 0.66 or more, so a fill keyed on the tone would have put a lighter fill on a
light body. `data-ground` and the hosts' `color-scheme` follow the scheme, which the measurement
shows is the body's half in every phase and pose.

**Hint without complexity.** The runtime consumes no `complexity`; the hint carries tone and
luminance only, and the deviation is kept in the statistics above.

**The gaps the runtime derived.** At 1440 × 900 the window (461 × 720) asks for a sampling padding
that rounds up to 64 CSS px, so the ornament row hangs 64 px below the window; the two ornaments are
24 px apart (core's advisory floor is larger than their own 3σ). Under Reduce Transparency the frost
thickens and the gaps become 77 and 49; the guide narrows to keep the row within the window. At
1280 × 720 the window is 410 × 541. This is the one place the page reads less like visionOS than
part one hoped: a visionOS ornament overlaps its window's edge, and on the texture path an ornament
may not, so the row reads as attached by alignment (it spans exactly the window's width, flush with
both its edges) rather than by contact. Recorded, not worked around: pinning a smaller padding
would stop following the blur.

**The audio guide.** macOS Chromium exposes the system voices, so the guide plays, underlines the
sentence it is reading and scrolls the window's own scroller to keep it in view (instantly under
Reduce Motion). Its transport first showed an estimated elapsed time; it now shows the estimate only
before playing ("About 0:49") and, once playing, the real listening time and the ring's progress
through the text by character, which the synthesiser reports.

**The audit contract.** `window.__vitrea` and `__glassDemo` are published only once all three
groups are registered, so an instrument that reads the root two frames after it appears reads the
composed page. `setPhase` cuts to the work and leaves the window's view as it was;
`setReducedTransparency` is a capture's statement and is not remembered, where the Rooms view's
switch is the visitor's choice and is.

**Diagnostics: zero.** Both channels (`root.diagnostics`, `root.scene.diagnostics`), both schemes,
GPU and CSS tiers, after load and after each of: three dissolves in a row, a dissolve interrupted
mid-way, the Rooms view, choosing a room, arrow keys, Reduce Transparency on and off from the
switch, resizing to 1280 × 720 and 1600 × 1000, a scheme flip, the receded pose and back, scrolling,
playing and pausing the guide. No console error or warning from the page.

**Mechanical ban subset.** No backdrop-filter, box-shadow, border or background authored on a host
(the hosts' rules set position, box, font and custom properties only); no host carries a list,
listitem, row, table or article role (`section`, `nav`, `div role="group"`); no tint; no opacity
transition anywhere; nothing on `html` or `body` (the root's container) beyond overflow and a
background colour; spans 461 and 52; the window at or above 96; zero diagnostics.

**CSS tier.** `cssBody` read `two-layer` at DPR 1 (present CSS hosts 461 × 720 + 176 × 52 + 261 ×
52, about 0.355 M device px, under the 400,000 budget) and `collapsed` at DPR 2 (about 1.42 M). Both
forms inspected: two-layer keeps the painting's structure visible through the frost; collapsed is
flatter and a little warmer, the Van Gogh's strokes reduced to soft colour under the text. Same
layout, same hierarchy, no refraction and no hue retention, as designed.

**Forced colours.** The runtime removes the glass and draws Canvas panels; the page's marks survive
as system colours: the data section's and the selected room's borders, the selected index button's
border, the whole-work outline in Highlight, the switch in CanvasText and Highlight, the guide's
ring in GrayText and CanvasText, the spoken sentence's underline. Every ornament button also shows
its (normally transparent) border as CanvasText, a conventional high-contrast affordance that was
kept. The layout reflows because the material's padding shrinks with the glass gone.

**Receded pose.** Left on `auto`. Unfocused, the bodies darken (light scheme 0.66 to 0.91 behind
text), the shadow stops, the rim collapses; every line still passes (worst 7.36 light, 6.72 dark on
the label, 5.23 dark on the rooms view's lifted row).

**Flat phase.** `fog`: under the two ornaments Monet's water and haze leave a painted luma deviation
of about 0.03, so the rim has little to bend there and the shadow and edge carry the ornaments.
Content shown as it is; not altered.

**Geometry as built.** As part one, with one change: the rooms list's rows moved out to the data
section's inset (14 from the window edge, radius 18 = 32 − 14) so a row's lifted fill and the data
fill share one radius; the rows' thumbnails, 12 inside them, take 6. The whole-work frame stays at
the 28 inset, radius 4. The ornaments' inner buttons are 44 tall at radius 22 in 52-tall capsules.
The guide gained a third control beside play and pause, start the stop again, disabled at the start.

**The eye (check 20).** No native capture of a visionOS window with ornaments is available here, so
no side-by-side comparison was made. What the eye sees that the checks do not: at thickness 8 and
span 461 the window's refraction is a narrow band at the edge, and the body reads as frost rather
than as a thick lens; in the dark scheme over a bright painting (Avercamp, Homer's spray) the window
reads as a smoked slab, which is the measured dark material over white (its response at white is a
dark grey) plus the grade, and is the evening room part one asked for, but it hides more of the
painting than the light scheme does; and the 64 px ornament gap above.

**Commands** (after the last change). `pnpm --filter demo lint`: exit 0 (eslint, tsc, tsc over
the e2e project). `pnpm --filter demo build`: exit 0. `pnpm --filter demo test:e2e
e2e/gallery.spec.ts`: 16 passed, the exhibition's light and dark cases among them.
