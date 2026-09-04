# W16 G1 — the dry run (parent's record)

The branch `w16-g1-two-layer` (`349d2c6`, the worker's G1: the element model of Decision Log 2
(a), the raster mask, the effective-width conversion 1.380 / 1.485, the linear-light reference
filter as the default on Chromium) captured by the harness into a scratch matrix beside the W15
bed (`c00f89e`), the holdout unread (contract X8 waits for the frozen configuration). The referee
is `verify-dry.py` (this directory); its reports are kept beside this file.

## 1. The first dry run — the linear-light form as built (`dry1-linear.verify.txt`)

Twelve runs: the GPU tier on all six profiles with the holdout (its byte identity is not a
holdout read — the tier is bound unchanged), the CSS tier on all six with calibration and
validation. **S1 met**: 115 of 115 GPU captures byte-identical to the bed, every GPU row exact.
**S2 fired** at 2x: `checkerboard__rrect-md` 0.9174 → 0.9150 (under its floor 0.9159),
`rrect-ml` 0.8808 → 0.8774 (above its floor, below the bed). **S3 fired** at 1x: the interior
spread OVERSHOOTS native on `rrect-sm` (+0.0137), the capsule (+0.0170), the toolbar
(+0.0130) and `rrect-ml` (+0.0179); `rrect-md` is inside (+0.0065). S4, S5, S6 met; the
cross-tier ΔE over the fitted sets fell on every profile (1x light 0.00760 → 0.00718).

## 2. The `blur()` control — the same branch with `referenceFilterInBackdrop` off (`dry1-control.verify.txt`)

