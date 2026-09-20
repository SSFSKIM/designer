# The strip a thin σ leaves undrawn — W30 G3's blocking finding

**Status: a renderer defect, reproducible on 0.19.0's own shipped document with one
constant changed, found by this child's fit and not caused by it.** It breaks an
adopted bound (W20's declaration conformance, 170 texture cells) and it is visible
to the eye on the dark bed's capsule. Claims §5.159 §6 records it; the Decision Log
entry it needs is drafted there.

## What it is

At a casting span of 44 CSS px the fitted σ law draws σ = 2.13 where 0.19.0 draws
11.0. At that width the optics pass leaves a horizontal strip **inside the
surface** undrawn: the composite shows the page through it, and the
declaration-conformance capture — the same scene over a transparent page — shows
alpha 0 there.

On `checkerboard__capsule-button__rest` at `apple-macos-27.0-1x-dark-standard-glass0.5`
the strip is eight rows of the capsule's lower half, full width except the two
caps, and it reads as a row of white checker squares punched through the frosted
body. `results/2026-09-20-w30-g3-operators/sheets/1x-dark-standard-glass0.5__active.png`
carries it, first row.

## How to reproduce it, with no W30 leaf involved

Take the macOS 27 light or dark document **as 0.19.0 ships it** and change one
constant that has existed since W14:

```jsonc
"outerShadow": { "sigmaPx": 8 }   // 11 draws clean; 8 does not
```

then capture one scene:

```bash
npx tsx cli/compare.ts --profile apple-macos-27.0-1x-light-standard-glass0.5 \
  --material-profile <that document> --receded-profile <its recede> \
  --renderer webgpu --set calibration --scene checkerboard__capsule-button__rest \
  --alpha --write-partial --out-matrix /tmp/probe.json
```

`shape.silhouetteAreaWeb` reads **4872** at σ 11 and **2715** at σ 8, against a
declared region of 4872; `shape.silhouetteHolesWeb` reads 0 and 9. **No leaf this
wave added is set in that document**, so the defect is not W30's: it is a latent
one that no shipped material had ever reached, because every σ the project has
shipped is above 10 CSS px.

## What it is a function of, measured

Five one-scene captures, each changing one constant of the sealed light document
(`/tmp/.../bisect-alpha.sh`, the readings in this table taken off the alpha
capture's own coverage per row; the capsule occupies rows 78…121 of a 200-row
canvas):

| document | strip, canvas rows | rows |
| --- | --- | ---: |
| 0.19.0, σ 11 | none | 0 |
| σ 8, flat | 95…121 | 27 |
| σ 4, flat | 83…121 | 39 |
| the fitted law (σ(44) = 2.13) | 104…111 | 8 |
| the fitted law, `offsetPx` 0 | 96…103 | 8 |
| the fitted law, `spreadPx` 0 | 107…108 | 2 |
| the fitted law, `thinOcclusionMid` 0.6 | 104…111 | 8 |
| the fitted law, `thinOcclusionMid` 0 | 104…111 | 8 |

Three readings of that table matter.

**It is not the shadow's AMPLITUDE.** Zeroing `thinOcclusionMid` — which takes the
shadow's occlusion over a mid backdrop to exactly 0, and with it `shadowAlpha` —
leaves the strip byte for byte where it was. Nothing the shadow paints is
involved.

**It is the shadow's GEOMETRY, through the group field rect.** `offsetPx` and
`spreadPx` enter `outerShadowReachPx` and nothing else the body reads, and the
rect is `groupFieldRect(surfaces, union, undefined, shadowReachPx)`. Zeroing the
offset moves the strip up by exactly eight rows, which is `offsetPx` 7.95 rounded;
zeroing the spread shortens it from eight rows to two. Across all three the
strip's BOTTOM edge sits **24 CSS px above the rect's own bottom edge** — 135−111,
127−103, 132−108 — which is a constant in canvas px and not in the rect's uv.

**It is the geometry of the CASTER, not of the pixel.** The strip appears on
`capsule-button` (120×44) and on `toolbar-group` (three 44×44 members) and on no
`rrect` at any span, which is what makes the 170 W20 failures exactly the
span-44 texture cells of all six profiles.

## What it costs, and what it does not

| reading | before | after |
| --- | ---: | ---: |
| W20 declaration conformance, texture cells outside contour ≤ 1 px and IoU ≥ 0.99 | **0** | **170** |
| the conditioning predicate's exclusions | 68 | **83** (all fifteen new ones span-44 texture cells) |
| `checkerboard__capsule-button__rest` 1x light, `ssimMean` | 0.98217 | 0.97826 |
| `checkerboard__capsule-button__rest` 1x light, `oklabDeltaEP95` | 0.02127 | 0.02395 |

The perceptual rows barely move, which is worth stating plainly rather than
taking as comfort: SSIM over the whole cell is dominated by the interior and by
the backdrop outside it, and a strip eight rows tall inside a 44-row surface does
not move it far. **The bound that catches this is the one that reads the drawn
coverage**, which is what W20 is for, and it caught it on 170 cells.
