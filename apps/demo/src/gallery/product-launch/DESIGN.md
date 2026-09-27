# Product launch: Alder One

The launch page for a full-frame mirrorless camera from a small maker, the Alder Camera Company
(fourteen people, Portland, Oregon; fictional). One page of the vitrea demo gallery, React over
`@vitreajs/vitrea-react` on the workspace source (0.24.0), desktop first at 1440 wide. Written
under the materialist skill (`skills/materialist/`). The record lines below were written before
the first host was registered and brought up to date by the fix pass that followed the source
review; everything after "What was built" was written after looking.

## Derivation

**Is glass earned.** Yes: two bars of controls sit over full-bleed photographs of the product
that change beneath them, section by section and choice by choice. The product's identity lives
in those photographs, in the type and in the order the page tells its story; the glass owns none
of it.

**The opaque page first.** A launch page is a sequence: the camera on the bench, then the sensor,
the lenses, the body and the price, each a printed sheet of facts. The glass finds only the
controls a buyer uses while reading: where am I (section navigation), what am I configuring
(finish, lens), and the one commitment (order). Everything else is content and stays opaque.

**The plane, and why the sheets fade instead of passing under.** The runtime reads a texture's
pixels and bends them (the lens is real only there); the DOM path on the macOS 27 material draws
no lens at all (`refractionScale.approximate` is 0 in `macos27-profile.ts`), and a texture
cannot see DOM text. So the page is two layers: a viewport-fixed canvas that paints the product's
photographs (the live plane, registered as the texture), and a scrolling column of opaque sheets
above it with transparent "windows" between them. The scroll edge is a mask on the column that
fades the sheets out across the bars' measured footprints, so the bars always stand on the
photograph and never on text the texture cannot see. The photograph under them follows the story:
the plane shows the photograph of the last window the reader has reached, and the lens and finish
windows show whichever lens and finish are chosen, so choosing one changes the picture both bars
are made of. The Nickel window is the hero's photograph framed closer, not a macro of its own
(Decisions, 9).

**Light or dark.** The scene is daylight: a camera photographed from above on weathered deck boards
in open shade. Both schemes are designed (`colorScheme="auto"`); the light sheet is a pale warm
grey taken from the satin top plate, the dark sheet the brown-black of the gaps between the boards.
Five of the seven photographs are low-key macros, so the light scheme carries a real tension: dark
photograph bands framing a pale sheet. It is kept because the product's scene is daylight; the
fade is designed to read as a sheet's edge rather than a smudge.

**Tint.** Withheld. The plane cycles through orange-brown wood, a green-cream sensor, magenta and
teal lens coating, gold contacts and grey metal; any one seed clashes with at least one of them,
and the skill's rule is to withhold where the plane already carries the product's colour. The
order action is found by position (the trailing end of the bottom bar), by grouping (its own
group) and by its label, which is the price.

## Record