The CSS tier on the two light-standard profiles only, calibration and validation; the only
difference from §1 is the blur's colour space. At 1x every checkerboard `ssimMean` is higher
than §1's by 0.004–0.008 (`rrect-md` 0.9096, `rrect-ml` 0.8676) and the level sits UNDER native
by 0.04–0.06 (`rrect-md` 0.6390 against 0.6829), which fires S4 on `rrect-md` and `rrect-ml`
(below their pre-W11c levels). At 2x both held rows fall further than in §1 (`rrect-md`
0.9125, `rrect-ml` 0.8751, both under their floors) and the band falls more (−0.050 / −0.040
against §1's −0.030 / −0.025). S3 fires on the same 1x spans.

## 3. The two runs beside the bed


**apple-macos-26.5-1x-light-standard**, CSS tier — `ssimMean` · `ssimBand` · spread web / native · level web / native

| cell | bed | linear (first dry run) | blur() control |
| --- | --- | --- | --- |
| `checkerboard__rrect-sm__rest` | 0.9855 · 0.6891 · 0.1472 / 0.1549 · 0.6117 / 0.6285 | 0.9868 · 0.7339 · 0.1686 / 0.1549 · 0.6924 / 0.6285 | 0.9883 · 0.7712 · 0.1712 / 0.1549 · 0.6160 / 0.6285 |
| `checkerboard__capsule-button__rest` | 0.9619 · 0.6437 · 0.1250 / 0.1424 · 0.6075 / 0.6207 | 0.9697 · 0.7360 · 0.1594 / 0.1424 · 0.6942 / 0.6207 | 0.9735 · 0.7771 · 0.1607 / 0.1424 · 0.6119 / 0.6207 |
| `checkerboard__rrect-md__rest` | 0.8963 · 0.6191 · 0.0767 / 0.1131 · 0.6352 / 0.6829 | 0.9045 · 0.6093 · 0.1196 / 0.1131 · 0.7327 / 0.6829 | 0.9096 · 0.6169 · 0.1192 / 0.1131 · 0.6390 / 0.6829 |
| `checkerboard__rrect-ml__rest` | 0.8515 · 0.6791 · 0.0591 / 0.0865 · 0.6335 / 0.6936 | 0.8599 · 0.6517 · 0.1044 / 0.0865 · 0.7368 / 0.6936 | 0.8676 · 0.6573 · 0.1031 / 0.0865 · 0.6369 / 0.6936 |
| `checkerboard__toolbar-group__rest` | 0.9584 · 0.6136 · 0.1332 / 0.1481 · 0.6029 / 0.6210 | 0.9632 · 0.6751 · 0.1611 / 0.1481 · 0.6841 / 0.6210 | 0.9661 · 0.7031 · 0.1620 / 0.1481 · 0.6055 / 0.6210 |
| `checkerboard__glass-over-glass__rest` | 0.8516 · 0.6967 · 0.1279 / 0.1321 · 0.6699 / 0.7231 | (not read) | (not read) |
| `checkerboard__rrect-lg__rest` | 0.8448 · 0.7479 · 0.0375 / 0.0650 · 0.6323 / 0.7066 | (not read) | (not read) |
| `hc-text__rrect-md__rest` | 0.9072 · 0.6402 · 0.0666 / 0.1078 · 0.7013 / 0.7368 | (not read) | (not read) |
| `photo__rrect-md__rest` | 0.9628 · 0.9065 · 0.0557 / 0.0572 · 0.7264 / 0.6649 | 0.9625 · 0.9058 · 0.0544 / 0.0572 · 0.7146 / 0.6649 | 0.9630 · 0.9074 · 0.0521 / 0.0572 · 0.7256 / 0.6649 |
| `photo__rrect-ml__rest` | 0.9468 · 0.9081 · 0.0614 / 0.0627 · 0.7285 / 0.6734 | 0.9459 · 0.9063 · 0.0563 / 0.0627 · 0.7175 / 0.6734 | 0.9469 · 0.9085 · 0.0572 / 0.0627 · 0.7275 / 0.6734 |

**apple-macos-26.5-2x-light-standard**, CSS tier — `ssimMean` · `ssimBand` · spread web / native · level web / native

| cell | bed | linear (first dry run) | blur() control |
| --- | --- | --- | --- |
| `checkerboard__rrect-sm__rest` | 0.9880 · 0.7633 · 0.1462 / 0.1636 · 0.6116 / 0.6285 | 0.9885 · 0.7758 · 0.1655 / 0.1636 · 0.6992 / 0.6285 | 0.9890 · 0.7887 · 0.1791 / 0.1636 · 0.6168 / 0.6285 |
| `checkerboard__capsule-button__rest` | 0.9708 · 0.7296 · 0.1291 / 0.1552 · 0.6147 / 0.6226 | 0.9752 · 0.7873 · 0.1512 / 0.1552 · 0.7112 / 0.6226 | 0.9763 · 0.7979 · 0.1661 / 0.1552 · 0.6197 / 0.6226 |
| `checkerboard__rrect-md__rest` | 0.9174 · 0.7611 · 0.0771 / 0.1272 · 0.6420 / 0.6832 | 0.9150 · 0.7312 · 0.1180 / 0.1272 · 0.7574 / 0.6832 | 0.9125 · 0.7112 · 0.1401 / 0.1272 · 0.6482 / 0.6832 |
| `checkerboard__rrect-ml__rest` | 0.8808 · 0.8096 · 0.0593 / 0.1018 · 0.6404 / 0.6929 | 0.8774 · 0.7844 · 0.0874 / 0.1018 · 0.7637 / 0.6929 | 0.8751 · 0.7694 · 0.1043 / 0.1018 · 0.6436 / 0.6929 |
| `checkerboard__toolbar-group__rest` | 0.9656 · 0.6886 · 0.1321 / 0.1581 · 0.6099 / 0.6246 | 0.9680 · 0.7207 · 0.1563 / 0.1581 · 0.7016 / 0.6246 | 0.9688 · 0.7250 · 0.1700 / 0.1581 · 0.6151 / 0.6246 |
| `checkerboard__glass-over-glass__rest` | 0.8709 · 0.8112 · 0.1267 / 0.1401 · 0.6756 / 0.7223 | (not read) | (not read) |
| `checkerboard__rrect-lg__rest` | 0.8760 · 0.8456 · 0.0377 / 0.0810 · 0.6393 / 0.7052 | (not read) | (not read) |
| `hc-text__rrect-md__rest` | 0.9405 · 0.8167 · 0.0670 / 0.1004 · 0.7086 / 0.7404 | (not read) | (not read) |
| `photo__rrect-md__rest` | 0.9739 · 0.9422 · 0.0551 / 0.0591 · 0.7269 / 0.6654 | 0.9740 · 0.9420 · 0.0588 / 0.0591 · 0.7118 / 0.6654 | 0.9740 · 0.9421 · 0.0562 / 0.0591 · 0.7270 / 0.6654 |
| `photo__rrect-ml__rest` | 0.9628 · 0.9426 · 0.0612 / 0.0641 · 0.7288 / 0.6732 | 0.9628 · 0.9420 · 0.0604 / 0.0641 · 0.7152 / 0.6732 | 0.9629 · 0.9424 · 0.0606 / 0.0641 · 0.7286 / 0.6732 |

## 4. The parent's reading

- **The level is the mechanism, and it is a conversion.** Under the linear-light form the layer
  beneath the tint carries the backdrop's LINEAR mean (0.5 on a checkerboard), where the tint's
  sRGB-overlay alpha was solved for the encoded blur's output level (the encoded mean, 0.214
  linear). On `rrect-md` at 1x the encoded overlay lands the level at 0.7327 against native's
  0.6829 and the GPU tier's 0.6946; the `blur()` control lands it at 0.6390 — one form 0.05
  over, the other 0.044 under, the reference between them. Apple's material and the GPU tier both
  blur in linear light, so the linear form with the conversion anchored where its layer actually
  sits is the derivation to make, not a choice between two wrong levels. Sent to the G1 worker.
