# W18 G1 — the pre-check at the gate (Decision Log 3)

The carriers of the charter's corrected Design bullet are built, and this is what they measure
before any whole-bed run. **The two carriers reproduce G0's `no-outer-shadow` decline within
0.0002 on every one of the twenty-four rows of the separation bed, and they do it while the
shadow stays on the page outside every surface** — which is what makes the closure a removal
from the sampled backdrop rather than a removal of the shadow.

The five headline numbers. `checkerboard__toolbar-group` goes from **−0.0122 to −0.0028** at
dpr 1 and from **−0.0040 to +0.0044** at dpr 2; `photo__toolbar-group` from **−0.0150 to
−0.0087** at dpr 1 and from **−0.0101 to −0.0044** at dpr 2. Three of those four are inside
S4's 0.005; `photo__toolbar-group` at dpr 1 is not, and it is the cell G0's `[parent-impact]` 4
said would not reach 0.005 on this mechanism alone. Carrier A alone leaves −0.0099 and −0.0140
on the same two cells, so **carrier B is load-bearing and is two thirds of the closure on a
group.**

Every GPU capture in this pre-check is byte-identical to G0's, so X3 holds through the change.

## 0. The instrument

**The bed** is G0's own, unchanged: the eighteen scratch scenes of `w18-web.json` through
`VITREA_SCENES` (the lone 44 × 44 capsule, the canonical 120 × 44 one, the three-up at the
declared spacing of 12 and at 40, the stack with its base and its overlay alone, over
`checkerboard`, `photo` and `light-solid`), captured by `capture-web` into scratch roots under
`/Users/new/.claude/jobs/5c70e47f/tmp/w18/g1/`. Nothing canonical was written.

**Two configurations, differing in exactly one branch.** `cfgAB` is the branch as it stands.
`cfgA` stands carrier B down inside `planCssTierShadow` — `run-carriers.sh` applies that one
edit, captures, and reverts it with `git checkout`, asserting the revert before it exits. The
calibration page aliases `@vitreajs/vitrea-web` straight at `platform-web/src/index.ts`, so the
branch's source is what was captured and no build step stands between the edit and the pixels.

**The mask** is the declared component region on every row, the same mask G0's tables are under;
where a native fixture and the same declared geometry both exist the native silhouette agrees to
0.0001 (G0 §0), and `separation.ts` computes both. The reader is G0's `separation.ts` for the
means and this directory's `spread.ts` for the spreads; X4's recovery travels with them
unchanged, because it is the same reader on the same masks (G0 §1).

**The GPU tier, captured once and compared byte for byte.** All 36 PNGs of
`gpu-webgpu-{1,2}x` are identical to G0's `sep-webgpu-{1,2}x`; the only difference anywhere in
those trees is the `capturedAt` field of each `report__webgpu.json`. X3 holds.

## 1. CSS − GPU, whole component, declared region, linear luminance

### dpr 1