```
plane: one viewport-fixed <canvas> painting the current state's photograph cover-fit at the box's
  own size (exact paint = sample), cross-dissolving on a state change; registered as texture
  source "plane". States: hero (camera on deck boards), sensor, lens-28 | lens-45 | lens-90,
  finish-nickel | finish-graphite. Broad frequency: board seams, the camera body, mount rings,
  aperture blades, coating bloom. Fine: wood grain, knurling, leatherette pebble, blade texture.
  Each state's crop (focal point) is chosen so the two bands the bars stand on carry both
  (as built: the hero anchored at 30 % from the top, the macros centred, and finish-nickel the
  hero's photograph at 1.5 times the cover fit anchored at 12 % / 27 %, so board seams, grain,
  the strap and the camera's plates run under both bars; all checked on the render at 1440 × 900
  and 1024 × 768, both schemes).
inventory: base plane, top: the section navigation capsule (wordmark + Sensor, Lenses, Body,
  Price; navigation) and the display toggle (reduce transparency; an action). Base plane, bottom:
  the finish segmented control (Nickel | Graphite), the lens chooser (a button that morphs into
  the lens platter on the overlay plane; action + transient platter) and the order button (the
  primary action, labelled with the price). Six entries, read aloud in one breath. Opaque: the
  sheets (printed model: hairlines, type, tabular figures, no shadow), the lens and finish
  comparison cards inside them, the photographs in the windows (the plane itself).
groups: nav { nav capsule } / display { toggle } / finish { segmented } / lens { morph } /
  order { order button }, all texture "plane". Top bar 2 groups, bottom bar 3. On the WebGPU tier
  no hint is declared, because in 0.24.0 a declared hint REPLACES the per-surface silhouette tone
  the renderer measures from the texture (renderer.ts: `backdropToneHint` skips `silhouetteTone`);
  on the CSS tier each group declares { tone, luminance, complexity } measured from the frame the
  canvas holds under that group's own box, re-measured on every frame the canvas paints, so a
  dissolve is declared as the blend on screen rather than the photograph arriving (recorded
  below). Gaps between
  groups are derived from the runtime (max of core's advisory 24 and `samplingPaddingFor` over the
  bar's members), never pinned; as built, the worst case over every accessibility state and both
  schemes, held constant (Decisions, 5).
family: thickness 8 across all surfaces. Span 44: nav capsule r22, display toggle capsule r22.
  Span 56 (the finish track and the lens trigger measure 58 with their 1 px border; the order capsule 56):
  finish track r28, lens trigger capsule r28, order capsule r28. Span ~160: lens platter
  fixed r28 (the morph keeps one radius so the corner never changes while the size law works).
  Anchor: the viewport edge at radius 0 (a square browser window; recorded as the web deviation
  from a macOS window corner). Inner radii from their housing: nav link pills 22 - 6 = 16; finish
  indicator by the runtime's resolveConcentric at inset 5 (about 23); platter rows 28 - 8 = 20.
tint: none (see Derivation).
scheme and pose: colorScheme auto, tokens follow prefers-color-scheme; windowActivation auto.
motion: the lens chooser is a GlassMorph (matchedGeometry) from its trigger to the platter; the
  finish indicator slides on the runtime's springs; press is the runtime's glow and compression
  on every glass control, the navigation housing included (`interactive`, its links plain inside
  it); the plane cross-dissolves over 480 ms on a state change (a content state, not glass),
  stepped under Reduce Motion; anchor scrolling is smooth unless Reduce Motion. Nothing moves at
  idle.
tier expectation: webgpu where the engine grants a secure context and an adapter (localhost in
  Chromium); css elsewhere and on request via ?renderer=css; the CSS tier is the same design
  without refraction and without hue retention.
accessibility: the app offers Reduce Transparency as a visible toggle (top right) and always
  passes the root a boolean, initialised from prefers-reduced-transparency where the engine can
  answer it and from the stored choice otherwise; Increase Contrast, Reduce Motion and forced
  colours follow the system; under forced colours the runtime removes the glass, the bars remain
  real buttons and links, and the selected finish carries the system's Highlight pair on its
  radio. Keyboard: Tab reaches the navigation first and crosses the bottom bar in drawn order;
  the lens platter closes on Escape, a choice, Tab, a press outside it or focus leaving it, and
  hands focus back to its trigger only on Escape or a choice; scrolling keys pressed on the
  floating chrome scroll the page unless the focused control owns them.
contrast: labels use the runtime's primary ink on child elements; measured on rendered pixels
  per state, both schemes, both tiers, results below.
```

## What was built

Files: `main.tsx` (mounts the glass root's container before `#root`), `App.tsx` (renderer choice,
the Reduce Transparency setting, the `GlassRoot`), `Page.tsx` (state, the plane painter, the one
frame callback), `Chrome.tsx` (the floating layer), `LensMenu.tsx` (the morph and its
lifecycle), `Sheets.tsx` (the content), `plane.ts` (painter, and measurement of the frame it
painted), `content.ts` (the product), `styles.css`.

