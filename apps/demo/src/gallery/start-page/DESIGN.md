# Daybreak — a start page, in the spatial register

A browser start page. The day's photograph of one valley fills the window; the time, the weather,
the day's agenda, the tasks and the places the person goes sit on glass over it, glanceable from
across the room and workable up close; a search field leads. Built under `skills/materialist`
(SKILL.md 1.1.0, its `references/vitrea.md`, `optics.md` and `examples.md`) on
`@vitreajs/vitrea-react` 0.24.0, workspace source.

## Part one — the record, written before the first host was registered

The lines below are the skill's record template (`references/examples.md`, spatial form). Numbers
marked *measured* were read on this machine before any page code existed: a throwaway probe put a
400 × 400 window and a 300 × 56 capsule on a texture group over a uniform canvas at 21 encoded
levels, both schemes, both poses, both tiers, and read the drawn body back from the screenshot.

```
register: spatial. Daybreak is a launcher / start surface — the skill's first named spatial case.
  Nothing on the page acts on the photograph; the person searches, goes somewhere, glances at the
  day and ticks things off. The surfaces are the interface and the photograph is their
  environment. It is not an instrument over content (there is no content being operated on) and
  not a worksheet with translucent cards: three windows, not a tile field.

environment: one viewport-fixed, full-bleed <canvas> painting the day's photograph cover-fit with
  a per-photograph crop, registered as the texture source `daybreak` and supplied as an
  ImageBitmap placed on the canvas element (imported once per repaint, not every frame). The
  photograph is one valley, Val d'Orcia and the Crete Senesi south of Siena, at four times of
  day; those are the environment's four PHASES:
    dawn   05–09  "Layers of Light", near Pienza, mist and a lit farmhouse (Fabrizio Lunardi, CC0)
    day    09–17  "Val d'Orcia – Montichiello", cypress road under cumulus (Marco Usan, CC BY 3.0)
    dusk   17–21  "Tramonto a Montichiello", banded cloud over a burning sky (Marco Usan, CC BY 3.0)
    night  21–05  "Site Transitoire", the Milky Way over the Crete (Emiliano Carchia, CC BY 3.0)
  By default the phase follows the local clock, like a dynamic desktop picture; the person can
  pin one from the photograph platter. A phase change repaints at once: it is a state, not an
  animation. Every glass footprint was checked on the photographs before layout: the search
  ornament sits over cloud, ridge line or stars (never a flat sky gradient), the windows over
  fields, cloud banks or star field, i.e. a broad term to bend and a fine one to displace in every
  phase.
  Grading, derived from the measured body curves:
    light material, thick (span 400) and capsule (span 56): the drawn body never falls below
      0.518 encoded at any backdrop level (0.498 receded at backdrop 0.05) and the runtime picks
      dark ink everywhere; dark primary over the 0.518 floor is 4.9:1 — *measured*. So in the
      light scheme the photographs are shown as shot; the only obligation is the night phase's
      near-black, where the receded floor is thinnest, so the night photograph is lifted just
      enough that no footprint reads below 0.08 encoded.
    dark material: the thick body rises 0.125 → 0.36 over backdrop 0 → 0.30, then enters the
      published-ink dead band (0.396 at 0.35) and saturates at 0.478 over white, where white
      primary reads 3.7:1 — *measured*. The capsule body climbs to 0.67 and flips its ink across
      the band. So the dark scheme gets its own grade of every photograph — an "evening print",
      a tone curve that keeps shadows and compresses highlights — tuned per phase until the
      blurred backdrop under every glass footprint stays at or below 0.28 encoded (body ≤ 0.35).
      Pinning the scheme is not the answer; grading the plane for the scheme is.
  Source statistics, tone input and drawn level are kept apart: (1) the source's whole average is
  what a texture group reads without a hint and it is not representative of any one window, so
  (2) each group declares the level measured under its OWN box from the painted canvas — the
  runtime's own statistic, the encoded per-channel mean decoded once, Rec. 709 luma — re-measured
  on every phase change, scheme change, resize and layout change (the gaps move with Reduce
  Transparency), and (3) the drawn surface behind each text line is measured on rendered pixels,
  per line, and is what gates contrast.

windows: (role words as on the hosts' data-glass-role)
  module  "Now"       the glance: time, date, conditions now, five-day forecast. Figures, not
                      prose. ≈ 320 × 340, span ≥ 320, radius 32. Left column.
  window  "Places"    twelve places the person goes, a 4 × 3 grid of plain links on lighter
                      child fills; typing in the search narrows them. ≈ 496 × 400, radius 32.
                      Centre column.
  window  "Today"     the day's agenda (nine events, past ones quieter, the current one lifted)
                      and seven tasks with real checkboxes, in one child scroller with scroll
                      edges at the window's inner edges. ≈ 376 × 530, radius 32. Right column.
  ornament "Search"   capsule, 56 high, overlay plane, attached ABOVE Places and centred on it,
                      no wider than it, outside its edge by the runtime-derived gap. A search
                      form: glyph, text field, nothing else. It leads: topmost surface, focused
                      at load, `/` returns to it.
  ornament "Photograph" capsule, 48 high, overlay plane, attached BELOW Now at the derived gap;
                      names the phase and its photographer. It is the closed end of a
                      matchedGeometry GlassMorph whose open end is the
  platter "Photograph" the four photographs, follow-the-day, Reduce transparency, the credit.
                      Opens below its ornament into open environment; it never overlaps a
                      window (a texture-path platter over a window would show environment where
                      the eye expects the window's glass).
  Environment visible around every one: a sky band above (only the search in it), ≥ 64 px
  between columns, a foreground band below the windows where the photograph's subject — the
  farmhouse, the cypress road, the horizon, the monument — stays in view.

groups: five, one member each, all texture `daybreak` with a declared hint measured as above:
  `now`, `places`, `today` (base plane), `search`, `photograph` (overlay plane; the morph's own
  group). Gaps are never pinned: each gap is ceil(max(samplingPaddingFor(a), samplingPaddingFor
  (b))) of the two groups it separates, from the root's own document, the resolved scheme and the
  resolved accessibility policy — *measured* 63.2 px between two windows (64 laid out), 71.6 /
  76.6 under Reduce Transparency light / dark. The layout reflows when that number moves and
  invalidates the hosts' geometry.

family: thickness 8 across every surface (no reason to leave the home default: the windows are
  reading surfaces, not lenses to show off). Windows and module: fixed radius 32, spans 320–500.
  Ornaments: capsules (56 → 28, 48 → 24). Platter: fixed 24.
  anchor: the window corner, r 32. Inner fills inset 20 take 32 − 20 = 12; rows inset 12 in
  a section take 12 − 4 = 8 where they meet a section corner; the search field's inner mark
  inset 8 takes 28 − 8 = 20. Opaque imagery (the photograph thumbnails in the platter) sits in
  frames of 24 − 12 = 12.

tint: none. The photograph is the page's colour and the glass carries its hue on the GPU tier;
  a tinted primary would be a second hue fighting a sunset. Accent withheld, deliberately.
  Emphasis is weight, size and the lighter "selected" fill.

scheme and pose: colorScheme auto, the page's own tokens follow prefers-color-scheme;
  windowActivation auto — the receded pose is looked at and measured, never pinned.

motion: the photograph platter morphs from its ornament (matchedGeometry, own group); nothing
  else moves. The clock ticking and the photograph changing at a phase boundary are content.
  No idle motion, no parallax, no entrance. Reduced Motion: the runtime's non-elastic morph.

tier expectation: webgpu on localhost Chromium (texture path: refraction "true", analysis
  "exact"); css elsewhere and on ?tier=css — the same page without refraction or hue. cssBody
  per group, the DPR and the present-host area recorded on the CSS capture (part two).

accessibility: the runtime follows the system for motion and contrast. Reduce Transparency is
  the page's own setting in the platter, passed to the root as a boolean (default: the system
  query where the engine answers it, else off; remembered), so the engine that cannot answer
  still gets the person's answer and no diagnostic. Forced colours: glass removed, every window a
  Canvas panel with a CanvasText border; child fills become borders; the current event, the
  checked tasks, the selected photograph and the switch carry marks (border, glyph, check), not
  translucent fills.

contrast: every text line on glass is styled on a child from the runtime's primary and
  secondary tokens (tertiary only for hairlines; quaternary never named). Measured per rendered
  line: ink = the line's computed colour composited over the drawn surface, surface = the pixels
  of the line's own box with the text hidden, worst of median and 10th/90th percentile; 4.5:1 for
  text below 24 px (18.67 px bold), 3:1 above; both schemes × four phases × active and receded,
  scrolled and at rest, GPU and CSS tiers, and with transparency reduced. Worst line gates; every
  failing line is recorded in part two as a failure.

fidelity: Apple's macOS 27 material composed in Apple's visionOS way — Apple-shaped at window
  scale, not visionOS glass. Window spans 320–500 extrapolate the fitted laws beyond the span-160
  bed (shadow σ keeps growing, amplitude holds, body depth saturated). No clear variant anywhere.
  Nearest Apple surfaces: macOS 27 desktop widgets over a dynamic desktop picture, and Safari's
  Start Page with a background image; no native capture was made for comparison.
```

