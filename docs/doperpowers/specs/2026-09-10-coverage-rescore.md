# Coverage matrix re-score (2026-09-10)

> Companion to [`2026-08-25-coverage-matrix.md`](./2026-08-25-coverage-matrix.md), whose §7
> carries the summary. This file is the per-row evidence: every one of the matrix's 174 rows
> scored again against `main` at `c5b3320` (W26 recomposed), sixteen days and twenty-six waves
> after the matrix was compiled. The 2026-08-25 column is the matrix's own recorded reading,
> reconstructed from git (`322dc28`) so that later in-place annotations do not contaminate it;
> both halves reproduce §4's recorded counts exactly. Nothing in the matrix is rewritten.
>
> Produced by two read-only agents (§1–§2 and §3), each citing a file and line, a scene id, a
> changelog version or a claims section for every move; a row with nothing citable keeps its
> August status. Neither ran a suite or a capture.

## Combined headline — 174 rows

| status | 2026-08-25 | 2026-09-10 | delta |
| --- | --- | --- | --- |
| `replicated+measured` | 25 | **41** | +16 |
| `replicated, unmeasured` | 23 | **25** | +2 |
| `partial` | 30 | **26** | −4 |
| `excluded by decision` | 18 | **23** | +5 |
| `absent, undecided` | 58 | **40** | −18 |
| `n/a` | 20 | **19** | −1 |
| **total** | **174** | **174** | — |
| scoreable (total − `n/a`) | 154 | **155** | +1 |

---

# Coverage matrix §1–§2, re-scored 2026-09-10

A re-score **beside** `docs/doperpowers/specs/2026-08-25-coverage-matrix.md`,
not a rewrite of it. The 2026-08-25 column is the matrix's own recorded reading, reconstructed
row by row and cross-checked against §4's counts (it reproduces them exactly: §1 = 10 / 5 / 10 / 4 / 13 / 10,
§2 = 1 / 2 / 3 / 7 / 10 / 3). Nothing in the matrix is edited.

**Scope.** §1 (52 rows) and §2 (26 rows). Repository at `main`, `c5b3320` / `cc89dd2`, 2026-09-10.

**Vocabulary.** The matrix's §0 table names five values; §4's table adds `n/a` as the sixth
column, for a native item with no vitrea analogue by nature rather than by omission. One value
per row, no hedging.

**Rule applied.** A row moves only against a citation — a source file and line, an export, a
scene id, a changelog version, or a claims-doc section. Where nothing citable changed, the row
keeps its 2026-08-25 status and the last column says `unchanged`.

---

## 1. Per-subsection tables