The story, top to bottom: the camera on the deck boards (a full-screen window); the intro sheet
("Alder One", 150 px); the sensor window, then its sheet (figures, specifications); the chosen
lens's window, then the three-lens comparison with radio cards kept in step with the bar; the
chosen finish's window (Nickel: the hero's photograph, closer; Graphite: the leatherette macro),
then the two finishes, whose cards carry the knurled-ring and leatherette macros, and the body's
specifications; the price sheet (summary table, delivery, box contents, warranty) and the
colophon (all seven photographs credited, one line each, with links to the photographers'
profiles and photo pages; the Reduce Transparency switch). Each window
is 100svh, so a navigation jump lands on a whole photograph and never on a sheet edge caught in a
scroll edge.

## What the runtime resolved (read in the page, 1440 × 900, Chromium with `channel: "chromium"`)

| tier | every group (`nav`, `display`, `finish`, `lens`, `order`) |
|---|---|
| WebGPU (default) | `activeRenderer: webgpu`, `samplingBackend: gpu-texture`, `refraction: true`, `analysis: exact`, `health: ok`, document `apple-macos-27.0-glass0.5` |
| CSS (`?renderer=css`) | `activeRenderer: css`, `samplingBackend: css-backdrop`, `refraction: none`, `analysis: hint`, `health: ok`, `cssBody: two-layer` |

Diagnostics: `__vitrea.diagnostics.reported` and `__vitrea.scene.diagnostics.reported` are both
empty in both schemes on both tiers at rest, at each navigation landing, with the lens menu open,
mid-dissolve (a finish change, a lens choice and a scroll into the lens window, each read at
200 to 250 ms), after choosing lenses and finishes, and with Reduce Transparency toggled; also at
1280 × 800 and 1024 × 768.
Window pose follows focus (`inactive` verified by standing in for a focus loss; headless Chromium
never loses focus on its own).

The CSS tier's declarations at each state's landing, measured from the frame the canvas holds
under each group's own box (linear relative luminance; the dark column is the dimmed frame, since
the dim is painted into the canvas):

| state | light: nav / display / finish / lens / order | dark: nav / display / finish / lens / order |
|---|---|---|
| hero | 0.262 / 0.191 / 0.233 / 0.125 / 0.192 | 0.088 / 0.065 / 0.079 / 0.044 / 0.065 |
| sensor | 0.001 / 0.052 / 0.267 / 0.009 / 0.023 | 0.001 / 0.019 / 0.088 / 0.004 / 0.009 |
| lens-28 | 0.008 / 0.558 / 0.014 / 0.011 / 0.011 | 0.004 / 0.182 / 0.006 / 0.005 / 0.005 |
| lens-45 | 0.353 / 0.002 / 0.045 / 0.031 / 0.030 | 0.115 / 0.001 / 0.017 / 0.013 / 0.012 |
| lens-90 | 0.025 / 0.000 / 0.163 / 0.388 / 0.010 | 0.010 / 0.000 / 0.055 / 0.127 / 0.005 |
| finish-nickel | 0.277 / 0.302 / 0.317 / 0.115 / 0.127 | 0.093 / 0.101 / 0.106 / 0.041 / 0.045 |
| finish-graphite | 0.145 / 0.008 / 0.002 / 0.003 / 0.004 | 0.049 / 0.004 / 0.001 / 0.002 / 0.002 |

The spread under one bar is the reason the declaration is per group and per state: one group's
number moves from 0.001 to 0.39 across the story, and a single declared value would be false at
both ends. It is also why the declaration follows the dissolve rather than the destination: the
first build declared the arriving photograph the moment the state changed, so for 480 ms the
navigation declared 0.001 over a canvas still painting 0.237. Now the painter reports what it last
painted (which photograph, the one dissolving out beneath it, the alpha, the dim), the page
recomposes exactly that from each photograph's sRGB grid, in encoded values as the canvas does,
and a new declaration goes out on every painted frame. Checked against the canvas's own pixels
through a Nickel to Graphite dissolve, frame by frame under the navigation, finish and order: the
declaration stayed within 0.052 of the painted mean in the light scheme and 0.011 in the dark, the
remainder being the frame React's commit takes to reach the runtime. The lens group is re-measured
over the platter's box while it is open.

