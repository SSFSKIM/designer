# Saying it in vitrea

The cookbook half of the materialist skill: each decision a glass page makes, and the vitrea call
that states it. `SKILL.md` owns the aesthetic, the laws and the QA; this file owns the API, as it
exists at 0.24.0 (npm `latest`, checked 2026-09-26). React names come from `@vitreajs/vitrea-react`
and vanilla names from `@vitreajs/vitrea-web`; both sit on the same runtime, so every decision
below has one form in each and the same meaning. The runtime reports what it drew rather than what
was asked for, so the last sections are about reading that back.

## 1. Which material the page draws, and how the root says so

One `GlassRoot` (or `createGlassRoot()`) owns the runtime, the frame loop and the two managed
planes. Everything the page decides about the material as a whole is a root option.

- **The tier is a request.** `renderer` defaults to `"css"`: a root that never asks for WebGPU draws
  the CSS tier with `health: "ok"`, which is a configuration and not a fault. `renderer="webgpu"`
  asks for the GPU tier, and `navigator.gpu` exists only in a secure context: `https://`,
  `http://localhost`, and in Chrome a page opened from `file://` as well, which Chrome treats as
  secure (tested 2026-09-26 in Chrome and Chromium; Firefox and Safari untested). Anywhere else the
  request is demoted with `demotionReason: "no-webgpu"`.
- **A colour scheme is a material, not a theme.** The material is measured per scheme, so
  `colorScheme="dark"` selects the measured dark material rather than dimming the light one, and
  `"auto"` follows `prefers-color-scheme` and re-derives both tiers when the system flips, without
  rebuilding the root. The default is `"light"`. This is different from a group's `hint`, which
  states what is behind a surface; a dark page can legitimately hint `light` over a white card.
- **The recede is part of the material. Leave it on.** `windowActivation` defaults to `"auto"` and
  follows the document's focus: an unfocused window draws the receded endpoint, whose rim collapses,
  whose tint keeps its shade and loses its chroma, and which casts no outer shadow. Pin `"active"`
  or `"inactive"` only for a preview, a screenshot or a capture run. A background tab and a jsdom
  document both read as unfocused under `"auto"`.
- **Which macOS.** `materialProfileDocument` defaults to `macos27MaterialProfileDocument`; pass
  `macos26MaterialProfileDocument` to pin the material a page was designed against before 0.19.0.
  One document carries both schemes, both poses and the CSS crossing, so a document is one choice.
  `materialProfile` merges a leaf-by-leaf tuning over whatever the document selected; hold that
  object still between renders.
- **The accessibility overrides are for a preference the engine cannot see.** `reducedMotion`,
  `reducedTransparency` and `increasedContrast` each take `"system"` or a boolean, and `"system"`
  is the default, so writing it changes nothing. The case that needs a prop is
  `prefers-reduced-transparency`, which is not Baseline: where an engine cannot answer, `"system"`
  resolves false and the runtime emits `reduced-transparency-undetectable`, asking for an explicit
  boolean. The only way to honour the preference there is to offer it in the app and pass the
  answer as a boolean; a page that leaves the prop on `"system"` keeps the diagnostic on those
  engines, so zero diagnostics means either an app-level switch or a recorded decision not to
  carry the preference. `forced-colors` has no override by type: the OS mandate is not the app's
  to switch off.
- **Dev mode is part of the design.** `devMode` defaults to true and runs the structural checks:
  nested glass, content-layer hosts, same-plane overlap, tint mixing, variant mixing, non-uniform
  radii, hosts outside their plane, backdrop-root breaks. `onDiagnostic` (React) or
  `diagnosticSink` (vanilla) replaces the console; `useGlassDiagnostics` puts the findings on the
  page. Zero diagnostics is a finish condition, not a nicety.

```tsx
import { GlassRoot } from "@vitreajs/vitrea-react";

<GlassRoot
  renderer="webgpu"
  colorScheme="auto"
  windowActivation="auto"
  // An app setting, because an engine that cannot query prefers-reduced-transparency
  // honours the preference only through a boolean; "system" is already the default.
  reducedTransparency={settings.reduceTransparency}
>
  <Page />
</GlassRoot>
```

## 2. What the glass is over, and how the runtime learns it

The runtime never pixel-analyses arbitrary DOM. It learns the backdrop one of two ways, and the
choice is the largest single decision about how real the material can be.

