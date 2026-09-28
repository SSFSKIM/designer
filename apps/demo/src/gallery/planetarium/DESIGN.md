# Tonight — a planetarium display in clear glass tuned toward a lens

The gallery's flagship page, built in the main session on 2026-09-28 under
`docs/doperpowers/specs/2026-09-28-planetarium-flagship.md`. Part one is the record written before
the first host; part two is what building it changed and what was measured.

## Part one: the record

```
register: spatial — the product's surfaces (a sky guide's window, a Moon module, two ornaments) are
  the interface and the real sky over a place, turning with the Earth, is their environment; a
  display and a guide beside the thing it describes. Named before the first host.
environment: one viewport-fixed WebGL2 canvas on the texture path, supplied as a live canvas: the
  sky over the place at the page's time in a stereographic projection (view centre 36° up, 84° of
  vertical field, panned by drag) — 9,096 catalogue stars as additive sprites, NASA's Milky Way and
  constellation-figure layers sampled through the inverse projection, the Sun, Moon and planets from
  astronomy-engine, airglow, twilight and day from the Sun's altitude, a ridge for the ground. Phases
  (the audit's): night, dusk, dawn, day, as instants of the pinned day. Source statistics: a night
  sky at encoded 0.10–0.18 with the Milky Way to 0.45 and the Moon's glow above it; a day sky at
  0.55–0.75 encoded. Tone input: measured under each group's own box from an eighth-scale render of
  the composite the page paints (dimming included), re-measured every 240 ms while the sky changes
  and on every layout change. Drawn surface levels behind text: the audit's per-line reads (part
  two). Local contrast: the Milky Way and the Moon's glow are the busy regions; by day the sky is
  flat except the Sun's glow, a recorded phase. The published-ink dead band (encoded 0.39–0.49) is
  avoided by the dimming layer's target, not by the source.
windows: window "Tonight" (place, the twilight state and its next change, the chosen object's card,
  the list of what is up), 400 × 560, radius 28, base plane, texture path, its list scrolling inside
  the host with scroll edges at the inner top and bottom; module "The Moon" (phase glyph, lit
  fraction, rise and set, next quarter), 320 × 176, radius 28, base plane; ornament "Place", a 48 px
  capsule in the overlay plane at the scene's top edge in the open sky, morphing into a 400-wide
  platter (radius 24) that opens downward into sky; ornament "Time", a 48 px capsule at the scene's
  bottom edge above the drawn ridge, morphing into the Timeline platter that opens upward into sky.
  Both ornaments act on the whole scene, so they hang at its edges rather than at the window's; the
  environment stays visible around every surface. Gap between groups: the runtime's derived
  padding for this material (20–24 px), never less, with 32 px of air as the design's floor.
  Arrangements (`layout.ts`): standard at 1240 wide and 700 tall or more, if its fit test holds
  (400 px of open sky between window and module, every platter inside the viewport and clear of
  the other surfaces); otherwise compact — the module below a shorter window (360 minimum) in the
  left column, both ornaments in the right column, the Time ornament dropped below an open Place
  platter — and below about 1024 × 700 the compact boxes clamped inside the viewport. Closed faces
  are the anchor's box (Place 320 × 48, Time 372 × 48); the Place platter is 400 × 504, the
  Timeline 400 × 244.
groups: tonight (the window; texture "tonight-sky"; hint measured under its box), moon (the module;
  same source), place (the ornament/platter morph host; same source; box read every frame it moves),
  time (the same). Every hint is { tone, luminance } from the composite under the group's box, the
  tone the pole the level is on; each group's dimming policy names the strength actually painted.
family: thickness 14 across all surfaces (the runtime's own open-morph thickness; the lens depth and
  displacement scale with it); window and module radius 28 fixed; ornaments capsule (24 at 48);
  platters 24 fixed; anchor: the window corner, 28; the card inside 28 − 8 = 20; rows 14.
tint: none. The environment carries the colour; nothing needs finding first.
scheme and pose: colorScheme auto; windowActivation auto. Both schemes are the same environment.
motion: materialise on arrival, with the specular sweep driven once around each rim (page-driven
  `sweep`/`shimmer`, staggered, on the runtime's frame loop, not under Reduce Motion); two matched-
  geometry morphs; press on the closed ornaments the runtime's, inside open platters the page's
  (press, glow and the point written onto the host); the sidereal turn and the time-lapse are
  content; nothing else moves. Reduce Motion: the sweep does not start, springs at critical damping.
tier expectation: webgpu on Chromium over localhost/https; `?tier=css` draws the CSS tier, the same
  design without refraction; cssBody recorded per group at the captured DPR in part two.
accessibility: the runtime follows the system; the page offers Reduce Transparency in the Place
  platter and passes a boolean; forced colours: each host's full-size child draws a 2 px CanvasText
  frame on the WebGPU tier, marks keep outlines; page-owned motion follows Reduce Motion live.
contrast: primary ink from the runtime's token on children; secondary authored at 88 % of the
  primary; measured per rendered line, glyphs suppressed, in every state the audit reads (both
  schemes, four phases, the scrollers, the platter, the CSS tier, the receded pose, reduced
  transparency); 4.5:1 for text, 3:1 for large text and marks; every reading in part two, worst line
  gating.
fidelity: Apple's macOS material composed in Apple's visionOS way, at spans beyond the bed's 160,
  on the clear variant no bed scene declares, with six leaves tuned by the page (the tune table in
  the spec and `shared.ts`): Apple-shaped, not Apple-measured. The runtime reports `tuned: true`.
  Nearest Apple surface: visionOS window glass over a room; no native capture; no comparison made.
material: clear everywhere; the dimming layer painted into the sky under each footprint, adaptive
  (floor 0.16, cap 0.9, composite target linear 0.046), feathered 22 px inward; uncalibrated.
```

