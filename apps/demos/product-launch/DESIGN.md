# DESIGN.md — Sable One launch page

Project design law for `apps/demos/product-launch`. One page: the launch of the **Sable One**, a
mirrorless camera made by Sable Optical Works, a forty-bodies-a-week works in Bristol. Desktop at
1440. One HTML file plus a served repository: it imports the workspace build of vitrea 0.14.0
through an import map (`/packages/core/dist/index.js`, `/packages/platform-web/dist/index.js`), so
it needs `python3 -m http.server` at the repository root and an `http://localhost` origin. It does
not run from `file://` at all, because a browser will not load an ES module over an opaque origin.

## 0. Stance commitment

**One committed idea.** A room hung with low-key photographs of a machined object, in which the only
things that float are the navigation and the thing you press to buy. The page is the maker's own
photography at full window, a column of ruled specification over it, and two glass bars that read
their material off the picture underneath them. It is **not** a feature marketing page: no three-up
of benefits, no pricing trio, no testimonial, no icon set, and no card whose only job is to hold a
sentence. *If a decision is ever ambiguous, choose the more literal option* — the number over the
adjective, the photograph over the illustration, the rule over the box.

**Axis position.**

- **Density: standard** (constraint) — the reader passes through four sections once and fills one
  small configuration; dense would make a spec sheet of a launch, spacious would bury the numbers a
  £3,290 decision turns on.
- **Criticality: transactional** (constraint) — money moves, against a deposit that is refundable
  until the batch is cut, so nothing here is irreversible and nothing is regulated.
- **Energy: composed** — the object is bought after weeks of reading, and a page that shouted would
  contradict its own claim of eleven controls and no menu.
- **Type: neutral sans, grotesque tradition, in a condensed cut for display, with a mono for data** —
  criteria: a family with a width axis so the display line reads as the engraved lettering on an
  aluminium top plate, a tall x-height that survives being set over a photograph, tabular figures,
  and a mono with an unmistakable 0/O for focal lengths, apertures and prices.
- **Material model: glass over planes** for the floating layer, **tonal** for the page's own
  surfaces beneath it — the earning test passes on its own terms: the photographic stage genuinely
  changes under the controls, both as the reader scrolls and as the configuration changes, and the
  bars have to stay readable across all of it. The sheets, rules and tables in the scrolling column
  are tonal, three lightness rungs and a hairline, and they carry no glass.
- **Color commitment: restrained** — the photographs carry every hue on the page; chromatic surface
  outside them stays under a tenth.
- **Accent job: directional** — the index mark, and only that: the selected lens, the selected
  finish, the tint on the reserve action, and the focus ring. It never carries status.
- **Ground lightness: dark** — the scene: a working photographer at a desk at the end of a day,
  looking at seven low-key macros of a black machined object. Those photographs are the page; a
  light ground would set them as bright rectangles on white and would leave the floating bars over a
  uniform field.
- **Ground temperature: brand-tinted** — the olive bloom on a multicoated lens element, held at
  C 0.022 and hue 122 so the ground is recognisably built from the product's own colour.

**Rejected coordinate vector.** standard · transactional · quiet · characterful serif · printed ·
restrained · none · **light** · neutral — the luxury-fashion vector the sampler drew: a white page,
hairlines everywhere, a Didone display, no accent at all. It lost on the imagery: every photograph
the ladder returned for this subject is a low-key macro, so a white page turns them into bright
rectangles, and the floating bars would sit over a uniform white field, which is the ghost-glass
failure `liquid-glass.md` names at step 5.

**Sampled ingredients.** Two mutations kept: luxury-fashion's **hairline organisation**, which
retires the card grid for the three lenses in favour of one ruled table, and the **condensed display
cut**. Declined in one line each: risograph and bauhaus, which no page whose content layer is
photography survives; the old-style serif, because this is a machined object and not a book; the
heavily coloured canvas, because the photographs are the colour.

**Derivation.**

- *Accent.* **Index red `#E9644C`** (OKLCH 0.665 / 0.170 / 32), from the red index dot on a lens
  mount, the mark you align to fit a lens to a body. It marks alignment and commitment, which is
  exactly the accent's one job here. Weighed and rejected: **amber-gold**, the coating bloom itself,
  because it is the ground's own hue family and it is already the loudest colour inside the
  photographs; an accent that is in the picture cannot mark the one thing to press.
