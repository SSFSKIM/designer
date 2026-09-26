# The vitrea authoring surface at 0.14.0

What a page author can actually do with `@vitreajs/vitrea-web` and `@vitreajs/vitrea-react`, read off
the code rather than off the READMEs, so a design skill can instruct a builder without guessing. Every
claim below carries a file and line. Companion to `docs/research/vitrea-designer-contract.md` (which
predates 0.7.0) and the source of truth for corrections to `skills/designer/references/material.md`,
collected in §7.

**Version reality, and it matters.** The workspace is at `0.14.0` for all three published packages
(`packages/platform-web/package.json:3`). npm's `latest` is **0.13.0**, and `0.12.0` was never
published — the registry holds `0.2.0 … 0.11.0, 0.13.0` (checked 2026-09-09). So a CDN page cannot
pin `@0.14.0`; a workspace page can. Nothing in 0.12–0.14 added a component, prop or option: every
change is material constants reached through `materialProfile` / `setMaterialProfile`
(`packages/platform-web/CHANGELOG.md:3-238`; core and react changelogs are dependency bumps only).

---

## 1. The minimal vanilla page

### 1a. Against the workspace build

`pnpm -r build` emits three files that matter:

| File | Size | Imports |
| --- | --- | --- |
| `packages/platform-web/dist/index.js` | 233 KB | bare `@vitreajs/vitrea` (one specifier, `dist/index.js:1`) |
| `packages/core/dist/index.js` | 44 KB | relative `./chunk-WM2DV3ZD.js`; dynamic `import('./dist-FT6ROOFL.js')` |
| `packages/core/dist/dist-FT6ROOFL.js` | 292 KB | the WebGPU renderer + WGSL, loaded only on `renderer: "webgpu"` |

The dynamic import is the tier split (`packages/core/src/renderer-seam.ts:36-38`): a CSS-tier page
never downloads a shader. Because `platform-web` ships one *bare* specifier, a page served by a plain
static file server needs an import map — there is no other resolution step:

```html
<script type="importmap">
{ "imports": {
    "@vitreajs/vitrea":     "/packages/core/dist/index.js",
    "@vitreajs/vitrea-web": "/packages/platform-web/dist/index.js"
} }
</script>
<script type="module">
  import { createGlassRoot } from "@vitreajs/vitrea-web";
</script>
```

Serve the repo root (`npx serve .`, `python3 -m http.server`) so both paths resolve. React adds three
more externals — `react`, `react-dom`, `react/jsx-runtime` (`packages/react/dist/index.js:1-4`) —
which is why the React path realistically wants a bundler.

### 1b. Against esm.sh

`skills/designer/references/material.md:133` records `https://esm.sh/@vitreajs/vitrea-web@0.6.0`
working with no import map (esm.sh rewrites the bare specifier and the dynamic chunk). The mechanism
has not changed, but the pin must move: the highest publishable pin today is **`@0.13.0`**. I could
not re-verify the fetch — esm.sh returned `408 timeout, the module is waiting to be built` for both
`@0.13.0` and `@0.14.0` on 2026-09-09, which is a cold-cache response, not a 404. Treat the recipe as
unverified-since-0.6.0 and re-check before a skill instructs it. unpkg still needs an import map.

### 1c. The smallest working example

This is `packages/platform-web/e2e/fixtures/vanilla.ts:26-127`, which runs against Chromium, Firefox
and WebKit on every suite run — a tested path, not a snippet. Adding the image backdrop:

