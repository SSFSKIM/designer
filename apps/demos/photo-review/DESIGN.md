# Ashcombe — design law

The project design law for `apps/demos/photo-review/index.html`, a desktop culling and adjustment
tool for a working photographer. Written before any UI code. The token file is the `:root` block in
`index.html`; this document owns usage. Where the two disagree, the token block wins for a value and
this document wins for a use.

---

## 0. Stance commitment

**The frame is the only coloured thing on the screen.** Ashcombe is a neutral instrument wrapped
around one photograph: an achromatic dark surround, an achromatic control layer, and a grey so
exactly neutral that the eye's white point stays on the frame. It is not a media player and not a
gallery — nothing here is styled to make a photograph look better than it is, because the whole task
is judging how good it actually is. *If a decision is ever ambiguous, choose the option that puts
less of the interface between the photographer and the frame.*

**Axis position.**

- **Density: dense** — a cull is thirty verdicts in a sitting; the photographer scans and presses
  keys rather than reads. (constraint)
- **Criticality: transactional** — a flag is reversible and nothing is deleted here, but a reject
  feeds a delete step later, so counts stay visible and every verdict is undoable. (constraint)
- **Energy: quiet** — the frame is the only thing allowed to be loud; a control that asks for
  attention is a control competing with the photograph.
- **Type: mono-as-display, plus one neutral UI sans** — the display element of this product is a
  frame identifier (`ASH_1210`), and everything else it says is measured: shutter, aperture, ISO,
  Kelvin, EV, elapsed seconds. Criteria: tabular figures throughout, unmistakable `0`/`O` and `1`/`l`,
  high x-height at 11 px, a weight range wide enough to carry a rating without colour.
- **Material model: glass over planes** — the controls genuinely sit above a photograph that changes
  under them, which is the earning test. **Underneath, tonal**: the filmstrip band and the readout
  column are opaque planes told apart by one lightness step, and they carry no shadow. Rejected:
  elevated, which would put a lifted slab beside the frame it exists to show.
- **Color commitment: restrained** — chromatic surface in the chrome is zero. All chroma on the page
  belongs to the photograph.
- **Accent job: none** — a monochrome interaction language. A chromatic control 40 px from a skin
  tone shifts how that skin tone is judged (simultaneous contrast), and judging tone is the entire
  task. Weight, fill, position, and a visible non-colour focus ring carry every state.
- **Ground lightness: dark** — the physical scene: one photographer, late evening, a dim room, a
  calibrated display, three hours after a shoot, deciding what to send. A light surround makes every
  frame read dark and photographers over-brighten to compensate.
- **Ground temperature: neutral, at chroma exactly 0** — every neutral is `r = g = b`. A surround with
  any hue at all biases the frame's apparent colour balance, which is the thing the white-balance
  control exists to set.

**Rejected coordinate vector.** *quiet · characterful serif · tonal · restrained · directional ·
dark · warm* — the "editorial darkroom" reading, warm neutrals and a serif nameplate, rejected because
warm neutrals around a photograph are a measurement error, not a mood, and a serif nameplate spends
the page's one risk on the tool rather than on the shoot.

**Rejected ingredients.** The sampler drew `maximalist`, `risograph`, `swiss`, humanist serif,
mono-as-display, and textured-paper/cream canvas. `swiss` survives as the discipline (strict grid,
neutrals, function declares the aesthetic) and mono-as-display is adopted outright, for the reason
above. Cream canvas is refused: it is the taste layer's saturated default *and* it is the wrong
surround for image evaluation. `risograph` and `maximalist` are refused — visible grain and layered
misregistration are exactly the artefacts this tool exists to detect.

**Derivation.**

- *Accent hue, weighed and rejected:* **the orange mask of colour-negative film** (roughly OKLCH
  h 60, the thing every photographer sees on a light table). It is the honest hue this product's world
  offers, and it lost on the product's own grounds — an orange chip beside a frame of hot steel is a
  reference the eye adapts to, and the frames here are lit by forge fire. Where the world's own colour
  is a colour the frame already contains, the accent job is `none`.