### §1.1 The glass modifier and the `Glass` value

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| `glassEffect(_:in:)` | `replicated+measured` | `replicated+measured` | `packages/react/src/surface.tsx:65-120`; `packages/calibration/results/matrix.json` 637 cells over 88 scene ids and six profile keys | Bed widened from 30 texture cells / 2 profiles to 318 texture + 319 dom cells / 6 profiles (229 gated); status holds |
| `DefaultGlassEffectShape` (capsule default) | `partial` | `partial` | `DEFAULT_RADIUS = 12` at `packages/react/src/surface.tsx:123`; family chosen at `:200`; `capsule` default `false` at `:136` | Capsule family now draws a true stadium on the GPU tier (CHANGELOG 0.9.0 `bc7706e`; claims §5.83–§5.86); vitrea's 12px default is unchanged and still unruled |
| `Glass.regular` | `replicated+measured` | `replicated+measured` | `MATERIAL_VARIANTS` `packages/core/src/material.ts:22`; `packages/calibration/profiles/apple-macos-26.5-1x-{light,dark}-standard.json` | Dark profile added and shipped as `darkMaterialProfile` (CHANGELOG 0.10.0 `c017625`; claims §5.90–§5.92) |
| `Glass.clear` | `replicated, unmeasured` | `replicated, unmeasured` | No `clear` scene: `apps/reference-apple/scenes.json` has backgrounds / components / **tints** only; `packages/renderer-webgpu/src/material.ts:1854,2030` records the constants as unfitted for want of rows | unchanged (W24 retired the variant's unfitted one-sided specular, claims §5.109 — no rows either way) |
| `Glass.identity` | `absent, undecided` | `absent, undecided` | `grep -rniE "\bidentity\b" packages/{react,core,platform-web}/src` returns only React-identity and identity-transform prose | unchanged |
| `Glass.tint(_ color:)` | `absent, undecided` | **`replicated+measured`** | `tint?: string \| null` at `packages/react/src/surface.tsx:92`; `GlassTint` `packages/core/src/material.ts:67-71`; parser `packages/platform-web/src/tint.ts:82,135`; CHANGELOG 0.2.0 `0ffd246`; `scenes.json:291-305` tints registry, 16 tinted scenes incl. holdout `photo__rrect-lg__rest-tint-orange`; 98 tinted cells in `results/matrix.json`; claims §5.36–§5.37, §5.80–§5.82 | W3/W10/W19 landed the author tint on both tiers and measured it against tinted native captures |
| `Glass.interactive(_:)` | `replicated, unmeasured` | **`partial`** | `pressCompression` and `glow` drivers at `packages/motion/src/channels.ts:14,16`, written at `packages/react/src/interaction.ts:191-222`; `shimmer` is 0 on an undriven surface and has no driver (`packages/platform-web/src/channels.ts:63-91`); CHANGELOG 0.11.0 `6a0b8f1`; `optics.ts:250` `specularGain: 0`; claims §5.94, §5.96 | W22 found the only resting band was the sweep's parked idle phase and gated it to zero; scaling and press glow present, shimmering has a channel and no driver |
| Chaining `.regular.tint(.orange).interactive()` | `partial` | **`replicated+measured`** | `variant`, `tint`, `interactive` all compose on one surface (`surface.tsx:132,133,141`); the chain is a measured cell — `photo__capsule-button__rest-tint-orange`, `checkerboard__capsule-button__rest-tint-blue` (validation) | The row's named gap ("tint does not exist to chain") is closed |
| `glassEffect(_:in:isEnabled:)` | `n/a` | `n/a` | — | unchanged |

### §1.2 `GlassEffectContainer`

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| `GlassEffectContainer<Content>` | `replicated+measured` | `replicated+measured` | `GlassGroup` `packages/react/src/group.tsx:128-161`; `checkerboard__toolbar-group__rest`, `photo__toolbar-group__rest` (the latter now validation) | Same two scenes, now measured at both scales and both schemes |
| `init(spacing:)` | `replicated+measured` | `replicated+measured` | `mergeDistance` `packages/core/src/scene.ts:186-190`; claims §5.77 — Apple's layer tree read directly (`CASDFLayer.smoothness` 12 at spacing 12, 40 at spacing 40, `mergeElements` 0, no separation threshold) against `DEFAULT_GROUP_UNION`'s 16 | The 2026-08-25 note ("unmeasurable by this scene set") no longer holds; the union law is measured and vitrea diverges in kind above 16 — recorded as the renderer's charter item |
| The sampling-region rationale (one proxy per group) | `replicated+measured` | `replicated+measured` | `DEFAULT_GROUP_SAMPLING` `packages/core/src/scene.ts:146-149`; 3σ floor `packages/platform-web/src/proxy-geometry.ts:16` | W6(d) rederived the default padding from the resolved post-policy blur; W22 G3 gave a group stacked on glass that glass's tone (claims §5.95) |
| Rest-state blending rule | `replicated, unmeasured` | **`replicated+measured`** | `packages/geometry/test/union.test.ts`; claims §5.77 — native probe bed at spacings 12 and 40, seven attested runs, `toolbar-group` / `toolbar-group-wide` native interior 0.6210 / 0.6212; vitrea's union flat ±0.0002 over gaps 12–56 | W18 G0 captured the probe bed the 2026-08-25 row said could not exist |
| Modifier ordering | `n/a` | `n/a` | — | unchanged |
| Performance ceiling | `replicated+measured` | `replicated+measured` | `packages/renderer-webgpu/src/governor.ts`; `e2e/bench/budget.spec.ts` | Cost moved, not status: W8's shadow 3.35× → 2.79× frame time on the mobile bench; W26's heavy tap +0.18 ms (claims §5.120) |
| Container **nesting** rules | `absent, undecided` | `absent, undecided` | `packages/platform-web/src/layer-model.ts:164-169` checks host-inside-host, not container-inside-container | W4 added a structural glass-nesting rule; it is not a *container* nesting rule, and Apple still documents none |

### §1.3 Morphing: IDs, transitions, unions

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| `glassEffectID(_:in:)` + `@Namespace` | `replicated, unmeasured` | `replicated, unmeasured` | `GlassMorph` `packages/react/src/morph.tsx:75-97,170-181`; `packages/react/e2e/morph.spec.ts` | unchanged (last substantive touch is W5's pre-pin polish, `2677b86`). See §3 — the cited `morphNamespace` mechanism is inert |
| `glassEffectUnion(id:namespace:)` | `absent, undecided` | `absent, undecided` | `grep -rniE "glassEffectUnion\|unionId" packages/*/src` returns nothing | unchanged |
| `GlassEffectTransition` kinds | `partial` | `partial` | No `kind`/`transition` prop on `GlassMorphProps` (`morph.tsx:75-97`); `grep -rniE "matchedGeometry\|materialize\|transitionKind" packages/*/src` returns only prose | unchanged |
| `glassEffectTransition(_:isEnabled:)` | `n/a` | `n/a` | — | unchanged |
| Scope limit (morph is a transition, not a property) | `replicated, unmeasured` | `replicated, unmeasured` | `packages/motion/src` | unchanged |
| UIKit has no ID-based morph API | `n/a` | `n/a` | — | unchanged |

### §1.4 Scroll edge effects and background extension

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| `ScrollEdgeEffectStyle` | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| `scrollEdgeEffectStyle(_:for:)` / `scrollEdgeEffectHidden(_:for:)` | `excluded by decision` | `excluded by decision` | same line | unchanged |
| UIKit `UIScrollEdgeEffect` | `excluded by decision` | `excluded by decision` | same line | unchanged |
| `safeAreaBar(...)` | `absent, undecided` | `absent, undecided` | `grep -rniE "safeAreaBar\|safe-area-bar" packages/*/src` returns nothing | unchanged |
| `backgroundExtensionEffect()` | `absent, undecided` | `absent, undecided` | `grep -rniE "backgroundExtension\|background-extension" packages/*/src` returns nothing | unchanged |
| `UIBackgroundExtensionView` / `NSBackgroundExtensionView` | `absent, undecided` | `absent, undecided` | same grep | unchanged |

### §1.5 Concentricity

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| `ConcentricRectangle` (level-set offset) | `replicated+measured` | `replicated+measured` | `packages/geometry/test/concentric.test.ts`; `resolveConcentric` `packages/geometry/src/concentric.ts` | unchanged |
| The definition (shared centre) | `replicated+measured` | `replicated+measured` | same | unchanged |
| `Shape.rect(corners:isUniform:)` | `partial` | `partial` | `packages/platform-web/test/non-uniform-radii.test.ts:1-16`; W5 re-deferral commit `5ac6cc3` (wave Tracking Map, W5 row) | Per-corner radii re-deferred with its reason at W5's cut; the v1 dev-mode error became a warning raised at the public boundary — the limit is unchanged |
| `Edge.Corner.Style` | `partial` | `partial` | `DEFAULT_CONCENTRIC_MIN_RADIUS = 2` `packages/geometry/src/concentric.ts:59` | unchanged |
| `containerShape(_:)` + `RoundedRectangularShape` | `partial` | **`replicated, unmeasured`** | `ConcentricParent` `packages/core/src/scene.ts:228-233`; `GlassNodeDescriptor.concentricOf` `:260` with registration-time validation `:582-620,769,778,786-792`; `GlassHostOptions.concentricOf` `packages/platform-web/src/host.ts:91`; tests `packages/core/test/scene-shape-fields.test.ts`, `packages/platform-web/test/shape-fields.test.ts`; CHANGELOG 0.2.0 `aca1d25` | W5 landed Decision Log #23(c): the parent link is a scene-model field, not a render input. Caveat: reachable from the host API only — React exposes no `concentricOf` (`surface.tsx:65-117`) |
| `GeometryProxy.concentricCornerRadii` | `absent, undecided` | `absent, undecided` | `resolveConcentric` is not exported from `packages/react/src/index.ts:80-88` | unchanged. See §3 |
| UIKit `UICornerConfiguration` | `partial` | `partial` | no `capsule(maximumRadius:)` analogue | unchanged |
| Apple's own corner curve (`.continuous` is not G1) | `replicated+measured` | `replicated+measured` | claims §5.84 (Apple measured on a ten-rung radius ladder over two backgrounds above the saturation ratio), §5.86 (ΔE better on 61 of 65 corner cells) | The 2026-08-25 note said the corner question was undecidable by the fixtures; W20 made it decidable above r/min 0.327 and found vitrea's clamp wrong there |

### §1.6 Button styles, and the UIKit / AppKit surfaces

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| `GlassButtonStyle` / `GlassProminentButtonStyle` | `partial` | `partial` | `packages/react/src/controls/button.tsx:36-43`; `grep -rniE "prominent" packages/ apps/` returns zero hits repo-wide | unchanged. `tint` is now the emphasis mechanism but is **not** in `GlassButtonProps`' `Pick` list (`button.tsx:38-41`) |
| `UIGlassEffect` (`style`, `tintColor`, `isInteractive`) | `partial` | **`replicated+measured`** | style: `MATERIAL_VARIANTS` `core/src/material.ts:22`; tintColor: `surface.tsx:92` + 98 tinted cells; isInteractive: `surface.tsx:105` | The row's named gap ("`tintColor` does not exist in vitrea") is closed; all three members now map across. `isInteractive`'s shimmer third is carried by §1.1's row |
| `UIGlassContainerEffect.spacing` | `replicated+measured` | `replicated+measured` | same as §1.2 | unchanged |
| `UIButton.Configuration.glass()` / `.prominentGlass()` / … | `partial` | `partial` | `variant` reachable via `GlassButtonProps` `button.tsx:40`; no prominent form | unchanged |
| AppKit `NSGlassEffectView` | `n/a` | `n/a` | — | unchanged |
| Toolbar-group glass management (`ToolbarSpacer`, `sharedBackgroundVisibility`) | `absent, undecided` | `absent, undecided` | `grep -rniE "toolbarspacer\|sharedBackground" packages/*/src` returns nothing; `GlassToolbarProps` `packages/react/src/controls/toolbar.tsx:72-84` | unchanged. See §3 |
| `glassBackgroundEffect(displayMode:)` (visionOS) | `n/a` | `n/a` | — | unchanged |
| Platform coverage as a fact about the API | `n/a` | `n/a` | — | unchanged |

### §1.7 What WWDC26 / OS 27 changed in this layer

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| `NSGlassEffectView.effectIsInteractive` | `n/a` | `n/a` | — | unchanged |
| The material moved with no API change (OS 27) | `absent, undecided` | `absent, undecided` | every profile key in `results/matrix.json` is `apple-macos-26.5-*`; `packages/calibration/profiles/` holds only 26.5 documents | unchanged — the reference is still macOS 26.5 after 26 waves |
| User-facing "ultra clear to fully tinted" slider | `absent, undecided` | `absent, undecided` | the tint's strength is the colour's own alpha, author-set (`surface.tsx:84`); no user/system preference feeds it | unchanged. A continuous author strength axis now exists; a *user* axis does not |
| Concentricity moved outward (read-back accessors) | `absent, undecided` | `absent, undecided` | see §1.5 | unchanged |
| Toolbar-minimization machinery | `absent, undecided` | `absent, undecided` | `grep -rn "minimiz" packages/*/src/*.ts` returns nothing | unchanged |
| `UIScrollEdgeEffect.Style.automatic` changed meaning | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| The old-design opt-out is being removed | `n/a` | `n/a` | — | unchanged |
| The `toolbarMinimizeBehavior` naming trap | `n/a` | `n/a` | — | unchanged |

### §2 Component families that adopt glass natively

| row | 2026-08-25 | 2026-09-10 | evidence | what changed |
| --- | --- | --- | --- | --- |
| Buttons | `replicated+measured` | `replicated+measured` | `capsule-button` is 28 of 92 scenes (`scenes.json`), across six profile keys; CHANGELOG 0.9.0 `bc7706e` | Cell count grew and the capsule draws a true stadium; prominent style and extra-large control size still absent (`grep -rniE "controlSize" packages/*/src` returns nothing) |
| Toolbars / toolbar items | `partial` | `partial` | `toolbar.tsx:72-84`; the container is deliberately not a glass surface (`toolbar.tsx:15-19`) | unchanged. `concentricOf` now exists in the scene model, but the bar itself is not a registered surface, so bar-concentric radii for contained controls stay unexpressible |
| Tab bars | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| Navigation bars / split views | `absent, undecided` | `absent, undecided` | — | unchanged |
| Sidebars and inspectors | `absent, undecided` | `absent, undecided` | — | unchanged |
| Segmented controls / pickers | `replicated, unmeasured` | `replicated, unmeasured` | `packages/react/src/controls/segmented-control.tsx`; `grep -ic segmented apps/reference-apple/scenes.json` → 0 | unchanged — still no canonical scene |
| Sliders | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| Toggles / switches | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| Steppers | `absent, undecided` | `absent, undecided` | — | unchanged |
| Menus and context menus | `replicated, unmeasured` | `replicated, unmeasured` | `grep -ic menu scenes.json` → 0; the `glass-over-glass` cells are still a stack | unchanged. W22 G3 fixed the stack's overlay tone (claims §5.95, CHANGELOG 0.11.0) — a better-measured stack, still not a menu |
| Popovers | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| Sheets | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| Action sheets | `absent, undecided` | `absent, undecided` | — | unchanged |
| Alerts | `absent, undecided` | `absent, undecided` | — | unchanged |
| Search fields | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| Text fields | `absent, undecided` | `absent, undecided` | `grep -ic textfield scenes.json` → 0 | unchanged |
| Scroll edge effect (cross-cutting) | `excluded by decision` | `excluded by decision` | §Out of scope | unchanged |
| Corner concentricity (cross-cutting) | `partial` | `partial` | see §1.5 | One sub-row moved (`containerShape`); the family stays partial — React can still not request a concentric shape (`surface.tsx:200`) |
| Windows / window chrome | `absent, undecided` | `absent, undecided` | — | unchanged |
| Widgets | `absent, undecided` | `absent, undecided` | — | unchanged |
| App icons | `absent, undecided` | `absent, undecided` | — | unchanged |
| Custom views | `partial` | `partial` | `surface.tsx:65-117` | The row's "minus tint" clause is closed; identity, union-by-id and named transitions remain |
| Keyboard accessory views | `absent, undecided` | `absent, undecided` | — | unchanged |
| tvOS controls | `n/a` | `n/a` | — | unchanged |
| watchOS | `n/a` | `n/a` | — | unchanged |
| Lists, tables, forms (the prohibition) | `n/a` | **`replicated, unmeasured`** | `glass-in-content-layer` warning keyed on list/table roles, `packages/platform-web/src/layer-model.ts:85-127,172-180`; `glass-inside-glass` error `:164-169`; code registered `packages/platform-web/src/diagnostics.ts:76-79`; tests `packages/platform-web/test/layer-model.test.ts`, `packages/react/e2e/layer-model.spec.ts`; W4, commit `da0e532` | W4 turned the prohibition from prose into a checkable contract. The matrix's §4 counted this row as unscoreable; it is scoreable now, so §2's scoreable rows go 23 → 24 |

---

## 2. Headline tables

### §1 Material API surface — 52 rows

| status | 2026-08-25 (matrix §4) | 2026-09-10 |
| --- | --- | --- |
| `replicated+measured` | 10 | **14** |
| `replicated, unmeasured` | 5 | 4 |
| `partial` | 10 | 8 |
| `excluded by decision` | 4 | 4 |
| `absent, undecided` | 13 | **12** |
| `n/a` | 10 | 10 |
| **total** | **52** | **52** |

### §2 Component families — 26 rows

| status | 2026-08-25 (matrix §4) | 2026-09-10 |
| --- | --- | --- |
| `replicated+measured` | 1 | 1 |
| `replicated, unmeasured` | 2 | **3** |
| `partial` | 3 | 3 |
| `excluded by decision` | 7 | 7 |
| `absent, undecided` | 10 | 10 |
| `n/a` | 3 | **2** |
| **total** | **26** | **26** |

### §1 + §2 combined — 78 rows

| status | 2026-08-25 | 2026-09-10 | delta |
| --- | --- | --- | --- |
| `replicated+measured` | 11 | **15** | +4 |
| `replicated, unmeasured` | 7 | 7 | 0 |
| `partial` | 13 | **11** | −2 |
| `excluded by decision` | 11 | 11 | 0 |
| `absent, undecided` | 23 | **22** | −1 |
| `n/a` | 13 | **12** | −1 |
| **total** | **78** | **78** | — |
| scoreable (total − `n/a`) | 65 | **66** | +1 |

Seven rows moved. Six of them trace to two children — W3/W10/W19's author tint (three rows) and
W5's deferred API batch (one row) — plus W18's native probe bed (one row), W4's content-layer
contract (one row) and W22's shimmer gate (one row, the only move in the losing direction).

---

## 3. Rows I believe were scored wrong at the time (not merely stale)

Each of these was decidable from the code as it stood on 2026-08-25; none turns on a later change.

1. **§1.3 `glassEffectID(_:in:)` + `@Namespace` — scored `replicated, unmeasured`; arguably `partial`.**
   The row cites `morphNamespace on GlassGroup` as the mechanism. `morphNamespace` is declared
   (`packages/core/src/scene.ts:181`), forwarded by the binding (`packages/react/src/group.tsx:143,264,302`)
   and asserted as a descriptor field by one test (`packages/react/test/lifecycle.test.tsx:174-179`)
   — and read by nothing else in the repository. vitrea's morph is driven entirely by `GlassMorph`'s
   two geometry endpoints (`morph.tsx:170-181`); there is no identity association at all. The
   *behaviour* is replicated; the *mechanism the row names* has never been wired.

2. **§1.1 `Glass.interactive(_:)` — scored `replicated, unmeasured`; was already `partial`.**
   Apple's three verbs are scaling, bouncing and shimmering. The shimmer channel's own doc comment
   ("what a shimmer driver will output **when one exists**", `packages/platform-web/src/channels.ts:63-73`)
   predates the matrix, and the only thing that looked like a shimmer — the specular band — was
   later measured as the sweep's parked idle phase, present on every resting surface since the pass
   landed (claims §5.94). The row is moved above on W22's evidence, but the 2026-08-25 reading was
   generous on the day it was written.

3. **§1.5 `GeometryProxy.concentricCornerRadii` — scored `absent, undecided`; arguably `partial`.**
   The same table's `containerShape(_:)` row records that C8's segmented-control indicator "derives
   its radius via `resolveConcentric`" — which is precisely reading the computed radius without
   drawing a shape (`packages/react/src/controls/segmented-control.tsx:194`). The mechanism existed;
   what is absent is a *public* accessor (`resolveConcentric` is not among `packages/react/src/index.ts:80-88`'s
   shape exports, and `@vitrea/geometry` is private). "Absent" overstates it.

4. **§1.6 Toolbar-group glass management — scored `absent, undecided` ("no way to split the shared
   background"); arguably `partial`.** Two levers predate the matrix: `GlassToolbarProps.group`
   (`packages/react/src/controls/toolbar.tsx:82`, present in the pre-2026-08-26 file) and
   `GlassSurfaceOwnProps.groupId`, which the v1 `GlassButton` already forwarded
   (`git show <pre-2026-08-26>:packages/react/src/controls/button.tsx` line 40). Naming a different
   group on one item is exactly Apple's description of `sharedBackgroundVisibility(.hidden)` —
   "the item is placed in its own grouping". What is genuinely absent is the declarative
   *spacer*, and the ergonomics; the capability is not.

5. **§1.1 `Glass.clear` — scored `replicated, unmeasured`; arguably `partial`.** The row's
   "replicated" half rests on an optics row and a dimming refusal. But the dimming policy the
   variant requires is drawn by no renderer — `grep -rn "dimming" packages/renderer-webgpu/src`
   returns zero hits, and `packages/platform-web/src/optics.ts:257-259` says so in the code
   ("Uncalibrated in either tier: the canonical scene matrix has no clear-variant scene").
   `ResolvedMaterial.dimming` (`packages/core/src/material.ts:126`) is produced and consumed by
   nobody. The variant resolves, warns and tints; its defining layer is not painted.

---

## 4. Native items the matrix never enumerated

1. **The reference's own layer tree as a source.** §0 grades the native side's sourcing by DocC
   JSON, HIG pages and session transcripts. Since W12 the project reads Apple's *rendered* layer
   tree directly — `CABackdropLayer`, `CASDFElementLayer` with `operation: union`,
   `CASDFLayer.smoothness`, backdrop `scale` 0.25, `marginWidth` 8.8 (claims §5.50, §5.77). This
   answers questions the public API cannot express at all — the container's blending law is
   `smoothness == declared spacing` with no separation threshold, which no Apple document states.
   §1.2's `init(spacing:)` row was written against prose that had no such answer.

2. **Material appearance selection, as distinct from the backdrop's tone.** §1 has no row for
   "which of the two materials this surface is made of". Apple selects it by appearance
   (`NSAppearance` / `preferredColorScheme`), and vitrea now ships the axis:
   `createGlassRoot({ colorScheme })`, `<GlassRoot colorScheme>`, `root.setColorScheme(...)` and the
   exported `darkMaterialProfile` (CHANGELOG 0.10.0 `c017625`). The matrix's only light/dark row is
   §3.2's *size-gated flip*, which is a different question — and the code says so in the same
   changelog entry ("a group's backdrop `hint` states the tone of what is behind the surface, and
   `colorScheme` states which material the surface is made of").

3. **Apple's corner saturation rule.** §1.5 enumerates `.continuous` and its
   `cornerCurveExpansionFactor`, but not what Apple does when the reach no longer fits half the
   short side. Measured in claims §5.84: Apple keeps the requested radius and compresses the
   shoulder, so the corner tends to a circular arc and a capsule is a true stadium. That is a
   distinct, native, enumerable behaviour of every capsule control, and it governed 21 of 40 bed
   scenes while vitrea got it wrong (claims §5.83).

4. **The tint's strength axis.** §1.6 and §1.1 enumerate `Glass.tint(_ color: Color?)` as "a
   per-surface author-set tint colour". `Color` carries opacity, and that opacity is a *strength*
   axis with its own law — measured as an encoded-space mix agreeing with Apple to 0.003 on ten
   attested rungs (claims §5.80). The matrix has no row for it, and it is the axis the OS 27 user
   slider (§1.7) would drive.

5. **The material's outer shadow.** No §1 row names it, correctly — Apple exposes no shadow API.
   But the reference casts one, it is two terms on one falloff (a backdrop-adaptive black multiply
   and a σ-40 blurred copy of the backdrop's own light, claims §5.62–§5.66), and at the matrix's
   date vitrea rendered zero across its entire footprint. An enumeration organised by API surface
   could not see the largest visible fidelity gap the project has measured.


---

# §3 behavioral-system re-score — 2026-09-10

Re-scored all 96 behavioral rows against verified HEAD `c5b3320`. 26 rows move. No repository files were edited.

## Headline

| §3 status | Recorded 2026-08-25 | Re-scored 2026-09-10 | Change |
| --- | ---: | ---: | ---: |
| `replicated+measured` | 14 | 26 | +12 |
| `replicated, unmeasured` | 16 | 18 | +2 |
| `partial` | 17 | 15 | −2 |
| `excluded by decision` | 7 | 12 | +5 |
| `absent, undecided` | 35 | 18 | −17 |
| `n/a` | 7 | 7 | 0 |
| **Total** | **96** | **96** | **0** |

### Scoring conventions

- The original column is the actual 2026-08-25 reading, retrieved from git at `322dc28`, not the subsequently annotated version. In particular, §3.10's last row originally said `replicated, unmeasured`; its later `replicated` annotation is not a seventh status.
- §0 defines five scoreable statuses; §4 supplies `n/a` as the sixth category.
- `replicated+measured` means implemented with named measurement evidence, not perfect fidelity or complete cross-tier equivalence.
- The scheme-selection mechanism receives `replicated, unmeasured`: its browser tests explicitly inspect resolved render input and styles, not pixels. The selected materials themselves have native calibration measurements.
- An unchanged status can have stronger evidence or an implementation correction. Where nothing relevant changed, the last column says **unchanged**.
- Named implementation or diagnostic refusals count as decisions. Merely listing an unresolved feature as future work does not turn it into implemented coverage.

## Evidence key

Every abbreviated citation below resolves to an absolute file path. A suffix such as `M:2231` is a line number; claims citations use the document's stable section numbers.

| Key | Absolute path |
| --- | --- |
| B | `docs/doperpowers/specs/2026-08-25-coverage-matrix.md` |
| C | `docs/doperpowers/specs/c9a-fidelity-claims.md` |
| W | `docs/doperpowers/specs/2026-08-28-post-v1-wave.md` |
| D | `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md` |
| CL | `packages/platform-web/CHANGELOG.md` |
| M | `packages/renderer-webgpu/src/material.ts` |
| O | `packages/renderer-webgpu/src/wgsl/optics.ts` |
| H | `packages/renderer-webgpu/src/wgsl/highlight.ts` |
| R | `packages/platform-web/src/root.ts` |
| CSS | `packages/platform-web/src/css-tier.ts` |
| P | `packages/platform-web/src/optics.ts` |
| L | `packages/platform-web/src/layer-model.ts` |
| CM | `packages/core/src/material.ts` |
| A | `packages/core/src/accessibility.ts` |
| F | `packages/core/src/foreground.ts` |
| I | `packages/react/src/interaction.ts` |
| S | `apps/reference-apple/scenes.json` |
| README | `packages/core/README.md` |
| LT | `packages/platform-web/test/layer-model.test.ts` |
| ST | `packages/platform-web/e2e/shared/color-scheme.spec.ts` |
| GI | `packages/platform-web/e2e/gpu/foreground-audit.spec.ts` |
| CI | `packages/platform-web/e2e/pixel/css-tier-pixels.spec.ts` |
| SF | `packages/platform-web/test/shape-fields.test.ts` |
| RM | `packages/motion/test/reduced-motion.test.ts` |

## §3.1 The two variants

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Exactly two variants exist | `replicated, unmeasured` | `replicated, unmeasured` | CM:22; S:307–314; M:1908–1910 | unchanged; no native `clear` calibration axis |
| Regular is context-independent | `replicated+measured` | `replicated+measured` | C §5.127; CL 0.15.0 | Broader measured bed and improved material; remaining fidelity misses are recorded |
| What regular optically does | `partial` | `replicated+measured` | M:3273; P:458–542; C §5.34–§5.35 | Blur now composes with a measured backdrop-luminosity response rather than a fixed tint alone |
| Clear has no adaptive behavior at all | `replicated, unmeasured` | `partial` | CM:123–158; R:1952–2025; M:3104–3141 | W7/W9's shared adaptation reaches clear too; "constrained" is metadata, not a zero-adaptation guard |
| Clear's three preconditions | `absent, undecided` | `absent, undecided` | CM:141–158; B:252 | unchanged |
| Dimming is 35% and conditional | `partial` | `partial` | CM:97–110,148–158 | unchanged; required policy and default 0.28 remain, not conditional 0.35 |
| The dimming layer may be omitted | `absent, undecided` | `absent, undecided` | CM:148–158 | unchanged; no dark-backdrop or existing-scrim exemption |
| Dimming may be localized | `absent, undecided` | `absent, undecided` | CM:97–118; B:255 | unchanged; no separately declared localized-dimming policy |
| Consequence of skipping dimming | `replicated, unmeasured` | `replicated, unmeasured` | CM:148–158 | unchanged; clear still falls back to regular with a diagnostic |
| Modality signalled by glass plus dimming | `absent, undecided` | `absent, undecided` | CM:125–126,146–158 | unchanged; resolved dimming remains clear-only |
| Never mix the variants | `replicated, unmeasured` | `replicated, unmeasured` | CM:15–17,217–227; B:258 | unchanged; the check remains group-scoped |

## §3.2 Size-dependent behavior

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Larger surfaces refract, shadow, and scatter more | `partial` | `replicated+measured` | M:2069–2073,2154–2232,2586–2592; C §5.52, §5.62, §5.127 | All three mechanisms now draw; the fitted outer shadow matters even though the inner-shadow size gain is identity |
| Opacity grows with element size | `absent, undecided` | `replicated+measured` | M:2231,4126–4140; P:2546–2560; C §5.26 | `sizeOcclusionGain=0.05` closes the former zero-gain result on the expanded bed |
| Size gates the light/dark flip | `absent, undecided` | `replicated+measured` | M:3104–3112,3254–3273; C §5.8, §5.115 | Size conditions adaptation on both tiers; the full scene-selected flip remains partial in §3.3 |
| Large surfaces pick up ambient colour spill | `absent, undecided` | `absent, undecided` | M's size/tone facets; O:411–449; B:273 | unchanged; the new exterior shadow lift is not ambient colour spilling onto the surface |
| Sheets become more opaque at full height | `excluded by decision` | `excluded by decision` | D:200–202; W:400–406 | unchanged |
| App-icon glass effects scale with size | `n/a` | `n/a` | B:275 | unchanged |

**Facet accounting:** lensing, scattering, opacity, outer-shadow depth, and size-conditioned adaptation are implemented and measured. They no longer all reduce to W2's original four scalar gains: scattering gained its own span/depth law, and W26 gives the light GPU material a real heavy-width parameter. Ambient spill onto large surfaces remains absent. The exact thin-surface appearance switch is a separate remaining gap, not closed by the existence of the size gate.

## §3.3 Light/dark adaptation

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Small elements flip light/dark to underlying content | `absent, undecided` | `partial` | C §5.8, §5.34, §5.89, §5.108; M:3104–3112,3273 | Continuous response and collapse exist; W21's scene-selected thin light/dark appearance switch does not |
| Foreground mirrors the material's flip | `partial` | `replicated+measured` | R:2519–2557; CSS:718–757; GI:95; C §3.3 | Both tiers decide inherited ink against adapted/tinted material automatically when an input is available |
| Foreground defaults to monochromatic | `partial` | `replicated+measured` | CSS:140–144,730–737; CI:402–434; GI:95 | Default ink is the achromatic light/dark pair on both tiers, not an adaptive-colour palette |
| Ship both colour variants in a single-appearance app | `absent, undecided` | `replicated, unmeasured` | CL:385–411; ST:52–82 | Both material bases ship and are selectable; app-owned content colours remain the app's responsibility |
| Runtime profile selection by colour scheme | `absent, undecided` | `replicated, unmeasured` | R:971–987; ST:6–17,52–133; CL 0.10.0 | `colorScheme: light/dark/auto`, live selection, exported dark profile, and override composition now exist |
| Variant appearance changes with system settings | `partial` | `partial` | A behavior table; CL:385–411; CM:53–59 | Scheme selection joins accessibility; the OS preferred-glass-look slider still has no runtime axis |
| visionOS luminance adaptation without Dark Mode | `n/a` | `n/a` | B:380 | unchanged |

The W7 annotation is evidence of an implemented adaptation mechanism, not today's complete verdict. W21 measured two thin dark appearances at the same footprint input; the surrounding scene selects between them. W24 confirmed that the dark structured capsules' remaining error is not the near-black collapse.

## §3.4 Colour and tinting

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Colourless by default; takes colour from behind | `partial` | `replicated+measured` | CM:83–95; M:3177; C §5.34, §5.36–§5.37 | Backdrop response is live and author tint is optional, supported, and calibrated |
| Tint is a brightness-mapped range of tones | `absent, undecided` | `partial` | M:3040–3086; C §5.36, §5.80–§5.82 | Measured luminance-dependent, hue-preserving shade exists; Apple's broader hue/chroma/vibrancy behavior is not implemented |
| Tint sparingly, on backgrounds not symbols | `absent, undecided` | `replicated, unmeasured` | CM:178–211; CL:1001–1002 | Public guidance and a non-pixel-tested tint-mixing diagnostic now name the intended composition |
| A solid fill is not a tint | `absent, undecided` | `replicated+measured` | M:3040–3086; C §5.36–§5.37, §5.80 | Supported tint varies with the material; full strength is an opaque shade, not a constant host fill |
| Avoid label/background colour collision | `absent, undecided` | `absent, undecided` | CSS:718–737; B:390 | unchanged; foreground choice uses level, not hue collision |

The current tint is **a shade**, not W3's original translucent wash. It multiplies the seed by a luminance-conditioned scalar and composites in encoded space at author strength. On the light profile its fitted endpoints are `0.5289` and `1.0175`, clamped to one. This earns brightness mapping, but not a general hue-changing vibrant tone system. W19 also records the remaining full-strength native gap and the CSS tier's per-source shading limit.

## §3.5 Lensing and refraction physics

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Samples an area larger than itself | `replicated+measured` | `replicated+measured` | P:3930; W:561–568; B:396 | Sampling support now follows post-policy blur; the measured enlarged-region contract remains |
| Lensing is the primary mechanism | `replicated+measured` | `replicated+measured` | M:3411–3479; C §5.49–§5.52; CL:747–778 | W12 replaces the earlier band with the measured steep profile and ovalized direction |
| Synthetic meta-material, not physical glass | `n/a` | `n/a` | B:398 | unchanged |
| Simulated lighting environment with moving lights | `partial` | `partial` | H:12–26; C §5.94, §5.108, §5.116; CL:166–174 | One-sided specular is retired; static diagonal and along-side rim laws exist, but no moving-light environment |
| Specular responds to device motion | `absent, undecided` | `absent, undecided` | I:252–274; H:12–26 | unchanged; no device-motion input |
| Touch and pointer have different intensity | `partial` | `partial` | I:235–274 | unchanged; pointer handlers do not branch on pointer type |
| Light bleeds into the shadow | `absent, undecided` | `replicated+measured` | O:411–449; M:2592; C §5.62, §5.66 | W14 adds a blurred-backdrop light term beneath the GPU shadow; CSS derives net darkening instead |
| Materialize/dematerialize is not a fade | `partial` | `partial` | I:193–225; B:403; W:400–401 | unchanged; the motion channel exists without a complete public optical materialization transition |
| WWDC26's revised optics | `absent, undecided` | `excluded by decision` | W Decision Log 2, W:400–403 | Reference remains macOS 26.5; OS 27 migration is explicitly deferred |

The old "single fixed `lightDirection`" description is stale. W24 removed the one-sided specular term from both tiers; its profile fields survive but are unread. The current resting rim uses a symmetric diagonal light factor and W25's position-dependent grading. None supplies moving sources or a stock shimmer driver.

## §3.6 Container merging, morphing, and interactivity

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Glass cannot sample glass | `replicated+measured` | `replicated+measured` | C §5.39, §5.95; B:417 | Mixed-backend stacking now composites and receives the base material's tone; the recorded architectural-analogue status is retained |
| Proximity-driven continuous blending | `replicated+measured` | `replicated+measured` | C §5.77 §6; B:418 | Native spacing behavior is now read directly; the old "unmeasurable at 12px" account is superseded, and a separation-rule mismatch remains |
| Containers enforce uniform adaptation | `replicated, unmeasured` | `replicated, unmeasured` | CM:112–128; C §5.77 §6; B:419 | unchanged; shared group policy is not a full native uniform-adaptation measurement |
| Grouping is mandatory for correctness | `replicated+measured` | `replicated+measured` | W:561–568; B:420 | unchanged |
| Shapes merge like liquid droplets | `replicated, unmeasured` | `replicated, unmeasured` | C §5.77 §6; B:421 | No fitted native neck/bulge law landed; the native spacing/separation discrepancy is now explicit |
| Morphing preserves one floating plane | `replicated, unmeasured` | `replicated, unmeasured` | B:422; W:400–401 | unchanged |
| Presentations morph from their originating control | `replicated, unmeasured` | `replicated, unmeasured` | B:423; W:400–401 | unchanged |
| Gel-like stretch tracks the gesture | `partial` | `partial` | I:193–241,252–274 | unchanged; state-driven compression, not continuous gesture-following stretch |
| Glow spreads onto nearby glass | `excluded by decision` | `excluded by decision` | D:159,200–202; W:405–408 | unchanged |
| Elements lift into glass transiently | `absent, undecided` | `absent, undecided` | I:193–225; CM:22; B:426 | unchanged; no transient material-presence behavior |
| Drag preserves momentum and stretches | `excluded by decision` | `excluded by decision` | D:200–202 | unchanged |
| Window/scene focus changes the material | `absent, undecided` | `excluded by decision` | W:412–413,717–720; C §5.11 | Inactive material is measured and explicitly deferred as a window-focus-aware feature |
| Dragging a sheet recedes, opacifies, and grows it | `excluded by decision` | `excluded by decision` | D:200–202 | unchanged |
| OS 27 bounce-on-click | `partial` | `partial` | I:191–224; RM:164–200; W:400–403 | unchanged; spring compression exists, not a measured OS 27 interaction reproduction |

## §3.7 Layering, elevation, and the floating layer

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Distinct functional layer above content | `replicated+measured` | `replicated+measured` | B:436; L:155–178; W Decision Log 6 | The plane model now also has structural placement diagnostics |
| No glass on glass | `partial` | `partial` | L:137–168; LT:180–206; C §5.95 | DOM nesting is diagnosed across planes; intentional sibling/cross-plane stacking remains supported |
| Shadow opacity is content-aware | `absent, undecided` | `replicated+measured` | M:4239–4254,4317–4328; C §5.62, §5.66 | Thin shadow opacity follows backdrop level; thick shadow follows span; no semantic text detector is claimed |
| Glass lifts controls from the background | `replicated, unmeasured` | `replicated, unmeasured` | M:2582–2596; B:439 | Outer-shadow measurements strengthen the optical evidence, not a native control-affordance measurement |
| Scroll-edge effect as primary separation | `excluded by decision` | `excluded by decision` | D:200–202; W:403–404 | unchanged |
| Hard scroll-edge style for pinned accessories | `excluded by decision` | `excluded by decision` | D:200–202 | unchanged |
| Rounded forms nest into hardware | `absent, undecided` | `absent, undecided` | B:442,503; W:405–406 | unchanged; no window/display-corner input |
| Avoid content/glass intersection at rest | `absent, undecided` | `excluded by decision` | W Decision Log 6; L:58–59 | Detection explicitly rejected: per-frame geometry without an identifiable content layer |
| Non-interactive items should not be glassed | `absent, undecided` | `excluded by decision` | W Decision Log 6; L:54–57 | Detection explicitly rejected because legitimate glass containers would trigger it |
| Use glass sparingly | `absent, undecided` | `absent, undecided` | README:124–154; B:445 | unchanged; placement guidance and cost limits do not implement an interface-wide overuse rule |

## §3.8 Accessibility modes

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Reduce Transparency: frostier, more obscuring | `replicated+measured` | `replicated+measured` | S:544–564; C §5.6, §5.62 §5; M:4361–4384 | Native fixtures and adopted gates now exist; shadow adaptation also flattens under the preference |
| Increase Contrast: monochrome plus border | `replicated+measured` | `replicated+measured` | S:566–586; C §5.6, §5.103–§5.106; CL:246–251 | Native coupled-state measurements exist; strong border now replaces the whole rim |
| Reduce Motion: lower intensity, no elasticity | `replicated, unmeasured` | `replicated, unmeasured` | RM:42–108,164–200; W Decision Log 3 | unchanged; no native frame-sequence metric |
| General HIG Reduce Motion list | `partial` | `partial` | RM:42–108; I:193–224; B:474 | unchanged; no complete blur/depth-transition policy |
| Developer tests custom elements under settings | `replicated, unmeasured` | `replicated+measured` | W:108–138; C §5.6; S:544–586 | Accessibility testing now includes captured native reference profiles |
| Stacked-setting dark-mode caveat | `replicated, unmeasured` | `replicated, unmeasured` | A precedence fold; S:432–660; B:476 | unchanged; the captured accessibility profiles are light, not dark stacked-setting references |
| All three automatic, system-wide modifiers | `replicated, unmeasured` | `replicated, unmeasured` | A behavior table and resolver; B:477 | unchanged; material axes remain modifiers, motion still lacks native temporal measurement |
| Modes compose rather than override | `replicated, unmeasured` | `replicated+measured` | W Decision Log 8; C §5.6; A precedence fold | Increase Contrast plus Reduce Transparency is now measured against macOS's coupled reference |
| Differentiate Without Color | `absent, undecided` | `absent, undecided` | A `ACCESSIBILITY_FLAGS`; CM:67–70 | unchanged; author tint now exists, but this accessibility input still does not |
| Show Button Shapes | `absent, undecided` | `absent, undecided` | A `ACCESSIBILITY_FLAGS`; B:480 | unchanged |
| Forced-colors/system-colour mandate | `replicated+measured` | `replicated+measured` | A `forcedColors` behavior row; CSS:728,1004–1016 | unchanged |
| Web-side accessibility overrides exceed native | `n/a` | `n/a` | A override types; B:482 | Captures remove the old evidence blocker, not the read-only-native versus per-root-web asymmetry |

Native accessibility evidence is no longer empty. The important limitation is different now: macOS couples Increase Contrast with Reduce Transparency, so that captured profile does **not** establish a standalone Increase Contrast claim. The dark accessibility combination and motion sequences remain unmeasured.

## §3.9 Legibility and the content-layer prohibition

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Do not use glass in the content layer | `absent, undecided` | `partial` | L:85–126,172–178; README:124–154 | Documentation and registration diagnostics exist for identifiable roles, not arbitrary content |
| Lists and tables named explicitly | `absent, undecided` | `replicated, unmeasured` | L:85–126,172–178; LT:90–116,218 | List/table tags and roles now trigger a tested developer warning |
| No scroll means nothing to refract | `absent, undecided` | `excluded by decision` | W Decision Log 6; L:44–49 | Temporal detection explicitly rejected; a resting page cannot prove that it never scrolls |
| Transient interactive content-layer exception | `excluded by decision` | `excluded by decision` | D:200–202; B:491 | unchanged |
| Controls sit on material, not directly on content | `absent, undecided` | `absent, undecided` | L:50–53; B:492 | unchanged; W4 identifies a missing alternative, not an implemented separation rule |
| Four standard-material thicknesses | `absent, undecided` | `absent, undecided` | CM:22; L:50–53 | unchanged; no standard-material family |
| Vibrancy is automatic foreground behavior | `absent, undecided` | `absent, undecided` | CSS:718–737; M:3040–3059; B:494 | unchanged; binary ink selection and tint shading are not foreground vibrancy |
| Vibrancy has named levels and a floor | `absent, undecided` | `absent, undecided` | CSS:140–144,718–737; B:495 | unchanged; no label/fill hierarchy |
| Thickness is a legibility/context tradeoff | `partial` | `partial` | M:3254,3363–3398,4126–4140; C §6.5 | Size-derived opacity exists; author thickness still is not a calibrated native thickness/contrast axis |
| Choose semantically, not by apparent colour | `replicated, unmeasured` | `replicated, unmeasured` | CM:22–24,112–128; CL:406–411 | Variant remains semantic; author colour is a separate tint axis rather than a replacement variant |

## §3.10 Concentricity

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Hardware informs curvature | `absent, undecided` | `absent, undecided` | B:503; R:319 | unchanged; concentric parent is a scene node, not a window/display corner |
| Radius matching depends on corner distance | `partial` | `partial` | W:405–406; CL:1048–1054; B:504 | Public parent links exist, but the level-set rule remains position-independent |
| Diagnose pinched or flared corners | `absent, undecided` | `absent, undecided` | C §5.84–§5.86; B:505 | unchanged; declaration-conformance measurement is not a nested-corner aesthetic diagnostic |
| Nested shapes are concentric to containers | `partial` | `replicated, unmeasured` | R:319,2307–2309,2936–2938; SF:104–122,161–175 | W5 makes the concentric parent link consumable by registered glass hosts and forwards it to the renderer |
| Fixed, capsule, and concentric shape types | `replicated+measured` | `replicated+measured` | C §5.84–§5.86; CL 0.9.0 | W20 corrects the render-path capsule clamp; actual capsules now reach the declared stadium |
| Apply material to the control, not inner views | `replicated, unmeasured` | `replicated, unmeasured` | W Decision Log 6; L:137–168; LT:180–206 | W4 supplies the cross-plane structural check the original credit incorrectly assumed |

## §3.11 Performance

| row | 2026-08-25 status | 2026-09-10 status | evidence | what changed |
| --- | --- | --- | --- | --- |
| Combine effects into a container for performance | `replicated+measured` | `replicated+measured` | C §5.77 §6; B:514 | unchanged; native layer inspection also confirms the shared backdrop container |
| One sampling pass per group | `replicated+measured` | `replicated+measured` | C §5.77 §6; B:515 | unchanged; source-owned pyramid reuse remains the stronger runtime invariant |
| Limit simultaneous effects | `replicated+measured` | `replicated+measured` | CL:638–646,1161–1164; C §5.127 | Governor remains; CSS body collapse and the heavy-tap cost are now measured additions |
| OS 27 glass profiling metric | `n/a` | `n/a` | B:517 | unchanged |
| Third-party engineering report hosted by Apple | `n/a` | `n/a` | B:518 | unchanged |
| tvOS hardware floor | `n/a` | `n/a` | B:519 | unchanged |

## Original statuses that were wrong at the time

1. **§3.10 — Apply material to the control, not its inner views.** The original `replicated, unmeasured` credit claimed structural enforcement that did not exist. A cross-plane nested host escaped the geometric overlap check. W4 explicitly records the correction in W Decision Log 6, and `LT:206` tests the formerly silent case. The original status is preserved in the comparison; the same status is now earned by different, actual code.

2. **§3.10 — The three shape types.** The original `replicated+measured` credit overclaimed the render-path capsule implementation. C §5.83–§5.84 establishes that the GPU renderer had drawn capsules with a radius clamped to about `0.327` of the short side since v1; its shape metric hid the shoulders. W20 fixed it, and C §5.86 supplies the measurement that makes today's unchanged headline status defensible.

The original light/dark contradiction was a wrong interpretation of an inadequate capture bed, but its **absent** implementation status was not wrong. Likewise, stronger accessibility evidence is a stale-evidence correction, not proof that the original policy-test status was invalid.

## Native behaviors not separately enumerated by the matrix

- **Two settled, byte-reproducible appearances under the same attested active conditions.** Not the active/inactive distinction: C §5.18, §5.22–§5.25; W's stability-study record.
- **Thin dark appearance can depend on scene content beyond the surface footprint.** The same footprint input produces different native appearances: C §5.89. The matrix's backdrop-flip row does not enumerate this distinct input.
- **The body is a sharp/heavy mixture graded by depth from the contour, with device-scale behavior.** C §5.50, §5.61, §5.69–§5.70, §5.121. "Scatter more when larger" did not enumerate this structure.
- **The resting rim has both a symmetric diagonal angular field and a position-dependent corner-to-corner field.** C §5.108, §5.113, §5.116. A single directional specular term cannot reproduce it.
- **Collapsed glass retains an absolute rim and some blurred backdrop transmission; tinted rims retain the paint's chromaticity.** C §5.100–§5.108.
- **Reduce Transparency flattens shadow adaptation and suppresses the shadow's light term.** C §5.62 §5; `M:4361–4384`.
- **Above the continuous-corner budget, Apple preserves the requested radius and compresses the shoulder.** C §5.84. The three-family enumeration omitted that limiting behavior.

## Rows that moved

- **§3.1:** regular's optical behavior; clear's no-adaptation claim.
- **§3.2:** larger-surface refraction/shadow/scatter; size-dependent opacity; size-gated adaptation.
- **§3.3:** small-element flip; foreground mirroring; monochromatic foreground default; shipping both colour variants; runtime scheme selection.
- **§3.4:** colourless/default backdrop colour; brightness-mapped tint range; sparse/background tint guidance; supported tint instead of solid fill.
- **§3.5:** light bleeding into shadow; OS 27 optics disposition.
- **§3.6:** window/scene-focus material disposition.
- **§3.7:** content-aware shadow; resting content/glass-intersection disposition; non-interactive-glass disposition.
- **§3.8:** custom-element accessibility measurement; setting composition measurement.
- **§3.9:** content-layer prohibition; list/table diagnostics; no-scroll diagnostic disposition.
- **§3.10:** registered glass consuming concentric parent links.

Verification was read-only: source, historical statuses, native scene definitions, tests, and recorded measurements were inspected; test suites and capture runs were not rerun.
