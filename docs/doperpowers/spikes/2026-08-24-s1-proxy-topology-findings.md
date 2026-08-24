# S1 — Backdrop proxy topology spike — Findings

> **Parent:** [`docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`](../specs/2026-08-24-vitrea-liquid-glass-design.md)
> — child **S1** (*Backdrop proxy topology spike — spike, findings never a merge*),
> parent pin **`b756ccd`**. Binding design inheritance: §The rendering contract,
> §Backdrop & analysis contracts, §Gating spikes (S1). Contracts under test: **X1**
> (rendering sandwich & plane law) and **X2** (the `probe-failed` demotion path).
>
> Prototypes: [`spikes/s1-proxy-topology/`](../../../spikes/s1-proxy-topology/).
> Throwaway by design — the findings below are the deliverable.

## Verdict at a glance

| Engine | Verdict | Basis |
| --- | --- | --- |
| **Chromium** (headless 151.0.7922.34 + retail Chrome 151.0.7922.172) | **Confirmed, with four contract amendments** | 122 screenshot variants × 2 builds, region-split diffs, exact-arithmetic probes |
| **Gecko** (Firefox 154.0 retail, Firefox 153.0 Playwright) | **Not measured — blocked** | `backdrop-filter` renders as a no-op in *every* capture path available on this machine; `filter`, `mix-blend-mode` and `opacity` all render correctly in the same runs |
| **WebKit** (WebKit 26.5 Playwright, system WKWebView on macOS 26.5.2) | **Not measured — blocked** | same failure signature; real Safari 26 could not be driven at all (needs an admin/GUI action) |

The topology **holds in Chromium** and is *better* than in-place `backdrop-filter`
on one axis (edge fidelity), at the price of four rules the parent spec does not
yet state — a mask-extent clarification, a padding minimum of 3σ, a group
separation invariant, and deterministic proxy paint order. The double-filter
question has a definite answer: **sibling proxies do chain**, and the contract
needs an invariant to bound it. The conformance probe
**cannot be a pixel test** in any engine; the honest probe is structural plus a
CI-generated conformance table, and one whole failure class stays undetectable.

Two of three engines are an **open gate**, not a pass and not a fail. §Environmental
blocker says exactly what is needed to close it; a ready-made
[`manual-check.html`](../../../spikes/s1-proxy-topology/pages/manual-check.html)
closes it in about two minutes of human attention.

---

## Method and how to read the numbers

`spikes/s1-proxy-topology/pages/bench.html` builds the exact sandwich from URL
parameters, so every variant is pixel-comparable: identical page content,
identical final glass geometry, and only *where the filter lives* or *how the
proxy is masked* changes between two images being diffed.

```
#scene              patterned page content: gradient, 24px checkerboard,
                    a deterministic high-frequency PNG, high-contrast type,
                    optional position:fixed stripe, optional overflow:auto scroller
  ↓
#glass-root         position:fixed, full viewport (the "plane root")
  └ .plane            position:fixed 1000x800
      ├ .proxy-layer  one pointer-events:none proxy per sampling group,
      │               box = union(shapes) inflated by `pad`, clipped by
      │               clip-path: path(...) to the shape union, carrying
      │               backdrop-filter: blur(20px) saturate(1.8)
      ├ canvas.optics transparent; paints placeholder tint + rim
      ├ .hosts        real <button>, transparent background
      └ canvas.highlight
```

Diffs are per-region, because the whole question is *where* error lives. For each
1000×800 viewport a 660×240 window is captured around the glass band, and each
comparison reports `mean` and `max` per-channel absolute difference over named
regions: `A_interior` / `B_interior` (each shape inset 26px), `A_edge` / `B_edge`
(the outer 26px ring), `GAP` (the 40px band between the two shapes),
`OUTSIDE_LEFT` and `OUTSIDE_ABOVE` (background that must never change),
`*_inner` (the 54px band of each shape facing the gap in the 8px-gap stress
geometry). Values are 0–255. `mean 0 / max 0` means byte-identical.

Two builds were run: **headless Chromium** (software rasterisation, fully
deterministic, the reference numbers below) and **retail Google Chrome** (GPU
rasterisation, which adds roughly ±10/255 of run-to-run noise on high-frequency
content and produces non-monotonic sweeps — treat it as a qualitative
cross-check only, and read the sweeps off headless Chromium).

Driver: [`harness/run.mjs`](../../../spikes/s1-proxy-topology/harness/run.mjs).
Raw results: `spikes/s1-proxy-topology/shots/report.json`, per-engine
`shots/<engine>/results.json`, difference heatmaps under `shots/<engine>/heat/`.

---

## Environmental blocker — Gecko and WebKit pixels are unobtainable here

This is the single most consequential outcome of the spike, so it comes before
the findings that depend on it.

