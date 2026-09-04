# Material model

The material model is one of the stance axes: what a surface is made of, and how the interface shows that one thing sits over another. It is decided in the parse step alongside density, criticality, energy, type, color commitment, accent job, ground lightness and ground temperature — not in the craft pass. Read this file while placing the brief on the axes, and again before building if the answer was glass over planes. `references/effects-policy.md` still governs the craft pass: whether any given effect is earned, and the one-material-moment rule that limits how much of a page carries it. This file governs what the surfaces are.

## The axis

A material model answers two questions about every surface in the product at once: what is this made of, and how does a viewer know it is above or below the thing beside it. Printed surfaces are ink on paper, and separation is a rule or a gap. Tonal surfaces are flat planes stepped by lightness. Elevated surfaces lift, and a shadow says how far. Glass surfaces are translucent controls floating over live content, and the material itself carries the separation.

It belongs at stance level because it decides more than a style rule. It sets the component canon — a glass system has planes, platters and portalled menus where a printed system has rules, columns and footnotes. It sets the plane model: whether the page is one surface or a base plus an overlay. It sets how controls sit over content. None of that can be layered onto a finished flat page. The shadow tiers, the border system, the radius tendency and the containment strategy all descend from the material, so changing it late means rebuilding surfaces rather than restyling them.

Decide it from the brief with four questions:

- **Does anything genuinely sit above content that changes underneath it?** A map, a canvas, video, artwork, a live document. If nothing does, glass is already out.
- **Does the product's own world have physical layers?** A spatial workspace, a stack of panels, a sheet drawn up over a scene — as against flat information that happens to be on a screen.
- **Is the surface a printed thing?** A document, a catalogue, an archive, a schedule, a specimen sheet. If the honest metaphor is paper, printed is the answer and every shadow is a lie about it.
- **What are the density, energy and criticality?** Dense and quiet pull toward printed or tonal. Spacious and lively support elevated. Glass needs a live plane regardless of energy — a lively brand is not a reason for it — and at dense or consequential work it is confined to a small persistent control layer while the primary task surfaces stay opaque.

| Position | What a surface is | Separation is drawn by | Shadow tiers | Border system | Radius | Texture | Typical named stances |
|---|---|---|---|---|---|---|---|
| **printed** | Ink on paper. A region of the page, not an object above it. | Rules and whitespace | None | Hairline rules only (1px, low opacity), or none at all | 0–2px | One at the root (grain), never per component | `editorial`, `archival`, `brutalist`, `swiss`, `terminal` (box-drawing rules), `risograph`, `bauhaus`, `luxury-fashion`, `deco`, `vernacular`, `topographic` |
| **tonal** | A flat plane, told apart from its neighbour by lightness | Lightness steps plus 1px low-opacity borders | Floating UI only: popover, modal, drag | 1px, low opacity, on most surfaces | 2–8px | Rare | Precision industrial, Institutional calm, `data-dense`, `minimalist` |
| **elevated** | An object that lifts off the page | Soft shadow encoding height | Four: rest / hover / float / overlay | Optional — the shadow does the work | 8–16px, pills for chips | Rare; product media carries the interest instead | Playful consumer, Contemporary craft commerce (product media only), `y2k-web` (gloss as a period reference, flagged in `DESIGN.md`) |
| **glass over planes** | A translucent control floating over live content, on a managed plane | The material itself, and depth between planes | None on glass — the material carries its own rim and occlusion; conventional surfaces underneath keep their own model | None on a glass host | 12–26px, capsules | In the backdrop, never on the glass | `kinetic`, media and immersive products, spatial-OS-like experiences, map / canvas / video-led workspaces |

The radius and border columns are tendencies, not values. Radius is derived from energy crossed with density, and border weight from material crossed with density, so a quiet dense product at `tonal` sits at the bottom of that 2–8px band while a lively spacious one sits at the top. The material sets the range and the tell; the other axes place the value inside it.

