# Film festival: design record

The programme page of the Northlight Film Festival, a city's winter festival: four days (Thursday 18
to Sunday 21 February 2027), three cinemas, twenty-four films. It is for someone deciding what to see
and buying a ticket. The page does three things in order: shows the opening film, lets the reader
pick a day and read that day's schedule by cinema, and sells a ticket or a pass. Written under the
materialist skill (`skills/materialist/SKILL.md`) on vitrea 0.24.0 through
`@vitreajs/vitrea-react`.

Part one was written before the first host was registered and is kept as written. Part two records
what building changed, what the runtime resolved and what the eye saw, and what the source review of
2026-09-27 changed after it (change 8, the contrast failures). Where the two disagree, part two is
the page as built.

## Part one: the record, before the first host

**Is glass earned?** Yes. The controls float over a full-bleed still from the opening film, and the
programme sheet scrolls up beneath them. The transparency keeps the film in view while the reader
works the controls. That is the "floating bar over a full-bleed photograph" case.

**The opaque page first.** Without any material, the page is a festival programme printed on
snow-white paper. It has a title tab rising into the still, a schedule for one day with a column per
cinema, then the strands, the passes, and the venues with access notes. Hierarchy comes from type
(a serif for titles, the UI face for times and metadata), from hairline rules and from whitespace.
The three floating controls would sit as a plain row of links, tabs and a button at the top. The
glass is laid over that page and carries no structure of its own.