- **The band.** `ssimBand` fell on `rrect-md` and `rrect-ml` at both scales in both forms (more
  in the control) while `ssimInterior` rose by up to +0.15. By eye at 2x (`dry1-linear-2x.png`),
  the candidate's near-contour checker is crisp and regular where native's is compressed and
  curved by the lens and the GPU tier's carries that curvature: the band's loss is the chartered
  gap no CSS form reaches, made more visible by a body that is finally sharp there. Whether the
  sharp layer at the nominal σ_s is sharper than the renderer's effective 1.6–1.7 is the one
  term that could move it and is being measured on single cells.
- **The spread's overshoot at 1x** on the thin spans and `rrect-ml` (+0.013–0.018) is in both
  forms, so it is not the colour space; it moves with the level conversion (the encoded overlay
  passes structure through the sRGB decode's slope at the composite's level) and is re-read
  after it.
- **Everything else held**: the solids and tinted cells within 0.002, the photo cells' level
  moved toward native, the dark rows up or flat, the accessibility rows inside their bounds
  (reduced-transparency and increased-contrast `rrect-md` −0.008 / −0.007, to be named at the
  declaration).

## 5. The re-form, on single cells (the worker's captures, `3db2416`; configurations A–H)

The parent asked for the level as a derivation. The worker measured eight configurations on
`checkerboard__rrect-md`, the capsule and `rrect-ml` (Δ against native unless marked; the bed's
`ssimMean` / `ssimBand` in the header; the GPU tier's own level on `rrect-md` at 1x is +0.0117
over native, its spread −0.0080):