**Choosing between tonal and elevated** is the most common real decision, and the question is not how modern the page should look. It is whether the product has a spatial model worth teaching. If panels genuinely open over other panels, if things are dragged, if an overlay is temporary and the user must feel it is temporary, elevation is doing work. If the screen is a fixed arrangement of regions that are all equally present, tonal is the honest answer and shadows are decoration. A dense operations tool almost always wants tonal even when its register leans expressive.

**Checkable consequences.** Each position leaves a tell that can be checked against the built page:

- **printed** — `box-shadow` appears nowhere except a popover or modal, and preferably nowhere at all. No `backdrop-filter`. The radius scale stops at 2px.
- **tonal** — no shadow on a card at rest; a card is a 1px border plus one lightness step. Shadow tokens exist, and are referenced only by popover, modal and drag.
- **elevated** — every shadow in the stylesheet is one of the four named tiers and each tier means a height. A card that lifts on hover moves one tier; it does not get an invented value.
- **glass over planes** — no `backdrop-filter` and no glass host outside the declared plane surfaces. No glass on rows, lists, tables, or prose. The non-glass surfaces underneath declare their own model and follow it.

**A page has one material model.** A glass toolbar over a tonal dashboard is still `glass over planes` for the floating layer, with tonal beneath: record both lines in `DESIGN.md`, the second as the model the page's own surfaces obey. That is a layered system, not a blend, and the difference is that every surface knows which of the two it belongs to. How much of the page may carry the material is not this axis's call — `effects-policy.md`'s one-material-moment-per-screen rule governs it, and it is a tight limit.

## Holding a model that is not glass

Three positions out of four have no runtime and no capability question, which makes them easier to ship and easier to let drift. Each has its own discipline.

**printed.** Nothing lifts. A hover state is a color change, a rule appearing, or a weight change — never a shadow and never a translate, because paper does not hover. If a genuine overlay is unavoidable, a modal is the one exception and it takes exactly one shadow, recorded in `DESIGN.md` as the exception it is. Texture, if any, is one grain at the root: a grain per card is exactly the reflex `effects-policy.md` names.

**tonal.** The system is a lightness ladder, so decide how many rungs it has and what each one means — page, panel, raised control, hover — and stop at three or four. Past that the steps stop being distinguishable and the ladder becomes noise that reads as inconsistency. Borders and lightness do the same job here, so a surface that has both a border and a step should be the exception, not the pattern.

**elevated.** Name the four tiers and make each mean a height, then use every one; a tier nothing references is a token that will be misused later. Shadows share one light direction across the whole page, and their color derives from the ground rather than being black at low opacity — a shadow on a warm ground is a warm shadow, and the difference between the two is most of why one page looks made and another looks defaulted.

## When glass is earned, and when it is not

Glass is earned when the UI genuinely sits above a changing visual plane and the transparency preserves context. That is `effects-policy.md`'s condition, unchanged, and its list holds: floating controls over a map, canvas, video, 3D scene, or photo-led workspace; a media player with artwork or video as the ground; a bottom sheet that should keep the location beneath it readable; a spatial or immersive operating-system-like experience; a temporary overlay, command palette, inspector, or menu platter.

It is not earned over flat gray app chrome, dense tables, forms, documentation, dashboards, or inventory systems. It is not earned because a card can be made translucent.

Two additions from vitrea's own documentation sharpen the test:

- **Refraction is only legible over detail.** A flat backdrop gives a lens nothing to bend, and the demo rejected an editorial ingredient on exactly that ground (`apps/demo/DESIGN.md` §0). If the ground behind the glass has no high-frequency structure — no texture, no imagery, no live content with edges — the material has nothing to do and the surface is a translucent panel wearing a physics costume.
- **A light backdrop is the harder and more distinctive demonstration.** Every verified competitor demo is dark, because dark is where glass is easy; the demo's ground is a cool near-white instrument window (`#dde6eb`) chosen against that grain, as the harder and unclaimed demonstration. So "glass implies dark mode" is a reflex to catch, not a rule — the ground is still decided by the ground axis, from the product's own scene sentence.

