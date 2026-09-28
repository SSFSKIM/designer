# Chronograph — a watch under optical glass

A rattrapante chronograph lies on a watchmaker's bench. Its dial runs live under a domed crystal. A
loupe on the mat can be picked up and moved over the dial, and the stopwatch's glass controls sit
beside the watch. It is vitrea's second flagship. The first, Tonight, puts clear windows over a
live sky. This one uses the material as optics: glass you look *through*, bending what is under
it, rather than frosted panels. Built in the main session on `@vitreajs/vitrea-react`, workspace
source (0.24.0 plus the capsule fix in `63b9d6e9`); the project record is
`docs/doperpowers/specs/2026-09-29-chronograph-flagship.md`.

## The record

```
register: instrument, with two optical objects. The watch is the content; the crystal and the
  loupe are glass OVER it with nothing on them, and the chronograph's controls float over the
  bench beside it. The glass never holds the content: the dial, the hands and the loupe's
  enlarged image are all painted into the plane under it.

plane: one viewport-fixed <canvas>, the texture `bench`, painted from the root's own frame loop
  and re-imported every frame. It holds a cutting mat with a 12 px grid and rulers, the maker's
  name printed on it, the strap running off the top and bottom of the window, and the watch: a
  polished case with horn lugs, a tachymeter bezel, a plain flange, and a tapisserie dial with
  three registers, applied indices, a date at half past four and micro-printing at six. The hands
  keep local time, and the small seconds and the chronograph hand beat at eight steps a second
  (a 28,800 vph movement). Under the loupe the same scene is drawn again at twice the size, from
  a watch cache rendered at twice the canvas resolution, so the enlargement stays sharp. The dial
  pattern was chosen for the lens: a square grid is not radially symmetric, so wherever the round
  crystal bends it, the lines curve. A sunburst dial under the same crystal showed almost nothing,
  because a radial pattern under a radial lens only stretches along itself.

floating (role words as on the hosts' data-glass-role):
  lens     the crystal: one circle, base plane, over the bezel's inner edge (0.87 of the case),
           thickness proportional to the case (6 px at the design's 348 px case radius for the
           domed crystal), aria-hidden, no pointer events.
  lens     the loupe: a circle (0.27 of the case radius, 64–96 px), overlay plane so it can pass over
           the crystal, interactive; drag it, or focus it and use the arrow keys (Shift for a
           bigger step, Home or a double click to put it back). It stays out of the controls'
           column, because above them in the overlay plane it would show the bench where their
           labels are.
  control  the dial switch (Day, Night): GlassSegmentedControl, capsule track.
  control  the crystal capsule, which morphs into the Crystal platter (overlay, below-end,
           Escape / outside press / Tab out close it, focus returns): Flat sapphire, Domed
           sapphire, Box hesalite, Apple's glass, and a Reduce transparency switch.
  window   the timing window: running time (written from the root's loop, aria-hidden), status in
           a polite live region, laps table (fastest and slowest splits marked), key hints.
  control  Lap / Reset and Start / Stop, round GlassButtons; Start is tinted green, Stop red.
```

## The material

The runtime's default is Apple's macOS 27 material as measured: a frosted body. The page tunes it
toward clear optics, once, for the whole root (`shared.ts`, `OPTICAL_PROFILE`), and the runtime
reports every group as `tuned`:

- `blurSigma` 0.35, `tintAlpha` 0.06: the body's own blur and white plate nearly gone.
- `sizeOcclusionGain` 0, the heavy-scatter gains 1 and heavy taps 0: a large surface is as clear
  as a small one.
- `backdropToneResponseStrength` 0 and `bodyChromaRetention` 1: the body is the backdrop's own
  level and colour, not a material level solved toward it.
- `rimAlpha` 0.24 (0.115 light, 0.055 dark calibrated): brighter rims, so clear glass still
  shows its edge.
- `lensHeightMax` 160 (20 calibrated): the lens's height law keeps growing with the span past the
  bed's cap, so a large crystal refracts across a band as wide as its size asks.

The lens's profile, gain and reach are left at their calibrated values, so a 44 px button bends
its backdrop exactly as it does on the default material. **Thickness is the per-surface lever**:
depth and displacement both scale with it. The three crystals are three thicknesses (3, 6 and 12
px at the design size), and the fourth choice, Apple's glass, removes the tuning from the whole
page. That shows the calibrated frosted material over the same dial, and the dial all but
disappears under it.

What was tried and rejected, with the lab captures under `docs/research/data/2026-09-29-chronograph/`:

- A flatter lens profile (`lensProfileExponent` 1–2.5, `lensExtentGain` 1) turns a circle into
  a true magnifier, but the profile is root-wide. Rounded rectangles then crease along their
  medial axis and small controls invert their whole interior.
- So the loupe's magnification is **painted**, and the glass over it draws only its own edge. The
  loupe also has to magnify on the CSS tier, which bends nothing. A loupe that enlarged only on
  WebGPU would be a broken loupe on every other engine.
- A pointer-driven glint (the runtime's `sweep` and `shimmer` channels, phase toward the pointer)
  was built and removed: the band is `rimWidth` wide (2.2 to 6.5 px), and at full shimmer it did
  not read on the crystal or the timing window.

## Legibility

Each control group declares the relative luminance painted under its own box (the canvas's
encoded mean, decoded once), re-measured whenever the layout or dial changes. The day mat is pale
(`#e3e8e3`), so light glass on it takes dark ink by a wide margin. The first day mat, a mid sage
(`#56766a`), sat in the ink dead band: the runtime picked black at about 4.2:1 against white's
5:1. The night mat is slate, which takes white ink. The first hints were encoded luma declared as
if they were luminance, and in the day scheme that tipped the ink to black. A hint's `luminance`
is relative (linear) luminance.

## States

- **Reduce Transparency, forced colours and an unfocused window: the lenses step aside.** The
  crystal and the loupe render `present={false}`. The dial stays sharp, and the loupe keeps its
  enlarged image inside a painted ring (forced colours: a `CanvasText` border). Glass *over*
  content that thickens to protect legibility would hide the content it protects. The receded
  pose has a second reason: the runtime composes the receded patch over the app's tuning, so a
  tuned clear crystal fogs when the window loses focus (tracked). The controls recede and frost
  as the material asks.
- **Increased contrast**: stronger rims and ink from the runtime; no page change.
- **Reduce Motion**: the runtime's springs damp; the crystal menu remounts closed when the
  preference changes (the tracked morph seam). The hands keep beating: they are the content.
- **CSS tier** (`?tier=css`): the same page without refraction. The crystal is flat, the loupe
  still enlarges, and the controls are one `backdrop-filter` plus one layer.
- **Layouts**: `wide` puts the watch left of centre with the strap off both edges and the column
  on the right. `stacked` (portrait, narrow) puts settings on top, the strapless head with bare
  spring bars in the middle, the timing window and buttons at the foot, and the loupe resting on
  the crystal over the date.

## Keyboard

Space starts and stops, L takes a lap, R resets, anywhere focus is not already on a control. The
loupe moves with the arrow keys once focused. The Crystal platter is a radio group with arrow
keys, and Escape closes it.

## Honest gaps

- The crystal is Apple's macOS controls lens, tuned and scaled to a 600 px circle. It is not a
  measured watch crystal, and the edge band hides the outer part of whatever lies under it,
  because the lens samples inward by up to its displacement (see the spec's Surprises).
- The whole page is tuned. Only the Apple's glass choice draws the calibrated material, and the
  record says so on the page.
- An unfocused window fogs any tuned glass, because the receded patch overrides the tune. The
  lenses step aside to avoid it; the controls take it.
