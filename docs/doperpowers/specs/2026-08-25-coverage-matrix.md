# vitrea coverage matrix — the native Liquid Glass system versus what v1 ships

Child of [the vitrea composite spec](./2026-08-24-vitrea-liquid-glass-design.md).
Binding sections: §v1 scope, §Out of scope (v1 cut list), §Material variants,
§Accessibility policy, §Geometry, §Motion, §Calibration harness & methodology,
Decision Log #27 and #30 (the published pair is unscoped **`vitrea`** and
**`vitrea-react`**). Per-cell fidelity numbers are quoted from
[c9a-fidelity-claims.md](./c9a-fidelity-claims.md).

This document answers one question and refuses to answer it kindly: **of the full
native SwiftUI / UIKit / AppKit Liquid Glass system, how much does vitrea v1
actually cover, and where exactly does the coverage stop?** It is not a progress
report. Where vitrea has nothing, the row says so; where the composite spec never
considered the native item at all, §6 names it.

---

## 0. How to read this, and how well each layer is sourced

**Status vocabulary** — one value per row, no hedging:

| status | meaning |
| --- | --- |
| `replicated+measured` | vitrea implements it **and** a calibration cell or a pixel/golden test measures it against something. The cell or test is named. |
| `replicated, unmeasured` | vitrea implements it and non-pixel tests cover its mechanics, but no measurement against the reference exists. Code/test named. |
| `partial` | one half is present. The row says which half. |
| `excluded by decision` | a recorded ruling puts it outside v1. The Decision Log entry or §Out of scope line is named. |
| `absent, undecided` | vitrea has nothing, and no vitrea document has ruled on it. **These are the rows that matter.** |

**Sourcing quality of the native side**, stated per layer because it is not
uniform:

| layer | sourcing | confidence |
| --- | --- | --- |
| §1 Material API surface | Apple DocC JSON read symbol-by-symbol (`developer.apple.com/tutorials/data/documentation/…json`), plus WWDC25 session transcripts (219, 284, 323, 356) and the three June-2026 framework changelogs. Availability annotations were inspected directly, so iOS 26 versus iOS 27 additions are separable. | **High.** Named negatives (`glassEffect(_:in:isEnabled:)` 404s, no UIKit morph-by-ID exists) are verified negatives, not gaps in searching. |
| §2 Component families | Apple's **"Adopting Liquid Glass"** technology overview carries the only authoritative named lists; most per-component HIG pages say nothing about glass and several have not been revised since 2022–2023. Cross-checked against per-page HIG DocC JSON for ~172 HIG pages and the WWDC26 session catalog (138 entries enumerated). | **High for what Apple names; explicitly incomplete for what Apple does not.** §2 marks four widely-assumed adopters (notifications, Control Center, media transport controls, macOS Dock and menu bar) as *undocumented* rather than listing them. |
| §3 Behavioral system | HIG **Materials**, **Color**, **Motion**, **Scroll views** and **App icons** pages (via DocC JSON), "Adopting Liquid Glass", "Applying Liquid Glass to custom views", the `Glass` symbol pages, and full WWDC25 transcripts for sessions 219, 284, 310, 323, 356, 361 plus WWDC26 102, 269, 278, 289. | **High on variants, size-dependence, light/dark, container merging, layering, legibility, concentricity, and the OS 27 revisions** — several of these are triangulated across three independent sources. **Thin in one specific place, flagged in §3.8: accessibility.** What the system substitutes under each mode rests on a *single spoken paragraph* of WWDC25 session 219; the HIG Accessibility page mentions Liquid Glass nowhere at all and its change log ends 2025-06-09. |

Two sourcing facts that constrain how this document may be cited:

- **The no-glass-on-glass rule is not on the HIG Materials page.** Its only
  written primary home is "Adopting Liquid Glass"; its expansive form is spoken
  in session 219. A citation to HIG Materials for it will not hold up.
- **Apple publishes exactly one number for this entire material** — the 35%
  clear-variant dimming layer. No blur radii, refraction indices, shadow
  opacities, tint ranges, size thresholds, or a count of "too many" simultaneous
  effects exists in any Apple source. Every quantitative row in this document is
  therefore vitrea's own measurement of Apple's *captures*, never a comparison
  against a published figure. That is the whole reason the calibration harness
  exists.

And one fact that bears directly on vitrea's premise, worth reading twice: Apple
explicitly disclaims cross-version visual stability for the material. Of icon
glass — "These effects automatically adapt with the size of your icon, apply
consistently across platforms, and **can appear differently between system
versions**" ([HIG App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)).
A profile-keyed, version-pinned fidelity claim is not conservatism; it is the
only kind of claim the reference permits.

One methodology fact that shaped all three layers and is worth recording:
`developer.apple.com` HIG and documentation URLs are JavaScript shells that
return only a `<title>` to a plain fetch. The readable body is DocC JSON at
`https://developer.apple.com/tutorials/data/<path>.json`. A matrix built from
naive HTML fetches of Apple's docs would be empty and would not say so.

---

## 1. Material API surface

Native items in the material layer proper — the APIs an app calls to put the
material on a view.

### 1.1 The glass modifier and the `Glass` value

