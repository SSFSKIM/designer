# W20 G0 — the instrument, and the exposure list (2026-09-06)

The instrument half of W20 G0, against claims §5.83 and the wave charter
(`docs/doperpowers/specs/2026-09-05-w20-capsule-corner.md`). Two questions, answered
separately: what does the render path actually resolve for every shape the bed declares, and
what has to change in the calibration matrix before it can see the answer. Nothing here
touches the renderer or the geometry resolvers — the fix is G1's, and contract X1 requires the
instrument to read the defect before the fix removes it.

Branch `worktree-agent-a25a82664c39b28df`, commit `3636f5d` (code and scripts).

---

## 1. What was built

| file | what it is |
| --- | --- |
| `packages/geometry/test/render-path-conformance.test.ts` | The geometry-level conformance report: every declared component through the render path and the spec path, at 1x and 2x, plus the default host shape's exposure. Reports and asserts. |
| `packages/geometry/test/harness/say.ts` | One ambient `process.stdout` declaration, in `harness/env.ts`'s shape, so a reporting test can print without `@types/node` reaching the package. |
| `packages/calibration/web/scene.ts` | `?transparent=1`: the page ground goes transparent and the backdrop raster is hidden (`visibility`, so the stage keeps its size). Reported as `SceneReport.transparentPage`. |
| `packages/calibration/scripts/capture-web.ts` | `--alpha`: a third capture per scene, on the tier that actually drew, with `omitBackground`, written as `<scene>__<tier>__alpha.png`. The resolved tier is re-read off its own report and a disagreement is a problem, not a relabel. |
| `packages/calibration/cli/measure.ts` | Reads the conformance capture, conditions on the tier's own interior alpha, extracts `{alpha ≥ 0.5}` with **no region**, and hands the shape axis four new figures. `DRAWN_ALPHA_THRESHOLD`, `MIN_INTERIOR_ALPHA`, `INTERIOR_ALPHA_DEPTH_CSS_PX`. |
| `packages/calibration/src/report.ts` | `ShapeAxisReport` gains optional `drawnAreaWeb`, `declaredIoUWeb`, `declaredContourP95Web`, `declaredContourMaxWeb`, and `DeclaredConformanceInput`. |
| `packages/calibration/cli/compare.ts` | `--alpha` (passed to the capture driver); the alpha image selected on existence so `--skip-capture` re-measures one already on disk; a `declaration conformance` block in the run's own output. |
| `packages/calibration/test/declared-conformance.test.ts` | Contract X4 and the analytic counterpart of the defect, over synthetic masks. |
| `results/2026-09-05-w20-capsule-corner/g0/` | The run scripts and their logs: `g0-conformance-run.sh` (the bed run, to scratch), `g0-alpha-separation.py`, `g0-x4-dilate.py`, `g0-golden-exposure.ts`, and the `.txt` outputs beside them. |

**Schema.** The four rows are optional and `RESULT_MATRIX_SCHEMA_VERSION` stays at 5, which is
the precedent the file already sets for the W13 X6 band-windowed SSIM rows and the W14 X7
shadow affine pair: nothing above them changes meaning, absent keeps its existing sense of
"not measured", and an older matrix still deserialises. The schema doc comment records the
addition beside the other two.

**Flags.** `capture-web … --alpha`; `compare … --alpha`. Both off by default: every committed
matrix so far was measured without the capture, and a run that did not take it must leave the
rows absent rather than assert conformance.

---

## 2. The geometry-level conformance table

`pnpm --filter @vitrea/geometry exec vitest run test/render-path-conformance.test.ts`, output
kept at `g0-geometry-conformance.txt`. Every component `apps/reference-apple/scenes.json`
declares, resolved through the render path exactly as `renderer-webgpu/src/instances.ts` does
— `resolveFromChannels(channels, "apple-continuous", family)` over the channel vector
`platform-web`'s `registerHost` builds (one radius spread to the Vec4, smoothing from
`DEFAULT_HOST_SHAPE`, which is 0) — and through the spec path `resolveShape`.

`gap→declared` is the max distance from the drawn contour to the declared geometry: the
circular rounded rectangle of the declared radius, which for a capsule is the stadium, and
which is the same rule `component-region.ts` rasterises and the same shape `Capsule()` draws.
`gap render↔spec` is the max nearest-neighbour distance between the two paths' contours.

### At 1x (CSS px)