```ts
import { createGlassRoot, GLASS_CHANNEL_PROPERTIES } from "@vitreajs/vitrea-web";

const root = createGlassRoot({ renderer: "webgpu", devMode: true });

// The page paints the picture itself. The renderer maps a texture over the WHOLE
// viewport, cover-fit, so the page's copy must be viewport-sized and cover too, or the
// glass reveals a different crop of the same file (packages/react/README.md:283-292).
const img = Object.assign(document.createElement("img"), { src: "/hero.jpg", alt: "" });
img.style.cssText = "position:fixed;inset:0;width:100%;height:100%;object-fit:cover";
document.body.prepend(img);

// Declare the source, then supply the pixels — two steps, because core may hold no
// HTMLImageElement (core/src/scene.ts:151-160; root.ts:441-465).
root.registerBackdropSource({ id: "hero", kind: "texture",
  probe: { taint: "clean", textureCompatibility: "compatible" } });
img.addEventListener("load", () =>
  root.setBackdropTexture("hero", { kind: "image", image: img }));

root.registerGroup({ id: "controls", backdropSourceId: "hero" });

const button = document.createElement("button");
button.type = "button";
button.textContent = "Share";
button.style.cssText = "position:absolute;left:120px;top:220px;width:160px;height:44px";
root.plane("base").hostLayer.append(button);          // MUST be inside the host layer

root.registerHost({ host: button, groupId: "controls",
  shapeFamily: "fixed-rounded-rect", radii: [14, 14, 14, 14], thickness: 8 });

let press = 0, target = 0;
button.addEventListener("pointerdown",  () => (target = 1));
button.addEventListener("pointerup",    () => (target = 0));
button.addEventListener("pointerleave", () => (target = 0));
root.subscribe(({ deltaMs }) => {                     // NOT a second rAF loop
  press += (target - press) * Math.min(1, deltaMs / 90);
  button.style.setProperty(GLASS_CHANNEL_PROPERTIES.press, press.toFixed(4));
});
```

Two omissions that would break it silently: the button must be appended into
`root.plane("base").hostLayer` (registration *checks* containment and reports `host-outside-plane`
rather than adopting the element — `packages/platform-web/src/host.ts:10-19`), and the source must be
registered before a group names it, or `registerGlassGroup` throws `Unknown backdrop source`
(`packages/core/src/scene.ts:91`).

---

## 2. Every author-facing concept

**Root** — `createGlassRoot(options)` (`root.ts:690`), options at `root.ts:215-295`. What a designer
touches: `container` (defaults `document.body`), `zIndex` (default 1000, `planes.ts:92`), `renderer`
(**default `"css"`** — `root.ts:789` reads `options.renderer ?? "css"`, so the GPU tier is opt-in),
`colorScheme` (`"light" | "dark" | "auto"`, default `"light"`; a scheme change is a material change,
not a teardown — `root.setColorScheme`, `root.ts:483-489`), `accessibilityOverrides`, `devMode`
(default true), `diagnosticSink`, `materialProfile`, `autoStart`. `cssTierMapping` is calibration's
seam, not an app knob, and React deliberately does not surface it (`root.ts:283-291`).

**Plane** — exactly two, `"base"` and `"overlay"` (`packages/core/src/planes.ts:16`). Each is a
four-layer sandwich in DOM order: backdrop-proxy → optics canvas → **semantic host DOM** → highlight
canvas (`planes.ts:40-45`). `root.plane(p).hostLayer` is the one layer an app writes into. The whole
root is `position: fixed; inset: 0; pointer-events: none` (`planes.ts:95-99`) — glass is
viewport-fixed by construction, and each registered host has `pointer-events: auto` written back onto
it (`root.ts:2919`). The canvases are `aria-hidden` and `pointer-events: none`, so hit-testing and
the a11y tree pass straight to the real element (`planes.ts:116-119`).

**Group** — `root.registerGroup({ id, backdropSourceId?, backdrop?, estimator?, material?,
foreground?, samplingPadding?, mergeDistance?, morphNamespace? })`; descriptor at
`core/src/scene.ts:177-203`, defaulting `backdropSourceId` to `DEFAULT_DOM_SOURCE_ID` = `"vitrea.dom"`
(`root.ts:213, 2830-2835`). A group is one backdrop read, one proxy, one optics pass, one tint seed.

**Backdrop source** — `registerBackdropSource({ id, kind: "dom" })` or
`{ id, kind: "texture", probe, resolution? }` (`scene.ts:151-167`), then
`root.setBackdropTexture(id, { kind: "image" | "canvas" | "video", … })`
(`renderer-bridge.ts:96-111`) — a no-op on a CSS-tier root, so it can be called unconditionally.
Declaring a texture and never supplying it is honest, not silent: `health: "demoted"`,
`demotionReason: "no-texture-supplied"`. Video and live canvas are re-marked dirty by the frame loop;
a decoded image is imported once (`root.ts:441-465`).