| scene | G0 default | G0 shadow declined | carrier A | A + B | closed form (predicted move) |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button__rest` | -0.0005 | +0.0006 | +0.0006 | +0.0006 | +0.0026 |
| `checkerboard__capsule-sm__rest` | -0.0077 | -0.0045 | -0.0046 | -0.0046 | +0.0031 |
| `checkerboard__toolbar-group-wide__rest` | -0.0063 | -0.0031 | -0.0033 | -0.0032 | +0.0032 |
| `checkerboard__toolbar-group__rest` | -0.0122 | -0.0026 | -0.0099 | -0.0028 | +0.0056 |
| `photo__capsule-button__rest` | +0.0004 | +0.0011 | +0.0011 | +0.0011 | +0.0007 |
| `photo__capsule-sm__rest` | -0.0063 | -0.0051 | -0.0053 | -0.0053 | +0.0007 |
| `photo__toolbar-group-wide__rest` | -0.0101 | -0.0084 | -0.0086 | -0.0085 | +0.0010 |
| `photo__toolbar-group__rest` | -0.0150 | -0.0086 | -0.0140 | -0.0087 | +0.0016 |
| `light-solid__capsule-button__rest` | +0.0015 | +0.0026 | +0.0026 | +0.0026 | +0.0014 |
| `light-solid__capsule-sm__rest` | -0.0029 | +0.0017 | +0.0016 | +0.0016 | +0.0017 |
| `light-solid__toolbar-group-wide__rest` | -0.0031 | +0.0017 | +0.0016 | +0.0017 | +0.0017 |
| `light-solid__toolbar-group__rest` | -0.0052 | +0.0017 | -0.0019 | +0.0016 | +0.0030 |

### dpr 2

| scene | G0 default | G0 shadow declined | carrier A | A + B | closed form (predicted move) |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button__rest` | +0.0094 | +0.0101 | +0.0101 | +0.0101 | +0.0018 |
| `checkerboard__capsule-sm__rest` | +0.0026 | +0.0045 | +0.0045 | +0.0045 | +0.0023 |
| `checkerboard__toolbar-group-wide__rest` | +0.0022 | +0.0042 | +0.0041 | +0.0041 | +0.0023 |
| `checkerboard__toolbar-group__rest` | -0.0040 | +0.0044 | -0.0026 | +0.0044 | +0.0045 |
| `photo__capsule-button__rest` | +0.0015 | +0.0018 | +0.0018 | +0.0018 | +0.0005 |
| `photo__capsule-sm__rest` | +0.0017 | +0.0024 | +0.0023 | +0.0023 | +0.0005 |
| `photo__toolbar-group-wide__rest` | -0.0038 | -0.0028 | -0.0028 | -0.0028 | +0.0007 |
| `photo__toolbar-group__rest` | -0.0101 | -0.0043 | -0.0096 | -0.0044 | +0.0013 |
| `light-solid__capsule-button__rest` | +0.0022 | +0.0026 | +0.0025 | +0.0025 | +0.0010 |
| `light-solid__capsule-sm__rest` | +0.0019 | +0.0028 | +0.0028 | +0.0028 | +0.0012 |
| `light-solid__toolbar-group-wide__rest` | +0.0018 | +0.0028 | +0.0028 | +0.0028 | +0.0013 |
| `light-solid__toolbar-group__rest` | -0.0006 | +0.0028 | -0.0000 | +0.0028 | +0.0025 |

## 2. The remainder on the lone box, with both carriers: mean and spread per tier

Declared component region. `keep` is the tier's interior standard deviation over the
backdrop's own under the identical mask — how much of the backdrop's structure survives.