**Symptom.** In Firefox and WebKit, every `backdrop-filter` variant renders
byte-identically to the same scene with no filter at all. Not "slightly
different" — identical. On a flat `#3a5a80` ground with `backdrop-filter:
brightness(1.25)`, Chromium returns `rgb(72,112,160)` (exactly 1.25×) while
Firefox and WebKit return the untouched `rgb(58,90,128)`.

**It is specific to `backdrop-filter`.** A four-row control page
([`pages/min.html`](../../../spikes/s1-proxy-topology/pages/min.html), driven by
[`harness/engine-check.mjs`](../../../spikes/s1-proxy-topology/harness/engine-check.mjs))
measures `backdrop-filter`, `filter`, `mix-blend-mode` and `opacity` side by side
on the same ground. Expected `128 / 128 / 112 / 159`:

| Build | backdrop-filter | filter | mix-blend-mode | opacity |
| --- | --- | --- | --- | --- |
| Playwright Chromium 151 | **128** | 128 | 112 | 160 |
| retail Chrome 151 | **128** | 128 | 112 | 159 |
| Playwright Firefox 153 (headless, headed, and with WebRender/acceleration prefs forced) | **64** | 128 | 112 | 160 |
| Playwright WebKit 26.5 (headless and headed) | **64** | 128 | 112 | 160 |
| retail Firefox 154 (`--headless --screenshot`) | **64** | 128 | 112 | 160 |
| retail Firefox 154 (headed, WebDriver BiDi `captureScreenshot`, both `origin: document` and `origin: viewport`) | **64** | 128 | — | — |
| system WKWebView on macOS 26.5.2 (`takeSnapshot`, `afterScreenUpdates: true`, window both off-screen and on-screen) | **64** | 128 | 112 | 160 |

Every other compositing-dependent feature in the same screenshot is correct, so
these builds are not "compositing nothing".

**Not a markup problem.** Sixteen structural variants
([`pages/structures.html`](../../../spikes/s1-proxy-topology/pages/structures.html))
— with and without a background on the filtered element, with and without child
content, `isolation: isolate` parent, `z-index: 0` parent,
`will-change: backdrop-filter`, `translateZ(0)`, `border-radius`,
`clip-path`, `contain: paint`, `position: fixed` on the backdrop and on the
filtered element, and `blur` / `invert` / `grayscale` instead of `brightness` —
all return 64 in retail Firefox, headless and headed, while the CSS-`filter`
control in the same image returns 128. A red|blue seam test
([`pages/split.html`](../../../spikes/s1-proxy-topology/pages/split.html)) in
WKWebView leaves the seam at pure `rgb(0,0,255)` under `backdrop-filter:
blur(10px)` while the CSS-`filter` control smears it to `rgb(122,0,133)`.

**Most likely cause, and why it is not a finding about those engines.** In both
Gecko and WebKit, `backdrop-filter` is applied in the accelerated-compositing
pass, and the automation snapshot paths used here appear to rasterise the display
list without that pass. Independent WPT data (Chrome 152 / Firefox 154 /
Safari 26.6 stable runs) shows Firefox and Safari *passing* many
`backdrop-filter` reftests, and WPT captures through a widget-layer path rather
than these snapshot APIs. `-webkit-backdrop-filter` has shipped since Safari 9
and is in wide production use. So the correct conclusion is **"this environment
cannot measure it"**, not "these engines do not do it".

**Real Safari 26 could not be driven at all.** `safaridriver` is present and
binds its port, but `POST /session` hangs indefinitely: Remote Automation is not
enabled, which needs an authenticated `safaridriver --enable` plus Safari's
*Develop → Allow Remote Automation*. `screencapture` also fails
(`could not create image from rect`) because the terminal lacks Screen Recording
permission. Both are admin/GUI actions.

**What is needed to close the gate.** Cheapest first:

1. **Open [`spikes/s1-proxy-topology/pages/manual-check.html`](../../../spikes/s1-proxy-topology/pages/manual-check.html)
   directly in real Safari 26 and real Firefox** and answer its eleven amber
   questions. It is built for this: every test that can be reduced to a
   human-reliable judgement is, and the two quantitative ones (double filtering,
   canvas compositing) are self-scoring — the answer is "does this band match
   swatch ONE or swatch TWO", with the swatches painted at the exact predicted
   values. Open it as a local file, not in an iframe or a preview pane: an
   enclosing compositing layer can change the very thing being measured.

   The page was validated against Chromium first, where it **reproduces this
   spike's automated results by eye**: its section D grid shows exactly the seven
   re-rooting styles and six harmless ones that the numeric Q5 table below
   records, and its section B overlap band visibly lands on the "applied twice"
   swatch. That is what makes a human's answers from it directly comparable to
   the Chromium column, rather than a vague impression.
2. Or grant **Screen Recording** permission to the terminal, which makes
   `screencapture` work and lets the harness be re-pointed at a real browser
   window.
3. Or run `sudo safaridriver --enable` and enable *Allow Remote Automation*,
   which would let the existing
   [`harness/bidi.mjs`](../../../spikes/s1-proxy-topology/harness/bidi.mjs)
   WebDriver-BiDi client drive real Safari — though its screenshots may well go
   through the same non-compositing path, so this is the least certain option.

Until then, every Chromium finding below should be read as **provisionally
cross-engine**, with the Filter Effects 2 normative text (cited inline) as the
reason to expect it to generalise, and the WPT stable-run data as the reason to
expect the two known per-engine deviations noted in §Impact.

---

## Q1 — Sampling equivalence

**Answer: the portaled masked proxy is not pixel-identical to in-place
`backdrop-filter`, and the difference is desirable. It is confined to a band the
width of the blur, it exists because in-place filtering starves the blur at the
element's own edge, and the padded proxy is the more physically correct of the
two.**

### The proxy is identical to in-place everywhere except an edge band

Headless Chromium, `blur(20px) saturate(1.8)`, mixed background:

| comparison | A_interior | A_edge | GAP | OUTSIDE_LEFT |
| --- | --- | --- | --- | --- |
| in-place vs proxy `pad=0` | 0.33 / 9 | 1.84 / 18 | 0 / 0 | 0 / 0 |
| in-place vs proxy `pad=20` | 0.89 / 9 | 5.38 / 22 | 0 / 0 | 0 / 0 |
| in-place vs proxy `pad=60` | 0.90 / 9 | 5.40 / 21 | 0 / 0 | 0 / 0 |
| in-place vs proxy `pad=full` | 0.90 / 9 | 5.40 / 21 | 0 / 0 | 0 / 0 |

(`mean / max`.) Background outside the shapes is **byte-identical** in every
case — the proxy never leaks. The interior is effectively identical (0.01% of
pixels exceed 8/255, and those sit just inside the 26px inset, within blur reach
of the boundary). All of the difference is in the edge ring: mean 5.4, max 21,
with 27.5% of ring pixels above 8/255. Heatmap:
`shots/chromium/heat/inplace__vs__proxy-padfull.png`.

### Why: the filter input is normatively clipped to the filtered element's own border box

This is not an engine bug. [Filter Effects 2 §3](https://drafts.csswg.org/filter-effects-2/#BackdropRoot)
builds the Backdrop Root Image by painting everything below the element and then
"clip[ping] the final painted output to this border quad", and §2.1 adds that a
`blur()` in the list "will be applied with `edgeMode="mirror"`, with the edge
defined by the clipped, transformed border box of the element."

So a shape-sized filtered element blurs *only the pixels inside the shape*,
mirroring at its own boundary. Native Liquid Glass does no such thing — it
samples the real backdrop beyond the shape. Making the proxy box larger than the
shape and clipping the *result* to the shape is precisely how the DOM tier
recovers the unclamped sampling the GPU tier gets for free. The padding is not an
optimisation knob; it is the mechanism.

That reframes "equivalence": the right reference is not in-place filtering but
the un-starved proxy, and the measurement that matters is how much padding is
needed to reach it.

### How much padding: exactly 3σ, verified at three blur radii

CSS `blur(<length>)` takes the Gaussian standard deviation directly —
[Filter Effects 1](https://drafts.csswg.org/filter-effects-1/) says "the passed
parameter defines the value of the standard deviation to the Gaussian function"
and warns that "standard deviation is different to `box-shadow`'s blur radius".
So `blur(20px)` means σ = 20px, and padding can be expressed in multiples of σ.

Distance from `pad=full` (a viewport-sized proxy, which cannot be starved),
headless Chromium, A_edge `mean / max`, at three radii:

| proxy padding | blur(8px) | blur(20px) | blur(40px) |
| --- | --- | --- | --- |
| 0σ | 3.37 / 55 | 4.00 / 21 | 2.67 / 6 |
| 0.5σ | 1.29 / 21 | 3.33 / 26 | 1.74 / 5 |
| 1σ | 0.60 / 15 | 0.82 / 6 | 1.63 / 6 |
| 1.5σ | 0.18 / 6 | 0.64 / 8 | 0.13 / 3 |
| 2σ | 0.02 / 2 | 0.18 / 3 | 0.04 / 3 |
| 2.5σ | 0.00 / 2 | 0.01 / 2 | 0.00 / 0 |
| **3σ** | **0 / 0** | **0 / 0** | **0 / 0** |
| 4σ | 0 / 0 | 0 / 0 | 0 / 0 |

**`samplingPadding ≥ 3σ` is byte-exact at every radius tested; `≥ 2σ` is within
0.2/255 mean and 3/255 max.** Three radii spanning 5× is what makes this a rule
rather than a number fitted to one blur — and 3σ is the standard Gaussian kernel
truncation, which is why it lands exactly. Retail Chrome agrees at the endpoints
(3σ and 4σ byte-identical to `pad=full`); its intermediate rows are GPU-raster
noise. This number is the spike's most directly usable output, and the parent
spec currently does not carry it.

One counterintuitive detail from the same sweep: the in-place clamping artifact is
**worst for small blurs**, not large ones. In-place versus `pad=full` gives
A_edge max 66/255 at `blur(8px)`, 21/255 at `blur(20px)`, and 18/255 at
`blur(40px)`. A small σ preserves high-frequency detail right up to the shape
boundary, so mirroring at that boundary is badly wrong; a large σ has already
smoothed everything, so the mirror is nearly right. Tight-blur materials are
therefore the ones that most need the padded proxy.

Background-independent: `pad=full` vs `pad=3σ` is `0 / 0` on the checkerboard, on
the raster image, and on the gradient alike. The in-place-versus-proxy edge delta
does vary with backdrop content (checkerboard 1.20, gradient 1.03, raster image
5.01) — as expected, since starving the blur only matters where the content near
the boundary is busy.

### Masking mechanism does not matter; masking extent matters a great deal

| comparison | result |
| --- | --- |
| `clip-path: path(...)` vs equivalent SVG `mask-image` | A_edge 0.01 / 4 — equivalent |
| `clip-path: path(...)` vs `border-radius` + `overflow: hidden` wrapper | A_edge 0.03 / 18 — equivalent |
| mask = shape union vs **mask = padded box** | GAP **102.92 / 137**, OUTSIDE_LEFT **102.31 / 138** |

The last row is the important one. Masking the proxy to *shape + padding* rather
than to the shapes leaves a full-strength blurred rectangle standing proud of the
glass — a 40% halo, not a subtlety. Heatmap:
`shots/chromium/heat/proxy-padfull__vs__proxy-pad60.png` for the convergence
case; the halo case is visible directly in `shots/chromium/proxy-clippadded.png`.
The parent spec's X1 wording is ambiguous on exactly this point (§Impact, item 1).

### Hit-testing and focus survive the sandwich, in all three engines

Measured by [`harness/extras.mjs`](../../../spikes/s1-proxy-topology/harness/extras.mjs)
— and this part is valid for all three engines, because it does not depend on the
filter rendering. At the panel centre, `document.elementFromPoint` returns
`BUTTON.glass-host` in Chromium, Firefox and WebKit; `elementsFromPoint` shows
neither proxy nor canvas in the stack; a synthetic click at that point is
received by the button; the proxy's computed `pointer-events` is `none`.
Keyboard `Tab` lands on the button in Chromium and Firefox and on `BODY` in
WebKit — the latter is WebKit's default "Tab moves focus to form controls only"
preference, not a property of the sandwich.

---

## Q2 — Double filtering

**Answer: yes, sibling proxies chain. A later-painted proxy samples an
earlier-painted proxy's already-filtered output. Paint order therefore matters,
and the contract needs an invariant that keeps the effect out of visible glass —
the current `samplingPadding` rule does not, on its own, provide one.**

### The mechanism, by exact arithmetic

Flat `#3a5a80` = `rgb(58,90,128)`, filter `brightness(1.25)`, no blur, so the
prediction is exact. Two panels whose masks deliberately **overlap** (a
configuration the parent spec forbids — used here only to isolate the mechanism):

