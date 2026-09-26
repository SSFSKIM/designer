---
name: materialist
description: Invoke whenever a UI uses or asks for Liquid Glass, glassmorphism, glass or translucent floating controls, an Apple-, macOS- or visionOS-like material, or the vitrea library (@vitreajs/*), whether designing, building or reviewing such an interface. Not for developing the vitrea runtime, its renderer or its calibration harness themselves.
version: 1.0.0
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

Apple introduced it as "a new digital meta-material that dynamically bends and shapes light",
said that "the primary way Liquid Glass visually defines itself is through something called
lensing", and gave it one goal: "to remain visually clear, deferring to the content underneath"
(WWDC25 219). So: a lens, not a blur preset. A surface has a thickness; its edge refracts what is
behind it inward, more on a wider surface and less on a narrower one; its body takes the tone and,
on the GPU tier, the hue of its backdrop, so over a photograph it reads as the picture seen through
glass and over dark content it stays present, its level following the backdrop's; its rim catches
light; it casts a soft shadow onto the plane outside it whose blur and depth grow with the surface's
own size; it thins to clarity when small and thickens to protect legibility when large; when its
window loses focus it recedes, and when it is pressed it lights from the point of contact and
compresses a little on a spring. Those sentences are measurements of Apple's material on a Mac,
fitted into vitrea as laws, wherever `references/optics.md` says so, and that file names the two
that are designed rather than measured: the tint's appearance and the motion's timing.

It is also a controls material. Apple's own statement of it is a layer model before it is a look:
"Liquid Glass forms a distinct functional layer for controls and navigation elements that floats
above the content layer, establishing a clear visual hierarchy between functional elements and
content", and, in the imperative, "Don't use Liquid Glass in the content layer." Nearly everything
below follows from taking that seriously. A screen has exactly two planes: content, opaque, filling
the window and reaching its edges; and a small, load-bearing set of controls floating above it on
glass. The material's whole job is to separate what you can act on from what you are reading, and
glass on both sides of that line collapses the distinction it exists to draw.

## 2. The register

The brief this skill was written to (2026-09-26) names the aesthetic as refined futurism with
skeuomorphism at its finest: as if a person were operating a physical glass instrument held over the
page. That is a precise description once each word is pinned.

**Skeuomorphism, optical rather than ornamental.** The skeuomorphism of the early 2010s failed
because it depicted: linen, leather, bevels and drop shadows drawn onto flat pixels that did
nothing. This material depicts nothing. It behaves. The lens really bends the content beneath it,
the body really takes the backdrop's tone, the shadow really removes light from the plane, so the
metaphor is not painted on but computed, and it passes the honesty test that the earlier kind
failed. Practitioners reached for the same words when it shipped: "we've come back, in a sense, to
skeuomorphic interfaces, but this time not with a lacquer resembling a material" (Sebastiaan de
With); "where glassmorphism blurs the background, liquid glass bends it", and "depth always comes
back, but only the honest versions stay" (Roman Kamushken). The consequence is a boundary: the glass
is the only material on the page that pretends to be a material, and it pretends by behaving. No
brushed metal, no leather, no bevel, no faux paper grain on a panel, no gradient that imitates a
light that is not there. The content plane is real content: a photograph, a map, video, a drawn
field, a document. Ive's line holds here exactly: "designing and
making are inseparable", and a material that is made rather than drawn is the finest form of the
idea.

**Futurism, refined.** The feeling is an instrument over a world. The content plane is the world,
full-bleed, edge to edge, carrying every colour and every picture; the controls are the instrument,
small, monochrome, precise, floating a measured distance above it. Apple's own lineage for it runs
from Aqua through "the realtime blurs of iOS 7" and the fluidity of the iPhone X and the Dynamic
Island to visionOS, and its test is still iOS 7's deference test: is the interface calling attention
to itself, does it compete with the content. The chrome should "support interaction where needed,
and remain unobtrusive when it's not" (WWDC25 356). It is a heads-up display without the neon: the
future here is quiet, light, exact. Which is why daylight is the distinctive register.
Every verified competitor demo is dark, because dark is where the material is easy; a light plane
with a legible control layer is the harder and more distinctive demonstration, and the ground is
still derived from the product's own scene rather than defaulted to black.

**Where the identity lives.** Deference pushed to its limit has a known failure, and the critics
named it within a year: chrome that defers until every app looks alike, "see-through blandness" in
John Gruber's phrase. The answer is never louder glass. A product's identity lives in its plane (the
content it shows and the ground it is drawn on), in its typography, in the quality of its motion and
in one accent; the glass shows those and owns none of them. A glass page that reads as generic has an
underdesigned plane, not an underdesigned material.

**Curvature, used actively.** Precision here is curvature: capsule silhouettes for single-row
floating housings and controls, concentric corners for anything nested, radii derived from the
container rather than typed, one thickness across the family. The ruling recorded when six demo pages
were built on the material (2026-09-10) stands as law: stronger curvature read as much better, with
the padding and inner geometry moving together so the silhouette never crowds its content.

**Motion, physical.** Apple says "the visuals and motion of Liquid Glass were designed as one", and
describes "an inherent gel-like flexibility" that "moves in tandem with your interaction" (WWDC25
219). Nothing cuts and nothing fades. Glass materialises by modulating its own lensing, morphs
between states so the floating plane stays one plane, glows from the touch point, compresses on a
spring and bounces back on release. It has no idle motion at all: every movement answers input, a
state change or the environment, and it is held back where an interaction is frequent, because what
delights on the first press distracts on the twentieth.

**Honesty as part of the aesthetic.** The runtime reports what it drew rather than what was asked
for; the CSS tier is the same material without refraction, and it is a complete design; Reduce
Transparency, Increase Contrast and forced colours are states of the design to open and look at,
not degradations to apologise for. A page that reads as the system with the glass removed is a page
that was composed correctly.

If a decision is ever ambiguous, choose the option that makes the glass more like glass and the page
less like a page wearing it.

## 3. The decision function

At every choice, in order:

1. **Control or content?** Only navigation, actions and transient platters float. A card, a row, a
   list, a table, a hero, a panel of content is content and stays opaque, whatever a brief calls it.
2. **What is under it, and does it have structure to bend?** Name the live plane. If nothing changes
   beneath the controls, or the backdrop is a flat field, the material has no job here and the honest
   answer is a different surface model.
3. **Could a sheet of glass do this?** Bend, tone, shadow, glow, morph, recede: yes. A border, a fill,
   a fade, a colour swap on hover, a glow with no light source, a shadow with no caster: no.
4. **Does it flow from where it was?** A menu emerges from its control, a sheet from its source, a
   toolbar morphs into its next state. Two glass surfaces never cross-fade.
5. **Can it be read at the worst phase of its backdrop**, in both colour schemes, with transparency
   reduced, and with the glass removed altogether?

If the first five do not resolve it: fewer surfaces, larger, calmer.

## 4. Laws

### The two layers and the floating inventory

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

- The backdrop is designed, not inherited. The lens needs both spatial frequencies: something broad
  to bend and something fine to displace, and the fine part painted into the plane, because a grid,
  grain or gradient laid over the plane in CSS is not behind the glass and will not be refracted.
- Where the plane is real content, a photograph, a map, footage, artwork, this is already satisfied;
  check that each surface sits over the plane's varied region rather than its empty corner, and
  check it at every phase the content passes through.
- Prefer a texture plane where the content is an image, a canvas or a video: that is the path where
  the lens is real and the runtime reads the backdrop's pixels itself. On the DOM path the group's
  declared tone and luminance is an assertion the runtime trusts, and a false one measurably breaks
  label contrast; declare the honest value for the range and measure at its worst phase.
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
  side; concentric, the container's radius minus the gap, so the two arcs share a centre and the
  radius correctly falls toward zero as the element moves away from the corner. Pinched or flared
  corners on a nested element are the failure signal, and no measurement is needed to see them.
- Prefer capsules for single-row floating housings, search fields, segmented housings and standalone
  floating buttons; keep compact inner controls concentric with their housing; give multi-row
  platters, sidebars and sheets a generous rounded rectangle so the corners keep usable space.
  Shape, padding and nested radii move together.
- Name the concentric anchor. Apple's is the window corner; a web page's is whatever the design
  draws as its outer frame, the viewport edge or the plane's own rounded container, and a page that
  has not named one has no concentricity to derive.
- Choose a size family, not sizes per component: a small set of spans, one radius per span, one
  thickness across all of them, and the family straddling the size law's band from 32 to 96 CSS px
  so the material's size behaviour exists on the page. Below 32 the law is inert; a control sized
  there is a thin sheet with no depth, which is correct for a tiny toggle and wrong for a housing.
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
- A surface carries at most one short line or a real control's own label. The material never carries
  information: state, hierarchy and affordance are read from layout, type and colour, and the prose
  that explains a control lives on the plane beside it.
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
  and interruptible everywhere: a release mid-press redirects from the current position and velocity
  with no snap. Apple's own spring discipline governs anything added on top: start with no bounce,
  reward a gesture that carries momentum with a little overshoot, and treat the macOS 27 click
  bounce as Apple does, "a little goes a long way". Under Reduce Motion the elastic behaviour is
  removed outright, so no layout depends on it.
- Motion is rationed by frequency: the interactions a person performs all day carry the least of it,
  and a page adds no motion of its own on top of the runtime's press, morph and materialise. Apple
  also scales emphasis by input, more under direct touch and subdued under a pointer; the runtime's
  response is the same under both today, which is a recorded gap rather than a page's decision.

### Poses, schemes and variants

- The receded pose is a state of the design: when the window loses focus the body darkens, the rim
  collapses, a tint keeps its shade and loses its chroma, and the exterior shadow stops. Leave the
  runtime following the window and look at the page unfocused. Never hand-animate a recede.
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
- The CSS tier is the same material without refraction, and it is a complete design. Compose so that
  hierarchy is carried by layout, grouping and type; then removing the material removes an effect and
  never the structure. Look at the CSS tier once, on purpose.
- Labels stay real DOM. A glass button is a `<button>`, focusable, IME-capable, announced as one, with
  the material painted around it. Content portalled into a plane leaves its landmark behind, and
  re-establishing one is a design decision about how the overlay is announced.

### Layout under floating chrome

- Content clears the floating bars by an inset derived from the bar's measured size and recomputed
  when it changes, never a constant typed once; at rest, first paint, the top of a scroll, content
  does not sit under a glass control at all, and the intersection happens only while scrolling.
- Where content scrolls under a floating control the transition is a scroll edge, a gradient mask on
  the scrolling content's own edge, one per scrolling view, never a darkening scrim under the bar and
  never present where nothing floats. Put it on the scroll container, never on an ancestor of the
  glass root: a mask, filter, opacity or clip on an ancestor re-roots the backdrop and demotes the
  material.
- No bar, sheet or popover takes a custom background, border or darkening layer of its own.

### The macOS reading

Apple's platform chrome conventions are a reference for a desktop page rather than law for the web:
search at the toolbar's trailing edge or the top of the sidebar; a tab bar for navigation and never
for actions; the automatic scroll-edge style, which the HIG has preferred since June 2026; controls
nesting into the window's rounded corners; menu icons hidden by default since macOS 27 and shown only
for key actions. Read them when the product is a client of the platform, adopt the ones that fit,
and record the ones that do not. Two macOS behaviours have no web equivalent and are not simulated:
leading toolbar items clearing window controls, and a title bar that doubles as a drag surface.

Read the macOS 27 refinements as a concession worth learning from: after a year of the material,
Apple ran sidebars edge to edge on the Mac, unified the toolbar where content scrolls under it
(content still passes beneath a unified bar; what the live-plane law calls the visible failure is a
bar in its own opaque band with content stopping at its edge), tightened every window's corner radius
and hid the menu icons, while improving the glass's own diffusion and giving the body a darkened edge
with brighter highlights. Dense, pointer-driven,
multi-window work wants more structure and more opacity than a full-screen touch surface; a desktop
web product takes that as licence for a small, quiet control layer over an opaque worksheet, not as a
reason to soften the material's rules.

## 5. The home system

The material's defaults are the home system, and most of them are the runtime's rather than yours.
What a product derives is the live plane, the floating inventory, the size family, the anchor, the
scheme and whether the one tint is spent.

| decision | home default | derived per product |
|---|---|---|
| renderer | request the GPU tier; the CSS tier is the same design | the tier a deliverable can host |
| material | macOS 27, the runtime's default document | pin macOS 26.5 only to hold an earlier look |
| colour scheme | follow the system where the page does | the scene the product is used in |
| window pose | follows the document's focus | never pinned outside a preview or a capture |
| size family | three spans straddling 32 to 96, one radius each, one thickness of 8 | the spans the controls want |
| curvature | capsule housings and buttons; concentric children; generous rounded platters | the anchor the page names |
| groups | one per bar partition; texture plane where the content is media | the inventory |
| tint | none | one seed on the primary action or a status, or withheld |
| ink | the runtime's primary label token on a child element | an app ink where a ratio is guaranteed |
| accessibility | the runtime follows the system; a boolean from the app's own setting where Reduce Transparency cannot be queried | pinned only for a capture |
| motion | the runtime's springs; no idle motion | nothing, unless measured |

## 6. Derivation

- **Is glass earned at all?** It is earned when controls genuinely sit over a plane that changes
  beneath them and the transparency preserves context: a media player over artwork, controls over a
  map or a canvas, a floating bar over a full-bleed photograph, an inspector over a document, a
  transient platter. It is not earned over flat grey chrome, dense tables, forms or dashboards, and it
  is never earned because a card can be made translucent. A brief that names glass for a product with
  no live plane gets the smallest honest version, one control layer over the least flat surface the
  product has, with the tension recorded in a line.
- **Design the opaque page first.** Lay the page out as if no material existed, with its hierarchy
  carried by layout, grouping and type; then let the glass find the controls. The fallback tiers and
  the accessibility states fall out of that order for free, and the alternative, a page designed
  around its translucency, is the one the critics were describing.
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

- No glass on content: a card, a row, a list, a table, a panel of content, a hero made of glass.
- No glass on glass, and no border, background, shadow or blur authored on a glass host.
- No two variants on one page; no clear glass over bright content without its dimming layer.
- No second tint hue in a group; no tint on a label; no solid fill standing in for a tint; no
  hand-rolled blur standing in for the material.
- No glass over a flat, uniform field.
- No cross-fade between glass surfaces, no fade-in by opacity, no idle motion, no colour-swap press
  state.
- No depicted material anywhere else on the page: no brushed metal, leather, bevel, faux grain or
  painted highlight.
- No dishonest backdrop declaration, no pinned sampling padding, no fixed pixel offset standing in
  for a bar inset.
- No prose on glass.

### Mechanical subset

```
no backdrop-filter, box-shadow, border or background authored on any element the runtime registers
  (the one allowed background is the user-agent reset on a native button: transparent, appearance none)
no element registered as glass carries a list, listitem, row, table or article role
no two distinct tint hues resolve inside one sampling group
no opacity transition or animation targets a glass host or any ancestor of the glass root
no filter, backdrop-filter, opacity < 1, mask-image, clip-path or mix-blend-mode on any ancestor of the glass root
every registered surface's shorter span is at or above 32 unless it is a control the family deliberately sizes smaller
dev-mode diagnostics: zero
```

## 8. QA lens

Answer each on the rendered page, in both colour schemes, once with transparency reduced, once on the
CSS tier and once with the window unfocused. A page failing a `[layer]` or `[material]` check is not
this material whatever else it does; a `[layout]` or `[legibility]` check can occasionally be lost to
a web context, and the record says which and why rather than passing it silently.

1. `[layer]` Every glass surface is navigation, an action or a transient platter; no content surface
   uses glass.
2. `[layer]` No glass is drawn on glass; anything on glass is a fill, transparency or vibrancy.
3. `[layer]` The floating inventory is short and each entry is load-bearing.
4. `[material]` One variant across the page; clear only over media with its dimming layer.
5. `[material]` At most one tinted control per view, the primary action or a status, tinted on its
   background; no solid fill and no hand-rolled blur anywhere in its place.
6. `[material]` No glass over a flat, uniform field; every surface sits over structure at every phase
   of its plane.
7. `[material]` No depicted material anywhere else on the page.
8. `[geometry]` Every rounded shape is fixed, capsule or concentric; nested radii derive from their
   container and no corner reads pinched or flared; the concentric anchor is named.
9. `[geometry]` Single-row floating housings and buttons are capsules; inner controls are concentric
   with their housing; platters keep a generous rounded rectangle.
10. `[geometry]` The size family straddles 32 to 96 with one radius per span and one thickness.
11. `[grouping]` Related items share one group, unrelated ones do not, at most three groups per bar,
    no text button beside an icon button in one group, groups spaced past the runtime's padding.
12. `[legibility]` Label contrast measured on rendered pixels across the plane's phases: 4.5:1 for
    labels, 3:1 for large text and plates, both schemes.
13. `[legibility]` At rest, content does not sit under a glass control; a scroll edge sits wherever
    content passes under one and nowhere else.
14. `[legibility]` The page works with transparency reduced, contrast increased, motion reduced and
    under forced colours, and the receded pose is a designed state.
15. `[layout]` Content reaches the window's edges and clears the floating bars by a measured inset;
    the plane is viewport-fixed and never scrolls its glass out from under itself.
16. `[layout]` No bar, sheet or popover carries a custom background, border or scrim.
17. `[motion]` Glass materialises and morphs; menus and sheets emerge from their control; press is
    glow and flex at the pointer; nothing moves at idle.
18. `[colour]` The control layer is monochrome by default; saturated colour is the plane's; no label
    colour approaches the content behind it.
19. `[honesty]` The declared backdrop matches the plane at its lightest and darkest; the runtime's
    resolved state is read, not assumed; dev-mode diagnostics are zero.
20. `[eye]` The page's capture sits beside a native capture of the nearest Apple surface, and the
    difference the eye sees that the checks did not is written down. Where no native capture is
    available, the record names the nearest Apple surface and says that no comparison was made.

## 9. Reference routing

| reference | read it for |
|---|---|
| `references/optics.md` | the measured physical model: the lens, the size law, the body's two components, tone and hue, the rim, the exterior shadow, poses, schemes, variants, tint, ink, accessibility states, motion character, the two tiers and the named gaps |
| `references/vitrea.md` | the cookbook: each decision above mapped to the 0.24.0 API on the React and vanilla paths, what the runtime does not catch, the CSS-only path, single-file and CDN status |
| `references/examples.md` | six worked derivations from built pages, what they have in common, and the record template a project writes down |

## 10. Provenance

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
