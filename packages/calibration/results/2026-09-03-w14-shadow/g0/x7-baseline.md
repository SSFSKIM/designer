# W14 X7 — the shadow axis's affine pair, baseline on the W12 close bed

The contract (charter X7): *"per ring and direction, beside the occlusion ratio,
the affine pair (a, c) against the backdrop raster, absent where the ring's
backdrop has no contrast to identify them (a solid). Its baseline on the W12
close bed lands with it."* This is that baseline. **Nothing was captured for it**
— the GPU was in use by another worker — and nothing under `profiles/`,
`packages/renderer-webgpu/` or `results/matrix.json` was touched.

## 1. What landed, in one paragraph

`shadowField` now fits `y = a·bg + c` by ordinary least squares over each band's
pixels, against the backdrop raster the capture was taken over, in **linear
luminance**, on both the native and the web side, in the shared measurement path
so `compare` and `diff` write the same thing. The pair is recorded and bounded by
nothing; `adopted-thresholds.test.ts` is untouched and does not read it. The
fields are on `ShadowAxisReport` as `affineNative` and `affineWeb`, arrays of
`ShadowAffineSample`:

| field | meaning | absent when |
| --- | --- | --- |
| `direction` | one of the axis's four sectors, or `all` | never |
| `ringLabel`, `innerDistanceCssPx`, `outerDistanceCssPx` | the band, CSS px | never |
| `sampleCount` | pixels in the band | never |
| `backdropMeanLinear`, `backdropStdDevLinear` | the backdrop under it | never |
| `renderedLevelLinear` | mean rendered luminance over the band | never |
| `slopeALinear` (`a`) | transmission | backdrop σ < 0.02 linear, or n < 32 |
| `interceptCLinear` (`c`) | the lift — light not from the backdrop | the same two conditions |
| `rSquared` | fit quality | the same two, and alone where the render is constant |
| `unidentifiableReason` | which condition failed, in words | when the pair is present |

A band holding no exterior pixel is not emitted at all: that is the frame having
eaten it, not a reading. `unidentifiableReason` distinguishes the two failure
modes, and on a solid backdrop it carries the level and the backdrop mean it
*did* identify, because their ratio is `a + c/bg` and nothing in the band splits
it. The pair is fitted **before** the axis's backdrop-support gate, which is the
point of the contract: `impulse` and `dark-solid` refuse an occlusion ratio and
are exactly where a lift would be identified alone.

Bands are G0's rings, in CSS px: `0-3`, `3-6`, `6-12`, `12-24`, `24-48`, and the
overlapping `0-6` that claims §5.60 §3 and §5.62 quote. They are cut from the
axis's own `signedDistancePx` with the axis's own four sectors, so the pair sits
over the pixels whose occlusion it complements. Bands rather than the occlusion
profile's unit-wide rings because two parameters need the backdrop to *vary*
across the pixels they are fitted over, where a ring mean needs only pixels.

## 2. Method

`cli/diff.ts` — which measures ONE native/web pair from files already on disk —
over the canonical captures in the main checkout's
`packages/calibration/web-captures/` and the fixtures under
`apps/reference-apple/fixtures/`, for every scene of the four standard profiles
(1x and 2x × light and dark) on both tiers: **196 cells, 0 failures**. The
`--fixture-set` label for each scene was read from `apps/reference-apple/scenes.json`'s
`split`. One invocation per cell, from `packages/calibration/`:

```
npx tsx cli/diff.ts \
  --native ../../apps/reference-apple/fixtures/<profile>/<scene>.png \
  --web web-captures/<profile>/<scene>/<scene>__<renderer>.png \
  --background ../../apps/reference-apple/fixtures/backgrounds/<backdrop>@<scale>x.png \
  --profile <profile> --scene <scene> \
  --web-cell web-captures/<profile>/<scene>/cell__<renderer>.json \
  --tier <texture|dom> --fixture-set <set> \
  --matrix <scratch>/matrix-x7-baseline.json --out <scratch>/cells/<...>.json
```
 Output went to a scratch matrix at
`/Users/new/.claude/jobs/5c70e47f/tmp/w14/x7/matrix-x7-baseline.json` with the
per-cell reports beside it under `cells/`; **`results/matrix.json` was not
touched**. The scratch matrix is 7.9 MB and is therefore *not* copied beside this
file — see §7, where its size is a finding of its own.

Two cells in the tables below, `checkerboard__rrect-lg__rest` and
`checkerboard__glass-over-glass__rest`, are holdout scenes. They are read here
for the same reason G0 read them: this is a measurement of Apple's material with
no bound attached and nothing fitted to it, and `rrect-lg` is the span at which
the reference's lift saturates, so a baseline that omitted it could not be
checked against §5.62 at all. Nothing in this document may be fitted to.

`diff` was invoked with its default blur axis and no blur region, so the material
axis's blur figures in the scratch matrix are not the canonical ones. Only the
shadow axis is read here.

## 3. The headline: the lift ladder, against G0

Native, `below`, linear luminance. G0's column is `g0-shadow.md` §2's `lift, lin`
at ring 0–6 with its guard applied; X7's `0-6` column is the same band without a
guard, and its `3-6` column is the innermost band that holds no part of the body.

| cell | span | G0 c_lin (0–6 below) | X7 1x c | X7 2x c | X7 1x, 3–6 | X7 2x, 3–6 |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.0000 | 0.00054 | 0.00028 | 0.00000 | 0.00000 |
| `capsule-button` | 44 | 0.0000 | 0.00115 | 0.00050 | 0.00000 | -0.00000 |
| `rrect-md` | 96 | 0.0022 | 0.00275 | 0.00249 | 0.00211 | 0.00210 |
| `rrect-ml` | 128 | 0.0034 | 0.00529 | 0.00402 | 0.00330 | 0.00334 |
| `rrect-lg` | 160 | 0.0038 | 0.00480 | 0.00445 | 0.00362 | 0.00364 |
| `glass-over-glass` | 130 | 0.0035 | 0.00485 | 0.00406 | 0.00349 | 0.00350 |

