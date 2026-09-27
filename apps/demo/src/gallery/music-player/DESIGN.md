# Music player: the record

A desktop music player for a streaming service's Mac web client (the service is called Fathom
here), built under the materialist skill on `@vitreajs/vitrea-react` 0.24.0 from the workspace
source. Part one, the derivation and the record lines, was written before the first host was
registered. Part two, what the runtime resolved and what the eye saw, was added after running it.
An independent review then returned six findings, the first of them that the queue was content on
glass; both parts were revised with the fixes, so every line below describes the page as it now
is, and the findings and what each changed close part two.

## Part one: the derivation, before any host

### The scene and the ground

The listener is at a desk in daylight, the player one window among several, the album left running
while they work. So the page is light by default, and it follows the system into dark at night,
where the artwork is dimmed the way a room's lamp dims a print rather than being replaced by a
black shell. Both schemes are designed states; the root is `colorScheme="auto"` and the plane is
repainted per scheme.

### Is glass earned?

Yes, and by the product's own nature: a player's controls sit over artwork that changes when the
sounding release changes, and the transparency keeps the listener in the record while they skip,
scrub or queue. This is the first case the skill's derivation names.

### The plane

One viewport-fixed `<canvas>`, painted at the viewport's device-pixel size and registered as the
texture source `artwork` for every group, so the lens bends real pixels on the GPU tier and the
element shows exactly the pixels the texture holds (the canvas is painted at its own box, so there
is no crop/stretch disagreement). Painted into it, in order:

1. The sounding release's artwork, cover-fit. The album is *Pressure Ridge*, whose sleeve is
   `icehouse.jpg` (Abby Santurbane): cracked lake ice from directly above. It carries both
   frequencies across the whole frame: crack lines from a few pixels to half the frame for the
   lens to bend, and trapped bubbles of two to six pixels for it to displace. There is no empty
   corner in it, which is why it is the plane.
2. In dark, the artwork multiplied down to roughly 40 % so the window reads as a dark room with
   the sleeve in it.
3. A reading wash on the left, under the album column, painted in the texture (so the lens bends
   it, and so it is behind the glass rather than over it): the scheme's ground colour, nearly
   opaque at the window edge and gone by about 45 % of the width. The album identity and the
   tracklist are printed on it. The glass never sits on the washed region, so every surface
   stands on unveiled artwork.

The queue carries one song from another release, the single *Meltwater*, whose art is
`slow-thaw.jpg` (Aaron Burden): an aerial view of a frozen lake, fine frost everywhere and broad
lighter and darker bands. When it sounds, the plane dissolves to it (480 ms, stepped under reduced
motion) and the album column shows the single. That is the plane's second phase and every check
below is made at both.

`groyne-field.jpg` is not used. Its top half is sky and haze, which is where the queue's control
and its menu stand, and glass over a flat field is the skill's first uncaught failure.

### The opaque page first

Laid out with no material at all: the service's wordmark and the app's one display setting at the
top of a left column; the album's identity (kind and year, title, artist, count, length, label);
the tracklist with the sounding track marked; a one-line liner note; the photograph credits. On
the right, the queue list and its action; at the bottom, the transport and the volume. That page
reads; the material is laid over the controls of it and nothing else.

### Floating inventory (read aloud)

1. **Transport**, base plane: previous, play/pause, next and the scrubber with elapsed and remaining
   time. One capsule housing at the bottom, centred on the open artwork between the column and the
   queue.
2. **Volume**, base plane: mute and the level. One small capsule, bottom right.
3. **Queue control**, base plane: "Save Queue", a capsule directly under the queue panel,
   right-aligned with it, the way a Mac list carries its actions below it. Unavailable while
   nothing is queued. It is one end of a matched-geometry morph whose other end is
4. **the playlist menu**, overlay plane while open: add the queue to one of the playlists, or make
   a new playlist from it. It drops below the control into open artwork, and its height is bounded
   by a measurement against the bottom band, so it never reaches the transport or the volume; past
   the bound it scrolls inside itself.

The brief names the queue as floating. It floats in placement only: a list of songs with their
artists and releases is content by the decision function's first question, whatever a brief calls
it, so the queue is an opaque panel over the artwork and only its action is glass.

Opaque, printed on the washed plane: wordmark, the Reduce Transparency switch, album identity,
tracklist (its rows are plain buttons with a tonal hover), liner note, credits. Opaque and tonal,
at the top right: the queue panel, "Playing Next" with a summary and six rows visible, each row a
plain button that plays from there, the rest scrolling inside the panel. Inside glass, as fills
and never hosts: the transport's buttons, both sliders, the capsule's label, the menu items.