| shape | r/min | declared r | render r | render reach | spec r | saturated | gap→declared | gap render↔spec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| capsule-button 120×44 | 0.5000 | 22.00 | **14.39** | 22.00 | 22.00 | YES | **3.1797** | 3.1798 |
| toolbar-group item 44×44 | 0.5000 | 22.00 | **14.39** | 22.00 | 22.00 | YES | **3.1797** | 3.1798 |
| rrect-sm 64×32 | 0.2500 | 8.00 | 8.00 | 12.23 | 8.00 | no | 0.1104 | 0.0000 |
| rrect-md 160×96 | 0.2083 | 20.00 | 20.00 | 30.57 | 20.00 | no | 0.2760 | 0.0000 |
| rrect-ml 224×128 | 0.2109 | 27.00 | 27.00 | 41.27 | 27.00 | no | 0.3726 | 0.0000 |
| rrect-lg 280×160 | 0.2125 | 34.00 | 34.00 | 51.97 | 34.00 | no | 0.4691 | 0.0000 |
| glass-over-glass base 220×130 | 0.1846 | 24.00 | 24.00 | 36.69 | 24.00 | no | 0.3312 | 0.0000 |
| glass-over-glass over 120×56 | 0.2857 | 16.00 | 16.00 | 24.46 | 16.00 | no | 0.2208 | 0.0000 |

### At 2x (device px)

Every row is the 1x row doubled, to nine decimal places: the clamp is a ratio and is therefore
scale-invariant, so the 2x bed carries the same defect and not a worse one. The capsule draws
at **28.783** device px of a declared 44, with a **6.3594** px gap.

### What the table says

- **The capsule is the whole defect and the ratio is what decides it.** Both capsules sit at
  exactly one half of the short side; every rounded rectangle of the bed is under Apple's
  saturation ratio of 0.327083, and no rounded rectangle is clamped at either scale. The
  render path and the spec path give the identical corner on all six rounded rectangles —
  radius, reach, and contour to zero.
- **The residual on a rounded rectangle is Apple's own curve, not an error.** The declared
  geometry is circular and Apple's `.continuous` corner is not, so `gap→declared` on a
  rounded rectangle is a fixed 0.0137985 · r — the same constant on all six shapes at both
  scales, because the curve is similar in r. The capsule's gap is 0.14453 · r, an order of
  magnitude larger and a clamp rather than a curve. The shape axis's floor is the raster grid
  at ±0.5 px, so the first is invisible to it and the second is not.
- **`saturated` is reported by the contour builder and nowhere else.** `buildAppleContour`
  sets it; `resolveCorner` returns the clamped radius with no flag on it, and the renderer
  calls the resolver. That is the second half of why nineteen waves passed without a warning.

---

## 3. The alpha-separation evidence

The recommended instrument reads the tier's DRAWN silhouette as `{alpha ≥ 0.5}` over a
transparent-page capture. That rule is only honest if the tier's fill is above the threshold
and everything it draws outside its contour is below, so both were measured rather than
assumed: `g0-alpha-separation.py` profiles the alpha by analytic signed distance to the
declared contour. Output at `g0-alpha-separation.txt`, on
`apple-macos-26.5-1x-light-standard` at 1x with the committed light profile
(`sha256:16c2f2805f87`), real adapter `apple/metal-3`.

### The GPU tier: the rule holds exactly

`photo__capsule-button__rest`, alpha by distance shell (device px, negative inside):

| shell | −8…−2 | −1…0 | 0…1 | 1…2 | 2…3 | 3…4 | 4…5 | 6…13 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| max | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3843 | 0.1098 | ≤ 0.1020 |
| mean | 1.0000 | 0.9992 | 0.3850 | 0.2982 | 0.2408 | 0.0908 | 0.0740 | ≤ 0.0664 |

- Interior alpha at four CSS px of depth: median **1.0000**, min 1.0000, max 1.0000.
- The outer shadow never exceeds **0.1098** beyond the boundary band; on `photo__rrect-md__rest`
  its highest value anywhere outside the contour is 0.5294, and every such pixel is inside the
  antialiased boundary itself — the extracted area at threshold 0.5 comes back at 15017 against
  a declared 15024, i.e. below it.
- Extraction at 0.5 on the capsule: **5104 px**, against **5104** for the clamped contour
  computed analytically and **4872** for the declaration. The rule recovers the drawn shape to
  the pixel, and the 232 px excess is the shoulders §5.83 measured.