| scene | dpr | GPU mean | CSS mean | Δ mean | GPU sd | CSS sd | Δ sd | GPU keep | CSS keep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button__rest` | 1 | 0.6783 | 0.6789 | +0.0006 | 0.1385 | 0.1399 | +0.0014 | 0.277 | 0.280 |
| `checkerboard__capsule-sm__rest` | 1 | 0.6764 | 0.6718 | -0.0046 | 0.1531 | 0.1390 | -0.0142 | 0.306 | 0.278 |
| `photo__capsule-button__rest` | 1 | 0.6178 | 0.6189 | +0.0011 | 0.0474 | 0.0392 | -0.0082 | 0.542 | 0.448 |
| `photo__capsule-sm__rest` | 1 | 0.5871 | 0.5818 | -0.0053 | 0.0258 | 0.0211 | -0.0048 | 0.967 | 0.789 |
| `light-solid__capsule-button__rest` | 1 | 0.9715 | 0.9741 | +0.0026 | 0.0076 | 0.0031 | -0.0045 | — | — |
| `light-solid__capsule-sm__rest` | 1 | 0.9701 | 0.9717 | +0.0016 | 0.0072 | 0.0049 | -0.0023 | — | — |
| `checkerboard__capsule-button__rest` | 2 | 0.6847 | 0.6948 | +0.0101 | 0.1439 | 0.1522 | +0.0083 | 0.288 | 0.304 |
| `checkerboard__capsule-sm__rest` | 2 | 0.6822 | 0.6867 | +0.0045 | 0.1587 | 0.1493 | -0.0094 | 0.317 | 0.299 |
| `photo__capsule-button__rest` | 2 | 0.6179 | 0.6198 | +0.0018 | 0.0519 | 0.0425 | -0.0094 | 0.588 | 0.481 |
| `photo__capsule-sm__rest` | 2 | 0.5841 | 0.5864 | +0.0023 | 0.0263 | 0.0242 | -0.0021 | 0.994 | 0.913 |
| `light-solid__capsule-button__rest` | 2 | 0.9716 | 0.9742 | +0.0025 | 0.0075 | 0.0028 | -0.0046 | — | — |
| `light-solid__capsule-sm__rest` | 2 | 0.9702 | 0.9730 | +0.0028 | 0.0068 | 0.0045 | -0.0024 | — | — |

## 2a. The remainder attributed — what the spread says and what it does not

**The structure-dependent part, isolated.** The light solid is the one backdrop whose mirror is
exact, so a component's reading there is the tier's own offset with no structure in it, and the
difference between a structured backdrop and the solid on the same component is the
structure-dependent remainder. With both carriers, dpr 1:

| component | checkerboard − solid | photo − solid |
| --- | --- | --- |
| 120 × 44 capsule | −0.0020 | −0.0015 |
| 44 × 44 circle | −0.0062 | −0.0069 |
| three at gap 40 | −0.0049 | −0.0102 |
| three at gap 12 | −0.0044 | −0.0103 |

and at dpr 2: +0.0076 / −0.0007 on the capsule, +0.0017 / −0.0005 on the circle. **M2's expected
signature is confirmed and its sign is not stable across scales:** at dpr 1 the structured
remainder is one-signed negative and three times larger on the small box than on the capsule; at
dpr 2 it is inside 0.002 on the photo and turns POSITIVE on the checkerboard, where it reaches
+0.0076 on the capsule. The `photo` three-up rows are confounded exactly as G0 recorded them —
the third circle sits over a patch whose GPU-tier level is 0.7374 against its siblings' 0.587,
and it alone reads −0.0177 — so the −0.010 in that column is one member's backdrop and not the
neighbours.

**The spread says where it comes from, and it is the leading candidate the parent named.** On
the 1x checkerboard the tier's `keep` — its interior standard deviation over the backdrop's own
under the same mask — is **0.278 on the 44 × 44 circle and 0.280 on the 120 × 44 capsule**, while
the renderer's is **0.306 and 0.277**. The renderer keeps more of the backdrop's structure on the
small box than on the capsule; the CSS tier keeps the same fraction on both. The parent's native
readings put Apple on the renderer's side of that (0.1503 native against 0.1424 on the capsule,
where the renderer reads 0.1531 and 0.1385), so **the box-dependence of the effective blur is a
property of the material that the CSS tier does not have.** The mechanism is M2's: the renderer
samples the real backdrop with 24 px of padding, while a `backdrop-filter` reads the element's
own border-box snapshot with `edgeMode="mirror"`, and on a 44 px box a heavy component at
σ ≈ 13.8 CSS px reaches ±41 px — the kernel covers the box in both extents and the mirror decides
most of the result. On the 120 × 44 capsule the long extent has real content inside the kernel and
only the short one mirrors, which is exactly where the two tiers agree.

**What is NOT derived, stated plainly.** The step from a spread difference to a level difference
is not one coefficient. On the 1x checkerboard circle a spread deficit of −0.0142 accompanies a
level deficit of −0.0062; on the 1x photo circle −0.0048 accompanies −0.0069; on the 1x photo
capsule −0.0082 accompanies **+0.0011**. A mirror preserves a linear blur's box mean exactly, so
every part of this is the chain's nonlinearity — the linear-light encode, the table transfer's
remainder amplified by 1/(1 − α₃) = 2.99, the heavy layer under its raster ramp — acting on a
different distribution, and the distribution is the backdrop's. I could not reduce it to the
profile's numbers in this pre-check, and I am not offering a fitted coefficient in its place.

**The admissible carry, as a bound per box and per scale** (K5's "derived with residual", W16's
effective width as the precedent). With both carriers, on the separation bed:

| dpr | box | structure-dependent remainder | solid-backdrop offset | total CSS − GPU |
| --- | --- | --- | --- | --- |
| 1 | 120 × 44 | −0.0015 … −0.0020 | +0.0026 | +0.0006 … +0.0011 |
| 1 | 44 × 44, alone or grouped | −0.0044 … −0.0069 (−0.0103 on the confounded photo patch) | +0.0016 … +0.0017 | −0.0028 … −0.0087 |
| 2 | 120 × 44 | −0.0007 … +0.0076 | +0.0025 | +0.0018 … +0.0101 |
| 2 | 44 × 44, alone or grouped | −0.0005 … +0.0017 | +0.0028 | +0.0023 … +0.0045 |

The whole of the CSS − GPU spread on the bed with the carriers in is **[−0.0087, +0.0101]**, and
its widest single row is `photo__toolbar-group` at dpr 1 and `checkerboard__capsule-button` at
dpr 2.

## 3. The stack, with both carriers (S4's restated clause)

| scene | dpr | part | GPU | CSS | CSS − GPU | px |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__stack-base__rest` | 1 | whole | 0.6947 | 0.6952 | +0.0005 | 28100 |
| `checkerboard__stack-over__rest` | 1 | whole | 0.6850 | 0.6897 | +0.0047 | 6508 |
| `checkerboard__glass-over-glass__rest` | 1 | whole | 0.7127 | 0.7083 | -0.0044 | 28100 |
| | 1 | base (overlay excluded) | 0.6593 | 0.6674 | +0.0081 | 21592 |
| | 1 | overlay | 0.8899 | 0.8440 | -0.0459 | 6508 |
| `photo__stack-base__rest` | 1 | whole | 0.6597 | 0.6549 | -0.0047 | 28100 |
| `photo__stack-over__rest` | 1 | whole | 0.6208 | 0.6265 | +0.0057 | 6508 |
| `photo__glass-over-glass__rest` | 1 | whole | 0.6861 | 0.6742 | -0.0118 | 28100 |
| | 1 | base (overlay excluded) | 0.6295 | 0.6311 | +0.0016 | 21592 |
| | 1 | overlay | 0.8739 | 0.8174 | -0.0565 | 6508 |
| `checkerboard__stack-base__rest` | 2 | whole | 0.7013 | 0.7057 | +0.0045 | 112416 |
| `checkerboard__stack-over__rest` | 2 | whole | 0.6920 | 0.7003 | +0.0083 | 26012 |
| `checkerboard__glass-over-glass__rest` | 2 | whole | 0.7181 | 0.7168 | -0.0013 | 112416 |
| | 2 | base (overlay excluded) | 0.6657 | 0.6765 | +0.0108 | 86404 |
| | 2 | overlay | 0.8923 | 0.8510 | -0.0413 | 26012 |
| `photo__stack-base__rest` | 2 | whole | 0.6602 | 0.6555 | -0.0048 | 112416 |
| `photo__stack-over__rest` | 2 | whole | 0.6215 | 0.6267 | +0.0052 | 26012 |
| `photo__glass-over-glass__rest` | 2 | whole | 0.6865 | 0.6739 | -0.0127 | 112416 |
| | 2 | base (overlay excluded) | 0.6301 | 0.6307 | +0.0006 | 86404 |
| | 2 | overlay | 0.8740 | 0.8172 | -0.0569 | 26012 |