```
plane: one viewport-fixed <canvas> painted once per resize with the still from Ironai (the opening
  film; photograph by Plainery n., Unsplash). It is cover-fit around an anchor: the frame's right
  edge sits at image x 2065 of 2600 (the nearest lamp standard) and its top at image y 297, scaled
  to cover (s = 0.772 at 1440 x 900). The default cover fit was measured and rejected: it put the day
  control and Tickets over flat grey sky (luminance standard deviation 1.0 of 255 under both). The
  anchored crop puts every bar group over structure: the facade and the "50" sign under the
  navigation (sd 36.8), the traffic light and the hotel's window grid under the days (sd 51.6), and a
  lamp standard's arm and glass globe under Tickets (sd 32.0). Broad frequency: facades, the sky's
  gradient, the receding lamp standards, the road. Fine frequency: sign lettering, window grids,
  snowflakes, the lamp globes. Texture path: after painting, the canvas is snapshotted to an
  ImageBitmap and handed over as source "still", placed by the canvas element. Paint and sample are
  the same pixels at the element's box, imported once per resize rather than every frame. Nothing
  is laid over the plane in CSS.
inventory: three surfaces on the base plane, one row at the top of the viewport:
  1. navigation capsule: the wordmark and four section links (Programme, Strands, Passes, Visit).
     Navigation.
  2. day control: a segmented control of the four festival days. It chooses the schedule's day and
     brings the schedule into view.
  3. Tickets: the primary action. A capsule that morphs into the tickets platter (overlay plane
     while open). The platter is transient: four ways to buy, and a link to compare passes.
  Everything else is content and stays opaque, on the printed model: the title tab, the schedule,
  the strands, the passes, the venues, the reduce-transparency setting and the footer. Paper,
  hairlines and whitespace, square corners, no shadow anywhere.
groups:
  nav      navigation capsule; texture "still"; hint { tone: "dark", luminance: 0.13,
           complexity: 0.6 } (encoded mean 0.40, p5 to p95 0.21 to 0.66)
  days     day control; texture "still"; hint { tone: "light", luminance: 0.28, complexity: 0.8 }
           (encoded 0.56, p5 to p95 0.15 to 0.81)
  tickets  Tickets morph; DOM sampling, not the texture. Open while the page is scrolled, the
           platter sits over the sheet, and a texture group would refract the still where the
           reader sees paper. Its hint is declared per state, because the app knows what is under
           it: closed, { light, 0.49, 0.5 } (the lamp band); open at rest, { light, 0.53, 0.35 }
           (sky and lamps); open over the sheet, the sheet's own paper in the resolved scheme.
           The platter closes when the page scrolls, like a menu, so its backdrop is fixed for as
           long as it is open.
  Gaps: the three groups are separated by the bar's flexible space, at least 48 px at 1440. That is
  wider than the padding the runtime derives at span 48, and wider than the Reduce Transparency
  padding. samplingPadding is never written.
  At rest and scrolled: the scroll edge (below) keeps the sheet out of the bar's band, so nav and
  days only ever have the still behind them.
family: thickness 8 across all surfaces, the morph's open end included. Two spans. Span 48: the
  navigation capsule, the day control and the Tickets capsule, all capsules at radius 24. Span
  about 330: the tickets platter at a fixed radius of 28. The bar's controls want one row height,
  and a second bar height would be decoration. The size law is shown by the morph instead: one
  host grows from span 48, low in the 32 to 96 band, to 330, past saturation, so larger-is-more-
  opaque happens in front of the reader. Anchor: the viewport edge at radius 0, with the bar at the
  32 px page margin and 20 px from the top. No surface takes its radius from the viewport, and
  concentricity is held inside each surface: navigation link focus pill 24 − 6 = 18, day indicator
  24 − 4 (through the runtime's own resolveConcentric), platter rows 28 − 8 = 20.
tint: one seed, on Tickets, the page's primary action: #c42233, the red of the "50" sign's ring,
  lifted from its overcast reading of rgb(156 32 40). It stands apart from the plane's dominant cool
  grey. The seed is dropped while the platter is open, so the platter reads as regular glass. The
  same hue is the sheet's one accent: gala marks, links, focus, the selected day's rule. It is
  never a status.
scheme and pose: colorScheme "auto". The sheet's tokens follow prefers-color-scheme: light is
  snow-white paper, dark is the slate of the facade after dark. The still is the same picture in
  both, because a film still is not re-graded for a theme. windowActivation "auto", never pinned.
motion: Tickets is a matchedGeometry morph (capsule to platter, below-end, gap 10, one host for the
  pair's life). The day indicator slides on the runtime's springs. Press is the runtime's glow and
  compression at the pointer. Nothing moves at idle. Choosing a day swaps the schedule in one step
  and scrolls to it (smooth, instant under Reduce Motion). The scroll edge's mask follows the
  scroll position, which is a state rather than an animation. Reduced motion: the runtime floors
  its springs; the page adds nothing.
scroll edge and inset: the scrolling column carries a mask-image, a sibling of the glass root and
  never its ancestor. The mask is transparent from the viewport top to the bar's measured bottom
  plus 12 px, then ramps to opaque over 56 px. Its stops are recomputed on every scroll from the
  bar's measured box (ResizeObserver), never typed as a constant. At rest the first screen is the
  still and no content sits under the bar. Section anchors take a scroll margin from the same
  measurement.
tier expectation: webgpu where the engine grants a secure context and an adapter (Chromium over
  https or localhost). ?renderer=css asks for the CSS tier, which is the same design without
  refraction and without the body's hue.
accessibility: the page offers a Reduce Transparency switch (in Visit, under "This page") and always
  passes the root a boolean. The switch starts from prefers-reduced-transparency where the engine
  answers it, follows the system until the reader flips it, and then persists the reader's choice.
  Increase Contrast and Reduce Motion follow the system. Under forced colours the glass is removed
  and the bar is plain links, tabs and a button over the still.
contrast: labels are styled on child elements with the runtime's primary ink token. They are measured
  on rendered pixels at rest and scrolled, in both schemes. Results are in part two.
```

## Part two: built, resolved, seen

### What changed from part one, and why

1. **The crop moved 104 image px left** (anchor right edge 1961 of 2600, was 2065). With the first
   crop, the "50" sign sat under the navigation's right end. In the dark scheme its white face
   pushed the capsule's body into the band where neither ink holds body text: "Visit" measured 4.50:1
   with opaque white. Now the sign sits in the 96 px gap between the navigation and the days, with
   its right half bent at the day control's left rim. The navigation is over facades alone
   (encoded 0.36), the days are over the hotel and the traffic light (0.49), and Tickets is centred
   on the lamp standard's head (0.74). The pedestrian stays in frame with a hand at the edge. The
   hints were re-measured off the new crop: nav `{ dark, 0.11, 0.55 }`, days `{ dark, 0.20, 0.75 }`,
   tickets closed `{ light, 0.51, 0.5 }`, platter at rest `{ light, 0.54, 0.4 }`. Those were
   constants read at 1440 × 900; change 8 replaced them.
