# apps/demo — design law

Authored by the repo's own `skills/designer` skill for vitrea's public demo site
(child C9b of `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`).
Values live in `src/tokens.css`; this file owns usage. Token file wins on a value,
this file wins on a use.

## 0. Stance commitment

**Survey plate.** A field-instrument register borrowed from USGS quadrangles and
NASA mission graphics: a cool near-white ground, hairline rules, a monospace face
carrying display and annotation, and one dark instrument window in which the
material is actually running. The page is a measurement document, not a product
launch. It is explicitly **not** a dark neon glass reel, not a warm-paper editorial
essay, and not a SaaS landing page with feature cards.

Rejected ingredients, and why: the sampler offered `editorial` (which maps to the
Quiet editorial system's warm paper ground, inside taste-calibration's cream band
and, worse, a flat backdrop with nothing for a lens to bend), `kinetic` (motion as
primary character competes with the one thing on the page that must move), and
`dark mode` as the canvas (every verified competitor demo is dark, because dark is
where glass is easy; the harder and unclaimed demonstration is daylight). Taken
from the sampler: `topographic`, whose contour-and-graticule language is not a
metaphor here, since vitrea's geometry is literally contour IR, level sets, and
distance fields.

Signature element: **the reference pair.** A live vitrea render beside Apple's own
macOS 26.5 capture, at identical `scenes.json` geometry over the identical raster
background, with the measured axes named beneath it. One risk, spent there.
Everything else stays quiet.

Scope: this law governs the public site at `/`. The internal acceptance harness at
`/playground/` is outside it, because its structure, control names and layout are
pinned by `vitrea-react`'s Playwright suite rather than by taste; §9 binds it
anyway, since that is about correctness.

If a decision is ever ambiguous, choose the more **instrumental** option: the one
that reads as measurement rather than as presentation.

## 1. Palette, with usage rules

Two grounds, one accent.

- `--paper-0..9` is the page: a cool neutral ramp at hue 232. `--paper-2` is the
  body ground, `--paper-9` primary ink, `--paper-7` secondary text, `--paper-5`
  rules and dividers. Semantic aliases (`--background`, `--foreground`, `--card`,
  `--muted`, `--muted-foreground`, `--border`) exist and are what components use.
- `--stage-*` is the instrument window only: `--stage-0` ground, `--stage-1`
  panel, `--stage-ink` / `--stage-ink-dim` text, `--stage-rule` hairlines. These
  never appear outside `.stage`.
- `--accent` (oxide orange) and its stage twin `--accent-stage` do exactly one
  job: **marking a measurement or a current position.** The active section marker,
  the focus ring, a delta callout, a selected control. It does not tint headings,
  icons, dividers, panels, or grounds.

Every app-authored region inside a glass plane declares `color-scheme: dark`
(`.stage--mirror` and `.platter`). That is not decoration: the CSS tier writes its
foreground as `light-dark(...)`, which resolves against the element's own computed
scheme, so without it a control on glass over the dark instrument gets dark ink on a
dark surface.

Forbidden: a second accent; a status green anywhere (green on a fidelity page
reads as "test passed" and would smuggle a claim the calibration data does not
support, which is why contour green lost to oxide orange despite being the
topographic default); any color literal outside `tokens.css` except the two
documented exceptions, `--stage-rule`-style white alphas inside `.stage` and the
runtime's own `--vitrea-*` channel properties.

## 2. Typography roles, with placement rules

Two families, no third.

- `--font-mono` (system monospace stack) carries **display, headings, labels, and
  all data**. This inversion is the stance: an instrument annotates in mono.
- `--font-ui` (system sans stack) carries **body copy, lead paragraphs, and
  control labels**. Nothing else.

Roles are `--type-display`, `--type-h2`, `--type-h3`, `--type-lead`,
`--type-body`, `--type-small`, `--type-label`, `--type-data`. `--type-display` is
used **once**, in the masthead. `--type-label` is the only uppercase role, and
uppercase only ever arrives through `text-transform` so the string stays sentence
case. Numbers in tables and readouts carry
`font-variant-numeric: tabular-nums slashed-zero`. Prose measure is capped at
66ch; no element restyles its type ad hoc.

## 3. Canvas & texture

The page ground is flat `--paper-2`. No grain, no gradient, no blur, no shadow on
any page surface.

Exactly one texture exists: a hairline **graticule** inside `.stage`, one 32px
grid at low alpha, applied once on the stage ground. It earns its place twice
over: it is the instrument's coordinate reference, and it is high-frequency
backdrop detail without which refraction has nothing to bend. It is never
animated, never repeated per component, and never sits behind body copy.

## 4. Layout system

Asymmetric split, 45/55, and the split is load-bearing rather than decorative:
the narrative scrolls, the instrument does not.

- **The column** (left, 45%) is ordinary document flow and the only thing that
  scrolls. It holds every word, every code block, and every native capture.