**Hint** — `{ tone: "light" | "dark" | "mixed", luminance?: 0..1, complexity?: 0..1 }`
(`core/src/backdrop-hint.ts:21-27`). **In vanilla the descriptor field is `backdrop`**, not `hint`
(`scene.ts:196`) — and `backdropSourceId`, a different field, names the source. In React the prop
names invert: `hint` is the tone declaration and `backdrop` is the *source*
(`packages/react/src/group.tsx:132-136`). This collision is the single easiest thing to get wrong on
the vanilla path; passing `hint:` to `registerGroup` leaves the group at `analysis: "none"` with no
error. An explicit hint beats an estimator and says so once (`backdrop-hint.ts:98-111`). A texture
group needs no hint — the runtime measures the pixels it was given. A group with neither adapts at
all on neither tier.

**Tint** — any CSS colour the engine can parse, alpha read as strength (`host.ts:47-55`,
`core/src/material.ts:36-71`). A **seed, not a fill**: tone-mapped per pixel against the backdrop.
`null` clears an inherited tint, `undefined` inherits. An unparseable colour renders untinted and
reports `tint-unparseable` (`tint.ts:135-152`). Zero strength collapses to no tint at all
(`material.ts:91-95`).

**Size / radius family** — the size law is one smoothstep on **span = min(width, height)**
(`optics.ts:2552`, `renderer-webgpu/src/material.ts:3094-3100`), from `sizeSpanMin: 32` to
`sizeSpanMax: 96` CSS px (`material.ts:1940-1941`). Below 32 it is *exactly* inert — a small control
renders as if the law did not exist; at and above 96 it saturates. Every thickness-derived facet (lens
depth, occlusion, inner shadow) is a gain on that one number. Radii are uniform in v1: four different
values render differently per tier and warn with `non-uniform-radii` (`root.ts:898-911`). `capsule`
sets the radius to half the shorter side, forcing effective smoothing to 0 and making an exact stadium
(`react/src/shape.ts:68-77`).

**Thickness** — CSS px, default 8 (`host.ts:118-123`, `react/src/surface.tsx:123`), and it is the
reference for the lens: `lensThicknessReference: 8` (`renderer-webgpu/src/material.ts:2102`), so
`thickness` scales the reference's own height law rather than being a free number.

**Toolbar** — React only. `GlassToolbar` is **not** a glass surface: it is plain DOM with
`role="toolbar"`, one tab stop and roving arrows, and it creates a `GlassGroup` for its members whose
merging fields *are* the platter (`react/src/controls/toolbar.tsx:1-25`). `group={false}` puts them in
the group already in scope; `groupProps` is how the group's id and hint are declared.

**Morph** — React only, `GlassMorph` (`react/src/morph.tsx:75-103`). One registered host for the
pair's whole life; what interpolates is `{center, size, radii, smoothing, thickness}`, each on its own
interruptible spring. Defaults: radius 14 → 20, thickness 8 → 14, gap 8, plane `base` → `overlay`
(`morph.tsx:99-103, 135-136`). Both ends must share a corner reference or it throws at the API
boundary — `"continuous"` and `"circular"` are separate fits, so author `APPLE_LIKE_SMOOTHING` at both
ends (`react/src/shape.ts:92-106`).

**Capabilities** — `root.capabilities(groupId)` / `useGlassCapabilities(groupId)` returns
`GlassGroupState` (`core/src/state.ts:47-114`): `configuredSource`, `activeRenderer`,
`samplingBackend`, `refraction`, `analysis`, `health`, `demotionReason?`, plus three CSS-tier
readouts — `cssBody?: "two-layer" | "collapsed"`, `cssTint?: "linear" | "encoded"`,
`cssShadow?: "layer" | "group" | "host"`. Choosing CSS is not a fault: `webgpu: "not-requested"` and
`"pending"` both resolve `health: "ok"` (`capability.ts:11-24`).

**Accessibility** — four preferences, strictest wins (`core/src/accessibility.ts`). Three are
overridable per root (`reducedMotion`, `reducedTransparency`, `increasedContrast`); `forcedColors` is
excluded *in the type system* (`accessibility.ts:59-70`). `prefers-reduced-transparency` is not
Baseline, and where it cannot be queried `"system"` silently resolves false and the runtime warns
`reduced-transparency-undetectable` (`accessibility.ts:290-294`) — so setting it explicitly is
load-bearing.

**Channels** — `GLASS_CHANNEL_PROPERTIES` (`channels.ts:37-46`): `--vitrea-press`, `--vitrea-glow`,
`--vitrea-sweep`, `--vitrea-shimmer`, `--vitrea-lens`, `--vitrea-press-x/y`, `--vitrea-state`. Write
0..1 on the host's inline style; the write phase reads them back at zero layout cost. `--vitrea-shimmer`
is new in 0.11.0 and is 0 at rest, which is what removed the standing bright band every resting
surface used to carry (`platform-web/CHANGELOG.md:246-257`).

