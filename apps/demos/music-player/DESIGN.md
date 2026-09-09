# DESIGN.md — Skerry, a desktop player

Design law for `apps/demos/music-player/index.html`. One page: a streaming service's Mac web
client, playing one album, at 1440 wide. Built on vitrea 0.14.0 through the workspace import map.

---

## 0. Stance commitment

A monochrome slate control layer, quiet and concentric, floating on a bright ice photograph that
carries every colour on the screen, interrupted only by one port-light red that means, wherever it
appears, *this is sounding now*.

What it is not: a dark player shell with the artwork blurred behind it. If a decision is ever
ambiguous, choose the option that gives the photograph more of the window and the chrome less.

**Axis position**

- **Density: standard** (constraint). The listener works elsewhere and returns to act; controls are
  reached at a glance, not scanned in rows all shift.
- **Criticality: exploratory** (constraint). Every action here is undone by pressing the opposite
  one. Nothing is audited, priced or irreversible, which is what permits transparency on the
  primary surfaces at all.
- **Energy: quiet.** The chrome sits on a photograph that is already doing the expressing; anything
  louder competes with the record it exists to play.
- **Type: characterful serif for the record, neutral sans for the controls, mono for time.**
  Tradition: transitional/Scotch. Criteria: faceted terminals and a large x-height so a 58px title
  holds over a textured photograph, a true italic for the liner note, tabular figures for durations,
  and a UI face native to the platform at 13px control labels.
- **Material model: glass over planes.** The artwork genuinely changes under the controls when the
  sounding track changes; the controls must not hide the thing they control. Rejected: elevated,
  which puts an opaque slab over the artwork the page exists to show. Nothing underneath declares a
  second model, because there is no second surface: content sits directly on the plane.
- **Color commitment: restrained.** The chrome is monochrome by rule; chromatic surface in the
  control layer is under 1%, and all of it is the sounding line.
- **Accent job: status-only.** One hue, one meaning: sounding now. It never carries an action, a
  hover, a focus ring or a heading.
- **Ground lightness: light.** Scene: a person at a desk in a lit room in the afternoon, the browser
  one window among several, music running while they work on something else. A player that turns
  into a black rectangle in the middle of a bright desktop is the thing to avoid.
- **Ground temperature: cool.** The neutrals are the photograph's own hue family, slate-blue around
  h 250 at C ≤ 0.02, so the chrome belongs to the plane instead of sitting on it as foreign grey.

**Rejected coordinate vector.** The modal streaming-client vector, composed / committed /
atmospheric / dark / brand-tinted: a dark shell with the artwork's dominant colour extracted and
washed behind the chrome, the brand hue carrying every action. It lost twice. The extracted-colour
wash is the flat field the material has nothing to refract over (rule 16), and dark is where every
verified competitor demo already sits, which `material.md` calls the easy demonstration.

**Derivation**

- *Accent hue.* The world of this record label is cold water and coastal navigation, and the one
  saturated convention in that world marks position in a passage: the port-side channel light.
  `--sounding` is `#9E2F24`, near `oklch(0.49 0.14 30)`: a deep lamp red rather than a brand red,
  set dark enough to hold 3:1 against the plane at its darkest phase. Weighed and rejected: a
  sea-blue pulled from the artwork itself, which fails `liquid-glass.md` rule 25 (it would vanish
  into the plane it sits on) and could not mean one thing, because it would change with every
  album.
- *Ground.* The plane is the photograph, so the "ground" decision is which photograph: a pale, cool
  one whose mean relative luminance is about 0.48. Weighed and rejected: `wpqpLxcXeZg`, a foggy snow
  coastline that is genuinely beautiful and genuinely dead flat across its right two thirds, exactly
  where the queue sits. That is rule 16, and it was caught by opening the file rather than by
  reading its caption.
- *Type.* Charter carries the record: a transitional serif with flat faceted terminals, drawn for
  coarse output, so it stays crisp at 58px over crystalline texture where a high-contrast Didone
  would shatter. It ships with macOS, which matters because this page loads exactly one external
  module and it is not a font. SF (via `-apple-system`) carries the controls because the brief is a
  Mac client and its control labels should be the platform's. SF Mono carries durations, timecodes
  and the catalogue number, which are genuinely tabular.

**Signature element: the sounding line.** One 2px rule in `--sounding`, in exactly two places: the
scrubber's elapsed fill, and a vertical rule beside the sounding track in the album list that fills
to the same fraction. Nothing else on the page is red. The volume slider borrows the same 2px track
shape and fills it in `--ink-2`, which is how the two read as one control language and still say
different things.

