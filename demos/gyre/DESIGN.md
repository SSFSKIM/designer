# Gyre — design law

The design law for `demos/gyre`, a demo built on the published `@vitreajs/vitrea-react@0.6.0`.
Values live in `src/styles/tokens.css` (UI) and `src/field/palettes.ts` (the data-field ramps);
this file owns usage. The token file wins on a value, this file wins on a use.

## 0. Stance commitment

**Optical Swiss.** Swiss typographic discipline laid over a live, light, drenched colour field,
with Liquid Glass as the only material and only on the controls layer. Gyre is a fictional
ocean-surface-current instrument: the whole viewport is the field, running live, and every
control floats on it as glass. The page is a working instrument, not a launch page: it is
explicitly **not** a dark neon glass reel, not a hero-and-feature-cards landing page, and not a
warm-paper editorial essay.

Light rather than dark, decided by scene: an oceanographer at a bright desk at midday, glancing
at a live current field between two other windows, glare on the screen. Dark glass is the easy
demonstration and the reflex answer to "futuristic"; the harder and less-seen one is a bright
material bending a bright field.

Single viewport, no document scroll. vitrea draws glass in viewport-fixed planes, so a page that
scrolled its glass away would be working against the material it is showing. Content that would
have been sections is reached through the nav and appears as **sheets**: ordinary DOM with a
translucent white fill, never glass.

Rejected ingredients, and why: the sampler offered `warm` and a cream textured canvas (a
flat cream ground gives a lens nothing to bend and sits in the cream band), `data-dense` (a
Bloomberg density would bury the one instrument reading that matters), and a glyphic serif (a
Trajan register belongs to monuments, not instruments). Taken from the sampler: `swiss`, whose
strict grid, neutral-plus-one-accent restraint and neo-grotesque type are this law's skeleton.

Signature element: **the probe.** One large draggable glass lens over the live field, reading
the field at its centre in mono. The material's size-parameterised lensing is the demonstration,
and the reading is what makes it a control rather than an ornament. One risk, spent there; the
rest of the chrome stays quiet.

If a decision is ever ambiguous, choose the more **instrumental** option: the one that reads as
a measurement rather than a presentation.

## 1. Palette, with usage rules

- `--ink` is the only text colour over the field and the primary text on sheets. It is a cool
  near-black at OKLCH L 0.20, never pure black.
- `--muted` is secondary text and appears **only on sheets**, never over the field or on glass
  (it clears 6.5:1 on the sheet's worst composite and would not be guaranteed over the field).
- `--sheet` is the content fill: white at 84% over whatever the field is doing. It is the only
  content-layer surface. It has no shadow, no blur and no border beyond a hairline.
- `--accent` (vermilion, OKLCH 0.47 0.19 27) does exactly three jobs: the one tinted primary
  action, the selected state, and the focus ring. It never colours a heading, an icon, a rule or
  a ground. Ultramarine was weighed and lost: it sits inside the currents ramp. `--accent-hex`
  is the same colour in the numeric syntax the runtime's tint parser accepts, and is read from
  the stylesheet at runtime rather than repeated in code.
- The three field ramps in `src/field/palettes.ts` are **data colours, not UI tokens**. They
  are the one sanctioned place a colour literal lives outside `tokens.css`, because they are a
  colormap and each carries a legend. Every ramp holds OKLCH lightness at or above 0.75, which is
  what guarantees `--ink` at least 7.8:1 and `--accent` at least 3.2:1 anywhere on the field
  (`scripts/palette.mjs` prints the arithmetic).
- The runtime's own `--vitrea-*` properties are read, with a token as fallback, and never
  redeclared.
- Two material variants, each with one job. Every control is `regular`. The probe alone is
  `clear`, because it is a lens over media and its reading has to be seen against the field it
  measures; its group carries a light `lighten` scrim (0.16) so dark ink stays legible on a
  bright field. Variants are never mixed inside one group.

Forbidden: a second accent; a green anywhere (green reads as "healthy" on an instrument and
would smuggle a claim); a colour literal outside the two files named above; any dark ground.

## 2. Typography roles, with placement rules

Two families, no third.

- `--font-display` is Archivo at width 125, weight 500. It carries the wordmark, the one
  display statement per sheet, and the probe's principal reading. Nothing else.
- `--font-ui` is Archivo at width 100. Body, control labels, table text, captions.
- `--font-mono` is Fragment Mono. Coordinates, speeds, headings-as-in-bearings, timestamps, the
  runtime readout, and table numerals. Never prose. Numerals are `tabular-nums slashed-zero`.

Roles: `--type-display`, `--type-h2`, `--type-body`, `--type-small`, `--type-label`,
`--type-data`, `--type-reading`. `--type-label` is the only uppercase role and uppercase arrives
through `text-transform` only. Prose measure is capped at 60ch. Nothing restyles a role ad hoc.

## 3. Canvas & texture

The ground is the field: one WebGL canvas, `position: fixed; inset: 0`, registered with vitrea
as the backdrop texture. It is content, so it is allowed to move, and it is the only thing on
the page that moves continuously. No grain, no gradient behind anything, no shadow anywhere
that vitrea did not draw. Under `prefers-reduced-motion` the field freezes at its current phase;
the controls keep working.

The field's mapping and the glass's sampling must agree: the canvas is viewport-cover and so is
the registered texture. No glass surface ever sits over a sheet, because the texture tier would
show the field through it where the sheet is.

## 4. Layout system

A fixed viewport with four reserved strips, on an 8px grid with `--space-1..8`:

- **Nav strip**, top, 72px: the glass nav, top-left, start-aligned, never centred.
- **Field**, everything between: the probe's drag area. It shrinks to exclude an open sheet.
- **Transport strip**, bottom, 88px: the transport toolbar bottom-left, the actions menu 48px
  to its right, the layer segmented control bottom-right. Separate sampling groups keep at
  least 48px of clear space between their bounds (the runtime's proxy padding measures about
  36px at the nominal blur).
- **Sheet**, left, `min(440px, 100vw)`: opens below the nav strip and above the transport strip.

Radius: glass takes the material's own radii (`--radius-glass` 18px, capsules for buttons and
the probe); sheets take `--radius-0`. Roundness belongs to the material.