2. **The platter grows in place.** GlassMorph's `below-end` placement with `gap={-48}` puts the open
   end's top edge where the capsule's was, so the platter unfolds down and left from the capsule and
   "Tickets" stays where it was pressed. It is 300 × 245 at radius 28, so its span is 245, not the
   330 part one estimated.
3. **The photo credit moved onto the tab's paper.** Set on the still's snow, the caption crossed a tyre
   and "Hayama" was illegible. No line of small type stays legible across tyres, snow and coats.
4. **The day indicator became an ink pill.** Part one's 13% ink wash darkened the selected label's
   own ground (4.11:1 in the dark scheme). The opposite pole at 42% vanished on the light material.
   The indicator is now the ink at 90%, with the selected label in the opposite pole (10:1 or
   better). It also needed `position: relative` on the track. On the GPU tier the runtime's owned
   transform happens to make the track the containing block; on the CSS tier nothing did, and the
   indicator landed beside Tickets.
5. **Glass ink is opaque, and two labels take the page's pole.** See *Contrast*.
6. **Below 1360 px the bar spreads instead of centring.** At 1280 the centred day control came
   within 16 px of the navigation, and the runtime reported the proxy overlap. Below 1360 the row is
   a flex row with a 48 px minimum gap, which is diagnostic-free at 1280 and 1360 with transparency
   reduced.