- **A texture is the plane itself.** `backdrop={{ kind: "texture", id }}` on a `GlassGroup` moves
  it onto the GPU texture path: the lens bends real pixels (`refraction: "true"`), and the
  analysis is `exact`, read from the pixels the page handed over. The declaration and the pixels
  are two steps because core may hold no `HTMLImageElement`: the prop declares the source, and
  `root.setBackdropTexture(id, { kind: "image" | "canvas" | "video", … })` supplies it, in either
  order. A decoded image is imported once; a canvas or video is re-imported every frame that
  samples it, which is what makes a painted plane live. **Where the texture lands** is the source
  element's own box: an in-document `<img>`, `<canvas>` or `<video>` is measured every read phase
  like a host, and the whole texture is fitted to that box, stretched, with no crop and no aspect
  preservation (`uv = (viewport − box.xy) / box.wh`, clamped outside it). So paint and sample agree
  only when the pixels the element shows are the pixels the texture holds at the box's aspect: a
  canvas the page paints at the box's own size is exact, while an `<img>` under `object-fit:
  cover` shows a crop of the file and the glass reveals the file stretched, and the two disagree
  whenever the file's aspect differs from the box's. A source with no box, an `ImageBitmap`, an
  `OffscreenCanvas`, an element kept out of the document, is placed by
  `setBackdropTexture(id, { …, placement: { kind: "element", element } })` or
  `{ kind: "rect", rect }`; with neither, the old rule applies, the texture covers the viewport
  cover-fit, and the root says so once with `backdrop-texture-unplaced`.
- **The DOM path takes a declaration.** With no texture, the group samples the page through a
  masked `backdrop-filter` proxy, and the material learns the backdrop only from `hint`:
  `{ tone: "light" | "dark" | "mixed", luminance?: 0..1, complexity?: 0..1 }`. The hint decides the
  ink and the body's tone response: the interior level follows the declared backdrop along the
  material's measured curve. On the macOS 26.5 document that response was size-gated to the point
  where a small surface over near-black vanished into it; the macOS 27 default keeps the material
  present over dark content at every size, and small and large surfaces differ little at the dark
  end. A false hint is a false fact either way, and the demo measured 1.6:1 to 3.0:1 label
  contrast from exactly that mismatch. A group with neither texture nor hint never adapts at all,
  on either tier, and the runtime will not guess.
- **A texture group should still declare a hint.** On the WebGPU tier the pixels win and
  `analysis` stays `exact`; on the CSS tier the same group has no pixels and resolves `analysis:
  "none"` unless a hint is declared. The music-player demo measured both: the hint costs the
  texture tier nothing and lifts the CSS tier to `hint` (its `DESIGN.md`, decision log).
- **The vanilla names invert.** In `root.registerGroup({ … })` the tone declaration is the field
  `backdrop` and the source is `backdropSourceId`; React's `hint` prop is the former and its
  `backdrop` prop the latter. Passing `hint:` to `registerGroup` is ignored and the group resolves
  `analysis: "none"` with no error; TypeScript's excess-property check catches it only in an object
  literal.

## 3. Groups: the unit of composition

A group is one backdrop read, one proxy, one blur and one optics pass, shared by its members. It is
also one tint seed and one variant. It is Apple's `GlassEffectContainer`, and it is where a page
decides what reads as one body of material.

- **A toolbar is a group, not a surface.** `GlassToolbar` is plain DOM with `role="toolbar"` and one
  tab stop; the platter the eye sees is its members' fields merging. It creates a group for its
  children (`groupProps` names the id and hint; `group={false}` joins the group in scope), and it is
  deliberately not a glass host, because glass on the container and on its controls is the nesting
  the runtime refuses as `glass-inside-glass`.
- **Splitting a bar is re-grouping it.** Children are partitioned into groups at each
  `<GlassToolbarSpacer kind="fixed" | "flexible" />` and at each item declaring
  `sharedBackground="hidden"`. One `role="toolbar"`, N bodies of material; the roving focus never
  saw the split. That is also how a tinted primary action steps out of a plain bar, since one group
  carries one seed. The partition is structural: decide it with the item set, not per frame.
- **The gap between two groups is one padding, and the runtime derives it.** Each group samples a
  padded box around its shapes, and where one group's padded box covers a neighbour's painted
  shapes the filter applies twice. The safe gap is the larger group's effective `samplingPadding`,
  which the runtime sets at 3σ of the blur it actually draws, so it moves with the surface span and
  rises under Reduce Transparency. `GlassToolbarSpacer` opens that number itself;
  `samplingPaddingFor({ members, material, profile?, cssTierMapping? })` answers it for a layout of
  your own. Never write `samplingPadding` by hand: a pinned value stops following the blur, and one
  the blur has outgrown is raised with a warning. Below the gap the runtime reports
  `proxy-overlap-after-enforcement`.

## 4. Surfaces: shape, size, thickness, variant

`GlassSurface` is the material on one box. It has no intrinsic size and takes no position: it
measures the box your CSS produced once per frame, so a surface with no styles is as tall as its
content and nothing more. Give it a real box.

- **Shape is one of three families.** `radius` (default 12) is a fixed uniform radius; `capsule`
  derives the radius from the measured box, half the shorter side, which forces the corner to an
  exact stadium. `profile` chooses the corner curve: `"continuous"` (the default, fit directly to
  Apple's measured curve), `"circular"`, or a number on the Figma smoothing axis. The two named
  profiles are separate fits, not two points on one axis, so a morph pair must share a reference:
  author `profile={APPLE_LIKE_SMOOTHING}` at both ends of a `GlassMorph` to keep an Apple-like
  corner on the interpolable axis. Radii are uniform in v1; four different values warn with
  `non-uniform-radii`.
- **Concentric shapes.** The vanilla path has a family for it: `shapeFamily:
  "concentric-rounded-rect"` with `concentricOf: { nodeId, inset }` draws a surface as a level set
  of a registered parent in the same group, inset by a fixed distance, so the two are one field
  rather than two shapes that happen to nest. `GlassSegmentedControl` resolves its indicator the
  same way, through geometry's `resolveConcentric` from the track's own shape, because plain
  subtraction is exact only for circular corners and the default corner is Apple's continuous
  curve. A page nesting an ordinary element inside a rounded glass surface has no resolver to
  call and derives the child's radius by hand, parent radius minus the gap, reaching zero when the
  gap exceeds the parent's radius; that is the circular-corner approximation, close enough for a
  `border-radius` on a fill and exact when the parent's `profile` is `"circular"`.
- **Thickness is the lens's reference.** `thickness` defaults to 8 CSS px and the material's
  `lensThicknessReference` is 8, so `thickness` scales the reference's own height law rather than
  being a free number; the demo holds one thickness across a whole size family.
- **The size family must straddle 32 to 96.** The thickness-derived facets (lens depth, occlusion,
  the inner shadow) are gains on one smoothstep of the box's shorter side, exactly zero at or below
  span 32 and saturated at 96. Two other laws keep moving above that band: the body's heavy scatter
  rides its own ramp to span 256, and since 0.20.0 the outer shadow's σ is a line in the casting
  span above a knee and its amplitude grows with it, so a 160 px panel casts a wider, deeper shadow
  than a 96 px one. A family of controls all under 32 shows none of the material's size behaviour;
  one all over 96 shows the shadow and the haze growing but a lens that no longer deepens. The
  demo's 112 / 68 / 40 with radii 26 / 18 / 12 is one instantiation of the method.
- **Variants.** `variant` is `"regular"` (the default) or `"clear"`. A clear surface requires a
  `dimming` policy on its group; core refuses one without it, renders regular and says so.
  `DEFAULT_CLEAR_DIMMING` is `{ scrim: 0.28, direction: "darken" }`. Mixing variants in one group
  warns and changes nothing.
- **A menu is a surface over the app's own primitive.** `GlassSurface asChild` registers the
  element you render instead of a `<div>`, which is how a menu platter is composed over whichever
  accessible menu primitive the app already uses; vitrea ships none and takes no dependency on one.
- **Never a background on a host.** The runtime owns two properties on a registered host,
  `background` and `transform`. The CSS tier writes `background-color: transparent` and
  `background-image: none` inline whenever its declarations change, so a stylesheet fill is simply
  discarded there; on the WebGPU tier the host sits above the optics canvas, so a fill paints over
  the glass, which is the opaque solid Apple names as breaking the material. Colour a surface with
  `tint`; put an image on a child or a pseudo-element. An inline `transform` you set is reported.
- **Declare `color-scheme` on app content inside a plane.** The CSS tier's default ink is
  `light-dark(...)`, resolved against the element's own computed scheme, so a control on light glass
  gets dark-scheme ink whenever the reader's system prefers dark unless the content says which
  scheme its ground is.

## 5. Colour: a seed, not a fill, and the ink that follows it

- **Tint takes any CSS colour, and the colour's alpha is the strength.** `tint="#ff9500"` is a full
  tint; `tint="rgb(255 149 0 / 50%)"` is a half tint, the way `Color.orange.opacity(0.5)` is in
  SwiftUI. The colour is a seed the material tone-maps against the backdrop: an opaque,
  hue-preserving shade whose brightness follows the untinted material's own luminance, per pixel
  on the WebGPU tier and at one backdrop level on the CSS tier. It never moves the material's own
  opacity, so an accessibility preference resolves first and the tinted surface gets more of the
  author's colour, not a different one. Strength 0 is byte-identical to no tint.
- **A group carries one seed.** `<GlassGroup tint>` colours every member that declares none;
  `tint={null}` on a member opts out; a member's own `tint` overrides. Two different seeds in one
  group raise `tint-mixing`, because the WebGPU tier draws the group in the first surface's colour
  while the CSS tier honours each. Give the second colour its own group (in a toolbar,
  `sharedBackground="hidden"` does exactly that).
- **The body carries the backdrop's hue on the WebGPU tier only.** Since 0.21.0 the macOS 27
  documents restore the composited body's chromaticity toward the blurred backdrop's at a held
  luminance; over a neutral backdrop nothing changes. The CSS tier was measured and declined, and
  Reduce Transparency stands the retention down. Design the plane knowing the two tiers differ
  here.
- **Four ink tokens, and what each promises.** Every host publishes `--vitrea-foreground` and its
  `-secondary`, `-tertiary` and `-quaternary`, macOS's label ladder through Apple's vibrancy
  operator: pure black or pure white at a fixed alpha per level, never a hex. The primary is a
  two-token pick and promises no ratio. The secondary holds WCAG 4.5 against the surface the group
  is actually drawing wherever the primary can, and collapses onto the primary where it cannot.
  Tertiary and quaternary carry no body-text floor; quaternary is for separators and decoration.
  There is a band of surface levels where neither ink carries body text (encoded roughly 0.39 to
  0.49); a hint, a thicker or less clear variant, or an authored colour on a child moves a surface
  out of it. Read the tokens with your own value as fallback: `color: var(--vitrea-foreground,
  var(--my-ink))`.
- **Who owns the label.** vitrea's controls set `vibrant` for themselves. On a `GlassSurface
  asChild` the author opts in with `foreground="vibrant"` (`vibrant: true` on the vanilla handle),
  which raises the ink rule's precedence so it survives a reset such as `button { color: … }`; it
  changes no colour, and an application rule naming the element still wins.

## 6. Motion: materialise, morph, press, recede

- **Presence, never opacity.** `present={false}` dematerialises a surface to identity in place: the
  element, its semantics and its ink tokens stay, and only the material's optical terms go. It
  publishes `--vitrea-materialization` in 0..1 on a monotonic 220 ms ease that reverses from its
  current value when interrupted. Fading the host's `opacity` instead creates a backdrop root and
  cuts off sampling. A surface first mounted absent starts at identity with no entrance; keep it
  mounted and flip `present` to animate one.
- **A morph is one host for the pair's whole life.** `GlassMorph open={…}` with a render prop
  interpolates centre, size, radii, smoothing and thickness on interruptible springs, promoting the
  surface as a unit from `plane` to `openPlane` (defaults `base` to `overlay`). Defaults: radius 14
  to 20, thickness 8 to 14, `gap` 8, `placement` one of `below-start`, `below-end`, `above-start`,
  `above-end`. `transition="matchedGeometry"` (the default) is one surface travelling and nothing
  cross-fades; `transition="materialize"` materialises the destination in its own place while the
  source dematerialises and cross-fades only the content, for two ends that are not the same object.
  A materialise pair registers two nodes and reserves `` `${nodeId}-open` `` for the open one. Give
  the morph its own `groupId`, and keep the trigger inside the platter a plain button, since the
  platter is already the material.
- **Press is light and compression at the pointer.** vitrea's controls wire it; a vanilla host
  writes the channels itself on the host's inline style, 0..1, inside `root.subscribe`:
  `GLASS_CHANNEL_PROPERTIES.press`, `.glow`, `.pressX`, `.pressY` (also `.lensStrength`, `.sweep`,
  `.shimmer`, `.materialization`, `.state`). Never a colour swap. Apple scales the response by
  input, more under direct touch and subdued under a pointer; the runtime's press response is the
  same for both today, so a page has no knob for that and should not invent one.
- **The character, in the shipped defaults.** Layout geometry springs at about 420 to 460 ms with
  damping 0.82 to 0.90, slightly underdamped because a trace of overshoot reads as material rather
  than tween. Press compression is faster and looser, 260 ms at damping 0.72, and its release
  bounce is most of what makes a press feel physical; full compression is 1.5 % of scale. Lens
  strength is critically damped at 300 ms so it never over-bends. Glow attacks in 70 ms and decays
  over 320, so light arrives with the finger and lingers. Hover lifts lens to 1.06 and glow to
  0.28; pressed is 1.14 and 1. These live in `packages/motion/src/tunables.ts` as advisory
  constants, overridable as a whole through `GlassRoot profile`.
- **Reduced Motion.** Every spring's damping floors at 1 (no overshoot, no deformation, no shimmer
  travel), morphs shorten to non-elastic interpolation at 0.7 of their response, presence and
  materialise transitions step. Positional continuity is kept: reduced is not none.
- **The pose swap.** When the window loses focus the CSS tier fades the outer shadow out through the
  `box-shadow` transition it writes; the WebGPU tier's two poses are fixed endpoints and it swaps
  in one frame.

```tsx
import { GlassMorph, APPLE_LIKE_SMOOTHING } from "@vitreajs/vitrea-react";

