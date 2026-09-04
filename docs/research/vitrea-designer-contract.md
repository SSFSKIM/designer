# vitrea, for a designer — the contract distilled

> Research note, 2026-09-05. Read from this repository's own sources and verified live where
> stated. Source for `skills/designer/references/material.md`. Not loaded at plugin runtime.
> Sources: `packages/core/README.md`, `packages/react/README.md`, `packages/platform-web/README.md`,
> `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md` (rendering contract, core
> model, backdrop & analysis contracts), `docs/doperpowers/specs/c9a-fidelity-claims.md`,
> `apps/demo/DESIGN.md`, `apps/demo/src/site/*`.

## 1. The mental model

- **Root.** `GlassRoot` (React) / `createGlassRoot()` (plain JS) owns one runtime, one scheduler,
  and the managed planes. Planes attach to `document.body` by default, `position: fixed`.
- **Plane sandwich.** Per plane, paint order is: page content → backdrop-proxy layer → optics
  canvas (glass body) → **semantic host DOM** → highlight canvas. The label sits *inside* the
  sandwich, which is why the next law holds.
- **Labels stay real DOM.** `registerHost` binds an element you created and placed; it never
  wraps, replaces, or reparents it. A `GlassButton` is a `<button>` — focusable, IME-capable,
  announced as a button. The runtime owns exactly two properties on your host: `transform`
  (during press/morph) and `background` (the CSS tier rewrites the shorthand every frame — put
  your own background-image on a pseudo-element).
- **Group = the sampling unit.** One `GlassGroup` is one backdrop read: one proxy, one blur, one
  optics pass, shared by every member. Also one author tint seed per group.
- **Surface = the material on one box.** `GlassSurface` has **no intrinsic size**. Position and
  size are never props; vitrea measures the box your CSS produced once per frame.
- **Backdrop hints must be honest.** vitrea never pixel-analyses arbitrary DOM.
  `hint={{ tone, luminance?, complexity? }}` is the one mechanism. It decides the foreground ink
  *and* the material's own tone (a dark backdrop's tone is taken on, size-gated, below ~0.16
  linear luminance). A dishonest hint is a declared fact that is false: the demo measured
  1.6:1–3.0:1 label contrast from exactly that mismatch (`apps/demo/src/site/Stage.tsx`, the
  `STAGE_HINT` comment).
- **Content-layer prohibition.** Apple states it as a prohibition: glass on the button, not the
  row; on the toolbar's controls, not on the toolbar *and* its controls; never on a list or
  table. Dev-mode diagnostics `glass-inside-glass` and `glass-in-content-layer` enforce the
  structurally decidable half.
- **No overlap within one plane** (dev-mode error). Overlap *across* planes is the supported
  case and is what `GlassMorph` uses.
- **One overlay plane.** v1 ships exactly two planes (base + one overlay); menus portal
  internally to overlay. Arbitrary interleaving with foreign stacking contexts is out of contract.
- **Portalling costs a landmark.** Content portalled into a plane leaves its DOM position;
  re-establishing a landmark region is the author's job.

## 2. Two tiers, and the runtime reports what it drew

`GlassGroupState` (spec, backdrop & analysis contracts; `packages/core/src/state.ts`) is a closed
set of legal states:

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

`configuredSource` survives demotion; every demotion names a reason; and **choosing CSS is not
a fault** — a root that never asked for WebGPU resolves `activeRenderer: "css"`, `health: "ok"`.
Read it with `useGlassCapabilities(groupId)` or `root.capabilities(groupId)`. The CSS tier has
its own renderer and *converts* the material the root carries rather than holding one of its own,
so retuning moves both tiers together. `refraction: "none"` on the CSS tier is by contract:
`backdrop-filter` blurs, it never bends. `cssBody` names which body the CSS tier drew:
`two-layer` is the full material — a sharp `backdrop-filter` and a heavy one over it, mixed by
the renderer's own depth ramp — and `collapsed` is the declared reduction taken when the CSS
cost budget cannot afford two layers; absent on a WebGPU-tier group and before that group has
resolved a frame.

## 3. Accessibility: runtime vs. author

Runtime (`packages/core/src/accessibility.ts`), strictest preference wins:

