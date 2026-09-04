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
