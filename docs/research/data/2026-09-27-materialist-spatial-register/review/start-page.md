# Start-page — independent source review

Reviewed 2026-09-27 against the materialist skill's spatial register, its vitrea cookbook, the spatial-register specification's Design B reading 3 and Design C, the page's source and record, and the supplied audit and captures. Instrument-only checks 1, 3, 10, 13 and 15 are not applied; their spatial replacements are 21–28. (Pre-fix reading; the fix wave that followed is recorded in the page's `DESIGN.md` part two.) The scoped motion reading is **r23 = 1; r23Strict = 0**. Supporting live checks and three captures are in `review/start-page-live/`.

## Findings

1. **Check 14 `[legibility]` — fails the check: changing Reduce Motion while the Photograph platter is open makes it disappear.**

   **Page call site:** `apps/demo/src/gallery/start-page/photograph-ornament.tsx:128–145`.
   **Underlying cause:** `packages/react/src/morph.tsx:315–326`, `443–450`, `492–500`.

   Reproduced in full Chromium on the actual WebGPU texture tier at 1440 × 900, DPR 1, `?at=15:10`: open Photograph with Reduce Motion off, then change the preference to reduce. Its host moves from approximately `(61, 618, 320, 226)` to **`(0, 0, 0, 0)`** on subsequent frames. Keyboard focus remains on the now-invisible selected photograph radio. Forced colours is not required. The runtime continues reporting `health: ok`, illustrating why the audit's successful policy resolution does not establish usability.

   The matched-geometry morph recreates zero-seeded geometry drivers when `motionProfile` changes, but its placement effect returns when neither initial placement nor `open` changed. The ticker then writes those zero drivers to the host. This is a **runtime seam, not a reason to reject the register or replace GlassMorph with a page animation**. The existing record does not name this seam.

   **Fix:** preserve/reseed and retarget the geometry when the motion profile changes; retain the current open/closed endpoint and focus. Cover both settled-open and in-flight preference changes in the runtime regression test. A page workaround should not introduce an opacity transition or force an unnecessary close. Keep this as a recorded failure until the runtime fix lands.

   Control checks succeeded: Reduce Motion enabled before mounting still permits opening and closing; Escape returns focus to the trigger. The page-owned switch transition becomes `0s` when the preference changes, so that child implementation is correct.

   **Evidence:** `review/start-page-live/reduced-motion-open.png` and the accompanying `checks.json`.

2. **Check 9 `[geometry]` — partial: the closed Photograph ornament stops being an exact capsule on the CSS tier.**

   **Location:** `apps/demo/src/gallery/start-page/photograph-ornament.tsx:134`; `apps/demo/src/gallery/start-page/start-page.css:605–617`.

   The page derives radius 24 from the intended 48 px closed height. On WebGPU the actual box is 248 × 48, so it holds. On CSS the generated morph host retains `box-sizing: content-box`; the runtime's 1 px border produces an actual **250 × 50** box while both the registered and CSS radius remain **24**, rather than 25. The other four hosts get border-box sizing through `boxStyle`; this generated host does not. The border is runtime-authored, so this is **not** a host-border ban violation.

   **Fix:** make the morph host's sizing border-box and verify its content/geometry on both tiers, or derive the closed radius from its measured outer span. This is a tiny, non-blocking geometry discrepancy suitable for tracked debt if it is not included in the fix wave; it should not be described as exact capsule geometry on both tiers.

3. **Checks 12 and 23 `[legibility]` — partial verification: the independent audit does not reproduce the record's full contrast matrix.**

   **Claim:** `apps/demo/src/gallery/start-page/DESIGN.md:219–254`.
   **Evidence:** `docs/research/data/2026-09-27-materialist-spatial-register/audit/start-page.json`.

   The supplied audit has **3,061/3,061 passing line readings**, not the maker's separately reported 14,128 readings. It captures first viewport, Today scroller positions and menu in both schemes; four environment phases in both schemes; and light-scheme CSS, receded and reduced-transparency subsets. It does not independently establish the full phase × pose × tier × transparency matrix in both schemes, nor preserve the maker's entire successful line/icon population. The audit URL also lacks `?at=15:10`: its captures show 17:06–17:07, whereas the maker's record describes a pinned 15:10 run. Consequently it does not reproduce that run's current-event state.

   This is **not an observed contrast failure** and the different minima are not contradictory measurements. The audit's per-line method is the relevant reading; its older `glassContrast` section contains scroller-clipping artefacts and should not replace it.

   **Fix:** retain/link the maker's raw line-and-mark matrix and identify its capture/run separately from the independent audit. If the missing combinations are required for an independently verified full-check verdict, capture those combinations explicitly; do not change the ink merely because the supplied evidence is narrower.

4. **Checks 19 `[honesty]` and 28 `[material]` — note: retain the distinctions between input, rendered measurement and historical layout numbers.**

   **Locations:** `apps/demo/src/gallery/start-page/DESIGN.md:171–176`, `194–216`, `258–265`.

   The important fallback claim reproduces exactly: **569,364 present-host device pixels at 1440 × 900, DPR 1, with `cssBody: collapsed`**. I also inspected the missing two-layer case live: all five groups report `two-layer` at 1024 × 768, DPR 1, and content remains usable. That current read totals **390,950**, rather than the record's 387,670. The current design-size window gap is 63 px, rather than the record's 64. Neither discrepancy crosses the CSS budget or creates an overlap.

   Likewise, the record's inset body medians and the audit's whole-host encoded means are different statistics, not numbers that should be substituted for one another. All **160 audit host readings** remain outside the dead band; a surrounding environment ring entering it is not a failing host.

   **Fix:** append the current layout readings beside the earlier ones and label the measurement definitions. Preserve recorded historical numbers rather than rewriting them to match the new read.