## Contrast, on rendered pixels

Method: each glass label captured at device scale 2, then the same frame with the labels made
transparent; the ink is the median of the glyph cores (the tenth of changed pixels that changed
most), the background is the labels-hidden glass under the label's box, and "worst" takes the 5th
or 95th percentile of that background, whichever is nearer the ink. Read at the landing of each of
the seven plane states, 1440 × 900. (The first pass also read each state scrolled, with a sheet in
the fade; that pass predates the Nickel frame and the painted-frame hints and was not repeated.)

| tier, scheme | at rest (hero) | worst label over the seven states (state) | display toggle icon, worst (3:1 applies) |
|---|---|---|---|
| WebGPU, light | 11.08 | 6.70 (graphite, order) | 6.64 |
| WebGPU, dark | 6.61 | 6.48 (nickel, nav) | 6.70 |
| CSS, light | 10.93 | 5.39 (sensor, nav) | 5.39 |
| CSS, dark | 6.01 | 4.94 (lens-90, lens chooser) | 4.17 |
| WebGPU, light, Reduce Transparency | 18.46 | 18.26 | 18.26 |
| WebGPU, dark, Reduce Transparency | 10.35 | 10.05 (lens-45 nav; lens-90 lens chooser) | 10.20 |

At the Body landing (the Nickel frame) the minima are 10.62 light and 6.48 dark on WebGPU, 10.44
and 5.58 on the CSS tier. Every label clears 4.5:1 and every graphic 3:1. It took three changes,
each recorded below; before them the dark scheme measured 2.5 to 4.7 over the deck boards and the
nickel, and 3.0 to 4.4 on the CSS tier's darker bodies.

## Decisions the skill did not make for me

1. **Hints on the CSS tier only.** In 0.24.0 a declared hint does not merely help the CSS tier: on
   the WebGPU tier it replaces the per-surface silhouette tone the renderer measures from the
   texture (`renderer.ts`, `backdropToneHint`), so "declare a hint beside the texture, the pixels
   win" is not what the code does for the body's level. The page declares a measured hint exactly
   where the tier has no pixels (`activeRenderer === "css"`) and nothing on the GPU tier, and it
   describes the frame the canvas holds, dissolves included, not the state the page is heading
   to. The estimator form was rejected for a related reason: platform-web reads a hint for tone
   and ink only when its availability is `author-hint`, so an estimator is reported as
   `analysis: hint` and then not used.
2. **The dark appearance dims the plane** by 0.4, painted into the canvas, the way iOS dims the
   wallpaper under Dark Mode. Without it the dark material over the deck boards and the satin
   nickel sat at L 0.19 to 0.29, the band where neither ink carries text. The windows show the
   dimmed photographs too, because the plane is one thing.
3. **Labels take the runtime's pole at full strength** (`rgb(from var(--vitrea-foreground) r g b / 1)`).
   The published primary is Apple's label alpha (measured ink about 0.81 white), which cannot reach
   4.5:1 on a body above L about 0.16. The pole stays the runtime's pick; the ratio is the page's.
4. **Selection fills come from the opposite pole** (current link, selected finish, focused platter
   row): a highlight under dark ink, a well under light ink. A fill of the ink's own pole lowered the
   label's ratio by up to a point on the CSS tier.