<GlassMorph open={open} groupId="actions" profile={APPLE_LIKE_SMOOTHING}
  openProfile={APPLE_LIKE_SMOOTHING} placement="below-end" aria-label="Actions">
  {({ open }) => (open ? <Menu items={items} /> : <button onClick={toggle}>Actions</button>)}
</GlassMorph>
```

## 7. Reading what drew

Asking for a tier is not getting it, and the readout is how a page finds out which happened.

- `useGlassCapabilities(groupId)` / `root.capabilities(groupId)` returns `GlassGroupState`:
  `configuredSource` (what you declared, never mutated), `activeRenderer`, `samplingBackend`,
  `refraction` (`"true"` only on a texture over WebGPU; the CSS tier is `"none"` by contract, since
  `backdrop-filter` blurs and never bends), `analysis`, `health`, `demotionReason` with its recovery
  named, the CSS-tier readouts `cssBody` (`"two-layer"` or `"collapsed"`), `cssTint`, `cssShadow`,
  and `materialDocument` (`name`, `platform`, `profileKey`, `resolvedMaterialSha256`, `tuned`). It
  is `undefined` until a frame has resolved the group.
- `useGlassWindowActivation()` reports `"active"` or `"inactive"` with `"auto"` already folded;
  `root.material` names the endpoint that drew, its digest and whether an app tuned it. A layout
  that needs a number on its first render reads the SELECTED document from `useGlassRootHandle()`;
  the digest route is the stronger reading and arrives one frame later.
- Choosing CSS is not a fault: `webgpu: "not-requested"` resolves `health: "ok"` with no reason.
  Playwright's default headless shell hands back a software adapter, and a suite that never asks
  for `channel: "chromium"` runs green on the CSS tier while every readout honestly says
  `no-webgpu`; force the CSS tier with `renderer="css"` when you mean to look at it.

## 8. What the runtime does not catch

The runtime refuses nesting, overlap, tint and variant mixing, non-uniform radii, padding floors,
proxy overlap, hosts outside their plane, inline transforms, unparseable tints and backdrop-root
breaks (`filter`, `backdrop-filter`, `opacity` below 1, `mask-image`, `mask-border-source`,
`clip-path`, `mix-blend-mode`, a `will-change` naming any of them; `transform`, `contain`,
`isolation` and `z-index` were measured harmless). These twelve it does not catch, re-checked
against 0.24.0, and each breaks the look:

1. A flat backdrop. The lens has nothing to bend; no diagnostic infers it.
2. A texture whose element shows different pixels than the texture holds: the renderer fits the
   whole source to the element's box, stretched, so an `<img>` under `object-fit: cover` and its
   texture disagree whenever the file's aspect differs from the box's. Paint a canvas at the box's
   size, or size the image to its own aspect.
3. A grid, grain or gradient laid over the backdrop in CSS: it is not behind the glass and is not
   refracted. Paint it into the plane.
4. A surface with no box.
5. A size family entirely under span 32, or entirely over 96.
6. A `background` on a glass host. The CSS tier overwrites it inline with `transparent` and `none`
   whenever its declarations change, so the fill is lost there; the WebGPU tier leaves the host
   above the optics canvas, so the fill paints over the glass as a solid. Neither is the material.
7. No `color-scheme` on app content inside a plane, so `light-dark()` ink flips with the reader's
   system.
8. A transformed ancestor of the plane container: `position: fixed` descendants then resolve
   against it, and a morph platter is one.
9. Portalled content with no landmark. A plane's DOM sits outside every landmark the page wrote.
10. `hint:` passed to `registerGroup` on the vanilla path (the field is `backdrop`).
11. A second `requestAnimationFrame` loop beside `root.subscribe`, or an uncapped delta on a
    backgrounded tab.
12. Assumed contrast. The published ink is a pick, not a ratio, and axe reports "incomplete" over a
    canvas; measure on rendered pixels across the backdrop's phases.

```ts
import { createGlassRoot, GLASS_CHANNEL_PROPERTIES } from "@vitreajs/vitrea-web";