### Record lines

```
plane: one viewport-fixed canvas, texture source "artwork", painting the sounding release's
  artwork cover-fit (icehouse.jpg for the album, slow-thaw.jpg for the queued single), dimmed to
  about a third in dark, and a left reading wash in the scheme's ground colour. Broad frequency:
  crack lines and frost bands; fine: bubbles and frost grain, both in the photograph itself.
  Nothing is laid over the plane in CSS.
inventory: transport housing (base), volume housing (base), queue control (base) morphing into the
  playlist menu (overlay). Printed on the wash: wordmark, the Reduce Transparency switch, album
  identity, tracklist, liner note, credits. Tonal: the queue panel at the top right, a solid step
  of the neutral ramp (#f6f9fb light, #121a22 dark) with a hairline of ink (10 %, 45 % under
  Increase Contrast), r24, no shadow, blur or depicted material, six rows tall at every length.
groups: transport = transport housing; volume = volume housing; queue-menu = the morph (control
  and menu). All three read texture "artwork" and each also declares a hint measured off the frame
  the canvas is showing under its own box (queue-menu: the capsule plus the box it opens into,
  the laid-out menu while open), re-read on every repaint (scheme, release, resize), on the menu
  opening and closing, and every other frame through a release dissolve and once as it lands:
  tone by encoded level, luminance = the encoded Rec. 709 mean decoded once (the runtime's
  convention), complexity = the encoded luma's standard deviation over 0.25. Values in part two.
  Gaps derived with samplingPaddingFor under the resolved policy and laid out, never pinned:
  transport to volume; the capsule below the panel by its own group's padding, so neither tier's
  blur reaches under the panel; the open menu's foot above the band by the larger group's.
family: thickness 8 across all surfaces. S 46 as measured: volume and the queue control, capsule r23.
  M 64: transport, capsule r32. L: the menu (272 wide, about 200 tall with three playlists),
  fixed r24. Straddles 32 to 96. Anchor: the viewport edge, r0 (a web page cannot see the browser
  window's corner radius; the window clips the viewport's bottom corners itself). Inner radii
  derived as housing radius minus inset: transport previous/next 40 at inset 12 = 32-12 = r20
  (circles); play 48 at inset 8 = 32-8 = r24 (circle); volume mute 32 at inset 6 = 22-6 = r16
  (circle); menu items 36 tall at inset 6 = 24-6 = r18 (capsules). The panel is content, not a
  rung, and shares the geometry: r24, rows at inset 8 = 24-8 = r16.
tint: none. The plane is the colour (ice blue, then frost blue). The page's one accent, an ember
  orange, is a status in the content plane only: the mark on the sounding track.
scheme and pose: colorScheme auto; windowActivation auto, never pinned.
motion: queue control <-> menu is GlassMorph matchedGeometry, below-end, one thickness at both
  ends. Press is the runtime's glow and flex on the transport, the volume and the queue control,
  and nothing else: inner buttons and menu items show a quiet plate on hover and focus, and a
  press changes no colour and adds no scale. A slider's knob grows while held or focused, the
  page's stand-in for the sanctioned lift of a knob into glass. The plane dissolves when the
  release changes (a state). Nothing moves at idle; the page loads paused. Reduced motion: the
  runtime's springs go critical, the dissolve steps, the knob and plate transitions stop.
tier expectation: webgpu requested (localhost is a secure context); ?renderer=css forces the CSS
  tier, which is the same design without refraction.
accessibility: the runtime follows the system for motion, contrast and forced colours. Reduce
  Transparency is also an app setting (the switch at the top of the column, stored in
  localStorage, seeded from the system where the engine can answer) passed to the root as a
  boolean, so zero diagnostics means the app answered. With nothing queued the capsule is
  aria-disabled (focusable, announced unavailable) and never opens an empty menu; if the queue
  runs out while the menu is open, the menu closes and the capsule takes focus. Forced colours
  removes the glass; the page's own fills that must survive it, the slider tracks, are solid
  system colours (CanvasText tracks, Highlight thumbs and, in Firefox, Highlight progress).
contrast: labels on glass use the runtime's primary and secondary ink on child elements; the
  panel and the column use the page's own ink ramp; all measured on rendered pixels at both
  phases, both schemes, with transparency reduced and on the CSS tier; results in part two.
```