7. **The Tickets morph is keyed on Reduce Motion.** See *Runtime findings*, 1.
8. **Every hint is measured, live, off what the page displays** (source review, 2026-09-27). A
   declared hint overrides the runtime's own tone reading on both tiers: on the WebGPU tier a texture
   group still refracts the still's pixels, but its measured local tone stands down for the
   declaration (platform-web `root.ts`, renderer-webgpu `renderer.ts`, `backdropToneHint`). So the
   constants of change 1 were what the body and the ink followed at every size, and they were true
   only at 1440 × 900: the crop is a cover fit that moves with the viewport and the bar re-lays
   itself out below 1360, so the days' real backdrop was 0.40 at 1280 × 900 and 0.28 at
   1440 × 1080 against a declared 0.20. The platter's hint was a binary test that declared pure
   paper (`{ dark, 0.01 }` in the dark scheme) as soon as the sheet's top reached y 265, although
   the platter's top 60 px always sit in the scroll edge's clear band over the still.
   Method (`beneath.ts`): the page composes what it displays under each group's footprint (the
   still's pixels, read back from the canvas they were painted into, and wherever the scroll column
   paints paper, that paper at the mask's alpha for the row) and reduces it as the runtime's
   silhouette reading does (`silhouetteBackdropTone`): encoded Rec. 709 luma averaged over the
   device-pixel centres inside the rounded footprint, decoded once. Tone is light at an encoded
   mean of 0.5 or more; complexity is the spread as a fraction of its maximum 0.5, stated for the
   record because the runtime reads none. Footprints: the navigation and day hosts' boxes as
   capsules; the Tickets spacer at radius 24 while closed; while open, the platter placed from the
   spacer as the morph places its open end, at the open content's laid-out size, radius 28. The
   hints are read again after every repaint of the still, whenever the bar, a host or the Tickets
   spacer changes box (a ResizeObserver), on a change of scheme (the paper), when the platter opens
   or closes, and on every frame of scroll while it is open. Type, rules and the printed figure on
   the paper are not modelled. One residual, recorded: when the platter opens or closes the hint is
   read at the endpoint (the open platter's box, or the capsule), not at the morph's moving box
   through its roughly 400 ms spring, so across the sheet's edge the declaration describes the
   destination for that interval.
9. **The navigation's and the platter's labels take their own pole** (the review's follow-up). The
   runtime picks one ink per surface, off the surface's whole backdrop; a platter opened across the
   sheet's edge has a body on both sides of the crossover. Each navigation link and each platter
   label (the head and every row) is read with change 8's method under its own box, the platter's
   at the offsets they settle at inside the placed platter. Its ground is predicted as the runtime
   composes it: the body the runtime publishes for the frame it is drawing (`renderInput()`, the
   node's `optics.tint` laid over the backdrop at `optics.tintAlpha`, after the pose and
   accessibility folds), over that reading, in encoded space. The label takes black at full
   strength where that ground is at or above relative luminance 0.179, where the two poles tie,
   and white below it (`beneath.ts`, `inkOver`). The readings are taken on the hints' cadence and
   the pole is re-chosen on every frame the runtime draws, since a new hint reaches the published
   body a frame later. A highlighted row's fill is its own ink, with the label in the other pole.
   Checked against captures: the predicted ground is within 0.01 of the rendered median on rows
   wholly over one backdrop and within 0.02 on the row the edge crosses, on both tiers.

### As built

```
plane: as part one, anchored at image (1961, 297) of (2600, 1463); s = 0.772 at 1440 x 900.
  Measured under the groups at 1440 x 900: nav encoded 0.36 (sd 0.12), days 0.49 (sd 0.17),
  Tickets 0.74 (sd 0.12); at 1280 x 900: nav 0.41 (sd 0.16), days 0.67 (sd 0.23), Tickets 0.74.
  The plane is identical in both schemes.
inventory: navigation capsule, day control, Tickets capsule (base), with the tickets platter on the
  overlay plane while open. Everything else is printed and opaque.
groups: nav (texture), days (texture), tickets (DOM). Every hint is measured under the group's
  footprint by change 8's method; the table below gives the values. Gaps at 1440: nav to days
  96 px, days to Tickets 415 px. The platter closes on scroll and on a click elsewhere.
family: thickness 8 everywhere. Span 48: three capsules at radius 24. Span 245: the platter at
  fixed radius 28. Inner radii: link focus ring 24 − 6 = 18; day indicator 24 − 4 through
  resolveConcentric, resolved to 20; platter rows and close button 28 − 8 = 20. Anchor: the
  viewport edge at r0, bar at the 32 px margin, 20 px from the top.
tint: #c42233 on Tickets at full strength while closed; none on the open platter.
scroll edge: the bar's measured bottom (68 at 1440) + 12 = 80, ramp to opaque at 136. Sections
  land their heading rule at 152 (the first section lands the sheet's own edge at 80, where the
  ramp starts, so no hard step shows inside it).
```

Hints `{ tone, luminance }` as declared before the review and as measured now. Complexity is on
change 8's scale (nav 0.25, days 0.35, Tickets 0.25 at 1440 × 900) and moves no pixel. Tickets
reads the same at both widths because the crop is anchored at its right edge, under the lamp.

| group, state | before (any size) | 1440 × 900 | 1280 × 900 |
|---|---|---|---|
| nav | dark 0.11 | dark 0.11 | dark 0.14 |
| days | dark 0.20 | dark 0.20 | light 0.40 |
| Tickets, closed | light 0.51 | light 0.51 | light 0.51 |
| platter, at rest | light 0.54 | light 0.54 | light 0.54 |
| platter, sheet's top at y 190 | light 0.92 / dark 0.01 | light 0.65 / dark 0.28 | the same |
| platter, over the schedule (scrollY 1000) | light 0.92 / dark 0.01 | light 0.77 / dark 0.09 | the same |

At 1440 × 1080 the navigation reads dark 0.15, the days light 0.28 and Tickets light 0.49. Each
value was checked against a capture of the page with the glass hidden, read with the same
reduction: within 0.01 for every bar group at all three sizes, and for the platter at rest, across
the sheet's edge and over the schedule. Where the programme's heading and its rule sit under the
platter (scrollY 800), the unmodelled type puts the light scheme's value 0.03 high (0.76 against
0.73) and the dark scheme's 0.01 low.

### What the runtime resolved

Read from `__vitrea.capabilities(groupId)` at 1440 × 900 and 1280 × 900 in real Chromium
(`channel: "chromium"`, `--enable-unsafe-webgpu`), in both schemes. The readout was identical at
rest, scrolled, with the menu open, receded, with transparency reduced and with Increase Contrast
on.

| group | `?renderer` default (webgpu) | `?renderer=css` |
|---|---|---|
| nav | webgpu · gpu-texture · refraction true · analysis exact · ok | css · css-backdrop · none · hint · ok · two-layer |
| days | webgpu · gpu-texture · refraction true · analysis exact · ok | css · css-backdrop · none · hint · ok · two-layer |
| tickets | webgpu · css-backdrop · refraction approximate · analysis hint · ok | css · css-backdrop · none · hint · ok · two-layer |

Material document `apple-macos-27.0-1x-{light,dark}-standard-glass0.5`, following the scheme.
`windowActivation` read `active` with focus and `inactive` with the window unfocused (focus and
blur emulated).

**Diagnostics: zero on both channels** (`__vitrea.diagnostics.reported` and
`__vitrea.scene.diagnostics.reported`), with zero console warnings or errors. That holds for both
schemes on both tiers, through rest, scroll, menu open and closed, a day change, reduced
transparency, Increase Contrast with Reduce Motion, the receded pose, and a resize to 1280 and back.
Two findings were cleared on the way. Three `quaternary-ink-on-thin-material` warnings came from
the platter's separator: the check is document-wide, so a quaternary token anywhere warns for every
thin surface. The separator now uses the primary ink at 14%. One scene diagnostic at 1280 was the
proxy overlap described in change 6. After changes 8 and 9 the review read both channels again,
zero on each, with no console warning or error: at 1440 × 900 and 1280 × 900, both schemes and both
tiers, at rest, scrolled, with the platter open at rest, at five openings across the sheet's edge
and over the schedule, while scrolling with it open, with the window unfocused, and with Reduce
Transparency and Increase Contrast.

### Contrast

Measured on rendered pixels at 2x. Each state is captured twice, once as drawn and once with the
glass labels made transparent. The label's computed ink is composited over the second capture pixel
by pixel, and the tables give the worst pixel under any label's text box. The median and a
percentile reading of the first capture agree within 0.1. Floor: 4.5:1 (every glass label is body
size). Bold cells are below it.

At 1440 × 900. The measured hints here equal the constants they replaced in tone and luminance, so
the rows the review did not touch stand; the review's re-measurement reproduced the rest, receded,
menu and platter rows within 0.1. The platter rows across the sheet's edge and over the schedule
are new: the second replaces a row read under the binary paper hint (10.36 in the dark scheme),
which was drawn by a false statement.

| state | light · webgpu | light · css | dark · webgpu | dark · css |
|---|---|---|---|---|
| nav, rest and scrolled | 9.97 | 9.84 | 4.84 | 5.09 |
| days, rest and scrolled | 10.93 | 10.71 | 4.71 | 4.56 |
| Tickets, rest | 6.20 | 6.20 | 5.80 | 5.80 |
| platter over the still | 16.27 | 16.69 | 4.56 | 4.63 |
| platter across the sheet's edge (its top at y 250 to 130) | 16.35 | 16.80 | **4.43** | **4.41** |
| platter over the schedule (scrollY 1000) | 17.06 | 17.51 | 5.17 | 5.25 |
| receded: nav / days / Tickets | 8.95 / 9.41 / 6.84 | 8.77 / 9.24 / 6.84 | 4.98 / 4.53 / 6.33 | 5.22 / **4.36** / 6.33 |
| reduced transparency: nav / days / Tickets | 18.43 / 17.58 / 5.84 | 17.42 / 17.27 / 5.84 | 9.89 / 9.74 / 5.80 | 8.28 / 9.59 / 5.80 |
| reduced transparency, platter | 16.67 | 16.86 | 9.28 | 9.28 |
| receded + reduced transparency, Tickets | 9.14 | 9.14 | 9.44 | 9.44 |
| Increase Contrast: nav / days / Tickets | 10.57 / 10.58 / 5.95 | 11.01 / 10.99 / 5.95 | 8.09 / 7.88 / 5.80 | 6.90 / 6.56 / 5.80 |
| Increase Contrast, receded Tickets | 7.84 | 7.84 | 8.83 | 8.83 |

At 1280 × 900, where the crop moves the days onto brighter pixels and the bar spreads (change 6):

| state | light · webgpu | light · css | dark · webgpu | dark · css |
|---|---|---|---|---|
| nav, rest and scrolled | 10.51 | 10.60 | **4.36** | **4.43** |
| days, rest and scrolled | 14.89 | 15.08 | 6.50 | 6.91 |
| Tickets, rest | 6.20 | 6.20 | 5.80 | 5.80 |
| platter over the still | 16.27 | 16.69 | 4.56 | 4.63 |
| platter across the sheet's edge (its top at y 250 to 130) | 16.35 | 16.80 | **4.43** | **4.41** |
| platter over the schedule (scrollY 1000) | 17.06 | 17.51 | 5.17 | 5.31 |
| receded: nav / days / Tickets | 9.28 / 12.20 / 6.84 | 9.35 / 12.84 / 6.84 | **4.40** / 6.32 / 6.41 | 4.60 / 6.42 / 6.33 |
| reduced transparency: nav / days / Tickets | 18.43 / 17.58 / 5.84 | 17.72 / 17.58 / 5.84 | 9.86 / 9.15 / 5.80 | 8.50 / 6.95 / 5.80 |
| reduced transparency, platter | 19.44 | 19.61 | 9.28 | 9.28 |
| receded + reduced transparency: nav / days / Tickets | 19.77 / 17.58 / 9.14 | 18.69 / 17.58 / 9.14 | 9.71 / 9.10 / 9.44 | 9.92 / 9.28 / 9.44 |
| Increase Contrast: nav / days / Tickets | 10.74 / 13.90 / 5.95 | 11.26 / 14.62 / 5.95 | 7.92 / 6.68 / 5.80 | 6.63 / 5.40 / 5.80 |
| Increase Contrast, receded: nav / days / Tickets | 10.71 / 13.07 / 7.84 | 10.76 / 13.78 / 7.84 | 7.54 / 6.45 / 8.83 | 6.41 / 5.38 / 8.83 |

The scrolled rows equal the rest rows because the scroll edge keeps the backdrop under the bar
the same at every scroll position. The platter's rows are the same at both widths because the
crop keeps the lamp under Tickets.

How it got there. With the runtime's published primary (black at 0.85, white at 0.80), the light
scheme passed everywhere except Tickets (4.46), and the dark scheme failed wholesale: nav 3.55 to
3.93, days 4.11, platter 4.14 to 4.34. Over this still, the dark material's body sits at encoded
0.43 to 0.48 whatever the backdrop, exactly the band vitrea.md names where neither translucent
pole carries body text. Three moves closed it:
- **Opaque poles.** Every glass label takes the runtime's choice of black or white at full
  opacity (`rgb(from var(--vitrea-foreground) r g b / 1)`). This gives up the vibrancy blend for a
  ratio.
- **The crop change** above.
- **The page's own pole for two labels.** The days are black, except where the dark scheme's
  material goes dark under Reduce Transparency or Increase Contrast; there they are white. Tickets
  is white on the red shade the tint keeps whenever the window is active, black on the receded
  grey, and white on the dark scheme's receded frost. The runtime's pick was wrong in exactly
  these places: white on the dark CSS tier's receded days (3.99), black on the tinted capsule under
  light Increase Contrast (3.53), white on the dark receded tint under Increase Contrast (2.38).
  Each branch is backed by a row of the table.

**Three failures, all in the dark scheme.** The light scheme passes everywhere at both sizes
(6.20 or better). Each dark failure is the dark material's body over this bright still landing
near the ink crossover, relative luminance 0.18, where black and white both read about 4.6. In
each, no choice of ink reaches 4.5 at the label's worst pixel:
1. **"Sun 21", 1440 × 900, CSS tier, window unfocused: 4.36** at its worst pixel, 4.75 at the
   median. It sits over the traffic light's dark housing while Fri 19 and Sat 20 sit over the hotel.
   The review measured the pole per label in that state: black 4.36, white 4.18. A label's ratio
   rises as its ink moves away from the ground towards either pole, so no ink colour does better
   than the better pole, and no local ink remedy exists. Moving the traffic light out from under the
   control would crop the pedestrian out of the still. The WebGPU tier reads 4.53 there.
2. **The navigation at 1280 × 900: "Visit" 4.36** (WebGPU) and 4.43 (CSS) at rest, 4.40 receded
   on WebGPU; medians 4.72 to 5.02. Its own pole (change 9) is white, as the runtime's was, and
   white is the better one (black 4.09): the ground under the label straddles the crossover. The
   crop puts brighter facade under the capsule's right end at this width; the old constant (0.11
   against a measured 0.14) had darkened the body into a pass (4.79 and 5.06).