## 3a. The stack, read against S4's restated clause

S4 restated (Decision Log 2 (2)) asks for the tier's own share: the base excluding the overlay
within 0.005 of the GPU tier, and the overlay alone over the raw backdrop within 0.005.

| part | dpr | before (G0) | with the carriers | inside 0.005 |
| --- | --- | --- | --- | --- |
| `checkerboard` base, overlay excluded | 1 | +0.0083 | **+0.0081** | no, and it was not before |
| `photo` base, overlay excluded | 1 | +0.0018 | **+0.0016** | yes |
| `checkerboard` overlay alone, raw backdrop | 1 | +0.0043 | **+0.0047** | yes |
| `photo` overlay alone, raw backdrop | 1 | +0.0054 | **+0.0057** | yes |
| `checkerboard` base, overlay excluded | 2 | — | **+0.0108** | no |
| `photo` base, overlay excluded | 2 | — | **+0.0006** | yes |

The overlay's whole-cell term is unchanged and is the renderer's: −0.0459 / −0.0565 at dpr 1
against G0's −0.0464 / −0.0572, which is the unsampled white at α 0.66496 on a DOM-sourced group
(G0 §4, charter Deferred). **The one clause the carriers do not meet on the stack is the
checkerboard base excluding the overlay, at +0.0081 (dpr 1) and +0.0108 (dpr 2).** It is not a
shadow term — G0 measured the shadow's whole share of that number at 0.0054 and the carriers
move it by 0.0002 — and it is the 220 × 130 box, the largest on the bed, over the checkerboard,
which is the same structure-dependent remainder as §2a with the opposite sign at 2x.

## 4. The canonical bed's light cells: the closed form's predicted move (S5)

The move is `−shadowTermPredicted`, area-weighted over the cell's surfaces — what the
cell's CSS − GPU rises by when the shadow leaves the sampled backdrop. The W17 bed's
reading is beside it where the wave's Grounding Baseline records one.