**Clone test.** Another streaming client would land on standard/exploratory and could plausibly land
on quiet/restrained/light. It would not land on Charter over a light ice plane with a port-light
status hue and no tinted control anywhere; those came from this record and this photograph.

---

## 1. Palette, with usage rules

Tokens live in the `:root` block of `index.html`; this section owns their jobs.

| Role | Job | Not allowed |
|---|---|---|
| `--ink` | Titles, track names, control labels, glyphs | — |
| `--ink-2` | Artist, durations, meta lines, secondary labels | Below 13px on the plane |
| `--ink-3` | Inert glyphs and the faintest rules | Any text |
| `--sounding` | Sounding-now status only: the scrubber fill, the album list's sounding rule | Any action, hover, focus, heading, icon or border |
| `--plate` | Fills *inside* a glass surface: row hover, the play button, menu row highlight | Any glass host's own background |
| `--hairline` | 1px dividers inside glass and in the album column | Anything above 1px |
| `--track` | The inert half of a 2px slider: the scrubber's remainder, the volume's remainder, the unplayed part of the sounding rule | Text, or any border |

- Every neutral is `--ink` at an alpha. There is no grey ramp and no second hue.
- No glass host carries a `background`, `border`, `box-shadow`, `backdrop-filter` or `border-radius`
  set by this page's own rules other than the radius that matches its registration; the CSS tier
  rewrites all of them every frame.
- No tint is passed to any group. `liquid-glass.md` rule 24 says the control layer is monochrome and
  saturated colour lives in the content layer; on this page the content layer is a photograph, so
  the tint budget is spent by not spending it. Rule 6 is satisfied at zero.
- Color literals appear in exactly two places outside `:root`: the canvas painting code, where the
  wash and the grain are arguments to a 2D context rather than styles, and the scroll edge's mask
  gradient, where the stops carry alpha and the colour is not rendered.

## 2. Typography roles, with placement rules

| Role | Family | Where | Never |
|---|---|---|---|
| Record | `Charter, "Iowan Old Style", Palatino, Georgia, serif` | Album title (58/1.02), the liner note in italic | Any control label, any glass surface |
| Control | `-apple-system, "SF Pro Text", system-ui, sans-serif` | Every label, row, heading and button on glass and in the queue | The album title |
| Time | `ui-monospace, "SF Mono", Menlo, monospace` | Durations, elapsed and remaining, track numbers, the catalogue number, playlist counts | Prose, titles, control labels |

- The catalogue kicker (`SKERRY EDITIONS · SKE 041`) is uppercase, tracked, mono, and appears
  **once** on the page. A second one anywhere is the eyebrow-on-every-section defect.
- Text on a glass surface is at most one short line or a real control's label. The liner note, the
  personnel and the credits are on the plane, never on glass.
- Every element inside a vitrea plane sets `color-scheme: light` so the runtime's `light-dark()` ink
  cannot flip to dark-scheme ink under a reader whose system prefers dark.

## 3. Canvas, texture & material

**Material model: glass over planes.** Path: **vitrea**, `@vitreajs/vitrea-web` 0.14.0 from the
workspace build through an import map. The deliverable is one HTML file plus a served repository; it
does not run from `file://` at all, because an ES module over `file://` is CORS-blocked.

**The live plane.** One `<canvas>`, `position: fixed; inset: 0`, painted at device pixel ratio and
registered as a `kind: "texture"` source declaring `taint: "clean"`, which is true because the
photographs are same-origin files in `images/`. It paints, in order: the artwork cover-fitted; a
reading wash,
white at 0.40 out to x=600 and falling to 0 by x=800, multiplied by a vertical factor that is 0
above y=124 and full by y=196 so no glass surface ever sits over it; and a 1px grain at 0.035. All
three are
painted **into** the texture, so the lens bends them. Changing the sounding track to a different
release cross-dissolves the plane over 520ms. The canvas is re-uploaded every frame by the runtime,
which is what makes the plane live rather than a still.

**Groups.** Three, all on the texture source, all `variant: "regular"`, none tinted, none declaring
`samplingPadding` or `mergeDistance` — the runtime derives 3σ from the blur it actually resolved.

