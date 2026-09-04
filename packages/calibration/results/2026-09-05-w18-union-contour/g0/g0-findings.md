# W18 G0 — the union-contour residual, separated (spike findings)

The charter (`docs/doperpowers/specs/2026-09-05-w18-union-contour-residual.md`) opens this wave on
a residual it names three candidate owners for: the box (M1), the box-limited filter input (M2), the
neighbours (M3), and the stack's route (M4). It expects the neighbours' term to be the union's — "a
three-up minus lone-circle difference on one tier only, and which tier names the owner".

**The owner is one mechanism the charter does not list, and it is entirely the CSS tier's: the tier
draws the outer shadow as a `box-shadow` on the HOST, the host's three filter layers are its
children, and Chromium samples a `backdrop-filter`'s backdrop over the region its kernel needs — so
the tier blurs its own shadow, and its neighbours', into its own body.** Declining the outer shadow
moves the GPU tier's interior mean by **0.00000** on every cell measured and moves the CSS tier's by
+0.0011 to +0.0096. It is **−0.0096 of the −0.0122** on `checkerboard__toolbar-group` at dpr 1,
**−0.0064 of the −0.0150** on `photo__toolbar-group`, and **−0.0084** on the 2x checkerboard cell
whose whole residual is −0.0040. It is the whole of the neighbours' term — the three-up's excess
over the same three circles at a non-merging gap is −0.0058 with the shadow and **+0.0005** without
it — and roughly half of the lone 44 × 44 box's.