### Data

One album, *Pressure Ridge* by Signe Halvorsen (Tundra Tapes, 2025), nine tracks, 39 minutes,
recorded through hydrophones set into lake ice; the listener is on track 4. A queue of six: the
single *Meltwater* by Kasper Lind (added by the listener with Play Next), then the album's tracks 5
to 9; playing the album's first track makes it nine. Three playlists: Late Desk (48 songs), Cold
Mornings (23), Long Drive North (61), and one more for each "New Playlist from Queue". There is no
audio; playback is a clock, and the page opens paused, as a web client restoring a session does.

## Part two: what the runtime resolved, what was measured, what the eye saw

Read in Chromium (Playwright, `channel: "chromium"`, `--enable-unsafe-webgpu`, device scale 2)
against the Vite dev server, 1440 × 900 unless stated, 2026-09-27, after the review's fixes.

### Resolved state (`root.capabilities(groupId)`)

| group | default URL | `?renderer=css` |
|---|---|---|
| transport, volume, queue-menu | `webgpu`, `gpu-texture`, refraction `true`, analysis `exact`, health `ok` | `css`, `css-backdrop`, refraction `none`, analysis `hint`, `cssBody: collapsed`, health `ok` |

Every group resolved `materialDocument.profileKey` `apple-macos-27.0-1x-light-standard-glass0.5`
in light (the dark key was read in the first pass, before the fixes, and not re-read). The CSS
tier reaching `hint` rather than `none` is the declared hints doing their job. The first pass read
`cssBody: two-layer` on that tier; this pass reads `collapsed` on all three groups. The runtime
collapses the body on its cost budget, on a surface with no span, or on a blur step that rounds to
nothing, and which of those applied here was not traced. The footer prints the transport group's
resolved tier in words, so the page says which material a visitor is looking at.

### Diagnostics

Zero on both channels (`__vitrea.diagnostics.reported`, `__vitrea.scene.diagnostics.reported`)
in: light and dark; the menu open with six and with nine queued rows, grown to nine playlists and
scrolling, closed by Escape and by a choice; the queue empty; the queue running out while the menu
is open; transparency reduced; the second phase (the single) and through the dissolve to it;
reduced motion, including flipped at runtime with the menu closed and open; increased contrast;
forced colours in both schemes; the receded pose in both schemes; the CSS tier in both schemes;
1440 × 790 with and without reduced transparency. Two findings on the way there in the first pass,
both fixed:

1. `quaternary-ink-on-thin-material`: the first build drew its hover plates from
   `--vitrea-foreground-quaternary`. The runtime cannot see that a rule uses the token only as a
   fill, so it flagged the page. Plates are now mixed from the ink itself (`currentColor` at 10 %),
   which follows the runtime's pole just the same.
2. `group-proxy-overlap` under forced colours only: `samplingPaddingFor` derives zero when the
   material draws no blur, the layout gap followed it to zero, and core still checks against its
   advisory 24 px. The derived gaps are floored at `DEFAULT_GROUP_SAMPLING.samplingPadding`, the
   same floor `GlassToolbar` uses.

### Declared backdrops, measured off the plane

Measured by the page off the frame the canvas is showing under each group's box (the menu's group:
the capsule plus the box it opens into), re-measured on every repaint and through every dissolve.
Luminance is the runtime's convention (encoded Rec. 709 mean, decoded once). At rest:

| phase | transport | volume | queue-menu |
|---|---|---|---|
| album, light | light 0.54 | light 0.41 | light 0.43 |
| album, dark | dark 0.06 | dark 0.05 | dark 0.05 |
| single, light | mixed 0.27 | mixed 0.22 | mixed 0.29 |
| single, dark | dark 0.03 | dark 0.03 | dark 0.03 |

Through the dissolve from the album to the single, read off the scene every frame: the light
declaration moves in 19 steps (transport 0.54, 0.53, 0.51 … 0.28, 0.27; its tone turns `mixed` at
0.34, a little past halfway), the dark one in 8, and no frame declares the destination before it
is on screen.

### Gaps the material asked for (`samplingPaddingFor`, laid out, never pinned)

| | light | dark | light, reduced transparency | dark, reduced transparency |
|---|---|---|---|---|
| panel ↔ queue control | 24 (the floor) | 26 | 40 | 48 |
| transport ↔ volume | 26 | 30 | 42 | 51 |
| menu's height bound at 1440 × 900 | 273 | 271 | 250 | 237 |
| menu's height bound at 1440 × 790 | 200 | | 177 | 164 |

