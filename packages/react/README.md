# vitrea-react

**React bindings for [vitrea](https://www.npmjs.com/package/@vitreajs/vitrea) — a
production-oriented, reference-calibrated material compositor for semantic web
controls.**

vitrea replicates Apple's Liquid Glass material on the web: real-time
size-parameterized lensing, per-element backdrop adaptation, container-scoped
sampling, and shape-to-shape morphing. This package is the declarative surface —
components and hooks — and it is thin by policy. It maps React lifecycle and JSX
onto the runtime and owns no material, no geometry and no motion of its own, so a
later Vue, Svelte or Web-Components adapter duplicates nothing but the lifecycle.

The important consequence of that thinness is what your markup stays. A
`GlassButton` renders a real `<button>`: selectable text, real focus, working IME,
announced by a screen reader as a button. The glass is drawn on canvases above and
below it, never instead of it.

---

## Install

```bash
npm install @vitreajs/vitrea-react
```

The library is called vitrea and publishes under the npm scope `@vitreajs`. This
package declares two dependencies, both of them ours and both installed for you:
`@vitreajs/vitrea` (the pure runtime) and `@vitreajs/vitrea-web` (the browser
host). React is a peer (`>=19`). Everything else — the geometry kernel, the
motion kernel, the WebGPU renderer — is internal and bundled in at publish time.
There is no state library, no animation library, and no accessibility library in
here.

The host is a **dependency rather than an inlined copy**, and that is deliberate:
a page that mounts one root through these bindings and another through
[`@vitreajs/vitrea-web`](../platform-web/README.md) directly must share one host,
or it gets two plane managers and two host registries that cannot see each
other's nodes. It also means React is no longer the only way to render glass in a
browser, which it was until 0.2.

**What this package adds over the host.** JSX, lifecycle, the `asChild` seam, the
v1 controls, and the interaction wiring that turns pointer and keyboard events
into the material's channels. It adds no material, no geometry and no motion —
those all live below it, which is why a later Vue, Svelte or Web-Components
adapter duplicates nothing but the lifecycle.

---

## Quickstart

```tsx
import { GlassRoot, GlassGroup, GlassToolbar, GlassButton } from "@vitreajs/vitrea-react";

export function App() {
  return (
    <GlassRoot renderer="webgpu">
      {/* Your page. Ordinary DOM, and it stays ordinary DOM. */}
      <YourPage />

      <GlassToolbar
        aria-label="Actions"
        groupProps={{ hint: { tone: "dark", luminance: 0.18 } }}
        style={{ position: "fixed", bottom: 32, left: "50%", transform: "translateX(-50%)" }}
      >
        <GlassButton onClick={share}>Share</GlassButton>
        <GlassButton onClick={save}>Save</GlassButton>
      </GlassToolbar>
    </GlassRoot>
  );
}
```

Three things are happening there, and each is a deliberate contract rather than a
convenience:

`GlassRoot` owns the whole lifecycle — one runtime, one scheduler, the managed
planes — and is the only component that does. Note that glass surfaces render
nothing for exactly one commit while the root is built in an effect; your own page
content renders immediately, because gating the app's content on vitrea's schedule
would be the wrong trade.

`GlassToolbar` creates its own **sampling group** for its members (pass
`group={false}` to put them in the group already in scope instead). A group is
the sampling unit: one backdrop proxy, one blur, shared between members. It also
handles arrow-key roving focus for its items, wherever in the DOM they have been
portalled to.

`hint` is how you tell the runtime what is behind a group. vitrea does not
automatically pixel-analyse arbitrary DOM and never claims to — the hint (or an
estimator provider) is the one mechanism, and it is documented as a hint
everywhere it appears.

**The hint also decides how the material itself looks over a dark backdrop.**
Apple's Liquid Glass stops being a lighter thing in front of a dark enough
backdrop and takes that backdrop's own tone; vitrea now does the same, so the
tone you declare is the tone a small surface settles into. The threshold is low —
nothing happens above roughly a fifth of the luminance range — and the effect is
size-gated: a 44 px control over a near-black backdrop disappears into it, while
a large panel over the same backdrop keeps most of its own appearance. Measured
against the reference rather than styled;
`docs/doperpowers/specs/c9a-fidelity-claims.md` §5.8 has the numbers.

Where you register a **texture** backdrop, vitrea measures that source's average
tone from the pixels you handed over and needs no hint for this. Where it has
neither, the material does not adapt at all, on either tier — it will not guess a
backdrop it has not been shown.

### Surfaces outside a control

```tsx
<GlassGroup id="hero" hint={{ tone: "light" }}>
  <GlassSurface radius={20} thickness={10}>
    <h1>Anything you like in here</h1>
  </GlassSurface>
</GlassGroup>
```

`GlassSurface` takes `asChild` when you want to register your own element rather
than have it render a `<div>` — which is how the menu is composed, over whichever
accessible menu primitive your app already uses. This package deliberately takes
no dependency on one.

**A surface has no intrinsic size**, and this is the one thing about it that
surprises people. vitrea declares neither position nor size for a host: it
measures the box your CSS produced, once per frame, and fits the material to it.
The element is portalled into its plane's host layer, which is a
`position: absolute; inset: 0` overlay, so a surface places itself the way any
overlay child does. Give it your own width, height and positioning — a
`<GlassSurface>` with no styles of its own is as tall as its content and nothing
more. Position and size are never props, because a measured rect is the single
source of truth that lets press compression and morph deformation be composed
transforms rather than shape changes.

### Identity in place: `present`

```tsx
<GlassSurface present={showGlass} radius={20}>
  <button onClick={() => setShowGlass((value) => !value)}>Toggle the material</button>
</GlassSurface>
```

`present` defaults to `true`. Set it to `false` to dematerialize to `Glass.identity`
without unmounting, changing geometry, or hiding content; set it back to bring the
material back. A surface initially mounted absent starts at identity, without an
entrance animation. To animate an entrance, keep it mounted and change `present`.
Unmount still releases synchronously — there is no delayed-unmount hook.

The per-frame `--vitrea-materialization` channel goes from 1 to 0 in a monotonic
220 ms ease (and reverses from its current value when interrupted). That ease is
the built-in default and is **not** tuned by a `profile` passed to `GlassRoot`:
presence is driven once by the framework-agnostic root, which has no motion-profile
input of its own, so an app's profile retunes the channels the bindings own and
leaves this one at its default. It scales the
material, never the host's `opacity`: fading a host would create a Backdrop Root
and cut off sampling. Reduced Motion steps presence on both tiers. Timing and
easing are authored, not measured against a native frame sequence. Identity does
not hide, disable or remove content from the accessibility tree, and foreground
tokens remain published. The app still owns its content, interaction, and contrast
over the now-uncovered backdrop.

### Choosing a morph transition

`GlassMorph transition="matchedGeometry"` is the default, preserving the existing
geometry-matching behavior. `transition="materialize"` instead materializes the
destination in its own place while dematerializing the source, and crossfades
only their content. It never matches the endpoints' positions or sizes. Reduced
Motion steps that transition too. Keep the accessible trigger, destination and
focus behavior supplied by the app's menu or other control primitive; changing
the material transition does not supply those semantics. In materialize mode the
render function runs once per endpoint, with that endpoint's `open` value (the
source still receives `false` while the destination is open). Give content IDs
that are distinct between endpoints.

