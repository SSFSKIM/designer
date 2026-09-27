---
name: materialist
description: Invoke whenever a UI uses or asks for Liquid Glass, glassmorphism, glass or translucent floating controls, an Apple-, macOS- or visionOS-like material, or the vitrea library (@vitreajs/*), whether designing, building or reviewing such an interface. Not for developing the vitrea runtime, its renderer or its calibration harness themselves.
version: 1.1.0
---

# The Materialist

An aesthetic guideline for designing with Liquid Glass, and with vitrea, its web implementation. It
is a decision function and its laws rather than a style sheet, written for an agent that already
knows how to build interfaces and needs to know what this material is, what register it belongs to,
and how to think when a brief has no rule for it. Read it once, end to end, before the first
surface is drawn; consult it mid-build as one voice. It stands on its own: nothing here assumes the
designer skill, its sampler or its `DESIGN.md`. When that skill is also loaded, it routes here the
moment a page's material model resolves to glass over planes, and this file governs the material and
the floating layer while the designer skill governs the rest of the page.

## 1. What the material is

Liquid Glass bends and shapes light, deferring to the content beneath it (WWDC25 219): a lens,
not a blur preset. A surface has a thickness; its edge refracts what is
behind it inward, more on a wider surface and less on a narrower one; its body takes the tone and,
on the GPU tier, the hue of its backdrop, so over a photograph it reads as the picture seen through
glass and over dark content it stays present, its level following the backdrop's; its rim catches
light; it casts a soft shadow onto the plane outside it whose blur and depth grow with the surface's
own size; it thins to clarity when small and thickens to protect legibility when large; when its
window loses focus it recedes, and when it is pressed it lights from the point of contact and
compresses a little on a spring. Those sentences are measurements of Apple's material on a Mac,
fitted into vitrea as laws, wherever `references/optics.md` says so, and that file names the two
that are designed rather than measured: the tint's appearance and the motion's timing.

Apple's first reading is a controls material: "Liquid Glass forms a distinct functional layer for
controls and navigation elements — like tab bars and sidebars — that floats above the content
layer, establishing a clear visual hierarchy between functional elements and content", and
"Don't use Liquid Glass in the content layer" (HIG Materials). The **instrument register** takes that literally: opaque content, full-bleed,
and a small, load-bearing set of glass controls above it. The two-layer law is Apple's rule for the
platforms it governs, not a universal prohibition.

Apple's other reading is the visionOS window, "a canvas for your contained UI" (WWDC23 10076).
Its glass "limits the range of background color information so a window can continue to provide
contrast" (HIG Materials, visionOS). Lists, collections, text and imagery really sit on that
canvas; controls hang at its edge as ornaments, rather than crowding its contents (WWDC24 10086;
HIG Ornaments). The **spatial register** takes that composition, not a licence to glass every card.
The two materials are not interchangeable: vitrea measures macOS glass, not visionOS glass.

## 2. The register

**Optical skeuomorphism.** A physical glass instrument, not a painted likeness: the lens bends the
content, the body takes its tone and hue, the shadow removes light from the plane. Precision is
curvature — capsule housings, concentric children, a generous fixed window corner — and one
thickness across a family. The user's curvature ruling (2026-09-10) is law: stronger curvature,
with padding and inner geometry moving together, read better. Glass is the only depicted material;
no leather, bevel, faux paper grain or painted light competes with what it actually computes.

**Two readings of refined futurism.** The instrument register is an instrument over a world: the
content fills the screen and a few quiet, monochrome controls act on it. The spatial register is
the world seen through glass: a few substantial windows are the interface and the world is their
environment. Their content is held together by the canvas; their controls stay attached to it,
not arbitrarily afloat. In both, daylight remains the distinctive case, not black chosen because
glass is easy there; derive the light from the product's own scene.

**Where identity lives.** Deference can become Gruber's "see-through blandness". In the instrument
register, identity lives in the content plane, the type, motion quality and one accent; in the
spatial register, in the environment, the type and the window geometry. Louder glass solves neither.
A generic glass page has an underdesigned world, not an underdesigned material.

**Physical motion.** Glass objects "materialize in and out" (WWDC25 219), morph, light from the
point of contact and compress on a spring; it has no
idle motion. The more frequent an interaction, the less emphasis it gets. A changing environment
is content, never animation commissioned to show off a lens.

**Honesty is part of the aesthetic.** The runtime reports what drew. CSS, the receded pose and the
accessibility states are complete designs, not apologies. In the spatial register the web draws
Apple's macOS material composed in Apple's visionOS way: Apple-shaped at window scale, not a
measured replica of visionOS. The distinction belongs in the record beside the tier that drew.

If a decision is ever ambiguous, choose the option that makes the glass more like glass and the page
less like a page wearing it.

## 3. The decision function

At every choice, in order:

0. **Which register?** The instrument register when the screen's content is the world (media, a
   map, a document, a canvas, a worksheet) and a person acts on it with a few controls; the spatial
   register when the product's surfaces are the interface and the world is their environment: a
   launcher or start surface, a glance surface, a guide or label beside the thing it describes, a
   display, an ambient or spatial product. Default to instrument; name and justify spatial in the
   record before the first host. Many glass tiles are not a register choice: they fail the window
   count. In spatial, use the ten conditions below in place of step 1; steps 2–5 govern both.
1. **Control or content, in the instrument register?** Only navigation, actions and transient
   platters are glass. A card, row, list, table, hero or panel of content stays opaque, whatever a
   brief calls it.
   A platter holds choices and actions; a collection or table read in place is content even inside
   a dialog. Floating is a placement, not a material: a content panel may float over the plane,
   opaque, while the controls that act on it and the menus they open are glass.
2. **What is under it, and does it have structure to bend?** Name the live plane or environment.
   If a plane the page chose is a flat field beneath the glass, the material has no job and the
   honest answer is a different surface model; content shown as it is may go flat in some
   phases without changing that answer (§4, the live plane).
3. **Could a sheet of glass do this?** Bend, tone, shadow, glow, morph, recede: yes. A border, a fill,
   a fade, a colour swap on hover, a glow with no light source, a shadow with no caster: no.
4. **Does it flow from where it was?** A menu emerges from its control, a sheet from its source, a
   toolbar morphs into its next state. Two glass surfaces never cross-fade.
5. **Can it be read at the worst phase of its backdrop**, in both colour schemes, with transparency
   reduced, and with the glass removed altogether?

If those do not resolve it: fewer surfaces, larger, calmer.

## 4. Laws

Unless marked instrument, these govern both registers; spatial differences are gathered below.

### The two layers and the floating inventory

The instrument register.

- Every glass surface is a control, a piece of navigation or a transient platter. The count of glass
  surfaces on a screen is small and each is load-bearing; write the inventory as a list short enough
  to read aloud before any markup exists.
- Glass never sits on glass. The material goes on the control, never on the control and its
  container, never on a control's inner views. A toolbar is not a surface: the platter you see is its
  members' fields merging. Anything that must sit on glass uses a fill, transparency or vibrancy.
- One sanctioned exception runs the other way: a control that lives in content, a slider knob or a
  switch, may lift into glass for the duration of an interaction. vitrea's layer model refuses nested
  glass in both directions, so on the web that lift is a fill today, and the record says so. The
  record is the set of lines `references/examples.md`'s template names, written in `DESIGN.md` if the
  project keeps one and in the page's own header otherwise; every "the record says" below means it.
- Everything not on the inventory declares its own surface model underneath and follows it, so the
  page is a layered system rather than a blend: glass over a photograph, glass over a printed sheet,
  glass over a tonal workspace. The layer beneath is decided by the product, not by the material.

### The live plane

The instrument register.

- The backdrop is designed, not inherited. The lens needs both spatial frequencies: something broad
  to bend and something fine to displace, and the fine part painted into the plane, because a grid,
  grain or gradient laid over the plane in CSS is not behind the glass and will not be refracted.
- Where the plane is real content, a photograph, a map, footage, artwork, the page usually chooses
  it: choose, crop or reframe it so every surface sits over its varied region rather than its empty
  corner at every phase the content passes through. Content the page must show as it is, a
  photographer's frame or a reader's document, may go locally flat in some phases. Keep the control
  where the task needs it and let its edge and shadow carry it there; never alter the content or move
  the controls per frame for the glass's sake, and record those phases.
- Prefer a texture plane where the content is an image, a canvas or a video: that is the path where
  the lens is real and the runtime reads the backdrop's pixels itself. A declared tone and luminance
  overrides that reading on either tier, and on the DOM path it is the only statement there is. The
  runtime trusts it, and a false one measurably breaks label contrast, so it describes the plane as
  displayed under the group's actual boxes at every phase, transitions and layout changes included;
  a value measured once is false on a plane that changes. `references/vitrea.md` §2 says when a
  texture group needs one.
- Content reaches the window's edges and the controls float over it. A bar sitting beside its
  content in its own band of background is an ordinary page wearing the material, and the most
  visible way a glass page fails.
- The plane is fixed to the viewport. A layout where floating chrome and scrolling content share a
  scroll container will scroll its own glass out from under itself.

### Groups

- A sampling group is one backdrop read, one variant and one tint seed shared by its members, and it
  is a composition unit: what shares a group reads as one body of material. Group by function and
  frequency, at most three groups in a bar, and never a text button and an icon button in one group,
  which reads as one combined control.
- Two surfaces in one group merge or stay separate by their spacing, so decide per pair and space
  them to say so. Two groups need at least the larger group's sampling padding between them, a
  distance the runtime derives from the blur it actually drew and that rises under Reduce
  Transparency; never pin it, and let the layout give it room.
- Surfaces within one plane never overlap. Overlap across planes is the supported case and is how a
  morph works.

### Geometry and the size family

- Every rounded shape is one of three kinds: fixed, a constant radius; capsule, half the shorter
  side as the box measures it, which padding, borders and intrinsic sizing all move; concentric, the
  container's radius minus the gap, so the two arcs share a centre and the radius correctly falls
  toward zero as the element moves away from the corner. Pinched or flared corners on a nested
  element are the failure signal, and no measurement is needed to see them.
- Prefer capsules for single-row floating housings, search fields, segmented housings and standalone
  floating buttons; keep compact inner controls concentric with their housing; give multi-row
  platters, sidebars and sheets a generous rounded rectangle so the corners keep usable space.
  Shape, padding and nested radii move together.
- Name the concentric anchor. Apple's is the window corner; a web page's is whatever the design
  draws as its outer frame, the viewport edge or the plane's own rounded container, and a page that
  has not named one has no concentricity to derive.
- Choose a size family, not sizes per component: a small set of spans, one radius per span, one
  thickness across all of them. In the instrument register the family straddles 32 to 96 CSS px
  so the material's size behaviour exists on the page; spatial windows use the thick end below.
  Below 32 the law is inert: a thin sheet, correct for a tiny toggle and wrong for a housing.
- Thickness is 8 unless the product gives a reason, and it is one number across the family.

### Colour

- Glass has no colour of its own; it takes colour from what is behind it. The control layer is
  monochrome by default, and saturated colour lives in the content plane, which on a glass page is
  where the colour already is.
- Tint is rationed: at most one tinted control per view, it is the primary action or a status, the
  tint sits on the control's background and never on its label, and it is a seed the material
  tone-maps against the backdrop rather than a fill. A solid background on a glass host is opaque and
  stops being the material. One seed per group; a second hue steps out into its own group.
- Label colour must not approach the content passing behind it. Where the plane carries the product's
  colour, the control layer's one accent is chosen to stand apart from it, or withheld: spending the
  tint budget by not spending it is a legitimate derivation.
- The light and dark materials are separate measurements, not one dimmed. Choose the scheme from the
  product's scene and let it follow the system where the page does; a group's backdrop hint is a
  different statement from the scheme and can honestly disagree with it.

### Type and content on glass

- Legibility comes before translucency. The one charge every serious critic of the material agreed
  on is that anything placed over something else is harder to read, and a page answers it by
  composition rather than by opacity: regular glass wherever text sits, text kept off small surfaces
  over busy planes, and the opaque version of the page designed first so the material is laid over a
  page that already works.
- In the instrument register a surface carries one short line or a control's own label; explanatory
  prose lives on the plane. In both, state and hierarchy come from layout, type and colour, not sheen.
- Ink on glass is vibrant and automatic: the runtime publishes four label levels against the material
  it is actually drawing, and the primary is the one to use for labels. It is a pick between two poles,
  not a contrast calculation, so contrast is measured on rendered pixels across the backdrop's phases
  at 4.5:1 for labels and 3:1 for large text and controls, in both schemes. A page that needs a
  guaranteed ratio sets its own ink on a child element.
- Prefer regular through bold weights and avoid light ones; a symbol over a word in a bar where a
  recognisable symbol exists, and a word where none does. The platform's own UI face on a page that
  is a client of that platform.
- App-authored content inside a plane declares its own `color-scheme`, so the runtime's ink resolves
  against the plane's ground rather than the reader's system preference.

### Motion

- Glass appears and disappears by materialising, never by fading opacity. Between states it morphs,
  so the floating plane stays one plane; a menu, a popover, a sheet emerges from the control that
  summoned it, in place; a cross-fade between two glass surfaces is wrong in every case.
- Press feedback is light and compression: a glow from the pointer spreading through the element, a
  scale of about one to two per cent on a spring, a bounce on release. Never a colour swap.
- The glass has no idle motion. No shimmer at rest, no drifting backdrop for its own sake, no
  animated blur. The plane may change when its content changes; that is a state, not decoration.
- Springs are slightly underdamped for geometry and press, critically damped for optical strength,
  and interruptible: a release mid-press redirects without a snap. Start without bounce; reserve
  overshoot for momentum and keep frequent click feedback restrained. Under Reduce Motion the
  elastic behaviour is removed outright, so no layout depends on it.
- Motion is rationed by frequency: the interactions a person performs all day carry the least of it,
  and a page adds no motion of its own on top of the runtime's press, morph and materialise. Apple
  also scales emphasis by input, more under direct touch and subdued under a pointer; the runtime's
  response is the same under both today, which is a recorded gap rather than a page's decision.

### Poses, schemes and variants

- The receded pose is a state of the design: when the window loses focus the body darkens, the rim
  collapses, a tint keeps its shade and loses its chroma, and the exterior shadow stops. Leave the
  runtime following the window and look at the page unfocused. Never hand-animate a recede.
- The dark scheme is a second material to design and measure, not a free variant. Over a bright
  plane expect its ink to fall short of the floor, and decide up front between grading the plane for
  that scheme and authoring the label ink on a child, then measure both schemes before calling the
  page done. Pinning the scheme to dodge the failure is not an answer.
- Two variants exist and are never mixed on one page: regular, which adapts to protect legibility and
  is the answer wherever a surface carries text; and clear, only over media-rich content whose
  content layer a dimming layer will not harm, with bold bright content on the glass, and then with
  that dimming layer.

### Accessibility and the fallback

- Reduce Transparency, Increase Contrast, Reduce Motion and forced colours modify the material
  itself, and the page is designed with all four open: frostier and more occluding, stronger borders
  and near-monochrome, no elastic motion, and no glass at all. The runtime follows the system's
  preferences by default; the one it cannot query on every engine is Reduce Transparency, and where an
  engine cannot answer it the runtime warns and resolves the preference false. A page honours it there
  by offering the setting itself and passing a boolean from it, or from a stored preference, so that
  zero diagnostics means the engine answered or the app did.
- The runtime's resolved policy covers the material, not what the page authored. Look at every
  authored fill, track, switch and selection marker, a segmented control's indicator included, after
  forced-colour substitution: a border or mark in system colours survives, a gradient or a
  translucent fill does not. Motion the page owns follows Reduce Motion as it changes, not as it read
  at mount.
- The CSS tier is the same material without refraction, and it is a complete design. Compose so that
  hierarchy is carried by layout, grouping and type; then removing the material removes an effect and
  never the structure. Look at the CSS tier once, on purpose.
- Labels stay real DOM. A glass button is a `<button>`, focusable, IME-capable, announced as one, with
  the material painted around it. Content portalled into a plane leaves its landmark behind, and
  re-establishing one is a design decision about how the overlay is announced.

### Layout under floating chrome

The instrument register.

- Content clears the floating bars by an inset derived from the bar's measured size and recomputed
  when it changes, never a constant typed once; at rest, first paint, the top of a scroll, content
  does not sit under a glass control at all, and the intersection happens only while scrolling.
  Content here is what the reader reads; the live plane is what the controls float over by design.
- Where content scrolls under a floating control the transition is a scroll edge, a gradient mask on
  the scrolling content's own edge, one per scrolling view, never a darkening scrim under the bar and
  never present where nothing floats. Put it on the scroll container, never on an ancestor of the
  glass root: a mask, filter, opacity or clip on an ancestor re-roots the backdrop and demotes the
  material.
- Decide which composition the scroll edge makes: a band of the plane kept clear under the bar by
  masking the content before it arrives, or the content itself becoming the bar's backdrop as it
  passes under. Either way a surface straddling the clear band, the gradient and the content has the
  visible composite behind it, and its declared backdrop says so.
- No glass bar, sheet or popover takes a custom background, border or darkening layer of its own;
  an opaque content panel that floats is content and keeps its own fill.

### The spatial register

Two forms, not a glass-card template: a **window** holds an app's content on one canvas, with
ornaments at its edge; a **glance module** holds one information unit — headlines, figures or
graphs, not prose — with a bright foreground (WWDC23 10076; WWDC25 255; HIG Widgets).

1. **Design the environment.** One product-owned, full-bleed, viewport-fixed texture plane:
   photograph, footage, artwork or a painted scene. visionOS glass limits background information;
   vitrea's macOS material does not make that promise, so grade the environment until every drawn
   window or module body stays outside the published-ink dead band, roughly encoded 0.39–0.49.
   That is the SURFACE level, not the source's average or the group's tone input. Keep the area
   behind text calmer than the rim; a passing average cannot rescue a failing line (HIG Materials;
   NN/g, Glassmorphism). Active texture groups use the WHOLE source's average unless a hint
   overrides it: a window on part of a graded plane declares the level measured under its own
   boxes, on a cadence (§2 of the cookbook). Only the rendered level behind each line gates
   contrast, not that input. A live environment changes for the product, never for the glass.
2. **Few windows, thick and fitted.** One to three windows or modules at rest, each a real task
   unit, with the environment visible around every one. Span 96 or above for windows and modules
   reaches the material's saturated size law; ornament labels answer to contrast, not that span
   floor. Use one thickness, 8 or up to 14 with the reason recorded, generous fixed radii and the
   window corner as concentric anchor. Minimise unused glass, not the world around it (WWDC23
   10072; HIG Windows; the size law in `references/optics.md`).
3. **Compose content for glass.** Use primary ink for standard text and controls, secondary for
   descriptions; tertiary and quaternary are for decoration and rules only, never readable metadata.
   Put the tokens on children, medium body through bold titles with slightly opened tracking;
   measure body text per rendered line at 4.5:1 across phases, schemes and poses, the worst line
   gating and every failing line recorded. Author ink on a child when a ratio needs guaranteeing.
   Apple's predominantly white spatial type is precedent, not a reason to override vitrea's
   published polarity (WWDC23 10076; HIG Typography). Lists, collections and sections belong in
   windows; long prose gets its own. Glance modules keep foreground information bright, with text
   at least 11 CSS px as this skill's web floor (HIG Widgets says 11 points); full-colour imagery
   is media smaller than the module. Window images and video are opaque in concentric frames.
4. **Fills inside, ornaments outside.** Darker child fills separate sections and inputs; lighter
   child fills lift interactive or selected elements, never light on light (WWDC23 10076). No
   nested glass host. A control needing material becomes an ornament: few, no wider than the
   window, plain buttons on its glass, attached at an edge in its own overlay-plane group (HIG
   Ornaments). On the texture path place it OUTSIDE the edge by the runtime-derived group gap:
   its source is the environment, not the window's rendered glass. Only the DOM path can sample
   the composite for a cross-plane overlap; the hosts still cannot nest in DOM.
5. **Spend colour where it survives.** Windows and modules are untinted; the environment supplies
   their colour, with hue retained on the GPU tier. Accents go in bold text, an entire button or
   a child fill, not light type or a thin mark. At most one tinted glass control, in an ornament;
   imagery keeps its colour instead of turning the window into an opaque brand panel (HIG Color;
   WWDC23 10076; WWDC24 10086).
6. **One source of depth.** The material's shadow onto the environment is the page's elevation.
   Windows never overlap within a plane; sheets and popovers morph from their control into the
   overlay plane. Large shadows are extrapolated, not another authored elevation token.
7. **Scroll within the canvas.** The window host stays still; a child scroller clips and carries
   scroll edges at the window's inner edges. Ornaments stay attached while content scrolls (HIG
   Ornaments). A mask on that child is not a mask on the glass host or an ancestor of the root.
8. **Regular for reading.** Windows and modules use regular (HIG Materials). Clear is only for
   media being watched, whose dimming does not harm it, with bold bright foregrounds (WWDC25 219).
   Its required policy draws no scrim: paint dimming into the plane under the footprint, not on
   the host. HIG Materials suggests dark at 35% for bright content; the `Glass.clear` API example
   uses black at 30%. Neither is vitrea calibration; record clear and its page-painted layer as
   uncalibrated, and never mix variants on the page.
9. **Let the material yield.** A modal task darkens the plane below it (WWDC25 356); Reduce
   Transparency frosts windows, Increase Contrast strengthens their edges, and forced colours
   makes Canvas panels with CanvasText borders whose authored fills must survive substitution.
   The CSS root sums present CSS host width × height × dpr² and collapses its two-layer body
   above 400,000 device pixels, not at a fixed window size: read `cssBody`, record it and inspect
   both forms. The fallback is still the window, not an excuse to lose its content (HIG
   accessibility; `references/optics.md`).
10. **No added motion.** Windows materialise and morph; ornaments press as light and compression.
    Nothing moves at idle. Content changing in a live environment is not the glass moving.

The Dynamic Island's opaque backing is not a glass-surface precedent (HIG Live Activities).
Liquid Glass clock numerals are display type, not permission for prose on a thin sheet (Apple's
2025 design announcement). Neither analogy exempts a window from these conditions.

### The macOS reading

Platform conventions are reference, not web law: search at a toolbar's trailing edge or a sidebar's
top; tabs for navigation, not actions; automatic scroll edges; controls nesting into window corners;
macOS 27 menu icons only for key actions. Adopt what fits and record what does not. Window-control
clearance and title-bar dragging have no web equivalent. macOS 27's edge-to-edge sidebars, unified
toolbars and tighter corners concede that dense pointer-driven work wants more structure and opacity;
take that as a quieter instrument over an opaque worksheet, not accidental spatial composition.

## 5. The home system

The material's defaults are the home system, and most of them are the runtime's rather than yours.
Derive the register, its world and surfaces, the size family, anchor, scheme and tint budget.

| decision | home default | derived per product |
|---|---|---|
| register | instrument | spatial when the surfaces are the interface and the world their environment |
| renderer | request the GPU tier; the CSS tier is the same design | the tier a deliverable can host |
| material | macOS 27, the runtime's default document | pin macOS 26.5 only to hold an earlier look |
| colour scheme | follow the system where the page does | the scene the product is used in |
| window pose | follows the document's focus | never pinned outside a preview or a capture |
| size family | instrument spans straddle 32 to 96; spatial windows/modules ≥96; one thickness of 8 | the task's spans; spatial thickness up to 14 with a reason |
| curvature | capsule housings and buttons; concentric children; generous rounded platters | the anchor the page names |
| groups | one per bar partition; texture plane where the content is media | the inventory |
| tint | none | one seed on the primary action or a status, or withheld |
| ink | the runtime's primary label token on a child element | an app ink where a ratio is guaranteed |
| accessibility | the runtime follows the system; a boolean from the app's own setting where Reduce Transparency cannot be queried | pinned only for a capture |
| motion | the runtime's springs; no idle motion | nothing, unless measured |

## 6. Derivation

- **Which register?** Name what the person acts on: the world through an instrument, or content
  gathered on windows within an environment. A launcher is not a worksheet with transparent cards.
- **The environment, for spatial.** Design where each window looks through before designing its
  content; grade for the drawn body and worst text line, not a photograph's overall average.
- **Is instrument glass earned?** It is earned when controls genuinely sit over a plane that changes
  beneath them and the transparency preserves context: a media player over artwork, controls over a
  map or a canvas, a floating bar over a full-bleed photograph, an inspector over a document, a
  transient platter. It is not earned over flat grey chrome, dense tables, forms or dashboards, and it
  is never earned because a card can be made translucent. A brief that names glass for a product with
  no live plane gets the smallest honest version, one control layer over the least flat surface the
  product has, with the tension recorded in a line.
- **Design the opaque page first.** Lay the page out as if no material existed, with its hierarchy
  carried by layout, grouping and type; then let glass find the chosen register's surfaces.
  Accessibility and fallback must preserve that hierarchy without translucency.
- **Dense or consequential work** confines the glass to a small persistent control layer while the
  primary task surfaces stay opaque; the material is for the instrument, not the worksheet.
- **A light plane** is the harder and more distinctive case and the default to try first; a dark
  plane is chosen when the product's scene is dark, never because glass is easier there.
- **Spend the tint** when one action must be found before anything else is read and no colour in the
  plane competes with it; withhold it when the plane already carries the product's colour or when a
  status hue would change with the content.
- **Reach for clear** only when all three of Apple's conditions hold at once, and then design the
  dimming layer as part of the plane.
- **On touch**, capsules and larger targets; on a dense desktop, compact inner controls may stay
  rounded rectangles inside a capsule housing.
- **Without vitrea**, the aesthetic still applies with one `backdrop-filter`, one `rgba()` layer, a
  shadow whose blur follows the surface's span, capsule and concentric geometry and no refraction;
  `references/vitrea.md` gives the path, and the record says which path the page took.

## 7. Ban list

- In the instrument register, no glass on a card, row, list, table, content panel or hero.
- No nested glass hosts; no border, background, shadow or blur authored on a glass host.
- No two variants on one page; no clear glass over bright content without its dimming layer.
- No second tint hue in a group; no tint on a label; no solid fill standing in for a tint; no
  hand-rolled blur standing in for the material.
- No glass over a flat, uniform field the page chose; content shown as it is that goes flat in some
  phases is recorded, not a ban.
- No cross-fade between glass surfaces, no fade-in by opacity, no idle motion, no colour-swap press
  state.
- No depicted material anywhere else on the page: no brushed metal, leather, bevel, faux grain or
  painted highlight.
- No dishonest backdrop declaration, no pinned sampling padding, no fixed pixel offset standing in
  for a bar inset.
- No instrument prose on glass; no spatial prose on a thin sheet or in a glance module.
- No tile field instead of one to three spatial windows/modules; no tinted window, light-on-light
  inner fills, or texture-path ornament straddling a window.
- No window body in the published-ink dead band, no sub-96 window/module, and no claim that the
  Dynamic Island or glass clock licenses either.

### Mechanical subset

```
no backdrop-filter, box-shadow, border or background authored on any element the runtime registers
  (the one allowed background is the user-agent reset on a native button: transparent, appearance none)
no element registered as glass carries a list, listitem, row, table or article role
no two distinct tint hues resolve inside one sampling group
no opacity transition or animation targets a glass host or any ancestor of the glass root
no filter, backdrop-filter, opacity < 1, mask-image, clip-path or mix-blend-mode on any ancestor of the glass root
every registered surface's shorter span is at or above 32 unless it is a control the family deliberately sizes smaller
in the spatial register every window or module host is at or above span 96
dev-mode diagnostics: zero
```

## 8. QA lens

Checks 1, 3, 10, 13 and 15 govern instrument; spatial replaces them with 21–28. The other checks
govern both: check 2 refuses nested hosts (a DOM-sampled cross-plane overlap is not nesting), and
check 12 includes spatial body text. Answer in both colour schemes, with transparency reduced, on
the CSS tier and unfocused. An `[environment]`, `[layer]` or `[material]` failure means the page is
not this register; other misses remain recorded failures, never passes with residuals.

1. `[layer]` Every glass surface is navigation, an action or a transient platter; no content surface
   uses glass, and no platter holds a collection read in place.
2. `[layer]` No glass host nests inside another; inner elements use fills, transparency or vibrancy.
3. `[layer]` The floating inventory is short and each entry is load-bearing.
4. `[material]` One variant across the page; clear only over media with its dimming layer.
5. `[material]` At most one tinted control per view, the primary action or a status, tinted on its
   background; no solid fill and no hand-rolled blur anywhere in its place.
6. `[material]` No glass over a flat, uniform field; every surface sits over structure at every phase
   of a plane the page chose, and where content shown as it is goes flat the record lists the phases.
7. `[material]` No depicted material anywhere else on the page.
8. `[geometry]` Every rounded shape is fixed, capsule or concentric; nested radii derive from their
   container and no corner reads pinched or flared; the concentric anchor is named.
9. `[geometry]` Single-row floating housings and buttons are capsules, radius half the span the box
   measures; inner controls are concentric with their housing; platters keep a generous rounded
   rectangle.
10. `[geometry]` The size family straddles 32 to 96 with one radius per span and one thickness.
11. `[grouping]` Related items share one group, unrelated ones do not, at most three groups per bar,
    no text button beside an icon button in one group, groups spaced past the runtime's padding.
12. `[legibility]` Label contrast measured on rendered pixels across the plane's phases: 4.5:1 for
    labels, 3:1 for large text and plates, both schemes. The record keeps every reading, per text
    line and icon, per scheme, at rest, scrolled and in the receded pose; one under the floor is a
    recorded failure, never a pass with a residual.
13. `[legibility]` At rest, reading content does not sit under a glass control; a scroll edge sits
    wherever content passes under one and nowhere else.
14. `[legibility]` The page works with transparency reduced, contrast increased, motion reduced and
    under forced colours, judged on its authored marks after substitution rather than on the resolved
    policy; page-owned motion follows Reduce Motion as it changes; the receded pose is a designed
    state.
15. `[layout]` Content reaches the window's edges and clears the floating bars by a measured inset;
    the plane is viewport-fixed and never scrolls its glass out from under itself.
16. `[layout]` No glass host carries a custom background, border or scrim; clear and modal
    dimming belongs to the plane below it.
17. `[motion]` Glass materialises and morphs; menus and sheets emerge from their control; press is
    glow and flex at the pointer; nothing moves at idle.
18. `[colour]` The control layer is monochrome by default; saturated colour is the plane's; no label
    colour approaches the content behind it.
19. `[honesty]` Every declared backdrop describes the displayed composite under its group's actual
    boxes at every phase, transitions and layout changes included; the runtime's resolved state is
    read, not assumed; dev-mode diagnostics are zero (`references/vitrea.md` §1 names the one
    page-scoped exception).
20. `[eye]` The page's capture sits beside a native capture of the nearest Apple surface, and the
    difference the eye sees that the checks did not is written down. Where no native capture is
    available, the record names the nearest Apple surface and says that no comparison was made.

21. `[environment]` The product's fixed, full-bleed environment remains visible around each window
    or module;
    its grading keeps every drawn body outside the ink dead band and every text line readable,
    with source average, declared tone and rendered level recorded separately.
22. `[layer]` One to three windows/modules at rest, each a task unit; every window/module ≥96 span,
    with a shared thickness and fixed concentric anchor; ornament labels pass contrast independently.
23. `[legibility]` Window/module text uses the semantic ink ladder on children, medium or heavier; every
    body line passes 4.5:1 across captured phases, both schemes, scrolled and receded; modules carry
    bright glance content rather than prose; tertiary/quaternary are only rules and decoration.
24. `[layer]` Internal hierarchy is darker separating/input fills and lighter interactive/selected
    fills, not nested glass or light-on-light stacks; ornaments have their own overlay group and
    sit outside the window on the texture path, at the derived gap.
25. `[layout]` The host is still, its child scrolls with inner scroll edges and opaque media in
    concentric frames, ornaments stay attached, and no windows overlap within a plane.
26. `[colour]` Windows/modules are untinted; colour stays in the environment, imagery, bold text,
    entire buttons or role-bearing fills, with at most one tinted ornament control.
27. `[material]` Reading surfaces use regular; any clear surface meets all three media conditions
    with page-painted dimming, not just a policy; modal dimming is likewise below the host.
28. `[material]` The record names the actual CSS `cssBody` at the captured DPR and area; both CSS
    forms and the forced-colours Canvas panel preserve content and authored marks; window-scale
    optics and any clear use are stated as uncalibrated beyond the named bed, not visionOS fidelity.

## 9. Reference routing

| reference | read it for |
|---|---|
| `references/optics.md` | the measured physical model: the lens, the size law, the body's two components, tone and hue, the rim, the exterior shadow, poses, schemes, variants, tint, ink, accessibility states, motion character, the two tiers, window-scale extrapolation, the ink dead band and named gaps |
| `references/vitrea.md` | the cookbook: each decision above mapped to the 0.24.0 API on the React and vanilla paths, windows, modules and ornaments on both paths; what the runtime does not catch; CSS-only and CDN status |
| `references/examples.md` | six instrument derivations, spatial derivations as their pages land, and the register-aware record template |

## 10. Provenance

The second register: `docs/research/2026-09-27-glass-as-surface-prior-art.md`, especially §§1–4 and
8 (WWDC23 10072/10076, WWDC24 10086, WWDC25 255; HIG Materials, Windows, Ornaments, Typography,
Color and Widgets), with its web conditions checked against the runtime. visionOS is precedent,
not a measured material in this harness; authoring choices and source limits are in the distillation.

Apple's own guidance, read and quoted in `docs/research/2026-09-10-liquid-glass-design-language.md`
(the HIG's Materials, Toolbars, Layout, Color, Typography and Accessibility pages; the Adopting
Liquid Glass and ConcentricRectangle articles; WWDC25 sessions 219, 356, 323, 284 and 220), with the
practitioner critique it collects marked as secondary. The aesthetic articulation, the lineage Apple
states for the material, the macOS 27 refinements, the spring discipline and the critical reception
through September 2026, in `docs/research/2026-09-26-liquid-glass-aesthetic-prior-art.md`. The
material's physics from the fidelity ledger `docs/doperpowers/specs/c9a-fidelity-claims.md`, section
by section as `references/optics.md` cites them. Two recorded taste rulings: daylight as the
distinctive register (`apps/demo/DESIGN.md` §0, 2026-09-03) and active curvature
(`2026-09-10-liquid-glass-into-the-skill.md`, Decision Log). The distillation record, law by law, is
`docs/research/materialist-distillation.md`. Distilled 2026-09-26.