Two consequences follow immediately and both matter to the parent. **The renderer's union is not
implicated:** the GPU tier's interior mean over the three-up is flat to ±0.0002 across eight gaps
from 12 to 56, so nothing about `DEFAULT_GROUP_UNION` reaches the number this wave is closing.
**The stack is a different mechanism and it is the renderer's:** the stack's residual is not the
shadow (declining it moves the overlay's reading by 0.0001) and not the overlay's material (the same
overlay alone over the raw backdrop reads +0.004 / +0.005), it is that the renderer draws an
*unsampled* material on a DOM-sourced group — a white tint at α 0.665 with `analysis: "none"` —
where the CSS tier draws the profile's converted one. Section 7 carries that as a `[parent-impact]`.

Every reading below is a GPU-tier or CSS-tier capture taken on this machine's `apple / metal-3`
adapter through Playwright's full Chromium binary at the scene's pixel size, into scratch capture
roots under `/Users/new/.claude/jobs/5c70e47f/tmp/w18/g0/`. Nothing canonical was written. The
native probe's Screen Recording grant is denied on this machine and its capture half is stopped —
§5 states exactly what that costs and what was recovered without it.

## 0. The instrument

**The bed.** Eighteen scratch scenes through `VITREA_SCENES`, geometry for the four twins copied
verbatim from `apps/reference-apple/scenes.json`: the lone 44 × 44 capsule (`capsule-sm`), the
canonical 120 × 44 one at the same span, the three-up at the declared spacing of 12 and at 40 — past
the renderer's separation of 16 and past the sampling padding of 24, so the renderer draws no union
and nothing of the tier's overlaps — over `checkerboard`, `photo` and `light-solid`; and the stack
with its base (220 × 130 r24) and its overlay (120 × 56 r16 at [0, −8]) alone. A second scratch bed
carries the same three circles at eight gaps. `compare` is not the driver: eight of the eighteen
scenes have no native fixture and never will on this bed, and the quantity under test is a
CSS-tier-minus-GPU-tier difference, which needs no reference at all. The driver is `capture-web`
and the reading is `separation.ts`'s.

**The masks, both stated.** Where the canonical bed has a fixture for the scene id AND declares the
same geometry, the reading is under the **native silhouette**, which is the mask every number in
the Grounding Baseline is under. Everywhere else it is under the **declared component region**,
rasterised by pixel-centre containment at margin 0 — the same region that bounds the native
extractor's own search. On `checkerboard__toolbar-group__rest` the two masks are the same 4 584
pixels and give the same mean to 0.0e+00; on `glass-over-glass` they differ by 89 pixels of 28 100
and by 0.0001 of the difference. Every table below says which mask it is under.

**The declines.** Seven scratch profile documents (`make-profiles.mjs`, reproduced under
`profiles/`): the charter's five terms one at a time, all five together, and a sixth this spike
added — the whole outer shadow, every occlusion anchor and the lift at zero. Each is the committed
light-standard document with the declined fields written into its `patch`, the isolation proof's
construction through the `--material-profile` seam. **Both tiers are rendered under every document**,
which is what makes the reading a separation: `optics.ts` derives the CSS tier's material from the
same profile the renderer resolves, so a declined term is declined on both sides and the movement of
the CSS-minus-GPU difference is that term's *share of the residual* rather than the term's own size.

## 1. (f) — the X4 recovery, before any separation was read

`x4-recovery.ts` is W17 G0's contract on this wave's own reader. W17's script validated `measureCell`
under the native silhouette; this study also reads a **declared component region** and a **per-surface
shape**, which that script never exercised, so the recovery is run under every mask the findings use.
Construction unchanged: each capture pixel decoded to linear light, raised by a nominal +0.03,
clamped at white, re-encoded to eight bits; the ACHIEVED offset recomputed independently over the
same mask from the bytes actually written.

Scratch cell `checkerboard__toolbar-group__rest`, CSS tier, dpr 1, capture `72ad31e5837aa26e`:

| mask | pixels | interior mean as captured | recovery | against nominal +0.030 | against the offset on disk |
| --- | --- | --- | --- | --- | --- |
| declared component region | 4 584 | 0.664088 | +0.030632 | +0.000632 | +3.2e−15 |
| declared surface 0 | 1 528 | 0.676882 | +0.030712 | +0.000712 | −1.5e−15 |
| declared surface 1 | 1 528 | 0.659594 | +0.030486 | +0.000486 | −2.4e−15 |
| declared surface 2 | 1 528 | 0.655789 | +0.030699 | +0.000699 | +6.3e−16 |
| native silhouette | 4 584 | 0.664088 | +0.030632 | +0.000632 | +3.2e−15 |

The recovery is inside 0.0008 of the nominal offset under every mask and inside 3.2e−15 of the offset
the doctored file carries; the whole of the +0.0005…+0.0007 is the eight-bit round trip's own upward
bias. **`measureCell` — the production path — returns 0.6640883818392666 on this capture and this
script's native-mask reading is 0.6640883818392666, a difference of 0.0e+00.** No pixel of any mask
was clamped at white. `parts/x4-recovery.json`.

## 2. (a) — the separation

Interior mean, linear luminance, whole component. The mask is the **declared component region** on
every row of this table; where a native silhouette also exists it is given beside it and agrees to
0.0001 (§0). Standard light profile, committed material.

### dpr 1

| scene | GPU | CSS | CSS − GPU |
| --- | --- | --- | --- |
| `checkerboard__capsule-button` (120 × 44) | 0.6783 | 0.6778 | −0.0005 |
| `checkerboard__capsule-sm` (44 × 44) | 0.6764 | 0.6687 | **−0.0077** |
| `checkerboard__toolbar-group-wide` (3 × 44, gap 40) | 0.6762 | 0.6698 | −0.0063 |
| `checkerboard__toolbar-group` (3 × 44, gap 12) | 0.6763 | 0.6641 | **−0.0122** |
| `photo__capsule-button` | 0.6178 | 0.6183 | +0.0004 |
| `photo__capsule-sm` | 0.5871 | 0.5807 | −0.0063 |
| `photo__toolbar-group-wide` | 0.6374 | 0.6272 | −0.0101 |
| `photo__toolbar-group` | 0.6363 | 0.6213 | **−0.0150** |
| `light-solid__capsule-button` | 0.9715 | 0.9730 | +0.0015 |
| `light-solid__capsule-sm` | 0.9701 | 0.9672 | −0.0029 |
| `light-solid__toolbar-group-wide` | 0.9701 | 0.9670 | −0.0031 |
| `light-solid__toolbar-group` | 0.9701 | 0.9649 | −0.0052 |

### dpr 2

| scene | GPU | CSS | CSS − GPU |
| --- | --- | --- | --- |
| `checkerboard__capsule-button` | 0.6847 | 0.6941 | +0.0094 |
| `checkerboard__capsule-sm` | 0.6822 | 0.6848 | +0.0026 |
| `checkerboard__toolbar-group-wide` | 0.6821 | 0.6842 | +0.0022 |
| `checkerboard__toolbar-group` | 0.6821 | 0.6781 | **−0.0040** |
| `photo__capsule-button` | 0.6179 | 0.6194 | +0.0015 |
| `photo__capsule-sm` | 0.5841 | 0.5857 | +0.0017 |
| `photo__toolbar-group-wide` | 0.6362 | 0.6324 | −0.0038 |
| `photo__toolbar-group` | 0.6374 | 0.6273 | **−0.0101** |
| `light-solid__capsule-button` | 0.9716 | 0.9738 | +0.0022 |
| `light-solid__capsule-sm` | 0.9702 | 0.9721 | +0.0019 |
| `light-solid__toolbar-group-wide` | 0.9702 | 0.9721 | +0.0018 |
| `light-solid__toolbar-group` | 0.9702 | 0.9696 | −0.0006 |

**The bed reproduces.** `checkerboard__toolbar-group` reads −0.0122 and `photo__toolbar-group`
−0.0150 at dpr 1 and −0.0040 / −0.0101 at dpr 2 — the Grounding Baseline's four numbers to the
digit, under the same mask, on a scratch bed that declares the geometry independently.

**The three parts, on the two homogeneous backdrops** (the photo is confounded: a 44 px circle at
gap 12 and the same circle at gap 40 sit over different patches of it, and the GPU tier's own
reading moves by 0.005 between them, so only the `checkerboard` and `light-solid` columns separate
cleanly).

| part | checkerboard 1x | light-solid 1x | checkerboard 2x | light-solid 2x |
| --- | --- | --- | --- | --- |
| the same span alone (120 × 44 capsule) | −0.0005 | +0.0015 | +0.0094 | +0.0022 |
| the box (44 × 44 circle minus that capsule) | −0.0072 | −0.0044 | −0.0068 | −0.0003 |
| the neighbours far (three at 40 minus the lone circle) | +0.0014 | −0.0002 | −0.0004 | −0.0001 |
| the neighbours near (three at 12 minus three at 40) | **−0.0059** | **−0.0021** | **−0.0062** | **−0.0024** |
| sum | −0.0122 | −0.0052 | −0.0040 | −0.0006 |
| measured | −0.0122 | −0.0052 | −0.0040 | −0.0006 |

The parts are differences of measured cells, so they sum to the whole exactly; what the table says
is where the residual lives. **At 2x the `toolbar-group` cell is small by cancellation, not by
health:** the box costs −0.0068 and the neighbours −0.0062 against a capsule that is itself +0.0094.

**The spacing sweep resolves the length scale and names the tier.** The same three circles at eight
gaps (`run-spacing.sh`, `parts/spacing.txt`), declared region:

| gap | GPU ck 1x | CSS ck 1x | CSS − GPU ck 1x | CSS − GPU ls 1x | CSS − GPU ck 2x | CSS − GPU ls 2x |
| --- | --- | --- | --- | --- | --- | --- |
| 12 | 0.6763 | 0.6641 | −0.0122 | −0.0052 | −0.0040 | −0.0006 |
| 16 | 0.6762 | 0.6651 | −0.0111 | −0.0041 | −0.0011 | +0.0006 |
| 20 | 0.6764 | 0.6668 | −0.0096 | −0.0036 | +0.0005 | +0.0013 |
| 24 | 0.6762 | 0.6680 | −0.0082 | −0.0033 | +0.0018 | +0.0017 |
| 28 | 0.6763 | 0.6701 | −0.0062 | −0.0031 | +0.0021 | +0.0018 |
| 32 | 0.6762 | 0.6697 | −0.0064 | −0.0031 | +0.0021 | +0.0018 |
| 40 | 0.6762 | 0.6698 | −0.0063 | −0.0031 | +0.0022 | +0.0018 |
| 56 | 0.6762 | 0.6688 | −0.0074 | −0.0031 | +0.0027 | +0.0018 |

**The GPU tier's interior mean is flat to ±0.0002 across the whole sweep** on both homogeneous
backdrops — 0.6762–0.6764 at 1x, 0.9701–0.9702 on the solid — so crossing the renderer's separation
(16) and the sampling padding (24) costs the renderer's interior nothing. The CSS tier rises
monotonically and saturates by a gap of 28, which is neither 16 nor 24; it is the reach of a
Gaussian of σ 15.55 CSS px, the outer shadow's own width. §3 confirms that by declining it.

**The annulus, per surface** (`parts/annulus.txt`, declared shape, four bands by the fraction of the
half extent). At dpr 1 on the solid, the lone circle reads −0.0053 / −0.0068 / −0.0003 / +0.0008
from centre outward: a broad interior offset, not a contour band, exactly W17 G1's signature. Each
member of the three-up at gap 40 reads the lone circle's profile to the last digit
(−0.0053 / −0.0068 / −0.0003 / +0.0008), and at gap 12 the two members with a close neighbour drop
to −0.0054…−0.0076 in the core while the third stays at the lone value. On the `checkerboard` the
per-surface numbers are dominated by the checker's phase under each circle (the three sit at
different phases of a 16 px cell), which is why the three-member spread there is not a mechanism.