`taste-calibration.md`'s absolute ban stays in force and is not in tension with any of this. The ban is on glass-by-reflex — blur reached for because it looks premium — not on glass. Meeting the conditions above, in writing, is what separates the two.

The three questions `effects-policy.md` asks of any material apply here with specific answers available. What does it mean in this product: the controls are above the content and the content stays visible through them. Why this surface and not everywhere: because exactly one layer floats, and the rest of the page is a conventional material underneath. What remains without it: a frosted surface, and under forced colors a solid one — which is why the tier question below matters more than the shader does. A brief that names glass explicitly still gets glass, per the precedence chain; a brief that names it for a product with no live plane gets it with the tension recorded in one line of `DESIGN.md`, and gets the smallest honest version of it.

## Designing for glass, before any implementation

These are design decisions, made while composing the page. They constrain layout, not just style, and getting them wrong is not fixable in the craft pass.

- **Plane model.** The system has a base plane and one overlay plane. Menus and transient platters live on the overlay; everything else is on base. Arbitrary interleaving with the page's own stacking contexts is outside the contract, so a design that needs three depths of floating chrome needs rethinking, not a third plane.
- **Content-layer prohibition.** Glass goes on the control, never on the row, the list, the table, or the article being read through it. And never on a container *and* its controls — a toolbar is its members' fields merging, not a pane with panes inside it.
- **Labels stay real DOM.** A glass button is a `<button>`: focusable, IME-capable, announced as a button. The material is painted around the element you wrote and placed; it never wraps or replaces it. Design the control first, then let the material find it.
- **No prose over glass.** A surface carries at most one short line or a real control's label. The material never carries information — state, hierarchy and affordance are read from layout, type and color, exactly as `effects-policy.md` requires of every simulated material.
- **One tint seed per group, used sparingly.** Two hues in one sampling group is a defect, not a palette. If a design wants a colored floating surface, that color is the group's seed and it is one color.
- **Surfaces in a plane never overlap.** Overlap across planes is the supported case and is how a morph works; overlap within one plane is an error. Compositions that stack floating chrome need to be redrawn as adjacency or as a plane change.
- **The backdrop must be honest and declared.** Each group declares the tone and luminance of what is actually behind it. This is a fact the design asserts, and asserting it falsely measurably breaks label contrast — the demo recorded 1.6:1 to 3.0:1 from precisely that mismatch. If the backdrop's luminance changes with content (album artwork, a video), pick the honest declaration for the range and measure at its worst phase.
- **The sampling group is a layout unit, so groups need room.** One group is one backdrop read shared by its members, and the runtime derives that group's sampling padding from the blur it actually resolved — at least 3σ — so it moves with the surface's span and reduced-transparency rather than sitting at a fixed number. The safe gap between two groups is therefore at least the *larger* group's effective sampling padding, not the sum of two defaults; below that, one group's padded proxy box covers the other's shapes, the backdrop filter applies twice there, and `packages/platform-web/src/backdrop-proxy.ts` reports `proxy-overlap-after-enforcement`. The demo's 4rem is one product's comfortable margin, not a rule.
- **Size and radius as a family, not per component.** The demo's worked example is a three-step size sweep at 112 / 68 / 40px short side with radii 26 / 18 / 12 and a single shared thickness of 8. That is one instantiation of the method — a small set of sizes, a radius per size, one thickness across all of them — not a table to copy.
- **The backdrop is designed, not inherited.** The lens needs both high and low spatial frequency to have anything to show. The demo's ground is one canvas painting a 32px graticule plus slow chromatic lobes, with the graticule painted *into* the texture rather than laid over it in CSS — a CSS grid on top of the backdrop is not behind the glass and will not be refracted. Where the backdrop is real content (artwork, video, a map), this is already satisfied; where it is a designed field, design it as one image.
- **Portalling costs a landmark.** Content portalled into a plane leaves its position in the document. Re-establishing a landmark region for it is the author's job, and it is a design decision about how the overlay is announced, not a cleanup task.
- **Glass lives in viewport-fixed planes.** A page must not scroll its own glass out from under itself: the demo's answer is an asymmetric split where the narrative column scrolls and the instrument window holding all the glass is `position: fixed`. Any layout where the floating chrome and the scrolling content share a scroll container is a design error, not an implementation detail.