### Why this composition, and what was rejected

- **Three surfaces, not six.** The brief lists six things (search, time, weather, agenda, tasks,
  places). Six glass tiles is the tile field the register refuses. Time and weather are one glance
  ("what is it like now"); agenda and tasks are one working surface ("what is today"); search and
  places are one act ("go"), which is why the search ornament hangs from the Places window and
  narrows it as the person types.
- **The clock on the photograph** (a lock-screen clock with no glass) was considered for the
  across-the-room glance and rejected: text straight on a photograph has no measured floor across
  four phases and two grades, and the glance module is exactly the form the register gives a
  figure.
- **A platter that opens over a window** (from an ornament in the top band, or above the Now
  module) was rejected: on the texture path the platter samples the environment, not the window
  under it. It opens downward into open photograph instead, which is why the Photograph ornament
  hangs below the module.
- **Dark scheme by pinning the night photograph** was rejected: the scheme is the person's system
  setting and the phase is the time of day; they are different facts. Each photograph gets a dark
  grade instead.

## Part two — what building changed, and what was measured

Everything below was read from the built page on this machine (macOS 27, Chromium with
`channel: "chromium"` on the Apple GPU for the WebGPU tier, the same binary with `?tier=css` for the
CSS tier), at 1440 × 900 CSS px, device scale 1 unless stated, with the clock pinned by the
capture aid `?at=15:10` so the agenda holds a past event, the event in progress (lifted), the next
one and later ones in every capture. Without `?at` the page reads the real time.