| cell | dpr | predicted move | W17 bed CSS − GPU | predicted after | leaves 0.01? |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button__pressed` | 1 | +0.0026 | — | — |  |
| `checkerboard__capsule-button__pressed` | 2 | +0.0018 | — | — |  |
| `checkerboard__capsule-button__rest` | 1 | +0.0026 | -0.0005 | +0.0021 | no |
| `checkerboard__capsule-button__rest` | 2 | +0.0018 | +0.0095 | +0.0113 | **yes** |
| `checkerboard__capsule-button__rest-tint-blue` | 1 | +0.0026 | — | — |  |
| `checkerboard__capsule-button__rest-tint-blue` | 2 | +0.0018 | — | — |  |
| `checkerboard__capsule-button__rest-tint-orange` | 1 | +0.0026 | — | — |  |
| `checkerboard__capsule-button__rest-tint-orange` | 2 | +0.0018 | — | — |  |
| `checkerboard__glass-over-glass__rest` | 1 | +0.0065 | -0.0042 | +0.0023 | no |
| `checkerboard__glass-over-glass__rest` | 2 | +0.0060 | -0.0012 | +0.0048 | no |
| `checkerboard__rrect-lg__rest` | 1 | +0.0015 | — | — |  |
| `checkerboard__rrect-lg__rest` | 2 | +0.0010 | — | — |  |
| `checkerboard__rrect-md__pressed` | 1 | +0.0016 | — | — |  |
| `checkerboard__rrect-md__pressed` | 2 | +0.0010 | — | — |  |
| `checkerboard__rrect-md__rest` | 1 | +0.0016 | — | — |  |
| `checkerboard__rrect-md__rest` | 2 | +0.0010 | — | — |  |
| `checkerboard__rrect-ml__rest` | 1 | +0.0015 | — | — |  |
| `checkerboard__rrect-ml__rest` | 2 | +0.0010 | — | — |  |
| `checkerboard__rrect-sm__rest` | 1 | +0.0031 | — | — |  |
| `checkerboard__rrect-sm__rest` | 2 | +0.0023 | — | — |  |
| `checkerboard__toolbar-group__rest` | 1 | +0.0056 | -0.0122 | -0.0066 | no |
| `checkerboard__toolbar-group__rest` | 2 | +0.0045 | -0.0040 | +0.0005 | no |
| `hc-text__capsule-button__rest` | 1 | +0.0034 | — | — |  |
| `hc-text__capsule-button__rest` | 2 | +0.0025 | — | — |  |
| `hc-text__capsule-button__rest-tint-orange` | 1 | +0.0034 | — | — |  |
| `hc-text__capsule-button__rest-tint-orange` | 2 | +0.0025 | — | — |  |
| `hc-text__rrect-md__rest` | 1 | +0.0024 | — | — |  |
| `hc-text__rrect-md__rest` | 2 | +0.0017 | — | — |  |
| `impulse__capsule-button__rest` | 1 | +0.0000 | — | — |  |
| `impulse__capsule-button__rest` | 2 | +0.0000 | — | — |  |
| `impulse__capsule-button__rest-tint-orange` | 1 | +0.0000 | — | — |  |
| `impulse__capsule-button__rest-tint-orange` | 2 | +0.0000 | — | — |  |
| `impulse__rrect-md__rest` | 1 | +0.0000 | — | — |  |
| `impulse__rrect-md__rest` | 2 | +0.0000 | — | — |  |
| `light-solid__capsule-button__rest` | 1 | +0.0014 | — | — |  |
| `light-solid__capsule-button__rest` | 2 | +0.0010 | — | — |  |
| `light-solid__capsule-button__rest-tint-orange` | 1 | +0.0014 | — | — |  |
| `light-solid__capsule-button__rest-tint-orange` | 2 | +0.0010 | — | — |  |
| `light-solid__rrect-md__rest` | 1 | +0.0036 | — | — |  |
| `light-solid__rrect-md__rest` | 2 | +0.0023 | — | — |  |
| `light-solid__rrect-ml__rest` | 1 | +0.0034 | — | — |  |
| `light-solid__rrect-ml__rest` | 2 | +0.0022 | — | — |  |
| `mid-dark-solid__capsule-button__rest` | 1 | +0.0002 | — | — |  |
| `mid-dark-solid__capsule-button__rest` | 2 | +0.0002 | — | — |  |
| `photo__capsule-button__pressed` | 1 | +0.0007 | — | — |  |
| `photo__capsule-button__pressed` | 2 | +0.0005 | — | — |  |
| `photo__capsule-button__rest` | 1 | +0.0007 | +0.0005 | +0.0012 | no |
| `photo__capsule-button__rest` | 2 | +0.0005 | +0.0016 | +0.0021 | no |
| `photo__capsule-button__rest-tint-blue` | 1 | +0.0007 | — | — |  |
| `photo__capsule-button__rest-tint-blue` | 2 | +0.0005 | — | — |  |
| `photo__capsule-button__rest-tint-orange` | 1 | +0.0007 | — | — |  |
| `photo__capsule-button__rest-tint-orange` | 2 | +0.0005 | — | — |  |
| `photo__capsule-button__rest-tint-orange-half` | 1 | +0.0007 | — | — |  |
| `photo__capsule-button__rest-tint-orange-half` | 2 | +0.0005 | — | — |  |
| `photo__glass-over-glass__rest` | 1 | +0.0019 | -0.0119 | -0.0100 | no |
| `photo__glass-over-glass__rest` | 2 | +0.0018 | -0.0126 | -0.0108 | **yes** |
| `photo__rrect-lg__rest` | 1 | +0.0005 | — | — |  |
| `photo__rrect-lg__rest` | 2 | +0.0003 | — | — |  |
| `photo__rrect-lg__rest-tint-orange` | 1 | +0.0005 | — | — |  |
| `photo__rrect-lg__rest-tint-orange` | 2 | +0.0003 | — | — |  |
| `photo__rrect-md__pressed` | 1 | +0.0005 | — | — |  |
| `photo__rrect-md__pressed` | 2 | +0.0003 | — | — |  |
| `photo__rrect-md__rest` | 1 | +0.0005 | — | — |  |
| `photo__rrect-md__rest` | 2 | +0.0003 | — | — |  |
| `photo__rrect-md__rest-tint-orange` | 1 | +0.0005 | — | — |  |
| `photo__rrect-md__rest-tint-orange` | 2 | +0.0003 | — | — |  |
| `photo__rrect-ml__rest` | 1 | +0.0005 | — | — |  |
| `photo__rrect-ml__rest` | 2 | +0.0003 | — | — |  |
| `photo__rrect-sm__rest` | 1 | +0.0008 | — | — |  |
| `photo__rrect-sm__rest` | 2 | +0.0006 | — | — |  |
| `photo__toolbar-group__rest` | 1 | +0.0016 | -0.0150 | -0.0134 | **yes** |
| `photo__toolbar-group__rest` | 2 | +0.0013 | -0.0101 | -0.0088 | no |

## 4a. S5's clause on the twins: measured move against the closed form's (bound 0.0015)

| scene | dpr | measured move | closed form | miss | inside 0.0015 |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button__rest` | 1 | +0.0011 | +0.0026 | -0.0015 | yes |
| `checkerboard__capsule-sm__rest` | 1 | +0.0031 | +0.0031 | -0.0000 | yes |
| `checkerboard__toolbar-group-wide__rest` | 1 | +0.0031 | +0.0032 | -0.0000 | yes |
| `checkerboard__toolbar-group__rest` | 1 | +0.0094 | +0.0056 | +0.0039 | **no** |
| `photo__capsule-button__rest` | 1 | +0.0006 | +0.0007 | -0.0001 | yes |
| `photo__capsule-sm__rest` | 1 | +0.0011 | +0.0007 | +0.0004 | yes |
| `photo__toolbar-group-wide__rest` | 1 | +0.0016 | +0.0010 | +0.0005 | yes |
| `photo__toolbar-group__rest` | 1 | +0.0063 | +0.0016 | +0.0047 | **no** |
| `light-solid__capsule-button__rest` | 1 | +0.0010 | +0.0014 | -0.0004 | yes |
| `light-solid__capsule-sm__rest` | 1 | +0.0045 | +0.0017 | +0.0029 | **no** |
| `light-solid__toolbar-group-wide__rest` | 1 | +0.0048 | +0.0017 | +0.0030 | **no** |
| `light-solid__toolbar-group__rest` | 1 | +0.0068 | +0.0030 | +0.0038 | **no** |
| `checkerboard__capsule-button__rest` | 2 | +0.0007 | +0.0018 | -0.0011 | yes |
| `checkerboard__capsule-sm__rest` | 2 | +0.0019 | +0.0023 | -0.0003 | yes |
| `checkerboard__toolbar-group-wide__rest` | 2 | +0.0020 | +0.0023 | -0.0003 | yes |
| `checkerboard__toolbar-group__rest` | 2 | +0.0084 | +0.0045 | +0.0038 | **no** |
| `photo__capsule-button__rest` | 2 | +0.0003 | +0.0005 | -0.0002 | yes |
| `photo__capsule-sm__rest` | 2 | +0.0007 | +0.0005 | +0.0002 | yes |
| `photo__toolbar-group-wide__rest` | 2 | +0.0010 | +0.0007 | +0.0003 | yes |
| `photo__toolbar-group__rest` | 2 | +0.0057 | +0.0013 | +0.0044 | **no** |
| `light-solid__capsule-button__rest` | 2 | +0.0004 | +0.0010 | -0.0006 | yes |
| `light-solid__capsule-sm__rest` | 2 | +0.0009 | +0.0012 | -0.0003 | yes |
| `light-solid__toolbar-group-wide__rest` | 2 | +0.0010 | +0.0013 | -0.0003 | yes |
| `light-solid__toolbar-group__rest` | 2 | +0.0034 | +0.0025 | +0.0009 | yes |