- *Ground.* **Olive-bronze `#1F2216` / `#2D3125` / `#3B3F32`**, the bloom on coated glass. Weighed
  and rejected: **a neutral near-black** — where a dark camera page lands by reflex, and half of
  `taste-calibration.md`'s second saturated default (near-black plus one hot accent). The olive is a
  colour the object actually has, and it moves the ground out of that band.
- *Type.* Under the criteria above: **Saira Condensed** for display, **Saira** for UI and body,
  **Spline Sans Mono** for every number. Three families are licensed by a real data role: seven
  specification tables of figures that must align in columns.

**Signature element.** *The stage answers the configuration.* The live plane behind the glass is the
product being configured, so choosing a finish or a lens changes the photograph the whole page
stands on, and the two floating bars re-read their material from it in the same frame.

**Clone test.** Another mirrorless launch would share the two constraint lines and could plausibly
share the seven coordinates. It may not share this olive, this index red, this family trio, or a
composition in which a viewport-fixed photographic plane carries the whole scroll while the
specification column passes over it.

## 1. Palette, with usage rules

Values live in `:root` in `index.html`; this section owns which role does which job.

| Role | Token | Job |
|---|---|---|
| Page ground | `--void` | Behind the stage, and the ink the audit measures glass labels against. |
| Sheet | `--panel` | The one sheet per section. Nothing else takes it. |
| Raised row | `--panel-2` | A table's header row and its selected row. The ladder stops here: three rungs. |
| Ink | `--ink` | Headings, body, every label on glass. |
| Secondary ink | `--ink-2` | Table values, captions. |
| Tertiary ink | `--ink-3` | Metadata and units. Allowed on `--void` and `--panel` only; it does not clear 4.5:1 on `--panel-2`. |
| Accent | `--index` | The accent role. Marks and fills only. |
| Accent as text | `--index-text` | The same role where it has to be a word or a rule on a sheet. |
| Fills | `--fill-hover`, `--fill-on`, `--fill-seg`, `--well` | What sits **on** glass. Rule 2 allows a fill, a transparency or a vibrancy there, never a second material. |
| Rules | `--line`, `--line-firm`, `--line-lit` | Hairlines, at 14 / 26 / 44 percent ink. |
| Tint seed | `--tint-seed` | The one tinted control's seed. The module reads it back from `:root` rather than holding a second copy. |

Rules. There is **no second accent**: no green, no amber, no blue anywhere in the stylesheet. No
status set exists, because the page has no status. The two inline SVG glyphs take `currentColor`.
Exactly two colour literals live outside `:root`, both named here: the `#000` stops in the scroll
edge's `mask-image`, which are alpha keywords rather than a colour, and the per-state multiply factor
the stage's treatment computes from that state's own exposure number. The accent never carries meaning
alone: a selected lens is the accent tick **and** a filled radio **and** the word "Fitted".

## 2. Typography roles, with placement rules

- **Display — Saira Condensed 600.** The hero claim, the four section titles, the price total.
  Nowhere else, and never below 22px.
- **UI and body — Saira 400/500/600.** Every sentence, every control label, every link.
- **Data — Spline Sans Mono 400/500.** Figures only: focal lengths, apertures, weights, dimensions,
  ISO ranges, dates, prices, and the small caps labels that key a table's rows. Never a sentence.

Placement. Headings inherit their role from the token system and are not restyled per section.
The one tracked small-caps label, `.key`, is a **row key**: it names the left side of a definition
row, a bar control, or a total, and it never sits above a heading. There is no kicker above a section
heading anywhere on this page, which is the check that matters: the label marks what a value is, not
that a section has started.

## 3. Canvas, texture and material

The canvas is the **photographic stage**: a viewport-filling `<canvas>` the page paints itself, from
seven same-origin JPEGs in `images/`, cover-fit, cross-dissolving over 420ms when the section or the
configuration changes. It is registered as vitrea's texture backdrop source, so the glass samples the
pixels the reader is looking at rather than a hint about them. Every state is treated in the canvas,
at full frame: a warm multiply that normalises exposure so the top and bottom bands of every state
land between 20 and 85 of 255, and brings seven photographs by six photographers into one system.
The treatment is applied to the whole image; there is no darkening layer under either bar, and no
scrim.