| variant | A only | overlap | B only |
| --- | --- | --- | --- |
| no filter | 58,90,128 | 58,90,128 | 58,90,128 |
| one proxy over the whole strip | 72,112,160 | **72,112,160** | 72,112,160 |
| two overlapping proxies, order A→B | 72,112,160 | **90,140,200** | 72,112,160 |
| two overlapping proxies, order B→A | 72,112,160 | **90,140,200** | 72,112,160 |
| two overlapping *in-place* hosts | 72,112,160 | **90,140,200** | 72,112,160 |

`58 × 1.25 = 72.5`; `58 × 1.25² = 58 × 1.5625 = 90.6`. The overlap is filtered
exactly twice. Retail Chrome returns `73,113,160` / `91,141,200` — the same
result at rounding. In-place hosts behave identically, so this is generic
`backdrop-filter` sibling semantics, not something the proxy topology introduces.

This matches [Filter Effects 2 §2.1](https://drafts.csswg.org/filter-effects-2/#backdrop-filter-operation),
whose final step composites a backdrop-filtered element's finished output into its
parent, and §3, which then paints "all content, in painting order" into the next
element's backdrop image. An element with `backdrop-filter` is a Backdrop Root
only for its *descendants*. Siblings chain by construction.

**This makes the parent spec's same-plane no-overlap rule load-bearing for a
second, independent reason.** It is currently justified by z-order (the sandwich
cannot put one surface's body above another's DOM label). It is *also* required
to prevent exact double application of the material's own filter.

### The legal geometry still leaks, and the leak is order-dependent

With non-overlapping shapes but generous padding, each proxy's *box* covers a
slab of the other group's *masked region*, so the later proxy blurs the earlier
proxy's output and spreads it inward. Measured against a single-group proxy over
both shapes (which by construction cannot chain), `blur(20px) saturate(1.8)`,
headless Chromium:

| group gap | padding | A_inner (gap-facing band) | B_inner (gap-facing band) |
| --- | --- | --- | --- |
| 40px | 60px, order A→B | 0.03 / 18 | 0.05 / 18 |
| 40px | 60px, order B→A | 0.04 / 18 | 0.02 / 18 |
| **8px** | 60px, order A→B | 0.01 / 18 | **1.01 / 17** |
| **8px** | 60px, order B→A | **0.49 / 18** | 0.01 / 17 |
| 8px | 60px, `brightness` only | 0 / 4 | **1.64 / 9** |

The signature is unambiguous: **the later-painted proxy is the contaminated one**,
and swapping the order swaps which band is affected. At a 40px gap the leak is
Gaussian-tail noise. At an 8px gap it is mean ~1/255 with peaks of 17/255 (6.7%)
across a 54px band — borderline perceptible on a smooth backdrop, and it grows as
groups get closer or padding grows. Heatmaps:
`shots/chromium/heat/near-single__vs__near-split-ab.png`,
`.../near-split-ab__vs__near-split-ba.png`,
`.../nearb-single__vs__nearb-split-ab.png`.

Paint order alone (A→B versus B→A, same geometry) shifts the gap-facing bands by
mean 0.49 / 1.00 with max 3 and 7 — i.e. **paint order is observable**, which for
a fidelity-first library means group ordering must be deterministic, not
incidental.

The fix is an invariant, not a smaller padding: see §Impact item 3.

---

## Q3 — Robustness

All rows are headless Chromium unless noted. Where the in-place reference had to
stay put (scroll, zoom), it is a `position: fixed` host with the filter on itself
— comparing a scrolling in-place host against a fixed-plane proxy measures the
host scrolling away, not sampling, and that confound invalidated the first run of
this section.

| Scenario | Comparison | A_interior | A_edge | Verdict |
| --- | --- | --- | --- | --- |
| **Page scroll** (400px) | fixed in-place host vs proxy `pad=60` | 0.26 / 3 | 1.97 / 10 | **tracks correctly** — smaller than the no-scroll edge delta |
| **`position: fixed` content behind the glass** | in-place host vs proxy `pad=full`, no scroll | 0.90 / 9 | 5.40 / 21 | **sampled correctly** — identical to the no-fixed-content case (and to the fixed-host reference, since `Q3s` shows host positioning is irrelevant without scroll) |
| **`position: fixed` content + scroll** | fixed host vs proxy `pad=full` | 0.26 / 3 | 1.97 / 10 | **correct** |
| **`transform: translate3d` on an ancestor of the backdrop content** | transformed proxy vs untransformed proxy | **0 / 0** | **0 / 0** | **byte-identical — transform does not re-root the backdrop** |
| **`transform: translate3d` on a common ancestor of content and plane root** | transformed proxy vs untransformed proxy | **0 / 0** | **0 / 0** | **byte-identical** |
| **CSS `zoom: 1.5`** on the document | in-place vs proxy `pad=full`, whole capture | 0.07 / 12 | — | **correct** |
| **`devicePixelRatio` 2** | in-place vs proxy `pad=60` | 1.73 / 19 | 14.4 / 73 | **correct** — the same edge-clamp delta, scaled by 2 |
| **`overflow: auto` scroller under the glass** | proxy `pad=full` vs proxy `pad=60` | **0 / 0** | **0 / 0** | **no scroller-specific effect** |
| **`overflow: auto` scroller under the glass** | proxy `pad=full` vs proxy `pad=0` | 4.59 / 28 | 23.42 / 77 | edge-clamping, **amplified** by the scroller's hard edges (A_edge mean 4.00 → 23.42, max 21 → 77 versus the no-scroller scene) |
| **Scrolling the inner scroller** (300px) | fixed host vs proxy `pad=full` | 2.99 / 21 | 17.99 / 57 | **tracks correctly**, same clamp signature |
| Static vs `position: fixed` in-place host, with scroller | — | **0 / 0** | **0 / 0** | host positioning is irrelevant to sampling |

The transform result is worth stating plainly, because the folklore says
otherwise: **an ancestor `transform`, including a 3D-promoting `translate3d`, does
not break the proxy's backdrop sampling in Chromium** — the two images are
byte-identical to the untransformed case. Filter Effects 2 agrees explicitly:
its Backdrop Root definition notes that "a Backdrop Root is not formed by
elements with `z-index` applied, fixed or sticky-positioned elements, and elements
with transforms applied."

What this spike did *not* exercise is a genuine 3D rendering context — an ancestor
with `perspective` or `preserve-3d`, which flattens differently and is a
different case from a 3D transform *function* like `translate3d`. That case has a
documented history of breaking `backdrop-filter` (WebKit bugs 252181 and 201987,
Gecko bug 1816561, all open), and the WPT stable runs show
`backdrop-filter-nested-3d-transform-perspective.html` failing in Firefox 154
while Chrome and Safari pass. It remains a live per-engine hazard and belongs in
C5's test matrix even though the plain-transform case is clean.

The scroll-container row deserves emphasis for the opposite reason. A scroller
under the glass does not break anything, but it puts hard high-contrast
boundaries right under the shape edge, and that is exactly where a starved blur
goes wrong: `pad=0` is off by up to 78/255 there. It is the strongest single
argument for the padding rule.

### One real hazard: large proxies silently lose the filter under software rasterisation

Discovered as an anomaly and worth carrying forward. Comparing each variant
against the *unfiltered* scene — where `0 / 0` means the filter did nothing at all:

| build | DPR | proxy padding | proxy box (device px) | vs unfiltered |
| --- | --- | --- | --- | --- |
| headless Chromium | 1 | full | 1000×800 = 0.8 Mpx | 97.77 — filtered |
| headless Chromium | 2 | 60 | 1120×480 = 0.54 Mpx | 97.78 — filtered |
| headless Chromium | 2 | 200 | 1680×1040 = 1.75 Mpx | 97.88 — filtered |
| headless Chromium | 2 | 300 | 2080×1440 = 3.00 Mpx | **0 — filter dropped** |
| headless Chromium | 2 | full | 2000×1600 = 3.20 Mpx | **0 — filter dropped** |
| headless Chromium | 3 | 60 | 1680×720 = 1.21 Mpx | 97.78 — filtered |
| headless Chromium | 3 | full | 3000×2400 = 7.20 Mpx | **0 — filter dropped** |
| **retail Chrome** | 1, 2 and 3 | 60 … full | up to 7.20 Mpx | 97.58 at every size — **never dropped** |

So this is a **software-rasterisation size limit, not a Chrome behaviour** — the
threshold sits somewhere between 1.75 and 3.0 megapixels of proxy area in device
pixels, and GPU-composited retail Chrome has no such ceiling. It matters anyway,
for two reasons. It is the exact configuration C5's Playwright CI will run in, so
a viewport-sized proxy would produce phantom failures there; and it fails
*silently*, which is the worst mode. See §Impact item 6.

CDP layer-tree introspection returned no layers in headless Chromium, so
"does each proxy get its own composited layer" is **unmeasured**; it needs a
GPU-composited retail Chrome session with `LayerTree` enabled.

---

## Q4 — Canvas interaction

**Answer: within a plane, no. The transparent optics and highlight canvases
painted above the proxy are never included in the proxy's backdrop sampling —
confirmed by exact arithmetic, not by eye. Across planes, yes, necessarily: an
overlay-plane proxy samples the base plane's canvases and host DOM.**

### Within a plane: exact source-over, no re-sampling

If the proxy had sampled the canvas above it, the result would not equal plain
source-over compositing. It does, to the byte. Optics tint `rgba(255,255,255,
0.28)` plus a highlight gradient reaching `α ≈ 0.175` at the sample point:

| sample | proxy, canvases empty | proxy + canvases | predicted plain source-over |
| --- | --- | --- | --- |
| inside shape A (tint + highlight) | `137,119,120` | `185,174,174` | `185,174,174` ✓ |
| inside shape B (tint only) | `123,136,117` | `160,169,155` | `160,169,156` ✓ |
| unfiltered control, shape A | `174,108,108` | `207,167,167` | `207,167,167` ✓ |

Heatmap: `shots/chromium/heat/canvas-off-padfull__vs__canvas-on-padfull.png` —
the difference is exactly the tinted shapes and nothing else; `OUTSIDE_LEFT` is
`0 / 0`. The sandwich's ordering guarantee holds.

### Across planes: the overlay proxy re-filters the base plane's glass

Adding the overlay plane changes the base panel's pixels (A_interior mean 26.74,
max 30) and blurs the inter-shape gap that the base plane leaves untouched (GAP
mean 50.36, max 142). Heatmap:
`shots/chromium/heat/overlay-base-only__vs__overlay-on.png`.