A materialize pair registers two glass nodes, and it names the second one itself:
a `nodeId` names the closed endpoint and `` `${nodeId}-open` `` is **reserved** for
the open one. Do not name another surface with that suffix — a scene may not carry
two nodes under one id, and the collision surfaces as core's `duplicate-id`
`GlassSceneError` at registration rather than as anything visual.

The playground's **Dismiss glass / Bring glass back** control demonstrates
identity. Select **Materialize the Actions menu**, then open **Actions**, to try
the transition without a geometry match.

### Colouring a surface: `tint`

```tsx
<GlassToolbar aria-label="Document actions">
  <GlassButton onClick={publish} tint="#ff9500">Publish</GlassButton>
  <GlassButton onClick={duplicate}>Duplicate</GlassButton>
  <GlassButton onClick={remove}>Delete</GlassButton>
</GlassToolbar>
```

`tint` takes **any CSS colour** — a hex, an `rgb()`, a named colour, an
`oklch()`, whatever your design tokens are already written in. It is the
supported way to colour glass, and it exists because the obvious alternative is a
documented failure: a background colour on the host element is a solid fill, and
Apple names exactly that — *"it is completely opaque and breaks the visual
character of Liquid Glass."*

**The colour you pass is a seed, not a fill.** Apple's material "generates a
range of tones that are mapped to content brightness underneath the tinted
element", and vitrea does the same, measured on the reference rather than
assumed: the tint is an opaque, hue-preserving **shade** of the seed whose
brightness follows the untinted material's own luminance, so one orange settles
to a deep amber over dark content and the seed itself over light content. On the
WebGPU tier that happens per pixel, inside the optics pass, against the same
lens-displaced sample the material refracts. On the CSS tier — which has one
colour per element to work with — the shade is read at one backdrop level and
folded into the same single layer the material's own tint goes through, so the
two tiers stay derived from one document instead of holding two sets of numbers.

**A tint never moves the material's own opacity.** The shade is composited over
the material at the strength you give it — opaque at full strength, as the
reference's is; at half strength the material still shows through — and what it
never touches is the material's occlusion, which is the axis *Reduce
Transparency* lifts and where a system-level glass preference lands. The
accessibility policies still resolve after the tint, so a tinted surface under an
accessibility preference gets *more of the author's colour*, not a different one.

The colour's own **alpha is the tint's strength** — `rgb(255 149 0 / 50%)` is a
half-strength orange, the same way `Color.orange.opacity(0.5)` is in SwiftUI — so
subtlety is expressed in the colour rather than in a second prop. `tint={null}`
clears a tint inherited from the group.

Three things worth knowing before you reach for it:

- **Tint sparingly.** Apple's guidance is to colour one element that benefits
  from emphasis — a primary action, a status indicator — and explicitly not the
  backgrounds of several controls at once: *"when every element is tinted,
  nothing stands out."*
- **A group carries one seed.** A `GlassGroup` is one sampling region and one
  optics pass, which is exactly enough for the composition above (one coloured
  control among plain ones) and not enough for two different hues in one group.
  Asking for two raises a dev-mode warning naming the fix, which is to give the
  second surface its own group. That one seed can be declared on the group
  itself — `<GlassGroup tint="#ff9500">` colours every member that declares no
  colour of its own, and a member opts out with `tint={null}`.
- **The ink follows the tint.** vitrea publishes `--vitrea-foreground` against
  the material it is actually drawing, so a dark tint gets the light ink without
  you declaring anything — including on a group with no backdrop hint at all,
  wherever the tint decides the answer for every possible backdrop.

Under **forced colours** the tint goes with the rest of the material: there is no
glass to colour, and the surface takes the platform's palette.

**What is measured, and what is not.** The tint is implemented on both tiers and
visually verified on both — that a tinted surface takes the colour, that its
untinted neighbour in the same group does not, and that the backdrop still
transmits through it rather than being replaced by paint. **It carries no
fidelity number.** Every constant in the tone curve is an advisory default, and
the tinted native captures that would fit them are a scheduled extension of the
capture harness, not something this release measured. When those land, the curve
becomes a data change and the claim below gains a tint section; until then, treat
the tint's *appearance* as designed rather than as calibrated.