Material model, both lines: **glass over planes** for the floating layer (§4), **tonal** for the
scrolling column. Tonal means three rungs — `--void`, `--panel`, `--panel-2` — plus a 1px hairline at
14% ink. No shadow appears anywhere on the page: the glass carries its own occlusion and the sheets
do not lift. No `backdrop-filter` is written by hand.

## 4. Layout system

### The six composition lines

1. **Posture: narrative** — an authored page, read once, in the maker's order, by someone deciding
   whether to spend £3,290.
2. **Dominant activity: decide (buy)** — the first read answers "what is this and is it for me", and
   the success condition is a reservation with a finish and a lens chosen. Proposition, then
   evidence, then the action, with the action reachable in the first viewport.
3. **Unit and relation** — the unit is the brief's own noun, **the camera**; the relation the first
   read acts on is a **set**, one body in two finishes with one of three lenses. Beneath it runs a
   **sequence**: sensor, lenses, body, price.
4. **Co-visibility: on demand, over a permanent commitment strip** — the price and the configuration
   stay visible while the evidence is read, which is what the floating bottom bar is for; the lens
   comparison opens on demand as a platter from that bar.
5. **Temporal: static** — nothing moves on its own. Delivery dates are scheduled facts, not a feed,
   so there is no live badge and no "real-time" copy anywhere.
6. **Volume and homogeneity: few heterogeneous** — four sections with four different topologies. The
   one repetition is the three lenses, which are three homogeneous peers **by the brief's own
   count**, and the two finishes, which are two.

### Compiled consequences

- **Dominance: one dominant** — the photographic stage. It is the product, it holds the whole first
  viewport, and it stays behind everything below.
- **Reading order** — the stage is first in DOM order and fills the window from the top left; then
  the hero claim, then the four sections in the maker's order, then the credits. The two bars live in
  the glass planes, which are appended last and are fixed to the viewport by construction.
- **Columns and ratio** — no page-level split. One measure of 44rem over the stage, centred, so the
  stage stays present at both edges at 1440. Inside a section, where units are peers they take
  **equal tracks**: three lens columns, two finish columns. There is no felt ratio on this page
  because nothing on it is a dominant region beside a subordinate one.
- **Where density lives** — the specification tables, and nowhere else. The bars and the hero stay
  open.
- **What repeats** — the three lens columns and the two finish options. Nothing else repeats.
- **Chrome** — conventional: wordmark leading in the top bar, four section links after it, the
  configuration and the price in the bottom bar with the commit action trailing.

### The ledger

| Brief evidence | Interpreted relationship | Layout constraint | Rendered assertion | Forbidden move |
|---|---|---|---|---|
| "Hero photography of the camera fills the first screen" | The photograph is the product, not an illustration of it | The stage is a viewport-fixed plane behind everything, at every scroll position | A 1440×900 capture at scroll 0 is photograph edge to edge, with no band of page background anywhere | A hero section that ends at a fold and hands over to flat bands |
| "with the navigation floating over it" | Navigation is a distinct functional layer, not a band of chrome | The navigation is one glass surface in the base plane, inset from the viewport, with content passing beneath it | The nav bar has no background, border or scrim of its own; the stage is visible through it | A full-width sticky header with a solid or blurred bar behind it |
| "the sensor, the lenses, the body and the price scroll beneath the floating bar" | Four heterogeneous evidence sections in the maker's order, in one scroll | One document scroll, one measure, four titled sections, each with its own topology | Section titles read Sensor, Lenses, Body, Price in DOM order; no two sections share a topology | A card grid of four "features" |
| "three lens options" | Three homogeneous peers the brief itself counts | One three-column ruled table, all three aligned on every row | The three lenses share one axis in one region; each column has the same eight rows | Three cards with an icon, a heading and a paragraph |
| "two body colours" | Two peers, and a choice that changes the object | Two equal options, and choosing one changes the stage photograph | Selecting Nickel or Graphite cross-dissolves the plane and moves the tick, the radio and the word "Fitted" | A colour swatch that changes nothing but itself |
| "a configure-and-buy bar floats at the bottom" | The commitment must stay reachable through the whole read | Two glass surfaces in one group at the bottom of the viewport, present from first paint | The price and the reserve control are on screen at scroll 0 and at the end of the document | A buy box that scrolls away, or a bar that appears only after the fold |