This follows necessarily from paint order plus the Q2 result, and is not
avoidable within the plane model: the base plane's optics canvas, semantic host
DOM and highlight canvas are all painted before the overlay plane, so they are in
the overlay proxy's backdrop image. It may well be *desirable* — native Liquid
Glass menus do blur the toolbar beneath them — but it means an overlay's material
is calibrated against a **glassed** backdrop, and the base tint gets blurred and
then re-tinted. The spec should say so deliberately (§Impact item 4).

Caveat on this one number: the prototype's optics painter draws the base shapes
on *both* planes' canvases, so the magnitudes above overstate a real overlay.
The qualitative conclusion rests on paint order and the Q2 arithmetic, not on
these two figures.

### Scroll cadence: no measurable cost, and a weak measurement

Ninety `requestAnimationFrame` deltas during a programmatic scroll, with and
without the whole glass root:

| build | with glass (mean / p50 / p95 / >20ms) | without glass |
| --- | --- | --- |
| headless Chromium | 11.76 / 10.2 / 27.0 / 5 of 88 | 12.27 / 10.9 / 27.2 / 6 of 88 |
| retail Chrome | 12.02 / 10.5 / 27.2 / 6 of 88 | 11.81 / 10.3 / 25.3 / 5 of 88 |

Indistinguishable — the sandwich costs nothing measurable here, and no flicker or
tearing appeared in mid-scroll captures. **Treat this as near-zero evidence about
real 60fps behaviour.** Headless rAF cadence is not vsync, software rasterisation
is not the GPU compositor, and the very effect under test is the one this
environment renders differently. Frame-time and layer-promotion behaviour under
scroll needs a real GPU session; it should be a C5 or C6 measurement, not an S1
claim.