## What holds cleanly

- **Register and inventory — checks 21, 22.** The record explicitly chooses spatial for a launcher: the photograph is the environment, not the object being edited. Now is one glance module; Places and Today are two task windows, not six glass tiles. At the specified desktop size their spans are 320, 404 and 376 px, with shared thickness 8 and fixed radius 32. The window corner is the named concentric anchor. Audit glass coverage is **43.89%**, leaving the environment around every task surface. Instrument-only checks 1, 3, 10, 13 and 15 are not applied.
- **Environment and hints — checks 6, 19, 21.** Four real photographs provide broad and fine structure; both schemes and all four phases were inspected, including their suppressed-glyph twins. The grade is painted into the texture, not laid over glass. `environment.ts:67–113` paints the actual crop/grade; `132–175` measures each footprint using the runtime's encoded-channel-mean statistic. `app.tsx:243–297` recomputes declarations when the painted environment or layout changes and samples the morph's moving box through the root frame subscription. These are measured hints, not constants. Source average, declared input and rendered level are separately identified. The audit reports five healthy WebGPU/gpu-texture/exact/true groups, no diagnostics and no findings in either ban subset.
- **Layers, fills and ornaments — checks 2, 11, 16, 24–27.** No nested hosts or authored host background, border, shadow or backdrop filter was found. Semantic lists remain children of labelled section hosts. Child fills carry interaction/current/selection roles rather than additional elevation; neither windows nor module is tinted. All surfaces are regular; clear is not spent. Search and Photograph have separate overlay groups outside their associated windows. `layout.ts:58–85` derives a conservative gap from runtime padding and current/nominal policy rather than pinning a pixel gap. The open Photograph platter stays below Now in exposed environment rather than sampling through a window.
- **Ink and geometry — checks 8, 18, 23.** Primary ink is on children; authored secondary is explicitly 84% of the runtime primary, preserving its polarity. Readable text uses medium through bold weights; tertiary is limited to the forecast separator. The module contains figures and short labels, not prose. Child radii follow their actual inset structure; opaque thumbnails are concentric within their option fills. The CSS capsule exception is listed above.
- **Today scrolling — check 25.** The host and ornaments remain fixed. `today-window.tsx:98–132` tracks the child's scroll edges and initial agenda position. `start-page.css:350–379` masks only that child, only where more content continues. Top, middle and bottom captures preserve reading order and reach the final tasks. No root-ancestor mask is introduced.
- **Motion and r23 — check 17.** Photograph uses one matched-geometry GlassMorph with matching smoothing references, not an opacity arrival. Search's interactive GlassSurface and the closed morph both use the runtime's channel-based light/compression. No host transitions opacity, background or filter. Plain items inside the open platter carry hover/selected fills and no separate press: **scoped r23 passes; strict r23 does not**. The only authored transition is the switch knob's state change, disabled by a live Reduce Motion media query. No decorative idle movement was found; the minute clock and time-of-day photograph changes are content.
- **Accessibility and fallbacks — checks 14, 28, apart from finding 1.** The page offers and persists an explicit Reduce Transparency boolean. Reduced transparency and increased contrast captures remain structured and readable. The forced-colours frames are genuinely on children, keyed to the tier actually drawn—not authored host borders. The open forced-colours platter was inspected live as well: radio selection, switches, event outline, labels and credits survive. Both CSS body forms preserve the hierarchy. `windowActivation="auto"` remains enabled; the receded audit records `inactive` and 385/385 passing lines. Dark-receded completeness remains the evidence limitation above.
- **Runtime workarounds are stated accurately.** `photograph-ornament.tsx:62–71` writes `data-glass-role` onto the generated morph host after frames; the other roles are declarative. `app.tsx:259–280` dispatches the documented synthetic scroll event when that host's rounded rect key changes, invalidating stale geometry after same-sized movement. Neither is disguised as material authoring; both deserve the runtime tracking already requested by the maker.
- **Honesty about Apple — check 20 and the fidelity clause of 28.** The record states macOS 27 material composed spatially, not measured visionOS fidelity; it calls window-scale optics extrapolated, names the nearest Apple surfaces and explicitly says no native comparison was made. It also records the visible diagonal rim discrepancy. No native comparison was fabricated in this review.

## Judgment

Daybreak is the register the skill describes: a product-owned environment surrounding three substantial task surfaces, with content composed on glass and two attached ornaments rather than a glass-card dashboard. Its strongest decisions are the independently graded environment, per-footprint tone declarations, restrained ink hierarchy and the grouping of the brief's six functions into three canvases. The supplied captures support that judgment in both schemes, without a material, layer or environment failure. It is not yet an unconditional QA pass: the live Reduce Motion transition genuinely loses the open platter, the CSS ornament has a small capsule-sizing mismatch, and the maker's larger contrast claim must remain distinct from the narrower independently retained evidence. The first issue belongs to the runtime, not to the spatial register's design conditions.