### Candidates

**Chosen — stage behind, column over.** The photographic stage is viewport-fixed and fills the
window at every scroll position; a single measure of sections scrolls as the document over it. The
hero fills the first screen, so at rest nothing has reached either bar, and the intersection happens
only while scrolling.

```text
+------------------------------------------------------------+
|  [ SABLE ONE ][ sensor lenses body price ]        <- glass  |
|                                                             |
|         F O R T Y - F O U R   M E G A P I X E L S           |
|              (the stage: photograph, full bleed)            |
|                    +----------------+                       |
|                    |  measure 44rem |   <- scrolls as the   |
|                    |  ruled sheets  |      document          |
|                    +----------------+                       |
|  [ Finish · Lens ]                    [ Reserve £4,430 ]    |
+------------------------------------------------------------+
```

**Rejected — stacked bands.** A full-bleed hero, then opaque sections stacked under it. Past the
first screen the bars sit over flat sheets, and the live plane stops living at the fold.

**Rejected — the asymmetric split**, stage left and specification right at 1.6 : 1. The brief asks
for the sections to scroll *beneath* the bar, which is one scroll over one plane, and a right-hand
column at 1440 puts the bottom bar beside content instead of over it.

**Prior adopted:** **full-bleed image** ("the image is the product"), crossed with the **product
detail** prior's collapsed form — a sticky commitment bar rather than a sticky buy-box beside a
gallery. The line that earned the crossing: the stage takes the whole width, so the buy-box has
nowhere to sit beside it and becomes the bar the brief asks for.

**Defaults overridden by name:** the headline band with an empty right half (the right half is the
photograph); the three-up of features; the pricing trio (there is one price); the FAQ; the stat row;
the sidebar; the eyebrow above every section; the almost-equal split.

### The plane split

Two planes, which is all there are. **Base** carries the navigation bar and the two members of the
configure-and-buy bar. **Overlay** carries the lens platter, and only while it is open, so the one
overlap on the page is a cross-plane one. The stage and the column are ordinary
document DOM beneath the root; nothing in them is portalled. The plane content is given its own
landmarks by hand, because a plane's DOM sits outside every landmark the document wrote: the
navigation host is a `<nav aria-label="Sable One">`, the configure host is a `<section
aria-label="Configure">`, and the platter is a `<div role="menu">`.

### The floating-layer inventory

Four surfaces, and the list is short enough to read aloud.

1. **`nav-mark`** — the wordmark, a link to the top of the page.
2. **`nav-sections`** — the four section links, one control.
3. **`configure`** — the finish choice and the lens trigger.
4. **`reserve`** — the primary action, the one tinted control on the page.
5. **`platter`** — the lens menu, on the overlay plane, present only while open.

Everything else is opaque: the sheets, the tables, the rules, the hero claim, the credits. Each of
the five is navigation or a control; none of them is a card, a list, a panel or a hero.

### The group plan

| Group | Members | Backdrop | Why one group |
|---|---|---|---|
| `nav` | `nav-mark`, `nav-sections` | texture `stage` | Both are navigation, read together, spaced 10px so they merge at rest. |
| `commit` | `configure`, `reserve` | texture `stage` | Configuration and its commitment are one act. Spaced 12px, merging. |
| `platter` | `platter` | texture `stage` | A transient surface on another plane reads its own material and gets its own group, so an unplaced platter cannot drag the bar's sampling union. |