| Group | Members | Plane | Declared backdrop | Measured range |
|---|---|---|---|---|
| `transport` | the transport bar, the volume capsule | base | `light`, luminance 0.38, complexity 0.85 | 0.27 to 0.49 |
| `queue` | the queue sidebar | base | `light`, luminance 0.34, complexity 0.85 | 0.27 to 0.42 |
| `menu` | the playlist platter | overlay | `light`, luminance 0.34, complexity 0.85 | 0.31 to 0.38 |

The declared luminance is the midpoint of the relative luminance measured off the plane under that
group's own box, across all three artworks; the range is recorded beside it because the plane
changes with the release. Declaring it costs the texture tier nothing (measured: `analysis` stays
`exact` on WebGPU, because the runtime still reads pixels) and it is what the CSS tier adapts to,
where the same groups resolve `hint` instead of `none`.

**Group separation.** Painted regions are laid out so no group's padded box reaches a neighbour's
painted region at 1440×900: `transport` paints 312–1128 × 24–112, `queue` paints 1088–1416 ×
208–828, `menu` paints 1124–1396 × 257–495 on the overlay plane. The vertical gap between the
transport union and the queue is 96px, past a conservative 64px padding, and no sampling padding or
merge distance is declared by hand.

**Geometry.** The concentric anchor is named: the viewport edge, treated as a macOS 26 window
corner of radius 46, which a web page cannot measure. Every floating surface sits at the 24px page
margin, so the concentric radius at that margin is 46 − 24 = **22**.

| Size | Short side | Radius | Kind |
|---|---|---|---|
| plate | 328 (queue), 272 (menu) | 22 | fixed, concentric with the window corner |
| bar | 88 (transport) | 44 | capsule, radius = height / 2 |
| capsule | 44 (volume) | 22 | capsule, radius = height / 2 |

Thickness **8** across all three. Inside a plate, rows inset 8 take radius 22 − 8 = **14**. Inside
the bar, the play button is a capsule at 56 and the previous/next hover fills are capsules at 40.
The transport uses 24px horizontal padding: its 44px outer radius minus that inset equals the
40px end buttons’ 20px radius. This capsule follows the user’s curvature preference, not a
requirement attributed to Apple. Every registered surface is at or above the size
law's floor of 32 and the family straddles the 32–96 band the law grades across.

**What stays out of the material.** The album identity, the tracklist, the liner note, the personnel
and the credits sit on the plane with no surface at all; queue rows, menu rows and the play button
are fills inside a glass surface, never hosts.

**Accessibility.** All three overrides are set explicitly at the root, because
`prefers-reduced-transparency` is not Baseline and a silent false is the failure mode. Under forced
colours there is no glass: the surfaces take `Canvas` with a `CanvasText` border and the page is
still a working player, because hierarchy is carried by layout, grouping and type. Contrast is
measured on rendered pixels, never attested.

## 4. Layout system

**The six composition lines**

1. **Posture: workspace.** The window is open for an afternoon and returned to; it is where the
   listening happens, not a page about it.
2. **Dominant activity: operate.** The first read serves "what is playing, and what do I do to it".
   The stage is the plane, at 4.4 : 1 against the widest thing beside it.
3. **Unit and relation: the track, in sequence.** Both lists are orderings and the whole product is
   about what comes next, so the ordering key leads every row.
4. **Co-visibility: none (one level), with one on-demand disclosure.** The page has no second level.
   The queue is a named supporting pane whose reason is that it is the ordering `next` acts on, so it
   must be visible whenever the transport is. The playlist menu is the one disclosure and it emerges
   from the control that opened it.
5. **Temporal structure: live.** Playback advances while the page is watched and the plane changes
   when the sounding track changes release.
6. **Volume and homogeneity: few homogeneous, per region.** Nine album tracks, six queue rows, three
   playlists; each set shares one schema.

**Compiled consequences.** One dominant region: the plane. Reading order: the plane and the album
identity first in DOM order and top-left, then the queue, then the transport, then the volume.
Ratio: plane 1440 to queue 328, about 4.4 : 1; album column 512 to queue 328 is 1.56 : 1, clear of
the forbidden 1.1–1.35 band. Density lives in the two row lists; the transport and volume stay
spacious. Repetition: the track row twice and the menu row once, nothing else. Chrome conventional:
the transport at the top of the window where macOS Music puts it, the queue at the trailing edge,
the volume beside the transport, the menu opening from the queue's own control.

**Ledger**