## Shipping it: two paths

**vitrea is the implementation path when the stack can host an ES module; CSS glass when it cannot. `DESIGN.md` records which, and why.** The skill stays runtime-neutral: neither path is a fallback for the other, and the CSS path is a complete answer for a deliverable that cannot take a dependency.

### Path A — vitrea

React, from `@vitreajs/vitrea-react`:

```tsx
import { GlassRoot, GlassGroup, GlassToolbar, GlassButton } from "@vitreajs/vitrea-react";

export function App() {
  return (
    <GlassRoot renderer="webgpu">
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

What v1 gives a designer to compose with: `GlassRoot`, `GlassGroup`, `GlassSurface`, `GlassMorph`, `GlassButton`, `GlassIconButton`, `GlassToolbar`, `GlassSegmentedControl`, `PlanePortal`. A surface has no intrinsic size — position and size are never props, and the runtime measures the box the layout produced. Defaults worth knowing while drawing: `GlassRoot renderer` defaults to `"css"`, `GlassSurface` to radius 12 and thickness 8, `GlassButton` to radius 14. The `clear` variant requires a dimming policy on its group. There is no menu component: a menu is a surface composed over an accessible menu primitive the app chooses, which is a design decision about which primitive, made before the material is applied.

Any DOM without React, from `@vitreajs/vitrea-web`:

```ts
import { createGlassRoot, GLASS_CHANNEL_PROPERTIES } from "@vitreajs/vitrea-web";

const root = createGlassRoot();
root.registerGroup({ id: "controls" });

const button = document.createElement("button");
button.textContent = "Share";
button.style.cssText = "position:absolute;left:120px;top:220px;width:160px;height:44px";
root.plane("base").hostLayer.append(button);

const handle = root.registerHost({
  host: button, groupId: "controls",
  shapeFamily: "fixed-rounded-rect", radii: [14, 14, 14, 14],
});
```

`createGlassRoot()` defaults to the CSS renderer — `options.renderer ?? "css"` in `packages/platform-web/src/root.ts` — so this root never asks for a GPU device; pass `createGlassRoot({ renderer: "webgpu" })` to request the GPU tier, without which the localhost-and-HTTPS note below never applies.

**One API asymmetry, documented in no README.** React's `<GlassGroup hint={...}>` maps to a core descriptor field named `backdrop`. In plain JS the honest backdrop declaration is passed as `root.registerGroup({ id, backdrop: { tone, luminance } })`. Passing `hint:` there is silently ignored and the group resolves to `analysis: "none"` — no error, just a group that never learned what is behind it.

**Single self-contained HTML file.** `<script type="module">import { createGlassRoot } from "https://esm.sh/@vitreajs/vitrea-web@0.6.0"</script>` works with no import map (verified 2026-09-05); esm.sh rewrites the one bare specifier and the dynamic WebGPU chunk import. unpkg serves the raw bare specifier and does need an import map. `navigator.gpu` is undefined outside a secure context, so a page opened from `file://` always gets the CSS tier with `demotionReason: "no-webgpu"` — serve over `http://localhost` or HTTPS to see the GPU tier. And a CDN import means the "self-contained" file needs network to run at all, which `DESIGN.md` must say plainly.

### The fallback is the design, by construction