## 5. The DOM the carriers produce

Read out of a real Chromium through the e2e harness (`e2e/shared/css-tier-shadow.spec.ts`, four
tests, green on chromium; inline styles elided).

A lone host — `GlassGroupState.cssShadow` is `"layer"`, no container exists anywhere, and the
shadow is L3's second `box-shadow` behind the inset rim:

```
<button data-vitrea-node="solo" data-vitrea-group="solo">glass
  <div data-vitrea-css-layer="sharp"   aria-hidden="true"></div>
  <div data-vitrea-css-layer="heavy"   aria-hidden="true"></div>
  <div data-vitrea-css-layer="overlay" aria-hidden="true"></div>
</button>
```

A three-member group — `cssShadow` is `"group"`; members `a` and `b` are unchanged, and the LAST
host in document order carries the container with one caster per member:

```
<button data-vitrea-node="c" data-vitrea-group="g">glass
  <div data-vitrea-css-layer="sharp"   aria-hidden="true"></div>
  <div data-vitrea-css-layer="heavy"   aria-hidden="true"></div>
  <div data-vitrea-css-layer="overlay" aria-hidden="true"></div>
  <div data-vitrea-css-group-shadow="" aria-hidden="true">
    <div data-vitrea-css-shadow="a" aria-hidden="true"></div>
    <div data-vitrea-css-shadow="b" aria-hidden="true"></div>
    <div data-vitrea-css-shadow="c" aria-hidden="true"></div>
  </div>
</button>
```