- *Ground, weighed and rejected:* **near-black `#0A0A0A`**. Rejected because a near-black surround
  inflates apparent contrast and photographers flatten their frames to compensate; the surround sits
  instead at L\* ≈ 12, dark enough that the frame is the brightest thing in the field.
- *Type:* one UI sans and one mono, which is the family count density allows. Both are the platform's
  own system faces (`ui-sans-serif` / `ui-monospace`), because the page makes no network request
  beyond the one module and because a page held to the macOS reading should use the macOS faces.

**The named chroma exception.** The white-balance temperature and tint tracks are drawn as real
ramps — blue to amber, green to magenta. There the hue *is* the value being set, so it is data, not
decoration. It is the only chroma in the control layer and it appears nowhere else.

**Signature element.** **The burst ledger.** The filmstrip brackets consecutive frames shot less than
two seconds apart and writes each burst's span and decided-count above it, so the strip shows the
shoot's rhythm — where the photographer fired four and where one — and the cull becomes a walk
through eleven decisions instead of thirty.

**Clone test.** Another culling tool would land on dense and transactional, and might land on quiet,
dark and restrained. It would not land on chroma exactly zero with a named ramp exception, on a
surround derived from adaptation rather than from taste, or on bursts as the unit of work.

---

## 1. Palette, with usage rules

Every colour is a token in the `:root` block. **The neutral ramp is achromatic by law:
`r = g = b` in every neutral token** — a QA pass greps for a neutral whose channels differ.

| Role | Token | Job |
|---|---|---|
| Stage surround | `--ground-0` | The field around the frame. Painted into the canvas, never as CSS. |
| Band | `--ground-1` | The filmstrip band and the readout column. One step up from the surround. |
| Well | `--ground-2` | A cell well, a slider track, a rest state. |
| Raised | `--ground-3` | Hover and the selected cell's well. |
| Ink | `--ink-0` | Primary text and every label on glass. |
| Ink, secondary | `--ink-1` | Values in the readout column. |
| Ink, muted | `--ink-2` | Labels and units in the opaque planes. Used down to 9.5 px, and measured at 4.5:1 on `--ground-1`. |
| Hairline | `--line-1`, `--line-2` | Dividers and the cell border. White at 10% and 20%. |
| Wash | `--wash-hover`, `--wash-press`, `--wash-field`, `--wash-track` | The control layer's whole state language: white at 10 / 18 / 12 / 22 %. |
| Plane paint | `--edge`, `--guide`, `--divider`, `--mask`, `--hist-ink` | What the canvas draws with. The plane has no palette of its own. |

**There is no accent token.** Selection, focus, and the primary action are carried by fill, weight
and rule: the selected cell takes a 2 px `--ink-0` border and a 4 px rise; focus takes a 2 px
`--ink-0` outline over a 4 px `--focus-halo` shadow, so it survives both a bright frame and a dark
one; the primary action (`Pick`) takes a solid `--ink-0` fill with `--ground-0` ink. **Ink alpha
never encodes state** — a label is `--ink-0` or `--ink-0-mute`, and the state is the wash under it.

**The only chromatic tokens on the page** are the white-balance family: the two ramps (`--wb-cool`,
`--wb-warm`, `--wb-green`, `--wb-magenta`, `--wb-neutral`) and the four correction tints the plane
multiplies by (`--wb-fix-*`). Every other token is achromatic, `r = g = b`. A colour literal anywhere
outside the `:root` block — CSS, markup, or a canvas fill — is a defect; the plane's painting reads
the same tokens through `getComputedStyle`.

---

## 2. Typography roles, with placement rules

| Role | Family | Treatment | Where |
|---|---|---|---|
| Display | mono | 20 px / 500 / `0.02em` | The frame identifier, once per view. Nowhere else. |
| Section label | mono | 10 px / 600 / `0.10em` / uppercase | The readout column's four blocks (`FRAME`, `CAPTURE`, `SHOOT`, `PHOTOGRAPHS`) and the open platter's one title. It is that column's structure, never an eyebrow above a heading elsewhere. |
| Data | mono | 11 px / 450 / `tabular-nums` | Every measured value: exposure, Kelvin, EV, times, counts, ratings. |
| UI | sans | 12–13 px / 500 | Control labels, headings, the filmstrip header. |