All three declare `backdropSourceId: "stage"` **and** one measured hint,
`{ tone: "dark", luminance: 0.05, complexity: 0.8 }`. The reference says a texture group declares no
hint, and on the WebGPU tier that holds: the runtime reads these pixels and reports `analysis:
"exact"` either way. The hint is for the CSS tier, which has no texture path and without it resolved
`analysis: "none"` and never adapted at all, making the fallback a degraded copy rather than the
design. It is measured: across all seven states the band under a bar sits between relative luminance
0.014 and 0.058, over a photographic plane. `nav` and `commit` sit about 700px apart, far past any
sampling padding either could resolve; `platter` opens 16px above `commit`, on the other plane. No
group declares `samplingPadding` or `mergeDistance`; the runtime derives both from the resolved blur.

### The size family

Three sizes, one radius each, one thickness across all of them. Span is the short side, which is
what vitrea's size law reads, and the family straddles the law's band on purpose: it is inert below
32 and saturated at 96.

| Surface | Span | Radius | Shape | Thickness |
|---|---|---|---|---|
| `nav-mark`, `nav-sections` | 44 | 14 | fixed rounded rect | 8 |
| `configure` | 64 | 20 | fixed rounded rect | 8 |
| `reserve` | 64 | 32 | capsule (half the height) | 8 |
| `platter` | 268 | 26 | fixed rounded rect | 8 |

Concentricity. A web page has no bezel, and this page's outer frame is the viewport edge, whose
corner radius is zero, so no floating surface can be concentric with it. That is recorded as the web
deviation it is: the three outer radii above are fixed values from the family, and concentricity is
held **inside** each surface instead, where rule 9 actually bites. A control nested in a host takes
the host's radius minus its inset: the section links inside `nav-sections` are 32 tall at a 6px inset,
so 14 − 6 = 8; the segmented track and the lens trigger inside `configure` are 44 tall at a 10px
inset, so 20 − 10 = 10, and a segment inside that track sits at 3px, so 10 − 3 = 7; a platter row
inside `platter` sits at 10px, so 26 − 10 = 16. `reserve` is a capsule, because it is the one
standout action and Apple reserves capsules for exactly that in a dense desktop layout.

Merging. The two members of each bar are spaced **16px, above the merge threshold**, so each reads as
its own control: the wordmark is a link home and the section list is navigation, and the configure
cluster and the commitment are two acts. Fusing either pair would read as one combined control, which
HIG Toolbars names as the failure.

### The backdrop design

The plane is real content, so both frequencies are there: broad tonal masses for the lens to bend,
and wood grain, knurling, aperture blades and coating bloom for it to displace. Two things are still
designed. The crop, per state, so the bands the bars stand on carry structure rather than an empty
corner: the hero is zoomed 1.3 and offset to the frame's right so the copy falls on clean wood and
the camera bleeds off the leading edge. And the exposure, so every state's bar bands sit in one range
and one ink passes over all seven. Nothing is laid over the plane in CSS, so everything the glass
refracts is painted into the canvas that *is* the texture.

### The scroll edge, and the rule it half answers

**The document is the scroller.** Not a fixed inner container: a page whose column scrolls inside a
fixed box is one viewport tall to everything outside it, so its scrollbar, its scroll restoration,
find-in-page, fragment navigation and every full-page capture see one screen. The column scrolls as
the document, `#column` takes `position: relative; z-index: 1` because the plane is `position: fixed`
and would otherwise paint over it, and fragment links land clear of the bar through
`scroll-margin-top` rather than through a hijacked click handler.

**Rule 15 is answered at rest and lost mid-scroll, recorded rather than passed.** The clearance is
real: the column's padding is derived from the two bars' **measured** boxes and kept in step by a
`ResizeObserver`, and the hero's minimum height is derived from the same numbers so that the first
screen holds the hero alone. At rest no content sits under a glass control, which is the rule that
shapes layout. The fade itself is not there, and it cannot be: a mask that follows the viewport has
to live either on an ancestor of the glass root, where `mask-image` re-roots the backdrop and demotes
every group with `probe-failed`, or on the column with stops driven from scroll position, where a
full-page capture at scroll 0 masks the entire page away. Both were built and measured. What is left
is the language's own second half, that the intersection happens only while scrolling and the
material occludes what passes under it. There is no darkening layer under either bar, and no scrim.

### Mechanics