### The tune, and why each leaf

See `shared.ts`, `tuneWith`, and the spec's table. In one sentence: the shipped material makes a
window-sized clear body a plate by three fitted laws of the regular material — the heavy scatter
component's chain level, the size law's occlusion facet, and the tone response with its black
branch — and by a nominal base blur of 4; the page sets those to a lens's values and touches nothing
else. `?sigma=`, `?alpha=` and `?tone=` on the URL draw other values, capture aids for the sweep.

### Data and credits

`images/CREDITS.md`: NASA/Goddard SVS Deep Star Maps 2020 (Gaia DR2: ESA/Gaia/DPAC), the Yale
Bright Star Catalogue (CDS V/50, public domain), astronomy-engine (MIT). The Place platter carries
the credit line on screen.

## Part two: what building it changed, and what was measured

### What the sweep found, and what the tune became

The page was first drawn with the shipped clear variant and one tuned leaf, its base blur (σ 1.0),
on the assumption that the blur was what fogged a window. It was not. In order, on real hardware
(Chromium on the Apple GPU, 1440 × 900, `?at=22:30`, captures under `tmp/flagship` on the build
machine and the sweep's readings in the spec's Surprises):

1. Base σ from 0.05 to 30 and tint alpha from 0 to 0.9 left the window body a flat plate, lighter
   than the sky: the body samples the scatter chain's heavy level at window span. `sizeScatterGainMax`
   (and its 2x forms) at 1 made the heavy level the sharp one, and the sky appeared through the
   glass with the constellation lines bent at the rim.
2. The light material still drew the window at encoded 0.42 over a 0.15 sky (the ink dead band;
   the first audit's worst light line, "Moon", 4.13 against ground 108/106/107): the fitted tone
   response and its black branch. Both at 0 for clear.
3. The size law's occlusion facet, a twentieth of white on the light material, went to 0.
4. The Milky Way layer's faint-star grain drew contour-like ripples through the lens and a
   per-frame dither crawled under it; the map was smoothed by 1.1 px and the dither fixed.
5. Base σ settled at 0.6 (window σ about 3 px at 1x): stars soften to points, lines stay lines.

### Layout changes the page made against its first placement

- The Time ornament first hung below the window and its platter opened upward over the window,
  showing sky where the eye expected the window's glass; the Place ornament's platter opened
  downward over it. Both ornaments moved to the scene's edges in the open sky (record, `windows:`).
- The Time ornament first sat on the ground's flat dark; the layout now asks the projection where
  the drawn ridge crosses under it and keeps the ornament above.
- The window's side padding grew from 22 to 40 px so no line sits in the lens band (47 px at
  thickness 14).