The three-playlist menu is 199 px, so it fits everywhere except 1440 × 790 with transparency
reduced, where it scrolls 22 px (light) and 35 px (dark) inside itself; the arrow keys still reach
its last item, which scrolls into view. Nine playlists at 1440 × 900 fill the 273 px bound and
scroll. In every state measured the open menu's foot stands at least 63 px above the band, and
the menu never overlaps the transport or the volume.

### Contrast, on rendered pixels

Method: each label's text box (a range over its text; a glyph's own box) is read twice at 2x,
once as drawn and once with every label's colour set to transparent (the glass samples the plane,
not the text, so the second capture is the exact background). Ink is the core of the glyphs (the
10 % of changed pixels furthest from the background); "worst" is that ink against the least
favourable background pixel under the label. Menu open in every row.

| state | glass labels | glass glyphs | panel labels | plane labels | plane, large |
|---|---|---|---|---|---|
| album, light | 6.5 | 11.9 | 9.4 | 6.0 | 11.8 |
| album, light, reduced transparency | 7.5 | 14.1 | 9.4 | 6.0 | 11.8 |
| single, light | 6.3 | 10.0 | 9.4 | 7.0 | 12.8 |
| album, dark | 5.3 | 5.5 | 8.5 | 8.1 | 15.2 |
| album, dark, reduced transparency | 7.1 | 7.5 | 8.5 | 8.1 | 15.2 |
| single, dark | 6.7 | 6.9 | 8.5 | 8.3 | 15.6 |
| CSS tier, album, light | 6.7 | 12.0 | 9.4 | 6.0 | 11.8 |
| CSS tier, single, light | 6.4 | 10.2 | 9.4 | 7.0 | 12.8 |
| CSS tier, album, dark | 5.2 | 5.5 | 8.5 | 8.1 | 15.2 |
| CSS tier, single, dark | 6.7 | 6.9 | 8.5 | 8.3 | 15.6 |

All labels clear 4.5:1 and all glyphs 3:1 at their worst pixel: the lowest label anywhere is
5.2:1 (the transport's elapsed time, dark, CSS tier), the lowest in light 6.0:1 (a track
duration on the wash), the lowest glyph 5.5:1. Two changes bought that in the first pass, both
found by this measurement rather than assumed:

- **The runtime's secondary ink sat at the floor, not above it.** It measured 4.2 to 4.6 in both
  schemes (the runtime holds it at exactly 4.5 against the one level it resolved; a textured body
  varies around that level). Secondary labels on glass now use the runtime's own secondary on the
  pole the runtime picked, its alpha floored at 0.68 on black and 0.78 on white, through relative
  colour syntax on each element inside a host. Primary labels still use the runtime's token
  untouched.
- **The wash's fade began under the durations.** The right-aligned track durations measured 3.7:1
  over the wash's tail; the wash now holds to 24 px short of the column edge and is gone 72 px past
  it. And the dark scheme's dimming went from about 40 % to about a third, which took white primary
  ink on the dark glass from 5.1 to 5.9.

### What the eye saw

- The size law is legible on the page: the 46 px volume and capsule are the clearest glass, the
  64 px transport hazes the cracks, and the menu at about 200 px is the most opaque body, which is
  where the densest glass text sits.
- The queue reads as a printed card at the top right: pale over the ice in light, a dark card over
  the dimmed artwork at night, and in both it is plainly a different material from the glass
  capsule beneath it. The capsule 24 px under it now reads as the list's action; the first pass's
  62 px gap, which the glass queue's own padding asked for, read detached.
- Refraction is quiet under this much frost. At 2x the rim shows as a brighter band a few pixels
  wide at every edge, but a displaced crack line inside it is too subtle to point to; at normal
  viewing the surfaces read as frost with a lit edge. Over the single's frost, which has little
  broad line to bend, the lens is quieter still.
- Over the single the glass reads blue on both tiers, because the blur carries the frost's colour
  through; the WebGPU tier's hue retention holds a little more of it. Nothing depends on the hue.
- Dark: the dark material stays a present, lighter plate over the dimmed artwork rather than
  vanishing into it, and lighter than the dark panel beside it; the room reads as night, not as a
  black shell.