| Brief evidence | Interpreted relationship | Layout constraint | Rendered assertion | Forbidden move |
|---|---|---|---|---|
| "the current album's artwork fills the window" | The artwork is the content layer, not a backdrop for chrome | One canvas plane, fixed, inset 0, registered as the texture source | The plane's box equals the viewport at every width and every group reports `samplingBackend: gpu-texture` | A blurred or zoomed artwork wash behind an opaque shell |
| "the transport, the queue and the volume float over it" | Three floating controls, one control layer | Four glass surfaces in three groups, all inside vitrea planes | `[data-vitrea-node]` count is 4 and each is a control or navigation surface; `backdrop-filter` appears nowhere in the page's own CSS | Glass on the tracklist, the queue rows or the liner note |
| "a menu opens from the queue control" | A transient platter disclosed from a control | One host for the pair's whole life, on the overlay plane, box springing from the trigger's rect | `__glassDemo.openMenu()` grows one surface from the trigger's rect; no second surface fades in | A cross-fade between two glass surfaces |
| "one album with its tracks" | Nine rows of one schema, more than the column holds | The album column reaches the window's top edge and is inset from the transport by the bar's measured height | Its `padding-top` is read from the transport's rect and recomputed on resize; a hard scroll edge sits on its top | A fixed pixel offset typed once |
| "a queue of six" | A sequence read downward, ordering key first | A 328px sidebar of six 88px rows | Six rows, one visible ordering axis | A horizontal queue strip in the bottom bar |
| "three playlists" | Three peers the brief itself counts | Three rows in one icon group inside the platter | Three menu rows, all with leading icons | A three-up card grid of playlists |
| "desktop at 1440 wide" | One screen, no page scroll | Only the album column and the queue scroll, inside their own containers | Document height equals the viewport; capture width is 1440 | A page that scrolls its own glass out from under itself |

**Candidates.** Chosen: **A, plane with a trailing queue rail and a top transport** — album identity
and tracklist on the plane at the left, scrolling under a floating transport at the top; the queue a
floating sidebar at the trailing edge; the volume a capsule beside the transport in the same group;
the playlist platter opening from the queue's header on the overlay plane.

```text
+--------------------------------------------------------------+
|        [ transport bar ]  [vol]                              |
|  SKERRY EDITIONS · SKE 041                    +------------+ |
|  Fast Ice                                     | UP NEXT    | |
|  The Marram Trio                              | 6 rows     | |
|  1  Fast Ice            6:41                  |            | |
|  ...  (scrolls under the bar)                 |            | |
|  liner note, personnel, credits               +------------+ |
+--------------------------------------------------------------+
```

Rejected: **B, one bottom shelf** carrying transport, scrubber, volume and a horizontal queue in a
single wide bar. It destroys the sequence relation's ordering axis, puts text rows and icon buttons
in one glass background, and makes one surface so wide the size law saturates and the family
collapses to a single rung. Rejected: **C, the framed plane**, artwork inset in a rounded container
with the chrome in the margin around it — content then stops at the frame's inner edge instead of
reaching the window's, which is precisely the Tahoe failure `liquid-glass.md` §8 records.

**Prior adopted: primary region with supporting pane**, earned by line 4's named supporting pane
with its stated reason, over "full-bleed image" for the plane itself.

**Defaults overridden by name.** The dark player shell. The blurred artwork wash behind the chrome.
The left navigation sidebar every streaming client has (this surface has zero peer destinations; a
sidebar needs six). The listening-stats row (nothing here is monitored by the numbers). The three-up
(the three playlists are menu rows the brief counted, not columns). The bottom bar sitting *beside*
content in its own band of opaque background.

**Mechanics.** Page margin 72 for content on the plane, 24 for the floating layer. Spacing scale
4/8/12/16/24/32/48/72. Sections in the album column are separated by whitespace and one hairline
above the liner note; there are no cards anywhere on the page.

**Responsive collapse, at 1180px.** The queue stops being chrome and becomes content: its glass host
is released, the same DOM nodes move into the album column as an "Up next" section below the
tracklist, and the floating layer drops from four surfaces to three. The transport and volume shift
to the leading edge. This is a hierarchy change, not a compression: when there is no room to float
the queue beside the plane, the honest answer is that it is a list, and a list belongs on the plane.
Below 900px the volume capsule leaves too, because at that width the system's own volume is closer
to hand than a 184px capsule crowding the transport; the floating layer is then the transport and
the platter.