## 3. (b) — the per-term attribution

`run-attribution.sh`: eight configurations × two tiers × two scales over the twelve separation
scenes, 32 runs, all exit 0. Each column is `delta(default) − delta(that decline)` — what the
CSS-minus-GPU residual loses when the term is taken out of both tiers at once. `whole` is
`delta(default) − delta(all five declined)`. `parts/attribution.txt` carries all 24 rows; the four
`toolbar-group` and `capsule-sm` rows and their controls:

### dpr 1

| scene | default | whole (five) | lens | rim | highlight | lift | inner shadow | sum | sum − whole | **outer shadow** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-sm` | −0.0077 | +0.0113 | −0.0000 | +0.0081 | +0.0018 | +0.0000 | +0.0011 | +0.0110 | −0.00026 | **−0.0032** |
| `checkerboard__capsule-button` | −0.0005 | +0.0080 | +0.0002 | +0.0058 | +0.0015 | +0.0000 | +0.0016 | +0.0090 | +0.00098 | −0.0011 |
| `checkerboard__toolbar-group` | −0.0122 | +0.0114 | −0.0000 | +0.0080 | +0.0024 | +0.0000 | +0.0012 | +0.0116 | +0.00023 | **−0.0096** |
| `checkerboard__toolbar-group-wide` | −0.0063 | +0.0106 | −0.0001 | +0.0075 | +0.0021 | +0.0000 | +0.0011 | +0.0105 | −0.00011 | −0.0033 |
| `photo__toolbar-group` | −0.0150 | +0.0095 | −0.0025 | +0.0087 | +0.0022 | +0.0000 | +0.0008 | +0.0093 | −0.00018 | **−0.0064** |
| `photo__toolbar-group-wide` | −0.0101 | +0.0119 | −0.0001 | +0.0086 | +0.0023 | +0.0000 | +0.0009 | +0.0116 | −0.00026 | −0.0017 |
| `light-solid__capsule-sm` | −0.0029 | +0.0055 | +0.0000 | +0.0007 | +0.0005 | +0.0000 | +0.0047 | +0.0058 | +0.00030 | **−0.0046** |
| `light-solid__capsule-button` | +0.0015 | +0.0091 | +0.0000 | +0.0057 | +0.0063 | +0.0000 | +0.0030 | +0.0150 | **+0.00593** | −0.0011 |
| `light-solid__toolbar-group` | −0.0052 | +0.0061 | +0.0000 | +0.0007 | +0.0003 | +0.0000 | +0.0046 | +0.0056 | −0.00052 | **−0.0069** |
| `light-solid__toolbar-group-wide` | −0.0031 | +0.0054 | +0.0000 | +0.0005 | +0.0003 | +0.0000 | +0.0046 | +0.0054 | +0.00005 | −0.0048 |

**Superposition holds on 22 of 24 rows.** `sum − whole` is inside 0.0018 on every row but
`light-solid__capsule-button`, which reads **+0.0059 at dpr 1 and +0.0065 at dpr 2** and is the
charter's 0.003 clause missed, twice, on one cell. The cell is the reference at 0.9715 over a
backdrop at 0.9701: the rim's and the highlight's light are both clipping at white on the GPU tier
and their declines are therefore not independent there. It is named rather than absorbed.

**The five terms are not the mechanism.** With all five declined the residual on
`checkerboard__capsule-sm` is −0.0189 against a default of −0.0077, and on
`checkerboard__toolbar-group` −0.0236 against −0.0122: declining them makes the residual *worse*.
Whatever the −0.012 is, the lens, the rim, the highlight, the lift and the inner shadow are not
carrying it.

**The outer shadow is.** The last column, and the absolute levels behind it (`parts/attr-*.json`):

| cell, dpr 1 | GPU default | GPU no-outer-shadow | CSS default | CSS no-outer-shadow |
| --- | --- | --- | --- | --- |
| `light-solid__capsule-sm` | 0.97010 | **0.97010** | 0.96719 | 0.97184 |
| `light-solid__toolbar-group` | 0.97010 | **0.97010** | 0.96493 | 0.97184 |
| `checkerboard__capsule-sm` | 0.67640 | **0.67640** | 0.66873 | 0.67193 |
| `checkerboard__toolbar-group` | 0.67628 | **0.67628** | 0.66409 | 0.67367 |

**Declining the outer shadow moves the GPU tier's interior by exactly zero** — as the shader's
`liftEncoded · (1 − coverage)` and an occlusion drawn outside the coverage both say it must — **and
moves the CSS tier's by +0.0032 to +0.0096.** The tier darkens its own interior with its own
shadow, and with its neighbours'.

**The mechanism, stated.** `css-tier.ts` writes the outer shadow as `box-shadow` on the **host**
(line 1092, "It stays on the HOST: it paints outside the border box and below the ... children"),
and L1, L2 and L3 — the filter layers — are that host's children. A `backdrop-filter`'s backdrop is
everything painted below the element, and Chromium samples it over the region the kernel needs
rather than over the border box alone, so the shadow just outside the border box is inside the
blur's support. At σ 13.8 CSS px on a 44 px box that support is most of the surface. The renderer
composites its shadow after it samples, so it has no such path.

**The neighbours' term is that mechanism and nothing else.** The three-up's excess over the same
three circles at a non-merging gap, per configuration:

| configuration | ck 1x | photo 1x | ls 1x | ck 2x | photo 2x | ls 2x |
| --- | --- | --- | --- | --- | --- | --- |
| default | −0.0058 | −0.0049 | −0.0021 | −0.0061 | −0.0063 | −0.0024 |
| no-lens | −0.0059 | −0.0025 | −0.0021 | −0.0063 | −0.0034 | −0.0024 |
| no-rim | −0.0064 | −0.0050 | −0.0023 | −0.0066 | −0.0066 | −0.0021 |
| no-highlight | −0.0062 | −0.0048 | −0.0020 | −0.0063 | −0.0062 | −0.0031 |
| no-lift | −0.0058 | −0.0049 | −0.0021 | −0.0061 | −0.0063 | −0.0024 |
| no-inner-shadow | −0.0060 | −0.0048 | −0.0022 | −0.0066 | −0.0063 | −0.0022 |
| **no-outer-shadow** | **+0.0005** | **−0.0001** | **+0.0000** | **+0.0003** | **−0.0015** | **+0.0000** |
| all five declined | −0.0066 | −0.0025 | −0.0028 | −0.0067 | −0.0036 | −0.0025 |

**What the residual would be without it.** Whole component, declared region
(`parts/after-shadow.txt`):

| cell | dpr | default | outer shadow declined |
| --- | --- | --- | --- |
| `checkerboard__toolbar-group` | 1 | −0.0122 | **−0.0026** |
| `photo__toolbar-group` | 1 | −0.0150 | **−0.0086** |
| `light-solid__toolbar-group` | 1 | −0.0052 | **+0.0017** |
| `checkerboard__toolbar-group` | 2 | −0.0040 | **+0.0044** |
| `photo__toolbar-group` | 2 | −0.0101 | **−0.0043** |
| `light-solid__toolbar-group` | 2 | −0.0006 | **+0.0028** |

Three of the six land inside 0.005 and `photo__toolbar-group` at dpr 1 does not. The photo's
remainder is not the neighbours: the three-up at gap 40 reads −0.0084 with the shadow declined
against the group's −0.0086, so what is left there is a per-surface term over a structured backdrop
— M2's family. The photo's own structure is what carries it: at gap 40 the third circle sits over a
patch whose GPU-tier level is 0.7374 against the other two's 0.5871 and 0.5876, and that member alone
reads −0.0177 where its two siblings read −0.0063.

## 4. (c) — the stack, decomposed

Declared region; the whole-component rows also carry a native silhouette reading (§0) that agrees to
0.0001. `parts/stack.txt`.

| scene | dpr | part | GPU | CSS | CSS − GPU | px |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__stack-base` (220 × 130 alone) | 1 | whole | 0.6947 | 0.6949 | +0.0002 | 28 100 |
| `checkerboard__stack-over` (120 × 56 alone, raw backdrop) | 1 | whole | 0.6850 | 0.6893 | +0.0043 | 6 508 |
| `checkerboard__glass-over-glass` | 1 | whole | 0.7127 | 0.7084 | −0.0043 | 28 100 |
| | 1 | base, overlay excluded | 0.6593 | 0.6676 | +0.0083 | 21 592 |
| | 1 | overlay | 0.8899 | 0.8435 | **−0.0464** | 6 508 |
| `photo__stack-base` | 1 | whole | 0.6597 | 0.6547 | −0.0049 | 28 100 |
| `photo__stack-over` | 1 | whole | 0.6208 | 0.6262 | +0.0054 | 6 508 |
| `photo__glass-over-glass` | 1 | whole | 0.6861 | 0.6742 | −0.0119 | 28 100 |
| | 1 | base, overlay excluded | 0.6295 | 0.6313 | +0.0018 | 21 592 |
| | 1 | overlay | 0.8739 | 0.8166 | **−0.0572** | 6 508 |
| `checkerboard__glass-over-glass` | 2 | whole | 0.7181 | 0.7169 | −0.0013 | 112 416 |
| | 2 | overlay | 0.8923 | 0.8505 | **−0.0418** | 26 012 |
| `photo__glass-over-glass` | 2 | whole | 0.6865 | 0.6740 | −0.0126 | 112 416 |
| | 2 | overlay | 0.8740 | 0.8167 | **−0.0573** | 26 012 |