- **The stage** (right, 55%) is `position: fixed`. All glass lives here, because
  X1 puts glass in viewport-fixed planes and a page that scrolled its own glass
  out from under itself would be the library lying on its own home page.

Sections are separated by a single `--paper-5` hairline and whitespace. No cards,
no panels, no shadows, no eyebrow above headings. Spacing steps are
`--space-1..9`; radius is `--radius-0..3` and **frame surfaces take
`--radius-0`** — roundness belongs to the material, which is what makes the glass
read as a different substance from the page.

Collapse at 900px: the stage becomes a fixed band across the **bottom** at 46vh,
the column takes the full width above it with matching bottom padding, and section
order is unchanged. Bottom rather than top is §9 rule 2, not taste: a top band puts
the behaviour toolbar inside the viewport's origin corner, which has to stay clear
of glass. Below 560px the band grows to 52vh, because the behaviour stage needs
about 260px to hold three sampling groups more than 48px apart, and the reference
pair shows one panel at a time: two 320px frames do not fit side by side on a phone,
and scaling both far enough to fit makes a fidelity comparison unreadable.

## 5. Component canon

One of each; reuse rather than rebuild. `.masthead`, `.section` (hairline-
separated, with `.section__marker` for the active tick), `.readout` (the one
definition-list pattern for runtime state, used by the capabilities panel, the
tier table and the calibration figures), `.code` (the one pre/code block),
`.pair` (the reference pair frame, with `.panel-switch` for its collapsed
single-panel form), `.field` (the one label-plus-control row, used by every
accessibility and tier toggle), `.note` (the one caveat line).

Build order: tokens → masthead and section shell → stage shell and graticule →
readout → stage modes (material, reference, behavior, access) → fields → code.

## 6. Voice

Precision industrial. Terse, technical, no adjective it cannot defend, complete
sentences, sentence case everywhere. State what was measured and on what; name
what was not. Numbers are numerals and always carry their unit and their cell.
Buttons are verbs. **No em dashes and no double hyphens**, in any copy on the
page. No buzzwords. Caveats are stated in the same size as the claim, never as
fine print.

## 7. Motion

Durations `--duration-fast` 120ms, `--duration-standard` 180ms,
`--duration-slow` 260ms; easing `--ease-standard` for everything the page owns.
Only three things move, and the stage swap is deliberately not one of them: it is
instant, because a cross-fade between two stage modes would put two materials on
screen at once and a page carrying two of those has neither. What moves is the
current-section marker and heading (standard), control hover and focus (fast), and
the material's own springs, which are the runtime's and not this stylesheet's. No
parallax, no reveal-on-scroll, no
drifting gradient, no animated blur.

`prefers-reduced-motion: reduce` cuts every page transition to 1ms and the stage
swaps instantly; the runtime removes overshoot and deformation on its own side.
Both halves must hold, and the page must remain fully usable with all of it off.

## 8. Hard don'ts

- No glass, blur, or `backdrop-filter` on page chrome. Glass appears only inside
  `.stage`, and only as a registered vitrea surface.
- No radius on frame surfaces, no shadow anywhere on the page, no gradient text,
  no side-stripe borders, no identical card grid, no hero metric block.
- No second accent, no green, no color as the only carrier of state.
- No em dashes in copy. No lorem ipsum or invented fidelity numbers: every figure
  is read from `packages/calibration/results/matrix.json` at build time or the
  slot is labeled unmeasured.
- No webfonts and no external requests of any kind. The site must build to a
  self-contained static directory.
- No prose over glass. A glass surface carries at most one short line, at
  `--type-h3` size or larger, or a real control's own label; everything that
  explains it lives in the column, on paper. The material never carries
  information.
- Text over glass is **measured, not assumed**. axe cannot compute contrast over a
  canvas backdrop, so `e2e/contrast.spec.ts` samples the rendered pixels across
  several phases of the backdrop's drift and holds 4.5:1 for labels and 3:1 for the
  plates. Brightening the stage field, dimming a label, or lightening the segmented
  indicator are all changes that test is guarding.

## 9. Glass placement law (domain-specific)

The dev-mode checks in `vitrea` are part of this page's definition of done,
so three placement rules are law rather than preference. `pnpm --filter demo dev`
must report zero diagnostics.

1. **Two-group separation.** Two sampling groups on one plane must sit more than
   the sum of their `samplingPadding` apart, which at the 24px advisory default
   means **more than 48px of clear space** between their member bounds.
2. **The origin corner stays clear.** `GlassMorph` renders its closed platter in
   the plane host layer's own flow until it has measured itself, which puts a
   registered box at the viewport origin for one to two frames. So no glass
   surface may occupy the top-left `160×64` of the viewport, and a morph is
   always given **its own `groupId`** so that transient cannot inflate a
   neighbour's proxy union.
3. **No post-mount reflow of glass.** A container holding a morph is laid out
   start-aligned, never auto-centered, so the anchor spacer growing from zero to
   its measured size cannot move its siblings and produce a phantom overlap
   between two hosts measured in different epochs.