**Published tokens** — on every host, both tiers: `--vitrea-foreground`, `--vitrea-tint`,
`--vitrea-occlusion`, `--vitrea-border-color`, `--vitrea-blur` (`css-tier.ts:152-156`). The ink is
delivered as one prepended `:where([data-vitrea-node]) { color: var(--vitrea-foreground) }` rule
(`ink-stylesheet.ts:49`), **not** inline — so any app selector naming the host wins. `background` and
`transform` on the host are still the runtime's; style around them.

---

## 3. The constraints a design must respect

Each checked against code. All nine claims in `references/material.md` §"Designing for glass" hold;
three want sharpening.

1. **One plane model, two planes.** CONFIRMED — `GLASS_PLANES = ["base", "overlay"]`
   (`core/src/planes.ts:16`). Interleaving with foreign stacking contexts is out of contract.
2. **No nested glass.** CONFIRMED — `glass-inside-glass`, severity **error**, checked structurally at
   registration in both directions, and it still fires across planes (`layer-model.ts:137-170`). Its
   sibling `glass-in-content-layer` (warning) fires on list/table roles; an explicit `role` stands it
   down (`layer-model.ts:120-132`).
3. **Surfaces in a plane must not overlap.** CONFIRMED — `same-plane-overlap`, severity error, message
   naming the fix ("put the upper one on the overlay plane") — `core/src/scene.ts:1048-1051`. Touching
   edges are legal; adjacency in a toolbar is the common case (`core/src/planes.ts:107-116`).
4. **One tint seed per group.** CONFIRMED — `checkTintMixing` warns and changes nothing, because the
   GPU tier carries one seed per group while the CSS tier would honour both, so the two tiers would
   disagree (`core/src/material.ts:195-215`). Untinted members are not a mix.
5. **Honest backdrop hints.** CONFIRMED, and sharpened. Out-of-range values clamp with a warning
   (`backdrop-hint.ts:69-91`). The demo's own note records that a `dark` tone left behind a light
   ground measured 1.6:1–3.0:1 on control labels (`apps/demo/src/site/Stage.tsx:71-95`). Two things
   `material.md` does not say: a **texture** group should declare *no* hint and let the runtime read
   the pixels (`apps/demo/src/site/StageBackdrop.tsx:83-85`), and a group with neither hint nor
   texture does not adapt at all — the runtime will not guess a backdrop it has not been shown.
6. **Sampling padding.** CONFIRMED. There is no fixed default in practice: when a group declares none,
   the runtime uses 3σ of the blur it actually resolved for that group's **largest member**
   (`proxy-geometry.ts:153`, `optics.ts:3885-3890`, `root.ts:1802-1813`). Core's
   `DEFAULT_GROUP_SAMPLING = 24` is an advisory that only applies where the platform layer is not
   driving. A declared padding below 3σ is raised with `sampling-padding-below-3-sigma`
   (`proxy-geometry.ts:277-283`), and `mergeDistance` must then be ≥ the raised value.
   **The safe gap between two groups is one padding, not two**: the predicate is a padded box against
   the neighbour's *painted region* (`backdrop-proxy.ts:188-216`), and the message says "at least the
   larger group's effective samplingPadding". Below that, `proxy-overlap-after-enforcement`.
7. **Viewport-fixed planes.** CONFIRMED — `position:fixed;inset:0` on the root
   (`planes.ts:95`). A page that scrolls its glass out from under itself is a design error.
8. **Labels real DOM.** CONFIRMED — registration never wraps, replaces, reparents or re-contents the
   element; the one property vitrea takes is `transform`, and an inline one you set is reported
   (`host.ts:1-43`). A glass button is a real `<button>`.
9. **Prose over glass.** This is the demo's own law (`apps/demo/DESIGN.md:189-192` — "the material
   never carries information"), not a runtime check. Correctly attributed in `material.md`.

