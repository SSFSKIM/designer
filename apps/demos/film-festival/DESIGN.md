# HALFLIGHT — design law

The programme page for HALFLIGHT, Dundee's film festival, eighth edition, Thursday 5 to Sunday 8
November 2026. One HTML file on the vitrea 0.14.0 workspace build, served from the repository root.

## 0. Stance commitment

A cold-press programme sheet drawn up over one winter frame, with the festival's whole apparatus —
mark, section titles, times, durations, prices — set in a monospace, and the films set in a
humanist sans so a title never reads as a timetable entry. It is not a cinema-black poster site and
it is not a warm-paper magazine. **If a decision is ever ambiguous, choose the more legible option.**

**Axis position.**

- Density: **standard** (constraint) — a member of the public reads this for ten minutes to decide
  what to book; the timetable tightens to the bottom of the standard steps, nothing else does.
- Criticality: **transactional** (constraint) — a wrong click costs £9.50 and a sold-out screening
  is a real loss, but nothing is audited and nothing is irreversible.
- Energy: **composed** — the films carry the excitement; the page is the object that lists them.
- Type: **mono-as-display** — the two things that must be exact are times and durations, so the
  face that sets them sets the festival's own voice too. Criteria: tabular figures, unmistakable
  0/O and 1/l at 11px, and a form that holds at 72px; the sans needs a tall x-height at 15px, open
  apertures, and a true 600 for film titles at 14px.
- Material model: **glass over planes** for the floating layer — the controls sit over a still that
  is the window's live plane — with **printed** beneath: the programme is a printed object, so the
  sheet takes hairline rules and whitespace and no shadow at all.
- Colour commitment: **restrained** — the photographs are the only saturated surface on the page.
- Accent job: **directional** — the primary action, a link and the focus ring. Never state: sold
  out, returns and 35mm are words, not hues.
- Ground lightness: **light** — the scene is a kitchen table on a September afternoon with the
  printed programme open beside the laptop, three weeks before the passes go on sale.
- Ground temperature: **cool** — the ground is drawn from the snow in the opening film's own still,
  a blue-violet white; the warmth is spent entirely in the accent.

**Rejected coordinate vector:** quiet · characterful serif · dark · neutral · committed ·
atmospheric. That is what "film festival" predicts twice over — near-black with a serif display and
a poster colour drenching the strands — and dark is also where glass is easy, which
`references/material.md` names as the reason every verified competitor demo is dark. It lost on the
timetable: 39 screenings scanned in afternoon light read better as ink on a light sheet.

**Rejected ingredients (sampler):** `bauhaus` — primary colour blocking would put saturated colour
in the control layer, which the material forbids; heavily-coloured canvas — the live plane is a
photograph and a saturated canvas would fight it; `editorial` — its warm-neutral serif is the
second-order reflex for this category. `mono-as-display` was taken, and one trace of `data-dense`
survives in the timetable's 15-minute rail.