| Preference | Consequence |
| --- | --- |
| `prefers-reduced-motion` | No overshoot, deformation, or shimmer travel; morphs non-elastic. Positional continuity kept. |
| `prefers-reduced-transparency` | More frost, less refraction, higher occlusion. |
| `prefers-contrast: more` | Stronger borders, near-monochrome foregrounds, reduced ambient tint. |
| `forced-colors: active` | System colours, borders, **no glass** at all. |

First three overridable per root (`<GlassRoot reducedTransparency increasedContrast="system">`);
`forcedColors` has no override. `prefers-reduced-transparency` is not Baseline — where an engine
cannot answer, `"system"` resolves false and the runtime emits a diagnostic; the explicit override
is load-bearing.

**Author's job.** The runtime publishes `--vitrea-foreground` (plus `--vitrea-tint`,
`--vitrea-occlusion`, `--vitrea-border-color`, `--vitrea-blur`) on every host on both tiers,
through a zero-specificity `:where([data-vitrea-node])` rule. It **is not a contrast calculation
and promises no ratio** — it picks between two ink tokens. An app needing a guaranteed ratio sets
its own foreground. axe reports "incomplete" for text over a canvas backdrop, so contrast over
glass must be measured on rendered pixels (`apps/demo/e2e/contrast.spec.ts` samples across
backdrop phases, holding 4.5:1 labels / 3:1 plates). Style a *child* element, not the host.

## 4. v1 primitives

From `packages/react/src/index.ts`: components `GlassRoot`, `GlassGroup`, `GlassSurface`,
`GlassMorph`, `GlassButton`, `GlassIconButton`, `GlassToolbar`, `GlassSegmentedControl`,
`PlanePortal`; hooks `useGlassCapabilities`, `useGlassAccessibility`, `useGlassDiagnostics`,
`useGlassMotionProfile`, `useGlassTicker`, `useGlassRoot`, `useToolbarItem`. **No menu
component** — v1's menu is composed as `GlassSurface asChild` over an accessible menu primitive the
app chooses (`apps/demo/src/ActionsMenu.tsx`).

Minimal props: `GlassRoot renderer` (default `"css"`); `GlassGroup id` + `hint`; `GlassSurface
radius` (default 12) / `thickness` (default 8) / `capsule` / `variant` / `tint`. `GlassButton`
defaults radius 14, thickness 8. `clear` variant *requires* a `dimming` policy on its group
(`DEFAULT_CLEAR_DIMMING`).

React (`packages/react/README.md`):

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

Plain JS (`packages/platform-web/README.md`; executed version
`packages/platform-web/e2e/fixtures/vanilla.ts`):

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

`createGlassRoot()` defaults to the CSS renderer (`options.renderer ?? "css"`,
`packages/platform-web/src/root.ts`), so this root never asks for a GPU device; pass
`createGlassRoot({ renderer: "webgpu" })` to request the GPU tier, without which the
localhost-and-HTTPS caveat in §5 never applies.

**API asymmetry not in any README:** React's `<GlassGroup hint={...}>` maps to the core
descriptor field named `backdrop` (`packages/react/src/group.tsx:221`,
`packages/core/src/scene.ts:199`). In plain JS pass
`root.registerGroup({ id, backdrop: { tone, luminance } })`. Passing `hint:` there is silently
ignored and the group resolves to `analysis: "none"` (hit live).

## 5. Single self-contained HTML: verified working (2026-09-05)

Not documented in the repo. Verified live:

- `npm view @vitreajs/vitrea-web` → `0.6.0`, dependencies `{ "@vitreajs/vitrea": "^0.6.0" }`.
  One runtime dependency, itself dependency-free; everything else bundled at publish
  (`packages/platform-web/tsup.config.ts`, `noExternal: [/^@vitrea\//]`).
- All three packages are `"type": "module"`, ESM-only, `exports["."]` → `dist/index.js`.
- `https://esm.sh/@vitreajs/vitrea-web@0.6.0` returns 200 and rewrites the one bare specifier
  and the dynamic WebGPU-renderer chunk import to resolvable URLs. **No import map needed.**
  unpkg serves the raw file with a bare `from '@vitreajs/vitrea'` and *does* need an import map.
- Smoke test, single HTML file, no bundler, headless Chrome over `http://localhost`: root
  mounted, group registered, host bound; resolved
  `{configuredSource:"dom", activeRenderer:"webgpu", samplingBackend:"css-backdrop",
  refraction:"approximate", analysis:"hint", health:"ok"}`; `--vitrea-foreground` published.