The container is `position: absolute; inset: -1px; z-index: -1; pointer-events: none` with
`clip-path: path(evenodd, "…")` of one outer rectangle and three rounded holes; each caster
stands on its member's own measured box to within 0.1 px and carries that member's own
`box-shadow`. Nothing in it is focusable, hit-testable or announced.

A host with `overflow: hidden` — `cssShadow` is `"host"`, the shadow is back on the host, L3
carries only the rim, and no container is built. The DOM is the lone host's.

Releasing the last member of a two-member group takes the container and its casters off the page
and the group falls back to `"layer"`, which the fourth test asserts.

**The shadow is still on the page.** Over a ring one device pixel outside every surface and out
to 40 CSS px, on the 1x checkerboard: the default reads 0.47473, G0's `no-outer-shadow` decline
reads 0.50287, carrier A reads 0.47471 and both carriers read **0.47505**. On the lone capsule
the four read 0.48225 / 0.50222 / 0.48223 / 0.48223. So the carriers take the shadow out of the
sampled backdrop and leave it in the picture, to 0.0003 on the group and 0.00002 on the lone
surface; the 0.0003 is the even-odd clip's edge at the members' contours, which the ring begins
one device pixel outside.

## 6. The cost knee, W16 G0's harness, with and without carrier B (S8)

Every surface is in a group of three, so every surface gets a caster and every third host
a clipped container — the most carrier B can cost. The knee is the count at which the
median leaves the display's 16.7 ms cadence.

| form | dpr | n | median ms | p90 ms |
| --- | --- | --- | --- | --- |
| `two-mask` | 1 | 20 | 11.2 | 16.6 |
| `two-mask` | 1 | 28 | 10.5 | 15.9 |
| `two-mask` | 1 | 32 | 11.8 | 21.1 |
| `two-mask` | 1 | 36 | 13.7 | 22.7 |
| `two-mask` | 1 | 40 | 15.7 | 28.9 |
| `two-mask` | 1 | 48 | 18.1 | 34.6 |
| `two-mask-shadow` | 1 | 20 | 13.9 | 16.7 |
| `two-mask-shadow` | 1 | 28 | 10.7 | 16.7 |
| `two-mask-shadow` | 1 | 32 | 11.7 | 20.2 |
| `two-mask-shadow` | 1 | 36 | 13.6 | 27.1 |
| `two-mask-shadow` | 1 | 40 | 16.6 | 27.0 |
| `two-mask-shadow` | 1 | 48 | 21.6 | 28.7 |
| `two-mask` | 2 | 32 | 12.3 | 20.6 |
| `two-mask` | 2 | 40 | 16.7 | 27.2 |
| `two-mask` | 2 | 48 | 21.5 | 29.7 |
| `two-mask-shadow` | 2 | 32 | 13.6 | 20.1 |
| `two-mask-shadow` | 2 | 40 | 18.4 | 25.6 |
| `two-mask-shadow` | 2 | 48 | 20.9 | 30.5 |

