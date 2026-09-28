# Chronograph — a flagship for vitrea's optics

Status: landed 2026-09-29. Page: `apps/demo/gallery/chronograph/`, source
`apps/demo/src/gallery/chronograph/` (its record is `DESIGN.md` there). Evidence:
`docs/research/data/2026-09-29-chronograph/`.

## Purpose

The user asked for one design, made in the main session, that shows what vitrea can do at its
fullest: every capability, the material's aesthetic potential, and "more optical glass than frosted
glass". They asked for it to be the main session's own, without reference to the flagship another
session had built (Tonight, `2026-09-28-planetarium-flagship.md`, which this work did not read).

The page answers that with an object whose glass *is* optics: a watch crystal. It adds a loupe,
because a magnifier is the optical tool, and the stopwatch's Liquid Glass controls beside the
watch, which are the same tuned glass used as UI. It is meant to be the page someone opens to see
that the web can bend a live image through glass, and to see the difference between Apple's frosted
material and clear optics by switching between them.

## Design

See `DESIGN.md` for the record: the plane, the surfaces and their roles, the material tuning, the
legibility measurements, the accessibility states and the layouts. In one paragraph: one canvas
paints a cutting mat and a rattrapante chronograph live, and the hands beat at 8 Hz. A round crystal
in the base plane and a movable loupe in the overlay plane refract it. A timing window, two round
buttons, a dial switch and a crystal capsule that morphs into a platter run the stopwatch. The
whole root is tuned from the calibrated macOS 27 material toward clear glass, and the Crystal
platter puts the calibrated material back for comparison.

## Decision Log

1. **The subject is an optical object, not a panel of text on glass.** A watch crystal makes
   refraction the point of the page. The other candidates were a camera viewfinder with zoom lenses
   and a darkfield microscope. They were offered to the user as a non-blocking choice while the
   optics experiment ran; there was no answer by then, so the recommended one was built.
2. **Tune the body, keep the lens.** On the lab bench (`apps/demo/lab/optics/`), the calibrated
   macOS 27 body is a frosted plate at every span. Removing the plate, the blur, the size law's
   occlusion and heavy scatter, and the tone response gives clear glass whose calibrated lens
   already reads as liquid glass at every size (`lab/optical-body-calibrated-lens.jpg`). The lens
   leaves stayed calibrated. `lensHeightMax` was extended from 20 to 160, so a large surface
   refracts across a band proportional to its size, and `rimAlpha` was raised to 0.24 so the edge
   of clear glass still shows.
3. **The loupe's magnification is painted, not a lens profile.** A flatter profile
   (`lensProfileExponent` 1–2.5, extent to the radius) makes a circle an exact magnifier, since
   the displacement then grows linearly toward the edge. But the profile is root-wide: it creases
   rounded rectangles along their medial axis and inverts small controls
   (`lab/flat-profile-rejected.jpg`, `lab/magnifier-profile-rejected.jpg`). A loupe also has to
   magnify on the CSS tier, which bends nothing. So the page draws the scene at twice the size under
   the loupe, and the glass draws its edge.
4. **A tapisserie dial.** A radial pattern under a round lens only stretches radially and shows
   no curvature, and the first sunburst dial hid the crystal almost entirely. A square grid bends
   wherever the lens displaces it.
5. **The lenses step aside where the material would thicken.** Under Reduce Transparency, forced
   colours and an unfocused window, the crystal and the loupe go `present={false}` and the loupe is
   drawn as a ring. They are glass over the content, so frosting them to protect legibility would
   hide the content itself.
6. **A pale day bench.** The first day mat, a mid sage, drew light glass inside the published-ink
   dead band. Black ink was picked at about 4.2:1 against 4.5. The pale mat puts dark ink far from
   the band, and the night scheme keeps a slate mat with a lamp pool.
7. **Secondary ink is the page's own.** The runtime's secondary token is solved against the
   calibrated body. On the tuned glass it read 4.26–4.49:1 in the light scheme and 3.6 in the dark
   platter. The page authors `--ink-soft` per dial (black 0.68, white 0.76), and the audit then
   passes every enabled text line.
8. **Scope held.** No glint: the sweep channel was built and removed (Surprises 3). No spare-crystal
   tray: the liquid union was left out rather than invented for the page. No crown or time-setting:
   the stopwatch is the function.

## Surprises

1. **A hint's `luminance` is relative (linear) luminance.** The first hints declared the canvas's
   encoded luma. The runtime reads the number as linear, so 0.2 encoded became 0.48 encoded behind
   the glyphs, which crossed the ink crossover. The skill's cookbook now says so (vitrea.md §2).
2. **`GlassSurface capsule` lost its capsule on any other prop change.** The patch effect sent the
   `radius` prop's radii over the measured capsule radius, and the capsule effect never re-applied.
   A tinted Start button became a rounded square the moment it turned into Stop. Fixed in
   `@vitreajs/vitrea-react` with a regression test and a patch changeset (`63b9d6e9`). A narrower
   first-frame gap remains (tracker).
3. **The sweep does not read.** The highlight pass's sweep band is `rimWidth` wide: 6.5 px on the
   light document, 2.2 on the dark one, and inside the contour only. With the channel held at full
   shimmer and a fixed phase, neither the 600 px crystal nor the timing window showed a visible arc
   at 2x (tracker).
4. **An app's tune does not survive the receded pose.** `posedProfile` merges the receded patch
   over the active profile, which already includes the app's `materialProfile`. The receded
   patch's scatter, heavy-tap and tone leaves therefore override the tune, and a clear crystal fogs
   when the window loses focus. This is by the runtime's design (the receded document is a
   difference over the complete active endpoint), but for a tuned page the receded endpoint is
   undefined (tracker).
5. **The edge band hides what lies under it.** The lens samples inward by up to its displacement,
   about 45 CSS px at the domed crystal's design size. The outermost band of the dial under the
   crystal is replaced by an enlargement of the dial just inside it. That is why the flange carries
   no printing: the lens hides it.

## Deferred

1. A per-surface lens profile, or a lens mode that magnifies, so a loupe could be the material's
   own on WebGPU without creasing the page's other shapes. That is a runtime design question, not a
   page one.
2. A tune that composes over the receded patch, or a receded endpoint derived from a tuned active
   one (Surprises 4).
3. A sweep band whose width is its own leaf rather than the rim's (Surprises 3), after which a
   pointer glint is worth building.
4. The liquid union (`mergeDistance`) shown on a page with a reason for it; this one did not have one.

## Outcomes and Retrospective

- The page landed with zero runtime diagnostics in both schemes, zero page errors, zero ban
  findings, zero glass drawn under forced colours, and every enabled text line at or above its floor
  in both schemes and with the menu open (`audit.json`). The one failing line is the disabled
  Reset label, an inactive control that WCAG 1.4.3 exempts. The gallery e2e passes in both
  schemes. Frame rate on this machine: 80 fps at rest and 72 while dragging the loupe (2x, WebGPU).
- What the page shows that no earlier gallery page did: clear glass at every size with the
  calibrated lens, a domed crystal whose band curves a grid, a movable magnifier, and the
  calibrated material and the tuned one on the same scene one click apart.
- The one design error the process caught late was the hint's luminance space. It cost a wrong ink
  on the first day bench and is now one line in the skill.

## Revision Notes

- 2026-09-29: written at landing.