const root = createGlassRoot({ renderer: "webgpu", colorScheme: "auto", devMode: true });
root.registerBackdropSource({ id: "plane", kind: "texture",
  probe: { taint: "clean", textureCompatibility: "compatible" } });
img.addEventListener("load", () => root.setBackdropTexture("plane", { kind: "image", image: img }));
root.registerGroup({ id: "transport", backdropSourceId: "plane",
  backdrop: { tone: "light", luminance: 0.38 } });          // `backdrop`, not `hint`, here
root.plane("base").hostLayer.append(button);                 // must be inside the host layer
const handle = root.registerHost({ host: button, groupId: "transport",
  shapeFamily: "capsule", radii: [22, 22, 22, 22], thickness: 8, vibrant: true });
root.subscribe(({ deltaMs }) => {
  press += (target - press) * Math.min(1, deltaMs / 90);     // one loop, the root's
  button.style.setProperty(GLASS_CHANNEL_PROPERTIES.press, press.toFixed(4));
});
```

## 9. Shipping the aesthetic without vitrea

A stack that cannot take the dependency still owes the same composition: one floating control
layer, capsule and concentric geometry, a designed plane, monochrome controls with one tinted
primary, and the fallbacks drawn as states of the design. What CSS alone can carry is one sharp
`backdrop-filter` plus one `rgba()` layer, a `box-shadow` whose blur grows with the surface's span
(the macOS 27 material's `box-shadow` blur radius is about 4 CSS px at a 44 px control and 35 at a
160 px panel), a 1 px rim, and no refraction at all. The minimum is here so this skill stands on
its own; the fuller recipe with its rules ("Shippable CSS: restrained frosted surface" in
`skills/designer/references/effects-policy.md`) applies when that skill is installed. Write both
fallbacks by hand either way, because nothing reports the tier on this path:

```css
.glass { backdrop-filter: blur(20px) saturate(1.4); background: rgb(255 255 255 / 0.55);
  border-radius: 9999px; box-shadow: 0 8px 12px rgb(0 0 0 / 0.06); }