The playground's **tint-and-ink band** is this section running. A `GlassGroup
tint` colours a plate and the button beside it, a `GlassButton tint` sits in the
group it had to step out into to carry a second seed, and both are over a light
and a dark ground at once — so the same colour settling to two shades is one
glance rather than two paragraphs. Both seeds and both strengths are under
controls, and the band names the tier that drew it.

### Splitting a toolbar's background

A system toolbar rarely has one piece of glass in it. Apple gives you two ways to
break the shared background up — `ToolbarSpacer`, a gap at a position, and
`sharedBackgroundVisibility(.hidden)`, one item stepping out — and vitrea ships
both, because both are the same thing: **`GlassToolbar`'s children are
partitioned into sampling groups at each `GlassToolbarSpacer` and at each item
that declares `sharedBackground="hidden"`.**

```tsx
<GlassToolbar aria-label="Document actions" groupProps={{ id: "bar" }}>
  <GlassButton onClick={share}>Share</GlassButton>
  <GlassButton onClick={duplicate}>Duplicate</GlassButton>

  <GlassToolbarSpacer kind="flexible" />

  <GlassButton onClick={publish} sharedBackground="hidden" tint="#ff9500">
    Publish
  </GlassButton>
</GlassToolbar>
```

That is one `role="toolbar"` with two sampling groups — never two toolbars. The
row keeps its single tab stop and its arrow-key order across the split, because
the roving order is over the items and never saw the grouping; the flex layout is
untouched, because a group renders no DOM. What changes is what shares a proxy,
a blur and a union: the first two buttons read as one body of material, the
tinted one as its own.

This is also the answer to *"a group carries one seed"* above. A tinted primary
action beside a tinted toolbar is two seeds, which one group cannot carry — so
the item that steps out takes its own group, and the tint goes with it. Where
that group needs more than a colour, the item can carry `groupProps` of its own
(`groupProps={{ id: "primary", hint: … }}`), merged over the toolbar's.

`kind` is `"fixed"` (the default: hold the gap) or `"flexible"` (also take the
free space, which is what puts the last item at the far end). **The gap is a
minimum you do not choose.** Two adjacent groups each sample a padded region
around their own shapes, and where one group's padded box covers the other's
shapes the backdrop filter applies twice over the overlap. So a spacer opens the
sampling padding the material actually requires under the resolved accessibility
policy, and never less than the advisory the scene model checks a layout
against — turn *Reduce Transparency* on, the frost thickens, and the material's
own requirement rises past that advisory on a normal-height bar. Your own `gap`,
margin or width adds to it rather than fighting it, and an explicit `style` of
your own still wins: a number you wrote is a statement about your geometry, and
the dev-mode overlap warning is the backstop either way.

Nothing new is needed on the framework-agnostic entry: a group is already the
primitive there, so a host-level app splits a toolbar by registering its members
in two groups and leaving one padding between them.
`samplingPaddingFor({ members, material })` from `@vitreajs/vitrea-web` is the
material's half of the number this spacer opens; the other half is
`DEFAULT_GROUP_SAMPLING.samplingPadding` (or your group's own
`samplingPadding`, when you declare one).

### Where a surface belongs: the controls layer

`GlassSurface` will glass whatever element you hand it, and there is one place it
should not go. Apple states it as a prohibition rather than as advice — **"Don't
use Liquid Glass in the content layer"** — because the material's whole job is to
separate what you can act on from what you are reading, and glass on both sides
of that line collapses it. The same rule read the other way is why `GlassToolbar`
is deliberately *not* a glass surface: stacking the material on itself is a
failure Apple names outright ("avoid applying the material to both layers.
Instead, use fills, transparency, and vibrancy for the top elements"), so the
toolbar is a plain container and the platter you see is its members' fields
merging.

In practice: glass on the button, not on the row it sits in; glass on the
toolbar's controls, not on the toolbar and its controls; and never on a list or a
table, which is the case Apple calls out by name and the one `asChild` makes
easiest to get wrong.

Two dev-mode diagnostics now say so instead of leaving it to the docs:

- **`glass-inside-glass`** — a surface registered inside another surface's
  subtree. It names both nodes and tells you to keep the material on whichever of
  the two is the control, giving the other a fill, a translucency or a vibrant
  foreground. Not the same finding as core's `same-plane-overlap`: that one is
  geometric and about the paint sandwich, this one is structural and still fires
  when the nesting crosses planes.
- **`glass-in-content-layer`** — a surface registered on an element whose
  resolved ARIA role is a list or table structure (`<ul>`, `<li>`, `<tr>`,
  `role="row"`, and so on). An explicit `role` wins over the tag's implicit one,
  so `<ul role="menu">` is a controls-layer container and says nothing; the
  message names that escape.

Both run once per registration, in `devMode` only, and never from a frame — a
production build pays nothing for them. Both arrive on the diagnostics channel
like every other finding, so `useGlassDiagnostics` puts them on screen if you
want them there rather than in the console.

### A texture backdrop

`backdrop={{ kind: "texture", id }}` moves a group onto the GPU texture path, and
it is deliberately two steps: the prop **declares** the source, and the root
handle **supplies** the pixels. `@vitreajs/vitrea` is platform-free and may not
hold an `HTMLImageElement`, so the declaration cannot carry one.

```tsx
import { GlassGroup, GlassSurface, useGlassRoot } from "@vitreajs/vitrea-react";