Mono never carries a sentence. Sans never carries a number that sits in a column with other numbers.
No third family, no italic, no letter-spaced sans.

---

## 3. Canvas, texture & material

**The live plane is one `<canvas>`, viewport-sized, fixed at `inset: 0`, registered as the glass
backdrop texture.** It paints the surround and then the selected frame, fit whole, with the current
exposure, white balance, compare state and crop overlay already applied. Screen and texture are the
same pixels by construction, which is the only way the lens shows what the photographer is judging.
No CSS gradient, grid or grain is laid over it: anything drawn outside the canvas is not behind the
glass and would not be refracted.

**Material model: glass over planes, with tonal underneath.**

- **Planes.** `base` carries all three floating surfaces. **The `overlay` plane is unused, and that
  is a decision**: no floating surface ever overlaps another, and the adjustment platter grows in
  place out of the tool column rather than opening over it, so there is nothing to promote.
- **Groups.** Three, all reading the same texture source `stage`, and therefore **declaring no
  backdrop hint** — a texture group lets the runtime read the pixels, and a hint would be a weaker
  assertion about a backdrop the runtime can see:
  - `view` — the compare segmented control. 1 surface.
  - `tools` — the tool column, which morphs into the adjustment platter. 1 surface.
  - `verdict` — the reject / rate / pick bar. 1 surface.
- **Separation.** No `samplingPadding` or `mergeDistance` is declared; the runtime derives 3σ of the
  blur it resolves. The measured gaps at 1440 × 900 are **168 px** (compare
  control to platter) and **152 px** (platter to verdict bar), far past any padding the runtime
  derives, and both are recomputed from the frame's rectangle at every width rather than typed once.
- **Backdrop honesty.** Every glass surface is positioned inside the photograph's own rectangle and
  never over the grey surround. Glass over a flat field is invisible glass; the surround is flat on
  purpose, so nothing floats there.
- **Variant: `regular`, on all three groups.** `clear` is refused: its conditions require a dimming
  layer over the content, and dimming the photograph is the one thing this tool may not do.
- **Tint: none, anywhere.** The accent job is `none`; a tinted control would be the page's only hue.
- **Size family.** Three rungs by short side, one thickness across all of them:

  | Rung | Short side | Radius | Shape kind | Member |
  |---|---|---|---|---|
  | L | 248 | 28 | fixed | the adjustment platter, open |
  | M | 56 | 28 | capsule for the bar, fixed for the column | verdict bar; the tool column at rest |
  | S | 40 | 12 | fixed | compare control |

  Thickness **9** on all three. The L radius is set to 28 precisely so that it equals the M rung's
  capsule radius (56 ÷ 2) and the two read as one material. The family straddles the size law's live
  band — 40 and 56 inside 32–96, 248 past saturation — and **the morph carries one surface across
  it**: the tools host is registered once and grows from the M rung to the L rung, so the law's own
  behaviour, larger glass more opaque and smaller glass clearer, is shown rather than described.
- **Concentricity anchor: the photograph's own rectangle, radius 0.** A photograph has square
  corners and nothing here rounds one, so no glass surface is concentric with the plane — the three
  glass radii are fixed or capsule, and that is recorded rather than left unstated. Concentricity is
  used one level down, inside each surface: an inner view inset by *g* takes the surface's radius
  minus *g* (platter 28 − 10 = 18; verdict bar 28 − 8 = 20, which is also that inner row's own capsule
  radius; compare control 12 − 4 = 8).
- **Radius in the content layer is 0, everywhere.** Thumbnails, wells, and panels are square-cornered,
  for the same reason the anchor is: a photograph has square corners.
