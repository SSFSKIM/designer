# W12 G1 — the corner field (2026-09-03)

Method (`g1b-corners.py`, `corners/corners.json`, crops `corners/<comp>-<scale>x-<corner>.png` at 10× per
CSS px: native | vitrea webgpu | radial prediction on the native interior's σ | radial prediction on vitrea's
own two-component body). The radial prediction is the landed law, `D(u) = L·1.6·(1 − u/L)²` along the exact
SDF normal (L = 20.8 CSS px on both cells), sampling the checkerboard plate blurred at the native
interior's single-Gaussian σ with the native's own (a, t). RMS in linear luminance over the band
(0.5 < u ≤ L + 4) inside a (2r + 8)-px square at each corner, and inside the same square centred on the
straight top edge for reference. Sweeps vary only what a straight-edge law cannot fix at a corner: the
magnitude S (0.6…1.6 × the landed 33.3 px) and the extent L (0.75…1.5 × 20.8).

Interior fits used for the prediction (σ CSS px / a / t): `rrect-md` 1x native 1.25 / 0.556 / 0.246, 2x
native 3.0 / 0.473 / 0.413; `rrect-lg` 1x native 1.0 / 0.659 / 0.093, 2x native 6.0 / 0.438 / 0.534
(the 2x large-span σ is at the identifiable limit of a pitch-16 cell — see `g1-body-2x.md`). Vitrea's
body: k 0.93 on the (1.25, 10) pair at the inset interior, a/t 0.573/0.239 (md), 0.629/0.129 (lg).

## 1. Band RMS per corner

| cell | box | native − vitrea | native − prediction | vitrea − prediction | vitrea − prediction on vitrea's body |
| --- | --- | --- | --- | --- | --- |
| `rrect-md` 1x | top-left | 0.081 | 0.079 | 0.022 | 0.016 |
| | top-right | 0.081 | 0.081 | 0.022 | 0.013 |
| | bottom-left | 0.081 | 0.083 | 0.020 | 0.012 |
| | bottom-right | 0.087 | 0.088 | 0.018 | 0.010 |
| | *top edge* | 0.064 | 0.059 | 0.018 | 0.006 |
| `rrect-md` 2x | top-left | 0.087 | 0.097 | 0.039 | 0.024 |
| | top-right | 0.086 | 0.094 | 0.043 | 0.020 |
| | bottom-left | 0.095 | 0.095 | 0.048 | 0.017 |
| | bottom-right | 0.101 | 0.102 | 0.044 | 0.012 |
| | *top edge* | 0.065 | 0.072 | 0.035 | 0.019 |
| `rrect-lg` 1x | top-left | 0.053 | 0.054 | 0.025 | 0.020 |
| | top-right | 0.054 | 0.054 | 0.020 | 0.011 |
| | bottom-left | 0.050 | 0.051 | 0.021 | 0.013 |
| | bottom-right | 0.050 | 0.051 | 0.021 | 0.011 |
| | *top edge* | 0.046 | 0.044 | 0.017 | 0.005 |
| `rrect-lg` 2x | top-left | 0.063 | 0.065 | 0.033 | 0.027 |
| | top-right | 0.068 | 0.063 | 0.024 | 0.018 |
| | bottom-left | 0.073 | 0.064 | 0.028 | 0.017 |
| | bottom-right | 0.077 | 0.068 | 0.021 | 0.011 |
| | *top edge* | 0.042 | 0.046 | 0.023 | 0.018 |

**Vitrea's corners are the radial law.** Against the prediction on its own body vitrea reads 0.010–0.027
at every corner, within 0.01–0.02 of its straight edge (0.005–0.019); the residual that is left is the
prediction's single-σ stand-in for the two-component body, not the geometry. The instrument therefore
sees a radial corner when there is one.