| native item | citation | vitrea status | notes |
| --- | --- | --- | --- |
| `glassEffect(_ glass: Glass = .regular, in shape: some Shape = DefaultGlassEffectShape())` — the only documented overload; glass anchors to the view's bounds **including padding** | [swiftui/view/glasseffect(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:)) | `replicated+measured` — `GlassSurface` (`packages/react/src/surface.tsx`) with `asChild`; measured across all 30 texture-tier cells in `packages/calibration/results/matrix.json` | vitrea's equivalent is a registered host element rather than a modifier, so shape comes from the measured box plus `radius`/`capsule`/`profile` rather than an arbitrary `Shape`. Not a like-for-like surface. |
| `DefaultGlassEffectShape` — the default is a **capsule** | [swiftui/defaultglasseffectshape](https://developer.apple.com/documentation/swiftui/defaultglasseffectshape) | `partial` — the shape families exist (capsule is one) but vitrea's default is a 12px rounded rect (`DEFAULT_RADIUS`, `packages/react/src/surface.tsx`), not a capsule | Deliberate or not, this is a divergence from Apple's default that no ruling records. |
| `Glass.regular` — the adaptive default | [swiftui/glass/regular](https://developer.apple.com/documentation/swiftui/glass/regular) | `replicated+measured` — `MATERIAL_VARIANTS` (`packages/renderer-webgpu/src/material.ts`); the tuned profile is `packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json` | The one variant the whole 30-cell matrix measures. |
| `Glass.clear` — permanently more translucent; docs carry the legibility obligation | [swiftui/glass/clear](https://developer.apple.com/documentation/swiftui/glass/clear) | `replicated, unmeasured` — `variant: "clear"` on `GlassSurface`/`GlassGroup`, its own optics row in `MATERIAL_OPTICS` (`packages/platform-web/src/optics.ts`), dimming refusal tested in `packages/core/test/material.test.ts` | **No canonical scene renders `clear`.** `apps/reference-apple/scenes.json` has no variant axis at all, so the clear variant carries zero measurement on either side. |
| `Glass.identity` — "your content remains unaffected as if no glass effect was applied"; the documented way to turn glass off, **animatedly** | [swiftui/glass/identity](https://developer.apple.com/documentation/swiftui/glass/identity) | `absent, undecided` | The composite spec never mentions it — see §6. vitrea can unmount a surface, which is not the same thing as animating the material to nothing in place. |
| `Glass.tint(_ color: Color?)` — a per-surface author-set tint colour | [swiftui/glass/tint(_:)](https://developer.apple.com/documentation/swiftui/glass/tint(_:)) | `absent, undecided` | vitrea's tint is a **calibrated internal constant** (`tint`/`tintAlpha` in `MaterialOptics`, `packages/renderer-webgpu/src/material.ts`), tuned to 0.62 by C9a. No public prop anywhere in `packages/react/src` sets a tint colour. The spec discusses "tint thresholds" as a delegated calibration unknown and never as an author-facing API. |
| `Glass.interactive(_ isEnabled: Bool = true)` — "reacts to user interaction by scaling, bouncing, and shimmering" | [swiftui/glass/interactive(_:)](https://developer.apple.com/documentation/swiftui/glass/interactive(_:)) | `replicated, unmeasured` — `interactive` prop on `GlassSurface`; press glow and compression in `packages/renderer-webgpu/src/wgsl/highlight.ts`; behaviour asserted in `packages/react/e2e/press.spec.ts` | Unmeasured **for a stated reason**: the native pressed fixtures are byte-identical to rest (all four, SHA-256), because `Glass.interactive(true)` opts the material into *responding* to input rather than posing pressed, and Apple exposes no declarative pose (Decision Log #29(f)). No press claim is made, and none can be from stills. |
| Chaining — `.glassEffect(.regular.tint(.orange).interactive())` | [applying-liquid-glass-to-custom-views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views) | `partial` — variant and interactive compose on one surface; tint does not exist to chain | |
| `glassEffect(_:in:isEnabled:)` | **Not verified to exist** — the DocC path 404s; only unreliable secondary support | n/a | Recorded so the matrix does not inherit a beta-era signature from a blog. The documented conditional-disable route is `Glass.identity`. |

### 1.2 `GlassEffectContainer`

| native item | citation | vitrea status | notes |
| --- | --- | --- | --- |
| `GlassEffectContainer<Content>` — "combines multiple Liquid Glass shapes into a single shape that can morph individual shapes into one another" | [swiftui/glasseffectcontainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer) | `replicated+measured` — `GlassGroup` (`packages/react/src/group.tsx`); measured in `checkerboard__toolbar-group__rest` and `photo__toolbar-group__rest` | |
| `init(spacing: CGFloat? = nil)` — "the higher the spacing, the sooner blending begins as the shapes approach each other" | [same](https://developer.apple.com/documentation/swiftui/glasseffectcontainer) | `replicated+measured` — and the measurement is a refutation — `mergeDistance` on `GlassGroup`, wired into `DEFAULT_GROUP_UNION` by corrective K3 (merge 35b92b6) | The one row where measurement overturned a design assumption. C9a: **the reference does not union at the 12px spacing the canonical matrix declares** — three separate bodies on both sides, and sweeping merge distance across 24/12/4 gives a byte-identical silhouette. The union caps are therefore unmeasurable by this scene set (§Surprises). A tighter canonical scene is a named parent-impact item. |
| The real rationale: **"glass can not sample other glass, so having nearby glass elements in different containers will result in inconsistent behavior"** — the container is a shared sampling region | [WWDC25 session 323](https://developer.apple.com/videos/play/wwdc2025/323/) | `replicated+measured` — one masked backdrop proxy per sampling group, `samplingPadding ≥ 3σ`, `mergeDistance ≥ samplingPadding`; byte-exact on Chromium across 122 capture variants (spike S1) | vitrea's proxy model is a structurally *different* mechanism that lands on the same constraint. This is the strongest architectural correspondence in the matrix. |
| Rest-state blending rule — container spacing exceeding interior layout spacing blends at rest | [applying-liquid-glass-to-custom-views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views) | `replicated, unmeasured` — `packages/geometry/test/union.test.ts` | Cannot be measured against the reference for the reason in the row above. |
| Modifier ordering — apply `glassEffect` after other appearance-affecting modifiers | [same](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views) | n/a — no modifier ordering exists in a registration-based API | Recorded as a genuine non-applicability rather than a gap. |
| Performance ceiling — "creating too many containers … degrades performance. Limit simultaneous Liquid Glass effects onscreen" | [same](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views) | `replicated+measured` — quality governor with intra-tier degradation (`packages/renderer-webgpu/src/governor.ts`); benchmark in `packages/renderer-webgpu/e2e/bench/budget.spec.ts` | Measured against the spec's own 2ms hypothesis, not against Apple: mobile 1.47ms median, desktop 2.20ms, p95 over budget on both. |
| Container **nesting** rules | **Apple documents none.** No Apple page or session states a nesting rule; widely repeated claims trace to secondary blogs | `absent, undecided` — and correctly so | A row where the honest answer is that the native side has no answer to replicate. |

### 1.3 Morphing: IDs, transitions, unions

| native item | citation | vitrea status | notes |
| --- | --- | --- | --- |
| `glassEffectID(_:in:)` + `@Namespace` — associates an identity so SwiftUI animates shapes to and from each other | [swiftui/view/glasseffectid(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffectid(_:in:)) | `replicated, unmeasured` — `morphNamespace` on `GlassGroup` + `GlassMorph` (`packages/react/src/morph.tsx`); asserted in `packages/react/e2e/morph.spec.ts` on three engines | Parent acceptance #4 passes behaviourally. **No motion metric exists**: no frame sequences were captured, so the entire motion axis of §Calibration is unmeasured (acceptance #7, open). |
| `glassEffectUnion(id:namespace:)` — merges geometries into one shape **even at rest**, by shared ID, for views outside a layout container | [swiftui/view/glasseffectunion(id:namespace:)](https://developer.apple.com/documentation/swiftui/view/glasseffectunion(id:namespace:)) | `absent, undecided` | vitrea unions by **proximity only** (`mergeDistance`). There is no way to declare "these two surfaces are one body regardless of distance." The composite spec never mentions union-by-identity — see §6. |
| `GlassEffectTransition` with `.matchedGeometry` (the default inside container spacing), `.materialize`, `.identity` | [swiftui/glasseffecttransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition) | `partial` — vitrea has exactly one morph behaviour, always matched-geometry-like; `GlassMorph` exposes geometry endpoints but no transition *kind* | The `materialize` case — fade content, animate the material in or out, **do not** match a neighbour's geometry — has no vitrea equivalent and no ruling. The names appear nowhere in vitrea's documents (§6). |
| `glassEffectTransition(_:isEnabled:)` | **Not verified to exist** — path 404s | n/a | |
| Scope limit — `glassEffectID` and `glassEffectTransition` "only affect content during view hierarchy transitions or animations" | [applying-liquid-glass-to-custom-views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views) | `replicated, unmeasured` — `morphing` is an interaction state, not a persistent property (`packages/motion/src`) | |
| **UIKit has no ID-based morph API at all.** Merging is purely proximity-driven via `UIGlassContainerEffect.spacing`; presentation morphing uses `preferredTransition = .zoom` | [WWDC25 session 284](https://developer.apple.com/videos/play/wwdc2025/284/) | n/a | Worth stating because it means vitrea's proximity-only union is *UIKit-equivalent*, and the SwiftUI-only capability is the one that is absent. |

### 1.4 Scroll edge effects and background extension

| native item | citation | vitrea status | notes |
| --- | --- | --- | --- |
| `ScrollEdgeEffectStyle` — `.automatic` / `.soft` ("subtle, blurred boundary") / `.hard` ("linear, nearly opaque boundary") | [swiftui/scrolledgeeffectstyle](https://developer.apple.com/documentation/swiftui/scrolledgeeffectstyle) | `excluded by decision` — §Out of scope: "scroll-edge effects"; also §Deferred | The exclusion is a bare list entry with no rationale recorded, which is thin for a mechanism Apple applies **by default on every system bar** and cites as a legibility mechanism (§3.9). |
| `scrollEdgeEffectStyle(_:for:)`, `scrollEdgeEffectHidden(_:for:)` | [swiftui/view/scrolledgeeffectstyle(_:for:)](https://developer.apple.com/documentation/swiftui/view/scrolledgeeffectstyle(_:for:)) | `excluded by decision` — same line | |
| UIKit `UIScrollEdgeEffect` (`isHidden`, `style`) reached via `UIScrollView.topEdgeEffect` / `.bottomEdgeEffect` / `.leftEdgeEffect` / `.rightEdgeEffect`; `UIScrollEdgeElementContainerInteraction` | [uikit/uiscrolledgeeffect](https://developer.apple.com/documentation/uikit/uiscrolledgeeffect) | `excluded by decision` — same line | |
| `safeAreaBar(edge:alignment:spacing:content:)` — like `safeAreaInset`, but additionally "extends the edge effect of any scroll views affected by the inset safe area" | [swiftui/view/safeareabar(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareabar(edge:alignment:spacing:content:)) | `absent, undecided` | The glass-aware inset. Never named in any vitrea document (§6). |
| `backgroundExtensionEffect()` and `backgroundExtensionEffect(isEnabled:)` — **mirrors** the view into blurred copies around it on any edge with safe area | [swiftui/view/backgroundextensioneffect()](https://developer.apple.com/documentation/swiftui/view/backgroundextensioneffect()) | `absent, undecided` | Not scroll-edge, not covered by that exclusion, and never mentioned anywhere in vitrea's documents (§6). It is also the item most likely to be misimplemented on the web, because it mirrors rather than clips or stretches. |
| UIKit `UIBackgroundExtensionView`, AppKit `NSBackgroundExtensionView` | [uikit/uibackgroundextensionview](https://developer.apple.com/documentation/uikit/uibackgroundextensionview) | `absent, undecided` | |

### 1.5 Concentricity

| native item | citation | vitrea status | notes |
| --- | --- | --- | --- |
| `ConcentricRectangle` — "corners … squared, rounded, or concentric relative to a container shape's corners", radii computed relative to the container so the view adapts without hard-coded values | [swiftui/concentricrectangle](https://developer.apple.com/documentation/swiftui/concentricrectangle) | `replicated+measured` — the `concentric` shape family as a **level-set offset of the parent's field** (X8 rider 2); error bound < 0.18px at every inset, `packages/geometry/test/concentric.test.ts`, spike S2 findings | vitrea's mechanism is the mathematically honest one for its field family: instantiating the child as its own resolved shape adds an offset error that grows to 0.326px at 8px inset and dominates past ~4px. |
| The definition: concentric when "the corner's radius shares a common center with the containing shape's rounded corner radius" | [same](https://developer.apple.com/documentation/swiftui/concentricrectangle) | `replicated+measured` | vitrea independently established the corollary Apple's docs imply — concentricity governs **radius derivation only**, not the corner curve profile. An earlier vitrea claim conflating the two was refuted (§Surprises). |
| `Shape.rect(corners: Edge.Corner.Style, isUniform: Bool = false)`; `isUniform: true` resolves all radii then applies the **largest** | [swiftui/shape/rect(corners:isuniform:)](https://developer.apple.com/documentation/swiftui/shape/rect(corners:isuniform:)) | `partial` — vitrea's v1 requires **all four radii equal** (dev-mode error otherwise, X8 rider 3), so per-corner styles have no expression; the uniform case is covered by construction | Explicitly ruled: per-corner algebra is post-v1, "no v1 component needs it" (Decision Log #20). A recorded exclusion, not an oversight. |
| `Edge.Corner.Style` — `.concentric`, `.concentric(minimum:)`, `.fixed(_:)`; distant corners can legitimately resolve to **zero** radius | [swiftui/edge/corner/style](https://developer.apple.com/documentation/swiftui/edge/corner/style) | `partial` — vitrea's concentric family floors at a minimum radius (the `.concentric(minimum:)` analogue); `.fixed` is the default family; the resolve-to-square behaviour is not reproduced | |
| `containerShape(_:)` + the `RoundedRectangularShape` protocol — what makes concentricity resolve; a non-conforming container falls back to an inset `ContainerRelativeShape` | [swiftui/view/containershape(_:)](https://developer.apple.com/documentation/swiftui/view/containershape(_:)) | `partial` — the parent link is a **render input, not a scene-model field**, deferred to a post-v1 core API round (Decision Log #23c); C8's segmented-control indicator derives its radius via `resolveConcentric` instead | So concentricity works for the one v1 component that needs it and is not a general capability. |
| `GeometryProxy.concentricCornerRadii` and `concentricCornerRadii(in:)` — read the computed radii **without drawing a shape**. iOS/macOS **27.0 beta** | [swiftui/geometryproxy/concentriccornerradii](https://developer.apple.com/documentation/swiftui/geometryproxy/concentriccornerradii) | `absent, undecided` | One of only two 27.0-era additions anywhere in this area (§1.7). |
| UIKit `UICornerConfiguration` (squared default) + `UICornerRadius.containerConcentric(minimum:)` + `UIView.cornerConfiguration`; `UIView.effectiveRadius(corner:)` | [uikit/uicornerconfiguration-swift.struct](https://developer.apple.com/documentation/uikit/uicornerconfiguration-swift.struct) | `partial` — same as the SwiftUI rows; `capsule(maximumRadius:)`'s escape hatch (break the capsule paradigm above a given radius) has no vitrea analogue | |
| **Apple's own corner curve** — `.continuous` is **not G1**: a measured 2.4532° tangent break at both shoulder joins, edge-reach 1.528665 matching the published `cornerCurveExpansionFactor` | vitrea's own measurement (spike S2), corroborated against Apple's published factor | `replicated+measured` — the `rsupn` field family fits **directly** to Apple's measured curve; value error ≤ 0.170px max / 0.156px p95, gradient error ≤ 2.91° max | vitrea is, on this axis, more precise than the ecosystem: routing through the Figma-squircle family costs 6.4× the value error, and the widely cited Figma smoothing 0.6 is wrong for Apple-matching (0.66 measures ~2× closer). C9a then found the corner question **undecidable by the fixtures** — 0.012px vs 0.039px at the largest canonical radius, both two orders of magnitude under a pixel — so the claim rests on S2's geometry, not on pixels. |

### 1.6 Button styles, and the UIKit / AppKit surfaces

| native item | citation | vitrea status | notes |
| --- | --- | --- | --- |
| `GlassButtonStyle` (with `init()` **and `init(_ glass: Glass)`**), `GlassProminentButtonStyle`, `PrimitiveButtonStyle.glass` / `.glassProminent` / `.glass(_:)` | [swiftui/glassbuttonstyle](https://developer.apple.com/documentation/swiftui/glassbuttonstyle) | `partial` — `GlassButton` / `GlassIconButton` exist (`packages/react/src/controls/button.tsx`) and are the plain-glass analogue; **there is no prominent variant** | "prominent" appears **zero times** in every vitrea spec document (§6). Apple's prominent style is how a primary action is expressed on glass, and it is the emphasis mechanism that the missing tint API would otherwise provide. |
| `UIGlassEffect` — `init(style:)` only, `tintColor`, `isInteractive`; `UIGlassEffect.Style` = `regular` \| `clear` | [uikit/uiglasseffect](https://developer.apple.com/documentation/uikit/uiglasseffect) | `partial` — variant and interactive map across; `tintColor` does not exist in vitrea | |
| `UIGlassContainerEffect.spacing` — "the distance between elements at which they begin to merge" | [uikit/uiglasscontainereffect](https://developer.apple.com/documentation/uikit/uiglasscontainereffect) | `replicated+measured` — same row as `GlassEffectContainer(spacing:)` above | |
| `UIButton.Configuration.glass()` / `.prominentGlass()` / `.clearGlass()` / `.prominentClearGlass()` | [uikit/uibutton/configuration-swift.struct/glass()](https://developer.apple.com/documentation/uikit/uibutton/configuration-swift.struct/glass()) | `partial` — plain and clear reachable by composing `GlassButton` with `variant`; the two prominent forms are absent | |
| AppKit `NSGlassEffectView` (`contentView`, `tintColor`, `cornerRadius`, `style`, `effectIsInteractive`), `NSGlassEffectContainerView(spacing:)`, `NSButton.BezelStyle.glass` | [appkit/nsglasseffectview](https://developer.apple.com/documentation/appkit/nsglasseffectview) | n/a — a third framework expressing the same material; nothing additional to replicate | Recorded because AppKit exposes a plain `cornerRadius` where UIKit uses a corner *configuration*, which is a hint that Apple treats the corner story as unsettled too. |
| Toolbar-group glass management: `ToolbarSpacer`, `sharedBackgroundVisibility(_:)` ("hiding the effect will cause the item to be placed in its own grouping"), `UIBarButtonItem.hidesSharedBackground` | [swiftui/customizabletoolbarcontent/sharedbackgroundvisibility(_:)](https://developer.apple.com/documentation/swiftui/customizabletoolbarcontent/sharedbackgroundvisibility(_:)) | `absent, undecided` | vitrea's `GlassToolbar` groups its children into one glass group and offers **no way to split the shared background**, which is the whole of Apple's toolbar grouping vocabulary. Never mentioned in any vitrea document (§6). |
| `glassBackgroundEffect(displayMode:)` — **visionOS 1.0+, a different material** with thickness, specularity, and z-axis layout influence | [swiftui/view/glassbackgroundeffect(displaymode:)](https://developer.apple.com/documentation/swiftui/view/glassbackgroundeffect(displaymode:)) | n/a — correctly out of scope | Recorded as a **naming trap**: visionOS has had an unrelated material literally named "glass" since 2023, and filtering Apple's sources on the word "glass" produces false positives on the Windows, Buttons, and Widgets HIG pages. |
| **Platform coverage as a fact about the API**: the core glass symbols list iOS, iPadOS, Mac Catalyst, macOS, tvOS, watchOS — **not visionOS**. `ConcentricRectangle`, `Edge.Corner.Style`, `backgroundExtensionEffect()`, `ScrollEdgeEffectStyle`, and `safeAreaBar` **do** include visionOS 26.0 | verified consistently across those symbol pages | n/a | |

### 1.7 What WWDC26 / OS 27 changed in this layer

Verified three independent ways: Apple's June-2026 changelogs for
[SwiftUI](https://developer.apple.com/documentation/updates/swiftui),
[UIKit](https://developer.apple.com/documentation/updates/uikit) and
[AppKit](https://developer.apple.com/documentation/updates/appkit) contain **zero**
glass, concentricity, or scroll-edge entries (every glass mention on those pages
is filed under June 2025); the 138-session WWDC26 catalog has **no dedicated
Liquid Glass session** and no "what's new" session for UIKit or AppKit; and
availability inspection shows every pre-existing glass-material symbol still
carrying its original 26.0 annotation with no beta flag.

| native item | citation | vitrea status | notes |
| --- | --- | --- | --- |
| `NSGlassEffectView.effectIsInteractive` — macOS 27.0 beta. **The only new symbol on the glass-material surface in the entire WWDC26 cycle.** | [appkit/nsglasseffectview/effectisinteractive](https://developer.apple.com/documentation/appkit/nsglasseffectview/effectisinteractive) | n/a — AppKit catching up to `Glass.interactive(_:)` and `UIGlassEffect.isInteractive`, both of which shipped at 26.0 and both of which vitrea already has | |
| The material itself moved with **no API change**: "we tuned Liquid Glass so it more effectively diffuses complex content behind it. And to establish more depth and separation, we also introduced a darkened edge along with brighter specular highlights." Apps get it "without even needing to recompile" | [WWDC26 Platforms State of the Union](https://developer.apple.com/videos/play/wwdc2026/102/) | `absent, undecided` — vitrea calibrates against **macOS 26.5** captures (§Calibration; profile keys `apple-macos-26.5-*`) | Not a defect: 26.5 is the declared profile and every claim cites it. But it is a **shelf-life fact the roadmap does not price** — the reference material has already moved, and vitrea's fidelity claim is against a superseded version. |
| A user-facing slider adjusting Liquid Glass "anywhere from ultra clear to fully tinted" | [same](https://developer.apple.com/videos/play/wwdc2026/102/) | `absent, undecided` | Apple's own HIG anticipates this: "the appearance of these variants can differ … if people choose a preferred look for Liquid Glass in their device's settings." vitrea's variant axis is binary and author-controlled. |
| Concentricity moved outward: AppKit gained the whole `NSView.cornerConfiguration` / `NSViewCornerConfiguration` / `NSViewCornerRadius.containerConcentric` stack (macOS 27.0 beta), SwiftUI gained the two `GeometryProxy` read-back accessors | [appkit/nsviewcornerconfiguration](https://developer.apple.com/documentation/appkit/nsviewcornerconfiguration) | `absent, undecided` (the read-back accessors); the rest is AppKit parity | |
| Toolbar-minimization machinery: `toolbarMinimizationBehavior(_:for:)`, `toolbarMinimizationRestoration(.atScrollEdge, …)`, `toolbarMinimizationSafeAreaAdjustment(_:for:)`, `ToolbarPlacement.statusBar`; UIKit `UIBarMinimization` and its three enums on `UINavigationItem.navigationBarMinimization` | [swiftui/view/toolbarminimizationbehavior(_:for:)](https://developer.apple.com/documentation/swiftui/view/toolbarminimizationbehavior(_:for:)) | `absent, undecided` | Chrome behaviour rather than material, but it is where Apple spent its WWDC26 API budget in this area, and vitrea has no bar-retraction concept at all. |
| `UIScrollEdgeEffect.Style.automatic` changed meaning — it "no longer switches between the existing soft and hard styles but provides its own visuals"; an app that overrode it to `.soft` "should re-evaluate" | [WWDC26 session 278](https://developer.apple.com/videos/play/wwdc2026/278/) | `excluded by decision` (scroll-edge, §Out of scope) | |
| The old-design opt-out is being removed: "once your app is recompiled with Xcode 27, it will automatically begin to use the new design with Liquid Glass" | [WWDC26 State of the Union](https://developer.apple.com/videos/play/wwdc2026/102/) | n/a | Recorded because `UIDesignRequiresCompatibility` is the native equivalent of an opt-out, and vitrea has no notion of one — every vitrea surface is opt-in by construction, which is the safer default. |
| A **verified naming trap**: WWDC26 session recordings name `toolbarMinimizeBehavior` and `barMinimizationBehavior`; the shipped symbols are `toolbarMinimizationBehavior(_:for:)` and `UINavigationItem.navigationBarMinimization`. Code copied from the videos will not compile. | [session 269](https://developer.apple.com/videos/play/wwdc2026/269/) vs [documentation/updates/swiftui](https://developer.apple.com/documentation/updates/swiftui) | n/a | |

---

## 2. Component families that adopt glass natively

Named as Apple's sources actually name them. The authoritative enumeration is
**not** in the Human Interface Guidelines — it is the two verbatim lists on
["Adopting Liquid Glass"](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
(**ALG** below). Most per-component HIG pages contain **zero** glass content; a
matrix built from HIG component pages alone would badly under-count. Session
shorthand: **S284** = [Build a UIKit app with the new design](https://developer.apple.com/videos/play/wwdc2025/284/),
**S323** = [Build a SwiftUI app with the new design](https://developer.apple.com/videos/play/wwdc2025/323/),
**S356** = [Get to know the new design system](https://developer.apple.com/videos/play/wwdc2025/356/).

| native family (as the sources name it) | how it adopts glass | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| **Buttons** — SwiftUI `Button` / UIKit `UIButton` / AppKit `NSButton` | Automatic on recompile, plus four named opt-in styles; default capsule via `buttonBorderShape(.capsule)`; `controlSize(_:)` gains an extra-large size; buttons "fluidly morph into menus and popovers" | ALG; S323 | `replicated+measured` — `GlassButton`, `GlassIconButton`; the `capsule-button` component is 12 of the 30 measured cells | The single best-covered family. The button→menu morph is parent acceptance #4 and passes on three engines (`packages/react/e2e/morph.spec.ts`). Missing: the prominent style, and the extra-large control size. |
| **Toolbars / toolbar items** — `View.toolbar(content:)` / `UIToolbar`, `UINavigationBar`, `UIBarButtonItem` / `NSToolbar` | Automatic. Item grouping with shared backgrounds; `ToolbarSpacer(.fixed)` / `(.flexible, placement:)` to split groups; `sharedBackgroundVisibility(.hidden)`; `.prominent` for one primary action; scroll edge effect on by default; contained buttons, text fields, headers and footers get radii **concentric with the bar** | ALG; S284; [HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars) | `partial` — `GlassToolbar` exists and groups into one glass group; measured as `toolbar-group` in 2 cells | Absent from the vitrea side: group splitting (`ToolbarSpacer` / `sharedBackgroundVisibility`), the prominent item, the default scroll edge effect, and bar-concentric radii for contained controls. **The HIG states corner concentricity for real components exactly once, on this page** — and it is the one place it applies to contained buttons and text fields. |
| **Tab bars** — `TabView` / `UITabBar`, `UITabBarController` | Automatic; items "rest on a Liquid Glass background that allows content beneath to peek through". `tabBarMinimizeBehavior(.onScrollDown)`; `tabViewBottomAccessory(content:)` / `UITabAccessory`; tab-to-sidebar via `.tabViewStyle(.sidebarAdaptable)` | ALG; [HIG Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars); S323; S284 | `excluded by decision` — §Out of scope: "TabBar" | |
| **Navigation bars / split views** — `NavigationStack`, `NavigationSplitView` / `UINavigationBar`, `UISplitViewController` / `NSSplitView` | Automatic; split views reflow continuously for arbitrary window sizes | ALG | `absent, undecided` | Not in the v1 component list and not in the cut list. The HIG has **no** navigation-bars page — that URL redirects to Toolbars. |
| **Sidebars and inspectors** — `NavigationSplitView` + `inspector(isPresented:content:)` / `UISplitViewController.Column.inspector` / `NSSplitViewItem(inspectorWithViewController:)` | Automatic — they "float in this Liquid Glass layer"; opt-in `backgroundExtensionEffect()` | ALG; [HIG Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars) | `absent, undecided` | Sidebars are also where Apple's opacity-grows-with-size rule is stated most plainly ("more opaque in larger elements like sidebars"), which is exactly vitrea's open gap §4.1. |
| **Segmented controls / pickers** — `Picker` / `UISegmentedControl` / `NSSegmentedControl` | Automatic on recompile. Only the shared control-list citation; the HIG segmented-controls page says nothing about glass | ALG | `replicated, unmeasured` — `GlassSegmentedControl` (`packages/react/src/controls/segmented-control.tsx`); indicator slide asserted in `packages/react/test/controls.test.tsx` | Kept in v1 deliberately: it exercises the **within-group indicator morph**, a distinct case from the cross-plane morph (Decision Log #13). No canonical scene renders it. |
| **Sliders** — `Slider` / `UISlider` / `NSSlider` | Automatic; the knob "transforms into Liquid Glass during interaction" — a transient content-layer exception. New: automatic tick marks from `step`, `UISlider.TrackConfiguration`, `SliderStyle.thumbless` | ALG; [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials); S284 | `excluded by decision` — §Out of scope: "Slider" | The exclusion drops more than a component: the **transient-glass** behaviour (glass appearing only during interaction, on an element that is otherwise content-layer) is a distinct material behaviour with no other v1 carrier. |
| **Toggles / switches** — `Toggle` / `UISwitch` / `NSSwitch` | Automatic; same transient-knob exception. The HIG toggles page never mentions it | ALG; HIG Materials | `excluded by decision` — §Out of scope: "Toggle" | |
| **Steppers** — `Stepper` / `UIStepper` / `NSStepper` | Automatic on recompile; named only in the control list | ALG | `absent, undecided` | |
| **Menus and context menus** — `Menu` / `UIMenu` | Automatic: "Menus have a refreshed look… They adopt Liquid Glass." Standard selectors drive automatic action icons; buttons morph into menus; new iPadOS menu bar | ALG; S356 | `replicated, unmeasured` — the menu is composed as `GlassSurface asChild` over React Aria hooks (Decision Log #24e); it is the destination of the acceptance-#4 morph | Measured only as geometry, not as a menu: the `glass-over-glass` scenes are a **stack**, not a menu, and are a mixed-backend cell by construction. |
| **Popovers** | Automatic; use the **regular** variant; remove custom visual-effect views from popover content; anchor via `sourceItem` for the morph | ALG; HIG Materials; S284 | `excluded by decision` — §Out of scope: "Popover" | |
| **Sheets** — `presentationDetents(_:)` / `UISheetPresentationController` | Automatic. Increased corner radius; half sheets inset from display edges so content peeks through; **transition to a more opaque appearance at full height**; remove custom `presentationBackground(_:)` | ALG; S323; S284 | `excluded by decision` — §Out of scope: "Sheet" | The "more opaque at full height" rule is a second instance of Apple's size-dependent opacity, which vitrea's material cannot express at all (§4.1). |
| **Action sheets** — `confirmationDialog(...)` / `UIAlertController` + `sourceView`/`sourceItem` | Automatic; now originates from the invoking element rather than the screen bottom, and permits interaction elsewhere | ALG; S356 | `absent, undecided` | |
| **Alerts** | Automatic; use the **regular** variant (text-heavy). Bolder, left-aligned typography. The HIG alerts page has no glass content | HIG Materials; S356 | `absent, undecided` | |
| **Search fields** — `searchable(text:)`, `searchToolbarBehavior(.minimize)`, `Tab(role: .search)` / `UISearchTab`, `preferredSearchBarPlacement` | Placement changes **automatically** (bottom on iPhone, top-trailing on iPad/Mac); minimize behavior is opt-in | ALG; S323; S284 | `excluded by decision` — §Out of scope: "SearchField" | |
| **Text fields** — `TextField` / `UITextField` / `NSTextField` | Automatic; inside a bar they get radii concentric with the bar | ALG; HIG Toolbars | `absent, undecided` | |
| **Scroll edge effect** (cross-cutting, not a component) | Automatic on system bars; custom bars register manually. `soft` default on iOS, `hard` on macOS, dense UIs, pinned table headers, free-floating text | ALG; [HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views) | `excluded by decision` — §Out of scope | |
| **Corner concentricity** (cross-cutting) | `ConcentricRectangle`, `.rect(corners:isUniform:)` / `UICornerConfiguration` | ALG | `partial` — see §1.5 | |
| **Windows / window chrome** — `WindowStyle.titleBar` | Automatic: rounder corners "to fit controls and navigation elements"; iPadOS gains window controls and continuous resizing | ALG | `absent, undecided` | The HIG windows page's five "glass" hits are all **visionOS's older material also called glass** — a verified false-positive trap. |
| **Widgets** | Automatic but **user-selected**: "in a clear appearance, the system desaturates the widget and adds translucency, highlights, and the Liquid Glass material"; accented rendering substitutes a glass background | [HIG Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets) | `absent, undecided` | Never mentioned in any vitrea document (§6). Notable because it is the one place Apple documents a **desaturation** step alongside the material. |
| **App icons** (non-control) | Layered icons "take on Liquid Glass attributes like specular highlights, refraction, and translucency", applied by the system; authored in Icon Composer; light/dark/clear/tinted variants | [HIG App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons); ALG | `absent, undecided` | Legitimately outside a web material runtime's job, but it is the only place Apple names a **four-way** appearance axis (light/dark/clear/tinted) for the same material. |
| **Custom views** — `glassEffect`, `Glass`, `GlassEffectContainer`, `glassEffectID`, `glassEffectUnion`, `GlassEffectTransition` | The opt-in path; see §1 | [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views) | `partial` — this **is** vitrea's whole surface, minus tint, identity, union-by-id, and named transitions | |
| **Keyboard accessory views** | The clearest automatic-versus-opt-in statement Apple publishes: *"If you use a standard toolbar to contain your controls, it automatically adopts Liquid Glass"* — a custom accessory container does not | [HIG Virtual keyboards](https://developer.apple.com/design/human-interface-guidelines/virtual-keyboards) | `absent, undecided` | Almost never cited, and it is the cleanest articulation of Apple's opt-in boundary. |
| **tvOS controls** | Buttons and image views adopt glass **on focus**, via `focusable(_:)` / `UIFocusItem`; Apple TV 4K 2nd-gen and newer only | ALG; HIG Materials | n/a | Recorded because *glass-on-focus* is a native interaction state vitrea's interaction machine (idle/hover/pressed/focused/disabled/morphing) has a slot for but does not use materially. |
| **watchOS** | Glass appears **without rebuilding** against the new SDK | ALG | n/a | |
| **Lists, tables, forms** | **Deliberately do NOT get glass.** "Don't use Liquid Glass in the content layer… Instead, use Standard materials." What they get is metric changes: larger row height and padding, increased section corner radius, title-style section headers | ALG "Organization and layout"; HIG Materials | n/a — **and this is the most important n/a in the document** | This is a *prohibition*, and it is the single most likely thing for a web glass library to get wrong in the opposite direction — by applying glass where Apple explicitly forbids it. See §3.9; the phrase "content layer" appears **zero times** in vitrea's specs (§6). |

**Four families the ecosystem assumes are glass adopters and Apple does not
document as such**, verified as negative findings rather than search gaps:
**notifications**, **Control Center controls**, **media / transport controls**,
and the **macOS Dock and menu bar**. The WidgetKit Controls page has not been
revised since June 2024 and says nothing about glass; the macOS menu bar page
contains no appearance guidance at all. The only adjacent confirmations are that
HIG Materials names Control Center in a **tvOS** context, and that "Elevate the
design of your iPad app" describes the iPad menu bar's pointer highlight as "a
liquid glass platter that materializes directly on top of the buttons you're
hovering over" ([WWDC25 session 208](https://developer.apple.com/videos/play/wwdc2025/208/)).
They are excluded from the table above on purpose.

**WWDC26 adds no new glass-adopting family.** Session 269 frames Liquid Glass as
a refinement apps get "without having to change a single line of code"; the
WWDC26 design guide lists no glass-component sessions at all.

**Two families are documented as glass adopters ONLY on the Materials page** —
sliders and toggles, via the transient-interaction exception. Their own HIG pages
have not been revised to say so. A matrix drawn from component pages alone would
score them as non-adopting.

---

## 3. The behavioral system

The documented behaviors of the material itself, as distinct from the API that
applies it and the components that adopt it. **HIG** = the
[Materials page](https://developer.apple.com/design/human-interface-guidelines/materials);
**HIG Color** = the [Color page](https://developer.apple.com/design/human-interface-guidelines/color)'s
Liquid Glass section; **S219** = [Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/),
which names no API symbols at all and is purely the material's design and physics.

### 3.1 The two variants

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| Exactly two variants exist, and they are the same two the API exposes | "Liquid Glass provides two variants — regular and clear — that you can choose when building custom components or styling some system components." | HIG | `replicated, unmeasured` — `MATERIAL_VARIANTS`, `packages/core/test/material.test.ts` | Only `regular` is measured. |
| Regular is context-independent | "Use the regular variant when background content might create legibility issues, or when components have a significant amount of text, such as alerts, sidebars, or popovers." / S219: it "provides legibility regardless of context. It works in any size, over any content and anything can be placed on top of it." | HIG; S219 | `replicated+measured` — 30 of 30 texture-tier cells; holdout IoU 0.9924/0.9612, SSIM 0.9475/0.9007, ΔE 0.0320/0.0548 | The claim vitrea actually earns. |
| What regular optically does | "The regular variant blurs and adjusts the luminosity of background content to maintain legibility of text and other foreground elements." | HIG | `partial` — blur and tint are implemented and tuned; **the luminosity adjustment is a fixed tint, not a per-backdrop luminosity transform** | C9a measured the difference precisely: the reference's interior "rises monotonically with the backdrop across the whole canonical range (0.680 at a backdrop of 0.003 to 0.932 at 0.891)" — a transfer curve — where vitrea applies one alpha. |
| Clear has **no adaptive behavior at all** | S219: "does not have adaptive behaviors. It is permanently more transparent… it needs a dimming layer to darken the underlying content." | S219 | `replicated, unmeasured` — `clear` gets "constrained adaptation" plus a required dimming policy, refused if absent (`DEFAULT_CLEAR_DIMMING`) | vitrea's "constrained" is weaker than Apple's "none". No scene renders it, so nobody has checked. |
| Clear is restricted to visually rich backgrounds, under **three preconditions that must all hold** | "First, the element you're applying it to is over media-rich content. Second, your content layer won't be negatively affected by introducing a dimming layer. And lastly, the content sitting above it is bold and bright." | S219; HIG | `absent, undecided` | vitrea's runtime **refuses clear without a dimming policy** but never checks any of the three. The dimming requirement is enforced; the use-restriction is not, and no diagnostic mentions it. |
| The dimming layer is **35% opacity, and conditional** | "If the underlying content is bright, consider adding a dark dimming layer of 35% opacity." | HIG | `partial` — a dimming policy is required, and its value is a calibration-delegated unknown ("clear-variant dimming", §Calibration) | **The 35% figure appears nowhere in vitrea's documents** (§6), even though it is exact, citable, and free. Note also that Apple's obligation is softer than vitrea's: "consider adding", conditional on bright content — vitrea refuses outright. |
| The dimming layer may be omitted | "If the underlying content is sufficiently dark, or if you use standard media playback controls from AVKit that provide their own dimming layer, you don't need to apply a dimming layer." | HIG | `absent, undecided` | vitrea has no "sufficiently dark" escape and no way to declare an existing dimming layer. |
| Dimming may be **localized** rather than full-canvas | "If Liquid Glass elements in your app have a smaller footprint, you can use localized dimming and allow the content to retain more of its original vibrancy." | S219 | `absent, undecided` | vitrea's `DimmingPolicy` is a group-level property; there is no localized form. |
| Consequence of skipping the dimming layer | "To provide enough legibility for symbols or labels, it needs a dimming layer to darken the underlying content. Without it, legibility gets noticeably worse." | S219 | `replicated, unmeasured` — this is precisely why vitrea *refuses* clear-without-dimming rather than inventing a scrim | The one place vitrea is deliberately stricter than Apple, with the reasoning recorded (Decision Log #19). |
| Modality is signalled by **pairing glass with a dimming layer** — dimming is not only a clear-variant device | "When a task interrupts the main flow, pair Liquid Glass with a dimming layer to help center attention… when a task happens in parallel, Liquid Glass creates a natural separation." | [S356](https://developer.apple.com/videos/play/wwdc2025/356/) | `absent, undecided` | vitrea ties dimming exclusively to the clear variant. Apple also uses it as a modality signal on regular glass. |
| **Never mix the variants** | S219: "They should never be mixed, as they each have their own characteristics and specific use cases." | S219 | `replicated, unmeasured` — same-group variant mixing raises a dev-mode warning and deliberately does not coerce the author's intent (`packages/core/test/material.test.ts`) | vitrea's check is **per group**; Apple's guidance is per interface. Cross-group mixing passes silently. |

### 3.2 Size-dependent behavior — vitrea's largest open gap

Size-dependence is not an incidental property. Apple states it as an axiom —
"Liquid Glass is designed from the ground up to be **adaptive to both its size
and its environment**" (S219) — and then names four separate consequences, each
of which gets its own row. This is the layer's densest sourcing and vitrea's
thinnest coverage.

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| **Larger surfaces refract, shadow, and scatter MORE** — the full claim, verbatim | "When glass flexes and morphs to larger sizes – like when presenting a menu from a toolbar button – its material characteristics change to simulate a thicker, more substantial material. It **casts deeper, richer shadows, has more pronounced lensing and refraction effects, and a softer scattering of light**. These subtle changes enhance the perceived depth and aid in the legibility of the content within the glass element itself." | S219 | `partial` — lensing yes, shadow no, scattering no | `lensDepthPx = min(thickness * sizeGain(span), span / 2)` with `lensSpanMin` / `lensSpanMax` / `lensSizeGainMax` in the material profile; visible end to end after corrective K2 ("larger plate lenses harder"), which is parent acceptance #2's mechanism. `shadowDepth` and `shadowAlpha` carry **no** size term, and there is no scattering channel at all. Note that Apple frames this as *morph-driven* — the button-to-menu case — which is exactly vitrea's one v1 morph pair, so the material should thicken across that transition and does not. |
| **Opacity grows with element size** — stated three times, in three registers | HIG: "Liquid Glass appears more opaque in larger elements like sidebars to preserve legibility over complex backgrounds and accommodate richer content on the material's surface." / S284: "Glass adapts the appearance based on its size. **A larger size is more opaque. A smaller size is clearer**, and switches between light and dark mode automatically, to increase contrast." | HIG Color; [S284](https://developer.apple.com/videos/play/wwdc2025/284/) | `absent, undecided` in the runtime; the **gap itself is measured** | C9a §4.1 quantified it exactly: the reference's transmission runs **0.88 at a 32px span to 0.56 at 96px**; vitrea has no size term and cannot vary. It is the named mechanism behind the holdout overfitting signal — holdout took both `rrect-lg` cells, and on `checkerboard__rrect-lg__rest` the reference interior sits at 0.6384 against vitrea's 0.8000. The parent spec lists a size term on the tint alpha as a parent-impact item; nothing schedules it. |
| **Size gates the light/dark flip** | "Small elements like navbars and tabbars… flip from light to dark based on the background… **Bigger elements, like menus or sidebars also adapt based on context, but they don't flip from light to dark. Their surface area is too big and transitions like these would be distracting.**" | S219 | `absent, undecided` | A size-conditioned *behavioral switch*, not a parameter — the material changes which adaptation it performs at all. vitrea has no such threshold anywhere. |
| **Large surfaces pick up ambient colour spill from nearby content** | "On larger elements, like sidebars, the appearance of Liquid Glass is informed by the ambient environment within the app. **Light from colorful content nearby can subtly spill onto its surface**, reinforcing the material's context and its sense of elevation." | S219 | `absent, undecided` | vitrea samples only what is *behind* a surface, never beside it. Structurally reachable — a group's proxy is already padded past the member union — and entirely unbuilt. |
| Sheets become **more opaque at full height** — the same rule in a component | "When a half sheet expands to full height, it transitions to a more opaque appearance to help maintain focus on the task." | ALG | `excluded by decision` (Sheet, §Out of scope) | Recorded because it corroborates the opacity rule as *systemic* rather than a sidebar special case. |
| App-icon glass effects also scale with size | "These effects automatically adapt with the size of your icon, apply consistently across platforms, and can appear differently between system versions." | [HIG App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons) | n/a | Fourth independent corroboration of the same axiom. |

**Read together, these five rows are the single largest coherent absence in the
matrix.** Apple describes one mechanism — the material simulates a thicker
substance as it grows, and that shows up as shadow, lensing, scattering,
opacity, and a switch in which adaptation it performs. vitrea implements exactly
one of the five, and it is the one Apple quantifies least.

> **Annotated after wave child W2 landed the size law (2026-08-30).** The
> statuses above are the pre-W2 ones and stay as the before-state; what changed
> is recorded in the claims doc's §5.7 rather than restated here, because this
> document is the enumeration and that one is the measurement. In short: vitrea
> now derives all four *parametric* facets from one shared curve rather than one.
> The lens and the inner shadow ship with fitted gains; the scattering and the
> occlusion ship with the mechanism built on both tiers and its constant at the
> identity, because the settled bed cannot identify the first and fits the second
> to zero until W7's tone axis exists.
>
> The fifth row — the size-gated light/dark flip — is still `absent`, and now has
> a measurement attached: over `dark-solid` the reference's 44 px capsule adapts
> until the extractor finds no silhouette at all, while its 96 px rrect sits at
> 0.454 and does not adapt (over `impulse`, 0.013 against 0.412). It gates an
> adaptation vitrea does not perform, so it belongs with W7, which can key it off
> the curve W2 built.
>
> One correction this table should carry rather than pass on: the second row's
> "the gap itself is measured" cites C9a §4.1's transmission figures, whose
> *direction* the settled bed reverses. §5.7 explains why neither reading is a
> clean measurement of size — that estimator runs across backdrops, which is
> exactly where tone adaptation lives — and measures it within one backdrop
> instead.
>
> **The fifth row is CLOSED (W7, 2026-08-30).** The size-gated light/dark flip is
> implemented on both tiers and keys off the same `sizeThickness` curve, exactly
> as the paragraph above anticipated — the thickness enters the adaptation curve's
> *argument*, so a thicker surface reads its backdrop as brighter and holds its own
> appearance longer. The claims doc's §5.8 is the measurement; §3.3's box above is
> where the flip itself is resolved. The band 32…96 is now pinned by both children
> independently: W2 set it from the reference's transmission, and the tone axis
> requires it (a band ending at 64 lifts the 44 px capsule out of full adaptation;
> one ending at 128 over-adapts the 96 px surface). Of the five facets, four are
> now derived from the shared curve with fitted or identity constants and the fifth
> — **ambient colour spill on large surfaces** — remains the only one absent.

### 3.3 Light/dark adaptation

> **The one place where vitrea's measurement contradicts Apple's documentation,
> and it is not resolved.** Apple states plainly and repeatedly that the material
> flips light/dark **in response to the backdrop** for small elements. C9a
> measured the actual macOS 26.5 material through `glassEffect` at rest and found
> it doing no such thing: over the *same* bright checkerboard the reference sits
> at interior level **0.809 in the light scheme and 0.055 in the dark scheme**,
> and across the whole canonical backdrop range in one scheme its interior rises
> *monotonically* with the backdrop (0.680 at a backdrop of 0.003 to 0.932 at
> 0.891) rather than inverting against it. Both facts are well-evidenced and they
> do not fit together. Three explanations survive, and this document does not
> choose between them: (a) Apple's flip is scoped to *system* navigation bars and
> tab bars and a custom `glassEffect` view does not receive it; (b) the flip is
> driven by something the canonical scenes do not vary — the scenes are static
> stills at rest, and Apple's own framing is "as text scrolls underneath"; or
> (c) the canonical component sizes (120×44 up to 280×160) sit above whatever
> threshold gates the flip. **Resolving this is a prerequisite for any adaptive
> tint work**, because C9a already spent a tuning round on an inversion that the
> reference does not perform and had to make the crossover inert to undo it.

> **RESOLVED (W7, 2026-08-30): the answer is (c), and (a) and (b) are wrong.**
> Annotated in place by the child that measured it, under the convention W2 used
> in §3.2; the measurement is the claims doc's §5.8 and this document stays the
> enumeration.
>
> The contradiction was an artefact of the bed. C9a measured the *mixed* v1
> capture set, which was caught mid-adaptation on precisely the cells the flip
> lives in (wave Surprise, 2026-08-30). On the settled bed a custom `glassEffect`
> view flips exactly as Apple says it does — so (a) is wrong, the flip is not
> reserved for system bars — and it does so at rest on a static still, so (b) is
> wrong too: scrolling is not the trigger. **(c) was right**, and the threshold is
> measured: over a backdrop of linear 0.0117 the light-scheme 44 px capsule reads
> 0.0117, byte-identical to its own background *and* to the dark-scheme capsule
> over the same backdrop, while a 96 px surface over that backdrop keeps three
> quarters of its own appearance. The canonical sizes straddle the gate rather
> than sitting above it, which is why one bed showed both halves of the
> contradiction.
>
> One correction the resolution carries: it is not a *flip between two schemes*.
> Both schemes converge on the same value — the backdrop's own tone — so the
> scheme sets the neutral and the adaptation moves away from it. That also settles
> the tension this table's last row names between scheme-keying and
> luminance-keying: macOS 26.5 does both, in series, and they are not alternatives.
>
> Two rows change. **"Small elements flip light/dark to the underlying content"**
> becomes `present, measured`: the axis is implemented on both tiers with fitted
> constants and a per-group backdrop reading, and the seven adopted-gate rows it
> used to cost re-entered the gate and pass at unchanged bounds. **"Foreground
> mirrors the material's flip"** is no longer mirroring nothing — the ink is
> decided against the adapted material on both tiers. What stays `absent` is the
> row below them: nothing still selects a profile from the colour scheme.

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| Small elements flip light/dark **to the underlying content** | HIG Color: "For smaller elements like toolbars and tab bars, the system can adapt Liquid Glass between a light and dark appearance in response to the underlying content." / S219: "unlike previous materials that had a fixed light or dark appearance, **each layer continuously adapts based on what's behind it**… when needed, it can also independently switch between light and dark." / S284: "the glass and its content will switch to light or dark mode automatically, **when using dynamic colors**." | HIG Color; S219; S284 | `absent, undecided` — the GPU tier has the machinery (an adaptive tint driven by an analysis reduction, `packages/renderer-webgpu/src/analysis.ts`) and C9a **made its backdrop crossover inert** | See the box above. The machinery is built, wired, and switched off, for a measured reason. |
| Foreground **mirrors** the material's flip, automatically, on regular glass | "To maintain legibility, symbols and glyphs on top of Liquid Glass do the same. They flip from light to dark and vice versa, **mirroring the glass's behavior** to maximize contrast. **All content placed on the Regular variant will automatically receive this treatment.**" | S219 | `partial` — `ForegroundAdaptation = fixed \| author-hint \| sampled-async` with async readback capped at 15Hz plus threshold, hysteresis and crossfade; corrective K4 wired the CSS tier to honour X6's hint | The mechanism exists and is the right shape (Apple's is automatic on regular glass; vitrea's is opt-in per surface). But it mirrors a material flip that vitrea no longer performs, so on the GPU tier it currently mirrors nothing. |
| Foreground/symbol colour defaults to **monochromatic** | "By default, symbols and text on these elements follow a monochromatic color scheme, **becoming darker when the underlying content is light, and lighter when it's dark**." / "prefer a monochromatic appearance for toolbars and tab bars" over colourful content | HIG Color | `partial` — `near-monochrome` exists but only as an **accessibility** consequence of increased contrast, not as the material's default | Inverted defaults: Apple's default is monochrome, vitrea's is adaptive-colour. |
| Ship both colour variants even in a single-appearance app | "Even if your app ships in a single appearance mode, provide both light and dark colors to support Liquid Glass adaptivity in these contexts." | HIG Color | `absent, undecided` | vitrea has a committed dark profile the host must pass in by hand; nothing asks an author for both. |
| Nothing in the runtime selects a profile by colour scheme | — | — | `absent, undecided` | C9a §4.3, stated plainly: "nothing in the runtime reads the scheme, so dark mode is correct only for a host that passes the dark profile itself." A committed dark profile exists (`apple-macos-26.5-1x-dark-standard.json`) and must be handed in by the application. |
| Variant appearance is **not fixed** — system settings change it | "The appearance of these variants can differ in response to certain system settings, like if people choose a preferred look for Liquid Glass in their device's settings, or turn on accessibility settings that reduce transparency or increase contrast." | HIG | `partial` — the accessibility half is implemented (§3.8); the user-preference half is absent | The "preferred look" clause is the HIG anticipating WWDC26's ultra-clear-to-fully-tinted slider (§1.7). vitrea has no axis for it. |
| visionOS: glass adapts to backdrop **luminance** because there is no Dark Mode | "visionOS doesn't have a distinct Dark Mode setting. Instead, glass automatically adapts to the luminance of the objects and colors behind it." | HIG | n/a | Included because it is Apple confirming that scheme-keying and luminance-keying are two different mechanisms it deploys on different platforms — which is the cleanest resolution of the tension three rows up. |

### 3.4 Colour and tinting

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| Glass is **colourless by default** and takes colour from behind it | "By default, Liquid Glass has no inherent color, and instead takes on colors from the content directly behind it. You can apply color to some Liquid Glass elements, giving them the appearance of colored or stained glass." | HIG Color | `partial` — the "takes colour from behind" half is what the analysis pass and adaptive tint were for, now inert; the "apply colour" half does not exist | |
| **A tint is a brightness-mapped range of tones, not a colour** | "Selecting a color generates a **range of tones that are mapped to content brightness underneath** the tinted element… changing its hue, brightness and saturation depending on what's behind without deviating too much from the intended color." / "just like text within a glass effect, the tint also uses a **vibrant** color that adapts to the content behind it." | S219; [S323](https://developer.apple.com/videos/play/wwdc2025/323/) | `absent, undecided` | This deepens the §1.1 absence considerably. `Glass.tint(_:)` is not a fill — it is a *seed* for a backdrop-conditioned tone mapping with vibrancy. Implementing it as a flat overlay colour would be the wrong thing, and it is the obvious wrong thing to build under time pressure. |
| Tint sparingly, on backgrounds not symbols | "Apply color sparingly… reserve it for elements that truly benefit from emphasis, such as status indicators or primary actions. To emphasize primary actions, apply color to the background rather than to symbols or text… Refrain from adding color to the background of multiple controls." / S219: "When every element is tinted, nothing stands out. If you want to imbue color into your app, do it in the content layer instead." | HIG Color; S219 | `absent, undecided` | No author tint exists to apply sparingly (§1.1). This is guidance vitrea cannot follow or violate. |
| **A solid fill is not a tint, and breaks the material** | "Here is a button that is using a solid fill instead of the built-in tinting. As you can tell, it is completely opaque and **breaks the visual character of Liquid Glass**." | S219 | `absent, undecided` | The failure mode Apple names is exactly what an author will do in vitrea today, because a background colour on the host element is the only tinting route available. |
| Avoid label/background colour collision | "Avoid applying a similar color to button labels and content layer backgrounds. If your app already has bright, colorful content… prefer using the default monochromatic appearance of button labels." | [HIG Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons) | `absent, undecided` | vitrea's foreground policy adapts light/dark; it has no notion of hue collision. |

### 3.5 Lensing and refraction physics

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| The material "reflects and refracts lights, picking colors from nearby content… by sampling content from an area larger than itself" | this is the container's stated rationale, and the clearest physical description Apple gives in a developer source | [S323](https://developer.apple.com/videos/play/wwdc2025/323/) | `replicated+measured` — sampling from an enlarged region is exactly `samplingPadding ≥ 3σ`, verified byte-exact at three radii spanning 5× (spike S1) | vitrea's version of this claim is stronger than Apple's, because it is a measured floor rather than a description. |
| **"Lensing" is the named primary mechanism** — bending, not scattering | "The primary way Liquid Glass visually defines itself is through something called **Lensing**… Whereas previous materials scattered light, this new set of materials dynamically **bends, shapes, and concentrates light in real time**." | S219 | `replicated+measured` — the `rsupn` pseudo-SDF field family with measured error bounds (≤0.170px value, ≤2.91° gradient); optics and highlight passes in linear premultiplied light; goldens on real headless Chromium | Apple publishes no numbers, so "measured" means against Apple's *captures* and against vitrea's own declared bounds. vitrea's architecture is on the right side of the distinction Apple draws: real refraction where a texture is registered, and it *names* the CSS tier `refraction: "none"` rather than passing a blur off as lensing. |
| It is a **synthetic meta-material**, not a glass simulation | "rather than trying to simply recreate a material from the physical world, Liquid Glass is a new digital **meta-material** that dynamically bends and shapes light." | S219 | n/a | Worth recording as a framing correction: fidelity here means matching Apple's *invention*, not matching physics. Which is precisely why a calibration harness against captures is the only defensible method. |
| Highlights come from a **simulated lighting environment** with moving lights | "Liquid Glass lives inside an environment that behaves like the world around us. Light sources inside of this environment shine on the material producing highlights that respond to geometry just as you'd expect." / "On interactions, such as locking and unlocking your phone, these lights move in space, causing light to travel around the material, defining its silhouette." | S219 | `partial` — a specular sweep travels the rim in angular coordinates, driven by motion-driver output, but from a **single fixed `lightDirection`** in the material profile | vitrea has a travelling band; Apple has a lighting environment with multiple positioned sources. Different in kind, similar in effect at rest. |
| Specular highlights respond to **device motion** — documented, but Apple hedges it | S219, hedged: "And **in some cases**, the lighting responds to device motion, making it feel like Liquid Glass is aware of its position in the real world." App icons, unhedged: "the system uses [four layers] to produce specular highlights **when a person moves their device**." | S219; [Landmarks sample](https://developer.apple.com/documentation/swiftui/landmarks-building-an-app-with-liquid-glass) | `absent, undecided` | The behavior is real and cited — my earlier reading that it was unsubstantiated was wrong. Note the hedge is Apple's own and should not be sharpened. For the web this is `DeviceOrientationEvent`, which is permission-gated on iOS Safari and absent on desktop — so a faithful implementation is partly unreachable, which is itself worth deciding explicitly rather than leaving undecided. |
| Reacts to touch **and** pointer in real time, with **different intensity for each** | "reacts to touch and pointer interactions in real time." / "the movement of Liquid Glass responds to direct touch interaction with **greater emphasis** to reinforce the feeling of a tactile experience, but produces a **more subdued effect** when a person interacts using a trackpad." | [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views); [HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion) | `partial` — vitrea's interaction machine handles pointer events uniformly; there is no touch-versus-pointer intensity split | A cheap, well-specified fidelity win that nothing in vitrea's documents mentions. |
| **Light bleeds into the shadow** | "the effect isn't limited to the surface, the light reflects, scatters, and **bleeds into the shadow** as well – much like it would in the physical world." | S219 | `absent, undecided` | vitrea's shadow is an opacity/depth pair with no coupling to the highlight pass. |
| **Materialize / dematerialize is a distinct third state**, not a fade — with an API consequence | "Instead of fading, Liquid Glass objects **materialize** in and out by gradually modulating the light bending and lensing, ensuring a graceful transition that preserves the optical integrity of the material." / UIKit: "Always prefer setting the effect property over the alpha to ensure that the glass dematerializes or materializes with the appropriate animation." | S219; S284 | `partial` — vitrea has an `opacity/materialization` channel driven by a monotonic ease or step with no overshoot (§Motion), which is the right *channel*; whether it modulates lensing rather than alpha is unverified and untested | Directly connected to the missing `Glass.identity` (§1.1) and the missing `.materialize` transition (§1.3): these three are one capability seen from three angles. |
| WWDC26 tuned the optics: better diffusion of complex content, "a darkened edge along with brighter specular highlights" | verbatim | [WWDC26 SOTU](https://developer.apple.com/videos/play/wwdc2026/102/) | `absent, undecided` — vitrea targets 26.5 | See §1.7. This is the one row where the *reference* moved and vitrea did not. |

### 3.6 Container merging, morphing, and interactivity

The API surface is in §1.2 and §1.3; the behavioral facts follow. Apple names
three reactions to interaction and vitrea implements two of them: "Glass reacts
to user interaction by **scaling, bouncing, and shimmering**"
([S323](https://developer.apple.com/videos/play/wwdc2025/323/)) — vitrea has the
scale (press compression) and the shimmer (specular sweep) and gets the bounce
from the same spring. What it does not have is anything below the fourth row.

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| **Glass cannot sample glass** | "glass can not sample other glass, so having nearby glass elements in different containers will result in inconsistent behavior" | S323 | `replicated+measured` — and vitrea's structural analogue is *harder*: S1 established that an overlay-plane proxy **necessarily** samples the base plane's rendered output, so overlay material calibrates against a glassed backdrop | The consequence is recorded honestly: the `glass-over-glass` scenes "can never be a clean texture-tier claim" and resolve to `gpu-texture+css-backdrop` with `refraction: "approximate"` even on the GPU tier. |
| Blending is proximity-driven and continuous — "as shapes near one another, their paths start to blend" | verbatim | [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer) | `replicated+measured` (refuted at the declared spacing) — see §1.2 | The union caps (neck width, max bulge, separation threshold) are calibration-delegated and remain **unmeasured**, because the reference does not union at 12px. |
| Containers **enforce uniform adaptation** across their members | "UIGlassContainerEffect does more than just enabling animations. It **enforces a uniform adaptation**! Glass dynamically adapts to its background, but still gets a consistent appearance." | S284 | `replicated, unmeasured` — a `GlassGroup` carries one material profile and one adaptation policy for all members, and per-node `variant` falls back to the group's | An exact correspondence, and the reason vitrea's variant-mixing warning is scoped to the group. |
| Grouping is **mandatory for correctness**, not polish | "This grouping is essential for visual correctness." | S323 | `replicated+measured` | vitrea's version is stronger: a group that is not grouped does not merely look inconsistent, it fails the S1 proxy constraints (`mergeDistance ≥ samplingPadding`, cross-group proxy-rect overlap) and core reports it. |
| Shapes merge **like liquid droplets** | "As long as there is space between them, they appear as two separate views. Only if they get closer, they start **merging like small droplets of water**." / "grouped glass elements can fluidly join and separate using a liquid visual effect." | S284; [S310](https://developer.apple.com/videos/play/wwdc2025/310/) | `replicated, unmeasured` — bounded smooth-min proximity union with capped neck width, max bulge, and separation threshold "so nothing reads as jelly" (§Geometry) | The caps are calibration-delegated and remain unmeasured because the reference does not union at the declared spacing (§1.2). |
| Morphing preserves **one singular floating plane** across app states | "As you go between states in an app, Liquid Glass dynamically morphs between the controls in each context. This maintains the concept of having a **singular floating plane** that the controls live on… the controls continually shape shift." | S219 | `replicated, unmeasured` — this is X1's plane law and the cross-plane *unit promotion* rule (body, semantic host, and highlight moved together so the transition renders on one canvas pair) | vitrea derived the same invariant from a rendering constraint that Apple derived from a design intent. The strongest conceptual match in the document. |
| Presentations **morph out of the control that spawned them**, in place | "When a presentation, like a menu or a popover is originated from a glass button, **the button morphs into the overlay**." / "When showing a menu, the bubble simply pops open to reveal the content contained within. This lightweight, in-line transition keeps everything right where you just tapped." | S284; S219 | `replicated, unmeasured` — parent acceptance #4, asserted on three engines | vitrea's one morph pair is exactly Apple's canonical example. |
| Flexing / gel-like stretch that tracks the gesture | "it has an inherent **gel-like flexibility** to it that communicates its transient and malleable nature, as it moves in tandem with your interaction." / "Liquid Glass responds to interaction by instantly flexing and energizing with light." | S219 | `partial` — vitrea has press compression (~1–2%) on a velocity-preserving interruptible spring and deformation channels that Reduced Motion zeroes; no gel-like stretch and no in-tandem tracking of a continuing gesture | vitrea's press is a state transition; Apple's is a continuous deformation following the finger. |
| **The glow spreads onto nearby glass elements** | "the material illuminates from within as a form of feedback. Starting right under your fingertips, the glow spreads throughout the element and **onto any Liquid Glass elements nearby**." | S219 | `excluded by decision` — §Out of scope and §Deferred: "neighbor glow diffusion"; §Motion states plainly "the neighbor glow-diffusion field is post-v1" | A clean, correctly-identified exclusion — vitrea named this native behavior, scoped it out, and recorded it. One of very few rows where the cut list demonstrably read the reference. |
| Elements can **lift into glass transiently**, staying quiet at rest | "Elements can even lift up into Liquid Glass temporarily, such as when you interact with a component. This lets the resting state stay visually quiet, while it comes to life on touch." | S219 | `absent, undecided` | The general form of the sliders-and-toggles content-layer exception (§3.9). Expressible in vitrea's interaction machine; not offered. |
| Drag preserves **momentum and stretches** | "with sliders, in addition to the liquid glass effects on the thumb, they now **preserve momentum and stretch when they are moved**." | S284 | `excluded by decision` (Slider, §Out of scope) | |
| **Window / scene focus state changes the material** | "when a window loses focus on the Mac or iPad, Liquid Glass shifts its appearance and **visually recedes** to guide attention." OS 27 extends it: "our iPad app automatically takes on a distinct appearance when inactive." Also named as a system adaptation input: "System frameworks also dynamically adapt these components in response to factors like **element overlap and focus state**." | S219; [WWDC26 269](https://developer.apple.com/videos/play/wwdc2026/269/); ALG | `absent, undecided` | A whole state axis — independent of size, backdrop, and interaction — that vitrea's interaction machine (idle/hover/pressed/focused/disabled/morphing) has no member for. `focused` is DOM focus-within, not window activation. |
| Dragging a sheet upward makes the material **recede, opacify, and grow** | "when focus shifts, like dragging a sheet upward, Liquid Glass subtly recedes, becoming more opaque and gently growing in size to signal a deeper level of engagement." | S356 | `excluded by decision` (Sheet, §Out of scope) | Recorded because it is the same recede-on-focus-shift mechanism as the window row above, and a third instance of size-coupled opacity. |
| **New in OS 27: an explicit bounce-on-click effect** | "New in macOS 27, there is an effect that can be added to glass. Where the glass subtly bounces when clicked… use this effect with controls and buttons, or glass containers of interactive controls. A little goes a long way!" | [WWDC26 289](https://developer.apple.com/videos/play/wwdc2026/289/) | `partial` — vitrea's press compression is already a spring with overshoot removable by Reduced Motion, which is the same idea | The one row where vitrea is *ahead* of a 27.0 addition rather than behind it. |

### 3.7 Layering, elevation, and the floating-layer model

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| Glass is a **distinct functional layer above content** | "Liquid Glass forms a distinct functional layer for controls and navigation elements — like tab bars and sidebars — that floats above the content layer, establishing a clear visual hierarchy between functional elements and content." / S219: "best reserved for the navigation layer that floats above the content of your app." | HIG; S219 | `replicated+measured` — the X1 rendering sandwich, two managed planes (base + overlay), checked same-plane overlap, unit cross-plane promotion; `packages/platform-web/test/plane-law.test.ts`, `packages/platform-web/e2e/shared/promotion.spec.ts` | vitrea's plane model is the single closest structural correspondence in the whole matrix, and it was arrived at from a competitor's failure (liquidGL's all-targets-one-z-index constraint) rather than from Apple's guidance. |
| **No glass on glass** | ALG: "avoid overcrowding or layering Liquid Glass elements on top of each other." / S219: "Stacking Liquid Glass elements on top of each other can quickly make the interface feel cluttered and confusing… avoid applying the material to both layers. Instead, use fills, transparency, and vibrancy for the top elements." | ALG; S219 | `partial` — same-plane overlap is a checked dev-mode error, but **cross-plane overlap is the intended v1 morph case** and is not just permitted, it is calibrated (`glass-over-glass` scenes) | An honest divergence, not a bug: Apple forbids the stack, vitrea's menu-over-toolbar acceptance requires it. Nothing in vitrea's documents notes that the case Apple advises against is the case vitrea holds out. **Citation caveat**: the no-glass-on-glass rule does *not* appear on the HIG Materials page; its only verbatim primary home is ALG. |
| **Shadow opacity is content-aware** — the specific mechanism | "The element is aware of what's behind it and **increases the opacity of its shadow when it is over text. Conversely, it lowers the opacity of its shadow when it is over a solid light background.** This provides separation from the content to make sure elements are always easy to spot." / "As text scrolls underneath, shadows become more prominent to create additional separation. The amount of tint and the dynamic range shift to always ensure buttons remain legible." | S219 | `absent, undecided` | vitrea's `shadowDepth` and `shadowAlpha` are fixed constants with no backdrop input, and C9a deliberately left them alone because "both sides ≈0 outside the contour" (Decision Log #29a). That measurement is consistent with the mechanism: none of the six canonical backgrounds is *text over which a shadow would deepen* except `hc-text`, and that is a holdout cell. **This is a behavior the scene matrix is nearly blind to**, which is a stronger statement than "unmeasured". |
| Glass **lifts** controls that used to blend into the background | "Previously, they would blend into the background when the interface was at rest. Liquid Glass helps lift them, creating more separation from your content while reinforcing interactivity." | S356 | `replicated, unmeasured` — rim, tint and shadow all exist to provide separation, and the CSS tier's "always paints a real tint and a real border" rule is the honest-minimum version of it | |
| The scroll edge effect is the **primary** separation device, and it is not decoration | "As content begins to scroll underneath a glass element, the effect gently dissolves the content into the background, **lifting the glass visually above the moving content**." / "When darker content scrolls under, triggering the glass itself to transition to its dark style, the effect intelligently switches to apply a subtle **dimming** instead." / HIG: "Scroll edge effects aren't decorative. They don't block or darken like overlays; they exist to ensure controls stay visually distinct." + "Apply one scroll edge effect per view." | S219; [HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views) | `excluded by decision` — §Out of scope | The exclusion is a bare list entry. Apple treats this as a *legibility requirement* on by default on every system bar, with its own light/dark branch. See §5. |
| Hard style for pinned accessories | "In some cases, like when there are pinned accessory views under a toolbar, such as column headers… we use a 'hard style' effect instead… applied uniformly across the height of the toolbar and the pinned accessory view." | S219 | `excluded by decision` — same line | |
| Rounded floating forms **nest into the hardware** | "It's represented in the UI in rounded, floating forms that nest neatly in the rounded curves of modern devices." / "Glass controls nest perfectly into the rounded corners of windows, maintaining concentricity throughout the UI." | S219 | `absent, undecided` | See §3.10 — vitrea's concentricity chain has no window or display corner in it. |
| **Avoid content/glass intersection at rest** | "In steady states, such as when an app first launches, **avoid intersections between content and Liquid Glass**. Instead, reposition or scale the content to maintain separation." / HIG Color: "make sure its default or resting state… maintains clear legibility." | S219; HIG Color | `absent, undecided` | vitrea checks *glass-on-glass* overlap within a plane and never checks glass-over-content collision, which is the case Apple actually names. |
| **Non-interactive items should not be on glass** | "Non-interactive items like custom titles and status indicators should avoid the glass material. The informational text in the Photos toolbar is a great example. With the glass material backing, it almost looks like a button." | [S310](https://developer.apple.com/videos/play/wwdc2025/310/) | `absent, undecided` | vitrea's `GlassSurface` will glass a `<span>` as readily as a `<button>` and says nothing. Adjacent to the content-layer prohibition (§3.9) and equally unenforced. |
| Use glass **sparingly** | "Use Liquid Glass effects sparingly… overusing this material in multiple custom controls can provide a subpar user experience by distracting from that content. Limit these effects to the most important functional elements in your app." | HIG | `absent, undecided` as guidance; `replicated+measured` as a performance ceiling (§1.2) | vitrea enforces the *cost* of overuse via the governor and says nothing about the *taste* of it. |

### 3.8 Accessibility modes

**Sourcing warning — this is the one thin pillar, and it is thin in a specific
way.** Apple *does* state what each of the three modes substitutes, contrary to a
common assumption, but **all three statements live in a single spoken paragraph
of WWDC25 session 219**, and the [HIG Accessibility
page](https://developer.apple.com/design/human-interface-guidelines/accessibility)
mentions Liquid Glass **nowhere at all** — its change log ends 2025-06-09 and it
was never revised for the material. So this sub-table's native column rests on
one transcript passage plus one sentence of WWDC26 and an Apple Support release
note. It is well-evidenced and narrowly-sourced at the same time. Treat the
substitutions as quotable and the surrounding detail as absent.

Independently, **the native column of this whole section has no captures at
all.** Both accessibility profiles are declared in `scenes.json`
(`apple-macos-26.5-1x-light-reduced-transparency` and its increased-contrast
sibling) with zero fixtures, because macOS exposes these modes as get-only
`EnvironmentValues` and each profile needs its own capture run behind a System
Settings toggle. Parent acceptance #7 is open on exactly this. Every
`replicated+measured` below is measured against *vitrea's own* policy, never
against Apple.

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| **Reduce Transparency** → frostier, obscures more | "Reduced Transparency, makes Liquid Glass **frostier and obscures more of the content behind it**." | S219 | `replicated+measured` (against vitrea's own policy) — `reducedTransparency: { frost: "increased", refraction: "reduced", occlusion: "increased" }` (`packages/core/src/accessibility.ts`); pixel-asserted in `packages/platform-web/e2e/pixel/css-tier-pixels.spec.ts` and `packages/platform-web/e2e/shared/media-policy.spec.ts` | An **exact** three-for-two match: Apple names frost and occlusion, vitrea adds the refraction reduction as a reasoned third. vitrea also correctly notes that `prefers-reduced-transparency` is not Baseline, so the explicit `GlassRoot` override is load-bearing and emits a diagnostic when the platform cannot answer — a case the native side does not have. |
| **Increase Contrast** → near-monochrome plus a drawn border | "Increased contrast, makes elements **predominantly black or white and highlights them with a contrasting border**." | S219 | `replicated+measured` (against vitrea's own policy) — `{ border: "strong", foreground: "near-monochrome", ambientTint: "reduced" }`; `border: "strong"` is documented as "a drawn border" rather than a rim highlight | Another close match. Apple says black-or-white *elements*; vitrea says near-monochrome *foregrounds* and pulls the ambient tint back — the glass body itself is not forced to black or white. A real, small divergence. |
| **Reduce Motion** → less intensity, **no elastic properties** | "Reduced Motion **decreases the intensity of some effects and disables any elastic properties for the material**." A later refinement is recorded in the iOS 26.4 release notes: "Reduce Motion setting more reliably reduces the animations of Liquid Glass." | S219; [Apple Support 123075](https://support.apple.com/en-us/123075) | `replicated, unmeasured` — `{ overshoot: "none", deformation: "none", shimmer: "none", morph: "non-elastic", crossfade: "large-plane-shifts" }`; 15 assertions in `packages/motion/test/reduced-motion.test.ts` including "never overshoots any state-driven channel across the whole state graph" and "still redirects an interrupted press continuously" | "Disables any elastic properties" maps precisely onto vitrea's overshoot-and-deformation zeroing, and vitrea's decision to *keep* positional continuity matches the HIG's general Reduce Motion advice ("tracking animations directly with people's gestures"). Unmeasurable against the reference by construction: **no frame sequences were ever captured**, so the entire motion axis of §Calibration has no ground truth. |
| The HIG's general Reduce Motion list, which is not glass-specific but is the only list | "Tightening animation springs to reduce bounce effects; Tracking animations directly with people's gestures; Avoiding animating depth changes in z-axis layers; Replacing transitions in x-, y-, and z-axes with fades; **Avoiding animating into and out of blurs**." | [HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) | `partial` — vitrea does the first two explicitly and "reserves crossfade for large plane shifts", which is the fourth; it does not address z-axis depth or blur animation | "Avoid animating into and out of blurs" is in direct tension with materialize/dematerialize (§3.5) and neither Apple nor vitrea reconciles them. |
| Custom elements are **the developer's responsibility** to test | "If you use standard components from system frameworks, this experience adapts automatically. **Ensure you test your app's custom elements, colors, and animations with different configurations of these settings.**" | ALG | `replicated, unmeasured` | Direct obligation on a library like vitrea, and vitrea's test suite discharges it for its own policy. What it cannot discharge is agreement with Apple's rendering, for want of captures. |
| Stacked-setting caveat | "in Dark Mode with Increase Contrast and Reduce Transparency turned on (both separately and together), you may find places where dark text is less legible when it's on a dark background." | [HIG Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode) | `replicated, unmeasured` — `ACCESSIBILITY_PRECEDENCE` folds weakest-first with a recorded commutativity argument for exactly this pair | Apple names the combination as a hazard; vitrea reasons about it structurally. Neither measures it. |
| All three are **automatic and system-wide**, and are modifiers rather than replacements | "These are available automatically whenever you use the new material. So whenever these settings are turned on at a system-level, Liquid Glass elements will get them across the board." / "These act as **modifiers on the material that change certain layers** of Liquid Glass, without sacrificing its magic." | S219 | `replicated, unmeasured` — vitrea's policy resolves per root from media queries and *modifies* the material's optical axes rather than swapping a different renderer in | The "modifiers on layers, not a different material" framing is exactly vitrea's `ResolvedMaterialPolicy` shape (frost / refraction / occlusion / border / ambientTint / foreground as independent axes). Convergent design. |
| Modes **compose** rather than override | Not addressed by Apple | — | `replicated, unmeasured` — `ACCESSIBILITY_PRECEDENCE` folds weakest-first with a recorded commutativity argument; `forcedColors` last because "a platform-level colour mandate outranks every softening" | vitrea reasoning with no native counterpart. |
| **Differentiate Without Color** | **Verified negative.** The phrase appears nowhere in the full text of ~172 HIG pages, nowhere in the Technology Overviews or SwiftUI glass documentation, and in no WWDC25 or WWDC26 transcript examined. The only artifacts are the API symbols themselves (`accessibilityDifferentiateWithoutColor`, `shouldDifferentiateWithoutColor`, `differentiateWithoutColorDidChangeNotification`), which say nothing about the material. | — (negative finding) | `absent, undecided` | vitrea's `ACCESSIBILITY_FLAGS` is exactly four values and this is not one of them. It appears **once** in vitrea's documents — incidentally, in a C7 surprise about macOS environment values — and never as policy (§6). Because vitrea has no author tint, the mode is arguably moot today; it stops being moot the moment tint ships. |
| **Show Button Shapes** — Apple states the *developer obligation* and not the *system substitution* | WWDC26 SOTU, in the same breath as glass accessibility: "Liquid Glass seamlessly adapts to a variety of accessibility settings… And now macOS 27 also supports the **'show borders' environment value**, just like iOS. So you can adapt your macOS app's custom controls for this setting as well." The symbol itself: "interactive custom controls such as buttons should be drawn in such a way that their **edges and borders are clearly visible**." | [WWDC26 102](https://developer.apple.com/videos/play/wwdc2026/102/); [accessibilityShowButtonShapes](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityshowbuttonshapes) | `absent, undecided` | Never mentioned in any vitrea document (§6). Directly relevant, and the obligation is explicitly aimed at **custom controls** — which is all vitrea ships. A glass button whose only affordance is a rim highlight is precisely what this mode exists to fix, and vitrea already has a `border: "strong"` axis that would serve it unchanged. |
| `forced-colors` / a system colour mandate | Not a Liquid Glass topic in Apple's sources — it is a web platform feature with no direct native analogue | — | `replicated+measured` — `{ glass: "none", colorSource: "system", occlusion: "opaque", border: "strong", foreground: "near-monochrome" }`; asserted in `packages/platform-web/e2e/shared/media-policy.spec.ts` | A row where vitrea has a capability the native side has no equivalent for, and handles it by removing glass entirely — the right call. |
| **Accessibility is the one axis where the web side can do more than native** | — | — | n/a — a recorded asymmetry, not a gap | macOS exposes the display modes as read-only system state; vitrea sets them per-render through `accessibilityOverrides`. The *native side* is the constraint on this axis (§Surprises, C7). |

### 3.9 Legibility rules and the content-layer prohibition

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| **Do not use glass in the content layer** | "Don't use Liquid Glass in the content layer. Liquid Glass works best when it provides a clear distinction between interactive elements and content, and including it in the content layer can result in unnecessary complexity and a confusing visual hierarchy." | HIG | `absent, undecided` | **The most consequential absence in this document.** The phrase "content layer" appears **zero times** across every vitrea spec (§6). vitrea's `GlassSurface asChild` will glass any element an app hands it, including a list row, and no diagnostic objects. Apple's central prohibition has no expression in vitrea's API, its diagnostics, or its docs. |
| The rule stated for **lists and tables** by name | "Consider this tableview: making it Liquid Glass would make it compete with other elements and muddy the hierarchy. So keep it in the content layer instead to ensure clarity." | S219 | `absent, undecided` | Apple names the exact case a web glass library will get wrong. |
| **OS 27 restates it with a mechanical reason** — no scroll, nothing to refract | "avoid Liquid Glass in the content area of a view, since **with nothing scrolling underneath there's nothing for it to refract** and the simpler flat design is usually better; glass is for controls hugging the content layer." | [WWDC26 group lab 8120](https://developer.apple.com/videos/play/wwdc2026/8120/) — Apple's own written Q&A summary, not a verbatim speaker quote | `absent, undecided` | The most actionable phrasing for vitrea specifically, because it is a criterion an API could actually check: a glass surface over a static, never-scrolling backdrop is doing nothing the material exists for. vitrea already tracks a backdrop dirty epoch, so it knows this. |
| The **one** exception: transient interactive elements | "An exception to this is for controls in the content layer with a transient interactive element like sliders and toggles; in these cases, the element takes on a Liquid Glass appearance to emphasize its interactivity when a person activates it." | HIG | `excluded by decision` (Slider, Toggle, §Out of scope) — but the *behavior* is unrepresented | vitrea has interaction states, so a transient-glass surface is expressible; nothing names the pattern or offers it. |
| Controls sit on **a material**, never directly on content | "Like in Safari today, controls sit on top of a system material, not directly on content. Without that separation, contrast can suffer." | S356 | `absent, undecided` | vitrea's answer to "what goes under a control where glass would be wrong" is nothing at all — see the standard-materials row below. |
| Standard materials are the content-layer answer, in four named thicknesses | "iOS and iPadOS continue to provide four standard materials — ultra-thin, thin, regular (default), and thick." / "use standard materials for elements in the content layer, such as app backgrounds." | HIG | `absent, undecided` | vitrea ships one material. It is not obliged to ship Apple's other four — but a library that glasses arbitrary DOM and offers no content-layer alternative is structurally pushing users toward the thing Apple forbids. |
| **Vibrancy is the foreground requirement, and it is automatic** | "The label **automatically becomes vibrant**, based on its textColor. This ensures legibility against a wide variety of backgrounds." / and it applies to tints too: "just like text within a glass effect, the tint also uses a vibrant color that adapts to the content behind it." | S284; S323 | `absent, undecided` | The word "vibrancy" appears **zero times** in vitrea's documents (§6). This is not a nice-to-have: vibrancy is the mechanism by which *anything* placed on Apple's glass stays legible, it is automatic on the native side, and vitrea's foreground story is a single adaptive/near-monochrome axis plus a CSS variable. On the CSS tier this is why C9d is fixing a 4.402-versus-4.5 contrast failure at the token level — a vibrancy model would have made the foreground a function of the material rather than a token to re-derive. |
| Vibrancy has **named levels**, with a documented floor | labels: `label` (default), `secondaryLabel`, `tertiaryLabel`, `quaternaryLabel`, and "avoid using quaternary on top of the thin and ultraThin materials, because the contrast is too low"; fills: `fill`, `secondaryFill`, `tertiaryFill`; separators have a single default | HIG | `absent, undecided` | No hierarchy of foreground weights on glass exists in vitrea at all. |
| Thickness is a legibility/context tradeoff | "Thicker materials, which are more opaque, can provide better contrast for text and other elements with fine features. Thinner materials, which are more translucent, can help people retain their context." | HIG | `partial` — `thickness` is a first-class morph channel (X8) and drives lensing depth and shadow, but it is **not** wired to opacity or contrast | And it is unmeasurable: `scenes.json` declares no thickness channel, so the web side uses its own 8px default against whatever SwiftUI does — "comparing two unrelated defaults, not measuring a fidelity gap" (§Surprises, C7). |
| Choose semantically, never by apparent colour | "Avoid selecting a material or effect based on the apparent color it imparts to your interface, because system settings can change its appearance and behavior." | HIG | `replicated, unmeasured` — vitrea's variant axis is semantic (`regular`/`clear`) with no colour knob, so this is satisfied by omission | The one place where the missing tint API is arguably a virtue. |

### 3.10 Concentricity as a design rule

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| **Hardware informs the curvature** | ALG: "Across Apple platforms, the shape of the hardware informs the curvature, size, and shape of nested interface elements…" / S356: "Apple's hardware features a consistent bezel and that same precision now guides the UI, with curvature, size, and proportion aligning to create a unified rhythm between what you hold and what you see." / S219: "Glass controls nest perfectly into the rounded corners of windows." | ALG; S356; S219 | `absent, undecided` | vitrea's concentric family resolves against a *parent shape*; there is no display or window corner in the chain. `GeometryProxy.containerCornerInsets` exists natively precisely because system UI and window radii participate, and Apple even gives a platform split: "For phone layouts, use a capsule with extra margin to create space near the screen edge. For iPad and Mac, use a concentric shape that aligns with the window edge" (S356). No vitrea document mentions the viewport or window as a container. |
| **Radius matching is a function of DISTANCE from the container's corner** | S356: "By aligning radii and margins around a shared center, shapes can comfortably nest within each other." / WWDC26 289: "When a view sits near the corner of its container, its own rounded corners should follow the curve of that container. **The closer the view is to the container's corner, the more its radius should match.**" / S284: "When moving further away the corner radius decreases, to maintain concentricity automatically." | S356; [WWDC26 289](https://developer.apple.com/videos/play/wwdc2026/289/); S284 | `partial` — and the divergence is structural, not a missing knob | vitrea's concentric family is a **level-set inset of the parent's field**: the offset is uniform and position-independent, so a child near a corner and a child in the middle of the same parent resolve identically. Apple's rule is a distance gradient, which is also why `Edge.Corner.Style.concentric(minimum:)` exists — distant corners legitimately resolve to zero (§1.5). vitrea floors at a minimum radius instead of ever reaching zero. **The most rigorously measured geometry in the project implements a different rule from the one Apple states**, and no vitrea document notices. |
| The failure mode Apple tells you to look for | "keep an eye out for corners that feel too pinched — or flared. They can create tension and break the sense of balance. One place this often shows up in is nested containers — like artwork in a card." | S356 | `absent, undecided` | No diagnostic, and no calibration metric, targets pinched or flared corners specifically. |
| Nested shapes should be concentric to their containers | "Help maintain a sense of visual continuity in your interface by using rounded shapes that are concentric to their containers" | ALG | `partial` — the mechanism is measured (§1.5); **no v1 glass surface consumes it** | The one v1 consumer is the segmented-control indicator, and Decision Log #24c plus `packages/react/test/controls.test.tsx` confirm the indicator is deliberately **not** a glass node — only the track is, because X1 forbids the overlap. So vitrea's concentric family, the most rigorously measured geometry in the project, has zero glass consumers in v1. |
| The three shape types, verbatim | "fixed shapes have a constant corner radius. Capsules use a radius that's half the height of the container. And concentric shapes calculate their radius by subtracting padding from the parent's." | [S356](https://developer.apple.com/videos/play/wwdc2025/356/) | `replicated+measured` — vitrea's three v1 families are exactly `fixed`, `capsule`, `concentric` | An exact correspondence, arrived at independently. |
| Apply the material to the control, not its inner views | S356: "make sure to apply the material directly to the control, not its inner views." | S356 | `replicated` — **status corrected 2026-08-28 (Wave 1 / W4)**: the original "enforced structurally" credit was half-true — the overlap check is geometric and same-plane only, so a nested host on the overlay plane and a non-overlapping glassed list both passed silently; before W4 this row was honestly `absent`. Now enforced by the structural, cross-plane `glass-inside-glass` dev-mode error (`packages/platform-web/src/layer-model.ts`). | See the Wave 1 spec's Surprises: the overlap finding's own remediation advice, followed on a glass-on-glass nesting, silenced the only check that fired. |

### 3.11 Performance

| native behavior | what Apple says | citation | vitrea status | notes |
| --- | --- | --- | --- | --- |
| Combine custom effects into a container for performance | "make sure to combine them using a GlassEffectContainer, which helps optimize performance while fluidly morphing Liquid Glass shapes into each other." / AppKit's container exists for "reducing the number of passes required to render similar glass effect views." | ALG; [NSGlassEffectContainerView](https://developer.apple.com/documentation/appkit/nsglasseffectcontainerview) | `replicated+measured` — per-group field pass (instances → group field → one optical pass); blur/analysis pyramids belong to `BackdropSource` and rebuild at most once per dirty source per frame | vitrea's invariant is stricter and is enforced by a test (`packages/renderer-webgpu/test/dirty-epoch.test.ts`). |
| The mechanism behind the saving is **one sampling pass per group** | Grouping "improves the performance of the glass effect, since it only needs **one sampling pass for the entire group**." | [S310](https://developer.apple.com/videos/play/wwdc2025/310/) | `replicated+measured` — vitrea's group field pass is exactly this: instances → one group SDF/coverage field → one optical pass, with blur/analysis pyramids owned by the `BackdropSource` and rebuilt at most once per dirty source per frame (`packages/renderer-webgpu/test/dirty-epoch.test.ts`) | Apple states the property; vitrea enforces it with a test. |
| Limit simultaneous effects | "Creating too many Liquid Glass effect containers and applying too many effects to views outside of containers can degrade performance." | ALG | `replicated+measured` — the quality governor, with long hysteresis and cooldown, never switching tiers mid-interaction | Measured against vitrea's own 2ms hypothesis: mobile 1.47ms median, desktop 2.20ms, **p95 over budget on both**. Apple publishes no budget to compare against — every quantitative performance statement in this row is vitrea's own. |
| OS 27 makes glass a named target of a new profiling metric | "The new hitches metric surfaces issues in more places than scrolling, like understanding how apps use Liquid Glass and SwiftUI views." | [WWDC26 258](https://developer.apple.com/videos/play/wwdc2026/258/) | n/a | Apple treating glass cost as a first-class profiling concern corroborates that vitrea's governor is not over-engineering. |
| **Not Apple's guidance** — a third-party engineering talk hosted by Apple | CNN's team: "The effect is GPU intensive, especially in scrollable or frequently updated views. We limit its use in high frequency UI areas like list and animations, reserving it for static or top level components like the tab bar and toolbars." And on nesting: applying the effect to both parent and child "led to visual redundancy and double translucency with layered blur and unpredictable rendering." | [Meet with Apple 256](https://developer.apple.com/videos/play/meet-with-apple/256/) | n/a | Flagged explicitly so it is never quoted as Apple's position. It is a practitioner report — and it independently reproduces both the glass-on-glass hazard and the content-layer rule from the field. |
| tvOS hardware floor: Apple TV 4K (2nd gen) and newer; older devices keep the current appearance | verbatim | ALG | n/a — but the analogue exists | vitrea's honest-degradation ladder (WebGPU → CSS with an enumerated `demotionReason`) is the same idea expressed for a different substrate, and is parent acceptance #5. |

---

## 4. Headline numbers

174 native items enumerated across the three layers. 20 of them have no vitrea
analogue by nature rather than by omission (AppKit expressing the same material a
third time, visionOS's older unrelated material, tvOS focus gating, Apple
documenting no rule for a thing vitrea also has no rule for). That leaves **154
rows on which vitrea can be scored.**

| layer | rows | `replicated+measured` | `replicated, unmeasured` | `partial` | `excluded by decision` | `absent, undecided` | n/a |
| --- | --- | --- | --- | --- | --- | --- | --- |
| §1 Material API surface | 52 | 10 | 5 | 10 | 4 | **13** | 10 |
| §2 Component families | 26 | 1 | 2 | 3 | 7 | **10** | 3 |
| §3 Behavioral system | 96 | 14 | 16 | 17 | 7 | **35** | 7 |
| **total** | **174** | **25** | **23** | **30** | **18** | **58** | **20** |

Read as proportions of the 154 scoreable rows:

- **16% (25) are replicated and measured.** This is the honest ceiling of what
  vitrea can currently claim, and it is concentrated in three places: the plane
  and sandwich model, the container-sampling constraint, and the corner geometry.
- **15% (23) are replicated but unmeasured** — built, tested for mechanics, never
  compared to the reference. The motion axis is the bulk of it, and it is
  unmeasured for a hard reason: no frame sequences were ever captured.
- **19% (30) are partial** — one half present. Almost every one of these is the
  same shape: vitrea has the *channel* and not the *law that drives it*
  (thickness exists but is not wired to opacity; foreground adapts but mirrors a
  material flip that no longer happens; lensing scales with size but shadow does
  not).
- **12% (18) are excluded by a recorded decision.** Every one traces to a
  §Out of scope line or a Decision Log entry. Only one of them — neighbour glow
  diffusion — was excluded with the native behavior explicitly named.
- **38% (58) are absent and undecided.** This is the number the document exists
  to produce. It is not a to-do list; most of these items are correctly out of a
  v1's reach. What matters is that **58 native items have never been ruled on**,
  and a v1 cut list of 18 entries against 58 unconsidered items means the cut
  list was not written against an enumeration of the reference.

Three cross-cutting facts the per-layer table hides:

1. **The component layer is where vitrea is thinnest, and it is thinnest by
   design.** One measured row out of 26. That is the correct trade for a v1 whose
   thesis is the *material*, not the widget set — but it means the phrase
   "Liquid Glass for the web" is carrying far more weight in the component
   dimension than the code supports.
2. **Two of the four declared calibration profiles have zero captures**, both
   accessibility modes, and the canonical 2× keys are unreachable on the capture
   machine. So the accessibility rows in §3.8 and every 2× claim rest on
   vitrea's own policy and nothing else. Parent acceptance #7 is open on exactly
   this, and its blocker is a human toggling System Settings, not code.
3. **The reference has already moved.** vitrea calibrates against macOS 26.5;
   OS 27 tuned the material's diffusion, added a darkened edge and brighter
   specular highlights, and added a user-facing tint slider — all reaching
   existing apps with no recompile. Nothing in vitrea's roadmap prices a
   reference refresh, and Apple explicitly warns that glass "can appear
   differently between system versions."

## 5. The three highest-value absences, for a post-v1 roadmap

Chosen on evidence rather than effort: each is measured or measurable, each
blocks a claim vitrea already wants to make, and each is a *system* rather than a
feature.

**1. The size term on the material — opacity first, then shadow and scattering.**
The reference passes 0.88 of the backdrop at a 32px span and 0.56 at 96px; vitrea
passes one fitted constant at every size. This is the only open gap that is
already quantified, already named as a parent-impact item, already the identified
mechanism behind the holdout overfitting signal, and already implicated in five
separate native rows (§3.2). It is also the gap that makes the *existing* claim
weaker than it needs to be: a single `tintAlpha` fitted across a size sweep must
over-opacify the large end and under-opacify the small end, so every cell in the
matrix is paying for its absence. Nothing else on this list improves a number
that is already published.

**2. An author-facing tint — implemented as Apple implements it, or not at
all.** `Glass.tint(_:)` and `UIGlassEffect.tintColor` are the material's only
emphasis mechanism, and their absence cascades: no prominent button style (§1.6),
no way to follow Apple's "apply color to the background rather than to symbols"
guidance (§3.4), and Differentiate Without Color stays moot only because there is
no colour to differentiate (§3.8). The reason this belongs on the list rather
than in a corner is the trap: Apple's tint is not a fill but "a range of tones
mapped to content brightness underneath… changing its hue, brightness and
saturation depending on what's behind," with vibrancy — and Apple names the flat
alternative as a failure ("a solid fill… breaks the visual character of Liquid
Glass"). Today an author reaching for emphasis in vitrea has no option *but* the
failure mode. Shipping the naive version would be worse than shipping nothing,
which is precisely why it needs a decision rather than a backlog entry.

**3. The content-layer prohibition, as an enforced contract rather than
guidance.** Apple's single most emphatic rule — "Don't use Liquid Glass in the
content layer", restated for tables by name, restated again at OS 27 with a
mechanical reason ("with nothing scrolling underneath there's nothing for it to
refract") — has zero expression anywhere in vitrea: not in the API, not in a
diagnostic, not in the docs, and the phrase itself appears nowhere in any spec.
Meanwhile `GlassSurface asChild` will glass a list row, a `<span>`, or a static
page background without comment. This is the highest-leverage item on the list
because it costs the least and protects the most: vitrea already has a diagnostics
channel, already tracks a backdrop dirty epoch (so it knows when nothing scrolls
underneath), and already ships dev-mode errors for overlap and clear-without-
dimming. A project whose stated tiebreaker is fidelity is currently silent on the
one rule Apple repeats most, and a library that makes the forbidden thing the
easy thing will be measured on what its users ship, not on its calibration cells.

## 6. Flagged prominently — native items the composite spec never mentions

Every item below was checked by grep across `docs/doperpowers/specs/` and
`docs/doperpowers/spikes/`. "Never mentioned" means **zero occurrences** in the
composite spec and in `c9a-fidelity-claims.md`. These are not disagreements with
vitrea's scope; they are things vitrea's scope never had an opinion about, which
is a different and more useful finding.

**Material API — never mentioned:**

- `Glass.identity` — the documented way to animate glass to nothing in place.
  Every "identity" hit in the spec is byte-identity or an unrelated phrase.
- `glassEffectUnion(id:namespace:)` — union by shared identity, at rest,
  independent of distance. vitrea unions by proximity only.
- `GlassEffectTransition`, `matchedGeometry`, `materialize` — the named transition
  kinds. vitrea has one hardcoded morph behaviour and no vocabulary for the other.
- `backgroundExtensionEffect()` / `UIBackgroundExtensionView` /
  `NSBackgroundExtensionView` — and note this is *not* covered by the scroll-edge
  exclusion. It mirrors adjacent content and blurs the copies.
- `safeAreaBar(edge:…)` — the glass-aware safe-area inset.
- The glass button styles by name: `.glass`, `.glassProminent`, `glass(_:)`,
  `GlassButtonStyle`, `GlassProminentButtonStyle`. The word "prominent" appears
  zero times anywhere in vitrea's documents.
- `ToolbarSpacer` and `sharedBackgroundVisibility(_:)` — the entire vocabulary for
  splitting a toolbar's shared glass background, which vitrea's `GlassToolbar`
  cannot do.
- The toolbar-minimization family and `tabBarMinimizeBehavior` — the bars-recede
  behaviour, in both its 26.0 and 27.0 forms.
- `UIDesignRequiresCompatibility` — the native opt-out, and the fact that OS 27
  removes it.
- Platform scoping: `tvOS`, `watchOS`, and `visionOS` appear nowhere as
  considerations, including the fact that the core glass symbols deliberately
  exclude visionOS while the concentricity and scroll-edge symbols include it.

**Behavioral system — never mentioned:**

- **"content layer"** — zero occurrences. Apple's central prohibition, and the
  name of the thing glass is defined against. See §5, item 3.
- **"vibrancy"** — zero occurrences. The mechanism by which anything placed on
  Apple's glass stays legible, automatic on the native side.
- **The 35% dimming figure** — zero occurrences, despite being the only number
  Apple publishes about this material and despite clear-variant dimming being an
  explicitly calibration-delegated unknown in vitrea's own spec. It was free.
- **Size-gated behavioral switching** — that small elements flip light/dark and
  large ones deliberately do not, because "their surface area is too big and
  transitions like these would be distracting."
- **Ambient colour spill onto large surfaces** from nearby (not behind) content
  — "spill" has zero occurrences. (The word "ambient" does appear four times,
  but only as "reduced ambient tint" in the accessibility policy, a different
  quantity entirely.)
- **Content-aware shadow opacity** — shadow deepening over text and lightening
  over solid light backgrounds. vitrea's shadow has no backdrop input, and the
  canonical scene matrix is nearly blind to the behavior.
- **Window / scene focus state** as a material state axis — glass receding when a
  window loses focus, and "element overlap and focus state" being named by Apple
  as system-managed adaptation inputs.
- **Touch versus pointer intensity** — Apple gives direct touch "greater
  emphasis" and a trackpad "a more subdued effect."
- **Motion-reactive specular highlights** — hedged by Apple ("in some cases"),
  unhedged in its consumer material, and unreachable on desktop web, which is a
  reason to decide explicitly rather than a reason to be silent.
- **Show Button Shapes / `accessibilityShowButtonShapes`** — and Apple's
  obligation here is aimed specifically at *custom controls*, which is all vitrea
  ships. vitrea already has the `border: "strong"` axis that would serve it.
- **Differentiate Without Color** — appears once, incidentally, in a C7 surprise
  about which macOS environment values are writable. Never as policy. (Apple in
  turn documents no relationship between this mode and Liquid Glass at all, so
  this one is a shared blank rather than a one-sided gap.)
- **The concentricity distance gradient** — "the closer the view is to the
  container's corner, the more its radius should match." vitrea's level-set inset
  is position-independent, so the most rigorously measured geometry in the
  project implements a different rule from the one Apple states, and no vitrea
  document notices.
- **Hardware and window corners as the top of the concentricity chain** — the
  viewport as a container.
- **Non-interactive elements should not be glass** — titles and status
  indicators. `GlassSurface` glasses a `<span>` without comment.
- **Glass/content intersection at rest** — Apple says reposition or scale the
  content; vitrea checks glass-on-glass overlap and never glass-over-content.
- **Materialize / dematerialize as lensing modulation rather than a fade**,
  including the explicit UIKit instruction to animate the effect and never the
  alpha.
- **App icons and widgets** as members of the Liquid Glass system — including
  that widget glass is user-selected and involves desaturation, and that icon
  glass in clear mode is deliberately pinned *outside* the OS 27 user slider.
- **Keyboard accessory views** — the clearest automatic-versus-opt-in statement
  Apple publishes. ("accessory" has zero occurrences; the single "keyboard"
  hit is acceptance #1's IME requirement, unrelated to the accessory bar.)

**Also never mentioned, and this one is about vitrea's own premise:** Apple's
explicit disclaimer that these effects "can appear differently between system
versions", and the fact that OS 27 has already changed the material's diffusion,
edge, and specular highlights with no recompile required. vitrea's fidelity claim
is correctly profile-keyed, which means it is *structurally* honest about this —
but no vitrea document states that the reference is a moving target or prices the
cost of tracking it.

---

*Compiled 2026-08-25. Native side: Apple DocC JSON, HIG page text, and WWDC
transcripts as cited per row. vitrea side: `main` at 24c4a7d, with K5 (CSS-tier
opacity coherence) and C9d (release gates) in flight — neither changes any row's
status, and K5's landing is what would move the dom tier's rows in §3 out of
"more than 2× out of step with the texture tier."*

---

## 7. Re-scored 2026-09-10, beside the August reading

Every row above was scored again against `main` at `c5b3320` (W26 recomposed,
0.15.0), sixteen days and twenty-six waves after §4 was written. The per-row
tables with their citations are in
[`2026-09-10-coverage-rescore.md`](./2026-09-10-coverage-rescore.md); the
August column there is reconstructed from git so that the in-place annotations
W2 and W7 left in §3.2 and §3.3 do not contaminate it, and it reproduces §4's
counts exactly. The tables above are left as written.

| layer | rows | `replicated+measured` | `replicated, unmeasured` | `partial` | `excluded by decision` | `absent, undecided` | n/a |
| --- | --- | --- | --- | --- | --- | --- | --- |
| §1 Material API surface | 52 | 10 → **14** | 5 → 4 | 10 → 8 | 4 → 4 | 13 → **12** | 10 → 10 |
| §2 Component families | 26 | 1 → 1 | 2 → **3** | 3 → 3 | 7 → 7 | 10 → 10 | 3 → 2 |
| §3 Behavioral system | 96 | 14 → **26** | 16 → 18 | 17 → 15 | 7 → **12** | 35 → **18** | 7 → 7 |
| **total** | **174** | **25 → 41** | **23 → 25** | **30 → 26** | **18 → 23** | **58 → 40** | **20 → 19** |

As proportions of the 155 scoreable rows: replicated and measured 16% → **26%**;
replicated, unmeasured 15% → 16%; partial 19% → 17%; excluded by decision 12% →
15%; absent and never ruled on 38% → **26%**.

**Where the movement came from.** Thirty-three rows moved, thirty-two of them
toward a build or a ruling and one away. Most trace to the post-v1 wave's first
eight children (W1–W8, closed 2026-09-01) and the tint waves: the author tint
(W3, W10, W19) closed §5's second absence and four §3.4 rows; the size law and
tone adaptation (W2, W7, W9) closed §5's first absence and four of §3.2's five
facets; the content-layer contract (W4) turned Apple's prohibition into two
diagnostics and, by refusing three others with reasons, moved three `absent`
rows to `excluded by decision`; the outer shadow (W8) and the capture campaign
(W1, fixtures behind both accessibility profiles and both scales) did the rest.
The eighteen fidelity waves since 2026-09-01 (W9–W26) moved six rows between
them — W14's light-bleed and content-aware-shadow pair, W18's measurement of
the rest-state blending rule, W21's scheme-selection pair, and W22's one move
downward (§1.1's `interactive`, when the resting specular was found to be the
sweep's parked idle phase) — and strengthened the evidence under a dozen
others without changing a verdict.

**The forty rows still `absent, undecided`,** grouped by what would close them:

- *The material's missing transitions and identities* — `Glass.identity`, the
  `materialize` transition kind, `glassEffectUnion` by shared id. The motion
  kernel's `materialization` channel exists with nothing public reaching it.
- *The foreground* — vibrancy as the automatic legibility model, its named
  levels and floor, label/background colour collision. Still a token path; the
  word appears in two doc comments and no runtime.
- *Chrome the material sits in* — `safeAreaBar`, `backgroundExtensionEffect`,
  toolbar minimization, toolbar group splitting (a `groupId` lever exists; the
  declarative spacer and ergonomics do not), navigation bars, sidebars, text
  fields, steppers, alerts, action sheets, windows, widgets, icons, keyboard
  accessories.
- *States the material has and vitrea does not* — ambient colour spill from
  nearby content, transient lift-into-glass, device-motion speculars, the
  clear variant's three preconditions, dimming that may be omitted, localized,
  or used as a modality signal. (Window focus moved to `excluded by decision`
  with its reference bed preserved; it is a decision, not a gap.)
- *Concentricity's outer end* — hardware and window corners at the top of the
  chain, the pinched/flared diagnostic, the read-back accessors.
- *Accessibility inputs* — Differentiate Without Color, Show Button Shapes.
- *The reference's own drift* — the OS 27 material and its user-facing slider.

**Five August readings that were wrong on the day, not stale** (the companion
file argues each): `Glass.clear` credited a dimming layer no renderer paints;
`Glass.interactive` credited a shimmer that was the sweep's idle phase;
`glassEffectID` credited a `morphNamespace` that nothing reads; the concentric
read-back was already reachable internally; toolbar splitting already had a
`groupId` lever. Two §3 rows earned their unchanged status through different
code than the one credited (the control-not-inner-views check, which W4 built
after the geometric one was found blind; the capsule, which W20 found clamped
since v1).

**Native behaviors the matrix never enumerated,** found by measuring rather
than reading: Apple's rendered layer tree as a source (the container blends at
`smoothness == spacing` with no separation threshold, which no document states
and vitrea diverges from above 16); the tint's strength axis and its
encoded-space law; the corner saturation rule (radius kept, shoulder
compressed); material selection by appearance as distinct from backdrop tone;
the outer shadow's two terms; the body as a depth-graded sharp/heavy mixture;
the rim's diagonal and along-side fields; the collapsed rim's absolute floor;
two settled appearances under identical attested conditions; and a thin dark
appearance selected by scene content beyond the surface's footprint.

Two of §4's three cross-cutting facts changed. The accessibility profiles and
the 2x keys have captures now, and every claim on them is against Apple. The
component layer is still one measured row of 26, by the same deliberate trade.
The third, that the reference has already moved, is unchanged: after
twenty-six waves every profile key still reads `apple-macos-26.5`.

---

### Re-scored 2026-09-14 after W27, beside the 2026-09-10 reading

W27 (`2026-09-10-w27-coverage-wave.md`) closed on 2026-09-14 with its Decision Log 20. Its
Parent-Level Acceptance clause 1 named the rows the wave undertook to move by build; this is that
re-score, against `main` at `d3d3163`. **Seven rows move, one row is added, and one row the charter
named holds where it was.** The 2026-09-10 table above is left as written and no row's earlier
record is rewritten.

| row | matrix | 2026-09-10 | 2026-09-14 | evidence |
| --- | --- | --- | --- | --- |
| `Glass.identity` | §1.1 | `absent, undecided` | **`replicated, unmeasured`** | `GlassSurface present={false}`, `registerHost({ present })` and `handle.update({ present })` retarget the motion kernel's `materialization` driver; at presence 0 the material is absent while the host DOM, geometry, semantics and content remain, and an initially absent surface starts at identity with no entrance animation. Presence 1 is byte-identical to the undriven render and presence 0 to omitting the surface; no golden was re-recorded. Claims §5.132. Unmeasured because there is no native frame sequence for this transition: the 220 ms ease and intermediate optical trajectory are authored and unmeasured against Apple. The GPU deltas at presence 0.70 and 0.35 are reach proofs against vitrea's own endpoints, not errors against Apple |
| `GlassEffectTransition` kinds | §1.3 | `partial` | **`replicated, unmeasured`** | `GlassMorphTransition = "matchedGeometry" \| "materialize"` (`packages/react/src/morph.tsx`, exported at `index.ts`); `matchedGeometry` stays the default, while `materialize` registers source and destination as distinct surfaces on their own measured boxes, drives presence out and in without interpolating geometry, and crossfades content only. With `present={false}` as the identity case, all three of Apple's kinds now have a vitrea form and a name. Claims §5.132. Same motion-axis reason |
| Materialize / dematerialize is not a fade | §3.5 | `partial` | **`replicated, unmeasured`** | Presence scales lens depth, body mix, tint alpha, rim, inner and outer shadow and glow, and never the element's opacity — no host or ancestor opacity is written, which is also what keeps the group's proxy sampling alive. The August row's “whether it modulates lensing rather than alpha is unverified and untested” is closed by `packages/renderer-webgpu/e2e/gpu/materialization.spec.ts` and `packages/platform-web/test/css-presence.test.ts`. Claims §5.132. Same motion-axis reason |
| Toolbar-group glass management (`ToolbarSpacer`, `sharedBackgroundVisibility`) | §1.6 | `absent, undecided` | **`replicated, unmeasured`** | `GlassToolbarSpacer` (`kind: "fixed" \| "flexible"`) and the published `GlassToolbarItemProps` — `sharedBackground: "shared" \| "hidden"` plus `groupProps` — partition a toolbar's children into N sampling groups while one `role="toolbar"` and one document-wide roving tab stop survive (`packages/react/src/controls/toolbar.tsx`; `packages/react/test/toolbar-partition.test.tsx`, `packages/react/e2e/toolbar-partition.spec.ts`, `packages/react/e2e/semantics.spec.ts`). The gap clears the live policy-derived padding, published as `samplingPaddingFor` (`packages/platform-web/src/optics.ts`) and proved on real proxies at nominal and Reduce Transparency settings (`packages/platform-web/e2e/shared/accessible-padding.spec.ts`). **Recorded, not scored:** the framework-agnostic path adds no named toolbar option — a non-React app splits through the existing `registerGroup` / `groupId` primitives and clears `samplingPaddingFor` itself. Unmeasured for a stated reason: `apps/reference-apple/scenes.json` carries `toolbar-group__rest` and `toolbar-group__inactive` and no split scene; the wave's eye sheet compares split against unsplit in vitrea's own harness, never against Apple |
| `GlassButtonStyle` / `GlassProminentButtonStyle` | §1.6 | `partial` | **`partial` — unchanged; the plain half moved and the row did not** | The row's recorded blocker — `tint` absent from `GlassButtonProps`' allow-list — is closed by W27a: `GlassButton` and `GlassIconButton` forward `tint` and `foreground` (`packages/react/src/controls/button.tsx`), so **ordinary `Glass.tint` on buttons is replicated and measured** — on the tinted capsule-button cells `photo__capsule-button__rest-tint-orange` and `checkerboard__capsule-button__rest-tint-blue`, and shown live in `apps/demo/src/TintInkPlate.tsx`. That is what clause 1 asked of this row, and it is met. The row itself names two styles and **the prominent form is still absent** — now held by a recorded ruling, W27 Decision Log 6, rather than unruled — so the row keeps `partial`: scoring the pair `replicated+measured` would credit a style nothing in the repo renders. §1.6's `UIButton.Configuration` row keeps `partial` for the same reason, the two prominent forms being the whole of its gap |
| Window / scene focus state changes the material | §3.6 | `excluded by decision` | **`partial` — the measured half, not the runtime half** | Apple's inactive material is measured end to end. §5.128 read **121 matched native-to-native cells over 37 scenes** with byte-identical backgrounds and found the broad outer shadow gone beyond 2 CSS px in all 121, the bright rim gone in standard and reduced-transparency profiles, hue nearly eliminated and tint strength surviving as an achromatic body-level change; it fitted nothing. §5.130 fitted the scheme-conditioned endpoint, §5.134 classified the residuals and declared a bound, §5.139 read the checking bed, §5.141 fitted the accessibility recede and refused the dark far ordinate, and §5.143 captured a fresh 26.5.2 neutral anchor — fourteen runs, 4/4 attested inactive each — that put the response step in the abscissa, re-fitted the dark response on four knots (mean body ΔE 0.15771 → 0.01502 under a 9× refusal cap) and split the accessibility level per policy (0.88 / 0.98). The frozen holdout was read once and the unchanged bound scored once: **it holds on four of six profiles**, failing clause 3 on light standard 1x and 2x at `hc-text__rrect-sm__inactive` (2.44× / 2.15×). **No inactive floor was adopted.** The endpoint ships as `recededMaterialProfile` (`packages/platform-web/src/receded-profile.ts`) and nothing consumes it: no `windowActivation` option or prop, no focus observer and no React export. W27 Decision Log 20 rules that G2 and G3 stay held and that the profile documents, four-knot response and per-policy level ship inert. Clause 1 asked for `replicated+measured`; the wave did not earn it, and this row records the wave rather than the charter |
| Vibrancy is the foreground requirement, and it is automatic | §3.9 | `absent, undecided` | **`replicated+measured`** | Apple's operator is read from the committed macOS layer dumps: 50 2x dumps, 26 labelled, of which the 24 automatic-colour labels carry `vibrantColorMatrix` and the two authored-colour labels do not; both scheme matrices reproduce with **zero residual** at `inputBackdropAware=1`, `inputClamp=1`, pinned in `packages/calibration/test/vibrancy.test.ts` (§5.133, §5.137). Derived semantics — saturating source-over, black at glyph coverage in light, white at 0.95 × coverage in dark — were proved in the browser over 448 synthetic cells against a bound declared at 1 code value and **measured at 0.54** (§5.137). §5.140 ships it as a CPU fold on both tiers with no per-pixel filter; `foreground` defaults to `"vibrant"` on `GlassButton`, `GlassIconButton` and `GlassSegmentedControl`, the labels vitrea owns. Arbitrary `GlassSurface asChild` content keeps the token and opts in with `foreground="vibrant"`. **No native label pixel exists**, so the Apple-side claim is the coefficient and configuration reading, never a label-pixel comparison — the no-text fixture rule stands |
| Vibrancy has named levels, with a documented floor | §3.9 | `absent, undecided` | **`replicated+measured`** | `FOREGROUND_LEVELS = ["secondary", "tertiary", "quaternary"]` beneath the default, published on both tiers with per-level custom properties (`packages/platform-web/src/vibrancy.ts`, `css-tier.ts`, `root.ts`), secondary solved per surface against the actual composite over the whole bracket and collapsed onto primary where primary itself cannot reach 4.5 (W27 Decision Log 9; §5.140). §5.142 measures **53 unique route/family/text combinations, 411 readings per tier-and-scheme cell, 1,644 total**, every visible glyph inside glass across `/`, `/laws/` and `/playground/`, with dynamic scenes sampled at four phases. Floors: semantic body labels 4.5, qualifying large labels 3.0, secondary 4.45 CSS / 4.25 WebGPU; tertiary and quaternary are read-only but must hold ladder order. Weakest final margins 3.021 / 3.057, 4.644 / 4.508 and 4.463 / 4.278. Only the 0.95 dark factor is read from Apple's dumps; the 0.847059 base alpha and the four-level ladder are documentation-sourced, and these are vitrea rendered-pixel regression floors, not Apple bounds. The secondary's 0.037 shortfall is attributed to the ideal-composite solve differing from the rendered material plus 8-bit recovery, and tracked |
| **The WebGPU tier over a DOM-sourced group draws the profile's material, not an unsampled flat** — a row the matrix never enumerated, added here under §3.7 | §3.7 | — (new) | **`replicated+measured`** | Over a `css-backdrop` group the renderer painted an `unsampledMaterial` of `tint [1, 1, 1]` at α 0.665 (claims §5.77 §4). W27f replaces it with the profile's response, size, collapse, shade, rim and shadow laws evaluated at the known backdrop tone through `materialAtBackdrop` (`packages/platform-web/src/optics.ts`) and mirrored per pixel in the GPU optics shader so a merged group keeps each member's span, with no lens; the author hint wins, then a measured tone, and where tone is unknown response and collapse are not invented. §5.129 measured the flat's miss, §5.131 the derived material, and **§5.135 adopted the bound**: declared at `9edaa0b`, before the first capture, on three native stack cells over 308 captures, and met in both clauses on all nine rows, with the sampled path byte-identical at the landing head. Shipped since 0.16.0. Recorded limits: Clause B is tighter than A on all nine rows, so dark checker is frozen at its regression (hinted overlay ΔE 0.011332 → 0.013059, S1 0.013765 → 0.016702); dark photo has no native fixture; instrument stop S4 was tripped and scoped to the WebGPU arms by Decision Log 14; refraction over DOM stays a seam. The canonical matrix has no WebGPU-over-DOM cell type, so the 20 ordinary readings live in `packages/calibration/results/2026-09-11-w27f-g2/` and `adopted-thresholds.test.ts` asserts the committed ledger rather than regenerating captures — evidence weaker than a live matrix floor, and named as such |

| layer | rows | `replicated+measured` | `replicated, unmeasured` | `partial` | `excluded by decision` | `absent, undecided` | n/a |
| --- | --- | --- | --- | --- | --- | --- | --- |
| §1 Material API surface | 52 | 14 → 14 | 4 → **7** | 8 → **7** | 4 → 4 | 12 → **10** | 10 → 10 |
| §2 Component families | 26 | 1 → 1 | 3 → 3 | 3 → 3 | 7 → 7 | 10 → 10 | 2 → 2 |
| §3 Behavioral system | 96 → **97** | 26 → **29** | 18 → **19** | 15 → 15 | 12 → **11** | 18 → **16** | 7 → 7 |
| **total** | **174 → 175** | **41 → 44** | **25 → 29** | **26 → 25** | **23 → 22** | **40 → 36** | **19 → 19** |

As proportions of the **156** scoreable rows (155 plus the row added under §3.7): replicated and
measured 26% → **28%**; replicated, unmeasured 16% → **19%**; partial 17% → 16%; excluded by
decision 15% → 14%; absent and never ruled on 26% → **23%**. The single net `partial` row the wave
retired is §1's `GlassEffectTransition` kinds; the button pair beside it holds `partial` on the
prominent style, which is why §1 falls by one rather than two and why `replicated+measured` gains
three rows rather than four. §3's `partial` count is unchanged at 15 and its composition is not:
materialize left it upward, while window focus entered it from `excluded by decision`.

**Where the movement came from, and where it did not.** Three rows are one capability seen from
three angles: W27d's authored presence closes `Glass.identity`, the `materialize` transition kind
and materialize-is-not-a-fade together, and all three stop at `replicated, unmeasured` because no
frame sequence of Apple's transition exists. The motion axis remains the largest unmeasured thing in
the project. The other moves are W27b's toolbar partition and W27e's operator and named ink levels;
W27f's page material is the row added beside them rather than one that moved. Two rows clause 1 named
did not move as rows. W27a's button tint is replicated
and measured, but it shares a row with `GlassProminentButtonStyle`, which is absent, so the row
holds `partial` and the capability is credited inside it. And clause 1 named window focus
`replicated+measured`; it is not, and the row above says why.

**A reading this re-score is careful about.** The vibrancy rows are measured against Apple's
operator, read exactly from 26 committed layer dumps, and against vitrea's own rendered pixels —
never against a pixel of Apple's text, because no such fixture exists under the no-text rule. The
§3.7 row's bound is enforced by asserting a committed ledger, not by a regenerating floor. Each is a
real measurement against Apple and each is named for what it is; neither has the same evidence shape
as the matrix's live calibration cells.

**The six rows W27 built and this re-score did not move.** §1.6's `GlassButtonStyle` pair keeps
`partial`, its row above recording the tint half as replicated and measured and the prominent style
as absent. §2's *Toolbars / toolbar items* keeps
`partial`: the split changes grouping, while the bar itself is still not a registered surface and
bar-concentric radii stay unexpressible. §2's *Custom views* keeps `partial`: identity and the named
transitions are closed, `glassEffectUnion` by shared id is not. §1.3's union row stays
`absent, undecided`; presence is per surface and unions remain proximity-only. §1.6's
`UIButton.Configuration` stays `partial` because the prominent forms are its remaining gap. §3.9's
*Controls sit on material, not directly on content* stays `absent, undecided`: W27f changed what
draws over page content, not whether a separation rule exists.

The thirty-six rows still `absent, undecided` are the 2026-09-10 list less the four closed here. What
remains is the chrome the material sits in, the states vitrea does not have, concentricity's outer
end, two accessibility inputs and the reference's own drift. After twenty-seven waves every profile
key still reads `apple-macos-26.5`; W27's charter opened by observing that reference being
superseded.

---

### Re-scored 2026-09-15 after W28, beside the 2026-09-14 reading

W28 (`2026-09-14-w28-footprint-response.md`) built the footprint abscissa the inactive response
needed, held the unchanged bound on all six profiles, shipped the window-activation runtime and
published the inactive rows. **One row moves, none is added, none moves downward.** The two tables
above are left as written and no row's earlier record is rewritten.

| row | matrix | 2026-09-14 | 2026-09-15 | evidence |
| --- | --- | --- | --- | --- |
| Window / scene focus state changes the material | §3.6 | `partial` — the measured half, not the runtime half | **`replicated+measured`** | The 2026-09-14 cell named its own blocker: "the endpoint ships as `recededMaterialProfile` … and nothing consumes it: no `windowActivation` option or prop, no focus observer and no React export." All three exist. **Measured:** W28 G0 read the response's abscissa from 398 committed native cells with the checking set excluded and a curve-free statistic, and returned *not identifiable from this bed* (§5.144); Decision Log 2 ruled the simplest survivor built and the bound as referee; G1 landed the per-surface silhouette abscissa profile-gated on both tiers and refitted the receded rows on non-D cells, sealed at `6d7465c9` (§5.145); G2 ran the sealed reader once — 188 WebGPU rows, six holdouts admitted once — and scored the **unchanged** 2026-09-11 bound, which **holds clauses 1–3 jointly on all six profiles**, 72 / 72 checking cells under their caps (§5.146). The cell that held W27c, light `hc-text__rrect-sm__inactive`, went from 2.44× / 2.15× its clause-3 floor to **0.9269× / 0.8023×** of its ceiling. **Replicated:** `createGlassRoot({ windowActivation })` with `"auto" \| "active" \| "inactive"`, `root.setWindowActivation`, the free `setWindowActivation(root, value)`, the resolved `root.windowActivation` getter and the `focus`/`blur` observer consuming `document.hasFocus()` through the batched read (`packages/platform-web/src/window-activation.ts`, `root.ts`, `measure.ts`); `<GlassRoot windowActivation>` and `useGlassWindowActivation()` (`packages/react/src/root.tsx`, `store.ts`); the pose applied through `applyMaterialProfile` as two frozen endpoints, tested on three engines, documented in both package READMEs, and operable in the playground's pin with its resolved readout (§5.147). **Published:** 470 inactive rows in the canonical matrix as the scene's declared `state`, on both tiers across all six profiles, captured through the runtime's own `"inactive"` pose and proved byte-identical to G2's frozen captures before a row was written — 354 / 354 inactive and 60 / 60 active (§5.148). **And a first:** a real window-manager focus change, read without a driver, moves the pose — `hasFocus` false, root `inactive`, `visibilityState` still `"visible"` (§5.148 §4). **What the score does not claim.** No inactive floor is adopted and none may be while seven runs is the probe bar (W27 Decision Log 13), so this row is fidelity rather than a gate. The abscissa's kind and scale remain unidentified — the silhouette mean is the candidate that passed, not Apple's law — and the identifying sitting is priced and deferred. The transit's 240 ms / 120 ms are inherited and unmeasured against any native sequence. §5.146's eye residuals stand: the light text square is still visibly too bright, structured transfer and rim/lens bands differ on the large panes, the low-contrast checker's amplitude differs in dark, the one-pixel contour under Increase Contrast and Reduce Transparency's backdrop-dependent slope are unclosed. Dark accessibility, 2x accessibility, the `clear` variant and the stack regime are still not inactive evidence classes. And the row quotes Apple naming **two** system-managed adaptation inputs — "element overlap and focus state" — of which only focus state ships |

| layer | rows | `replicated+measured` | `replicated, unmeasured` | `partial` | `excluded by decision` | `absent, undecided` | n/a |
| --- | --- | --- | --- | --- | --- | --- | --- |
| §1 Material API surface | 52 | 14 → 14 | 7 → 7 | 7 → 7 | 4 → 4 | 10 → 10 | 10 → 10 |
| §2 Component families | 26 | 1 → 1 | 3 → 3 | 3 → 3 | 7 → 7 | 10 → 10 | 2 → 2 |
| §3 Behavioral system | 97 | 29 → **30** | 19 → 19 | 15 → **14** | 11 → 11 | 16 → 16 | 7 → 7 |
| **total** | **175** | **44 → 45** | **29 → 29** | **25 → 24** | **22 → 22** | **36 → 36** | **19 → 19** |

As proportions of the same **156** scoreable rows: replicated and measured 28% → **29%**;
replicated, unmeasured 19% → 19%; partial 16% → **15%**; excluded by decision 14% → 14%; absent and
never ruled on 23% → 23%. §1 and §2 are untouched — W28 built no API surface and no component —
and the scoreable denominator does not move, so every proportion above is a row moving rather than
a denominator changing.

**Why only one row, when the wave was four gates long.** W28 is the narrowest wave the project has
run: one state axis, end to end. Its other products are evidence rather than coverage. The
footprint abscissa is a mechanism inside the response, not a native behaviour the matrix
enumerates, and it is gated to the receded documents — the active material is byte-identical by
contract (X11), so no row that scores the active response moves. G0's reading is a finding *about*
the reference (it takes the response's input under the surface, not over the source) that the
matrix has gestured at since 2026-09-10 — "a thin dark appearance selected by scene content beyond
the surface's footprint" — and it stays a gesture here rather than becoming a row, because the
reading's own verdict was **not identifiable**: a row scored on a candidate the bed could not
select would be crediting a law nobody has read. When the identifying sitting is taken, that row is
the one to add.

**Three rows this re-score checked and did not move**, each for a reason worth naming rather than
leaving to silence. §3.6's *sheet drag makes the material recede, opacify and grow* keeps
`excluded by decision`: it is the same recede mechanism, but the row is scored on a gesture-driven
component that §Out of scope excludes, and W28 built no gesture-driven pose. §3.3's *small elements
flip light/dark to the underlying content* keeps `partial`: G0 added real native evidence about
where the reference takes that decision's input, and X11 held the active material still, so the
evidence under the row is stronger and the verdict is unchanged. §2's *Windows / window chrome*
keeps `absent, undecided`: a window **activation pose** is not window chrome, and vitrea still
renders no title bar and no window corner.

**One §6 entry is now half-stale**, recorded here rather than rewritten there. §6 lists *"Window /
scene focus state as a material state axis — glass receding when a window loses focus, and 'element
overlap and focus state' being named by Apple as system-managed adaptation inputs"* under a section
whose criterion is zero occurrences in the composite spec and the claims ledger. The first half is
now measured, fitted, bounded and shipped across §§5.128–5.148; the second half — element overlap —
remains genuinely unmentioned and unbuilt, which is the half that keeps the entry alive.

### Re-scored 2026-09-20 after W29, beside the 2026-09-15 reading

W29 (`2026-09-16-w29-os27-recapture.md`) moved the reference itself: Apple's material was captured
again on macOS 27.0 build 26A428 under new keys, measured native-against-native cell by cell before
any vitrea constant moved, refit on both tiers, and selected as what a page draws by default.
**Two rows move, both in §1.7, both upward; none is added and none moves downward.** The three
tables above are left as written and no row's earlier record is rewritten.

| row | matrix | 2026-09-15 | 2026-09-20 | evidence |
| --- | --- | --- | --- | --- |
| The material itself moved with no API change — "we tuned Liquid Glass so it more effectively diffuses complex content behind it … a darkened edge along with brighter specular highlights", and apps get it without recompiling | §1.7 | `absent, undecided` — "vitrea calibrates against macOS 26.5 captures … the reference material has already moved, and vitrea's fidelity claim is against a superseded version" | **`replicated+measured`** | **Measured, and measured first.** The 2026-09-15 cell named the shelf-life fact; this wave priced it and paid it. A macOS 27 bed of **624 cells over six profile keys** was captured at seven runs per cell with every pixel-moving axis attested per run, no shortfall and no refusal (§5.150); **619 pairs were then read native-against-native against a noise bar defined per metric from the macOS 27 bed's own run-to-run behaviour and committed before the first macOS 26.5 pair was opened** — Apple's material moved on **every one of them** and Apple's geometry did not (§5.151). The State of the Union's three claims are all in that reading and all quantified: the diffusion moved (scatter, 589 of 589, and conditioned on the backdrop's spatial scale rather than uniformly), the edge moved (the rim band on all 330 active cells, in amplitude and in width), the speculars moved (the angular ratio on 132 of 132). Two the announcement did not name moved further: the interior level, which stopped vanishing into a dark backdrop, and the **outer shadow**, which is dimmer, tighter, shorter and less displaced on every measurable cell of every profile (§5.154). **Fitted:** two macOS 27 patch documents plus two receded endpoints, bounds declared at the macOS 26.5 tables' values *before* the read (X5) and no floor adopted, holdout read once; the whole-cell ΔE mean roughly halves on every standard profile on both tiers and the p95 tail falls 0.46 → 0.14 light (§5.153, §5.154). **Replicated:** `createGlassRoot({ materialProfileDocument })` selects a whole measured material — active and receded patches per scheme plus the CSS crossing — `macos27MaterialProfileDocument` is the default from 0.19.0, `<GlassRoot materialProfileDocument>` surfaces it in React, and `root.material` reports which endpoint drew with its digest (§5.155). **What the score does not claim.** Seven declared rows are recorded as missed rather than met; the shadow's blur is span-invariant in vitrea and is not on macOS 27, where one constant cannot hold 1.8 and 17.4 CSS px; the highlight's *directionality* is measured and unfitted for want of a web-side angular reader; and the by-eye residuals of §5.153, §5.154 and §5.155 stand. The row scores the material having been re-measured and refit, not the gap having closed |
| A user-facing slider adjusting Liquid Glass "anywhere from ultra clear to fully tinted" | §1.7 | `absent, undecided` | **`partial`** | The axis is identified, attested and fitted at one point on it; nothing about it is exposed. **Identified:** Apple documents no API and no defaults key, and G0 found the backing store by diffing every preference domain across the update — `NSGlassTintAmount`, a float in `NSGlobalDomain` that did not exist on macOS 26.5 — then measured that it **drives rendering with no GUI**, moving 10 of 10 probe cells beyond their own three-run spread at both ends and at the machine's as-found position, in both poses, at both scales, in both schemes (§5.149 §4). **Attested:** with the key deleted the material renders at exactly the 0.5 arm, so the system's own default is 0.5; Decision Log 3 (a) ruled the bed captured there, the position is read from the machine per run by something that can refuse, and it is the trailing `-glass0.5` token of every macOS 27 profile key (X6). **Not replicated:** vitrea has no slider, no media query reports one, and the material is fitted at 0.5 alone. The two ends stay evidence classes this wave declined to capture (§Deferred), which is what holds the row at `partial` rather than higher |

| layer | rows | `replicated+measured` | `replicated, unmeasured` | `partial` | `excluded by decision` | `absent, undecided` | n/a |
| --- | --- | --- | --- | --- | --- | --- | --- |
| §1 Material API surface | 52 | 14 → **15** | 7 → 7 | 7 → **8** | 4 → 4 | 10 → **8** | 10 → 10 |
| §2 Component families | 26 | 1 → 1 | 3 → 3 | 3 → 3 | 7 → 7 | 10 → 10 | 2 → 2 |
| §3 Behavioral system | 97 | 30 → 30 | 19 → 19 | 14 → 14 | 11 → 11 | 16 → 16 | 7 → 7 |
| **total** | **175** | **45 → 46** | **29 → 29** | **24 → 25** | **22 → 22** | **36 → 34** | **19 → 19** |

As proportions of the same **156** scoreable rows: replicated and measured 28.8% → **29.5%**;
replicated, unmeasured 18.6% → 18.6%; partial 15.4% → **16.0%**; excluded by decision 14.1% →
14.1%; absent and never ruled on 23.1% → **21.8%**. §2 and §3 are untouched and the scoreable
denominator does not move, so every proportion above is a row moving rather than a denominator
changing.

**Why §3 does not move, when the wave refit most of §3's material.** The behavioural rows are
scored on whether vitrea replicates a native behaviour and whether that claim is measured, not on
which release it was measured against. Every row W29 touched — the size law, the tone response,
scatter, the rim, tinting, the recede — was already `replicated+measured` on the macOS 26.5 bed,
and re-measuring them on a newer bed makes each claim younger rather than broader. Scoring them
again would be counting one replication twice; the fact that actually changed belongs to the two
§1.7 rows above, which is where it is recorded.

**Four rows this re-score checked and did not move**, each for a reason worth naming.

- §3.3's *small elements flip light/dark to the underlying content* keeps `partial`, and the reason
  is a **finding rather than an absence of work**: on macOS 27 the adaptation band that stood the
  level law down over dark backdrops measures **inert** — Apple's material does not disappear
  anywhere on this bed, reading 0.2899 over `dark-solid` where vitrea's macOS 26.5 capsule rendered
  0.0126 — so the refit moved the band to the bottom of its range (§5.153 §2 item 1). The row's
  native behaviour is weaker on the new reference than on the old one, which is not the same thing
  as vitrea replicating more of it.
- §3.6's *window / scene focus state changes the material* keeps `replicated+measured`. W29 G3b
  refit the pose on the new bed and found the largest single difference from macOS 26.5 — a receded
  surface now **keeps** its outer shadow, where the macOS 26.5 endpoint removes it entirely — and
  W29 G4 made the fitted macOS 27 endpoints what the runtime applies by default. It is the same
  claim on a newer bed, with the declared recede bound **missed on eleven of twelve profile-tiers**
  and recorded rather than re-pinned (Decision Log 7 (b)): a fidelity fact under an unchanged score.
- §1.7's *concentricity moved outward* and *toolbar-minimization machinery* keep `absent,
  undecided`. This wave measured the material and not the API surface, and Apple's window corner
  never enters the harness's capture region at all — the region is the window's own rectangle,
  which G0 measured and §5.149 §5 records — so the wave has nothing to say about either row in any
  direction.

**One §6 entry is now stale in its first half, and is recorded here rather than rewritten there.**
§6's closing item is Apple's disclaimer that these effects "can appear differently between system
versions", with the observation that "no vitrea document states that the reference is a moving
target or prices the cost of tracking it". Seven claims sections now do both: §§5.149–5.155 are the
price, paid, with the hours and the machine-unavailability recorded in the wave's Grounding
Baseline and its `sitting.md`. The half that stays alive is the disclaimer itself — nothing in the
project yet says what happens at macOS 28.

### Re-scored 2026-09-20 after W30, beside the same day's W29 reading

W30 (`2026-09-20-w30-operator-wave.md`) replaced two constants of the material with operators: the
outer shadow's blur became a line in the CASTING SPAN, and the diffusion gained a term keyed on the
backdrop's measured spatial scale. **No row moves, and that is the finding rather than an omission.**
The four tables above are left as written and no row's earlier record is rewritten.

**Why nothing moves.** Both operators land inside behaviours the matrix already scores
`replicated+measured`. §3.2's *larger surfaces refract, shadow, and scatter more* was moved there on
2026-09-10 (`2026-09-10-coverage-rescore.md`) on the argument that all three mechanisms draw and the
outer shadow is fitted; W30 makes the shadow's half of that claim a function of size where it had
been a size-gated amplitude over one width, and makes the scatter's half a function of what is
behind the surface. That is the same claim measured better, which is W29's own reason for §3 not
moving, applied to a wave that refit rather than recaptured. A matrix that moved a row for a better
fit of a replicated behaviour would be scoring accuracy where it scores coverage.

**What does change is a limit recorded inside a row**, and it is recorded here rather than rewritten
there.

| row | matrix | the limit as recorded 2026-09-20 (W29) | 2026-09-20 (W30) |
| --- | --- | --- | --- |
| The material itself moved with no API change | §1.7 | "the shadow's blur is span-invariant in vitrea and is not on macOS 27, where one constant cannot hold 1.8 and 17.4 CSS px" | **Closed.** σ is `sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan · (span − sigmaSpanRefPx))` in both tiers' material, fitted jointly across every bed each document serves and adopted as a bound — within ±5 % of the native median at spans 96, 128 and 160 on all six profiles, and within a factor 1.5 of the native thin-span statistic at span 44 against 0.19.0's 5.97–7.34× (claims §5.159 §1, §5.160). The row's other three named limits stand: seven declared rows are still recorded as missed, the highlight's directionality is still unfitted, and the by-eye residuals of §5.153–§5.155 are unchanged |

> **Split beside, 2026-09-20 (W30 G4 review closure; claims §5.160 §9, finding 12).** The closure
> sentence in that row runs the two tolerances together and so reads B2 as adopted, which it is not.
> Separated: **B1 is the adopted bound** — the σ law within ±5 % of the native statistic at spans 96,
> 128 and 160 on every bed each document serves, four cases in `adopted-thresholds.test.ts`, and
> jointly tighter than ±5 % because the admissible σ is the intersection of the served beds' windows.
> **B2 — the factor 1.5 at span 44, read at 1.155–1.419 against 0.19.0's 5.97–7.34 — is a one-wave
> reading and is not adopted**, as §5.156 §5 (b) declared before either operator existed: the
> thin-span (amplitude, σ) pair is not identified, trading at constant product at that span, and the
> thin σ bifurcates on the author's tint. What would make it adoptable is a thin-span cell whose
> amplitude lets the pair separate, which is item 4 of the wave's Deferred at close. The row's
> recorded limit is closed by B1 alone; nothing about that closure depends on B2.

**Three rows this re-score checked and did not move**, each for a reason worth naming.

- §3.2's *larger surfaces refract, shadow, and scatter more* keeps `replicated+measured`, as above.
  Worth stating beside it: the wave measured that Apple's own blur is span-invariant on macOS 26.5
  — σ within 15.4–15.9 CSS px from a 32 px control to a 160 px panel — so the size term this row is
  about did not exist in the reference until macOS 27. vitrea's matching it on the older bed was
  correct, and matching it on the newer one required a shape the row's mechanism did not have.
- §1.6's *toolbar-group glass management* keeps `replicated, unmeasured`. W30 G4 closed the seam
  that had `GlassToolbar` deriving its gap from the package's default material rather than from the
  document its own root selected, and the gap now follows the resolved colour scheme as well. The
  row's recorded reason for `unmeasured` is unchanged and is about the bed: `scenes.json` carries
  `toolbar-group__rest` and `toolbar-group__inactive` and no split scene, so the comparison is still
  vitrea against vitrea.
- §3.2's *large surfaces pick up ambient colour spill* keeps `absent, undecided`. The scatter's new
  term reads the backdrop's spatial SCALE — how coarse the structure behind the surface is — and not
  its colour, so it is not a step toward this row in any direction, and the wave's own charter
  refuses the chromatic axis by name (W29 Decision Log 6 (c)).

The tallies are therefore unchanged from the W29 reading above: **45 → 46 → 46** replicated and
measured of 156 scoreable rows, 29.5 %.