- The threshold is not delicate: 0.3 gives 5120 and 0.7 gives 5086, all within the
  antialiased band of the same shape.

Note that the alpha above 1.0 through the 0…3 shells is not shadow. It is the defect: those
pixels are *outside the declared stadium and inside the drawn rounded rectangle*, at full
coverage, out to the 3.18 px the geometry table predicts. The instrument sees the shoulders
directly.

### The CSS tier: the shadow crosses the fill, and the reading is refused

`photo__capsule-button__rest` on the CSS tier, same profile:

| shell | −8…−2 | −1…0 | 0…1 | 1…2 | 2…3 | 3…4 | 4…13 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| max | 0.2667 | 0.5255 | 0.5255 | 0.5255 | 0.5255 | 0.1255 | ≤ 0.1137 |
| mean | 0.2667 | 0.3655 | 0.2005 | 0.2575 | 0.0983 | 0.0713 | ≤ 0.0677 |

- Interior alpha at four CSS px of depth: a flat **0.2667** — one `rgba()` layer, exactly one
  value over the whole body, min = max = median. That is **below** the 0.5 threshold.
- The 0.5255 pixels are the tier's rim border: 184 of them, RGB 255/255/255, a one-pixel ring
  on the contour. So the tier's own material has TWO levels and the higher one is a line, not
  a body.
- At threshold 0.5 the extraction returns 184 px on the capsule and 376 px on rrect-md — the
  rim ring alone, no body. At 0.7 it returns nothing.
- Lowering the threshold does not rescue it. Half the tier's own interior level (0.1333) admits
  the shadow: **5236** px against a declared 4872 on the capsule, 5220 on
  `light-solid__capsule-button__rest`, 15560 against 15024 on rrect-md. That is a systematic
  +1.25 px of dilation on a tier whose shape is the DOM's `border-radius` and is right by
  construction — the instrument reporting its own artefact as a conformance failure.

**So the shadow's alpha crosses the fill's on the CSS tier, with numbers.** The instrument
handles it by conditioning rather than by guessing: `MIN_INTERIOR_ALPHA = 0.9` is checked per
capture against the tier's own measured interior level, and a tier below it gets the rows
ABSENT with that level named in the note — never a conformance number that would be the
instrument's rather than the renderer's. On the GPU tier, which is the fidelity target (wave
Decision Log 23) and the only tier with the defect, the condition holds with no margin
question: 1.0000 against 0.9.

The cross-tier fallback the brief names (|L_gpu − L_css| inside the dilated declared box) was
not built. It is not needed for the GPU tier, where the alpha rule is exact, and it cannot
answer the CSS tier's own conformance either: after G1 the two tiers agree, so a cross-tier
difference is silent about whether either drew what it was told to. What would extend the
instrument to the CSS tier is listed in §7.

---

## 4. The instrument's readings

### The end-to-end reading, on real captures

`compare --skip-capture --alpha` over the GPU-tier captures of
`apple-macos-26.5-1x-light-standard`, committed light profile, adapter `apple/metal-3`. Log at
`g0-x4-recovery.txt`; this is the whole pipeline — driver, capture, extractor, matrix row,
report block — and not the metric in isolation.

```
── the shape axis (bounded, as it has always been) ──
1x-light-standard  calibration n= 2   IoU mean 1.0000 worst 1.0000   contour p95 mean 0.00 worst 0.00

── declaration conformance: the web tier's DRAWN silhouette against the declaration ──
profile             scene                          drawn px  declared px  IoU     contour p95  contour max
1x-light-standard   photo__capsule-button__rest        5104         4872  0.9545         2.83         3.16
1x-light-standard   photo__rrect-md__rest             15017        15024  0.9993         0.00         1.00
```

Those two blocks are the finding in one screen. The bounded axis reads 1.0000 and 0.00 on both
cells, as it has since v1; the unbounded reading on the same pixels of the same capture says
the capsule is **232 px larger than declared with its contour 3.16 px out**, and the
rounded rectangle is not (7 px under the declaration, within the antialiased boundary, contour
max 1.00 which is the raster). The 3.16 px is the 3.1797 the geometry table predicts
analytically, read through a raster whose floor is ±0.5 px.

On the CSS tier the same two cells produce no conformance row: the interior alpha is 0.2667
against `MIN_INTERIOR_ALPHA` 0.9, and the note names that number. §3 has the evidence.

### Over the bed