3. **The platter opened across the sheet's edge: 4.43** (WebGPU) and 4.41 (CSS), on the one row
   the edge crosses; medians 4.60 or better. With the sheet's top anywhere from about y 250 to 150
   the platter's mean is a mid level (0.48 down to 0.19), and the dark material collapses its body
   to a mid-grey on the crossover (`rgba(113, 113, 113, 0.891)` at 0.28). Under one pole per surface
   whole rows failed, to 3.70 (WebGPU) and 3.82 (CSS). With change 9 every row wholly over the
   still or the paper passes, and what remains is the row whose ground runs from one side of the
   crossover to the other: at its worst pixel the better pole reads 4.41 to 4.48 there, and the
   page's choice is within 0.04 of it, the two poles tying. Opened at rest or over the schedule the
   platter passes (4.56 and 5.17). The binary paper hint had declared a black backdrop and so drawn
   a near-black body at 10.3 or better; the page does not buy that back with a false statement.
   Closing the last row needs a per-pixel vibrancy blend in the runtime (*Runtime findings*, 4).

QA12 is therefore failing, with these three exceptions recorded rather than passed. What change 9
made pass: every platter row wholly over one backdrop, which had failed at 3.70 to 4.41.

The sheet's own pairs (`sheet` tokens, resolved to sRGB in the page): light 5.52 to 15.14, dark 6.20
to 15.61. The smallest type, the 11 px uppercase strand labels, reads 5.67 in light and 6.20 in dark.