The runtime resolves a tier per group and reports what it drew. `GlassGroupState` is a closed set (`packages/core/src/state.ts`):

```ts
configuredSource: "texture" | "dom";   // what you declared — never mutated
activeRenderer:  "webgpu" | "css";
samplingBackend: "gpu-texture" | "css-backdrop" | "none";
refraction:      "true" | "approximate" | "none";
analysis:        "exact" | "hint" | "none";
health:          "ok" | "demoted";
demotionReason?: "no-webgpu" | "no-backdrop-filter" | "tainted-source" | "incompatible-texture"
               | "no-texture-supplied" | "device-lost" | "probe-failed" | "governor";
cssBody?:        "two-layer" | "collapsed";
```

`configuredSource` survives demotion, every demotion names a reason, and choosing CSS is not a fault — a root that never asked for WebGPU resolves `activeRenderer: "css"`, `health: "ok"`. The CSS tier converts the same material profile the root carries rather than holding one of its own, so retuning the material moves both tiers together and the fallback cannot drift away from the design. `refraction: "none"` on the CSS tier is by contract: `backdrop-filter` blurs, it never bends. `cssBody` names which body the CSS tier drew: `two-layer` is the full material — a sharp `backdrop-filter` and a heavy one over it, mixed by the renderer's own depth ramp — and `collapsed` is the declared reduction taken when the CSS cost budget cannot afford two layers; it is absent on a WebGPU-tier group and before that group has resolved a frame. Read the state with `useGlassCapabilities(groupId)` or `root.capabilities(groupId)`, and in development keep diagnostics at zero — a page with warnings is not finished.

### Accessibility: what the runtime handles, what is yours

The runtime resolves user preferences itself, strictest wins (`packages/core/src/accessibility.ts`):

| Preference | Consequence |
| --- | --- |
| `prefers-reduced-motion` | No overshoot, deformation, or shimmer travel; morphs non-elastic. Positional continuity kept. |
| `prefers-reduced-transparency` | More frost, less refraction, higher occlusion. |
| `prefers-contrast: more` | Stronger borders, near-monochrome foregrounds, reduced ambient tint. |
| `forced-colors: active` | System colours, borders, no glass at all. |

The first three are overridable per root (`<GlassRoot reducedTransparency increasedContrast="system">`); `forcedColors` has none. `prefers-reduced-transparency` is not Baseline, so where an engine cannot answer, `"system"` resolves false and the runtime emits a diagnostic — the explicit root override is load-bearing, not boilerplate.

The author's job is contrast. The runtime publishes `--vitrea-foreground` (with `--vitrea-tint`, `--vitrea-occlusion`, `--vitrea-border-color`, `--vitrea-blur`) on every host on both tiers, but it is a two-token ink pick, not a contrast calculation, and it promises no ratio. An app that needs a guaranteed ratio sets its own foreground on a child element — never on the host, whose `background` the CSS tier rewrites every frame — and measures on rendered pixels, because axe reports "incomplete" for text over a canvas backdrop (`apps/demo/e2e/contrast.spec.ts`).

### Browser truth

| Engine | WebGPU (texture tier) | CSS tier |
| --- | --- | --- |
| Chromium (Chrome, Edge) | Default-on 113 desktop, 121 Android | Yes — backdrop-proxy equivalence measured byte-exact |
| Safari / WebKit | Default-on from Safari 26 | Yes, manually verified only |
| Firefox / Gecko | Default-on 141 Windows, 145 ARM Mac; still flagged on Linux | Yes, manually verified |

No cross-engine pixel-fidelity claim exists, and none can be made: `backdrop-filter` is a complete no-op in every automatable capture path on Gecko and WebKit while rendering correctly live, so there is nothing to compare. Never write "pixel-identical to Apple" or claim cross-engine parity in a `DESIGN.md` or a hand-off note. What is true is narrower and enough: the material resolves per engine, and the runtime says which tier drew.

### Path B — CSS glass