Grid: one column, `min(44rem, 100% - 4rem)`, centred, in the document flow. Sections are
separated by a 96px gap and a hairline, never by a card. Spacing scale 4 / 8 / 12 / 16 / 24 / 32 /
48 / 64 / 96 / 128. Radius scale 0 / 4 / 8 / 12 / 16 / 20 / 26 / 9999. Two responsive collapses, each an intentional
rearrangement. At 900px the measure goes full-width at 24px gutters, the top bar spans the width and
its section list scrolls inside itself, and the bottom bar's two surfaces stack with a 16px gap, so
they still do not overlap within the plane; the three-column lens table becomes three stacked blocks
that keep the same eight row keys, so the comparison survives. At 560px the bar sheds what it can
rather than overflowing: the model name leaves the wordmark, the `Finish` and `Lens` keys and the
divider leave the configure bar, and the lens price leaves the trigger, because the price is already
on the reserve control beside it.

### Imagery, per slot

Every photograph is rung 2 of the ladder, **Unsplash** through
`skills/designer/scripts/find-image.mjs search`. Rung 1 did not answer: `find-image inventory` lists
200 images in this repository and every one is a test fixture or a calibration capture. Rungs 3 and 4
were not needed. Files are downloaded into `images/` and referenced by relative path, because a
cross-origin image taints the canvas and demotes the group to `tainted-source`.

| Stage state | File | Photographer | Job |
|---|---|---|---|
| hero | `hero-body.jpg` | Wesley Hilario | The camera on a bench: the first screen, and the widest tonal range on the page. |
| sensor | `sensor.jpg` | kuaileqie RE | The mount with the lens off. |
| lens 28 | `lens-28.jpg` | Kool C | Aperture blades, wide. |
| lens 45 | `lens-45.jpg` | Agence Olloweb | Aperture blades with the coating bloom. |
| lens 90 | `lens-90.jpg` | Tatiana Conde | The mount contacts, close. |
| finish Nickel | `finish-nickel.jpg` | Jonathan Cosens Photography | Knurled metal: the fine frequency the lens displaces. |
| finish Graphite | `finish-graphite.jpg` | Jonathan Cosens Photography | Leatherette and a viewfinder window. |

Every photographer is named with a link in the page's credits section, which is what the Unsplash
licence asks for. All seven downloads are registered with Unsplash through `find-image pick`, which
its API terms require; the first attempt returned 403 with `x-ratelimit-remaining: 0` on the shared
demo key and succeeded on retry an hour later, and the credit links in the page are the canonical
handles that call returned rather than guessed ones.

## 5. Component canon

- **`sheet`** — the one section container. One per section, `--panel`, radius 16, hairline, no
  shadow. There is no card.
- **`spec`** — the one table. A ruled definition table: a mono small-caps key on the left, a value on
  the right, hairline between rows, `--panel-2` on a header or selected row.
- **`spec--peers`** — the same table with n value columns, used for the three lenses. Rows are the
  same keys; columns are the peers.
- **`choice`** — the one selection control: a real `<input type="radio">` with a visible tick, a
  label, and the accent. Used for the two finishes and the three lenses, in the bar and in the sheet.
- **`glass-bar`** — a registered vitrea host. Only the five surfaces in §4 are one.
- **`index-tick`** — the signature mark: a 2px accent rule at the leading edge of whatever is
  currently selected.

Build order: tokens, stage, column and sections, then the glass root and its five hosts, then the
platter, then the channels and the motion.

## 6. Voice

