# W12 G1 — the small spans' bands (2026-09-03)

Method (`g1b-small.py`, `small.json`, `small.out`): W11c's per-shell radial fit, `Y = a + t·G_σ(P)(q −
D·n̂)`, on 0.5-px shells with D on a 0.5-px grid and σ ∈ {0.5…8}, native at 1x pitch 16 (canonical),
1x pitch 32 (the W9 probe), 2x pitch 16 (canonical), and vitrea webgpu at both scales, pitch 16.
Lens depths from the landed law: `rrect-sm` L = 8.0 (span 32 → `sizeThickness` 0, gain 1, 8 × 1 = 8;
the span/2 clamp of 16 is not reached), `capsule-button` L = 9.18 (span 44, gain 1.148), `rrect-md`
L = 20.8. Landed magnitudes S = 1.6 L: 12.8 / 14.7 / 33.3. The shell fit is the same crude instrument
§5.43 used — a single shift per shell — so the near-contour rows (u < 1.5, where it reads σ 8 and
negative t) are not readings; from u ≈ 2 in, the D column is a serviceable radial mean.

## 1. D(u), CSS px

| u | `rrect-sm` native 1x p16 | native 1x p32 | native 2x p16 | vitrea 1x | vitrea 2x | landed law (L 8, S 12.8) |
| --- | --- | --- | --- | --- | --- | --- |
| 1.5 | 10.5 | 10.5 | 12.0 | 8.5 | 9.0 | 8.5 |
| 2 | 9.5 | 10.0 | 8.0 | 7.5 | 7.5 | 7.2 |
| 2.5 | 5.0 | 4.5 | 7.0 | 5.5 | 6.0 | 6.1 |
| 3 | 5.0 | 4.5 | 7.0 | 5.0 | 5.0 | 5.0 |
| 3.5 | 4.0 | 5.0 | 5.5 | 4.5 | 4.5 | 4.1 |
| 4 | 4.0 | 4.5 | 3.0 | 4.0 | 4.0 | 3.2 |
| 4.5 | 3.0 | 4.0 | 1.5 | 3.5 | 3.0 | 2.5 |
| 5 | 3.0 | 3.5 | 1.0 | 3.0 | 2.0 | 1.8 |
| 5.5 | 2.0 | 3.5 | 0.5 | 1.5 | 2.0 | 1.3 |
| 6 | 2.0 | 3.5 | 0.0 | 1.5 | 0.5 | 0.8 |
| 6.5 | 1.0 | 2.5 | −0.5 | 0.5 | 0.5 | 0.5 |
| 7 | 1.0 | 2.5 | −1.0 | 0.5 | 0.5 | 0.2 |
| 8 | 0.0 | 2.0 | −2.0 | 0.5 | 0.0 | 0 |
| 9 | −1.0 | 1.0 | 1.5 | −0.5 | −0.5 | 0 |
| 9.5 | −2.0 | 0.0 | 1.5 | 0 | −0.5 | 0 |

| u | `capsule-button` native 1x p16 | native 1x p32 | native 2x p16 | vitrea 1x | vitrea 2x | landed law (L 9.18, S 14.7) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 24.0 | 18.5 | 24.0 | 16.0 | 16.0 | 11.7 |
| 1.5 | 18.0 | 18.0 | 19.0 | 10.0 (σ 8) | 10.0 (σ 8) | 10.3 |
| 2 | 17.5 | 17.5 | 16.0 | 8.5 (σ 8) | 8.0 (σ 8) | 9.0 |
| 2.5 | 12.5 | 13.0 | 13.0 | 5.5 (σ 8) | 6.5 (σ 8) | 7.8 |
| 3 | 11.0 | 11.0 | 11.0 | 5.0 | 5.0 | 6.7 |
| 3.5 | 10.0 | 9.5 | 9.5 | 3.5 | 4.0 | 5.6 |
| 4 | 8.0 | 8.0 | 8.0 | 1.0 | 1.5 | 4.7 |
| 4.5 | 7.0 | 6.5 | 7.0 | 1.0 | 1.0 | 3.8 |
| 5 | 6.0 | 6.0 | 6.0 | 1.0 | 0.5 | 3.0 |
| 5.5 | 5.0 | 5.0 | 5.0 | 0.5 | 0.5 | 2.4 |
| 6 | 4.5 | 4.0 | 4.5 | 0 | 0.5 | 1.8 |
| 6.5 | 3.0 | 3.5 | 3.5 | 0.5 | 0.5 | 1.3 |
| 7 | 3.0 | 2.5 | 2.5 | 0 | 0 | 0.9 |
| 7.5 | 2.0 | 2.0 | 2.0 | 0 | 0 | 0.5 |
| 8 | 1.5 | 1.5 | 1.5 | 0 | 0 | 0.2 |
| 8.5 | 1.0 | 1.0 | 1.0 | 0 | 0 | 0.1 |
| 9 | 1.0 | 0.5 | 0.5 | 0 | 0 | 0 |
| 9.5 | 0.5 | 0.5 | 0.5 | 0 | 0 | 0 |
| 10 | 0.5 | 0.5 | 0.5 | 0 | 0 | 0 |
| 10.5 | 0 | 0 | 0 | 0 | 0 | 0 |

For the normalised comparison, `rrect-md` under the same instrument (native, 1x pitch 32 / 2x pitch
16): u 4: 32 / 25; 6: 20 / 18; 8: 13 / 12; 10: 9 / 8; 12: 6 / 6; 14: 3 / 3; 16: 2 / 2; 18: 1 / 0;
19–20: 0 / 0 — §5.43's 33·(1 − u/20)² at both scales.

## 2. What the tables say

**The capsule's band is the same at pitch 16, pitch 32 and 2x** — the three native columns agree to
±1 px at every shell, so the reading is the material's, not the pattern's or the display's. It is
**1.7–1.9× the landed law from u 2 to 6 and reaches 10.5 px in where the law ends at 9.2**: D(2) =
17.5 against 9.0, D(4) = 8.0 against 4.7, D(6) = 4.5 against 1.8, D(8) = 1.5 against 0.2. A quadratic
through it is close to 20·(1 − u/11)² (13.4 / 8.1 / 4.1 / 1.5 at u 2 / 4 / 6 / 8) — §5.43 §4's
"L 11, S 20" — except at u ≤ 2 where the native is steeper (17.5). Vitrea's capsule reads the law
from u 3 in and the shell fit fails on it at u ≤ 2.5 (σ 8, negative level: the heavy-component share
at span 44 is 0.4, and a single-σ shift cannot describe a two-component sample under a fold).

**`rrect-sm` is near the law at 1x and weaker at 2x.** 1x: D(2) 9.5–10 against 7.2, D(4) 4–4.5
against 3.2, D(6) 2–3.5 against 0.8, extent 8 (pitch 16) to 9.5 (pitch 32) against 8. 2x: D(2) 8.0,
D(4) 3.0, D(6) 0, extent ≈ 5.5–6 — shorter than at 1x by 2–3 px, the only cell here whose band differs
between the scales. Vitrea reads the law at both scales within 1 px from u 2.5 in.

**Scaled by lens depth, the bands do not collapse.** D/L at u/L ≈ 0.25: `rrect-sm` 1.19 (1x) / 1.0 (2x),
`capsule-button` 1.9, `rrect-md` 1.4 (u 5.2: D ≈ 29); the landed law gives 0.9 for all three. At u/L
≈ 0.5: 0.5 / 0.19, 0.87, 0.38 (law 0.4). At u/L ≈ 0.75: 0.25–0.44 / 0, 0.33, 0.1 (law 0.1). The
measured extents are 8–9.5 / 10.5 / 20 CSS px for spans 32 / 44 / 96, against the law's 8 / 9.2 / 20.8:
the extent follows the size law's thickness curve to within 15%, but the magnitude over the extent
does not — S/L reads ≈ 1.2 (sm), ≈ 1.9 (capsule), 1.6 (md and the larger spans, §5.43). The capsule
is the outlier at both ends: a deeper and a proportionally stronger lens than its span gives it under
`sizeThickness`, on a shape whose corner radius (22) is its half-height — the one cell whose contour is
all corner.

**By the eye these are the same lobes at smaller size**: the capsule's band at 2x (sheet
`g1-2x.png`, row 2) shows the reversed cells and the sharp inner fold like `rrect-md`'s at 2/5 the
depth; vitrea's shows the soft compression.

## 3. Numbers to carry

- Capsule: D(2 / 4 / 6 / 8) = 17.5 / 8.0 / 4.5 / 1.5 CSS px, extent 10.5, at pitch 16, 32 and 2x alike;
  law 9.0 / 4.7 / 1.8 / 0.2, extent 9.2.
- `rrect-sm`: D(2 / 4 / 6) = 9.5 / 4.0 / 2.0 (1x p16), 10 / 4.5 / 3.5 (1x p32), 8.0 / 3.0 / 0 (2x);
  law 7.2 / 3.2 / 0.8.
- Vitrea reads the landed law on both cells from u ≈ 2.5–3 in; nearer the contour the single-shift
  instrument cannot read vitrea's two-component sample.