- **Scroll edge.** No content scrolls under a floating control at rest, so no scroll edge is drawn —
  the rule's own wording is "wherever content scrolls under a floating control and nowhere else". The
  filmstrip's horizontal overflow takes the **hard** desktop treatment: frames clip against the band's
  edge under a 1 px hairline, with no fade and no scrim.
- **Path: vitrea `0.14.0`, the workspace build**, `@vitreajs/vitrea-web` through an import map. The
  deliverable is one HTML file plus a served repository; it needs `http://localhost` (or https) both
  for the module and for `navigator.gpu`, and it does not run from `file://` at all.
- **Tier expectation:** `webgpu` in Chromium over localhost, `css` elsewhere. `?renderer=css` forces
  the CSS tier for QA. The CSS tier is the same material without refraction, and it is a complete
  design, not a degraded copy.
- **Accessibility:** `reducedTransparency`, `increasedContrast` and `reducedMotion` are set explicitly
  at the root because `prefers-reduced-transparency` is not Baseline. Under forced colours there is no
  glass; what remains is the same layout in system colours with visible borders on every control.
- **Contrast:** labels get their own colour on a child element, never on the host, whose `background`
  the CSS tier rewrites every frame. Measured on rendered pixels over the darkest and brightest
  frames in the shoot.

---

## 4. Layout system

**The six composition lines.**

1. **Posture: workspace** — the photographer works out of this surface for the length of a cull, not
   a page read once.
2. **Dominant activity: decide** — the first read answers "is this frame a keeper", and the success
   condition is thirty frames each flagged or rated.
3. **Unit and relation:** the unit is the **frame**; the relation is a **sequence** — the shoot is an
   ordered run in capture order, and the ordering key is the frame number.
4. **Co-visibility: peer panes** — the run must stay visible while one frame is judged, so the strip
   and the stage are on screen together; the frame's own capture data must stay visible too, which is
   what earns the readout column.
5. **Temporal: static** — the card is already ingested. Nothing updates while it is viewed, and
   nothing on this page carries a live badge or the word "real-time".
6. **Volume and homogeneity: many homogeneous** — thirty frames on one schema, grouped into eleven
   bursts by capture interval.

**Compiled consequences.** One dominant region (the stage) with one named supporting pane (the
readout column) and one subordinate band (the filmstrip). Reading order: stage, filmstrip, readout.
The stage : column ratio is **5.9 : 1** by width, nowhere near the 1.1–1.35 band. Density lives in the
filmstrip cell and the readout column; the stage carries none. What repeats: the filmstrip cell, ×30,
and nothing else. Chrome is conventional — there is none beyond the filmstrip header, because a
single-surface tool has no destinations.

**Ledger.**

| Brief evidence | Interpreted relationship | Layout constraint | Rendered assertion | Forbidden move |
|---|---|---|---|---|
| "the selected photograph fills the stage" | The frame is the whole first read | The stage takes the full width less one readout column; the frame is fit whole inside it | The stage is first in DOM, at (0,0), and holds ≥ 80% of the first viewport; the layout never crops the frame | Cropping the frame to fill the stage edge to edge |
| "a tool palette, the adjustment controls … float over it" | Controls above content, not docked beside it | Every control is a glass surface placed inside the frame's own rectangle | No floating surface touches the grey surround; no adjustment panel is docked | A right-hand adjustments panel in its own band of background |
| "a filmstrip of the shoot runs beneath" | A sequence with an ordering key | One horizontally scrolling band flush to the bottom edge, frame number first in each cell | 30 cells in capture order, ≥ 10 in view at 1440; the selected cell marked by border and offset | A thumbnail grid, or paging |
| "thirty frames with ratings and flags" | Many homogeneous, grouped into bursts by capture interval | The strip brackets frames shot < 2 s apart | Each bracket carries the burst's frame span and its decided count | Thirty undifferentiated cells in one flat run |
| "culling" | Disposition one frame at a time, not comparison of two | No second stage and no side-by-side pane; compare is the frame against itself | The verdict bar sits inside the frame's lower edge, reachable without moving the eye off the frame | A two-up compare pane |