### What drew

- **WebGPU tier**, all five groups: `activeRenderer webgpu`, `samplingBackend gpu-texture`,
  `analysis exact`, `refraction true`, `health ok`. The texture is the painted canvas, first as a
  canvas source (so a phase change shows on the next frame) and then as an ImageBitmap placed on
  the canvas element (imported once, not every frame).
- **CSS tier** (`?tier=css`): `css / css-backdrop`, no refraction, no hue retention. `cssBody` is
  **collapsed** at the design size — 569,364 device px of present hosts at 1x and 2,277,456 at 2x,
  both over the 400,000 budget; 489,931 at 1280 × 720 1x, also collapsed — and **two-layer** only
  at 1024 × 768 1x (387,670). Both forms were looked at: the collapsed body is a flatter, even
  frost; the two-layer body keeps a little more of the valley's structure behind the type. The
  hierarchy is carried by layout and type in both and nothing reads differently. These areas are
  the maker's reads; the review's and the fix wave's later reads stand beside them in "The fix
  wave after the independent review" below, with the statistic defined.
- The headless shell (no adapter) resolves the WebGPU request to the CSS tier and reports the
  environment finding `webgpu-unavailable`, which is the honesty core working.
- Material: the default macOS 27 document; `windowActivation` auto. The receded pose was captured
  by `root.setWindowActivation("inactive")` for the capture only.

### Diagnostics