5. **Nothing in a bar may move without resizing.** The runtime re-measures a host when it resizes,
   scrolls or the viewport changes, not when a sibling's reflow slides it along a flex row. The
   first build drew the finish control's glass 77 px from its label and raised same-plane-overlap
   and group-proxy-overlap on load, because the morph's spacer grows from zero after its first
   measurement. So: the lens slot reserves the trigger's footprint with a hidden replica from the
   first render, the trigger is as wide as its widest label whatever is chosen, and the gap between
   groups is derived once as the worst case over both schemes and Reduce Transparency and Increase
   Contrast (50 px at 1440; core's advisory 24 at nominal) rather than recomputed per state.
6. **The glass root is mounted before the page** (`GlassRoot container`), so the navigation is the
   first thing Tab and a screen reader reach; appended to `<body>` by default it was the last.
   The morph portals its host to the end of the plane's host layer, so Tab is routed through the
   bottom bar in its drawn order (finish, lens, order) with six hand-offs, and the open platter
   routes its own Tab and Shift+Tab to order and to the finish (closing as it goes) rather than
   letting the browser continue from the end of the plane into the story.
7. **The page's scroller is a fixed column**, because the scroll-edge mask must sit on the scroll
   container and never on an ancestor of the glass root. The consequence is that nothing outside
   the column scrolls it, so three things are carried to it: wheel events over a bar; the first
   scroll key pressed with nothing focused (focus then moves to the column; it is not taken on
   load, so the first Tab still reaches the navigation); and scroll keys pressed while focus is on
   the floating chrome, with focus left where it is. From the chrome only keys the focused control
   does not own are forwarded: nothing already handled, nothing inside the open menu, no arrows or
   Home/End on the finish radios, no Space on anything Space activates. PageDown on the first
   navigation link scrolls the page by a screen, as it would in an ordinary document.
8. **The scroll edge follows the floating layer, including the platter.** When the lens platter
   opens, the bottom edge rises with its measured box, so the platter stands on the plane its
   texture holds rather than over sheet text the texture cannot see.
9. **The Nickel window is the hero's photograph, closer.** The first build showed a knurled-ring
   macro there, and both bars stood on its defocused grey: the knurling is one diagonal band
   across the frame, the bars are horizontal and centred 808 px apart, a crop anchor has 60 px of
   vertical travel at the cover fit, and bringing the band under both bars needs it steep enough
   to cross both, which it only is over a stretch about 330 px tall, a zoom of about 2.4. Rotating
   the photograph was rejected as re-composing someone else's picture. The hero's photograph is the
   other photograph of a Nickel body, and at 1.5 times the cover fit it puts the satin plates, the
   knurled dials, the strap, board seams and grain under every surface. The macro stays on the
   page as the Nickel card's photograph, where the knurling is the point.
10. **The lens menu's lifecycle is the page's.** The morph gives the platter a shape and nothing
    else. Escape and a choice close it and return focus to the trigger; Tab and Shift+Tab close it
    and move to the bar's neighbours; a press anywhere outside it, or focus leaving it for another
    element, closes it and leaves focus where the reader put it. The first build pulled focus
    back to the trigger after every close, so a click on Order left the menu open and took focus
    from the button the reader had just pressed.
11. **Forced colours keep the finish selection on the radio.** The palette erases authored fills,
    and the finish indicator is one, so both finishes read unselected. The selected radio takes
    the system's Highlight and HighlightText, radius 28 at inset 0 (the capsule's own end), and its
    swatch fills like a checked radio's dot; the glass host is left to the runtime. The pair needs
    `forced-color-adjust: none`, because otherwise Chromium draws its Canvas backplate behind the
    HighlightText label and the word becomes a solid block; the lens platter's focused row had the
    same fault and has the same fix.

## QA lens (§8)

1. `[layer]` Pass. Glass: section navigation, display toggle, finish control, lens chooser and its
   platter, order. Sheets, comparison cards and windows are opaque content.
2. `[layer]` Pass. Links, segments, the trigger and platter rows are plain DOM with fills; the finish
   indicator is a DOM fill because the runtime refuses nested glass.
3. `[layer]` Pass. Six entries, each load-bearing: where am I, how the glass looks, what I am buying
   (two), the commitment, and the setting the skill requires.
4. `[material]` Pass. Regular throughout.
5. `[material]` Pass. No tint; no solid fill; no authored blur.
6. `[material]` Pass. Every state puts rings, blades, contacts, pebble grain or wood grain under
   both bars. The Nickel state, which stood both bars on a macro's defocused grey, is now the hero's
   photograph closer (Decisions, 9): at the Body landing the navigation stands on a board seam, the
   weathered plank and the lens hood's rim, the display toggle on weathered grain, and the bottom
   bar on the strap, the plank's grain, a seam and the camera's lower plate; checked in both
   schemes at 1440 × 900 and 1024 × 768.