- The CSS tier is the same page without the bend; side by side the listener would have to look for
  a difference (the plates' blue is a touch greyer over the single).
- The receded pose, looked at in both schemes with the root set `inactive` for the capture only:
  at this frost the plates read almost unchanged, the runtime stops their shadow, and nothing on
  the page depends on either. The page itself leaves `windowActivation` on `auto`.
- Increased contrast: the panel's hairline strengthens and the page's own secondary ink (column and
  panel) takes the primary; the glass takes the runtime's increased-contrast treatment.
- Forced colours: the runtime removes the glass and gives each host a system edge; the panel takes
  Canvas and a CanvasText border; both sliders show a solid CanvasText track with a Highlight
  thumb in both schemes (the first pass's gradient track vanished in this mode and left bare
  thumbs).

### Decisions the skill did not make for me

1. **Where the queue control lives.** Under the queue panel, right-aligned, as a Mac list carries
   its actions below it, so its menu drops into open artwork rather than over the panel. The menu
   holds only playlist actions: add the queue to a playlist, or make one.
2. **What a queued song from another release does to the plane.** It changes it: a player shows
   what is sounding, so the queue's single brings its own artwork, a second designed phase, and
   every check above runs at both. `groyne-field.jpg` was rejected for that phase (sky under the
   control and its menu).
3. **How to declare a texture group's hint honestly.** Measured by the page from the pixels it
   painted, per group, per phase and per scheme, rather than one typed number. A declared hint
   overrides the runtime's own tone reading on both tiers, so it states the frame on screen:
   through a dissolve it is read every other frame off the two layers mixed by the weight the
   canvas drew them with (canvas 2D composites in encoded values and luma is linear in them), not
   off the layer the dissolve is heading to. Reading the two CPU-side layers rather than the
   visible canvas avoids reading back the canvas the renderer uploads from every frame.
4. **Short windows.** A 1440 px Mac display leaves a browser about 790 px of height. Queue rows and
   track rows yield a few pixels there (`clamp` on the viewport height), and the menu's height is
   measured against the band, so at 1440 × 790 it still clears the transport band, scrolling
   inside itself when transparency is reduced.
5. **Focus across a plane promotion.** Opening the morph promotes the platter to the overlay plane,
   which moves its node, and a focused element that is moved loses focus. The menu's first item is
   focused after that commit; Escape and a choice return focus to the capsule, which the runtime's
   own restore then carries through the demotion.
6. **The playback clock.** Paced by the root's frame loop, but timed by `performance.now()`,
   because the loop's deltas are capped for motion and a position has to keep real time.
7. **`samplingPaddingFor` and `DEFAULT_GROUP_SAMPLING` are imported from `@vitreajs/vitrea-web`
   and `@vitreajs/vitrea`**; the React package re-exports neither. Everything else comes from
   `@vitreajs/vitrea-react`.
8. **The queue as content.** The brief's "floats" is about placement, not material. The panel is
   bounded at six rows so nothing below it moves as the queue changes length (an emptied slot
   reads as calm space); a longer queue scrolls inside it. Nothing floats over the panel, so it
   has no scroll edge, deliberately.
9. **Where the menu stops.** The menu's height bound is measured, from the capsule's foot plus
   the morph's gap to the band's top edge, less the larger group's padding, and recomputed with
   the layout; the menu scrolls past it rather than laying glass over the controls below.
10. **A runtime defect the page works around.** In 0.24.0 the matched-geometry morph rebuilds its
    geometry drivers at zero when the root's motion profile changes, and a pinned morph is never
    placed again: flipping Reduce Motion with the page open left the capsule a 0 × 0 box at the
    viewport's origin, unreachable by pointer (a page loaded with the setting already on was
    fine). The page remounts the morph on that flag, closed, because a fresh morph measures its
    closed footprint from whatever end is mounted; so a flip with the menu open closes the menu.
    The runtime's materialise morph already carries its driver's value across the same rebuild;
    the matched-geometry one should too, and the workaround goes when it does.

### QA lens (§8)

1. `[layer]` Pass. Glass: transport, volume, the queue control and its menu, each an action or a
   transient platter. The queue is an opaque tonal panel; album identity, tracklist, liner,
   credits and the switch are printed on the plane.
2. `[layer]` Pass. No host inside a host; every inner control and menu item is a fill; the open
   menu is bounded so it never lies over the transport or the volume.
3. `[layer]` Pass. Three surfaces at rest, the capsule becoming the menu when open; each is an
   action the brief names.