**The native corner is not the radial law, and the shortfall is the same one the straight edge has.**
Native-vs-prediction at the corners (0.079–0.102 md, 0.051–0.068 lg) is 1.3–1.5× the straight edge's
(0.059–0.072 md, 0.044–0.046 lg) — the law misses the edge by nearly as much as it misses the corner,
so most of the corner's loss is the band's shape, not a corner-specific term. The prediction (third
panel of every crop) looks like vitrea's second panel — a soft compression — while the native corner
shows a bright arc, a dark ring just inside it, and a large crisp lobe that is the reversed image of the
cell outside the corner.

## 2. Magnitude and extent sweeps at the corner (native − prediction, band RMS)

| cell | box | S × 0.6 / 0.8 / **1.0** / 1.2 / 1.4 / 1.6 | L × 0.75 / **1.0** / 1.25 / 1.5 | joint best (L×, S×) |
| --- | --- | --- | --- | --- |
| `rrect-md` 1x | top-left | 0.102 / 0.081 / **0.079** / 0.093 / 0.109 / 0.122 | 0.103 / **0.079** / 0.126 / 0.138 | (1.0, 1.0) 0.079 |
| | top-right | 0.099 / 0.083 / **0.081** / 0.089 / 0.105 / 0.121 | 0.105 / **0.081** / 0.127 / 0.139 | (1.0, 1.0) 0.081 |
| | bottom-left | 0.089 / 0.081 / **0.083** / 0.084 / 0.092 / 0.096 | 0.106 / **0.083** / 0.083 / 0.084 | (1.25, 0.6) 0.080 |
| | bottom-right | 0.091 / 0.082 / **0.088** / 0.090 / 0.096 / 0.098 | 0.110 / **0.088** / 0.088 / 0.090 | (1.25, 0.6) 0.081 |
| | *top edge* | 0.108 / 0.075 / **0.059** / 0.078 / 0.106 / 0.130 | 0.083 / **0.059** / 0.149 / 0.169 | (0.75, 1.4) 0.042 |
| `rrect-md` 2x | top-left | 0.108 / 0.094 / **0.097** / 0.106 / 0.127 / 0.141 | 0.114 / **0.097** / 0.133 / 0.162 | (1.0, 0.8) 0.094 |
| | top-right | 0.104 / 0.092 / **0.094** / 0.099 / 0.120 / 0.138 | 0.113 / **0.094** / 0.130 / 0.159 | (1.25, 0.6) 0.092 |
| | bottom-left | 0.100 / 0.100 / **0.095** / 0.103 / 0.110 / 0.117 | 0.119 / **0.095** / 0.096 / 0.101 | (1.25, 0.6) 0.092 |
| | bottom-right | 0.102 / 0.103 / **0.102** / 0.110 / 0.115 / 0.120 | 0.125 / **0.102** / 0.103 / 0.108 | (1.25, 0.6) 0.094 |
| | *top edge* | 0.115 / 0.080 / **0.072** / 0.074 / 0.107 / 0.138 | 0.092 / **0.072** / 0.135 / 0.180 | (0.75, 1.4) 0.047 |
| `rrect-lg` 1x | top-left | 0.054 / 0.054 / **0.054** / 0.056 / 0.061 / 0.068 | 0.057 / **0.054** / 0.070 / 0.074 | (0.75, 1.4) 0.051 |
| | top-right | 0.058 / 0.055 / **0.054** / 0.058 / 0.064 / 0.070 | 0.057 / **0.054** / 0.070 / 0.075 | (1.0, 1.0) 0.054 |
| | bottom-left | 0.052 / 0.051 / **0.051** / 0.053 / 0.058 / 0.059 | 0.055 / **0.051** / 0.051 / 0.058 | (1.25, 0.8) 0.050 |
| | bottom-right | 0.056 / 0.056 / **0.051** / 0.053 / 0.058 / 0.064 | 0.055 / **0.051** / 0.051 / 0.058 | (1.0, 1.0) 0.051 |
| | *top edge* | 0.061 / 0.050 / **0.044** / 0.051 / 0.063 / 0.073 | 0.052 / **0.044** / 0.083 / 0.088 | (0.75, 1.4) 0.038 |
| `rrect-lg` 2x | top-left | 0.066 / 0.064 / **0.065** / 0.065 / 0.071 / 0.081 | 0.070 / **0.065** / 0.075 / 0.091 | (0.75, 1.4) 0.062 |
| | top-right | 0.068 / 0.064 / **0.063** / 0.066 / 0.074 / 0.082 | 0.069 / **0.063** / 0.074 / 0.092 | (1.0, 1.0) 0.063 |
| | bottom-left | 0.073 / 0.068 / **0.064** / 0.070 / 0.076 / 0.084 | 0.076 / **0.064** / 0.067 / 0.082 | (1.0, 1.0) 0.064 |
| | bottom-right | 0.081 / 0.076 / **0.068** / 0.073 / 0.082 / 0.093 | 0.081 / **0.068** / 0.071 / 0.086 | (1.0, 1.0) 0.068 |
| | *top edge* | 0.064 / 0.052 / **0.046** / 0.045 / 0.059 / 0.076 | 0.053 / **0.046** / 0.068 / 0.088 | (0.75, 1.4) 0.030 |