function Hero() {
  const root = useGlassRoot();

  return (
    <>
      {/* Declare. `configuredSource` stays "texture" through any demotion. */}
      <GlassGroup id="hero" backdrop={{ kind: "texture", id: "hero" }}>
        <GlassSurface radius={26} thickness={18}>…</GlassSurface>
      </GlassGroup>

      {/* Supply. The id joins the two halves; the order does not matter, and
          `setBackdropTexture` marks the source dirty itself. */}
      <img
        src="/hero.jpg"
        alt=""
        onLoad={(event) =>
          root?.setBackdropTexture("hero", { kind: "image", image: event.currentTarget })
        }
      />
    </>
  );
}
```

`{ kind: "canvas", canvas }` and `{ kind: "video", video }` are the other two
forms — a video and a live canvas are re-imported every frame that samples them,
a decoded image once — and `undefined` withdraws a source's pixels. Declaring a
texture and never supplying one is not a silent hole: the group reports
`health: "demoted"` with `demotionReason: "no-texture-supplied"` and goes on
drawing tint, rim and glow.

**Where the texture is placed.** The renderer maps the source over the **whole
viewport**, cover-fit — filling it, with the overflow cropped symmetrically, the
same geometry as `object-fit: cover` on a `position: fixed; inset: 0` element.
Not over the group, and not over the surface. So if your app also paints that
image — the usual case, since the picture is on the page and the glass sits on it
— the two mappings have to agree. An `<img>` sized to a region under a texture
mapped to the viewport samples a different crop of the same file, and the
mismatch shows up as the glass revealing the wrong part of the picture, which
reads convincingly like a lensing artefact rather than a registration error.
Paint your copy viewport-sized and `object-fit: cover`.

### Seeing what actually resolved

```tsx
function TierReadout() {
  const state = useGlassCapabilities("hero");
  if (state === undefined) return null;
  return (
    <p>
      configured {state.configuredSource}, drawing on {state.activeRenderer},
      sampling {state.samplingBackend}, refraction {state.refraction}
      {state.health === "demoted" ? ` — demoted: ${state.demotionReason}` : ""}
    </p>
  );
}
```

Asking for the GPU tier is not the same as getting it, and this hook is how you
find out which happened. Choosing the CSS tier is **not** a fault: a root that
never requested WebGPU resolves to `activeRenderer: "css"` with `health: "ok"`
and no demotion reason. Every real demotion names both a reason and its recovery
condition. The full model is documented in
[`@vitreajs/vitrea`'s README](https://www.npmjs.com/package/@vitreajs/vitrea).

### Colour scheme

The material is measured per colour scheme, so a dark page needs the dark
material rather than the light one dimmed:

```tsx
<GlassRoot colorScheme="auto">{/* "light" | "dark" | "auto" */}</GlassRoot>
```

`"light"` is the default and is the material the runtime's own constants are, so
nothing moves for an app that upgrades. `"dark"` draws the numbers vitrea
recorded from Apple's dark-mode material, and `"auto"` follows
`prefers-color-scheme` and re-derives both tiers when the system flips — without
rebuilding the root, so a theme toggle costs no registrations.

**A backdrop hint and the colour scheme are different things.** A group's
`hint={{ tone, luminance }}` states the tone of what is BEHIND the surface, which
is what the adaptation and the ink decision read; the scheme states which
material the surface is made of. A dark page can legitimately hand a light hint
to a surface over a white card.

Your own tokens stay yours: vitrea does not write your page's background, so an
app offering "follow the system" reads `prefers-color-scheme` for its colours as
well as passing `"auto"` here. `apps/demo`'s site switch is the worked example of
both halves moving together.

### Which macOS the material is measured against

macOS 27 changed Apple's material under every app, and **from 0.19.0 a page draws
the macOS 27 material by default**. The previous reference is shipped beside it
and selectable, as one value:

```tsx
import { macos26MaterialProfileDocument } from "@vitreajs/vitrea-web";