| cell | dpr | configuration | `ssimMean` | `ssimBand` | level Δ | spread Δ |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1x | bed 0.8963 / 0.6191 — A, as first dry-run | 0.9045 | 0.6093 | +0.0498 | +0.0065 |
| | | B, anchor at the linear mean | 0.8903 | 0.5538 | −0.0277 | +0.0490 |
| | | C, anchor at the mix of encoded and linear means | 0.8932 | 0.5648 | −0.0126 | +0.0413 |
| | | D, C + the effective sharp width | 0.8949 | 0.5764 | −0.0018 | +0.0244 |
| | | **E, the effective sharp width alone (landed)** | **0.9028** | **0.6148** | +0.0590 | **−0.0066** |
| | | F, `contrast()` joint solve | 0.9097 | 0.6335 | +0.0159 vs GPU | −0.0151 |
| | | H, `feComponentTransfer` joint solve | 0.9010 | 0.6034 | −0.0226 (−0.0343 vs GPU) | −0.0026 |
| capsule | 1x | bed 0.9619 / 0.6437 — A | 0.9697 | 0.7360 | +0.0735 | +0.0170 |
| | | C | 0.9670 | 0.7004 | +0.0129 | +0.0577 |
| | | D | 0.9659 | 0.6886 | +0.0253 | +0.0359 |
| | | **E** | **0.9672** | **0.7076** | +0.0844 | **−0.0008** |
| | | F | 0.9711 | 0.7514 | −0.0026 vs GPU | −0.0166 |
| | | H | 0.9677 | 0.7072 | +0.0044 (−0.0532 vs GPU) | −0.0005 |
| `rrect-ml` | 1x | bed 0.8515 / 0.6791 — A | 0.8599 | 0.6517 | +0.0432 | +0.0179 |
| | | C | 0.8335 | 0.5980 | −0.0209 | +0.0497 |
| | | D | 0.8395 | 0.6155 | −0.0109 | +0.0344 |
| | | **E** | **0.8593** | **0.6615** | +0.0511 | **+0.0062** |
| | | F | 0.8711 | 0.6760 | +0.0141 vs GPU | +0.0012 |
| | | H | 0.8535 | 0.6457 | −0.0306 (−0.0317 vs GPU) | +0.0122 |
| `rrect-md` | 2x | bed 0.9174 / 0.7611 — A | 0.9150 | 0.7312 | +0.0742 | −0.0091 |
| | | B | 0.9075 | 0.6856 | +0.0042 | +0.0323 |
| | | C | 0.9078 | 0.6868 | +0.0061 | +0.0314 |
| | | D | 0.9081 | 0.6903 | +0.0086 | +0.0275 |
| | | **E** | **0.9149** | **0.7331** | +0.0761 | **−0.0120** |
| | | F | 0.9138 | 0.7215 | +0.0112 vs GPU | +0.0030 |
| | | H | 0.9099 | 0.7004 | −0.0093 (−0.0276 vs GPU) | +0.0179 |
| capsule | 2x | bed 0.9708 / 0.7296 — A | 0.9752 | 0.7873 | +0.0886 | −0.0040 |
| | | C | 0.9735 | 0.7648 | +0.0286 | +0.0428 |
| | | D | 0.9723 | 0.7508 | +0.0339 | +0.0355 |
| | | **E** | **0.9738** | **0.7698** | +0.0932 | **−0.0096** |
| | | F | 0.9749 | 0.7824 | −0.0077 vs GPU | −0.0045 |
| | | H | 0.9733 | 0.7594 | +0.0041 (−0.0580 vs GPU) | +0.0133 |
| `rrect-ml` | 2x | bed 0.8808 / 0.8096 — A | 0.8774 | 0.7844 | +0.0708 | −0.0144 |
| | | C | 0.8707 | 0.7507 | +0.0034 | +0.0161 |
| | | D | 0.8721 | 0.7560 | +0.0054 | +0.0146 |
| | | **E** | **0.8783** | **0.7884** | +0.0722 | **−0.0156** |
| | | F | 0.8777 | 0.7795 | +0.0166 vs GPU | −0.0036 |
| | | H | 0.8745 | 0.7651 | −0.0143 (−0.0227 vs GPU) | +0.0073 |

(G was a null run — a revert had removed the wiring, and it reproduced E; recorded because it cost
a capture round.) F also captured `dark-solid__rrect-md` at an interior level of 0.7083 against
native's 0.4844 and `impulse__rrect-md` 0.6573 against 0.4358 — `contrast()` pivots at encoded 0.5
and drags a dark ground up to it — and stepped the declared occlusion 0.172 across the collapse
band where the pin allows 0.163; H put those cells back at 0.5162 / 0.4580 (within 0.0003 of the
bed in `ssimMean`) and its collapse-band sweep is smooth by construction.