**The stack's residual is the overlay's, it is 0.04–0.06, and it is on the checkerboard as much as
on the photo.** The whole-cell number is small and backdrop-dependent only because the overlay is
23 % of the region and the base's own difference is positive and larger on the checkerboard
(+0.0083) than on the photo (+0.0018) — the charter's Grounding reading (iii), that the stack's
residual is "a backdrop-dependent term of the overlay's sampling", is an artefact of that dilution.

**It is not the overlay's material.** The same 120 × 56 r16 surface at the same offset, alone over
the raw backdrop, reads **+0.0043** on the checkerboard and **+0.0054** on the photo. The two tiers
agree about this overlay to half a hundredth of the residual it carries when stacked.

**It is not the shadow.** Under `no-outer-shadow` the overlay reads −0.0465 / −0.0570 against
−0.0464 / −0.0572 (§3's decline, `run-stack-decline.sh`) — a move of 0.0002. What the decline *does*
move is the base: the base excluding the overlay goes from +0.0083 to +0.0029 on the checkerboard,
because the OVERLAY's shadow falls on the base's body and the two tiers do not darken it equally.

**It is the route, and the reports name it.** On the GPU tier the overlay group resolves
`samplingBackend: "css-backdrop"`, `refraction: "approximate"`, `analysis: "none"`, and carries an
`unsampledMaterial` of `tint [1, 1, 1], tintAlpha 0.66496`. On the CSS tier the same group resolves
`css-backdrop`, `cssBody: "two-layer"`, `cssTint: "linear"` and `unsampledMaterial: null` — the
profile's converted material. The arithmetic closes on the renderer's side: a white lerp at α 0.665
over the base's own rendered level of 0.6951 gives 0.335 × 0.6951 + 0.665 = **0.898** against the
0.8899 measured, so the GPU tier's overlay is exactly the unsampled static material and nothing
else. The CSS tier's 0.8435 is that same base under the profile's tone-shaded tint (T ≈ 0.90 rather
than 1.0) at its own alpha. **The two tiers draw different materials on a DOM-sourced group by
design of the renderer's unsampled path, and that is where the 0.05 is.**

## 5. (e) — the native probe: the bed exists, the capture is stopped, the layer tree is not

**`./capture.sh probe`, run before anything else: `ScreenCaptureKit: BLOCKED`,
"사용자가 응용 프로그램, 윈도우, 디스플레이 캡처의 TCC를 거절함" — the grant is denied.** Per the
charter's stop the native capture half is not run and is reported for the user's hand: System
Settings → Privacy & Security → Screen & System Audio Recording, remove any existing entry for
`apps/reference-apple/build/VitreaReference.app` and re-add it (a recorded denial suppresses the
prompt), then the seven attested runs by W9's rule can be taken against the committed bed. The
harness binary is unchanged, so the grant does not need a rebuild.

**The bed is written and committed:** `apps/reference-apple/scenes-w18-probe.json`, W9's template,
canvas 320 × 200, backgrounds `checkerboard` and `photo` (existing kinds — nothing rebuilds),
components `capsule-sm` (44 × 44), `capsule-button`, `toolbar-group` (spacing 12),
`toolbar-group-wide` (spacing 40) and `glass-over-glass`, one profile
`apple-macos-26.5-1x-light-standard`, ten scenes. **Every scene is filed `recorded`**, which is a
reading of the charter's "a split by W9's rule (recorded for twins of holdout geometry)" that goes
one step further than the parenthetical: three of the five components are twins and are recorded by
that rule, and the two that are not — `capsule-sm` and `toolbar-group-wide` — are filed the same way
because X10 forbids fitting anything to this bed at all, so a split naming a cell `calibration`
would declare a fit phase the wave has ruled out. `compare`'s `recorded` set is opt-in twice over,
which is the custody these readings need.

**`dump-layers` needs no grant and was run, and it answers the canonical scene's own question.**
`VITREA_SCENES=…/scenes-w18-probe.json ./capture.sh dump-layers --settle 8` on
`checkerboard__toolbar-group__rest` and `checkerboard__toolbar-group-wide__rest`, into
`../probe/layer-dumps/`:

| what the layer tree declares | spacing 12 | spacing 40 |
| --- | --- | --- |
| `CABackdropLayer` bounds | 156 × 44 — the whole row | 212 × 44 — the whole row |
| `CASDFLayer` bounds | 156 × 44 | 212 × 44 |
| `CASDFElementLayer` count and size | 3 × (44 × 44) | 3 × (44 × 44) |
| each element's `operation` | `union` | `union` |
| `CASDFLayer.smoothness` | **12** | **40** |
| `CASDFLayer.mergeElements` | 0 | 0 |
| backdrop `scale` / `marginWidth` | 0.25 / 8.8 | 0.25 / 8.8 |

Three readings, none of them fitted to anything. **Apple's container samples ONE backdrop over the
whole row at both spacings** — a single `CABackdropLayer` at the row's bounding box, with three
union elements inside it — where vitrea's CSS tier draws three independent hosts each filtering its
own border box, and vitrea's renderer draws one texture over the row. **`GlassEffectContainer(spacing:)`
is the SDF's smooth-union `smoothness` verbatim**: 12 at spacing 12, 40 at spacing 40. So natively
the members' fields blend by a smoothness equal to the declared gap at *every* gap, and there is no
separation threshold at all — where vitrea's renderer stops unioning past `DEFAULT_GROUP_UNION`'s
separation of 16. That is a difference in kind between the two unions, it is the renderer's item
and not this tier's, and it is recorded here for the renderer's charter.

**What is still missing without the grant:** every native *pixel* — whether Apple's 44 × 44 circle
sits at its 120 × 44 capsule's level, what the merge does to the interior between and inside the
members, and the stack's native level for the renderer's overlay charter. Nothing in this document
is fitted to a native reading, so the separation, the attribution, the stack's decomposition and the
closed forms are all complete without it; what is deferred is the gap ledger's half.

## 6. (d) — the closed forms and their residuals

`closed-form.ts`. The attributed part with the largest share is the shadow the tier samples through
its own backdrop, and it is derived rather than tabulated: the page the tier's filter sees is

    E(P) = E(B) · Π_j (1 − a · C_j)

with `a` the alpha `cssTierShadowAlpha` writes and `C_j` the coverage of a CSS box shadow — host j's
border box grown by `spreadPx` (3.1), displaced by `offsetPx` (7.95) down, blurred by a Gaussian of
standard deviation `sigmaPx` (15.55; CSS Backgrounds 3 defines the blur RADIUS as twice that, which
`cssShadowBlurRadius` reconciles), and not painted inside the casting host's own border box. Every
one of those is the profile's own number and the script reads them out of `cssTierDeclarations`'
own declaration string rather than restating the rule. That page goes through the tier's own body —
L1 at `sharpSigmaCssPx`, L2 at `heavyStepSigmaCssPx` under the ramp's mask, the affine — and the
same page without the shadows through the same chain; the difference of the two means over the
surface's own shape is the prediction. The measurement is the CSS tier's default capture minus its
`no-outer-shadow` capture over that identical mask, so the affine's constants, the encode's offset
and the mask all cancel out of the comparison.

`parts/closed-form.txt` is all 64 rows. Per surface, dpr 1:

| surface | predicted | measured | residual |
| --- | --- | --- | --- |
| `checkerboard__capsule-sm` | −0.0031 | −0.0032 | **+0.0001** |
| `checkerboard__capsule-button` | −0.0026 | −0.0011 | −0.0014 |
| `checkerboard__toolbar-group-wide` items 0/1/2 | −0.0026 / −0.0032 / −0.0037 | −0.0029 / −0.0032 / −0.0037 | **+0.0002 / −0.0000 / +0.0000** |
| `checkerboard__toolbar-group` items 0/1/2 | −0.0045 / −0.0068 / −0.0054 | −0.0086 / −0.0123 / −0.0078 | **+0.0041 / +0.0056 / +0.0024** |
| `photo__toolbar-group-wide` items 0/1/2 | −0.0007 / −0.0007 / −0.0016 | −0.0013 / −0.0012 / −0.0026 | +0.0005 / +0.0005 / +0.0010 |
| `photo__toolbar-group` items 0/1/2 | −0.0012 / −0.0015 / −0.0021 | −0.0071 / −0.0077 / −0.0045 | **+0.0059 / +0.0062 / +0.0024** |
| `light-solid__capsule-sm` | −0.0017 | −0.0046 | +0.0030 |
| `light-solid__toolbar-group` items 0/1/2 | −0.0027 / −0.0037 / −0.0027 | −0.0075 / −0.0080 / −0.0052 | +0.0048 / +0.0044 / +0.0025 |

**The form carries the lone box and the non-merging three-up and misses the merging one.** On every
surface with no close neighbour the residual is at most 0.0014 and usually under 0.0005, at both
scales; on the three circles at gap 40 it is at most 0.0004. At gap 12 it under-predicts by +0.0024
to +0.0062, and at dpr 2 by up to +0.0061 — **a residual over 0.003 on both `toolbar-group`
cells, which the charter names as a `[parent-impact]` on the acceptance** (§7). The model puts a
sibling's shadow into the neighbour's sampled page and clamps its blur at the canvas; what it does
not carry is Chromium's own paint order for three siblings that each establish a stacking context,
and the measured asymmetry says that is where the miss is — the third member's residual is half the
second's on every backdrop, and a symmetric model cannot produce that.

**The largest residual is +0.0274, on `photo__glass-over-glass` surface 0 (the base) at dpr 2**, and
it is a modelling mismatch rather than a mechanism error: on the stack, the overlay's shadow lands
on the base's *rendered body* and is composited over it, not sampled into its backdrop, and the
script models only the sampled path. The stack's own residual is not this term at all (§4).

**M1's candidates, evaluated.** The charter names three terms the tier might carry as a function of
the span where the renderer integrates over the box, and two of the three already carry the box:
`interiorBandLight` and `interiorShadowKeep` both take the surface's own width, height and radius
through the co-area integral (`root.ts` builds an `InteriorSurfaceGeometry` from the measured bounds
and `record.radii[0]`). The third, `scatterRampAreaMean`, takes the extents and ignores the corners.
Its error against the exact co-area value over the rounded rectangle, on the device grid, is
**+0.0000 on the 44 × 44 circle** (0.3082 against 0.3082 — the ramp's reach is short enough that the
corner correction is below the fourth decimal), −0.0002 on the 120 × 44 capsule, −0.0005 on the
220 × 130 base at dpr 1 and −0.0017 / −0.0013 / −0.0016 on the three boxes at dpr 2. **The ramp's
rectangle form is not the box term.** Nothing in M1's candidate list carries a share worth the
−0.007 the box costs; §3's declines put roughly half of that on the shadow and leave the rest with
the body over a structured backdrop.

## 7. (g) — the cost, and (h) the decisions, and what is `[parent-impact]`

### (g) the cost

**The closure this evidence points at adds no element and no primitive, so no cost run was made.**
The mechanism is that the tier's own `box-shadow` is inside its own `backdrop-filter`'s sampled
region. Two shapes of fix follow and neither grows the element model: compensating the sampled
shadow inside the affine the tier already writes (`CssTierInterior`'s three numbers, one of which
moves), or moving the shadow so the filter does not sample it — which is a change to which of the
four elements the tier already creates carries `box-shadow`, not a fifth. A compensation inside the
affine is a mean correction against a spatially structured perturbation and will leave a signature
the level does not show, which is G1's to measure; if G1 finds it needs a real fifth element, the
knee has to be re-measured on W16 G0's harness and that is a cost run this spike did not need to
make.

### (h) the decisions, against the numbers

The user executed Decision Log 1 at the recommendations (charter `d7fd283`) while this spike ran.
Every answer is supported by what was measured, and one of them is now load-bearing in a way the
recommendation did not anticipate.

- **q0 — the target is the renderer's rendered interior, without qualification. Supported, and the
  evidence is stronger than the recommendation's.** The mechanism the tier is being moved off is not
  a difference of tuning, it is the tier sampling a thing it draws. On the three-up the tier sits
  nearer Apple today (+0.043 against the renderer's +0.055 on the checkerboard at 1x) *because* it
  darkens itself by 0.0096 with its own shadow, which is not a fidelity property and would move
  under any change of gap, neighbour count or shadow constant.
- **q1 — the native probe at 1x from this machine. Supported and blocked.** The bed is committed;
  the grant is denied (§5). `dump-layers` recovered the container's declared merge without a grant
  and it is the more decisive of the two readings the probe was chartered for.
- **q2 — the stack in scope as a second mechanism family, and a part that is the renderer's overlay
  route is named and left. Supported, and it is the whole of the stack's term** (§4). The tier's own
  share of `glass-over-glass` is +0.008 / +0.002 on the base and +0.004 / +0.005 on the overlay's
  material; there is nothing else for G1 to close there.
- **q3 — a part attributed to the renderer stops the wave for a re-decision. Called, once** (item 1
  below). The union is not that part: the renderer's interior is flat across the whole spacing
  sweep.
- **q4 — the fold's clause at 0.01. Not measured here.** The fold was not captured (this spike is
  the two light-standard profiles) and nothing found argues against the clause; the mechanism §3
  names is present under every profile, since the tier draws a shadow under reduced transparency
  too and `reducedTransparencyOcclusion` is 0.197. G1 owns the measurement.
- **q5 — a level that costs structure past S2 goes to the user. Not called by this evidence.** The
  closure removes light the tier is adding to nothing; §6's form predicts the removal within 0.0014
  everywhere the model is complete, and no structure metric was moved by any capture here.

### `[parent-impact]`

1. **The stack's residual is the renderer's, not the tier's.** On a DOM-sourced group the renderer
   draws an unsampled material — `tint [1,1,1]`, `tintAlpha 0.66496`, `analysis: "none"` — and the
   CSS tier draws the profile's converted one, and the 0.042–0.057 on the overlay is the difference
   between those two materials over the same base. The overlay alone over a raw backdrop reads
   +0.004 / +0.005, so this is not a material gap; it is the renderer's unsampled path. Under q3(a)
   and Design's third binding rule this stops the wave for the parent's re-decision: **the tier's own
   share of `photo__glass-over-glass` is already inside 0.005 and there is nothing for G1 to close
   on the stack** — S4's stack clause has to be restated against the tier's share or the renderer's
   part chartered where the goldens' isolation proof lives.
2. **The closed form leaves a residual over 0.003 on both `toolbar-group` cells.** §6: +0.0024 to
   +0.0062 per surface at the merging gap, at both scales, where the same form is exact to 0.0004 at
   the non-merging one. The mechanism is named and its length scale measured; what is not derived is
   the last third of the neighbours' term. G1 either completes the model (Chromium's paint order for
   three sibling stacking contexts, which is a measurable thing rather than a fitted one) or carries
   that part as a bounded residual with its geometry, per K5.