Add one the reference does not list: **no backdrop-root trigger on any ancestor of the root's
container.** `filter`, `backdrop-filter`, `opacity < 1`, `mask-image`, `mask-border-source`,
`clip-path`, `mix-blend-mode` and a `will-change` naming any of them re-root the proxy's backdrop and
demote the group with `probe-failed` (`probe/backdrop-root.ts:65-85`; the audit walks from the plane
root upward, `root.ts:1269-1278`). `transform`, `translate3d`, `contain`, `isolation`, `z-index` and
`will-change: transform` were **measured harmless** and are deliberately not on the list
(`backdrop-root.ts:22-27`) — worth knowing, because the intuitive list over-triggers.

---

## 4. What the CSS tier draws, and what a `file://` page gets

**The doctrine is that the fallback is the design** (`css-tier.ts:1-12`): the surface always paints a
real tint and a real border and never relies on the blur for contrast, so a group whose
`backdrop-filter` silently no-ops still reads as a legible surface. The tier holds **no optical number
of its own** — every value is derived from the same material profile the WebGPU tier reads
(`css-tier.ts:76-83`), so retuning the material moves both.

Since W16 the tier puts three children on each host, all `aria-hidden`, `pointer-events: none`, at
negative z-index under the host's own content (`css-tier.ts:36-54`): **L1** the sharp
`backdrop-filter` plus `saturate()`; **L2** the heavy `backdrop-filter`, whose share is carried by a
raster mask where the engine composes one and a flat opacity where it does not; **L3** the tint, press
glow, rim and outer shadow, above both filters. The tier builds **no proxy** — which is exactly why
`probe-failed` can demote *to* it.

What it cannot render, stated where the code states it:

- **`refraction: "none"`, by contract** — `backdrop-filter` blurs, it does not bend
  (`core/src/capability.ts:31-34`).
- **No directional rim.** One inset shadow cannot vary its brightness around a contour, so the CSS
  tier's rim is one number: it takes 0.13.0's lit-edge *exponent* but not 0.14.0's corner-to-corner
  field (`platform-web/CHANGELOG.md:135-146, 63-68`).
- **No outer-shadow lift** — drawing it would need a *copy* of the backdrop, and the moment this tier
  wants one it stops being demotable-to (`css-tier.ts:20-22`).
- **`cssBody: "collapsed"`** — the declared degradation when the cost budget cannot afford two layers,
  and it is reported rather than hidden (`core/src/state.ts:57-74`).

**A `file://` page.** Two separate consequences, and only one is about vitrea. `navigator.gpu` is
undefined outside a secure context, so the GPU tier is unreachable and every group resolves
`activeRenderer: "css"` (`packages/core/README.md:493-497`). But before that: a browser will not load
an ES module over `file://` at all — module fetches are CORS-checked and `file://` is an opaque
origin. So the vitrea path on `file://` does not degrade to the CSS tier, it fails to boot.
`references/material.md:224` currently offers "open the page from `file://`" as a way to force the CSS
tier; use `renderer="css"` (the default anyway) instead.

---

## 5. The demo, as a worked example of a page designed for glass

Three pages, and only two are governed by `apps/demo/DESIGN.md` — its scope is the public site at `/`
and, by §9, the laws page; `src/App.tsx` is the acceptance playground and is explicitly outside it
(`DESIGN.md:44-46`).

**The backdrop is painted, not sourced.** There is no image asset anywhere: the ground is a `<canvas>`
registered as a texture (`src/site/StageBackdrop.tsx`), because DESIGN.md forbids external requests
outright (`DESIGN.md:187-188`). It carries **two spatial frequencies on purpose** — broad chromatic
lobes for the lens to bend, a 32 px graticule for the high-frequency half
(`StageBackdrop.tsx:130-131, 204, 225`) — and the graticule is painted *into* the texture rather than
laid over it in CSS: "a graticule drawn outside it would sit over the glass unbent, and the page would
be showing a lens that misses half its own backdrop" (`StageBackdrop.tsx:5-15`). The ground colour is
pinned to its token (`#dde6eb` = `--stage-0`) with its luminance written out longhand so a reader can
check it (`StageBackdrop.tsx:70-95`); the lobes composite with `multiply` and their alpha has a floor,
because label contrast over the glass is measured on rendered pixels against it
(`StageBackdrop.tsx:133-155`). The ground is **light on purpose**: "every verified competitor demo is
dark, because dark is where glass is easy" (`DESIGN.md:31-33`).