**No corner wants its own magnitude.** The S sweep at every corner is flat to ±0.005 around the landed
value, and the joint (L, S) search never buys more than 0.009 (md 2x top-right, 0.094 → 0.092; lg
1x top-left 0.054 → 0.051). A radial law with a different magnitude or extent at the corner does not
reproduce the native lobe; the corner's residual is the same shape failure as the edge's, wrapped
radially.

**Two things the sweep does say.**

1. The straight edge prefers a shorter, stronger lens than the corner does: on every top-edge box the
   joint best is (L × 0.75, S × 1.4) at 0.030–0.047 against 0.044–0.072 at the landed pair, while the
   corners sit at the landed pair or a marginally deeper, weaker one. If the edge is refitted to (L 15.6,
   S 46.6) the corner would be over-driven — the field is not one radial profile at both.
2. **Top and bottom differ.** On `rrect-md` the top corners' S minimum is at 1.0× and the bottom corners'
   at 0.6–0.8× (joint bests (1.25, 0.6)), at both scales; the native-vs-vitrea band RMS is 0.081/0.081
   top against 0.081/0.087 bottom at 1x and 0.087/0.086 against 0.095/0.101 at 2x. The bottom corners
   carry less displacement, or something the radial model reads as less displacement (the rim's light
   sits top-left — `g1-rim.md` §2 — and the lower band is where the reference's outer shadow lands).
   Recorded, not fitted.

## 3. By eye (the crops)

`corners/rrect-md-2x-top-left.png`: native — bright arc 1 CSS px wide, a darker ring 1–2 px inside it
following the arc, then a large crisp lobe whose inner boundary is sharp; the lobe is the black outside
cell, reversed and pulled around the corner. Vitrea — bright arc, then a soft grey compression with no
ring and no sharp inner boundary. Prediction (native σ 3, S 33) — a soft compression like vitrea's with
slightly more structure: the shape of the landed law is what vitrea draws; the native is a different
shape. `rrect-md-1x-top-left.png` reads the same at half the size, and the native's lobe is crisper
still (interior σ 1.25). `rrect-lg-2x-bottom-right.png`: the native lobe is a clean disc with the
outside white cell inside it; both predictions are diffuse.

## 4. Numbers to carry

- Vitrea corner = radial law: band RMS 0.010–0.027 against its own-body prediction (md 1x: 0.010–0.016).
- Native corner ≠ radial law at any S 0.6–1.6× or L 0.75–1.5×: best 0.079–0.094 (md), 0.050–0.068
  (lg); straight edge at the landed pair 0.044–0.072, at its own best (0.75 L, 1.4 S) 0.030–0.047.
- Corner/edge residual ratio under the landed law: 1.3–1.5 (md), 1.1–1.5 (lg).
- Bottom corners prefer 0.6–0.8× S; top corners 1.0×. Difference in RMS terms ≤ 0.009.
