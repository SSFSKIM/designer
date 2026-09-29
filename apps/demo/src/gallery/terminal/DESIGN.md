# Terminal — a shell running on clear glass over Lake Tahoe

A terminal window made of Liquid Glass, its text written directly on the glass, over a relief map
of the Lake Tahoe basin drawn from real elevation data. Version 1 of the terminal-on-glass idea,
built in the main session on 2026-09-29 on `@vitreajs/vitrea-react` (workspace source, 0.24.0).
The shell is simulated, because the page is static: it runs over a snapshot of this repository,
says so in its greeting, and refuses what would need a real machine (`shell/types.ts`). Part one
is the record written before the first host; part two is what building it changed and measured.

## Part one: the record

```
register: spatial — the terminal window is the interface and the basin is its environment, the
  desktop it sits on. A window holding one app's content on one canvas, with its controls hung
  at its edges as ornaments. Precedent for text directly on clear glass: macOS 26's Terminal,
  whose Clear Light and Clear Dark profiles are "inspired by Liquid Glass". Named before the
  first host.
environment: one viewport-fixed 2D canvas on the texture path (`tahoe-relief`), painted from
  `data/relief.*` (built by `scripts/build-terminal-relief.mjs` from Terrain Tiles on AWS, the
  USGS 3D Elevation Program at about 30 m): the hillshade tinted per scheme, contours every 50 m
  with index lines every 250 m, the lakes flat with water lines along their shores, the
  California–Nevada line, and labels (summits with the height the data reads, towns, lakes).
  Framed so Lake Tahoe lies under the window's first position: the lake's flat water is the calm
  area behind the text, and the shores' dense contours cross the window's left and right rims,
  where the lens bends them. Phases (the audit's): the window over the lake, over the east shore
  (the Carson Range, the densest contours) and over the west shore (Desolation Wilderness).
  Tone input: measured under each group's own box from a quarter-scale copy of the composite the
  page paints, dimming included, on every move. The drawn levels behind text are the audit's.
windows: window "Terminal" (title line naming the session and its size; the xterm.js viewport,
  DOM renderer, system monospace 13 px), base plane, texture path; 880 × 560 at the standard
  viewport, never below 520 × 320 where the viewport has room and never below 296 × 160 anywhere
  (a 320 px phone less its margins, about 30 columns; the title line and five rows); dragged by
  its title line and resized from its lower-right corner by pointer, a resize holding the left
  and top edges; the terminal's grid refits to the box and the shell hears the new size.
  Ornament "Sessions": a capsule of tabs above the window's top edge, left-aligned, and a
  separate capsule for a new session beside it (a text group and an icon group never share
  one); tabs shrink from 116 to 36 px to stay within the window, showing the number alone below
  64. Ornaments "Profile": below the bottom edge, two segmented controls — Glass (Clear,
  Regular) and Appearance (Dark, Light) — and a Reduce transparency toggle, three groups at
  the runtime's derived gap, packed into as many rows (up to three) as keep each no wider than
  the window, each row centred under it. A 28 px band at the viewport's foot holds the terrain
  credit, plain text on an opaque plate. Every ornament is attached to the window and moves with it, in the
  overlay plane, outside the edge by the derived gap, never straddling it. No platters: nothing
  opens over the window, whose see-through glass a platter would punch a hole in.
groups: terminal (the window), sessions, new-session, glass, appearance, transparency; every one
  reads the texture, and each declares the composite measured under its own box.
family: window radius 22 (a working window's tighter corner, the macOS reading: dense work
  wants structure), thickness 12, the lens band's width set into the window's padding; ornaments
  capsule 44 tall, thickness 8; anchor: the window corner.
tint: none. The map carries the colour; nothing on the page must be found before it is read.
scheme and pose: the Appearance choice is the root's colour scheme, following the system until
  the person picks one; windowActivation auto.
motion: materialise on arrival, except the two segmented controls, which take no `present` and
  are mounted once the rest has materialised (a tracked gap); drag and resize are the person's
  own motion, the dimming layer following the window under its footprint; the terminal cursor
  blinks unless Reduce Motion; the shells start once the tier the page asked for is drawing,
  the glass has finished materialising and the page has measured under the window, and the
  first one's intro then types `glass` and `git log --oneline -8` unless Reduce Motion, when they
  appear at once; nothing else moves.
tier expectation: webgpu on Chromium over localhost or https; `?tier=css` draws the CSS tier.
accessibility: the page offers Reduce transparency and passes a boolean; the terminal's
  accessibility tree is xterm's screen-reader mode; Tab completes in the shell, so Shift-Tab
  leaves the terminal backward and Escape then Tab leaves it forward (`help` says so);
  forced colours: Canvas panels with CanvasText frames, on the WebGPU tier drawn by the page on
  children and pseudo-elements, never on a host. Arrow keys move between tabs and keep focus
  there; a click, Enter, a new session or a closing one puts focus in the terminal.
contrast: the runtime's ink on the page's own labels; the terminal's sixteen colours are the
  page's ink on a child, one set per ink polarity the runtime picks for the window, each colour
  held to 4.5:1 on the drawn body; measured per rendered line, glyphs suppressed, in every state
  the audit reads.
material: two, one at a time for the whole page. Clear: the clear variant tuned toward a lens
  (the planetarium's leaves, base σ chosen for text) with the dimming layer painted into the map
  under every footprint, darkening for Dark and lightening for Light, adaptive, feathered inward;
  uncalibrated. Regular: vitrea's calibrated macOS 27 material, untuned, no layer painted.
  Clear is the default because a terminal on glass is the brief; the skill's rule that a reading
  surface is regular is broken on purpose and on the record, with Apple's own Terminal as the
  precedent and Regular one choice away.
fidelity: Apple's macOS material composed as a window over an environment, at spans beyond the
  bed; Clear is Apple-shaped, not Apple-measured, and the runtime reports `tuned: true` for it.
  Nearest Apple surface: macOS 26 Terminal in Clear Dark over a desktop picture; no native
  capture; no comparison made.
```

