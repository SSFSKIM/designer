# Chromium bug report draft — ready to file at issues.chromium.org

File under **Chromium > Blink > Paint** (or Blink > Compositing). Attach
`repro.html` from this directory. Everything below the line is paste-ready; the
bracketed environment line should be adjusted to the machine you file from.

---

**Title:** `backdrop-filter` renders as a no-op on an element with
`clip-path: path()` inside an ancestor with `overflow: hidden` + `border-radius`
(regression 151 → 152)

**Steps to reproduce:**
1. Open the attached `repro.html` (self-contained, no scripts needed for the
   visual repro).
2. Compare the two panels. Both are `backdrop-filter: blur(14px) saturate(1.8)`
   over a checkerboard, with the same rounded-rect clip — the left panel via
   `clip-path: path('M22,0H218A22,22…Z')`, the right via
   `clip-path: inset(0 round 22px)`. Both sit inside a container with
   `overflow: hidden` and `border-radius: 6px`.

**Expected:** Both panels blur the checkerboard identically. Chrome 151,
Firefox, and Safari all render them identically.

**Actual (Chrome 152):** The left (`path()`) panel's backdrop-filter has no
effect at all — the checkerboard shows through sharp. The clip itself still
applies; only the filter is dropped. No console message, no devtools warning.

**Regression range:** last good 151.0.7922.34, first bad seen 152 stable
(reproduced on 152.0.7977.64). [Filed from macOS 26.5 (arm64); also observed
on macOS retail Chrome 152 on a second machine.]

**The exact trigger set, measured** (filter-on vs filter-off screenshot
pixel-diff; "live" = large diff, "NO-OP" = 0.00):

| ancestor `overflow:hidden` + `border-radius` | element `clip-path` | 151 | 152 |
| --- | --- | --- | --- |
| yes | `path(…)` | live | **NO-OP** |
| yes | `inset(0 round 22px)` | live | live |
| yes | `inset(0)` | live | live |
| yes | `circle(45%)` | live | live |
| yes | `polygon(…)` | live | live |
| yes | none | live | live |
| no (either property removed) | `path(…)` | live | live |

So all three ingredients are required — the element's `clip-path: path()`
specifically (every basic-shape value is unaffected), plus both `overflow:
hidden` and `border-radius` on an ancestor. The ancestor needs no opacity,
filter, mask, or blend mode, i.e. nothing that forms a backdrop root per
Filter Effects 2 — and an element's own `clip-path` forming a backdrop root
must not disable that same element's own `backdrop-filter` (it doesn't for any
basic shape, and didn't for `path()` in 151).

**Why it matters:** a `clip-path`'d `backdrop-filter` panel is a standard
technique for glass-morphism UI (it is how arbitrary-shaped frosted panels are
built), and rounded `overflow: hidden` containers (cards, modals, scroll areas)
are ubiquitous. The combination fails silently — the panel simply loses its
frost with no signal — and pages have no feature-detectable workaround short of
rewriting `path()` clips as basic shapes where possible.

---

## Provenance (not part of the report)

- Found 2026-08-26 through vitrea's S1 manual-check page in the user's retail
  Chrome 152; bisected to the three-ingredient shape in
  `packages/platform-web/.vitrea-tmp/isolate*.mjs`; the `path()`-only
  differentiator measured 2026-08-28 in
  `packages/platform-web/.vitrea-tmp/crbug-differentiator.mjs` (12 cells × 2
  builds, table above).
- `repro.html` itself verified: 151.0.7922.34 broken-panel diff 31.37 (live),
  152.0.7977.64 broken-panel diff 0.00 (no-op) with control at 31.38.
- vitrea's product is measured immune under its default mount (Decision Log
  #39): CSS-tier hosts clip with `border-radius`, and the GPU tier's proxies
  live in a `position: fixed` plane root parented to `body`, outside any
  rounded-overflow ancestor. The engine-versioned probe advisory row remains a
  post-v1 seed for the class.