- The dimming feather scales with the host (12 % of the shorter span, 5–16 px): a fixed 22 px left a
  48 px capsule half undimmed by day and lifted its declared level into the light pole, so its ink
  went dark on a body that was in fact dark (the second audit's Time lines at 2.2–2.9). The
  footprint measurement moved from an eighth to a quarter scale for the same reason.
- `directionOfObject` took degrees where every caller passed radians: the card said ENE where the
  list said ESE and the drawn Moon stood in the wrong place. Found by `test/planetarium.test.ts`.

### Contrast — every rendered line and mark on glass

Method: the audit's per-line read on glyph-suppressed captures (`glass-audit.mjs`, `lineContrast`):
each line box's computed ink against the mean ground under it, 4.5:1 for text, 3:1 for large text
and marks. Matrix: WebGPU × light and dark × the first viewport, the window's scroller at top,
middle and bottom, the Timeline platter open, the four phases (night, dusk, dawn, day); the CSS
tier (`?tier=css`) for the same; the receded pose; reduced transparency. The final audit (the
fourth, after the review's fix wave), 2026-09-28,
`docs/research/data/2026-09-28-planetarium-flagship/audit/planetarium.json`; the third, before
the wave, read the same counts and worst lines.

| state | lines | pass | worst |
|---|---|---|---|
| WebGPU · light · rest, scrollers, platter | 306 | 306 | 5.10 |
| WebGPU · light · four phases | 218 | 218 | 4.69 |
| WebGPU · dark · rest, scrollers, platter | 306 | 306 | 6.12 |
| WebGPU · dark · four phases | 218 | 218 | 5.46 |
| CSS · rest, scrollers, platter | 306 | 306 | 5.15 |
| CSS · four phases | 218 | 218 | 4.68 |
| receded pose | 241 | 241 | 5.10 |
| reduced transparency | 55 | 55 | 6.45 |

**No reading is below its floor in any state.** The pooled glass-text sample: 172 of 172 pairs in
each scheme. No host's drawn body sits in the published-ink dead band in any state read
(`hostLuminance`, inside and a 24 px ring). The first audit had 227 readings below the floor (the
day phase's dead-band bodies and the light material's plate), the second 35 (the Time ornament's
half-feathered capsule by day, and the secondary ink on lifted rows at 4.35–4.46); the third and
the final none. The 68 audit captures and 10 captures of the page's states (both schemes, day,
dusk, both platters, the CSS tier, a 2× rim crop, the 1366 × 768 and 1024 × 700 arrangements) are
hashed in `captures.sha256` beside the audit and archived as GitHub release
`planetarium-flagship-2026-09-28` (zip SHA-256
400298c3b30738209d134f0f1920f1c86b0cba1ff9feb9c9bc9066c28b9d56b1).

### What the runtime reports

Every group: `webgpu / gpu-texture / refraction true / analysis exact / health ok`, variant `clear`,
`materialDocument apple-macos-27.0-glass0.5`, `tuned: true`, the dark or light profile key by
scheme. The CSS tier: `css / css-backdrop`, `cssBody two-layer` for all four groups at device scale
1 (the four hosts sum to 0.31 M device px; at scale 2 the same page collapses, 1.2 M). Diagnostics:
zero on both channels in every pass. Ban subset and spatial ban subset: zero findings. Forced
colours: the runtime draws no glass (0 surfaces, 0 backdrop-filter elements), policy as asked.
Reduced transparency through the page's own switch: policy as asked, material moved. Glass covers
24.2 % of the first viewport.

### Measured under each footprint (page readout `window.__tonightReadings`)

Night, 22:30, dark scheme: raw 0.014–0.030 linear under the four hosts, strength at the floor
0.16, composites 0.013–0.028 (encoded 0.12–0.18), every hint `dark`. Day, 13:00: raw 0.35–0.67,
strengths 0.87–0.92, composites 0.061 (window), 0.104 (module, under the Sun's glow), 0.081 (Place),
0.118 (Time), every hint `dark`, white ink throughout.

### Motion, read at runtime

The materialise sweep: `--vitrea-shimmer` reaches 1.0 on each host in turn over the first two
seconds, `--vitrea-materialization` 0.54 → 0.97 → 1 across the first 300 ms. A press inside the
open Timeline platter writes press 0.69 / glow 0.64 to its host while held and decays to
0.0005 / 0.08 within 600 ms of release. A live Reduce Motion flip with the platter open remounts
the morph closed at 346 × 48 with focus on its trigger; Enter reopens it to 400 × 242; Escape
closes it with focus on the trigger. The time-lapse advances 17 minutes of sky per 1.5 s.

### Gaps found in the runtime (for its tracker)

- The clear variant at window span is opaque by three regular-material laws (the tracker entry of
  this date), not by its own constants; `adaptation: "constrained"` is unread.
- `samplingPaddingFor` does take `variant` on 0.24.0; the tracker's sentence that it does not is
  stale.

### The independent review and its fix wave

2026-09-28, after the third audit. The review (a `doperpowers:reviewer-high` reading of the whole
page against the cookbook) found twelve items, ten must-fix; one fix wave closed all twelve, each
with its own probe or unit test, and the sky test grew from seven cases to seventeen:

1. No narrow-viewport arrangement: at 1024 × 768 the Place platter opened over the module and at
   390 × 844 the controls left the viewport. Fixed by the compact and clamped arrangements above,
   a fit test (162 viewport × azimuth cases in the unit suite), and the Place platter's true
   height (504, not the 352 first written) in the layout's own numbers.
2. The closed morph face measured once at its content's width, so a longer place name was clipped
   after a change of place. Faces are now the anchor's box with ellipsis; Place is 320 wide.
3. The Timeline's origin moved with the scrubbed time, so End jumped to the next noon. The night
   is taken once when the platter opens and held.
4. The selection ring kept the RA/Dec from the moment of choosing while the Moon moved (154 px
   off after a day of playback). Bodies are resolved from the frame's own positions.
5. The Moon's lit limb was the chord between two projected points, wrong by up to 175° and
   falling to screen-right when the Sun did not project. It is the projected tangent toward the
   Sun (`sky/limb.ts`), 0.01° from an independent great-circle step in the test.
6. Local noon and the wall clock used the current instant's offset across DST; `zonedInstant`
   resolves a wall time at its own offset and a night is 23–25 hours (`nightSpan`).
7. Twilight was classified on refracted altitude against geometric floors, counting refraction
   twice (Seoul, three minutes before sunrise, read as day). Geometric altitude now.
8. The next twilight event assumed the Sun would reach the boundary it was heading for; at
   Reykjavík in June it never does. Both boundaries are searched and the earliest taken.
9. The measurement target's output texture leaked across resizes. Kept and deleted with its
   framebuffer.
10. No keyboard path turned the sky. The canvas is a focusable application: arrows turn by 5°,
    Shift-arrows by 20°; choosing a row in the window turns the view to an object out of view.
11. The Place options claimed radio semantics without arrow keys. Roving focus and arrows now.
12. Tab out of a platter's last control left it open. Tab there, or Shift-Tab on the first, closes
    it with focus on the trigger.

Three things the wave saw and left, taken by the session after it: the module's third column
reached the rim with "Sun 11 Oct" (now "11 Oct"); the Time capsule's floor was read at its centre
alone and its end crossed the ridge at some azimuths (read across its width now); and the height
gate for the standard arrangement (820) sent common laptop viewports to compact, where the fit
test alone was enough (700 now). The page's first automatic selection no longer scrolls a short
window's header away.

### Recorded limits and decisions

- **Apple-shaped, not measured.** Six tuned leaves; no native clear capture; spans beyond the bed.
- **Minimum viewport 1024 × 700**; below it the compact boxes are clamped inside the viewport and
  may overlap the window. The page is a desktop display.
- **Day is flat.** By day the sky is a gradient with the Sun's glow; the lens has little to bend.
  Content shown as it is; recorded.
- **Ornaments hang at the scene's edges**, not the window's: they act on the whole scene, and a
  window-attached platter on the texture path opens over the window.
- **The Moon and the Sun at five times their angular size**; the canvas's label says so.
- **`[eye]`.** Nearest Apple surface: visionOS window glass over a room. No native capture exists
  in the harness; no comparison was made. Seen by eye without one: the lens band on the 48 px
  capsules is the whole capsule, which reads as a thick lozenge (visionOS's ornaments do too); a
  faint ripple survives at the window's top-left corner at device scale 2 where the lens crosses the
  Milky Way's residual grain; the light material's clear body is a faint milky sheen where the dark
  one is nearly invisible, both transmitting the sky.