### Runtime findings, for vitrea

1. **GlassMorph collapses when Reduce Motion changes mid-session.** In
   `packages/react/src/morph.tsx`, `drivers` is memoised on the root's motion profile. Flipping
   `prefers-reduced-motion` swaps the profile, which rebuilds every geometry driver at 0, and the
   `placed` ref stops the first-placement branch from ever running again. The host sat at 0 × 0 at
   the origin and could not be opened, in both directions of the toggle. The page keys the morph on
   `useGlassAccessibility().reducedMotion`, so a change remounts it. Fix in the package: re-place
   (jump) the new drivers to the current target when they are rebuilt.
2. **The two-pole ink pick sits on its crossover in two places over a bright photograph.** One is the
   dark material's plain body. The other is a tinted surface under Increase Contrast, where the
   pick chose black on the red shade and white on its receded grey. The page works around both;
   the runtime's own pick would fail 4.5 in the states listed above.
3. **`quaternary-ink-on-thin-material` is document-wide.** A quaternary token used only on a
   245 px platter still warns for every 48 px surface on the page.
4. **One ink per surface cannot serve a surface whose backdrop straddles the crossover.** Over a
   mid-level backdrop the dark material collapses its body towards a mid-grey (`renderInput()`
   publishes tint 113 at alpha 0.891 for the platter at a declared 0.28), where neither pole holds
   4.5 with any margin. A platter half over a bright photograph and half over dark paper then needs
   black on one half and white on the other, and the runtime publishes one `--vitrea-foreground`
   per surface. The page now chooses per label from the published body (change 9), which leaves
   only the line the edge crosses (*Contrast*, failure 3); a per-pixel vibrancy blend would close
   that too. A page can otherwise hide it only by declaring a darker backdrop than the truth, which
   this page did until the review.