<GlassRoot materialProfileDocument={macos26MaterialProfileDocument}>…</GlassRoot>
```

A document carries the active patch and the receded difference for both colour
schemes plus what the material costs on the CSS tier, so one prop moves every
tier and both poses together. It is read at construction: a scheme and a window
pose move *within* one material, where a different document is a different
material.

`materialProfile` (a tuning of the renderer's optical constants, applied live)
and `cssTierMapping` (the CSS crossing) are surfaced beside it for an app naming
a material by hand; both merge over whatever the document selected. Before
0.19.0 this binding surfaced none of the three, so a React app could not select
a reference material at all.

**Upgrading changes what your page looks like** — surfaces over dark backdrops
are no longer nearly invisible, the rim and the outer shadow differ, and
CSS-tier visitors get a wider blur. The documents, the measurements behind them
and how to read `root.material` back are in
[`@vitreajs/vitrea-web`'s README](https://www.npmjs.com/package/@vitreajs/vitrea-web).

### Window activation

Apple's glass recedes when its window loses focus. That is a fact about the
window, not about any one surface, so it is a prop on the root and there is no
`inactive` interaction state to look for on a surface:

```tsx
<GlassRoot windowActivation="auto">{/* "auto" | "active" | "inactive" */}</GlassRoot>
```

`"auto"` is the default and follows the window's own focus, re-read from
`document.hasFocus()` whenever the window fires `focus` or `blur`. Pin the prop
to `"active"` or `"inactive"` and the pin wins over the window in both
directions, which is what a preview pane, a screenshot or a visual-regression
run needs. Changing it does not rebuild the root, so no registration in the tree
is dropped.

```tsx
function PoseReadout() {
  const pose = useGlassWindowActivation(); // "active" | "inactive", "auto" already folded
  return <p>the glass is drawing its {pose} material</p>;
}
```

The hook reports what resolved rather than what was asked for, on the same rule
as `useGlassCapabilities`. An app that needs to move the pose imperatively —
from an event the prop cannot see, or from outside React's render — reaches the
runtime through `useGlassRoot()` and calls `root.setWindowActivation(...)`; the
binding does not re-assert its prop on every frame, so what you set by hand
stays set until the prop itself changes.

The material it selects is the receded endpoint of whichever document the root
drew. On macOS 27's, which is the default, the body darkens and the surface
**keeps** its outer shadow; on macOS 26.5's the shadow and the bright rim go
entirely. In both, an author's tint survives as an achromatic shade. It is a
fitted appearance rather than a pixel-match guarantee, and the gaps are named in
[`@vitreajs/vitrea-web`'s README](https://www.npmjs.com/package/@vitreajs/vitrea-web).

---

## What this package exports

**Components** — `GlassRoot`, `GlassGroup`, `GlassSurface`, `GlassMorph`,
`GlassButton`, `GlassIconButton`, `GlassToolbar`, `GlassToolbarSpacer`,
`GlassSegmentedControl`, `PlanePortal`.

**Hooks** — `useGlassCapabilities`, `useGlassAccessibility`,
`useGlassWindowActivation`, `useGlassDiagnostics`, `useGlassMotionProfile`,
`useGlassTicker`, `useGlassRoot`, `useToolbarItem`.

**Composition helpers** — `renderAsChild`, `composeRefs`, `mergeSlotProps` for
`asChild` seams; `radiiFor`, `smoothingFor`, `capsuleRadius`,
`cornerReferenceFor`, `assertSharedCornerReference` for shapes;
`withoutToolbarItemProps`, which a control of your own that declares
`GlassToolbarItemProps` uses to drop the pair before it spreads the rest onto an
element.

**Types** — `GlassColorScheme` and `ResolvedColorScheme`, and
`GlassWindowActivation` and `ResolvedWindowActivation`, re-exported from the
runtime so a `colorScheme` or `windowActivation` prop of your own can be typed
without installing it;
`GlassToolbarItemProps`, the `sharedBackground` / `groupProps` pair a toolbar
reads off its children, so a control your app wrote can declare them too.

**Frames** — `createGlassTicker`, the rAF loop the bindings drive their motion
from. One per tree, whatever the surface count; its `advance()` steps time by
hand, which is the path a test with no animation frames takes.

**Constants and defaults** — `DEFAULT_CLEAR_DIMMING` (the one-liner that
satisfies the clear variant's dimming requirement — the runtime refuses a clear
surface without a policy rather than inventing a scrim),
`APPLE_LIKE_SMOOTHING` (the Apple-matching corner on the interpolable smoothing
axis — a `GlassMorph` pair needs it, because `"continuous"` and the numeric axis
are separate fits to different curves and an interpolated corner between the two
has no measured error bound; authoring this number at both ends keeps the morph
on one axis), `DEFAULT_GLASS_MOTION_PROFILE`,
`GLASS_ROOT_ACCESSIBILITY_DEFAULTS`, `SUPPORTED_PLANES`,
`GLASS_CHANNEL_PROPERTIES`.

**DOM attribute names** — `TOOLBAR_ITEM_ATTRIBUTE` (`data-vitrea-toolbar-item`,
which marks an item's owning toolbar wherever the item has been portalled to) and
`PLANE_MOUNT_ATTRIBUTE` (`data-vitrea-mount`). Both are public because tests and
dev tooling read them.

### Contract limits worth knowing before you design around it

- All glass lives inside `GlassRoot`'s managed planes. v1 ships exactly two —
  base and one overlay — and menus portal internally to the overlay plane.
  Interleaving glass with foreign stacking contexts is out of contract.
- Two glass surfaces must not overlap **within one plane**: it is a dev-mode
  error, because the paint sandwich cannot place one surface's body above another
  surface's DOM label. Overlap *across* planes is the supported case, and is what
  `GlassMorph` uses.
- Corner radii are uniform in v1. The API keeps its four-component shape; a
  non-uniform set is a dev-mode error.
- Mixing `regular` and `clear` variants inside one group raises a dev-mode
  warning, mirroring Apple's own guidance.
- One `tint` seed per group. Two different tint colours inside one `GlassGroup`
  raise a dev-mode warning: a group is one optics pass, so the WebGPU tier draws
  them all in the first surface's colour while the CSS tier honours each. Per
  surface, tint *strength* is unrestricted — one coloured control among plain
  ones is the supported composition.

---

## Styling a glass host

A glass host is your element. The runtime writes to it every frame — the tint,
the border, the blur, and a set of custom properties — but it never takes the
element's styling away from you.

The properties it publishes, on every host, on **both** tiers:

| Property | What it carries |
| --- | --- |
| `--vitrea-foreground` | The ink the runtime resolved as readable on the material this group is drawing — Apple's automatic label colour through its vibrancy operator, so `rgb(0 0 0 / 0.847059)` over a bright surface and `rgb(255 255 255 / 0.804706)` over a dark one. |
| `--vitrea-foreground-secondary` | The same ink, reduced — Apple's `secondaryLabel`. Holds WCAG 4.5 against this surface wherever the primary can. |
| `--vitrea-foreground-tertiary` | Apple's `tertiaryLabel`. Supporting text; below the body-text floor. |
| `--vitrea-foreground-quaternary` | Apple's `quaternaryLabel`. Separators and decoration; **not** for text. |
| `--vitrea-tint` | The tint colour, with its alpha. |
| `--vitrea-occlusion` | That alpha on its own, `0`–`1`. |
| `--vitrea-border-color` | The rim colour. |
| `--vitrea-blur` | The frost radius, in CSS px, after accessibility policy. |

Read them the way the demo does, with your own value as the fallback so a tier
that published nothing degrades to your design rather than to nothing:

```css
.my-panel__label {
  color: var(--vitrea-foreground, var(--my-ink));
}
.my-panel__caption {
  color: var(--vitrea-foreground-secondary, var(--my-ink-secondary));
}
```

### What the four ink levels guarantee, and what they do not

Apple names four label levels and gives each a fixed alpha, and vitrea publishes
**macOS's** four rather than iOS's — this is a runtime replicating macOS's
material, so it publishes macOS's ladder. The two poles are not symmetric, so
there is one number per level *per pole* rather than one per level:

| Level | Dark ink, over a bright surface | Light ink, over a dark surface |
| --- | --- | --- |
| primary | 0.847059 | 0.804706 |
| secondary | 0.498039 | 0.521569 |
| tertiary | 0.258824 | 0.234706 |
| quaternary | 0.098039 | 0.093137 |

Where those come from, because it explains both the colour and the asymmetry.
Apple's labels do not draw their own colour on glass: a `vibrantColorMatrix` sits
on the label inside the `glassEffect`, and both of its poles offset every colour
channel by a whole unit against the filter's clamp, so the operator *saturates* —
nothing of the input colour survives it and the only thing the label contributes
is its alpha. That is why vitrea's ink is pure black and pure white rather than a
hex. The lightening pole additionally scales alpha by 0.95, and that one
coefficient is the whole of the right-hand column above: it is macOS's
dark-appearance ladder (0.549020, 0.247059, 0.098039) times 0.95, and 0.804706 is
0.847059 times it.

The four alphas themselves are documentation-sourced, and are published as such.
Apple publishes no component values for `labelColor` and its three siblings and
says not to hard-code them, so these are third-party measurements — four of them
agreeing exactly, and unchanged from macOS 11 through macOS 26.5.

Every one of those numbers is calibrated against the platform's own *opaque*
backgrounds, and glass is never one. So vitrea does not publish them flat.

- **`--vitrea-foreground-secondary` holds 4.5** against the colour this surface
  is actually drawing — the composite, not a grey of the same brightness, so a
  saturated tint is measured against the tint. Where the backdrop is not known
  the floor is solved against both ends of the range the surface can reach and
  the harder answer taken, so the guarantee does not depend on which backdrop
  turns up. It is Apple's own alpha wherever that already clears the floor and
  raised where it does not — as far as the *primary's* own alpha and no further,
  which is 0.847059 or 0.804706 rather than opaque. In practice Apple's number
  survives unraised only over dark surfaces below an encoded level of about 0.19:
  over a bright one the black ink at 0.498039 never reaches 4.5 through this much
  translucency, so it is always raised there. On a surface whose *primary* ink
  cannot hold 4.5 either, secondary collapses onto the primary: there is no
  second readable level there, and publishing one would be a lie your users would
  find before you did. Secondary is therefore never worse than primary, and holds
  4.5 wherever primary can.
- **There is a band of surfaces where neither ink carries body text, and Apple's
  alpha widened it.** A translucent primary costs contrast on both poles, so the
  range of surface levels over which neither the black ink nor the white one
  reaches 4.5 has grown from an encoded [0.4425, 0.5145], where an opaque primary
  left it, to [0.3935, 0.4900]. A surface that lands in there gets a primary that
  misses the floor and a secondary collapsed onto it, and the runtime will not
  pretend otherwise. Three things move a surface out of the band: hint the
  group's backdrop, so the ink is decided against the level the surface really
  has rather than against the hardest one its bracket could reach; pick a thicker
  or a less clear variant, so more of what the glyphs sit on is the material's
  own; or author the colour yourself, which is a right an application rule naming
  the host keeps — see below.
- **Tertiary and quaternary carry no floor.** They are Apple's supporting and
  decorative tiers, they are not body text, and lifting them to 4.5 would
  collapse the whole scale onto one value. Use tertiary for text a reader may
  skip, and quaternary for separators, placeholders and decorative glyphs.
- **Quaternary on a thin surface is what Apple explicitly warns about.** In dev
  mode, a page whose CSS names `--vitrea-foreground-quaternary` while a surface
  resolves below the material's thin/thick knee gets a diagnostic naming the
  pair. It changes nothing — the token is published either way.
- Under **forced colours** all four are `CanvasText`, and under **increased
  contrast** all four are the near-monochrome ink. A preference that asked for
  more contrast does not get three dimmer answers.

All four are on one surface in the playground's tint-and-ink band, over both
grounds. What the band makes visible is the part the list above states without
showing: secondary is a *solved* level, so the two grounds can publish an alpha
that appears in neither pole's ladder, while tertiary and quaternary are Apple's
own numbers untouched — which is still two different numbers across the two
grounds, because the poles are not symmetric.

**The ink transits rather than snapping.** A surface whose own level drifts
across the point where the two poles trade places does not flip its text colour
on the frame it crosses: the published ink crossfades over 180 ms through a
0.08-wide dead band, so a backdrop wandering back and forth over that point
cannot pump the label. Mid-transit the token holds a premultiplied mix of the two
poles, which is exactly what `color-mix(in srgb, …)` produces — the value the
platform itself would have interpolated had the custom property been registered
as a `<color>`.

**Your own `color` rule on the host wins.** The runtime's ink reaches the host
through a static rule that resolves `--vitrea-foreground`, installed first in the
document's `<head>` — and never as an inline style, which is what it was up to
0.1.1 and which meant an application rule on a glass host parsed, cascaded, and
silently never applied. On most surfaces that rule is `:where([data-vitrea-node])`
at specificity (0,0,0), so any selector of yours that names the element — a class,
an id, an attribute, a tag — overrides it, and so does an equally weak one by
source order. On vitrea's own controls it is `[data-vitrea-vibrant]` at (0,1,0)
instead, which a class or an id of yours still beats. The section below is why
there are two of them, and how to choose.

Two properties the runtime does own outright, and which you should style around
rather than on:

- **`background`** on the host — the CSS tier writes the shorthand every frame,
  so a `background-image` of yours is clobbered. Put it on a pseudo-element.
- **`transform`** on the host, while a press or a morph is running.

### Who owns the label: `foreground`

`GlassSurface`'s `foreground` prop — and the same prop on `GlassButton`,
`GlassIconButton` and `GlassSegmentedControl` — carries two different kinds of
answer. An object is the **cadence**: `{ mode: "fixed" | "author-hint" |
"sampled-async" }`, how the surface reads the backdrop its ink is decided
against. Two strings are the **ownership** of the label:

- **`foreground="vibrant"`** says this label is vitrea's. It changes no colour:
  the published token already *is* the vibrancy operator's output, because the
  operator carries no backdrop term, which is what lets vitrea fold it into a
  colour rather than install a `filter` over your subtree. What it changes is the
  specificity the runtime's `color` declaration lands at — `[data-vitrea-vibrant]`
  (0,1,0) rather than `:where([data-vitrea-node])` (0,0,0) — so the ink survives a
  reset sheet's `button { color: … }` or a `* { color: … }`, which is the class of
  rule that was quietly taking vitrea's own control labels away from it.
- **`foreground="token"`** hands ownership back, for a control whose content your
  app owns outright.

`GlassButton`, `GlassIconButton` and `GlassSegmentedControl` default to
`"vibrant"`, because vitrea wrote those labels. A bare `GlassSurface asChild` does
not: it holds whatever you put in it, so the operator is an opt-in there.

**A rule of yours that names the element wins on either path**, and that is the
intended behaviour rather than a shortfall. Apple installs the operator on the
*automatic* label colour and leaves a label that names its own colour alone, so a
class or an id of yours beating (0,1,0) — and a tag beating (0,0,0) — is vitrea
doing what the reference does.

One limitation to design around: the two axes share one prop, so a surface cannot
ask for `sampled-async` **and** `"vibrant"` at once. Passing an adaptation object
leaves the label on the token path. Fixing that is additive, and it is tracked.

---

## Fidelity

The material is tuned against real ScreenCaptureKit captures of Apple's
`glassEffect`, not against recollection. The complete record — what was
measured, what could not be, and every gap left open — is
[`docs/doperpowers/specs/c9a-fidelity-claims.md`](https://github.com/SSFSKIM/designer/blob/main/docs/doperpowers/specs/c9a-fidelity-claims.md).

**The bed moved to macOS 27 in 0.19.0**, which is what the default material is
fitted against: 624 cells captured on macOS 27.0 (build 26A428) at the
appearance slider's shipped position, every one of them measured against its
macOS 26.5 counterpart before a line of vitrea changed. Apple's material moved
on all 619 comparable cells and its geometry did not. On the thirteen light
standard scenes held out of all tuning, at 1×, the refitted WebGPU tier reaches
silhouette IoU 0.9994 mean / 0.9951 worst, contour distance 0.015 px mean, SSIM
0.9661 mean / 0.8843 worst and OKLab ΔE 0.0189 mean / 0.0760 worst; the CSS tier
over the same cells reads ΔE 0.0180 mean / 0.0791 worst at SSIM 0.9523 mean. It
is not pixel-identical to Apple's material and seven declared rows are recorded
as missed rather than met — the ledger's §5.153 and §5.154 name each one and what
would close it.

The macOS 26.5 claim below is kept as recorded rather than restated. It is what
this package drew through 0.18.0 and what
`materialProfileDocument={macos26MaterialProfileDocument}` still selects, and its
bed is frozen. As that document words it:

> **Reference-calibrated against macOS 26.5 captures.** vitrea's WebGPU texture
> tier — its own shader math over a GPU-owned backdrop — was calibrated against
> 30 ScreenCaptureKit captures of Apple's `glassEffect` material on macOS 26.5,
> in the cell *Chromium 151, `gpu-texture` backend, Apple Metal-3 adapter, sRGB,
> 1× scale*. Across the six scenes held out of tuning, the rendered result
> reaches a silhouette IoU of 0.9924 mean / 0.9612 worst, a contour distance of
> 0.18 px mean / 0.56 px worst-cell-mean, SSIM 0.9475 mean / 0.9007 worst, and
> OKLab ΔE 0.0320 mean / 0.0548 worst. Tuning improved every one of those axes
> over the untuned defaults. It is not pixel-identical to Apple's material and
> two named gaps remain open.

And for the CSS tier, which is what most visitors will actually see:

> **No cross-engine pixel-wise fidelity claim is made for the dom tier, and none
> can be. On Chromium, in the same cell with `renderer: css` and
> `samplingBackend: css-backdrop`: OKLab ΔE 0.0091 mean / 0.0240 worst and SSIM
> 0.9700 mean / 0.9304 worst over the 12 light calibration cells, ΔE 0.0108 /
> 0.0273 over the 6 validation cells, and ΔE 0.0291 mean / 0.0560 worst with SSIM
> 0.9373 / 0.9205 on the six scenes held out of all tuning. Silhouette IoU 0.9424
> mean over the calibration cells and 0.9684 on holdout, with a 1.06 px mean
> contour distance.**

This tier does not hold a material of its own — it **converts** the one the root
carries — so retuning the material moves both tiers at once. And on demotion:

> On Chromium, a group that demotes from the WebGPU texture tier to the CSS tier
> keeps the same material to within 1.3% of its interior level in the mean and 11%
> on the worst measured cell, at a cross-tier OKLab ΔE of 0.0063 mean / 0.0124
> worst over the fitted sets and 0.0188 / 0.0313 over the held-out ones. It is
> **not** the same rendering — refraction is absent on the CSS tier by contract
> (`refraction: "none"`) — but the material's opacity, tint and frost do not
> change visibly on demotion.

Not claimed, explicitly: **never "pixel-identical to Apple"** — every figure is
scoped to one native profile and one web cell; **no press-state claim**, because
Apple's `Glass.interactive(true)` opts the material into responding to press
input rather than posing it pressed, and the native "pressed" captures are
byte-identical to their rest counterparts; **no adopted pass/fail thresholds**,
only proposals awaiting a human gate; **1× scale only**, with both
accessibility-mode profiles still uncaptured; **no fidelity claim for the author
tint**, whose tone curve is advisory until a tinted native bed exists that
carries colour — the 2026-08-30 captures carry the tint's strength but not its
seed (see `tint` above — implemented and visually verified on both tiers,
measured on neither); and **no claim that the two tiers are identical**, nor that the
coherence figure above holds on Gecko or WebKit, where nothing about
`backdrop-filter` is measurable at all.

---

## Browser support

| Engine | WebGPU (texture tier) | CSS tier |
| --- | --- | --- |
| **Chromium** (Chrome, Edge) | Default-on from 113 desktop, 121 Android | Yes — backdrop-proxy sampling equivalence measured byte-exact |
| **Safari / WebKit** | Default-on from Safari 26 | Yes, manually verified: automated capture cannot observe `backdrop-filter` on this engine |
| **Firefox / Gecko** | Default-on from 141 Windows, 145 ARM Mac; **still flagged on Linux** | Yes, manually verified: same capture blindness |

Where WebGPU is missing, every group resolves to the CSS tier with
`demotionReason: "no-webgpu"`, renders presentable glass, and logs no errors. The
CSS tier is a hard requirement of the design, not a courtesy — which is why it has
its own renderer rather than a degraded code path.

### One known engine defect: Chromium 152 and a rounded, clipping ancestor

Chromium 152 drops `backdrop-filter` entirely on an element with
`clip-path: path()` when an ancestor has `overflow` other than `visible`
**together with** a `border-radius`. All three ingredients are required; every
basic-shape `clip-path` is unaffected. vitrea's GPU-tier backdrop proxies are
exactly that shape, so this can reach a real page.

**With the default mount it cannot**: `GlassRoot`'s planes are `position: fixed`
children of `<body>`, above any rounded, clipping container. It becomes
reachable only if you pass your own `container` and that container sits inside
one — a rounded card, modal or scroll area. There the proxies lose their frost
silently: the engine logs nothing, and no readback path in a page can observe
`backdrop-filter` output at all.

So the runtime says it for you. In dev mode, a group whose proxy chain has that
shape on Chromium 152 or newer emits `engine-known-defect` — a **warning**, never
a demotion, because nothing here is measurable and demoting on a structural match
would trade a possibly-unfrosted GPU tier for a certainly-lower one. The message
names the ancestor, the three workarounds (mount at the default; remove either
the radius or the overflow from that ancestor; or use a geometry a basic shape
can express) and the verified repro. The bug report is drafted at
[`spikes/s1-proxy-topology/chrome152-regression/`](https://github.com/SSFSKIM/designer/blob/main/spikes/s1-proxy-topology/chrome152-regression/REPORT.md).

---

## Testing your app

**Trust the readout; check the launcher.** `useGlassCapabilities()` reports what
resolved, so a `demotionReason: "no-webgpu"` means that session really had no
WebGPU. The environment is the part worth checking, because Playwright's bundled
headless shell resolves WebGPU to a SwiftShader adapter while `channel: "chromium"`
— the full browser binary — resolves it to real hardware. A suite that never asks
for the channel runs green on the CSS tier and every readout in it honestly says
`no-webgpu`: nothing looks broken, it is simply the other tier.

```ts
// playwright.config.ts
projects: [
  {
    name: "chromium-gpu",
    use: {
      channel: "chromium",
      launchOptions: {
        args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
      },
    },
  },
],
```

Serve the page over `http://localhost` while you are at it: `navigator.gpu` is
undefined outside a secure context, and on `file://` or `data:` URLs its absence
reads exactly like "no WebGPU on this machine". A test that means to assert the
GPU tier should fail when no adapter answers rather than skip.