3. **The charter's mechanism list does not contain the mechanism.** M1, M2, M3 and M4 are all
   about what the tier computes; the owner is what the tier *paints* and then re-reads. Design's
   advisory M3 expects "a three-up minus lone-circle difference on one tier only, and which tier
   names the owner" — that part is confirmed exactly, and the owner is the tier — but M1's candidate
   terms carry no share (§6) and M2's expected signature (zero on the solid) is contradicted: the
   solid carries −0.0046 of shadow on the lone circle, its largest single share. G1's design section
   should be rewritten on §3 rather than refined on M1.
4. **`photo__toolbar-group` at dpr 1 does not reach 0.005 on this mechanism alone.** With the shadow
   declined it reads −0.0086, and the three-up at gap 40 reads −0.0084 under the same decline, so
   what remains is a per-surface term over a structured backdrop and not the neighbours'. S4's clause
   on that cell needs a second mechanism or a restated bound; G1 should not discover this at its dry
   run.

Two smaller findings recorded rather than raised. `light-solid__capsule-button` misses the
superposition clause by +0.0059 and +0.0065 (§3) because the rim's and the highlight's light clip at
white on that cell. And at dpr 2 the `checkerboard__toolbar-group` residual is small by cancellation
— a box term of −0.0068 and a neighbours' term of −0.0062 against a capsule at +0.0094 — so a fix
that removes only the shadow moves that cell from −0.0040 to **+0.0044**, which is inside 0.005 but
on the other side of zero and is worth knowing before S5 is read.