### QA lens (skill §8)

Answered on the rendered page in both schemes: with transparency reduced, on the CSS tier, with the
window unfocused, with Increase Contrast and Reduce Motion, and under forced colours.

1. `[layer]` Pass. Glass is the navigation, the day control, the Tickets action and its transient
   platter. The tab, schedule, strands, passes and venues are printed paper.
2. `[layer]` Pass. Nothing glass sits on glass. The day indicator, the menu highlight and the
   separator are fills on the glass. Inside the platter everything is plain buttons.
3. `[layer]` Pass. Three bar surfaces and one platter, each load-bearing.
4. `[material]` Pass. Regular variant throughout.
5. `[material]` Pass. One tint, on Tickets, dropped while the platter is open. There is no solid
   fill on any host and no hand-rolled blur. The native macOS 27 tinted capsule over a photograph
   (fixture `photo__capsule-button__rest-tint-orange`) is itself a flat, opaque colour, which
   matches the page's red capsule.
6. `[material]` Pass. Every surface sits over structure at every phase, because the plane under
   the bar never changes with scroll. The default cover fit failed this (sd 1.0 under two groups)
   and was replaced before any host existed.
7. `[material]` Pass. No depicted material. The sheet is paper tone, hairlines and type.
8. `[geometry]` Pass. Capsules at 24, fixed 28 on the platter, concentric children (18, 20, 20).
   The anchor is named: the viewport edge at r0.