**Zero authoring findings**, both channels (`root.diagnostics` and `root.scene.diagnostics`), in a
sweep of 32 configurations — GPU channel and headless shell × WebGPU request and `?tier=css` ×
light and dark × 1440 × 900, 1280 × 720, 1024 × 768 and 1920 × 1080 — each driven through load,
all four phases, the receded pose, Reduce Transparency on, the platter opened and closed, a
query typed, the Today scroller at its end, a live resize, forced colours, then Increase Contrast
with Reduce Motion. The only codes reported anywhere were environment codes
(`webgpu-unavailable` on the headless shell). `reduced-transparency-undetectable` never fires,
because the root always receives the page's boolean. `pnpm --filter demo test:e2e
e2e/gallery.spec.ts -g start-page` passes in both schemes.

### The environment's three quantities (encoded luma; the runtime's statistic)

| scheme · phase | source average | declared: Now · Places · Today · Search · Photograph | drawn body median (Now · Places · Today) |
|---|---|---|---|
| light · dawn | 0.483 | 0.549 · 0.565 · 0.474 · 0.769 · 0.402 | 0.830 · 0.872 · 0.806 |
| light · day | 0.493 | 0.477 · 0.374 · 0.349 · 0.835 · 0.288 | 0.781 · 0.795 · 0.734 |
| light · dusk | 0.333 | 0.344 · 0.391 · 0.349 · 0.317 · 0.497 | 0.736 · 0.807 · 0.751 |
| light · night | 0.255 | 0.228 · 0.260 · 0.300 · 0.211 · 0.268 | 0.663 · 0.745 · 0.704 |
| dark · dawn | 0.179 | 0.202 · 0.206 · 0.182 · 0.237 · 0.168 | 0.269 · 0.324 · 0.252 |
| dark · day | 0.168 | 0.164 · 0.143 · 0.139 · 0.235 · 0.117 | 0.235 · 0.274 · 0.217 |
| dark · dusk | 0.137 | 0.145 · 0.156 · 0.147 · 0.133 · 0.192 | 0.222 · 0.285 · 0.226 |
| dark · night | 0.149 | 0.139 · 0.154 · 0.173 · 0.128 · 0.159 | 0.218 · 0.284 · 0.242 |

Declared and source values are the painted canvas's; drawn medians are the WebGPU tier's, focused
pose, transparency nominal, read inside each host 28 px in from its edge.

The Places body median sits on its lifted tiles, which cover most of its interior. Across every
phase, both poses and both tiers the drawn window and module bodies stay outside the dead band:
light 0.635–0.872 (dark ink), dark 0.164–0.324 (light ink); Reduce Transparency frosts them to
0.94–0.99 light and a constant 0.25 (Now, Today) / 0.30 (Places) dark. The day photograph shows
why the declaration is per footprint: its whole average is 0.493 while the search ornament stands
over cloud at 0.835 and the Photograph ornament over shadowed field at 0.288. Hints are
re-measured on every phase change, scheme change, resize and layout change, and for the
Photograph group on every frame its morph moves.

### Contrast — every rendered line and mark on glass

**Whose run this is.** The matrix and the table below are the maker's own run, not the independent
audit's. A Playwright script (`measure.mjs`, in the maker's scratch directory `/tmp/sp/`) drove
full Chromium on the GPU against the dev server at 1440 × 900, device scale 1, with the clock pinned
by `?at=15:10` (`&tier=css` for the CSS tier); it set the scheme on the browser context, Reduce
Transparency through the page's `__glassDemo.setReducedTransparency`, the phase through
`__glassDemo.setPhase`, the pose through `root.setWindowActivation`, and the five states by
scrolling the Today scroller, typing "gi" and `__glassDemo.openMenu()`. Its output, `final4.json`,
holds the 14,128 line-and-mark readings counted below and 1,600 body-level readings (SHA-256
`05b61fdbab24e882348c385e034bab6ba27ca285b2875c87dc065d02d68ba34d`). That file was scratch,
outside the repository; the session copied it and its script into the initiative's evidence at
`docs/research/data/2026-09-27-materialist-spatial-register/review/start-page-maker-contrast/`
(`final4.json`, same SHA-256, and `measure.mjs`) at the fix wave's landing. The independent audit
(`docs/research/data/2026-09-27-materialist-spatial-register/audit/start-page.json`, audited
2026-09-27 08:07 UTC) is a separate and narrower read: 3,061 line readings, all 3,061 passing,
worst 5.16:1. It covers the first viewport, the Today scroller's positions and the open menu in
both schemes, the four phases in both schemes, and light-scheme subsets for the CSS tier, the
receded pose and reduced transparency. It ran without the clock pin, so its captures read
17:06–17:07 and its agenda is a different current-event state from this run's. It finds no
failure in what it covers; it does not reproduce this matrix, and neither set of numbers
replaces the other.

Method as part one: surface = the pixels of each line's own box with all text, glyphs and marks
hidden; ink = the line's computed colour composited over them; the gate is the worst of the 10th,
50th and 90th percentile surface pixels. Lines are enumerated from the DOM per rendered line
(`Range.getClientRects`), the placeholder included; icons and the checkbox and switch marks are
graphical objects at 3:1, a glyph drawn on a filled mark against that fill.

Matrix: two tiers × two schemes × four phases × active and receded × transparency nominal and
reduced × five states (at rest; the Today scroller at its top and at its end; a query typed with
its place lifted; the platter open): **14128 readings, 13656 gated (9536 text lines at 4.5:1, 2240 large-text lines at 3:1, 1880 icons and marks at 3:1); 0 below their floor.** Nothing failed, so no failing line is listed.
The platter state was measured again after the platter was tightened (item 6): its 928
readings are among these, the lowest 5.30:1. The worst reading per tier, scheme and transparency
setting:

| tier · scheme · transparency | text lines, worst (where) | large text, worst | icons & marks, worst |
|---|---|---|---|
| WebGPU · light · nominal | 5.17 — “Search or type an address”, Search, night inactive (n 1192) | 6.85 (n 280) | 6.73 (n 235) |
| WebGPU · light · reduced | 8.33 — “H”, Now, day active (n 1192) | 13.50 (n 280) | 13.50 (n 235) |
| WebGPU · dark · nominal | 4.81 — “Search or type an address”, Search, dawn active (n 1192) | 4.91 (n 280) | 6.04 (n 235) |
| WebGPU · dark · reduced | 5.29 — “15:00”, Today, dusk active, top (n 1192) | 5.30 (n 280) | 7.47 (n 235) |
| CSS · light · nominal | 5.12 — “Search or type an address”, Search, night inactive (n 1192) | 6.82 (n 280) | 6.68 (n 235) |
| CSS · light · reduced | 8.33 — “H”, Now, day active (n 1192) | 13.50 (n 280) | 13.50 (n 235) |
| CSS · dark · nominal | 4.82 — “Search or type an address”, Search, dawn active (n 1192) | 4.93 (n 280) | 6.06 (n 235) |
| CSS · dark · reduced | 5.29 — “15:00”, Today, dusk active, top (n 1192) | 5.30 (n 280) | 7.38 (n 235) |

The tightest line on the page is the search field's placeholder over the dawn ridge in the dark
scheme, 4.81:1 (WebGPU) / 4.82:1 (CSS); the median text line reads 6.93:1 light and 6.57:1 dark.
Every line on the Now module reads at least 5.2:1 in either scheme, so the across-the-room glance
has margin everywhere.

Lines inside the Today scroller's masked edge bands (28 px top, 36 px bottom, only while content
continues past them) are deliberately faded by the scroll edge; they were measured but not gated
(472 readings). Nothing else was excluded. Not measured:
Increase Contrast (its near-monochrome ink only raises contrast; looked at, not gated), forced
colours (system colours; looked at), and the platter thumbnails, which are images.

### What building changed

0. **The dawn crop.** The first build put the search ornament over dawn's flat peach sky — the
   one footprint part one said would never be a flat gradient. The dawn photograph is now zoomed
   1.16 and framed so the Radicofani ridge and its fortress run behind the ornament's lower half
   and the lit farmhouse stays in view below the Today window. The other three phases were checked
   the same way: cumulus (day), banded cloud (dusk) and the star field (night) behind the search.
   Built sizes at 1440 × 900: Now 320 × 332, Places 496 × 404, Today 376 × 600, Search 440 × 56,
   Photograph 248 × 48 closed and 320 × 226 open; one gap of 64 px (72 light / 77 dark with
   transparency reduced). (Beside these, from the fix wave below: the Photograph host's closed box
   is 248 × 48 on the WebGPU tier and was 250 × 50 on the CSS tier, radius 24 on both, until the
   fix wave sized it as a border box; it now reads 248 × 48 on both tiers. The gap reads 63 px.) The search ornament also names the place Return will go to (`↵ GitHub`).
1. **The secondary ink is authored.** The runtime's `--vitrea-foreground-secondary` read
   **4.30–4.49:1** on these drawn bodies in both schemes (it is solved against the surface the
   runtime models from the declared level; the drawn body differed by a few hundredths). Every
   description line now takes `color-mix(in srgb, var(--vitrea-foreground) 84%, transparent)`,
   declared on each host's children: it keeps the pole the runtime picked, and its transit, and
   holds the ratio. Tertiary is used only for the forecast's hairline; quaternary is never named.
2. **Dark lifted fills halved.** A 20 % white lift under the event in progress put its primary
   title at 4.32:1 and its secondary at 2.98:1 in the dark scheme; the dark lift is now 7 % /
   13 %, and every line on a lifted fill takes the primary ink.
3. **The dark grade became a luma curve.** Compressing each channel greyed the dusk sky and the
   day's fields; the curve now maps each pixel's encoded luma and scales the pixel, so the evening
   print keeps the photograph's hue. It holds every window body at or under 0.324.
4. **The gap has two floors.** Under forced colours the material draws no blur and the derived
   padding fell to zero; the runtime's overlap check still reads its advisory 24 px, and reported
   `group-proxy-overlap` twice. The gap is now the larger of the advisory padding, the current
   policy's derivation and the nominal policy's, so a preference can open the layout (Reduce
   Transparency: 64 → 72 / 77 px) but never close it.
5. **The Photograph ornament's closed face is fixed-width** (248 px, the widest maker's name): a
   closed morph never follows a new closed size. Below about 1200 px wide, where the Now column
   is narrower than that face, a second, compact face (phase only, 120 px) is a second morph by
   key, and the platter is forced closed across the switch so a morph is never mounted open.
6. **The platter was tightened and scrolls inside itself** where the viewport is too short for it
   below its ornament. At 249 px it first scrolled by 17 px under Reduce Transparency — the one
   setting that lives inside it; at 226 px it now ends 56 px above the bottom edge at 1440 × 900,
   38 px (light) and 28 px (dark) with transparency reduced. It never flips upward over the
   module.
7. The module lost its one-sentence outlook (prose in a glance module) and gained a line of
   height in the narrow layout; the clock scales with the module (container units); the page
   keeps British English's 24-hour clock whatever the browser's locale; the Today window opens
   scrolled to the event before the one in progress, measured by rects rather than `offsetTop`
   (whose parent was the host, so the first version scrolled a header too far).
8. **Forced colours on the WebGPU tier** draws each host as a Canvas panel with no CanvasText
   border (the CSS tier writes a 2 px border on the host). Each host's one full-size child now
   draws a 2 px CanvasText frame there, keyed on the tier the runtime reports, so a white panel over
   a white cloud keeps its edge. Never on the host.
9. **The search's focus ring** appears only after keyboard navigation (Tab or `/`): the field is
   focused at load and a ring at rest would be a second edge on the lead. It is concentric, drawn
   by the child (28 − 6 = 22).

### Gaps found in the runtime (for its tracker)

- **Secondary token under its promise** on drawn bodies: 4.30–4.49:1 against 4.5 (item 1).
- **Forced colours, WebGPU tier: no CanvasText border** on the panel (item 8).
- **`GlassMorph` realigns a closed host without invalidating its geometry.** When the layout moved
  the ornament's footprint without resizing it (Reduce Transparency opening the gap), the morph
  wrote the host's new `left`/`top` and the glass stayed at the old box. The morph exposes no host
  handle, so the page marks that one host dirty by dispatching a `scroll` event at it — the
  geometry sync's own "this host moved" signal — whenever its rect changes.
- **`GlassMorph` collapses to 0 × 0 when Reduce Motion changes while it is mounted** (found by
  the independent review on this page; tracked as "`GlassMorph` collapses to 0×0 when Reduce Motion
  toggles mid-session" in `docs/doperpowers/specs/tech-debt-tracker.md`). The page's workaround is
  in the fix wave below.
- **`GlassMorph` passes no `data-*` attribute to its host**, so the audit contract's
  `data-glass-role` (`ornament` closed, `platter` open) is written onto the host after each frame.

### Recorded limits and decisions

- **Focus and reading order.** Hosts portal into the root's planes inside `<main>`, the overlay
  plane after the base: in the DOM the search and the Photograph ornament come after the three
  windows. The search takes focus at load and `/` returns to it; it is also the `search` landmark.
- **Hover** on a place tile, a task or a platter row lifts its child fill a step; that is content
  inside a window (visionOS's hover highlight), not a glass state. Glass press is the runtime's:
  the search ornament is `interactive`, the closed Photograph ornament is the morph's pressable
  end, the windows are not interactive.
- **Motion** the page owns is the switch knob's 180 ms slide, removed under Reduce Motion. The
  phase change repaints at once; there is no dissolve.
- **Narrow viewports** (under ~1200 px) keep the three columns scaled with the compact ornament;
  the brief is desktop at 1440 and nothing narrower was designed further.
- **`[eye]`.** The nearest Apple surfaces are macOS 27 desktop widgets over a dynamic desktop
  picture and Safari's Start Page with a background image; no native capture was made, so no
  comparison was made. Seen by eye without one: vitrea's rim lights the top-left of each large
  window as a diagonal sheen, where Apple's edge is a thin line bright at vertical normals;
  and a 600 px window's shadow is the size law extrapolated far past the bed.

### The fix wave after the independent review

2026-09-27. The review, which read the page before this wave, is
`docs/research/data/2026-09-27-materialist-spatial-register/review/start-page.md`. It fixed two
findings and recorded two notes; nothing the review listed as holding was touched. Every reading
below is full Chromium (`channel: "chromium"`) on the Apple GPU against the dev server at
1440 × 900, device scale 1, `?at=15:10`, unless stated.

- **A live Reduce Motion change no longer loses the Photograph platter** (finding 1, check 14).
  Before this wave, opening the platter and then changing the preference moved the morph's host
  from about (61, 618, 320, 226) to (0, 0, 0, 0) with focus left on the vanished photograph radio.
  The cause is the runtime's, named under "Gaps found in the runtime" above, and what the page does
  is **a workaround for that seam, not its fix**, following the cookbook's recipe: the morph's key
  now carries the resolved `useGlassAccessibility()?.reducedMotion` beside the compact/full face,
  so a change of preference remounts it with the new motion profile instead of leaving a mounted
  morph to rebuild its springs at zero (`photograph-ornament.tsx`). A morph mounted open would
  measure the platter as its closed size, so the app closes the platter in the same render in
  which the key changes, and records the key it was opened under, so it stays closed if the change
  reverses (`app.tsx`). Focus that the remount drops, from the platter or from a trigger still
  closing, returns to the new trigger once the new morph has measured and placed its closed face;
  until then its trigger sits in an unplaced host and cannot be pressed, which is what keeps a
  reopen from reaching a morph that has not measured. Focus held outside the morph is not moved.
  No opacity transition was added. The platter closing on a preference change is the workaround's
  cost: the runtime fix (reseed the geometry at its current value and target) would keep it open,
  and until that lands the review's check 14 stays recorded against the runtime.
  Read live on both tiers, a flip each way with the platter open and settled: the host goes from
  the open box (61, 618, 320 × 226) through the new morph's unplaced box for two frames (0 × 0 at
  the origin, then 0 × 0 on WebGPU and 2 × 2 on CSS, the border's floor, at its footprint) to the
  closed capsule at (61, 562, 248 × 48), where it stays for the rest of the 90-frame trace; it is
  never left at 0 × 0. Focus lands on the trigger, the group reports `health ok`, the Enter key on
  the focused trigger reopens the platter to 320 × 226 with the selected photograph focused, and
  Escape closes it back to 248 × 48 with focus on the trigger, under both preferences. Also read,
  on WebGPU: a flip five frames into an opening and three frames into a close by Escape both settle closed
  at 248 × 48 with focus on the trigger; a flip while the search field holds focus leaves it
  there; and crossing into the compact width with the platter open and back again leaves it
  closed at 248 × 48 (before this wave the face key alone kept the platter's open state, so by the
  code's reading the crossing back would have remounted the morph open; that was not reproduced).
  Both diagnostic channels stay empty and no
  page error is raised.
- **The closed Photograph ornament is an exact capsule on both tiers** (finding 2, check 9). The
  morph writes its host's box from its springs, and the CSS tier gives every host a 1 px border
  that is layout; the generated host was a content box, so the CSS tier drew 250 × 50 at radius
  24. The class the morph passes to its host now sets `box-sizing: border-box`
  (`start-page.css`), as `boxStyle` does for the other four hosts. Read after the change, closed:
  WebGPU 248 × 48, border 0, registered radii 24; CSS 248 × 48, border 1 px, radius 24 registered
  and computed; CSS under forced colours 248 × 48 with its 2 px CanvasText border; WebGPU under
  forced colours 248 × 48. Open, 320 × 226 on both tiers. The cost is inside the host on the CSS
  tier: the content box is inset by the border, so the fixed 248 × 48 trigger sits 1 px right and
  down and its last 2 px, padding, are clipped (4 px under forced colours' 2 px border), and the
  platter's right and bottom padding show 10 and 8 px of their 12 and 10. Looked at, closed and
  open, on both tiers and under forced colours: no label, mark or link is cut.
- **The contrast record names its run** (finding 3, checks 12 and 23). "Whose run this is" at the
  head of the contrast section identifies the maker's matrix and the independent audit as two
  reads; no number in either was changed and no ink was changed.
- **Later layout readings, beside the earlier ones** (finding 4, checks 19 and 28). Two statistics,
  kept apart:
  - *Present-host device pixels*: the sum over every registered host (`[data-vitrea-node]`) of its
    border box's width × height × dpr², read on `?tier=css` at `?at=15:10`; this is the maker's
    statistic, and the CSS root compares its own sum with the 400,000 budget. `cssBody` is the
    runtime's report for all five groups.

    | viewport | maker (part two) | review, before this wave | this wave, after the border box | `cssBody` |
    |---|---|---|---|---|
    | 1440 × 900 @1 | 569,364 | 569,364 | 568,768 | collapsed |
    | 1440 × 900 @2 | 2,277,456 | — | 2,275,072 | collapsed |
    | 1280 × 720 @1 | 489,931 | — | 489,335 | collapsed |
    | 1024 × 768 @1 | 387,670 | 390,950 | 390,610 | two-layer |
    | 1024 × 768 @2 | — | — | 1,562,440 | collapsed |

    This wave's reductions are exactly the Photograph host's lost border: 596 device px at
    248 × 48 (2,384 at 2x), 340 at the compact 120 × 48. The review's 390,950 is what the current
    layout gives at a 63 px gap with the host at 122 × 50; at 64 px the same arithmetic gives
    389,740, so the gap alone does not account for the maker's 387,670, whose layout state was not
    reconstructed. No viewport changes side of the budget.
  - *The window gap*: the distance between neighbouring hosts' border boxes at 1440 × 900 (Now to
    Places, Places to Today, the search to Places, Now to the Photograph ornament). Part one
    recorded a derivation of 63.2 px laid out as 64, and part two a gap of 64 px; read now, all
    four gaps are **63 px** in both schemes on both tiers. The page's own derivation, evaluated in
    the page, gives a widest single-member padding of 62.44 px (the Today window, nominal policy,
    either scheme), whose ceiling is 63; why it moved from 63.2 was not traced in this wave.

Commands after the last change: `pnpm --filter demo lint` exit 0 (eslint and both `tsc`
projects); `pnpm --filter demo build` exit 0 (the existing chunk-size warning only);
`pnpm --filter demo test:e2e e2e/gallery.spec.ts` 16 passed, the start page's two among them.