**The size sweep** is three plates at span 112 / 68 / 40 px with radii 26 / 18 / 12 and **one shared
thickness of 8** (`src/site/Stage.tsx:129-135`). Three rather than two because the law is a curve and
"two points cannot show a curve" (`Stage.tsx:479-483`); the three straddle the shipped band — 40 sits
just past the floor of 32, 68 mid-curve, 112 past the ceiling of 96. The thickness is the sweep's
*control variable*, declared once and emitted as `data-sweep-thickness` so the suite can catch a
drift. The boxes are `px`, not `rem`, and `height`, not `min-height`, so a reader's text size or a
long label cannot move a plate out of the band it was chosen to sit in (`site.css:644-676`). All three
are one group over one texture, so the comparison is over identical backdrop pixels.

**The plane split.** Almost everything is on `base`, hoisted by *one* `PlanePortal` per plane so the
stage's layout survives the move — "without it every surface would portal for itself and the geometry
would scatter to the plane root" (`src/site/Site.tsx:679-686`). The only `plane="overlay"` surface in
the whole demo is the laws page's glass-over-glass pane (`src/laws/LawsStage.tsx:259-278`), and it is
on a separate plane rather than nested inside the base surface's content precisely because that is the
composition the layer model allows (`src/laws/Laws.tsx:519-523`). The morph promotes itself.

**Groups.** Seven on the site, seven on the laws page, and **not one declares `samplingPadding` or
`mergeDistance`**. §9.1 is satisfied spatially instead, by a 4rem gap between groups
(`site.css:483-498`), and DESIGN.md is honest that 4rem is one product's comfortable margin. Texture
groups declare no hint; DOM groups declare `{tone, luminance}` moving together with the page's own
scheme (`Stage.tsx:97-100`). The morph gets its own `groupId` — an unplaced platter still joins its
group's sampling union and would drag it toward the plane origin (`DESIGN.md:209-228`).

**The morph's trigger is a plain `<button>`, not a `GlassButton`** — "the platter around it is already
the glass surface, and nesting a second one inside it is the same-plane overlap X1 forbids"
(`src/ActionsMenu.tsx:186-190`). That single line is the clearest statement of the nesting rule
anywhere in the repo.

---

## 6. Build mistakes the runtime will not catch

The runtime catches nesting, overlap, tint mixing, variant mixing, non-uniform radii, padding floors,
proxy overlap, hosts outside their plane, inline transforms, unparseable tints and backdrop-root
breaks. It does **not** catch these, and each one breaks the look:

1. **A flat backdrop.** The lens has nothing to bend and the surface is a translucent panel. No
   diagnostic exists — the layer model deliberately declines to infer it (`layer-model.ts:44-50`).
2. **A texture the page paints at a different crop.** The renderer maps a texture over the *whole
   viewport*, cover-fit; an `<img>` sized to a region samples a different crop of the same file, and
   the mismatch reads convincingly as a lensing artefact (`packages/react/README.md:283-292`).
3. **A CSS overlay on the backdrop instead of inside it.** A grid, grain or gradient laid over the
   texture is not behind the glass and will not be refracted.
4. **A surface with no box.** Position and size are never props; a `<GlassSurface>` with no styles is
   as tall as its content and nothing more (`react/src/surface.tsx:26-36`).
5. **Every control below span 32.** The size law is exactly inert there
   (`renderer-webgpu/src/material.ts:3086-3090`) and 0.14.0's rim grading is flat by construction
   (`platform-web/CHANGELOG.md:10-21`), so a sweep entirely under 32 demonstrates nothing.
6. **`background` on a glass host.** The CSS tier writes the shorthand every frame, so a
   `background-image` is clobbered — put it on a pseudo-element. A solid fill is also the failure
   Apple names by name.
7. **No `color-scheme` on app-authored content inside a plane.** The CSS tier writes its foreground as
   `light-dark(...)`, resolved against the element's own computed scheme, so a control on light glass
   gets light ink whenever the reader's system prefers dark (`apps/demo/DESIGN.md:70-75`).
8. **A transformed ancestor of the plane container.** `position: fixed` descendants resolve against it
   instead of the viewport, and a morph platter is exactly such a descendant (`site.css:483-488`).
9. **Portalled content with no landmark.** A plane's DOM sits outside every landmark the page wrote;
   giving it a `<nav>` or named region is the author's job (`react/src/plane-portal.tsx:14-17`).