7. `[material]` Pass. The leatherette and knurling are photographs of the product, not styling.
8. `[geometry]` Pass. Capsules r22 (span 44) and r28 (span 56, measured 58 on the two bordered housings), platter fixed r28; link pills 16,
   finish indicator resolved concentric by the runtime, platter rows 20; content cards 20 with
   images at 8. Anchor: the viewport edge at radius 0, a square browser window.
9. `[geometry]` Pass.
10. `[geometry]` Pass. 44 / 56 / the platter at about 160, thickness 8 everywhere.
11. `[grouping]` Pass. One group per control, two in the top bar and three in the bottom; 50 px
    between bottom groups, above the runtime's padding in every accessibility state; no text and
    icon button share a group.
12. `[legibility]` Pass; table above.
13. `[legibility]` Pass. At rest only the hero photograph is under the bars; the scroll edge exists
    only where a sheet meets a bar. In the light scheme the fade from pale sheet to a black macro
    reads as a smoky band rather than Apple's soft blurred edge: the web has no blurred scroll-edge
    primitive, and a mask is the honest half of one.
14. `[legibility]` Pass for Reduce Transparency (opaque frost; 18.3 and 10.1:1), Increase Contrast
    (strong border, near-monochrome ink; captured in the first pass), forced colours (the runtime's
    palette, bars still real links and buttons, the selected finish in Highlight on its radio, the
    focused platter row likewise; captured in both schemes) and the receded pose (captured in the
    first pass: no outer shadow). The keyboard completes the page: Tab from the open platter lands
    on Order (Shift+Tab on the finish) with the platter closed; a click on Order closes it and
    leaves focus on Order's own target; PageDown, Space, the arrows and Home on a navigation link
    scroll the page, while the arrows and Home on the finish radios change the finish and Space on
    the toggle presses it. Reduce Motion is verified by code path only: the dissolve steps, smooth
    scrolling is off, the runtime floors its springs. Not captured.
15. `[layout]` Pass. Content reaches the window's edges; insets come from measured boxes every
    frame; the plane is a viewport-fixed canvas and no glass shares the scrolling column.
16. `[layout]` Pass.
17. `[motion]` Pass. The platter morphs out of its trigger (matched geometry) and back; press is the
    runtime's glow and compression on every glass control, the navigation housing included: it is
    `interactive`, so a press on any of its links lights and flexes the capsule (read while held:
    press 1.0, glow 0.97, scale 0.985) while the links stay plain, with no press state of their own
    and no colour swap. Nothing moves at idle. The plane's dissolve is a content state.
18. `[colour]` Pass. The control layer is black or white ink on whatever the photograph lends the
    glass; the only colour on screen is the photographs'.
19. `[honesty]` Pass. GPU: exact texture analysis, no declaration. CSS: declarations measured from
    the frame the canvas holds, re-measured on every painted frame, so a dissolve is declared as
    the blend on screen (table; tracked within 0.052 light and 0.011 dark of the canvas's own
    pixels through a dissolve). Readouts read in the page; zero diagnostics at rest, at every
    landing, with the menu open and mid-dissolve, on both tiers.
20. `[eye]` Compared against the native macOS 27 capture `photo__capsule-button__rest` (light and
    dark, `apps/reference-apple/fixtures`). What the eye sees that the checks do not: Apple's light
    body keeps visibly more of the backdrop's hue where vitrea's is paler and greyer (the ledger's
    chroma-retention gap); Apple's capsule has a crisp dark outer contour and a bright inner line
    where vitrea's rim is a softer diagonal highlight (the named edge gap); Apple's dark capsule is
    more transparent than this page's, which also carries the plane's dark-appearance dim. The
    backdrops differ (a synthetic colour field against camera macros), so levels are not compared.