**Imagery ladder.** Rung 1, the project's own assets, holds only test fixtures and answered nothing.
All three photographs come from **rung 2, Unsplash**, downloaded into `images/` so the texture path
gets a same-origin file that cannot taint the source:

| Slot | File | Rung | Why |
|---|---|---|---|
| The album's artwork, and the live plane | `images/icehouse.jpg` (`CMosZWsrIoc`, Abby Santurbane) | Unsplash | Pale, crystalline, and structured at both frequencies the lens needs: fine grain everywhere and long cracks for it to displace |
| *Slow Thaw*, queue row 5 | `images/slow-thaw.jpg` (`if9vJoHDQes`, Aaron Burden) | Unsplash | The same label's world, distinctly bluer, so the two read as siblings and not duplicates |
| *Groyne Field*, queue row 6 | `images/groyne-field.jpg` (`6tA3NtdigD8`, Gabriel McCallin) | Unsplash | Warmer and hazier, which moves the plane's luminance far enough to prove the material adapts rather than being tuned to one picture |

Credits name every photographer with a link, at the foot of the album column where a sleeve's photo
credit belongs.

## 5. Component canon

- **Track row** (album list): mono number, title, mono duration, 36px. The sounding row adds the
  2px sounding rule at its leading edge and nothing else.
- **Queue row**: 56px sleeve, title, artist and release, mono duration, 88px, concentric radius 14.
  Row 1 carries the `NEXT` marker; rows 5 and 6 carry `FROM YOUR LIBRARY`.
- **Glass surface**: an element in a plane's `hostLayer`, registered with a radius from the size
  family and thickness 8, carrying no background of its own.
- **Icon button**: 40px hit box, 24px glyph, capsule hover fill in `--plate`, `aria-label` always.
- **Menu row**: leading 16px glyph, label, trailing mono count, concentric radius 14.
- **Scrubber**: a 2px track, `--ink-3` remainder, `--sounding` fill, a 12px knob, a real
  `<input type="range">` underneath for keyboard and screen readers.

Build order: plane, then album column, then transport, then queue, then menu.

## 6. Voice

Concrete and quiet. Sentence case everywhere except the one mono kicker and the two queue markers.
Real durations that sum correctly; real dates; a liner note written the way a label writes one, in
two sentences, naming the room and what happened in it. No em dashes. None of: streamline, seamless,
immersive, curated, elevate, transform. Control labels are verbs a listener would say out loud
("Play", "Previous track", "Add to playlist"), never system nouns.

## 7. Motion

- Glass **materialises and morphs**; it never cross-fades. The playlist platter is one host whose
  box springs from the trigger's rect to the open rect on five critically-damped springs (x, y,
  width, height, radius), with the radius written back through `handle.update` only when it has
  moved more than a quarter pixel.
- Press feedback is `--vitrea-press`, `--vitrea-glow` and `--vitrea-press-x/-y` written on the host
  at the pointer, never a colour swap.
- The plane cross-dissolves over 520ms on a release change. That is a state change, not idle motion.
- There is no idle motion anywhere: no shimmer, no drifting artwork, no ambient meter.
- Reduced motion: springs are replaced by an immediate jump, the plane cuts instead of dissolving,
  and the scrubber still advances because it is data, not decoration.
- Everything runs inside one `root.subscribe` callback. There is no second `requestAnimationFrame`.

## 8. Hard don'ts

1. No glass on a card, a row, a list, a table, the tracklist, the liner note or the credits.
2. No glass drawn on top of glass within one plane. The platter is on the overlay plane, which is
   the case `material.md` and `liquid-glass.md` §6 both name as supported and as how a morph works.
3. No `background`, `background-image`, `border`, `box-shadow`, `backdrop-filter` or `transform`
   authored on a registered host.
4. No `filter`, `backdrop-filter`, `opacity` below 1, `mask-image`, `clip-path` or `mix-blend-mode`
   on `<html>` or `<body>`. The scroll-edge mask goes on the scrolling container, which is a sibling
   of the glass root and not an ancestor of it.
5. No tint on any group, and no second hue anywhere in the control layer.
6. No hint whose tone or luminance is not the measured truth of the plane beneath that group.
7. `--sounding` never carries an action, a focus ring, a hover, an icon or a heading.
8. No second kicker, no numbered section markers, no eyebrow above any heading but the one.
9. No `lorem ipsum`, no `TODO`, no guessed image URL, no uncredited photograph.
10. No fixed pixel offset standing in for a safe-area inset; the album column's inset is read from
    the transport's measured box.