4. `[material]` Pass. Regular only.
5. `[material]` Pass. No tint; no fill in its place; no hand-rolled blur anywhere.
6. `[material]` Pass at both phases. Every surface stands on unwashed artwork: cracks and bubbles on
   the album, frost on the single. The single's frost is weaker in broad structure, so the bend is
   quieter there (noted above).
7. `[material]` Pass. The wash is a ground colour sampled from each sleeve and the panel a flat
   step of the neutral ramp, not depicted material; the knob, plates and tracks are flat fills.
8. `[geometry]` Pass. Capsules r22 and r32; the menu r24; inner radii derived (20, 24, 16, 18);
   the panel r24 with rows r16; the switch's knob concentric with its track; anchor named
   (viewport edge, r0).
9. `[geometry]` Pass. Single-row housings and the control are capsules; the menu's items are
   capsules by derivation; the menu keeps r24.
10. `[geometry]` Pass. 44 / 64 / about 200 px spans, one radius per rung, thickness 8 everywhere,
    including both ends of the morph.
11. `[grouping]` Pass. One group per function; the bottom band has two groups; no text button
    beside an icon button in any group; gaps derived and laid out.
12. `[legibility]` Pass, table above: 5.2:1 is the lowest label anywhere, 5.5:1 the lowest glyph.
13. `[legibility]` Pass. Nothing scrolls under glass. The column scrolls on its own only in a
    window shorter than its content, where no glass sits over it; the queue panel and the open
    menu scroll inside themselves with nothing floating over them. So there is no scroll edge,
    deliberately.
14. `[legibility]` Pass for reduced transparency (the app's switch), increased contrast, reduced
    motion (dissolve steps, springs critical; a runtime flip handled per decision 10) and forced
    colours (sliders keep solid tracks); the receded pose was looked at. An empty queue leaves the
    capsule focusable and unavailable rather than opening a menu of dead items.
15. `[layout]` Pass. The artwork reaches every edge; the plane is viewport-fixed; the band is laid
    out from the column's own width variable, the capsule from the panel's height variable and
    the derived gap, and the menu's bound from a measurement of the band. The column clears the
    band by construction rather than by measurement, because they share one edge.
16. `[layout]` Pass. No custom background, border or scrim on any bar or menu. The queue panel
    carries its own background and hairline because it is content, not a bar.
17. `[motion]` Pass. The menu is a matched-geometry morph out of its capsule; press is the
    runtime's light and flex on the housings at the pointer and adds no colour and no scale; the
    only other motion is the plane's dissolve on a release change, the scrubber while playing and
    a slider knob growing while held. The page loads paused.
18. `[colour]` Pass. The control layer is monochrome; the ember accent is a status in the content
    plane, a glyph never a label, and far from the ice blue behind the glass.
19. `[honesty]` Pass. Hints are measured off the frame on screen at both phases and through the
    dissolve between them; the resolved state was read (table above); zero diagnostics.
20. `[eye]` The nearest Apple surface is Music's full-screen Now Playing on macOS 27 (artwork behind
    a floating transport and a Playing Next list). No native capture of it was made, so no
    side-by-side comparison exists. What the eye notes against the material as measured: the rim
    reads as a diagonal lit edge rather than Apple's thin bright inner line (the named gap in
    `optics.md` §6), and over the single the body's blue is paler than Apple's would be (§5).

### The review's findings, and what each changed

1. `[layer]` The permanent queue was content on glass. It is now an opaque tonal panel in the
   content layer at the same position; its group, its hint and its padding term are gone, and
   three groups remain (`transport`, `volume`, `queue-menu`).
2. `[layer]` A nine-row queue and a growing menu could lay glass over the volume. The panel is
   bounded at six rows and scrolls, and the menu's height is bounded by a measurement against the
   band (checked at 1440 × 900 and 1440 × 790, with nine rows and nine playlists).
3. `[honesty]` The declared hint described the destination artwork during a dissolve. It is now
   measured off the frame on screen, every other frame through the dissolve and once as it lands.
4. `[motion]` Press was a colour swap and a shrink on inner buttons, rows and menu items. Both are
   gone; hover and focus keep a quiet plate, and press is the runtime's alone.
5. `[legibility]` Forced colours lost the slider tracks. They are solid system colours now, for
   the WebKit and the Firefox pseudo-elements.
6. `[legibility]` An empty queue's menu trapped keyboard users. The capsule is unavailable while
   nothing is queued, and the menu closes to it if the queue runs out while it is open.