`g0-conformance-run.sh` runs the instrument over six profiles (1x and 2x light and dark
standard, plus the two 1x light accessibility profiles) on both tiers, `--set
calibration,validation`, everything redirected to scratch. **It did not run**: the shared GPU
was held for the whole session by the parallel native probe worker
(`VitreaReference … capture --run-label w20-probe-N`, runs 3 through 8+ back to back), and the
protocol for this bed is that two captures never overlap. The script is committed and runs
unattended in one command —

```
bash packages/calibration/results/2026-09-05-w20-capsule-corner/g0/g0-conformance-run.sh
python3 packages/calibration/results/2026-09-05-w20-capsule-corner/g0/g0-bed-table.py \
  /Users/new/.claude/jobs/5c70e47f/tmp/w20/g0-a/bed/g0-conformance.json
```

— and it must be started when nothing else is capturing. A waiter that would have fired it the
moment the machine went quiet was deliberately stopped rather than left armed: it can only see
that the native harness is idle, not that it is finished, and a Chromium capture starting
inside a gap between two of its runs would damage the other side's fixtures rather than this
side's numbers.

What that leaves unverified is coverage, not mechanism: the alpha rule, the refusal, the row
plumbing and the numbers are all read off real captures above, on the primary profile at 1x on
both tiers. What is not yet read is whether any 2x, dark or accessibility cell behaves
differently — in particular whether the `glass-over-glass` overlay group, which resolves
`css-backdrop` sampling even on the GPU tier, still composites above the interior-alpha floor.


### The bed run, taken (2026-09-06 05:13–05:18, after the probe released the GPU)

*The paragraph above is left as written; this is the run it describes, started by the parent once
the native probe had finished.* `g0-conformance-run.sh` at `aa237c8`, twelve runs, every one exit
0, 0 fallen back, 0 problems; 170 cells to scratch (`g0-conformance.json`, schema 5); the table
from `g0-bed-table.py` kept beside this file as `g0-bed-table.txt`. Per profile, tier and
component (n cells; drawn and declared px; IoU; contour p95 / max in device px):

| profile | tier | component | n | drawn | declared | excess | IoU | p95 | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1x light standard | webgpu | capsule-button | 12 | 5104 | 4872 | +232 | 0.9545 | 2.83 | 3.16 |
| 1x light standard | webgpu | toolbar-group | 2 | 5280 | 4584 | +696 | 0.8682 | 3.16 | 3.16 |
| 1x light standard | webgpu | rrect-sm | 2 | 2000 | 2000 | 0 | 1.0000 | 0.00 | 0.00 |
| 1x light standard | webgpu | rrect-md | 6 | 15017 | 15024 | −7 | 0.9993 | 0.00 | 1.00 |
| 1x light standard | webgpu | rrect-ml | 3 | 28039 | 28048 | −9 | 0.9990 | 0.00 | 1.00 |
| 2x light standard | webgpu | capsule-button | 12 | 20400 | 19468 | +932 | 0.9542 | 5.83 | 6.40 |
| 2x light standard | webgpu | toolbar-group | 2 | 21078 | 18276 | +2802 | 0.8671 | 6.32 | 6.40 |
| 2x light standard | webgpu | rrect-sm / md / ml | 2 / 6 / 3 | | | −6 / −41 / −81 | 0.999 | ≤ 1.00 | 1.00 |
| 1x dark standard | webgpu | capsule-button | 6 | 5104 | 4872 | +232 | 0.9545 | 2.83 | 3.16 |
| 2x dark standard | webgpu | capsule-button | 6 | 20400 | 19468 | +932 | 0.9542 | 5.83 | 6.40 |
| 1x increased contrast | webgpu | capsule-button / toolbar-group | 4 / 1 | | | +232 / +696 | 0.9545 / 0.8682 | | 3.16 |
| 1x reduced transparency | webgpu | capsule-button / toolbar-group | 3 / 1 | | | +232 / +696 | 0.9545 / 0.8682 | | 3.16 |
| every profile | webgpu | rrect-md (dark, IC, RT) | 3 / 2 / 2 | | | −10 / −12 / −12 | 0.9992 | 0.00 | 1.00 |
| 1x light / dark, RT | css | capsule-button | 8 / 6 / 1 | 5204 | 4872 | +332 | 0.9362 | 2.24 | 2.83 |
| 1x light / dark | css | rrect-md | 1 / 3 | 15548 / 15540 | 15024 | +524 / +516 | 0.966 | 2.00 | 2.83–3.00 |
| 1x increased contrast | css | capsule-button | 2 | 5544 | 4872 | +672 | 0.8788 | 5.00 | 5.66 |
| 2x light / dark | css | capsule-button | 8 / 6 | 20796 | 19468 | +1328 | 0.936 | 5.00 | 5.66–5.83 |
| 2x light / dark | css | rrect-md | 1 / 3 | 62138 / 62128 | 60064 | +2074 / +2064 | 0.9667 | 4.0–4.1 | 5.66–5.83 |