Composed and literal, British spelling, first person plural for the maker ("we publish the service
manual"). Sentences are short and carry a number wherever a number exists. No exclamation marks, no
em dashes, and none of the buzzword family. Case: sentence case everywhere except the mono table keys
and the wordmark. An empty state does not arise on this page; the one error state that could —
choosing a lens that is not yet shipping — is written as a plain sentence with the date in it.

## 7. Motion

Three motions, each answering an input or a state change; the system has no idle motion and this page
has none.

- **The stage cross-dissolve**, 420ms `cubic-bezier(0.32, 0, 0.16, 1)`, when the section or the
  configuration changes. It is a change of state, not decoration.
- **The platter**, which materialises out of the lens trigger: one registered host whose box springs
  from the trigger's rect to the open rect over 260ms while `--vitrea-lens` and `--vitrea-sweep` rise
  from 0 to 1. There is no cross-fade between two glass surfaces anywhere.
- **Press**, which is `--vitrea-press` with `--vitrea-press-x/y` at the pointer, driven on the frame
  the root already runs. It is never a colour swap.

Under `prefers-reduced-motion` the dissolve and the platter both become instantaneous and the press
spring is not driven; the runtime removes elastic behaviour on its own, and no layout depends on it.

## 8. Hard don'ts

- No glass on a sheet, a table, a row, the hero, or anything in the scrolling column.
- No glass inside glass. The controls inside a bar are plain DOM with a fill, never a second host.
- No opaque `background`, no `border` and no shadow written onto a registered host: the CSS tier
  rewrites the shorthand every frame and Apple names the solid fill as the failure. The single
  permitted declaration is `background: transparent` with `appearance: none`, which removes the user
  agent's own button face; without it the reserve control drew as a flat `#6B6B6B` slab and the
  material was invisible. Under forced colours the hosts do take a system background, because there
  is no glass left there to destroy.
- No hand-rolled `backdrop-filter` anywhere in the stylesheet.
- No scrim, no darkening layer and no gradient under either bar, and no mask, filter, opacity below
  1 or clip-path on any ancestor of the glass root.
- No second accent, no status colour set, and no colour literal outside `:root`.
- No shadow token exists. Nothing on this page lifts except the glass, which carries its own.
- No card grid, no three-up of benefits, no pricing trio, no FAQ, no stat row, no kicker above a
  heading.
- No em dash in page copy, and no word from the buzzword family.
- No `filter`, `opacity < 1`, `clip-path`, `mix-blend-mode` or `mask-image` on any ancestor of the
  glass root's container: each of them re-roots the backdrop and demotes every group with
  `probe-failed`.
- No control below span 32 in the floating layer, where vitrea's size law is exactly inert.
- No host is registered before the first layout has settled. A host measured while its own type
  metrics were still moving was reported as `same-plane-overlap` on roughly one load in eight.

## 9. Legibility and the fallback

The contrast floor is measured on rendered pixels, not assumed: `--ink` on `--void` is 14.4:1, on
`--panel` 11.9:1, `--ink-2` on `--panel` 7.1:1, `--ink-3` on `--panel` 4.8:1 and it is not permitted
on `--panel-2` (3.9:1). Labels on glass carry their own colour rather than inheriting
`--vitrea-foreground`, which is a two-token ink pick and promises no ratio. The rule sits on the host,
which is correct at 0.14.0: the runtime delivers its ink as one prepended `:where([data-vitrea-node])`
rule at zero specificity, so an app rule on the host wins. Measured on rendered pixels, the plate
behind every label clears 6.3:1 at its worst across all seven stage states, the open platter and the
reduced-transparency pass.

The CSS tier, reduced transparency, increased contrast and forced colours are states of this design
rather than repairs, and each was opened and looked at. `?tier=css` on the page's own URL forces the
fallback, which is how it is checked rather than assumed; opening the page from `file://` does not
force the tier, it stops the module loading. Hierarchy is carried by layout, grouping and type, so removing the material
removes an effect and not the structure: the bars keep their boxes, their spacing and their ink.
The hero's own minimum height and both column insets are `calc()` over the measured bar tokens, so a
bar that changes size moves them. `reducedTransparency` and `increasedContrast` are set explicitly at the root, because
`prefers-reduced-transparency` is not Baseline and a root that leaves it to the media query silently
resolves it false. Under forced colours the stage is hidden and the bars take system colours, because
an unreadable photograph behind system-coloured text is worse than no photograph. The root declares
`colorScheme: "dark"`, and every plane-side element declares `color-scheme: dark`, so a reader whose
system prefers light does not get light ink on this page's dark glass.

Tier expectation: **webgpu** on Chromium over `https` or `http://localhost`, with
`samplingBackend: "gpu-texture"`, `refraction: "true"` and `analysis: "exact"`, because the plane is
a canvas the page owns. Every other engine, and any Chromium without an adapter, gets the CSS tier,
which is the same material without refraction and is a complete design.