**What the eight say.** (i) The sharp component takes the same effective-width conversion as
the heavy one (E, `3db2416`): the spread lands inside ±0.007 of native at 1x and ±0.016 at 2x on
every cell, and the 1x rows rise over the bed. (ii) The level is a two-equation conversion — the
tier's encoded overlay must match the renderer's linear lerp in mean AND slope, which one alpha
cannot; `contrast()` carries it with a pivot the derivation cannot honour, `feComponentTransfer`
with a free intercept carries it exactly. (iii) With the conversion exact (H), the tier lands on
the renderer's *analytic* composite — and on native to within −0.03…+0.004 — and 0.023–0.058
BELOW the GPU tier's *rendered* interior, because the shader also draws the lens, the rim and the
highlight into the same pixels; E sits 0.027–0.064 ABOVE it. The GPU tier's rendered level is
between the two and neither conversion can aim at it, since the excess is the light of terms the
CSS tier does not draw. (iv) By the adopted metric E is the better landing (above the bed on four
of six against H's one; the band and the 2x rows closer to the bed), and it reads whiter than
native and than the GPU tier; H reads at native's level and scores lower. The branch carries E.
The parent's second dry run (§6) is of E; the level's residual is a named gap either way.

## 6. The second dry run — configuration E at `af49e00`, the holdout read once (`dry2.verify.txt`, `dry2-tables.md`)

Thirteen runs from a fresh build: the GPU tier on all six profiles with the holdout, the CSS
tier on all six with calibration and validation, then the CSS tier's holdout once — contract X8's
single reading of the frozen configuration. **S1 met**: 115 of 115 GPU captures byte-identical,
every GPU row exact. **At 1x every checkerboard row is above the bed, the holdout included**:
`rrect-sm` +0.0007, the capsule +0.0053, `rrect-md` 0.8963 → 0.9028, `rrect-ml` 0.8515 →
0.8593, the toolbar +0.0033, `glass-over-glass` 0.8516 → 0.8529, `rrect-lg` 0.8448 → 0.8513;
`hc-text__rrect-md` 0.9072 → 0.9387 (its pre-W11c reading was 0.9295) and its spread 0.0666 →
0.0808 against native's 0.1078; the spread on the five calibration checkerboard spans within
±0.007 of native (`rrect-md` 0.1064 / 0.1131, `rrect-ml` 0.0927 / 0.0865). **At 2x the thin
spans rise** (the capsule +0.0030, the toolbar +0.0016, `rrect-sm` +0.0001) **and the four
large spans fall**: `rrect-md` 0.9174 → 0.9149 (its floor is 0.9159), `rrect-ml` 0.8808 →
0.8783, `glass-over-glass` 0.8709 → 0.8683, `rrect-lg` 0.8760 → 0.8709 — the last three above
their floors — with `ssimBand` down 0.020–0.028 on each and `ssimInterior` up. **Stops:** S2
fired on those four (one under its floor by 0.0010); S3 fired on `rrect-ml` at 2x by 0.0006
(−0.0156 against ±0.015); S4 fired on `hc-text__capsule-button` by 0.0030 (0.9769 against its
pre-W11c 0.9799; +0.0030 over the bed); S5 and S6 met — the solids and tinted cells within
0.0004, the photo cells within 0.0008, the cross-tier ΔE over the fitted sets down on every
profile (1x light 0.00760 → 0.00721). The dark checkerboard rows are up on every cell (1x
`rrect-md` +0.0022, `glass-over-glass` +0.0039). The accessibility rows stay inside their bounds
and move: increased contrast `rrect-md` 0.9277 → 0.9241 and the capsule −0.0012; reduced
transparency `rrect-md` 0.9772 → 0.9729 and the capsule −0.0012.

**The level, on the whole bed.** The interior level sits 0.06–0.09 over native on every
checkerboard cell at both scales (`rrect-md` 0.7419 / 0.6829 at 1x, 0.7593 / 0.6832 at 2x;
the GPU tier 0.6946 / 0.7015) and 0.10 over on `hc-text__rrect-md` (0.8018 / 0.7368); on the
photo cells it moved TOWARD native on every span (`rrect-md` 0.7264 → 0.7147 against 0.6649).
The cross-tier level ratio reads 0.92–0.98 against its 0.8–1.25 bound.

**By eye** (`sheets/g1-1x.png`, `g1-2x.png`; five panels: native, the CSS bed, the candidate,
the GPU bed, the candidate's signed difference): the checker is back at the right pitch and
contrast on every span where the bed smeared it — on `rrect-lg` the bed is a flat grey and the
candidate reads like native and the GPU tier; the `hc-text` bars are legible again. The
candidate reads visibly whiter than native and than the GPU tier on the checkerboards. Neither
CSS column carries the lens curvature at the edges or the rim band the native and GPU columns
show; the candidate's crisp regular checker runs to the contour where native's is compressed
and curved, and that is where the 2x band rows lose.