@supports not (backdrop-filter: blur(1px)) { .glass { background: rgb(246 247 249 / 0.96); } }
@media (prefers-reduced-transparency: reduce) { .glass { background: rgb(246 247 249 / 0.92); } }
```

Under `forced-colors: active` remove the material entirely and keep a `Canvas` fill with a
`CanvasText` border; hierarchy must already be carried by layout, grouping and type.

## 10. One file, a CDN, and `file://`

`npm view @vitreajs/vitrea-web version` reports `0.24.0`, and
`https://esm.sh/@vitreajs/vitrea-web@0.24.0` answered 200 with `application/javascript` on
2026-09-26, so a single HTML file can `import { createGlassRoot } from` that URL with no import
map: esm.sh rewrites the one bare specifier (`@vitreajs/vitrea`) and the dynamic WebGPU chunk.
unpkg serves the raw file and needs an import map. A CDN page needs network to run at all, which
its design law should say plainly.

Such a file boots from `file://` too, because the module it imports is a CDN URL and esm.sh
answers with `access-control-allow-origin: *`; what fails over `file://` is a relative local module
import (`./vitrea.js`), whose opaque origin fails the CORS check. Chrome also treats `file://` as
a secure context, so `navigator.gpu` exists there and the GPU tier is reachable (tested 2026-09-26
in Chrome and Chromium; Firefox and Safari untested). To look at the CSS tier deliberately, pass
`renderer="css"`; do not rely on the URL scheme to select a tier.