Collapse at 720px: the nav keeps the wordmark and the tinted action; the three sheet links move
into the actions menu, which itself moves to the top-right and opens downward; the sheet becomes
a bottom sheet occupying the lower 56% of the viewport above the controls; the layer control
takes a row of its own 52px above the transport; the probe shrinks to 132px and hides while a
sheet is open.

## 5. Component canon

One of each. `Nav` (the one `GlassToolbar` at the top), `Probe` (the one draggable surface),
`Transport` (the one bottom toolbar, with `LayerMenu` as its morph), `LayerControl` (the one
segmented control), `Sheet` (the one content panel), `Readout` (the one `dl` pattern for any
key/value data), `Legend` (the one colormap bar). Build order: tokens → field → nav → probe →
transport and layers → sheets → readout.

## 6. Voice

Precision industrial. Terse, complete sentences, sentence case everywhere, numerals with units.
Buttons are verbs. **No em dashes and no double hyphens** anywhere. No buzzwords. Every number
on a sheet is derived from the same anchors (0.08° grid, 41 min latency, 6 h horizon, 1,900
drifters) and stays consistent across sheets. Errors and empty states say what happened and the
next step.

## 7. Motion

`--duration-fast` 120ms and `--duration-standard` 180ms on `--ease-standard` for hover, focus
and sheet entry. The probe follows the pointer directly with no easing. Everything else that
moves is the runtime's: press compression, the morph, the segmented indicator. No parallax, no
entrance choreography, no animated blur. Reduced motion freezes the field and cuts page
transitions to 1ms; the runtime removes its own overshoot.

## 8. Hard don'ts

- No glass on a sheet, a table, a list, or any element that is not a control. No glass inside
  glass. The wordmark is a button because it is a control (it closes the sheet).
- No shadow, gradient text, side-stripe border, card grid, eyebrow-per-section, or hero
  metric block. No numbered markers.
- No colour literal outside `tokens.css` and `palettes.ts`. No second accent. No green.
- No text over the field in `--muted`. No prose on glass: a glass surface carries a label or
  one reading, never a sentence.
- No em dashes in copy. No lorem ipsum. No round placeholder numbers.
- No invented rendering claims: the readout prints what `useGlassCapabilities` resolved, and a
  demoted group names its reason.

## 9. Glass placement law

vitrea's dev-mode diagnostics are part of this demo's definition of done: the console must show
none. Two sampling groups on one plane keep at least 48px between their member bounds. The
probe is clamped to the field with that same margin so it never nears another group. The morph
has its own group, and the viewport's origin corner stays clear of glass because a morph's
platter spends its first frame there: the wordmark is plain ink for exactly that reason.
Containers holding glass are start-aligned, never auto-centred. A surface that must be a disc
declares `profile="circular"`, since the continuous profile clamps a radius to fit its curve.