Absent rows: on the GPU tier one cell per standard profile (the `dark-solid` cell, whose shape
axis is absent — the numbers are in its note, §7); on the CSS tier 17 of 26 cells on each light
standard profile and 5 of 7 on each accessibility profile, refused by the interior-alpha condition.

**What the bed says.**

- **The GPU tier's defect is the same number everywhere.** +232 px per capsule and +696 per toolbar
  at 1x on every profile — light, dark, increased contrast, reduced transparency — and +932 / +2802
  at 2x (the analytic 948 / 2844 less the antialiased band), contour max 3.16 / 6.40 device px:
  the clamp is a ratio and nothing about the scheme, the accessibility fold or the scale touches
  it. Every rounded rectangle reads at its declaration to the antialiased band (−6…−81 px, contour
  max ≤ 1 device px, IoU ≥ 0.999); `rrect-sm` at 1x reads exactly 2000 of 2000.
- **The CSS tier, where the rule applies, reads a uniform oversize.** The condition passes on the
  full-strength tinted cells and on the dark scheme (an opaque or near-opaque material), and there
  the tier's drawn silhouette is **+332 px on the capsule and +516…+524 on rrect-md** — about
  **1.1 px all round** (332 over a 290 px perimeter; 516 over 478), and +672 under increased
  contrast, +1328 / +2064 at 2x. That is not a corner: it is the rim ring, which reads 0.5255 of
  alpha (§3) — 0.03 above the threshold — sitting outside the DOM's border-radius box. The reading
  is honest and marginal at once: a threshold of 0.55 would drop the ring and read the box. It is
  the same line §5.83 saw as the CSS tier's 0.17 |ΔL| ring two pixels outside the contour, and it
  belongs to the CSS tier's rim band (W16 Deferred), recorded under wave Decision Log 23 (a) and
  not chartered.

---

## 5. X4 — the recovery of a known dilation

Two forms, because they answer different questions.

**The metric, over synthetic masks** (`packages/calibration/test/declared-conformance.test.ts`,
8 tests). A mask built from the bed's own declared geometry, dilated by a stated number of
device pixels, read through exactly the composition `measureCell` performs:

| injected | contour max | contour p95 | area excess | IoU |
| --- | --- | --- | --- | --- |
| 0 (exact) | 0.0000 | 0.0000 | 0 | 1.0000 |
| 1 device px | 1.4142 | — | — | < 1 |
| 4 device px, 1x | 4.2426 | 4.1231 | +1150…1300 | declared/drawn |
| 4 device px, 2x | 4.2426 | — | > +2300 | — |

The recovered figure is √2 above the injection because the metric compares boundary pixel
RINGS on the raster: an outer corner pixel's nearest inner boundary pixel is a diagonal away,
so the grid's own √2 is the residual — the same floor `silhouette.ts` already declares. The
reading tracks the injected quantity rather than merely increasing with it.

The same file rebuilds the defect from the geometry alone — the capsule at `22 / 1.52866495` —
and gets **5104 px drawn against 4872 declared, +232, IoU 0.9545** at 1x and **+948** at 2x,
which is the analytic counterpart of the real capture's reading in §3 and of §5.83's shoulder
count. A rounded rectangle at its declared radius reads 1.0000 and 0.

**The pipeline, over a real capture** (`g0-x4-dilate.py`, log at `g0-x4-recovery.txt`): the
driver's own GPU-tier conformance capture, its coverage grown by a Euclidean ball of four
device pixels — a ball rather than a square, because a square dilates the diagonal by 4√2 and
the metric would report that instead of the injection — written back under the same filename,
then re-measured through `compare --skip-capture --alpha`.

| cell | | drawn px | IoU | contour p95 | contour max |
| --- | --- | --- | --- | --- | --- |
| `photo__rrect-md__rest` | as captured | 15017 | 0.9993 | 0.00 | 1.00 |
| | +4 device px | 16941 | 0.8868 | **4.00** | **4.12** |
| `photo__capsule-button__rest` | as captured | 5104 | 0.9545 | 2.83 | 3.16 |
| | +4 device px | 6336 | 0.7689 | 6.40 | 6.71 |