**Derivation.** The accent is `--accent`, a print-fade magenta: the colour an ageing release print
goes when its cyan and yellow dyes fail, which is why the Nitrate strand exists at all. **Rejected
hue: the orange of colour negative's own mask**, the other colour that belongs to film — rejected
because on a cool ground an orange at the chroma a primary action needs reads as a warning, and
this page needs its one hue to mean "press this" and nothing else. (The hue is derived from the
festival's material, not from what a status set left over: this page has no status set.) The ground
is `--ground`, the blue-violet white of shaded snow, sampled from the opening film's still so that
the sheet and the film are one material world with the glass between them. **Rejected ground: warm
paper cream**, the honest metaphor for a printed programme — rejected because the festival's stock
is cold-press, because the cream would fight a snow-blue frame, and because that band is the
saturated default `references/taste-calibration.md` names. Type: the mono is the timetable's voice
and therefore the festival's; the sans exists so a film title is never mistaken for a time.

**Signature element: the floating layer never leaves the film.** A scroll-edge mask keeps the band
above the bar clear of the sheet at every scroll position, so the toolbar sits on the opening film's
still from first paint to the foot of the page. One backdrop, one ink, a texture group that stays
honest at every scroll position, and a strip of the film always visible above the schedule.

**Clone test.** Another city festival would land on standard and transactional too, and might land
on composed, light and directional. The magenta, this blue-violet ground, the mono-carries-the-
apparatus rule and the mask that keeps the film under the bar are this festival's and are argued
from its own material above.

## 1. Palette, with usage rules

Values live in the `:root` token block; this section owns the jobs.

- `--ground` is the sheet and the page. `--ground-sunk` is the timetable's hour bands, the footer
  and the venue table's header. `--paper` is a screening block and a pass row. Three surfaces, no
  fourth.
- `--ink` is every heading, film title and body line. `--ink-2` is metadata and secondary copy and
  is the lightest colour any text is allowed to take. `--ink-faint` is **not a text colour**: rules,
  ticks and the time rail's half-hour marks only.
- `--accent` carries exactly three jobs: the Book control's glass tint, a link in the sheet, and the
  focus ring. It never marks sold out, returns, a gala, a premiere or a strand. It is also absent
  from the control layer apart from that one tint: the selected day is a solid `--ink` fill with
  `--ground` on it, because the floating layer is monochrome but for its one tinted primary.
- `--rule-faint` draws the half-hour ticks, `--paper-lift` a screening block's hover, and
  `--fill-on-glass` a platter item's hover — the fill a thing sitting on glass uses instead of a
  second glass surface.
- `--glass-ink` is the floating layer's foreground, set on a child `<span>` of every host and never
  on the host itself, whose `background` the CSS tier rewrites every frame.
- Forbidden: a second accent; a hue for state; a colour literal anywhere outside `:root` except
  three commented exceptions — the `forced-colors` system keywords, the canvas painter (a 2D context
  cannot read a custom property), and the scroll-edge mask's `transparent`/`#000` stops, which are a
  mask channel rather than a colour. The Book control's tint is composed from `--accent` at runtime
  so the seed cannot drift from the token.

## 2. Typography roles, with placement rules

- `--font-mono` carries the **apparatus**: the wordmark, the opening film's title in the hero,
  every section heading, strand names, all times, durations, dates, prices, seat counts and venue
  codes. Uppercase with tracking above 13px; tabular figures everywhere it sets a number.
- `--font-sans` carries the **films and the prose**: film titles, director and country lines, notes,
  body copy, every control label in the floating layer.
- A film title is never set in the mono; a time is never set in the sans. That single rule is what
  the type system is checkable against.
- No eyebrow: no section carries a small tracked label above its heading. The section heading is
  itself mono uppercase, which is the device, used once per section and nowhere else.

## 3. Canvas, texture & material

The base ground is `--ground`, flat, with no grain and no gradient. The one texture on the page is
the live plane.

**Material model: glass over planes** (floating layer) over **printed** (everything in the sheet).
Printed means: `box-shadow` appears nowhere in the stylesheet, section boundaries are a 1px rule or
whitespace, and content radii stop at 2px.

**The live plane.** A `<canvas>` fixed to the viewport, painted once per resize with
`images/ironai-crossing.jpg` cover-fit to the window, a soft light wash under the hero copy, and a
2px monochrome grain field at ±5/255 — the film's own medium, painted *into* the plane so the lens
has a high-frequency term everywhere including the pale sky under the toolbar. It is registered as
the texture backdrop source `film`.

**Planes.** `base` carries the four bar surfaces. `overlay` carries the venue menu, which is
registered when it opens and released when it closes, and re-establishes its own label there.

**Groups.**

| Group | Members | Source | Backdrop | Gap to neighbour |
|---|---|---|---|---|
| `masthead` | the nav bar | texture `film` | measured; no hint, by contract | 96px |
| `filters` | day control, venue button | texture `film` | measured | 96px (28px inside the group, above `mergeDistance` so the two do not fuse) |
| `book` | the Book capsule, tinted | texture `film` | measured | — |
| `venuemenu` | the platter, overlay plane | dom | `{ tone: "light", luminance: 0.80 }` — it opens over the sheet as often as over the still, and both are light | — |

The three bar groups sample the texture rather than the DOM because the mask guarantees only the
still is ever behind them. The platter cannot make that claim, so it declares a hint instead. One
tint seed, on `book` only.

**Size family.** Three spans across the size law's band (inert below 32, saturated at 96): **40**
(day control, venue button, Book), **68** (masthead), **≥190** (the platter). The one-row floating
controls are capsules: radius 20 at height 40 and radius 34 at height 68. Below 560px the day track
and masthead step down to heights 36 and 56, and the capsule geometry follows their short side.
One thickness of **10** stays unchanged. Book remains the only tinted control.

The user-directed curvature follow-up prefers round capsules to rectangular controls; it does not
claim Apple requires them. The multirow venue platter keeps radius 28 and the printed content keeps
its established geometry. The selected-day pill is concentric: 20 − 4 = 16 on desktop, 18 − 3 = 15
on mobile. The platter items retain their existing radius 22. Layout, imagery, material and behaviour
remain unchanged.

**Concentricity anchor:** the viewport edge, square, with the page's own 80px margin standing in
for the window's inset. Every radius above is a fixed radius from the size family or a capsule; the
two concentric shapes are named above.

**Scroll edge.** One, on the one scrolling view: a `mask-image` on the scrolling stack, offset by
`scrollY` each frame from the glass root's own loop. Its two stops are the page's safe-area inset
and are measured from the bar's own box — `syncSafeArea()` writes the bar's bottom plus 12 and plus
76 back as `--edge` and `--edge-2` — because `env(safe-area-inset-*)` is zero on desktop and a
constant typed once stops being true the moment the bar's height changes. The mask is on `.stack`,
a sibling of the glass root, never on an ancestor of it. The web has no hard or soft scroll-edge
primitive, so this gradient is `liquid-glass.md` §1 step 7's own web equivalent; §8's "hard is the
desktop default" has nothing to resolve to here, and the tension is recorded rather than passed
silently.

**Fallback.** `?renderer=css` on the URL forces the CSS tier so it can be looked at rather than
assumed; it resolves `two-layer` bodies on all four groups and is still the design. The CSS tier
draws the same material without refraction. Reduced transparency,
increased contrast and forced colours are drawn states, not repairs: under forced colours there is
no glass and the bar reads as bordered system-coloured controls over the still.

## 4. Layout system

**The six composition lines.**

1. Posture: **narrative** — an authored public page read in the festival's order; nobody works out
   of it.
2. Dominant activity: **browse** — the first read answers "what is on, and what do I want"; the
   success condition is a reader who can name three screenings and see which of them clash.
3. Unit and relation: the unit is the **screening** (the festival's own noun: a film, at a time, in
   a venue); the relation the first read acts on is a **matrix**, time against venue, within a day.
4. Co-visibility: **none (one level)** — nothing in the brief asks for two films to be readable at
   once; the timetable carries title, director, country, runtime and marks, and the fuller note
   lives once per film in the strand it belongs to.
5. Temporal structure: **scheduled** — four dated days against three venues. There is no "now" mark
   because the whole schedule is eight weeks in the future; what stands in its place is the on-sale
   state per screening and the booking date in the hero.
6. Volume and homogeneity: **many homogeneous** in the timetable (39 screenings on one schema);
   **few heterogeneous** beneath it — five strands, three venues, four pass tiers, each with its
   own topology.

**Compiled consequences.** One dominant band in the first viewport, the still, and the timetable
dominant among the content regions. Reading order: still, programme, strands, closing night,
venues, passes — first in DOM order and top-left. Columns: the timetable is a 72px time rail plus
**three equal venue tracks**, equal because venues are peers and a 19:00 in one has to be
comparable with a 19:00 in another; the closing-night band is the page's one felt ratio, 1.72 : 1
image against copy, derived from the still surviving a 16:9 crop at 720px beside four short lines.
Density lives in the timetable. What repeats: the screening block (39), the venue track (3), the
strand block (5), the pass row (4). Chrome conventional: mark at the leading edge, section links
beside it, primary action at the trailing edge, credits and address in the footer.

**Ledger.**

| Brief evidence | Interpreted relationship | Layout constraint | Rendered assertion | Forbidden move |
|---|---|---|---|---|
| "a full-bleed still … fills the first screen" | The film is the festival's face and the window's live plane | Fixed, full bleed, and the only backdrop the floating layer ever sees | At scroll 0 and at the foot of the page the top 104px of the window shows the still; the bar's groups report `samplingBackend: "gpu-texture"` | The still cropped into a right-hand panel beside a headline |
| "the navigation and the date-and-tickets controls floating over it" | Three functions: identify, narrow, buy | Three groups in one bar, 96px apart, monochrome but for one tint | Four glass surfaces, three groups, base plane; exactly one carries a tint | A fourth group; any glass in the sheet |
| "the schedule by day and venue" | A matrix: time against venue, inside one day | One day at a time, a 15-minute rail and three equal tracks | The timetable is a CSS grid of three equal tracks with a labelled time axis, switched in place by the day control | One card per film; four day sections stacked |
| "twenty-four films … three venues" | Many homogeneous screenings; three peer venues; five heterogeneous strands | Density in the timetable; the venues are the page's only three-across group | 39 screening blocks, 24 film rows, 3 venue columns | A three-up of features; a pricing trio |
| "the strands and the passes extend beneath" | The programme is a printed object with sections | Titled sections parted by hairline rules and whitespace | `box-shadow` appears nowhere in the stylesheet | Stacked shadow cards for strands and passes |

**Chosen candidate: A — a day at a time, time against venue.** The day control in the floating bar
switches one timetable in place; the strands carry the films and their notes below it.
**Rejected candidate: B — one continuous programme, day after day, with an A–Z film index and a
venue filter.** It makes a reader hold four days in their head to see a clash, and it repeats one
topology four times down the page, which the narrative posture forbids.

**Prior adopted: titled sections (the editorial stack)**, earned by narrative posture crossed with
few heterogeneous content, opened by **full-bleed image**, earned by the brief naming it and by the
product genuinely being the image. Inside the programme section the nearest prior is **table-led**,
adopted for the dominant region's form on the relation (matrix) and the volume (many homogeneous);
the activity is browse rather than find, so no search field precedes it and there is none on the
page.

**Defaults overridden by name:** the headline band with an empty right half; the three-up of
features (the only three-across group is the venue tracks, earned by the brief's own count); the
pricing trio (four pass tiers in one table); the FAQ (no objections named); the sidebar (four
sections is not six peer destinations); the stat row; a card grid of the 24 films.

**Mechanics.** 1280px content column inside an 80px page margin — the same margin the bar's leading
item aligns to — one 8-based spacing scale (4/8/12/16/24/32/48/64/96/128), sections parted by a 1px
`--rule` and 96px of space, with the section rules full-bleed and every rule inside a section inset
to the column. Two elements stick: the timetable's venue header at `--edge-2`, so the band above it
is the scroll edge's ramp and never a half-covered row, and each strand's side head. The timetable
becomes its own scrollport only below 1080px, because `overflow-x: auto` computes `overflow-y` to
auto as well and a sticky header inside one sticks to the container instead of the window.
Collapse at 1080px: the masthead drops its section links to the footer, the venue button is
released from the plane rather than hidden, the venue three-up becomes one column, and the
timetable scrolls horizontally at its real minimum width rather than reflowing. At 760px the day
control keeps the numerals only and the Book capsule shortens to "Book". At 560px the page margin
drops to 16px, the size family steps down, and the plane's wash switches from a trailing ellipse to
a bottom lift, because the copy has moved from the trailing third to the lower two thirds.

**Imagery ladder.** Hero (`images/ironai-crossing.jpg`) and the closing band
(`images/haar-shore.jpg`) both came off **rung 2, Unsplash**; rung 1 held no photograph belonging
to this festival, and the brief's slot is a photograph of a world, not an artifact to draw. Both
are credited by photographer in the footer, and both are same-origin files because a cross-origin
image taints the texture source and demotes the group.

## 5. Component canon

`.bar-surface` (a glass host: a positioned box, a label `<span>`, nothing else), `.seg` (the day
control's track and its four buttons), `.platter` and `.platter-item` (the venue menu),
`.screening` (a timetable block: time, title, meta, marks), `.filmrow` (a strand's film: title,
credit line, note, the days it plays), `.venuecard`, `.passrow`, `.mark` (the one chip, for 35mm /
Q&A / sold out / premiere / captioned — neutral, bordered, never accent-coloured). The page's `h1`
is the festival line in the opening band; the opening film's title is an `h2`, because the page is
the festival's programme and the opening film is the first thing on it. Build order: tokens, the
plane, the bar, the timetable, the strands, the closing band, the venues and passes, the footer.

## 6. Voice

Composed and factual. Sentence case in prose, uppercase only where the mono sets the apparatus.
Times are 24-hour, durations in minutes, prices with pence only when they have them. No em dashes.
No buzzwords. A sold-out screening says "Sold out. Returns from 18:00 at the box office", not
"Unavailable". Empty states name the specific absence: "No screenings at Verdant Works on Thursday
5 November" with the filter's own way out beside it.

## 7. Motion

Two moves only. The venue menu **materialises**: its host is registered at the trigger's box and
its box springs to the open box over 240ms on `cubic-bezier(0.22, 1, 0.36, 1)`, so it grows out of
the control that opened it rather than cross-fading in. Press feedback is vitrea's own
`--vitrea-press` channel driven from the root's frame loop, a glow and a flex at the pointer, never
a colour swap. Everything else is a 120ms colour or border change. Under `prefers-reduced-motion`
the menu appears at its open box with no spring, and every transition is removed.

## 8. Hard don'ts

- No glass on a card, a row, a table, a strand, a pass or the sheet. Four surfaces, three groups,
  plus one platter. No fifth group.
- No `backdrop-filter` written by hand anywhere in the stylesheet.
- No `box-shadow` anywhere, including on the glass, which carries its own occlusion.
- No `background` on a glass host, no inline `transform` on one, and no glass host outside
  `root.plane(…).hostLayer`.
- No `filter`, `backdrop-filter`, `opacity` below 1, `mask-image`, `clip-path` or `mix-blend-mode`
  on `<html>`, `<body>` or any ancestor of the glass root: each one re-roots the backdrop and
  demotes the group.
- No prose on a glass surface. A surface carries a control's label and nothing else.
- No second tinted control, no second hue in a group, no `clear` variant, no non-uniform radii.
- No accent on a status: sold out, returns, gala, premiere and 35mm are words in a neutral chip.
- No eyebrow above a section heading, no numbered section markers, no side-stripe borders, no
  gradient text, no identical card grid.
- No lorem ipsum, no guessed image URL, no photograph without its photographer named on the page.

## 9. Accessibility

The runtime resolves reduced motion, reduced transparency, increased contrast and forced colours;
all three overridable ones are passed explicitly at the root because `prefers-reduced-transparency`
is not Baseline and a silent `false` is worse than a declared one. The page owes the rest: 4.5:1
for every label and 3:1 for large text, measured on rendered pixels over the still rather than
computed from tokens; a visible focus ring on every control in both the sheet and the plane; the
platter announced as a menu with its own label because portalled content leaves its landmark
behind; and `color-scheme: light` declared on the plane's own content, without which a reader whose
system prefers dark gets dark ink on light glass. The page has one colour scheme, declared at the
root, because the festival's programme is one printed object.

## User-directed capsule follow-up

The masthead retains its 22px end padding (16px / 13px at the existing narrow breakpoints),
the venue control its 16px, and the day track its 4px / 3px inset. This preserves the established
bar footprint while giving the capsule ends and selected segments their existing breathing room. Frozen PNGs and
`audit.json` remain baseline evidence; follow-up captures and checks live in
`figma-design-workspace/capsule-followup/film-festival/`.