**The guarded comparison reproduces G0 to 0.0002 on every span.** X7's `3-6`
band against G0's guarded 0–6: 0.0000 / 0.0000 / 0.00211 / 0.00330 / 0.00349 /
0.00362 against 0 / 0 / 0.0022 / 0.0034 / 0.0035 / 0.0038 at spans 32 / 44 / 96 /
128 / 130 / 160. The knee at 64 is exact — both thin spans read `c` = 0.00000 to
five decimals — and the saturation G0 found is there: 0.58 / 0.91 / 0.96 / 1.00
of the span-160 value where `VibrancyContribution` would say 0.33 / 0.67 / 0.69 /
1.00. It is scale-free: the 2x column matches the 1x column to 0.00005 in every
row of the `3-6` band.

**Where the two differ, and why.** X7's `0-6` band reads high by 0.0005 (span 32)
to 0.0019 (span 128), and it reads a lift on the two spans G0 puts at exactly
zero. Three causes, in order of size:

1. **No guard.** G0's `g0_span.py` excludes `d < 1.5` device px, the antialiased
   boundary. X7 does not, on principle: what would have to be excluded is a
   *measured* quantity — how far each source over-fills its declared contour,
   which §5.62's last Surprise puts at 3.5–4 CSS px for vitrea's GPU capsule and
   3–3.5 for the CSS tier against Apple's ≤ 1 — and a fixed guard chosen inside
   the axis would bake one renderer's current over-fill into the instrument. The
   consequence is visible rather than hidden, and it is the reading that pins the
   cause: **vitrea's own web side, whose shadow is a pure black multiply with
   `c` identically zero, reads `c` = 0.060 in `0-3` below
   `checkerboard__capsule-button__rest` on the GPU tier and 0.432 on the CSS
   tier, and 0.00000 in every band further out.** That is not a lift; it is the
   body. Band `0-3`, and therefore `0-6`, holds the body's own edge — the same
   caveat the axis already states about ring 0 in `falloffPoints`. The field's
   doc comment says so, and every reading below quotes `3-6` as the guard-free
   one.
2. **The sector scheme.** G0 classifies an exterior pixel by the *normal of the
   nearest declared rect* and keeps a fifth `corner` class out of the four sides;
   the axis classifies by aspect-normalised angle from the component's centre and
   has no corner class, so X7's `below` contains the corner surrounds G0's
   excludes. G0 measured the corner lift *below* the side lift (0.0349 against
   0.0479 encoded on `rrect-lg`), so this pushes X7's `below` down, not up — it
   is second-order here and partly cancels cause 1. It is why X7's `3-6` sits
   0.0001–0.0002 under G0's guarded 0–6 rather than exactly on it.
3. **Intercept versus black-square level.** G0's span table reads the mean over
   the checkerboard's black squares directly, with no regression; X7 fits a line
   over both levels. On an exactly two-level backdrop these are the same number,
   and the difference measured here is under 0.0001.

## 4. The tables: the six checkerboard cells, `below`, both scales, both sides