9. `[geometry]` Pass. One-row housings are capsules. The platter is a generous rounded rectangle.
10. `[geometry]` Pass with a recorded choice. Two spans, 48 and 245, one thickness. The bar's
    controls want one height. The size law is shown by the morph carrying one host from 48 to 245.
11. `[grouping]` Pass. One group per backdrop fact. The text-only navigation and the radio
    segments are separate groups. Gaps of 96 and 415 px exceed the derived padding: no overlap
    diagnostic at 1280, 1360, 1440 or 1920, including with transparency reduced.
12. `[legibility]` Fail, in the dark scheme only, with three exceptions recorded under
    *Contrast*: "Sun 21" on the CSS tier with the window unfocused at 1440 × 900 (4.36, and no ink
    can reach 4.5 on that ground); the navigation's "Visit" at 1280 × 900 (4.36 to 4.43, white
    already the better pole); and, with the platter opened across the sheet's edge, the one row the
    edge crosses (4.41 to 4.43). Per-label ink (change 9) made the platter's other rows pass there;
    they had failed at 3.70 to 4.41. The light scheme passes at 6.20 or better, measured at
    1440 × 900 and 1280 × 900 at rest, scrolled, receded, with the platter open at rest, across the
    edge and over the schedule, and with Reduce Transparency and Increase Contrast.
13. `[legibility]` Pass. At rest the first screen is the still and nothing sits under the bar. The
    scroll edge is a mask on the scrolling column only, positioned from the measured bar.
14. `[legibility]` Pass. Reduce Transparency (the page's own switch) frosts the navigation and
    days to 6.9:1 or better (8.3 at 1440 × 900) and holds Tickets at 5.8. Increase Contrast
    strengthens borders and holds 5.4:1 or better (5.8 at 1440 × 900). Reduce Motion steps
    the springs and makes day jumps instant. Forced colours removes the glass and leaves plain
    links, radios (selected day marked in Highlight) and a button. The receded pose greys the tint
    and stops the shadow, and was looked at in both schemes.
15. `[layout]` Pass. The still is viewport-fixed. The sheet reaches both window edges. The inset is
    derived from the bar's measured box, never typed.
16. `[layout]` Pass. No bar, platter or proxy carries a background, border or scrim of the page's.
17. `[motion]` Pass. The platter grows from its capsule in place. The day pill slides on the
    runtime's springs. Press is the runtime's glow. Nothing moves at idle.
18. `[colour]` Pass. The control layer is monochrome except the one seed. Colour lives in the still.
    The red of the seed is taken from the "50" sign and does not approach anything passing behind
    the bar, because nothing passes behind it.
19. `[honesty]` Pass at rest, through the dissolve and through scroll; the morph's own spring is the
    recorded residual (the hint is read at the endpoint, not the moving box, for about 400 ms when
    the platter opens or closes across the sheet's edge). Every group's hint is measured off what the page displays under its
    footprint (change 8): the still's painted pixels and, where the column paints it, the paper
    through the scroll edge's mask, reduced as the runtime's silhouette reading is. It is read again
    after every repaint, layout change, scheme change and opening or closing of the platter, and on
    every frame of scroll while the platter is open. Checked against captures with the glass hidden:
    within 0.01, and 0.03 where the programme's unmodelled heading sits under the platter. The
    resolved state is read, not assumed. Diagnostics are zero.
20. `[eye]` The page's capsules were placed beside the native macOS 27 fixtures
    `photo__capsule-button__rest`, `…rest-tint-orange` and `…inactive-tint-orange`. The eye sees
    three differences the checks do not:
    - Apple's untinted body carries far more of the photograph's hue. The navigation reads as a
      pale blue-grey where Apple's would be tinted by the facade (the documented chroma-retention
      gap).
    - Apple draws a crisp one-pixel bright line inside the edge, where vitrea's rim is softer and
      graded along a diagonal (the documented inner-line gap).
    - The Tickets capsule's refraction is approximate because it samples the DOM. Its rim bends
      the lamp less than the navigation's rim bends the "50" sign.
    No capture of a native toolbar over this still exists, so that comparison was not made.

### Imagery

Rung one of the ladder, both stills used. *Ironai* (Plainery n., Unsplash) is the plane. *Haar*
(Elin Tabitha, Unsplash) is a printed figure in the Strands section. Both photographers are
credited on the page: under the tab, in the figure caption and in the footer.