**The knee is unmoved.** Both forms hold the cadence to 36 surfaces at dpr 1 and to 32 at dpr 2,
and both break at 40 — where W16 G0 put it (claims §5.71 §7). Above the knee carrier B costs
0.9 ms at 40 and 3.5 ms at 48 surfaces at dpr 1, and 1.7 ms at 40 and −0.6 ms at 48 at dpr 2,
against a form that has already left the cadence and that the tier's own area budget collapses.
The measurement is deliberately the worst case the runtime can produce: every surface is in a
group of three, so every surface has a caster and every third host a clipped container, where a
real page's groups are mostly one member and get no container at all.

## 7. What contradicts Decision Log 2, and what I could not do

**One correction to the Design's corrected bullet.** It says of carrier A: "L3 is inset by the
border width and carries the inner radius, so grow the shadow's `spread` by the border width to
keep the caster box and the corner radius exactly the host's border box." **No growth is needed
and none was applied.** `layerFrame` writes `inset: -<borderWidth>` on an absolutely positioned
child, whose containing block is the host's PADDING box, so L3's own border box already IS the
host's border box; and `border-radius: inherit` puts the host's own radius on a box of the host's
own size. The caster box and the corner radius are exact with no arithmetic, and adding the
spread would have grown the shadow by the border width on every surface. The unit tests pin the
value written on L3 against the value the material resolved.

**S5's 0.0015 clause is met on every isolated box and missed on the merging three-up.** Table 5:
the measured move matches the closed form to 0.0015 on all eight isolated-box rows at both scales
and on the non-merging three-up, and misses by +0.0038 to +0.0047 on `toolbar-group` at gap 12 —
which is precisely the residual G0 recorded and Decision Log 2 (1) declined to model, because the
carriers remove the thing it models. It also misses by +0.0029 / +0.0030 on the two `light-solid`
rows at dpr 1 that G0 also recorded (+0.0030 on `light-solid__capsule-sm`). On the CANONICAL bed
the only light cells with more than one member are the two `toolbar-group` cells, so S5 as
written would fail on exactly those two and pass everywhere else. **This is a `[parent-impact]`
on S5's wording, not on the closure:** the clause asks the closed form to predict a move whose
last third the closed form was never asked to carry.

**One canonical light cell is predicted to leave W17's 0.01 clause.** `checkerboard__capsule-button`
at dpr 2 stands at +0.0095 on the W17 bed and the twin's measured move is +0.0007, so it lands at
about **+0.0102** — a hundredth over. It is the cell the charter's Deferred list already named
("the 2x `capsule-button` at +0.0094 — the shadow's removal moves it; S5 names what leaves 0.01").
The shadow's removal is not what put it there; it is 0.0007 of it. The other named cell,
`photo__glass-over-glass` at dpr 2, stays at −0.0108 because its remainder is the renderer's
overlay route, which no carrier touches.

**What I could not do.** I did not derive the structure-dependent remainder from the profile
(§2a); it is offered as a bound per box and per scale with its geometry, and the mechanism is
named and evidenced by the spread. I did not read the holdout, did not run the whole bed, and did
not touch the canonical matrix, the canonical captures, the fixtures or `scenes.json` — the gate
is Decision Log 3 and this stops here. The fold profiles (reduced transparency, increased
contrast) were not captured in this pre-check: G0's bed is the two light-standard documents, and
q4's clause on `photo__toolbar-group` is measured at the dry run.

## 8. What is in this directory

| file | what it is |
| --- | --- |
| `run-carriers.sh` | the six captures: both tiers, both scales, both configurations, one at a time |
| `spread.ts` | §2's reader — mean, standard deviation and the backdrop's own, under both masks |
| `closed-form.ts` | G0 §6's form on a whole scene bed; two changes from G0's, both named in its header |
| `tables.py` | every table above, from the JSON alone |
| `cost.mjs`, `cost-cases.json`, `pages/cost.html`, `cost-probe.js` | §6's knee run — W16 G0's harness plus one form that adds carrier B |
| `parts/` | every reading: the four separations, the two spreads, the bed's closed form, the cost |