11. No page-level scroll. The document is exactly one viewport tall at 1440×900.
12. No sampling padding or merge distance declared by hand; the runtime derives 3σ from the blur it
    resolved.

---

## Decision log

- **2026-09-10 — user-directed capsule follow-up.** The listener preferred actively rounded
  floating controls, naming this player and park-trails as the strongest demos. The transport now
  has fully rounded 44px ends and 24px horizontal breathing room; the volume’s existing capsule declaration now also supplies explicit 22px renderer radii.
  The queue and playlist platter retain their larger-panel geometry. Layout, imagery, material,
  interactions and API are unchanged. Existing PNGs and `audit.json` remain frozen baseline
  evidence; follow-up captures live in `figma-design-workspace/capsule-followup/music-player/`.

- **2026-09-10 — the volume shares the transport's group.** It is a third surface but sits on the
  same band of the plane, 24px from the bar, and reads as one material with it. Rule 14 asks for
  spacing chosen so two surfaces merge or stay separate on purpose; 24px keeps them separate inside
  one backdrop read, where two groups would have put two padded proxy boxes 24px apart.
- **2026-09-10 — the transport is at the top.** macOS Music puts it there, and it is what makes the
  scroll edge real: the column reaches the window's top edge, is inset at rest by the bar's measured
  height (rule 17), and passes under it only while scrolling (rule 15). A bottom transport over a
  left column satisfied neither.
- **2026-09-10 — every group declares a backdrop as well as naming the texture.** The first build
  declared none, on the reading that a texture group lets the runtime read pixels. True on the
  WebGPU tier, false on the CSS tier, where the same groups resolved `analysis: "none"` and never
  adapted. Measured both ways: the declaration leaves the texture tier at `exact` and lifts the CSS
  tier to `hint`, so it costs nothing.
- **2026-09-10 — no tint, anywhere.** Rule 6 permits one tinted control; rule 24 asks that the
  control layer be monochrome and that saturated colour live in the content layer. On this page the
  content layer is a photograph, so spending the tint would have put a second hue on screen for no
  reason a listener could name.

## Deferred

- **The slider knob does not lift into glass.** `liquid-glass.md` §1 names this as the one exception
  running the other way, but vitrea raises `glass-inside-glass` in both directions and across
  planes, so a knob on the transport bar has no expression in v1. The knob is a fill.
- **Rule 12 and the queue.** It forbids a text button sharing a glass background with an icon
  button. It is written for toolbar items, and the queue's header control was made a text button
  ("Playlists") so the question does not arise; the rows are list items inside a `region`.
- **A renderer defect this page found, since fixed.** On the WebGPU tier before commit c62c19c, any
  glass surface larger than about 304px in **both** dimensions painted an opaque white rectangle
  over the region inset roughly 152px from every edge: the outer shadow's falloff fed `tanh` an
  argument that overflows to NaN on Metal past roughly 153px of depth. The band measured
  `(width − 304) × (height − 304)`, which is how the threshold was found (310 × 644 showed a
  6 × 340 band, 304 × 644 showed none); it reproduced on a page holding one surface over a flat
  texture, on either sampling backend, at any smoothing or thickness, and the CSS tier was clean.
  The clamp landed in the workspace build and the sidebar's interior draws in full at 328 × 620.
  Nothing in the size family is drawn around a ceiling; the widths here are the ones the rows
  wanted.
- **Cross-plane overlap when the platter is open.** Rule 2 forbids glass on glass. The platter is on
  the overlay plane and travels there from its trigger, which both reference files name as the
  supported case and which is what macOS Music does, but the eye still sees one surface over another
  while it is open. Recorded rather than passed silently.

## Responsive capsule regression fix — 2026-09-10

At 350px the 24px transport ends pushed the remaining-time box to x=332, past the
capsule's x=326 edge. At widths up to 400px the transport uses 12px ends, 8px control
gaps, no extra now-playing inset and 6px scrub-row gaps. Both time readouts and a
usable scrub track remain inside the curved silhouette; the 88px capsule and desktop
24px ends remain unchanged.

Verified in real Chromium with `node docs/research/scripts/capsule-responsive-regression.mjs`:
123 layout states across all three demos, including 721/732px, 350px, 1023/1024px and
three repeated round trips per demo. The assertions read actual runtime shape/radius
registrations as well as DOM bounds. Before/after captures live only under
`figma-design-workspace/capsule-responsive-fix/`; frozen captures and audits are untouched.