---

## Q5 — The conformance probe

**Answer: no pixel oracle exists, in any engine, by any interoperable means. The
honest probe is a three-layer construction — a support gate, a deterministic
structural audit of the backdrop-root chain, and a CI-generated engine
conformance table — and it leaves one whole failure class undetectable, which the
spec should say out loud.**

Everything in this section was measured in **all three engines**, because the
probe battery ([`pages/probe.html`](../../../spikes/s1-proxy-topology/pages/probe.html))
does not depend on `backdrop-filter` rendering.

### What is not detectable — four negative results, all measured

**1. `CSS.supports` is not a conformance signal.** It returns `true` for
`backdrop-filter: blur(1px)` in *all three engines*, including the two builds that
render nothing at all. Worse for the parent spec's reserved displacement seam
(Decision Log #11): `CSS.supports('backdrop-filter', 'url(#x)')` and
`...('backdrop-filter', 'blur(1px) url(#x)')` are **`true` in all three engines**,
although only Chromium renders reference filters inside `backdrop-filter`
(WebKit bug 245510; Gecko bug 1887451). `CSS.supports` cannot distinguish the
displacement tier either.

**2. Computed-style readback carries no capability information.** All three
engines round-trip `backdrop-filter: url(#nope)` and
`blur(8px) url(#nope)` through `getComputedStyle` unchanged. Only a
*syntactically invalid* function (`bogusfn(3)`) drops the declaration, and that
happens identically in all three. Filter Effects 2 specifies
`Computed value: as specified`, and WPT's
`backdrop-filter-computed.html` asserts exactly this case and passes everywhere.
The "engines drop what they can't render" idea is simply false — **this probe
avenue is closed.**

**3. The offscreen reference construction works, and cannot see
`backdrop-filter`.** An SVG data URI containing a `foreignObject`, loaded as an
`<img>` and drawn into a canvas, rasterises correctly and leaves the canvas
**origin-clean in all three engines** — so `getImageData` succeeds. And CSS
`filter` *does* render through it: a red|blue seam under `filter: blur(8px)`
reads `121,0,134` instead of `0,0,255`, identically in Chromium, Firefox and
WebKit. But `backdrop-filter` never applies inside it: the blur variant leaves
the seam at `0,0,255`, `brightness(2)` over `#404040` stays at 64, and a
`clip-path`ed variant is unchanged — in **all three engines**. The reason is
structural rather than a bug: an SVG loaded as an image is a separate document
whose own root is a Backdrop Root, so the host page's pixels are not in the
document being rasterised. The construction is still worth keeping as a
*positive control* that the engine's blur math and the canvas readback path
function; it can never be a backdrop-sampling oracle.

**4. Every other readback path is closed by design.** View Transitions snapshots
are specified unreadable by script; Houdini's `PaintRenderingContext2D`
deliberately omits `getImageData`; `getDisplayMedia` (and therefore Element and
Region Capture, which are defined on top of it) requires transient activation and
a permission prompt, which disqualifies it from a startup probe on both UX and
privacy grounds. One genuine exception exists and is Chromium-only: HTML-in-Canvas
`drawElementImage()` defines "read-back-allowed rendering" and gained explicit
`backdrop-filter` support in April 2026, but it is flag- and origin-trial-gated
(Chrome 148–150), so it can only ever be an optional single-engine confirmation.

### What *is* detectable: the backdrop-root chain, and it matches the spec exactly

This is where a probe earns its place. The dominant real-world failure is not an
engine defect — it is application CSS putting a backdrop-root-forming style on an
ancestor of the plane root, which silently re-roots the proxy's backdrop so the
filter sees nothing. That *is* statically detectable from computed styles.

Ground truth was measured by putting exactly one candidate style on the GlassRoot
element — an ancestor of the proxy but **not** of the backdrop content — and
diffing against both the clean case and the unfiltered scene. `0` against
"unfiltered" means the filter saw nothing:

| style on GlassRoot | vs clean | vs unfiltered | verdict |
| --- | --- | --- | --- |
| *(none)* | 0 | 97.77 | control — filtered |
| `opacity: 0.99` | 97.77 | **0** | **re-roots** |
| `filter: none` | 0 | 97.77 | harmless |
| `filter: blur(0px)` | 97.77 | **0** | **re-roots** |
| `filter: grayscale(0)` | 97.77 | **0** | **re-roots** |
| `mask-image: linear-gradient(#000,#000)` | 97.77 | **0** | **re-roots** |
| `clip-path: inset(0)` | 97.77 | **0** | **re-roots** |
| `mix-blend-mode: multiply` | 97.77 | **0** | **re-roots** |
| `will-change: opacity` | 97.77 | **0** | **re-roots** |
| `contain: paint` | 0 | 97.77 | harmless |
| `isolation: isolate` | 0 | 97.77 | harmless |
| `will-change: transform` | 0 | 97.77 | harmless |
| `transform: translate3d(0,0,0)` | 0 | 97.77 | harmless |

Retail Chrome reproduces every row (97.58 / 0). Note that `filter: blur(0px)` and
`filter: grayscale(0)` — visually no-ops that real application CSS emits all the
time, e.g. as animation start states — break the topology just as thoroughly as
`opacity: 0.5`.

This is *exactly* [Filter Effects 2's normative trigger list](https://drafts.csswg.org/filter-effects-2/#BackdropRoot):
root element, `filter` other than `none`, `opacity` below 1, `mask` / `mask-image`
/ `mask-border` / `clip-path` other than `none`, `backdrop-filter` other than
`none`, `mix-blend-mode` other than `normal`, and `will-change` naming any of
those. The measurements also settle two things the spec text does not: `contain`
is **not** a trigger (the spec is silent and no WPT test covers it), and
`isolation: isolate` is **not** one (matching
`backdrop-filter-isolation-isolate.html`, which passes in all three engines).

### The audit was prototyped and scored against that ground truth

`probe.html` implements the walk (`auditChain`) with the *intuitive* property list
— the one a developer would write from memory — and runs it against the same
thirteen fixtures. Scored against the measured column above: **11 of 13 correct,
0 false negatives, 2 false positives.** The two it got wrong were `contain: paint`
and `isolation: isolate`, both of which "look like" isolation boundaries and
neither of which re-roots the backdrop.

That is the useful result. The failure mode of a hand-written list is
over-triggering, which demotes working groups; and it is fixed by pinning the list
to Filter Effects 2's normative triggers and nothing more. The measurements are
what license dropping those two entries — without them, dropping `contain` would
have been a guess, since the spec never mentions it and no WPT test covers it.

The one caveat to carry: the spec's own text says this section "does not yet have
Working Group consensus, specifically on the definition of Backdrop Root"
([fxtf-drafts#53](https://github.com/w3c/fxtf-drafts/issues/53), open since 2016),
and the WPT stable runs bear that out — `backdrop-filter-backdrop-root-mask.html`
**fails in Firefox 154 and Safari 26.6**, and
`backdrop-filter-backdrop-root-clip-path-2.html` fails in Safari 26.6. So on
those engines an ancestor `mask` may *not* re-root, and a probe that flags it
would demote a group that would actually have worked. That is the safe direction
to be wrong in, and it is worth revisiting per engine once §Environmental blocker
is closed.

### Proposed probe

Three layers, each with an explicitly stated reach — the reach matters as much as
the verdict, because two of the three layers cannot see what they would most like
to check.

**Layer 1 — support gate.** `CSS.supports('backdrop-filter', 'blur(1px)') ||
CSS.supports('-webkit-backdrop-filter', 'blur(1px)')`. Cheap, and catches only
the total absence of the property. Note that WebKit reports `true` for the
prefixed form and Chromium/Gecko report `false` for it while reporting `true`
unprefixed, so both must be tested and both must be emitted in CSS. Failure →
demote with `no-backdrop-filter`.

**Layer 2 — structural backdrop-root audit.** The load-bearing layer. For each
sampling group, walk from every member host element and from the group's proxy up
to their lowest common ancestor, and assert that no element on the shared segment
carries a trigger from the list above (with the two spec-silent exclusions,
`contain` and `isolation`, deliberately *not* flagged, per the measurements).
Deterministic, synchronous, allocation-light, and it catches the failure mode
that will actually happen in the field. Failure → demote that group with
`probe-failed`, naming the offending element and property in the dev-mode
message; that message is most of the value, because the fix is one CSS line in
the host app.

Two design requirements follow from what was measured. It must run at
**registration time and again whenever the audited chain's computed styles
change** — the inputs are application CSS, which mutates at runtime (hover
states, animations, theme switches), so a startup-only probe is not enough. And
it must be **per group**, not per document, because different groups can sit
under different ancestors.

*Reach:* catches app-induced re-rooting. Does not see engine behaviour at all.
Over-triggers on engines that do not implement `mask`/`clip-path` as triggers —
which is fail-safe, and which the CI table below can eventually relax per engine.

**Layer 3 — engine conformance table, generated in CI.** A committed matrix keyed
by engine family plus version range, recording only the properties that cannot be
measured at runtime: does the engine rasterise `backdrop-filter` at all; edge
mode; reference-filter (`url()`) support; the proxy-area limit; the 3D-transform
hazard. Runtime picks a row from engine detection and **must fail closed** — an
unrecognised engine gets the conservative row. The table must be *generated by
this spike's own harness in CI*, not hand-maintained, or it will rot; the harness
already emits `shots/report.json` in the right shape to become that artefact.

*Reach:* covers known-version behaviour. Cannot cover an unknown version, and —
the important gap — cannot cover a **per-environment condition** that suppresses
`backdrop-filter` on an engine and version that otherwise supports it: a
blocklisted GPU, forced software rasterisation, a reduced-transparency
accessibility setting, a remote-desktop or screen-sharing pipeline.

**This machine is a live instance of that class.** Firefox 154 and WebKit 26.5
here report full support through every JS-observable channel — `CSS.supports`
true, computed style intact, no error, no warning — and deliver no filter into the
output actually consumed. Whatever the specific cause, it is invisible from inside
the page, which is the whole point: the class is not hypothetical, and a probe
cannot close it.

**What follows from the undetectable class.** Because no probe can catch "the
engine renders nothing", vitrea cannot promise that a demoted group is always
correctly identified. Two consequences the spec should adopt: the CSS tier must
be presentable enough that a *missed* demotion is a fidelity loss and not a
broken UI (a group whose filter silently no-ops must still read as a legible
surface — which argues for the optics canvas always painting a real tint and rim
rather than relying on the blur for contrast); and `useGlassCapabilities()`
should surface the probe's *reach*, not just its verdict, so an app can tell
"probed and passed" from "not probeable here".

---

## Impact on C5 and X1/X2 — proposed contract adjustments

Proposals only. The parent spec is not edited by this child; these are for the
parent to accept, modify, or reject.

**1 — X1: disambiguate the mask extent.** Current text reads "ONE
`pointer-events:none` proxy per sampling group, masked to the union of member
shapes + `samplingPadding`". Read literally that produces a 40%-strength blurred
halo standing proud of the glass (GAP mean 102.92/255, measured). Proposed
wording: *the proxy's **box** is the union of member shapes inflated by
`samplingPadding`; its **mask** is the shape union only. The padding is a bleed
region that is never painted.*

**2 — X1: add the padding rule and its reason.** **`samplingPadding ≥ 3σ`**,
where σ is the `blur()` length (Filter Effects 1: the parameter *is* the standard
deviation). Byte-exact at `blur(8px)`, `blur(20px)` and `blur(40px)`; `≥ 2σ` is
within 0.2/255 mean, 3/255 max. State the mechanism alongside it, because it
explains why the padding is not optional:
Filter Effects 2 clips the filter *input* to the filtered element's own border box
with `edgeMode="mirror"`, so a shape-sized proxy starves the blur at the shape
edge, and inflating the box is exactly how the DOM tier recovers the unclamped
sampling the GPU tier gets for free. This also means **the DOM tier is not
"in-place `backdrop-filter`, portaled"** — it is deliberately different from
in-place filtering, and closer to native, at the shape boundary. Worth saying,
since a reviewer would otherwise read the Q1 edge delta as a defect.

**3 — X1: add a group-separation invariant.** Sibling proxies chain exactly
(1.25² measured), and in the *legal* geometry the later-painted proxy's
gap-facing band is contaminated by up to 17/255 when two groups sit 8px apart
with 60px padding. Proposed invariant: **`mergeDistance ≥ samplingPadding`** —
equivalently, two groups whose padded boxes intrude on each other's shape region
must be merged into one group. The spec already carries `mergeDistance` on
`GlassGroup`; this ties the two knobs together instead of leaving them
independent. Add also: **proxy paint order within a plane must be deterministic**
(order alone shifts pixels by mean 0.5–1.0, max 7), so group ordering is part of
the contract, not an artefact of insertion order.

**4 — X1: state the cross-plane sampling consequence.** An overlay-plane proxy
necessarily samples the base plane's optics canvas, semantic host DOM and
highlight canvas — this follows from paint order and is not avoidable in the
plane model. Decide it deliberately (it resembles native behaviour, where a menu
blurs the toolbar beneath it) and record the consequence: **an overlay's material
parameters calibrate against a glassed backdrop, not a raw one**, and the base
tint is blurred and then re-tinted. This is a C7 calibration input as well as an
X1 clarification.

**5 — X1: give the same-plane no-overlap rule its second justification.** It is
currently justified by z-order alone. It is also required to prevent exact double
application of the material's filter (measured: `1.25² = 1.5625`, in both proxy
and in-place form). Recording both reasons makes the rule much harder to
"optimise away" later.

**6 — X1 / C5: bound proxy area, and make a dropped filter fail loudly.**
Headless Chromium silently drops `backdrop-filter` when the proxy exceeds roughly
1.75–3.0 megapixels of device-pixel area; retail Chrome never does. Two
proposals: cap proxy area (which the `mergeDistance`/`samplingPadding` invariant
mostly achieves anyway, and which argues against ever using a viewport-sized
proxy); and add a CI assertion that a padded proxy differs from the unfiltered
scene, so a silent drop fails the suite instead of quietly changing the baselines.

**7 — X2: make `probe-failed` re-enterable.** §rendering contract says "a runtime
conformance probe validates the proxy topology **at startup**". The structural
audit's inputs are application CSS, which changes at runtime, so a startup-only
probe under-detects. Proposed: the probe runs at group registration and again when
the audited ancestor chain's computed styles change, with a named recovery
transition when the offending style is removed. `probe-failed` stays the demotion
reason; only its lifecycle changes.

**8 — C5 acceptance: narrow the Playwright pixel claim.** C5's acceptance says
"Playwright integration suite (all engines runnable locally)". For
`backdrop-filter` **pixels** that is not achievable: Gecko and WebKit render it as
a no-op in every capture path tested here, so any pixel assertion on the DOM tier
in those engines would be asserting the wrong thing. Proposed split: pixel
assertions on the DOM tier are **Chromium-only**; Firefox and WebKit get
non-pixel assertions plus the committed `manual-check.html` as a release-time
human gate. The non-pixel surface is genuinely testable everywhere — this spike
verified hit-testing, `elementFromPoint`/`elementsFromPoint` stacking, click
delivery, focus, the `CSS.supports` and computed-style probe battery, the
offscreen-construction control, and the backdrop-root audit walk in all three
engines. What cannot be asserted there is any statement about filtered pixels.
This is a real change to a child's acceptance criteria and needs the parent's
agreement.

**9 — X1 / risk register: the per-engine promise is still open.** The parent's
risk entry reads "S1 partially fails on an engine → the arbitrary-DOM promise
narrows there". Neither outcome applies to Gecko or WebKit yet: this spike could
neither confirm nor narrow them. Proposed status: **S1 confirmed for Chromium;
Gecko and WebKit blocked on one human action** (§Environmental blocker), with
C5 free to start — its Chromium path, its structural probe and its CSS tier are
all fully specified by these findings, and the two open engines affect only
whether their `dom` groups keep `samplingBackend: "css-backdrop"` or fall to the
CSS tier. That is a per-engine table entry in the Layer-3 conformance artefact,
not an API change — exactly as the parent's risk entry anticipated.

**10 — Decision Log candidate.** Suggested entry: *proxy topology confirmed on
Chromium with four amendments (mask extent, padding rule, `mergeDistance ≥
samplingPadding`, deterministic paint order); sibling proxies provably chain, so
the no-overlap rule and the separation invariant are both load-bearing; no
runtime pixel oracle for `backdrop-filter` exists in any engine, so the
conformance probe is structural plus a CI-generated engine table, with
per-user/GPU disablement acknowledged as undetectable; Gecko and WebKit remain
unmeasured pending a human-driven check.*

---

## Reproducing

```bash
cd spikes/s1-proxy-topology
npm install
node harness/gen-noise.mjs                 # deterministic backdrop raster
node harness/engine-check.mjs              # does this build rasterise backdrop-filter?
node harness/run.mjs                       # all four builds: matrix + probe battery
node harness/extras.mjs                    # hit-testing, layers, page zoom
```

`harness/run.mjs` with no arguments runs `chromium`, `chrome`, `firefox` and
`webkit`. The `firefox` and `webkit` rows are retained for their *probe battery*
and their structural results, which are valid; **no pixel conclusion should be
read out of them** — every filtered variant there equals the unfiltered one, so
their diffs are zeros that mean "not measured", not "identical".
`harness/bidi.mjs` (WebDriver BiDi) and `harness/wksnap.swift`
(`swiftc -O -o wksnap harness/wksnap.swift`) drive retail Firefox and the system
WKWebView respectively — both were used to establish §Environmental blocker and
both remain available if the environment changes.

### Evidence index

Committed under `spikes/s1-proxy-topology/shots/`. Full PNGs are kept for
**headless Chromium** only — it is the deterministic build and the one every
citation below refers to. For `chrome`, `firefox` and `webkit` only
`results.json` is kept: Chrome's PNGs add nothing beyond its numbers given the
GPU-raster noise, and the Firefox/WebKit PNGs are all copies of the unfiltered
scene. Re-generate any of them with `node harness/run.mjs <engine>`.

| Finding | Artefacts |
| --- | --- |
| Q1 edge band, in-place vs proxy | `shots/chromium/heat/inplace__vs__proxy-padfull.png`, `shots/chromium/{inplace,proxy-pad0,proxy-pad20,proxy-pad40,proxy-pad60,proxy-padfull}.png` |
| Q1 padding convergence | `shots/chromium/heat/proxy-padfull__vs__proxy-pad60.png`; `Q1c` rows in `shots/chromium/results.json` |
| Q1 the 3σ rule across three blur radii | `Q1s` rows in `shots/chromium/results.json`; `shots/chromium/s{8,20,40}-pad*.png` |
| Q1 halo from masking the padded box | `shots/chromium/proxy-clippadded.png` vs `shots/chromium/proxy-pad60.png` |
| Q1 background independence | `shots/chromium/heat/{inplace-checker__vs__padfull-checker,inplace-image__vs__padfull-image}.png` |
| Q2 mechanism (exact arithmetic) | `shots/chromium/{mech-none,mech-inplace,mech-proxy-ab,mech-proxy-ba,mech-single}.png`; `pixels` in `results.json` |
| Q2 legal-geometry leak | `shots/chromium/heat/{near-single__vs__near-split-ab,near-split-ab__vs__near-split-ba,nearb-single__vs__nearb-split-ab}.png` |
| Q3 scroll / fixed content | `shots/chromium/heat/{ipf-scroll__vs__scroll-pad60,ipf-fixed-scroll__vs__fixed-scroll-padfull}.png` |
| Q3 transformed ancestors | `shots/chromium/{xf-content-padfull,xf-common-padfull,proxy-padfull}.png` (byte-identical) |
| Q3 scroll container | `shots/chromium/heat/{scr-padfull__vs__scr-pad0,ipf-scroller-300__vs__scr-scrolled-padfull}.png` |
| Q3 DPR proxy-area limit | `shots/chromium/{zoom2-pad200,zoom2-pad300,zoom2-padfull,zoom2-nofilter,zoom3-padfull}.png`; `Q3d` rows |
| Q4 canvas compositing | `shots/chromium/heat/canvas-off-padfull__vs__canvas-on-padfull.png`; `pixels` in `results.json` |
| Q4 overlay plane | `shots/chromium/heat/overlay-base-only__vs__overlay-on.png` |
| Q4 hit-testing, focus, all engines | `shots/extras.json` |
| Q5 probe battery, all four builds | `probe` in `shots/{chromium,chrome,firefox,webkit}/results.json` — `supports`, `computedReadback`, `offscreen`, `auditFixtures`, identical across all four |
| Q5 backdrop-root ground truth | `shots/chromium/break-*.png`; `Q5` rows |
| Q5 audit scored against ground truth | `probe.auditFixtures` in any `results.json`, read against the `Q5` rows |
| Environmental blocker | `harness/engine-check.mjs` output; `pages/{min,structures,split}.html` |
| Human gate for Gecko and WebKit | `pages/manual-check.html` |