Choose this when the deliverable must work offline as one file, when the brief rules out dependencies, or when an existing stack cannot load an ES module. Use the "Shippable CSS: restrained frosted surface" recipe in `references/effects-policy.md` and its practical rules (blur 12–24px, a reasonably opaque fill, a small number of surfaces) rather than a second recipe here.

On this path the author writes the fallback by hand — `@supports not (backdrop-filter: blur(1px))` for the solid surface, and a `prefers-reduced-transparency` block — because nothing reports the tier. There is no `health: "demoted"` to read and no diagnostic when the material silently fails, so the solid version has to be written and looked at deliberately, not assumed. The recipe's own occlusion shadow is part of the material, not an entry in the page's elevation ladder: glass surfaces still take no shadow tier.

## Don'ts

- **No glass in the content layer** — not on rows, lists, tables, or the article read through it. The material is for controls above content.
- **No nested glass** — on the control or its container, never both. A platter is its members' fields merging.
- **No glass under a filtered, opacity, mask, or clip ancestor** — engines legitimately differ, and the runtime demotes to CSS rather than trust a support query.
- **No dishonest hints** — a `dark` tone declared over a light ground measurably breaks label contrast.
- **No background color on a glass host** — it is a solid fill and it destroys the material. Use the tint.
- **Tint sparingly, one seed per group** — two hues in one group is a defect.
- **No overlapping surfaces within a plane**, no non-uniform radii, no mixing `regular` and `clear` in one group.
- **No glass over a flat backdrop** — refraction is only legible over detail.
- **Don't pin the sampling padding** — the default is 3σ of the blur actually drawn and it follows accessibility changes.

## What DESIGN.md records for a glass system

```
material model: glass over planes — the transport controls sit over album artwork that
  changes with every track; the artwork is the product's ground, not its decoration.
  Rejected: elevated, which would put an opaque slab over the artwork it exists to show.
path: vitrea, @vitreajs/vitrea-web over an ES module import. The deliverable is one HTML
  file served over localhost, so a module import is available. Needs network to load.
planes: base carries the transport bar and the volume capsule. The queue menu portals to
  the overlay plane and re-establishes its own landmark region there.
groups: "transport" (backdrop: tone dark, luminance 0.18), "queue" (tone dark, 0.22).
  4rem apart — past the larger group's effective sampling padding, which the runtime
  derives from the resolved blur rather than from a fixed default.
surfaces: transport bar radius 26, buttons radius 18, volume capsule; thickness 8 across
  all three. One tint seed per group, unset by default.
tier expectation: webgpu on Chromium over https, css elsewhere and always on file://.
  The CSS tier is the same material without refraction, and it is a complete design.
accessibility: reducedTransparency and increasedContrast set explicitly at the root
  because prefers-reduced-transparency is not Baseline. forced-colors removes the glass.
contrast: labels get their own foreground on a child element, measured on rendered pixels
  across three artwork phases at 4.5:1 for labels and 3:1 for plates.
```

## QA additions for glass

Run these alongside `references/qa-protocol.md`, not instead of it:

1. **Measure label contrast on rendered pixels**, across the backdrop's phases — 4.5:1 for labels, 3:1 for plates. An automated contrast checker reporting "incomplete" over a canvas is not a pass.
2. **Force the CSS tier once** (`renderer="css"`, or open the page from `file://`) and confirm the page is still the design rather than a degraded copy of it.
3. **Check `prefers-reduced-transparency` and `forced-colors` renders.** Under forced colors there is no glass at all; confirm what remains is a working interface.
4. **Zero dev-mode diagnostics.** `glass-inside-glass`, `glass-in-content-layer`, overlap errors and tint warnings are all part of done.
5. **No glass scrolled out from under itself** — scroll every scrollable region to both ends with the floating chrome in view.
6. **Hints match the actual backdrop.** Compare each declared tone and luminance against the ground the group actually sits over, at its lightest and darkest content.