Caveat: `navigator.gpu` is undefined outside a secure context, so a file opened from `file://`
gets `demotionReason: "no-webgpu"` and the CSS tier, always. Serve over `http://localhost` or
HTTPS to see the GPU tier. "Self-contained" and "CDN" are in tension — the page needs network.

## 6. Browser support truth

| Engine | WebGPU (texture tier) | CSS tier |
| --- | --- | --- |
| Chromium (Chrome, Edge) | Default-on 113 desktop, 121 Android | Yes — backdrop-proxy equivalence measured byte-exact, 122 capture variants |
| Safari / WebKit | Default-on from Safari 26 | Yes, **manually verified only** |
| Firefox / Gecko | Default-on 141 Windows, 145 ARM Mac; still flagged on Linux | Yes, manually verified |

`backdrop-filter` renders as a **complete no-op in every automatable capture path** on Gecko and
WebKit while rendering correctly live, so no cross-engine pixel-fidelity claim exists. Every
fidelity number is scoped to Chromium 151 / Apple Metal-3 / sRGB / 1× against macOS 26.5, and
nothing claims pixel-identity.

Chromium 152 defect: `backdrop-filter` is dropped on an element with `clip-path: path()` when an
ancestor has both non-`visible` overflow and a `border-radius`. Unreachable with the default
mount; reachable only with a custom `container` inside a rounded, clipping card. Dev mode emits
`engine-known-defect` (warning, never a demotion).

## 7. What the docs tell designers not to do

1. No glass in the content layer — not on rows, lists, tables, or the article read through it.
2. No nested glass — glass on the control *or* its container, never both. `GlassToolbar` is
   deliberately not a surface; the platter is its members' fields merging.
3. No glass under a filtered / opacity / mask / clip ancestor — engines legitimately differ; the
   startup probe demotes to CSS rather than trusting a support query.
4. No dishonest hints — a `dark` tone over a light ground measurably breaks label contrast.
5. No background colour on a glass host — it is a solid fill and breaks the material. Use `tint`.
6. Tint sparingly, one seed per group — two hues in one group is a dev-mode warning.
7. Don't overlap surfaces in a plane; don't use non-uniform radii (v1); don't mix `regular` and
   `clear` in one group.
8. Don't put glass over a flat backdrop — `apps/demo/DESIGN.md` §0 rejected an editorial
   ingredient as "a flat backdrop with nothing for a lens to bend". Refraction is only legible
   over detail.
9. Don't pin `samplingPadding` — the default is 3σ of the blur actually drawn and follows
   accessibility changes.

## 8. The demo as a worked example

`apps/demo/DESIGN.md` and `apps/demo/src/site/*`:

- **The backdrop is deliberately light**: a cool near-white instrument window (`#dde6eb`), chosen
  against the grain — "every verified competitor demo is dark, because dark is where glass is
  easy; the harder and unclaimed demonstration is daylight."
- **The backdrop is a registered texture painted by one canvas** (`StageBackdrop.tsx`): a 32px
  graticule plus slow chromatic lobes, giving the lens both high and low spatial frequency. The
  graticule is painted *into* the texture, not laid over it as CSS.
- **Layout is a 45/55 asymmetric split**: the narrative column scrolls, the instrument window is
  `position: fixed`, and all glass lives inside it.
- **Sizing and grouping** (`Stage.tsx`): a three-step size sweep at 112 / 68 / 40 px short side,
  radii 26 / 18 / 12, one shared thickness of 8; three separate sampling groups at 4rem gaps.
  The floor is not a fixed 48px: the runtime derives each group's `samplingPadding` from the
  blur it resolved (≥ 3σ), so it moves with surface span, DPR, and reduced-transparency, and
  the safe gap is at least the *larger* group's effective padding — under it, the proxy boxes
  overlap and `backdrop-proxy.ts` reports `proxy-overlap-after-enforcement`. 4rem is this
  demo's comfortable margin, not a rule.
- **Its own hard don'ts:** no glass or `backdrop-filter` on page chrome; **no prose over glass** —
  a surface carries at most one short line or a real control's label, "the material never carries
  information"; no invented fidelity numbers; zero dev-mode diagnostics is part of done.