## Part two: what building it changed, and what was measured

### What the first captures changed

On real hardware (Chromium on the Apple GPU, 1440 × 900 unless named; captures under
`tmp/terminal` on the build machine):

1. **The lakes were not drawn.** The build script's Douglas–Peucker simplification took a closed
   ring's first chord, from a point to itself, as having no length, so every point lay at
   distance zero from it and every ring — every shore and every hilltop contour — collapsed to
   one point. Rings are now split at their farthest point and each half simplified; the map went
   from 336 lines to 1,196, and the lakes, islands and summits' closed contours appeared.
2. **The dark map had no lake.** The first dark palette put the water within a few codes of the
   shaded land; the land was lifted and the water deepened until the shore reads at a glance.
3. **Map labels under ornaments read as second words.** A town's name under the Sessions capsule
   showed through the small, nearly sharp clear surface beside the tab's own label. Ornaments
   now take a higher dimming floor (0.62) than the window (0.2), and Lake Tahoe's name moved to
   the north basin, out from under the window's first place.
4. **The first texture import warned.** Supplying the canvas before its first paint made the
   WebGPU tier try to import a canvas with no pixels. The texture is now supplied in the frame
   that first paints it.
5. **The intro's `glass` reported the moment before the map.** Under Reduce Motion the intro is
   written at once, and it read the runtime while the window was still the CSS tier's
   `no-texture-supplied` fallback. Gating the shells on the texture alone was not enough (the
   review, below): the shells now wait for the tier the page asked for, the end of the arrival
   materialisation and the page's first measurement, so the report names the material on the
   screen.
6. **Two colours fell short over the west shore.** The first audit, run against a stand-in shell
   printing all sixteen colours, read Clear Light's dark-ink yellow at 4.46 and its grey at 4.35
   over the Sierra crest's shaded slopes (phase `west-shore`), and, in Clear Dark, the selected
   tab's number at 4.41 on its lifted fill. The dark-ink set moved a step darker and the secondary ink's share rose from
   70 to 80 per cent. The second audit read that grey at 4.44 on the CSS tier's collapsed body at
   the same place, and it moved once more.

### The shell

Built by a separate worker against `shell/types.ts` and reviewed on its own (its report: six
findings, all fixed with tests). It runs over `shell/content.json` (252 KB: 4,018 of the
repository's files by name, 14 readable in full, the last 60 commits with their parents, and one
real `pnpm test` run of `packages/core` with its timing), written by
`scripts/build-terminal-content.mjs`; re-run it after changing this file, which is one of the 14.
`test/terminal-shell.test.ts` drives the shell through a headless xterm.

### Weight

The page's script is 660 KB (183 KB compressed): xterm.js, the page, and the shell with its
snapshot, which is imported statically. The map is 330 KB of hillshade and 235 KB of vectors.
Loading the snapshot lazily is the obvious next saving.

### The independent review and its fix wave

2026-09-29, after the second audit. The project's registered reviewer (`doperpowers:reviewer-high`)
ran on GPT through the Codex gateway and stopped on the accounts' usage limit (HTTP 429) before
reporting; the same brief was then given to a Claude Opus agent under a read-only instruction,
which is recorded here as a departure from the review route. It reproduced each finding in
Chromium. One fix wave (also Opus) closed all of the following, each reproduced first and
verified after:

1. **Arrow keys in the tabs pushed focus into the terminal**, because a session focused its
   terminal whenever it became active. Focus now follows only an explicit activation.
2. **Ornament rows were not fitted.** The wrapped row was reserved at one gap and placed at
   another, and nothing held a row inside the viewport: on a 390 × 844 phone on Regular a switch
   started at x = −11 and another ended off the bottom, and four tabs made a capsule wider than the
   window. The rows are now packed and reserved by the same function, the tabs shrink, and a check
   across five viewports, both glasses, one and four sessions and Reduce Transparency found every
   host inside the viewport and every pair of groups at least its sampling padding apart.
3. **The intro's report could name the wrong tier** (1 cold load in 8 printed `css` on a WebGPU
   machine, and `?tier=css` printed `two-layer` 170 ms before the body collapsed). See item 5.
4. **The hillshade was lit from the south-west.** The build script's illumination term was
   `cos(az − π/2 − aspect)`; ESRI's, for this gradient convention, is `cos((450° − az) − aspect)`.
   The data was regenerated; the relief reads the right way up now.
5. **Forced colours framed only the window** on the WebGPU tier; the ornaments now carry their
   frames on pseudo-elements.
6. **A short viewport gave a window below span 96**, and a negative height below about 230 px.
   The floor above holds it.

And the minor ones: the segmented controls mount once the rest has materialised; the idle frame
loop no longer reads six footprints every frame (0 reads over 2 s idle, one per 120 ms in a drag);
the texture is supplied again after a cleanup (not testable end to end, because a root rebuild
throws in vitrea-react, a tracker entry); the gap follows the window's live size; a corner resize
holds the window's left and top; the React root sits inside `<main>` (axe's `region` rule); the
canvas is sized to the viewport the painter uses; the terrain credit is on the page and in
`data/CREDITS.md`; the contours sit at pixel centres; and the elevation range is read from the raw
grid (1,189–3,314 m, where the blurred grid had put the top below Freel Peak's own reading).
The audit's east and west phases move the window as far toward each shore as the viewport allows,
about 7 km at 1440 wide.

Left, and why: no pointer or keyboard alternative to dragging the window (WCAG 2.5.7), because
nothing on the page depends on where the window stands; the terminal precedes the tabs in tab
order, because the runtime's planes order the DOM; the declared hint trails a profile switch by
one frame; and the runtime's white forced-colours panels under a dark forced palette, a tracker
entry.

### Contrast — every rendered line on glass

The audit's per-line read on glyph-suppressed captures (`glass-audit.mjs`), 4.5:1 for text: the
final run, after the fix wave, on `?intro=instant` (the intro's `glass` report and git log),
2026-09-29.

| state | lines | pass | worst |
|---|---|---|---|
| WebGPU · light · first viewport | 70 | 70 | 5.95 |
| WebGPU · light · lake, east shore, west shore | 210 | 210 | 5.20 |
| WebGPU · dark · first viewport | 70 | 70 | 5.38 |
| WebGPU · dark · lake, east shore, west shore | 210 | 210 | 5.35 |
| CSS tier · first viewport | 70 | 70 | 5.84 |
| CSS tier · three phases | 210 | 210 | 5.06 |
| receded pose | 70 | 70 | 5.95 |
| reduced transparency | 70 | 70 | 7.60 |

No reading is below its floor in any state, and no host's drawn body sits in the published-ink
dead band. Diagnostics zero, ban subset and spatial ban subset zero, forced colours draw no glass,
Reduce Transparency through the page's switch moved the material as asked. Glass covers 40.6 % of
the first viewport. The CSS tier's body is `collapsed` for every group at device scale 1: the
window alone is 492,800 device px, over the 400,000 at which the tier folds its two layers. The
audit's JSON is in `docs/research/data/2026-09-29-terminal-gallery/`.

### Recorded limits

- **Clear is uncalibrated.** Ten tuned leaves, the planetarium's with this page's base σ, and a
  page-painted dimming layer; the runtime reports `tuned: true`. An unfocused window composes the
  receded patch over the tune and frosts (the chronograph's tracker entry); the text stays legible
  there (the receded row above).
- **The smallest viewport that fits the floor and its ornaments** is 320 wide, 336 tall on Clear
  and 416 on Regular on a wide screen, and 472 (Clear) or 632 (Regular) at 320 wide where the
  controls take three rows. Below that the window's top-left stays on screen and the rest
  overflows.
- **A map label under an ornament** still shows faintly through the small, nearly sharp clear
  capsule in the dark scheme (Tahoe City beside the first tab); the floor of 0.62 makes it a
  ghost, not a word.
- **`[eye]`.** Nearest Apple surface: macOS 26 Terminal in Clear Dark over a desktop picture. No
  native capture was made; no comparison.