**Chosen candidate.** *Single stage, bottom filmstrip, one right readout column; every control floats
inside the frame's rectangle and the frame is fit whole on a neutral surround.*

**Rejected candidates.** *Two-up compare stage* — the brief's compare is before-and-after on one
frame, and two stages halve the thing the tool exists to judge. *Full-bleed frame with the filmstrip
as a hover platter* — the strip is where the photographer knows their position in the run, and a
filmstrip made of glass would be glass in the content layer.

**Prior adopted: center stage**, earned by the *decide* activity on one unit, with **primary region
plus one named supporting pane** for the readout column — named (the frame's capture data), capped
(208 px), and never a grid of cards.

**Defaults overridden by name.** No left sidebar — there are no peer destinations and the filmstrip is
the navigation. No stat row — the picked/rejected/open counts sit in the readout column, not in a band
above the stage. No main-plus-rail grid of cards. No near-equal split. And no docked adjustments panel,
which is what every photo editor ships and what the brief explicitly replaces with floating controls.

**Mechanics.** Everything is positioned from one measured rectangle: the frame's rect, computed at
each resize as the largest 3:2 box fitting the stage inset by 24 px horizontally and 16 px vertically.
Glass positions are expressed as insets from that rect (20 px), so the material follows the picture
rather than the window. Spacing scale: 4 / 8 / 12 / 16 / 20 / 24 / 32. Sections are separated by
hairlines and by the surround, never by cards or shadows.

**Responsive collapse, in two tiers.** At **≤ 1180 px** the readout column is removed and the frame
identity and the counts move into the filmstrip header as one mono line; the frame takes the
column's width back. At **≤ 900 px** the frame is no longer large enough to hold three separated
groups — a group needs at least its neighbour's sampling padding of clearance, and forcing it is
exactly the overlap the runtime reports — so the compare control and the adjustment platter are
*released* from the floating layer and re-mount as opaque controls in a row inside the band, the tool
column turning horizontal. The verdict bar is then the only glass on the page. At phone width this
is a culling tool and not a grading tool, and the material's own spacing rule is what decided it.

**Imagery ladder.** Every frame is rung 2, **Unsplash** — rung 1 returned nothing relevant (the
repository's only photographs belong to a sibling demo and are a different subject). Ten setups were
downloaded at a normalised 2400 × 1600 crop, so the shoot reads as one camera, with 400 px derivatives
for the strip. The thirty frames are those ten setups shot as bursts, each frame carrying its own crop
rectangle — which is what a burst actually is, and what makes culling necessary. Every photographer is
credited by name with a link, in the readout column.

---

## 5. Component canon

- **`frame-cell`** — the one filmstrip cell: a square-cornered 3:2 thumbnail in a `--ground-2` well,
  its frame number in mono beneath, a flag block and rating dots overlaid at its edges. The flag is a
  word in a block, never a glyph: `PICK` is an `--ink-0` fill with `--ground-0` ink, `REJ` is a
  `--scrim` block with a strike through it. Selected = 2 px `--ink-0` border plus a 4 px rise.
  Rejected = 45% opacity as well as the struck block.
- **`burst-bracket`** — the bracket above a run of cells: a hairline with two end ticks, carrying the
  burst's first frame number and its decided count (`1209 … 2/4`) in 9.5 px mono.
- **`readout-row`** — a mono label / mono value pair on one line, label in `--ink-2`, value in
  `--ink-1`, values right-aligned on one column.
- **`glass-bar`** — a registered glass host containing only plain DOM. Never nested, never given a
  `background`, never given a shadow.
- **`bar-button`** — a text button inside a glass bar: `--ink-0` ink, transparent rest, 8% white
  hover, capsule. Its prominent variant inverts to a solid `--ink-0` fill.
- **`icon-button`** — a 36 px square button carrying one 20 × 20 monoweight SVG at stroke 1.5, always
  with an `aria-label`.
- **`slider-row`** — a mono label, a mono value, a styled `<input type="range">`, and a reset
  icon-button. The white-balance rows are the only ones whose track carries a ramp.
- **`histogram`** — a 160 × 56 canvas drawing the frame's luminance distribution from the stage's own
  pixels, in one ink at 75%, with a baseline and quarter hairlines. No second series, no colour.

Build order: tokens → canvas plane → filmstrip → readout column → glass root → the three groups.

---

## 6. Voice

Instrumental and terse. Labels are nouns or imperatives at 1–2 words: `Reject`, `Pick`, `Exposure`,
`White balance`, `Crop`, `Split`. Sentence case everywhere except the two mono section labels. Units
are always written and always spaced (`1/320 s`, `3200 K`, `+0.35 EV`, `f/2.8`). Counts are stated as
plain numbers with a noun, never as a percentage. No exclamation, no encouragement, no product voice.
Empty states name the specific absence in the domain's own words: the readout's adjust row reads
`as shot` when nothing has been moved, and the histogram reads `no clipping` rather than drawing a
false zero. The error
state names the recovery: "Frame unavailable — re-ingest from card".

---

## 7. Motion

Every motion answers an input or a state change; there is no idle motion and no shimmer at rest.

- **The platter morphs**, it does not cross-fade: one registered host whose width is driven from 56
  to 328 px by a damped step (`dt / 110`) inside the root's own frame callback, its contents swapping
  inside. There is never a second glass surface faded in over the first, and it is deliberately not a
  CSS transition — the box the runtime measures is the box being animated.
- **Press** is the runtime's own glow, driven by writing `--vitrea-press` and `--vitrea-press-x/y` from
  the pointer inside the root's single frame callback. Never a colour swap, and never a second
  `requestAnimationFrame` loop.
- **The stage does not transition between frames.** A photographer needs the next frame instantly; a
  cross-fade would be the interface asking to be noticed. This absence is deliberate.
- **Reduced motion** collapses the morph to an instant width change and makes the filmstrip's
  scroll-into-view non-smooth. No layout depends on any transition.

---

## 8. Hard don'ts

1. No chromatic value anywhere outside the four white-balance ramp tokens. A neutral whose `r`, `g`
   and `b` differ is a defect.
2. No glass on a filmstrip cell, the readout column, the band, or any text surface. Glass is a
   control or it is not glass.
3. No glass over the grey surround. Every floating surface stays inside the frame's rectangle.
4. No `background`, `box-shadow`, `border`, or backing scrim on a glass host.
5. No nested glass, no second glass surface faded in over another, no `clear` variant, no tint.
6. No `filter`, `backdrop-filter`, `opacity` below 1, `mask-image`, `clip-path` or `mix-blend-mode`
   on `<html>` or `<body>` — each re-roots the backdrop and demotes every group.
7. No rounded corner in the content layer.
8. No CSS overlay on the backdrop. Anything meant to be refracted is painted into the canvas.
9. No shadow on any surface, glass or opaque. This page has no elevation ladder.
10. No cream, no warm neutral, no sage, no violet, no gradient text, no side-stripe border, no
    decorative eyebrow above a third section.
11. No status communicated by colour alone — there is no colour to use.
12. No lorem ipsum, no invented metric, no live badge on static content.

---

## 9. Frame data

The shoot is a magazine assignment: *Smiths' Weekend, Ashcombe Forge, Wealden — 6 September 2026*,
card 2 of 2, thirty frames on a Nikon Z 8 with a 24–70 mm f/2.8. Frame identifiers run `ASH_1188`
through `ASH_1217` consecutively, because a card holds every frame that was shot. Exposure data is
constant within a burst and changes between setups the way it actually would: ISO 1600 by the window,
ISO 6400 in the dark bay, shutter rising to 1/320 s when the hammer is moving. Ratings and flags are
distributed as a half-finished cull — seven picked, five rejected, eighteen open — and one frame
(`ASH_1207`) is soft, which is why it is rejected. No frame is captioned and no person in a frame is
named: the photographs carry the world, not the people the copy is about.