Native and web (`web` is vitrea's GPU tier), linear luminance. R² is the fit's.

### 1x light, GPU tier, below

| cell | ring | a (native) | c (native) | R² | a (web) | c (web) | R² | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 0-3 | 0.7575 | 0.00114 | 0.999 | 0.7986 | 0.00035 | 1.000 | 184 |
| `rrect-sm` | 3-6 | 0.7821 | 0.00000 | 1.000 | 0.8181 | 0.00000 | 1.000 | 204 |
| `rrect-sm` | 6-12 | 0.8248 | 0.00000 | 0.999 | 0.8488 | 0.00000 | 0.999 | 474 |
| `rrect-sm` | 12-24 | 0.8984 | 0.00000 | 0.998 | 0.9113 | 0.00000 | 0.999 | 1182 |
| `rrect-sm` | 24-48 | 0.9804 | 0.00000 | 0.999 | 0.9837 | -0.00000 | 0.999 | 3316 |
| `rrect-sm` | 0-6 | 0.7704 | 0.00054 | 0.999 | 0.8089 | 0.00016 | 0.999 | 388 |
| `capsule-button` | 0-3 | 0.7538 | 0.00238 | 0.998 | 0.7321 | 0.06027 | 0.884 | 316 |
| `capsule-button` | 3-6 | 0.7808 | 0.00000 | 1.000 | 0.8125 | 0.00032 | 1.000 | 340 |
| `capsule-button` | 6-12 | 0.8224 | 0.00000 | 0.999 | 0.8414 | -0.00000 | 0.999 | 748 |
| `capsule-button` | 12-24 | 0.8966 | 0.00000 | 0.998 | 0.9031 | -0.00000 | 0.999 | 1766 |
| `capsule-button` | 24-48 | 0.9798 | -0.00000 | 0.999 | 0.9804 | 0.00000 | 0.999 | 4572 |
| `capsule-button` | 0-6 | 0.7678 | 0.00115 | 0.998 | 0.7738 | 0.02920 | 0.943 | 656 |
| `rrect-md` | 0-3 | 0.7893 | 0.00343 | 0.999 | 0.7971 | 0.00083 | 1.000 | 450 |
| `rrect-md` | 3-6 | 0.8075 | 0.00211 | 1.000 | 0.8162 | -0.00000 | 1.000 | 470 |
| `rrect-md` | 6-12 | 0.8436 | 0.00173 | 0.999 | 0.8457 | 0.00000 | 0.999 | 996 |
| `rrect-md` | 12-24 | 0.9076 | 0.00101 | 0.999 | 0.9079 | -0.00000 | 0.999 | 2214 |
| `rrect-md` | 24-48 | 0.9818 | 0.00018 | 1.000 | 0.9825 | -0.00000 | 0.999 | 5314 |
| `rrect-md` | 0-6 | 0.7986 | 0.00275 | 0.999 | 0.8069 | 0.00041 | 0.999 | 920 |
| `rrect-ml` | 0-3 | 0.7537 | 0.00736 | 0.996 | 0.7967 | 0.00122 | 1.000 | 628 |
| `rrect-ml` | 3-6 | 0.7805 | 0.00330 | 1.000 | 0.8162 | 0.00000 | 1.000 | 652 |
| `rrect-ml` | 6-12 | 0.8192 | 0.00270 | 0.999 | 0.8454 | 0.00000 | 0.999 | 1352 |
| `rrect-ml` | 12-24 | 0.8939 | 0.00153 | 0.998 | 0.9072 | -0.00000 | 0.999 | 2934 |
| `rrect-ml` | 24-48 | 0.9695 | 0.00045 | 0.999 | 0.9732 | -0.00000 | 1.000 | 4068 |
| `rrect-ml` | 0-6 | 0.7674 | 0.00529 | 0.998 | 0.8066 | 0.00060 | 0.999 | 1280 |
| `rrect-lg` | 0-3 | 0.7586 | 0.00601 | 0.998 | 0.7973 | 0.00032 | 1.000 | 780 |
| `rrect-lg` | 3-6 | 0.7883 | 0.00362 | 0.999 | 0.8159 | 0.00000 | 1.000 | 800 |
| `rrect-lg` | 6-12 | 0.8280 | 0.00285 | 0.999 | 0.8451 | -0.00000 | 0.999 | 1666 |
| `rrect-lg` | 12-24 | 0.8874 | 0.00185 | 0.999 | 0.8979 | 0.00000 | 0.999 | 2584 |
| `rrect-lg` | 24-48 | 0.9711 | 0.00045 | 0.999 | 0.9732 | -0.00000 | 1.000 | 532 |
| `rrect-lg` | 0-6 | 0.7736 | 0.00480 | 0.998 | 0.8067 | 0.00016 | 1.000 | 1580 |
| `glass-over-glass` | 0-3 | 0.7554 | 0.00626 | 0.997 | 0.7968 | 0.00093 | 1.000 | 622 |
| `glass-over-glass` | 3-6 | 0.7786 | 0.00349 | 1.000 | 0.8160 | 0.00000 | 1.000 | 642 |
| `glass-over-glass` | 6-12 | 0.8188 | 0.00273 | 0.999 | 0.8450 | -0.00000 | 0.999 | 1336 |
| `glass-over-glass` | 12-24 | 0.8943 | 0.00154 | 0.998 | 0.9069 | 0.00000 | 0.999 | 2906 |
| `glass-over-glass` | 24-48 | 0.9676 | 0.00048 | 0.999 | 0.9722 | -0.00000 | 0.999 | 3744 |
| `glass-over-glass` | 0-6 | 0.7672 | 0.00485 | 0.998 | 0.8066 | 0.00046 | 0.999 | 1264 |

### 2x light, GPU tier, below

| cell | ring | a (native) | c (native) | R² | a (web) | c (web) | R² | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 0-3 | 0.7604 | 0.00058 | 0.999 | 0.7991 | 0.00015 | 1.000 | 740 |
| `rrect-sm` | 3-6 | 0.7845 | 0.00000 | 1.000 | 0.8175 | 0.00000 | 1.000 | 822 |
| `rrect-sm` | 6-12 | 0.8233 | -0.00000 | 0.999 | 0.8488 | 0.00000 | 0.999 | 1880 |
| `rrect-sm` | 12-24 | 0.8981 | -0.00000 | 0.998 | 0.9110 | 0.00000 | 0.999 | 4730 |
| `rrect-sm` | 24-48 | 0.9805 | 0.00000 | 0.999 | 0.9837 | 0.00000 | 0.999 | 13276 |
| `rrect-sm` | 0-6 | 0.7731 | 0.00028 | 0.999 | 0.8088 | 0.00007 | 0.999 | 1562 |
| `capsule-button` | 0-3 | 0.7575 | 0.00103 | 0.999 | 0.7226 | 0.06996 | 0.855 | 1268 |
| `capsule-button` | 3-6 | 0.7822 | -0.00000 | 1.000 | 0.8119 | 0.00008 | 1.000 | 1356 |
| `capsule-button` | 6-12 | 0.8213 | -0.00000 | 0.999 | 0.8417 | 0.00000 | 1.000 | 2994 |
| `capsule-button` | 12-24 | 0.8964 | 0.00000 | 0.998 | 0.9028 | -0.00000 | 0.999 | 7054 |
| `capsule-button` | 24-48 | 0.9799 | 0.00000 | 0.999 | 0.9803 | 0.00000 | 0.999 | 18330 |
| `capsule-button` | 0-6 | 0.7703 | 0.00050 | 0.999 | 0.7687 | 0.03384 | 0.929 | 2624 |
| `rrect-md` | 0-3 | 0.7882 | 0.00290 | 1.000 | 0.7974 | 0.00057 | 1.000 | 1808 |
| `rrect-md` | 3-6 | 0.8096 | 0.00210 | 1.000 | 0.8154 | -0.00000 | 1.000 | 1874 |
| `rrect-md` | 6-12 | 0.8432 | 0.00172 | 0.999 | 0.8461 | -0.00000 | 1.000 | 3986 |
| `rrect-md` | 12-24 | 0.9081 | 0.00100 | 0.999 | 0.9076 | 0.00000 | 0.999 | 8852 |
| `rrect-md` | 24-48 | 0.9816 | 0.00018 | 1.000 | 0.9823 | 0.00000 | 0.999 | 21272 |
| `rrect-md` | 0-6 | 0.7991 | 0.00249 | 0.999 | 0.8066 | 0.00028 | 1.000 | 3682 |
| `rrect-ml` | 0-3 | 0.7562 | 0.00473 | 0.999 | 0.7974 | 0.00037 | 1.000 | 2512 |
| `rrect-ml` | 3-6 | 0.7806 | 0.00334 | 1.000 | 0.8151 | 0.00000 | 1.000 | 2590 |
| `rrect-ml` | 6-12 | 0.8208 | 0.00270 | 0.999 | 0.8456 | -0.00000 | 1.000 | 5408 |
| `rrect-ml` | 12-24 | 0.8947 | 0.00154 | 0.998 | 0.9069 | -0.00000 | 0.999 | 11732 |
| `rrect-ml` | 24-48 | 0.9696 | 0.00044 | 0.999 | 0.9728 | -0.00000 | 0.999 | 16294 |
| `rrect-ml` | 0-6 | 0.7686 | 0.00402 | 0.999 | 0.8064 | 0.00018 | 1.000 | 5102 |
| `rrect-lg` | 0-3 | 0.7587 | 0.00527 | 0.998 | 0.7974 | 0.00030 | 1.000 | 3128 |
| `rrect-lg` | 3-6 | 0.7877 | 0.00364 | 0.999 | 0.8151 | 0.00000 | 1.000 | 3206 |
| `rrect-lg` | 6-12 | 0.8274 | 0.00284 | 0.999 | 0.8455 | -0.00000 | 1.000 | 6648 |
| `rrect-lg` | 12-24 | 0.8866 | 0.00185 | 0.999 | 0.8979 | 0.00000 | 0.999 | 10346 |
| `rrect-lg` | 24-48 | 0.9711 | 0.00045 | 0.999 | 0.9731 | 0.00000 | 1.000 | 2130 |
| `rrect-lg` | 0-6 | 0.7734 | 0.00445 | 0.998 | 0.8064 | 0.00015 | 1.000 | 6334 |
| `glass-over-glass` | 0-3 | 0.7574 | 0.00464 | 0.999 | 0.7975 | 0.00030 | 1.000 | 2494 |
| `glass-over-glass` | 3-6 | 0.7786 | 0.00350 | 1.000 | 0.8151 | 0.00000 | 1.000 | 2564 |
| `glass-over-glass` | 6-12 | 0.8198 | 0.00274 | 0.999 | 0.8456 | -0.00000 | 1.000 | 5362 |
| `glass-over-glass` | 12-24 | 0.8948 | 0.00154 | 0.998 | 0.9068 | 0.00000 | 0.999 | 11622 |
| `glass-over-glass` | 24-48 | 0.9674 | 0.00047 | 0.999 | 0.9719 | 0.00000 | 0.999 | 14968 |
| `glass-over-glass` | 0-6 | 0.7682 | 0.00406 | 0.999 | 0.8064 | 0.00015 | 1.000 | 5058 |

**The instrument's recovery of vitrea's own W8 shadow (X4).** vitrea's `c` is
0.00000 in every band from `3-6` outward on every cell at both scales — a pure
black multiply, read back as a pure black multiply, with no lift invented. Its
`a` at `3-6` is 0.8159 (1x) and 0.8151 (2x) on `rrect-lg`, the same 0.81 on every
span, which is W8's span-invariant amplitude seen from outside. The reference's
`a` in the same band runs 0.7785–0.8096 across the spans, so vitrea's black term
removes **0.83–0.96 of the light the reference's removes** at 1x
(`(1 − a_web)/(1 − a_native)`: 0.835 / 0.855 / 0.955 / 0.838 / 0.870 / 0.831 on
the six cells in order) — §5.62's fourth Surprise put it at 0.84–0.92 on the mid
backdrops, and this is the same reading from the harness rather than from the
spike's own script.

The CSS tier, same window:

### 1x light, CSS tier, below

| cell | ring | a (native) | c (native) | R² | a (web) | c (web) | R² | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 0-3 | 0.7575 | 0.00114 | 0.999 | 0.4632 | 0.36537 | 0.599 | 184 |
| `rrect-sm` | 3-6 | 0.7821 | 0.00000 | 1.000 | 0.8430 | -0.00000 | 0.999 | 204 |
| `rrect-sm` | 6-12 | 0.8248 | 0.00000 | 0.999 | 0.8703 | 0.00000 | 0.998 | 474 |
| `rrect-sm` | 12-24 | 0.8984 | 0.00000 | 0.998 | 0.9258 | 0.00000 | 0.998 | 1182 |
| `rrect-sm` | 24-48 | 0.9804 | 0.00000 | 0.999 | 0.9857 | 0.00000 | 1.000 | 3316 |
| `rrect-sm` | 0-6 | 0.7704 | 0.00054 | 0.999 | 0.6629 | 0.17327 | 0.765 | 388 |
| `capsule-button` | 0-3 | 0.7538 | 0.00238 | 0.998 | 0.2815 | 0.43178 | 0.289 | 316 |
| `capsule-button` | 3-6 | 0.7808 | 0.00000 | 1.000 | 0.8155 | 0.00000 | 0.999 | 340 |
| `capsule-button` | 6-12 | 0.8224 | 0.00000 | 0.999 | 0.8456 | -0.00000 | 0.999 | 748 |
| `capsule-button` | 12-24 | 0.8966 | 0.00000 | 0.998 | 0.9071 | 0.00000 | 0.998 | 1766 |
| `capsule-button` | 24-48 | 0.9798 | -0.00000 | 0.999 | 0.9805 | 0.00000 | 0.999 | 4572 |
| `capsule-button` | 0-6 | 0.7678 | 0.00115 | 0.998 | 0.5583 | 0.20799 | 0.618 | 656 |
| `rrect-md` | 0-3 | 0.7893 | 0.00343 | 0.999 | 0.4063 | 0.38600 | 0.487 | 450 |
| `rrect-md` | 3-6 | 0.8075 | 0.00211 | 1.000 | 0.8160 | 0.00000 | 0.999 | 470 |
| `rrect-md` | 6-12 | 0.8436 | 0.00173 | 0.999 | 0.8471 | 0.00000 | 0.999 | 996 |
| `rrect-md` | 12-24 | 0.9076 | 0.00101 | 0.999 | 0.9069 | -0.00000 | 0.998 | 2214 |
| `rrect-md` | 24-48 | 0.9818 | 0.00018 | 1.000 | 0.9799 | 0.00000 | 0.999 | 5314 |
| `rrect-md` | 0-6 | 0.7986 | 0.00275 | 0.999 | 0.6156 | 0.18881 | 0.703 | 920 |
| `rrect-ml` | 0-3 | 0.7537 | 0.00736 | 0.996 | 0.3494 | 0.42152 | 0.411 | 628 |
| `rrect-ml` | 3-6 | 0.7805 | 0.00330 | 1.000 | 0.8119 | 0.00008 | 0.999 | 652 |
| `rrect-ml` | 6-12 | 0.8192 | 0.00270 | 0.999 | 0.8404 | -0.00000 | 0.999 | 1352 |
| `rrect-ml` | 12-24 | 0.8939 | 0.00153 | 0.998 | 0.9017 | -0.00000 | 0.998 | 2934 |
| `rrect-ml` | 24-48 | 0.9695 | 0.00045 | 0.999 | 0.9704 | 0.00000 | 0.999 | 4068 |
| `rrect-ml` | 0-6 | 0.7674 | 0.00529 | 0.998 | 0.5850 | 0.20685 | 0.661 | 1280 |
| `rrect-lg` | 0-3 | 0.7586 | 0.00601 | 0.998 | 0.3182 | 0.43665 | 0.358 | 780 |
| `rrect-lg` | 3-6 | 0.7883 | 0.00362 | 0.999 | 0.8075 | 0.00011 | 0.999 | 800 |
| `rrect-lg` | 6-12 | 0.8280 | 0.00285 | 0.999 | 0.8364 | 0.00000 | 0.999 | 1666 |
| `rrect-lg` | 12-24 | 0.8874 | 0.00185 | 0.999 | 0.8902 | -0.00000 | 0.998 | 2584 |
| `rrect-lg` | 24-48 | 0.9711 | 0.00045 | 0.999 | 0.9745 | -0.00000 | 1.000 | 532 |
| `rrect-lg` | 0-6 | 0.7736 | 0.00480 | 0.998 | 0.5659 | 0.21562 | 0.632 | 1580 |
| `glass-over-glass` | 0-3 | 0.7554 | 0.00626 | 0.997 | 0.3531 | 0.41794 | 0.415 | 622 |
| `glass-over-glass` | 3-6 | 0.7786 | 0.00349 | 1.000 | 0.8123 | 0.00017 | 0.999 | 642 |
| `glass-over-glass` | 6-12 | 0.8188 | 0.00273 | 0.999 | 0.8411 | -0.00000 | 0.999 | 1336 |
| `glass-over-glass` | 12-24 | 0.8943 | 0.00154 | 0.998 | 0.9020 | 0.00000 | 0.998 | 2906 |
| `glass-over-glass` | 24-48 | 0.9676 | 0.00048 | 0.999 | 0.9693 | 0.00000 | 0.999 | 3744 |
| `glass-over-glass` | 0-6 | 0.7672 | 0.00485 | 0.998 | 0.5863 | 0.20575 | 0.663 | 1264 |

### 2x light, CSS tier, below

| cell | ring | a (native) | c (native) | R² | a (web) | c (web) | R² | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 0-3 | 0.7604 | 0.00058 | 0.999 | 0.4607 | 0.36807 | 0.596 | 740 |
| `rrect-sm` | 3-6 | 0.7845 | 0.00000 | 1.000 | 0.8435 | 0.00000 | 0.998 | 822 |
| `rrect-sm` | 6-12 | 0.8233 | -0.00000 | 0.999 | 0.8700 | -0.00000 | 0.998 | 1880 |
| `rrect-sm` | 12-24 | 0.8981 | -0.00000 | 0.998 | 0.9258 | -0.00000 | 0.998 | 4730 |
| `rrect-sm` | 24-48 | 0.9805 | 0.00000 | 0.999 | 0.9858 | 0.00000 | 1.000 | 13276 |
| `rrect-sm` | 0-6 | 0.7731 | 0.00028 | 0.999 | 0.6622 | 0.17437 | 0.763 | 1562 |
| `capsule-button` | 0-3 | 0.7575 | 0.00103 | 0.999 | 0.2802 | 0.43755 | 0.284 | 1268 |
| `capsule-button` | 3-6 | 0.7822 | -0.00000 | 1.000 | 0.8157 | -0.00000 | 0.999 | 1356 |
| `capsule-button` | 6-12 | 0.8213 | -0.00000 | 0.999 | 0.8452 | 0.00000 | 0.999 | 2994 |
| `capsule-button` | 12-24 | 0.8964 | 0.00000 | 0.998 | 0.9071 | -0.00000 | 0.998 | 7054 |
| `capsule-button` | 24-48 | 0.9799 | 0.00000 | 0.999 | 0.9805 | -0.00000 | 0.999 | 18330 |
| `capsule-button` | 0-6 | 0.7703 | 0.00050 | 0.999 | 0.5569 | 0.21144 | 0.612 | 2624 |
| `rrect-md` | 0-3 | 0.7882 | 0.00290 | 1.000 | 0.4069 | 0.39201 | 0.480 | 1808 |
| `rrect-md` | 3-6 | 0.8096 | 0.00210 | 1.000 | 0.8172 | -0.00000 | 0.999 | 1874 |
| `rrect-md` | 6-12 | 0.8432 | 0.00172 | 0.999 | 0.8477 | -0.00000 | 0.999 | 3986 |
| `rrect-md` | 12-24 | 0.9081 | 0.00100 | 0.999 | 0.9082 | 0.00000 | 0.998 | 8852 |
| `rrect-md` | 24-48 | 0.9816 | 0.00018 | 1.000 | 0.9807 | 0.00000 | 0.999 | 21272 |
| `rrect-md` | 0-6 | 0.7991 | 0.00249 | 0.999 | 0.6157 | 0.19249 | 0.696 | 3682 |
| `rrect-ml` | 0-3 | 0.7562 | 0.00473 | 0.999 | 0.3509 | 0.42741 | 0.404 | 2512 |
| `rrect-ml` | 3-6 | 0.7806 | 0.00334 | 1.000 | 0.8128 | -0.00000 | 0.999 | 2590 |
| `rrect-ml` | 6-12 | 0.8208 | 0.00270 | 0.999 | 0.8420 | -0.00000 | 0.999 | 5408 |
| `rrect-ml` | 12-24 | 0.8947 | 0.00154 | 0.998 | 0.9025 | -0.00000 | 0.998 | 11732 |
| `rrect-ml` | 24-48 | 0.9696 | 0.00044 | 0.999 | 0.9707 | 0.00000 | 0.999 | 16294 |
| `rrect-ml` | 0-6 | 0.7686 | 0.00402 | 0.999 | 0.5854 | 0.21044 | 0.654 | 5102 |
| `rrect-lg` | 0-3 | 0.7587 | 0.00527 | 0.998 | 0.3166 | 0.44476 | 0.346 | 3128 |
| `rrect-lg` | 3-6 | 0.7877 | 0.00364 | 0.999 | 0.8089 | -0.00000 | 1.000 | 3206 |
| `rrect-lg` | 6-12 | 0.8274 | 0.00284 | 0.999 | 0.8373 | 0.00000 | 0.999 | 6648 |
| `rrect-lg` | 12-24 | 0.8866 | 0.00185 | 0.999 | 0.8911 | 0.00000 | 0.998 | 10346 |
| `rrect-lg` | 24-48 | 0.9711 | 0.00045 | 0.999 | 0.9748 | 0.00000 | 1.000 | 2130 |
| `rrect-lg` | 0-6 | 0.7734 | 0.00445 | 0.998 | 0.5658 | 0.21964 | 0.623 | 6334 |
| `glass-over-glass` | 0-3 | 0.7574 | 0.00464 | 0.999 | 0.3533 | 0.42331 | 0.409 | 2494 |
| `glass-over-glass` | 3-6 | 0.7786 | 0.00350 | 1.000 | 0.8114 | 0.00000 | 0.999 | 2564 |
| `glass-over-glass` | 6-12 | 0.8198 | 0.00274 | 0.999 | 0.8402 | 0.00000 | 0.999 | 5362 |
| `glass-over-glass` | 12-24 | 0.8948 | 0.00154 | 0.998 | 0.9008 | -0.00000 | 0.998 | 11622 |
| `glass-over-glass` | 24-48 | 0.9674 | 0.00047 | 0.999 | 0.9687 | -0.00000 | 0.999 | 14968 |
| `glass-over-glass` | 0-6 | 0.7682 | 0.00406 | 0.999 | 0.5855 | 0.20873 | 0.656 | 5058 |

The CSS tier's `0-3` band is the over-fill and nothing else: `c` between 0.29 and
0.43 with R² 0.29–0.60 on every component, and 0.00000 from `3-6` outward. Its
`a` at `3-6` sits within 0.009 of the GPU tier's on five of the six components
(0.8155 against 0.8125 on the capsule, 0.8160 against 0.8162 on `rrect-md`,
0.8075 against 0.8159 on `rrect-lg`) and 0.025 away on `rrect-sm` — the same
shadow from one profile, with the smallest span the least alike.

The dark scheme, GPU tier (the dark bed holds `capsule-button`, `rrect-md` and
`glass-over-glass` on the checkerboard; `rrect-sm`, `-ml` and `-lg` were never
captured there):

### 1x dark, GPU tier, below

| cell | ring | a (native) | c (native) | R² | a (web) | c (web) | R² | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | — | — | — | — | — | — | — | — |
| `capsule-button` | 0-3 | 0.9504 | 0.00038 | 0.996 | 0.8443 | 0.00994 | 0.859 | 316 |
| `capsule-button` | 3-6 | 0.9579 | -0.00000 | 1.000 | 0.9395 | 0.00009 | 0.999 | 340 |
| `capsule-button` | 6-12 | 0.9672 | -0.00000 | 1.000 | 0.9513 | 0.00000 | 1.000 | 748 |
| `capsule-button` | 12-24 | 0.9815 | 0.00000 | 1.000 | 0.9709 | 0.00000 | 1.000 | 1766 |
| `capsule-button` | 24-48 | 0.9974 | -0.00000 | 1.000 | 0.9957 | 0.00000 | 1.000 | 4572 |
| `capsule-button` | 0-6 | 0.9543 | 0.00018 | 0.998 | 0.8936 | 0.00483 | 0.929 | 656 |
| `rrect-md` | 0-3 | 0.8271 | 0.00131 | 0.998 | 0.9345 | 0.00027 | 0.998 | 450 |
| `rrect-md` | 3-6 | 0.8475 | 0.00108 | 1.000 | 0.9425 | 0.00000 | 1.000 | 470 |
| `rrect-md` | 6-12 | 0.8745 | 0.00089 | 1.000 | 0.9525 | -0.00000 | 1.000 | 996 |
| `rrect-md` | 12-24 | 0.9265 | 0.00048 | 0.999 | 0.9724 | 0.00000 | 1.000 | 2214 |
| `rrect-md` | 24-48 | 0.9858 | 0.00008 | 1.000 | 0.9964 | -0.00000 | 1.000 | 5314 |
| `rrect-md` | 0-6 | 0.8375 | 0.00119 | 0.999 | 0.9386 | 0.00013 | 0.999 | 920 |
| `rrect-ml` | — | — | — | — | — | — | — | — |
| `rrect-lg` | — | — | — | — | — | — | — | — |
| `glass-over-glass` | 0-3 | 0.7539 | 0.00222 | 0.996 | 0.9347 | 0.00030 | 0.998 | 622 |
| `glass-over-glass` | 3-6 | 0.7805 | 0.00187 | 1.000 | 0.9424 | 0.00000 | 1.000 | 642 |
| `glass-over-glass` | 6-12 | 0.8190 | 0.00147 | 0.999 | 0.9523 | -0.00000 | 1.000 | 1336 |
| `glass-over-glass` | 12-24 | 0.8934 | 0.00083 | 0.998 | 0.9721 | 0.00000 | 1.000 | 2906 |
| `glass-over-glass` | 24-48 | 0.9673 | 0.00027 | 0.999 | 0.9934 | 0.00000 | 1.000 | 3744 |
| `glass-over-glass` | 0-6 | 0.7674 | 0.00204 | 0.997 | 0.9386 | 0.00015 | 0.999 | 1264 |

### 2x dark, GPU tier, below

| cell | ring | a (native) | c (native) | R² | a (web) | c (web) | R² | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | — | — | — | — | — | — | — | — |
| `capsule-button` | 0-3 | 0.9535 | 0.00017 | 0.998 | 0.8377 | 0.01161 | 0.846 | 1268 |
| `capsule-button` | 3-6 | 0.9584 | 0.00000 | 1.000 | 0.9417 | 0.00003 | 1.000 | 1356 |
| `capsule-button` | 6-12 | 0.9672 | -0.00000 | 1.000 | 0.9513 | -0.00000 | 1.000 | 2994 |
| `capsule-button` | 12-24 | 0.9813 | -0.00000 | 1.000 | 0.9709 | 0.00000 | 1.000 | 7054 |
| `capsule-button` | 24-48 | 0.9974 | 0.00000 | 1.000 | 0.9957 | 0.00000 | 1.000 | 18330 |
| `capsule-button` | 0-6 | 0.9560 | 0.00008 | 0.999 | 0.8914 | 0.00563 | 0.923 | 2624 |
| `rrect-md` | 0-3 | 0.8285 | 0.00125 | 0.999 | 0.9367 | 0.00018 | 0.999 | 1808 |
| `rrect-md` | 3-6 | 0.8476 | 0.00108 | 1.000 | 0.9436 | -0.00000 | 1.000 | 1874 |
| `rrect-md` | 6-12 | 0.8745 | 0.00089 | 1.000 | 0.9525 | -0.00000 | 1.000 | 3986 |
| `rrect-md` | 12-24 | 0.9272 | 0.00048 | 0.999 | 0.9723 | 0.00000 | 1.000 | 8852 |
| `rrect-md` | 24-48 | 0.9859 | 0.00008 | 1.000 | 0.9964 | 0.00000 | 1.000 | 21272 |
| `rrect-md` | 0-6 | 0.8382 | 0.00116 | 0.999 | 0.9402 | 0.00009 | 0.999 | 3682 |
| `rrect-ml` | — | — | — | — | — | — | — | — |
| `rrect-lg` | — | — | — | — | — | — | — | — |
| `glass-over-glass` | 0-3 | 0.7553 | 0.00207 | 0.998 | 0.9373 | 0.00010 | 0.999 | 2494 |
| `glass-over-glass` | 3-6 | 0.7785 | 0.00187 | 1.000 | 0.9434 | -0.00000 | 1.000 | 2564 |
| `glass-over-glass` | 6-12 | 0.8192 | 0.00146 | 0.999 | 0.9523 | -0.00000 | 1.000 | 5362 |
| `glass-over-glass` | 12-24 | 0.8936 | 0.00083 | 0.998 | 0.9721 | 0.00000 | 1.000 | 11622 |
| `glass-over-glass` | 24-48 | 0.9674 | 0.00027 | 0.999 | 0.9934 | -0.00000 | 1.000 | 14968 |
| `glass-over-glass` | 0-6 | 0.7671 | 0.00197 | 0.999 | 0.9404 | 0.00005 | 1.000 | 5058 |

**A finding this baseline adds.** The reference's lift survives into the dark
colour scheme at about half its light-scheme amplitude: `c` at `3-6` below reads
0.00108 on `rrect-md` against 0.00211 in the light scheme (0.51×) and 0.00187 on
`glass-over-glass` against 0.00349 (0.54×), the same ratio at both scales. G0's
reading that the lift is absent over *dark backdrops* stands untouched — that is
`impulse` and `dark-solid`, not the dark scheme — but the dark scheme's own
thick composite was left open there (W14 Deferred, "the shadow under the dark
scheme beyond what G0 reads"), and the ratio is now on the record.

## 5. The light-solid capsule, by ring

`light-solid` is a constant backdrop, so the pair is absent by construction and
the band reports the level it did identify. Backdrop 0.8910 linear throughout.

| scale | tier | direction | ring | native level | web level | backdrop | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1x | GPU | below | 0-3 | 0.81126 | 0.73781 | 0.8910 | collinear |
| 1x | GPU | below | 3-6 | 0.81836 | 0.72461 | 0.8910 | collinear |
| 1x | GPU | below | 6-12 | 0.83142 | 0.75062 | 0.8910 | collinear |
| 1x | GPU | below | 12-24 | 0.85704 | 0.80542 | 0.8910 | collinear |
| 1x | GPU | below | 24-48 | 0.88513 | 0.87269 | 0.8910 | collinear |
| 1x | GPU | below | 0-6 | 0.81494 | 0.73097 | 0.8910 | collinear |
| 1x | GPU | all | 0-3 | 0.83688 | 0.81477 | 0.8910 | collinear |
| 1x | GPU | all | 3-6 | 0.84071 | 0.77250 | 0.8910 | collinear |
| 1x | GPU | all | 6-12 | 0.85204 | 0.79495 | 0.8910 | collinear |
| 1x | GPU | all | 12-24 | 0.87081 | 0.83777 | 0.8910 | collinear |
| 1x | GPU | all | 24-48 | 0.88829 | 0.88151 | 0.8910 | collinear |
| 1x | GPU | all | 0-6 | 0.83884 | 0.79309 | 0.8910 | collinear |
| 1x | CSS | below | 0-3 | 0.81126 | 0.89845 | 0.8910 | collinear |
| 1x | CSS | below | 3-6 | 0.81836 | 0.72727 | 0.8910 | collinear |
| 1x | CSS | below | 6-12 | 0.83142 | 0.75491 | 0.8910 | collinear |
| 1x | CSS | below | 12-24 | 0.85704 | 0.80867 | 0.8910 | collinear |
| 1x | CSS | below | 24-48 | 0.88513 | 0.87270 | 0.8910 | collinear |
| 1x | CSS | below | 0-6 | 0.81494 | 0.80973 | 0.8910 | collinear |
| 1x | CSS | all | 0-3 | 0.83688 | 0.86273 | 0.8910 | collinear |
| 1x | CSS | all | 3-6 | 0.84071 | 0.78264 | 0.8910 | collinear |
| 1x | CSS | all | 6-12 | 0.85204 | 0.80552 | 0.8910 | collinear |
| 1x | CSS | all | 12-24 | 0.87081 | 0.84479 | 0.8910 | collinear |
| 1x | CSS | all | 24-48 | 0.88829 | 0.88246 | 0.8910 | collinear |
| 1x | CSS | all | 0-6 | 0.83884 | 0.82165 | 0.8910 | collinear |
| 2x | GPU | below | 0-3 | 0.80981 | 0.73923 | 0.8910 | collinear |
| 2x | GPU | below | 3-6 | 0.81756 | 0.72325 | 0.8910 | collinear |
| 2x | GPU | below | 6-12 | 0.83167 | 0.75087 | 0.8910 | collinear |
| 2x | GPU | below | 12-24 | 0.85709 | 0.80519 | 0.8910 | collinear |
| 2x | GPU | below | 24-48 | 0.88518 | 0.87257 | 0.8910 | collinear |
| 2x | GPU | below | 0-6 | 0.81382 | 0.73097 | 0.8910 | collinear |
| 2x | GPU | all | 0-3 | 0.83432 | 0.81447 | 0.8910 | collinear |
| 2x | GPU | all | 3-6 | 0.84059 | 0.77171 | 0.8910 | collinear |
| 2x | GPU | all | 6-12 | 0.85220 | 0.79482 | 0.8910 | collinear |
| 2x | GPU | all | 12-24 | 0.87081 | 0.83754 | 0.8910 | collinear |
| 2x | GPU | all | 24-48 | 0.88831 | 0.88144 | 0.8910 | collinear |
| 2x | GPU | all | 0-6 | 0.83755 | 0.79243 | 0.8910 | collinear |
| 2x | CSS | below | 0-3 | 0.80981 | 0.89914 | 0.8910 | collinear |
| 2x | CSS | below | 3-6 | 0.81756 | 0.72671 | 0.8910 | collinear |
| 2x | CSS | below | 6-12 | 0.83167 | 0.75459 | 0.8910 | collinear |
| 2x | CSS | below | 12-24 | 0.85709 | 0.80869 | 0.8910 | collinear |
| 2x | CSS | below | 24-48 | 0.88518 | 0.87273 | 0.8910 | collinear |
| 2x | CSS | below | 0-6 | 0.81382 | 0.81004 | 0.8910 | collinear |
| 2x | CSS | all | 0-3 | 0.83432 | 0.86313 | 0.8910 | collinear |
| 2x | CSS | all | 3-6 | 0.84059 | 0.78242 | 0.8910 | collinear |
| 2x | CSS | all | 6-12 | 0.85220 | 0.80546 | 0.8910 | collinear |
| 2x | CSS | all | 12-24 | 0.87081 | 0.84475 | 0.8910 | collinear |
| 2x | CSS | all | 24-48 | 0.88831 | 0.88246 | 0.8910 | collinear |
| 2x | CSS | all | 0-6 | 0.83755 | 0.82153 | 0.8910 | collinear |

Read as occlusion — `(0.8910 − level)/0.8910`, which is the shadow axis's own
quantity — the `0-6` band below reads **0.0854 native against 0.1796 for the GPU
tier**, a factor of **2.10**, and 0.0854 against 0.0913 for the CSS tier at that
band, where the CSS body's over-fill has already filled `0-3` with surface. Taking
the CSS tier's guard-free `3-6` band instead: 0.0815 native against 0.1838, a
factor of **2.25**. Both bracket §5.62's 2.24× and the charter's 2.4×, and this is
now a harness row rather than a spike's finding: it is the number W14 G2's stop
S3 will be read against.

## 6. Coverage: where the pair identifies at all

Across all 196 cells, 5 880 native bands: **4 032 identified (68.6%)**, 1 848
absent for a flat backdrop, none absent for too few samples. By backdrop:

| backdrop | identified / bands | reading |
| --- | --- | --- |
| `checkerboard` | 1 560 / 1 560 | the lift's primary window |
| `photo` | 1 910 / 1 920 | identified everywhere the band is whole |
| `hc-text` | 350 / 360 | identified |
| `impulse` | 212 / 480 | identified only where the impulses fall in the band |
| `dark-solid` | 0 / 840 | solid — level reported |
| `light-solid` | 0 / 480 | solid — level reported |
| `mid-dark-solid` | 0 / 240 | solid — level reported |

`photo` carries a lift of its own worth flagging for G1: native `c` at `3-6`
below reads 0.01365 on `rrect-lg` and 0.01405 on `rrect-md` at 1x — four to six
times the checkerboard's, and *not* ordered by span. A `photo` band's backdrop
has low-frequency structure that a two-parameter affine cannot separate from a
blurred copy of itself, so some of that intercept is the copy projecting onto the
constant. It is a caveat on reading `c` over `photo` as the lift, not a
measurement of a larger lift, and G0's §4 reached the same conclusion by a
different route (the per-channel fit on `photo` "cannot settle it").

## 7. What this baseline costs, and what is deferred

- **The scratch matrix is 7.9 MB for 196 cells**, of which the affine block is
  about 23 KB per cell — roughly 63% of a cell's bytes, because 30 bands × 2
  sides × 11 fields are written at full float precision. On the canonical bed
  (~60 cells) the same addition would take `results/matrix.json` from 2.4 MB to
  about 3.8 MB. Recorded here rather than optimised away, because the trade —
  dropping the pooled `all` direction (−20%), dropping the two distance fields
  the label already carries (−18%), or rounding at the write boundary — is a
  decision about committed evidence and belongs to the parent at X7's adoption,
  not to this contract.
- **No guard on band `0-3`.** Deferred deliberately (§3, cause 1). The right fix
  is the over-fill measurement §5.62's last Surprise already put in the tech-debt
  tracker: once each source's over-fill is a measured per-cell quantity, this
  axis can take its guard from it instead of from a constant.
- **The sector scheme is the axis's, not G0's.** X7's `below` folds in the corner
  surrounds G0 keeps separate. Reconciling them would mean giving the whole axis
  a fifth direction, which would move the occlusion rows too — out of scope for a
  recorded addition, and worth doing only if G1's fit needs the corner separated.
- **No adopted bound.** By the charter: X7 is recorded from G1 on and adopted at
  G2, and Decision Log 1's third question puts the bound at G2's landing.