## 8. What is in this directory

| file | what it is |
| --- | --- |
| `run-separation.sh` | §2's and §4's captures: eighteen scratch scenes, both tiers, both scales |
| `run-spacing.sh` | §2's spacing sweep: the three circles at eight gaps |
| `make-profiles.mjs`, `profiles/` | §3's seven scratch profile documents and why each field stands its term down |
| `run-attribution.sh` | §3's 32 runs, one at a time, all to scratch |
| `run-stack-decline.sh` | §4's stack under `no-outer-shadow` |
| `separation.ts` | the reader: both masks, per surface, the annulus |
| `x4-recovery.ts`, `parts/x4-recovery.json` | §1's contract X4 under every mask the findings use |
| `attribution.py`, `parts/attribution.txt`, `parts/attribution-neighbour.txt` | §3's tables |
| `closed-form.ts`, `closed-form-table.py`, `parts/closed-form.{json,txt}` | §6's derivation and its residuals |
| `tables.py`, `parts/{separation,annulus,spacing,stack,after-shadow}.txt` | §2's and §4's tables |
| `parts/separation-*.json`, `parts/spacing-*.json`, `parts/attr-*.json`, `parts/stack-*.json` | every reading, per cell and per surface |
| `../probe/layer-dumps/` | §5's two native layer dumps (no TCC grant needed) |