10. **`hint:` passed to `registerGroup`.** Silently ignored on the vanilla path — the field is
    `backdrop` (§2). TypeScript's excess-property check catches it in an object literal and nothing
    catches it otherwise.
11. **Un-capped `deltaMs`, or a second `requestAnimationFrame` loop.** A backgrounded tab returns an
    arbitrarily large first step; a second loop means two wake-ups per frame with no declared ordering
    between them (`root.ts:531-554`).
12. **Assuming contrast.** The published ink is a two-token pick, not a ratio calculation, and axe
    reports "incomplete" over a canvas backdrop — a ratio has to be measured on rendered pixels across
    the backdrop's phases (`apps/demo/DESIGN.md:193-197`, `apps/demo/e2e/contrast.spec.ts:4-8`).

---

## 7. What `references/material.md` gets wrong

Of roughly sixty checkable claims, one is contradicted, one is stale, one is incomplete, and two want
sharpening. Everything else — the two-plane model, the overlap error, the nesting and content-layer
diagnostics, the tint-seed rule, the hint contract and its React/vanilla asymmetry, the 3σ padding
derivation, viewport-fixed planes, real-DOM labels, and every numeric constant and API name it cites —
is confirmed, in several places verbatim against the source comments.

- **Line 174 — CONTRADICTED. The Gecko CSS-tier cell says "Yes, manually verified".** The conformance
  table has Gecko at `rasterisesBackdropFilter: "unverified"`
  (`platform-web/src/probe/conformance-table.ts:200-201`), and the module comment says so in as many
  words: "The WebKit 18.6 row is exactly such a closure… **Gecko's gate is still open**"
  (`conformance-table.ts:37-39`). The adjacent Safari cell ("Yes, manually verified only") *is*
  correct — that row carries a labelled manual pass. The Gecko cell should read *unverified*, and the
  distinction matters: `"unverified"` is not `"no"`, it is capture-path blindness, and a skill that
  reports it as verified is claiming evidence the repo deliberately declined to claim.
- **Line 133 — the esm.sh pin `@0.6.0`.** Eight minors behind, and `@0.14.0` cannot be pinned at all
  because it is unpublished (npm `latest` is 0.13.0; 0.12.0 was skipped). The recipe was last verified
  2026-09-05 and I could not re-verify it (esm.sh 408, cold cache).
- **Lines 137-149 — the `GlassGroupState` block is incomplete.** It lists `cssBody` but not
  `cssTint?: "linear" | "encoded"` or `cssShadow?: "layer" | "group" | "host"`, both of which are on
  the record now (`core/src/state.ts:75-113`). A skill that tells a builder to read the state should
  name all three.
- **Line 224 — "force the CSS tier … or open the page from `file://`".** A `file://` page cannot load
  an ES module at all, so this does not force the CSS tier; it prevents the page booting. Drop the
  `file://` half; `renderer="css"` is the whole answer. Line 211's `"css elsewhere and always on
  file://"` in the DESIGN.md template has the same problem.
- **Line 131 — the API asymmetry can be sharper.** It is right that React's `hint` is core's
  `backdrop`. What it does not say is that React *also* has a prop literally called `backdrop`, and it
  means the opposite thing (the texture source). The vanilla equivalent of React's `backdrop` is
  `backdropSourceId`. Stating both halves is what prevents the mistake.

Two things worth adding rather than correcting. **Line 74's sampling-padding advice is right and the
reason is better than stated** — the overlap predicate compares a padded box to the neighbour's
*painted* region, so one padding of clearance is provably enough (measured byte-identical zero at that
separation), which is why the safe gap is the larger group's padding and not the sum. It is also
right against the demo, whose own CSS comment still describes 4rem as "the separation two 24px
sampling paddings need" (`apps/demo/src/site/site.css:487`) — the sum, not the larger. And **the hint
carries a third field, `complexity` (0..1)**, that `material.md` never names
(`core/src/backdrop-hint.ts:26`); `luminance` is likewise optional, so `{ tone }` alone is a legal
hint and a weaker one.

Unrelated staleness found on the way: `apps/demo/src/site/Stage.tsx:580-584` says the runtime writes
the host's `color` inline "so an app rule on the host loses to it". That has not been true since the
ink moved to a prepended `:where()` rule (`platform-web/src/ink-stylesheet.ts:1-49`); an app rule on
the host now wins. The demo's wrapper span is still good practice, but its stated reason is wrong.