**What is in the DOM depends on the tier.** `[data-vitrea-proxy]` elements exist
only for a group resolved to `activeRenderer: "webgpu"` with
`samplingBackend: "css-backdrop"` — the GPU tier sampling arbitrary DOM — and
there is one per group *per plane* it has members on. A GPU-tier group on a
texture backdrop has none, because there is nothing in the page to filter. And on
the CSS tier there are no proxy elements at all: that tier applies
`backdrop-filter` in place, on each glass host element, which is what keeps a
host's own text and icons above its filter without any layering. So assert the
CSS tier by reading a host's computed `backdrop-filter`, `background-color` and
`border-color`, and assert the tier itself with `useGlassCapabilities()`.

---

## Accessibility

Each preference resolves to a declared consequence, and the strictest active one
wins:

| Preference | What changes |
| --- | --- |
| `prefers-reduced-motion` | No overshoot, no deformation, no shimmer travel; morphs become non-elastic. Direct-manipulation positional continuity is kept — reduced motion is not no motion. |
| `prefers-reduced-transparency` | More frost, less refraction, higher occlusion. |
| `prefers-contrast: more` | Stronger borders, near-monochrome foregrounds, reduced ambient tint. |
| `forced-colors: active` | System colours, borders, **no glass**. |

The first three are overridable per root; the fourth is not, and its absence is
enforced in the type system rather than merely documented — an operating-system
colour mandate is not an app's to switch off.

```tsx
<GlassRoot reducedTransparency={true} increasedContrast="system" />
```

`"system"` follows the media query, a boolean overrules it. Note that
`prefers-reduced-transparency` is not Baseline: on an engine that cannot answer
the query, `"system"` silently resolves to false and the user's preference is
lost, so the runtime emits a diagnostic saying exactly that. Setting it
explicitly is load-bearing.

One obligation this package hands you: content portalled into a plane leaves its
original DOM position, so if it was inside a landmark region you own
re-establishing the landmark. A landmark/`role` seam on `GlassMorph` is deferred
post-v1 API work, and this is the documented behaviour until then.

---

## License

Apache License 2.0. See [`LICENSE`](https://github.com/SSFSKIM/designer/blob/main/LICENSE).

"Liquid Glass" is the name of Apple Inc.'s design language, referenced here
descriptively to say what this library replicates. vitrea is not affiliated with,
endorsed by, or sponsored by Apple Inc. See [`NOTICE`](https://github.com/SSFSKIM/designer/blob/main/NOTICE).