The rounded rectangle is the clean recovery: it starts at the declaration, so the reading after
the injection is the injection — **4.00 at p95 and 4.12 at max, against 4 injected**. The
capsule starts 3.16 px out already, and four more pixels of dilation take it to 6.71 rather
than to 7.16, because the two displacements are along different outward normals at the
diagonal; that is the geometry, not a loss of sensitivity. Both cells' area excesses grow by
the perimeter times the injection (+1232 and +1924 px), as they must.

---

## 6. The exposure for authors

**The react binding.** `<GlassSurface capsule>` registers `shapeFamily: "capsule"` with
`capsuleRadius(width, height)` — half the short side — and re-writes that radius on every
measured box change (`packages/react/src/surface.tsx`). Its default `profile` is `undefined`,
which `cornerReferenceFor` maps to `apple-continuous`. So every capsule an application authors
takes the clamp: the row in §2 is the application's row. The demo's capsule scenes derive from
`scenes.json` through `apps/demo/src/site/scenes.ts` and pass the same prop, so the demo has
shown the clamped shape since v1.

**`DEFAULT_HOST_SHAPE`** (`packages/platform-web/src/host.ts`) is radius 12, and 12 /
0.327083 = **36.688 px**: any host whose short side is under that is clamped.

| host height | drawn radius | clamped by |
| --- | --- | --- |
| 24 | 7.8500 | 4.1500 CSS px |
| 32 | 10.4666 | 1.5334 CSS px |
| 36 | 11.7750 | 0.2250 CSS px |
| 40 | 12.0000 | — |
| 48 | 12.0000 | — |

Ordinary control heights are exactly where it bites; a 24 px chip loses a third of its corner.

**The goldens: none are exposed.** `g0-golden-exposure.ts` reads
`renderer-webgpu/e2e/fixtures/scenes.ts` as data — the same module the golden run, the
regeneration script and the benchmark read — and resolves all 20 surfaces the way
`instances.ts` does. Output at `g0-golden-exposure.txt`:

- **0 of 20 are `family: "capsule"`**, so the capsule fix moves no golden.
- **0 of 20 are clamped** by the reference they draw under. The `rect` helper's default is
  `reference: "figma-smoothing"`, so 19 of the 20 never reach Apple's budget policy at all;
  the one that does is `rim-two-references`'s `a` surface, 88×88 at radius 26, whose r/min is
  **0.2955 — under the 0.327083 ratio**. So even a change to the Apple reference ABOVE the
  ratio leaves every committed golden byte-identical.
- The nearest miss is `lens-size-scaling`'s small surface, 48×30 at radius 10, r/min 0.3333 —
  over the ratio, but on the Figma reference, where the clamp is the budget (15) and 10 passes
  unclamped. It is the one golden to re-check if a future change moves the Figma reference's
  policy instead.

---

## 7. What did not work, and what is left

- **The alpha rule does not reach the CSS tier**, measured in §3: the fill is 0.267 flat, the
  rim border 0.526, the shadow 0.126 at three pixels out, and no fixed threshold separates
  coverage from shadow. The rows are refused there with the tier's interior level in the note.
  The work that would close it is to suppress the outer shadow on the conformance capture
  alone — it is not a fidelity capture, and without the shadow the CSS tier's alpha is a clean
  two-level image whose lower level is the body. That needs the shadow expressed as something
  the page can turn off per capture without going through a material profile the cell would
  then have to name, so it is a design decision rather than a line of code, and it is deferred
  to the wave rather than taken here.
- **The declared region was left alone.** The charter's Decision Log 1 recommends dilating it
  per side by the corner budget as the default instrument. The raster reading measured here is
  exact where it applies and needs no per-side judgement about the shadow, so it is offered as
  the instrument and the dilation is not implemented; if G1 wants both (the charter's option
  2c), the dilation is still open.
- **The conformance rows ride on the shape axis**, so a cell whose shape axis is absent —
  either silhouette empty inside the declared region, which the bed has over `dark-solid` —
  carries no conformance row even when the capture was read. `measureCell` emits the numbers
  in a note in that case rather than dropping them; making them an axis of their own would be
  the cleaner shape if the wave keeps them.
- **Holdout was not read.** The bed run is `--set calibration,validation` only.
