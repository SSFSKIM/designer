# W28 G4 eye read

Read 2026-09-15 from the three sheets in `sheets/`, after the inactive rows were measured
and the canonical matrix was written. Two of them put the demo's two poses beside the
harness capture of an inactive scene, one per colour scheme; the third is the same page
under a real focus change rather than a pin.

- **The demo, light (`demo-and-harness-light.png`).** Pinned inactive, every surface on the
  page loses the two things the endpoint removes, and they are legible separately. The broad
  outer shadow goes: in the amplified difference the toolbar's three controls, the star, the
  `Publish` button and the two ink plates each leave a soft rectangular halo where nothing
  else differs, which is the shadow field and not the body. The bright rim goes with it — the
  `Regular material` pane over the DOM column reads as a flat card in the inactive frame where
  the active one has a lit upper edge. The author tint survives as an achromatic shade exactly
  as the document says it should: `Publish` is orange when active and a pale neutral when
  inactive, at what looks like the same lightness, and the blue star button greys the same way.
  The bodies themselves barely move — this is a pose that removes structure rather than one
  that dims.
- **The demo, dark (`demo-and-harness-dark.png`).** The same families, on the dark endpoint.
  The `Larger surface` pane over the texture region is the clearest: active it is a dark pane
  with a visible lit edge, inactive it is flatter and very slightly lighter through the body,
  with the edge gone. The `regular` chip below it does the same at a smaller span. Nothing in
  the dark sheet suggests a different mechanism from the light one.
- **A confound in both demo bands, named rather than cropped out.** The playground's texture
  region is an animated canvas, so the two poses are captured at different animation phases
  and the middle third of every difference strip is the animation, not the recede. The pose is
  read on the DOM-backdrop column, the panel and the controls, where nothing moves between the
  two frames. A page whose backdrop held still would make the same point without the
  distraction; the playground is the page with the pin on it, and the pin is the operable path
  this sheet is about.
- **The harness band, both schemes.** `photo__rrect-md__inactive` at 2× — Apple's capture, the
  WebGPU row this wave published, and their amplified difference. The bodies agree closely in
  level in both schemes: the difference is not a flat offset over the pane. What it is, is a
  strong band following the whole contour and a low-frequency structured pattern across the
  interior — the two residuals §5.146 named as structured transfer and the rim/lens band, seen
  here on a cell that is not in the checking set. The light band's contour reads slightly red
  on one side and blue on the other, which is the lens displacement rather than a level error.
  These are the same gaps the G2 sheets carry, unchanged by the landing, and they are what the
  user's eye on those sheets is being asked about.
- **A real focus change (`real-focus.png`).** With the pin on `auto` and the machine's own
  frontmost application switched to the Finder, the page recedes — and this is the first
  reading in the project where a window manager, rather than a test, moved the pose. The
  backgrounded frame is visibly the inactive pose on every surface at once, and making the
  browser frontmost again restores it. The runtime's own readout agrees at each step:
  `hasFocus` true / `active`, then false / `inactive`, then true / `active` again. Note that
  `document.visibilityState` stayed `"visible"` throughout, which is the whole reason the
  observer does not listen to `visibilitychange`.

The reading the sheets support is narrow and worth stating narrowly. They show that the
endpoint an adopter gets is the endpoint the matrix measured, that it is reachable both by
pinning and by losing focus for real, and that the pose removes the shadow and the rim and
keeps an achromatic tint. They show nothing about the transit between the two poses — the
captures are settled endpoints — and they do not close any residual §5.146 named. The light
`hc-text__rrect-sm__inactive` control is not on these sheets; it is on G2's, and it is still
visibly too bright there.
